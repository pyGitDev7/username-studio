"""HTTP request handler for the web dashboard."""
from __future__ import annotations

import json
import traceback
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from typing import Any, Dict
from urllib.parse import parse_qs, urlparse

import config
import utils
from . import tasks as task_state
from . import telegram_auth as telegram_auth_state
from .payloads import (
    DEFAULT_TABLE_LIMIT,
    MAX_TABLE_LIMIT,
    build_check_preview,
    clamp_int,
    clean_username_list,
    first_query,
    get_accounts_payload,
    get_channel_candidates,
    get_storage,
    get_usernames_payload,
    parse_bool,
    parse_float,
    read_log_lines,
)
from .server import SERVER_RUN_TOKEN, close_browser_client, register_browser_client
from .tasks import (
    run_channel_create_task,
    run_generation_task,
    run_telegram_check_task,
    start_task,
    validate_channel_username,
)
from .telegram_auth import (
    account_auth_action,
    confirm_telegram_code,
    confirm_telegram_password,
    delete_account_payload,
    get_telegram_auth_status,
    get_telegram_config_payload,
    require_checker_accounts,
    require_main_telegram_authorized,
    reset_telegram_session,
    save_telegram_config,
    start_telegram_auth,
)
from .templates import INDEX_HTML


class UsernameDashboardHandler(BaseHTTPRequestHandler):
    server_version = "UsernameDashboard/1.0"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send_json(self, payload: Dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        raw = json.dumps(payload, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _send_html(self, html: str) -> None:
        raw = html.replace("__SERVER_RUN_TOKEN__", SERVER_RUN_TOKEN).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8", errors="replace")
        if not raw:
            return {}
        payload = json.loads(raw)
        if payload is None:
            return {}
        if not isinstance(payload, dict):
            raise ValueError("JSON body must be an object")
        return payload

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        try:
            if parsed.path in {"/", "/index.html"}:
                self._send_html(INDEX_HTML)
            elif parsed.path == "/favicon.ico":
                self.send_response(HTTPStatus.NO_CONTENT)
                self.send_header("Cache-Control", "public, max-age=86400")
                self.send_header("Content-Length", "0")
                self.end_headers()
            elif parsed.path == "/api/config":
                self._send_json({
                    "batch_size": config.BATCH_SIZE,
                    "score_threshold": config.SCORE_THRESHOLD,
            "max_telegram_checks": config.MAX_TELEGRAM_CHECKS_PER_BATCH,
            "username_min_length": config.USERNAME_MIN_LENGTH,
            "username_max_length": config.USERNAME_MAX_LENGTH,
            "generation_min_length": config.USERNAME_MIN_LENGTH,
            "generation_max_length": config.USERNAME_MAX_LENGTH,
            "generation_allow_digits": False,
            "table_limit": DEFAULT_TABLE_LIMIT,
            "max_table_limit": MAX_TABLE_LIMIT,
        })
            elif parsed.path == "/api/stats":
                stats = get_storage().get_stats()
                self._send_json({"stats": stats})
            elif parsed.path == "/api/usernames":
                self._send_json(get_usernames_payload(query))
            elif parsed.path == "/api/accounts":
                self._send_json(get_accounts_payload())
            elif parsed.path == "/api/telegram/auth/status":
                self._send_json({"auth": get_telegram_auth_status()})
            elif parsed.path == "/api/telegram/config":
                self._send_json({"telegram_config": get_telegram_config_payload()})
            elif parsed.path == "/api/telegram/preview":
                limit = clamp_int(
                    first_query(query, "limit"),
                    min(config.MAX_TELEGRAM_CHECKS_PER_BATCH, 10),
                    maximum=config.MAX_TELEGRAM_CHECKS_PER_BATCH,
                )
                min_score = parse_float(first_query(query, "min_score"), config.SCORE_THRESHOLD) or config.SCORE_THRESHOLD
                usernames = clean_username_list(query.get("username"))
                self._send_json(build_check_preview(limit=limit, min_score=min_score, usernames=usernames or None))
            elif parsed.path == "/api/channels/available":
                self._send_json(get_channel_candidates(query))
            elif parsed.path == "/api/logs":
                lines = clamp_int(first_query(query, "lines"), 120, maximum=1000)
                self._send_json(read_log_lines(lines))
            elif parsed.path.startswith("/api/tasks/"):
                task_id = parsed.path.rsplit("/", 1)[-1]
                with task_state._task_lock:
                    task = dict(task_state._tasks.get(task_id) or {})
                if not task:
                    self._send_json({"error": "task_not_found"}, HTTPStatus.NOT_FOUND)
                else:
                    self._send_json({"task": task})
            elif parsed.path == "/api/tasks":
                with task_state._task_lock:
                    tasks = list(task_state._tasks.values())
                    active = dict(task_state._tasks.get(task_state._active_task_id) or {}) if task_state._active_task_id else None
                self._send_json({"active": active, "tasks": tasks[-20:]})
            else:
                self._send_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self._send_json({"error": str(exc), "traceback": traceback.format_exc()}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        try:
            payload = self._read_json()

            if parsed.path in {"/api/client/open", "/api/client/ping"}:
                self._send_json(register_browser_client(payload))

            elif parsed.path == "/api/client/close":
                self._send_json(close_browser_client(payload, self.server))

            elif parsed.path == "/api/generate":
                batch_size = clamp_int(payload.get("batch_size"), config.BATCH_SIZE, maximum=500)
                min_length = clamp_int(payload.get("min_length"), config.USERNAME_MIN_LENGTH, minimum=4, maximum=10)
                max_length = clamp_int(payload.get("max_length"), config.USERNAME_MAX_LENGTH, minimum=4, maximum=10)
                if max_length < min_length:
                    min_length, max_length = max_length, min_length
                allow_digits = parse_bool(payload.get("allow_digits"), False)
                task, active = start_task(
                    "generation",
                    f"Генерация batch {batch_size} ({min_length}-{max_length})",
                    lambda task_id: run_generation_task(task_id, batch_size, min_length, max_length, allow_digits),
                )
                if active:
                    self._send_json({"error": "task_already_running", "active": active}, HTTPStatus.CONFLICT)
                else:
                    self._send_json({"task": task}, HTTPStatus.ACCEPTED)

            elif parsed.path == "/api/accounts/auth":
                self._send_json(account_auth_action(payload), HTTPStatus.ACCEPTED)

            elif parsed.path == "/api/accounts/delete":
                self._send_json(delete_account_payload(payload))

            elif parsed.path == "/api/telegram/auth/start":
                auth = start_telegram_auth(payload.get("phone") or "")
                self._send_json({"auth": auth}, HTTPStatus.ACCEPTED)

            elif parsed.path == "/api/telegram/auth/confirm":
                auth = confirm_telegram_code(payload.get("flow_id") or "", payload.get("code") or "")
                self._send_json({"auth": auth})

            elif parsed.path == "/api/telegram/auth/password":
                auth = confirm_telegram_password(payload.get("flow_id") or "", payload.get("password") or "")
                self._send_json({"auth": auth})

            elif parsed.path == "/api/telegram/auth/cancel":
                flow_id = str(payload.get("flow_id") or "")
                with telegram_auth_state._auth_lock:
                    telegram_auth_state._auth_flows.pop(flow_id, None)
                self._send_json({"cancelled": bool(flow_id)})

            elif parsed.path == "/api/telegram/auth/reset-session":
                self._send_json({"reset": reset_telegram_session()})

            elif parsed.path == "/api/telegram/config":
                saved = save_telegram_config(payload)
                self._send_json({"telegram_config": saved})

            elif parsed.path == "/api/telegram/check":
                dry_run = parse_bool(payload.get("dry_run"), True)
                limit = clamp_int(
                    payload.get("limit"),
                    min(config.MAX_TELEGRAM_CHECKS_PER_BATCH, 10),
                    maximum=config.MAX_TELEGRAM_CHECKS_PER_BATCH,
                )
                min_score = parse_float(payload.get("min_score"), config.SCORE_THRESHOLD) or config.SCORE_THRESHOLD
                usernames = clean_username_list(payload.get("usernames"))
                preview = build_check_preview(limit=limit, min_score=min_score, usernames=usernames)
                candidates = preview["candidates"][:limit]

                if not candidates:
                    self._send_json({"error": "no_valid_candidates", "preview": preview}, HTTPStatus.BAD_REQUEST)
                    return

                if dry_run:
                    self._send_json({
                        "dry_run": True,
                        "message": "Preview: Telegram-запросы не выполнялись",
                        "preview": preview,
                    })
                    return

                if payload.get("confirm") != "CHECK":
                    self._send_json({"error": "confirmation_required", "required": "CHECK"}, HTTPStatus.BAD_REQUEST)
                    return

                auth_error = require_checker_accounts()
                if auth_error:
                    self._send_json(auth_error, HTTPStatus.BAD_REQUEST)
                    return

                task, active = start_task(
                    "telegram_check",
                    f"Telegram-проверка {len(candidates)} username",
                    lambda task_id: run_telegram_check_task(task_id, candidates),
                )
                if active:
                    self._send_json({"error": "task_already_running", "active": active}, HTTPStatus.CONFLICT)
                else:
                    self._send_json({"task": task, "candidates": candidates}, HTTPStatus.ACCEPTED)

            elif parsed.path == "/api/channels/create":
                username = utils.normalize_username_input(payload.get("username") or "")
                title = str(payload.get("title") or username).strip()[:80]
                dry_run = parse_bool(payload.get("dry_run"), True)
                record, reason = validate_channel_username(username)

                if reason:
                    self._send_json({"error": "username_not_allowed", "reason": reason, "record": record}, HTTPStatus.BAD_REQUEST)
                    return

                if dry_run:
                    self._send_json({
                        "dry_run": True,
                        "message": f"Preview: канал для @{username} не создавался",
                        "record": record,
                    })
                    return

                if str(payload.get("confirm") or "").strip().lower() != "y":
                    self._send_json({"error": "confirmation_required", "required": "y", "record": record}, HTTPStatus.BAD_REQUEST)
                    return

                auth_error = require_main_telegram_authorized()
                if auth_error:
                    self._send_json(auth_error, HTTPStatus.BAD_REQUEST)
                    return

                task, active = start_task(
                    "channel_create",
                    f"Создание @{username}",
                    lambda task_id: run_channel_create_task(task_id, username, title),
                )
                if active:
                    self._send_json({"error": "task_already_running", "active": active}, HTTPStatus.CONFLICT)
                else:
                    self._send_json({"task": task, "record": record}, HTTPStatus.ACCEPTED)
            else:
                self._send_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)
        except json.JSONDecodeError:
            self._send_json({"error": "invalid_json"}, HTTPStatus.BAD_REQUEST)
        except ValueError as exc:
            self._send_json({"error": "invalid_json", "message": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self._send_json({"error": str(exc), "traceback": traceback.format_exc()}, HTTPStatus.INTERNAL_SERVER_ERROR)

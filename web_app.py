"""
Local browser dashboard for the Telegram username generator.

The app uses only the Python standard library and keeps Telegram actions behind
explicit dry-run/confirmation checks. The existing CLI in main.py remains the
source of generation, evaluation, Telegram checks, and channel creation logic.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import threading
import time
import traceback
import uuid
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple
from urllib.parse import parse_qs, urlparse

import config
import utils
from account_manager import AccountManager
from storage import UsernameStorage


HOST = "127.0.0.1"
PORT = 8080
DEFAULT_TABLE_LIMIT = 50
MAX_TABLE_LIMIT = 200

_storage: Optional[UsernameStorage] = None
_storage_lock = threading.Lock()
_telegram_session_lock = threading.RLock()
_account_manager: Optional[AccountManager] = None
_account_manager_lock = threading.RLock()

_task_lock = threading.Lock()
_tasks: Dict[str, Dict[str, Any]] = {}
_active_task_id: Optional[str] = None

_auth_lock = threading.Lock()
_auth_flows: Dict[str, Dict[str, Any]] = {}
AUTH_FLOW_TTL_SECONDS = 10 * 60
ENV_PATH = Path(".env")
TELEGRAM_ENV_KEYS = ["TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_PHONE"]


def get_storage() -> UsernameStorage:
    global _storage
    with _storage_lock:
        if _storage is None:
            _storage = UsernameStorage(config.DATABASE_PATH)
        return _storage


def get_account_manager() -> AccountManager:
    global _account_manager
    with _account_manager_lock:
        if _account_manager is None:
            _account_manager = AccountManager()
        return _account_manager


def now_iso() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def clamp_int(value: Any, default: int, minimum: int = 1, maximum: int = MAX_TABLE_LIMIT) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


def parse_float(value: Any, default: Optional[float] = None) -> Optional[float]:
    if value in (None, ""):
        return default
    try:
        return float(str(value).replace(",", "."))
    except ValueError:
        return default


def parse_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def mask_phone(phone: str) -> str:
    phone = str(phone or "").strip()
    if len(phone) <= 5:
        return phone
    return f"{phone[:3]}{'*' * max(3, len(phone) - 6)}{phone[-3:]}"


def refresh_config() -> None:
    config.reload_env()


def telegram_session_path() -> Path:
    path = Path(config.SESSION_NAME)
    if not str(path).endswith(".session"):
        path = Path(str(path) + ".session")
    return path


def reset_telegram_session() -> Dict[str, Any]:
    refresh_config()
    with _telegram_session_lock:
        with _auth_lock:
            _auth_flows.clear()

        deleted: List[str] = []
        for path in (telegram_session_path(), Path(str(telegram_session_path()) + "-journal")):
            if path.exists():
                path.unlink()
                deleted.append(str(path))

    return {
        "session_name": config.SESSION_NAME,
        "deleted": deleted,
        "message": "Telegram-сессия сброшена. Теперь можно войти заново.",
    }


def get_telegram_config_payload() -> Dict[str, Any]:
    refresh_config()
    return {
        "api_id": str(config.TELEGRAM_API_ID or ""),
        "api_hash_set": bool(config.TELEGRAM_API_HASH),
        "phone": config.TELEGRAM_PHONE,
        "session_name": config.SESSION_NAME,
        "dry_run": bool(config.TELEGRAM_DRY_RUN),
    }


def _clean_env_value(value: Any) -> str:
    text = str(value or "").strip()
    if "\n" in text or "\r" in text:
        raise ValueError("Значение не должно содержать переносы строк")
    return text


def write_env_values(updates: Dict[str, str]) -> None:
    existing = ENV_PATH.read_text(encoding="utf-8", errors="replace").splitlines() if ENV_PATH.exists() else []
    seen = set()
    lines: List[str] = []

    for line in existing:
        stripped = line.strip()
        key = stripped.split("=", 1)[0].strip() if "=" in stripped and not stripped.startswith("#") else ""
        if key in updates:
            lines.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            lines.append(line)

    if lines and lines[-1].strip():
        lines.append("")

    for key in TELEGRAM_ENV_KEYS:
        if key in updates and key not in seen:
            lines.append(f"{key}={updates[key]}")

    ENV_PATH.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def save_telegram_config(payload: Dict[str, Any]) -> Dict[str, Any]:
    refresh_config()
    api_id = _clean_env_value(payload.get("api_id"))
    api_hash = _clean_env_value(payload.get("api_hash"))
    phone = _clean_env_value(payload.get("phone"))

    if api_id:
        try:
            int(api_id)
        except ValueError as exc:
            raise ValueError("TELEGRAM_API_ID должен быть числом") from exc

    updates = {
        "TELEGRAM_API_ID": api_id,
        "TELEGRAM_PHONE": phone,
    }
    if api_hash:
        updates["TELEGRAM_API_HASH"] = api_hash

    write_env_values(updates)
    refresh_config()
    result = get_telegram_config_payload()
    result["message"] = "Telegram API настройки сохранены"
    result["api_hash_changed"] = bool(api_hash)
    return result


def first_query(query: Dict[str, List[str]], key: str, default: Any = None) -> Any:
    values = query.get(key)
    return values[0] if values else default


def api_row(row: Dict[str, Any]) -> Dict[str, Any]:
    score = row.get("score")
    try:
        score = None if score is None else round(float(score), 2)
    except (TypeError, ValueError):
        score = None

    return {
        "username": row.get("username") or "",
        "score": score,
        "status": row.get("status") or "unchecked",
        "generation_type": row.get("generation_type") or "",
        "batch_num": row.get("batch_num"),
        "checked_at": row.get("checked_at") or "",
        "scored_at": row.get("scored_at") or "",
        "readability": row.get("readability"),
        "brandability": row.get("brandability"),
        "meaning": row.get("meaning"),
        "rarity": row.get("rarity"),
        "channel_id": row.get("channel_id"),
        "channel_name": row.get("channel_name") or "",
        "notes": row.get("notes") or "",
    }


def clean_username_list(raw_items: Any) -> List[str]:
    if not isinstance(raw_items, list):
        return []
    result: List[str] = []
    seen = set()
    for item in raw_items:
        username = utils.normalize_username_input(str(item or ""))
        if not username or username in seen:
            continue
        seen.add(username)
        result.append(username)
    return result


def get_usernames_payload(query: Dict[str, List[str]]) -> Dict[str, Any]:
    storage = get_storage()
    status = first_query(query, "status") or None
    if status == "all":
        status = None

    limit = clamp_int(first_query(query, "limit"), DEFAULT_TABLE_LIMIT)
    min_score = parse_float(first_query(query, "min_score"))
    last_batch_only = parse_bool(first_query(query, "last_batch"))
    search = utils.normalize_username_input(first_query(query, "search", ""))
    valid_only = parse_bool(first_query(query, "valid_only"), status == "available")

    fetch_limit = None if search else limit
    rows = storage.get_username_records(
        limit=fetch_limit,
        min_score=min_score,
        status=status,
        last_batch_only=last_batch_only,
        valid_only=valid_only,
    )

    if search:
        rows = [row for row in rows if search in str(row.get("username") or "")]

    sliced = rows[:limit]
    return {
        "rows": [api_row(row) for row in sliced],
        "total_visible": len(sliced),
        "has_more": len(rows) > len(sliced),
        "limit": limit,
    }


def classify_check_rows(
    rows: List[Dict[str, Any]],
    min_score: float,
    *,
    telegram_format: bool = False,
    allow_missing_score: bool = False,
    allow_recheck: bool = False,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    candidates: List[Dict[str, Any]] = []
    skipped: List[Dict[str, Any]] = []

    for row in rows:
        normalized = api_row(row)
        username = normalized["username"]
        score = normalized["score"]
        reason = ""

        if normalized["status"] != "unchecked" and not allow_recheck:
            reason = f"status:{normalized['status']}"
        elif telegram_format and not utils.is_telegram_username_format(username):
            reason = "invalid_telegram_format"
        elif not telegram_format and not utils.is_valid_username(username):
            reason = f"invalid_format_{config.USERNAME_MIN_LENGTH}_{config.USERNAME_MAX_LENGTH}_az"
        elif score is None and not allow_missing_score:
            reason = "no_score"
        elif score is not None and score < min_score:
            reason = f"score_below_{min_score:g}"

        if reason:
            skipped.append({"username": username, "reason": reason, "row": normalized})
        else:
            candidates.append(normalized)

    return candidates, skipped


def build_check_preview(
    limit: int,
    min_score: float,
    usernames: Optional[List[str]] = None,
) -> Dict[str, Any]:
    storage = get_storage()

    if usernames:
        rows = []
        for username in usernames:
            record = storage.get_username_record(username)
            if record:
                rows.append(record)
            else:
                rows.append({
                    "username": username,
                    "score": None,
                    "status": "unchecked",
                    "generation_type": "manual",
                })
        candidates, skipped = classify_check_rows(
            rows,
            min_score,
            telegram_format=True,
            allow_missing_score=True,
            allow_recheck=True,
        )
        source = "manual"
    else:
        last_batch_rows = storage.get_username_records(
            limit=None,
            status="unchecked",
            last_batch_only=True,
            valid_only=False,
        )
        last_candidates, last_skipped = classify_check_rows(last_batch_rows, min_score)

        database_rows = storage.get_username_records(
            limit=None,
            status="unchecked",
            valid_only=False,
        )
        database_candidates, database_skipped = classify_check_rows(database_rows, min_score)

        if last_candidates:
            candidates, skipped, source = last_candidates, last_skipped, "last_batch"
        elif database_candidates:
            candidates, skipped, source = database_candidates, database_skipped, "database"
        elif last_batch_rows:
            candidates, skipped, source = last_candidates, last_skipped, "last_batch"
        else:
            candidates, skipped, source = database_candidates, database_skipped, "database"

    selected = candidates[:limit]
    return {
        "source": source,
        "min_score": min_score,
        "limit": limit,
        "candidates": selected,
        "candidate_count": len(candidates),
        "skipped": skipped[:100],
        "skipped_count": len(skipped),
    }


def get_channel_candidates(query: Dict[str, List[str]]) -> Dict[str, Any]:
    storage = get_storage()
    limit = clamp_int(first_query(query, "limit"), DEFAULT_TABLE_LIMIT)
    min_score = parse_float(first_query(query, "min_score"))
    rows = storage.get_username_records(
        limit=limit,
        min_score=min_score,
        status="available",
        valid_only=False,
    )
    rows = [
        row for row in rows
        if row.get("status") == "available"
        and utils.is_telegram_username_format(row.get("username", ""))
        and not storage.is_username_used(row.get("username", ""))
    ]
    return {"rows": [api_row(row) for row in rows[:limit]], "limit": limit}


def read_log_lines(line_count: int) -> Dict[str, Any]:
    path = Path("logs") / config.LOG_FILE
    if not path.exists():
        return {"path": str(path), "lines": [], "text": ""}

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    tail = lines[-line_count:]
    return {"path": str(path), "lines": tail, "text": "\n".join(tail)}


def cleanup_auth_flows() -> None:
    cutoff = time.time() - AUTH_FLOW_TTL_SECONDS
    with _auth_lock:
        expired = [
            flow_id for flow_id, flow in _auth_flows.items()
            if flow.get("created_ts", 0) < cutoff
        ]
        for flow_id in expired:
            _auth_flows.pop(flow_id, None)


async def build_telegram_auth_status_from_client(client: Any) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "configured": True,
        "authorized": False,
        "ready": False,
        "session_matches_config": True,
        "needs_relogin": False,
        "session_name": config.SESSION_NAME,
        "configured_phone": mask_phone(config.TELEGRAM_PHONE),
        "has_configured_phone": bool(config.TELEGRAM_PHONE),
        "user": None,
        "error": "",
    }
    result["authorized"] = bool(await client.is_user_authorized())
    if result["authorized"]:
        me = await client.get_me()
        actual_phone = getattr(me, "phone", "") or ""
        matches_config = utils.telegram_phone_matches(actual_phone, config.TELEGRAM_PHONE)
        result["session_matches_config"] = matches_config
        result["ready"] = matches_config
        if not matches_config:
            result["needs_relogin"] = True
            result["error"] = (
                "Сессия подключена к другому Telegram-аккаунту. "
                "Сбросьте сессию и войдите по телефону из .env."
            )
        result["user"] = {
            "id": getattr(me, "id", None),
            "first_name": getattr(me, "first_name", "") or "",
            "last_name": getattr(me, "last_name", "") or "",
            "username": getattr(me, "username", "") or "",
            "phone": mask_phone(actual_phone),
        }
    return result


async def get_telegram_auth_status_async() -> Dict[str, Any]:
    refresh_config()
    configured = bool(config.TELEGRAM_API_ID and config.TELEGRAM_API_HASH)
    result: Dict[str, Any] = {
        "configured": configured,
        "authorized": False,
        "ready": False,
        "session_matches_config": True,
        "needs_relogin": False,
        "session_name": config.SESSION_NAME,
        "configured_phone": mask_phone(config.TELEGRAM_PHONE),
        "has_configured_phone": bool(config.TELEGRAM_PHONE),
        "user": None,
        "error": "",
    }
    if not configured:
        result["error"] = "TELEGRAM_API_ID/TELEGRAM_API_HASH не заданы в .env"
        return result

    from telethon import TelegramClient

    with _telegram_session_lock:
        client = TelegramClient(config.SESSION_NAME, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
        try:
            await client.connect()
            result = await build_telegram_auth_status_from_client(client)
        except Exception as exc:
            result["error"] = str(exc) or type(exc).__name__
        finally:
            await client.disconnect()
    return result


def get_telegram_auth_status() -> Dict[str, Any]:
    return asyncio.run(get_telegram_auth_status_async())


async def start_telegram_auth_async(phone: str) -> Dict[str, Any]:
    refresh_config()
    if not (config.TELEGRAM_API_ID and config.TELEGRAM_API_HASH):
        raise RuntimeError("TELEGRAM_API_ID/TELEGRAM_API_HASH не заданы в .env")

    phone = str(phone or config.TELEGRAM_PHONE or "").strip()
    if not phone:
        raise RuntimeError("Введите телефон или задайте TELEGRAM_PHONE в .env")

    from telethon import TelegramClient

    with _telegram_session_lock:
        client = TelegramClient(config.SESSION_NAME, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
        try:
            await client.connect()
            if await client.is_user_authorized():
                status = await build_telegram_auth_status_from_client(client)
                if not status.get("ready"):
                    raise RuntimeError(status.get("error") or "Сессия подключена к другому Telegram-аккаунту")
                status["already_authorized"] = True
                return status

            sent = await client.send_code_request(phone)
            flow_id = uuid.uuid4().hex[:12]
            with _auth_lock:
                _auth_flows[flow_id] = {
                    "flow_id": flow_id,
                    "phone": phone,
                    "phone_code_hash": sent.phone_code_hash,
                    "created_at": now_iso(),
                    "created_ts": time.time(),
                    "password_required": False,
                }
            return {
                "flow_id": flow_id,
                "phone": mask_phone(phone),
                "expires_in": AUTH_FLOW_TTL_SECONDS,
                "code_type": type(getattr(sent, "type", None)).__name__,
            }
        finally:
            await client.disconnect()


def start_telegram_auth(phone: str) -> Dict[str, Any]:
    cleanup_auth_flows()
    return asyncio.run(start_telegram_auth_async(phone))


def get_auth_flow(flow_id: str) -> Dict[str, Any]:
    cleanup_auth_flows()
    with _auth_lock:
        flow = dict(_auth_flows.get(flow_id) or {})
    if not flow:
        raise RuntimeError("Сессия входа истекла. Отправьте код заново.")
    return flow


async def confirm_telegram_code_async(flow_id: str, code: str) -> Dict[str, Any]:
    refresh_config()
    flow = get_auth_flow(flow_id)
    code = str(code or "").strip().replace(" ", "")
    if not code:
        raise RuntimeError("Введите код Telegram")

    from telethon import TelegramClient
    from telethon.errors import SessionPasswordNeededError

    with _telegram_session_lock:
        client = TelegramClient(config.SESSION_NAME, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
        try:
            await client.connect()
            try:
                await client.sign_in(
                    phone=flow["phone"],
                    code=code,
                    phone_code_hash=flow["phone_code_hash"],
                )
            except SessionPasswordNeededError:
                with _auth_lock:
                    if flow_id in _auth_flows:
                        _auth_flows[flow_id]["password_required"] = True
                return {
                    "authorized": False,
                    "password_required": True,
                    "message": "Нужен 2FA-пароль Telegram",
                }

            with _auth_lock:
                _auth_flows.pop(flow_id, None)
            return await build_telegram_auth_status_from_client(client)
        finally:
            await client.disconnect()


def confirm_telegram_code(flow_id: str, code: str) -> Dict[str, Any]:
    return asyncio.run(confirm_telegram_code_async(flow_id, code))


async def confirm_telegram_password_async(flow_id: str, password: str) -> Dict[str, Any]:
    refresh_config()
    get_auth_flow(flow_id)
    password = str(password or "")
    if not password:
        raise RuntimeError("Введите 2FA-пароль Telegram")

    from telethon import TelegramClient

    with _telegram_session_lock:
        client = TelegramClient(config.SESSION_NAME, config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
        try:
            await client.connect()
            await client.sign_in(password=password)
            with _auth_lock:
                _auth_flows.pop(flow_id, None)
            return await build_telegram_auth_status_from_client(client)
        finally:
            await client.disconnect()


def confirm_telegram_password(flow_id: str, password: str) -> Dict[str, Any]:
    return asyncio.run(confirm_telegram_password_async(flow_id, password))


def get_accounts_payload() -> Dict[str, Any]:
    manager = get_account_manager()
    manager.load_accounts()
    return {
        "accounts": manager.list_accounts(),
        "active_account": manager.get_active_account(),
        "has_accounts": manager.has_accounts(),
    }


def account_auth_action(payload: Dict[str, Any]) -> Dict[str, Any]:
    manager = get_account_manager()
    action = str(payload.get("action") or "start").strip().lower()

    if action == "start":
        auth = asyncio.run(manager.start_auth(
            payload.get("api_id"),
            payload.get("api_hash"),
            payload.get("phone") or "",
        ))
    elif action == "code":
        auth = asyncio.run(manager.confirm_code(
            payload.get("flow_id") or "",
            payload.get("code") or "",
        ))
    elif action == "password":
        auth = asyncio.run(manager.confirm_password(
            payload.get("flow_id") or "",
            payload.get("password") or "",
        ))
    elif action == "cancel":
        auth = {"cancelled": manager.cancel_auth(payload.get("flow_id") or "")}
    else:
        raise ValueError("Неизвестное действие авторизации аккаунта")

    result = get_accounts_payload()
    result["auth"] = auth
    return result


def delete_account_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    account_id = str(payload.get("account_id") or "").strip()
    if not account_id:
        account_id = utils.normalize_phone(str(payload.get("phone") or ""))
    if not account_id:
        raise ValueError("Не указан аккаунт для удаления")

    deleted = get_account_manager().delete_account(account_id)
    result = get_accounts_payload()
    result["deleted"] = deleted
    return result


def require_telegram_authorized() -> Optional[Dict[str, Any]]:
    if get_account_manager().has_accounts():
        return None

    status = get_telegram_auth_status()
    if status.get("authorized") and status.get("ready", True):
        return None
    if status.get("needs_relogin"):
        return {
            "error": "telegram_wrong_account",
            "message": status.get("error") or "Сессия подключена к другому Telegram-аккаунту.",
            "auth": status,
        }
    return {
        "error": "telegram_login_required",
        "message": "Сначала войдите в Telegram во вкладке Telegram.",
        "auth": status,
    }


def update_task(task_id: str, **fields: Any) -> None:
    with _task_lock:
        task = _tasks.get(task_id)
        if not task:
            return
        task.update(fields)
        task["updated_at"] = now_iso()


def finish_task(task_id: str, result: Dict[str, Any]) -> None:
    update_task(
        task_id,
        status="completed",
        progress=100,
        message="Готово",
        result=result,
        finished_at=now_iso(),
    )


def fail_task(task_id: str, exc: BaseException) -> None:
    update_task(
        task_id,
        status="failed",
        message=str(exc) or type(exc).__name__,
        error=str(exc) or type(exc).__name__,
        traceback=traceback.format_exc(),
        finished_at=now_iso(),
    )


def start_task(kind: str, title: str, target: Callable[[str], None]) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    global _active_task_id

    with _task_lock:
        if _active_task_id and _tasks.get(_active_task_id, {}).get("status") == "running":
            return None, dict(_tasks[_active_task_id])

        task_id = uuid.uuid4().hex[:12]
        task = {
            "id": task_id,
            "kind": kind,
            "title": title,
            "status": "running",
            "progress": 1,
            "message": "Старт",
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "result": None,
        }
        _tasks[task_id] = task
        _active_task_id = task_id

        if len(_tasks) > 20:
            old_ids = sorted(_tasks, key=lambda item: _tasks[item]["created_at"])[:-20]
            for old_id in old_ids:
                if old_id != _active_task_id:
                    _tasks.pop(old_id, None)

    def runner() -> None:
        global _active_task_id
        try:
            target(task_id)
        except BaseException as exc:
            fail_task(task_id, exc)
        finally:
            with _task_lock:
                if _active_task_id == task_id:
                    _active_task_id = None

    thread = threading.Thread(target=runner, name=f"web-task-{task_id}", daemon=True)
    thread.start()
    return dict(task), None


def run_generation_task(
    task_id: str,
    batch_size: int,
    min_length: int,
    max_length: int,
    allow_digits: bool,
) -> None:
    from main import UsernameGenerationSystem

    update_task(task_id, progress=8, message="Инициализация генератора")
    system = UsernameGenerationSystem(dry_run=True, no_telegram=True)

    settings_text = f"{min_length}-{max_length}, {'с цифрами' if allow_digits else 'без цифр'}"
    update_task(task_id, progress=20, message=f"Генерация batch ({settings_text})")
    batch = system.generate_batch(
        batch_size,
        min_length=min_length,
        max_length=max_length,
        allow_digits=allow_digits,
    )
    usernames = batch.get("usernames") or []
    if not usernames:
        raise RuntimeError(batch.get("error") or "Не удалось сгенерировать username")

    update_task(
        task_id,
        progress=55,
        message=f"Оценка {len(usernames)} username",
        result={"batch_num": batch.get("batch_num"), "generated_count": len(usernames)},
    )
    evaluated = system.evaluate_batch(usernames)

    rows = []
    for item in evaluated:
        username = item.get("username") or ""
        rows.append({
            "username": username,
            "score": round(float(item.get("total_score") or item.get("score") or 0), 2),
            "status": "unchecked",
            "generation_type": item.get("generation_type") or system.last_generation_types.get(username) or "",
            "batch_num": batch.get("batch_num"),
            "readability": item.get("readability"),
            "brandability": item.get("brandability"),
            "meaning": item.get("meaning"),
            "rarity": item.get("rarity"),
        })

    finish_task(task_id, {
        "batch_num": batch.get("batch_num"),
        "generated_count": len(usernames),
        "evaluated_count": len(rows),
        "settings": batch.get("settings") or {
            "min_length": min_length,
            "max_length": max_length,
            "allow_digits": allow_digits,
        },
        "rows": rows[:MAX_TABLE_LIMIT],
    })


def run_telegram_check_task(task_id: str, candidates: List[Dict[str, Any]]) -> None:
    from main import UsernameGenerationSystem

    update_task(task_id, progress=5, message="Подключение к Telegram")
    system = UsernameGenerationSystem(dry_run=False, no_telegram=False)
    system.account_manager = get_account_manager()

    async def check() -> Dict[str, Dict[str, Any]]:
        try:
            update_task(task_id, progress=20, message=f"Проверка {len(candidates)} username")

            def on_checked(username: str, details: Dict[str, Any], index: int, total: int) -> None:
                progress = 20 + int((index / max(total, 1)) * 70)
                status = details.get("status") or ("available" if details.get("available") else "checked_taken")
                account_phone = details.get("account_phone") or "-"
                update_task(
                    task_id,
                    progress=min(progress, 95),
                    message=f"Проверено {index}/{total}: @{username} ({status}) через {account_phone}",
                )

            return await system.check_availability_batch(candidates, progress_callback=on_checked)
        finally:
            await system.close_telegram()

    with _telegram_session_lock:
        results = asyncio.run(check())
    rows = []
    by_username = {item["username"]: item for item in candidates}
    for username, details in results.items():
        source = by_username.get(username, {})
        rows.append({
            "username": username,
            "score": source.get("score"),
            "generation_type": source.get("generation_type") or "",
            "batch_num": source.get("batch_num"),
            "available": bool(details.get("available")),
            "status": details.get("status") or ("available" if details.get("available") else "checked_taken"),
            "notes": details.get("notes") or "",
        })

    finish_task(task_id, {
        "checked_count": len(rows),
        "available_count": sum(1 for row in rows if row.get("available")),
        "rows": rows,
    })


def validate_channel_username(username: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    username = utils.normalize_username_input(username)
    if not username:
        return None, "empty_username"
    if not utils.is_telegram_username_format(username):
        return None, "invalid_telegram_format"

    storage = get_storage()
    record = storage.get_username_record(username)
    if not record:
        return None, "not_in_database"

    api_record = api_row(record)
    if api_record["status"] != "available":
        return api_record, f"status:{api_record['status']}"
    if storage.is_username_used(username):
        return api_record, "already_used"

    return api_record, None


def run_channel_create_task(task_id: str, username: str, title: str) -> None:
    from main import UsernameGenerationSystem

    update_task(task_id, progress=8, message=f"Создание канала @{username}")
    system = UsernameGenerationSystem(dry_run=False, no_telegram=False)

    async def create() -> Optional[int]:
        try:
            return await system.create_channel_for_username(username, title or username)
        finally:
            await system.close_telegram()

    with _telegram_session_lock:
        channel_id = asyncio.run(create())
    if not channel_id:
        raise RuntimeError("Канал не создан. Подробности есть в логах.")

    finish_task(task_id, {"username": username, "channel_id": channel_id, "title": title or username})


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
        raw = html.encode("utf-8")
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
                with _task_lock:
                    task = dict(_tasks.get(task_id) or {})
                if not task:
                    self._send_json({"error": "task_not_found"}, HTTPStatus.NOT_FOUND)
                else:
                    self._send_json({"task": task})
            elif parsed.path == "/api/tasks":
                with _task_lock:
                    tasks = list(_tasks.values())
                    active = dict(_tasks.get(_active_task_id) or {}) if _active_task_id else None
                self._send_json({"active": active, "tasks": tasks[-20:]})
            else:
                self._send_json({"error": "not_found"}, HTTPStatus.NOT_FOUND)
        except Exception as exc:
            self._send_json({"error": str(exc), "traceback": traceback.format_exc()}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)

        try:
            payload = self._read_json()

            if parsed.path == "/api/generate":
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
                with _auth_lock:
                    _auth_flows.pop(flow_id, None)
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

                auth_error = require_telegram_authorized()
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

                auth_error = require_telegram_authorized()
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


class ReusableThreadingHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local web dashboard for Telegram username generator")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", type=int, default=PORT)
    parser.add_argument("--no-browser", action="store_true", help="start server without opening a browser")
    return parser.parse_args()


def create_server(host: str, port: int) -> ReusableThreadingHTTPServer:
    ports = [port] if port == 0 else [port, *range(port + 1, port + 21)]
    last_error = None
    for candidate in ports:
        try:
            return ReusableThreadingHTTPServer((host, candidate), UsernameDashboardHandler)
        except OSError as exc:
            last_error = exc
    raise last_error or OSError(f"Cannot bind {host}:{port}")


def run_server(host: str, port: int, open_browser: bool = False) -> None:
    server = create_server(host, port)
    url = f"http://{host}:{server.server_address[1]}"
    print(f"Username dashboard: {url}", flush=True)
    if open_browser:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard...", flush=True)
    finally:
        server.server_close()


INDEX_HTML = r"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Telegram Username Dashboard</title>
  <style>
    :root {
      --bg: #f2f5f7;
      --panel: #ffffff;
      --panel-soft: #eef4f7;
      --text: #101720;
      --muted: #66758a;
      --line: #d6dee8;
      --line-strong: #c7d1df;
      --accent: #0d9488;
      --accent-strong: #0f766e;
      --accent-soft: #dff7f2;
      --blue: #2563eb;
      --green: #16814d;
      --red: #b42318;
      --amber: #a15c07;
      --violet: #6d28d9;
      --sidebar: #111820;
      --sidebar-soft: #1b2632;
      --sidebar-text: #eef4f7;
      --sidebar-muted: #aeb9c8;
      --shadow: 0 16px 40px rgba(16, 23, 32, 0.08);
      --shadow-soft: 0 8px 22px rgba(16, 23, 32, 0.06);
      --focus: 0 0 0 3px rgba(13, 148, 136, 0.18);
    }

    * { box-sizing: border-box; }
    [hidden] { display: none !important; }
    html { overflow-x: hidden; }
    body {
      margin: 0;
      min-height: 100vh;
      background: linear-gradient(180deg, #f7f9fb 0%, var(--bg) 54%, #edf3f4 100%);
      color: var(--text);
      font: 14px/1.45 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      letter-spacing: 0;
      font-variant-numeric: tabular-nums;
    }

    button, input, select, textarea {
      font: inherit;
      letter-spacing: 0;
    }

    .app {
      display: grid;
      grid-template-columns: 248px minmax(0, 1fr);
      min-height: 100vh;
    }

    .sidebar {
      position: sticky;
      top: 0;
      height: 100vh;
      padding: 22px 14px;
      border-right: 1px solid rgba(255, 255, 255, 0.08);
      background: var(--sidebar);
      color: var(--sidebar-text);
    }

    .brand {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 18px;
      padding: 0 6px;
    }

    .brand h1 {
      margin: 0;
      color: var(--sidebar-text);
      font-size: 18px;
      line-height: 1.2;
      font-weight: 780;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 3px 8px;
      border-radius: 999px;
      border: 1px solid rgba(125, 211, 190, 0.34);
      background: rgba(13, 148, 136, 0.16);
      color: #b9f4e7;
      font-size: 12px;
      font-weight: 650;
      white-space: nowrap;
    }

    .nav {
      display: grid;
      gap: 5px;
    }

    .nav button {
      width: 100%;
      min-height: 40px;
      padding: 9px 10px;
      border: 0;
      border-radius: 8px;
      background: transparent;
      color: var(--sidebar-muted);
      text-align: left;
      cursor: pointer;
      font-size: 13px;
      font-weight: 650;
      transition: background 150ms ease, color 150ms ease, transform 150ms ease;
    }

    .nav button::before {
      content: "";
      display: inline-block;
      width: 7px;
      height: 7px;
      margin-right: 10px;
      border-radius: 999px;
      background: currentColor;
      opacity: 0.42;
      vertical-align: 1px;
    }

    .nav button:hover { background: var(--sidebar-soft); color: var(--sidebar-text); }
    .nav button.is-active {
      background: #ffffff;
      color: var(--text);
      box-shadow: 0 10px 26px rgba(0, 0, 0, 0.16);
    }
    .nav button.is-active::before { opacity: 1; color: var(--accent); }

    main {
      min-width: 0;
      padding: 30px;
    }

    .section {
      display: none;
      width: 100%;
      max-width: 1260px;
      margin: 0;
    }
    .section.is-active { display: block; }

    .section-head {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 20px;
    }

    .section-title {
      margin: 0;
      font-size: 26px;
      line-height: 1.2;
      font-weight: 760;
    }

    .section-meta {
      margin-top: 5px;
      color: var(--muted);
      font-size: 13px;
      max-width: 820px;
    }

    .grid {
      display: grid;
      gap: 14px;
    }

    .stats-grid {
      grid-template-columns: repeat(auto-fit, minmax(188px, 1fr));
      margin-bottom: 22px;
    }

    .card {
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow-soft);
    }

    .stat-card {
      position: relative;
      min-height: 96px;
      overflow: hidden;
      padding: 15px 16px 14px 18px;
      background: linear-gradient(180deg, #ffffff 0%, #fbfcfe 100%);
      box-shadow: var(--shadow-soft);
    }

    .stat-card::before {
      content: "";
      position: absolute;
      inset: 0 auto 0 0;
      width: 4px;
      background: var(--stat-accent, var(--accent));
    }

    .stat-card[data-stat="total_checked"],
    .stat-card[data-stat="last_batch_checked"] { --stat-accent: var(--blue); }
    .stat-card[data-stat="total_available"],
    .stat-card[data-stat="last_batch_available"] { --stat-accent: var(--green); }
    .stat-card[data-stat="total_taken_invalid"] { --stat-accent: var(--red); }
    .stat-card[data-stat="total_unchecked"] { --stat-accent: var(--amber); }
    .stat-card[data-stat="total_used"] { --stat-accent: var(--violet); }

    .stat-label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 720;
      line-height: 1.25;
      text-transform: uppercase;
    }

    .stat-value {
      margin-top: 9px;
      font-size: 27px;
      line-height: 1;
      font-weight: 780;
      white-space: nowrap;
    }

    .toolbar {
      display: flex;
      flex-wrap: wrap;
      align-items: end;
      gap: 12px;
      margin-bottom: 16px;
      padding: 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow-soft);
    }

    label {
      display: grid;
      gap: 5px;
      min-width: 130px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 650;
    }

    input, select {
      min-height: 38px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #ffffff;
      color: var(--text);
      box-shadow: inset 0 1px 0 rgba(16, 23, 32, 0.03);
      transition: border-color 150ms ease, box-shadow 150ms ease;
    }

    input:hover, select:hover { border-color: var(--line-strong); }
    input:focus, select:focus, button:focus-visible {
      outline: 0;
      border-color: var(--accent);
      box-shadow: var(--focus);
    }

    input[type="checkbox"] {
      min-height: auto;
      width: 16px;
      height: 16px;
      padding: 0;
    }

    .check-label {
      display: inline-flex;
      grid-template-columns: none;
      align-items: center;
      min-width: auto;
      min-height: 38px;
      gap: 8px;
      color: var(--text);
      font-size: 13px;
    }

    .btn {
      min-height: 38px;
      padding: 8px 13px;
      border: 1px solid var(--line);
      border-radius: 7px;
      background: #fff;
      color: var(--text);
      cursor: pointer;
      font-weight: 720;
      white-space: nowrap;
      box-shadow: 0 1px 0 rgba(16, 23, 32, 0.05);
      transition: background 150ms ease, border-color 150ms ease, box-shadow 150ms ease, transform 150ms ease;
    }

    .btn:hover { border-color: var(--line-strong); box-shadow: var(--shadow-soft); transform: translateY(-1px); }
    .btn.primary { border-color: var(--accent); background: var(--accent); color: #fff; }
    .btn.primary:hover { background: var(--accent-strong); }
    .btn.danger { border-color: #f5b5af; background: #fff7f5; color: var(--red); }
    .btn:disabled { opacity: 0.55; cursor: not-allowed; }

    .panel {
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow-soft);
    }

    .split {
      display: grid;
      grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.75fr);
      gap: 16px;
      align-items: start;
    }

    .table-wrap {
      width: 100%;
      max-width: 100%;
      overflow: auto;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
      box-shadow: var(--shadow-soft);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      min-width: 780px;
      font-size: 13px;
    }

    th, td {
      padding: 11px 12px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: middle;
      white-space: nowrap;
    }

    th {
      background: #f5f8fb;
      color: var(--muted);
      font-size: 12px;
      font-weight: 760;
      position: sticky;
      top: 0;
      z-index: 1;
    }

    tbody tr:hover { background: #f8fbfb; }
    tr:last-child td { border-bottom: 0; }
    td.notes {
      max-width: 320px;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .mono {
      font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
    }

    .badge {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 8px;
      border-radius: 999px;
      border: 1px solid var(--line);
      background: #f8fafc;
      color: var(--muted);
      font-size: 12px;
      font-weight: 720;
      white-space: nowrap;
    }

    .badge.available { border-color: #bbf7d0; background: #ecfdf3; color: var(--green); }
    .badge.active { border-color: #bbf7d0; background: #ecfdf3; color: var(--green); }
    .badge.cooldown { border-color: #fed7aa; background: #fff7ed; color: var(--amber); }
    .badge.dead { border-color: #fecaca; background: #fef2f2; color: var(--red); }
    .badge.unchecked { border-color: #bfdbfe; background: #eff6ff; color: var(--blue); }
    .badge.used { border-color: #ddd6fe; background: #f5f3ff; color: var(--violet); }
    .badge.invalid, .badge.checked_taken, .badge.error { border-color: #fecaca; background: #fef2f2; color: var(--red); }
    .badge.warn { border-color: #fed7aa; background: #fff7ed; color: var(--amber); }

    .progress {
      height: 9px;
      overflow: hidden;
      border-radius: 999px;
      background: #e6edf2;
    }

    .progress > div {
      width: 0%;
      height: 100%;
      background: linear-gradient(90deg, var(--accent) 0%, #22c55e 100%);
      transition: width 180ms ease;
    }

    .status-line {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin: 10px 0;
      color: var(--muted);
      font-size: 13px;
    }

    .empty {
      padding: 18px;
      color: var(--muted);
      text-align: center;
    }

    .log-box {
      min-height: 420px;
      max-height: 70vh;
      margin: 0;
      overflow: auto;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #111820;
      color: #e5e7eb;
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 12px;
      box-shadow: var(--shadow-soft);
    }

    .selected-box {
      display: grid;
      gap: 10px;
    }

    .selected-name {
      font-size: 20px;
      font-weight: 760;
    }

    .auth-panel {
      display: grid;
      grid-template-columns: minmax(220px, 0.85fr) minmax(280px, 1.2fr) minmax(320px, 1.4fr);
      gap: 12px;
      align-items: start;
      margin-bottom: 14px;
    }

    .auth-summary {
      display: grid;
      gap: 8px;
      align-content: start;
    }

    .auth-actions {
      display: grid;
      grid-template-columns: repeat(2, minmax(150px, 1fr));
      gap: 10px;
      align-items: end;
    }

    .auth-panel input,
    .auth-panel select {
      width: 100%;
      min-width: 0;
    }

    .auth-panel .btn {
      min-width: 0;
      white-space: normal;
      line-height: 1.2;
    }

    .config-actions {
      grid-template-columns: repeat(2, minmax(150px, 1fr));
      margin-top: 10px;
    }

    .accounts-auth {
      grid-template-columns: minmax(360px, 1fr) minmax(360px, 1fr);
    }

    .accounts-auth .auth-actions {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    @media (max-width: 1040px) {
      .split { grid-template-columns: 1fr; }
      .auth-panel { grid-template-columns: 1fr; }
      .auth-actions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .config-actions { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }

    @media (max-width: 760px) {
      .app { grid-template-columns: 1fr; }
      .sidebar {
        position: static;
        height: auto;
        border-right: 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      }
      .nav { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      main { padding: 16px; }
      .section-head { display: block; }
      .stats-grid { grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); }
      label { min-width: 100%; }
      .btn { width: 100%; }
      .auth-actions { grid-template-columns: 1fr; }
    }

    @media (max-width: 520px) {
      .stats-grid { grid-template-columns: 1fr; }
      .section-title { font-size: 24px; }
    }
  </style>
</head>
<body>
  <div class="app">
    <aside class="sidebar">
      <div class="brand">
        <h1>Username Studio</h1>
        <span class="pill">local</span>
      </div>
      <nav class="nav" aria-label="Навигация">
        <button class="is-active" data-tab="dashboard">Dashboard</button>
        <button data-tab="generation">Генерация</button>
        <button data-tab="database">База</button>
        <button data-tab="telegram">Telegram</button>
        <button data-tab="accounts">Аккаунты</button>
        <button data-tab="channels">Канал</button>
        <button data-tab="logs">Логи</button>
      </nav>
    </aside>

    <main>
      <section id="dashboard" class="section is-active">
        <div class="section-head">
          <div>
            <h2 class="section-title">Dashboard</h2>
            <div class="section-meta" id="dashMeta">-</div>
          </div>
          <button class="btn" id="refreshDashboard">Обновить</button>
        </div>
        <div class="grid stats-grid" id="statsGrid"></div>
        <div class="split">
          <div>
            <div class="section-head">
              <h3 class="section-title" style="font-size:18px">Последний batch</h3>
            </div>
            <div class="table-wrap">
              <table>
                <thead><tr><th>username</th><th>score</th><th>status</th><th>type</th><th>batch</th></tr></thead>
                <tbody id="lastBatchRows"></tbody>
              </table>
            </div>
          </div>
          <div>
            <div class="section-head">
              <h3 class="section-title" style="font-size:18px">Available top</h3>
            </div>
            <div class="table-wrap">
              <table style="min-width:420px">
                <thead><tr><th>username</th><th>score</th><th>type</th></tr></thead>
                <tbody id="availableTopRows"></tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      <section id="generation" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">Генерация</h2>
            <div class="section-meta">LM Studio + локальная оценка, без Telegram-действий</div>
          </div>
        </div>
        <div class="panel" style="margin-bottom:14px">
          <div class="status-line" style="margin:0">
            <span>Активный аккаунт ротации</span>
            <span id="rotationAccountBadge" class="badge warn">loading</span>
          </div>
          <div id="rotationAccountDetails" class="section-meta" style="margin-top:8px">Проверка списка аккаунтов...</div>
        </div>
        <div class="toolbar">
          <label>Размер batch
            <input id="batchSize" type="number" min="1" max="500" value="100">
          </label>
          <label>Мин. длина
            <input id="generationMinLength" type="number" min="4" max="10" value="5">
          </label>
          <label>Макс. длина
            <input id="generationMaxLength" type="number" min="4" max="10" value="6">
          </label>
          <label class="check-label"><input id="generationAllowDigits" type="checkbox"> цифры</label>
          <button class="btn primary" id="generateBtn">Сгенерировать и оценить</button>
        </div>
        <div class="panel">
          <div class="status-line"><span id="generationStatus">Готово к запуску</span><span id="generationTaskId"></span></div>
          <div class="progress"><div id="generationProgress"></div></div>
        </div>
        <div class="table-wrap" style="margin-top:14px">
          <table>
            <thead><tr><th>username</th><th>score</th><th>status</th><th>generation_type</th><th>batch</th></tr></thead>
            <tbody id="generationRows"></tbody>
          </table>
        </div>
      </section>

      <section id="database" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">База username</h2>
            <div class="section-meta" id="databaseMeta">Лимит вывода включен</div>
          </div>
        </div>
        <div class="toolbar">
          <label>Статус
            <select id="dbStatus">
              <option value="all">Все</option>
              <option value="available">available</option>
              <option value="unchecked">unchecked</option>
              <option value="used">used</option>
              <option value="taken_invalid">checked_taken/invalid</option>
              <option value="checked">checked</option>
            </select>
          </label>
          <label>Поиск
            <input id="dbSearch" placeholder="username">
          </label>
          <label>Min score
            <input id="dbMinScore" type="number" step="0.1" min="0" max="10">
          </label>
          <label>Top N
            <input id="dbLimit" type="number" min="1" max="200" value="50">
          </label>
          <label class="check-label"><input id="dbLastBatch" type="checkbox"> last batch</label>
          <button class="btn primary" id="loadDatabase">Показать</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>username</th><th>score</th><th>status</th><th>generation_type</th><th>batch</th><th>checked_at</th><th>notes</th></tr></thead>
            <tbody id="databaseRows"></tbody>
          </table>
        </div>
      </section>

      <section id="telegram" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">Telegram-проверка</h2>
            <div class="section-meta" id="telegramMeta">Preview включен</div>
          </div>
        </div>
        <div class="auth-panel">
          <div class="panel auth-summary">
            <div class="status-line" style="margin:0">
              <span>Telegram аккаунт</span>
              <span id="tgAuthBadge" class="badge warn">checking</span>
            </div>
            <div id="tgAuthDetails" class="section-meta">Проверка сессии...</div>
            <button class="btn" id="tgAuthRefresh">Обновить статус</button>
          </div>
          <div class="panel">
            <div class="status-line" style="margin:0">
              <span>Telegram API</span>
              <span id="tgConfigBadge" class="badge warn">loading</span>
            </div>
            <div class="auth-actions config-actions">
              <label>API ID
                <input id="tgApiId" inputmode="numeric" autocomplete="off" placeholder="1234567">
              </label>
              <label>API HASH
                <input id="tgApiHash" type="password" autocomplete="off" placeholder="оставьте пустым, если уже сохранен">
              </label>
              <label>Телефон
                <input id="tgConfigPhone" autocomplete="tel" placeholder="+79990000000">
              </label>
              <button class="btn primary" id="tgSaveConfig">Сохранить API</button>
            </div>
            <div class="section-meta" id="tgConfigMessage" style="margin-top:10px">API ID и HASH нужны до отправки кода Telegram.</div>
          </div>
          <div class="panel">
            <div class="status-line" style="margin:0 0 10px">
              <span>Вход по коду</span>
            </div>
            <div class="auth-actions">
              <label>Телефон
                <input id="tgPhone" placeholder="+79990000000 или из .env">
              </label>
              <button class="btn" id="tgSendCode">Отправить код</button>
              <label>Код
                <input id="tgCode" inputmode="numeric" autocomplete="one-time-code" placeholder="12345">
              </label>
              <button class="btn primary" id="tgConfirmCode">Войти</button>
              <label>2FA пароль
                <input id="tgPassword" type="password" autocomplete="current-password" placeholder="если включен">
              </label>
              <button class="btn" id="tgConfirmPassword">Подтвердить 2FA</button>
              <button class="btn" id="tgCancelAuth">Сбросить вход</button>
              <button class="btn danger" id="tgResetSession">Сбросить сессию</button>
            </div>
            <div class="section-meta" id="tgAuthMessage" style="margin-top:10px">Код и пароль не сохраняются в браузере после отправки.</div>
          </div>
        </div>
        <div class="toolbar">
          <label>Manual username
            <input id="tgManualUsername" placeholder="@username">
          </label>
          <label>Лимит проверки
            <input id="tgLimit" type="number" min="1" max="30" value="10">
          </label>
          <label>Min score
            <input id="tgMinScore" type="number" step="0.1" min="0" max="10" value="6">
          </label>
          <label class="check-label"><input id="tgDryRun" type="checkbox" checked> dry-run</label>
          <label>Live confirm
            <input id="tgConfirm" placeholder="CHECK">
          </label>
          <button class="btn" id="tgPreviewBtn">Preview</button>
          <button class="btn primary" id="tgCheckBtn">Preview выбранных</button>
        </div>
        <div class="panel">
          <div class="status-line"><span id="telegramStatus">Кандидаты не загружены</span><span id="telegramTaskId"></span></div>
          <div class="progress"><div id="telegramProgress"></div></div>
        </div>
        <div class="split" style="margin-top:14px">
          <div class="table-wrap">
            <table>
              <thead><tr><th></th><th>username</th><th>score</th><th>status</th><th>type</th><th>batch</th></tr></thead>
              <tbody id="telegramRows"></tbody>
            </table>
          </div>
          <div class="table-wrap">
            <table style="min-width:420px">
              <thead><tr><th>skip</th><th>reason</th></tr></thead>
              <tbody id="telegramSkippedRows"></tbody>
            </table>
          </div>
        </div>
      </section>

      <section id="accounts" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">Аккаунты</h2>
            <div class="section-meta" id="accountsMeta">Мульти-аккаунты для ротации live-проверок</div>
          </div>
          <button class="btn primary" id="accountAddBtn">+ Добавить</button>
        </div>
        <div class="auth-panel accounts-auth" id="accountsAuthPanel">
          <div class="panel">
            <div class="status-line" style="margin:0">
              <span>Новый аккаунт</span>
              <span id="accountAuthBadge" class="badge warn">not started</span>
            </div>
            <div class="auth-actions config-actions">
              <label>API ID
                <input id="accountApiId" inputmode="numeric" autocomplete="off" placeholder="1234567">
              </label>
              <label>API HASH
                <input id="accountApiHash" type="password" autocomplete="off" placeholder="api_hash">
              </label>
              <label>Телефон
                <input id="accountPhone" autocomplete="tel" placeholder="+79990000000">
              </label>
              <button class="btn primary" id="accountSendCode">Отправить код</button>
            </div>
            <div class="section-meta" id="accountAuthMessage" style="margin-top:10px">API ID, API Hash и телефон сохраняются локально в sessions после успешного входа.</div>
          </div>
          <div class="panel">
            <div class="status-line" style="margin:0 0 10px">
              <span>Подтверждение входа</span>
            </div>
            <div class="auth-actions">
              <label>Код Telegram
                <input id="accountCode" inputmode="numeric" autocomplete="one-time-code" placeholder="12345">
              </label>
              <button class="btn primary" id="accountConfirmCode">Войти</button>
              <label id="accountPasswordLabel" hidden>2FA пароль
                <input id="accountPassword" type="password" autocomplete="current-password" placeholder="если включен">
              </label>
              <button class="btn" id="accountConfirmPassword" hidden>Подтвердить 2FA</button>
              <button class="btn" id="accountCancelAuth">Сбросить вход</button>
            </div>
          </div>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>телефон</th><th>status</th><th>cooldown</th><th>user</th><th>last error</th><th></th></tr></thead>
            <tbody id="accountsRows"></tbody>
          </table>
        </div>
      </section>

      <section id="channels" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">Создание канала</h2>
            <div class="section-meta">Только valid available username</div>
          </div>
        </div>
        <div class="toolbar">
          <label>Min score
            <input id="channelMinScore" type="number" step="0.1" min="0" max="10">
          </label>
          <label>Top N
            <input id="channelLimit" type="number" min="1" max="100" value="20">
          </label>
          <button class="btn" id="loadChannels">Обновить</button>
        </div>
        <div class="split">
          <div class="table-wrap">
            <table>
              <thead><tr><th>username</th><th>score</th><th>status</th><th>type</th><th></th></tr></thead>
              <tbody id="channelRows"></tbody>
            </table>
          </div>
          <div class="panel selected-box">
            <div class="selected-name" id="selectedChannelName">-</div>
            <div class="section-meta" id="selectedChannelScore">score: -</div>
            <label>Название канала
              <input id="channelTitle" placeholder="optional">
            </label>
            <label class="check-label"><input id="channelDryRun" type="checkbox" checked> dry-run</label>
            <label id="channelConfirmLabel">Использовать username? (y/n)
              <input id="channelConfirm" placeholder="y">
            </label>
            <button class="btn primary" id="createChannelBtn">Создать</button>
            <div class="status-line"><span id="channelStatus">Username не выбран</span><span id="channelTaskId"></span></div>
            <div class="progress"><div id="channelProgress"></div></div>
          </div>
        </div>
      </section>

      <section id="logs" class="section">
        <div class="section-head">
          <div>
            <h2 class="section-title">Логи</h2>
            <div class="section-meta" id="logsMeta">logs/logs.txt</div>
          </div>
        </div>
        <div class="toolbar">
          <label>Строк
            <input id="logLines" type="number" min="20" max="1000" value="160">
          </label>
          <button class="btn primary" id="refreshLogs">Обновить</button>
        </div>
        <pre class="log-box" id="logsBox"></pre>
      </section>
    </main>
  </div>

  <script>
    const $ = (selector) => document.querySelector(selector);
    const $$ = (selector) => Array.from(document.querySelectorAll(selector));
    const app = { config: {}, selectedChannel: null, telegramPreview: null, authFlowId: null, accountAuthFlowId: null };

    async function api(path, options = {}) {
      const response = await fetch(path, {
        headers: { "Content-Type": "application/json" },
        ...options
      });
      const data = await response.json();
      if (!response.ok) {
        const message = data.error || response.statusText;
        const error = new Error(message);
        error.data = data;
        throw error;
      }
      return data;
    }

    function fmtNumber(value) {
      if (value === null || value === undefined || value === "") return "0";
      return Number(value).toLocaleString("ru-RU", { maximumFractionDigits: 2 });
    }

    function fmtScore(value) {
      if (value === null || value === undefined || value === "") return "-";
      return Number(value).toFixed(2);
    }

    function badge(status) {
      const value = status || "unchecked";
      return `<span class="badge ${escapeHtml(value)}">${escapeHtml(value)}</span>`;
    }

    function escapeHtml(value) {
      return String(value ?? "").replace(/[&<>"']/g, (char) => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }[char]));
    }

    function rowHtml(row, extra = "") {
      return `<tr>${extra}<td class="mono">@${escapeHtml(row.username)}</td><td>${fmtScore(row.score)}</td><td>${badge(row.status)}</td><td>${escapeHtml(row.generation_type || "-")}</td><td>${escapeHtml(row.batch_num || "-")}</td></tr>`;
    }

    function setProgress(id, value) {
      $(id).style.width = `${Math.max(0, Math.min(100, Number(value) || 0))}%`;
    }

    function fmtCooldown(value) {
      const seconds = Number(value || 0);
      if (seconds <= 0) return "-";
      const minutes = Math.floor(seconds / 60);
      const rest = seconds % 60;
      return minutes ? `${minutes}m ${rest}s` : `${rest}s`;
    }

    function accountUserText(account) {
      const user = account?.user || {};
      const username = user.username ? `@${user.username}` : "без username";
      const name = `${user.first_name || ""} ${user.last_name || ""}`.trim();
      return name ? `${name} · ${username}` : username;
    }

    function renderRotationAccount(data) {
      const active = data.active_account;
      const badgeEl = $("#rotationAccountBadge");
      badgeEl.className = "badge";
      if (!data.has_accounts) {
        badgeEl.classList.add("warn");
        badgeEl.textContent = "fallback";
        $("#rotationAccountDetails").textContent = "Мульти-аккаунты не добавлены. Live-проверка использует старую Telegram-сессию из .env.";
        return;
      }
      if (!active) {
        badgeEl.classList.add("warn");
        badgeEl.textContent = "waiting";
        $("#rotationAccountDetails").textContent = "Аккаунты загружены, активный появится после старта live-проверки.";
        return;
      }
      badgeEl.classList.add(active.status || "active");
      badgeEl.textContent = active.status || "active";
      const cooldown = active.cooldown_remaining ? ` · cooldown ${fmtCooldown(active.cooldown_remaining)}` : "";
      $("#rotationAccountDetails").textContent = `${active.phone || "-"} · ${accountUserText(active)}${cooldown}`;
    }

    function renderAccounts(data) {
      const accounts = data.accounts || [];
      $("#accountsMeta").textContent = accounts.length
        ? `Загружено аккаунтов: ${accounts.length}`
        : "Мульти-аккаунты не добавлены";
      renderRotationAccount(data);
      $("#accountsRows").innerHTML = accounts.length ? accounts.map((account) => `
        <tr>
          <td class="mono">${escapeHtml(account.phone || "-")}</td>
          <td>${badge(account.status || "active")}</td>
          <td>${escapeHtml(fmtCooldown(account.cooldown_remaining))}</td>
          <td>${escapeHtml(accountUserText(account))}</td>
          <td class="notes">${escapeHtml(account.last_error || "")}</td>
          <td><button class="btn danger" data-delete-account="${escapeHtml(account.account_id)}">Удалить</button></td>
        </tr>
      `).join("") : `<tr><td colspan="6" class="empty">Нет аккаунтов</td></tr>`;
      $$("[data-delete-account]").forEach((button) => button.addEventListener("click", () => deleteAccount(button.dataset.deleteAccount)));
    }

    async function loadAccounts() {
      const data = await api("/api/accounts");
      renderAccounts(data);
      return data;
    }

    function resetAccountAuthForm(clearCredentials = false) {
      app.accountAuthFlowId = null;
      $("#accountCode").value = "";
      $("#accountPassword").value = "";
      $("#accountPasswordLabel").hidden = true;
      $("#accountConfirmPassword").hidden = true;
      if (clearCredentials) {
        $("#accountApiId").value = "";
        $("#accountApiHash").value = "";
        $("#accountPhone").value = "";
      }
    }

    function setAccountAuthBadge(status) {
      const badgeEl = $("#accountAuthBadge");
      badgeEl.className = "badge";
      badgeEl.classList.add(status === "authorized" ? "active" : "warn");
      badgeEl.textContent = status;
    }

    async function startAccountAuth() {
      setAccountAuthBadge("sending");
      $("#accountAuthMessage").textContent = "Отправка кода Telegram...";
      try {
        const data = await api("/api/accounts/auth", {
          method: "POST",
          body: JSON.stringify({
            action: "start",
            api_id: $("#accountApiId").value.trim(),
            api_hash: $("#accountApiHash").value.trim(),
            phone: $("#accountPhone").value.trim()
          })
        });
        const auth = data.auth || {};
        if (auth.authorized || auth.already_authorized) {
          resetAccountAuthForm(true);
          setAccountAuthBadge("authorized");
          $("#accountAuthMessage").textContent = "Аккаунт авторизован и готов к ротации.";
        } else {
          app.accountAuthFlowId = auth.flow_id;
          setAccountAuthBadge("code sent");
          $("#accountAuthMessage").textContent = `Код отправлен на ${auth.phone || "телефон"}. Введите код справа.`;
        }
        renderAccounts(data);
      } catch (error) {
        setAccountAuthBadge("error");
        $("#accountAuthMessage").textContent = error.data?.message || error.data?.error || error.message;
      }
    }

    async function confirmAccountCode() {
      if (!app.accountAuthFlowId) {
        $("#accountAuthMessage").textContent = "Сначала отправьте код.";
        return;
      }
      setAccountAuthBadge("checking");
      try {
        const data = await api("/api/accounts/auth", {
          method: "POST",
          body: JSON.stringify({
            action: "code",
            flow_id: app.accountAuthFlowId,
            code: $("#accountCode").value.trim()
          })
        });
        const auth = data.auth || {};
        $("#accountCode").value = "";
        if (auth.password_required) {
          $("#accountPasswordLabel").hidden = false;
          $("#accountConfirmPassword").hidden = false;
          setAccountAuthBadge("2FA");
          $("#accountAuthMessage").textContent = auth.message || "Введите 2FA-пароль.";
          return;
        }
        resetAccountAuthForm(true);
        setAccountAuthBadge("authorized");
        $("#accountAuthMessage").textContent = "Аккаунт добавлен.";
        renderAccounts(data);
      } catch (error) {
        setAccountAuthBadge("error");
        $("#accountAuthMessage").textContent = error.data?.message || error.data?.error || error.message;
      }
    }

    async function confirmAccountPassword() {
      if (!app.accountAuthFlowId) {
        $("#accountAuthMessage").textContent = "Нет активного входа.";
        return;
      }
      setAccountAuthBadge("checking");
      try {
        const data = await api("/api/accounts/auth", {
          method: "POST",
          body: JSON.stringify({
            action: "password",
            flow_id: app.accountAuthFlowId,
            password: $("#accountPassword").value
          })
        });
        resetAccountAuthForm(true);
        setAccountAuthBadge("authorized");
        $("#accountAuthMessage").textContent = "Аккаунт добавлен.";
        renderAccounts(data);
      } catch (error) {
        $("#accountPassword").value = "";
        setAccountAuthBadge("error");
        $("#accountAuthMessage").textContent = error.data?.message || error.data?.error || error.message;
      }
    }

    async function cancelAccountAuth() {
      if (app.accountAuthFlowId) {
        await api("/api/accounts/auth", {
          method: "POST",
          body: JSON.stringify({ action: "cancel", flow_id: app.accountAuthFlowId })
        }).catch(() => {});
      }
      resetAccountAuthForm(false);
      setAccountAuthBadge("not started");
      $("#accountAuthMessage").textContent = "Вход сброшен.";
    }

    async function deleteAccount(accountId) {
      if (!confirm("Удалить аккаунт и его локальную сессию?")) return;
      try {
        const data = await api("/api/accounts/delete", {
          method: "POST",
          body: JSON.stringify({ account_id: accountId })
        });
        renderAccounts(data);
      } catch (error) {
        $("#accountsMeta").textContent = error.data?.message || error.data?.error || error.message;
      }
    }

    async function loadConfig() {
      const data = await api("/api/config");
      app.config = data;
      $("#batchSize").value = data.batch_size;
      $("#generationMinLength").value = data.generation_min_length || data.username_min_length || 5;
      $("#generationMaxLength").value = data.generation_max_length || data.username_max_length || 6;
      $("#generationAllowDigits").checked = Boolean(data.generation_allow_digits);
      $("#tgMinScore").value = data.score_threshold;
      $("#tgLimit").max = data.max_telegram_checks;
    }

    async function loadDashboard() {
      const data = await api("/api/stats");
      const stats = data.stats || {};
      const items = [
        ["total_evaluated", "Всего оценено"],
        ["total_checked", "Проверено в Telegram"],
        ["total_available", "Доступных"],
        ["total_taken_invalid", "Занятых/невалидных"],
        ["total_used", "Использованных"],
        ["total_unchecked", "Непроверенных"],
        ["avg_score", "Средний score"],
        ["best_score", "Лучший score"],
        ["last_batch_num", "Последний batch"],
        ["last_batch_count", "Username в batch"],
        ["last_batch_checked", "Batch checked"],
        ["last_batch_available", "Batch available"]
      ];
      $("#statsGrid").innerHTML = items.map(([key, label]) => `
        <article class="card stat-card" data-stat="${key}">
          <div class="stat-label">${label}</div>
          <div class="stat-value">${fmtNumber(stats[key])}</div>
        </article>
      `).join("");
      $("#dashMeta").textContent = `Обновлено: ${new Date().toLocaleTimeString("ru-RU")}`;
      await loadMiniTables();
    }

    async function loadMiniTables() {
      const last = await api("/api/usernames?last_batch=1&limit=10");
      $("#lastBatchRows").innerHTML = last.rows.length
        ? last.rows.map((row) => rowHtml(row)).join("")
        : `<tr><td colspan="5" class="empty">Нет данных</td></tr>`;

      const available = await api("/api/usernames?status=available&valid_only=1&limit=10");
      $("#availableTopRows").innerHTML = available.rows.length
        ? available.rows.map((row) => `<tr><td class="mono">@${escapeHtml(row.username)}</td><td>${fmtScore(row.score)}</td><td>${escapeHtml(row.generation_type || "-")}</td></tr>`).join("")
        : `<tr><td colspan="3" class="empty">Нет данных</td></tr>`;
    }

    async function loadDatabase() {
      const params = new URLSearchParams();
      params.set("status", $("#dbStatus").value);
      params.set("limit", $("#dbLimit").value || "50");
      if ($("#dbSearch").value.trim()) params.set("search", $("#dbSearch").value.trim());
      if ($("#dbMinScore").value) params.set("min_score", $("#dbMinScore").value);
      if ($("#dbLastBatch").checked) params.set("last_batch", "1");
      const data = await api(`/api/usernames?${params.toString()}`);
      $("#databaseMeta").textContent = data.has_more ? `Показано ${data.total_visible}, есть еще` : `Показано ${data.total_visible}`;
      $("#databaseRows").innerHTML = data.rows.length ? data.rows.map((row) => `
        <tr>
          <td class="mono">@${escapeHtml(row.username)}</td>
          <td>${fmtScore(row.score)}</td>
          <td>${badge(row.status)}</td>
          <td>${escapeHtml(row.generation_type || "-")}</td>
          <td>${escapeHtml(row.batch_num || "-")}</td>
          <td>${escapeHtml(row.checked_at || "-")}</td>
          <td class="notes">${escapeHtml(row.notes || "")}</td>
        </tr>
      `).join("") : `<tr><td colspan="7" class="empty">Нет данных</td></tr>`;
    }

    async function startGeneration() {
      $("#generateBtn").disabled = true;
      $("#generationStatus").textContent = "Запуск...";
      setProgress("#generationProgress", 1);
      try {
        const data = await api("/api/generate", {
          method: "POST",
          body: JSON.stringify({
            batch_size: Number($("#batchSize").value || app.config.batch_size || 100),
            min_length: Number($("#generationMinLength").value || 5),
            max_length: Number($("#generationMaxLength").value || 6),
            allow_digits: $("#generationAllowDigits").checked
          })
        });
        $("#generationTaskId").textContent = data.task.id;
        await pollTask(data.task.id, renderGenerationTask);
      } catch (error) {
        $("#generationStatus").textContent = error.message;
      } finally {
        $("#generateBtn").disabled = false;
        await loadDashboard();
      }
    }

    function renderGenerationTask(task) {
      $("#generationStatus").textContent = task.message || task.status;
      setProgress("#generationProgress", task.progress || 0);
      if (task.status === "completed" && task.result) {
        const rows = task.result.rows || [];
        $("#generationRows").innerHTML = rows.length
          ? rows.map((row) => rowHtml(row)).join("")
          : `<tr><td colspan="5" class="empty">Нет результатов</td></tr>`;
      }
      if (task.status === "failed") {
        $("#generationRows").innerHTML = `<tr><td colspan="5" class="empty">${escapeHtml(task.error || "Ошибка")}</td></tr>`;
      }
    }

    async function loadTelegramAuthStatus() {
      const data = await api("/api/telegram/auth/status");
      renderTelegramAuth(data.auth || {});
      return data.auth || {};
    }

    async function loadTelegramConfig() {
      const data = await api("/api/telegram/config");
      renderTelegramConfig(data.telegram_config || {});
      return data.telegram_config || {};
    }

    function renderTelegramConfig(configData) {
      const badge = $("#tgConfigBadge");
      badge.className = "badge";
      const configured = Boolean(configData.api_id && configData.api_hash_set);
      badge.classList.add(configured ? "available" : "warn");
      badge.textContent = configured ? "configured" : "not ready";
      $("#tgApiId").value = configData.api_id || "";
      $("#tgConfigPhone").value = configData.phone || "";
      $("#tgApiHash").value = "";
      $("#tgApiHash").placeholder = configData.api_hash_set
        ? "сохранен, оставьте пустым чтобы не менять"
        : "вставьте TELEGRAM_API_HASH";
      if (!$("#tgPhone").value.trim() && configData.phone) {
        $("#tgPhone").value = configData.phone;
      }
      $("#tgConfigMessage").textContent = configured
        ? `Сессия: ${configData.session_name || "telegram_session"}`
        : "Заполните API ID и API HASH, затем сохраните.";
    }

    async function saveTelegramConfig() {
      $("#tgConfigMessage").textContent = "Сохранение Telegram API...";
      try {
        const data = await api("/api/telegram/config", {
          method: "POST",
          body: JSON.stringify({
            api_id: $("#tgApiId").value.trim(),
            api_hash: $("#tgApiHash").value.trim(),
            phone: $("#tgConfigPhone").value.trim()
          })
        });
        const cfg = data.telegram_config || {};
        renderTelegramConfig(cfg);
        $("#tgPhone").value = cfg.phone || "";
        $("#tgConfigMessage").textContent = cfg.api_hash_changed
          ? "API настройки сохранены. Если это новый аккаунт, сбросьте сессию и войдите заново."
          : "API ID/телефон сохранены. API HASH не менялся.";
        await loadTelegramAuthStatus();
      } catch (error) {
        $("#tgConfigMessage").textContent = error.data?.message || error.message;
      }
    }

    function renderTelegramAuth(auth) {
      const badge = $("#tgAuthBadge");
      badge.className = "badge";
      if (!auth.configured) {
        badge.classList.add("invalid");
        badge.textContent = "not configured";
        $("#tgAuthDetails").textContent = auth.error || "Заполните TELEGRAM_API_ID и TELEGRAM_API_HASH в .env";
        return;
      }

      if (auth.authorized && auth.session_matches_config === false) {
        const user = auth.user || {};
        badge.classList.add("invalid");
        badge.textContent = "wrong account";
        const username = user.username ? `@${user.username}` : "без username";
        $("#tgAuthDetails").textContent = auth.error || `Текущая сессия ${username} не совпадает с телефоном из .env`;
      } else if (auth.authorized) {
        const user = auth.user || {};
        badge.classList.add("available");
        badge.textContent = "authorized";
        const username = user.username ? `@${user.username}` : "без username";
        const name = `${user.first_name || ""} ${user.last_name || ""}`.trim();
        $("#tgAuthDetails").textContent = `${name || username} · ${username} · id ${user.id || "-"}`;
      } else {
        badge.classList.add("warn");
        badge.textContent = "login required";
        $("#tgAuthDetails").textContent = auth.error || `Сессия ${auth.session_name || "telegram_session"} не авторизована`;
      }
    }

    async function sendTelegramCode() {
      $("#tgAuthMessage").textContent = "Отправка кода...";
      try {
        const data = await api("/api/telegram/auth/start", {
          method: "POST",
          body: JSON.stringify({ phone: $("#tgPhone").value.trim() })
        });
        const auth = data.auth || {};
        if (auth.already_authorized || auth.authorized) {
          renderTelegramAuth(auth);
          $("#tgAuthMessage").textContent = "Аккаунт уже авторизован";
          return;
        }
        app.authFlowId = auth.flow_id;
        $("#tgAuthMessage").textContent = `Код отправлен на ${auth.phone || "телефон"}. Введите код и нажмите "Войти".`;
      } catch (error) {
        $("#tgAuthMessage").textContent = error.message;
      }
    }

    async function confirmTelegramCode() {
      if (!app.authFlowId) {
        $("#tgAuthMessage").textContent = "Сначала отправьте код";
        return;
      }
      $("#tgAuthMessage").textContent = "Проверка кода...";
      try {
        const data = await api("/api/telegram/auth/confirm", {
          method: "POST",
          body: JSON.stringify({ flow_id: app.authFlowId, code: $("#tgCode").value.trim() })
        });
        const auth = data.auth || {};
        $("#tgCode").value = "";
        if (auth.password_required) {
          $("#tgAuthMessage").textContent = auth.message || "Введите 2FA-пароль";
          return;
        }
        app.authFlowId = null;
        renderTelegramAuth(auth);
        $("#tgAuthMessage").textContent = "Вход выполнен";
      } catch (error) {
        $("#tgAuthMessage").textContent = error.message;
      }
    }

    async function confirmTelegramPassword() {
      if (!app.authFlowId) {
        $("#tgAuthMessage").textContent = "Нет активного входа";
        return;
      }
      $("#tgAuthMessage").textContent = "Проверка 2FA...";
      try {
        const data = await api("/api/telegram/auth/password", {
          method: "POST",
          body: JSON.stringify({ flow_id: app.authFlowId, password: $("#tgPassword").value })
        });
        $("#tgPassword").value = "";
        app.authFlowId = null;
        renderTelegramAuth(data.auth || {});
        $("#tgAuthMessage").textContent = "Вход выполнен";
      } catch (error) {
        $("#tgPassword").value = "";
        $("#tgAuthMessage").textContent = error.message;
      }
    }

    async function cancelTelegramAuth() {
      if (app.authFlowId) {
        await api("/api/telegram/auth/cancel", {
          method: "POST",
          body: JSON.stringify({ flow_id: app.authFlowId })
        }).catch(() => {});
      }
      app.authFlowId = null;
      $("#tgCode").value = "";
      $("#tgPassword").value = "";
      $("#tgAuthMessage").textContent = "Вход сброшен";
      await loadTelegramAuthStatus();
    }

    async function resetTelegramSession() {
      if (!confirm("Сбросить локальную Telegram-сессию и войти заново?")) return;
      $("#tgAuthMessage").textContent = "Сброс Telegram-сессии...";
      try {
        await api("/api/telegram/auth/reset-session", {
          method: "POST",
          body: JSON.stringify({})
        });
        app.authFlowId = null;
        $("#tgCode").value = "";
        $("#tgPassword").value = "";
        $("#tgAuthMessage").textContent = "Сессия сброшена. Отправьте код для нового входа.";
        await loadTelegramAuthStatus();
      } catch (error) {
        $("#tgAuthMessage").textContent = error.message;
      }
    }

    async function loadTelegramPreview() {
      const params = new URLSearchParams();
      params.set("limit", $("#tgLimit").value || "10");
      params.set("min_score", $("#tgMinScore").value || app.config.score_threshold || "6");
      const manualUsername = $("#tgManualUsername").value.trim();
      if (manualUsername) params.set("username", manualUsername);
      const data = await api(`/api/telegram/preview?${params.toString()}`);
      app.telegramPreview = data;
      $("#telegramMeta").textContent = `${data.source}: ${data.candidate_count} candidates, ${data.skipped_count} skipped`;
      $("#telegramStatus").textContent = "Preview готов";
      $("#telegramRows").innerHTML = data.candidates.length ? data.candidates.map((row) => `
        <tr>
          <td><input type="checkbox" class="tgPick" value="${escapeHtml(row.username)}" checked></td>
          <td class="mono">@${escapeHtml(row.username)}</td>
          <td>${fmtScore(row.score)}</td>
          <td>${badge(row.status)}</td>
          <td>${escapeHtml(row.generation_type || "-")}</td>
          <td>${escapeHtml(row.batch_num || "-")}</td>
        </tr>
      `).join("") : `<tr><td colspan="6" class="empty">Нет кандидатов</td></tr>`;
      $("#telegramSkippedRows").innerHTML = data.skipped.length ? data.skipped.map((item) => `
        <tr><td class="mono">@${escapeHtml(item.username)}</td><td>${escapeHtml(item.reason)}</td></tr>
      `).join("") : `<tr><td colspan="2" class="empty">Нет пропусков</td></tr>`;
    }

    async function checkTelegramSelected() {
      const usernames = $$(".tgPick:checked").map((input) => input.value);
      const manualUsername = $("#tgManualUsername").value.trim().replace(/^@/, "").toLowerCase();
      if (manualUsername && !usernames.includes(manualUsername)) usernames.unshift(manualUsername);
      $("#telegramStatus").textContent = "Подготовка...";
      setProgress("#telegramProgress", 1);
      const dryRun = $("#tgDryRun").checked;
      if (!dryRun && $("#tgConfirm").value.trim() !== "CHECK") {
        $("#telegramStatus").textContent = "Для live-проверки введите CHECK";
        return;
      }
      try {
        const data = await api("/api/telegram/check", {
          method: "POST",
          body: JSON.stringify({
            usernames,
            limit: Number($("#tgLimit").value || 10),
            min_score: Number($("#tgMinScore").value || app.config.score_threshold || 6),
            dry_run: dryRun,
            confirm: $("#tgConfirm").value.trim()
          })
        });
        if (data.dry_run) {
          $("#telegramStatus").textContent = data.message;
          app.telegramPreview = data.preview;
          return;
        }
        $("#telegramTaskId").textContent = data.task.id;
        const finishedTask = await pollTask(data.task.id, renderTelegramTask);
        await loadDashboard();
        if (finishedTask.status === "completed" && finishedTask.result) {
          const checked = finishedTask.result.checked_count || 0;
          const available = finishedTask.result.available_count || 0;
          $("#telegramStatus").textContent = `Проверка завершена: ${checked} проверено, ${available} доступны`;
          $("#telegramMeta").textContent = "Показаны результаты live-проверки. Для следующих unchecked нажмите Preview.";
        }
      } catch (error) {
        $("#telegramStatus").textContent = error.data?.message || error.message;
      }
    }

    function syncTelegramMode() {
      const dryRun = $("#tgDryRun").checked;
      $("#tgCheckBtn").textContent = dryRun ? "Preview выбранных" : "Проверить выбранные live";
      $("#telegramMeta").textContent = dryRun ? "Preview включен" : "Live режим: введите CHECK";
      $("#tgConfirm").disabled = dryRun;
    }

    function renderTelegramTask(task) {
      $("#telegramStatus").textContent = task.message || task.status;
      setProgress("#telegramProgress", task.progress || 0);
      loadAccounts().catch(() => {});
      if (task.status === "completed" && task.result) {
        $("#telegramRows").innerHTML = (task.result.rows || []).map((row) => `
          <tr>
            <td></td>
            <td class="mono">@${escapeHtml(row.username)}</td>
            <td>${fmtScore(row.score)}</td>
            <td>${badge(row.status)}</td>
            <td>${escapeHtml(row.generation_type || "-")}</td>
            <td>${escapeHtml(row.batch_num || "-")}</td>
          </tr>
        `).join("");
      }
    }

    async function loadChannels() {
      const params = new URLSearchParams();
      params.set("limit", $("#channelLimit").value || "20");
      if ($("#channelMinScore").value) params.set("min_score", $("#channelMinScore").value);
      const data = await api(`/api/channels/available?${params.toString()}`);
      $("#channelRows").innerHTML = data.rows.length ? data.rows.map((row) => `
        <tr>
          <td class="mono">@${escapeHtml(row.username)}</td>
          <td>${fmtScore(row.score)}</td>
          <td>${badge(row.status)}</td>
          <td>${escapeHtml(row.generation_type || "-")}</td>
          <td><button class="btn" data-channel="${escapeHtml(row.username)}" data-score="${escapeHtml(row.score)}">Выбрать</button></td>
        </tr>
      `).join("") : `<tr><td colspan="5" class="empty">Нет available username</td></tr>`;
      $$("[data-channel]").forEach((button) => button.addEventListener("click", () => selectChannel(button.dataset.channel, button.dataset.score)));
    }

    function selectChannel(username, score) {
      app.selectedChannel = { username, score };
      $("#selectedChannelName").textContent = `@${username}`;
      $("#selectedChannelScore").textContent = `score: ${fmtScore(score)}`;
      $("#channelTitle").value = username;
      $("#channelConfirmLabel").firstChild.textContent = `Использовать ${username} (score: ${fmtScore(score)})? (y/n)`;
      $("#channelStatus").textContent = "Готово к preview";
    }

    async function createChannel() {
      if (!app.selectedChannel) {
        $("#channelStatus").textContent = "Username не выбран";
        return;
      }
      $("#channelStatus").textContent = "Подготовка...";
      setProgress("#channelProgress", 1);
      try {
        const data = await api("/api/channels/create", {
          method: "POST",
          body: JSON.stringify({
            username: app.selectedChannel.username,
            title: $("#channelTitle").value.trim(),
            dry_run: $("#channelDryRun").checked,
            confirm: $("#channelConfirm").value.trim()
          })
        });
        if (data.dry_run) {
          $("#channelStatus").textContent = data.message;
          return;
        }
        $("#channelTaskId").textContent = data.task.id;
        await pollTask(data.task.id, renderChannelTask);
        await loadDashboard();
        await loadChannels();
      } catch (error) {
        $("#channelStatus").textContent = error.data?.message || error.data?.reason || error.message;
      }
    }

    function renderChannelTask(task) {
      $("#channelStatus").textContent = task.message || task.status;
      setProgress("#channelProgress", task.progress || 0);
      if (task.status === "completed" && task.result) {
        $("#channelStatus").textContent = `Создан канал ID ${task.result.channel_id}`;
      }
    }

    async function pollTask(taskId, render) {
      for (;;) {
        const data = await api(`/api/tasks/${taskId}`);
        const task = data.task;
        render(task);
        if (task.status !== "running") return task;
        await new Promise((resolve) => setTimeout(resolve, 1200));
      }
    }

    async function loadLogs() {
      const lines = $("#logLines").value || "160";
      const data = await api(`/api/logs?lines=${encodeURIComponent(lines)}`);
      $("#logsMeta").textContent = data.path;
      $("#logsBox").textContent = data.text || "";
      $("#logsBox").scrollTop = $("#logsBox").scrollHeight;
    }

    function bindEvents() {
      $$(".nav button").forEach((button) => {
        button.addEventListener("click", () => {
          $$(".nav button").forEach((item) => item.classList.remove("is-active"));
          $$(".section").forEach((item) => item.classList.remove("is-active"));
          button.classList.add("is-active");
          $(`#${button.dataset.tab}`).classList.add("is-active");
        });
      });
      $("#refreshDashboard").addEventListener("click", loadDashboard);
      $("#loadDatabase").addEventListener("click", loadDatabase);
      $("#dbSearch").addEventListener("keydown", (event) => { if (event.key === "Enter") loadDatabase(); });
      $("#generateBtn").addEventListener("click", startGeneration);
      $("#tgSaveConfig").addEventListener("click", saveTelegramConfig);
      $("#tgAuthRefresh").addEventListener("click", loadTelegramAuthStatus);
      $("#tgSendCode").addEventListener("click", sendTelegramCode);
      $("#tgConfirmCode").addEventListener("click", confirmTelegramCode);
      $("#tgConfirmPassword").addEventListener("click", confirmTelegramPassword);
      $("#tgCancelAuth").addEventListener("click", cancelTelegramAuth);
      $("#tgResetSession").addEventListener("click", resetTelegramSession);
      $("#tgCode").addEventListener("keydown", (event) => { if (event.key === "Enter") confirmTelegramCode(); });
      $("#tgPassword").addEventListener("keydown", (event) => { if (event.key === "Enter") confirmTelegramPassword(); });
      $("#tgPreviewBtn").addEventListener("click", loadTelegramPreview);
      $("#tgCheckBtn").addEventListener("click", checkTelegramSelected);
      $("#tgDryRun").addEventListener("change", syncTelegramMode);
      $("#accountAddBtn").addEventListener("click", () => {
        resetAccountAuthForm(true);
        setAccountAuthBadge("not started");
        $("#accountAuthMessage").textContent = "Введите API ID, API Hash и телефон.";
        $("#accountApiId").focus();
      });
      $("#accountSendCode").addEventListener("click", startAccountAuth);
      $("#accountConfirmCode").addEventListener("click", confirmAccountCode);
      $("#accountConfirmPassword").addEventListener("click", confirmAccountPassword);
      $("#accountCancelAuth").addEventListener("click", cancelAccountAuth);
      $("#accountCode").addEventListener("keydown", (event) => { if (event.key === "Enter") confirmAccountCode(); });
      $("#accountPassword").addEventListener("keydown", (event) => { if (event.key === "Enter") confirmAccountPassword(); });
      $("#loadChannels").addEventListener("click", loadChannels);
      $("#createChannelBtn").addEventListener("click", createChannel);
      $("#refreshLogs").addEventListener("click", loadLogs);
    }

    async function init() {
      bindEvents();
      syncTelegramMode();
      await loadConfig();
      await Promise.all([loadDashboard(), loadDatabase(), loadTelegramConfig(), loadTelegramAuthStatus(), loadAccounts(), loadTelegramPreview(), loadChannels(), loadLogs()]);
    }

    init().catch((error) => {
      console.error(error);
      $("#dashMeta").textContent = error.message;
    });
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    args = parse_args()
    run_server(args.host, args.port, open_browser=not args.no_browser)

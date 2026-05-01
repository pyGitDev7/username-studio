"""Telegram authorization helpers for the web dashboard."""
from __future__ import annotations

import asyncio
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import config
import utils
from .payloads import (
    get_account_manager,
    get_accounts_payload,
    mask_phone,
    now_iso,
    refresh_config,
)


_telegram_session_lock = threading.RLock()
_auth_lock = threading.Lock()
_auth_flows: Dict[str, Dict[str, Any]] = {}
AUTH_FLOW_TTL_SECONDS = 10 * 60
ENV_PATH = Path(".env")
TELEGRAM_ENV_KEYS = ["TELEGRAM_API_ID", "TELEGRAM_API_HASH", "TELEGRAM_PHONE"]


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


def require_main_telegram_authorized() -> Optional[Dict[str, Any]]:
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
        "message": "Сначала войдите в основной Telegram-аккаунт для создания каналов.",
        "auth": status,
    }


def require_checker_accounts() -> Optional[Dict[str, Any]]:
    accounts = get_account_manager().list_accounts()
    active_accounts = [account for account in accounts if account.get("status") == "active"]
    if active_accounts:
        return None

    if accounts:
        return {
            "error": "telegram_checker_accounts_unavailable",
            "message": "Для live-проверки нет активных аккаунтов. Дождитесь cooldown или добавьте аккаунт во вкладке Аккаунты.",
            "accounts": accounts,
        }

    return {
        "error": "telegram_checker_accounts_required",
        "message": "Live-проверка выполняется только через аккаунты из вкладки Аккаунты. Основной аккаунт используется только для создания каналов.",
        "accounts": accounts,
    }

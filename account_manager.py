"""
Multi-account Telegram session management.
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from threading import RLock
from typing import Any, Dict, List, Optional

from telethon import TelegramClient
from telethon import errors as telethon_errors
from telethon.errors import SessionPasswordNeededError

import utils
from logger import logger


SESSIONS_DIR = Path("sessions")
AUTH_FLOW_TTL_SECONDS = 10 * 60


def _now_iso() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def _clean_phone(phone: str) -> str:
    phone = str(phone or "").strip()
    if not phone:
        return ""
    if phone.startswith("+"):
        return "+" + utils.normalize_phone(phone)
    return phone


def _account_id_from_phone(phone: str) -> str:
    normalized = utils.normalize_phone(phone)
    if not normalized:
        raise ValueError("Введите полный номер телефона")
    return normalized


def _auth_error_types() -> tuple[type[BaseException], ...]:
    names = (
        "AuthKeyError",
        "AuthKeyInvalidError",
        "AuthKeyNotFound",
        "AuthKeyUnregisteredError",
        "SessionExpiredError",
        "SessionRevokedError",
        "UserDeactivatedError",
        "UserDeactivatedBanError",
        "PhoneNumberBannedError",
    )
    return tuple(getattr(telethon_errors, name) for name in names if hasattr(telethon_errors, name))


AUTH_ERROR_TYPES = _auth_error_types()


def is_auth_error(exc: BaseException) -> bool:
    if AUTH_ERROR_TYPES and isinstance(exc, AUTH_ERROR_TYPES):
        return True
    name = type(exc).__name__.lower()
    return (
        "authkey" in name
        or "sessionexpired" in name
        or "sessionrevoked" in name
        or "deactivated" in name
        or "banned" in name
    )


@dataclass
class Account:
    account_id: str
    phone: str
    api_id: int
    api_hash: str
    session_name: str
    status: str = "active"
    cooldown_until: float = 0.0
    last_error: str = ""
    user: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    last_used_at: str = ""

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Account":
        return cls(
            account_id=str(data.get("account_id") or _account_id_from_phone(data.get("phone", ""))),
            phone=str(data.get("phone") or ""),
            api_id=int(data.get("api_id") or 0),
            api_hash=str(data.get("api_hash") or ""),
            session_name=str(data.get("session_name") or ""),
            status=str(data.get("status") or "active"),
            cooldown_until=float(data.get("cooldown_until") or 0),
            last_error=str(data.get("last_error") or ""),
            user=dict(data.get("user") or {}),
            created_at=str(data.get("created_at") or _now_iso()),
            updated_at=str(data.get("updated_at") or _now_iso()),
            last_used_at=str(data.get("last_used_at") or ""),
        )

    @property
    def cooldown_remaining(self) -> int:
        if self.status != "cooldown":
            return 0
        return max(0, int(round(self.cooldown_until - time.time())))

    @property
    def effective_status(self) -> str:
        if self.status == "cooldown" and self.cooldown_remaining <= 0:
            return "active"
        return self.status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "account_id": self.account_id,
            "phone": self.phone,
            "api_id": self.api_id,
            "api_hash": self.api_hash,
            "session_name": self.session_name,
            "status": self.status,
            "cooldown_until": self.cooldown_until,
            "last_error": self.last_error,
            "user": self.user,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_used_at": self.last_used_at,
        }

    def to_public_dict(self) -> Dict[str, Any]:
        status = self.effective_status
        return {
            "account_id": self.account_id,
            "phone": self.phone,
            "api_id": self.api_id,
            "api_hash_set": bool(self.api_hash),
            "session_name": self.session_name,
            "status": status,
            "stored_status": self.status,
            "cooldown_until": self.cooldown_until,
            "cooldown_remaining": self.cooldown_remaining if status == "cooldown" else 0,
            "last_error": self.last_error,
            "user": self.user,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "last_used_at": self.last_used_at,
        }


class AccountManager:
    """Loads Telegram accounts and chooses an account for username checks."""

    def __init__(self, sessions_dir: Path | str = SESSIONS_DIR):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)
        self._lock = RLock()
        self._accounts: Dict[str, Account] = {}
        self._cursor = 0
        self.active_account_id: Optional[str] = None
        self._auth_flows: Dict[str, Dict[str, Any]] = {}
        self.load_accounts()

    def load_accounts(self) -> List[Account]:
        with self._lock:
            accounts: Dict[str, Account] = {}
            for path in sorted(self.sessions_dir.glob("*.json")):
                try:
                    data = json.loads(path.read_text(encoding="utf-8"))
                    account = Account.from_dict(data)
                    if not account.session_name:
                        account.session_name = str(self._session_base(account.account_id))
                    accounts[account.account_id] = account
                except Exception as exc:
                    logger.warning(f"Не удалось загрузить аккаунт {path}: {exc}")
            self._accounts = accounts
            self._normalize_expired_cooldowns(save=True)
            return list(self._accounts.values())

    def has_accounts(self) -> bool:
        with self._lock:
            self._normalize_expired_cooldowns(save=True)
            return any(account.effective_status != "dead" for account in self._accounts.values())

    def has_active_accounts(self) -> bool:
        with self._lock:
            self._normalize_expired_cooldowns(save=True)
            return any(account.effective_status == "active" for account in self._accounts.values())

    def list_accounts(self) -> List[Dict[str, Any]]:
        with self._lock:
            self._normalize_expired_cooldowns(save=True)
            return [account.to_public_dict() for account in sorted(self._accounts.values(), key=lambda item: item.phone)]

    def get_active_account(self) -> Optional[Dict[str, Any]]:
        with self._lock:
            account = self._accounts.get(self.active_account_id or "")
            return account.to_public_dict() if account else None

    def get_available_account(self, exclude: Optional[set[str]] = None) -> Optional[Account]:
        exclude = exclude or set()
        with self._lock:
            self._normalize_expired_cooldowns(save=True)
            accounts = [account for account in self._accounts.values() if account.effective_status == "active" and account.account_id not in exclude]
            if not accounts:
                return None
            accounts.sort(key=lambda item: item.account_id)
            account = accounts[self._cursor % len(accounts)]
            self._cursor = (self._cursor + 1) % max(len(accounts), 1)
            self.active_account_id = account.account_id
            account.last_used_at = _now_iso()
            self._save_account(account)
            return account

    def set_cooldown(self, account: Account, seconds: int, reason: str) -> None:
        seconds = max(1, int(seconds))
        with self._lock:
            current = self._accounts.get(account.account_id, account)
            current.status = "cooldown"
            current.cooldown_until = time.time() + seconds
            current.last_error = reason
            current.updated_at = _now_iso()
            self._accounts[current.account_id] = current
            self._save_account(current)

    def mark_dead(self, account: Account, reason: str) -> None:
        with self._lock:
            current = self._accounts.get(account.account_id, account)
            current.status = "dead"
            current.cooldown_until = 0
            current.last_error = reason
            current.updated_at = _now_iso()
            self._accounts[current.account_id] = current
            self._save_account(current)

    def mark_active(self, account: Account) -> None:
        with self._lock:
            current = self._accounts.get(account.account_id, account)
            current.status = "active"
            current.cooldown_until = 0
            current.last_error = ""
            current.updated_at = _now_iso()
            self._accounts[current.account_id] = current
            self.active_account_id = current.account_id
            self._save_account(current)

    def delete_account(self, account_id: str) -> bool:
        account_id = str(account_id or "").strip()
        with self._lock:
            account = self._accounts.pop(account_id, None)
            if not account:
                return False
            if self.active_account_id == account_id:
                self.active_account_id = None

        for path in self._account_paths(account_id):
            try:
                if path.exists():
                    path.unlink()
            except Exception as exc:
                logger.warning(f"Не удалось удалить {path}: {exc}")
        return True

    async def start_auth(self, api_id: Any, api_hash: Any, phone: str) -> Dict[str, Any]:
        api_id_int = self._validate_api_id(api_id)
        api_hash_text = str(api_hash or "").strip()
        if not api_hash_text:
            raise ValueError("Введите API Hash")
        phone_text = _clean_phone(phone)
        account_id = _account_id_from_phone(phone_text)
        session_name = str(self._session_base(account_id))

        client = TelegramClient(session_name, api_id_int, api_hash_text)
        try:
            await client.connect()
            if await client.is_user_authorized():
                account = await self._save_authorized_client(client, account_id, phone_text, api_id_int, api_hash_text, session_name)
                return {
                    "already_authorized": True,
                    "authorized": True,
                    "account": account.to_public_dict(),
                }

            sent = await client.send_code_request(phone_text)
            flow_id = uuid.uuid4().hex[:12]
            with self._lock:
                self._auth_flows[flow_id] = {
                    "flow_id": flow_id,
                    "account_id": account_id,
                    "phone": phone_text,
                    "api_id": api_id_int,
                    "api_hash": api_hash_text,
                    "session_name": session_name,
                    "phone_code_hash": sent.phone_code_hash,
                    "created_at": _now_iso(),
                    "created_ts": time.time(),
                    "password_required": False,
                }
            return {
                "flow_id": flow_id,
                "phone": phone_text,
                "expires_in": AUTH_FLOW_TTL_SECONDS,
                "code_type": type(getattr(sent, "type", None)).__name__,
            }
        finally:
            await client.disconnect()

    async def confirm_code(self, flow_id: str, code: str) -> Dict[str, Any]:
        flow = self._get_auth_flow(flow_id)
        code = str(code or "").strip().replace(" ", "")
        if not code:
            raise ValueError("Введите код Telegram")

        client = TelegramClient(flow["session_name"], flow["api_id"], flow["api_hash"])
        try:
            await client.connect()
            try:
                await client.sign_in(
                    phone=flow["phone"],
                    code=code,
                    phone_code_hash=flow["phone_code_hash"],
                )
            except SessionPasswordNeededError:
                with self._lock:
                    if flow_id in self._auth_flows:
                        self._auth_flows[flow_id]["password_required"] = True
                return {
                    "authorized": False,
                    "password_required": True,
                    "flow_id": flow_id,
                    "message": "Нужен 2FA-пароль Telegram",
                }

            account = await self._save_authorized_client(
                client,
                flow["account_id"],
                flow["phone"],
                flow["api_id"],
                flow["api_hash"],
                flow["session_name"],
            )
            with self._lock:
                self._auth_flows.pop(flow_id, None)
            return {"authorized": True, "account": account.to_public_dict()}
        finally:
            await client.disconnect()

    async def confirm_password(self, flow_id: str, password: str) -> Dict[str, Any]:
        flow = self._get_auth_flow(flow_id)
        password = str(password or "")
        if not password:
            raise ValueError("Введите 2FA-пароль Telegram")

        client = TelegramClient(flow["session_name"], flow["api_id"], flow["api_hash"])
        try:
            await client.connect()
            await client.sign_in(password=password)
            account = await self._save_authorized_client(
                client,
                flow["account_id"],
                flow["phone"],
                flow["api_id"],
                flow["api_hash"],
                flow["session_name"],
            )
            with self._lock:
                self._auth_flows.pop(flow_id, None)
            return {"authorized": True, "account": account.to_public_dict()}
        finally:
            await client.disconnect()

    async def add_account_interactive(self, api_id: Any, api_hash: str, phone: str) -> Account:
        started = await self.start_auth(api_id, api_hash, phone)
        if started.get("account"):
            return Account.from_dict({**started["account"], "api_hash": api_hash})

        flow_id = started["flow_id"]
        code = input("Введите код Telegram: ").strip()
        confirmed = await self.confirm_code(flow_id, code)
        if confirmed.get("password_required"):
            password = input("Введите 2FA-пароль Telegram: ")
            confirmed = await self.confirm_password(flow_id, password)

        account_id = (confirmed.get("account") or {}).get("account_id")
        with self._lock:
            account = self._accounts[account_id]
        return account

    def cancel_auth(self, flow_id: str) -> bool:
        with self._lock:
            return self._auth_flows.pop(str(flow_id or ""), None) is not None

    def _normalize_expired_cooldowns(self, save: bool = False) -> None:
        for account in self._accounts.values():
            if account.status == "cooldown" and account.cooldown_remaining <= 0:
                account.status = "active"
                account.cooldown_until = 0
                account.updated_at = _now_iso()
                if save:
                    self._save_account(account)

    async def _save_authorized_client(
        self,
        client: TelegramClient,
        account_id: str,
        phone: str,
        api_id: int,
        api_hash: str,
        session_name: str,
    ) -> Account:
        me = await client.get_me()
        actual_phone = getattr(me, "phone", "") or ""
        if not utils.telegram_phone_matches(actual_phone, phone):
            raise RuntimeError("Авторизованная сессия принадлежит другому телефону")

        user = {
            "id": getattr(me, "id", None),
            "first_name": getattr(me, "first_name", "") or "",
            "last_name": getattr(me, "last_name", "") or "",
            "username": getattr(me, "username", "") or "",
            "phone": actual_phone or phone,
        }
        now = _now_iso()
        with self._lock:
            existing = self._accounts.get(account_id)
            account = Account(
                account_id=account_id,
                phone=phone,
                api_id=api_id,
                api_hash=api_hash,
                session_name=session_name,
                status="active",
                cooldown_until=0,
                last_error="",
                user=user,
                created_at=existing.created_at if existing else now,
                updated_at=now,
                last_used_at=existing.last_used_at if existing else "",
            )
            self._accounts[account_id] = account
            self.active_account_id = account_id
            self._save_account(account)
            return account

    def _get_auth_flow(self, flow_id: str) -> Dict[str, Any]:
        flow_id = str(flow_id or "").strip()
        cutoff = time.time() - AUTH_FLOW_TTL_SECONDS
        with self._lock:
            expired = [key for key, flow in self._auth_flows.items() if flow.get("created_ts", 0) < cutoff]
            for key in expired:
                self._auth_flows.pop(key, None)
            flow = dict(self._auth_flows.get(flow_id) or {})
        if not flow:
            raise RuntimeError("Сессия входа истекла. Отправьте код заново.")
        return flow

    def _save_account(self, account: Account) -> None:
        account.updated_at = _now_iso()
        path = self.sessions_dir / f"{account.account_id}.json"
        path.write_text(json.dumps(account.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")

    def _session_base(self, account_id: str) -> Path:
        return self.sessions_dir / account_id

    def _account_paths(self, account_id: str) -> List[Path]:
        base = self._session_base(account_id)
        return [
            self.sessions_dir / f"{account_id}.json",
            Path(str(base) + ".session"),
            Path(str(base) + ".session-journal"),
            Path(str(base) + ".session-shm"),
            Path(str(base) + ".session-wal"),
            *self.sessions_dir.glob(f"{account_id}.session-*"),
        ]

    @staticmethod
    def _validate_api_id(api_id: Any) -> int:
        try:
            value = int(str(api_id or "").strip())
        except ValueError as exc:
            raise ValueError("API ID должен быть числом") from exc
        if value <= 0:
            raise ValueError("API ID должен быть положительным числом")
        return value

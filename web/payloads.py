"""Payload builders and shared helpers for the web dashboard."""
from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import config
import utils
from account_manager import AccountManager
from storage import UsernameStorage


DEFAULT_TABLE_LIMIT = 50
MAX_TABLE_LIMIT = 200

_storage: Optional[UsernameStorage] = None
_storage_lock = threading.Lock()
_account_manager: Optional[AccountManager] = None
_account_manager_lock = threading.RLock()


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

def get_accounts_payload() -> Dict[str, Any]:
    manager = get_account_manager()
    manager.load_accounts()
    return {
        "accounts": manager.list_accounts(),
        "active_account": manager.get_active_account(),
        "has_accounts": manager.has_accounts(),
        "has_active_accounts": manager.has_active_accounts(),
    }

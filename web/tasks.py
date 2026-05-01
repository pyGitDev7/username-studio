"""Background task state and task runners for the web dashboard."""
from __future__ import annotations

import asyncio
import threading
import traceback
import uuid
from typing import Any, Callable, Dict, List, Optional, Tuple

import utils
from .payloads import (
    MAX_TABLE_LIMIT,
    api_row,
    get_account_manager,
    get_storage,
    now_iso,
)
from .telegram_auth import _telegram_session_lock


_task_lock = threading.Lock()
_tasks: Dict[str, Dict[str, Any]] = {}
_active_task_id: Optional[str] = None


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

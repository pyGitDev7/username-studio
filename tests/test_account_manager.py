import json
import time

from account_manager import AccountManager


def write_account(
    sessions_dir,
    account_id,
    *,
    phone=None,
    status="active",
    cooldown_until=0,
):
    payload = {
        "account_id": account_id,
        "phone": phone or f"+7999000{account_id}",
        "api_id": 12345,
        "api_hash": "test_hash",
        "session_name": str(sessions_dir / account_id),
        "status": status,
        "cooldown_until": cooldown_until,
        "last_error": "",
        "user": {"id": int(account_id), "phone": phone or f"7999000{account_id}"},
        "created_at": "2026-01-01 00:00:00",
        "updated_at": "2026-01-01 00:00:00",
        "last_used_at": "",
    }
    (sessions_dir / f"{account_id}.json").write_text(
        json.dumps(payload),
        encoding="utf-8",
    )
    return payload


def accounts_by_id(manager):
    return {item["account_id"]: item for item in manager.list_accounts()}


def test_loads_accounts_and_exposes_public_statuses(tmp_path):
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    write_account(sessions_dir, "1001", status="active")
    write_account(sessions_dir, "1002", status="cooldown", cooldown_until=time.time() + 60)
    write_account(sessions_dir, "1003", status="dead")

    manager = AccountManager(sessions_dir)
    accounts = accounts_by_id(manager)

    assert accounts["1001"]["status"] == "active"
    assert accounts["1002"]["status"] == "cooldown"
    assert accounts["1002"]["cooldown_remaining"] > 0
    assert accounts["1003"]["status"] == "dead"
    assert manager.has_accounts()
    assert manager.has_active_accounts()


def test_cooldown_expiration_reactivates_and_persists_account(tmp_path):
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    write_account(sessions_dir, "1001", status="cooldown", cooldown_until=time.time() - 1)

    manager = AccountManager(sessions_dir)

    assert manager.has_active_accounts()
    assert accounts_by_id(manager)["1001"]["status"] == "active"
    saved = json.loads((sessions_dir / "1001.json").read_text(encoding="utf-8"))
    assert saved["status"] == "active"
    assert saved["cooldown_until"] == 0


def test_has_active_accounts_ignores_future_cooldown_and_dead_accounts(tmp_path):
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    write_account(sessions_dir, "1001", status="cooldown", cooldown_until=time.time() + 300)
    write_account(sessions_dir, "1002", status="dead")

    manager = AccountManager(sessions_dir)

    assert manager.has_accounts()
    assert not manager.has_active_accounts()
    assert manager.get_available_account() is None


def test_get_available_account_rotates_active_accounts_only(tmp_path):
    sessions_dir = tmp_path / "sessions"
    sessions_dir.mkdir()
    write_account(sessions_dir, "1001", status="active")
    write_account(sessions_dir, "1002", status="active")
    write_account(sessions_dir, "1003", status="dead")

    manager = AccountManager(sessions_dir)

    first = manager.get_available_account()
    second = manager.get_available_account()
    third = manager.get_available_account(exclude={first.account_id, second.account_id})

    assert [first.account_id, second.account_id] == ["1001", "1002"]
    assert third is None
    assert manager.active_account_id == "1002"

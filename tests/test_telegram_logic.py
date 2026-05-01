import asyncio

import main


class NoActiveAccounts:
    def has_active_accounts(self):
        return False


class ActiveAccounts:
    def has_active_accounts(self):
        return True


class StorageSpy:
    def __init__(self):
        self.added = []

    def get_score(self, username):
        return 6.0

    def add_checked_username(self, **kwargs):
        self.added.append(kwargs)
        return True


def make_system(account_manager):
    system = main.UsernameGenerationSystem.__new__(main.UsernameGenerationSystem)
    system.no_telegram = False
    system.dry_run = False
    system.account_manager = account_manager
    system.storage = StorageSpy()
    system.batch_num = 42
    return system


def test_live_check_without_active_accounts_does_not_start_rotation(monkeypatch):
    async def fail_if_called(*args, **kwargs):
        raise AssertionError("Telegram rotation must not start without active checker accounts")

    monkeypatch.setattr(main, "check_batch_with_rotation", fail_if_called)
    monkeypatch.setattr(main, "create_telegram_manager", lambda: (_ for _ in ()).throw(AssertionError("main .env account must not be used")))

    system = make_system(NoActiveAccounts())
    result = asyncio.run(system.check_availability_batch([{"username": "noria", "score": 9.0}]))

    assert result == {}
    assert system.storage.added == []


def test_live_check_with_active_accounts_saves_rotation_results(monkeypatch):
    async def fake_check_batch_with_rotation(usernames, account_manager, progress_callback=None):
        assert usernames == ["noria", "lumen"]
        assert isinstance(account_manager, ActiveAccounts)
        if progress_callback:
            progress_callback("noria", {"available": True, "status": "available"}, 1, 2)
        return {
            "noria": {"available": True, "status": "available", "notes": "ok"},
            "lumen": {"available": False, "status": "checked_taken", "notes": "taken"},
        }

    monkeypatch.setattr(main, "check_batch_with_rotation", fake_check_batch_with_rotation)
    system = make_system(ActiveAccounts())

    result = asyncio.run(system.check_availability_batch([
        {"username": "noria", "score": 9.0, "generation_type": "brandable"},
        {"username": "lumen", "score": 8.0, "generation_type": "multilingual", "batch_num": 5},
    ]))

    assert result["noria"]["available"] is True
    assert result["lumen"]["status"] == "checked_taken"
    assert system.storage.added == [
        {
            "username": "noria",
            "available": True,
            "score": 9.0,
            "generation_type": "brandable",
            "notes": "ok",
            "status": "available",
            "batch_num": 42,
        },
        {
            "username": "lumen",
            "available": False,
            "score": 8.0,
            "generation_type": "multilingual",
            "notes": "taken",
            "status": "checked_taken",
            "batch_num": 5,
        },
    ]

import web_app


class FakeAccountManager:
    def __init__(self, accounts):
        self._accounts = accounts

    def list_accounts(self):
        return self._accounts


def test_require_checker_accounts_accepts_active_account(monkeypatch):
    monkeypatch.setattr(web_app, "get_account_manager", lambda: FakeAccountManager([
        {"account_id": "1001", "status": "active"},
    ]))

    assert web_app.require_checker_accounts() is None


def test_require_checker_accounts_requires_at_least_one_account(monkeypatch):
    monkeypatch.setattr(web_app, "get_account_manager", lambda: FakeAccountManager([]))

    error = web_app.require_checker_accounts()

    assert error["error"] == "telegram_checker_accounts_required"
    assert error["accounts"] == []
    assert "Основной аккаунт" in error["message"]


def test_require_checker_accounts_rejects_only_cooldown_or_dead_accounts(monkeypatch):
    accounts = [
        {"account_id": "1001", "status": "cooldown"},
        {"account_id": "1002", "status": "dead"},
    ]
    monkeypatch.setattr(web_app, "get_account_manager", lambda: FakeAccountManager(accounts))

    error = web_app.require_checker_accounts()

    assert error["error"] == "telegram_checker_accounts_unavailable"
    assert error["accounts"] == accounts


def test_require_main_telegram_authorized_accepts_ready_session(monkeypatch):
    monkeypatch.setattr(web_app, "get_telegram_auth_status", lambda: {
        "authorized": True,
        "ready": True,
    })

    assert web_app.require_main_telegram_authorized() is None


def test_require_main_telegram_authorized_reports_wrong_account(monkeypatch):
    status = {
        "authorized": True,
        "ready": False,
        "needs_relogin": True,
        "error": "wrong session",
    }
    monkeypatch.setattr(web_app, "get_telegram_auth_status", lambda: status)

    error = web_app.require_main_telegram_authorized()

    assert error["error"] == "telegram_wrong_account"
    assert error["auth"] == status


def test_require_main_telegram_authorized_requires_login(monkeypatch):
    status = {
        "authorized": False,
        "ready": False,
        "needs_relogin": False,
    }
    monkeypatch.setattr(web_app, "get_telegram_auth_status", lambda: status)

    error = web_app.require_main_telegram_authorized()

    assert error["error"] == "telegram_login_required"
    assert error["auth"] == status

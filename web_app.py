"""
Compatibility launcher for the local browser dashboard.

The implementation lives in the ``web`` package. Keep this module importable so
``python web_app.py`` and older imports from ``web_app`` continue to work.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from web.handlers import UsernameDashboardHandler
from web.payloads import (
    DEFAULT_TABLE_LIMIT,
    MAX_TABLE_LIMIT,
    api_row,
    build_check_preview,
    clamp_int,
    classify_check_rows,
    clean_username_list,
    first_query,
    get_account_manager,
    get_accounts_payload,
    get_channel_candidates,
    get_storage,
    get_usernames_payload,
    mask_phone,
    now_iso,
    parse_bool,
    parse_float,
    read_log_lines,
    refresh_config,
)
from web.server import (
    HOST,
    PORT,
    SERVER_RUN_TOKEN,
    ReusableThreadingHTTPServer,
    close_browser_client,
    create_server,
    monitor_browser_clients,
    parse_args,
    register_browser_client,
    run_server,
)
from web.tasks import (
    fail_task,
    finish_task,
    run_channel_create_task,
    run_generation_task,
    run_telegram_check_task,
    start_task,
    update_task,
    validate_channel_username,
)
from web.telegram_auth import (
    _clean_env_value,
    account_auth_action,
    build_telegram_auth_status_from_client,
    cleanup_auth_flows,
    confirm_telegram_code,
    confirm_telegram_code_async,
    confirm_telegram_password,
    confirm_telegram_password_async,
    delete_account_payload,
    get_auth_flow,
    get_telegram_auth_status,
    get_telegram_auth_status_async,
    get_telegram_config_payload,
    reset_telegram_session,
    save_telegram_config,
    start_telegram_auth,
    start_telegram_auth_async,
    telegram_session_path,
    write_env_values,
)
from web.templates import INDEX_HTML


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


if __name__ == "__main__":
    args = parse_args()
    run_server(args.host, args.port, open_browser=not args.no_browser)

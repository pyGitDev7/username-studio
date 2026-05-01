"""Server lifecycle and browser-client tracking for the web dashboard."""
from __future__ import annotations

import argparse
import threading
import time
import uuid
import webbrowser
from http.server import ThreadingHTTPServer
from typing import Any, Dict, Optional


HOST = "127.0.0.1"
PORT = 8080

SERVER_RUN_TOKEN = uuid.uuid4().hex
CLIENT_HEARTBEAT_TIMEOUT_SECONDS = 15
CLIENT_SHUTDOWN_GRACE_SECONDS = 4
_client_lock = threading.RLock()
_active_clients: Dict[str, float] = {}
_client_seen = False
_shutdown_timer: Optional[threading.Timer] = None
_shutdown_requested = False


def _browser_client_id(payload: Dict[str, Any]) -> str:
    if str(payload.get("server_token") or "") != SERVER_RUN_TOKEN:
        raise ValueError("stale browser client")
    return str(payload.get("client_id") or "").strip()[:80]


def _cleanup_stale_clients_locked(now: Optional[float] = None) -> None:
    current = now or time.time()
    stale_ids = [
        client_id for client_id, last_seen in _active_clients.items()
        if current - last_seen > CLIENT_HEARTBEAT_TIMEOUT_SECONDS
    ]
    for client_id in stale_ids:
        _active_clients.pop(client_id, None)


def _cancel_pending_shutdown_locked() -> None:
    global _shutdown_requested, _shutdown_timer

    if _shutdown_timer is not None:
        _shutdown_timer.cancel()
        _shutdown_timer = None
    _shutdown_requested = False


def _schedule_server_shutdown(server: ThreadingHTTPServer, reason: str) -> bool:
    global _shutdown_requested, _shutdown_timer

    with _client_lock:
        _cleanup_stale_clients_locked()
        if not _client_seen or _active_clients:
            return False
        if _shutdown_requested:
            return True

        _shutdown_requested = True

        def shutdown_server() -> None:
            print(f"Stopping dashboard: {reason}", flush=True)
            server.shutdown()

        _shutdown_timer = threading.Timer(CLIENT_SHUTDOWN_GRACE_SECONDS, shutdown_server)
        _shutdown_timer.daemon = True
        _shutdown_timer.start()
        return True


def _client_payload(shutdown_scheduled: bool = False) -> Dict[str, Any]:
    with _client_lock:
        _cleanup_stale_clients_locked()
        return {
            "active_clients": len(_active_clients),
            "shutdown_scheduled": shutdown_scheduled or _shutdown_requested,
            "heartbeat_timeout": CLIENT_HEARTBEAT_TIMEOUT_SECONDS,
        }


def register_browser_client(payload: Dict[str, Any]) -> Dict[str, Any]:
    global _client_seen

    client_id = _browser_client_id(payload)
    if not client_id:
        raise ValueError("client_id is required")

    with _client_lock:
        _client_seen = True
        _active_clients[client_id] = time.time()
        _cancel_pending_shutdown_locked()
    return _client_payload()


def close_browser_client(payload: Dict[str, Any], server: ThreadingHTTPServer) -> Dict[str, Any]:
    client_id = _browser_client_id(payload)
    with _client_lock:
        if client_id:
            _active_clients.pop(client_id, None)
        _cleanup_stale_clients_locked()
    return _client_payload(_schedule_server_shutdown(server, "browser closed"))


def monitor_browser_clients(server: ThreadingHTTPServer, stop_event: threading.Event) -> None:
    while not stop_event.wait(2):
        with _client_lock:
            _cleanup_stale_clients_locked()
            idle = _client_seen and not _active_clients
        if idle:
            _schedule_server_shutdown(server, "browser heartbeat stopped")

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
    from .handlers import UsernameDashboardHandler

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
    monitor_stop = threading.Event()
    monitor = threading.Thread(
        target=monitor_browser_clients,
        args=(server, monitor_stop),
        name="browser-client-monitor",
        daemon=True,
    )
    monitor.start()
    url = f"http://{host}:{server.server_address[1]}"
    print(f"Username dashboard: {url}", flush=True)
    if open_browser:
        threading.Timer(0.7, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard...", flush=True)
    finally:
        monitor_stop.set()
        server.server_close()

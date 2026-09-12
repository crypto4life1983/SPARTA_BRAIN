"""Launcher for the SPARTA Commander Telegram bot (long-poll loop).

Thin wrapper around sparta_commander.telegram_bot_runtime.run_bot, which is the
ONE module permitted to talk to the Telegram Bot API. This launcher adds no
network code, no credential handling and no new capability: it only starts the
existing hardened loop, writes a heartbeat/log locally, and exits cleanly.

Safety, unchanged from the runtime it starts:
  * fails closed without local_secrets/telegram_bot_token.txt and
    local_secrets/telegram_allowed_users.json (no polling, safe error);
  * replies only to the originating chat of an allowed user;
  * never executes an approved action, never starts/stops a bot, never trades;
  * the token is never printed, logged or written by this launcher.

CLI:
    python tools/run_sparta_commander_telegram_bot.py            # run until stopped
    python tools/run_sparta_commander_telegram_bot.py --check    # preflight only, no polling
    python tools/run_sparta_commander_telegram_bot.py --max-cycles 1
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from sparta_commander.telegram_bot_runtime import (  # noqa: E402
    ALLOWED_USERS_PATH,
    TOKEN_PATH,
    TelegramRuntimeError,
    load_allowed_users,
    load_token,
    run_bot,
)

LOG_DIR = _REPO_ROOT / "logs" / "telegram_bot"
HEARTBEAT = LOG_DIR / "heartbeat.json"
LOCK_PATH = LOG_DIR / "bot.lock"


def _pid_alive(pid: int) -> bool:
    """True if a process with this pid exists (Windows-safe, no psutil)."""
    if pid <= 0:
        return False
    try:
        import ctypes
        h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)  # QUERY_LIMITED_INFORMATION
        if not h:
            return False
        ctypes.windll.kernel32.CloseHandle(h)
        return True
    except Exception:
        try:
            import os
            os.kill(pid, 0)
            return True
        except Exception:
            return False


def acquire_lock(path: Path = LOCK_PATH) -> bool:
    """Single-instance guard: two long-poll loops on one bot token conflict
    (Telegram serves getUpdates to one caller at a time). Returns False when a
    live instance already holds the lock; stale locks are reclaimed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            try:
                held = json.loads(path.read_text(encoding="utf-8"))
                pid = int(held.get("pid", -1))
            except Exception:
                pid = -1
            import os as _os
            if pid > 0 and pid != _os.getpid() and _pid_alive(pid):
                return False
        import os as _os
        path.write_text(json.dumps({"pid": _os.getpid(), "at": _stamp()}), encoding="utf-8")
        return True
    except Exception:
        return True  # never let lock bookkeeping stop a legitimate start


def release_lock(path: Path = LOCK_PATH) -> None:
    try:
        import os as _os
        if path.exists():
            held = json.loads(path.read_text(encoding="utf-8"))
            if int(held.get("pid", -1)) == _os.getpid():
                path.unlink()
    except Exception:
        pass


def _stamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _write(event: str, **fields) -> None:
    """Local-only log line. Never contains the token."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        payload = {"at": _stamp(), "event": event, **fields}
        with (LOG_DIR / "runtime.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload) + "\n")
        HEARTBEAT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception:
        pass


def preflight() -> tuple[bool, str]:
    """Credentials present and well formed? Returns (ok, message). No network call."""
    try:
        token = load_token(TOKEN_PATH)
        allowed = load_allowed_users(ALLOWED_USERS_PATH)
    except TelegramRuntimeError as exc:
        return False, f"fail-closed: {exc}"
    except Exception as exc:  # unreadable secret file, bad JSON, ...
        return False, f"fail-closed: {type(exc).__name__}"
    if not token or not allowed:
        return False, "fail-closed: token or allowed-users missing"
    return True, f"ready: {len(allowed)} allowed user(s)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Start the SPARTA Commander Telegram bot")
    ap.add_argument("--check", action="store_true", help="preflight only; do not poll")
    ap.add_argument("--max-cycles", type=int, default=None, help="stop after N poll cycles")
    args = ap.parse_args(argv)

    ok, msg = preflight()
    print(f"[commander-bot] preflight {msg}")
    _write("preflight", ok=ok, detail=msg)
    if not ok:
        return 2
    if args.check:
        return 0

    if not acquire_lock():
        print("[commander-bot] another instance is already polling; exiting")
        _write("skipped", reason="already_running")
        return 0

    _write("start", max_cycles=args.max_cycles)
    print(f"[commander-bot] polling started {_stamp()} (Ctrl+C to stop)")
    try:
        result = run_bot(root=_REPO_ROOT, max_cycles=args.max_cycles)
    except KeyboardInterrupt:
        _write("stopped", reason="keyboard_interrupt")
        print("[commander-bot] stopped")
        return 0
    except TelegramRuntimeError as exc:
        _write("stopped", reason="runtime_error", detail=str(exc)[:200])
        print(f"[commander-bot] fail-closed: {exc}")
        return 2
    except Exception as exc:
        _write("stopped", reason=type(exc).__name__)
        print(f"[commander-bot] stopped on {type(exc).__name__}")
        return 1
    finally:
        release_lock()
    _write("exited", processed=(result or {}).get("processed"), cycles=(result or {}).get("cycles"))
    print(f"[commander-bot] exited cleanly: {json.dumps(result or {})[:200]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

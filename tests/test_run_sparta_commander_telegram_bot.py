"""Launcher guards for the SPARTA Commander Telegram bot.

The launcher must never weaken the runtime's hardened invariants: it fails closed
without local secrets, never logs the token, and refuses to start a second
long-poll loop on the same bot token.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools import run_sparta_commander_telegram_bot as launcher  # noqa: E402


def test_lock_is_single_instance(tmp_path: Path):
    lock = tmp_path / "bot.lock"
    assert launcher.acquire_lock(lock) is True
    assert json.loads(lock.read_text())["pid"] == os.getpid()
    # same process re-acquiring is fine (idempotent restart within one process)
    assert launcher.acquire_lock(lock) is True
    # a different, live pid holds it -> refuse
    lock.write_text(json.dumps({"pid": _other_live_pid(), "at": "x"}), encoding="utf-8")
    assert launcher.acquire_lock(lock) is False


def _other_live_pid() -> int:
    """A pid that exists and is not us: the parent process (or pid 4, System)."""
    ppid = os.getppid()
    return ppid if ppid and ppid != os.getpid() and launcher._pid_alive(ppid) else 4


def test_stale_lock_is_reclaimed(tmp_path: Path):
    lock = tmp_path / "bot.lock"
    lock.write_text(json.dumps({"pid": 999999, "at": "x"}), encoding="utf-8")  # dead pid
    assert launcher.acquire_lock(lock) is True
    assert json.loads(lock.read_text())["pid"] == os.getpid()


def test_corrupt_lock_is_reclaimed(tmp_path: Path):
    lock = tmp_path / "bot.lock"
    lock.write_text("not json", encoding="utf-8")
    assert launcher.acquire_lock(lock) is True


def test_release_only_removes_own_lock(tmp_path: Path):
    lock = tmp_path / "bot.lock"
    launcher.acquire_lock(lock)
    launcher.release_lock(lock)
    assert not lock.exists()
    lock.write_text(json.dumps({"pid": 4, "at": "x"}), encoding="utf-8")  # someone else's
    launcher.release_lock(lock)
    assert lock.exists()


def test_preflight_fails_closed_without_secrets(monkeypatch, tmp_path: Path):
    def boom(*a, **k):
        raise launcher.TelegramRuntimeError("token file missing")
    monkeypatch.setattr(launcher, "load_token", boom)
    ok, msg = launcher.preflight()
    assert ok is False and "fail-closed" in msg


def test_preflight_reports_allowed_user_count_without_token(monkeypatch):
    monkeypatch.setattr(launcher, "load_token", lambda *a, **k: "SECRET-TOKEN-VALUE")
    monkeypatch.setattr(launcher, "load_allowed_users", lambda *a, **k: ["123"])
    ok, msg = launcher.preflight()
    assert ok is True
    assert "1 allowed user" in msg
    assert "SECRET-TOKEN-VALUE" not in msg  # the token never appears in output


def test_check_mode_does_not_poll(monkeypatch, capsys):
    monkeypatch.setattr(launcher, "preflight", lambda: (True, "ready: 1 allowed user(s)"))
    monkeypatch.setattr(launcher, "run_bot", lambda **k: (_ for _ in ()).throw(AssertionError("polled")))
    assert launcher.main(["--check"]) == 0


def test_second_instance_exits_quietly(monkeypatch, capsys):
    monkeypatch.setattr(launcher, "preflight", lambda: (True, "ready: 1 allowed user(s)"))
    monkeypatch.setattr(launcher, "acquire_lock", lambda *a, **k: False)
    monkeypatch.setattr(launcher, "run_bot", lambda **k: (_ for _ in ()).throw(AssertionError("polled")))
    assert launcher.main([]) == 0
    assert "already polling" in capsys.readouterr().out

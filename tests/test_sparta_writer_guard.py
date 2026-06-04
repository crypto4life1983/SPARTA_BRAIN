"""Tests for SPARTA Writer Concurrency Guard v1.

Proves the advisory writer lock behaves safely:
- one writer can acquire (an exclusive claim file is created),
- a second writer is blocked while the first runs,
- a stale claim (gone owner + expired heartbeat) is detected,
- force-stale takeover works only for genuinely stale claims,
- a cross-user PermissionError probe is treated as ALIVE, never stale,
- release requires the matching token,
- read-only mode creates no file at all,
- the module contains no network / subprocess / trading machinery,
- claiming is an atomic exclusive create,
- the default claim path lives under the gitignored ``storage/`` tree.

The guard module is loaded by file path so these tests do not depend on
``tools`` being importable as a package.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_GUARD_PATH = _REPO_ROOT / "tools" / "sparta_writer_guard.py"


def _load_guard():
    spec = importlib.util.spec_from_file_location(
        "sparta_writer_guard_under_test", _GUARD_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


guard = _load_guard()


# --- helpers ---------------------------------------------------------------

def _raise(exc_type):
    def _stub(_pid):
        raise exc_type("stubbed")
    return _stub


def _old_iso(hours=2):
    return (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()


def _write_claim(path, *, pid, heartbeat_iso, token="rawtoken", ttl=900, **extra):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "schema_version": 1,
        "owner_pid": pid,
        "token": token,
        "heartbeat_at": heartbeat_iso,
        "ttl_seconds": ttl,
        "os_user": "someone",
        "purpose": "write",
    }
    data.update(extra)
    path.write_text(json.dumps(data), encoding="utf-8")


@pytest.fixture
def lock_at(tmp_path, monkeypatch):
    """Repoint the claim file at a temp path and clear read-only mode."""
    target = tmp_path / "storage" / "locks" / "sparta_writer.lock.json"
    monkeypatch.setattr(guard, "LOCK_PATH", target)
    monkeypatch.delenv("SPARTA_READ_ONLY", raising=False)
    return target


# --- acquire / block -------------------------------------------------------

def test_acquire_succeeds(lock_at):
    handle = guard.acquire(purpose="commit")
    assert handle is not None
    assert lock_at.exists()
    data = json.loads(lock_at.read_text(encoding="utf-8"))
    assert data["owner_pid"] == os.getpid()
    assert data["purpose"] == "commit"
    assert len(data["token"]) >= 16
    assert handle.token == data["token"]


def test_second_writer_blocked(lock_at):
    first = guard.acquire(purpose="build")
    assert first is not None
    with pytest.raises(guard.WriterLockHeld):
        guard.acquire(purpose="build")
    # the original claim is untouched
    data = json.loads(lock_at.read_text(encoding="utf-8"))
    assert data["token"] == first.token


# --- staleness -------------------------------------------------------------

def test_stale_claim_detected(lock_at, monkeypatch):
    monkeypatch.setattr(guard, "_probe_pid", _raise(ProcessLookupError))
    _write_claim(lock_at, pid=424242, heartbeat_iso=_old_iso())
    snap = guard.status()
    assert snap["locked"] is True
    assert snap["pid_status"] == "gone"
    assert snap["heartbeat_expired"] is True
    assert snap["stale"] is True


def test_force_stale_takeover(lock_at, monkeypatch):
    monkeypatch.setattr(guard, "_probe_pid", _raise(ProcessLookupError))
    _write_claim(lock_at, pid=424242, heartbeat_iso=_old_iso(), token="oldtoken")

    with pytest.raises(guard.WriterLockHeld):
        guard.acquire(force_stale=False)

    handle = guard.acquire(force_stale=True)
    assert handle is not None
    assert handle.took_over is not None
    data = json.loads(lock_at.read_text(encoding="utf-8"))
    assert data["token"] == handle.token
    assert data["token"] != "oldtoken"
    assert data["owner_pid"] == os.getpid()


def test_cross_user_permissionerror_is_not_stale(lock_at, monkeypatch):
    # A process we cannot access (owned by another user) must read as ALIVE.
    monkeypatch.setattr(guard, "_probe_pid", _raise(PermissionError))
    _write_claim(lock_at, pid=15296, heartbeat_iso=_old_iso())

    snap = guard.status()
    assert snap["locked"] is True
    assert snap["pid_status"] == "running_other_user"
    assert snap["stale"] is False

    # even an explicit force-stale must NOT steal a running owner's claim
    with pytest.raises(guard.WriterLockHeld):
        guard.acquire(force_stale=True)


# --- release ---------------------------------------------------------------

def test_release_requires_matching_token(lock_at):
    handle = guard.acquire()
    with pytest.raises(guard.WriterLockTokenMismatch):
        guard.release(token="not-the-real-token")
    assert lock_at.exists()  # still held after a bad release

    assert guard.release(handle=handle) is True
    assert not lock_at.exists()
    assert guard.release(handle=handle) is False  # nothing left to release


# --- read-only bypass ------------------------------------------------------

def test_read_only_mode_creates_no_file(lock_at, monkeypatch):
    monkeypatch.setenv("SPARTA_READ_ONLY", "1")
    assert guard.require_writer_lock("commit") is None
    assert guard.acquire("commit") is None
    assert not lock_at.exists()


def test_status_creates_no_file_when_unlocked(lock_at):
    snap = guard.status()
    assert snap["locked"] is False
    assert not lock_at.exists()


# --- no network / subprocess / trading -------------------------------------

def test_module_has_no_network_subprocess_or_trading():
    src = _GUARD_PATH.read_text(encoding="utf-8")
    forbidden = [
        "import socket", "import subprocess", "from subprocess",
        "urllib", "requests", "httpx", "http.client", "smtplib", "asyncio",
        "Popen", "os.system", "os.popen", "check_output", "check_call",
        "place_order", "paper_trade", "live_trade", "backtest", "ccxt",
    ]
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden tokens present: {hits}"

    roots = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {
        "__future__", "argparse", "getpass", "json", "os", "platform",
        "secrets", "sys", "datetime", "pathlib", "ctypes",
    }
    assert roots <= allowed, f"unexpected imports: {sorted(roots - allowed)}"


# --- atomicity -------------------------------------------------------------

def test_claim_uses_atomic_exclusive_create(lock_at):
    guard.acquire()
    # a raw exclusive create on the same path must fail - proving O_EXCL
    with pytest.raises(FileExistsError):
        with open(str(guard.lock_path()), "x", encoding="utf-8") as handle:
            handle.write("x")


# --- path safety -----------------------------------------------------------

def test_default_lock_path_under_storage():
    fresh = _load_guard()  # unmonkeypatched default
    path = Path(fresh.LOCK_PATH)
    assert path.is_absolute()
    assert path.parts[-3:] == ("storage", "locks", "sparta_writer.lock.json")
    assert "storage" in path.parts  # the gitignored runtime tree

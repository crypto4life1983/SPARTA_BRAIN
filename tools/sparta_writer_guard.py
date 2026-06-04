"""SPARTA Writer Concurrency Guard v1.

A lightweight, stdlib-only, advisory writer lock for SPARTA build / commit /
push workflows. Its only job is to let one writer claim the repository and make
concurrent writers refuse to proceed, so two agent sessions cannot mutate the
same tree at the same time.

Design contract:
- The lock is runtime-only. It lives under ``storage/`` (gitignored), so it is
  never committed.
- Advisory only. This guard installs no git hooks and terminates no process. It
  reports state; callers decide what to do.
- Read-only callers never touch the lock. With ``SPARTA_READ_ONLY=1`` set,
  acquiring is a no-op that creates no file.
- Claiming uses an atomic exclusive create (``open(path, "x")``).
- Releasing requires the matching token, so one writer cannot drop another's
  claim.
- A held claim owned by a still-running process is honored. Taking over a stale
  claim requires an explicit force-stale request.
- A liveness probe that is denied access (a process owned by a different user,
  e.g. a cross-user sandbox) is treated as ALIVE, never stale.

This module performs no network access, spawns no child process, and contains
no trading, market, or money-movement logic of any kind.
"""
from __future__ import annotations

import argparse
import getpass
import json
import os
import platform
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1
DEFAULT_TTL_SECONDS = 900

_REPO_ROOT = Path(__file__).resolve().parents[1]
# Runtime-only claim file. ``storage/`` is gitignored, so this never lands in a
# commit. Tests repoint this module global at a temp directory.
LOCK_PATH = _REPO_ROOT / "storage" / "locks" / "sparta_writer.lock.json"

_READ_ONLY_TRUTHY = {"1", "true", "yes", "on"}


# --- errors ----------------------------------------------------------------

class WriterLockError(Exception):
    """Base class for writer-guard failures."""


class WriterLockHeld(WriterLockError):
    """Raised when a claim is already held and cannot be taken over."""


class WriterLockTokenMismatch(WriterLockError):
    """Raised when a release is attempted with the wrong token."""


# --- small helpers ---------------------------------------------------------

def lock_path() -> Path:
    """Return the active claim-file path (a module global tests can repoint)."""
    return Path(LOCK_PATH)


def read_only_mode() -> bool:
    """True when ``SPARTA_READ_ONLY`` selects a read-only, lock-free session."""
    return os.environ.get("SPARTA_READ_ONLY", "").strip().lower() in _READ_ONLY_TRUTHY


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _now_iso() -> str:
    return _utcnow().isoformat()


def _parse_iso(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        text = value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _os_user() -> str:
    try:
        return getpass.getuser()
    except Exception:  # pragma: no cover - environment dependent
        return os.environ.get("USERNAME") or os.environ.get("USER") or "unknown"


# --- liveness probe --------------------------------------------------------

def _probe_pid(pid: int) -> None:
    """Read-only liveness probe.

    Returns ``None`` when the process is running. Raises ``ProcessLookupError``
    when it does not exist, and ``PermissionError`` when it exists but is owned
    by another user / otherwise not accessible.

    On Windows ``os.kill(pid, 0)`` does NOT probe - it would send a console
    control event - so a read-only handle open is used there instead. The
    exception contract above is preserved on every platform.
    """
    if os.name == "nt":
        _probe_pid_windows(int(pid))
        return
    os.kill(int(pid), 0)


def _probe_pid_windows(pid: int) -> None:
    import ctypes
    from ctypes import wintypes

    process_query_limited_information = 0x1000
    err_access_denied = 5
    still_active = 259

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenProcess.restype = wintypes.HANDLE
    kernel32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    handle = kernel32.OpenProcess(process_query_limited_information, False, pid)
    if not handle:
        code = ctypes.get_last_error()
        if code == err_access_denied:
            raise PermissionError(f"access denied probing pid {pid}")
        raise ProcessLookupError(f"no such pid {pid}")
    try:
        kernel32.GetExitCodeProcess.restype = wintypes.BOOL
        kernel32.GetExitCodeProcess.argtypes = (
            wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD))
        exit_code = wintypes.DWORD()
        if (kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code))
                and exit_code.value != still_active):
            raise ProcessLookupError(f"pid {pid} has exited")
    finally:
        kernel32.CloseHandle(handle)


def _pid_status(pid) -> str:
    """Classify a pid as ``running``, ``running_other_user`` or ``gone``."""
    if not isinstance(pid, int):
        return "gone"
    try:
        _probe_pid(pid)
    except ProcessLookupError:
        return "gone"
    except PermissionError:
        return "running_other_user"
    except OSError:
        # Unknown probe failure: stay safe and assume the owner is running.
        return "running"
    return "running"


# --- claim evaluation ------------------------------------------------------

def _read_lock(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("claim payload is not an object")
    return data


def _evaluate(data: dict, now=None) -> dict:
    """Decide whether an existing claim is stale.

    Stale requires BOTH that the owning pid is gone AND that the heartbeat has
    aged past its ttl. A running owner - including one we cannot access because
    it belongs to another user - is never stale.
    """
    now = now or _utcnow()
    pid = data.get("owner_pid")
    pid_state = _pid_status(pid if isinstance(pid, int) else None)

    heartbeat = _parse_iso(data.get("heartbeat_at"))
    ttl = data.get("ttl_seconds")
    if not isinstance(ttl, (int, float)) or ttl < 0:
        ttl = DEFAULT_TTL_SECONDS
    if heartbeat is None:
        heartbeat_expired = True
        age_seconds = None
    else:
        age_seconds = (now - heartbeat).total_seconds()
        heartbeat_expired = age_seconds > ttl

    running = pid_state in ("running", "running_other_user")
    stale = (pid_state == "gone") and heartbeat_expired
    return {
        "pid_status": pid_state,
        "running": running,
        "heartbeat_expired": heartbeat_expired,
        "heartbeat_age_seconds": age_seconds,
        "stale": stale,
    }


def _build_payload(purpose: str, ttl_seconds: int, session_label) -> dict:
    stamp = _now_iso()
    return {
        "schema_version": SCHEMA_VERSION,
        "owner_pid": os.getpid(),
        "host": platform.node(),
        "os_user": _os_user(),
        "session_label": session_label
        or os.environ.get("SPARTA_WRITER_LABEL")
        or "unspecified",
        "purpose": purpose,
        "token": secrets.token_hex(16),
        "acquired_at": stamp,
        "heartbeat_at": stamp,
        "ttl_seconds": int(ttl_seconds),
    }


def _atomic_replace(path: Path, payload: dict) -> None:
    tmp = path.with_suffix(path.suffix + f".{os.getpid()}.{secrets.token_hex(4)}.tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(path))


# --- claim handle ----------------------------------------------------------

class WriterLock:
    """A held claim. Carries the secret token required to release it."""

    def __init__(self, path: Path, payload: dict, took_over=None):
        self.path = Path(path)
        self.payload = payload
        self.token = payload["token"]
        self.took_over = took_over
        self.released = False

    def renew(self, ttl_seconds=None) -> None:
        """Extend the heartbeat (and optionally the ttl) of this claim."""
        if self.released:
            raise WriterLockError("cannot renew a released claim")
        data = _read_lock(self.path)
        if data.get("token") != self.token:
            raise WriterLockTokenMismatch("claim no longer owned by this handle")
        data["heartbeat_at"] = _now_iso()
        if ttl_seconds is not None:
            data["ttl_seconds"] = int(ttl_seconds)
        _atomic_replace(self.path, data)
        self.payload = data

    def release(self) -> bool:
        result = release(handle=self)
        self.released = True
        return result

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if not self.released:
            try:
                self.release()
            except WriterLockError:
                pass
        return False


# --- public api ------------------------------------------------------------

def acquire(purpose: str = "write", ttl_seconds: int = DEFAULT_TTL_SECONDS,
            session_label=None, force_stale: bool = False):
    """Claim the writer lock.

    Returns a :class:`WriterLock` on success, or ``None`` when the session is
    read-only (no file is created). Raises :class:`WriterLockHeld` when a
    running owner already holds the claim, or when the claim is stale and
    ``force_stale`` was not requested.
    """
    if read_only_mode():
        return None

    path = lock_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _build_payload(purpose, ttl_seconds, session_label)

    try:
        with open(str(path), "x", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)
        return WriterLock(path, payload)
    except FileExistsError:
        pass

    # A claim already exists - inspect it.
    try:
        existing = _read_lock(path)
    except (ValueError, json.JSONDecodeError, OSError):
        if not force_stale:
            raise WriterLockHeld(
                "an unreadable claim already exists; rerun with force_stale to "
                "take it over")
        _atomic_replace(path, payload)
        return WriterLock(path, payload, took_over={"reason": "corrupt"})

    verdict = _evaluate(existing)
    if verdict["stale"]:
        if not force_stale:
            raise WriterLockHeld(
                "a stale claim exists; rerun with force_stale to take it over")
        _atomic_replace(path, payload)
        return WriterLock(path, payload, took_over=existing)

    raise WriterLockHeld(
        "writer lock is held by pid "
        f"{existing.get('owner_pid')} ({existing.get('os_user')}) "
        f"for '{existing.get('purpose')}'")


def require_writer_lock(purpose: str = "write", **kwargs):
    """Acquire for a write workflow, bypassing entirely in read-only mode."""
    if read_only_mode():
        return None
    return acquire(purpose=purpose, **kwargs)


def release(handle=None, *, token=None, path=None) -> bool:
    """Release a claim. The matching token is required.

    Returns ``True`` when a claim was removed, ``False`` when none existed.
    """
    target = Path(path) if path is not None else (
        handle.path if isinstance(handle, WriterLock) else lock_path())
    want = token if token is not None else (
        handle.token if isinstance(handle, WriterLock) else None)
    if want is None:
        raise WriterLockError("a token (or handle) is required to release")

    if not target.exists():
        return False
    data = _read_lock(target)
    if data.get("token") != want:
        raise WriterLockTokenMismatch("token does not match the held claim")
    target.unlink()
    return True


def status() -> dict:
    """Read-only snapshot of the current claim. Never creates a file."""
    path = lock_path()
    base = {"read_only_mode": read_only_mode(), "lock_path": str(path)}
    if not path.exists():
        return {**base, "locked": False}
    try:
        data = _read_lock(path)
    except (ValueError, json.JSONDecodeError, OSError):
        return {**base, "locked": True, "corrupt": True}
    verdict = _evaluate(data)
    return {
        **base,
        "locked": True,
        "corrupt": False,
        "owner_pid": data.get("owner_pid"),
        "os_user": data.get("os_user"),
        "host": data.get("host"),
        "purpose": data.get("purpose"),
        "session_label": data.get("session_label"),
        "acquired_at": data.get("acquired_at"),
        "heartbeat_at": data.get("heartbeat_at"),
        "pid_status": verdict["pid_status"],
        "running": verdict["running"],
        "heartbeat_expired": verdict["heartbeat_expired"],
        "heartbeat_age_seconds": verdict["heartbeat_age_seconds"],
        "stale": verdict["stale"],
    }


# --- command line ----------------------------------------------------------

# Preflight exit codes for the ``check`` subcommand.
EXIT_CLEAR = 0
EXIT_HELD = 2
EXIT_STALE = 3


def _cli_status(_args) -> int:
    print(json.dumps(status(), indent=2))
    return EXIT_CLEAR


def _cli_check(_args) -> int:
    if read_only_mode():
        print("clear: read-only mode, no writer lock required")
        return EXIT_CLEAR
    snap = status()
    if not snap["locked"]:
        print("clear: no writer lock held")
        return EXIT_CLEAR
    if snap.get("corrupt"):
        print("held: an unreadable claim exists (treat as held)")
        return EXIT_HELD
    if snap["stale"]:
        print("stale: claim owner is gone and heartbeat expired "
              "(rerun acquire with --force-stale to take over)")
        return EXIT_STALE
    print(f"held: pid {snap['owner_pid']} ({snap['os_user']}) "
          f"purpose '{snap['purpose']}'")
    return EXIT_HELD


def _cli_acquire(args) -> int:
    try:
        handle = acquire(purpose=args.purpose, ttl_seconds=args.ttl,
                         session_label=args.label, force_stale=args.force_stale)
    except WriterLockHeld as exc:
        print(f"refused: {exc}")
        return EXIT_HELD
    if handle is None:
        print("read-only mode: no claim created")
        return EXIT_CLEAR
    print(json.dumps({"acquired": True, "token": handle.token,
                      "purpose": args.purpose}, indent=2))
    return EXIT_CLEAR


def _cli_release(args) -> int:
    try:
        removed = release(token=args.token)
    except WriterLockTokenMismatch as exc:
        print(f"refused: {exc}")
        return EXIT_HELD
    print("released" if removed else "no claim to release")
    return EXIT_CLEAR


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="sparta_writer_guard",
        description="Advisory writer lock for SPARTA build/commit/push flows.")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="print the current claim").set_defaults(
        func=_cli_status)
    sub.add_parser("check", help="preflight: 0 clear, 2 held, 3 stale"
                   ).set_defaults(func=_cli_check)

    ap_acq = sub.add_parser("acquire", help="claim the writer lock")
    ap_acq.add_argument("--purpose", default="write")
    ap_acq.add_argument("--ttl", type=int, default=DEFAULT_TTL_SECONDS)
    ap_acq.add_argument("--label", default=None)
    ap_acq.add_argument("--force-stale", action="store_true")
    ap_acq.set_defaults(func=_cli_acquire)

    ap_rel = sub.add_parser("release", help="release a claim by token")
    ap_rel.add_argument("--token", required=True)
    ap_rel.set_defaults(func=_cli_release)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

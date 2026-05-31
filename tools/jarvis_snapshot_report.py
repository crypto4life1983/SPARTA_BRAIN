"""Generate an offline, read-only JARVIS status snapshot (manual only).

Run by hand:

    python tools/jarvis_snapshot_report.py

This reads the existing read-only JARVIS status aggregate
(``app.api_jarvis_status``) and writes a timestamped JSON snapshot under
``storage/jarvis/snapshots/`` plus a ``latest_snapshot.json`` pointer. It is the
Step 45 realization of the Step 44 plan (Option C): capture a prior read-only
baseline so a future, separately-approved step can answer "what changed?" with a
real diff.

Read-only by construction:

- It captures ONLY whitelisted, already-public status display fields (git
  head/commits, commander state/warnings, trading posture/latest reports, cache
  freshness, file-hygiene counts, status key count + a deterministic hash of the
  top-level keys). A snapshot can never widen exposure beyond the read-only
  status the console already shows.
- It NEVER writes outside ``storage/jarvis/snapshots/``; never stages, commits,
  cleans, or deletes anything; never trades, refreshes, or fetches data; never
  captures secrets, API keys, broker credentials, raw chat logs, audio,
  transcripts, order data, trade instructions, command/action/execute fields, or
  environment variables. A defense-in-depth guard fails the run closed if any
  forbidden token ever appears in the assembled snapshot.
- It is NOT wired to the browser. The web app neither imports nor invokes it and
  exposes no snapshot endpoint or control.

Exit code is 0 when a valid snapshot is written, nonzero (fail-closed) otherwise.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_DIR = REPO_ROOT / "storage" / "jarvis" / "snapshots"
LATEST_NAME = "latest_snapshot.json"

# Only these fields are ever copied out of each status section. Anything not
# whitelisted is dropped, so the snapshot is strictly a subset of the already
# read-only status payload.
_ALLOWED_GIT_FIELDS = ("branch", "head", "clean", "dirty",
                       "modified_count", "untracked_count")
_ALLOWED_COMMANDER_FIELDS = ("overall_state", "headline", "warnings",
                             "trading_posture", "cache_status",
                             "staged_count", "untracked_count")
_ALLOWED_TRADING_FIELDS = ("state", "read_only", "paper_ready", "live_ready",
                           "broker_control", "candidate_status")
_ALLOWED_CACHE_FIELDS = ("state", "overall", "generated_at")
_ALLOWED_HYGIENE_FIELDS = ("state", "total_untracked_count",
                           "tracked_modified_count", "staged_count")

# Defense-in-depth: whole-word tokens that must never appear anywhere in a
# serialized snapshot. Word boundaries (\b) mean legitimate compounds like
# "commander_snapshot" or an "..._audit" report name do NOT trip the guard,
# while a genuine secret/credential/order/command field would.
_FORBIDDEN_TOKEN_RE = re.compile(
    r"\b(?:secret|secrets|api_key|apikey|broker_password|password|credential|"
    r"credentials|token|tokens|command|action|execute|order|orders|"
    r"trade_ticket|audio|transcript|transcripts|chat_log|environment)\b"
)


def _load_status() -> dict:
    """Return the existing read-only JARVIS status aggregate. Performs no I/O
    beyond what the status helpers already do read-only; mutates nothing."""
    # Allow ``python tools/jarvis_snapshot_report.py`` to find the repo-root
    # ``app`` module (when run directly, only ``tools/`` is on sys.path).
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    import app as app_module
    status = app_module.api_jarvis_status()
    if not isinstance(status, dict):
        raise ValueError("JARVIS status aggregate is not a dict")
    return status


def _pick(section, fields) -> dict:
    """Copy only the whitelisted scalar fields from a status section."""
    if not isinstance(section, dict):
        return {}
    return {k: section.get(k) for k in fields if k in section}


def _recent_commits(git) -> list:
    out: list = []
    if isinstance(git, dict) and isinstance(git.get("commits"), list):
        for c in git["commits"][:5]:
            if isinstance(c, dict):
                out.append({
                    "short_hash": c.get("short_hash"),
                    "subject": c.get("subject"),
                })
    return out


def _trading_latest_reports(trading) -> list:
    out: list = []
    if isinstance(trading, dict) and isinstance(trading.get("latest_reports"), list):
        for r in trading["latest_reports"][:5]:
            if isinstance(r, dict):
                out.append({
                    "name": r.get("name"),
                    "path": r.get("path"),
                    "modified_at": r.get("modified_at"),
                    "has_md": r.get("has_md"),
                })
    return out


def build_snapshot(status: dict) -> dict:
    """Assemble a read-only snapshot from the status aggregate. Pure function:
    no I/O, no mutation. Only whitelisted display fields are copied in."""
    if not isinstance(status, dict):
        raise ValueError("status must be a dict")
    keys = sorted(str(k) for k in status.keys())
    key_blob = "|".join(keys)
    snapshot = {
        "kind": "jarvis_status_snapshot",
        "read_only": True,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "status_key_count": len(keys),
        "status_key_hash": hashlib.sha256(key_blob.encode("utf-8")).hexdigest(),
        "git": _pick(status.get("git"), _ALLOWED_GIT_FIELDS),
        "recent_commits": _recent_commits(status.get("git")),
        "commander_snapshot": _pick(status.get("commander_snapshot"),
                                    _ALLOWED_COMMANDER_FIELDS),
        "trading_detail": _pick(status.get("trading_detail"),
                                _ALLOWED_TRADING_FIELDS),
        "trading_latest_reports": _trading_latest_reports(status.get("trading_detail")),
        "cache_freshness": _pick(status.get("cache_freshness"), _ALLOWED_CACHE_FIELDS),
        "file_hygiene": _pick(status.get("file_hygiene_report"), _ALLOWED_HYGIENE_FIELDS),
    }
    return snapshot


def assert_snapshot_safe(snapshot: dict) -> None:
    """Fail-closed guard: raise if the serialized snapshot contains any
    forbidden whole-word token (secret/credential/order/command/etc.) or is not
    JSON-serializable. The whitelist build already excludes these; this is an
    independent second check so a regression can never silently leak."""
    blob = json.dumps(snapshot, ensure_ascii=False).lower()
    m = _FORBIDDEN_TOKEN_RE.search(blob)
    if m:
        raise ValueError(f"snapshot contains forbidden token: {m.group(0)!r}")


def _timestamped_name(when: datetime) -> str:
    # No colons — safe on Windows filesystems. Microseconds avoid collisions.
    return "snapshot_" + when.strftime("%Y-%m-%dT%H-%M-%S_%f") + ".json"


def write_snapshot(snapshot: dict, out_dir) -> Path:
    """Write the snapshot to a timestamped file under ``out_dir`` and update
    ``latest_snapshot.json`` in the same dir. Writes ONLY these two files and
    ONLY inside ``out_dir``. Returns the timestamped file path."""
    assert_snapshot_safe(snapshot)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    when = datetime.fromisoformat(snapshot["generated_at"]) \
        if isinstance(snapshot.get("generated_at"), str) else datetime.now()
    payload = json.dumps(snapshot, indent=2, ensure_ascii=False)
    ts_path = out_dir / _timestamped_name(when)
    ts_path.write_text(payload, encoding="utf-8")
    (out_dir / LATEST_NAME).write_text(payload, encoding="utf-8")
    return ts_path


def generate(out_dir=None) -> tuple[Path, dict]:
    """Load read-only status, build the snapshot, and write it. Returns
    (timestamped_path, snapshot)."""
    status = _load_status()
    snapshot = build_snapshot(status)
    path = write_snapshot(snapshot, out_dir or SNAPSHOT_DIR)
    return path, snapshot


def main() -> int:
    try:
        path, snapshot = generate()
    except Exception as exc:  # noqa: BLE001 — fail-closed on any failure
        print(f"[jarvis_snapshot_report] ERROR: {type(exc).__name__}: {exc}")
        return 1
    print(f"[jarvis_snapshot_report] wrote snapshot "
          f"(keys={snapshot['status_key_count']}, "
          f"hash={snapshot['status_key_hash'][:12]}...) -> {path}")
    print(f"[jarvis_snapshot_report] latest -> {SNAPSHOT_DIR / LATEST_NAME}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

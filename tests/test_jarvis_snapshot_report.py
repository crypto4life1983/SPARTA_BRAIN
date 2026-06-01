"""Step 45 — tests for the offline, read-only JARVIS snapshot script.

The script under test (``tools/jarvis_snapshot_report.py``) is operator-run
only. It reads the existing read-only JARVIS status aggregate and writes a
timestamped JSON snapshot (plus a ``latest_snapshot.json`` pointer) under
``storage/jarvis/snapshots/``. These tests pin the safety contract:

- it writes ONLY the two snapshot files and ONLY inside the given dir,
- the snapshot carries the required read-only display fields,
- the snapshot excludes every forbidden token (secrets/credentials/order/
  command/action/execute/audio/transcript/...),
- the live ``/api/jarvis/status`` shape is unchanged (28 keys, flags locked),
- the browser has no snapshot control and no snapshot/refresh endpoint exists.

All filesystem writes go to ``tmp_path`` so the real storage tree is never
touched.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

import tools.jarvis_snapshot_report as snap

_REPO_ROOT = Path(__file__).resolve().parents[1]

# Tokens the user explicitly required the snapshot to never contain.
_FORBIDDEN_TOKENS = (
    "secret", "api_key", "broker_password", "command", "action", "execute",
    "order", "trade_ticket", "audio", "transcript",
)


@pytest.fixture()
def real_snapshot():
    """Build a snapshot from the real read-only status aggregate (no writes)."""
    import app as app_module
    status = app_module.api_jarvis_status()
    return snap.build_snapshot(status)


# --- build / content ------------------------------------------------------

def test_snapshot_is_read_only_marked(real_snapshot):
    assert real_snapshot["kind"] == "jarvis_status_snapshot"
    assert real_snapshot["read_only"] is True


def test_snapshot_has_required_fields(real_snapshot):
    for key in (
        "generated_at", "status_key_count", "status_key_hash", "git",
        "recent_commits", "commander_snapshot", "trading_detail",
        "trading_latest_reports", "cache_freshness", "file_hygiene",
    ):
        assert key in real_snapshot, f"missing snapshot field: {key}"
    assert isinstance(real_snapshot["status_key_count"], int)
    assert real_snapshot["status_key_count"] > 0
    assert isinstance(real_snapshot["status_key_hash"], str)
    assert len(real_snapshot["status_key_hash"]) == 64  # sha256 hexdigest


def test_snapshot_trading_flags_locked_false(real_snapshot):
    trading = real_snapshot["trading_detail"]
    assert trading.get("read_only") is True
    assert trading.get("paper_ready") is False
    assert trading.get("live_ready") is False
    assert trading.get("broker_control") is False


def test_snapshot_excludes_forbidden_tokens(real_snapshot):
    blob = json.dumps(real_snapshot, ensure_ascii=False).lower()
    for tok in _FORBIDDEN_TOKENS:
        assert not re.search(rf"\b{re.escape(tok)}\b", blob), \
            f"forbidden token leaked into snapshot: {tok!r}"


def test_assert_snapshot_safe_passes_on_real_snapshot(real_snapshot):
    # Independent fail-closed guard must accept a legitimately whitelisted snap.
    snap.assert_snapshot_safe(real_snapshot)


def test_assert_snapshot_safe_rejects_forbidden_token():
    bad = {"kind": "jarvis_status_snapshot", "leak": "broker_password=hunter2"}
    with pytest.raises(ValueError):
        snap.assert_snapshot_safe(bad)


def test_build_snapshot_drops_non_whitelisted_fields():
    fake_status = {
        "git": {"branch": "master", "head": "abc1234", "secret": "leak",
                "commits": [{"short_hash": "abc1234", "subject": "x"}]},
        "trading_detail": {"read_only": True, "paper_ready": False,
                           "live_ready": False, "broker_control": False,
                           "order_ticket": "should-not-appear",
                           "latest_reports": []},
        "commander_snapshot": {"overall_state": "yellow",
                               "api_key": "should-not-appear"},
        "cache_freshness": {"overall": "fresh", "command": "drop-me"},
        "file_hygiene_report": {"state": "ok", "password": "drop-me"},
    }
    out = snap.build_snapshot(fake_status)
    assert "secret" not in out["git"]
    assert "order_ticket" not in out["trading_detail"]
    assert "api_key" not in out["commander_snapshot"]
    assert "command" not in out["cache_freshness"]
    assert "password" not in out["file_hygiene"]
    # whitelisted fields survive
    assert out["git"]["branch"] == "master"
    assert out["trading_detail"]["read_only"] is True


# --- write location -------------------------------------------------------

def test_write_snapshot_writes_only_two_files_in_dir(real_snapshot, tmp_path):
    out_dir = tmp_path / "snapshots"
    ts_path = snap.write_snapshot(real_snapshot, out_dir)
    written = sorted(p.name for p in out_dir.iterdir())
    assert len(written) == 2
    assert snap.LATEST_NAME in written
    assert ts_path.name in written
    assert ts_path.parent == out_dir


def test_write_snapshot_does_not_escape_dir(real_snapshot, tmp_path):
    # Use a dedicated sandbox so the global conftest isolation dir (created
    # directly under tmp_path) does not register as a stray write.
    sandbox = tmp_path / "sandbox"
    sandbox.mkdir()
    out_dir = sandbox / "snapshots"
    snap.write_snapshot(real_snapshot, out_dir)
    # The script created ONLY out_dir inside the sandbox, nothing alongside it.
    assert [p for p in sandbox.iterdir()] == [out_dir]


def test_latest_snapshot_is_valid_json(real_snapshot, tmp_path):
    out_dir = tmp_path / "snapshots"
    snap.write_snapshot(real_snapshot, out_dir)
    latest = out_dir / snap.LATEST_NAME
    loaded = json.loads(latest.read_text(encoding="utf-8"))
    assert loaded["kind"] == "jarvis_status_snapshot"
    assert loaded["read_only"] is True


def test_timestamped_name_has_no_colons():
    from datetime import datetime
    name = snap._timestamped_name(datetime(2026, 5, 30, 20, 40, 0))
    assert ":" not in name
    assert name.startswith("snapshot_")
    assert name.endswith(".json")


def test_generate_writes_under_tmp_dir(tmp_path):
    out_dir = tmp_path / "snapshots"
    path, snapshot = snap.generate(out_dir)
    assert path.exists()
    assert path.parent == out_dir
    assert (out_dir / snap.LATEST_NAME).exists()
    assert snapshot["read_only"] is True


# --- live status shape unchanged ------------------------------------------

def test_status_shape_unchanged():
    import app as app_module
    status = app_module.api_jarvis_status()
    assert isinstance(status, dict)
    # 24 base sections + 4 Bundle B read-only observation panels
    # (factory_status, survival_ledger, candidate_registry, freshness_guard)
    # + 1 Bundle 1 Strategy Factory snapshot panel (strategy_factory).
    assert len(status) == 29
    assert status["read_only"] is True
    trading = status["trading_detail"]
    assert trading["read_only"] is True
    assert trading["paper_ready"] is False
    assert trading["live_ready"] is False
    assert trading["broker_control"] is False


# --- browser is unaware of snapshots --------------------------------------

def test_template_has_no_snapshot_control():
    # The page has a read-only "Commander's Snapshot" *display* panel, but it
    # must offer no control that captures a file snapshot or triggers a refresh:
    # no snapshot/refresh endpoint reference, and no write/refresh affordances.
    body = (_REPO_ROOT / "templates" / "jarvis.html").read_text(encoding="utf-8")
    low = body.lower()
    assert "/api/jarvis/snapshot" not in low
    assert "/api/jarvis/refresh" not in low
    assert "method=\"post\"" not in low
    assert "onclick" not in low
    assert "<form" not in low


def test_no_snapshot_or_refresh_endpoint():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    assert client.post("/api/jarvis/snapshot").status_code == 404
    assert client.get("/api/jarvis/snapshot").status_code == 404
    assert client.post("/api/jarvis/refresh").status_code == 404
    assert client.get("/api/jarvis/refresh").status_code == 404


def test_app_source_has_no_snapshot_endpoint():
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    assert "/api/jarvis/snapshot" not in src
    assert "/api/jarvis/refresh" not in src

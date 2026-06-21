"""Route-level smoke test for the read-only SPARTA Control Panel (/control).

Proves the additive /control endpoint renders the read-only control panel end-to-end
(HTTP 200, the panel chrome + — when the live build succeeds — the status badge and the C22
collection HOLD state). Skips cleanly if the FastAPI app cannot be imported here."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

try:
    from fastapi.testclient import TestClient
    import app as app_module
    _CLIENT = TestClient(app_module.app)
    _APP_OK = True
except Exception:  # noqa: BLE001
    _APP_OK = False

requires_app = pytest.mark.skipif(not _APP_OK, reason="app not importable here")


@requires_app
def test_control_route_renders_read_only_panel():
    r = _CLIENT.get("/control")
    assert r.status_code == 200
    text = r.text
    # panel chrome is always present (page never crashes)
    assert "SPARTA — CONTROL PANEL" in text
    assert "Read-only status surface" in text
    assert "never auto-executed" in text
    # when the live build succeeds, the badge + C22 HOLD state + suggested token appear
    if "unavailable" not in text:
        assert "SPARTA STATUS:" in text
        assert "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS" in text
        assert ("HUMAN_STAGE_MORE_FROZEN_DAILY_TREND_RADAR_GC_WINDOWS_THEN_REREVIEW_"
                "C22_LABELS" in text)
        # E2: the read-only watchdog + lifecycle sections are surfaced
        assert "Scheduled-run watchdog" in text
        assert "Candidate lifecycle" in text
        assert "Current gate:" in text
        # proof flags rendered, read-only
        assert "reran_any_task=False" in text
        assert "advances_any_candidate=False" in text
        # no execution affordances
        assert "<script" not in text.lower()


@requires_app
def test_control_route_no_paper_live_or_execution_affordance():
    r = _CLIENT.get("/control")
    assert r.status_code == 200
    low = r.text.lower()
    assert "onclick" not in low
    assert "place order" not in low and "send-trading-signal" not in low

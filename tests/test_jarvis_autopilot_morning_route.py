"""Route-level smoke tests for the JARVIS Autopilot Morning Report panel.

Proves the additive JARVIS endpoints work end-to-end and that the panel does NOT
change the /api/jarvis/status shape (it is served from its own endpoint):
  * GET /api/jarvis/autopilot-morning returns the read-only panel JSON;
  * GET /jarvis/autopilot-morning renders the read-only HTML page with no
    paper/live-readiness claim;
  * api_jarvis_status() does NOT gain an 'autopilot_morning' key.

Skips cleanly if the FastAPI app cannot be imported in this environment."""
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
def test_api_autopilot_morning_returns_panel():
    r = _CLIENT.get("/api/jarvis/autopilot-morning")
    assert r.status_code == 200
    j = r.json()
    assert isinstance(j, dict)
    assert "html" in j
    assert "run_status" in j
    assert j.get("no_paper_live_readiness_claim") is True


@requires_app
def test_page_autopilot_morning_renders_html():
    r = _CLIENT.get("/jarvis/autopilot-morning")
    assert r.status_code == 200
    body = r.text
    low = body.lower()
    assert "autopilot morning report" in low
    assert "no paper/live-readiness claim" in low
    for banned in ("approved for paper", "approved for live",
                   "profit guarantee", "ready for live", "ready for paper"):
        assert banned not in low, banned


@requires_app
def test_panel_does_not_change_jarvis_status_shape():
    """The panel is served from its OWN endpoint, so /api/jarvis/status must
    NOT gain an autopilot_morning key (keeps the existing status contract)."""
    status = app_module.api_jarvis_status()
    assert isinstance(status, dict)
    assert "autopilot_morning" not in status


@requires_app
def test_jarvis_page_includes_panel_div_and_loader():
    r = _CLIENT.get("/jarvis")
    assert r.status_code == 200
    body = r.text
    assert 'id="pAutopilotMorning"' in body
    assert "loadAutopilotMorning(" in body
    assert "/api/jarvis/autopilot-morning" in body

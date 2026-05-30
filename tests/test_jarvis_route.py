"""Tests for the SPARTA JARVIS Command Center (additive, read-only).

Coverage:
- GET /jarvis returns 200 and renders the cinematic title + sections
- nav link to /jarvis is present (rendered by base.html)
- GET /api/jarvis/status returns the expected read-only aggregate shape
- safety gates surface LOCKED / approval-required posture
- the page contains no forbidden trade-action language or order call ids
- the JARVIS app.py block imports no broker / execution / scheduler surface
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytest.importorskip("fastapi")

# TestClient pulls in httpx; import lazily inside tests to mirror the
# existing route tests and avoid polluting runtime import scans.

_REPO_ROOT = Path(__file__).resolve().parents[1]


# --- page render ----------------------------------------------------------

def test_jarvis_route_returns_200():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/jarvis")
    assert r.status_code == 200


def test_jarvis_page_renders_title_and_core_sections():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    body = client.get("/jarvis").text
    assert "Sparta Jarvis Command Center" in body
    for section in (
        "System Core", "AI Brains", "Trading Bridge", "Content Engine",
        "Money Engine", "Moving Company", "Daily Mission", "Safety Gates",
    ):
        assert section in body, f"missing section: {section}"


def test_jarvis_page_marks_read_only():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    body = client.get("/jarvis").text
    assert "Read-Only" in body
    assert "does not trade" in body.lower()


def test_jarvis_nav_link_present():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    body = client.get("/jarvis").text
    assert 'href="/jarvis"' in body


# --- status API -----------------------------------------------------------

def test_jarvis_status_api_shape():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    r = client.get("/api/jarvis/status")
    assert r.status_code == 200
    d = r.json()
    assert d["online"] is True
    assert d["read_only"] is True
    for key in (
        "system_core", "ai_brains", "trading_bridge", "content_engine",
        "money_engine", "moving_company", "daily_mission", "safety_gates",
    ):
        assert key in d, f"missing status key: {key}"


def test_jarvis_status_trading_is_read_only_and_locked():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    tb = client.get("/api/jarvis/status").json()["trading_bridge"]
    assert tb.get("read_only") is True
    assert tb.get("locked") is True


def test_jarvis_status_safety_gates_locked():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    sg = client.get("/api/jarvis/status").json()["safety_gates"]
    names = {g["name"]: g["status"] for g in sg.get("gates", [])}
    assert names.get("Trading execution") == "LOCKED"
    assert names.get("YouTube upload") == "APPROVAL_REQUIRED"
    assert names.get("Live automation") == "BLOCKED"


def test_jarvis_status_moving_company_is_placeholder():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    mv = client.get("/api/jarvis/status").json()["moving_company"]
    assert mv.get("state") == "placeholder"
    assert mv.get("leads") is None and mv.get("tasks") is None


# --- safety: no forbidden trade-action language ---------------------------

_FORBIDDEN_ON_PAGE = (
    r"\bbuy\b", r"\bsell\b", r"\bgo long\b", r"\bgo short\b",
    r"\bexecute trade\b", r"\bplace order\b", r"\bplace trade\b",
    r"\bopen position\b", r"\bclose position\b", r"\bsubmit order\b",
)


def test_jarvis_page_has_no_forbidden_action_language():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    body = client.get("/jarvis").text.lower()
    for pat in _FORBIDDEN_ON_PAGE:
        assert re.search(pat, body) is None, f"forbidden phrase on page: {pat}"


def test_jarvis_page_has_no_order_call_identifiers():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    body = client.get("/jarvis").text
    for ident in (
        "place_order(", "submit_order(", "execute_trade(", "open_position(",
        "close_position(", "send_telegram(",
    ):
        assert ident not in body, f"forbidden call id on page: {ident}"


# --- app.py additive scan -------------------------------------------------

def test_jarvis_app_block_has_no_broker_or_execution_imports():
    src = (_REPO_ROOT / "app.py").read_text(encoding="utf-8")
    m = re.search(
        r"SPARTA JARVIS Command Center.*?END SPARTA JARVIS Command Center",
        src, flags=re.S,
    )
    assert m is not None, "JARVIS block not found in app.py"
    code = re.sub(r"(?m)#.*$", "", m.group(0)).lower()
    forbidden = (
        "place_order", "submit_order", "execute_trade", "place_trade",
        "import broker", "from broker", "send_telegram(", "post_to_webhook",
        "register-scheduledtask",
    )
    for tok in forbidden:
        assert tok not in code, f"forbidden token in JARVIS block: {tok}"

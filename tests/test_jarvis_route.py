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


# --- Step 02: operator intelligence sections ------------------------------

def test_jarvis_status_has_operator_sections():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()
    for key in ("git", "safety", "project", "brain_memory",
                "recommended_next_actions"):
        assert key in d, f"missing operator key: {key}"


def test_jarvis_status_operator_safety_flags_true():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    s = client.get("/api/jarvis/status").json()["safety"]
    for flag in ("read_only", "no_execution_control", "no_broker_control",
                 "no_secret_display", "no_force_git"):
        assert s.get(flag) is True, f"safety flag not True: {flag}"


def test_jarvis_status_git_section_shape():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    g = client.get("/api/jarvis/status").json()["git"]
    # Either a healthy snapshot or a fail-closed 'unavailable' — never a crash.
    assert g.get("state") in ("online", "unavailable")
    if g.get("state") == "online":
        assert isinstance(g.get("modified_count"), int)
        assert isinstance(g.get("untracked_count"), int)
        assert isinstance(g.get("commits"), list)


def test_jarvis_status_project_file_booleans():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    p = client.get("/api/jarvis/status").json()["project"]
    for key in ("release_note_exists", "jarvis_template_exists",
                "tests_file_exists"):
        assert isinstance(p.get(key), bool), f"not a bool: {key}"


def test_jarvis_status_brain_memory_does_not_expose_log_contents():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    bm = client.get("/api/jarvis/status").json()["brain_memory"]
    assert "projects" in bm
    # The probe must not surface the gitignored logs dir as a project key.
    assert "logs" not in (bm.get("projects") or {})


def test_jarvis_status_next_actions_is_list():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    na = client.get("/api/jarvis/status").json()["recommended_next_actions"]
    assert isinstance(na, list) and len(na) >= 1
    assert all(isinstance(x, str) for x in na)


def test_jarvis_status_exposes_no_execution_fields():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()
    # No control affordance should be exposed as a key anywhere in the feed.
    def _keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield str(k).lower()
                yield from _keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from _keys(v)
    all_keys = set(_keys(d))
    # Forbid keys that would represent an execution trigger / control
    # affordance. A descriptive "command" label inside the cached health
    # report is read-only data, not a control, so it is allowed.
    for forbidden in ("place_order", "submit_order", "execute_trade",
                      "run_command", "exec", "shell", "force_push", "git_push"):
        assert forbidden not in all_keys, f"forbidden key in feed: {forbidden}"


# --- Step 03: cached health report ----------------------------------------

def test_jarvis_status_has_health_report_key():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()
    assert "health_report" in d
    assert isinstance(d["health_report"], dict)
    assert d["health_report"].get("state") in (
        "ready", "missing", "unavailable", "error",
    )


def test_jarvis_health_report_missing_is_graceful(monkeypatch, tmp_path):
    import app as app_module
    # Point BASE at an empty dir so the cached file is absent.
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    hr = app_module._jarvis_health_report()
    assert hr["state"] == "missing"
    assert "tools/jarvis_health_report.py" in hr["message"]


def test_jarvis_health_report_invalid_is_fail_closed(monkeypatch, tmp_path):
    import app as app_module
    d = tmp_path / "storage" / "jarvis"
    d.mkdir(parents=True)
    (d / "health_report.json").write_text("{ not valid json", encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    hr = app_module._jarvis_health_report()
    assert hr["state"] == "unavailable"
    assert "error" in hr


def test_jarvis_health_report_valid_is_passed_through(monkeypatch, tmp_path):
    import json
    import app as app_module
    d = tmp_path / "storage" / "jarvis"
    d.mkdir(parents=True)
    payload = {
        "state": "ready", "generated_at": "2026-05-30T00:00:00", "overall": "pass",
        "checks": [{"name": "py_compile", "status": "pass", "returncode": 0}],
    }
    (d / "health_report.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    hr = app_module._jarvis_health_report()
    assert hr["overall"] == "pass"
    assert hr["checks"][0]["name"] == "py_compile"


def test_jarvis_endpoint_does_not_execute_health_checks(monkeypatch):
    # The web route must never spawn subprocesses to build the feed.
    import subprocess
    import app as app_module
    from fastapi.testclient import TestClient

    def _boom(*a, **k):
        raise AssertionError("endpoint must not run subprocesses")

    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)
    client = TestClient(app_module.app)
    r = client.get("/api/jarvis/status")
    assert r.status_code == 200
    assert "health_report" in r.json()


# --- Step 03: health report script ----------------------------------------

def test_health_report_script_exists_and_compiles():
    import py_compile
    script = _REPO_ROOT / "tools" / "jarvis_health_report.py"
    assert script.exists(), "tools/jarvis_health_report.py missing"
    py_compile.compile(str(script), doraise=True)


def test_health_report_script_has_no_secret_dumps():
    src = (_REPO_ROOT / "tools" / "jarvis_health_report.py").read_text(
        encoding="utf-8"
    )
    low = src.lower()
    # Target real env/secret ACCESS patterns, not the word "secret" in prose.
    for tok in ("os.environ", "getenv", "environ.copy", "dotenv",
                "load_secrets", "local_secrets"):
        assert tok not in low, f"script must not touch env/secrets: {tok}"


def test_health_report_module_writes_expected_shape(monkeypatch, tmp_path):
    # Run the script's logic without invoking real py_compile/pytest:
    # stub _run_check so the test is fast and not environment-fragile.
    import importlib.util
    import json
    script = _REPO_ROOT / "tools" / "jarvis_health_report.py"
    spec = importlib.util.spec_from_file_location("jarvis_health_report", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(mod, "REPORT_DIR", tmp_path / "storage" / "jarvis")
    monkeypatch.setattr(
        mod, "REPORT_PATH", tmp_path / "storage" / "jarvis" / "health_report.json"
    )
    monkeypatch.setattr(
        mod, "_run_check",
        lambda c: {"name": c["name"], "command": "stub", "status": "pass",
                   "returncode": 0, "stdout_tail": "", "stderr_tail": "",
                   "duration_seconds": 0.0},
    )
    rc = mod.main()
    assert rc == 0
    report = json.loads(mod.REPORT_PATH.read_text(encoding="utf-8"))
    assert report["overall"] == "pass"
    assert {c["name"] for c in report["checks"]} == {"py_compile", "pytest"}
    assert "generated_at" in report


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

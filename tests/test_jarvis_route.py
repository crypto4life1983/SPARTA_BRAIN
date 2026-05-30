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


# --- Step 04: read-only mission board -------------------------------------

def test_jarvis_status_has_mission_board_key():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()
    assert "mission_board" in d
    assert isinstance(d["mission_board"], dict)
    assert d["mission_board"].get("state") in (
        "ready", "missing", "unavailable", "error",
    )


def test_jarvis_mission_board_seed_file_is_valid_and_ready():
    import app as app_module
    mb = app_module._jarvis_mission_board()
    assert mb["state"] == "ready", mb
    assert mb.get("version") == 1
    assert isinstance(mb.get("missions"), list) and len(mb["missions"]) >= 4
    for m in mb["missions"]:
        for key in ("id", "title", "status", "priority", "area"):
            assert key in m, f"mission missing {key}"
    counts = mb.get("counts") or {}
    assert counts.get("total") == len(mb["missions"])


def test_jarvis_mission_board_missing_is_graceful(monkeypatch, tmp_path):
    import app as app_module
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    mb = app_module._jarvis_mission_board()
    assert mb["state"] == "missing"
    assert "jarvis_mission_board.json" in mb["message"]


def test_jarvis_mission_board_invalid_json_is_fail_closed(monkeypatch, tmp_path):
    import app as app_module
    d = tmp_path / "docs"
    d.mkdir(parents=True)
    (d / "jarvis_mission_board.json").write_text("{ broken", encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    mb = app_module._jarvis_mission_board()
    assert mb["state"] == "unavailable"
    assert "error" in mb


def test_jarvis_mission_board_bad_shape_is_fail_closed(monkeypatch, tmp_path):
    import json
    import app as app_module
    d = tmp_path / "docs"
    d.mkdir(parents=True)
    # missions present but a mission lacks required fields
    payload = {"version": 1, "missions": [{"id": "X", "title": "no fields"}]}
    (d / "jarvis_mission_board.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    mb = app_module._jarvis_mission_board()
    assert mb["state"] == "unavailable"


def test_jarvis_mission_board_does_not_execute_prompts(monkeypatch):
    # Reading the board must never spawn a subprocess / run a prompt.
    import subprocess
    import app as app_module
    from fastapi.testclient import TestClient

    def _boom(*a, **k):
        raise AssertionError("mission board must not execute anything")

    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)
    client = TestClient(app_module.app)
    mb = client.get("/api/jarvis/status").json()["mission_board"]
    assert mb["state"] == "ready"


def test_jarvis_mission_board_prompt_is_text_only():
    import app as app_module
    mb = app_module._jarvis_mission_board()
    for m in mb["missions"]:
        # safe_next_prompt, if present, is a plain string — never a callable
        # descriptor, command list, or execution affordance.
        p = m.get("safe_next_prompt", "")
        assert isinstance(p, str)
        # mission dicts expose no execution/control fields
        for forbidden in ("command", "cmd", "exec", "run", "shell", "action"):
            assert forbidden not in m, f"mission exposes control field: {forbidden}"


def test_jarvis_mission_board_seed_file_is_tracked_safe():
    # The seed file lives under docs/ (tracked) and is pure data — no code.
    src = (_REPO_ROOT / "docs" / "jarvis_mission_board.json").read_text(
        encoding="utf-8"
    )
    import json
    data = json.loads(src)
    assert data["version"] == 1
    assert isinstance(data["missions"], list)


# --- Step 05: read-only trading research detail ---------------------------

def test_jarvis_status_has_trading_detail_key():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()
    assert "trading_detail" in d
    td = d["trading_detail"]
    assert isinstance(td, dict)
    assert td.get("state") in ("ready", "missing", "unavailable", "error")


def test_jarvis_trading_detail_is_read_only_and_non_deployable():
    import app as app_module
    td = app_module._jarvis_trading_detail()
    assert td.get("read_only") is True
    assert td.get("paper_ready") is False
    assert td.get("live_ready") is False
    assert td.get("broker_control") is False
    assert td.get("candidate_status") == "RESEARCH_CANDIDATE_ONLY"


def test_jarvis_trading_detail_s26_detection():
    import app as app_module
    td = app_module._jarvis_trading_detail()
    if td.get("state") == "ready":
        s26 = td.get("s26") or {}
        assert s26.get("status") == "RESEARCH_CANDIDATE_ONLY"
        assert isinstance(s26.get("d17_friction_report_exists"), bool)
        assert isinstance(s26.get("d18_decision_gate_exists"), bool)
        assert isinstance(td.get("latest_reports"), list)
        assert isinstance(td.get("warnings"), list)


def test_jarvis_trading_detail_missing_dir_is_graceful(monkeypatch, tmp_path):
    import app as app_module
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    td = app_module._jarvis_trading_detail()
    assert td.get("state") == "missing"
    # Even when missing, posture flags must still be safe.
    assert td.get("paper_ready") is False
    assert td.get("live_ready") is False
    assert td.get("broker_control") is False


def test_jarvis_trading_detail_never_reads_raw_artifacts(monkeypatch, tmp_path):
    import json
    import app as app_module
    reports = tmp_path / "trading_research" / "agentic_factory" / "reports"
    d17 = reports / app_module._JARVIS_S26_D17_DIR
    d17.mkdir(parents=True)
    (d17 / "report.json").write_text(
        json.dumps({"title": "t", "s26_current_status": {"level": "RESEARCH_CANDIDATE"}}),
        encoding="utf-8",
    )
    # A raw artifact whose contents must never be opened.
    raw = d17 / "s26_d17_friction_raw.json"
    raw.write_text('{"SECRET_DO_NOT_READ": true}', encoding="utf-8")

    opened = []
    import pathlib
    orig = pathlib.Path.read_text

    def _tracking_read_text(self, *a, **k):
        opened.append(str(self))
        return orig(self, *a, **k)

    monkeypatch.setattr(pathlib.Path, "read_text", _tracking_read_text)
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    td = app_module._jarvis_trading_detail()
    assert td.get("state") == "ready"
    # The raw file must appear in a warning but must NOT have been read.
    assert any("raw" in str(p).lower() for p in [raw])
    assert not any("friction_raw" in p for p in opened), opened
    assert any("raw artifact present" in w for w in td.get("warnings", []))


def test_jarvis_trading_detail_exposes_no_execution_fields():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    td = client.get("/api/jarvis/status").json()["trading_detail"]

    def _keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield str(k).lower()
                yield from _keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from _keys(v)

    keys = set(_keys(td))
    for forbidden in ("place_order", "submit_order", "execute_trade",
                      "start_bot", "stop_bot", "run_backtest", "fetch_data",
                      "exec", "shell", "broker_login", "api_key"):
        assert forbidden not in keys, f"forbidden trading control key: {forbidden}"


def test_jarvis_trading_detail_does_not_run_subprocess(monkeypatch):
    import subprocess
    import app as app_module

    def _boom(*a, **k):
        raise AssertionError("trading detail must not run subprocesses")

    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)
    td = app_module._jarvis_trading_detail()
    assert td.get("read_only") is True


# --- Step 06: cached route smoke report -----------------------------------

def test_jarvis_status_has_route_smoke_key():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()
    assert "route_smoke_report" in d
    assert isinstance(d["route_smoke_report"], dict)
    assert d["route_smoke_report"].get("state") in (
        "ready", "missing", "unavailable", "error",
    )


def test_jarvis_route_smoke_missing_is_graceful(monkeypatch, tmp_path):
    import app as app_module
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    rs = app_module._jarvis_route_smoke_report()
    assert rs["state"] == "missing"
    assert "tools/jarvis_route_smoke_report.py" in rs["message"]


def test_jarvis_route_smoke_invalid_is_fail_closed(monkeypatch, tmp_path):
    import app as app_module
    d = tmp_path / "storage" / "jarvis"
    d.mkdir(parents=True)
    (d / "route_smoke_report.json").write_text("{ not valid", encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    rs = app_module._jarvis_route_smoke_report()
    assert rs["state"] == "unavailable"
    assert "error" in rs


def test_jarvis_route_smoke_valid_is_passed_through(monkeypatch, tmp_path):
    import json
    import app as app_module
    d = tmp_path / "storage" / "jarvis"
    d.mkdir(parents=True)
    payload = {
        "state": "ready", "generated_at": "2026-05-30T00:00:00",
        "base_url": "http://127.0.0.1:8765", "overall": "pass",
        "counts": {"total": 3, "pass": 3, "fail": 0},
        "routes": [
            {"path": "/", "status_code": 200, "ok": True,
             "duration_seconds": 0.01, "required": True, "error": None},
        ],
    }
    (d / "route_smoke_report.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    rs = app_module._jarvis_route_smoke_report()
    assert rs["overall"] == "pass"
    assert rs["routes"][0]["path"] == "/"
    assert rs["counts"]["total"] == 3


def test_jarvis_endpoint_does_not_probe_routes(monkeypatch):
    # The web route must never open a socket / probe URLs to build the feed.
    import urllib.request
    import subprocess
    import app as app_module
    from fastapi.testclient import TestClient

    def _boom(*a, **k):
        raise AssertionError("endpoint must not probe routes / run subprocesses")

    monkeypatch.setattr(urllib.request, "urlopen", _boom)
    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)
    client = TestClient(app_module.app)
    r = client.get("/api/jarvis/status")
    assert r.status_code == 200
    assert "route_smoke_report" in r.json()


def test_route_smoke_script_exists_and_compiles():
    import py_compile
    script = _REPO_ROOT / "tools" / "jarvis_route_smoke_report.py"
    assert script.exists(), "tools/jarvis_route_smoke_report.py missing"
    py_compile.compile(str(script), doraise=True)


def test_route_smoke_script_has_no_secret_or_header_dumps():
    src = (_REPO_ROOT / "tools" / "jarvis_route_smoke_report.py").read_text(
        encoding="utf-8"
    )
    low = src.lower()
    # No env/secret access and no auth/cookie header injection.
    for tok in ("os.environ", "getenv", "environ.copy", "dotenv",
                "load_secrets", "local_secrets", "authorization",
                "cookie", "api_key", "bearer"):
        assert tok not in low, f"route smoke script must not touch: {tok}"


def test_route_smoke_module_builds_expected_shape(monkeypatch, tmp_path):
    # Run the script's logic without making real HTTP calls: stub _probe.
    import importlib.util
    import json
    script = _REPO_ROOT / "tools" / "jarvis_route_smoke_report.py"
    spec = importlib.util.spec_from_file_location("jarvis_route_smoke_report", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    def _fake_probe(base_url, path, timeout):
        return {"path": path, "url": base_url + path, "status_code": 200,
                "ok": True, "content_length": 10, "error": None,
                "duration_seconds": 0.0}

    monkeypatch.setattr(mod, "_probe", _fake_probe)
    report = mod.build_report("http://127.0.0.1:8765", 1.0)
    assert report["overall"] == "pass"
    assert report["counts"]["total"] == len(mod.ROUTES)
    assert report["counts"]["fail"] == 0
    assert all(set(("path", "url", "status_code", "ok", "duration_seconds")) <= set(r)
               for r in report["routes"])
    assert "generated_at" in report and report["base_url"].startswith("http")
    # A failing required route must flip overall to fail.
    monkeypatch.setattr(
        mod, "_probe",
        lambda b, p, t: {"path": p, "url": b + p, "status_code": 500, "ok": False,
                         "content_length": None, "error": "HTTP 500",
                         "duration_seconds": 0.0},
    )
    bad = mod.build_report("http://127.0.0.1:8765", 1.0)
    assert bad["overall"] == "fail"


def test_route_smoke_report_exposes_no_execution_fields():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    rs = client.get("/api/jarvis/status").json()["route_smoke_report"]

    def _keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield str(k).lower()
                yield from _keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from _keys(v)

    keys = set(_keys(rs))
    for forbidden in ("run_command", "exec", "shell", "place_order",
                      "submit_order", "execute_trade", "probe_now", "trigger"):
        assert forbidden not in keys, f"forbidden control key: {forbidden}"


# --- Step 07: read-only prompt library ------------------------------------

def test_jarvis_status_has_prompt_library_key():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()
    assert "prompt_library" in d
    assert isinstance(d["prompt_library"], dict)
    assert d["prompt_library"].get("state") in (
        "ready", "missing", "unavailable", "error",
    )


def test_jarvis_prompt_library_seed_file_is_valid_and_ready():
    import app as app_module
    pl = app_module._jarvis_prompt_library()
    assert pl["state"] == "ready", pl
    assert pl.get("version") == 1
    prompts = pl.get("prompts")
    assert isinstance(prompts, list) and 6 <= len(prompts) <= 10
    for p in prompts:
        for key in ("id", "title", "category", "risk", "prompt", "allowed"):
            assert key in p, f"prompt missing {key}"
    counts = pl.get("counts") or {}
    assert counts.get("total") == len(prompts)


def test_jarvis_prompt_library_missing_is_graceful(monkeypatch, tmp_path):
    import app as app_module
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    pl = app_module._jarvis_prompt_library()
    assert pl["state"] == "missing"
    assert "jarvis_prompt_library.json" in pl["message"]


def test_jarvis_prompt_library_invalid_json_is_fail_closed(monkeypatch, tmp_path):
    import app as app_module
    d = tmp_path / "docs"
    d.mkdir(parents=True)
    (d / "jarvis_prompt_library.json").write_text("{ broken", encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    pl = app_module._jarvis_prompt_library()
    assert pl["state"] == "unavailable"
    assert "error" in pl


def test_jarvis_prompt_library_bad_shape_is_fail_closed(monkeypatch, tmp_path):
    import json
    import app as app_module
    d = tmp_path / "docs"
    d.mkdir(parents=True)
    # prompts present but a prompt lacks required fields
    payload = {"version": 1, "prompts": [{"id": "X", "title": "no fields"}]}
    (d / "jarvis_prompt_library.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    pl = app_module._jarvis_prompt_library()
    assert pl["state"] == "unavailable"


def test_jarvis_prompt_library_valid_shape_passed_through(monkeypatch, tmp_path):
    import json
    import app as app_module
    d = tmp_path / "docs"
    d.mkdir(parents=True)
    payload = {
        "version": 1,
        "updated_at": "2026-05-30T00:00:00",
        "prompts": [{
            "id": "T1", "title": "Test", "category": "jarvis",
            "risk": "read_only", "prompt": "Read only. Do nothing.",
            "allowed": True, "notes": "n",
        }],
    }
    (d / "jarvis_prompt_library.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    pl = app_module._jarvis_prompt_library()
    assert pl["state"] == "ready"
    assert pl["version"] == 1
    assert pl["prompts"][0]["prompt"] == "Read only. Do nothing."
    assert pl["counts"]["total"] == 1
    assert pl["counts"]["by_category"].get("jarvis") == 1
    assert pl["counts"]["by_risk"].get("read_only") == 1


def test_jarvis_prompt_library_prompt_is_text_only():
    import app as app_module
    pl = app_module._jarvis_prompt_library()
    for p in pl["prompts"]:
        # The prompt is a plain display string — never a callable, command
        # list, or execution descriptor.
        assert isinstance(p.get("prompt"), str)
        # prompt dicts expose no execution/control fields
        for forbidden in ("command", "cmd", "exec", "run", "shell", "action",
                           "callback", "handler"):
            assert forbidden not in p, f"prompt exposes control field: {forbidden}"


def test_jarvis_prompt_library_does_not_execute_anything(monkeypatch):
    # Reading the library must never spawn a subprocess, make an HTTP call, or
    # otherwise run prompt text.
    import subprocess
    import urllib.request
    import app as app_module
    from fastapi.testclient import TestClient

    def _boom(*a, **k):
        raise AssertionError("prompt library must not execute anything")

    monkeypatch.setattr(urllib.request, "urlopen", _boom)
    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)
    client = TestClient(app_module.app)
    r = client.get("/api/jarvis/status")
    assert r.status_code == 200
    assert r.json()["prompt_library"]["state"] == "ready"


def test_jarvis_prompt_library_exposes_no_execution_fields():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    pl = client.get("/api/jarvis/status").json()["prompt_library"]

    def _keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield str(k).lower()
                yield from _keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from _keys(v)

    keys = set(_keys(pl))
    for forbidden in ("run_command", "exec", "shell", "place_order",
                      "submit_order", "execute_trade", "callback", "handler",
                      "onclick", "trigger"):
        assert forbidden not in keys, f"forbidden control key: {forbidden}"


def test_jarvis_prompt_library_seed_file_is_tracked_safe():
    # The seed file lives under docs/ (tracked) and is pure data — no code.
    import json
    src = (_REPO_ROOT / "docs" / "jarvis_prompt_library.json").read_text(
        encoding="utf-8"
    )
    data = json.loads(src)
    assert data["version"] == 1
    assert isinstance(data["prompts"], list)
    for p in data["prompts"]:
        assert p.get("risk") == "read_only", "seed prompts must be read_only"


# --- Step 08: read-only file hygiene panel --------------------------------

def test_jarvis_status_has_file_hygiene_key():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()
    assert "file_hygiene_report" in d
    assert isinstance(d["file_hygiene_report"], dict)
    assert d["file_hygiene_report"].get("state") in (
        "ready", "missing", "unavailable", "error",
    )


def test_jarvis_file_hygiene_missing_is_graceful(monkeypatch, tmp_path):
    import app as app_module
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    fh = app_module._jarvis_file_hygiene_report()
    assert fh["state"] == "missing"
    assert "jarvis_file_hygiene_report.py" in fh["message"]


def test_jarvis_file_hygiene_invalid_is_fail_closed(monkeypatch, tmp_path):
    import app as app_module
    d = tmp_path / "storage" / "jarvis"
    d.mkdir(parents=True)
    (d / "file_hygiene_report.json").write_text("{ broken", encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    fh = app_module._jarvis_file_hygiene_report()
    assert fh["state"] == "unavailable"
    assert "error" in fh


def test_jarvis_file_hygiene_non_object_is_fail_closed(monkeypatch, tmp_path):
    import json
    import app as app_module
    d = tmp_path / "storage" / "jarvis"
    d.mkdir(parents=True)
    (d / "file_hygiene_report.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    fh = app_module._jarvis_file_hygiene_report()
    assert fh["state"] == "unavailable"


def test_jarvis_file_hygiene_valid_is_passed_through(monkeypatch, tmp_path):
    import json
    import app as app_module
    d = tmp_path / "storage" / "jarvis"
    d.mkdir(parents=True)
    payload = {
        "generated_at": "2026-05-30T00:00:00",
        "git_ok": True,
        "total_untracked_count": 4369,
        "tracked_modified_count": 0,
        "staged_count": 0,
        "top_untracked_dirs": [{"dir": "data", "count": 1200}],
        "known_safe_areas": ["storage/jarvis/"],
        "warnings": [],
    }
    (d / "file_hygiene_report.json").write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(app_module, "BASE", tmp_path)
    fh = app_module._jarvis_file_hygiene_report()
    assert fh["state"] == "ready"
    assert fh["total_untracked_count"] == 4369
    assert fh["top_untracked_dirs"][0]["dir"] == "data"


def test_jarvis_file_hygiene_endpoint_does_not_run_git(monkeypatch):
    # Hitting the endpoint must never run git / spawn a subprocess for hygiene;
    # it only reflects the cached report. (Other sections are fail-closed too.)
    import subprocess
    import app as app_module
    from fastapi.testclient import TestClient

    def _boom(*a, **k):
        raise AssertionError("endpoint must not run git / scan files")

    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)
    client = TestClient(app_module.app)
    r = client.get("/api/jarvis/status")
    assert r.status_code == 200
    assert "file_hygiene_report" in r.json()


def test_file_hygiene_script_exists_and_compiles():
    import py_compile
    script = _REPO_ROOT / "tools" / "jarvis_file_hygiene_report.py"
    assert script.exists(), "tools/jarvis_file_hygiene_report.py missing"
    py_compile.compile(str(script), doraise=True)


def test_file_hygiene_script_has_no_secret_or_mutation_commands():
    src = (_REPO_ROOT / "tools" / "jarvis_file_hygiene_report.py").read_text(
        encoding="utf-8"
    )
    low = src.lower()
    # No env/secret access.
    for tok in ("os.environ", "getenv", "dotenv", "local_secrets",
                "authorization", "cookie", "api_key", "bearer"):
        assert tok not in low, f"hygiene script must not touch: {tok}"
    # No mutating git / filesystem commands — read-only by construction.
    for tok in ('"add"', "'add'", '"commit"', "'commit'", '"rm"', "'rm'",
                '"clean"', "'clean'", '"reset"', "'reset'", '"checkout"',
                "'checkout'", '"restore"', "'restore'", '"stash"', "'stash'",
                '"push"', "'push'", "os.remove", "shutil.rmtree", "path.unlink",
                ".write_bytes("):
        assert tok not in low, f"hygiene script must not mutate via: {tok}"


def test_file_hygiene_module_builds_expected_shape(monkeypatch):
    # Run build_report without touching the real repo: stub the git wrapper.
    import importlib.util
    script = _REPO_ROOT / "tools" / "jarvis_file_hygiene_report.py"
    spec = importlib.util.spec_from_file_location("jarvis_file_hygiene_report", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    porcelain = (
        "?? data/a.json\n"
        "?? data/b.json\n"
        "?? tools/x.py\n"
        " M app.py\n"
        "M  templates/jarvis.html\n"
    )

    def _fake_git(args):
        if args[:1] == ["status"]:
            return 0, porcelain
        if args[:1] == ["check-ignore"]:
            return 0, ""
        return 0, ""

    monkeypatch.setattr(mod, "_git", _fake_git)
    report = mod.build_report()
    assert report["state"] == "ready"
    assert report["git_ok"] is True
    assert report["total_untracked_count"] == 3
    # ' M' = worktree modified; 'M ' = staged.
    assert report["tracked_modified_count"] == 1
    assert report["staged_count"] == 1
    top = {d["dir"]: d["count"] for d in report["top_untracked_dirs"]}
    assert top.get("data") == 2 and top.get("tools") == 1
    # A staged file must raise an operator warning.
    assert any("STAGED" in w for w in report["warnings"])


def test_file_hygiene_report_exposes_no_mutation_fields():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    fh = client.get("/api/jarvis/status").json()["file_hygiene_report"]

    def _keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield str(k).lower()
                yield from _keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from _keys(v)

    keys = set(_keys(fh))
    for forbidden in ("delete", "remove", "clean", "stage", "commit", "exec",
                      "run_command", "shell", "rmtree", "unlink", "trigger"):
        assert forbidden not in keys, f"forbidden mutation key: {forbidden}"


# --- Step 09: commander's snapshot (derived, read-only) -------------------

def _green_snapshot_inputs():
    return dict(
        operator_safety={"state": "locked", "read_only": True,
                         "no_broker_control": True, "no_execution_control": True},
        safety_gates={"state": "locked"},
        health={"state": "ready", "overall": "pass"},
        route_smoke={"state": "ready", "overall": "pass"},
        mission_board={"counts": {"total": 4}},
        prompt_library={"counts": {"total": 8}},
        file_hygiene={"state": "ready", "total_untracked_count": 12, "staged_count": 0},
        trading_detail={"broker_control": False, "paper_ready": False,
                        "live_ready": False},
        git={"dirty": False},
    )


def test_jarvis_status_has_commander_snapshot_key():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()
    assert "commander_snapshot" in d
    cs = d["commander_snapshot"]
    assert isinstance(cs, dict)
    for key in ("overall_state", "headline", "safety_status", "health_status",
                "route_smoke_status", "trading_posture", "mission_count",
                "prompt_count", "staged_count", "untracked_count", "warnings"):
        assert key in cs, f"snapshot missing {key}"
    assert cs["overall_state"] in ("green", "yellow", "red")


def test_commander_snapshot_green_only_when_all_clear():
    import app as app_module
    cs = app_module._jarvis_commander_snapshot(**_green_snapshot_inputs())
    assert cs["overall_state"] == "green", cs
    assert cs["safety_status"] == "locked"
    assert cs["health_status"] == "pass"
    assert cs["route_smoke_status"] == "pass"
    assert cs["trading_posture"] == "research_only"
    assert cs["mission_count"] == 4
    assert cs["prompt_count"] == 8


def test_commander_snapshot_red_when_safety_unsafe():
    import app as app_module
    args = _green_snapshot_inputs()
    args["operator_safety"] = {"state": "locked", "read_only": True,
                               "no_broker_control": False,
                               "no_execution_control": True}
    cs = app_module._jarvis_commander_snapshot(**args)
    assert cs["overall_state"] == "red", cs
    assert cs["safety_status"] == "unknown"


def test_commander_snapshot_red_when_execution_capability_present():
    import app as app_module
    args = _green_snapshot_inputs()
    args["trading_detail"] = {"broker_control": False, "paper_ready": True,
                              "live_ready": False}
    cs = app_module._jarvis_commander_snapshot(**args)
    assert cs["overall_state"] == "red", cs
    assert cs["trading_posture"] == "EXECUTION_RISK"


def test_commander_snapshot_red_when_required_report_fails():
    import app as app_module
    args = _green_snapshot_inputs()
    args["route_smoke"] = {"state": "ready", "overall": "fail"}
    cs = app_module._jarvis_commander_snapshot(**args)
    assert cs["overall_state"] == "red", cs
    assert cs["route_smoke_status"] == "fail"


def test_commander_snapshot_yellow_when_report_missing():
    import app as app_module
    args = _green_snapshot_inputs()
    args["health"] = {"state": "missing"}
    cs = app_module._jarvis_commander_snapshot(**args)
    assert cs["overall_state"] == "yellow", cs
    assert cs["health_status"] == "missing"


def test_commander_snapshot_yellow_when_files_staged():
    import app as app_module
    args = _green_snapshot_inputs()
    args["file_hygiene"] = {"state": "ready", "total_untracked_count": 5,
                            "staged_count": 2}
    cs = app_module._jarvis_commander_snapshot(**args)
    assert cs["overall_state"] == "yellow", cs
    assert cs["staged_count"] == 2
    assert any("staged" in w.lower() for w in cs["warnings"])


def test_commander_snapshot_yellow_when_tree_dirty_or_huge_backlog():
    import app as app_module
    args = _green_snapshot_inputs()
    args["git"] = {"dirty": True}
    args["file_hygiene"] = {"state": "ready", "total_untracked_count": 4371,
                            "staged_count": 0}
    cs = app_module._jarvis_commander_snapshot(**args)
    assert cs["overall_state"] == "yellow", cs


def test_commander_snapshot_derives_from_live_sections():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    d = client.get("/api/jarvis/status").json()
    cs = d["commander_snapshot"]
    # mission/prompt counts must mirror the underlying sections, not invent data
    assert cs["mission_count"] == (d["mission_board"].get("counts") or {}).get("total", 0)
    assert cs["prompt_count"] == (d["prompt_library"].get("counts") or {}).get("total", 0)
    fh = d["file_hygiene_report"]
    if fh.get("state") == "ready":
        assert cs["untracked_count"] == fh.get("total_untracked_count")
        assert cs["staged_count"] == fh.get("staged_count")


def test_commander_snapshot_endpoint_runs_no_new_commands(monkeypatch):
    # Producing the snapshot must not spawn a subprocess or make an HTTP call.
    # (git/route sections are fail-closed; the snapshot only reads their dicts.)
    import subprocess
    import urllib.request
    import app as app_module
    from fastapi.testclient import TestClient

    def _boom(*a, **k):
        raise AssertionError("snapshot must not run new commands / scans")

    monkeypatch.setattr(subprocess, "run", _boom)
    monkeypatch.setattr(subprocess, "Popen", _boom)
    monkeypatch.setattr(urllib.request, "urlopen", _boom)
    client = TestClient(app_module.app)
    r = client.get("/api/jarvis/status")
    assert r.status_code == 200
    cs = r.json()["commander_snapshot"]
    assert cs["overall_state"] in ("green", "yellow", "red")


def test_commander_snapshot_exposes_no_execution_fields():
    import app as app_module
    from fastapi.testclient import TestClient
    client = TestClient(app_module.app)
    cs = client.get("/api/jarvis/status").json()["commander_snapshot"]

    def _keys(o):
        if isinstance(o, dict):
            for k, v in o.items():
                yield str(k).lower()
                yield from _keys(v)
        elif isinstance(o, list):
            for v in o:
                yield from _keys(v)

    keys = set(_keys(cs))
    for forbidden in ("run_command", "exec", "shell", "place_order",
                      "submit_order", "execute_trade", "stage", "commit",
                      "delete", "trigger", "onclick"):
        assert forbidden not in keys, f"forbidden control key: {forbidden}"


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

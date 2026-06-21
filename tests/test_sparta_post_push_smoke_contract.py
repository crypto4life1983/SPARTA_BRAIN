"""Tests for the SPARTA post-push smoke (Bundle E3, read-only).

Proves the smoke folds the gathered read-only checks into POST_PUSH_SMOKE_OK /
POST_PUSH_SMOKE_NEEDS_ATTENTION; flags repo/guard/current-state/watchdog/lifecycle/control
failures with reasons; treats the watchdog/lifecycle/control safety flags as hard SAFETY
alarms; runs nothing itself (no task/token/gate); and -- via the live runner -- builds a
valid report read-only. Anti-tamper + module/runner purity."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.sparta_post_push_smoke_contract as ps
import tools.sparta_post_push_smoke_once as runner


def _ok_inputs(**ov):
    base = {
        "repo": {"head": "h", "origin": "h", "ahead": 0, "behind": 0, "clean": True,
                 "staged_count": 0, "dangerous_staged": False},
        "artifact_guard_clean": True,
        "current_state": {"overall_status": "HEALTHY", "c22_progress": "1/20",
                          "c22_state": "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS",
                          "task_health_overall": "OK"},
        "watchdog": {"severity": "NONE", "primary_recommendation": "NO_ACTION_REQUIRED",
                     "reran_any_task": False, "changed_any_scheduled_task": False,
                     "auto_executes_any_token": False},
        "lifecycle": {"current_gate": "C22_COLLECT_MORE_WINDOWS",
                      "suggested_human_token": "HUMAN_STAGE_MORE", "advances_any_candidate": False,
                      "opens_c23_as_active": False, "auto_executes_any_token": False,
                      "modifies_repo": False},
        "control_route": {"available": True, "status_code": 200, "has_control_panel": True,
                          "has_c22_hold": True, "has_watchdog_section": True,
                          "has_lifecycle_section": True, "no_execution_affordances": True},
    }
    base.update(ov)
    return base


# ---- all-clear -------------------------------------------------------------

def test_all_clear_ok():
    r = ps.build_smoke_report(_ok_inputs())
    assert r["overall"] == "POST_PUSH_SMOKE_OK"
    assert r["all_clear"] is True
    assert r["failed_checks"] == []
    assert r["attention_reasons"] == []
    assert ps.validate_smoke_report(r)["valid"] is True


# ---- repo out of sync / dirty / dangerous staged ---------------------------

def test_repo_out_of_sync_attention():
    r = ps.build_smoke_report(_ok_inputs(repo={"head": "a", "origin": "b", "ahead": 1,
                                               "behind": 0, "clean": True,
                                               "staged_count": 0,
                                               "dangerous_staged": False}))
    assert r["overall"] == "POST_PUSH_SMOKE_NEEDS_ATTENTION"
    assert "repo_in_sync" in r["failed_checks"]
    assert ps.validate_smoke_report(r)["valid"] is True


def test_dangerous_staged_attention():
    r = ps.build_smoke_report(_ok_inputs(
        repo={"head": "h", "origin": "h", "ahead": 0, "behind": 0, "clean": True,
              "staged_count": 1, "dangerous_staged": True},
        artifact_guard_clean=False))
    assert r["overall"] == "POST_PUSH_SMOKE_NEEDS_ATTENTION"
    assert "artifact_guard_clean" in r["failed_checks"]
    assert "repo_clean_no_staged" in r["failed_checks"]


# ---- SAFETY failures are hard alarms ---------------------------------------

def test_watchdog_safety_violation_is_hard_attention():
    r = ps.build_smoke_report(_ok_inputs(
        watchdog={"severity": "NONE", "primary_recommendation": "NO_ACTION_REQUIRED",
                  "reran_any_task": True, "changed_any_scheduled_task": False,
                  "auto_executes_any_token": False}))
    assert r["overall"] == "POST_PUSH_SMOKE_NEEDS_ATTENTION"
    assert "watchdog_safe" in r["safety_failed"]
    assert "SAFETY:watchdog_safe" in r["attention_reasons"]


def test_lifecycle_safety_violation_is_hard_attention():
    r = ps.build_smoke_report(_ok_inputs(
        lifecycle={"current_gate": "C22_COLLECT_MORE_WINDOWS",
                   "suggested_human_token": "X", "advances_any_candidate": True,
                   "opens_c23_as_active": False, "auto_executes_any_token": False,
                   "modifies_repo": False}))
    assert "lifecycle_safe" in r["safety_failed"]
    assert "SAFETY:lifecycle_safe" in r["attention_reasons"]


def test_control_execution_affordance_is_hard_attention():
    r = ps.build_smoke_report(_ok_inputs(
        control_route={"available": True, "status_code": 200, "has_control_panel": True,
                       "has_c22_hold": True, "has_watchdog_section": True,
                       "has_lifecycle_section": True, "no_execution_affordances": False}))
    assert "control_no_execution_affordances" in r["safety_failed"]


# ---- control route non-200 / missing sections ------------------------------

def test_control_route_failure_attention():
    r = ps.build_smoke_report(_ok_inputs(
        control_route={"available": False, "status_code": 500, "has_control_panel": False,
                       "has_c22_hold": False, "has_watchdog_section": False,
                       "has_lifecycle_section": False, "no_execution_affordances": False}))
    assert r["overall"] == "POST_PUSH_SMOKE_NEEDS_ATTENTION"
    for c in ("control_route_200", "control_panel_present", "control_watchdog_section",
              "control_lifecycle_section"):
        assert c in r["failed_checks"]


# ---- the smoke runs nothing itself -----------------------------------------

def test_smoke_runs_nothing():
    r = ps.build_smoke_report(_ok_inputs())
    assert r["executed_no_task"] is True
    assert r["executed_no_token"] is True
    assert r["advanced_no_gate"] is True
    for flag in ("runs_tasks", "reruns_pickup", "reruns_import", "auto_executes_any_token",
                 "advances_any_candidate", "opens_c23_as_active", "modifies_repo",
                 "commits", "pushes"):
        assert r[flag] is False, flag
    for key, val in r["scope_locks"].items():
        assert val is True, key


# ---- anti-tamper -----------------------------------------------------------

def test_tamper_rejected():
    r = ps.build_smoke_report(_ok_inputs())
    # claim OK while a check failed
    bad = {**r, "checks": {**r["checks"], "repo_in_sync": False}}
    assert ps.validate_smoke_report(bad)["valid"] is False
    # claim executed a token
    assert ps.validate_smoke_report({**r, "executed_no_token": False})["valid"] is False
    for flag in ps._CAPABILITY_FLAGS_FALSE:
        assert ps.validate_smoke_report({**r, flag: True})["valid"] is False


# ---- markdown render -------------------------------------------------------

def test_render_markdown():
    md = ps.render_smoke_markdown(ps.build_smoke_report(_ok_inputs()))
    assert "POST_PUSH_SMOKE_OK" in md
    assert "Watchdog: NONE" in md
    assert "Lifecycle gate: C22_COLLECT_MORE_WINDOWS" in md


# ---- runner builds a valid live report read-only ---------------------------

def test_runner_builds_valid_report():
    r = runner.build_smoke()
    assert ps.validate_smoke_report(r)["valid"] is True
    assert r["overall"] in ("POST_PUSH_SMOKE_OK", "POST_PUSH_SMOKE_NEEDS_ATTENTION")


# ---- runner does no commit/push/rerun/token-exec ---------------------------

_FORBIDDEN_RUNNER_TOKENS = (
    "git commit", "git push", "git add", "import_one", "run_import_automation",
    "Register-ScheduledTask", "Start-ScheduledTask", "schtasks /run", "place_order",
    "build_c23_proposal", "import requests",
)


def test_runner_read_only():
    src = Path(runner.__file__).read_text(encoding="utf-8")
    for tok in _FORBIDDEN_RUNNER_TOKENS:
        assert tok not in src, tok
    # only read-only git subcommands are allow-listed
    assert "_GIT_READ_ALLOWLIST" in src


# ---- contract module purity ------------------------------------------------

def test_contract_module_purity():
    src = Path(ps.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "json.load", "read_text", "glob(",
                 "TestClient"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas",
              "fastapi"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned

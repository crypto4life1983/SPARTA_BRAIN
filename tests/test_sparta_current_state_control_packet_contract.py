"""Tests for the SPARTA current-state control packet (contract + read-only runner).

Proves the canonical packet aggregates repo state (incl. the dangerous-staged artifact
guard), lane state (C21 closed/ledger-26, C22 active HOLD replay-locked, C23 on-deck),
C22 collection (progress, missing-export warning, 20/20 readiness alert), scheduled-task
health, and the next-action tokens (collect / review-at-20 / open-C23-after-C22) as
SUGGESTIONS ONLY (never auto-executed); overall_status HEALTHY vs NEEDS_ATTENTION is
consistent with the attention reasons; and module/runner purity + anti-tamper."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.sparta_current_state_control_packet_contract as cp
import sparta_commander.sparta_scheduled_task_health_classifier_contract as th
import tools.sparta_current_state_once as runner

_COLLECT = "HUMAN_STAGE_MORE_FROZEN_DAILY_TREND_RADAR_GC_WINDOWS_THEN_REREVIEW_C22_LABELS"
_REVIEW = "HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW"
_C23_OPEN = "HUMAN_DECISION_OPEN_CANDIDATE_23_AFTER_C22_CONCLUDES_OR_HOLD"

_CLEAN_REPO = {"head": "h", "origin": "h", "ahead": 0, "behind": 0, "clean": True,
               "staged_paths": []}
_OK_HEALTH = th.build_task_health(
    [{"name": n, "found": True, "last_result": 0, "hours_since_last_run": 3.0}
     for n in th.PRIORITY_TASKS])

_P = cp.build_current_state_packet(_CLEAN_REPO, 1, "2026-06-20", 1, _OK_HEALTH)


# ---- healthy aggregate (clean repo, ok tasks, fresh export) ----------------

def test_healthy_aggregate():
    assert _P["verdict"] == "SPARTA_CURRENT_STATE_CONTROL_PACKET"
    assert _P["overall_status"] == "HEALTHY"
    assert _P["attention_reasons"] == []
    assert cp.validate_current_state_packet(_P)["valid"] is True


# ---- repo state + dangerous-staged guard -----------------------------------

def test_repo_state_and_dangerous_staged_guard():
    rs = _P["repo_state"]
    assert rs["in_sync"] is True and rs["tracked_tree_clean"] is True
    assert rs["has_staged"] is False
    assert rs["dangerous_staged_artifact"] is False
    # staging a gitignored dataset artifact -> dangerous + NEEDS_ATTENTION
    dirty = {**_CLEAN_REPO, "clean": False,
             "staged_paths": ["data/external_signum_trend_radar_gc/x.json"]}
    p = cp.build_current_state_packet(dirty, 1, "2026-06-20", 1, _OK_HEALTH)
    assert p["repo_state"]["dangerous_staged_artifact"] is True
    assert p["overall_status"] == "NEEDS_ATTENTION"
    assert "dangerous_artifact_staged" in p["attention_reasons"]
    assert "tracked_tree_dirty" in p["attention_reasons"]
    assert cp.is_dangerous_staged(["reports/automation_v2_daily/r.md"]) is True
    assert cp.is_dangerous_staged(["sparta_commander/foo.py"]) is False


# ---- lane state ------------------------------------------------------------

def test_lane_state():
    lane = _P["lane"]
    assert lane["c21_closed_rejected"] is True and lane["rejected_ledger_count"] == 26
    assert lane["active_candidate"] == "C22"
    assert lane["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert lane["c22_replay_locked"] is True
    assert lane["c23_on_deck"] is True and lane["c23_is_active"] is False


# ---- C22 collection: progress, missing-export, readiness alert -------------

def test_c22_collection_progress_and_missing_export():
    c = _P["c22_collection"]
    assert c["progress"] == "1/20" and c["windows_remaining"] == 19
    assert c["missing_export_warning"] is False
    # an export gap of >1 day -> missing-export warning + NEEDS_ATTENTION
    p = cp.build_current_state_packet(_CLEAN_REPO, 1, "2026-06-18", 3, _OK_HEALTH)
    assert p["c22_collection"]["missing_export_warning"] is True
    assert p["c22_collection"]["missing_export_detail"]
    assert "c22_export_appears_missing" in p["attention_reasons"]
    assert p["overall_status"] == "NEEDS_ATTENTION"


def test_2020_readiness_alert_suggestion_only():
    p = cp.build_current_state_packet(_CLEAN_REPO, 20, "2026-07-09", 0, _OK_HEALTH)
    c = p["c22_collection"]
    assert c["progress"] == "20/20" and c["ready_for_review"] is True
    assert c["readiness_alert"] and _REVIEW in c["readiness_alert"]
    # at 20/20 the authoritative action is the SUGGESTED review token
    assert p["next_action"]["authoritative_next_action"] == _REVIEW
    assert p["next_action"]["auto_executes_any_token"] is False
    assert cp.validate_current_state_packet(p)["valid"] is True


# ---- task-health failure surfaces as NEEDS_ATTENTION ------------------------

def test_task_failure_surfaces_attention():
    bad_health = th.build_task_health([
        {"name": "C22_Signum_GC_Import_Automation", "found": True, "last_result": 2,
         "hours_since_last_run": 6.0}])
    p = cp.build_current_state_packet(_CLEAN_REPO, 1, "2026-06-20", 1, bad_health)
    assert "scheduled_task_failed_or_missing" in p["attention_reasons"]
    assert p["overall_status"] == "NEEDS_ATTENTION"


# ---- next-action tokens are suggestion-only, never auto-executed -----------

def test_tokens_suggestion_only():
    na = _P["next_action"]
    assert na["authoritative_next_action"] == _COLLECT          # < 20
    assert na["collect_more_windows_token"] == _COLLECT
    assert na["review_token_when_ready"] == _REVIEW
    assert na["c23_open_token_after_c22"] == _C23_OPEN
    assert na["tokens_are_suggestion_only"] is True
    assert na["auto_executes_any_token"] is False


# ---- anti-tamper -----------------------------------------------------------

def test_tamper_rejected():
    # HEALTHY with attention reasons -> invalid
    bad = {**_P, "attention_reasons": ["x"]}
    assert cp.validate_current_state_packet(bad)["valid"] is False
    # tokens auto-execute -> invalid
    bad2 = {**_P, "next_action": {**_P["next_action"], "auto_executes_any_token": True}}
    assert cp.validate_current_state_packet(bad2)["valid"] is False
    for flag in cp._CAPABILITY_FLAGS_FALSE:
        assert _P[flag] is False, flag
        assert cp.validate_current_state_packet({**_P, flag: True})["valid"] is False
    for key, val in _P["scope_locks"].items():
        assert val is True, key


# ---- runner builds a valid packet read-only --------------------------------

def test_runner_builds_valid_packet():
    p = runner.build_current_state()
    assert cp.validate_current_state_packet(p)["valid"] is True
    assert p["lane"]["active_candidate"] == "C22"


# ---- runners do no git-write / scheduler-mutation / trading ----------------

_FORBIDDEN_RUNNER_TOKENS = (
    "git commit", "git push", "git add", "Register-ScheduledTask", "New-ScheduledTask",
    "Set-ScheduledTask", "schtasks /create", "schtasks /change", "place_order",
    "send-trading-signal", "import requests", "import ccxt",
)


def test_runners_read_only():
    for mod in (runner, __import__("tools.sparta_scheduled_task_status_once",
                                   fromlist=["x"])):
        src = Path(mod.__file__).read_text(encoding="utf-8")
        for tok in _FORBIDDEN_RUNNER_TOKENS:
            assert tok not in src, "%s: %s" % (Path(mod.__file__).name, tok)


# ---- contract module purity ------------------------------------------------

def test_contract_module_purity():
    src = Path(cp.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "json.load", "read_text", "glob(",
                 ".now(", ".today("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas",
              "datetime"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned

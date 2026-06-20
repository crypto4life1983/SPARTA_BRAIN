"""Tests for the SPARTA Automation V2 -- Nightly Report Wrapper / Autopilot Readiness
bundle.

Verifies the wrapper is DEFINITION-ONLY and SCHEDULER-SAFE: it defines a safe read-only
invocation of the daily report runner (classified REPORT_ONLY / READ_ONLY / NO_NETWORK /
NO_GIT_WRITE), proves autopilot-queue eligibility as a reporting-only task, installs /
triggers NO scheduler (and neither the wrapper nor the runner source contains any
scheduler-install/trigger token), verifies the morning-output guarantee (C22
DATA_NOT_READY + dataset-staging token + do-not-proceed-to-labels + do-not-fabricate-data
+ danger locks + git-safety state), and proves the safe failure behaviour (unsafe repo ->
RESOLVE_REPO_BEFORE_AUTOMATION, never advance; never proceeds to labels). Includes the
proof that C22 DATA_NOT_READY still recommends dataset staging only."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.sparta_automation_v2_nightly_wrapper_contract as nw


_S = nw.build_nightly_wrapper_spec()
_ROOT = Path(nw.__file__).resolve().parents[1]
_RUNNER = _ROOT / "tools" / "sparta_automation_v2_daily_report_once.py"

# ACTIONABLE scheduler-install/trigger/persistence CALLS that must appear in NEITHER the
# wrapper NOR the runner. (The descriptive words "daemon"/"background"/"scheduler" appear
# only in the wrapper's NEGATED safety declarations, e.g. starts_persistent_daemon=False,
# and are intentionally excluded -- it is the actual API calls that are forbidden.)
_SCHEDULER_TOKENS = (
    "schtasks", "Register-ScheduledTask", "Unregister-ScheduledTask",
    "New-ScheduledTask", "ScheduledTaskTrigger", "crontab", "cron.d", "schedule.every",
    "at.exe", "systemctl", "launchctl", "while True", "BackgroundScheduler",
    "BlockingScheduler", "Popen", "nohup", "start /b",
)


# ---- core: spec builds + validates -----------------------------------------

def test_spec_builds_and_validates():
    assert _S["mode"] == "RESEARCH_ONLY"
    assert _S["is_definition_only"] is True
    assert _S["executes_nothing"] is True
    assert _S["does_not_invoke_runner"] is True
    assert _S["does_not_run_autopilot"] is True
    assert nw.validate_nightly_wrapper_spec(_S)["valid"] is True


# ---- (1) nightly wrapper: read-only invocation, gitignored output ----------

def test_runner_invocation_read_only_gitignored_output():
    assert _S["runner_path"] == "tools/sparta_automation_v2_daily_report_once.py"
    assert _S["runner_invocation"] == (
        "python tools/sparta_automation_v2_daily_report_once.py")
    assert _S["runner_is_read_only"] is True
    assert _S["output_artifact_dir"] == "reports/automation_v2_daily"
    assert _S["output_is_gitignored"] is True
    # the actual .gitignore covers the path
    gi = (_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "reports/automation_v2_daily/" in gi


# ---- (2) autopilot integration readiness: REPORT_ONLY task -----------------

def test_autopilot_queue_eligibility_report_only():
    assert set(_S["invocation_classification"]) >= {
        "REPORT_ONLY", "READ_ONLY", "NO_NETWORK", "NO_GIT_WRITE"}
    aq = _S["autopilot_queue_eligibility"]
    assert aq["eligible"] is True
    assert aq["task_class"] == "REPORT_ONLY"
    assert aq["read_only"] is True and aq["no_network"] is True
    assert aq["no_git_write"] is True
    assert aq["requires_no_human_gate_crossing"] is True
    assert aq["may_be_queued_as_reporting_only_task"] is True
    assert aq["does_not_auto_advance_or_promote"] is True


# ---- (3) scheduler safety: nothing installed / triggered -------------------

def test_scheduler_safety_flags():
    sch = _S["scheduler_safety"]
    for k in ("installs_scheduler", "triggers_scheduler",
              "modifies_windows_task_scheduler", "modifies_cron",
              "starts_background_process", "starts_persistent_daemon",
              "auto_executes", "modifies_existing_scheduled_task"):
        assert sch[k] is False, k
    assert sch["is_definition_only"] is True
    # tamper: claim it installs a scheduler -> invalid
    bad_sch = {**sch, "installs_scheduler": True}
    assert nw.validate_nightly_wrapper_spec(
        {**_S, "scheduler_safety": bad_sch})["valid"] is False


def test_no_scheduler_tokens_in_wrapper_or_runner():
    wrapper_src = Path(nw.__file__).read_text(encoding="utf-8")
    runner_src = _RUNNER.read_text(encoding="utf-8")
    for tok in _SCHEDULER_TOKENS:
        assert tok not in wrapper_src, "wrapper: %s" % tok
        assert tok not in runner_src, "runner: %s" % tok


# ---- (5) morning-output guarantee verified ---------------------------------

def test_morning_output_guarantee_verified():
    mog = _S["morning_output_guarantee"]
    assert mog["verified_ok"] is True
    assert mog["clean_report_valid"] is True
    for f in ("c22_data_not_ready", "next_human_approval_token",
              "do_not_proceed_to_labels", "do_not_fabricate_data", "danger_locks",
              "git_safe_to_automate", "git_head"):
        assert f in mog["required_fields"], f
    d = mog["detail"]
    assert d["token_is_dataset_staging"] is True
    assert d["c22_data_not_ready"] is True
    assert d["do_not_proceed_to_labels"] is True
    assert d["do_not_fabricate_data"] is True
    assert d["danger_locks_all_locked"] is True
    assert d["git_safety_state_present"] is True


def test_guarantee_fails_on_incomplete_report():
    # a report missing required fields fails the guarantee
    g = nw.verify_morning_output_guarantee({"c22_data_not_ready": True})
    assert g["ok"] is False
    assert "next_human_approval_token" in g["missing_fields"]
    # a report that surfaces labels instead of staging fails
    import sparta_commander.sparta_automation_v2_daily_report_contract as drc
    rep = drc.build_daily_report(dict(drc.SAMPLE_REPO_STATE), "2026-06-20T00:00:00Z")
    bad = {**rep, "next_human_approval_token": "HUMAN_DECISION_C22_ADVANCE_TO_LABELS"}
    assert nw.verify_morning_output_guarantee(bad)["ok"] is False


# ---- (6) failure behaviour: dirty repo -> RESOLVE_REPO, never advance ------

def test_failure_behavior_dirty_repo_resolve_not_advance():
    assert _S["dirty_state_recommendation"] == (
        "RECOMMEND_RESOLVE_REPO_BEFORE_AUTOMATION")
    assert _S["clean_state_recommendation"] == "RECOMMEND_DATASET_STAGING"
    fb = _S["failure_behavior"]
    assert fb["unsafe_repo_recommends_resolve_not_advance"] is True
    assert fb["dirty_report_does_not_advance_to_labels"] is True
    assert fb["dirty_report_still_says_do_not_proceed_to_labels"] is True
    assert fb["fails_safe_if_artifact_not_gitignored"] is True
    assert fb["disallowed_runner_action_fails_daily_report_validation"] is True


# ---- C22 DATA_NOT_READY still recommends dataset staging only ---------------

def test_c22_data_not_ready_staging_only():
    assert _S["c22_data_not_ready"] is True
    assert _S["clean_state_recommendation"] == "RECOMMEND_DATASET_STAGING"
    assert _S["next_human_approval_token"] == (
        "HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET_THEN_REAUTHORISE_C22_LABELS")
    # tamper: a clean-state recommendation that advances -> invalid
    bad = {**_S, "clean_state_recommendation": "RECOMMEND_ADVANCE_HUMAN_DECISION"}
    assert nw.validate_nightly_wrapper_spec(bad)["valid"] is False


# ---- (4) safety: capability flags + danger locks ---------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in nw._CAPABILITY_FLAGS_FALSE:
        assert _S[flag] is False, flag
        bad = {**_S, flag: True}
        assert nw.validate_nightly_wrapper_spec(bad)["valid"] is False, flag


def test_danger_locks_and_scope_locks():
    dl = _S["danger_locks"]
    for k in ("live_trading_locked", "paper_trading_locked", "signum_locked",
              "mcp_locked", "hyperliquid_locked", "scheduler_locked",
              "no_automatic_commit", "no_automatic_push", "never_skips_human_gates"):
        assert dl[k] is True, k
    for key, val in _S["scope_locks"].items():
        assert val is True, key
    for must in ("no_scheduler_install", "no_scheduler_trigger",
                 "no_modify_task_scheduler", "no_modify_cron", "no_background_process",
                 "no_persistent_daemon", "no_invoke_runner", "no_run_autopilot",
                 "no_modify_existing_scheduled_task"):
        assert _S["scope_locks"][must] is True, must


# ---- module purity (the pure definition contract) --------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(nw.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen", "urlopen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "os", "io", "shutil", "ssl", "ftplib",
              "datetime", "random", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    for call in ast.walk(tree):
        if isinstance(call, ast.Call):
            name = (call.func.attr if isinstance(call.func, ast.Attribute)
                    else getattr(call.func, "id", ""))
            assert name not in ("open", "exec", "eval", "compile"), name

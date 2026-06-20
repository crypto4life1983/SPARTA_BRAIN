"""Tests for the SPARTA Automation V2 -- Autopilot Task Registry / Allowlist Registration
bundle.

Verifies the registration is DEFINITION-ONLY and SAFE: it registers the Automation V2 daily
decision report runner (tools/sparta_automation_v2_daily_report_once.py) as an ALLOWED
REPORT_ONLY / READ_ONLY / NO_NETWORK / NO_GIT_WRITE task whose output stays in the
GITIGNORED reports/automation_v2_daily/ path; it does NOT mutate the frozen crypto_d1
overnight queue allowlist; it installs / triggers NO scheduler (and neither the contract
nor the runner source contains any scheduler-install/trigger token); it proves -- in-memory
-- the runner cannot fetch data, trade, place orders, commit, push, advance gates, promote
candidates, or use APIs; and it proves C22 DATA_NOT_READY still recommends dataset staging
only. The allowlist gate admits only the registered runner and refuses everything else."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.sparta_automation_v2_autopilot_task_registry_contract as tr
import sparta_commander.overnight_autopilot_research_queue_contract as oq

_R = tr.build_task_registration()
_ROOT = Path(tr.__file__).resolve().parents[1]
_RUNNER = _ROOT / "tools" / "sparta_automation_v2_daily_report_once.py"
_STAGING_TOKEN = (
    "HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET_THEN_REAUTHORISE_C22_LABELS")

# ACTIONABLE scheduler-install/trigger/persistence CALLS forbidden in BOTH the contract and
# the runner. (Descriptive words like "scheduler"/"daemon"/"background" appear only in the
# NEGATED safety declarations, e.g. starts_persistent_daemon=False, and are excluded.)
_SCHEDULER_TOKENS = (
    "schtasks", "Register-ScheduledTask", "Unregister-ScheduledTask",
    "New-ScheduledTask", "ScheduledTaskTrigger", "crontab", "cron.d", "schedule.every",
    "at.exe", "systemctl", "launchctl", "while True", "BackgroundScheduler",
    "BlockingScheduler", "nohup", "start /b",
)


# ---- core: registration builds, validates, REGISTERED -----------------------

def test_registration_builds_and_validates_registered():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["verdict"] == tr.VERDICT_REGISTERED
    assert _R["blockers"] == []
    assert _R["is_definition_only"] is True
    assert _R["executes_nothing"] is True
    assert tr.validate_task_registration(_R)["valid"] is True


# ---- (1) the registered REPORT_ONLY task row --------------------------------

def test_registered_task_is_report_only_gitignored():
    assert tuple(_R["registered_report_only_tasks"]) == (tr.REGISTERED_TASK_ID,)
    rt = _R["registered_task"]
    assert rt["task_id"] == "automation_v2_daily_report"
    assert rt["runner_path"] == "tools/sparta_automation_v2_daily_report_once.py"
    assert rt["runner_invocation"] == (
        "python tools/sparta_automation_v2_daily_report_once.py")
    assert rt["task_class"] == "REPORT_ONLY"
    assert set(rt["classification"]) >= {
        "REPORT_ONLY", "READ_ONLY", "NO_NETWORK", "NO_GIT_WRITE"}
    assert rt["output_artifact_dir"] == "reports/automation_v2_daily"
    assert rt["output_is_gitignored"] is True
    assert rt["enabling_in_overnight_runner_is_a_separate_human_gate"] is True
    # the actual .gitignore covers the path
    gi = (_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "reports/automation_v2_daily/" in gi
    # the runner file the registration points at actually exists
    assert _RUNNER.is_file()


# ---- (2) eligible for a future overnight report-only queue ------------------

def test_autopilot_queue_eligibility_report_only():
    aq = _R["autopilot_queue_eligibility"]
    assert aq["eligible_for_report_only_queue"] is True
    assert aq["task_class"] == "REPORT_ONLY"
    assert aq["read_only"] is True and aq["no_network"] is True
    assert aq["no_git_write"] is True
    assert aq["requires_no_human_gate_crossing"] is True
    assert aq["does_not_auto_advance_or_promote"] is True
    assert _R["next_required_action"] == (
        "HUMAN_APPROVED_ENABLE_AUTOMATION_V2_REPORT_ONLY_TASK_IN_OVERNIGHT_QUEUE")


# ---- (3) does NOT mutate the frozen crypto_d1 overnight queue allowlist -----

def test_does_not_modify_frozen_overnight_queue_allowlist():
    assert _R["does_not_modify_frozen_overnight_queue_allowlist"] is True
    assert _R["modifies_frozen_overnight_queue_allowlist"] is False
    # the frozen allowlist is exactly the original four task types -- untouched.
    assert oq.ALLOWED_TASK_TYPES == (
        "integrity_audit", "contract_certification_sweep",
        "safety_test_suite_report", "seed_research_brief_draft")
    assert tr.REGISTERED_TASK_ID not in oq.ALLOWED_TASK_TYPES
    # the frozen queue contract still self-certifies unchanged
    c = oq.build_overnight_autopilot_contract()
    assert oq.validate_overnight_autopilot_contract(c)["valid"] is True
    assert tuple(c["allowed_task_types"]) == oq.ALLOWED_TASK_TYPES


# ---- (4) scheduler safety: nothing installed / triggered -------------------

def test_scheduler_safety_flags():
    sch = _R["scheduler_safety"]
    for k in ("installs_scheduler", "triggers_scheduler",
              "modifies_windows_task_scheduler", "modifies_cron",
              "modifies_existing_scheduled_task", "starts_background_process",
              "starts_persistent_daemon", "auto_executes"):
        assert sch[k] is False, k
    assert sch["is_definition_only"] is True
    # tamper: claim it installs a scheduler -> invalid
    bad = {**_R, "scheduler_safety": {**sch, "installs_scheduler": True}}
    assert tr.validate_task_registration(bad)["valid"] is False


def test_no_scheduler_tokens_in_contract_or_runner():
    contract_src = Path(tr.__file__).read_text(encoding="utf-8")
    runner_src = _RUNNER.read_text(encoding="utf-8")
    for tok in _SCHEDULER_TOKENS:
        assert tok not in contract_src, "contract: %s" % tok
        assert tok not in runner_src, "runner: %s" % tok


# ---- (5) safety proof: cannot fetch/trade/order/commit/push/advance/promote/api

def test_registered_runner_proven_incapable_of_dangerous_actions():
    proof = _R["registration_safety_proof"]
    assert proof["all_dangerous_capabilities_disproven"] is True
    pic = proof["proven_incapable_of"]
    for k in ("fetch_data", "trade", "place_orders", "commit", "push",
              "advance_gate", "promote_candidate", "use_api"):
        assert pic[k] is True, k
    assert proof["daily_report_valid"] is True
    assert proof["morning_output_guarantee_ok"] is True
    assert _R["nightly_wrapper_valid"] is True


# ---- (6) C22 DATA_NOT_READY still recommends dataset staging only -----------

def test_c22_data_not_ready_staging_only():
    assert _R["c22_data_not_ready"] is True
    assert _R["recommends_dataset_staging_only"] is True
    assert _R["next_human_approval_token"] == _STAGING_TOKEN
    proof = _R["registration_safety_proof"]
    assert proof["recommended_gate_kind"] == "RECOMMEND_DATASET_STAGING"
    # tamper: a proof that no longer recommends staging-only -> invalid
    bad_proof = {**proof, "recommends_dataset_staging_only": False}
    bad = {**_R, "registration_safety_proof": bad_proof,
           "recommends_dataset_staging_only": False}
    assert tr.validate_task_registration(bad)["valid"] is False


# ---- (7) allowlist gate admits only the registered runner ------------------

def test_allowlist_gate_admits_only_registered_runner():
    ok = tr.is_task_allowed_in_report_only_queue({
        "task_id": "automation_v2_daily_report", "task_class": "REPORT_ONLY",
        "runner_path": "tools/sparta_automation_v2_daily_report_once.py"})
    assert ok["allowed"] is True and ok["reasons"] == []
    # unregistered task_id refused
    assert tr.is_task_allowed_in_report_only_queue({
        "task_id": "data_fetch_run", "task_class": "REPORT_ONLY"})["allowed"] is False
    # wrong task_class refused
    assert tr.is_task_allowed_in_report_only_queue({
        "task_id": "automation_v2_daily_report",
        "task_class": "EXECUTE"})["allowed"] is False
    # forbidden credential/order field refused
    bad = tr.is_task_allowed_in_report_only_queue({
        "task_id": "automation_v2_daily_report", "task_class": "REPORT_ONLY",
        "api_key": "x"})
    assert bad["allowed"] is False
    assert any("forbidden_descriptor_field" in r for r in bad["reasons"])
    # non-dict refused
    assert tr.is_task_allowed_in_report_only_queue("nope")["allowed"] is False


# ---- (8) danger locks + capability flags all locked/false ------------------

def test_danger_locks_and_capability_flags():
    dl = _R["danger_locks"]
    for k in ("live_trading_locked", "paper_trading_locked", "signum_locked",
              "mcp_locked", "hyperliquid_locked", "scheduler_locked",
              "no_automatic_commit", "no_automatic_push", "no_automatic_data_fetch",
              "never_skips_human_gates"):
        assert dl[k] is True, k
    for flag in tr._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert tr.validate_task_registration(bad)["valid"] is False, flag
    for key, val in _R["scope_locks"].items():
        assert val is True, key


# ---- module purity (the pure definition contract) --------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = Path(tr.__file__).read_text(encoding="utf-8")
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

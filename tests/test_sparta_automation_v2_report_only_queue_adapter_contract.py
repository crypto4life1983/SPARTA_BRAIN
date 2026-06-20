"""Tests for the SPARTA Automation V2 -- Report-Only Queue Adapter bundle.

Proves the adapter additively WIRES the registered Automation V2 daily report task into a
consultable overnight/autopilot REPORT-ONLY queue without touching the frozen legacy
allowlist: automation_v2_daily_report is eligible for future overnight report-only
execution; it stays REPORT_ONLY / READ_ONLY / NO_NETWORK / NO_GIT_WRITE; its output path
stays gitignored; the frozen crypto_d1 overnight queue allowlist is preserved byte-for-byte
(and the V2 task is not smuggled into it); no scheduler is installed/triggered (and no
scheduler/data-fetch/git-write tokens appear in the contract); dispatch executes nothing;
the runner is proven incapable of fetch/trade/order/commit/push/advance/promote/api; C22
DATA_NOT_READY still recommends dataset staging only; and Jarvis/morning report can surface
the generated artifact path."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.sparta_automation_v2_report_only_queue_adapter_contract as qa
import sparta_commander.sparta_automation_v2_autopilot_task_registry_contract as tr
import sparta_commander.overnight_autopilot_research_queue_contract as oq
import tools.sparta_autopilot_morning_report as mr

_Q = qa.build_v2_report_only_queue()
_ROOT = Path(qa.__file__).resolve().parents[1]
_RUNNER = _ROOT / "tools" / "sparta_automation_v2_daily_report_once.py"
_STAGING_TOKEN = (
    "HUMAN_STAGE_FROZEN_TREND_RADAR_GC_DETECTOR_DATASET_THEN_REAUTHORISE_C22_LABELS")

# actionable scheduler-install/trigger/persistence + git-write/data-fetch CALLS / IMPORTS
# that must NOT appear in the adapter source. Descriptive negated-safety words (e.g.
# "accesses_hyperliquid=False", "no_hyperliquid=True") are intentionally excluded -- it is
# the actual API calls / imports that are forbidden, proven via the capability flags below.
_FORBIDDEN_SOURCE_TOKENS = (
    "schtasks", "Register-ScheduledTask", "ScheduledTaskTrigger", "crontab",
    "schedule.every", "systemctl", "launchctl", "while True", "BackgroundScheduler",
    "BlockingScheduler", "Popen", "subprocess", "nohup", "start /b",
    "import requests", "from requests", "import ccxt", "from ccxt",
    "import hyperliquid", "urlopen", "git commit", "git push", "git add",
)


# ---- core: adapter builds, validates, READY --------------------------------

def test_adapter_builds_and_validates_ready():
    assert _Q["mode"] == "RESEARCH_ONLY"
    assert _Q["verdict"] == qa.VERDICT_QUEUE_READY
    assert _Q["blockers"] == []
    assert _Q["is_definition_only"] is True
    assert _Q["is_additive_adapter"] is True
    assert _Q["executes_nothing"] is True
    assert qa.validate_v2_report_only_queue(_Q)["valid"] is True


# ---- (1) the task is eligible for future overnight report-only execution ----

def test_task_eligible_for_future_overnight_report_only_execution():
    assert _Q["eligible_for_future_overnight_report_only_execution"] is True
    assert _Q["queue_task_ids"] == ["automation_v2_daily_report"]
    assert len(_Q["queue"]) == 1
    entry = _Q["queue"][0]
    assert entry["task_id"] == "automation_v2_daily_report"
    assert entry["runner_path"] == "tools/sparta_automation_v2_daily_report_once.py"
    assert entry["allowlist_check"]["allowed"] is True
    assert _Q["registry_verdict"] == tr.VERDICT_REGISTERED
    assert _Q["registry_valid"] is True
    assert _RUNNER.is_file()


# ---- (2) stays REPORT_ONLY / READ_ONLY / NO_NETWORK / NO_GIT_WRITE ----------

def test_entry_stays_report_only_read_only_no_network_no_git_write():
    entry = _Q["queue"][0]
    assert entry["task_class"] == "REPORT_ONLY"
    assert set(entry["classification"]) >= {
        "REPORT_ONLY", "READ_ONLY", "NO_NETWORK", "NO_GIT_WRITE"}
    assert entry["read_only"] is True
    assert entry["no_network"] is True
    assert entry["no_git_write"] is True


# ---- (3) output path gitignored --------------------------------------------

def test_output_path_gitignored():
    assert _Q["artifact_dir"] == "reports/automation_v2_daily"
    assert _Q["artifact_is_gitignored"] is True
    assert _Q["queue"][0]["output_is_gitignored"] is True
    gi = (_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "reports/automation_v2_daily/" in gi


# ---- (4) frozen legacy allowlist preserved, V2 task not smuggled in --------

def test_frozen_legacy_allowlist_preserved():
    assert _Q["does_not_modify_frozen_overnight_queue_allowlist"] is True
    assert _Q["modifies_frozen_overnight_queue_allowlist"] is False
    legacy = _Q["legacy_allowlist_preserved"]
    assert legacy["unchanged"] is True
    assert legacy["v2_task_not_in_legacy_allowlist"] is True
    assert legacy["legacy_contract_self_certifies"] is True
    # the real frozen tuple is untouched + the V2 task is not in it
    assert oq.ALLOWED_TASK_TYPES == (
        "integrity_audit", "contract_certification_sweep",
        "safety_test_suite_report", "seed_research_brief_draft")
    assert "automation_v2_daily_report" not in oq.ALLOWED_TASK_TYPES


# ---- (5) no scheduler install/trigger --------------------------------------

def test_no_scheduler_install_or_trigger():
    sch = _Q["scheduler_safety"]
    for k in ("installs_scheduler", "triggers_scheduler",
              "modifies_windows_task_scheduler", "modifies_cron",
              "modifies_existing_scheduled_task", "starts_background_process",
              "starts_persistent_daemon", "auto_executes"):
        assert sch[k] is False, k
    assert sch["is_definition_only"] is True
    bad = {**_Q, "scheduler_safety": {**sch, "triggers_scheduler": True}}
    assert qa.validate_v2_report_only_queue(bad)["valid"] is False


# ---- (6) dispatch executes nothing; no data fetch; no git write ------------

def test_dispatch_defines_but_executes_nothing():
    disp = _Q["dispatch_definition"]
    assert disp["dispatchable"] is True
    assert disp["will_execute"] is False
    assert disp["executes_here"] is False
    assert disp["requires_human_or_scheduled_trigger"] is True
    # dispatch refuses an unregistered task
    refused = qa.resolve_dispatch({"task_id": "data_fetch_run",
                                   "task_class": "REPORT_ONLY"})
    assert refused["dispatchable"] is False
    assert refused["will_execute"] is False


def test_no_forbidden_source_tokens_in_adapter():
    src = Path(qa.__file__).read_text(encoding="utf-8")
    for tok in _FORBIDDEN_SOURCE_TOKENS:
        assert tok not in src, tok


# ---- (7) runner proven incapable; no C22 labels/replay; no promote/advance -

def test_runner_proven_incapable_no_labels_no_promote():
    proof = _Q["registration_safety_proof"]
    assert proof["all_dangerous_capabilities_disproven"] is True
    pic = proof["proven_incapable_of"]
    for k in ("fetch_data", "trade", "place_orders", "commit", "push",
              "advance_gate", "promote_candidate", "use_api"):
        assert pic[k] is True, k
    # explicit capability flags for labels/replay/promote/advance are False
    for flag in ("starts_c22_labels", "builds_replay", "auto_promotes_candidate",
                 "auto_advances_gate", "fetches_data", "performs_git_io"):
        assert _Q[flag] is False, flag


# ---- (8) C22 DATA_NOT_READY still recommends dataset staging only -----------

def test_c22_data_not_ready_staging_only():
    assert _Q["c22_data_not_ready"] is True
    assert _Q["recommends_dataset_staging_only"] is True
    assert _Q["next_human_approval_token"] == _STAGING_TOKEN
    proof = _Q["registration_safety_proof"]
    assert proof["recommended_gate_kind"] == "RECOMMEND_DATASET_STAGING"
    bad = {**_Q, "recommends_dataset_staging_only": False}
    assert qa.validate_v2_report_only_queue(bad)["valid"] is False


# ---- (9) Jarvis/morning report can surface the generated artifact path ------

def test_morning_report_surfaces_artifact_path():
    # the adapter exposes a gitignored artifact path pattern...
    pattern = qa.v2_report_artifact_path()
    assert pattern.startswith("reports/automation_v2_daily/")
    assert qa.v2_report_artifact_path("20260620T000000Z").endswith(
        "20260620T000000Z.md")
    # ...and the live morning report markdown already surfaces that artifact dir.
    report = mr.build_morning_report(
        {"run_time": "t", "tasks_attempted": [], "tasks_completed": [],
         "tasks_failed": [], "tasks_skipped": [], "errors": [],
         "integrity_status": "INTACT", "explicit_status": None},
        {"branch": "master", "staged": 0, "modified": 0, "untracked": 0,
         "clean": True},
        {})
    md = mr.render_markdown(report)
    assert "reports/automation_v2_daily" in md


# ---- (10) capability flags + scope locks all locked ------------------------

def test_capability_flags_and_scope_locks():
    for flag in qa._CAPABILITY_FLAGS_FALSE:
        assert _Q[flag] is False, flag
        bad = {**_Q, flag: True}
        assert qa.validate_v2_report_only_queue(bad)["valid"] is False, flag
    for key, val in _Q["scope_locks"].items():
        assert val is True, key
    dl = _Q["danger_locks"]
    for k in ("live_trading_locked", "paper_trading_locked", "signum_locked",
              "mcp_locked", "hyperliquid_locked", "scheduler_locked",
              "never_skips_human_gates"):
        assert dl[k] is True, k


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = Path(qa.__file__).read_text(encoding="utf-8")
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

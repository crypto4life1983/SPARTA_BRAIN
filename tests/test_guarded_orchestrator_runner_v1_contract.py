"""Tests for the Guarded Orchestrator Runner v1 (dry-run / planning) contract.

Verifies: research-only, dry-run / planning only, executes nothing; composes
Orchestrator v2 + the Commit Guard to either emit an APPROVED 7-phase dry-run plan
(safety precheck / expected-files allowlist / relevant tests / explicit-path staging /
commit / push-verify / final report) for a clean bounded research unit, or REFUSE for
every human-stop gate (new candidate / C19, advance/reject, fetch, labels->replay,
replay verdict, optimization/rescue, XAUUSD / new instrument class, scheduler,
credentials/private API, paper/live/broker/order/trading code), broad staging,
unexpected files, and un-exempted data/report artifacts; tolerates untracked clutter
only under explicit-path staging; pairs with both policy contracts; capability flags +
scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.guarded_orchestrator_runner_v1_contract as gor
import sparta_commander.autopilot_research_orchestrator_v2_contract as aro2


_C = gor.build_runner_contract()


def _clean_unit(**over):
    unit = {
        "category": "research_only_contract_or_test",
        "description": "build a pure contract + test",
        "expected_files": ["sparta_commander/x_contract.py", "tests/test_x.py"],
        "relevant_tests": ["tests/test_x.py"],
        "precheck": {"clean_working_tree": True, "head_equals_origin_master": True,
                     "no_mutating_shell_pending": True, "expected_files_only": True},
        "tests": {"ran": True, "passed": True},
        "staging_command": "git add sparta_commander/x_contract.py tests/test_x.py",
        "staged_files": ["sparta_commander/x_contract.py", "tests/test_x.py"],
        "exemptions": [],
        "commit_message_ref": "C:/tmp/x.txt",
        "untracked_clutter_present": True,
    }
    unit.update(over)
    return unit


# ---- contract is dry-run policy and validates ------------------------------

def test_contract_dry_run_only_and_validates():
    assert _C["mode"] == "RESEARCH_ONLY"
    assert _C["is_dry_run_only"] is True
    assert _C["is_pure_planning_only"] is True
    assert _C["is_live_runner"] is False
    assert _C["executes_anything"] is False
    assert gor.validate_runner_contract(_C)["valid"] is True


def test_contract_declares_seven_phases_and_pairing():
    assert _C["plans_seven_phases"] == [
        "safety_precheck", "expected_files_allowlist", "relevant_tests",
        "explicit_path_staging_plan", "commit_plan", "push_verification_plan",
        "final_report_requirements"]
    assert _C["pairs_with_orchestrator_v2"] == (
        "autopilot_research_orchestrator_v2_contract")
    assert _C["pairs_with_commit_guard"] == (
        "explicit_allowlist_commit_guard_v1_contract")
    assert _C["orchestrator_v2_valid"] is True
    assert _C["commit_guard_valid"] is True
    assert set(_C["refuses_categories"]) == set(aro2.HUMAN_STOP_CATEGORIES)


# ---- approve a clean bounded research unit ---------------------------------

def test_plan_ready_for_clean_unit():
    p = gor.plan_bounded_research_unit(_clean_unit())
    assert p["verdict"] == "PLAN_READY_DRY_RUN"
    assert p["plan_ready"] is True
    assert p["refused"] is False
    assert p["refusal_reasons"] == []
    assert p["executes_nothing"] is True
    assert p["is_dry_run_only"] is True


def test_plan_has_all_seven_phases():
    p = gor.plan_bounded_research_unit(_clean_unit())
    ep = p["execution_plan"]
    for phase in ("phase_1_safety_precheck", "phase_2_expected_files_allowlist",
                  "phase_3_relevant_tests", "phase_4_explicit_path_staging_plan",
                  "phase_5_commit_plan", "phase_6_push_verification_plan",
                  "phase_7_final_report_requirements"):
        assert phase in ep, phase
    # the test command is declared (string), not executed
    assert "pytest" in ep["phase_3_relevant_tests"]["command_to_run_by_hand"]
    assert ep["phase_4_explicit_path_staging_plan"]["explicit_path_only"] is True
    assert "HEAD == origin/master" in ep["phase_6_push_verification_plan"]["verify"]


def test_every_auto_continue_category_plans_when_clean():
    for cat in aro2.AUTO_CONTINUE_CATEGORIES:
        p = gor.plan_bounded_research_unit(_clean_unit(category=cat))
        assert p["verdict"] == "PLAN_READY_DRY_RUN", cat


# ---- refuse every human-stop category --------------------------------------

def test_refuse_every_human_stop_category():
    for cat in aro2.HUMAN_STOP_CATEGORIES:
        p = gor.plan_bounded_research_unit(_clean_unit(category=cat))
        assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN", cat
        assert p["refused"] is True
        assert p["refusal_reasons"]


def test_refuse_new_candidate_and_c19_and_advance_reject():
    for cat in ("start_new_candidate_c_number", "advance_vs_reject_decision",
                "replay_result_decision", "labels_to_replay_advance",
                "network_fetch_execution", "optimization_tuning_or_rescue_variant",
                "add_new_instrument_class",
                "paper_live_broker_order_or_trading_code",
                "scheduler_change_beyond_research_only_reporting",
                "credentials_env_secrets_account_api_or_private_broker_endpoint"):
        p = gor.plan_bounded_research_unit(_clean_unit(category=cat))
        assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN", cat


# ---- refuse staging hazards -------------------------------------------------

def test_refuse_broad_staging():
    p = gor.plan_bounded_research_unit(_clean_unit(staging_command="git add ."))
    assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN"
    assert p["broad_staging_detected"] is True
    assert any("broad_staging" in r for r in p["refusal_reasons"])


def test_refuse_unexpected_file_outside_allowlist():
    unit = _clean_unit(
        staged_files=["sparta_commander/x_contract.py", "tests/test_x.py",
                      "sparta_commander/surprise.py"])
    p = gor.plan_bounded_research_unit(unit)
    assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN"
    assert ("sparta_commander/surprise.py"
            in p["execution_plan"]["phase_4_explicit_path_staging_plan"]
            ["staged_outside_allowlist"])


def test_refuse_unexempted_data_or_report_artifact():
    for art in ("data/labels.csv", "reports/run.md", "x/result.json",
                "x/events.jsonl", "x/run.log"):
        unit = _clean_unit(
            expected_files=["sparta_commander/x_contract.py", art],
            staged_files=["sparta_commander/x_contract.py", art],
            staging_command="git add sparta_commander/x_contract.py %s" % art)
        p = gor.plan_bounded_research_unit(unit)
        assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN", art


def test_artifact_allowed_with_reviewed_contract_exemption():
    unit = _clean_unit(
        expected_files=["sparta_commander/x_contract.py", "data/frozen.json"],
        staged_files=["sparta_commander/x_contract.py", "data/frozen.json"],
        staging_command="git add sparta_commander/x_contract.py data/frozen.json",
        exemptions=[{"path": "data/frozen.json",
                     "reviewed_contract": "x_data_readiness_contract"}])
    p = gor.plan_bounded_research_unit(unit)
    assert p["verdict"] == "PLAN_READY_DRY_RUN"


def test_refuse_when_no_expected_files_declared():
    unit = _clean_unit(expected_files=[], staged_files=[])
    p = gor.plan_bounded_research_unit(unit)
    assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN"
    assert any("no_expected_files_declared" in r for r in p["refusal_reasons"])


def test_refuse_on_dirty_tracked_tree_and_sha_drift():
    u1 = _clean_unit()
    u1["precheck"]["clean_working_tree"] = False
    assert gor.plan_bounded_research_unit(u1)["verdict"] == "REFUSED_STOP_FOR_HUMAN"
    u2 = _clean_unit()
    u2["precheck"]["head_equals_origin_master"] = False
    assert gor.plan_bounded_research_unit(u2)["verdict"] == "REFUSED_STOP_FOR_HUMAN"


def test_refuse_on_failing_tests():
    unit = _clean_unit(tests={"ran": True, "passed": False})
    p = gor.plan_bounded_research_unit(unit)
    assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN"
    assert any("failing_tests" in r for r in p["refusal_reasons"])


# ---- clutter tolerated only under explicit-path staging --------------------

def test_clutter_tolerated_under_explicit_staging():
    # untracked clutter present + explicit per-path staging -> still plans
    p = gor.plan_bounded_research_unit(_clean_unit(untracked_clutter_present=True))
    assert p["verdict"] == "PLAN_READY_DRY_RUN"
    assert p["untracked_clutter_tolerated"] is True


def test_clutter_not_a_shield_for_broad_staging():
    # clutter present but broad staging -> refused (clutter does not excuse it)
    p = gor.plan_bounded_research_unit(
        _clean_unit(untracked_clutter_present=True, staging_command="git add -A"))
    assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN"


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in gor._CAPABILITY_FLAGS_FALSE:
        assert _C[flag] is False, flag
        bad = {**_C, flag: True}
        assert gor.validate_runner_contract(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _C["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_git", "no_shell", "no_run_tests", "no_stage",
                 "no_commit", "no_push", "no_file_deletion", "no_broad_staging",
                 "no_data_fetch", "no_optimization", "no_rescue_variant",
                 "no_new_candidate", "no_c19", "no_xauusd", "no_paper_trading",
                 "no_live_trading", "no_broker", "no_credentials", "no_private_api"):
        assert _C["scope_locks"][must] is True, must


def test_validator_rejects_tamper():
    bad = {**_C, "is_live_runner": True}
    assert gor.validate_runner_contract(bad)["valid"] is False
    bad2 = {**_C, "refuses_broad_staging": False}
    assert gor.validate_runner_contract(bad2)["valid"] is False
    bad3 = {**_C, "refuses_categories": list(aro2.HUMAN_STOP_CATEGORIES)[:-1]}
    assert gor.validate_runner_contract(bad3)["valid"] is False


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(gor.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random", "numpy", "pandas"}
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

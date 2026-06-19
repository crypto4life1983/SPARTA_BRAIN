"""Tests for the Guarded Orchestrator Executor v1 (authorization) contract.

Verifies: research-only, authorization-only, executes nothing, ships no real runner;
NOT a scheduler and never auto/overnight; DEFAULTS TO DRY-RUN; real execution requires
ALL of a separate explicit token + human authorization + a runner-approved plan + a
clean live precheck + green tests; re-derives the plan via the dry-run runner
(anti-tamper); authorizes only the 7 bounded phases; refuses the full human-stop set,
broad staging, unexpected files, un-exempted data/report artifacts, dirty tracked
tree, SHA drift, and failing/un-run tests; tolerates untracked clutter only under
explicit-allowlist staging; capability flags + scope locks; validator anti-tamper;
module purity."""
from __future__ import annotations

import ast

import sparta_commander.guarded_orchestrator_executor_v1_contract as goe
import sparta_commander.autopilot_research_orchestrator_v2_contract as aro2


_C = goe.build_executor_contract()


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


def _exec_request(**over):
    req = {
        "unit": _clean_unit(),
        "mode": "execute",
        "human_authorized": True,
        "execution_token": goe.EXECUTION_TOKEN,
    }
    req.update(over)
    return req


# ---- contract is authorization-only and validates --------------------------

def test_contract_authorization_only_and_validates():
    assert _C["mode"] == "RESEARCH_ONLY"
    assert _C["is_pure_authorization_only"] is True
    assert _C["is_scheduler"] is False
    assert _C["runs_automatically"] is False
    assert _C["runs_overnight"] is False
    assert _C["default_mode"] == "dry_run"
    assert _C["real_runner_shipped"] is False
    assert _C["tool_runner_disabled_by_default"] is True
    assert goe.validate_executor_contract(_C)["valid"] is True


def test_contract_declares_phases_gates_and_pairing():
    assert list(_C["allowed_execution_phases"]) == [
        "safety_precheck", "run_declared_tests",
        "explicit_path_git_add_allowlist_only", "git_commit_declared_message",
        "git_push_origin_master", "post_push_verification", "final_report"]
    for k in ("execution_requires_separate_token",
              "execution_requires_human_authorization",
              "execution_requires_runner_approved_plan",
              "execution_requires_clean_precheck_and_green_tests"):
        assert _C[k] is True, k
    assert _C["pairs_with_runner"] == "guarded_orchestrator_runner_v1_contract"
    assert _C["runner_valid"] is True
    assert set(_C["refuses_categories"]) == set(aro2.HUMAN_STOP_CATEGORIES)


# ---- default is dry-run -----------------------------------------------------

def test_default_mode_is_dry_run_when_unspecified():
    # no mode / no token / no authorization -> safe plan stays DRY-RUN, not executed
    d = goe.authorize_execution({"unit": _clean_unit()})
    assert d["decision"] == "DRY_RUN_PLAN_ONLY"
    assert d["is_dry_run"] is True
    assert d["authorized_to_execute"] is False
    assert "mode_is_dry_run_default" in d["dry_run_reasons"]
    assert d["executes_nothing"] is True


def test_safe_plan_without_token_stays_dry_run():
    d = goe.authorize_execution(_exec_request(execution_token=None))
    assert d["decision"] == "DRY_RUN_PLAN_ONLY"
    assert "missing_or_wrong_execution_token" in d["dry_run_reasons"]


def test_safe_plan_without_human_auth_stays_dry_run():
    d = goe.authorize_execution(_exec_request(human_authorized=False))
    assert d["decision"] == "DRY_RUN_PLAN_ONLY"
    assert "missing_human_authorization" in d["dry_run_reasons"]


def test_wrong_token_stays_dry_run():
    d = goe.authorize_execution(_exec_request(execution_token="NOT_THE_TOKEN"))
    assert d["decision"] == "DRY_RUN_PLAN_ONLY"
    assert d["execution_token_ok"] is False


# ---- the only path to authorized execution ---------------------------------

def test_authorized_to_execute_requires_all_conditions():
    d = goe.authorize_execution(_exec_request())
    assert d["decision"] == "AUTHORIZED_TO_EXECUTE"
    assert d["authorized_to_execute"] is True
    assert d["plan_approved_by_runner"] is True
    assert d["human_authorized"] is True
    assert d["execution_token_ok"] is True
    # the bounded command sequence maps to the 7 phases, in order
    phases = [c["phase"] for c in d["bounded_command_sequence"]]
    assert phases == list(goe.ALLOWED_EXECUTION_PHASES)


def test_authorized_command_sequence_is_explicit_and_bounded():
    d = goe.authorize_execution(_exec_request())
    seq = {c["phase"]: c["action"] for c in d["bounded_command_sequence"]}
    assert "git add sparta_commander/x_contract.py tests/test_x.py" == (
        seq["explicit_path_git_add_allowlist_only"])
    assert seq["git_push_origin_master"] == "git push origin master"
    assert "git commit -F" in seq["git_commit_declared_message"]
    assert "pytest" in seq["run_declared_tests"]


# ---- refuse every human-stop category even with full authorization ----------

def test_refuse_every_human_stop_category_even_when_authorized():
    for cat in aro2.HUMAN_STOP_CATEGORIES:
        d = goe.authorize_execution(_exec_request(unit=_clean_unit(category=cat)))
        assert d["decision"] == "REFUSED_STOP_FOR_HUMAN", cat
        assert d["refused"] is True
        assert d["refusal_reasons"]


def test_refuse_new_candidate_c19_advance_reject_fetch_trading():
    for cat in ("start_new_candidate_c_number", "advance_vs_reject_decision",
                "network_fetch_execution", "labels_to_replay_advance",
                "replay_result_decision", "optimization_tuning_or_rescue_variant",
                "add_new_instrument_class",
                "paper_live_broker_order_or_trading_code",
                "scheduler_change_beyond_research_only_reporting",
                "credentials_env_secrets_account_api_or_private_broker_endpoint"):
        d = goe.authorize_execution(_exec_request(unit=_clean_unit(category=cat)))
        assert d["decision"] == "REFUSED_STOP_FOR_HUMAN", cat


# ---- refuse staging + state hazards even with full authorization ------------

def test_refuse_broad_staging():
    d = goe.authorize_execution(
        _exec_request(unit=_clean_unit(staging_command="git add -A")))
    assert d["decision"] == "REFUSED_STOP_FOR_HUMAN"
    assert any("broad_staging" in r for r in d["refusal_reasons"])


def test_refuse_unexpected_file():
    unit = _clean_unit(
        staged_files=["sparta_commander/x_contract.py", "tests/test_x.py",
                      "sparta_commander/surprise.py"])
    d = goe.authorize_execution(_exec_request(unit=unit))
    assert d["decision"] == "REFUSED_STOP_FOR_HUMAN"


def test_refuse_data_or_report_artifact():
    for art in ("data/labels.csv", "reports/run.md", "x/result.json",
                "x/events.jsonl", "x/run.log"):
        unit = _clean_unit(
            expected_files=["sparta_commander/x_contract.py", art],
            staged_files=["sparta_commander/x_contract.py", art],
            staging_command="git add sparta_commander/x_contract.py %s" % art)
        d = goe.authorize_execution(_exec_request(unit=unit))
        assert d["decision"] == "REFUSED_STOP_FOR_HUMAN", art


def test_refuse_dirty_tree_and_sha_drift():
    u1 = _clean_unit()
    u1["precheck"]["clean_working_tree"] = False
    assert goe.authorize_execution(_exec_request(unit=u1))["decision"] == (
        "REFUSED_STOP_FOR_HUMAN")
    u2 = _clean_unit()
    u2["precheck"]["head_equals_origin_master"] = False
    assert goe.authorize_execution(_exec_request(unit=u2))["decision"] == (
        "REFUSED_STOP_FOR_HUMAN")


def test_refuse_failing_or_unrun_tests():
    u1 = _clean_unit(tests={"ran": True, "passed": False})
    assert goe.authorize_execution(_exec_request(unit=u1))["decision"] == (
        "REFUSED_STOP_FOR_HUMAN")
    u2 = _clean_unit(tests={"ran": False, "passed": False})
    assert goe.authorize_execution(_exec_request(unit=u2))["decision"] == (
        "REFUSED_STOP_FOR_HUMAN")


# ---- clutter tolerated only under explicit-allowlist staging ---------------

def test_clutter_tolerated_under_explicit_staging():
    d = goe.authorize_execution(
        _exec_request(unit=_clean_unit(untracked_clutter_present=True)))
    assert d["decision"] == "AUTHORIZED_TO_EXECUTE"
    assert d["untracked_clutter_tolerated_under_explicit_staging"] is True


def test_clutter_not_a_shield_for_broad_staging():
    unit = _clean_unit(untracked_clutter_present=True, staging_command="git add .")
    d = goe.authorize_execution(_exec_request(unit=unit))
    assert d["decision"] == "REFUSED_STOP_FOR_HUMAN"


# ---- anti-tamper: a hand-edited "approved" plan cannot smuggle past ---------

def test_executor_rederives_plan_so_passed_state_cannot_lie():
    # caller claims execute + token, but the UNIT itself is a forbidden category;
    # the executor re-runs the runner and refuses regardless of the request framing.
    d = goe.authorize_execution(_exec_request(
        unit=_clean_unit(category="paper_live_broker_order_or_trading_code")))
    assert d["decision"] == "REFUSED_STOP_FOR_HUMAN"


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in goe._CAPABILITY_FLAGS_FALSE:
        assert _C[flag] is False, flag
        bad = {**_C, flag: True}
        assert goe.validate_executor_contract(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _C["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_scheduler", "no_overnight", "no_git",
                 "no_run_tests", "no_push", "no_broad_staging", "no_data_fetch",
                 "no_optimization", "no_new_candidate", "no_c19", "no_xauusd",
                 "no_paper_trading", "no_live_trading", "no_broker",
                 "no_credentials", "no_private_api",
                 "no_execute_without_separate_token"):
        assert _C["scope_locks"][must] is True, must


def test_validator_rejects_tamper():
    for k in ("is_scheduler", "runs_overnight"):
        bad = {**_C, k: True}
        assert goe.validate_executor_contract(bad)["valid"] is False, k
    bad2 = {**_C, "default_mode": "execute"}
    assert goe.validate_executor_contract(bad2)["valid"] is False
    bad3 = {**_C, "real_runner_shipped": True}
    assert goe.validate_executor_contract(bad3)["valid"] is False
    bad4 = {**_C, "execution_requires_separate_token": False}
    assert goe.validate_executor_contract(bad4)["valid"] is False


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(goe.__file__, encoding="utf-8").read()
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

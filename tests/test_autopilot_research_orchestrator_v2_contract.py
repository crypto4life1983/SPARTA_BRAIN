"""Tests for the Autopilot Research Orchestrator v2 policy contract.

Verifies: research-only, pure policy (not a runner / scheduler / overnight
automation), executes nothing; declares the two closed lists (auto-continue vs
human-stop) with the blocklist-always-wins rule; the precheck/stop/pipeline
discipline (tests before commit, expected-files-only, no data artifacts); the
decision function AUTO_CONTINUEs only a clean bounded research step and STOPs on
every human-decision / forbidden gate, dirty tree, SHA drift, unexpected files,
staged data artifact, failing/un-run tests, and unclear gate; capability flags +
scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.autopilot_research_orchestrator_v2_contract as aro2


_C = aro2.build_orchestrator_contract()


def _clean_precheck() -> dict:
    return {"clean_working_tree": True, "head_equals_origin_master": True,
            "no_mutating_shell_pending": True, "expected_files_only": True}


def _green_tests() -> dict:
    return {"ran": True, "passed": True}


def _clean_diff() -> dict:
    return {"only_expected_files": True, "contains_data_artifact": False}


def _auto_step(category="research_only_contract_or_test") -> dict:
    return {"category": category, "precheck": _clean_precheck(),
            "tests": _green_tests(), "scoped_diff": _clean_diff(),
            "intends_commit": True, "intends_push": True}


# ---- contract is pure policy and validates ---------------------------------

def test_contract_pure_policy_and_validates():
    assert _C["mode"] == "RESEARCH_ONLY"
    assert _C["is_pure_policy_only"] is True
    assert _C["is_runner"] is False
    assert _C["installs_scheduler"] is False
    assert _C["runs_overnight_automation"] is False
    assert aro2.validate_orchestrator_contract(_C)["valid"] is True


def test_two_closed_lists_disjoint_and_complete():
    ac = set(_C["auto_continue_categories"])
    hs = set(_C["human_stop_categories"])
    assert ac == set(aro2.AUTO_CONTINUE_CATEGORIES)
    assert hs == set(aro2.HUMAN_STOP_CATEGORIES)
    assert ac & hs == set()
    assert _C["blocklist_always_wins"] is True
    # the named human-stop gates the user requires are all present
    for must in ("start_new_candidate_c_number", "advance_vs_reject_decision",
                 "replay_result_decision", "optimization_tuning_or_rescue_variant",
                 "add_new_instrument_class",
                 "paper_live_broker_order_or_trading_code",
                 "scheduler_change_beyond_research_only_reporting",
                 "credentials_env_secrets_account_api_or_private_broker_endpoint"):
        assert must in hs, must


def test_explicit_allowlist_staging_policy_declared():
    # V2 now pairs with the commit guard: explicit-allowlist staging + clutter
    # tolerance so a clean tracked tree can proceed amid unrelated untracked clutter.
    for k in ("requires_explicit_allowlist_staging", "forbids_broad_staging",
              "untracked_clutter_tolerated",
              "clean_tracked_tree_with_clutter_may_proceed"):
        assert _C[k] is True, k
    assert _C["pairs_with_commit_guard"] == (
        "explicit_allowlist_commit_guard_v1_contract")
    assert _C["scope_locks"]["no_broad_staging"] is True
    assert _C["scope_locks"]["no_git_add_dot"] is True
    bad = {**_C, "forbids_broad_staging": False}
    assert aro2.validate_orchestrator_contract(bad)["valid"] is False
    bad2 = {**_C, "pairs_with_commit_guard": None}
    assert aro2.validate_orchestrator_contract(bad2)["valid"] is False


def test_broad_staging_command_stops_even_when_clean():
    step = _auto_step()
    step["staging_command"] = "git add -A"
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "broad_staging_forbidden" in d["reasons"]
    assert d["broad_staging_detected"] is True


def test_explicit_path_staging_command_proceeds():
    step = _auto_step()
    step["staging_command"] = "git add sparta_commander/x.py tests/test_x.py"
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "AUTO_CONTINUE"
    assert d["broad_staging_detected"] is False


def test_untracked_clutter_present_does_not_block_clean_tracked_step():
    # clean tracked tree (precheck all True) + unrelated untracked clutter present
    step = _auto_step()
    step["precheck"]["untracked_clutter_present"] = True  # informational only
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "AUTO_CONTINUE"
    assert d["untracked_clutter_tolerated"] is True


def test_discipline_flags_declared():
    for k in ("tests_required_before_commit", "push_requires_pass_and_clean_diff",
              "commit_expected_files_only", "never_stages_data_artifacts",
              "does_not_weaken_human_gates", "one_compact_report_per_step"):
        assert _C[k] is True, k
    assert list(_C["safe_step_pipeline"]) == [
        "precheck", "build", "run_tests", "commit_expected_only",
        "push_after_pass_and_clean_diff", "report"]


# ---- decision function: AUTO_CONTINUE only a clean bounded research step -----

def test_auto_continue_clean_research_step():
    d = aro2.decide_orchestrator_step(_auto_step())
    assert d["verdict"] == "AUTO_CONTINUE"
    assert d["auto_continue"] is True
    assert d["reasons"] == []
    assert d["executes_nothing"] is True


def test_every_auto_continue_category_can_proceed_when_clean():
    for cat in aro2.AUTO_CONTINUE_CATEGORIES:
        d = aro2.decide_orchestrator_step(_auto_step(cat))
        assert d["verdict"] == "AUTO_CONTINUE", cat


# ---- decision function: STOP on every human-stop gate (blocklist wins) -------

def test_stop_on_every_human_stop_category():
    for cat in aro2.HUMAN_STOP_CATEGORIES:
        step = _auto_step(cat)  # otherwise perfectly clean
        d = aro2.decide_orchestrator_step(step)
        assert d["verdict"] == "STOP_FOR_HUMAN", cat
        assert d["stop_for_human"] is True
        assert d["blocklist_wins"] is True
        assert any("human_decision_or_forbidden_gate" in r for r in d["reasons"])


# ---- decision function: STOP on each hard stop condition --------------------

def test_stop_on_dirty_tree():
    step = _auto_step()
    step["precheck"]["clean_working_tree"] = False
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "dirty_tree" in d["reasons"]


def test_stop_on_sha_drift():
    step = _auto_step()
    step["precheck"]["head_equals_origin_master"] = False
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "sha_drift" in d["reasons"]


def test_stop_on_unexpected_files():
    step = _auto_step()
    step["precheck"]["expected_files_only"] = False
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "unexpected_files" in d["reasons"]


def test_stop_on_mutating_shell_pending():
    step = _auto_step()
    step["precheck"]["no_mutating_shell_pending"] = False
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "mutating_shell_pending" in d["reasons"]


def test_stop_on_staged_data_artifact():
    step = _auto_step()
    step["scoped_diff"]["contains_data_artifact"] = True
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "data_artifact_staged" in d["reasons"]


def test_stop_on_failing_tests():
    step = _auto_step()
    step["tests"] = {"ran": True, "passed": False}
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "failing_tests" in d["reasons"]


def test_stop_when_tests_not_run_before_commit():
    step = _auto_step()
    step["tests"] = {"ran": False, "passed": False}
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "tests_not_run_before_commit" in d["reasons"]


def test_stop_on_unclear_gate():
    step = _auto_step("some_unknown_category_not_in_either_list")
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "unclear_or_unrecognized_gate" in d["reasons"]


def test_blocklist_wins_even_if_step_looks_clean_and_passing():
    # a forbidden category with otherwise-perfect precheck/tests/diff still stops
    step = _auto_step("paper_live_broker_order_or_trading_code")
    d = aro2.decide_orchestrator_step(step)
    assert d["verdict"] == "STOP_FOR_HUMAN"


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in aro2._CAPABILITY_FLAGS_FALSE:
        assert _C[flag] is False, flag
        bad = {**_C, flag: True}
        assert aro2.validate_orchestrator_contract(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _C["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_git", "no_auto_commit", "no_auto_push",
                 "no_data_fetch", "no_scheduler_install", "no_overnight_automation",
                 "no_new_candidate", "no_advance_or_reject_decision",
                 "no_optimization_or_rescue_variant", "no_new_instrument_class",
                 "no_xauusd", "no_paper_trading", "no_live_trading",
                 "no_human_gate_weakening"):
        assert _C["scope_locks"][must] is True, must


def test_validator_rejects_list_tamper():
    bad = {**_C, "auto_continue_categories":
           list(aro2.AUTO_CONTINUE_CATEGORIES) + ["start_new_candidate_c_number"]}
    assert aro2.validate_orchestrator_contract(bad)["valid"] is False
    bad2 = {**_C, "blocklist_always_wins": False}
    assert aro2.validate_orchestrator_contract(bad2)["valid"] is False
    bad3 = {**_C, "does_not_weaken_human_gates": False}
    assert aro2.validate_orchestrator_contract(bad3)["valid"] is False


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(aro2.__file__, encoding="utf-8").read()
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

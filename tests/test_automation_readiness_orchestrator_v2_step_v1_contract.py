"""Tests for the Automation-Readiness Step (Orchestrator V2 + Allowlist Guard) v1.

Verifies: research-only, readiness-step-only, executes nothing; cross-checks the LIVE
state and confirms readiness only when NO active candidate, ledger 23, C18
rejected/closed, Orchestrator V2 + Commit Guard both live/valid/paired, explicit-
allowlist staging required, and untracked clutter tolerated; declares the future
guarded posture (auto-continue vs human-stop) and the explicit-allowlist staging
policy; starts no candidate / no C19, fetches no data, writes no trading code, and
touches no untracked clutter; capability flags + scope locks; validator anti-tamper;
module purity."""
from __future__ import annotations

import ast

import sparta_commander.automation_readiness_orchestrator_v2_step_v1_contract as ars
import sparta_commander.autopilot_research_orchestrator_v2_contract as aro2
import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as lane


_R = ars.build_automation_readiness_step()


def test_research_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_readiness_step_only"] is True
    assert _R["blockers"] == []
    assert _R["readiness_verdict"] == "READY_FOR_ORCHESTRATOR_V2_GUARDED_AUTOMATION"
    assert _R["is_ready"] is True
    assert ars.validate_automation_readiness_step(_R)["valid"] is True


def test_is_the_step_for_the_lane_token():
    assert _R["is_step_for"] == lane.AUTOMATION_READINESS_TOKEN
    assert _R["is_step_for"] == "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY"


def test_live_state_no_active_ledger_23_c18_rejected():
    assert _R["active_candidate"] is None
    assert _R["open_candidate_gate"] is False
    assert _R["rejected_ledger_count"] == 23
    assert _R["last_rejected_candidate"] == "C18"
    assert _R["last_rejected_candidate_verdict"] == "C18_REJECTED_AT_FEE_HONEST_REPLAY"
    assert _R["next_stage"] == "automation_readiness"


def test_all_readiness_checks_pass():
    for k, v in _R["readiness_checks"].items():
        assert v is True, k
    # tamper: any failed check -> not ready -> invalid
    bad_checks = {**_R["readiness_checks"], "no_active_candidate": False}
    bad = {**_R, "readiness_checks": bad_checks, "blockers": ["no_active_candidate"]}
    assert ars.validate_automation_readiness_step(bad)["valid"] is False


def test_certifies_orchestrator_v2_and_guard_live():
    assert _R["orchestrator_v2_valid"] is True
    assert _R["commit_guard_valid"] is True
    assert _R["orchestrator_v2_contract"] == (
        "autopilot_research_orchestrator_v2_contract")
    assert _R["commit_guard_contract"] == (
        "explicit_allowlist_commit_guard_v1_contract")
    assert _R["readiness_checks"]["guard_paired_with_orchestrator"] is True


def test_future_guarded_posture_declared():
    # mirrors the V2 closed lists exactly
    assert set(_R["future_auto_continue_categories"]) == set(
        aro2.AUTO_CONTINUE_CATEGORIES)
    assert set(_R["future_human_stop_categories"]) == set(
        aro2.HUMAN_STOP_CATEGORIES)
    assert _R[
        "future_automation_must_stop_for_real_decisions_and_forbidden_gates"] is True
    assert "explicit_per_path_git_add_only" in _R["future_staging_policy"]
    # the named human-stop gates the scope requires are all present
    for must in ("start_new_candidate_c_number", "advance_vs_reject_decision",
                 "network_fetch_execution", "labels_to_replay_advance",
                 "replay_result_decision", "optimization_tuning_or_rescue_variant",
                 "add_new_instrument_class",
                 "paper_live_broker_order_or_trading_code",
                 "scheduler_change_beyond_research_only_reporting",
                 "credentials_env_secrets_account_api_or_private_broker_endpoint"):
        assert must in _R["future_human_stop_categories"], must


def test_hard_guarantees_of_this_step():
    for k in ("starts_no_candidate", "starts_no_c19", "fetches_no_data",
              "optimizes_nothing", "creates_no_strategy_or_candidate_logic",
              "creates_no_trading_code", "touches_no_untracked_clutter",
              "uses_explicit_allowlist_staging_only"):
        assert _R[k] is True, k
        bad = {**_R, k: False}
        assert ars.validate_automation_readiness_step(bad)["valid"] is False, k


def test_next_action_is_human_direction_gate_no_c19():
    nra = ars.get_automation_readiness_next_action()
    assert nra == _R["next_required_action"]
    assert "NO_C19_STARTED" in nra
    assert "NO_ACTIVE_CANDIDATE" in nra
    for banned in ("START_C19", "FETCH", "OPTIMIZE", "PAPER", "LIVE", "BROKER",
                   "ORDER"):
        assert banned not in nra.upper().replace("NO_C19", ""), banned


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in ars._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert ars.validate_automation_readiness_step(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_git", "no_broad_staging", "no_data_fetch",
                 "no_optimization", "no_new_candidate", "no_c19",
                 "no_new_instrument_class", "no_xauusd", "no_paper_trading",
                 "no_live_trading", "no_clutter_deletion", "no_clutter_move",
                 "no_clutter_stash", "no_clutter_modification"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(ars.__file__, encoding="utf-8").read()
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

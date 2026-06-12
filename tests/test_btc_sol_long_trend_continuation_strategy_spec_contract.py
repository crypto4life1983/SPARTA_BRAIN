"""Tests for the Candidate #3 strategy spec contract
(BTC_SOL_LONG_TREND_CONTINUATION_V1).

Proves: a NEW family gated on both rejection records staying intact; only
the 3 frozen seeds as research inputs; BTC/SOL long-only; the 81 bps floor
and 27 bps fee model inherited and tamper-locked; WIDER-stop rule frozen;
pre-committed failure rules frozen; zero capability of any kind.
"""

from __future__ import annotations

import ast

import sparta_commander.btc_sol_long_trend_continuation_strategy_spec_contract as tc


def test_spec_ready_and_gated_on_intact_ledger():
    record = tc.build_candidate_3_spec()
    assert record["verdict"] == tc.VERDICT_TC_READY
    assert record["blockers"] == []
    assert tc.validate_candidate_3_spec(record)["valid"] is True
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    assert C1 == C2 == "REJECTED_KEPT_ON_RECORD"


def test_new_family_identity_and_seed_inputs():
    record = tc.build_candidate_3_spec()
    assert record["candidate_id"] == "BTC_SOL_LONG_TREND_CONTINUATION_V1"
    assert record["candidate_family"] == "long_biased_trend_continuation"
    assert record["frozen_seed_inputs"] == [
        "btc_was_net_positive_in_all_variants_small_sample",
        "sol_was_net_positive_at_3r_and_4r",
        "long_side_was_materially_stronger_than_shorts"]
    guarantees = record["non_rescue_guarantees"]
    for key in ("candidate_1_status_unchanged",
                "candidate_2_status_unchanged", "candidate_2_not_revived",
                "candidate_2_not_mutated",
                "seeds_are_research_inputs_for_new_family_only"):
        assert guarantees[key] is True, key
    assert "breakout" not in str(record["pullback_rules"]).lower()
    assert "breakout" not in str(record["resumption_entry"]).lower()
    assert "no range breakout requirement" in guarantees[
        "distinct_from_candidate_2"]
    assert "reviving_or_mutating_candidate_2" in tc.FORBIDDEN


def test_btc_sol_long_only():
    record = tc.build_candidate_3_spec()
    assert record["symbols"] == ["BTCUSD", "SOLUSD"]
    assert record["direction"] == "long_only"
    assert "short_setups" in tc.FORBIDDEN
    assert "symbols_outside_btc_sol" in tc.FORBIDDEN
    tampered = tc.build_candidate_3_spec()
    tampered["symbols"] = ["BTCUSD", "SOLUSD", "DOGEUSD"]
    assert tc.validate_candidate_3_spec(tampered)["valid"] is False
    tampered2 = tc.build_candidate_3_spec()
    tampered2["direction"] = "both"
    assert tc.validate_candidate_3_spec(tampered2)["valid"] is False


def test_cost_discipline_inherited_and_locked():
    from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
        MINIMUM_RISK_DISTANCE_BPS)
    assert MINIMUM_RISK_DISTANCE_BPS == 81
    record = tc.build_candidate_3_spec()
    cost = record["cost_discipline"]
    assert cost["minimum_risk_distance_bps"] == 81
    assert cost["assumed_round_trip_cost_bps"] == 27
    assert cost["maker_execution_assumed"] is False
    assert cost["floor_may_be_lowered"] is False
    assert "evaluate_setup_cost_viability" in cost[
        "checked_at_label_time_via"]
    assert "lowering_the_81bps_floor" in tc.FORBIDDEN
    assert "assuming_maker_execution" in tc.FORBIDDEN
    for field, value in (("minimum_risk_distance_bps", 54),
                         ("assumed_round_trip_cost_bps", 10),
                         ("maker_execution_assumed", True),
                         ("floor_may_be_lowered", True)):
        tampered = tc.build_candidate_3_spec()
        tampered["cost_discipline"][field] = value
        assert tc.validate_candidate_3_spec(tampered)["valid"] is False, field


def test_stop_and_entry_rules_frozen():
    record = tc.build_candidate_3_spec()
    assert record["stop_rules"]["selection"] == (
        "WIDER_of_structural_and_volatility_stop_always")
    assert record["stop_rules"]["never_tightened_after_entry"] is True
    assert record["resumption_entry"]["entry_price"] == (
        "close_of_the_resumption_bar")
    assert "NEXT 15m bar" in record["resumption_entry"]["anti_lookahead"]
    assert record["trend_qualification"]["both_required"] is True
    assert record["target_variants"] == ["2r", "3r", "4r"]
    tampered = tc.build_candidate_3_spec()
    tampered["stop_rules"]["selection"] = "tighter_of_the_two"
    assert tc.validate_candidate_3_spec(tampered)["valid"] is False


def test_pre_committed_failure_rules_frozen():
    record = tc.build_candidate_3_spec()
    rules = record["pre_committed_failure_rules"]
    assert len(rules) == 3
    assert any("REJECTED_KEPT_ON_RECORD" in rule for rule in rules)
    assert any("one authorized mutable filter-only edit" in rule
               for rule in rules)
    assert any("zero accepted labels" in rule for rule in rules)
    tampered = tc.build_candidate_3_spec()
    tampered["pre_committed_failure_rules"] = rules[:1]
    assert tc.validate_candidate_3_spec(tampered)["valid"] is False


def test_zero_capability_and_gates_locked():
    record = tc.build_candidate_3_spec()
    for key in ("executes", "writes_files", "labels_now",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "stages_data_now", "fetches_data", "calls_api",
                "uses_network", "uses_credentials", "uses_wallet",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "revives_candidate_2"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    assert "paper_or_live_capability" in tc.FORBIDDEN
    assert "profitability_claims" in tc.FORBIDDEN
    assert ("wallet_account_order_trading_api_key_capability"
            in tc.FORBIDDEN)
    tampered = tc.build_candidate_3_spec()
    tampered["live_gate_locked"] = False
    assert tc.validate_candidate_3_spec(tampered)["valid"] is False
    tampered2 = tc.build_candidate_3_spec()
    tampered2["claims_profitability"] = True
    assert tc.validate_candidate_3_spec(tampered2)["valid"] is False
    tampered3 = tc.build_candidate_3_spec()
    tampered3["forbidden"] = tampered3["forbidden"][:2]
    assert tc.validate_candidate_3_spec(tampered3)["valid"] is False


def test_deterministic_and_label_and_action():
    assert tc.build_candidate_3_spec() == tc.build_candidate_3_spec()
    assert tc.get_candidate_3_spec_label() == tc.TC_LABEL
    assert "READ-ONLY" in tc.TC_LABEL
    assert "NOT A RESCUE" in tc.TC_LABEL
    assert tc.TC_MODE == "RESEARCH_ONLY"
    assert tc.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_3_DETECTOR_SPEC_AND_DRY_RUN_PATH")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in tc.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_is_pure_rules_no_io_no_network():
    src = open(tc.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "pathlib", "os", "io", "json", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "hashlib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))

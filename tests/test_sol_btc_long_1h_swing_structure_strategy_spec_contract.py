"""Tests for the Candidate #4 strategy spec contract
(SOL_BTC_LONG_1H_SWING_STRUCTURE_V1).

Proves: a NEW family gated on ALL THREE rejection records staying intact;
only the 3 frozen seeds as research inputs; SOL/BTC long-only on 1h/4h;
the 81 bps floor and 27 bps fee model inherited and tamper-locked;
WIDER-stop rule frozen; pre-committed failure rules (one edit max)
frozen; zero capability."""

from __future__ import annotations

import ast

import sparta_commander.sol_btc_long_1h_swing_structure_strategy_spec_contract as c4


def test_spec_ready_and_gated_on_three_record_ledger():
    record = c4.build_candidate_4_spec()
    assert record["verdict"] == c4.VERDICT_C4_READY
    assert record["blockers"] == []
    assert c4.validate_candidate_4_spec(record)["valid"] is True
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    assert C1 == C2 == C3 == "REJECTED_KEPT_ON_RECORD"
    # determinism
    assert c4.build_candidate_4_spec() == record


def test_new_family_identity_seeds_and_thesis():
    record = c4.build_candidate_4_spec()
    assert record["candidate_id"] == "SOL_BTC_LONG_1H_SWING_STRUCTURE_V1"
    assert record["candidate_family"] == "long_1h_swing_structure"
    assert record["frozen_seed_inputs"] == [
        "btc_sol_long_side_strength_from_candidate_2",
        "sol_produced_7_of_9_accepted_labels_in_candidate_3_v1",
        "structural_stop_setups_with_healthy_92_to_151_bps_risk"
        "_geometry"]
    assert "one timeframe up" in record["thesis"]
    assert "81 bps floor" in record["thesis"]
    guarantees = record["non_rescue_guarantees"]
    for key in ("candidate_1_status_unchanged",
                "candidate_2_status_unchanged",
                "candidate_3_status_unchanged",
                "candidate_3_not_revived",
                "candidate_3_not_mutated_again",
                "seeds_are_research_inputs_for_new_family_only"):
        assert guarantees[key] is True, key
    assert "different timeframe" in guarantees["distinct_from_candidate_3"]
    assert "reviving_candidate_1_2_or_3" in c4.FORBIDDEN
    assert "mutating_candidate_3_again" in c4.FORBIDDEN


def test_sol_btc_long_only_1h_4h():
    record = c4.build_candidate_4_spec()
    assert record["symbols"] == ["SOLUSD", "BTCUSD"]
    assert record["direction"] == "long_only"
    assert record["execution_timeframe"] == "1h"
    assert record["trend_timeframe"] == "4h"
    assert "short_setups" in c4.FORBIDDEN
    assert "symbols_outside_sol_btc" in c4.FORBIDDEN
    for field, value in (("symbols", ["SOLUSD", "BTCUSD", "ETHUSD"]),
                         ("direction", "both"),
                         ("execution_timeframe", "15m"),
                         ("thesis", "anything")):
        tampered = c4.build_candidate_4_spec()
        tampered[field] = value
        assert c4.validate_candidate_4_spec(
            tampered)["valid"] is False, field


def test_structure_entry_and_stop_rules_frozen():
    record = c4.build_candidate_4_spec()
    swing = record["swing_structure_rules"]
    assert "strictly lower than" in swing["swing_low_definition"]
    assert "confirmed only 2 bars later" in swing["swing_low_definition"]
    assert "higher-low" in swing["setup"]
    assert swing["max_bars_between_swings"] == 48
    assert swing["max_bars_from_sl2_to_entry"] == 24
    entry = record["entry_rules"]
    assert entry["entry_price"] == "close_of_the_trigger_bar"
    assert "NEXT 1h bar" in entry["anti_lookahead"]
    assert "void" in entry["invalidation_before_entry"]
    assert entry["one_setup_per_swing_pair"] is True
    trend = record["trend_qualification"]
    assert trend["both_required"] is True
    assert "sma10" in trend["rule_1"]
    assert "3_bars_ago" in trend["rule_2"]
    stops = record["stop_rules"]
    assert stops["selection"] == (
        "WIDER_of_structural_and_volatility_stop_always")
    assert stops["never_tightened_after_entry"] is True
    assert record["target_variants"] == ["2r", "3r", "4r"]
    tampered = c4.build_candidate_4_spec()
    tampered["stop_rules"]["selection"] = "tighter_of_the_two"
    assert c4.validate_candidate_4_spec(tampered)["valid"] is False


def test_cost_discipline_inherited_and_locked():
    from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
        MINIMUM_RISK_DISTANCE_BPS)
    assert MINIMUM_RISK_DISTANCE_BPS == 81
    record = c4.build_candidate_4_spec()
    cost = record["cost_discipline"]
    assert cost["minimum_risk_distance_bps"] == 81
    assert cost["assumed_round_trip_cost_bps"] == 27
    assert cost["maker_execution_assumed"] is False
    assert cost["floor_may_be_lowered"] is False
    assert "evaluate_setup_cost_viability" in cost[
        "checked_at_label_time_via"]
    assert "lowering_the_81bps_floor" in c4.FORBIDDEN
    assert "assuming_maker_execution" in c4.FORBIDDEN
    for field, value in (("minimum_risk_distance_bps", 54),
                         ("assumed_round_trip_cost_bps", 10),
                         ("maker_execution_assumed", True),
                         ("floor_may_be_lowered", True)):
        tampered = c4.build_candidate_4_spec()
        tampered["cost_discipline"][field] = value
        assert c4.validate_candidate_4_spec(
            tampered)["valid"] is False, field


def test_pre_committed_failure_rules_one_edit_max():
    record = c4.build_candidate_4_spec()
    rules = record["pre_committed_failure_rules"]
    assert len(rules) == 5
    assert any("fewer than 10 accepted labels" in rule
               and "REJECTED_KEPT_ON_RECORD" in rule for rule in rules)
    assert any("net-negative in ALL" in rule
               and "filter-only" in rule for rule in rules)
    assert any("at most ONE mutable edit total" in rule for rule in rules)
    assert any("zero accepted labels" in rule
               and "valid honest" in rule for rule in rules)
    assert any("no profitability claim" in rule for rule in rules)
    tampered = c4.build_candidate_4_spec()
    tampered["pre_committed_failure_rules"] = rules[:2]
    assert c4.validate_candidate_4_spec(tampered)["valid"] is False


def test_zero_capability_and_gates_locked():
    record = c4.build_candidate_4_spec()
    for key in ("executes", "writes_files", "labels_now",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "stages_data_now", "fetches_data", "calls_api",
                "uses_network", "uses_credentials", "uses_wallet",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "revives_candidate_3"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for field, value in (("live_gate_locked", False),
                         ("claims_profitability", True),
                         ("revives_candidate_3", True),
                         ("forbidden", [])):
        tampered = c4.build_candidate_4_spec()
        tampered[field] = value
        assert c4.validate_candidate_4_spec(
            tampered)["valid"] is False, field


def test_label_action_and_module_purity():
    assert c4.get_candidate_4_spec_label() == c4.C4_LABEL
    assert "READ-ONLY" in c4.C4_LABEL
    assert "NOT A RESCUE" in c4.C4_LABEL
    assert c4.C4_MODE == "RESEARCH_ONLY"
    assert c4.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_4_DETECTOR_SPEC_AND_DRY_RUN_PATH")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c4.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c4.__file__, encoding="utf-8").read()
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

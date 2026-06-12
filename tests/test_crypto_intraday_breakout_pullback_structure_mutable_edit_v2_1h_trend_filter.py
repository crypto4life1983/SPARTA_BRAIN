"""Tests for the SPARTA Breakout-Pullback Mutable Edit V2 - 1h Trend Filter.

Proves V2 is gated on the frozen replay evidence, adds ONLY the 1h
trend-filter parameters (a filter that can never expand scope or weaken
entries), preserves the floor/costs/replay standards, keeps everything
locked, and records the fail-then-reject rule.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.crypto_intraday_breakout_pullback_structure_mutable_edit_v2_1h_trend_filter as bv2
from sparta_commander.crypto_intraday_breakout_pullback_structure_strategy_spec_contract import (
    build_candidate_asset_instance,
)

_FROZEN = "BP_REPLAY_RESULTS_FROZEN_CANDIDATE_REJECTED_AS_IS"


def test_v2_edit_ready_when_replay_evidence_frozen():
    record = bv2.record_bp_mutable_edit_v2(_FROZEN)
    assert record["verdict"] == bv2.VERDICT_BV2_READY
    assert record["blockers"] == []
    assert record["edited_asset_verdict"] == (
        "CANDIDATE_ASSET_ACCEPTED_FOR_RESEARCH")
    assert record["candidate_id"] == (
        "CRYPTO_INTRADAY_BREAKOUT_PULLBACK_STRUCTURE_V1")
    assert bv2.validate_bp_mutable_edit_v2(record)["valid"] is True


def test_v2_edit_blocked_without_frozen_evidence():
    for bad in (None, "BP_REPLAY_RESULTS_REVIEW_REJECTED",
                "BP_REPLAY_RESULTS_REVIEW_BLOCKED", "anything"):
        record = bv2.record_bp_mutable_edit_v2(bad)
        assert record["verdict"] == bv2.VERDICT_BV2_BLOCKED, bad
        assert "replay_evidence_not_frozen" in record["blockers"]
        assert record["edited_asset"] is None


def test_real_repo_build_gates_on_live_frozen_evidence():
    if not os.path.isfile("C:/SPARTA_BRAIN/data/breakout_pullback/"
                          "replay_results/bp_replay_results_2026-05-12"
                          "_2026-06-10.jsonl"):
        pytest.skip("real replay evidence absent on this machine")
    record = bv2.build_bp_mutable_edit_v2("C:/SPARTA_BRAIN")
    assert record["verdict"] == bv2.VERDICT_BV2_READY
    assert bv2.validate_bp_mutable_edit_v2(record)["valid"] is True


def test_only_the_1h_trend_filter_parameters_added():
    assert bv2.V2_NEW_PARAMETERS == {
        "htf_trend_filter_enabled": True,
        "htf_trend_timeframe": "1h",
        "htf_trend_sma_period": 20,
        "htf_trend_rule_long": "1h_close_above_1h_sma20_at_breakout_time",
        "htf_trend_rule_short": "1h_close_below_1h_sma20_at_breakout_time",
        "filter_only_trade_count_must_reduce_or_equal": True}
    base = build_candidate_asset_instance()
    edited = bv2.build_edited_candidate_asset_bv2()
    # base builder output is NOT mutated
    assert "htf_trend_filter_enabled" not in base["fields"]["parameters"]
    # outer research flags identical
    for key in ("research_only", "live_trading_authorized",
                "paper_trading_authorized", "human_review_required",
                "optimizer_may_edit", "locked_instructions_may_edit",
                "locked_scorer_may_edit"):
        assert edited[key] == base[key], key
    changed = {name for name in base["fields"]
               if edited["fields"][name] != base["fields"][name]}
    assert changed == {"parameters", "constraints", "lineage", "status",
                       "audit_notes", "rationale"}
    # entry/exit/risk rule TEXT untouched -- nothing weakened
    assert edited["fields"]["entry_rules_text"] == (
        base["fields"]["entry_rules_text"])
    assert edited["fields"]["exit_rules_text"] == (
        base["fields"]["exit_rules_text"])
    assert edited["fields"]["risk_rules_text"] == (
        base["fields"]["risk_rules_text"])
    # all base parameters preserved (floor and costs included)
    for key, value in base["fields"]["parameters"].items():
        assert edited["fields"]["parameters"][key] == value, key
    assert edited["fields"]["parameters"]["minimum_risk_distance_bps"] == 81
    assert edited["fields"]["parameters"]["round_trip_cost_bps"] == 27


def test_filter_only_never_expands_scope():
    record = bv2.record_bp_mutable_edit_v2(_FROZEN)
    assert record["filter_only_never_expands_scope"] is True
    assert record["entry_rules_weakened"] is False
    assert ("never add or weaken" in bv2.V2_TREND_FILTER_RULE)
    assert "weakening_entry_rules" in bv2.FORBIDDEN
    assert "expanding_trade_scope" in bv2.FORBIDDEN
    parameters = bv2.build_edited_candidate_asset_bv2()["fields"]["parameters"]
    assert parameters["filter_only_trade_count_must_reduce_or_equal"] is True
    tampered = bv2.record_bp_mutable_edit_v2(_FROZEN)
    tampered["filter_only_never_expands_scope"] = False
    assert bv2.validate_bp_mutable_edit_v2(tampered)["valid"] is False
    tampered2 = bv2.record_bp_mutable_edit_v2(_FROZEN)
    tampered2["entry_rules_weakened"] = True
    assert bv2.validate_bp_mutable_edit_v2(tampered2)["valid"] is False


def test_floor_costs_and_replay_standards_preserved():
    record = bv2.record_bp_mutable_edit_v2(_FROZEN)
    assert record["cost_floor_lowered"] is False
    assert record["maker_execution_assumed"] is False
    for guarantee in ("81bps_floor_unchanged_27bps_costs_unchanged",
                      "anti_lookahead_and_conservative_replay_standards"
                      "_unchanged",
                      "breakout_pullback_continuation_rules_unchanged_no"
                      "_loosening",
                      "locked_scorer_unchanged",
                      "locked_instructions_unchanged",
                      "no_maker_execution_assumption"):
        assert guarantee in record["unchanged_guarantees"], guarantee
    tampered = bv2.record_bp_mutable_edit_v2(_FROZEN)
    tampered["edited_asset"]["fields"]["parameters"][
        "minimum_risk_distance_bps"] = 10
    assert bv2.validate_bp_mutable_edit_v2(tampered)["valid"] is False
    tampered2 = bv2.record_bp_mutable_edit_v2(_FROZEN)
    tampered2["cost_floor_lowered"] = True
    assert bv2.validate_bp_mutable_edit_v2(tampered2)["valid"] is False


def test_locked_machinery_and_schema_unchanged():
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        FORBIDDEN_FOREVER, LOCKED_HUMAN_INSTRUCTIONS, LOCKED_SCORING_RULES)
    assert len(LOCKED_HUMAN_INSTRUCTIONS) == 7
    assert len(LOCKED_SCORING_RULES) == 9
    assert len(FORBIDDEN_FOREVER) == 12
    from sparta_commander.crypto_intraday_breakout_pullback_structure_detector_spec import (
        BP_DETECTOR_STATUSES, BP_LABEL_REQUIRED_FIELDS)
    assert len(BP_LABEL_REQUIRED_FIELDS) == 38
    assert len(BP_DETECTOR_STATUSES) == 10
    record = bv2.record_bp_mutable_edit_v2(_FROZEN)
    for key in ("modifies_locked_scorer", "modifies_locked_instructions",
                "modifies_detector_label_schema",
                "modifies_staged_candles", "modifies_previous_labels"):
        assert record[key] is False, key


def test_credential_order_live_fields_reject():
    from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
        validate_candidate_asset)
    for bad in ("api_key_env", "order_endpoint", "wallet_address",
                "broker_account", "login_token"):
        smuggled = bv2.build_edited_candidate_asset_bv2()
        smuggled["fields"] = dict(smuggled["fields"], **{bad: "x"})
        assert validate_candidate_asset(smuggled)["verdict"] == (
            "CANDIDATE_ASSET_REJECTED"), bad
    flipped = bv2.build_edited_candidate_asset_bv2()
    flipped["live_trading_authorized"] = True
    assert validate_candidate_asset(flipped)["verdict"] == (
        "CANDIDATE_ASSET_REJECTED")


def test_nothing_runs_and_failure_rule_recorded():
    record = bv2.record_bp_mutable_edit_v2(_FROZEN)
    for key in ("executes", "writes_files", "writes_reports",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    assert record["one_experiment_only"] is True
    assert record["redetection_requires_separate_human_approval"] is True
    assert record["replay_requires_separate_human_approval"] is True
    assert "rejected and kept on record" in record["failure_rule"]
    src = open(bv2.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for tool in ("detection_once", "replay_105_once"):
        assert tool not in src, tool
    tampered = bv2.record_bp_mutable_edit_v2(_FROZEN)
    tampered["failure_rule"] = "keep trying"
    assert bv2.validate_bp_mutable_edit_v2(tampered)["valid"] is False
    tampered2 = bv2.record_bp_mutable_edit_v2(_FROZEN)
    tampered2["live_gate_locked"] = False
    assert bv2.validate_bp_mutable_edit_v2(tampered2)["valid"] is False


def test_deterministic_and_validator_strict():
    assert (bv2.record_bp_mutable_edit_v2(_FROZEN)
            == bv2.record_bp_mutable_edit_v2(_FROZEN))
    tampered = bv2.record_bp_mutable_edit_v2(_FROZEN)
    tampered["v2_new_parameters"] = dict(tampered["v2_new_parameters"],
                                         htf_trend_sma_period=2)
    assert bv2.validate_bp_mutable_edit_v2(tampered)["valid"] is False
    tampered2 = bv2.record_bp_mutable_edit_v2(_FROZEN)
    tampered2["forbidden"] = tampered2["forbidden"][:3]
    assert bv2.validate_bp_mutable_edit_v2(tampered2)["valid"] is False
    tampered3 = bv2.record_bp_mutable_edit_v2(_FROZEN)
    tampered3["v2_trend_filter_rule"] = "whatever"
    assert bv2.validate_bp_mutable_edit_v2(tampered3)["valid"] is False


def test_prior_candidates_preserved_and_upstream_untouched():
    record = bv2.record_bp_mutable_edit_v2(_FROZEN)
    assert record["prior_evidence_kept_on_record"] is True
    assert ("candidate_1_and_candidate_2_evidence_kept_on_record"
            in record["unchanged_guarantees"])
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS)
    assert REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    import sparta_commander.crypto_intraday_breakout_pullback_structure_replay_results_review_contract as r2
    assert r2.VERDICT_BPR2_FROZEN == _FROZEN
    assert r2.EXPECTED_VARIANTS["2r"][4] == -55.607231
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_and_imports_clean():
    assert bv2.get_bp_mutable_edit_v2_label() == bv2.BV2_LABEL
    assert "READ-ONLY" in bv2.BV2_LABEL and bv2.BV2_MODE == "RESEARCH_ONLY"
    assert bv2.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_BP_V2_REDETECTION_WITH_1H_TREND_FILTER")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in bv2.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(bv2.__file__, encoding="utf-8").read()
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json",
                   "shutil", "databento", "ssl", "ftplib", "datetime",
                   "hashlib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))
"""Tests for the SPARTA Crypto Intraday Breakout-Pullback-Structure
Strategy Spec (Candidate #2).

Proves the spec is gated on the pushed family decision, never revives the
rejected FVG/CHOCH candidate, defines deterministic breakout/retest/
continuation/stop/target/rejection rules, enforces the 81 bps floor before
replay eligibility via the pushed cost filter, keeps the 27/3x/81 fee
discipline with no maker assumption, builds no detector/replay/scorer, and
keeps all gates LOCKED.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.crypto_intraday_breakout_pullback_structure_strategy_spec_contract as bp

_RECORDED = (
    "NEXT_CANDIDATE_FAMILY_DECISION_RECORDED_BREAKOUT_PULLBACK_STRUCTURE")


def _conditions(**overrides):
    conditions = {
        "breakout_present": True, "retest_present": True,
        "continuation_confirmed": True,
        "breakout_failed": False, "ambiguous": False,
        "insufficient_candles": False,
        "proposed_entry_price": 100.0,
        "proposed_stop_price": 99.0,  # 100 bps risk distance
    }
    conditions.update(overrides)
    return conditions


def test_spec_ready_when_family_decision_recorded():
    spec = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    assert spec["verdict"] == bp.VERDICT_BP_READY
    assert spec["blockers"] == []
    assert bp.validate_breakout_pullback_strategy_spec(spec)["valid"] is True


def test_spec_blocked_without_recorded_family_decision():
    for bad in (None, "NEXT_CANDIDATE_FAMILY_DECISION_REJECTED",
                "NEXT_CANDIDATE_FAMILY_DECISION_BLOCKED", "anything"):
        spec = bp.record_breakout_pullback_strategy_spec(bad)
        assert spec["verdict"] == bp.VERDICT_BP_BLOCKED, bad
        assert "next_family_decision_not_recorded" in spec["blockers"]


def test_real_repo_build_gates_on_live_family_decision():
    if not os.path.isfile("C:/SPARTA_BRAIN/data/ny_fvg_choch/"
                          "detector_labels/v3_structural_stop_eligibility"
                          "_2026-05-12_2026-06-10.json"):
        pytest.skip("real rejection evidence absent on this machine")
    spec = bp.build_breakout_pullback_strategy_spec("C:/SPARTA_BRAIN")
    assert spec["verdict"] == bp.VERDICT_BP_READY
    assert bp.validate_breakout_pullback_strategy_spec(spec)["valid"] is True


def test_candidate_identity_matches_selected_family():
    spec = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    assert spec["candidate_id"] == (
        "CRYPTO_INTRADAY_BREAKOUT_PULLBACK_STRUCTURE_V1")
    assert spec["candidate_family"] == "intraday_breakout_pullback_structure"
    assert spec["research_only"] is True
    assert spec["live_trading_authorized"] is False
    assert spec["paper_trading_authorized"] is False
    assert spec["human_review_required"] is True
    asset = bp.build_candidate_asset_instance()
    assert asset["fields"]["candidate_id"] == spec["candidate_id"]
    assert asset["fields"]["candidate_family"] == spec["candidate_family"]


def test_rejected_fvg_choch_candidate_not_revived():
    spec = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    assert spec["rejected_predecessor"] == (
        "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1")
    assert spec["candidate_id"] != spec["rejected_predecessor"]
    assert spec["predecessor_revived"] is False
    assert "fvg_choch" not in spec["candidate_family"]
    assert "reviving_ny_fvg_choch_candidate_1" in bp.FORBIDDEN
    assert "deleting_or_hiding_rejected_evidence" in bp.FORBIDDEN
    tampered = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    tampered["candidate_id"] = "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1"
    assert bp.validate_breakout_pullback_strategy_spec(tampered)[
        "valid"] is False
    tampered2 = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    tampered2["predecessor_revived"] = True
    assert bp.validate_breakout_pullback_strategy_spec(tampered2)[
        "valid"] is False
    # candidate #1's rejection record remains intact in the pushed module
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_REASON, REJECTION_STATUS)
    assert REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    assert REJECTION_REASON == "COST_NON_VIABLE_RISK_GEOMETRY"


def test_deterministic_rules_exist_for_every_concept():
    rules = bp.DETERMINISTIC_RULES
    for key in ("range_definition", "breakout_definition",
                "pullback_retest", "breakout_failure",
                "continuation_confirmation", "entry_rule", "stop_rule",
                "target_rule", "cost_viability"):
        assert key in rules and len(rules[key]) > 20, key
    assert "20 completed 15m bars" in rules["range_definition"]
    assert "10 bps" in rules["breakout_definition"]
    assert "50%" in rules["breakout_definition"]
    assert "15 bps" in rules["pullback_retest"]
    assert "61.8%" in rules["pullback_retest"]
    assert "25%" in rules["breakout_failure"]
    assert "higher low" in rules["continuation_confirmation"]
    assert "1.5 x ATR(14, 15m)" in rules["stop_rule"]
    assert "WIDER" in rules["stop_rule"]
    assert ">= 81 bps" in rules["stop_rule"]
    assert "2R, 3R, or 4R" in rules["target_rule"]
    assert "never order placement" in rules["target_rule"]
    assert bp.TARGET_R_OPTIONS == (2.0, 3.0, 4.0)
    for rule in ("no_breakout", "failed_retest",
                 "missing_continuation_confirmation",
                 "risk_distance_below_81_bps", "ambiguous_structure",
                 "insufficient_candles",
                 "any_live_paper_order_api_credential_field"):
        assert rule in bp.REJECTION_RULES, rule


def test_no_1m_scalp_geometry():
    spec = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    assert spec["context_timeframes"] == ["1h", "15m"]
    assert spec["trigger_timeframe"] == "15m"
    assert spec["no_1m_scalp_entry_geometry"] is True
    assert "no tiny 1m trigger" in spec["evaluation_window"]
    asset = bp.build_candidate_asset_instance()
    assert asset["fields"]["timeframe_scope"] == (
        "1h_15m_context_15m_trigger_no_1m_scalp")
    tampered = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    tampered["no_1m_scalp_entry_geometry"] = False
    assert bp.validate_breakout_pullback_strategy_spec(tampered)[
        "valid"] is False


def test_complete_setup_with_wide_risk_passes():
    result = bp.evaluate_setup_completeness(_conditions())
    assert result["verdict"] == bp.VERDICT_SETUP_COMPLETE
    assert result["rejection_reasons"] == []
    assert result["risk_distance_bps"] == 100.0
    assert result["completeness_authorizes_nothing"] is True


def test_missing_components_reject():
    no_breakout = bp.evaluate_setup_completeness(
        _conditions(breakout_present=False))
    assert no_breakout["verdict"] == bp.VERDICT_SETUP_REJECTED
    assert "no_breakout" in no_breakout["rejection_reasons"]
    no_retest = bp.evaluate_setup_completeness(
        _conditions(retest_present=False))
    assert "failed_retest" in no_retest["rejection_reasons"]
    failed = bp.evaluate_setup_completeness(
        _conditions(breakout_failed=True))
    assert "failed_retest" in failed["rejection_reasons"]
    no_cont = bp.evaluate_setup_completeness(
        _conditions(continuation_confirmed=False))
    assert ("missing_continuation_confirmation"
            in no_cont["rejection_reasons"])
    ambiguous = bp.evaluate_setup_completeness(_conditions(ambiguous=True))
    assert "ambiguous_structure" in ambiguous["rejection_reasons"]
    short_data = bp.evaluate_setup_completeness(
        _conditions(insufficient_candles=True))
    assert "insufficient_candles" in short_data["rejection_reasons"]
    assert bp.evaluate_setup_completeness(None)["verdict"] == (
        bp.VERDICT_SETUP_REJECTED)


def test_risk_distance_below_81_bps_rejects():
    tight = bp.evaluate_setup_completeness(
        _conditions(proposed_stop_price=99.50))  # 50 bps
    assert tight["verdict"] == bp.VERDICT_SETUP_REJECTED
    assert "risk_distance_below_81_bps" in tight["rejection_reasons"]
    assert tight["risk_distance_bps"] == 50.0
    edge = bp.evaluate_setup_completeness(
        _conditions(proposed_stop_price=99.19))  # exactly 81 bps
    assert edge["verdict"] == bp.VERDICT_SETUP_COMPLETE
    missing_prices = bp.evaluate_setup_completeness(
        _conditions(proposed_entry_price=None))
    assert ("risk_distance_below_81_bps"
            in missing_prices["rejection_reasons"])
    # the gate is the PUSHED V2 cost filter, not a local copy
    from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
        MINIMUM_RISK_DISTANCE_BPS)
    assert MINIMUM_RISK_DISTANCE_BPS == bp.MINIMUM_RISK_DISTANCE_BPS == 81


def test_fee_discipline_27_3x_81_no_maker_no_lowering():
    spec = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    assert spec["cost_viability"] == {
        "round_trip_cost_bps": 27,
        "minimum_risk_to_round_trip_cost_multiple": 3,
        "minimum_risk_distance_bps": 81,
        "reject_cost_dominated_setups": True}
    assert spec["maker_execution_assumed"] is False
    assert spec["cost_floor_lowered"] is False
    assert "maker_execution_assumptions" in bp.FORBIDDEN
    assert "lowering_the_81_bps_floor" in bp.FORBIDDEN
    parameters = bp.build_candidate_asset_instance()["fields"]["parameters"]
    assert parameters["round_trip_cost_bps"] == 27
    assert parameters["minimum_risk_distance_bps"] == 81
    assert parameters["reject_cost_dominated_setups"] is True
    for flag, value in (("maker_execution_assumed", True),
                        ("cost_floor_lowered", True)):
        tampered = bp.record_breakout_pullback_strategy_spec(_RECORDED)
        tampered[flag] = value
        assert bp.validate_breakout_pullback_strategy_spec(tampered)[
            "valid"] is False, flag
    tampered2 = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    tampered2["cost_viability"] = dict(tampered2["cost_viability"],
                                       minimum_risk_distance_bps=10)
    assert bp.validate_breakout_pullback_strategy_spec(tampered2)[
        "valid"] is False


def test_live_paper_order_api_credential_fields_reject():
    leak = bp.evaluate_setup_completeness(_conditions(order_id="x"))
    assert leak["verdict"] == bp.VERDICT_SETUP_REJECTED
    assert any(r.startswith("any_live_paper_order_api_credential_field")
               for r in leak["rejection_reasons"])
    for bad in ("api_key_env", "live_authorized", "paper_flag",
                "wallet_address", "broker_account"):
        leak2 = bp.evaluate_setup_completeness(_conditions(**{bad: "x"}))
        assert leak2["verdict"] == bp.VERDICT_SETUP_REJECTED, bad
    from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
        validate_candidate_asset)
    asset = bp.build_candidate_asset_instance()
    assert validate_candidate_asset(asset)["verdict"] == (
        "CANDIDATE_ASSET_ACCEPTED_FOR_RESEARCH")
    smuggled = bp.build_candidate_asset_instance()
    smuggled["fields"] = dict(smuggled["fields"], api_key_env="X")
    assert validate_candidate_asset(smuggled)["verdict"] == (
        "CANDIDATE_ASSET_REJECTED")
    flipped = bp.build_candidate_asset_instance()
    flipped["live_trading_authorized"] = True
    assert validate_candidate_asset(flipped)["verdict"] == (
        "CANDIDATE_ASSET_REJECTED")


def test_detector_replay_scorer_optimizer_not_built():
    spec = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    for key in ("runs_detector_now", "runs_replay_now", "scores_now",
                "executes", "writes_files", "writes_reports",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        assert spec[key] is False, key
    assert spec["paper_trading_gate_locked"] is True
    assert spec["micro_live_gate_locked"] is True
    assert spec["live_gate_locked"] is True
    src = open(bp.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for tool in ("detector_run_once", "redetection_run_once",
                 "replay_7_accepted_once",
                 "redetection_v3_structural_stop_once"):
        assert tool not in src, tool
    tampered = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    tampered["live_gate_locked"] = False
    assert bp.validate_breakout_pullback_strategy_spec(tampered)[
        "valid"] is False
    tampered2 = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    tampered2["forbidden"] = tampered2["forbidden"][:3]
    assert bp.validate_breakout_pullback_strategy_spec(tampered2)[
        "valid"] is False
    tampered3 = bp.record_breakout_pullback_strategy_spec(_RECORDED)
    tampered3["deterministic_rules"] = {"vibes": "only"}
    assert bp.validate_breakout_pullback_strategy_spec(tampered3)[
        "valid"] is False


def test_deterministic_and_upstream_untouched():
    assert (bp.record_breakout_pullback_strategy_spec(_RECORDED)
            == bp.record_breakout_pullback_strategy_spec(_RECORDED))
    import sparta_commander.next_candidate_family_decision_contract as nf
    assert nf.NEXT_FAMILY_ID == bp.CANDIDATE_ID
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        build_optimizer_contract)
    assert build_optimizer_contract()["verdict"] == (
        "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY")
    from sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec import (
        ALLOWED_EDITABLE_FIELDS)
    assert len(ALLOWED_EDITABLE_FIELDS) == 16
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_and_imports_clean():
    assert bp.get_breakout_pullback_strategy_spec_label() == bp.BP_LABEL
    assert "READ-ONLY" in bp.BP_LABEL and bp.BP_MODE == "RESEARCH_ONLY"
    assert bp.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_BREAKOUT_PULLBACK_DETECTOR_SPEC")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in bp.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(bp.__file__, encoding="utf-8").read()
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    sparta_imports = {node.module for node in ast.walk(tree)
                      if isinstance(node, ast.ImportFrom) and node.module
                      and node.module.startswith("sparta_commander")}
    for module in sparta_imports:
        for fragment in ("replay_runner", "replay_spec", "optimizer",
                         "detector_spec"):
            assert fragment not in module, module
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
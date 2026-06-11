"""Tests for the SPARTA NY-Session FVG+CHOCH Detector/Labeler Spec."""

from __future__ import annotations

import ast

import sparta_commander.crypto_d1_auto_research_mutable_candidate_asset_spec as ca
import sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract as op
import sparta_commander.ny_session_fvg_choch_detector_spec as dt


def _observation(**overrides):
    obs = {
        "setup_id": "setup_20260611_btc_001", "symbol": "BTC",
        "session_date": "2026-06-11", "direction": "long",
        "session_window": "09:30-12:00",
        "htf_fvg_present": True, "context_present": True,
        "choch_present": True, "ltf_fvg_present": True,
        "fib_alignment_pass": True, "htf_invalidated": False,
        "ambiguous": False,
        "htf_fvg_bounds": (63000.0, 63250.0), "htf_fvg_midpoint": 63125.0,
        "htf_fvg_type": "bullish", "htf_context_reason": "prior swing low",
        "liquidity_inflection_reference": "15m swing low 62800",
        "support_resistance_flip_reference": "63000 flip held",
        "previous_high_low_retest_reference": "prev session low retest",
        "choch_time": "2026-06-11T14:42:00Z", "choch_direction": "long",
        "choch_pivot_reference": "lower-high pivot 63180",
        "ltf_fvg_bounds": (63100.0, 63140.0), "ltf_fvg_midpoint": 63120.0,
        "fib_0618_zone": (63110.0, 63135.0),
        "proposed_entry_price": 63120.0, "proposed_stop_price": 63060.0,
        "proposed_target_4r_price": 63360.0,
        "breakeven_structure_trigger_reference": "new 1m higher-low pivot",
    }
    obs.update(overrides)
    return obs


def test_detector_spec_ready_and_gated():
    s = dt.build_ny_fvg_choch_detector_spec()
    assert s["verdict"] == dt.VERDICT_DET_READY
    assert s["blockers"] == []
    assert s["candidate_id"] == "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1"
    assert s["htf_timeframe"] == "15m" and s["ltf_timeframe"] == "1m"
    assert s["next_required_action"] == "HUMAN_APPROVED_FVG_CHOCH_REPLAY_SPEC"
    assert dt.validate_ny_fvg_choch_detector_spec(s)["valid"] is True


def test_status_set_is_closed_nine():
    assert len(dt.DETECTOR_STATUSES) == 9
    assert dt.DETECTOR_STATUSES[0] == "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW"
    assert "SETUP_REJECTED_FORBIDDEN_CAPABILITY" in dt.DETECTOR_STATUSES
    s = dt.build_ny_fvg_choch_detector_spec()
    s["detector_statuses"].append("SETUP_AUTO_TRADED")
    assert dt.validate_ny_fvg_choch_detector_spec(s)["valid"] is False


def test_accepted_label_has_all_required_fields():
    label = dt.label_setup(_observation())
    assert label["detector_status"] == "SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW"
    assert label["label_authorizes_nothing"] is True
    for field in dt.LABEL_REQUIRED_FIELDS:
        assert field in label, field
    assert label["candidate_id"] == dt.CANDIDATE_ID
    assert label["fib_alignment_pass"] is True
    assert label["proposed_entry_price"] == 63120.0
    assert label["proposed_target_4r_price"] == 63360.0
    assert label["rejection_reason"] is None


def test_labeling_is_deterministic():
    assert dt.label_setup(_observation()) == dt.label_setup(_observation())


def test_each_missing_component_rejects_with_auditable_reason():
    cases = (("htf_fvg_present", "SETUP_REJECTED_MISSING_HTF_FVG"),
             ("context_present", "SETUP_REJECTED_MISSING_CONTEXT"),
             ("choch_present", "SETUP_REJECTED_MISSING_CHOCH"),
             ("ltf_fvg_present", "SETUP_REJECTED_MISSING_LTF_FVG"),
             ("fib_alignment_pass", "SETUP_REJECTED_FIB_MISALIGNMENT"))
    for cond, status in cases:
        label = dt.label_setup(_observation(**{cond: False}))
        assert label["detector_status"] == status, cond
        assert label["rejection_reason"] == "condition_failed:" + cond
        assert label["detector_status"] in dt.DETECTOR_STATUSES


def test_htf_invalidation_and_ambiguity_reject():
    label = dt.label_setup(_observation(htf_invalidated=True))
    assert label["detector_status"] == "SETUP_REJECTED_HTF_INVALIDATED"
    assert label["invalidation_reason"] == "htf_fvg_closed_through"
    label2 = dt.label_setup(_observation(ambiguous=True))
    assert label2["detector_status"] == "SETUP_REJECTED_AMBIGUOUS"
    label3 = dt.label_setup(None)
    assert label3["detector_status"] == "SETUP_REJECTED_AMBIGUOUS"


def test_forbidden_capability_fields_reject():
    for bad in ("order_id", "api_key", "credential_token", "wallet_address",
                "account_balance", "live_authorized_flag",
                "paper_authorized_flag", "fetch_url"):
        label = dt.label_setup(_observation(**{bad: "x"}))
        assert label["detector_status"] == (
            "SETUP_REJECTED_FORBIDDEN_CAPABILITY"), bad
        assert "forbidden_capability_field" in label["rejection_reason"]


def test_bad_direction_window_or_incomplete_fields_reject():
    label = dt.label_setup(_observation(direction="sideways"))
    assert label["detector_status"] == "SETUP_REJECTED_AMBIGUOUS"
    label2 = dt.label_setup(_observation(session_window="03:00-04:00"))
    assert label2["detector_status"] == "SETUP_REJECTED_AMBIGUOUS"
    label3 = dt.label_setup(_observation(proposed_entry_price=None))
    assert label3["detector_status"] == "SETUP_REJECTED_AMBIGUOUS"
    assert "accepted_fields_incomplete" in label3["rejection_reason"]


def test_detector_cannot_fetch_score_trade_or_unlock():
    s = dt.build_ny_fvg_choch_detector_spec()
    for key in ("fetches_data", "uses_network", "calls_api", "scores_now",
                "runs_replay_now", "executes", "contains_order_logic",
                "connects_broker", "connects_exchange", "uses_credentials",
                "uses_wallet", "promotes_gate", "unlocks_downstream_gate"):
        assert s[key] is False, key
    assert s["paper_trading_gate_locked"] is True
    assert s["micro_live_gate_locked"] is True
    assert s["live_gate_locked"] is True
    joined = " ".join(dt.DETECTOR_RULES)
    assert "no_network_calls_and_no_data_fetching" in joined
    assert "labels_only" in joined
    assert "never_deleted" in joined
    assert "never_instructions" in joined
    assert "separate_human_approval" in joined


def test_foundation_and_pm_lane_untouched():
    assert op.build_optimizer_contract()["verdict"] == (
        op.VERDICT_OPT_CONTRACT_READY)
    assert ca.build_mutable_candidate_asset_spec()["verdict"] == (
        ca.VERDICT_CA_SPEC_READY)
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN
    s = dt.build_ny_fvg_choch_detector_spec()
    assert s["modifies_mission_flow"] is False
    assert s["modifies_pm_lane"] is False


def test_validate_catches_tampering():
    s1 = dt.build_ny_fvg_choch_detector_spec()
    s1["label_required_fields"] = s1["label_required_fields"][:5]
    assert dt.validate_ny_fvg_choch_detector_spec(s1)["valid"] is False
    s2 = dt.build_ny_fvg_choch_detector_spec()
    s2["labels_authorize_nothing"] = False
    assert dt.validate_ny_fvg_choch_detector_spec(s2)["valid"] is False
    s3 = dt.build_ny_fvg_choch_detector_spec()
    s3["live_gate_locked"] = False
    assert dt.validate_ny_fvg_choch_detector_spec(s3)["valid"] is False


def test_label_action_and_imports_clean():
    assert dt.get_ny_fvg_choch_detector_spec_label() == dt.DET_LABEL
    assert "READ-ONLY" in dt.DET_LABEL and dt.DET_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in dt.NEXT_REQUIRED_ACTION.upper(), banned
    tree = ast.parse(open(dt.__file__, encoding="utf-8").read())
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "pathlib", "os", "io", "json"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)

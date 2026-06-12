"""Tests for the SPARTA Breakout-Pullback-Structure Detector Spec
(Candidate #2's labeling gate)."""

from __future__ import annotations

import ast

import sparta_commander.crypto_intraday_breakout_pullback_structure_detector_spec as bpd

_READY = "BREAKOUT_PULLBACK_STRATEGY_SPEC_READY"


def _accepted_observation(**overrides):
    observation = {
        "setup_id": "BTCUSD_2026-06-10_bp_dry_run",
        "symbol": "BTCUSD", "session_date": "2026-06-10",
        "direction": "long", "sufficient_candles": True,
        "breakout_present": True, "breakout_strong": True,
        "pullback_present": True, "retest_pass": True,
        "continuation_confirmed": True, "ambiguous": False,
        "range_high": 100.5, "range_low": 99.5,
        "breakout_time": "2026-06-10T14:00:00Z", "breakout_level": 100.5,
        "breakout_direction": "long", "breakout_close": 101.0,
        "breakout_distance_bps": 49.75, "breakout_body_ratio": 0.8,
        "pullback_time": "2026-06-10T14:30:00Z", "pullback_level": 100.55,
        "pullback_depth_ratio": 0.58,
        "continuation_time": "2026-06-10T14:45:00Z",
        "continuation_close": 101.9,
        "structure_confirmation_reference": "higher low confirmation",
        "atr_14_15m": 1.025, "structural_stop_price": 100.55,
        "atr_stop_price": 100.36, "selected_stop_price": 100.36,
        "stop_model": "atr_1_5x", "entry_price": 101.9,
        "target_2r_price": 104.98, "target_3r_price": 106.52,
        "target_4r_price": 108.06,
    }
    observation.update(overrides)
    return observation


def test_detector_spec_gated_on_strategy_spec():
    spec = bpd.record_bp_detector_spec(_READY)
    assert spec["verdict"] == bpd.VERDICT_BPD_READY
    assert spec["blockers"] == []
    assert bpd.validate_bp_detector_spec(spec)["valid"] is True
    for bad in (None, "BREAKOUT_PULLBACK_STRATEGY_SPEC_BLOCKED", "x"):
        blocked = bpd.record_bp_detector_spec(bad)
        assert blocked["verdict"] == bpd.VERDICT_BPD_BLOCKED, bad
        assert "strategy_spec_not_ready" in blocked["blockers"]


def test_label_schema_complete_and_status_set_closed():
    assert len(bpd.BP_LABEL_REQUIRED_FIELDS) == 38
    for field in ("setup_id", "candidate_id", "symbol", "session_date",
                  "direction", "context_timeframe", "trigger_timeframe",
                  "range_lookback_bars", "range_high", "range_low",
                  "breakout_time", "breakout_level", "breakout_direction",
                  "breakout_close", "breakout_distance_bps",
                  "breakout_body_ratio", "pullback_time", "pullback_level",
                  "pullback_depth_ratio", "retest_pass",
                  "continuation_time", "continuation_close",
                  "structure_confirmation_reference", "atr_14_15m",
                  "structural_stop_price", "atr_stop_price",
                  "selected_stop_price", "stop_model", "entry_price",
                  "risk_distance_bps", "target_2r_price", "target_3r_price",
                  "target_4r_price", "cost_floor_bps", "cost_floor_pass",
                  "rejection_reason", "detector_status",
                  "label_authorizes_nothing"):
        assert field in bpd.BP_LABEL_REQUIRED_FIELDS, field
    assert len(bpd.BP_DETECTOR_STATUSES) == 10
    for status in ("BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW",
                   "BP_SETUP_REJECTED_NO_BREAKOUT",
                   "BP_SETUP_REJECTED_WEAK_BREAKOUT",
                   "BP_SETUP_REJECTED_NO_PULLBACK",
                   "BP_SETUP_REJECTED_FAILED_RETEST",
                   "BP_SETUP_REJECTED_NO_CONTINUATION",
                   "BP_SETUP_REJECTED_RISK_BELOW_81_BPS",
                   "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE",
                   "BP_SETUP_REJECTED_INSUFFICIENT_CANDLES",
                   "BP_SETUP_REJECTED_FORBIDDEN_CAPABILITY"):
        assert status in bpd.BP_DETECTOR_STATUSES, status


def test_valid_observation_accepts_with_floor_pass():
    label = bpd.label_bp_setup(_accepted_observation())
    assert label["detector_status"] == (
        "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW")
    assert set(label) == set(bpd.BP_LABEL_REQUIRED_FIELDS)
    assert label["candidate_id"] == (
        "CRYPTO_INTRADAY_BREAKOUT_PULLBACK_STRUCTURE_V1")
    assert label["cost_floor_bps"] == 81
    assert label["cost_floor_pass"] is True
    assert label["risk_distance_bps"] is not None
    assert label["risk_distance_bps"] >= 81
    assert label["label_authorizes_nothing"] is True
    assert label["rejection_reason"] is None


def test_each_missing_condition_maps_to_its_status():
    for flag, status in (("sufficient_candles",
                          "BP_SETUP_REJECTED_INSUFFICIENT_CANDLES"),
                         ("breakout_present",
                          "BP_SETUP_REJECTED_NO_BREAKOUT"),
                         ("breakout_strong",
                          "BP_SETUP_REJECTED_WEAK_BREAKOUT"),
                         ("pullback_present",
                          "BP_SETUP_REJECTED_NO_PULLBACK"),
                         ("retest_pass",
                          "BP_SETUP_REJECTED_FAILED_RETEST"),
                         ("continuation_confirmed",
                          "BP_SETUP_REJECTED_NO_CONTINUATION")):
        label = bpd.label_bp_setup(_accepted_observation(**{flag: False}))
        assert label["detector_status"] == status, flag
        assert label["rejection_reason"] == "condition_failed:" + flag
        assert label["cost_floor_pass"] is False
    ambiguous = bpd.label_bp_setup(_accepted_observation(ambiguous=True))
    assert ambiguous["detector_status"] == (
        "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE")


def test_risk_below_81_bps_rejects_at_label_time():
    tight = bpd.label_bp_setup(_accepted_observation(
        selected_stop_price=101.5))  # ~39 bps from entry 101.9
    assert tight["detector_status"] == "BP_SETUP_REJECTED_RISK_BELOW_81_BPS"
    assert tight["cost_floor_pass"] is False
    assert tight["risk_distance_bps"] < 81
    missing = bpd.label_bp_setup(_accepted_observation(entry_price=None))
    assert missing["detector_status"] == (
        "BP_SETUP_REJECTED_RISK_BELOW_81_BPS")


def test_forbidden_fields_and_bad_direction_reject():
    for bad in ("order_id", "api_key_env", "wallet_address",
                "live_authorized_flag", "broker_account", "login_token"):
        label = bpd.label_bp_setup(_accepted_observation(**{bad: "x"}))
        assert label["detector_status"] == (
            "BP_SETUP_REJECTED_FORBIDDEN_CAPABILITY"), bad
    sideways = bpd.label_bp_setup(_accepted_observation(direction="both"))
    assert sideways["detector_status"] == (
        "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE")
    assert bpd.label_bp_setup(None)["detector_status"] == (
        "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE")


def test_incomplete_accepted_fields_reject_as_ambiguous():
    no_target = bpd.label_bp_setup(_accepted_observation(
        target_4r_price=None))
    assert no_target["detector_status"] == (
        "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE")
    assert no_target["cost_floor_pass"] is False
    bad_model = bpd.label_bp_setup(_accepted_observation(
        stop_model="vibes"))
    assert bad_model["detector_status"] == (
        "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE")


def test_candidate_1_remains_rejected_and_preserved():
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_REASON, REJECTION_STATUS)
    assert REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    assert REJECTION_REASON == "COST_NON_VIABLE_RISK_GEOMETRY"
    assert bpd.CANDIDATE_ID != "NY_SESSION_FVG_CHOCH_STRATEGY_CANDIDATE_V1"
    assert ("candidate_1_fvg_choch_stays_rejected_on_record"
            in bpd.BP_DETECTOR_RULES)


def test_validator_strict_and_gates_locked():
    spec = bpd.record_bp_detector_spec(_READY)
    for key in ("executes", "writes_files", "writes_reports",
                "runs_detector_now", "runs_replay_now", "scores_now",
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
    assert spec["cost_floor_bps"] == 81
    tampered = bpd.record_bp_detector_spec(_READY)
    tampered["detector_statuses"] = tampered["detector_statuses"][:5]
    assert bpd.validate_bp_detector_spec(tampered)["valid"] is False
    tampered2 = bpd.record_bp_detector_spec(_READY)
    tampered2["cost_floor_bps"] = 10
    assert bpd.validate_bp_detector_spec(tampered2)["valid"] is False
    tampered3 = bpd.record_bp_detector_spec(_READY)
    tampered3["live_gate_locked"] = False
    assert bpd.validate_bp_detector_spec(tampered3)["valid"] is False
    assert (bpd.record_bp_detector_spec(_READY)
            == bpd.record_bp_detector_spec(_READY))


def test_label_action_and_imports_clean():
    assert bpd.get_bp_detector_spec_label() == bpd.BPD_LABEL
    assert "READ-ONLY" in bpd.BPD_LABEL and bpd.BPD_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in bpd.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(bpd.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
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
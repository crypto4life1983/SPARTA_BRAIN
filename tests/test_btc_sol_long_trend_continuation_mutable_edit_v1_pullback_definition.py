"""Tests for Candidate #3 Mutable Edit V1 (pullback definition).

Proves: contract READY only while the zero-accepts freeze certifies and
the ledger holds; the edit scope is exactly one field; the V1 scanner
accepts a lower-close pullback the old scanner rejected, while behaving
IDENTICALLY to the old scanner on the original fixtures (everything else
unchanged); failure rules and forbidden changes are frozen; zero
capability."""

from __future__ import annotations

import ast

import pytest

import sparta_commander.btc_sol_long_trend_continuation_detector_spec_contract as tcd
import sparta_commander.btc_sol_long_trend_continuation_mutable_edit_v1_pullback_definition as m1

REPO_ROOT = "C:/SPARTA_BRAIN"


def _fixture_15m_lower_close_pullback():
    """The accepted fixture geometry, but bar 26 makes a lower CLOSE
    without a lower LOW -- invisible to the old consecutive-lower-low
    scanner, visible to V1."""
    bars = []
    for i in range(24):
        close = 100.0 + 0.05 * i
        bars.append({"time_utc": tcd._stamp_15m(i), "open": close - 0.02,
                     "high": close + 0.05, "low": close - 0.10,
                     "close": close})
    bars.append({"time_utc": tcd._stamp_15m(24), "open": 102.0,
                 "high": 102.6, "low": 101.95, "close": 102.5})
    bars.append({"time_utc": tcd._stamp_15m(25), "open": 102.1,
                 "high": 102.2, "low": 101.8, "close": 101.9})
    # lower close (101.85 < 101.9) but NOT a lower low (101.8 == prior)
    bars.append({"time_utc": tcd._stamp_15m(26), "open": 101.9,
                 "high": 102.0, "low": 101.8, "close": 101.85})
    bars.append({"time_utc": tcd._stamp_15m(27), "open": 101.85,
                 "high": 101.9, "low": 101.5, "close": 101.7})
    bars.append({"time_utc": tcd._stamp_15m(28), "open": 102.0,
                 "high": 102.45, "low": 101.9, "close": 102.4})
    bars.append({"time_utc": tcd._stamp_15m(29), "open": 102.4,
                 "high": 102.6, "low": 102.2, "close": 102.5})
    return bars


def test_contract_ready_and_gated_on_frozen_evidence():
    record = m1.build_tc3_mutable_edit_v1(REPO_ROOT, tracked_paths=[])
    if record["verdict"] == m1.VERDICT_M1_BLOCKED and (
            "zero_accepts_evidence_not_certified" in record["blockers"]):
        pytest.skip("candidate #3 label artifacts not present")
    assert record["verdict"] == m1.VERDICT_M1_READY
    assert record["blockers"] == []
    assert m1.validate_tc3_mutable_edit_v1(record)["valid"] is True


def test_edit_scope_is_exactly_one_field():
    assert m1.ALLOWED_EDITED_FIELDS == ("pullback_bar_definition",)
    params = m1.V1_NEW_PARAMETERS
    assert params["consecutive_lower_low_only_requirement_removed"] is True
    assert "lower low OR a lower close" in params["pullback_bar_rule_new"]
    assert params["pullback_window_bars_min"] == 2
    assert params["pullback_window_bars_max"] == 8
    assert params["pullback_must_hold_above_prior_swing_low"] is True
    assert params["max_retrace_pct_of_impulse_leg"] == 61.8
    locked = m1.LOCKED_UNCHANGED
    for item in ("symbols_btcusd_solusd_only", "direction_long_only",
                 "trend_qualification_1h_sma20_above_and_rising",
                 "impulse_new_20_bar_closing_high_within_8_bars",
                 "entry_on_first_15m_close_above_pullback_high",
                 "stop_wider_of_structural_and_1_5x_atr14_never_tightened",
                 "minimum_risk_distance_81_bps_checked_at_label_time",
                 "fee_honest_27_bps_round_trip_for_any_future_replay",
                 "maker_execution_never_assumed",
                 "label_schema_and_closed_statuses_unchanged"):
        assert item in locked, item


def test_v1_scanner_accepts_lower_close_pullback_old_scanner_missed():
    bars = _fixture_15m_lower_close_pullback()
    uptrend = tcd._fixture_1h(True)
    old = tcd.scan_tc_setups(bars, uptrend, "BTCUSD")
    old_accepts = [lab for lab in old
                   if lab["status"] == "accepted_for_replay_review"]
    assert old_accepts == []  # old rule: k=1 -> pullback_too_short
    impulse_label_old = [lab for lab in old if lab["setup_id"]
                         == "BTCUSD_" + tcd._stamp_15m(24)][0]
    assert impulse_label_old["status"] == "rejected_pullback_too_short"
    new = m1.scan_tc_setups_v1(bars, uptrend, "BTCUSD")
    new_accepts = [lab for lab in new
                   if lab["status"] == "accepted_for_replay_review"]
    assert len(new_accepts) == 1
    winner = new_accepts[0]
    assert winner["pullback_bar_count"] == 3
    assert winner["entry_price"] == 102.4
    assert winner["stop_price"] == 101.5
    assert winner["risk_distance_bps"] >= 81
    assert winner["cost_viable"] is True
    assert tcd.validate_tc_label(winner)["valid"] is True


def test_v1_scanner_identical_on_original_fixtures():
    """Everything except the pullback rule is unchanged: on fixtures
    whose pullbacks are strict lower-lows, V1 must reproduce the pushed
    scanner's labels EXACTLY."""
    uptrend = tcd._fixture_1h(True)
    downtrend = tcd._fixture_1h(False)
    for bars, bars_1h, symbol in (
            (tcd._fixture_15m_accepted(), uptrend, "BTCUSD"),
            (tcd._fixture_15m_tight(), uptrend, "SOLUSD"),
            (tcd._fixture_15m_accepted(), downtrend, "BTCUSD")):
        assert (m1.scan_tc_setups_v1(bars, bars_1h, symbol)
                == tcd.scan_tc_setups(bars, bars_1h, symbol))


def test_v1_scanner_still_enforces_floor_and_scope():
    uptrend = tcd._fixture_1h(True)
    tight = m1.scan_tc_setups_v1(tcd._fixture_15m_tight(),
                                 uptrend, "SOLUSD")
    assert not any(lab["status"] == "accepted_for_replay_review"
                   for lab in tight)
    assert any(lab["status"] == "rejected_cost_floor_risk_too_small"
               for lab in tight)
    down = m1.scan_tc_setups_v1(_fixture_15m_lower_close_pullback(),
                                tcd._fixture_1h(False), "BTCUSD")
    assert not any(lab["status"] == "accepted_for_replay_review"
                   for lab in down)
    with pytest.raises(ValueError):
        m1.scan_tc_setups_v1(_fixture_15m_lower_close_pullback(),
                             uptrend, "ETHUSD")


def test_failure_rules_and_forbidden_changes_frozen():
    rules = m1.PRE_COMMITTED_FAILURE_RULES_V1
    assert len(rules) == 3
    assert any("zero or near-zero" in rule
               and "REJECTED_KEPT_ON_RECORD" in rule for rule in rules)
    assert any("net-negative in all target variants" in rule
               for rule in rules)
    assert any("no second mutable edit" in rule for rule in rules)
    assert m1.NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS == 10
    for item in ("lowering_the_81bps_floor", "adding_short_setups",
                 "changing_symbols_or_adding_symbols",
                 "weakening_or_changing_the_1h_trend_qualification",
                 "changing_or_tightening_the_stop_rule",
                 "changing_the_label_schema_or_statuses",
                 "touching_candidate_1_or_candidate_2_records"):
        assert item in m1.FORBIDDEN_CHANGES, item


def test_tampering_invalidates():
    record = m1.build_tc3_mutable_edit_v1(REPO_ROOT, tracked_paths=[])
    if record["verdict"] != m1.VERDICT_M1_READY:
        pytest.skip("candidate #3 label artifacts not present")
    for field, value in (
            ("allowed_edited_fields", ["pullback_bar_definition",
                                       "stop_rule"]),
            ("v1_new_parameters", {}),
            ("locked_unchanged", []),
            ("near_zero_threshold_accepted_labels", 0),
            ("pre_committed_failure_rules_v1", []),
            ("forbidden_changes", []),
            ("cost_floor_bps", 54),
            ("one_authorized_edit_only", False),
            ("not_a_rescue_of_candidate_2", False),
            ("live_gate_locked", False),
            ("claims_profitability", True),
            ("revives_candidate_2", True)):
        tampered = m1.build_tc3_mutable_edit_v1(REPO_ROOT,
                                                tracked_paths=[])
        tampered[field] = value
        assert m1.validate_tc3_mutable_edit_v1(
            tampered)["valid"] is False, field


def test_ledger_intact_and_capabilities_locked():
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    assert C1 == C2 == "REJECTED_KEPT_ON_RECORD"
    record = m1.build_tc3_mutable_edit_v1(REPO_ROOT, tracked_paths=[])
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "revives_candidate_2"):
        assert record[key] is False, key
    assert record["not_a_rescue_of_candidate_2"] is True
    assert record["one_authorized_edit_only"] is True
    assert record["second_edit_requires_separate_human_decision"] is True


def test_label_action_and_module_purity():
    assert m1.get_mutable_edit_v1_label() == m1.M1_LABEL
    assert "READ-ONLY" in m1.M1_LABEL
    assert "ONE AUTHORIZED EDIT" in m1.M1_LABEL
    assert "NOT A RESCUE" in m1.M1_LABEL
    assert m1.M1_MODE == "RESEARCH_ONLY"
    assert m1.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_3_V1_REDETECTION_ON_STAGED_SAMPLE")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in m1.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(m1.__file__, encoding="utf-8").read()
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
                   "ssl", "ftplib", "hashlib", "datetime"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))

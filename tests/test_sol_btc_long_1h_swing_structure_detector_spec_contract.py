"""Tests for the Candidate #4 detector spec + dry-run path.

Proves: contract READY only while the (triple-ledger-gated) strategy
spec is READY; the 33-field schema and 9 closed statuses are frozen; the
81 bps floor is checked AT LABEL TIME; the WIDER-stop rule holds; swing
lows are confirmed-only (no lookahead) and the 4h trend gate is
completed-bars-only; the synthetic dry run passes; the scanner refuses
out-of-scope symbols; module purity."""

from __future__ import annotations

import ast

import pytest

import sparta_commander.sol_btc_long_1h_swing_structure_detector_spec_contract as c4d


def test_contract_ready_and_gated():
    record = c4d.build_c4_detector_spec_contract()
    assert record["verdict"] == c4d.VERDICT_C4D_READY
    assert record["blockers"] == []
    assert c4d.validate_c4_detector_spec_contract(record)["valid"] is True
    assert record["candidate_id"] == "SOL_BTC_LONG_1H_SWING_STRUCTURE_V1"
    assert record["symbols"] == ["SOLUSD", "BTCUSD"]
    assert record["direction"] == "long_only"
    assert record["cost_floor_bps"] == 81
    assert record["cost_floor_checked_at_label_time"] is True
    assert record["assumed_round_trip_cost_bps"] == 27
    assert record["maker_execution_assumed"] is False
    assert record["dry_run_uses_synthetic_fixtures_only"] is True
    assert record["runs_real_detection_now"] is False
    assert "fewer than 10 accepted labels" in record["near_zero_rule_note"]


def test_schema_and_statuses_frozen():
    assert len(c4d.C4_LABEL_REQUIRED_FIELDS) == 33
    for field in ("sl1_low_price", "sl2_low_price",
                  "sl2_confirmation_bar_time_utc",
                  "inter_swing_high_price", "risk_distance_bps",
                  "stop_source", "label_authorizes_nothing"):
        assert field in c4d.C4_LABEL_REQUIRED_FIELDS, field
    assert len(c4d.C4_DETECTOR_STATUSES) == 9
    assert c4d.C4_DETECTOR_STATUSES[0] == "accepted_for_replay_review"
    assert all(s.startswith("rejected_")
               for s in c4d.C4_DETECTOR_STATUSES[1:])
    for field, value in (("label_required_fields", ["setup_id"]),
                         ("detector_statuses", ["accepted_for_replay_review"]),
                         ("cost_floor_bps", 54),
                         ("stop_rule", "tighter_stop"),
                         ("near_zero_rule_note", "none"),
                         ("dry_run_uses_synthetic_fixtures_only", False),
                         ("runs_real_detection_now", True)):
        tampered = c4d.build_c4_detector_spec_contract()
        tampered[field] = value
        assert c4d.validate_c4_detector_spec_contract(
            tampered)["valid"] is False, field


def test_dry_run_passes_with_expected_outcomes():
    result = c4d.run_c4_detector_dry_run()
    assert result["verdict"] == c4d.VERDICT_C4D_DRY_RUN_PASSED
    assert result["failures"] == []
    assert result["uses_synthetic_fixtures_only"] is True
    assert result["reads_staged_candles"] is False
    assert result["reads_any_files"] is False
    accepted = result["fixtures"]["accepted_fixture"]
    assert accepted["risk_distance_bps"] >= 81
    assert accepted["stop_source"] == "structural_sl2_low"
    assert accepted["schema_valid_all"] is True
    assert "accepted_for_replay_review" in accepted["statuses"]
    tight = result["fixtures"]["tight_fixture"]
    assert "rejected_cost_floor_risk_too_small" in tight["statuses"]
    assert "accepted_for_replay_review" not in tight["statuses"]
    down = result["fixtures"]["downtrend_fixture"]
    assert "rejected_trend_not_qualified" in down["statuses"]
    assert "accepted_for_replay_review" not in down["statuses"]
    assert c4d.run_c4_detector_dry_run() == result  # determinism


def test_accepted_label_geometry_and_floor():
    labels = c4d.scan_c4_setups(
        c4d._fixture_1h_accepted(), c4d._fixture_4h(True), "SOLUSD")
    assert len(labels) == 1
    winner = labels[0]
    assert winner["status"] == "accepted_for_replay_review"
    assert winner["sl1_low_price"] == 99.0
    assert winner["sl2_low_price"] == 99.8
    assert winner["sl2_low_price"] > winner["sl1_low_price"]
    assert winner["bars_between_swings"] == 6
    assert winner["inter_swing_high_price"] == 101.5
    assert winner["entry_price"] == 101.8
    assert winner["stop_price"] == 99.8
    assert winner["structural_stop_price"] == 99.8
    assert winner["volatility_stop_price"] > 99.8  # structural is WIDER
    assert 196.0 < winner["risk_distance_bps"] < 197.0
    assert winner["cost_viable"] is True
    assert winner["cost_viability_floor_bps"] == 81
    assert winner["target_2r_price"] == 105.8
    assert winner["target_3r_price"] == 107.8
    assert winner["target_4r_price"] == 109.8
    assert winner["trend_qualified"] is True
    assert c4d.validate_c4_label(winner)["valid"] is True
    mutated = dict(winner, risk_distance_bps=80.9)
    assert c4d.validate_c4_label(mutated)["valid"] is False
    mutated2 = dict(winner, sl2_low_price=98.9)  # not higher-low anymore
    assert c4d.validate_c4_label(mutated2)["valid"] is False
    mutated3 = dict(winner, label_authorizes_nothing=False)
    assert c4d.validate_c4_label(mutated3)["valid"] is False
    mutated4 = dict(winner, direction="short")
    assert c4d.validate_c4_label(mutated4)["valid"] is False


def test_tight_fixture_rejected_at_floor():
    labels = c4d.scan_c4_setups(
        c4d._fixture_1h_tight(), c4d._fixture_4h(True), "BTCUSD")
    rejects = [lab for lab in labels
               if lab["status"] == "rejected_cost_floor_risk_too_small"]
    assert len(rejects) == 1
    reject = rejects[0]
    assert reject["risk_distance_bps"] < 81
    assert reject["cost_viable"] is False
    assert reject["target_2r_price"] is None


def test_swing_lows_confirmed_only_no_lookahead():
    bars = c4d._fixture_1h_accepted()
    swings = c4d.find_confirmed_swing_lows(bars)
    assert swings == [10, 16]
    # a swing low needs 2 bars AFTER it: truncate the series right after
    # the SL2 bar and it must vanish (not knowable yet)
    assert c4d.find_confirmed_swing_lows(bars[:17]) == [10]
    assert c4d.find_confirmed_swing_lows(bars[:18]) == [10]
    assert c4d.find_confirmed_swing_lows(bars[:19]) == [10, 16]


def test_4h_trend_gate_completed_bars_only():
    bars_4h = c4d._fixture_4h(True)  # 20 bars from 2026-01-29T00:00
    # signal before the 13th bar completes -> insufficient
    early = c4d.evaluate_trend_qualification_4h(
        bars_4h, "2026-01-31T03:59:00Z")
    assert early["completed_bars"] == 12
    assert early["insufficient_history"] is True
    # one minute later the 13th bar completes -> sufficient
    later = c4d.evaluate_trend_qualification_4h(
        bars_4h, "2026-01-31T04:00:00Z")
    assert later["completed_bars"] == 13
    assert later["insufficient_history"] is False


def test_aggregate_4h_complete_groups_only():
    bars_1h = c4d._fixture_1h_accepted()  # 24 bars from 00:00
    bars_4h = c4d.aggregate_4h_from_1h(bars_1h)
    assert len(bars_4h) == 6  # 24 hours = 6 complete 4h groups
    assert bars_4h[0]["time_utc"] == "2026-02-02T00:00:00Z"
    first_group = bars_1h[0:4]
    assert bars_4h[0]["open"] == first_group[0]["open"]
    assert bars_4h[0]["close"] == first_group[-1]["close"]
    assert bars_4h[0]["high"] == max(b["high"] for b in first_group)
    assert bars_4h[0]["low"] == min(b["low"] for b in first_group)
    # drop one bar -> the last group is incomplete and must vanish
    assert len(c4d.aggregate_4h_from_1h(bars_1h[:-1])) == 5


def test_scanner_rejects_out_of_scope_symbols():
    with pytest.raises(ValueError):
        c4d.scan_c4_setups(c4d._fixture_1h_accepted(),
                           c4d._fixture_4h(True), "ETHUSD")
    with pytest.raises(ValueError):
        c4d.scan_c4_setups(c4d._fixture_1h_accepted(),
                           c4d._fixture_4h(True), "DOGEUSD")


def test_not_higher_low_and_void_paths():
    bars = c4d._fixture_1h_accepted()
    # lower the second swing low BELOW the first -> not_higher_low
    lower = [dict(b) for b in bars]
    lower[16]["low"] = 98.5
    lower[16]["open"] = 99.0
    lower[16]["close"] = 99.2
    labels = c4d.scan_c4_setups(lower, c4d._fixture_4h(True), "SOLUSD")
    assert [lab["status"] for lab in labels] == ["rejected_not_higher_low"]
    # break the SL2 low before the trigger -> void. The 99.7 print also
    # creates a NEW confirmed swing low at bar 19, so a second pair
    # (16,19) appears and is correctly rejected as not-higher-low.
    void = [dict(b) for b in bars]
    void[19]["low"] = 99.7  # below SL2 low 99.8, before bar-20 trigger
    labels2 = c4d.scan_c4_setups(void, c4d._fixture_4h(True), "SOLUSD")
    assert [lab["status"] for lab in labels2] == [
        "rejected_sl2_low_broken_before_entry",
        "rejected_not_higher_low"]
    assert not any(lab["status"] == "accepted_for_replay_review"
                   for lab in labels2)


def test_label_action_and_module_purity():
    assert c4d.get_candidate_4_detector_label() == c4d.C4D_LABEL
    assert "READ-ONLY" in c4d.C4D_LABEL
    assert "SYNTHETIC FIXTURES" in c4d.C4D_LABEL
    assert c4d.C4D_MODE == "RESEARCH_ONLY"
    assert c4d.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_4_DRY_RUN_REVIEW")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c4d.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c4d.__file__, encoding="utf-8").read()
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
                   "ssl", "ftplib", "hashlib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))

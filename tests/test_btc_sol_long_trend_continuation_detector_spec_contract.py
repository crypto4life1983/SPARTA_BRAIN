"""Tests for the Candidate #3 detector spec + dry-run path.

Proves: contract READY only while the (ledger-gated) strategy spec is
READY; the 33-field label schema and 10 closed statuses are frozen; the
81 bps floor is checked AT LABEL TIME via the pushed cost-viability gate;
the WIDER-stop rule holds; trend qualification is anti-lookahead; the
synthetic dry run passes with the expected outcomes; the scanner refuses
out-of-scope symbols; and the module has no network/scheduler/file-write
capability.
"""

from __future__ import annotations

import ast

import sparta_commander.btc_sol_long_trend_continuation_detector_spec_contract as tcd


def test_contract_ready_and_gated():
    record = tcd.build_tc_detector_spec_contract()
    assert record["verdict"] == tcd.VERDICT_TCD_READY
    assert record["blockers"] == []
    assert tcd.validate_tc_detector_spec_contract(record)["valid"] is True
    assert record["candidate_id"] == "BTC_SOL_LONG_TREND_CONTINUATION_V1"
    assert record["symbols"] == ["BTCUSD", "SOLUSD"]
    assert record["direction"] == "long_only"
    assert record["cost_floor_bps"] == 81
    assert record["cost_floor_checked_at_label_time"] is True
    assert record["assumed_round_trip_cost_bps"] == 27
    assert record["maker_execution_assumed"] is False
    assert record["dry_run_uses_synthetic_fixtures_only"] is True
    assert record["runs_real_detection_now"] is False


def test_schema_and_statuses_frozen():
    assert len(tcd.TC_LABEL_REQUIRED_FIELDS) == 33
    assert "label_authorizes_nothing" in tcd.TC_LABEL_REQUIRED_FIELDS
    assert "risk_distance_bps" in tcd.TC_LABEL_REQUIRED_FIELDS
    assert "stop_source" in tcd.TC_LABEL_REQUIRED_FIELDS
    assert len(tcd.TC_DETECTOR_STATUSES) == 10
    assert tcd.TC_DETECTOR_STATUSES[0] == "accepted_for_replay_review"
    assert all(s.startswith("rejected_")
               for s in tcd.TC_DETECTOR_STATUSES[1:])
    for field, value in (("label_required_fields", ["setup_id"]),
                         ("detector_statuses", ["accepted_for_replay_review"]),
                         ("cost_floor_bps", 54),
                         ("stop_rule", "tighter_stop"),
                         ("dry_run_uses_synthetic_fixtures_only", False),
                         ("runs_real_detection_now", True)):
        tampered = tcd.build_tc_detector_spec_contract()
        tampered[field] = value
        assert tcd.validate_tc_detector_spec_contract(
            tampered)["valid"] is False, field


def test_dry_run_passes_with_expected_outcomes():
    result = tcd.run_tc_detector_dry_run()
    assert result["verdict"] == tcd.VERDICT_TCD_DRY_RUN_PASSED
    assert result["failures"] == []
    assert result["uses_synthetic_fixtures_only"] is True
    assert result["reads_staged_candles"] is False
    assert result["reads_any_files"] is False
    accepted = result["fixtures"]["accepted_fixture"]
    assert accepted["risk_distance_bps"] >= 81
    assert accepted["stop_source"] == "structural_pullback_low"
    assert accepted["schema_valid_all"] is True
    assert "accepted_for_replay_review" in accepted["statuses"]
    tight = result["fixtures"]["tight_fixture"]
    assert "rejected_cost_floor_risk_too_small" in tight["statuses"]
    assert "accepted_for_replay_review" not in tight["statuses"]
    down = result["fixtures"]["downtrend_fixture"]
    assert "rejected_trend_not_qualified" in down["statuses"]
    assert "accepted_for_replay_review" not in down["statuses"]
    # determinism
    assert tcd.run_tc_detector_dry_run() == result


def test_accepted_label_floor_checked_at_label_time():
    labels = tcd.scan_tc_setups(
        tcd._fixture_15m_accepted(), tcd._fixture_1h(True), "BTCUSD")
    winners = [lab for lab in labels
               if lab["status"] == "accepted_for_replay_review"]
    assert len(winners) == 1
    winner = winners[0]
    assert winner["entry_price"] == 102.4
    assert winner["stop_price"] == 101.5
    assert winner["structural_stop_price"] == 101.5
    assert winner["volatility_stop_price"] > 101.5  # structural is WIDER
    assert 87.0 < winner["risk_distance_bps"] < 88.0
    assert winner["cost_viable"] is True
    assert winner["cost_viability_floor_bps"] == 81
    assert winner["target_2r_price"] == 104.2
    assert winner["target_3r_price"] == 105.1
    assert winner["target_4r_price"] == 106.0
    assert winner["trend_qualified"] is True
    assert winner["direction"] == "long"
    assert winner["label_authorizes_nothing"] is True
    assert tcd.validate_tc_label(winner)["valid"] is True
    # an accepted label below the floor must fail validation
    mutated = dict(winner, risk_distance_bps=80.9)
    assert tcd.validate_tc_label(mutated)["valid"] is False
    mutated2 = dict(winner, label_authorizes_nothing=False)
    assert tcd.validate_tc_label(mutated2)["valid"] is False
    mutated3 = dict(winner, status="totally_new_status")
    assert tcd.validate_tc_label(mutated3)["valid"] is False
    mutated4 = dict(winner, direction="short")
    assert tcd.validate_tc_label(mutated4)["valid"] is False


def test_wider_stop_rule_uses_volatility_when_structural_tight():
    labels = tcd.scan_tc_setups(
        tcd._fixture_15m_tight(), tcd._fixture_1h(True), "SOLUSD")
    rejects = [lab for lab in labels
               if lab["status"] == "rejected_cost_floor_risk_too_small"]
    assert len(rejects) == 1
    reject = rejects[0]
    assert reject["stop_source"] == "volatility_1_5x_atr14"
    assert reject["stop_price"] < reject["structural_stop_price"]
    assert reject["risk_distance_bps"] < 81
    assert reject["cost_viable"] is False
    assert reject["target_2r_price"] is None  # no targets for rejects


def test_trend_qualification_is_anti_lookahead():
    bars_1h = tcd._fixture_1h(True)
    # signal before ANY 1h bar completes -> insufficient history
    early = tcd.evaluate_trend_qualification(
        bars_1h, "2026-01-01T06:30:00Z")
    assert early["insufficient_history"] is True
    assert early["qualified"] is False
    # signal exactly when the 25th bar completes -> enough history
    later = tcd.evaluate_trend_qualification(
        bars_1h, "2026-01-02T07:00:00Z")
    assert later["completed_bars"] == 25
    assert later["insufficient_history"] is False
    # only completed bars count: one minute earlier sees one bar fewer
    earlier = tcd.evaluate_trend_qualification(
        bars_1h, "2026-01-02T06:59:00Z")
    assert earlier["completed_bars"] == 24
    assert earlier["insufficient_history"] is True


def test_scanner_rejects_out_of_scope_symbols():
    import pytest
    with pytest.raises(ValueError):
        tcd.scan_tc_setups(
            tcd._fixture_15m_accepted(), tcd._fixture_1h(True), "ETHUSD")
    with pytest.raises(ValueError):
        tcd.scan_tc_setups(
            tcd._fixture_15m_accepted(), tcd._fixture_1h(True), "DOGEUSD")


def test_aggregate_1h_complete_hours_only():
    bars_15m = tcd._fixture_15m_accepted()  # starts 12:00, 30 bars
    bars_1h = tcd.aggregate_1h_from_15m(bars_15m)
    # 30 bars = 7 complete hours + 2 leftover quarters
    assert len(bars_1h) == 7
    assert bars_1h[0]["time_utc"] == "2026-01-02T12:00:00Z"
    first_quarter = bars_15m[0:4]
    assert bars_1h[0]["open"] == first_quarter[0]["open"]
    assert bars_1h[0]["close"] == first_quarter[-1]["close"]
    assert bars_1h[0]["high"] == max(b["high"] for b in first_quarter)
    assert bars_1h[0]["low"] == min(b["low"] for b in first_quarter)


def test_capabilities_locked_and_blocked_propagates():
    record = tcd.build_tc_detector_spec_contract()
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
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    assert "staged 15m candles only" in record[
        "future_real_run_data_source"]
    assert "separate human approval" in record[
        "future_real_run_data_source"]
    tampered = tcd.build_tc_detector_spec_contract()
    tampered["live_gate_locked"] = False
    assert tcd.validate_tc_detector_spec_contract(
        tampered)["valid"] is False


def test_label_action_and_module_purity():
    assert tcd.get_candidate_3_detector_label() == tcd.TCD_LABEL
    assert "READ-ONLY" in tcd.TCD_LABEL
    assert "SYNTHETIC FIXTURES" in tcd.TCD_LABEL
    assert tcd.TCD_MODE == "RESEARCH_ONLY"
    assert tcd.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_3_DRY_RUN_REVIEW")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in tcd.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(tcd.__file__, encoding="utf-8").read()
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

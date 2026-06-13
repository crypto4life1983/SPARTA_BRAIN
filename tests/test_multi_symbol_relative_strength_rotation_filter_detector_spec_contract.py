"""Tests for the Candidate #6 detector spec + synthetic dry-run path.

Pure scanner proven on in-memory fixtures: strict-rank-#1 accept; tie
rejection; rank-#1-but-negative-RS rejection; no-fresh-high emits no
attempt; next-bar-only evaluation; one setup per event bar; not a
delayed pullback resumption; WIDER stop max-rule exactness and invalid
geometry; 81 bps floor before replay eligibility; 27 bps preserved;
universe enforcement; chain gates live; purity. Runs alongside the
Candidate #6 spec-review tests and the commander safety suite."""

from __future__ import annotations

import ast

import pytest

import sparta_commander.multi_symbol_relative_strength_rotation_filter_detector_spec_contract as c6d


def _aligned(sol=None, eth=None, btc=None):
    return c6d.build_bars({
        "BTCUSD": btc or c6d.fixture_flat(50.0),
        "ETHUSD": eth or c6d.fixture_flat(80.0),
        "SOLUSD": sol or c6d.fixture_sol_breakout()})


def test_contract_ready_and_chain_gated():
    import sparta_commander.multi_symbol_relative_strength_rotation_filter_spec_review_contract as c6s
    import sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract as c6p
    import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as cr
    import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
    assert c6s.build_candidate_6_spec_review()["verdict"] == (
        "CANDIDATE_6_SPEC_REVIEW_READY")
    assert c6p.build_candidate_6_family_proposal()["verdict"] == (
        "CANDIDATE_6_FAMILY_PROPOSAL_READY")
    assert cr.build_candidate_recommendation()["verdict"] == (
        "STRATEGY_FACTORY_CANDIDATE_RECOMMENDATION_V1_READY")
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        "STRATEGY_FACTORY_AUTOPILOT_RESEARCH_LOOP_V1_READY")
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
        REJECTION_STATUS as C4)
    from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
        REJECTION_STATUS as C5)
    assert C1 == C2 == C3 == C4 == C5 == "REJECTED_KEPT_ON_RECORD"
    record = c6d.build_c6_detector_spec_contract()
    assert record["verdict"] == c6d.VERDICT_C6D_READY
    assert record["blockers"] == []
    assert c6d.validate_c6_detector_spec_contract(record)["valid"] is True
    assert c6d.build_c6_detector_spec_contract() == record


def test_dry_run_passes_and_fixture_counts():
    result = c6d.run_c6_detector_dry_run()
    assert result["verdict"] == c6d.VERDICT_C6D_DRY_RUN_PASSED
    assert result["failures"] == []
    assert result["uses_synthetic_fixtures_only"] is True
    assert result["reads_real_candles"] is False
    assert result["reads_staged_data"] is False
    assert result["reads_any_files"] is False
    fixtures = result["fixtures"]
    assert fixtures["sol_rank1_breakout"]["accepted"] == 1
    assert fixtures["sol_rank1_breakout"]["attempts"] == 1
    assert fixtures["rank_tie_fails"]["accepted"] == 0
    assert fixtures["rank1_but_negative_rs"]["accepted"] == 0
    assert fixtures["rank1_but_negative_rs"]["attempts"] == 3
    assert fixtures["no_fresh_closing_high"]["attempts"] == 0
    assert fixtures["event_on_last_bar"]["accepted"] == 0
    assert c6d.run_c6_detector_dry_run() == result  # determinism


def test_1_expected_setup_emitted_exactly():
    setups = c6d.scan_c6_setups(_aligned(), "SOLUSD")
    assert len(setups) == 1
    setup = setups[0]
    assert setup["status"] == "accepted_for_replay_review"
    for field in c6d.C6_SETUP_REQUIRED_FIELDS:
        assert field in setup, field
    assert setup["symbol"] == "SOLUSD"
    assert setup["timeframe"] == "1h"
    assert setup["direction"] == "long"
    assert setup["event_time"] == c6d._stamp(30)
    assert setup["entry_price"] == 106.5
    assert setup["strict_rank_1"] is True
    assert setup["rs_positive"] is True
    assert setup["fresh_10_bar_closing_high"] is True
    assert setup["return_20_candidate"] > 0
    assert all(setup["return_20_candidate"] > value
               for value in setup["return_20_others"].values())
    assert setup["stop_price"] < setup["entry_price"]
    assert setup["geometry_floor_pass_by_variant"] == {
        "2r": True, "3r": True, "4r": True}
    assert setup["rejection_reasons"] == []


def test_2_ties_fail():
    bars = c6d.build_bars({
        "BTCUSD": c6d.fixture_flat(50.0),
        "ETHUSD": c6d.fixture_sol_breakout(),
        "SOLUSD": c6d.fixture_sol_breakout()})
    setups = c6d.scan_c6_setups(bars, "SOLUSD")
    assert [s["status"] for s in setups] == [
        "rejected_not_strict_rank_1"]
    assert setups[0]["strict_rank_1"] is False
    # the gate itself: equal returns are never strictly greater
    gate = c6d.rank_gate(bars, "SOLUSD", 30)
    assert gate["strict_rank_1"] is False
    assert gate["passes"] is False


def test_3_negative_or_zero_rs_rejected_even_if_rank_1():
    bars = c6d.build_bars({
        "BTCUSD": c6d.fixture_falling(300.0),
        "ETHUSD": c6d.fixture_falling(250.0),
        "SOLUSD": c6d.fixture_recovering_but_negative()})
    setups = c6d.scan_c6_setups(bars, "SOLUSD")
    assert len(setups) == 3
    for setup in setups:
        assert setup["status"] == "rejected_rs_not_positive"
        assert setup["strict_rank_1"] is True   # rank #1 held
        assert setup["rs_positive"] is False    # but RS negative
        assert setup["return_20_candidate"] < 0
    # zero RS also fails (strictly greater than zero required)
    flat = c6d.fixture_flat(100.0)
    gate = c6d.rank_gate(c6d.build_bars(
        {"BTCUSD": c6d.fixture_falling(300.0),
         "ETHUSD": c6d.fixture_falling(250.0),
         "SOLUSD": flat}), "SOLUSD", 30)
    assert gate["strict_rank_1"] is True
    assert gate["rs_positive"] is False
    assert gate["passes"] is False


def test_4_not_fresh_closing_high_no_attempt():
    no_event = c6d.fixture_sol_breakout()
    no_event[30] = c6d._bar(30, 105.5)
    for i, close in enumerate((105.4, 105.3, 105.2, 105.1)):
        no_event[31 + i] = c6d._bar(31 + i, close)
    setups = c6d.scan_c6_setups(_aligned(sol=no_event), "SOLUSD")
    assert setups == []
    # the primitive: a close equal to the prior max is NOT fresh
    equal = c6d.fixture_sol_breakout()
    equal[30] = c6d._bar(30, 105.6)  # equals plateau max
    assert c6d.is_fresh_closing_high(equal, 30) is False


def test_5_evaluation_next_bar_only():
    setup = c6d.scan_c6_setups(_aligned(), "SOLUSD")[0]
    assert setup["event_time"] == c6d._stamp(30)
    assert setup["replay_start_time"] == c6d._stamp(31)
    assert setup["replay_start_time"] > setup["event_time"]
    # event on the very last bar has no evaluation bar -> rejected
    truncated = c6d.build_bars({
        "BTCUSD": c6d.fixture_flat(50.0, 31),
        "ETHUSD": c6d.fixture_flat(80.0, 31),
        "SOLUSD": c6d.fixture_sol_breakout()[:31]})
    last = c6d.scan_c6_setups(truncated, "SOLUSD")
    assert [s["status"] for s in last] == ["rejected_no_evaluation_bar"]
    assert last[0]["replay_start_time"] is None


def test_6_one_setup_per_event_bar():
    setups = c6d.scan_c6_setups(_aligned(), "SOLUSD")
    event_times = [s["event_time"] for s in setups]
    assert len(event_times) == len(set(event_times))  # one per bar
    assert len(setups) == 1  # exactly the single event bar


def test_7_not_delayed_pullback_resumption():
    # structural proof: entry happens AT the fresh-high event bar, not
    # after a pullback; no pullback fields exist in the schema
    setup = c6d.scan_c6_setups(_aligned(), "SOLUSD")[0]
    assert setup["event_time"] == c6d._stamp(30)  # the high bar itself
    assert setup["entry_price"] == 106.5          # that bar's close
    for forbidden_field in ("pullback_low", "pullback_high",
                            "pullback_bar_count",
                            "resumption_bar_time_utc"):
        assert forbidden_field not in c6d.C6_SETUP_REQUIRED_FIELDS
    record = c6d.build_c6_detector_spec_contract()
    assert record["not_a_delayed_pullback_resumption"] is True
    assert record["entry_at_event_bar_close"] is True


def test_8_wider_stop_max_rule_exact():
    # structure wider
    stop = c6d.compute_stop(106.5, 105.0, 0.5)
    assert stop["stop_distance"] == max(1.5 * 0.5, 106.5 - 105.0)
    assert stop["stop_distance"] == 1.5
    assert stop["stop_price"] == 105.0
    # ATR wider
    wide_atr = c6d.compute_stop(100.0, 99.9, 1.0)
    assert wide_atr["stop_distance"] == 1.5
    assert wide_atr["stop_price"] == 98.5
    # a min(...) mutation would differ in both cases
    assert min(1.5 * 0.5, 106.5 - 105.0) != stop["stop_distance"]
    assert min(1.5 * 1.0, 100.0 - 99.9) != wide_atr["stop_distance"]
    assert c6d.ATR_LENGTH == 14
    assert c6d.ATR_MULTIPLIER == 1.5
    assert c6d.STRUCTURE_LOOKBACK_BARS == 10


def test_9_invalid_stop_geometry_rejected():
    bad = c6d.compute_stop(100.0, 101.0, 0.0)  # negative structure, 0 atr
    assert bad["valid"] is False
    zero = c6d.compute_stop(100.0, 100.0, 0.0)
    assert zero["valid"] is False


def test_10_floor_81bps_before_replay_eligibility():
    assert c6d.TARGET_DISTANCE_FLOOR_BPS == 81.0
    tiny = c6d.geometry_floor_by_variant(100.0, 0.10)  # 4r = 40 bps
    assert tiny["floor_pass"] == {"2r": False, "3r": False, "4r": False}
    assert tiny["any_variant_passes"] is False
    partial = c6d.geometry_floor_by_variant(100.0, 0.28)
    assert partial["floor_pass"] == {"2r": False, "3r": True,
                                     "4r": True}
    full = c6d.geometry_floor_by_variant(100.0, 0.50)
    assert full["floor_pass"] == {"2r": True, "3r": True, "4r": True}
    record = c6d.build_c6_detector_spec_contract()
    assert record["floor_checked_before_replay_eligibility"] is True


def test_11_fee_27bps_preserved():
    assert c6d.FEE_ROUND_TRIP_BPS == 27.0
    assert 27.0 * 3 == 81.0
    record = c6d.build_c6_detector_spec_contract()
    assert record["fee_round_trip_bps"] == 27.0
    assert record["no_maker_rebate_no_zero_fee"] is True


def test_12_universe_enforced():
    with pytest.raises(ValueError):
        c6d.scan_c6_setups(_aligned(), "DOGEUSD")
    incomplete = {"BTCUSD": c6d.fixture_flat(50.0),
                  "SOLUSD": c6d.fixture_sol_breakout()}
    with pytest.raises(ValueError):
        c6d.scan_c6_setups(incomplete, "SOLUSD")
    misaligned = _aligned()
    misaligned["BTCUSD"] = misaligned["BTCUSD"][:-1]
    with pytest.raises(ValueError):
        c6d.scan_c6_setups(misaligned, "SOLUSD")


def test_13_contract_record_tamper_invalidates():
    for field, value in (
            ("universe", ["BTCUSD", "ETHUSD"]),
            ("rs_lookback_bars", 10),
            ("closing_high_lookback_bars", 5),
            ("structure_lookback_bars", 5),
            ("ties_fail", False),
            ("rs_must_be_positive", False),
            ("atr_length", 7),
            ("atr_multiplier", 1.0),
            ("wider_stop_rule", "min(1.5 * atr14, entry - low)"),
            ("fee_round_trip_bps", 10.0),
            ("target_distance_floor_bps", 54.0),
            ("target_variants", ["2r", "8r"]),
            ("entry_at_event_bar_close", False),
            ("evaluation_starts_next_bar", False),
            ("one_setup_per_event_bar", False),
            ("not_a_delayed_pullback_resumption", False),
            ("setup_required_fields", ["setup_id"]),
            ("detector_statuses", ["accepted_for_replay_review"]),
            ("dry_run_uses_synthetic_fixtures_only", False),
            ("claims_profitability", True),
            ("runs_real_detection_now", True),
            ("live_gate_locked", False),
            ("verdict", "CANDIDATE_6_APPROVED")):
        tampered = c6d.build_c6_detector_spec_contract()
        tampered[field] = value
        assert c6d.validate_c6_detector_spec_contract(
            tampered)["valid"] is False, field


def test_14_no_execution_capability_and_locks():
    record = c6d.build_c6_detector_spec_contract()
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    assert "staged 15m candles" in record["future_real_run_data_source"]
    assert "separate human approval" in record[
        "future_real_run_data_source"]


def test_15_ast_purity_and_verdicts():
    assert c6d.VERDICT_C6D_READY == "CANDIDATE_6_DETECTOR_SPEC_READY"
    assert c6d.VERDICT_C6D_DRY_RUN_PASSED == (
        "CANDIDATE_6_DETECTOR_DRY_RUN_PASSED")
    assert c6d.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_6_DRY_RUN_REVIEW")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c6d.NEXT_REQUIRED_ACTION.upper(), banned
    assert c6d.get_candidate_6_detector_label() == c6d.C6D_LABEL
    assert "READ-ONLY" in c6d.C6D_LABEL
    assert "SYNTHETIC" in c6d.C6D_LABEL
    assert c6d.C6D_MODE == "RESEARCH_ONLY"
    src = open(c6d.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "random" not in src
    assert "now(" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "pathlib", "os", "io", "json", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "hashlib", "statistics",
                   "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))
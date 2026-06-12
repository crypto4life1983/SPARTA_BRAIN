"""Tests for the Candidate #5 detector spec + synthetic dry-run path.

Pure scanner proven on in-memory fixtures: ETH and SOL accepts; RS,
pullback, trigger, stop, and geometry-floor failures; target-variant
freeze; no-lookahead (future-bar mutation cannot change a past setup;
replay starts next bar only); per-variant same-symbol non-overlap
(reduce-only, cross-symbol non-blocking); purity and safety. Tamper
tests on every frozen numeric. Commander safety suite runs alongside."""

from __future__ import annotations

import ast

import pytest

import sparta_commander.eth_sol_relative_strength_pullback_continuation_detector_spec_contract as c5d


def test_contract_ready_and_chain_gated():
    record = c5d.build_c5_detector_spec_contract()
    assert record["verdict"] == c5d.VERDICT_C5D_READY
    assert record["blockers"] == []
    assert c5d.validate_c5_detector_spec_contract(record)["valid"] is True
    assert record["current_loop_stage"] == "detector_and_label_review"
    assert c5d.build_c5_detector_spec_contract() == record


def test_dry_run_passes_and_fixture_counts():
    result = c5d.run_c5_detector_dry_run()
    assert result["verdict"] == c5d.VERDICT_C5D_DRY_RUN_PASSED
    assert result["failures"] == []
    assert result["uses_synthetic_fixtures_only"] is True
    assert result["reads_real_candles"] is False
    assert result["reads_any_files"] is False
    fixtures = result["fixtures"]
    assert fixtures["eth_accepted"]["accepted"] == 1
    assert fixtures["sol_accepted"]["accepted"] == 1
    assert fixtures["rs_not_stronger"]["accepted"] == 0
    assert fixtures["pullback_too_short"]["accepted"] == 0
    assert fixtures["pullback_too_long"]["accepted"] == 0
    assert fixtures["pullback_too_deep"]["accepted"] == 0
    assert fixtures["pullback_below_leg_low"]["accepted"] == 0
    assert fixtures["no_trigger_intrabar_only"]["attempts"] == 0
    assert fixtures["tight_floor_partial"]["accepted"] == 1
    assert fixtures["tight_floor_partial"]["floor_pass"] == {
        "2r": False, "3r": True, "4r": True}
    assert c5d.run_c5_detector_dry_run() == result  # determinism


def test_eth_and_sol_accepted_setup_records():
    flat = c5d.fixture_flat_other()
    for symbol in ("ETHUSD", "SOLUSD"):
        setups = c5d.scan_c5_setups(c5d.fixture_accepted(), flat, symbol)
        assert len(setups) == 1
        setup = setups[0]
        assert setup["status"] == "accepted_for_replay_review"
        for field in c5d.C5_SETUP_REQUIRED_FIELDS:
            assert field in setup, field
        assert setup["symbol"] == symbol
        assert setup["timeframe"] == "1h"
        assert setup["direction"] == "long"
        assert setup["entry_price"] == 110.7
        assert setup["pullback_low"] == 108.9
        assert setup["pullback_high"] == 110.6
        assert setup["up_leg_high"] == 110.8
        assert setup["up_leg_size"] > 0
        assert setup["return_20_symbol"] > 0
        assert setup["return_20_symbol"] > setup["return_20_other"]
        assert setup["stop_distance"] == 1.8  # structure wider than ATR
        assert setup["stop_price"] == 108.9
        assert setup["stop_price"] < setup["entry_price"]
        assert setup["target_2r"] == 114.3
        assert setup["target_3r"] == 116.1
        assert setup["target_4r"] == 117.9
        assert setup["target_distance_bps_2r"] > 81
        assert setup["geometry_floor_pass_by_variant"] == {
            "2r": True, "3r": True, "4r": True}
        assert setup["accepted_for_labeling_by_variant"] == {
            "2r": True, "3r": True, "4r": True}
        assert setup["rejection_reasons"] == []


def test_rs_gate_failures():
    flat = c5d.fixture_flat_other()
    # return <= 0: declining series
    declining = [c5d._bar(i, 120.0 - 0.5 * i, 120.2 - 0.5 * i,
                          119.6 - 0.5 * i, 120.0 - 0.5 * i)
                 for i in range(30)]
    gate = c5d.rs_gate(declining, flat, 25)
    assert gate["positive"] is False
    assert gate["passes"] is False
    # return <= other symbol
    gate2 = c5d.rs_gate(c5d.fixture_accepted(),
                        c5d.fixture_rs_stronger_other(), 25)
    assert gate2["positive"] is True
    assert gate2["stronger"] is False
    assert gate2["passes"] is False
    # full-scan: rs-not-stronger rejection emitted
    setups = c5d.scan_c5_setups(c5d.fixture_accepted(),
                                c5d.fixture_rs_stronger_other(), "ETHUSD")
    assert [s["status"] for s in setups] == ["rejected_rs_not_stronger"]
    # rs lookback mutation: a 10-bar lookback would change the return
    bars = c5d.fixture_accepted()
    assert c5d.compute_return_20(bars, 25) != (
        float(bars[25]["close"]) / float(bars[15]["close"]) - 1.0)
    assert c5d.compute_return_20(bars, 19) is None  # not enough history


def test_pullback_failures():
    flat = c5d.fixture_flat_other()
    short = c5d.scan_c5_setups(c5d.fixture_too_short(), flat, "ETHUSD")
    assert [s["status"] for s in short] == [
        "rejected_pullback_too_short"]
    long_run = c5d.scan_c5_setups(c5d.fixture_too_long(), flat, "ETHUSD")
    assert [s["status"] for s in long_run] == [
        "rejected_pullback_too_long"]
    deep = c5d.scan_c5_setups(c5d.fixture_too_deep(), flat, "ETHUSD")
    assert [s["status"] for s in deep] == ["rejected_pullback_too_deep"]
    below = c5d.scan_c5_setups(c5d.fixture_below_leg_low(), flat,
                               "ETHUSD")
    assert [s["status"] for s in below] == [
        "rejected_pullback_below_up_leg_low"]
    # depth threshold mutation: at 0.618 the deep fixture would pass
    bars = c5d.fixture_too_deep()
    depth = 110.8 - 107.0
    up_leg_size = 110.8 - 102.1
    assert depth > 0.382 * up_leg_size      # frozen rule rejects
    assert depth < 0.618 * up_leg_size      # looser rule would accept


def test_trigger_failures_and_close_only():
    flat = c5d.fixture_flat_other()
    intrabar = c5d.scan_c5_setups(
        c5d.fixture_no_trigger_intrabar_high_only(), flat, "ETHUSD")
    assert intrabar == []  # high pierced, close did not -> no attempt
    no_breakout = c5d.fixture_accepted()
    no_breakout[25] = c5d._bar(25, 109.1, 110.5, 109.0, 110.4)
    no_breakout[26] = c5d._bar(26, 110.4, 110.5, 109.9, 110.0)
    setups = c5d.scan_c5_setups(no_breakout, flat, "ETHUSD")
    assert all(s["status"] != "accepted_for_replay_review"
               for s in setups)


def test_stop_logic_wider_rule_and_invalid():
    # invalid when distance <= 0
    bad = c5d.compute_stop(100.0, 101.0, 0.0)
    assert bad["valid"] is False
    # WIDER rule: max(...) -- a min(...) mutation would differ
    stop = c5d.compute_stop(110.7, 108.9, 0.875)
    assert stop["valid"] is True
    assert stop["stop_distance"] == max(1.5 * 0.875, 110.7 - 108.9)
    assert round(stop["stop_distance"], 6) == 1.8
    mutated_min = min(1.5 * 0.875, 110.7 - 108.9)
    assert round(mutated_min, 6) == 1.3125  # min-rule would differ
    assert mutated_min != stop["stop_distance"]
    # ATR-side wider: tiny structure, big ATR
    wide_atr = c5d.compute_stop(100.0, 99.9, 1.0)
    assert wide_atr["stop_distance"] == 1.5
    assert wide_atr["stop_price"] == 98.5
    # ATR length/multiplier frozen
    assert c5d.ATR_LENGTH == 14
    assert c5d.ATR_MULTIPLIER == 1.5
    bars = c5d.fixture_accepted()
    assert c5d.compute_atr14(bars, 13) is None  # needs 14 + prior close


def test_geometry_floor_81bps_per_variant():
    assert c5d.FEE_ROUND_TRIP_BPS == 27.0
    assert c5d.TARGET_DISTANCE_FLOOR_BPS == 81.0
    assert 27.0 * 3 == 81.0
    # all variants fail when stop is 10 bps of entry (4r = 40 bps < 81)
    tiny = c5d.geometry_floor_by_variant(100.0, 0.10)
    assert tiny["target_distance_bps"]["4r"] == 40.0
    assert tiny["floor_pass"] == {"2r": False, "3r": False, "4r": False}
    assert tiny["any_variant_passes"] is False
    # partial: stop = 28 bps -> 2r 56 bps fails, 3r 84 / 4r 112 pass
    partial = c5d.geometry_floor_by_variant(100.0, 0.28)
    assert partial["target_distance_bps"]["2r"] == 56.0
    assert partial["floor_pass"]["2r"] is False
    assert partial["floor_pass"]["3r"] is True
    assert partial["floor_pass"]["4r"] is True
    # full pass: stop = 50 bps -> 2r 100 bps clears the floor
    full = c5d.geometry_floor_by_variant(100.0, 0.50)
    assert full["target_distance_bps"]["2r"] == 100.0
    assert full["floor_pass"] == {"2r": True, "3r": True, "4r": True}


def test_target_variants_frozen_2r_3r_4r_only():
    assert [name for name, _m in c5d.TARGET_VARIANTS] == [
        "2r", "3r", "4r"]
    assert [m for _n, m in c5d.TARGET_VARIANTS] == [2.0, 3.0, 4.0]
    floor = c5d.geometry_floor_by_variant(100.0, 1.0)
    assert sorted(floor["targets"]) == ["2r", "3r", "4r"]
    assert floor["targets"]["2r"] == 102.0
    assert floor["targets"]["3r"] == 103.0
    assert floor["targets"]["4r"] == 104.0
    setup = c5d.scan_c5_setups(c5d.fixture_accepted(),
                               c5d.fixture_flat_other(), "ETHUSD")[0]
    assert sorted(setup["geometry_floor_pass_by_variant"]) == [
        "2r", "3r", "4r"]


def test_no_lookahead_future_mutation_and_replay_start():
    flat = c5d.fixture_flat_other()
    bars = c5d.fixture_accepted()
    base = c5d.scan_c5_setups(bars, flat, "ETHUSD")[0]
    # mutate a FUTURE bar wildly: the past setup must be unchanged
    mutated = [dict(b) for b in bars]
    mutated[28] = c5d._bar(28, 50.0, 200.0, 10.0, 150.0)
    after = [s for s in c5d.scan_c5_setups(mutated, flat, "ETHUSD")
             if s["setup_id"] == base["setup_id"]]
    assert len(after) == 1
    assert after[0] == base
    # replay starts on the NEXT bar only
    assert base["trigger_time"] == c5d._stamp(25)
    assert base["replay_start_time"] == c5d._stamp(26)
    assert base["replay_start_time"] > base["trigger_time"]
    # a trigger on the last bar has no next bar -> not accepted
    truncated = bars[:26]
    last = c5d.scan_c5_setups(truncated, flat, "ETHUSD")
    assert all(s["status"] != "accepted_for_replay_review"
               for s in last)
    assert any("no_next_bar_for_evaluation" in s["rejection_reasons"]
               for s in last)


def test_non_overlap_reduce_only_and_cross_symbol():
    rows = [
        {"symbol": "ETHUSD", "trigger_time": "T01",
         "exit_time_by_variant": {"2r": "T05"}},
        {"symbol": "ETHUSD", "trigger_time": "T03",   # overlaps T01 hold
         "exit_time_by_variant": {"2r": "T08"}},
        {"symbol": "ETHUSD", "trigger_time": "T06",   # after T05 exit
         "exit_time_by_variant": {"2r": "T09"}},
        {"symbol": "SOLUSD", "trigger_time": "T02",   # other symbol
         "exit_time_by_variant": {"2r": "T04"}},
    ]
    result = c5d.apply_same_symbol_non_overlap(rows, "2r")
    kept_ids = [(r["symbol"], r["trigger_time"]) for r in result["kept"]]
    removed_ids = [(r["symbol"], r["trigger_time"])
                   for r in result["removed"]]
    assert ("ETHUSD", "T01") in kept_ids
    assert ("ETHUSD", "T06") in kept_ids
    assert ("SOLUSD", "T02") in kept_ids  # different symbol not blocked
    assert removed_ids == [("ETHUSD", "T03")]
    assert len(result["kept"]) + len(result["removed"]) == len(rows)
    assert len(result["kept"]) <= len(rows)  # reduce-or-keep, never add
    # deterministic
    again = c5d.apply_same_symbol_non_overlap(rows, "2r")
    assert again == result


def test_contract_record_tamper_invalidates():
    for field, value in (
            ("rs_lookback_bars", 10),
            ("pullback_min_bars", 1),
            ("pullback_max_bars", 12),
            ("max_pullback_depth_fraction", 0.618),
            ("atr_length", 7),
            ("atr_multiplier", 1.0),
            ("wider_stop_rule",
             "min(atr_stop_distance, structure_stop_distance)"),
            ("fee_round_trip_bps", 10.0),
            ("target_distance_floor_bps", 54.0),
            ("target_variants", ["2r", "3r", "4r", "8r"]),
            ("non_overlap_same_symbol_per_variant_reduce_only", False),
            ("replay_starts_next_bar_after_trigger_close", False),
            ("setup_required_fields", ["setup_id"]),
            ("detector_statuses", ["accepted_for_replay_review"]),
            ("dry_run_uses_synthetic_fixtures_only", False),
            ("claims_profitability", True),
            ("auto_pushes", True),
            ("runs_real_detection_now", True),
            ("live_gate_locked", False),
            ("verdict", "CANDIDATE_5_APPROVED")):
        tampered = c5d.build_c5_detector_spec_contract()
        tampered[field] = value
        assert c5d.validate_c5_detector_spec_contract(
            tampered)["valid"] is False, field


def test_symbol_scope_and_safety_flags():
    with pytest.raises(ValueError):
        c5d.scan_c5_setups(c5d.fixture_accepted(),
                           c5d.fixture_flat_other(), "BTCUSD")
    record = c5d.build_c5_detector_spec_contract()
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True


def test_verdict_strings_and_module_purity():
    assert c5d.VERDICT_C5D_READY == "CANDIDATE_5_DETECTOR_SPEC_READY"
    assert c5d.VERDICT_C5D_DRY_RUN_PASSED == (
        "CANDIDATE_5_DETECTOR_DRY_RUN_PASSED")
    assert c5d.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_5_DRY_RUN_REVIEW")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c5d.NEXT_REQUIRED_ACTION.upper(), banned
    assert c5d.get_candidate_5_detector_label() == c5d.C5D_LABEL
    assert "READ-ONLY" in c5d.C5D_LABEL
    assert "SYNTHETIC" in c5d.C5D_LABEL
    assert c5d.C5D_MODE == "RESEARCH_ONLY"
    src = open(c5d.__file__, encoding="utf-8").read()
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
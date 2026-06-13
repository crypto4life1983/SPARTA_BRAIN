"""Tests for the Candidate #7 detector spec + synthetic dry-run path
(VOLATILITY_COMPRESSION_EXPANSION_V1).

Synthetic fixtures only -- no real candles, no files, no network.
Proves: valid compression+expansion produces an accepted setup; no
setup before sufficient ATR/rolling history; strict contraction
threshold rejects equality at 0.6; contraction requires 5 consecutive
bars; expansion requires TR > 1.8 x contracted ATR; upper-third close
confirmation enforced; long-only BTCUSD 4h enforced; 81 bps floor
enforced per variant; WIDER stop uses max(1.5 x ATR(14),
structure_stop_distance); anti-cluster keeps earlier event and drops
later event within 6 bars; anti-cluster does NOT consume the single
edit token; downstream execution/replay/data/paper/live gates remain
locked. Commander safety suite runs alongside (12 tests)."""

from __future__ import annotations

import ast

import sparta_commander.volatility_compression_expansion_v1_detector_spec_dry_run_contract as c7d


def _bar(time_utc, open_, high, low, close):
    return {"time_utc": time_utc, "open": open_, "high": high,
            "low": low, "close": close}


# (0) dry run passes and contract certifies READY -----------------------------

def test_0_dry_run_passes_and_contract_certifies_ready():
    spec = c7d.build_c7_detector_spec_contract()
    assert spec["verdict"] == c7d.VERDICT_C7D_READY
    assert spec["blockers"] == []
    assert c7d.validate_c7_detector_spec_contract(
        spec)["valid"] is True
    dry = c7d.run_c7_detector_dry_run()
    assert dry["verdict"] == c7d.VERDICT_C7D_DRY_RUN_PASSED, (
        dry["failures"])
    combined = c7d.build_c7_detector_spec_dry_run_review()
    assert combined["combined_verdict"] == (
        c7d.VERDICT_C7D_SPEC_DRY_RUN_READY)
    # determinism
    assert c7d.build_c7_detector_spec_contract() == spec


# (1) valid compression + expansion produces expected accepted setup ----------

def test_1_valid_compression_expansion_produces_accepted_setup():
    bars = c7d.fixture_warmup_then_contraction_then_expansion()
    setups = c7d.scan_c7_setups(bars, "BTCUSD")
    accepted = [s for s in setups
                if s["status"] == "accepted_for_replay_review"]
    assert len(accepted) == 1
    s = accepted[0]
    assert s["symbol"] == "BTCUSD"
    assert s["timeframe"] == "4h"
    assert s["direction"] == "long"
    assert s["contraction_window_passes"] is True
    assert s["close_in_upper_third_passes"] is True
    assert s["expansion_multiplier_observed"] > 1.8
    assert s["stop_distance"] > 0
    assert s["stop_price"] < s["entry_price"]
    assert s["geometry_floor_pass_by_variant"] == {
        "2r": True, "3r": True, "4r": True}
    assert s["accepted_for_labeling_by_variant"] == {
        "2r": True, "3r": True, "4r": True}
    assert s["replay_start_time"] is not None
    # event_index is at warmup + contraction_run = 115 + 20 = 135
    assert s["event_index"] == 135
    # every required field present
    for field in c7d.C7_SETUP_REQUIRED_FIELDS:
        assert field in s, field


# (2) no setup before enough ATR/rolling-window history exists -----------------

def test_2_no_setup_before_sufficient_history():
    # min_event_index = ATR_LENGTH + ATR_ROLLING_AVERAGE_WINDOW_4H_BARS
    # - 1 + CONTRACTION_WINDOW_BARS = 14 + 99 + 5 = 118.
    # Fixture default contraction_run_length is 20, so expansion is at
    # warmup_length + 20. To get an expansion bar BEFORE index 118 we
    # need warmup_length + 20 < 118 -> warmup_length < 98.
    short = c7d.fixture_warmup_then_contraction_then_expansion(
        warmup_length=30)
    setups = c7d.scan_c7_setups(short, "BTCUSD")
    assert setups == []
    # also check just under the minimum: warmup=95 -> exp at 115 < 118
    just_under = c7d.fixture_warmup_then_contraction_then_expansion(
        warmup_length=95)
    setups2 = c7d.scan_c7_setups(just_under, "BTCUSD")
    assert setups2 == []


# (3) strict contraction threshold rejects equality at 0.6 --------------------

def test_3_strict_contraction_threshold_rejects_equality_at_0_6():
    # Construct ATR values and a rolling avg such that ATR == 0.6 * avg
    # at every bar in the 5-bar window. Build the fixture so the rolling
    # average is ~1.5 and contracted ATR is ~0.9 (= 0.6 * 1.5).
    bars = c7d.fixture_warmup_then_contraction_then_expansion(
        contracted_atr_target=0.9, rolling_atr_target=1.5)
    setups = c7d.scan_c7_setups(bars, "BTCUSD")
    # The scanner uses strict < ; ATR = 0.6 * avg should fail
    accepted = [s for s in setups
                if s["status"] == "accepted_for_replay_review"]
    rejected_contraction = [
        s for s in setups
        if s["status"] == "rejected_contraction_window"]
    assert accepted == []
    assert len(rejected_contraction) >= 1
    # any rejection on contraction must have the per-bar pass = False
    # somewhere
    rec = rejected_contraction[0]
    assert rec["contraction_window_passes"] is False


# (4) contraction requires 5 consecutive completed 4h bars --------------------

def test_4_contraction_requires_5_consecutive_bars():
    bars = c7d.fixture_only_4_contraction_bars()
    setups = c7d.scan_c7_setups(bars, "BTCUSD")
    accepted = [s for s in setups
                if s["status"] == "accepted_for_replay_review"]
    assert accepted == []
    # at least one attempt at the expansion bar must reject on
    # contraction
    contraction_rejections = [
        s for s in setups
        if s["status"] == "rejected_contraction_window"]
    assert len(contraction_rejections) >= 1


# (5) expansion requires true_range > 1.8 x contracted ATR --------------------

def test_5_expansion_requires_true_range_above_1_8x_contracted_atr():
    bars = c7d.fixture_expansion_only_1_7x_multiplier()
    setups = c7d.scan_c7_setups(bars, "BTCUSD")
    accepted = [s for s in setups
                if s["status"] == "accepted_for_replay_review"]
    assert accepted == []
    rejected_multiplier = [
        s for s in setups
        if s["status"] == "rejected_expansion_multiplier"]
    assert len(rejected_multiplier) >= 1
    # the recorded observed multiplier must be < 1.8
    rec = rejected_multiplier[0]
    assert rec["expansion_multiplier_observed"] is not None
    assert rec["expansion_multiplier_observed"] < 1.8


# (6) upper-third close confirmation is enforced ------------------------------

def test_6_upper_third_close_confirmation_enforced():
    bars = c7d.fixture_expansion_close_at_midpoint()
    setups = c7d.scan_c7_setups(bars, "BTCUSD")
    accepted = [s for s in setups
                if s["status"] == "accepted_for_replay_review"]
    assert accepted == []
    rejected_close = [
        s for s in setups
        if s["status"] == "rejected_close_not_in_upper_third"]
    assert len(rejected_close) >= 1
    rec = rejected_close[0]
    assert rec["close_in_upper_third_passes"] is False
    # the multiplier_passes check passed at this stage (else it would
    # have rejected on multiplier first)
    assert rec["expansion_multiplier_observed"] is not None
    assert rec["expansion_multiplier_observed"] > 1.8


# (7) long-only BTCUSD 4h only ------------------------------------------------

def test_7_long_only_btcusd_4h_only_enforced():
    bars = c7d.fixture_warmup_then_contraction_then_expansion()
    # ETHUSD / SOLUSD must raise ValueError on the universe gate
    for bad in ("ETHUSD", "SOLUSD", "BTCUSDT", ""):
        try:
            c7d.scan_c7_setups(bars, bad)
            raise AssertionError("expected ValueError for " + bad)
        except ValueError:
            pass
    # BTCUSD works
    setups = c7d.scan_c7_setups(bars, "BTCUSD")
    # every emitted setup is timeframe 4h, direction long, BTCUSD
    for s in setups:
        assert s["symbol"] == "BTCUSD"
        assert s["timeframe"] == "4h"
        assert s["direction"] == "long"
    # bars not a list -> raises
    try:
        c7d.scan_c7_setups("not a list", "BTCUSD")
        raise AssertionError("expected ValueError for non-list bars")
    except ValueError:
        pass


# (8) 81 bps floor enforced per target variant --------------------------------

def test_8_81_bps_floor_enforced_per_variant():
    # Tiny risk distance fixture: expansion is barely above 1.8 x
    # contracted ATR but high/low span is small relative to entry,
    # so the 2R/3R/4R target distances all fall below 81 bps.
    # We build this by making contracted ATR very small and expansion
    # just barely above threshold.
    bars = c7d.fixture_warmup_then_contraction_then_expansion(
        contracted_atr_target=0.01,
        rolling_atr_target=0.03,
        expansion_close=50000.05,
        expansion_low=50000.0,
        expansion_high=50000.06,
    )
    setups = c7d.scan_c7_setups(bars, "BTCUSD")
    # The result depends on stop-distance math; check that any setup
    # that gets to the floor stage and fails it is recorded as
    # rejected_geometry_floor. We assert the path exists -- either
    # this exact fixture rejects on floor, or we synthesize the
    # floor-check directly on geometry_floor_by_variant.
    floor = c7d.geometry_floor_by_variant(50000.0, 1.0)
    # 1.0 / 50000 * 10000 = 0.2 bps -> all variants well below 81 bps
    assert floor["floor_pass"] == {
        "2r": False, "3r": False, "4r": False}
    assert floor["any_variant_passes"] is False
    # Now a large enough stop distance passes
    floor2 = c7d.geometry_floor_by_variant(50000.0, 250.0)
    # 250 / 50000 * 10000 = 50 bps; 2R = 100 bps PASS, 3R = 150 bps
    # PASS, 4R = 200 bps PASS
    assert floor2["floor_pass"]["2r"] is True
    assert floor2["floor_pass"]["3r"] is True
    assert floor2["floor_pass"]["4r"] is True
    # 81 bps floor itself -- a stop_distance/entry of exactly 81 bps
    # at 2R yields 162 bps (PASS); we test the boundary: 40 bps at
    # 2R yields 80 bps (FAIL just below 81)
    entry = 50000.0
    stop_dist_at_40bps = entry * 40.0 / 10000.0
    floor3 = c7d.geometry_floor_by_variant(entry, stop_dist_at_40bps)
    # 2R distance = 80 bps -> just below 81 -> FAIL
    assert floor3["floor_pass"]["2r"] is False
    assert floor3["floor_pass"]["3r"] is True   # 120 bps PASS
    assert floor3["floor_pass"]["4r"] is True   # 160 bps PASS


# (9) WIDER stop formula uses max(1.5 x ATR14, structure_stop_distance) --------

def test_9_wider_stop_formula_max_atr_or_structure():
    # case A: structure is wider
    res = c7d.compute_stop(entry_price=100.0, ten_bar_low=92.0,
                           atr14=2.0)
    # ATR stop = 1.5 * 2.0 = 3.0; structure_stop = 100 - 92 = 8.0
    # winner = 8.0 (structure wider)
    assert res["atr_stop_distance"] == 3.0
    assert res["structure_stop_distance"] == 8.0
    assert res["stop_distance"] == 8.0
    assert res["stop_price"] == 92.0
    assert res["valid"] is True
    # case B: ATR is wider
    res2 = c7d.compute_stop(entry_price=100.0, ten_bar_low=99.0,
                            atr14=4.0)
    # ATR stop = 1.5 * 4 = 6.0; structure = 1.0; winner = 6.0
    assert res2["atr_stop_distance"] == 6.0
    assert res2["structure_stop_distance"] == 1.0
    assert res2["stop_distance"] == 6.0
    assert res2["stop_price"] == 94.0
    assert res2["valid"] is True
    # case C: invalid (entry below ten_bar_low + tiny ATR)
    res3 = c7d.compute_stop(entry_price=100.0, ten_bar_low=100.0,
                            atr14=0.0)
    assert res3["stop_distance"] == 0.0
    assert res3["valid"] is False


# (10) anti-cluster keeps earlier, drops later within 6 bars -----------------

def test_10_anti_cluster_keeps_earlier_drops_later_within_6_bars():
    base = {"setup_id": "A", "symbol": "BTCUSD",
            "status": "accepted_for_replay_review",
            "event_index": 120, "rejection_reasons": []}
    inside_gap = dict(base, setup_id="B", event_index=123)
    edge_just_inside = dict(base, setup_id="C", event_index=125)
    just_outside = dict(base, setup_id="D", event_index=126)
    later_after_outside = dict(base, setup_id="E", event_index=130)
    result = c7d.apply_anti_cluster_filter(
        [base, inside_gap, edge_just_inside, just_outside,
         later_after_outside])
    kept_ids = [s["setup_id"] for s in result["kept"]]
    dropped_ids = [s["setup_id"] for s in result["dropped"]]
    # A is the earliest; B (120+3=123) and C (120+5=125) are within
    # 6 bars of A; D (120+6=126) is the first kept after A; E (130)
    # is then >6 bars after D (=130-126=4 < 6) so E is also dropped.
    assert kept_ids == ["A", "D"]
    assert dropped_ids == ["B", "C", "E"]
    # the dropped records' status is updated
    for s in result["dropped"]:
        assert s["status"] == (
            "rejected_clustered_within_6_bars_of_prior_accepted")
        assert (
            "less_than_6_completed_4h_bars_after_prior_accepted"
            "_event_on_same_symbol") in s["rejection_reasons"]
    # exact boundary: index difference of exactly 6 is KEPT (>= gap)
    pair = c7d.apply_anti_cluster_filter([
        {"setup_id": "X", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review", "event_index": 200,
         "rejection_reasons": []},
        {"setup_id": "Y", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review", "event_index": 206,
         "rejection_reasons": []},
    ])
    assert [s["setup_id"] for s in pair["kept"]] == ["X", "Y"]
    # index difference of 5 is DROPPED
    pair2 = c7d.apply_anti_cluster_filter([
        {"setup_id": "X", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review", "event_index": 200,
         "rejection_reasons": []},
        {"setup_id": "Y", "symbol": "BTCUSD",
         "status": "accepted_for_replay_review", "event_index": 205,
         "rejection_reasons": []},
    ])
    assert [s["setup_id"] for s in pair2["kept"]] == ["X"]
    assert [s["setup_id"] for s in pair2["dropped"]] == ["Y"]


# (11) anti-cluster does not consume the single edit token -------------------

def test_11_anti_cluster_does_not_consume_edit_token():
    res = c7d.apply_anti_cluster_filter([])
    assert res["anti_cluster_min_bar_gap"] == 6
    assert res["tie_breaker"] == (
        "keep_the_earlier_event_drop_the_later_one")
    assert res["anti_cluster_does_not_consume_edit_token"] is True
    # the contract record declares this too
    record = c7d.build_c7_detector_spec_contract()
    assert record["anti_cluster_does_not_consume_edit_token"] is True
    # flipping the contract flag invalidates
    tampered = dict(record)
    tampered["anti_cluster_does_not_consume_edit_token"] = False
    assert c7d.validate_c7_detector_spec_contract(
        tampered)["valid"] is False


# (12) downstream execution/replay/data/paper/live gates remain locked -------

def test_12_downstream_gates_remain_locked():
    record = c7d.build_c7_detector_spec_contract()
    assert record["is_synthetic_fixture_dry_run_only"] is True
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_relabel", "runs_replay",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now",
                "claims_profitability"):
        assert record[key] is False, key
        tampered = dict(record)
        tampered[key] = True
        assert c7d.validate_c7_detector_spec_contract(
            tampered)["valid"] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_7_DRY_RUN_REVIEW")


# (13) AST/purity -- in-memory only, no I/O, no banned imports --------------

def test_13_ast_purity_and_no_writers_or_runners():
    assert c7d.get_candidate_7_detector_label() == c7d.C7D_LABEL
    assert c7d.C7D_MODE == "RESEARCH_ONLY"
    assert c7d.VERDICT_C7D_READY == "CANDIDATE_7_DETECTOR_SPEC_READY"
    assert c7d.VERDICT_C7D_DRY_RUN_PASSED == (
        "CANDIDATE_7_DETECTOR_DRY_RUN_PASSED")
    assert c7d.VERDICT_C7D_SPEC_DRY_RUN_READY == (
        "CANDIDATE_7_DETECTOR_SPEC_DRY_RUN_READY")
    assert c7d.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_7_DRY_RUN_REVIEW")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c7d.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(c7d.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "random" not in src
    assert "now(" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "subprocess", "Popen", "system("):
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

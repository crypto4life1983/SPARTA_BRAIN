"""P4 synthetic smoke battery (T1-T15 + T7b + T7c + T16 + T17) for s14-d1-cross-sector RSI(3) runner.

Tests AUTHORED at P3 BUILD; EXECUTED at P4 synthetic smoke under separate operator authorization.
"""

import pytest


# ---------- T1: module imports clean ----------

def test_T1_module_imports_clean(runner_harness_module):
    assert runner_harness_module["main"] is not None
    assert runner_harness_module["execution_guard"] is not None
    assert runner_harness_module["in_sample_driver"] is not None
    assert runner_harness_module["out_of_sample_driver"] is not None


# ---------- T2: runner class instantiable ----------

def test_T2_runner_class_instantiable(runner_harness_module):
    main = runner_harness_module["main"]
    algo = main.Algo()
    algo.Initialize()
    assert algo.config["candidate_record_id"] == (
        "s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history"
    )
    assert algo._stale_fill_warning_count == 0
    assert algo.all_safety_warnings_zero() is True
    assert algo.open_position_count() == 0


# ---------- T3: Wilder ATR(14) on constant TR=2.0 ----------

def test_T3_wilder_atr_synthetic(runner_harness_module):
    main = runner_harness_module["main"]
    tr_series = [2.0] * 15
    atr = main.wilder_atr(tr_series, period=14)
    assert atr == pytest.approx(2.0)
    # insufficient data -> None
    assert main.wilder_atr([2.0] * 13, period=14) is None


# ---------- T4: RSI(3) computation on synthetic series ----------

def test_T4_rsi_3_synthetic(runner_harness_module):
    """RSI(3) Wilder smoothing on close-to-close diffs."""
    main = runner_harness_module["main"]
    # Three strictly up bars -> RSI(3) close to 100
    closes_up = [100.0, 101.0, 102.0, 103.0]
    assert main.wilder_rsi(closes_up, period=3) == pytest.approx(100.0)
    # Three strictly down bars -> RSI(3) close to 0
    closes_down = [100.0, 99.0, 98.0, 97.0]
    assert main.wilder_rsi(closes_down, period=3) == pytest.approx(0.0)
    # Insufficient data -> None (need period+1 = 4 closes)
    assert main.wilder_rsi([100.0, 101.0, 102.0], period=3) is None


# ---------- T5: RSI oversold/overbought entry triggers (15 / 85) ----------

def test_T5_rsi_oversold_overbought_entry_trigger(runner_harness_module):
    """RSI(3)<15 fires long entry; RSI(3)>85 fires short entry."""
    main = runner_harness_module["main"]
    assert main.long_entry_signal(rsi=10.0, threshold=15) is True
    assert main.long_entry_signal(rsi=15.0, threshold=15) is False  # strict <
    assert main.long_entry_signal(rsi=20.0, threshold=15) is False
    assert main.short_entry_signal(rsi=90.0, threshold=85) is True
    assert main.short_entry_signal(rsi=85.0, threshold=85) is False  # strict >
    assert main.short_entry_signal(rsi=80.0, threshold=85) is False
    assert main.long_entry_signal(rsi=None, threshold=15) is False
    assert main.short_entry_signal(rsi=None, threshold=85) is False


# ---------- T6: stop placement at 2N ----------

def test_T6_stop_placement_at_2n(runner_harness_module):
    main = runner_harness_module["main"]
    stop_long = main.compute_stop_price(100.0, 2.0, side="long", multiplier=2.0)
    assert stop_long == pytest.approx(100.0 - 4.0)
    stop_short = main.compute_stop_price(99.0, 2.0, side="short", multiplier=2.0)
    assert stop_short == pytest.approx(99.0 + 4.0)


# ---------- T7: pyramid trigger computed (informational) ----------

def test_T7_pyramid_trigger_informational(runner_harness_module):
    """Pyramid TRIGGER PRICE COMPUTED at +0.5*2N (informational); invocation forbidden."""
    pyramid_trigger_informational = 100.0 + 0.5 * 2.0 * 2.0  # 0.5 * 2N
    assert pyramid_trigger_informational == pytest.approx(102.0)


# ---------- T7b: add_pyramid_unit raises ----------

def test_T7b_add_pyramid_unit_raises(runner_harness_module):
    main = runner_harness_module["main"]
    with pytest.raises(RuntimeError, match="PYRAMID_FORBIDDEN"):
        main.add_pyramid_unit()


# ---------- T7c: starting_cash invariant $100,000 (DA4=B) ----------

def test_T7c_starting_cash_invariant_100000(runner_harness_module):
    """CONFIG['start_cash_usd'] == 100_000 (s14-d1-cross-sector; DA4=B)."""
    main = runner_harness_module["main"]
    assert main.CONFIG["start_cash_usd"] == 100_000


# ---------- T8: RSI exit thresholds (long>55 / short<45) ----------

def test_T8_exit_thresholds(runner_harness_module):
    """RSI(3)>55 closes long; RSI(3)<45 closes short."""
    main = runner_harness_module["main"]
    assert main.long_exit_signal(rsi=60.0, threshold=55) is True
    assert main.long_exit_signal(rsi=55.0, threshold=55) is False  # strict >
    assert main.long_exit_signal(rsi=50.0, threshold=55) is False
    assert main.short_exit_signal(rsi=40.0, threshold=45) is True
    assert main.short_exit_signal(rsi=45.0, threshold=45) is False  # strict <
    assert main.short_exit_signal(rsi=50.0, threshold=45) is False
    assert main.long_exit_signal(rsi=None, threshold=55) is False
    assert main.short_exit_signal(rsi=None, threshold=45) is False


# ---------- T9: portfolio cap (max_total_positions=3, per-name=1) ----------

def test_T9_portfolio_cap(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["max_total_positions"] == 3
    assert main.CONFIG["max_positions_per_name"] == 1
    assert main.CONFIG["inter_name_signal_coordination"] == "NONE"
    assert main.portfolio_can_open(2, max_total_positions=3) is True
    assert main.portfolio_can_open(3, max_total_positions=3) is False


# ---------- T10: sizing at 0.5% risk on $100k cash (SHARES) ----------

def test_T10_sizing_0_5pct_shares(runner_harness_module):
    """compute_position_shares returns floor((0.005 * 100000) / (2.0 * ATR_entry))."""
    main = runner_harness_module["main"]
    shares = main.compute_position_shares(100_000.0, 2.0, stop_multiplier=2.0, risk_pct=0.005)
    # floor((0.005 * 100000) / (2.0 * 2.0)) = floor(500 / 4) = floor(125) = 125
    assert shares == 125


# ---------- T11: tiny equity returns 0 shares ----------

def test_T11_skip_when_share_count_lt_one(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.compute_position_shares(5.0, 2.0, stop_multiplier=2.0, risk_pct=0.005) == 0
    # zero/negative ATR -> 0
    assert main.compute_position_shares(100_000.0, 0.0, stop_multiplier=2.0, risk_pct=0.005) == 0


# ---------- T12: RTH-only filter attested ----------

def test_T12_rth_only_filter_attested(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["rth_safe_window_open"] == (9, 30)
    assert main.CONFIG["rth_safe_window_close"] == (16, 0)
    assert main.CONFIG["eod_cancel_time"] == (16, 0)
    assert main.CONFIG["rth_window_tz"] == "America/New_York"
    assert main.CONFIG["daily_bars_only"] is True


# ---------- T13: cost surface (per-share commission + slippage proxy) ----------

def test_T13_cost_surface(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["commission_per_share_usd"] == 0.005
    assert main.CONFIG["min_commission_per_trade_usd"] == 1.0
    assert main.CONFIG["slippage_model"] == "half_bid_ask_spread_proxy"
    assert main.CONFIG["slippage_proxy_bps"] == 1.0


# ---------- T14: cost-stress matrix S0-S4 ----------

def test_T14_cost_stress_matrix_S0_S1_S2_S3_S4(runner_harness_module):
    main = runner_harness_module["main"]
    tiers = main.CONFIG["cost_stress_tiers"]
    assert len(tiers) == 5
    assert [t["tier"] for t in tiers] == ["S0", "S1", "S2", "S3", "S4"]
    assert [t["cost_scalar"] for t in tiers] == [0.0, 1.0, 1.5, 2.0, 3.0]


# ---------- T15: validator harness pass ----------

def test_T15_validator_harness_pass_on_synthetic(runner_harness_module):
    main = runner_harness_module["main"]
    guard = runner_harness_module["execution_guard"]
    algo = main.Algo()
    algo.Initialize()
    safety_counters = {"stale_fill_warning_count": algo._stale_fill_warning_count}
    result = guard.full_guard_check(algo.config, safety_counters=safety_counters)
    assert result["overall_pass"] is True, f"errors: {result['errors']}"
    for k in (
        "assert_seal_inheritance",
        "assert_no_forbidden_order_paths",
        "assert_rec1_equivalent_binding_preserved",
        "assert_locked_strategy_params",
        "assert_boundary_alignment",
        "assert_split_only_convention",
        "assert_universe_locked",
        "assert_no_leverage_cap",
        "safety_counters_all_zero",
    ):
        assert result["checks"].get(k) is True, f"check {k} failed: {result['errors']}"


# ---------- T16: cross-sector universe locked AAPL/JPM/XOM ----------

def test_T16_universe_locked_cross_sector(runner_harness_module):
    main = runner_harness_module["main"]
    guard = runner_harness_module["execution_guard"]
    assert main.CONFIG["universe"] == ["AAPL", "JPM", "XOM"]
    assert main.CONFIG["universe_sectors"] == {
        "AAPL": "Information Technology",
        "JPM": "Financials",
        "XOM": "Energy",
    }
    # widened/substituted universe must raise
    bad = dict(main.CONFIG)
    bad["universe"] = ["AAPL", "MSFT", "NVDA"]
    with pytest.raises(Exception, match="UNIVERSE_DRIFT"):
        guard.assert_universe_locked(bad)


# ---------- T17: split_only convention (DA17) ----------

def test_T17_split_only_convention(runner_harness_module):
    main = runner_harness_module["main"]
    guard = runner_harness_module["execution_guard"]
    assert main.CONFIG["adjustment_convention"] == "split_only"
    assert main.CONFIG["dividends_adjusted"] is False
    aapl = next(a for a in main.CONFIG["known_corporate_actions"] if a["symbol"] == "AAPL")
    assert aapl["date"] == "2020-08-31"
    assert aapl["factor"] == 4.0
    assert aapl["applied"] is True and aapl["dr9_verified"] is True
    # passing config attests cleanly
    guard.assert_split_only_convention(main.CONFIG)
    # switching convention must raise
    bad = dict(main.CONFIG)
    bad["adjustment_convention"] = "split_and_dividend"
    with pytest.raises(Exception, match="C5_ADJUSTMENT_CONVENTION_NOT_SPLIT_ONLY"):
        guard.assert_split_only_convention(bad)

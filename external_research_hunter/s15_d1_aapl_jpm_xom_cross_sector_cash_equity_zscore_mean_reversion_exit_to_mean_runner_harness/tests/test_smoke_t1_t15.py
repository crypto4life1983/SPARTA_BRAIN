"""P4 synthetic smoke battery for s15-d1-cross-sector z-score mean-reversion exit-to-mean runner.

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
        "s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean"
    )
    assert algo._stale_fill_warning_count == 0
    assert algo.all_safety_warnings_zero() is True
    assert algo.open_position_count() == 0


# ---------- T3: rolling mean / std ----------

def test_T3_rolling_mean_std(runner_harness_module):
    main = runner_harness_module["main"]
    series = [10.0, 20.0, 30.0, 40.0]
    assert main.rolling_mean(series, 4) == pytest.approx(25.0)
    assert main.rolling_std(series, 4) == pytest.approx((500.0 / 3.0) ** 0.5)  # ddof=1
    # insufficient data -> None
    assert main.rolling_mean([10.0, 20.0, 30.0], 4) is None
    assert main.rolling_std([10.0, 20.0, 30.0], 4) is None


# ---------- T4: z-score ----------

def test_T4_zscore(runner_harness_module):
    main = runner_harness_module["main"]
    series = [10.0, 20.0, 30.0, 40.0]  # mean 25, std sqrt(500/3)
    assert main.zscore(series, 4) == pytest.approx(15.0 / (500.0 / 3.0) ** 0.5)
    # insufficient data -> None
    assert main.zscore([10.0, 20.0, 30.0], 4) is None
    # zero variance -> None
    assert main.zscore([50.0, 50.0, 50.0, 50.0], 4) is None


# ---------- T5: entry band signals ----------

def test_T5_entry_band_signals(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.long_entry_signal(z=-2.5, k=2.0) is True
    assert main.long_entry_signal(z=-2.0, k=2.0) is True  # boundary inclusive
    assert main.long_entry_signal(z=-1.5, k=2.0) is False
    assert main.short_entry_signal(z=2.5, k=2.0) is True
    assert main.short_entry_signal(z=2.0, k=2.0) is True
    assert main.short_entry_signal(z=1.5, k=2.0) is False
    assert main.long_entry_signal(z=None, k=2.0) is False
    assert main.short_entry_signal(z=None, k=2.0) is False


# ---------- T6: EXIT-TO-MEAN ----------

def test_T6_exit_to_mean(runner_harness_module):
    """Long closes when close re-crosses up to the mean; short when it falls to the mean."""
    main = runner_harness_module["main"]
    assert main.long_exit_to_mean(close=101.0, mean=100.0) is True
    assert main.long_exit_to_mean(close=100.0, mean=100.0) is True  # at the mean
    assert main.long_exit_to_mean(close=99.0, mean=100.0) is False
    assert main.short_exit_to_mean(close=99.0, mean=100.0) is True
    assert main.short_exit_to_mean(close=100.0, mean=100.0) is True
    assert main.short_exit_to_mean(close=101.0, mean=100.0) is False
    assert main.long_exit_to_mean(close=100.0, mean=None) is False
    assert main.short_exit_to_mean(close=100.0, mean=None) is False


# ---------- T7: vol-scaled catastrophe stop placement (NOT 2N) ----------

def test_T7_catastrophe_stop_placement(runner_harness_module):
    main = runner_harness_module["main"]
    stop_long = main.compute_catastrophe_stop(100.0, 2.0, side="long", sigma_multiple=3.5)
    assert stop_long == pytest.approx(100.0 - 7.0)  # 3.5 * 2.0
    stop_short = main.compute_catastrophe_stop(100.0, 2.0, side="short", sigma_multiple=3.5)
    assert stop_short == pytest.approx(100.0 + 7.0)


# ---------- T7b: add_pyramid_unit raises ----------

def test_T7b_add_pyramid_unit_raises(runner_harness_module):
    main = runner_harness_module["main"]
    with pytest.raises(RuntimeError, match="PYRAMID_FORBIDDEN"):
        main.add_pyramid_unit()


# ---------- T7c: starting_cash invariant $100,000 (DA4=B) ----------

def test_T7c_starting_cash_invariant_100000(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["start_cash_usd"] == 100_000


# ---------- T8: catastrophe stop wider than entry band (first-principles invariant) ----------

def test_T8_catastrophe_stop_wider_than_entry_band(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["catastrophe_stop_sigma_multiple"] == 3.5
    assert main.CONFIG["entry_band_k_sigma"] == 2.0
    assert main.CONFIG["catastrophe_stop_sigma_multiple"] > main.CONFIG["entry_band_k_sigma"]
    assert main.CONFIG["catastrophe_stop_is_fixed_2N"] is False
    assert main.CONFIG["stop_method"] == "vol_scaled_catastrophe_sigma"


# ---------- T9: portfolio cap ----------

def test_T9_portfolio_cap(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["max_total_positions"] == 3
    assert main.CONFIG["max_positions_per_name"] == 1
    assert main.CONFIG["inter_name_signal_coordination"] == "NONE"
    assert main.portfolio_can_open(2, max_total_positions=3) is True
    assert main.portfolio_can_open(3, max_total_positions=3) is False


# ---------- T10: vol-normalized sizing ----------

def test_T10_vol_normalized_sizing(runner_harness_module):
    """shares = floor((0.005 * 100000) / (3.5 * sigma))."""
    main = runner_harness_module["main"]
    shares = main.compute_position_shares_vol_normalized(100_000.0, 2.0, sigma_multiple=3.5, risk_pct=0.005)
    # floor(500 / 7.0) = floor(71.428) = 71
    assert shares == 71


# ---------- T11: tiny equity / zero sigma returns 0 ----------

def test_T11_skip_when_share_count_lt_one(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.compute_position_shares_vol_normalized(5.0, 2.0, 3.5, 0.005) == 0
    assert main.compute_position_shares_vol_normalized(100_000.0, 0.0, 3.5, 0.005) == 0
    assert main.compute_position_shares_vol_normalized(100_000.0, None, 3.5, 0.005) == 0


# ---------- T12: RTH-only filter attested ----------

def test_T12_rth_only_filter_attested(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["rth_safe_window_open"] == (9, 30)
    assert main.CONFIG["rth_safe_window_close"] == (16, 0)
    assert main.CONFIG["eod_cancel_time"] == (16, 0)
    assert main.CONFIG["daily_bars_only"] is True


# ---------- T13: cost surface ----------

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
        "assert_seal_inheritance", "assert_no_forbidden_order_paths",
        "assert_rec1_equivalent_binding_preserved", "assert_locked_strategy_params",
        "assert_exit_to_mean_rule", "assert_catastrophe_stop_vol_scaled_not_2N",
        "assert_boundary_alignment", "assert_split_only_convention", "assert_universe_locked",
        "assert_no_leverage_cap", "safety_counters_all_zero",
    ):
        assert result["checks"].get(k) is True, f"check {k} failed: {result['errors']}"


# ---------- T16: cross-sector universe locked ----------

def test_T16_universe_locked_cross_sector(runner_harness_module):
    main = runner_harness_module["main"]
    guard = runner_harness_module["execution_guard"]
    assert main.CONFIG["universe"] == ["AAPL", "JPM", "XOM"]
    bad = dict(main.CONFIG)
    bad["universe"] = ["AAPL", "MSFT", "NVDA"]
    with pytest.raises(Exception, match="UNIVERSE_DRIFT"):
        guard.assert_universe_locked(bad)


# ---------- T17: split_only convention ----------

def test_T17_split_only_convention(runner_harness_module):
    main = runner_harness_module["main"]
    guard = runner_harness_module["execution_guard"]
    assert main.CONFIG["adjustment_convention"] == "split_only"
    assert main.CONFIG["dividends_adjusted"] is False
    guard.assert_split_only_convention(main.CONFIG)
    bad = dict(main.CONFIG)
    bad["adjustment_convention"] = "split_and_dividend"
    with pytest.raises(Exception, match="C5_ADJUSTMENT_CONVENTION_NOT_SPLIT_ONLY"):
        guard.assert_split_only_convention(bad)


# ---------- T18: exit-to-mean + catastrophe-stop-not-2N guards (the binding axis) ----------

def test_T18_exit_to_mean_and_catastrophe_stop_guards(runner_harness_module):
    main = runner_harness_module["main"]
    guard = runner_harness_module["execution_guard"]
    # passing config attests cleanly
    guard.assert_exit_to_mean_rule(main.CONFIG)
    guard.assert_catastrophe_stop_vol_scaled_not_2N(main.CONFIG)
    # reverting the exit to an oscillator threshold (the s14-d1 failed design) must raise
    bad_exit = dict(main.CONFIG)
    bad_exit["exit_rule"] = "RSI_THRESHOLD"
    with pytest.raises(Exception, match="EXIT_RULE_DRIFT"):
        guard.assert_exit_to_mean_rule(bad_exit)
    # reverting to a fixed 2N stop (the s14-d1 failed design) must raise
    bad_stop = dict(main.CONFIG)
    bad_stop["catastrophe_stop_is_fixed_2N"] = True
    with pytest.raises(Exception, match="STOP_DESIGN_DRIFT"):
        guard.assert_catastrophe_stop_vol_scaled_not_2N(bad_stop)
    bad_method = dict(main.CONFIG)
    bad_method["stop_method"] = "fixed_2N_atr"
    with pytest.raises(Exception, match="STOP_METHOD_DRIFT"):
        guard.assert_catastrophe_stop_vol_scaled_not_2N(bad_method)


# ---------- T19: time-stop fallback ----------

def test_T19_time_stop_fallback(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["time_stop_max_hold_bars"] == 10
    assert main.time_stop_hit(9, max_hold_bars=10) is False
    assert main.time_stop_hit(10, max_hold_bars=10) is True
    assert main.time_stop_hit(11, max_hold_bars=10) is True

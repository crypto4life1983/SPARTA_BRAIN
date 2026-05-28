"""P4 synthetic smoke battery for s16-d1 Donchian breakout trend runner. Authored at P3 BUILD; run at P4."""

import pytest


def test_T1_module_imports_clean(runner_harness_module):
    assert all(runner_harness_module[k] is not None for k in ("main", "execution_guard", "in_sample_driver", "out_of_sample_driver"))


def test_T2_runner_class_instantiable(runner_harness_module):
    main = runner_harness_module["main"]
    algo = main.Algo(); algo.Initialize()
    assert algo.config["candidate_record_id"] == "s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history"
    assert algo._stale_fill_warning_count == 0 and algo.all_safety_warnings_zero() is True and algo.open_position_count() == 0


def test_T3_channel_high_low(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.channel_high([10.0, 20.0, 30.0, 40.0], 4) == 40.0
    assert main.channel_low([10.0, 20.0, 30.0, 40.0], 4) == 10.0
    assert main.channel_high([10.0, 20.0], 4) is None
    assert main.channel_low([10.0, 20.0], 4) is None


def test_T4_breakout_entries(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.long_entry_breakout(41.0, 40.0) is True
    assert main.long_entry_breakout(40.0, 40.0) is False  # strict >
    assert main.short_entry_breakout(9.0, 10.0) is True
    assert main.short_entry_breakout(10.0, 10.0) is False
    assert main.long_entry_breakout(41.0, None) is False
    assert main.short_entry_breakout(9.0, None) is False


def test_T5_trailing_exits(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.long_trailing_exit(9.0, 10.0) is True
    assert main.long_trailing_exit(10.0, 10.0) is False  # strict <
    assert main.short_trailing_exit(41.0, 40.0) is True
    assert main.short_trailing_exit(40.0, 40.0) is False
    assert main.long_trailing_exit(9.0, None) is False
    assert main.short_trailing_exit(41.0, None) is False


def test_T6_wilder_atr(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.wilder_atr([2.0] * 15, period=14) == pytest.approx(2.0)
    assert main.wilder_atr([2.0] * 13, period=14) is None


def test_T7_initial_stop_2atr(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.compute_initial_stop(100.0, 2.0, side="long", atr_multiple=2.0) == pytest.approx(96.0)
    assert main.compute_initial_stop(100.0, 2.0, side="short", atr_multiple=2.0) == pytest.approx(104.0)


def test_T7b_add_pyramid_unit_raises(runner_harness_module):
    main = runner_harness_module["main"]
    with pytest.raises(RuntimeError, match="PYRAMID_FORBIDDEN"):
        main.add_pyramid_unit()


def test_T7c_starting_cash_invariant_100000(runner_harness_module):
    assert runner_harness_module["main"].CONFIG["start_cash_usd"] == 100_000


def test_T8_stop_design_is_2atr_not_tight(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["initial_catastrophe_stop_atr_multiple"] == 2.0
    assert main.CONFIG["stop_is_tight_mean_reversion_stop"] is False
    assert main.CONFIG["stop_method"] == "trailing_donchian_plus_2atr_initial_floor"


def test_T9_portfolio_cap(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["max_total_positions"] == 6
    assert main.CONFIG["max_positions_per_name"] == 1
    assert main.portfolio_can_open(5, max_total_positions=6) is True
    assert main.portfolio_can_open(6, max_total_positions=6) is False


def test_T10_vol_normalized_sizing(runner_harness_module):
    main = runner_harness_module["main"]
    # floor((0.005 * 100000) / (2 * 2.0)) = floor(500/4) = 125
    assert main.compute_position_shares_vol_normalized(100_000.0, 2.0, atr_multiple=2.0, risk_pct=0.005) == 125


def test_T11_skip_when_share_count_lt_one(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.compute_position_shares_vol_normalized(5.0, 2.0, 2.0, 0.005) == 0
    assert main.compute_position_shares_vol_normalized(100_000.0, 0.0, 2.0, 0.005) == 0
    assert main.compute_position_shares_vol_normalized(100_000.0, None, 2.0, 0.005) == 0


def test_T12_rth_only_filter_attested(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["rth_safe_window_open"] == (9, 30) and main.CONFIG["eod_cancel_time"] == (16, 0)
    assert main.CONFIG["daily_bars_only"] is True


def test_T13_cost_surface(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["commission_per_share_usd"] == 0.005 and main.CONFIG["min_commission_per_trade_usd"] == 1.0
    assert main.CONFIG["slippage_proxy_bps"] == 1.0


def test_T14_cost_stress_matrix(runner_harness_module):
    tiers = runner_harness_module["main"].CONFIG["cost_stress_tiers"]
    assert [t["tier"] for t in tiers] == ["S0", "S1", "S2", "S3", "S4"]
    assert [t["cost_scalar"] for t in tiers] == [0.0, 1.0, 1.5, 2.0, 3.0]


def test_T15_validator_harness_pass(runner_harness_module):
    main = runner_harness_module["main"]; guard = runner_harness_module["execution_guard"]
    algo = main.Algo(); algo.Initialize()
    result = guard.full_guard_check(algo.config, safety_counters={"stale_fill_warning_count": algo._stale_fill_warning_count})
    assert result["overall_pass"] is True, f"errors: {result['errors']}"
    for k in ("assert_seal_inheritance", "assert_no_forbidden_order_paths", "assert_rec1_equivalent_binding_preserved",
              "assert_locked_strategy_params", "assert_trailing_donchian_exit", "assert_initial_stop_2atr_not_tight",
              "assert_boundary_alignment", "assert_split_only_convention", "assert_universe_locked",
              "assert_no_leverage_cap", "safety_counters_all_zero"):
        assert result["checks"].get(k) is True, f"check {k} failed: {result['errors']}"


def test_T16_universe_locked_12name(runner_harness_module):
    main = runner_harness_module["main"]; guard = runner_harness_module["execution_guard"]
    assert main.CONFIG["universe"] == ["AAPL", "MSFT", "NVDA", "JPM", "XOM", "UNH", "WMT", "KO", "META", "AMZN", "JNJ", "CVX"]
    bad = dict(main.CONFIG); bad["universe"] = ["AAPL", "JPM", "XOM"]
    with pytest.raises(Exception, match="UNIVERSE_DRIFT"):
        guard.assert_universe_locked(bad)


def test_T17_split_only_convention(runner_harness_module):
    main = runner_harness_module["main"]; guard = runner_harness_module["execution_guard"]
    assert main.CONFIG["adjustment_convention"] == "split_only" and main.CONFIG["dividends_adjusted"] is False
    guard.assert_split_only_convention(main.CONFIG)
    bad = dict(main.CONFIG); bad["adjustment_convention"] = "split_and_dividend"
    with pytest.raises(Exception, match="C5_ADJUSTMENT_CONVENTION_NOT_SPLIT_ONLY"):
        guard.assert_split_only_convention(bad)


def test_T18_trend_exit_stop_guards(runner_harness_module):
    main = runner_harness_module["main"]; guard = runner_harness_module["execution_guard"]
    guard.assert_trailing_donchian_exit(main.CONFIG)
    guard.assert_initial_stop_2atr_not_tight(main.CONFIG)
    # reverting to an oscillator/exit-to-mean rule (mean-reversion family) must raise
    bad_exit = dict(main.CONFIG); bad_exit["exit_rule"] = "EXIT_TO_MEAN"
    with pytest.raises(Exception, match="EXIT_RULE_DRIFT"):
        guard.assert_trailing_donchian_exit(bad_exit)
    # reverting to a tight mean-reversion stop must raise
    bad_stop = dict(main.CONFIG); bad_stop["stop_is_tight_mean_reversion_stop"] = True
    with pytest.raises(Exception, match="STOP_DESIGN_DRIFT"):
        guard.assert_initial_stop_2atr_not_tight(bad_stop)


def test_T19_donchian_periods_locked(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["n_entry_donchian"] == 20
    assert main.CONFIG["n_exit_donchian_trailing"] == 10
    assert main.CONFIG["exit_rule"] == "TRAILING_DONCHIAN_CHANNEL"
    assert main.CONFIG["atr_period"] == 14

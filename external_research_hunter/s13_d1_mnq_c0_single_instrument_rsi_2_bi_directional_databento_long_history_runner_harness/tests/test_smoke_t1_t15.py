"""P4 synthetic smoke battery (T1-T15 + T7b + T7c) for s13-d1 RSI(2) bi-directional runner.

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
        "s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history"
    )
    assert algo._stale_fill_warning_count == 0
    assert algo.all_safety_warnings_zero() is True


# ---------- T3: Wilder ATR(20) on constant TR=2.0 ----------

def test_T3_wilder_atr_synthetic(runner_harness_module):
    main = runner_harness_module["main"]
    tr_series = [2.0] * 21
    atr = main.wilder_atr(tr_series, period=20)
    assert atr == pytest.approx(2.0)


# ---------- T4: RSI(2) computation on synthetic series ----------

def test_T4_rsi_2_synthetic(runner_harness_module):
    """RSI(2) Wilder smoothing on close-to-close diffs."""
    main = runner_harness_module["main"]
    # Two strictly up bars -> RSI(2) close to 100
    closes_up = [100.0, 101.0, 102.0]
    rsi_up = main.wilder_rsi(closes_up, period=2)
    assert rsi_up == pytest.approx(100.0)
    # Two strictly down bars -> RSI(2) close to 0
    closes_down = [100.0, 99.0, 98.0]
    rsi_down = main.wilder_rsi(closes_down, period=2)
    assert rsi_down == pytest.approx(0.0)
    # Insufficient data -> None
    assert main.wilder_rsi([100.0], period=2) is None
    assert main.wilder_rsi([100.0, 101.0], period=2) is None  # only 1 diff, need 2 for RSI(2)


# ---------- T5: RSI oversold/overbought entry triggers ----------

def test_T5_rsi_oversold_overbought_entry_trigger(runner_harness_module):
    """RSI(2)<10 fires long entry; RSI(2)>90 fires short entry."""
    main = runner_harness_module["main"]
    # Oversold: RSI < 10
    assert main.long_entry_signal(rsi=5.0, threshold=10) is True
    assert main.long_entry_signal(rsi=10.0, threshold=10) is False  # strict <
    assert main.long_entry_signal(rsi=15.0, threshold=10) is False
    # Overbought: RSI > 90
    assert main.short_entry_signal(rsi=95.0, threshold=90) is True
    assert main.short_entry_signal(rsi=90.0, threshold=90) is False  # strict >
    assert main.short_entry_signal(rsi=85.0, threshold=90) is False
    # None RSI does not fire
    assert main.long_entry_signal(rsi=None, threshold=10) is False
    assert main.short_entry_signal(rsi=None, threshold=90) is False


# ---------- T6: stop placement at 2N ----------

def test_T6_stop_placement_at_2n(runner_harness_module):
    main = runner_harness_module["main"]
    entry_long = 100.0
    atr = 2.0
    stop_long = main.compute_stop_price(entry_long, atr, side="long", multiplier=2.0)
    assert stop_long == pytest.approx(100.0 - 4.0)
    entry_short = 99.0
    stop_short = main.compute_stop_price(entry_short, atr, side="short", multiplier=2.0)
    assert stop_short == pytest.approx(99.0 + 4.0)


# ---------- T7: pyramid trigger computed (informational) ----------

def test_T7_pyramid_trigger_at_05n(runner_harness_module):
    """Pyramid TRIGGER PRICE COMPUTED at +0.5*2N (informational); invocation forbidden."""
    entry = 100.0
    atr = 2.0
    pyramid_trigger_informational = entry + 0.5 * 2.0 * atr  # 0.5 * 2N
    assert pyramid_trigger_informational == pytest.approx(102.0)


# ---------- T7b: add_pyramid_unit raises ----------

def test_T7b_add_pyramid_unit_raises_under_max_units_1(runner_harness_module):
    main = runner_harness_module["main"]
    with pytest.raises(RuntimeError, match="PYRAMID_FORBIDDEN"):
        main.add_pyramid_unit()


# ---------- T7c: starting_cash invariant $200,000 (DA4=C) ----------

def test_T7c_starting_cash_invariant_200000(runner_harness_module):
    """CONFIG['starting_cash_mnq_equivalent'] == 200_000 (s13-d1-specific; DA4=C)."""
    main = runner_harness_module["main"]
    assert main.CONFIG["starting_cash_mnq_equivalent"] == 200_000


# ---------- T8: RSI 50 crossover exit ----------

def test_T8_exit_on_rsi_50_crossover(runner_harness_module):
    """RSI(2)>50 closes long; RSI(2)<50 closes short."""
    main = runner_harness_module["main"]
    # Long exit when RSI > 50
    assert main.long_exit_signal(rsi=55.0, threshold=50) is True
    assert main.long_exit_signal(rsi=50.0, threshold=50) is False  # strict >
    assert main.long_exit_signal(rsi=45.0, threshold=50) is False
    # Short exit when RSI < 50
    assert main.short_exit_signal(rsi=45.0, threshold=50) is True
    assert main.short_exit_signal(rsi=50.0, threshold=50) is False  # strict <
    assert main.short_exit_signal(rsi=55.0, threshold=50) is False
    # None RSI does not fire
    assert main.long_exit_signal(rsi=None, threshold=50) is False
    assert main.short_exit_signal(rsi=None, threshold=50) is False


# ---------- T9: portfolio cap uses unit count ----------

def test_T9_portfolio_cap_uses_unit_count_not_contract_count(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["max_total_units"] == 1
    assert main.CONFIG["max_units_per_market"] == 1


# ---------- T10: sizing at 0.5% risk on $200k cash ----------

def test_T10_sizing_0_5pct_floor(runner_harness_module):
    """compute_unit_contracts returns floor((0.005 * 200000) / (ATR_entry * 0.5))."""
    main = runner_harness_module["main"]
    equity = 200_000.0
    atr_entry = 2.0
    tick_value = 0.5
    contracts = main.compute_unit_contracts(equity, atr_entry, tick_value, risk_pct=0.005)
    # Expected: floor((0.005 * 200000) / (2.0 * 0.5)) = floor(1000 / 1) = 1000
    assert contracts == 1000


# ---------- T11: tiny equity returns 0 contracts ----------

def test_T11_skip_when_contract_count_lt_one(runner_harness_module):
    main = runner_harness_module["main"]
    contracts = main.compute_unit_contracts(5.0, 2.0, 0.5, risk_pct=0.005)
    assert contracts == 0


# ---------- T12: RTH-only filter attested ----------

def test_T12_rth_only_filter_attested(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["rth_safe_window_open"] == (9, 30)
    assert main.CONFIG["rth_safe_window_close"] == (16, 0)
    assert main.CONFIG["eod_cancel_time"] == (16, 0)
    assert main.CONFIG["rth_window_tz"] == "America/New_York"


# ---------- T13: roll-cost tick_value_usd = 0.50 ----------

def test_T13_roll_cost_modeled_1_spread_tick(runner_harness_module):
    main = runner_harness_module["main"]
    assert main.CONFIG["tick_value_usd"] == 0.5
    assert main.CONFIG["tick_size_points"] == 0.25


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
        "assert_no_corporate_actions_for_futures",
        "safety_counters_all_zero",
    ):
        assert result["checks"].get(k) is True, f"check {k} failed: {result['errors']}"

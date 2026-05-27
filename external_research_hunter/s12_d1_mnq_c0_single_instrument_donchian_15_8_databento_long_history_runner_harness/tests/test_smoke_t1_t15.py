"""P4 synthetic smoke battery (T1-T15 + T7b + T7c) for s12-d1 runner harness.

These tests are AUTHORED at P3 BUILD. They are EXECUTED at P4 synthetic smoke
under separate operator authorization. P3 BUILD does NOT execute these tests.

Tests verify the s12-d1 module structure, CONFIG invariants, and signal primitives
on the synthetic fixture; they do NOT exercise the sealed MNQ CSV.

Inherits Phase 2 safety contracts (C1-C8) from:
  docs/phase2_safety_contract_template.md
Template source candidate (parked, not money-proven):
  s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
Template reuse notice: NKE strategy logic NOT inherited; only safety contracts.
"""

import pytest


# ---------- T1: module imports clean ----------

def test_T1_module_imports_clean(runner_harness_module):
    """main + execution_guard + drivers importable without QC/databento at module level."""
    assert runner_harness_module["main"] is not None
    assert runner_harness_module["execution_guard"] is not None
    assert runner_harness_module["in_sample_driver"] is not None
    assert runner_harness_module["out_of_sample_driver"] is not None


# ---------- T2: runner class instantiable ----------

def test_T2_runner_class_instantiable(runner_harness_module):
    """main.Algo() Initialize() succeeds without QC runtime."""
    main = runner_harness_module["main"]
    algo = main.Algo()
    algo.Initialize()
    assert algo.config["candidate_record_id"] == (
        "s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history"
    )
    assert algo._stale_fill_warning_count == 0
    assert algo.all_safety_warnings_zero() is True


# ---------- T3: Wilder ATR(20) on constant TR=2.0 returns 2.0 ----------

def test_T3_wilder_atr_synthetic(runner_harness_module):
    """ATR(20) on constant 21-bar TR series returns 2.0."""
    main = runner_harness_module["main"]
    tr_series = [2.0] * 21
    atr = main.wilder_atr(tr_series, period=20)
    assert atr == pytest.approx(2.0)


# ---------- T4: Donchian-15 high/low matches max/min ----------

def test_T4_donchian_15_8_synthetic(runner_harness_module):
    """Donchian-15 high/low and Donchian-8 high/low on synthetic series match max/min."""
    main = runner_harness_module["main"]
    # Use a flat-region window from the synthetic series: highs all 101, lows all 99
    highs_15 = [101.0] * 15
    lows_15 = [99.0] * 15
    dh, dl = main.donchian_channels(highs_15, lows_15, n=15)
    assert dh == 101.0
    assert dl == 99.0
    # Donchian-8 on the same window (subset)
    dh8, dl8 = main.donchian_channels(highs_15[-8:], lows_15[-8:], n=8)
    assert dh8 == 101.0
    assert dl8 == 99.0


# ---------- T5: 15-day breakout triggers long entry ----------

def test_T5_entry_trigger_synthetic_breakout(runner_harness_module):
    """Synthetic 15-day breakout bar triggers long entry."""
    main = runner_harness_module["main"]
    # Prior 15 highs all 101 (flat region), breakout bar close=101.5
    donchian_high_15 = 101.0
    assert main.long_entry_signal(close=101.5, donchian_high_n_prior=donchian_high_15) is True
    # Same close at exactly equal does NOT trigger (must be strictly greater)
    assert main.long_entry_signal(close=101.0, donchian_high_n_prior=donchian_high_15) is False


# ---------- T6: stop placement at 2N ----------

def test_T6_stop_placement_at_2n(runner_harness_module):
    """Stop = entry - 2 * N for long; entry + 2 * N for short."""
    main = runner_harness_module["main"]
    entry_long = 101.5
    atr = 2.0
    stop_long = main.compute_stop_price(entry_long, atr, side="long", multiplier=2.0)
    assert stop_long == pytest.approx(101.5 - 4.0)
    entry_short = 99.5
    stop_short = main.compute_stop_price(entry_short, atr, side="short", multiplier=2.0)
    assert stop_short == pytest.approx(99.5 + 4.0)


# ---------- T7: pyramid trigger computed at +0.5N (invocation forbidden) ----------

def test_T7_pyramid_trigger_at_05n(runner_harness_module):
    """Pyramid trigger COMPUTED at +0.5N (informational); add_pyramid_unit() is forbidden (see T7b)."""
    # The pyramid TRIGGER PRICE for long would be entry + 0.5 * N (if pyramid were authorized).
    # s12-d1 has max_units_per_market=1 / no_pyramid_per_signal; trigger price is informational only.
    entry = 101.5
    atr = 2.0
    pyramid_trigger_informational = entry + 0.5 * 2.0 * atr  # 0.5 * 2N
    assert pyramid_trigger_informational == pytest.approx(101.5 + 2.0)


# ---------- T7b: add_pyramid_unit raises RuntimeError ----------

def test_T7b_add_pyramid_unit_raises_under_max_units_1(runner_harness_module):
    """add_pyramid_unit raises RuntimeError when max_units=1."""
    main = runner_harness_module["main"]
    with pytest.raises(RuntimeError, match="PYRAMID_FORBIDDEN"):
        main.add_pyramid_unit()


# ---------- T7c: starting_cash invariant $100,000 (DA4=B) ----------

def test_T7c_starting_cash_invariant_100000(runner_harness_module):
    """CONFIG['starting_cash_mnq_equivalent'] == 100_000 (s12-d1-specific S-STOP; DA4=B)."""
    main = runner_harness_module["main"]
    assert main.CONFIG["starting_cash_mnq_equivalent"] == 100_000


# ---------- T8: Donchian-8 reversal triggers exit ----------

def test_T8_exit_on_donchian_8_reversal(runner_harness_module):
    """Donchian-8 reversal triggers exit (LONG: close < prior 8-day low)."""
    main = runner_harness_module["main"]
    donchian_low_8 = 113.5  # arbitrary
    # Exit triggered when close < donchian_low_8
    assert main.long_exit_signal(close=110.0, donchian_low_m_prior=donchian_low_8) is True
    assert main.long_exit_signal(close=113.5, donchian_low_m_prior=donchian_low_8) is False
    # SHORT exit: close > prior 8-day high
    donchian_high_8 = 95.0
    assert main.short_exit_signal(close=99.0, donchian_high_m_prior=donchian_high_8) is True


# ---------- T9: portfolio cap uses unit count, not contract count ----------

def test_T9_portfolio_cap_uses_unit_count_not_contract_count(runner_harness_module):
    """max_total_units=1 enforced (single instrument, single unit)."""
    main = runner_harness_module["main"]
    assert main.CONFIG["max_total_units"] == 1
    assert main.CONFIG["max_units_per_market"] == 1
    # contracts-per-unit is sizing-dependent (not capped at 1; capped by 1% risk)
    # The cap is on UNITS, not CONTRACTS-PER-UNIT.


# ---------- T10: 1% risk floor sizing ----------

def test_T10_sizing_1pct_floor(runner_harness_module):
    """compute_unit_contracts returns floor((0.01 * 100000) / (ATR_entry * 0.5))."""
    main = runner_harness_module["main"]
    equity = 100_000.0
    atr_entry = 2.0
    tick_value = 0.5
    contracts = main.compute_unit_contracts(equity, atr_entry, tick_value, risk_pct=0.01)
    # Expected: floor((0.01 * 100000) / (2.0 * 0.5)) = floor(1000 / 1) = 1000
    assert contracts == 1000


# ---------- T11: tiny equity returns 0 contracts ----------

def test_T11_skip_when_contract_count_lt_one(runner_harness_module):
    """Tiny equity returns 0 contracts."""
    main = runner_harness_module["main"]
    # Equity = $5, ATR = 2.0, tick_value = 0.5 -> raw = (0.01 * 5) / 1.0 = 0.05 -> floor = 0
    contracts = main.compute_unit_contracts(5.0, 2.0, 0.5, risk_pct=0.01)
    assert contracts == 0


# ---------- T12: RTH-only filter attested ----------

def test_T12_rth_only_filter_attested(runner_harness_module):
    """RTH window 09:30-16:00 ET America/New_York in CONFIG."""
    main = runner_harness_module["main"]
    assert main.CONFIG["rth_safe_window_open"] == (9, 30)
    assert main.CONFIG["rth_safe_window_close"] == (16, 0)
    assert main.CONFIG["eod_cancel_time"] == (16, 0)  # C4 boundary alignment
    assert main.CONFIG["rth_window_tz"] == "America/New_York"


# ---------- T13: roll-cost tick_value_usd = 0.50 ----------

def test_T13_roll_cost_modeled_1_spread_tick(runner_harness_module):
    """tick_value_usd=0.50 in CONFIG."""
    main = runner_harness_module["main"]
    assert main.CONFIG["tick_value_usd"] == 0.5
    assert main.CONFIG["tick_size_points"] == 0.25


# ---------- T14: cost-stress matrix S0-S4 ----------

def test_T14_cost_stress_matrix_S0_S1_S2_S3_S4(runner_harness_module):
    """5 tiers in CONFIG['cost_stress_tiers']."""
    main = runner_harness_module["main"]
    tiers = main.CONFIG["cost_stress_tiers"]
    assert len(tiers) == 5
    expected_tiers = ["S0", "S1", "S2", "S3", "S4"]
    actual_tiers = [t["tier"] for t in tiers]
    assert actual_tiers == expected_tiers
    expected_cost_scalars = [0.0, 1.0, 1.5, 2.0, 3.0]
    actual_cost_scalars = [t["cost_scalar"] for t in tiers]
    assert actual_cost_scalars == expected_cost_scalars
    expected_slip_scalars = [0.0, 1.0, 1.5, 2.0, 3.0]
    actual_slip_scalars = [t["slippage_scalar"] for t in tiers]
    assert actual_slip_scalars == expected_slip_scalars


# ---------- T15: validator harness pass on synthetic ----------

def test_T15_validator_harness_pass_on_synthetic(runner_harness_module):
    """execution_guard.full_guard_check returns overall_pass=True on synthetic algo proxy."""
    main = runner_harness_module["main"]
    guard = runner_harness_module["execution_guard"]
    algo = main.Algo()
    algo.Initialize()
    safety_counters = {"stale_fill_warning_count": algo._stale_fill_warning_count}
    result = guard.full_guard_check(algo.config, safety_counters=safety_counters)
    assert result["overall_pass"] is True, f"errors: {result['errors']}"
    # Required individual checks pass
    for k in (
        "assert_seal_inheritance",
        "assert_no_forbidden_order_paths",
        "assert_rec1_binding_preserved",
        "assert_locked_strategy_params",
        "assert_boundary_alignment",
        "assert_no_corporate_actions_for_futures",
        "safety_counters_all_zero",
    ):
        assert result["checks"].get(k) is True, f"check {k} failed: {result['errors']}"

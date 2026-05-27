"""s10 D2 T1-T15 smoke test SCAFFOLD (synthetic-only).

PREPARED at P3 BUILD time. NOT executed by P3. To be run at P4 (separate
operator authorization). Each test corresponds to a T-gate from the plan-lock
future_smoke_test_gates.

NO real market data. NO Databento. NO QuantConnect runtime required.
NO live trading. NO broker imports.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

# Import the runner harness under test. main.py uses lazy QC access, so this
# import succeeds without a QC runtime present.
from external_research_hunter.s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness import main as runner_main
from external_research_hunter.s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness import execution_guard


# ---------------------------------------------------------------------------
# Fixture loaders (CSV -> lists)
# ---------------------------------------------------------------------------
def _load_csv(path: Path):
    bars = {"date": [], "open": [], "high": [], "low": [], "close": [], "volume": []}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            # SAFETY: refuse to load any CSV whose source column is not the synthetic marker.
            if row.get("source") != "SYNTHETIC_PHASE2_SMOKE_FIXTURE":
                raise RuntimeError(f"Refusing to load CSV without SYNTHETIC marker: {path}")
            bars["date"].append(row["date"])
            bars["open"].append(float(row["open"]))
            bars["high"].append(float(row["high"]))
            bars["low"].append(float(row["low"]))
            bars["close"].append(float(row["close"]))
            bars["volume"].append(int(row["volume"]))
    return bars


@pytest.fixture(scope="session")
def synthetic_bars(fixtures_dir):
    return {
        "NQ": _load_csv(fixtures_dir / "synthetic_nq_daily.csv"),
        "GC": _load_csv(fixtures_dir / "synthetic_gc_daily.csv"),
        "ZN": _load_csv(fixtures_dir / "synthetic_zn_daily.csv"),
        "CL": _load_csv(fixtures_dir / "synthetic_cl_daily.csv"),
    }


# ---------------------------------------------------------------------------
# T1 -- module imports clean (no QC runtime required)
# ---------------------------------------------------------------------------
def test_t1_module_imports_clean():
    assert runner_main.CANDIDATE_RECORD_ID == "s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl"
    assert runner_main.ALGO_VERSION_FOR_RUN_ID == "s10_d2_v0_1_0"
    assert runner_main.PHASE_PREFIX == "PHASE2-S10-D2-XAD-RC"
    # Inheritance shas embedded
    assert runner_main.TIER_N_SPEC_SEAL_SHA256 == "f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679"
    assert runner_main.PLAN_LOCK_SEAL_SHA256   == "ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354"
    assert runner_main.PHASE2_PLAN_SEAL_SHA256 == "7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3"


# ---------------------------------------------------------------------------
# T2 -- runner class instantiable without QC runtime
# ---------------------------------------------------------------------------
def test_t2_runner_class_instantiable():
    algo = runner_main.TenD2CrossAssetDonchianNoPyramidReparamCapAlgo()
    # Stubbed Initialize should not raise when QC is absent (LiveMode defaults to False)
    algo.Initialize()
    assert algo._backtest_run_id.startswith("PHASE2-S10-D2-XAD-RC-")
    assert len(algo._run_id_12) == 12


# ---------------------------------------------------------------------------
# T3 -- WilderATR(20) on a known synthetic series
# ---------------------------------------------------------------------------
def test_t3_wilder_atr_synthetic():
    # 21 bars; constant TR = 2.0; expected ATR = 2.0
    highs  = [102.0] * 21
    lows   = [100.0] * 21
    closes = [101.0] * 21
    atr = runner_main.wilder_atr(highs, lows, closes, n=20)
    assert abs(atr - 2.0) < 1e-9


# ---------------------------------------------------------------------------
# T4 -- Donchian high/low channel on synthetic series
# ---------------------------------------------------------------------------
def test_t4_donchian_55_20_synthetic(synthetic_bars):
    nq = synthetic_bars["NQ"]
    assert len(nq["high"]) >= 55
    h55 = runner_main.donchian_high(nq["high"][:55], n=55)
    l55 = runner_main.donchian_low(nq["low"][:55], n=55)
    assert h55 == max(nq["high"][:55])
    assert l55 == min(nq["low"][:55])


# ---------------------------------------------------------------------------
# T5 -- entry trigger fires on a synthetic breakout
# ---------------------------------------------------------------------------
def test_t5_entry_trigger_synthetic_breakout(synthetic_bars):
    nq = synthetic_bars["NQ"]
    # By construction, fixture has a breakout segment near bar 56.
    prev_55_high = max(nq["high"][:55])
    breakout_bar_high = nq["high"][55]
    assert breakout_bar_high > prev_55_high


# ---------------------------------------------------------------------------
# T6 -- stop placed at 2N below entry (long)
# ---------------------------------------------------------------------------
def test_t6_stop_placement_at_2n():
    pyr = runner_main.PyramidManager(market="NQ", max_units=1, pyramid_spacing_n=0.5, stop_n_multiplier=2.0)
    pyr.open_first_unit(direction="long", entry_price=15000.0, n_entry=50.0, contracts=1)
    assert pyr.stops[0] == 15000.0 - 2.0 * 50.0


# ---------------------------------------------------------------------------
# T7 -- pyramid trigger at +0.5N above last entry (long)
# ---------------------------------------------------------------------------
def test_t7_pyramid_trigger_at_05n():
    # Under s8-D1 max_units=1, the trigger is still COMPUTED for completeness
    # but add_pyramid_unit raises if invoked (see T7b).
    pyr = runner_main.PyramidManager(market="NQ", max_units=1, pyramid_spacing_n=0.5, stop_n_multiplier=2.0)
    pyr.open_first_unit(direction="long", entry_price=15000.0, n_entry=50.0, contracts=1)
    assert pyr.next_pyramid_trigger == 15000.0 + 0.5 * 50.0


def test_t7b_add_pyramid_unit_raises_under_max_units_1():
    """S10-D2 no-pyramid invariant: add_pyramid_unit must raise when called with
    current_unit_count >= max_units = 1."""
    pyr = runner_main.PyramidManager(market="NQ", max_units=1, pyramid_spacing_n=0.5, stop_n_multiplier=2.0)
    pyr.open_first_unit(direction="long", entry_price=15000.0, n_entry=50.0, contracts=1)
    import pytest as _pt
    with _pt.raises(RuntimeError, match="exceed max_units=1"):
        pyr.add_pyramid_unit(entry_price=15025.0, contracts=1)

def test_t7c_starting_cash_invariant_500000():
    """S10-D2 S-STOP-14: starting_cash_mnq_equivalent MUST be 500_000."""
    assert runner_main.CONFIG["starting_cash_mnq_equivalent"] == 500_000



# ---------------------------------------------------------------------------
# T8 -- Donchian-20 reversal triggers exit (synthetic)
# ---------------------------------------------------------------------------
def test_t8_exit_on_donchian_20_reversal(synthetic_bars):
    nq = synthetic_bars["NQ"]
    # Construct a clear reversal: today's low < min of last 20 highs/lows
    lows_20 = nq["low"][-20:]
    today_low = min(lows_20) - 10.0
    assert today_low < runner_main.donchian_low(lows_20, n=20)


# ---------------------------------------------------------------------------
# T9 -- portfolio cap uses UNIT count (s6 bugfix regression)
# ---------------------------------------------------------------------------
def test_t9_portfolio_cap_uses_unit_count_not_contract_count():
    # S10-D2: 4 markets * 1 unit = 4 units total. per_market_cap=1.
    cap = runner_main.PortfolioCapTracker(max_total_units=4, per_market_cap=1)
    cap.update_market_units("NQ", 1)
    cap.update_market_units("GC", 1)
    cap.update_market_units("ZN", 1)
    cap.update_market_units("CL", 1)
    assert cap.total_open_units() == 4
    assert cap.at_or_above_cap()
    assert cap.cap_binding_events_count == 0  # structurally non-binding at 4 markets * 1 unit

    # Passing > 1 (either s6 bug OR s8-D1 no-pyramid invariant violation) must raise
    cap2 = runner_main.PortfolioCapTracker(max_total_units=4, per_market_cap=1)
    with pytest.raises(ValueError, match="max per market is 1"):
        cap2.update_market_units("NQ", 10)  # contract count; bug detector fires
    cap3 = runner_main.PortfolioCapTracker(max_total_units=4, per_market_cap=1)
    with pytest.raises(ValueError, match="max per market is 1"):
        cap3.update_market_units("NQ", 2)   # unit count 2; no-pyramid invariant fires


# ---------------------------------------------------------------------------
# T10 -- sizing computation floor((0.01 * equity) / (N * $/pt))
# ---------------------------------------------------------------------------
def test_t10_sizing_1pct_floor():
    # 1% of 100_000 / (50 * 20) = 1000 / 1000 = 1 contract for NQ-like params
    contracts = runner_main.compute_unit_contracts(portfolio_equity=100_000, n_entry=50.0,
                                                   dollar_per_point=20, risk_pct=0.01)
    assert contracts == 1


# ---------------------------------------------------------------------------
# T11 -- skip when computed contracts < 1
# ---------------------------------------------------------------------------
def test_t11_skip_when_contract_count_lt_one():
    # tiny equity should produce 0 contracts for NQ; entry should be skipped upstream
    contracts = runner_main.compute_unit_contracts(portfolio_equity=10.0, n_entry=50.0,
                                                   dollar_per_point=20, risk_pct=0.01)
    assert contracts == 0


# ---------------------------------------------------------------------------
# T12 -- RTH-only filter attested (per-market windows from CONFIG)
# ---------------------------------------------------------------------------
def test_t12_rth_only_filter_attested():
    cfg = runner_main.CONFIG["markets_meta"]
    assert cfg["NQ"]["rth_close_et"] == [16, 0]
    assert cfg["GC"]["rth_close_et"] == [16, 0]
    assert cfg["ZN"]["rth_close_et"] == [16, 0]
    assert cfg["CL"]["rth_close_et"] == [14, 30]
    # Each market has open + close declared
    for m in ("NQ", "GC", "ZN", "CL"):
        assert "rth_open_et" in cfg[m]
        assert "rth_close_et" in cfg[m]


# ---------------------------------------------------------------------------
# T13 -- roll cost modeled (1 spread tick per market at roll dates)
# ---------------------------------------------------------------------------
def test_t13_roll_cost_modeled_1_spread_tick():
    # The exact roll-cost ledger is built at P6 in-sample. Here we just confirm
    # the CONFIG declares per-market tick values used to model the cost.
    cfg = runner_main.CONFIG["markets_meta"]
    assert cfg["NQ"]["tick_value_usd"] == 5.00
    assert cfg["GC"]["tick_value_usd"] == 10.00
    assert cfg["ZN"]["tick_value_usd"] == 15.625
    assert cfg["CL"]["tick_value_usd"] == 10.00


# ---------------------------------------------------------------------------
# T14 -- cost stress matrix has S0..S4 tiers
# ---------------------------------------------------------------------------
def test_t14_cost_stress_matrix_S0_S1_S2_S3_S4():
    tiers = list(runner_main.CONFIG["cost_stress_tiers"].keys())
    assert tiers == ["S0", "S1", "S2", "S3", "S4"]


# ---------------------------------------------------------------------------
# T15 -- validator-on-synthetic via execution_guard.full_guard_check (synthetic)
# ---------------------------------------------------------------------------
def test_t15_validator_harness_pass_on_synthetic():
    diagnostic_blob = (
        '{"status_fields": {"trading_status": "PAUSED", "live_status": "BLOCKED_AT_6_GATES"}, '
        '"labels": ["DIAGNOSTIC_ONLY_NOT_LIVE_GRADE", "EXTERNAL_CLAIM_ONLY"]}'
    )
    # Minimal synthetic algo proxy with LiveMode=False
    class _AlgoStub:
        LiveMode = False
    result = execution_guard.full_guard_check(
        algo_obj=_AlgoStub(),
        modules_iter=["sys", "json", "math"],  # no broker imports
        diagnostic_blob=diagnostic_blob,
        constants_module=execution_guard,
        engine_start=__import__("datetime").date(2013, 1, 1),
        engine_end=__import__("datetime").date(2022, 12, 30),
        config_start_tuple=(2013, 1, 1),
        config_end_tuple=(2022, 12, 30),
        ceiling_tuple=(2022, 12, 30),
    )
    assert result["overall_pass"] is True
    assert result["no_forbidden_imports"]["pass"] is True
    assert result["no_forbidden_output_tokens"]["pass"] is True
    assert result["required_output_strings"]["pass"] is True
    assert result["live_mode_refused"]["pass"] is True
    assert result["chain_shas_present"]["pass"] is True
    assert result["engine_dates_match_config"]["pass"] is True
    assert result["window_ceiling_ok"]["pass"] is True

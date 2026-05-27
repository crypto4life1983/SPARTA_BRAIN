"""S12-D1 P3 BUILD smoke battery T1-T15.

Tests the strategy primitives + execution guard + driver-level invariants
on synthetic / metadata-only fixtures. T14 reads the audit-clean CSV
ONLY to verify sha256 + row count (metadata; no signal compute on
data outside this verification).

These tests are exercised during P3 BUILD; 15/15 must PASS for BUILD
verdict to be PASS. No live trading, no broker call, no Databento
call, no API-key access, no network IO.
"""
from __future__ import annotations

import hashlib
import math
import pathlib

import pytest

from external_research_hunter.s12_d1_mnq_c0_single_instrument_donchian_15_8_runner_harness import (
    runner_main,
    execution_guard,
    in_sample_driver,
    out_of_sample_driver,
)


# ============================================================================
# T1 - Donchian-15 entry signal on synthetic uptrend (long-side)
# ============================================================================

def test_T1_donchian_entry_long_breakout_on_uptrend():
    """A monotonic uptrend triggers donchian_entry_long_breakout at the bar
    whose close exceeds the 15-bar high (i.e., from bar 15 onwards)."""
    # Build 16 monotonically increasing closes; highs = closes; lows = closes - 1.
    closes = [100.0 + i for i in range(16)]
    highs = list(closes)
    lows = [c - 1.0 for c in closes]

    # At idx=15, the donchian-15 high over [0..14] is closes[14] = 114.0.
    # current close = closes[15] = 115.0 > 114.0 -> entry fires.
    fired = runner_main.donchian_entry_long_breakout(
        prices_highs=highs,
        current_close=closes[15],
        period_n=15,
        idx=15,
    )
    assert fired is True

    # Before idx=15 there is insufficient history -> no entry.
    fired_early = runner_main.donchian_entry_long_breakout(
        prices_highs=highs,
        current_close=closes[10],
        period_n=15,
        idx=10,
    )
    assert fired_early is False


# ============================================================================
# T2 - Donchian-15 entry signal on synthetic downtrend (short-side)
# ============================================================================

def test_T2_donchian_entry_short_breakout_on_downtrend():
    """A monotonic downtrend triggers donchian_entry_short_breakout at idx 15."""
    closes = [200.0 - i for i in range(16)]
    lows = list(closes)
    highs = [c + 1.0 for c in closes]

    # At idx=15, the donchian-15 low over [0..14] is closes[14] = 186.0.
    # current close = closes[15] = 185.0 < 186.0 -> short entry fires.
    fired = runner_main.donchian_entry_short_breakout(
        prices_lows=lows,
        current_close=closes[15],
        period_n=15,
        idx=15,
    )
    assert fired is True


# ============================================================================
# T3 - Donchian-8 exit signal on synthetic reversal
# ============================================================================

def test_T3_donchian_exit_long_on_reversal():
    """A reversal after an uptrend triggers donchian_exit_long when the
    current close drops below the 8-bar low."""
    # 8 stable highs/lows around $100, then a sharp drop below the 8-bar low.
    lows = [100.0] * 8
    highs = [101.0] * 8
    # idx = 8: the 8-bar low over [0..7] = 100.0; current close = 99.0 -> exit.
    fired = runner_main.donchian_exit_long(
        prices_lows=lows,
        current_close=99.0,
        period_m=8,
        idx=8,
    )
    assert fired is True

    # close == 100.0 is NOT strictly below -> no exit
    fired_eq = runner_main.donchian_exit_long(
        prices_lows=lows,
        current_close=100.0,
        period_m=8,
        idx=8,
    )
    assert fired_eq is False


# ============================================================================
# T4 - Wilder ATR(20) on a known reference series
# ============================================================================

def test_T4_wilder_atr_20_on_known_series():
    """Wilder ATR(20) on a constant-range series should equal that range."""
    # 21 bars; each bar has high - low = 2.0; closes = prior close (no gap).
    # True range = high - low = 2.0 for every bar -> ATR = 2.0 exactly.
    highs = [101.0] * 21
    lows = [99.0] * 21
    closes = [100.0] * 21

    atr = runner_main.wilder_atr(highs, lows, closes, period=20)
    assert atr is not None
    assert abs(atr - 2.0) < 1e-9

    # Too few bars -> None
    atr_short = runner_main.wilder_atr([100.0], [99.0], [99.5], period=20)
    assert atr_short is None


# ============================================================================
# T5 - ATR 2N stop placement
# ============================================================================

def test_T5_atr_2n_stop_placement():
    entry = 100.0
    atr = 1.5
    n = 2.0
    stop_long = runner_main.atr_stop_long(entry, atr, n)
    stop_short = runner_main.atr_stop_short(entry, atr, n)
    assert abs(stop_long - (100.0 - 3.0)) < 1e-9   # 97.0
    assert abs(stop_short - (100.0 + 3.0)) < 1e-9  # 103.0


# ============================================================================
# T6 - Position sizing at 1% risk on $100k
# ============================================================================

def test_T6_position_sizing_1pct_on_100k():
    """At $100,000 equity, 2N ATR stop, MNQ.c.0 tick = 0.25 / $0.50:
    risk_per_unit = 2 * ATR * (0.50 / 0.25) = 4 * ATR dollars.
    target risk = $1,000 -> units = floor(1000 / (4 * ATR)).

    For ATR = 50, risk_per_unit = $200, units = floor(1000/200) = 5.
    """
    units = runner_main.position_size_units(
        equity_usd=100_000.0,
        atr_value=50.0,
        stop_multiple_n=2.0,
        dollar_per_tick=0.50,
        tick_size=0.25,
        risk_fraction=0.01,
    )
    assert units == 5

    # Zero / invalid inputs return 0 (defensive)
    assert runner_main.position_size_units(0, 50, 2, 0.5, 0.25) == 0
    assert runner_main.position_size_units(100_000, 0, 2, 0.5, 0.25) == 0
    assert runner_main.position_size_units(100_000, 50, 2, 0, 0.25) == 0


# ============================================================================
# T7 - no-pyramid invariant under multiple successive long entries
# ============================================================================

def test_T7_no_pyramid_invariant_held():
    """ExecutionGuard.attempt_open_unit raises GuardViolation on the
    SECOND attempt to open a unit on the same symbol (max_units_per_market = 1)."""
    guard = execution_guard.ExecutionGuard()
    guard.attempt_open_unit("MNQ.c.0")  # first attempt: OK
    assert guard.open_units("MNQ.c.0") == 1
    with pytest.raises(execution_guard.GuardViolation):
        guard.attempt_open_unit("MNQ.c.0")  # second attempt: violation
    # After close, opening again should work
    guard.register_close_unit("MNQ.c.0")
    assert guard.open_units("MNQ.c.0") == 0
    guard.attempt_open_unit("MNQ.c.0")
    assert guard.open_units("MNQ.c.0") == 1


# ============================================================================
# T8 - Cost-stress S0 produces zero commission + zero slippage
# ============================================================================

def test_T8_cost_tier_S0_zero():
    out = runner_main.apply_cost_tier(
        base_commission_usd=0.74,
        base_fees_usd=0.36,
        base_slippage_ticks=(1, 1, 1),
        cost_tier_key="S0",
    )
    assert out["cost_scalar"] == 0.0
    assert out["slippage_scalar"] == 0.0
    assert out["commission_usd"] == 0.0
    assert out["fees_usd"] == 0.0
    assert out["slippage_ticks_entry"] == 0
    assert out["slippage_ticks_stop"] == 0
    assert out["slippage_ticks_exit"] == 0


# ============================================================================
# T9 - Cost-stress S1 baseline retail commission + fees + slippage
# ============================================================================

def test_T9_cost_tier_S1_baseline():
    out = runner_main.apply_cost_tier(
        base_commission_usd=0.74,
        base_fees_usd=0.36,
        base_slippage_ticks=(1, 1, 1),
        cost_tier_key="S1",
    )
    assert out["cost_scalar"] == 1.0
    assert out["slippage_scalar"] == 1.0
    assert abs(out["commission_usd"] - 0.74) < 1e-9
    assert abs(out["fees_usd"] - 0.36) < 1e-9
    assert out["slippage_ticks_entry"] == 1
    assert out["slippage_ticks_stop"] == 1
    assert out["slippage_ticks_exit"] == 1


# ============================================================================
# T10 - Cost-stress S4 extreme adversarial (3x scalars)
# ============================================================================

def test_T10_cost_tier_S4_extreme():
    out = runner_main.apply_cost_tier(
        base_commission_usd=0.74,
        base_fees_usd=0.36,
        base_slippage_ticks=(1, 1, 1),
        cost_tier_key="S4",
    )
    assert out["cost_scalar"] == 3.0
    assert out["slippage_scalar"] == 3.0
    assert abs(out["commission_usd"] - 2.22) < 1e-9
    assert abs(out["fees_usd"] - 1.08) < 1e-9
    assert out["slippage_ticks_entry"] == 3
    assert out["slippage_ticks_stop"] == 3
    assert out["slippage_ticks_exit"] == 3


# ============================================================================
# T11 - WARMUP_DAYS = 220: no order submission within first 220 days
# ============================================================================

def test_T11_warmup_220_invariant():
    guard = execution_guard.ExecutionGuard()
    guard.assert_warmup_220()  # static check passes

    # day_index 0..219 is within warmup -> raises
    for day_index in (0, 50, 100, 200, 219):
        with pytest.raises(execution_guard.GuardViolation):
            guard.assert_warmup_passed(day_index)

    # day_index 220 onwards is post-warmup -> OK
    guard.assert_warmup_passed(220)
    guard.assert_warmup_passed(500)


# ============================================================================
# T12 - RTH window 09:30-16:00 ET correctly held in CONFIG
# ============================================================================

def test_T12_rth_window_locked():
    rth = runner_main.CONFIG["rth_window"]
    assert rth == "09:30-16:00 ET America/New_York"
    # The daily Databento schema means each bar is RTH-aggregated upstream;
    # this test confirms the CONFIG value is preserved byte-equivalent.


# ============================================================================
# T13 - K4 max-drawdown threshold ($50,000 = 50% of $100k) tracked correctly
# ============================================================================

def test_T13_k4_max_drawdown_threshold():
    """K4 fires when equity drops > 50% of starting cash in absolute dollars."""
    starting_cash = 100_000.0

    # Curve never drops below threshold -> no breach
    safe_curve = [100_000.0, 120_000.0, 110_000.0, 80_000.0, 90_000.0]
    assert runner_main.k4_drawdown_breach(safe_curve, starting_cash, k4_fraction=0.50) is False
    # peak = 120k; min = 80k; drawdown = 40k; threshold = 50k -> 40k <= 50k -> no breach

    # Curve drops > 50k from peak -> breach
    breach_curve = [100_000.0, 120_000.0, 110_000.0, 65_000.0]
    # peak = 120k; min after = 65k; drawdown = 55k > 50k -> breach
    assert runner_main.k4_drawdown_breach(breach_curve, starting_cash, k4_fraction=0.50) is True

    # CONFIG abs threshold sanity
    assert runner_main.CONFIG["k4_max_drawdown_fraction"] == 0.50
    assert runner_main.CONFIG["k4_max_drawdown_abs_usd"] == 50_000.0


# ============================================================================
# T14 - Audit-clean MNQ.c.0 CSV row count + sha256 integrity
# ============================================================================

def test_T14_csv_row_and_sha_integrity():
    """The audit-clean MNQ.c.0 CSV must be present, have the exact sha256
    locked at SEAL, and the expected data-row count.

    NOTE: This is metadata-only verification (sha256 + row count). No
    signal compute, no derivation of prices, no driver invocation.
    """
    expected_sha = (
        "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e"
    )
    expected_rows = 2066
    csv_path = pathlib.Path(runner_main.CONFIG["data_csv_path"])

    assert csv_path.exists(), (
        f"audit-clean MNQ.c.0 CSV not present at {csv_path!s}"
    )
    raw = csv_path.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    assert sha == expected_sha, (
        f"CSV sha256 mismatch: expected {expected_sha!r}; got {sha!r}"
    )
    data_rows = len(raw.decode("utf-8").splitlines()) - 1  # subtract header
    assert data_rows == expected_rows, (
        f"CSV data-row count mismatch: expected {expected_rows}; got {data_rows}"
    )

    # Also: the driver helper agrees
    rows, sha_via_driver = in_sample_driver.assert_csv_present_and_byte_stable()
    assert rows == expected_rows
    assert sha_via_driver == expected_sha

    rows2, sha2 = out_of_sample_driver.assert_csv_present_and_byte_stable()
    assert rows2 == expected_rows
    assert sha2 == expected_sha


# ============================================================================
# T15 - IS / OOS window boundary: no leakage between phases
# ============================================================================

def test_T15_is_oos_window_no_leakage():
    """The IS window end (2023-12-29) must precede the OOS window start
    (2024-01-02) strictly. No overlap. Each driver hard-codes its
    window constants."""
    import datetime
    is_end = datetime.date.fromisoformat(in_sample_driver.IN_SAMPLE_END)
    oos_start = datetime.date.fromisoformat(out_of_sample_driver.OUT_OF_SAMPLE_START)
    assert is_end < oos_start, (
        f"IS end {is_end} must be strictly before OOS start {oos_start}"
    )

    # Sanity: the driver constants are also locked in CONFIG (byte-equivalent)
    assert in_sample_driver.IN_SAMPLE_START == runner_main.CONFIG["is_window_start"]
    assert in_sample_driver.IN_SAMPLE_END == runner_main.CONFIG["is_window_end"]
    assert out_of_sample_driver.OUT_OF_SAMPLE_START == runner_main.CONFIG["oos_window_start"]
    assert out_of_sample_driver.OUT_OF_SAMPLE_END == runner_main.CONFIG["oos_window_end"]

    # OOS driver structurally cannot inspect an IS date (the window filter
    # excludes it)
    fake_is_date_row = (
        "2020-01-15 00:00:00+00:00,35,1,1,100.0,101.0,99.0,100.5,1000,MNQ.c.0"
    )
    # We don't actually pass this to a real reader; we just verify the
    # _is_within_window helper agrees the OOS driver would exclude it.
    in_oos_window = out_of_sample_driver._is_within_window(
        "2020-01-15",
        out_of_sample_driver.OUT_OF_SAMPLE_START,
        out_of_sample_driver.OUT_OF_SAMPLE_END,
    )
    assert in_oos_window is False, (
        "OOS driver must not consider an IS date as in-window"
    )

    # IS driver excludes an OOS date for symmetry
    in_is_window = in_sample_driver._is_within_window(
        "2024-06-15",
        in_sample_driver.IN_SAMPLE_START,
        in_sample_driver.IN_SAMPLE_END,
    )
    assert in_is_window is False, (
        "IS driver must not consider an OOS date as in-window"
    )

    # ExecutionGuard's static invariants must hold at construction.
    guard = execution_guard.ExecutionGuard()
    guard.assert_all_static_invariants_held()

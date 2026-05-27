"""S12-D1 runner_main: central CONFIG + pure-function strategy primitives.

This module is the single source of truth for sealed-spec parameters
and the implementation of the F1 mechanic primitives:
- Donchian-15/8 entry/exit channel break detection
- Wilder ATR(20)
- 2N stop placement
- 1% per-trade risk position sizing
- Cost-tier scaling (S0/S1/S2/S3/S4)

The CONFIG dict here is the byte-equivalent canonical configuration
that the IS and OOS drivers both lazy-import. NO parameter is ever
mutated post-import.

This module does NOT fetch data. It does NOT call Databento. It does
NOT access DATABENTO_API_KEY. It does NOT make any network call. It
does NOT submit any order. It does NOT invoke any brokerage.

P3 BUILD authors this module; it does not run the strategy.
"""
from __future__ import annotations

import math
from typing import Iterable, List, Optional, Sequence, Tuple

# ----------------------------------------------------------------------------
# Sealed-spec CONFIG (byte-equivalent to docs/.../s12_d1_..._tier_n_spec.md)
# ----------------------------------------------------------------------------

CANDIDATE_RECORD_ID = (
    "s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history"
)

CONFIG = {
    # Mechanic family (LOCKED at PLAN; LOCKED at SEAL; no retreat to 55/20)
    "mechanic_family": "F1",
    "signal_direction": "long_and_short_bi_directional",
    "donchian_entry_period_N": 15,
    "donchian_exit_period_M": 8,
    "no_pyramid": True,
    "max_units_per_market": 1,
    # Universe (LOCKED; widening + substitution FORBIDDEN post-seal)
    "universe": ("MNQ.c.0",),
    "universe_kind": "single_fixed_instrument_continuous_micro_futures",
    # Sizing + execution (DA1=A, DA2=A, DA3=A, DA4=B, DA5=A)
    "atr_period": 20,
    "atr_kind": "wilder",
    "stop_multiple_n": 2.0,
    "portfolio_risk_per_trade_pct": 1.0,
    "starting_cash_mnq_equivalent_usd": 100_000.0,  # DA4=B revised at SEAL
    "k4_max_drawdown_fraction": 0.50,
    "k4_max_drawdown_abs_usd": 50_000.0,  # 50% x $100k
    "warmup_days": 220,
    "rth_window": "09:30-16:00 ET America/New_York",
    # Contract specs (DA8-DA10 framework-locked)
    "tick_size_mnq_c0": 0.25,
    "dollar_per_tick_mnq_c0": 0.50,
    "commission_per_round_trip_usd": 0.74,
    "fees_per_round_trip_usd": 0.36,
    "slippage_ticks_entry_stop_exit": (1, 1, 1),
    # Cost-stress (DA7 framework-locked; 5-tier; carried byte-equivalent)
    "cost_tiers": {
        "S0": {"cost_scalar": 0.0, "slippage_scalar": 0.0, "note": "zero-cost ideal"},
        "S1": {"cost_scalar": 1.0, "slippage_scalar": 1.0, "note": "baseline retail"},
        "S2": {"cost_scalar": 1.5, "slippage_scalar": 1.5, "note": "stressed retail"},
        "S3": {"cost_scalar": 2.0, "slippage_scalar": 2.0, "note": "adversarial"},
        "S4": {"cost_scalar": 3.0, "slippage_scalar": 3.0, "note": "extreme adversarial"},
    },
    # K-gates (carried byte-equivalent from s11-d1 with single-instrument simplifications)
    "k9_threshold_min_closed_trades": 100,
    # Data source
    "data_csv_path": (
        "data/s10_d1_mnq_mgc_databento_long_history/raw/"
        "MNQ_1d_2019-05-13_2025-12-30.csv"
    ),
    "data_csv_sha256": (
        "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e"
    ),
    "data_csv_expected_data_rows": 2066,
    "new_databento_fetch_required": False,
    # Windows (LOCKED at SEAL)
    "is_window_start": "2019-05-13",
    "is_window_end": "2023-12-29",
    "oos_window_start": "2024-01-02",
    "oos_window_end": "2025-12-30",
    # Negative invariants summary (informational; actual enforcement in execution_guard)
    "no_live_trading": True,
    "no_strategy_lab_promotion": True,
    "no_review_queue_mutation": True,
    "no_brokerage_connection": True,
    "no_external_network_at_runtime": True,
    "no_databento_at_runtime": True,
    "no_databento_api_key_access": True,
    "no_pyramid_per_signal": True,
    "single_instrument_universe_NO_widening_post_seal": True,
    "donchian_15_8_locked_at_plan_no_retreat_to_55_20": True,
}

# Pre-anchored predecessor seal fingerprints (informational; runtime asserts elsewhere)
PREDECESSOR_SEALS = {
    "tier_n_spec": "422bbbff75f24816ec743104b730178298de36f395e43ac126ba52a7d82c03a1",
    "p1_plan_lock": "f19a7a4c9967cefb9bcf05fffba6a89b16dde8491b1d94e6a3b29df8f89a2c94",
    "p2_phase_2_plan": "0bcfe99ca1dc1010dd27ddf12da3baf6f3d4a49d7c7c20fd118b343c20abbaf4",
    "draft_review": "860e766e6933751d97cd7821fff6911de133772aaec3ac778754d62e6889b8d8",
    "audit_clean_mnq_c0_csv_sha256": (
        "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e"
    ),
}


# ----------------------------------------------------------------------------
# Pure-function strategy primitives
# ----------------------------------------------------------------------------

def wilder_atr(
    highs: Sequence[float],
    lows: Sequence[float],
    closes: Sequence[float],
    period: int = 20,
) -> Optional[float]:
    """Wilder Average True Range over the most-recent `period` bars.

    Returns the smoothed ATR value (Wilder smoothing) or None if there
    are fewer than `period + 1` bars (need a prior close).
    """
    n = len(closes)
    if n < period + 1:
        return None
    if not (len(highs) == n and len(lows) == n):
        raise ValueError("highs/lows/closes must have equal length")

    # True Range series (length n - 1; aligned to closes[1..n-1])
    tr = []
    for i in range(1, n):
        hi = highs[i]
        lo = lows[i]
        prev_close = closes[i - 1]
        tr_i = max(hi - lo, abs(hi - prev_close), abs(lo - prev_close))
        tr.append(tr_i)

    # Initial ATR: simple mean of first `period` TR values
    atr = sum(tr[:period]) / period
    # Wilder smoothing for the rest
    for i in range(period, len(tr)):
        atr = (atr * (period - 1) + tr[i]) / period
    return atr


def donchian_high(prices_highs: Sequence[float], period: int, idx: int) -> Optional[float]:
    """Highest high over the `period` bars ENDING at idx-1 (exclusive of idx).

    Returns None if there are fewer than `period` prior bars.
    """
    if idx < period:
        return None
    return max(prices_highs[idx - period : idx])


def donchian_low(prices_lows: Sequence[float], period: int, idx: int) -> Optional[float]:
    """Lowest low over the `period` bars ENDING at idx-1 (exclusive of idx)."""
    if idx < period:
        return None
    return min(prices_lows[idx - period : idx])


def donchian_entry_long_breakout(
    prices_highs: Sequence[float], current_close: float, period_n: int, idx: int
) -> bool:
    """Long entry signal: current close strictly above the donchian-N high.

    The donchian-N high is computed over the `period_n` bars ENDING at idx-1
    (so the current bar is not in the window).
    """
    ref = donchian_high(prices_highs, period_n, idx)
    if ref is None:
        return False
    return current_close > ref


def donchian_entry_short_breakout(
    prices_lows: Sequence[float], current_close: float, period_n: int, idx: int
) -> bool:
    """Short entry signal: current close strictly below the donchian-N low."""
    ref = donchian_low(prices_lows, period_n, idx)
    if ref is None:
        return False
    return current_close < ref


def donchian_exit_long(
    prices_lows: Sequence[float], current_close: float, period_m: int, idx: int
) -> bool:
    """Long exit signal: current close strictly below the donchian-M low.

    Used to close an open long position.
    """
    ref = donchian_low(prices_lows, period_m, idx)
    if ref is None:
        return False
    return current_close < ref


def donchian_exit_short(
    prices_highs: Sequence[float], current_close: float, period_m: int, idx: int
) -> bool:
    """Short exit signal: current close strictly above the donchian-M high."""
    ref = donchian_high(prices_highs, period_m, idx)
    if ref is None:
        return False
    return current_close > ref


def atr_stop_long(entry_price: float, atr_value: float, stop_multiple_n: float = 2.0) -> float:
    """Stop placement for a long position: entry - N * ATR."""
    return entry_price - stop_multiple_n * atr_value


def atr_stop_short(entry_price: float, atr_value: float, stop_multiple_n: float = 2.0) -> float:
    """Stop placement for a short position: entry + N * ATR."""
    return entry_price + stop_multiple_n * atr_value


def position_size_units(
    equity_usd: float,
    atr_value: float,
    stop_multiple_n: float,
    dollar_per_tick: float,
    tick_size: float,
    risk_fraction: float = 0.01,
) -> int:
    """Compute integer position size in contracts at `risk_fraction` of equity.

    risk_per_unit_usd = stop_multiple_n * atr_value * (dollar_per_tick / tick_size)
    target_risk_usd = equity_usd * risk_fraction
    units = floor(target_risk_usd / risk_per_unit_usd)

    Returns at least 0 (no short-sale-of-cash semantics; integer contracts only).
    """
    if equity_usd <= 0 or atr_value <= 0 or tick_size <= 0 or dollar_per_tick <= 0:
        return 0
    risk_per_unit_usd = stop_multiple_n * atr_value * (dollar_per_tick / tick_size)
    if risk_per_unit_usd <= 0:
        return 0
    target_risk_usd = equity_usd * risk_fraction
    return max(0, int(math.floor(target_risk_usd / risk_per_unit_usd)))


def apply_cost_tier(
    base_commission_usd: float,
    base_fees_usd: float,
    base_slippage_ticks: Tuple[int, int, int],
    cost_tier_key: str,
) -> dict:
    """Scale base costs by the locked cost-tier scalars.

    The slippage_scalar multiplies each tick count (entry/stop/exit) before
    converting to dollars elsewhere; cost_scalar multiplies commission + fees.
    Tier S0 produces zero commission/fees AND zero slippage (the
    'profitable kernel exists' ideal). Tier S4 is 3x baseline (extreme).
    """
    tiers = CONFIG["cost_tiers"]
    if cost_tier_key not in tiers:
        raise ValueError(
            f"Unknown cost_tier_key {cost_tier_key!r}; "
            f"allowed: {tuple(tiers.keys())}"
        )
    tier = tiers[cost_tier_key]
    cs = tier["cost_scalar"]
    ss = tier["slippage_scalar"]
    return {
        "cost_tier_key": cost_tier_key,
        "commission_usd": base_commission_usd * cs,
        "fees_usd": base_fees_usd * cs,
        "slippage_ticks_entry": base_slippage_ticks[0] * ss,
        "slippage_ticks_stop": base_slippage_ticks[1] * ss,
        "slippage_ticks_exit": base_slippage_ticks[2] * ss,
        "cost_scalar": cs,
        "slippage_scalar": ss,
    }


def k4_drawdown_breach(
    equity_curve_usd: Iterable[float],
    starting_cash_usd: float,
    k4_fraction: float = 0.50,
) -> bool:
    """K4 max-drawdown threshold breach.

    Returns True iff at any point the equity dropped by more than
    `k4_fraction` of `starting_cash_usd` (in absolute dollars).
    """
    threshold_abs = starting_cash_usd * k4_fraction
    peak = starting_cash_usd
    for eq in equity_curve_usd:
        if eq > peak:
            peak = eq
        if (peak - eq) > threshold_abs:
            return True
    return False


def warmup_passed(day_index: int, warmup_days: int = 220) -> bool:
    """True iff day_index >= warmup_days (zero-indexed).

    P3 BUILD encodes the warmup invariant here so unit tests can verify it
    without invoking a full driver run.
    """
    return day_index >= warmup_days


# ----------------------------------------------------------------------------
# Module self-test sentinel (informational; never invoked at BUILD)
# ----------------------------------------------------------------------------

def _module_invariants_sanity():
    """Internal sanity: assert CONFIG values that BUILD locks at SEAL.

    Not invoked at BUILD; future-phase code MAY call this from a driver's
    seal-inheritance check.
    """
    assert CONFIG["donchian_entry_period_N"] == 15
    assert CONFIG["donchian_exit_period_M"] == 8
    assert CONFIG["atr_period"] == 20
    assert CONFIG["atr_kind"] == "wilder"
    assert CONFIG["stop_multiple_n"] == 2.0
    assert CONFIG["portfolio_risk_per_trade_pct"] == 1.0
    assert CONFIG["starting_cash_mnq_equivalent_usd"] == 100_000.0
    assert CONFIG["max_units_per_market"] == 1
    assert CONFIG["no_pyramid"] is True
    assert CONFIG["warmup_days"] == 220
    assert CONFIG["k4_max_drawdown_fraction"] == 0.50
    assert CONFIG["k9_threshold_min_closed_trades"] == 100
    assert tuple(CONFIG["universe"]) == ("MNQ.c.0",)
    assert set(CONFIG["cost_tiers"].keys()) == {"S0", "S1", "S2", "S3", "S4"}
    return True

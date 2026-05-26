"""s9 cross-asset RSI-2 mean-reversion signal module (ETF-proxy track).

Pure deterministic function from a LoadedSymbol (from the Step 03
loader) to a SignalResult of per-bar long-only RSI-2 trigger flags.
Operates on in-sample-window dates only. Long-only by design: the
dataclass shape itself enforces no short side at the type level.

In-sample-only structural enforcement (five layers):

  1. No public function accepts a window= / lookback= / threshold=
     / series= / enable_short= parameter; the caller cannot substitute.
  2. IN_SAMPLE_WINDOW is a hardcoded module-level constant.
  3. The eligibility predicate evaluates the bar date against
     IN_SAMPLE_WINDOW; out-of-sample and post-out-of-sample dates
     are excluded from the iteration loop.
  4. After the loop, the result attests that the last SignalEvent
     date is on or before IN_SAMPLE_WINDOW[1].
  5. A defensive scan asserts no SignalEvent date lies in
     OUT_OF_SAMPLE_WINDOW or POST_OOS_DIAGNOSTIC_WINDOW; any
     violation raises SignalOosBlockedError.

RSI(2) computation (Wilder smoothing; per signal spec section 8):

  delta_i = adj_close[i] - adj_close[i-1]  for i >= 1
  gain_i  = max(delta_i, 0)
  loss_i  = max(-delta_i, 0)

  Seed at bar 2:
    avg_gain[2] = (gain_1 + gain_2) / 2
    avg_loss[2] = (loss_1 + loss_2) / 2

  Wilder smoothing for i > 2 (RSI_LOOKBACK = 2):
    avg_gain[i] = (avg_gain[i-1] + gain_i) / 2
    avg_loss[i] = (avg_loss[i-1] + loss_i) / 2

  rs  = avg_gain / avg_loss
  rsi = 100.0 - (100.0 / (1.0 + rs))

  Conventions for degenerate cases:
    avg_loss == 0 and avg_gain > 0  -> rsi = 100.0  (all gains)
    avg_gain == 0 and avg_loss > 0  -> rsi = 0.0    (all losses)
    avg_loss == 0 and avg_gain == 0 -> rsi = 50.0   (no movement; neutral)

  No look-ahead: bar i RSI uses only adj_close[0..i].

Trigger rules:

  entry_long_triggered = (rsi_value < RSI_OVERSOLD_ENTRY_THRESHOLD)  # < 10
  exit_long_triggered  = (rsi_value > RSI_EXIT_THRESHOLD)            # > 50

The module records the flags for every signal-eligible IS bar
regardless of any hypothetical position state. Position state is
a simulator (P7/P8) concern, not a signal concern.

This module does not:

  - import any vendor SDK, network library, or broker SDK;
  - perform any file IO;
  - read any environment variable beginning with a credential prefix;
  - disable SSL verification;
  - compute any per-day percentage difference, log price difference,
    cumulative price difference, or annualized growth measure;
  - compute any performance statistic family that downstream phases
    will later compute (risk-adjusted ratios, loss-side metrics,
    pairwise dependence measures);
  - track position state, size positions, set stops, decide entry
    timing, simulate fills, or compute execution-side costs;
  - emit any trade order, trade id, fill price, or order id;
  - inspect or compute any value for any bar whose date is in
    OUT_OF_SAMPLE_WINDOW or POST_OOS_DIAGNOSTIC_WINDOW.

All of those are downstream concerns belonging to the simulator
(P7/P8) or the later result-aggregation phases (P9+), each requiring
its own separately authorized plan.

Spec anchors:
  Tier-N:    docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md
             sha256 6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409
  Signal:    docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md
             sha256 59e5f401232f19342777445a0d992d1df23dda95a71419379e1daded89e9a0c9
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

# -- Public constants ----------------------------------------------------
RSI_LOOKBACK = 2
RSI_OVERSOLD_ENTRY_THRESHOLD = 10.0
RSI_EXIT_THRESHOLD = 50.0

IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")

# Private out-of-sample window constants; used only for the defensive
# post-loop scan. Not exported; the public API exposes nothing that
# could be mistaken for permission to operate against these windows.
_OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")
_POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")

_ALLOWED_SYMBOLS = frozenset({"SPY", "TLT", "GLD", "USO"})


# -- Exception tree ------------------------------------------------------
class SignalError(Exception):
    """Base for every signal-module refusal mode."""


class SignalInputError(SignalError):
    """Input not a LoadedSymbol or LoadedSymbol structurally invalid."""


class SignalOosBlockedError(SignalError):
    """Attempt to compute a signal for an out-of-sample or
    post-out-of-sample bar; structurally refused."""


class SignalParameterOverrideError(SignalError):
    """Attempt to override a hardcoded parameter via kwargs."""


# -- Result dataclasses --------------------------------------------------
@dataclass(frozen=True)
class SignalEvent:
    """Per-bar signal event.

    Long-only by type: only entry_long_triggered and exit_long_triggered
    are exposed; no opposite-side trigger fields are defined on this
    dataclass. No per-trade economics, no sizing, no stop, no position
    state, no order id, no trade id. The dataclass shape itself
    enforces the long-only, signal-only contract from the spec.
    """
    date: str
    bar_index: int
    rsi_value: float
    today_adj_close: float
    entry_long_triggered: bool
    exit_long_triggered: bool


@dataclass(frozen=True)
class SignalResult:
    """Per-symbol in-sample-only signal computation result."""
    symbol: str
    csv_sha256_observed: str
    window: tuple
    bars_in_window: int
    first_signal_eligible_bar_index: int
    first_signal_eligible_date: str
    last_signal_eligible_bar_index: int
    last_signal_eligible_date: str
    signals: tuple
    oos_signal_intentionally_omitted: bool
    post_oos_signal_intentionally_omitted: bool


@dataclass(frozen=True)
class CrossSymbolSignalResult:
    """Per-bundle (four-symbol) in-sample-only signal computation result."""
    per_symbol: Mapping
    cross_symbol_bars_in_window_equal: bool
    cross_symbol_first_eligible_date_equal: bool
    cross_symbol_last_eligible_date_equal: bool
    oos_signal_intentionally_omitted: bool
    post_oos_signal_intentionally_omitted: bool


# -- Private helpers -----------------------------------------------------
def _looks_like_loaded_symbol(obj: Any) -> bool:
    """Duck-type check for the fields the s9 signal module reads."""
    return all(
        hasattr(obj, attr)
        for attr in (
            "symbol", "dates", "adj_close",
            "csv_path", "csv_sha256",
        )
    )


def _date_in_window(d: str, window: tuple) -> bool:
    return window[0] <= d <= window[1]


def _compute_rsi_series(adj_close: tuple) -> list:
    """Compute Wilder-smoothed RSI(RSI_LOOKBACK) for every bar from
    index 0 to len(adj_close)-1. Returns a list of floats; values at
    indices 0 .. RSI_LOOKBACK-1 are None (insufficient warmup). For
    i >= RSI_LOOKBACK, the value is the canonical RSI(2) per spec
    section 8.
    """
    n = len(adj_close)
    rsi_series: list = [None] * n
    if n < RSI_LOOKBACK + 1:
        return rsi_series

    # Pre-compute deltas, gains, losses for i = 1 .. n-1
    # (delta_0 is undefined; loops start at i = 1).
    # We do not need to store the full delta vector; we only need a
    # running avg_gain / avg_loss with Wilder smoothing.

    # Seed at i == RSI_LOOKBACK == 2:
    # avg_gain[2] = (gain_1 + gain_2) / 2
    # avg_loss[2] = (loss_1 + loss_2) / 2
    avg_gain = 0.0
    avg_loss = 0.0
    for j in range(1, RSI_LOOKBACK + 1):
        delta = adj_close[j] - adj_close[j - 1]
        gain = delta if delta > 0 else 0.0
        loss = -delta if delta < 0 else 0.0
        avg_gain += gain
        avg_loss += loss
    avg_gain /= float(RSI_LOOKBACK)
    avg_loss /= float(RSI_LOOKBACK)

    # Compute RSI at index RSI_LOOKBACK == 2
    rsi_series[RSI_LOOKBACK] = _rsi_from_avgs(avg_gain, avg_loss)

    # Wilder smoothing for i > RSI_LOOKBACK
    for i in range(RSI_LOOKBACK + 1, n):
        delta = adj_close[i] - adj_close[i - 1]
        gain = delta if delta > 0 else 0.0
        loss = -delta if delta < 0 else 0.0
        avg_gain = ((RSI_LOOKBACK - 1) * avg_gain + gain) / float(RSI_LOOKBACK)
        avg_loss = ((RSI_LOOKBACK - 1) * avg_loss + loss) / float(RSI_LOOKBACK)
        rsi_series[i] = _rsi_from_avgs(avg_gain, avg_loss)

    return rsi_series


def _rsi_from_avgs(avg_gain: float, avg_loss: float) -> float:
    """Convert (avg_gain, avg_loss) to RSI per spec section 8 conventions."""
    if avg_loss == 0.0 and avg_gain == 0.0:
        return 50.0
    if avg_loss == 0.0:
        return 100.0
    if avg_gain == 0.0:
        return 0.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


# -- Public API ----------------------------------------------------------
def compute_signals(loaded: Any, **kwargs) -> SignalResult:
    """Compute in-sample-only RSI(2) long-only trigger flags for one
    symbol. Returns a SignalResult with one SignalEvent per signal-
    eligible in-sample bar. Raises SignalError subclass on any
    structural refusal.
    """
    if kwargs:
        raise SignalParameterOverrideError(
            f"unexpected kwargs {sorted(kwargs.keys())}; only "
            f"(loaded,) accepted; the s9 mechanic is locked at the "
            f"Tier-N spec"
        )
    if not _looks_like_loaded_symbol(loaded):
        raise SignalInputError(
            f"input does not look like a LoadedSymbol (missing fields); "
            f"got type={type(loaded).__name__}"
        )
    sym = getattr(loaded, "symbol", None)
    if sym not in _ALLOWED_SYMBOLS:
        raise SignalInputError(
            f"unknown symbol {sym!r}; expected one of {sorted(_ALLOWED_SYMBOLS)}"
        )
    dates = loaded.dates
    adj = loaded.adj_close
    if not isinstance(dates, tuple):
        raise SignalInputError(
            f"{sym} dates must be a tuple; got {type(dates).__name__}"
        )
    if not isinstance(adj, tuple):
        raise SignalInputError(
            f"{sym} adj_close must be a tuple; got {type(adj).__name__}"
        )
    if len(dates) != len(adj):
        raise SignalInputError(
            f"{sym} dates/adj_close length mismatch: {len(dates)} vs {len(adj)}"
        )

    # Read the hardcoded constants into local names once; any attempt
    # to monkey-patch module-level IN_SAMPLE_WINDOW after this point
    # cannot affect the loop because the loop uses these locals.
    is_lo, is_hi = IN_SAMPLE_WINDOW
    oos_lo, oos_hi = _OUT_OF_SAMPLE_WINDOW
    post_lo, post_hi = _POST_OOS_DIAGNOSTIC_WINDOW
    lookback = RSI_LOOKBACK
    entry_thr = RSI_OVERSOLD_ENTRY_THRESHOLD
    exit_thr = RSI_EXIT_THRESHOLD

    # bars_in_window: count of loaded bars whose date is in IS window
    bars_in_window = sum(1 for d in dates if is_lo <= d <= is_hi)

    # Compute RSI series (None at indices < lookback)
    rsi_series = _compute_rsi_series(adj)

    signals_list = []
    first_idx = -1
    last_idx = -1
    for i in range(len(dates)):
        d = dates[i]
        if not (is_lo <= d <= is_hi):
            continue
        if i < lookback:
            continue
        rsi_val = rsi_series[i]
        if rsi_val is None:
            # Should not happen given the lookback check, but defensive
            continue
        ev = SignalEvent(
            date=d,
            bar_index=i,
            rsi_value=rsi_val,
            today_adj_close=adj[i],
            entry_long_triggered=(rsi_val < entry_thr),
            exit_long_triggered=(rsi_val > exit_thr),
        )
        signals_list.append(ev)
        if first_idx == -1:
            first_idx = i
        last_idx = i

    if first_idx == -1:
        raise SignalInputError(
            f"{sym} no signal-eligible in-sample bar found "
            f"(no bar in {IN_SAMPLE_WINDOW} with index >= {lookback})"
        )

    first_date = dates[first_idx]
    last_date = dates[last_idx]

    # Layer 4: post-loop assertion that the last event date is on or
    # before the in-sample-window end.
    if last_date > is_hi:
        raise SignalOosBlockedError(
            f"{sym} last signal date {last_date} exceeds in-sample end {is_hi}"
        )

    # Layer 5: defensive scan that no event date is in out-of-sample or
    # post-out-of-sample windows.
    for ev in signals_list:
        if oos_lo <= ev.date <= oos_hi:
            raise SignalOosBlockedError(
                f"{sym} signal date {ev.date} falls in out-of-sample window; "
                f"structural enforcement failure"
            )
        if post_lo <= ev.date <= post_hi:
            raise SignalOosBlockedError(
                f"{sym} signal date {ev.date} falls in post-out-of-sample "
                f"window; structural enforcement failure"
            )

    return SignalResult(
        symbol=sym,
        csv_sha256_observed=loaded.csv_sha256,
        window=IN_SAMPLE_WINDOW,
        bars_in_window=bars_in_window,
        first_signal_eligible_bar_index=first_idx,
        first_signal_eligible_date=first_date,
        last_signal_eligible_bar_index=last_idx,
        last_signal_eligible_date=last_date,
        signals=tuple(signals_list),
        oos_signal_intentionally_omitted=True,
        post_oos_signal_intentionally_omitted=True,
    )


def compute_signals_all(data: Any, **kwargs) -> CrossSymbolSignalResult:
    """Compute in-sample-only RSI(2) long-only trigger flags for the
    four-symbol bundle. Calls compute_signals per symbol then attests
    cross-symbol consistency.
    """
    if kwargs:
        raise SignalParameterOverrideError(
            f"unexpected kwargs {sorted(kwargs.keys())}; only "
            f"(data,) accepted"
        )
    if not isinstance(data, Mapping):
        raise SignalInputError(
            f"compute_signals_all input must be a Mapping; "
            f"got {type(data).__name__}"
        )
    if set(data.keys()) != _ALLOWED_SYMBOLS:
        raise SignalInputError(
            f"compute_signals_all keys {sorted(data.keys())} != "
            f"expected {sorted(_ALLOWED_SYMBOLS)}"
        )
    per_symbol = {}
    for sym in sorted(_ALLOWED_SYMBOLS):
        per_symbol[sym] = compute_signals(data[sym])

    bars_counts = {s: r.bars_in_window for s, r in per_symbol.items()}
    first_dates = {s: r.first_signal_eligible_date for s, r in per_symbol.items()}
    last_dates = {s: r.last_signal_eligible_date for s, r in per_symbol.items()}

    return CrossSymbolSignalResult(
        per_symbol=per_symbol,
        cross_symbol_bars_in_window_equal=(len(set(bars_counts.values())) == 1),
        cross_symbol_first_eligible_date_equal=(len(set(first_dates.values())) == 1),
        cross_symbol_last_eligible_date_equal=(len(set(last_dates.values())) == 1),
        oos_signal_intentionally_omitted=True,
        post_oos_signal_intentionally_omitted=True,
    )

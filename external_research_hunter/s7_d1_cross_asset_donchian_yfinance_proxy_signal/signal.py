"""Signal-computation module for s7 D1 cross-asset entry/exit channel triggers.

Pure deterministic function from a LoadedSymbol (from the Step 03 loader)
to a SignalResult of per-bar channel-breakout trigger flags. Operates on
in-sample-window dates only. Bidirectional (long and short triggers per
spec sec 5). No simulator state, no sizing, no entry-timing decision,
no fills, no PnL aggregation.

In-sample-only structural enforcement (five layers):

  1. No public function accepts a window= parameter; the caller cannot
     substitute the in-sample window.
  2. IN_SAMPLE_WINDOW is a hardcoded module-level constant.
  3. The eligibility predicate `is_eligible(i)` evaluates the bar date
     against IN_SAMPLE_WINDOW; out-of-sample and post-out-of-sample
     dates are excluded from the iteration loop.
  4. After the loop, the result attests that the last SignalEvent date
     is on or before IN_SAMPLE_WINDOW[1].
  5. A defensive scan asserts no SignalEvent date lies in
     OUT_OF_SAMPLE_WINDOW or POST_OOS_DIAGNOSTIC_WINDOW; any violation
     raises SignalOosBlockedError.

Channel construction (sourced from parent spec section 5; not re-designed
here): the entry channel high at bar index i is the maximum of the prior
ENTRY_CHANNEL_LOOKBACK loaded high values (indices i - ENTRY_CHANNEL_LOOKBACK
through i - 1 inclusive; NOT including the current bar i). The entry
channel low is the minimum of the prior ENTRY_CHANNEL_LOOKBACK loaded low
values over the same window. Exit channel high/low use the same formula
with EXIT_CHANNEL_LOOKBACK. Channels read from the high and low columns
only; close and adj_close are not used for channel construction. The
current bar close is carried through onto SignalEvent.today_close as a
diagnostic only.

Trigger rules (sourced from parent spec section 5; not re-designed):

  entry_long_triggered  = today_high > entry_channel_high_55
  entry_short_triggered = today_low  < entry_channel_low_55
  exit_long_triggered   = today_low  < exit_channel_low_20
  exit_short_triggered  = today_high > exit_channel_high_20

This module does not:

  - import any vendor SDK, any network library, any result-aggregation
    engine;
  - perform any file IO;
  - call os.environ to read any secret or vendor key;
  - compute any rolling moving average, exponential moving average,
    or any pairwise dependence measure;
  - compute any per-day percentage difference, log price difference,
    cumulative price difference, or annualized growth measure;
  - compute any performance statistic family that downstream phases
    will later compute (risk-adjusted ratios, loss-side metrics, etc.);
  - track position state, size positions, set stops, decide entry
    timing, simulate fills, or compute execution-side costs;
  - emit any trade order, trade id, fill price, or order id;
  - inspect or compute any value for any bar whose date is in
    OUT_OF_SAMPLE_WINDOW or POST_OOS_DIAGNOSTIC_WINDOW.

All of those are downstream concerns belonging to the simulator
(Step 06+) or the later result-aggregation phases (Step 07+), each
requiring its own separately authorized plan.

Spec anchor:
  docs/s7_d1_cross_asset_donchian_step_05_signal_computation_specification_plan.md
  sha256 6e039d352af7a7f20c99b1e26173f07539417a7f65b3c458458aa3ca1c8e2ff4
  commit 7e76bb785fa9f75b9fa483e26e6b826cde244851
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

# -- Public constants ----------------------------------------------------
ENTRY_CHANNEL_LOOKBACK = 55
EXIT_CHANNEL_LOOKBACK = 20

IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")

# Private out-of-sample window constants used only for the defensive
# post-loop scan. Their values mirror the Step 04 validator's pins; they
# are not exported because the signal module's public API must not expose
# anything that could be mistaken for a permission to compute against
# those windows.
_OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")
_POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")

_ALLOWED_SYMBOLS = frozenset({"SPY", "TLT", "GLD", "USO"})


# -- Exception tree ------------------------------------------------------
class SignalError(Exception):
    """Base for every signal-module refusal mode."""


class SignalInputError(SignalError):
    """Input not a LoadedSymbol or LoadedSymbol structurally invalid."""


class SignalOosBlockedError(SignalError):
    """Attempt to compute signals for an out-of-sample or
    post-out-of-sample bar; structurally refused."""


class SignalParameterOverrideError(SignalError):
    """Attempt to override the hardcoded lookbacks or window."""


# -- Result dataclasses --------------------------------------------------
@dataclass(frozen=True)
class SignalEvent:
    """Per-bar signal event."""
    date: str
    bar_index: int
    entry_channel_high_55: float
    entry_channel_low_55: float
    exit_channel_high_20: float
    exit_channel_low_20: float
    today_high: float
    today_low: float
    today_close: float
    entry_long_triggered: bool
    entry_short_triggered: bool
    exit_long_triggered: bool
    exit_short_triggered: bool


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
    """Duck-type check for the fields the signal module reads."""
    return all(
        hasattr(obj, attr)
        for attr in (
            "symbol", "dates", "high", "low", "close",
            "csv_path", "csv_sha256",
        )
    )


def _date_in_window(d: str, window: tuple) -> bool:
    return window[0] <= d <= window[1]


# -- Public API ----------------------------------------------------------
def compute_signals(loaded: Any) -> SignalResult:
    """Compute in-sample-only channel breakout triggers for one symbol.

    Returns a SignalResult containing one SignalEvent per signal-eligible
    in-sample bar. Raises SignalError subclass on any structural refusal.
    """
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
    highs = loaded.high
    lows = loaded.low
    closes = loaded.close
    if not (len(dates) == len(highs) == len(lows) == len(closes)):
        raise SignalInputError(
            f"{sym} column length mismatch: dates={len(dates)} "
            f"highs={len(highs)} lows={len(lows)} closes={len(closes)}"
        )

    # Read the hardcoded constants into local names exactly once. Any
    # attempt to monkey-patch the module-level IN_SAMPLE_WINDOW after this
    # point cannot affect the loop because the loop uses these locals.
    is_lo, is_hi = IN_SAMPLE_WINDOW
    entry_lb = ENTRY_CHANNEL_LOOKBACK
    exit_lb = EXIT_CHANNEL_LOOKBACK

    bars_in_window = sum(1 for d in dates if is_lo <= d <= is_hi)

    signals_list = []
    first_idx = -1
    last_idx = -1
    for i in range(len(dates)):
        d = dates[i]
        if not (is_lo <= d <= is_hi):
            continue
        if i < entry_lb:
            continue
        # Look-back slices: indices [i - entry_lb, i) and [i - exit_lb, i),
        # which exclude the current bar i, matching the spec.
        entry_hi = max(highs[i - entry_lb:i])
        entry_lo = min(lows[i - entry_lb:i])
        exit_hi = max(highs[i - exit_lb:i])
        exit_lo = min(lows[i - exit_lb:i])
        today_hi = highs[i]
        today_lo = lows[i]
        today_cl = closes[i]
        ev = SignalEvent(
            date=d,
            bar_index=i,
            entry_channel_high_55=entry_hi,
            entry_channel_low_55=entry_lo,
            exit_channel_high_20=exit_hi,
            exit_channel_low_20=exit_lo,
            today_high=today_hi,
            today_low=today_lo,
            today_close=today_cl,
            entry_long_triggered=(today_hi > entry_hi),
            entry_short_triggered=(today_lo < entry_lo),
            exit_long_triggered=(today_lo < exit_lo),
            exit_short_triggered=(today_hi > exit_hi),
        )
        signals_list.append(ev)
        if first_idx == -1:
            first_idx = i
        last_idx = i

    if first_idx == -1:
        raise SignalInputError(
            f"{sym} no signal-eligible in-sample bar found "
            f"(no bar in {IN_SAMPLE_WINDOW} with at least "
            f"{ENTRY_CHANNEL_LOOKBACK} prior loaded bars)"
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
    oos_lo, oos_hi = _OUT_OF_SAMPLE_WINDOW
    post_lo, post_hi = _POST_OOS_DIAGNOSTIC_WINDOW
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


def compute_signals_all(data: Mapping) -> CrossSymbolSignalResult:
    """Compute in-sample-only channel breakout triggers for the four-symbol
    bundle. Calls compute_signals per symbol then attests cross-symbol
    consistency.
    """
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

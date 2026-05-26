"""Simulator module for s9 cross-asset RSI-2 mean-reversion (ETF-proxy track).

Pure deterministic in-memory long-only RSI-2 mechanic executor. Consumes
LoadedSymbol structures from the Step 03 loader and SignalResult / Cross
SymbolSignalResult structures from the s9 P6 signal module. Applies the
entry / exit / sizing rules per the s9 Tier-N spec sections 9-13. Produces
a per-trade ledger plus a daily equity ledger. In-sample only.

This module:

  - reads loaded.open (for next-bar-open fills) and loaded.close
    (for daily mark-to-market end-of-day equity);
  - applies open-on-next-bar fills (ONO) at entry on RSI(2) < 10 trigger
    and exit on RSI(2) > 50 trigger, with cost-tier-scaled slippage
    embedded in the fill price;
  - sizes each entry at equal-dollar 1% of portfolio mark-to-market
    equity at the trigger bar's close (deterministic, info-available);
  - tracks per-symbol open state (long or flat; at most one open
    record per symbol; no second concurrent on the same symbol),
    cash, mark-to-market equity, high-water mark, max-drawdown;
  - enforces the K4 catastrophic park rule (drawdown > 50%) by forced
    close at the K4 day's close (no slippage charged), then continues
    iterating to record bookkeeping daily equity points;
  - flat-marks any still-open record at the last IS bar's close with
    exit_reason IN_SAMPLE_END_FLAT and exit_fill_price equal to that
    bar's close (boundary safety; never crosses into OOS bars);
  - records a daily equity point per processed in-sample date from
    the first signal-eligible date through the last.

This module does NOT:

  - run any result-aggregation engine; no risk-adjusted ratio, no
    portfolio-statistic, no win-fraction, no pairwise dependence
    measure, no average pairwise measure is computed (those are
    deferred to the future s9 aggregator phase);
  - simulate any out-of-sample bar; no SignalEvent date outside
    IN_SAMPLE_WINDOW reaches the loop, and every TradeRecord field
    date plus every DailyEquityPoint.date is checked against
    IN_SAMPLE_WINDOW;
  - compute RSI of any kind (the upstream signal module emits the
    trigger flags; the simulator only consumes them);
  - use any rolling-channel construct or any volatility-based sizing
    construct (s9 has no channel mechanic and no volatility sizing);
  - apply any hard or time or trailing exit (the only exits are the
    canonical RSI > 50 signal, the K4 catastrophic park, and the
    in-sample-end flat-mark);
  - layer multiple records per symbol (MAX_UNITS_PER_SYMBOL = 1; a
    second RSI < 10 firing while a record is already open on the
    same symbol is recorded as a skip in entry_skip_log);
  - execute any live order, paper order, broker session, automated-run
    queueing, production-signal write, or downstream-research-system
    promotion;
  - import any vendor SDK, network library, or broker SDK;
  - read or write any environment variable beginning with a vendor
    credential prefix;
  - disable SSL verification;
  - perform any file IO;
  - mutate any input.

ETF-proxy adaptations (documented explicitly; not deviations from the
locked Tier-N semantics):

  - ETF_DOLLAR_PER_SHARE = 1.0 (each $1 price change times 1 share
    equals $1 cash; no futures contract multiplier);
  - ETF_TICK_SIZE = 0.01 (penny tick);
  - S1 commission baseline = $0 per share (zero-commission ETF broker
    assumption); slippage baseline = 1 cent at entry, 1 cent at exit;
  - no borrow cost (long-only ETF track);
  - no roll handling (ETFs do not expire).

Spec anchors:
  Tier-N spec:
    docs/s9_cross_asset_mean_reversion_rsi2_tier_n_specification_plan.md
    sha256 6690c0d789285598c400495f90ec0aa2c6db5165d449608762d9689bf807f409
    commit 5bd8e62a1a614042a30e44f4060e54c7cdd20401
  Signal-module spec:
    docs/s9_cross_asset_mean_reversion_rsi2_signal_module_specification_plan.md
    sha256 59e5f401232f19342777445a0d992d1df23dda95a71419379e1daded89e9a0c9
    commit c5393ab31a58059004b8cd337cd428eacbcbaece
  Simulator-module spec:
    docs/s9_cross_asset_mean_reversion_rsi2_simulator_specification_plan.md
    sha256 c64bbe7525ad06d5d870b51b6c5b8c9ba45a17675acc5ecc3e2faa4c545f83bf
    commit 3a9a0de9eba9e448d0440fa45fb40e8107fb8e0f
"""
from __future__ import annotations

import enum
import math
from dataclasses import dataclass
from typing import Any, Mapping, Optional

# -- Public constants ----------------------------------------------------
RSI_LOOKBACK = 2
RSI_OVERSOLD_ENTRY_THRESHOLD = 10.0
RSI_EXIT_THRESHOLD = 50.0
MAX_UNITS_PER_SYMBOL = 1
PER_SIGNAL_ALLOCATION_FRACTION = 0.01
DEFAULT_STARTING_CASH = 100000.0
K4_PORTFOLIO_MAXDD_PCT = 50.0
IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")
ETF_DOLLAR_PER_SHARE = 1.0
ETF_TICK_SIZE = 0.01

# -- Private constants ---------------------------------------------------
_OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")
_POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")
_ALLOWED_SYMBOLS = frozenset({"SPY", "TLT", "GLD", "USO"})
_LONG = "long"

# S1 baseline (per ETF-proxy adaptation documented in the Tier-N spec)
_COMMISSION_PER_SHARE_S1_DOLLARS = 0.00
_SLIPPAGE_ENTRY_PER_SHARE_S1 = ETF_TICK_SIZE * 1.0  # $0.01
_SLIPPAGE_EXIT_PER_SHARE_S1 = ETF_TICK_SIZE * 1.0   # $0.01


# -- Public enums --------------------------------------------------------
class CostTier(enum.Enum):
    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"


class ExitReason(enum.Enum):
    RSI_EXIT_TRIGGER = "RSI_EXIT_TRIGGER"
    K4_FORCED_PARK = "K4_FORCED_PARK"
    IN_SAMPLE_END_FLAT = "IN_SAMPLE_END_FLAT"


_TIER_SCALARS = {
    # (slippage_scalar, commission_scalar)
    CostTier.S0: (0.0, 0.0),
    CostTier.S1: (1.0, 1.0),
    CostTier.S2: (3.0, 1.5),
    CostTier.S3: (5.0, 2.0),
}


# -- Exception tree ------------------------------------------------------
class SimulatorError(Exception):
    """Base for every simulator refusal mode."""


class SimulatorInputError(SimulatorError):
    """Input shape, type, or value invalid."""


class SimulatorOosBlockedError(SimulatorError):
    """Attempt to simulate any bar outside IN_SAMPLE_WINDOW."""


class SimulatorParameterOverrideError(SimulatorError):
    """Attempt to override a hardcoded parameter or pass an unknown kwarg."""


class SimulatorK4FiredError(SimulatorError):
    """Reserved for explicit raise patterns; current implementation uses the
    SimulationResult.k4_fired flag instead. Imported for API completeness."""


# -- Result dataclasses (immutable) --------------------------------------
@dataclass(frozen=True)
class TradeRecord:
    """One long entry-exit cycle on a symbol.

    Long-only by type: only entry_long_triggered / exit_long_triggered
    are exposed on the upstream SignalEvent; opposite-side trigger
    fields are not defined on this dataclass. Per-trade economics are
    expressed as gross / net dollar amounts; no risk-adjusted ratio is
    computed at this layer.
    """
    symbol: str
    trade_id: str
    direction: str
    entry_trigger_date: str
    entry_fill_date: str
    entry_fill_price: float
    entry_slippage_dollars: float
    shares: int
    exit_trigger_date: str
    exit_fill_date: str
    exit_fill_price: float
    exit_slippage_dollars: float
    exit_reason: ExitReason
    commission_dollars: float
    gross_pnl_dollars: float
    net_pnl_dollars: float
    hold_days: int


@dataclass(frozen=True)
class DailyEquityPoint:
    """One end-of-day mark-to-market snapshot per in-sample date.

    Records cash, open-record count, mark-to-market equity, drawdown
    percent from running high-water, and the k4_armed flag (True iff
    drawdown crossed K4 threshold on this bar; equivalent to the
    simulator setting k4_fired at the same bar).
    """
    date: str
    cash_balance: float
    open_positions_count_total: int
    open_positions_per_symbol: Mapping
    mark_to_market_equity: float
    drawdown_pct_from_high_water: float
    k4_armed: bool


@dataclass(frozen=True)
class SimulationResult:
    """Output of a single simulate() call.

    Records per-trade ledger, daily equity ledger, cash-flow trail, and
    permanent attestations that no out-of-sample or post-out-of-sample
    bar was simulated. Aggregation statistics (risk-adjusted ratios,
    pairwise dependence measures, average win-fraction) are NOT
    computed at this layer.
    """
    starting_cash: float
    final_cash_balance: float
    cost_tier: str
    cost_tier_slippage_scalar: float
    cost_tier_commission_scalar: float
    per_signal_allocation_fraction: float
    trade_records: tuple
    trade_records_per_symbol: Mapping
    num_closed_trades_total: int
    entry_skip_log: tuple
    daily_equity_ledger: tuple
    max_drawdown_pct_observed: float
    k4_fired: bool
    k4_fired_date: Optional[str]
    in_sample_window: tuple
    first_signal_date_processed: str
    last_signal_date_processed: str
    # FORBIDDEN_TOKEN_EXCLUSION: spec sec 8 mandates these two attestation field names.
    oos_simulation_intentionally_omitted: bool
    post_oos_simulation_intentionally_omitted: bool


# -- Private mutable per-call state --------------------------------------
class _SymbolState:
    """Mutable per-symbol state during one simulate() call. Per-call only;
    a fresh _SymbolState is constructed inside simulate(). No module-level
    mutable state survives across calls."""

    __slots__ = (
        "symbol", "direction", "entry_trigger_date", "entry_fill_date",
        "entry_fill_price", "entry_slippage_dollars", "shares",
        "cost_basis_dollars", "pending_action",
    )

    def __init__(self, symbol):
        self.symbol = symbol
        self.direction = None  # "long" or None
        self.entry_trigger_date = None
        self.entry_fill_date = None
        self.entry_fill_price = None
        self.entry_slippage_dollars = None
        self.shares = None
        self.cost_basis_dollars = None
        # pending_action queued at close of bar D, processed at open of D+1.
        # One of: None, {"type": "entry_long", "trigger_date": ...,
        #               "trigger_bar_index": ...},
        #               {"type": "exit_long", "trigger_date": ...,
        #               "trigger_bar_index": ...}.
        self.pending_action = None


# -- Private helpers -----------------------------------------------------
def _looks_like_loaded_symbol(obj):
    return all(hasattr(obj, a) for a in (
        "symbol", "dates", "open", "close",
        "csv_path", "csv_sha256",
    ))


def _looks_like_signal_result(obj):
    return all(hasattr(obj, a) for a in (
        "symbol", "csv_sha256_observed", "window", "bars_in_window",
        "signals", "oos_signal_intentionally_omitted",
    ))


def _coerce_signals_to_mapping(signals):
    """Accept either a Mapping[str, SignalResult] or a CrossSymbolSignalResult
    (which carries a .per_symbol Mapping). Returns the underlying Mapping."""
    if isinstance(signals, Mapping):
        return signals
    if hasattr(signals, "per_symbol") and isinstance(signals.per_symbol, Mapping):
        return signals.per_symbol
    return None


def _validate_inputs(loaded, signals, cost_tier, starting_cash):
    if not isinstance(loaded, Mapping):
        raise SimulatorInputError(
            f"loaded must be Mapping; got {type(loaded).__name__}"
        )
    coerced = _coerce_signals_to_mapping(signals)
    if coerced is None:
        raise SimulatorInputError(
            f"signals must be Mapping or CrossSymbolSignalResult; "
            f"got {type(signals).__name__}"
        )
    if set(loaded.keys()) != _ALLOWED_SYMBOLS:
        raise SimulatorInputError(
            f"loaded keys {sorted(loaded.keys())} != "
            f"expected {sorted(_ALLOWED_SYMBOLS)}"
        )
    if set(coerced.keys()) != _ALLOWED_SYMBOLS:
        raise SimulatorInputError(
            f"signals keys {sorted(coerced.keys())} != "
            f"expected {sorted(_ALLOWED_SYMBOLS)}"
        )
    for sym in sorted(_ALLOWED_SYMBOLS):
        if not _looks_like_loaded_symbol(loaded[sym]):
            raise SimulatorInputError(
                f"loaded[{sym}] does not look like a LoadedSymbol"
            )
        if not _looks_like_signal_result(coerced[sym]):
            raise SimulatorInputError(
                f"signals[{sym}] does not look like a SignalResult"
            )
    if not isinstance(cost_tier, CostTier):
        raise SimulatorParameterOverrideError(
            f"cost_tier must be a CostTier enum; got {type(cost_tier).__name__}"
        )
    if cost_tier not in _TIER_SCALARS:
        raise SimulatorParameterOverrideError(
            f"cost_tier {cost_tier!r} not in supported tiers "
            f"{sorted(_TIER_SCALARS.keys())}"
        )
    if not isinstance(starting_cash, (int, float)):
        raise SimulatorInputError(
            f"starting_cash must be number; got {type(starting_cash).__name__}"
        )
    sc = float(starting_cash)
    if not math.isfinite(sc) or sc <= 0:
        raise SimulatorInputError(
            f"starting_cash must be finite positive; got {starting_cash!r}"
        )


def _is_in_sample(date_str):
    return IN_SAMPLE_WINDOW[0] <= date_str <= IN_SAMPLE_WINDOW[1]


def _is_in_oos(date_str):
    return _OUT_OF_SAMPLE_WINDOW[0] <= date_str <= _OUT_OF_SAMPLE_WINDOW[1]


def _is_in_post_oos(date_str):
    return _POST_OOS_DIAGNOSTIC_WINDOW[0] <= date_str <= _POST_OOS_DIAGNOSTIC_WINDOW[1]


def _verify_date_is(date_str, ctx):
    if not _is_in_sample(date_str):
        if _is_in_oos(date_str) or _is_in_post_oos(date_str):
            raise SimulatorOosBlockedError(
                f"out-of-sample date {date_str} reached {ctx}; "
                f"structural enforcement failure"
            )
        raise SimulatorInputError(
            f"unexpected date {date_str} reached {ctx}; not in any known window"
        )


def _mtm_open_record(state, current_close_price):
    """Signed market value of one symbol's open record.

    For long records: +shares * current_close_price (asset value adds to
    equity). Long-only by type at this layer; opposite direction is never
    set so the negative branch is structurally unreachable. The pair
    cash + signed market value yields the correct mark-to-market equity
    at any current close.
    """
    if state.direction is None or state.shares is None:
        return 0.0
    return state.shares * current_close_price


def _portfolio_equity_now(cash, sym_states, current_close_per_symbol):
    """Cash plus signed market value of open records across all symbols."""
    eq = cash
    for sym, state in sym_states.items():
        if state.direction is None:
            continue
        cc = current_close_per_symbol.get(sym)
        if cc is None:
            continue
        eq += _mtm_open_record(state, cc)
    return eq


def _new_trade_id(symbol, entry_trigger_date):
    return f"{symbol}_{entry_trigger_date}"


def _bar_index_in(loaded_symbol, date_str):
    """Return the bar index of date_str in loaded_symbol.dates, or None."""
    dates = loaded_symbol.dates
    # Linear scan is acceptable; dates are tuples of ~2266 strings per symbol
    # and this lookup is rare (only when matching signal-event dates).
    # For determinism we use straight equality scan.
    try:
        return dates.index(date_str)
    except ValueError:
        return None


def _count_open_positions(sym_states):
    return sum(1 for s in sym_states.values() if s.direction is not None)


def _open_positions_per_symbol_view(sym_states):
    return {sym: (1 if s.direction is not None else 0)
            for sym, s in sym_states.items()}


def _build_record_long_close(state, current_date, exit_trigger_date,
                             exit_fill_date, exit_fill_price,
                             exit_slippage_dollars, exit_reason,
                             commission_scalar):
    """Build a TradeRecord closing a long record. Pure construction; the
    cash-flow update is the caller's responsibility."""
    commission_dollars = (
        _COMMISSION_PER_SHARE_S1_DOLLARS * commission_scalar * state.shares
    )
    gross = state.shares * (exit_fill_price - state.entry_fill_price)
    net = (gross
           - state.entry_slippage_dollars
           - exit_slippage_dollars
           - commission_dollars)
    hold_days = _count_calendar_days_between(state.entry_fill_date,
                                             exit_fill_date)
    return TradeRecord(
        symbol=state.symbol,
        trade_id=_new_trade_id(state.symbol, state.entry_trigger_date),
        direction=state.direction,
        entry_trigger_date=state.entry_trigger_date,
        entry_fill_date=state.entry_fill_date,
        entry_fill_price=state.entry_fill_price,
        entry_slippage_dollars=state.entry_slippage_dollars,
        shares=state.shares,
        exit_trigger_date=exit_trigger_date,
        exit_fill_date=exit_fill_date,
        exit_fill_price=exit_fill_price,
        exit_slippage_dollars=exit_slippage_dollars,
        exit_reason=exit_reason,
        commission_dollars=commission_dollars,
        gross_pnl_dollars=gross,
        net_pnl_dollars=net,
        hold_days=hold_days,
    )


def _count_calendar_days_between(start_date, end_date):
    """Calendar days between two YYYY-MM-DD strings, inclusive of start and
    exclusive of end. Used for the hold_days field on TradeRecord; not used
    for any execution decision."""
    import datetime
    s = datetime.date.fromisoformat(start_date)
    e = datetime.date.fromisoformat(end_date)
    delta = (e - s).days
    return max(delta, 0)


def _reset_symbol_state(state):
    state.direction = None
    state.entry_trigger_date = None
    state.entry_fill_date = None
    state.entry_fill_price = None
    state.entry_slippage_dollars = None
    state.shares = None
    state.cost_basis_dollars = None
    state.pending_action = None


# -- Public API ----------------------------------------------------------
def simulate(loaded, signals, cost_tier=CostTier.S1,
             starting_cash=DEFAULT_STARTING_CASH, **kwargs):
    """Simulate the long-only RSI-2 mean-reversion mechanic in-sample only.

    Inputs:
      loaded:        Mapping[str, LoadedSymbol] keyed by {SPY,TLT,GLD,USO}.
      signals:       Mapping[str, SignalResult] or CrossSymbolSignalResult.
      cost_tier:     CostTier enum (S0/S1/S2/S3).
      starting_cash: positive finite float (default 100000.0).

    Returns a SimulationResult. Raises SimulatorError subclass on refusal.

    No out-of-sample bar reaches the loop. No post-out-of-sample bar
    reaches the loop. The function is pure deterministic.
    """
    if kwargs:
        raise SimulatorParameterOverrideError(
            f"unexpected kwargs {sorted(kwargs.keys())}; only "
            f"(loaded, signals, cost_tier, starting_cash) accepted"
        )
    _validate_inputs(loaded, signals, cost_tier, starting_cash)
    signals = _coerce_signals_to_mapping(signals)
    slippage_scalar, commission_scalar = _TIER_SCALARS[cost_tier]

    # Build a cross-symbol date-keyed event index.
    # Each entry: date -> { sym: SignalEvent }.
    date_to_events = {}
    for sym, sr in signals.items():
        for ev in sr.signals:
            _verify_date_is(ev.date, f"signal event for {sym}")
            date_to_events.setdefault(ev.date, {})[sym] = ev
    sorted_dates = sorted(date_to_events.keys())
    if not sorted_dates:
        raise SimulatorInputError("no signal events to simulate")
    first_signal_date = sorted_dates[0]
    last_signal_date = sorted_dates[-1]
    _verify_date_is(first_signal_date, "first signal date")
    _verify_date_is(last_signal_date, "last signal date")

    # Per-symbol column references for price lookup. Open is used for ONO
    # fill price; close is used for daily mark-to-market.
    sym_opens = {sym: loaded[sym].open for sym in _ALLOWED_SYMBOLS}
    sym_closes = {sym: loaded[sym].close for sym in _ALLOWED_SYMBOLS}

    # Per-symbol state and portfolio state.
    sym_states = {sym: _SymbolState(sym) for sym in _ALLOWED_SYMBOLS}
    cash = float(starting_cash)
    hwm = float(starting_cash)
    max_dd_pct = 0.0
    k4_fired = False
    k4_fired_date = None

    # Outputs.
    trade_records_closed = []
    daily_equity_ledger = []
    entry_skip_log = []

    # Pre-compute today's close per symbol per date for fast equity calc.
    # We index by bar_index from each SignalEvent (the signal module is
    # cross-symbol-aligned, but defensively we look it up per symbol).
    def _today_close_per_symbol(events_today):
        out = {}
        for sym, ev in events_today.items():
            out[sym] = sym_closes[sym][ev.bar_index]
        return out

    # Iterate dates in chronological order. The loop processes pending
    # ONO fills at today's open, then evaluates today's signal events to
    # queue tomorrow's actions, then records the daily equity point at
    # today's close (and evaluates K4).
    for di, current_date in enumerate(sorted_dates):
        # Layer L3 of the IS-only enforcement: every iterated date must
        # be in IN_SAMPLE_WINDOW. The signal module already enforces this
        # transitively (it only emits IS events), but we defend in depth.
        _verify_date_is(current_date, "simulation loop")
        events_today = date_to_events[current_date]
        is_last_signal_date = (current_date == last_signal_date)

        # ---- Step A: process pending ONO fills at today's open ----
        for sym in sorted(_ALLOWED_SYMBOLS):
            state = sym_states[sym]
            if state.pending_action is None:
                continue
            action = state.pending_action
            ev_today = events_today.get(sym)
            if ev_today is None:
                # Symbol had no event today (should not occur for
                # cross-aligned data); cancel pending and move on.
                state.pending_action = None
                continue
            bar_idx_today = ev_today.bar_index
            open_price_today = sym_opens[sym][bar_idx_today]
            atype = action["type"]
            trigger_date = action["trigger_date"]
            if atype == "entry_long":
                if state.direction is not None:
                    # Should never happen: we only queue entry when flat.
                    state.pending_action = None
                    continue
                if k4_fired:
                    entry_skip_log.append({
                        "symbol": sym, "trigger_date": trigger_date,
                        "reason": "k4_already_fired",
                    })
                    state.pending_action = None
                    continue
                if open_price_today is None or not math.isfinite(
                        open_price_today) or open_price_today <= 0:
                    entry_skip_log.append({
                        "symbol": sym, "trigger_date": trigger_date,
                        "reason": "open_price_invalid",
                    })
                    state.pending_action = None
                    continue
                # Equity at the trigger bar's close: cash plus signed
                # market value of any open records using prior bar's close.
                trigger_bar_idx = action["trigger_bar_index"]
                prior_close_per_sym = {}
                for s2 in _ALLOWED_SYMBOLS:
                    other_state = sym_states[s2]
                    if other_state.direction is None:
                        continue
                    # Use the close at the trigger bar of THIS entry's
                    # symbol's signal day; for the open positions on other
                    # symbols use the same trigger bar's close on each.
                    # Cross-aligned dates guarantee both symbols share the
                    # same bar_index for the same calendar date.
                    prior_close_per_sym[s2] = sym_closes[s2][trigger_bar_idx]
                equity_at_trigger = (cash
                                     + sum(prior_close_per_sym[s2]
                                           * sym_states[s2].shares
                                           for s2 in prior_close_per_sym
                                           if sym_states[s2].shares))
                if equity_at_trigger <= 0:
                    entry_skip_log.append({
                        "symbol": sym, "trigger_date": trigger_date,
                        "reason": "equity_non_positive",
                        "equity_at_trigger": equity_at_trigger,
                    })
                    state.pending_action = None
                    continue
                target_dollars = (PER_SIGNAL_ALLOCATION_FRACTION
                                  * equity_at_trigger)
                shares_raw = target_dollars / open_price_today
                shares = int(math.floor(shares_raw))
                if shares < 1:
                    entry_skip_log.append({
                        "symbol": sym, "trigger_date": trigger_date,
                        "reason": "shares_floor_zero",
                        "equity_at_trigger": equity_at_trigger,
                        "open_price": open_price_today,
                    })
                    state.pending_action = None
                    continue
                per_share_entry_slip = (_SLIPPAGE_ENTRY_PER_SHARE_S1
                                        * slippage_scalar)
                # Long entry: buy at open + slippage.
                fill_price = open_price_today + per_share_entry_slip
                entry_slip_dollars = shares * per_share_entry_slip
                cost_basis = shares * fill_price
                cash -= cost_basis
                state.direction = _LONG
                state.entry_trigger_date = trigger_date
                state.entry_fill_date = current_date
                state.entry_fill_price = fill_price
                state.entry_slippage_dollars = entry_slip_dollars
                state.shares = shares
                state.cost_basis_dollars = cost_basis
                state.pending_action = None
            elif atype == "exit_long":
                if state.direction is None:
                    # Should not happen; defensive.
                    state.pending_action = None
                    continue
                if open_price_today is None or not math.isfinite(
                        open_price_today) or open_price_today <= 0:
                    # Skip the exit; the record stays open. Defensive
                    # behavior; for real ETF-proxy data this branch is
                    # unreachable because the validator already ensures
                    # finite positive prices.
                    state.pending_action = None
                    continue
                per_share_exit_slip = (_SLIPPAGE_EXIT_PER_SHARE_S1
                                       * slippage_scalar)
                # Long exit: sell at open - slippage.
                fill_price = open_price_today - per_share_exit_slip
                exit_slip_dollars = state.shares * per_share_exit_slip
                cash += state.shares * fill_price
                rec = _build_record_long_close(
                    state=state,
                    current_date=current_date,
                    exit_trigger_date=trigger_date,
                    exit_fill_date=current_date,
                    exit_fill_price=fill_price,
                    exit_slippage_dollars=exit_slip_dollars,
                    exit_reason=ExitReason.RSI_EXIT_TRIGGER,
                    commission_scalar=commission_scalar,
                )
                cash -= rec.commission_dollars
                trade_records_closed.append(rec)
                _reset_symbol_state(state)

        # ---- Step B: evaluate end-of-day mark-to-market + K4 ----
        today_close_per_sym = _today_close_per_symbol(events_today)
        mtm_equity_today = _portfolio_equity_now(
            cash, sym_states, today_close_per_sym,
        )
        if mtm_equity_today > hwm:
            hwm = mtm_equity_today
        if hwm > 0:
            dd_pct_today = (hwm - mtm_equity_today) / hwm * 100.0
        else:
            dd_pct_today = 0.0
        if dd_pct_today > max_dd_pct:
            max_dd_pct = dd_pct_today
        k4_armed_today = dd_pct_today > K4_PORTFOLIO_MAXDD_PCT

        if k4_armed_today and not k4_fired:
            # K4 catastrophic park: forced close all open records at
            # today's close. No slippage charged on the forced close
            # (consistent with the s7 D1 simulator's K4 behavior; the
            # K4 close is a bookkeeping termination, not a mechanical
            # market fill).
            k4_fired = True
            k4_fired_date = current_date
            for sym in sorted(_ALLOWED_SYMBOLS):
                st = sym_states[sym]
                if st.direction is None:
                    continue
                ev_t = events_today.get(sym)
                if ev_t is None:
                    continue
                exit_close = sym_closes[sym][ev_t.bar_index]
                cash += st.shares * exit_close
                rec = _build_record_long_close(
                    state=st,
                    current_date=current_date,
                    exit_trigger_date=current_date,
                    exit_fill_date=current_date,
                    exit_fill_price=exit_close,
                    exit_slippage_dollars=0.0,
                    exit_reason=ExitReason.K4_FORCED_PARK,
                    commission_scalar=commission_scalar,
                )
                cash -= rec.commission_dollars
                trade_records_closed.append(rec)
                _reset_symbol_state(st)
            # Re-mark equity after the forced close.
            mtm_equity_today = _portfolio_equity_now(
                cash, sym_states, today_close_per_sym,
            )

        # ---- Step C: end-of-IS flat-mark at the last signal date ----
        if is_last_signal_date:
            for sym in sorted(_ALLOWED_SYMBOLS):
                st = sym_states[sym]
                if st.direction is None:
                    continue
                ev_t = events_today.get(sym)
                if ev_t is None:
                    continue
                exit_close = sym_closes[sym][ev_t.bar_index]
                cash += st.shares * exit_close
                rec = _build_record_long_close(
                    state=st,
                    current_date=current_date,
                    exit_trigger_date=current_date,
                    exit_fill_date=current_date,
                    exit_fill_price=exit_close,
                    exit_slippage_dollars=0.0,
                    exit_reason=ExitReason.IN_SAMPLE_END_FLAT,
                    commission_scalar=commission_scalar,
                )
                cash -= rec.commission_dollars
                trade_records_closed.append(rec)
                _reset_symbol_state(st)
            # Re-mark after the flat-close.
            mtm_equity_today = _portfolio_equity_now(
                cash, sym_states, today_close_per_sym,
            )

        # ---- Step D: evaluate today's signals to queue tomorrow's
        #              actions. Symbol iteration is alphabetical for
        #              deterministic tie-resolution: GLD-SPY-TLT-USO. ----
        if not k4_fired and not is_last_signal_date:
            for sym in sorted(_ALLOWED_SYMBOLS):
                ev = events_today.get(sym)
                if ev is None:
                    continue
                # Defensive OOS guard.
                _verify_date_is(ev.date, f"event evaluation {sym}")
                state = sym_states[sym]
                if state.direction is None:
                    # Flat: evaluate entry_long_triggered.
                    if ev.entry_long_triggered:
                        state.pending_action = {
                            "type": "entry_long",
                            "trigger_date": current_date,
                            "trigger_bar_index": ev.bar_index,
                        }
                else:
                    # Long is open on this symbol.
                    if ev.exit_long_triggered:
                        state.pending_action = {
                            "type": "exit_long",
                            "trigger_date": current_date,
                            "trigger_bar_index": ev.bar_index,
                        }
                    elif ev.entry_long_triggered:
                        # A second RSI < 10 firing while a long is already
                        # open. Per Tier-N section 12 with
                        # MAX_UNITS_PER_SYMBOL = 1, no second record is
                        # layered on this symbol. Record the skip; the
                        # position stays open.
                        entry_skip_log.append({
                            "symbol": sym, "trigger_date": current_date,
                            "reason": "position_already_open",
                        })

        # ---- Step E: append DailyEquityPoint ----
        # MAX_UNITS_PER_SYMBOL is 1; open count per symbol is 0 or 1.
        # The total is 0..4 across the four symbols.
        daily_equity_ledger.append(DailyEquityPoint(
            date=current_date,
            cash_balance=cash,
            open_positions_count_total=_count_open_positions(sym_states),
            open_positions_per_symbol=_open_positions_per_symbol_view(
                sym_states,
            ),
            mark_to_market_equity=mtm_equity_today,
            drawdown_pct_from_high_water=dd_pct_today,
            k4_armed=k4_armed_today,
        ))

    # ---- Post-loop assertions (Layer L4) ----
    # Every closed record's four date fields must be in IS.
    for rec in trade_records_closed:
        _verify_date_is(rec.entry_trigger_date, "TradeRecord.entry_trigger_date")
        _verify_date_is(rec.entry_fill_date, "TradeRecord.entry_fill_date")
        _verify_date_is(rec.exit_trigger_date, "TradeRecord.exit_trigger_date")
        _verify_date_is(rec.exit_fill_date, "TradeRecord.exit_fill_date")
    for pt in daily_equity_ledger:
        _verify_date_is(pt.date, "DailyEquityPoint.date")
    if daily_equity_ledger:
        last_pt_date = daily_equity_ledger[-1].date
        if last_pt_date > IN_SAMPLE_WINDOW[1]:
            raise SimulatorOosBlockedError(
                f"last DailyEquityPoint.date {last_pt_date} > "
                f"IN_SAMPLE_WINDOW end {IN_SAMPLE_WINDOW[1]}"
            )

    # ---- Layer L5: defensive scan against OOS / post-OOS windows ----
    for rec in trade_records_closed:
        for d in (rec.entry_trigger_date, rec.entry_fill_date,
                  rec.exit_trigger_date, rec.exit_fill_date):
            if _is_in_oos(d) or _is_in_post_oos(d):
                raise SimulatorOosBlockedError(
                    f"TradeRecord date {d} in OOS / post-OOS window; "
                    f"L5 defensive scan failure"
                )
    for pt in daily_equity_ledger:
        if _is_in_oos(pt.date) or _is_in_post_oos(pt.date):
            raise SimulatorOosBlockedError(
                f"DailyEquityPoint.date {pt.date} in OOS / post-OOS; "
                f"L5 defensive scan failure"
            )

    # Per-symbol counts.
    trade_records_per_symbol = {
        sym: sum(1 for r in trade_records_closed if r.symbol == sym)
        for sym in sorted(_ALLOWED_SYMBOLS)
    }

    return SimulationResult(
        starting_cash=float(starting_cash),
        final_cash_balance=cash,
        cost_tier=cost_tier.name,
        cost_tier_slippage_scalar=slippage_scalar,
        cost_tier_commission_scalar=commission_scalar,
        per_signal_allocation_fraction=PER_SIGNAL_ALLOCATION_FRACTION,
        trade_records=tuple(trade_records_closed),
        trade_records_per_symbol=dict(trade_records_per_symbol),
        num_closed_trades_total=len(trade_records_closed),
        entry_skip_log=tuple(entry_skip_log),
        daily_equity_ledger=tuple(daily_equity_ledger),
        max_drawdown_pct_observed=max_dd_pct,
        k4_fired=k4_fired,
        k4_fired_date=k4_fired_date,
        in_sample_window=IN_SAMPLE_WINDOW,
        first_signal_date_processed=first_signal_date,
        last_signal_date_processed=last_signal_date,
        # FORBIDDEN_TOKEN_EXCLUSION: spec sec 8 mandates these two negative attestations.
        oos_simulation_intentionally_omitted=True,
        post_oos_simulation_intentionally_omitted=True,
    )

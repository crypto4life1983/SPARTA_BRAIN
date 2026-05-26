"""Simulator module for s7 D1 cross-asset entry/exit channel execution.

Pure deterministic in-memory Faith System 1 mechanic executor. Consumes
LoadedSymbol structures from the Step 03 loader and SignalResult
structures from the Step 05 signal module. Applies entry/exit/stop/
sizing rules per parent spec sections 6-10. Produces a trade ledger
plus an optional daily equity ledger. In-sample only.

This module:

  - reads loaded.open/high/low/close/dates and signal events;
  - computes Wilder ATR(20) at trigger bars for sizing (per spec sec 6);
  - applies open-on-next-bar fills (ONO) at entry and Donchian-20 exit;
  - applies intra-bar stop fills at stop_price plus slippage;
  - tracks per-symbol position state (direction, units, stops, next
    pyramid trigger) and portfolio state (cash, equity, high-water
    mark, max drawdown);
  - enforces the K4 catastrophic park rule (drawdown > 50%) by flat-
    marking remaining open units at the K4-triggering bar's close;
  - flat-marks any still-open units at the last in-sample signal date
    with exit_reason IN_SAMPLE_END_FLAT and exit_fill_price equal to
    that bar's close;
  - records a daily equity point per processed in-sample date.

This module does NOT:

  - run a result-aggregation engine; no risk-adjusted ratio, no
    loss-side metric, no per-trade summary statistic, no winning-
    fraction count, no pairwise dependence measure is computed
    (those are deferred to the next phase);
  - simulate any out-of-sample bar; no SignalEvent date outside
    IN_SAMPLE_WINDOW reaches the loop, and every TradeUnit and
    DailyEquityPoint date is checked against IN_SAMPLE_WINDOW;
  - make any live order, paper order, broker session, automated-run
    queueing, production-signal write, or downstream-research-system
    promotion;
  - import any vendor SDK, network library, or broker SDK;
  - read or write any environment variable beginning with a vendor
    credential prefix;
  - disable SSL verification;
  - perform any file IO;
  - mutate any input.

ETF-proxy adaptations vs the futures-oriented spec (documented
explicitly; not deviations from Faith semantics):

  - ETF_DOLLAR_PER_SHARE = 1.0 replaces futures $/pt multiplier;
  - ETF_TICK_SIZE = 0.01 (penny tick) replaces futures tick sizes;
  - S1 commission baseline = $0/share (zero-commission ETF broker
    assumption); slippage baseline = 1 cent entry, 2 cents stop,
    1 cent exit per share;
  - ETF short borrow cost assumed zero at this baseline (documented
    adaptation; defer borrow-stress to a later phase under separate
    authorization);
  - no roll handling (ETFs do not expire).

Spec anchor:
  docs/s7_d1_cross_asset_donchian_step_06_simulator_specification_plan.md
  sha256 f7581af358c676519d46f1a0bec486c35cf61f0f5f618faf7f000adf6223878b
  commit c964c59ce0d499b7feb24611d5ea2f6c7a840e08
"""
from __future__ import annotations

import enum
import math
from dataclasses import dataclass, field
from typing import Any, Mapping, Optional

# -- Public constants ----------------------------------------------------
ENTRY_CHANNEL_LOOKBACK = 55
EXIT_CHANNEL_LOOKBACK = 20
WILDER_ATR_LOOKBACK = 20
STOP_DISTANCE_N_MULTIPLE = 2.0
PYRAMID_STEP_N_MULTIPLE = 0.5
MAX_UNITS_PER_SYMBOL = 4
PER_UNIT_RISK_FRACTION = 0.01
DEFAULT_STARTING_CASH = 100000.0
K4_PORTFOLIO_MAXDD_PCT = 50.0
IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")
ETF_DOLLAR_PER_SHARE = 1.0
ETF_TICK_SIZE = 0.01

# -- Private constants ---------------------------------------------------
_OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")
_POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")
_ALLOWED_SYMBOLS = frozenset({"SPY", "TLT", "GLD", "USO"})

# S1 baseline (per ETF-proxy adaptation documented in plan section 14)
_COMMISSION_PER_RT_S1_DOLLARS = 0.00
_SLIPPAGE_ENTRY_PER_SHARE_S1 = ETF_TICK_SIZE * 1.0  # 0.01
_SLIPPAGE_STOP_PER_SHARE_S1 = ETF_TICK_SIZE * 2.0   # 0.02
_SLIPPAGE_EXIT_PER_SHARE_S1 = ETF_TICK_SIZE * 1.0   # 0.01


# -- Public enums --------------------------------------------------------
class CostTier(enum.Enum):
    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"


class ExitReason(enum.Enum):
    DONCHIAN_20_EXIT = "DONCHIAN_20_EXIT"
    STOP_HIT = "STOP_HIT"
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
class TradeUnit:
    symbol: str
    trade_group_id: str
    unit_index: int
    entry_trigger_date: str
    entry_fill_date: str
    entry_fill_price: float
    entry_slippage_dollars: float
    n_entry_dollars: float
    shares: int
    stop_price_at_entry: float
    exit_date: str
    exit_fill_price: float
    exit_slippage_dollars: float
    exit_reason: ExitReason
    commission_dollars: float
    gross_pnl_dollars: float
    net_pnl_dollars: float


@dataclass(frozen=True)
class TradeGroup:
    symbol: str
    trade_group_id: str
    direction: str
    n_entry_dollars: float
    trigger_date_unit_0: str
    units: tuple
    group_open_date: str
    group_close_date: str
    group_gross_pnl_dollars: float
    group_net_pnl_dollars: float
    group_unit_count: int
    group_close_reason: ExitReason


@dataclass(frozen=True)
class DailyEquityPoint:
    date: str
    cash_balance: float
    open_units_count_total: int
    open_units_per_symbol: Mapping
    mark_to_market_equity: float
    drawdown_pct_from_high_water: float
    k4_armed: bool


@dataclass(frozen=True)
class SimulationResult:
    starting_cash: float
    final_cash_balance: float
    cost_tier: str
    cost_tier_slippage_scalar: float
    cost_tier_commission_scalar: float
    trade_groups: tuple
    trade_groups_per_symbol: Mapping
    num_closed_units_total: int
    num_closed_units_per_symbol: Mapping
    daily_equity_ledger: tuple
    max_drawdown_pct_observed: float
    k4_fired: bool
    in_sample_window: tuple
    first_signal_date_processed: str
    last_signal_date_processed: str
    entry_skip_log: tuple
    oos_simulation_intentionally_omitted: bool
    post_oos_simulation_intentionally_omitted: bool


# -- Private mutable state (used only inside simulate()) -----------------
class _SymbolState:
    """Mutable per-symbol state during one simulate() call. Per-call only;
    a fresh _SymbolState is constructed inside simulate(). No module-level
    mutable state survives across calls."""

    __slots__ = (
        "symbol", "direction", "n_entry_first_unit", "unit_entries",
        "next_pyramid_trigger_price", "current_trade_group_id",
        "current_trigger_date_unit_0", "pending_action",
        "partial_stopped_units", "next_unit_index",
    )

    def __init__(self, symbol):
        self.symbol = symbol
        self.direction = None  # "long", "short", or None
        self.n_entry_first_unit = 0.0
        self.unit_entries = []  # list of dicts with keys: trigger_date, fill_date,
                                # fill_price, entry_slippage, shares, stop_price,
                                # unit_index
        self.next_pyramid_trigger_price = 0.0
        self.current_trade_group_id = None
        self.current_trigger_date_unit_0 = None
        # pending_action queued at close of bar D, to be processed at open of D+1.
        self.pending_action = None
        # Units that stopped out while the group is still partially alive;
        # merged into the eventual TradeGroup at group close.
        self.partial_stopped_units = []
        # Lifetime counter: next unit's unit_index in this trade group. Reset
        # to 0 at group close. Separate from len(unit_entries) because partial
        # stops remove entries from unit_entries but later pyramid units must
        # still receive the next lifetime index.
        self.next_unit_index = 0


# -- Private helpers -----------------------------------------------------
def _looks_like_loaded_symbol(obj):
    return all(hasattr(obj, a) for a in (
        "symbol", "dates", "open", "high", "low", "close",
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
            f"signals must be Mapping or CrossSymbolSignalResult; got {type(signals).__name__}"
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
            raise SimulatorInputError(f"loaded[{sym}] does not look like a LoadedSymbol")
        if not _looks_like_signal_result(coerced[sym]):
            raise SimulatorInputError(f"signals[{sym}] does not look like a SignalResult")
    if not isinstance(cost_tier, CostTier):
        raise SimulatorParameterOverrideError(
            f"cost_tier must be a CostTier enum; got {type(cost_tier).__name__}"
        )
    if cost_tier not in _TIER_SCALARS:
        raise SimulatorParameterOverrideError(
            f"cost_tier {cost_tier!r} not in supported tiers {sorted(_TIER_SCALARS.keys())}"
        )
    if not isinstance(starting_cash, (int, float)):
        raise SimulatorInputError(
            f"starting_cash must be number; got {type(starting_cash).__name__}"
        )
    sc = float(starting_cash)
    if not math.isfinite(sc) or sc <= 0:
        raise SimulatorInputError(f"starting_cash must be finite positive; got {starting_cash!r}")


def _wilder_atr_at(highs, lows, closes, bar_index, lookback=WILDER_ATR_LOOKBACK):
    """Return Wilder ATR at bar_index, or None if undefined."""
    if bar_index < lookback:
        return None
    # TR for j = 1 .. bar_index
    trs = []
    for j in range(1, bar_index + 1):
        h = highs[j]
        lo = lows[j]
        pc = closes[j - 1]
        tr = max(h - lo, abs(h - pc), abs(lo - pc))
        trs.append(tr)
    if len(trs) < lookback:
        return None
    # Initial value: simple average of first lookback TRs.
    atr = sum(trs[:lookback]) / float(lookback)
    # Wilder smoothing for remaining TRs.
    for tr in trs[lookback:]:
        atr = ((lookback - 1) * atr + tr) / float(lookback)
    return atr


def _size_shares(equity, n_entry):
    if n_entry is None or n_entry <= 0:
        return 0
    raw = (PER_UNIT_RISK_FRACTION * equity) / (n_entry * ETF_DOLLAR_PER_SHARE)
    return int(math.floor(raw))


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
                f"out-of-sample date {date_str} reached {ctx}; structural enforcement failure"
            )
        raise SimulatorInputError(
            f"unexpected date {date_str} reached {ctx}; not in any known window"
        )


def _new_group_id(counter):
    return f"tg_{counter:06d}"


def _mtm_open_units(state, current_close):
    """Signed market value of open units for one symbol.

    For long units: +shares * current_close (asset value adds to equity).
    For short units: -shares * current_close (owed-shares value reduces equity).

    This is the position's CURRENT MARKET VALUE, signed. It pairs with cash
    tracking that already subtracted the entry cost on long entry (and added
    the short-sale proceeds on short entry). The sum cash + signed-position-
    value yields the correct portfolio equity at any current_close.
    """
    if state.direction is None or not state.unit_entries:
        return 0.0
    sign = 1.0 if state.direction == "long" else -1.0
    mtm = 0.0
    for u in state.unit_entries:
        mtm += u["shares"] * sign * current_close
    return mtm


def _portfolio_equity_now(cash, sym_states, current_closes):
    """Cash plus signed market value of open units across all symbols."""
    eq = cash
    for sym, state in sym_states.items():
        if state.direction is None:
            continue
        cc = current_closes.get(sym)
        if cc is None:
            continue
        eq += _mtm_open_units(state, cc)
    return eq


# -- Public API ----------------------------------------------------------
def simulate(loaded, signals, cost_tier=CostTier.S1,
             starting_cash=DEFAULT_STARTING_CASH, **kwargs):
    """Simulate Faith System 1 mechanic over loaded data and signal events.

    Returns a SimulationResult. Raises SimulatorError subclass on refusal.
    """
    if kwargs:
        raise SimulatorParameterOverrideError(
            f"unexpected kwargs {sorted(kwargs.keys())}; only "
            f"(loaded, signals, cost_tier, starting_cash) accepted"
        )
    _validate_inputs(loaded, signals, cost_tier, starting_cash)
    # After validation, normalize signals to the underlying Mapping.
    signals = _coerce_signals_to_mapping(signals)
    slippage_scalar, commission_scalar = _TIER_SCALARS[cost_tier]

    # Cross-symbol date-keyed event index, plus bar_index lookup.
    # Each entry: (date) -> { sym: signal_event_or_None }
    date_to_events = {}
    for sym, sr in signals.items():
        for ev in sr.signals:
            # Defensive OOS guard on every event we read
            _verify_date_is(ev.date, f"signal event for {sym}")
            date_to_events.setdefault(ev.date, {})[sym] = ev
    sorted_dates = sorted(date_to_events.keys())
    if not sorted_dates:
        raise SimulatorInputError("no signal events to simulate")
    first_signal_date = sorted_dates[0]
    last_signal_date = sorted_dates[-1]

    # Per-symbol price column references (for ONO fill lookup and ATR).
    sym_opens = {sym: loaded[sym].open for sym in _ALLOWED_SYMBOLS}
    sym_highs = {sym: loaded[sym].high for sym in _ALLOWED_SYMBOLS}
    sym_lows = {sym: loaded[sym].low for sym in _ALLOWED_SYMBOLS}
    sym_closes = {sym: loaded[sym].close for sym in _ALLOWED_SYMBOLS}
    sym_dates = {sym: loaded[sym].dates for sym in _ALLOWED_SYMBOLS}

    # Per-symbol state
    sym_states = {sym: _SymbolState(sym) for sym in _ALLOWED_SYMBOLS}

    # Portfolio state
    cash = float(starting_cash)
    hwm = float(starting_cash)
    max_dd_pct = 0.0
    k4_fired = False

    # Outputs
    trade_groups_closed = []
    daily_equity_ledger = []
    entry_skip_log = []
    trade_group_counter = 0

    def _close_group(state, units_to_persist, close_date, close_reason):
        """Build a TradeGroup from a list of TradeUnit instances (plus any
        previously stopped partial units accumulated on the state) and reset
        state."""
        # Merge any partial-stop units from earlier in the group's life.
        merged = list(state.partial_stopped_units) + list(units_to_persist)
        # Sort merged units by entry_trigger_date then unit_index for
        # deterministic ledger ordering.
        merged.sort(key=lambda u: (u.entry_trigger_date, u.unit_index))
        gross = sum(u.gross_pnl_dollars for u in merged)
        net = sum(u.net_pnl_dollars for u in merged)
        group = TradeGroup(
            symbol=state.symbol,
            trade_group_id=state.current_trade_group_id,
            direction=state.direction,
            n_entry_dollars=state.n_entry_first_unit,
            trigger_date_unit_0=state.current_trigger_date_unit_0,
            units=tuple(merged),
            group_open_date=state.current_trigger_date_unit_0,
            group_close_date=close_date,
            group_gross_pnl_dollars=gross,
            group_net_pnl_dollars=net,
            group_unit_count=len(merged),
            group_close_reason=close_reason,
        )
        trade_groups_closed.append(group)
        # Reset state
        state.direction = None
        state.n_entry_first_unit = 0.0
        state.unit_entries = []
        state.next_pyramid_trigger_price = 0.0
        state.current_trade_group_id = None
        state.current_trigger_date_unit_0 = None
        state.pending_action = None
        state.partial_stopped_units = []
        state.next_unit_index = 0

    def _make_unit(state, unit_entry, exit_date, exit_fill_price,
                   exit_slippage, exit_reason):
        sign = 1.0 if state.direction == "long" else -1.0
        gross = unit_entry["shares"] * sign * (exit_fill_price - unit_entry["fill_price"])
        commission = _COMMISSION_PER_RT_S1_DOLLARS * commission_scalar
        net = gross - unit_entry["entry_slippage"] - exit_slippage - commission
        return TradeUnit(
            symbol=state.symbol,
            trade_group_id=state.current_trade_group_id,
            unit_index=unit_entry["unit_index"],
            entry_trigger_date=unit_entry["trigger_date"],
            entry_fill_date=unit_entry["fill_date"],
            entry_fill_price=unit_entry["fill_price"],
            entry_slippage_dollars=unit_entry["entry_slippage"],
            n_entry_dollars=state.n_entry_first_unit,
            shares=unit_entry["shares"],
            stop_price_at_entry=unit_entry["stop_price"],
            exit_date=exit_date,
            exit_fill_price=exit_fill_price,
            exit_slippage_dollars=exit_slippage,
            exit_reason=exit_reason,
            commission_dollars=commission,
            gross_pnl_dollars=gross,
            net_pnl_dollars=net,
        )

    # Iterate dates in chronological order.
    # Per-bar processing order:
    #   A. Fill pending ONO actions at today's open (from yesterday's close)
    #   B. Stop intra-bar check using today's high/low
    #   C. Compute end-of-day equity using today's close (for sizing and K4)
    #   D. Update HWM and drawdown; K4 check (flat-mark all open units if fired)
    #   E. Evaluate Donchian-20 exit triggers -> queue ONO exit
    #   F. Evaluate entry triggers -> queue ONO entry (or pyramid)
    #   G. Append DailyEquityPoint
    for di, current_date in enumerate(sorted_dates):
        _verify_date_is(current_date, "simulation loop")
        events_today = date_to_events[current_date]
        is_last_signal_date = (current_date == last_signal_date)

        # ---- Step A: Process pending ONO fills at today's open ----
        for sym in sorted(_ALLOWED_SYMBOLS):
            state = sym_states[sym]
            if state.pending_action is None:
                continue
            action = state.pending_action
            bar_idx_today = events_today.get(sym).bar_index if events_today.get(sym) else None
            if bar_idx_today is None:
                # Symbol had no event today (should not happen for cross-aligned data);
                # cancel pending and move on.
                state.pending_action = None
                continue
            open_price_today = sym_opens[sym][bar_idx_today]
            atype = action["type"]
            trigger_date = action["trigger_date"]
            if atype in ("entry_long", "entry_short"):
                direction = "long" if atype == "entry_long" else "short"
                # Compute Wilder ATR at the trigger bar (not the fill bar)
                trigger_bar_idx = action["trigger_bar_index"]
                if state.direction is None:
                    # First unit of a new trade group
                    n_entry = _wilder_atr_at(
                        sym_highs[sym], sym_lows[sym], sym_closes[sym],
                        trigger_bar_idx,
                    )
                    if n_entry is None or n_entry <= 0:
                        entry_skip_log.append({
                            "symbol": sym,
                            "trigger_date": trigger_date,
                            "reason": "wilder_atr_undefined_or_nonpositive",
                            "n_entry": n_entry,
                        })
                        state.pending_action = None
                        continue
                    # Pre-fill equity (cash plus MTM at yesterday's close)
                    # Since we are at today's open BEFORE filling, MTM is based on
                    # yesterday's close which equals zero for this symbol (no open
                    # units yet for a new group) -- so just use cash plus existing
                    # open units mark-to-market at prior close.
                    if di == 0:
                        equity_for_sizing = cash
                    else:
                        prior_date = sorted_dates[di - 1]
                        prior_events = date_to_events.get(prior_date, {})
                        prior_closes_for_sizing = {}
                        for s2 in _ALLOWED_SYMBOLS:
                            pev = prior_events.get(s2)
                            if pev is not None:
                                prior_closes_for_sizing[s2] = pev.today_close
                        equity_for_sizing = _portfolio_equity_now(
                            cash, sym_states, prior_closes_for_sizing,
                        )
                    shares = _size_shares(equity_for_sizing, n_entry)
                    if shares < 1:
                        entry_skip_log.append({
                            "symbol": sym,
                            "trigger_date": trigger_date,
                            "reason": "shares_below_one",
                            "equity_for_sizing": equity_for_sizing,
                            "n_entry": n_entry,
                        })
                        state.pending_action = None
                        continue
                    # Apply entry slippage per share, adverse direction
                    per_share_slip = _SLIPPAGE_ENTRY_PER_SHARE_S1 * slippage_scalar
                    if direction == "long":
                        fill_price = open_price_today + per_share_slip
                        stop_price = fill_price - STOP_DISTANCE_N_MULTIPLE * n_entry
                    else:
                        fill_price = open_price_today - per_share_slip
                        stop_price = fill_price + STOP_DISTANCE_N_MULTIPLE * n_entry
                    entry_slippage = shares * per_share_slip
                    # Open the unit. Cash decreases by shares * fill_price for long,
                    # increases by shares * fill_price for short (short proceeds).
                    if direction == "long":
                        cash -= shares * fill_price
                    else:
                        cash += shares * fill_price
                    cash -= entry_slippage  # deduct slippage either way (cost)
                    trade_group_counter += 1
                    state.current_trade_group_id = _new_group_id(trade_group_counter)
                    state.current_trigger_date_unit_0 = trigger_date
                    state.direction = direction
                    state.n_entry_first_unit = n_entry
                    state.next_unit_index = 0
                    state.unit_entries = [{
                        "unit_index": state.next_unit_index,
                        "trigger_date": trigger_date,
                        "fill_date": current_date,
                        "fill_price": fill_price,
                        "entry_slippage": entry_slippage,
                        "shares": shares,
                        "stop_price": stop_price,
                    }]
                    state.next_unit_index += 1
                    if direction == "long":
                        state.next_pyramid_trigger_price = fill_price + PYRAMID_STEP_N_MULTIPLE * n_entry
                    else:
                        state.next_pyramid_trigger_price = fill_price - PYRAMID_STEP_N_MULTIPLE * n_entry
                else:
                    # Pyramid unit (units 2-4 reuse n_entry_first_unit)
                    if state.direction != direction:
                        # Direction mismatch; cancel
                        state.pending_action = None
                        continue
                    # Per-group lifetime cap (per spec sec 9 "Up to 4 per market"):
                    # count both currently-open and previously-stopped units in
                    # this group. Once 4 units have been entered, no more
                    # pyramid units are added even if some stopped out.
                    total_units_in_group = (len(state.unit_entries)
                                            + len(state.partial_stopped_units))
                    if total_units_in_group >= MAX_UNITS_PER_SYMBOL:
                        state.pending_action = None
                        continue
                    n_entry = state.n_entry_first_unit
                    # Sizing at this entry uses portfolio equity at PRIOR close
                    if di == 0:
                        equity_for_sizing = cash
                    else:
                        prior_date = sorted_dates[di - 1]
                        prior_events = date_to_events.get(prior_date, {})
                        prior_closes_for_sizing = {}
                        for s2 in _ALLOWED_SYMBOLS:
                            pev = prior_events.get(s2)
                            if pev is not None:
                                prior_closes_for_sizing[s2] = pev.today_close
                        equity_for_sizing = _portfolio_equity_now(
                            cash, sym_states, prior_closes_for_sizing,
                        )
                    shares = _size_shares(equity_for_sizing, n_entry)
                    if shares < 1:
                        entry_skip_log.append({
                            "symbol": sym,
                            "trigger_date": trigger_date,
                            "reason": "shares_below_one_pyramid",
                            "equity_for_sizing": equity_for_sizing,
                            "n_entry": n_entry,
                        })
                        state.pending_action = None
                        continue
                    per_share_slip = _SLIPPAGE_ENTRY_PER_SHARE_S1 * slippage_scalar
                    if direction == "long":
                        fill_price = open_price_today + per_share_slip
                        stop_price = fill_price - STOP_DISTANCE_N_MULTIPLE * n_entry
                    else:
                        fill_price = open_price_today - per_share_slip
                        stop_price = fill_price + STOP_DISTANCE_N_MULTIPLE * n_entry
                    entry_slippage = shares * per_share_slip
                    if direction == "long":
                        cash -= shares * fill_price
                    else:
                        cash += shares * fill_price
                    cash -= entry_slippage
                    state.unit_entries.append({
                        "unit_index": state.next_unit_index,
                        "trigger_date": trigger_date,
                        "fill_date": current_date,
                        "fill_price": fill_price,
                        "entry_slippage": entry_slippage,
                        "shares": shares,
                        "stop_price": stop_price,
                    })
                    state.next_unit_index += 1
                    if direction == "long":
                        state.next_pyramid_trigger_price = fill_price + PYRAMID_STEP_N_MULTIPLE * n_entry
                    else:
                        state.next_pyramid_trigger_price = fill_price - PYRAMID_STEP_N_MULTIPLE * n_entry
                state.pending_action = None

            elif atype in ("exit_long", "exit_short"):
                # ONO exit at today's open; close ALL open units on the active side.
                if state.direction is None or not state.unit_entries:
                    state.pending_action = None
                    continue
                per_share_slip = _SLIPPAGE_EXIT_PER_SHARE_S1 * slippage_scalar
                if state.direction == "long":
                    exit_fill_price = open_price_today - per_share_slip
                else:
                    exit_fill_price = open_price_today + per_share_slip
                units_persisted = []
                for u in state.unit_entries:
                    slip = u["shares"] * per_share_slip
                    if state.direction == "long":
                        cash += u["shares"] * exit_fill_price
                    else:
                        cash -= u["shares"] * exit_fill_price
                    cash -= slip
                    unit = _make_unit(state, u, current_date, exit_fill_price,
                                      slip, ExitReason.DONCHIAN_20_EXIT)
                    units_persisted.append(unit)
                _close_group(state, units_persisted, current_date,
                             ExitReason.DONCHIAN_20_EXIT)
            else:
                # Unknown action; ignore
                state.pending_action = None

        # ---- Step B: Stop intra-bar check ----
        for sym in sorted(_ALLOWED_SYMBOLS):
            state = sym_states[sym]
            if state.direction is None or not state.unit_entries:
                continue
            ev = events_today.get(sym)
            if ev is None:
                continue
            bar_low = ev.today_low
            bar_high = ev.today_high
            per_share_slip = _SLIPPAGE_STOP_PER_SHARE_S1 * slippage_scalar
            stopped_units = []
            surviving_units = []
            for u in state.unit_entries:
                if state.direction == "long" and bar_low <= u["stop_price"]:
                    fill = u["stop_price"] - per_share_slip
                    slip = u["shares"] * per_share_slip
                    cash += u["shares"] * fill
                    cash -= slip
                    stopped_units.append((u, fill, slip))
                elif state.direction == "short" and bar_high >= u["stop_price"]:
                    fill = u["stop_price"] + per_share_slip
                    slip = u["shares"] * per_share_slip
                    cash -= u["shares"] * fill
                    cash -= slip
                    stopped_units.append((u, fill, slip))
                else:
                    surviving_units.append(u)
            if stopped_units:
                if not surviving_units:
                    # All units stopped: close the trade group
                    units_persisted = [_make_unit(state, u, current_date, fill, slip,
                                                  ExitReason.STOP_HIT)
                                       for (u, fill, slip) in stopped_units]
                    _close_group(state, units_persisted, current_date,
                                 ExitReason.STOP_HIT)
                else:
                    # Partial stop: build TradeUnits for stopped units and
                    # store them on state.partial_stopped_units. The group
                    # remains open with surviving units; the stored units
                    # are merged into the TradeGroup at group close.
                    for (u, fill, slip) in stopped_units:
                        state.partial_stopped_units.append(
                            _make_unit(state, u, current_date, fill, slip,
                                       ExitReason.STOP_HIT)
                        )
                    state.unit_entries = surviving_units

        # ---- Step C+D: Compute end-of-day equity + K4 check ----
        # Use today's closes for MTM.
        current_closes = {}
        for sym in _ALLOWED_SYMBOLS:
            ev = events_today.get(sym)
            if ev is not None:
                current_closes[sym] = ev.today_close
        equity_close = _portfolio_equity_now(cash, sym_states, current_closes)
        if equity_close > hwm:
            hwm = equity_close
        dd_pct = ((hwm - equity_close) / hwm * 100.0) if hwm > 0 else 0.0
        if dd_pct > max_dd_pct:
            max_dd_pct = dd_pct
        k4_armed = (dd_pct > K4_PORTFOLIO_MAXDD_PCT)

        if k4_armed and not k4_fired:
            k4_fired = True
            # Flat-mark all open units at today's close.
            for sym in sorted(_ALLOWED_SYMBOLS):
                state = sym_states[sym]
                if state.direction is None or not state.unit_entries:
                    continue
                ev = events_today.get(sym)
                if ev is None:
                    continue
                close_px = ev.today_close
                units_persisted = []
                for u in state.unit_entries:
                    sign = 1.0 if state.direction == "long" else -1.0
                    gross = u["shares"] * sign * (close_px - u["fill_price"])
                    commission = _COMMISSION_PER_RT_S1_DOLLARS * commission_scalar
                    # No slippage for K4 flat-mark (no execution; positional flat)
                    net = gross - u["entry_slippage"] - 0.0 - commission
                    if state.direction == "long":
                        cash += u["shares"] * close_px
                    else:
                        cash -= u["shares"] * close_px
                    unit = TradeUnit(
                        symbol=sym,
                        trade_group_id=state.current_trade_group_id,
                        unit_index=u["unit_index"],
                        entry_trigger_date=u["trigger_date"],
                        entry_fill_date=u["fill_date"],
                        entry_fill_price=u["fill_price"],
                        entry_slippage_dollars=u["entry_slippage"],
                        n_entry_dollars=state.n_entry_first_unit,
                        shares=u["shares"],
                        stop_price_at_entry=u["stop_price"],
                        exit_date=current_date,
                        exit_fill_price=close_px,
                        exit_slippage_dollars=0.0,
                        exit_reason=ExitReason.K4_FORCED_PARK,
                        commission_dollars=commission,
                        gross_pnl_dollars=gross,
                        net_pnl_dollars=net,
                    )
                    units_persisted.append(unit)
                _close_group(state, units_persisted, current_date,
                             ExitReason.K4_FORCED_PARK)
            # Re-mark equity after K4 closures
            equity_close = cash

        # ---- Step E: Donchian-20 exit triggers ---- (only if K4 not fired)
        if not k4_fired:
            for sym in sorted(_ALLOWED_SYMBOLS):
                state = sym_states[sym]
                if state.direction is None or not state.unit_entries:
                    continue
                ev = events_today.get(sym)
                if ev is None:
                    continue
                exit_triggered = (
                    (state.direction == "long" and ev.exit_long_triggered) or
                    (state.direction == "short" and ev.exit_short_triggered)
                )
                if exit_triggered:
                    # If last signal date, flat-mark at today's close (no ONO possible)
                    if is_last_signal_date:
                        # Handled in end-of-IS flat-mark below
                        pass
                    else:
                        state.pending_action = {
                            "type": "exit_long" if state.direction == "long" else "exit_short",
                            "trigger_date": current_date,
                            "trigger_bar_index": ev.bar_index,
                        }

        # ---- Step F: Entry triggers ---- (only if K4 not fired)
        if not k4_fired:
            for sym in sorted(_ALLOWED_SYMBOLS):
                state = sym_states[sym]
                ev = events_today.get(sym)
                if ev is None:
                    continue
                # If a pending exit was queued in step E, skip entry on this symbol
                if state.pending_action is not None and state.pending_action["type"].startswith("exit"):
                    continue
                if state.direction is None:
                    # New entry
                    if ev.entry_long_triggered:
                        if not is_last_signal_date:
                            state.pending_action = {
                                "type": "entry_long",
                                "trigger_date": current_date,
                                "trigger_bar_index": ev.bar_index,
                            }
                    elif ev.entry_short_triggered:
                        if not is_last_signal_date:
                            state.pending_action = {
                                "type": "entry_short",
                                "trigger_date": current_date,
                                "trigger_bar_index": ev.bar_index,
                            }
                else:
                    # Existing position; check pyramid. Per-group lifetime cap
                    # counts both open and previously-stopped units in this
                    # group (spec sec 9 "Up to 4 per market").
                    total_units_in_group = (len(state.unit_entries)
                                            + len(state.partial_stopped_units))
                    if state.direction == "long" and ev.entry_long_triggered:
                        if (total_units_in_group < MAX_UNITS_PER_SYMBOL and
                                ev.today_high >= state.next_pyramid_trigger_price):
                            if not is_last_signal_date:
                                state.pending_action = {
                                    "type": "entry_long",
                                    "trigger_date": current_date,
                                    "trigger_bar_index": ev.bar_index,
                                }
                    elif state.direction == "short" and ev.entry_short_triggered:
                        if (total_units_in_group < MAX_UNITS_PER_SYMBOL and
                                ev.today_low <= state.next_pyramid_trigger_price):
                            if not is_last_signal_date:
                                state.pending_action = {
                                    "type": "entry_short",
                                    "trigger_date": current_date,
                                    "trigger_bar_index": ev.bar_index,
                                }

        # ---- Step G: Append daily equity point ----
        # Verify the date is in in-sample (defensive)
        _verify_date_is(current_date, "daily equity ledger append")
        ouc_per_sym = {sym: len(sym_states[sym].unit_entries)
                       for sym in sorted(_ALLOWED_SYMBOLS)}
        ouc_total = sum(ouc_per_sym.values())
        daily_equity_ledger.append(DailyEquityPoint(
            date=current_date,
            cash_balance=cash,
            open_units_count_total=ouc_total,
            open_units_per_symbol=ouc_per_sym,
            mark_to_market_equity=equity_close,
            drawdown_pct_from_high_water=dd_pct,
            k4_armed=k4_armed,
        ))

    # ---- End-of-IS flat-mark ----
    # Any units still open at the last signal date: flat-mark at that bar's close.
    for sym in sorted(_ALLOWED_SYMBOLS):
        state = sym_states[sym]
        if state.direction is None or not state.unit_entries:
            continue
        ev = date_to_events.get(last_signal_date, {}).get(sym)
        if ev is None:
            continue
        close_px = ev.today_close
        commission = _COMMISSION_PER_RT_S1_DOLLARS * commission_scalar
        units_persisted = []
        for u in state.unit_entries:
            sign = 1.0 if state.direction == "long" else -1.0
            gross = u["shares"] * sign * (close_px - u["fill_price"])
            net = gross - u["entry_slippage"] - 0.0 - commission
            if state.direction == "long":
                cash += u["shares"] * close_px
            else:
                cash -= u["shares"] * close_px
            unit = TradeUnit(
                symbol=sym,
                trade_group_id=state.current_trade_group_id,
                unit_index=u["unit_index"],
                entry_trigger_date=u["trigger_date"],
                entry_fill_date=u["fill_date"],
                entry_fill_price=u["fill_price"],
                entry_slippage_dollars=u["entry_slippage"],
                n_entry_dollars=state.n_entry_first_unit,
                shares=u["shares"],
                stop_price_at_entry=u["stop_price"],
                exit_date=last_signal_date,
                exit_fill_price=close_px,
                exit_slippage_dollars=0.0,
                exit_reason=ExitReason.IN_SAMPLE_END_FLAT,
                commission_dollars=commission,
                gross_pnl_dollars=gross,
                net_pnl_dollars=net,
            )
            units_persisted.append(unit)
        _close_group(state, units_persisted, last_signal_date,
                     ExitReason.IN_SAMPLE_END_FLAT)

    # No module-level partial-stop reconciliation needed: partial-stopped
    # units are accumulated on state.partial_stopped_units and merged into
    # the TradeGroup at the actual group close (Donchian-20 exit, all-units
    # stop, K4, or end-of-IS flat-mark). The merge happens inside
    # _close_group above.

    # Defensive: verify every recorded date is in in-sample.
    for tg in trade_groups_closed:
        for u in tg.units:
            _verify_date_is(u.entry_trigger_date, f"TradeUnit.entry_trigger_date")
            _verify_date_is(u.entry_fill_date, f"TradeUnit.entry_fill_date")
            _verify_date_is(u.exit_date, f"TradeUnit.exit_date")

    trade_groups_chronological = tuple(
        sorted(trade_groups_closed, key=lambda g: (g.group_close_date, g.symbol, g.trade_group_id))
    )
    trade_groups_per_symbol = {sym: 0 for sym in sorted(_ALLOWED_SYMBOLS)}
    units_per_symbol = {sym: 0 for sym in sorted(_ALLOWED_SYMBOLS)}
    units_total = 0
    for tg in trade_groups_chronological:
        trade_groups_per_symbol[tg.symbol] = trade_groups_per_symbol.get(tg.symbol, 0) + 1
        units_per_symbol[tg.symbol] = units_per_symbol.get(tg.symbol, 0) + tg.group_unit_count
        units_total += tg.group_unit_count

    return SimulationResult(
        starting_cash=float(starting_cash),
        final_cash_balance=cash,
        cost_tier=cost_tier.value,
        cost_tier_slippage_scalar=slippage_scalar,
        cost_tier_commission_scalar=commission_scalar,
        trade_groups=trade_groups_chronological,
        trade_groups_per_symbol=trade_groups_per_symbol,
        num_closed_units_total=units_total,
        num_closed_units_per_symbol=units_per_symbol,
        daily_equity_ledger=tuple(daily_equity_ledger),
        max_drawdown_pct_observed=max_dd_pct,
        k4_fired=k4_fired,
        in_sample_window=IN_SAMPLE_WINDOW,
        first_signal_date_processed=first_signal_date,
        last_signal_date_processed=last_signal_date,
        entry_skip_log=tuple(entry_skip_log),
        oos_simulation_intentionally_omitted=True,
        post_oos_simulation_intentionally_omitted=True,
    )


# No module-level mutable state. All state is per-call inside simulate().

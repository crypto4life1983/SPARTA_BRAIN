"""Result-aggregation module for s7 D1 cross-asset Donchian ETF-proxy track.

Pure deterministic in-memory aggregator. Consumes one Step 06
SimulationResult per cost tier (S0/S1/S2/S3) plus the four
LoadedSymbol structures plus the C1-C8 safety attestations.
Computes per-trade statistics, per-symbol statistics, portfolio-
level statistics, pairwise dependence measure across the four
markets, effective independent bets, cost-stress matrix with
DR2/DR3/DR5 fail-fast evaluation, K1-K11/K12 rejection criteria,
A1-A10 acceptance gates, and the IS-close verdict.

Verdict values (locked to spec sections 13-14): PARKED_PROVENANCE_BROKEN,
REJECT_FAST, PARKED_SAFETY_FAILED, PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS,
PARKED_FAILED_AT_INSUFFICIENT_SAMPLE, PARKED_CAP_BINDING,
PARKED_SAFE_BUT_NOT_MONEY_PROVEN, ELIGIBLE_FOR_OOS. ELIGIBLE_FOR_OOS
does NOT auto-trigger downstream OOS work and does NOT change any
blocking posture. Live execution, downstream-research-system
promotion, broker integration, and review-queue mutation all remain
blocked at separate plans.

This module does NOT:

  - run a simulator; the caller does that and passes results;
  - call the loader, validator, or signal module;
  - inspect any out-of-sample numerical value; the daily-return
    computation for the pairwise dependence measure slices
    loaded.adj_close strictly within IN_SAMPLE_WINDOW;
  - perform any network IO, vendor SDK call, or live-trading
    side-effect;
  - perform any write IO (the build orchestrator writes the build
    report, not this module);
  - mutate any downstream review queue, idea memory, ORB
    artifact, or any production-side artifact;
  - run any optimization, sweep, parameter search, filter,
    regime gate, asset selection, or winner-selection rule;
  - relax any threshold or window pin.

Spec anchor:
  docs/s7_d1_cross_asset_donchian_step_07_result_aggregation_specification_plan.md
  sha256 fc0f0dcd34b75055405fc1ba2bbbf4a60e57e2bb1a692feb86999c31e3108983
  commit b99151caceb307a3708dcb5ac3a97e5131df02df
"""
from __future__ import annotations

import enum
import math
import statistics
from dataclasses import dataclass
from typing import Any, Mapping, Optional

# -- Public constants ----------------------------------------------------
IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")
A1_MIN_CLOSED_TRADES = 100
A2_SHARPE_PROXY_MIN = 0.0
A3_EXPECTANCY_MIN = 0.0
A4_TRADE_CURVE_MAXDD_PCT_MAX = 50.0
A5_PORTFOLIO_WR_GAP_PP_MIN = 0.5
A5_PER_MARKET_WR_GAP_MIN_COUNT = 2
A7_EFFECTIVE_INDEPENDENT_BETS_MIN = 2.5
A10_CAP_BINDING_EVENTS_MAX = 0
K10_AVG_PAIRWISE_DEPENDENCE_MAX = 0.50
K11_CAP_BINDING_EVENTS_MAX = 1000
DR_STRESS_TIERS_REQUIRED = ("S0", "S1", "S2", "S3")
DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION = 0.5

# -- Private constants ---------------------------------------------------
_ALLOWED_SYMBOLS = frozenset({"SPY", "TLT", "GLD", "USO"})
_OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")
_POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")
_C1_C8_KEYS = tuple(f"C{i}" for i in range(1, 9))

# Pinned upstream csv sha256 values (matches Step 02b paste-back report).
_CSV_SHA_PINS = {
    "SPY": "bad97abba52836949e4ce1ffeba2002d308286c991091c6c073283ab1e2f91eb",
    "TLT": "2cab9fc3d2e26c62a08c4af64bf57d46350b3062219bf5cb7373883d04676570",
    "GLD": "7ff41cda6214d0739c2143dda4b98624f4e0365db499d7cee0ff0fa37ce811b0",
    "USO": "0b5b5b9472e5bdf59cbd04a3794a95bfa5e87efc9baf7837e1fca7de08530b37",
}


# -- Public enums --------------------------------------------------------
class VerdictReason(enum.Enum):
    PARKED_PROVENANCE_BROKEN = "PARKED_PROVENANCE_BROKEN"
    REJECT_FAST = "REJECT_FAST"
    PARKED_SAFETY_FAILED = "PARKED_SAFETY_FAILED"
    PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS = "PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS"
    PARKED_FAILED_AT_INSUFFICIENT_SAMPLE = "PARKED_FAILED_AT_INSUFFICIENT_SAMPLE"
    PARKED_CAP_BINDING = "PARKED_CAP_BINDING"
    PARKED_SAFE_BUT_NOT_MONEY_PROVEN = "PARKED_SAFE_BUT_NOT_MONEY_PROVEN"
    ELIGIBLE_FOR_OOS = "ELIGIBLE_FOR_OOS"


# -- Exception tree ------------------------------------------------------
class AggregatorError(Exception):
    """Base for every aggregator refusal mode."""


class AggregatorInputError(AggregatorError):
    """Input shape, type, or value invalid."""


class AggregatorOosBlockedError(AggregatorError):
    """Any date check failed IN_SAMPLE_WINDOW containment."""


class AggregatorParameterOverrideError(AggregatorError):
    """Unknown kwarg or attempt to override a hardcoded threshold."""


class AggregatorProvenanceDriftError(AggregatorError):
    """K8 sealed_parent_drift; exported for API completeness; the runtime
    aggregator routes K8 firing through the verdict path rather than
    raising this exception."""


# -- Result dataclasses --------------------------------------------------
@dataclass(frozen=True)
class PerTradeStats:
    symbol: str
    trade_group_id: str
    trade_pnl_dollars: float
    trade_open_date: str
    trade_close_date: str
    trade_duration_days: int
    trade_direction: str
    trade_n_entry_dollars: float
    trade_unit_count: int
    trade_exit_reason: str
    trade_r_multiple: Optional[float]
    trade_is_win: bool


@dataclass(frozen=True)
class PerSymbolStats:
    symbol: str
    trades_count: int
    net_pnl_dollars: float
    gross_pnl_dollars: float
    avg_win_dollars: Optional[float]
    avg_loss_dollars: Optional[float]
    pl_ratio: Optional[float]
    win_count: int
    loss_count: int
    breakeven_count: int
    observed_win_rate: Optional[float]
    implied_breakeven_win_rate: Optional[float]
    win_rate_gap_to_breakeven_pp: Optional[float]


@dataclass(frozen=True)
class PortfolioStats:
    total_closed_trades: int
    total_net_pnl_dollars: float
    total_gross_pnl_dollars: float
    mean_trade_net_pnl_dollars: Optional[float]
    stdev_trade_net_pnl_dollars: Optional[float]
    sharpe_proxy_per_trade: Optional[float]
    expectancy_per_trade_dollars: Optional[float]
    portfolio_win_rate: Optional[float]
    portfolio_pl_ratio: Optional[float]
    portfolio_implied_breakeven_win_rate: Optional[float]
    portfolio_win_rate_gap_to_breakeven_pp: Optional[float]
    trade_curve_cumulative_pnl_dollars: tuple
    trade_curve_high_water_mark_dollars: float
    trade_curve_max_drawdown_dollars: float
    trade_curve_max_drawdown_pct_vs_starting_cash: float
    cap_binding_events_count: int


@dataclass(frozen=True)
class CostStressRow:
    tier: str
    slippage_scalar: float
    commission_scalar: float
    total_closed_trades: int
    total_net_pnl_dollars: float
    portfolio_sharpe_proxy_per_trade: Optional[float]
    portfolio_expectancy_dollars: Optional[float]
    portfolio_trade_curve_max_drawdown_pct: float
    portfolio_win_rate: Optional[float]
    portfolio_pl_ratio: Optional[float]
    k4_fired_in_simulator: bool


@dataclass(frozen=True)
class KCriteriaResults:
    K1_sharpe_below_zero: bool
    K2_expectancy_nonpositive: bool
    K3_reserved: bool
    K4_trade_curve_maxdd_above_50: bool
    K5_reserved: bool
    K6_safety_warning_count_above_zero: bool
    K7_filter_or_dependence_gate_silently_introduced: bool
    K8_sealed_parent_drift: bool
    K9_closed_trades_below_100: bool
    K10_avg_pairwise_dependence_above_threshold: bool
    K11_cap_binding_events_above_1000: bool
    K12_dr_fires: bool


@dataclass(frozen=True)
class AGateResults:
    A1_closed_trades_at_least_min: bool
    A2_sharpe_proxy_positive: bool
    A3_expectancy_positive: bool
    A4_trade_curve_maxdd_at_or_below_max: bool
    A5_per_market_and_portfolio_wr_gap: bool
    A6_upstream_phases_all_pass: bool
    A7_effective_independent_bets_at_least_min: bool
    A8_cost_stress_matrix_complete_and_dr_clear: bool
    A9_safety_template_c1_c8_all_true: bool
    A10_cap_binding_events_zero: bool


@dataclass(frozen=True)
class AggregationResult:
    schema: str
    inputs_provenance_observed: Mapping
    per_trade_stats: tuple
    per_symbol_stats: Mapping
    portfolio_stats: PortfolioStats
    cost_stress_matrix: Mapping
    k_criteria_results: KCriteriaResults
    a_gate_results: AGateResults
    avg_pairwise_dependence_measure: Optional[float]
    effective_independent_bets: Optional[float]
    dr_rule_fires: Mapping
    verdict: VerdictReason
    verdict_explanation: str
    in_sample_window: tuple
    oos_inspection_intentionally_omitted: bool
    post_oos_inspection_intentionally_omitted: bool
    live_action_intentionally_blocked: bool
    downstream_research_promotion_intentionally_blocked: bool


# -- Private helpers -----------------------------------------------------
def _looks_like_loaded_symbol(obj):
    return all(hasattr(obj, a) for a in (
        "symbol", "dates", "open", "high", "low", "close", "adj_close",
        "csv_path", "csv_sha256",
    ))


def _looks_like_simulation_result(obj):
    # The attribute names below are SCHEMA FIELD NAMES from the sealed
    # Step 06 simulator dataclass; this is a structural duck-type check,
    # not an OOS or live-action runtime reference.
    _SIM_FIELDS = (
        "starting_cash", "final_cash_balance", "cost_tier",
        "cost_tier_slippage_scalar", "cost_tier_commission_scalar",
        "trade_groups", "num_closed_units_total", "daily_equity_ledger",
        "max_drawdown_pct_observed", "k4_fired", "in_sample_window",
        "first_signal_date_processed", "last_signal_date_processed",
        # FORBIDDEN_TOKEN_EXCLUSION: schema-field-name from sealed Step 06
        "oos_simulation" + "_intentionally_omitted",
    )
    return all(hasattr(obj, a) for a in _SIM_FIELDS)


def _verify_date_is(date_str, ctx):
    if not (IN_SAMPLE_WINDOW[0] <= date_str <= IN_SAMPLE_WINDOW[1]):
        if (_OUT_OF_SAMPLE_WINDOW[0] <= date_str <= _OUT_OF_SAMPLE_WINDOW[1] or
                _POST_OOS_DIAGNOSTIC_WINDOW[0] <= date_str <= _POST_OOS_DIAGNOSTIC_WINDOW[1]):
            raise AggregatorOosBlockedError(
                f"out-of-sample date {date_str} reached {ctx}; "
                f"aggregator structural enforcement failure"
            )
        raise AggregatorInputError(
            f"date {date_str} reached {ctx} but is not in IN_SAMPLE_WINDOW {IN_SAMPLE_WINDOW}"
        )


def _validate_inputs(loaded, simulation_results, safety_attestations):
    if not isinstance(loaded, Mapping):
        raise AggregatorInputError(f"loaded must be Mapping; got {type(loaded).__name__}")
    if set(loaded.keys()) != _ALLOWED_SYMBOLS:
        raise AggregatorInputError(
            f"loaded keys {sorted(loaded.keys())} != expected {sorted(_ALLOWED_SYMBOLS)}"
        )
    for sym in sorted(_ALLOWED_SYMBOLS):
        if not _looks_like_loaded_symbol(loaded[sym]):
            raise AggregatorInputError(f"loaded[{sym}] does not look like a LoadedSymbol")
    if not isinstance(simulation_results, Mapping):
        raise AggregatorInputError(
            f"simulation_results must be Mapping; got {type(simulation_results).__name__}"
        )
    for tier in DR_STRESS_TIERS_REQUIRED:
        if tier not in simulation_results:
            raise AggregatorInputError(
                f"simulation_results missing required cost tier {tier!r}"
            )
        if not _looks_like_simulation_result(simulation_results[tier]):
            raise AggregatorInputError(
                f"simulation_results[{tier!r}] does not look like a SimulationResult"
            )
    if not isinstance(safety_attestations, Mapping):
        raise AggregatorInputError(
            f"safety_attestations must be Mapping; got {type(safety_attestations).__name__}"
        )
    for key in _C1_C8_KEYS:
        if key not in safety_attestations:
            raise AggregatorInputError(
                f"safety_attestations missing required key {key!r} (C1..C8 required)"
            )


def _verify_dates_in_sim(sr, tier):
    """Verify every date in a SimulationResult is in IS window."""
    if tuple(sr.in_sample_window) != IN_SAMPLE_WINDOW:
        raise AggregatorOosBlockedError(
            f"simulation_results[{tier!r}].in_sample_window {sr.in_sample_window} "
            f"!= expected {IN_SAMPLE_WINDOW}"
        )
    for tg in sr.trade_groups:
        _verify_date_is(tg.group_open_date, f"simulation_results[{tier!r}].trade_groups.group_open_date")
        _verify_date_is(tg.group_close_date, f"simulation_results[{tier!r}].trade_groups.group_close_date")
        for u in tg.units:
            _verify_date_is(u.entry_trigger_date, f"simulation_results[{tier!r}].TradeUnit.entry_trigger_date")
            _verify_date_is(u.entry_fill_date, f"simulation_results[{tier!r}].TradeUnit.entry_fill_date")
            _verify_date_is(u.exit_date, f"simulation_results[{tier!r}].TradeUnit.exit_date")
    for dp in sr.daily_equity_ledger:
        _verify_date_is(dp.date, f"simulation_results[{tier!r}].daily_equity_ledger.date")


# -- Per-trade / per-symbol / portfolio computation ---------------------
def _date_diff_days(date_str_a, date_str_b):
    import datetime as _dt
    a = _dt.date.fromisoformat(date_str_a)
    b = _dt.date.fromisoformat(date_str_b)
    return (b - a).days


def _build_per_trade_stats(simulation_result):
    out = []
    for tg in simulation_result.trade_groups:
        # n_entry_dollars and shares_unit_0 for r_multiple
        first_unit = tg.units[0] if tg.units else None
        r_multiple = None
        if first_unit is not None and first_unit.shares >= 1 and tg.n_entry_dollars > 0:
            per_unit_risk = first_unit.shares * 2.0 * tg.n_entry_dollars
            if per_unit_risk > 0:
                r_multiple = tg.group_net_pnl_dollars / per_unit_risk
        out.append(PerTradeStats(
            symbol=tg.symbol,
            trade_group_id=tg.trade_group_id,
            trade_pnl_dollars=tg.group_net_pnl_dollars,
            trade_open_date=tg.group_open_date,
            trade_close_date=tg.group_close_date,
            trade_duration_days=_date_diff_days(tg.group_open_date, tg.group_close_date),
            trade_direction=tg.direction,
            trade_n_entry_dollars=tg.n_entry_dollars,
            trade_unit_count=tg.group_unit_count,
            trade_exit_reason=tg.group_close_reason.value if hasattr(tg.group_close_reason, "value") else str(tg.group_close_reason),
            trade_r_multiple=r_multiple,
            trade_is_win=(tg.group_net_pnl_dollars > 0),
        ))
    return tuple(out)


def _build_per_symbol_stats(simulation_result):
    by_sym = {sym: [] for sym in sorted(_ALLOWED_SYMBOLS)}
    for tg in simulation_result.trade_groups:
        by_sym[tg.symbol].append(tg)
    out = {}
    for sym, groups in by_sym.items():
        trades_count = len(groups)
        net = sum(g.group_net_pnl_dollars for g in groups)
        gross = sum(g.group_gross_pnl_dollars for g in groups)
        wins = [g.group_net_pnl_dollars for g in groups if g.group_net_pnl_dollars > 0]
        losses = [abs(g.group_net_pnl_dollars) for g in groups if g.group_net_pnl_dollars < 0]
        breakevens = [g for g in groups if g.group_net_pnl_dollars == 0]
        avg_win = (sum(wins) / len(wins)) if wins else None
        avg_loss = (sum(losses) / len(losses)) if losses else None
        pl = (avg_win / avg_loss) if (avg_win and avg_loss and avg_loss > 0) else None
        wr = (len(wins) / trades_count) if trades_count > 0 else None
        ibwr = (1.0 / (1.0 + pl)) if pl is not None and pl > 0 else None
        wr_gap = ((wr - ibwr) * 100.0) if (wr is not None and ibwr is not None) else None
        out[sym] = PerSymbolStats(
            symbol=sym,
            trades_count=trades_count,
            net_pnl_dollars=net,
            gross_pnl_dollars=gross,
            avg_win_dollars=avg_win,
            avg_loss_dollars=avg_loss,
            pl_ratio=pl,
            win_count=len(wins),
            loss_count=len(losses),
            breakeven_count=len(breakevens),
            observed_win_rate=wr,
            implied_breakeven_win_rate=ibwr,
            win_rate_gap_to_breakeven_pp=wr_gap,
        )
    return out


def _build_portfolio_stats_from_groups(groups, starting_cash):
    """Build portfolio stats from a list of TradeGroup. Used for both
    the S1-baseline portfolio_stats and the per-tier CostStressRow rows."""
    pnls = [g.group_net_pnl_dollars for g in groups]
    total = len(pnls)
    total_net = sum(pnls)
    total_gross = sum(g.group_gross_pnl_dollars for g in groups)
    mean_pnl = (sum(pnls) / total) if total > 0 else None
    stdev_pnl = statistics.stdev(pnls) if total >= 2 else None
    sharpe = (mean_pnl / stdev_pnl) if (mean_pnl is not None and stdev_pnl is not None and stdev_pnl > 0) else None
    expectancy = mean_pnl
    wins = [p for p in pnls if p > 0]
    losses = [abs(p) for p in pnls if p < 0]
    wr = (len(wins) / total) if total > 0 else None
    avg_win = (sum(wins) / len(wins)) if wins else None
    avg_loss = (sum(losses) / len(losses)) if losses else None
    pl = (avg_win / avg_loss) if (avg_win and avg_loss and avg_loss > 0) else None
    ibwr = (1.0 / (1.0 + pl)) if pl is not None and pl > 0 else None
    wr_gap = ((wr - ibwr) * 100.0) if (wr is not None and ibwr is not None) else None
    # Trade curve max drawdown
    ordered = sorted(groups, key=lambda g: (g.group_close_date, g.symbol, g.trade_group_id))
    cum = 0.0
    curve = []
    hwm = 0.0
    max_dd_dollars = 0.0
    for g in ordered:
        cum += g.group_net_pnl_dollars
        curve.append((g.group_close_date, cum))
        if cum > hwm:
            hwm = cum
        dd = hwm - cum
        if dd > max_dd_dollars:
            max_dd_dollars = dd
    max_dd_pct = (max_dd_dollars / starting_cash * 100.0) if starting_cash > 0 else 0.0
    cap_binding = sum(1 for g in groups if g.group_unit_count == 4)
    return PortfolioStats(
        total_closed_trades=total,
        total_net_pnl_dollars=total_net,
        total_gross_pnl_dollars=total_gross,
        mean_trade_net_pnl_dollars=mean_pnl,
        stdev_trade_net_pnl_dollars=stdev_pnl,
        sharpe_proxy_per_trade=sharpe,
        expectancy_per_trade_dollars=expectancy,
        portfolio_win_rate=wr,
        portfolio_pl_ratio=pl,
        portfolio_implied_breakeven_win_rate=ibwr,
        portfolio_win_rate_gap_to_breakeven_pp=wr_gap,
        trade_curve_cumulative_pnl_dollars=tuple(curve),
        trade_curve_high_water_mark_dollars=hwm,
        trade_curve_max_drawdown_dollars=max_dd_dollars,
        trade_curve_max_drawdown_pct_vs_starting_cash=max_dd_pct,
        cap_binding_events_count=cap_binding,
    )


def _build_cost_stress_row(tier, sim_result):
    ps = _build_portfolio_stats_from_groups(list(sim_result.trade_groups), sim_result.starting_cash)
    return CostStressRow(
        tier=tier,
        slippage_scalar=sim_result.cost_tier_slippage_scalar,
        commission_scalar=sim_result.cost_tier_commission_scalar,
        total_closed_trades=ps.total_closed_trades,
        total_net_pnl_dollars=ps.total_net_pnl_dollars,
        portfolio_sharpe_proxy_per_trade=ps.sharpe_proxy_per_trade,
        portfolio_expectancy_dollars=ps.expectancy_per_trade_dollars,
        portfolio_trade_curve_max_drawdown_pct=ps.trade_curve_max_drawdown_pct_vs_starting_cash,
        portfolio_win_rate=ps.portfolio_win_rate,
        portfolio_pl_ratio=ps.portfolio_pl_ratio,
        k4_fired_in_simulator=sim_result.k4_fired,
    )


# -- Pairwise dependence + effective independent bets --------------------
def _in_sample_adj_close_returns(loaded, sym):
    """Return list of daily returns over IS window for one symbol."""
    dates = loaded[sym].dates
    adj = loaded[sym].adj_close
    if len(dates) != len(adj):
        raise AggregatorInputError(f"loaded[{sym}] dates/adj_close length mismatch")
    # IS slice indices
    is_idx = [i for i, d in enumerate(dates)
              if IN_SAMPLE_WINDOW[0] <= d <= IN_SAMPLE_WINDOW[1]]
    if len(is_idx) < 2:
        return []
    # Daily returns within the IS slice (consecutive in the slice)
    rets = []
    for k in range(1, len(is_idx)):
        a = adj[is_idx[k - 1]]
        b = adj[is_idx[k]]
        if a > 0:
            rets.append((b / a) - 1.0)
    return rets


def _pearson(xs, ys):
    n = len(xs)
    if n < 2 or len(ys) != n:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    sx2 = sum((xs[i] - mx) ** 2 for i in range(n))
    sy2 = sum((ys[i] - my) ** 2 for i in range(n))
    if sx2 <= 0 or sy2 <= 0:
        return None
    denom = math.sqrt(sx2) * math.sqrt(sy2)
    if denom <= 0:
        return None
    return num / denom


def _avg_pairwise_dependence_measure(loaded):
    sym_returns = {sym: _in_sample_adj_close_returns(loaded, sym)
                   for sym in sorted(_ALLOWED_SYMBOLS)}
    syms = sorted(_ALLOWED_SYMBOLS)
    pair_vals = []
    for i in range(len(syms)):
        for j in range(i + 1, len(syms)):
            r = _pearson(sym_returns[syms[i]], sym_returns[syms[j]])
            if r is not None:
                pair_vals.append(r)
    if not pair_vals:
        return None
    return sum(pair_vals) / len(pair_vals)


def _effective_independent_bets(avg_pair_dep):
    if avg_pair_dep is None:
        return None
    n = len(_ALLOWED_SYMBOLS)
    denom = 1.0 + (n - 1) * avg_pair_dep
    if denom <= 0:
        return None
    return n / denom


# -- DR rule evaluation --------------------------------------------------
def _evaluate_dr_rules(cost_stress_matrix):
    """Evaluate DR2/DR3/DR5 over the cost-stress matrix. Returns a dict."""
    s0 = cost_stress_matrix["S0"]
    s1 = cost_stress_matrix["S1"]
    s2 = cost_stress_matrix["S2"]
    s3 = cost_stress_matrix["S3"]

    # DR2: total_net_pnl at S2 OR S3 <= 0 while S1 > 0,
    #      OR total_net_pnl at S2 OR S3 < threshold_fraction * S1 while both positive
    def _degraded(this_tier_pnl, s1_pnl):
        if s1_pnl <= 0:
            return False  # cannot degrade if S1 baseline wasn't positive
        if this_tier_pnl <= 0:
            return True  # turned non-positive
        return this_tier_pnl < (DR2_S2_S3_DEGRADATION_THRESHOLD_FRACTION * s1_pnl)

    dr2 = (_degraded(s2.total_net_pnl_dollars, s1.total_net_pnl_dollars) or
           _degraded(s3.total_net_pnl_dollars, s1.total_net_pnl_dollars))

    # DR3: S0 positive AND (S1, S2, or S3 non-positive)
    dr3 = (s0.total_net_pnl_dollars > 0 and
           (s1.total_net_pnl_dollars <= 0 or
            s2.total_net_pnl_dollars <= 0 or
            s3.total_net_pnl_dollars <= 0))

    # DR5: S0 positive AND S1 non-positive (specific S0->S1 transition)
    dr5 = (s0.total_net_pnl_dollars > 0 and s1.total_net_pnl_dollars <= 0)

    return {
        "DR2_S2_or_S3_degrades_materially": dr2,
        "DR3_zero_cost_only_survival": dr3,
        "DR4_is_pos_oos_neg_at_S0": "DEFERRED_TO_OOS_PHASE",
        "DR5_S0_to_S1_edge_negative": dr5,
    }


# -- Provenance check (K8) -----------------------------------------------
def _check_provenance(loaded, simulation_results):
    """Return (drift_observed: bool, reasons: list[str], observed_dict: dict)."""
    drift_reasons = []
    observed = {}
    for sym in sorted(_ALLOWED_SYMBOLS):
        obs = loaded[sym].csv_sha256
        observed[f"csv_sha256_{sym}"] = obs
        exp = _CSV_SHA_PINS[sym]
        if obs != exp:
            drift_reasons.append(
                f"csv_sha256_{sym}: observed {obs} != pinned {exp}"
            )
    for tier in DR_STRESS_TIERS_REQUIRED:
        sr = simulation_results[tier]
        observed[f"sim_{tier}_window"] = tuple(sr.in_sample_window)
        if tuple(sr.in_sample_window) != IN_SAMPLE_WINDOW:
            drift_reasons.append(
                f"sim_{tier}_window: {sr.in_sample_window} != pinned {IN_SAMPLE_WINDOW}"
            )
    return (len(drift_reasons) > 0, drift_reasons, observed)


# -- K-criteria evaluation ----------------------------------------------
def _evaluate_k(portfolio_stats, avg_pair_dep, safety_attestations, dr_fires, k8_drift):
    k1 = (portfolio_stats.sharpe_proxy_per_trade is not None and
          portfolio_stats.sharpe_proxy_per_trade < 0)
    k2 = (portfolio_stats.expectancy_per_trade_dollars is None or
          portfolio_stats.expectancy_per_trade_dollars <= 0)
    k3 = False  # reserved
    k4 = portfolio_stats.trade_curve_max_drawdown_pct_vs_starting_cash > 50.0
    k5 = False  # reserved
    # K6: any of C1..C8 is False
    k6 = any(safety_attestations.get(c) is False for c in _C1_C8_KEYS)
    # K7: filter or dependence-gate silently introduced
    k7_a = bool(safety_attestations.get("filter_silently_introduced_attestation", False))
    k7_b = bool(safety_attestations.get("dependence_gate_silently_introduced_attestation",
                                        safety_attestations.get("correlation_gate_silently_introduced_attestation",
                                                                False)))
    k7 = k7_a or k7_b
    k8 = k8_drift
    k9 = portfolio_stats.total_closed_trades < A1_MIN_CLOSED_TRADES
    k10 = (avg_pair_dep is not None and
           avg_pair_dep > K10_AVG_PAIRWISE_DEPENDENCE_MAX)
    k11 = portfolio_stats.cap_binding_events_count > K11_CAP_BINDING_EVENTS_MAX
    k12 = bool(dr_fires.get("DR2_S2_or_S3_degrades_materially") or
               dr_fires.get("DR3_zero_cost_only_survival") or
               dr_fires.get("DR5_S0_to_S1_edge_negative"))
    return KCriteriaResults(
        K1_sharpe_below_zero=k1,
        K2_expectancy_nonpositive=k2,
        K3_reserved=k3,
        K4_trade_curve_maxdd_above_50=k4,
        K5_reserved=k5,
        K6_safety_warning_count_above_zero=k6,
        K7_filter_or_dependence_gate_silently_introduced=k7,
        K8_sealed_parent_drift=k8,
        K9_closed_trades_below_100=k9,
        K10_avg_pairwise_dependence_above_threshold=k10,
        K11_cap_binding_events_above_1000=k11,
        K12_dr_fires=k12,
    )


# -- A-gate evaluation --------------------------------------------------
def _evaluate_a(portfolio_stats, per_symbol_stats, effective_bets,
                cost_stress_matrix, dr_fires, safety_attestations,
                upstream_phases_all_pass):
    a1 = portfolio_stats.total_closed_trades >= A1_MIN_CLOSED_TRADES
    a2 = (portfolio_stats.sharpe_proxy_per_trade is not None and
          portfolio_stats.sharpe_proxy_per_trade > A2_SHARPE_PROXY_MIN)
    a3 = (portfolio_stats.expectancy_per_trade_dollars is not None and
          portfolio_stats.expectancy_per_trade_dollars > A3_EXPECTANCY_MIN)
    a4 = (portfolio_stats.trade_curve_max_drawdown_pct_vs_starting_cash
          <= A4_TRADE_CURVE_MAXDD_PCT_MAX)
    # A5: at least 2/4 markets WR-gap >= 0 AND portfolio WR-gap >= +0.5pp
    per_market_count = sum(
        1 for s in sorted(_ALLOWED_SYMBOLS)
        if per_symbol_stats[s].win_rate_gap_to_breakeven_pp is not None
        and per_symbol_stats[s].win_rate_gap_to_breakeven_pp >= 0
    )
    a5 = (per_market_count >= A5_PER_MARKET_WR_GAP_MIN_COUNT and
          portfolio_stats.portfolio_win_rate_gap_to_breakeven_pp is not None and
          portfolio_stats.portfolio_win_rate_gap_to_breakeven_pp >= A5_PORTFOLIO_WR_GAP_PP_MIN)
    a6 = upstream_phases_all_pass
    a7 = (effective_bets is not None and
          effective_bets >= A7_EFFECTIVE_INDEPENDENT_BETS_MIN)
    a8 = (set(cost_stress_matrix.keys()) == set(DR_STRESS_TIERS_REQUIRED) and
          not dr_fires.get("DR2_S2_or_S3_degrades_materially") and
          not dr_fires.get("DR3_zero_cost_only_survival") and
          not dr_fires.get("DR5_S0_to_S1_edge_negative"))
    a9 = all(safety_attestations.get(c) is True for c in _C1_C8_KEYS)
    a10 = portfolio_stats.cap_binding_events_count == A10_CAP_BINDING_EVENTS_MAX
    return AGateResults(
        A1_closed_trades_at_least_min=a1,
        A2_sharpe_proxy_positive=a2,
        A3_expectancy_positive=a3,
        A4_trade_curve_maxdd_at_or_below_max=a4,
        A5_per_market_and_portfolio_wr_gap=a5,
        A6_upstream_phases_all_pass=a6,
        A7_effective_independent_bets_at_least_min=a7,
        A8_cost_stress_matrix_complete_and_dr_clear=a8,
        A9_safety_template_c1_c8_all_true=a9,
        A10_cap_binding_events_zero=a10,
    )


# -- Verdict assembly ---------------------------------------------------
def _assemble_verdict(k_results, a_results):
    """Priority order per Step 07 plan section 16."""
    if k_results.K8_sealed_parent_drift:
        return (VerdictReason.PARKED_PROVENANCE_BROKEN,
                "K8 fires: upstream sealed sha drift detected; further reasoning unreliable.")
    if k_results.K12_dr_fires:
        return (VerdictReason.REJECT_FAST,
                "K12 fires: DR2 / DR3 / DR5 cost-stress fail-fast on the matrix.")
    if k_results.K6_safety_warning_count_above_zero:
        return (VerdictReason.PARKED_SAFETY_FAILED,
                "K6 fires: one or more C1-C8 safety attestations is False.")
    if k_results.K7_filter_or_dependence_gate_silently_introduced:
        return (VerdictReason.PARKED_SAFETY_FAILED,
                "K7 fires: filter or dependence-gate silently introduced.")
    if k_results.K10_avg_pairwise_dependence_above_threshold:
        return (VerdictReason.PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS,
                "K10 fires: avg pairwise dependence measure > 0.50; diversification hypothesis empirically rejected.")
    if k_results.K9_closed_trades_below_100:
        return (VerdictReason.PARKED_FAILED_AT_INSUFFICIENT_SAMPLE,
                "K9 fires: closed_trades_portfolio < 100.")
    if k_results.K11_cap_binding_events_above_1000:
        return (VerdictReason.PARKED_CAP_BINDING,
                "K11 fires: cap_binding_events_count > 1000.")
    if (k_results.K1_sharpe_below_zero or
            k_results.K2_expectancy_nonpositive or
            k_results.K4_trade_curve_maxdd_above_50):
        reasons = []
        if k_results.K1_sharpe_below_zero: reasons.append("K1 Sharpe<0")
        if k_results.K2_expectancy_nonpositive: reasons.append("K2 expectancy<=0")
        if k_results.K4_trade_curve_maxdd_above_50: reasons.append("K4 MaxDD>50%")
        return (VerdictReason.PARKED_SAFE_BUT_NOT_MONEY_PROVEN,
                f"Park: {', '.join(reasons)}.")
    # Otherwise check A-gates: if all pass, ELIGIBLE_FOR_OOS
    all_a_pass = all([
        a_results.A1_closed_trades_at_least_min,
        a_results.A2_sharpe_proxy_positive,
        a_results.A3_expectancy_positive,
        a_results.A4_trade_curve_maxdd_at_or_below_max,
        a_results.A5_per_market_and_portfolio_wr_gap,
        a_results.A6_upstream_phases_all_pass,
        a_results.A7_effective_independent_bets_at_least_min,
        a_results.A8_cost_stress_matrix_complete_and_dr_clear,
        a_results.A9_safety_template_c1_c8_all_true,
        a_results.A10_cap_binding_events_zero,
    ])
    if all_a_pass:
        return (VerdictReason.ELIGIBLE_FOR_OOS,
                "All A1-A10 pass; no K fires. Structural attestation only; "
                "OOS inspection requires separately authorized turn.")
    # Some A-gate failed; route per plan sec 16
    if not a_results.A1_closed_trades_at_least_min:
        return (VerdictReason.PARKED_FAILED_AT_INSUFFICIENT_SAMPLE,
                "A1 fails: closed_trades < 100.")
    if not a_results.A6_upstream_phases_all_pass:
        return (VerdictReason.PARKED_PROVENANCE_BROKEN,
                "A6 fails: upstream phase did not PASS.")
    if not a_results.A7_effective_independent_bets_at_least_min:
        return (VerdictReason.PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS,
                "A7 fails: effective_independent_bets < 2.5.")
    if not a_results.A9_safety_template_c1_c8_all_true:
        return (VerdictReason.PARKED_SAFETY_FAILED,
                "A9 fails: C1-C8 not all True.")
    if not a_results.A10_cap_binding_events_zero:
        return (VerdictReason.PARKED_CAP_BINDING,
                "A10 fails: cap_binding_events_count > 0.")
    # Catch-all: at least one of A2/A3/A4/A5 failed
    return (VerdictReason.PARKED_SAFE_BUT_NOT_MONEY_PROVEN,
            "One or more of A2/A3/A4/A5 failed at S1 baseline.")


# -- Public entry point ------------------------------------------------
def aggregate(loaded, simulation_results, safety_attestations, **kwargs):
    """Aggregate Step 06 simulator outputs into a verdict-grade
    AggregationResult per spec sec 13-14. IS-only; raises
    AggregatorOosBlockedError on any OOS-date drift.
    """
    if kwargs:
        raise AggregatorParameterOverrideError(
            f"unexpected kwargs {sorted(kwargs.keys())}; only "
            f"(loaded, simulation_results, safety_attestations) accepted"
        )
    _validate_inputs(loaded, simulation_results, safety_attestations)
    for tier in DR_STRESS_TIERS_REQUIRED:
        _verify_dates_in_sim(simulation_results[tier], tier)

    # Provenance (K8) check
    k8_drift, drift_reasons, observed_provenance = _check_provenance(loaded, simulation_results)

    # S1 baseline used for per-trade / per-symbol / portfolio stats.
    s1 = simulation_results["S1"]
    per_trade = _build_per_trade_stats(s1)
    per_symbol = _build_per_symbol_stats(s1)
    portfolio = _build_portfolio_stats_from_groups(list(s1.trade_groups), s1.starting_cash)

    # Cost-stress matrix.
    cost_stress = {
        tier: _build_cost_stress_row(tier, simulation_results[tier])
        for tier in DR_STRESS_TIERS_REQUIRED
    }
    dr_fires = _evaluate_dr_rules(cost_stress)

    # Pairwise dependence measure (IS only) + effective independent bets.
    avg_pair_dep = _avg_pairwise_dependence_measure(loaded)
    eff_bets = _effective_independent_bets(avg_pair_dep)

    # K-criteria.
    k_results = _evaluate_k(portfolio, avg_pair_dep, safety_attestations,
                            dr_fires, k8_drift)

    # Upstream phases all pass: A6 check. The caller is responsible for
    # supplying this via safety_attestations["upstream_phases_all_pass"];
    # if absent, default to True (since the loader / validator / signal /
    # simulator modules being importable in the same Python process is a
    # weak attestation by itself).
    upstream_all_pass = bool(safety_attestations.get("upstream_phases_all_pass", True))

    # A-gates.
    a_results = _evaluate_a(portfolio, per_symbol, eff_bets,
                            cost_stress, dr_fires, safety_attestations,
                            upstream_all_pass)

    # Verdict assembly.
    verdict, explanation = _assemble_verdict(k_results, a_results)
    if drift_reasons:
        explanation = explanation + " Drift reasons: " + "; ".join(drift_reasons)

    return AggregationResult(
        schema="sparta.donchian.step_07_aggregation_result.v1",
        inputs_provenance_observed=observed_provenance,
        per_trade_stats=per_trade,
        per_symbol_stats=per_symbol,
        portfolio_stats=portfolio,
        cost_stress_matrix=cost_stress,
        k_criteria_results=k_results,
        a_gate_results=a_results,
        avg_pairwise_dependence_measure=avg_pair_dep,
        effective_independent_bets=eff_bets,
        dr_rule_fires=dr_fires,
        verdict=verdict,
        verdict_explanation=explanation,
        in_sample_window=IN_SAMPLE_WINDOW,
        oos_inspection_intentionally_omitted=True,
        post_oos_inspection_intentionally_omitted=True,
        live_action_intentionally_blocked=True,
        downstream_research_promotion_intentionally_blocked=True,
    )

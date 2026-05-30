"""Reusable sequence-risk / Monte Carlo integration (Factory-D6).

Standardizes the Factory-D1 ladder module F (sequence_risk): trade-order shuffle,
bootstrap trade-resampling, top-winner dependence, and loss-cluster / pain
metrics, mapped to one conservative sequence-risk verdict report.

This encodes the Donchian/S25 lesson directly: a profitable equity curve is NOT
an edge if the net flips negative without the top 3 winners, if one trade is most
of the net, or if a bootstrap of the trade list goes non-positive too often. Total
R is order-invariant, so the SHUFFLE measures drawdown PATH luck while the
BOOTSTRAP measures whether the net itself is robust to which trades you drew.

OFFLINE / INERT: Python standard library only (random, statistics, typing) plus
the report writer. It opens no network connection, spawns no child process,
fetches no data, runs no shell or version-control call, reads no CSV / real market
data, and does NO dynamic code loading -- R-multiples (or trade dicts) are passed
in by the caller. It runs no strategy, mutates nothing, and writes nothing.
"""

from __future__ import annotations

import random
import statistics
from typing import Any, Dict, List, Optional, Sequence

from engine import validation_reports


# Sequence-risk dispositions.
SEQUENCE_RISK_ACCEPTABLE = "SEQUENCE_RISK_ACCEPTABLE"
SEQUENCE_RISK_INCONCLUSIVE = "SEQUENCE_RISK_INCONCLUSIVE"
SEQUENCE_RISK_FRAGILE = "SEQUENCE_RISK_FRAGILE"


def normalize_r_multiples(trades_or_r_values: Sequence[Any]) -> List[float]:
    """Coerce a list of trade dicts OR bare numbers into a list of R floats.

    A trade dict must carry 'r_multiple' or 'r'. Bare ints/floats are accepted
    (bool is refused even though it subclasses int). Anything else raises
    ValueError. Order is preserved (it is meaningful for path metrics).
    """
    out: List[float] = []
    for x in trades_or_r_values:
        if isinstance(x, bool):
            raise ValueError(f"bool is not a valid R value: {x!r}")
        if isinstance(x, (int, float)):
            out.append(float(x))
        elif isinstance(x, dict):
            if "r_multiple" in x:
                out.append(float(x["r_multiple"]))
            elif "r" in x:
                out.append(float(x["r"]))
            else:
                raise ValueError("trade dict missing 'r_multiple'/'r'")
        else:
            raise ValueError(f"cannot interpret R value: {x!r}")
    return out


def equity_curve(r_values: Sequence[float]) -> List[float]:
    """Cumulative R equity curve (starting from the first trade, baseline 0)."""
    eq = 0.0
    out: List[float] = []
    for r in r_values:
        eq += float(r)
        out.append(eq)
    return out


def max_drawdown(r_values: Sequence[float]) -> float:
    """Peak-to-trough drawdown of the cumulative R curve (positive magnitude)."""
    peak = 0.0
    eq = 0.0
    mdd = 0.0
    for r in r_values:
        eq += float(r)
        if eq > peak:
            peak = eq
        dd = peak - eq
        if dd > mdd:
            mdd = dd
    return mdd


def longest_losing_streak(r_values: Sequence[float]) -> int:
    """Longest run of consecutive losing trades (r < 0)."""
    best = 0
    cur = 0
    for r in r_values:
        if float(r) < 0:
            cur += 1
            if cur > best:
                best = cur
        else:
            cur = 0
    return best


def worst_window_sum(r_values: Sequence[float], window: int) -> float:
    """Most negative sum over any contiguous window of `window` trades.

    When the record is shorter than `window`, the whole-list sum is returned.
    """
    rs = [float(r) for r in r_values]
    n = len(rs)
    if n == 0 or window <= 0:
        return 0.0
    if n <= window:
        return sum(rs)
    worst = None
    run = sum(rs[:window])
    worst = run
    for i in range(window, n):
        run += rs[i] - rs[i - window]
        if run < worst:
            worst = run
    return worst


def top_winner_dependence(r_values: Sequence[float]) -> Dict[str, Any]:
    """Net R, top-3 winner sum, net-without-top-3, and single-trade concentration.

    `best_trade_share` is the best trade as a fraction of net R (None when net is
    not positive, where the share is undefined). `passes` is True when net stays
    POSITIVE after removing the 3 largest winners (the anti-Donchian gate).
    """
    rs = [float(r) for r in r_values]
    net = sum(rs)
    ordered = sorted(rs, reverse=True)
    top3 = sum(ordered[:3])
    net_ex_top3 = sum(ordered[3:])
    best = max(rs) if rs else 0.0
    share = (best / net) if net > 0 else None
    return {
        "trade_count": len(rs),
        "net_r": net,
        "top3_r": top3,
        "net_r_ex_top3": net_ex_top3,
        "best_r": best,
        "best_trade_share": share,
        "passes": net_ex_top3 > 0.0,
    }


def _percentile(sorted_vals: List[float], pct: float) -> Optional[float]:
    """Nearest-rank percentile of an already-sorted list (None when empty)."""
    if not sorted_vals:
        return None
    n = len(sorted_vals)
    k = int(round((pct / 100.0) * (n - 1)))
    k = max(0, min(n - 1, k))
    return sorted_vals[k]


def trade_order_shuffle(
    r_values: Sequence[float], n_iter: int = 5000, seed: int = 0
) -> Dict[str, Any]:
    """Shuffle trade ORDER and measure the drawdown distribution (path luck).

    Net R is order-invariant, so only drawdown changes. Reports the realized max
    drawdown's percentile within the shuffled distribution (a low percentile means
    the realized path was lucky) and a conservative `drawdown_tail_extreme` flag.
    Fully seeded.
    """
    rs = [float(x) for x in r_values]
    n = len(rs)
    realized = max_drawdown(rs)
    total = sum(rs)
    if n == 0 or n_iter <= 0:
        return {
            "n_iter": int(max(n_iter, 0)), "seed": int(seed),
            "realized_max_dd": realized, "dd_mean": None,
            "dd_p50": None, "dd_p95": None,
            "realized_dd_percentile": None, "drawdown_tail_extreme": False,
        }
    rng = random.Random(seed)
    dds: List[float] = []
    for _ in range(n_iter):
        shuffled = rs[:]
        rng.shuffle(shuffled)
        dds.append(max_drawdown(shuffled))
    dds_sorted = sorted(dds)
    dd_p95 = _percentile(dds_sorted, 95)
    realized_pct = 100.0 * sum(1 for d in dds if d <= realized) / n_iter
    if total > 0:
        dd_extreme = dd_p95 is not None and dd_p95 > 1.5 * total
    else:
        dd_extreme = True
    return {
        "n_iter": int(n_iter), "seed": int(seed),
        "realized_max_dd": realized,
        "dd_mean": sum(dds) / n_iter,
        "dd_p50": _percentile(dds_sorted, 50),
        "dd_p95": dd_p95,
        "realized_dd_percentile": realized_pct,
        "drawdown_tail_extreme": bool(dd_extreme),
    }


def bootstrap_resample(
    r_values: Sequence[float], n_iter: int = 5000, seed: int = 0
) -> Dict[str, Any]:
    """Resample trades WITH replacement (same count) and total the R each draw.

    Reports prob(total R <= 0) plus the total distribution percentiles. A high
    prob(total<=0) means the net depends on having drawn this particular set of
    trades -- the bootstrap robustness check. Fully seeded.
    """
    rs = [float(x) for x in r_values]
    n = len(rs)
    if n == 0 or n_iter <= 0:
        return {
            "n_iter": int(max(n_iter, 0)), "seed": int(seed),
            "prob_total_le_0": None, "mean_total": None,
            "p05": None, "p50": None, "p95": None,
        }
    rng = random.Random(seed)
    totals: List[float] = []
    for _ in range(n_iter):
        totals.append(sum(rs[rng.randrange(n)] for _ in range(n)))
    totals_sorted = sorted(totals)
    le0 = sum(1 for t in totals if t <= 0.0) / n_iter
    return {
        "n_iter": int(n_iter), "seed": int(seed),
        "prob_total_le_0": le0,
        "mean_total": sum(totals) / n_iter,
        "p05": _percentile(totals_sorted, 5),
        "p50": _percentile(totals_sorted, 50),
        "p95": _percentile(totals_sorted, 95),
    }


def derive_sequence_risk_verdict(summary: Dict[str, Any]) -> str:
    """Map a sequence-risk summary to one conservative verdict.

    FRAGILE if any of:
      * bootstrap prob(total<=0) >= 20%,
      * net is positive but goes <= 0 without the top 3 winners,
      * best trade is > 50% of net.
    ACCEPTABLE only if ALL of:
      * bootstrap prob(total<=0) < 10%,
      * net stays > 0 without the top 3 winners,
      * best trade <= 35% of net,
      * drawdown tail not flagged extreme.
    Otherwise INCONCLUSIVE (including empty / unmeasurable inputs).
    """
    boot = summary.get("bootstrap", {}) or {}
    tw = summary.get("top_winner", {}) or {}
    shuf = summary.get("shuffle", {}) or {}

    p_le0 = boot.get("prob_total_le_0")
    net = tw.get("net_r", 0.0)
    net_ex3 = tw.get("net_r_ex_top3", 0.0)
    share = tw.get("best_trade_share")
    net_positive = summary.get("net_positive", net > 0)
    dd_extreme = bool(shuf.get("drawdown_tail_extreme", False))

    if summary.get("n_trades") == 0 or p_le0 is None:
        return SEQUENCE_RISK_INCONCLUSIVE

    if p_le0 >= 0.20:
        return SEQUENCE_RISK_FRAGILE
    if net_positive and net_ex3 <= 0.0:
        return SEQUENCE_RISK_FRAGILE
    if share is not None and share > 0.50:
        return SEQUENCE_RISK_FRAGILE

    if (
        p_le0 < 0.10
        and net_ex3 > 0.0
        and share is not None
        and share <= 0.35
        and not dd_extreme
    ):
        return SEQUENCE_RISK_ACCEPTABLE

    return SEQUENCE_RISK_INCONCLUSIVE


def run_sequence_risk(
    r_values: Sequence[Any], n_iter: int = 5000, seed: int = 0
) -> Dict[str, Any]:
    """Run the full sequence-risk battery and return one structured summary.

    Accepts trade dicts or bare R numbers. Computes top-winner dependence,
    drawdown/streak/pain metrics, the order-shuffle drawdown distribution, and the
    bootstrap total distribution, then derives the verdict. Deterministic for a
    fixed seed.
    """
    rs = normalize_r_multiples(r_values)
    n = len(rs)
    total = sum(rs)

    summary: Dict[str, Any] = {
        "n_trades": n,
        "total_r": total,
        "net_positive": total > 0,
        "top_winner": top_winner_dependence(rs),
        "drawdown": {
            "realized_max_dd": max_drawdown(rs),
            "longest_losing_streak": longest_losing_streak(rs),
            "worst_5_trade_window": worst_window_sum(rs, 5),
        },
        "shuffle": trade_order_shuffle(rs, n_iter=n_iter, seed=seed),
        "bootstrap": bootstrap_resample(rs, n_iter=n_iter, seed=seed),
    }
    summary["verdict"] = derive_sequence_risk_verdict(summary)
    return summary


def build_sequence_risk_report(
    *,
    branch_id: str,
    title: str,
    summary: Dict[str, Any],
    verdict: Optional[str] = None,
    module_id: str = "sequence_risk",
    source_commits: Optional[Dict[str, Any]] = None,
    input_files: Optional[List[str]] = None,
    data_window: Optional[Dict[str, Any]] = None,
    frozen_parameters: Optional[Dict[str, Any]] = None,
    status: str = "COMPLETE",
    caveats: Optional[List[Any]] = None,
    next_allowed_step: str = "regime_breakdown",
    forbidden_actions: Optional[List[Any]] = None,
    notes: Optional[List[Any]] = None,
    created_utc: str = "",
) -> Dict[str, Any]:
    """Assemble a Factory-D2-schema sequence-risk report from a run summary.

    The verdict defaults to the summary's own derived verdict (or re-derives it),
    but the caller may override. n_iter / seed are frozen into frozen_parameters
    for reproducibility. Writes nothing.
    """
    v = verdict or summary.get("verdict") or derive_sequence_risk_verdict(summary)

    frozen = dict(frozen_parameters or {})
    boot = summary.get("bootstrap", {}) or {}
    frozen.setdefault("n_iter", boot.get("n_iter"))
    frozen.setdefault("seed", boot.get("seed"))

    default_forbidden = [
        "no_optimization", "no_parameter_sweeps", "no_data_fetch",
        "no_paper_or_live", "no_execution_or_api", "no_cherry_picked_ordering",
    ]
    return validation_reports.make_report(
        branch_id=branch_id,
        module_id=module_id,
        title=title,
        status=status,
        verdict=v,
        created_utc=created_utc,
        source_commits=dict(source_commits or {}),
        input_files=list(input_files or []),
        data_window=dict(data_window or {}),
        frozen_parameters=frozen,
        metrics=dict(summary),
        caveats=list(caveats or []),
        next_allowed_step=next_allowed_step,
        forbidden_actions=list(forbidden_actions or default_forbidden),
        notes=list(notes or []),
    )

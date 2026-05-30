"""Reusable friction / slippage-stress integration (Factory-D7 / ladder module J).

Stresses an already-produced R-multiple record against a ladder of per-trade
R-costs (commission + slippage modelled as a flat R deduction per trade) and finds
the break-even cost. This encodes the S26 lesson: a thin ~0.06R edge that goes
negative under a realistic per-trade cost is FRICTION_SENSITIVE, not tradable.

It computes NO strategy trades and fetches NO data. R-multiples are supplied by
the caller; this layer only subtracts costs and totals the result.

OFFLINE / INERT: Python standard library only (typing) plus the report writer. It
opens no network connection, spawns no child process, fetches no data, runs no
shell or version-control call, reads no real market data, and does NO dynamic code
loading. It mutates nothing and writes nothing.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from engine import validation_reports


# Friction dispositions.
FRICTION_ROBUST = "FRICTION_ROBUST"
FRICTION_SENSITIVE = "FRICTION_SENSITIVE"
FRICTION_FRAGILE = "FRICTION_FRAGILE"
FRICTION_FAIL = "FRICTION_FAIL"

DEFAULT_COSTS = (0.02, 0.05, 0.10, 0.20)


def apply_r_cost(
    r_values: Sequence[float], cost_per_trade_r: float
) -> List[float]:
    """Subtract a flat per-trade R cost from each trade's R-multiple."""
    c = float(cost_per_trade_r)
    return [float(r) - c for r in r_values]


def break_even_cost_per_trade(r_values: Sequence[float]) -> Optional[float]:
    """The per-trade R cost at which net R reaches zero (mean R per trade).

    Net stays positive while the real per-trade cost is below this value. Returns
    None for an empty record. May be negative when the raw record is net-negative.
    """
    rs = [float(r) for r in r_values]
    n = len(rs)
    if n == 0:
        return None
    return sum(rs) / n


def friction_scenarios(
    r_values: Sequence[float], costs: Sequence[float] = DEFAULT_COSTS
) -> Dict[str, Any]:
    """Total R / net sign at each per-trade cost level, plus the break-even cost.

    Returns the zero-cost baseline, one entry per tested cost, the break-even cost
    per trade, and the min / max tested costs (used by derive_friction_verdict).
    """
    rs = [float(r) for r in r_values]
    n = len(rs)
    baseline_total = sum(rs)

    scenarios: Dict[str, Any] = {}
    for c in costs:
        adj = apply_r_cost(rs, c)
        tot = sum(adj)
        scenarios["%g" % float(c)] = {
            "cost_per_trade_r": float(c),
            "total_r": tot,
            "trade_count": n,
            "net_positive": tot > 0,
            "avg_r": (tot / n) if n else 0.0,
        }

    return {
        "trade_count": n,
        "baseline_total_r": baseline_total,
        "baseline_net_positive": baseline_total > 0,
        "scenarios": scenarios,
        "break_even_cost_per_trade": break_even_cost_per_trade(rs),
        "min_tested_cost": (min(float(c) for c in costs) if costs else None),
        "max_tested_cost": (max(float(c) for c in costs) if costs else None),
        "costs_tested": [float(c) for c in costs],
    }


def derive_friction_verdict(summary: Dict[str, Any]) -> str:
    """Map a friction-scenario summary to one conservative robustness verdict.

    FAIL      -- no trades, or the raw record is already net <= 0 (break-even
                 cost <= 0): there is no edge to stress.
    ROBUST    -- break-even cost >= the highest tested cost (survives every level).
    FRAGILE   -- break-even cost <= the lowest tested cost (dies at the gentlest).
    SENSITIVE -- break-even cost falls between the lowest and highest tested cost.
    """
    n = summary.get("trade_count", 0)
    be = summary.get("break_even_cost_per_trade")
    lo = summary.get("min_tested_cost")
    hi = summary.get("max_tested_cost")

    if n == 0 or be is None or be <= 0.0:
        return FRICTION_FAIL
    if lo is None or hi is None:
        return FRICTION_SENSITIVE
    if be >= hi:
        return FRICTION_ROBUST
    if be <= lo:
        return FRICTION_FRAGILE
    return FRICTION_SENSITIVE


def build_friction_report(
    *,
    branch_id: str,
    title: str,
    summary: Dict[str, Any],
    verdict: Optional[str] = None,
    module_id: str = "friction_stress",
    source_commits: Optional[Dict[str, Any]] = None,
    input_files: Optional[List[str]] = None,
    data_window: Optional[Dict[str, Any]] = None,
    frozen_parameters: Optional[Dict[str, Any]] = None,
    status: str = "COMPLETE",
    caveats: Optional[List[Any]] = None,
    next_allowed_step: str = "readiness_gate",
    forbidden_actions: Optional[List[Any]] = None,
    notes: Optional[List[Any]] = None,
    created_utc: str = "",
) -> Dict[str, Any]:
    """Assemble a Factory-D2-schema friction-stress report from a summary.

    The verdict defaults to derive_friction_verdict(summary); the caller may
    override. The tested cost ladder is frozen into frozen_parameters. Writes
    nothing.
    """
    v = verdict or derive_friction_verdict(summary)
    frozen = dict(frozen_parameters or {})
    frozen.setdefault("costs_tested", summary.get("costs_tested"))

    default_forbidden = [
        "no_optimization", "no_parameter_sweeps", "no_data_fetch",
        "no_paper_or_live", "no_execution_or_api", "no_cost_cherry_picking",
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

"""continue / park / kill decision logic.

OFFLINE / INERT: pure function of a metrics dict + thresholds. No network,
no file writes, no side effects.

Mapping:
- "continue" -> the variant clears the continue bar (enough trades + PF +
  win rate + drawdown). Worth iterating params further.
- "park"     -> profitable-ish but below the continue bar. Shelve it.
- "kill"     -> below the park bar (or too few trades). Discard it.
"""

from __future__ import annotations

from typing import Dict, Any


CONTINUE = "continue"
PARK = "park"
KILL = "kill"


def default_thresholds() -> Dict[str, Any]:
    """Fallback thresholds mirroring config\\factory_config.yaml `decision:`."""
    return {
        "min_trades": 30,
        "continue": {
            "min_profit_factor": 1.30,
            "min_win_rate": 0.40,
            "max_drawdown_pct": 25.0,
        },
        "park": {
            "min_profit_factor": 1.00,
        },
    }


def decide(metrics: Dict[str, float], thresholds: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Return a decision dict: {'decision': ..., 'reasons': [...]}.

    `metrics` is the dict produced by metrics.summarize().
    """
    if thresholds is None:
        thresholds = default_thresholds()

    min_trades = thresholds.get("min_trades", 30)
    cont = thresholds.get("continue", {})
    park = thresholds.get("park", {})

    trades = metrics.get("trade_count", 0.0)
    pf = metrics.get("profit_factor", 0.0)
    wr = metrics.get("win_rate", 0.0)
    dd = metrics.get("max_drawdown_pct", 0.0)

    reasons = []

    # Not enough evidence -> kill (too few trades to trust anything).
    if trades < min_trades:
        reasons.append(f"trade_count {trades:.0f} < min_trades {min_trades}")
        return {"decision": KILL, "reasons": reasons}

    meets_continue = (
        pf >= cont.get("min_profit_factor", 1.30)
        and wr >= cont.get("min_win_rate", 0.40)
        and dd <= cont.get("max_drawdown_pct", 25.0)
    )
    if meets_continue:
        reasons.append(
            f"PF {pf:.2f} >= {cont.get('min_profit_factor')}, "
            f"win_rate {wr:.2f} >= {cont.get('min_win_rate')}, "
            f"max_dd {dd:.1f}% <= {cont.get('max_drawdown_pct')}%"
        )
        return {"decision": CONTINUE, "reasons": reasons}

    meets_park = pf >= park.get("min_profit_factor", 1.00)
    if meets_park:
        reasons.append(
            f"PF {pf:.2f} >= park bar {park.get('min_profit_factor')} "
            f"but below continue bar"
        )
        return {"decision": PARK, "reasons": reasons}

    reasons.append(f"PF {pf:.2f} below park bar {park.get('min_profit_factor')}")
    return {"decision": KILL, "reasons": reasons}

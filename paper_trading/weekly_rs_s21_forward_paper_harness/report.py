"""Weekly report generation (plan 3dd8b3c sec 5)."""

from .killswitch import check_killswitch


def build_weekly_report(week, signal_date, fill_basis, equity, weekly_return, cumulative_return,
                        rebalances_to_date, closed_this_week, cumulative_closed, turnover_names,
                        cost_this_week, cost_cumulative, annualized_cost_drag, mean_shortfall_bps,
                        holdings, drawdown_metrics, diagnostic_tracking, data_integrity_ok, killswitch_metrics):
    ks = check_killswitch(killswitch_metrics)
    verdict = "HALT" if ks["halt"] else ("WARN" if ks["status"] in ("WARN", "REVIEW") else "CONTINUE")
    return {
        "week": week, "signal_date": signal_date, "fill_basis": fill_basis,
        "equity_usd": round(equity, 2), "weekly_return_pct": round(weekly_return * 100, 4),
        "cumulative_return_pct": round(cumulative_return * 100, 4),
        "rebalances_to_date": rebalances_to_date, "closed_trades_this_week": closed_this_week,
        "cumulative_closed_trades": cumulative_closed, "turnover_names": turnover_names,
        "cost_this_week_usd": round(cost_this_week, 2), "cost_cumulative_usd": round(cost_cumulative, 2),
        "annualized_cost_drag_pct": round(annualized_cost_drag * 100, 4), "mean_shortfall_bps": round(mean_shortfall_bps, 2),
        "holdings": list(holdings), "drawdown": drawdown_metrics, "diagnostic_tracking": diagnostic_tracking,
        "data_integrity_ok": data_integrity_ok, "killswitch": ks, "verdict": verdict,
        "status_disclosure": "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE; PAUSED; BLOCKED_AT_6_GATES; FRC NEVER_GRANTED",
    }


def render_markdown(r):
    return (
        "# Weekly paper report -- week %s (%s)\n\n" % (r["week"], r["signal_date"]) +
        "- equity: $%s | weekly: %s%% | cumulative: %s%%\n" % (r["equity_usd"], r["weekly_return_pct"], r["cumulative_return_pct"]) +
        "- rebalances: %s | closed this wk: %s | cumulative closed: %s\n" % (r["rebalances_to_date"], r["closed_trades_this_week"], r["cumulative_closed_trades"]) +
        "- cost this wk: $%s | cumulative: $%s | ann cost-drag: %s%% | shortfall: %s bps\n" % (r["cost_this_week_usd"], r["cost_cumulative_usd"], r["annualized_cost_drag_pct"], r["mean_shortfall_bps"]) +
        "- drawdown: %s | holdings: %s\n" % (r["drawdown"], r["holdings"]) +
        "- killswitch: %s %s | **verdict: %s**\n" % (r["killswitch"]["status"], r["killswitch"]["reasons"], r["verdict"]) +
        "- %s\n" % r["status_disclosure"]
    )

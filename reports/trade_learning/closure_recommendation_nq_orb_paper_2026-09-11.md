# Closure recommendation -- nq_orb_paper -- 2026-09-11

**READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER**

Status: **REJECTED**
Sign: NEGATIVE
Window: {"end_or_min_n": {"fired_trades": 40, "trading_days": 60}, "kind": "trading_days_AND_fired_trades", "satisfied": true}
Sample: {"n_days": 80, "n_trades": 52}
Launched: 2026-05-13 · days elapsed 121
Criteria file: `obsidian-trade-logger/reports/nq_phase12_paper_plan.md (section 5 graduation criteria; section 4 alert thresholds; nq_paper_tracker/alerts.py)`

## Why the window resolved

own window satisfied (80/60 days, 52/40 trades); sign NEGATIVE; hard gate FAIL: c3_realized_pnl_positive

## Own gates at resolution

| own gate | threshold | value | status | hard |
|---|---|---|---|---|
| c1_trading_days | >= 60 | 80 | PASS | yes |
| c2_fired_trades | >= 40 | 52 | PASS | yes |
| c3_realized_pnl_positive | > 0 after locked costs | -2,172.5 | FAIL | yes |
| c4_max_drawdown_within_15pct | > -15% for the entire window | -0.0693 | PASS | yes |
| c5_worst_day_within_5pct | > -5% of initial capital | -0.0095 | PASS | yes |
| c6_long_and_short_min_each | >= 10 long AND >= 10 short | L19/S33 | PASS | yes |
| c7_no_unresolved_critical_alerts | == 0 | 0 | PASS | yes |
| c8_explicit_human_go_live_sign_off | written go-live note | - | MANUAL | yes |

## Recommendation (observation only)

The pre-registered window for nq_orb_paper resolved without meeting its own criteria (own window satisfied (80/60 days, 52/40 trades); sign NEGATIVE; hard gate FAIL: c3_realized_pnl_positive). Record the window read as resolved-negative in the trading decision record; the operator chooses between continue-tracking (with this read logged) or restart with a new fixed launch date. No mid-window strategy edit, no re-tuning, no rescue. own plan: 'If any mandatory criterion is unmet, paper tracking either continues or is restarted -- live capital is NOT considered.' Observation only: no rule change, no strategy approval, no live-readiness claim.

## Headline metrics

```json
{
 "active_alert_codes": [],
 "initial_capital_usd": 50000.0,
 "instrument": "MNQ",
 "max_drawdown_pct": -0.069346,
 "n_long": 19,
 "n_short": 33,
 "n_skipped_size_zero": 25,
 "n_trades_fired": 52,
 "net_pnl_usd": -2172.5,
 "paper_equity_usd": 47827.5,
 "report_age_days": 1,
 "report_date": "2026-09-10",
 "spec_hash_match": true,
 "stale_hours": 28.1,
 "strategy_label": "MNQ_risk_$500",
 "total_costs_usd": 167.5,
 "tracker_status": "ON-TRACK",
 "worst_day_pct": -0.0095
}
```

Source files (read-only):
- `C:\Users\mahmo\obsidian-trade-logger\reports\nq_paper_orb\equity_curve.csv`
- `C:\Users\mahmo\obsidian-trade-logger\reports\nq_paper_orb\latest.json`
- `C:\Users\mahmo\obsidian-trade-logger\reports\nq_paper_orb\latest.md`
- `C:\Users\mahmo\obsidian-trade-logger\reports\nq_paper_orb\trades.csv`

---
This file is written once when the line's own window first resolves and is never rewritten. It changes no rule, sends no order, and grants nothing.
READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

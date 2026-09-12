# Closure recommendation -- funding_carry_paper -- 2026-09-12

**READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER**

Status: **REJECTED**
Sign: POSITIVE
Window: {"end_or_min_n": 90, "kind": "calendar_days_since_launch", "satisfied": true}
Sample: {"n_days": 122, "n_position_changes": 5}
Launched: 2026-05-13 · days elapsed 122
Criteria file: `obsidian-trade-logger/reports/funding_carry_phase7_paper_plan.md (section 7 alerts, section 8 graduation criteria)`

## Why the window resolved

own window satisfied (122/90 days); hard gate FAIL: g2_realized_cagr_within_30pct_of_phase6b_same_period

## Own gates at resolution

| own gate | threshold | value | status | hard |
|---|---|---|---|---|
| g1_90d_without_non_outage_critical | >= 90 days and 0 non-outage CRITICAL | 0 | PASS | yes |
| g2_realized_cagr_within_30pct_of_phase6b_same_period | +/- 30% of same-period estimate 0.02296 (band 0.01607..0.02985) | 0.0153 | FAIL | yes |
| g3_max_dd_vs_phase6b_worst_oos | >= -0.0267 (3x of -0.89%) | -0.0017 | PASS | yes |
| g4_phase8_basis_aware_completed_and_reviewed | report present and reviewed by a human | True | MANUAL | yes |
| g5_explicit_human_sign_off | written go-live note | - | MANUAL | yes |

## Recommendation (observation only)

The pre-registered window for funding_carry_paper resolved without meeting its own criteria (own window satisfied (122/90 days); hard gate FAIL: g2_realized_cagr_within_30pct_of_phase6b_same_period). Record the window read as resolved-negative in the trading decision record; the operator chooses between continue-tracking (with this read logged) or restart with a new fixed launch date. No mid-window strategy edit, no re-tuning, no rescue. plan section 8: 'If any of these is unmet, paper tracking continues without going live.' Observation only: no rule change, no strategy approval, no live-readiness claim.

## Headline metrics

```json
{
 "active_alert_codes": [],
 "basis_pnl_total_usd": 0.41,
 "cost_consumption_pct": 0.355,
 "final_equity_usd": 10051.02,
 "funding_pnl_total_usd": 98.97,
 "initial_capital_usd": 10000.0,
 "max_drawdown_pct": -0.001697,
 "n_position_changes": 5,
 "net_pnl_usd": 51.02,
 "phase6b_full_sample_oos_cagr_pct_reference_only": 8.08,
 "realized_annualized_return": 0.01534,
 "report_age_days": 0,
 "report_date": "2026-09-12",
 "stale_hours": 0.0,
 "strategy_label": "always_on_monthly",
 "total_simulated_costs_usd": 48.36,
 "tracker_status": "ON-TRACK"
}
```

Source files (read-only):
- `C:\Users\mahmo\obsidian-trade-logger\reports\paper_funding_carry\alerts.csv`
- `C:\Users\mahmo\obsidian-trade-logger\reports\paper_funding_carry\g2_same_period_estimate_20260912T162609Z.json`
- `C:\Users\mahmo\obsidian-trade-logger\reports\paper_funding_carry\latest.json`

---
This file is written once when the line's own window first resolves and is never rewritten. It changes no rule, sends no order, and grants nothing.
READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

# Paper systems scorecard -- 2026-10-05

**READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER**

Each line is scored against ITS OWN pre-registered window and gates (cited per line). Status vocabulary: SHADOW / CONFIRMED / REJECTED / BLOCKED / NO_DATA. A CONFIRMED or REJECTED read closes a paper window and nothing else. Observation only: no rule change, no strategy approval, no live-readiness claim.

| line | status | sign | window | sample | reason |
|---|---|---|---|---|---|
| funding_carry_paper | **REJECTED** | NONE | closed_by_operator satisfied | {} | closed by recorded operator decision (funding_carry_closure_decision_20260919.json): REJECTED_CLOSED (2026-09-19) |
| nq_orb_paper | **REJECTED** | NONE | closed_by_operator satisfied | {} | closed by recorded operator decision (CLOSURE_DECISION_2026-09-11.md): Decision (operator, 2026-09-11, recorded via SPARTA): CLOSED — REJECTED_BY_OWN_GRADUATION_CRITERIA. |
| gc_ict_paper | **SHADOW** | POSITIVE | trading_days_AND_fired_trades open | {"n_days": 80, "n_trades": 3} | own window not yet satisfied (80/60 days, 3/40 trades); thin line: own rules doc expects ~2 years to reach 40 fired trades |
| frozen_stack_paper_forward | **SHADOW** | NEGATIVE | forward_clean_paper_run_days open | {"n_backfill_rows_excluded": 257, "n_days": 23, "n_trades": 4} | own window not yet satisfied (4 out-of-sample executed rows after the 2026-03-31 data ceiling (188-day span), 23 days of clean forward running since 2026-09-12) |
| s21_weekly_rs_paper | **REJECTED** | NONE | closed_by_operator satisfied | {} | closed by recorded operator decision (S21_REPLAYED_OOS_DIAGNOSTIC_20260919.json): CLOSED_FAILED_OWN_DRAWDOWN_GATE (2026-09-19) |

## funding_carry_paper -- REJECTED

- Criteria file: `obsidian-trade-logger/reports/funding_carry_phase7_paper_plan.md (section 7 alerts, section 8 graduation criteria)`
- Launched: - · as_of 2026-10-05 · days elapsed -
- Window: {"end_or_min_n": null, "kind": "closed_by_operator", "satisfied": true}
- Sign: NONE · sample {}
- Reason: closed by recorded operator decision (funding_carry_closure_decision_20260919.json): REJECTED_CLOSED (2026-09-19)
- Recommendation: Closed on record. No further action; the line is not re-scored.

(no own gates evaluated)

Headline metrics:

```json
{}
```

Source files (read-only):
- `C:\SPARTA_BRAIN\reports\approvals\funding_carry_closure_decision_20260919.json`
- `C:\Users\mahmo\obsidian-trade-logger\reports\paper_funding_carry\alerts.csv`
- `C:\Users\mahmo\obsidian-trade-logger\reports\paper_funding_carry\g2_same_period_estimate_20260912T162609Z.json`
- `C:\Users\mahmo\obsidian-trade-logger\reports\paper_funding_carry\latest.json`

## nq_orb_paper -- REJECTED

- Criteria file: `obsidian-trade-logger/reports/nq_phase12_paper_plan.md (section 5 graduation criteria; section 4 alert thresholds; nq_paper_tracker/alerts.py)`
- Launched: - · as_of 2026-10-05 · days elapsed -
- Window: {"end_or_min_n": null, "kind": "closed_by_operator", "satisfied": true}
- Sign: NONE · sample {}
- Reason: closed by recorded operator decision (CLOSURE_DECISION_2026-09-11.md): Decision (operator, 2026-09-11, recorded via SPARTA): CLOSED — REJECTED_BY_OWN_GRADUATION_CRITERIA.
- Recommendation: Closed on record. No further action; the line is not re-scored.

(no own gates evaluated)

Headline metrics:

```json
{}
```

Source files (read-only):
- `C:\Users\mahmo\obsidian-trade-logger\reports\nq_paper_orb\CLOSURE_DECISION_2026-09-11.md`
- `C:\Users\mahmo\obsidian-trade-logger\reports\nq_paper_orb\equity_curve.csv`
- `C:\Users\mahmo\obsidian-trade-logger\reports\nq_paper_orb\latest.json`
- `C:\Users\mahmo\obsidian-trade-logger\reports\nq_paper_orb\latest.md`
- `C:\Users\mahmo\obsidian-trade-logger\reports\nq_paper_orb\trades.csv`

## gc_ict_paper -- SHADOW

- Criteria file: `obsidian-trade-logger/reports/observation_mode/gc_ict_observation_rules.md (review milestones + graduation criteria; gc_paper_tracker/spec.py LAUNCH_DATE)`
- Launched: 2026-06-14 · as_of 2026-10-05 · days elapsed 113
- Window: {"end_or_min_n": {"fired_trades": 40, "trading_days": 60}, "kind": "trading_days_AND_fired_trades", "satisfied": false}
- Sign: POSITIVE · sample {"n_days": 80, "n_trades": 3}
- Reason: own window not yet satisfied (80/60 days, 3/40 trades); thin line: own rules doc expects ~2 years to reach 40 fired trades
- Recommendation: gc_ict_paper stays in SHADOW (own window not yet satisfied (80/60 days, 3/40 trades); thin line: own rules doc expects ~2 years to reach 40 fired trades). Keep tracking; nothing to act on. own plan: 'If any mandatory criterion is unmet, paper tracking either continues or is restarted -- live capital is NOT considered.' Observation only: no rule change, no strategy approval, no live-readiness claim.

| own gate | threshold | value | status | hard | note |
|---|---|---|---|---|---|
| c1_trading_days | >= 60 | 80 | PASS | yes |  |
| c2_fired_trades | >= 40 | 3 | PENDING | yes |  |
| c3_realized_pnl_positive | > 0 after locked costs | 2,272.92 | PASS | yes |  |
| c4_max_drawdown_within_15pct | > -15% for the entire window | -0.009 | PASS | yes |  |
| c5_worst_day_within_5pct | > -5% of initial capital | -0.009 | PASS | yes |  |
| c6_long_and_short_min_each | >= 10 long AND >= 10 short | L2/S1 | PENDING | yes |  |
| c7_no_unresolved_critical_alerts | == 0 | 0 | PASS | yes |  |
| c8_explicit_human_go_live_sign_off | written go-live note | - | MANUAL | yes | outside any automated read |

Headline metrics:

```json
{
 "active_alert_codes": [],
 "avg_r": 1.67,
 "initial_capital_usd": 50000.0,
 "instrument": "MGC",
 "max_drawdown_pct": -0.009015,
 "n_long": 2,
 "n_short": 1,
 "n_trades_fired": 3,
 "net_pnl_usd": 2272.92,
 "paper_equity_usd": 52272.92,
 "report_age_days": 1,
 "report_date": "2026-10-04",
 "spec_hash_match": true,
 "stale_hours": 48.0,
 "strategy_label": "GC_ICT_withtrend_$500",
 "total_costs_usd": 148.5,
 "tracker_status": "ON-TRACK",
 "win_rate": 66.7,
 "worst_day_pct": -0.009015
}
```

Source files (read-only):
- `C:\Users\mahmo\obsidian-trade-logger\reports\gc_paper_ict\alerts.csv`
- `C:\Users\mahmo\obsidian-trade-logger\reports\gc_paper_ict\latest.json`
- `C:\Users\mahmo\obsidian-trade-logger\reports\gc_paper_ict\latest.md`

## frozen_stack_paper_forward -- SHADOW

- Criteria file: `obsidian-trade-logger/reports/final_frozen_architecture.md (section 8 alert table, section 9 checklist '60-90 day clean paper run') + analytics/final_stack_operational_validation.py (BURN_IN_DAYS=30, ALERT_DD_ENVELOPE_BREACH_PCT=-10, ALERT_D4_REPRODUCIBILITY_PCT=90)`
- Launched: 2026-03-31 · as_of 2026-10-05 · days elapsed 23
- Window: {"end_or_min_n": "60-90 days (conservative 90) from 2026-03-31", "kind": "forward_clean_paper_run_days", "satisfied": false}
- Sign: NEGATIVE · sample {"n_backfill_rows_excluded": 257, "n_days": 23, "n_trades": 4}
- Reason: own window not yet satisfied (4 out-of-sample executed rows after the 2026-03-31 data ceiling (188-day span), 23 days of clean forward running since 2026-09-12)
- Recommendation: frozen_stack_paper_forward stays in SHADOW (own window not yet satisfied (4 out-of-sample executed rows after the 2026-03-31 data ceiling (188-day span), 23 days of clean forward running since 2026-09-12)). Keep tracking; nothing to act on. own doc section 9: forward paper evidence accrues; nothing is tuned Observation only: no rule change, no strategy approval, no live-readiness claim.

| own gate | threshold | value | status | hard | note |
|---|---|---|---|---|---|
| f1_clean_paper_run_days | 60-90 days (section 9 states a range; 90 used as the conservative read) | 23 | PENDING | yes | days of clean forward RUNNING since 2026-09-12; the 188-day span back to the 2026-03-31 data ceiling is out-of-sample evidence, not run time; burn-in 30 days suppresses alerts before that |
| f2_paper_equity_dd_within_envelope | > -10.0% | - | NOT_EVALUABLE | yes | trades CSV carries net_r only; equity-% drawdown comes from the operational validator, which reads full history (backfill included), not forward-only |
| f3_d4_reproducibility | >= 90.0% | 100 | PASS | yes | validator read over full history (not forward-only); shown as the line's own gate value |
| f4_rolling_90d_avg_r_non_negative | >= 0 with n >= 5 (warning-level in own table) | -0.3469 | PENDING | no | forward executed rows only |

Headline metrics:

```json
{
 "appended_rows_last_run": 0,
 "backfill_not_scored": {
  "by_engine": {
   "baseline_breakout": {
    "n": 62,
    "sum_net_r": 39.6983
   },
   "skipped_by_d4": {
    "n": 125,
    "sum_net_r": 0.0
   },
   "v2_bb_snapback": {
    "n": 70,
    "sum_net_r": 36.7649
   }
  },
  "last_entry_time": "2026-02-06",
  "n_rows": 257
 },
 "candidate_rows_last_run": 275,
 "forward_by_engine": {
  "baseline_breakout": {
   "n": 2,
   "sum_net_r": 0.6123
  },
  "skipped_by_d4": {
   "n": 14,
   "sum_net_r": 0.0
  },
  "v2_bb_snapback": {
   "n": 2,
   "sum_net_r": -2.0
  }
 },
 "forward_n_executed": 4,
 "forward_n_skipped_by_d4": 14,
 "forward_split": "2026-03-31",
 "forward_sum_net_r": -1.3877,
 "stack_label": "Donchian-ATR-3.0x + V2-BB-snapback-0.5x + D4-90d-pause",
 "state_age_days": 1,
 "state_generated_at": "2026-10-04T11:30:20.182132+00:00",
 "state_status": "OK",
 "validator_d4_agreement_pct": 100.0,
 "validator_global_verdict": "DRIFT_WARNING"
}
```

Source files (read-only):
- `C:\Users\mahmo\obsidian-trade-logger\data\final_stack_paper_state.json`
- `C:\Users\mahmo\obsidian-trade-logger\data\final_stack_paper_trades.csv`
- `C:\Users\mahmo\obsidian-trade-logger\reports\final_stack_operational_validation.json`

## s21_weekly_rs_paper -- REJECTED

- Criteria file: `paper_trading/weekly_rs_s21_forward_paper_harness/manifest.py (gate_thresholds) + OPERATIONS_CHECKLIST.md section 8 (12-week >= 15 closed, 24-week >= 35 closed) + cycle_runner.evaluate_gates`
- Launched: - · as_of 2026-10-05 · days elapsed -
- Window: {"end_or_min_n": null, "kind": "closed_by_operator", "satisfied": true}
- Sign: NONE · sample {}
- Reason: closed by recorded operator decision (S21_REPLAYED_OOS_DIAGNOSTIC_20260919.json): CLOSED_FAILED_OWN_DRAWDOWN_GATE (2026-09-19)
- Recommendation: Closed on record. No further action; the line is not re-scored.

(no own gates evaluated)

Headline metrics:

```json
{}
```

Source files (read-only):
- `C:\SPARTA_BRAIN\paper_trading\weekly_rs_s21_forward_paper_harness\manifest.py`
- `C:\SPARTA_BRAIN\reports\s21_weekly_rs_paper\S21_REPLAYED_OOS_DIAGNOSTIC_20260919.json`

---
READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

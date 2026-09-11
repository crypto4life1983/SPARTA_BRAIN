# Paper systems scorecard -- 2026-09-11

**READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER**

Each line is scored against ITS OWN pre-registered window and gates (cited per line). Status vocabulary: SHADOW / CONFIRMED / REJECTED / BLOCKED / NO_DATA. A CONFIRMED or REJECTED read closes a paper window and nothing else. Observation only: no rule change, no strategy approval, no live-readiness claim.

| line | status | sign | window | sample | reason |
|---|---|---|---|---|---|
| funding_carry_paper | **SHADOW** | POSITIVE | calendar_days_since_launch satisfied | {"n_days": 121, "n_position_changes": 5} | own window satisfied (121/90 days); unresolved own gates: g2_realized_cagr_within_30pct_of_phase6b_same_period=NOT_EVALUABLE |
| nq_orb_paper | **REJECTED** | NEGATIVE | trading_days_AND_fired_trades satisfied | {"n_days": 80, "n_trades": 52} | own window satisfied (80/60 days, 52/40 trades); sign NEGATIVE; hard gate FAIL: c3_realized_pnl_positive |
| gc_ict_paper | **SHADOW** | NEGATIVE | trading_days_AND_fired_trades open | {"n_days": 63, "n_trades": 1} | own window not yet satisfied (63/60 days, 1/40 trades); thin line: own rules doc expects ~2 years to reach 40 fired trades |
| frozen_stack_paper_forward | **SHADOW** | NONE | forward_clean_paper_run_days open | {"n_backfill_rows_excluded": 257, "n_days": 0, "n_trades": 0} | 0 forward rows with entry_time > 2026-09-11 (forward window not started; 257 backfill rows excluded from scoring) |
| s21_weekly_rs_paper | **NO_DATA** | NONE | weeks_AND_closed_trades open | {"n_trades": 0} | no harness_state.json under runs/cycles_v2/ (C:\SPARTA_BRAIN\paper_trading\weekly_rs_s21_forward_paper_harness\runs\cycles_v2\harness_state.json); legacy runs/dry_cycle_001/002 are NOT valid evidence (brain_memory/projects/trading_bot/lessons.md LESSON_S21_PAPER_001/002); manifest paper_state=HARNESS_BUILT_NOT_YET_RUN |

## funding_carry_paper -- SHADOW

- Criteria file: `obsidian-trade-logger/reports/funding_carry_phase7_paper_plan.md (section 7 alerts, section 8 graduation criteria)`
- Launched: 2026-05-13 · as_of 2026-09-11 · days elapsed 121
- Window: {"end_or_min_n": 90, "kind": "calendar_days_since_launch", "satisfied": true}
- Sign: POSITIVE · sample {"n_days": 121, "n_position_changes": 5}
- Reason: own window satisfied (121/90 days); unresolved own gates: g2_realized_cagr_within_30pct_of_phase6b_same_period=NOT_EVALUABLE
- Recommendation: funding_carry_paper stays in SHADOW (own window satisfied (121/90 days); unresolved own gates: g2_realized_cagr_within_30pct_of_phase6b_same_period=NOT_EVALUABLE). Keep tracking; nothing to act on. plan section 8: 'If any of these is unmet, paper tracking continues without going live.' Observation only: no rule change, no strategy approval, no live-readiness claim.

| own gate | threshold | value | status | hard | note |
|---|---|---|---|---|---|
| g1_90d_without_non_outage_critical | >= 90 days and 0 non-outage CRITICAL | 0 | PASS | yes | counted CRITICAL rows in alerts.csv since launch, excluding DATA_STALE*/DATA_MISSING* outage codes |
| g2_realized_cagr_within_30pct_of_phase6b_same_period | +/- 30% of same-period Phase-6B estimate | 0.0151 | NOT_EVALUABLE | yes | the tracker does not emit a same-period Phase-6B simulator estimate; the full-sample Phase-6B OOS CAGR (+8.08%) is shown in headline_metrics for reference only and is NOT the plan's gate quantity |
| g3_max_dd_vs_phase6b_worst_oos | >= -0.0267 (3x of -0.89%) | -0.0017 | PASS | yes |  |
| g4_phase8_basis_aware_completed_and_reviewed | report present and reviewed by a human | True | MANUAL | yes | reviewed-by-human is not machine-readable |
| g5_explicit_human_sign_off | written go-live note | - | MANUAL | yes | outside any automated read |

Headline metrics:

```json
{
 "active_alert_codes": [],
 "basis_pnl_total_usd": 0.18,
 "cost_consumption_pct": 0.3577,
 "final_equity_usd": 10049.78,
 "funding_pnl_total_usd": 97.96,
 "initial_capital_usd": 10000.0,
 "max_drawdown_pct": -0.001697,
 "n_position_changes": 5,
 "net_pnl_usd": 49.78,
 "phase6b_full_sample_oos_cagr_pct_reference_only": 8.08,
 "realized_annualized_return": 0.01509,
 "report_age_days": 0,
 "report_date": "2026-09-11",
 "stale_hours": 0.0,
 "strategy_label": "always_on_monthly",
 "total_simulated_costs_usd": 48.36,
 "tracker_status": "ON-TRACK"
}
```

Source files (read-only):
- `C:\Users\mahmo\obsidian-trade-logger\reports\paper_funding_carry\alerts.csv`
- `C:\Users\mahmo\obsidian-trade-logger\reports\paper_funding_carry\latest.json`

## nq_orb_paper -- REJECTED

- Criteria file: `obsidian-trade-logger/reports/nq_phase12_paper_plan.md (section 5 graduation criteria; section 4 alert thresholds; nq_paper_tracker/alerts.py)`
- Launched: 2026-05-13 · as_of 2026-09-11 · days elapsed 121
- Window: {"end_or_min_n": {"fired_trades": 40, "trading_days": 60}, "kind": "trading_days_AND_fired_trades", "satisfied": true}
- Sign: NEGATIVE · sample {"n_days": 80, "n_trades": 52}
- Reason: own window satisfied (80/60 days, 52/40 trades); sign NEGATIVE; hard gate FAIL: c3_realized_pnl_positive
- Recommendation: The pre-registered window for nq_orb_paper resolved without meeting its own criteria (own window satisfied (80/60 days, 52/40 trades); sign NEGATIVE; hard gate FAIL: c3_realized_pnl_positive). Record the window read as resolved-negative in the trading decision record; the operator chooses between continue-tracking (with this read logged) or restart with a new fixed launch date. No mid-window strategy edit, no re-tuning, no rescue. own plan: 'If any mandatory criterion is unmet, paper tracking either continues or is restarted -- live capital is NOT considered.' Observation only: no rule change, no strategy approval, no live-readiness claim.

| own gate | threshold | value | status | hard | note |
|---|---|---|---|---|---|
| c1_trading_days | >= 60 | 80 | PASS | yes |  |
| c2_fired_trades | >= 40 | 52 | PASS | yes |  |
| c3_realized_pnl_positive | > 0 after locked costs | -2,172.5 | FAIL | yes |  |
| c4_max_drawdown_within_15pct | > -15% for the entire window | -0.0693 | PASS | yes |  |
| c5_worst_day_within_5pct | > -5% of initial capital | -0.0095 | PASS | yes |  |
| c6_long_and_short_min_each | >= 10 long AND >= 10 short | L19/S33 | PASS | yes |  |
| c7_no_unresolved_critical_alerts | == 0 | 0 | PASS | yes |  |
| c8_explicit_human_go_live_sign_off | written go-live note | - | MANUAL | yes | outside any automated read |

Headline metrics:

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

## gc_ict_paper -- SHADOW

- Criteria file: `obsidian-trade-logger/reports/observation_mode/gc_ict_observation_rules.md (review milestones + graduation criteria; gc_paper_tracker/spec.py LAUNCH_DATE)`
- Launched: 2026-06-14 · as_of 2026-09-11 · days elapsed 89
- Window: {"end_or_min_n": {"fired_trades": 40, "trading_days": 60}, "kind": "trading_days_AND_fired_trades", "satisfied": false}
- Sign: NEGATIVE · sample {"n_days": 63, "n_trades": 1}
- Reason: own window not yet satisfied (63/60 days, 1/40 trades); thin line: own rules doc expects ~2 years to reach 40 fired trades
- Recommendation: gc_ict_paper stays in SHADOW (own window not yet satisfied (63/60 days, 1/40 trades); thin line: own rules doc expects ~2 years to reach 40 fired trades). Keep tracking; nothing to act on. own plan: 'If any mandatory criterion is unmet, paper tracking either continues or is restarted -- live capital is NOT considered.' Observation only: no rule change, no strategy approval, no live-readiness claim.

| own gate | threshold | value | status | hard | note |
|---|---|---|---|---|---|
| c1_trading_days | >= 60 | 63 | PASS | yes |  |
| c2_fired_trades | >= 40 | 1 | PENDING | yes |  |
| c3_realized_pnl_positive | > 0 after locked costs | -450.77 | PENDING | yes |  |
| c4_max_drawdown_within_15pct | > -15% for the entire window | 0 | PASS | yes |  |
| c5_worst_day_within_5pct | > -5% of initial capital | -0.009 | PASS | yes |  |
| c6_long_and_short_min_each | >= 10 long AND >= 10 short | L1/S0 | PENDING | yes |  |
| c7_no_unresolved_critical_alerts | == 0 | 0 | PASS | yes |  |
| c8_explicit_human_go_live_sign_off | written go-live note | - | MANUAL | yes | outside any automated read |

Headline metrics:

```json
{
 "active_alert_codes": [],
 "avg_r": -1.0,
 "initial_capital_usd": 50000.0,
 "instrument": "MGC",
 "max_drawdown_pct": 0.0,
 "n_long": 1,
 "n_short": 0,
 "n_trades_fired": 1,
 "net_pnl_usd": -450.77,
 "paper_equity_usd": 49549.23,
 "report_age_days": 1,
 "report_date": "2026-09-10",
 "spec_hash_match": true,
 "stale_hours": 24.0,
 "strategy_label": "GC_ICT_withtrend_$500",
 "total_costs_usd": 22.0,
 "tracker_status": "ON-TRACK",
 "win_rate": 0.0,
 "worst_day_pct": -0.009015
}
```

Source files (read-only):
- `C:\Users\mahmo\obsidian-trade-logger\reports\gc_paper_ict\alerts.csv`
- `C:\Users\mahmo\obsidian-trade-logger\reports\gc_paper_ict\latest.json`
- `C:\Users\mahmo\obsidian-trade-logger\reports\gc_paper_ict\latest.md`

## frozen_stack_paper_forward -- SHADOW

- Criteria file: `obsidian-trade-logger/reports/final_frozen_architecture.md (section 8 alert table, section 9 checklist '60-90 day clean paper run') + analytics/final_stack_operational_validation.py (BURN_IN_DAYS=30, ALERT_DD_ENVELOPE_BREACH_PCT=-10, ALERT_D4_REPRODUCIBILITY_PCT=90)`
- Launched: 2026-09-11 · as_of 2026-09-11 · days elapsed 0
- Window: {"end_or_min_n": "60-90 days (conservative 90) from 2026-09-11", "kind": "forward_clean_paper_run_days", "satisfied": false}
- Sign: NONE · sample {"n_backfill_rows_excluded": 257, "n_days": 0, "n_trades": 0}
- Reason: 0 forward rows with entry_time > 2026-09-11 (forward window not started; 257 backfill rows excluded from scoring)
- Recommendation: frozen_stack_paper_forward stays in SHADOW (0 forward rows with entry_time > 2026-09-11 (forward window not started; 257 backfill rows excluded from scoring)). Keep tracking; nothing to act on. own doc section 9: forward paper evidence accrues; nothing is tuned Observation only: no rule change, no strategy approval, no live-readiness claim.

| own gate | threshold | value | status | hard | note |
|---|---|---|---|---|---|
| f1_clean_paper_run_days | 60-90 days (section 9 states a range; 90 used as the conservative read) | 0 | PENDING | yes | counted from the forward split date; burn-in 30 days suppresses alerts before that |
| f2_paper_equity_dd_within_envelope | > -10.0% | - | NOT_EVALUABLE | yes | trades CSV carries net_r only; equity-% drawdown comes from the operational validator, which reads full history (backfill included), not forward-only |
| f3_d4_reproducibility | >= 90.0% | 100 | PASS | yes | validator read over full history (not forward-only); shown as the line's own gate value |
| f4_rolling_90d_avg_r_non_negative | >= 0 with n >= 5 (warning-level in own table) | - | PENDING | no | forward executed rows only |

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
 "candidate_rows_last_run": 257,
 "forward_by_engine": {},
 "forward_n_executed": 0,
 "forward_n_skipped_by_d4": 0,
 "forward_split": "2026-09-11",
 "forward_sum_net_r": 0,
 "stack_label": "Donchian-ATR-3.0x + V2-BB-snapback-0.5x + D4-90d-pause",
 "state_age_days": 0,
 "state_generated_at": "2026-09-11T11:30:16.695627+00:00",
 "state_status": "OK",
 "validator_d4_agreement_pct": 100.0,
 "validator_global_verdict": "DRIFT_WARNING"
}
```

Source files (read-only):
- `C:\Users\mahmo\obsidian-trade-logger\data\final_stack_paper_state.json`
- `C:\Users\mahmo\obsidian-trade-logger\data\final_stack_paper_trades.csv`
- `C:\Users\mahmo\obsidian-trade-logger\reports\final_stack_operational_validation.json`

## s21_weekly_rs_paper -- NO_DATA

- Criteria file: `paper_trading/weekly_rs_s21_forward_paper_harness/manifest.py (gate_thresholds) + OPERATIONS_CHECKLIST.md section 8 (12-week >= 15 closed, 24-week >= 35 closed) + cycle_runner.evaluate_gates`
- Launched: - · as_of 2026-09-11 · days elapsed -
- Window: {"end_or_min_n": {"12wk": {"min_closed_trades": 15, "weeks": 12}, "24wk": {"min_closed_trades": 35, "weeks": 24}}, "kind": "weeks_AND_closed_trades", "satisfied": false}
- Sign: NONE · sample {"n_trades": 0}
- Reason: no harness_state.json under runs/cycles_v2/ (C:\SPARTA_BRAIN\paper_trading\weekly_rs_s21_forward_paper_harness\runs\cycles_v2\harness_state.json); legacy runs/dry_cycle_001/002 are NOT valid evidence (brain_memory/projects/trading_bot/lessons.md LESSON_S21_PAPER_001/002); manifest paper_state=HARNESS_BUILT_NOT_YET_RUN
- Recommendation: Observation only: no rule change, no strategy approval, no live-readiness claim.

(no own gates evaluated)

Headline metrics:

```json
{
 "manifest_status": {
  "frc_status": "NEVER_GRANTED",
  "live_status": "BLOCKED_AT_6_GATES",
  "paper_state": "HARNESS_BUILT_NOT_YET_RUN",
  "research_label": "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE",
  "s21_remains_diagnostic_only_until_paper_gates_pass": true,
  "trading_status": "PAUSED"
 }
}
```

Source files (read-only):
- `C:\SPARTA_BRAIN\paper_trading\weekly_rs_s21_forward_paper_harness\manifest.py`

---
READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

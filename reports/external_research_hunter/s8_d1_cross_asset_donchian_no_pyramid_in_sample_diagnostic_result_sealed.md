# s8-D1 No-Pyramid - P6 In-Sample Diagnostic Result (SEALED, cost_tier=S1)

**Schema id:** `sparta.external_research_hunter.s8_d1_cross_asset_donchian_no_pyramid_in_sample_diagnostic.v1`
**Phase:** `P6_IN_SAMPLE_RUN_COMPLETE_SEALED`
**Candidate operational status:** `AWAITING_P7_DECISION_MEMO_THEN_P8`
**Report date UTC:** 2026-05-26T00:02:30Z

**Diagnostic seal:** `07a3fa91509f2206ba15ac8a21cd326b7ea85bae8191cbd4747fa1ed50a88f00`
**Predecessor (smoke pass) seal:** `1ab57a67f1a81be57a0f084f8fb4c6bc1fcc72de750839728a2787dcc5d0d361`
**Driver byte sha at run:** `129411e90fba23ff...` (matches BUILD-recorded: True)

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S8_D1_P6_IN_SAMPLE_RESULT_SEALED, SINGLE_DELTA_FROM_S7_D1_MAX_UNITS_1, NO_S7_D1_REVIVAL
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted

---

## Run metadata

- Cost tier: **S1**
- Duration: **240.6s** wall
- In-sample window: 2013-01-01 -> 2022-12-30 UTC
- Cache: 480 files, 129,789,451 bytes (s7-D1 P5 cache re-used)
- CONFIG max_units_per_market: **1**
- CONFIG filter: **NONE** (AMB6 locked)

## Performance metrics (portfolio)

- **closed_trades_portfolio:** 111
- **net_pnl_usd:** $193,482.91
- **win_rate_pct:** 39.6396%
- **sharpe_proxy_per_trade:** 0.224998
- **expectancy_per_trade_usd:** $1,743.09
- **pl_ratio:** 3.3222650201355326
- **win_rate_gap_to_breakeven_pp:** 16.50362194194087
- **trade_curve_maxdd_pct:** -23.8341%
- **trade_curve_maxdd_usd:** $-23,834.11
- **starting_cash:** $100,000
- **final_equity:** $293,482.91

## Per-market breakdown

| Market | trades | net_pnl_usd | win_rate_pct |
|---|---|---|---|
| NQ | 18 | $30,110.81 | 44.4444% |
| GC | 28 | $16,300.35 | 35.7143% |
| ZN | 48 | $86,471.34 | 37.5000% |
| CL | 17 | $60,600.40 | 47.0588% |

## K-gate evaluation

- **K-gates fired:** NONE
- Implied park status if K fires: **N/A (no K fires)**

- K1_sharpe_proxy_lt_0: `False`
- K2_expectancy_le_0: `False`
- K4_trade_curve_maxdd_gt_50: `False`
- K6_safety_warning_count_gt_0: `False`
- K7_filter_silently_introduced: `False`
- K7_correlation_gate_silently_introduced: `False`
- K8_sealed_parent_drift: `0`
- K9_closed_trades_lt_100: `False`
- K10_avg_pairwise_corr_gt_0_50: `None`
- K11_cap_binding_events_gt_1000: `False`
- K12_DR_fires_on_cost_stress: `NOT_EVALUATED_THIS_TURN_ONLY_S1_RUN`

## C7 verdict (closed enum)

### **VERDICT: `READY_FOR_LONGER_BACKTEST`**

Reasons:
- All safety counters zero AND closed_trades >= 100; research label only (live-block applies regardless).

(C7 enum is closed: FAIL_SAFETY / INSUFFICIENT_SAMPLE / READY_FOR_LONGER_BACKTEST. READY_FOR_LONGER_BACKTEST is a research label only; 6-gate live-block applies regardless of verdict.)

## No-pyramid attestation

- max_units_per_market (CONFIG):       **1**
- max_units_observed_per_market:       `{'NQ': 0, 'GC': 1, 'ZN': 0, 'CL': 0}`
- max_units_observed_per_market_max:   **1**
- no_pyramid_invariant_held:           **True**
- per_market_unit_count_invariant_violation_count: **0**
- second_unit_add_attempt_count:       **0**

### **No-pyramid invariant pass: `True`**

## Safety counters (must all be 0)

- `stale_fill_warning_count`: 0
- `non_rth_fill_warning_count`: 0
- `rollover_violation_count`: 0
- `pyramid_state_machine_violation_count`: 0
- `n_calculation_drift_detected_count`: 0
- `unsupported_order_type_detected_count`: 0
- `per_market_unit_count_invariant_violation_count`: 0
- `cap_binding_events_count`: 0
- `all_safety_warnings_zero`: True

## Parent chain (byte-stable through run)

- smoke_pass_report: `1ab57a67f1a81be5...` (byte_stable=True)
- in_sample_driver_build_report: `d7b82d7adad62979...` (byte_stable=True)
- runner_build_report: `e1f2a13cb860a629...` (byte_stable=True)
- phase2_plan: `5e6fccd1aeb40db7...` (byte_stable=True)
- plan_lock: `612abbbda7235c8c...` (byte_stable=True)
- tier_n_spec: `8cff6babf8e4a451...` (byte_stable=True)
- selection_plan: `6b7bdb4c350f4a77...` (byte_stable=True)

Drift count: **0**

## s7-D1 non-revival attestation

- s7-D1 chain status: PERMANENTLY_PARKED_AT_COMMIT_f08220a
- s7-D1 revived by this run: **False**
- s7-D1 file shas byte-stable through P6 run: **True**
- s8-D1 source files byte-stable through P6 run: **True**

## Negative invariants this turn (all True)

- `no_b005_001_revival`: True
- `no_broker_adapter_instantiated`: True
- `no_code_patching_this_turn`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_data_fetch`: True
- `no_databento_api_call_via_db_Historical`: True
- `no_db_Historical_instantiated`: True
- `no_frc_granted`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_inspection`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_qc_api_call`: True
- `no_qc_cloud_submit`: True
- `no_review_queue_mutation`: True
- `no_s7_d1_file_modification`: True
- `no_s7_d1_revival`: True
- `no_scheduler_change`: True
- `no_threshold_loosening`: True
- `obsidian_file_count_bytes_invariant`: False

## Next step

> **AUTHORIZE S8-D1 P7 in-sample decision memo (PLAN-ONLY)** -- interpret this result, formalize the verdict + K-fire mapping, decide between PARK / OOS-AUTHORIZE / cost-stress-expansion, and record honest qualifications.

---

*End of s8-D1 P6 in-sample diagnostic result.*

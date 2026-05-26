# s8-D1 No-Pyramid - P9 OOS-S1 Diagnostic Result (SEALED, OOS window 2023-2025, cost_tier=S1)

**Phase:** `P9_OOS_S1_BASELINE_RUN_COMPLETE_SEALED`
**Operational status:** `OOS_S1_RUN_COMPLETE_VERDICT_INSUFFICIENT_SAMPLE_K_FIRES_1_AWAITING_P10_OR_OPTIONAL_P9_5`
**Report date UTC:** 2026-05-26T02:04:20Z

**OOS-S1 diagnostic seal:** `dedd8003381a8b9ae01e9432cacefdccda49f658a909b7bb8fcda9f2cda60c4f`
**Predecessor (P8 lifecycle) seal:** `49b1e6a726183484ce11bf3406c31885e19ba9c3ab67b0fdb9be28a35e1c98d3`
**Driver byte sha at run:** `129411e90fba23ff...` (file unchanged through run: True)

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S8_D1_P9_OOS_S1_RESULT_SEALED,
> NO_S7_D1_REVIVAL, OOS_WINDOW_2023_2025_NO_FUTURE_EXTRAPOLATION
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted
> No profitability claim. READY_FOR_LONGER_BACKTEST is a research label only.

---

## Runtime monkey-patch attestation

Driver `.py` file byte sha UNCHANGED (`129411e90fba23ff...`). Module-level
constants temporarily monkey-patched in-memory ONLY (P8 plan-lock allowed
OOS run using the same driver byte-equivalent against OOS window):

- `IN_SAMPLE_START`: 2013-01-01 -> 2023-01-01
- `IN_SAMPLE_END`:   2022-12-30 -> 2025-12-30
- `EXPECTED_FILES_PER_ROOT`: 120 -> 156
- `EXPECTED_CACHE_BYTES`: per-market originals -> combined IS+OOS values
- Constants restored after run: True

---

## Run metadata

- Cost tier: **S1**
- Duration: **289.7s** wall
- OOS window: 2023-01-01 -> 2025-12-30 UTC
- Cache (combined IS+OOS) at run start: 624 files, 172,454,306 bytes
- CONFIG max_units_per_market: **1** (locked)
- CONFIG filter: **NONE** (AMB6 locked)

## Performance metrics (OOS-S1)

- **closed_trades_portfolio:** 15
- **net_pnl_usd:** $1,442.94
- **win_rate_pct:** 46.6667%
- **win_rate_gap_to_breakeven_pp:** 2.7702719455934
- **sharpe_proxy_per_trade:** 0.044547
- **expectancy_per_trade_usd:** $96.20
- **pl_ratio:** 1.278091415830858
- **trade_curve_maxdd_pct:** -5.0997%
- **trade_curve_maxdd_usd:** $-5,099.67
- **starting_cash:** $100,000
- **final_equity:** $101,442.94

## Per-market breakdown (OOS-S1)

| Market | trades | net_pnl_usd | win_rate_pct |
|---|---|---|---|
| NQ | 0 | $0.00 | 0.0000% |
| GC | 0 | $0.00 | 0.0000% |
| ZN | 15 | $1,442.94 | 46.6667% |
| CL | 0 | $0.00 | 0.0000% |

## K-gate evaluation (OOS-S1)

- **K-gates fired:** ['K9']
- Implied next lifecycle state: **`ESCALATE_K9_OOS_VS_WINDOW_LENGTH_DECISION`**

- K1_sharpe_proxy_lt_0: `False`
- K2_expectancy_le_0: `False`
- K4_trade_curve_maxdd_gt_50: `False`
- K6_safety_warning_count_gt_0: `False`
- K7_filter_silently_introduced: `False`
- K8_sealed_parent_drift: `0`
- K9_closed_trades_lt_100: `True`
- K10_avg_pairwise_corr_gt_0_50: `None`
- K11_cap_binding_events_gt_1000: `False`
- K12_DR_fires_on_cost_stress: `NOT_EVALUATED_THIS_TURN_ONLY_S1`

## C7 verdict

### **VERDICT: `INSUFFICIENT_SAMPLE`**

Reasons:
- closed_trades_portfolio=15 < 100 -- expected in 3-year OOS window per phase-2 plan

## No-pyramid attestation

- `max_units_per_market` (CONFIG): **1**
- `max_units_observed_per_market_max`: **1**
- `no_pyramid_invariant_held`: **True**
- `per_market_unit_count_invariant_violation_count`: **0**
- **No-pyramid invariant pass: `True`**

## DR4 evaluation

- DR4 strict requires IS-S0 vs OOS-S0; only S1 run this turn -> **DR4 NOT directly evaluable**.
- Informational IS-S1 vs OOS-S1 comparison:
  - IS-S1 sharpe: 0.2250 -> OOS-S1 sharpe: 0.0445
  - IS-S1 expectancy: $1,743.09 -> OOS-S1 expectancy: $96.20
  - IS-S1 informational_sharpe_flipped_negative: False
  - IS-S1 informational_expectancy_flipped_non_positive: False

## IS-S1 vs OOS-S1 comparison (informational)

| metric | IS-S1 | OOS-S1 | delta |
|---|---|---|---|
| closed_trades | 111 | 15 | -96 |
| win_rate_pct | 39.63963963963964 | 46.666666666666664 | 7.0270270270270245 |
| sharpe_proxy | 0.22499793195273615 | 0.044547307945570276 | -0.18045062400716588 |
| expectancy_usd | 1743.08925972359 | 96.19569101901718 | -1646.8935687045728 |
| mdd_pct | -23.834105279667796 | -5.09966701216351 | 18.734438267504284 |

Interpretation note: OOS window is 3 years vs IS 10 years; trade-count differences are structurally expected.

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

- `P8_lifecycle`: `49b1e6a726183484...` (byte_stable=True)
- `P7_5_k10`: `221e759e09cc70b2...` (byte_stable=True)
- `P7_decision_memo`: `e26d00587d39404d...` (byte_stable=True)
- `P6_5_cost_stress`: `edae2e56cf16c925...` (byte_stable=True)
- `P6_in_sample_diagnostic`: `07a3fa91509f2206...` (byte_stable=True)
- `P4_smoke`: `1ab57a67f1a81be5...` (byte_stable=True)
- `driver_build`: `d7b82d7adad62979...` (byte_stable=True)
- `runner_build`: `e1f2a13cb860a629...` (byte_stable=True)
- `phase2_plan`: `5e6fccd1aeb40db7...` (byte_stable=True)
- `plan_lock`: `612abbbda7235c8c...` (byte_stable=True)
- `tier_n_spec`: `8cff6babf8e4a451...` (byte_stable=True)
- `selection_plan`: `6b7bdb4c350f4a77...` (byte_stable=True)

Drift count: **0**

## s7-D1 non-revival + s8-D1 source byte-stability

- s7-D1 file shas byte-stable through P9 run: **True**
- s8-D1 source files byte-stable through P9 run: **True**
- Driver `.py` file byte sha unchanged: **True**

## Negative invariants this turn (all True)

- `monkey_patch_was_in_memory_only_module_state_restored_after_run`: True
- `no_b005_001_revival`: True
- `no_broker_adapter_instantiated`: True
- `no_code_patch_committed_to_disk`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_data_fetch`: True
- `no_databento_api_call_via_db_Historical`: True
- `no_db_Historical_instantiated`: True
- `no_driver_file_modification_on_disk`: True
- `no_frc_granted`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_cost_stress_this_turn`: True
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

---

## Next step

Per the P8 OOS decision tree:

> Implied next lifecycle state: **`ESCALATE_K9_OOS_VS_WINDOW_LENGTH_DECISION`**

Operator options:
- **AUTHORIZE S8-D1 P9.5 OOS cost-stress S0/S2/S3/S4** (mirror P6.5 to evaluate DR2/DR3/DR4/DR5/K12 on OOS)
- **AUTHORIZE S8-D1 P9.75 K10 OOS robustness check** (re-compute avg_pairwise_correlation on OOS window)
- **AUTHORIZE S8-D1 P10 OOS decision memo (PLAN-ONLY)** (synthesize OOS-S1 result into recommendation per P8 decision tree)
- **AUTHORIZE S8-D1 P11 default park** (conservative path; record OOS-S1 outcome and stop)

---

*End of s8-D1 P9 OOS-S1 diagnostic result. Sealed at `dedd8003381a8b9ae01e9432cacefdccda49f658a909b7bb8fcda9f2cda60c4f`.*

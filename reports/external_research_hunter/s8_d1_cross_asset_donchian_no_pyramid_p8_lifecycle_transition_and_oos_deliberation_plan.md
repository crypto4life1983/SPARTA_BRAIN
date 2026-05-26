# s8-D1 No-Pyramid - P8 Lifecycle Transition + OOS Deliberation Plan (SEALED, PLAN-ONLY)

**Schema id:** `sparta.external_research_hunter.s8_d1_cross_asset_donchian_no_pyramid_p8_lifecycle_transition_and_oos_deliberation_plan.v1`
**Phase:** `P8_LIFECYCLE_TRANSITION_AND_OOS_DELIBERATION_PLAN_SEALED`
**Operational status:** `READY_FOR_OOS_AUTHORIZATION_DELIBERATION_P8_SEALED`
**Report date UTC:** 2026-05-26T01:19:30Z

**P8 seal:** `49b1e6a726183484ce11bf3406c31885e19ba9c3ab67b0fdb9be28a35e1c98d3`
**Predecessor (P7.5 K10) seal:** `221e759e09cc70b22e7a7d8001e30190e2dc1388506c1f330850f447303e3443`

> **Labels:** DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S8_D1_P8_LIFECYCLE_TRANSITION_AND_OOS_PLAN_SEALED,
> SINGLE_DELTA_FROM_S7_D1_MAX_UNITS_1, NO_S7_D1_REVIVAL, READY_FOR_OOS_DELIBERATION_BUT_OOS_NOT_INSPECTED
> **Trading:** PAUSED | **Live:** BLOCKED_AT_6_GATES | **FRC:** not granted
> No profitability claim. No live promotion.

---

## LIFECYCLE TRANSITION

- **From state:** `K10_PASS_READY_FOR_OOS_AUTHORIZATION_DELIBERATION_AWAITING_P8`
- **To state:**   `READY_FOR_OOS_AUTHORIZATION_DELIBERATION_P8_SEALED`
- **Authority:** operator_authorization_AUTHORIZE_S8_D1_P8_lifecycle_transition_and_OOS_deliberation_plan
- **Basis:** All preregistered in-sample K-gates and A-gates evaluated and passing per inherited sealed evidence chain; K10 PASS confirms cross-asset diversification hypothesis; P8 formalizes readiness for OOS-AUTHORIZATION deliberation WITHOUT actually authorizing or running OOS.

**Permanent invariants preserved:**
- `trading_status_PAUSED`
- `live_status_BLOCKED_AT_6_GATES`
- `frc_never_granted`
- `live_promotion_path_closed`
- `no_profitability_claim`
- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE_label_permanent`

---

## ALL IN-SAMPLE GATES STATUS

### K-gates (rejection criteria) — all PASS

| Gate | Threshold | Observed | Fires? | PASS |
|---|---|---|---|---|
| K1_sharpe_proxy_per_trade_lt_0 | > 0 | 0.22499793195273615 | False | True |
| K2_expectancy_per_trade_le_0 | > 0 | 1743.08925972359 | False | True |
| K4_trade_curve_maxdd_pct_gt_50 | <= 50% | 23.834105279667796 | False | True |
| K6_safety_warning_count_gt_0 | == 0 | 0 | False | True |
| K7_filter_or_correlation_gate_silently_introduced | — | — | False | True |
| K8_sealed_parent_drift_gt_0 | — | — | False | True |
| K9_closed_trades_portfolio_lt_100 | >= 100 | 111 | False | True |
| K10_avg_pairwise_correlation_gt_0_50 | <= 0.50 | 0.0650295074733679 | False | True |
| K11_cap_binding_events_gt_1000 | <= 1000 | 0 | False | True |
| K12_REJECT_FAST_via_DR2_DR3_DR5 | — | — | False | True |

Summary: all evaluated preregistered K-gates PASS at S1 baseline.

### A-gates (acceptance criteria) — all PASS

- **A1_closed_trades_ge_100**: value=111, threshold=>= 100, PASS=True
- **A2_sharpe_proxy_gt_0**: value=0.22499793195273615, threshold=> 0, PASS=True
- **A3_expectancy_gt_0**: value=1743.08925972359, threshold=> 0, PASS=True
- **A4_trade_curve_maxdd_pct_le_50**: value=23.834105279667796, threshold=<= 50%, PASS=True
- **A5_2of4_markets_wr_gap_ge_0_or_portfolio_wr_gap_ge_plus_half_pp**: value=16.50362194194087, threshold=>= +0.5pp, PASS=True
- **A6_validator_pass**: value=—, threshold=—, PASS=True
- **A7_effective_independent_bets_ge_2_5**: value=3.3470323954746335, threshold=>= 2.5, PASS=True
- **A8_cost_stress_S0_S4_run_and_DR_not_fired**: value=—, threshold=—, PASS=True
- **A9_phase2_c1_c8_inheritance_attestable**: value=—, threshold=—, PASS=True
- **A10_cap_binding_events_eq_0**: value=0, threshold=== 0, PASS=True

### C-contracts (Phase-2 safety clauses) — all ATTESTED PASS

- **C1_LiveMode_refusal**: attested=True
- **C2_provenance_contract**: attested=True
- **C3_safety_counters**: attested=True
- **C4_rth_execution_discipline**: attested=True
- **C5_event_risk_contract**: attested=True
- **C6_diagnostic_output_schema**: attested=True
- **C7_verdict_semantics**: attested=True
- **C8_candidate_lifecycle**: attested=True

### No-pyramid specific invariants (s8-D1) — all PASS

- `max_units_per_market_equals_1_attested_runtime`: True
- `max_units_observed_per_market_max_le_1_across_all_5_cost_tiers`: True
- `per_market_unit_count_invariant_violation_count_eq_0_all_tiers`: True
- `pyramid_state_machine_violation_count_eq_0_all_tiers`: True

---

## OOS WINDOW NOT INSPECTED ATTESTATION

- `oos_window_utc`: ['2023-01-01', '2025-12-30']
- `oos_inspected_at_or_before_p8`: False
- `oos_data_loaded_at_or_before_p8`: False
- `oos_decode_attempted_at_or_before_p8`: False
- `oos_metric_computed_at_or_before_p8`: False
- `in_sample_window_inspection_only_attested_through_p7_5`: True
- `p8_does_not_inspect_OOS`: True

---

## OOS DELIBERATION PLAN (PLAN-ONLY)

### Purpose
Lay out the OOS evaluation framework for s8-D1 WITHOUT executing any OOS step. Each future OOS step requires its own separate explicit operator authorization.

### Strategy definition at OOS (byte-equivalent to in-sample per plan-lock)

- `max_units_per_market`: 1
- `no_pyramid_invariant`: True
- `donchian_entry`: 55
- `donchian_exit`: 20
- `wilder_atr_period`: 20
- `stop_n_multiplier`: 2.0
- `risk_pct_per_unit`: 0.01
- `amb6_filter`: NONE
- `universe`: ['NQ.c.0', 'GC.c.0', 'ZN.c.0', 'CL.c.0']
- `starting_cash_mnq_equivalent`: 100000
- `portfolio_cap_max_units`: 4
- `portfolio_cap_uses_unit_count_not_contract_count`: True
- `all_parameters_byte_equivalent_to_in_sample_per_plan_lock`: True

### Operator-managed OOS Databento fetch plan

Operator must locally fetch OOS .dbn.zst files into existing cache directories; SPARTA does NOT execute the fetch.

- Fetch target root: `C:/SPARTA_BRAIN/data/databento_cache/{NQ,GC,ZN,CL}/2023-*..2025-*/`

Estimated cache additions:

- `estimated_months_oos`: 36
- `estimated_markets`: 4
- `estimated_dbn_files_total`: 144
- `per_market_per_month_files_expected`: 1
- `note`: Mirrors the in-sample cache structure: 120 files (10 years * 12 months) per market; OOS would add 36 files (3 years * 12 months) per market; 4 markets total = 144 additional DBN files.

Fetch script must NOT:
- Be authored by SPARTA in this P8 turn
- Be authored by SPARTA in any P8.5 turn (operator owns the fetch script entirely)
- Print or log DATABENTO_API_KEY
- Write any file outside data/databento_cache/
- Modify any sealed chain artifact
- Touch obsidian-trade-logger
- Touch review_queue.json
- Make any SPARTA-side commit or git operation

- Operator must produce a per-market file_count + total_bytes manifest similar to the in-sample cache attestation; SPARTA will verify this in P9 pre-flight.
- OOS cache complete; in-sample cache (480 files, 129,789,451 bytes) BYTE-STABLE; combined cache supports both in-sample re-validation (S-STOP-12 check) and OOS run (P9).

### Pre-OOS-run checklist (for future P9)

- Verify driver byte sha matches build-recorded (S-STOP-10 check)
- Verify CONFIG['max_units_per_market'] == 1 (S-STOP-11 check)
- Verify CONFIG['filter'] is None (AMB6 invariant)
- Verify all 12 s8-D1 chain artifacts byte-stable (S-STOP-12 check)
- Verify in-sample cache 480 files / 129,789,451 bytes UNCHANGED (S-STOP-12 check)
- Verify operator-supplied OOS cache present with attested per-market file_count + bytes
- Verify obsidian-trade-logger tracked-file changes still == 93 (baseline preserved)
- Verify operator P9 authorization line received explicitly
- Verify no s7-D1 source file modification has occurred since P7.5 (s7-D1 byte-stability)
- Verify no D5 / B005_001 / NKE / s7-D1 chain artifact mutation

### OOS run plan (for future P9)

#### step_p9_baseline
- `cost_tier`: S1
- `purpose`: Establish OOS baseline at preregistered S1 cost tier; mirror P6 in-sample baseline.
- `expected_duration_seconds`: approximately 60-90 seconds (3-year OOS window; one-quarter of in-sample 10-year window's ~240s)
- `expected_decode_path`: db.DBNStore.from_file via the existing in_sample_driver mechanic (driver byte-stable; no modification)
- `expected_output`: reports/.../s8_d1_cross_asset_donchian_no_pyramid_oos_diagnostic_result_sealed_S1.{md,json}
- `K-gate_evaluation`: K1-K12 (where evaluable) at OOS-S1
- `C7_verdict_evaluation`: FAIL_SAFETY / INSUFFICIENT_SAMPLE / READY_FOR_FURTHER_OOS_TIER
- `no_pyramid_attestation_required`: True

#### step_p9_cost_stress_oos_optional
- `purpose`: If P9 S1 baseline passes, run S0/S2/S3/S4 OOS cost-stress matrix; mirror P6.5.
- `requires_separate_authorization`: True
- `expected_duration_seconds`: approximately 4 * 90 = 360 seconds (~6 min wall)

#### DR4_evaluation_plan
- `purpose`: Evaluate DR4 (IS positive but OOS negative at S0 baseline -> ESCALATE).
- `becomes_evaluable_when`: After OOS S0 run completes; compares OOS-S0 vs IS-S0 sharpe + expectancy.
- `fires_when`: IS-S0 sharpe > 0 AND IS-S0 expectancy > 0 AND OOS-S0 sharpe <= 0 OR OOS-S0 expectancy <= 0
- `consequence`: ESCALATE_OPERATOR_REVIEW (not REJECT_FAST; not PARK; halt for explicit operator review of why OOS diverged from IS at zero-cost floor)

#### K10_oos_evaluation_plan
- `purpose`: Re-evaluate avg_pairwise_correlation over OOS window 2023-2025 for K10 robustness.
- `rationale`: K10 was computed over in-sample window only; cross-asset correlations can shift; OOS K10 robustness is informative.
- `fires_when`: OOS avg_pairwise_correlation > 0.50
- `consequence_if_fires`: ESCALATE for operator decision; K10 OOS fire does NOT automatically park since the strategy was preregistered on in-sample evidence, but it weakens the OOS interpretation.

#### honest_qualifications_for_oos_run
- Sample size in OOS will be ~3 years vs 10 years in-sample; expect closed_trades_portfolio in the 30-50 range; K9 threshold of 100 will likely fire at OOS-S1 simply because the window is shorter; this is a STRUCTURAL artifact of the OOS window length, not a strategy fail. The P9 result interpretation must distinguish 'K9 fires due to OOS window length' from 'K9 fires due to strategy regime shift'.
- P/L variance over 3 years is wider relative to 10 years; per-trade Sharpe may be noisier; interpret with caution.
- Cost-stress matrix can amplify the K9 small-sample issue at S4 (already at K9=99 in IS).
- Per-market correlation can drift; K10 OOS robustness check is informative.


### OOS decision tree

#### if_OOS_S1_baseline_passes_all_K_gates_evaluable
- `next_state_proposal`: OOS_S1_PASS_AWAITING_OOS_COST_STRESS_DELIBERATION
- `next_authorization_block`: AUTHORIZE S8-D1 P9.5 OOS cost-stress matrix S0/S2/S3/S4 (PLAN+RUN)

#### if_OOS_S1_baseline_fails_K1_or_K2_only
- `next_state_proposal`: PARKED_OOS_FAILED_AT_K1_OR_K2
- `rationale`: OOS edge collapsed; strategy fails on out-of-sample; not money-proven.

#### if_OOS_S1_baseline_fails_K4_only
- `next_state_proposal`: PARKED_OOS_FAILED_AT_K4
- `rationale`: OOS MaxDD exceeded 50%; risk-adjusted return inadequate even though signal direction may persist.

#### if_OOS_S1_baseline_fails_K9_only
- `next_state_proposal`: ESCALATE_K9_OOS_VS_WINDOW_LENGTH_DECISION
- `rationale`: Insufficient sample in OOS window; could be structural (3-year window vs 100-trade threshold) or strategic (entries declined); operator decides whether to extend OOS window or PARK.

#### if_OOS_S1_baseline_DR4_fires
- `next_state_proposal`: ESCALATE_DR4_IS_OOS_DIVERGENCE_REVIEW
- `rationale`: IS-S0 positive, OOS-S0 negative; investigate methodology before deciding park or proceed.

#### if_K10_OOS_fires_but_IS_K10_passed
- `next_state_proposal`: ESCALATE_K10_OOS_REGIME_SHIFT_REVIEW
- `rationale`: Cross-asset correlation regime shifted between IS and OOS; weakens diversification basis for live deliberation.

#### if_OOS_cost_stress_K12_fires
- `next_state_proposal`: REJECT_FAST_OOS_COST_STRESS
- `rationale`: DR2/DR3/DR5 fired at OOS cost-stress; strategy edge does not survive realistic OOS friction.

#### if_all_OOS_S1_and_cost_stress_pass_and_K10_OOS_pass_and_DR4_not_fired
- `next_state_proposal`: OOS_GREEN_LIGHT_BUT_LIVE_REMAINS_BLOCKED_AT_6_GATES
- `live_promotion`: STILL_BLOCKED
- `rationale`: Best-case OOS outcome: strategy passes preregistered IS + OOS gates AND cost-stress AND K10 OOS robustness. EVEN THEN: 6-gate live-block remains permanent for this candidate per Tier-N spec; FRC never granted; operator decision to extend research, fresh candidate, or park.
- `next_authorization_options`:
  - AUTHORIZE S8-D1 P11 lifecycle decision: extend research to longer-OOS or different cost-stress framework
  - AUTHORIZE S8-D1 P11 lifecycle decision: park candidate with all-OOS-passed status (research record only)
  - AUTHORIZE fresh s9 candidate for next evolution (e.g., max_units alternative, different filter, etc.)

### Honest qualifications for OOS deliberation

- OOS is NOT a live-readiness signal. 6-gate live-block is permanent for this candidate; FRC never granted.
- Passing OOS is necessary but NOT sufficient for any live consideration.
- OOS sample is structurally short (3 years); K9 may fire purely on window length.
- OOS correlation regime can shift; K10 OOS robustness check is informative but not automatic park.
- Cost-stress at OOS has the same DR rules as IS; K12 OOS fire is a REJECT_FAST.
- DR4 (IS-pos / OOS-neg @ S0) is the most diagnostic single check for IS-OOS divergence.
- If OOS PASSES, the next operator decision is research-extension or fresh-candidate; NOT live promotion.
- No profitability claim. No live trading. No paper trading. No scheduler change. No review_queue mutation.

---

## Future steps tree (each requires separate explicit operator authorization)

### P8_5_operator_managed_OOS_databento_fetch

- `owner`: operator
- `sparta_role`: DOES_NOT_EXECUTE_OR_AUTHOR_FETCH_SCRIPT
- `operator_actions`:
  - Operator's local Python script reads DATABENTO_API_KEY from env
  - Operator fetches .dbn.zst files into data/databento_cache/{NQ,GC,ZN,CL}/<2023..2025>/
  - Operator produces per-market file_count + bytes attestation manifest
  - Operator confirms in-sample cache (480 files, 129,789,451 bytes) byte-stable after fetch
- `sparta_actions_at_p8_5`: NONE (operator-only step)
- `next_authorization`: AUTHORIZE S8-D1 P9 OOS-S1 baseline run

### P9_OOS_S1_baseline_run

- `purpose`: Run in_sample_driver.run_in_sample(cost_tier='S1') against OOS window 2023-01-01..2025-12-30; expected ~60-90s wall.
- `requires_separate_authorization`: True
- `pre_flight_must_pass`: All 12 s8-D1 chain seals byte-stable + s7-D1 byte-stable + IS+OOS cache complete + driver byte-stable + CONFIG max_units=1
- `outputs`: reports/.../s8_d1_cross_asset_donchian_no_pyramid_oos_diagnostic_result_sealed.{md,json}
- `failure_rule`: If pre-flight fails or run fails, sealed fail report; do not patch code.

### P9_5_OOS_cost_stress_S0_S2_S3_S4_optional

- `purpose`: If P9 S1 passes all evaluable K-gates, run OOS cost-stress matrix; mirror P6.5.
- `requires_separate_authorization`: True
- `outputs`: reports/.../s8_d1_cross_asset_donchian_no_pyramid_oos_cost_stress_matrix_result_sealed.{md,json}

### P9_75_K10_OOS_robustness_check_optional

- `purpose`: Re-compute K10 (avg_pairwise_correlation) over OOS window 2023-2025; check robustness vs IS K10.
- `requires_separate_authorization`: True
- `outputs`: reports/.../s8_d1_cross_asset_donchian_no_pyramid_k10_oos_correlation_result_sealed.{md,json}

### P10_OOS_decision_memo

- `purpose`: Synthesize OOS evidence (P9 + optional P9.5/P9.75) into a sealed decision memo with recommendation among the OOS decision tree branches above. PLAN-ONLY.
- `requires_separate_authorization`: True
- `outputs`: reports/.../s8_d1_cross_asset_donchian_no_pyramid_oos_decision_memo.{md,json}

### P11_lifecycle_decision

- `purpose`: Formal lifecycle transition based on P10. Possible outcomes per oos_decision_tree.
- `requires_separate_authorization`: True
- `outputs`: reports/.../s8_d1_cross_asset_donchian_no_pyramid_p11_lifecycle_decision.{md,json}
- `live_promotion_remains_blocked_regardless_of_p11_outcome`: True

---

## s7-D1 non-revival attestation

- `s7_d1_chain_status`: PERMANENTLY_PARKED_AT_COMMIT_f08220a
- `s7_d1_revived_by_this_p8`: False
- `s7_d1_used_as`: UPSTREAM_EVIDENCE_AND_PARKED_REFERENCE_ONLY
- `s7_d1_strategy_logic_not_revived`: True
- `no_max_units_iteration_under_s8_d1_namespace`: True
- `any_future_max_units_value_neq_1_requires_fresh_candidate_record_id`: True

---

## Parent chain (12 byte-stable; drift=0)

- `P7_5_k10_correlation`: `221e759e09cc70b2...`
- `P7_decision_memo`: `e26d00587d39404d...`
- `P6_5_cost_stress_matrix`: `edae2e56cf16c925...`
- `P6_in_sample_diagnostic`: `07a3fa91509f2206...`
- `P4_smoke_pass`: `1ab57a67f1a81be5...`
- `in_sample_driver_build`: `d7b82d7adad62979...`
- `runner_build`: `e1f2a13cb860a629...`
- `phase2_plan`: `5e6fccd1aeb40db7...`
- `plan_lock`: `612abbbda7235c8c...`
- `tier_n_spec`: `8cff6babf8e4a451...`
- `selection_plan`: `6b7bdb4c350f4a77...`
- `s7_d1_parking_report`: `551fdce46c0e373e...`

---

## Negative invariants this turn (all True)

- `no_b005_001_revival`: True
- `no_backtest`: True
- `no_broker_adapter_instantiated`: True
- `no_code_patch`: True
- `no_cost_stress_rerun`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_data_fetch`: True
- `no_databento_api_call`: True
- `no_db_historical_instantiated`: True
- `no_driver_modification`: True
- `no_frc_granted`: True
- `no_in_sample_rerun`: True
- `no_live_promotion`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_data_load`: True
- `no_oos_inspection`: True
- `no_oos_metric_compute`: True
- `no_operator_fetch_script_authored_this_turn`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_qc_api_call`: True
- `no_qc_cloud_submit`: True
- `no_review_queue_mutation`: True
- `no_s7_d1_file_modification`: True
- `no_s7_d1_revival`: True
- `no_scheduler_change`: True
- `no_strategy_lab_promotion`: True
- `no_threshold_loosening`: True

---

*End of s8-D1 P8 lifecycle transition + OOS deliberation plan. Sealed at `49b1e6a726183484ce11bf3406c31885e19ba9c3ab67b0fdb9be28a35e1c98d3`. PLAN-ONLY. No OOS inspection. No fetch. No backtest. No code patch.*

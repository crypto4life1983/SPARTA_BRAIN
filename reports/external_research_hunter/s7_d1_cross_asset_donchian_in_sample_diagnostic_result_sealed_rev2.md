# s7 D1 -- In-Sample Diagnostic Result REV2 (SEALED, S1 baseline, PATCHED driver)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_diagnostic_result_sealed_rev2.v1`
**Status:** `SEALED`
**Candidate operational status:** `IN_SAMPLE_RUN_REV2_PATCHED_DRIVER_S1_BASELINE_READY_FOR_LONGER_BACKTEST`
**Sealed at (UTC):** `2026-05-25T20:33:37Z`
**Verdict:** `READY_FOR_LONGER_BACKTEST`  -- C7 enum default after FAIL_SAFETY and INSUFFICIENT_SAMPLE excluded
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`

> REV2: re-run of in-sample S1 baseline using the PATCHED in_sample_driver.py.
> Prior P6.5 result (commit c234bb1, seal 157ad1bf...) stays byte-stable as the historical
> record of the buggy-driver run. This REV2 is the first non-buggy empirical test of s7-D1.
> S0/S2/S3/S4 deferred. K12 / A6 / A7 / A8 deferred.
> No real promotion. Diagnostic only. NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT holds.

## Driver provenance
- Patched driver byte sha (committed at 8e8eb6e): `8741bc5182e227336a5c0e75afa9d037fc1c633b12eae97577ef98b6eea31ea9`
- Driver byte sha observed at run:                 `8741bc5182e227336a5c0e75afa9d037fc1c633b12eae97577ef98b6eea31ea9`
- Matches patched: **True**
- Prior buggy driver byte sha (was ae068755..., now superseded): committed at ee9aab7, then patched at 8e8eb6e

## Inheritance chain (drift=0; 11 prior seals)
- Predecessor (s7 selection plan):     `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
- Tier-N spec seal:                    `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
- Plan-lock seal:                      `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d`
- Phase-2 plan seal:                   `e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a`
- Runner build report seal:            `10610a6ad47c2fd584b556e773edb3ea09c8dfa9fb67aaa350b526938df03946`
- Execution guard build seal:          `5cfbfdbbb9fc695673e5d8dabce0019a67d053a7b18ad962962a9a97311b017e`
- Smoke pass report seal:              `ec244e92953ab850f68f7ec88945c80263bb40f154a90bba19bf930f4c9133e8`
- Blocked report seal:                 `f0f465d4c9b9199c4a45c060b8ff2552368128c5086354307394d2f8999fccf0`
- Prior driver_build_report seal:      `26e9c6f0c217f1f2daf994445bcae0c4d1bfe1ef9e81cfc1133f41823816b38e`
- Prior diagnostic_result seal:        `157ad1bf5a8994ea5364cffcf3f596728778f40ead2eb51615081c72e2b2bde5`
- Patch plan seal:                     `d03201de481f8712b008e213e16e082a2f394a977f65540705b225f93523fe1f`
- Patch build report seal:             `2ab3ed5852de0dadcbe11da3aa7451a8c8a01372cb26395e4e28467628892522`
- Parent sha drift at run:             **0**

## Context: prior P6.5 result
committed at c234bb1df2c5e8c6cd4827904b46fa2c978fe376; produced 0 closed trades because the prior driver (byte sha ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394) had a buffer-size off-by-one (buf_len=55 vs entry-trigger required >= 56). This REV2 run uses the patched driver (byte sha 8741bc5182e227336a5c0e75afa9d037fc1c633b12eae97577ef98b6eea31ea9) committed at 8e8eb6e; patch_build_report seal 2ab3ed5852de0dadcbe11da3aa7451a8c8a01372cb26395e4e28467628892522.

- This run supersedes prior for strategy interpretation: **True**
- This run does NOT invalidate prior for historical record: **True**
- Prior was strategy-falsifying: **False**
- Prior was driver-implementation-incomplete: **True**

## Run telemetry
- Invocation:    `in_sample_driver.run_in_sample(cost_tier='S1')`
- Started (UTC): `2026-05-25T20:29:57Z`
- Ended (UTC):   `2026-05-25T20:33:37Z`
- Runtime:       **219.9 s**
- Window:        `{'start': '2013-01-01', 'end': '2022-12-30'}`
- Cost tiers executed: `['S1']`
- Cost tiers deferred: `['S0', 'S2', 'S3', 'S4']`
- **Nonzero trades this run:** **True**

## S1 trade diagnostics
- `closed_trades_portfolio`: 313
- `n_long`: 197
- `n_short`: 116
- `wins`: 135
- `losses`: 178
- `win_rate_pct`: 43.13099041533546
- `avg_win_usd`: 18387.454629629625
- `avg_loss_usd`: -7497.274849770138
- `pl_ratio`: 2.452551760216364
- `expectancy_per_trade_usd`: 3667.065341025288
- `breakeven_wr_pct`: 28.964084232507847
- `win_rate_gap_to_breakeven_pp`: 14.166906182827615
- `sharpe_proxy_per_trade`: 0.1923049325498757
- `trade_curve_maxdd_usd`: -221668.0760195105
- `trade_curve_maxdd_pct`: -221.66807601951052

## Per-market breakdown
| Market | n_trades | net_pnl_usd | win_rate_pct |
|---|---:|---:|---:|
| `NQ` | 77 | 225,055.04 | 55.84 |
| `GC` | 56 | -27,110.15 | 33.93 |
| `ZN` | 115 | 369,866.62 | 33.91 |
| `CL` | 65 | 579,979.94 | 52.31 |

## Safety diagnostics (C3 counters)
- `stale_fill_warning_count`: 0
- `non_rth_fill_warning_count`: 0
- `rollover_violation_count`: 0
- `pyramid_state_machine_violation_count`: 0
- `n_calculation_drift_detected_count`: 0
- `unsupported_order_type_detected_count`: 0
- `cap_binding_events_count`: 0
- `all_safety_warnings_zero`: True

## K1-K12 evaluation
| K | name | fired | value | threshold | implied park |
|---|---|---|---|---|---|
| K1 | sharpe_negative | ok | 0.1923049325498757 | 0 | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| K2 | expectancy_nonpositive | ok | 3667.065341025288 | 0 | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| K4 | maxdd_excessive | FIRED | -221.66807601951052 | -50.0 | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| K6 | safety_warnings_nonzero | ok | 0 | 0 | PARKED_SAFETY_FAILED |
| K7 | filter_or_corr_gate_intro | ok | False | False | PARKED_SAFETY_FAILED |
| K8 | sealed_parent_drift | ok | 0 | 0 | PARKED_PROVENANCE_BROKEN |
| K9 | insufficient_sample | ok | 313 | 100 | PARKED_FAILED_AT_INSUFFICIENT_SAMPLE |
| K10 | diversification_falsified | ok | NOT_COMPUTED_IN_THIS_RUN | 0.5 | PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS |
| K11 | cap_binding_excessive | ok | 0 | 1000 | PARKED_CAP_BINDING |
| K12 | reject_fast | ok | NOT_EVALUATED_REQUIRES_FULL_S0_S4_MATRIX |  | REJECT_FAST |

- **Any K fired:** `['K4']`
- **Implied park status:** `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`

## A1-A10 acceptance gates
| A | name | pass | value | threshold |
|---|---|---|---|---|
| A1 | sample_size | True | 313 | >= 100 |
| A2 | sharpe_proxy_positive | True | 0.1923049325498757 | > 0 |
| A3 | expectancy_positive | True | 3667.065341025288 | > 0 |
| A4 | maxdd_acceptable | False | -221.66807601951052 | >= -50% |
| A5 | wr_breakeven_gap | True | {'markets_with_positive_pnl': 3, 'portfolio_wr_gap_pp': 14.166906182827615} | >= 2 markets positive AND portfolio wr_gap >= +0.5 pp |
| A6 | validator_pass | NOT_EVALUATED_IN_THIS_RUN |  |  |
| A7 | effective_independent_bets | NOT_COMPUTED_IN_THIS_RUN |  | >= 2.5 |
| A8 | cost_stress_survival | NOT_EVALUATED_REQUIRES_FULL_S0_S4_MATRIX |  |  |
| A9 | safety_template_C1_C8 | True |  |  |
| A10 | cap_binding_events_zero | True | 0 | == 0 |

- Fully-evaluated pass: **6**
- Fully-evaluated fail: **1**
- Deferred gates: `['A6', 'A7', 'A8']`

## C1-C8 attestation
- `C1_LiveMode_refusal`: applies; driver has no LiveMode path; status_fields PAUSED + BLOCKED_AT_6_GATES recorded
- `C2_provenance_contract`: applies; engine-truth window 2013-01-01..2022-12-30 hard-checked at function entry
- `C3_safety_counters`: applies; counters reported: {'stale_fill_warning_count': 0, 'non_rth_fill_warning_count': 0, 'rollover_violation_count': 0, 'pyramid_state_machine_violation_count': 0, 'n_calculation_drift_detected_count': 0, 'unsupported_order_type_detected_count': 0, 'cap_binding_events_count': 0, 'all_safety_warnings_zero': True}
- `C4_rth_execution_discipline`: applies; RTH per-market windows enforced (NQ/GC/ZN 09:30-16:00 ET, CL 09:30-14:30 ET)
- `C5_event_risk_contract`: PARTIAL; roll/expiry blackout NOT enforced in this driver version (continuous-front-month series stitched by Databento absorbs roll). Documented as limitation.
- `C6_diagnostic_output_schema`: applies; this report IS the C6 emission; sealed via LESSON_HUNTER_004
- `C7_verdict_semantics`: applies; closed-enum verdict = READY_FOR_LONGER_BACKTEST
- `C8_candidate_lifecycle`: applies; candidate_operational_status advanced to IN_SAMPLE_RUN_REV2_PATCHED_DRIVER_S1_BASELINE_READY_FOR_LONGER_BACKTEST

## Verdict
- **`READY_FOR_LONGER_BACKTEST`** -- C7 enum default after FAIL_SAFETY and INSUFFICIENT_SAMPLE excluded
- caveats: `['K4(maxdd_excessive) fired']`

## Obsidian-trade-logger preserved through run
- start == end: **True**

## Negative invariants (all True)
- `no_oos_inspection`: `True`
- `no_databento_api_call`: `True`
- `no_db_historical_client_invoked`: `True`
- `no_data_fetch`: `True`
- `no_network_call`: `True`
- `no_qc_call`: `True`
- `no_qc_cloud_submit`: `True`
- `no_broker_or_exchange_adapter`: `True`
- `no_yfinance`: `True`
- `no_live_trading`: `True`
- `no_paper_trading`: `True`
- `no_scheduler_code`: `True`
- `no_review_queue_mutation`: `True`
- `no_obsidian_trade_logger_touch`: `True`
- `no_code_patched`: `True`
- `no_threshold_loosened`: `True`
- `amb6_filter_none_invariant_preserved`: `True`
- `s6_portfolio_cap_bugfix_inherited`: `True`
- `no_d5_revived`: `True`
- `no_b005_001_revived`: `True`
- `no_nke_revived`: `True`
- `no_profitability_claim`: `True`
- `no_promotion_to_live`: `True`
- `prior_p6_5_result_unchanged`: `True`

## Next step
- `operator_decision_required; choose among: (a) AUTHORIZE_P6_5c_FULL_COST_STRESS_MATRIX (run S0/S2/S3/S4 to complete DR2/DR3/DR5 evaluation), (b) AUTHORIZE_P7_IN_SAMPLE_DECISION_MEMO (draft memo from S1 result; cite prior buggy-driver run for context), (c) AUTHORIZE_P8_LIFECYCLE_TRANSITION (park or hold based on K-fires)`

## Seal block (canonical)
- **`report_seal_sha256`**: `2563ef93092171718b11291048181664a9653d4f7d9e33d0e9df5bf7b741f4f6`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_diagnostic_result_sealed_rev2.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T20:33:37Z`

*End of REV2 in-sample diagnostic result. Diagnostic-only. No live promotion path. FRC never granted.*

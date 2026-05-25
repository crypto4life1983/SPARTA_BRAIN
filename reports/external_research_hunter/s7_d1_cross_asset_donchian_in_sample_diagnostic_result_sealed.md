# s7 D1 -- In-Sample Diagnostic Result (SEALED, S1 baseline)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_diagnostic_result_sealed.v1`
**Status:** `SEALED`
**Candidate operational status:** `IN_SAMPLE_RUN_COMPLETE_S1_BASELINE_INSUFFICIENT_SAMPLE`
**Sealed at (UTC):** `2026-05-25T19:36:30Z`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`
**FRC granted:** `False`
**Verdict:** `INSUFFICIENT_SAMPLE`  -- closed_trades_portfolio=0 < verdict_min_closed_trades=100

> S1 baseline cost tier only. S0/S2/S3/S4 deferred. K12 (DR2/DR3/DR5) requires full matrix.
> A6 (validator pass), A7 (effective_independent_bets), and A8 (cost-stress survival) deferred.
> No real promotion. Diagnostic only. NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT holds.

## Inheritance chain (all match recorded)
- Predecessor (s7 selection plan): `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
- Tier-N spec seal:                `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
- Plan-lock seal:                  `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d`
- Phase-2 plan seal:               `e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a`
- Runner build report seal:        `10610a6ad47c2fd584b556e773edb3ea09c8dfa9fb67aaa350b526938df03946`
- Execution guard build seal:      `5cfbfdbbb9fc695673e5d8dabce0019a67d053a7b18ad962962a9a97311b017e`
- Smoke pass report seal:          `ec244e92953ab850f68f7ec88945c80263bb40f154a90bba19bf930f4c9133e8`
- Blocked report seal:             `f0f465d4c9b9199c4a45c060b8ff2552368128c5086354307394d2f8999fccf0`
- Driver build report seal:        `26e9c6f0c217f1f2daf994445bcae0c4d1bfe1ef9e81cfc1133f41823816b38e`
- Driver byte sha at run:          `ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394`  match_committed=**True**
- Parent sha drift at run:         **0**

## Run telemetry
- Invocation:    `in_sample_driver.run_in_sample(cost_tier='S1')`
- Started (UTC): `2026-05-25T19:32:29Z`
- Ended (UTC):   `2026-05-25T19:36:30Z`
- Runtime:       **241.2 s**
- Window:        `{'start': '2013-01-01', 'end': '2022-12-30'}`
- Cost tiers executed: `['S1']`
- Cost tiers deferred: `['S0', 'S2', 'S3', 'S4']`

## S1 trade diagnostics
- `closed_trades_portfolio`: 0
- `n_long`: 0
- `n_short`: 0
- `wins`: 0
- `losses`: 0
- `win_rate_pct`: 0.0
- `avg_win_usd`: 0.0
- `avg_loss_usd`: 0.0
- `pl_ratio`: inf
- `expectancy_per_trade_usd`: 0.0
- `breakeven_wr_pct`: None
- `win_rate_gap_to_breakeven_pp`: None
- `sharpe_proxy_per_trade`: 0.0
- `trade_curve_maxdd_usd`: 0.0
- `trade_curve_maxdd_pct`: 0.0

## Per-market breakdown
| Market | n_trades | net_pnl_usd | win_rate_pct |
|---|---:|---:|---:|
| `NQ` | 0 | 0.00 | 0.00 |
| `GC` | 0 | 0.00 | 0.00 |
| `ZN` | 0 | 0.00 | 0.00 |
| `CL` | 0 | 0.00 | 0.00 |

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
| K1 | sharpe_negative | ok | 0.0 | 0 | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| K2 | expectancy_nonpositive | FIRED | 0.0 | 0 | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| K4 | maxdd_excessive | ok | 0.0 | -50.0 | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| K6 | safety_warnings_nonzero | ok | 0 | 0 | PARKED_SAFETY_FAILED |
| K7 | filter_or_corr_gate_intro | ok | False | False | PARKED_SAFETY_FAILED |
| K8 | sealed_parent_drift | ok | 0 | 0 | PARKED_PROVENANCE_BROKEN |
| K9 | insufficient_sample | FIRED | 0 | 100 | PARKED_FAILED_AT_INSUFFICIENT_SAMPLE |
| K10 | diversification_falsified | ok | NOT_COMPUTED_IN_THIS_RUN | 0.5 | PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS |
| K11 | cap_binding_excessive | ok | 0 | 1000 | PARKED_CAP_BINDING |
| K12 | reject_fast | ok | NOT_EVALUATED_REQUIRES_FULL_S0_S4_MATRIX |  | REJECT_FAST |

- **Any K fired:** `['K2', 'K9']`
- **Implied park status:** `PARKED_FAILED_AT_INSUFFICIENT_SAMPLE`

## A1-A10 acceptance gates
| A | name | pass | value | threshold |
|---|---|---|---|---|
| A1 | sample_size | False | 0 | >= 100 |
| A2 | sharpe_proxy_positive | False | 0.0 | > 0 |
| A3 | expectancy_positive | False | 0.0 | > 0 |
| A4 | maxdd_acceptable | True | 0.0 | >= -50% |
| A5 | wr_breakeven_gap | False | {'markets_with_positive_pnl': 0, 'portfolio_wr_gap_pp': None} | >= 2 markets positive AND portfolio wr_gap >= +0.5 pp |
| A6 | validator_pass | NOT_EVALUATED_IN_THIS_RUN |  |  |
| A7 | effective_independent_bets | NOT_COMPUTED_IN_THIS_RUN |  | >= 2.5 |
| A8 | cost_stress_survival | NOT_EVALUATED_REQUIRES_FULL_S0_S4_MATRIX |  |  |
| A9 | safety_template_C1_C8 | True |  |  |
| A10 | cap_binding_events_zero | True | 0 | == 0 |

- Fully-evaluated pass: **3**
- Fully-evaluated fail: **4**
- Deferred gates: `['A6', 'A7', 'A8']`

## C1-C8 attestation
- `C1_LiveMode_refusal`: applies; driver has no LiveMode path; status_fields recorded PAUSED + BLOCKED_AT_6_GATES
- `C2_provenance_contract`: applies; engine-truth window 2013-01-01..2022-12-30 baked into run_in_sample; cache + seal hard-checked at function entry
- `C3_safety_counters`: applies; counters reported: {'stale_fill_warning_count': 0, 'non_rth_fill_warning_count': 0, 'rollover_violation_count': 0, 'pyramid_state_machine_violation_count': 0, 'n_calculation_drift_detected_count': 0, 'unsupported_order_type_detected_count': 0, 'cap_binding_events_count': 0, 'all_safety_warnings_zero': True}
- `C4_rth_execution_discipline`: applies; RTH per-market windows enforced in derive_rth_daily_bars (NQ/GC/ZN 09:30-16:00 ET, CL 09:30-14:30 ET)
- `C5_event_risk_contract`: PARTIAL; roll/expiry blackout NOT enforced in this driver version (continuous-front-month series stitched by Databento absorbs roll). Documented as limitation.
- `C6_diagnostic_output_schema`: applies; this report IS the C6 emission; sealed via LESSON_HUNTER_004
- `C7_verdict_semantics`: applies; closed-enum verdict = INSUFFICIENT_SAMPLE
- `C8_candidate_lifecycle`: applies; candidate_operational_status advanced to IN_SAMPLE_RUN_COMPLETE_S1_BASELINE_INSUFFICIENT_SAMPLE

## Verdict
- **`INSUFFICIENT_SAMPLE`** -- closed_trades_portfolio=0 < verdict_min_closed_trades=100

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

## Next step
- `operator_decision_required; choose among: (a) AUTHORIZE_P6_5b_FULL_COST_STRESS_MATRIX (run S0/S2/S3/S4 -- ~2-3 hours; or first patch driver to cache decoded data), (b) AUTHORIZE_P7_IN_SAMPLE_DECISION_MEMO (draft memo from S1 result only), (c) AUTHORIZE_P8_LIFECYCLE_TRANSITION (park or hold)`

## Seal block (canonical)
- **`report_seal_sha256`**: `157ad1bf5a8994ea5364cffcf3f596728778f40ead2eb51615081c72e2b2bde5`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_diagnostic_result_sealed.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T19:36:30Z`

*End of in-sample diagnostic result. Diagnostic-only. No live promotion path. FRC never granted.*

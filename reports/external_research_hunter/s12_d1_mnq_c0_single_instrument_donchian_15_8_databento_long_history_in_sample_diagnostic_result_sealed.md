# S12-D1 P6 IS diagnostic result (sealed)

**Candidate record id:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`
**Phase:** `PHASE2-S12-D1-MNQ-DONCHIAN-15-8` / `P6_IS_DIAGNOSTIC`
**Backtest run_id:** `PHASE2-S12-D1-IS-0db3bf330b31`
**Authored (UTC):** `2026-05-27T15:56:37.333627Z`
**Lifecycle state:** P6_IS_DIAGNOSTIC_SEALED
**Report seal sha256:** `33c91592c09860c3ab9469aab38741b7378f54ad56ff3772f9ef6a03ea92156d`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES (UTF-8 explicit)

## Verdict

**`INSUFFICIENT_SAMPLE`**

### Verdict reasons

- K9 closed_trades = 48 < 100 (A1 fails)

### Verdict caveats (LOAD-BEARING)

- P6 IS verdict reflects IS-window performance only; OOS verdict requires separate P10 authorization
- REC1 (binding): OOS K9 STRUCTURALLY UNREACHABLE -- implied OOS trade count 35-87 < K9=100; expected OOS terminal verdict is PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED regardless of IS outcome
- P6 IS PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict
- P6.5 cost-stress sweep not yet run; DR2/DR3/DR4/DR5/DR10 thresholds NOT YET EVALUATED at S0/S2/S3/S4 tiers

## Performance summary

| Metric | Value |
|---|---|
| `starting_cash_usd` | $100,000.00 (DA4=B) |
| `final_equity_usd` | $193,921.43 |
| `gross_pnl_usd` | $94,665.02 |
| `net_pnl_usd` | $93,921.42 |
| `total_commission_usd` | $500.24 |
| `total_fees_usd` | $243.36 |
| `total_slippage_usd` | $676.00 |
| `total_costs_usd` | $1,419.60 |
| `max_drawdown_usd` | $91,677.74 |
| `max_drawdown_pct` (magnitude) | 37.6202% |
| `longest_drawdown_days` | 1014 |
| `time_underwater_pct` | 81.29% |
| `cagr_pct` | 15.3788% |
| `sharpe_annualized` | 0.5038 |
| `sortino_annualized` | 0.5978 |
| `sharpe_proxy_per_trade` | 0.1192 |
| `expectancy_per_trade_usd` | $1956.70 |
| `avg_win_usd` | $15105.93 |
| `avg_loss_usd` | $-10140.60 |
| `profit_loss_ratio` | 1.4896 |
| `win_rate_pct_or_NA_INSUFFICIENT_SAMPLE` | NA_INSUFFICIENT_SAMPLE |
| `closed_trades_count` | 48 |
| `trades_per_year_observed` | 10.37 |
| `annual_turnover` | 78.4884 |
| `s1_cost_drag_fraction` | 1.4196% |
| `s2_cost_drag_fraction_estimate` | 2.1294% |

## Trade diagnostics

| Field | Value |
|---|---|
| Closed trades count | 48 |
| Long trades | 25 |
| Short trades | 23 |
| Stop exits | 9 |
| Donchian exits | 38 |
| Window-end closes | 1 |
| Win count | 23 |
| Loss count | 25 |

## Safety diagnostics

| Counter | Value |
|---|---|
| `stale_fill_warning_count` | 0 |
| `extended_hours_fill_warning_count` | 0 (NOT_APPLICABLE for futures) |
| `unsupported_order_type_detected_count` | 0 (NOT_APPLICABLE for CSV simulator) |
| `warmup_orders_attempted` | 0 (B006_002 invariant) |
| `cap_binding_events_count` | 0 (NOT_APPLICABLE for F1 no leverage cap) |
| `pyramid_attempts` | 0 |
| `all_safety_warnings_zero` | True |

## A-gates (P6 IS)

| Gate | Result |
|---|---|
| A1 closed_trades >= 100 | False (48 trades) |
| A2 sharpe_proxy_per_trade > 0 | True (0.1192) |
| A3 expectancy_per_trade > 0 | True ($1956.70) |
| A4 \|maxdd_pct\| <= 50% | True (37.6202%) |
| A6 no_pyramid attestation | True |
| A8 cost-stress S0/S4 | DEFERRED_TO_P6_5 |
| A9 C1-C8 inheritance attestable | True |
| A10 cap_binding_events==0 | NOT_APPLICABLE_F1_NO_LEVERAGE_CAP |

## K-gates (P6 IS scope)

| K-gate | Triggered |
|---|---|
| K1 sharpe_proxy < 0 at S1 | False |
| K2 expectancy <= 0 at S1 | False |
| K4 \|maxdd\| > 50% | False |
| K9 closed_trades < 100 | True |
| K12 DR fires on cost-stress | DEFERRED_TO_P6_5 |

## Scan diagnostics

| Field | Value |
|---|---|
| Bars processed (total IS) | 1443 |
| Bars after warmup | 1223 |
| Warmup days used | 220 |
| IS window start (engine truth) | 2019-05-13 |
| IS window end (engine truth) | 2023-12-29 |
| IS window length (years) | 4.6297 |
| CSV sha verified at load | True |
| CSV path used at load | `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` |
| CSV sha256 | `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e` |
| OOS data filtered out at load | True |
| OOS bars NEVER read in signal logic | True |

## REC1 inherited_constraints_block (carried byte-equivalent; binding)

> *"OOS K9 EXPECTED TO FIRE. Implied OOS trade count over 2.0y at IS rate is approximately 35-87 trades, below K9 = 100. If OOS K9 fires, the OOS verdict will be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s12-d1 accepts the structural likelihood of an OOS PARK outcome."*

## Parent references

| Phase | Commit | Seal sha256 |
|---|---|---|
| Tier-N SEAL | `66bbbd1` | `07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48` |
| P1 plan-lock | `d8bd359` | `eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340` |
| P2 phase-2 plan | `0b8d948` | `689dd3d06c0e2518ab5f6105544cb3d38194027647de10940da976e427c8efa9` |
| P3 BUILD (3 reports within) | `91e740e` | (runner / IS-driver / OOS-driver sealed) |
| P4 smoke | `ea78845` | `6d2bff4d2b40d4349a1c26d37375ca6d9e8ea616ff9f85d3d9f56293325b8bd4` |

## Hard boundaries held (this P6 IS turn; ~38 boundaries; all True)

See JSON sidecar `hard_boundaries_held_this_p6_is_turn` for full attestation. Key:
- `no_oos_inspection`, `no_oos_data_read_by_signal_logic`
- `no_p6_5_cost_stress_run`, `no_p7_decision_memo`, `no_p10_oos_gate`, `no_p11_lifecycle`
- `csv_sha_verified_at_load`, `csv_loaded_from_sealed_expected_path_only`
- `oos_rows_filtered_out_at_load`, `warmup_window_observed_no_orders_during_warmup`
- `no_modification_of_p3_source_files_main_execution_guard_drivers`
- `no_modification_of_s11_d1_sealed_artifacts / s12_d1_seal / p1 / p2 / p3 / p4`
- `no_rec1_demotion_to_advisory`
- `no_lessons_md_touched`

## Status

| Field | Value |
|---|---|
| trading_status | PAUSED |
| live_status | BLOCKED_AT_6_GATES |
| frc_status | NEVER_GRANTED |
| backtest_diagnostic_only | True |
| research_label | DIAGNOSTIC_ONLY_NOT_LIVE_GRADE |
| lifecycle_state | P6_IS_DIAGNOSTIC_SEALED |
| rec1_oos_k9_risk_disclosure_binding | True |

## Next phase requirements

P6.5 cost-stress matrix requires separate authorization: `Authorize s12 D1 MNQ.c.0 P6.5 cost-stress matrix only`. **NO phase beyond P6.5 pre-approved by this P6 IS report.**

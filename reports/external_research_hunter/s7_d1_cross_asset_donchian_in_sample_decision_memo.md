# s7 D1 -- In-Sample Decision Memo (SEALED)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_decision_memo.v1`
**Status:** `SEALED`
**Candidate operational status (at memo):** `IN_SAMPLE_DECISION_MEMO_SEALED_RECOMMEND_PARK`
**Recommended next status (P8 required):** `PARKED_SAFE_BUT_NOT_MONEY_PROVEN (P8 lifecycle transition required)`
**Sealed at (UTC):** `2026-05-25T20:46:57Z`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`
**FRC granted:** `False`

> PLAN-ONLY. No new backtest. No code patched. No Databento/QC/network/OOS.
> No obsidian touch. No review_queue mutation. No s8 files created.
> Prior buggy P6.5 result preserved byte-stable. Rev2 supersedes for strategy interpretation.
> NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT continues to hold.

## Final recommendation
- **Action:** `PARK_AS_PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- **Recommended park status:** `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- **Do NOT proceed to live:** **True**
- **Do NOT claim profitability:** **True**
- **Do NOT run further s7-D1 tests unless separately authorized:** **True**
- **Do NOT iterate parameters:** **True**
- **Park is permanent for s7-D1:** **True**
- **Revival requires fresh s8+ candidate_record_id:** **True**
- **Next separately-authorized step:** `P8_LIFECYCLE_TRANSITION (writes canonical PARKING_REPORT.{md,json}; advances candidate_operational_status to PARKED_SAFE_BUT_NOT_MONEY_PROVEN; preserves all sealed artifacts including the rev2 result)`

### Park reason summary
K4 fired at -221.67% trade-curve MaxDD; the cross-asset Donchian signal is genuinely positive at the per-trade economics level, but the 4-unit pyramid mechanic produces catastrophic drawdowns that breach the safety threshold. Park preserves the empirical record; no further iteration of s7-D1 parameters.

## Inheritance chain (drift=0; 12 sealed seals)
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
- Rev2 diagnostic result seal:         `2563ef93092171718b11291048181664a9653d4f7d9e33d0e9df5bf7b741f4f6`
- Patched driver byte sha:             `8741bc5182e227336a5c0e75afa9d037fc1c633b12eae97577ef98b6eea31ea9`
- Parent sha drift at memo:            **0**

## Evidence anchor
- Rev2 diagnostic result seal: `2563ef93092171718b11291048181664a9653d4f7d9e33d0e9df5bf7b741f4f6`
- Patched driver commit:       `8e8eb6e`
- Rev2 run commit:             `6048075`
- Rev2 invocation:             `in_sample_driver.run_in_sample(cost_tier='S1')`
- Rev2 runtime:                **219.9 s**
- In-sample window:            `2013-01-01..2022-12-30`
- Cost tier run:               `S1`
- Cost tiers deferred:         `['S0', 'S2', 'S3', 'S4']`

## Rev2 trade metrics
- `closed_trades_portfolio`: `313`
- `n_long`: `197`
- `n_short`: `116`
- `wins`: `135`
- `losses`: `178`
- `win_rate_pct`: `43.131`
- `avg_win_usd`: `18387.45`
- `avg_loss_usd`: `-7497.27`
- `pl_ratio`: `2.4526`
- `expectancy_per_trade_usd`: `3667.07`
- `breakeven_wr_pct`: `28.9641`
- `win_rate_gap_to_breakeven_pp`: `14.1669`
- `sharpe_proxy_per_trade`: `0.1923`
- `trade_curve_maxdd_usd`: `-221668.08`
- `trade_curve_maxdd_pct`: `-221.6681`
- `net_pnl_usd`: `1147791.45`

## Per-market summary
| Market | trades | net_pnl_usd | win_rate_pct | verdict |
|---|---:|---:|---:|---|
| `CL` | 65 | 579,979.94 | 52.31 | profitable |
| `GC` | 56 | -27,110.15 | 33.93 | losing |
| `NQ` | 77 | 225,055.04 | 55.84 | profitable |
| `ZN` | 115 | 369,866.62 | 33.91 | profitable |

- **Profitable markets:** 3 of 4 (CL, NQ, ZN)
- **Losing market:** `GC`

## K-criteria evaluation
| K | fired | value | notes |
|---|---|---|---|
| K1_sharpe_negative | ok | `0.1923` |  |
| K2_expectancy_nonpositive | ok | `3667.07` |  |
| K4_maxdd_excessive | **FIRED** | `-221.6681` | maxdd_excessive, trade_curve_maxdd_pct = -221.67% |
| K6_safety_warnings | ok | `0` |  |
| K7_filter_or_corr_gate | ok | `False` |  |
| K8_sealed_parent_drift | ok | `0` |  |
| K9_insufficient_sample | ok | `313` |  |
| K10_diversification_falsified | DEFERRED | `` |  |
| K11_cap_binding_excessive | ok | `0` |  |
| K12_reject_fast | DEFERRED | `` |  |

- **K-criteria any fired:** `['K4']`
- **K-criteria implied park:** `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`

## C7 closed-enum verdict (parallel with K-criteria)
- **Verdict:** `READY_FOR_LONGER_BACKTEST`
- **Reason:** C7 enum default after FAIL_SAFETY (no safety counter fires) and INSUFFICIENT_SAMPLE (313 >= 100) are excluded
- **Caveats from K-criteria:** `['K4 (maxdd_excessive) fired']`
- **C7 and K-criteria run in parallel:** **True**

Per the Phase-2 plan C7 specification, the closed-enum verdict (FAIL_SAFETY / INSUFFICIENT_SAMPLE / READY_FOR_LONGER_BACKTEST) and the Tier-N K-criteria run in parallel. C7 reports the safety + sample situation. K-criteria report the strategy-performance situation. Both are honest. A C7 verdict of READY_FOR_LONGER_BACKTEST with K4 fired is the canonical signal for PARKED_SAFE_BUT_NOT_MONEY_PROVEN: the run was clean and sufficient, the strategy was tested, and a hard quality threshold (catastrophic DD) was breached.

## Prior buggy P6.5 context (chain integrity)
- Diagnostic result seal: `157ad1bf5a8994ea5364cffcf3f596728778f40ead2eb51615081c72e2b2bde5`
- Diagnostic result commit: `c234bb1`
- Buggy driver byte sha:    `ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394`
- Buggy driver commit:      `ee9aab7`
- Patch plan commit:        `e70b7e4`
- Patch apply commit:       `8e8eb6e`
- Remains committed for history: **True**
- Remains byte-stable: **True**
- Strategy-falsifying: **False**
- Driver-implementation-incomplete: **True**
- Supersedes for strategy interpretation: **True**
- Supersedes for historical record: **False**

The prior P6.5 result (closed_trades_portfolio=0, K9 fired) stays byte-stable and committed. It is NOT a strategy-falsifying result. It is a driver-implementation-incomplete result: the prior driver had an off-by-one in buf_len (max=55 vs entry-trigger required >= 56), so the entry trigger never fired regardless of strategy/data. The P6.5a patch fixed this. The rev2 run with the patched driver supersedes the prior result for STRATEGY INTERPRETATION; the prior result remains as the HISTORICAL RECORD of how the chain reached its empirical answer.

## Main lesson
### Cross-asset Donchian signal shows promise, but max-4 pyramid causes unacceptable drawdown

**Evidence the signal works:**
- 313 closed trades over 10 years across 4 markets (NQ + GC + ZN + CL)
- Expectancy strongly positive: +$3,667 per trade
- Net PnL: +$1,147,791 MNQ-equivalent
- Win rate (43.13%) is +14.17 pp ABOVE the P/L-ratio-implied breakeven (28.96%)
- 3 of 4 markets profitable: CL +$580k (52% WR), NQ +$225k (56% WR), ZN +$370k (34% WR)
- Only GC losing: -$27k (34% WR)
- Sharpe proxy per-trade: +0.192 (positive)
- P/L ratio: 2.45 (winners > 2x average losers in size)
- C3 safety counters all zero (no pyramid state-machine violations, no N-drift, no rollover violations, no stale fills)
- Cap binding events: 0 (s6 cap-bugfix preserved; structurally non-binding at 4 markets x 4 units)
- All in clear contrast to s6 (same-family NQ+ES+YM): s6 WR 14.66% with -2.96 pp gap below breakeven; s7-D1 WR 43.13% with +14.17 pp gap ABOVE breakeven

**Evidence the pyramid is the problem:**
- trade_curve_maxdd_pct: -221.67% of starting capital -- catastrophically exceeds K4 threshold (-50%)
- Mechanism: 197 long + 116 short = 313 positions, many escalating to 4-unit pyramids, produce huge cumulative drawdowns even on a positive-expectancy strategy
- s6 lesson 3 reproduces: 'aggressive 4-unit pyramiding with low win rate AMPLIFIES drawdowns'. s6 saw MaxDD -123% on 191 trades; s7-D1 sees MaxDD -222% on 313 trades. Pyramid amplification scales roughly with trade count even when per-trade expectancy is positive.
- K4 (catastrophic MaxDD safety threshold) firing is the operative reason the candidate parks despite passing K1/K2/K3/K6-K11.

**Interpretation:**
The s7 selection plan's load-bearing hypothesis -- that cross-family diversification (avg pairwise correlation <0.5) would lift the no-filter Donchian above breakeven -- is empirically corroborated at the per-trade economics level (expectancy, Sharpe, WR-gap, 3 of 4 markets profitable). What it is NOT corroborated for is the TRADE-CURVE DRAWDOWN level: pyramid amplification at the locked 4-unit max + low-WR regime produces drawdowns that violate the K4 catastrophic-DD safety threshold. The hypothesis test is decisive on the signal layer (positive); decisive on the sizing layer (K4 fires); ambiguous on whether a no-pyramid or smaller-pyramid variant of the same universe would clear K4.

## Future candidate (INFORMATIONAL ONLY)
- **id:** `s8-cross-asset-donchian-no-pyramid`
- **name:** `s8 cross-asset Donchian no-pyramid (max_units_per_market = 1)`
- **authorized by P7 memo:** **False**
- **authorization required:** Fresh s8 candidate_record_id; fresh sealed chain from selection plan onward; separate operator authorization for each phase.
- **scope clarification:** This entry is INFORMATIONAL ONLY. P7 does not author, plan, or authorize any s8 work. No s8 files created by this memo.

### Rationale
The natural next-candidate thought is to test whether removing pyramid amplification lets the same cross-asset signal pass K4 without sacrificing the positive expectancy. The s7 selection plan §D2 (no-pyramid variant) was pre-scored at 28/40 and remained a fallback. With the s7-D1 result now empirical, the natural s8 candidate is the union of D1 (cross-asset universe) and D2 (no-pyramid).

### Preliminary expected behavior (NOT a claim)
Removing pyramid would:  - Cut trade count by roughly 50-75% (only first units per signal)  - Cut per-trade winners by similar factor (less amplification)  - Cut per-trade losers by similar factor  - SHRINK MaxDD substantially (the K4 problem)  - MAY shrink or preserve expectancy (Faith's pyramid was the alpha-capture mechanism;     without it, winners are truncated)Whether s8 clears K4 AND K1/K2 simultaneously is empirically unknown and would require a fresh sealed chain to test. The s7-D1 result does not predict s8.

## C1-C8 safety attestation (re-affirmed from rev2 result)
- `C1_LiveMode_refusal`: applies; driver has no LiveMode path; status_fields PAUSED + BLOCKED_AT_6_GATES
- `C2_provenance_contract`: applies; engine-truth window enforced at run; 12 prior chain seals + driver byte sha embedded in rev2 result
- `C3_safety_counters`: applies; all counters zero in rev2 run
- `C4_rth_execution_discipline`: applies; per-market RTH windows enforced (NQ/GC/ZN 09:30-16:00 ET, CL 09:30-14:30 ET)
- `C5_event_risk_contract`: PARTIAL; roll/expiry blackout not enforced in this driver (continuous-front-month series stitched by Databento absorbs roll). Documented as limitation in rev2 result and inherited here.
- `C6_diagnostic_output_schema`: applies; rev2 result is the C6 emission; sealed via LESSON_HUNTER_004; this memo references that emission
- `C7_verdict_semantics`: applies; closed-enum verdict = READY_FOR_LONGER_BACKTEST with K4 caveat (parallel with K-criteria implied PARKED_SAFE_BUT_NOT_MONEY_PROVEN)
- `C8_candidate_lifecycle`: this memo recommends transition: IN_SAMPLE_RUN_REV2 -> (P8 authorization required) -> PARKED_SAFE_BUT_NOT_MONEY_PROVEN

## Decision rule applied
**Rule source:** Tier-N spec §14 (Rejection gates) + Phase-2 plan §C7 (verdict semantics) + Phase-2 plan §C8 (candidate lifecycle weak-performance rejection rule)

If a candidate shows decisively negative DD per K4 (>50% trade-curve drawdown) on a meaningful sample (>=100 closed trades, C3 safety counters zero), operator MUST park as PARKED_SAFE_BUT_NOT_MONEY_PROVEN. Do NOT iterate parameters in search of better numbers -- that is optimization, forbidden by the safety template.

**Applied to rev2:**
- `closed_trades_portfolio`: `313`
- `meets_min_100`: `True`
- `trade_curve_maxdd_pct`: `-221.67`
- `exceeds_K4_threshold_50pct`: `True`
- `c3_safety_counters_zero`: `True`
- `applies`: `True`
- `operator_action_per_rule`: `PARK AS PARKED_SAFE_BUT_NOT_MONEY_PROVEN`

## Negative invariants (this turn -- all True/pass)
- `no_new_backtest`: `True`
- `no_cost_stress_matrix_executed`: `True`
- `no_S0_S2_S3_S4_run`: `True`
- `no_code_patched`: `True`
- `no_databento_api_call`: `True`
- `no_data_fetch`: `True`
- `no_qc_call`: `True`
- `no_qc_cloud_submit`: `True`
- `no_network_call`: `True`
- `no_oos_inspection`: `True`
- `no_obsidian_trade_logger_touch`: `True`
- `no_review_queue_mutation`: `True`
- `no_d5_revived`: `True`
- `no_b005_001_revived`: `True`
- `no_nke_revived`: `True`
- `no_s8_files_created`: `True`
- `no_s8_plan_authored`: `True`
- `no_profitability_claim`: `True`
- `no_promotion_to_live`: `True`
- `no_committed_file_modified`: `True`
- `no_prior_sealed_artifact_modified`: `True`
- `prior_buggy_p6_5_result_preserved_byte_stable`: `True`
- `rev2_result_byte_stable`: `True`
- `patched_driver_byte_stable`: `True`
- `amb6_filter_none_invariant_preserved`: `True`
- `s6_portfolio_cap_bugfix_preserved`: `True`

## Operator-side state
- `obsidian_trade_logger_unchanged_through_memo`: **True**

## Authorization gates
- P7 authorizes nothing downstream: **True**
- P8 lifecycle transition requires separate operator authorization: **True**

## Next step
- `operator_authorization_required_for_p8_lifecycle_transition_writing_PARKING_REPORT`

## Seal block (canonical)
- **`report_seal_sha256`**: `5354d3395319e309b953e112c85283bf7753bb3b13c6ae2403eaf502394afef3`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_in_sample_decision_memo.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T20:46:57Z`

*End of in-sample decision memo. PLAN-ONLY. No new backtest. No code patched.
No live promotion. No profitability claim. FRC never granted.*

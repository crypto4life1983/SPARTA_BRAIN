# s10 D1 MNQ+MGC Databento Long-History -- Tier-N Spec Review (SEALED)

**Schema:** `sparta.s10.d1.mnq_mgc_databento_long_history.tier_n_spec_review.v1`
**Phase:** `S10_D1_MNQ_MGC_TIER_N_SPEC_REVIEW`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T00:25:54Z`

## Verdict: `SPEC_REVIEW_PASS_WITH_CLARIFICATIONS`

Both s10-D1 and s10-D2 Tier-N specs are sealed cleanly with all expected sealed-report seals recomputing canonically. Threshold-lock invariants are honored (A7 and K4 documented as domain-adapted / tightened respectively, both permitted under the inherited threshold-lock invariant). DATABENTO_API_KEY handling posture is correct (deny-by-default; key access only at Step 02b operator-side ingest turn; never at controller turn). The 19 RUNTIME_INVARIANTS are all True at SEAL. Live trading, Strategy Lab promotion, brokerage connection, review_queue mutation, and idea_memory mutation all remain BLOCKED. OOS inspection is structurally blocked at every code path until IS verdict ELIGIBLE_FOR_OOS plus a separately authorized OOS-inspection turn. Five clarifications documented (none blockers); summary in the clarifications block. The spec is build-ready conditional on operator routing decision (D1 vs D2 vs both) and Step 02b ingest authorization.

> Review-only turn. No spec modification. No simulator. No
> backtest. No signal. No data fetch. No Databento call. No
> DATABENTO_API_KEY access. No live trading.

---

## 1. Files read (read-only)

| Tag | Path | Exists | sha256 (first 16) | bytes |
|---|---|---|---|---|
| `d1_tier_n_spec` | `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md` | True | `59002adb041eac18` | 34,665 |
| `d1_tier_n_spec_plan` | `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_plan.md` | True | `0d07fa1cc89f4843` | 27,983 |
| `d1_tier_n_spec_draft` | `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec_DRAFT.md` | True | `bcbf616c41ac912e` | 28,715 |
| `d1_probe_memo_json` | `reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.json` | True | `76dcb833f89d3044` | 11,306 |
| `d1_probe_memo_md` | `reports/external_research_hunter/s10_d1_micro_availability_probe_result_memo.md` | True | `006d39df196f3780` | 17,420 |
| `t8_family_park_memo_json` | `reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.json` | True | `5ba11ea7f51e693d` | 12,675 |
| `t8_family_park_memo_md` | `reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.md` | True | `277beba2eb6a8a56` | 16,452 |
| `availability_attestation_json` | `reports/external_research_hunter/s10_micro_futures_availability_attestation_analysis.json` | True | `64e34f3831ba6b55` | 19,892 |
| `availability_attestation_md` | `reports/external_research_hunter/s10_micro_futures_availability_attestation_analysis.md` | True | `60e099b61bbdb66e` | 14,371 |
| `successor_selection_plan_json` | `reports/external_research_hunter/s10_micro_futures_successor_selection_plan.json` | True | `bf4a841f4fe48dec` | 21,288 |
| `successor_selection_plan_md` | `reports/external_research_hunter/s10_micro_futures_successor_selection_plan.md` | True | `f91ff5bab713aa5e` | 15,961 |
| `d2_plan_lock_json` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_plan_lock.json` | True | `a9490dd6a2e9343d` | 15,152 |
| `d2_plan_lock_md` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_plan_lock.md` | True | `92a481e2b784cd45` | 11,463 |
| `d2_tier_n_spec_json` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_tier_n_spec.json` | True | `1a7850dbde36ab8b` | 22,585 |
| `d2_tier_n_spec_md` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_tier_n_spec.md` | True | `9ccef4a502a18fce` | 9,146 |

## 2. Sealed reports verified (canonical seal recomputation)

| Tag | seal field present | recorded seal (first 16) | recomputed seal (first 16) | match |
|---|---|---|---|---|
| `d1_probe_memo_json` | False | `` | `` | None |
| `t8_family_park_memo_json` | True | `4f375af7a46d0590` | `4f375af7a46d0590` | True |
| `availability_attestation_json` | True | `417ed6c7b4e177e0` | `417ed6c7b4e177e0` | True |
| `successor_selection_plan_json` | True | `007110ff5a57dd04` | `007110ff5a57dd04` | True |
| `d2_plan_lock_json` | True | `ba8bf954d44b373c` | `ba8bf954d44b373c` | True |
| `d2_tier_n_spec_json` | True | `f5ca5ee63024e9c8` | `f5ca5ee63024e9c8` | True |

**Seal verification summary:**
- Total JSON reports examined: 6
- With seal field present and matching: 5
- With no seal field (expected for raw probe memo): 1
- With seal field but mismatch: 0

## 3. s10-D1 candidate summary

- **candidate_record_id:** `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`
- **Family:** F1 long_plus_short_bi_directional_donchian_trend_no_pyramid_atr_stop
- **Mechanic at seal:** trend_following (Donchian breakout; no pyramid; ATR stop)
- **Trend/MeanRev:** trend (long+short bi-directional Donchian-N breakout)
- **Symbols:** `['MNQ.c.0', 'MGC.c.0']`
- **Excluded:** `['MCL.c.0 (per probe memo: unreliable before 2021; excluded to preserve clean common-history window starting in 2019)']`
- **Data source:** Databento Historical API; dataset GLBX.MDP3; schema ohlcv-1d; stype_in continuous
- **IS window:** `['2019-05-13', '2023-12-29']` (~4.6 years; ~1140 trading days/symbol)
- **OOS window (blocked at IS):** `['2024-01-02', '2025-12-30']` (~2.0 years)
- **Phase at seal:** `TIER_N_SPEC_SEALED_BUILD_NOT_AUTHORIZED`
- **Diagnostic only:** **True**
- **Advisory label permanent:** `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- **19 RUNTIME_INVARIANTS all True at SEAL:** **True**
- **FRC granted:** **False**

### Locked parameters (13 at DA = default A)

| Parameter | Locked value |
|---|---|
| `DONCHIAN_ENTRY_WINDOW_N` | `20` |
| `DONCHIAN_EXIT_WINDOW_M` | `10` |
| `ATR_STOP_WINDOW_P` | `20` |
| `ATR_STOP_MULTIPLIER_K` | `2.0` |
| `SIDE` | `long_plus_short_bi_directional` |
| `PER_TRADE_RISK_PCT_PORTFOLIO_EQUITY` | `0.01` |
| `PER_SYMBOL_CONTRACT_CAP_PER_SIGNAL` | `1` |
| `DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN` | `0.3` |
| `K4_TRADE_CURVE_MAX_DRAWDOWN_PCT_THRESHOLD` | `0.3` |
| `PER_SYMBOL_MIN_TRADE_COUNT_OVER_IS` | `30` |
| `START_CASH_USD` | `100000` |
| `WARMUP_DAYS` | `220` |
| `OUTPUT_SCHEMA_NAME` | `sparta.s10.mnq_mgc.trend_no_pyramid.diagnostic_run_report.v1` |

### Cost-stress matrix S0/S1/S2/S3

| Tier | commission/contract USD | slippage ticks one-way |
|---|---|---|
| S0 | 0.0 | 0.0 |
| S1 | 0.85 | 0.5 |
| S2 | 0.85 | 1.5 |
| S3 | 0.85 | 3.0 |

### Gates and thresholds
- K9 portfolio closed-trades threshold: 100
- Diversification thresholds: A7 >= 1.5, K10 <= 0.5
  - Note: A7 lowered from inherited 2.5 to 1.5 because universe has only 2 symbols (vs 4 in s7/s9 ETF-proxy)
- DR1-DR10 locked: True
- DR11 status: NOT_CARRIED (F1 has no leverage cap; single-contract per signal makes leverage-cap-bound-rate undefined; B006_002 DR11 specifically for vol-targeting)
- DR precedence chain: `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5`

### Closed verdict enum

- `REJECT_FAST`
- `INCONCLUSIVE_HOLD`
- `ELIGIBLE_FOR_HUMAN_REVIEW`
- `REQUEST_FULL_PREREGISTRATION_REVIEW`
- `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- `HARD_FAIL_VOIDED`
- `ELIGIBLE_FOR_OOS`

## 4. DATABENTO_API_KEY handling posture

- `review_only_this_turn`: **True**
- `no_key_access_this_turn`: **True**
- `spec_section_4_attestation`: **reads DATABENTO_API_KEY from environment ONLY at Step 02b operator-side fetch turn (NOT at controller turn); never echoed, logged, or saved**
- `controller_side_databento_call_locked_off`: **True**
- `future_data_fetch_requires_separate_authorization`: **True**
- `deny_by_default_protocol_alignment`: **True**

## 5. Threshold-lock invariant verification

- `A1_min_closed_trades_inherited_100`: **True**
### `A7_effective_independent_bets_min_changed`
- `inherited_value`: 2.5
- `s10_d1_value`: 1.5
- `rationale`: 2-symbol universe vs s7/s9 4-symbol; documented in spec section 13
- `is_loosening`: False
- `is_tightening_or_neutral`: domain-adapted; not a relaxation of the protocol threshold itself but a fresh value for a different universe size
### `K4_max_drawdown_pct_changed`
- `inherited_value_pct`: 50.0
- `s10_d1_value_pct`: 30.0
- `rationale`: stricter; documented in spec section 9 DA9 = A
- `is_loosening`: False
- `is_tightening`: True
- `tightening_allowed_under_threshold_lock_invariant`: True
- `K9_min_closed_trades_inherited_100`: **True**
- `K10_avg_pairwise_dependence_max_inherited_0_50`: **True**
- `DR2_S2_S3_degradation_threshold_inherited_pattern`: **True**
- `DR3_zero_cost_only_survival_inherited`: **True**
- `DR5_S0_to_S1_edge_negative_inherited`: **True**
### `DR9_redefined_for_2_symbol_universe`
- `original_DR9_in_s7_s9`: single-CSV continuity check
- `s10_d1_DR9`: gap > 5 trading days on either symbol; OR > 5 missing observations on consolidated date set
- `redefinition_documented_in_spec_section_11`: True
- `DR11_carved_out_for_F1`: **leverage-cap-bound-rate undefined for single-contract no-leverage mechanic; DR11 in B006_002 specifically for vol-targeting with leverage cap**
- `oos_blocked_until_is_verdict_ELIGIBLE_FOR_OOS`: **True**
- `live_trading_blocked_at_6_gates`: **True**
- `FRC_never_granted`: **True**

## 6. D1 / D2 / t8 / selection-plan relationship clarification

**Summary:** The s10 thread comprises TWO SIBLING tracks both at TIER_N_SPEC_SEALED_BUILD_NOT_AUTHORIZED phase. The next-track selection plan accepted in commit 2ec9330 recommended T7-Path-A which maps to the s10-D1 micro-futures direction. A subsequent availability attestation analysis (commit 2a53b19) identified MCL as sample-limited (only available from 2021 onward); D1 was then re-scoped to MNQ+MGC only (excluding MCL) and sealed as a 2-symbol micro-futures spec with ~4.6 year IS. The same attestation analysis ALSO recommended D2 (higher-capital successor on the original 4-symbol full-futures universe). D2 was subsequently sealed as a separate sibling Tier-N spec at commit d6cc4512 with starting_cash $500,000 (single delta from s8-D1).

### s10-D1 track
- `track_id`: `S10-D1`
- `candidate_record_id`: `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`
- `universe`: `MNQ.c.0 + MGC.c.0 (2-symbol micro futures)`
- `is_window`: `2019-05-13 to 2023-12-29 (~4.6 years)`
- `starting_cash_usd`: `100000`
- `mechanic`: `F1 long+short bi-directional Donchian-20 / Exit-10 / ATR-20 x 2.0`
- `tier_n_spec_path`: `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md`
- `tier_n_spec_sha256`: `59002adb041eac18f63ce0de56951f3ea61f94ddbca33fbedc5fcf71c615692f`
- `tier_n_spec_seal_commit`: `90404293a5f17ab4a0ab4b57085f9ca9a76c5df5`
- `phase`: `TIER_N_SPEC_SEALED_BUILD_NOT_AUTHORIZED`
- `alignment_with_accepted_selection_plan_T7_Path_A`: `True`

### s10-D2 track
- `track_id`: `S10-D2`
- `canonical_record_id`: `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
- `universe`: `NQ.c.0 + GC.c.0 + ZN.c.0 + CL.c.0 (4-symbol full futures; s8-D1 preserved)`
- `is_window_inherited_from_s8_d1`: `True`
- `starting_cash_usd`: `500000`
- `single_delta_from_s8_d1`: `starting_cash_mnq_equivalent ($500K vs s8-D1 $100K)`
- `mechanic`: `byte-equivalent to s8-D1: Donchian-55 entry / Donchian-20 exit / no-pyramid / 2N ATR stop`
- `tier_n_spec_path`: `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_tier_n_spec.{json,md}`
- `tier_n_spec_seal`: `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
- `tier_n_spec_seal_commit`: `d6cc4512263792ada4cf146d740a6817a3bb93e3`
- `phase`: `TIER_N_SPEC_SEALED_BUILD_NOT_AUTHORIZED`
- `rationale`: `addresses s8-D1's NQ/GC/CL contracts-below-1 sizing-skip cascade by raising starting capital above the empirical $476K NQ-clearing threshold`

### t8 family-park memo
- `path`: `reports/external_research_hunter/t8_spy_tlt_gld_uso_2014_2022_family_park_memo.{json,md}`
- `seal`: `4f375af7a46d0590...`
- `role`: `Formal family-level park of SPY/TLT/GLD/USO 2014-2022 simple canonical mechanics. Establishes the first-principles burden the s10-D1 spec satisfies (R5_AB_a, R5_AB_b in spec section 2).`
- `supports_d1_build`: `True`
- `supports_d2_build`: `True`

### Accepted next-track selection plan (commit 2ec9330)
- `commit`: `2ec9330`
- `recommendation`: `T8 + T7-Path-A`
- `hygiene_review_commit`: `9f13e55`
- `maps_to_s10_d1`: `True`
- `alignment_notes`: `The accepted T7-Path-A direction matches the s10-D1 spec's 2-symbol MNQ+MGC long-history universe (after MCL was dropped per availability attestation). The accepted recommendation also formally references the T8 family-park of SPY/TLT/GLD/USO, which is now sealed at the t8 memo.`

**Sibling-tracks attestation:** D1 and D2 are independent sibling Tier-N specs; neither supersedes the other. Both are sealed and build-not-authorized. The operator may authorize either build (or both, sequentially or in parallel) under separate authorization. The s10 micro-futures successor selection plan (seal 007110ff5a57dd04) recommended D1 at 58/64 with D2 as fallback; the subsequent availability attestation analysis (seal 417ed6c7b4e177e0) recommended D2 as primary after MCL was identified as sample-limited; the actual D1 spec was then re-designed to drop MCL (producing the 2-symbol MNQ+MGC variant) and sealed in parallel to D2.

## 7. Blockers and clarifications

**Blockers count:** 0
**Clarifications count:** 5

**No blockers identified.**

### Clarifications

**1. spec_format_asymmetry** (blocker: False)

s10-D1 Tier-N spec is markdown-only (sealed via in-document attestation in spec section 20 and commit 90404293). The s10-D2 Tier-N spec has both .json and .md forms with canonical seal field f5ca5ee63024e9c8. Asymmetry is documentational, not structural; D1's seal record is the markdown content plus the git commit metadata. Future P2 ingest authorization may produce a companion JSON for the D1 spec.

**2. A7_threshold_domain_adaptation** (blocker: False)

A7_EFFECTIVE_INDEPENDENT_BETS_MIN was 2.5 in the s7/s9 ETF-proxy 4-symbol universe. The s10-D1 spec sets A7 = 1.5 for the 2-symbol MNQ+MGC universe. This is a domain-adapted value, not a loosening of an inherited threshold (the threshold semantics depend on universe size). Documented in D1 spec section 13.

**3. K4_tightened_from_50pct_to_30pct** (blocker: False)

K4_TRADE_CURVE_MAX_DRAWDOWN_PCT_THRESHOLD was 50% in s7/s9. The s10-D1 spec sets it to 30%, which is STRICTER. Tightening is allowed under the inherited threshold-lock invariant (only loosening is forbidden post-seal). Documented in D1 spec section 9 DA9 = A.

**4. d1_and_d2_both_sealed_build_not_authorized** (blocker: False)

Both D1 (MNQ+MGC micro) and D2 (NQ/GC/ZN/CL full at $500K) Tier-N specs are sealed simultaneously and build-not-authorized. The operator should clarify whether (a) D1 is the primary build target per the accepted T7-Path-A recommendation, (b) D2 is the primary target per the availability attestation analysis, or (c) both should proceed in parallel. This is a routing decision for the next operator authorization, not a defect in either spec.

**5. build_authorization_required** (blocker: False)

Both Tier-N specs are at TIER_N_SPEC_SEALED_BUILD_NOT_AUTHORIZED. Proceeding requires a separately authorized turn (e.g., 'Authorize s10 D1 MNQ+MGC operator-side data ingest at Step 02b only', or 'Authorize s10 D2 NQ/GC/ZN/CL operator-side data ingest at Step 02b only'). The Step 02b phase is the only phase that touches DATABENTO_API_KEY; the controller-side build phases use the sealed local cache produced by Step 02b.

## 8. Parallel-session commits in chain (chronological)

| Commit | Subject |
|---|---|
| `530b545` | Add next research-track selection plan after s7 d1 park |
| `5c13821` | Add ETF-proxy family park memo and s10 d1 MNQ MGC plan |
| `2a53b19` | Seal S10 availability attestation analysis |
| `d6cc4512` | Seal S10-D2 cross-asset Donchian no-pyramid reparam-cap Tier-N spec |
| `90404293` | Seal s10 D1 MNQ MGC Tier-N spec |

## 9. Negative invariants (all True)

- `no_CLAUDE_md_modified`: **True**
- `no_RUNBOOK_modified`: **True**
- `no_b005_b006_artifact_modified`: **True**
- `no_backtest_run`: **True**
- `no_branch_change`: **True**
- `no_branch_creation`: **True**
- `no_brokerage_connection`: **True**
- `no_candidate_promotion`: **True**
- `no_data_fetch`: **True**
- `no_databento_api_key_access`: **True**
- `no_databento_call`: **True**
- `no_docs_decisions_md_modified`: **True**
- `no_git_push`: **True**
- `no_gitignore_modified`: **True**
- `no_lessons_md_staged_or_modified`: **True**
- `no_live_trading`: **True**
- `no_network_io`: **True**
- `no_paper_order_placed`: **True**
- `no_pipeline_manifest_modified`: **True**
- `no_production_idea_memory_mutation`: **True**
- `no_real_order_placed`: **True**
- `no_review_queue_mutation`: **True**
- `no_s10_artifact_modified`: **True**
- `no_s7_artifact_modified`: **True**
- `no_s9_artifact_modified`: **True**
- `no_signal_computation`: **True**
- `no_simulator_run`: **True**
- `no_spec_modification_this_turn`: **True**
- `no_strategy_lab_invoked`: **True**
- `no_strategy_lab_promotion`: **True**
- `no_vendor_sdk_import`: **True**
- `no_yahoo_finance_call`: **True**
- `no_yfinance_call`: **True**

## 10. Status

- Trading status: `PAUSED`
- Live status: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

## 11. Labels

- `S10_D1_MNQ_MGC_TIER_N_SPEC_REVIEW_COMPLETE`
- `SPEC_REVIEW_VERDICT_SPEC_REVIEW_PASS_WITH_CLARIFICATIONS`
- `D1_AND_D2_ARE_SIBLING_TRACKS_BOTH_SEALED_BUILD_NOT_AUTHORIZED`
- `DATABENTO_API_KEY_DENY_BY_DEFAULT_POSTURE_CONFIRMED`
- `OOS_BLOCKED_AT_IS_PHASE`
- `TRADING_PAUSED`
- `LIVE_BLOCKED_AT_6_GATES`
- `FRC_NEVER_GRANTED`

## 12. Seal verification

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**Review sealed. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**


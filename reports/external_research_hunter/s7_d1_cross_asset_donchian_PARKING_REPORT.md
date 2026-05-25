# s7 D1 Cross-Asset Donchian No-Filter -- PARKING REPORT (SEALED)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_PARKING_REPORT.v1`
**Status:** `SEALED`
**candidate_record_id:** `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl`
**candidate_operational_status:** **`PARKED_SAFE_BUT_NOT_MONEY_PROVEN`**
**Park date (UTC):** `2026-05-25T21:01:52Z`
**Permanence:** `PERMANENT -- s7-d1 not to be revived`

> PARKING ACTION. No code. No backtest. No optimization. No OOS inspection.
> No strategy parameter changed. All sealed parents BYTE-STABLE.
> Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`.
> FRC never granted. No profitability claim.
> NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT continues to hold.

## Lifecycle Transition
- **from:** `IN_SAMPLE_DECISION_MEMO_SEALED_RECOMMEND_PARK`
- **to:**   **`PARKED_SAFE_BUT_NOT_MONEY_PROVEN`**
- **effective_at_utc:** `2026-05-25T21:01:52Z`
- **permanence:** `PERMANENT -- s7-d1 not to be revived`
- **K-criteria triggering park:** `['K4']`
- **K-criteria implied park:** `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- **C7 closed-enum verdict:** `READY_FOR_LONGER_BACKTEST`
- **C7 and K-criteria parallel:** **True**
- **Operative rule source:** Tier-N spec §14 (K-criteria) + Phase-2 plan §C7/C8 (verdict + lifecycle)

## Inheritance chain (drift=0; 13 s7-d1 chain artifacts + 16 parent shas)
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
- Decision memo seal:                  `5354d3395319e309b953e112c85283bf7753bb3b13c6ae2403eaf502394afef3`
- Patched driver byte sha:             `8741bc5182e227336a5c0e75afa9d037fc1c633b12eae97577ef98b6eea31ea9`
- Prior buggy driver byte sha:         `ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394`
- Parent sha drift at parking:         **0**
- All 13 s7-d1 chain artifacts byte-stable: **True**

## Parking rationale
- **C7 verdict:** `READY_FOR_LONGER_BACKTEST`
- **K fire:** `['K4']`
- **K4 reason:** maxdd_excessive, trade_curve_maxdd_pct = -221.67% vs threshold -50%
- **closed_trades_portfolio:** 313
- **expectancy_per_trade_usd:** $3,667.07
- **net_pnl_usd:** $1,147,791.45
- **win_rate_pct:** 43.13%
- **pl_ratio:** 2.45
- **breakeven_wr_pct:** 28.96%
- **win_rate_gap_to_breakeven_pp:** +14.17 pp ABOVE breakeven
- **sharpe_proxy_per_trade:** +0.1923
- **trade_curve_maxdd_pct:** -221.67%
- **C3 safety counters all zero:** **True**
- **AMB6 filter NONE invariant preserved:** **True**
- **s6 portfolio-cap-bugfix preserved:** **True**

### Per-market breakdown
| Market | trades | net_pnl_usd | win_rate_pct |
|---|---:|---:|---:|
| `CL` | 65 | 579,979.94 | 52.31 |
| `GC` | 56 | -27,110.15 | 33.93 |
| `NQ` | 77 | 225,055.04 | 55.84 |
| `ZN` | 115 | 369,866.62 | 33.91 |

- **Profitable markets (3 of 4):** `['CL', 'NQ', 'ZN']`
- **Losing market:** `GC`

### Main lesson
**Cross-asset Donchian signal shows promise, but max-4 pyramid causes unacceptable drawdown**

## Prior buggy P6.5 context (preserved for chain integrity)
- Diagnostic result seal: `157ad1bf5a8994ea5364cffcf3f596728778f40ead2eb51615081c72e2b2bde5`
- Diagnostic result commit: `c234bb1`
- Buggy driver byte sha:    `ae0687559bf3d1734121fff32fb6d6d1752b95ade54c7da4c0f548bd78333394`
- Buggy driver commit:      `ee9aab7`
- Patch plan commit:        `e70b7e4`
- Patch apply commit:       `8e8eb6e`
- Rev2 run commit:          `6048075`
- Decision memo commit:     `c4f674d`
- Remains committed for history: **True**
- Remains byte-stable: **True**
- Strategy-falsifying: **False**
- Driver-implementation-incomplete: **True**
- Rev2 supersedes for strategy interpretation: **True**
- Rev2 does NOT invalidate prior for historical record: **True**

The prior P6.5 result (committed at c234bb1; 0 closed trades; K9 INSUFFICIENT_SAMPLE) remains byte-stable. It was driver-implementation-incomplete (buf_len off-by-one capped the deque at 55 vs the entry trigger required >= 56), NOT strategy-falsifying. The P6.5a patch fixed this; the rev2 result (committed at 6048075; 313 trades; K4 fires) is the operative strategy interpretation. Both results are preserved in this parking report's chain for full provenance.

## Revival rule
- **s7-d1 revival permitted:** **False**
- **s7-d1 revival requires:** Fresh s8+ candidate_record_id and full fresh sealed chain (selection plan -> Tier-N spec -> plan-lock -> Phase-2 plan -> BUILD -> smoke -> in-sample -> decision memo -> parking)
- **Fresh chain required:** True
- **Old run records stay intact:** True
- **No iteration of s7-d1 parameters permitted:** True
- **Rule source:** Phase-2 plan §C8 candidate lifecycle 'revival' clause; s7 selection plan §'any s7 strategy requires a fresh candidate_record_id and fresh sealed chain' applied recursively

## s8 informational only
- **id:** `s8-cross-asset-donchian-no-pyramid`
- **Natural follow-up:** True
- **Authorized by P8 parking report:** **False**
- **s8 files created by this report:** `[]`
- **Operator action required for s8:** If operator chooses to pursue s8, a fresh sealed chain must be authored starting from a new s8 selection memo or directly from a fresh s8 Tier-N spec authoring authorization. No s8 work is pre-authorized by this parking report.
- **Scope clarification:** INFORMATIONAL ONLY. No s8 candidate_record_id reserved. No s8 spec authored. No s8 BUILD scope defined.

## Permanent attributes (unchanged by parking, per Phase-2 plan §C8)
- DIAGNOSTIC_ONLY_NOT_LIVE_GRADE secondary label
- All advisory labels declared in Tier-N spec
- 6-gate live-block
- FRC status (never granted)
- All sealed-chain artifacts (13 prior seals) byte-stable
- Driver byte sha (patched: 8741bc51...) byte-stable
- Prior buggy driver byte sha (ae068755...) preserved in chain history

## Sibling parking chains (preserved byte-stable)
| Candidate | park_status | parking_seal |
|---|---|---|
| `s2_NKE_options_wheel` | `PARKED (reference in HUNTER_BRAIN_LESSONS.md)` | -- |
| `s3_MNQ_daily_range_breakout` | `PARKED` | `1f557888e1212d6ffe0e305ac43308977f618db7473b22c90e407fe805d3f7ad` |
| `s4_turtle_system_1_NQ_c_0` | `PARKED` | `8cda3ca644524cd558cc3a1291a869d983a8c5fae9c1d0f15d6e56ba266a1cb4` |
| `s5_donchian_no_filter_NQ_c_0` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` | `6c308b42da6854d5dd3f8e8936fb5299666dae3158904bec65ec6458156f234c` |
| `s6_multi_market_donchian_no_filter` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN` | `f6953c1fb3c334d34572aa7dac29317b4ff412bf3648db62276707ef9de2894a` |
| `s7_d1_cross_asset_donchian_no_filter` | `PARKED_SAFE_BUT_NOT_MONEY_PROVEN (THIS REPORT)` | `(self -- to be sealed below)` |

- **Total parked candidates after s7-d1:** **6**
- **No money-proven strategy in chain:** **True**

## No-Live status (PERMANENT)
- `trading_status`: `PAUSED`
- `live_status`: `BLOCKED_AT_6_GATES`
- `frc_granted`: `False`
- `live_promotion_path_closed`: `True`
- `six_gate_live_block_forever`: `True`
- `diagnostic_only_label_permanent`: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `secondary_label_permanent`: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `no_profitability_claim`: `True`
- `live_promotion_never`: `True`
- `no_live_trading_approval`: `True`
- `no_paper_trading_approval`: `True`

## Negative invariants (parking action)
- `all_sealed_parents_byte_stable`: `True`
- `lifecycle_transitioned_to_parked_safe_but_not_money_proven`: `True`
- `parking_action_authored_code`: `False`
- `parking_action_ran_backtest`: `False`
- `parking_action_called_databento_api`: `False`
- `parking_action_called_qc`: `False`
- `parking_action_made_network_call`: `False`
- `parking_action_fetched_data`: `False`
- `parking_action_inspected_oos`: `False`
- `parking_action_touched_obsidian_trade_logger`: `False`
- `parking_action_mutated_review_queue`: `False`
- `parking_action_modified_any_committed_file`: `False`
- `parking_action_modified_any_prior_sealed_artifact`: `False`
- `parking_action_changed_k_threshold`: `False`
- `parking_action_loosened_any_threshold`: `False`
- `parking_action_changed_strategy_parameter`: `False`
- `parking_action_changed_amb6_filter_invariant`: `False`
- `parking_action_changed_s6_cap_bugfix`: `False`
- `parking_action_revived_d5`: `False`
- `parking_action_revived_b005_001`: `False`
- `parking_action_revived_nke`: `False`
- `parking_action_created_s8_files`: `False`
- `parking_action_authored_s8_plan`: `False`
- `parking_action_claimed_profitability`: `False`
- `parking_action_proposed_live_path`: `False`
- `parking_action_promoted_to_live`: `False`
- `parking_action_granted_frc`: `False`
- `parking_action_iterated_s7_d1_parameters`: `False`
- `k4_fired_as_strategy_observation`: `True`
- `c3_safety_zero_in_rev2`: `True`
- `prior_buggy_p6_5_result_preserved`: `True`
- `rev2_result_byte_stable`: `True`
- `patched_driver_byte_stable`: `True`

## Obsidian-trade-logger preserved through parking turn
- start == end: **True**

## Status fields
- `candidate_operational_status`: `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- `candidate_record_id`: `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl`
- `trading_status`: `PAUSED`
- `live_status`: `BLOCKED_AT_6_GATES`
- `frc_granted`: `False`
- `live_promotion_path_closed`: `True`
- `schema_status`: `SEALED`
- `backtest_diagnostic_only`: `True`

## Labels
- `EXTERNAL_CLAIM_ONLY`
- `NEEDS_VERIFICATION`
- `NOT_A_SIGNAL`
- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `NO_FRC_GRANTED`
- `S7_D1_PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- `K4_FIRED_CATASTROPHIC_MAXDD`
- `C7_VERDICT_READY_FOR_LONGER_BACKTEST_WITH_K4_CAVEAT`
- `CROSS_ASSET_SIGNAL_POSITIVE_PYRAMID_DD_UNACCEPTABLE`
- `313_CLOSED_TRADES_POSITIVE_EXPECTANCY_NEGATIVE_K4`
- `PRIOR_BUGGY_P6_5_PRESERVED_FOR_HISTORY`
- `REV2_PATCHED_DRIVER_OPERATIVE`
- `PARKING_ACTION_NO_CODE_NO_BACKTEST`
- `S7_D1_SEALED_CHAIN_BYTE_STABLE_PERMANENTLY`
- `S2_S6_SIBLING_PARKED_CHAINS_PRESERVED`

## Advisory labels (permanent)
- `DONCHIAN_TREND_WITHOUT_SYSTEM_1_FILTER`
- `MULTI_DAY_TREND_FOLLOWING`
- `VOLATILITY_ADJUSTED_POSITION_SIZING`
- `PYRAMIDING_ENABLED_4_UNIT_05N_SPACING`
- `MULTI_MARKET_PORTFOLIO_CROSS_ASSET_4_MARKETS_NQ_GC_ZN_CL`
- `EXTERNAL_RESEARCH_HUNTER_S7_D1_CANDIDATE_PARKED`
- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `NO_LIVE_PROMOTION_PATH`
- `NO_FRC_GRANTED`

## Final status list
- `S7_D1_CROSS_ASSET_DONCHIAN_NO_FILTER_PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- `LIFECYCLE_TRANSITION_IN_SAMPLE_DECISION_MEMO_SEALED_RECOMMEND_PARK_TO_PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- `K4_FIRED_TRADE_CURVE_MAXDD_PCT_-221.67_EXCEEDS_THRESHOLD_-50.0`
- `C7_VERDICT_READY_FOR_LONGER_BACKTEST_WITH_K4_CAVEAT`
- `C7_AND_K_CRITERIA_RUN_IN_PARALLEL_PER_PHASE2_PLAN`
- `CLOSED_TRADES_PORTFOLIO_313_EXPECTANCY_+3667_USD_NET_PNL_+1147791_USD`
- `WIN_RATE_43.13_PCT_PL_RATIO_2.45_SHARPE_PROXY_+0.192`
- `WIN_RATE_GAP_TO_BREAKEVEN_+14.17_PP_ABOVE_BREAKEVEN_OF_28.96_PCT`
- `3_OF_4_MARKETS_PROFITABLE_CL_NQ_ZN_GC_LOSING`
- `C3_SAFETY_COUNTERS_ALL_ZERO`
- `CAP_BINDING_EVENTS_0`
- `AMB6_FILTER_NONE_INVARIANT_PRESERVED`
- `S6_PORTFOLIO_CAP_BUGFIX_PRESERVED`
- `PRIOR_BUGGY_P6_5_RESULT_PRESERVED_BYTE_STABLE_AT_C234BB1`
- `REV2_PATCHED_DRIVER_RESULT_OPERATIVE_AT_6048075`
- `DECISION_MEMO_RECOMMENDED_PARK_AT_C4F674D`
- `ALL_13_S7D1_CHAIN_ARTIFACTS_BYTE_STABLE_AT_PARKING`
- `PARENT_SHA_DRIFT_ZERO_AT_PARKING`
- `S7_D1_REVIVAL_PERMANENTLY_BLOCKED`
- `REVIVAL_REQUIRES_FRESH_S8_OR_LATER_CANDIDATE_RECORD_ID`
- `S8_INFORMATIONAL_ONLY_NOT_AUTHORIZED_BY_P8`
- `NO_S8_FILES_CREATED_BY_THIS_PARKING_REPORT`
- `TRADING_STATUS_PAUSED_PERMANENT`
- `LIVE_STATUS_BLOCKED_AT_6_GATES_PERMANENT`
- `FRC_NEVER_GRANTED`
- `NO_PROFITABILITY_CLAIM`
- `NO_LIVE_TRADING_APPROVAL`
- `NO_PAPER_TRADING_APPROVAL`
- `S2_S3_S4_S5_S6_SIBLING_PARKED_CHAINS_PRESERVED`
- `TOTAL_PARKED_CANDIDATES_AFTER_S7_D1_6`
- `NO_MONEY_PROVEN_STRATEGY_IN_S7_CHAIN`

## Authorization gates
- P8 authorizes nothing downstream: **True**
- No further s7-d1 work authorized: **True**
- Any s8+ requires separate authorization: **True**

## Next step (none required in s7-d1 chain)
- `no_next_step_in_s7_d1_chain; chain is complete; operator owns any decision to start s8+ as a fresh candidate`

## Closing note
s7-d1 cross-asset Donchian no-filter (NQ+GC+ZN+CL) is permanently parked as PARKED_SAFE_BUT_NOT_MONEY_PROVEN. The cross-asset signal works at the per-trade economics level (positive expectancy, positive Sharpe, +14.17 pp WR gap to breakeven, 3 of 4 markets profitable). The 4-unit pyramid mechanic produces catastrophic 221% drawdown that breaches the K4 safety threshold. The chain is complete and honest: the buggy P6.5 result is preserved as the historical record of the implementation journey; the rev2 result is the strategy answer; this parking report seals the lifecycle. Six candidates now parked in the s2-s7 chain. No money-proven strategy. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted.

## Seal block (canonical)
- **`report_seal_sha256`**: `551fdce46c0e373eac03d79597d6439d740ae56f4a0ba9f2c6f2b39d25974b32`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_PARKING_REPORT.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T21:01:52Z`

*End of parking report. s7-D1 chain complete. PARKED_SAFE_BUT_NOT_MONEY_PROVEN.
No code. No backtest. No live promotion. No profitability claim. FRC never granted.*

# S12-D1 P1 Plan-Lock (SEALED)

**Schema:** `sparta.s12.d1.mnq_c0.donchian_15_8.p1_plan_lock.v1`
**Phase:** `S12_D1_P1_PLAN_LOCK`
**Phase prefix:** `PHASE2-S12-D1-P1`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T15:05:00Z`
**Authorization:** *"Authorize s12 D1 P1 plan-lock spec only."*

**Candidate:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`

---

## 0. Anchor — sealed Tier-N spec

| Field | Value |
|---|---|
| Sealed spec commit | `9ce4d66e687943dacde8da233b39faa71b56ce6f` |
| `report_seal_sha256` | `422bbbff75f24816ec743104b730178298de36f395e43ac126ba52a7d82c03a1` |
| `canonical_docs_md_sha256` | `793b181e2e6beb31` |
| `companion_md_sha256` | `368cd097584518e1` |
| Bit-identical at HEAD | True |

This P1 plan-lock **anchors to this session's sealed spec at `9ce4d66`**. The parallel session maintains a parallel S12-D1 chain (SEAL `66bbbd1` → P1 `d8bd359`) at distinct non-colliding paths; that chain is **not anchored or modified** by this P1.

---

## 1. Locked universe

| Field | Value |
|---|---|
| Universe kind | `single_fixed_instrument_continuous_micro_futures` |
| Symbols | `{MNQ.c.0}` (1 symbol) |
| Universe widening post-seal | **FORBIDDEN** |
| Symbol substitution post-seal | **FORBIDDEN** |

---

## 2. Locked mechanic family

| Field | Value |
|---|---|
| Family ID | F1 |
| Description | Long+Short Bi-Directional Donchian Trend, No Pyramid, ATR(20)-Based Stop, Single MNQ.c.0 Contract Per Signal |
| **Donchian entry N** | **15 days** |
| **Donchian exit M** | **8 days** |
| Signal direction | Long+Short bi-directional |
| Pyramid mechanism | NONE / `max_units_per_market = 1` |
| Locked at PLAN | True |
| Locked at SEAL | True |
| Plan-lock does not reopen | True |

---

## 3. Locked capital + risk

| Field | Value |
|---|---|
| **`START_CASH_USD`** | **`$100,000`** (DA4=B) |
| DA4 rationale | DR10 turnover-cost-explosion risk mitigation under Donchian-15/8; halves contracts-per-trade for given ATR |
| Per-trade risk | 1.0% of portfolio equity |
| ATR stop window | Wilder ATR(20) |
| ATR stop multiplier | 2.0 (2N stop) |
| K4 max-drawdown fraction | 0.50 (= **$50,000** absolute) |

---

## 4. Locked DA-register

| DA | Selection | Resolved value |
|---|---|---|
| DA1 ATR window P | A | 20 |
| DA2 ATR multiplier K | A | 2.0 |
| DA3 Per-trade risk % | A | 1.0% |
| **DA4 START_CASH_USD** | **B** | **$100,000** |
| DA5 K4 max-drawdown fraction | A | 0.50 |
| DA6 Output schema name | A | `sparta.s12.d1.mnq_c0.donchian_15_8.diagnostic_run_report.v1` |
| DA7 Cost-stress tier set | A | 5-tier S0/S1/S2/S3/S4 (0.0/1.0/1.5/2.0/3.0) |
| DA8 Commission / round-trip | A | $0.74 |
| DA9 Fees / round-trip | A | $0.36 |
| DA10 Slippage e/s/x ticks | A | 1/1/1 |
| DA11 WARMUP_DAYS | A | 220 |
| DA12 RTH window | A | 09:30-16:00 ET America/New_York |
| DA13 DR9 thresholds | A | 0.95 / 0.30 / 5 / 5 |
| DA14 DR10 thresholds | A | annual_turnover ≤ 0.50; s2_cost_drag ≤ 0.05 |

**Only DA4 revised. All others at default A.**

---

## 5. Review clarifications carried byte-equivalent from SEAL

### C1.A — Accept OOS K9 risk as part of structural test
> At expected IS trade densities (80-200 over 4.6y), proportional scaling to the 2.0y OOS window yields expected OOS trade counts of **35 / 61 / 87** at lower / central / upper IS bounds — all below K9=100. The candidate may park under `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` on OOS verdict. This is the structural test of the fresh-candidate hypothesis, not a defect.

### C1.D — OOS K9 sub-threshold maps to DR1 INCONCLUSIVE_HOLD (not REJECT_FAST)
> DR1 was extended at SEAL to cover `oos_closed_trades < K9_threshold`. The verdict for OOS K9 sub-threshold is `INCONCLUSIVE_HOLD`, not `REJECT_FAST`. Candidate is parked, not killed; IS evidence preserved.

---

## 6. Locked IS / OOS windows

| Field | Value |
|---|---|
| IS start | 2019-05-13 |
| IS end | 2023-12-29 |
| IS length | ~4.6y / 1,443 rows audit-confirmed |
| OOS start (never inspected at IS) | 2024-01-02 |
| OOS end (never inspected at IS) | 2025-12-30 |
| OOS length | ~2.0y / 622 rows structural only |
| OOS inspection at IS phase | **FORBIDDEN** |

---

## 7. Locked data source

| Field | Value |
|---|---|
| Vendor | Databento Historical API |
| Dataset | `GLBX.MDP3` |
| Schema | `ohlcv-1d` |
| `stype_in` | `continuous` |
| Symbol | `MNQ.c.0` |
| CSV reuse path | `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv` |
| CSV sha256 | `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e` |
| CSV rows | 2,066 |
| **New Databento fetch required** | **False** |
| API key handling | NOT REQUIRED AT ANY PHASE |
| Controller-side Databento call | LOCKED OFF at every phase |

---

## 8. Locked cost-stress matrix

| Tier | cost_scalar | slippage_scalar |
|---|---|---|
| S0 | 0.0 | 0.0 |
| S1 | 1.0 | 1.0 |
| S2 | 1.5 | 1.5 |
| S3 | 2.0 | 2.0 |
| S4 | 3.0 | 3.0 |

Commission $0.74 / Fees $0.36 / Slippage 1-1-1 ticks. MNQ.c.0 tick = 0.25 / $0.50.

---

## 9. K9 sample-size warning at P1

| Estimate | IS trades (4.6y) | × (2.0/4.6) | OOS expected (2y) |
|---|---|---|---|
| Lower | 80 | 0.435 | **35** |
| Central | 140 | 0.435 | **61** |
| Upper | 200 | 0.435 | **87** |

**All three OOS estimates below K9 = 100.** Per C1.A + C1.D carried from SEAL: OOS K9 sub-threshold → DR1 `INCONCLUSIVE_HOLD`. The candidate may park under `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` on the eventual OOS verdict. **This is the structural test of the fresh-candidate hypothesis, not a defect.**

---

## 10. Locked invariants — no live / no Strategy Lab / no review_queue (25 total)

**7 inherited B005_NNN:** `no_live_trading` · `no_strategy_lab_promotion` · `no_review_queue_mutation` · `no_brokerage_connection` · `no_external_network` · `no_databento_at_runtime` · `no_production_signal`

**4 inherited B006_001:** `no_strategy_optimization_authorized` · `no_profitability_claim` · `no_universe_membership_logic` · `no_dr_redefinition_post_seal`

**2 inherited B006_002:** `no_warmup_order_submission` · `dr6_warmup_contamination_blocked`

**5 inherited s10-D1:** `no_continuous_roll_stitch_modification_post_seal` · `no_mcl_inclusion_under_long_history_scope` · `no_intraday_schema_ingest_under_daily_only_design` · `databento_api_key_read_from_env_only_never_logged_or_saved` · `no_pyramid_per_signal`

**3 inherited s11-d1:** `single_instrument_universe_NO_widening_post_seal` · `no_substitution_of_any_symbol_into_this_universe_post_seal` · `mnq_c0_csv_reuse_byte_equivalent_no_fresh_fetch`

**4 new s12-d1:** `donchian_15_8_locked_at_plan_no_retreat_to_55_20` · `no_revision_of_s11_d1_sealed_artifacts` · `s12_d1_does_not_supersede_s11_d1_v1_p1_p2_clarification_rev2` · `mechanic_family_lock_at_plan_no_reopening_at_draft_or_seal`

---

## 11. Exact next authorized phases (NONE pre-approved)

This P1 plan-lock authorizes ONLY the existence of the locked plan. It does NOT authorize execution of any subsequent phase. **Each subsequent phase requires a separate fresh operator authorization block.**

| Next phase | Authorization phrase required | Scope summary |
|---|---|---|
| **P2 phase-2 plan** | `"Authorize s12 D1 P2 phase-2 plan only"` | Author the phase-2 plan referencing this P1. P2 is a planning artifact only, not BUILD. |
| **P3 BUILD only** | `"Authorize s12 D1 P3 BUILD only"` | Author the runner harness implementing the locked F1 mechanic. BUILD is implementation only, **NOT a RUN**. |
| **No automatic build/run** | (no implicit authorization) | This P1 does NOT self-authorize P2, P3, BUILD, RUN, simulator, backtest, signal compute, data fetch, Databento call, API key access, Strategy Lab promotion, review_queue mutation, idea_memory mutation, brokerage connection, orders, paper trade, or live trade. |
| **Deferral option** | `"Defer / Pause s12-d1 track"` | Hold the S12-D1 chain on file at P1 without advancing. |

---

## 12. Validation V-gates (this P1 turn)

- **V1** ASCII-only.
- **V2** Numbered/keyed sections consistent.
- **V3** No execution language.
- **V4** No self-authorization to P2 / P3 / BUILD / RUN.
- **V5** No code modification.
- **V6** No backtest run.
- **V7** No simulator run.
- **V8** No signal computation.
- **V9** No data fetch.
- **V10** No network IO.
- **V11** No live trading.
- **V12** Sealed spec @ `9ce4d66` byte-stable at HEAD.
- **V13** Exactly 2 new files staged.
- **V14** `lessons.md` unstaged and untouched.
- **V15** DA4=B locked from SEAL DA-register.
- **V16** C1.A and C1.D carried byte-equivalent from SEAL.

---

## 13. Posture

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live | `BLOCKED_AT_6_GATES` (permanent) |
| FRC granted | `False` |
| Advisory label permanent | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| `verdict_never_means_live_ready` | True |
| `live_promotion_path_closed` | True |

---

## 14. Negative invariants (all True)

`no_build` · `no_runner_build` · `no_simulator_run` · `no_backtest_run` · `no_signal_computed` · `no_data_fetch` · `no_databento_call` · `no_databento_api_key_access` · `no_external_network_call` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_brokerage_connection` · `no_orders_created` · `no_paper_or_live_trade` · `no_s7_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_s10_d2_artifact_modified` · `no_s11_d1_artifact_modified` · `no_s12_d1_draft_modified` · `no_s12_d1_plan_modified` · `no_s12_d1_review_modified` · `no_s12_d1_addendum_memo_modified` · `no_s12_d1_sealed_spec_modified` · `no_parallel_session_s12_d1_seal_modified` · `no_parallel_session_s12_d1_p1_modified` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_cache_modification` · `no_data_modification` · `no_driver_modification` · `no_test_modification` · `no_strategy_code_modification` · `no_runbook_modification` · `no_pipeline_manifest_modification` · `no_decisions_md_modification` · `no_gitignore_modification` · `no_claude_md_modification` · `no_lessons_md_modification` · `no_lessons_md_staging` · `no_lessons_md_commit` · `no_branch_change` · `no_git_push` · `no_frc_grant` · `no_live_readiness_claim` · `no_profitability_claim` · `no_oos_confirmation_claim` · `no_k9_threshold_relaxation_proposed` · `no_self_authorization_of_p2_p3_build_or_run` · `no_automatic_build_or_run_path` · `no_key_leakage`

---

## 15. Labels

`S12_D1_P1_PLAN_LOCK_COMPLETE` · `SPEC_LOCKED` · `ANCHORS_TO_SEAL_AT_9CE4D66` · `DA4_B_LOCKED` · `ALL_OTHER_DA_DEFAULT_A` · `C1_A_CARRIED_BYTE_EQUIVALENT` · `C1_D_CARRIED_BYTE_EQUIVALENT` · `START_CASH_100000_LOCKED` · `DONCHIAN_15_8_LOCKED` · `MNQ_C0_ONLY_LOCKED` · `NO_PYRAMID_LOCKED` · `ATR_20_STOP_LOCKED` · `COST_STRESS_5_TIER_LOCKED` · `IS_OOS_WINDOWS_LOCKED` · `OOS_K9_RISK_WARNING_DOCUMENTED` · `DR1_INCONCLUSIVE_HOLD_FOR_OOS_K9_SUB_THRESHOLD` · `NO_AUTOMATIC_BUILD_OR_RUN` · `P2_AND_P3_BUILD_REQUIRE_SEPARATE_AUTHORIZATION` · `NO_BUILD` · `NO_SIMULATOR_RUN` · `NO_BACKTEST` · `NO_SIGNAL_COMPUTED` · `NO_DATA_FETCH` · `NO_DATABENTO_CALL` · `NO_DATABENTO_API_KEY_ACCESS` · `NO_REVIEW_QUEUE_MUTATION` · `NO_STRATEGY_LAB_PROMOTION` · `NO_LIVE_TRADING` · `VERDICT_NEVER_MEANS_LIVE_READY`

---

## 16. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**S12-D1 P1 plan-lock sealed. Anchors to sealed spec at `9ce4d66`. DA4=B locked. C1.A + C1.D carried byte-equivalent. OOS K9 risk warning documented; disposition DR1 INCONCLUSIVE_HOLD. No automatic build or run. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

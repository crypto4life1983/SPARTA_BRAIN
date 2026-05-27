# S10-D2 P10.5 OOS Cost-Stress Sweep at S0/S2/S3 (SEALED)

**Schema:** `sparta.s10.d2.oos_cost_stress_sweep_p10_5_report.v1`
**Phase:** `S10_D2_P10_5_OOS_COST_STRESS_SWEEP`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC-P10.5`
**Controller session:** `THIS_SESSION_ONLY`
**Report kind:** oos_cost_stress_sweep_S0_S2_S3_S1_parity_baseline_from_P10
**Sealed at (UTC):** `2026-05-27T13:39:01Z`

**Authorization:** *"Authorize S10-D2 P10.5 OOS cost-stress sweep at S0/S2/S3 only."*

> S1 was NOT rerun. The S1 row in the matrix below is the parity baseline taken byte-equivalent from the sealed P10 OOS gate at commit `15231cb` (seal `4038e5334feba9ea`). S0/S2/S3 were freshly run in this sweep against the existing OOS cache via the committed `out_of_sample_driver.py`.

---

## 0. Executive

- **OOS cost-stress verdict:** **`OOS_COST_STRESS_SURVIVES`**
- **K12 OOS (DR fires):** **False**
- **OOS safety all zero across S0/S2/S3:** **True**
- **K9 OOS sample status:** **REMAINS_INSUFFICIENT** (53 closed trades < 100 threshold; cost-stress does not change closed_trades)
- **Lifecycle status:** **`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`** (unchanged)
- **Candidate remains parked:** **True**

---

## 1. OOS cost-stress matrix

| Tier | source | trades | net_pnl USD | sharpe pt | expectancy | maxdd % | wr % | wr_gap pp | safety zero |
|---|---|---|---|---|---|---|---|---|---|
| S0 | this sweep | 53 | +119,284.66 | +0.10578 | +2,250.65 | -12.81 | 33.96 | +6.85 | True |
| S1 | P10 (parity baseline) | 53 | +113,450.34 | +0.10051 | +2,140.57 | -12.96 | 33.96 | +6.52 | True |
| S2 | this sweep | 53 | +107,698.00 | +0.09542 | +2,032.04 | -13.22 | 33.96 | +6.21 | True |
| S3 | this sweep | 53 | +100,516.42 | +0.08859 | +1,896.54 | -13.49 | 33.96 | +5.77 | True |

## 2. Decision-rule evaluation (OOS-side)

- **DR2 OOS** (S2 or S3 degrades >50% vs S1 OR flips negative): **False**
  - per-tier: S2 = False; S3 = False
- **DR3 OOS** (S0 positive AND any of S1/S2/S3 non-positive): **False**
- **DR5 OOS** (S0 positive AND S1 non-positive): **False**
- **K12 OOS (DR fires):** **False**

## 3. Per-tier durations + driver byte-stability

- Sweep total: 203.8 s
  - S0: 74.7 s
  - S2: 66.5 s
  - S3: 62.6 s

- OOS driver byte-sha at start: `7941ff28e0dbad0fae68aff3fd62b21b05fcc8fe1615c251fce1cc01858bf9b4`
- OOS driver byte-sha at end:   `7941ff28e0dbad0fae68aff3fd62b21b05fcc8fe1615c251fce1cc01858bf9b4`
- Driver byte-stable through sweep: **True**
- Monkey patches applied: **0**

## 4. Cache attestation

| Cache | File count | Total bytes | Pre-agg sha (16) | Post-agg sha (16) | Byte-stable through sweep |
|---|---|---|---|---|---|
| OOS | 144 | 42,663,855 | `244cfd0bd9b20cde` | `244cfd0bd9b20cde` | **True** |
| IS  | 480 | 129,790,451 | `3ac2681cc9e5f204` | `3ac2681cc9e5f204` | **True** |

Caches remain separate: **True**

## 5. Required explicit statements

- S2/S3 (and S0) remain directionally positive (net_pnl, sharpe, expectancy all > 0): **True**
- Safety remains clean across S0/S2/S3: **True**
- Drawdown remains acceptable (|maxdd| < 50% K4 threshold for all tiers): **True**
- **K9 remains insufficient for OOS:** **True** (S1 OOS closed_trades = 53 < 100; cost-stress does not change closed_trades)
- **Candidate remains parked:** **True**
- no_databento_call: **True**
- no_databento_api_key_access: **True**
- no_data_fetch: **True**
- no_strategy_lab_invoked: **True**
- no_review_queue_mutation: **True**
- no_live_trading: **True**

## 6. Verdict interpretation

OOS cost-stress sweep refines the interpretation of the existing 53-trade OOS sample by testing whether the directional consistency observed at S1 also holds at S0/S2/S3. The verdict applies ONLY to the cost-stress dimension. It does NOT address the K9 sample-size finding. The candidate remains PARKED.

## 7. Inherited seals (anchors preserved byte-equivalent)

- `tier_n_spec_seal`: `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
- `plan_lock_seal`: `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
- `phase2_plan_seal`: `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
- `p3_6_oos_driver_build_seal`: `c7d9d7888f2bc5df6850ab37f9bde0b95c3c794486382c4b0d45f32b6bd1b73d`
- `p6_is_diagnostic_seal`: `e6cdc7c68a9e2b7b6d749b73ff433e585c9de55890af5dce3dca51d74430c1b8`
- `p6_5_cost_stress_seal`: `04351ca093ec20b0ee11a22c32fd4c83d814444835951d594440c3e67730f571`
- `p7_decision_memo_seal`: `87baa6e8c4cc1eb47c1345b97990eab86d5cefb37636e9fe57a029506d398c05`
- `k10_pairwise_dependence_seal`: `8c620cc5bfe53f71d4ededba45b3d8cee0de54992db6819103875811cbdb99e4`
- `p10_oos_gate_seal`: `4038e5334feba9ea61b91dcb47287a7a8f9f8fdfd8ad35990866bc9fbd106137`
- `p11_park_memo_seal`: `e121b82b411697c7d06bbe9ee1cc2df29c04df76712873ed0fbfd76f25fab1cb`
- `oos_scope_reconciliation_review_seal`: `c57bb806ca56e1589c0a53c8cb249e678286e05f67ea12919d2881bbbd6378e4`
- `lifecycle_park_report_seal`: `8d59e94a736aa82da1ee3891518a9de6a8798128133cd1f39633f05faa6593d0`
- `terminal_lesson_seal`: `7026b1b5f50a04100c45b503ef7eaebb4c739328056842e98d4ce25d5bfc33a7`
- `continuation_track_selection_plan_seal`: `c6df16dff233ee232fd73208b1b83d4174904f6477b36f9750f1f6fca5e45a4b`

## 8. Negative invariants (all True)

- `monkey_patches_applied_count`: **0**
- `no_backtest_run_outside_oos_driver`: **True**
- `no_branch_change`: **True**
- `no_brokerage_connection`: **True**
- `no_cache_modification`: **True**
- `no_candidate_promoted`: **True**
- `no_canonical_k10_modification`: **True**
- `no_claude_md_modification`: **True**
- `no_data_fetch`: **True**
- `no_databento_api_key_access`: **True**
- `no_databento_call`: **True**
- `no_decisions_md_modification`: **True**
- `no_external_network_call`: **True**
- `no_frc_grant`: **True**
- `no_git_push`: **True**
- `no_gitignore_modification`: **True**
- `no_idea_memory_mutation`: **True**
- `no_in_sample_driver_modification`: **True**
- `no_is_cache_mutation`: **True**
- `no_is_cache_touched_or_read`: **False**
- `no_k9_threshold_relaxation_proposed`: **True**
- `no_key_leakage`: **True**
- `no_lessons_md_commit`: **True**
- `no_lessons_md_modification`: **True**
- `no_lessons_md_staging`: **True**
- `no_lifecycle_status_change`: **True**
- `no_live_readiness_claim`: **True**
- `no_oos_cache_mutation`: **True**
- `no_oos_confirmation_claim`: **True**
- `no_oos_driver_modification`: **True**
- `no_orb_artifact_modified`: **True**
- `no_orders_created`: **True**
- `no_p10_re_run`: **True**
- `no_p11_modification`: **True**
- `no_paper_or_live_trade`: **True**
- `no_phase2_plan_modification`: **True**
- `no_pipeline_manifest_modification`: **True**
- `no_plan_lock_modification`: **True**
- `no_profitability_claim`: **True**
- `no_review_queue_mutation`: **True**
- `no_runbook_modification`: **True**
- `no_runner_harness_modification`: **True**
- `no_s10_d1_artifact_modified`: **True**
- `no_s11_d1_artifact_modified`: **True**
- `no_s1_re_run`: **True**
- `no_s7_artifact_modified`: **True**
- `no_s8_d1_artifact_modified`: **True**
- `no_s9_artifact_modified`: **True**
- `no_signal_compute_outside_oos_driver`: **True**
- `no_simulator_run_outside_oos_driver`: **True**
- `no_step_30_cost_constant_modified`: **True**
- `no_strategy_code_modification`: **True**
- `no_strategy_lab_invoked`: **True**
- `no_threshold_loosening`: **True**
- `no_tier_n_spec_modification`: **True**
- `no_unpark`: **True**

## 9. Status

- Trading: `PAUSED`
- Live: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- `verdict_never_means_live_ready`: **True**
- `live_promotion_path_closed`: **True**
- S10-D2 lifecycle status: **`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`** (unchanged by this sweep)

## 10. Labels

- `S10_D2_P10_5_OOS_COST_STRESS_SWEEP_COMPLETE`
- `OOS_COST_STRESS_S0_S2_S3_EVALUATED`
- `S10_D2_REMAINS_PARKED`
- `NO_LIFECYCLE_STATUS_CHANGE`
- `OOS_VERDICT_OOS_COST_STRESS_SURVIVES`
- `K12_OOS_DR_FIRES_False`
- `OOS_SAFETY_ALL_ZERO_NEW_TIERS_True`
- `K9_REMAINS_INSUFFICIENT`
- `NO_UNPARK`
- `NO_OOS_CONFIRMATION_CLAIM`
- `NO_DATABENTO_CALL`
- `NO_DATABENTO_API_KEY_ACCESS`
- `NO_DATA_FETCH`
- `NO_REVIEW_QUEUE_MUTATION`
- `NO_STRATEGY_LAB_PROMOTION`
- `NO_LIVE_TRADING`
- `VERDICT_NEVER_MEANS_LIVE_READY`

## 11. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**OOS cost-stress sweep sealed. Verdict: OOS_COST_STRESS_SURVIVES. K12 OOS DR fires: False. Candidate REMAINS PARKED. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**


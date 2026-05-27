# S12-D1 MNQ.c.0 Donchian-15/8 Tier-N Spec (SEALED) — Report Companion

**Schema:** `sparta.s12.d1.mnq_c0.donchian_15_8.tier_n_spec.sealed.v1`
**Phase:** `S12_D1_TIER_N_SPEC_SEALED`
**Phase prefix:** `PHASE2-S12-D1-SEAL`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T14:50:00Z`

**Authorization:** *"Authorize s12 D1 MNQ.c.0 Tier-N spec SEAL with revisions: DA4=B; all others as default A. At SEAL also affirm C1.A + C1.D from review."*

**Canonical sealed spec (primary document):** `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_tier_n_spec.md`

---

## 0. SEAL summary

| Field | Value |
|---|---|
| candidate_record_id | `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history` |
| Source DRAFT | commit `7e9c8679`, sha `9f09ec94028659eb`, byte-count 28,116 |
| Source review | commit `07be7fc`, seal `860e766e6933751d`, verdict `DRAFT_REVIEW_PASS_WITH_CLARIFICATIONS` |

## 1. DA-register resolution

| DA | Selection | Resolved value |
|---|---|---|
| DA1 ATR stop window P | **A** | Wilder ATR(20) |
| DA2 ATR multiplier K | **A** | 2.0 (2N stop) |
| DA3 Per-trade risk % | **A** | 1.0% of portfolio equity |
| **DA4 START_CASH_USD** | **B** | **$100,000** (operator-revised at SEAL) |
| DA5 K4 max-drawdown threshold | **A** | 0.50 (50% × $100k = $50,000 absolute) |
| DA6–DA14 | **A** (framework-locked) | (see canonical spec §0) |

**All other DA = default A.** **DA4=B applied.**

## 2. Review clarifications affirmed at SEAL

- **C1.A — Accept OOS K9 risk as part of structural test:** Affirmed. Proportional scaling yields OOS expected trade counts of 35 / 61 / 87 at lower / central / upper IS bounds — all below K9=100. The candidate may park under `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` on OOS verdict; this is the structural test of the fresh-candidate hypothesis, not a defect.
- **C1.D — OOS K9 sub-threshold maps to DR1 INCONCLUSIVE_HOLD (not REJECT_FAST):** Affirmed. DR1 extended at SEAL to cover `oos_closed_trades < K9_threshold`. Candidate is parked, not killed; IS evidence is preserved.

## 3. Locked parameters at SEAL

| Field | Value |
|---|---|
| Universe | `{MNQ.c.0}` (single instrument) |
| Mechanic family | F1 (bi-directional Donchian trend, no pyramid, ATR stop) |
| Donchian entry / exit | **15 / 8** |
| Pyramid | NONE / `max_units_per_market = 1` |
| ATR stop | Wilder ATR(20), 2N |
| Per-trade risk | 1.0% portfolio equity |
| `START_CASH_USD` | **$100,000** (DA4=B) |
| K4 max-drawdown threshold (abs) | $50,000 (50% × START_CASH) |
| K9 threshold (IS + OOS) | 100 closed trades |
| Cost-stress matrix | 5-tier S0/S1/S2/S3/S4 with scalars 0.0/1.0/1.5/2.0/3.0 |
| Tick / $-per-tick (MNQ.c.0) | 0.25 pts / $0.50 |
| Commission / Fees / Slippage | $0.74 / $0.36 / 1-1-1 ticks |
| WARMUP_DAYS | 220 |
| RTH window | 09:30-16:00 ET America/New_York |
| IS window | 2019-05-13 → 2023-12-29 (~4.6y; 1,443 rows) |
| OOS window | 2024-01-02 → 2025-12-30 (~2y; 622 rows) |
| Data | Audit-clean MNQ.c.0 CSV from s10-D1 (sha `8b7b832c62fae185`); zero new Databento fetch |
| Total SEAL invariants | 25 |

## 4. K9 / sample-size at SEAL

| Estimate | IS trades (4.6y) | × (2.0/4.6) | Expected OOS trades (2y) |
|---|---|---|---|
| Lower | 80 | 0.435 | **35** |
| Central | 140 | 0.435 | **61** |
| Upper | 200 | 0.435 | **87** |

All three OOS estimates **below K9 = 100**. Per C1.A + C1.D affirmed at SEAL: OOS K9 sub-threshold → DR1 `INCONCLUSIVE_HOLD`.

## 5. Posture

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live | `BLOCKED_AT_6_GATES` (permanent) |
| FRC | `NEVER_GRANTED` |
| Advisory label | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` (permanent) |
| `verdict_never_means_live_ready` | True |
| `live_promotion_path_closed` | True |

## 6. Negative invariants (all True)

`no_build` · `no_runner_build` · `no_simulator_run` · `no_backtest_run` · `no_signal_computed` · `no_data_fetch` · `no_databento_call` · `no_databento_api_key_access` · `no_external_network_call` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_brokerage_connection` · `no_orders_created` · `no_paper_or_live_trade` · `no_s7_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_s10_d2_artifact_modified` · `no_s11_d1_artifact_modified` · `no_s12_d1_draft_modified` · `no_s12_d1_plan_modified` · `no_s12_d1_review_modified` · `no_s12_d1_addendum_memo_modified` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_cache_modification` · `no_data_modification` · `no_driver_modification` · `no_test_modification` · `no_strategy_code_modification` · `no_runbook_modification` · `no_pipeline_manifest_modification` · `no_decisions_md_modification` · `no_gitignore_modification` · `no_claude_md_modification` · `no_lessons_md_modification` · `no_lessons_md_staging` · `no_lessons_md_commit` · `no_branch_change` · `no_git_push` · `no_frc_grant` · `no_live_readiness_claim` · `no_profitability_claim` · `no_oos_confirmation_claim` · `no_k9_threshold_relaxation_proposed` · `no_self_authorization_of_p1_p2_p3_build_or_run` · `no_key_leakage`

## 7. Predecessor anchors (byte-stable)

| Anchor | Seal / sha (first 16) |
|---|---|
| Source DRAFT | `9f09ec94028659eb` |
| Source review | `860e766e6933751d` |
| s11-d1 v1 spec | `077e29e62f23dbc3` |
| s11-d1 rev2 | `46659b4a8a73cb72` |
| s10-D2 P11 PARK | `e121b82b411697c7` |
| s10-D1 PARK | `32c1a87146264197` |
| Audit-clean MNQ.c.0 CSV | `8b7b832c62fae185` |

## 8. Next authorization scopes (NONE pre-approved)

- *"Authorize s12 D1 P1 plan-lock spec only"*
- *"Authorize s12 D1 P2 phase-2 plan only"*
- *"Authorize s12 D1 P3 BUILD only"*
- *"Defer / Pause s12-d1 track"*

## 9. Labels

`S12_D1_TIER_N_SPEC_SEALED` · `DA4_B_ACCEPTED` · `ALL_OTHER_DA_DEFAULT_A` · `C1_A_ACCEPTED` · `C1_D_ACCEPTED` · `START_CASH_100000_LOCKED` · `DONCHIAN_15_8_LOCKED` · `MNQ_C0_ONLY` · `NO_PYRAMID` · `ATR_20_STOP` · `COST_STRESS_5_TIER_LOCKED` · `IS_OOS_WINDOWS_LOCKED` · `OOS_K9_RISK_ACKNOWLEDGED_AS_STRUCTURAL_TEST` · `DR1_INCONCLUSIVE_HOLD_FOR_OOS_K9_SUB_THRESHOLD` · `NO_BUILD` · `NO_SIMULATOR_RUN` · `NO_BACKTEST` · `NO_SIGNAL_COMPUTED` · `NO_DATA_FETCH` · `NO_DATABENTO_CALL` · `NO_DATABENTO_API_KEY_ACCESS` · `NO_REVIEW_QUEUE_MUTATION` · `NO_STRATEGY_LAB_PROMOTION` · `NO_LIVE_TRADING` · `VERDICT_NEVER_MEANS_LIVE_READY`

## 10. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**S12-D1 Tier-N spec sealed. DA4=B; all others A. C1.A + C1.D affirmed. Donchian-15/8 + MNQ.c.0 + 5-tier cost-stress locked. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

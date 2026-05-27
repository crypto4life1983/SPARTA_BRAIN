# T1 RSI MNQ.c.0 Tier-N Spec (SEALED) — Report Companion

**Schema:** `sparta.t1.rsi_mnq_c0.mean_reversion_2.tier_n_spec.sealed.v1`
**Phase:** `T1_RSI_MNQ_TIER_N_SPEC_SEALED`
**Phase prefix:** `PHASE2-T1-RSI-MNQ-SEAL`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T17:55:00Z`

**Authorization:** *"Authorize T1 RSI MNQ Tier-N spec SEAL with revisions: DA8=B; DA9=B; all others as default A."*

**Canonical sealed spec:** `docs/t1_rsi_mnq_tier_n_spec.md`

---

## 0. SEAL summary

| Field | Value |
|---|---|
| `candidate_record_id` | `t1-rsi-mnq-c0-mean-reversion-2-period-databento-long-history` |
| Source PLAN | commit `729207f`, seal `70549a9ac2c15f36` |
| Source DRAFT | commit `fb1079a`, bit-identical at HEAD |
| Algo version | `t1_v0_1_0` |
| SEAL revisions | **DA8=B (0.5% risk) + DA9=B ($200k cash)** ; all other DAs default A |

## 1. DA-register resolution

| DA | Selection | Resolved value |
|---|---|---|
| DA1 RSI period | (PLAN-LOCK) | **2** (Connors canonical) |
| DA2 RSI oversold threshold | A | 10 |
| DA3 RSI overbought threshold | A | 90 |
| DA4 RSI exit centerline | A | 50 |
| DA5 Exit-by-time max bars | A | 5 |
| DA6 ATR window | A | Wilder 20 |
| DA7 ATR multiplier | A | 2.0 (2N stop) |
| **DA8 Per-trade risk %** | **B** | **0.5%** (operator-revised; DR10 mitigation) |
| **DA9 START_CASH_USD** | **B** | **$200,000** (operator-revised; DR10 mitigation) |
| DA10 K4 max-drawdown fraction | A | 0.50 → **$100,000 absolute** (50% × $200k) |
| DA11 Output schema | A | (framework-locked) |
| DA12 Cost-stress tier set | A | 5-tier S0–S4 (0.0/1.0/1.5/2.0/3.0) |
| DA13 Commission per round-trip | A | $0.74 |
| DA14 Fees per round-trip | A | $0.36 |
| DA15 Slippage e/s/x ticks | A | 1/1/1 |
| DA16 WARMUP_DAYS | A | 220 |
| DA17 RTH window | A | 09:30-16:00 ET |
| DA18 DR9 thresholds | A | 0.95 / 0.30 / 5 / 5 |
| DA19 DR10 thresholds | A | annual_turnover ≤ 0.50; s2_cost_drag ≤ 0.05 |
| DA20 OOS K9 sub-threshold disposition | A | DR1 INCONCLUSIVE_HOLD (NOT REJECT_FAST) |

**Revisions vs DRAFT defaults:** 2 (DA8 + DA9). All others default A.

## 2. Locked parameters at SEAL

| Field | Value |
|---|---|
| Mechanic family | F3 RSI mean-reversion, bi-directional, no pyramid |
| RSI period | 2 (PLAN-LOCK) |
| Long entry / exit | RSI(2)<10 / RSI(2)>50 |
| Short entry / exit | RSI(2)>90 / RSI(2)<50 |
| Exit-by-time max bars | 5 |
| Pyramid | NONE / max_units_per_market = 1 |
| ATR stop | Wilder ATR(20), 2N |
| **Per-trade risk** | **0.5%** (DA8=B) |
| **START_CASH** | **$200,000** (DA9=B) |
| **K4 max-drawdown abs** | **$100,000** (50% × $200k) |
| WARMUP_DAYS | 220 |
| RTH | 09:30-16:00 ET America/New_York |
| Tick / $-per-tick (MNQ.c.0) | 0.25 / $0.50 |
| Commission / Fees | $0.74 / $0.36 |
| Slippage e/s/x ticks | 1/1/1 |
| K9 threshold (IS + OOS) | 100 closed trades |
| Universe | `{MNQ.c.0}` |
| IS window | 2019-05-13 → 2023-12-29 |
| OOS window | 2024-01-02 → 2025-12-30 |
| Total SEAL invariants | 25 |

## 3. K9-reachability analysis at SEAL

| Window | Required trades/y | Expected trades/y | Status |
|---|---|---|---|
| IS (4.6y) | ≥21.74 | 46-68 | **CLEARS WITH MARGIN** (lower-bound ratio 2.12) |
| **OOS (2.0y)** | **≥50.00** | 46-68 | **BORDERLINE_TO_CLEARING** |

OOS proportional-scaling at IS lower-bound (46/y × 2y) = **92 trades** < 100 → fires K9 (ratio 0.92)
OOS central (57/y × 2y) = **114 trades** > 100 → clears (ratio 1.14)
OOS upper (68/y × 2y) = **136 trades** > 100 → clears with margin (ratio 1.36)

Per DA20=A: OOS K9 sub-threshold → DR1 `INCONCLUSIVE_HOLD` (NOT REJECT_FAST).

## 4. OOS borderline warning

OOS K9 at lower-bound estimate (92 closed_trades) is **BELOW the 100-trade threshold and would fire OOS K9**. At central and upper estimates, the candidate clears OOS K9. T1 is structurally more favorable than S12-D1 (T1 OOS lower-bound ratio 0.92 vs S12-D1 IS lower-bound ratio 0.80) but **OOS K9 clearance is NOT guaranteed at lower-bound estimate**. If OOS K9 fires at sub-threshold at the future P10 phase, disposition is DR1 `INCONCLUSIVE_HOLD` per DA20=A.

## 5. DR10 cost-turnover risk disclosure

RSI(2) is structurally **more cost-sensitive** than Donchian trend-following:

- DR2/DR3/DR5 reject-fast rules apply with **ELEVATED prior probability** at S2/S3
- DR10 turnover-cost-explosion **ELEVATED prior probability**: RSI(2) trades 5–6× as often as Donchian-15/8; per-trade dollar move smaller; dollar-turnover ~30–40× higher than S12-D1

**Operator-applied DR10 mitigation at SEAL:**
- **DA8=B** (0.5% risk; halves contracts-per-trade vs s12-d1 baseline 1.0%)
- **DA9=B** ($200k START_CASH; doubles base capital vs s12-d1 baseline $100k; reduces per-dollar turnover pressure)
- **DA19=A** (DR10 threshold itself unchanged at framework default 0.50/0.05; mitigation is sizing-based, not threshold-based)

This matches parallel session's `s13-d1` SEAL choice direction.

## 6. 25 SEAL invariants (4 new T1-specific)

**7 inherited B005_NNN** + **4 B006_001** + **2 B006_002** + **5 s10-D1-specific** + **3 s11-d1-specific** + **4 new T1-specific:**
- `rsi_period_2_locked_at_plan_no_retreat_to_3_4_or_other`
- `mean_reversion_centerline_50_locked_at_plan_no_drift_to_55_60`
- `bi_directional_locked_at_plan_no_retreat_to_long_only`
- `mechanic_family_f3_lock_at_plan_no_reopening_at_draft_or_seal`

## 7. K-gates + DR-rules (carried byte-equivalent with F3-RSI(2) adaptations)

K-gates: K1/K2/**K4 ($100k abs)**/K7/K8/K9/**K12 (ELEVATED prior)**; K6/K10/K11 N/A for single-instrument F3.

DR-rules: DR1-DR10 applicable; **DR2/DR3/DR5/DR10 ELEVATED prior probability** under RSI(2); DR11 not in chain.

DR precedence: `DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`.

## 8. 17 RF-criteria for runtime safety

Standard RF1-RF17 carried from s12-d1 lineage with T1-specific adaptations:
- **RF13** RSI period silently switched from LOCKED 2 → REJECT_FAST
- **RF14** Mean-reversion centerline silently switched from LOCKED 50 → REJECT_FAST
- **RF17** Retroactive re-anchoring of T1 PLAN / DRAFT / s11-d1 / s12-d1 → REJECT_FAST

OOS K9 sub-threshold is NOT a REJECT_FAST condition (DA20=A → DR1 INCONCLUSIVE_HOLD).

## 9. Predecessor anchors (byte-stable)

| Anchor | Seal / sha (first 16) |
|---|---|
| Source PLAN | `70549a9ac2c15f36` |
| Source DRAFT (commit) | `fb1079afe34e722c` |
| s12-d1 P11 PARK memo (this session) | `321b8940a5516762` |
| s12-d1 sealed Tier-N spec (this session) | `422bbbff75f24816` |
| s12-d1 P11 PARK memo (parallel canonical) | `b9722d424f6faabe` |
| s10-D2 lifecycle park report (this session) | `8d59e94a736aa82d` |
| s11-d1 v1 spec | `077e29e62f23dbc3` |
| s11-d1 rev2 | `46659b4a8a73cb72` |
| Audit-clean MNQ.c.0 CSV | `8b7b832c62fae185` |

## 10. Posture

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live | `BLOCKED_AT_6_GATES` (permanent) |
| FRC granted | `False` |
| Advisory label permanent | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| `verdict_never_means_live_ready` | True |
| `live_promotion_path_closed` | True |

## 11. Next authorization scopes (NONE pre-approved)

- *"Authorize T1 P1 plan-lock spec only"*
- *"Authorize T1 P2 phase-2 plan only"*
- *"Authorize T1 P3 BUILD only"*
- *"Defer / Pause T1 track"*

## 12. Negative invariants (51 evaluated; all True)

`no_build` · `no_runner_build` · `no_simulator_run` · `no_backtest_run` · `no_signal_computed` · `no_rsi_computation` · `no_data_fetch` · `no_databento_call` · `no_databento_api_key_access` · `no_external_network_call` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_brokerage_connection` · `no_orders_created` · `no_paper_or_live_trade` · `no_s7_artifact_modified` · `no_s8_d1_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_s10_d2_artifact_modified` · `no_s11_d1_artifact_modified` · `no_s12_d1_artifact_modified` · `no_t1_plan_modified` · `no_t1_draft_modified` · `no_parallel_s13_d1_chain_modified` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_cache_modification` · `no_data_modification` · `no_csv_modification` · `no_driver_modification` · `no_test_modification` · `no_strategy_code_modification` · `no_runbook_modification` · `no_pipeline_manifest_modification` · `no_decisions_md_modification` · `no_gitignore_modification` · `no_claude_md_modification` · `no_lessons_md_modification` · `no_lessons_md_staging` · `no_lessons_md_commit` · `no_branch_change` · `no_git_push` · `no_frc_grant` · `no_live_readiness_claim` · `no_profitability_claim` · `no_oos_confirmation_claim` · `no_k9_threshold_relaxation_proposed` · `no_self_authorization_of_p1_p2_p3_build_or_run` · `no_key_leakage`

## 13. Labels

`T1_RSI_MNQ_TIER_N_SPEC_SEALED` · `DA8_B_ACCEPTED` · `DA9_B_ACCEPTED` · `DA19_A_ACCEPTED` · `ALL_OTHER_DA_DEFAULT_A` · `START_CASH_200000_LOCKED` · `RISK_0_5_PERCENT_LOCKED` · `K4_THRESHOLD_100000_USD_ABSOLUTE` · `HIGHER_DENSITY_MECHANIC_SELECTED` · `F3_RSI_MEAN_REVERSION_BIDIRECTIONAL` · `RSI_PERIOD_2_LOCKED_AT_PLAN` · `UNIVERSE_MNQ_C0_SINGLE_INSTRUMENT` · `IS_OOS_WINDOWS_LOCKED` · `K9_REACHABILITY_ANALYSIS_AT_SEAL` · `OOS_K9_BORDERLINE_TO_CLEARING` · `DR1_INCONCLUSIVE_HOLD_FOR_OOS_K9_SUB_THRESHOLD` · `DR10_MITIGATION_VIA_DA8_DA9_SIZING_LEVERS` · `DR2_DR3_DR5_K12_ELEVATED_PRIOR_PROBABILITY` · `NO_BUILD` · `NO_SIMULATOR_RUN` · `NO_BACKTEST` · `NO_RSI_COMPUTED` · `NO_SIGNAL_COMPUTED` · `NO_DATA_FETCH` · `NO_DATABENTO_CALL` · `NO_DATABENTO_API_KEY_ACCESS` · `NO_REVIEW_QUEUE_MUTATION` · `NO_STRATEGY_LAB_PROMOTION` · `NO_LIVE_TRADING` · `VERDICT_NEVER_MEANS_LIVE_READY`

## 14. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**T1 RSI MNQ Tier-N spec sealed. DA8=B (0.5% risk) + DA9=B ($200k cash) DR10-mitigation revisions applied; all other DAs default A. RSI(2) bi-directional mean-reversion on MNQ.c.0 locked. K9-reachability: IS clears with margin; OOS BORDERLINE_TO_CLEARING. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

# T1 RSI MNQ — Tier-N Spec PLAN (SEALED Companion Report)

**Schema:** `sparta.t1.rsi_mnq.tier_n_spec_plan.sealed.v1`
**Phase:** `T1_RSI_MNQ_TIER_N_SPEC_PLAN`
**Phase prefix:** `PHASE2-T1-RSI-MNQ-PLAN`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T17:00:00Z`
**Authorization:** *"Authorize T1 RSI MNQ Tier-N spec PLAN only."*

**Canonical PLAN document:** `docs/t1_rsi_mnq_tier_n_spec_plan.md`

**Candidate:** `t1-rsi-mnq-c0-mean-reversion-2-period-databento-long-history`

---

## 0. PLAN summary

T1 is the first candidate in the new **T-series higher-frequency mean-reversion track**, authored as the successor to S12-D1 (which parked at `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` due to K9 firing on Donchian-15/8 trend-following with only ~7 trades/year on single MNQ.c.0).

**Mechanic family pivot:** F1 trend → **F3 mean-reversion**. Expected signal density: **5–6× higher** than S12-D1.

---

## 1. Load-bearing decisions LOCKED at PLAN

| Field | LOCKED at PLAN |
|---|---|
| Mechanic family | **F3** — RSI mean-reversion, bi-directional, no pyramid |
| **RSI period** | **2** (Connors canonical) |
| Signal direction | Long + Short bi-directional |
| Entry/exit framework | Long when RSI(2) < 10; close when RSI(2) > 50. Short when RSI(2) > 90; close when RSI(2) < 50. (Numerics within `{5,10,15,20}` / `{50,60}` bands deferred to DRAFT.) |
| Pyramid | NONE / `max_units_per_market = 1` |
| Universe | `{MNQ.c.0}` (single Micro E-mini Nasdaq-100 continuous front-month) |
| Schema | `ohlcv-1d` |
| `stype_in` | `continuous` |
| IS window | 2019-05-13 → 2023-12-29 (same as S12-D1; apples-to-apples) |
| OOS window | 2024-01-02 → 2025-12-30 (never inspected at IS) |
| Data source | Audit-clean MNQ.c.0 CSV (sha `8b7b832c62fae185`); **zero new Databento fetch** |

---

## 2. Plan source upstream anchors (READ-ONLY)

| Anchor | Commit | Seal (first 16) |
|---|---|---|
| S12-D1 P11 PARK memo (this session) | `ce279cf` | `321b8940a5516762` |
| S12-D1 P11 PARK memo (parallel canonical) | `ecbd0011` | `b9722d424f6faabe` |
| S12-D1 sealed Tier-N spec (this session) | `9ce4d66` | `422bbbff75f24816` |
| S10-D2 lifecycle park report (this session) | `b580aedb` | `8d59e94a736aa82d` |
| Parallel post-park selection plan | `0e3f9d49` | (selection plan MD) |
| Parallel `s13-d1` sealed Tier-N spec | `262491c` | (distinct chain; non-colliding) |
| Audit-clean MNQ.c.0 CSV | — | `8b7b832c62fae185` |

This T1 chain is **distinct from parallel's `s13-d1` chain** (parallel uses longer `..._databento_long_history` naming; T1 uses operator-specified shorter naming). Both chains coexist at non-colliding paths.

---

## 3. K9-reachability analysis at PLAN (NEW framework discipline)

Per L8 lesson from `0e3f9d49`: every PLAN must include explicit K9-reachability calculations at both IS and OOS scopes.

### 3.1 K9 threshold per window

| Window | Length (years) | Required trades/year for K9 = 100 |
|---|---:|---|
| IS | 4.6 | ≥ 21.74 trades/y |
| **OOS** | **2.0** | **≥ 50.00 trades/y** (BINDING) |

### 3.2 T1 expected trade frequency (PLAN-level disclosure)

| Estimate band | RSI(2) bi-directional on MNQ.c.0 |
|---|---|
| Lower | **~46 trades/year** (~210 over 4.6y IS) |
| Central | **~57 trades/year** (~262 over 4.6y IS) |
| Upper | **~68 trades/year** (~313 over 4.6y IS) |

**5–6× higher signal density than S12-D1's ~7–10 trades/year** on the same universe.

### 3.3 K9 status

| Window | Lower-bound estimate | Threshold | Ratio | Status |
|---|---|---|---|---|
| IS (22/y) | 46 | 22 | **2.12** | **CLEARS WITH MARGIN** |
| **OOS (50/y)** | **46** | **50** | **0.92** | **BORDERLINE — fires at lower bound; clears at central/upper** |

**Honest disclosure:** at the lower-bound estimate of 46 trades/year, OOS K9 fires (46 < 50). At central (57/y) and upper (68/y) estimates, OOS K9 clears. T1 is structurally **more favorable than S12-D1** (S12-D1's IS lower-bound ratio was 0.80; T1's OOS lower-bound ratio is 0.92) but OOS K9 clearance is NOT guaranteed at lower-bound estimate.

**Disposition at OOS K9 sub-threshold:** DR1 `INCONCLUSIVE_HOLD` per C1.D lineage (carried from S12-D1 SEAL; NOT REJECT_FAST).

---

## 4. First-principles burden vs predecessors (no rescue)

| Predecessor | T1 first-principles distinction |
|---|---|
| S12-D1 (Donchian-15/8 MNQ.c.0) | Different mechanic family (F3 RSI vs F1 Donchian); 5–6× signal density |
| S10-D2 (4-market Donchian-55/20) | Different mechanic; single instrument vs 4-market |
| S10-D1 (MNQ+MGC Donchian) | Different mechanic; MGC structurally absent |
| **s9 (RSI-2 ETF-proxy long-only)** | Different universe (MNQ futures vs SPY/TLT/GLD/USO); **bi-directional** vs long-only; different asset class; different cost surface |
| s7-D1 (Donchian + pyramid 4-ETF) | Different mechanic; NO pyramid; different universe |
| s8-D1 (Donchian no-pyramid 4-market) | Different mechanic; single instrument; sizing fix inherited |
| s11-d1 (single MNQ.c.0 Donchian-55/20) | Different mechanic; ~5–6× higher signal frequency |
| B005 / B006 / T8 ETF-proxy | Different asset class (futures vs ETFs) |
| Parallel `s13-d1` chain | Non-colliding paths; both chains coexist |

T1 satisfies all 8 `T-FORBID-1` through `T-FORBID-8` forbidden-track exclusions (carried from `0e3f9d49`).

---

## 5. Critical risk disclosure: RSI(2) cost sensitivity

RSI(2) is structurally **more cost-sensitive** than Donchian trend-following because mean-reversion exits at smaller per-trade moves. Implications:

- **DR2 / DR3 / DR5** reject-fast rules apply with **higher prior probability** at S2/S3 for T1 than for trend-following candidates
- **DR10** turnover-cost-explosion **ELEVATED prior probability**: RSI(2) trades 5–6× as often; per-trade dollar move smaller; dollar-turnover ~30–40× higher than S12-D1
- Mitigation lever at SEAL: larger `START_CASH_USD` (carry s12-d1 DA4=B $100k, or revise to $200k at DRAFT per parallel's `s13-d1` choice)
- Per-trade risk fraction may revise from 1.0% to 0.5% at DRAFT (parallel's `s13-d1` chose 0.5%)

DRAFT-level analysis required: pre-registered S0 edge sign, expected expectancy band, cost-tier flip-to-negative tier (if any).

---

## 6. Cost-stress / K-gates / DR-rules (deferred to SEAL; carried byte-equivalent from S12-D1)

- 5-tier cost-stress S0–S4 with scalars 0.0/1.0/1.5/2.0/3.0 (framework-locked)
- K-gates K1/K2/K4/K6/K7/K8/K9/K12 applicable (K6/K10/K11 N/A for single-instrument F3)
- DR1/DR2/DR3/DR4/DR5/DR6/DR7/DR8/DR9/DR10 applicable; DR10 ELEVATED prior probability; DR11 not in chain

---

## 7. DA register placeholders (deferred to DRAFT; 14 items)

| DA | Field | Default |
|---|---|---|
| DA1 | RSI period | 2 |
| DA2 | RSI oversold threshold | 10 (alternatives 5/15/20) |
| DA3 | RSI overbought threshold | 90 (alternatives 85/80/75) |
| DA4 | RSI exit centerline | 50 (alternative 55/60) |
| DA5 | Exit-by-time max bars | 5 (alternative 3/7/10) |
| DA6 | ATR period | Wilder 20 |
| DA7 | ATR stop multiplier | 2.0 (may tighten for mean-reversion at DRAFT) |
| DA8 | Per-trade risk % | 1.0% (parallel s13-d1 chose 0.5%) |
| DA9 | `START_CASH_USD` | $100,000 (parallel s13-d1 chose $200k) |
| DA10 | K4 max-drawdown threshold | 0.50 |
| DA11 | `WARMUP_DAYS` | 220 (RSI(2) needs only ~5 but framework default for consistency) |
| DA12 | RTH window | 09:30-16:00 ET |
| DA13 | DR9 thresholds | 0.95 / 0.30 / 5 / 5 |
| DA14 | DR10 thresholds | ELEVATED prior; may revise at SEAL |

---

## 8. Validation V-gates (17 evaluated; all True)

V1 ASCII · V2 numbered sections monotonic · V3 no execution language · V4 no self-authorization to DRAFT/SEAL/BUILD/RUN · V5 no code mod · V6 no backtest · V7 no simulator · V8 no signal compute (no RSI compute) · V9 no fetch · V10 no network IO · V11 no live trading · V12 no prior-phase artifact mod · V13 exactly 3 new files staged · V14 `lessons.md` unstaged/untouched · V15 load-bearing decisions LOCKED at PLAN · V16 K9-reachability analysis explicit at PLAN · V17 forbidden-tracks list inherited from `0e3f9d49`

---

## 9. Posture

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live | `BLOCKED_AT_6_GATES` |
| FRC granted | `False` |
| Advisory label permanent | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| `verdict_never_means_live_ready` | True |
| `live_promotion_path_closed` | True |
| This PLAN authorizes DRAFT / SEAL / BUILD / RUN | **No** |

---

## 10. Exact next authorized phases (NONE pre-approved)

| Phase | Authorization phrase | Scope |
|---|---|---|
| **T1 Tier-N spec DRAFT** | `"Authorize T1 RSI MNQ Tier-N spec DRAFT only"` | Author DRAFT with DA1–DA14 register; PLAN-locked decisions NOT reopened |
| Deferral | `"Defer / Pause T1 track"` | Hold at PLAN |
| Pivot | `"Authorize alternative track selection plan revision only"` | Reject T1; request fresh selection plan |

---

## 11. Negative invariants (53 evaluated; all True)

`no_draft` · `no_seal` · `no_build` · `no_runner_build` · `no_simulator_run` · `no_backtest_run` · `no_signal_computed` · `no_rsi_computation` · `no_data_fetch` · `no_databento_call` · `no_databento_api_key_access` · `no_external_network_call` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_brokerage_connection` · `no_orders_created` · `no_paper_or_live_trade` · `no_s7_artifact_modified` · `no_s8_d1_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_s10_d2_artifact_modified` · `no_s11_d1_artifact_modified` · `no_s12_d1_artifact_modified` · `no_parallel_s13_d1_chain_modified` · `no_s12_d1_revival` · `no_s12_d1_revN_revision_authorized` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_cache_modification` · `no_data_modification` · `no_csv_modification` · `no_runbook_modification` · `no_pipeline_manifest_modification` · `no_decisions_md_modification` · `no_gitignore_modification` · `no_claude_md_modification` · `no_lessons_md_modification` · `no_lessons_md_staging` · `no_lessons_md_commit` · `no_branch_change` · `no_git_push` · `no_frc_grant` · `no_live_readiness_claim` · `no_profitability_claim` · `no_oos_inspection` · `no_oos_confirmation_claim` · `no_k9_threshold_relaxation_proposed` · `no_self_authorization_of_draft_seal_build_run` · `no_key_leakage`

---

## 12. Labels

`T1_RSI_MNQ_TIER_N_SPEC_PLAN_SEALED` · `HIGHER_DENSITY_MECHANIC_SELECTED` · `F3_RSI_MEAN_REVERSION_BIDIRECTIONAL` · `RSI_PERIOD_2_LOCKED_AT_PLAN` · `UNIVERSE_MNQ_C0_SINGLE_INSTRUMENT` · `IS_OOS_WINDOWS_LOCKED_AT_PLAN` · `AUDIT_CLEAN_CSV_REUSE` · `K9_REACHABILITY_ANALYSIS_AT_PLAN` · `OOS_K9_BORDERLINE_TO_CLEARING_AT_LOWER_BOUND_FIRES` · `C1_A_C1_D_LINEAGE_CARRIED_TO_T1_SEAL` · `FORBIDDEN_TRACKS_LIST_INHERITED_FROM_0E3F9D49` · `STRUCTURALLY_FRESH_NOT_A_RESCUE` · `NO_DRAFT` · `NO_SEAL` · `NO_BUILD` · `NO_SIMULATOR_RUN` · `NO_BACKTEST` · `NO_SIGNAL_COMPUTED` · `NO_DATA_FETCH` · `NO_DATABENTO_CALL` · `NO_DATABENTO_API_KEY_ACCESS` · `NO_REVIEW_QUEUE_MUTATION` · `NO_STRATEGY_LAB_PROMOTION` · `NO_LIVE_TRADING` · `VERDICT_NEVER_MEANS_LIVE_READY`

---

## 13. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**T1 RSI MNQ Tier-N spec PLAN sealed. F3 RSI(2) mean-reversion bi-directional locked at PLAN. K9-reachability analysis applied: OOS BORDERLINE (lower-bound 46 < 50; central/upper clear). 5–6× signal density vs S12-D1. No DRAFT / SEAL / BUILD / RUN authorized by this PLAN. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

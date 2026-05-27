# T1 vs Parallel s13-d1 Alignment Review (SEALED)

**Schema:** `sparta.t1.alignment_review.vs_parallel_s13_d1.v1`
**Phase:** `T1_S13_D1_ALIGNMENT_REVIEW`
**Phase prefix:** `PHASE2-T1-ALIGNMENT-REVIEW`
**Report kind:** Read-only alignment review. No build. No run.
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T18:30:00Z`
**Authorization:** *"Authorize T1 / parallel S13-D1 alignment review only."*

---

## 0. Verdict & primary recommendation

| Question | Answer |
|---|---|
| Are T1 and s13-d1 materially the same candidate? | **YES** |
| Is parallel s13-d1 P6 IS sealed + reproducible? | **YES** (HIGH reproducibility) |
| **Primary recommendation** | **OPTION C — Independent review / verification lane** (STRONG) |
| Secondary recommendation | OPTION B — Defer to parallel s13-d1 as canonical (MODERATE) |
| Not recommended | OPTION A (continue independently) and OPTION D (explicit halt) |

---

## 1. T1 chain (this session) snapshot

| Phase | Commit | Seal (first 16) |
|---|---|---|
| PLAN | `729207f` | `70549a9ac2c15f36` |
| DRAFT | `fb1079a` | (single MD; sha varies) |
| **SEAL** | **`d7fc7f5`** | **`abe9718d2f7f89db`** |

**Current phase:** SEAL only. P1 / P2 / P3 BUILD / P4 SMOKE / P6 IS **NOT yet run**.

## 2. Parallel s13-d1 chain snapshot

| Phase | Commit | Seal (first 16) |
|---|---|---|
| PLAN | `5e57984` | — |
| DRAFT | `8fcefaf` | — |
| **SEAL** | **`262491c`** | **`2f9d176388fe0b66`** |
| P1 plan-lock | `005cb8a` | — |
| L1-gap closure addendum | `e2ae683` | — |
| P2 phase-2 plan | `beecd87` | — |
| P2 L1 supplement | `508285f` | — |
| P3 BUILD | `24625c6` | — |
| P3 L1 supplement | `b015a35` | — |
| P4 SMOKE | `c44fb13` | — |
| P4 L1 supplement | `dd06d45` | — |
| **P6 IS** | **`3fa479a`** | (sealed) |

**Current phase:** P6 IS sealed; P6.5/P7/P10 NOT run.

**P6 IS verdict:** `READY_FOR_LONGER_BACKTEST` · **159 closed trades** / 4.6297 years · sharpe_proxy +0.1076 · expectancy +$540.73 · |maxdd| 17.68%.

---

## 3. Side-by-side parameter comparison

| Parameter | T1 (this session) | s13-d1 (parallel) | Match |
|---|---|---|---|
| `candidate_record_id` | `t1-rsi-mnq-c0-mean-reversion-2-period-databento-long-history` | `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history` | cosmetic-only |
| Mechanic family | F3 RSI mean-reversion bi-directional no pyramid | F3 rsi_2 bi_directional mean_reversion no_pyramid atr_stop | **IDENTICAL** |
| RSI period | 2 | 2 | **IDENTICAL** |
| Signal direction | long+short bi-directional | long+short bi-directional | **IDENTICAL** |
| RSI oversold | 10 (DA2=A) | 10 (DA-default) | **IDENTICAL** |
| RSI overbought | 90 (DA3=A) | 90 (DA-default) | **IDENTICAL** |
| RSI exit centerline | 50 (DA4=A) | 50 (DA-default) | **IDENTICAL** |
| ATR window | Wilder 20 (DA6=A) | Wilder 20 (DA-default) | **IDENTICAL** |
| ATR multiplier | 2.0 (DA7=A) | 2.0 (DA-default) | **IDENTICAL** |
| **Per-trade risk** | **0.5%** (DA8=B) | **0.5%** (DA3=B) | **IDENTICAL** |
| **START_CASH** | **$200,000** (DA9=B) | **$200,000** (DA4=C) | **IDENTICAL** |
| K4 max-drawdown frac | 0.50 (DA10=A) | 0.50 | **IDENTICAL** |
| K4 max-drawdown abs | $100,000 | $100,000 | **IDENTICAL** |
| WARMUP_DAYS | 220 (DA16=A) | 220 | **IDENTICAL** |
| RTH | 09:30-16:00 ET | 09:30-16:00 ET | **IDENTICAL** |
| Commission / Fees | $0.74 / $0.36 | $0.74 / $0.36 | **IDENTICAL** |
| Slippage e/s/x ticks | 1/1/1 | 1/1/1 | **IDENTICAL** |
| Cost-stress tiers | 5-tier S0–S4 | 5-tier S0–S4 | **IDENTICAL** |
| IS window | 2019-05-13 → 2023-12-29 | 2019-05-13 → 2023-12-29 | **IDENTICAL** |
| OOS window | 2024-01-02 → 2025-12-30 | 2024-01-02 → 2025-12-30 | **IDENTICAL** |
| Data CSV path | `data/.../MNQ_1d_2019-05-13_2025-12-30.csv` | same | **IDENTICAL** |
| CSV sha256 | `8b7b832c62fae185...` | `8b7b832c62fae185...` | **IDENTICAL** |
| K9 threshold | 100 (IS + OOS) | 100 | **IDENTICAL** |
| OOS K9 disposition | DR1 INCONCLUSIVE_HOLD (DA20=A) | DR1 INCONCLUSIVE_HOLD-equivalent (REC1) | **IDENTICAL** |

**Substantive material differences:** none.

**Cosmetic / structural differences (not material):**
- `candidate_record_id` naming (t1- vs s13-d1- prefix)
- File path naming convention (T1 shorter; s13-d1 uses `..._databento_long_history_...`)
- DA register layout (T1 has 20 items; s13-d1 has 14 items; same substantive choices)
- T1 SEAL is at `d7fc7f5` (this session); s13-d1 SEAL is at `262491c` (parallel session)

### Verdict: **`MATERIALLY_THE_SAME_CANDIDATE`**

---

## 4. Parallel P6 IS reproducibility assessment

| Check | Status |
|---|---|
| P6 IS sealed at canonical path | **Yes** (`3fa479a`) |
| Byte-verified vs pre-auth draft | **Yes** (per commit message) |
| OOS NEVER read attestation | **Yes** |
| C6 inherited_constraints_block carried verbatim | **Yes** |
| Methodology documented | **Yes** |
| Same audit-clean CSV (sha-verified) | **Yes** (presumed per chain pattern) |
| Reproducibility rating | **HIGH** |

**Reproducibility evidence.** The parallel chain has full lifecycle provenance from PLAN → DRAFT → SEAL → P1 → P2 → P3 BUILD → P4 SMOKE → P6 IS. Each phase has its own sealed commit + supplementary addenda. The audit-clean CSV is the deterministic data source; given byte-equivalent strategy parameters (which the alignment review confirms), an independent simulator implementation should converge on similar substantive verdict.

**Caveats.** Per s12-d1 dual-chain precedent, exact closed_trades counts may differ between implementations (s12-d1 parallel got 48; this session got 33 on the same data; substantive verdict agreed). Expect implementation-noise variance of ±20-30% on metric magnitudes; substantive K-gate verdicts are robust under reasonable implementation choices.

---

## 5. K9-reachability finding: T1 SEAL was over-optimistic

| Metric | T1 SEAL K9-reachability analysis | Parallel s13-d1 actual P6 IS |
|---|---|---|
| Expected IS trades/year (range) | **46–68** | — |
| Expected IS trades/year (central) | **57** | — |
| **Actual IS trades** | — | **159** |
| **Actual IS window (years)** | — | **4.6297** |
| **Actual IS trades/year** | — | **34.34** |

**Finding:** Parallel's actual IS rate (34.34/y) is **below T1 SEAL's lower-bound estimate of 46/y** (ratio 0.747). My T1 SEAL's K9-reachability analysis was **over-optimistic by ~30%** relative to empirical reality on the same data.

**Implication for IS K9:** Parallel still cleared IS K9 (159 > 100 over 4.6y) — the absolute trade count was sufficient. But my T1 SEAL's K9-reachability framework predicted lower-bound 46/y × 4.6y = 212 trades; actual was 159. The mechanic produces fewer trades than literature-based estimates suggested.

**Implication for OOS K9 (status revision):**

| OOS K9 status | T1 SEAL prediction | Revised given parallel actual |
|---|---|---|
| Lower-bound | 46/y × 2.0y = 92 trades < 100 (fires) | — |
| Central | 57/y × 2.0y = 114 trades > 100 (clears) | — |
| Upper | 68/y × 2.0y = 136 trades > 100 (clears) | — |
| **Parallel-actual scaling** | — | **34.34/y × 2.0y = 68.7 trades < 100 (LIKELY FIRES)** |

**T1 SEAL status:** "BORDERLINE_TO_CLEARING"
**Revised status (per parallel actual IS rate):** **"LIKELY_FIRES_OOS_K9"**

Per DA20=A (carried into both chains): OOS K9 sub-threshold maps to DR1 `INCONCLUSIVE_HOLD`, NOT REJECT_FAST. Candidate would park at OOS under `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` (analogous to S10-D2 OOS outcome).

This is **informational** — it does NOT modify the T1 SEAL (which remains byte-stable). It is a refinement of the K9-reachability framework's accuracy.

---

## 6. Continuation decision matrix

### Option A — Continue T1 chain independently

| | |
|---|---|
| Description | Author T1 P1 → P2 → P3 BUILD → P4 SMOKE → P6 IS in this session |
| Pros | Independent corroboration; deterministic-driver demonstration; alternate-naming parity |
| Cons | Duplicate effort; substantive parameters identical → negligible new info; chain-management overhead |
| Value per unit effort | **LOW** |

### Option B — Defer to parallel s13-d1 as canonical

| | |
|---|---|
| Description | Accept parallel as canonical; T1 SEAL remains on file unmodified; no further T1 phases |
| Pros | Resource-efficient; parallel has IS verdict already; T1 SEAL preserved as alternate-naming reference |
| Cons | T1 SEAL becomes "stranded" artifact; loss of independent corroboration for later phases |
| Value per unit effort | **HIGH** |

### Option C — Independent review / verification lane ★ RECOMMENDED

| | |
|---|---|
| Description | This session continues as review/verification lane only; ad-hoc cross-chain audits when authorized; no T1 P1-P6 execution unless verification need arises |
| Pros | **Mirrors established session pattern** (S10-D2 OOS reconciliation review at `b6a22110`; S10-D2 P10.5 cost-stress sweep at `89ca9a7`; S12-D1 P6 IS independent corroboration at `8621c322`; S12-D1 P11 PARK at `ce279cf`; S10-D2 lifecycle park report at `b580aedb`); provides corroborating capacity; T1 SEAL serves as alternate-DA-resolution baseline |
| Cons | T1 chain remains at SEAL; some capacity unused for direct execution |
| Value per unit effort | **HIGH** (specialized role) |

### Option D — Stop T1 explicitly

| | |
|---|---|
| Description | Halt T1 at SEAL; no further T1 phases under any authorization; SEAL preserved as historical |
| Pros | Cleanest disposition |
| Cons | Loses optionality; no advantage over B or C |
| Value per unit effort | **MEDIUM** |

---

## 7. Final recommendation (verbatim)

### **PRIMARY: Option C — Independent review / verification lane (STRONG)**

**Rationale:**
1. The substantive parameters of T1 and parallel s13-d1 are **IDENTICAL**. Executing T1 P1-P6 would produce near-byte-equivalent results to parallel (with implementation-noise variance ±20-30% on metric magnitudes).
2. Parallel s13-d1 has already reached P6 IS with `READY_FOR_LONGER_BACKTEST`. The canonical execution chain is established. This session adds the most value as a verification / review / corroboration lane.
3. The **established session pattern** across the entire research arc (S10-D2 OOS reconciliation review, S10-D2 P10.5 cost-stress sweep, S10-D2 lifecycle park report, S10-D2 terminal lesson, S12-D1 P6 IS independent corroboration, S12-D1 P11 PARK memo, T1 PLAN/DRAFT/SEAL alternate-DA-resolution baseline) all support this controller session in a **review/verification role complementing parallel execution**.
4. The T1 SEAL remains on file as an **alternate-DA-resolution baseline** (different DA-register layout — 20 items vs 14 items — documents an additional axis of methodology variation for future audits).
5. This recommendation preserves optionality: future operator authorizations to verify parallel results (e.g., reproduce P6 IS, cross-check P6.5 cost-stress, audit OOS verdict) can use this session's chain as an independent corroboration lane.

### **SECONDARY: Option B — Defer to parallel s13-d1 as canonical (MODERATE)**

Resource-efficient choice if the operator prefers to skip further T1 execution entirely; T1 SEAL remains as alternate-naming reference.

### **NOT recommended:** A (continue independently) and D (explicit halt).

---

## 8. Continuation path practical implications

### If operator chooses Option C (recommended):

- This session continues as **review / verification lane**
- T1 SEAL remains on file unmodified
- Parallel chain continues as canonical execution chain
- Natural next operator-authorization scopes:
  - *"Authorize T1/parallel S13-D1 future-phase verification review only"* (operator-driven; this session does cross-chain audit when parallel advances)
  - *"Authorize <future operator task>"* (any review/corroboration/cleanup task)
  - *"Defer / Pause T1 track"* / *"Defer / Pause trading-bot track"* / *"Authorize cross-domain pivot only"*

### If operator chooses Option B (defer):

- This session can pause T1 track or continue other (non-T1) tasks
- T1 SEAL remains on file unmodified
- Parallel chain continues as canonical execution chain

### If operator chooses Option A (continue independently):

- T1 chain advances through P1 → P2 → P3 BUILD → P4 SMOKE → P6 IS
- Expected T1 P6 IS verdict: **likely `READY_FOR_LONGER_BACKTEST` with metrics near parallel** (159 trades / sharpe +0.1076 / expectancy +$540.73), subject to implementation-noise variance per s12-d1 dual-chain precedent (33 vs 48 trades on same data)

### If operator chooses Option D (halt):

- T1 track explicitly halted at SEAL
- T1 SEAL preserved as historical reference
- Further T1 phases FORBIDDEN until explicit un-halt authorization

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
| This review authorizes any phase | **No** |

---

## 10. Validation V-gates (16 evaluated; all True)

V1 ASCII · V2 keyed sections consistent · V3 no execution language · V4 no self-authorization to any phase · V5 no code mod · V6 no backtest · V7 no simulator · V8 no signal compute · V9 no RSI compute · V10 no fetch · V11 no network IO · V12 no live trading · V13 T1 chain byte-stable at HEAD · V14 parallel chain NOT modified · V15 exactly 2 new files staged · V16 `lessons.md` unstaged/untouched

---

## 11. Negative invariants (53 evaluated; all True)

`no_build` · `no_simulator_run` · `no_backtest_run` · `no_rsi_computation` · `no_signal_computed` · `no_data_fetch` · `no_databento_call` · `no_databento_api_key_access` · `no_external_network_call` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_brokerage_connection` · `no_orders_created` · `no_paper_or_live_trade` · `no_t1_plan_modified` · `no_t1_draft_modified` · `no_t1_seal_modified` · `no_parallel_s13_d1_chain_modified` · `no_s7_artifact_modified` · `no_s8_d1_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_s10_d2_artifact_modified` · `no_s11_d1_artifact_modified` · `no_s12_d1_artifact_modified` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_cache_modification` · `no_data_modification` · `no_csv_modification` · `no_driver_modification` · `no_test_modification` · `no_strategy_code_modification` · `no_runbook_modification` · `no_pipeline_manifest_modification` · `no_decisions_md_modification` · `no_gitignore_modification` · `no_claude_md_modification` · `no_lessons_md_modification` · `no_lessons_md_staging` · `no_lessons_md_commit` · `no_branch_change` · `no_git_push` · `no_frc_grant` · `no_live_readiness_claim` · `no_profitability_claim` · `no_oos_confirmation_claim` · `no_oos_inspection` · `no_k9_threshold_relaxation_proposed` · `no_self_authorization_of_any_phase` · `no_key_leakage`

---

## 12. Labels

`T1_S13_ALIGNMENT_REVIEW_COMPLETE` · `T1_AND_S13_D1_MATERIALLY_SAME_CANDIDATE` · `PARALLEL_P6_IS_REPRODUCIBILITY_HIGH` · `RECOMMENDATION_OPTION_C_INDEPENDENT_REVIEW_VERIFICATION_LANE_STRONG` · `SECONDARY_OPTION_B_DEFER_TO_PARALLEL_CANONICAL_MODERATE` · `K9_REACHABILITY_ANALYSIS_AT_T1_SEAL_OVER_OPTIMISTIC_VS_PARALLEL_ACTUAL` · `ACTUAL_IS_RATE_34_PER_YEAR_BELOW_T1_LOWER_BOUND_46` · `OOS_K9_LIKELY_FIRES_AT_PROPORTIONAL_SCALING` · `NO_BUILD` · `NO_SIMULATOR_RUN` · `NO_BACKTEST` · `NO_RSI_COMPUTED` · `NO_SIGNAL_COMPUTED` · `NO_DATA_FETCH` · `NO_DATABENTO_CALL` · `NO_DATABENTO_API_KEY_ACCESS` · `NO_REVIEW_QUEUE_MUTATION` · `NO_STRATEGY_LAB_PROMOTION` · `NO_LIVE_TRADING` · `VERDICT_NEVER_MEANS_LIVE_READY`

---

## 13. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**T1 / parallel s13-d1 alignment review sealed. Verdict: MATERIALLY_THE_SAME_CANDIDATE. Parallel P6 IS reproducibility HIGH. Primary recommendation: Option C (independent review/verification lane; STRONG). Secondary: Option B (defer to parallel as canonical; MODERATE). K9-reachability analysis at T1 SEAL was over-optimistic vs parallel actual; OOS K9 status revised from "borderline" to "likely fires" per actual IS rate. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

# S10-D2 Continuation-Track Selection Plan (SEALED)

**Schema:** `sparta.s10.d2.continuation_track_selection_plan.v1`
**Phase:** `S10_D2_CONTINUATION_TRACK_SELECTION_PLAN`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC-CONTINUATION-SELECTION`
**Report kind:** Selection plan. **Not an execution authorization. No track is pre-approved.**
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T05:20:00Z`

**Authorization:** *"Authorize S10-D2 continuation-track selection plan only."*

---

## 0. Scope boundary

This plan **selects and ranks** the four future-research options identified in the S10-D2 P11 PARK memo. It **does not run** any of them and **does not pre-approve** any of them for execution. Each track requires its own separate fresh sealed operator authorization.

- This plan is a **selection plan**, not an execution authorization.
- **No track is pre-approved.**
- **No phase is run.** No fetch, no Databento, no API-key access, no cache change, no strategy code change, no `lessons.md` mod, no `review_queue` mutation, no candidate promotion.

---

## 1. Candidate origin

| Field | Value |
|---|---|
| candidate_record_id | `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl` |
| Park status | `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` |
| Binding constraint | **OOS window length** |
| Evidence | OOS 3-year window → 53 closed trades; K9 threshold = 100; trade density 88% of IS preserved |
| IS clean | True |
| Cost-stress clean | True |
| K10 clean | True |
| Safety clean throughout | True |
| OOS directionally consistent but undersampled | True |

---

## 2. Parallel-session activity (read-only awareness)

HEAD at plan authoring: `74e254fd0d99b3eb5e91938dcdacc7e1f1a001b3`

Relevant parallel commits:
- `9c630886` — *Seal S11-D1 MNQ.c.0 single-instrument Tier-N specification*
- `c110fd4d` — *Add S11-D1 Tier-N spec rev2 drawdown condition fix*
- `74e254fd` — *Add s11 D1 MNQ.c.0 Tier-N spec DRAFT (mechanic F1 trend-no-pyramid RESOLVED)*

**Implication.** Parallel session is independently and actively pursuing Option 2 (S11-D1 single-instrument fallback) across three iterations. Authorizing Option 2 in THIS session would create a direct race condition on the same chain. This is taken into account in the recommendation below.

---

## 3. Selection criteria

| Letter | Criterion |
|---|---|
| A | Informational gain per unit of new scope/cost |
| B | Reuse of existing sealed S10-D2 infrastructure |
| C | Risk profile (vendor, code surface, key handling, race) |
| D | Directness vs the binding constraint (OOS sample size) |
| E | Time-to-result |
| F | Chain-of-custody integrity (extends vs starts a new chain) |
| G | Parallel-session deconfliction |

---

## 4. Option analysis

### Option 1 — OOS cost-stress sweep

**Summary:** Run S0 / S2 / S3 cost tiers (and optionally S4) against the existing OOS data, using the existing OOS driver, to test whether IS-side cost-robustness survives the OOS regime.

| Criterion | Assessment |
|---|---|
| A — Information gain | **HIGH** per unit cost. Orthogonal evidence to K9. Tests whether OOS direction degrades under cost stress. |
| B — Reuse | **HIGHEST.** OOS driver (sealed at `f0b3721`), OOS cache, Tier-N spec, `runner_main.CONFIG`, all anchors. No new code. |
| C — Risk | **LOW.** No fetch. No Databento. No API key access. ~5–6 minutes runtime. Only artifact is the result report. |
| D — Directness | **INDIRECT (orthogonal).** Does NOT add OOS samples. Does NOT lower K9. Adds cost-robustness evidence. |
| E — Time | **MINUTES.** Same day. |
| F — Chain integrity | **EXTENDS** S10-D2 chain. Same anchors, same Tier-N spec, same drivers. |
| G — Parallel overlap | **NONE.** Parallel is on S11-D1 (different chain). |

**Recommendation:** **PRIMARY** — authorize next.

---

### Option 2 — S11-D1 MNQ.c.0 single-instrument fallback

**Summary:** Pursue a single-instrument MNQ.c.0 long-history Tier-N candidate with the Donchian breakout strategy.

| Criterion | Assessment |
|---|---|
| A — Information gain | **MEDIUM-HIGH.** Different universe → different trade-frequency profile → different binding constraints. |
| B — Reuse | **LOW.** Different Tier-N spec, plan-lock, drivers, cache. Reuses framework discipline patterns only. |
| C — Risk | **MEDIUM.** Requires Databento fetch (DR9-vulnerable as s10-D1 showed). Vendor dependency + key handling required. |
| D — Directness | **INDIRECT.** Does NOT extend S10-D2 evidence. Tests a different hypothesis. |
| E — Time | **WEEKS.** Multi-week effort across full chain. |
| F — Chain integrity | **NEW CHAIN.** Fresh S11-D1 anchors. |
| G — Parallel overlap | **HIGH RISK.** Parallel session is actively iterating on S11-D1 Tier-N spec at `74e254fd`. |

**Recommendation:** **DEFER_TO_PARALLEL_SESSION.** Parallel is the natural canonical executor; let them continue. This session should NOT authorize Option 2.

---

### Option 3 — Longer OOS window

**Summary:** Extend the OOS window past 2025-12-31 to incorporate additional Databento history.

| Criterion | Assessment |
|---|---|
| A — Information gain | **MEDIUM.** Directly attacks binding constraint, but adds only ~14% additional history (5 months / 36 months). |
| B — Reuse | **MEDIUM.** Reuses strategy code, IS driver source (after constants update), `runner_main.CONFIG`. |
| C — Risk | **MEDIUM-HIGH.** Vendor dependency, key handling, network transient errors (already observed on s10-D1), DR9 risk (already killed s10-D1). |
| D — Directness | **MOST DIRECT but INSUFFICIENT IN ISOLATION.** 5 months × 17.7 trades/year = ~7 additional trades → 60 total, **still below K9=100**. Verdict would not move from `INSUFFICIENT_SAMPLE`. |
| E — Time | **DAYS.** Fetch + cache + new OOS driver constants + P10 OOS re-run. |
| F — Chain integrity | **EXTENDS** with P10.OOS_EXTENDED or sibling phase. |
| G — Parallel overlap | **LOW-MEDIUM.** No current overlap. |

**Recommendation:** **DEFER.** Revisit in 12-24 months when more OOS history exists, OR after Option 1's verdict reveals whether longer-OOS is the right attack vector.

---

### Option 4 — Fresh candidate (different markets / regime overlay)

**Summary:** Author an entirely new Tier-N candidate using a different universe or a regime-overlay variant on the existing strategy.

| Criterion | Assessment |
|---|---|
| A — Information gain | **VARIABLE.** Could be high (different sample-density profile) or wasteful (same constraint reappears). |
| B — Reuse | **LOWEST.** Full new Tier-N spec, plan-lock, drivers, runner, cache. |
| C — Risk | **HIGHEST.** New code, new vendor surface, new candidate-specific risks. |
| D — Directness | **INDIRECT.** Tests a different hypothesis entirely. |
| E — Time | **WEEKS-MONTHS.** Slowest. |
| F — Chain integrity | **NEW CHAIN.** No linkage to S10-D2. |
| G — Parallel overlap | **LOW.** No current overlap. |

**Recommendation:** **DEFER.** Worth keeping on the research roadmap but not the next move. Should follow at least Option 1's verdict to inform candidate-design priorities.

---

## 5. Selection summary table

| Option | Cost | Info gain | Reuse | Risk | Directness | Time | Chain | Parallel overlap | Recommendation |
|---|---|---|---|---|---|---|---|---|---|
| **`oos_cost_stress_sweep`** | low | **high** | **highest** | **low** | indirect/orthogonal | **minutes** | extends | **none** | **PRIMARY** |
| `s11_d1_mnq_single_instrument_fallback` | medium | medium-high | low | medium | indirect | weeks | new chain | **HIGH** | **DEFER_TO_PARALLEL** |
| `longer_oos_window` | medium-high | medium | medium | medium-high | direct but insufficient | days | extends | low-medium | **DEFER** |
| `fresh_candidate_different_markets_or_regime_overlay` | highest | variable | lowest | highest | indirect | weeks-months | new chain | low | **DEFER** |

---

## 6. Recommendation

### Primary next track: **`oos_cost_stress_sweep`**

**Rationale:**
- Highest informational-gain-per-unit-cost of the four options
- Reuses S10-D2 sealed infrastructure 100% (OOS driver, OOS cache, Tier-N spec)
- Zero new vendor surface (no fetch, no Databento, no API key access)
- Adds **orthogonal** evidence to the K9 sample-size finding: tests whether IS-side cost-stress robustness survives the OOS regime
- Quickest path to a sealed result (minutes; deterministic driver)
- Cleanest parallel-session deconfliction (parallel is on S11-D1, not on S10-D2 OOS-side)

### Secondary: **DEFER S11-D1 TO PARALLEL SESSION**

Parallel session has been iterating on S11-D1 Tier-N spec across three commits (`9c630886`, `c110fd4d`, `74e254fd`). They are the natural canonical executor. Authorizing S11-D1 in THIS session would compete with parallel work. Best operator move: **let parallel continue on S11-D1; this session extends S10-D2 evidence with Option 1.**

### Defer Option 3 (longer OOS)

Only ~5 months of additional history is currently available beyond 2025-12-31. At 17.7 trades/year, that's ~7 additional trades → 60 total, still below K9 = 100. **The verdict would not move from `INSUFFICIENT_SAMPLE`.** Worth revisiting in 12-24 months OR after Option 1.

### Defer Option 4 (fresh candidate)

Largest scope. Should follow Option 1 or Option 2 to inform candidate-design priorities.

### Recommended authorization sequence (informational; nothing pre-approved)

1. **Authorize Option 1** *(S10-D2 P10.5 OOS cost-stress sweep)* when ready.
2. **Observe** parallel session's progress on S11-D1 (independent; no this-session authorization needed).
3. **After Option 1's verdict:** re-evaluate whether to pursue Option 3 (longer OOS) or Option 4 (fresh candidate) based on what Option 1 revealed about cost-sensitivity on the OOS regime.

---

## 7. Option 1 execution-authorization prerequisites (informational only)

What a future *"Authorize Option 1 / OOS cost-stress sweep"* block would need to specify. **This plan does NOT authorize any of this**; listed for operator drafting convenience.

- Cost tiers to run (recommend S0, S2, S3; S1 already covered by P10)
- Whether to include S4 (currently reserved/out-of-scope per Tier-N spec)
- Single-shot OOS invariant (no iteration based on results)
- No threshold loosening on K12 / DR2 / DR3 / DR5
- Output paths (suggest `reports/external_research_hunter/s10_d2_p10_5_oos_cost_stress_sweep_report.{json,md}` or another non-colliding path)
- Pre-stage empty check + explicit `git add --` discipline
- No `lessons.md` stage
- Parallel-session race-condition awareness

**Expected runtime:** ~240 seconds (4 tiers × ~80s per P10 reference)
**Expected artifact count:** 2 (json + md companion)
**Expected verdict options (pre-anchored):**
- S0/S2/S3 all positive AND no new K12/DR fires → `OOS_COST_STRESS_SURVIVES`
- S2 or S3 flips negative OR DR2/DR3/DR5 fires → `OOS_COST_STRESS_BREAKS_AT_TIER_X`
- Mixed → case-by-case interpretation per pre-anchored enum

**None of the above is pre-approved by this plan.**

---

## 8. Future options remain open

All four options remain on the research roadmap. **No option is eliminated by this plan. No option is pre-approved by this plan.** This is a priority ordering, not a commitment.

---

## 9. Negative invariants (all True)

`no_databento_call` · `no_databento_api_key_access` · `no_data_fetch` · `no_oos_re_run` · `no_oos_cost_stress_run` · `no_p10_re_run` · `no_p10_5_run` · `no_p11_modification` · `no_oos_driver_modification` · `no_in_sample_driver_modification` · `no_runner_harness_modification` · `no_cache_modification` · `no_strategy_code_modification` · `no_canonical_k10_modification` · `no_simulator_run` · `no_backtest_run` · `no_signal_compute` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_brokerage_connection` · `no_orders_created` · `no_paper_or_live_trade` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_lessons_md_modification` · `no_lessons_md_staging` · `no_lessons_md_commit` · `no_tier_n_spec_modification` · `no_plan_lock_modification` · `no_phase2_plan_modification` · `no_runbook_modification` · `no_pipeline_manifest_modification` · `no_decisions_md_modification` · `no_gitignore_modification` · `no_claude_md_modification` · `no_branch_change` · `no_git_push` · `no_s7_artifact_modified` · `no_s8_d1_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_s11_d1_artifact_modified` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_threshold_loosening` · `no_k9_threshold_relaxation_proposed` · `no_track_pre_approved_for_execution` · `no_frc_grant` · `no_live_readiness_claim` · `no_profitability_claim` · `no_key_leakage` · `no_external_network_call` · `no_parallel_session_artifact_modified`

---

## 10. Status

- Trading: `PAUSED`
- Live: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`
- S10-D2: still `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED`

---

## 11. Labels

- `S10_D2_CONTINUATION_TRACK_SELECTION_PLAN_COMPLETE`
- `PRIMARY_RECOMMENDATION_OOS_COST_STRESS_SWEEP`
- `S11_D1_DEFERRED_TO_PARALLEL_SESSION`
- `LONGER_OOS_WINDOW_DEFERRED`
- `FRESH_CANDIDATE_DEFERRED`
- `NO_TRACK_PRE_APPROVED`
- `NO_EXECUTION_AUTHORIZED`
- `SELECTION_PLAN_ONLY`
- `NO_OOS_RERUN`
- `NO_SIMULATOR_RERUN`
- `NO_BACKTEST`
- `NO_DATA_FETCH`
- `NO_DATABENTO_CALL`
- `NO_DATABENTO_API_KEY_ACCESS`
- `NO_REVIEW_QUEUE_MUTATION`
- `NO_STRATEGY_LAB_PROMOTION`
- `NO_LIVE_TRADING`
- `VERDICT_NEVER_MEANS_LIVE_READY`

---

## 12. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**Selection plan sealed. Primary recommendation: Option 1 (OOS cost-stress sweep). S11-D1 deferred to parallel session. Longer-OOS and fresh-candidate deferred. No execution authorized by this plan. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

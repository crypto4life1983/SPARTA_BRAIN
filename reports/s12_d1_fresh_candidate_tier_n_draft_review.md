# S12-D1 Fresh-Candidate Tier-N DRAFT Review (SEALED)

**Schema:** `sparta.s12.d1.fresh_candidate_tier_n_draft_review.v1`
**Phase:** `S12_D1_FRESH_CANDIDATE_TIER_N_DRAFT_REVIEW`
**Phase prefix:** `PHASE2-S12-D1-REVIEW`
**Controller session:** THIS_SESSION_ONLY
**Report kind:** Read-only review of parallel-session DRAFT. No modification. No build.
**Sealed at (UTC):** `2026-05-27T14:35:00Z`

**Authorization:** *"Authorize S12-D1 fresh-candidate Tier-N spec draft review only."*

---

## 0. DRAFT under review

| Field | Value |
|---|---|
| Path | `docs/s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_tier_n_spec_DRAFT.md` |
| Commit | `7e9c86799e5d9b0cecfb34a0de16bdda4eaf9b71` |
| Subject | *"Add s12 D1 MNQ.c.0 Donchian-15/8 fresh-candidate Tier-N spec DRAFT (mechanic family + Donchian 15/8 LOCKED at PLAN)"* |
| Predecessor PLAN | `b4eac65` |
| DRAFT status | DRAFT not SEALED; 14 DA items pending operator confirmation at SEAL turn |
| Lines | 397 |
| Sections | 17 |

---

## 1. Candidate summary (Task 2)

| Field | Value |
|---|---|
| candidate_record_id | `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history` |
| Symbol / universe | **`{MNQ.c.0}` only** (1 symbol; single Micro E-mini Nasdaq-100 continuous front-month) |
| Mechanic family | **F1** — Long+Short Bi-Directional Donchian Trend, No Pyramid, ATR-based Stop |
| Donchian entry N | **15 days** (load-bearing departure from s11-d1 v1's 55) |
| Donchian exit M | **8 days** (load-bearing departure from s11-d1 v1's 20) |
| Pyramid | NONE / max_units_per_market = 1 |
| Data source | Databento `GLBX.MDP3`, `ohlcv-1d`, `stype_in=continuous` |
| Data reuse | **REUSES audit-clean MNQ.c.0 CSV from s10-D1 byte-equivalent** (sha `8b7b832c62fae185...`); **zero new Databento fetch required** |
| IS window | **2019-05-13 → 2023-12-29** (~4.6 years; 1,443 rows audit-confirmed) |
| OOS window | **2024-01-02 → 2025-12-30** (~2 years; 622 rows structural only) |
| Expected IS trade count | **80-200** (central ~140); 3-4× s11-d1's expected 25-50 |
| Cost-stress tiers | S0 / S1 / S2 / S3 / **S4** (5-tier; locked at SEAL) |
| Starting cash (DA4=A default) | $50,000 |
| Total SEAL invariants | **25** |

---

## 2. Task 3 — K9 / sample-size mitigation assessment

| Item | Finding |
|---|---|
| Problem that parked s10-D2 | OOS closed_trades = 53 on 3-year window for 4-market Donchian-55/20 portfolio; below K9 = 100 |
| s12-d1 mitigation mechanic | Shorten Donchian lookbacks 55/20 → 15/8 (~3-4× signal density) on single instrument |
| **DRAFT admission (§10 verbatim)** | *"K9 risk: borderline at lower bound — lower estimate 80 < K9; central estimate ~140 clears; upper estimate 200 clears with margin"* |
| **IS K9 addressed explicitly** | **Yes** — passes at central + upper estimate; borderline at lower |
| **OOS K9 addressed explicitly** | **No** — DRAFT silent on OOS expected trade count |

### Proportional OOS K9 scaling check (this review)

| IS estimate | IS trades | Scaling factor (2.0 / 4.6) | Implied OOS trades | Clears K9 = 100? |
|---|---|---|---|---|
| Lower | 80 | 0.435 | **35** | **No** |
| Central | 140 | 0.435 | **61** | **No** |
| Upper | 200 | 0.435 | **87** | **No** |

**At all three IS estimate bounds, proportional scaling yields OOS trade counts BELOW the K9 threshold of 100.** This is the same binding constraint that parked s10-D2.

**Verdict on K9:** `PARTIAL_K9_MITIGATION` — IS K9 addressed; OOS K9 not addressed; proportional scaling suggests OOS K9 is likely to re-fire.

---

## 3. Task 4 — Not-a-rescue assessment

DRAFT §2 explicitly addresses first-principles burden against every parked predecessor:

| Predecessor | First-principles distinction |
|---|---|
| s11-d1 v1 (Donchian-55/20 sealed) | Different Donchian periods (15/8 vs 55/20); s11-d1 v1 SEAL §9 invariant *requires* fresh `candidate_record_id` for any period change — s12-d1 satisfies structurally |
| s10-D2 (4-market Donchian-55/20 portfolio; PARKED) | Different universe (single MNQ.c.0 vs 4-market); different periods |
| s10-D1 MNQ+MGC | Different universe (MNQ.c.0 only); MGC structurally absent |
| s9 (RSI-2 mean-reversion ETF-proxy; PARKED) | Different mechanic family; different universe |
| s7-D1 (Donchian + pyramid ETFs) | NO pyramid; different universe |
| B006_001 / B006_002 (SPY vol-targeting) | No leverage cap; DR11 structurally absent |
| T8 ETF-proxy umbrella | Universe is futures; T8 does not apply |

**Verdict:** `STRUCTURALLY_FRESH_NOT_A_RESCUE`

---

## 4. Task 5 — Cost-stress from day 1

DRAFT §9 locks cost-stress at SEAL (carried byte-equivalent from s11-d1 v1):

| Tier | cost_scalar | slippage_scalar | Note |
|---|---|---|---|
| S0 | 0.0 | 0.0 | zero-cost ideal |
| S1 | 1.0 | 1.0 | baseline retail |
| S2 | 1.5 | 1.5 | stressed retail |
| S3 | 2.0 | 2.0 | adversarial |
| S4 | 3.0 | 3.0 | extreme adversarial |

- Tick: 0.25 index pts; $0.50 / tick (MNQ.c.0)
- Commission: $0.74 round-trip; Fees: $0.36 round-trip; Slippage: 1/1/1 ticks (entry/stop/exit)
- Pre-registered S0 edge sign: open question (no a-priori claim)
- Pre-registered K12 composite: DR2 + DR3 (S2/S3/S4 degrade >50% or sign flip)
- DR10 (turnover-cost-explosion) thresholds locked: `annual_turnover ≤ 0.50` AND `S2 cost drag ≤ 0.05`

**Verdict:** `COST_STRESS_FROM_DAY_1_FULLY_SPECIFIED`

---

## 5. Task 6 — No live / Strategy Lab / review_queue path

DRAFT §13 enumerates **25 SEAL invariants**:

- 7 inherited B005_NNN framework (incl. `no_live_trading`, `no_strategy_lab_promotion`, `no_review_queue_mutation`, `no_brokerage_connection`, `no_external_network`, `no_databento_at_runtime`, `no_production_signal`)
- 4 inherited B006_001 (incl. `no_profitability_claim`, `no_dr_redefinition_post_seal`)
- 2 inherited B006_002 (incl. `no_warmup_order_submission`)
- 5 inherited s10-D1-specific (incl. `databento_api_key_read_from_env_only_never_logged_or_saved`)
- 3 inherited s11-d1-specific (incl. `single_instrument_universe_NO_widening_post_seal`)
- **4 new s12-d1-specific** (incl. `donchian_15_8_locked_at_plan_no_retreat_to_55_20`, `mechanic_family_lock_at_plan_no_reopening_at_draft_or_seal`)

Permanent status surface: `Trading=PAUSED`, `Live=BLOCKED_AT_6_GATES`, `FRC=NEVER_GRANTED`, `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE=permanent`.

**Verdict:** `NO_LIVE_STRATEGY_LAB_REVIEW_QUEUE_PATH`

---

## 6. Task 7 — Blockers

| Topic | Status | Note |
|---|---|---|
| Data availability | **NOT_A_BLOCKER** | Audit-clean MNQ.c.0 CSV reused byte-equivalent from s10-D1; DR9-clean; zero new Databento fetch |
| IS/OOS split | **NOT_A_BLOCKER** | IS 4.6y / 1,443 rows; OOS 2y / 622 rows; cleanly defined |
| Cost model | **NOT_A_BLOCKER** | 5-tier from day 1; thresholds locked |
| Thresholds | **NOT_A_BLOCKER** | K9, K4, DR9, DR10 all locked at SEAL |
| Similar to parked candidates | **NOT_A_BLOCKER** | §2 explicit first-principles burden against 8 predecessors |
| Insufficient trade-density rationale | **PARTIAL_CONCERN** | IS density rationale strong; **OOS density implicit, likely below K9** |
| DR10 turnover-cost-explosion risk | **FLAGGED_WITH_MITIGATION** | ELEVATED prior probability flagged; DA4=B is the mitigation lever |

---

## 7. Task 8 — Review verdict

### Verdict: **`DRAFT_REVIEW_PASS_WITH_CLARIFICATIONS`**

**Strength:** STRONG on structure / MODERATE on K9 OOS mitigation

**Rationale:**
- DRAFT is comprehensive across all 17 sections expected for a Tier-N spec
- Mechanic family + Donchian-15/8 locked at PLAN; DRAFT does not reopen
- Universe / Dataset / Schema / `stype_in` / IS-OOS windows / cost-stress / sample-size / K-gates / DR-gates all locked
- First-principles burden against all parked predecessors explicitly addressed (§2)
- Cost-stress from day 1 with 5-tier matrix and locked thresholds
- No live / no Strategy Lab / no review_queue / no brokerage (25 sealed invariants)
- Trade-density rationale honest at IS (80-200; borderline-to-clearing)
- Audit-clean MNQ.c.0 data reused byte-equivalent (zero new Databento call)
- DA register DA1-DA14 well-bounded (DA1-DA5 genuinely negotiable; DA6-DA14 framework-locked)

---

## 8. Clarifications for SEAL turn

### C1 — OOS K9 handling (**SUBSTANTIVE**)

**Issue.** DRAFT addresses IS K9 explicitly (§10) but is silent on OOS K9. By proportional scaling, all three IS estimate bounds yield OOS trade counts of **35–87**, below the K9 threshold of 100. This is the same binding constraint that parked s10-D2.

**Options for operator at SEAL:**
| Option | Label | Detail |
|---|---|---|
| **C1.A** | **Accept OOS K9 risk as structural test** | Pre-acknowledge OOS K9 may still fire; if it does, candidate parks under `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` but with cleaner cost-stress + trade-density story. **Most disciplined option.** |
| C1.B | Extend OOS window | Push OOS end past 2025-12-30 (~5 months currently available; requires fresh Databento fetch authorization). Pushes central OOS estimate ~61 → ~74; still below K9. |
| C1.C | Pivot to multi-symbol Donchian-15/8 | Add a second symbol to roughly double trade density. Conflicts with `single_instrument_universe_NO_widening_post_seal` invariant; requires fresh `candidate_record_id`. |
| **C1.D** | **Affirm OOS K9 sub-threshold → DR1 INCONCLUSIVE_HOLD** | Already implied by DRAFT §8.2 DR1. Affirm at SEAL that OOS K9 under-fire maps to DR1 not REJECT_FAST. |

**Recommended at review time:** **C1.A combined with C1.D affirmed at SEAL.** Accept that OOS K9 may still fire; treat it as the structural test of the fresh-candidate hypothesis. Map to DR1 INCONCLUSIVE_HOLD (not REJECT_FAST) to preserve IS evidence for future cross-reference.

### C2 — DR10 mitigation lever DA4 (**INFORMATIONAL**)

DR10 turnover-cost-explosion has ELEVATED prior probability under Donchian-15/8. DA4 = B (raise START_CASH $50k → $100k) reduces per-dollar commission/slip pressure by halving contracts-per-trade.

**Recommended at SEAL:** DA4 = B (operator decides; the elevated DR10 risk is real and worth the mitigation).

### C3 — DA register completeness (INFORMATIONAL)

14 items; DA1-DA5 genuinely negotiable, DA6-DA14 framework-locked. **No additional clarifications needed for the DA register itself.**

### C4 — Post-OOS data use (INFORMATIONAL)

DRAFT §7 marks 2026-01-02 onward as informational only. Confirm at SEAL that post-OOS data cannot be re-promoted to OOS scope (already locked by `oos_inspection_blocked_at_in_sample` invariant).

---

## 9. Posture at review time

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live | `BLOCKED_AT_6_GATES` |
| FRC granted | `False` |
| Advisory label permanent | `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| `verdict_never_means_live_ready` | True |
| `live_promotion_path_closed` | True |
| This review authorizes anything | **No** |
| This review modifies s12-d1 DRAFT | **No** |
| This review authorizes SEAL / BUILD / RUN | **No** |

---

## 10. Negative invariants (all True)

`no_s12_d1_draft_modification` · `no_s12_d1_plan_modification` · `no_build` · `no_runner_build` · `no_simulator_run` · `no_backtest_run` · `no_signal_computed` · `no_data_fetch` · `no_databento_call` · `no_databento_api_key_access` · `no_external_network_call` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_s7_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_s10_d2_artifact_modified` · `no_s11_d1_artifact_modified` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_cache_modification` · `no_data_modification` · `no_driver_modification` · `no_test_modification` · `no_strategy_code_modification` · `no_tier_n_spec_modification` · `no_plan_lock_modification` · `no_phase2_plan_modification` · `no_runbook_modification` · `no_pipeline_manifest_modification` · `no_decisions_md_modification` · `no_gitignore_modification` · `no_claude_md_modification` · `no_lessons_md_modification` · `no_lessons_md_staging` · `no_lessons_md_commit` · `no_branch_change` · `no_git_push` · `no_brokerage_connection` · `no_orders_created` · `no_paper_or_live_trade` · `no_frc_grant` · `no_live_readiness_claim` · `no_profitability_claim` · `no_oos_confirmation_claim` · `no_self_authorization_of_seal_or_build` · `no_key_leakage`

---

## 11. Labels

- `S12_D1_DRAFT_REVIEW_COMPLETE`
- `REVIEW_VERDICT_REPORTED`
- `DRAFT_REVIEW_PASS_WITH_CLARIFICATIONS`
- `STRUCTURALLY_FRESH_NOT_A_RESCUE`
- `COST_STRESS_FROM_DAY_1_VERIFIED`
- `NO_LIVE_STRATEGY_LAB_REVIEW_QUEUE_PATH_VERIFIED`
- `K9_IS_MITIGATION_VERIFIED`
- `K9_OOS_PARTIAL_MITIGATION_CLARIFICATION_NEEDED`
- `C1_OOS_K9_HANDLING_CLARIFICATION_NEEDED`
- `DR10_ELEVATED_RISK_MITIGATION_LEVER_DA4_FLAGGED`
- `NO_BUILD`
- `NO_SIMULATOR_RUN`
- `NO_BACKTEST`
- `NO_SIGNAL_COMPUTED`
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

**S12-D1 DRAFT review sealed. Verdict: `DRAFT_REVIEW_PASS_WITH_CLARIFICATIONS`. Substantive clarification C1 needed at SEAL (OOS K9 handling). Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**

# S12-D1 P11 Lifecycle Park Memo (SEALED)

**Schema:** `sparta.s12.d1.mnq_c0.donchian_15_8.p11_park_memo_sealed.v1`
**Phase:** `S12_D1_P11_LIFECYCLE_DECISION`
**Phase prefix:** `PHASE2-S12-D1-P11`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T16:35:00Z`
**Authorization:** *"Authorize s12 D1 P11 PARK memo only."*

**Candidate:** `s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history`

---

## 0. Lifecycle transition

| Field | Value |
|---|---|
| Lifecycle state before this memo | `ACTIVE_RESEARCH` |
| **Lifecycle state after this memo** | **`PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS`** |
| Operational status transition | `ACTIVE_RESEARCH -> PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` |
| Terminal for this `candidate_record_id` | **True** |

### Park status enum allowed (extended set across recent candidates)

`PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` ← **selected (this candidate)**
`PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` (s10-D2)
`PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED` (s8-D1 precedent)
`PARKED_OOS_REFUTED`
`PARKED_PENDING_LONGER_OOS_WINDOW`
`PARKED_FAIL_SAFETY`
`PARKED_REJECT_FAST_COST_STRESS`

---

## 1. Chain phase inventory (this session)

| Phase | Commit | Seal (first 16) |
|---|---|---|
| Sealed Tier-N spec | `9ce4d66` | `422bbbff75f24816` |
| P1 plan-lock | `bd7245ee` | `f19a7a4c9967cefb` |
| P2 phase-2 plan | `2b27acc2` | `0bcfe99ca1dc1010` |
| P3 BUILD | `b97331a` | `8c6ec346029ae8a9` |
| P4 SMOKE | `8cfdeb1` | `fde4a4524cda82cb` |
| **P6 IS diagnostic** | `8621c322` | `b984b85fe2772e08` |

**Phases SKIPPED due to INSUFFICIENT_SAMPLE at IS:** P6.5 cost-stress, P7 decision memo, P10 OOS gate, P10.5 OOS cost-stress.

The chain hit K9 at IS and parks. Cost-stress / decision memo / OOS phases would not change the verdict — they are moot.

---

## 2. P6 IS verdict anchor

| Metric | Value |
|---|---|
| C7 verdict | **`INSUFFICIENT_SAMPLE`** |
| closed_trades_count_observed | **33** |
| K9 threshold | 100 |
| **K9 fired** | **True** |
| K_fires at S1 | `K9_closed_trades_lt_100` only |
| net_pnl_usd (informational) | +$6,277.14 |
| expectancy_per_trade_usd | +$190.22 |
| sharpe_proxy_per_trade | +0.16773 |
| trade_curve_maxdd_pct | −3.78% |
| win_rate_pct | 45.45 |
| long_trades / short_trades | 19 / 14 |
| K-gates NOT triggered at S1 | K1, K2, K4, K6, K11 (all clear) |

**Informational economics disclaimer.** Positive headline economics (sharpe / expectancy / net PnL) do **NOT** override the K9 verdict. C8 weak-performance-rejection framework applies: **insufficient sample size is dispositive regardless of in-sample positivity.**

---

## 3. Park decision driver

| Driver | Status |
|---|---|
| **Primary** | K9 fires at IS phase (closed_trades=33 < threshold=100) |
| **Secondary** | P2 plan IS estimate (80–200; central 140) was over-optimistic; actual ~7 trades/year on single MNQ.c.0 over 4.6y is below P2 lower bound of 80 |
| C8 weak-performance-rejection applied | True |
| K9 gate triggered at | `P6_IS_DIAGNOSTIC` |
| K9 threshold inviolacy preserved | True |
| K9 relaxation authorized | **No** |
| Donchian period modification authorized | **No** |
| ATR period or multiplier modification authorized | **No** |
| START_CASH modification authorized | **No** |
| Parameter iteration authorized | **No** |
| DR redefinition authorized | **No** |

---

## 4. K9 mitigation hypothesis: **FALSIFIED at IS**

| Source | Expected | Actual |
|---|---|---|
| DRAFT estimate (lower bound) | 80 | — |
| DRAFT estimate (central) | 140 | — |
| DRAFT estimate (upper bound) | 200 | — |
| **This session P6 IS** | — | **33** |
| Parallel session P6 IS | — | 48 |

| Ratio | Value |
|---|---|
| Actual / DRAFT lower bound | 0.413 |
| Actual / DRAFT central | 0.236 |
| Actual below DRAFT lower bound? | **Yes** |
| Actual below K9 threshold? | **Yes** |
| **Hypothesis falsified at IS** | **Yes** |

Locks reinforced by this park:
- `do_not_authorize_fresh_donchian_n_m_revision_via_this_candidate_id`
- `do_not_iterate_parameters_to_seek_higher_trade_count`
- `donchian_n_m_locked_at_PLAN_no_retreat_to_55_20_AND_no_advance_to_10_5_via_this_candidate_id`

---

## 5. C1.A / C1.D reinforcement at P11 PARK

- **C1.A** (originally at SEAL `9ce4d66`): OOS proportional-scaling expected 35/61/87 trades across lower/central/upper IS estimates; all below K9=100; OOS K9 may fire; structural test of fresh-candidate hypothesis.
- **C1.D** (originally at SEAL): OOS K9 sub-threshold maps to DR1 `INCONCLUSIVE_HOLD` (not REJECT_FAST).
- **Actual IS rate observed at P6:** ~7.17 trades/year on real audit-clean MNQ.c.0 IS window.
- **Implied OOS trade count at actual rate:** approximately **14 trades** over 2-year OOS window — vastly below K9=100.
- **Summary:** C1.A's structural unreachability framework was correct **and conservatively understated.** The actual IS trade density was even lower than the P2 lower-bound estimate, meaning OOS K9 (if reached) would fire even more decisively than C1.A's proportional-scaling prediction.

C1.A + C1.D binding preserved at P11.

---

## 6. Comparison vs s10-D2 PARK precedent

| | s10-D2 | s12-d1 |
|---|---|---|
| Park status | `PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED` | `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` |
| K9 fired at | **OOS** | **IS** |
| Lifecycle phase reached | P11 (full P6→P6.5→P7→P10→P11) | P11 (P6→P11; skipped intermediate phases) |
| Binding constraint root | OOS window length (3y) on 4-market Donchian-55/20 | IS trade density on single MNQ.c.0 Donchian-15/8 |

**Common lessons:**
- Both produced clean phase pre-park lifecycles
- Both fired K9 as the binding constraint
- Both correctly parked without threshold loosening
- Both preserved all safety K-gates clear (no K1/K2/K4/K6 fires)
- Framework discipline held: positive headline economics did not override K9 verdict

**Different lessons:**
- s10-D2: OOS-window-length-binding ⇒ sample-size constrained at OOS
- s12-d1: Single-instrument trade-density-binding ⇒ universe choice was structurally too narrow

S12-D1 parks **earlier in the lifecycle** than s10-D2 (IS not OOS).

---

## 7. Comparison vs parallel session P11 PARK

| | Parallel (`ecbd0011`) | This session (this commit) |
|---|---|---|
| Park status enum | `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` | `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` |
| P6 closed_trades | 48 | 33 |
| Lifecycle terminal | True | True |
| Path | `reports/s12_d1_p11_lifecycle_memo_sealed.{json,md}` | `reports/external_research_hunter/s12_d1_..._p11_park_memo_sealed.{json,md}` |

**Two independent chains converge at the same park status.** Both falsify the K9 mitigation hypothesis on real audit-clean MNQ.c.0 data. Substantive verdict identical.

---

## 8. Lessons learned (carried byte-equivalent from parallel chain; `lessons.md` NOT modified)

Per operator's standing no-lessons-md-staging invariant, lifecycle lessons are documented in **this sealed park memo only**, not appended to `lessons.md`.

1. Donchian-15/8 on a single MNQ.c.0 instrument over 4.6y produces ~7–10 trades/year (this session 7.17/y; parallel 10.4/y), **NOT** the 17–43 trades/year linear-scaling estimates suggested. DRAFT estimate (80–200) was **~2–3× over-optimistic**.
2. K9-mitigation via shorter Donchian periods on a **single futures instrument** is structurally hard. The 4.6y IS window over a single instrument has limited signal density even at Donchian-15/8. Future candidates likely need either **multi-instrument scope** or **higher-frequency mechanics** (RSI / vol-targeting at shorter intervals).
3. C1.A / C1.D (parallel REC1 analog) structural unreachability framework was correct and **conservatively understated**. Future Phase-2 candidates should apply C1.A-style proportional-scaling-vs-K9 analysis at DRAFT time.
4. Positive headline economics (positive sharpe + expectancy + net PnL) do **NOT** override K9 verdict semantics. C8 framework working as designed.
5. DA4=B START_CASH revision did **not** materially affect trade count (sizing affects contracts-per-trade, not trade-event frequency). The DR10 mitigation lever does **not** address K9 risk.
6. Two independent implementations of the same mechanic on the same data can produce different exact closed_trades counts (33 vs 48) due to cost-model / stop-timing / entry-exit conventions, but **should agree on substantive verdict** (both `INSUFFICIENT_SAMPLE` here). Future Tier-N candidates may benefit from a **shared reference-implementation convention** to reduce implementation-noise.
7. Lifecycle terminal at PARK preserves all phase-pre-park sealed artifacts for future cross-reference; **archived evidence is more valuable than discarding**.

---

## 9. Future research options (NONE authorized by this memo)

| Option | Status | Reason |
|---|---|---|
| Run P6.5 cost-stress on s12-d1 | **NOT_AUTHORIZED** | Cannot change INSUFFICIENT_SAMPLE verdict; moot |
| Run P7 decision memo on s12-d1 | **NOT_AUTHORIZED** | Already effectively decided via this P11 park |
| Run P10 OOS gate on s12-d1 | **NOT_AUTHORIZED** | INSUFFICIENT_SAMPLE does not qualify for OOS eligibility per C7 enum |
| Author fresh `_revN_` revision changing Donchian periods | **FORBIDDEN** | Per Tier-N spec invariant `donchian_15_8_locked_at_plan_no_retreat_to_55_20`; ANY Donchian period change requires fresh `candidate_record_id` |
| Author fresh `candidate_record_id` with different mechanic on MNQ.c.0 (e.g., RSI / vol-targeting) | POSSIBLE | Would require fresh selection plan + fresh PLAN/DRAFT/SEAL lifecycle |
| Authorize s10-D2 longer-OOS-window | DEFER | Per s10-D2 continuation track selection plan; revisit when more OOS history accumulates |
| Pivot to T1 RSI MNQ candidate | NOT_AUTHORIZED_BY_THIS_MEMO | Parallel session has authored a post-park selection plan at `0e3f9d49` recommending T1 RSI MNQ; informational only; requires fresh authorization |

---

## 10. No-promotion attestation

`6_gate_live_block_remains_active` · `permanent_live_block_remains_active` · `no_promotion_to_live` · `no_promotion_to_paper` · `no_promotion_to_frc` · `no_promotion_to_review_queue` · `no_promotion_to_strategy_lab` · `no_promotion_to_idea_memory` · `no_promotion_to_brokerage` · `p11_park_memo_DOES_NOT_grant_any_promotion_pathway`

---

## 11. Park status attestation

| Field | Value |
|---|---|
| Operational status | `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` |
| Park terminal for this `candidate_record_id` | True |
| Revival authorized by this memo | **No** |
| Revival fresh `candidate_record_id` required | **Yes** |
| Revival requires `FRESH_SEALED_RESEARCH_CYCLE` | **Yes** |
| Fresh `_revN_` revision of s12-d1 authorized | **No** |
| Fresh `candidate_record_id` with different Donchian periods | requires fresh selection plan + fresh PLAN/DRAFT/SEAL lifecycle (NOT a `_revN_` of s12-d1) |

**Permanent attributes unchanged by parking:** Trading PAUSED · Live BLOCKED_AT_6_GATES (permanent) · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE (permanent) · `verdict_never_means_live_ready` True · `live_promotion_path_closed` True.

---

## 12. Hard boundaries held this P11 PARK memo turn (53 evaluated; all True)

`no_databento_call` · `no_databento_api_key_access` · `no_data_fetch` · `no_external_network_call` · `no_simulator_run` · `no_backtest_run` · `no_signal_computed` · `no_orders_created` · `no_brokerage_connection` · `no_paper_or_live_trade` · `no_review_queue_mutation` · `no_idea_memory_mutation` · `no_strategy_lab_invoked` · `no_candidate_promoted` · `no_s12_d1_sealed_spec_modified` · `no_s12_d1_p1_plan_lock_modified` · `no_s12_d1_p2_phase_2_plan_modified` · `no_s12_d1_p3_build_modified` · `no_s12_d1_p4_smoke_modified` · `no_s12_d1_p6_is_modified` · `no_runner_harness_module_modified` · `no_test_file_modified` · `no_parallel_session_chain_modified` · `no_s7_artifact_modified` · `no_s9_artifact_modified` · `no_s10_d1_artifact_modified` · `no_s10_d2_artifact_modified` · `no_s11_d1_artifact_modified` · `no_orb_artifact_modified` · `no_step_30_cost_constant_modified` · `no_cache_modification` · `no_data_modification` · `no_csv_modification` · `no_runbook_modification` · `no_pipeline_manifest_modification` · `no_decisions_md_modification` · `no_gitignore_modification` · `no_claude_md_modification` · `no_lessons_md_modification` · `no_lessons_md_staging` · `no_lessons_md_commit` · `no_branch_change` · `no_git_push` · `no_frc_grant` · `no_live_readiness_claim` · `no_profitability_claim` · `no_oos_inspection` · `no_oos_confirmation_claim` · `no_k9_threshold_relaxation_proposed` · `no_dr_redefinition` · `no_donchian_n_m_modification` · `no_atr_modification` · `no_starting_cash_modification` · `no_fresh_revN_revision_authorized` · `no_p6_5_run` · `no_p7_run` · `no_p10_run` · `no_p10_5_run` · `no_self_authorization_of_next_candidate_lifecycle` · `no_key_leakage`

---

## 13. Next-step options post-park (NONE pre-approved)

| Option | Authorization phrase |
|---|---|
| **A — Pivot to alternative track** | `"Authorize <next-candidate> Tier-N spec DRAFT (or PLAN) only"` |
| **B — Cross-domain pivot** | `"Authorize cross-domain pivot only"` |
| **C — Defer / pause** | `"Defer / Pause trading-bot track"` |
| **D — Fresh candidate (different mechanic or universe)** | `"Authorize <fresh-id> selection plan revision only"` |

S12-D1 lifecycle is terminal at this park. All subsequent steps require separate operator authorization.

---

## 14. Labels

`S12_D1_P11_LIFECYCLE_PARK_MEMO_SEALED` · `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS` · `S12_D1_MNQ_DONCHIAN_15_8_FRESH_CANDIDATE` · `TERMINAL_FOR_THIS_CANDIDATE_RECORD_ID` · `K9_FIRED_AT_IS_NOT_OOS` · `K9_MITIGATION_HYPOTHESIS_FALSIFIED_AT_IS` · `TWO_INDEPENDENT_CHAINS_CONVERGE_AT_SAME_PARK_STATUS` · `CORROBORATES_PARALLEL_P11_AT_ECBD0011` · `CLEAN_LIFECYCLE_NO_THRESHOLD_LOOSENING` · `NO_REVIEW_QUEUE_MUTATION` · `NO_STRATEGY_LAB_PROMOTION` · `NO_LIVE_TRADING` · `NO_PAPER_TRADING` · `NO_BROKERAGE_CONNECTION` · `NO_OOS_INSPECTION` · `NOT_LIVE_READY` · `NOT_PAPER_READY` · `NEVER_PROMOTED_TO_STRATEGY_LAB` · `NEVER_INSERTED_INTO_REVIEW_QUEUE` · `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` · `VERDICT_NEVER_MEANS_LIVE_READY`

---

## 15. Seal

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**S12-D1 P11 PARK memo sealed. Lifecycle state: `PARKED_SAFE_BUT_INSUFFICIENT_SAMPLE_AT_IS`. Terminal for this `candidate_record_id`. Two independent chains converge at the same park status. Trading: PAUSED. Live: BLOCKED_AT_6_GATES (permanent). FRC never granted.**

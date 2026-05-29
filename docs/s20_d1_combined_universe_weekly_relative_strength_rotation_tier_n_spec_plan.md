# s20-d1 combined-universe (s18∪s19, 48-name) weekly relative-strength rotation — Tier-N specification PLAN

Status: **PLAN_ONLY** (no code, no spec drafted/sealed, no BUILD, no data fetched, no backtest, no OOS; the next step is a separate operator authorization to advance to a Tier-N spec DRAFT).

Authored: 2026-05-29
Authorization phrase: `Authorize s20-d1 combined-universe weekly relative-strength rotation Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13.`
Origin: **T3** of the post-s19 next-research-track selection plan (`6a79c99`). FRESH candidate on the **fixed union of two already-DR9-passed baskets** — s18 universe (`d86e5d1`; DR9 result_seal `85667ab3…`) ∪ s19 universe (`574fa9e`; DR9 result_seal `0c8e21f2…`). **No fetch/refetch.** Framework binding: **DR10 v2** (`78cd22e`) + **walk-forward K13** (`52a3b60`).

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT/SEAL/BUILD/code/backtest/simulator/signal/fetch/OOS/live. No vendor API / network. **No Strategy Lab / promotion / FRC / broker / paper-via-broker / review_queue mutation.** **REPLICATION, NOT TUNING:** the mechanic is LOCKED byte-equivalent to s18/s19; **no parameter is changed, searched, or tuned** (T-FORBID-22/23). **This is a FRESH s20-d1 candidate — NOT a `_revN_`/patch of s18 or s19.** **No modification/revival of s18/s19/s17/s16/s15/s14/s13/s12** (s18 is OOS_CONFIRMED-frozen; s19 is K9-terminal-frozen). **No lowering K9.** **No retroactive K13/DR10 reinterpretation.** No modification of any sealed artifact. No `lessons.md` modification unless separately authorized. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. Purpose — a SAMPLE-SIZE (OOS-K9 reachability) test, not a clean generalization test

The binding blocker across the weekly-RS line is **OOS turnover at the K9 ≥50/y margin**: top-8 of a **24**-name pool sits right at the edge — s18 cleared it (58.7/y), s19 fell short (43.6/y, INSUFFICIENT_SAMPLE). The edge itself is portable (positive on both independent universes); the open question is whether a **broader ranking pool** lifts OOS turnover clear of the K9 floor **by structure, without tuning**.

s20 tests exactly that: it holds the **IDENTICAL locked mechanic** (incl. **M=8 unchanged**) but ranks over the **48-name union** of the two prior baskets. A larger pool → more names competing near the rank-8 boundary → more frequent top-8 membership flips → more closed trades → higher OOS turnover. **The only change vs s18/s19 is the universe size; no parameter is altered.**

----

## 2. Anti-overfit / selection-bias disclosure (REQUIRED; honest, not eliminated)

**The concern.** The 48-name union = the **s18 basket (OOS_CONFIRMED — known-good)** ∪ the **s19 basket (positive edge, K9-failed)**. Combining baskets that were **already tested** — and in particular **including a basket known to have OOS-confirmed** — introduces a **selection bias**: the combined IS/OOS edge is tilted upward by the s18 names' known-good behavior. **Therefore a positive s20 IS/OOS is WEAKER fresh-generalization evidence than s19 was** (s19 was a genuinely never-tested universe; s20 is not). s20's honest scientific value is the **SAMPLE-SIZE (OOS-K9-reachability-via-breadth) question — NOT independent edge generalization.**

**Mitigants (partial, disclosed):**
1. It is the **UNION of two PRE-COMMITTED baskets** — no name added, dropped, or cherry-picked on individual performance; the universe is mechanically determined, not searched.
2. Mechanic + **all** parameters are byte-identical to s18/s19 — **zero tuning** (T-FORBID-22/23).
3. **M=8 unchanged** (not scaled to top-16) — the breadth effect comes purely from pool size, not a new held-N lever.
4. The **edge is re-proven from scratch at s20 P6 IS** — NOT inherited from s18/s19 (§6).
5. The 48-name pool **dilutes** any single prior basket: at each weekly rebalance the top-8 is drawn from 48, so neither parent basket dominates the held set.

**Residual concern: MODERATE — disclosed, not removed.** Interpretation rule carried into every downstream phase: **read a positive s20 as evidence about OOS-K9 reachability (sample), NOT as fresh edge-generalization.** A null / K9-terminal / DR-rejected s20 remains fully informative (breadth did not solve the sample, or the combined edge did not survive).

----

## 3. First-principles justification of the 48-name union as a sample-size-safe basket

| Question | First-principles answer |
|---|---|
| Why broaden the pool at all? | The recurring blocker is **OOS sample** (K9), not edge sign. s18/s19 show top-8-of-24 sits on the K9 ≥50/y knife-edge (58.7 vs 43.6/y). Sample is a function of ranking-pool breadth at fixed M. |
| Why does breadth raise turnover (not just dilute)? | At fixed **M=8**, a larger ranking pool puts **more names near the rank-8 cutoff**; the marginal (8th) slot changes hands more often → more entries/exits → more closed round-trips → higher turnover. Breadth ↑ ⇒ boundary churn ↑ ⇒ OOS trade count ↑. |
| Why keep **M=8** rather than scale to 16? | Scaling M is a **new design lever** (a parameter change) → borderline tune. Holding **M=8** isolates the breadth-from-universe-size effect with **zero parameter change** — the cleanest anti-tune posture. Side benefit: 8/48 names held ⇒ even more diversification breadth (K10/K6/A7 comfortable). |
| Why the **union** (not a fresh 48-name fetch)? | **Zero fetch** — both baskets are already DR9-passed (`d86e5d1` + `574fa9e`). The union is the natural **pre-committed** combination of the two vetted baskets. (T1 — a fresh never-tested 48-name universe — is the *cleaner* generalization test but is fetch-gated; the operator chose T3 for speed, accepting the §2 selection caveat.) |

----

## 4. Candidate identification

| Field | Proposed value (LOCKED at PLAN) |
|---|---|
| `candidate_record_id` | **`s20-d1-combined-universe-weekly-relative-strength-rotation-48name-large-cap-long-history`** |
| `candidate_family` | **F-xmom: cross-sectional relative-strength rotation, long-only, WEEKLY** (IDENTICAL family to s18/s19) |
| `is_a_replication` | **TRUE** — identical locked mechanic; the only change is the 48-name combined universe |
| `is_a_s18_or_s19_revN_or_tune` | **false** — fresh `candidate_record_id`; no parameter change/search; s18 & s19 frozen/untouched |
| `predecessor_lineage_references_read_only` | s18 SEAL (`7e6aa36`) + s18 P11 (`5dde0f7`); s19 SEAL (`a3aed99`) + s19 P11 (`81563fd`); s18-universe DR9 (`d86e5d1` / `85667ab3…`); s19-universe DR9 (`574fa9e` / `0c8e21f2…`); selection plan (`6a79c99`); `walk_forward_validation_seal` (`52a3b60`); `framework_dr10_revision_seal_v2` (`78cd22e`) |
| `diagnostic_only` | true · `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| DR9 status | **ALREADY PASSED all 48** (24 via `d86e5d1`, 24 via `574fa9e`); **no fetch** |

----

## 5. Universe + mechanic (LOCKED at PLAN; mechanic IDENTICAL to s18/s19)

| Field | LOCKED value |
|---|---|
| Universe (48 = fixed union; **zero overlap** between the two baskets) | **s18 (24):** AAPL, MSFT, NVDA, JPM, XOM, UNH, WMT, KO, META, AMZN, JNJ, CVX, GOOGL, V, MA, HD, PG, COST, ABBV, MRK, BAC, CAT, DIS, COP · **s19 (24):** ORCL, CSCO, ADBE, CRM, AMD, NFLX, TMUS, CMCSA, MCD, NKE, LOW, PEP, PM, MDLZ, GS, MS, WFC, AXP, LLY, ABT, TMO, SLB, EOG, HON — DR9-passed `d86e5d1` + `574fa9e`; reuse only; substitution/widening post-SEAL FORBIDDEN |
| Relative-strength signal | **126-21 skip-month** trailing total return — IDENTICAL to s18/s19 (DA6/DA8) |
| Rebalance cadence `R` | **5 trading days (weekly)** — IDENTICAL (DA11) |
| Held `M` | **8**, equal-weight `1/8` — **IDENTICAL (DA10/DA3); NOT scaled** |
| Direction / exit | long-only; relative-rank rotation exit (no trailing/ATR stop) — IDENTICAL (DA20/DA12) |
| START_CASH / adjustment / vendor / warmup | $100,000 / split_only / tiingo / 160 — IDENTICAL |
| IS / OOS windows | IS 2019-01-02…2023-12-29; OOS 2024-01-02…2025-12-30 — IDENTICAL |
| DA register | DA1–DA22 mirrored byte-equivalent **except DA1 (candidate id), DA14/DA16 (combined data provenance — BOTH dirs), DA17 (48-name union)**; all strategy params (DA6/DA8/DA10/DA11/DA12/DA3/DA20) byte-identical |
| K13 fold scheme (DA22) | identical bar-index scheme (warmup 0-159; F1 160-478 … F5 1436-1758) on the shared **1759-bar** calendar; pre-committed, unsearched |

### 5.1 Calendar-alignment verification (deferred to BUILD)
Both baskets are `row_count=1759`, vendor tiingo, range `20190102…20251230`, split_only. Cross-sectional ranking over 48 names **requires bar-for-bar date alignment** across all 48 CSVs. Both parent sets share the NYSE calendar, so alignment is expected; it is **asserted at P3 BUILD** (a hard precondition for the cross-sectional ranker). Any misalignment → BUILD-time HALT, not a silent reindex.

----

## 6. The EDGE must be RE-PROVEN at P6 IS — it CANNOT be inherited from s18/s19

Per §2, the combined basket's edge is **not assumed**. It is re-tested from scratch on the 48-name union at:
- **s20 P6 IS** — K1 sharpe_proxy>0 AND K2 expectancy>0 on the combined universe (NOT inherited).
- **s20 P6.7 K13** — ≥3/5 folds positive + aggregate>0 + per-fold-OR-aggregate K9.
- **s20 P10 OOS** — DR4 (oos-negative-while-is-positive) on the combined 2024-2025 window.

**Honest framing:** because s20 contains the known-OOS-good s18 basket, a positive IS/OOS is **expected** and is **weak** generalization evidence (§2). The genuinely informative s20 outcomes are: (a) **does OOS turnover clear K9** (the sample question s20 exists to answer), and (b) **does the combined edge survive DR10-v2 cost-drag** under higher turnover (§7).

----

## 7. Reachability tables (PROJECTED from s18/s19 MEASURED; necessary-not-sufficient — binding only at the pre-SEAL re-measurement and at P6/P6.7/P10)

> LESSON_S19_D1_003 governs: pre-SEAL/IS-rate projections are **necessary-not-sufficient**; the binding tests are the DRAFT pre-SEAL K9 re-measurement (signal-only, no P&L; T-FORBID-24) and the phase measurements (P6/P6.7/P10).

### 7.1 Pre-SEAL K9 aggregate (IS) — expected CLEAR (comfortable)
| Basis | s18 measured | s19 measured | s20 projection (48-name, M=8) |
|---|---|---|---|
| IS closed trades | 229 | 226 | **~280–400** (more boundary churn at fixed M; ≥ each parent) |
| K9 aggregate floor | 100 | 100 | **100 — clears comfortably** |

### 7.2 OOS K9 (≥50/y ⇒ ≥100 over 2y) — the BINDING blocker; expected to clear with MORE margin, but UNPROVEN
| Basis | s18 measured | s19 measured | s20 projection |
|---|---|---|---|
| OOS closed trades (2y) | 117 (cleared) | **87 (FAILED)** | **~110–160 (~55–80/y)** |
| vs ≥50/y floor | +8.7/y margin | **−6.4/y (terminal)** | **projected +5–30/y margin** |
| **Honest downside** | — | — | **If 2024-25 top-8 is dominated by sticky mega-caps drawn from both baskets, churn could stay near s19's ~44/y → another K9-terminal outcome is POSSIBLE.** Binding only at P10. |

### 7.3 K13 per-fold (~1.27y/fold) — expected reachable
| Basis | s18 | s19 | s20 projection |
|---|---|---|---|
| folds positive | 3/5 | 5/5 | **≥3/5 projected** (both parents ≥3) |
| per-fold trade count | ~50–72 | ~50–72 | **higher** (broader pool) → per-fold-OR-aggregate K9 more reachable |

### 7.4 DR10 v2 — the COUNTER-PRESSURE gate (honest two-sided tension)
DR10 v2 = `(annual_turnover>0.50 AND S2_cost_drag>0.05) → REJECT_FAST`.
- **Turnover branch (>0.50):** already TRUE for weekly rotation (both parents) — and s20 raises it further. So the AND hinges entirely on the **cost-drag branch**.
- **Cost-drag branch (>0.05):** parents measured **cost_drag <1%** at S2 (≈5× headroom under the 5% ceiling). **The same breadth that helps OOS-K9 (more turnover) also raises cost_drag** — this is the genuine tension in T3. Projection: s20 cost_drag **~1–3%** (up from <1%), **still under 5% → DR10-v2 EXPECTED to clear, but with a NARROWER margin** than the parents.
- **Binding confirmation:** P6.5 cost-stress. A DR10-v2 REJECT_FAST is a **more live possibility** here than for the 24-name parents and must not be discounted.

**Net reachability conclusion:** K9-aggregate clears comfortably; **OOS-K9 is projected to clear with more margin than either parent but is UNPROVEN (sticky-leader downside → another K9-terminal is possible)**; K13 per-fold reachable; **DR10-v2 expected to clear on a narrower cost-drag margin (the breadth-for-K9 trade-off)**. No turnover/P&L is computed at PLAN.

----

## 8. DR register + K-gates (carried; DR10 v2; K13)

DR precedence `DR7→DR1→DR9→DR10→DR6→DR4→DR2→DR3→DR5`; **DR10 v2** by-ref `78cd22e`; DR11 NOT IN CHAIN (unlevered cash equity). K1/K2 binding edge gates (re-proven on s20, §6); **K9 INVIOLATE** (aggregate ≥100; OOS ≥50/y) — **not lowered**; **K13** at P6.7 (by-ref `52a3b60`); K10/K6/A7 diversification load-bearing (top-8 of 48 ⇒ broad sector spread); K11 NOT_APPLICABLE. DR9 = PASSED all 48 (`85667ab3…` + `0c8e21f2…`). The **C6 inherited-constraints block (16 entries)** is carried verbatim at the s20 SEAL (not introduced at PLAN), per prior candidates.

----

## 9. T-FORBID compliance

16/17/18 (not mean-reversion), 19/20/21 (not s16 trend), **22 (locked params; pre-committed unsearched folds; no per-fold refit)**, **23 (combined-universe is a FRESH s20 candidate with the IDENTICAL locked mechanic — NOT a tune/`_revN_` of s18/s19; both frozen)**, **24 (pre-SEAL K9 re-measurement at the s20 DRAFT)** — all CLEARED/ENFORCED. **Plus the §2 selection-bias caveat is disclosed and carried as an interpretation constraint into every downstream phase.**

----

## 10. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/BUILD/fetch/backtest/OOS) | met |
| REPLICATION not tuning; mechanic byte-identical; M=8 unchanged; no param search | met |
| Fresh s20 candidate; **no `_revN_`/patch/modification of s18 or s19** (both frozen) | met |
| No lowering K9; no retroactive K13/DR10; no sealed-artifact modification | met |
| No data fetch (reuse DR9-passed 48-name union) | met |
| Anti-overfit/selection concern disclosed (§2) | met |
| Edge re-proven (not inherited) at s20 P6 IS (§6) | committed-to |
| `lessons.md` not modified this turn | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 11. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s20_d1_combined_universe_weekly_relative_strength_rotation_tier_n_spec_plan.md` | This Tier-N spec PLAN (PLAN only; no JSON sidecar; no seal). |

No other repository file is modified.

----

## 12. Next-step authorization scope

- **Proceed to DRAFT (with the pre-SEAL K9 re-measurement on the 48-name union):** `Authorize s20-d1 combined-universe weekly relative-strength rotation Tier-N spec DRAFT only — bound by DR10 v2 + walk-forward K13; DRAFT carries the pre-SEAL K9 turnover measurement (signal-only, no P&L) on the 48-name union; mechanic locked identical to s18/s19 (no tuning); §2 selection caveat carried.`
- **Defer:** `Defer / Pause s20-d1 at PLAN.`

----

End of PLAN. PLAN-authoring turn only. No code/backtest/fetch/DRAFT/SEAL/BUILD. **s20-d1 is a FRESH candidate that ranks the IDENTICAL byte-locked weekly RS mechanic (126-21 / R=5 / top-8 / long-only / relative-rank exit; M=8 UNCHANGED) over the fixed 48-name UNION of the DR9-passed s18 + s19 baskets — the ONLY change is the universe size. Its purpose is the SAMPLE-SIZE (OOS-K9-reachability-via-breadth) question, NOT clean edge generalization: because the union includes the known-OOS-good s18 basket, a positive result is weak generalization evidence (selection caveat, §2, disclosed and carried). Reachability: K9-aggregate clears comfortably; OOS-K9 projected to clear with more margin than either parent but UNPROVEN (sticky-leader downside → another K9-terminal possible; binding at P10); K13 per-fold reachable; DR10-v2 expected to clear on a NARROWER cost-drag margin — the breadth that helps K9 raises cost_drag. The EDGE is re-proven at P6 IS, never inherited.** No tuning / no param search / M=8 unchanged / no s18-or-s19 `_revN_` / no modification of frozen artifacts; no lowering K9; no revival; no retroactive K13/DR10; no `lessons.md` modification. Trading `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

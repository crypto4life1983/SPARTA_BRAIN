# s19-d1 independent-universe weekly relative-strength rotation — Tier-N specification PLAN (REPLICATION of the s18 mechanic)

Status: **PLAN_ONLY** (no code, no spec drafted/sealed, no data fetched, no backtest, no OOS; the next step is a separate operator authorization to commit this PLAN, then a Tier-N spec DRAFT).

Authored: 2026-05-28
Authorization phrase: `Authorize s19-d1 independent-universe weekly relative-strength rotation Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13 (replication: lock the identical s18 mechanic; no tuning).`
Origin: **R1** of the post-s18 robustness-replication plan (`50e5fcf`). FRESH candidate on the **DR9-passed independent 24-name universe** (`574fa9e`; result_seal `0c8e21f2…`). Framework binding: **DR10 v2** (`78cd22e`) + **walk-forward K13** (`52a3b60`).

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT/SEAL/code/backtest/simulator/signal/fetch/OOS/live. No vendor API / network. No Strategy Lab / promotion / FRC / broker. **REPLICATION, NOT TUNING:** the mechanic is LOCKED byte-equivalent to s18; **no parameter is changed, searched, or tuned** (T-FORBID-22/23). **No `_revN_`/patch/modification of s18** (it is OOS_CONFIRMED and frozen). **No revival of s18/s17/s16/s15/s14/s13/s12.** **No retroactive K13.** No modification of any sealed artifact. No `lessons.md` modification. No commit beyond this PLAN's own authorization. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. Purpose — a generalization test, not a new mechanic

s18-d1 weekly cleared the full ladder (OOS_CONFIRMED_DIAGNOSTIC) but the pass was **fragile**: thin OOS edge (+$210/trade), marginal K13 (3/5), and a **negative most-recent fold F5** (LESSON_S18_D1_003). The binding open question (LESSON_S18_D1_004): **is the s18 edge a generalizing relative-strength premium, or a single-universe artifact?**

s19 answers it by running the **IDENTICAL LOCKED s18 mechanic** on an **independent** 24-name universe (zero overlap with s17/s18). The edge is **NOT assumed** — it is re-tested from scratch on new data at s19 P6 IS / P6.7 K13 / P10 OOS. A positive s19 = corroborating generalization evidence (still DIAGNOSTIC_ONLY); a null/negative s19 = the s18 result was universe-specific.

----

## 2. Candidate identification

| Field | Proposed value (LOCKED at PLAN) |
|---|---|
| `candidate_record_id` | **`s19-d1-independent-universe-weekly-relative-strength-rotation-24name-large-cap-long-history`** |
| `candidate_family` | **F-xmom: cross-sectional relative-strength rotation, long-only, WEEKLY** (IDENTICAL family to s18) |
| `is_a_replication_of_s18` | **TRUE** — identical locked mechanic; only the universe differs |
| `is_a_s18_revN_or_tune` | **false** — fresh `candidate_record_id`; no parameter change/search; s18 frozen/untouched |
| `predecessor_lineage_references_read_only` | `s19_dr9_result` (`574fa9e` / `0c8e21f2…`), `s19_run_book` (`5ef4eaa`), `post_s18_robustness_replication_plan` (`50e5fcf`), `s18_tier_n_spec_seal` (`7e6aa36`), `s18_p11_lifecycle` (`5dde0f7`), `walk_forward_validation_seal` (`52a3b60`), `framework_dr10_revision_seal_v2` (`78cd22e`) |
| `diagnostic_only` | true · `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| DR9 status | **ALREADY PASSED all 24** (independent universe; `574fa9e` / `0c8e21f2…`); no fetch |

----

## 3. Universe + mechanic (LOCKED at PLAN; mechanic IDENTICAL to s18)

| Field | LOCKED value |
|---|---|
| Universe (24, independent) | {ORCL, CSCO, ADBE, CRM, AMD, NFLX, TMUS, CMCSA, MCD, NKE, LOW, PEP, PM, MDLZ, GS, MS, WFC, AXP, LLY, ABT, TMO, SLB, EOG, HON} — ~8 GICS sectors; DR9-passed `574fa9e`; reuse only; widening/substitution post-SEAL FORBIDDEN |
| Relative-strength signal | **126-21 skip-month** trailing total return — IDENTICAL to s18 (DA6/DA8) |
| Rebalance cadence `R` | **5 trading days (weekly)** — IDENTICAL to s18 (DA11) |
| Held `M` | **8 (top third of 24)**, equal-weight `1/8` — IDENTICAL to s18 (DA10/DA3) |
| Direction / exit | long-only; relative-rank rotation exit (no trailing/ATR stop) — IDENTICAL to s18 (DA20/DA12) |
| START_CASH / adjustment / vendor / warmup | $100,000 / split_only / tiingo / 160 — IDENTICAL to s18 |
| DA register | DA1–DA22 mirrored from s18 byte-equivalent **except DA1 (candidate id), DA14/DA16 (s19 data provenance), DA17 (s19 universe)**; all strategy params (DA6/DA8/DA10/DA11/DA12/DA3/DA20) byte-identical to s18 |
| K13 fold scheme (DA22) | identical bar-index scheme (warmup 0-159; F1 160-478 … F5 1436-1758) on the s19 1759-bar calendar; pre-committed, unsearched |

### 3.1 Replication discipline (NOT tuning — T-FORBID-22/23)

The ONLY change vs s18 is the universe. No lookback/skip/cadence/held-N/direction/sizing is altered or searched. The s18 candidate (SEAL `7e6aa36`; P11 `5dde0f7`) is frozen and untouched. This is a like-for-like generalization test; the edge is re-proven independently at s19 P6 IS (it is NOT inherited from s18).

----

## 4. Reachability (PROJECTED from s18's MEASURED clearance; RE-MEASURED at the s19 DRAFT pre-SEAL gate)

The mechanic is identical to s18, which MEASURED (committed): 229 IS closed trades, 117 OOS (58.7/y), per-fold ~54-72. Since s19 runs the same mechanic on a same-size (24-name) basket, the projections below are expected to hold; they are **re-measured signal-only (no P&L) on the s19 universe at the DRAFT pre-SEAL gate** (mirroring s18; T-FORBID-24). No turnover is computed at PLAN.

| Gate | Projected (from s18 measured) | Status |
|---|---|---|
| K9 aggregate (IS, ≥100) | ~200-250 (s18: 229) | expected CLEAR; confirm pre-SEAL |
| K13 per-fold (~1.27y) | ~50-72/fold (s18: 68/69/72/…) | expected CLEAR; confirm pre-SEAL |
| OOS K9 (≥50/y ⇒ ≥100/2y) | ~100-120 (s18: 117) | expected CLEAR; confirm pre-SEAL |
| DR10 v2 | turnover ~20×, cost_drag <1% (s18) | CLEARS (turnover branch alone; AND not triggered) |

----

## 5. The EDGE is the open question (re-proven on independent data; not assumed)

K9/turnover reachability is mechanic-driven and expected to clear (it did for s18). **The binding unknown is whether the relative-strength EDGE appears on this independent universe.** It is tested fresh at:
- **s19 P6 IS** — K1 sharpe_proxy>0 AND K2 expectancy>0 on the independent universe (NOT inherited from s18).
- **s19 P6.7 K13** — ≥3/5 folds positive + aggregate>0 + K9.
- **s19 P10 OOS** — DR4 (oos-negative-while-is-positive) on the independent 2024-2025 window.

**Honest framing:** s18's OOS edge was thin and recently-weak (F5 negative). A clean s19 replication is genuinely uncertain — the replication exists precisely to find out. Any s19 phase may FAIL/REJECT, which would be the informative result (s18 was universe-specific). No outcome is assumed.

----

## 6. DR register + K-gates (carried; DR10 v2; K13)

DR precedence `DR7→DR1→DR9→DR10→DR6→DR4→DR2→DR3→DR5`; DR10 v2 by-ref `78cd22e`; DR11 NOT IN CHAIN. K1/K2 binding edge gates (re-proven on s19); K9 INVIOLATE; **K13** ADDED at P6.7 (by-ref `52a3b60`); K10/K6/A7 diversification load-bearing (top-8 ~8 sectors); K11 NOT_APPLICABLE. DR9 = PASSED all 24 (independent; `0c8e21f2…`).

----

## 7. T-FORBID compliance

16/17/18 (not mean-reversion), 19/20/21 (not s16 trend), **22 (locked params; pre-committed unsearched folds; no per-fold refit)**, **23 (replication on a fresh universe with the IDENTICAL locked mechanic — NOT a tune/`_revN_` of s18; s18 frozen)**, **24 (pre-SEAL K9 re-measurement at the s19 DRAFT)** — all CLEARED/ENFORCED.

----

## 8. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/BUILD/fetch/backtest/OOS) | met |
| REPLICATION not tuning; mechanic byte-identical to s18; no param search | met |
| No `_revN_`/patch/modification of s18 (frozen) | met |
| No revival / no retroactive K13 / no sealed-artifact modification | met |
| No data fetch (reuse DR9-passed independent 24-name) | met |
| `lessons.md` not modified; no commit by this PLAN turn | met |
| Edge re-proven (not inherited) at s19 P6 IS | committed-to |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 9. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s19_d1_independent_universe_weekly_relative_strength_rotation_tier_n_spec_plan.md` | This Tier-N spec PLAN (PLAN only; no JSON sidecar; no seal). |

No other repository file is modified.

----

## 10. Next-step authorization scope

- **Commit this PLAN:** `Authorize commit s19-d1 independent-universe weekly relative-strength rotation Tier-N spec PLAN only.`
- **Proceed to DRAFT (with the pre-SEAL K9 re-measurement on the s19 universe):** `Authorize s19-d1 independent-universe weekly relative-strength rotation Tier-N spec DRAFT only — bound by DR10 v2 + walk-forward K13; DRAFT carries the pre-SEAL K9 turnover measurement (signal-only, no P&L) on the s19 universe; mechanic locked identical to s18 (no tuning).`
- **Defer:** `Defer / Pause s19-d1 at PLAN.`

----

End of PLAN. PLAN-authoring turn only. No code/backtest/fetch/DRAFT/SEAL/BUILD. **s19-d1 is a REPLICATION of the OOS_CONFIRMED s18 weekly mechanic (126-21 / R=5 / top-8 / long-only / relative-rank exit), byte-identical, on an INDEPENDENT 24-name DR9-passed universe — the ONLY change is the universe. K9/turnover reachability is expected to clear (mechanic-driven, demonstrated by s18; re-measured pre-SEAL); the EDGE is the open question, re-proven on independent data at s19 P6 IS / P6.7 K13 / P10 OOS, NOT assumed and NOT inherited.** No tuning / no param search / no s18 `_revN_` / no s18 modification; no revival; no retroactive K13; no sealed-artifact modification; no `lessons.md` modification. Trading `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

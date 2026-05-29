# s21-d1 broader-universe (fresh 48-name) weekly relative-strength rotation — Tier-N specification PLAN (CLEAN generalization test)

Status: **PLAN_ONLY** (no code, no spec drafted/sealed, no BUILD, no backtest, no OOS; the next step is a separate operator authorization to advance to a Tier-N spec DRAFT).

Authored: 2026-05-29
Authorization phrase: `Authorize s21-d1 broader-universe weekly relative-strength rotation Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13.`
Origin: the **T1 path** from the post-s19 selection plan (`6a79c99`), elected at the **s20 P11** (`7ef6488`) to resolve the s20 selection caveat. FRESH 48-name universe, **DR9-passed all 48** (`d76c999`; result_seal `9835c0d2…`; RUN_BOOK `dd69414`). Framework binding: **DR10 v2** (`78cd22e`) + **walk-forward K13** (`52a3b60`).

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT/SEAL/BUILD/code/backtest/simulator/signal/fetch/OOS/live. No vendor API / network. No Strategy Lab / promotion / FRC / broker / review_queue. **REPLICATION, NOT TUNING:** the mechanic is LOCKED byte-equivalent to s18/s19/s20; **no parameter is changed, searched, or tuned** (T-FORBID-22/23). **Fresh s21 candidate — NOT a `_revN_`/patch of s18/s19/s20** (all frozen). **No lowering K9.** **No retroactive K13/DR10 reinterpretation.** No modification of any sealed artifact. No `lessons.md` modification unless separately authorized. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. Purpose — the CLEAN generalization test (resolves the s20 selection caveat)

s20-d1 PASSED the full ladder (OOS_CONFIRMED_DIAGNOSTIC) and proved that **breadth solves the OOS-K9 blocker** — but its 48-name universe was the s18∪s19 UNION, which **includes the known-OOS-CONFIRMED s18 basket**, so it was a SAMPLE-SIZE demonstration, **not clean generalization** (LESSON_S20_D1_002, binding caveat carried through every s20 phase).

s21 closes that gap: it runs the **IDENTICAL byte-locked weekly RS mechanic** on a **FRESH 48-name universe with ZERO overlap vs s17/s18/s19** (DR9-passed). A positive s21 result is therefore **genuine independent generalization evidence** — no name in the basket has ever been backtested under this mechanic. A null/negative s21 = the edge is partly universe-specific (accepted, informative).

----

## 2. Anti-overfit posture (cleanest available; honest residual)

| Dimension | s20 (combined union) | **s21 (fresh universe)** |
|---|---|---|
| Includes a known-OOS-good basket? | YES (s18) → selection bias | **NO — zero overlap with s17/s18/s19** |
| Names ever backtested under this mechanic? | 24 of 48 (the s18 half) | **0 of 48** |
| Generalization reading of a positive result | WEAK (sample-size demo) | **STRONG (clean independent test)** |
| Parameter tuning | none (M=8 fixed) | **none (M=8 fixed; byte-identical)** |

**Honest residual:** the 48 names were chosen as liquid large-caps spanning ~9 sectors and **pre-committed in the RUN_BOOK (`dd69414`) BEFORE any backtest** — selection was by liquidity/sector-spread/listing-history, **never by performance**. There is a mild *composition* choice (which large-caps), but **no performance-based selection** and no look-ahead. This is the cleanest generalization test the framework can run without live-forward data.

----

## 3. Candidate identification

| Field | Proposed value (LOCKED at PLAN) |
|---|---|
| `candidate_record_id` | **`s21-d1-broader-universe-weekly-relative-strength-rotation-48name-fresh-large-cap-long-history`** |
| `candidate_family` | **F-xmom: cross-sectional relative-strength rotation, long-only, WEEKLY** (IDENTICAL family to s18/s19/s20) |
| `is_a_clean_generalization_test` | **TRUE** — fresh universe, zero overlap, identical locked mechanic |
| `is_a_s18_s19_s20_revN_or_tune` | **false** — fresh `candidate_record_id`; no parameter change/search; s18/s19/s20 frozen/untouched |
| `predecessor_lineage_references_read_only` | s21 DR9 result (`d76c999` / `9835c0d2…`), RUN_BOOK (`dd69414`), s20 P11 (`7ef6488`) + SEAL (`e9ec72f`), selection plan (`6a79c99`), walk_forward K13 (`52a3b60`), DR10 v2 (`78cd22e`) |
| `diagnostic_only` | true · `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| DR9 status | **ALL 48 PASS** (fresh; `d76c999` / `9835c0d2…`); calendar-aligned 1759 bars; no fetch |

----

## 4. Universe + mechanic (LOCKED at PLAN; mechanic IDENTICAL to s18/s19/s20)

| Field | LOCKED value |
|---|---|
| Universe (48, fresh; zero overlap) | AVGO, QCOM, TXN, INTC, MU, AMAT, IBM, INTU, NOW, ADI, VZ, T, CHTR, EA, SBUX, TGT, BKNG, MAR, GM, TJX, ROST, MO, CL, KMB, GIS, STZ, PFE, BMY, AMGN, GILD, CVS, CI, ISRG, SYK, C, USB, SCHW, BLK, SPGI, CB, BA, ITW, UPS, RTX, LMT, DE, PSX, VLO — DR9-passed `d76c999`; reuse only; substitution/widening post-SEAL FORBIDDEN |
| Relative-strength signal | **126-21 skip-month** trailing total return — IDENTICAL (DA6/DA8) |
| Rebalance cadence `R` | **5 trading days (weekly)** — IDENTICAL (DA11) |
| Held `M` | **8**, equal-weight `1/8` — **IDENTICAL (DA10/DA3); NOT scaled** |
| Direction / exit | long-only; relative-rank rotation exit (no trailing/ATR stop) — IDENTICAL (DA20/DA12) |
| START_CASH / adjustment / vendor / warmup | $100,000 / split_only / tiingo / 160 — IDENTICAL |
| IS / OOS windows | IS 2019-01-02…2023-12-29; OOS 2024-01-02…2025-12-30 — IDENTICAL |
| DA register | DA1–DA22 byte-equivalent **except DA1 (id), DA14/DA16 (s21 fresh provenance), DA17 (fresh 48-name)**; all strategy params byte-identical |
| K13 fold scheme (DA22) | identical bar-index scheme (warmup 0-159; F1 160-478 … F5 1436-1758) on the shared 1759-bar calendar; pre-committed, unsearched |

### 4.1 Replication discipline (NOT tuning — T-FORBID-22/23)
The ONLY change vs s18/s19/s20 is the universe (fresh names). No lookback/skip/cadence/held-N/direction/sizing is altered or searched. s18/s19/s20 are frozen and untouched. The edge is re-proven independently at s21 P6 IS (it is NOT inherited).

----

## 5. Reachability (PROJECTED from s20's MEASURED clearance at the same 48-name breadth; UNPROVEN on fresh names; re-measured at the s21 DRAFT pre-SEAL gate + binding at P6/P10)

> LESSON_S19_D1_003 / LESSON_S20_D1_003 govern: pre-SEAL/IS-rate projections are necessary-not-sufficient; binding tests are the DRAFT pre-SEAL signal-only measurement (T-FORBID-24) and the phase measurements (P6/P6.7/P10).

| Gate | s20 measured (48-name union) | s21 projection (fresh 48) | Status |
|---|---|---|---|
| K9 aggregate (IS, ≥100) | 284 | comparable (same breadth) | expected CLEAR; confirm pre-SEAL |
| OOS K9 (≥50/y ⇒ ≥100/2y) | 134 (67.2/y, cleared) | ~55-75/y expected | expected CLEAR but UNPROVEN; confirm signal-only at DRAFT, binding at P10 |
| K13 per-fold (~1.27y) | 77/96/81/77/84 (5/5) | sample-sufficient expected | expected reachable; sign re-measured at P6.7 |
| DR10 v2 | turnover 23.9×, cost_drag 1.03% (<5%) | comparable (~1-3%) | expected CLEAR (narrow); confirm at P6.5 |

**The EDGE is the open question** (§6): K9/turnover reachability is breadth-driven and expected to clear (s20 precedent at this breadth); whether the relative-strength EDGE appears on **these fresh names** is genuinely uncertain and is the whole point of the clean test.

----

## 6. The EDGE must be RE-PROVEN at P6 IS — NOT inherited

The fresh-basket edge is **not assumed**. Re-tested from scratch at:
- **s21 P6 IS** — K1 sharpe_proxy>0 AND K2 expectancy>0 on the fresh universe (NOT inherited).
- **s21 P6.7 K13** — ≥3/5 folds positive + aggregate>0 + K9.
- **s21 P10 OOS** — DR4 on the fresh 2024-2025 window.

**Honest framing:** unlike s20, a positive s21 is genuine generalization evidence (no selection bias). But any phase may FAIL/REJECT — that would be the informative result (the weekly RS edge is partly universe-specific). No outcome is assumed.

----

## 7. DR register + K-gates (carried; DR10 v2; K13)

DR precedence `DR7→DR1→DR9→DR10→DR6→DR4→DR2→DR3→DR5`; DR10 v2 by-ref `78cd22e`; DR11 NOT IN CHAIN. K1/K2 binding edge gates (re-proven on s21); **K9 INVIOLATE** (aggregate ≥100; OOS ≥50/y) — not lowered; **K13** at P6.7 (by-ref `52a3b60`); K10/K6/A7 diversification load-bearing (top-8 of 48 ⇒ broad sector spread); K11 NOT_APPLICABLE. DR9 = PASSED all 48 (`9835c0d2…`). C6 (16) carried verbatim at the s21 SEAL.

----

## 8. T-FORBID compliance

16/17/18 (not mean-reversion), 19/20/21 (not s16 trend), **22 (locked params; pre-committed unsearched folds; no per-fold refit)**, **23 (fresh-universe candidate with the IDENTICAL locked mechanic — NOT a tune/`_revN_` of s18/s19/s20; all frozen)**, **24 (pre-SEAL K9 re-measurement at the s21 DRAFT)** — all CLEARED/ENFORCED.

----

## 9. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/BUILD/fetch/backtest/OOS) | met |
| REPLICATION not tuning; mechanic byte-identical; M=8 unchanged; no param search | met |
| Fresh s21 candidate; no `_revN_`/modification of s18/s19/s20 (frozen) | met |
| No lowering K9; no retroactive K13/DR10; no sealed-artifact modification | met |
| No data fetch (reuse DR9-passed fresh 48) | met |
| Edge re-proven (not inherited) at s21 P6 IS | committed-to |
| `lessons.md` not modified this turn | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 10. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s21_d1_broader_universe_weekly_relative_strength_rotation_tier_n_spec_plan.md` | This Tier-N spec PLAN (PLAN only; no JSON sidecar; no seal). |

No other repository file is modified.

----

## 11. Next-step authorization scope

- **Proceed to DRAFT (with the pre-SEAL K9 re-measurement on the fresh 48):** `Authorize s21-d1 broader-universe weekly relative-strength rotation Tier-N spec DRAFT only — bound by DR10 v2 + walk-forward K13; DRAFT carries the pre-SEAL K9 turnover measurement (signal-only, no P&L) on the fresh 48-name universe; mechanic locked identical to s18/s19/s20 (no tuning).`
- **Defer:** `Defer / Pause s21-d1 at PLAN.`

----

End of PLAN. PLAN-authoring turn only. No code/backtest/fetch/DRAFT/SEAL/BUILD. **s21-d1 is the CLEAN generalization test that resolves the s20 selection caveat: the IDENTICAL byte-locked weekly RS mechanic (126-21 / R=5 / top-8 / M=8 / long-only / relative-rank exit) on a FRESH 48-name universe with ZERO overlap vs s17/s18/s19 (DR9-passed `d76c999`). K9/turnover reachability is expected to clear (breadth-driven; s20 precedent 67.2/y at this breadth) but UNPROVEN on fresh names; the EDGE is re-proven from scratch at P6 IS / P6.7 K13 / P10 OOS, NOT inherited. A positive result here is genuine independent generalization evidence; a null/negative is equally informative.** No tuning / no param search / M=8 unchanged / no s18/s19/s20 `_revN_` / no modification of frozen artifacts; no lowering K9; no retroactive K13/DR10; no `lessons.md` modification. Trading `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

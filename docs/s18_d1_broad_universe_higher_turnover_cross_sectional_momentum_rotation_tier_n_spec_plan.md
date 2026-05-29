# s18-d1 broad-universe higher-turnover (fortnightly) cross-sectional momentum rotation — Tier-N specification PLAN

Status: **PLAN_ONLY** (no code, no spec drafted, no spec sealed, no data fetched, no backtest, no OOS; the next step is a separate operator authorization to commit this PLAN, then — only if the K9 reachability is acceptable — a Tier-N spec DRAFT).

Authored: 2026-05-28
Authorization phrase: `Authorize s18-d1 broad-universe higher-turnover cross-sectional momentum Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13.`
Origin: Track **T1** of the post-s17 selection plan (`86c9fb2`). **FRESH candidate** — NOT a `_revN_`/patch/cadence-tune of the terminal s17-d1 (LESSON_S17_D1_001; T-FORBID-23). Reuses the 24-name DR9-passed universe from the s17 data gate (`d86e5d1`, result_seal `85667ab3`); zero fetch.
Framework binding: **DR10 v2 AND-conjunction** (`78cd22e`) **+ walk-forward K13** (`52a3b60`).

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT/SEAL/code/backtest/simulator/signal/fetch/OOS/live. No vendor API / network / API-key. No `review_queue`/`idea_memory` mutation. No Strategy Lab / promotion / FRC / broker. **No `_revN_`/patch/cadence-tune of s17-d1** (T-FORBID-23 — a fresh candidate, decided independent of s17's K9 count). **No revival of s17/s16/s15/s14/s13/s12.** **No retroactive K13.** No modification of any sealed artifact (incl. s17 DR9 result `d86e5d1`, 24 CSVs, DR10 v2 `78cd22e`, walk-forward `52a3b60`). **No strategy parameter optimization / grid search** (parameters first-principles, justify-not-tune at SEAL). **No SEAL of any low-turnover rotation without a pre-SEAL K9-reachability demonstration** (T-FORBID-24). No `lessons.md` modification. No commit beyond this PLAN's own authorization. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. Purpose + the single design change vs s17

s17-d1 (cross-sectional momentum, **monthly** top-6) showed the first positive, non-regime-artifact edge in the s14→s17 line (expectancy +$1,130.75/trade, win 63.5%, profit_factor 2.42, +145.79% IS) but terminated **INSUFFICIENT_SAMPLE** at P6 IS — only 85 closed trades (17/y) vs the K9 floor of 100. The failure axis was **turnover/sample**, not edge.

s18-d1 is a **fresh** candidate that keeps the proven momentum SIGNAL and changes the **holding cadence**: re-rank and rotate **fortnightly** instead of monthly, on a **top-third** held set. The hypothesis (tested at P6 IS, never assumed): a faster holding cadence inside the momentum-persistence window rotates into emerging relative leaders sooner and generates enough round-trips to be statistically verifiable, while preserving the relative-momentum edge.

----

## 2. Candidate identification

| Field | Proposed value (LOCKED at PLAN unless noted) |
|---|---|
| `candidate_record_id` | **`s18-d1-broad-universe-higher-turnover-cross-sectional-momentum-rotation-24name-large-cap-long-history`** |
| `candidate_family` | **F-xmom: cross-sectional (relative-strength) momentum rotation, long-only** (same FAMILY as s17; DIFFERENT cadence/width; FRESH candidate) |
| `is_a_s17_revision_or_patch` | **false** — fresh `candidate_record_id`; cadence/width chosen on first principles, decided independent of s17's K9 count (T-FORBID-23 cleared) |
| `predecessor_lineage_references_read_only` | `s17_p7_p11_terminal` (`7592e18`), `s17_p6_is` (`970a3c5`; the measured turnover anchor), `post_s17_selection_plan` (`86c9fb2`), `s17_dr9_result` (`d86e5d1` / `85667ab3`), `walk_forward_validation_seal` (`52a3b60`), `framework_dr10_revision_seal_v2` (`78cd22e`) |
| `diagnostic_only` | true · `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| DR9 status | **ALREADY PASSED all 24** (reuse sealed CSVs `d86e5d1` / `85667ab3`); no fetch |
| **K9-reachability pre-SEAL discipline** | **TRUE + BINDING** (§4; T-FORBID-24) — and it is this candidate's primary open question |

----

## 3. Universe + mechanic (LOCKED-at-PLAN proposal; reuse 24-name DR9 data)

| Field | LOCKED-at-PLAN value |
|---|---|
| Universe (24) | {AAPL, MSFT, NVDA, JPM, XOM, UNH, WMT, KO, META, AMZN, JNJ, CVX, GOOGL, V, MA, HD, PG, COST, ABBV, MRK, BAC, CAT, DIS, COP} — reuse `d86e5d1`; widening/substitution post-SEAL FORBIDDEN |
| Momentum signal | **126-21 skip-month** trailing total return (UNCHANGED from s17 — proven 6-month formation; first-principles, not tuned) |
| Rebalance cadence `R` | **10 trading days (fortnightly)** — the design change |
| Held `M` | **8 (top third of 24)**, equal-weight `1/8` |
| Direction / leverage / pyramid | long-only · unlevered (DR11 NOT IN CHAIN) · no pyramid |
| Exit | relative-rank rotation (a held name leaving the top-M = one closed trade; no trailing/ATR stop) |
| Sizing (DA3) | equal-weight `1/M` per held name, rebalanced each `R` |
| START_CASH | `$100,000` · adjustment `split_only` · vendor `tiingo` |
| Warmup | ≥ `L + S + margin` = 126 + 21 + ~13 ≈ **160 bars** |

### 3.1 First-principles justification (NOT a post-hoc K9 fix — T-FORBID-23)

- **Fortnightly cadence (R=10):** the shortest holding horizon that still sits **inside the cross-sectional momentum-persistence window and above the short-term-reversal zone** the 21-day skip is designed to avoid. It re-ranks into emerging relative leaders ~2× sooner than monthly — an edge-relevant hypothesis (faster capture of momentum-rank changes), not a trade-count device. The momentum SIGNAL horizon (126-21) is unchanged; only the holding cadence moves.
- **Top-third held set (M=8):** terciles are a standard cross-sectional-momentum portfolio breakpoint; top-8 of 24 captures the premium with **better diversification** (higher A7 effective-bets, lower K10 avg-correlation) than s17's top-6.
- **Honest disclosure (transparency over T-FORBID-23):** K9-reachability is *a* design constraint for any fresh low-turnover-family candidate (we must pick a cadence/width that *can* clear the floor). Both choices above also stand on independent edge/diversification first principles, and **the edge is tested independently of sample sufficiency at P6 IS** (if fortnightly has no edge it dies at K1/K2 regardless of trade count). This is a legitimate fresh-candidate design — not reverse-fitting s17's terminal cadence.

----

## 4. Reachability tables (grounded in s17's MEASURED turnover; analytical — a real measurement is the pre-SEAL gate)

**Anchor (measured, committed `970a3c5`):** s17 monthly top-6 → **1.604 closed trades per rebalance**, 17.0/y, 85 over the 5y IS. s18 fortnightly (R=10) ≈ **110 rebalances over IS**. Scaling the measured exits/rebalance for (a) large-cap rank **stickiness** at shorter intervals (×0.6–0.9) and (b) top-8 boundary churn (×1.1–1.4) gives the ranges below. **These are estimates; the binding K9 demonstration is a pre-SEAL turnover measurement (signal-only, not a P&L backtest), forbidden at PLAN.**

### 4.1 K9 aggregate (IS ~5y; floor ≥ 100 total)
| Scenario (stickiness × M-lift) | exits/rebalance | IS total | per year |
|---|---:|---:|---:|
| pessimistic (0.6 × 1.1) | 1.06 | ~116 | ~23 |
| central | ~1.3–1.7 | ~146–185 | ~29–37 |
| optimistic (0.9 × 1.4) | 2.02 | ~222 | ~44 |
→ **K9 aggregate: CLEARS ≥100** across the range (low end ~116). 

### 4.2 K9 per-fold under K13 (5 folds ~1.27y each)
| Scenario | per-fold trades |
|---|---:|
| pessimistic | ~30 |
| central | ~37–47 |
| optimistic | ~56 |
→ **K9 per-fold: BORDERLINE** vs an OOS-equivalent ≥50/y leg; the discipline allows per-fold OR aggregate (aggregate clears), so K13's K9 sub-condition is plausibly met on aggregate.

### 4.3 OOS K9 (OOS 2024-01-02→2025-12-30 ~2y; floor ≥ 50/y ⇒ ≥ 100 over 2y) — **THE BINDING RISK**
| Scenario | OOS 2y trades | vs ≥100 floor |
|---|---:|---|
| pessimistic | ~47 | **SHORT** |
| central | ~58–74 | **SHORT** |
| optimistic | ~89 | **SHORT** |
→ **OOS K9 ≥50/y: PROJECTED SHORT in every scenario** (max ~89 < 100). Large-cap rank **stickiness** (mega-cap leaders persist for long stretches) caps the turnover gain from faster rebalancing, so fortnightly does not reach the OOS floor on this universe. **This is the candidate's binding kill-risk.**

### 4.4 DR10-v2 reachability
Fortnightly raises annual turnover (~3–6) but cash-equity cost_drag stays ~0.4–1.0% « 5%; the turnover branch fires alone, the AND-conjunction (`turnover>0.50 AND cost_drag>0.05`) is **not** triggered → **DR10 v2 CLEARS with margin.**

### 4.5 K13 walk-forward reachability
5 fixed pre-committed unsearched DA22-style folds (re-derived for s18 at SEAL). K13 PASS = positive in ≥3/5 + aggregate net>0 + K9 (per-fold OR aggregate). The K9 sub-condition is plausibly met on aggregate; the **standalone P10 OOS K9 ≥50/y (§4.3) is the binding gate the candidate is projected to FAIL.** The edge persistence itself (≥3/5 folds) is untested and would be evaluated at P6.7 only if the candidate clears K9.

----

## 5. Determination — author the design, but OOS K9 is a projected blocker (do NOT advance to DRAFT on fortnightly alone)

The fortnightly top-8 design is authored as requested and is first-principles-justified. **But its own reachability tables show the binding OOS K9 ≥50/y floor is projected SHORT in every grounded scenario (~47–89 over the 2y OOS vs ~100 needed)**, because large-cap momentum ranks are sticky and faster rebalancing yields diminishing turnover. Aggregate K9 clears; OOS K9 does not.

**Honest recommendation:** do NOT spend DRAFT/SEAL/BUILD budget on **fortnightly** in the expectation it clears OOS K9 (LESSON_S17_D1_002 — prove K9 before SEAL). The evidence points to a **weekly** cadence (selection-plan T3) as the design that can actually clear OOS ≥50/y on this universe (weekly ≈ ~52 rebalances/y → grounded ~40–70/y → ~80–140 over 2y → clears). Two disciplined options for the operator:
1. **Pivot to the weekly fresh candidate (recommended):** authorize the T3 weekly relative-strength PLAN, where OOS K9 is projected to clear.
2. **Proceed to a fortnightly DRAFT only as a pre-SEAL K9 *measurement* step:** authorize a fortnightly DRAFT whose sole gating purpose is a real signal-only turnover measurement (no P&L) to confirm/refute §4.3; if it confirms SHORT, s18-fortnightly is K9-blocked at the pre-SEAL gate and parked.

No DRAFT is auto-authored (T-FORBID-24: OOS K9 is unproven and projected short).

----

## 6. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/BUILD/fetch/backtest/OOS) | met |
| Fresh candidate; no `_revN_`/patch/cadence-tune of s17 (T-FORBID-23) | met |
| Cadence/width justified on first principles, edge tested independently | met |
| All 5 reachability tables included (K9 agg / K9 per-fold / OOS K9 / DR10-v2 / K13) | met |
| No SEAL/DRAFT without pre-SEAL K9 demonstration (T-FORBID-24) | met (no DRAFT auto-authored) |
| No revival / no retroactive K13 / no sealed-artifact modification | met |
| No data fetch (reuse DR9-passed 24-name) | met |
| `lessons.md` not modified · no commit by this PLAN turn | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 7. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s18_d1_broad_universe_higher_turnover_cross_sectional_momentum_rotation_tier_n_spec_plan.md` | This Tier-N spec PLAN (PLAN only; no JSON sidecar; no seal — planning document). |

No other repository file is modified.

----

## 8. Next-step authorization scope (operator chooses; each separate)

- **Commit this PLAN:** `Authorize commit s18-d1 broad-universe higher-turnover cross-sectional momentum Tier-N spec PLAN only.`
- **Pivot to weekly (recommended — OOS K9 projected to clear):** `Authorize s18-d1 broad-universe weekly relative-strength rotation Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13.`
- **Fortnightly DRAFT as a pre-SEAL K9 measurement only (signal-only turnover, no P&L):** `Authorize s18-d1 fortnightly cross-sectional momentum Tier-N spec DRAFT only — bound by DR10 v2 + walk-forward K13; DRAFT scope limited to a pre-SEAL K9 turnover measurement (no P&L backtest, no OOS).`
- **Defer:** `Defer / Pause s18-d1 at PLAN.`

----

End of PLAN. PLAN-authoring turn only. No code/backtest/fetch/DRAFT/SEAL/BUILD. **s18-d1 (fresh fortnightly top-8 long-only cross-sectional momentum, reuse 24-name data) is authored with first-principles cadence justification, but its grounded reachability tables project the binding OOS K9 ≥50/y floor SHORT in every scenario (large-cap rank stickiness) — so NO DRAFT is auto-authored; a weekly cadence is the evidence-based path to clear OOS K9.** No `_revN_`/patch/cadence-tune of s17; no revival; no retroactive K13; no sealed-artifact modification; no `lessons.md` modification. Trading `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

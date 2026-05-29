# Next-research-track selection plan (after s17-d1 INSUFFICIENT_SAMPLE / K9 at P6 IS)

Status: **PLAN_ONLY** (no code, no spec sealed, no data fetched, no backtest, no OOS; the next step is a separate operator authorization to author a Tier-N spec PLAN for a selected track, or to defer).

Authored: 2026-05-28
Authorization phrase: `Authorize next research-track selection plan after s17-d1 INSUFFICIENT_SAMPLE only.`
Trigger: s17-d1 terminal at P6 IS with **INSUFFICIENT_SAMPLE/K9** (P6 IS `970a3c5`; P7/P11 memo `7592e18`, report_seal `bb803bb7…`). Lessons LESSON_S17_D1_001/002/003 committed `9c937cd`. Binds under **DR10 v2** (`78cd22e`) **+ walk-forward K13** (`52a3b60`).

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT/SEAL/code/backtest/simulator/signal/fetch/OOS/live. No vendor API / network. No `review_queue`/`idea_memory` mutation. No Strategy Lab / promotion / FRC / broker. No commit beyond this doc's own authorization. No `lessons.md` modification (the S17 lessons were committed at `9c937cd`; not touched here).

### The plan FORBIDS (binding on any track selected from it)
- **Any `_revN_`/patch of s17-d1** (terminal; preserved verbatim).
- **Cadence-tuning s17 after seeing the K9 failure** — choosing a faster cadence *because* it manufactures the trades K9 needs is reverse-fitting the sample floor (T-FORBID-23). A faster cadence must be a FRESH candidate justified on first-principles momentum-horizon grounds, decided independent of the K9 count.
- **Retroactively applying K13 or any framework change to old candidates** (s17/s16/s15/s14/s13/s12 verdicts stand).
- **Promoting s17 or any prior terminal candidate** (no revival, no Strategy Lab, no live).
- **Any low-turnover rotation/carry candidate that cannot prove K9 reachability BEFORE SEAL** (T-FORBID-24) — a pre-SEAL closed-trades/year table must clear the aggregate floor (>=100 over IS) AND the per-fold/OOS floors (K13 per-fold; OOS >=50/y).
- Carried T-FORBID-1..22 (incl. no mean-reversion / absolute-trend re-skin; no per-fold refit / fold-scheme search).

Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. What changed — s17 is qualitatively different from s14/s15/s16

| Candidate | Family | Terminal gate | Edge sign | Failure axis |
|---|---|---|---|---|
| s14-d1 | mean-reversion (RSI3+2N) | P6 IS FAIL_SAFETY | negative | no edge |
| s15-d1 | mean-reversion (z-score exit-to-mean) | P6 IS FAIL_SAFETY | negative | no edge |
| s16-d1 | absolute trend (Donchian) | P10 OOS REJECT_FAST (DR4) | positive IS, negative OOS | generalization |
| **s17-d1** | **cross-sectional relative momentum** | **P6 IS INSUFFICIENT_SAMPLE (K9)** | **positive (never disproven)** | **sample (turnover), NOT edge** |

**Load-bearing observation:** s17 is the **first line member with a positive, non-regime-artifact IS edge** (expectancy +$1,130.75/trade, sharpe_proxy/trade +0.285, win 63.5%, profit_factor 2.42, +145.79% IS). It failed only because the LOCKED **monthly top-6** rotation produced 85 < 100 closed trades. **The most promising lead in the whole line is the one we could not properly test — relative momentum at a cadence that clears K9** — but a positive thin-sample result is *unverified*, not *proven* (LESSON_S17_D1_003).

----

## 2. Tracks (the bundle requires at least T1–T5)

- **T1** — FRESH higher-turnover **long-only cross-sectional momentum** on the same 24-name DR9-passed universe; **fortnightly (~10-day) rebalance and/or wider held-N (top-8/10)**; cadence justified on first-principles momentum-horizon grounds (NOT K9-fit). Zero fetch (reuse `d86e5d1`).
- **T2** — FRESH **long/short cross-sectional momentum** on the same 24-name universe (long top-N + short bottom-N, ~dollar-neutral); shorting represented ONLY as a CSV-simulator dollar-neutral position with a modeled borrow-cost term — **no broker/borrow-live, no leverage semantics**. Zero fetch.
- **T3** — FRESH **daily/weekly sector/relative-strength rotation** on the same 24-name universe, designed explicitly to clear K9 + K13 via a faster cadence. Zero fetch.
- **T4** — **Broaden the universe further** (≈40–60 names or sector ETFs) — requires a fresh fetch + DR9 (data/fetch friction).
- **T5** — **Pause / defer** the trading-bot track.

----

## 3. Scoring (8 axes /10 each; total /80)

Axes: (1) K9 aggregate reachability · (2) K9 per-fold reachability under K13 · (3) DR10 v2 reachability · (4) first-principles (not merely tuned to fix s17) · (5) expected OOS/regime robustness · (6) data reuse / low friction · (7) implementation simplicity · (8) live/trading-safety boundaries.

| Track | (1) K9 agg | (2) K9/fold | (3) DR10v2 | (4) first-principles | (5) OOS-robust | (6) data-reuse | (7) impl-simple | (8) live-safety | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **T1** fortnightly long-only xmom | 8 | 6 | 8 | 7 | 6 | 10 | 7 | 9 | **61/80** |
| **T3** weekly/daily relative-strength rotation | 9 | 8 | 6 | 5 | 5 | 10 | 7 | 9 | **59/80** |
| **T2** long/short xmom | 8 | 6 | 7 | 6 | 7 | 10 | 4 | 6 | **54/80** |
| **T4** broaden universe (fetch) | 7 | 4 | 8 | 4 | 6 | 3 | 6 | 9 | **47/80** |
| **T5** pause/defer | — | — | — | — | — | — | — | — | n/a |

### Per-track honest notes
- **T1 (61):** fortnightly (~26–52 trades/y → ~130–260 over IS) clears K9 aggregate with margin; per-fold ~36–73 → clears OOS ≥50/y borderline-to-OK but **UNPROVEN until a pre-SEAL K9 table is built**. Fortnightly sits near the momentum premium's natural horizon, so the cadence is edge-motivated rather than K9-fitted (axis 4 = 7). Long-only → high live-safety. **The monthly s17 edge is NOT inherited — it must be re-proven at fortnightly at P6 IS** (faster cadence may dilute it).
- **T3 (59):** weekly (~52/y) clears K9 per-fold most comfortably (axis 2 = 8), BUT weekly relative-strength is faster than the momentum premium's natural horizon → highest risk of being "tuned to clear K9" rather than edge-motivated (axis 4 = 5) and noisier/weaker OOS (axis 5 = 5). It buys sample at the cost of edge plausibility.
- **T2 (54):** long/short ~doubles turnover and is classically more regime-robust (market-neutral, axis 5 = 7), but the short leg adds real implementation surface (borrow cost, dollar-neutral rebalancing) and a live/safety concern (axis 7 = 4, axis 8 = 6) — shorting must be representable as a pure CSV-simulator term with no broker/borrow-live and no leverage semantics, which needs a careful pre-SEAL design.
- **T4 (47):** **conceptually weak** — broadening the universe adds *ranking breadth*, not *turnover*, and K9 is driven by turnover (LESSON_S17_D1_001). Broadening alone does NOT fix the s17 failure; it also costs a fresh fetch + DR9 (axis 6 = 3). Lowest-leverage.
- **T5:** legitimate after four terminals, but s17 left a live positive lead, so a full pivot walks away from the strongest signal seen so far.

----

## 4. Determination — strongest direction, but NO clear blocker-free winner (no Tier-N PLAN auto-authored)

**Strongest direction: T1** (fortnightly long-only cross-sectional momentum, reuse 24-name data) — it preserves the only positive, non-regime-artifact edge in the line, fixes the failure axis (turnover) with an edge-motivated cadence rather than a K9-fitted one, needs zero fetch, and is long-only (cleanest live-safety).

**But T1 is NOT a clear blocker-free winner, so no Tier-N PLAN is auto-authored:**
1. **Unresolved K9/K13 reachability blocker.** T1's K9-per-fold (under K13) and OOS ≥50/y are only *estimated* at PLAN time. The entire s17 lesson is "prove K9 reachability before SEAL" — that demonstration is exactly what a T1 PLAN/pre-SEAL gate must produce; it is unresolved now.
2. **Unproven edge at the new cadence.** The positive economics were at MONTHLY cadence; fortnightly may dilute the momentum premium. T1 must re-prove K1/K2 at P6 IS — not inheritable.
3. **Not an unambiguous separation.** T1 (61) leads T3 (59) by only 2 points; both are faster-cadence cross-sectional-momentum cousins, and the fortnightly-momentum vs weekly-relative-strength choice is itself an open design question. There is no single track that is both clearly top AND blocker-free.

Per the bundle's gate ("author the Tier-N PLAN if and only if there is one clear blocker-free winner; if the top track has unresolved K9/K13 reachability … blockers, stop after the selection plan"), the disciplined action is to **stop at the selection plan** and report the exact next authorization. The operator chooses whether to open the T1 PLAN (which is where the pre-SEAL K9-reachability table gets built and the cadence gets first-principles-justified).

----

## 5. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/code/fetch/backtest/OOS) | met |
| No `_revN_`/patch/cadence-tune of s17-d1 (T-FORBID-23) | met |
| No low-turnover candidate without a pre-SEAL K9 gate (T-FORBID-24) | enforced on all tracks |
| No revival of s17/s16/s15/s14/s13/s12 | met |
| No retroactive K13 / no DR/K reinterpretation | met |
| No per-fold optimization / fold-scheme search (T-FORBID-22) | met |
| No modification of any sealed artifact | met |
| `lessons.md` not modified this turn | met |
| **No Tier-N PLAN auto-authored (T1 strongest but not blocker-free)** | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 6. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/next_research_track_selection_plan_after_s17_d1_insufficient_sample.md` | This selection plan (PLAN only; no JSON sidecar; no seal — planning document). |

No other repository file is modified.

----

## 7. Exact next-authorization options (operator chooses; each separate)

- **T1 — fortnightly long-only cross-sectional momentum (recommended direction; fresh candidate, reuse 24-name data):**
  `Authorize s18-d1 broad-universe higher-turnover cross-sectional momentum Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13; PLAN must include a pre-SEAL K9-reachability table (aggregate >=100 + per-fold/OOS >=50/y) and justify the fortnightly cadence from first principles (not K9-fitted), with the monthly-vs-fortnightly edge to be re-proven at P6 IS.`
- **T3 — weekly relative-strength rotation (fresh candidate):**
  `Authorize s18-d1 broad-universe weekly relative-strength rotation Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13; PLAN must justify the weekly cadence on first principles (not K9-fitted) and include the pre-SEAL K9-reachability table.`
- **T2 — long/short cross-sectional momentum (fresh candidate):**
  `Authorize s18-d1 broad-universe long/short cross-sectional momentum Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13; PLAN must include the pre-SEAL K9 table and a CSV-only dollar-neutral short representation (no broker/borrow-live, no leverage semantics).`
- **Park / defer:** `Defer / Pause trading-bot track.`

----

End of PLAN. PLAN-authoring turn only. No code/backtest/fetch/DRAFT/SEAL/BUILD. **T1 (fresh fortnightly long-only cross-sectional momentum, reuse 24-name data) is the strongest direction, but it is NOT a clear blocker-free winner — its K9-per-fold reachability and its edge at the faster cadence are unproven, and T1/T3 are too close to separate — so NO Tier-N PLAN is auto-authored.** No `_revN_`/patch/cadence-tune of s17; no revival; no retroactive K13; no sealed-artifact modification; no `lessons.md` modification. Trading `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

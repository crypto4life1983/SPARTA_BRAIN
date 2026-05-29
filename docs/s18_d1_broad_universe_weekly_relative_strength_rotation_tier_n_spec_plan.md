# s18-d1 broad-universe weekly relative-strength rotation — Tier-N specification PLAN

Status: **PLAN_ONLY** (no code, no spec drafted, no spec sealed, no data fetched, no backtest, no OOS; the next step is a separate operator authorization to commit this PLAN, then — only if K9/K13 reachability and the edge survive a pre-SEAL check — a Tier-N spec DRAFT).

Authored: 2026-05-28
Authorization phrase: `Authorize s18-d1 broad-universe weekly relative-strength rotation Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13.`
Origin: Track **T3** of the post-s17 selection plan (`86c9fb2`). **FRESH sibling candidate** — NOT a `_revN_`/patch of terminal s17-d1, and **NOT a rescue of the fortnightly s18 PLAN** (`d2f0cc7`, which recorded a pre-SEAL OOS-K9 blocker). Reuses the 24-name DR9-passed universe from the s17 data gate (`d86e5d1`, result_seal `85667ab3`); zero fetch.
Framework binding: **DR10 v2 AND-conjunction** (`78cd22e`) **+ walk-forward K13** (`52a3b60`).

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT/SEAL/code/backtest/simulator/signal/fetch/OOS/live. No vendor API / network / API-key. No `review_queue`/`idea_memory` mutation. No Strategy Lab / promotion / FRC / broker. **No `_revN_`/patch/cadence-tune of s17-d1** (T-FORBID-23). **No rescue/patch of the fortnightly s18 PLAN** — this is a fresh sibling, decided on its own merits. **No revival of s17/s16/s15/s14/s13/s12.** **No retroactive K13.** **No reinterpretation of K9/K13/DR10.** No modification of any sealed artifact. **No strategy parameter optimization / grid search.** **No SEAL of any rotation without a pre-SEAL K9-reachability demonstration** (T-FORBID-24). No `lessons.md` modification. No commit beyond this PLAN's own authorization. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. Purpose + the cadence ladder

The s14→s17 line established that cross-sectional relative momentum is the **only** family that has shown a positive, non-regime-artifact edge (s17 monthly: expectancy +$1,130.75/trade, win 63.5%, PF 2.42) — but s17 monthly was **K9-blocked** (85 trades) and the **fortnightly** sibling (`d2f0cc7`) is **projected to fail OOS K9 ≥50/y in every scenario** because large-cap ranks are sticky. This PLAN tests the next rung: **weekly** re-ranking, the cadence at which the same universe finally generates enough round-trips to be statistically verifiable.

| Cadence | candidate | held M | OOS K9 (~2y, floor ≥100) | status |
|---|---|---:|---|---|
| Monthly (R=21) | s17-d1 (terminal) | 6 | ~34 (measured 17/y) | **K9 FAIL — INSUFFICIENT_SAMPLE** |
| Fortnightly (R=10) | s18 fortnightly (`d2f0cc7`) | 8 | ~47–89 (projected) | **OOS-K9 projected SHORT (all scenarios)** |
| **Weekly (R=5)** | **s18 weekly (this PLAN)** | **8** | **~62–138 (projected)** | **OOS-K9 REACHABLE in central/optimistic scenarios** |

----

## 2. Candidate identification

| Field | Proposed value (LOCKED at PLAN unless noted) |
|---|---|
| `candidate_record_id` | **`s18-d1-broad-universe-weekly-relative-strength-rotation-24name-large-cap-long-history`** |
| `candidate_family` | **F-xmom: cross-sectional relative-strength rotation, long-only** (same family; WEEKLY cadence; FRESH sibling) |
| `is_a_s17_revision_or_fortnightly_rescue` | **false** — fresh `candidate_record_id`; weekly cadence decided on its own first-principles + reachability merits (T-FORBID-23 cleared; not a rescue of `d2f0cc7`) |
| `predecessor_lineage_references_read_only` | `s17_p7_p11_terminal` (`7592e18`), `s17_p6_is` (`970a3c5`; measured turnover anchor), `s18_fortnightly_plan` (`d2f0cc7`; OOS-K9 blocker evidence), `post_s17_selection_plan` (`86c9fb2`), `s17_dr9_result` (`d86e5d1`/`85667ab3`), `walk_forward_validation_seal` (`52a3b60`), `framework_dr10_revision_seal_v2` (`78cd22e`) |
| `diagnostic_only` | true · `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` |
| DR9 status | **ALREADY PASSED all 24** (reuse `d86e5d1`/`85667ab3`); no fetch |
| K9-reachability pre-SEAL discipline | **TRUE + BINDING** (§5; T-FORBID-24) |

----

## 3. Universe + mechanic (LOCKED-at-PLAN proposal; reuse 24-name DR9 data)

| Field | LOCKED-at-PLAN value |
|---|---|
| Universe (24) | {AAPL, MSFT, NVDA, JPM, XOM, UNH, WMT, KO, META, AMZN, JNJ, CVX, GOOGL, V, MA, HD, PG, COST, ABBV, MRK, BAC, CAT, DIS, COP} — reuse `d86e5d1`; widening/substitution post-SEAL FORBIDDEN |
| Relative-strength signal | **126-21 skip-month** trailing total return (UNCHANGED — proven formation; the ranking metric for relative strength; first-principles, not tuned) |
| Rebalance cadence `R` | **5 trading days (weekly)** — the design change vs the fortnightly sibling (cadence is the SOLE difference) |
| Held `M` | **8 (top third of 24)**, equal-weight `1/8` |
| Direction / leverage / pyramid | long-only · unlevered (DR11 NOT IN CHAIN) · no pyramid |
| Exit | relative-rank rotation (a held name leaving the top-M = one closed trade; no trailing/ATR stop) |
| Sizing (DA3) | equal-weight `1/M`, rebalanced to equal weight each `R` |
| START_CASH | `$100,000` · adjustment `split_only` · vendor `tiingo` |
| Warmup | ≥ `L + S + margin` = 126 + 21 + ~13 ≈ **160 bars** |

### 3.1 First-principles justification for weekly cadence (with honest disclosure of the tension; NOT K9-fitting)

- **Relative-strength rotation is a recognized practitioner family** (e.g., point-and-figure / Dorsey-Wright relative-strength rotation, sector RS rotation) that operates at **weekly** cadence — re-ranking into current relative leaders weekly. This gives weekly an *a-priori* basis distinct from academic monthly 6-1 momentum: it is the RS-rotation family's native cadence, not an arbitrary speed-up.
- **Honest tension (load-bearing, stated plainly):** weekly is **faster than the momentum premium's natural monthly-to-quarterly horizon**, so its first-principles edge basis is **weaker** than monthly/fortnightly, and it sits closer to the short-term-reversal contamination zone (mitigated, but not eliminated, by the 21-day signal skip). The selection plan (`86c9fb2`) scored weekly's "not-merely-tuned" axis only 5/10 for exactly this reason.
- **Why this is still legitimate (not a post-hoc K9 fix, T-FORBID-23):** weekly is justified on the RS-rotation family's native-cadence grounds AND its K9 sufficiency is an acknowledged, disclosed consequence — not a hidden reverse-fit of s17's terminal cadence. Critically, **the edge is tested independently of sample sufficiency at P6 IS** (§7): if weekly RS rotation has no edge or a diluted edge, it dies at K1/K2 regardless of clearing K9. Transparency over both motivations is the safeguard.

----

## 4. Reachability tables (grounded in s17's MEASURED turnover; analytical — a real measurement is the pre-SEAL gate)

**Anchor (measured, committed `970a3c5`):** s17 monthly top-6 → **1.604 closed trades/rebalance**, 17/y, 85 over IS. s18 weekly (R=5) ≈ **220 rebalances over IS**. Scaling the measured exits/rebalance for (a) large-cap stickiness at the much-shorter weekly interval (×0.4–0.7) and (b) top-8 boundary churn (×1.1–1.4). **Estimates only; the binding K9 demonstration is a pre-SEAL signal-only turnover measurement (no P&L), forbidden at PLAN.**

### 4.1 K9 aggregate (IS ~5y; floor ≥ 100 total)
| Scenario | exits/reb | IS total | per year |
|---|---:|---:|---:|
| pessimistic (0.4 × 1.1) | 0.71 | ~155 | ~31 |
| central | ~0.97–1.23 | ~213–272 | ~43–54 |
| optimistic (0.7 × 1.4) | 1.57 | ~346 | ~69 |
→ **K9 aggregate: CLEARS ≥100 comfortably** across the full range (low end ~155).

### 4.2 OOS K9 (OOS 2024-01-02→2025-12-30 ~2y; floor ≥ 50/y ⇒ ≥ 100 over 2y) — THE BINDING SAMPLE GATE
| Scenario | OOS 2y trades | vs ≥100 floor |
|---|---:|---|
| pessimistic (sticky) | ~62 | SHORT |
| central | ~85–109 | **borderline → CLEARS** |
| optimistic | ~138 | **CLEARS** |
→ **OOS K9 ≥50/y: REACHABLE** — clears in central/optimistic scenarios (~85–138 over 2y); only the pessimistic (very-sticky) end is short. **This is materially better than the fortnightly sibling (short in ALL scenarios) and is the first cadence in the ladder with a credible path to the OOS floor.** A pre-SEAL measurement must confirm.

### 4.3 K13 per-fold (5 folds ~1.27y each; positive in ≥3/5 + aggregate net>0 + K9 per-fold OR aggregate)
| Scenario | per-fold trades |
|---|---:|
| pessimistic | ~39 |
| central | ~54–69 |
| optimistic | ~88 |
→ **K13 per-fold K9: mostly CLEARS** (central ~54–69 clears the per-fold ≥50/y-equivalent leg); aggregate clears regardless. The **edge-persistence** sub-condition (≥3/5 folds positive) is untested and is the real K13 question (§7), evaluated at P6.7 only if K9 and the edge clear earlier.

### 4.4 DR10-v2 reachability
Weekly is the **highest-turnover** rung (annual turnover ~10–20×), so cost_drag is the largest in the family — but for liquid large-caps at 1bp slippage + tiny per-share commission it is still ~0.3–0.8% (and ~1–2% even at S4 3× stress) « the 5% threshold. The turnover branch fires alone; the v2 AND-conjunction (`turnover>0.50 AND cost_drag>0.05`) is **NOT triggered** → **DR10 v2 CLEARS.** (P6.5 cost-stress is more load-bearing here than at slower cadences — flagged.)

----

## 5. T-FORBID compliance

| Rule | Status |
|---|---|
| T-FORBID-16/17/18 (no mean-reversion re-skin) | CLEARED (relative-momentum continuation) |
| T-FORBID-19/20/21 (no s16 trend `_revN_`/OOS-tweak/DR4-relax/regime-rescue) | CLEARED (different family) |
| T-FORBID-22 (no per-fold refit / fold-scheme search) | CLEARED (locked params; K13 folds pre-committed unsearched at SEAL) |
| T-FORBID-23 (no `_revN_`/patch/cadence-tune of s17; no rescue of fortnightly) | CLEARED (fresh sibling; weekly justified on RS-rotation family grounds with K9 disclosed, edge independently tested) |
| T-FORBID-24 (no SEAL of a rotation without a pre-SEAL K9 demonstration) | ENFORCED (no DRAFT/SEAL auto-authored; pre-SEAL K9 measurement required) |

----

## 6. DR register + K-gates (carried; DR10 = v2; K13 ADDED)

DR precedence chain `DR7→DR1→DR9→DR10→DR6→DR4→DR2→DR3→DR5`; DR10 v2 by-reference (`78cd22e`); DR11 NOT IN CHAIN. K-gates K1/K2/K4/K6/K7/K8/**K9**/K10/K12; K11 NOT_APPLICABLE; **K13 walk-forward** ADDED at P6.7 (by-reference `52a3b60`). DR9 = PASSED all 24 by reuse. K1/K2 are the binding edge gates (per-fold + aggregate); **K9 is the gate s17 died on and the gate this cadence is designed to clear**; K10/K6/A7 diversification load-bearing (top-8 across ~8 sectors → strong).

----

## 7. Binding caveats (edge is NOT inherited; stop-before-SEAL conditions)

1. **Weekly cannot inherit s17's monthly economics.** The +$1,130.75/trade / 63.5%-win / 2.42-PF profile was measured at MONTHLY cadence. Weekly re-ranking on the same 6-month signal is noisier and closer to short-term reversal; the weekly edge is **genuinely uncertain and must be RE-PROVEN at P6 IS** (K1 sharpe_proxy>0 AND K2 expectancy>0). A positive monthly edge is not evidence of a positive weekly edge.
2. **Stop-before-SEAL conditions (T-FORBID-24 + LESSON_S17_D1_002):** if at PLAN/DRAFT the pre-SEAL K9 turnover **measurement** shows OOS K9 < 50/y (the sticky-low scenario), OR P6 IS shows the weekly edge is negative/zero (K1/K2 fail), the candidate **stops before SEAL** — it is K9-blocked or edge-blocked, and is NOT rescued by re-tuning cadence/M (a further change is yet another fresh candidate).
3. **No auto-DRAFT.** Weekly is K9-reachable (unlike fortnightly), so a DRAFT is *justified* — but the edge is unproven and weekly's first-principles basis is the weakest in the ladder, so the operator decides whether to advance. No DRAFT is auto-authored here.

----

## 8. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/BUILD/fetch/backtest/OOS) | met |
| Fresh sibling; no `_revN_`/patch of s17; no rescue of fortnightly (T-FORBID-23) | met |
| First-principles weekly justification + honest edge-tension disclosure (not K9-fitting) | met |
| Explicit comparison vs monthly + fortnightly (§1) | met |
| K9 aggregate / OOS K9 / K13 per-fold / DR10-v2 tables included | met (§4) |
| Edge-not-inherited + stop-before-SEAL conditions stated | met (§7) |
| No SEAL/DRAFT without pre-SEAL K9 demonstration (T-FORBID-24) | met (no DRAFT auto-authored) |
| No revival / no retroactive K13 / no K9-K13-DR10 reinterpretation / no sealed-artifact modification | met |
| No data fetch (reuse DR9-passed 24-name) | met |
| `lessons.md` not modified · no commit by this PLAN turn beyond its own authorization | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 9. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/s18_d1_broad_universe_weekly_relative_strength_rotation_tier_n_spec_plan.md` | This Tier-N spec PLAN (PLAN only; no JSON sidecar; no seal — planning document). |

No other repository file is modified.

----

## 10. Next-step authorization scope (operator chooses; each separate)

- **DRAFT (only with the pre-SEAL K9 measurement + edge re-proof discipline):** `Authorize s18-d1 broad-universe weekly relative-strength rotation Tier-N spec DRAFT only — bound by DR10 v2 + walk-forward K13; DRAFT must carry a pre-SEAL K9 turnover measurement (signal-only, no P&L) and lock the K13 fold scheme, with the weekly edge to be re-proven at P6 IS.`
- **Defer:** `Defer / Pause s18-d1 weekly at PLAN.`
- **Park the trading-bot track:** `Defer / Pause trading-bot track.`

----

End of PLAN. PLAN-authoring turn only. No code/backtest/fetch/DRAFT/SEAL/BUILD. **s18-d1 weekly relative-strength rotation (fresh sibling, reuse 24-name data) is the first cadence in the monthly→fortnightly→weekly ladder projected to clear OOS K9 (~62–138 over 2y; central/optimistic clear), but its weekly first-principles edge basis is the weakest in the ladder and the edge is NOT inherited from s17 — it must be re-proven at P6 IS, and the candidate stops before SEAL if the pre-SEAL K9 measurement or the P6 IS edge fails.** No `_revN_`/patch/cadence-tune of s17; no rescue of the fortnightly PLAN; no revival; no retroactive K13; no K9/K13/DR10 reinterpretation; no sealed-artifact modification; no `lessons.md` modification. Trading `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

# Robustness-replication selection plan (after s18-d1 weekly OOS_CONFIRMED_DIAGNOSTIC)

Status: **PLAN_ONLY** (no code, no spec sealed, no data fetched, no backtest, no new OOS inspected; the next step is a separate operator authorization to author a Tier-N spec PLAN for a selected replication path, or to defer).

Authored: 2026-05-28
Authorization phrase: `Authorize next research-track robustness-replication selection plan after s18-d1 OOS_CONFIRMED only.`
Trigger: s18-d1 weekly relative-strength rotation completed P11 with **OOS_CONFIRMED_DIAGNOSTIC** (P11 `5dde0f7`; P10 `522df8d`) — the first candidate in the s12→s18 line to clear the full gated ladder. Lessons LESSON_S18_D1_001/002/003/004 committed `05bf86b`. Binds under **DR10 v2** (`78cd22e`) + **walk-forward K13** (`52a3b60`).

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT/SEAL/code/backtest/simulator/signal/fetch/new-OOS-inspection/live. No vendor API / network. No Strategy Lab / promotion / FRC / broker. **No `_revN_`/patch/parameter-tune of s18-d1 weekly** (it is OOS_CONFIRMED and frozen; any variant is a FRESH candidate). **No parameter search / adjacent-variation grid** (T-FORBID-22/23). **No revival of s17/s16/s15/s14/s13/s12.** **No retroactive K13.** **No promotion of s18** (it remains DIAGNOSTIC_ONLY / BLOCKED_AT_6_GATES / FRC NEVER_GRANTED — there is no live-promotion path by framework design). No modification of any sealed artifact. No `lessons.md` modification (the S18 lessons were committed at `05bf86b`). No commit beyond this doc's own authorization. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. The binding question after s18

s18 weekly PASSED P10 OOS (net +$39,786, expectancy +$210/trade, 117 trades, no DR4) but the pass is **fragile** (LESSON_S18_D1_003/004):
- **Recent-fold weakness:** K13's most-recent fold F5 (2024-09→2025-12) was NEGATIVE; the contiguous-OOS positive is driven substantially by strong early-2024. The recent ~15 months were weak/negative.
- **Single window, single universe:** one 2024-2025 hold-out on one 24-name basket.
- **Thin edge:** OOS expectancy (+$210) is below IS (+$370).

**The binding robustness question is therefore: is the s18 edge a genuine, generalizing premium, or a single-window/single-universe artifact that is already decaying (per F5)?** The replication path should attack *that* question, not chase a bigger number.

----

## 2. Replication paths (the bundle requires comparing R1–R5)

- **R1** — **same mechanic, DIFFERENT universe.** Re-run the locked weekly RS rule (126-21 / R=5 / top-8 / long-only) on an independent large-cap basket (fresh names) as a FRESH candidate (s19). Tests universe-generalization with genuinely independent data.
- **R2** — **same universe, STRICTER robustness confirmation (zero fetch).** A fresh candidate that adds pre-committed robustness checks on the existing 24-name data: first-principles parameter-**perturbation stability** (does the edge survive small a-priori L/M/R neighbors WITHOUT tuning/selection?), finer cost-stress, and explicit recent-sub-period (F5) stability reporting.
- **R3** — **adjacent weekly-momentum variations.** Try nearby momentum specs (different lookback/skip/held-N) — **only if first-principles and not parameter-tuned.**
- **R4** — **longer / more-recent holdout or rolling-validation expansion.** Extend the hold-out or add rolling-origin folds.
- **R5** — **pause / defer.**

----

## 3. Scoring (6 axes /10 each; total /60). PRIMARY axis = directly attacks the binding fragility (recent-weakness + single-window/universe).

| Path | recent-weakness probe | independent generalization | overfitting/tuning distance | data/fetch friction | impl. complexity | diagnostic value | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|
| **R1** different universe | 5 | **9** | 8 | 3 (fetch+DR9) | 6 | 9 | **40/60** |
| **R2** stricter same-universe robustness (zero fetch) | 6 | 4 | 7 | 10 | 7 | 6 | **40/60** |
| R4 rolling/expanded holdout | 5 | 3 | 4 | 6 | 5 | 4 | **27/60** |
| R3 adjacent weekly variations | 3 | 3 | **2** | 9 | 6 | 3 | **26/60** |
| R5 pause/defer | — | — | — | — | — | — | n/a |

### Per-path honest notes
- **R1 (40):** an **independent universe is the strongest generalization test** — genuinely new data the s18 rule never saw, the cleanest probe of the "single-universe artifact?" question (axis 2 = 9; overfit-distance 8 = no reuse-snoop). Costs a fresh fetch + DR9 (axis 4 = 3) and is a fresh candidate (s19) with its own full ladder. Does NOT directly re-test the s18 *recent* weakness (a different universe's 2024-2025 is its own regime).
- **R2 (40):** **zero fetch** (axis 4 = 10) and directly foregrounds the F5 recent-weakness; tests whether the edge is stable to small first-principles parameter perturbations (a real overfitting probe) and across sub-periods. BUT it re-uses already-seen data, so it cannot provide *independent* generalization evidence (axis 2 = 4) — it tightens confidence, it does not extend it. Perturbation set must be pre-committed and first-principles (no selection), or it becomes T-FORBID-22/23 tuning.
- **R4 (27):** **largely not actionable now** — there is no data beyond 2025-12-30 to form a "more recent / longer" holdout without a fetch, and re-slicing the already-seen 2019-2025 data into finer rolling folds is snoop-prone (axis 3 = 4) and mostly re-confirms what K13 F5 already showed.
- **R3 (26):** **highest tuning risk** — "adjacent variations" is one step from a parameter search; near T-FORBID-22/23 (no fold/param search; no s18 tune). Only defensible for a single, a-priori-justified neighbor as a *fresh* candidate, and even then the garden-of-forking-paths risk is high. Lowest-recommended.
- **R5:** legitimate — s18 is already DIAGNOSTIC_ONLY with no live path; given the recent-fold weakness, pausing to avoid over-investing in a possibly-decaying edge is defensible.

----

## 4. Determination — recommend R1 (with R2 as a zero-fetch complement); no clean single blocker-free winner

**Recommendation: R1 (same mechanic, DIFFERENT universe)** is the strongest *direction* — the binding question is whether s18's edge generalizes beyond one universe, and only genuinely independent data answers it. It is a FRESH candidate (s19) requiring a future fetch + DR9 and its own full ladder; it is **not** a tune or `_revN_` of s18.

**R2 (stricter same-universe robustness)** is the recommended **zero-fetch complement / interim**: it cheaply tightens confidence and explicitly stress-tests the F5 recent-weakness and parameter-perturbation stability, but it cannot substitute for independent data.

**No clean blocker-free single winner:** R1 needs a fetch (a separate authorization) and is a multi-phase fresh candidate; R2 is cheap but provides no independent generalization; both are tied on total. R3/R4 are not recommended (tuning risk / not-actionable). **No Tier-N PLAN is auto-authored.**

**Honest meta-note:** s18 is already the line's strongest *diagnostic* result and there is **no live-promotion path** regardless of what replication finds (FRC NEVER_GRANTED; 6-gate block). Replication buys *confidence in a diagnostic finding*, not a path to capital. The operator may reasonably choose R5 (defer) if further diagnostic confidence has low marginal value.

----

## 5. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/code/fetch/backtest/new-OOS) | met |
| No `_revN_`/patch/tune of s18; replication is a FRESH candidate | met |
| No parameter search / adjacent-variation grid (T-FORBID-22/23) | met (R3 flagged high-risk, not recommended) |
| No promotion of s18 (no live path exists) | met |
| No revival / no retroactive K13 / no sealed-artifact modification | met |
| `lessons.md` not modified this turn | met |
| **No Tier-N PLAN auto-authored (no clean blocker-free winner)** | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 6. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/next_research_track_robustness_replication_plan_after_s18_oos_confirmed.md` | This robustness-replication selection plan (PLAN only; no JSON sidecar; no seal). |

No other repository file is modified.

----

## 7. Exact next-authorization options (operator chooses; each separate)

- **R1 — different universe (recommended; fresh candidate, needs a future fetch+DR9):**
  `Authorize s19-d1 weekly relative-strength rotation availability probe + DR9 audit framework only (independent large-cap universe; replication of the s18 mechanic).`
- **R2 — stricter same-universe robustness (zero fetch; fresh candidate):**
  `Authorize s19-d1 weekly relative-strength rotation stricter-robustness Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13; reuse the 24-name data; pre-committed first-principles parameter-perturbation stability + F5 recent-sub-period stress (no tuning/selection).`
- **Defer:** `Defer / Pause trading-bot track.`

----

End of PLAN. PLAN-authoring turn only. No code/backtest/fetch/new-OOS/DRAFT/SEAL/BUILD. **R1 (same mechanic, different universe) is the strongest robustness direction — independent data is the only clean test of whether s18's edge generalizes beyond one universe — but it needs a future fetch and is a fresh candidate; R2 (zero-fetch stricter robustness) is the recommended complement; no Tier-N PLAN auto-authored.** s18 remains DIAGNOSTIC_ONLY with no live path regardless of replication. No `_revN_`/tune of s18; no parameter search; no promotion; no revival; no retroactive K13; no sealed-artifact modification; no `lessons.md` modification. Trading `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

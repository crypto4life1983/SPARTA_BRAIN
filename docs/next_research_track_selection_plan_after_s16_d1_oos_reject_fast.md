# Next-research-track selection plan (after s16-d1 OOS REJECT_FAST; under DR10 v2)

Status: **PLAN_ONLY** (no code, no spec drafted/sealed, no data fetched, no signal computation, no backtest, no OOS, no live; the next step is a separate operator authorization to author a Tier-N spec PLAN for a selected track, or to fetch data for a chosen universe).

Authored: 2026-05-28
Authorization phrase: `Authorize next research-track selection plan after s16-d1 OOS REJECT_FAST only.`
Predecessors: `docs/next_research_track_selection_plan_after_s14_d1_cross_sector_terminal.md` (`89d6838`), `docs/next_research_track_selection_plan_after_s15_d1_cross_sector_terminal.md` (`343bdac`). **s16-d1 is now TERMINAL (REJECT_FAST at P10 OOS via DR4; P11 `99f58bd`).**

Trigger: s16-d1 P11 lifecycle decision `99f58bd` (P10 OOS `3d466f5`). Lessons LESSON_S16_D1_004/005/006 committed at `90afbb8`.

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT/SEAL/code/backtest/simulator/signal/fetch/OOS/live. No vendor API / API-key / network. No `review_queue`/`idea_memory` mutation. No Strategy Lab / candidate promotion / FRC. **No `_revN_`/patch of s16-d1 / s15-d1 / s14-d1.** **No re-run of s16 with a tweaked OOS window or relaxed DR4 (no threshold reinterpretation).** **No post-hoc regime filter bolted onto s16 to rescue its OOS result.** **No retroactive framework application to old candidates. No revival of s16/s15/s14/s13/s12.** No modification of any sealed artifact. No `lessons.md` modification or staging (S16 lessons already committed at `90afbb8`; cited only). No commit beyond this doc's own authorization. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. Context: what the three terminals establish, and how the binding axis has migrated

| Candidate | Family | Furthest phase | Terminal driver |
|---|---|---|---|
| s14-d1-cross-sector | RSI(3)+2N mean-reversion (3-name) | P6 IS | FAIL_SAFETY (negative IS edge) |
| s15-d1-cross-sector | z-score exit-to-mean mean-reversion (3-name) | P6 IS | FAIL_SAFETY (negative IS edge; exit/stop fix improved risk not edge) |
| s16-d1-expanded | Donchian-20/10 trend (12-name) | **P10 OOS** | **REJECT_FAST (DR4): IS+cost-stress positive, but OOS edge negative** |

**The binding selection axis has migrated across the line:**
- post-s13 (rev1): DR10 reachability · post-s14 (rev2): K9-OOS reachability · post-s14-cross-sector: exit/stop edge design · post-s15: (same; led to s16 trend).
- **NOW (post-s16): OOS GENERALIZATION / REGIME-ROBUSTNESS.** s16 cleared every prior axis (K9, DR9, DR10-v2, A7/K10, exit/stop design, positive IS edge, cost-stress survival) and still failed — because the edge did not generalize out-of-sample (LESSON_S16_D1_004). The new question a candidate must answer is: *will the IS edge survive an OOS regime that differs from the IS regime?*

### 1.1 A subtlety that makes this harder (honest caveat)

The s16 IS window (2019-01-02→2023-12-29) **already spanned multiple regimes** — including the 2022 large-cap/tech bear. So the OOS failure is **not** a simple "IS was all-bull" overfit. The 2024-2025 OOS regime (mega-cap concentration + sector rotation; defensive/staples trended while broad tech/energy chopped) simply did not suit the Donchian rule. **Regime-robustness is therefore not a one-line fix** (a longer/multi-regime IS would not obviously have prevented this). Any "regime filter" track must reckon with this.

----

## 2. Forbidden tracks (carry T-FORBID-1..18; this plan ADDS T-FORBID-19..21)

- **T-FORBID-19**: Any `_revN_`/parameter-patch of s16-d1 (Donchian-20/10, 2N stop, 12-name basket).
- **T-FORBID-20**: Re-running s16 with a tweaked OOS window, a relaxed DR4, or any threshold reinterpretation to convert the OOS REJECT into a pass (`no_dr_redefinition_post_seal`).
- **T-FORBID-21**: Bolting a regime filter onto s16 post-hoc to rescue its OOS result (= K7 silent-filter / overfitting-to-OOS). A regime filter is admissible ONLY as a FRESH candidate whose filter is justified from first principles at PLAN/SEAL, never fitted to the s16 OOS outcome.

Prior forbiddens carry: no mean-reversion re-skin on AAPL/JPM/XOM (T-FORBID-17/18); no revival of any terminal/parked candidate. The all-tech DRAFT `214bae0` (RSI(3)+2N) remains preserved and not recommended.

----

## 3. Track candidates (scored on the new binding axis: OOS-generalization / regime-robustness)

Axes (/10): **OOS-generalization-robustness (PRIMARY)**, K9 reachability, DR10-v2 reachability, data/fetch friction, overfitting-risk (K7-distance), implementation complexity, reuse-DR9-data. Total /70.

### 3.1 T1 — Trend/breakout with a FIRST-PRINCIPLES regime filter, on the 12-name reuse basket

| Field | Value |
|---|---|
| Mechanic | Donchian/MA breakout trend + a regime gate justified a priori (e.g., trade longs only when price > long-horizon MA / regime-up; trade trend only when a slow trend-strength proxy is positive). NOT s16 with a fitted filter. |
| Universe | `{12-name}` reuse (DR9-passed `245ac0d`); zero fetch |
| OOS-robustness | **MODERATE** — a regime gate is the textbook response to s16's regime-dependence (LESSON_S16_D1_005), but §1.1 warns it is not a guaranteed fix |
| K9 reachability | **WEAK-MODERATE** — a regime filter cuts trades; s16 was ~65/y IS / ~67/y OOS, a filter could drop this toward/below the 50/y OOS floor; must be shown at PLAN |
| Overfitting risk (K7) | **ELEVATED** — the filter must be first-principles and NOT tuned to the s16 OOS; clears T-FORBID-21 only with a clean a-priori justification |
| Data/fetch | zero (reuse) |

**T1 scoring:** OOS-robustness **6** · K9 **5** · DR10-v2 **9** · data/fetch **10** · overfitting-distance **5** · complexity **6** · reuse-DR9 **10** → **51/70**.

### 3.2 T2 — Cross-sectional relative-strength / dual-momentum rotation, broader universe

| Field | Value |
|---|---|
| Mechanic | Rank a broad universe (e.g., 20-40 large-caps or sector ETFs) by trailing momentum; hold top-N; periodic rebalance. Relative (cross-sectional) rather than absolute-directional. |
| OOS-robustness | **MODERATE-STRONG** — relative momentum is less single-direction-regime-dependent than absolute trend (it rotates into whatever is leading), which directly addresses the s16 failure mode (defensive led OOS; a relative system would have rotated into them) |
| K9 reachability | **WEAK** — rotation is low-turnover (monthly rebalance → few "trades"); K9-light, likely fails OOS ≥50/y unless trade-counting is defined per-rebalance-leg |
| Data/fetch | **FETCH REQUIRED** (broader universe) → gated out of immediate PLAN; needs availability-probe + DR9 first |
| Overfitting risk | LOW-MODERATE |

**T2 scoring:** OOS-robustness **8** · K9 **4** · DR10-v2 **9** · data/fetch **4 (fetch)** · overfitting-distance **7** · complexity **6** · reuse-DR9 **2** → **40/70**.

### 3.3 T3 — Same trend family, multi-regime / walk-forward validation discipline (framework-level)

| Field | Value |
|---|---|
| Idea | Keep a trend family but require a WALK-FORWARD / multi-window validation (rolling IS/OOS folds) BEFORE the full ladder, so a single IS/OOS split cannot produce a false positive. |
| OOS-robustness | **STRONG in principle** — directly attacks LESSON_S16_D1_004 (IS+cost-stress not sufficient) by demanding cross-window persistence |
| Caveat | This is a **framework-discipline change**, not just a candidate; §1.1 shows s16's IS already spanned regimes, so walk-forward raises the bar but is not a guaranteed pass. Requires a framework-level SEAL revision (analogous to the DR10 v2 revision), NOT a post-hoc candidate tweak. |
| K9 / data | depends on instantiation |

**T3 scoring (as a framework move, not a candidate):** OOS-robustness **9** · K9 **n/a** · DR10-v2 **n/a** · data/fetch **n/a** · overfitting-distance **9** · complexity **4 (framework change)** · reuse-DR9 **8** → not directly comparable; recorded as a **framework-improvement option**.

### 3.4 T4 — Pause / strategic reconsideration

After three cash-equity-daily terminals, a legitimate option is to pause the trading-bot track and reconsider domain/approach (e.g., whether daily cash-equity is the right domain, or whether the validation discipline should change per T3) rather than immediately authoring a fourth candidate. Not scored.

----

## 4. Score summary + recommendation

| Track | Total | OOS-robustness | K9 | data/fetch | overfit-distance |
|---|---:|---:|---:|---:|---:|
| **T1: regime-filtered trend on reuse 12-name** | **51/70** | 6 | 5 | 10 | 5 |
| T2: cross-sectional momentum rotation, broader universe | 40/70 | 8 | 4 | 4 (fetch) | 7 |
| T3: walk-forward validation discipline (framework move) | — | 9 | — | — | 9 |
| T4: pause / reconsider | n/a | — | — | — | — |

### Determination

**There is no clean blocker-free single-candidate winner.** The new binding axis (OOS-generalization) is hard to satisfy cheaply: the zero-fetch option (T1) carries both a K9-after-filtering risk and an elevated K7/overfitting risk, and §1.1 shows a regime filter is not a guaranteed fix; the more OOS-robust option (T2) needs a fetch and is K9-light; the most principled response (T3) is a **framework-discipline change** (walk-forward validation), not a candidate.

**Recommendation (operator decides; each separate authorization):**
1. **Strongest framework move — T3:** adopt a walk-forward / multi-window validation requirement before the full ladder. This directly encodes LESSON_S16_D1_004 (IS+cost-stress is not sufficient) and is the highest-leverage response to three terminals. It is a framework-level SEAL revision, not a candidate, so it would be authored like the DR10 v2 revision.
2. **Strongest zero-fetch candidate — T1:** regime-filtered trend on the reuse 12-name basket, with the filter first-principles-justified at PLAN/SEAL (clears T-FORBID-21) and a PLAN-time K9-after-filter reachability table (K9-blocked if it cannot show ≥50/y OOS).
3. **Most OOS-robust candidate (needs fetch) — T2:** cross-sectional momentum rotation on a broader universe; requires an availability-probe + DR9 audit first.
4. **T4:** pause / reconsider.

----

## 5. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/code/fetch/backtest/OOS) | met |
| No `_revN_`/patch of s16/s15/s14; no s16 OOS-window-tweak or DR4 relaxation; no post-hoc regime filter on s16 (T-FORBID-19/20/21) | met |
| No revival of s16/s15/s14/s13/s12; no promotion of any candidate | met |
| No modification of any sealed artifact | met |
| `lessons.md` not modified by this plan (S16 lessons committed at 90afbb8) | met |
| No data fetch / vendor API / network | met |
| **No Tier-N PLAN auto-authored (no clean blocker-free winner; framework-move T3 may precede)** | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 6. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/next_research_track_selection_plan_after_s16_d1_oos_reject_fast.md` | This selection plan (PLAN only; no JSON sidecar; no seal — planning document, per predecessor convention). |

No other repository file is modified.

----

## 7. Exact next-authorization options (operator chooses; each separate)

- **Framework move (recommended highest-leverage):** `Authorize framework walk-forward / multi-window validation discipline revision PLAN only.`
- **T1 candidate (zero fetch):** `Authorize s17-d1 expanded-universe regime-filtered trend Tier-N spec PLAN only — bound by DR10 v2; PLAN must justify the regime filter from first principles (not fitted to s16 OOS) and include a K9-after-filter OOS reachability table.`
- **T2 candidate (fetch first):** `Authorize s17-d1 broad-universe cross-sectional momentum availability probe + DR9 audit framework only.`
- **Pause:** `Defer / Pause trading-bot track.`

----

End of selection plan. PLAN only. No code/backtest/fetch/DRAFT/SEAL/BUILD. **No Tier-N PLAN authored this turn — no clean blocker-free winner; the highest-leverage response (T3 walk-forward validation) is a framework-discipline move, not a candidate.** Trading `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. s16/s15/s14 terminals preserved verbatim; all sealed artifacts byte-stable.

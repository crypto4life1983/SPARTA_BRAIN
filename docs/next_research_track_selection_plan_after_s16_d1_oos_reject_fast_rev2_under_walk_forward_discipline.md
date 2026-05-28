# Next-research-track selection plan rev2 (after s16-d1 OOS REJECT_FAST; under the walk-forward validation discipline)

Status: **PLAN_ONLY** (no code, no spec sealed, no data fetched, no backtest, no OOS, no live; the next step is a separate operator authorization to author a Tier-N spec PLAN for a selected track, or to fetch data for a chosen universe).

Authored: 2026-05-28
Authorization phrase: `Authorize next research-track selection plan after s16-d1 OOS REJECT_FAST rev2 under walk-forward validation discipline only.`
Supersedes: rev1 at `56ddd4d` (`docs/next_research_track_selection_plan_after_s16_d1_oos_reject_fast.md`). Rev2 re-scores the candidate directions under the **newly sealed walk-forward / multi-window validation discipline** (framework SEAL `52a3b60`; K13 walk-forward-persistence gate; binds s17+).

Trigger for rev2: framework discipline revision SEAL `52a3b60` (`reports/framework_walk_forward_validation_revision_seal_v1.json`, report_seal `4268d6f75bbc095a795510f7d8ccc50c2d8886eef36f50f769b79342002893d2`). The K13 gate + fixed 5-fold scheme + P6.7 placement now bind every s17+ candidate.

----

## HARD BOUNDARIES (held by this rev2 PLAN)

PLAN only. No DRAFT/SEAL/code/backtest/simulator/signal/fetch/OOS/live. No vendor API / network. No `review_queue`/`idea_memory` mutation. No Strategy Lab / promotion / FRC. **No `_revN_`/patch/revival of s16/s15/s14/s13/s12; no retroactive application of the walk-forward discipline to any prior candidate (their verdicts stand).** No modification of any existing sealed artifact (incl. `framework_walk_forward_validation_revision_seal_v1` `52a3b60`, `framework_dr10_revision_seal_v2` `78cd22e`). No `lessons.md` modification or staging. No commit beyond this doc's own authorization. **No per-fold optimization / no fold-scheme search** (the SEAL's anti-snoop safeguards are inviolate). Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. What changed since rev1

| Field | rev1 (`56ddd4d`) | rev2 (under walk-forward SEAL `52a3b60`) |
|---|---|---|
| Walk-forward validation | proposed as a candidate "T3" framework idea | **SEALED and binding for s17+** (K13 gate, fixed 5-fold scheme, P6.7 phase) |
| Binding scoring axis | OOS-generalization / regime-robustness (informal) | **K13 walk-forward persistence — now a formal, binding gate** (≥3 of 5 OOS folds positive + aggregate-positive + K9 holds, else OOS_NOT_ROBUST→REJECT_FAST) |
| What a candidate must now survive | single P10 OOS (the s16 failure point) | **K13 at P6.7 (multi-fold persistence) BEFORE P10** |
| rev1 "T3 walk-forward as a track" | a track option | **REMOVED as a track — it is now the binding discipline, not a candidate** |

**Implication:** the bar is now explicitly higher. A candidate must show its LOCKED edge persists across 5 sequential OOS folds, not just one. The right rev2 question is: **which direction is most likely to actually clear K13?**

----

## 2. Forbidden tracks (carry T-FORBID-1..21; rev2 adds T-FORBID-22)

- **T-FORBID-22**: Any candidate whose apparent K13 pass depends on per-fold parameter re-fitting or on a searched/anchored fold scheme (= data-snooping; violates the walk-forward SEAL's inviolate anti-snoop safeguards). K13 must be cleared by a LOCKED rule re-evaluated on the fixed, pre-committed fold scheme.
- Carried: T-FORBID-17/18 (no mean-reversion re-skin on AAPL/JPM/XOM), T-FORBID-19/20/21 (no s16 `_revN_`/OOS-window-tweak/DR4-relaxation/post-hoc-regime-filter-rescue), and all prior. No revival of any terminal/parked candidate.

----

## 3. Tracks re-scored by EXPECTED K13 survivability (the new binding axis)

Axes (/10): **expected-K13-walk-forward-survivability (PRIMARY)**, K9-per-fold reachability, DR10-v2 reachability, data/fetch friction, overfitting-distance (K7/T-FORBID-22), implementation complexity, reuse-DR9-data. Total /70.

### 3.1 T1 (rev2) — Regime-filtered trend on the 12-name reuse basket
- Mechanic: Donchian/MA trend + a first-principles regime gate (e.g., long only in regime-up). Zero fetch (reuse `245ac0d`).
- **K13 outlook: UNCERTAIN-to-LOW.** s16's unfiltered trend already failed the single OOS; a regime filter aims at persistence but s16's IS already spanned 2022, so multi-fold persistence is not assured. A filter that cuts trades also stresses **K9-per-fold** (5 folds → each fold needs its own ≥-floor sample). Elevated K7/T-FORBID-22 risk if the filter is tuned to pass folds.
- **Scoring:** K13-survivability **5** · K9-per-fold **4** · DR10-v2 **9** · data/fetch **10** · overfit-distance **5** · complexity **6** · reuse-DR9 **10** → **49/70**.

### 3.2 T2 (rev2) — Cross-sectional relative-strength / dual-momentum rotation, broader universe
- Mechanic: rank a broad universe (≈20-40 large-caps or sector ETFs) by trailing momentum; hold top-N; periodic rebalance. Relative (cross-sectional), not absolute-directional.
- **K13 outlook: BEST of the price-based options.** Relative momentum rotates into whatever is leading in each regime, so it is structurally the most likely to **persist across folds** (it would have rotated into the OOS leaders — defensive/staples — that beat s16's absolute trend). This is the most K13-aligned direction.
- **Frictions:** needs a fresh fetch (broader universe → availability-probe + DR9 first); rotation is low-turnover → **K9-per-fold is the key risk** (few "trades" per fold; trade-counting must be defined per-rebalance-leg and shown to clear the floor in each of 5 folds).
- **Scoring:** K13-survivability **8** · K9-per-fold **4** · DR10-v2 **9** · data/fetch **4 (fetch)** · overfit-distance **7** · complexity **6** · reuse-DR9 **2** → **40/70**.

### 3.3 T3 (rev2) — Defer / strategic reconsideration
- After three terminals (s14/s15 IS-fail; s16 OOS-fail) and with K13 now raising the bar, a legitimate option is to pause the trading-bot track and reconsider domain/approach (daily price-only cash-equity may be a structurally hard domain for a K13-surviving edge). Not scored.

----

## 4. Score summary + recommendation

| Track | Total | K13-survivability | K9-per-fold | data/fetch | overfit-distance |
|---|---:|---:|---:|---:|---:|
| T1 (rev2): regime-filtered trend, reuse 12-name | 49/70 | 5 | 4 | 10 | 5 |
| **T2 (rev2): cross-sectional momentum rotation, broader universe** | **40/70** | **8** | 4 | 4 (fetch) | 7 |
| T3 (rev2): defer / reconsider | n/a | — | — | — | — |

### Determination + honest read

**The two are close on total but diverge on the binding axis.** T1 scores higher overall purely on data-reuse (zero fetch), but its **K13-survivability is weak** — it is the cheapest, not the most likely to pass the new gate. T2 has the **best K13 outlook** (relative momentum is the most regime-robust price-based family) but pays a fetch + a real **K9-per-fold** concern.

**Honest meta-observation (load-bearing):** K13 was sealed precisely because single-window edges keep failing. It will, by design, **reject candidates that lack genuine multi-regime persistence — which plausibly includes most price-only daily cash-equity rules already tried.** The operator should expect a higher rejection rate and decide deliberately:
- if willing to invest a fetch for the **most K13-aligned** direction → **T2** (cross-sectional momentum rotation), with a PLAN-time K13-per-fold + K9-per-fold reachability table required;
- if preferring zero-fetch → **T1**, accepting weak K13 odds and a first-principles (untuned) regime filter (clears T-FORBID-21/22 only with a clean a-priori justification);
- if neither is compelling under the higher K13 bar → **T3 defer / reconsider domain**.

**Recommendation:** **T2 (rev2)** is the strongest *direction* under the K13 discipline (best persistence outlook), conditional on a fetch; there is **no clean blocker-free single-candidate winner** (T2 needs a fetch + must demonstrate K9-per-fold; T1 is zero-fetch but weak on the binding axis). No Tier-N PLAN is auto-authored.

----

## 5. Boundaries held this rev2 PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/code/fetch/backtest/OOS) | met |
| No retroactive application of the walk-forward discipline to s16/s15/s14/s13/s12 | met |
| No `_revN_`/patch/revival of any candidate | met |
| No per-fold optimization / no fold-scheme search (T-FORBID-22; SEAL anti-snoop inviolate) | met |
| No modification of any sealed artifact (incl. WF SEAL 52a3b60, DR10 v2 78cd22e) | met |
| `lessons.md` not modified | met |
| **No Tier-N PLAN auto-authored (no clean blocker-free winner)** | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 6. Files written this rev2 PLAN turn

| File | Purpose |
|---|---|
| `docs/next_research_track_selection_plan_after_s16_d1_oos_reject_fast_rev2_under_walk_forward_discipline.md` | This rev2 selection plan (PLAN only; no JSON sidecar; no seal — planning document). |

No other repository file is modified.

----

## 7. Exact next-authorization options (operator chooses; each separate)

- **T2 — most K13-aligned (fetch first):** `Authorize s17-d1 broad-universe cross-sectional momentum availability probe + DR9 audit framework only.`
- **T1 — zero-fetch (weak K13 odds; first-principles filter):** `Authorize s17-d1 expanded-universe regime-filtered trend Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13; PLAN must justify the regime filter from first principles (not fitted) and include K13-per-fold + K9-per-fold reachability tables.`
- **Defer / reconsider:** `Defer / Pause trading-bot track.`

----

End of rev2. PLAN-authoring turn only. No code/backtest/fetch/DRAFT/SEAL/BUILD. **No Tier-N PLAN authored — no clean blocker-free winner; T2 (cross-sectional momentum rotation) is the most K13-aligned direction but requires a fetch and a K9-per-fold demonstration.** The walk-forward K13 discipline (`52a3b60`) binds every s17+ candidate. No retroactive application; no existing-gate relaxation; no candidate revival; no sealed-artifact modification; no `lessons.md` modification. Trading `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

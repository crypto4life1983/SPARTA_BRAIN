# Next-research-track selection plan (after s19-d1 OOS INSUFFICIENT_SAMPLE / K9)

Status: **PLAN_ONLY** (no code, no spec sealed, no data fetched, no backtest, no OOS; the next step is a separate operator authorization to author a Tier-N spec PLAN or a RUN_BOOK for a selected path, or to defer).

Authored: 2026-05-29
Authorization phrase: `Authorize next research-track selection plan after s19-d1 OOS INSUFFICIENT_SAMPLE only.`
Trigger: s19-d1 (replication of s18 weekly RS on an independent universe) terminated at P10 by **INSUFFICIENT_SAMPLE/K9** (P11 `81563fd`; P10 `9c018bb`). The s18 weekly RS **edge generalized** (s19 OOS net +$44,050, expectancy +$336/trade, sharpe +0.238, DR4 no-fire; P6.7 K13 5/5) but the s19 candidate's OOS turnover (43.6/y, 87 trades) fell below the K9 ≥50/y floor. Lessons LESSON_S19_D1_001/002/003 committed `26e79bf`. Binds under **DR10 v2** (`78cd22e`) + **walk-forward K13** (`52a3b60`).

----

## HARD BOUNDARIES (held by this PLAN; binding on any selected track)

PLAN only. No DRAFT/SEAL/code/backtest/simulator/signal/fetch/OOS/live. No Strategy Lab / promotion / FRC / broker / review_queue. **The plan FORBIDS:** any `_revN_`/patch of s19; **changing s19 after seeing the K9 failure** (wider-N on the *same* s19 spec to fix K9 = a post-hoc tune); **lowering K9** (the floor is inviolate); retroactive K13/DR10 reinterpretation; promoting s18 or s19; any live/paper/Strategy-Lab/FRC action. No `lessons.md` modification (S19 lessons committed `26e79bf`). No commit beyond this doc's own authorization. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. The binding constraint after s18 + s19

| Candidate | OOS edge | OOS turnover | Verdict |
|---|---|---|---|
| s18 weekly (24-name) | +$39,786 (+$210/trade) | 58.7/y (117 trades) | OOS_CONFIRMED_DIAGNOSTIC (but recent-fold weak) |
| s19 weekly (independent 24-name) | +$44,050 (+$336/trade, stronger) | **43.6/y (87 trades)** | **INSUFFICIENT_SAMPLE/K9** |

**The edge is portable (positive on two independent universes); the recurring binding blocker is OOS turnover/sample.** A top-8 weekly rotation on 24 names sits right at the K9 ≥50/y margin — s18 cleared it, s19 didn't. **Governing constraint for the next candidate (LESSON_S19_D1_002/003 + operator guidance): the design must SOLVE OOS K9 BY STRUCTURE (genuine breadth/turnover headroom) and prove it at the pre-SEAL K9 measurement (necessary) AND at P10 (binding) — NOT by tuning s19, NOT by lowering K9.**

----

## 2. Tracks (the bundle requires comparing T1–T5)

- **T1** — same locked weekly RS mechanic, **broader FRESH independent universe** (≈40–50 large-caps, zero overlap with s18/s19), enough breadth that top-8 boundary churn clears OOS K9. Fresh fetch + DR9 required.
- **T2** — same s19 24-name universe, **wider held-N** (e.g., top-12) to lift turnover.
- **T3** — **combined s18+s19 broad universe (48 names, zero fetch)** with explicit anti-overfit controls; more breadth → more boundary churn → OOS K9 headroom. Reuses both DR9-passed sets (`d86e5d1` + `574fa9e`).
- **T4** — **sector/industry ETF universe** weekly RS — lower single-name noise; fresh fetch + DR9.
- **T5** — **defer / pause.**

----

## 3. Scoring (8 axes /10 each; total /80). PRIMARY = OOS K9 reachability by structure (the binding blocker).

| Track | OOS-K9 reach | K13 per-fold | edge portability/independence | DR10 v2 | data/fetch friction | diversification | impl. simplicity | not-a-post-hoc-tune | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **T1** broader fresh universe | 8 | 8 | **9** | 8 | 3 (fetch+DR9) | 9 | 6 | **9** | **60/80** |
| **T3** combined s18+s19 48-name (zero fetch) | 8 | 8 | 6 | 8 | **10** | 9 | 6 | **5** | **60/80** |
| T2 s19 24-name wider held-N | 7 | 7 | 4 | 8 | 10 | 6 | 7 | **2** | **51/80** |
| T4 sector/industry ETF RS | **4** | 5 | 7 | 8 | 3 | 7 | 6 | 8 | **48/80** |
| T5 defer/pause | — | — | — | — | — | — | — | — | n/a |

### Per-track honest notes
- **T1 (60):** the **cleanest** sample-safe generalization test — a never-tested universe avoids any selection bias (axis 8 = 9), broader breadth lifts top-8 turnover toward the K9 floor with margin (axis 1 = 8), and it independently re-tests portability (axis 3 = 9). BUT it requires a fresh fetch + DR9 (axis 5 = 3) → a RUN_BOOK→fetch→DR9 must precede the PLAN; **it cannot go straight to a Tier-N PLAN this bundle.**
- **T3 (60):** the **cheapest** path — zero fetch (reuse both DR9-passed sets; axis 5 = 10), and 48-name breadth gives the best structural OOS-K9 headroom without new data. BUT it carries a real **anti-overfit/selection concern (axis 8 = 5):** the combined universe *includes the known-OOS-confirmed s18 24 names*, so it is partly composed of a basket already shown to work — a soft selection bias. Mitigable with explicit controls (union of two PRE-COMMITTED independent baskets, NOT cherry-picked; locked-identical mechanic; edge re-proven at P6 IS; disclose the s18-inclusion) but NOT cleanly blocker-free.
- **T2 (51):** **near-forbidden.** Widening held-N on the *same s19 universe that just K9-failed*, after seeing that failure, is a post-hoc patch (axis 8 = 2) — squarely in the "changing s19 after seeing K9 failure" prohibition. Not recommended.
- **T4 (48):** **worsens the binding constraint** — sector/industry ETF ranks are stickier than single names, so weekly turnover is LOWER (axis 1 = 4), making OOS K9 *harder*, plus a fresh fetch. Poor fit for a sample-size-solving goal.

----

## 4. Determination — NO clear blocker-free winner; no Tier-N PLAN auto-authored

T1 and T3 tie at 60/80 and trade off cleanly against each other: **T1 is the anti-overfit-cleanest + most-independent generalization test but is fetch-gated** (a RUN_BOOK→fetch→DR9 must precede its PLAN); **T3 is zero-fetch and structurally sample-safe but carries a genuine selection concern** (it reuses the known-OOS-good s18 universe). Both have OOS-K9 reachability that is *projected, not proven* (LESSON_S19_D1_003 — the exact thing that bit s19; only the pre-SEAL measurement + P10 are binding). **There is therefore no single clear blocker-free winner, so NO Tier-N PLAN is auto-authored** (per the bundle's Step 3 gate).

**Recommendation (operator chooses):**
- If you want the **cleanest generalization evidence** and accept a fetch → **T1** (broader fresh universe): authorize its **RUN_BOOK** first (fetch is a separate authorization).
- If you want the **fastest zero-fetch sample-safe test** and accept the disclosed anti-overfit caveat → **T3** (combined 48-name): authorize its **Tier-N PLAN** directly (reuses DR9-passed data), with the PLAN required to (a) treat the universe as the fixed union of two pre-committed baskets, (b) include K9-aggregate / OOS-K9 / K13-per-fold / DR10-v2 reachability tables, (c) re-prove the edge at P6 IS, (d) carry the pre-SEAL K9 measurement as the binding sample gate.
- **Honest meta-note:** the edge is already corroborated across two universes; there is **no live path regardless** (FRC NEVER_GRANTED; 6-gate block). A third candidate buys *diagnostic confidence about OOS-K9 reachability*, not capital. T5 (defer) is legitimate if that marginal value is low.

----

## 5. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/code/fetch/backtest/OOS) | met |
| No s19 `_revN_`/patch; no changing s19 after the K9 failure (T2 flagged near-forbidden, not recommended) | met |
| No lowering K9; no K9/K13/DR10 retroactive reinterpretation | met |
| No promotion of s18/s19; no live/paper/Strategy-Lab/FRC | met |
| No revival of any terminal/frozen candidate | met |
| `lessons.md` not modified this turn (S19 lessons committed 26e79bf) | met |
| **No Tier-N PLAN auto-authored (no clear blocker-free winner)** | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 6. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/next_research_track_selection_plan_after_s19_d1_oos_insufficient_sample.md` | This selection plan (PLAN only; no JSON sidecar; no seal). |

No other repository file is modified.

----

## 7. Exact next-authorization options (operator chooses; each separate)

- **T1 — broader fresh independent universe (cleanest; fetch-gated):**
  `Authorize s20-d1 broader-universe weekly relative-strength rotation availability probe + DR9 audit framework only (independent ~40-50 large-caps; replication of the s18/s19 mechanic; sample-size-safe breadth).`
- **T3 — combined s18+s19 48-name (zero fetch; fastest; anti-overfit-disclosed):**
  `Authorize s20-d1 combined-universe (s18+s19, 48-name) weekly relative-strength rotation Tier-N spec PLAN only — bound by DR10 v2 + walk-forward K13; reuse DR9-passed data; fixed union of two pre-committed baskets; pre-SEAL K9-reachability table required; edge re-proven at P6 IS; no tuning.`
- **Defer:** `Defer / Pause trading-bot track.`

----

End of PLAN. PLAN-authoring turn only. No code/backtest/fetch/DRAFT/SEAL/BUILD. **The s18 weekly RS edge is portable (corroborated on two independent universes); the binding blocker is OOS turnover/sample (K9). T1 (broader fresh universe) is the anti-overfit-cleanest sample-safe direction but fetch-gated; T3 (combined 48-name, zero fetch) is the fastest but carries a disclosed selection concern; neither is a clear blocker-free winner, so NO Tier-N PLAN is auto-authored.** No s19 `_revN_`/tune; no lowering K9; no retroactive K13/DR10; no promotion; no revival; no `lessons.md` modification. Trading `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

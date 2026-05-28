# Next-research-track selection plan (after s15-d1-cross-sector terminal FAIL_SAFETY; under DR10 v2)

Status: **PLAN_ONLY** (no code written, no spec drafted, no spec sealed, no data fetched, no signal computation, no backtest, no OOS, no live; the next step is a separate operator authorization to author a Tier-N spec PLAN for a selected track, or to fetch data for a K9-clearing universe).

Authored: 2026-05-28
Authorization phrase: `Authorize post-s15 terminal continuation bundle: lessons update, next-track selection plan, and first PLAN for the selected fresh candidate if and only if the selection plan has a clear winner.`
Predecessors: `docs/next_research_track_selection_plan_after_s14_d1_cross_sector_terminal.md` (commit `89d6838`, which selected T1 = s15-d1 z-score exit-to-mean). **Both s14-d1-cross-sector (RSI(3)+2N) and s15-d1-cross-sector (z-score exit-to-mean) are now TERMINAL FAIL_SAFETY.**

Trigger: s15-d1-cross-sector P7 decision memo `8abcd31` (P6 IS `2a6d130`) formalized FAIL_SAFETY. Lessons LESSON_S15_D1_001/002/003 committed at `fb805a1`.

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No data fetch. No vendor API / API-key access. No network IO. No `review_queue.json` / `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No `_revN_` / patch of s15-d1 or s14-d1-cross-sector.** **No another daily mean-reversion tweak on AAPL/JPM/XOM.** **No reusing RSI(3)+2N or z-score exit-to-mean on the same basket as a new candidate.** **No retroactive application of any framework revision to old candidates.** **No promotion of any prior candidate.** No revival of s15-d1 / s14-d1 / s13-d1 / s12-d1. No modification of any existing sealed artifact. No phase-2 safety contract template / CLAUDE.md / `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging** (S15 lessons already committed at `fb805a1`; cited only). No git commit beyond this doc (commit is part of the authorized bundle). No live trading. No profitability claim. Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED`.

----

## 1. Context: what the two cross-sector terminals establish

| Candidate | Mechanic | Trades | Expectancy/trade | sharpe_proxy | maxdd | Verdict |
|---|---|---:|---:|---:|---:|---|
| s14-d1-cross-sector | RSI(3) bi-dir + fixed 2N stop | 348 | −$39.53 | −0.1119 | 14.04% | FAIL_SAFETY |
| s15-d1-cross-sector | z-score + exit-to-mean + 3.5σ stop | 180 | −$28.49 | −0.0938 | 7.17% | FAIL_SAFETY |

Both cleared K9, DR9, DR10 v2, and A7/K10 diversification. The s15 exit/stop redesign **improved risk geometry materially but did not create edge** (LESSON_S15_D1_001). **Two distinct mean-reversion mechanics failing on AAPL/JPM/XOM with ample sample ⇒ the mean-reversion edge on this universe over 2019-2023 IS appears structurally absent** (LESSON_S15_D1_002).

### 1.1 The binding tension for the next track

The cross-sector basket's **data/diversification quality is strong and reusable** (DR9 passed; A7≈2.09 / K10≈0.45 in band; zero fetch). But:
- **Mean-reversion** is the family that clears K9 comfortably on a 3-name daily basket (frequent signals) — and its edge here is exhausted.
- **Non-mean-reversion** families (trend/momentum/breakout, rotation) are **K9-light** on a 3-name daily basket (trend round-trips ≈ 6-24/y basket, well under the 50/y OOS K9 floor).

So the next track faces a structural trade-off: **reuse the proven data (zero fetch) but accept a K9-OOS reachability problem for a non-MR mechanic, OR change/expand the universe (fetch friction) to get a K9-clearing non-MR mechanic.** This tension is the central finding of this plan and determines whether a clear blocker-free winner exists.

----

## 2. Forbidden tracks (carry prior T-FORBID-1..15; this plan ADDS T-FORBID-16..18)

- **T-FORBID-16**: Any `_revN_` / parameter-patch of s15-d1-cross-sector (z-score L=20/k=2.0, exit-to-mean, 3.5σ stop, time-stop 10).
- **T-FORBID-17**: A third daily mean-reversion mechanic on AAPL/JPM/XOM (predictable framework waste per LESSON_S15_D1_002/003 — two same-family failures with ample sample).
- **T-FORBID-18**: Reusing RSI(3)+2N or z-score exit-to-mean as a "new" candidate on the same basket (these are the terminal mechanics).

The all-tech sibling DRAFT `214bae0` (AAPL/MSFT/NVDA, RSI(3)+2N) shares the terminal s14 mechanic and a less-diversified basket; **not recommended for advancement** and not revived here.

----

## 3. Reachability disciplines (carried; the decisive axis this round is K9-OOS for non-MR mechanics)

| Window | Length (y) | K9 floor |
|---|---:|---|
| IS 2019-01-02 → 2023-12-29 | ~5.0 | ≥ 20 trades/y (≥100 total) |
| **OOS 2024-01-02 → 2025-12-30** | **~2.0** | **≥ 50 trades/y (BINDING)** |

DR10 v2 (cost_drag branch) is permissive for cash equity (clears). DR9 is **already PASSED** for AAPL/JPM/XOM (reusable, zero fetch).

----

## 4. Track candidates (scored on the required axes)

Axes (/10): **first-principles-avoids-s14/s15-failure**, **K9 reachability (IS+OOS)**, DR10-v2 reachability, **data availability / fetch friction**, diversification/concentration, implementation complexity, can-reuse-DR9-data. Total /70.

### 4.1 T1 — Cash-equity trend/momentum/breakout on the SAME DR9-passed AAPL/JPM/XOM universe

| Field | Value |
|---|---|
| Mechanic family | trend / time-series-momentum / breakout (e.g., Donchian or dual-MA) with a trailing stop — the **opposite** family to the failed mean-reversion |
| Universe | `{AAPL, JPM, XOM}` — reuse DR9-passed sealed CSVs (`b13af03`); **zero fetch** |
| First-principles vs s14/s15 | **STRONG** — directly tests whether the universe has a TREND edge where it lacks a MR edge; not a mean-reversion tweak; clears T-FORBID-16/17/18 |
| K9 reachability | **WEAK / likely FAILS** — daily trend/breakout on 3 names ≈ 6-24/y basket; OOS needs ≥50/y. Trend round-trips per name (~3-10/y) cannot reach 50/y on 3 names at daily frequency. **This is a structural K9-OOS blocker.** |
| DR10-v2 | clears (low turnover → cost_drag tiny) |
| Data / fetch | **ZERO fetch** (reuse) — strongest on this axis |
| Diversification | in-band (same universe; A7≈2.09 / K10≈0.45) |
| Complexity | moderate (trailing stop + per-name trend state) |
| Reuse DR9 data | **YES** |

**T1 scoring:** first-principles **9** · **K9 reachability 3 (likely fails OOS)** · DR10-v2 **9** · data/fetch **10** · diversification **8** · complexity **6** · reuse-DR9 **10** → **55 / 70**. *(K9-OOS is the binding low and an unresolved blocker.)*

### 4.2 T2 — Different cash-equity universe with stronger behavioral mean-reversion

| Field | Value |
|---|---|
| Mechanic family | mean-reversion (RSI/z-score) on a DIFFERENT universe |
| First-principles vs s14/s15 | **WEAK-MODERATE** — still the family that failed twice; only the universe changes; risk of repeating the failure unless the new universe is behaviorally different (higher-beta / more retail-driven names) |
| K9 reachability | clears (MR frequent) **if** the new universe behaves |
| DR10-v2 | clears |
| Data / fetch | **FETCH REQUIRED** (new universe; Tiingo) — friction; **blocks PLAN per bundle Step 3 (no fetch before PLAN)** |
| Reuse DR9 data | NO |

**T2 scoring:** first-principles **5** · K9 **8** · DR10-v2 **9** · data/fetch **4 (fetch)** · diversification **6** · complexity **6** · reuse-DR9 **2** → **40 / 70**. *(Fetch-gated + same exhausted family.)*

### 4.3 T3 — Sector / relative-strength rotation across ETFs or large-cap sectors

| Field | Value |
|---|---|
| Mechanic family | cross-sectional relative-strength / dual-momentum rotation (non-mean-reversion; low turnover) |
| First-principles vs s14/s15 | **MODERATE-STRONG** — genuinely different family; low turnover |
| K9 reachability | **WEAK** — rotation rebalances monthly/weekly → very few "trades"; K9-light (likely fails OOS ≥50/y) |
| DR10-v2 | clears (low turnover) |
| Data / fetch | **FETCH REQUIRED** (sector ETFs / broader large-cap set) — friction |
| Reuse DR9 data | NO (3 names insufficient for rotation breadth) |

**T3 scoring:** first-principles **7** · **K9 reachability 3** · DR10-v2 **9** · data/fetch **4 (fetch)** · diversification **8** · complexity **6** · reuse-DR9 **2** → **39 / 70**. *(K9-light + fetch.)*

### 4.4 T4 — Multi-instrument futures RSI / futures basket

| Field | Value |
|---|---|
| Mechanic family | futures basket (RSI or other) — multi-instrument |
| K9 reachability | clears (multi-instrument) |
| Data / fetch | **BLOCKED** — requires Databento fetch, which is gate-blocked on this machine (TLS/network; s14-d1-multi-instrument chain stalled at Databento). No fetch capability. |

**T4 status: BLOCKED** (no Databento fetch capability). Not scored; not selectable this round. Revisit only if Databento availability changes.

### 4.5 T5 — Pause / defer

Binary; not scored. Available if the operator prefers to pause the trading-bot track.

----

## 5. Score summary

| Track | Total | 1st-principles | K9 reach | DR10-v2 | data/fetch | diversif. | complexity | reuse-DR9 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **T1: trend/momentum on reuse universe** | **55 / 70** | 9 | **3** | 9 | 10 | 8 | 6 | 10 |
| T2: MR on different cash-equity universe | 40 / 70 | 5 | 8 | 9 | 4 | 6 | 6 | 2 |
| T3: sector/relative-strength rotation | 39 / 70 | 7 | 3 | 9 | 4 | 8 | 6 | 2 |
| T4: multi-instrument futures basket | BLOCKED | — | — | — | 0 | — | — | — |
| T5: defer | n/a | — | — | — | — | — | — | — |

----

## 6. Recommendation — direction vs clean-winner determination

**Best DIRECTION: T1** (trend/momentum on the reuse universe). It is the only track that is simultaneously zero-fetch, data-reuse, and a genuinely different (non-mean-reversion) mechanic family that directly tests the s14/s15 finding. It scores highest (55/70).

**BUT T1 is NOT a clear blocker-free winner.** Its K9-OOS reachability is a **structural blocker**: a daily trend/breakout on a 3-name basket cannot plausibly reach the ≥50 trades/year OOS K9 floor (trend round-trips are ~3-10/y per name; 3 names ≈ 6-24/y basket). Per the framework's K9-reachability discipline, a candidate expected to fail K9-OOS at PLAN time is predictable terminal work (T-FORBID-12-style waste). Resolving this requires a design decision the operator must make first:
- **(a)** commit to a higher-frequency non-MR mechanic and/or accept documenting the K9-OOS risk explicitly, OR
- **(b)** expand the universe (more names) to lift basket trade frequency — which requires a fresh fetch + DR9 audit.

The K9-clearing alternatives (T2 MR-different-universe, T3 rotation) **both require a data fetch before PLAN** and are therefore gated out of in-bundle PLAN authoring; T2 also re-uses the exhausted MR family. T4 is **blocked** (no Databento).

### Determination for Step 3 (conditional Tier-N PLAN)

**No track is a clear winner with no unresolved blocker.** T1 (the top score) carries an unresolved K9-OOS reachability blocker; the only K9-clearing options require a pre-PLAN fetch. Per the bundle rule ("If there is a tie or the top track requires data fetch before PLAN, do not author the Tier-N PLAN; stop after the selection plan and report the exact next authorization") and ("ambiguous top-track decision ⇒ HALT"), **this plan does NOT auto-author a Tier-N spec PLAN.** It stops here and reports the exact next-authorization options.

----

## 7. Exact next-authorization options (operator chooses; each separate)

1. **Pursue T1 (trend on reuse universe), resolving K9-OOS explicitly** — author the Tier-N PLAN with a higher-frequency trend/breakout design and an explicit K9-OOS-reachability table; operator accepts that if the PLAN-time table cannot show ≥50/y OOS, the candidate is K9-blocked:
   ```
   Authorize s16-d1 cross-sector cash-equity trend/breakout (reuse AAPL/JPM/XOM DR9 data) Tier-N spec PLAN only — bound by DR10 v2; PLAN must include a K9-OOS reachability table and is K9-blocked if it cannot show >=50 trades/y OOS.
   ```
2. **Pursue a K9-clearing universe (T2/T3)** — authorize the data fetch + DR9 audit first (PLAN cannot precede the fetch):
   ```
   Authorize s16-d1 <universe> availability probe + DR9 audit framework only.
   ```
3. **Defer:** `Defer / Pause trading-bot track.`

Recommended: **Option 1** if the operator wants to keep zero-fetch momentum and is comfortable that a 3-name daily trend may be K9-blocked (in which case the PLAN itself will surface the block honestly); **Option 2** if the operator wants a K9-robust track and accepts fetch friction.

----

## 8. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT/SEAL/BUILD/fetch/backtest/OOS) | met |
| No `_revN_`/patch of s15-d1 or s14-d1-cross-sector | met |
| No daily mean-reversion tweak on AAPL/JPM/XOM (T-FORBID-17) | met |
| No reuse of RSI(3)+2N or z-score exit-to-mean as a new candidate (T-FORBID-18) | met |
| No retroactive framework application to old candidates | met |
| No promotion of any prior candidate | met |
| No revival of s15/s14/s13/s12 | met |
| No modification of any sealed artifact | met |
| No data fetch / vendor API / network | met |
| **No Tier-N PLAN auto-authored (no clear blocker-free winner)** | met |
| `lessons.md` not modified by this plan (S15 lessons committed at fb805a1) | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |

----

## 9. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/next_research_track_selection_plan_after_s15_d1_cross_sector_terminal.md` | This selection plan (PLAN only; no JSON sidecar; no seal — planning document, per predecessor convention). |

No other repository file is modified.

----

End of selection plan. PLAN only. No code / backtest / fetch / DRAFT / SEAL / BUILD. **No Tier-N PLAN authored this turn — no clear blocker-free winner (T1 top-scored but K9-OOS-blocked; K9-clearing options require pre-PLAN fetch; T4 blocked).** Trading remains `PAUSED`. Live `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. s14/s15-d1-cross-sector terminals preserved verbatim.

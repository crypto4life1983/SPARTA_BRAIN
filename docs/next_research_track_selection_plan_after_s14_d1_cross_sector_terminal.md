# Next-research-track selection plan (after s14-d1-cross-sector terminal FAIL_SAFETY; under DR10 v2)

Status: **PLAN_ONLY** (no code written, no spec drafted, no spec sealed, no data fetched, no signal computation, no backtest, no OOS, no live; the next step is a separate operator authorization to author a Tier-N specification PLAN for the selected track).

Authored: 2026-05-28
Authorization phrase: `Authorize next research-track selection plan after s14-d1-cross-sector terminal FAIL_SAFETY only.`
Predecessor: rev2 at `docs/next_research_track_selection_plan_after_s13_d1_terminal_rev2_under_dr10_v2.md` (which co-recommended T1 multi-instrument micro-futures and T2 cash-equity 3-name basket). **T2 of that plan became `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history`, which is now TERMINAL (FAIL_SAFETY at P6 IS, P7 memo `6485ea9`).** This plan selects the next FRESH track informed by that terminal outcome.

Trigger event: s14-d1-cross-sector P7 decision memo `6485ea9` formalized `FAIL_SAFETY` (verdict-determining at P6 IS `7248a96`). Lessons committed to `brain_memory/projects/trading_bot/lessons.md` at `5085d2a` (LESSON_S14_D1_001/002/003).

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo / Tiingo / Databento call. No API-key access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No s14-d1-cross-sector / s13-d1 / s12-d1 revival.** **No `_revN_` or patch of s14-d1-cross-sector** (no re-tuning RSI(3) thresholds / 2N stop / universe). **No reinterpretation of any sealed candidate's verdict.** **No modification of any existing sealed artifact** (s14-d1-cross-sector SEAL `53cb804` / P1 `02b77d8` / P2 `27dbddc` / P3 `30fbc6a` / P4 `06bfcdb` / P6 IS `7248a96` / P7 `6485ea9`; all-tech sibling DRAFT `214bae0`; s14-d1 multi-instrument chain; s13-d1 / s12-d1 chains; `framework_dr10_revision_seal_v2` `78cd22e` — all byte-stable). No phase-2 safety contract template modification. No CLAUDE.md / `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging** (the S14-D1 lessons are already committed at `5085d2a`; this PLAN only cites them). No branch change. No git push. No live trading. No profitability claim. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

This plan evaluates FRESH candidates only. s14-d1-cross-sector's terminal status is binding and is NOT re-opened.

----

## 1. Context: what s14-d1-cross-sector proved

s14-d1-cross-sector was the strongest-scoring track in the rev2 plan (43/60, cleanest DR10 v2 + orthogonal universe). It cleared every structural gate that has historically been the binding low — and still failed:

| Gate / metric | rev1 binding low | rev2 binding low | s14-d1-cross-sector observed | Pass? |
|---|---|---|---|---|
| DR10 (turnover/cost) | **binding (v1 OR)** | permissive (v2 AND) | turnover 14.45 high but S2 cost_drag est ~2.1% < 5% → v2 AND does not fire | **CLEARED** |
| K9 OOS reachability | secondary | **binding** | 348 IS trades basket-summed (~70/y); ample | **CLEARED** (K9 satisfied) |
| DR9 data continuity | — | — | AAPL/JPM/XOM all 3 PASS (sealed `b13af03`) | **CLEARED** |
| A7 / K10 diversification | — | — | A7 2.09, K10 0.4529 — both inside SEAL expected bands | **CLEARED** |
| K6 dispersion | — | — | no single-symbol >70% concentration | **CLEARED** |
| **K1 sharpe_proxy / K2 expectancy** | not the binding low | not the binding low | **sharpe_proxy/trade −0.1119; expectancy −$39.53/trade; net −$13,754.96** | **FAILED → FAIL_SAFETY** |

### 1.1 The new binding low: exit/stop edge design

Every structural and diversification gate passed. The candidate failed on **per-trade edge** (K1/K2). Root cause (LESSON_S14_D1_002): the RSI(3) bi-directional entry was paired with a **hard 2N ATR stop**, which is structurally adversarial to the mean-reversion premise — winners exit small at the RSI 55/45 mid-band, losers run to the full 2N stop. Result: 54.31% win rate with negative expectancy (profit/loss ratio < 1).

**Therefore the binding scoring axis for this plan is `exit/stop first-principles edge design`** — does the candidate's exit/stop geometry align with (rather than truncate) its entry thesis? This axis is upstream of K9/DR9/DR10/A7 in practical importance, because s14-d1-cross-sector demonstrated those can all pass while a mis-designed exit/stop still produces FAIL_SAFETY.

----

## 2. Lessons from s14-d1-cross-sector carried into this plan (committed at `5085d2a`)

| # | Lesson | Source | Implication for next track |
|---|---|---|---|
| L1 | Cross-sector diversification can improve A7/K10 without creating edge | LESSON_S14_D1_001 | Hold the proven-diversified universe constant; do NOT spend the next candidate "fixing" diversification — it was never broken |
| L2 | RSI(3) + 2N ATR hard stop → >50% win rate but negative expectancy | LESSON_S14_D1_002 | The 2N hard stop is the falsified component; the next track must NOT pair a tight hard stop with a mean-reversion entry |
| L3 | Mean-reversion candidates need exit/stop design tested from first principles before SEAL | LESSON_S14_D1_003 | Exit/stop edge viability is the primary selection axis; justify it at PLAN time, not after P6 |
| L4 | K9 / DR9 / DR10-v2 / A7 / K10 all passed yet candidate failed | s14-d1 P6 IS `7248a96` | Structural-gate clearance is necessary-but-not-sufficient; do not over-weight gates that s14-d1 already showed are non-binding here |
| L5 | Favorable readings on one axis do not rescue a failure on another (carries B006_002_002 + S14_D1_001) | committed lessons | Score the edge axis independently; a clean A7/K10 is not a partial pass |

----

## 3. Reachability disciplines (carried; K9 + DR9 + DR10-v2)

### 3.1 K9-reachability (binding)

| Window | Length (y) | Required trades/y for K9=100 (basket-summed) |
|---|---:|---|
| IS (2019-01-02 → 2023-12-29) | ~5.0 | ≥ 20 |
| **OOS (2024-01-02 → 2025-12-30)** | **~2.0** | **≥ 50 (BINDING)** |

s14-d1-cross-sector cleared this comfortably (~70/y). Any mean-reversion mechanic on a 3-name daily basket at comparable signal density also clears; **K9 is NOT expected to be the binding low for this plan** (it was rev2's binding low; it is now subordinate to exit/stop edge design).

### 3.2 DR9 data continuity (reuse vs fresh)

The AAPL/JPM/XOM `split_only` CSVs are **already DR9-PASSED and sealed** (`b13af03`, result_seal `a8ff9126…`). A fresh MECHANIC on the **same universe** therefore has **zero data-scope friction and DR9 already satisfied**. A new universe requires a fresh availability probe + DR9 audit (operator-side fetch).

### 3.3 DR10-v2-reachability (AND-conjunction; permissive for cash equity)

Cash-equity per-share commissions keep S2 cost_drag far below 5% (s14-d1 observed ~2.1%), so DR10 v2 does not fire regardless of turnover. **DR10 v2 is not expected to be the binding low for any cash-equity mean-reversion track here.**

----

## 4. Forbidden tracks (carry T-FORBID-1..12; this plan ADDS T-FORBID-13..15)

All prior forbidden tracks carry. New forbidden tracks from the s14-d1-cross-sector terminal:

- **T-FORBID-13**: Re-attempt RSI(3) bi-directional + hard 2N ATR stop on a cash-equity basket = s14-d1-cross-sector territory.
- **T-FORBID-14**: Any `_revN_` / parameter-patch of s14-d1-cross-sector (re-tuning RSI(3) thresholds 15/55/85/45, ATR(14), 2N multiplier, 0.5% risk, $100k cash, AAPL/JPM/XOM universe) while keeping the same mechanic+stop structure. The failure was the **mechanic/stop geometry**, not a parameter that iteration would fix.
- **T-FORBID-15** (the load-bearing new one): Any mean-reversion candidate that pairs the entry with a **hard ATR stop tighter than the expected reversion horizon** WITHOUT a first-principles exit/stop justification at PLAN time = predictable repeat of the s14-d1 FAIL_SAFETY = framework waste.

**Note on the all-tech sibling DRAFT (`214bae0`):** the `{AAPL, MSFT, NVDA}` all-tech sibling uses the **same RSI(3) + 2N stop mechanic** as s14-d1-cross-sector. By LESSON_S14_D1_002, advancing it would very likely **reproduce the same negative-expectancy FAIL_SAFETY** (the failure was the mechanic, not the basket; an all-tech basket is *less* diversified than cross-sector, so no improvement is expected). It is preserved byte-stable and is **not recommended for advancement** under this plan. Advancing it would be a separate operator decision and is effectively T-FORBID-15-adjacent.

----

## 5. Track candidates (scored on the new exit/stop-edge-design axis)

Scoring axes (each /10): **Exit/stop first-principles edge design (PRIMARY/load-bearing)**, K9-OOS reachability, DR9 / data-scope friction, DR10-v2 reachability, first-principles burden vs forbidden tracks, lifecycle complexity, K9-IS reachability. Total /70.

### 5.1 Track T1 — Non-RSI z-score / Bollinger mean-reversion, **exit-to-mean**, vol-scaled (not fixed-2N) stop, on the DR9-passed AAPL/JPM/XOM universe

| Field | Value |
|---|---|
| Candidate id (placeholder; assigned at next PLAN turn) | e.g., `s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean` |
| Mechanic family | **NON-RSI** (F-new): z-score / Bollinger-band mean-reversion. Entry when close < lower band (z ≤ −k, k~2.0-2.5) long / > upper band short. **Exit when price re-crosses the moving mean (the band midline) — i.e., the exit IS the reversion target by construction.** Stop = volatility-scaled disaster brake (e.g., z ≤ −4 or N×realized-vol), NOT a fixed 2N that truncates. |
| Universe | `{AAPL, JPM, XOM}` — **reuse DR9-PASSED sealed CSVs** (`b13af03`); zero fetch |
| Sizing | DA3=B (0.5% risk/name); $100k shared account; portfolio cap 3 (carry the proven safe-contract structure) |
| Exit/stop first-principles | **The exit equals the thesis**: a mean-reversion trade should close when the mean is recovered, not at an arbitrary RSI threshold; the stop is a wide vol-scaled catastrophe brake, not a primary exit. This directly removes BOTH s14-d1 failure components (arbitrary RSI-mid exit + tight 2N stop). |
| First-principles burden vs s14-d1-cross-sector | NON-RSI mechanic family (z-score vs RSI(3)); exit-to-mean vs RSI-threshold; vol-scaled-catastrophe stop vs fixed-2N. Same universe held constant **deliberately, to isolate the exit/stop variable** (clean experimental design, NOT a patch). |

**K9 (basket, 3 names):** z|2| daily mean-reversion ~ 20-35/y per name → 60-105/y basket → IS ✅ (≥20), OOS ✅ (≥50). **DR10 v2:** cost_drag << 5% (cash equity) → CLEARS. **DR9:** already PASSED (reuse).

**Pros:** zero data-scope friction (DR9 done); exit==thesis (the cleanest fix to the falsified component); genuinely fresh non-RSI mechanic; holds the proven-diversified universe constant to isolate the fix; K9/DR9/DR10 all known-favorable.
**Cons:** band/z parameters and the vol-scaled stop must be first-principles justified at SEAL (NOT grid-searched — `no_strategy_optimization_authorized`); "exit-to-mean" can produce occasional long holds (time-stop fallback advisable).

**T1 scoring:** Exit/stop design **9** · K9-OOS **8** · DR9/data-friction **10** (reuse) · DR10-v2 **9** · first-principles burden **9** · lifecycle complexity **6** · K9-IS **8** → **59 / 70**.

### 5.2 Track T2 — RSI(2) mean-reversion with **time-based (max-hold) exit** + catastrophic-only stop (no hard 2N), AAPL/JPM/XOM (reuse data)

| Field | Value |
|---|---|
| Candidate id (placeholder) | e.g., `s15-d1-aapl-jpm-xom-cash-equity-rsi-2-time-exit-no-hard-stop` |
| Mechanic | RSI(2) entry (oversold/overbought); **exit on max-hold of N bars (time-based) OR RSI mid-cross, whichever first**; stop = wide catastrophe brake only (e.g., 4-5N), never the primary exit |
| Universe | `{AAPL, JPM, XOM}` — reuse DR9-PASSED CSVs |
| Exit/stop first-principles | A time-based exit **gives the reversion time to play out** rather than truncating it; the wide catastrophe stop caps tail risk without being hit in normal reversion. Directly addresses LESSON_S14_D1_002/003. |
| First-principles burden | Different RSI period (2 vs s14-d1's 3); **fundamentally different exit/stop** (time-based + catastrophe-only vs RSI-mid + 2N). Fresh mechanic structure, not a `_revN_`. Must clear T-FORBID-13/14/15 (it does: no hard 2N stop). |

**K9:** RSI(2) is higher-frequency than RSI(3) → strongly clears IS and OOS. **DR10 v2:** CLEARS. **DR9:** PASSED (reuse).

**Pros:** zero data friction; keeps a familiar entry while fixing the falsified exit/stop; time-based exit is simple and well-understood; K9 very strong.
**Cons:** RSI lineage is close to s13-d1/s14-d1 territory — first-principles burden must lean on the exit/stop redesign as the differentiator (it is structurally new); max-hold N must be justified from the reversion horizon, not tuned.

**T2 scoring:** Exit/stop design **8** · K9-OOS **9** · DR9/data-friction **10** · DR10-v2 **9** · first-principles burden **7** (RSI-adjacent) · lifecycle complexity **7** · K9-IS **9** → **59 / 70**.

### 5.3 Track T3 — Profit-target / stop **asymmetry** mean-reversion (CRITICALLY EVALUATED)

| Field | Value |
|---|---|
| Mechanic | RSI or z-score entry; fixed profit target + fixed stop with deliberate asymmetry |
| Exit/stop first-principles | **CAUTION:** the s14-d1 failure WAS effectively an asymmetry in the wrong direction (small target via RSI-mid + wide 2N stop = target < stop). A viable asymmetry for mean-reversion must ensure `win_rate × avg_win > loss_rate × avg_loss`. Naive "small target, wide stop" replicates the s14-d1 trap. |

**Assessment:** This option (from the operator menu) is **only viable with explicit first-principles calibration** showing the payoff geometry is net-positive — which cannot be asserted at PLAN time without the very edge analysis the SEAL must precommit. Higher risk of re-failing K1/K2. Recommended ONLY if folded into T1/T2 as a calibrated component, not as a standalone track.

**T3 scoring:** Exit/stop design **5** (trap-adjacent) · K9-OOS **8** · DR9/data-friction **10** · DR10-v2 **9** · first-principles burden **5** · lifecycle complexity **7** · K9-IS **8** → **52 / 70**.

### 5.4 Track T4 — Trend / breakout pivot with trailing stop (non-mean-reversion), cross-sector basket

| Field | Value |
|---|---|
| Mechanic | Donchian / MA-cross breakout; **trailing ATR stop** (let winners run, cut losers) — opposite exit geometry to mean-reversion |
| Universe | `{AAPL, JPM, XOM}` reuse, or a precommitted trend-suitable basket |
| Exit/stop first-principles | Trend mechanics WANT a trailing stop (the stop IS the exit, aligned with "ride the trend"); no truncation problem. A genuinely different thesis from the failed mean-reversion family. |

**K9 RISK:** daily-bar trend/breakout on 3 names is **low frequency** (~6-15/y basket) → **OOS K9 likely FAILS** (need ≥50/y). This is the rev2-style K9-OOS binding low resurfacing for low-frequency mechanics.

**T4 scoring:** Exit/stop design **8** · **K9-OOS 3 (likely fails)** · DR9/data-friction **9** · DR10-v2 **9** · first-principles burden **8** · lifecycle complexity **7** · K9-IS **4** → **48 / 70**.

### 5.5 Track T5 — Defer / pause

Binary; not scored. Available if the operator wants to pause the trading-bot track after this analysis.

----

## 6. Score summary

| Track | Total | Exit/stop design (PRIMARY) | K9-OOS | DR9/data | DR10-v2 | 1st-principles | Complexity | K9-IS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **T1: Non-RSI z-score exit-to-mean, vol-scaled stop, AAPL/JPM/XOM reuse** | **59 / 70** | **9** | 8 | 10 | 9 | 9 | 6 | 8 |
| **T2: RSI(2) time-based exit + catastrophe-only stop, AAPL/JPM/XOM reuse** | **59 / 70** | 8 | 9 | 10 | 9 | 7 | 7 | 9 |
| T3: Profit-target/stop asymmetry (critically evaluated) | 52 / 70 | 5 | 8 | 10 | 9 | 5 | 7 | 8 |
| T4: Trend/breakout + trailing stop (non-mean-reversion) | 48 / 70 | 8 | 3 | 9 | 9 | 8 | 7 | 4 |
| T5: Defer | n/a | — | — | — | — | — | — | — |

**Key shift from rev2:** rev2's binding low was K9-OOS; this plan's binding low is **exit/stop first-principles edge design**. The top two tracks both hold the proven AAPL/JPM/XOM universe constant (zero data friction, DR9/K9/DR10 already favorable) and change ONLY the exit/stop mechanic — the variable s14-d1 falsified. This is deliberate experimental hygiene: fix the one thing that failed, hold everything that passed.

----

## 7. Recommendation

### Strongest single track: **T1 — Non-RSI z-score/Bollinger mean-reversion with exit-to-mean + vol-scaled stop, on the DR9-passed AAPL/JPM/XOM universe (59/70).**

Rationale: it most directly embodies LESSON_S14_D1_002/003. The **exit equals the reversion thesis** (close when the mean recovers) and the **stop is a wide vol-scaled catastrophe brake** rather than a fixed 2N that truncates — removing BOTH falsified components in one structural change. It is a genuinely fresh **non-RSI** mechanic (orthogonal to the s13/s14 RSI lineage), and by reusing the already-DR9-passed cross-sector CSVs it has **zero data-scope friction** while **holding the proven-diversified universe constant** so the next experiment isolates exactly the variable that failed.

### Co-strong runner-up: **T2 — RSI(2) with time-based exit + catastrophe-only stop (59/70).**

Tied on total; choose T2 if the operator prefers staying within a familiar RSI entry while still fixing the exit/stop. Its only deduction vs T1 is first-principles burden (RSI-adjacent to s13/s14), offset by a stronger K9 margin.

### Conditional: T3 (asymmetry) — only as a calibrated component of T1/T2, not standalone (re-failure risk).
### Not recommended now: T4 (trend) — likely fails K9-OOS at daily-bar frequency on 3 names.
### Do NOT advance the all-tech sibling DRAFT `214bae0` — same RSI(3)+2N mechanic; expected to reproduce the FAIL_SAFETY.
### Defer: T5.

----

## 8. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT / SEAL / BUILD / fetch / backtest / OOS) | met |
| No strategy code / simulator / signal computation | met |
| No data fetch / vendor API / API-key access / network IO | met |
| No live trading / paper / broker / Strategy Lab / candidate promotion | met |
| **No s14-d1-cross-sector `_revN_` or patch** | met |
| **No s14-d1-cross-sector / s13-d1 / s12-d1 / parked revival** | met |
| **No modification of any sealed artifact** (s14-d1-cross-sector SEAL/P1/P2/P3/P4/P6/P7 + all-tech DRAFT 214bae0 + multi-instrument + s13/s12 chains + DR10 v2 78cd22e byte-stable) | met |
| No reinterpretation of any sealed verdict | met |
| No phase-2 safety contract template / CLAUDE.md / .gitignore modification | met |
| **No `brain_memory/projects/trading_bot/lessons.md` modification or staging** (S14-D1 lessons already committed at 5085d2a; cited only) | met |
| No `review_queue` / `idea_memory` mutation | met |
| No profitability claim | met |
| Trading `PAUSED` · Live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` | met |
| `no_strategy_optimization_authorized` / `no_dr_redefinition_post_seal` | TRUE |
| K9-reachability + DR9 + DR10-v2-reachability disciplines | binding (carried) |
| T-FORBID-1..15 forbidden tracks | carried (13/14/15 added this turn) |

----

## 9. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/next_research_track_selection_plan_after_s14_d1_cross_sector_terminal.md` | This selection plan (PLAN only; no JSON sidecar; no canonical seal — a planning document, not a sealed Tier-N/framework artifact, consistent with the rev2 predecessor convention). |

No other repository file is modified.

----

## 10. Next-step authorization scope

### Primary (strongest; non-RSI exit-to-mean; zero data friction)

```
Authorize s15-d1 cross-sector cash-equity z-score mean-reversion exit-to-mean Tier-N spec PLAN only — bound by DR10 v2.
```

Authors the Tier-N spec PLAN for a fresh candidate per T1: z-score/Bollinger entry, **exit-to-mean**, vol-scaled catastrophe stop, on the DR9-passed AAPL/JPM/XOM universe (reuse). PLAN must include a first-principles exit/stop-edge-design section (the new binding axis) and DR10-v2 + K9 reachability tables. PLAN-only; no DRAFT/SEAL/BUILD until separately authorized.

### Co-strong runner-up (RSI(2) time-based exit; zero data friction)

```
Authorize s15-d1 cross-sector cash-equity RSI-2 time-based-exit no-hard-stop Tier-N spec PLAN only — bound by DR10 v2.
```

Authors the Tier-N spec PLAN for a fresh candidate per T2.

### Alternative analysis

```
Authorize alternative next-track selection plan rev2 only.
```

If the operator rejects T1/T2 and wants a different analysis (e.g., a track not enumerated here, or a cross-domain pivot).

### Pause without advancing

```
Defer / Pause trading-bot track.
```

----

## 11. Carried-forward status (UNCHANGED across this PLAN turn)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` applies to any future candidate descended from this plan | TRUE |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` | TRUE |
| s14-d1-cross-sector lifecycle terminal (FAIL_SAFETY; P7 `6485ea9`) | TRUE — preserved verbatim |
| all-tech sibling DRAFT `214bae0` | preserved byte-stable; NOT recommended for advancement (same RSI(3)+2N mechanic) |
| s14-d1 multi-instrument / s13-d1 / s12-d1 / earlier chains byte-stable | TRUE — preserved |
| LESSON_S14_D1_001/002/003 committed at `5085d2a` | TRUE — cited, not modified |
| K9-reachability + DR9 + DR10-v2-reachability disciplines | binding |
| framework_dr10_revision_seal_v2 `78cd22e` | binding for s15+ new SEAL turns |

----

End of selection plan. PLAN-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No vendor API. No QC/LEAN. No brokerage. No real/paper order. No Strategy Lab promotion. No `review_queue` / `idea_memory` mutation. **No s14-d1-cross-sector `_revN_`/patch. No revival of any terminal/parked candidate. No `lessons.md` modification or staging. No modification of any sealed artifact.** No live trading. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. s14-d1-cross-sector lifecycle terminal preserved verbatim.

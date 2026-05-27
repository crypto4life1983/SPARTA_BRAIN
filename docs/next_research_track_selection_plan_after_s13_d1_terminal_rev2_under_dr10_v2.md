# Next-research-track selection plan rev2 (after s13-d1 terminal; under DR10 v2 AND-conjunction)

Status: **PLAN_ONLY** (no code written, no spec drafted, no spec sealed, no data fetched, no signal computation, no backtest, no OOS, no live; the next step is a separate operator authorization to author a Tier-N specification PLAN for the selected track).

Authored: 2026-05-27
Authorization phrase: `Authorize alternative next-track selection plan rev2 only.`
Supersedes: rev1 at commit `30c836e` (`docs/next_research_track_selection_plan_after_s13_d1_terminal.md`). Rev2 re-scores candidates under the newly sealed DR10 v2 AND-conjunction framework.

Trigger event for rev2: framework-level DR10 SEAL revision v2 sealed at commit `78cd22e` (`reports/framework_dr10_revision_seal_v2.json`, `report_seal_sha256` `7794bb5222ed2a2cb1cd8e1ef2f43f3d1abc6f1539d71af31dda32d832b5e907`). The OR connective in DR10 v1 became AND in DR10 v2; both thresholds preserved verbatim (0.50 turnover; 0.05 cost_drag). DR10 v2 binds new candidate `candidate_record_id`s from s14+ onward.

----

## HARD BOUNDARIES (held by this rev2 PLAN)

PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No `DATABENTO_API_KEY` access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No s13-d1 / s12-d1 revival.** **No retroactive application of DR10 v2 to any existing sealed candidate.** **No reinterpretation of any existing sealed candidate's verdict.** **No modification of any existing sealed candidate artifact** (s11-d1 / s12-d1 / s13-d1 SEAL/P1/P2/P3/P4/P6/P6.5/P7 + framework_dr10_revision_seal_v2 all byte-stable). No phase-2 safety contract template modification. No CLAUDE.md modification. No `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No branch change. No git push. No live trading. No profitability claim. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

Rev2 evaluates FRESH s14+ candidates only. Existing sealed candidates are NOT re-evaluated; their terminal/parked statuses remain binding under their original SEAL-time DR10 versions.

----

## 1. Context: what's changed since rev1

| Field | rev1 (under DR10 v1; commit 30c836e) | rev2 (under DR10 v2; commit 78cd22e onward) |
|---|---|---|
| DR10 definition | `turnover>0.50 OR cost_drag>0.05 -> REJECT_FAST` | `(turnover>0.50 AND cost_drag>0.05) -> REJECT_FAST` |
| Connective | OR (disjunctive) | **AND (conjunctive)** |
| Thresholds | 0.50 turnover; 0.05 cost_drag | 0.50; 0.05 (preserved verbatim) |
| Binding scope | s11-d1 / s12-d1 / s13-d1 lineage (and pre-v2 candidates) | NEW SEAL turns from s14+ onward only |
| Existing candidates re-evaluated under v2? | -- | **NO** (per `no_dr_redefinition_post_seal=True`; v1 verdicts immutable) |
| s13-d1 terminal status | terminal REJECT_FAST under v1 | terminal REJECT_FAST under v1 (UNCHANGED; v2 does NOT promote) |
| Active-trading candidates at retail-scale start_cash | structurally rejected by v1 OR turnover branch | **structurally admissible under v2** if S2 cost_drag is managed below 5% |

### 1.1 Why the candidate space opens up under v2

Under DR10 v1 OR-disjunctive: any candidate with high turnover (which is intrinsic to micro-futures contract-quantization at retail scale; see investigation PLAN §4) fires DR10 alone regardless of cost. Result: all five rev1 candidates T1-T5 failed DR10 reachability at PLAN time.

Under DR10 v2 AND-conjunctive: a candidate fires DR10 only if BOTH branches fire. Most realistic strategies have S2 cost_drag well below 5% (s13-d1 observed 2.35% at S2 with DA4=C $200k start_cash; even at default $100k it would be ~4.7% — still close to but below 5%). The cost_drag branch is structurally easier to clear than the turnover branch at retail scale. Therefore: **most candidates that previously failed v1 because of turnover alone now clear v2 by virtue of the cost_drag branch not firing.**

### 1.2 What's NOT changed under v2

- K9 inviolate ≥ 100 trades (unchanged; OOS K9 ≥ 50 trades/y binding per K9-reachability discipline)
- K9-reachability discipline (binding for all PLAN-time work)
- DR10-reachability discipline (binding; under v2 evaluated as AND-conjunction)
- DR precedence chain `DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5` (unchanged; DR10 retains position 4)
- Other DR rules DR1/DR2/DR3/DR4/DR5/DR6/DR7/DR9 (unchanged)
- K-gates K1/K2/K4/K7/K8/K9/K12 (unchanged)
- C1-C8 phase-2 safety contracts (unchanged)
- All T-FORBID-1..12 forbidden tracks from rev1 (carry; see §4)
- s13-d1 / s12-d1 / earlier lifecycle terminals (preserved verbatim)

### 1.3 Implication: K9 OOS becomes the binding low scoreable criterion

In rev1, DR10 reachability was the binding low criterion (all T1-T5 scored 2-3/10 on DR10). In rev2, DR10 reachability under v2 is permissive for cost-managed strategies; the binding low criterion is now **K9 reachability at OOS** (≥ 50 trades/y over the 2.0y OOS window). Candidates that produce ≥ 50 trades/y on average across the full diagnostic window are admissible; those below it remain K9-blocked.

----

## 2. Lessons from s13-d1 carried into rev2 (NOT written to lessons.md)

These lessons are PLAN-time framework context. They are NOT written to `brain_memory/projects/trading_bot/lessons.md` by this PLAN; that requires separate authorization. (LESSON_S13_D1_001/002/003 from s13-d1 P7 memo §4 remain eligible-but-not-written.)

| # | Lesson | Source | Status under v2 |
|---|---|---|---|
| L1 | DR10's OR-disjunctive structure (v1) made turnover branch load-bearing alone; AND-conjunctive (v2) removes this | s13-d1 P6.5 + framework_dr10_revision_seal_v2 §1-§6 | RESOLVED at framework level (v2 sealed at 78cd22e) |
| L2 | Contract-quantization at retail-scale start_cash forces per-trade notional ≥ 15% of start_cash for micro-futures | s13-d1 + DR10 investigation PLAN §4 | UNCHANGED (still structural); but cost_drag branch is now what binds DR10 v2, not turnover |
| L3 | K9 trade-count clearance + positive A-gates are necessary but not sufficient; DR precedence is upstream | s13-d1 P6.5 + P7 | UNCHANGED |
| L4 | Favorable economics do NOT override fail-closed verdicts (LESSON_B006_002_002 reinforced) | s13-d1 P7 §3 | UNCHANGED |
| L5 | s13-d1's 84.79 turnover + 2.35% cost_drag would have CLEARED DR10 v2 (AND-conjunction); under v1 it fired the turnover branch alone. **This is INFORMATIONAL ONLY; s13-d1 verdict remains terminal under v1.** | framework_dr10_revision_seal_v2 §7 | INFORMATIONAL; does NOT affect s13-d1 status |
| L6 | K9-reachability discipline (introduced post-s12-d1) binds at PLAN time | rev1 plan §3 | UNCHANGED; binding |
| L7 | DR10-reachability discipline (introduced post-s13-d1 rev1) now evaluated against v2 AND-conjunction at PLAN time | rev1 plan §3 + v2 SEAL §8 | UPDATED for v2 |
| L8 | Path B (new candidate) and Path C (framework-level SEAL revision) were the only non-pause forward paths under v1; Path C executed (DR10 v2 at 78cd22e); Path B now under reconsideration in rev2 | s13-d1 P7 §5 + rev1 plan §10 + v2 SEAL §8 | Path C COMPLETED; Path B reopened with new scoring |

----

## 3. K9-reachability + DR10-reachability disciplines (v2-updated)

### 3.1 K9-reachability (unchanged from rev1; binding)

| Window | Length (y) | Required trades/y for K9=100 |
|---|---:|---|
| IS | ~4.6 | ≥ 21.74 |
| **OOS** | **2.0** | **≥ 50.00** (BINDING) |

For rev2 scoring, **K9 OOS reachability is the load-bearing structural constraint** that distinguishes admissible candidates from K9-blocked candidates.

### 3.2 DR10-reachability under v2 AND-conjunction (UPDATED)

Every Tier-N spec PLAN authored under v2 binding (s14+) shall include an explicit PLAN-time DR10-v2-reachability table:

| Field | Computation |
|---|---|
| Expected per-trade notional ($) | (units per trade) × (price per unit) × (dollar-per-unit multiplier) |
| Expected trades per year | from mechanic + universe signal density |
| Expected total round-trip notional/year | per-trade notional × trades/year × 2 |
| start_cash ($) | from DA4 |
| Expected annual_turnover | total_notional_per_year / start_cash |
| **Expected S2 cost_drag** | (commissions + fees + slippage) × cost_scalar=1.5 / start_cash (analogous to s13-d1's 2.35%) |
| **DR10 v2 status** | `CLEARS` if (turnover ≤ 0.50 OR cost_drag ≤ 0.05); `FAILS` only if BOTH branches fire |

Under v2, DR10 reachability is dominated by the cost_drag branch (the easier-to-clear branch). Candidates with cost-managed S2 cost_drag below 5% clear v2 regardless of turnover.

----

## 4. Forbidden tracks (T-FORBID-1..12 carry from rev1; rev2 adds none)

All 12 forbidden tracks from rev1 (commit 30c836e) carry verbatim into rev2:

- T-FORBID-1..8: carried from prior selection plans (s12-d1, s10-d1, s9, s7-d1, B005/B006/T8, NKE)
- T-FORBID-9: re-attempt RSI(2) bi-directional MNQ.c.0 with DA3=B + DA4=C = s13-d1 territory
- T-FORBID-10: any `_revN_` revision of s13-d1 RSI thresholds / ATR / risk_pct / START_CASH / warmup / cost-stress tiers
- T-FORBID-11: DR10 threshold reinterpretation within s11/s12/s13-lineage definition (resolved at framework level via DR10 v2 SEAL; the `0.50` and `0.05` thresholds themselves remain immutable under v2)
- T-FORBID-12: candidates that adopt s13-lineage DR10 by-reference but are structurally expected to fail DR10 at PLAN time = framework waste. **Under v2 this becomes: candidates that fail BOTH turnover ≤ 0.50 AND cost_drag ≤ 0.05 at PLAN time** (i.e., would fire v2 AND-conjunction at PLAN time).

Alternative tracks below are authored such that they satisfy first-principles burden against each forbidden track AND have a PLAN-time DR10-v2-reachability table showing `CLEARS` (the easier criterion under AND-conjunction).

----

## 5. Track candidates under DR10 v2 scoring

### 5.1 Track T1 (rev2) — Multi-instrument RSI(2) bi-directional micro-futures basket

| Field | Value |
|---|---|
| Candidate id (placeholder; assigned at next PLAN turn) | e.g., `s14-d1-mnq-mes-mym-m2k-multi-instrument-rsi-2-bi-directional-databento-long-history` |
| Mechanic family | F3 (RSI mean-reversion; same family as s13-d1 but applied to MULTIPLE instruments with per-instrument independent signal generation; ORTHOGONAL universe vs s13-d1's single-instrument scope) |
| Mechanic detail (PLAN-time placeholder) | Connors RSI(2) bi-directional thresholds 10/50/90/50 per instrument; per-instrument max 1 unit; portfolio cap from K11-style aggregation |
| Universe | `{MNQ.c.0, MES.c.0, MYM.c.0, M2K.c.0}` (4 equity-index micros; NOT in s10-d1 MNQ+MGC pairing, NOT in s12-d1 single MNQ scope) |
| Asset class | micro-futures basket |
| Sizing | DA3=B (0.5% per-trade risk; carry-over from s13-d1 SEAL as a PROVEN-effective cost_drag mitigation; admissible in fresh candidate); DA4=B ($100k cash; **different from s13-d1's DA4=C $200k**, making this NOT s13-d1 territory under T-FORBID-9/10) |
| Cost surface | per-contract commission + tick-slippage; identical structure to s13-d1; expected S2 cost_drag ~ 2-4% (s13-d1 was 2.35% at $200k; at $100k roughly 2x = ~4.7% — close to 5%, borderline) |
| Data scope | MNQ.c.0 reuses sealed CSV; **MES, MYM, M2K require fresh Databento fetch + new DR9-audit phase (operator-side)** |
| First-principles burden vs s13-d1 | ORTHOGONAL universe (multi-instrument vs single); ORTHOGONAL DA4 ($100k vs $200k); same mechanic family F3; same RSI thresholds — fresh candidate, NOT _revN_ |
| First-principles burden vs s10-d1 | s10-d1 was MNQ+MGC (failed DR9 on MGC); T1 (rev2) is 4 equity-index micros (no MGC); no overlap |
| First-principles burden vs s10-d2 | s10-d2 was Donchian-55/20 on 4 different markets at $500k cash; T1 (rev2) is RSI(2) on 4 equity-index micros at $100k cash; orthogonal mechanic + sizing |

**K9-reachability table:**

| Window | Length (y) | Required trades/y for K9 | Expected RSI(2) trades/y per instrument | 4-instrument portfolio expected | K9 status |
|---|---:|---|---|---|---|
| IS | ~4.6 | ≥ 21.74 | ~34/y (s13-d1 baseline on MNQ) | 4 × 34 = ~136/y | **CLEARS with strong margin** (136 >> 21.74) |
| **OOS** | **2.0** | **≥ 50.00** | ~34/y per instrument | 4 × 34 = ~136/y | **CLEARS with strong margin** (136 >> 50) |

**DR10-v2-reachability table:**

| Sizing assumption | Per-trade notional | Trades/y | annual_turnover | S2 cost_drag est. | DR10 v2 status |
|---|---|---|---|---|---|
| 0.5% risk per trade per instrument; ~5-15 contracts per trade; $100k start cash | $80-150k per trade avg | 136 | ~30-50 (high; turnover branch fires) | ~3-5% (borderline; depends on MES/MYM/M2K commission structure) | **CLEARS** (AND fails if cost_drag < 5%; need to confirm at SEAL time the cost surface keeps S2 below 5%) |
| 0.25% risk per trade (more conservative) | $40-75k per trade | 136 | ~15-25 | ~1.5-3% | **CLEARS** with margin |

**Pros:**
- **Only track that clears K9 at BOTH IS and OOS with strong margin** (136 trades/y >> 50/y floor)
- Reuses s13-d1's proven-profitable RSI(2) mechanic on a different (multi-instrument) universe
- ORTHOGONAL to s13-d1 SCOPE (single vs multi); legitimately fresh candidate
- DR10 v2 status: CLEARS via cost_drag branch (under v2 AND-conjunction, cost_drag < 5% is sufficient; needs SEAL-time confirmation at chosen DA4)
- C1-C8 phase-2 safety contracts carry by-reference from s13-d1 P2

**Cons:**
- Requires fresh availability probe + new DR9 audit for MES, MYM, M2K (operator-side Databento fetch; potentially fresh sealed CSVs)
- Per-instrument concentration risk (s7-D1 USO lesson; K11-style portfolio cap needed at SEAL)
- Cost surface for the additional micros not yet calibrated; at DA4=B ($100k) S2 cost_drag may be borderline 5%
- DA4=B at $100k start_cash means total turnover at K9-clearing rate is high (~30-50); under v2 this only matters if cost_drag also fires

**T1 (rev2) scoring under v2:**

| Criterion | Score (/10) | Note |
|---|---:|---|
| K9 reachability at IS | 9 | 136/y >> 21.74/y |
| **K9 reachability at OOS (binding low under v2)** | **9** | 136/y >> 50/y; strong margin |
| DR10 v2 reachability | 7 | Clears via cost_drag branch; borderline if MES/MYM/M2K cost surface is unfavorable; SEAL-time precommit reduces this risk |
| First-principles burden vs predecessors | 8 | Orthogonal universe + DA4; same mechanic family is OK (different scope) |
| Data scope friction | 4 | MES/MYM/M2K availability probe + DR9 audit + fresh fetch required |
| Lifecycle complexity | 6 | Multi-symbol coordination + per-market caps + portfolio-level A7 |
| **Total** | **43 / 60** | K9 + DR10 both pass with strong margin; data scope is the main friction |

----

### 5.2 Track T2 (rev2) — Cash-equity 3-name basket RSI(3) bi-directional at standard sizing

| Field | Value |
|---|---|
| Candidate id (placeholder) | e.g., `s14-d1-aapl-msft-nvda-cash-equity-rsi-3-bi-directional` |
| Mechanic family | F3-adjacent (RSI(3) mean-reversion; slower period than s13-d1's RSI(2); bi-directional) |
| Mechanic detail | RSI(3) thresholds 15/55/85/45 (slower entry; tighter exit); per-name max 1 position; portfolio-level cap |
| Universe | precommitted 3-name basket NOT in s7-D1/s9 (e.g., `{AAPL, MSFT, NVDA}` from large-cap tech with low pairwise correlation; OR a precommitted shortlist authored at SEAL time) |
| Asset class | cash equity (US large-cap) |
| Sizing | DA3=B (0.5% risk per trade; **standard sizing — nano-sizing is no longer required under v2**) |
| Cost surface | per-share commission ~$0.005, half-bid-ask slippage (varies by symbol); estimated S2 cost_drag ~0.3-1.0% on $200k start_cash (commissions are very small fraction of notional) |
| Data scope | requires fresh daily OHLCV fetch for each name (operator-side; orthogonal to all current sealed-CSV chains) |
| First-principles burden vs s9 | different universe (single-name large-cap basket vs 4-ETF basket); different mechanic period (RSI(3) vs RSI(2)); bi-directional vs long-only; s9 falsification does not transfer |
| First-principles burden vs s13-d1 | ORTHOGONAL universe (cash equity vs micro-futures); fine-grained sizing (shares vs contracts); slower RSI period |
| First-principles burden vs s7-D1 | s7-D1 was 4-ETF basket; T2 is single-name basket (not ETFs); different cost surface; orthogonal |

**K9-reachability table:**

| Window | Length (y) | Required trades/y for K9 | Expected RSI(3) trades/y per name | 3-name basket expected | K9 status |
|---|---:|---|---|---|---|
| IS | ~5 (TBD at next PLAN turn) | ≥ 20 | ~25-40 | 3 × 25-40 = 75-120/y | **CLEARS with margin** |
| **OOS** | **~2** | **≥ 50** | ~25-40 | 75-120/y | **CLEARS with margin** |

**DR10-v2-reachability table:**

| Sizing assumption | Per-trade notional | Trades/y | annual_turnover | S2 cost_drag est. | DR10 v2 status |
|---|---|---|---|---|---|
| 0.5% risk × $200k = $1,000 risk; AAPL ATR ~$5 → 200 shares × $200 = $40,000 notional | $40,000 | 100 (basket) | ~40 (high; turnover branch fires) | ~0.3-0.5% (per-share commission is very small) | **CLEARS** (AND fails because cost_drag << 5%) |
| 0.25% risk → 100 shares × $200 = $20,000 | $20,000 | 100 | ~20 (turnover branch fires) | ~0.2% | **CLEARS** |

**Pros:**
- **Truly orthogonal universe** to all prior parked candidates (single-name large-cap basket; not ETFs; not micro-futures)
- K9 clears at BOTH IS and OOS with margin
- DR10 v2 clears cleanly (cost_drag branch is far below 5%; cash-equity commissions are tiny relative to notional)
- Slower RSI(3) period reduces signal density vs s13-d1
- C1-C8 phase-2 contracts carry; minor adaptations for equity cost surface

**Cons:**
- Requires fresh daily OHLCV fetch for selected symbols (operator-side; new data audit phase)
- Equity cost surface (per-share commission + half-bid-ask) is structurally different from futures; new calibration needed at SEAL
- Single-name large-cap basket has concentration risk if one name dominates (A7 effective_independent_bets metric load-bearing)
- First-principles argument vs s9 must be carefully stated at SEAL: s9 falsification was 4-ETF basket-specific; T2 is single-name basket — DIFFERENT test, but operator should explicitly weigh the lineage burden

**T2 (rev2) scoring under v2:**

| Criterion | Score (/10) | Note |
|---|---:|---|
| K9 reachability at IS | 8 | 75-120/y >> 20/y |
| K9 reachability at OOS | 8 | 75-120/y > 50/y |
| DR10 v2 reachability | 9 | cost_drag << 5% on cash equities; AND-conjunction does not fire |
| First-principles burden vs predecessors | 8 | Orthogonal universe + slower RSI + bi-directional |
| Data scope friction | 4 | Fresh OHLCV fetch required |
| Lifecycle complexity | 6 | Equity cost-surface calibration; 3-name coordination |
| **Total** | **43 / 60** | Tied with T1 (rev2); different friction profile |

----

### 5.3 Track T3 (rev2) — Slower RSI(7) + min-hold + cooldown on MNQ.c.0 single-instrument

| Field | Value |
|---|---|
| Candidate id (placeholder) | e.g., `s14-d1-mnq-c0-single-instrument-rsi-7-cooldown-min-hold` |
| Mechanic family | F3 (RSI mean-reversion; slower period; with structural cooldown + min-hold to reduce signal density) |
| Mechanic detail | RSI(7) thresholds 20/55/80/45 (slower entry; tighter exit); min-hold ≥ 3 bars; cooldown ≥ 5 bars post-exit before re-entry on same instrument |
| Universe | `{MNQ.c.0}` (reuses sealed CSV; zero data scope friction) |
| Sizing | DA3=A (1.0% per-trade risk); DA4=A ($100k cash); **different combination from s13-d1's DA3=B + DA4=C** |
| Cost surface | identical to s13-d1; reuse sealed CSV at `8b7b832c...23e` |
| First-principles burden vs s13-d1 | DIFFERENT RSI period (7 vs 2); ADDED cooldown + min-hold (structurally new mechanism); DIFFERENT DA combination (DA3=A + DA4=A vs DA3=B + DA4=C) — NOT s13-d1 territory; NOT T-FORBID-9 |
| First-principles burden vs T-FORBID-10 | T-FORBID-10 prohibits `_revN_` of s13-d1 parameters; T3 is a fresh candidate_record_id with materially different parameters AND mechanic structure (cooldown is structurally new) — NOT _revN_ |

**K9-reachability table:**

| Window | Length (y) | Required trades/y | Expected RSI(7) + cooldown trades/y on MNQ.c.0 | K9 status |
|---|---:|---|---|---|
| IS | 4.6 | ≥ 21.74 | ~15-20 (slower RSI; cooldown halves frequency vs RSI(2)) | **BORDERLINE** (15 × 4.6 = 69 < 100; 20 × 4.6 = 92 < 100; IS K9 inviolate at 100 likely fails) |
| **OOS** | **2.0** | **≥ 50.0** | ~15-20 | **FAILS** (15-20 × 2 = 30-40 << 100) |

**DR10-v2-reachability table:**

| Sizing | Per-trade notional | Trades/y | annual_turnover | S2 cost_drag est. | DR10 v2 status |
|---|---|---|---|---|---|
| 1.0% risk on $100k = $1k risk; MNQ ATR ~$100 = 10 contracts × $30k = $300k notional | $300,000 | 17 | ~100 | ~3-5% (similar to s13-d1 scaled by trade-count and capital) | **CLEARS likely** (cost_drag branch under 5% probable; AND not fired) |

**Pros:**
- Zero data scope friction (reuses sealed MNQ.c.0 CSV)
- Cooldown + min-hold structurally reduce turnover
- DR10 v2 clears via cost_drag branch

**Cons:**
- **K9 IS likely fails** at expected 15-20/y rate (need ~22/y to clear IS K9; borderline-to-fail)
- **K9 OOS FAILS** at 15-20/y rate (need ≥50/y; fails by 2-3x)
- Lifecycle expected terminal at K9 IS or K9 OOS; framework waste under T-FORBID-12 reading (candidate expected to fail K9 at PLAN time)

**T3 (rev2) scoring under v2:**

| Criterion | Score (/10) | Note |
|---|---:|---|
| K9 reachability at IS | 4 | Borderline fail |
| **K9 reachability at OOS** | **2** | FAILS by 2-3x |
| DR10 v2 reachability | 8 | Clears via cost_drag branch |
| First-principles burden | 6 | Fresh candidate but K9 is the binding low; T-FORBID-12 concern |
| Data scope friction | 10 | Zero fresh fetch |
| Lifecycle complexity | 7 | Cooldown + min-hold are well-understood mechanisms |
| **Total** | **37 / 60** | K9 OOS binding low |

----

### 5.4 Track T4 (rev2) — Donchian-10/5 weekly bar on MNQ.c.0 (fresh; NOT s12-d1)

| Field | Value |
|---|---|
| Candidate id (placeholder) | e.g., `s14-d1-mnq-c0-weekly-bar-donchian-10-5` |
| Mechanic family | F1 (Donchian breakout; no pyramid; ATR stop) — SAME family as s12-d1 but on WEEKLY bars and DIFFERENT period (10/5 vs 15/8) |
| Universe | `{MNQ.c.0}` (reuses sealed daily CSV, aggregated to weekly OHLC deterministically) |
| Sizing | DA3=A + DA4=A (different from s12-d1's DA combination) |
| First-principles burden vs s12-d1 | DIFFERENT time aggregation (weekly vs daily); DIFFERENT Donchian period (10/5 vs 15/8); DIFFERENT DA combination — NOT s12-d1 territory; NOT T-FORBID-1/2 |

**K9-reachability table:**

| Window | Length (y) | Required trades/y | Expected weekly-Donchian-10/5 trades/y | K9 status |
|---|---:|---|---|---|
| IS | 4.6 | ≥ 21.74 | ~6-10 | **FAILS** (6-10 × 4.6 = 28-46; < 100) |
| **OOS** | **2.0** | **≥ 50.0** | ~6-10 | **FAILS badly** (12-20; << 100) |

**DR10-v2-reachability table:**

| Sizing | Per-trade notional | Trades/y | annual_turnover | S2 cost_drag est. | DR10 v2 status |
|---|---|---|---|---|---|
| 1.0% risk on $100k; MNQ 1-contract scaled | $30,000 | 8 | 4.8 | ~0.3-0.5% (very few trades; low cost) | **CLEARS via both branches; turnover branch fires (4.8 > 0.50) but cost_drag (0.3-0.5%) << 5%; AND not fired** |

**Pros:**
- Reuses sealed CSV (zero fresh fetch)
- Weekly bars are structurally different from s12-d1 daily; orthogonal time aggregation
- DR10 v2 clears

**Cons:**
- **K9 FAILS at both IS and OOS** by 2-5x
- Lifecycle expected terminal at K9 IS or OOS

**T4 (rev2) scoring under v2:**

| Criterion | Score (/10) | Note |
|---|---:|---|
| K9 reachability at IS | 3 | Fails |
| K9 reachability at OOS | 1 | Fails badly |
| DR10 v2 reachability | 9 | Clears easily |
| First-principles burden | 6 | Fresh candidate but K9 is binding |
| Data scope friction | 9 | Reuses sealed CSV; weekly aggregation is deterministic but adds a small pre-processing step |
| Lifecycle complexity | 7 | Weekly-bar aggregation well-understood |
| **Total** | **35 / 60** | K9 fails at both IS and OOS |

----

### 5.5 Track T5 (rev2) — Vol/regime-filtered RSI(2) bi-directional on MNQ.c.0 with DIFFERENT DA combination

| Field | Value |
|---|---|
| Candidate id (placeholder) | e.g., `s14-d1-mnq-c0-single-instrument-rsi-2-bi-directional-regime-filtered-da-a` |
| Mechanic family | F3 (RSI mean-reversion; SAME thresholds 10/50/90/50 as s13-d1) + regime overlay (only trade when trailing-60d realized vol percentile is below trailing-252d 75th percentile, i.e., NOT in high-vol regime) |
| Universe | `{MNQ.c.0}` (reuses sealed CSV) |
| Sizing | DA3=A (1.0% per-trade risk; **different from s13-d1's DA3=B 0.5%**) + DA4=A ($100k cash; **different from s13-d1's DA4=C $200k**) |
| First-principles burden vs s13-d1 / T-FORBID-9 | T-FORBID-9: "re-attempt RSI(2) bi-directional MNQ.c.0 with DA3=B + DA4=C". T5 (rev2) uses **DA3=A + DA4=A** — materially different DA combination. Regime filter is structurally new. NOT s13-d1 territory; NOT T-FORBID-9. |
| First-principles burden vs K7 | K7 (correlation_or_filter_silently_introduced) is triggered if a filter is introduced POST-SEAL. Here the regime filter is AT SEAL TIME in the new candidate's SEAL, NOT silently — admissible. |

**K9-reachability table:**

| Window | Length (y) | Required trades/y | Expected filtered RSI(2) trades/y | K9 status |
|---|---:|---|---|---|
| IS | 4.6 | ≥ 21.74 | ~17-25 (filter cuts s13-d1's 34/y by ~30-50%) | **BORDERLINE** (17 × 4.6 = 78 < 100; 25 × 4.6 = 115 > 100) |
| **OOS** | **2.0** | **≥ 50.0** | ~17-25 | **BORDERLINE-TO-FAIL** (17 × 2 = 34 < 100; 25 × 2 = 50 = floor) |

**DR10-v2-reachability table:**

| Sizing | Per-trade notional | Trades/y | annual_turnover | S2 cost_drag est. | DR10 v2 status |
|---|---|---|---|---|---|
| 1.0% risk on $100k; MNQ ATR ~$100 = 10 contracts × $30k = $300k notional | $300,000 | 20 | ~120 | ~3-5% (similar to s13-d1 scaled; borderline 5%) | **CLEARS likely** (cost_drag < 5%; AND not fired) but borderline; SEAL-time confirmation needed |

**Pros:**
- Zero data scope friction (reuses sealed CSV)
- Regime filter has independent theoretical support (RSI mean-reversion known to work better in low-vol regimes)
- DR10 v2 clears (cost_drag branch under 5% expected)
- Fresh candidate_record_id with materially different DA combination

**Cons:**
- **K9 OOS borderline-to-fail** at expected filtered rate (17-25/y; OOS K9 floor 50/y; only the high end clears)
- DA3=A 1.0% risk is the s13-d1-rejected sizing (DR3 risk elevated for RSI lineage); operator should weigh this risk explicitly at SEAL time
- Adjacent to T-FORBID-9 (same mechanic family + same universe + RSI thresholds); operator should be comfortable that DA combination + regime filter is sufficient orthogonality to NOT be re-doing s13-d1
- DR10 v2 cost_drag at DA4=A ($100k) is borderline 5% (lower start_cash makes cost_drag larger as fraction)

**T5 (rev2) scoring under v2:**

| Criterion | Score (/10) | Note |
|---|---:|---|
| K9 reachability at IS | 6 | Borderline-to-clear |
| K9 reachability at OOS | 4 | Borderline-to-fail |
| DR10 v2 reachability | 6 | Borderline cost_drag at $100k start_cash |
| First-principles burden | 5 | Close to T-FORBID-9; DA combination + regime filter is the structural difference |
| Data scope friction | 10 | Zero fresh fetch |
| Lifecycle complexity | 7 | Regime filter well-understood |
| **Total** | **38 / 60** | K9 OOS + first-principles burden are the binding lows |

----

### 5.6 Track T6 (rev2) — Cash-equity single-name (or 3-name basket) at v2-standard sizing (rev1 T1 carry-over)

| Field | Value |
|---|---|
| Candidate id (placeholder) | similar to T2 (rev2) but single-name option (e.g., `s14-d1-aapl-single-name-rsi-3-bi-directional`) |
| Mechanic family | F3 RSI(3); same as T2 (rev2) but single-name; or basket variant |
| Universe | precommitted single name (NOT in s7-D1/s9) |
| Sizing | DA3=B (0.5% risk; **standard, not nano** — under v2 the nano-sizing precommit from rev1 is no longer needed) |
| Why retained | rev1's T1 was "cash-equity single-name with nano-sizing precommit"; under v2 the nano-sizing constraint is dropped because DR10 v2 cost_drag-branch clears at standard sizing. T6 (rev2) is the v2-updated rev1-T1 retained for completeness. |

**K9-reachability:**

| Window | Length (y) | Required trades/y | Expected single-name RSI(3) trades/y | K9 status |
|---|---:|---|---|---|
| IS | ~5 | ≥ 20 | ~25-40 | CLEARS |
| OOS | ~2 | ≥ 50 | ~25-40 | **BORDERLINE-TO-FAIL** at single-name; 3-name basket clears |

**DR10-v2-reachability:** clears (same math as T2 rev2; cost_drag << 5%).

**Pros / cons:** essentially T2 (rev2) collapsed to single-name; OOS K9 borderline if single-name; mitigation = basket (which is T2 rev2). T6 (rev2) is dominated by T2 (rev2) unless the operator specifically prefers single-name simplicity.

**T6 (rev2) scoring:** ~38/60 (single-name K9 OOS borderline-to-fail; basket = T2 (rev2) at 43/60).

----

### 5.7 Track T7 (rev2) — Defer / pause

Binary option; not scored. Available if operator wants to pause trading-bot track after the rev2 analysis without authoring T1 (rev2) or T2 (rev2).

----

## 6. Score summary (rev2 under DR10 v2)

| Track | Total | K9 IS | K9 OOS | DR10 v2 | First-principles | Data scope | Complexity |
|---|---:|---:|---:|---:|---:|---:|---:|
| **T1 (rev2): Multi-instrument RSI(2) micro-futures basket** | **43 / 60** | 9 | 9 | 7 | 8 | 4 | 6 |
| **T2 (rev2): Cash-equity 3-name basket RSI(3) at standard sizing** | **43 / 60** | 8 | 8 | 9 | 8 | 4 | 6 |
| T5 (rev2): Vol-regime-filtered RSI(2) MNQ.c.0 DA-A combination | 38 / 60 | 6 | 4 | 6 | 5 | 10 | 7 |
| T6 (rev2): Cash-equity single-name standard sizing | 38 / 60 | 8 | 5 | 9 | 8 | 4 | 6 |
| T3 (rev2): Slower RSI(7) + cooldown MNQ.c.0 | 37 / 60 | 4 | 2 | 8 | 6 | 10 | 7 |
| T4 (rev2): Donchian-10/5 weekly bar MNQ.c.0 | 35 / 60 | 3 | 1 | 9 | 6 | 9 | 7 |
| T7 (rev2): Defer | n/a (binary) | -- | -- | -- | -- | -- | -- |

### Rev1 vs rev2 score comparison (under v2 the DR10 ceiling is no longer load-bearing for cost-managed strategies)

| Track | rev1 score (under v1) | rev2 score (under v2) | Delta | Reason |
|---|---:|---:|---:|---|
| T1 rev1 (cash-equity nano) → T2 rev2 (cash-equity standard) | 31/60 | 43/60 | **+12** | DR10 v2 cost_drag-branch clears without nano-sizing precommit; K9 OOS clears at 3-name basket |
| T2 rev1 (MNQ quarterly rebalance) → not retained | 30/60 | n/a | -- | K9 fails; not advanced into rev2 |
| T3 rev1 (MNQ weekly Donchian) → T4 rev2 | 30/60 | 35/60 | +5 | DR10 v2 clears; K9 still fails |
| T4 rev1 (regime-filtered RSI(2)) → T5 rev2 | 31/60 | 38/60 | +7 | DR10 v2 clears; DA combination differentiation |
| T5 rev1 (alternate futures universe ZN/CL/MES) → ZN/CL not retained; MES merged into T1 rev2 | 21/50 | -- | -- | -- |
| (NEW in rev2) T1 rev2: Multi-instrument RSI(2) micro-futures basket | -- | 43/60 | -- | Was implicit in T1-T5 rev1 analysis; under v2 the K9 OOS arithmetic now favors it strongly |

**Key shift:** under DR10 v1 (rev1), the binding low criterion for ALL tracks was DR10 reachability. Under DR10 v2 (rev2), DR10 reachability is permissive for cost-managed strategies, and **K9 OOS reachability becomes the binding low**. The candidates that score highest are those with K9 OOS ≥ 50/y by structural design (multi-instrument basket OR cash-equity basket).

----

## 7. Recommendation

### Two co-recommended primary paths (operator selects; each requires separate authorization)

**Path T1 rev2** (micro-futures basket, K9 + DR10 v2 strongest) and **Path T2 rev2** (cash-equity basket, DR10 v2 cleanest + orthogonal universe) tie at 43/60 with different friction profiles. The operator's preference between them depends on:

- **Choose T1 rev2 if:** the operator wants to retain the s13-d1-proven RSI(2) mechanic (which was economically profitable at S0-S4; only the rev1 DR10 v1 OR-rule blocked it) and is willing to invest in fresh availability probes for MES/MYM/M2K (operator-side Databento fetch + new DR9 audit phase).
- **Choose T2 rev2 if:** the operator wants a truly orthogonal universe (cash equity vs micro-futures; cleaner first-principles burden) and is willing to invest in fresh OHLCV fetch for the single-name basket.

### Strong tertiary: T5 rev2 (vol-regime-filtered) IF operator accepts T-FORBID-9-adjacent risk

T5 rev2 has zero data scope friction (reuses sealed MNQ.c.0 CSV), but operator should explicitly weigh whether the DA combination change (DA3=A + DA4=A) + regime filter is sufficient orthogonality vs s13-d1. Conservative reading: avoid T5 rev2 unless first-principles burden can be carefully argued at SEAL time.

### NOT RECOMMENDED: T3 rev2, T4 rev2

Both fail K9 OOS (T3: 30-40/y < 50/y; T4: 12-20/y << 50/y). Lifecycle expected terminal at K9 OOS. T-FORBID-12 concern (predictable terminal lifecycle work; framework waste).

### Defer option: T7 rev2

Available if operator wants to pause trading-bot track for further reflection.

----

## 8. Boundaries held this rev2 PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT / no SEAL / no BUILD / no fetch) | met |
| No strategy code | met |
| No backtest / simulator / signal computation | met |
| No data fetch / Databento call / `DATABENTO_API_KEY` access | met |
| No network IO | met |
| No live trading | met |
| No candidate promotion | met |
| **No retroactive application of DR10 v2 to any existing sealed candidate** | met |
| **No reinterpretation of any existing sealed candidate's verdict** | met |
| **No modification of any existing sealed candidate artifact** (s11-d1 / s12-d1 / s13-d1 SEAL/P1/P2/P3/P4/P6/P6.5/P7 + framework_dr10_revision_seal_v2 byte-stable) | met |
| **No s13-d1 revival** | met |
| **No s12-d1 revival** | met |
| No s10-D2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 revival | met |
| No phase-2 safety contract template modification | met |
| No CLAUDE.md / RUNBOOK / pipeline_manifest / .gitignore modification | met |
| **No `brain_memory/projects/trading_bot/lessons.md` modification or staging** | met |
| No mutation of `review_queue.json` | met |
| No mutation of production `idea_memory` | met |
| No profitability claim | met |
| Trading status | `PAUSED` |
| Live status | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` (per existing sealed candidates) | TRUE |
| K9-reachability discipline | binding (carried) |
| DR10-reachability discipline under v2 AND-conjunction | binding (carried; updated for v2) |
| All T-FORBID-1..12 forbidden tracks | carried |

----

## 9. Files written this rev2 PLAN turn

| File | Purpose |
|---|---|
| `docs/next_research_track_selection_plan_after_s13_d1_terminal_rev2_under_dr10_v2.md` | This rev2 selection-plan revision (PLAN only; no JSON sidecar; no canonical seal sha256 since this is a planning document, not a sealed Tier-N or framework artifact). |

No other repository file is modified. The `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state from prior controller sessions remains **untouched**.

----

## 10. Next-step authorization scope

The next operator authorization in the established controller-session pattern shall use one of these scopes:

### Primary (micro-futures basket; same mechanic as s13-d1 on different universe)

```
Authorize s14-d1 multi-instrument RSI(2) bi-directional micro-futures basket Tier-N spec PLAN only — bound by DR10 v2.
```

Authors the Tier-N spec PLAN for a fresh candidate `s14-d1-mnq-mes-mym-m2k-multi-instrument-rsi-2-bi-directional-databento-long-history` per T1 (rev2). PLAN-only; no DRAFT/SEAL/BUILD until separately authorized. PLAN-time DR10-v2-reachability table must show CLEARS via cost_drag branch at SEAL-time-precommitted DA4. Universe scope: 4 equity-index micros precommitted at PLAN.

### Primary (cash-equity orthogonal universe; cleanest first-principles)

```
Authorize s14-d1 cash-equity 3-name basket RSI(3) bi-directional Tier-N spec PLAN only — bound by DR10 v2.
```

Authors the Tier-N spec PLAN for a fresh candidate per T2 (rev2). Universe shortlist (precommitted at PLAN): NOT in s7-D1/s9 (e.g., `{AAPL, MSFT, NVDA}` or operator-chosen). Fresh OHLCV fetch required (operator-side). PLAN-only; DA3=B 0.5% standard sizing.

### Secondary (vol-regime-filtered; conditional on first-principles burden)

```
Authorize s14-d1 vol-regime-filtered RSI(2) bi-directional MNQ.c.0 Tier-N spec PLAN only — bound by DR10 v2; DA3=A + DA4=A combination.
```

If operator accepts the T-FORBID-9-adjacent risk and the K9-OOS borderline. PLAN-only.

### Alternative analysis

```
Authorize alternative selection plan rev3 only.
```

If operator rejects T1 rev2, T2 rev2, T5 rev2 and wants a different analysis (e.g., a track not enumerated here, or cross-domain pivot).

### Lessons.md update (separate scope)

```
Authorize LESSON_S13_D1_001 / LESSON_S13_D1_002 / LESSON_S13_D1_003 update to lessons.md only.
```

Promote eligible-but-not-written lessons from s13-d1 P7 memo §4 to `lessons.md`. Note: pre-existing `M` state of `lessons.md` from prior B006_002 session should be resolved first.

### Pause without advancing

```
Defer / Pause trading-bot track.
```

----

## 11. Carried-forward status (UNCHANGED across this rev2 PLAN turn)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label applies to any future candidate descended from this rev2 | TRUE |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` (per existing sealed candidates) | TRUE |
| s13-d1 lifecycle terminal | TRUE — preserved verbatim under DR10 v1 |
| s12-d1 lifecycle terminal | TRUE — preserved |
| s11-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 byte-stable | TRUE — preserved |
| `lessons.md` dirty + unstaged + uncommitted (NOT touched this turn) | TRUE |
| K9-reachability discipline | binding |
| DR10-reachability discipline under DR10 v2 AND-conjunction | binding |
| framework_dr10_revision_seal_v2 sealed at `78cd22e` | binding for s14+ new SEAL turns |

----

End of rev2. PLAN-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No Databento. No `DATABENTO_API_KEY` access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No `review_queue` mutation. No production `idea_memory` mutation. **No retroactive application of DR10 v2 to existing candidates. No s13-d1 / s12-d1 / parked-candidate revival. No `lessons.md` modification or staging.** No live trading. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. s13-d1 lifecycle terminal preserved verbatim under DR10 v1.

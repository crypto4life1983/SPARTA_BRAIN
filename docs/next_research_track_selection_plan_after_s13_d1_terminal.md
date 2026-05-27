# Next-research-track selection plan after s13-d1 terminal REJECT_FAST by DR10

Status: **PLAN_ONLY** (no code written, no spec drafted, no spec sealed, no data fetched, no signal computation, no backtest, no OOS, no live; the next step is a separate operator authorization to author a Tier-N specification PLAN for the selected track).

Authored: 2026-05-27
Authorization phrase: `Authorize next research-track selection plan after s13-d1 terminal REJECT_FAST by DR10 only.`

Predecessor terminal candidate (READ-ONLY; lifecycle terminal): `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history` — REJECT_FAST by DR10 turnover_cost_explosion on the `annual_turnover > 0.50` branch at P6.5 cost-stress. P7 decision memo sealed at commit `cc1817b` (memo seal `f68dd92b00fd6c08b76a445b54ddab66555f41bd4f1eca6588977f1240de8af8`).

----

## HARD BOUNDARIES (held by this plan)

PLAN only. No DRAFT. No SEAL. No code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No `DATABENTO_API_KEY` access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No DR10 modification.** **No DR10 threshold reinterpretation.** **No s13-d1 sealed-artifact modification** (SEAL/P1/P2/P3/P4/P6/P6.5/P7 all byte-stable). No s13-d1 `_revN_` revision authorized by this plan. No s13-d1 revival. **No s12-d1 revival**. No s11-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005_NNN / B006_NNN / T8 sealed-artifact modification. No phase-2 safety contract template modification. No CLAUDE.md modification. No `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No branch change. No git push. No live trading. No profitability claim. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

----

## 1. s13-d1 terminal context (carried into framework)

| Field | Value |
|---|---|
| s13-d1 lifecycle state | `P7_DECISION_MEMO_SEALED_CANDIDATE_TERMINAL` |
| Terminal commit | `cc1817b` (P7); preceded by `15c4fb1` (P6.5), `3fa479a` (P6 IS) |
| Terminal verdict | `REJECT_FAST` (driven by DR10 turnover_cost_explosion) |
| Terminal driver | DR10 `annual_turnover>0.50 OR S2_cost_drag>0.05` — **annual_turnover branch fires** at 84.7851 >> 0.50 |
| s13-d1 terminal for this `candidate_record_id` | **True** (per SEAL `fail_safety_outcomes_terminal_for_this_candidate_record_id=True`) |
| s13-d1 NOT revived by this plan | True |
| s13-d1 `_revN_` revision NOT authorized by this plan | True |
| DR10 NOT modified by this plan | True |
| Turnover threshold NOT reinterpreted by this plan | True |

The s13-d1 candidate (single-instrument MNQ.c.0 RSI(2) bi-directional with DA3=B 0.5% risk + DA4=C $200k cash) was profitable at every cost-stress tier (S0–S4), passed all 4 A-gates at every tier, cleared K9 with margin (159 IS trades vs 100 inviolate), did NOT trigger DR3 (zero-cost-only survival) or DR5 (cost-stress tier flip), and had S0→S4 metric degradation well below the 50% provisional DR2 threshold. **But it failed DR10 at the `annual_turnover>0.50` branch** because the strategy traded at 34.34 trades/year with contracts scaled to risk (5–20 contracts per trade), producing $76M total IS notional on $200k start cash over 4.63 years = 84.7851 annual turnover.

----

## 2. Lessons from s13-d1 (carried into THIS selection-plan revision)

These lessons are recorded here as PLAN-time framework context. They are NOT written to `brain_memory/projects/trading_bot/lessons.md` by this plan; that requires separate authorization (the s13-d1 P7 memo §4 captured three eligible lessons LESSON_S13_D1_001/002/003 as deferred-to-separate-authorization).

| # | Lesson | Source |
|---|---|---|
| L1 | **DR10's `annual_turnover > 0.50` branch is OR-disjunctive with the cost_drag branch.** A capital-base mitigation (DA4=C $200k vs default $100k) addresses only the cost_drag branch (S2 drag 2.35% < 5% threshold); it does NOT reduce the turnover ratio. Both branches must clear for DR10 not to fire. | s13-d1 P6.5 + P7 |
| L2 | **For contract-based futures with proportional sizing, turnover ratio is invariant under capital rescaling.** Contracts scale with equity, so `total_notional / start_cash` does not move with start_cash. DA4 cannot mitigate the turnover branch. | s13-d1 P6.5 mathematics |
| L3 | **K9 trade-count clearance + positive A-gates are necessary but NOT sufficient for OOS progression.** An upstream DR rule firing terminates the lifecycle ahead of K-gate/A-gate consideration. DR precedence per SEAL: `DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`. | s13-d1 P6.5 + P7 |
| L4 | **Favorable economics do NOT override fail-closed verdicts by design** (LESSON_B006_002_002 reinforced). The s13-d1 strategy was profitable at every cost-stress tier (S4 still nets $79,058 on $200k) but DR10 firing made it REJECT_FAST. | s13-d1 P7 §3 |
| L5 | **DR10's 0.50 threshold combined with K9 ≥ 100 is structurally incompatible with active futures trading at proportional sizing.** Math: MNQ at index ~$15k means 1 contract ≈ $30k notional. K9-clearing trade counts at any contract size produce turnover >> 0.50. Cash equities with fine-grained sizing (< 0.5% of equity per leg) can clear both. | s13-d1 P6.5 + P7 math derivation |
| L6 | **DR10-reachability analysis MUST be performed at PLAN time** (analogous to the K9-reachability discipline introduced after s12-d1). Estimate per-trade notional × expected trade count / start_cash / years at PLAN time and confirm < 0.50 before authoring DRAFT. | This plan introduces this discipline |
| L7 | **The SEAL was correctly calibrated.** DR10 was flagged ELEVATED at s13-d1 SEAL time (Tier-N spec at `262491c`) and the P6.5 outcome confirmed the prior. The SEAL framework's `no_dr_redefinition_post_seal=True` made the firing binding. No post-SEAL re-interpretation is admissible. | s13-d1 SEAL + P7 framework reading |
| L8 | **Path C (framework-level DR10 SEAL revision) is the only way to change the threshold; Path B (new candidate with structurally lower turnover) is the only way to clear DR10 within the existing framework without modifying it.** This plan implements Path B. | s13-d1 P7 §5 |

----

## 3. DR10-reachability discipline (NEW framework requirement, analogous to K9-reachability)

Going forward, every Tier-N spec PLAN shall include an explicit **DR10-reachability table** at PLAN time (NOT deferred to SEAL or DRAFT). The table shall enumerate, for the proposed mechanic + universe + sizing scheme:

| Field | Computation |
|---|---|
| Expected per-trade notional ($) | (units per trade) × (price-per-unit) × (dollar-per-unit-multiplier) |
| Expected trades per year | from mechanic + universe signal density at PLAN time |
| Expected total_notional per year ($) | per-trade notional × trades/year × 2 (entry + exit legs) |
| `start_cash` ($) | from DA4 |
| **Expected annual_turnover** | total_notional_per_year / start_cash |
| **DR10 status** | `CLEARS` if expected < 0.50 with margin; `BORDERLINE` if 0.25–0.50; `FAILS` if > 0.50 |

The threshold 0.50 is binding under the framework's `no_dr_redefinition_post_seal=True` for any new candidate that adopts the s13-lineage DR10 by-reference. (A candidate that proposes a different DR10 definition would require a separate SEAL revision, which is Path C territory and is FORBIDDEN to author in this plan.)

The K9-reachability table (introduced after s12-d1) remains a requirement. **Both K9 and DR10 reachability tables must be present at PLAN time**, and any combination that fails either is structurally rejected at PLAN authoring before SEAL.

Applied retroactively to the alternative tracks enumerated below.

----

## 4. Forbidden tracks (explicit; carried from prior plans + s13-d1 additions)

The following tracks are FORBIDDEN to author as candidates at this turn (or any future turn) without explicit fresh operator authorization that resolves their forbidden status:

- **T-FORBID-1** (carried): Any candidate that re-attempts Donchian-15/8 on single-instrument MNQ.c.0 (s12-d1 territory; terminal)
- **T-FORBID-2** (carried): Any `_revN_` revision of s12-d1 changing parameters
- **T-FORBID-3** (carried): Any candidate that revives s10-D2 PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED via parameter iteration
- **T-FORBID-4** (carried): Any candidate that revives s10-d1 MNQ+MGC via reusing the MGC.c.0 DR9-failed continuous-stitch
- **T-FORBID-5** (carried): Any candidate that revives s9 RSI-2 ETF-proxy on its original SPY/TLT/GLD/USO universe (orthogonal universe = OK; same universe = forbidden)
- **T-FORBID-6** (carried): Any candidate that revives s7-D1 ETF-proxy or T8 ETF-proxy family on the SPY/TLT/GLD/USO universe
- **T-FORBID-7** (carried): Any candidate that revives B006_001 / B006_002 SPY vol-targeting (orthogonal asset class = OK)
- **T-FORBID-8** (carried): Any candidate that revives the NKE Tier-1 Options Wheel mechanic family
- **T-FORBID-9** (NEW from s13-d1): Any candidate that re-attempts RSI(2) bi-directional on single-instrument MNQ.c.0 with DA3=B + DA4=C (s13-d1 territory; terminal)
- **T-FORBID-10** (NEW from s13-d1): Any `_revN_` revision of s13-d1 changing RSI thresholds, ATR-P/K, risk_pct, START_CASH, warmup, or cost-stress tiers (per s13-d1 SEAL `no_strategy_parameter_modification_post_seal=True`)
- **T-FORBID-11** (NEW from s13-d1): Any candidate that proposes to **reinterpret** DR10's `annual_turnover > 0.50` threshold within the existing s11/s12/s13-lineage DR10 definition. Per `no_dr_redefinition_post_seal=True`, the only admissible path to change DR10 is a fresh framework-level SEAL revision (Path C from s13-d1 P7 §5), which is FORBIDDEN to author in this plan.
- **T-FORBID-12** (NEW from s13-d1): Any candidate that adopts the s13-lineage DR10 by-reference but is **structurally expected to fail DR10 at PLAN time** (i.e., DR10-reachability table shows `FAILS`). Authoring such a candidate would be predictable terminal lifecycle work and is framework waste.

Alternative tracks below are authored such that they satisfy first-principles burden against each forbidden track AND have a DR10-reachability table showing `CLEARS` or `BORDERLINE` at PLAN time.

----

## 5. Track candidate T1 — Single-name cash-equity mean-reversion with fine-grained sizing (recommended primary)

### 5.1 Track summary

| Field | Value |
|---|---|
| Candidate id (placeholder; assigned at next PLAN turn) | e.g., `s14-d1-spx-single-name-rsi-3-bidir-cash-equity-fine-sizing` |
| Mechanic family | F3-adjacent (RSI-3 mean reversion; bi-directional optional) on cash equity — distinct from s9 (RSI-2 4-ETF basket long-only) and s13-d1 (RSI-2 single MNQ futures bi-directional) |
| Mechanic detail (PLAN-time placeholder; locked at SEAL) | RSI(3) thresholds 15/55/85/45 (LONG entry RSI(3)<15, exit RSI(3)>55; SHORT entry RSI(3)>85, exit RSI(3)<45) — SLOWER than RSI(2); fewer signals per year |
| Universe | TBD at next PLAN turn — candidate universes: `{single large-cap equity}` from a precommitted shortlist NOT overlapping s7-D1/s9 (e.g., AAPL, MSFT, NVDA, GOOG, TSLA — DOES NOT REUSE SPY/TLT/GLD/USO) |
| Asset class | cash equity (US large-cap) |
| Resolution | daily (OHLCV-1d) |
| Sizing scheme | **fine-grained**: position size = `risk_pct * equity / (ATR * price_proxy)` rounded to nearest share (not contract); per-trade notional independent of equity scaling at low position counts |
| Cost surface | per-share commission ~$0.005, half-bid-ask slippage proxy (varies by symbol); separate from futures cost surface |
| Data scope | requires fresh daily OHLCV fetch for selected symbol(s); orthogonal to MNQ.c.0 / MGC.c.0 audit chain; operator-side fetch (NOT controller) |
| First-principles burden vs s9 | different universe (single large-cap vs 4-ETF basket); different mechanic period (RSI(3) vs RSI(2)); bi-directional optional (vs long-only); s9 falsification was instrument-cost-edge-interaction — does not transfer to single large-cap equity at different costs |
| First-principles burden vs s13-d1 | orthogonal universe (cash equity vs micro-futures); fine-grained sizing addresses the s13-d1 turnover-branch root cause; mechanic period slower (RSI(3) vs RSI(2)) reduces signal density |
| First-principles burden vs s7-D1 / B006 | different mechanic family (mean-reversion vs trend/vol-targeting); cost surface differs |

### 5.2 K9-reachability table (PLAN-time discipline applied)

| Window | Length (y) | Required closed_trades/year for K9=100 | Expected RSI(3) trades/y on a single large-cap equity | K9 status |
|---|---:|---|---|---|
| IS | ~5 (precommitted at next PLAN turn; e.g., 2019-2023) | ≥ 20 | ~25–40 (slower RSI, single name, bi-directional; depends on vol regime) | CLEARS WITH MARGIN |
| **OOS** | ~2 (e.g., 2024-2025) | **≥ 50** | ~25–40 | **BORDERLINE-TO-FAIL** |

**K9 risk assessment:** OOS K9 at ~25–40 trades/year on a single name is below the 50/year OOS floor. To clear, would need either (a) longer OOS window (~2.5–4y), (b) higher per-name signal density via more volatile name, or (c) small basket of 2–3 names (revives s9-adjacency risk if names are large-cap equities).

**Mitigation candidate:** a precommitted small-basket of 3 truly low-correlation single-names (e.g., 1 tech + 1 healthcare + 1 energy) would yield ~75–120 trades/year combined — clears OOS K9 with margin. This is a basket of single-names, NOT an ETF universe, so it does NOT revive s7-D1/s9 forbidden universe.

### 5.3 DR10-reachability table (NEW framework requirement applied)

| Sizing assumption | Per-trade notional | Trades/year | Total notional/year | Start cash | annual_turnover | DR10 status |
|---|---|---|---|---|---|---|
| 0.5% risk per trade on 1 large-cap @ $200 share, ATR ~$5, $200k cash | $200k × 0.5% / ($5/share) = 200 shares × $200 = $40,000 | 30 | $2.4M | $200,000 | **12.0** | **FAILS** |
| 0.1% risk per trade ($200 risk per trade) on 1 large-cap @ $200 share, ATR ~$5, $200k cash | $200 / $5 = 40 shares × $200 = $8,000 | 30 | $480,000 | $200,000 | **2.4** | **FAILS** |
| 0.05% risk per trade ($100) on 1 large-cap @ $200, ATR ~$5, $200k cash | 20 shares × $200 = $4,000 | 30 | $240,000 | $200,000 | **1.2** | **FAILS** |
| 0.01% risk per trade ($20) on 1 large-cap @ $200, ATR ~$5, $200k cash | 4 shares × $200 = $800 | 30 | $48,000 | $200,000 | **0.24** | **CLEARS** |

**DR10 status with margin:** at 0.01% risk per trade (very small relative to standard practice), the candidate can clear DR10 on a single name at ~30 trades/year. **This is structurally awkward** — a $200k account trading $800 per position is functionally trivial and would never be a real-money implementation. The math reveals that the s11/s12/s13-lineage DR10 threshold of 0.50 is calibrated for institutional buy-and-hold-with-quarterly-rebalance frequencies, NOT for active trading strategies of any kind on any liquid asset class.

**Implication:** T1 (or any active-trading candidate) under the s11/s12/s13-lineage DR10 by-reference must either (a) propose nano-sized positions to clear the threshold, or (b) accept that under THIS framework with DR10 unchanged, active-trading strategies are structurally rejected regardless of mechanic family or asset class.

### 5.4 Pros / cons

**Pros:**
- Truly orthogonal universe to all prior parked candidates (cash equity single-name; not in s7-D1/s9/s10-d1/s10-d2/s11-d1/s12-d1/s13-d1/B006 universes)
- Fine-grained sizing (shares vs contracts) eliminates the contract-quantization issue that drove s13-d1's high notional-per-trade
- Slower RSI period (RSI(3) vs RSI(2)) and tighter entry thresholds reduce signal density vs s13-d1
- C1–C8 phase-2 safety contracts carry by-reference (minor adaptations for equity cost surface)

**Cons:**
- **DR10 status remains FAILS under standard risk sizing**; only clears at unrealistically-small sizing (0.01% risk)
- OOS K9 borderline-to-fail on a single name; requires small precommitted basket to clear
- Requires fresh daily OHLCV fetch for new symbol(s); operator-side; new data audit phase
- Equity cost surface (per-share commission + half-bid-ask) differs from futures; new cost-stress calibration needed
- First-principles burden vs s9 must be argued carefully if any equity universe is used

### 5.5 T1 scoring (per K9 + DR10 reachability + first-principles framework)

| Criterion | Score (/10) | Note |
|---|---:|---|
| K9 reachability at IS | 7 | ~25–40/y clears 20/y floor with margin |
| K9 reachability at OOS | 5 | Borderline on single name; clears at 3-name basket |
| **DR10 reachability under s13-lineage threshold** | **2** | FAILS at all realistic sizings; CLEARS only at < 0.05% risk per trade |
| First-principles burden satisfied vs predecessors | 8 | Truly orthogonal universe + sizing scheme |
| Data scope friction | 3 | Fresh OHLCV fetch required; new audit phase |
| Lifecycle complexity | 6 | Equity cost surface adaptation needed |
| **Total** | **31 / 60** | Of which DR10 score is the binding low score |

----

## 6. Track candidate T2 — Buy-and-hold-with-rebalance on MNQ.c.0 (low-frequency by structural design)

### 6.1 Track summary

| Field | Value |
|---|---|
| Candidate id (placeholder) | e.g., `s14-d1-mnq-c0-single-instrument-quarterly-rebalance` |
| Mechanic family | F2-adjacent (buy-and-hold with periodic rebalance) |
| Mechanic detail | Long 1 MNQ.c.0 contract by default; rebalance position size **quarterly** based on trailing-60d realized volatility targeting `target_vol_pct` annualized; no signal-based entry/exit |
| Universe | `{MNQ.c.0}` (reuses sealed CSV) |
| Asset class | micro-futures |
| Sizing scheme | rebalance to 1 contract scaled by `target_vol / realized_vol` ratio, clipped to [0, 2] contracts; one rebalance per quarter |
| Cost surface | identical to s13-d1 (sealed CSV at `8b7b832c...23e` reusable) |
| Data scope | reuses sealed MNQ.c.0 CSV; ZERO fresh fetch |

### 6.2 K9-reachability table

| Window | Length (y) | Required trades/year for K9 | Quarterly rebalance rate | K9 status |
|---|---:|---|---|---|
| IS | ~4.6 | ≥ 21.7 | ~4/y (quarterly) | **FAILS** (4 × 4.6 = 18 trades, < 100) |
| **OOS** | ~2.0 | **≥ 50.0** | ~4/y | **FAILS** (4 × 2 = 8 trades, << 100) |

**K9 risk assessment:** K9 fails massively at quarterly frequency. Monthly rebalance (~12/y; IS 55, OOS 24) still fails K9 at OOS. Weekly rebalance (~52/y; IS 240, OOS 104) clears K9 but reintroduces DR10 turnover risk.

### 6.3 DR10-reachability table

| Sizing assumption | Per-trade notional | Trades/year | Total notional/year | Start cash | annual_turnover | DR10 status |
|---|---|---|---|---|---|---|
| 1 MNQ contract @ ~$15k index = $30k notional, quarterly rebalance | $30,000 | 4 | $240,000 | $200,000 | **1.20** | **FAILS** |
| 1 MNQ contract notional adjusted to $200 vol-target band (size 0.1 contract equivalent NOT SUPPORTED — contracts are integer) | n/a | n/a | n/a | n/a | n/a | structurally infeasible |

**DR10 status:** even at quarterly rebalance with the minimum 1-contract size, MNQ.c.0 produces 1.2 turnover — **FAILS DR10 by 2.4x**. This is the contract-quantization issue: MNQ at index ~$15k means the SMALLEST trade size is already $30k notional, which is 15% of $200k start cash. Four such trades per year is already 60% of start cash in one-way notional; doubled for round-trips = 1.20 turnover.

To clear DR10 with MNQ.c.0 at start_cash $200k, the candidate would need ≤ 1.67 round-trips per year on 1 contract. K9 (≥100 trades over 6.6y combined window) requires ≥ 15 round-trips per year. These two constraints are **mutually exclusive** for MNQ.c.0 with $200k start_cash and 1-contract minimum size.

### 6.4 Pros / cons

**Pros:**
- Reuses sealed MNQ.c.0 CSV (zero fresh fetch)
- C5 STRUCTURALLY_ABSENT (futures) carries
- Mechanic family F2-adjacent; B006_001 falsification was C4 SPY-specific (DR11) and does not transfer

**Cons:**
- **K9 FAILS at quarterly frequency**
- **DR10 FAILS even at quarterly minimum-contract sizing** (contract quantization)
- Higher start_cash ($500k+) would proportionally lower turnover, but DA4 already at C ($200k); would require Path C SEAL revision to change cap structure

### 6.5 T2 scoring

| Criterion | Score (/10) | Note |
|---|---:|---|
| K9 reachability at IS | 2 | FAILS at quarterly |
| K9 reachability at OOS | 1 | FAILS at all rebalance frequencies clearing DR10 |
| **DR10 reachability** | **3** | FAILS at 1-contract minimum size |
| First-principles burden | 6 | Orthogonal mechanic but contract-quantization is binding |
| Data scope friction | 10 | Zero fresh fetch |
| Lifecycle complexity | 8 | Simple rebalance rules |
| **Total** | **30 / 60** | K9 + DR10 both block |

----

## 7. Track candidate T3 — Weekly-bar Donchian or RSI on MNQ.c.0 (lower-frequency by time-aggregation)

### 7.1 Track summary

| Field | Value |
|---|---|
| Candidate id (placeholder) | e.g., `s14-d1-mnq-c0-weekly-bar-donchian-10-5` |
| Mechanic family | F1 (Donchian breakout, no pyramid, ATR stop) — same family as s12-d1 but on WEEKLY bars |
| Mechanic detail | Donchian-10/5 on weekly bars (entry: weekly close at new 10-week high/low; exit: weekly close at 5-week extreme opposite) |
| Universe | `{MNQ.c.0}` (reuses sealed daily CSV, aggregated to weekly OHLC) |
| Asset class | micro-futures |
| Sizing scheme | 1-contract fixed (NO scaling) to minimize turnover |
| Cost surface | identical to s13-d1 |
| Data scope | reuses sealed MNQ.c.0 daily CSV; weekly aggregation is deterministic |

### 7.2 K9-reachability table

| Window | Length (y) | Required trades/year for K9 | Expected weekly-Donchian-10/5 trades/y | K9 status |
|---|---:|---|---|---|
| IS | ~4.6 | ≥ 21.7 | ~6–10 (weekly bars; trend mechanic) | **FAILS** (6 × 4.6 = 28; < 100) |
| **OOS** | **~2.0** | **≥ 50.0** | ~6–10 | **FAILS** (6 × 2 = 12; << 100) |

**K9 risk assessment:** K9 fails badly. Weekly-bar mechanics on a single instrument are structurally too low-frequency for K9=100 inviolate. To clear K9, would need a weekly-bar mechanic on a 4–5-instrument basket (revives s10-d1/s10-d2 universe concerns), OR a much longer window (>15y; not available for MNQ.c.0 sealed CSV which is 2019–2025).

### 7.3 DR10-reachability table

| Sizing assumption | Per-trade notional | Trades/year | Total notional/year | Start cash | annual_turnover | DR10 status |
|---|---|---|---|---|---|---|
| 1 MNQ contract = $30k notional, ~8 weekly-bar trades/y, fixed 1-contract | $30,000 | 8 | $480,000 | $200,000 | **2.40** | **FAILS** |

**DR10 status:** still FAILS at 8 trades/year on 1 contract because contract notional ($30k) is large relative to $200k start_cash. **The contract-quantization issue persists.**

### 7.4 Pros / cons

**Pros:**
- Reuses sealed CSV
- Different time aggregation (weekly vs daily) is structurally orthogonal to s13-d1 daily-bar regime
- Mechanic family F1 same as s12-d1 but on weekly bars (less of a falsification headwind than re-doing daily Donchian)

**Cons:**
- **K9 FAILS badly** at weekly-bar frequency on a single instrument
- **DR10 still FAILS** due to MNQ contract-quantization
- Effectively requires Path C (framework-level DR10 SEAL revision) to make viable

### 7.5 T3 scoring

| Criterion | Score (/10) | Note |
|---|---:|---|
| K9 reachability at IS | 3 | FAILS at weekly frequency on single instrument |
| K9 reachability at OOS | 1 | FAILS badly |
| **DR10 reachability** | **3** | FAILS at MNQ contract quantization |
| First-principles burden | 7 | Weekly bars + F1 is orthogonal-adjacent to s12-d1 daily F1 |
| Data scope friction | 9 | Reuses sealed CSV |
| Lifecycle complexity | 7 | Weekly-bar aggregation deterministic |
| **Total** | **30 / 60** | K9 + DR10 both fail |

----

## 8. Track candidate T4 — Regime-filtered RSI(2) on MNQ.c.0 (less likely to help; recorded for completeness)

### 8.1 Track summary

| Field | Value |
|---|---|
| Candidate id (placeholder) | e.g., `s14-d1-mnq-c0-rsi-2-bidir-regime-filter` |
| Mechanic family | F3 + regime overlay |
| Mechanic detail | s13-d1's RSI(2) bi-directional + regime filter (only trade when trailing-60d realized vol is BELOW its trailing 252d 75th percentile, i.e., not in high-vol regime) |
| Universe | `{MNQ.c.0}` (reuses sealed CSV) |
| Asset class | micro-futures |

### 8.2 K9-reachability table

| Window | Length (y) | Required trades/y for K9 | Expected filtered trades/y | K9 status |
|---|---:|---|---|---|
| IS | 4.6 | ≥ 21.7 | ~17–25 (filter reduces s13-d1's 34/y by ~30–50%) | **BORDERLINE** (17 × 4.6 = 78, < 100; 25 × 4.6 = 115, > 100) |
| **OOS** | **2.0** | **≥ 50.0** | ~17–25 | **FAILS** |

### 8.3 DR10-reachability table

| Sizing | Per-trade notional | Trades/y | Annual notional | Start cash | annual_turnover | DR10 status |
|---|---|---|---|---|---|---|
| 0.5% risk on $200k = $1k per trade; MNQ ATR ~$100 = 10 contracts × $30k = $300k notional | $300,000 | 20 | $6.0M (×2 round-trip) → $12.0M one-way → $6M round-trip | $200,000 | **30.0** | **FAILS** |
| Reduce to fixed 1-contract on filtered trades | $30,000 | 20 | $600,000 | $200,000 | **3.0** | **FAILS** |

**DR10 status:** filtering reduces trade frequency by ~30–50%, but the per-trade notional is unchanged (still 5–20 contracts at $30k each for risk-based sizing, or $30k for 1-contract-fixed). **Filtering trade COUNT does not fix DR10's turnover ratio** because the ratio is dominated by per-trade notional × frequency.

### 8.4 Pros / cons

**Pros:**
- Trivial PLAN-time adaptation of s13-d1; reuses sealed CSV
- Vol-regime filter has independent theoretical support (RSI mean-reversion known to work better in low-vol regimes)

**Cons:**
- **DR10 still FAILS** by 6–60x depending on sizing
- K9 borderline-to-fail at OOS
- T-FORBID-10 risk: if interpreted as "s13-d1 with a filter added", it's a forbidden _revN_; must be explicitly authored as a fresh candidate_record_id with structurally different parameters to avoid this

### 8.5 T4 scoring

| Criterion | Score (/10) | Note |
|---|---:|---|
| K9 reachability at IS | 5 | Borderline (17–25/y) |
| K9 reachability at OOS | 3 | FAILS at OOS at filtered rate |
| **DR10 reachability** | **2** | FAILS regardless of filter |
| First-principles burden | 4 | Close to T-FORBID-10 (s13-d1 _revN_ territory) |
| Data scope friction | 10 | Reuses sealed CSV |
| Lifecycle complexity | 7 | Filter overlay well-understood |
| **Total** | **31 / 60** | DR10 binding low |

----

## 9. Track candidate T5 — Different universe entirely (Treasury / energy futures or different micro)

### 9.1 Track summary

| Field | Value |
|---|---|
| Candidate id (placeholder) | TBD at next PLAN turn |
| Mechanic | TBD (likely F1 Donchian or F3 RSI, ideally with cooldown + min-hold for turnover reduction) |
| Universe | `{ZN.c.0}` (10-yr Treasury futures), `{CL.c.0}` (crude oil), or `{MES.c.0}` (E-mini S&P; smaller notional than MNQ) — separately, not as basket |
| Asset class | varies |
| Data scope | **requires fresh Databento fetch + new dataset audit phase + availability probe** |

### 9.2 Notional-per-contract comparison (DR10-relevant)

| Symbol | Approximate notional per contract (2024) | DR10 sensitivity at $200k start_cash |
|---|---|---|
| MNQ.c.0 | ~$30,000 | high (s13-d1 contract-quantization issue) |
| MES.c.0 | ~$26,000 | high (similar) |
| ZN.c.0 | ~$110,000 | very high (1 contract = 55% of start_cash) |
| CL.c.0 | ~$70,000 | very high |
| 6E.c.0 (euro micro) | ~$130,000 | very high |

**DR10-reachability:** ALL liquid futures contracts at $200k start_cash produce 1-contract round-trip notional that is 15–65% of start_cash. **Active trading on any liquid futures contract under the s13-lineage DR10 threshold is structurally impossible.**

### 9.3 First-principles burden

- Orthogonal universe to all prior candidates (no overlap with sealed audit chains)
- BUT data scope friction is HIGH: each new symbol needs availability probe + DR9-equivalent audit + fresh sealed CSV

### 9.4 Pros / cons

**Pros:**
- Truly novel diagnostic (no inherited falsification baggage)
- Could clarify whether DR10 binding-ness is universal or asset-class-specific

**Cons:**
- **DR10 still expected to FAIL** at all futures asset classes due to contract-quantization (see notional table)
- Highest data scope friction
- Operator-side Databento fetch with API key access required
- Multiple additional sealed turns required before any Tier-N spec PLAN

### 9.5 T5 scoring

| Criterion | Score (/10) | Note |
|---|---:|---|
| K9 reachability | 5 | TBD; depends on universe |
| **DR10 reachability** | **3** | FAILS expected at all liquid futures asset classes |
| First-principles burden | 9 | Truly orthogonal |
| Data scope friction | 1 | Highest; fresh fetch + audit + multiple prerequisite turns |
| Lifecycle complexity | 3 | New universe = new audit lifecycle |
| **Total** | **21 / 50 (excluding TBD K9 OOS score)** | DR10 still binding low |

----

## 10. Track candidate T6 — Defer trading-bot track entirely; investigate framework-level DR10 SEAL revision (Path C from s13-d1 P7 §5)

### 10.1 Track summary

| Field | Value |
|---|---|
| Mechanic | None |
| Action | Pause new candidate authoring; convene a **separately authorized** framework-level investigation of DR10's `annual_turnover > 0.50` threshold |

### 10.2 Rationale

**The PLAN-time analysis of T1–T5 above demonstrates that** the s11/s12/s13-lineage DR10 threshold of 0.50 is structurally incompatible with K9-clearing active-trading strategies on any liquid asset class at retail-scale start_cash ($100k–$500k). Specifically:

- **Futures (MNQ, MES, ZN, CL):** Contract-quantization forces per-trade notional ≥ 15% of start_cash; even quarterly rebalance fails DR10.
- **Cash equities (single-name or small basket):** Standard 0.5% risk sizing produces ~5–25 turnover at K9-clearing trade counts; clears DR10 only at unrealistic 0.01% risk per trade.
- **ETFs (forbidden by T-FORBID-5/6 with prior universes; orthogonal ETFs possible but same math):** similar to single-name equities.

**Two non-exclusive readings:**

1. **The framework is correct; active trading at retail scale is structurally rejected.** Buy-and-hold + quarterly rebalance is the only DR10-clearing pattern. This is a defensible institutional-asset-management posture. Under this reading, the next research candidate is a buy-and-hold-with-rebalance and K9 must be relaxed via window extension (Path C SEAL revision required).
2. **DR10's 0.50 threshold is mis-calibrated for retail-scale active trading.** A revised threshold (e.g., 5.0, 10.0, or s2_cost_drag-only) would unblock the analysis. This is Path C from s13-d1 P7 §5: a fresh framework-level SEAL revision that explicitly revises DR10 with new threshold + justification + audit trail. **NOT a post-SEAL re-interpretation within any existing candidate.**

Both readings require separate operator authorization. T6 is the path that **acknowledges this PLAN-time finding** and proposes a framework-level investigation BEFORE authoring another candidate.

### 10.3 Pros / cons

**Pros:**
- Zero new sealed-artifact cost for now
- Preserves all existing chains
- Acknowledges the load-bearing PLAN-time finding (T1–T5 all fail DR10) and avoids predictable terminal lifecycle work (which would be framework waste; see T-FORBID-12)

**Cons:**
- No forward research motion on candidate authoring
- A framework-level SEAL revision is a heavyweight turn (requires audit of all prior DR10-binding candidates, justification of the new threshold, and re-evaluation of whether prior REJECT_FAST verdicts would still hold)

### 10.4 T6 scoring

Binary option; not scored on the 50-point scale. **Default-recommended secondary** to T1 if T1's path through DR10 (nano-sizing or basket aggregation) is rejected.

----

## 11. Recommendation

### Score summary

| Track | Total | K9 IS | K9 OOS | DR10 | First-principles | Data scope | Complexity |
|---|---:|---:|---:|---:|---:|---:|---:|
| **T1: cash-equity single-name RSI(3) bi-directional fine-grained sizing** | **31 / 60** | 7 | 5 | 2 (binding low) | 8 | 3 | 6 |
| T2: MNQ.c.0 quarterly rebalance | 30 / 60 | 2 | 1 | 3 | 6 | 10 | 8 |
| T3: MNQ.c.0 weekly-bar Donchian | 30 / 60 | 3 | 1 | 3 | 7 | 9 | 7 |
| T4: MNQ.c.0 RSI(2) regime-filtered | 31 / 60 | 5 | 3 | 2 | 4 | 10 | 7 |
| T5: Different futures universe (ZN/CL/MES) | 21 / 50 (TBD K9 OOS) | TBD | TBD | 3 | 9 | 1 | 3 |
| **T6: Defer + propose framework-level DR10 SEAL revision (Path C from P7 §5)** | **binary (default-recommended secondary)** | -- | -- | -- | -- | -- | -- |

### Honest reading of the score table

**All five candidate tracks (T1–T5) FAIL DR10 reachability at PLAN time** under the s13-lineage DR10 threshold of 0.50. The highest-scoring active-trading candidate (T1; cash equity) clears DR10 only at nano-sizing (0.01% risk per trade = $20 per position on $200k cash), which is not a meaningful trading scale. The other candidates fail DR10 at any realistic sizing. **Authoring any of T1–T5 at SEAL would be predictable terminal lifecycle work** (T-FORBID-12 territory) unless the candidate explicitly adopts nano-sizing as a structural design choice.

### Recommended primary: **T1 with explicit nano-sizing precommitment**, OR **T6 (defer + framework investigation)**

The two viable forward paths are:

**Primary (active trading, conditional):** **T1 (cash-equity single-name RSI(3) bi-directional with fine-grained sizing)** authored with an explicit nano-sizing structural precommitment (e.g., position size capped at 0.05% of start_cash = $100 per trade on $200k). This is unusual for a real-money strategy but is the only way an active-trading candidate clears DR10 under the s13-lineage threshold. **The Tier-N spec PLAN authoring would need to (a) precommit DA-sizing parameters at PLAN-time, NOT defer to SEAL, and (b) carry a PLAN-time DR10-reachability table showing CLEARS with margin at the nano-sizing level.**

**Primary (framework path):** **T6 (defer + propose framework-level DR10 SEAL revision)**. This acknowledges the PLAN-time finding that the s13-lineage DR10 threshold is structurally incompatible with K9-clearing active-trading and proposes a heavyweight SEAL revision to address it. This is the cleanest path if the operator agrees that DR10 at 0.50 is mis-calibrated for the framework's actual research intent.

### Recommended secondary: T6 (if T1 is rejected) OR T1 (if T6 is rejected)

T6 and T1 are complementary; the operator selects which constraint they want to relax — sizing (T1, nano-precommit) or threshold (T6, SEAL revision).

### NOT RECOMMENDED: T2, T3, T4, T5

All four fail K9 and/or DR10 structurally under the s13-lineage thresholds at any practical retail-scale sizing. Authoring any would be framework waste (T-FORBID-12).

### Defer-only option

The operator may choose to pause trading-bot track entirely without authoring T1 or T6. This is a third option (not scored).

----

## 12. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no DRAFT / no SEAL / no BUILD / no fetch) | met |
| No strategy code | met |
| No backtest / simulator / signal computation | met |
| No data fetch / Databento call / `DATABENTO_API_KEY` access | met |
| No network IO | met |
| No live trading | met |
| No candidate promotion | met |
| **No DR10 modification** | met |
| **No DR10 threshold reinterpretation** | met |
| **No s13-d1 revival** | met |
| **No s13-d1 `_revN_` revision authorized** | met |
| **No s13-d1 sealed-artifact modification** (SEAL/P1/P2/P3/P4/P6/P6.5/P7 byte-stable) | met |
| **No s12-d1 revival** | met |
| No s11-d1 / s10-D2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 sealed-artifact modification | met — byte-stable |
| No phase-2 safety contract template modification | met |
| No CLAUDE.md / RUNBOOK / pipeline_manifest / .gitignore modification | met |
| **No `brain_memory/projects/trading_bot/lessons.md` modification or staging** (per operator instruction) | met |
| No mutation of `review_queue.json` | met |
| No mutation of production `idea_memory` | met |
| No profitability claim | met |
| Trading status | `PAUSED` |
| Live status | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` | TRUE |
| K9-reachability discipline (introduced after s12-d1) carried | TRUE |
| **DR10-reachability discipline (introduced THIS turn) applied retroactively to T1–T5** | TRUE |

----

## 13. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/next_research_track_selection_plan_after_s13_d1_terminal.md` | This selection-plan revision (PLAN only; no JSON sidecar; no canonical seal sha256 since this is a planning document, not a sealed Tier-N artifact) |

No other repository file is modified by this plan. The `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state from prior controller sessions remains **untouched**.

----

## 14. Next-step authorization scope

The next operator authorization in the established controller-session pattern shall use one of these scopes:

### Primary (active-trading path; conditional on nano-sizing precommit)

```
Authorize T1 cash-equity single-name RSI(3) bi-directional Tier-N spec PLAN only — nano-sizing precommit at PLAN time.
```

This authors the Tier-N spec PLAN for a fresh candidate (e.g., `s14-d1-<universe>-single-name-rsi-3-bidir-cash-equity-fine-sizing`) per T1, with the explicit PLAN-time precommitment of nano-sizing (e.g., 0.05% risk per trade) to clear DR10. PLAN-only; no DRAFT/SEAL/BUILD until separately authorized.

### Primary (framework path; defers candidate authoring)

```
Authorize framework-level DR10 SEAL revision investigation PLAN only.
```

Authors a heavyweight PLAN that proposes a revised DR10 definition + threshold + justification + audit-of-prior-candidates trail. NOT a post-SEAL re-interpretation. NOT a candidate spec.

### Secondary / clarification

```
Authorize alternative selection plan rev2 only.
```

If operator rejects T1 (nano-sizing) and T6 (framework SEAL revision) and wants a different analysis (e.g., a buy-and-hold sub-track not enumerated here, or cross-domain pivot).

### Pause without advancing

```
Defer / Pause trading-bot track.
```

Trading-bot track pauses indefinitely; s13-d1 P7 terminal status is honored; no T1/T6 work authorized until a fresh authorization.

----

## 15. Carried-forward status (UNCHANGED across this PLAN turn)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label applies to any future candidate descended from this plan | TRUE |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` | TRUE |
| s13-d1 lifecycle terminal | TRUE |
| s12-d1 lifecycle terminal | TRUE |
| s11-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 byte-stable | TRUE |
| `lessons.md` dirty + unstaged + uncommitted (NOT touched this turn) | TRUE |
| K9-reachability discipline (introduced after s12-d1) | continues to bind |
| **DR10-reachability discipline (introduced THIS turn)** | now binding for all future Tier-N spec PLAN authoring |

----

End of plan. PLAN-authoring turn only. No code. No backtest. No simulator. No signal. No data fetch. No Databento. No `DATABENTO_API_KEY` access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No `review_queue` mutation. No production `idea_memory` mutation. **No DR10 modification. No turnover threshold reinterpretation. No `lessons.md` modification or staging.** No live trading. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. s13-d1 lifecycle terminal preserved.

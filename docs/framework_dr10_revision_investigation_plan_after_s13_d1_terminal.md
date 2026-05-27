# Framework-level DR10 SEAL revision investigation PLAN (after s13-d1 terminal)

Status: **PLAN_ONLY** — investigation document. **NOT a SEAL revision.** **NOT a candidate spec.** **NOT a threshold proposal as binding.** No code, no backtest, no fetch, no OOS, no live, no broker, no Strategy Lab, no candidate authoring, no sealed-artifact modification.

Authored: 2026-05-27
Authorization phrase: `Authorize framework-level DR10 SEAL revision investigation PLAN only.`

Trigger event: s13-d1 terminal REJECT_FAST by DR10 at P6.5 cost-stress (P7 sealed at commit `cc1817b`); next-research-track selection plan after s13-d1 (commit `30c836e`) found that all five candidate tracks T1-T5 FAIL DR10 reachability at PLAN time under the s13-lineage DR10 threshold of 0.50 at any practical retail-scale sizing.

----

## HARD BOUNDARIES (held by this PLAN)

PLAN only. No SEAL. **No SEAL revision authored or proposed as binding by this PLAN** (this PLAN scopes out *what a future SEAL revision would need*; it does not perform the revision). No candidate spec authored. No Tier-N PLAN authored. No DRAFT. No BUILD. No code. No backtest. No simulator. No signal computation. No data fetch. No yfinance / Yahoo Finance call. No Databento call. No `DATABENTO_API_KEY` access. No QC / LEAN call. No network IO. No `review_queue.json` mutation. No production `idea_memory` mutation. No Strategy Lab run. No candidate promotion. **No reinterpretation of DR10 in any existing sealed candidate** (s11-d1 / s12-d1 / s13-d1 SEAL/P1/P2/P3/P4/P6/P6.5/P7 verdicts remain byte-equivalent and BINDING). **No modification of any sealed candidate artifact.** No s13-d1 revival. No s13-d1 `_revN_` revision authorized by this PLAN. No s12-d1 revival. No s10-d2 / s10-d1 / s9 / s7-d1 / B005_NNN / B006_NNN / T8 revival. No phase-2 safety contract template modification. No CLAUDE.md modification. No `.gitignore` modification. **No `brain_memory/projects/trading_bot/lessons.md` modification or staging.** No branch change. No git push. No live trading. No profitability claim. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`.

This PLAN proposes 7 governance options for the operator's consideration. It does NOT recommend a specific option. It does NOT specify a new DR10 threshold. A future SEAL revision (if any) would be a separate authorization that produces a fresh framework-level sealed artifact.

----

## 1. Context

### 1.1 DR10 canonical definition (READ-ONLY; preserved verbatim from s13-d1 SEAL)

> **DR10**: `turnover_cost_explosion annual_turnover>0.50 OR S2_cost_drag>0.05 byte-equivalent (DA14=A) -> REJECT_FAST; ELEVATED prior probability vs s11-d1 v1 and s12-d1 (RSI 50-65 trades/y is 5-10x higher turnover); DA4=C mitigates via 2x capital base`

The canonical definition is OR-disjunctive across two branches:

1. **Turnover branch**: `annual_turnover > 0.50` — measured as `total_round_trip_notional / start_cash / years`
2. **Cost-drag branch**: `S2_cost_drag > 0.05` — measured as `(total_costs_at_S2_tier) / start_cash`

DR10 fires if EITHER branch fires (OR-disjunctive). Per s11/s12/s13 SEAL clause `no_dr_redefinition_post_seal=True`, this definition is immutable within each sealed candidate's own lineage.

### 1.2 The s13-d1 outcome

At P6.5 cost-stress, s13-d1 produced:

| Branch | Observed | Threshold | Fires? |
|---|---|---|---|
| `annual_turnover` | 84.7851 | > 0.50 | **YES** |
| `S2_cost_drag` | 0.023467 (2.35%) | > 0.05 | no |

DA4=C ($200k start_cash, double the default $100k) successfully mitigated the cost-drag branch (S2 drag 2.35% < 5% threshold) but did NOT affect the turnover branch. Because DR10 is OR-disjunctive, the candidate fired REJECT_FAST despite favorable economics (159 IS trades, all 4 A-gates pass at every cost-stress tier, edge positive at S0-S4, S0->S4 sharpe degradation 13%).

### 1.3 The selection-plan finding (commit `30c836e`)

The post-s13-d1 next-track selection plan found that **all five enumerated candidate tracks (T1-T5) FAIL DR10 reachability at PLAN time** under the s13-lineage DR10 threshold of 0.50, at any practical retail-scale sizing on liquid asset classes:

- Liquid futures (MNQ, MES, ZN, CL, 6E): contract-quantization forces per-trade notional to 15-65% of $200k start_cash; even quarterly rebalance at 1-contract minimum size fails DR10
- Cash equities at standard 0.5% risk sizing: ~12-25x turnover at K9-clearing trade counts; clears DR10 only at unrealistic 0.01-0.05% risk per trade
- ETFs: similar math to cash equities

The selection plan introduced the **DR10-reachability discipline** as a NEW framework requirement (analogous to the K9-reachability discipline introduced after s12-d1) and enumerated T-FORBID-12: candidates that adopt s13-lineage DR10 by-reference but are structurally expected to fail DR10 at PLAN time are framework waste.

This investigation PLAN is the response to that finding.

----

## 2. The investigation question (formalized)

> **Question:** Is the current DR10 `annual_turnover > 0.50` threshold mathematically incompatible with K9 ≥ 100 trades for active-trading strategies on liquid futures and cash equities at practical retail-scale start_cash ($100k – $1M)?

The question has two sub-questions:

- **Sub-Q1 (compatibility):** Can ANY active-trading mechanic at K9-clearing trade rates (≥ 50 trades/y per the OOS K9-reachability constraint) on liquid futures or cash equities at $100k – $1M start_cash satisfy `annual_turnover ≤ 0.50`?
- **Sub-Q2 (governance):** If Sub-Q1's answer is NO at practical sizing, what are the operator's governance options for resolving this in the framework going forward, without modifying any existing sealed candidate or reinterpreting DR10 post-SEAL within any existing lineage?

This PLAN answers Sub-Q1 mathematically and lays out governance options for Sub-Q2 without ranking them.

----

## 3. K9 reachability math (post-s12-d1 framework discipline; carried)

For the s11/s12/s13-lineage IS window (~4.6y) and OOS window (~2.0y):

| Window | Length (y) | Required trades/y for K9=100 inviolate |
|---|---:|---|
| IS | 4.6 | ≥ 21.74 |
| **OOS** | **2.0** | **≥ 50.00** (BINDING per K9-reachability discipline) |

The OOS constraint (50/y) is binding because OOS K9 fires last in the lifecycle and is the binding gate. Any candidate that produces fewer than 50 trades/y on average across the full diagnostic window is structurally expected to fire OOS K9, regardless of IS outcome.

For this investigation, **K9 reachability requires ≥ 50 trades/y on average**.

----

## 4. DR10 reachability math (NEW load-bearing analysis)

### 4.1 DR10 math derivation

```
annual_turnover = total_round_trip_notional / start_cash / years
                = (per_trade_notional × trades/year × 2_legs) / start_cash / 1_year
                = 2 × per_trade_notional × trades/year / start_cash
```

For DR10 to clear at the s11/s12/s13-lineage threshold:

```
2 × per_trade_notional × trades/year / start_cash  ≤  0.50
=>  per_trade_notional × trades/year  ≤  0.25 × start_cash
=>  per_trade_notional  ≤  0.25 × start_cash / trades/year
```

Combining with K9-reachability (trades/year ≥ 50):

```
per_trade_notional  ≤  0.25 × start_cash / 50
                    =  0.005 × start_cash
                    =  0.5% of start_cash
```

**KEY RESULT (K9 ∧ DR10 joint constraint):** Per-trade notional must be ≤ 0.5% of start_cash to satisfy both K9 (OOS, ≥ 50 trades/y) AND DR10 (annual_turnover ≤ 0.50).

### 4.2 Per-trade notional by asset class (instrument-only; not sizing-specific)

| Asset class | Instrument | Approximate 2024 notional per minimum unit |
|---|---|---|
| Equity-index micro-futures | MNQ.c.0 (Nasdaq-100 micro) | ~$30,000 / 1 contract |
| Equity-index micro-futures | MES.c.0 (S&P 500 micro) | ~$26,000 / 1 contract |
| Equity-index micro-futures | MYM.c.0 (Dow micro) | ~$20,000 / 1 contract |
| Equity-index micro-futures | M2K.c.0 (Russell 2000 micro) | ~$11,000 / 1 contract |
| Treasury futures | ZN.c.0 (10-yr Treasury) | ~$110,000 / 1 contract |
| Energy futures | CL.c.0 (crude oil) | ~$70,000 / 1 contract |
| Metal micro-futures | MGC.c.0 (gold micro) | ~$24,000 / 1 contract |
| Currency micro-futures | 6E.c.0 (euro micro) | ~$130,000 / 1 contract |
| Crypto micro-futures | MBT.c.0 (BTC micro) | ~$70,000 / 1 contract |
| Cash equity (large-cap) | AAPL @ $200 | $200 / 1 share |
| Cash equity (large-cap) | MSFT @ $400 | $400 / 1 share |
| Cash equity (large-cap) | NVDA @ $130 | $130 / 1 share |
| Cash equity (large-cap) | TSLA @ $250 | $250 / 1 share |
| ETF (large-cap) | SPY @ $500 | $500 / 1 share |
| ETF (large-cap) | QQQ @ $400 | $400 / 1 share |
| ETF (sector) | XLF @ $40 | $40 / 1 share |

### 4.3 Maximum per-trade notional for joint K9 ∧ DR10 clearance by start_cash

| start_cash | 0.5% of start_cash (= max per-trade notional) | MNQ feasible? | MES feasible? | AAPL feasible (5 shares = $1k)? | SPY feasible (2 shares = $1k)? |
|---|---|---|---|---|---|
| $100,000 | $500 | NO (1 contract = $30k = 60x over) | NO (1 contract = $26k = 52x over) | YES (2-3 shares = $400-600) | NO (1 share = $500 — borderline) |
| $200,000 | $1,000 | NO (30x over) | NO (26x over) | YES (5 shares) | YES (2 shares) |
| $500,000 | $2,500 | NO (12x over) | NO (10x over) | YES (12 shares) | YES (5 shares) |
| $1,000,000 | $5,000 | NO (6x over) | NO (5x over) | YES (25 shares) | YES (10 shares) |
| $5,000,000 | $25,000 | borderline (1 contract = $30k = 1.2x over) | YES (1 contract) | YES | YES |
| $10,000,000 | $50,000 | YES (1 contract) | YES | YES | YES |
| $50,000,000 | $250,000 | YES (multiple contracts) | YES | YES | YES |

**Observation:** At retail-scale start_cash ($100k - $1M), NO liquid futures contract has a minimum unit size small enough to permit K9 ∧ DR10 joint clearance at active-trading frequencies. Cash equities and ETFs are feasible at retail scale because share-level granularity allows arbitrarily small per-trade notional.

### 4.4 Sample sizing scenarios across asset classes at $200k start_cash

| Scenario | Asset | Sizing rule | Per-trade notional | Trades/y | annual_turnover | DR10 status |
|---|---|---|---|---|---|---|
| s13-d1 (historical) | MNQ.c.0 | 0.5% risk-based; 5-20 contracts | ~$300,000 avg | 34.34 | **84.79** | FAILS |
| MNQ quarterly rebalance 1-contract | MNQ.c.0 | 1-contract fixed | $30,000 | 4 | 1.20 | FAILS |
| MNQ weekly Donchian 1-contract | MNQ.c.0 | 1-contract fixed | $30,000 | 8 | 2.40 | FAILS |
| MNQ buy-and-hold 1-contract | MNQ.c.0 | 1-contract held | $30,000 | 2 (entry + exit per year) | 0.60 | FAILS |
| MES quarterly rebalance 1-contract | MES.c.0 | 1-contract fixed | $26,000 | 4 | 1.04 | FAILS |
| ZN quarterly rebalance 1-contract | ZN.c.0 | 1-contract fixed | $110,000 | 4 | 4.40 | FAILS |
| Cash equity standard 0.5% risk | AAPL @ $200, ATR $5 | 0.5%/ATR = 200 shares | $40,000 | 50 | **20.00** | FAILS |
| Cash equity 0.1% risk | AAPL @ $200 | 0.1%/ATR = 40 shares | $8,000 | 50 | 4.00 | FAILS |
| Cash equity 0.05% risk | AAPL @ $200 | 0.05%/ATR = 20 shares | $4,000 | 50 | 2.00 | FAILS |
| Cash equity 0.01% risk | AAPL @ $200 | 0.01%/ATR = 4 shares | $800 | 50 | 0.40 | **CLEARS** |
| Cash equity 0.005% risk | AAPL @ $200 | 0.005%/ATR = 2 shares | $400 | 50 | 0.20 | CLEARS |
| ETF SPY @ standard sizing | SPY @ $500 | 0.5%/ATR = 50 shares | $25,000 | 50 | 12.50 | FAILS |
| ETF SPY @ 0.02% risk | SPY @ $500 | 0.02%/ATR = 2 shares | $1,000 | 50 | 0.50 | borderline |
| 3-name equity basket 0.01% risk | {AAPL, MSFT, NVDA} | 0.01%/ATR per name | ~$800 avg | 150 (50/y × 3 names) | 1.20 | FAILS |
| 3-name equity basket 0.003% risk | {AAPL, MSFT, NVDA} | 0.003%/ATR per name | ~$240 avg | 150 | 0.36 | CLEARS |

### 4.5 Generalized constraint summary

For a candidate with K9-clearing trade rate of T trades/year (T ≥ 50) and start_cash S:

- **Maximum feasible per-trade notional = 0.25 × S / T**
- At T = 50/y and S = $200k: max notional ≤ $1,000 per trade
- At T = 100/y and S = $200k: max notional ≤ $500 per trade

**Liquid futures with 1-contract minimum notional ≥ $20k cannot satisfy this constraint at retail-scale start_cash.** This is a hard mathematical consequence of contract quantization, not a soft sizing preference.

----

## 5. Combined K9 ∧ DR10 feasibility analysis

### 5.1 Sub-Q1 answer

**Sub-Q1 (compatibility): NO**, at retail-scale start_cash ($100k – $1M), there is **NO** active-trading mechanic on liquid futures contracts that simultaneously satisfies K9 (≥ 50 trades/y, OOS) AND DR10 (annual_turnover ≤ 0.50). Cash equities and ETFs can satisfy both, but only at unrealistically small per-trade notional (e.g., 2-5 shares per trade on $200 stocks; $400 - $1,000 per position).

### 5.2 Where the constraint binds

| Capital scale | Active futures trading clears K9 ∧ DR10? | Active cash-equity trading clears K9 ∧ DR10 at standard risk sizing? |
|---|---|---|
| Retail ($100k – $1M) | NO (no liquid futures contract small enough) | NO (0.5% risk = ~12-25x over) |
| Sub-institutional ($1M – $5M) | NO (still 5-12x over for MNQ) | borderline (3-12x over) |
| Lower-institutional ($5M – $20M) | borderline (1-5x over for MNQ; cleaner for MES) | CLEARS |
| Institutional ($20M+) | CLEARS | CLEARS |

### 5.3 Where the constraint does NOT bind

The constraint does NOT bind for **buy-and-hold-with-rebalance** strategies at LOW frequency (≤ 4 turnovers/y) — these trivially have annual_turnover ≤ 1.0 and often ≤ 0.25. But K9 ≥ 100 over 6.6y combined window typically fails for such strategies (≤ 26 trades total). So **buy-and-hold candidates fail K9, not DR10**.

The only candidate that clears BOTH K9 and DR10 simultaneously at retail-scale capital is **active cash-equity trading at nano-sizing** (e.g., 0.005% – 0.02% risk per trade), which corresponds to $10 – $40 risk per trade on $200k. This is functionally trivial sizing — not a meaningful trading strategy at retail capital.

----

## 6. Historical candidate audit (sealed-chain READ-ONLY)

This audit examines whether prior candidates *would have* fired DR10 under the s13-lineage definition. **The sealed verdicts of these prior candidates are not modified by this audit.** This is informational only.

| Candidate | Mechanic | Universe | Outcome at SEAL | annual_turnover (observed or estimated) | DR10 status under s13-lineage definition |
|---|---|---|---|---|---|
| s7-D1 | Donchian | 4-ETF basket | parked (concentration / USO dominance) | low (~5/y; basket diversifies notional) | est. CLEARS |
| s9 | RSI(2) long-only | 4-ETF basket | parked (DR2/DR3; S2/S3 negative edge) | est. 5-15 | est. **FAILS** |
| s10-D1 | Donchian | MNQ + MGC | parked (MGC DR9 continuous-stitch failure; data integrity) | est. low | est. CLEARS (low frequency) |
| s10-D2 | Donchian-55/20 | 4-market futures | parked (OOS K9: 53 trades / OOS window) | est. ~1.5 | est. **FAILS** |
| s11-d1 v1 | (parent SEAL) | -- | parked | est. ~5-10 | est. **FAILS** |
| s12-d1 | Donchian-15/8 | MNQ.c.0 single | parked (K9 falsified at IS: 48 trades) | ~1.0 (at observed 10/y rate) | est. **FAILS** |
| **s13-d1** | **RSI(2) bi-directional** | **MNQ.c.0 single** | **terminal REJECT_FAST by DR10 turnover branch** | **84.79** | **FAILS (binding)** |
| B005_001 | intraday ETF momentum | SPY | parked | (different DR set; not s11-lineage) | n/a (B005/B006 use a different DR chain) |
| B006_001/002 | SPY vol-targeting | SPY | rejected (DR11; C4 leverage-cap) | ~0.1 (low rebalance) | est. CLEARS |

**Pattern observed:** Every actively-traded candidate in the s9/s10/s11/s12/s13 lineage that progressed to IS execution had observed or estimated annual_turnover well above 0.50. Only buy-and-hold-style or very-low-frequency candidates would have cleared. **The s13-d1 outcome was the first time DR10 was actually evaluated against an observed annual_turnover** because prior s11/s12-lineage candidates terminated at upstream gates (K9 inviolate, DR9 data integrity, etc.) before reaching P6.5.

**Implication:** DR10's `annual_turnover > 0.50` branch has been latent across the s9/s10/s11/s12 chain — it would have fired had any of those candidates reached P6.5 with positive A-gate outcomes. s13-d1 is the first candidate to *reach* P6.5 with K9 cleared and edge positive, exposing the latent constraint. The constraint was structural, not specific to RSI(2).

----

## 7. Governance options (math trade-offs; PLAN does NOT recommend one)

Each option is presented with its math implications, framework consequences, and risks. The operator selects the path under a separate authorization.

### 7.1 Option A — Status quo (DR10 unchanged)

| Field | Value |
|---|---|
| Change | None. DR10 remains `annual_turnover > 0.50 OR S2_cost_drag > 0.05` in the s11/s12/s13-lineage definition. |
| Framework consequence | Future candidates that adopt s13-lineage DR10 by-reference must structurally clear DR10 at PLAN time per the DR10-reachability discipline. The framework targets buy-and-hold-with-rebalance OR institutional-scale active trading. |
| Active-trading candidates at retail scale | Structurally rejected; framework intent affirmed. |
| Migration cost | Zero. |
| Risk | Trading-bot research track effectively pauses for retail-scale active trading; only T1-style nano-sizing or sub-institutional capital scenarios are admissible. |

### 7.2 Option B — Raise threshold to a higher calibrated value

| Field | Value |
|---|---|
| Change | Replace `0.50` with a calibrated higher value (e.g., `5.0`, `15.0`, `25.0`, or `100.0`). |
| Math at threshold = 25.0 | per_trade_notional ≤ 12.5% of start_cash at OOS-K9 ≥ 50/y. Allows MNQ.c.0 single-contract trading at $200k start_cash (1 contract = 15% = borderline-fails at 25.0; clears at 30.0). |
| Math at threshold = 100.0 | s13-d1's 84.79 turnover would CLEAR. Effectively disables the turnover branch. |
| Framework consequence | Looser DR10 ≈ more candidates pass ≈ trading-bot research track proceeds. |
| Risk | Loses one signal of "over-trading". The threshold becomes a calibration parameter rather than a structural constraint. Requires defensible justification for the new value (e.g., academic literature on turnover-cost trade-off, or institutional-trading standards). |
| Migration cost | Moderate. Audit all prior candidates that *passed* DR10 (none under s11/s12-lineage actually reached P6.5; s13-d1 is terminal; no verdict change). |

### 7.3 Option C — Drop the turnover branch; keep cost_drag only

| Field | Value |
|---|---|
| Change | Replace `annual_turnover > 0.50 OR S2_cost_drag > 0.05` with `S2_cost_drag > 0.05` alone. |
| Original DR10 name | "turnover_cost_explosion" — implies cost was the load-bearing concern; turnover was a proxy. |
| Math consequence | s13-d1's S2 cost_drag was 2.35% < 5% — would NOT fire under Option C. Cost-drag governance preserved; raw-turnover governance dropped. |
| Framework consequence | DR10 becomes purely cost-driven. Strategies that "churn" with high turnover but maintain low total cost-drag (e.g., commission-free micro-futures at deep liquidity) pass cleanly. |
| Risk | Loses raw-turnover as a screening signal. Strategies with operational fragility tied to high turnover (slippage variance, fill-rate degradation in stress markets) are no longer caught by DR10. Other DRs (DR5 cost-stress tier flip; DR2 OOS metrics degrade) provide partial overlap. |
| Migration cost | Low. The "OR" branch is simply removed. Need to confirm no prior candidate would be retroactively re-verdicted (audit confirms s13-d1 is terminal regardless under either option C or status quo). |

### 7.4 Option D — Asset-class-specific threshold

| Field | Value |
|---|---|
| Change | DR10 threshold becomes a function of asset_class: |
| Liquid futures (contract-quantized) | `annual_turnover > X_futures` (e.g., `> 50.0`) |
| Cash equities (fine-grained sizing) | `annual_turnover > Y_equity` (e.g., `> 5.0`) |
| ETFs | `annual_turnover > Z_etf` (e.g., `> 10.0`) |
| Math consequence | Reflects the contract-quantization reality. MNQ.c.0 with X_futures = 50.0 would have s13-d1's 84.79 still firing (close call). Cash-equity nano-sizing easier to clear. |
| Framework consequence | More nuanced; explicitly acknowledges asset-class structural differences. |
| Risk | Parameter proliferation; harder to defend each per-class threshold; opens debate at each new asset class. |
| Migration cost | High. Requires audit + justification per asset class. |

### 7.5 Option E — Normalize threshold by capital scale

| Field | Value |
|---|---|
| Change | DR10 threshold becomes `annual_turnover > 0.50 × ($1M / start_cash)`. |
| Math at $200k | Effective threshold = 0.50 × 5 = 2.50. s13-d1's 84.79 still FAILS. Not enough to fix retail-scale active trading. |
| Math at $1M | Effective threshold = 0.50 × 1 = 0.50. Same as today; no change at institutional reference scale. |
| Math at $5M | Effective threshold = 0.50 × 0.2 = 0.10. STRICTER at higher capital. Counter-intuitive. |
| Framework consequence | Threshold dynamically reflects capital scale, but the direction (stricter at higher capital) is counter-intuitive for a turnover-cost-explosion rule. |
| Risk | Direction is wrong: institutional traders are LESS sensitive to turnover-driven cost-explosion (better execution), so a capital-normalized threshold should be looser at higher capital, not stricter. A reverse normalization (`× start_cash / $1M`) would address this but introduces a counter-intuitive load-bearing arbitrariness in the threshold. |
| Migration cost | Moderate. Requires defensible anchor capital choice. |

### 7.6 Option F — Multi-prong AND threshold

| Field | Value |
|---|---|
| Change | Replace OR with AND: `annual_turnover > 0.50 AND S2_cost_drag > 0.05`. |
| Math consequence | Both branches must fire for DR10 to fire. s13-d1: 84.79 turnover fires AND 2.35% cost_drag does NOT fire → DR10 DOES NOT fire under Option F. |
| Framework consequence | Effectively turns DR10 into "high turnover + high cost-drag" simultaneity check. Either branch alone is permissive. |
| Risk | Removes the ability to fire DR10 on raw turnover alone. A strategy with 1000x turnover but zero costs (theoretical-only example) would pass. The original intent of catching "turnover-driven cost-explosion" survives if costs are tracked; the raw-turnover screen is dropped. |
| Migration cost | Low. Single-character change (OR → AND). |

### 7.7 Option G — Defer (no SEAL change for now)

| Field | Value |
|---|---|
| Change | None. Same as Option A in framework consequence. |
| Distinction from A | Option A is an active operator decision to keep DR10 unchanged after reviewing the math; Option G is a deferral to revisit later (e.g., after more candidates surface the constraint, after Trading Lab matures, after additional research). |
| Framework consequence | Trading-bot research track pauses; no new candidate authoring authorized in the meantime. |
| Migration cost | Zero. |

### 7.8 Combined-option matrix

| Option | Threshold change | s13-d1 verdict (if hypothetically re-run under revised DR10 — **NOT actually re-run; s13-d1 verdict is terminal under the OLD DR10 by SEAL invariant**) | Migration cost | Defensibility |
|---|---|---|---|---|
| A. Status quo | none | unchanged: REJECT_FAST | zero | high (status quo) |
| B. Raise threshold (e.g., to 100) | scalar revision | would NOT have fired | moderate | medium (depends on calibration) |
| C. Drop turnover branch | structural | would NOT have fired (S2 drag 2.35% < 5%) | low | medium (loses signal) |
| D. Asset-class-specific | structural | depends on X_futures choice | high | medium-low (parameter proliferation) |
| E. Capital-scale normalize | structural | unchanged: would still fire at $200k | moderate | low (counter-intuitive direction) |
| F. OR → AND | operator | would NOT have fired (S2 drag does NOT fire) | low | medium (removes one branch) |
| G. Defer | none | n/a | zero | high (deferral) |

**Critical clarification (preserved across all options):** Per s13-d1 SEAL `no_dr_redefinition_post_seal=True` and `fail_safety_outcomes_terminal_for_this_candidate_record_id=True`, s13-d1's REJECT_FAST verdict and terminal lifecycle status are byte-equivalent and binding under the OLD DR10 regardless of which option is selected. **A future SEAL revision (if any) applies only to NEW SEAL turns going forward (e.g., s14+).** Past sealed candidates retain their old DR10 verdicts byte-equivalent.

----

## 8. What a SEAL revision would require (scoping, NOT performing)

If the operator selects Option B / C / D / E / F under a separate authorization, the SEAL revision turn would need to produce:

### 8.1 A fresh framework-level SEAL artifact

A new sealed document (proposed path: `reports/framework_dr10_revision_seal_v2.json` and `.md`) that:

- Records the revised DR10 definition verbatim
- Carries an audit trail explaining the revision rationale
- Lists all prior candidates with their DR10 status under both OLD and NEW definitions (for transparency; the prior candidates' SEALs are NOT modified)
- Names the SEAL revision (e.g., "DR10_v2") and binds the new definition to all subsequent Tier-N specs

### 8.2 Migration rules

The SEAL revision turn would document:

- Which framework-level docs (if any) need updating
- Whether the K9-reachability + DR10-reachability disciplines are themselves revised
- Whether the DR precedence chain (`DR7 → DR1 → DR9 → DR10 → DR6 → DR4 → DR2 → DR3 → DR5`) is preserved or revised
- Which candidate `candidate_record_id`s are eligible to adopt the new DR10 (default: all new candidates from s14 onward; existing parked / terminal candidates remain on old DR10 by-reference)

### 8.3 Forbidden in the SEAL revision turn (carried)

- No reinterpretation of any existing sealed candidate's verdict
- No modification of any existing sealed artifact
- No revival of any parked / terminal candidate
- No backtest, no fetch, no OOS, no live, no Strategy Lab promotion
- No silent threshold change ("silently" = without a sealed framework-level audit trail)
- No `lessons.md` edit (unless separately authorized within the SEAL revision turn)

### 8.4 Sign-off requirements

A SEAL revision is heavyweight. The turn would need:

- Operator typed authorization (e.g., `Authorize framework-level DR10 SEAL revision to <option> only.`)
- All prior candidates' SEAL/P1/P2/P3/P4/P6/P6.5/P7 byte-stability re-attested in the SEAL revision document
- The current state of trading (`PAUSED`), live (`BLOCKED_AT_6_GATES`), FRC (`NEVER_GRANTED`) carried verbatim

----

## 9. What this PLAN explicitly does NOT do

- This PLAN does NOT propose a specific revised DR10 threshold as binding.
- This PLAN does NOT modify any existing sealed candidate.
- This PLAN does NOT reinterpret any existing sealed verdict.
- This PLAN does NOT author a SEAL revision; it scopes out what one would need.
- This PLAN does NOT revive s13-d1, s12-d1, or any prior parked candidate.
- This PLAN does NOT recommend a specific governance option (Options A–G presented with trade-offs only).
- This PLAN does NOT promote anything to Strategy Lab.
- This PLAN does NOT grant FRC, modify the live block, or change any other framework status field.
- This PLAN does NOT modify `lessons.md`.
- This PLAN does NOT run any backtest, fetch any data, inspect OOS, connect to broker, or place any order.

----

## 10. Boundaries held this PLAN turn

| Boundary | Status |
|---|---|
| PLAN only (no SEAL / no SEAL revision / no Tier-N spec / no DRAFT / no BUILD / no code) | met |
| No backtest / simulator / signal computation | met |
| No data fetch / Databento call / `DATABENTO_API_KEY` access | met |
| No network IO | met |
| No live trading | met |
| No candidate promotion | met |
| **No reinterpretation of DR10 within any existing sealed candidate** | met |
| **No modification of any existing sealed candidate artifact** (s11-d1 / s12-d1 / s13-d1 SEAL/P1/P2/P3/P4/P6/P6.5/P7 byte-stable) | met |
| **No revival of s13-d1, s12-d1, or any prior parked candidate** | met |
| **No threshold proposal as binding** (Options A–G are presented as trade-off analysis, not as a recommendation) | met |
| **No specific governance option recommended** | met |
| **No `brain_memory/projects/trading_bot/lessons.md` modification or staging** | met |
| No mutation of `review_queue.json` | met |
| No mutation of production `idea_memory` | met |
| No profitability claim | met |
| Trading status | `PAUSED` |
| Live status | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` (per existing sealed candidates) | TRUE — preserved verbatim |
| K9-reachability discipline (from after s12-d1) | continues to bind |
| DR10-reachability discipline (from after s13-d1) | continues to bind |

----

## 11. Files written this PLAN turn

| File | Purpose |
|---|---|
| `docs/framework_dr10_revision_investigation_plan_after_s13_d1_terminal.md` | This investigation PLAN (PLAN only; not a sealed Tier-N artifact; no JSON sidecar; no canonical seal sha256). |

No other repository file is modified by this PLAN. The `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state from prior controller sessions remains **untouched**.

----

## 12. Next-step authorization scope

The next operator authorization in the established controller-session pattern shall use one of these scopes (one per option from §7; the operator selects which to pursue, if any):

### Option A authorization

```
Authorize framework-level confirmation that DR10 remains at 0.50 (status quo; no SEAL revision).
```

Affirms framework intent; documents the trade-off as accepted. No SEAL revision turn required.

### Option B authorization

```
Authorize framework-level DR10 SEAL revision to raise threshold to <specific value> only.
```

The operator specifies the new threshold value at authorization time. SEAL revision turn produces a fresh framework-level sealed artifact.

### Option C authorization

```
Authorize framework-level DR10 SEAL revision to drop turnover branch (keep S2_cost_drag only) only.
```

Structural revision; turn produces fresh framework SEAL.

### Option D authorization

```
Authorize framework-level DR10 SEAL revision to asset-class-specific thresholds only.
```

Heavyweight; per-asset-class thresholds. Turn produces fresh framework SEAL.

### Option E authorization

```
Authorize framework-level DR10 SEAL revision to capital-scale-normalized threshold only.
```

Operator should resolve the direction-of-normalization concern (§7.5) before authorizing.

### Option F authorization

```
Authorize framework-level DR10 SEAL revision to AND-conjunction of turnover and S2_cost_drag only.
```

Single-operator change; turn produces fresh framework SEAL.

### Option G authorization

```
Defer / pause framework-level DR10 SEAL revision investigation.
```

No further work on this thread.

### Alternative: revise this investigation PLAN

```
Authorize framework-level DR10 SEAL revision investigation rev2 only.
```

If operator wants a different analysis (e.g., a governance option not enumerated here, or a different framing of the question).

----

## 13. Carried-forward status (UNCHANGED across this PLAN turn)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label | applies to any future candidate descended from any post-revision DR10 |
| `no_strategy_optimization_authorized` | TRUE |
| `no_dr_redefinition_post_seal` (per existing sealed candidates) | TRUE — preserved |
| s13-d1 lifecycle terminal | TRUE — preserved verbatim |
| s12-d1 lifecycle terminal | TRUE — preserved |
| s11-d1 / s10-d2 / s10-d1 / s9 / s7-d1 / B005 / B006 / T8 byte-stable | TRUE — preserved |
| `lessons.md` dirty + unstaged + uncommitted (NOT touched this turn) | TRUE |
| K9-reachability discipline | binding |
| DR10-reachability discipline | binding |
| Framework-level DR10 SEAL revision (if any) | scope authored this turn as PLAN ONLY; no revision performed; awaiting operator selection of Option A–G |

----

End of PLAN. Investigation document only. No SEAL. No SEAL revision. No Tier-N spec. No candidate. No code. No backtest. No simulator. No signal. No data fetch. No Databento. No `DATABENTO_API_KEY` access. No QC. No LEAN. No brokerage. No real order. No paper order. No Strategy Lab promotion. No `review_queue` mutation. No production `idea_memory` mutation. **No reinterpretation of DR10 within any existing sealed candidate. No modification of any sealed artifact. No revival of any parked / terminal candidate. No `lessons.md` modification or staging.** No live trading. Trading remains `PAUSED`. Live remains `BLOCKED_AT_6_GATES`. FRC `NEVER_GRANTED`. s13-d1 lifecycle terminal preserved verbatim under the OLD DR10 definition regardless of any future revision.

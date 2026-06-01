# SPARTA Arbitrage Research Protocol v1

> **Research-only. Protocol/specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls and no data fetch in this
> bundle.** The protocol exists to lock in language, scope, costs, kill rules,
> and validation phases **before** any data work begins.

**Protocol id:** `arbitrage_research_protocol_v1` · **version:** `1.0`

---

## 1. Research objective

Define the exact, conservative protocol SPARTA will follow if and when it
studies arbitrage / market-inefficiency opportunities. This document does not
build a bot, does not fetch data, does not connect to any exchange, and does
not claim profitability. It exists so that **no future arbitrage work can
start** without first having a written contract for what arbitrage means,
which costs are mandatory, and which kill conditions are immovable.

## 2. What counts as arbitrage vs. not arbitrage

**Pure arbitrage** — simultaneous (or near-simultaneous) round-trip trade
across two or more instruments / venues that nets a positive cash flow with
zero or near-zero directional exposure, **after every realistic cost is
subtracted**. Pure arbitrage in liquid public markets is rare; the default
assumption is that apparent edges are an artifact of stale data, ignored
costs, or unmeasured execution risk.

**Apparent edge ≠ profit.** A price difference visible in two data feeds is
**not** profit. It only becomes a profit hypothesis after:
fees, transfer delay, liquidity at the visible price, spreads at execution
time, funding, borrow cost, latency to fill, withdrawal limits, exchange
counterparty risk, and operational risk have all been deducted. Apparent
edges that vanish under any of these subtractions are research-only
curiosities.

**Not arbitrage** — anything that requires direction, persistence, or
mean-reversion of a relationship (statistical / relative-value strategies,
pairs trading, lead-lag predictors, regime alpha). These belong in their own
protocol; we will study them but never call them arbitrage.

**Word discipline.** In every downstream SPARTA report, the word *arbitrage*
is reserved for the pure-arbitrage definition above. Everything else is
labelled `statistical_relative_value`.

## 3. Categories in scope

### A. Cross-exchange spot arbitrage
- **Example:** BTC/USDT price difference between two regulated spot venues.
- **Hypothesis:** Persistent positive expectancy from buying the cheap venue
  and selling the rich venue, sized so spreads + fees + transfer delay +
  withdrawal limits + counterparty risk do not erode the gap.
- **Data needed:** L1/tick order books per venue, withdrawal/deposit latency
  stats, fee schedules per tier, withdrawal limits, historical venue-outage
  events, custody constraints.
- **Minimum viable test:** Offline replay of aligned L1 books with MAKER+TAKER
  fees, a withdrawal-latency penalty, and a "both legs would have been
  touched" rule. Require positive expectancy with non-overlapping confidence
  intervals.
- **Main costs:** Fees per leg, crossed spread, withdrawal/deposit fees,
  network transfer time, rebalance ops, FX/stablecoin conversion.
- **Main risks:** Stale-quote illusion; withdrawal freeze; exchange
  insolvency; KYC / regulatory friction; capital lockup; thin liquidity at
  visible price.
- **Likely feasibility:** LOW for a single retail operator; HFT desks have
  this competed away within milliseconds on liquid pairs.
- **Why it may fail:** By the time funds rebalance the gap is gone; visible
  book is informational not executable; outages turn lock-up into loss.
- **First safe research step:** Author the data contract (venues, pairs,
  clock, fee tiers, withdrawal latency assumption, counterparty haircut,
  source of OFFLINE history). **Do not pull data yet.**

### B. Spot-perp basis / funding arbitrage
- **Example:** Long BTC spot + short BTC perp (or vice versa) while funding
  pays the short.
- **Hypothesis:** After all fees + funding flow + carry > maintenance margin
  + borrow cost + adverse spread.
- **Data needed:** Funding-rate history per venue, perp mark/index, spot
  history on the same clock, margin/maintenance/liquidation rules, borrow
  rates, custody/stablecoin costs.
- **Minimum viable test:** Offline replay on a SINGLE venue first (avoid
  cross-venue settlement risk). Hypothetical funding accruals, entry/exit
  fees on both legs, one funding-flip stress, one liquidation-stress; report
  net annualized carry.
- **Main costs:** Entry/exit fees, funding-paid (not received) regimes,
  borrow/short cost, margin lockup, MTM volatility.
- **Main risks:** Funding flips against you; perp dislocations on stress;
  liquidation cascade; oracle / index manipulation; counterparty risk on one
  venue.
- **Likely feasibility:** MEDIUM-LOW.
- **Why it may fail:** Funding can flip persistently negative during stress;
  tail liquidation wipes the carry.
- **First safe research step:** Data contract + cost model + liquidation-stress
  scenario. Pre-register: any single stress eating > N months of carry kills
  the lane.

### C. Triangular arbitrage
- **Example:** BTC/USDT → ETH/BTC → ETH/USDT loop on a single venue.
- **Hypothesis:** Cross-rate inconsistency on a single venue's quote book is
  large enough, often enough, after fees, to net positive.
- **Data needed:** Synchronous L1 (or L2 top-of-book) snapshots for all three
  pairs at the SAME timestamp; venue fee schedule per pair; quote-vs-fill
  slippage; tick rules.
- **Minimum viable test:** Offline replay; for each timestamp compute implied
  vs. quoted cross-rate; require all three legs simultaneously executable at
  top-of-book after maker-or-taker fees, after a one-tick slippage on each
  leg, after a minimum dwell time so the snapshot is not stale.
- **Main costs:** Three fees, three slippages, time-to-fire on three legs
  (slowest leg = risk window).
- **Main risks:** By the third leg, one book has moved; partial fills leave
  unhedged exposure; venue rate-limits trip on bursts; visible top-of-book is
  not always executable size.
- **Likely feasibility:** LOW for retail; this is a co-located HFT problem on
  liquid venues.
- **Why it may fail:** The "gap" is informational latency.
- **First safe research step:** Strict synchronous-quote-book definition +
  offline test on a single past hour of one liquid venue.

### D. Futures calendar / basis arbitrage
- **Example:** Front-month vs. next-month contract (or fixed-expiry vs. perp)
  basis trades.
- **Hypothesis:** Term structure between contracts deviates from a
  no-arbitrage / cost-of-carry model in a way that survives fees, margin, and
  rolls.
- **Data needed:** Continuous front/next series with explicit roll dates and
  method, margin schedule, fee schedule, settlement vs. close conventions,
  cash/carry assumption.
- **Minimum viable test:** **OFFLINE replay only; specification phase only
  in this protocol version. NO backtest is run in Bundle 4.** Pre-register
  contracts, roll method, cost model, OOS window.
- **Main costs:** Two-leg fees, exchange margin, roll slippage,
  market-impact on illiquid back months.
- **Main risks:** Liquidity drops at the back month; crowded rolls; basis
  dislocation during expirations/news; large capital required.
- **Likely feasibility:** MEDIUM in theory, MEDIUM-LOW in practice for
  retail.
- **Why it may fail:** Roll spreads eat the basis; back-month liquidity
  vanishes when needed.
- **First safe research step:** Spec only. Do not start a backtest from this
  bundle.

### E. Statistical / relative-value mispricing (**NOT pure arbitrage**)
- **Example:** Pairs trade on two correlated equities or two correlated
  crypto majors when the spread widens vs. its historical distribution.
- **Hypothesis:** Historically mean-reverting spread reverts often enough,
  with bounded drawdown, to produce positive expectancy after fees and borrow.
- **Data needed:** Aligned price series, borrow availability/cost,
  transaction cost model, cointegration / stationarity diagnostics.
- **Minimum viable test:** OFFLINE replay of the spread on frozen data with
  explicit cointegration test on the IN-SAMPLE window only; OOS verdict held
  back. **Do not call this arbitrage in any report.**
- **Main costs:** Two-leg fees + slippage, borrow on the short leg, capital
  tied up, financing.
- **Main risks:** Cointegration is not permanent; half-life longer than your
  hold willingness; structural break ends the relationship.
- **Likely feasibility:** MEDIUM as a directional lane; LOW as risk-free.
- **Why it may fail:** Regime change; spread does not revert in time; one
  leg has an event.
- **First safe research step:** Author the pair-selection rule, the holdout
  split, the kill condition. **Mark category as RELATIVE_VALUE, not
  ARBITRAGE, throughout all downstream reports.**

## 4. Out of scope

- Cross-jurisdiction tax-arbitrage of regulated products.
- Stablecoin de-peg trading (counterparty + regulatory + tail-risk dominated).
- DeFi flash-loan strategies (smart-contract + MEV + gas + reorg risk).
- OTC / dark-pool arbitrage (requires venue relationships).
- Predictive / directional strategies dressed up as "arbitrage" (market-making, latency arb, news arb).
- Anything that requires placing a real order anywhere from this protocol's runtime.
- Anything that requires fetching live data from any venue from this protocol's runtime.

## 5. Market / data requirements

- **Frozen data only.** No live fetch in any phase of this protocol.
- **Explicit clock.** Multi-venue / multi-leg studies must align to one
  documented UTC source and disclose per-venue clock skew.
- **Synchronous snapshot rule.** Cross-venue / triangular tests must compare
  snapshots that share a documented timestamp; never mix last-trade vs.
  mid-book vs. ticker.
- **No lookahead.** Features and quotes available at decision time only; no
  future bars.
- **OOS seal.** Each category declares an IS window and an OOS window before
  any test.

## 6. Exchange / venue requirements

- Venue must be **named** in the spec.
- Venue must have a fee schedule **attached**.
- Venue must have a withdrawal-latency **assumption**.
- Venue must have a counterparty **haircut**.
- **No live connection** is established by this protocol — venues are
  inputs to the data contract.

## 7. Cost-model minimums

- **Fees per leg:** MAKER and TAKER tiers documented; default to TAKER for
  sizing tests unless a maker proof is provided.
- **Spread haircut:** at least 1 tick / 1 bp per leg on top of fees, larger
  on illiquid pairs.
- **Withdrawal latency:** conservative (slow-day) latency for cross-venue
  legs; never best-case.
- **Funding/borrow:** spot-perp and short-leg pair trades carry an explicit
  funding/borrow PnL line.
- **Stress overlay:** each category includes at least one adverse stress
  scenario (venue outage, funding flip, liquidation cascade, roll
  dislocation) deducted from expectancy.

## 8. Liquidity filters

- Test fills capped at a documented fraction of displayed top-of-book size.
- At least one depth-aware sensitivity test per category before any
  go/no-go.
- Per-venue withdrawal caps are a hard ceiling on cross-exchange sizing.

## 9. Capital constraints

- Max capital at risk per leg is documented per category; default low
  (≤ 10%).
- Cross-venue strategies document expected capital lock-up and ramp.
- **No leverage in the first test.**

## 10. Execution feasibility checklist

- Is the displayed price actually executable at the size we want?
- Do all legs fire close enough in time to make the snapshot meaningful?
- Are fees + spreads + slippage + transfer costs already inside the
  expectancy number?
- Have we written down the stress scenario AND deducted it from expectancy?
- Is there a clear, written kill condition before any data run?
- Have we declared venue, clock, OOS window, sizing limit?

## 11. Risk checklist

- Stale-quote illusion; visible book has already moved.
- Withdrawal freeze / venue outage during the round-trip.
- Counterparty / custody risk concentrated on one venue.
- Liquidation cascade in spot-perp or pair trades.
- Roll / settlement dislocation in futures-calendar trades.
- Cointegration break / regime change in relative-value trades.
- Regulatory / jurisdiction shock.
- Operational / API risk during the trade window.
- Tail risk in low-frequency, high-magnitude events not visible in baseline.

## 12. Validation phases

| Phase | Purpose |
|---|---|
| `P0_protocol` | **This bundle.** Lock language, scope, costs, kill rules. No data, no run. |
| `P1_data_contract` | For any category we want to test next: author its data contract (venues, fields, clock, fee tier, frozen window). Still no data pull. |
| `P2_data_acquisition` | Acquire frozen historical data only, behind its own explicit authorization. No live fetch. |
| `P3_offline_replay` | Run the minimum viable test offline on the frozen IS window with full cost + stress model. |
| `P4_holdout_oos` | Apply the same rule, unchanged, to the sealed OOS window. **No re-tuning.** |
| `P5_decision_gate` | PASS / WATCH / FAIL / PARK / RETIRE per the rules below. |
| `P6_periodic_review` | If WATCH or ACTIVE, schedule a periodic re-test. Still no live. |
| `P_NONE_live_or_paper` | **Live trading and paper-order execution are NOT phases of this protocol.** They require a SEPARATE, independent authorization with a different protocol. |

## 13. Pass / Watch / Fail rules

- **PASS** — IS shows positive expectancy after the full cost + stress model
  with non-overlapping confidence intervals; OOS confirms direction and
  magnitude within a pre-registered tolerance; no kill condition triggered;
  no rule was changed mid-study.
- **WATCH** — IS shows positive expectancy after costs, but stress overlay
  shrinks it materially OR OOS magnitude is meaningfully smaller than IS.
  Lane is documented and re-checked, never live-traded.
- **FAIL** — IS expectancy is not positive after full cost + stress, OR OOS
  contradicts IS sign, OR any kill condition triggered.
- **PARK** — FAIL but the failure mode is informative; document and move on;
  do not re-run with tweaks on the same data.
- **RETIRE** — Failure mode is structural; category does not work for
  SPARTA's constraints.

## 14. Kill conditions

- Any single stress scenario (venue outage, funding flip, liquidation, roll
  dislocation) eats more than N months of estimated edge under the cost
  model.
- Backtest cannot be reproduced bit-for-bit by a second offline run.
- Data contract was changed mid-study to make the result pass.
- An assumption (no-spread, no-latency, no-counterparty-haircut,
  no-withdrawal-fee) is found to have been silently dropped.
- The strategy depends on data the operator cannot legally / technically
  acquire.
- Expectancy after full costs is statistically indistinguishable from zero.

## 15. Required reports for future implementation

- Per-category **data contract memo** (no data pulled).
- **Cost model** (JSON or spreadsheet) with maker, taker, spread, slippage,
  funding, borrow, withdrawal latency, counterparty haircut.
- **Stress overlay scenarios** (≥ 1 per category) with quantified PnL
  deduction.
- **Pre-registered IS / OOS windows and tolerances**, sealed before any run.
- **Backtest report.json + report.md** per category, with PASS / WATCH /
  FAIL verdict and reasoning.
- **Lane closeout memo** when a category PARKs / RETIREs.

## 16. Safety boundaries (pinned, non-negotiable)

- Research-only. Protocol/specification only.
- No broker control, no exchange connection, no API keys, no .env, no
  credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in this
  protocol's runtime.
- **No data fetch in this bundle.** Data acquisition is a SEPARATE,
  explicitly authorized bundle (P2).
- Do not modify paper / live execution files (sealed in earlier bundles).
- Do not claim profitability. Do not claim live-readiness. Do not claim
  STRONG evidence from this protocol alone.
- Apparent edge ≠ profit. Pure arbitrage is rare. Default assumption is that
  apparent edges vanish under realistic costs.

## 17. Non-profitability pledges

- This protocol does **not** assume any arbitrage category is profitable.
- This protocol does **not** claim SPARTA has an arbitrage edge.
- This protocol does **not** authorize a bot, an order, an exchange
  connection, or a data fetch.
- This protocol does **not** promote any category to ACTIVE or STRONG by its
  existence; a category remains IDEA / PARKED / WATCH until evidence
  justifies otherwise.

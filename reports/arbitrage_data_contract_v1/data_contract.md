# SPARTA Arbitrage Data Contract v1

> **Research-only. Data contract / specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls and no data fetch in this
> bundle.** This document is the written input spec that any future,
> separately-authorized data-acquisition bundle (Arbitrage Research Protocol
> v1, phase **P2**) must satisfy.

**Data contract id:** `arbitrage_data_contract_v1` · **version:** `1.0`

**Companion document:** [`arbitrage_research_protocol_v1`](../arbitrage_research_protocol_v1/protocol.md).

---

## 1. Research objective

Define exactly what data would be required to later test the five Arbitrage
Research Protocol v1 categories. This contract does not fetch data, does not
connect to any exchange, does not establish any data feed, and does not
authorize trading. Its purpose is to make any future data-acquisition step
**impossible to start without** first having a complete, written input spec.

## 2. Data requirements by arbitrage category

### A. Cross-exchange spot arbitrage

- Synchronized **bid/ask quotes** (L1, optionally L2) on the SAME UTC clock
  for both venues, with documented per-venue clock skew.
- Venue **fee schedules** (maker / taker / volume-tier overrides).
- **Spread** series at quote time (best_bid, best_ask, mid, microprice if
  available).
- **Depth at the test size** (cumulative notional / quantity at the touch
  and at +1 to +5 ticks).
- **Withdrawal / deposit constraints**: min amount, daily cap, fees,
  networks accepted.
- **Transfer delay assumptions**: conservative (slow-day) latency, per
  asset and per network.
- **Asset / network compatibility** between the two venues.

Row is invalid if: either venue's quote is missing on the aligned
timestamp; depth at test size is unavailable; the asset / network is not
transferable between the venues.

### B. Spot-perp basis / funding arbitrage

- **Spot bid/ask** aligned with the perp's mark/index timestamps.
- **Perp bid/ask** (mark price, index price, last-traded).
- **Funding-rate history** per venue (rate, timestamp, settlement period,
  predicted vs. realized if distinguishable).
- **Funding timestamp schedule** (e.g., every 8h, UTC).
- **Borrow / margin** constraints if the short leg requires borrow.
- **Liquidation rules**: maintenance margin, liquidation-engine model,
  partial vs. full liquidation behaviour.
- **Basis calculation inputs**: how mark / index are computed.

Row is invalid if: funding settlement-period boundaries are missing; the
perp's mark/index source changed mid-window without disclosure; borrow
availability cannot be confirmed.

### C. Triangular arbitrage

- **Three synchronized pair quote streams** on a single venue sharing one
  UTC clock at sub-second resolution.
- **Bid/ask** for each leg + documented quote-update rate per pair.
- **Taker fees** per leg (and maker fees per leg if the protocol's MVT
  permits maker fills).
- **Minimum order sizes** per pair (notional and quantity).
- **Precision / rounding rules** per pair (tick / lot).
- **Depth per leg** at the test size.
- **Execution sequence assumptions**: which leg first, expected slippage
  by the time leg N is sent.

Snapshot is invalid if: any of the three legs is older than the max age
(default **250 ms**); any leg's quote is missing or zero-bid/ask;
top-of-book size is below the configured min-fill on any leg.

### D. Futures calendar / basis arbitrage

- **Front- and next-month contract quote series** with explicit roll dates
  + roll method (open-interest / volume / calendar).
- **Expiry calendar** per contract (last trading day, settlement date,
  method).
- **Contract multiplier** and **tick size** per contract.
- **Roll schedule** (which days the operator's protocol would have rolled).
- **Margin assumptions** (initial + maintenance) per contract per venue.
- **Carry / funding / cost-of-capital** assumptions used to compute fair
  basis.

Row is invalid if: contract multiplier or tick size is missing; the roll
method on a roll day is not documented; expiry calendar disagrees with the
cited venue source.

### E. Statistical / relative-value mispricing (**NOT pure arbitrage**)

- **Historical aligned price series** for both legs (close-to-close OR
  intraday at the documented bar size).
- **Spread / z-score definitions** (log-ratio, beta-adjusted spread,
  distance-from-rolling-mean, etc.).
- **Correlation / stationarity / cointegration** diagnostics over the
  **IS** window only.
- **Regime labels** if regime gating is part of the strategy spec.
- **Transaction-cost assumptions** (fees, spread, slippage, borrow on the
  short leg).
- **Explicit note** in every downstream artifact: this category is
  **RELATIVE_VALUE**, not ARBITRAGE.

Row is invalid if: legs are not aligned to the same bar timestamp; any
diagnostic was computed on OOS data (look-ahead); a corporate-action / fork
event has no documented adjustment.

## 3. Timestamp and synchronization rules

- **Primary clock:** UTC, monotonic, ISO-8601.
- **Accepted timestamp fields** (in preference order):
  `exchange_send_ts` → `exchange_recv_ts` → `venue_match_ts` (trade
  prints). `local_recv_ts` is **always recorded** but is **never the sole
  timestamp**.
- **Exchange vs. local skew:** document per-venue skew; report the rolling
  distribution, not just a single number.
- **Max skew allowed:** default **250 ms** for cross-venue and triangular
  studies; tighter for studies that depend on top-of-book convergence.
- **Stale-quote rule:** a quote is stale if its exchange timestamp is older
  than `max_skew_allowed + venue_publish_interval`.
- **Alignment rules:**
  - Cross-venue: align by `exchange_send_ts` when available; never align
    last-trade vs. mid-quote across venues.
  - Triangular: all three legs share the same source clock at sub-second
    resolution.
  - Spot-perp: align spot to perp's mark/index timestamp; do not mix
    venues unless explicitly documented.
- **Timezone normalization:** all stored timestamps UTC; any source in
  local time converted at ingest with original timezone preserved as
  metadata.
- **Bar aggregation (if later used):** documented bar size; time-bar vs.
  tick-bar vs. volume-bar; left-closed / right-open by default; bars must
  not mix venues.
- **Row invalidity:** missing primary timestamp; exchange timestamp older
  than publish-interval + max skew; exchange timestamp ahead of UTC wall
  clock; duplicate primary timestamp without sequence number; row spans a
  documented exchange outage without an outage flag.

## 4. Cost model requirements

- **Maker / taker fees per venue per instrument-class.** Default sizing
  uses **taker**. Lowest realistic tier (not best-case).
- **Spread cost:** at least 1 tick / 1 bp per leg on top of fees, larger
  on illiquid pairs.
- **Slippage model:** depth-aware (test fill must consume the depth it
  needs); conservative (not best-case) on illiquid windows.
- **Funding payments:** spot-perp tests carry funding as a distinct PnL
  line, never netted silently.
- **Borrow costs:** short-leg pair trades must include an explicit borrow
  proxy.
- **Withdrawal / deposit fees:** per asset per network.
- **Network fees:** crypto on-chain gas / network distribution recorded.
- **Transfer-delay risk:** the slowest leg defines the risk window;
  the latency haircut is conservative.
- **Capital lockup:** cross-venue strategies disclose expected capital
  lockup and ramp.
- **Tax / accounting:** ignored for research, **explicitly noted** as a
  real-world issue that further reduces realized edge.

## 5. Liquidity / depth requirements

- **Minimum notional depth at touch** documented per category per venue
  per pair.
- **Depth-at-size:** cumulative size from best bid/ask up to the test
  size; never assume infinite liquidity at the quote.
- **Volume filter:** pair-level minimum 24h volume threshold per
  category; below threshold = excluded from MVT.
- **Stale order-book filter:** L2 snapshot older than max-skew at decision
  time excluded.
- **Quote-flicker filter:** recurring multi-tick flicker on a single side
  within a sub-second window is flagged.
- **Exchange downtime / outage flags:** first-class boolean column, not
  inferred from gaps.
- **Suspicious data flags:** `depth_collapse`, `spread_widening_spike`,
  `trade_print_without_corresponding_book_change`, `post-outage_first_minute`.

## 6. Order-book / trade-print / quote requirements

- Order book: L1 minimum, L2 (5-10 levels) preferred. Fields per level
  `price / size / side / level_index`. Snapshot or snapshot+delta with a
  re-sync rule. Missing-side rows invalid. Zero/negative-price rows
  invalid. Crossed top-of-book flagged.
- Trade prints: `price / size / side_if_signed / venue_match_ts`. Aggressor
  side recorded iff venue exposes it; otherwise unknown — never inferred
  for arbitrage MVTs. Self-trades filtered if identifiable. Block /
  OTC prints flagged separately.
- Quotes: minimum update frequency documented; quote-flicker filter on;
  any quote older than max-skew at decision time excluded.

## 7. Data quality and normalization

- **Duplicates** removed on `(instrument_id, primary_ts, sequence_no_if_present)`;
  duplicates without sequence number are invalid.
- **Missing values:** never silently forward-filled; gaps preserved with
  explicit flags.
- **Out-of-order:** strictly monotonic by primary timestamp; OOO rows
  flagged.
- **Outliers** identified by venue/asset-specific rules; flagged not
  dropped.
- **Reproducibility:** same raw inputs + same code + same contract version
  → bit-for-bit identical processed dataset.
- **Provenance:** every row carries a source identifier and contract
  version; never anonymous.
- Normalization: documented currency, symbol canonicalization, tick/lot
  rounding, stitching for continuous contracts, split/dividend adjustment
  for equities (raw + adjusted both stored).

## 8. Minimum viable dataset (per-category)

- IS window disclosed BEFORE any run.
- OOS window SEALED BEFORE any run.
- Warmup buffer documented.
- Fee schedule attached.
- Outage calendar attached.
- Provenance metadata per row.

Per-category minima are inherited from §2.

## 9. Future allowed data sources

- Existing on-disk frozen historical files already in SPARTA's research
  tree (no network).
- A future, separately-authorized **data-acquisition bundle (P2)** which
  ships its own contract addendum and explicit authorization.
- Operator-supplied paid-vendor exports that **do not** require a live API
  connection from SPARTA's runtime (vendor pushes files; SPARTA reads them
  offline).

## 10. Forbidden data sources / methods

- Live exchange APIs from this contract's runtime.
- Scraping any venue HTML / WebSocket / undocumented endpoint.
- Any source requiring an embedded API key, OAuth token, or `.env`
  credential.
- Any source that requires SPARTA to make a network call from its runtime.
- Synthetic / mock-priced data in place of real history.
- Any dataset whose provenance cannot be cited line-by-line.
- Any dataset whose OOS window was peeked before sealing.
- Any feed whose terms of service forbid research use.

## 11. Required future artifacts

- Per-category **data acquisition memo** (names venue(s), pairs, fee tier,
  withdrawal-latency assumption, IS/OOS windows, storage path) BEFORE any
  data pull.
- Per-category **data integrity report** (row counts, gap stats, outage
  overlap, fee schedule attached, contract version pinned).
- Per-category **cost model snapshot** sealed before any IS run.
- Per-category **stress overlay scenarios** (≥1) with quantified PnL
  deduction.
- **Backtest report.json + report.md** per category, with PASS / WATCH /
  FAIL verdict against the Arbitrage Research Protocol v1 rules.
- **Lane closeout memo** for any category that PARKs / RETIREs.

## 12. PASS / WATCH / FAIL rules

- **PASS** — All required sections of this contract present for the
  category under test; data integrity report has zero unresolved flags;
  fee + funding + cost-of-capital lines non-null and sourced; IS/OOS
  windows sealed before any run.
- **WATCH** — Contract satisfied but at least one liquidity / latency /
  coverage assumption is borderline; the lane is documented and re-checked
  before any further phase.
- **FAIL** — Any required section missing; any forbidden data source used;
  any safety flag True; any OOS window peeked; reproducibility check fails.

## 13. No-profit-claim policy

- A price gap is **not** profit.
- Any future test must subtract all known costs.
- Any future test must include conservative (not best-case) slippage.
- Any future result is invalid if it ignores fees, latency, liquidity, or
  funding.
- This contract does **not** authorize trading.
- This contract does **not** authorize an exchange connection.
- This contract does **not** promote arbitrage to ACTIVE / STRONG by its
  existence.

## 14. Safety boundaries (pinned, non-negotiable)

- Research-only. Data contract / specification only.
- No broker control, no exchange connection, no API keys, no .env, no
  credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in this
  contract's runtime.
- **No data fetch in this bundle.** Data acquisition is a SEPARATE,
  explicitly authorized bundle (Arbitrage Research Protocol v1, P2).
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not claim
  STRONG evidence from this contract alone.
- A price gap is not profit. Apparent edge ≠ profit.

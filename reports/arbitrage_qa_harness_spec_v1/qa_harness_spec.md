# SPARTA Arbitrage QA Harness Spec v1

> **Research-only. QA harness specification only.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> background daemon. **No external network calls. No data fetch. No backtest.
> No dataset processing in this bundle.** This document is the written input
> spec that any future, separately-authorized QA harness implementation MUST
> satisfy.

**QA harness spec id:** `arbitrage_qa_harness_spec_v1` · **version:** `1.0`

**Companion documents:**
[`arbitrage_research_protocol_v1`](../arbitrage_research_protocol_v1/protocol.md) ·
[`arbitrage_data_contract_v1`](../arbitrage_data_contract_v1/data_contract.md) ·
[`arbitrage_dataset_manifest_v1`](../arbitrage_dataset_manifest_v1/dataset_manifest.md).

---

## 1. Research objective

Define exactly how a **future** QA harness must check any future arbitrage
dataset + per-dataset manifest **before** a research test is allowed to use
it. This spec does not fetch data, does not connect to any exchange, does
not process datasets, does not run a backtest, and does not authorize
trading.

## 2. Required inputs

- Frozen on-disk dataset (no network).
- Per-dataset manifest file satisfying
  `arbitrage_dataset_manifest_v1.manifest_schema.required_future_manifest_fields`.
- Pinned **Arbitrage Data Contract v1** version reference.
- Pinned **Arbitrage Research Protocol v1** version reference.
- QA configuration (`max_skew_allowed_ms`, `max_snapshot_age_ms`,
  `depth_at_size`, `volume_filter`, outlier thresholds) — all pre-declared,
  no auto-tuning during a run.

## 3. Forbidden inputs

- Live exchange APIs at QA-run time.
- Any source requiring an embedded API key, OAuth, or `.env` credential at
  QA-run time.
- Scraping any venue HTML / WebSocket / undocumented endpoint.
- Network URLs in dataset `source_location`.
- Datasets without a manifest.
- Datasets whose manifest fails `arbitrage_dataset_manifest_check`.
- Synthetic / mock-priced data presented as historical (`source_type`
  `synthetic_diagnostic_only_NOT_FOR_BACKTEST` is allowed only when QA
  explicitly logs it; it cannot reach **QA_PASS**).
- Datasets whose OOS window was peeked before sealing.

## 4. QA check groups

### A. Manifest integrity
- Every required manifest field present and non-empty (except `notes`).
- `dataset_id` present, canonical, never reused.
- `dataset_version` present (monotonically increasing integer).
- Data Contract version referenced.
- Research Protocol version referenced.
- `freeze_status` present (must be **FROZEN** before QA_PASS).
- `qa_status` field exists; harness will populate.
- `allowed_use` includes `research_only`; never `live_trading` /
  `paper_order_execution` / `broker_control` / `exchange_connection`.
- `forbidden_use` explicitly forbids the four execution modes above.
- Source provenance present (`source_type`, `source_location`,
  `ingest_pipeline_version` non-null).
- Checksum policy present (sha256 or stronger; per-file verifiable on
  FROZEN).

### B. Timestamp and synchronization
- `exchange_send_ts` / `exchange_recv_ts` / `venue_match_ts` available per
  row.
- `local_recv_ts` recorded if available, never sole.
- Timezones normalized to UTC; original tz preserved as metadata.
- Per-venue skew within `max_skew_allowed`.
- Stale-quote rule enforced
  (`max_skew_allowed + venue_publish_interval`).
- Duplicates removed on `(instrument_id, primary_ts, sequence_no_if_present)`;
  duplicates without sequence number are **INVALID**.
- Primary timestamp strictly monotonic per `instrument_id`; OOO flagged.
- Cross-venue / triangular tests share one aligned timestamp source at
  sub-second resolution.

### C. Quote and spread
- `bid <= ask` on every L1 row.
- Non-negative spread.
- Spread outlier detection (`spread > N * rolling_median`).
- Stale-quote detection.
- Quote-flicker detection (recurring multi-tick flicker within sub-second).
- Missing-side handling (any row missing bid or ask is **INVALID**).
- Crossed-market handling (`bid >= ask` flagged; excluded from MVT unless
  strategy explicitly handles it).

### D. Order book / depth
- L1 mandatory; L2 (≥5 levels) for any depth-at-size test.
- Depth-at-size = cumulative size from best bid/ask up to the test size.
- Any level with `size <= 0` is **INVALID**.
- Book-imbalance warning on extreme one-sided book.
- Stale-order-book detection.
- Crossed-book flag.

### E. Trade prints
- `price > 0` and `size > 0`.
- Outlier-print detection (`price` deviates from rolling-mid by
  `> M * spread`).
- Quote/trade alignment (trade `venue_match_ts` aligned to a contemporaneous
  quote-book snapshot).
- Duplicate `trade_id` removal where exposed.
- Block / OTC prints flagged separately.

### F. Fee / funding / cost
- `maker_fee_bps` + `taker_fee_bps` per `(venue, instrument-class)` non-null.
- Funding `settlement_ts` present for spot-perp rows.
- Funding `rate` + `interval` present for spot-perp rows.
- Withdrawal / deposit fee references per asset per network non-null.
- Network fees reference present (crypto on-chain gas distribution).
- **Cost fields non-null before any future edge claim** — no future PnL
  number is permitted without fees + spread + slippage + funding/borrow
  lines.

### G. Liquidity and latency
- Minimum notional depth per category per venue per pair met.
- Per-pair 24h volume filter met (QA config).
- Exchange downtime / outage flags present as a first-class column.
- Latency / skew warning (`exchange_send_ts` vs. `local_recv_ts`
  > `max_skew_allowed` triggers **WARN**).
- Suspicious venue-state column populated when present
  (`depth_collapse` / `spread_widening_spike` /
  `trade_print_without_book_change` / `post-outage_first_minute`).

### H. Anomaly detection
- Depth-collapse detection (sudden zero-size at touch).
- Spread-widening spike detection.
- Trade-print-without-book-change detection.
- Post-outage first-minute exclusion (unless strategy explicitly handles).
- Regime-break detection (statistical_relative_value only).

### Category-specific checks
- **A. Cross-exchange spot** — venue pair clock alignment; synced L1
  coverage; depth-at-test-size; withdrawal-latency assumption attached;
  fee schedule attached; asset/network compatibility.
- **B. Spot-perp basis / funding** — funding timestamp alignment; funding
  rate completeness; perp contract specs attached; liquidation-risk notes
  attached; spot-perp clock alignment.
- **C. Triangular** — 3-leg pair mapping; snapshot age ≤
  `max_snapshot_age_ms` (default 250); per-leg taker fee attached;
  per-leg precision; per-leg depth; leg sequence assumption.
- **D. Futures calendar** — expiry calendar; multiplier; roll calendar;
  margin + carry assumptions; venue source pin.
- **E. Statistical / relative-value (NOT pure arbitrage)** — aligned bar
  check; spread definition; IS-only diagnostics; regime label definition;
  **explicit `RELATIVE_VALUE` (not ARBITRAGE) label** on every downstream
  artifact; corporate-action adjustment for equities.

## 5. QA status model

| Status | When it applies |
|---|---|
| **QA_DRAFT** | Harness has not yet been run on this `dataset_version`. NOT research-usable. |
| **QA_PASS** | Every blocking check passed. Zero unresolved WARNs (or every WARN has an explicit operator-acceptance note). Row counts match (or a documented gap). Manifest FROZEN with valid checksums. Research-usable. **QA_PASS does NOT imply profitability, does NOT prove edge, and does NOT authorize backtesting, paper trading, or live trading.** |
| **QA_WARN** | Every blocking check passed but ≥1 non-blocking WARN unresolved. Research-usable **only** after an explicit operator-acceptance memo per `dataset_version`. The memo names the WARN, why acceptable, the limit imposed. |
| **QA_FAIL** | ≥1 blocking check failed (missing field, broken checksum, crossed book everywhere, manifest invalid, peeked OOS, etc.). NOT research-usable until cause is fixed AND a new `dataset_version` is produced. |
| **QA_BLOCKED** | Externally blocked (legal / TOS / vendor). Cannot proceed regardless of harness output. |
| **QA_RETIRED** | Operator-retired. History preserved for traceability; cannot be re-promoted to QA_PASS. |

### Hard rules
- **QA_PASS does NOT imply profitability.**
- **QA_PASS does NOT authorize backtesting.**
- **QA_PASS does NOT authorize paper or live trading.**
- **QA_FAIL blocks research use.**
- **QA_WARN requires explicit operator-acceptance memo before any research use.**

## 6. Report schema (every future QA report must contain)

`qa_report_id` · `dataset_id` · `dataset_version` · `manifest_version` ·
`data_contract_version` · `generated_at` · `qa_status` · `checks_run` ·
`checks_passed` · `checks_warned` · `checks_failed` · `blocking_failures` ·
`warnings` · `row_count_observed` · `missing_data_summary` ·
`timestamp_summary` · `quote_summary` · `fee_funding_summary` ·
`liquidity_summary` · `category_specific_summary` · `allowed_next_step` ·
`forbidden_next_steps` · `safety_flags`.

`safety_flags` pinned False in every QA report: `live_trading_enabled`,
`broker_control_enabled`, `paper_order_execution_enabled`,
`exchange_connection_enabled`, `data_fetch_enabled`, `backtest_enabled`.

## 7. PASS / WATCH / FAIL rules (for THIS spec)

- **PASS** — All required top-level sections present; all 8 QA check groups
  documented; all 5 categories carry category-specific checks; QA status
  model contains all 6 statuses; report schema lists all required future
  QA report fields; no safety flag True; no forbidden phrase appears.
- **WATCH** — Spec satisfied but ≥1 section is borderline (e.g., an
  anomaly threshold is loose); documented and re-checked.
- **FAIL** — Any required section missing; any safety flag True; any QA
  status missing; any required future QA report field absent; any
  forbidden phrase present.

## 8. Required future artifacts

- QA harness implementation that satisfies this spec (separately
  authorized; stdlib-only or pinned-dependency only; no network at
  runtime).
- Per-`(dataset_id, dataset_version)` QA report file satisfying the report
  schema.
- Per-WARN operator-acceptance memo (when QA_WARN is accepted as
  research-usable).
- Per-FAIL remediation memo OR a new `dataset_version` that addresses the
  failure.
- Retirement memo when QA_RETIRED transitions in.

## 9. No-profit-claim policy

- **QA is not strategy validation.**
- QA does not prove edge.
- A clean dataset does not imply profit.
- A price gap is not profit.
- No QA artifact authorizes live trading, paper-order execution, or broker
  control.
- **QA_PASS does not authorize backtesting** — that is a separate,
  separately-authorized phase.

## 10. Safety boundaries (pinned, non-negotiable)

- Research-only. QA harness specification only.
- No broker control, no exchange connection, no API keys, no `.env`, no
  credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls in this
  spec's runtime.
- **No data fetch. No backtest. No dataset processing in this bundle.**
- Do not modify paper / live execution files.
- Do not claim profitability. Do not claim live-readiness. Do not claim
  STRONG evidence from this spec alone.
- A price gap is not profit. **QA is not strategy validation.** QA_PASS
  does not imply edge.

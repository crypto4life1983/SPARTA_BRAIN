# SPARTA Arbitrage Data Contract v1 — build report

> **Research-only. Data contract / specification only.** No broker, no live
> trading, no paper-order execution, no exchange connection, no API keys, no
> scheduler, no external network calls, **no data fetch in this bundle**.

## Files changed

| Path | Purpose |
|---|---|
| `reports/arbitrage_data_contract_v1/data_contract.json` | Machine-readable data contract (validator source of truth). |
| `reports/arbitrage_data_contract_v1/data_contract.md` | Human-readable contract: 5 categories of arbitrage data needs + timestamp / order-book / quote / fee / funding / liquidity / latency / quality / normalization / MVT / future-sources / forbidden-sources / future-artifacts / PASS-WATCH-FAIL / safety boundaries / no-profit-claim policy. |
| `reports/arbitrage_data_contract_v1/report.md` | This build report. |
| `reports/arbitrage_data_contract_v1/report.json` | Build report (machine). |
| `tools/arbitrage_data_contract_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_arbitrage_data_contract.py` | 16 tests covering schema, safety contract, integration. |
| `tools/strategy_candidate_registry.py` | `extra_files` extended to include the new data-contract docs for the arbitrage seed. Lane stays **IDEA** (never ACTIVE, never STRONG). |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 5 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 6 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper/live execution code in
`paper_trading/`, sealed data, `tools/arbitrage_protocol_check.py` (Bundle 4
validator unchanged; its existing `required_future_artifacts` list already
references the data-contract memo by name), `brain_memory/projects/trading_bot/lessons.md`.

## What the data contract defines

1. **Research objective** — what data would later be required to test the
   five Arbitrage Research Protocol v1 categories. Does not fetch, does not
   connect, does not authorize trading.
2. **Per-category data requirements** — for each of the five categories
   (`cross_exchange_spot`, `spot_perp_basis_funding`, `triangular`,
   `futures_calendar`, `statistical_relative_value` labelled **NOT pure
   arbitrage**): the exact field set, the validity rules that invalidate a
   row, and any category-specific clock/alignment requirements.
3. **Timestamp + synchronization rules** — UTC primary clock, accepted
   field hierarchy (`exchange_send_ts > exchange_recv_ts > venue_match_ts
   > local_recv_ts`), max skew (250 ms default), stale-quote rule,
   alignment rules (cross-venue / triangular / spot-perp), timezone
   normalization, bar-aggregation rules, row-invalidity criteria.
4. **Cost model requirements** — maker/taker fees, spread cost, slippage
   model, funding, borrow, withdrawal/deposit/network fees, transfer-delay
   risk, capital lockup; tax/accounting noted as a real-world issue beyond
   research.
5. **Liquidity / depth requirements** — minimum notional depth, depth-at-
   size calculation, volume filter, stale order-book filter, quote-flicker
   filter, outage flags, suspicious-data flags.
6. **Order-book / trade-print / quote requirements** — L1 minimum (L2
   preferred), required fields, snapshot-vs-delta rule, invalidation rules.
7. **Data-quality and normalization rules** — duplicate / missing /
   out-of-order / outlier handling; reproducibility; provenance per row;
   symbol canonicalization; continuous-contract stitching; split/dividend
   adjustment for equities.
8. **Minimum viable dataset** — IS/OOS sealed before run, warmup buffer,
   fee schedule attached, outage calendar attached, provenance metadata
   per row.
9. **Future allowed sources** — frozen on-disk files, a separately-
   authorized future data-acquisition bundle, operator-supplied paid-vendor
   exports that don't require a live network connection from SPARTA's
   runtime.
10. **Forbidden sources / methods** — live exchange APIs, scraping,
    embedded keys / OAuth / `.env`, runtime network calls, synthetic /
    mock-priced data, untraceable provenance, peeked OOS, forbidden TOS.
11. **Required future artifacts** — per-category acquisition memo,
    integrity report, cost-model snapshot, stress overlays, backtest
    report.json + report.md, lane closeout memo.
12. **PASS / WATCH / FAIL rules** + **safety boundaries** + **no-profit-
    claim policy** (price gap is not profit; conservative slippage
    mandatory; ignoring any cost invalidates a future result).

## Safety guarantees (enforced by tests)

- Five execution / fetch / connection flags pinned **False**:
  `data_fetch_enabled`, `exchange_connection_enabled`,
  `live_trading_enabled`, `broker_control_enabled`,
  `paper_order_execution_enabled`.
- `research_only: true` asserted.
- Statistical category self-labels **NOT pure arbitrage**; markdown carries
  the same word discipline.
- Validator scans both JSON and Markdown for forbidden capability claims
  (`guaranteed profit`, `risk-free profit`, `live-ready`, `production-
  ready`, `place the order`, `connect to exchange`, etc.).
- Tool is **stdlib-only** (AST scan). No `requests`, `urllib`, `socket`,
  `ssl`, `tiingo`, `ccxt`, `alpaca`, `binance`, `dotenv`, `subprocess`,
  `os.environ`, `getenv`, `urlopen`.

One validator nuance applied: `live api connection` is **intentionally not
in the forbidden-phrase list** because it only ever appears in safety
language (e.g., *"DO NOT require a live API connection"*). The remaining 11
phrases cover the actual capability claims that must never appear.

## Tests run

```bash
python -m pytest tests/test_arbitrage_data_contract.py tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 75 passed in 0.79s
```

- `test_arbitrage_data_contract.py` — **16 new tests** (Bundle 5).
- `test_arbitrage_research_protocol.py` — 14 (Bundle 4); still pass.
- `test_strategy_candidate_registry.py` — 16 (Bundle 3); still pass.
- `test_strategy_next_bundle.py` — 24 (Bundle 2); still pass.

## JSON validity

```
python tools/arbitrage_data_contract_check.py validate   → validate: OK
python tools/arbitrage_protocol_check.py validate        → validate: OK
python tools/strategy_candidate_registry.py validate     → validate: OK
python tools/strategy_next_bundle.py validate            → validate: OK
```

## How this fits after Arbitrage Research Protocol v1

```
Arbitrage Research Protocol v1  (30dabc4)  ← phase P0_protocol
        ↓
Arbitrage Data Contract v1      (this bundle)  ← phase P1_data_contract
        ↓
(separate bundles, separately authorized)
   Arbitrage Dataset Manifest v1  →  Arbitrage QA Harness Spec v1  →  P2 data acquisition  →  …
```

The contract is the input spec that any future data-acquisition bundle
(Protocol P2) MUST satisfy before any pull is authorized.

## Candidate registry status for arbitrage after build

- **status:** `IDEA` ✅ (unchanged — the new docs contain only "data" /
  "protocol" keywords, no `failed_`/`closeout`/`retire` triggers)
- **evidence_level:** `MIXED` (4 matched documents now; no test/baseline/
  OOS evidence; explicitly cannot reach `STRONG`)
- **source_reports:** `["data_contract.json", "data_contract.md",
  "protocol.json", "protocol.md"]`
- **next_action:** *"Claude/Codex: arbitrage data-contract bundle"* (from
  the queue's `next_bundle_suggestion`; will be naturally superseded once
  the queue evolves)

## Next-bundle generator selected bundle after update

**Still selects "Arbitrage research protocol"** (lane=
`arbitrage_research_protocol`, priority=3). Deterministic logic was not
artificially modified; the queue at HEAD doesn't yet include a "Dataset
Manifest" or "QA Harness Spec" item, so the existing protocol/data-first
scoring axes still rank arbitrage at the top.

## Recommended next bundle

Per the contract's own phase ladder, the natural next steps (each its own
separately-authorized bundle) are:

1. **Arbitrage Dataset Manifest v1** — for ONE category at a time, name
   the venue(s), pairs, fee tier, withdrawal-latency assumption, IS/OOS
   windows, and storage path. Spec only; **no data pull**.
2. **Arbitrage QA Harness Spec v1** — define the harness that will verify
   the future acquired dataset against this contract (row-count checks,
   gap-stats, outage overlap, provenance pin, contract-version pin).
3. **Crypto-D1 Protocol Memo** — alternative lane (currently PARKED with
   closeout memo); would require a NEW hypothesis, not a re-tune.

All three are read-only specs; **none of them** authorize data fetch,
broker connection, or execution.

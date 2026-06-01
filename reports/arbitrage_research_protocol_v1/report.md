# SPARTA Arbitrage Research Protocol v1 — build report

> **Research-only. Protocol/specification only.** No broker, no live trading,
> no paper-order execution, no exchange connection, no API keys, no scheduler,
> no external network calls, **no data fetch in this bundle**.

## What was built

| Path | Purpose |
|---|---|
| `reports/arbitrage_research_protocol_v1/protocol.json` | Machine-readable protocol spec (validator's source of truth). |
| `reports/arbitrage_research_protocol_v1/protocol.md` | Human-readable protocol document (definitions, 5 categories, costs, risks, phases, kill conditions). |
| `reports/arbitrage_research_protocol_v1/report.md` | This build report. |
| `reports/arbitrage_research_protocol_v1/report.json` | Build report in machine-readable form. |
| `tools/arbitrage_protocol_check.py` | Stdlib-only validator with `validate / show` CLI. |
| `tests/test_arbitrage_research_protocol.py` | 14 tests covering protocol schema, distinction discipline, validator behaviour, registry integration. |
| `tools/strategy_candidate_registry.py` | Extended with per-seed `extra_files` so the SPARTA-side protocol docs are picked up as matched reports for the arbitrage lane (lane stays IDEA — never ACTIVE / never STRONG). |

**Not touched:** `app.py`, `templates/*.html`, paper/live execution code in
`paper_trading/`, sealed data, `brain_memory/projects/trading_bot/lessons.md`.

## What the protocol defines

1. **Research objective** — lock in the rules SPARTA will follow if/when it
   studies arbitrage. No bot, no data fetch, no exchange connection.
2. **Definitions** — *pure arbitrage* vs. *apparent edge ≠ profit* vs.
   *statistical relative-value* (not arbitrage). Word discipline enforced
   downstream.
3. **Five categories in scope** — (A) cross-exchange spot, (B) spot-perp
   basis / funding, (C) triangular, (D) futures calendar / basis, (E)
   statistical / relative-value (explicitly labelled **NOT pure arbitrage**).
   Each category carries: hypothesis, data needed, minimum viable test, main
   costs, main risks, likely feasibility, why it may fail, first safe
   research step.
4. **Out of scope** — tax-arb, stablecoin de-peg, DeFi flash-loans, OTC,
   predictive strategies dressed up as "arbitrage", any live-order or
   live-data path.
5. **Data / venue / cost / liquidity / capital requirements** — frozen data
   only, explicit clock, synchronous snapshot rule, OOS seal, fee/spread/
   funding/latency/counterparty haircut all mandatory.
6. **Execution feasibility & risk checklists** — written-down stress
   scenarios; expectancy after costs only counts when stress is deducted.
7. **Validation phases** — `P0_protocol` (this bundle) → `P1_data_contract`
   → `P2_data_acquisition` → `P3_offline_replay` → `P4_holdout_oos` →
   `P5_decision_gate` → `P6_periodic_review`. **Live/paper-order execution
   is `P_NONE` — not a phase of this protocol.**
8. **PASS / WATCH / FAIL / PARK / RETIRE rules** with kill conditions.
9. **Required future artifacts** — what each downstream category must
   produce before any pass claim.
10. **Safety boundaries + non-profitability pledges** — pinned, non-negotiable.

## Safety guarantees (enforced by tests)

- Five execution flags pinned `False`: `live_trading_enabled`,
  `broker_control_enabled`, `paper_order_execution_enabled`,
  `exchange_connection_enabled`, `data_fetch_enabled`.
- `research_only: true` asserted.
- Statistical category self-labels **NOT pure arbitrage**; markdown carries
  the same word discipline (`Pure arbitrage`, `NOT pure arbitrage`,
  `statistical_relative_value`, `Apparent edge`).
- Validator scans both JSON and Markdown for forbidden profitability / live
  phrases (`guaranteed profit`, `risk-free profit`, `live-ready`,
  `production-ready`, `place the order`, `connect to exchange`, etc.).
- Tool is **stdlib-only** (AST scan). No `requests`, `urllib`, `socket`,
  `ssl`, `tiingo`, `ccxt`, `alpaca`, `binance`, `dotenv`, `subprocess`,
  `os.environ`, `getenv`, `urlopen`.

## Tests run

```bash
python -m pytest tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 56 passed in 0.63s
```

- `test_arbitrage_research_protocol.py` — 14 new tests (this bundle).
- `test_strategy_candidate_registry.py` — 16 tests (pre-existing; still pass
  after `extra_files` registry extension).
- `test_strategy_next_bundle.py` — 24 tests (pre-existing + 2 lessons; still
  pass after registry extension).
- Two tests previously failing in Bundle 4 build (one validator gate bug)
  fixed during build; final run shows 56/56.

## JSON validity

```bash
python tools/arbitrage_protocol_check.py validate    → validate: OK
python tools/strategy_candidate_registry.py validate → validate: OK
python tools/strategy_next_bundle.py validate        → validate: OK
```

## How this fits into the SPARTA pipeline

```
Strategy Factory Routine Layer v1   (98f8918)
        ↓
JARVIS Strategy Factory Dashboard   (5fe3107)
        ↓
Next Bundle Generator v1            (a699198)
        ↓
Strategy Candidate Registry v1      (191948c)   ← arbitrage lane = IDEA
        ↓
Arbitrage Research Protocol v1      (this bundle, P0_protocol phase)
        ↓
(separate bundles, separate authorizations)
   P1_data_contract → P2_data_acquisition → P3_offline_replay → ...
```

The next bundle generator, when re-run after this bundle, still picks
**Arbitrage research protocol** as the highest-scoring queue item — but now
the lane has matched reports in the registry, so future selections will
account for the protocol's existence without claiming new evidence.

## Candidate registry status for arbitrage after build

- `status`: **IDEA** (unchanged — protocol/spec keyword keeps it IDEA, never
  ACTIVE, never STRONG)
- `evidence_level`: **MIXED** (matched reports exist on disk but no
  test/baseline/OOS evidence yet)
- `source_reports`: `["protocol.json", "protocol.md"]` (the new docs)
- `next_action`: *"Claude/Codex: arbitrage data-contract bundle"* (from the
  Routine Layer's queue suggestion)

## Recommended next bundle

Per the protocol's own phase ladder, the natural next step is **P1 —
Arbitrage Data Contract v1**: pick **one** of the five categories
(suggested: cross-exchange spot for clearest definitions, OR spot-perp
basis for cleanest single-venue starting point), author its data contract
(venues, pairs, clock, fee tier, withdrawal-latency assumption,
counterparty haircut, source of OFFLINE history), and seal the IS/OOS
windows. **Do not pull data in that bundle either** — data acquisition is
its own P2 bundle, also separately authorized.

Alternative Bundle 5 candidates from the broader SPARTA queue:
- **Crypto-D1 Protocol Memo** (lane is currently PARKED with a closeout
  memo; revisiting requires a new hypothesis, not a re-tune).
- **Data QA / freeze workflow** (cross-cutting; would benefit any category
  that ever moves past P0).

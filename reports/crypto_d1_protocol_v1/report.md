# SPARTA Crypto-D1 Protocol Memo v1 — build report

> **Research-only. Protocol / specification only.** No broker, no live
> trading, no paper-order execution, no exchange connection, no API keys,
> no scheduler, no external network calls, **no data fetch, no backtest,
> no dataset processing in this bundle**.

## Files changed

| Path | Purpose |
|---|---|
| `reports/crypto_d1_protocol_v1/protocol.json` | Machine-readable protocol (validator source of truth). |
| `reports/crypto_d1_protocol_v1/protocol.md` | Human-readable protocol: scope (BTC/ETH/SOL, spot only, daily only, 24/7 sessions), 7 candidate strategy families (mean-reversion WATCH-only), data + fee + slippage + risk requirements, 9-phase validation ladder P0..P8, PASS/WATCH/FAIL rules, kill conditions, no-profit-claim policy. |
| `reports/crypto_d1_protocol_v1/report.md` | This build report. |
| `reports/crypto_d1_protocol_v1/report.json` | Build report (machine). |
| `tools/crypto_d1_protocol_check.py` | Stdlib-only validator (`validate` / `show` CLI). |
| `tests/test_crypto_d1_protocol.py` | 21 tests covering schema, safety, registry integration. |
| `tools/strategy_candidate_registry.py` | Added `extra_files` + new `lane_status_override="WATCH"` to crypto_d1 seed; added per-seed override mechanism to `_build_candidate` that fires only when at least one of the seed's `extra_files` exists on disk; passed `repo_root` through. Crypto-D1 lane now classifies as **WATCH** (re-opened by the v1 memo) instead of PARKED. |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 11 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 12 candidate list. |

**Not touched:** `app.py` (pre-existing dirty modification from outside
this session — explicitly **not** staged), `templates/*.html`, paper/live
execution code, sealed data, all 8 prior arbitrage validators + docs,
`lessons.md`.

## What the Crypto-D1 protocol defines

1. **Lane scope.** Lane `crypto_d1_protocol`. Targets BTC / ETH / SOL.
   Spot only. Daily only. Perps / dated futures / options / leveraged
   tokens / margin spot are forbidden at this stage.
2. **Session model.** 24/7 crypto calendar. Weekday-only filters
   forbidden. Missing-day rules pre-declared (flagged, never silently
   forward-filled). UTC primary clock.
3. **Seven candidate strategy families** (define, not test): daily trend
   following, Donchian / channel breakout, moving-average trend filter,
   volatility regime gate, momentum continuation, simple risk-on/risk-off
   filter (all primary), **mean reversion (WATCH-only)**. Each carries a
   one-line summary + minimum-viable-test shape.
4. **Data requirements** for any future per-dataset manifest:
   OHLCV-daily, UTC timezone, 24/7 sessions, missing-day flagged,
   exchange/source provenance, symbol mapping, split/rename/fork/delisting
   handling, fee + slippage assumptions, stablecoin quote handling, data
   freeze, no-lookahead.
5. **Fee + slippage** defaults: taker on every leg, dated per-venue
   schedule pinned, fees as a distinct PnL line, depth-aware slippage
   when L2 is available.
6. **Risk assumptions:** no leverage in first test; equal-weight or
   pre-declared fixed-fraction sizing; pre-registered stops if any;
   pre-declared drawdown limits; tail-risk disclosure.
7. **Nine validation phases** P0..P8:
   - **P0** protocol (this bundle)
   - **P1** data contract / source selection (spec only)
   - **P2** dataset manifest + data freeze (separately authorized)
   - **P3** baseline strategy implementation
   - **P4** IS/OOS split sealed before any run
   - **P5** walk-forward / rolling validation
   - **P6** robustness + sensitivity
   - **P7** paper-signal **simulation only** (separately authorized)
   - **P8** live trading **explicitly out of scope** for this stack
8. **PASS / WATCH / FAIL rules** + **kill conditions** + **required
   future artifacts** + **no-profit-claim policy** + **safety
   boundaries**.

## Safety guarantees (enforced by tests)

- **Seven** execution / fetch / connection / backtest / dataset-processing
  flags pinned **False**: `data_fetch_enabled`,
  `exchange_connection_enabled`, `live_trading_enabled`,
  `broker_control_enabled`, `paper_order_execution_enabled`,
  `backtest_enabled`, `dataset_processing_enabled`.
- `research_only: true` asserted.
- Target assets MUST include BTC, ETH, SOL (validator scans canonical
  symbols).
- `allowed_market_type` MUST be `spot`; perp / dated_futures / options /
  leveraged are in `forbidden_market_types`.
- Timeframe is `1d`; `intraday_explicitly_out_of_scope=True`.
- Session model declares `24/7` calendar; weekday-only filters
  forbidden; missing-day policy required.
- `mean_reversion` strategy family carries `status=WATCH_only`.
- All 9 validation phases P0..P8 present.
- MD carries `Crypto trend ideas are not profitable until tested`,
  `A good historical chart does not imply future returns`, `No backtest
  is authorized by this protocol alone`, `24/7`.
- Validator scans MD + JSON for forbidden capability claims (`guaranteed
  profit`, `risk-free profit`, `live-ready`, `production-ready`, `place
  the order`, `connect to exchange`, `fetch live data`, etc.).
- Tool is **stdlib-only** (AST scan; only `argparse`, `json`, `pathlib`,
  `__future__`). No `requests`, `urllib`, `socket`, `ssl`, `tiingo`,
  `ccxt`, `alpaca`, `binance`, `dotenv`, `subprocess`, `os.environ`,
  `getenv`, `urlopen`.

## Tests run

```bash
python -m pytest tests/test_crypto_d1_protocol.py tests/test_arbitrage_readiness_gate.py tests/test_arbitrage_sample_dataset_plan.py tests/test_arbitrage_data_source_evaluation.py tests/test_arbitrage_qa_harness_spec.py tests/test_arbitrage_dataset_manifest.py tests/test_arbitrage_data_contract.py tests/test_arbitrage_research_protocol.py tests/test_strategy_candidate_registry.py tests/test_strategy_next_bundle.py --rootdir=tests -q
→ 232 passed in 2.04s
```

- `test_crypto_d1_protocol.py` — **21 new tests** (Bundle 11).
- Bundle 10 readiness gate — 22 still pass.
- Bundle 9 sample dataset plan — 23 still pass.
- Bundle 8 data source evaluation — 23 still pass.
- Bundle 7 QA harness spec — 22 still pass.
- Bundle 6 dataset manifest — 19 still pass.
- Bundle 5 data contract — 16 still pass.
- Bundle 4 research protocol — 14 still pass.
- Bundle 3 candidate registry — 16 still pass (the new
  `lane_status_override` mechanism fires only when `extra_files` actually
  exist on disk; in tmp-path tests the crypto_d1 v1 paths don't exist, so
  the historical PARKED classification continues — backward-compatible).
- Bundle 2 next-bundle generator — 24 still pass.

## JSON validity

```
python tools/crypto_d1_protocol_check.py validate                → validate: OK
python tools/arbitrage_readiness_gate_check.py validate          → validate: OK
python tools/arbitrage_sample_dataset_plan_check.py validate     → validate: OK
python tools/arbitrage_data_source_evaluation_check.py validate  → validate: OK
python tools/arbitrage_qa_harness_spec_check.py validate         → validate: OK
python tools/arbitrage_dataset_manifest_check.py validate        → validate: OK
python tools/arbitrage_data_contract_check.py validate           → validate: OK
python tools/arbitrage_protocol_check.py validate                → validate: OK
python tools/strategy_candidate_registry.py validate             → validate: OK
python tools/strategy_next_bundle.py validate                    → validate: OK
```

## Crypto-D1 protocol validation result

**`validate: OK`** on the committed protocol. All required top-level keys
present, all 7 safety flags pinned `False`, lane = `crypto_d1_protocol`,
target assets include BTC + ETH + SOL, allowed market type = `spot`,
perp/dated/options/leveraged listed in `forbidden_market_types`,
timeframe = `1d` with intraday explicitly out of scope, session model
declares 24/7 + weekday-only filters forbidden + missing-day policy
required + UTC, all 7 candidate strategy families present with
`mean_reversion` marked `WATCH_only`, all 11 data-requirement keys
populated, all 9 validation phases P0..P8 present, MD carries all 4
required distinction phrases, zero forbidden capability phrases.

## Candidate registry status for crypto_d1 after build

- **status:** **`WATCH`** ✅ (re-opened from PARKED via the new
  `lane_status_override="WATCH"` mechanism; fires because the seed's
  `extra_files` include the new v1 protocol docs which now exist on disk)
- **evidence_level:** `MIXED` (17 matched docs across historical CODR-1
  reports + the new v1 memo; cannot reach `STRONG`)
- The new v1 memo (`protocol.md`, `protocol.json`) is added to
  `source_reports`.
- Guards held: **never ACTIVE / never STRONG**.

**Honest disclosure:** historical reports under
`trading_research/agentic_factory/reports/crypto_d*` (including
`crypto_d14_lane_closeout_and_next_roadmap`, `crypto_d7_codr1_closeout`)
remain authoritative for the prior CODR-1 line. The v1 memo opens a
**new** study; it does not revive, re-tune, or continue any prior
parameter set. The override is gated on the v1 memo's actual on-disk
presence, so in any test tree where the v1 memo is absent, the
classifier honors the historical PARKED signal (preserves Bundle-3
test invariants).

## Next-bundle generator selected bundle after update

**Selects "Arbitrage research protocol"** (lane=
`arbitrage_research_protocol`, priority=3) — same as Bundle 10. Both
arbitrage and crypto_d1 are now WATCH with the same `+15` bonus; the
arbitrage lane wins on the existing protocol-first / data-first scoring
hints already in its queue item. Deterministic logic was **not**
artificially modified.

This is honest behaviour, not a recommendation to keep building
arbitrage. The operator should consult both lanes' next-step lists
(`arbitrage_research_readiness_gate_v1.lane_recommendation` and
`crypto_d1_protocol_v1.required_future_artifacts`) to pick the actual
Bundle 12 — most natural is one of the four crypto_d1 follow-ups.

## How this starts the crypto lane after arbitrage WATCH closure

```
Arbitrage foundation lane           crypto_d1 lane
   (Bundles 4-10, WATCH)               (Bundle 11, WATCH)
        |                                    |
        +-----  parallel research lanes -----+
                       |
                       | (operator picks next move)
                       v
        Bundle 12: one of the recommendations below
```

The crypto_d1 lane v1 protocol explicitly re-opens the lane after the
CODR-1 closeout, with a clean scope (BTC/ETH/SOL, spot, daily, 24/7) and
seven well-defined strategy families. The protocol itself does not
collect data, run any backtest, or claim edge.

## Recommended next bundle

All four follow this protocol's `required_future_artifacts`. Each is a
SEPARATE, separately-authorized future bundle; all are spec-only (no
fetch, no backtest, no execution):

1. **Crypto-D1 Data Contract v1** — defines the data fields, freeze
   rules, fee/slippage schedule, and validity rules for any future daily
   crypto dataset. Spec only.
2. **Crypto-D1 Dataset Manifest v1** — per-dataset manifest schema for
   the crypto-D1 lane. Spec only.
3. **Crypto-D1 Data QA / Freeze Spec v1** — QA harness spec for the
   daily-crypto data shape. Spec only.
4. **Crypto-D1 Baseline Backtest Plan v1** — pre-registration memo for
   the FIRST candidate strategy family + IS / OOS split. Plan only, no
   backtest run.

# Crypto-D3b — Factory-Internal Immutable Crypto Data Freeze (no fetch)

**This is a DATA FREEZE + QA step only.** No network, no fetch, no exchange API,
no broker, no paper/live, no backtest, no strategy test, no optimization, no
parameter sweep. Source files were **not modified**. No S30/futures-branch
changes, no JARVIS/`templates/base.html`/hydra changes, no staging, no commit.

- **Created:** 2026-05-30
- **HEAD at step:** `ce62a71` (Crypto-D3a) — confirmed ancestor of HEAD; factory
  tree clean; nothing staged; snapshot dir confirmed **absent** before create.

---

## 1. Source files (read-only)

From `data/frozen_regime_inputs/` (gitignored, outside the factory, live
daily-refreshed). Schema `timestamp,open,high,low,close,volume`.

| Symbol | File | Size | mtime (UTC) | Rows |
|---|---|---|---|---|
| BTC | `btcusdt_1d_2020-01-01_2026-05-29.csv` | 132101 | 2026-05-30T00:15:04Z | 2341 |
| ETH | `ethusdt_1d_2020-01-01_2026-05-29.csv` | 125579 | 2026-05-30T00:15:04Z | 2341 |
| SOL | `solusdt_1d_2020-08-11_2026-05-29.csv` | 114188 | 2026-05-30T00:15:04Z | 2118 |

**Read-only proof:** sizes and mtimes were **identical before and after** the
freeze for all three files — no source CSV was modified.

## 2. Snapshot created

`trading_research/agentic_factory/data_crypto/spot_binance_usdt_1d_2020_2025/`
(did **not** pre-exist; not overwritten):

- `BTCUSDT_1d_2020_2025.csv`, `ETHUSDT_1d_2020_2025.csv`, `SOLUSDT_1d_2020_2025.csv`
- `provenance.json` (machine sidecar), `MANIFEST.md` (human-readable)

**Seal:** only rows ≤ `2025-12-31` kept; **149** 2026 rows excluded per symbol.

## 3. QA — frozen snapshot

| Check | BTC | ETH | SOL |
|---|---|---|---|
| Kept rows | 2192 | 2192 | 1969 |
| Date range | 2020-01-01→2025-12-31 | 2020-01-01→2025-12-31 | 2020-08-11→2025-12-31 |
| Header schema | ✅ | ✅ | ✅ |
| Duplicate timestamps | 0 | 0 | 0 |
| Invalid OHLC | 0 | 0 | 0 |
| Zero/neg volume | 0 | 0 | 0 |
| Missing calendar days (24/7) | 0 | 0 | 0 |
| 2026 excluded | ✅ | ✅ | ✅ |

Quote consistency: USDT across all three. UTC daily boundary (00:00, `%Y-%m-%d`).
**QA verdict: CLEAN.**

**SHA256 (immutability seal):**
- BTC `d87742b8e4c90eeadb3312561e8f63314c3139e6740c06e151b206ee06622941`
- ETH `4a4d7b082b5c6c086c71d4dbc933e9d45f67b1632c9130a7df48d0daeb0180e7`
- SOL `bd8b28f1fd7c6d5187bc3f60e609e22aa28c57d57477472e4b845059c07c5f32`

## 4. Provenance sidecar

`provenance.json` + `MANIFEST.md` record: vendor **Binance public market data**,
endpoint family `https://api.binance.com/api/v3/klines`, **market_type=spot**,
**quote=USDT**, **interval=1d (daily-native)**, **timezone=UTC (00:00)**,
retrieval scripts `tools/fetch_binance_crypto_daily_frozen.py` +
`tools/regime_shadow_fresh_data_update.py`, `no_fetch=true`,
`no_exchange_execution=true`, `source_modified=false`. Provenance basis =
Crypto-D3a pin (`ce62a71`, 9/10 fields PINNED); the one prior gap (immutability)
is **closed** by this hash-pinned freeze.

## 5. Verdict — `DATA_READY_FOR_CRYPTO_D4_SPEC`

An immutable, SHA256-pinned, 2026-sealed factory snapshot of BTC/ETH/SOL spot
daily USDT candles (2020–2025) now exists inside the factory with a provenance
sidecar. Source provenance was pinned in Crypto-D3a and the single remaining gap
(dataset immutability) is now closed. The data is ready to back a future,
**separately-authorized** Crypto-D4 frozen strategy spec.

**Still blocked / out of scope:** Crypto-D4 not started or authorized here;
perps blocked until funding sourced+frozen; quote reconciliation (USDT vs
USD/USDC) and an independent second-source cross-check (Kraken/Coinbase) remain
advisable before any edge claim; 2026 stays sealed out unless separately
authorized.

## 6. Tests (scoped factory suite)

```
python -m pytest trading_research/agentic_factory/tests -q \
  --rootdir=trading_research/agentic_factory \
  --confcutdir=trading_research/agentic_factory -p no:cacheprovider
```

**Result: 293 passed, 1 failed.** The single failure is the **pre-existing,
unrelated** `test_config_wiring.py::test_load_config_includes_strategy_block`
(`session_start` is `09:30`, test expects `14:30`) — **not** caused by and
**not** fixed in this crypto data step (out of scope). (A one-shot temp builder
script was used to create the snapshot and **deleted** immediately after; an
interim run flagged its `binance` token via the safety-guard scan, which is why
it was removed — the final tree contains no such file.)

## 7. Forbidden actions (this lane)

`no_strategy_test` · `no_exchange_api_execution` · `no_broker` · `no_paper_or_live` ·
`no_network` · `no_data_fetch` · `no_backtest` · `no_optimization` ·
`no_parameter_sweep` · `no_modification_of_source_csv` ·
`no_perps_until_funding_rules_frozen` · `no_using_old_results_as_proof` ·
`no_mixing_crypto_with_futures_validation_claims` ·
`do_not_touch_s30_or_futures_branches` · `jarvis_templates_base_hydra_untouched` ·
`no_staging` · `no_commit`.

---

**Final line:** *Crypto-D3b freezes an immutable, SHA256-pinned, 2026-sealed
factory snapshot of BTC/ETH/SOL spot daily USDT candles (2020–2025) derived
read-only from local data with a provenance sidecar — verdict
**DATA_READY_FOR_CRYPTO_D4_SPEC**; no fetch/network/exchange/broker/paper/live
occurred, no source file was modified, no crypto strategy is
specified/validated/paper-ready/live-ready, perps remain blocked, and
S30/futures branches are untouched.*

**Trading recommendation:** NONE. Data freeze + QA only. An immutable
hash-pinned 2020–2025 spot snapshot now backs the crypto lane, but no crypto
strategy is validated, paper-ready, or live-ready; Crypto-D4 is not authorized;
perps blocked; crypto stays a separate research lane; S30 stays PARKED after
IS_FAIL and the futures branches are untouched.

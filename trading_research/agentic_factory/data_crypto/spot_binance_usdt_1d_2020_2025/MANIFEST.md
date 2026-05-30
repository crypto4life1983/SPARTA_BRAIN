# Frozen Crypto Snapshot — `spot_binance_usdt_1d_2020_2025`

**Step:** Crypto-D3b — factory-internal immutable data freeze (no fetch, no network).
**Created (UTC):** 2026-05-30T17:54:00Z

This is an **immutable, SHA256-pinned** snapshot of BTC/ETH/SOL **spot daily**
candles for **2020–2025 only**, derived **read-only** from the local
regime-intelligence drop-zone. No exchange API, no network, no fetch was used.
2026 rows are **sealed out** (Crypto-D1 §10).

## Source

- **Vendor:** Binance public market data
- **Endpoint family:** `https://api.binance.com/api/v3/klines` (SPOT; perp would be `fapi.binance.com`)
- **Market type:** SPOT · **Quote:** USDT · **Interval:** `1d` (daily-native) · **Timezone:** UTC (00:00 boundary)
- **Retrieval scripts (producer):** `tools/fetch_binance_crypto_daily_frozen.py`, `tools/regime_shadow_fresh_data_update.py`
- **Provenance basis:** Crypto-D3a pin (commit `ce62a71`) — 9/10 source-provenance fields PINNED; the one unmet item (immutability) is closed by **this** freeze.

## Files (schema: `timestamp,open,high,low,close,volume`)

| Symbol | File | Rows | Date range | SHA256 |
|---|---|---|---|---|
| BTC | `BTCUSDT_1d_2020_2025.csv` | 2192 | 2020-01-01 → 2025-12-31 | `d87742b8e4c90eeadb3312561e8f63314c3139e6740c06e151b206ee06622941` |
| ETH | `ETHUSDT_1d_2020_2025.csv` | 2192 | 2020-01-01 → 2025-12-31 | `4a4d7b082b5c6c086c71d4dbc933e9d45f67b1632c9130a7df48d0daeb0180e7` |
| SOL | `SOLUSDT_1d_2020_2025.csv` | 1969 | 2020-08-11 → 2025-12-31 | `bd8b28f1fd7c6d5187bc3f60e609e22aa28c57d57477472e4b845059c07c5f32` |

Each source had **149** 2026 rows excluded (through 2026-05-29).

## QA (frozen snapshot, all symbols)

- Header schema ✅ · 0 duplicate timestamps · 0 invalid OHLC · 0 zero/neg volume · 0 missing calendar days (24/7) · single USDT quote · 2026 fully excluded.

## Seal / windows

- **Seal max date:** 2025-12-31. **IS:** 2020–2023 · **OOS:** 2024–2025.
- **2026 excluded** unless separately authorized.
- **SOL** starts 2020-08-11 (listing) — tri-symbol joint tests align to common
  2020-08-11+ index or pre-registered per-symbol windows.
- **Quote rule:** USDT documented; reconcile vs USD/USDC before any edge claim.

## Read-only proof

Source files in `data/frozen_regime_inputs/` were **not modified** — sizes and
mtimes identical before and after the freeze (all `2026-05-30T00:15:04Z`).

## Status

- **Perps:** BLOCKED until funding sourced + frozen.
- **No strategy** is specified, validated, paper-ready, or live-ready. This is
  data freeze + QA only. Crypto stays a **separate** lane (never mixed with
  futures validation claims). S30 / futures branches untouched.
- Re-freeze must reproduce identical SHA256 or be a new `snapshot_id`.

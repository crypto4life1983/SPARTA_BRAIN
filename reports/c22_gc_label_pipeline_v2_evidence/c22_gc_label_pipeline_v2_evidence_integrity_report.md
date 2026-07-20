# C22 GC Label Pipeline V2 — Evidence Integrity Report

Read-only evidence report. Issues no token; authorizes no replay, optimization,
or activation; changes no collection state.

## Scope

- Window range: 2026-06-20 .. 2026-07-15 (frozen)
- Windows: 26, labels: 1300
- Artifact: `c22_gc_real_candle_entry_labels_multiwindow_v2_26w_2026-06-20_2026-07-15.json`

## Label distribution

- BEAR_SHORT: 72
- HEDGE_SHORT: 3
- LONG_ENTRY: 13
- NONE: 1212
- SKIP: 0

## Signal concentration by date (non-NONE only)

- 2026-06-20: BEAR_SHORT=1, LONG_ENTRY=1
- 2026-06-21: BEAR_SHORT=2
- 2026-06-23: BEAR_SHORT=2, LONG_ENTRY=1
- 2026-06-24: BEAR_SHORT=1
- 2026-06-26: BEAR_SHORT=1
- 2026-06-27: LONG_ENTRY=1
- 2026-06-28: BEAR_SHORT=2
- 2026-06-29: BEAR_SHORT=2, LONG_ENTRY=1
- 2026-06-30: BEAR_SHORT=1, LONG_ENTRY=1
- 2026-07-01: BEAR_SHORT=2, HEDGE_SHORT=1, LONG_ENTRY=1
- 2026-07-02: BEAR_SHORT=3, LONG_ENTRY=1
- 2026-07-03: BEAR_SHORT=2
- 2026-07-04: BEAR_SHORT=3, LONG_ENTRY=1
- 2026-07-05: BEAR_SHORT=6
- 2026-07-06: BEAR_SHORT=6, HEDGE_SHORT=1, LONG_ENTRY=1
- 2026-07-07: BEAR_SHORT=6, LONG_ENTRY=1
- 2026-07-08: BEAR_SHORT=6, HEDGE_SHORT=1
- 2026-07-09: BEAR_SHORT=4
- 2026-07-10: BEAR_SHORT=3, LONG_ENTRY=1
- 2026-07-11: BEAR_SHORT=4
- 2026-07-12: BEAR_SHORT=5
- 2026-07-13: BEAR_SHORT=2
- 2026-07-14: BEAR_SHORT=3
- 2026-07-15: BEAR_SHORT=5, LONG_ENTRY=2

## Signal concentration by asset (non-NONE only)

- BINANCE:AAVEUSDT: BEAR_SHORT=1, LONG_ENTRY=1
- BINANCE:CRVUSDT: BEAR_SHORT=5
- BINANCE:DEXEUSDT: LONG_ENTRY=2
- BINANCE:IMXUSDT: BEAR_SHORT=1
- BINANCE:INJUSDT: BEAR_SHORT=3
- BINANCE:JSTUSDT: LONG_ENTRY=1
- BINANCE:JUPUSDT: LONG_ENTRY=2
- BINANCE:LINKUSDT: BEAR_SHORT=1
- BINANCE:PENDLEUSDT: BEAR_SHORT=5
- BINANCE:QNTUSDT: BEAR_SHORT=5
- BINANCE:SOLUSDT: BEAR_SHORT=1
- BINANCE:SUNUSDT: BEAR_SHORT=2
- BINANCE:TIAUSDT: BEAR_SHORT=4, HEDGE_SHORT=2
- BINANCE:TRXUSDT: BEAR_SHORT=10
- BINANCE:VIRTUALUSDT: BEAR_SHORT=1
- BINANCE:ZECUSDT: BEAR_SHORT=3, LONG_ENTRY=1
- BITFINEX:LEOUSD: BEAR_SHORT=1
- BYBIT:GRAMUSDT: BEAR_SHORT=4
- BYBIT:TELUSDT: BEAR_SHORT=1
- COINBASE:AEROUSD: LONG_ENTRY=3
- COINBASE:MORPHOUSD: BEAR_SHORT=1, HEDGE_SHORT=1, LONG_ENTRY=1
- GATE:ASTERUSDT: BEAR_SHORT=3
- GATE:GTUSDT: BEAR_SHORT=12
- KRAKEN:KASUSD: BEAR_SHORT=2
- KRAKEN:SPXUSD: BEAR_SHORT=5, LONG_ENTRY=2
- OKX:OKBUSDT: BEAR_SHORT=1

## Provenance tiers

- FULL_RAW_REDUCTION_PROVENANCE: 6 windows
- LEGACY_REDUCED_ONLY: 8 windows
- LEGACY_REDUCED_WITH_SIDECAR_NO_RAW: 12 windows

- Sidecars mandatory from: 2026-06-28
- Raw top-100 mandatory from: 2026-07-10
- Windows missing raw top-100 (by design, pre-activation): 2026-06-20, 2026-06-21, 2026-06-22, 2026-06-23, 2026-06-24, 2026-06-25, 2026-06-26, 2026-06-27, 2026-06-28, 2026-06-29, 2026-06-30, 2026-07-01, 2026-07-02, 2026-07-03, 2026-07-04, 2026-07-05, 2026-07-06, 2026-07-07, 2026-07-08, 2026-07-09
- Windows missing raw top-100 (MANDATORY — blocker): none
- Windows missing sidecar (by design, pre-activation): 2026-06-20, 2026-06-21, 2026-06-22, 2026-06-23, 2026-06-24, 2026-06-25, 2026-06-26, 2026-06-27
- Windows missing sidecar (MANDATORY — blocker): none
- Windows with full raw+sidecar provenance: 2026-07-10, 2026-07-11, 2026-07-12, 2026-07-13, 2026-07-14, 2026-07-15
- End-to-end provenance complete for all windows: False
- Pre-build status: LABEL_SOURCE_INTEGRITY_PASS_WITH_LEGACY_PROVENANCE_GAP

## Determinism and hashes

- Aggregate manifest SHA-256: `48347e9c8ea8cee037863b6a1c23fa0506a0dbf429fb7e2900782addeef2d167`
- Canonical label payload SHA-256: `5dc9eae4471fd697b18622e716b2086a6899f17d0cd02fd589d88ca6da927991`
- Artifact SHA-256 on disk: `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8`
- Artifact SHA-256 rebuilt from frozen sources: `b6a28a4873d1aff17014a9d598702c67047b4ebe023b8cfddce05094f9ce9dd8`
- Byte-identical rebuild: True
- Anti-tamper validator: PASS

## Recommendation

**READY_FOR_HUMAN_REVIEW_OF_REPLAY_APPROVAL**

The V2 label evidence is internally consistent, provenance-honest, and
deterministically rebuildable. A separate human replay-approval decision
is still required before any replay; this report authorizes nothing.

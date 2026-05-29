# s21 weekly RS paper data refresh — RUN_BOOK (sealed; framework ONLY; NO fetch)

**report_seal:** `ff8aed3d7aca37d0302626258e9dd1a3ab389546a77d4f52a592427c8f4913ce` · **Authored:** 2026-05-29T14:00:18.646528Z · run-date context 2026-05-29
Bounded plan to bring the s21 paper data current so a FORWARD cycle (002+) can run. **NO fetch this turn.** Sealed DR9 set is never overwritten.

## Frozen universe (48; byte-identical to s21 sealed)
AVGO, QCOM, TXN, INTC, MU, AMAT, IBM, INTU, NOW, ADI, VZ, T, CHTR, EA, SBUX, TGT, BKNG, MAR, GM, TJX, ROST, MO, CL, KMB, GIS, STZ, PFE, BMY, AMGN, GILD, CVS, CI, ISRG, SYK, C, USB, SCHW, BLK, SPGI, CB, BA, ITW, UPS, RTX, LMT, DE, PSX, VLO

## Target range
**2025-12-31 → latest COMPLETED weekly-anchor session on/before the fetch run date** (~2026-05-29; computed precisely at fetch; ~21-22 new weekly anchors).

## Vendor / convention
tiingo · **split_only** (raw OHLCV × cumulative(1/splitFactor) for splits strictly after each date; volume ÷ factor; dividends NOT adjusted) — identical to s21. TIINGO_API_KEY from env only, never printed.

## CRITICAL: split_only is RETROACTIVE
A new split after 2025-12-30 re-scales the ENTIRE pre-split history. So the refresh **re-fetches FULL history and recomputes split_only over the whole series** (not a naive append). No-split symbols must **reproduce** the sealed 2019..2025-12-30 values byte-for-byte; split symbols re-scale (return-continuous) and are documented. Undocumented overlap divergence → **data-integrity HALT**.

## Output (local-only; sealed dir NEVER overwritten)
Refresh dir: `data/s21_weekly_rs_paper_refresh/raw` · filename `<SYM>_ohlcv_1d_20190102_<ASOF>.csv` · update manifest with per-symbol sha256, row counts, new rows, splits, overlap-reproduction flag. Sealed DR9 dir `data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw` is immutable.

## Verification
SHA256 (per CSV + manifest) · calendar alignment (identical 48 date vectors; overlap matches sealed calendar) · historical-overlap reproduction · split-consistency (band 0.85-1.15) · DR9 thresholds (gap≥0.95, max_gap≤0.30, quality≤5).

## Stale-data kill
If latest bar < target weekly-anchor session, or empty/short history, or misalignment, or undocumented divergence → **HALT** (no partial/stale write; no paper cycle on stale data).

## Downstream note
The harness cycle currently expects the `_20251230.csv` suffix; wiring a forward cycle to the refreshed dir/filenames is a SEPARATE step (small BUILD or explicit dir/pattern at RUN). This RUN_BOOK defines the DATA refresh only.

## Status / next
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY. lessons.md NOT touched; no sealed artifact modified.
- **Execute the refresh (separate auth):** `Authorize s21 weekly RS paper data refresh fetch + verification workflow only — Tiingo split_only, frozen 48-name universe, FULL-HISTORY re-fetch + recompute, write to data/s21_weekly_rs_paper_refresh/raw (do NOT overwrite the sealed s21 DR9 CSVs), run SHA + calendar-alignment + split-consistency + historical-overlap-reproduction checks, HALT on stale/misaligned/undocumented-divergence; TIINGO_API_KEY from env only, never printed; no paper cycle, no broker, no live, no FRC.`
- **Defer / Pause at RUN_BOOK.**

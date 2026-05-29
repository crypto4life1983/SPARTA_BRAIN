# s21-d1 broader-universe weekly RS rotation — availability-probe + DR9-audit RUN_BOOK (sealed; framework ONLY; NO fetch)

**report_seal:** `efb22bb2c9e90fb9e6662c67f258ac61e4dc58058ae05f410b9a41070f4c8c7d` · **Authored:** 2026-05-29T04:21:38.569452Z
**T1 CLEAN GENERALIZATION TEST** — resolves the s20 selection caveat. **NO fetch this turn** (fetch = separate authorization).

## Purpose
s20 OOS_CONFIRMED on the s18+s19 UNION proved breadth solves the OOS-K9 blocker, but the union includes the known-OOS-good s18 basket (sample-size demo, not clean generalization — LESSON_S20_D1_002). s21 runs the **IDENTICAL byte-locked mechanic** (126-21 / R=5 / top-8 / M=8 / long-only / relative-rank exit) on a **FRESH 48-name universe, ZERO overlap with s17/s18/s19** — a positive result = genuine independent generalization. Replication-not-tuning; s17-s20 frozen.

## Fresh universe (48, zero-overlap; ~9 sectors)
AVGO, QCOM, TXN, INTC, MU, AMAT, IBM, INTU, NOW, ADI, VZ, T, CHTR, EA, SBUX, TGT, BKNG, MAR, GM, TJX, ROST, MO, CL, KMB, GIS, STZ, PFE, BMY, AMGN, GILD, CVS, CI, ISRG, SYK, C, USB, SCHW, BLK, SPGI, CB, BA, ITW, UPS, RTX, LMT, DE, PSX, VLO

**Reserve (clean replacements on DR9 fail):** EMR, ETN, NSC, UNP, DUK, SO

## Vendor / window
tiingo · split_only · 2019-01-02..2025-12-30 · expected 1759 bars · `data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw` · TIINGO_API_KEY from env only (never printed).

## DR9 audit (per symbol)
gap_continuity >= 0.95 · max_gap_ratio <= 0.30 · quality_violation_count <= 5 · roll NOT_APPLICABLE_CASH_EQUITY · split-consistency band 0.85-1.15 · row_count == 1759 · identical NYSE calendar across all 48. The audit verifies ALL Tiingo splitFactors (e.g. AVGO 10:1 2024-07-15), not just pre-listed.

## Reachability discipline
K9 IS expected to clear (s20 measured 284 at this breadth) · OOS K9 expected ~55-75/y (s20 67.2/y) but UNPROVEN on fresh names -> measured signal-only pre-SEAL at the s21 DRAFT, binding with P&L at P10 · K13 5 DA22 folds (>=3/5 + agg>0 + K9) · DR10 v2 (78cd22e). Edge re-proven at P6 IS, NOT inherited.

## Contingency
Per-symbol DR9 fail -> drop + pull next RESERVE + re-audit (no performance selection). >4 primary fails -> HALT/reassess. Vendor/API fail -> BLOCKER/HALT. Listing post-2019 (row<1759) -> drop to RESERVE. Calendar misalignment -> HALT (no silent reindex).

## Status / next
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY. lessons.md NOT touched.
- **Fetch (separate auth):** `Authorize s21-d1 fresh-universe Tiingo split_only fetch + DR9 result sealing workflow only.`
- **Defer / Pause s21-d1 at RUN_BOOK.**

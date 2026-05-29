# s21-d1 broader-universe (fresh 48-name) weekly RS rotation — Tier-N spec DRAFT

**report_seal:** `e7350f96772c0b691fdcd4640559ac9f9fd8588616c8818b5a82fabfd0f6f99d` · **Pre-SEAL reachability: `PRESEAL_REACHABILITY_PASS_ELIGIBLE_TO_SEAL`** — eligible to SEAL: **True**

## Pre-SEAL K9 turnover (signal-only, NO P&L; fresh 48; SHA 48/48 verified; 1759 bars aligned)
| Gate | Floor | Measured | vs prior | Status |
|---|---|---|---|---|
| K9 aggregate (IS) | >=100 | **310** | s20 union=284 | PASS |
| **OOS K9** | >=50/y (>=100/2y) | **171 (85.79/y)** | s18 117/58.7y · s19 87/43.6y FAIL · s20 134/67.2y | **PASS** |
| K13 per-fold | sample-sufficient | F1=97 F2=87 F3=83 F4=100 F5=112 (agg 479) | — | PASS |
| DR10 v2 | turnover>0.50 AND drag>0.05 | turnover TRUE; drag proj ~1-3% (<5%) | s20 1.03% | EXPECTED_CLEAR |

**OOS-K9 reachability GENERALIZES to a FRESH universe:** 171 (85.79/y) clears the >=50/y floor by +35.8/y signal-only -- even higher than the s20 union. NO OOS P&L inspected; EDGE untested until P10.

## Clean generalization (no selection bias)
0/48 names ever backtested under this mechanic -> a positive result is genuine independent generalization (unlike s20). Names pre-committed by liquidity/sector/listing-history, never by performance.

## Edge not inherited
Re-proven from scratch at P6 IS / P6.7 K13 / P10 OOS. Null/negative accepted.

## Stop-before-SEAL
If K9/OOS-K9/K13 reachability fails -> HALT after DRAFT, no SEAL. (All PASS here -> eligible.)

## Status
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY. Mechanic byte-identical to s18/s19/s20; M=8 unchanged; fresh candidate (not revN). lessons.md NOT touched.

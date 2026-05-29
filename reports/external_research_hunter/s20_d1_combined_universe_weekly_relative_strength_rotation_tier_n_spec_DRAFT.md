# s20-d1 combined-universe (s18 union s19, 48-name) weekly RS rotation — Tier-N spec DRAFT

**Authored (UTC):** `2026-05-29T03:42:43.841343Z` · **report_seal:** `5daa6a82b9d098ae22ee99b88f72223fff8ec00931fd55e7afd975e8de6360e6`
**Pre-SEAL reachability: `PRESEAL_REACHABILITY_PASS_ELIGIBLE_TO_SEAL`** — eligible to SEAL: **True**

## Pre-SEAL K9 turnover measurement (signal-only, NO P&L; 48-name union; SHA256 48/48 verified; calendar 1759 bars aligned)
| Gate | Floor | Measured | vs parents | Status |
|---|---|---|---|---|
| K9 aggregate (IS) | >=100 | **284** | s18=229, s19=226 | PASS |
| **OOS K9** | >=50/y (>=100/2y) | **134 (67.23/y)** | s18=117/58.7y CLEARED · **s19=87/43.6y FAILED** | **PASS** |
| K13 per-fold | sample-sufficient | F1=77 F2=96 F3=81 F4=77 F5=84 (agg 415) | — | PASS |
| DR10 v2 | turnover>0.50 AND drag>0.05 | turnover TRUE; drag proj ~1-3% (<5%) | parents <1% | EXPECTED_CLEAR (narrower) |

**Breadth STRUCTURALLY SOLVES the s19 OOS-K9 blocker:** OOS turnover 134 (67.23/y) clears the >=50/y floor by +17.2/y (signal-only; binding at P10 with P&L). OOS turnover is calendar/ranking-structural — NO OOS P&L inspected; the EDGE is untested until P10.

## Selection caveat (sec 2, carried)
The union includes the known-OOS-good s18 basket -> a positive s20 is WEAK generalization evidence; s20's honest value is the SAMPLE question. Mitigated by union-of-pre-committed-baskets, zero tuning, M=8 unchanged, edge re-proven at P6 IS.

## Edge not inherited
Re-proven from scratch at P6 IS / P6.7 K13 / P10 OOS. Null/negative accepted.

## Status
PAUSED · BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. Mechanic byte-identical to s18/s19; M=8 unchanged; fresh candidate (not s18/s19 revN). lessons.md NOT touched.

## Next
SEAL (reachability PASSED): `Authorize ... SEAL` (within the authorized DRAFT-to-diagnostic bundle).

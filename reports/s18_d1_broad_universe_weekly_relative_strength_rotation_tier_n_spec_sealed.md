# s18-d1 broad-universe weekly relative-strength rotation — Tier-N spec SEAL (binding; immutable)

**Authored (UTC):** `2026-05-29T01:59:22.923780Z` · **report_seal:** `06e96e3cc7902a196cba33cc5cb57587fb4fd3c1034737715b85aebaf546940e`
**Candidate:** `s18-d1-broad-universe-weekly-relative-strength-rotation-24name-large-cap-long-history` · fresh sibling. Anchors DRAFT `1b21f8c` (file `27be104931caf56f…` / report_seal `b173382c497a3026…`).

All **DA1–DA22 locked byte-equivalent**; canonical immutable spec; anchor for P1/P2/P3 BUILD/P4/P6/P6.5/**P6.7 K13**/P7/P10/P11.

## K8 sealed-parent-drift check
`PASS (DRAFT re-read at SEAL; recomputed canonical seal == stored report_seal; no drift)`

## Locked weekly design
126-21 RS signal · **weekly (R=5)** · hold **top-8 equal-weight** · long-only · relative-rank exit · $100k · split_only · tiingo · reuse 24-name DR9 data.

## Pre-SEAL K9 gate: PASS (carried from DRAFT, measured signal-only no P&L)
aggregate **229** (CLEARS ≥100) · per-fold **F1=68/F2=69/F3=72** (~54–57/y CLEAR) · OOS projected **~100–113/2y** (clears marginally). T-FORBID-24 satisfied. DR10 v2 CLEARS.

## K13 fold scheme LOCKED (DA22; unsearched)
| Fold | idx | dates | bars |
|---|---|---|---|
| F1 | 160-478 | 2019-08-21..2020-11-23 | 319 |
| F2 | 479-797 | 2020-11-24..2022-03-02 | 319 |
| F3 | 798-1116 | 2022-03-03..2023-06-08 | 319 |
| F4 | 1117-1435 | 2023-06-09..2024-09-16 | 319 |
| F5 | 1436-1758 | 2024-09-17..2025-12-30 | 323 |

## Binding caveat
The **edge is UNTESTED** — weekly is the weakest first-principles edge basis in the ladder and is **NOT inherited** from monthly s17; it must be re-proven at **P6 IS** (K1/K2). Stop-before-promotion (terminal, not a cadence tune) if P6 IS edge fails, K13 <3/5 folds, or P10 OOS K9 <50/y.

## Status
trading PAUSED · live BLOCKED_AT_6_GATES · FRC NEVER_GRANTED · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s17/s16/s15/s14/s13/s12 terminal · DR10 v2 + walk-forward K13 binding. C6=15 entries. lessons.md NOT touched.

## Next
- Commit: `Authorize commit s18-d1 broad-universe weekly relative-strength rotation Tier-N spec SEAL only.`
- Forward: `Authorize s18-d1 broad-universe weekly relative-strength rotation P1 plan-lock only — bound by DR10 v2 + walk-forward K13.`

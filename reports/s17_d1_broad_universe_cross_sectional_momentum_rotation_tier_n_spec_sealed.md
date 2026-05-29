# s17-d1 broad-universe (24-name) cross-sectional momentum rotation — Tier-N spec SEAL (binding; immutable)

**Authored (UTC):** `2026-05-29T00:35:48.529982Z`
**Lifecycle:** `S17_D1_BROAD_UNIVERSE_CROSS_SECTIONAL_MOMENTUM_TIER_N_SPEC_SEALED`
**Report seal sha256:** `ff4b237436cf116b5ab3f1f28cfbd966a99d21020589bec4a1892004fc16b5dc`
**Authorization:** `Authorize s17-d1 broad-universe cross-sectional momentum Tier-N spec SEAL only — bound by DR10 v2 + walk-forward K13.`
**Candidate:** `s17-d1-broad-universe-cross-sectional-momentum-rotation-24name-large-cap-long-history`

All **DA1–DA22 locked byte-equivalent**; canonical immutable spec; anchor for P1/P2/P3 BUILD/P4/P6/P6.5/**P6.7 (K13)**/P7/P10/P11 (each a separate authorization). First candidate under the walk-forward K13 discipline (`52a3b60`). Parent DRAFT lock: file sha `75e4d25b36bdf974…` / report_seal `64690e2195cd0f7e…` (commit `ec9c0ad`).

## Locked mechanic
Long-only cross-sectional momentum rotation: **L=126 / S=21** (skip-month) signal · rank 24 · **hold top-M=6 equal-weight** · **monthly (R=21) rebalance** · relative-rank exit (no trailing/ATR stop) · START_CASH $100k · split_only · tiingo.

## K13 fold scheme LOCKED byte-equivalent (DA22; uniform, UNSEARCHED)
Warmup idx 0..159 (2019-01-02 .. 2019-08-20); 5 contiguous rolling OOS folds; PASS = positive in **≥3 of 5** + aggregate net>0 + K9; P6.7 before P10.

| Fold | idx | dates | bars |
|---|---|---|---|
| F1 | 160..478 | 2019-08-21 .. 2020-11-23 | 319 |
| F2 | 479..797 | 2020-11-24 .. 2022-03-02 | 319 |
| F3 | 798..1116 | 2022-03-03 .. 2023-06-08 | 319 |
| F4 | 1117..1435 | 2023-06-09 .. 2024-09-16 | 319 |
| F5 | 1436..1758 | 2024-09-17 .. 2025-12-30 | 323 |

P10 final hold-out (separate): 2024-01-02 .. 2025-12-30 (idx 1258..1758).

## Reachability
- **K9 (PRIMARY kill-risk):** aggregate clears ≥100 (~84–252); standalone **P10 OOS ≥50/y AT RISK** (~24–72 over 2y); per-fold TIGHT. Shortfall = **terminal block, NOT a cadence-tune**.
- **DR10 v2:** CLEARS strong margin. **DR9:** all 24 PASS by reuse (`85667ab3`).

## Gates
DR chain `DR7→DR1→DR9→DR10→DR6→DR4→DR2→DR3→DR5`; DR10 v2 by-ref `78cd22e`; DR11 NOT IN CHAIN. K1/K2 binding (per-fold + aggregate); K9 INVIOLATE (primary kill-risk); **K13 ADDED** (by-ref `52a3b60`) at P6.7; K10/K6/A7 load-bearing; K11 NOT_APPLICABLE. C6 inherited_constraints_block: 14 entries.

## T-FORBID clearance
16/17/18/19/20/21/**22** (locked params; pre-committed unsearched folds; no per-fold refit) — all CLEARED.

## Status
trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s16/s15/s14/s13/s12 terminal (not re-evaluated under K13) · DR10 v2 + walk-forward K13 binding. lessons.md NOT touched.

## Next authorization
- Commit: `Authorize commit s17-d1 broad-universe cross-sectional momentum Tier-N spec SEAL only.`
- Forward: `Authorize s17-d1 broad-universe cross-sectional momentum P1 plan-lock only — bound by DR10 v2 + walk-forward K13.`

End of SEAL. Canonical immutable Tier-N spec. No code / backtest / fetch / OOS / P1 / commit this turn.

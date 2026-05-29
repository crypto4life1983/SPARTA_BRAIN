# s17-d1 broad-universe (24-name) cross-sectional momentum rotation — Tier-N spec DRAFT (sealed; NOT a Tier-N SEAL)

**Authored (UTC):** `2026-05-29T00:28:54.409718Z`
**Lifecycle:** `S17_D1_BROAD_UNIVERSE_CROSS_SECTIONAL_MOMENTUM_TIER_N_SPEC_DRAFT_SEALED`
**Report seal sha256:** `64690e2195cd0f7e2d64c3408a920e1d37a3f86b563ba3d537b74843a7d033c0`
**Authorization:** `Authorize s17-d1 broad-universe cross-sectional momentum Tier-N spec DRAFT only — bound by DR10 v2 + walk-forward K13.`
**Candidate:** `s17-d1-broad-universe-cross-sectional-momentum-rotation-24name-large-cap-long-history`

DRAFT carries the PLAN structural locks (`15e891a`), formalizes the first-principles relative-momentum mechanic + DA register (DA1–DA22), and carries the K13-per-fold + K9-per-fold reachability tables. **NOT a Tier-N SEAL.** First candidate authored under the walk-forward K13 discipline (`52a3b60`).

## Mechanic (first-principles; justify-not-tune at SEAL)
Long-only cross-sectional momentum rotation: signal = **126−21 skip-month** trailing return (Jegadeesh-Titman); rank 24, **hold top-6 equal-weight**, **monthly (R=21) rebalance**; a name exits when it leaves the top-6 (relative-rank exit; no trailing/ATR stop). DA3 equal-weight 1/M; DA4 START_CASH $100k; long-only unlevered.

## K13 walk-forward (P6.7, before P10)
5 fixed pre-committed **unsearched** rolling OOS folds (~1.27y each over 2019–2025; exact boundaries locked at SEAL); PASS = positive in **≥3 of 5** folds + aggregate net>0 + K9. Validation-not-optimization, no per-fold refit (T-FORBID-22 INVIOLATE).

## Reachability (load-bearing)
- **K9 (primary kill-risk):** monthly top-6 ≈ ~12–36 trades/y → **aggregate clears ≥100** (~84–252) but the standalone **P10 OOS ≥50/y is AT RISK**; per-K13-fold TIGHT (~15–46). Edge-vs-sample tension surfaced. **A K9 shortfall = terminal block, NOT a cadence-tune** (a different cadence = a fresh candidate).
- **DR10 v2:** CLEARS strong margin (turnover ~1–3 alone; cost_drag ~0.2–0.6% « 5%; AND-conjunction not triggered).
- **DR9:** all 24 PASS by reuse (`85667ab3`); no fetch.

## Gates
DR chain `DR7→DR1→DR9→DR10→DR6→DR4→DR2→DR3→DR5`; DR10 v2 by-ref `78cd22e`; DR11 NOT IN CHAIN. K1/K2 binding edge gates (per-fold + aggregate); K9 INVIOLATE (primary kill-risk); **K13 ADDED** (by-ref `52a3b60`) at P6.7; K10/K6/A7 diversification load-bearing; K11 NOT_APPLICABLE.

## T-FORBID clearance
16/17/18 (not MR), 19/20/21 (not an s16 patch), **22 (locked params; pre-committed unsearched folds; no per-fold refit)** — all CLEARED.

## Status
trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s16/s15/s14/s13/s12 terminal (not re-evaluated under K13) · DR10 v2 + walk-forward K13 binding. lessons.md NOT touched.

## Next authorization
- Commit: `Authorize commit s17-d1 broad-universe cross-sectional momentum Tier-N spec DRAFT only.`
- Forward: `Authorize s17-d1 broad-universe cross-sectional momentum Tier-N spec SEAL only — bound by DR10 v2 + walk-forward K13.`

End of DRAFT. Sealed DRAFT document; NOT a Tier-N SEAL. No code / backtest / fetch / OOS / SEAL / commit this turn.

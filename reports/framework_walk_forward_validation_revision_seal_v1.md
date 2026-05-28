# Framework discipline revision SEAL v1 -- walk-forward / multi-window validation (SEALED)

**Revision id:** `FRAMEWORK_WALK_FORWARD_VALIDATION_v1` - **Report seal:** `4268d6f75bbc095a795510f7d8ccc50c2d8886eef36f50f769b79342002893d2` - **Authored:** `2026-05-28T23:25:44.463441Z`
**Binding scope:** s17+ candidate SEAL turns only (NON-retroactive; analogous to DR10 v2 binding s14+).
**Anchors:** PLAN `e0cb0b5` - DR10 v2 SEAL `78cd22e` - selection plan `56ddd4d` - s16 P11 `99f58bd`.

## Core distinction (INVIOLATE)
**Walk-forward = VALIDATION of LOCKED parameters, NOT optimization.** Each fold re-evaluates the SAME sealed rule (DA register byte-equivalent); NO per-fold re-fitting. Preserves `no_strategy_optimization_authorized`.

## K13 walk-forward-persistence gate (LOCKED)
- Pass: locked edge POSITIVE (expectancy>0 AND sharpe_proxy/trade>0 AND no K1/K2) in **>= ceil(0.6*N) OOS folds (N=5 -> >=3 of 5)** AND aggregate net>0 AND K9 holds.
- Fail: **OOS_NOT_ROBUST -> REJECT_FAST** (terminal).
- ADDITIVE gate; does NOT relax K1/K2/K4/K9/K12/DR chain.

## Fold scheme (LOCKED)
Fixed, pre-committed, **unsearched** sequence of **5** sequential OOS folds (rolling/expanding declared at candidate PLAN per asset/frequency class); per-fold warmup; no fold-anchoring.

## Ladder placement (LOCKED)
New phase **P6.7 walk-forward validation**, AFTER P6.5 and BEFORE P10; clear K13 before P10. P10 retained as final hold-out.

## Retroactive effect: NONE
s16/s15/s14/s13/s12 verdicts stand byte-equivalent; NOT re-evaluated. Whether s16 would have failed K13 is INFORMATIONAL-ONLY and not computed/used.

## Preserves
DR chain, DR10 v2 (`78cd22e`), K1-K12, K9 inviolate, REC1-equivalent, C1-C8, no_strategy_optimization, no_dr_redefinition_post_seal. K13 is purely additive.

## Honest limit
s16's IS already spanned 2022; this raises the bar / rejects more, NOT a silver bullet.

## Boundaries held
Framework SEAL only - no candidate/code/backtest/fetch/OOS/live - validation-not-optimization inviolate - fold scheme pre-committed/unsearched - NON-retroactive - no existing-gate relaxation - no DR10 v2 modification - no sealed-artifact mod - no lessons.md - no commit by script.

## Next
Commit: `Authorize commit framework walk-forward / multi-window validation discipline revision SEAL only.`

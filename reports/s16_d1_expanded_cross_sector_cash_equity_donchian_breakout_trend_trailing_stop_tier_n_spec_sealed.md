# s16-d1 expanded-universe Donchian breakout trend Tier-N specification (SEALED)

**Candidate:** `s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history`
**Phase:** `TIER_N_SPEC_SEAL` - **Report seal:** `359aea43df85c153c8cbf2b7a84ddeaa78d6516fe43769e34b052b4f88c60df8` - **Authored:** `2026-05-28T22:14:45.553265Z`
**Anchors:** DRAFT `15182cb` (file sha `69015fd4dac23823c2994180...`, report_seal `a9aded38fb3e6d4494155ce8...`) - PLAN `68c2539` - DR9 result `245ac0d` (`ec856253`) - DR10 v2 `78cd22e`

## 1. First-principles exit/stop (LOCKED; binding axis)
TRAILING Donchian channel (N_exit=10) + 2xATR(14) initial catastrophe stop (NOT a tight MR stop). Expected trend profile win<50%/P/L>1 -- HYPOTHESIS tested at P6 IS.

## 2. DA register (DA1-DA20; LOCKED byte-equivalent)
| Code | Name | Locked value |
|---|---|---|
| DA1 | candidate_record_id | s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history |
| DA2 | mechanic_family | F-trend: Donchian channel breakout (bi-directional) with trailing exit channel + ATR initial stop (NON-mean-reversion) |
| DA3 | per_trade_risk_pct | 0.005 |
| DA4 | START_CASH_USD | 100000 |
| DA5 | K4_max_drawdown_magnitude_threshold | 0.5 |
| DA6 | N_entry_donchian | 20 |
| DA7 | cost_stress_tiers | [{"tier": "S0", "cost_scalar": 0.0, "slippage_scalar": 0.0}, {"tier": "S1", "cost_scalar": 1.0, "slippage_scalar": 1.0}, {"tier": "S2", "cost_scalar": 1.5, "slippage_scalar": 1.5}, {"tier": "S3", "cost_scalar": 2.0, "slippage_scalar": 2.0}, {"tier": "S4", "cost_scalar": 3.0, "slippage_scalar": 3.0}] |
| DA8 | N_exit_donchian_trailing | 10 |
| DA9 | exit_rule | TRAILING_DONCHIAN_CHANNEL (long exits < prior 10d low; short exits > prior 10d high). [LOAD-BEARING binding axis] |
| DA10 | initial_catastrophe_stop_atr_multiple | 2.0 |
| DA11 | ATR_period | 14 |
| DA12 | sizing_method | vol_normalized: shares = floor((0.005*equity) / (2*ATR14)) |
| DA13 | DR10_definition | v2 AND-conjunction: (annual_turnover>0.50 AND S2_cost_drag>0.05) -> REJECT_FAST |
| DA14 | DR9_data_continuity | ALL 12 PASS by REUSE of sealed CSVs at 245ac0d (result_seal ec856253); NO fresh fetch; sha-verified at BUILD |
| DA15 | adjustment_convention | split_only |
| DA16 | data_vendor | tiingo (data already fetched + DR9-sealed; no new fetch) |
| DA17 | universe | ["AAPL", "MSFT", "NVDA", "JPM", "XOM", "UNH", "WMT", "KO", "META", "AMZN", "JNJ", "CVX"] |
| DA18 | portfolio_position_caps | max_positions_per_name=1, max_total_positions=6, no inter-name coordination, no pyramid |
| DA19 | warmup_days | 40 |
| DA20 | signal_direction | bi-directional (long+short) per-name |

## 3. DR9 (PASSED all 12 by reuse - no fetch) + reachability
DR9 all 12 PASS by reuse (245ac0d/ec856253). K9 ~96-180/y -> clears OOS >=50/y. DR10 v2 clears (cost_drag <<5%). K1/K2 are the binding edge gates (tested at P6 IS).

## 4. C6 inherited_constraints_block (LOCKED; 16 entries)
1. REC1-equivalent (BINDING): OOS K9 reachable on the 12-name basket (expected ~96-180/y). If observed effective IS rate < 25/y basket-summed, OOS K9 unreachability becomes structurally probable -> PARKED_SAFE_BUT_OOS_INDETERMINATE per precedent. The chain shall NOT relax K9 at OOS.
2. EXIT/STOP-FIRST-PRINCIPLES (BINDING; trend variant): exit = TRAILING DONCHIAN channel (N_exit=10; let winners run/cut losers) + 2xATR(14) initial catastrophe stop. Opposite geometry to the failed mean-reversion family; expected trend profile win<50% / P/L>1. Hypothesis tested at P6 IS, never assumed.
3. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%)
4. DA4=B: START_CASH_USD = 100000 ($100k); DR10 v2 cost_drag clears strong margin for cash equity
5. exit/stop-first-principles + K9-reachability + DR10-v2-reachability disciplines applied at PLAN+DRAFT; binding for all subsequent phases
6. K9_THRESHOLD_INVIOLATE: closed_trades_basket_summed >= 100; no relaxation at any phase
7. Mechanic family Donchian breakout trend (trailing-stop), NON-mean-reversion, LOCKED at PLAN
8. Donchian params N_entry=20 / N_exit=10 / ATR(14) 2N initial stop first-principles; to be JUSTIFIED (not tuned) and LOCKED at SEAL
9. DR10 = v2 AND-conjunction by-reference to framework SEAL 78cd22e; thresholds 0.50/0.05 immutable; no_dr_redefinition_post_seal
10. split_only adjustment convention CONFIRMED (DA15); reuse DR9-passed CSVs; switching post-SEAL FORBIDDEN
11. 12-name expanded cross-sector universe LOCKED at PLAN; widening/substitution post-SEAL FORBIDDEN
12. DR9 data-availability gate PASSED all 12 by REUSE (sealed 245ac0d; result_seal ec856253...); NO fresh fetch; cash_equity_data_reuse_byte_equivalent
13. A7 effective_independent_bets + K10 avg_pairwise_correlation + K6 dispersion LOAD-BEARING (12 names ~7 sectors; expected higher A7 / lower K10 than 3-name basket); NOT the candidate's risk axis (per-trade trend edge K1/K2 is)
14. s15-d1 + s14-d1-cross-sector terminal (FAIL_SAFETY) preserved verbatim; this candidate is FRESH NON-mean-reversion; clears T-FORBID-16/17/18
15. no_strategy_optimization_authorized: parameters first-principles justified at SEAL, NOT grid-searched
16. P6 IS PASS (if reached) does NOT imply READY at OOS; P6 PASS NEVER implies live-readiness; 6-gate live-block applies regardless; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent

## 5. Boundaries
SEAL only (no P1) - all DA locked byte-equivalent - DR10 v2 by-ref - DR9 by reuse - no build/backtest/fetch/OOS - no strategy optimization - no MR re-skin - no _revN_/revival - no sealed-artifact mod (incl. DRAFT 15182cb, s16 DR9 result, 12 CSVs) - no lessons.md - no commit by script.

## 6. Next
Commit: `Authorize commit s16-d1 expanded-universe trend/breakout Tier-N spec SEAL only.` - Forward: `Authorize s16-d1 expanded-universe trend/breakout P1 plan-lock only -- bound by DR10 v2.`

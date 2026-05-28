# s16-d1 expanded-universe Donchian breakout trend Tier-N spec DRAFT (SEALED)

**Candidate:** `s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history`
**Phase:** `TIER_N_SPEC_DRAFT` - **Report seal:** `a9aded38fb3e6d4494155ce8807a8e8df2c008721ee88318712fc10cc2660b69` - **Authored:** `2026-05-28T22:13:12.322223Z`
**Anchors:** PLAN `68c2539` - DR9 result `245ac0d` (result_seal `ec856253`) - DR10 v2 `78cd22e`

## 1. First-principles exit/stop (trend variant; binding axis)
- **Exit = TRAILING Donchian channel (N_exit=10)** - close when price reverses through the opposite 10-day channel (let winners run / cut losers).
- **Initial stop = 2xATR(14)** vol-scaled floor; whichever triggers first.
- Expected trend profile **win<50% / P/L>1** (mirror of failed mean-reversion); HYPOTHESIS tested at P6 IS.

## 2. DA register (DA1-DA20; proposed at DRAFT, locked at SEAL)
| Code | Name | Locked at | Resolution |
|---|---|---|---|
| DA1 | candidate_record_id | PLAN | s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history |
| DA2 | mechanic_family | PLAN | F-trend: Donchian channel breakout (bi-directional) with trailing exit channel + ATR initial stop (NON-mean-reversion) |
| DA3 | per_trade_risk_pct | PLAN | B = 0.005 (0.5%) |
| DA4 | START_CASH_USD | PLAN_PROPOSED_CONFIRM_AT_SEAL | B = 100000 |
| DA5 | K4_max_drawdown_magnitude_threshold | DRAFT_PROPOSED | 0.50 |
| DA6 | N_entry_donchian | PLAN | 20 (enter long > prior 20d high; short < prior 20d low); first-principles, NOT optimized |
| DA7 | cost_stress_tiers | DRAFT_PROPOSED | five_tier_S0_S1_S2_S3_S4 (0.0/1.0/1.5/2.0/3.0) |
| DA8 | N_exit_donchian_trailing | PLAN | 10 (trailing exit: long exits < prior 10d low; short exits > prior 10d high); first-principles, NOT optimized |
| DA9 | exit_rule_TRAILING_DONCHIAN | PLAN | TRAILING_DONCHIAN_CHANNEL: position closes when price reverses through the opposite N_exit=10 channel (let winners run / cut losers). [LOAD-BEARING binding axis; trend variant] |
| DA10 | initial_catastrophe_stop_atr | DRAFT_PROPOSED | 2 x ATR(14) from entry (vol-scaled floor; whichever of trailing-channel / ATR-stop triggers first). [LOAD-BEARING] |
| DA11 | ATR_period | DRAFT_PROPOSED | 14 (equity-standard) |
| DA12 | sizing_method_vol_normalized | DRAFT_PROPOSED | shares = floor((0.005*equity) / (2*ATR14)); per-trade dollar risk constant, keyed to the initial 2xATR stop distance |
| DA13 | DR10_definition | DRAFT_BY_REFERENCE_TO_FRAMEWORK_SEAL_78cd22e | v2 AND-conjunction (turnover>0.50 AND S2_cost_drag>0.05); thresholds byte-equivalent |
| DA14 | DR9_data_continuity | DRAFT_CARRIED_BY_REUSE | ALL 12 PASS by REUSE of sealed CSVs at 245ac0d (result_seal ec856253...); NO fresh fetch; sha-verified at BUILD |
| DA15 | adjustment_convention | DRAFT_CONFIRMED | split_only (AMZN 20:1, WMT 3:1, NVDA 4:1/10:1, AAPL 4:1 applied+verified; JNJ Kenvue spin-off informational; dividends not adjusted) |
| DA16 | data_vendor | DRAFT_CONFIRMED | tiingo (data already fetched + DR9-sealed; no new fetch) |
| DA17 | universe | PLAN | 12 names {AAPL,MSFT,NVDA,JPM,XOM,UNH,WMT,KO,META,AMZN,JNJ,CVX} across ~7 GICS sectors |
| DA18 | portfolio_position_caps | PLAN | max_positions_per_name=1, max_total_positions=6, no inter-name coordination, no pyramid |
| DA19 | warmup_days | DRAFT_PROPOSED | 40 (covers N_entry=20 + ATR(14) + margin) |
| DA20 | signal_direction | PLAN | bi-directional (long+short) per-name |

## 3. DR9 (PASSED all 12 by reuse - no fetch)
12 CSVs reuse the DR9-PASSED sealed dir (`245ac0d`, result_seal `ec856253`); sha-verified at BUILD.

## 4. Reachability
K9: Donchian-20/10 on 12 names ~96-180/y -> clears IS (>=20/y) + OOS (>=50/y). DR10 v2 clears (cost_drag ~0.3-0.8% <<5%). K1/K2 are the binding edge gates (tested at P6 IS). A7/K10/K6 LOAD-BEARING (not the risk axis).

## 5. Freshness
NON-mean-reversion Donchian trend; clears T-FORBID-16/17/18; distinguished from s12-d1 futures Donchian. s15/s14 chains preserved.

## 6. C6 inherited_constraints (forming; locked at SEAL; 16 entries)
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

## 7. Boundaries
DRAFT only - no SEAL/BUILD/backtest/fetch/OOS - no strategy optimization - DR10 v2 by-ref - DR9 by reuse - no MR re-skin - no _revN_/revival - no sealed-artifact mod (incl. s16 DR9 result + 12 CSVs) - no lessons.md - no commit by script.

## 8. Next
Commit: `Authorize commit s16-d1 expanded-universe trend/breakout Tier-N spec DRAFT only.` - Forward: `Authorize s16-d1 expanded-universe trend/breakout Tier-N spec SEAL only -- bound by DR10 v2.`

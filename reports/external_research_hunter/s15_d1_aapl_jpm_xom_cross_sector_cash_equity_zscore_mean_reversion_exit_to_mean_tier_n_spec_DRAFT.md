# s15-d1-cross-sector cash-equity z-score mean-reversion EXIT-TO-MEAN Tier-N spec DRAFT (SEALED)

**Candidate:** `s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean`
**Phase:** `TIER_N_SPEC_DRAFT` · **Lifecycle:** `S15_D1_CROSS_SECTOR_CASH_EQUITY_ZSCORE_EXIT_TO_MEAN_TIER_N_SPEC_DRAFT_SEALED`
**Authored (UTC):** `2026-05-28T19:59:19.461606Z`
**Report seal sha256:** `f9195b5261cd02c5b10279008273da819ed147229663def02183c9f4e3dcacdd`
**Authorization:** `Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean Tier-N spec DRAFT only — bound by DR10 v2.`
**Anchors:** PLAN `ae0f4fb` (sha `f6cb516ba7c8c833f8b94b7c...`) · selection plan `89d6838` · framework DR10 v2 `78cd22e`

## §1. First-principles exit/stop edge design (THE binding axis)

s14-d1-cross-sector cleared DR10-v2/K9/DR9/A7/K10 yet failed `FAIL_SAFETY` on per-trade edge (RSI-mid exit small winners + fixed 2N stop large losers → profit/loss<1 @ 54.31% win). This candidate's fix:

- **Exit = EXIT-TO-MEAN** — close on re-cross of the rolling mean (SMA_L midline); the exit *is* the reversion target.
- **Stop = vol-scaled catastrophe brake** — `entry ∓ S·σ_L`, S≈3.5 (wider than the k=2.0 entry band); a disaster brake, NOT a fixed 2N that truncates.
- **Time-stop** max-hold ≈10 bars fallback; **vol-normalized sizing** keyed to the stop distance.
- Expected effect (HYPOTHESIS, tested at P6 IS — not a claim): avg_win ↑, stop-frequency ↓ → profit/loss → ≥1.

## §2. DA register (DA1-DA20; proposed at DRAFT, locked at SEAL)

| Code | Name | Locked at | Resolution |
|---|---|---|---|
| DA1 | candidate_record_id | PLAN | s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean |
| DA2 | mechanic_family | PLAN | F-new: z-score / Bollinger-band mean-reversion with exit-to-mean (NON-RSI) |
| DA3 | per_trade_risk_pct | PLAN | B = 0.005 (0.5%); carried as proven-safe |
| DA4 | START_CASH_USD | PLAN_PROPOSED_CONFIRM_AT_SEAL | B = 100000 ($100k) |
| DA5 | K4_max_drawdown_magnitude_threshold | DRAFT_PROPOSED | 0.50 (50%) |
| DA6 | lookback_L | PLAN | 20 (Bollinger standard; first-principles, NOT optimized) |
| DA7 | cost_stress_tiers | DRAFT_PROPOSED | five_tier_S0_S1_S2_S3_S4 (0.0/1.0/1.5/2.0/3.0) |
| DA8 | entry_band_k_sigma | PLAN | 2.0 (Bollinger standard 2-sigma; entry long z<=-2.0, short z>=+2.0; first-principles, NOT optimized) |
| DA9 | exit_rule_EXIT_TO_MEAN | PLAN | EXIT-TO-MEAN: close long when close>=SMA_L (midline); close short when close<=SMA_L. The exit IS the reversion target. [LOAD-BEARING new binding axis] |
| DA10 | catastrophe_stop_vol_scaled | DRAFT_PROPOSED | entry -/+ S*sigma_L, S=3.5 (vol-scaled disaster brake; wider than k=2.0 entry band; NOT a fixed 2N ATR). [LOAD-BEARING new binding axis] |
| DA11 | time_stop_max_hold_bars | DRAFT_PROPOSED | M = 10 bars (fallback if mean not recovered within reversion horizon; first-principles, NOT tuned) |
| DA12 | sizing_method_vol_normalized | DRAFT_PROPOSED | shares = floor((0.005*equity) / (S*sigma_L)); per-trade dollar risk constant; keyed to the catastrophe-stop distance |
| DA13 | DR10_definition | DRAFT_BY_REFERENCE_TO_FRAMEWORK_SEAL_78cd22e | v2 AND-conjunction (annual_turnover>0.50 AND S2_cost_drag>0.05); thresholds byte-equivalent |
| DA14 | DR9_data_continuity | DRAFT_CARRIED_BY_REUSE | ALREADY PASSED all 3 (AAPL/JPM/XOM) — REUSE of sealed CSVs at b13af03 (result_seal a8ff9126...); NO fresh fetch; sha-verified at BUILD |
| DA15 | adjustment_convention | DRAFT_CONFIRMED | split_only (CONFIRMED; reuse same CSVs; AAPL 2020-08-31 4:1 already applied+verified; JPM/XOM no splits; dividends not adjusted) |
| DA16 | data_vendor | DRAFT_CONFIRMED | tiingo (data already fetched + sealed; no new fetch) |
| DA17 | universe | PLAN | {AAPL (Tech), JPM (Financials), XOM (Energy)} — held constant from s14-d1-cross-sector to ISOLATE the exit/stop variable |
| DA18 | portfolio_position_caps | PLAN | max_positions_per_name=1, max_total_positions=3, no inter-name coordination, no pyramid |
| DA19 | warmup_days | DRAFT_PROPOSED | 30 (covers lookback L=20 + margin) — CONFIRM AT SEAL |
| DA20 | signal_direction | PLAN | bi-directional (long+short symmetric) per-name |

## §3. DR9 (carried by REUSE — no fetch)

AAPL/JPM/XOM reuse the DR9-PASSED sealed CSVs (`b13af03`, result_seal `a8ff9126…`); split_only; sha-verified at BUILD. All 3 PASS. **No fresh fetch.**

## §4. DR / K-gates / reachability

DR precedence `DR7→DR1→DR9→DR10→DR6→DR4→DR2→DR3→DR5`; DR10 v2 by-reference (`78cd22e`); DR11 NOT IN CHAIN (unlevered). K11 NOT_APPLICABLE. **K1/K2** are the gates s14-d1-cross-sector failed — this candidate's exit/stop redesign targets clearing them (tested at P6 IS). K9 reachability CLEARS (~60-105/y basket); **K9 is NOT the binding low**. DR10 v2 CLEARS with strong margin (cost_drag ~0.3-0.6% << 5%). A7/K10/K6 LOAD-BEARING but already in-band for this universe (not the risk axis).

## §5. Freshness / forbidden-track clearance

NON-RSI z-score family; exit-to-mean; vol-scaled catastrophe stop. Universe held constant to isolate the exit/stop variable. Clears **T-FORBID-13** (not RSI(3)+2N), **T-FORBID-14** (not a `_revN_`), **T-FORBID-15** (exit/stop first-principles justified). s14-d1-cross-sector chain preserved terminal/byte-stable; all-tech DRAFT `214bae0` preserved (not advanced).

## §6. C6 inherited_constraints (forming; locked at SEAL; 16 entries)

1. REC1-equivalent (BINDING): OOS K9 reachable on the cross-sector basket (expected ~60-105/y basket-summed). If observed effective IS rate < 25/y basket-summed, OOS K9 unreachability becomes structurally probable -> PARKED_SAFE_BUT_OOS_INDETERMINATE per precedent. The chain shall NOT relax K9 at OOS.
2. EXIT/STOP-FIRST-PRINCIPLES (BINDING; NEW central thesis): the exit is EXIT-TO-MEAN (close on re-cross of SMA_L; the reversion target itself) and the stop is a vol-scaled catastrophe brake (S*sigma, S~3.5; NOT a fixed 2N). This design is the candidate's entire reason to exist after s14-d1-cross-sector FAIL_SAFETY (LESSON_S14_D1_002/003); it is a hypothesis to TEST at P6 IS, never assumed.
3. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%); carried as proven-safe sizing
4. DA4=B: START_CASH_USD = 100000 ($100k); DR10 v2 cost_drag clears strong margin for cash equity
5. exit/stop-first-principles + K9-reachability + DR10-v2-reachability disciplines applied at PLAN+DRAFT; binding for all subsequent phases
6. K9_THRESHOLD_INVIOLATE: closed_trades_basket_summed >= 100; no relaxation at any phase
7. Mechanic family z-score/Bollinger mean-reversion exit-to-mean (NON-RSI) LOCKED at PLAN
8. z-score params lookback L=20 + entry band k=2.0 first-principles (Bollinger standard, NOT optimized); exit-to-mean + catastrophe stop S~3.5 + time-stop M=10 to be JUSTIFIED (not tuned) and LOCKED at SEAL
9. DR10 = v2 AND-conjunction by-reference to framework SEAL 78cd22e; thresholds 0.50 turnover / 0.05 cost_drag immutable; no_dr_redefinition_post_seal
10. split_only adjustment convention CONFIRMED (DA15); reuse same DR9-passed CSVs; switching/mixing post-SEAL FORBIDDEN
11. Cross-sector universe {AAPL (Tech), JPM (Financials), XOM (Energy)} LOCKED at PLAN; held constant from s14-d1-cross-sector to isolate the exit/stop variable; widening/substitution post-SEAL FORBIDDEN
12. DR9 data-availability gate PASSED all 3 symbols by REUSE (sealed b13af03; result_seal a8ff9126...); data provenance locked; NO fresh fetch
13. A7 effective_independent_bets + K10 avg_pairwise_correlation + K6 dispersion LOAD-BEARING but NOT the candidate's risk axis (already measured in-band for this universe at s14-d1-cross-sector); the risk axis is per-trade edge under the new exit/stop design
14. s14-d1-cross-sector lifecycle terminal (FAIL_SAFETY; P7 6485ea9) preserved verbatim; this candidate is FRESH, NOT a _revN_/patch; clears T-FORBID-13/14/15
15. no_strategy_optimization_authorized: parameters are first-principles proposals to justify at SEAL, not grid-searched
16. P6 IS PASS (if reached) does NOT imply READY at OOS; P6 PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent

## §7. Boundaries held this DRAFT turn

DRAFT only · no SEAL/BUILD/backtest/simulator/signal/fetch/OOS · no strategy optimization · DR10 v2 by-reference (not redefined) · DR9 carried by reuse (not re-run) · **no `_revN_`/patch/revival of s14-d1-cross-sector or any terminal/parked candidate** · no modification of any sealed artifact (s14-d1-cross-sector chain, all-tech DRAFT 214bae0, multi-instrument, s13/s12, DR9 result, CSVs, DR10 v2 78cd22e) · **no `lessons.md`** · **no commit this turn**.

## §8. Next phase

- Commit: `Authorize commit s15-d1 cross-sector cash-equity z-score exit-to-mean Tier-N spec DRAFT only.`
- Forward: `Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean Tier-N spec SEAL only — bound by DR10 v2.`

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · REC1-equivalent binding · NOT a Tier-N SEAL.

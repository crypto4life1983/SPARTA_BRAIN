# s15-d1-cross-sector cash-equity z-score mean-reversion EXIT-TO-MEAN Tier-N specification (SEALED)

**Candidate:** `s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean`
**Phase:** `TIER_N_SPEC_SEAL` · **Lifecycle:** `S15_D1_CROSS_SECTOR_CASH_EQUITY_ZSCORE_EXIT_TO_MEAN_TIER_N_SPEC_SEALED`
**Authored (UTC):** `2026-05-28T20:03:33.087048Z`
**Report seal sha256:** `1a89df0f07c4360cb1969f02889cd6fa973b93e81b21f0b3e27c6adc3ff0903d`
**Authorization:** `Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean Tier-N spec SEAL only — bound by DR10 v2.`
**Anchors:** DRAFT `9f0ce14` (file sha `25ed180cdd09aa23eec2278b...`, report_seal `f9195b5261cd02c5b1027900...`) · PLAN `ae0f4fb` · selection plan `89d6838` · s14-d1-cross-sector P7 terminal `6485ea9` · framework DR10 v2 `78cd22e`

## §1. First-principles exit/stop edge design (LOCKED; the binding axis)

- **Exit = EXIT-TO-MEAN** (close on re-cross of SMA_L midline; the exit IS the reversion target).
- **Stop = vol-scaled catastrophe brake** `entry ∓ 3.5·σ_L` (wider than the k=2.0 entry band; **NOT** a fixed 2N).
- **Time-stop** max-hold 10 bars; **vol-normalized sizing** `shares=floor(risk$/(3.5·σ_L))`.
- Rationale: s14-d1-cross-sector failed FAIL_SAFETY (RSI-mid small winners + 2N large losers). Expected `avg_win↑ / stop-freq↓` is a **hypothesis to test at P6 IS, not a claim**.

## §2. DA register (DA1-DA20; LOCKED byte-equivalent)

| Code | Name | Locked value |
|---|---|---|
| DA1 | candidate_record_id | s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean |
| DA2 | mechanic_family | F-new: z-score / Bollinger-band mean-reversion with exit-to-mean (NON-RSI) |
| DA3 | per_trade_risk_pct | 0.005 |
| DA4 | START_CASH_USD | 100000 |
| DA5 | K4_max_drawdown_magnitude_threshold | 0.5 |
| DA6 | lookback_L | 20 |
| DA7 | cost_stress_tiers | [{"tier": "S0", "cost_scalar": 0.0, "slippage_scalar": 0.0}, {"tier": "S1", "cost_scalar": 1.0, "slippage_scalar": 1.0}, {"tier": "S2", "cost_scalar": 1.5, "slippage_scalar": 1.5}, {"tier": "S3", "cost_scalar": 2.0, "slippage_scalar": 2.0}, {"tier": "S4", "cost_scalar": 3.0, "slippage_scalar": 3.0}] |
| DA8 | entry_band_k_sigma | 2.0 |
| DA9 | exit_rule_EXIT_TO_MEAN | EXIT-TO-MEAN: close long when close>=SMA_L (midline); close short when close<=SMA_L. The exit IS the reversion target. [LOAD-BEARING binding axis] |
| DA10 | catastrophe_stop_vol_scaled_sigma_multiple | 3.5 |
| DA11 | time_stop_max_hold_bars | 10 |
| DA12 | sizing_method_vol_normalized | shares = floor((0.005*equity) / (3.5*sigma_L)); per-trade dollar risk constant; keyed to the catastrophe-stop distance |
| DA13 | DR10_definition | v2 AND-conjunction: (annual_turnover>0.50 AND S2_cost_drag>0.05) -> REJECT_FAST |
| DA14 | DR9_data_continuity | ALL 3 PASS (AAPL/JPM/XOM) by REUSE of sealed CSVs at b13af03 (result_seal a8ff9126...); NO fresh fetch; sha-verified at BUILD |
| DA15 | adjustment_convention | split_only |
| DA16 | data_vendor | tiingo (data already fetched + sealed; no new fetch) |
| DA17 | universe | ["AAPL", "JPM", "XOM"] |
| DA18 | portfolio_position_caps | max_positions_per_name=1, max_total_positions=3, no inter-name coordination, no pyramid |
| DA19 | warmup_days | 30 |
| DA20 | signal_direction | bi-directional (long+short symmetric) per-name |

## §3. DR9 (PASSED by reuse — no fetch)

AAPL/JPM/XOM reuse the DR9-PASSED sealed CSVs (`b13af03`, result_seal `a8ff9126…`); all 3 PASS; split_only; sha-verified at BUILD. **No fresh fetch.**

## §4. DR / K-gates / reachability

DR precedence `DR7→DR1→DR9→DR10→DR6→DR4→DR2→DR3→DR5`; DR10 v2 by-reference (`78cd22e`) CLEARS strong margin (S2 cost_drag ~0.3-0.6% << 5%); DR11 NOT IN CHAIN (unlevered); K11 NOT_APPLICABLE. K9 CLEARS (~60-105/y) — **NOT the binding low**. **K1/K2** (the gates s14-d1-cross-sector failed) are the candidate's risk axis, targeted by the §1 exit/stop redesign (tested at P6 IS). A7/K10/K6 LOAD-BEARING but already in-band for this universe.

## §5. C6 inherited_constraints_block (LOCKED; 16 entries)

1. REC1-equivalent (BINDING): OOS K9 reachable on the cross-sector basket (expected ~60-105/y basket-summed). If observed effective IS rate < 25/y basket-summed, OOS K9 unreachability becomes structurally probable -> PARKED_SAFE_BUT_OOS_INDETERMINATE per precedent. The chain shall NOT relax K9 at OOS.
2. EXIT/STOP-FIRST-PRINCIPLES (BINDING; central thesis): exit = EXIT-TO-MEAN (close on re-cross of SMA_L; the reversion target itself); stop = vol-scaled catastrophe brake (3.5*sigma_L; NOT a fixed 2N). This is the candidate's entire reason to exist after s14-d1-cross-sector FAIL_SAFETY (LESSON_S14_D1_002/003); a hypothesis to TEST at P6 IS, never assumed.
3. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%); proven-safe sizing
4. DA4=B (BINDING): START_CASH_USD = 100000 ($100k); DR10 v2 cost_drag clears strong margin for cash equity
5. exit/stop-first-principles + K9-reachability + DR10-v2-reachability disciplines applied at PLAN+DRAFT+SEAL; binding for all subsequent phases
6. K9_THRESHOLD_INVIOLATE: closed_trades_basket_summed >= 100; no relaxation at any phase
7. Mechanic family z-score/Bollinger mean-reversion exit-to-mean (NON-RSI) LOCKED at PLAN
8. z-score params LOCKED at SEAL: lookback L=20, entry band k=2.0, exit-to-mean, catastrophe stop 3.5*sigma, time-stop 10, vol-normalized sizing; modification post-SEAL FORBIDDEN
9. DR10 = v2 AND-conjunction by-reference to framework SEAL 78cd22e; thresholds 0.50 turnover / 0.05 cost_drag immutable; no_dr_redefinition_post_seal
10. split_only adjustment convention LOCKED (DA15); reuse same DR9-passed CSVs; switching/mixing post-SEAL FORBIDDEN
11. Cross-sector universe {AAPL (Tech), JPM (Financials), XOM (Energy)} LOCKED at PLAN; held constant from s14-d1-cross-sector to isolate the exit/stop variable; widening/substitution post-SEAL FORBIDDEN
12. DR9 data-availability gate PASSED all 3 symbols by REUSE (sealed b13af03; result_seal a8ff9126...); data provenance locked; NO fresh fetch; cash_equity_data_reuse_byte_equivalent
13. A7 effective_independent_bets + K10 avg_pairwise_correlation + K6 dispersion LOAD-BEARING but NOT the candidate's risk axis (already measured in-band for this universe at s14-d1-cross-sector); the risk axis is per-trade edge (K1/K2) under the new exit/stop design
14. s14-d1-cross-sector lifecycle terminal (FAIL_SAFETY; P7 6485ea9) preserved verbatim; this candidate is FRESH, NOT a _revN_/patch; clears T-FORBID-13/14/15
15. no_strategy_optimization_authorized: all parameters first-principles justified at SEAL, NOT grid-searched
16. P6 IS PASS (if reached) does NOT imply READY at OOS; P6 PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent

## §6. Freshness

NON-RSI z-score family; exit-to-mean; vol-scaled catastrophe stop. Clears T-FORBID-13/14/15. NOT a `_revN_`/patch. s14-d1-cross-sector chain + all-tech DRAFT `214bae0` preserved byte-stable.

## §7. Boundaries held this SEAL turn

SEAL only (no P1) · all DA locked byte-equivalent · DR10 v2 by-reference (not redefined) · DR9 carried by reuse · no build/backtest/fetch/OOS/Strategy Lab · no strategy optimization · no `_revN_`/patch/revival · no modification of any sealed artifact (incl. DRAFT 9f0ce14, all-tech 214bae0, DR9 result, CSVs, DR10 v2 78cd22e) · **no `lessons.md`** · **no commit this turn**.

## §8. Next phase

- Commit: `Authorize commit s15-d1 cross-sector cash-equity z-score exit-to-mean Tier-N spec SEAL only.`
- Forward: `Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean P1 plan-lock only — bound by DR10 v2.`

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · REC1-equivalent binding.

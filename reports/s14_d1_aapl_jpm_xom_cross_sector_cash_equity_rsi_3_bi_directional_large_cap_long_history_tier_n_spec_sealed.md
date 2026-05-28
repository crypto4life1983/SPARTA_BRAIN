# s14-d1-cross-sector cash-equity Tier-N specification (SEALED)

**Phase:** `TIER_N_SPEC_SEAL` (canonical immutable spec)
**Authored (UTC):** `2026-05-28T18:30:20.610231Z`
**Lifecycle state:** `S14_D1_CROSS_SECTOR_CASH_EQUITY_TIER_N_SPEC_SEALED`
**Report seal sha256:** `862c00a5ffcc470580b6defe9c31ce89c4a43114ad418b4b6b4dfb991500569c`
**Candidate:** `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history`
**Authorization:** `Authorize s14-d1-cross-sector cash-equity Tier-N spec SEAL only — bound by DR10 v2.`

## §1. Parent references

| Field | Value |
|---|---|
| Tier-N PLAN | commit `c61860d` (sha `3acf6e3f26dfaf77773e1da05487b794ad6329f37a4fda767fa821b8157f12a2`) |
| Tier-N DRAFT | commit `bfb6495` (sha `be9a4835b7c7ce69474eb8ba7b144e5385852ed4ef9eca4e9476e757a98d5164`) |
| Cross-sector DR9 result | commit `b13af03` · report_seal `a8ff91263e64529d52ac8b974ec01d8517d4bc7187df124b9938323870078a9c` · verdict `DR9_ALL_3_PASS_CROSS_SECTOR_BASKET_READY_FOR_DRAFT` |
| All-tech sibling DRAFT (preserved byte-stable) | commit `214bae0` |
| Framework DR10 v2 | commit `78cd22e` |
| Vendor / convention | tiingo / split_only |

## §2. DA register — ALL LOCKED byte-equivalent at SEAL

| Code | Name | Locked value |
|---|---|---|
| DA1 | candidate_record_id | `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history` |
| DA2 | mechanic_family | `F3-adjacent RSI(3) bi-directional mean-reversion` |
| DA3 | per_trade_risk_pct | `0.005` |
| DA4 | START_CASH_USD | `100000` |
| DA5 | K4_max_drawdown_magnitude_threshold | `0.5` |
| DA6 | RSI_period | `3` |
| DA7 | cost_stress_tiers | `[{'tier': 'S0', 'cost_scalar': 0.0, 'slippage_scalar': 0.0}, {'tier': 'S1', 'cost_scalar': 1.0, 'slippage_scalar': 1.0}, {'tier': 'S2', 'cost_scalar': 1.5, 'slippage_scalar': 1.5}, {'tier': 'S3', 'cost_scalar': 2.0, 'slippage_scalar': 2.0}, {'tier': 'S4', 'cost_scalar': 3.0, 'slippage_scalar': 3.0}]` |
| DA8 | RSI_long_entry_threshold | `15` |
| DA9 | RSI_long_exit_threshold | `55` |
| DA10 | RSI_short_entry_threshold | `85` |
| DA11 | RSI_short_exit_threshold | `45` |
| DA12 | ATR_period | `14` |
| DA13 | ATR_stop_multiplier_in_ATR | `2.0` |
| DA14 | DR10_definition | `v2 AND-conjunction: (annual_turnover>0.50 AND S2_cost_drag>0.05) -> REJECT_FAST` |
| DA15 | DR9_data_continuity | `0.95/0.30/NOT_APPLICABLE_roll/5 + documented_split_event_consistency; ALL 3 PASSED (sealed a8ff9126...)` |
| DA16 | warmup_days | `30` |
| DA17 | adjustment_convention | `split_only` |
| DA18 | data_vendor | `tiingo (split_only via splitFactor stream)` |
| DA19 | universe | `['AAPL', 'JPM', 'XOM']` |
| DA20 | portfolio_position_caps | `max_positions_per_name=1, max_total_positions=3, no inter-name coordination, no pyramid` |

DRAFT_PROPOSED items resolved at SEAL: DA4 START_CASH=$100k; DA12 ATR_period=14 (equity-standard); DA13 ATR_multiplier=2.0; DA16 warmup=30; DA5 K4=0.50; DA7 cost-stress S0-S4; cost surface ($0.005/share, $1 min, ~1bps slippage).

## §3. C6 inherited_constraints_block (16 entries)

1. REC1-equivalent (BINDING): OOS K9 reachable with improved margin vs all-tech (cross-sector higher signal independence ~75% vs all-tech ~60%; expected effective rate 45-79/y vs 50/y OOS floor). If observed effective IS rate falls below 25/y basket-summed, OOS K9 unreachability becomes structurally probable -> PARKED_SAFE_BUT_OOS_INDETERMINATE per s10-d2/s12-d1 precedent. The chain shall NOT relax K9 at OOS.
2. DA3=B (BINDING): per-trade risk pct = 0.005 (0.5%); standard sizing (not nano); admissible under DR10 v2 for cash equity
3. DA4=B (BINDING): START_CASH_USD = 100000 ($100k); DR10 v2 cost_drag clears strong margin at $100k for cash equity
4. K9-reachability discipline applied at PLAN+DRAFT+SEAL; binding for all subsequent phases
5. DR10-v2-reachability discipline applied at PLAN+DRAFT+SEAL (AND-conjunction); CLEARS WITH STRONG MARGIN
6. K9_THRESHOLD_INVIOLATE: closed_trades_basket_summed >= 100; no relaxation at any phase
7. Mechanic family F3-adjacent RSI(3) bi-directional mean-reversion LOCKED at PLAN
8. RSI thresholds 15/55/85/45 LOCKED at PLAN; modification post-SEAL FORBIDDEN
9. DR10 = v2 AND-conjunction by-reference to framework SEAL 78cd22e; thresholds 0.50 turnover / 0.05 cost_drag immutable; no_dr_redefinition_post_seal
10. split_only adjustment convention LOCKED (DA17); switching/mixing post-SEAL FORBIDDEN
11. Cross-sector universe {AAPL (Tech), JPM (Financials), XOM (Energy)} LOCKED at PLAN; universe widening/substitution post-SEAL FORBIDDEN
12. A7 effective_independent_bets + K10 avg_pairwise_correlation LOAD-BEARING (multi-name cross-sector; A7 ~2.3-2.8 / K10 ~0.30-0.50 expected; the candidate's central diversification thesis)
13. Cross-sector DR9 data-availability gate PASSED all 3 symbols (AAPL reused+carried; JPM/XOM fresh-fetched+audited); sealed at b13af03 report_seal a8ff9126...; data provenance locked
14. All-tech sibling DRAFT (214bae0) preserved byte-stable; non-mutually-exclusive sibling; this candidate is NOT a _revN_
15. P6 IS PASS (if reached) does NOT imply READY at OOS; OOS requires separate P10-equivalent authorization
16. P6 PASS NEVER implies live-readiness; 6-gate live-block applies regardless of any verdict; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE permanent

## §4. DR register (DR10 = v2 AND-conjunction)

DR precedence chain: `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5`. DR9 already PASSED all 3 symbols (sealed `a8ff91263e64529d...`). DR10 v2 CLEARS WITH STRONG MARGIN. DR11 NOT IN CHAIN.

## §5. K-gates

K9 inviolate (closed_trades_basket_summed ≥ 100). K10 avg_pairwise_correlation + K6 per_symbol_dispersion + A7 effective_independent_bets LOAD-BEARING (cross-sector; A7 ~2.3-2.8 / K10 ~0.30-0.50 expected — the candidate's central diversification thesis). K11 NOT_APPLICABLE (unlevered).

## §6. Status

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s13-d1 + s12-d1 terminal · framework DR10 v2 binding. **s14-d1-cross-sector lifecycle: `S14_D1_CROSS_SECTOR_CASH_EQUITY_TIER_N_SPEC_SEALED`.** All-tech sibling DRAFT (214bae0) preserved byte-stable.

## §7. Hard boundaries held this SEAL turn

SEAL only · no P1 plan-lock · no BUILD · no fetch/refetch · no backtest/simulator/OOS · no live/Strategy Lab · no candidate promotion · no s13-d1/s12-d1/parked revival · **no modification of any existing sealed artifact** (cross-sector DR9 result + DRAFT bfb6495 + PLAN c61860d + fetched CSVs/manifest + all-tech DRAFT 214bae0 + s14-d1-multi-instrument chain + s13-d1/s12-d1 chains + framework DR10 v2 78cd22e all byte-stable) · no phase-2-safety-contract / CLAUDE.md / .gitignore modification · **no `lessons.md` modification or staging** · no review_queue/idea_memory mutation · no profitability claim · DR10 v2 by-reference (not redefined) · all DA resolutions locked byte-equivalent · **no commit by this turn**.

## §8. Next-phase authorization scope

- **Commit this SEAL:** `Authorize commit s14-d1-cross-sector cash-equity Tier-N spec SEAL only.`
- **Primary forward:** `Authorize s14-d1-cross-sector cash-equity P1 plan-lock only — bound by DR10 v2.`
- **Defer:** `Defer / Pause s14-d1-cross-sector cash-equity at SEAL.`

Then: P2 phase-2 plan → P3 BUILD → P4 smoke → P6 IS diagnostic → P6.5 cost-stress → P7 decision memo (each separate authorization).

End of Tier-N spec SEAL. Canonical immutable spec; all DA1-DA20 locked byte-equivalent; C6 16 entries; DR10 v2 binding; DR9 PASSED carried; A7 cross-sector improvement is the central thesis. Not committed this turn. Subsequent phases anchor to this SEAL.

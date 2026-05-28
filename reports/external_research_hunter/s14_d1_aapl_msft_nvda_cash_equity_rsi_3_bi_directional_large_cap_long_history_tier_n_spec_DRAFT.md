# s14-d1-cash-equity 3-name basket RSI(3) bi-directional Tier-N specification DRAFT (sealed)

**Phase:** `TIER_N_SPEC_DRAFT`
**Authored (UTC):** `2026-05-28T17:14:11.046390Z`
**Lifecycle state:** `S14_D1_CASH_EQUITY_TIER_N_SPEC_DRAFT_SEALED`
**Report seal sha256:** `95d3c491801d18748a47e216913056562a7188aaf44661be782f02a5d35ea5d9`
**Candidate record id:** `s14-d1-aapl-msft-nvda-cash-equity-rsi-3-bi-directional-large-cap-long-history`
**Authorization phrase:** `Authorize s14-d1-cash-equity Tier-N spec DRAFT only — bound by DR10 v2.`

**This is a DRAFT, NOT a Tier-N SEAL.** The SEAL is a separate authorization that locks all DA-register resolutions byte-equivalent.

----

## §1. Parent references + DR9 gate status

| Field | Value |
|---|---|
| Tier-N spec PLAN | commit `a6cbafd` (sha `6a3a186aa665829abca3e5a40b770ae8df44438f2f0f888a4f482cebda8a5bdd`) |
| Availability-probe RUN_BOOK | commit `529bb6b` |
| **DR9 audit result (sealed)** | report_seal `1c93d4294e193b25b239fd613f4ff1e9d24a16860376ee31efd7ec2ef01eda40` (file sha `963f3477fe90a734230fa465802f24ddd09c125635e677dc152e42ecabe15362`) |
| **DR9 verdict** | **`DR9_ALL_3_PASS_BASKET_READY_FOR_DRAFT`** |
| DR9 per-symbol | AAPL `PASS` · MSFT `PASS` · NVDA `PASS` |
| Vendor | tiingo |
| Adjustment convention | split_only (confirmed; NVDA 10:1 split-event consistency PASS) |
| Framework DR10 binding | v2 AND-conjunction (commit `78cd22e`) |

The DR9 data-availability gate has PASSED for all 3 symbols; the data provenance is locked (sha-verified). This DRAFT carries that PASS forward — it does NOT re-run the audit.

----

## §2. Structural locks carried from PLAN (immutable from PLAN)

| Field | Locked value |
|---|---|
| Mechanic family | F3-adjacent RSI(3) bi-directional mean-reversion |
| RSI period | 3 |
| RSI thresholds (long entry / long exit / short entry / short exit) | 15 / 55 / 85 / 45 |
| Signal direction | bi-directional |
| Universe | {AAPL, MSFT, NVDA} |
| Per-name max positions | 1 |
| Portfolio max positions | 3 |
| Inter-name signal coordination | NONE |
| Pyramid | NONE |
| DA3 per-trade risk pct | 0.005 (0.5%) |
| DA4 START_CASH (proposed) | $100,000 |

----

## §3. DA (Design Adjustment) register — DA1 through DA20

| Code | Name | Resolution | Locked at |
|---|---|---|---|
| DA1 | candidate_record_id | `s14-d1-aapl-msft-nvda-cash-equity-rsi-3-bi-directional-large-cap-long-history` | PLAN |
| DA2 | mechanic_family | `F3-adjacent RSI(3) bi-directional mean-reversion` | PLAN |
| DA3 | per_trade_risk_pct | `B = 0.005 (0.5%)` | PLAN |
| DA4 | START_CASH_USD | `B = 100000 ($100k)` | PLAN_PROPOSED_CONFIRM_AT_SEAL |
| DA5 | K4_max_drawdown_magnitude_threshold | `A = 0.50 (50% fail-safety)` | DRAFT_PROPOSED |
| DA6 | RSI_period | `3 (Connors RSI-3)` | PLAN |
| DA7 | cost_stress_tiers | `A = five_tier_S0_S1_S2_S3_S4 (scalars 0.0/1.0/1.5/2.0/3.0)` | DRAFT_PROPOSED |
| DA8 | RSI_long_entry_threshold | `< 15 (oversold)` | PLAN |
| DA9 | RSI_long_exit_threshold | `> 55` | PLAN |
| DA10 | RSI_short_entry_threshold | `> 85 (overbought; symmetric)` | PLAN |
| DA11 | RSI_short_exit_threshold | `< 45` | PLAN |
| DA12 | ATR_period | `PROPOSED 14 (equity-standard) — CONFIRM AT SEAL (s13-d1 used 20; equity convention often 14)` | DRAFT_PROPOSED |
| DA13 | ATR_stop_multiplier_in_ATR | `2.0 (2N stop)` | DRAFT_PROPOSED |
| DA14 | DR10_definition | `v2 AND-conjunction (annual_turnover>0.50 AND S2_cost_drag>0.05); thresholds 0.50/0.05 byte-equivalent` | DRAFT_BY_REFERENCE_TO_FRAMEWORK_SEAL_78cd22e |
| DA15 | DR9_data_continuity_thresholds | `0.95 / 0.30 / NOT_APPLICABLE_CASH_EQUITY (roll) / 5 + documented_split_event_consistency` | DRAFT_CONFIRMED_BY_PASSED_AUDIT |
| DA16 | warmup_days | `PROPOSED 30 (covers RSI(3)+ATR(14) lookback with margin) — CONFIRM AT SEAL` | DRAFT_PROPOSED |
| DA17 | adjustment_convention | `split_only (CONFIRMED available + applied; DR9 split-event-consistency PASS all 3 symbols)` | DRAFT_CONFIRMED |
| DA18 | data_vendor | `Tiingo (split_only via splitFactor stream)` | DRAFT_CONFIRMED |
| DA19 | universe | `{AAPL, MSFT, NVDA} (3-name large-cap basket)` | PLAN |
| DA20 | portfolio_position_caps | `max_positions_per_name=1, max_total_positions=3, no inter-name signal coordination` | PLAN |

**Locked-at legend:** `PLAN` = locked at PLAN (immutable); `DRAFT_CONFIRMED` = confirmed this DRAFT turn (e.g., split_only feasibility verified via passed fetch); `DRAFT_PROPOSED` = proposed this DRAFT, to be locked byte-equivalent at SEAL; `PLAN_PROPOSED_CONFIRM_AT_SEAL` = PLAN proposal, operator confirms at SEAL; `DRAFT_BY_REFERENCE...` = carried by-reference to framework SEAL.

----

## §4. Cost surface (equity-specific; proposed at DRAFT; locked at SEAL)

| Field | Proposed value |
|---|---|
| Commission model | per_share |
| Commission per share | $0.005 |
| Min commission per trade | $1.00 |
| Slippage model | half_bid_ask_spread_proxy |
| Slippage proxy | ~1.0 bps |

Equity cost surface is structurally lower-drag than micro-futures contract-quantization. Exact constants locked at SEAL; cost-stress matrix (S0-S4) applies these × scalars at the P6.5-equivalent phase.

----

## §5. K-gates

- `K1_sharpe_proxy_lt_0`: if sharpe_proxy_per_trade < 0 at S1 -> FAIL_SAFETY
- `K2_expectancy_le_0`: if expectancy_per_trade_usd <= 0 at S1 -> FAIL_SAFETY
- `K4_trade_curve_maxdd_gt_50`: if |maxdd| > 50% (DA5=A) -> FAIL_SAFETY
- `K6_per_symbol_dispersion`: APPLICABLE (multi-name); thresholds carried from s10-d2 chain; LOAD-BEARING at SEAL
- `K7_filter_silently_introduced`: if any filter/regime/correlation gate introduced post-SEAL -> FAIL_SAFETY
- `K8_sealed_parent_drift`: if any sealed parent seal mismatches embedded constant -> FAIL_SAFETY
- `K9_closed_trades_lt_100`: if closed_trades_basket_summed < 100 -> INSUFFICIENT_SAMPLE (NOT FAIL_SAFETY); INVIOLATE
- `K10_avg_pairwise_corr`: APPLICABLE (multi-name); expected 0.70-0.85 (US large-cap tech); LOAD-BEARING at SEAL
- `K11_cap_binding_events`: NOT_APPLICABLE_NO_LEVERAGE_CAP (cash equity unlevered)
- `K12_DR_fires_on_cost_stress`: if any DR2/DR3/DR4/DR5 fires across S0/S2/S3/S4 cost-stress sweep at P6.5-equivalent -> FAIL_SAFETY

----

## §6. DR register (DR10 = v2 AND-conjunction)

| Rule | Definition |
|---|---|
| `DR1` | oos_rebalance_count<36 OOS-phase only -> INCONCLUSIVE_HOLD |
| `DR2` | oos_metrics_degrade_materially_under_cost_stress -> REJECT_FAST (OOS-only) |
| `DR3` | zero_cost_only_survival (S0>0 AND all S1..S4<=0) -> REJECT_FAST (RSI-lineage HIGHER prior; cash-equity multi-name hypothesis-fresh) |
| `DR4` | oos_negative_while_is_positive_unexplained -> REJECT_FAST (OOS-only) |
| `DR5` | cost_stress_turns_edge_negative tier flip -> REJECT_FAST / INCONCLUSIVE_HOLD carveout |
| `DR6` | post_warmup_sizing_ambiguity_or_invalid -> REJECT_FAST (per-name) |
| `DR7` | missing_oos_or_date_window_evidence -> INCONCLUSIVE_HOLD |
| `DR8` | live_or_order_routing_path_detected at Initialize -> HARD_FAIL_VOIDED |
| `DR9` | data_continuity_integrity_check (per-name; thresholds 0.95/0.30/NOT_APPLICABLE_roll/5 + documented_split_event_consistency) -> INCONCLUSIVE_HOLD. STATUS: ALREADY PASSED all 3 symbols (sealed result_seal 1c93d4294e...) |
| `DR10_v2` | turnover_cost_explosion (annual_turnover>0.50 AND S2_cost_drag>0.05) byte-equivalent (DA14) -> REJECT_FAST. AND-conjunction per framework SEAL 78cd22e. Cash-equity cost_drag branch clears with strong margin (~0.3-0.6% S2 << 5%); turnover branch alone does NOT fire under AND |
| `DR11` | NOT IN CHAIN — cash equity unlevered; no leverage cap |

**DR precedence chain:** `DR7 -> DR1 -> DR9 -> DR10 -> DR6 -> DR4 -> DR2 -> DR3 -> DR5`

----

## §7. K9-reachability (DRAFT)

| Window | Required/y | Expected basket effective | Total | Status |
|---|---|---|---|---|
| IS (5.0y) | ≥ 20.0 | 36-63/y | 180-315 | CLEARS WITH MARGIN (9-16x) |
| OOS (2.0y) | ≥ 50.0 | 36-63/y | 72-126 | CLEARS central/high; **BORDERLINE at low (36<50)** |

REC1-equivalent (BINDING): if observed effective IS rate < 25/y basket-summed, OOS K9 fires → PARK per precedent. **K9 OOS risk MODERATE.**

----

## §8. DR10-v2-reachability (DRAFT): CLEARS WITH STRONG MARGIN

- Expected annual_turnover ~30-60 (turnover branch fires alone — non-binding under AND)
- Expected S2 cost_drag ~0.3-0.6% (per-share commission tiny fraction of notional; well under 5%)
- AND-conjunction does NOT trigger → DR10 v2 CLEARS

----

## §9. Diversification metrics (LOAD-BEARING at SEAL)

- **A7 effective_independent_bets:** expected 1.5-2.0 (**POTENTIAL CONCERN** — all-tech basket ~0.7-0.85 pairwise correlation)
- K10 avg_pairwise_correlation: expected 0.70-0.85
- K6 per_symbol_dispersion: TBD at SEAL
- A6 concentration_index: NVDA-dominance risk (s7-D1 USO-dominance analog)
- **Cross-sector revision option:** operator may revise universe to cross-sector (e.g., `{AAPL, JPM, XOM}`) at a fresh sibling PLAN for stronger A7 before SEAL.

----

## §10. Hard boundaries held this DRAFT turn (40+ True)

DRAFT only · no Tier-N SEAL · no BUILD · no data fetch · no data refetch · no backtest · no simulator · no signal computation · no OOS inspection · no live trading · no broker/exchange API · no Strategy Lab invocation/promotion · no candidate promotion · no FRC grant · no live-block relaxation · no s13-d1/s12-d1/parked revival · **no modification of any existing sealed artifact** (DR9 result sealed + fetched CSVs/manifest + s14-d1-cash-equity PLAN `a6cbafd` + RUN_BOOK `529bb6b` + s14-d1-multi-instrument chain + s13-d1/s12-d1/s11-d1 chains + framework DR10 v2 `78cd22e` all byte-stable) · no phase-2-safety-contract / CLAUDE.md / .gitignore modification · **no `lessons.md` modification or staging** · no review_queue/idea_memory mutation · no profitability claim · no DR redefinition post-SEAL · no RSI threshold modification from PLAN · no universe widening · DR10 v2 carried by-reference (not redefined) · DR9 gate PASS carried (not re-run).

----

## §11. Status

trading: `PAUSED` · live: `BLOCKED_AT_6_GATES` · FRC: `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s13-d1 + s12-d1 lifecycles terminal · framework DR10 v2 binding for s14+. **s14-d1-cash-equity lifecycle advanced to `S14_D1_CASH_EQUITY_TIER_N_SPEC_DRAFT_SEALED`.**

----

## §12. Next-phase authorization scope

- **Primary forward:** `Authorize s14-d1-cash-equity Tier-N spec SEAL only — bound by DR10 v2.` (locks all DA-register resolutions byte-equivalent; produces the sealed Tier-N spec; P1/P2/P3 BUILD/P4/P6/P6.5/P7 follow under separate authorizations)
- **Universe revision:** `Authorize s14-d1-cash-equity universe revision to cross-sector basket — bound by DR10 v2.` (fresh sibling candidate for stronger A7 before SEAL)
- **Defer:** `Defer / Pause s14-d1-cash-equity at DRAFT.`

----

End of Tier-N spec DRAFT. Sealed DRAFT (not a Tier-N SEAL). DA register DA1-DA20 expanded; split_only convention confirmed; DR9 data-availability gate PASSED and carried; DR10 v2 reachability CLEARS with strong margin; K9 OOS risk MODERATE (REC1 binding); A7 diversification concern flagged load-bearing for SEAL. Next phase = Tier-N spec SEAL (separate authorization).

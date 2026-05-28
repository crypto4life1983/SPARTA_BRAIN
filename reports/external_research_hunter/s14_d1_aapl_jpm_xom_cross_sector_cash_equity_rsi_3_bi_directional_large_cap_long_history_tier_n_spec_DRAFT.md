# s14-d1-cross-sector cash-equity 3-name basket RSI(3) bi-directional Tier-N specification DRAFT (sealed)

**Phase:** `TIER_N_SPEC_DRAFT` (NOT a Tier-N SEAL)
**Authored (UTC):** `2026-05-28T18:24:49.230108Z`
**Lifecycle state:** `S14_D1_CROSS_SECTOR_CASH_EQUITY_TIER_N_SPEC_DRAFT_SEALED`
**Report seal sha256:** `ad5f046043bb137b83f6cb0a9270e848be644acd2152bb4f95f8ca05c834e764`
**Candidate:** `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history`
**Authorization:** `Authorize s14-d1-cross-sector cash-equity Tier-N spec DRAFT only — bound by DR10 v2.`

## §1. Parent references + cross-sector DR9 gate status

| Field | Value |
|---|---|
| Tier-N spec PLAN | commit `c61860d` (sha `3acf6e3f26dfaf77773e1da05487b794ad6329f37a4fda767fa821b8157f12a2`) |
| **Cross-sector DR9 result (sealed)** | commit `b13af03` · report_seal `a8ff91263e64529d52ac8b974ec01d8517d4bc7187df124b9938323870078a9c` (file sha `a3712d58d6820433db9b98a5ae0de59c3f363132c3cbde2500583aa83bd1679c`) |
| **DR9 verdict** | **`DR9_ALL_3_PASS_CROSS_SECTOR_BASKET_READY_FOR_DRAFT`** |
| DR9 per-symbol | AAPL `PASS` (reused/carried) · JPM `PASS` (fresh) · XOM `PASS` (fresh) |
| Vendor / convention | tiingo / split_only |
| All-tech DRAFT (model; preserved byte-stable) | commit `214bae0` (sha `ae3a635c8f173e1b99f9d738bd9a8ce6a0aae86f0eedcacff0e215ee37b5223d`) |
| Framework DR10 binding | v2 AND-conjunction (commit `78cd22e`) |

Cross-sector DR9 data-availability gate PASSED for all 3 symbols; provenance locked. This DRAFT carries that PASS — it does NOT re-run the audit.

## §2. Structural locks carried from PLAN

Mechanic F3 RSI(3) bi-directional · thresholds 15/55/85/45 · bi-directional · universe {AAPL (Tech), JPM (Financials), XOM (Energy)} · per-name max 1 / portfolio max 3 · no inter-name coordination · DA3=B 0.5% · DA4=B $100k proposed.

## §3. DA register DA1-DA20

| Code | Name | Resolution | Locked at |
|---|---|---|---|
| DA1 | candidate_record_id | `s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history` | PLAN |
| DA2 | mechanic_family | `F3-adjacent RSI(3) bi-directional mean-reversion` | PLAN |
| DA3 | per_trade_risk_pct | `B = 0.005 (0.5%)` | PLAN |
| DA4 | START_CASH_USD | `B = 100000 ($100k)` | PLAN_PROPOSED_CONFIRM_AT_SEAL |
| DA5 | K4_max_drawdown_magnitude_threshold | `A = 0.50 (50%)` | DRAFT_PROPOSED |
| DA6 | RSI_period | `3 (Connors)` | PLAN |
| DA7 | cost_stress_tiers | `A = five_tier_S0_S1_S2_S3_S4 (0.0/1.0/1.5/2.0/3.0)` | DRAFT_PROPOSED |
| DA8 | RSI_long_entry_threshold | `< 15` | PLAN |
| DA9 | RSI_long_exit_threshold | `> 55` | PLAN |
| DA10 | RSI_short_entry_threshold | `> 85` | PLAN |
| DA11 | RSI_short_exit_threshold | `< 45` | PLAN |
| DA12 | ATR_period | `PROPOSED 14 (equity-standard) — CONFIRM AT SEAL` | DRAFT_PROPOSED |
| DA13 | ATR_stop_multiplier_in_ATR | `2.0 (2N stop)` | DRAFT_PROPOSED |
| DA14 | DR10_definition | `v2 AND-conjunction (turnover>0.50 AND S2_cost_drag>0.05); thresholds byte-equivalent` | DRAFT_BY_REFERENCE_TO_FRAMEWORK_SEAL_78cd22e |
| DA15 | DR9_data_continuity | `0.95/0.30/NOT_APPLICABLE_roll/5 + documented_split_event_consistency — ALL 3 PASSED (sealed result_seal a8ff9126...)` | DRAFT_CONFIRMED_BY_PASSED_AUDIT |
| DA16 | warmup_days | `PROPOSED 30 (covers RSI(3)+ATR(14)) — CONFIRM AT SEAL` | DRAFT_PROPOSED |
| DA17 | adjustment_convention | `split_only (CONFIRMED; AAPL 4:1 verified; JPM/XOM no splits)` | DRAFT_CONFIRMED |
| DA18 | data_vendor | `Tiingo (split_only via splitFactor stream)` | DRAFT_CONFIRMED |
| DA19 | universe | `{AAPL (Tech), JPM (Financials), XOM (Energy)} — cross-sector for improved A7` | PLAN |
| DA20 | portfolio_position_caps | `max_positions_per_name=1, max_total_positions=3, no inter-name coordination` | PLAN |

## §4. K9-reachability (DRAFT)

| Window | Required/y | Effective (~75% independence) | Total | Status |
|---|---|---|---|---|
| IS (5.0y) | ≥ 20.0 | 45-79/y | 225-395 | CLEARS STRONG (11-20x) |
| OOS (2.0y) | ≥ 50.0 | 45-79/y | 90-158 | **CLEARS (1.8-3.2x)** — IMPROVED vs all-tech BORDERLINE |

K9 OOS risk **LOW-MODERATE** (improved vs all-tech MODERATE) due to cross-sector lower correlation → higher effective signal independence. REC1-equivalent binding.

## §5. DR10-v2-reachability (DRAFT): CLEARS WITH STRONG MARGIN
Turnover ~30-60 (non-binding under AND); S2 cost_drag ~0.3-0.6% << 5%; AND-conjunction not triggered.

## §6. Diversification metrics (LOAD-BEARING at SEAL — the central improvement)

| Metric | All-tech | Cross-sector (this candidate) |
|---|---|---|
| A7 effective_independent_bets | 1.5-2.0 (concern) | **2.3-2.8 (improved)** |
| K10 avg_pairwise_correlation | 0.70-0.85 | **0.30-0.50 (improved)** |
| A6 concentration_index | NVDA-dominance risk | balanced |

## §7. Hard boundaries held this DRAFT turn

DRAFT only · no Tier-N SEAL · no BUILD · no fetch/refetch · no backtest/simulator/OOS · no live/Strategy Lab · no candidate promotion · no s13-d1/s12-d1/parked revival · **no modification of any existing sealed artifact** (cross-sector DR9 result + fetched CSVs/manifest + all-tech DRAFT `214bae0` + cross-sector PLAN `c61860d` + s14-d1-multi-instrument chain + s13-d1/s12-d1 chains + framework DR10 v2 `78cd22e` all byte-stable) · no phase-2-safety-contract / CLAUDE.md / .gitignore modification · **no `lessons.md` modification or staging** · no review_queue/idea_memory mutation · no profitability claim · DR10 v2 by-reference (not redefined) · DR9 gate PASS carried (not re-run) · no RSI-threshold modification from PLAN · no universe widening · **no commit by this turn**.

## §8. Status

trading `PAUSED` · live `BLOCKED_AT_6_GATES` · FRC `NEVER_GRANTED` · DIAGNOSTIC_ONLY_NOT_LIVE_GRADE · s13-d1 + s12-d1 terminal · framework DR10 v2 binding. **s14-d1-cross-sector lifecycle: `S14_D1_CROSS_SECTOR_CASH_EQUITY_TIER_N_SPEC_DRAFT_SEALED`.**

## §9. Next-phase authorization scope

- **Commit this DRAFT:** `Authorize commit s14-d1-cross-sector cash-equity Tier-N spec DRAFT artifacts only.`
- **Primary forward (SEAL):** `Authorize s14-d1-cross-sector cash-equity Tier-N spec SEAL only — bound by DR10 v2.`
- **Advance all-tech sibling instead:** `Authorize s14-d1-cash-equity Tier-N spec SEAL only — bound by DR10 v2.`
- **Defer:** `Defer / Pause s14-d1-cross-sector cash-equity at DRAFT.`

End of cross-sector Tier-N spec DRAFT. Sealed DRAFT (NOT a Tier-N SEAL). DA1-DA20 expanded; split_only confirmed; cross-sector DR9 gate PASSED + carried; A7/K10 improvement is the central thesis. Next phase = Tier-N spec SEAL (separate authorization). Not committed this turn.

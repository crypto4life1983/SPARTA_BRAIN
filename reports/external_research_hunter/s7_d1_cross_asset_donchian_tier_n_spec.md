# s7 D1 — Cross-Asset Donchian (NQ + GC + ZN + CL) — Tier-N Spec (SEALED)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_tier_n_spec.v1`
**Schema status:** `SEALED`
**Candidate record id:** `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl`
**Sealed at (UTC):** `2026-05-25T14:58:01Z`
**Predecessor seal sha256:** `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
**Spec MD path:** `docs/s7_d1_cross_asset_donchian_spec.md`
**Spec MD sha256:** `c36588e77899f2511a429b967c0d2fab7bbf85828afae8af7cb4043f96764d4f`
**Seal plan MD path:** `docs/s7_d1_spec_seal_plan.md`
**Seal plan MD sha256:** `40a2ef6a0811fe02f1e00cde62bea5133818ab2d6f6a1908eb9775321126420b`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`
**FRC granted:** `False`
**Advisory label permanent:** `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

> Spec only. No code. No backtest. No Databento call. No QuantConnect call.
> No data fetch. No live trading. No paper bot change. No scheduler change.
> No obsidian-trade-logger mutation. No review_queue mutation. D5 not revived.
> B005_001 not revived. NKE not revived. NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT holds.

## Parent attestation summary
- `drift_count_at_start`: **0**
- `drift_count_at_end`: **0**
- `vt1_vt2_row_by_row_match`: **True**

| Parent | Mode | Recorded sha (head) | Observed sha (head) | Match |
|---|---|---|---|---|
| `s7_selection_plan_seal` | `recompute` | `8d8851bc365ef9a6…` | `8d8851bc365ef9a6…` | ✅ |
| `s6_parking_report` | `recompute` | `f6953c1fb3c334d3…` | `f6953c1fb3c334d3…` | ✅ |
| `s6_decision_memo` | `recompute` | `c2489d468a026a94…` | `c2489d468a026a94…` | ✅ |
| `s6_phase2_plan` | `recompute` | `e9db90cc124058ee…` | `e9db90cc124058ee…` | ✅ |
| `s6_plan_lock` | `recompute` | `e384e37990ac1c1b…` | `e384e37990ac1c1b…` | ✅ |
| `s6_rev1_tier_n` | `recompute` | `f3c727f627a5ff2c…` | `f3c727f627a5ff2c…` | ✅ |
| `s6_original_tier_n` | `recompute` | `17c89eb4c379f68f…` | `17c89eb4c379f68f…` | ✅ |
| `s6_t1_t15_smoke_pass_report` | `recompute` | `96c500a886bb5b8a…` | `96c500a886bb5b8a…` | ✅ |
| `s6_portfolio_cap_bugfix` | `recompute` | `fa232ca1267fe1d8…` | `fa232ca1267fe1d8…` | ✅ |
| `s6_patched_in_sample_diag` | `recompute` | `47f8173e3619577d…` | `47f8173e3619577d…` | ✅ |
| `s5_parking_report` | `recompute` | `6c308b42da6854d5…` | `6c308b42da6854d5…` | ✅ |
| `s5_decision_memo` | `recompute` | `9ee7981f26340f8f…` | `9ee7981f26340f8f…` | ✅ |
| `s4_parking_report` | `recompute` | `8cda3ca644524cd5…` | `8cda3ca644524cd5…` | ✅ |
| `s3_parking_report` | `recompute` | `1f557888e1212d6f…` | `1f557888e1212d6f…` | ✅ |
| `phase2_safety_template_md` | `byte` | `1812f4854a23e7a1…` | `1812f4854a23e7a1…` | ✅ |
| `phase2_safety_template_json` | `byte` | `695a9fb6e0cb6ae5…` | `695a9fb6e0cb6ae5…` | ✅ |

## Markets
| Symbol | Family | Exchange | tick | $/pt |
|---|---|---|---|---|
| `NQ` | equity_index | CME Globex | 0.25 | 20 |
| `GC` | metals | COMEX | 0.1 | 100 |
| `ZN` | bonds_10y | CBOT | 0.015625 | 1000 |
| `CL` | energy_crude | NYMEX | 0.01 | 1000 |

## Strategy parameters (s6 REV1 byte-equivalent)
- Entry channel: **55** bars
- Exit channel: **20** bars
- Filter: `None` (invariant `AMB6_LOCKED_NONE`)
- Entry timing: `ONO_open_on_next_bar`
- Stop: `2.0N` (Wilder ATR(20) at entry)
- Pyramid spacing: `0.5N`
- Max units per market: **4**
- Sizing: **1.0%** portfolio per unit
- Portfolio cap max units: **16**
- Cap uses **unit** count (s6 bugfix inherited): `True`

## Cost-stress matrix tiers
| Tier | slip × | cost × | purpose |
|---|---|---|---|
| S0 | 0.0 | 0.0 | diagnostic_floor_DR3_trigger |
| S1 | 1.0 | 1.0 | baseline_preregistered |
| S2 | 3.0 | 1.5 | mild_stress |
| S3 | 5.0 | 2.0 | realistic_adverse |
| S4 | 8.0 | 3.0 | tail_stress_informational_only |

## Acceptance gates A1-A10
- `A1` (sample_size): closed_trades_portfolio >= 100
- `A2` (sharpe_proxy_positive): sharpe_proxy_per_trade > 0
- `A3` (expectancy_positive): expectancy_per_trade_mnq_equivalent > 0
- `A4` (maxdd_acceptable): trade_curve_maxdd_pct <= 50.0
- `A5` (wr_breakeven_gap): >=2 of 4 markets have wr_gap_to_breakeven >= 0 AND portfolio wr_gap >= +0.5 pp
- `A6` (validator_pass): validator 16/16 (s6) + s7-specific corr_attestation_present
- `A7` (effective_independent_bets): effective_independent_bets >= 2.5 from empirical pairwise correlations
- `A8` (cost_stress_survival): not REJECT_FAST via DR2/DR3/DR5
- `A9` (safety_template_C1_C8): all 8 Phase 2 safety contracts attestable True
- `A10` (cap_binding_events_zero): cap_binding_events_count == 0 at portfolio level

## Rejection gates K1..K12
- `K1` (sharpe_negative): `portfolio_sharpe_proxy_per_trade < 0` → `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- `K2` (expectancy_nonpositive): `expectancy_per_trade <= 0` → `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- `K4` (maxdd_excessive): `trade_curve_maxdd_pct > 50` → `PARKED_SAFE_BUT_NOT_MONEY_PROVEN`
- `K6` (safety_warnings_nonzero): `safety_warning_count > 0` → `PARKED_SAFETY_FAILED`
- `K7` (filter_or_corr_gate_intro): `silently_introduced_filter_or_correlation_gate` → `PARKED_SAFETY_FAILED`
- `K8` (sealed_parent_drift): `sealed_parent_drift > 0` → `PARKED_PROVENANCE_BROKEN`
- `K9` (insufficient_sample): `closed_trades_portfolio < 100` → `PARKED_FAILED_AT_INSUFFICIENT_SAMPLE`
- `K10` (diversification_falsified): `avg_pairwise_correlation > 0.50` → `PARKED_FAILED_AT_DIVERSIFICATION_HYPOTHESIS`
- `K11` (cap_binding_excessive): `cap_binding_events_count > 1000` → `PARKED_CAP_BINDING`
- `K12` (reject_fast): `DR2 or DR3 or DR5 fires on cost-stress matrix` → `REJECT_FAST`

## Output paths to be authored on SEAL_PASS
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_tier_n_spec.json`
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_tier_n_spec.md`
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_validator_run.json`
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_validator_run.md`
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_parent_sha_attestation.json`

## Negative invariants (all True at seal time)
- `no_code_authored_this_turn`: `True`
- `no_backtest_run_this_turn`: `True`
- `no_databento_call_this_turn`: `True`
- `no_qc_call_this_turn`: `True`
- `no_data_fetch_this_turn`: `True`
- `no_live_trading_this_turn`: `True`
- `no_paper_bot_change_this_turn`: `True`
- `no_scheduler_change_this_turn`: `True`
- `no_obsidian_trade_logger_mutation`: `True`
- `no_review_queue_mutation`: `True`
- `no_d5_revived`: `True`
- `no_b005_001_revived`: `True`
- `no_nke_revived`: `True`
- `no_strategy_lab_promotion`: `True`
- `no_filter_or_corr_gate_added`: `True`

## Next step
- `operator_authorization_required_for_plan_lock_authoring_P1`
- Invariant: `NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT_HOLDS`

## Seal block (canonical)
- **`report_seal_sha256`**: `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_tier_n_spec.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T14:58:01Z`

*End of Tier-N spec. Spec-only sealed artifact; no code, no backtest, no fetch, no network, no live or paper trading.*

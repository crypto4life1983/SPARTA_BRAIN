# s8-D1 No-Pyramid - P11 Lifecycle Decision (FINAL PARK, SEALED, PLAN-ONLY)

**Phase:** `P11_LIFECYCLE_DECISION_FINAL_PARK_SEALED`
**FINAL operational status:** `PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED`
**Report date UTC:** 2026-05-26T16:03:18Z

**P11 lifecycle decision seal:** `c79b06206c51d9b94f8d6ee2a9b78ba2d71a16eadbba18aa551319c61213849b`
**Predecessor (P10 OOS decision memo) seal:** `a493931f0b812fad837b9e7679710d03e445ea39d3b53cc8a3ec4ecd7309f9b3`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S8_D1_P11_LIFECYCLE_DECISION_SEALED,
> FINAL_PARK_STATE_PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED, NO_S7_D1_REVIVAL,
> NO_REVIVAL_NO_RE_RUN_UNDER_SAME_CANDIDATE_RECORD_ID
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted
> No profitability claim. No live promotion. Live trading approval: none. Paper trading approval: none.

---

## FINAL LIFECYCLE STATE TRANSITION

- **From state:** `OOS_DECISION_MEMO_SEALED_AWAITING_P11_LIFECYCLE_DECISION`
- **To state:**   **`PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED`** ← **FINAL PARK STATE**
- **Authority:** operator_authorization_AUTHORIZE_S8_D1_P11_lifecycle_decision_PLAN_ONLY

**Basis:** Per the P10 OOS decision memo primary recommendation PARK_OOS_SIZING_UNDERSIZED_NOT_SIGNAL_FAILURE. Signal intact at OOS (164/111/82/92 raw Donchian-55 trigger candidates). OOS data clean (P9.5a). OOS K10 PASS (0.052). OOS zero-trade outcome for NQ/GC/CL caused by capital-vs-contract-size sizing mismatch (P9.5b 100%/100%/100% would_skip). ZN alone cleared (98.9% would_open; 15 actual trades). Strategy locked at $100k starting equity + 1% risk is structurally undersized for 3 of 4 markets in 2023-2025 vol regime; this is a structural parameter park, not a signal-failure park, not money-proven.

**Final state definition:**

> PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED: Candidate has cleared all preregistered in-sample gates (K1-K12, A1-A10, C1-C8) and passed all OOS structural integrity checks (data, diversification) but cannot trade the locked universe under the locked sizing rule in the OOS regime due to capital-vs-N-vs-contract-size mismatch. NOT a signal failure. NOT money-proven. NOT live-ready. FRC never granted. Live promotion path closed.

**Permanent attributes preserved:**

- `trading_status_PAUSED`
- `live_status_BLOCKED_AT_6_GATES`
- `frc_never_granted`
- `live_promotion_path_closed`
- `no_profitability_claim`
- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE_label_permanent`
- `no_live_trading_approval`
- `no_paper_trading_approval`

---

## RECORDED STATUS

- **Root cause:** capital-vs-contract-size sizing mismatch (P9.5b SIZING_SKIP_CONFIRMED)
- **Signal status:** intact (P9.5a triggers exist; not signal failure)
- **Data status:** clean (P9.5a all 4 markets decode; full OOS window covered)
- **Diversification status:** OOS K10 PASS at 0.052 (no regime shift vs IS 0.065)
- **Locked S8-D1 status:** not money-proven, not live-ready
- **In-sample gate pass record:** all preregistered K-gates (K1, K2, K4, K6, K7, K8, K9, K10, K11, K12), all A-gates (A1-A10), and all C-contracts (C1-C8) PASSED in-sample at $100k starting equity 2013-2022; A8 cost-stress S0-S4 PASS; K12 not fired

---

## NON-REVIVAL ATTESTATIONS

- **S8-D1 cannot be revived under same candidate_record_id:** True
- S8-D1 strategy logic locked at max_units_per_market=1 permanently: True
- S8-D1 namespace locked: `s8_d1_cross_asset_donchian_no_pyramid_*`
- Any parameter change requires fresh candidate_record_id: True

**Parameter changes that require a FRESH candidate_record_id (NOT allowed under s8-D1):**
- starting_cash_mnq_equivalent: any value other than 100000
- risk_pct_per_unit: any value other than 0.01
- contract type pivot to micro futures (MNQ/MGC/M2K/MCL): not allowed under s8-D1
- universe substitution: any change to NQ/GC/ZN/CL set
- Donchian channel lengths: any change to 55/20
- ATR period: any change to 20
- stop multiplier: any change to 2N
- filter introduction: any change from AMB6=NONE
- max_units_per_market: any value other than 1

- **Successor candidate authorized by P11:** False
- **P11 creates any successor files:** True (i.e. P11 does NOT)
- Operator decision required before any successor authoring: True

**Non-revival of other parked / rejected candidates:**
- `non_revival_of_s7_d1`: True
- `non_revival_of_d5_neither_s7_ym_only_nor_s8_zn_only`: True
- `non_revival_of_b005_001`: True
- `non_revival_of_nke_options_wheel`: True
- `non_revival_of_s2_kraken_xrp`: True
- `non_revival_of_s3_mnq_drb`: True
- `non_revival_of_s4_turtle_system_1`: True
- `non_revival_of_s5_baseline`: True
- `non_revival_of_s6_full_system`: True

---

## LIFECYCLE ARTIFACT INDEX (20 entries; Tier-N through P11)

| Step | Label | Seal | Commit hash (JSON) |
|---|---|---|---|
| `selection` | S8 selection plan (after six parks) | `6b7bdb4c350f4a77...` | `29ad2d9` |
| `tier_n_spec_draft_md` | Tier-N spec draft (human-readable) | `ada2c060a63a9f3b...` | `(uncommitted or operator-managed)` |
| `tier_n_spec` | Tier-N spec (sealed) | `8cff6babf8e4a451...` | `e7af786` |
| `P1_plan_lock` | P1 plan-lock | `612abbbda7235c8c...` | `63b3234` |
| `P2_phase2_plan` | P2 Phase-2 plan | `5e6fccd1aeb40db7...` | `8cfd0ba` |
| `P3_runner_build` | P3 runner BUILD report | `e1f2a13cb860a629...` | `c8e1fd3` |
| `P3_driver_build` | P3 in-sample driver BUILD report | `d7b82d7adad62979...` | `c8e1fd3` |
| `P4_smoke` | P4 T1-T15+T7b smoke pass | `1ab57a67f1a81be5...` | `942f85f` |
| `P6_in_sample_diagnostic` | P6 in-sample S1 diagnostic | `07a3fa91509f2206...` | `924f84a` |
| `P6_5_cost_stress` | P6.5 cost-stress matrix S0/S1/S2/S3/S4 | `edae2e56cf16c925...` | `784e7bb` |
| `P7_in_sample_decision_memo` | P7 in-sample decision memo | `e26d00587d39404d...` | `5e1b29c` |
| `P7_5_K10_in_sample` | P7.5 K10 correlation in-sample | `221e759e09cc70b2...` | `0c13eab` |
| `P8_lifecycle_oos_plan` | P8 lifecycle transition + OOS deliberation plan | `49b1e6a726183484...` | `1ad00c0` |
| `P8_5_operator_oos_fetch` | P8.5 operator-managed OOS Databento fetch (operator-owned; not authored by SPARTA) | `(operator-managed)` | `(uncommitted or operator-managed)` |
| `P9_oos_s1_diagnostic` | P9 OOS-S1 baseline diagnostic | `dedd8003381a8b9a...` | `3dd41e8` |
| `P9_5a_oos_data_integrity` | P9.5a OOS data integrity audit | `9d65511f83553de0...` | `de25468` |
| `K10_oos` | K10 OOS correlation (side product of P9.5a) | `ccb3609b42f92e61...` | `de25468` |
| `P9_5b_sizing_skip_audit` | P9.5b sizing-skip cascade audit | `957ede055785faf0...` | `d85ef9c` |
| `P10_oos_decision_memo` | P10 OOS decision memo | `a493931f0b812fad...` | `1315f2b` |
| `P11_lifecycle_decision` | P11 lifecycle decision (THIS artifact) | `(TO_BE_COMPUTED_BELOW)` | `(uncommitted or operator-managed)` |

Note: P11 lifecycle index entry's seal field shows `(TO_BE_COMPUTED_BELOW)` in the JSON because
the chain-index P11 entry is recorded BEFORE the P11 seal is computed. The actual P11 seal is
**`c79b06206c51d9b94f8d6ee2a9b78ba2d71a16eadbba18aa551319c61213849b`** (recorded at the top of this MD and in `report_seal_sha256` of the JSON twin).

---

## KEY EVIDENCE SNAPSHOT (for quick lookup)

### In-sample S1 (2013-2022)

- `verdict`: READY_FOR_LONGER_BACKTEST
- `K_fires`: []
- `closed_trades`: 111
- `net_pnl_usd`: 193483
- `sharpe_proxy_per_trade`: 0.225
- `expectancy_per_trade_usd`: 1743
- `trade_curve_maxdd_pct`: -23.83
- `win_rate_pct`: 39.64
- `win_rate_gap_to_breakeven_pp`: 16.5
- `all_4_markets_profitable`: True
- `no_pyramid_invariant_pass`: True

### In-sample cost-stress matrix (P6.5)

- `A8_pass`: True
- `K12_fires`: False
- `DR2_DR3_DR5_not_fired`: True
- `all_5_tiers_no_pyramid_invariant_pass`: True
- `S4_K9_by_1_trade_informational_only`: True

### In-sample K10 (P7.5)

- `avg_pairwise_correlation`: 0.06503
- `K10_fires`: False

### OOS S1 baseline (P9)

- `verdict`: INSUFFICIENT_SAMPLE
- `K_fires`: ['K9']
- `closed_trades`: 15
- `per_market_trades`: {'NQ': 0, 'GC': 0, 'ZN': 15, 'CL': 0}
- `net_pnl_usd`: 1443
- `sharpe_proxy_per_trade`: 0.0445
- `expectancy_per_trade_usd`: 96.2
- `trade_curve_maxdd_pct`: -5.1

### OOS data integrity (P9.5a)

- `conclusion`: DATA_OK_TRIGGERS_EXIST_BUT_ENTRY_LOGIC_BLOCKED
- `trigger_candidates_per_market`: {'NQ': 164, 'GC': 111, 'ZN': 92, 'CL': 82}
- `daily_bar_count_per_market`: {'NQ': 760, 'GC': 680, 'ZN': 773, 'CL': 773}

### OOS K10 (side product of P9.5a)

- `avg_pairwise_correlation`: 0.05159
- `K10_fires`: False
- `delta_vs_in_sample`: -0.01344

### OOS sizing-skip cascade (P9.5b) — root cause confirmed

- `conclusion`: SIZING_SKIP_CONFIRMED
- `would_skip_pct_per_market`: {'NQ': 100.0, 'GC': 100.0, 'ZN': 1.087, 'CL': 100.0}
- `median_N_per_market`: {'NQ': 238.04, 'GC': 24.07, 'ZN': 0.4832, 'CL': 1.6498}
- `median_contract_count_per_market`: {'NQ': 0, 'GC': 0, 'ZN': 2, 'CL': 0}

---

## WHAT P11 DOES NOT AUTHORIZE

- any new backtest run
- any audit re-run
- any OOS metric recomputation
- any code patch or driver modification
- any data fetch
- any Databento API call
- any QC API call
- any network call
- any parameter change to s8-D1
- any fresh successor candidate authoring
- any live trading change
- any paper trading change
- any scheduler change
- any review_queue.json mutation
- any obsidian-trade-logger touch
- any Strategy Lab promotion
- any FRC grant
- any s8-D1 candidate revival or re-run under same candidate_record_id

### What P11 does authorize next

> Operator may, as a SEPARATE explicit decision, authorize a fresh successor candidate (e.g. s10-cross-asset-donchian-no-pyramid-reparam-*) with re-parameterized starting_cash, risk_pct, contract type (micro futures), or universe; OR may pivot the research track to a different family entirely (e.g. trend-following with explicit volatility-targeted sizing, mean-reversion, etc.). P11 itself authorizes NONE of these.

---

## SUCCESSOR CANDIDATE FRAMING (carried forward from P10; NOT COMMITTED)

- Purpose in P11: Re-affirm that P11 does not author or commit to any successor candidate. The framing from P10 is preserved as informational context only.
- Successor candidate_record_id pattern: `e.g. s10-cross-asset-donchian-no-pyramid-reparam-<param>-* OR pivot to different family`
- Namespace collision note: Parallel session is at s9-RSI-2 commits (5bd8e62, c5393ab, 1a055bd). Any cross-asset Donchian reparameterization successor must use a non-colliding candidate_record_id (e.g. s10-* or s9-cross-asset-donchian-* explicitly distinct from s9-rsi2).
- No successor files authored in P11: **True**
- Operator decision required before any successor authoring: **True**

---

## Parent chain (17 byte-stable; drift=0)

- `P10_oos_decision_memo`: `a493931f0b812fad...`
- `P9_5b_sizing_skip`: `957ede055785faf0...`
- `P9_5a_data_integrity`: `9d65511f83553de0...`
- `K10_oos`: `ccb3609b42f92e61...`
- `P9_oos_s1`: `dedd8003381a8b9a...`
- `P8_lifecycle`: `49b1e6a726183484...`
- `P7_5_k10_in_sample`: `221e759e09cc70b2...`
- `P7_decision_memo`: `e26d00587d39404d...`
- `P6_5_cost_stress`: `edae2e56cf16c925...`
- `P6_in_sample_diagnostic`: `07a3fa91509f2206...`
- `P4_smoke`: `1ab57a67f1a81be5...`
- `driver_build`: `d7b82d7adad62979...`
- `runner_build`: `e1f2a13cb860a629...`
- `phase2_plan`: `5e6fccd1aeb40db7...`
- `plan_lock`: `612abbbda7235c8c...`
- `tier_n_spec`: `8cff6babf8e4a451...`
- `selection_plan`: `6b7bdb4c350f4a77...`

---

## Negative invariants this turn (all True)

- `no_audit`: True
- `no_b005_001_revival`: True
- `no_backtest`: True
- `no_broker_adapter_instantiated`: True
- `no_code_patch`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_data_fetch`: True
- `no_databento_api_call`: True
- `no_db_historical_instantiated`: True
- `no_driver_modification`: True
- `no_frc_granted`: True
- `no_live_promotion`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_new_run`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_recomputation`: True
- `no_paper_trading_change`: True
- `no_parameter_change_to_s8_d1`: True
- `no_profitability_claim`: True
- `no_qc_api_call`: True
- `no_review_queue_mutation`: True
- `no_s7_d1_file_modification`: True
- `no_s7_d1_revival`: True
- `no_s8_d1_revival_under_same_candidate_record_id`: True
- `no_scheduler_change`: True
- `no_strategy_lab_promotion`: True
- `no_successor_candidate_files_authored`: True
- `no_threshold_loosening`: True

---

## P11 is the terminal sealed record for the s8-D1 candidate lifecycle.

*End of s8-D1 P11 lifecycle decision. FINAL PARK. Sealed at `c79b06206c51d9b94f8d6ee2a9b78ba2d71a16eadbba18aa551319c61213849b`. PLAN-ONLY. No run. No audit. No code patch. No fresh successor candidate authored.*

# s8-D1 No-Pyramid - P7.5 K10 Correlation Result (SEALED)

**Phase:** `P7_5_K10_CORRELATION_COMPLETE_SEALED`
**Operational status:** `K10_PASS_READY_FOR_OOS_AUTHORIZATION_DELIBERATION_AWAITING_P8`
**Report date UTC:** 2026-05-26T01:07:35Z

**K10 result seal:** `221e759e09cc70b22e7a7d8001e30190e2dc1388506c1f330850f447303e3443`
**Predecessor (P7 decision memo) seal:** `e26d00587d39404d8db52717f66e5a2792aea34a59763e36da380ae9205561cb`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S8_D1_P7_5_K10_CORRELATION_SEALED, NO_S7_D1_REVIVAL
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted

---

## K10 EVALUATION

### avg_pairwise_correlation: **0.065030**

### K10 threshold (fires iff > 0.50): **PASS**

### Implied next operational state: **`READY_FOR_OOS_AUTHORIZATION_DELIBERATION`**

---

## Per-pair Pearson correlations (daily log-returns; aligned common dates)

| Pair | n_common_days | first_date | last_date | pearson_r |
|---|---|---|---|---|
| **NQ-GC** | 2253 | 2013-01-03 | 2022-12-30 | **0.007216** |
| **NQ-ZN** | 2523 | 2013-01-03 | 2022-12-30 | **-0.145667** |
| **NQ-CL** | 2522 | 2013-01-03 | 2022-12-30 | **0.182225** |
| **GC-ZN** | 2287 | 2013-01-03 | 2022-12-30 | **0.335988** |
| **GC-CL** | 2287 | 2013-01-03 | 2022-12-30 | **0.113925** |
| **ZN-CL** | 2562 | 2013-01-03 | 2022-12-30 | **-0.103509** |

**Average pairwise correlation:** **0.065030**

---

## Effective independent bets (informational; A7 threshold = 2.5)

- Formula: `N / (1 + (N-1) * avg_pairwise_correlation)`
- N markets: 4
- avg_pairwise_correlation: 0.065030
- **effective_independent_bets:** **3.3470**
- A7 threshold: 2.5
- A7 pass: **True**

---

## Data + computation metadata

- In-sample window: 2013-01-01 -> 2022-12-30 UTC
- Data source: local Databento cache only (480 files, 129,790,451 bytes)
- Decode: `db.DBNStore.from_file` via `in_sample_driver.derive_rth_daily_bars`
- `run_in_sample` NOT invoked this turn: True
- Bar derivation duration: 243.2s
- Daily bars per market: {'NQ': 2526, 'GC': 2290, 'ZN': 2571, 'CL': 2567}
- Log returns per market: {'NQ': 2525, 'GC': 2289, 'ZN': 2570, 'CL': 2564}

---

## Driver byte-stability

- driver_byte_sha at compute START: `129411e90fba23ff...`
- driver_byte_sha at compute END:   `129411e90fba23ff...`
- byte stable through compute: **True**

---

## s7-D1 non-revival attestation

- `s7_d1_chain_status`: PERMANENTLY_PARKED_AT_COMMIT_f08220a
- `s7_d1_revived_by_this_compute`: False
- `s7_d1_used_as`: NOT_USED_THIS_TURN_K10_USES_ONLY_S8_D1_DRIVER_HELPER
- `s7_d1_file_shas_byte_stable_through_compute`: True
- `s8_d1_source_files_byte_stable_through_compute`: True

---

## Parent chain (byte-stable at K10 compute time)

- `P7_decision_memo`: `e26d00587d39404d...`
- `P6_5_cost_stress_matrix`: `edae2e56cf16c925...`
- `P6_in_sample_diagnostic`: `07a3fa91509f2206...`
- `phase2_plan`: `5e6fccd1aeb40db7...`
- `plan_lock`: `612abbbda7235c8c...`
- `tier_n_spec`: `8cff6babf8e4a451...`
- `selection_plan`: `6b7bdb4c350f4a77...`

---

## Negative invariants this turn (all True)

- `compute_k10_only`: True
- `no_b005_001_revival`: True
- `no_broker_adapter_instantiated`: True
- `no_code_patch`: True
- `no_cost_stress_rerun`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_data_fetch`: True
- `no_databento_api_call`: True
- `no_db_Historical_instantiated`: True
- `no_driver_modification`: True
- `no_frc_granted`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_new_backtest`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_inspection`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_qc_api_call`: True
- `no_review_queue_mutation`: True
- `no_run_in_sample_invoked`: True
- `no_s7_d1_file_modification`: True
- `no_s7_d1_revival`: True
- `no_scheduler_change`: True

---

## Next step (K10 PASS)

> **AUTHORIZE S8-D1 P8 lifecycle transition + OOS deliberation plan (PLAN-ONLY)** -- K10 passes; the candidate's in-sample evidence chain is now complete (P3 BUILD -> P4 smoke -> P6 baseline -> P6.5 cost-stress -> P7 decision memo -> P7.5 K10). P8 would formalize transition to READY_FOR_OOS_AUTHORIZATION_DELIBERATION and outline the OOS deliberation plan WITHOUT actually inspecting OOS.

---

*End of s8-D1 P7.5 K10 correlation result. Sealed at `221e759e09cc70b22e7a7d8001e30190e2dc1388506c1f330850f447303e3443`. No backtest. No OOS. No code patch.*

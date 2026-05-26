# s8-D1 No-Pyramid - P9.5a OOS Data Integrity Audit (SEALED, READ-ONLY)

**Phase:** `P9_5A_OOS_DATA_INTEGRITY_AUDIT_COMPLETE_SEALED`
**Operational status:** `OOS_DATA_AUDIT_COMPLETE_CONCLUSION_DATA_OK_TRIGGERS_EXIST_BUT_ENTRY_LOGIC_BLOCKED_AWAITING_OPERATOR`
**Report date UTC:** 2026-05-26T02:20:40Z

**Audit seal:** `9d65511f83553de01d333814347e514d9ea19d0f6aabac0a2f6af26bd3df1c04`
**Predecessor (P9 OOS-S1) seal:** `dedd8003381a8b9ae01e9432cacefdccda49f658a909b7bb8fcda9f2cda60c4f`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S8_D1_P9_5A_OOS_AUDIT_SEALED, READ_ONLY_AUDIT_NO_BACKTEST, NO_S7_D1_REVIVAL
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted

---

## CONCLUSION: **`DATA_OK_TRIGGERS_EXIST_BUT_ENTRY_LOGIC_BLOCKED`**

Anomalies detected:
- (none)

---

## Per-market audit

| Market | bars | first | last | close min/max/mean | vol mean | NaN | zero-vol | log-ret mean/std | long triggers | short triggers | total triggers | finding |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **NQ** | 760 | 2023-01-03 | 2025-12-30 | 10828.50/26314.75/18705.13 | 431,039 | 0 | 0 | 0.001125 / 0.012612 | 145 | 19 | 164 | DATA_OK_TRIGGERS_EXIST_164_total |
| **GC** | 680 | 2023-01-04 | 2025-12-30 | 1815.50/4535.30/2619.37 | 124 | 0 | 0 | 0.001252 / 0.010926 | 101 | 10 | 111 | DATA_OK_TRIGGERS_EXIST_111_total |
| **ZN** | 773 | 2023-01-03 | 2025-12-30 | 105.50/116.48/111.32 | 666,719 | 0 | 0 | -0.000000 / 0.003901 | 40 | 52 | 92 | DATA_OK_TRIGGERS_EXIST_92_total |
| **CL** | 773 | 2023-01-03 | 2025-12-30 | 55.30/93.68/72.75 | 93,880 | 0 | 0 | -0.000367 / 0.019567 | 46 | 36 | 82 | DATA_OK_TRIGGERS_EXIST_82_total |

P9 OOS-S1 trade counts (for reference): NQ=0, GC=0, ZN=15, CL=0

---

## K10 OOS (side product)

### avg_pairwise_correlation_OOS: **0.051590253717225566**
### K10 OOS fires (avg > 0.50): **False**

| pair | n_common_days | first | last | pearson_r |
|---|---|---|---|---|
| NQ-GC | 666 | 2023-01-06 | 2025-12-30 | 0.057167 |
| NQ-ZN | 758 | 2023-01-04 | 2025-12-30 | -0.017233 |
| NQ-CL | 759 | 2023-01-04 | 2025-12-30 | 0.107979 |
| GC-ZN | 679 | 2023-01-06 | 2025-12-30 | 0.223576 |
| GC-CL | 679 | 2023-01-06 | 2025-12-30 | 0.137653 |
| ZN-CL | 771 | 2023-01-04 | 2025-12-30 | -0.199600 |

In-sample K10 reference: avg_pairwise_correlation = 0.065030 (PASS)

---

## Runtime monkey-patch attestation

Driver `.py` file byte sha UNCHANGED. Module-level IN_SAMPLE_START/END monkey-patched in-memory only for the OOS bar derivation; restored after audit.

- driver_byte_sha at audit START: `129411e90fba23ff...`
- driver_byte_sha at audit END:   `129411e90fba23ff...`
- byte stable through audit: **True**

---

## Parent chain (13 byte-stable; drift=0)

- `P9_oos_s1`: `dedd8003381a8b9a...`
- `P8_lifecycle`: `49b1e6a726183484...`
- `P7_5_k10`: `221e759e09cc70b2...`
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

- `no_b005_001_revival`: True
- `no_backtest`: True
- `no_broker_adapter_instantiated`: True
- `no_code_patch_committed_to_disk`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_data_fetch`: True
- `no_databento_api_call`: True
- `no_db_Historical_instantiated`: True
- `no_driver_file_modification_on_disk`: True
- `no_frc_granted`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_qc_api_call`: True
- `no_review_queue_mutation`: True
- `no_run_in_sample_invoked`: True
- `no_s7_d1_file_modification`: True
- `no_s7_d1_revival`: True
- `no_scheduler_change`: True
- `no_threshold_loosening`: True
- `read_only_audit`: True

---

*End of s8-D1 P9.5a OOS data integrity audit. Sealed at `9d65511f83553de01d333814347e514d9ea19d0f6aabac0a2f6af26bd3df1c04`. Read-only. No backtest. No code patch.*

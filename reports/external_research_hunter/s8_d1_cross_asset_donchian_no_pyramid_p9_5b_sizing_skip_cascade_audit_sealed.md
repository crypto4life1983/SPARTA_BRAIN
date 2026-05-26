# s8-D1 No-Pyramid - P9.5b Sizing-Skip Cascade Audit (SEALED, READ-ONLY)

**Phase:** `P9_5B_SIZING_SKIP_CASCADE_AUDIT_COMPLETE_SEALED`
**Operational status:** `P9_5B_AUDIT_COMPLETE_CONCLUSION_SIZING_SKIP_CONFIRMED_AWAITING_OPERATOR`
**Report date UTC:** 2026-05-26T02:43:58Z

**Audit seal:** `957ede055785faf041ccdbd13e268793076926e6547e8dad43c4edc1b38020d8`
**Predecessor (P9.5a) seal:** `9d65511f83553de01d333814347e514d9ea19d0f6aabac0a2f6af26bd3df1c04`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, READ_ONLY_AUDIT_NO_BACKTEST, NO_S7_D1_REVIVAL
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted

---

## CONCLUSION: **`SIZING_SKIP_CONFIRMED`**

- Equity assumption: $100,000; risk_pct: 0.01; risk_dollars per trigger: $1,000
- Contract formula: `floor(1000 / (N_entry × dollar_per_point))`
- skip_if_contract_count_lt_one: True

## Per-market sizing-skip cascade breakdown

| Market | $/pt | total triggers | would_open | would_skip | would_open % | would_skip % | N median | contracts median | P9 actual trades |
|---|---|---|---|---|---|---|---|---|---|
| **NQ** | 20 | 164 | 0 | 164 | 0.00% | **100.00%** | 238.0375 | 0.0 | 0 |
| **GC** | 100 | 111 | 0 | 111 | 0.00% | **100.00%** | 24.0650 | 0 | 0 |
| **ZN** | 1000 | 92 | 91 | 1 | 98.91% | **1.09%** | 0.4832 | 2.0 | 15 |
| **CL** | 1000 | 82 | 0 | 82 | 0.00% | **100.00%** | 1.6498 | 0.0 | 0 |

## N_entry (Wilder ATR(20)) distribution per market

| Market | min | median | mean | max |
|---|---|---|---|---|
| NQ | 167.7250 | 238.0375 | 254.5770 | 589.5500 |
| GC | 11.4900 | 24.0650 | 26.9255 | 66.7650 |
| ZN | 0.2695 | 0.4832 | 0.5067 | 1.0586 |
| CL | 1.2190 | 1.6498 | 1.7037 | 2.7235 |

## Contract-count distribution per market

| Market | min | median | mean | max |
|---|---|---|---|---|
| NQ | 0 | 0.0 | 0.0000 | 0 |
| GC | 0 | 0 | 0.0000 | 0 |
| ZN | 0 | 2.0 | 1.5870 | 3 |
| CL | 0 | 0.0 | 0.0000 | 0 |

## Sample triggers (first 3 + last 2 per market)

### NQ (dpp=20)

| bar_date | long? | short? | N_entry | contracts | would_open |
|---|---|---|---|---|---|
| 2023-03-22 | True | False | 248.9250 | 0 | False |
| 2023-03-30 | True | False | 255.0625 | 0 | False |
| 2023-03-31 | True | False | 254.1250 | 0 | False |
| 2025-10-28 | True | False | 376.5875 | 0 | False |
| 2025-10-29 | True | False | 376.0875 | 0 | False |

### GC (dpp=100)

| bar_date | long? | short? | N_entry | contracts | would_open |
|---|---|---|---|---|---|
| 2023-04-05 | True | False | 23.7150 | 0 | False |
| 2023-04-13 | True | False | 23.0100 | 0 | False |
| 2023-05-04 | True | False | 18.9950 | 0 | False |
| 2025-12-23 | True | False | 43.3300 | 0 | False |
| 2025-12-26 | True | False | 43.8900 | 0 | False |

### ZN (dpp=1000)

| bar_date | long? | short? | N_entry | contracts | would_open |
|---|---|---|---|---|---|
| 2023-03-23 | True | False | 0.9734 | 1 | True |
| 2023-03-24 | True | False | 0.9781 | 1 | True |
| 2023-04-05 | True | False | 1.0586 | 0 | False |
| 2025-10-21 | True | False | 0.3359 | 2 | True |
| 2025-12-23 | False | True | 0.2695 | 3 | True |

### CL (dpp=1000)

| bar_date | long? | short? | N_entry | contracts | would_open |
|---|---|---|---|---|---|
| 2023-04-12 | True | False | 2.3365 | 0 | False |
| 2023-06-12 | False | True | 2.0975 | 0 | False |
| 2023-07-13 | True | False | 1.7310 | 0 | False |
| 2025-12-15 | False | True | 1.2190 | 0 | False |
| 2025-12-16 | False | True | 1.2375 | 0 | False |

---

## Parent chain (12 byte-stable; drift=0)

- `P9_5a_audit`: `9d65511f83553de0...`
- `K10_oos`: `ccb3609b42f92e61...`
- `P9_oos_s1`: `dedd8003381a8b9a...`
- `P8_lifecycle`: `49b1e6a726183484...`
- `P7_5_k10`: `221e759e09cc70b2...`
- `P7_decision_memo`: `e26d00587d39404d...`
- `P6_5_cost_stress`: `edae2e56cf16c925...`
- `P6_in_sample_diagnostic`: `07a3fa91509f2206...`
- `driver_build`: `d7b82d7adad62979...`
- `tier_n_spec`: `8cff6babf8e4a451...`
- `plan_lock`: `612abbbda7235c8c...`
- `phase2_plan`: `5e6fccd1aeb40db7...`

## Driver byte-stability

- driver_byte_sha at audit START: `129411e90fba23ff...`
- driver_byte_sha at audit END:   `129411e90fba23ff...`
- byte stable through audit: **True**

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

*End of P9.5b sizing-skip cascade audit. Sealed at `957ede055785faf041ccdbd13e268793076926e6547e8dad43c4edc1b38020d8`. Read-only.*

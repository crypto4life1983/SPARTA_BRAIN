# s8-D1 No-Pyramid - P6.5 Cost-Stress Matrix Result (SEALED)

**Phase:** `P6_5_COST_STRESS_MATRIX_COMPLETE_SEALED`
**Operational status:** `COST_STRESS_PARTIAL_OR_FAILED_AWAITING_P7_OPERATOR_DECISION`
**Report date UTC:** 2026-05-26T00:39:54Z

**Cost-stress matrix seal:** `edae2e56cf16c92555bbf9dfaa2d773f49e3e68ce12141c6d541753f52d17ded`
**Predecessor (P6 in-sample result) seal:** `07a3fa91509f2206ba15ac8a21cd326b7ea85bae8191cbd4747fa1ed50a88f00`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S8_D1_P6_5_COST_STRESS_MATRIX_SEALED, NO_S7_D1_REVIVAL
> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted

---

## Per-tier matrix

| Tier | trades | net_pnl_usd | sharpe | expect/trade | pl_ratio | MaxDD% | K-fires | survive? |
|---|---|---|---|---|---|---|---|---|
| **S0** | 112 | $198,216 | 0.2296 | $1,769.78 | 3.45 | -22.94% | NONE | **True** |
| **S1** | 111 | $193,483 | 0.2250 | $1,743.09 | 3.32 | -23.83% | NONE | **True** |
| **S2** | 108 | $159,557 | 0.2071 | $1,477.38 | 3.19 | -20.76% | NONE | **True** |
| **S3** | 107 | $152,536 | 0.1994 | $1,425.57 | 3.31 | -22.11% | NONE | **True** |
| **S4** | 99 | $99,108 | 0.1571 | $1,001.09 | 2.93 | -23.92% | K9 | **False** |

- Sources: S1 imported from committed P6 result; S0/S2/S3/S4 freshly run (total 1032.5s wall)

## DR rule evaluation

- **DR2-like (in-sample S1->S2 or S1->S3 material degradation):** fires = `False`
  - S1->S2 material degrade: False
  - S1->S3 material degrade: False
- **DR3 (zero-cost-only survival):** fires = `False` (S0 positive AND all of S1/S2/S3/S4 negative)
- **DR4 (IS pos / OOS neg @ S0):** not evaluable this turn (OOS not run)
- **DR5 (S0->S1 edge flips negative):** fires = `False`

### **K12 (REJECT_FAST via DR2/DR3/DR5):** fires = `False`

### **A8 (cost-stress S0-S4 RUN AND DR2/DR3/DR5 not fired):** pass = `True`

## Survival summary

- **S0**: survives = True (K-fires: NONE)
- **S1**: survives = True (K-fires: NONE)
- **S2**: survives = True (K-fires: NONE)
- **S3**: survives = True (K-fires: NONE)
- **S4**: survives = False (K-fires: ['K9'])

### **Strategy survives ALL 5 tiers (S0-S4) under K-gate evaluation:** `False`

## No-pyramid attestation per tier

| Tier | max_units_per_market | max_units_observed_max | invariant_held | violations |
|---|---|---|---|---|
| S0 | 1 | 1 | True | 0 |
| S1 | 1 | 1 | True | 0 |
| S2 | 1 | 1 | True | 0 |
| S3 | 1 | 1 | True | 0 |
| S4 | 1 | 1 | True | 0 |

All tiers no-pyramid invariant pass: **True**

## Parent chain (byte-stable through runs)

- `P6_diagnostic_result`: `07a3fa91509f2206...` (byte_stable=True)
- `smoke_pass_report`: `1ab57a67f1a81be5...` (byte_stable=True)
- `in_sample_driver_build_report`: `d7b82d7adad62979...` (byte_stable=True)
- `runner_build_report`: `e1f2a13cb860a629...` (byte_stable=True)
- `phase2_plan`: `5e6fccd1aeb40db7...` (byte_stable=True)
- `plan_lock`: `612abbbda7235c8c...` (byte_stable=True)
- `tier_n_spec`: `8cff6babf8e4a451...` (byte_stable=True)
- `selection_plan`: `6b7bdb4c350f4a77...` (byte_stable=True)

## s7-D1 non-revival attestation

- s7-D1 file shas byte-stable through P6.5 run: **True**
- s8-D1 source files byte-stable through P6.5 run: **True**

## Negative invariants this turn (all True)

- `no_b005_001_revival`: True
- `no_broker_adapter_instantiated`: True
- `no_code_patching_this_turn`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_data_fetch`: True
- `no_databento_api_call_via_db_Historical`: True
- `no_db_Historical_instantiated`: True
- `no_frc_granted`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_inspection`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_qc_api_call`: True
- `no_qc_cloud_submit`: True
- `no_review_queue_mutation`: True
- `no_s7_d1_file_modification`: True
- `no_s7_d1_revival`: True
- `no_scheduler_change`: True
- `no_threshold_loosening`: True

---

## Next step

> **AUTHORIZE S8-D1 P7 in-sample decision memo (PLAN-ONLY)**

---

*End of s8-D1 P6.5 cost-stress matrix result.*

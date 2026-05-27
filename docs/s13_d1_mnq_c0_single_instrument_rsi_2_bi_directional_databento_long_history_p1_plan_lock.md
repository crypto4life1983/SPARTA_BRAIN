# S13-D1 P1 plan-lock (sealed)

**Candidate record id:** `s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history`
**Phase prefix:** `PHASE2-S13-D1-MNQ-RSI-2-BIDIR`
**Authored (UTC):** `2026-05-27T17:06:41.207309Z`
**Lifecycle state:** P1_PLAN_LOCK_SEALED
**Tier-N spec inherited byte-equivalent:** commit `262491c` (seal `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775`)
**Report seal sha256:** `1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c`
**Seal method:** LESSON_HUNTER_004 canonical roundtrip
**Reseal verified on disk:** YES (UTF-8 explicit)

## Tier-N spec inheritance

This P1 plan-lock document LOCKS the s13-d1 sealed Tier-N spec at commit `262491c` (seal sha `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775`) as the source of truth. Operator authorization phrase verbatim: *"Authorize s13 D1 MNQ.c.0 P1 plan-lock. Anchor to the s13-d1 SEAL at commit 262491c and carry forward DA3=B, DA4=C, the K9-reachability discipline, and the REC1-equivalent OOS K9 disclosure as binding."*

| Carried-binding field | Value | Origin |
|---|---|---|
| DA3 per-trade risk | **0.5%** | DA3=B revised at SEAL for DR3 mitigation |
| DA4 START_CASH | **$200,000** | DA4=C revised at SEAL for DR10 mitigation |
| K9-reachability discipline | applied at IS AND OOS | new framework standard (origin `0e3f9d4`) |
| REC1-equivalent OOS K9 disclosure | binding (priority HIGH) | carried byte-equivalent from SEAL |

All Tier-N spec decisions are inherited byte-equivalent into the BUILD phase. **No Tier-N spec modification permitted; modification requires fresh _revN_ Tier-N spec.**

## 1. Exact implementation files allowed for P3 BUILD

**Total allowed file count: 16**

### Source files (5)
- `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/__init__.py`
- `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/main.py`
- `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/execution_guard.py`
- `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/in_sample_driver.py`
- `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/out_of_sample_driver.py`

### Test scaffold (5)
- `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/tests/__init__.py`
- `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/tests/conftest.py`
- `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/tests/fixtures/synthetic_mnq_daily.csv`
- `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/tests/test_smoke_t1_t15.py`
- `external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness/tests/test_oos_driver_invariants.py`

### Sealed BUILD report files (6)
- `reports/external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_build_report.{json,md}`
- `reports/external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_in_sample_driver_build_report.{json,md}`
- `reports/external_research_hunter/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_out_of_sample_driver_build_report.{json,md}`

## 2. Strategy mechanic boundaries (LOCKED; carried byte-equivalent from SEAL)

| Field | Value | Note |
|---|---|---|
| Mechanic family | F3 RSI(2) bi-directional mean-reversion | LOCKED at PLAN |
| `rsi_period` | 2 (Connors classic; Wilder smoothing) | LOCKED at PLAN |
| `rsi_long_entry_threshold` | **`< 10`** | LOCKED at PLAN |
| `rsi_long_exit_threshold` | **`> 50`** | LOCKED at PLAN |
| `rsi_short_entry_threshold` | **`> 90`** | LOCKED at PLAN |
| `rsi_short_exit_threshold` | **`< 50`** | LOCKED at PLAN |
| `atr_period` | 20 (Wilder) | DA1=A |
| `stop_multiplier_in_atr` | 2.0 | DA2=A |
| **`risk_pct_per_trade`** | **0.005** | **DA3=B REVISED** |
| `max_units_per_market` | 1 | non-negotiable |
| `pyramid_method` | NONE | non-negotiable |
| **`starting_cash_mnq_equivalent`** | **$200,000** | **DA4=C REVISED** |
| `tick_size_points` / `tick_value_usd` / `dollar_per_point` | 0.25 / $0.50 / $2.00 | byte-equivalent |
| `rth_window_et` | `{9:30, 16:00, America/New_York}` | DA12=A |
| `intraday_data_used` | False | -- |
| `roll_method` | Databento continuous front-month | byte-equivalent |

## 3. K9 reachability table at P1 (carried byte-equivalent from SEAL)

| Window | Length (y) | Required trades/y | s13-d1 expected (low/central/high) | K9 status |
|---|---:|---|---|---|
| IS | 4.6 | ≥ 21.74 | 50 / 57 / 65 | **CLEARS (2.3-3.0× margin)** |
| **OOS** | **2.0** | **≥ 50.00** | 50 / 57 / 65 | **CLEARS at lower bound (thin margin)** |

## 4. REC1-equivalent OOS K9 disclosure (carried byte-equivalent; BINDING)

> *"OOS K9 reachable at lower bound with thin margin (~50-65 trades/year vs 50/year floor). If observed IS rate falls below 25/year on RSI(2) bi-directional, OOS K9 unreachability becomes structurally probable. The s9 RSI-2 baseline observed 414 trades over long-only 4-ETF window; if MNQ.c.0 bi-directional rate falls below half that proportional rate, OOS K9 fires. If OOS K9 fires, the OOS verdict shall be OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164 and s12-d1 P11 park at ecbd001. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s13-d1 accepts the structural possibility of an OOS PARK outcome if the IS rate falls below the DRAFT-estimated 50-65/y band."*

`rec1_equivalent_does_not_alter_DA1_through_DA14_resolutions`: True · `rec1_equivalent_does_not_alter_DR9_or_DR10_thresholds`: True · `no_chain_response_relaxes_K9_at_OOS`: True

## 5. Test plan adapted for s13-d1 (17 tests in P4 synthetic smoke + 12 OOS invariants)

s13-d1-specific test adaptations from s12-d1 baseline:
- T4_donchian_15_8 → **T4_rsi_2_synthetic** (RSI(2) computation tests)
- T5_donchian_breakout → **T5_rsi_oversold_overbought_entry_trigger** (RSI<10/>90 entries)
- **T7c_starting_cash_invariant_200000** (DA4=C; was 100k in s12-d1)
- T8_donchian_8_reversal → **T8_exit_on_rsi_50_crossover** (RSI mean-reversion exits)
- **T10_sizing_0_5pct_floor** (DA3=B; 0.5% risk; was 1% in s12-d1)
- T1, T2, T3 (ATR), T6 (2N stop), T7 (pyramid trigger), T7b (pyramid raises), T9, T11, T12 (RTH), T13, T14 (5-tier), T15 unchanged

## 6. Files explicitly forbidden during all S13-D1 phases

(See JSON sidecar `files_explicitly_forbidden_during_all_s13_d1_phases` for full list.) Key:
- **All s12-d1 SEAL/P1/P2/P3/P4/P6/P11 sealed artifacts** (terminal park preserved)
- All s11-d1 v1/P1/P2/clarification/rev2 sealed artifacts
- s10-d2 / s10-d1 / s9 / B005 / B006 / T8 / NKE / s7-d1 / s8-d1 sealed artifacts
- phase_2_safety_contract_template
- The s13-d1 SEAL at `262491c` (modification requires fresh _revN_)
- All parallel-session shorter-path sealed artifacts
- **`brain_memory/projects/trading_bot/lessons.md`** (off-limits in EVERY S13-D1 phase)

## 7. Input data path and sha requirement

- `primary_path`: `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `primary_sha256_required`: `8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e`
- `primary_row_count`: 2066
- `fresh_fetch_required`: False
- `build_phase_must_verify_csv_sha_at_runtime`: True (fail-loud error class `S13_D1_MNQ_CSV_SHA_MISMATCH`)

## 8. Cost tier definitions (LOCKED at SEAL; carried byte-equivalent)

| Tier | cost_scalar | slippage_scalar |
|---|---:|---:|
| `S0` | 0.0 | 0.0 |
| `S1` | 1.0 | 1.0 |
| `S2` | 1.5 | 1.5 |
| `S3` | 2.0 | 2.0 |
| `S4` | 3.0 | 3.0 |

Baseline: commission $0.74 + fees $0.36 + slippage 1/1/1 ticks per round-trip.

## 9. Rejection rules (LOCKED at SEAL; DR3 + DR10 elevated)

- **DR3 zero-cost-only survival** — ELEVATED for s13-d1 RSI lineage; mitigated via DA3=B
- **DR10 turnover-cost-explosion** — ELEVATED (high-frequency); mitigated via DA4=C
- K9 closed_trades < 100 → INSUFFICIENT_SAMPLE (not FAIL_SAFETY)
- All K-gates and A-gates carried byte-equivalent

## 10. Promotion rules

`permanent_live_block` / `permanent_paper_block` / `live_promotion_blocked_at_6_gates_permanently` / `no_verdict_unblocks_*` all True. `promotion_at_any_stage_is_OUT_OF_SCOPE`. `research_diagnostic_only`. `no_profitability_claim`.

## 11. Output artifact plan per phase

| Phase | Files |
|---|---|
| P1 plan-lock (this turn) | `docs/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_p1_plan_lock.md` + `reports/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_p1_plan_lock_sealed.json` |
| P2 phase-2 plan | `docs/s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_p2_phase2_plan.md` + JSON |
| P3 BUILD | see section 1 (16 files) |
| P4 smoke / P6 IS / P6.5 / P7 / P10 / P11 | per output_artifact_plan_per_phase in JSON sidecar |

## 12. Seal / hash protocol (LOCKED)

LESSON_HUNTER_004 canonical roundtrip; `json.dumps sort_keys=True separators=',:' ensure_ascii=False default=str` excluding `report_seal_sha256` + `seal_method`; sha256 over UTF-8.

### Embedded constants for P3 BUILD assert_seal_inheritance

| Constant | Value |
|---|---|
| `PREDECESSOR_PARK_REF_S12_D1` | `ecbd001` (terminal) |
| `PREDECESSOR_PARK_REF_S10_D1` | `1a9acec` |
| `PREDECESSOR_PARK_REF_S10_D2` | `23c7164` |
| `PREDECESSOR_PARK_REF_S9_RSI_2` | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| `TIER_N_SPEC_SEAL_SHA256` | `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775` |
| `PLAN_LOCK_SEAL_SHA256` | `1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c` |
| `REC1_EQUIVALENT_OOS_K9_DISCLOSURE_CARRIED_FROM_SEAL` | True |
| `K9_REACHABILITY_DISCIPLINE_APPLIED_AT_PLAN_DRAFT_SEAL_P1` | True |

## 13. Explicit next-phase requirement

P1 plan-lock authoring + sealing + commit completes here. The NEXT phase is **P2 phase-2 plan**, requiring separate operator authorization: `Authorize s13 D1 MNQ.c.0 P2 phase-2 plan only`.

**NO PHASE BEYOND P2 IS PRE-APPROVED by this P1 plan-lock.**

## Parent references (READ-ONLY)

| Field | Value |
|---|---|
| Tier-N SEAL | commit `262491c` / sha `2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775` |
| s13-d1 PLAN | commit `5e57984` |
| s13-d1 DRAFT | commit `8fcefaf` |
| Selection-plan revision | commit `0e3f9d4` |
| s12-d1 P11 park (TERMINAL) | commit `ecbd001` |
| s12-d1 SEAL | commit `66bbbd1` |
| s10-d2 park | commit `23c7164` |
| s10-d1 MNQ+MGC park | commit `1a9acec` |
| s9 RSI-2 ETF-proxy | PARKED_SAFE_BUT_NOT_MONEY_PROVEN |
| MNQ.c.0 CSV path | data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv |
| MNQ.c.0 CSV sha256 | 8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e |

## Status

| Field | Value |
|---|---|
| trading_status | PAUSED |
| live_status | BLOCKED_AT_6_GATES |
| frc_status | NEVER_GRANTED |
| research_label | DIAGNOSTIC_ONLY_NOT_LIVE_GRADE |
| lifecycle_state | P1_PLAN_LOCK_SEALED |
| K9_THRESHOLD_INVIOLATE | True |
| REC1_EQUIVALENT_OOS_K9_DISCLOSURE_BINDING | True |
| DA3=B + DA4=C carried binding | True |

## Seal metadata

- **Report seal sha256:** `1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c`
- **Seal method:** LESSON_HUNTER_004 canonical roundtrip
- **Reseal verified on disk:** YES (UTF-8 explicit)

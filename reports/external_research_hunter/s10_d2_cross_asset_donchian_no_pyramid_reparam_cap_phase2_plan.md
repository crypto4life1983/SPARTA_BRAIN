# S10-D2 Reparam-Cap Cross-Asset Donchian No-Pyramid - P2 Phase-2 Plan (SEALED)

**Artifact type:** `phase2_plan`
**Schema id:** `sparta.external_research_hunter.s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_phase2_plan.v1`
**Schema status:** `SEALED`
**Canonical record id:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Candidate operational status:** `PHASE2_PLAN_SEALED`
**Phase:** `P2_PHASE2_PLAN_SEALED_BUILD_NOT_AUTHORIZED`
**Report date UTC:** 2026-05-27T00:18:50Z

**Phase-2 plan seal sha256:** `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`
**Seal method:** `LESSON_HUNTER_004` canonical roundtrip

**Predecessor seal (P1 plan-lock):** `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
**Tier-N spec seal:** `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
**S10 selection plan seal:** `007110ff5a57dd04b184409bad64fd667374cd049155416c869a73f7af0c1f97`
**S10 availability analysis seal:** `417ed6c7b4e177e0681a3fe20a03744cb22c9946b9755e077a3def3afd7f50e7`
**S8-D1 P11 (terminal park) seal:** `c79b06206c51d9b94f8d6ee2a9b78ba2d71a16eadbba18aa551319c61213849b`

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S10_D2_P2_PHASE2_PLAN_SEALED,
> SINGLE_DELTA_FROM_S8_D1_STARTING_CASH_500K, NO_S8_D1_REVIVAL, NO_S7_D1_REVIVAL

> Trading: PAUSED | Live: BLOCKED_AT_6_GATES | FRC: not granted | No profitability claim

---

## Phase-2 safety template inheritance

Inherits Phase 2 safety contracts (C1-C8) byte-equivalent from:

- `docs/phase2_safety_contract_template.md` -- sha `1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981`
- `docs/phase2_safety_contract_template.json` -- sha `695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32`

Adapts each C-contract to s10-D2 specifics. Does NOT revive any parked or rejected candidate.

---

## C1-C8 required evidence summary (one-line)

- **C1** LiveMode raise in Initialize; status_fields strings PAUSED / BLOCKED_AT_6_GATES; no broker adapter; exception text 'LIVE_PATH_DETECTED: s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl is paper-only forever'
- **C2** engine-truth run_id; Initialize date cross-check; window ceiling; algo_version=s10_d2_v0_1_0; phase_prefix=PHASE2-S10-D2-XAD-RC; predecessor_seal=plan_lock_seal
- **C3** all universal + futures-specific counters; pyramid_state_machine_violation_count must be 0 (vestigial under max_units=1); per_market_unit_count_invariant_violation_count must be 0
- **C4** per-market RTH windows; eod_cancel == rth_close; LIMIT discipline; quote_age + spread checks
- **C5** known_contract_rolls + known_expirations from CME calendar; expiry blackout 5d before
- **C6** schema_id = sparta.external_research_hunter.s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_in_sample_diagnostic.v1; cagr from engine; win_rate literal when n<100; starting_cash=$500,000 baked into performance_summary fields; per-market unit-count audit (must always be 0 or 1 under max_units=1)
- **C7** closed enum {FAIL_SAFETY, INSUFFICIENT_SAMPLE, READY_FOR_LONGER_BACKTEST}; min_closed_trades=100; K-gates run in parallel; no enum extension
- **C8** park-on-weak-performance rule; revival requires fresh s11-* candidate_record_id; live-block permanent; no s10-D2 re-run under same candidate_record_id with different parameters

---

## Single delta from S8-D1 explicit record

| Field | S8-D1 | S10-D2 |
|---|---|---|
| `starting_cash_mnq_equivalent` | $100,000 | **$500,000** |
| All other locked parameters | (s8-D1 Tier-N) | byte-equivalent |
| Delta count | — | **1** |

**Rationale:** $500,000 is round number above empirical $476k NQ-clearing threshold from s8-D1 P9.5b sizing-skip cascade audit (median N=238.04 at OOS)

**Invariant:** S-STOP-14 fires if starting_cash != 500000 detected anywhere in CONFIG, runner constants, or runtime state.

---

## No-pyramid mechanics (preserved from s8-D1)

| Field | Value |
|---|---|
| `max_units_per_market` | **1** |
| Pyramid spacing (vestigial) | 0.5N (never fires under max_units=1) |
| Expected open-unit count per market | {0, 1} |
| Portfolio cap (max units total) | 4 |
| Portfolio cap structurally non-binding | **True** (4 markets x 1 unit = 4) |
| Portfolio cap uses unit count not contract count (s6 bugfix) | **True** |
| N source | Wilder ATR(20) of entry market at trigger bar |

---

## AMB6 filter confirmation

- `amb6_filter_setting`: **NONE**
- structurally_locked_none: True
- same_direction_filter / ma_filter / regime_filter / correlation_gate: all False
- Any new filter introduction at or after BUILD time triggers **K7**

---

## Data source confirmation

- Data source at runtime: **DATABENTO_GLBX_MDP3_LOCAL_CACHE_ONLY**
- No fresh Databento fetch authorized: **True**
- S8-D1 existing cache re-used: **True**
- IS cache: 480 files / 129,790,451 bytes
- OOS cache: 144 files / 42,663,855 bytes
- Combined: 624 files / 172,454,306 bytes
- Local decode path: `db.DBNStore.from_file()`
- P5 fetch needed: **False**
- P8.5 OOS fetch needed: **False**

---

## Window attestation

- In-sample window UTC: **2013-01-01 -> 2022-12-30**
- OOS window UTC: **2023-01-01 -> 2025-12-30** (noted but NOT inspected)
- OOS inspection during in-sample run: **prohibited**
- Window extension beyond plan-lock ceiling: **forbidden**

---

## Future steps gating (all require separate explicit operator authorization)

- `P3_build_only`: True
- `P4_t1_t15_synthetic_smoke`: True
- `no_P5_fetch_needed_existing_s8_d1_cache_re_used`: True
- `P6_in_sample_run_S1_baseline_optional_S0_S2_S3_S4`: True
- `P7_in_sample_decision_memo`: True
- `P7_5_K10_in_sample_correlation_compute`: True
- `P8_lifecycle_transition_OOS_deliberation_plan`: True
- `no_P8_5_OOS_fetch_needed_existing_s8_d1_P8_5_OOS_cache_re_used`: True
- `P9_OOS_S1_run`: True
- `P9_5_OOS_cost_stress_optional`: True
- `P10_OOS_decision_memo`: True
- `P11_lifecycle_decision_final`: True

P2 authorizes nothing downstream.

---

## C7 verdict semantics (preserved closed enum)

Allowed verdicts (closed; no extensions):

- **FAIL_SAFETY** -- safety counter > 0 at run end (top priority)
- **INSUFFICIENT_SAMPLE** -- closed_trades_portfolio < 100
- **READY_FOR_LONGER_BACKTEST** -- research label only; never live-ready; 6-gate live-block applies regardless

C7 enum + Tier-N K-gates K1..K12 run in parallel. Candidate proceeds to OOS authorization ONLY if BOTH (VERDICT == READY_FOR_LONGER_BACKTEST) AND (no K fires) AND (Tier-N acceptance gates A1..A10 all pass).

---

## Fail-closed conditions for future BUILD and run phases

- Any C1 violation: LiveMode bypass / status string change / broker import
- Any C2 violation: CONFIG/engine date divergence / window ceiling / seal recompute mismatch
- Any C3 hard safety counter > 0 at run end (including per_market_unit_count_invariant_violation_count)
- Any C4 violation: non-RTH bar in channel / MOC opens / eod_cancel misalignment
- Any C5 violation: position held across expiry without explicit handling
- Any C6 violation: schema_id bump / cagr from CONFIG / win_rate as number when n<100 / missing seal / max_units_observed > 1
- Any C7 enum extension or live-ready interpretation
- Any C8 weak-performance iteration / parking revival / threshold loosening / starting_cash != 500000 re-run under s10-D2 namespace
- Any K1..K12 fire from Tier-N rejection_gates
- Any S-STOP-1..S-STOP-10 from Tier-N stop_conditions
- Any S-STOP-11 fire: max_units_per_market != 1 detected anywhere
- Any S-STOP-12 fire: any s8-D1 chain artifact byte sha changes during s10-D2 turn
- Any S-STOP-13 fire: any s7-D1 chain artifact byte sha changes during s10-D2 turn
- Any S-STOP-14 fire: starting_cash != 500000 detected anywhere
- Any sealed parent sha drift detected mid-run
- Any obsidian-trade-logger mutation, review_queue mutation, strategy_lab promotion
- Any Databento key printed/echoed/logged
- Any QC API call from the local-engine code path or vice versa

---

## What future P3 BUILD MAY create

- Runner harness directory: `external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness/`
- Files in runner harness:
  - main.py (QC LEAN entry; lazy QC import; LiveMode raise; CONFIG dict)
  - execution_guard.py (C1-C8 attestation runtime hooks; no broker imports)
  - in_sample_driver.py (local Databento DBN decoder + Donchian backtest; DIRECT REUSE of s8-D1 patched driver mechanic with starting_cash=500000 CONFIG override)
  - tests/test_smoke_t1_t15.py (synthetic-only T1-T15 smoke battery)
  - tests/__init__.py
  - __init__.py
- BUILD reports under `reports/external_research_hunter/`:
  - s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_build_report.{md,json}
  - s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_in_sample_driver_build_report.{md,json} (when driver is patched/built)
- No smoke run yet; no in-sample run yet.

## What future P3 BUILD MAY NOT create

- Any file outside external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness/ or reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_*
- Any data/databento_cache/** mutation (cache is operator-managed; s10-D2 reuses s8-D1 cache)
- Any review_queue.json mutation
- Any strategy_lab approval or queue file
- Any obsidian-trade-logger file or directory
- Any modification of existing s8-D1 / s7-D1 chain artifacts or runner harness files
- Any broker/exchange/wallet/API adapter import
- Any Databento Historical client instantiation (db.Historical is forbidden in local-engine path)
- Any network call

---

## Pre-flight checklist for future P6 in-sample run

- Verify plan-lock seal byte-stable (ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354)
- Verify Tier-N spec seal byte-stable (f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679)
- Verify S10 selection plan + availability analysis seals byte-stable
- Verify all 20 s8-D1 chain artifacts byte-stable (S-STOP-12)
- Verify all s7-D1 chain artifacts byte-stable (S-STOP-13)
- Verify databento local cache: 480 IS + 144 OOS = 624 files / 172,454,306 bytes (s8-D1 cache re-used)
- Verify in_sample_driver.py byte sha matches BUILD-time recorded sha
- Verify CONFIG['starting_cash_mnq_equivalent'] == 500000 (S-STOP-14)
- Verify CONFIG['max_units_per_market'] == 1 (S-STOP-11)
- Verify AMB6 filter NONE at runtime (no filter functions wired)
- Verify obsidian-trade-logger tracked-file count and byte-total baseline preserved at run start
- Verify operator P6 authorization line received explicitly

---

## S8-D1 non-revival attestation

- `s8_d1_chain_status`: PERMANENTLY_PARKED_AT_COMMIT_6e7b491
- `s8_d1_final_operational_status`: PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED
- `s8_d1_revived_by_this_phase2_plan`: False
- `s8_d1_chain_artifacts_count`: 20
- `s8_d1_chain_byte_stable_at_authorship`: True
- `s8_d1_used_as`: UPSTREAM_EVIDENCE_AND_PARAMETER_BASELINE_ONLY
- `s8_d1_strategy_logic_not_inherited_beyond_locked_parameters`: True

Other parked/rejected candidates NOT revived: S7-D1, D5 (s7-YM-only / s8-ZN-only), B005_001, NKE Options Wheel, S2-Kraken-XRP, S3-MNQ-DRB, S4-Turtle-System-1, S5-baseline, S6-full-system, S10-D1 micro path (deferred per S10 availability analysis).

---

## Parent chain inheritance evidence (10 byte-stable; drift=0)

| Parent | sha256 | path |
|---|---|---|
| `S10_D2_plan_lock` | `ba8bf954d44b373c...` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_plan_lock.json` |
| `S10_D2_tier_n_spec` | `f5ca5ee63024e9c8...` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_tier_n_spec.json` |
| `S10_availability_analysis` | `417ed6c7b4e177e0...` | `reports/external_research_hunter/s10_micro_futures_availability_attestation_analysis.json` |
| `S10_selection_plan` | `007110ff5a57dd04...` | `reports/external_research_hunter/s10_micro_futures_successor_selection_plan.json` |
| `S7_D1_PARKING` | `551fdce46c0e373e...` | `reports/external_research_hunter/s7_d1_cross_asset_donchian_PARKING_REPORT.json` |
| `S8_D1_P11_lifecycle` | `c79b06206c51d9b9...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_p11_lifecycle_decision.json` |
| `S8_D1_phase2_plan` | `5e6fccd1aeb40db7...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_phase2_plan.json` |
| `S8_D1_tier_n_spec` | `8cff6babf8e4a451...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_tier_n_spec.json` |
| `phase2_safety_template_json` | `695a9fb6e0cb6ae5...` | `docs/phase2_safety_contract_template.json` |
| `phase2_safety_template_md` | `1812f4854a23e7a1...` | `docs/phase2_safety_contract_template.md` |

---

## Negative invariants this turn (all True)

- `no_b005_001_revival`: True
- `no_broker_adapter_instantiated`: True
- `no_code_authored`: True
- `no_credential_logged`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_databento_api_call`: True
- `no_databento_fetch`: True
- `no_databento_historical_client_instantiated`: True
- `no_databento_key_printed`: True
- `no_frc_granted`: True
- `no_in_sample_backtest`: True
- `no_in_sample_driver_invocation`: True
- `no_kraken_binance_alpaca_use`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_data_load`: True
- `no_oos_metric_compute`: True
- `no_oos_window_inspection`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_quantconnect_api_call`: True
- `no_quantconnect_submit`: True
- `no_review_queue_json_mutation`: True
- `no_runner_harness_directory_created`: True
- `no_s7_d1_revival`: True
- `no_s8_d1_revival`: True
- `no_scheduler_modification`: True
- `no_strategy_lab_promotion`: True
- `no_synthetic_smoke_run`: True
- `no_test_file_authored`: True

---

## Recommended next step

> **operator_authorization_required_for_BUILD_ONLY_turn_P3**

---

*End of S10-D2 P2 Phase-2 plan. Sealed at `7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3`. PHASE-2 PLAN DOC ONLY. No code, no BUILD, no backtest, no fetch, no live/paper trading change.*

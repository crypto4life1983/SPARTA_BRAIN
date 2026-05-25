# s8-D1 Cross-Asset Donchian No-Pyramid - P2 Phase-2 Plan (SEALED)

**Artifact type:** `phase2_plan`
**Schema id:** `sparta.external_research_hunter.s8_d1_cross_asset_donchian_no_pyramid_phase2_plan.v1`
**Schema status:** `SEALED`
**Canonical record id:** `s8-cross-asset-donchian-no-pyramid-nq-gc-zn-cl`
**Candidate operational status:** `PHASE2_PLAN_SEALED`
**Phase:** `P2_PHASE2_PLAN_SEALED_BUILD_NOT_AUTHORIZED`
**Report date UTC:** 2026-05-25T23:17:13Z

**Phase-2 plan seal sha256:** `5e6fccd1aeb40db7daf850ab60eff2947a03a082a6bcb5b332c967e2d8f9c826`
**Seal method:** `LESSON_HUNTER_004` canonical roundtrip

**Predecessor seal (P1 plan-lock):** `612abbbda7235c8c01239000cf997c804cd8178d88d2afbb9752004aed34e0a1`
**Tier-N spec seal:** `8cff6babf8e4a451adf02e94a684924ff8b32a7e0f5a795a13c65c845a12e0f4`
**S8 selection plan seal:** `6b7bdb4c350f4a779611546dcb32f6a83db2371c66d7b6ba0118121783801441`
**Spec MD sha:** `ada2c060a63a9f3bba81ab43f6cf30a926b6cfb95b58784796f1f2c2846b9d52`

> **Labels:** EXTERNAL_CLAIM_ONLY, NEEDS_VERIFICATION, NOT_A_SIGNAL,
> DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, PLAN_AND_SPEC_ONLY, NO_FRC_GRANTED,
> S8_D1_P2_PHASE2_PLAN_SEALED, SINGLE_DELTA_FROM_S7_D1_MAX_UNITS_1,
> NO_S7_D1_REVIVAL

> **Trading status:** PAUSED | **Live status:** BLOCKED_AT_6_GATES | **FRC:** not granted
> No backtest. No fetch. No OOS inspection. No live or paper trading change.

---

## Phase-2 safety template inheritance

Inherits Phase 2 safety contracts (C1-C8) from:

- `docs/phase2_safety_contract_template.md` -- sha `1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981`
- `docs/phase2_safety_contract_template.json` -- sha `695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32`

Adapts each C-contract to s8-D1 specifics. Does NOT revive any parked or rejected candidate.

---

## C1-C8 required evidence summary (one-line)

- **C1** LiveMode raise in Initialize; status_fields strings PAUSED / BLOCKED_AT_6_GATES; no broker/exchange/wallet/api adapter in imports
- **C2** engine-truth run_id; Initialize date cross-check; window ceiling check; plan_doc_sha256 = canonical seal of this phase2_plan.json
- **C3** all universal + futures-specific counters tracked; unique-day-set pattern; **no_pyramid_state_machine_violation_count must be 0 (vestigial under max_units=1 but still tracked for safety_zero)**
- **C4** per-market RTH windows; eod_cancel == rth_close per market; LIMIT discipline; quote_age + spread checks
- **C5** known_contract_rolls + known_expirations populated from CME calendar + Databento `definition` schema; blackout + LIMIT pre-close; unsupported-MOC detection
- **C6** schema_id == sparta.external_research_hunter.s8_d1_cross_asset_donchian_no_pyramid_in_sample_diagnostic.v1; cagr from engine; win_rate literal when n<100; **per-market unit-count audit (must always be 0 or 1 under no-pyramid)**
- **C7** closed enum {FAIL_SAFETY, INSUFFICIENT_SAMPLE, READY_FOR_LONGER_BACKTEST}; min_closed_trades=100; K-gates run in parallel; **no enum extension**
- **C8** park-on-weak-performance rule; revival requires fresh s9-* candidate_record_id; live-block permanent; **no s8-D2 max_units=2 patch-up of this candidate**

---

## No-pyramid mechanics explicit record

| Field | Value |
|---|---|
| `max_units_per_market` | **1** |
| `max_units_per_market_invariant` | S-STOP-11 fires if != 1 detected anywhere |
| Pyramid spacing | 0.5N (vestigial, never fires under max_units=1) |
| Expected open-unit count per market | {0, 1} |
| Expected portfolio unit count | {0, 1, 2, 3, 4} |
| Portfolio cap (max units total) | 4 |
| Portfolio cap structurally non-binding | **True** (4 markets x 1 unit = 4) |
| Portfolio cap uses unit count not contract count (s6 bugfix) | **True** |
| Any unit count observed outside set | **FAIL_SAFETY top priority** |
| N source | Wilder ATR(20) of entry market at trigger bar; locked at unit entry |
| No N re-use across pyramid units | trivially true (no second unit exists) |

---

## AMB6 filter confirmation

- `amb6_filter_setting`: **NONE**
- `amb6_filter_structurally_locked_none`: True
- `same_direction_filter`: False
- `ma_filter`: False
- `regime_filter`: False
- `correlation_gate`: False
- Any new filter introduction at or after BUILD time triggers **K7** (PARKED_SAFETY_FAILED)

---

## Data source confirmation

- Data source at runtime: **DATABENTO GLBX.MDP3 local cache only**
- No fresh Databento fetch authorized by this plan: **True**
- s7-D1 P5 cache re-used: **True** (480 files, 129,789,451 bytes)
- Local decode path: `db.DBNStore.from_file()`
- No `db.Historical` client in local path
- API key handling at runtime: `os.environ.get('DATABENTO_API_KEY')` only; never printed/logged

---

## Window attestation

- In-sample window UTC: **2013-01-01 -> 2022-12-30** (inclusive)
- OOS window UTC: **2023-01-01 -> 2025-12-30** (noted but NOT inspected)
- OOS inspection during in-sample run: **prohibited**
- Window extension beyond plan-lock ceiling: **forbidden**

---

## Future steps gating (all require separate explicit operator authorization)

- **P3** BUILD ONLY -- runner harness + execution_guard + driver + tests scaffold (under s8-D1 namespace)
- **P4** T1-T15 synthetic smoke pass
- **No P5 fetch needed** -- s7-D1 P5 cache re-used
- **P6** in-sample run at S1 baseline (optionally S0/S2/S3/S4)
- **P7** in-sample decision memo
- **P8** lifecycle transition (PARK or OOS-AUTHORIZE)

P2 authorizes nothing downstream.

---

## C7 verdict semantics (preserved closed enum)

Allowed verdicts (closed enum, no extensions):

- **FAIL_SAFETY** -- safety counter > 0 at run end (top priority)
- **INSUFFICIENT_SAMPLE** -- closed_trades_portfolio < 100
- **READY_FOR_LONGER_BACKTEST** -- research label only, never means live-ready; 6-gate live-block applies regardless

C7 enum + Tier-N K-gates K1..K12 run in parallel. The candidate proceeds to OOS authorization ONLY if BOTH (VERDICT == READY_FOR_LONGER_BACKTEST) AND (no K fires) AND (Tier-N acceptance gates A1..A10 all pass).

---

## Fail-closed conditions for future BUILD and run phases

- Any C1 violation: LiveMode bypass / status string change / broker import
- Any C2 violation: CONFIG/engine date divergence / window ceiling violation / seal recompute mismatch
- Any C3 hard safety counter > 0 at run end (including new s8-D1 per_market_unit_count_invariant_violation_count > 0)
- Any C4 violation: non-RTH bar in channel / MOC opens / eod_cancel misalignment
- Any C5 violation: position held across expiry without explicit handling / MOC close where rejected
- Any C6 violation: schema_id bump / cagr from CONFIG / win_rate as number when n<100 / missing seal / max_units_observed_per_market_max > 1 / second_unit_add_attempt_count > 0
- Any C7 enum extension or live-ready interpretation
- Any C8 weak-performance iteration / parking revival / threshold loosening / max_units != 1 re-run under s8-D1 namespace
- Any K1..K12 fire from Tier-N rejection_gates
- Any S-STOP-1..S-STOP-10 from Tier-N stop_conditions
- Any S-STOP-11 fire: max_units_per_market != 1 detected anywhere
- Any S-STOP-12 fire: any s7-D1 chain artifact byte sha changes during s8-D1 turn
- Any sealed parent sha drift detected mid-run
- Any obsidian-trade-logger mutation, review_queue mutation, strategy_lab promotion
- Any Databento key printed/echoed/logged
- Any QC API call from the local-engine code path or vice versa

---

## What future P3 BUILD MAY create

- Runner harness directory: `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/`
- Files in runner harness:
  - main.py (QC LEAN entry; lazy QC import; LiveMode raise; CONFIG dict)
  - execution_guard.py (C1-C8 attestation runtime hooks; no broker imports)
  - in_sample_driver.py (local Databento DBN decoder + Donchian backtest; DIRECT REUSE of s7-D1 patched driver mechanic with max_units=1 CONFIG override)
  - tests/test_smoke_t1_t15.py (synthetic-only T1-T15 smoke battery)
  - tests/__init__.py
  - __init__.py
- BUILD reports under `reports/external_research_hunter/`:
  - s8_d1_cross_asset_donchian_no_pyramid_runner_build_report.{md,json}
  - s8_d1_cross_asset_donchian_no_pyramid_in_sample_driver_build_report.{md,json} (when driver is patched/built)
- No smoke run yet; no in-sample run yet.

## What future P3 BUILD MAY NOT create

- Any file outside external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/ or reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_*
- Any test artifact under tests/<runtime-output>/ (BUILD ONLY allows test scaffolding, NOT test execution)
- Any data/databento_cache/** mutation (cache is operator-managed)
- Any review_queue.json mutation
- Any strategy_lab approval or queue file
- Any obsidian-trade-logger file or directory
- Any modification of existing s7-D1 runner harness files or any prior chain artifacts
- Any broker/exchange/wallet/API adapter import
- Any Databento Historical client instantiation (db.Historical is forbidden in local-engine path)
- Any network call

---

## Pre-flight checklist for future P6 in-sample run

- Verify plan-lock seal byte-stable (612abbbda7235c8c01239000cf997c804cd8178d88d2afbb9752004aed34e0a1)
- Verify Tier-N spec seal byte-stable (8cff6babf8e4a451adf02e94a684924ff8b32a7e0f5a795a13c65c845a12e0f4)
- Verify selection plan seal byte-stable (6b7bdb4c350f4a779611546dcb32f6a83db2371c66d7b6ba0118121783801441)
- Verify all 14 s7-D1 chain artifacts byte-stable (S-STOP-12)
- Verify databento local cache: 480 files / 129,789,451 bytes (s7-D1 P5 cache re-used)
- Verify in_sample_driver.py byte sha matches BUILD-time recorded sha
- Verify CONFIG['max_units_per_market'] == 1 (S-STOP-11)
- Verify AMB6 filter NONE at runtime (no filter functions wired)
- Verify obsidian-trade-logger tracked-file count and byte-total baseline preserved at run start
- Verify operator P6 authorization line received (no auto-run)

---

## s7-D1 non-revival attestation

- s7-D1 chain status: **PERMANENTLY_PARKED_AT_COMMIT_f08220a**
- s7-D1 revived by this phase-2 plan: **False**
- s7-D1 used as: **UPSTREAM EVIDENCE AND MECHANICAL BASELINE ONLY**
- All 14 s7-D1 sealed artifacts byte-stable at authorship

Other parked/rejected candidates not revived: s7-D5 (YM-only), s8-D5 (ZN-only), B005_001, NKE Options Wheel, s2-Kraken-XRP, s3-MNQ-DRB, s4-Turtle-System-1, s5-baseline, s6-full-system.

---

## Parent chain inheritance evidence (13 parents, all byte-stable at authorship)

| Parent | sha256 | reason |
|---|---|---|
| `phase2_safety_template_json` | `695a9fb6e0cb6ae5...` | C1_C8_SAFETY_TEMPLATE_JSON |
| `phase2_safety_template_md` | `1812f4854a23e7a1...` | C1_C8_SAFETY_TEMPLATE_MD |
| `s7_d1_decision_memo` | `5354d3395319e309...` | S7_D1_DECISION_RATIONALE |
| `s7_d1_diag_rev2` | `2563ef9309217171...` | S7_D1_OPERATIVE_STRATEGY_RESULT_LOAD_BEARING_EVIDENCE |
| `s7_d1_parking_report` | `551fdce46c0e373e...` | S7_D1_PERMANENT_PARK_STATE_NOT_REVIVED |
| `s7_d1_patch_build_report` | `2ab3ed5852de0dad...` | PATCHED_DRIVER_MECHANIC_BASELINE_FOR_S8_BUILD |
| `s7_d1_phase2_plan_for_pattern` | `e1800ee28bd99a27...` | PHASE2_PLAN_AUTHORING_PATTERN_BASELINE_NO_CONTENT_INHERITANCE_BEYOND_C1_C8_STRUCTURE |
| `s8_d1_plan_lock_json` | `612abbbda7235c8c...` | DIRECT_PARENT_P1_PLAN_LOCK |
| `s8_d1_plan_lock_md` | `107961a11e15ea73...` | PLAN_LOCK_MD_COMPANION |
| `s8_d1_spec_md` | `ada2c060a63a9f3b...` | HUMAN_READABLE_SPEC_DRAFT |
| `s8_d1_tier_n_spec_json` | `8cff6babf8e4a451...` | TIER_N_SPEC_LOCKED_PARAMETERS |
| `s8_d1_tier_n_spec_md` | `380400582343fbf7...` | TIER_N_SPEC_MD_COMPANION |
| `s8_selection_plan_json` | `6b7bdb4c350f4a77...` | SELECTION_PROVENANCE |

Drift count at authorship: **0**.

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
- `no_scheduler_modification`: True
- `no_strategy_lab_promotion`: True
- `no_synthetic_smoke_run`: True
- `no_test_file_authored`: True

---

## Next step

> **AUTHORIZE S8-D1 P3 BUILD ONLY** -- author runner harness + execution_guard + in_sample_driver + tests scaffold under `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/`. No smoke run. No backtest.

---

*End of s8-D1 P2 Phase-2 plan (SEALED). Phase-2 plan only -- no code, no backtest, no Databento, no QC, no fetch, no live/paper trading, no scheduler change, no obsidian mutation, no review_queue mutation, no D5/B005_001/NKE/s7-D1 revival, no profitability claim.*

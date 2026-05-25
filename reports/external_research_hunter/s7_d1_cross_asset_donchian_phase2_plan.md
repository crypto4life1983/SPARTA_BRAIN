# s7 D1 — Phase-2 Plan Doc (SEALED)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_phase2_plan.v1`
**Status:** `SEALED`
**Candidate:** `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl`
**Sealed at (UTC):** `2026-05-25T15:24:42Z`
**Predecessor seal:** `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
**Tier-N spec seal sha256:** `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
**Plan-lock seal sha256:** `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`
**FRC granted:** `False`
**Advisory label permanent:** `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

> PLAN-ONLY. No BUILD, no runner code, no smoke, no fetch, no run.
> Specifies what C1-C8 mean for s7 D1; what evidence each gate requires;
> what conditions fail closed; what future P3 BUILD may and may not create.
> P2 authorizes nothing downstream. NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT holds.

## Inheritance attestation
- Parent sha drift at P2: **0**
- Tier-N JSON seal match recorded: **True**
- Tier-N JSON roundtrip match: **True**
- Tier-N MD byte sha match recorded: **True**
- Plan-lock JSON seal match recorded: **True**
- Plan-lock JSON roundtrip match: **True**
- Spec MD match recorded: **True**
- Seal plan MD match recorded: **True**
- Phase-2 safety template MD match: **True** (sha `1812f4854a23e7a1...`)
- Phase-2 safety template JSON match: **True** (sha `695a9fb6e0cb6ae5...`)

## C1-C8 specifications for s7 D1 (one-line summary)
- **C1** — LiveMode raise in Initialize; status_fields strings PAUSED / BLOCKED_AT_6_GATES
- **C2** — engine-truth run_id; Initialize date cross-check; window ceiling check
- **C3** — all universal + futures-specific counters tracked; unique-day-set pattern
- **C4** — per-market RTH windows; eod_cancel == rth_close per market; LIMIT discipline
- **C5** — known_contract_rolls + known_expirations populated; blackout + LIMIT pre-close; unsupported-MOC detection
- **C6** — schema_id == s7_d1_cross_asset_donchian_in_sample_diagnostic.v1; cagr from engine; win_rate literal when n<100
- **C7** — closed enum {FAIL_SAFETY, INSUFFICIENT_SAMPLE, READY_FOR_LONGER_BACKTEST}; min_closed_trades=100; K-gates run in parallel
- **C8** — park-on-weak-performance rule; revival requires fresh s8 candidate_record_id; live-block permanent

## Fail-closed conditions for the future runner
- Any C1 violation: LiveMode bypass / status string change / broker import
- Any C2 violation: CONFIG/engine date divergence / window ceiling violation / seal recompute mismatch
- Any C3 hard safety counter > 0 at run end
- Any C4 violation: non-RTH bar in channel / MOC opens / eod_cancel misalignment
- Any C5 violation: position held across expiry without explicit handling / MOC close on a brokerage that rejects it
- Any C6 violation: schema_id bump / cagr from CONFIG / win_rate as number when n<100 / missing seal
- Any C7 enum extension or live-ready interpretation
- Any C8 weak-performance iteration / parking revival / threshold loosening
- Any K1..K12 fire from Tier-N rejection_gates
- Any S-STOP-1..S-STOP-10 from Tier-N stop_conditions
- Any sealed parent sha drift detected mid-run
- Any obsidian-trade-logger mutation, review_queue mutation, strategy_lab promotion
- Any Databento key printed/echoed/logged
- Any QC API call from the local-engine code path or vice versa

## What future P3 BUILD may create
**Scope root:** `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/`

Allowed files (recap from plan-lock):
- `main.py`
- `execution_guard.py`
- `README.md`
- `__init__.py`
- `requirements.txt`
- `tests/__init__.py`
- `tests/test_smoke_t1_t15.py`
- `tests/conftest.py`
- `tests/fixtures/synthetic_{nq,gc,zn,cl}_daily.csv`

Allowed BUILD-time report files (recap from plan-lock):
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_runner_build_report.{md,json}`
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_execution_guard_build_report.{md,json}`

Module constants the future runner MUST embed:
- `tier_n_spec_seal_sha256` = `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
- `plan_lock_seal_sha256` = `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d`
- `plan_doc_sha256` = `<computed at BUILD time as canonical_seal of this phase2_plan.json>`
- `algo_version_for_run_id` = `s7_d1_v0_1_0`
- `phase_prefix` = `PHASE2-S7-D1-XAD-NF`
- `predecessor_seal` = `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`

## What future P3 BUILD may NOT create
- Any file outside external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/
- Any runner-side or guard-side network call
- Any Databento key handling code that prints/logs/echoes the key
- Any QC API stub that would execute at build-time module import
- Any broker / exchange / wallet adapter import
- Any signal-shaped output (e.g. live trade decisions, real-time alerts)
- Any test that reads real market data (T1-T15 are synthetic-only)
- Any file under obsidian-trade-logger/, local_secrets/, or any other repo
- Any modification to review_queue.json, idea_memory, or Strategy Lab state

## Pre-flight checklist for future P6 in-sample run
- PF1: All 16 sealed parent shas match disk (canonical recompute for JSON parents; byte sha for Phase 2 template files)
- PF2: Tier-N spec seal sha matches recorded (72602305...)
- PF3: Plan-lock seal sha matches recorded (0f8e9fe6...)
- PF4: This phase2_plan.json seal matches its embedded report_seal_sha256
- PF5: All 4 Databento caches present and complete (NQ.c.0 already cached; GC, ZN, CL fetched by operator before this turn)
- PF6: CONFIG['end_date'] == [2022,12,30] and == plan_lock_window_ceiling
- PF7: Per-market rth_safe_window_close == eod_cancel_time
- PF8: known_contract_rolls and known_expirations populated for 2013-2022 in-sample window
- PF9: Deterministic run_id computed offline; distinct from all prior PHASE2-* run_ids
- PF10: Smoke init in QC OR local engine produces expected algo_version + run_id banner without CONFIG_*_DATE_MISMATCH

## Negative invariants (THIS Phase-2 plan-doc turn — all True)
- `no_code_authored_this_turn`: `True`
- `no_runner_code_authored`: `True`
- `no_execution_guard_code_authored`: `True`
- `no_test_authored`: `True`
- `no_smoke_executed_this_turn`: `True`
- `no_backtest_run_this_turn`: `True`
- `no_databento_call_this_turn`: `True`
- `no_qc_call_this_turn`: `True`
- `no_data_fetch_this_turn`: `True`
- `no_network_call_this_turn`: `True`
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
- `no_threshold_loosened`: `True`
- `no_oos_inspection`: `True`
- `no_profitability_claim`: `True`
- `no_tier_n_spec_or_plan_lock_or_seal_plan_modified`: `True`
- `no_parent_artifact_modified`: `True`
- `no_phase2_safety_template_modified`: `True`

## What this plan does NOT authorize
- P3 BUILD: separate operator authorization required
- P4 T1-T15 smoke: separate operator authorization required
- P5 operator-side Databento fetch: operator-managed, not Claude-executable
- P6 in-sample run: separate operator authorization required
- P7 in-sample decision memo: separate operator authorization required
- P8 lifecycle transition: separate operator authorization required
- OOS inspection: blocked until in-sample passes
- Live trading: permanently `BLOCKED_AT_6_GATES`

## Next step
- `operator_authorization_required_for_BUILD_ONLY_turn_P3`
- Invariant: `NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT_HOLDS`

## Citation block
```
# Inherits Phase 2 safety contracts (C1-C8) from:
#   docs/phase2_safety_contract_template.md  (sha 1812f485...8981)
#   docs/phase2_safety_contract_template.json (sha 695a9fb6...4a32)
# Template source candidate (parked, not money-proven):
#   s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
# Template reuse notice: NKE strategy logic NOT inherited; only safety contracts.
# Inherits Tier-N spec seal: 72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3
# Inherits plan-lock seal: 0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d
# Inherits s7 selection plan seal: 8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac
```

## Seal block (canonical)
- **`report_seal_sha256`**: `e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_phase2_plan.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T15:24:42Z`

*End of Phase-2 plan doc. Plan only — no implementation, no backtest, no fetch, no network, no live or paper trading.*

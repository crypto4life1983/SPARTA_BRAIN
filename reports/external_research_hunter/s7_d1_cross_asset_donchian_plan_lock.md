# s7 D1 — Plan-Lock (SEALED)

**Schema:** `sparta.external_research_hunter.s7_d1_cross_asset_donchian_plan_lock.v1`
**Status:** `SEALED`
**Candidate:** `s7-cross-asset-donchian-no-filter-nq-gc-zn-cl`
**Sealed at (UTC):** `2026-05-25T15:10:57Z`
**Tier-N spec seal sha256:** `72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3`
**Tier-N spec MD sha256:** `76fa35efcb2b40f8911a0bf0102e447bb1d983034ad8c39da862ba08cbba2cfb`
**Predecessor seal:** `8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac`
**Spec MD sha256:** `c36588e77899f2511a429b967c0d2fab7bbf85828afae8af7cb4043f96764d4f`
**Seal plan MD sha256:** `40a2ef6a0811fe02f1e00cde62bea5133818ab2d6f6a1908eb9775321126420b`
**Trading status:** `PAUSED`
**Live status:** `BLOCKED_AT_6_GATES`
**FRC granted:** `False`

> PLAN-LOCK ONLY. No BUILD, no smoke, no fetch, no run.
> Defines the future BUILD scope and future T1-T15 smoke gates.
> Authorizes nothing downstream. NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT holds.

## Inheritance attestation
- Parent sha drift at lock: **0**
- Phase 2 safety template MD match: **True**
- Phase 2 safety template JSON match: **True**
- Tier-N spec JSON seal match recorded: **True**
- Tier-N spec JSON roundtrip match: **True**
- Tier-N spec MD match recorded: **True**
- Spec MD match recorded: **True**

## Future build_scope (allowed paths only)
**Root:** `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/`

Allowed files (BUILD turn may create exactly these; no others):
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/main.py`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/execution_guard.py`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/README.md`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/__init__.py`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/requirements.txt`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/tests/__init__.py`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/tests/test_smoke_t1_t15.py`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/tests/conftest.py`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/tests/fixtures/synthetic_nq_daily.csv`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/tests/fixtures/synthetic_gc_daily.csv`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/tests/fixtures/synthetic_zn_daily.csv`
- `external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/tests/fixtures/synthetic_cl_daily.csv`

Allowed BUILD-time report files:
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_runner_build_report.json`
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_runner_build_report.md`
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_execution_guard_build_report.json`
- `reports/external_research_hunter/s7_d1_cross_asset_donchian_execution_guard_build_report.md`

## Future build_scope invariants
- `no_file_outside_build_scope_may_be_created_or_modified`: `True`
- `no_databento_call_at_build_time`: `True`
- `no_qc_call_at_build_time`: `True`
- `no_network_call_at_build_time`: `True`
- `no_data_fetch_at_build_time`: `True`
- `no_real_market_data_read_at_build_time`: `True`
- `no_live_trading_code_imported`: `True`
- `no_broker_or_exchange_adapter_instantiation`: `True`
- `no_kraken_binance_alpaca_anywhere_in_imports`: `True`
- `no_review_queue_mutation`: `True`
- `no_obsidian_trade_logger_touch`: `True`
- `no_filter_silently_introduced`: `True`
- `no_correlation_gate_silently_introduced`: `True`
- `no_threshold_loosening`: `True`
- `no_d5_revival`: `True`
- `no_b005_001_revival`: `True`
- `no_nke_revival`: `True`
- `no_strategy_lab_promotion`: `True`
- `no_credential_logged`: `True`
- `no_databento_key_printed_or_echoed`: `True`
- `imports_must_be_pure_python_plus_stdlib_plus_numpy_pandas_only_at_build_time`: `True`
- `no_quantconnect_lean_module_import_required_at_build_time`: `True`
- `runner_main_py_must_be_importable_without_qc_runtime_via_lazy_QC_attr_access`: `True`
- `execution_guard_must_be_runtime_safe_with_no_side_effects_on_import`: `True`
- `all_constants_must_match_tier_n_spec_byte_equivalent`: `True`
- `sha_pinned_tier_n_spec_seal_must_be_embedded_in_main_py_module_constant`: `True`

## Future T1-T15 smoke gates
- `T1` (module_imports_clean): import of main + execution_guard succeeds in isolated venv with no QC runtime present
- `T2` (runner_class_instantiable): runner class constructs on synthetic config without QC API access
- `T3` (wilder_atr_20_synthetic): WilderATR(20) on a deterministic synthetic series matches a hand-computed expected value within 1e-9
- `T4` (donchian_55_20_synthetic): Donchian high/low channel computation on synthetic series matches expected for entry=55 and exit=20
- `T5` (entry_trigger_synthetic_breakout): synthetic breakout bar fires the long-entry ENTRY_PENDING state for the next RTH open
- `T6` (stop_placement_at_2n): initial stop set at exactly 2*N below entry for long (above for short); per-unit N recorded
- `T7` (pyramid_trigger_at_05n): next pyramid trigger set at +0.5*N above (long) / below (short) last unit entry
- `T8` (exit_on_donchian_20_reversal): all open units of a market exit at next RTH open when the Donchian-20 reverse channel is breached
- `T9` (portfolio_cap_uses_unit_count): PortfolioCapTracker uses pyr.current_unit_count (max 4 per market * 4 markets = 16 cap); cap_binding_events_count == 0 in normal 4-unit lifecycle (s6 bugfix regression test)
- `T10` (sizing_1pct_floor): contract count = floor((0.01 * portfolio_equity) / (N_entry * dollar_per_point)); deterministic on synthetic
- `T11` (skip_when_contract_count_lt_one): entry skipped + logged when computed contract count < 1; no fill
- `T12` (rth_only_filter_attested): non-RTH bars do NOT contribute to daily-bar derivation per market; bar-count attested
- `T13` (roll_cost_modeled_1_spread_tick): roll dates absorb exactly 1 spread tick of cost per market; modeled_cost_dollar present in roll_attestation.json
- `T14` (cost_stress_matrix_S0_S1_S2_S3_S4): matrix constructable with 5 cost tiers; per-market baseline reads from CONFIG byte-equivalent to Tier-N spec
- `T15` (validator_harness_pass_on_synthetic): the 16+ item validator returns VALIDATOR_PASS on the synthetic smoke run; produces a sealed t1_t15 smoke pass JSON via LESSON_HUNTER_004 canonical roundtrip

**Smoke threshold:** `ALL_15_T_GATES_MUST_PASS_BEFORE_OPERATOR_AUTHORIZES_DATABENTO_FETCH`
**Smoke uses synthetic data only:** `True`
**Smoke reads no real data:** `True`

## Negative invariants (THIS plan-lock turn — all True)
- `no_code_authored_this_turn`: `True`
- `no_build_executed_this_turn`: `True`
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
- `no_tier_n_spec_or_seal_plan_modified`: `True`
- `no_parent_artifact_modified`: `True`

## What this plan-lock does NOT authorize
- P2 Phase-2 plan-doc authoring: separate operator authorization required
- P3 BUILD runner: separate operator authorization required
- P4 T1-T15 smoke: separate operator authorization required
- P5 operator-side Databento fetch: operator-managed, not Claude-executable
- P6 in-sample run: separate operator authorization required
- P7 in-sample decision memo: separate operator authorization required
- P8 lifecycle transition: separate operator authorization required
- OOS inspection: blocked until in-sample passes
- Live trading: permanently `BLOCKED_AT_6_GATES`

## Next step
- `operator_authorization_required_for_phase2_plan_doc_authoring_P2`
- Invariant: `NO_BACKTEST_BEFORE_SEAL_AND_AUTHORIZATION_INVARIANT_HOLDS`

## Seal block (canonical)
- **`report_seal_sha256`**: `0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d`
- **`seal_method`**: `sha256 over json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False, default=str) EXCLUDING report_seal_sha256 + seal_method`
- **`schema_id`**: `sparta.external_research_hunter.s7_d1_cross_asset_donchian_plan_lock.v1`
- **`schema_status`**: `SEALED`
- **`report_date_utc`**: `2026-05-25T15:10:57Z`

*End of plan-lock. Plan only — no implementation, no backtest, no fetch, no network, no live or paper trading.*

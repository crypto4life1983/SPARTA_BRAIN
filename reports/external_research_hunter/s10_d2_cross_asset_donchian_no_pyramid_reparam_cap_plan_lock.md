# S10-D2 Reparam-Cap Cross-Asset Donchian No-Pyramid - P1 Plan-Lock (SEALED)

**Artifact type:** `plan_lock`
**Canonical record id:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Plan-lock version:** v1
**Phase:** `P1_PLAN_LOCK_SEALED_BUILD_NOT_AUTHORIZED`
**Authored UTC:** 2026-05-26T23:59:08Z

**Plan-lock seal sha256:** `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`
**Seal method:** `LESSON_HUNTER_004` canonical roundtrip

> Labels: DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, NO_FRC_GRANTED, S10_D2_P1_PLAN_LOCK_SEALED,
> SINGLE_DELTA_FROM_S8_D1_STARTING_CASH_500K, NO_S8_D1_REVIVAL, NO_S7_D1_REVIVAL,
> NO_NAMESPACE_COLLISION_WITH_PARALLEL_S9_RSI_2

---

## Direct parent inheritance

| Parent | Seal sha256 | Role |
|---|---|---|
| S10-D2 Tier-N spec (JSON) | `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679` | direct parent; locked parameters |
| S10 selection plan | `007110ff5a57dd04b184409bad64fd667374cd049155416c869a73f7af0c1f97` | selection provenance, D1 deferred → D2 selected |
| S10 availability analysis | `417ed6c7b4e177e0681a3fe20a03744cb22c9946b9755e077a3def3afd7f50e7` | data availability constraint; D2 elected because D1 micro path K9-blocked |

All inherited seals byte-stable at authorship.

---

## Locked invariants (the plan-lock contract)

| Invariant | Value |
|---|---|
| `canonical_record_id` | `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl` |
| Naming prefix | `s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_` |
| **`starting_cash_mnq_equivalent`** | **$500,000** (DELTA from s8-D1 $100k) |
| `max_units_per_market` | 1 (s8-D1 preserved) |
| No-pyramid invariant | True (pyramid spacing 0.5N vestigial) |
| AMB6 filter | NONE (structurally locked) |
| Donchian entry channel | 55 |
| Donchian exit channel | 20 |
| Wilder ATR period | 20 |
| Stop multiplier | 2.0N |
| Per-unit risk | 1.0% portfolio equity |
| Universe | NQ.c.0, GC.c.0, ZN.c.0, CL.c.0 (4 markets; s8-D1 preserved) |
| Data source at runtime | DATABENTO GLBX.MDP3 **local cache only** (s8-D1 cache reused) |
| P5 fetch needed | **No** (s8-D1 IS cache covers) |
| P8.5 OOS fetch needed | **No** (s8-D1 P8.5 cache covers) |
| In-sample window | 2013-01-01 → 2022-12-30 |
| OOS window | 2023-01-01 → 2025-12-30 (**noted but NOT inspected**) |
| Portfolio cap | 4 markets × 1 unit = 4 units (structurally non-binding; s6 bugfix preserved) |
| Cost-stress matrix tiers | S0, S1, S2, S3, S4 (locked) |
| Cost-stress decision rules | DR2, DR3, DR4, DR5 (locked; loosening forbidden) |
| Entry/exit timing | ONO (open-on-next-bar) |
| N source | Wilder ATR(20) of entry market at trigger bar |

---

## Single delta from S8-D1

| Field | S8-D1 | S10-D2 |
|---|---|---|
| `starting_cash_mnq_equivalent` | $100,000 | **$500,000** |
| All other locked parameters | (s8-D1 Tier-N) | byte-equivalent |
| Delta count | — | **1** |

Selected rationale: $500,000 is round number above empirical $476k NQ-clearing threshold from s8-D1 P9.5b sizing-skip audit

---

## S8-D1 non-revival attestation

- `s8_d1_chain_status`: PERMANENTLY_PARKED_AT_COMMIT_6e7b491
- `s8_d1_final_operational_status`: PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED
- `s8_d1_revived_by_this_plan_lock`: False
- `s8_d1_chain_artifacts_count`: 20
- `s8_d1_chain_byte_stable_at_authorship`: True
- `s8_d1_used_as`: UPSTREAM_EVIDENCE_AND_PARAMETER_BASELINE_ONLY
- `s8_d1_strategy_logic_not_inherited_beyond_locked_parameters`: True

---

## Other parked/rejected candidates not revived

- `s8_d1_revived`: False
- `s7_selection_plan_d5_ym_only_revived`: False
- `s8_selection_plan_d5_zn_only_revived`: False
- `b005_001_revived`: False
- `nke_options_wheel_revived`: False
- `s2_kraken_xrp_revived`: False
- `s3_mnq_drb_revived`: False
- `s4_turtle_system_1_revived`: False
- `s5_baseline_revived`: False
- `s6_full_system_revived`: False
- `s7_d1_revived`: False
- `s10_d1_micro_path_NOT_attempted_as_candidate_per_S10_availability_analysis`: True

---

## No namespace collision attestation

- `parallel_session_s9_rsi_2_namespace`: s9-rsi-2 (mean-reversion track)
- `s10_d2_namespace`: s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_
- `collision_check`: no_collision (distinct prefixes; distinct candidate_record_ids)

---

## Parent chain inheritance evidence (12 byte-stable; drift=0)

| Parent | sha256 | path |
|---|---|---|
| `S10_D2_tier_n_spec` | `f5ca5ee63024e9c8...` | `reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_tier_n_spec.json` |
| `S10_availability_analysis` | `417ed6c7b4e177e0...` | `reports/external_research_hunter/s10_micro_futures_availability_attestation_analysis.json` |
| `S10_selection_plan` | `007110ff5a57dd04...` | `reports/external_research_hunter/s10_micro_futures_successor_selection_plan.json` |
| `S7_D1_PARKING` | `551fdce46c0e373e...` | `reports/external_research_hunter/s7_d1_cross_asset_donchian_PARKING_REPORT.json` |
| `S8_D1_P10_decision` | `a493931f0b812fad...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_oos_decision_memo.json` |
| `S8_D1_P11_lifecycle` | `c79b06206c51d9b9...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_p11_lifecycle_decision.json` |
| `S8_D1_P9_5b_sizing` | `957ede055785faf0...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_p9_5b_sizing_skip_cascade_audit_sealed.json` |
| `S8_D1_phase2_plan` | `5e6fccd1aeb40db7...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_phase2_plan.json` |
| `S8_D1_plan_lock` | `612abbbda7235c8c...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_plan_lock.json` |
| `S8_D1_tier_n_spec` | `8cff6babf8e4a451...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_tier_n_spec.json` |
| `phase2_safety_template_json` | `695a9fb6e0cb6ae5...` | `docs/phase2_safety_contract_template.json` |
| `phase2_safety_template_md` | `1812f4854a23e7a1...` | `docs/phase2_safety_contract_template.md` |

---

## Validator items at plan-lock time

- V_PL_1_canonical_record_id_locked
- V_PL_2_naming_prefix_locked_and_unique
- V_PL_3_starting_cash_equals_500000_invariant
- V_PL_4_max_units_per_market_equals_1_invariant
- V_PL_5_no_pyramid_invariant
- V_PL_6_amb6_filter_none_invariant
- V_PL_7_donchian_55_20_invariant
- V_PL_8_wilder_atr_20_2n_stop_invariant
- V_PL_9_1_pct_portfolio_equity_sizing_invariant
- V_PL_10_universe_4_markets_nq_gc_zn_cl_invariant
- V_PL_11_local_databento_cache_reuse_only_no_fresh_fetch
- V_PL_12_in_sample_window_2013_2022_locked
- V_PL_13_oos_window_2023_2025_noted_not_inspected
- V_PL_14_all_future_downstream_require_separate_authorization
- V_PL_15_tier_n_spec_seal_inherited_byte_equivalent
- V_PL_16_s10_availability_analysis_seal_inherited
- V_PL_17_s10_selection_plan_seal_inherited
- V_PL_18_no_s8_d1_revival
- V_PL_19_no_s7_d1_revival
- V_PL_20_no_d5_revival_neither_s7_ym_only_nor_s8_zn_only
- V_PL_21_no_b005_001_revival
- V_PL_22_no_nke_revival
- V_PL_23_no_s9_rsi_2_namespace_collision
- V_PL_24_seal_roundtrip_recompute_match
- V_PL_25_no_code_authored_this_turn
- V_PL_26_no_runner_harness_directory_created_this_turn
- V_PL_27_no_obsidian_touch_file_count_bytes_invariant
- V_PL_28_no_review_queue_mutation

---

## Stop conditions carried forward from Tier-N

- S_STOP_1_sealed_parent_sha_changes_mid_run
- S_STOP_2_phase2_c1_c8_nonzero_safety_warning
- S_STOP_3_databento_api_key_in_any_log_line
- S_STOP_4_non_allowlisted_network_call_or_qc_api_call_in_local_engine_path
- S_STOP_5_write_to_review_queue_idea_memory_strategy_lab_approval_or_obsidian
- S_STOP_6_broker_exchange_adapter_instantiated
- S_STOP_7_k6_or_k7_safety_fire_during_run
- S_STOP_8_data_quality_fail
- S_STOP_9_operator_STOP_S10_D2_instruction
- S_STOP_10_spec_sha_shown_in_runner_neq_sealed_tier_n_spec_sha
- S_STOP_11_max_units_per_market_neq_1_detected_anywhere
- S_STOP_12_any_s8_d1_chain_artifact_byte_sha_changes_during_s10_d2_turn
- S_STOP_13_any_s7_d1_chain_artifact_byte_sha_changes_during_s10_d2_turn
- S_STOP_14_starting_cash_neq_500000_detected_anywhere_in_CONFIG_or_runtime

---

## What this plan-lock does NOT authorize

- code_authoring
- runner_harness_directory_creation
- test_file_authoring
- synthetic_smoke_run
- in_sample_backtest
- in_sample_driver_invocation
- databento_fetch_or_api_call
- databento_historical_client_instantiation
- quantconnect_api_call
- quantconnect_submit
- network_call
- oos_window_inspection
- oos_data_load
- oos_metric_compute
- live_trading_change
- paper_trading_change
- broker_or_exchange_adapter_instantiation
- kraken_binance_alpaca_adapter_use
- review_queue_json_mutation
- obsidian_trade_logger_mutation
- credentials_or_api_key_print_or_log
- strategy_lab_promotion
- scheduler_modification
- spartacus_clone_engine_modification
- hydra_video_modification
- any_existing_artifact_mutation
- any_s8_d1_file_modification_or_revival
- any_starting_cash_value_other_than_500000_for_s10_d2

---

## Future downstream steps (each requires separate explicit operator authorization)

- P2_phase2_plan_authoring
- P3_build_only_runner_execution_guard_in_sample_driver_tests_scaffold_under_s10_d2_namespace
- P4_t1_t15_synthetic_smoke_pass
- no_P5_fetch_needed_existing_s8_d1_cache_re_used
- P6_in_sample_run_S1_baseline_optional_S0_S2_S3_S4_cost_stress
- P7_in_sample_decision_memo
- P7_5_K10_in_sample_correlation_compute
- P8_lifecycle_transition_OOS_deliberation_plan
- no_P8_5_OOS_fetch_needed_existing_s8_d1_P8_5_OOS_cache_re_used
- P9_OOS_S1_run
- P9_5_OOS_cost_stress_optional
- P10_OOS_decision_memo
- P11_lifecycle_decision_final

---

## Boundaries held this turn (all True)

- `no_b005_001_revival`: True
- `no_broker_adapter_instantiated`: True
- `no_code_authored`: True
- `no_credential_logged`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_databento_api_call`: True
- `no_databento_fetch`: True
- `no_databento_historical_client_instantiated`: True
- `no_databento_key_printed`: True
- `no_existing_artifact_mutation`: True
- `no_frc_granted`: True
- `no_hydra_video_modification`: True
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
- `no_s9_rsi_2_namespace_collision`: True
- `no_scheduler_modification`: True
- `no_spartacus_clone_engine_modification`: True
- `no_strategy_lab_promotion`: True
- `no_synthetic_smoke_run`: True
- `no_test_file_authored`: True

---

## Recommended next step

> **AUTHORIZE S10-D2 P2 phase-2 plan-doc authoring only -- single sealed pair under reports/external_research_hunter/s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_phase2_plan.{md,json}, inheriting C1-C8 byte-equivalent from docs/phase2_safety_contract_template.{md,json}**

---

*End of S10-D2 P1 plan-lock. Sealed at `ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354`. PLAN-LOCK ONLY. No code, no BUILD, no smoke, no backtest, no fetch.*

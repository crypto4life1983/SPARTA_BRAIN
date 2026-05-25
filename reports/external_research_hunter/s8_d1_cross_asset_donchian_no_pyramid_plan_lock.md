# s8-D1 Cross-Asset Donchian No-Pyramid - P1 Plan-Lock (SEALED)

**Artifact type:** `plan_lock`
**Canonical record id:** `s8-cross-asset-donchian-no-pyramid-nq-gc-zn-cl`
**Plan-lock version:** v1
**Phase:** `P1_PLAN_LOCK_SEALED_BUILD_NOT_AUTHORIZED`
**Authored UTC:** 2026-05-25T23:05:16Z

**Plan-lock seal sha256:** `612abbbda7235c8c01239000cf997c804cd8178d88d2afbb9752004aed34e0a1`
**Seal method:** `LESSON_HUNTER_004` canonical roundtrip

> **Labels:** EXTERNAL_CLAIM_ONLY, NEEDS_VERIFICATION, NOT_A_SIGNAL,
> DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, PLAN_AND_SPEC_ONLY, NO_FRC_GRANTED,
> S8_D1_P1_PLAN_LOCK_SEALED, SINGLE_DELTA_FROM_S7_D1_MAX_UNITS_1,
> NO_S7_D1_REVIVAL, NO_D5_REVIVAL, NO_B005_001_REVIVAL, NO_NKE_REVIVAL

---

## Direct parent inheritance

| Parent | sha256 | role |
|---|---|---|
| Tier-N spec (JSON seal) | `8cff6babf8e4a451adf02e94a684924ff8b32a7e0f5a795a13c65c845a12e0f4` | direct parent; locked parameters |
| Spec MD (file sha) | `ada2c060a63a9f3bba81ab43f6cf30a926b6cfb95b58784796f1f2c2846b9d52` | human-readable spec draft |
| S8 selection plan (seal) | `6b7bdb4c350f4a779611546dcb32f6a83db2371c66d7b6ba0118121783801441` | selection provenance, D1 at 39/40 |

All three byte-stable at authorship.

---

## Locked invariants (the plan-lock contract)

| Invariant | Value |
|---|---|
| `canonical_record_id` | `s8-cross-asset-donchian-no-pyramid-nq-gc-zn-cl` |
| Naming prefix | `s8_d1_cross_asset_donchian_no_pyramid_` (no other s8 variant under this prefix) |
| `max_units_per_market` | **1** |
| No-pyramid invariant | True (pyramid spacing 0.5N vestigial, never fires) |
| AMB6 filter | NONE (structurally locked) |
| Donchian entry channel | 55 |
| Donchian exit channel | 20 |
| Wilder ATR period | 20 |
| Stop multiplier | 2N (locked at entry, no trailing) |
| Per-unit risk | 1.0% portfolio equity |
| Universe | NQ.c.0, GC.c.0, ZN.c.0, CL.c.0 (4 markets; no cherry-pick; no substitution) |
| Data source at runtime | Databento GLBX.MDP3 **local cache only** (s7-D1 P5 cache re-used) |
| Fresh data fetch authorized | **No** |
| In-sample window | 2013-01-01 -> 2022-12-30 UTC |
| OOS window | 2023-01-01 -> 2025-12-30 UTC (**noted but not inspected**) |
| Portfolio cap | 4 markets x 1 unit = 4 units max (structurally non-binding) |
| Portfolio cap uses | unit count, not contract count (s6 bugfix preserved) |
| Cost-stress matrix tiers | S0, S1, S2, S3, S4 (locked) |
| Cost-stress decision rules | DR2, DR3, DR4, DR5 (locked; loosening forbidden) |
| Entry/exit timing | ONO (open-on-next-bar) |
| N source | Wilder ATR(20) of entry market at trigger bar (not fill bar) |
| Starting cash | $100,000 MNQ-equivalent |

---

## Single delta from s7-D1

| Field | s7-D1 | s8-D1 |
|---|---|---|
| `max_units_per_market` | **4** | **1** |
| All other locked parameters | (s7-D1 Tier-N seal `72602305...`) | (preserved byte-equivalent) |

Delta count: **1**.

---

## s7-D1 non-revival attestation

- s7-D1 chain status: **PERMANENTLY_PARKED_AT_COMMIT_f08220a**
- s7-D1 revived by this plan-lock: **False**
- s7-D1 used as: **UPSTREAM EVIDENCE AND MECHANICAL BASELINE ONLY**
- All 14 s7-D1 sealed artifacts byte-stable at authorship
- S-STOP-12 monitors s7-D1 byte-stability through all s8 work

Other parked/rejected candidates not revived: s7-D5 (YM-only), s8-D5 (ZN-only), B005_001, NKE Options Wheel, s2-Kraken-XRP, s3-MNQ-DRB, s4-Turtle-System-1, s5-baseline, s6-full-system.

---

## Parent chain inheritance evidence

| Parent | sha256 | reason |
|---|---|---|
| `phase2_safety_template_json` | `695a9fb6e0cb6ae5...` | PHASE_2_C1_C8_SAFETY_TEMPLATE_JSON_FOR_FUTURE_PHASE2_PLAN_AUTHORING |
| `phase2_safety_template_md` | `1812f4854a23e7a1...` | PHASE_2_C1_C8_SAFETY_TEMPLATE_MD_FOR_FUTURE_PHASE2_PLAN_AUTHORING |
| `s7_d1_decision_memo` | `5354d3395319e309...` | DECISION_RATIONALE_THAT_LED_TO_S8_DIRECTION |
| `s7_d1_diag_rev2` | `2563ef9309217171...` | OPERATIVE_S7_D1_STRATEGY_RESULT_LOAD_BEARING_EVIDENCE |
| `s7_d1_parking_report` | `551fdce46c0e373e...` | S7_D1_PERMANENTLY_PARKED_NOT_REVIVED_BY_THIS_PLAN_LOCK |
| `s7_d1_patch_build_report` | `2ab3ed5852de0dad...` | PATCHED_DRIVER_MECHANIC_INHERITED_BASELINE_FOR_S8_D1_BUILD |
| `s7_d1_tier_n_spec_for_parameter_parent` | `72602305ef8d6781...` | STRATEGY_PARAMETER_BASELINE_ALL_PRESERVED_EXCEPT_MAX_UNITS_DELTA |
| `s8_d1_spec_md` | `ada2c060a63a9f3b...` | DIRECT_PARENT_HUMAN_READABLE_SPEC_DRAFT |
| `s8_d1_tier_n_spec_json` | `8cff6babf8e4a451...` | DIRECT_PARENT_TIER_N_SPEC_LOCKED_PARAMETERS |
| `s8_selection_plan` | `6b7bdb4c350f4a77...` | SELECTION_PROVENANCE_D1_AT_39_OF_40 |

Drift count at authorship: **0** (all 10 parents byte-stable).

---

## What this plan-lock does NOT authorize

- Code authoring (no runner harness, no execution guard, no driver, no tests)
- Synthetic smoke run; in-sample backtest; in-sample driver invocation
- Databento fetch / API call / Historical client instantiation
- QuantConnect API call or submit
- Network call
- OOS window inspection / OOS data load / OOS metric compute
- Live trading change; paper trading change
- Broker/exchange adapter instantiation (Kraken/Binance/Alpaca)
- `review_queue.json` mutation; obsidian-trade-logger mutation
- Credential or API key print/log
- Strategy Lab promotion; scheduler modification
- spartacus_clone_engine or hydra_video modification
- Any existing artifact mutation
- s7-D1 / s7-D5 / s8-D5 / B005_001 / NKE revival

---

## Future downstream steps (each requires separate explicit operator authorization)

1. **P2** Phase-2 plan-doc authoring (inherits C1-C8 from `docs/phase2_safety_contract_template.{md,json}`)
2. **P3** BUILD ONLY (runner + execution_guard + in_sample_driver + tests scaffold under `external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_runner_harness/`)
3. **P4** T1-T15 synthetic smoke pass
4. **(no P5 fetch needed)** -- s7-D1 P5 cache re-used (480 files, 129,789,451 bytes)
5. **P6** in-sample run at S1 baseline (optionally S0/S2/S3/S4)
6. **P7** in-sample decision memo
7. **P8** lifecycle transition (PARK or OOS-AUTHORIZE)

No step pre-approved by this plan-lock.

---

## Validator items at plan-lock time

- V_PL_1_canonical_record_id_locked
- V_PL_2_naming_prefix_locked_and_unique
- V_PL_3_max_units_per_market_equals_1_invariant
- V_PL_4_no_pyramid_invariant
- V_PL_5_amb6_filter_none_invariant
- V_PL_6_donchian_55_20_invariant
- V_PL_7_wilder_atr_20_2n_stop_invariant
- V_PL_8_1_pct_portfolio_equity_sizing_invariant
- V_PL_9_universe_4_markets_nq_gc_zn_cl_invariant
- V_PL_10_local_databento_cache_reuse_only_no_fresh_fetch
- V_PL_11_in_sample_window_2013_2022_locked
- V_PL_12_oos_window_2023_2025_noted_not_inspected
- V_PL_13_all_future_downstream_require_separate_authorization
- V_PL_14_tier_n_spec_seal_inherited_byte_equivalent
- V_PL_15_selection_plan_seal_inherited_byte_equivalent
- V_PL_16_spec_md_sha_inherited_byte_equivalent
- V_PL_17_no_s7_d1_revival
- V_PL_18_no_d5_revival_neither_s7_nor_s8_d5
- V_PL_19_no_b005_001_revival
- V_PL_20_no_nke_revival
- V_PL_21_seal_roundtrip_recompute_match
- V_PL_22_no_code_authored_this_turn
- V_PL_23_no_runner_harness_directory_created_this_turn
- V_PL_24_no_obsidian_touch_file_count_bytes_invariant
- V_PL_25_no_review_queue_mutation

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
- S_STOP_9_operator_STOP_S8_D1_instruction
- S_STOP_10_spec_sha_shown_in_runner_neq_sealed_tier_n_spec_sha
- S_STOP_11_max_units_per_market_neq_1_detected_anywhere
- S_STOP_12_any_s7_d1_chain_artifact_byte_sha_changes_during_s8_d1_turn

---

## Boundaries held this turn

All True:

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
- `no_scheduler_modification`: True
- `no_spartacus_clone_engine_modification`: True
- `no_strategy_lab_promotion`: True
- `no_synthetic_smoke_run`: True
- `no_test_file_authored`: True

---

## Recommended next step

> **AUTHORIZE S8-D1 P2 phase-2 plan-doc authoring only -- single sealed pair under reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_phase2_plan.{md,json}, inheriting C1-C8 byte-equivalent from docs/phase2_safety_contract_template.{md,json}**

---

*End of s8-D1 P1 plan-lock (SEALED). Plan-lock only - no code, no backtest, no Databento, no QC, no fetch, no live/paper trading, no scheduler change, no obsidian mutation, no review_queue mutation, no D5/B005_001/NKE/s7-D1 revival, no profitability claim.*

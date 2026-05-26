# S10-D2 Reparam-Cap Cross-Asset Donchian No-Pyramid - Tier-N Spec (SEALED)

**Artifact type:** `tier_n_spec`
**Canonical record id:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Spec version:** v1
**Phase:** `TIER_N_SPEC_SEALED_BUILD_NOT_AUTHORIZED`
**Authored UTC:** 2026-05-26T21:32:29Z
**Authored by:** SPARTA_CLAUDE

**Tier-N seal sha256:** `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
**Seal method:** `LESSON_HUNTER_004` canonical roundtrip

> **Labels:** EXTERNAL_CLAIM_ONLY, NEEDS_VERIFICATION, NOT_A_SIGNAL,
> DIAGNOSTIC_ONLY_NOT_LIVE_GRADE, PLAN_AND_SPEC_ONLY, NO_FRC_GRANTED,
> S10_D2_CANDIDATE_TIER_N_SEALED, SINGLE_DELTA_FROM_S8_D1_STARTING_CASH_500K,
> NO_S8_D1_REVIVAL, NO_S7_D1_REVIVAL, NO_D5_REVIVAL, NO_B005_001_REVIVAL, NO_NKE_REVIVAL

---

## Selection source

- S10 selection plan seal: `007110ff5a57dd04b184409bad64fd667374cd049155416c869a73f7af0c1f97`
- S10 availability analysis seal: `417ed6c7b4e177e0681a3fe20a03744cb22c9946b9755e077a3def3afd7f50e7`
- Selection path within S10 plan: **S10-D2 higher-capital full-contract successor**
- S10-D1 blocking reason: MCL.c.0 first non-empty bar 2021-07-19; pure-micro IS window limited to ~17.5 months projecting ~16 portfolio trades vs K9 threshold 100 -> structural INSUFFICIENT_SAMPLE
- S10-D2 promoted to recommendation after S10-D1 micro path blocked by Databento history constraint

---

## Single delta from S8-D1

| Field | S8-D1 | S10-D2 |
|---|---|---|
| `starting_cash_mnq_equivalent` | $100,000 | **$500,000** |
| All other locked parameters | (s8-D1 Tier-N seal `8cff6babf8e4a451...`) | byte-equivalent |
| Delta count | — | **1** |

**Rationale:** $500,000 is a round number above the empirical $476,000 NQ-clearing threshold at OOS median N=238 computed in the s8-D1 P9.5b sizing-skip cascade audit. At $500k starting capital with 1% risk: (a) NQ: floor(5000 / (238 * 20)) = floor(1.05) = 1 contract (clears); (b) GC: floor(5000 / (24 * 100)) = floor(2.08) = 2 contracts (clears); (c) CL: floor(5000 / (1.65 * 1000)) = floor(3.03) = 3 contracts (clears); (d) ZN: floor(5000 / (0.4832 * 1000)) = floor(10.35) = 10 contracts (clears at higher count than s8-D1).

**Mechanical effect:** All other s8-D1 strategy logic byte-equivalent; only the per-trigger sizing cleared. Donchian-55 triggers fire on the same days as s8-D1; entry/exit/stop/no-pyramid logic preserved. Expected IS trade count >= 111 (some s8-D1 IS triggers that were skipped due to contracts<1 will now fire). Expected OOS trade count will dramatically exceed s8-D1 OOS 15 trades because all 4 markets now clear.

---

## Locked parameters (excerpt)

| Parameter | Value |
|---|---|
| Family | trend_following_donchian |
| Base recipe | FAITH_DONCHIAN_SYSTEM_1_NO_PYRAMID |
| Entry channel length | 55 |
| Exit channel length | 20 |
| Stop multiplier | 2.0N |
| Wilder ATR period | 20 |
| max_units_per_market | **1** (s8-D1 invariant preserved) |
| Pyramid spacing (vestigial) | 0.5N (never fires under max_units=1) |
| Per-unit risk | 1.0% portfolio equity |
| Entry timing | ONO |
| Filter | NONE (AMB6 structurally locked) |
| Universe | NQ.c.0 + GC.c.0 + ZN.c.0 + CL.c.0 (4 markets; s8-D1 universe preserved) |
| **Starting cash (DELTA)** | **$500,000** (vs s8-D1 $100k) |
| Portfolio cap | 4 markets × 1 unit = 4 units (s6 bugfix preserved) |
| In-sample window | 2013-01-01 → 2022-12-30 |
| OOS window | 2023-01-01 → 2025-12-30 (no inspection in-sample) |

---

## Data requirements (existing s8-D1 cache reused; no fetch)

- IS cache: **480 files / 129,790,451 bytes** (existing s8-D1 IS)
- OOS cache: **144 files / 42,663,855 bytes** (existing s8-D1 P8.5 OOS)
- Combined: **624 files / 172,454,306 bytes**
- Source: Databento GLBX.MDP3 (continuous, ohlcv-1m)
- Decode: `db.DBNStore.from_file()` (no `db.Historical` at runtime)
- **No fresh fetch required for S10-D2**

---

## Acceptance gates (inherited from s8-D1; all must pass)

A1-A10 byte-equivalent to s8-D1 Tier-N. Sample-size A1: closed_trades >= 100 expected to clear comfortably given $500k starting capital permits more triggers to actually fire (vs s8-D1 IS 111 trades baseline).

## Rejection gates (inherited from s8-D1; threshold-lock invariant)

K1-K12 byte-equivalent to s8-D1 Tier-N. Loosening post-seal forbidden; tightening requires fresh `_revN_` spec under fresh candidate_record_id.

## C7 verdict (closed enum preserved)

Allowed verdicts: **FAIL_SAFETY / INSUFFICIENT_SAMPLE / READY_FOR_LONGER_BACKTEST**

---

## S8-D1 revival attestation

- S8-D1 chain status: **PERMANENTLY_PARKED_AT_COMMIT_6e7b491**
- S8-D1 final operational status: `PARKED_SAFE_BUT_NOT_MONEY_PROVEN_OOS_SIZING_UNDERSIZED`
- S8-D1 revived by this spec: **False**
- S8-D1 used as: UPSTREAM_EVIDENCE_AND_PARAMETER_BASELINE_ONLY
- S8-D1 chain artifacts: 20 (all byte-stable at authorship)
- S-STOP-12 monitors s8-D1 byte-stability through all s10-D2 work

---

## Fresh candidate record id attestation

- `candidate_record_id`: s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl
- `is_fresh`: True
- `namespace_prefix_locked`: s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_
- `no_other_s10_variant_writes_under_this_prefix`: True
- `parallel_session_s9_rsi_2_namespace_collision_check`: no_collision (parallel track is s9-rsi-2 mean-reversion; this candidate is s10-cross-asset-donchian-no-pyramid-reparam-cap; distinct namespaces)
- `s10_d1_micro_path_NOT_authored_as_candidate`: True
- `s10_d1_status`: deferred_due_to_databento_micro_history_constraint_per_S10_availability_analysis

---

## Inherited seal registry (13 parents, all byte-stable at authorship)

| Inherited | sha256 | path |
|---|---|---|
| `S10_availability_analysis` | `417ed6c7b4e177e0...` | `reports/external_research_hunter/s10_micro_futures_availability_attestation_analysis.json` |
| `S10_selection_plan` | `007110ff5a57dd04...` | `reports/external_research_hunter/s10_micro_futures_successor_selection_plan.json` |
| `S7_D1_PARKING` | `551fdce46c0e373e...` | `reports/external_research_hunter/s7_d1_cross_asset_donchian_PARKING_REPORT.json` |
| `S8_D1_P10_decision` | `a493931f0b812fad...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_oos_decision_memo.json` |
| `S8_D1_P11_lifecycle` | `c79b06206c51d9b9...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_p11_lifecycle_decision.json` |
| `S8_D1_P6_in_sample` | `07a3fa91509f2206...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_in_sample_diagnostic_result_sealed.json` |
| `S8_D1_P9_5b_sizing` | `957ede055785faf0...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_p9_5b_sizing_skip_cascade_audit_sealed.json` |
| `S8_D1_phase2_plan` | `5e6fccd1aeb40db7...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_phase2_plan.json` |
| `S8_D1_plan_lock` | `612abbbda7235c8c...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_plan_lock.json` |
| `S8_D1_tier_n_spec` | `8cff6babf8e4a451...` | `reports/external_research_hunter/s8_d1_cross_asset_donchian_no_pyramid_tier_n_spec.json` |
| `S8_selection_plan` | `6b7bdb4c350f4a77...` | `reports/external_research_hunter/s8_next_candidate_selection_after_six_parks.json` |
| `phase2_safety_template_json` | `695a9fb6e0cb6ae5...` | `docs/phase2_safety_contract_template.json` |
| `phase2_safety_template_md` | `1812f4854a23e7a1...` | `docs/phase2_safety_contract_template.md` |

Drift count at authorship: **0**.

---

## Boundaries held by this Tier-N spec

- `no_b005_001_revival`: True
- `no_backtest`: True
- `no_code_authored_this_turn`: True
- `no_credential_logged`: True
- `no_d5_revival_neither_s7_ym_only_nor_s8_zn_only`: True
- `no_data_fetch`: True
- `no_databento_call`: True
- `no_databento_key_printed`: True
- `no_frc_granted`: True
- `no_live_trading_change`: True
- `no_network_call`: True
- `no_nke_revival`: True
- `no_obsidian_trade_logger_mutation`: True
- `no_oos_inspection`: True
- `no_paper_trading_change`: True
- `no_profitability_claim`: True
- `no_qc_call`: True
- `no_review_queue_mutation`: True
- `no_run`: True
- `no_s7_d1_revival`: True
- `no_s8_d1_revival`: True
- `no_s9_rsi2_namespace_collision`: True
- `no_scheduler_change`: True
- `no_strategy_lab_promotion`: True

---

## Next step (each requires separate explicit operator authorization)

- P1_plan_lock_authoring
- P2_phase2_plan_authoring
- P3_build_only_runner_execution_guard_tests_scaffold_under_s10_d2_namespace
- P4_t1_t15_synthetic_smoke
- no_P5_fetch_needed_existing_s8_d1_cache_reuse
- P6_in_sample_run_S1_baseline_optional_S0_S2_S3_S4
- P7_in_sample_decision_memo
- P7_5_K10_in_sample_correlation_compute
- P8_lifecycle_transition_OOS_deliberation_plan
- no_P8_5_OOS_fetch_needed_existing_s8_d1_P8_5_OOS_cache_reuse
- P9_OOS_S1_run
- P9_5_OOS_cost_stress_optional
- P10_OOS_decision_memo
- P11_lifecycle_decision_final

- No step pre-approved by this spec: **True**

---

*End of S10-D2 Tier-N spec. Sealed at `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`. PLAN/SPEC-ONLY. No code, no BUILD, no smoke, no backtest, no fetch.*

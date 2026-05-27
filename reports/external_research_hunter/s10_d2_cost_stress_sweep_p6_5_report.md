# S10-D2 P6.5 Cost-Stress Sweep Report (SEALED -- HALT)

**Schema:** `sparta.s10.d2.cost_stress_sweep_p6_5_report.v1`
**Phase:** `S10_D2_P6_5_COST_STRESS_SWEEP`
**Phase prefix:** `PHASE2-S10-D2-XAD-RC-P6.5`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T02:19:55Z`

## Outcome: **`S10_D2_P6_5_COST_STRESS_SWEEP_HALTED`**

**Severity:** `FAIL_CLOSED_BY_DESIGN_NOT_A_BUG`

**Candidate record id:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Tier-N spec seal:** `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
**Previous P6 IS diagnostic commit:** `d6977631c9ca8d851a357117794a183c3bf785fd`

> P6.5 sweep HALT. No cache modification. No driver modification.
> No OOS inspection. No Databento call. No DATABENTO_API_KEY access.
> No live trading. verdict_never_means_live_ready: True.

---

## 1. Halt root cause

Between the parallel session's prior P6 IS diagnostic run (commit d6977631c9ca8d851a357117794a183c3bf785fd; sealed S1 single-tier) and this controller session's P6.5 cost-stress sweep attempt, the local Databento cache directory has accumulated to its combined IS+OOS footprint (624 files / 172.4M bytes). The in_sample_driver.assert_cache_complete() hard check is configured to expect the IS-only-cache footprint (480 files / 129.8M bytes per the s8_d1_is_cache_attestation Tier-N pin). When the observed footprint exceeds the IS-only pin, the driver raises CACHE_INCOMPLETE because it cannot guarantee OOS-isolation if the cache directory may contain OOS bars alongside IS bars.

- **category:** `ooS_data_present_in_combined_cache_blocks_is_only_driver`
- **severity:** `FAIL_CLOSED_BY_DESIGN_NOT_A_BUG`
- **is_logic_error:** False
- **is_authentication_error:** False
- **is_authorization_error:** False
- **is_schema_or_data_validation_error:** False
- **is_data_corruption:** False
- **is_correct_fail_closed_protection:** **True**
- **operator_halt_per_authorization_clause:** *If parallel-session changes appear during execution, halt and report rather than silently merging scopes.*

## 2. Cache arithmetic (the math holds; cache is in the expected combined state)

### Observed cache footprint at HALT time

| Market | files (observed) | bytes (observed) |
|---|---|---|
| NQ | 156 | 72,918,723 |
| GC | 156 | 2,703,019 |
| ZN | 156 | 36,512,504 |
| CL | 156 | 60,320,060 |
| **TOTAL** | **624** | **172,454,306** |

### Driver-expected IS-only footprint

| Market | files (expected) | bytes (expected) |
|---|---|---|
| NQ | 120 | 53,148,359 |
| GC | 120 | 2,162,216 |
| ZN | 120 | 27,939,222 |
| CL | 120 | 46,540,654 |
| **TOTAL** | **480** | **129,790,451** |

### Tier-N spec pinned cache attestations

| Pin | file_count | total_bytes |
|---|---|---|
| `s8_d1_is_cache` (IS only) | 480 | 129,790,451 |
| `s8_d1_oos_cache` (OOS only) | 144 | 42,663,855 |
| **`combined_cache` (IS+OOS)** | **624** | **172,454,306** |

### Math check

- observed_total_files matches tier_n_combined_files: **True**
- observed_total_bytes matches tier_n_combined_bytes: **True**
- delta (observed - IS-only) equals OOS cache size: **True**

The observed cache footprint (624 files / 172.4M bytes) exactly matches the Tier-N spec's `combined_cache_attestation`. The cache contains both IS bars (480 files / 129.8M bytes) AND OOS bars (144 files / 42.7M bytes), co-located in the same cache directory. The IS-only driver's `assert_cache_complete()` hard check expects IS-only file counts and bytes (matching the IS-only-cache attestation, NOT the combined one). The driver correctly fail-closes when the cache footprint is larger than the IS-only pin, to prevent any possibility of accidentally reading OOS bars during an IS-only run. The cache is NOT corrupted; it is in the spec-expected combined state.

## 3. Fetch attempts (all halted; no tier executed)

| # | tier | outcome | error_class | tier_executed |
|---|---|---|---|---|
| 1 | S0 | `HALTED_BY_DRIVER_CACHE_ASSERTION` | `RuntimeError` | False |
| 2 | S1 | `HALTED_BY_DRIVER_CACHE_ASSERTION` | `RuntimeError` | False |
| 3 | S2 | `HALTED_BY_DRIVER_CACHE_ASSERTION` | `RuntimeError` | False |
| 4 | S3 | `HALTED_BY_DRIVER_CACHE_ASSERTION` | `RuntimeError` | False |

**Error summary (uniform across all 4 attempts):**

> CACHE_INCOMPLETE: per-market expected 120 files / IS-only-pinned bytes, observed 156 files / combined IS+OOS-sized bytes per market. Driver fail-closes by design to protect OOS isolation.

## 4. What this means for the candidate verdict

- DR2 / DR3 / DR5 evaluation: **NOT EVALUATED** (per-tier results unavailable)
- K12 evaluation: **NOT EVALUATED** (requires S0/S1/S2/S3 net PnL)
- K10 evaluation: **STILL NOT EVALUATED** (separate gap; was open before this turn)
- S10-D2 verdict at S1 single-tier (sealed at P6 commit `d6977631`) remains **PRELIMINARY**
- The P6.5 cost-stress dimension remains **OPEN**

## 5. Possible next steps (each requires separate authorization)

### `separate_oos_files_from_is_cache_directory` (priority 1)

Move (do not delete) the 144 OOS .dbn.zst files from the current cache root into a sibling OOS-only cache directory (e.g., data/databento_cache_oos/). After the move, the IS cache footprint matches the driver's IS-only-pin (480 files / 129.8M bytes), and the IS-only driver can run. This is a directory-restructuring operation, not a data fetch or data modification. Requires separate operator authorization.
- requires_separate_authorization: **True**
- operator_safety_review_needed: **True**

### `modify_driver_assertion_to_accept_superset_of_is_only_pin` (priority 3)

Modify in_sample_driver.assert_cache_complete() to accept the IS-only files as a SUBSET of a larger cache directory (verify each IS file is present and matches the expected byte count; allow OOS files alongside them). The current assertion is strict equality. The change would be a code modification subject to its own sealed plan-and-build, AND requires Tier-N spec revision (a `_revN_` spec) because the strict-equality OOS-isolation guarantee is a security boundary, not a usability one. Higher risk than option 1.
- requires_separate_authorization: **True**
- operator_safety_review_needed: **True**

### `investigate_origin_of_oos_files_in_cache` (priority 2)

Before any other action, surface to the operator: when and why did the OOS cache files appear in the same directory as the IS cache? Was this a deliberate parallel-session prep for a future OOS-inspection turn, or an inadvertent co-location? The Tier-N spec section 7 specifies that OOS data shall not be inspected at IS phase; storing it locally for a future authorized OOS turn is permissible only if it does not enable accidental IS-time reads. The driver's fail-closed today says it does enable that risk.
- requires_separate_authorization: **True**

### `halt_and_wait_for_operator_direction` (DEFAULT)

Default: do not modify cache, do not modify driver, do not retry the sweep. Wait for operator direction on whether to restructure the cache (option 1), revise the driver/spec (option 2), or accept the candidate as PRELIMINARY at S1 single-tier and pursue different research.
- requires_separate_authorization: **False**

## 6. Negative invariants (all True)

- `no_backtest_run_completed`: **True**
- `no_branch_change`: **True**
- `no_brokerage_connection`: **True**
- `no_cache_file_creation`: **True**
- `no_cache_file_deletion`: **True**
- `no_cache_file_movement_or_renaming`: **True**
- `no_cache_modification`: **True**
- `no_candidate_promoted`: **True**
- `no_data_fetch`: **True**
- `no_databento_api_key_access`: **True**
- `no_databento_call`: **True**
- `no_driver_modification`: **True**
- `no_git_push`: **True**
- `no_idea_memory_mutation`: **True**
- `no_key_leakage`: **True**
- `no_lessons_md_staged_or_modified`: **True**
- `no_live_trading`: **True**
- `no_oos_computation`: **True**
- `no_oos_inspection`: **True**
- `no_oos_value_inspected_beyond_file_count_attestation`: **True**
- `no_orb_artifact_modified`: **True**
- `no_paper_order_placed`: **True**
- `no_partial_matrix_report_on_disk_before_this_writer`: **True**
- `no_partial_per_tier_results_on_disk`: **True**
- `no_per_tier_diagnostic_emitted`: **True**
- `no_per_tier_payload_returned`: **True**
- `no_phase2_plan_modification`: **True**
- `no_plan_lock_modification`: **True**
- `no_real_order_placed`: **True**
- `no_review_queue_mutation`: **True**
- `no_runner_harness_modification`: **True**
- `no_s10_d1_artifact_modified`: **True**
- `no_s10_d2_p6_is_diagnostic_committed_artifact_modification`: **True**
- `no_s10_d2_runner_build_report_modification`: **True**
- `no_s10_d2_smoke_battery_report_modification`: **True**
- `no_s10_d2_tests_scaffold_report_modification`: **True**
- `no_s4_tier_run`: **True**
- `no_s7_artifact_modified`: **True**
- `no_s8_d1_artifact_modified`: **True**
- `no_s9_artifact_modified`: **True**
- `no_signal_computation`: **True**
- `no_simulator_run_completed`: **True**
- `no_step_30_cost_constant_modified`: **True**
- `no_strategy_code_modification`: **True**
- `no_strategy_lab_invoked`: **True**
- `no_third_attempt_after_double_fail_closed`: **True**
- `no_tier_n_spec_modification`: **True**

## 7. Status

- Trading status: `PAUSED`
- Live status: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

## 8. Labels

- `S10_D2_P6_5_COST_STRESS_SWEEP_HALTED`
- `DRIVER_FAIL_CLOSED_AT_CACHE_ASSERTION_BY_DESIGN`
- `CACHE_FOOTPRINT_MATCHES_TIER_N_COMBINED_IS_PLUS_OOS_ATTESTATION`
- `OOS_FILES_CO_LOCATED_IN_IS_CACHE_DIRECTORY`
- `NO_CACHE_MODIFICATION`
- `NO_DRIVER_MODIFICATION`
- `NO_OOS_INSPECTION`
- `NO_DATABENTO_CALL`
- `NO_DATABENTO_API_KEY_ACCESS`
- `NO_TIER_RUN_TO_COMPLETION`
- `NO_K12_EVALUATION_AVAILABLE_THIS_TURN`
- `AWAITING_OPERATOR_DIRECTION`

## 9. Seal verification

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**P6.5 cost-stress sweep HALT-sealed. K12 cannot be evaluated this turn. Awaiting operator direction. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**


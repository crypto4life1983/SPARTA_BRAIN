# S10-D2 Cache Directory Restructure Report (SEALED)

**Schema:** `sparta.s10.d2.cache_directory_restructure_report.v1`
**Phase:** `S10_D2_CACHE_DIRECTORY_RESTRUCTURE`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T02:28:27+00:00Z`

## Outcome: **`S10_D2_CACHE_RESTRUCTURE_COMPLETE`**

**Candidate record id:** `s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl`
**Tier-N spec seal:** `f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679`
**Previous P6.5 HALT commit:** `e89236f918b3ce7c70e87397488fb083dd38e24e`

> Cache restructuring only. No Databento call. No DATABENTO_API_KEY
> access. No data fetch. No signal computation. No simulator. No backtest.
> No OOS inspection (beyond filename-date classification needed for the move).
> No file content read, copied, modified, or deleted.

---

## 1. Paths

- **Old combined cache path:** `data/databento_cache/` (was IS+OOS together)
- **New IS-only cache path:** `data/databento_cache/` (same path; driver's CACHE_ROOT pin)
- **New OOS-only cache path:** `data/databento_cache_oos/` (new sibling)

The driver hard-codes CACHE_ROOT = data/databento_cache, so the IS-only post-move dir REUSES the original path (driver pin satisfied without code change). The 144 OOS month-directories are renamed into a NEW sibling dir at data/databento_cache_oos/ via shutil.move (filesystem rename; same drive; atomic; bytes invariant).

## 2. Tier-N pins vs post-state

| Pin | file_count | total_bytes | post_state files | post_state bytes | match |
|---|---|---|---|---|---|
| s8_d1_is_cache_attestation | 480 | 129,790,451 | 480 | 129,790,451 | True |
| s8_d1_oos_cache_attestation | 144 | 42,663,855 | 144 | 42,663,855 | True |
| combined_cache_attestation | 624 | 172,454,306 | 624 | 172,454,306 | True |

## 3. Per-market attestation

| Market | pre total | pre IS | pre OOS | post IS dir | post OOS dir | IS bytes (post) |
|---|---|---|---|---|---|---|
| NQ | 156 | 120 | 36 | 120 | 36 | 53,148,359 |
| GC | 156 | 120 | 36 | 120 | 36 | 2,162,216 |
| ZN | 156 | 120 | 36 | 120 | 36 | 27,939,222 |
| CL | 156 | 120 | 36 | 120 | 36 | 46,540,654 |

## 4. sha256 preservation attestation (per-file)

- `files_checked_pre_vs_post`: **624**
- `sha_mismatches`: **0**
- `bytes_mismatches`: **0**
- `every_pre_file_sha256_equals_post_file_sha256`: **True**
- `every_pre_file_bytes_equals_post_file_bytes`: **True**
- `no_file_content_modification`: **True**
- `method`: **shutil.move on whole YYYY-MM month-directories (filesystem rename; bytes invariant)**

## 5. Move log summary

- **Total month-directories moved:** 144
- **Method:** shutil.move (whole month-directory rename; same drive)

**Per-market moved count:**
- NQ: 36
- GC: 36
- ZN: 36
- CL: 36

**Sample moves (first 3 per market):**

| Market | Month | Source | Destination |
|---|---|---|---|
| NQ | 2023-01 | `data/databento_cache/NQ/2023-01` | `data/databento_cache_oos/NQ/2023-01` |
| NQ | 2023-02 | `data/databento_cache/NQ/2023-02` | `data/databento_cache_oos/NQ/2023-02` |
| NQ | 2023-03 | `data/databento_cache/NQ/2023-03` | `data/databento_cache_oos/NQ/2023-03` |
| GC | 2023-01 | `data/databento_cache/GC/2023-01` | `data/databento_cache_oos/GC/2023-01` |
| GC | 2023-02 | `data/databento_cache/GC/2023-02` | `data/databento_cache_oos/GC/2023-02` |
| GC | 2023-03 | `data/databento_cache/GC/2023-03` | `data/databento_cache_oos/GC/2023-03` |
| ZN | 2023-01 | `data/databento_cache/ZN/2023-01` | `data/databento_cache_oos/ZN/2023-01` |
| ZN | 2023-02 | `data/databento_cache/ZN/2023-02` | `data/databento_cache_oos/ZN/2023-02` |
| ZN | 2023-03 | `data/databento_cache/ZN/2023-03` | `data/databento_cache_oos/ZN/2023-03` |
| CL | 2023-01 | `data/databento_cache/CL/2023-01` | `data/databento_cache_oos/CL/2023-01` |
| CL | 2023-02 | `data/databento_cache/CL/2023-02` | `data/databento_cache_oos/CL/2023-02` |
| CL | 2023-03 | `data/databento_cache/CL/2023-03` | `data/databento_cache_oos/CL/2023-03` |

## 6. Classification method

- `rule`: **month-directory name (YYYY-MM); month <= '2022-12' is IS; month >= '2023-01' is OOS**
- `no_file_content_read`: **True**
- `no_oos_value_inspected`: **True**
- `ambiguous_classifications_count`: **0**

## 7. Driver dry-run (assert_cache_complete; no run_in_sample invocation)

- **dry-run at UTC:** `2026-05-27T02:28:27+00:00Z`
- **pass:** **True**
- **note:** Dry-run of in_sample_driver.assert_cache_complete() only; run_in_sample() NOT invoked.

**Observed by driver:**
- `NQ`: `{'exists': True, 'file_count': 120, 'bytes': 53148359}`
- `GC`: `{'exists': True, 'file_count': 120, 'bytes': 2162216}`
- `ZN`: `{'exists': True, 'file_count': 120, 'bytes': 27939222}`
- `CL`: `{'exists': True, 'file_count': 120, 'bytes': 46540654}`

## 8. Negative invariants (all True)

- `no_backtest_run`: **True**
- `no_branch_change`: **True**
- `no_brokerage_connection`: **True**
- `no_candidate_promoted`: **True**
- `no_data_fetch`: **True**
- `no_databento_api_key_access`: **True**
- `no_databento_call`: **True**
- `no_file_content_modification`: **True**
- `no_file_created_or_copied`: **True**
- `no_file_deleted`: **True**
- `no_git_push`: **True**
- `no_idea_memory_mutation`: **True**
- `no_in_sample_driver_code_modification`: **True**
- `no_key_leakage`: **True**
- `no_lessons_md_staged_or_modified`: **True**
- `no_live_trading`: **True**
- `no_oos_computation`: **True**
- `no_oos_inspection_beyond_filename_date_classification`: **True**
- `no_orb_artifact_modified`: **True**
- `no_paper_order_placed`: **True**
- `no_phase2_plan_modification`: **True**
- `no_plan_lock_modification`: **True**
- `no_real_order_placed`: **True**
- `no_review_queue_mutation`: **True**
- `no_runner_harness_code_modification`: **True**
- `no_s10_d1_artifact_modified`: **True**
- `no_s10_d2_p6_5_halt_report_modification`: **True**
- `no_s10_d2_p6_is_diagnostic_committed_artifact_modification`: **True**
- `no_s7_artifact_modified`: **True**
- `no_s8_d1_artifact_modified`: **True**
- `no_s9_artifact_modified`: **True**
- `no_signal_computed`: **True**
- `no_simulator_run`: **True**
- `no_step_30_cost_constant_modified`: **True**
- `no_strategy_lab_invoked`: **True**
- `no_tier_n_spec_modification`: **True**

## 9. Status

- Trading status: `PAUSED`
- Live status: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

## 10. Labels

- `S10_D2_CACHE_RESTRUCTURE_COMPLETE`
- `IS_CACHE_480_FILES_CONFIRMED`
- `OOS_CACHE_144_FILES_CONFIRMED`
- `COMBINED_CACHE_624_FILES_PRESERVED`
- `NO_FILE_CONTENT_MODIFICATION`
- `ALL_PER_FILE_SHA256_PRESERVED`
- `DRIVER_ASSERT_CACHE_COMPLETE_NOW_PASSES`
- `NO_DATABENTO_CALL`
- `NO_DATABENTO_API_KEY_ACCESS`
- `NO_SIGNAL_COMPUTED`
- `NO_SIMULATOR_RUN`
- `NO_BACKTEST`
- `NO_OOS_COMPUTATION`
- `NO_LIVE_TRADING`

## 11. Seal verification

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**Cache restructure sealed. Driver assert_cache_complete now PASSES. P6.5 cost-stress sweep can be re-authorized. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**


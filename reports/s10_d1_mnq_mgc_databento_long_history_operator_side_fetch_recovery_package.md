# S10-D1 MNQ+MGC -- Operator-Side Databento Fetch Recovery Package (SEALED)

**Schema:** `sparta.s10.d1.mnq_mgc.operator_side_fetch_recovery_package.v1`
**Phase:** `S10_D1_OPERATOR_SIDE_FETCH_RECOVERY_PACKAGE`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T01:15:58Z`

**Candidate record id:** `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`
**Sealed-spec commit anchor:** `90404293a5f17ab4a0ab4b57085f9ca9a76c5df5`

> Recovery-package preparation only. No controller-side Databento
> call. No controller-side DATABENTO_API_KEY access. No data fetch
> this turn. No signal. No simulator. No backtest. No live trading.

---

## 1. Reason for recovery path

Controller-side Databento fetch HALTED at commit 7d71d185 after two consecutive transient network failures (ConnectionResetError 10054 mid-stream, then ReadTimeout at 100s). Spec, data, and key are not implicated; root cause is network-level instability on the controller's egress path to hist.databento.com. The operator-side fetch tool already committed at a8df18b1 is designed for operator-shell execution with the API key in the operator's local environment, where network conditions may differ favorably.

- **Previous HALT cause:** transient_network_failure (NOT a logic error, NOT an authentication error, NOT an authorization error, NOT a schema or data validation error)
- **Previous HALT commit:** `7d71d18500cc4a21bf670f9018f10e11d77e3872`
- **Previous HALT report:** `reports/s10_d1_mnq_mgc_databento_long_history_step_02b_data_ingest_report.json`
- **No key leakage in previous HALT confirmed:** **True**
  - Evidence: Prior HALT report (commit 7d71d185) attests 8 key-safety booleans all true; no print/log/file-write/traceback of the key value.

## 2. Operator-side tool attestation

- **Path:** `tools/operator_side/s10_d1_mnq_mgc_step02b_fetch_databento.py`
- **Commit anchor:** `a8df18b110023f08e147137df565522426d074db`
- **sha256:** `9269a778c501bc9c45c11760a38610665d9c3008dfa3b64a2c9e5316f110683b`
- **bytes:** 12,414

### Safety scan
- `targets_only_s10_d1_symbols`: **True**
- `symbols_in_tool`: **['MNQ.c.0', 'MGC.c.0']**
- `symbols_NOT_in_tool`: **['MCL.c.0', 'ZN.c.0', 'CL.c.0', 'NQ.c.0 (as standalone)', 'GC.c.0 (as standalone)']**
- `uses_GLBX_MDP3_dataset`: **True**
- `uses_ohlcv_1d_schema`: **True**
- `uses_continuous_stype_in`: **True**
- `uses_2019_05_13_start_date`: **True**
- `uses_2025_12_30_end_date`: **True**
- `reads_DATABENTO_API_KEY_from_environment_only`: **True**
- `no_key_print_pattern_found`: **True**
- `no_key_write_to_file_pattern_found`: **True**
- `no_key_in_json_dump_pattern_found`: **True**
- `no_key_in_logger_pattern_found`: **True**
- `safe_for_operator_side_execution`: **True**

### Tool output filenames (BAT will rename to canonical)
- `MNQ.c.0`: `MNQ_c_0_ohlcv_1d_20190513_20251230.csv`
- `MGC.c.0`: `MGC_c_0_ohlcv_1d_20190513_20251230.csv`
- Tool manifest: `s10_d1_mnq_mgc_step02b_fetch_manifest.json`
- Tool writes to: `data/s10_d1_mnq_mgc_databento_long_history/raw/`
- Naming-mismatch resolution: The BAT renames the tool's CSV outputs to the canonical operator-authorized filenames after the fetch completes successfully (using Windows `move /Y`). The tool's manifest is left at its original filename (s10_d1_mnq_mgc_step02b_fetch_manifest.json) and treated as auxiliary; a future controller turn will create the canonical fetch_run_manifest.json by reference after CSVs are validated.

## 3. Operator package files (outside the repo; intentionally not staged)

| File | Path | sha256 (first 16) | bytes |
|---|---|---|---|
| bat | `C:\Users\mahmo\Downloads\s10_d1_mnq_mgc_databento_fetch\run_s10_d1_fetch.bat` | `09579cbc948d540f` | 3,739 |
| readme | `C:\Users\mahmo\Downloads\s10_d1_mnq_mgc_databento_fetch\README_OPERATOR_STEPS.txt` | `4648dd4d0ed29a7f` | 4,077 |

Both files are intentionally outside the repo. The BAT is operator-side
ephemera tied to the operator's local environment. The README is a
step-by-step text guide. Neither is staged in git; they can be regenerated
at any time from this recovery-package report under a separately authorized
turn.

## 4. Canonical expected CSV destinations (inside the repo)

- **Directory:** `data/s10_d1_mnq_mgc_databento_long_history/raw/`
- `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_1d_2019-05-13_2025-12-30.csv`
- `data/s10_d1_mnq_mgc_databento_long_history/raw/MGC_1d_2019-05-13_2025-12-30.csv`

**Canonical CSVs already present at time of package:** False

Not present at time of package; package proceeds. If they had been present, the BAT would still have run the tool and the rename step would have overwritten via `move /Y`. The recovery package report would have recommended a separately authorized paste-back/validation-by-reference turn instead of a fresh fetch.

## 5. Operator upload-back checklist

1. Run the BAT (one click) on a network where MNQ+MGC daily streaming completes within ~3 minutes.
2. Verify the BAT shows [OK] for both canonical CSV paths and [OK] for the tool manifest.
3. Upload to chat: the canonical MNQ_1d_2019-05-13_2025-12-30.csv file.
4. Upload to chat: the canonical MGC_1d_2019-05-13_2025-12-30.csv file.
5. Upload to chat: the s10_d1_mnq_mgc_step02b_fetch_manifest.json tool manifest.
6. Optional: paste the BAT's stdout block (no key value visible) for additional audit context.
7. Re-authorize a separately scoped 'paste-back / validation-by-reference sealing' turn after upload.
8. Do NOT paste the API key value into chat or anywhere else.

## 6. Negative invariants (all True)

- `no_CLAUDE_md_modified`: **True**
- `no_RUNBOOK_modified`: **True**
- `no_backtest_run`: **True**
- `no_branch_change`: **True**
- `no_brokerage_connection`: **True**
- `no_candidate_promoted`: **True**
- `no_controller_side_databento_api_key_access`: **True**
- `no_controller_side_databento_call`: **True**
- `no_data_fetch_this_turn`: **True**
- `no_docs_decisions_md_modified`: **True**
- `no_git_push`: **True**
- `no_gitignore_modified`: **True**
- `no_idea_memory_mutation`: **True**
- `no_key_leakage`: **True**
- `no_key_leakage_in_previous_halt_confirmed`: **True**
- `no_key_leakage_in_previous_halt_evidence`: **Prior HALT report (commit 7d71d185) attests 8 key-safety booleans all true; no print/log/file-write/traceback of the key value.**
- `no_lessons_md_staged_or_modified`: **True**
- `no_live_trading`: **True**
- `no_operator_side_BAT_or_README_staged_in_git_index`: **True**
- `no_orb_artifact_modified`: **True**
- `no_paper_order_placed`: **True**
- `no_pipeline_manifest_modified`: **True**
- `no_real_order_placed`: **True**
- `no_review_queue_mutation`: **True**
- `no_s10_d1_spec_modified`: **True**
- `no_s10_d2_spec_modified`: **True**
- `no_s7_artifact_modified`: **True**
- `no_s9_artifact_modified`: **True**
- `no_signal_computed`: **True**
- `no_simulator_run`: **True**
- `no_step_30_cost_constant_modified`: **True**
- `no_strategy_lab_invoked`: **True**
- `no_third_controller_side_fetch_attempt`: **True**

## 7. Status

- Trading status: `PAUSED`
- Live status: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

## 8. Labels

- `S10_D1_OPERATOR_SIDE_FETCH_RECOVERY_PACKAGE_COMPLETE`
- `ONE_CLICK_OPERATOR_RUNNER_READY`
- `NO_CONTROLLER_DATABENTO_CALL`
- `NO_CONTROLLER_DATABENTO_API_KEY_ACCESS`
- `NO_DATA_FETCH_THIS_TURN`
- `NO_KEY_LEAKAGE`
- `NO_SIGNAL_COMPUTED`
- `NO_SIMULATOR_RUN`
- `NO_BACKTEST`
- `NO_REVIEW_QUEUE_MUTATION`
- `NO_STRATEGY_LAB_PROMOTION`
- `NO_LIVE_TRADING`
- `BAT_AND_README_INTENTIONALLY_OUTSIDE_REPO`

## 9. Seal verification

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**Recovery package sealed. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**


# s10 D1 MNQ+MGC Databento Long-History -- Step 02b Data Ingest Report (SEALED -- HALT)

**Schema:** `sparta.s10.d1.mnq_mgc.step_02b_data_ingest_report.v1`
**Phase:** `S10_D1_STEP_02B_DATA_INGEST`
**Controller session:** THIS_SESSION_ONLY
**Sealed at (UTC):** `2026-05-27T00:54:06Z`

## Fetch outcome: **`HALT`**

**Reason:** Two consecutive transient network failures before any CSV row was written

**Candidate record id:** `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`
**Sealed-spec commit anchor:** `90404293a5f17ab4a0ab4b57085f9ca9a76c5df5`

> No CSVs written. No strategy code. No simulator. No backtest.
> No signal. No OOS inspection. No review_queue mutation. No
> Strategy Lab. No live trading. No key leakage.

---

## 1. Halt root cause

- **category:** `transient_network_failure`
- **description:** Two consecutive controller-side streaming fetch attempts against Databento Historical API hist.databento.com both failed with transient network-level errors before any CSV row was materialized to disk. The first attempt aborted mid-stream with a ConnectionResetError; the second timed out at the default 100s read timeout. Both failures were observed only on the MNQ.c.0 symbol; the MGC.c.0 fetch was never attempted because the script fails closed on the first symbol failure.
- **is_logic_error:** **False**
- **is_authentication_error:** **False**
- **is_authorization_error:** **False**
- **is_schema_or_data_validation_error:** **False**
- **operator_halt_per_authorization:** **True**
- **operator_authorization_text:** *If Databento fetch fails, HALT and report.*

## 2. Fetch attempts (2; both failed transient network)

### Attempt 1 -- `FAILED_TRANSIENT_NETWORK`
- symbol: `MNQ.c.0`
- dataset/schema/stype_in: `GLBX.MDP3` / `ohlcv-1d` / `continuous`
- start_passed_to_databento: `2019-05-13`
- end_passed_to_databento: `2025-12-31`
- error_class: `BentoError wrapping urllib3.exceptions.ProtocolError ConnectionResetError`
- error_summary: *ConnectionResetError(10054, 'An existing connection was forcibly closed by the remote host'); transient mid-stream failure*
- side_warning_observed_before_failure: *BentoWarning: streaming request contained reduced-quality days (2020-02-27 degraded, 2020-02-28 degraded, 2020-06-30 degraded, and possibly more). Warning is informational about source quality, not the cause of the failure.*
- partial_csv_written: **False**

### Attempt 2 -- `FAILED_TRANSIENT_NETWORK`
- symbol: `MNQ.c.0`
- dataset/schema/stype_in: `GLBX.MDP3` / `ohlcv-1d` / `continuous`
- start_passed_to_databento: `2019-05-13`
- end_passed_to_databento: `2025-12-31`
- error_class: `requests.exceptions.ReadTimeout (HTTPSConnectionPool hist.databento.com)`
- error_summary: *Read timed out at 100 seconds (default databento client read_timeout)*
- partial_csv_written: **False**

## 3. Files written by this HALT turn

| Path | sha256 (first 16) | bytes |
|---|---|---|
| `data/s10_d1_mnq_mgc_databento_long_history/raw/fetch_run_manifest.json` | `f2affab9158bdf93` | 2,632 |

**Plus the two sealed report files (.json + .md) written below.**

## 4. CSVs attempted (0 of 2 written)

| Symbol | CSV written | Authorized output path |
|---|---|---|
| MNQ.c.0 | False | `data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_1d_2019-05-13_2025-12-30.csv` |
| MGC.c.0 | False | `data/s10_d1_mnq_mgc_databento_long_history/raw/MGC_1d_2019-05-13_2025-12-30.csv` |

## 5. Databento call attestation

- databento_call_made: **True**
- databento_call_completed_successfully: **False**
- dataset: `GLBX.MDP3`
- schema: `ohlcv-1d`
- stype_in: `continuous`
- sdk_version: `0.75.0`

## 6. API key safety attestation (boolean only; value never exposed)

- `databento_api_key_present`: **True**
- `databento_api_key_source`: **env DATABENTO_API_KEY**
- `databento_api_key_logged`: **False**
- `databento_api_key_written_to_any_file`: **False**
- `databento_api_key_echoed`: **False**
- `databento_api_key_held_in_local_variable_only_during_attempts`: **True**
- `databento_api_key_passed_only_as_databento_client_kwarg`: **True**

## 7. Possible next steps (documented; each requires separate authorization)

### 1. `operator_directed_retry`

Operator may re-authorize the same fetch turn at a later time when network conditions are more favorable.
- requires_separate_authorization: **True**

### 2. `controller_side_chunked_fetch`

Fetch in smaller date windows (e.g., year-by-year or quarter-by-quarter) and concatenate. Smaller requests are less likely to hit read timeouts. Would require a separately authorized turn with a revised tooling design that may or may not match the operator's previous fetch path.
- requires_separate_authorization: **True**

### 3. `operator_side_fetch_via_existing_tool`

The parallel-session fetch tool at tools/operator_side/s10_d1_mnq_mgc_step02b_fetch_databento.py (committed at a8df18b110023f08e147137df565522426d074db) is designed to be operator-side run with the API key in the operator's local environment. Operator can run that tool in their own shell, then place the resulting CSVs in the approved output directory, and this controller-session can later seal a Step 02b ingest report by reference without making any Databento call.
- requires_separate_authorization: **True**

### 4. `switch_to_s10_d2`

S10-D2 reuses the existing s8-D1 cache (no new Databento fetch required for D2's 4-symbol full-futures universe at $500K start). Operator may pivot to D2 if D1 fetch infrastructure proves unreliable on this client.
- requires_separate_authorization: **True**

### 5. `halt_and_review_only` (DEFAULT)

Stop here, do not retry, do not pivot. Wait for operator direction. This is the default if no other action is authorized.
- requires_separate_authorization: **False**

## 8. Data integrity status at HALT

- `no_partial_csv_on_disk`: **True**
- `no_partial_manifest_on_disk_before_this_writer`: **True**
- `no_in_memory_payload_logged_or_persisted`: **True**
- `approved_output_dir_exists_only_with_manifest`: **True**

## 9. Negative invariants (all True)

- `no_CLAUDE_md_modified`: **True**
- `no_RUNBOOK_modified`: **True**
- `no_backtest_run`: **True**
- `no_branch_change`: **True**
- `no_brokerage_connection`: **True**
- `no_candidate_promoted`: **True**
- `no_docs_decisions_md_modified`: **True**
- `no_git_push`: **True**
- `no_gitignore_modified`: **True**
- `no_idea_memory_mutation`: **True**
- `no_key_leakage_via_print_log_file_or_traceback`: **True**
- `no_lessons_md_staged_or_modified`: **True**
- `no_live_trading`: **True**
- `no_oos_inspection_by_this_phase`: **True**
- `no_orb_artifact_modified`: **True**
- `no_order_creation`: **True**
- `no_paper_order_placed`: **True**
- `no_partial_data_persisted_to_disk`: **True**
- `no_pipeline_manifest_modified`: **True**
- `no_real_order_placed`: **True**
- `no_review_queue_mutation`: **True**
- `no_runner_built`: **True**
- `no_s10_d1_spec_modified`: **True**
- `no_s10_d2_data_fetched`: **True**
- `no_s10_d2_spec_modified`: **True**
- `no_s7_artifact_modified`: **True**
- `no_s9_artifact_modified`: **True**
- `no_signal_computation`: **True**
- `no_simulator_run`: **True**
- `no_step_30_cost_constant_modified`: **True**
- `no_strategy_code_modified`: **True**
- `no_strategy_lab_invoked`: **True**
- `no_third_retry_attempted`: **True**

## 10. Status

- Trading status: `PAUSED`
- Live status: `BLOCKED_AT_6_GATES`
- FRC granted: `False`
- Advisory label permanent: `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE`

## 11. Labels

- `S10_D1_STEP_02B_DATA_INGEST_HALTED`
- `NO_KEY_LEAKAGE`
- `NO_SIGNAL_COMPUTED`
- `NO_SIMULATOR_RUN`
- `NO_BACKTEST`
- `NO_LIVE_TRADING`
- `TRANSIENT_NETWORK_FAILURE_ROOT_CAUSE`
- `AWAITING_OPERATOR_DIRECTION`

## 12. Seal verification

```
seal_method = sha256 over json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False) EXCLUDING report_seal_sha256 + seal_method

report_seal_sha256 = <see JSON report_seal_sha256 field>
```

**Step 02b data ingest HALT-sealed. Awaiting operator direction. Trading: PAUSED. Live: BLOCKED_AT_6_GATES. FRC never granted.**


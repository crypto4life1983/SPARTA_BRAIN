# s7 D1 Cross-Asset Donchian - Step 02c Raw-Data Audit Plan

Status: PLAN_ONLY (audit not yet authorized; execution requires a separately authorized turn).
Authored: 2026-05-25
Parent spec: docs/s7_d1_cross_asset_donchian_spec.md
Parent fetch plan: docs/s7_d1_cross_asset_donchian_step_02b_alt_vendor_data_fetch_plan.md (sha256 2f2eb19827e9122c7b8443b4bfc432668ea4ef189282e6dd458f63d038edbc8c, committed at efdc30753449c8b5ed2d7da22682662c78cf11b9)
Parent fetch execution report: reports/s7_d1_cross_asset_donchian_step_02b_yfinance_fetch_execution_report.json (sha256 3a5f440a1dffac8b..., seal 6328bae3ddf67e0045d2aac42b6abcac8948372d19e5f042f0a9d63e1db46c50)
Parent cleanup report: reports/s7_d1_cross_asset_donchian_step_02b_cleanup_report.json (sha256 4f70a4806143c217..., seal 9adc4aaab68eb005ca5e0ff68f2fdf1b90a19f3fd51b1a025b1a7f6e6cbe70bb)
Naming convention: s7 D1 cross-asset Donchian (matches existing repo work; inherits the Step 02b plan's reconciled naming).

HARD BOUNDARIES (held by this plan). Plan only. No code change. No CSV read by claude during plan authoring. No fetch_run_manifest.json modification. No CSV modification. No yfinance import. No Yahoo Finance network call. No Databento call. No DATABENTO_API_KEY access. No Donchian signal computation. No Wilder ATR computation. No 55-bar channel computation. No 20-bar channel computation. No simulator run. No backtest. No paper-trade loop. No live trading. No ORB branch artifact mutation. No Step 30 cost constant mutation. No source code modification. No tests modification. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No branch change. No branch creation. No commit beyond the single new plan file. No git push. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted. No profitability claim.

----

## 1. Purpose

Define an independent claude-side raw-data audit of the four canonical daily-bar CSVs that Step 02b deposited at data/s7_d1_cross_asset_donchian/raw/. The audit re-reads each CSV byte-stream from disk, recomputes each R-rule and V-gate against the actual file content, and adds deeper raw-data integrity checks that the Step 02b plan did not enumerate (OHLCV sanity invariants, business-day contiguity, cross-CSV trading-day alignment, adj-vs-unadj divergence summary statistics, duplicate-date scan, monotonic-date check). The audit produces a sealed audit report and a sealed audit manifest. The audit performs no signal computation, no channel computation, no backtest, no simulator step.

## 2. Why Step 02c comes after Step 02b

Step 02b's V1-V10 and R1-R8 attestations in fetch_run_manifest.json and the paste-back validation report were derived from an operator-side local-Python fetch followed by a byte-identical copy from C:/Users/mahmo/Downloads/s7_d1_donchian_yfinance_fetch/ into data/s7_d1_cross_asset_donchian/raw/. Claude did not run yfinance itself this round and did not observe vendor-side stdout for fields such as yfinance_version. Several manifest entries are recorded as PASS (operator-side; not directly observed by claude this turn). Before any downstream artifact (canonical loader, Donchian input validator, simulator harness) consumes those CSVs, the canonical-path bytes deserve an independent claude-side audit that does not depend on operator-side claims. Step 02c is that audit. It is a pre-loader, pre-signal verification step.

## 3. Inputs from Step 02b

The audit reads only files already present on disk. The audit does not network-fetch, does not re-fetch, does not call yfinance, does not call Databento.

Locked input set:

- data/s7_d1_cross_asset_donchian/raw/SPY_1d_2014-01-01_2026-05-25.csv (expected sha256 bad97abba52836949e4ce1ffeba2002d308286c991091c6c073283ab1e2f91eb, expected 3116 rows, expected first_date 2014-01-02, expected last_date 2026-05-22).
- data/s7_d1_cross_asset_donchian/raw/TLT_1d_2014-01-01_2026-05-25.csv (expected sha256 2cab9fc3d2e26c62a08c4af64bf57d46350b3062219bf5cb7373883d04676570, expected 3116 rows, expected first_date 2014-01-02, expected last_date 2026-05-22).
- data/s7_d1_cross_asset_donchian/raw/GLD_1d_2014-01-01_2026-05-25.csv (expected sha256 7ff41cda6214d0739c2143dda4b98624f4e0365db499d7cee0ff0fa37ce811b0, expected 3116 rows, expected first_date 2014-01-02, expected last_date 2026-05-22).
- data/s7_d1_cross_asset_donchian/raw/USO_1d_2014-01-01_2026-05-25.csv (expected sha256 0b5b5b9472e5bdf59cbd04a3794a95bfa5e87efc9baf7837e1fca7de08530b37, expected 3116 rows, expected first_date 2014-01-02, expected last_date 2026-05-22).
- data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json (expected sha256 8fe210138dedcbaa07882b704cc3c3e30ba2ca4a1d4db7f05ca4dc782005a8f7).
- reports/s7_d1_cross_asset_donchian_step_02b_yfinance_fetch_execution_report.json (seal 6328bae3ddf67e0045d2aac42b6abcac8948372d19e5f042f0a9d63e1db46c50; used only as the comparison anchor for expected csv_sha256, expected row counts, expected date ranges).

The audit may also read the parent fetch plan and parent spec for cross-reference, but must not modify either.

## 4. Outputs the audit turn will create later

The execution turn for Step 02c shall write the following sealed artifacts and no others:

- reports/s7_d1_cross_asset_donchian_step_02c_raw_data_audit_report.json (sealed; canonical Python-side seal scheme matching prior s7 D1 reports).
- reports/s7_d1_cross_asset_donchian_step_02c_raw_data_audit_report.md (companion human-readable form; sha256 recorded in JSON).
- data/s7_d1_cross_asset_donchian/raw/audit_manifest.json (separate from fetch_run_manifest.json; this file shall not modify or replace the existing fetch_run_manifest.json).

No CSV shall be overwritten. No fetch_run_manifest.json field shall be edited. No new CSV shall be created at the storage path. No supplementary log files at the storage path. The audit turn shall not write any other files anywhere.

## 5. Files the audit turn may create or modify later

Permitted writes by the execution turn (subject to its own separate authorization):

- The three audit output files listed in section 4.
- A temporary audit script under scripts/ (suggested name: scripts/_s7_d1_donchian_step_02c_raw_data_audit.py) that the execution turn may write, run once, and then delete on success. The script shall be limited to read-only access to the input set in section 3 plus write-access to the three output files in section 4.
- A temporary sealing helper under scripts/ (suggested name: scripts/_step_02c_audit_report_seal.py) that the execution turn may write, run once, and delete on success.

The temp scripts shall be byte-deleted on success. Failure cases shall leave the temp script in place pending a separately authorized cleanup turn (mirroring the Step 02b cleanup-authorization pattern).

## 6. Files the audit turn must not modify

This list is exhaustive for the categories enumerated; any file not listed here is also not permitted unless it is in section 5.

- The four canonical CSVs at data/s7_d1_cross_asset_donchian/raw/*.csv must not be modified, renamed, moved, truncated, re-saved, or re-encoded.
- data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json must not be modified.
- reports/s7_d1_cross_asset_donchian_step_02b_*.json and reports/s7_d1_cross_asset_donchian_step_02b_*.md must not be modified.
- docs/s7_d1_cross_asset_donchian_spec.md must not be modified.
- docs/s7_d1_cross_asset_donchian_step_02b_alt_vendor_data_fetch_plan.md must not be modified.
- This Step 02c plan file must not be modified by the execution turn (the execution turn quotes it, attests against it; it does not edit it).
- CLAUDE.md must not be modified.
- docs/decisions.md must not be modified.
- RUNBOOK (if present) must not be modified.
- pipeline_manifest (if present) must not be modified.
- .gitignore must not be modified.
- All ORB branch artifacts must not be modified.
- All Step 30 cost constants must not be modified.
- review_queue.json, idea_memory directory, and Strategy Lab artifacts must not be modified.
- obsidian-trade-logger configuration must not be modified.

## 7. Raw CSV integrity checks (audit turn requirements)

The audit turn shall perform the following checks against actual CSV bytes on disk and record the pass/fail outcome per symbol in the audit report:

A1. File existence at the exact canonical path.
A2. File sha256 matches the value pinned in section 3.
A3. File size in bytes is recorded and matches the value at first sealing time (recorded in this plan only by reference; the execution turn shall record the on-disk byte count and compare to the value the operator's paste-back validation recorded).
A4. UTF-8 decodes without error.
A5. Line terminator is LF (newline-only), not CRLF, matching the operator-side fetch.py write-bytes path.
A6. The header row equals exactly: date,open,high,low,close,adj_close,volume (no trailing whitespace, no quotes).
A7. Column count per data row is exactly 7, with no extra trailing commas and no missing fields.
A8. Row count equals exactly 3116 (the value pinned in section 3 per symbol).
A9. The date column parses as YYYY-MM-DD strings, all 10 characters wide, no time-of-day suffix, no timezone suffix.
A10. The date column is strictly monotonically increasing (no duplicates, no out-of-order rows).
A11. The first_date equals 2014-01-02 and the last_date equals 2026-05-22 (the operator-side values).
A12. The open, high, low, close, adj_close columns parse as finite positive floats; volume parses as a finite non-negative integer or non-negative float.
A13. Per-row OHLCV sanity invariants: high >= max(open, close), low <= min(open, close), high >= low, all five price fields > 0, volume >= 0.
A14. No NaN, no Inf, no -Inf, no scientific-notation overflow string in any numeric field.

## 8. Manifest consistency checks (audit turn requirements)

The audit turn shall load fetch_run_manifest.json and verify:

M1. The manifest's storage_path equals exactly data/s7_d1_cross_asset_donchian/raw/.
M2. The manifest's symbols_requested equals exactly ["SPY","TLT","GLD","USO"] in that order.
M3. The manifest's start_date equals 2014-01-01 and end_date equals 2026-05-25.
M4. The manifest's frequency equals "1d".
M5. The manifest's per_symbol object has exactly four keys, one per symbol.
M6. Each per_symbol entry's csv_sha256 matches the actual file's sha256 (cross-check with A2).
M7. Each per_symbol entry's rows matches the actual file's row count (cross-check with A8).
M8. Each per_symbol entry's first_date matches the actual first date (cross-check with A11).
M9. Each per_symbol entry's last_date matches the actual last date (cross-check with A11).
M10. The manifest's api_key_safety_confirmation, donchian_isolation_confirmation, and no_orb_mutation_confirmation blocks are present and well-formed.
M11. The manifest contains no field whose value is a raw secret, an API key string, or an os.environ snapshot dump.
M12. The manifest's sha256 on disk equals 8fe210138dedcbaa07882b704cc3c3e30ba2ca4a1d4db7f05ca4dc782005a8f7 (pinned at Step 02b paste-back validation).

A discrepancy between any M-check and any A-check is a HALT (section 11).

## 9. Date-range and row-count checks (audit turn requirements)

The audit turn shall perform the following window checks:

D1. Per-symbol date span from first_date to last_date covers at least 10.0 calendar years and at most 13.5 calendar years (the operator's recorded value is 12.3833 years; the band allows for floating tolerance only and is not a permission to extend).
D2. The set of unique trading-day dates per symbol must equal exactly 3116 dates.
D3. The four symbols must share the same set of trading-day dates (full cross-symbol intersection equals each per-symbol set, no asymmetric missing days). If they do not, the audit reports the symmetric differences as a HALT signal and writes the differential set to the audit report (no auto-repair).
D4. The trading-day count gap to the NYSE business-day calendar within the same window shall be reported. The audit shall not interpolate, fill, forward-fill, or backfill any missing date. Missing-date counts shall be reported as a diagnostic, with a documented expectation band (NYSE has roughly 252 sessions per year; 3116 sessions over 12.3833 years is approximately 251.6 sessions per year, well within tolerance).
D5. The first business day on or after start_date 2014-01-01 is 2014-01-02; the audit shall record that the observed first_date 2014-01-02 matches that expectation.
D6. The last business day on or before end_date 2026-05-25 in the operator's vendor-returned range was 2026-05-22 (Friday); the audit shall record this and check that the observed last_date matches.
D7. No date in any CSV shall lie outside the inclusive band [2014-01-01, 2026-05-25]. The audit shall HALT on any out-of-band date.

## 10. Adjusted-close handling rules (audit turn requirements)

The audit turn shall examine close vs adj_close per symbol and produce summary statistics in the audit report:

J1. Per-symbol max(|close - adj_close|), the value the manifest already records as adjusted_vs_unadjusted_max_divergence.
J2. Per-symbol mean(|close - adj_close|), median(|close - adj_close|), and the count of rows where close != adj_close.
J3. Cross-symbol observation: the manifest recorded GLD and USO with max divergence 0.000000, SPY with 0.187731, TLT with 0.287879. The audit shall confirm these to within floating-point tolerance and record any disagreement as a HALT signal.
J4. The audit shall NOT auto-adjust close to adj_close. The audit shall NOT alter either column. The audit shall NOT pick one over the other for downstream consumption; that selection is a separate Step 03 design decision and is explicitly out of scope here.
J5. The audit shall record an attestation that the audit performed no Donchian channel construction on either close series and no other signal computation.

## 11. HALT conditions (audit turn requirements)

The audit turn shall HALT on any of:

- A1 file missing.
- A2 sha256 mismatch.
- A4 UTF-8 decode error.
- A5 line-terminator mismatch (CRLF found).
- A6 header row mismatch.
- A7 wrong column count on any row.
- A8 row count mismatch.
- A9 date format mismatch.
- A10 duplicate or out-of-order dates.
- A11 first_date or last_date mismatch.
- A12 non-positive price, non-finite price, or negative volume.
- A13 OHLCV sanity invariant violation on any row.
- A14 NaN, Inf, or -Inf in any numeric field.
- Any M-check disagreement with A-checks.
- M12 manifest sha256 mismatch.
- D3 cross-symbol date set mismatch.
- D7 out-of-band date.
- J3 divergence statistic mismatch beyond floating-point tolerance.
- Any attempt to write outside the section 4 output set.
- Any attempt to call Databento.
- Any attempt to access DATABENTO_API_KEY or os.environ DATABENTO_API_KEY.
- Any attempt to mutate an ORB branch artifact.
- Any attempt to compute a Donchian signal or run a simulator or backtest.
- Any attempt to substitute vendor.
- Any branch change or branch creation.
- Any commit beyond the audit-report commit (and only if a separate authorization permits a commit).

A HALT keeps partial audit artifacts in place and surfaces the failure verbatim. A separately authorized recovery turn is required to proceed.

## 12. Validation gates (audit turn requirements)

The audit-report self-validation shall verify in order:

VA1. The three output files in section 4 exist at their exact paths.
VA2. The audit report JSON has the required schema (sparta.donchian.step_02c_raw_data_audit_report.v1).
VA3. The audit report JSON contains an A-check block with all 14 A-checks per symbol.
VA4. The audit report JSON contains an M-check block with all 12 M-checks.
VA5. The audit report JSON contains a D-check block with all 7 D-checks.
VA6. The audit report JSON contains a J-check block with all 5 J-checks.
VA7. The audit report JSON contains a boundaries_held block listing every hard boundary from this plan as True.
VA8. The audit report JSON contains a negative_invariants block listing live_trading, databento_called, databento_api_key_accessed, donchian_signal_computed, simulator_run, backtest_run, orb_branch_mutated, csv_modified, manifest_modified, plan_modified, branch_changed, commit_made_beyond_audit, git_pushed as False.
VA9. The audit report JSON contains the canonical seal_method line and a report_seal_sha256 value.
VA10. The audit report MD companion's sha256 is recorded in the audit report JSON, and vice versa.

A VA-gate failure is a HALT (section 11).

## 13. No-signal / no-backtest boundary

The audit turn shall not compute a Donchian channel of any length. The audit turn shall not compute a Wilder ATR of any length. The audit turn shall not compute any rolling statistic that resembles a trading signal. The audit turn shall not run a simulator. The audit turn shall not run a backtest. The audit turn shall not generate any entry, exit, stop, or pyramid decision. The audit turn shall not write any signals.csv, trades.csv, or fills.csv. The audit turn shall not write to any directory other than the section 4 output set and the section 5 temp-script paths.

This boundary applies to any helper code the audit turn writes. A helper that contains a Donchian channel computation, Wilder ATR computation, simulator step, or backtest loop is itself out of scope and shall not be authored under this plan.

## 14. ORB isolation boundary

The audit turn shall not read any ORB branch artifact for the purpose of mutating it. The audit turn shall not modify any ORB Step 30 cost constant. The audit turn shall not modify any orb_* file, any branch_orb_* file, or any branch_orb_* report. The audit turn shall not touch app.py, hydra_video/, sparta_commander/, spartacus/, strategy_lab/, or any production module unless the file is explicitly part of the section 4 output set or the section 5 temp-script set.

## 15. Databento / API-key prohibition

The audit turn shall not call Databento. The audit turn shall not access DATABENTO_API_KEY. The audit turn shall not read os.environ["DATABENTO_API_KEY"]. The literal substring "DATABENTO_API_KEY" shall not appear in any audit script except as a forbidden-token comment. The audit turn shall not read any environment variable that begins with DATABENTO_. The audit turn shall not network-call any vendor. The audit turn shall not run yfinance. The audit turn shall not run a refetch. The audit turn shall not call Yahoo Finance.

The api_key_safety_confirmation block in the audit report shall attest:

- databento_called: false
- databento_api_key_accessed: false
- os_environ_DATABENTO_API_KEY_referenced: false
- yfinance_called_during_audit: false
- yahoo_finance_called_during_audit: false
- any_network_call_during_audit: false

## 16. Audit-script safety guardrails (operational rules for the execution turn)

The execution turn shall enforce in its own script the following operational rules:

- The script shall open each CSV in read mode only. No write mode against CSVs.
- The script shall not call pandas.DataFrame.to_csv against the canonical paths.
- The script shall not call shutil.copy / shutil.move / os.rename / os.remove against any file inside data/s7_d1_cross_asset_donchian/raw/ except for creating the new audit_manifest.json once (and not touching the existing fetch_run_manifest.json).
- The script shall not import yfinance.
- The script shall not import databento.
- The script shall not import requests, urllib, http.client, socket, or curl_cffi for the purpose of network IO; if any are imported transitively by a stdlib helper, no .get / .post / .request / .Session call shall be made.
- The script shall set no environment variable that begins with DATABENTO_.
- The script shall not disable SSL verification.
- The script shall log its full check list to stdout for the execution turn's report writer to capture.
- The script shall self-delete on success (mirroring the Step 02b cleanup pattern with a separately authorized cleanup turn for the failure case).

## 17. Audit report schema (sparta.donchian.step_02c_raw_data_audit_report.v1)

Required top-level fields in the JSON:

- schema: "sparta.donchian.step_02c_raw_data_audit_report.v1".
- phase: "S7_D1_DONCHIAN_STEP_02C_RAW_DATA_AUDIT".
- controller_session: "THIS_SESSION_ONLY".
- report_date_utc: ISO 8601 timestamp.
- plan_anchor: object with path, sha256, commit (this plan's commit).
- step_02b_anchor: object with manifest_sha256, paste_back_report_seal.
- per_symbol_a_checks: object keyed by symbol; each value contains A1..A14 outcomes.
- m_checks: object containing M1..M12 outcomes.
- d_checks: object containing D1..D7 outcomes.
- per_symbol_j_checks: object keyed by symbol; each value contains J1..J5 outcomes.
- va_gate_results: object containing VA1..VA10 outcomes.
- boundaries_held: object with one True flag per hard boundary in this plan.
- negative_invariants: object with one False flag per negative invariant (section 12 VA8).
- api_key_safety_confirmation: object with the six fields enumerated in section 15.
- audit_manifest_anchor: object with path, sha256.
- companion_md_sha256: string.
- seal_method: canonical string matching prior s7 D1 reports.
- report_seal_sha256: string.

The schema explicitly omits any field that could expose a secret. The schema explicitly forbids fields containing raw os.environ contents.

## 18. Audit manifest schema (data/s7_d1_cross_asset_donchian/raw/audit_manifest.json)

Required top-level fields:

- schema: "sparta.donchian.step_02c_audit_manifest.v1".
- audit_run_started_utc.
- audit_run_finished_utc.
- per_symbol: object keyed by symbol; each value contains observed_sha256, observed_rows, observed_first_date, observed_last_date, observed_byte_count, observed_close_min, observed_close_max, observed_adj_close_max_divergence.
- cross_symbol_date_set_aligned: boolean.
- fetch_manifest_sha256_observed: the actual on-disk sha256 of fetch_run_manifest.json.
- fetch_manifest_sha256_expected: 8fe210138dedcbaa07882b704cc3c3e30ba2ca4a1d4db7f05ca4dc782005a8f7.
- fetch_manifest_sha256_match: boolean.
- audit_isolation_attestation: object with no_csv_modification, no_fetch_manifest_modification, no_donchian_signal_computed, no_simulator_run, no_backtest_run, no_orb_branch_mutated, no_network_call, no_databento_call, no_databento_api_key_accessed, no_yfinance_call, no_yahoo_finance_call, no_certificate_verification_bypass, no_branch_change, no_commit_beyond_audit_report - all True.

## 19. Execution acceptance checklist (for the future execution turn)

Before the execution turn is acceptable to issue:

- A separate operator authorization explicitly authorizes execution of this plan.
- The plan path is exactly docs/s7_d1_cross_asset_donchian_step_02c_next_phase_plan.md.
- The four CSVs and fetch_run_manifest.json at data/s7_d1_cross_asset_donchian/raw/ are present and byte-unchanged since Step 02b paste-back validation.
- The output paths in section 4 are confirmed MISSING via L_FILE_SAFETY pre-state capture before any write.
- No co-active Databento path.
- No co-active backtest path.
- The execution turn writes only the three output files in section 4, plus the optional temp scripts in section 5 (each deleted on success).
- The execution turn's report contains a faithful list of every A-check, M-check, D-check, J-check, and VA-gate outcome per symbol.
- The execution turn refuses to fold any signal computation into the audit on any pretext.

## 20. What execution is NOT allowed to do

The execution turn shall NOT:

- Compute a Donchian channel of any length on any CSV.
- Compute a Wilder ATR of any length on any CSV.
- Compute any rolling statistic that resembles a trading signal.
- Run a backtest, simulator, or paper-trade loop.
- Make any live order, paper-trade, or broker call.
- Modify any of the four canonical CSVs.
- Modify the existing fetch_run_manifest.json.
- Modify any Step 02b report.
- Modify any spec, plan, or prior Step 02 artifact.
- Modify ORB branch artifacts.
- Modify Step 30 cost constants.
- Modify source code beyond the optional temp audit script in section 5.
- Modify CLAUDE.md, docs/decisions.md, RUNBOOK, pipeline_manifest, or .gitignore.
- Switch branches or create branches.
- Call yfinance, Yahoo Finance, or any network resource.
- Call Databento or any vendor.
- Access DATABENTO_API_KEY or any environment variable starting with DATABENTO_.
- Disable SSL certificate verification.
- Use the instruction phrase "compute Donchian signal now" as an active directive (this phrase appears here only as forbidden text).
- Treat the phrase "authorize Step 02c execution" as a completed or current action (this phrase appears here only to mark a future-state authorization gate).
- Treat the next downstream phase (Step 03 loader, Step 03 input validator, or any signal phase) as pre-authorized.

## 21. Next authorization required for execution

A future operator authorization is required to proceed beyond this plan. That authorization shall reference this plan by exact path. This plan is the source of truth for the audit; the execution turn is not pre-authorized by the plan itself.

Future expected status on the audit execution turn (informational; not granted here):

STEP_02C_RAW_DATA_AUDIT_EXECUTED
AUDIT_REPORT_SEALED
AUDIT_MANIFEST_WRITTEN
NO_CSV_MODIFIED
NO_FETCH_RUN_MANIFEST_MODIFIED
NO_DONCHIAN_SIGNAL_COMPUTED
NO_SIMULATOR_RUN
NO_BACKTEST
NO_DATA_FETCH
NO_NETWORK_CALL
NO_DATABENTO_CALL
NO_DATABENTO_API_KEY_ACCESS
NO_ORB_BRANCH_MUTATION
NO_LIVE_TRADING

Downstream-phase reminder (informational; not authorized by this plan):

- Step 03 (canonical loader specification and implementation) shall be specified in its own plan after Step 02c completes successfully. Step 03 shall not be pre-specified by this Step 02c plan.
- Donchian input validation, signal computation, simulator construction, and backtesting are all downstream of Step 03 and require their own plans, their own authorizations, and their own sealed artifacts. None of them are implied as automatic by Step 02c.

----

End of plan. Plan-authoring turn only. No CSV reading. No audit performed. No code execution. No Databento. No yfinance. No network beyond what this plan describes for the future execution turn. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.

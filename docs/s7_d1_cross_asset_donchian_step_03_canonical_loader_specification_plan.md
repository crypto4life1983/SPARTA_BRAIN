# s7 D1 Cross-Asset Donchian - Step 03 Canonical Loader Specification Plan

Status: PLAN_ONLY (build not yet authorized; execution requires a separately authorized turn).
Authored: 2026-05-25
Parent spec: docs/s7_d1_cross_asset_donchian_spec.md
Parent Step 02b plan: docs/s7_d1_cross_asset_donchian_step_02b_alt_vendor_data_fetch_plan.md (sha256 2f2eb19827e9122c7b8443b4bfc432668ea4ef189282e6dd458f63d038edbc8c, commit efdc30753449c8b5ed2d7da22682662c78cf11b9)
Parent Step 02c plan: docs/s7_d1_cross_asset_donchian_step_02c_next_phase_plan.md (sha256 c7dfd00784bbcb9bd8217ac88f4e5b440698e690dd67824f529403259140e5db, commit faebd583955cf13f8acece99da59fce6e95295fe)
Step 02c audit (verdict PASS): reports/s7_d1_cross_asset_donchian_step_02c_raw_data_audit_report.json (sha256 a17c90032fdab504c9da540a44cce37bed8f9bfaf983c625f9c1dbdfebf6d354, seal 872b8275a57e859017e85abb837966b64ad1c0860df413ec010109c407c1b14f, commit 1b640d1520eeec5e42b4eeccd103297abeab89e9)
Step 02c audit manifest: data/s7_d1_cross_asset_donchian/raw/audit_manifest.json (sha256 794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb)
Naming convention: s7 D1 cross-asset Donchian yfinance proxy (alternate-vendor research path; separate from the Databento path's runner_harness subtree referenced in parent spec section 15).

HARD BOUNDARIES (held by this plan). Plan only. No code change. No loader implementation. No test implementation. No build report write. No CSV read by claude during plan authoring beyond what was already loaded by Step 02c. No fetch_run_manifest.json modification. No audit_manifest.json modification. No CSV modification. No Donchian channel computation. No Wilder ATR computation. No 55-bar or 20-bar channel computation. No rolling signal statistic. No simulator run. No backtest. No paper-trade loop. No data fetch. No yfinance import. No Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No network IO. No ORB branch artifact mutation. No Step 30 cost constant mutation. No existing source code modification. No tests modification. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted. No profitability claim.

----

## 1. Purpose

Define the canonical Python loader for the four sealed daily-bar CSVs at data/s7_d1_cross_asset_donchian/raw/ that Step 02b deposited and Step 02c audited (verdict PASS at commit 1b640d1). The loader is a thin, deterministic, read-only adapter that returns the audited CSVs as in-memory Python data structures for downstream consumption by future phases (Donchian input validation, signal computation, simulator, backtest). The loader itself performs none of those downstream operations and contains none of their logic. The loader is the single canonical entry point through which downstream phases read these four CSVs; bypassing the loader to read raw CSV bytes directly in downstream code is forbidden by this plan.

## 2. Why Step 03 comes after Step 02c

Step 02c sealed the raw-data audit (verdict PASS, finding F1 documented). The four CSVs are now provably integrity-checked against the Step 02b fetch outputs: A1..A14 per symbol (file existence, sha256 pin match, UTF-8, LF-only line terminator, locked column header, 7 columns per row, exactly 3116 rows, YYYY-MM-DD date format, strictly monotonic dates, first 2014-01-02, last 2026-05-22, finite positive prices, OHLCV sanity invariants, no NaN/Inf), and the audit_manifest.json is sealed (sha256 794a9386abc68fdf...). With raw-data integrity confirmed, the next phase logically defines HOW that data enters memory for downstream work. A canonical loader is required so that every downstream consumer reads the data the same way, with the same sha256 verification, with the same dtype handling, with the same close vs adj_close handling (per F1), and refuses to load tampered or drifted data. Step 03 is that loader's specification. Step 03 is NOT the loader's implementation; the implementation requires a separately authorized Step 03b build turn.

## 3. Inputs from Step 02c

The loader specification depends only on the sealed Step 02c outputs and the Step 02b sealed inputs. No new data is introduced.

Locked input set:

- data/s7_d1_cross_asset_donchian/raw/SPY_1d_2014-01-01_2026-05-25.csv (sha256 pin bad97abba52836949e4ce1ffeba2002d308286c991091c6c073283ab1e2f91eb, 3116 rows, 2014-01-02 to 2026-05-22).
- data/s7_d1_cross_asset_donchian/raw/TLT_1d_2014-01-01_2026-05-25.csv (sha256 pin 2cab9fc3d2e26c62a08c4af64bf57d46350b3062219bf5cb7373883d04676570, 3116 rows, 2014-01-02 to 2026-05-22).
- data/s7_d1_cross_asset_donchian/raw/GLD_1d_2014-01-01_2026-05-25.csv (sha256 pin 7ff41cda6214d0739c2143dda4b98624f4e0365db499d7cee0ff0fa37ce811b0, 3116 rows, 2014-01-02 to 2026-05-22).
- data/s7_d1_cross_asset_donchian/raw/USO_1d_2014-01-01_2026-05-25.csv (sha256 pin 0b5b5b9472e5bdf59cbd04a3794a95bfa5e87efc9baf7837e1fca7de08530b37, 3116 rows, 2014-01-02 to 2026-05-22).
- data/s7_d1_cross_asset_donchian/raw/audit_manifest.json (sha256 pin 794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb).
- data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json (sha256 pin 8fe210138dedcbaa07882b704cc3c3e30ba2ca4a1d4db7f05ca4dc782005a8f7).

The loader build turn shall read these and only these CSV/manifest files from data/s7_d1_cross_asset_donchian/raw/. No other path.

## 4. Outputs the future build turn will create

The build turn for Step 03 shall create the following artifacts and no others:

- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/loader.py (the loader module).
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/__init__.py (re-exports the public API listed in section 7).
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/README.md (usage docs; pins the spec/audit/manifest sha256s for traceability).
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/test_loader.py (the test suite enumerated in section 18).
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/__init__.py (test package marker; may be empty).
- reports/s7_d1_cross_asset_donchian_step_03_canonical_loader_build_report.json (sealed; canonical Python-side seal scheme matching prior s7 D1 reports).
- reports/s7_d1_cross_asset_donchian_step_03_canonical_loader_build_report.md (companion human-readable form).

No other files. No supplementary modules. No __pycache__ writes intended (those are gitignored by Python tooling anyway). No log files at any path.

## 5. Files the build turn may create or modify later

Permitted writes by the build turn (subject to its own separate authorization):

- The seven output files in section 4.
- A temporary build script under scripts/ (suggested name: scripts/_s7_d1_donchian_step_03_loader_build.py) that the build turn may write, run once, and delete on success.
- A temporary sealing helper under scripts/ (suggested name: scripts/_step_03_loader_build_report_seal.py) that the build turn may write, run once, and delete on success.

The temp scripts shall be byte-deleted on success. Failure cases shall leave them in place pending a separately authorized cleanup turn (mirroring the Step 02b/02c cleanup-authorization pattern).

## 6. Files the build turn must not modify

This list is exhaustive for the categories enumerated; any file not listed here is also not permitted unless it is in section 5.

- The four canonical CSVs at data/s7_d1_cross_asset_donchian/raw/*.csv must not be modified, renamed, moved, truncated, re-saved, or re-encoded.
- data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json must not be modified.
- data/s7_d1_cross_asset_donchian/raw/audit_manifest.json must not be modified.
- reports/s7_d1_cross_asset_donchian_step_02b_*.json and .md must not be modified.
- reports/s7_d1_cross_asset_donchian_step_02c_*.json and .md must not be modified.
- docs/s7_d1_cross_asset_donchian_spec.md must not be modified.
- docs/s7_d1_cross_asset_donchian_step_02b_alt_vendor_data_fetch_plan.md must not be modified.
- docs/s7_d1_cross_asset_donchian_step_02c_next_phase_plan.md must not be modified.
- This Step 03 plan file must not be modified by the build turn (the build turn quotes it, attests against it; does not edit it).
- CLAUDE.md must not be modified.
- docs/decisions.md must not be modified.
- RUNBOOK (if present) must not be modified.
- pipeline_manifest (if present) must not be modified.
- .gitignore must not be modified.
- All ORB branch artifacts must not be modified.
- All Step 30 cost constants must not be modified.
- review_queue.json, the idea_memory directory, and Strategy Lab artifacts must not be modified.
- The Databento-track runner harness path external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/ (if/when it exists) is OUT OF SCOPE for this plan and must not be created, modified, or read by the build turn. The yfinance ETF-proxy loader is a separate alternate-vendor track.

## 7. API surface

The loader module shall expose exactly the following public API and no other public symbols:

- SYMBOLS: a frozenset of strings = frozenset({"SPY", "TLT", "GLD", "USO"}).
- LOCKED_COLS: a tuple of strings = ("date", "open", "high", "low", "close", "adj_close", "volume").
- RAW_DIR: a Path constant = Path("data/s7_d1_cross_asset_donchian/raw").
- AUDIT_MANIFEST_PATH: a Path constant = RAW_DIR / "audit_manifest.json".
- EXPECTED_ROWS: int = 3116.
- EXPECTED_FIRST_DATE: str = "2014-01-02".
- EXPECTED_LAST_DATE: str = "2026-05-22".
- class LoaderError(Exception) - base exception raised by every refusal mode (section 13).
- class LoaderShaMismatchError(LoaderError) - sha256 of disk file diverged from audit_manifest pin.
- class LoaderShapeMismatchError(LoaderError) - row count or column set diverged.
- class LoaderManifestMissingError(LoaderError) - audit_manifest.json missing or malformed.
- class LoaderCrossSymbolAlignmentError(LoaderError) - cross-symbol date sets do not match (load_all path).
- load_symbol(symbol: str) -> LoadedSymbol - return the loaded data for one symbol (see section 8 for the LoadedSymbol structure).
- load_all() -> dict[str, LoadedSymbol] - return all four symbols, additionally verify cross-symbol date alignment.

No other public function. No public mutable state. No module-level data load at import time (the loader must be lazy; importing the module performs no file IO).

## 8. Return-value schema and dtype preservation rules

The loader shall return its data via a dataclass (or equivalent immutable structure) named LoadedSymbol with the following fields:

- symbol: str (one of SYMBOLS).
- dates: tuple[str, ...] (length EXPECTED_ROWS) - dates as YYYY-MM-DD strings, byte-identical to the CSV's date column.
- open: tuple[float, ...] (length EXPECTED_ROWS).
- high: tuple[float, ...] (length EXPECTED_ROWS).
- low: tuple[float, ...] (length EXPECTED_ROWS).
- close: tuple[float, ...] (length EXPECTED_ROWS).
- adj_close: tuple[float, ...] (length EXPECTED_ROWS).
- volume: tuple[int, ...] (length EXPECTED_ROWS) - if the CSV stores volume as a float string (e.g. "12345.0"), the loader rounds to nearest int and verifies the result is non-negative; non-integer fractional values HALT.
- csv_path: str (the path the loader read).
- csv_sha256: str (the sha256 the loader observed on disk; equals the audit_manifest pin or load HALTed).

Dtype preservation rules:

- The loader shall preserve numerical precision as Python floats (IEEE 754 double). No precision loss beyond float parsing. No rounding except for the volume integer normalization noted above.
- The loader shall NOT use a pandas DataFrame in the returned LoadedSymbol structure (to keep dependencies minimal and the loader stdlib-only).
- Downstream phases that prefer pandas may wrap LoadedSymbol into a DataFrame in their own code. The loader does not.
- The loader shall NOT mutate, normalize, or rewrite the CSV bytes during load.
- The loader shall NOT cache results across calls in module-level mutable state. Each call re-reads the CSV bytes from disk. (Process-local caching as a future enhancement requires its own plan; not authorized here.)

## 9. sha256 verification rules

For each load_symbol(sym) call the loader shall:

1. Read audit_manifest.json from AUDIT_MANIFEST_PATH; verify its sha256 equals the pin 794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb; HALT with LoaderManifestMissingError if file is missing, malformed, or mismatched.
2. Read the CSV bytes for the symbol; compute sha256.
3. Compare observed sha256 to audit_manifest's per_symbol[sym].observed_sha256; HALT with LoaderShaMismatchError if mismatched.

For each load_all() call the loader shall perform steps 1-3 for each symbol, then additionally:

4. Verify the cross-symbol date set is identical across all four symbols (frozenset equality); HALT with LoaderCrossSymbolAlignmentError on mismatch.

The loader shall NOT skip sha verification under any flag, environment variable, or argument. There is no skip_verify=True path. There is no force-load fallback.

## 10. Adjusted-close handling per finding F1

Per Step 02c audit finding F1, the manifest's adjusted_vs_unadjusted_max_divergence stores max RELATIVE divergence (not max absolute). The loader shall:

- Preserve close and adj_close as two separate float tuples on the returned LoadedSymbol (loader.adj_close is distinct from loader.close, never overwritten or chosen-by-default).
- NOT auto-pick one over the other. Downstream code that wants total-return semantics shall consume adj_close explicitly; downstream code that wants price-only semantics shall consume close explicitly. The loader makes neither choice.
- NOT compute or apply any adjustment factor. The CSV already contains both columns; the loader returns both.
- NOT modify either column during load (no scaling, no log-transform, no return computation).

## 11. Date handling rules

- Dates in the returned LoadedSymbol shall be YYYY-MM-DD strings (10 characters each), byte-identical to the CSV's date column. The loader shall NOT convert to datetime.date or pandas Timestamp at load time. (Downstream may convert in their own code if needed.)
- The loader shall verify each date string is exactly 10 characters and parses as datetime.date.fromisoformat without raising; HALT otherwise.
- The loader shall verify dates are strictly monotonically increasing within each symbol; HALT otherwise.
- The loader shall verify dates[0] equals EXPECTED_FIRST_DATE and dates[-1] equals EXPECTED_LAST_DATE; HALT otherwise.
- The loader shall NOT apply any timezone conversion at load time. The CSV dates are already in calendar-date form with no time-of-day or timezone component.
- The loader shall NOT forward-fill, backfill, interpolate, or otherwise synthesize missing dates. Missing-date diagnostic is the audit's responsibility (Step 02c D-checks); the loader trusts the audited dates and returns them verbatim.

## 12. Refusal modes (HALT conditions)

The loader shall HALT with the corresponding exception on any of:

- LoaderManifestMissingError: audit_manifest.json missing OR malformed JSON OR sha256 mismatch against the pin (section 9 step 1).
- LoaderShaMismatchError: per-symbol CSV sha256 mismatch against the audit_manifest pin (section 9 step 3).
- LoaderShapeMismatchError: row count != EXPECTED_ROWS, OR column set != LOCKED_COLS, OR column order != LOCKED_COLS, OR per-row column count != 7.
- LoaderShapeMismatchError: any non-finite price (NaN, Inf, -Inf), any non-positive price (zero or negative), or any negative volume.
- LoaderShapeMismatchError: OHLCV sanity invariant violation (high < open, high < close, high < low, low > open, low > close).
- LoaderShapeMismatchError: any date that is not strictly monotonically increasing within the symbol, or that does not match EXPECTED_FIRST_DATE / EXPECTED_LAST_DATE pins.
- LoaderShapeMismatchError: any volume value that is not a non-negative finite number, or that has a non-zero fractional part when interpreted as a float.
- LoaderCrossSymbolAlignmentError: load_all detects that cross-symbol date sets are not identical (section 9 step 4).
- LoaderError (or subclass): any caller-provided symbol not in SYMBOLS.

A HALT shall raise the appropriate exception with a message containing the symbol, the path, the observed value, and the expected value. The loader shall NOT swallow exceptions silently. The loader shall NOT log to network. The loader shall NOT trigger any retry.

## 13. No-signal / no-backtest boundary

The loader module shall NOT contain any Donchian channel computation. The loader shall NOT compute Wilder ATR. The loader shall NOT compute any rolling statistic of any length. The loader shall NOT generate entry, exit, stop, or pyramid decisions. The loader shall NOT compute returns. The loader shall NOT compute z-scores, moving averages, exponential smoothing, or any other transformation that resembles a trading signal. The loader shall NOT contain any code that imports a backtest engine, a simulator, or a strategy runner. The loader shall NOT call out to LEAN, QC, or any external execution venue.

The loader's test suite shall NOT include any test whose pass condition depends on a Donchian channel value, a Wilder ATR value, a signal, a trade, or a backtest result. Tests that require such values are downstream concerns and are out of scope for the loader's own tests.

## 14. No-fetch / no-network boundary

The loader module shall NOT contain any of: import yfinance, import databento, import requests, import urllib (any submodule), import http.client, import socket, import curl_cffi, import aiohttp, import httpx. If any are transitively imported by a stdlib helper, no .get / .post / .request / .Session / .urlopen / .connect call shall be made from the loader's own code paths.

The loader shall NOT call os.environ to set or read any variable beginning with DATABENTO_, with API_KEY, or with SECRET. The loader shall NOT call os.environ to read DATABENTO_API_KEY under any circumstance. The loader shall NOT disable SSL verification (no verify=False, no ssl._create_unverified_context, no PYTHONHTTPSVERIFY=0, no urllib3.disable_warnings); the loader does not perform network IO at all, so this attestation is structural.

The loader shall NOT have a re-fetch path, a fallback-fetch path, or a vendor-substitution path. If a CSV is missing or mismatched, the loader HALTs. Recovery is the operator's responsibility under a separately authorized re-fetch turn (which would re-execute Step 02b and Step 02c).

## 15. ORB isolation boundary

The loader shall NOT read any ORB branch artifact for any purpose. The loader shall NOT modify any ORB branch artifact. The loader shall NOT read or modify any orb_* file, any branch_orb_* file, or any branch_orb_* report. The loader shall NOT modify any Step 30 cost constant. The loader shall NOT touch app.py, hydra_video/, sparta_commander/, spartacus/, strategy_lab/, or any production module unless the file is explicitly part of the section 4 output set.

## 16. Databento / API-key prohibition

The loader shall NOT call Databento. The loader shall NOT access DATABENTO_API_KEY. The loader shall NOT read os.environ["DATABENTO_API_KEY"]. The literal substring "DATABENTO_API_KEY" shall not appear in the loader module or its tests except as a forbidden-token comment. The loader shall NOT call Yahoo Finance, shall NOT call yfinance, shall NOT call any vendor. The loader is strictly an on-disk CSV adapter.

The build report shall include an api_key_safety_confirmation block attesting:

- databento_called: false
- databento_api_key_accessed: false
- os_environ_DATABENTO_API_KEY_referenced: false
- yfinance_imported_by_loader: false
- yahoo_finance_called_by_loader: false
- any_network_call_by_loader: false

## 17. Validation gates

The build turn shall verify, in order:

V1. The seven output files in section 4 exist at the locked paths.
V2. The loader module is syntactically valid Python (compiles to AST without error).
V3. The loader module imports cleanly without performing any file IO at import time (verified by a sandboxed import smoke test).
V4. The public API surface (section 7) matches exactly: SYMBOLS, LOCKED_COLS, RAW_DIR, AUDIT_MANIFEST_PATH, EXPECTED_ROWS, EXPECTED_FIRST_DATE, EXPECTED_LAST_DATE, LoaderError, LoaderShaMismatchError, LoaderShapeMismatchError, LoaderManifestMissingError, LoaderCrossSymbolAlignmentError, LoadedSymbol, load_symbol, load_all. No other public symbol.
V5. The loader module contains no forbidden import (section 14 list), verified by a static grep over the loader source bytes.
V6. The loader module contains no forbidden token ("DATABENTO_API_KEY", "yfinance", "yahoo_finance", "requests.get", "urllib.request", "socket.connect", "Donchian", "Wilder", "ATR(", "rolling("), verified by static grep. The grep itself is run on the loader source bytes; the build report records the grep results explicitly.
V7. The test suite runs to completion under pytest (or unittest) with all tests passing. No skipped tests are permitted. No test marked xfail.
V8. The test suite includes every test in section 18 (T1..T16). Missing or renamed tests HALT.
V9. A live round-trip test against the four sealed CSVs proves that load_all() returns four LoadedSymbol structures with the expected row count, date pins, sha256 pins, and cross-symbol alignment.
V10. A negative-path test proves that tampering the loader's expected sha256 pin (in a test-only constant, not the real audit_manifest) causes load_symbol to raise LoaderShaMismatchError.

A failing V-gate HALTs the build run; partial outputs are kept; a separately authorized recovery turn is required.

## 18. Test requirements (T1..T16)

The test suite shall contain at minimum these tests; renames are forbidden; additions are permitted only if they uphold the no-signal / no-backtest / no-network boundaries.

- T1: test_load_symbol_returns_loaded_symbol_with_expected_rows_for_each_symbol - parametrize over SPY/TLT/GLD/USO; assert len(.dates) == EXPECTED_ROWS for each.
- T2: test_load_symbol_dates_are_iso_strings_strictly_increasing - assert all dates are 10-char YYYY-MM-DD, strictly monotonic.
- T3: test_load_symbol_first_and_last_date_match_pins - assert .dates[0] == EXPECTED_FIRST_DATE and .dates[-1] == EXPECTED_LAST_DATE.
- T4: test_load_symbol_columns_match_locked_cols - assert returned LoadedSymbol has exactly the seven fields (date, open, high, low, close, adj_close, volume) plus the metadata fields (symbol, csv_path, csv_sha256).
- T5: test_load_symbol_sha256_matches_audit_manifest_pin - parametrize over symbols; assert .csv_sha256 equals the manifest's per_symbol pin.
- T6: test_load_symbol_raises_on_audit_manifest_missing - move the manifest to a temp path; assert LoaderManifestMissingError; restore the manifest.
- T7: test_load_symbol_raises_on_csv_missing - temp-rename a CSV; assert LoaderError (specifically LoaderShaMismatchError or its subclass); restore.
- T8: test_load_symbol_raises_on_csv_sha_mismatch - monkeypatch the manifest's recorded sha256 (in memory; do not write the manifest file); assert LoaderShaMismatchError.
- T9: test_load_symbol_raises_on_unknown_symbol - call load_symbol("ZZZ"); assert LoaderError.
- T10: test_load_symbol_preserves_close_and_adj_close_separately - assert .close is a different tuple than .adj_close, and at least one row has .close[i] != .adj_close[i] for SPY (per F1 evidence).
- T11: test_load_symbol_ohlcv_sanity_per_row - assert per-row invariants (high >= open, high >= close, high >= low, low <= open, low <= close, all prices > 0, volume >= 0).
- T12: test_load_all_returns_four_keys - assert load_all() returns a dict with exactly {"SPY", "TLT", "GLD", "USO"} as keys.
- T13: test_load_all_cross_symbol_dates_aligned - assert the four .dates tuples produce equal sets.
- T14: test_load_all_raises_on_cross_symbol_misalignment - construct an in-memory scenario (mocking one symbol's dates) that triggers LoaderCrossSymbolAlignmentError.
- T15: test_loader_module_imports_perform_no_file_io - import the loader inside a sandbox that fails on any open() call; assert import succeeds (i.e., no module-level file IO).
- T16: test_loader_module_contains_no_forbidden_token - static grep the loader source for "DATABENTO_API_KEY", "yfinance", "Donchian", "Wilder", "ATR(", "rolling(", "requests.get", "urllib.request", "socket.connect"; assert no hits outside comment-marked exclusion lines.

## 19. Build-script safety guardrails

The build turn shall enforce in its own script:

- The script shall open each CSV in read mode only. No write mode against CSVs.
- The script shall not call pandas.DataFrame.to_csv against any canonical path.
- The script shall not call shutil.copy / shutil.move / os.rename / os.remove against any file inside data/s7_d1_cross_asset_donchian/raw/.
- The script shall not import yfinance, databento, requests, urllib (any submodule), http.client, socket, curl_cffi, aiohttp, httpx.
- The script shall not set any environment variable that begins with DATABENTO_.
- The script shall not disable SSL verification.
- The script shall log its build steps to stdout for the build turn's report writer to capture.
- The script shall self-delete on success (mirroring the Step 02b/02c cleanup pattern with a separately authorized cleanup turn for the failure case).

## 20. Loader-build report schema and build acceptance checklist

Report schema (sparta.donchian.step_03_canonical_loader_build_report.v1):

- schema: "sparta.donchian.step_03_canonical_loader_build_report.v1".
- phase: "S7_D1_DONCHIAN_STEP_03_CANONICAL_LOADER_BUILD".
- controller_session: "THIS_SESSION_ONLY".
- report_date_utc: ISO 8601 timestamp.
- plan_anchor: object with path, sha256, commit.
- step_02c_anchor: object with audit_report_sha256, audit_report_seal, audit_manifest_sha256.
- output_files: object keyed by file path; each value contains sha256 and bytes.
- loader_api_surface_observed: list of the loader module's public symbols.
- v_gate_results: object with V1..V10 outcomes.
- t_test_results: object with T1..T16 outcomes (pass/fail/error).
- forbidden_token_grep_results: object with each forbidden token and its hit count in loader.py source (expected: 0 hits outside designated comment exclusion lines).
- boundaries_held: object with one True flag per hard boundary in this plan.
- negative_invariants: object with one False flag per negative invariant.
- api_key_safety_confirmation: object with the six fields in section 16.
- companion_md_sha256: string (one-way reference; the MD does not re-embed the JSON sha or seal, mirroring the Step 02c cycle-free pattern).
- seal_method: canonical string matching prior s7 D1 reports.
- report_seal_sha256: string.

Build acceptance checklist (for the future build turn to satisfy before claiming success):

- A separate operator authorization explicitly authorizes the Step 03 build.
- The plan path is exactly docs/s7_d1_cross_asset_donchian_step_03_canonical_loader_specification_plan.md.
- The four CSVs and audit_manifest.json at data/s7_d1_cross_asset_donchian/raw/ are present and byte-unchanged.
- The output paths in section 4 are confirmed MISSING via L_FILE_SAFETY pre-state capture before any write.
- No co-active Databento path.
- No co-active backtest path.
- The build turn writes only the seven output files in section 4 plus the optional temp scripts in section 5 (each deleted on success).
- The build turn's report contains a faithful list of every V-gate and T-test outcome.

## 21. What build is NOT allowed to do, and Next authorization required

The build turn shall NOT:

- Compute a Donchian channel of any length on any CSV.
- Compute a Wilder ATR of any length.
- Compute any rolling statistic that resembles a trading signal.
- Run a backtest, simulator, or paper-trade loop.
- Make any live order, paper-trade, or broker call.
- Modify any of the four canonical CSVs.
- Modify the existing fetch_run_manifest.json or audit_manifest.json.
- Modify any Step 02b or Step 02c report.
- Modify any spec, plan, or prior Step 02 artifact.
- Modify ORB branch artifacts.
- Modify Step 30 cost constants.
- Modify CLAUDE.md, docs/decisions.md, RUNBOOK, pipeline_manifest, or .gitignore.
- Switch branches or create branches.
- Call yfinance, Yahoo Finance, or any network resource.
- Call Databento or any vendor.
- Access DATABENTO_API_KEY or any environment variable starting with DATABENTO_.
- Disable SSL certificate verification.
- Create or modify external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/ (the Databento-track runner; out of scope for this yfinance-proxy track).
- Use the instruction phrase "build the loader now" as an active directive (this phrase appears here only as forbidden text).
- Treat the phrase "authorize Step 03 build" as a completed or current action (this phrase appears here only to mark a future-state authorization gate).
- Treat any downstream phase (Step 04 input validator, Step 05 signal computation, Step 06 simulator, Step 07 backtest, or any other) as pre-authorized.

A future operator authorization is required to proceed beyond this plan. That authorization shall reference this plan by exact path. This plan is the source of truth for the loader specification; the build turn is not pre-authorized by the plan itself.

Future expected status on the Step 03 build turn (informational; not granted here):

STEP_03_CANONICAL_LOADER_BUILT
LOADER_TEST_SUITE_PASSED_T1_TO_T16
LOADER_BUILD_REPORT_SEALED
NO_CSV_MODIFIED
NO_AUDIT_MANIFEST_MODIFIED
NO_FETCH_RUN_MANIFEST_MODIFIED
NO_DONCHIAN_SIGNAL_COMPUTED
NO_WILDER_ATR_COMPUTED
NO_CHANNEL_COMPUTED
NO_SIMULATOR_RUN
NO_BACKTEST
NO_DATA_FETCH
NO_NETWORK_CALL
NO_DATABENTO_CALL
NO_DATABENTO_API_KEY_ACCESS
NO_ORB_BRANCH_MUTATION
NO_LIVE_TRADING

Downstream-phase reminder (informational; not authorized by this plan):

- Step 04 (Donchian input validator) shall be specified in its own plan after Step 03 build completes successfully. The input validator is the bridge between LOADER and SIGNAL; it verifies that the loaded data is suitable for signal construction (e.g., enough warmup, no holes, expected liquidity). The input validator does NOT compute signals.
- Step 05 (signal computation), Step 06 (simulator), Step 07 (backtest) are all downstream of Step 04 and require their own plans, their own authorizations, and their own sealed artifacts. None of them are implied as automatic by Step 03.
- This Step 03 plan does not pre-specify any of those downstream phases. Doing so under this plan's authorization would be scope creep.

----

End of plan. Plan-authoring turn only. No code written. No loader built. No tests written. No data read by claude beyond what Step 02c already sealed. No Donchian signal. No Wilder ATR. No simulator. No backtest. No data fetch. No network. No Databento. No DATABENTO_API_KEY access. No ORB branch mutation. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.

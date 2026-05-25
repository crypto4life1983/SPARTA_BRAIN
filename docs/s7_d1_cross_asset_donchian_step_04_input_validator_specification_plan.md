# s7 D1 Cross-Asset Donchian - Step 04 Input Validator Specification Plan

Status: PLAN_ONLY (build not yet authorized; execution requires a separately authorized turn).
Authored: 2026-05-25
Parent spec: docs/s7_d1_cross_asset_donchian_spec.md
Parent Step 02b plan: docs/s7_d1_cross_asset_donchian_step_02b_alt_vendor_data_fetch_plan.md (commit efdc307)
Parent Step 02c plan: docs/s7_d1_cross_asset_donchian_step_02c_next_phase_plan.md (commit faebd58)
Step 02c audit (verdict PASS): reports/s7_d1_cross_asset_donchian_step_02c_raw_data_audit_report.json (sha256 a17c90032fdab504c9da540a44cce37bed8f9bfaf983c625f9c1dbdfebf6d354, seal 872b8275a57e859017e85abb837966b64ad1c0860df413ec010109c407c1b14f, commit 1b640d1)
Parent Step 03 plan: docs/s7_d1_cross_asset_donchian_step_03_canonical_loader_specification_plan.md (commit f759251)
Step 03 build (verdict PASS): reports/s7_d1_cross_asset_donchian_step_03_canonical_loader_build_report.json (sha256 137dd8534de840762abc9e6e3f9d22ad5314a1e6f2a4ddc783da3e90429c8386, seal 89b2e14122113fa12a319c0b0d8331573aa3bca824a494c4b9e1a5a43601a80c, commit d7b2a0c)
Loader module: external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/loader.py (sha256 e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9)
Naming convention: s7 D1 cross-asset Donchian yfinance proxy (continues the alternate-vendor research track).

HARD BOUNDARIES (held by this plan). Plan only. No code change. No validator implementation. No test implementation. No build report write. No CSV read by claude during plan authoring. No fetch_run_manifest.json modification. No audit_manifest.json modification. No CSV modification. No loader.py modification. No Donchian channel computation. No Wilder ATR computation. No 55-bar or 20-bar channel computation. No rolling signal statistic. No moving average. No exponential smoothing. No return computation. No log-return computation. No z-score. No correlation matrix. No covariance. No simulator run. No backtest. No paper-trade loop. No data fetch. No yfinance import. No Yahoo Finance call. No Databento call. No DATABENTO_API_KEY access. No network IO. No ORB branch artifact mutation. No Step 30 cost constant mutation. No existing source code modification. No tests modification. No CLAUDE.md modification. No docs/decisions.md modification. No RUNBOOK modification. No pipeline_manifest modification. No .gitignore modification. No branch change. No branch creation. No commit beyond the single new plan file. No git push. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted. No profitability claim.

----

## 1. Purpose

Define the canonical Python input validator for LoadedSymbol structures produced by the Step 03 canonical loader. The validator is the bridge between LOADER (Step 03, done) and SIGNAL (Step 05+, far future): it verifies that the loaded data is suitable for downstream channel construction, sizing, and backtest WITHOUT itself computing any of those quantities. The validator is a pure function over LoadedSymbol input; it does not call the loader (the caller does that first), does not re-read CSV bytes, does not perform any IO, and contains no signal-side logic.

This validator answers the question "is this LoadedSymbol fit to feed a downstream Donchian channel construction step?" with a PASS/FAIL outcome and a detailed per-symbol ValidationReport. It does NOT answer "what is the channel value at bar k" or "should we enter a trade." Those are downstream questions.

## 2. Why Step 04 comes after Step 03

Step 03 sealed the loader (verdict PASS at commit d7b2a0c). The loader returns LoadedSymbol structures with sha256-pinned data, locked column set, monotonic dates, OHLC invariants, and per-symbol distinct close vs adj_close (per Step 02c finding F1). With the loader in place, any downstream phase can call load_symbol() / load_all() to obtain the data. But before a downstream signal-construction phase consumes that data, the data should be checked for FITNESS-FOR-PURPOSE against the specific demands of the cross-asset Donchian-55 entry / Donchian-20 exit mechanic. Those demands include:

- **Warmup adequacy** - Donchian-55 needs at least 55 prior bars before the first signal-eligible bar. The validator confirms structural warmup adequacy without computing a channel.
- **Window coverage** - the parent spec section 11 pins in-sample window 2013-01-01 to 2022-12-30 and out-of-sample window 2023-01-01 to 2025-12-30. The validator confirms the loaded data covers these windows and records the per-symbol bar counts in each window.
- **Cross-symbol alignment** - the cross-asset mechanic depends on synchronized trading days across SPY/TLT/GLD/USO. The validator re-confirms alignment (the loader already does this in load_all(); the validator re-attests it as an independent layer).
- **Liquidity and price-range diagnostics** - downstream phases will want to know IS-window volume distribution and price-range bounds. The validator records these summary statistics for the IS window only (out-of-sample summary stats are deliberately NOT computed to preserve the spec's `oos_inspection_blocked_at_in_sample` invariant).

Step 04 is the validator's SPECIFICATION. Step 04 is NOT the validator's implementation; the implementation requires a separately authorized Step 04b build turn.

## 3. Inputs from Step 03

The validator depends only on the public API of the Step 03 loader package and on the LoadedSymbol dataclass. No new files are introduced. No CSV is read directly.

Locked input contract:

- The validator consumes a `LoadedSymbol` instance (or a `dict[str, LoadedSymbol]` keyed by symbol).
- LoadedSymbol fields the validator MAY read: `symbol`, `dates`, `open`, `high`, `low`, `close`, `adj_close`, `volume`, `csv_path`, `csv_sha256`.
- LoadedSymbol fields the validator MUST treat as opaque (no parsing, no transformation): all fields above are tuples; the validator reads them as-is and does not mutate, slice, or repackage them.

The validator MUST NOT call `load_symbol()` / `load_all()` itself. The caller is responsible for loading first.

## 4. Outputs the future build turn will create

The build turn for Step 04 shall create the following artifacts and no others:

- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/validator.py (the validator module).
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/__init__.py (re-exports the public API listed in section 7).
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/README.md (usage docs; pins the spec/loader/audit shas).
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/test_validator.py (the test suite enumerated in section 19).
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/__init__.py (test package marker; may be empty).
- reports/s7_d1_cross_asset_donchian_step_04_input_validator_build_report.json (sealed; canonical Python-side seal scheme).
- reports/s7_d1_cross_asset_donchian_step_04_input_validator_build_report.md (companion human-readable form).

No other files. No supplementary modules. No log files at any path.

## 5. Files the build turn may create or modify later

Permitted writes by the build turn (subject to its own separate authorization):

- The seven output files in section 4.
- A temporary build script under scripts/ (suggested name: scripts/_s7_d1_donchian_step_04_validator_build.py) written, run once, and deleted on success.
- A temporary sealing helper under scripts/ if needed (suggested name: scripts/_step_04_validator_build_report_seal.py) deleted on success.

The temp scripts shall be byte-deleted on success. Failure cases shall leave them in place pending a separately authorized cleanup turn.

## 6. Files the build turn must not modify

This list is exhaustive for the categories enumerated; any file not listed is also not permitted unless it is in section 5.

- The four canonical CSVs at data/s7_d1_cross_asset_donchian/raw/*.csv.
- data/s7_d1_cross_asset_donchian/raw/fetch_run_manifest.json.
- data/s7_d1_cross_asset_donchian/raw/audit_manifest.json.
- reports/s7_d1_cross_asset_donchian_step_02b_*.{json,md}.
- reports/s7_d1_cross_asset_donchian_step_02c_*.{json,md}.
- reports/s7_d1_cross_asset_donchian_step_03_*.{json,md}.
- docs/s7_d1_cross_asset_donchian_spec.md.
- docs/s7_d1_cross_asset_donchian_step_02b_alt_vendor_data_fetch_plan.md.
- docs/s7_d1_cross_asset_donchian_step_02c_next_phase_plan.md.
- docs/s7_d1_cross_asset_donchian_step_03_canonical_loader_specification_plan.md.
- This Step 04 plan file (the build turn quotes it, attests against it; does not edit it).
- external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/ contents (loader.py / __init__.py / README.md).
- tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/ contents.
- CLAUDE.md, docs/decisions.md, RUNBOOK (if present), pipeline_manifest (if present), .gitignore.
- All ORB branch artifacts.
- All Step 30 cost constants.
- review_queue.json, the idea_memory directory, Strategy Lab artifacts.
- The Databento-track runner harness path external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/ (out of scope; this is the yfinance ETF-proxy track).

## 7. API surface

The validator module shall expose exactly the following public API and no other public symbols:

- DONCHIAN_ENTRY_LOOKBACK: int = 55 (the lookback the validator's warmup check uses; intentionally NOT the channel computation itself).
- DONCHIAN_EXIT_LOOKBACK: int = 20.
- IN_SAMPLE_WINDOW: tuple[str, str] = ("2013-01-01", "2022-12-30") (spec section 11 pin; YYYY-MM-DD inclusive on both ends).
- OUT_OF_SAMPLE_WINDOW: tuple[str, str] = ("2023-01-01", "2025-12-30") (spec section 11 pin).
- POST_OOS_DIAGNOSTIC_WINDOW: tuple[str, str] = ("2026-01-02", "2026-05-22") (informational; not a pass/fail window; reflects ETF-proxy data extension beyond the spec's OOS end).
- class ValidatorError(Exception) - base class for every refusal mode (section 13).
- class ValidatorInputError(ValidatorError) - input not a LoadedSymbol or LoadedSymbol structurally invalid.
- class WarmupInsufficientError(ValidatorError) - fewer than DONCHIAN_ENTRY_LOOKBACK bars exist before the IS-window-first signal-eligible date.
- class WindowMisfitError(ValidatorError) - a window has zero bars or end-date < start-date.
- class ValidatorCrossSymbolAlignmentError(ValidatorError) - cross-symbol date sets do not match.
- @dataclass(frozen=True) class ValidationReport (per-symbol; schema in section 8).
- @dataclass(frozen=True) class CrossSymbolValidationReport (per-portfolio; schema in section 8).
- def validate_loaded_symbol(loaded: LoadedSymbol) -> ValidationReport - per-symbol check.
- def validate_all(data: Mapping[str, LoadedSymbol]) -> CrossSymbolValidationReport - cross-symbol check; calls validate_loaded_symbol on each then verifies alignment.

No other public function. No public mutable state. No module-level data load at import time.

## 8. ValidationReport schema and field definitions

ValidationReport (per-symbol) fields:

- symbol: str.
- csv_sha256_observed: str (carried through from LoadedSymbol; not recomputed).
- bar_count_total: int (must equal 3116).
- date_first: str.
- date_last: str.
- bar_count_in_in_sample_window: int (count of dates in [IN_SAMPLE_WINDOW[0], IN_SAMPLE_WINDOW[1]]).
- bar_count_in_oos_window: int (count of dates in [OUT_OF_SAMPLE_WINDOW[0], OUT_OF_SAMPLE_WINDOW[1]]).
- bar_count_in_post_oos_window: int.
- warmup_bars_available_before_first_in_sample_signal_eligible_bar: int.
- first_in_sample_signal_eligible_index: int (0-based index into LoadedSymbol.dates of the first bar in the IS window that has >= DONCHIAN_ENTRY_LOOKBACK prior bars).
- first_in_sample_signal_eligible_date: str.
- warmup_truncation_at_data_start: bool (True if IS-window-first date in data is later than IN_SAMPLE_WINDOW[0], meaning we have less than the spec-intended IS coverage; informational only).
- in_sample_volume_summary: dict with keys {min, median, max, zero_volume_day_count} (computed over IS window ONLY).
- in_sample_close_summary: dict with keys {min, max} (computed over IS window ONLY).
- in_sample_adj_close_summary: dict with keys {min, max} (computed over IS window ONLY).
- oos_summary_intentionally_omitted: bool (always True; documents the OOS-protection rule from section 12).
- post_oos_summary_intentionally_omitted: bool (always True; same protection extended to post-OOS).
- check_results: dict with keys for each W/B/S/G check outcome (see section 10).
- verdict: str (one of "PASS", "PASS_WITH_WARMUP_TRUNCATION", "FAIL"). PASS_WITH_WARMUP_TRUNCATION is a non-fatal pass that records the missing IS coverage at the start of the data; downstream phases consume the warmup-truncation flag and decide whether to proceed.

CrossSymbolValidationReport fields:

- per_symbol: dict[str, ValidationReport].
- cross_symbol_dates_aligned: bool.
- cross_symbol_bar_count_equal: bool (all symbols have the same bar_count_total).
- cross_symbol_in_sample_bar_count_equal: bool.
- cross_symbol_oos_bar_count_equal: bool.
- check_results: dict with keys for each A-check outcome (see section 11).
- portfolio_verdict: str (one of "PASS", "PASS_WITH_WARMUP_TRUNCATION", "FAIL"). FAIL if any per-symbol verdict is FAIL or any A-check fails.

Both dataclasses are frozen (immutable). No mutable fields.

## 9. Window definitions

Three windows are pinned in this plan. Their string boundaries are inclusive on both ends.

- **IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")**. Matches spec section 11 exactly. The ETF-proxy data starts 2014-01-02, which is later than 2013-01-01; the validator records this as warmup_truncation_at_data_start=True (informational; not a HALT).
- **OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")**. Matches spec section 11 exactly. The ETF-proxy data covers this range fully.
- **POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")**. Reflects the ETF-proxy data extension beyond the spec's OOS end. INFORMATIONAL ONLY. No pass/fail. No statistical inspection. Bar count only.

These windows are pinned constants in the validator module; downstream phases shall not silently override them. Any change to a window value requires a fresh `_revN_` validator spec under separate authorization.

## 10. Per-symbol validation checks

The validator runs five check categories per symbol. Each check outcome lands in ValidationReport.check_results.

**W: warmup checks**

- W1: bar_count_total == 3116. HALT (ValidatorInputError) on mismatch.
- W2: dates are 10-char YYYY-MM-DD strings, strictly monotonically increasing. HALT on violation.
- W3: warmup_bars_available_before_first_in_sample_signal_eligible_bar >= DONCHIAN_ENTRY_LOOKBACK (= 55). HALT (WarmupInsufficientError) on violation. Note: "bars available" counts ANY bars in the loaded data that precede the first IS-window date; for the ETF-proxy track these will be zero (data starts 2014-01-02 and IS starts 2013-01-01), so the validator computes the first IS bar that has >= 55 PRIOR loaded bars and reports that index/date.
- W4: first_in_sample_signal_eligible_index is finite and < bar_count_total. HALT on violation.

**B: bar-count checks**

- B1: bar_count_in_in_sample_window >= DONCHIAN_ENTRY_LOOKBACK + 1 (= 56). HALT (WindowMisfitError) on violation.
- B2: bar_count_in_oos_window > 0. HALT (WindowMisfitError) on violation.
- B3: bar_count_in_post_oos_window >= 0 (informational; never HALTs; recorded only).

**S: in-sample summary statistic checks (IS only)**

- S1: in_sample_close_summary.min > 0 AND in_sample_close_summary.max finite. HALT (ValidatorInputError) on violation.
- S2: in_sample_adj_close_summary.min > 0 AND in_sample_adj_close_summary.max finite. HALT on violation.
- S3: in_sample_volume_summary.min >= 0 AND in_sample_volume_summary.max finite. HALT on violation.
- S4: in_sample_volume_summary.zero_volume_day_count is recorded (no HALT; diagnostic).

**G: gap / continuity diagnostic checks**

- G1: dates list has no internal duplicates (re-confirmation; loader already enforces). HALT on violation.
- G2: every date in IS window is a calendar date (parses as datetime.date.fromisoformat). HALT on violation.
- G3: gap_count_in_in_sample_window_vs_weekday_count is recorded as a diagnostic; the validator does NOT HALT on holiday-gap variance.

## 11. Cross-symbol validation checks

CrossSymbolValidationReport runs the A-check category across the four LoadedSymbols.

- A1: per_symbol has exactly four keys equal to {"SPY", "TLT", "GLD", "USO"}. HALT (ValidatorInputError) on violation.
- A2: cross_symbol_bar_count_equal True. HALT (ValidatorCrossSymbolAlignmentError) on violation.
- A3: cross_symbol_dates_aligned True (the four .dates tuples produce equal sets). HALT on violation.
- A4: cross_symbol_in_sample_bar_count_equal True. HALT on violation.
- A5: cross_symbol_oos_bar_count_equal True. HALT on violation.
- A6: each per_symbol ValidationReport carries a verdict in {"PASS", "PASS_WITH_WARMUP_TRUNCATION"}. portfolio_verdict is FAIL if any per-symbol verdict is FAIL.

## 12. OOS protection rule

This is the key safety rule that distinguishes this validator from any signal-side analysis.

For the OUT_OF_SAMPLE_WINDOW and POST_OOS_DIAGNOSTIC_WINDOW, the validator records ONLY:

- the count of bars whose date falls in the window;
- the first and last date in the window (informational coverage marker).

The validator does NOT compute any of the following for OOS or post-OOS data:

- min/max/median/mean of close, open, high, low, adj_close, or volume in the OOS or post-OOS window;
- per-day returns or log-returns;
- rolling statistics of any length;
- z-scores or normalizations;
- correlations or covariances;
- any quantile, percentile, or rank statistic;
- any summary that depends on per-bar OOS-window numeric values beyond pure counting.

This rule preserves the spec section 11 invariant `oos_inspection_blocked_at_in_sample`. The OOS data exists on disk, the loader will return it whenever called, but THIS validator deliberately does not inspect it beyond bar-count and date-coverage. Downstream phases that need OOS access must be separately authorized AFTER an IS-window run has produced a verdict that grants OOS inspection.

`oos_summary_intentionally_omitted` and `post_oos_summary_intentionally_omitted` are always True in the ValidationReport (they are attestations that the OOS protection rule was applied, not toggle switches).

## 13. Refusal modes (HALT conditions)

The validator shall HALT with the corresponding exception on any of:

- ValidatorInputError: input is not LoadedSymbol; symbol field not in {"SPY","TLT","GLD","USO"}; bar_count_total != 3116; in_sample_close min not positive; in_sample_adj_close min not positive; in_sample_volume min negative; or any structural malformation of the input.
- WarmupInsufficientError: W3 violation (fewer than 55 prior loaded bars before the first IS-window date).
- WindowMisfitError: bar_count_in_in_sample_window < DONCHIAN_ENTRY_LOOKBACK + 1; bar_count_in_oos_window == 0; any window end-date earlier than start-date.
- ValidatorCrossSymbolAlignmentError: A1 / A2 / A3 / A4 / A5 violation.
- ValidatorError (base): any other unhandled refusal condition.

The validator shall NOT silently downgrade a FAIL to a PASS_WITH_WARMUP_TRUNCATION; only the specific warmup-truncation-at-data-start case (where the IS window's first calendar date precedes the loaded data's first date) maps to PASS_WITH_WARMUP_TRUNCATION, and only when W3 still passes (i.e., 55+ prior loaded bars exist before the first IS-window-resident loaded bar). All other shortfalls raise.

## 14. No-signal / no-channel / no-ATR / no-rolling-stat / no-correlation / no-returns boundary

The validator module shall NOT contain any of the following computations or any code that performs them:

- Donchian channel of any length;
- Wilder ATR of any length;
- simple moving average of any length;
- exponential moving average of any length;
- any rolling-window aggregation;
- per-day percentage return;
- per-day log-return;
- cumulative return;
- z-score;
- correlation matrix (Pearson, Spearman, Kendall, or otherwise);
- covariance matrix;
- principal component analysis;
- any quantile or percentile computation over OOS or post-OOS data (IS-window min/median/max as enumerated in section 10 is allowed; quantiles are not).

The validator's test suite shall NOT include any test whose pass condition depends on a Donchian channel value, a Wilder ATR value, a return value, a correlation, a signal, a trade, or a backtest result. Those are downstream concerns and out of scope.

## 15. No-fetch / no-network boundary

The validator module shall NOT contain any of: import yfinance, import databento, import requests, import urllib (any submodule), import http.client, import socket, import curl_cffi, import aiohttp, import httpx. The validator shall NOT call os.environ to set or read any variable beginning with DATABENTO_, API_KEY, or SECRET. The validator shall NOT call os.environ to read DATABENTO_API_KEY under any circumstance. The validator shall NOT disable SSL verification.

The validator performs NO file IO at all. It does not call the loader (the caller does that). It does not read CSVs. It does not read the audit_manifest.json. It does not read the loader source. It does not write to disk. (The build-time test suite may verify these properties via patched `builtins.open` / `Path.read_bytes`.)

## 16. ORB isolation boundary

The validator shall NOT read any ORB branch artifact for any purpose. The validator shall NOT modify any ORB branch artifact. The validator shall NOT read or modify any orb_* file, any branch_orb_* file, or any branch_orb_* report. The validator shall NOT modify any Step 30 cost constant. The validator shall NOT touch app.py, hydra_video/, sparta_commander/, spartacus/, strategy_lab/, or any production module unless the file is explicitly part of the section 4 output set.

## 17. Databento / API-key prohibition

The validator shall NOT call Databento. The validator shall NOT access DATABENTO_API_KEY. The validator shall NOT read os.environ["DATABENTO_API_KEY"]. The literal substring "DATABENTO_API_KEY" shall not appear in the validator module or its tests except as a forbidden-token comment. The validator shall NOT call Yahoo Finance, shall NOT call yfinance, shall NOT call any vendor. The validator is strictly an in-memory checker over LoadedSymbol structures.

The build report shall include an api_key_safety_confirmation block attesting:

- databento_called: false
- databento_api_key_accessed: false
- os_environ_DATABENTO_API_KEY_referenced: false
- yfinance_imported_by_validator: false
- yahoo_finance_called_by_validator: false
- any_network_call_by_validator: false
- any_file_io_by_validator: false

## 18. Validation gates V1-V10

The build turn shall verify, in order:

V1. The seven output files in section 4 exist at the locked paths.
V2. The validator module is syntactically valid Python (AST compiles without error).
V3. The validator module imports cleanly without performing any file IO at import time (verified by patched-open sandbox).
V4. The public API surface (section 7) matches exactly. No extra public symbol.
V5. The validator module contains no forbidden import (section 15 list), verified by static grep.
V6. The validator module contains no forbidden token: "DATABENTO_API_KEY", "yfinance", "yahoo_finance", "requests.get", "urllib.request", "socket.connect", "Donchian", "Wilder", "ATR(", "rolling(", "correlation", "covariance", ".pct_change(", "log_return", "ema(", "sma(". Verified by static grep over loader source bytes. The grep allows comment-marked exclusion lines (e.g. lines beginning with "#" containing "FORBIDDEN_TOKEN_EXCLUSION").
V7. The test suite runs to completion under stdlib unittest with all tests passing. No skipped tests. No xfail.
V8. The test suite includes every test in section 19 (T1..T16). Missing or renamed tests HALT.
V9. A live integration test: build a fresh load_all() result via the Step 03 loader (in test code only), pass it to validate_all(), assert portfolio_verdict in {"PASS", "PASS_WITH_WARMUP_TRUNCATION"}, assert all four per-symbol verdicts are in that set, assert cross_symbol_dates_aligned True.
V10. A live negative-path test: construct an in-memory LoadedSymbol with bar_count_total < 3116 OR a misaligned dates set, pass to validate_loaded_symbol / validate_all, assert raises the appropriate ValidatorError subclass.

A failing V-gate HALTs the build run; partial outputs are kept; a separately authorized recovery turn is required.

## 19. Test requirements (T1-T16)

The test suite shall contain at minimum these tests; renames are forbidden; additions are permitted only if they uphold the boundary rules in sections 14-17.

- T1: test_validate_loaded_symbol_returns_validationreport - for each symbol, returns a ValidationReport with bar_count_total == 3116.
- T2: test_validate_loaded_symbol_in_sample_bar_count_per_symbol - bar_count_in_in_sample_window is consistent across symbols.
- T3: test_validate_loaded_symbol_oos_bar_count_per_symbol - bar_count_in_oos_window is consistent across symbols.
- T4: test_validate_loaded_symbol_warmup_metric_is_at_least_55 - warmup_bars_available_before_first_in_sample_signal_eligible_bar >= 55.
- T5: test_validate_loaded_symbol_warmup_truncation_flag_true_for_etf_proxy - warmup_truncation_at_data_start is True for this dataset (data starts 2014-01-02; IS window starts 2013-01-01).
- T6: test_validate_loaded_symbol_in_sample_summary_present - in_sample_close_summary / in_sample_adj_close_summary / in_sample_volume_summary each have the expected keys.
- T7: test_validate_loaded_symbol_oos_summary_intentionally_omitted_true - the attestation is True; assert no field like "oos_close_min" exists on the ValidationReport.
- T8: test_validate_loaded_symbol_raises_on_input_not_loadedsymbol - pass a plain dict or None; expect ValidatorInputError.
- T9: test_validate_loaded_symbol_raises_on_bar_count_mismatch - construct LoadedSymbol with 3115 dates; expect ValidatorInputError (W1) or WindowMisfitError depending on which checks first.
- T10: test_validate_loaded_symbol_verdict_in_allowed_set - verdict is one of {"PASS", "PASS_WITH_WARMUP_TRUNCATION", "FAIL"}.
- T11: test_validate_all_returns_crosssymbolvalidationreport - load_all then validate_all returns CrossSymbolValidationReport with four per-symbol entries.
- T12: test_validate_all_cross_symbol_aligned_true_for_real_data - cross_symbol_dates_aligned True.
- T13: test_validate_all_raises_on_synthetic_misalignment - construct dict where one symbol has a perturbed dates tuple; expect ValidatorCrossSymbolAlignmentError.
- T14: test_validate_all_portfolio_verdict_consistent - portfolio_verdict is FAIL iff any per_symbol verdict is FAIL or any A-check fails.
- T15: test_validator_module_imports_perform_no_file_io - patched open() + Path.read_bytes; assert import triggers neither.
- T16: test_validator_module_contains_no_forbidden_token - static grep of validator.py for the V6 token list; zero hits outside comment-exclusion lines.

## 20. Build-script safety guardrails and Build report schema

Build-script safety guardrails:

- The script shall not open any CSV file in write mode against the canonical paths.
- The script shall not call pandas.DataFrame.to_csv against the canonical paths.
- The script shall not call shutil.copy / shutil.move / os.rename / os.remove against any file inside data/s7_d1_cross_asset_donchian/raw/.
- The script shall not import yfinance, databento, requests, urllib (any submodule), http.client, socket, curl_cffi, aiohttp, or httpx.
- The script shall not set any environment variable that begins with DATABENTO_.
- The script shall not disable SSL verification.
- The script shall log its build steps to stdout for the build turn's report writer to capture.
- The script shall self-delete on success (mirroring the Step 02b/02c/03 pattern; a separately authorized cleanup turn for the failure case).

Build report schema (sparta.donchian.step_04_input_validator_build_report.v1):

- schema: "sparta.donchian.step_04_input_validator_build_report.v1".
- phase: "S7_D1_DONCHIAN_STEP_04_INPUT_VALIDATOR_BUILD".
- controller_session: "THIS_SESSION_ONLY".
- report_date_utc: ISO 8601 timestamp.
- plan_anchor: object with path, sha256, commit (this plan's commit).
- step_03_anchor: object with build_report_sha256, build_report_seal, loader_module_sha256.
- step_02c_anchor: object with audit_report_sha256, audit_report_seal, audit_manifest_sha256.
- output_files: object keyed by path; each value contains sha256 and bytes.
- validator_api_surface_observed: list of the validator module's public symbols.
- v_gate_results: object with V1..V10 outcomes.
- t_test_results: object with T1..T16 outcomes.
- forbidden_token_grep_results: object with per-token hit counts for validator.py.
- boundaries_held: object with one True flag per hard boundary in this plan.
- negative_invariants: object with one False flag per negative invariant.
- api_key_safety_confirmation: object with the seven fields in section 17.
- companion_md_sha256: string (one-way reference; mirroring the Step 02c/03 cycle-free pattern).
- seal_method: canonical string matching prior s7 D1 reports.
- report_seal_sha256: string.

Build acceptance checklist (for the future build turn to satisfy before claiming success):

- A separate operator authorization explicitly authorizes the Step 04 build.
- The plan path is exactly docs/s7_d1_cross_asset_donchian_step_04_input_validator_specification_plan.md.
- The Step 03 loader module is byte-unchanged at sha256 e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9.
- The four CSVs and audit_manifest.json at data/s7_d1_cross_asset_donchian/raw/ are byte-unchanged.
- The output paths in section 4 are confirmed MISSING via L_FILE_SAFETY pre-state capture before any write.
- No co-active Databento path.
- No co-active backtest path.
- The build turn writes only the seven output files in section 4 plus the optional temp scripts in section 5 (each deleted on success).

## 21. What build is NOT allowed to do, and Next authorization required

The build turn shall NOT:

- Compute a Donchian channel of any length.
- Compute a Wilder ATR of any length.
- Compute returns, log-returns, z-scores, correlations, covariances, or any other transformation that approaches signal-side logic.
- Run a backtest, simulator, or paper-trade loop.
- Make any live order, paper-trade, or broker call.
- Modify any of the four canonical CSVs.
- Modify the existing fetch_run_manifest.json, audit_manifest.json, or any Step 02/03 artifact.
- Modify any spec or plan file.
- Modify ORB branch artifacts.
- Modify Step 30 cost constants.
- Modify CLAUDE.md, docs/decisions.md, RUNBOOK, pipeline_manifest, or .gitignore.
- Switch branches or create branches.
- Call yfinance, Yahoo Finance, or any network resource.
- Call Databento or any vendor.
- Access DATABENTO_API_KEY or any environment variable starting with DATABENTO_.
- Disable SSL certificate verification.
- Create or modify external_research_hunter/s7_d1_cross_asset_donchian_runner_harness/.
- Inspect OOS or post-OOS data beyond the bar-count + date-coverage permitted in section 12.
- Use the instruction phrase "build the validator now" as an active directive (this phrase appears here only as forbidden text).
- Treat the phrase "authorize Step 04 build" as a completed or current action (this phrase appears here only to mark a future-state authorization gate).
- Treat any downstream phase (Step 05 signal computation, Step 06 simulator, Step 07 backtest, or any other) as pre-authorized.

A future operator authorization is required to proceed beyond this plan. That authorization shall reference this plan by exact path. This plan is the source of truth for the validator specification; the build turn is not pre-authorized by the plan itself.

Future expected status on the Step 04 build turn (informational; not granted here):

STEP_04_INPUT_VALIDATOR_BUILT
VALIDATOR_TEST_SUITE_PASSED_T1_TO_T16
VALIDATOR_BUILD_REPORT_SEALED
NO_CSV_MODIFIED
NO_AUDIT_MANIFEST_MODIFIED
NO_FETCH_RUN_MANIFEST_MODIFIED
NO_LOADER_MODIFIED
NO_DONCHIAN_SIGNAL_COMPUTED
NO_WILDER_ATR_COMPUTED
NO_CHANNEL_COMPUTED
NO_ROLLING_STAT_COMPUTED
NO_RETURNS_COMPUTED
NO_CORRELATION_COMPUTED
NO_OOS_STAT_COMPUTED
NO_SIMULATOR_RUN
NO_BACKTEST
NO_DATA_FETCH
NO_NETWORK_CALL
NO_FILE_IO_BY_VALIDATOR
NO_DATABENTO_CALL
NO_DATABENTO_API_KEY_ACCESS
NO_ORB_BRANCH_MUTATION
NO_LIVE_TRADING

Downstream-phase reminder (informational; not authorized by this plan):

- Step 05 (Donchian signal computation) shall be specified in its own plan after Step 04 build completes successfully. Signal computation is where Donchian-55 entry and Donchian-20 exit channels are first constructed; this is the first downstream phase that crosses the no-signal boundary. Step 05 requires its own plan, its own authorization, and its own sealed artifacts.
- Step 06 (simulator), Step 07 (backtest), and any later phases are downstream of Step 05 and require their own plans, their own authorizations, and their own sealed artifacts.
- The OOS inspection invariant from spec section 11 (`oos_inspection_blocked_at_in_sample`) is OUT OF SCOPE for Step 04 to relax. The validator records OOS bar counts only; any actual OOS signal inspection requires a separately authorized turn that follows an IS-window PASS.

----

End of plan. Plan-authoring turn only. No code written. No validator built. No tests written. No CSV read. No LoadedSymbol constructed. No Donchian signal. No Wilder ATR. No correlation. No returns. No rolling stat. No simulator. No backtest. No data fetch. No network. No Databento. No DATABENTO_API_KEY access. No ORB branch mutation. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.

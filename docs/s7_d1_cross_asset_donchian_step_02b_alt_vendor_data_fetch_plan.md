# s7 D1 Cross-Asset Donchian - Step 02b Alternate-Vendor (yfinance) Data-Fetch Plan

Status: PLAN_ONLY (build/fetch not yet authorized; execution requires a separately authorized turn).
Authored: 2026-05-25
Parent spec: docs/s7_d1_cross_asset_donchian_spec.md
Reconciliation: reports/branch_donchian_cross_asset_step_02b_repository_reconciliation_report.json (seal a85b8fc684d00d8b90db7782e11ee3b0bd8fc81be50a4208ab36cfa3ff970514)
Naming convention: s7 D1 cross-asset Donchian (matches existing repo work; supersedes the absent branch_donchian_cross_asset_* references that were not in this repo).

HARD BOUNDARIES (held by this plan). Plan only. No code change. No yfinance import. No Yahoo Finance network call. No Databento call. No data fetch. No CSV write. No fetch_run_manifest.json write. No backtest. No Donchian signal computation. No simulator run. No ORB branch mutation. No branch change. No commit beyond the single new plan file. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC never granted. No profitability claim.

----

## 1. Purpose

Define an alternate-vendor daily-bar data-fetch workflow for the s7 D1 cross-asset Donchian research line that does NOT depend on Databento. The workflow uses yfinance (Yahoo Finance) only, with a narrow scope of four daily-bar ETF series chosen to proxy the four asset families the parent spec uses (equity index, bonds, metals, energy). This plan does not replace the Databento path; it adds a no-paid-data alternative that can be executed in a separately authorized turn.

## 2. Current repo reconciliation background

Prior execution authorization referenced:
- Commit a0981c5 (not in this repo's git log).
- Branch donchian_cross_asset (not in this repo; only master and chore/baseline-working-tree-2026-05-19 exist).
- Plan path docs/branch_donchian_cross_asset_step_02b_alt_vendor_data_fetch_plan.md (not present).

The sealed reconciliation report (a85b8fc684d00d8b90db7782e11ee3b0bd8fc81be50a4208ab36cfa3ff970514) classified the divergence as REFERENCES_INCORRECT. Existing Donchian work in this repo uses the s7 D1 naming convention. This plan adopts the s7 D1 convention so the artifact actually lands here, with no branch creation and no remote dependency.

## 3. Relationship to existing s7 D1 cross-asset Donchian artifacts

This plan inherits scope context from docs/s7_d1_cross_asset_donchian_spec.md (the Tier-N spec draft). It does NOT modify that spec, the runner harness, or any sealed P1 through P4 artifact. The fetched data this plan describes is for an alternate-vendor research path that uses ETF proxies on daily bars, not the spec's Databento continuous-front-month futures (NQ.c.0, GC.c.0, ZN.c.0, CL.c.0). The two paths are complementary research vendors and may produce different numbers; that is expected and is the entire point of an alternate-vendor check.

## 4. Why Databento path is not used for this alternate-vendor fetch

- Databento is the parent spec's primary vendor; this plan is explicitly the alternative.
- A no-paid-data fallback is required so the research line can proceed at zero data spend.
- Avoids any access to DATABENTO_API_KEY during this workflow.
- Keeps the Databento path independently versionable; nothing in this plan touches Databento code, configuration, cache, or vendor-docs directories.

## 5. Vendor selection (yfinance / Yahoo Finance only)

- Vendor: yfinance (PyPI package) only.
- Provider: Yahoo Finance.
- No vendor substitution mid-fetch; if yfinance fails the gate per section 14, HALT.
- yfinance requires no API key; no key file is read, written, or referenced.
- No alternate provider is permitted as a silent fallback inside this fetch.

## 6. Symbols (locked to exactly four)

- SPY (S&P 500 ETF; equity-index proxy for NQ-family).
- TLT (20+ year Treasury Bond ETF; bond proxy for ZN-family).
- GLD (Gold ETF; metals proxy for GC-family).
- USO (United States Oil Fund; energy proxy for CL-family).

No other symbol is permitted in this fetch. No micro/full-size pair selection. No survivorship-cherry-pick swap of any symbol for a higher-performing alternative.

## 7. Frequency

Daily bars only. No intraday. No minute-resolution. No weekly aggregation. yfinance interval parameter must be "1d".

## 8. Target window

Start: 2014-01-01
End:   2026-05-25

Both dates inclusive at daily-bar granularity. Yahoo Finance end-date conventions are vendor-specific; the execution turn must accept Yahoo's actual returned coverage and verify it spans the window. Any short-coverage symbol HALTs per section 14.

## 9. Minimum required span

At least 10 calendar years per symbol. NOT RELAXED under any circumstance. A symbol returning less than 10 years HALTs the fetch for that symbol with no auto-extend, no auto-fill, no auto-truncate-to-floor.

## 10. Storage path

data/s7_d1_cross_asset_donchian/raw/

This path is created only if it does not already exist and only by the execution turn (not by this plan-authoring turn). The directory is a leaf inside data/; the data/ directory itself is untracked in this repo's git state, which is intended.

## 11. Filename convention

<SYMBOL>_1d_<START>_<END>.csv

Where SYMBOL is one of SPY, TLT, GLD, USO; START is 2014-01-01; END is 2026-05-25.

Concrete expected filenames:
- SPY_1d_2014-01-01_2026-05-25.csv
- TLT_1d_2014-01-01_2026-05-25.csv
- GLD_1d_2014-01-01_2026-05-25.csv
- USO_1d_2014-01-01_2026-05-25.csv

## 12. Expected outputs

- Exactly four CSV files (one per symbol) at the storage path with the locked filename convention.
- Exactly one fetch_run_manifest.json at the same storage path.

No additional files. No supplementary CSVs. No log files in this directory. No backup copies. No subdirectories.

## 13. yfinance normalization rules

Output CSV columns and order, locked:

date,open,high,low,close,adj_close,volume

Rules:
- Date column from yfinance must be normalized to a string in YYYY-MM-DD form, no time component, no timezone suffix.
- Open, High, Low, Close, Volume columns from yfinance must be renamed to lowercase: open, high, low, close, volume.
- yfinance Adj Close must be renamed to adj_close and kept as a separate column.
- adj_close must NOT replace close. Both columns must be present and distinct.
- Duplicate dates HALT. No auto-dedupe is allowed. If yfinance returns duplicate date rows for any reason, the fetch HALTs for that symbol with no silent merge.
- Column order is locked exactly as above. Any reordering HALTs.

## 14. Vendor-risk checks (R1 through R8)

R1. yfinance importability and version recorded.
- Execution turn must perform `import yfinance` and record the package version into the manifest.
- ImportError HALTs the fetch.

R2. Empty data HALT.
- A symbol returning an empty DataFrame from yfinance.download HALTs the fetch for that symbol with no retry beyond R7.

R3. Reasonable close range check.
- For each symbol, the minimum close must be strictly positive and the maximum close must be finite.
- Per-symbol close ranges that are obviously implausible (zero, negative, NaN, infinite, or outside any reasonable historical band for SPY/TLT/GLD/USO) HALT the fetch.

R4. Zero-volume run detection.
- A run of N consecutive zero-volume trading days inside the requested window where N exceeds a documented threshold (recommended: 5) indicates a vendor data gap and HALTs the fetch.

R5. Adjusted-vs-unadjusted divergence check.
- Compute the per-symbol divergence between close and adj_close across the full window.
- Document the divergence in the manifest. No automatic adjustment is permitted.

R6. One-second throttle between symbols.
- Execution must wait at least 1.0 second between successive symbol fetches.

R7. One retry with 5-second delay only.
- A network exception on a symbol retries exactly once after a 5-second sleep.
- A second exception HALTs the fetch for that symbol.

R8. HALT on network exception.
- Beyond the single R7 retry, any uncaught network exception HALTs the fetch (no third attempt, no vendor substitution, no silent skip).

## 15. API/key safety

- yfinance requires no API key; no key is read, set, or referenced in this workflow.
- Databento must not be called by this workflow.
- DATABENTO_API_KEY must not be accessed by this workflow.
- The literal expression os.environ["DATABENTO_API_KEY"] must not appear in execution-turn code or be evaluated at runtime.
- No environment variable that begins with DATABENTO_ may be read by this workflow.
- The api_key_safety_confirmation manifest field (section 16) is an attestation, not a permission.

## 16. Manifest schema (fetch_run_manifest.json)

Required fields, all populated by the execution turn:

- yfinance_version: string (e.g. "0.2.x").
- run_started_utc: ISO 8601 timestamp.
- run_finished_utc: ISO 8601 timestamp.
- symbols_requested: ["SPY","TLT","GLD","USO"] (locked order).
- start_date: "2014-01-01".
- end_date:   "2026-05-25".
- frequency: "1d".
- storage_path: "data/s7_d1_cross_asset_donchian/raw/".
- per_symbol: object keyed by symbol; each value contains:
  - csv_path
  - csv_sha256
  - rows
  - first_date
  - last_date
  - years_covered
  - adjusted_close_present (boolean)
  - min_close, max_close
  - zero_volume_run_max
  - adjusted_vs_unadjusted_max_divergence
- api_key_safety_confirmation:
  - yfinance_requires_no_api_key: true
  - databento_called: false
  - databento_api_key_accessed: false
  - os_environ_DATABENTO_API_KEY_referenced: false
- donchian_isolation_confirmation:
  - no_donchian_signal_computed: true
  - no_simulator_run: true
  - no_backtest_run: true
- no_orb_mutation_confirmation:
  - no_orb_branch_artifact_mutated: true
  - no_orb_step_30_cost_constants_mutated: true
- vendor_risk_check_results: per-symbol object mapping R1..R8 to pass/fail outcomes.

The manifest must not contain raw API keys, raw secrets, or any os.environ snapshot dump.

## 17. Validation gates

The execution turn must verify, in order:

V1. All four CSV files exist at the locked paths.
V2. Each CSV passes yfinance normalization rules (section 13).
V3. Each CSV covers at least 10 years (section 9).
V4. Each CSV has no duplicate dates (R-rule supports this; V3 is a separate post-write check).
V5. The fetch_run_manifest.json exists at the locked path.
V6. The manifest schema matches section 16 (all required fields present).
V7. api_key_safety_confirmation block is present and all four sub-flags are set as specified.
V8. donchian_isolation_confirmation block is present.
V9. no_orb_mutation_confirmation block is present.
V10. csv_sha256 per symbol matches the file on disk.

A failing gate HALTs the fetch run; partial outputs are kept and a separate authorization is required to recover.

## 18. HALT conditions

The fetch HALTs on any of:
- R1 ImportError.
- R2 empty data.
- R3 implausible close range.
- R4 zero-volume run exceeding threshold.
- R7 second network exception.
- R8 uncaught network exception.
- Duplicate dates for a symbol (section 13).
- Symbol coverage less than 10 years (section 9).
- Any V-gate failure (section 17).
- Any attempt to substitute the vendor.
- Any attempt to call Databento.
- Any attempt to access DATABENTO_API_KEY or os.environ DATABENTO_API_KEY.
- Any attempt to mutate an ORB branch artifact.
- Any attempt to compute a Donchian signal or run a simulator.

## 19. What execution is NOT allowed to do

The execution turn must NOT:
- Compute Donchian signals on the fetched data.
- Run a backtest, simulator, or paper-trade loop.
- Make any live order, paper-trade, or broker call.
- Modify ORB branch artifacts.
- Modify Step 30 cost constants.
- Modify source code beyond a focused fetch script if explicitly permitted by the execution authorization.
- Modify CLAUDE.md, docs/decisions.md, RUNBOOK, pipeline_manifest, or .gitignore.
- Switch branches or create branches.
- Use the instruction phrase "fetch data now" as an active directive (this phrase appears here only as forbidden text).
- Treat the phrase "authorize Step 02b execution" as a completed or current action (this phrase appears here only to mark a future-state authorization gate).

## 20. Execution acceptance checklist

Before the execution turn is considered acceptable to issue:
- A separate operator authorization explicitly authorizes execution of this plan.
- The plan path is exactly docs/s7_d1_cross_asset_donchian_step_02b_alt_vendor_data_fetch_plan.md.
- The storage path is exactly data/s7_d1_cross_asset_donchian/raw/.
- All four symbols are listed exactly (SPY, TLT, GLD, USO).
- The start and end dates are exactly 2014-01-01 and 2026-05-25.
- The vendor is exactly yfinance / Yahoo Finance.
- The defensive spending cap remains 5.00 USD; expected cost is 0.00 USD; the cap is not raised.
- No Databento path is co-active.
- The execution turn produces only the four CSV files and the manifest; no other file write is permitted.
- The execution turn emits an execution report under reports/ describing yfinance_version, symbols fetched, rows per CSV, date range per CSV, csv sha256s, validation status, manifest path, and the no-Databento / no-network-beyond-Yahoo attestations.

## 21. Next authorization required for execution

A future operator authorization is required to proceed beyond this plan. That authorization must reference this plan by path. This plan is the source of truth; the execution turn is not pre-authorized by the plan itself.

Future expected status on execution turn (informational; not granted here):

STEP_02B_YFINANCE_DATA_FETCH_EXECUTED
FOUR_DAILY_CSVS_WRITTEN
FETCH_RUN_MANIFEST_WRITTEN
NO_DATABENTO_CALL
NO_DATABENTO_API_KEY_ACCESS
NO_BACKTEST
NO_DONCHIAN_SIGNAL_COMPUTED
NO_SIMULATOR_RUN
NO_ORB_BRANCH_MUTATION
NO_LIVE_TRADING

----

End of plan. Plan-authoring turn only. No fetch. No code execution. No Databento. No network beyond what this plan describes for the future execution turn. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES.

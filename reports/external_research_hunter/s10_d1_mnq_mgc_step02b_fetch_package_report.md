# s10 D1 MNQ+MGC -- Step 02b Operator-Side Databento Fetch Package -- Report

Status: PACKAGE_AUTHORED_NOT_RUN (controller did not run the fetch; the operator runs it in a separate local shell session).
Authored: 2026-05-26
Authorization: "Authorize s10 D1 MNQ+MGC Step 02b operator-side Databento fetch package."

Candidate: `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`
Sealed spec reference: `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md` (commit `9040429`)

---

## 1. What this package contains

Four artifacts authored this turn:

| # | Artifact | Path | Purpose |
|---|---|---|---|
| 1 | Fetch script | `tools/operator_side/s10_d1_mnq_mgc_step02b_fetch_databento.py` | Operator-side Python script that fetches MNQ.c.0 + MGC.c.0 ohlcv-1d from Databento `GLBX.MDP3` over the sealed-spec date range and writes raw CSV + manifest JSON |
| 2 | Operator runbook | `docs/s10_d1_mnq_mgc_step02b_operator_fetch_runbook.md` | Step-by-step PowerShell commands for the operator, including safe API-key handling, expected output, paste-back checklist, and abort conditions |
| 3 | Package report MD | `reports/external_research_hunter/s10_d1_mnq_mgc_step02b_fetch_package_report.md` | This document; describes the package, validation results, and next authorization |
| 4 | Package report JSON | `reports/external_research_hunter/s10_d1_mnq_mgc_step02b_fetch_package_report.json` | Machine-readable companion to (3); includes sha256 anchors and structured boundary attestations |

The controller did NOT run the fetch script. The controller did NOT access `DATABENTO_API_KEY`. The controller did NOT call Databento. The controller did NOT inspect OOS performance.

---

## 2. Fetch script summary

| Field | Value |
|---|---|
| Path | `tools/operator_side/s10_d1_mnq_mgc_step02b_fetch_databento.py` |
| sha256 | `e8cc33ae37b3431ee673c1b4374006472b2586a1a3711209dac5dd2cf354dedc` |
| Bytes | 10,408 |
| Lines | 296 |
| `py_compile` | **PASS** |
| ASCII-only | YES (0 non-ASCII chars) |
| Required strings present | 25 of 25 |
| `import yfinance` | ABSENT |
| `import strategy_lab` | ABSENT |
| `review_queue.json` mutation | ABSENT (the string appears once in a self-attestation docstring, with no `open()`/`json.dump()`/`.write()`/`.append()` call against it) |
| `idea_memory.write/append` | ABSENT |
| `SetLiveMode` / `SetBrokerageModel` / `DeployAlgorithm` | ABSENT |
| Backtest / simulator / signal / compute_signal / score_pnl function defs | ABSENT |
| `path=` kwarg in `get_range()` call | ABSENT (the string `path=` appears once inside a `# NOTE` comment that explicitly explains the kwarg is NOT passed; the actual `get_range()` call has 6 kwargs: `dataset`, `symbols`, `schema`, `start`, `end`, `stype_in`) |
| Key handling | reads `DATABENTO_API_KEY` from environment via `os.environ.get(...)`; key stored in local variable only; passed as `key=key` kwarg to `databento.Historical()`; never printed, logged, hashed, written, or otherwise exposed |
| Print discipline | only safe summary lines per symbol (`symbol | row_count | first_ts | last_ts | sha256 | bytes`) and the manifest path + sha; no row content, no API payloads, no return / sharpe / pnl numbers |

---

## 3. Locked fetch parameters (carried byte-equivalent from sealed spec)

| Field | Locked value |
|---|---|
| `SEALED_SPEC_COMMIT` | `9040429` |
| `DATASET` | `GLBX.MDP3` |
| `SCHEMA` | `ohlcv-1d` |
| `STYPE_IN` | `continuous` |
| `SYMBOLS` | `("MNQ.c.0", "MGC.c.0")` -- exactly two; `MCL.c.0` explicitly excluded |
| `START_DATE_INCLUSIVE` | `2019-05-13` |
| `END_DATE_INCLUSIVE` | `2025-12-30` |
| `IS_WINDOW_START` | `2019-05-13` (used by future IS-phase modules) |
| `IS_WINDOW_END` | `2023-12-29` |
| `OOS_WINDOW_START_LOCKED_NOT_INSPECTED` | `2024-01-02` |
| `OOS_WINDOW_END_LOCKED_NOT_INSPECTED` | `2025-12-30` |
| `APPROVED_OUTPUT_DIR` | `data/s10_d1_mnq_mgc_databento_long_history/raw` (validated via `Path.resolve()` + `relative_to()` before write) |
| `DEFAULT_OUTPUT_FILENAMES["MNQ.c.0"]` | `MNQ_c_0_ohlcv_1d_20190513_20251230.csv` |
| `DEFAULT_OUTPUT_FILENAMES["MGC.c.0"]` | `MGC_c_0_ohlcv_1d_20190513_20251230.csv` |
| `MANIFEST_FILENAME` | `s10_d1_mnq_mgc_step02b_fetch_manifest.json` |
| `REQUIRED_CSV_COLUMNS` | `("ts_event", "open", "high", "low", "close", "volume")` |

OOS-window dates are written into the manifest as `oos_window_start_LOCKED_NOT_INSPECTED` / `oos_window_end_LOCKED_NOT_INSPECTED`; the script does NOT slice, sort, summarize, score, or otherwise inspect the OOS rows. The OOS rows are fetched as raw data only because the sealed spec date range covers both windows; downstream IS-phase modules will structurally exclude OOS rows.

---

## 4. Fail-closed conditions in the script

| Exit code | Condition |
|---|---|
| 2 | `DATABENTO_API_KEY` not set in environment |
| 3 | Unknown symbol attempted (only `MNQ.c.0` and `MGC.c.0` permitted) |
| 4 | Resolved output path falls outside `APPROVED_OUTPUT_DIR` |
| 5 | DataFrame missing any of the 6 required columns OR `ts_event` missing after `reset_index()` |
| 6 | `databento` python client not installed |
| 7 | Any symbol returns 0 rows over the locked date range |

Successful exit code: `0`. No other exit code paths exist.

---

## 5. Runbook summary

| Section | Contents |
|---|---|
| Pre-flight | Confirm Databento account + python env + script path |
| Setting `DATABENTO_API_KEY` | PowerShell `$env:DATABENTO_API_KEY = "<key>"`; never paste to chat; never commit; never `echo`; verify-without-print idiom provided |
| Running the fetch | `python .\tools\operator_side\s10_d1_mnq_mgc_step02b_fetch_databento.py` from repo root |
| Expected output files | 2 CSVs + 1 manifest JSON in approved dir |
| Safe paste-back | per-symbol summary lines + manifest path + manifest sha |
| Forbidden paste-back | API key, row content, sharpe / pnl / return numbers, OOS analysis, raw API payloads |
| Explicit warnings | 6 numbered warnings covering key exposure, OOS inspection, script modification, cache file path, symbol modification, date range modification |
| Abort conditions | 5 numbered abort triggers |
| Post-run authorization | next operator phrase: `Authorize s10 D1 MNQ+MGC Step 02c raw-data audit only.` |

---

## 6. Validation results (all checks PASS)

| Check | Result |
|---|---|
| `py_compile` on fetch script | **PASS** |
| ASCII-only (script + runbook + this report MD) | **PASS** |
| Static scan: no forbidden key printing/logging in script | **PASS** |
| Static scan: no `yfinance` import in script | **PASS** |
| Static scan: no `review_queue` mutation call in script | **PASS** (substring only in self-disclaimer docstring) |
| Static scan: no `strategy_lab` import in script | **PASS** |
| Static scan: no signal/backtest/simulator function definitions in script | **PASS** |
| Static scan: no `SetLiveMode`/`SetBrokerageModel`/`DeployAlgorithm` in script | **PASS** |
| Static scan: `get_range()` has no `path=` kwarg in the actual call (string appears only in a `# NOTE` comment) | **PASS** |
| Required-string presence in script (25 distinct strings checked) | **PASS** (25 of 25) |
| OOS-window mentions in script are confined to metadata / comments / manifest fields | **PASS** |
| Fetch NOT run by controller this turn | **PASS** (no Databento call; no key access; no network) |

---

## 7. Boundaries held this PACKAGE turn

| Boundary | Status |
|---|---|
| Step 02b PACKAGE ONLY (no fetch run) | met |
| `DATABENTO_API_KEY` not accessed by controller | met |
| Key not printed, logged, hashed, stored, or inspected | met |
| No Databento call from controller | met |
| No backtest | met |
| No simulator run | met |
| No signal computation | met |
| No OOS inspection | met |
| No OOS return summary | met |
| No strategy performance evaluation | met |
| `review_queue.json` not mutated | met |
| Strategy Lab not run | met |
| No candidate promotion | met |
| No live trading | met |
| `brain_memory/projects/trading_bot/lessons.md` not modified or staged | met (dirty + unstaged; preserved) |
| No branch change, no branch creation, no git push | met |
| Only the 4 named package files authored | met |

---

## 8. Files written this PACKAGE turn

| File | Bytes | sha256 |
|---|---|---|
| `tools/operator_side/s10_d1_mnq_mgc_step02b_fetch_databento.py` | 10,408 | `e8cc33ae37b3431ee673c1b4374006472b2586a1a3711209dac5dd2cf354dedc` |
| `docs/s10_d1_mnq_mgc_step02b_operator_fetch_runbook.md` | (recorded in JSON companion) | (recorded in JSON companion) |
| `reports/external_research_hunter/s10_d1_mnq_mgc_step02b_fetch_package_report.md` | (this file) | (this file) |
| `reports/external_research_hunter/s10_d1_mnq_mgc_step02b_fetch_package_report.json` | (recorded in JSON itself) | (recorded in JSON itself) |

No other repository file is modified. The `brain_memory/projects/trading_bot/lessons.md` dirty + unstaged state from prior controller-session appends remains untouched.

---

## 9. Status carried forward (UNCHANGED by this package)

| Field | Value |
|---|---|
| Trading | `PAUSED` |
| Live mode | `BLOCKED_AT_6_GATES` |
| FRC | `NEVER_GRANTED` |
| `no_strategy_optimization_authorized` | TRUE |
| `no_live_trading` | TRUE |
| `no_strategy_lab_promotion` | TRUE |
| `no_review_queue_mutation` | TRUE |
| `no_brokerage_connection` | TRUE |
| `no_external_network` (controller side; runtime invariant) | TRUE |
| `no_databento` (controller side this turn) | TRUE |
| `no_oos_inspection_by_this_script` | TRUE |
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | permanent |

---

## 10. Next-step authorization scope

The next operator action is to RUN the fetch script in their local shell. The exact command sequence is in the runbook:

```powershell
cd C:\SPARTA_BRAIN
$env:DATABENTO_API_KEY = "<paste-your-databento-key-here-locally>"
python .\tools\operator_side\s10_d1_mnq_mgc_step02b_fetch_databento.py
```

After a successful fetch and safe paste-back of the per-symbol summary lines + manifest sha, the next controller authorization is:

```
Authorize s10 D1 MNQ+MGC Step 02c raw-data audit only.
```

Step 02c is local-only (no Databento call, no network) and consumes the manifest JSON written by Step 02b to validate row counts, sha256 anchors, date-window coverage, and required-column presence. No OOS inspection occurs at Step 02c either.

If the fetch fails closed at any exit code (2-7), the operator pastes back the safe summary line plus the exit code only. The controller authors a parking memo under separate authorization, NOT a parameter tweak.

---

End of report. Package authored, not run. Operator runs the fetch in their local shell. Controller did not access `DATABENTO_API_KEY`. Controller did not call Databento. Controller did not inspect OOS. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC NEVER_GRANTED.

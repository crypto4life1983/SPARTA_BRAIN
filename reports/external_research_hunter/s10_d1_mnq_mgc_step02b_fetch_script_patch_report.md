# s10 D1 MNQ+MGC Step 02b Fetch Script Patch Report

Status: PATCH_AUTHORED_NOT_RUN (controller patched the script; the operator reruns the fetch in their local shell).
Authored: 2026-05-26
Authorization: "Authorize s10 D1 MNQ+MGC Step 02b fetch script dataframe-normalization patch."

Candidate: `s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history`
Sealed spec reference: `docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md` (commit `9040429`)
Original fetch package: commit `a8df18b` (`Add s10 D1 MNQ MGC Step 02b Databento fetch package`).

---

## 1. Problem statement

On the first operator-side run, the Databento fetch:

- successfully read `DATABENTO_API_KEY` from the local environment (no key was pasted into chat);
- successfully reached the Databento Historical endpoint and initiated the MNQ.c.0 fetch;
- emitted two non-fatal warnings before fail-closing:
  - `DeprecationWarning: datetime.utcnow()` (from the script's manifest-timestamp call);
  - `BentoWarning: reduced quality days including 2020-02-27, 2020-02-28, 2020-06-30` (from the Databento client; flags days where the underlying CME tick feed was incomplete or reconstructed);
- fail-closed with exit code 5: `Output DataFrame missing required columns ['ts_event']; fail-closed.`

The fail-closed condition correctly halted progression. The root cause is a DataFrame shape / column-normalization issue inside the script, not a data-availability or vendor failure -- Databento returned the MNQ.c.0 daily bars, but the resulting DataFrame's timestamp was emitted as a (possibly unnamed) datetime index rather than as a column literally named `ts_event`.

## 2. Root cause analysis

Pre-patch `_write_csv_via_pandas` flow:

```
df = data.to_df()
missing = [c for c in REQUIRED_CSV_COLUMNS if c not in df.columns]   <- CHECK HAPPENS HERE
if missing:
    sys.exit(5)                                                       <- FAIL-CLOSED FIRES HERE
df = df.reset_index() if "ts_event" not in df.columns else df         <- RECOVERY ATTEMPT NEVER REACHED
```

The required-column check ran BEFORE the `reset_index()` recovery attempt. When Databento's `to_df()` returns the timestamp as an index (named `ts_event` OR unnamed), `df.columns` does NOT contain `ts_event` at the moment of the check, so the script fail-closes immediately and never gets a chance to surface the index as a column.

Secondary issues:

- `datetime.utcnow()` is deprecated in Python 3.12+; the manifest's `fetch_run_utc` field used it.
- The Databento `BentoWarning: reduced quality days` is an operator-facing data-quality signal that the Step 02b runbook did not previously document; it must be captured by the operator and forwarded to Step 02c raw-data audit.

## 3. Patch summary

| Change | Type | Location |
|---|---|---|
| Add `_normalize_dbn_dataframe(df)` helper | NEW function | `_write_csv_via_pandas` adjacent (before it) |
| Call `_normalize_dbn_dataframe(df)` BEFORE the required-column check | MODIFY | `_write_csv_via_pandas` body |
| Update fail-closed message to mention "after normalization" | MODIFY | `_write_csv_via_pandas` body |
| Replace `datetime.utcnow().isoformat() + "Z"` with `datetime.now(timezone.utc).isoformat()` | MODIFY | `main()` manifest-build block |
| Add `timezone` to `datetime` import | MODIFY | top-level imports |
| Document expected non-fatal warnings + reduced-quality-day handling | NEW section in runbook | `docs/s10_d1_mnq_mgc_step02b_operator_fetch_runbook.md` section 4.1 |
| Document rerun-after-patch quick reference | NEW section in runbook | runbook section 0 |
| Authorize this patch report | NEW file | `reports/external_research_hunter/s10_d1_mnq_mgc_step02b_fetch_script_patch_report.md` + `.json` |

## 4. Normalization helper -- design

```
def _normalize_dbn_dataframe(df):
    # Case 1: ts_event already a column -> return as-is.
    # Case 2: index has a name; reset_index surfaces it as a column.
    #         If reset_index produced ts_event, return it.
    # Case 3: index unnamed; reset_index produced 'index' column.
    #         Safe rename only if 'index' dtype is datetime64 AND
    #         no ambiguous alternative exists.
    # Fallback: return df2 (post reset_index) and let caller's
    #          required-column check fail-closed if ts_event still missing.
```

Defensive properties:

- **Idempotent**: if `ts_event` is already a column, the function returns the DataFrame unchanged.
- **Conservative renaming**: only renames the surfaced `index` column to `ts_event` when the dtype is datetime-like (`pd.api.types.is_datetime64_any_dtype`). No string-name guessing on non-datetime columns.
- **Fail-closed on ambiguity**: returns the partially-normalized DataFrame and defers to the caller's required-column check; the caller still exits 5 if `ts_event` cannot be recovered.
- **No row content access**: the helper inspects column names, index name, and a single dtype check. It never reads, prints, or hashes row values.

## 5. Patched fetch script -- post-patch artifact

| Field | Value |
|---|---|
| Path | `tools/operator_side/s10_d1_mnq_mgc_step02b_fetch_databento.py` |
| sha256 (pre-patch) | `e8cc33ae37b3431ee673c1b4374006472b2586a1a3711209dac5dd2cf354dedc` |
| sha256 (post-patch) | `9269a778c501bc9c45c11760a38610665d9c3008dfa3b64a2c9e5316f110683b` |
| Bytes (pre-patch) | 10,408 |
| Bytes (post-patch) | 12,414 |
| Lines (post-patch) | 348 |
| `py_compile` (post-patch) | **PASS** |
| ASCII-only (post-patch) | YES (0 non-ASCII chars) |

## 6. Validation results -- all PASS

| Check | Pre-patch | Post-patch |
|---|---|---|
| `py_compile` | PASS | **PASS** |
| ASCII-only | PASS | **PASS** |
| `datetime.utcnow()` absent | NO (present) | **YES (replaced with `datetime.now(timezone.utc)`)** |
| `timezone` imported | NO | **YES** |
| `_normalize_dbn_dataframe` function defined | NO | **YES** |
| `_normalize_dbn_dataframe` called before required-column check | NO | **YES** |
| Fail-closed message mentions "after normalization" | NO | **YES** |
| `import yfinance` | absent | **absent** |
| `import strategy_lab` | absent | **absent** |
| `idea_memory.write` / `idea_memory.append` | absent | **absent** |
| `SetLiveMode` / `SetBrokerageModel` / `DeployAlgorithm` | absent | **absent** |
| `compute_signal` / `run_backtest` / `simulate` / `evaluate_strategy` / `score_pnl` function defs | absent | **absent** |
| `path=` kwarg in actual `get_range()` call (substring only in `# NOTE` comment) | absent | **absent** |
| `DATABENTO_API_KEY` key-misuse patterns (print/log/hash/write) | absent | **absent** |
| Controller-side Databento call this turn | NO | **NO** |
| Controller-side `DATABENTO_API_KEY` access this turn | NO | **NO** |
| Controller-side fetch run this turn | NO | **NO** |
| OOS inspection in script or this turn | NO | **NO** |
| Backtest / simulator / signal computation in script or this turn | NO | **NO** |
| `review_queue.json` mutation | NO | **NO** |
| Strategy Lab promotion | NO | **NO** |
| Live trading | NO | **NO** |

## 7. Reduced-quality-day handling (documented; not enforced by script)

The Databento client may emit `BentoWarning: reduced quality days including <YYYY-MM-DD>, ...` for days where the underlying CME tick feed was incomplete or reconstructed. The operator's first run flagged at minimum: `2020-02-27`, `2020-02-28`, `2020-06-30`.

Decisions made by this patch:

- The patched script does NOT modify the date range (sealed scope: `2019-05-13 -> 2025-12-30`).
- The patched script does NOT exclude reduced-quality days from the CSV (preserving full sealed-spec fidelity).
- The patched script does NOT print or process the warning text directly.
- The runbook now documents that the operator MUST capture the warning text safely (copy the line; no row content) and forward it to **Step 02c raw-data audit**, which applies the sealed-spec DR9 thresholds (`DR9_MIN_PCT_EXPECTED_TRADING_DAYS = 0.95`, `DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN = 0.30`, `DR9_MAX_MISSING_OBSERVATIONS = 5`, `DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD = 5`) to decide whether the flagged days breach DR9.

This division of labor is correct: Step 02b is fetch-only; Step 02c is audit. Reduced-quality flags are an audit concern, not a fetch-time mutation concern.

## 8. Boundaries held this PATCH turn

| Boundary | Status |
|---|---|
| PATCH ONLY (no fetch run) | met |
| `DATABENTO_API_KEY` not accessed by controller | met |
| Key not printed, logged, hashed, stored, or inspected | met |
| No Databento call from controller | met |
| No backtest | met |
| No simulator run | met |
| No signal computation | met |
| No OOS inspection | met |
| No OOS return summary | met |
| `review_queue.json` not mutated | met |
| Strategy Lab not run | met |
| No candidate promotion | met |
| No live trading | met |
| `brain_memory/projects/trading_bot/lessons.md` not modified or staged | met (dirty + unstaged; preserved) |
| No branch change, no branch creation, no git push | met |
| Patched files only in approved scope | met (4 files: script + runbook + this report MD + companion JSON) |

## 9. Files modified or added this PATCH turn

| File | Action | sha256 (post-patch) |
|---|---|---|
| `tools/operator_side/s10_d1_mnq_mgc_step02b_fetch_databento.py` | MODIFIED | `9269a778c501bc9c45c11760a38610665d9c3008dfa3b64a2c9e5316f110683b` |
| `docs/s10_d1_mnq_mgc_step02b_operator_fetch_runbook.md` | MODIFIED (sections 0 + 4 + 4.1 added) | (recorded in companion JSON) |
| `reports/external_research_hunter/s10_d1_mnq_mgc_step02b_fetch_script_patch_report.md` | NEW (this file) | (recorded in companion JSON) |
| `reports/external_research_hunter/s10_d1_mnq_mgc_step02b_fetch_script_patch_report.json` | NEW (companion JSON) | (recorded in itself) |

No other repository file is modified. `lessons.md` dirty + unstaged state preserved.

## 10. Status carried forward (UNCHANGED by this patch)

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
| `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` | permanent |

## 11. Next-step authorization scope

The next operator action is to **rerun the patched fetch script** in their local shell. The exact command is in `docs/s10_d1_mnq_mgc_step02b_operator_fetch_runbook.md` section 0 (Rerun-after-patch quick reference):

```powershell
cd C:\SPARTA_BRAIN
$env:DATABENTO_API_KEY = "<paste-your-databento-key-here-locally>"
python .\tools\operator_side\s10_d1_mnq_mgc_step02b_fetch_databento.py
```

After a successful fetch and safe paste-back of the per-symbol summary lines + manifest sha + the reduced-quality-day warning text (no row content), the next controller authorization is:

```
Authorize s10 D1 MNQ+MGC Step 02c raw-data audit only.
```

If the rerun fails again at any exit code 2-7, the operator pastes back the safe summary line + exit code only; the controller assesses whether a second patch is warranted (e.g., a different normalization edge case) or whether the candidate should be parked under a data-availability finding.

---

End of patch report. Controller patched the script and updated the runbook; controller did not run the fetch. No Databento call. No `DATABENTO_API_KEY` access. No live trading. Trading remains PAUSED. Live remains BLOCKED_AT_6_GATES. FRC NEVER_GRANTED.

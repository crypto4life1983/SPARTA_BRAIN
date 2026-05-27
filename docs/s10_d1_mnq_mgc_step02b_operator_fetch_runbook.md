# s10 D1 MNQ+MGC Step 02b -- Operator-Side Databento Fetch Runbook

Status: OPERATOR_RUNBOOK (operator runs this in their local shell outside the controller session).
Authored: 2026-05-26
Authorization: "Authorize s10 D1 MNQ+MGC Step 02b operator-side Databento fetch package."

Sealed spec reference: docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md (commit 9040429).
Fetch script reference: tools/operator_side/s10_d1_mnq_mgc_step02b_fetch_databento.py.

---

## 1. What this runbook does and does not do

| Action | This runbook |
|---|---|
| Provides operator-facing PowerShell commands | YES |
| Asks the operator to set DATABENTO_API_KEY in their local shell | YES (env-var only) |
| Asks the operator to run the fetch script | YES |
| Tells the operator what output files should appear | YES |
| Tells the operator what to paste back to the controller | YES (safe summary only) |
| Tells the operator what NOT to paste back | YES (key material; row content; OOS performance) |
| Calls Databento from the controller | NO |
| Reads DATABENTO_API_KEY from the controller | NO |
| Inspects OOS performance | NO |
| Computes signals, returns, Sharpe, or pnl | NO |

---

## 2. Pre-flight checklist (operator, local shell)

1. Confirm you have a Databento account with permission to read `GLBX.MDP3 ohlcv-1d`.
2. Confirm you have a Python 3 environment with `databento` and `pandas` installed:

   ```powershell
   python -c "import databento, pandas; print('ok')"
   ```

   If that fails:

   ```powershell
   pip install databento pandas
   ```

3. Confirm the sealed fetch script exists in your local repo:

   ```powershell
   Get-Item C:\SPARTA_BRAIN\tools\operator_side\s10_d1_mnq_mgc_step02b_fetch_databento.py | Select-Object FullName, Length
   ```

4. Confirm you are NOT in a live-trading shell. The fetch script is read-only against Databento Historical and does not touch any broker.

---

## 3. Setting DATABENTO_API_KEY safely

The fetch script reads `DATABENTO_API_KEY` from the environment ONLY. The controller does not have, and must not be given, the key.

In a PowerShell session, set it only for the current shell:

```powershell
$env:DATABENTO_API_KEY = "<paste-your-databento-key-here-locally>"
```

Important warnings:

- DO NOT paste the key into ChatGPT, Claude, this controller session, or any chat tool.
- DO NOT commit the key to git.
- DO NOT echo the key (`$env:DATABENTO_API_KEY` will print it; avoid doing so unless you are alone at the machine and verifying it is set).
- DO NOT save the key to a file inside the repo.
- DO NOT set it system-wide unless that is your existing pattern; per-shell `$env:` is preferred.

To verify it is set without printing the value:

```powershell
if ($env:DATABENTO_API_KEY) { Write-Host "DATABENTO_API_KEY is set (value hidden)" } else { Write-Host "NOT SET" }
```

---

## 4. Running the fetch

From the repo root (`C:\SPARTA_BRAIN`):

```powershell
cd C:\SPARTA_BRAIN
python .\tools\operator_side\s10_d1_mnq_mgc_step02b_fetch_databento.py
```

The script will:

1. Print the candidate id, dataset, schema, stype_in, date range, and symbols.
2. Read `DATABENTO_API_KEY` from environment (never echoes it).
3. Create the output directory `data/s10_d1_mnq_mgc_databento_long_history/raw/` if it does not exist.
4. Fetch MNQ.c.0 first, then MGC.c.0, each over the full sealed-spec date range (2019-05-13 through 2025-12-30).
5. Write one CSV per symbol plus one manifest JSON.
6. Print one safe summary line per symbol: `symbol | row_count | first_timestamp | last_timestamp | sha256 | bytes`.
7. Exit with code 0 on success; non-zero on any fail-closed condition.

Expected runtime: under a few minutes total for daily-bar data over ~6.6 years on 2 symbols. If you see no progress within 5 minutes, abort with `Ctrl+C` and verify your Databento permissions.

---

## 5. What files should appear after a successful run

```
data/
  s10_d1_mnq_mgc_databento_long_history/
    raw/
      MNQ_c_0_ohlcv_1d_20190513_20251230.csv
      MGC_c_0_ohlcv_1d_20190513_20251230.csv
      s10_d1_mnq_mgc_step02b_fetch_manifest.json
```

The manifest JSON contains, for each symbol: symbol, output_path, output_filename, row_count, size_bytes, sha256, first_timestamp, last_timestamp, dataset, schema, stype_in, start, end. Plus top-level fields: candidate_record_id, sealed_spec_commit_anchor, fetch_run_utc, IS/OOS markers, and the `boundaries_held` self-attestation block.

---

## 6. What to paste back to the controller (SAFE)

Paste back ONLY the following:

- The two safe-summary lines printed by the script (one per symbol), each of the form:

  ```
  MNQ.c.0: <row_count> rows; first=<ts> last=<ts>; sha256=<hex>; bytes=<int>
  MGC.c.0: <row_count> rows; first=<ts> last=<ts>; sha256=<hex>; bytes=<int>
  ```

- The manifest path and its sha256 (last printed line of the script):

  ```
  manifest written: data/s10_d1_mnq_mgc_databento_long_history/raw/s10_d1_mnq_mgc_step02b_fetch_manifest.json sha256=<hex> bytes=<int>
  ```

- Any non-zero exit code and the accompanying single error message line (the script writes one terse error line to stderr per fail-closed condition).

---

## 7. What to NEVER paste back (FORBIDDEN)

- DO NOT paste `DATABENTO_API_KEY` or any portion of it.
- DO NOT paste any row of CSV data (no OHLCV values, no timestamps beyond the first/last marker, no volume).
- DO NOT paste any Sharpe, return, PnL, drawdown, win-rate, or performance number derived from the CSV.
- DO NOT paste any OOS-window analysis. The OOS window (2024-01-02 -> 2025-12-30) is raw-fetched but LOCKED -- it is not to be inspected, summarized, scored, or used by any IS-phase logic until a separate `Authorize ... OOS inspection` operator turn (which does not exist yet).
- DO NOT paste any internal Databento response payload.
- DO NOT paste the script source modified post-seal (any modification voids the Step 02b sealed scope).

---

## 8. Explicit operator warnings

| Warning | Rationale |
|---|---|
| **DO NOT paste DATABENTO_API_KEY** anywhere outside your local shell. | API key exposure would breach your Databento account; the controller cannot help you rotate it. |
| **DO NOT inspect OOS performance.** | The IS-phase modules have not been built yet; OOS inspection at this stage would contaminate the diagnostic. |
| **DO NOT modify the fetch script** to add signal computation, returns analysis, or sharpe printing. | Step 02b is fetch-only by sealed scope; any addition voids the package. |
| **DO NOT cache `.dbn.zst` files** outside `data/s10_d1_mnq_mgc_databento_long_history/raw/`. | The script does not pass a `path=` kwarg to `get_range()` so the client returns in-memory DBNStore -- no cache file is written. If you observe a `.dbn.zst` written elsewhere, abort and verify. |
| **DO NOT run the script against any other symbol.** | The script hard-codes `MNQ.c.0` + `MGC.c.0` only; any modification of `SYMBOLS` voids the sealed scope. |
| **DO NOT widen the date range.** | The script hard-codes `2019-05-13 -> 2025-12-30`; any modification voids the sealed scope. |

---

## 9. Abort conditions (operator action required)

Abort the fetch if any of the following occurs:

- Any symbol returns 0 rows. The script fails closed and exits with code 7; do not paste back any partial results.
- A `.dbn.zst` cache file appears outside `data/s10_d1_mnq_mgc_databento_long_history/raw/`. Investigate why; do not proceed.
- The script prints any row content beyond the safe summary line. Investigate why; do not paste back row content.
- The script writes any file outside the approved output directory. Fail-closed exit code 4 should prevent this; if observed, investigate.
- The script accesses any other environment variable beyond `DATABENTO_API_KEY` (it should not). Verify with `Select-String DATABENTO_API_KEY .\tools\operator_side\s10_d1_mnq_mgc_step02b_fetch_databento.py`.

On any abort: do NOT modify the script; do NOT modify the runbook; report the abort condition to the controller in a fresh turn using only the safe summary line format.

---

## 10. Post-run controller authorization

After a successful fetch and a safe paste-back of the summary lines + manifest sha:

The next operator authorization in the controller pattern is:

```
Authorize s10 D1 MNQ+MGC Step 02c raw-data audit only.
```

The Step 02c phase is local-only (no Databento call, no network) and consumes the manifest JSON to validate row counts, sha256 anchors, date-window coverage, and required-column presence. No OOS inspection occurs at Step 02c either.

If the fetch failed:

- If row count = 0 for any symbol: do NOT proceed; the candidate is parked under a data-availability finding. Use the safe summary line and the script's exit code in the report-back; the controller will author a parking memo under separate authorization.
- If any boundary was breached (key exposure, OOS inspection, signal computation, etc.): report immediately in plain language; do NOT paste back any contaminated material.

---

## 11. Status carried forward (UNCHANGED by this runbook)

- Trading: PAUSED
- Live mode: BLOCKED_AT_6_GATES
- FRC: NEVER_GRANTED
- `DIAGNOSTIC_ONLY_NOT_LIVE_GRADE` advisory label permanent for this candidate
- `no_strategy_optimization_authorized`: TRUE
- All 19 RUNTIME_INVARIANTS at SEAL remain TRUE

This runbook is documentation only. It does not authorize live trading, brokerage connection, Strategy Lab promotion, OOS inspection, or production candidate registration. Each remains BLOCKED at separate phases.

---

End of runbook. Operator-side execution only. No controller-side Databento call. No DATABENTO_API_KEY access by the controller. No live trading. No Strategy Lab promotion. No review_queue mutation. No OOS inspection. No signal computation. No backtest. No simulator.

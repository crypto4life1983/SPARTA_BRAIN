# SPARTA Crypto-D1 Data QA Runtime Tool v1 — build report

> **Research-only. Local-only.** No data fetched. No exchange contacted. No
> order placed. No paper or live trading authorized. The tool reads files
> only from `--dataset-dir`; on missing data emits a `QA_DRAFT` or
> `QA_FAIL` report and never fabricates results. **`QA_PASS` is the
> deterministic outcome of mechanical checks; it does NOT imply
> profitability and does NOT authorize a backtest plan by itself.**

This bundle implements Bundle 14's QA / Freeze spec as executable code.
The tool consumes an operator-supplied frozen dataset directory, runs the
7 Bundle 14 QA check groups against it, and emits a `qa_report.json`
populating **all 26 fields** declared by Bundle 14's `QA_report_schema`,
plus a human-readable `qa_report.md`.

## Files changed

| Path | Purpose |
|---|---|
| `tools/crypto_d1_data_qa_runtime_tool.py` | Stdlib-only QA runtime tool. CLI: `validate-spec`, `show-spec`, `run --dataset-dir <PATH> --out-dir <PATH>`. Implements all 7 check groups + 6-status QA model + sha256 verification + 26-field report emitter. |
| `tests/test_crypto_d1_data_qa_runtime_tool.py` | 39 tests using `tmp_path` synthetic fixtures only. |
| `reports/crypto_d1_data_qa_runtime_tool_v1/report.md` | This build report. |
| `reports/crypto_d1_data_qa_runtime_tool_v1/report.json` | Build report (machine). |
| `brain_memory/projects/trading_bot/decisions.md` | Append-only Bundle 19 decision. |
| `brain_memory/projects/trading_bot/next_actions.md` | Append-only Bundle 20 candidate list. |

**Not touched:** `app.py`, `templates/*.html`, paper / live execution
code, sealed data, all 7 prior Crypto-D1 spec docs + the backtest
runner, all 16 prior validator tools, `tools/strategy_candidate_registry.py`
(the QA tool is code, not evidence; lane stays WATCH unchanged),
`tools/strategy_next_bundle.py` (no artificial selection nudge),
`local_secrets/`, `paper_trading/`, `lessons.md`,
`data/crypto_d1_research/` (NOT created; storage root appears only when
the operator manually places a real dataset).

## What the runner implements

### 7 QA check groups (Bundle 14)

| Group | What it checks |
|---|---|
| **A — manifest integrity** | `manifest.json` exists + parses; 35 required fields populated; pins `protocol_version` / `data_contract_version`; `research_lane = "crypto_d1_protocol"`; `market_type = "spot"`; `timeframe = "1d"`; `freeze_status ∈ {DRAFT, FROZEN}`; `QA_status` in declared model; `allowed_use` / `forbidden_use` present. |
| **B — timestamp** | No duplicate `(symbol, timestamp)`; no weekday-only calendar (24/7 required); missing days reconciled against manifest's `missing_day_policy`; UTC primary clock. |
| **C — OHLCV** | `high < low` is `FAIL`; `high >= max(open, close, low)`; `low <= min(open, close, high)`; OHLC positive; close not missing (parser enforces). |
| **D — volume** | `volume < 0` is `FAIL`; `volume == 0` flagged as `WARN` for 24/7 asset review. |
| **E — symbol / source** | BTC/ETH/SOL canonical mapping; `quote_currency` consistency per symbol (mismatch = `FAIL`); source consistency per symbol (mismatch = `WARN`); duplicate `(symbol, source, timestamp)` triplets rejected; row-level `source_id` enforced at parse. |
| **F — fee / slippage** | `fees.json` exists + parses; per-venue taker fee declared; slippage declared; spread proxy `WARN` if missing. **No PASS if fees or slippage missing.** |
| **G — freeze** | `freeze_status == FROZEN`; `CHECKSUMS.txt` present + **sha256-verified per file at runtime**; `FREEZE_RECORD.txt` present with `freeze_timestamp_utc` + ≥ 3 of 6 version pins; manifest's `row_count_actual` recorded. |

### 6-status QA model

`QA_DRAFT` (required input missing) · `QA_PASS` (all blocking pass, zero
warnings) · `QA_WARN` (blocking pass, ≥ 1 warning) · `QA_FAIL` (any
blocking failure) · `QA_BLOCKED` (manifest declares an external block) ·
`QA_RETIRED` (set externally only).

### 26-field `qa_report.json` emitter

Every emitted report populates exactly the 26 fields Bundle 14 declared:
`qa_report_id`, `dataset_id`, `dataset_version`, `manifest_version`,
`data_contract_version`, `protocol_version`, `generated_at`, `qa_status`,
`checks_run`, `checks_passed`, `checks_warned`, `checks_failed`,
`blocking_failures`, `warnings`, `row_count_observed`,
`missing_day_summary`, `duplicate_summary`, `timestamp_summary`,
`OHLCV_summary`, `volume_summary`, `fee_slippage_summary`,
`source_provenance_summary`, `freeze_summary`, `allowed_next_step`,
`forbidden_next_steps`, `safety_flags`.

Plus a `qa_report.md` rendering.

## Safety guarantees (enforced by tests)

- **Stdlib only** (AST scan; only `argparse`, `csv`, `dataclasses`,
  `datetime`, `hashlib`, `json`, `math`, `pathlib`, `sys`, `__future__`
  plus two in-repo stdlib-only validators
  `crypto_d1_qa_freeze_spec_check` and `crypto_d1_dataset_manifest_check`).
- **No network / broker / exchange / vendor / credentials / subprocess
  imports** (AST `Import` / `ImportFrom` scan).
- **No `os.environ` / `os.getenv` / `urlopen` / `api.telegram.org`** in
  non-docstring source.
- **No order-placement / paper-order / live-trading code paths** in
  non-docstring source (verb scan).
- **Seven safety flags pinned `False`** in every emitted `qa_report`'s
  `safety_flags`.
- **Read-only with respect to `--dataset-dir`.** The tool writes only to
  `--out-dir` (operator-chosen). Never auto-creates
  `data/crypto_d1_research/`.
- **No defaults for `--dataset-dir` / `--out-dir`.** Operator must
  explicitly opt in to specific paths.
- **`QA_PASS` is reserved for clean datasets but does NOT autoauthorize
  a backtest plan.** Per Bundle 14, `QA_PASS` is a PRECONDITION for a
  future backtest plan, not the authorization itself.
- **`QA_BLOCKED` from the manifest overrides** any otherwise-clean
  result.
- **Deterministic.** `qa_report_id` is sha256-derived from dataset bytes
  + tool / spec version pins; same input → same `qa_report_id`.
- **No fabrication on missing data.** Emits `QA_DRAFT` (dir doesn't
  exist) or `QA_FAIL` (dir exists but unusable) with explicit reason in
  `_audit_context.no_input_reason`.

## Tests run

```
python -m pytest tests/test_crypto_d1_data_qa_runtime_tool.py --rootdir=tests -q
→ 39 passed in 0.55s

python -m pytest <all 18 test files> --rootdir=tests -q
→ 509 passed in 4.41s
```

All 16 prior validators `validate: OK` — Bundles 4–18 unaffected.

## Was real local data found?

**No.** `data/crypto_d1_research/` does not exist. The runner-style
behavior (handle absent data via `QA_DRAFT` / `QA_FAIL`) is tested via
`test_missing_dataset_dir_emits_qa_draft` and
`test_empty_dataset_dir_emits_qa_fail`.

## Was any real QA run executed against real data?

**No.** Only `tmp_path` synthetic fixtures (deterministic CSV +
manifest + CHECKSUMS + FREEZE_RECORD + fees) generated inside the test
suite were used.

## How to run with operator-supplied local dataset

1. **Prepare dataset** (per Bundle 17 manual steps). The operator
   places under `<DATASET_DIR>`:
   - `BTC_daily.csv` (and optionally `ETH_daily.csv`, `SOL_daily.csv`).
   - `manifest.json` (must pass
     `tools/crypto_d1_dataset_manifest_check.py` extended for
     per-dataset use).
   - `CHECKSUMS.txt` (one `<sha256_hex>  <filename>` line per dataset
     file).
   - `FREEZE_RECORD.txt` (key:value lines with `freeze_timestamp_utc`,
     operator, and the 6 prior-bundle version pins).
   - `fees.json` (declaring per-venue taker fee + `slippage_bps` +
     optional `spread_proxy_bps`).
2. **Precondition check.**

   ```bash
   python tools/crypto_d1_data_qa_runtime_tool.py validate-spec
   ```

3. **Inspect the spec.**

   ```bash
   python tools/crypto_d1_data_qa_runtime_tool.py show-spec
   ```

4. **Run.**

   ```bash
   python tools/crypto_d1_data_qa_runtime_tool.py run \
       --dataset-dir <DATASET_DIR> \
       --out-dir     <OUT_DIR>
   ```

5. **Inspect reports.** `OUT_DIR` contains `qa_report.json` (26 required
   fields) and `qa_report.md`. **NEVER commit `OUT_DIR` contents unless
   explicitly authorized.**

6. **Iterate on failures.**
   - `QA_FAIL` → remediation requires a NEW `dataset_version` (per
     Bundle 13 freeze rules).
   - `QA_WARN` → operator attaches an acceptance note to the manifest
     before any backtest plan references the dataset.

## What happens if no data exists

The tool emits:
- `QA_DRAFT` if `--dataset-dir` doesn't exist (the dataset isn't even
  drafted yet).
- `QA_FAIL` with `blocking_failures = ["no .csv files in dataset_dir"]`
  if `--dataset-dir` exists but is empty.

JSON + MD reports are still written so the operator has a traceable
audit trail. **NO synthetic / fabricated metrics emitted.**

## Candidate registry status for crypto_d1 after build

**Unchanged from Bundle 18** — `status = WATCH`, `evidence_level = MIXED`,
`source_reports = 29`. Per Bundle 16 precedent, the QA tool is code, not
evidence; the registry's `extra_files` were not extended. Promotion to
ACTIVE still requires a future per-strategy backtest report PASS verdict
on REAL data plus an explicit operator decision.

## Recommended next bundle

- **Operator step (NOT a bundle):** the operator manually executes
  Bundle 17 steps 1–10, then runs the QA tool against the resulting
  dataset.
- **Crypto-D1 Baseline Results Report v1** (separately authorized; only
  AFTER operator has supplied data, the QA tool returns `QA_PASS` or
  accepted `QA_WARN`, AND the backtest runner has produced output;
  documents the operator-reviewed run + pins verdict + caveats. Spec
  bundle; Claude works.).
- **Crypto-D1 Backtest Runner v2 (future)** — walk-forward driver +
  per-family parameter-grid sweep + structured sensitivity sweep +
  per-strategy report emitter matching the full 27-field Bundle 15
  schema. (Code bundle; recommend Codex.)

## Safety boundaries (pinned, non-negotiable)

- Research-only. Local-only.
- No broker control, no exchange connection, no API keys, no `.env`,
  no credential handling.
- No live trading. No paper-order execution. No order placement.
- No scheduler / background daemon. No external network calls.
- No data fetch (operator supplies local files only).
- Do not modify paper / live execution files.
- A `QA_PASS` verdict is **not** trading authorization.
- A `QA_PASS` verdict does **not** autoauthorize a backtest plan.
- Crypto trend ideas are not profitable until tested with full costs
  AND forward-validated under a separately-authorized future plan.
- A good historical chart does not imply future returns.
- 24/7 crypto session handling; weekday-only filters forbidden.

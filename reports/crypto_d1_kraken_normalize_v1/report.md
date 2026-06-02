# Crypto-D1 Kraken Normalize v1 — implementation report

> **Research-only. Offline operator tool.**
> No broker control. No live trading. No paper-order execution. No exchange
> connection. No API keys. No `.env`. No credential handling. No scheduler /
> daemon. **No external network calls. No data fetch. No QA run. No backtest.
> No real dataset was materialized in this step.**

**Report id:** `crypto_d1_kraken_normalize_v1` · **version:** `1.0`

This step created the offline normalization **tool, tests, and report only**.
It did **not** run `--write` or `--freeze`, did **not** create
`data/crypto_d1_research/`, and did **not** materialize any dataset.

---

## 1. What the tool does

`tools/crypto_d1_kraken_normalize.py` reads operator-supplied, manually
downloaded Kraken daily OHLCVT export files (the standard
`unix_time,open,high,low,close,volume[,trade_count]` CSV, no header, daily file
named like `XBTUSD_1440.csv`) and normalizes BTC / ETH / SOL spot USD daily
bars into a single canonical Crypto-D1 dataset.

It is **read-only by default**. Files are only written when `--write` is
passed, and freeze artifacts are only emitted when `--freeze` is *also* passed.

```
# dry run (default): inspect, write nothing
python tools/crypto_d1_kraken_normalize.py --raw-dir <DIR>
# materialize the dataset files
python tools/crypto_d1_kraken_normalize.py --raw-dir <DIR> --write
# materialize and freeze (checksums + freeze record)
python tools/crypto_d1_kraken_normalize.py --raw-dir <DIR> --write --freeze
```

## 2. Dataset identity (pinned)

| Field | Value |
|---|---|
| `dataset_id` | `CRYPTO_D1_SPOT_BTC_ETH_SOL_V001` |
| `dataset_version` | `V001` |
| write-jail | `data/crypto_d1_research/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V001/` |
| range | `2021-06-17` .. `2025-12-31` inclusive |
| expected rows / asset | `1659` (complete 24/7 calendar) |
| expected rows total | `4977` |
| quote currency | `USD` |

A data change requires a **new** `dataset_version` (in-place edits forbidden).

## 3. Output schema (one combined CSV)

```
timestamp,open,high,low,close,volume,symbol,source,quote_currency,trade_count
```

- `timestamp` — ISO-8601 UTC bar-open (`YYYY-MM-DDT00:00:00Z`), left-closed.
- Prices are kept as the source strings to avoid precision loss; they are
  validated numerically (OHLC self-consistency, positivity).
- `symbol` — canonical `BTC` / `ETH` / `SOL`.
- `source` — `kraken:<raw_filename>` row-level provenance.
- `trade_count` — Kraken's per-bar trade count when present (optional column).

## 4. Normalization decisions (approved)

1. Offline only — reads only `--raw-dir` files; no network, subprocess, or
   credential access.
2. Dry-run default; `--write` materializes; `--freeze` (requires `--write`)
   emits `CHECKSUMS.txt` + `FREEZE_RECORD.txt`.
3. Write-jail — every write path resolved and confined to the dataset dir.
4. Symbol aliases — `XBTUSD`/`XXBTZUSD`→BTC, `ETHUSD`/`XETHZUSD`→ETH,
   `SOLUSD`→SOL; all USD-quoted.
5. Unix-seconds bar-open → ISO-8601 UTC.
6. Range filtered to `2021-06-17`..`2025-12-31`; out-of-range / partial-day
   bars excluded.
7. One combined `daily_ohlcv.csv`, sorted by asset (BTC, ETH, SOL) then
   timestamp.
8. `fees.json` ships a `PLACEHOLDER_FILL_BEFORE_QA` sentinel; manifest
   `QA_status` stays `QA_DRAFT` until the operator fills real fees and runs the
   separate QA harness.
9. Manifest `freeze_status=FROZEN` only under `--freeze`; `created_by` =
   `Mahmoud Cherif — operator manual Kraken intake`.
10. `FREEZE_RECORD.txt` pins manifest / data-contract / protocol versions and
    carries a Kraken Terms-of-Service evidence reference for research use.

## 5. Integrity rules enforced at normalization time

- `high >= max(open, close, low)` and `low <= min(open, close, high)`.
- `open`/`high`/`low`/`close` strictly positive; `volume >= 0`;
  `trade_count >= 0` when present.
- Duplicate `(symbol, timestamp)` rows are a **hard error**.
- All three required asset files must be present; one raw source per asset.

## 6. Sidecar artifacts (only when materialized)

- `manifest.json` — the 35 required Crypto-D1 per-dataset manifest fields plus
  audit extras (`missing_day_list`, per-asset row counts, row-level
  provenance). `QA_status = QA_DRAFT`, `freeze_status = FROZEN` (under
  `--freeze`).
- `fees.json` — fee/slippage stub with the `PLACEHOLDER_FILL_BEFORE_QA`
  sentinel.
- `CHECKSUMS.txt` — sha256 per file (`daily_ohlcv.csv`, `manifest.json`,
  `fees.json`).
- `FREEZE_RECORD.txt` — freeze timestamp, operator label, version pins, Kraken
  TOS evidence reference.
- **No `qa_report.json`** is produced — QA is a separate, separately-authorized
  step.

## 7. Tests

`tests/test_crypto_d1_kraken_normalize.py` — synthetic fixtures only; every
write test points `--repo-root` at a pytest `tmp_path`, so the real
`data/crypto_d1_research/` tree is never created or touched.

```
PYTHONPATH=.. ../.venv/Scripts/python.exe -m pytest \
  test_crypto_d1_kraken_normalize.py --noconftest -q -p no:cacheprovider
# -> 28 passed
```

Coverage: dry-run writes nothing; `--write` required to materialize;
`--freeze` requires `--write`; write-jail blocks escape; no
network/subprocess/credential/`os` imports (AST scan); timestamp conversion;
range filter; `XBT`→`BTC` mapping; exact header/schema; one combined file;
expected counts (1659/asset, 4977 total); duplicate detection; OHLC
consistency; negative volume / trade_count rejection; manifest 35-field schema;
`QA_DRAFT`; `freeze_status` toggling; fees sentinel; `CHECKSUMS` correctness;
`FREEZE_RECORD` content; no `qa_report.json`; determinism.

## 8. Validators (regression check — unchanged governance docs)

```
tools/crypto_d1_dataset_manifest_check.py validate                 -> OK
tools/crypto_d1_readiness_gate_check.py validate                   -> OK
tools/crypto_d1_operator_missing_items_checklist_check.py validate -> OK
```

## 9. Distinctions (word discipline)

- **FROZEN means checksummed and immutable; it does NOT mean QA-passed.**
- **QA_PASS does not imply profitability.**
- **Clean daily OHLCV data does not imply profit.**
- **A good historical chart does not imply future returns.**
- **This tool does not authorize a backtest, paper trading, or live trading.**

## 10. Not done in this step

Did not run `--write`; did not run `--freeze`; did not create
`data/crypto_d1_research/`; did not materialize the dataset; did not copy raw
Kraken data into SPARTA; did not run QA; did not run a backtest; did not start
paper / live trading; did not start Bundle 23.

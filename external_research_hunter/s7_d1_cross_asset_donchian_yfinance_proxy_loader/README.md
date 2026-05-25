# s7 D1 Cross-Asset Yfinance Proxy Loader

Read-only canonical loader for the four sealed daily-bar CSVs at
`data/s7_d1_cross_asset_donchian/raw/`. Built under the Step 03
canonical-loader-specification plan.

## Anchors

- **Spec plan:** `docs/s7_d1_cross_asset_donchian_step_03_canonical_loader_specification_plan.md`
  - sha256 `a713354bdb81dd10f5621aae18ab8f92adac5c3340a82e9d09bdb5ae1bbe2107`
  - commit `f759251b238cd764fc96e0d62d814fd6c5ab3656`
- **Upstream raw-data audit (Step 02c, verdict PASS):**
  `reports/s7_d1_cross_asset_donchian_step_02c_raw_data_audit_report.json`
  - sha256 `a17c90032fdab504c9da540a44cce37bed8f9bfaf983c625f9c1dbdfebf6d354`
  - seal `872b8275a57e859017e85abb837966b64ad1c0860df413ec010109c407c1b14f`
  - commit `1b640d1520eeec5e42b4eeccd103297abeab89e9`
- **Audit manifest (sha256 pin enforced at every load):**
  `data/s7_d1_cross_asset_donchian/raw/audit_manifest.json`
  - sha256 `794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb`

## What this loader does

- Reads the four sealed CSVs (SPY/TLT/GLD/USO) from `RAW_DIR`.
- Verifies `audit_manifest.json` sha256 against its pinned value.
- Verifies each CSV's sha256 against `per_symbol[sym].observed_sha256`
  in the manifest.
- Checks row count (3116), column set, dtype validity, monotonic dates,
  first/last date pins, OHLC invariants, finite positive prices, and
  non-negative integer volumes.
- Returns a `LoadedSymbol` per call (immutable dataclass; tuple
  fields).
- Preserves `close` AND `adj_close` as two separate tuples (per Step
  02c audit finding F1; downstream chooses which to consume).

## What this loader does NOT do

- No signal computation, no channel construction, no smoothing
  statistic, no rolling aggregation.
- No backtest, no simulator, no paper-trade loop.
- No data fetch, no network IO. No `yfinance`, no Yahoo Finance, no
  vendor SDK. The loader is strictly an on-disk CSV adapter.
- No vendor API key access. No `DATABENTO_API_KEY` use.
- No CSV mutation. No manifest mutation. No fallback. No re-fetch.

## Usage

```python
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import (
    load_symbol, load_all, LoaderError,
)

# Single symbol
spy = load_symbol("SPY")
print(spy.dates[0], spy.dates[-1], len(spy.dates))
# 2014-01-02 2026-05-22 3116

# All four
data = load_all()
print(sorted(data.keys()))
# ['GLD', 'SPY', 'TLT', 'USO']

# close vs adj_close are both available; downstream chooses
spy_close = spy.close       # unadjusted closes
spy_adj   = spy.adj_close   # adjusted closes (per Yahoo's back-adjustment)
```

## Refusal modes (`LoaderError` tree)

| Exception | When raised |
|---|---|
| `LoaderManifestMissingError` | `audit_manifest.json` missing, malformed, or sha mismatch |
| `LoaderShaMismatchError` | per-symbol CSV sha mismatch against manifest pin |
| `LoaderShapeMismatchError` | row count / columns / dtype / invariants / date pins violated |
| `LoaderCrossSymbolAlignmentError` | `load_all` detects cross-symbol date set mismatch |
| `LoaderError` (base) | unknown symbol input |

There is no `skip_verify=True` path. No `force_load` fallback. No
retry. A refusal raises immediately.

## Tests

The test suite at
`tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_loader/test_loader.py`
runs T1-T16 under stdlib `unittest`. The build report records pass
status per test.

## Importing performs no file IO

`import external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader`
performs no `open()` and no `Path.read_bytes()` call. Loading is fully
lazy. Verified by test T15.

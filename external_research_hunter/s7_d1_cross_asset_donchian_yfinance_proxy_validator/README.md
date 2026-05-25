# s7 D1 Cross-Asset Yfinance Proxy Input Validator

Pure in-memory input validator over `LoadedSymbol` structures returned
by the Step 03 canonical loader. Built under the Step 04
input-validator specification plan.

## Anchors

- **Spec plan:** `docs/s7_d1_cross_asset_donchian_step_04_input_validator_specification_plan.md`
  - sha256 `c1aad410b50e132540f66ee7c973048967b4f36a3cb0872bb5d55f25683466da`
  - commit `a5acf59f497897c0c579b584e287f0e44139e337`
- **Upstream Step 03 build (loader, verdict PASS):** commit `d7b2a0c`
  - loader.py sha256 `e0609e404cadca1c442dbce371d766aa5e13e445362ed855509a6d9684ec6fd9`
- **Upstream Step 02c audit (verdict PASS):** commit `1b640d1`
  - audit_manifest sha256 pin `794a9386abc68fdffe411e5a54534852293c8ba9c9c14fc4a2443c67a374bdcb`

## What this validator does

- Takes `LoadedSymbol` (from `load_symbol()`) or `dict[str, LoadedSymbol]`
  (from `load_all()`) as input.
- Confirms structural fitness for downstream channel-construction phases:
  bar count, monotonic ISO dates, warmup adequacy, window coverage,
  cross-symbol alignment, in-sample summary statistics.
- Returns `ValidationReport` (per-symbol) or
  `CrossSymbolValidationReport` (portfolio).
- Raises `ValidatorError` subclass on structural refusal.

## What this validator does NOT do

- No channel construction of any length.
- No exit-channel construction of any length.
- No smoothing statistic.
- No moving average.
- No rolling aggregation of any length.
- No per-day return computation, no log-return, no cumulative return.
- No z-score, percentile, quantile.
- No correlation, covariance, or PCA.
- No simulator, no backtest, no paper-trade loop.
- No file IO at all. No `open()`, no `Path.read_bytes()`. The validator
  is pure in-memory.
- No network IO. No vendor SDK. No `yfinance`, no Yahoo Finance, no
  Databento. No `DATABENTO_API_KEY` access.

## Out-of-sample protection rule

For the `OUT_OF_SAMPLE_WINDOW` and `POST_OOS_DIAGNOSTIC_WINDOW`, the
validator records ONLY:

- bar count in the window;
- first / last date in the window (informational coverage marker).

The validator does NOT compute min / max / median / mean / percentile
/ return / correlation / any other distributional or signal-like
quantity over those windows. The attestation
`oos_summary_intentionally_omitted = True` is permanent on every
`ValidationReport`. This preserves the parent spec section 11 invariant
`oos_inspection_blocked_at_in_sample`.

## Verdicts

- `PASS` - all checks pass and the data covers the in-sample window
  start (no truncation).
- `PASS_WITH_WARMUP_TRUNCATION` - all checks pass, but the loaded
  data starts later than the in-sample window start (e.g., this
  ETF-proxy dataset starts 2014-01-02 while the in-sample window
  starts 2013-01-01). Downstream chooses how to handle.
- `FAIL` - one or more A-check failures at portfolio level.

`PASS_WITH_WARMUP_TRUNCATION` is the expected verdict for this
ETF-proxy dataset; it is NOT a fatal classification.

## Usage

```python
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_loader import load_all
from external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_validator import (
    validate_loaded_symbol, validate_all,
    IN_SAMPLE_WINDOW, OUT_OF_SAMPLE_WINDOW,
    DONCHIAN_ENTRY_LOOKBACK,
)

data = load_all()
portfolio_report = validate_all(data)
print(portfolio_report.portfolio_verdict)
# PASS_WITH_WARMUP_TRUNCATION

for sym, rep in portfolio_report.per_symbol.items():
    print(sym, rep.verdict,
          "bars_in_IS=", rep.bar_count_in_in_sample_window,
          "bars_in_OOS=", rep.bar_count_in_oos_window,
          "warmup_truncation=", rep.warmup_truncation_at_data_start)
```

## Refusal modes (`ValidatorError` tree)

| Exception | When raised |
|---|---|
| `ValidatorInputError` | input is not a `LoadedSymbol`, symbol not in {SPY,TLT,GLD,USO}, bar count != 3116, non-monotonic dates, non-positive in-sample price |
| `WarmupInsufficientError` | fewer than 55 prior loaded bars exist before the first in-sample-window bar |
| `WindowMisfitError` | in-sample window has fewer than 56 bars or out-of-sample window has zero bars |
| `ValidatorCrossSymbolAlignmentError` | cross-symbol date sets, bar counts, or window counts diverge |
| `ValidatorError` (base) | any other unhandled refusal |

There is no `skip_checks=True` path. No `force_pass` fallback. No
retry. A refusal raises immediately.

## Tests

The test suite at
`tests/external_research_hunter/s7_d1_cross_asset_donchian_yfinance_proxy_validator/test_validator.py`
runs T1-T16 under stdlib `unittest`. The build report records pass
status per test.

## Importing performs no file IO

`import external_research_hunter.s7_d1_cross_asset_donchian_yfinance_proxy_validator`
performs no `open()` and no `Path.read_bytes()` call. The validator
does not read any file at any point. Verified by test T15.

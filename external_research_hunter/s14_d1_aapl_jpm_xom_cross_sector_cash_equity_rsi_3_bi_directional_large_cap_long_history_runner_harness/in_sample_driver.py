"""s14-d1-cross-sector in-sample driver. Filters sealed cross-sector CSVs to IS window only.

P3 BUILD scope: structural skeleton + hardcoded constants. NO execution.
P6 IS diagnostic shall invoke run_in_sample() under separate operator authorization.

Inherits Phase 2 safety contracts (C1-C8). Cash-equity split_only convention (DA17).
"""

import datetime as _dt
import hashlib as _hashlib

IN_SAMPLE_START = _dt.date(2019, 1, 2)
IN_SAMPLE_END = _dt.date(2023, 12, 29)
TS_KEY = "date"

# DR9-passed sealed cross-sector CSV registry (reuse byte-equivalent; no fresh fetch post-seal)
CSV_REGISTRY = {
    "AAPL": {
        "path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/AAPL_ohlcv_1d_20190102_20251230.csv",
        "sha256": "f6625ff1a6f8026369344bd50ca82bffcba716f1f3be9cdcfb5b905e35f893a9",
    },
    "JPM": {
        "path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/JPM_ohlcv_1d_20190102_20251230.csv",
        "sha256": "8aa244ab7724b292c659c81171bd8d3cf5ce5684d6c69864ee61e0be90238db7",
    },
    "XOM": {
        "path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/XOM_ohlcv_1d_20190102_20251230.csv",
        "sha256": "fbbc462cbfbd11a68b0aed4d0c3fa72312afea5112cebcc24860689f33b7f77c",
    },
}


def verify_csv_sha256(symbol):
    """Read CSV bytes for `symbol` and verify sha256 against registry. Raises on mismatch."""
    entry = CSV_REGISTRY[symbol]
    with open(entry["path"], "rb") as f:
        actual = _hashlib.sha256(f.read()).hexdigest()
    if actual != entry["sha256"]:
        raise Exception(
            f"S14_D1_CROSS_SECTOR_CSV_SHA_MISMATCH: symbol={symbol} expected {entry['sha256']} "
            f"got {actual} path={entry['path']!r}"
        )
    return True


def filter_rows_to_is_window(rows, ts_key=TS_KEY):
    """Filter row-dicts to IS window bars."""
    out = []
    for row in rows:
        ts_raw = row.get(ts_key)
        if ts_raw is None:
            continue
        ts_str = str(ts_raw)
        try:
            date_part = _dt.datetime.fromisoformat(ts_str.replace("Z", "+00:00")).date()
        except ValueError:
            try:
                date_part = _dt.date.fromisoformat(ts_str[:10])
            except ValueError:
                continue
        if IN_SAMPLE_START <= date_part <= IN_SAMPLE_END:
            out.append(row)
    return out


def run_in_sample(*args, **kwargs):
    """Stub. NOT AUTHORIZED at P3 BUILD scope."""
    raise RuntimeError(
        "P6_IS_NOT_AUTHORIZED: run_in_sample() is gated by separate operator authorization "
        "(Authorize s14-d1-cross-sector cash-equity P6 IS diagnostic only). P3 BUILD scope does "
        "NOT authorize any signal computation, backtest, or simulator run."
    )

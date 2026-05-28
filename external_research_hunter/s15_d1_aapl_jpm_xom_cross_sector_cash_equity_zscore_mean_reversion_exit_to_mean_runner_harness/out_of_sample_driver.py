"""s15-d1-cross-sector out-of-sample driver. Filters reused DR9-passed CSVs to OOS window only.

P3 BUILD scope: structural skeleton + hardcoded constants. NO execution.
P10 OOS gate shall invoke run_out_of_sample() under separate operator authorization.

REC1-equivalent BINDING reminder (carried from SEAL): OOS K9 reachable on the cross-sector basket
(expected ~60-105/y); if observed effective IS rate falls below 25/y basket-summed, OOS K9
unreachability becomes structurally probable. Expected terminal verdict if K9 fires at OOS:
PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED.

By construction, this file does NOT contain in-sample-window constants, does NOT contain standalone
in-sample year tokens, and does NOT contain a run_in_sample function. OOS isolation is structurally
enforced by separate files.
"""

import datetime as _dt
import hashlib as _hashlib

OUT_OF_SAMPLE_START = _dt.date(2024, 1, 2)
OUT_OF_SAMPLE_END = _dt.date(2025, 12, 30)
TS_KEY = "date"

CSV_REGISTRY = {
    "AAPL": {"path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/AAPL_ohlcv_1d_20190102_20251230.csv", "sha256": "f6625ff1a6f8026369344bd50ca82bffcba716f1f3be9cdcfb5b905e35f893a9"},
    "JPM": {"path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/JPM_ohlcv_1d_20190102_20251230.csv", "sha256": "8aa244ab7724b292c659c81171bd8d3cf5ce5684d6c69864ee61e0be90238db7"},
    "XOM": {"path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/XOM_ohlcv_1d_20190102_20251230.csv", "sha256": "fbbc462cbfbd11a68b0aed4d0c3fa72312afea5112cebcc24860689f33b7f77c"},
}


def verify_csv_sha256(symbol):
    """Read CSV bytes for `symbol` and verify sha256 against registry. Raises on mismatch."""
    entry = CSV_REGISTRY[symbol]
    with open(entry["path"], "rb") as f:
        actual = _hashlib.sha256(f.read()).hexdigest()
    if actual != entry["sha256"]:
        raise Exception(
            f"S15_D1_CROSS_SECTOR_CSV_SHA_MISMATCH: symbol={symbol} expected {entry['sha256']} "
            f"got {actual} path={entry['path']!r}"
        )
    return True


def filter_rows_to_oos_window(rows, ts_key=TS_KEY):
    """Filter row-dicts to OOS window bars."""
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
        if OUT_OF_SAMPLE_START <= date_part <= OUT_OF_SAMPLE_END:
            out.append(row)
    return out


def run_out_of_sample(*args, **kwargs):
    """Stub. NOT AUTHORIZED at P3 BUILD scope.

    REC1-equivalent BINDING: OOS K9 borderline-reachable at lower bound; expected terminal verdict if
    K9 fires at OOS is PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED.
    """
    raise RuntimeError(
        "P10_OOS_NOT_AUTHORIZED: run_out_of_sample() is gated by separate operator authorization "
        "(Authorize s15-d1 cross-sector cash-equity z-score exit-to-mean P10 OOS gate only). "
        "P3 BUILD scope does NOT authorize OOS inspection, signal computation, or simulator run on OOS rows."
    )

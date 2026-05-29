"""s20-d1 out-of-sample driver. OOS window only; run_out_of_sample() STUB. OOS isolation: no IS constants/tokens. NO execution."""

import datetime as _dt
import hashlib as _hashlib

OOS_START = _dt.date(2024, 1, 2)
OOS_END = _dt.date(2025, 12, 30)
TS_KEY = "date"


def _registry():
    from .in_sample_driver import CSV_REGISTRY
    return CSV_REGISTRY


def verify_csv_sha256(symbol):
    entry = _registry()[symbol]
    with open(entry["path"], "rb") as f:
        actual = _hashlib.sha256(f.read()).hexdigest()
    if actual != entry["sha256"]:
        raise Exception(f"S20_D1_OOS_CSV_SHA_MISMATCH: symbol={symbol} expected {entry['sha256']} got {actual}")
    return True


def filter_rows_to_oos_window(rows, ts_key=TS_KEY):
    out = []
    for row in rows:
        ts_raw = row.get(ts_key)
        if ts_raw is None:
            continue
        ts_str = str(ts_raw)
        try:
            d = _dt.datetime.fromisoformat(ts_str.replace("Z", "+00:00")).date()
        except ValueError:
            try:
                d = _dt.date.fromisoformat(ts_str[:10])
            except ValueError:
                continue
        if OOS_START <= d <= OOS_END:
            out.append(row)
    return out


def run_out_of_sample(*args, **kwargs):
    raise RuntimeError(
        "P10_OOS_NOT_AUTHORIZED: run_out_of_sample() is gated by separate operator authorization (the final P10 "
        "OOS gate). P3 BUILD scope does NOT authorize any OOS signal computation, backtest, or simulator run."
    )

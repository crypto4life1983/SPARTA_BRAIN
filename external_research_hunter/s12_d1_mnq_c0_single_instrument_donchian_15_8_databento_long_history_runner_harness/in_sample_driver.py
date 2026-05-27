"""s12-d1 in-sample driver. Filters sealed CSV to IS window only.

P3 BUILD scope: structural skeleton + hardcoded constants. NO execution.
P6 IS diagnostic shall invoke run_in_sample() under separate operator authorization.

OOS data is structurally not accessible from this module (by file separation;
out_of_sample_driver.py is the sibling driver for OOS).

Inherits Phase 2 safety contracts (C1-C8) from:
  docs/phase2_safety_contract_template.md
Template source candidate (parked, not money-proven):
  s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
Template reuse notice: NKE strategy logic NOT inherited; only safety contracts.
"""

import datetime as _dt
import hashlib as _hashlib

# Hardcoded constants (LOCKED at SEAL/P1)
IN_SAMPLE_START = _dt.date(2019, 5, 13)
IN_SAMPLE_END = _dt.date(2023, 12, 29)
CSV_PATH_HARDCODED = (
    "data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv"
)
CSV_SHA256_HARDCODED = "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e"


def verify_csv_sha256(path=CSV_PATH_HARDCODED, expected=CSV_SHA256_HARDCODED):
    """Read CSV bytes and verify sha256. Returns True iff match; raises on mismatch."""
    with open(path, "rb") as f:
        actual = _hashlib.sha256(f.read()).hexdigest()
    if actual != expected:
        raise Exception(
            f"S12_D1_MNQ_CSV_SHA_MISMATCH: expected {expected} got {actual} path={path!r}"
        )
    return True


def filter_rows_to_is_window(rows, ts_key="ts_event"):
    """Filter an iterable of row-dicts to bars whose ts_event date is in [IN_SAMPLE_START, IN_SAMPLE_END]."""
    out = []
    for row in rows:
        ts_raw = row.get(ts_key)
        if ts_raw is None:
            continue
        ts_str = str(ts_raw)
        try:
            date_part = _dt.datetime.fromisoformat(ts_str.replace("Z", "+00:00")).date()
        except ValueError:
            # Fallback: try first 10 chars as YYYY-MM-DD
            try:
                date_part = _dt.date.fromisoformat(ts_str[:10])
            except ValueError:
                continue
        if IN_SAMPLE_START <= date_part <= IN_SAMPLE_END:
            out.append(row)
    return out


def run_in_sample(*args, **kwargs):
    """Run the s12-d1 IS diagnostic. NOT AUTHORIZED at P3 BUILD scope.

    This stub exists for module structure; actual P6 IS execution requires separate
    operator authorization. Calling this at P3 BUILD raises to enforce the gate.
    """
    raise RuntimeError(
        "P6_IS_NOT_AUTHORIZED: run_in_sample() is gated by separate operator authorization "
        "(Authorize s12 D1 MNQ.c.0 P6 IS diagnostic only). P3 BUILD scope does NOT authorize "
        "any signal computation, backtest, or simulator run."
    )

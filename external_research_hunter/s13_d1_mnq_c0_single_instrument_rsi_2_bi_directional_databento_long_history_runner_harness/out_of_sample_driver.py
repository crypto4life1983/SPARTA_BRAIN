"""s13-d1 out-of-sample driver. Filters sealed CSV to OOS window only.

P3 BUILD scope: structural skeleton + hardcoded constants. NO execution.
P10 OOS gate shall invoke run_out_of_sample() under separate operator authorization.

REC1-equivalent BINDING reminder (carried from SEAL):
  OOS K9 reachable at lower bound with thin margin (~50-65 trades/year vs 50/year floor).
  If observed IS rate falls below 25/year on RSI(2) bi-directional, OOS K9 unreachability
  becomes structurally probable. Expected terminal verdict if K9 fires at OOS:
  PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED.

By construction, this file does NOT contain IS-window constants (IN_SAMPLE_START / IN_SAMPLE_END),
does NOT contain standalone year tokens for the IS window, and does NOT contain a run_in_sample
function. OOS isolation is structurally enforced by separate files.

Inherits Phase 2 safety contracts (C1-C8). NKE strategy logic NOT inherited.
"""

import datetime as _dt
import hashlib as _hashlib

OUT_OF_SAMPLE_START = _dt.date(2024, 1, 2)
OUT_OF_SAMPLE_END = _dt.date(2025, 12, 30)
CSV_PATH_HARDCODED = (
    "data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv"
)
CSV_SHA256_HARDCODED = "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e"


def verify_csv_sha256(path=CSV_PATH_HARDCODED, expected=CSV_SHA256_HARDCODED):
    """Read CSV bytes and verify sha256."""
    with open(path, "rb") as f:
        actual = _hashlib.sha256(f.read()).hexdigest()
    if actual != expected:
        raise Exception(
            f"S13_D1_MNQ_CSV_SHA_MISMATCH: expected {expected} got {actual} path={path!r}"
        )
    return True


def filter_rows_to_oos_window(rows, ts_key="ts_event"):
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

    REC1-equivalent BINDING: OOS K9 is borderline-reachable at lower bound; expected terminal
    verdict if K9 fires at OOS is PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED.
    """
    raise RuntimeError(
        "P10_OOS_NOT_AUTHORIZED: run_out_of_sample() is gated by separate operator authorization "
        "(Authorize s13 D1 MNQ.c.0 P10 OOS gate only). P3 BUILD scope does NOT authorize "
        "OOS inspection, signal computation, or simulator run on OOS rows."
    )

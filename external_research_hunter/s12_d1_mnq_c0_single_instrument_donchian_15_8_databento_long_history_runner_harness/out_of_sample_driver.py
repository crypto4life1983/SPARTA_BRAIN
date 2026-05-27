"""s12-d1 out-of-sample driver. Filters sealed CSV to OOS window only.

P3 BUILD scope: structural skeleton + hardcoded constants. NO execution.
P10 OOS gate shall invoke run_out_of_sample() under separate operator authorization.

OOS K9 disclosure (REC1 binding; carried byte-equivalent from SEAL):
  Implied OOS trade count over 2.0y at IS rate is approximately 35-87 trades, below K9 = 100.
  OOS K9 is structurally unreachable; expected terminal verdict is
  PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED (analogous to S10-D2 P11 PARK at 23c7164).

By construction, this file does NOT contain IS-window constants
(IN_SAMPLE_START / IN_SAMPLE_END), does NOT contain the year/month tokens of the IS window,
and does NOT contain a run_in_sample function. OOS isolation is structurally enforced
by separate files.

Inherits Phase 2 safety contracts (C1-C8) from:
  docs/phase2_safety_contract_template.md
Template source candidate (parked, not money-proven):
  s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
Template reuse notice: NKE strategy logic NOT inherited; only safety contracts.
"""

import datetime as _dt
import hashlib as _hashlib

# Hardcoded constants (LOCKED at SEAL/P1; OOS-only)
OUT_OF_SAMPLE_START = _dt.date(2024, 1, 2)
OUT_OF_SAMPLE_END = _dt.date(2025, 12, 30)
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


def filter_rows_to_oos_window(rows, ts_key="ts_event"):
    """Filter an iterable of row-dicts to bars whose ts_event date is in [OUT_OF_SAMPLE_START, OUT_OF_SAMPLE_END]."""
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
    """Run the s12-d1 OOS diagnostic. NOT AUTHORIZED at P3 BUILD scope.

    This stub exists for module structure; actual P10 OOS execution requires separate
    operator authorization AFTER P6 IS verdict is ELIGIBLE_FOR_OOS. Calling this at
    P3 BUILD raises to enforce the gate.

    REC1 BINDING REMINDER (from SEAL 66bbbd1 carried byte-equivalent): OOS K9 is
    structurally unreachable; expected terminal verdict is
    PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED. The chain shall NOT relax K9 at OOS.
    """
    raise RuntimeError(
        "P10_OOS_NOT_AUTHORIZED: run_out_of_sample() is gated by separate operator authorization "
        "(Authorize s12 D1 MNQ.c.0 P10 OOS gate only). P3 BUILD scope does NOT authorize "
        "OOS inspection, signal computation, or simulator run on OOS rows."
    )

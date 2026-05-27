"""S12-D1 in_sample_driver: IS-phase entrypoint (P3 BUILD authors; future P6 invokes).

Hard-codes the IS window 2019-05-13 to 2023-12-29. Reads daily bars
from the audit-clean MNQ.c.0 CSV byte-equivalent (sha256 locked at
SEAL). Provides a `run_in_sample(*, expected_seals=None, cost_tier='S1')`
entrypoint that the future P6 IS diagnostic phase will invoke under
separate fresh operator authorization.

P3 BUILD authors this module. Module-level constants are byte-stable
under driver source byte-stability invariants. The body of
`run_in_sample` does NOT execute strategy logic at BUILD; the function
is callable in the future-phase context only after explicit P6
authorization.

No fetch. No Databento. No DATABENTO_API_KEY. No network IO. No
brokerage. No order submission. The driver reads ONLY from the
locally-present audit-clean CSV.
"""
from __future__ import annotations

import datetime as _dt
import hashlib as _hashlib
import os as _os
import pathlib as _pathlib
from typing import Dict, List, Optional, Tuple

from . import runner_main as _runner_main
from .execution_guard import ExecutionGuard as _ExecutionGuard

# ----------------------------------------------------------------------------
# IS window constants (LOCKED at SEAL; byte-stable through entire chain)
# ----------------------------------------------------------------------------

IN_SAMPLE_START = "2019-05-13"
IN_SAMPLE_END = "2023-12-29"

CACHE_ROOT = _pathlib.Path("data") / "databento_cache_s12_d1_is"
DATA_CSV_PATH = _pathlib.Path(_runner_main.CONFIG["data_csv_path"])
DATA_CSV_EXPECTED_SHA256 = _runner_main.CONFIG["data_csv_sha256"]
DATA_CSV_EXPECTED_DATA_ROWS = _runner_main.CONFIG["data_csv_expected_data_rows"]

# Pre-anchored predecessor seals (informational; runtime asserts in
# assert_seal_inheritance)
EXPECTED_PREDECESSOR_SEALS: Dict[str, str] = dict(_runner_main.PREDECESSOR_SEALS)

# Output paths (LOCKED at SEAL via P2 plan)
OUTPUT_DIAGNOSTIC_JSON = _pathlib.Path(
    "reports/external_research_hunter/"
    "s12_d1_mnq_c0_single_instrument_donchian_15_8_in_sample_diagnostic_result_sealed.json"
)
OUTPUT_DIAGNOSTIC_MD = _pathlib.Path(
    "reports/external_research_hunter/"
    "s12_d1_mnq_c0_single_instrument_donchian_15_8_in_sample_diagnostic_result_sealed.md"
)

SCHEMA_ID = "sparta.s12.d1.mnq_c0.donchian_15_8.in_sample_diagnostic_run_report.v1"


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _parse_iso_date(s: str) -> _dt.date:
    return _dt.date.fromisoformat(s)


def _is_within_window(date_str: str, start: str, end: str) -> bool:
    """date_str is the leading 'YYYY-MM-DD' substring of a ts_event."""
    d = _parse_iso_date(date_str[:10])
    return _parse_iso_date(start) <= d <= _parse_iso_date(end)


def assert_seal_inheritance(actual_seals: Optional[Dict[str, str]] = None) -> None:
    """Verify predecessor seals match the SEAL-locked anchors.

    actual_seals is a dict {anchor_name: sha256_hex}. If None, no check
    is performed (used during P3 BUILD when downstream provenance is
    not yet wired). Future P6 invocations should pass the live seals.
    """
    if actual_seals is None:
        return
    for k, expected in EXPECTED_PREDECESSOR_SEALS.items():
        if k not in actual_seals:
            continue
        if actual_seals[k] != expected:
            raise RuntimeError(
                f"Seal inheritance mismatch for {k!r}: "
                f"expected {expected!r}; got {actual_seals[k]!r}"
            )


def assert_csv_present_and_byte_stable() -> Tuple[int, str]:
    """Verify the audit-clean MNQ.c.0 CSV is present, sha matches, rowcount matches.

    Returns (data_row_count, sha256_hex). Raises RuntimeError on any
    integrity failure. Does NOT modify the CSV.
    """
    if not DATA_CSV_PATH.exists():
        raise RuntimeError(
            f"Audit-clean MNQ.c.0 CSV not found at {DATA_CSV_PATH!s} "
            "(no fresh fetch authorized; mnq_c0_csv_reuse_byte_equivalent_no_fresh_fetch)"
        )
    b = DATA_CSV_PATH.read_bytes()
    sha = _hashlib.sha256(b).hexdigest()
    if sha != DATA_CSV_EXPECTED_SHA256:
        raise RuntimeError(
            f"CSV sha256 mismatch: expected {DATA_CSV_EXPECTED_SHA256!r}; got {sha!r}"
        )
    lines = b.decode("utf-8").splitlines()
    if not lines:
        raise RuntimeError("CSV is empty")
    data_rows = len(lines) - 1  # subtract header
    if data_rows != DATA_CSV_EXPECTED_DATA_ROWS:
        raise RuntimeError(
            f"CSV data row count mismatch: expected "
            f"{DATA_CSV_EXPECTED_DATA_ROWS}; got {data_rows}"
        )
    return data_rows, sha


def derive_rth_daily_bars(
    csv_path: Optional[_pathlib.Path] = None,
    window_start: str = IN_SAMPLE_START,
    window_end: str = IN_SAMPLE_END,
) -> List[Dict[str, object]]:
    """Read the audit-clean MNQ.c.0 CSV and return daily bars within the
    in-sample window.

    The MNQ.c.0 source is already daily RTH data per the Databento
    `ohlcv-1d` schema (see SEAL section 5); no intraday aggregation
    needed. Each bar is a dict with keys date / open / high / low /
    close / volume.

    P3 BUILD authors this function; it is NOT invoked at BUILD. Future
    P6 IS phase invokes it under separate fresh operator authorization.
    """
    p = csv_path if csv_path is not None else DATA_CSV_PATH
    if not p.exists():
        raise RuntimeError(
            f"CSV not found at {p!s}; no new fetch authorized."
        )
    lines = p.read_bytes().decode("utf-8").splitlines()
    if len(lines) < 2:
        raise RuntimeError("CSV has no data rows")
    header = lines[0].split(",")
    # Header columns from the audit-clean Databento export:
    # ts_event,rtype,publisher_id,instrument_id,open,high,low,close,volume,symbol
    try:
        idx_ts = header.index("ts_event")
        idx_open = header.index("open")
        idx_high = header.index("high")
        idx_low = header.index("low")
        idx_close = header.index("close")
        idx_volume = header.index("volume")
    except ValueError as e:
        raise RuntimeError(f"CSV header missing expected column: {e}") from e

    bars: List[Dict[str, object]] = []
    for line in lines[1:]:
        if not line.strip():
            continue
        fields = line.split(",")
        ts_event = fields[idx_ts]
        if not _is_within_window(ts_event, window_start, window_end):
            continue
        bars.append(
            {
                "date": _parse_iso_date(ts_event[:10]),
                "open": float(fields[idx_open]),
                "high": float(fields[idx_high]),
                "low": float(fields[idx_low]),
                "close": float(fields[idx_close]),
                "volume": int(fields[idx_volume]),
            }
        )
    return bars


# ----------------------------------------------------------------------------
# IS run entrypoint (P3 BUILD authors; NOT invoked at BUILD)
# ----------------------------------------------------------------------------

def run_in_sample(
    *,
    expected_seals: Optional[Dict[str, str]] = None,
    cost_tier: str = "S1",
) -> Dict[str, object]:
    """In-sample diagnostic run entrypoint.

    This function is the future-phase entrypoint for the IS diagnostic.
    P3 BUILD authors the body; P3 BUILD does NOT invoke this function.
    A future P6 IS phase (separate fresh operator authorization) will
    invoke run_in_sample(cost_tier='S1') against the locally-present
    audit-clean CSV.

    P6's invocation will:
      1. assert_seal_inheritance(expected_seals)
      2. assert_csv_present_and_byte_stable()
      3. instantiate ExecutionGuard and run assert_all_static_invariants_held()
      4. derive_rth_daily_bars() over IN_SAMPLE_START..IN_SAMPLE_END
      5. Apply Donchian-15/8 + Wilder ATR(20) + 2N stop + 1% sizing
      6. Apply selected cost tier to commissions/fees/slippage
      7. Track equity curve + K4 max-drawdown
      8. Tally closed_trades (K9), sharpe-proxy (K1), expectancy (K2)
      9. Emit a sealed JSON+MD diagnostic report at OUTPUT_DIAGNOSTIC_*

    At BUILD time this function MUST NOT execute. It raises
    NotImplementedError so any inadvertent call at BUILD time fails
    loudly.
    """
    # Light-weight invariants (do NOT actually run anything)
    _ = ExecutionGuard()  # noqa: F841  (placeholder for future-phase wiring)
    raise NotImplementedError(
        "run_in_sample is the future-phase entrypoint and is not invoked "
        "at P3 BUILD. A separate fresh operator authorization is required "
        "to invoke this driver."
    )


# ----------------------------------------------------------------------------
# Alias for ExecutionGuard for test convenience
# ----------------------------------------------------------------------------

ExecutionGuard = _ExecutionGuard

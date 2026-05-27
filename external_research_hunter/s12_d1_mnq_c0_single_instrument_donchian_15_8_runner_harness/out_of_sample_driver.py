"""S12-D1 out_of_sample_driver: OOS-phase entrypoint (sibling to in_sample_driver).

Hard-codes the OOS window 2024-01-02 to 2025-12-30. Sibling-driver
pattern (per s10-D2 P3.6 BUILD lineage) preserves IS driver byte-
stability when the OOS driver is added; each driver hard-codes its
window constants; OOS driver structurally cannot inspect IS data and
vice versa.

P3 BUILD authors this module. The `run_out_of_sample` entrypoint is
NOT invoked at BUILD; future P10 OOS phase will invoke it under
separate fresh operator authorization.

No fetch. No Databento. No DATABENTO_API_KEY. No network IO. No
brokerage. No order submission.
"""
from __future__ import annotations

import datetime as _dt
import hashlib as _hashlib
import pathlib as _pathlib
from typing import Dict, List, Optional, Tuple

from . import runner_main as _runner_main
from .execution_guard import ExecutionGuard as _ExecutionGuard

# ----------------------------------------------------------------------------
# OOS window constants (LOCKED at SEAL; sibling to IS constants)
# ----------------------------------------------------------------------------

OUT_OF_SAMPLE_START = "2024-01-02"
OUT_OF_SAMPLE_END = "2025-12-30"

CACHE_ROOT = _pathlib.Path("data") / "databento_cache_s12_d1_oos"
DATA_CSV_PATH = _pathlib.Path(_runner_main.CONFIG["data_csv_path"])
DATA_CSV_EXPECTED_SHA256 = _runner_main.CONFIG["data_csv_sha256"]
DATA_CSV_EXPECTED_DATA_ROWS = _runner_main.CONFIG["data_csv_expected_data_rows"]

# Pre-anchored predecessor seals (informational; runtime asserts in
# assert_seal_inheritance)
EXPECTED_PREDECESSOR_SEALS: Dict[str, str] = dict(_runner_main.PREDECESSOR_SEALS)

# Output paths (LOCKED at SEAL via P2 plan)
OUTPUT_DIAGNOSTIC_JSON = _pathlib.Path(
    "reports/external_research_hunter/"
    "s12_d1_mnq_c0_single_instrument_donchian_15_8_out_of_sample_diagnostic_result_sealed.json"
)
OUTPUT_DIAGNOSTIC_MD = _pathlib.Path(
    "reports/external_research_hunter/"
    "s12_d1_mnq_c0_single_instrument_donchian_15_8_out_of_sample_diagnostic_result_sealed.md"
)

SCHEMA_ID = "sparta.s12.d1.mnq_c0.donchian_15_8.out_of_sample_diagnostic_run_report.v1"


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------

def _parse_iso_date(s: str) -> _dt.date:
    return _dt.date.fromisoformat(s)


def _is_within_window(date_str: str, start: str, end: str) -> bool:
    d = _parse_iso_date(date_str[:10])
    return _parse_iso_date(start) <= d <= _parse_iso_date(end)


def assert_seal_inheritance(actual_seals: Optional[Dict[str, str]] = None) -> None:
    """Verify predecessor seals match the SEAL-locked anchors.

    actual_seals is a dict {anchor_name: sha256_hex}. If None, no check
    is performed (used during P3 BUILD when downstream provenance is
    not yet wired). Future P10 invocations should pass live seals.
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
    if not DATA_CSV_PATH.exists():
        raise RuntimeError(
            f"Audit-clean MNQ.c.0 CSV not found at {DATA_CSV_PATH!s} "
            "(no fresh fetch authorized)"
        )
    b = DATA_CSV_PATH.read_bytes()
    sha = _hashlib.sha256(b).hexdigest()
    if sha != DATA_CSV_EXPECTED_SHA256:
        raise RuntimeError(
            f"CSV sha256 mismatch: expected {DATA_CSV_EXPECTED_SHA256!r}; got {sha!r}"
        )
    lines = b.decode("utf-8").splitlines()
    data_rows = len(lines) - 1
    if data_rows != DATA_CSV_EXPECTED_DATA_ROWS:
        raise RuntimeError(
            f"CSV data row count mismatch: expected "
            f"{DATA_CSV_EXPECTED_DATA_ROWS}; got {data_rows}"
        )
    return data_rows, sha


def derive_rth_daily_bars(
    csv_path: Optional[_pathlib.Path] = None,
    window_start: str = OUT_OF_SAMPLE_START,
    window_end: str = OUT_OF_SAMPLE_END,
) -> List[Dict[str, object]]:
    """Read the audit-clean CSV and return daily bars within the OOS window.

    P3 BUILD authors this function. NOT invoked at BUILD. Future P10
    OOS phase invokes it under separate fresh operator authorization.

    Sibling-driver invariant: this driver structurally cannot read IS-
    window bars because window_start defaults to OUT_OF_SAMPLE_START.
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
# OOS run entrypoint (P3 BUILD authors; NOT invoked at BUILD)
# ----------------------------------------------------------------------------

def run_out_of_sample(
    *,
    expected_seals: Optional[Dict[str, str]] = None,
    cost_tier: str = "S1",
) -> Dict[str, object]:
    """Out-of-sample diagnostic run entrypoint.

    Future P10 OOS phase will invoke run_out_of_sample(cost_tier='S1')
    only after the operator authorizes "Authorize s12 D1 P10 OOS gate
    only" (or equivalent), AND only after the IS verdict at P6 +
    cost-stress sweep at P6.5 + P7 decision memo all clear.

    Per C1.A acknowledgment at SEAL: OOS K9 may fire on this verdict
    (expected proportional-scaling OOS trades = 35/61/87 across
    lower/central/upper IS bounds, all below K9 = 100). Per C1.D:
    OOS K9 sub-threshold maps to DR1 INCONCLUSIVE_HOLD (NOT
    REJECT_FAST). Candidate parks; IS evidence preserved.

    At BUILD time this function MUST NOT execute. It raises
    NotImplementedError so any inadvertent BUILD-time call fails loudly.
    """
    _ = ExecutionGuard()  # noqa: F841  (placeholder for future-phase wiring)
    raise NotImplementedError(
        "run_out_of_sample is the future-phase entrypoint and is not "
        "invoked at P3 BUILD. A separate fresh operator authorization is "
        "required to invoke this driver."
    )


# ----------------------------------------------------------------------------
# Alias for ExecutionGuard for test convenience
# ----------------------------------------------------------------------------

ExecutionGuard = _ExecutionGuard

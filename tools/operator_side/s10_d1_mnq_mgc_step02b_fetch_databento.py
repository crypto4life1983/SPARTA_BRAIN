"""s10 D1 MNQ+MGC Step 02b operator-side Databento fetch.

Reads DATABENTO_API_KEY from environment ONLY. Never prints, logs, hashes,
writes, or exposes the key in any form. Fetches the sealed-spec ohlcv-1d data
for MNQ.c.0 + MGC.c.0 over the IS+OOS window and writes raw CSV files to a
single approved directory plus one manifest JSON. Fail-closed on every
deviation from the sealed-spec data scope.

Sealed spec reference:
  docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md (commit 9040429)

Scope of this script:
  - data fetch only;
  - no strategy code, no signal computation, no backtest, no simulator;
  - no OOS inspection, no return summary, no edge evaluation;
  - no review_queue.json mutation;
  - no Strategy Lab promotion;
  - no live trading.

Operator runs this script in their own local shell environment with
DATABENTO_API_KEY exported as an environment variable. The controller does
NOT run this script and does NOT have access to DATABENTO_API_KEY.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path


# Sealed-spec constants. DO NOT MODIFY POST-SEAL.
SEALED_SPEC_COMMIT = "9040429"
CANDIDATE_RECORD_ID = "s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history"

DATASET   = "GLBX.MDP3"
SCHEMA    = "ohlcv-1d"
STYPE_IN  = "continuous"
SYMBOLS   = ("MNQ.c.0", "MGC.c.0")

# Combined IS+OOS date scope.
START_DATE_INCLUSIVE = "2019-05-13"
END_DATE_INCLUSIVE   = "2025-12-30"

# IS / OOS markers (recorded in manifest; OOS is NOT inspected by this script).
IS_WINDOW_START  = "2019-05-13"
IS_WINDOW_END    = "2023-12-29"
OOS_WINDOW_START = "2024-01-02"
OOS_WINDOW_END   = "2025-12-30"

# Approved output directory. Fail-closed if a write path falls outside this tree.
APPROVED_OUTPUT_DIR = Path("data/s10_d1_mnq_mgc_databento_long_history/raw")

# Suggested output filenames (operator may override via CLI if needed; default
# mirrors the sealed-spec naming convention).
DEFAULT_OUTPUT_FILENAMES = {
    "MNQ.c.0": "MNQ_c_0_ohlcv_1d_20190513_20251230.csv",
    "MGC.c.0": "MGC_c_0_ohlcv_1d_20190513_20251230.csv",
}

MANIFEST_FILENAME = "s10_d1_mnq_mgc_step02b_fetch_manifest.json"

# Required columns in the emitted CSV. Fail-closed if any are missing.
REQUIRED_CSV_COLUMNS = ("ts_event", "open", "high", "low", "close", "volume")


def _read_databento_api_key():
    """Read DATABENTO_API_KEY from environment.

    The key is held in a local variable and passed only as a kwarg to the
    Databento client. It is never printed, logged, hashed, written to a
    file, or otherwise exposed.
    """
    key = os.environ.get("DATABENTO_API_KEY")
    if not key:
        sys.stderr.write(
            "DATABENTO_API_KEY not set in environment. Export it in your local "
            "shell only; do not commit it; do not echo it.\n"
        )
        sys.exit(2)
    return key


def _resolve_output_path(symbol):
    name = DEFAULT_OUTPUT_FILENAMES.get(symbol)
    if name is None:
        sys.stderr.write(f"Unknown symbol {symbol!r}; only {SYMBOLS} are permitted.\n")
        sys.exit(3)
    p = (APPROVED_OUTPUT_DIR / name).resolve()
    approved_resolved = APPROVED_OUTPUT_DIR.resolve()
    try:
        p.relative_to(approved_resolved)
    except ValueError:
        sys.stderr.write(
            f"Resolved output path {p} is outside the approved directory "
            f"{approved_resolved}. Fail-closed.\n"
        )
        sys.exit(4)
    return p


def _ensure_output_dir():
    APPROVED_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _fetch_one_symbol(client, symbol):
    """Fetch one symbol's ohlcv-1d data for the locked date range.

    Returns the DBNStore from databento. The caller is responsible for
    materializing it to disk. This function does NOT print any payload
    contents, and never prints record values.
    """
    data = client.timeseries.get_range(
        dataset=DATASET,
        symbols=[symbol],
        schema=SCHEMA,
        start=START_DATE_INCLUSIVE,
        end=END_DATE_INCLUSIVE,
        stype_in=STYPE_IN,
        # NOTE: no `path=` kwarg -> in-memory DBNStore -> no `.dbn.zst` cache
        # file is written by the client. CSV materialization happens below.
    )
    return data


def _write_csv_via_pandas(data, output_path):
    """Convert DBNStore to DataFrame and write CSV. Counts rows for caller.

    Does NOT print row contents. Does NOT log API payloads. Does NOT inspect
    or summarize OOS performance. Returns (row_count, first_ts, last_ts).
    """
    import pandas as pd  # local import; standard library + databento + pandas only
    df = data.to_df()
    if df is None or len(df) == 0:
        return 0, None, None

    # Validate required columns are present.
    missing = [c for c in REQUIRED_CSV_COLUMNS if c not in df.columns]
    if missing:
        sys.stderr.write(
            f"Output DataFrame missing required columns {missing}; fail-closed.\n"
        )
        sys.exit(5)

    # Ensure ts_event is sorted ascending and serializable.
    df = df.reset_index() if "ts_event" not in df.columns else df
    if "ts_event" not in df.columns:
        sys.stderr.write("ts_event column missing after reset_index; fail-closed.\n")
        sys.exit(5)
    df = df.sort_values("ts_event").reset_index(drop=True)

    df.to_csv(output_path, index=False)

    first_ts = df["ts_event"].iloc[0]
    last_ts = df["ts_event"].iloc[-1]
    # Convert to ISO strings without exposing record content beyond timestamps.
    first_ts = str(first_ts)
    last_ts = str(last_ts)
    return len(df), first_ts, last_ts


def _sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    # Validate sealed-spec scope before any vendor call.
    print(
        f"s10 D1 Step 02b fetch: candidate={CANDIDATE_RECORD_ID} "
        f"dataset={DATASET} schema={SCHEMA} stype_in={STYPE_IN} "
        f"start={START_DATE_INCLUSIVE} end={END_DATE_INCLUSIVE} "
        f"symbols={list(SYMBOLS)}"
    )
    print(f"sealed_spec_commit_anchor: {SEALED_SPEC_COMMIT}")
    print(f"approved_output_dir: {APPROVED_OUTPUT_DIR.resolve()}")
    print(
        "IS window (used by IS-phase modules): "
        f"{IS_WINDOW_START} -> {IS_WINDOW_END}"
    )
    print(
        "OOS window (LOCKED; NOT inspected by this script or any IS-phase code): "
        f"{OOS_WINDOW_START} -> {OOS_WINDOW_END}"
    )

    key = _read_databento_api_key()

    try:
        import databento  # type: ignore  # noqa: F401
    except ImportError:
        sys.stderr.write(
            "databento python client not installed. In your local shell:\n"
            "  pip install databento pandas\n"
        )
        return 6

    _ensure_output_dir()

    client = databento.Historical(key=key)
    # `key` is now held by `client` internally; it is never referenced in
    # any print/log/write below.

    manifest = {
        "schema": "sparta.s10.mnq_mgc.step02b_fetch_manifest.v1",
        "candidate_record_id": CANDIDATE_RECORD_ID,
        "sealed_spec_commit_anchor": SEALED_SPEC_COMMIT,
        "dataset": DATASET,
        "schema_databento": SCHEMA,
        "stype_in": STYPE_IN,
        "start_date_inclusive": START_DATE_INCLUSIVE,
        "end_date_inclusive": END_DATE_INCLUSIVE,
        "is_window_start": IS_WINDOW_START,
        "is_window_end": IS_WINDOW_END,
        "oos_window_start_LOCKED_NOT_INSPECTED": OOS_WINDOW_START,
        "oos_window_end_LOCKED_NOT_INSPECTED": OOS_WINDOW_END,
        "fetch_run_utc": datetime.utcnow().isoformat() + "Z",
        "symbols": [],
        "boundaries_held": {
            "databento_api_key_read_from_env_only": True,
            "databento_api_key_never_printed_or_logged_or_saved": True,
            "no_dbn_zst_cache_written_by_client_no_path_kwarg_passed": True,
            "no_signal_computation": True,
            "no_backtest": True,
            "no_simulator_run": True,
            "no_oos_inspection_by_this_script": True,
            "no_review_queue_mutation": True,
            "no_strategy_lab_promotion": True,
            "no_live_trading": True,
            "raw_csv_only_written_to_approved_directory": True,
        },
    }

    for symbol in SYMBOLS:
        output_path = _resolve_output_path(symbol)
        print(f"fetching {symbol} -> {output_path.name}")
        data = _fetch_one_symbol(client, symbol)
        row_count, first_ts, last_ts = _write_csv_via_pandas(data, output_path)

        if row_count == 0:
            sys.stderr.write(
                f"Symbol {symbol} returned zero rows over the locked date "
                f"range; fail-closed.\n"
            )
            return 7

        sha = _sha256_of_file(output_path)
        size_bytes = os.path.getsize(output_path)
        manifest["symbols"].append({
            "symbol": symbol,
            "output_path": str(output_path).replace("\\", "/"),
            "output_filename": output_path.name,
            "row_count": row_count,
            "size_bytes": size_bytes,
            "sha256": sha,
            "first_timestamp": first_ts,
            "last_timestamp": last_ts,
            "dataset": DATASET,
            "schema": SCHEMA,
            "stype_in": STYPE_IN,
            "start": START_DATE_INCLUSIVE,
            "end": END_DATE_INCLUSIVE,
        })
        # ONLY counts and shas are printed - never row content.
        print(
            f"  {symbol}: {row_count} rows; "
            f"first={first_ts} last={last_ts}; "
            f"sha256={sha}; bytes={size_bytes}"
        )

    manifest_path = APPROVED_OUTPUT_DIR / MANIFEST_FILENAME
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
        f.write("\n")

    manifest_sha = _sha256_of_file(manifest_path)
    manifest_bytes = os.path.getsize(manifest_path)
    print(
        f"manifest written: {manifest_path} "
        f"sha256={manifest_sha} bytes={manifest_bytes}"
    )
    print(
        "PASTE-BACK SAFE SUMMARY: symbol | row_count | first_timestamp | "
        "last_timestamp | sha256 | output_filename. Do NOT paste back: any row "
        "content, any return / sharpe / pnl number, any DATABENTO_API_KEY material."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

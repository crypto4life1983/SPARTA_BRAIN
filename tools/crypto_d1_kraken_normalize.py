"""SPARTA Crypto-D1 Kraken Normalize v1 -- offline operator tool (research-only).

Normalizes operator-supplied, manually-downloaded Kraken daily OHLCVT export
files (BTC / ETH / SOL spot, USD-quoted) into a single canonical Crypto-D1
dataset under::

    data/crypto_d1_research/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V001/

The tool is read-only by default. It only materializes files when ``--write``
is passed, and only emits freeze artifacts (``CHECKSUMS.txt`` +
``FREEZE_RECORD.txt``) when ``--freeze`` is *also* passed. It NEVER runs QA,
NEVER runs a backtest, NEVER fetches data, and NEVER touches paper / live
execution flows.

Hard boundaries (asserted by the companion test suite via source + AST scan):
- **No network.** No ``urllib`` / ``requests`` / ``socket`` / ``http`` /
  ``ftplib`` import. The tool reads only local files passed via ``--raw-dir``.
- **No subprocess.** No ``subprocess`` / ``os.system`` / ``popen``.
- **No credentials.** No ``os.environ`` read, no ``.env`` read, no API key,
  no broker / exchange SDK (``ccxt`` / ``krakenex`` / ...).
- **No scheduler / daemon.**
- **Write-jail.** Every write path is resolved and checked to live strictly
  inside the single approved dataset directory above; anything else raises.
- **Input is read-only.** ``--raw-dir`` files are opened for reading only.

The raw input is the standard Kraken daily OHLCVT CSV (no header):
``unix_time, open, high, low, close, volume[, trade_count]``. The tool selects
ONLY the three exact daily filenames ``XBTUSD_1440.csv`` / ``ETHUSD_1440.csv`` /
``SOLUSD_1440.csv`` (``1440`` = daily in minutes); pointing ``--raw-dir`` at the
full Kraken dump ignores every other interval / quote / name variant. A leading
header row, if present, is skipped.

Output canonical CSV schema (one combined file, all three assets)::

    timestamp,open,high,low,close,volume,symbol,source,quote_currency,trade_count

Timestamps are ISO-8601 UTC bar-open (``YYYY-MM-DDT00:00:00Z``). The covered
range is 2021-06-17 .. 2025-12-31 inclusive (1659 daily bars per asset over a
complete 24/7 calendar; 4977 rows total when no day is missing).

CLI::

    # dry run (default): inspect, write nothing
    python tools/crypto_d1_kraken_normalize.py --raw-dir <DIR>
    # materialize the dataset files
    python tools/crypto_d1_kraken_normalize.py --raw-dir <DIR> --write
    # materialize and freeze (checksums + freeze record)
    python tools/crypto_d1_kraken_normalize.py --raw-dir <DIR> --write --freeze

QA is intentionally NOT run here: ``fees.json`` ships with a
``PLACEHOLDER_FILL_BEFORE_QA`` sentinel, so the dataset manifest carries
``QA_status = QA_DRAFT`` until the operator fills the fee schedule and runs the
separate Crypto-D1 QA harness. A FROZEN dataset is still NOT research-eligible
until it earns QA_PASS (or an approved QA_WARN note). Clean OHLCV data does not
imply profit.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

# --------------------------------------------------------------------------
# Pinned dataset identity + scope (a data change requires a NEW version).
# --------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

DATASET_ID = "CRYPTO_D1_SPOT_BTC_ETH_SOL_V001"
DATASET_VERSION = "V001"
DATASET_REL = f"data/crypto_d1_research/{DATASET_ID}/{DATASET_VERSION}"

MANIFEST_VERSION = "crypto_d1_dataset_manifest_v1"
DATA_CONTRACT_VERSION = "crypto_d1_data_contract_v1"
PROTOCOL_VERSION = "crypto_d1_protocol_v1"

RESEARCH_LANE = "crypto_d1_protocol"
MARKET_TYPE = "spot"
TIMEFRAME = "1d"
QUOTE_CURRENCY = "USD"

RANGE_START = date(2021, 6, 17)
RANGE_END = date(2025, 12, 31)

OPERATOR_LABEL = "Mahmoud Cherif — operator manual Kraken intake"
SOURCE_NAME = "Kraken"
SOURCE_TYPE = "operator_manual_offline_file"

# Exact approved Kraken daily (1440-minute) USD-quote export filenames, one per
# canonical asset. Matching is by EXACT filename (case-insensitive) only -- no
# prefix matching -- so that pointing --raw-dir at the full Kraken dump selects
# precisely these three files and ignores every other interval / quote / name
# variant (e.g. XBTUSD1_1440.csv, XBTUSDC_1440.csv, ETHUSD1_1440.csv, lower
# intervals like XBTUSD_60.csv). Adding an asset requires a new dataset version.
EXPECTED_DAILY_FILES: dict[str, str] = {
    "BTC": "XBTUSD_1440.csv",
    "ETH": "ETHUSD_1440.csv",
    "SOL": "SOLUSD_1440.csv",
}
_FILENAME_TO_ASSET = {v.upper(): k for k, v in EXPECTED_DAILY_FILES.items()}
ASSET_ORDER = ("BTC", "ETH", "SOL")

CSV_HEADER = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "symbol",
    "source",
    "quote_currency",
    "trade_count",
)

# Sentinel that keeps the dataset at QA_DRAFT until the operator fills real
# fee / slippage assumptions and runs the separate QA harness.
SENTINEL = "PLACEHOLDER_FILL_BEFORE_QA"

DATA_FILE = "daily_ohlcv.csv"
MANIFEST_FILE = "manifest.json"
FEES_FILE = "fees.json"
CHECKSUMS_FILE = "CHECKSUMS.txt"
FREEZE_RECORD_FILE = "FREEZE_RECORD.txt"


class KrakenNormalizeError(Exception):
    """Raised on any contract / safety / data-integrity violation."""


# --------------------------------------------------------------------------
# Time helpers
# --------------------------------------------------------------------------

def _iso_bar_open(d: date) -> str:
    """ISO-8601 UTC bar-open timestamp for a daily bar (left-closed)."""
    return f"{d.isoformat()}T00:00:00Z"


def _unix_to_utc_date(token: str) -> date:
    """Convert a Kraken unix-seconds bar-open token to its UTC calendar date."""
    try:
        secs = int(token)
    except (TypeError, ValueError) as exc:
        raise KrakenNormalizeError(
            f"non-integer unix timestamp: {token!r}"
        ) from exc
    if secs <= 0:
        raise KrakenNormalizeError(f"non-positive unix timestamp: {secs}")
    dt = datetime.fromtimestamp(secs, tz=timezone.utc)
    return dt.date()


def _all_dates_in_range() -> list[date]:
    out: list[date] = []
    cur = RANGE_START
    while cur <= RANGE_END:
        out.append(cur)
        cur += timedelta(days=1)
    return out


def expected_rows_per_asset() -> int:
    return len(_all_dates_in_range())


# --------------------------------------------------------------------------
# Raw file discovery + parsing (read-only)
# --------------------------------------------------------------------------

def classify_raw_file(path: Path) -> str | None:
    """Return the canonical asset (BTC/ETH/SOL) for an EXACT approved daily
    filename (case-insensitive), else None. No prefix / interval / quote-variant
    matching: only ``XBTUSD_1440.csv`` / ``ETHUSD_1440.csv`` / ``SOLUSD_1440.csv``
    are recognized."""
    return _FILENAME_TO_ASSET.get(path.name.upper())


def _looks_like_header(fields: list[str]) -> bool:
    """A first row is a header when its first cell is not an int timestamp."""
    if not fields:
        return False
    try:
        int(fields[0].strip())
        return False
    except ValueError:
        return True


def read_kraken_file(path: Path) -> list[list[str]]:
    """Read a Kraken daily OHLCVT CSV (read-only). Returns raw string rows
    ``[ts, open, high, low, close, volume, trade_count?]``. A header is skipped.
    """
    rows: list[list[str]] = []
    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        first = True
        for raw in reader:
            fields = [c.strip() for c in raw]
            if not fields or all(c == "" for c in fields):
                continue
            if first:
                first = False
                if _looks_like_header(fields):
                    continue
            if len(fields) < 6:
                raise KrakenNormalizeError(
                    f"{path.name}: row has fewer than 6 columns: {fields!r}"
                )
            rows.append(fields)
    if not rows:
        raise KrakenNormalizeError(f"{path.name}: no data rows found")
    return rows


# --------------------------------------------------------------------------
# Normalization (pure + deterministic: no clock, no I/O)
# --------------------------------------------------------------------------

def _check_positive_float(name: str, token: str) -> float:
    try:
        val = float(token)
    except (TypeError, ValueError) as exc:
        raise KrakenNormalizeError(f"{name} not numeric: {token!r}") from exc
    if val <= 0:
        raise KrakenNormalizeError(f"{name} must be positive: {val}")
    return val


def _normalize_one_asset(
    asset: str, source: str, raw_rows: list[list[str]]
) -> list[list[str]]:
    """Normalize one asset's raw rows into canonical output rows, in-range,
    range-filtered, de-duplicated, OHLC-validated, ascending by date."""
    by_date: dict[date, list[str]] = {}
    for fields in raw_rows:
        d = _unix_to_utc_date(fields[0])
        if d < RANGE_START or d > RANGE_END:
            continue  # partial-day / out-of-range bars excluded
        o = _check_positive_float("open", fields[1])
        h = _check_positive_float("high", fields[2])
        low = _check_positive_float("low", fields[3])
        c = _check_positive_float("close", fields[4])
        try:
            vol = float(fields[5])
        except (TypeError, ValueError) as exc:
            raise KrakenNormalizeError(
                f"{asset}: volume not numeric: {fields[5]!r}"
            ) from exc
        if vol < 0:
            raise KrakenNormalizeError(f"{asset}: negative volume: {vol}")
        if h < max(o, c, low):
            raise KrakenNormalizeError(
                f"{asset} {d}: high {h} < max(open,close,low)"
            )
        if low > min(o, c, h):
            raise KrakenNormalizeError(
                f"{asset} {d}: low {low} > min(open,close,high)"
            )
        trade_count = ""
        if len(fields) >= 7 and fields[6] != "":
            try:
                tc = int(float(fields[6]))
            except (TypeError, ValueError) as exc:
                raise KrakenNormalizeError(
                    f"{asset} {d}: trade_count not numeric: {fields[6]!r}"
                ) from exc
            if tc < 0:
                raise KrakenNormalizeError(
                    f"{asset} {d}: negative trade_count: {tc}"
                )
            trade_count = str(tc)
        if d in by_date:
            raise KrakenNormalizeError(
                f"{asset} {d}: duplicate (symbol, timestamp) row"
            )
        by_date[d] = [
            _iso_bar_open(d),
            fields[1],
            fields[2],
            fields[3],
            fields[4],
            fields[5],
            asset,
            source,
            QUOTE_CURRENCY,
            trade_count,
        ]
    return [by_date[d] for d in sorted(by_date)]


def normalize(raw_dir: Path) -> dict:
    """Read every recognized raw file in ``raw_dir`` and produce the canonical
    combined dataset plus per-asset statistics. Pure with respect to the wall
    clock: identical raw input yields byte-identical ``csv_text``."""
    if not raw_dir.is_dir():
        raise KrakenNormalizeError(f"--raw-dir is not a directory: {raw_dir}")

    found: dict[str, Path] = {}
    for p in sorted(raw_dir.rglob("*")):
        if not p.is_file():
            continue
        asset = classify_raw_file(p)
        if asset is None:
            continue
        if asset in found:
            raise KrakenNormalizeError(
                f"duplicate exact daily file for {asset}: {found[asset]} and "
                f"{p} (expected exactly one {EXPECTED_DAILY_FILES[asset]})"
            )
        found[asset] = p

    missing_assets = [a for a in ASSET_ORDER if a not in found]
    if missing_assets:
        wanted = ", ".join(f"{a} ({EXPECTED_DAILY_FILES[a]})" for a in missing_assets)
        raise KrakenNormalizeError(
            f"missing required raw file(s) for: {wanted}"
        )

    rows: list[list[str]] = []
    per_asset: dict[str, dict] = {}
    all_range_dates = set(_all_dates_in_range())
    for asset in ASSET_ORDER:
        path = found[asset]
        source = f"{SOURCE_NAME.lower()}:{path.name}"
        asset_rows = _normalize_one_asset(
            asset, source, read_kraken_file(path)
        )
        observed = {
            datetime.strptime(r[0][:10], "%Y-%m-%d").date() for r in asset_rows
        }
        missing = sorted(all_range_dates - observed)
        per_asset[asset] = {
            "raw_file": path.name,
            "source": source,
            "row_count": len(asset_rows),
            "missing_day_count": len(missing),
            "missing_days": [d.isoformat() for d in missing],
            "first_bar": asset_rows[0][0] if asset_rows else None,
            "last_bar": asset_rows[-1][0] if asset_rows else None,
        }
        rows.extend(asset_rows)

    csv_text = _csv_text(rows)
    return {
        "rows": rows,
        "csv_text": csv_text,
        "per_asset": per_asset,
        "row_count_total": len(rows),
        "row_count_expected_per_asset": expected_rows_per_asset(),
        "row_count_expected_total": expected_rows_per_asset() * len(ASSET_ORDER),
    }


def _csv_text(rows: Iterable[list[str]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    writer.writerow(CSV_HEADER)
    for r in rows:
        writer.writerow(r)
    return buf.getvalue()


# --------------------------------------------------------------------------
# Manifest + fees + freeze artifacts
# --------------------------------------------------------------------------

def build_fees() -> dict:
    """Fee / slippage schedule stub. The sentinel keeps QA at QA_DRAFT until
    the operator fills real, dated, sourced Kraken fees."""
    return {
        "status": SENTINEL,
        "venue": SOURCE_NAME,
        "note": (
            "Fill real dated per-venue TAKER + MAKER fees, a conservative "
            "slippage haircut, and a spread proxy before running the Crypto-D1 "
            "QA harness. Until then QA_status stays QA_DRAFT."
        ),
        "taker_fee_bps": SENTINEL,
        "maker_fee_bps": SENTINEL,
        "slippage_bps": SENTINEL,
        "spread_proxy_bps": SENTINEL,
        "fee_tier": SENTINEL,
        "default_fill_assumption": "TAKER",
        "fees_dated_as_of": SENTINEL,
        "source_reference": SENTINEL,
    }


def build_manifest(result: dict, freeze: bool, now: datetime) -> dict:
    """Construct the per-dataset manifest (the 35 required Crypto-D1 fields plus
    a few audit extras). ``freeze`` controls only ``freeze_status``."""
    per_asset = result["per_asset"]
    return {
        "manifest_version": MANIFEST_VERSION,
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "created_at": now.astimezone(timezone.utc).isoformat(),
        "created_by": OPERATOR_LABEL,
        "research_lane": RESEARCH_LANE,
        "market_type": MARKET_TYPE,
        "assets": list(ASSET_ORDER),
        "symbols": list(ASSET_ORDER),
        "quote_currency": QUOTE_CURRENCY,
        "timeframe": TIMEFRAME,
        "time_start": RANGE_START.isoformat(),
        "time_end": RANGE_END.isoformat(),
        "timezone": "UTC",
        "bar_boundary": "UTC 00:00:00, left-closed / right-open (bar-open)",
        "data_frequency": "1d",
        "source_type": SOURCE_TYPE,
        "source_name": SOURCE_NAME,
        "source_location": f"{DATASET_REL}/{DATA_FILE}",
        "data_contract_version": DATA_CONTRACT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "checksum_policy": f"sha256 per file, recorded in {CHECKSUMS_FILE}",
        "row_count_expected": result["row_count_expected_total"],
        "row_count_actual": result["row_count_total"],
        "missing_day_policy": (
            "Missing daily bars are flagged per asset in missing_day_list; "
            "never silently forward-filled."
        ),
        "duplicate_policy": (
            "Duplicate (symbol, timestamp) rows are rejected at normalization "
            "time; a duplicate is a hard error."
        ),
        "partial_day_policy": (
            "Partial-day / out-of-range bars are excluded; only fully-closed "
            "UTC daily bars inside the declared range are kept."
        ),
        "zero_volume_policy": (
            "Zero-volume daily bars are retained as-is and must be reviewed by "
            "the QA harness; not silently dropped, not silently accepted."
        ),
        "outlier_policy": (
            "Outlier / suspicious-bar detection is deferred to the Crypto-D1 "
            "QA harness; this tool only enforces OHLC self-consistency."
        ),
        "normalization_policy": (
            "Kraken USD-quote daily OHLCVT exports mapped to canonical "
            "BTC/ETH/SOL; venue aliases XBTUSD->BTC, ETHUSD->ETH, SOLUSD->SOL; "
            "unix-seconds bar-open converted to ISO-8601 UTC; prices kept as "
            "source strings to avoid precision loss."
        ),
        "fee_slippage_assumption_reference": (
            f"{FEES_FILE} ({SENTINEL}: fees not yet filled — QA_status stays "
            "QA_DRAFT until completed)"
        ),
        "freeze_status": "FROZEN" if freeze else "DRAFT",
        "QA_status": "QA_DRAFT",
        "allowed_use": (
            "Research-only offline input to the Crypto-D1 QA harness. Must earn "
            "QA_PASS (or an approved QA_WARN note) before any pre-registered "
            "backtest may cite it."
        ),
        "forbidden_use": (
            "No live trading. No paper-order execution. No order placement. "
            "Does not authorize a backtest. Does not imply profitability or "
            "edge. A good historical chart does not imply future returns."
        ),
        "notes": (
            "Operator-manual offline Kraken intake. No network call was made "
            "by SPARTA to obtain this data; the operator downloaded the Kraken "
            "historical OHLCVT exports out-of-band. Kraken Terms-of-Service "
            "evidence for research use must be cited in FREEZE_RECORD.txt "
            "before QA. FROZEN means checksummed and immutable, NOT QA-passed "
            "and NOT research-eligible."
        ),
        "missing_day_list": {
            a: {
                "count": per_asset[a]["missing_day_count"],
                "dates": per_asset[a]["missing_days"],
            }
            for a in ASSET_ORDER
        },
        "per_asset_row_count": {
            a: per_asset[a]["row_count"] for a in ASSET_ORDER
        },
        "row_count_expected_per_asset": result["row_count_expected_per_asset"],
        "row_level_provenance": {
            a: per_asset[a]["source"] for a in ASSET_ORDER
        },
    }


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_checksums(file_bytes: dict[str, bytes]) -> str:
    """Render a ``CHECKSUMS.txt`` (``<sha256>  <name>`` per line, sorted)."""
    lines = [
        f"{_sha256_bytes(file_bytes[name])}  {name}"
        for name in sorted(file_bytes)
    ]
    return "\n".join(lines) + "\n"


def build_freeze_record(
    file_bytes: dict[str, bytes], now: datetime
) -> str:
    record = {
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "freeze_timestamp": now.astimezone(timezone.utc).isoformat(),
        "operator": OPERATOR_LABEL,
        "source_name": SOURCE_NAME,
        "manifest_version": MANIFEST_VERSION,
        "data_contract_version": DATA_CONTRACT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "kraken_tos_evidence_reference": (
            f"{SENTINEL}: cite the Kraken Terms-of-Service clause permitting "
            "research use of downloaded historical OHLCVT exports, plus the "
            "download date and the operator who performed the offline download."
        ),
        "frozen_files": sorted(file_bytes),
        "freeze_means": (
            "Files are checksummed and immutable. FROZEN does NOT mean "
            "QA-passed; QA_status is QA_DRAFT. No backtest, paper, or live "
            "trading is authorized by this freeze."
        ),
    }
    return json.dumps(record, indent=2, ensure_ascii=False) + "\n"


# --------------------------------------------------------------------------
# Write-jail + materialization
# --------------------------------------------------------------------------

def _out_dir(repo_root: Path) -> Path:
    return repo_root / DATASET_REL


def _jail_target(out_dir: Path, name: str) -> Path:
    base = out_dir.resolve()
    target = (out_dir / name).resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise KrakenNormalizeError(
            f"refusing to write outside dataset dir {base}: {target}"
        ) from exc
    return target


def materialize(
    result: dict,
    repo_root: Path,
    write: bool,
    freeze: bool,
    now: datetime,
) -> dict:
    """Produce the in-memory artifact set and, when ``write`` is set, write it
    to disk inside the write-jail. ``freeze`` additionally emits the freeze
    artifacts. Returns the file plan (names + sha256), regardless of write."""
    if freeze and not write:
        raise KrakenNormalizeError("--freeze requires --write")

    manifest = build_manifest(result, freeze=freeze, now=now)
    fees = build_fees()

    csv_bytes = result["csv_text"].encode("utf-8")
    manifest_bytes = (
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    fees_bytes = (
        json.dumps(fees, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")

    data_files: dict[str, bytes] = {
        DATA_FILE: csv_bytes,
        MANIFEST_FILE: manifest_bytes,
        FEES_FILE: fees_bytes,
    }

    extra_files: dict[str, bytes] = {}
    if freeze:
        extra_files[CHECKSUMS_FILE] = build_checksums(data_files).encode("utf-8")
        extra_files[FREEZE_RECORD_FILE] = build_freeze_record(
            data_files, now
        ).encode("utf-8")

    all_files = {**data_files, **extra_files}
    plan = {
        "out_dir": str(_out_dir(repo_root)),
        "files": {
            name: {
                "bytes": len(blob),
                "sha256": _sha256_bytes(blob),
            }
            for name, blob in all_files.items()
        },
        "manifest": manifest,
        "fees": fees,
        "written": False,
        "frozen": False,
    }

    if not write:
        return plan

    out_dir = _out_dir(repo_root)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, blob in all_files.items():
        target = _jail_target(out_dir, name)
        with open(target, "wb") as fh:
            fh.write(blob)
    plan["written"] = True
    plan["frozen"] = bool(freeze)
    return plan


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _print_summary(result: dict, plan: dict, write: bool, freeze: bool) -> None:
    print("SPARTA Crypto-D1 Kraken Normalize v1 (research-only, offline)")
    print(f"  dataset_id:        {DATASET_ID}")
    print(f"  dataset_version:   {DATASET_VERSION}")
    print(f"  range:             {RANGE_START} .. {RANGE_END} (inclusive)")
    print(f"  rows (actual):     {result['row_count_total']}")
    print(f"  rows (expected):   {result['row_count_expected_total']}")
    for asset in ASSET_ORDER:
        pa = result["per_asset"][asset]
        print(
            f"    {asset}: {pa['row_count']} rows "
            f"(missing {pa['missing_day_count']}) from {pa['raw_file']}"
        )
    mode = "DRY-RUN (no files written)"
    if write and freeze:
        mode = "WRITE + FREEZE"
    elif write:
        mode = "WRITE (not frozen)"
    print(f"  mode:              {mode}")
    print(f"  out_dir:           {plan['out_dir']}")
    print("  files:")
    for name, meta in plan["files"].items():
        print(f"    - {name}  ({meta['bytes']} bytes, sha256 {meta['sha256'][:12]}…)")
    print(
        "  QA_status:         QA_DRAFT  (fees are "
        f"{SENTINEL}; QA harness not run by this tool)"
    )
    print(
        "  reminder:          FROZEN != QA-passed. No backtest, paper, or live "
        "trading is authorized. Clean OHLCV data does not imply profit."
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize operator-supplied offline Kraken daily OHLCVT exports "
            "(BTC/ETH/SOL spot, USD) into the canonical Crypto-D1 dataset. "
            "Read-only by default; offline only; no network, no credentials, "
            "no QA, no backtest."
        )
    )
    parser.add_argument(
        "--raw-dir",
        required=True,
        help="directory holding the operator's Kraken daily CSVs (read-only)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="materialize the dataset files (default is dry-run)",
    )
    parser.add_argument(
        "--freeze",
        action="store_true",
        help=f"also emit {CHECKSUMS_FILE} + {FREEZE_RECORD_FILE} (requires --write)",
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="repo root (write-jail anchor); defaults to the SPARTA repo root",
    )
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    raw_dir = Path(args.raw_dir).resolve()
    now = datetime.now(timezone.utc)

    try:
        result = normalize(raw_dir)
        plan = materialize(
            result,
            repo_root=repo_root,
            write=args.write,
            freeze=args.freeze,
            now=now,
        )
    except KrakenNormalizeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    _print_summary(result, plan, write=args.write, freeze=args.freeze)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

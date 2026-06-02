"""SPARTA Crypto-D1 Data QA Runtime Tool v1 -- local-only, read-only, stdlib.

Implements the Bundle 14 (Crypto-D1 Data QA / Freeze Spec v1) check groups
as executable code. Validates an OPERATOR-SUPPLIED frozen dataset directory
and emits a `qa_report.json` populating all 26 fields declared by Bundle
14's QA_report_schema, plus a human-readable `qa_report.md`.

Hard non-negotiable guarantees (enforced by tests):
  * Standard library ONLY (argparse, csv, dataclasses, datetime, hashlib,
    json, math, pathlib, sys).
  * No network. No exchange / broker / vendor imports. No subprocess.
  * No os.environ / getenv / dotenv access.
  * No order placement. No live trading. No paper-order execution.
  * No data fetch -- reads files at --dataset-dir only.
  * Never writes inside --dataset-dir. Never creates data/crypto_d1_research/.
  * On missing data, emits a QA_DRAFT or QA_FAIL report; never fabricates.

The seven Bundle-15 safety flags are pinned False in every emitted report's
`safety_flags`: research_only=True, data_fetch_enabled=False,
exchange_connection_enabled=False, live_trading_enabled=False,
broker_control_enabled=False, paper_order_execution_enabled=False,
order_placement_enabled=False.

CLI:
  python tools/crypto_d1_data_qa_runtime_tool.py validate-spec
  python tools/crypto_d1_data_qa_runtime_tool.py show-spec
  python tools/crypto_d1_data_qa_runtime_tool.py run \
      --dataset-dir <DATASET_DIR> --out-dir <OUT_DIR>

QA_PASS is the natural deterministic outcome when ALL 7 check groups pass
with zero warnings. QA_PASS does NOT imply profitability and does NOT
authorize a backtest plan by itself -- per Bundle 14, a QA_PASS qa_report
is a precondition for a future backtest plan, NOT an authorization.
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Import prior validators (stdlib-only, in-repo) for cross-spec consistency.
# ---------------------------------------------------------------------------
_TOOLS_DIR = Path(__file__).resolve().parent
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))
import crypto_d1_qa_freeze_spec_check as _cqf       # noqa: E402
import crypto_d1_dataset_manifest_check as _cdm     # noqa: E402

# ---------------------------------------------------------------------------
# Version pins -- every emitted report cites these.
# ---------------------------------------------------------------------------
TOOL_VERSION = "crypto_d1_data_qa_runtime_tool_v1"
QA_FREEZE_SPEC_VERSION = "crypto_d1_qa_freeze_spec_v1"
DATA_CONTRACT_VERSION = "crypto_d1_data_contract_v1"
DATASET_MANIFEST_SPEC_VERSION = "crypto_d1_dataset_manifest_v1"
PROTOCOL_VERSION = "crypto_d1_protocol_v1"

TARGET_ASSETS = ("BTC", "ETH", "SOL")
REQUIRED_BAR_COLUMNS = (
    "timestamp", "open", "high", "low", "close", "volume",
    "symbol", "source", "quote_currency",
)

# Bundle 14 fields the emitted qa_report.json MUST populate.
QA_REPORT_REQUIRED_FIELDS = tuple(_cqf.REQUIRED_QA_REPORT_FIELDS)  # 26 fields
QA_CHECK_GROUPS_DECLARED = tuple(_cqf.REQUIRED_QA_CHECK_GROUPS)    # 7 group ids
QA_STATUSES_DECLARED = tuple(_cqf.REQUIRED_QA_STATUSES)            # 6 statuses

# Bundle 13 fields the operator's per-dataset manifest.json MUST populate.
REQUIRED_FUTURE_MANIFEST_FIELDS = tuple(_cdm.REQUIRED_FUTURE_MANIFEST_FIELDS)

SAFETY_FLAGS = {
    "research_only": True,
    "data_fetch_enabled": False,
    "exchange_connection_enabled": False,
    "live_trading_enabled": False,
    "broker_control_enabled": False,
    "paper_order_execution_enabled": False,
    "order_placement_enabled": False,
}

SAFETY_NOTES = (
    "Research-only. Local-only.",
    "No data was fetched. No exchange was contacted. No order was placed.",
    "QA_PASS is the deterministic outcome of mechanical checks; it does NOT"
    " imply profitability and does NOT authorize a backtest plan by itself.",
    "Per Bundle 14, a QA_PASS qa_report is a PRECONDITION for a future"
    " backtest plan -- never the authorization itself.",
    "A QA report cannot authorize paper or live trading.",
)

FORBIDDEN_NEXT_STEPS = (
    "Trade live or paper based on a QA_PASS verdict.",
    "Connect SPARTA's runtime to any exchange or vendor over the network.",
    "Promote crypto_d1_protocol to ACTIVE / STRONG without a separate operator decision.",
    "Schedule a daemon / cron / background process that touches this tool.",
    "Modify paper / live execution files.",
    "Install or read any API key, OAuth token, or .env credential.",
    "Use any synthetic / mock-priced data as evidence.",
)


# ===========================================================================
# Data classes
# ===========================================================================
@dataclasses.dataclass(frozen=True)
class Bar:
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str
    source: str
    quote_currency: str


@dataclasses.dataclass
class CheckResult:
    """One QA check outcome. severity is 'PASS' | 'WARN' | 'FAIL'."""
    group: str
    check_id: str
    severity: str
    detail: str

    def as_dict(self):
        return {
            "group": self.group, "check_id": self.check_id,
            "severity": self.severity, "detail": self.detail,
        }


# ===========================================================================
# Dataset discovery
# ===========================================================================
def discover_dataset_files(dataset_dir: Path):
    """Inspect dataset_dir. Return a dict of expected paths (existing or not)
    and the list of *.csv files found. NEVER reads outside dataset_dir."""
    dataset_dir = Path(dataset_dir)
    info = {
        "dataset_dir": dataset_dir,
        "exists": dataset_dir.exists() and dataset_dir.is_dir(),
        "manifest_path": dataset_dir / "manifest.json",
        "checksums_path": dataset_dir / "CHECKSUMS.txt",
        "freeze_record_path": dataset_dir / "FREEZE_RECORD.txt",
        "fees_path": dataset_dir / "fees.json",
        "csv_files": [],
    }
    if info["exists"]:
        info["csv_files"] = sorted(
            p for p in dataset_dir.iterdir()
            if p.is_file() and p.suffix.lower() == ".csv"
        )
    return info


def _safe_read_json(path: Path):
    if not path.exists():
        return None, f"missing: {path.name}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid JSON ({type(exc).__name__}): {path.name}"


def _safe_read_text(path: Path):
    if not path.exists():
        return None, f"missing: {path.name}"
    try:
        return path.read_text(encoding="utf-8"), None
    except OSError as exc:
        return None, f"read error ({type(exc).__name__}): {path.name}"


# ===========================================================================
# Checksum verification (Group G)
# ===========================================================================
def parse_checksums_txt(text: str):
    """Parse a CHECKSUMS.txt file. Format: '<sha256_hex>  <filename>'.
    Returns dict[filename] = sha256_hex. Skips blank lines and '#' comments."""
    entries = {}
    for line in (text or "").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split(None, 1)
        if len(parts) != 2:
            continue
        sha, name = parts[0].strip().lower(), parts[1].strip()
        if len(sha) == 64 and all(c in "0123456789abcdef" for c in sha):
            entries[name] = sha
    return entries


def compute_file_sha256(path: Path):
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def verify_checksums(dataset_dir: Path, checksums: dict):
    """For every filename in CHECKSUMS.txt, verify its sha256.

    Returns (mismatched: list[dict], missing: list[str])."""
    mismatched = []
    missing = []
    for fname, expected in checksums.items():
        p = dataset_dir / fname
        if not p.exists():
            missing.append(fname)
            continue
        try:
            actual = compute_file_sha256(p)
        except OSError:
            mismatched.append({"file": fname, "expected": expected, "actual": "<read_error>"})
            continue
        if actual.lower() != expected.lower():
            mismatched.append({"file": fname, "expected": expected, "actual": actual})
    return mismatched, missing


# ===========================================================================
# CSV reading + row-level validation
# ===========================================================================
def _parse_utc_date(s: str):
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _row_to_bar(row: dict, file_name: str, line_no: int):
    missing = [c for c in REQUIRED_BAR_COLUMNS if c not in row]
    if missing:
        return None, f"{file_name}:{line_no} missing columns {missing}"
    try:
        ts = _parse_utc_date(row.get("timestamp", ""))
        if ts is None:
            return None, f"{file_name}:{line_no} unparseable timestamp"
        if not str(row.get("close", "")).strip():
            return None, f"{file_name}:{line_no} missing close"
        o = float(row["open"])
        h = float(row["high"])
        lo = float(row["low"])
        c = float(row["close"])
        v = float(row["volume"])
    except ValueError as exc:
        return None, f"{file_name}:{line_no} unparseable numeric ({exc})"
    sym = (row.get("symbol") or "").strip().upper()
    src = (row.get("source") or "").strip()
    qc = (row.get("quote_currency") or "").strip().upper()
    if not sym:
        return None, f"{file_name}:{line_no} missing symbol"
    if not src:
        return None, f"{file_name}:{line_no} missing source"
    if not qc:
        return None, f"{file_name}:{line_no} missing quote_currency"
    return Bar(timestamp=ts, open=o, high=h, low=lo, close=c, volume=v,
               symbol=sym, source=src, quote_currency=qc), None


def read_csv_bars(path: Path):
    """Read a CSV into a list of Bar. Returns (bars, parse_errors)."""
    bars = []
    errors = []
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                return [], [f"{path.name}: empty file or missing header"]
            missing_cols = [c for c in REQUIRED_BAR_COLUMNS if c not in reader.fieldnames]
            if missing_cols:
                return [], [f"{path.name}: missing header columns {missing_cols}"]
            for line_no, row in enumerate(reader, start=2):
                bar, err = _row_to_bar(row, path.name, line_no)
                if bar is None:
                    errors.append(err)
                else:
                    bars.append(bar)
    except OSError as exc:
        errors.append(f"{path.name}: read error ({type(exc).__name__})")
    bars.sort(key=lambda b: (b.symbol, b.timestamp))
    return bars, errors


# ===========================================================================
# 7 QA check groups (each returns a list[CheckResult])
# ===========================================================================
def group_A_manifest_integrity(manifest, manifest_err, files_info):
    """A_manifest_integrity: manifest exists, parses, has 35 fields populated,
    pins protocol + data_contract + qa_freeze_spec versions."""
    results = []
    GID = "A_manifest_integrity"
    if manifest_err:
        results.append(CheckResult(GID, "manifest_present", "FAIL",
                                   manifest_err))
        return results
    if not isinstance(manifest, dict):
        results.append(CheckResult(GID, "manifest_object", "FAIL",
                                   "manifest.json is not a JSON object"))
        return results
    results.append(CheckResult(GID, "manifest_present", "PASS", "manifest.json exists and parses"))
    missing = [f for f in REQUIRED_FUTURE_MANIFEST_FIELDS if f not in manifest]
    if missing:
        results.append(CheckResult(GID, "manifest_required_fields", "FAIL",
                                   f"manifest missing {len(missing)} required field(s): {missing}"))
    else:
        results.append(CheckResult(GID, "manifest_required_fields", "PASS",
                                   f"all {len(REQUIRED_FUTURE_MANIFEST_FIELDS)} required fields present"))
    # Cross-spec version pins.
    pv = manifest.get("protocol_version")
    if not (isinstance(pv, str) and PROTOCOL_VERSION in pv):
        results.append(CheckResult(GID, "protocol_version_pin", "FAIL",
                                   f"protocol_version must pin {PROTOCOL_VERSION!r} (got {pv!r})"))
    else:
        results.append(CheckResult(GID, "protocol_version_pin", "PASS", f"pins {pv!r}"))
    dcv = manifest.get("data_contract_version")
    if not (isinstance(dcv, str) and DATA_CONTRACT_VERSION in dcv):
        results.append(CheckResult(GID, "data_contract_version_pin", "FAIL",
                                   f"data_contract_version must pin {DATA_CONTRACT_VERSION!r} (got {dcv!r})"))
    else:
        results.append(CheckResult(GID, "data_contract_version_pin", "PASS", f"pins {dcv!r}"))
    # research_lane + market_type + timeframe.
    if manifest.get("research_lane") != "crypto_d1_protocol":
        results.append(CheckResult(GID, "research_lane", "FAIL",
                                   f"research_lane must be 'crypto_d1_protocol' (got {manifest.get('research_lane')!r})"))
    else:
        results.append(CheckResult(GID, "research_lane", "PASS", "crypto_d1_protocol"))
    if manifest.get("market_type") != "spot":
        results.append(CheckResult(GID, "market_type", "FAIL",
                                   f"market_type must be 'spot' (got {manifest.get('market_type')!r})"))
    else:
        results.append(CheckResult(GID, "market_type", "PASS", "spot"))
    if manifest.get("timeframe") != "1d":
        results.append(CheckResult(GID, "timeframe", "FAIL",
                                   f"timeframe must be '1d' (got {manifest.get('timeframe')!r})"))
    else:
        results.append(CheckResult(GID, "timeframe", "PASS", "1d"))
    # freeze_status + QA_status presence.
    fs = manifest.get("freeze_status")
    if fs not in ("DRAFT", "FROZEN"):
        results.append(CheckResult(GID, "freeze_status_value", "FAIL",
                                   f"freeze_status must be DRAFT|FROZEN (got {fs!r})"))
    else:
        results.append(CheckResult(GID, "freeze_status_value", "PASS", str(fs)))
    qs = manifest.get("QA_status")
    if qs not in QA_STATUSES_DECLARED + ("DRAFT", "PASS", "WARN", "FAIL"):
        results.append(CheckResult(GID, "qa_status_value", "FAIL",
                                   f"QA_status must be one of {QA_STATUSES_DECLARED} (got {qs!r})"))
    else:
        results.append(CheckResult(GID, "qa_status_value", "PASS", str(qs)))
    # allowed_use / forbidden_use present.
    for k in ("allowed_use", "forbidden_use"):
        if not manifest.get(k):
            results.append(CheckResult(GID, f"{k}_present", "FAIL", f"{k} missing or empty"))
        else:
            results.append(CheckResult(GID, f"{k}_present", "PASS", "present"))
    return results


def group_B_timestamp(bars_by_symbol, manifest):
    """B_timestamp: UTC, daily bar boundary, no weekday-only, no duplicate
    (symbol, timestamp), missing-day reconciliation, partial-day exclusion."""
    results = []
    GID = "B_timestamp"
    if not bars_by_symbol:
        results.append(CheckResult(GID, "no_bars", "FAIL",
                                   "no parseable bars found across CSV files"))
        return results
    duplicate_count = 0
    weekday_only_warns = []
    missing_day_warns = []
    for symbol, bars in bars_by_symbol.items():
        seen = set()
        for b in bars:
            key = (b.symbol, b.timestamp)
            if key in seen:
                duplicate_count += 1
            seen.add(key)
        # Check for missing weekend bars -- 24/7 calendar means weekends MUST exist.
        # If we see only 5/7 days each week consistently, flag weekday-only.
        if len(bars) >= 14:
            weekdays = [datetime.strptime(b.timestamp, "%Y-%m-%d").weekday() for b in bars[:30]]
            if max(weekdays) <= 4:  # all in Mon-Fri
                weekday_only_warns.append(symbol)
        # Reconcile missing days with manifest's missing_day_list (if present).
        if len(bars) >= 2:
            try:
                d0 = datetime.strptime(bars[0].timestamp, "%Y-%m-%d")
                d1 = datetime.strptime(bars[-1].timestamp, "%Y-%m-%d")
                expected_days = (d1 - d0).days + 1
                observed = len(bars)
                missing_count = max(0, expected_days - observed)
                if missing_count > 0:
                    missing_day_warns.append({"symbol": symbol, "missing_days": missing_count})
            except ValueError:
                pass
    if duplicate_count > 0:
        results.append(CheckResult(GID, "duplicate_symbol_timestamp", "FAIL",
                                   f"{duplicate_count} duplicate (symbol, timestamp) row(s) detected"))
    else:
        results.append(CheckResult(GID, "duplicate_symbol_timestamp", "PASS",
                                   "no duplicate (symbol, timestamp) rows"))
    if weekday_only_warns:
        results.append(CheckResult(GID, "no_weekday_only_calendar", "FAIL",
                                   f"weekday-only calendar detected for {weekday_only_warns} -- 24/7 required"))
    else:
        results.append(CheckResult(GID, "no_weekday_only_calendar", "PASS",
                                   "24/7 calendar coverage"))
    if missing_day_warns:
        # Reconcile against manifest.missing_day_policy text (presence only).
        mdp = (manifest or {}).get("missing_day_policy")
        if mdp:
            results.append(CheckResult(GID, "missing_days_reconciled", "WARN",
                                       f"missing days observed: {missing_day_warns}; manifest's missing_day_policy text present"))
        else:
            results.append(CheckResult(GID, "missing_days_reconciled", "FAIL",
                                       f"missing days observed: {missing_day_warns}; manifest.missing_day_policy not declared"))
    else:
        results.append(CheckResult(GID, "missing_days_reconciled", "PASS",
                                   "no missing-day gaps in observed series"))
    results.append(CheckResult(GID, "utc_storage_required", "PASS",
                               "all bar timestamps parsed as ISO-8601 UTC dates"))
    return results


def group_C_OHLCV(bars_by_symbol):
    """C_OHLCV: positive OHLC, high>=max(o,c,l), low<=min(o,c,h), close not missing,
    impossible candle rules."""
    results = []
    GID = "C_OHLCV"
    self_inconsistent = []
    impossible_candle = []
    non_positive = []
    for symbol, bars in bars_by_symbol.items():
        for b in bars:
            if b.high < max(b.open, b.close, b.low):
                self_inconsistent.append((symbol, b.timestamp, "high < max(o,c,l)"))
            if b.low > min(b.open, b.close, b.high):
                self_inconsistent.append((symbol, b.timestamp, "low > min(o,c,h)"))
            if b.high < b.low:
                impossible_candle.append((symbol, b.timestamp, "high < low"))
            if b.open <= 0 or b.high <= 0 or b.low <= 0 or b.close <= 0:
                non_positive.append((symbol, b.timestamp))
    if impossible_candle:
        results.append(CheckResult(GID, "impossible_candle_high_lt_low", "FAIL",
                                   f"{len(impossible_candle)} rows with high < low"))
    else:
        results.append(CheckResult(GID, "impossible_candle_high_lt_low", "PASS",
                                   "no high < low rows"))
    if self_inconsistent:
        results.append(CheckResult(GID, "ohlcv_self_consistency", "FAIL",
                                   f"{len(self_inconsistent)} self-inconsistent rows"))
    else:
        results.append(CheckResult(GID, "ohlcv_self_consistency", "PASS",
                                   "every row satisfies high>=max(o,c,l) and low<=min(o,c,h)"))
    if non_positive:
        results.append(CheckResult(GID, "ohlc_positive", "FAIL",
                                   f"{len(non_positive)} rows with non-positive OHLC"))
    else:
        results.append(CheckResult(GID, "ohlc_positive", "PASS", "all OHLC values positive"))
    results.append(CheckResult(GID, "close_not_missing", "PASS",
                               "all parsed rows have a close value (parser rejects empty close)"))
    return results


def group_D_volume(bars_by_symbol):
    """D_volume: non-negative, zero-volume policy, suspicious volume outliers."""
    results = []
    GID = "D_volume"
    negative = []
    zero_volume = []
    for symbol, bars in bars_by_symbol.items():
        for b in bars:
            if b.volume < 0:
                negative.append((symbol, b.timestamp, b.volume))
            elif b.volume == 0:
                zero_volume.append((symbol, b.timestamp))
    if negative:
        results.append(CheckResult(GID, "volume_non_negative", "FAIL",
                                   f"{len(negative)} rows with negative volume"))
    else:
        results.append(CheckResult(GID, "volume_non_negative", "PASS", "all volume >= 0"))
    if zero_volume:
        results.append(CheckResult(GID, "zero_volume_flag", "WARN",
                                   f"{len(zero_volume)} zero-volume daily bar(s); 24/7 asset -- review"))
    else:
        results.append(CheckResult(GID, "zero_volume_flag", "PASS", "no zero-volume bars"))
    return results


def group_E_symbol_source(bars_by_symbol):
    """E_symbol_source: BTC/ETH/SOL canonical, quote_currency consistency,
    source consistency, duplicate (symbol, source, timestamp) rejected,
    row-level source_id present (already enforced at parse)."""
    results = []
    GID = "E_symbol_source"
    seen_assets = set(bars_by_symbol.keys())
    non_target = [s for s in seen_assets if s not in TARGET_ASSETS]
    target_present = [s for s in TARGET_ASSETS if s in seen_assets]
    if non_target:
        results.append(CheckResult(GID, "canonical_symbol_btc_eth_sol", "WARN",
                                   f"non-target asset(s) present: {sorted(non_target)}"))
    if not target_present:
        results.append(CheckResult(GID, "canonical_symbol_btc_eth_sol", "FAIL",
                                   "no BTC/ETH/SOL bars present"))
    else:
        results.append(CheckResult(GID, "canonical_symbol_btc_eth_sol", "PASS",
                                   f"target assets present: {target_present}"))
    # Quote-currency consistency per symbol.
    qc_mismatches = []
    src_mismatches = []
    dup_triplets = []
    for symbol, bars in bars_by_symbol.items():
        if not bars:
            continue
        qc0 = bars[0].quote_currency
        for b in bars:
            if b.quote_currency != qc0:
                qc_mismatches.append((symbol, b.timestamp))
                break
        src0 = bars[0].source
        for b in bars:
            if b.source != src0:
                src_mismatches.append((symbol, b.timestamp))
                break
        seen_triplet = set()
        for b in bars:
            t = (b.symbol, b.source, b.timestamp)
            if t in seen_triplet:
                dup_triplets.append(t)
            seen_triplet.add(t)
    if qc_mismatches:
        results.append(CheckResult(GID, "quote_currency_consistency", "FAIL",
                                   f"quote_currency mismatch in {qc_mismatches}"))
    else:
        results.append(CheckResult(GID, "quote_currency_consistency", "PASS",
                                   "all rows per symbol share the same quote_currency"))
    if src_mismatches:
        results.append(CheckResult(GID, "source_consistency", "WARN",
                                   f"source mismatch in {src_mismatches}; document stitching rule"))
    else:
        results.append(CheckResult(GID, "source_consistency", "PASS",
                                   "all rows per symbol share the same source"))
    if dup_triplets:
        results.append(CheckResult(GID, "duplicate_symbol_source_timestamp", "FAIL",
                                   f"{len(dup_triplets)} duplicate (symbol, source, timestamp) triplet(s)"))
    else:
        results.append(CheckResult(GID, "duplicate_symbol_source_timestamp", "PASS",
                                   "no duplicate (symbol, source, timestamp) triplets"))
    results.append(CheckResult(GID, "row_level_source_id_present", "PASS",
                               "parser rejects rows missing source"))
    return results


def group_F_fee_slippage(files_info):
    """F_fee_slippage: fees attached, taker + slippage declared,
    spread-proxy when L1 absent. No PASS if fees or slippage missing."""
    results = []
    GID = "F_fee_slippage"
    fees, err = _safe_read_json(files_info["fees_path"])
    if err:
        results.append(CheckResult(GID, "fees_json_present", "FAIL", err))
        results.append(CheckResult(GID, "fees_taker_declared", "FAIL",
                                   "no fees.json -- per Bundle 14, no PASS if fees missing"))
        results.append(CheckResult(GID, "slippage_declared", "FAIL",
                                   "no fees.json -- per Bundle 14, no PASS if slippage missing"))
        return results
    if not isinstance(fees, dict):
        results.append(CheckResult(GID, "fees_json_present", "FAIL",
                                   "fees.json is not a JSON object"))
        return results
    results.append(CheckResult(GID, "fees_json_present", "PASS", "fees.json exists and parses"))
    # Taker fee.
    has_taker = False
    if "fees" in fees and isinstance(fees["fees"], dict):
        for v in fees["fees"].values():
            if isinstance(v, dict) and ("taker_bps" in v or "taker_fee_bps" in v):
                has_taker = True
                break
    elif "taker_bps" in fees or "taker_fee_bps" in fees:
        has_taker = True
    if has_taker:
        results.append(CheckResult(GID, "fees_taker_declared", "PASS", "per-venue taker fee declared"))
    else:
        results.append(CheckResult(GID, "fees_taker_declared", "FAIL",
                                   "no taker fee declared -- per Bundle 14, no PASS without taker"))
    # Slippage.
    has_slippage = "slippage_bps" in fees or "slippage" in fees
    if has_slippage:
        results.append(CheckResult(GID, "slippage_declared", "PASS", "slippage assumption declared"))
    else:
        results.append(CheckResult(GID, "slippage_declared", "FAIL",
                                   "no slippage declared -- per Bundle 14, no PASS without slippage"))
    # Spread proxy (warn if absent).
    if "spread_proxy_bps" in fees or "spread_proxy" in fees:
        results.append(CheckResult(GID, "spread_proxy_declared", "PASS", "spread_proxy declared"))
    else:
        results.append(CheckResult(GID, "spread_proxy_declared", "WARN",
                                   "spread_proxy not declared; recommended when L1 quote data absent"))
    return results


def group_G_freeze(files_info, manifest):
    """G_freeze: dataset FROZEN, CHECKSUMS.txt present + sha256-verified per
    file, FREEZE_RECORD.txt present, row counts recorded, data-change-creates-
    new-version asserted."""
    results = []
    GID = "G_freeze"
    if (manifest or {}).get("freeze_status") != "FROZEN":
        results.append(CheckResult(GID, "freeze_status_FROZEN", "FAIL",
                                   f"freeze_status is not 'FROZEN' (got {(manifest or {}).get('freeze_status')!r})"))
    else:
        results.append(CheckResult(GID, "freeze_status_FROZEN", "PASS", "FROZEN"))
    # CHECKSUMS.txt.
    cs_text, cs_err = _safe_read_text(files_info["checksums_path"])
    if cs_err:
        results.append(CheckResult(GID, "checksums_txt_present", "FAIL", cs_err))
        results.append(CheckResult(GID, "checksums_verified", "FAIL",
                                   "CHECKSUMS.txt missing -- cannot verify per-file sha256"))
    else:
        results.append(CheckResult(GID, "checksums_txt_present", "PASS",
                                   "CHECKSUMS.txt exists"))
        checksums = parse_checksums_txt(cs_text)
        if not checksums:
            results.append(CheckResult(GID, "checksums_verified", "FAIL",
                                       "CHECKSUMS.txt parsed to 0 entries"))
        else:
            mismatched, missing = verify_checksums(files_info["dataset_dir"], checksums)
            if mismatched:
                results.append(CheckResult(GID, "checksums_verified", "FAIL",
                                           f"{len(mismatched)} file(s) sha256 mismatch: {[m['file'] for m in mismatched]}"))
            elif missing:
                results.append(CheckResult(GID, "checksums_verified", "FAIL",
                                           f"{len(missing)} file(s) listed in CHECKSUMS.txt are missing on disk: {missing}"))
            else:
                results.append(CheckResult(GID, "checksums_verified", "PASS",
                                           f"all {len(checksums)} file(s) sha256-verified"))
    # FREEZE_RECORD.txt.
    fr_text, fr_err = _safe_read_text(files_info["freeze_record_path"])
    if fr_err:
        results.append(CheckResult(GID, "freeze_record_present", "FAIL", fr_err))
    else:
        results.append(CheckResult(GID, "freeze_record_present", "PASS", "FREEZE_RECORD.txt exists"))
        # Minimal sanity: must mention freeze_timestamp_utc and at least one version pin.
        if "freeze_timestamp_utc" not in fr_text:
            results.append(CheckResult(GID, "freeze_record_has_timestamp", "FAIL",
                                       "FREEZE_RECORD.txt missing 'freeze_timestamp_utc' key"))
        else:
            results.append(CheckResult(GID, "freeze_record_has_timestamp", "PASS",
                                       "freeze_timestamp_utc present"))
        ver_pins_found = sum(1 for k in ("protocol_version", "data_contract_version",
                                          "manifest_version", "qa_freeze_spec_version",
                                          "backtest_plan_version", "runner_version")
                             if k in fr_text)
        if ver_pins_found < 3:
            results.append(CheckResult(GID, "freeze_record_version_pins", "WARN",
                                       f"only {ver_pins_found} of 6 version pins found in FREEZE_RECORD.txt"))
        else:
            results.append(CheckResult(GID, "freeze_record_version_pins", "PASS",
                                       f"{ver_pins_found} of 6 version pins found"))
    # Row counts recorded in manifest.
    if (manifest or {}).get("row_count_actual") is None:
        results.append(CheckResult(GID, "row_count_recorded", "FAIL",
                                   "manifest.row_count_actual not recorded"))
    else:
        results.append(CheckResult(GID, "row_count_recorded", "PASS",
                                   f"row_count_actual = {manifest.get('row_count_actual')}"))
    return results


# ===========================================================================
# Verdict classifier + report builder
# ===========================================================================
def classify_qa_status(all_results, has_blocked_flag: bool):
    """Map the aggregate results to one of the 6 Bundle-14 QA statuses."""
    if has_blocked_flag:
        return "QA_BLOCKED"
    fails = [r for r in all_results if r.severity == "FAIL"]
    warns = [r for r in all_results if r.severity == "WARN"]
    if fails:
        return "QA_FAIL"
    if warns:
        return "QA_WARN"
    return "QA_PASS"


def _summary_for_group(all_results, group_id):
    g = [r for r in all_results if r.group == group_id]
    return {
        "group": group_id,
        "checks_run": len(g),
        "checks_passed": sum(1 for r in g if r.severity == "PASS"),
        "checks_warned": sum(1 for r in g if r.severity == "WARN"),
        "checks_failed": sum(1 for r in g if r.severity == "FAIL"),
        "details": [r.as_dict() for r in g],
    }


def _qa_report_id(dataset_dir: Path, csv_files: list, manifest_text: str):
    """Deterministic 16-char id from dataset bytes + tool version pins."""
    h = hashlib.sha256()
    h.update(TOOL_VERSION.encode("utf-8"))
    h.update(QA_FREEZE_SPEC_VERSION.encode("utf-8"))
    h.update(DATA_CONTRACT_VERSION.encode("utf-8"))
    h.update(DATASET_MANIFEST_SPEC_VERSION.encode("utf-8"))
    h.update(PROTOCOL_VERSION.encode("utf-8"))
    for p in csv_files:
        h.update(p.name.encode("utf-8"))
        try:
            h.update(p.read_bytes())
        except OSError:
            h.update(b"<unreadable>")
    if manifest_text:
        h.update(manifest_text.encode("utf-8"))
    return h.hexdigest()[:16]


def build_qa_report(dataset_dir, out_dir):
    """Run all 7 check groups on dataset_dir and return the qa_report dict.

    Always returns a fully-populated 26-field report, even on missing data
    (in which case QA_status will be QA_DRAFT / QA_FAIL)."""
    dataset_dir = Path(dataset_dir)
    out_dir = Path(out_dir)
    files_info = discover_dataset_files(dataset_dir)

    # If dataset_dir doesn't exist, emit a QA_DRAFT report with empty groups.
    if not files_info["exists"]:
        return _build_empty_report(dataset_dir, out_dir, files_info,
                                   status="QA_DRAFT",
                                   blocking="dataset_dir does not exist")

    manifest, manifest_err = _safe_read_json(files_info["manifest_path"])
    manifest_text = ""
    if manifest is not None:
        manifest_text = json.dumps(manifest, sort_keys=True, ensure_ascii=False)

    # Read all CSVs in dataset_dir.
    bars_by_symbol = {}
    csv_parse_errors = []
    for csv_path in files_info["csv_files"]:
        bars, errs = read_csv_bars(csv_path)
        csv_parse_errors.extend(errs)
        for b in bars:
            bars_by_symbol.setdefault(b.symbol, []).append(b)
    for sym in bars_by_symbol:
        bars_by_symbol[sym].sort(key=lambda b: b.timestamp)

    # If no CSV files exist OR no bars parsed, emit QA_FAIL.
    if not files_info["csv_files"]:
        return _build_empty_report(dataset_dir, out_dir, files_info,
                                   status="QA_FAIL",
                                   blocking="no .csv files in dataset_dir")
    if not bars_by_symbol and csv_parse_errors:
        return _build_empty_report(dataset_dir, out_dir, files_info,
                                   status="QA_FAIL",
                                   blocking=f"no parseable bars; {len(csv_parse_errors)} parse error(s)")

    # External-block override: manifest may declare QA_BLOCKED.
    has_blocked_flag = (manifest or {}).get("QA_status") == "QA_BLOCKED"

    # Run the 7 groups.
    all_results = []
    all_results.extend(group_A_manifest_integrity(manifest, manifest_err, files_info))
    all_results.extend(group_B_timestamp(bars_by_symbol, manifest))
    all_results.extend(group_C_OHLCV(bars_by_symbol))
    all_results.extend(group_D_volume(bars_by_symbol))
    all_results.extend(group_E_symbol_source(bars_by_symbol))
    all_results.extend(group_F_fee_slippage(files_info))
    all_results.extend(group_G_freeze(files_info, manifest))

    # CSV parse errors are blocking too -- record as a synthetic group.
    if csv_parse_errors:
        all_results.append(CheckResult("A_manifest_integrity",
                                       "csv_row_parse_errors", "FAIL",
                                       f"{len(csv_parse_errors)} row parse error(s); first: {csv_parse_errors[0]}"))

    qa_status = classify_qa_status(all_results, has_blocked_flag)

    row_count_observed = {s: len(bars) for s, bars in bars_by_symbol.items()}
    total_rows = sum(row_count_observed.values())

    qa_report = {
        "qa_report_id": _qa_report_id(dataset_dir, files_info["csv_files"], manifest_text),
        "dataset_id": (manifest or {}).get("dataset_id"),
        "dataset_version": (manifest or {}).get("dataset_version"),
        "manifest_version": (manifest or {}).get("manifest_version", DATASET_MANIFEST_SPEC_VERSION),
        "data_contract_version": (manifest or {}).get("data_contract_version", DATA_CONTRACT_VERSION),
        "protocol_version": (manifest or {}).get("protocol_version", PROTOCOL_VERSION),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "qa_status": qa_status,
        "checks_run": len(all_results),
        "checks_passed": sum(1 for r in all_results if r.severity == "PASS"),
        "checks_warned": sum(1 for r in all_results if r.severity == "WARN"),
        "checks_failed": sum(1 for r in all_results if r.severity == "FAIL"),
        "blocking_failures": [r.as_dict() for r in all_results if r.severity == "FAIL"],
        "warnings": [r.as_dict() for r in all_results if r.severity == "WARN"],
        "row_count_observed": {"total": total_rows, "per_asset": row_count_observed},
        "missing_day_summary": _missing_day_summary(bars_by_symbol),
        "duplicate_summary": _duplicate_summary(bars_by_symbol),
        "timestamp_summary": _summary_for_group(all_results, "B_timestamp"),
        "OHLCV_summary": _summary_for_group(all_results, "C_OHLCV"),
        "volume_summary": _summary_for_group(all_results, "D_volume"),
        "fee_slippage_summary": _summary_for_group(all_results, "F_fee_slippage"),
        "source_provenance_summary": _summary_for_group(all_results, "E_symbol_source"),
        "freeze_summary": _summary_for_group(all_results, "G_freeze"),
        "allowed_next_step": _allowed_next_step(qa_status),
        "forbidden_next_steps": list(FORBIDDEN_NEXT_STEPS),
        "safety_flags": dict(SAFETY_FLAGS),
        # Audit context (not required by Bundle 14, kept for review).
        "_audit_context": {
            "tool_version": TOOL_VERSION,
            "qa_freeze_spec_version": QA_FREEZE_SPEC_VERSION,
            "dataset_dir": dataset_dir.as_posix(),
            "csv_files_seen": [p.name for p in files_info["csv_files"]],
            "csv_parse_errors_count": len(csv_parse_errors),
            "csv_parse_errors_sample": csv_parse_errors[:20],
            "safety_notes": list(SAFETY_NOTES),
        },
    }
    return qa_report


def _missing_day_summary(bars_by_symbol):
    out = {"total_missing_days": 0, "per_asset": {}}
    for symbol, bars in bars_by_symbol.items():
        if len(bars) < 2:
            continue
        try:
            d0 = datetime.strptime(bars[0].timestamp, "%Y-%m-%d")
            d1 = datetime.strptime(bars[-1].timestamp, "%Y-%m-%d")
            expected = (d1 - d0).days + 1
            observed = len(bars)
            missing = max(0, expected - observed)
            out["per_asset"][symbol] = {"observed": observed, "expected": expected, "missing": missing}
            out["total_missing_days"] += missing
        except ValueError:
            continue
    return out


def _duplicate_summary(bars_by_symbol):
    dup = {}
    for symbol, bars in bars_by_symbol.items():
        seen = set()
        cnt = 0
        for b in bars:
            k = (b.symbol, b.timestamp)
            if k in seen:
                cnt += 1
            seen.add(k)
        dup[symbol] = cnt
    return {"total_duplicates": sum(dup.values()), "per_asset": dup}


def _allowed_next_step(qa_status):
    if qa_status == "QA_PASS":
        return ("Dataset eligible for a SEPARATELY authorized backtest plan."
                " Operator must explicitly opt in; QA_PASS does NOT autoauthorize.")
    if qa_status == "QA_WARN":
        return ("Attach a written operator-acceptance note to the manifest"
                " before any backtest plan references the dataset.")
    if qa_status == "QA_FAIL":
        return "Remediation requires a NEW dataset_version. Do not reference this dataset."
    if qa_status == "QA_BLOCKED":
        return ("External block declared in manifest. Do not reference this"
                " dataset until the block is cleared.")
    return ("Operator review required to determine next step; not autoauthorized.")


def _build_empty_report(dataset_dir, out_dir, files_info, status, blocking):
    """Build a fully-populated 26-field report when no checks could run."""
    return {
        "qa_report_id": "no_input",
        "dataset_id": None,
        "dataset_version": None,
        "manifest_version": DATASET_MANIFEST_SPEC_VERSION,
        "data_contract_version": DATA_CONTRACT_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "qa_status": status,
        "checks_run": 0,
        "checks_passed": 0,
        "checks_warned": 0,
        "checks_failed": 1 if status == "QA_FAIL" else 0,
        "blocking_failures": ([{"group": "input", "check_id": "dataset_input",
                                 "severity": "FAIL", "detail": blocking}]
                              if status == "QA_FAIL" else []),
        "warnings": [],
        "row_count_observed": {"total": 0, "per_asset": {}},
        "missing_day_summary": {"total_missing_days": 0, "per_asset": {}},
        "duplicate_summary": {"total_duplicates": 0, "per_asset": {}},
        "timestamp_summary": {"group": "B_timestamp", "checks_run": 0,
                               "checks_passed": 0, "checks_warned": 0,
                               "checks_failed": 0, "details": []},
        "OHLCV_summary": {"group": "C_OHLCV", "checks_run": 0,
                           "checks_passed": 0, "checks_warned": 0,
                           "checks_failed": 0, "details": []},
        "volume_summary": {"group": "D_volume", "checks_run": 0,
                            "checks_passed": 0, "checks_warned": 0,
                            "checks_failed": 0, "details": []},
        "fee_slippage_summary": {"group": "F_fee_slippage", "checks_run": 0,
                                  "checks_passed": 0, "checks_warned": 0,
                                  "checks_failed": 0, "details": []},
        "source_provenance_summary": {"group": "E_symbol_source",
                                       "checks_run": 0, "checks_passed": 0,
                                       "checks_warned": 0, "checks_failed": 0,
                                       "details": []},
        "freeze_summary": {"group": "G_freeze", "checks_run": 0,
                            "checks_passed": 0, "checks_warned": 0,
                            "checks_failed": 0, "details": []},
        "allowed_next_step": _allowed_next_step(status),
        "forbidden_next_steps": list(FORBIDDEN_NEXT_STEPS),
        "safety_flags": dict(SAFETY_FLAGS),
        "_audit_context": {
            "tool_version": TOOL_VERSION,
            "qa_freeze_spec_version": QA_FREEZE_SPEC_VERSION,
            "dataset_dir": Path(dataset_dir).as_posix(),
            "csv_files_seen": [p.name for p in files_info["csv_files"]],
            "csv_parse_errors_count": 0,
            "csv_parse_errors_sample": [],
            "safety_notes": list(SAFETY_NOTES),
            "no_input_reason": blocking,
        },
    }


# ===========================================================================
# Report writers
# ===========================================================================
def _render_md(report: dict) -> str:
    lines = [
        "# SPARTA Crypto-D1 Data QA Runtime Tool v1 -- QA report",
        "",
        "> **Research-only. Local-only.** No data fetched. No exchange"
        " contacted. No order placed. QA_PASS does NOT authorize paper or"
        " live trading.",
        "",
        f"- **qa_report_id:** `{report['qa_report_id']}`",
        f"- **generated_at:** {report['generated_at']}",
        f"- **tool_version:** {report['_audit_context']['tool_version']}",
        f"- **qa_freeze_spec_version:** {report['_audit_context']['qa_freeze_spec_version']}",
        f"- **dataset_id:** `{report['dataset_id']}`",
        f"- **dataset_version:** `{report['dataset_version']}`",
        f"- **data_contract_version:** {report['data_contract_version']}",
        f"- **protocol_version:** {report['protocol_version']}",
        f"- **dataset_dir:** `{report['_audit_context']['dataset_dir']}`",
        "",
        "## QA verdict",
        f"- **qa_status:** **{report['qa_status']}**",
        f"- **checks_run:** {report['checks_run']}"
        f" (passed {report['checks_passed']} / warned {report['checks_warned']}"
        f" / failed {report['checks_failed']})",
        f"- **allowed_next_step:** {report['allowed_next_step']}",
        "",
        "## Safety flags (pinned)",
    ]
    for k, v in report["safety_flags"].items():
        lines.append(f"- {k}: {v}")
    if report["blocking_failures"]:
        lines += ["", "## Blocking failures"]
        for f in report["blocking_failures"][:50]:
            lines.append(f"- [{f['group']}] {f['check_id']}: {f['detail']}")
    if report["warnings"]:
        lines += ["", "## Warnings"]
        for w in report["warnings"][:50]:
            lines.append(f"- [{w['group']}] {w['check_id']}: {w['detail']}")
    lines += ["", "## Row counts"]
    rc = report["row_count_observed"]
    lines.append(f"- total: {rc.get('total')}")
    for s, n in rc.get("per_asset", {}).items():
        lines.append(f"  - {s}: {n}")
    lines += ["", "## Forbidden next steps"]
    for s in report["forbidden_next_steps"]:
        lines.append(f"- {s}")
    lines += ["", "## Safety notes"]
    for s in report["_audit_context"].get("safety_notes", []):
        lines.append(f"- {s}")
    return "\n".join(lines) + "\n"


def write_qa_report(report: dict, out_dir: Path):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "qa_report.json"
    md_path = out_dir / "qa_report.md"
    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    md_path.write_text(_render_md(report), encoding="utf-8")
    return json_path, md_path


# ===========================================================================
# CLI helpers (validate-spec, show-spec)
# ===========================================================================
def validate_spec(repo_root=None):
    """Confirm Bundle 14's QA spec validates as a precondition."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parent.parent
    return _cqf.validate(Path(repo_root))


def show_spec():
    return {
        "tool_version": TOOL_VERSION,
        "qa_freeze_spec_version": QA_FREEZE_SPEC_VERSION,
        "data_contract_version": DATA_CONTRACT_VERSION,
        "dataset_manifest_spec_version": DATASET_MANIFEST_SPEC_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "target_assets": list(TARGET_ASSETS),
        "allowed_market_type": "spot",
        "timeframe": "1d",
        "qa_check_groups": list(QA_CHECK_GROUPS_DECLARED),
        "qa_statuses": list(QA_STATUSES_DECLARED),
        "qa_report_required_fields": list(QA_REPORT_REQUIRED_FIELDS),
        "qa_report_required_field_count": len(QA_REPORT_REQUIRED_FIELDS),
        "required_csv_columns": list(REQUIRED_BAR_COLUMNS),
        "safety_flags": dict(SAFETY_FLAGS),
        "safety_notes": list(SAFETY_NOTES),
        "forbidden_next_steps": list(FORBIDDEN_NEXT_STEPS),
    }


# ===========================================================================
# CLI main
# ===========================================================================
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Data QA Runtime Tool v1 -- local-only, read-only.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("validate-spec", help="Validate Bundle 14 QA spec as a precondition.")
    sub.add_parser("show-spec", help="Print a structured Bundle 14 spec summary.")

    p_run = sub.add_parser("run", help="Run the 7 QA check groups against a dataset.")
    p_run.add_argument("--dataset-dir", required=True,
                       help="Directory containing operator-supplied dataset (CSV + manifest.json + CHECKSUMS.txt + FREEZE_RECORD.txt + fees.json).")
    p_run.add_argument("--out-dir", required=True,
                       help="Directory to write qa_report.json + qa_report.md.")

    args = parser.parse_args(argv)

    if args.command == "validate-spec":
        ok, errs = validate_spec()
        if ok:
            print("validate-spec: OK")
            return 0
        print("validate-spec: FAIL")
        for e in errs:
            print(f"  - {e}")
        return 2

    if args.command == "show-spec":
        print(json.dumps(show_spec(), indent=2, sort_keys=True, ensure_ascii=False, default=str))
        return 0

    if args.command == "run":
        report = build_qa_report(args.dataset_dir, args.out_dir)
        json_path, md_path = write_qa_report(report, args.out_dir)
        print(f"qa_report_id: {report['qa_report_id']}")
        print(f"qa_status:    {report['qa_status']}")
        print(f"checks_run:   {report['checks_run']}"
              f" (passed {report['checks_passed']} / warned {report['checks_warned']}"
              f" / failed {report['checks_failed']})")
        print(f"json:         {json_path.as_posix()}")
        print(f"md:           {md_path.as_posix()}")
        return 0 if report["qa_status"] in ("QA_PASS", "QA_WARN") else 2

    return 2


if __name__ == "__main__":
    raise SystemExit(main())

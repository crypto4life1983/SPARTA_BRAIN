"""Crypto-D1 Manual CSV Staging Helper (MANUAL CSV ONLY).

A PURE, stdlib-only, LOCAL-ONLY helper that stages *already-downloaded* BTC / ETH /
SOL daily spot OHLCV CSV files into the canonical layout the Real Data QA runner
reads. It:
  - reads source CSV files ONLY from a caller-provided local source folder;
  - normalizes the header into the exact canonical schema
    date,open,high,low,close,volume,source,instrument_type;
  - writes staged files ONLY to data/crypto_d1_spot/raw/{BTC,ETH,SOL}_1d.csv;
  - rejects any file whose header carries a forbidden account/order/trade field;
  - rejects any non-spot / futures / perp / leverage row.

It imports NOTHING that can reach a network, an exchange/broker, a credential, or a
.env (no urllib / requests / socket / http / ccxt / databento / dotenv). It fetches
nothing, downloads nothing, and changes NO gate: real_data_qa stays BLOCKED,
baseline stays BLOCKED, and paper / micro-live stay LOCKED. Staging a file makes it
available for a SEPARATE read-only QA pass; it never approves or runs anything.

Public API:
  - STAGER_SCHEMA_VERSION / STAGER_LABEL / STAGER_MODE
  - STAGER_HEADER_ALIASES / STAGER_NON_SPOT_TERMS
  - STAGE_STAGED / STAGE_REJECTED
  - normalize_header(source_header)
  - stage_one_symbol(source_path, symbol, dest_path, *, source_tag, write)
  - stage_manual_csv(source_dir, *, repo_root, symbol_files, source_tag, write)
  - render_staging_report_markdown(report)
"""

from __future__ import annotations

import csv
import os
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner import (
    QA_APPROVED_INPUT_DIR,
    QA_FORBIDDEN_FIELDS,
    QA_REQUIRED_FIELDS,
    QA_REQUIRED_INSTRUMENT_TYPE,
    QA_REQUIRED_SYMBOLS,
)

STAGER_SCHEMA_VERSION = "strategy_factory_crypto_d1_manual_csv_staging_helper.v1"
STAGER_LABEL = "Crypto-D1 Manual CSV Staging Helper (MANUAL CSV ONLY)"
STAGER_MODE = "RESEARCH_ONLY"

# Accepted source column names (lowercased) that map onto each canonical field. The
# canonical "source" and "instrument_type" are optional in the input -- if absent,
# they are filled with the source_tag and "spot" respectively.
STAGER_HEADER_ALIASES: dict[str, tuple[str, ...]] = {
    "date": ("date", "time", "timestamp", "datetime", "day"),
    "open": ("open", "o", "open_price", "openprice"),
    "high": ("high", "h", "high_price", "highprice"),
    "low": ("low", "l", "low_price", "lowprice"),
    "close": ("close", "c", "close_price", "closeprice"),
    "volume": ("volume", "vol", "v"),
    "source": ("source", "provider"),
    "instrument_type": ("instrument_type", "instrument", "asset_type", "type"),
}

# Any of these appearing in an instrument_type value forces rejection: this helper
# stages SPOT only.
STAGER_NON_SPOT_TERMS: tuple[str, ...] = (
    "future",
    "futures",
    "perp",
    "perpetual",
    "swap",
    "leverage",
    "margin",
    "option",
    "contract",
)

STAGE_STAGED = "STAGED"
STAGE_REJECTED = "REJECTED"

# Default candidate source filenames searched per symbol, in priority order.
_CANDIDATE_PATTERNS: tuple[str, ...] = (
    "{sym}_1d.csv",
    "{sym}.csv",
    "{low}_1d.csv",
    "{low}.csv",
    "{sym}USD_1d.csv",
    "{sym}USD.csv",
    "{sym}USDT.csv",
)


def _required_canonical() -> tuple[str, ...]:
    return tuple(f for f in QA_REQUIRED_FIELDS if f not in ("source", "instrument_type"))


def normalize_header(source_header: list[str]) -> dict[str, Any]:
    """Map a source CSV header onto canonical field indices. Returns a dict with
    `mapping` (canonical field -> source index), `forbidden` (forbidden source
    columns found), and `missing` (required canonical fields that could not be
    mapped). Pure; reads nothing."""
    lower = [c.strip().lower() for c in source_header]
    forbidden = [c for c in lower if c in QA_FORBIDDEN_FIELDS]

    mapping: dict[str, int] = {}
    for canonical, aliases in STAGER_HEADER_ALIASES.items():
        for i, col in enumerate(lower):
            if col in aliases:
                mapping[canonical] = i
                break

    missing = [f for f in _required_canonical() if f not in mapping]
    return {"mapping": mapping, "forbidden": forbidden, "missing": missing}


def stage_one_symbol(
    source_path: str,
    symbol: str,
    dest_path: str,
    *,
    source_tag: str = "manual_csv",
    write: bool = True,
) -> dict[str, Any]:
    """Validate and (optionally) stage one symbol's source CSV into the canonical
    schema at dest_path. Reads source_path read-only; writes ONLY dest_path. Returns
    a fresh result dict; never raises on bad data -- it returns a REJECTED status."""
    if not os.path.isfile(source_path):
        return _reject(symbol, source_path, dest_path, "source_file_missing")

    with open(source_path, "r", encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.reader(fh) if r and any(c.strip() for c in r)]

    if not rows:
        return _reject(symbol, source_path, dest_path, "empty_source_file")

    header = [c.strip() for c in rows[0]]
    data_rows = rows[1:]
    norm = normalize_header(header)

    if norm["forbidden"]:
        return _reject(
            symbol,
            source_path,
            dest_path,
            "forbidden_fields:" + ",".join(sorted(set(norm["forbidden"]))),
        )
    if norm["missing"]:
        return _reject(
            symbol,
            source_path,
            dest_path,
            "cannot_map_required_field:" + ",".join(norm["missing"]),
        )

    mapping = norm["mapping"]
    out_rows: list[list[str]] = []
    for row in data_rows:
        if len(row) < len(header):
            return _reject(symbol, source_path, dest_path, "ragged_source_row")
        itype = (
            row[mapping["instrument_type"]].strip().lower()
            if "instrument_type" in mapping
            else QA_REQUIRED_INSTRUMENT_TYPE
        )
        if itype != QA_REQUIRED_INSTRUMENT_TYPE or any(
            term in itype for term in STAGER_NON_SPOT_TERMS
        ):
            return _reject(symbol, source_path, dest_path, "non_spot_instrument_type")
        src_val = (
            row[mapping["source"]].strip() if "source" in mapping else source_tag
        ) or source_tag
        out_rows.append(
            [
                row[mapping["date"]].strip(),
                row[mapping["open"]].strip(),
                row[mapping["high"]].strip(),
                row[mapping["low"]].strip(),
                row[mapping["close"]].strip(),
                row[mapping["volume"]].strip(),
                src_val,
                QA_REQUIRED_INSTRUMENT_TYPE,
            ]
        )

    if write:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(list(QA_REQUIRED_FIELDS))
            writer.writerows(out_rows)

    return {
        "symbol": symbol,
        "status": STAGE_STAGED,
        "source_path": source_path,
        "dest_path": dest_path,
        "row_count": len(out_rows),
        "reason": "",
        "written": bool(write),
    }


def _reject(symbol: str, source_path: str, dest_path: str, reason: str) -> dict[str, Any]:
    return {
        "symbol": symbol,
        "status": STAGE_REJECTED,
        "source_path": source_path,
        "dest_path": dest_path,
        "row_count": 0,
        "reason": reason,
        "written": False,
    }


def _find_source(source_dir: str, symbol: str) -> str | None:
    for pat in _CANDIDATE_PATTERNS:
        cand = os.path.join(source_dir, pat.format(sym=symbol, low=symbol.lower()))
        if os.path.isfile(cand):
            return cand
    return None


def stage_manual_csv(
    source_dir: str,
    *,
    repo_root: str = ".",
    symbol_files: dict[str, str] | None = None,
    source_tag: str = "manual_csv",
    write: bool = True,
) -> dict[str, Any]:
    """Stage BTC / ETH / SOL source CSVs from source_dir into the canonical raw dir.
    symbol_files optionally maps a symbol to an explicit source filename (relative to
    source_dir). Returns a report dict. Reads only from source_dir; writes only under
    data/crypto_d1_spot/raw/. Touches no gate, fetches nothing."""
    dest_dir = os.path.join(repo_root, QA_APPROVED_INPUT_DIR)
    files_read: list[str] = []
    files_written: list[str] = []
    per_symbol: list[dict[str, Any]] = []

    for sym in QA_REQUIRED_SYMBOLS:
        if symbol_files and sym in symbol_files:
            src = os.path.join(source_dir, symbol_files[sym])
        else:
            src = _find_source(source_dir, sym)
        dest = os.path.join(dest_dir, sym + "_1d.csv")
        if src is None:
            per_symbol.append(_reject(sym, "", dest, "no_source_file_found"))
            continue
        result = stage_one_symbol(
            src, sym, dest, source_tag=source_tag, write=write
        )
        if result["status"] == STAGE_STAGED:
            files_read.append(src)
            if result["written"]:
                files_written.append(dest)
        per_symbol.append(result)

    staged = sum(1 for r in per_symbol if r["status"] == STAGE_STAGED)
    if staged == len(QA_REQUIRED_SYMBOLS):
        overall = "ALL_STAGED"
    elif staged == 0:
        overall = "NONE_STAGED"
    else:
        overall = "PARTIAL"

    return {
        "schema_version": STAGER_SCHEMA_VERSION,
        "label": STAGER_LABEL,
        "mode": STAGER_MODE,
        "source_dir": source_dir,
        "dest_dir": QA_APPROVED_INPUT_DIR,
        "canonical_schema": list(QA_REQUIRED_FIELDS),
        "overall_status": overall,
        "staged_count": staged,
        "required_count": len(QA_REQUIRED_SYMBOLS),
        "per_symbol": per_symbol,
        "files_read": files_read,
        "files_written": files_written,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "executes": False,
        "no_network_used": True,
        "no_credentials_used": True,
        "manual_csv_only": True,
    }


def render_staging_report_markdown(report: Any) -> str:
    """Render a staging report as deterministic markdown. Pure string work."""
    r = report if isinstance(report, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Manual CSV Staging Report")
    lines.append("")
    lines.append("- Overall: " + str(r.get("overall_status", "")))
    lines.append(
        "- Staged: "
        + str(r.get("staged_count", 0))
        + " / "
        + str(r.get("required_count", 0))
    )
    lines.append("- Source dir: " + str(r.get("source_dir", "")))
    lines.append("- Dest dir: " + str(r.get("dest_dir", "")))
    lines.append("")
    lines.append("## Per-symbol")
    for s in r.get("per_symbol", []):
        line = (
            "- "
            + str(s.get("symbol"))
            + ": "
            + str(s.get("status"))
            + " (rows="
            + str(s.get("row_count"))
            + ")"
        )
        if s.get("reason"):
            line += " - " + str(s.get("reason"))
        lines.append(line)
    lines.append("")
    lines.append("## Gates (read-only metadata, unchanged)")
    lines.append("- real_data_qa: BLOCKED")
    lines.append("- baseline_backtest: BLOCKED")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    return "\n".join(lines)

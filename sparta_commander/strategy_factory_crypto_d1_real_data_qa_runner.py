"""Crypto-D1 Real Data QA Runner (MANUAL CSV ONLY).

The authorized boundary-crossing artifact for Real Data QA. Unlike the pre-boundary
fetch runner (Block 150), this module is explicitly permitted local file I/O -- but
ONLY:
  - reads the three manual CSV files BTC_1d.csv / ETH_1d.csv / SOL_1d.csv under the
    approved input dir (default data/crypto_d1_spot/raw/);
  - writes provenance JSON under the approved provenance dir
    (default data/crypto_d1_spot/provenance/);
  - writes a QA report (json + md) under the approved report dir
    (default reports/crypto_d1_real_data_qa/).

It imports NOTHING that can reach a network, an exchange/broker, a credential, or a
.env (no urllib / requests / socket / http / ccxt / databento / dotenv). It performs
NO baseline / backtest / paper / live / micro-live action and changes NO gate: the
gate states it records are read-only metadata only. real_data_qa stays BLOCKED,
baseline stays BLOCKED, and paper / micro-live stay LOCKED regardless of input.

Verdict (precedence INVALID > NEEDS_DATA_FIX > PASS):
  - INVALID        : a forbidden account/order/trade field appears, a row is not
                     instrument_type "spot", or a boundary invariant is breached.
                     A safety / scope violation -- never PASS.
  - NEEDS_DATA_FIX : an input file is missing, the schema header is wrong, dates are
                     malformed / non-ascending / duplicated, a price is <= 0, volume
                     is null / negative, coverage is short, or recomputed provenance
                     does not match an existing provenance file. Fixable data issues.
  - PASS           : every check passes for all required symbols.

Public API:
  - QA_SCHEMA_VERSION / QA_LABEL / QA_MODE
  - QA_REQUIRED_FIELDS / QA_FORBIDDEN_FIELDS / QA_REQUIRED_INSTRUMENT_TYPE
  - QA_REQUIRED_SYMBOLS / QA_MIN_ROWS_PER_SYMBOL
  - QA_APPROVED_INPUT_DIR / QA_APPROVED_PROVENANCE_DIR / QA_APPROVED_REPORT_DIR
  - QA_GATE_METADATA
  - VERDICT_PASS / VERDICT_NEEDS_DATA_FIX / VERDICT_INVALID / QA_VERDICTS
  - file_provenance(path)
  - qa_check_symbol_file(path, symbol, existing_provenance=None)
  - run_real_data_qa(repo_root=".", *, input_dir=..., provenance_dir=...,
                     report_dir=..., symbols=..., write=True)
  - validate_qa_report(report)
  - render_qa_report_markdown(report)
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
from typing import Any

QA_SCHEMA_VERSION = "strategy_factory_crypto_d1_real_data_qa_runner.v1"
QA_LABEL = "Crypto-D1 Real Data QA Runner (MANUAL CSV ONLY)"
QA_MODE = "RESEARCH_ONLY"

# Exact required schema, in order.
QA_REQUIRED_FIELDS: tuple[str, ...] = (
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "source",
    "instrument_type",
)

# Any of these appearing as a column header is a hard INVALID: this is spot OHLCV
# history, never an account / order / trade surface.
QA_FORBIDDEN_FIELDS: tuple[str, ...] = (
    "order",
    "signal",
    "trade",
    "trade_instruction",
    "execution",
    "position",
    "balance",
    "account",
    "leverage",
    "perp",
    "perpetual",
    "future",
    "futures",
    "side",
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
    "margin",
    "pnl",
    "api_key",
    "secret",
)

QA_REQUIRED_INSTRUMENT_TYPE = "spot"
QA_REQUIRED_SYMBOLS: tuple[str, ...] = ("BTC", "ETH", "SOL")
QA_MIN_ROWS_PER_SYMBOL = 1

QA_APPROVED_INPUT_DIR = "data/crypto_d1_spot/raw"
QA_APPROVED_PROVENANCE_DIR = "data/crypto_d1_spot/provenance"
QA_APPROVED_REPORT_DIR = "reports/crypto_d1_real_data_qa"

# Read-only metadata recorded into the report. This runner NEVER changes a gate.
QA_GATE_METADATA: dict[str, bool] = {
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
    "executes": False,
    "authorizes_baseline": False,
    "authorizes_backtest": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_automation": False,
    "unlocks_downstream_gate": False,
}

VERDICT_PASS = "PASS"
VERDICT_NEEDS_DATA_FIX = "NEEDS_DATA_FIX"
VERDICT_INVALID = "INVALID"
QA_VERDICTS: tuple[str, ...] = (VERDICT_PASS, VERDICT_NEEDS_DATA_FIX, VERDICT_INVALID)


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _is_iso_date(value: str) -> bool:
    parts = value.split("-")
    if len(parts) != 3:
        return False
    y, m, d = parts
    if not (len(y) == 4 and y.isdigit() and m.isdigit() and d.isdigit()):
        return False
    mi, di = int(m), int(d)
    return 1 <= mi <= 12 and 1 <= di <= 31


def _as_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def file_provenance(path: str) -> dict[str, Any]:
    """Compute read-only provenance (sha256 + size). Reads the file in binary,
    never parses it as data. Returns exists=False if the path is absent."""
    if not os.path.isfile(path):
        return {"path": path, "exists": False, "sha256": None, "size_bytes": None}
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
            size += len(chunk)
    return {
        "path": path,
        "exists": True,
        "sha256": h.hexdigest(),
        "size_bytes": size,
    }


# --------------------------------------------------------------------------- #
# per-symbol QA
# --------------------------------------------------------------------------- #
def qa_check_symbol_file(
    path: str,
    symbol: str,
    existing_provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run every read-only QA check on one symbol CSV. Returns a fresh result dict
    carrying per-check booleans, a list of failures, and a per-file verdict. Reads
    the file read-only; writes nothing."""
    failures: list[str] = []
    invalid_reasons: list[str] = []
    prov = file_provenance(path)

    if not prov["exists"]:
        return {
            "symbol": symbol,
            "path": path,
            "exists": False,
            "provenance": prov,
            "row_count": 0,
            "header": [],
            "checks": {"file_present": False},
            "failures": ["file_missing"],
            "invalid_reasons": [],
            "verdict": VERDICT_NEEDS_DATA_FIX,
        }

    with open(path, "r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        rows = [r for r in reader if r and any(c.strip() for c in r)]

    header = [c.strip() for c in rows[0]] if rows else []
    data_rows = rows[1:] if rows else []
    lower_header = [c.lower() for c in header]

    # forbidden-field scan (hard INVALID)
    forbidden_hits = [c for c in lower_header if c in QA_FORBIDDEN_FIELDS]
    forbidden_clean = not forbidden_hits
    if forbidden_hits:
        invalid_reasons.append("forbidden_fields:" + ",".join(sorted(set(forbidden_hits))))

    # schema header must match exactly, in order
    schema_ok = tuple(c.lower() for c in header) == QA_REQUIRED_FIELDS
    if not schema_ok:
        failures.append("schema_header_mismatch")

    idx = {name: i for i, name in enumerate(lower_header)}

    dates_ascending = True
    dates_unique = True
    dates_well_formed = True
    prices_positive = True
    volume_valid = True
    high_low_ok = True
    instrument_spot_only = True
    gap_count = 0

    if schema_ok and forbidden_clean:
        prev_date: str | None = None
        seen: set[str] = set()
        prev_ord: int | None = None
        for row in data_rows:
            if len(row) != len(QA_REQUIRED_FIELDS):
                failures.append("ragged_row")
                continue
            cell = {name: row[idx[name]].strip() for name in QA_REQUIRED_FIELDS}

            if cell["instrument_type"].lower() != QA_REQUIRED_INSTRUMENT_TYPE:
                instrument_spot_only = False

            d = cell["date"]
            if not _is_iso_date(d):
                dates_well_formed = False
            else:
                if d in seen:
                    dates_unique = False
                seen.add(d)
                cur_ord = int(d.replace("-", ""))
                if prev_ord is not None and cur_ord <= prev_ord:
                    dates_ascending = False
                if prev_date is not None:
                    gap_count += _calendar_gap(prev_date, d)
                prev_ord = cur_ord
                prev_date = d

            o, hi, lo, cl = (
                _as_float(cell["open"]),
                _as_float(cell["high"]),
                _as_float(cell["low"]),
                _as_float(cell["close"]),
            )
            vol = _as_float(cell["volume"])
            if None in (o, hi, lo, cl) or min(
                v for v in (o, hi, lo, cl) if v is not None
            ) <= 0:
                prices_positive = False
            if vol is None or vol < 0:
                volume_valid = False
            if None not in (o, hi, lo, cl):
                if not (hi >= max(o, cl) and lo <= min(o, cl) and hi >= lo):
                    high_low_ok = False

        if not instrument_spot_only:
            invalid_reasons.append("non_spot_instrument_type")
        if not dates_well_formed:
            failures.append("date_malformed")
        if not dates_ascending:
            failures.append("dates_not_strictly_ascending")
        if not dates_unique:
            failures.append("duplicate_dates")
        if not prices_positive:
            failures.append("non_positive_price")
        if not volume_valid:
            failures.append("invalid_volume")
        if not high_low_ok:
            failures.append("ohlc_impossible")

    coverage_ok = len(data_rows) >= QA_MIN_ROWS_PER_SYMBOL
    if not coverage_ok:
        failures.append("coverage_below_minimum")

    provenance_match = True
    if existing_provenance and existing_provenance.get("sha256"):
        provenance_match = existing_provenance.get("sha256") == prov["sha256"]
        if not provenance_match:
            failures.append("provenance_sha256_mismatch")

    checks = {
        "file_present": True,
        "forbidden_fields_clean": forbidden_clean,
        "schema_ok": schema_ok,
        "instrument_spot_only": instrument_spot_only,
        "dates_well_formed": dates_well_formed,
        "dates_strictly_ascending": dates_ascending,
        "dates_unique": dates_unique,
        "prices_positive": prices_positive,
        "volume_valid": volume_valid,
        "ohlc_consistent": high_low_ok,
        "coverage_ok": coverage_ok,
        "provenance_match": provenance_match,
    }

    if invalid_reasons:
        verdict = VERDICT_INVALID
    elif failures:
        verdict = VERDICT_NEEDS_DATA_FIX
    else:
        verdict = VERDICT_PASS

    return {
        "symbol": symbol,
        "path": path,
        "exists": True,
        "provenance": prov,
        "row_count": len(data_rows),
        "header": header,
        "gap_count": gap_count,
        "checks": checks,
        "failures": failures,
        "invalid_reasons": invalid_reasons,
        "verdict": verdict,
    }


def _calendar_gap(prev_iso: str, cur_iso: str) -> int:
    """Number of missing calendar days strictly between two ISO dates (crypto spot
    trades every day, so any positive gap is reported -- never auto-softened). Pure
    arithmetic; assumes both inputs are well-formed and cur > prev."""
    import datetime

    a = datetime.date(int(prev_iso[0:4]), int(prev_iso[5:7]), int(prev_iso[8:10]))
    b = datetime.date(int(cur_iso[0:4]), int(cur_iso[5:7]), int(cur_iso[8:10]))
    return max(0, (b - a).days - 1)


# --------------------------------------------------------------------------- #
# runner
# --------------------------------------------------------------------------- #
def run_real_data_qa(
    repo_root: str = ".",
    *,
    input_dir: str = QA_APPROVED_INPUT_DIR,
    provenance_dir: str = QA_APPROVED_PROVENANCE_DIR,
    report_dir: str = QA_APPROVED_REPORT_DIR,
    symbols: tuple[str, ...] = QA_REQUIRED_SYMBOLS,
    write: bool = True,
) -> dict[str, Any]:
    """Run read-only Real Data QA over the manual CSV files for every symbol and
    return a report dict. When write=True, writes provenance JSON (for files that
    exist) under provenance_dir and the QA report (json + md) under report_dir --
    and writes NOWHERE else. Never fetches, never touches a gate."""
    in_dir = os.path.join(repo_root, input_dir)
    prov_dir = os.path.join(repo_root, provenance_dir)
    rep_dir = os.path.join(repo_root, report_dir)

    files_read: list[str] = []
    files_written: list[str] = []
    per_symbol: list[dict[str, Any]] = []

    for sym in symbols:
        path = os.path.join(in_dir, sym + "_1d.csv")
        existing_prov = None
        existing_prov_path = os.path.join(prov_dir, sym + "_1d.provenance.json")
        if os.path.isfile(existing_prov_path):
            try:
                with open(existing_prov_path, "r", encoding="utf-8") as fh:
                    existing_prov = json.load(fh)
            except (OSError, ValueError):
                existing_prov = None
        result = qa_check_symbol_file(path, sym, existing_provenance=existing_prov)
        if result["exists"]:
            files_read.append(path)
        per_symbol.append(result)

    verdicts = [r["verdict"] for r in per_symbol]
    if VERDICT_INVALID in verdicts:
        overall = VERDICT_INVALID
    elif VERDICT_NEEDS_DATA_FIX in verdicts:
        overall = VERDICT_NEEDS_DATA_FIX
    else:
        overall = VERDICT_PASS

    all_failures = {
        r["symbol"]: (r["invalid_reasons"] + r["failures"])
        for r in per_symbol
        if r["invalid_reasons"] or r["failures"]
    }

    report: dict[str, Any] = {
        "schema_version": QA_SCHEMA_VERSION,
        "label": QA_LABEL,
        "mode": QA_MODE,
        "authorization": "APPROVE_REAL_DATA_QA_BOUNDARY_CROSSING_MANUAL_CSV_ONLY",
        "input_dir": input_dir,
        "required_symbols": list(symbols),
        "required_schema": list(QA_REQUIRED_FIELDS),
        "forbidden_fields": list(QA_FORBIDDEN_FIELDS),
        "required_instrument_type": QA_REQUIRED_INSTRUMENT_TYPE,
        "verdict": overall,
        "verdicts": list(QA_VERDICTS),
        "per_symbol": per_symbol,
        "failures_by_symbol": all_failures,
        "files_read": files_read,
        "gate_metadata": dict(QA_GATE_METADATA),
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "executes": False,
        "authorizes_baseline_backtest": False,
        "no_network_used": True,
        "no_credentials_used": True,
        "manual_csv_only": True,
    }

    if write:
        os.makedirs(prov_dir, exist_ok=True)
        os.makedirs(rep_dir, exist_ok=True)
        for r in per_symbol:
            if not r["exists"]:
                continue
            p = os.path.join(prov_dir, r["symbol"] + "_1d.provenance.json")
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(
                    {
                        "symbol": r["symbol"],
                        "path": r["path"],
                        "sha256": r["provenance"]["sha256"],
                        "size_bytes": r["provenance"]["size_bytes"],
                        "row_count": r["row_count"],
                        "source": "manual_csv",
                    },
                    fh,
                    indent=2,
                )
            files_written.append(p)
        rep_json = os.path.join(rep_dir, "qa_report.json")
        with open(rep_json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        files_written.append(rep_json)
        rep_md = os.path.join(rep_dir, "qa_report.md")
        with open(rep_md, "w", encoding="utf-8") as fh:
            fh.write(render_qa_report_markdown(report))
        files_written.append(rep_md)

    report["files_written"] = files_written
    return report


# --------------------------------------------------------------------------- #
# validation + render
# --------------------------------------------------------------------------- #
def validate_qa_report(report: Any) -> dict[str, Any]:
    """Validate (read-only) a QA report. Confirms the report shape and -- critically
    -- that it records every gate as still blocked/locked and authorizes nothing."""
    r = report if isinstance(report, dict) else {}
    checks = {
        "schema_ok": r.get("schema_version") == QA_SCHEMA_VERSION,
        "mode_ok": r.get("mode") == QA_MODE,
        "verdict_ok": r.get("verdict") in QA_VERDICTS,
        "has_per_symbol": isinstance(r.get("per_symbol"), list)
        and len(r.get("per_symbol") or []) > 0,
        "real_data_qa_blocked": r.get("real_data_qa_blocked") is True,
        "baseline_backtest_blocked": r.get("baseline_backtest_blocked") is True,
        "paper_trading_gate_locked": r.get("paper_trading_gate_locked") is True,
        "micro_live_gate_locked": r.get("micro_live_gate_locked") is True,
        "executes_false": r.get("executes") is False,
        "no_network_used": r.get("no_network_used") is True,
        "no_credentials_used": r.get("no_credentials_used") is True,
        "manual_csv_only": r.get("manual_csv_only") is True,
    }
    verdict = dict(checks)
    verdict["valid"] = all(checks.values())
    return verdict


def render_qa_report_markdown(report: Any) -> str:
    """Render a QA report as a deterministic markdown brief. Pure string work."""
    r = report if isinstance(report, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Real Data QA Report (MANUAL CSV ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Mode: " + str(r.get("mode", "")))
    lines.append("- Authorization: " + str(r.get("authorization", "")))
    lines.append("- Required schema: " + ", ".join(r.get("required_schema", [])))
    lines.append("")
    lines.append("## Per-symbol")
    for s in r.get("per_symbol", []):
        lines.append(
            "- "
            + str(s.get("symbol"))
            + ": "
            + str(s.get("verdict"))
            + " (exists="
            + str(s.get("exists"))
            + ", rows="
            + str(s.get("row_count"))
            + ")"
        )
        fails = (s.get("invalid_reasons") or []) + (s.get("failures") or [])
        if fails:
            lines.append("  - failures: " + ", ".join(str(f) for f in fails))
    lines.append("")
    lines.append("## Gates (read-only metadata, unchanged)")
    lines.append("- real_data_qa: BLOCKED")
    lines.append("- baseline_backtest: BLOCKED")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- executes: False")
    lines.append("")
    lines.append("## Files read")
    for f in r.get("files_read", []) or ["(none)"]:
        lines.append("- " + str(f))
    lines.append("")
    lines.append("## Files written")
    for f in r.get("files_written", []) or ["(none)"]:
        lines.append("- " + str(f))
    return "\n".join(lines)


if __name__ == "__main__":  # pragma: no cover
    out = run_real_data_qa(repo_root=".")
    print(render_qa_report_markdown(out))

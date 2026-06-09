"""Crypto-D1 Baseline Backtest Prep Contract (PREP ONLY).

A PURE, stdlib-only, read-only module that PREPARES (but never runs) a baseline
backtest over the already QA-passed local staged spot CSVs. It:
  - reads ONLY the three QA-passed staged files
    data/crypto_d1_spot/raw/{BTC,ETH,SOL}_1d.csv (read-only);
  - validates the QA PASS receipt and confirms each staged file is byte-identical
    to what the Real Data QA run recorded (sha256 vs qa_report provenance);
  - defines the baseline input manifest and the baseline run constraints;
  - emits a READY / NOT_READY prep verdict.

It RUNS NOTHING: no backtest, no optimization, no parameter search, no strategy
execution, no simulation, no paper/live/micro-live, no broker/exchange. It
fetches no data, accesses no credentials, touches no network, and UNLOCKS no
gate. baseline_backtest stays BLOCKED and paper / micro-live stay LOCKED until a
SEPARATE explicit human command authorizes an actual baseline run.

Public API:
  - PREP_SCHEMA_VERSION / PREP_LABEL / PREP_MODE
  - VERDICT_READY / VERDICT_NOT_READY
  - BASELINE_STRATEGY_ID / BASELINE_RUN_CONSTRAINTS
  - get_baseline_backtest_prep_label()
  - build_baseline_input_manifest(repo_root)
  - baseline_run_constraints()
  - check_baseline_prep_readiness(repo_root)
  - validate_baseline_prep_report(report)
  - render_baseline_prep_markdown(report)
"""

from __future__ import annotations

import csv
import json
import os
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner import (
    QA_APPROVED_INPUT_DIR,
    QA_APPROVED_REPORT_DIR,
    QA_REQUIRED_FIELDS,
    QA_REQUIRED_SYMBOLS,
    file_provenance,
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_pass_receipt import (
    VERDICT_PASS,
    build_qa_pass_receipt,
    validate_qa_pass_receipt,
)

PREP_SCHEMA_VERSION = "strategy_factory_crypto_d1_baseline_backtest_prep_contract.v1"
PREP_LABEL = "Crypto-D1 Baseline Backtest Prep Contract (PREP ONLY)"
PREP_MODE = "RESEARCH_ONLY"

VERDICT_READY = "READY"
VERDICT_NOT_READY = "NOT_READY"

QA_REPORT_RELPATH = os.path.join(QA_APPROVED_REPORT_DIR, "qa_report.json")

# The reference baseline: the simplest possible long-only spot benchmark. It has
# NO tunable parameters -- this contract only DEFINES it; it never runs it.
BASELINE_STRATEGY_ID = "long_only_buy_and_hold_equal_weight_spot_d1"

# Hard constraints any future baseline run must honor. Defined here as a contract;
# enforced by a SEPARATE, human-authorized runner that does not yet exist.
BASELINE_RUN_CONSTRAINTS: dict[str, Any] = {
    "strategy_id": BASELINE_STRATEGY_ID,
    "instrument_type": "spot",
    "timeframe": "1d",
    "symbols": list(QA_REQUIRED_SYMBOLS),
    "long_only": True,
    "allow_shorting": False,
    "allow_leverage": False,
    "allow_margin": False,
    "single_pass": True,
    "optimization": False,
    "parameter_search": False,
    "walk_forward": False,
    "lookahead_allowed": False,
    "uses_only_qa_passed_inputs": True,
    "writes_orders": False,
    "touches_broker_or_exchange": False,
}


def get_baseline_backtest_prep_label() -> str:
    """Human label for the recognized Crypto-D1 baseline backtest prep contract."""
    return PREP_LABEL


def baseline_run_constraints() -> dict[str, Any]:
    """Return a fresh copy of the baseline run constraints. Pure."""
    return dict(BASELINE_RUN_CONSTRAINTS)


def _read_csv_summary(path: str) -> dict[str, Any]:
    """Read a staged CSV read-only and summarize header + row count + date span.
    Never raises on bad data; returns ok=False with a reason instead."""
    prov = file_provenance(path)
    summary: dict[str, Any] = {
        "path": path,
        "exists": prov["exists"],
        "sha256": prov["sha256"],
        "size_bytes": prov["size_bytes"],
        "header": [],
        "schema_ok": False,
        "row_count": 0,
        "first_date": None,
        "last_date": None,
        "ok": False,
        "reason": "",
    }
    if not prov["exists"]:
        summary["reason"] = "file_missing"
        return summary
    with open(path, "r", encoding="utf-8", newline="") as fh:
        rows = [r for r in csv.reader(fh) if r and any(c.strip() for c in r)]
    if not rows:
        summary["reason"] = "empty_file"
        return summary
    header = [c.strip() for c in rows[0]]
    data = rows[1:]
    summary["header"] = header
    summary["schema_ok"] = header == list(QA_REQUIRED_FIELDS)
    summary["row_count"] = len(data)
    if data:
        summary["first_date"] = data[0][0].strip()
        summary["last_date"] = data[-1][0].strip()
    if not summary["schema_ok"]:
        summary["reason"] = "schema_header_mismatch"
    elif not data:
        summary["reason"] = "no_data_rows"
    else:
        summary["ok"] = True
    return summary


def _qa_report_provenance(repo_root: str) -> dict[str, Any]:
    """Read the on-disk qa_report.json read-only and return
    {found, verdict, sha_by_symbol}. Never raises."""
    path = os.path.join(repo_root, QA_REPORT_RELPATH)
    out: dict[str, Any] = {"found": False, "verdict": None, "sha_by_symbol": {}}
    if not os.path.isfile(path):
        return out
    out["found"] = True
    try:
        with open(path, "r", encoding="utf-8") as fh:
            report = json.load(fh)
    except (OSError, ValueError):
        return out
    out["verdict"] = report.get("verdict")
    for s in report.get("per_symbol", []) or []:
        if isinstance(s, dict):
            prov = s.get("provenance") or {}
            out["sha_by_symbol"][str(s.get("symbol"))] = prov.get("sha256")
    return out


def build_baseline_input_manifest(repo_root: str = ".") -> dict[str, Any]:
    """Build the baseline input manifest from the QA-passed staged CSVs. Reads the
    three staged files read-only; writes nothing. Pure aside from those reads."""
    input_dir = os.path.join(repo_root, QA_APPROVED_INPUT_DIR)
    entries: list[dict[str, Any]] = []
    for sym in QA_REQUIRED_SYMBOLS:
        path = os.path.join(input_dir, sym + "_1d.csv")
        s = _read_csv_summary(path)
        s["symbol"] = sym
        entries.append(s)
    return {
        "schema_version": PREP_SCHEMA_VERSION,
        "input_dir": QA_APPROVED_INPUT_DIR,
        "required_schema": list(QA_REQUIRED_FIELDS),
        "symbols": list(QA_REQUIRED_SYMBOLS),
        "per_symbol": entries,
    }


def check_baseline_prep_readiness(repo_root: str = ".") -> dict[str, Any]:
    """Decide whether a baseline backtest is PREPARED (not run). READY requires:
    all three staged files present, canonical schema, non-empty, each file
    byte-identical to what QA recorded (sha256 == qa_report provenance), and the
    qa_report verdict is PASS. Reads files read-only; writes nothing; runs no
    backtest."""
    manifest = build_baseline_input_manifest(repo_root)
    qa_prov = _qa_report_provenance(repo_root)
    receipt = build_qa_pass_receipt()
    receipt_ok = validate_qa_pass_receipt(receipt)["valid"]

    blockers: list[str] = []
    per_symbol: list[dict[str, Any]] = []
    for entry in manifest["per_symbol"]:
        sym = entry["symbol"]
        sym_blockers: list[str] = []
        if not entry["exists"]:
            sym_blockers.append("staged_file_missing")
        if entry["exists"] and not entry["schema_ok"]:
            sym_blockers.append("schema_header_mismatch")
        if entry["exists"] and entry["row_count"] <= 0:
            sym_blockers.append("no_data_rows")
        qa_sha = qa_prov["sha_by_symbol"].get(sym)
        sha_match = bool(qa_sha) and qa_sha == entry["sha256"]
        if not sha_match:
            sym_blockers.append("sha256_not_matching_qa_report")
        per_symbol.append(
            {
                "symbol": sym,
                "exists": entry["exists"],
                "schema_ok": entry["schema_ok"],
                "row_count": entry["row_count"],
                "first_date": entry["first_date"],
                "last_date": entry["last_date"],
                "sha256": entry["sha256"],
                "sha256_matches_qa_report": sha_match,
                "blockers": sym_blockers,
            }
        )
        blockers.extend(sym + ":" + b for b in sym_blockers)

    if not qa_prov["found"]:
        blockers.append("qa_report_missing")
    if qa_prov["verdict"] != VERDICT_PASS:
        blockers.append("qa_report_verdict_not_pass")
    if not receipt_ok:
        blockers.append("qa_pass_receipt_invalid")

    verdict = VERDICT_READY if not blockers else VERDICT_NOT_READY
    return {
        "schema_version": PREP_SCHEMA_VERSION,
        "label": PREP_LABEL,
        "mode": PREP_MODE,
        "verdict": verdict,
        "blockers": blockers,
        "qa_report_found": qa_prov["found"],
        "qa_report_verdict": qa_prov["verdict"],
        "qa_pass_receipt_valid": receipt_ok,
        "input_manifest": manifest,
        "per_symbol": per_symbol,
        "baseline_strategy_id": BASELINE_STRATEGY_ID,
        "baseline_run_constraints": baseline_run_constraints(),
        # Capability + gate posture (this contract executes / authorizes nothing):
        "executes": False,
        "runs_baseline": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "authorizes_baseline_backtest": False,
        "baseline_is_human_gated": True,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "no_network_used": True,
        "no_credentials_used": True,
        "manual_csv_only": True,
        "next_required_action": "HUMAN_APPROVED_BASELINE_BACKTEST_RUN",
    }


def validate_baseline_prep_report(report: Any) -> dict[str, Any]:
    """Validate a prep report's structure and safety invariants. Pure. Returns a
    {"valid": bool, "errors": [...]} dict; never raises."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"valid": False, "errors": ["report_not_a_dict"]}
    r = report

    if r.get("verdict") not in (VERDICT_READY, VERDICT_NOT_READY):
        errors.append("bad_verdict")

    must_be_locked = (
        "real_data_qa_blocked",
        "baseline_backtest_blocked",
        "paper_trading_gate_locked",
        "micro_live_gate_locked",
    )
    for key in must_be_locked:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "runs_baseline",
        "runs_backtest",
        "runs_optimization",
        "authorizes_baseline_backtest",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    constraints = r.get("baseline_run_constraints")
    if not isinstance(constraints, dict):
        errors.append("constraints_missing")
    else:
        for key in ("optimization", "parameter_search", "allow_shorting", "allow_leverage"):
            if constraints.get(key) is not False:
                errors.append("constraint_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_baseline_prep_markdown(report: Any) -> str:
    """Render a prep report as deterministic markdown. Pure string work."""
    r = report if isinstance(report, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Baseline Backtest Prep (PREP ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Baseline strategy: " + str(r.get("baseline_strategy_id", "")))
    lines.append("- QA report verdict: " + str(r.get("qa_report_verdict", "")))
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    blockers = r.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    lines.append("")
    lines.append("## Baseline input manifest")
    for s in r.get("per_symbol", []):
        lines.append(
            "- "
            + str(s.get("symbol"))
            + ": rows="
            + str(s.get("row_count"))
            + ", "
            + str(s.get("first_date"))
            + " -> "
            + str(s.get("last_date"))
            + ", sha_matches_qa="
            + str(s.get("sha256_matches_qa_report"))
        )
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- baseline_backtest: BLOCKED (human-gated; NOT run by this prep)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    return "\n".join(lines)

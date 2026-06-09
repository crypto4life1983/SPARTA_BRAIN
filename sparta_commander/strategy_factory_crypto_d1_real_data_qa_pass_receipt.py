"""Crypto-D1 Real Data QA PASS Receipt / Baseline-Prep Gate (READ-ONLY).

A PURE, stdlib-only, read-only module that RECORDS the evidence of the completed
Manual CSV Real Data QA run (BTC/ETH/SOL daily spot, verdict PASS) and surfaces
it as a baseline-prep gate. It authorizes NOTHING: it does not run a baseline, a
backtest, a simulation, paper, or live; it touches no broker/exchange; it fetches
no data; it accesses no credentials; and it UNLOCKS no gate.

The PASS receipt only states that Real Data QA has PASS *evidence*. The
real_data_qa gate and the baseline_backtest gate both stay BLOCKED, and the
paper / micro-live gates stay LOCKED, until a SEPARATE explicit human baseline-
prep policy decision is issued. Baseline remains the next GATED action -- never
auto-run.

It imports nothing that can reach a network, an exchange/broker, a credential,
or a .env. The only IO is an OPTIONAL read-only cross-check that reads the
already-written qa_report.json to confirm the recorded evidence still matches.

Public API:
  - RECEIPT_SCHEMA_VERSION / RECEIPT_LABEL / RECEIPT_MODE
  - VERDICT_PASS / RECEIPT_SOURCE_TAG / RECEIPT_SYMBOLS / RECEIPT_EVIDENCE
  - REAL_DATA_QA_GATE_STATE / NEXT_REQUIRED_ACTION / QA_REPORT_RELPATH
  - build_qa_pass_receipt()
  - validate_qa_pass_receipt(receipt)
  - render_qa_pass_receipt_markdown(receipt)
  - verify_against_qa_report(repo_root)
  - get_qa_pass_receipt_label()
"""

from __future__ import annotations

import json
import os
from typing import Any

RECEIPT_SCHEMA_VERSION = "strategy_factory_crypto_d1_real_data_qa_pass_receipt.v1"
RECEIPT_LABEL = (
    "Crypto-D1 Real Data QA PASS Receipt (Manual CSV) -- BTC/ETH/SOL PASS"
)
RECEIPT_MODE = "RESEARCH_ONLY"

VERDICT_PASS = "PASS"

# The source tag the approved Group A local files were staged under.
RECEIPT_SOURCE_TAG = "binance_usdt_spot_frozen_regime_inputs"

RECEIPT_SYMBOLS: tuple[str, ...] = ("BTC", "ETH", "SOL")

# Frozen evidence from the completed Manual CSV Real Data QA run (verdict PASS).
RECEIPT_EVIDENCE: tuple[dict[str, Any], ...] = (
    {
        "symbol": "BTC",
        "verdict": VERDICT_PASS,
        "row_count": 2351,
        "first_date": "2020-01-01",
        "last_date": "2026-06-08",
        "sha256": "69a9bdb12ee84331d499d71b762d3d4532083fceaa5e25bb4afc65fbdec846d7",
    },
    {
        "symbol": "ETH",
        "verdict": VERDICT_PASS,
        "row_count": 2351,
        "first_date": "2020-01-01",
        "last_date": "2026-06-08",
        "sha256": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    },
    {
        "symbol": "SOL",
        "verdict": VERDICT_PASS,
        "row_count": 2128,
        "first_date": "2020-08-11",
        "last_date": "2026-06-08",
        "sha256": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
    },
)

# PASS evidence exists, but the gate stays BLOCKED until a separate, explicit
# human baseline-prep policy decision. This receipt does NOT move the gate.
REAL_DATA_QA_GATE_STATE = "BLOCKED_PENDING_HUMAN_BASELINE_PREP_POLICY"

# The single next action this receipt declares: a SEPARATE, human-approved
# baseline-backtest prep gate. Nothing auto-runs.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_BASELINE_BACKTEST_PREP_GATE"

QA_REPORT_RELPATH = "reports/crypto_d1_real_data_qa/qa_report.json"


def get_qa_pass_receipt_label() -> str:
    """Human label for the recognized Crypto-D1 Real Data QA PASS receipt."""
    return RECEIPT_LABEL


def build_qa_pass_receipt() -> dict[str, Any]:
    """Return a fresh, deterministic QA PASS receipt dict. Pure; reads nothing.

    The receipt records PASS evidence and the unchanged gate posture; it
    authorizes nothing and unlocks nothing."""
    return {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "label": RECEIPT_LABEL,
        "mode": RECEIPT_MODE,
        "verdict": VERDICT_PASS,
        "source_tag": RECEIPT_SOURCE_TAG,
        "symbols": list(RECEIPT_SYMBOLS),
        "per_symbol": [dict(e) for e in RECEIPT_EVIDENCE],
        "real_data_qa_pass_evidence": True,
        "real_data_qa_gate_state": REAL_DATA_QA_GATE_STATE,
        # Gate posture (read-only metadata, unchanged by this receipt):
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        # Capability posture: this receipt executes / authorizes nothing.
        "executes": False,
        "runs_baseline": False,
        "runs_backtest": False,
        "authorizes_baseline_backtest": False,
        "baseline_is_human_gated": True,
        "no_network_used": True,
        "no_credentials_used": True,
        "manual_csv_only": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def validate_qa_pass_receipt(receipt: Any) -> dict[str, Any]:
    """Validate a receipt's structure and safety invariants. Pure. Returns a
    {"valid": bool, "errors": [...]} dict; never raises."""
    errors: list[str] = []
    r = receipt if isinstance(receipt, dict) else {}
    if not isinstance(receipt, dict):
        return {"valid": False, "errors": ["receipt_not_a_dict"]}

    if r.get("verdict") != VERDICT_PASS:
        errors.append("verdict_not_pass")

    per = r.get("per_symbol")
    if not isinstance(per, list) or not per:
        errors.append("per_symbol_missing")
    else:
        seen = []
        for s in per:
            if not isinstance(s, dict):
                errors.append("per_symbol_row_not_dict")
                continue
            seen.append(s.get("symbol"))
            if s.get("verdict") != VERDICT_PASS:
                errors.append("symbol_verdict_not_pass:" + str(s.get("symbol")))
            if not isinstance(s.get("row_count"), int) or s.get("row_count", 0) <= 0:
                errors.append("bad_row_count:" + str(s.get("symbol")))
            sha = s.get("sha256")
            if not (isinstance(sha, str) and len(sha) == 64):
                errors.append("bad_sha256:" + str(s.get("symbol")))
        if [x for x in seen] != list(RECEIPT_SYMBOLS):
            errors.append("symbol_set_mismatch")

    # Safety invariants: nothing may be unlocked or authorized.
    must_be_blocked = (
        "real_data_qa_blocked",
        "baseline_backtest_blocked",
        "paper_trading_gate_locked",
        "micro_live_gate_locked",
    )
    for key in must_be_blocked:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)
    must_be_false = (
        "executes",
        "runs_baseline",
        "runs_backtest",
        "authorizes_baseline_backtest",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("unexpected_next_required_action")

    return {"valid": not errors, "errors": errors}


def verify_against_qa_report(repo_root: str = ".") -> dict[str, Any]:
    """OPTIONAL read-only cross-check: read the already-written qa_report.json and
    confirm it still records verdict PASS with matching per-symbol SHA256s. Reads
    one file read-only; writes nothing; never raises."""
    path = os.path.join(repo_root, QA_REPORT_RELPATH)
    result: dict[str, Any] = {
        "report_path": path,
        "report_found": False,
        "verdict_matches": False,
        "sha256_matches": False,
        "mismatches": [],
    }
    if not os.path.isfile(path):
        result["mismatches"].append("qa_report_missing")
        return result
    result["report_found"] = True
    try:
        with open(path, "r", encoding="utf-8") as fh:
            report = json.load(fh)
    except (OSError, ValueError):
        result["mismatches"].append("qa_report_unreadable")
        return result

    result["verdict_matches"] = report.get("verdict") == VERDICT_PASS
    if not result["verdict_matches"]:
        result["mismatches"].append("verdict_not_pass_in_report")

    report_sha: dict[str, str] = {}
    for s in report.get("per_symbol", []) or []:
        if isinstance(s, dict):
            prov = s.get("provenance") or {}
            report_sha[str(s.get("symbol"))] = str(prov.get("sha256"))

    sha_ok = True
    for e in RECEIPT_EVIDENCE:
        sym = str(e["symbol"])
        if report_sha.get(sym) != e["sha256"]:
            sha_ok = False
            result["mismatches"].append("sha256_mismatch:" + sym)
    result["sha256_matches"] = sha_ok
    return result


def render_qa_pass_receipt_markdown(receipt: Any) -> str:
    """Render a receipt as deterministic markdown. Pure string work."""
    r = receipt if isinstance(receipt, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Real Data QA PASS Receipt")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Source tag: " + str(r.get("source_tag", "")))
    lines.append("- Real Data QA gate: " + str(r.get("real_data_qa_gate_state", "")))
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    lines.append("")
    lines.append("## Per-symbol PASS evidence")
    for s in r.get("per_symbol", []):
        lines.append(
            "- "
            + str(s.get("symbol"))
            + ": "
            + str(s.get("verdict"))
            + " (rows="
            + str(s.get("row_count"))
            + ", "
            + str(s.get("first_date"))
            + " -> "
            + str(s.get("last_date"))
            + ", sha256="
            + str(s.get("sha256"))
            + ")"
        )
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED by this receipt)")
    lines.append("- real_data_qa: BLOCKED (PASS evidence recorded; gate not moved)")
    lines.append("- baseline_backtest: BLOCKED (human-gated; not auto-run)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    return "\n".join(lines)

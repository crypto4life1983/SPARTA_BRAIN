"""Candidate #22 -- Phase B1 FORWARD + EXECUTION DATA READINESS REPORT (READ-ONLY, ONE-SHOT).

Renders the two Phase-B1 contracts to a deterministic JSON + Markdown readiness report, and
performs a READ-ONLY local inventory of post-2026-07-15 Trend Radar snapshots + expected-session
accounting for the initial 30-calendar-day horizon. It ADMITS NOTHING, RENAMES NOTHING,
FETCHES NOTHING, MUTATES NOTHING, and runs NO replay/simulation. Snapshot hashing is read-only.

The inventory portion depends on on-disk files, so the JSON report's snapshot section reflects
current local state; the contract sections are pure and byte-stable. The renderer sorts all
collections so a rerun over unchanged inputs is byte-identical.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_forward_exit_data_readiness_contract as _fed  # noqa: E402
import sparta_commander.c22_execution_data_short_instrument_feasibility_contract as _exe  # noqa: E402,E501

DATA_DIR = REPO_ROOT / _fed.DATA_DIR
REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_forward_execution_readiness"
BASENAME = "c22_forward_and_execution_data_readiness_phase_b1"
RECOMMEND_READY = "READY_FOR_HUMAN_REVIEW_OF_C22_FORWARD_AND_EXECUTION_DATA_CONTRACT"
RECOMMEND_BLOCKED = "BLOCKED_BY_FORWARD_OR_EXECUTION_DATA_CONTRACT_REQUIREMENTS"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _snapshot_structurally_valid(parsed: dict, run_date: str) -> tuple:
    """READ-ONLY structural check: single runDate matching filename, 50 result rows."""
    results = parsed.get("results", [])
    rds = {r.get("runDate") for r in results if isinstance(r, dict)}
    single = (len(rds) == 1 and next(iter(rds)) == run_date)
    return (single and len(results) == 50), len(results), single


def local_forward_inventory() -> dict:
    """READ-ONLY inventory of post-cutoff snapshots + initial-horizon session accounting.
    Never admits/renames/mutates."""
    cutoff = _fed.ENTRY_CUTOFF
    ir = _fed.initial_exit_data_range()
    horizon_sessions = _fed.expected_export_sessions(ir["start"], ir["end"])

    present_files = {}
    if DATA_DIR.is_dir():
        for p in sorted(DATA_DIR.glob(_fed.EXPORT_PREFIX + "*.json")):
            if not p.is_file():
                continue
            name = p.name
            digits = "".join(ch for ch in name if ch.isdigit())
            if len(digits) < 8:
                continue
            ymd = digits[:8]
            run_date = "%s-%s-%s" % (ymd[:4], ymd[4:6], ymd[6:8])
            if run_date <= cutoff:
                continue  # entry-period file, not a forward snapshot
            try:
                parsed = json.loads(p.read_text(encoding="utf-8"))
                valid, rows, single = _snapshot_structurally_valid(parsed, run_date)
            except Exception:  # noqa: BLE001
                valid, rows, single = False, 0, False
            present_files.setdefault(run_date, []).append(
                {"filename": name, "sha256": _sha256(p), "row_count": rows,
                 "structurally_valid": valid})

    inventory = []
    present_valid_dates = set()
    for run_date in sorted(present_files):
        entries = present_files[run_date]
        duplicate = len(entries) > 1
        best = entries[0]
        in_range = ir["start"] <= run_date <= ir["end"]
        klass = _fed.classify_inventory_date(
            run_date, present=True, structurally_valid=best["structurally_valid"],
            duplicate=duplicate, in_required_range=in_range)
        if klass == "VALID_EXIT_ONLY_CANDIDATE":
            present_valid_dates.add(run_date)
        inventory.append({
            "run_date": run_date, "files": entries, "duplicate": duplicate,
            "in_initial_horizon": in_range, "classification": klass,
            "would_qualify_exit_only_structurally": best["structurally_valid"] and not duplicate,
            "admitted": False})

    missing_through_latest = []
    latest_present = max(present_valid_dates) if present_valid_dates else ir["start"]
    for s in horizon_sessions:
        if s <= latest_present and s not in present_valid_dates:
            missing_through_latest.append(s)
    missing_full_horizon = [s for s in horizon_sessions if s not in present_valid_dates]

    coverage = _fed.readiness_from_coverage(horizon_sessions, present_valid_dates)
    return {
        "cutoff": cutoff,
        "initial_horizon": ir,
        "expected_horizon_sessions": horizon_sessions,
        "present_post_cutoff_snapshots": inventory,
        "present_valid_exit_only_candidate_dates": sorted(present_valid_dates),
        "missing_expected_sessions_through_latest_collected": missing_through_latest,
        "missing_expected_sessions_full_initial_horizon": missing_full_horizon,
        "coverage_verdict": coverage["readiness"],
        "coverage_complete": coverage["covered"],
    }


def build_report() -> dict:
    fed_c = _fed.build_forward_exit_data_contract()
    exe_c = _exe.build_execution_data_contract()
    fed_v = _fed.validate_forward_exit_data_contract(fed_c)
    exe_v = _exe.validate_execution_data_contract(exe_c)
    inv = local_forward_inventory()
    contracts_ok = (fed_c["verdict"] == _fed.VERDICT_READY and fed_v["valid"]
                    and exe_c["verdict"] == _exe.VERDICT_READY and exe_v["valid"]
                    and not fed_c["blockers"] and not exe_c["blockers"])
    recommendation = RECOMMEND_READY if contracts_ok else RECOMMEND_BLOCKED
    return {
        "report": "c22_forward_and_execution_data_readiness_phase_b1",
        "mode": "RESEARCH_ONLY_READ_ONLY_CONTRACT_AND_PLANNING",
        "forward_exit_data_contract": fed_c,
        "forward_exit_data_contract_valid": fed_v["valid"],
        "forward_exit_data_contract_failures": fed_v["failures"],
        "execution_data_contract": exe_c,
        "execution_data_contract_valid": exe_v["valid"],
        "execution_data_contract_failures": exe_v["failures"],
        "local_forward_inventory": inv,
        "contracts_ready": contracts_ok,
        "forward_data_coverage_verdict": inv["coverage_verdict"],
        "recommendation": recommendation,
        "no_data_admitted": True, "no_instrument_selected": True,
        "no_cost_base_case_approved": True, "no_replay_or_simulation": True,
        "no_token_issued_or_consumed": True, "no_lifecycle_advanced": True,
        "human_review_required": True,
    }


def canonical_report_bytes(report: dict) -> bytes:
    return json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def render_markdown(r: dict) -> str:
    fed_c = r["forward_exit_data_contract"]; exe_c = r["execution_data_contract"]
    inv = r["local_forward_inventory"]
    lines = [
        "# C22 Forward Exit-Data & Execution-Data Readiness — Phase B1",
        "",
        "Contract + inventory + planning only. Admits no data, selects no instrument, approves",
        "no cost base case, runs no replay, issues no token, activates no lifecycle gate.",
        "",
        "- Bound accepted replay-spec SHA-256: `%s`" % fed_c["bound_replay_spec_sha256"],
        "- Forward-data contract SHA-256: `%s`" % fed_c["contract_sha256"],
        "- Execution-data contract SHA-256: `%s`" % exe_c["contract_sha256"],
        "- Recommendation: **%s**" % r["recommendation"],
        "",
        "## A. Forward exit-only data contract",
        "- Entry cutoff **%s**; first exit-only date **%s**; no new entries after cutoff; "
        "post-cutoff files marked **%s**"
        % (fed_c["entry_cutoff"], fed_c["first_exit_only_date"],
           fed_c["post_cutoff_files_marked"]),
        "- Initial review **%d cal days** (%s → %s); deterministic **%d-day** extensions "
        "(first %s → %s)"
        % (fed_c["initial_review_calendar_days"], fed_c["initial_exit_data_range"]["start"],
           fed_c["initial_exit_data_range"]["end"], fed_c["extension_increment_calendar_days"],
           fed_c["first_extension_range"]["start"], fed_c["first_extension_range"]["end"]),
        "- Insufficient coverage → **%s**" % fed_c["insufficient_data_outcome"],
        "- Five-case distinction: %s" % ", ".join(
            "%s→%s" % (k, v) for k, v in sorted(fed_c["rev1_five_case_distinction"].items())),
        "",
        "## Local forward inventory (read-only; nothing admitted)",
        "- Cutoff %s; initial horizon %s → %s (%d expected weekday sessions)"
        % (inv["cutoff"], inv["initial_horizon"]["start"], inv["initial_horizon"]["end"],
           len(inv["expected_horizon_sessions"])),
    ]
    for s in inv["present_post_cutoff_snapshots"]:
        lines.append("- %s: %s (rows=%d, valid=%s) → **%s**"
                     % (s["run_date"], s["files"][0]["filename"], s["files"][0]["row_count"],
                        s["files"][0]["structurally_valid"], s["classification"]))
    lines += [
        "- Present valid EXIT_ONLY candidate dates: %s"
        % (", ".join(inv["present_valid_exit_only_candidate_dates"]) or "none"),
        "- Missing expected sessions through latest collected: %s"
        % (", ".join(inv["missing_expected_sessions_through_latest_collected"]) or "none"),
        "- Missing expected sessions across full initial 30-day horizon: %d (%s …)"
        % (len(inv["missing_expected_sessions_full_initial_horizon"]),
           ", ".join(inv["missing_expected_sessions_full_initial_horizon"][:5])),
        "- Forward-data coverage verdict: **%s**" % inv["coverage_verdict"],
        "",
        "## B. Execution-data & short-instrument feasibility",
        "- Short instrument: **%s** (selected=%s)"
        % (exe_c["short_instrument_status"], exe_c["instrument_selected"]),
        "- Option 1 (perp) requirements: %s"
        % ", ".join(exe_c["option_1_linear_perpetual_futures"]["requirements"]),
        "- Option 2 (spot-margin) requirements: %s"
        % ", ".join(exe_c["option_2_spot_margin_short"]["requirements"]),
        "- Prohibitions: %s" % "; ".join(exe_c["prohibitions"]),
        "- Basis review required: %s (adjustment selected=%s); fields: %s"
        % (exe_c["basis_alignment_review_required"], exe_c["basis_adjustment_selected"],
           ", ".join(exe_c["basis_alignment_diagnostic_fields"])),
        "- Cost components: %s" % ", ".join(exe_c["cost_components"]),
        "- 37 bps: **%s** (base case=%s); result levels: %s"
        % (exe_c["thirty_seven_bps_status"], exe_c["thirty_seven_bps_is_base_case"],
           ", ".join(exe_c["cost_result_levels"])),
        "- Liquidity evidence: %s" % ", ".join(exe_c["liquidity_feasibility_evidence"]),
        "",
        "## Proposed lifecycle gates (not activated)",
    ]
    for g in exe_c["proposed_lifecycle_gates"]:
        lines.append("1. `%s` — %s (token `%s`)" % (g["gate"], g["purpose"], g["human_token"]))
    lines += ["", "## Recommendation", "", "**%s**" % r["recommendation"], ""]
    return "\n".join(lines)


def _write_atomic(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(blob)
    os.replace(tmp, path)


def main() -> int:
    r = build_report()
    _write_atomic(REPORT_DIR / (BASENAME + ".json"), canonical_report_bytes(r))
    _write_atomic(REPORT_DIR / (BASENAME + ".md"), render_markdown(r).encode("utf-8"))
    inv = r["local_forward_inventory"]
    print(json.dumps({
        "recommendation": r["recommendation"],
        "contracts_ready": r["contracts_ready"],
        "forward_data_coverage_verdict": r["forward_data_coverage_verdict"],
        "forward_contract_sha256": r["forward_exit_data_contract"]["contract_sha256"],
        "execution_contract_sha256": r["execution_data_contract"]["contract_sha256"],
        "present_post_cutoff_dates": [s["run_date"] for s in inv["present_post_cutoff_snapshots"]],
        "present_valid_exit_only_candidates": inv["present_valid_exit_only_candidate_dates"],
        "missing_full_initial_horizon_count":
            len(inv["missing_expected_sessions_full_initial_horizon"]),
        "report_json": str((REPORT_DIR / (BASENAME + ".json")).relative_to(REPO_ROOT)).replace("\\", "/"),
        "report_md": str((REPORT_DIR / (BASENAME + ".md")).relative_to(REPO_ROOT)).replace("\\", "/"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

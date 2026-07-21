"""Candidate #22 -- Phase B2 SHORT-INSTRUMENT EVIDENCE REQUEST REPORT (READ-ONLY, ONE-SHOT).

Derives the 22-asset short universe READ-ONLY from the frozen V2 label artifact, builds the pure
evidence-request contract, and renders a deterministic JSON + Markdown report. The canonical JSON
contains all 22 separate asset records; the Markdown may summarize groups. Browses NOTHING,
fetches NOTHING, calls NO API, imports/admits NO data, selects NO instrument, approves NO
mapping/basis/cost, issues/consumes NO token, changes NO state. Reads the frozen artifact
read-only; no present-day-availability inference.
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_short_instrument_evidence_request_contract as _er  # noqa: E402

V2_ARTIFACT = (REPO_ROOT / "data/external_signum_trend_radar_gc/detector_labels/"
               "c22_gc_real_candle_entry_labels_multiwindow_v2_26w_2026-06-20_2026-07-15.json")
REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_short_instrument_evidence_request"
BASENAME = "c22_short_instrument_evidence_request_phase_b2"
RECOMMEND_READY = "READY_FOR_HUMAN_REVIEW_OF_C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST"
RECOMMEND_BLOCKED = "BLOCKED_BY_SHORT_INSTRUMENT_EVIDENCE_REQUEST_DEFECT"


def derive_asset_records() -> list:
    """READ-ONLY. Derive per-asset short records from the frozen V2 artifact. Never mutates."""
    d = json.loads(V2_ARTIFACT.read_text(encoding="utf-8"))
    labels = d["labels"]
    short_dates = defaultdict(list)
    bear = defaultdict(int)
    hedge = defaultdict(int)
    long_dates = defaultdict(list)
    for r in labels:
        sym = r["symbol"]; sig = r["signal"]; dt = r["source_date"]
        if sig == "BEAR_SHORT":
            bear[sym] += 1; short_dates[sym].append(dt)
        elif sig == "HEDGE_SHORT":
            hedge[sym] += 1; short_dates[sym].append(dt)
        elif sig == "LONG_ENTRY":
            long_dates[sym].append(dt)
    records = []
    for sym in sorted(short_dates):
        sd = sorted(short_dates[sym])
        records.append(_er.build_asset_record(
            sym, sd, bear[sym], hedge[sym], sorted(long_dates.get(sym, []))))
    return records


def build_report() -> dict:
    records = derive_asset_records()
    req = _er.build_evidence_request(records)
    v = _er.validate_evidence_request(req)
    ready = (req["verdict"] == _er.VERDICT_READY and v["valid"] and not req["blockers"])
    return {
        "report": "c22_short_instrument_evidence_request_phase_b2",
        "mode": "RESEARCH_ONLY_READ_ONLY_EVIDENCE_REQUEST",
        "evidence_request": req,
        "evidence_request_valid": v["valid"],
        "evidence_request_failures": v["failures"],
        "recommendation": (RECOMMEND_READY if ready else RECOMMEND_BLOCKED),
        "no_browsing": True, "no_fetch": True, "no_api_call": True, "no_data_admitted": True,
        "no_instrument_selected": True, "no_mapping_approved": True,
        "no_basis_adjustment_selected": True, "no_cost_approved": True,
        "no_token_issued_or_consumed": True, "no_lifecycle_advanced": True,
        "human_review_required": True,
    }


def canonical_report_bytes(report: dict) -> bytes:
    return json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def render_markdown(rep: dict) -> str:
    req = rep["evidence_request"]
    recs = req["asset_records"]
    lines = [
        "# C22 Short-Instrument Historical Evidence Request — Phase B2",
        "",
        "Provider-neutral evidence request for the 22 short assets. Browses nothing, fetches",
        "nothing, selects no instrument, approves no mapping/basis/cost, issues no token.",
        "",
        "- Bound replay-spec SHA: `%s`" % req["bound_replay_spec_sha256"],
        "- Bound forward-data / execution-data SHA: `%s` / `%s`"
        % (req["bound_forward_contract_sha256"], req["bound_execution_contract_sha256"]),
        "- Evidence-request contract SHA-256: `%s`" % req["contract_sha256"],
        "- Assets: **%d** · BEAR_SHORT %d · HEDGE_SHORT %d · acquisition **%s**"
        % (req["asset_count"], req["expected_bear_short"], req["expected_hedge_short"],
           req["acquisition_status"]),
        "- Recommendation: **%s**" % rep["recommendation"],
        "",
        "## Identity-risk classes (retained)",
        "- HIGH_COLLISION_RISK: %s" % ", ".join(req["high_collision_risk_assets"]),
        "- VENUE_LOCKED_NATIVE: %s" % ", ".join(req["venue_locked_native_assets"]),
        "- MAPPING_SENSITIVE: %s" % ", ".join(req["mapping_sensitive_assets"]),
        "- PARTIAL (Binance funding ends %s, insufficient): %s"
        % (req["partial_funding_local_end"], ", ".join(req["partial_funding_binance_assets"])),
        "- Borrow evidence: **%s**" % req["borrow_local_status_all"],
        "",
        "## Coverage periods",
        "- Entry evidence: %s → %s" % (req["entry_evidence_period"][0],
                                       req["entry_evidence_period"][1]),
        "- Initial exit evidence: %s → %s" % (req["initial_exit_evidence_period"][0],
                                              req["initial_exit_evidence_period"][1]),
        "- Later exit: deterministic %d-day increments; final exit end date known: %s"
        % (req["exit_extension_increment_days"], req["final_exit_end_date_known"]),
        "",
        "## Evidence matrix (22 assets)",
        "",
        "| Asset | risk | shorts (B/H) | first→last | perp | margin | funding | borrow | blocker |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for r in recs:
        lines.append("| %s | %s | %d/%d | %s→%s | %s | %s | %s | %s | %s |" % (
            r["signal_symbol"], r["mapping_risk_class"].replace("_", " ").lower(),
            r["bear_short_count"], r["hedge_short_count"], r["first_short_date"],
            r["last_short_date"], ("FAIL_CLOSED" if r["fail_closed_perp"] else "ok"),
            ("FAIL_CLOSED" if r["fail_closed_margin"] else "ok"), r["funding_status"],
            r["borrow_status"], r["current_fail_closed_blocker"]))
    lines += [
        "",
        "## Signal/execution basis alignment",
        "- Status: **%s** (no adjustment selected)" % req["basis_alignment_status"],
        "- Fields: %s" % ", ".join(req["basis_alignment_fields"]),
        "",
        "## Component-cost evidence",
        "- Components: %s" % ", ".join(req["cost_component_evidence"]),
        "- %s" % req["thirty_seven_bps_status"],
        "",
        "## Proposed lifecycle gates (not activated)",
    ]
    for g in req["proposed_lifecycle_gates"]:
        lines.append("1. `%s` — %s (token `%s`)" % (g["gate"], g["purpose"], g["human_token"]))
    lines += ["", "## Recommendation", "", "**%s**" % rep["recommendation"], ""]
    return "\n".join(lines)


def _write_atomic(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(blob)
    os.replace(tmp, path)


def main() -> int:
    rep = build_report()
    _write_atomic(REPORT_DIR / (BASENAME + ".json"), canonical_report_bytes(rep))
    _write_atomic(REPORT_DIR / (BASENAME + ".md"), render_markdown(rep).encode("utf-8"))
    req = rep["evidence_request"]
    print(json.dumps({
        "recommendation": rep["recommendation"],
        "evidence_request_valid": rep["evidence_request_valid"],
        "asset_count": req["asset_count"],
        "bear_short": sum(r["bear_short_count"] for r in req["asset_records"]),
        "hedge_short": sum(r["hedge_short_count"] for r in req["asset_records"]),
        "all_fail_closed_perp": req["all_assets_fail_closed_perp"],
        "all_fail_closed_margin": req["all_assets_fail_closed_margin"],
        "acquisition_status": req["acquisition_status"],
        "contract_sha256": req["contract_sha256"],
        "report_json": str((REPORT_DIR / (BASENAME + ".json")).relative_to(REPO_ROOT)).replace("\\", "/"),
        "report_md": str((REPORT_DIR / (BASENAME + ".md")).relative_to(REPO_ROOT)).replace("\\", "/"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

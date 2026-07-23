"""Candidate #22 -- Phase B3 HISTORICAL EVIDENCE ACQUISITION PLAN REPORT (READ-ONLY, ONE-SHOT).

Derives the Phase-B2 short-asset records READ-ONLY from the frozen V2 artifact, builds the pure
acquisition-plan contract, and renders a deterministic JSON + Markdown report (all 22 feasibility
rows kept separately in the canonical JSON). Browses NOTHING, fetches NOTHING, calls NO API, uses
NO credentials, imports/admits NO data, selects NO instrument, approves NO mapping/basis/cost,
creates NO evidence layout, issues/consumes NO token, changes NO state.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.c22_historical_evidence_acquisition_plan_contract as _ap  # noqa: E402
import tools.c22_short_instrument_evidence_request_report_once as _b2  # noqa: E402

V2_ARTIFACT = _b2.V2_ARTIFACT
REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_historical_evidence_acquisition_plan"
BASENAME = "c22_historical_evidence_acquisition_plan_phase_b3"
RECOMMEND_READY = "READY_FOR_HUMAN_REVIEW_OF_C22_HISTORICAL_EVIDENCE_ACQUISITION_PLAN"
RECOMMEND_BLOCKED = "BLOCKED_BY_UNRESOLVED_EVIDENCE_SOURCE_FEASIBILITY"


def b2_records() -> list:
    """READ-ONLY Phase-B2 asset records derived from the frozen V2 artifact."""
    return _b2.derive_asset_records()


def build_report() -> dict:
    plan = _ap.build_acquisition_plan(b2_records())
    v = _ap.validate_acquisition_plan(plan)
    ready = (plan["verdict"] == _ap.VERDICT_READY and v["valid"] and not plan["blockers"])
    return {
        "report": "c22_historical_evidence_acquisition_plan_phase_b3",
        "mode": "RESEARCH_ONLY_READ_ONLY_ACQUISITION_PLAN",
        "acquisition_plan": plan,
        "acquisition_plan_valid": v["valid"],
        "acquisition_plan_failures": v["failures"],
        "recommendation": (RECOMMEND_READY if ready else RECOMMEND_BLOCKED),
        "no_network": True, "no_browsing": True, "no_api_call": True, "no_credentials": True,
        "no_fetch": True, "no_admission": True, "no_instrument_selected": True,
        "no_layout_created": True, "no_token_issued_or_consumed": True,
        "no_lifecycle_advanced": True, "human_review_required": True,
    }


def canonical_report_bytes(report: dict) -> bytes:
    return json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def render_markdown(rep: dict) -> str:
    p = rep["acquisition_plan"]
    rows = p["feasibility_matrix"]
    lines = [
        "# C22 Historical Instrument Evidence Acquisition Plan — Phase B3",
        "",
        "Source-feasibility review + acquisition plan. Fetches nothing, browses nothing, uses no",
        "credentials, selects no instrument, creates no layout, issues no token.",
        "",
        "- Bound SHAs: spec `%s` · fwd `%s` · exe `%s` · b2 `%s`"
        % (p["bound_replay_spec_sha256"][:12], p["bound_forward_contract_sha256"][:12],
           p["bound_execution_contract_sha256"][:12], p["bound_evidence_request_sha256"][:12]),
        "- Acquisition plan SHA-256: `%s`" % p["contract_sha256"],
        "- Acquisition status: **%s** · Recommendation: **%s**"
        % (p["acquisition_status"], rep["recommendation"]),
        "",
        "## Source hierarchy (best → worst; T5 never decisive)",
    ]
    for i, t in enumerate(p["source_hierarchy"], 1):
        lines.append("%d. %s" % (i, t))
    lines += [
        "- Decisive minimum tier: %s" % p["decisive_minimum_tier"],
        "",
        "## Feasibility matrix (22 assets)",
        "",
        "| Asset | risk | difficulty | perp src | margin src | datasets | fail-closed |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append("| %s | %s | %s | %d cls | %d cls | ~%d | %s |" % (
            r["signal_symbol"], r["mapping_risk_class"].replace("_", " ").lower(),
            r["expected_acquisition_difficulty"], len(r["possible_perp_source_classes"]),
            len(r["possible_margin_source_classes"]), r["estimated_distinct_evidence_datasets"],
            "BOTH" if r["currently_fail_closed_both"] else "no"))
    lines += [
        "",
        "## Acquisition groups (per-asset validation preserved; no cross-venue substitution)",
    ]
    for g, syms in sorted(p["acquisition_groups"].items()):
        lines.append("- **%s** (%d): %s" % (g, len(syms), ", ".join(syms) or "none"))
    lines += [
        "",
        "## Credential & safety",
        "- Classes: %s" % ", ".join(p["credential_classes"]),
        "- Prohibited: %s" % ", ".join(p["prohibited_permissions"]),
        "- Authenticated read-only source = future human decision; no credentials created.",
        "",
        "## Proposed local evidence layout (NOT created; under gitignored data/)",
        "- Root: `%s`" % p["proposed_evidence_root"],
    ]
    for k, v in sorted(p["proposed_layout"].items()):
        lines.append("  - %s: `%s`" % (k, v))
    lines += [
        "- Filename convention: %s" % p["filename_convention"],
        "",
        "## Acquisition order (fail-close-early)",
    ]
    for step in p["acquisition_order"]:
        note = p["early_fail_close_steps"].get(step, "")
        lines.append("1. %s%s" % (step, (" — " + note) if note else ""))
    lines += [
        "",
        "## Forward-horizon handling",
        "- No new entries after %s; min acquisition start %s; initial range end %s; "
        "deterministic %d-day extensions; final exit end date known: %s"
        % (p["no_new_entry_after"], p["min_acquisition_range_start"], p["initial_range_end"],
           p["extension_increment_days"], p["final_exit_end_date_known"]),
        "- %s" % p["incremental_update_procedure"],
        "",
        "## Proposed authorization sequence (not activated)",
    ]
    for b in p["proposed_authorization_sequence"]:
        lines.append("1. `%s` — %s (token `%s`)" % (b["batch"], b["purpose"], b["human_token"]))
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
    p = rep["acquisition_plan"]
    from collections import Counter
    diff = Counter(r["expected_acquisition_difficulty"] for r in p["feasibility_matrix"])
    print(json.dumps({
        "recommendation": rep["recommendation"],
        "acquisition_plan_valid": rep["acquisition_plan_valid"],
        "asset_count": p["asset_count"],
        "acquisition_status": p["acquisition_status"],
        "difficulty_breakdown": dict(diff),
        "contract_sha256": p["contract_sha256"],
        "report_json": str((REPORT_DIR / (BASENAME + ".json")).relative_to(REPO_ROOT)).replace("\\", "/"),
        "report_md": str((REPORT_DIR / (BASENAME + ".md")).relative_to(REPO_ROOT)).replace("\\", "/"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

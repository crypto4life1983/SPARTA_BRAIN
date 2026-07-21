"""Candidate #22 -- C22 Replay Specification human-readable report (READ-ONLY, ONE-SHOT).

Renders the PURE Phase-A replay specification (from the committed spec contract) to a
deterministic JSON + Markdown report under reports/ for human review. It runs NO replay,
fetches NO data, issues/consumes NO token, and changes NO state. The report is a pure function
of the spec (no timestamps/env), so repeated runs are byte-identical.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_replay_spec_contract as _spec  # noqa: E402,E501

REPORT_DIR = REPO_ROOT / "reports" / "c22_gc_replay_spec"
BASENAME = "c22_gc_replay_specification_phase_a"


def render_markdown(s: dict) -> str:
    ev = s["frozen_evidence"]; inv = s["price_path_missing_data_inventory"]
    cm = s["execution_and_cost_model"]; rg = s["precommitted_rejection_gates"]
    em = s["exit_methodology"]; fx = s["forward_exit_path_extension_rule"]
    fa = s["forward_snapshot_alignment"]; sg = s["short_instrument_gate"]
    du = s["delisting_and_unavailability"]; sh = s["signal_handling"]; bm = s["benchmarks"]
    lines = [
        "# C22 Replay Specification — Phase A, REV1 (spec-only, research-only)",
        "",
        "Revised under %s. Freezes *how* a future C22 fee-honest replay would run over the"
        % s["revise_decision_ref"],
        "frozen V2 label evidence. Runs no replay, fetches/admits no data, approves no short",
        "model or cost base case, issues no token, unlocks no gate.",
        "",
        "- Verdict: **%s**" % s["verdict"],
        "- Spec SHA-256: `%s`" % s["spec_sha256"],
        "- Replay-advance token (downstream, not issued): `%s`" % s["replay_advance_token"],
        "",
        "## Frozen evidence",
        "- Range %s → %s, **%d windows**, **%d rows**, **%d actionable** (%s)"
        % (ev["date_range"][0], ev["date_range"][1], ev["decision_windows"],
           ev["total_label_rows"], ev["actionable_labels"],
           ", ".join("%s=%d" % (k, v) for k, v in sorted(ev["actionable_breakdown"].items()))),
        "- No new entry after %s; excluded future dates: %s"
        % (ev["no_new_entry_after"], ", ".join(ev["excluded_future_dates"])),
        "- Provenance tiers retained: %s"
        % ", ".join("%s=%d" % (k, v)
                    for k, v in sorted(ev["provenance_tier_counts_retained_in_attribution"].items())),
        "",
        "## Exit methodology & forward-data extension (point 1)",
        "- Long exit: `%s`; or `%s`" % (em["long_exit_below_upper_band"],
                                        em["long_exit_out_of_radar"]),
        "- Short: stop `%s`; TP `%s`; or out-of-radar"
        % (em["short_stop_close_above_filter"], em["short_take_profit"]),
        "- Max holding period in frozen spec: **%s** — no artificial strategy max-hold"
        % em["max_holding_period_in_frozen_spec"],
        "- Forced/administrative liquidation is a **non-decisive truncation diagnostic only**",
        "- Initial review %d calendar days; if positions remain open → **%s**; extend in "
        "predeclared **%d-day** increments until every position closes naturally"
        % (fx["initial_review_calendar_days"],
           em["unresolved_positions_after_reviewed_coverage"],
           fx["extension_increment_calendar_days"]),
        "- Weekend/non-export: %s" % fx["weekend_and_non_export_handling"],
        "",
        "## Forward Trend Radar snapshot use (point 4)",
        "- Authoritative export: %s" % fa["authoritative_export_for_gc_fields"],
        "- Out-of-radar = %s" % fa["out_of_radar_definition"],
        "- Friday→Monday: %s" % fa["friday_positions_before_monday"],
        "- Malformed/unavailable export: %s" % fa["malformed_or_unavailable_export"],
        "- Post-2026-07-15 snapshots marked `%s` and rejected for any entry"
        % fa["exit_only_manifest_marker"],
        "- Missing-data status: **%s** → %s (gate `%s`)"
        % (inv["status"], inv["insufficient_data_outcome"], inv["gate_required_before_use"]),
        "",
        "## Delisting / unavailability (point 5, separate from out-of-radar)",
    ] + ["- **%s**: %s" % (c, du[c]) for c in du["categories"]] + [
        "",
        "## Short instrument gate (point 2 — UNRESOLVED)",
        "- Status: **%s**; 37bps short model approved: **%s**"
        % (sg["status"], sg["thirty_seven_bps_short_model_approved"]),
        "- Human must select: %s" % " OR ".join(sg["options"].keys()),
        "- Fail-closed when: %s" % "; ".join(sg["fail_closed_when"]),
        "",
        "## Execution & cost model (point 3 — disaggregated)",
        "- Entry/exit reference: %s / %s" % (cm["entry_price_reference"], cm["exit_price_reference"]),
        "- Components: %s" % ", ".join(cm["disaggregated_cost_components"]),
        "- 37 bps role: **%s** (base case NOT frozen here; from %s)"
        % (cm["thirty_seven_bps_role"], cm["base_case_values_source"]),
        "- Results required at: %s" % ", ".join(cm["results_required_at_three_levels"]),
        "",
        "## Exposure ordering (point 6)",
        "- Deterministic order: %s" % " → ".join(sh["deterministic_competition_ordering"]),
        "- %s" % sh["exit_ordering_vs_entry"],
        "- Insufficient NAV: %s" % sh["insufficient_nav_rule"],
        "- No simultaneous long+short same asset: %s"
        % sh["no_simultaneous_long_and_short_same_asset"],
        "",
        "## Benchmarks (point 7)",
        "- %s" % ", ".join(bm["required"]),
        "- Survivorship control: %s" % bm["survivorship_bias_control"],
        "- Random null: %s" % bm["random_null_matching"],
        "",
        "## Pre-committed rejection gates (point 9 — four separated classes)",
        "- Integrity: %s" % "; ".join(rg["integrity_rejection"]),
        "- Data/execution: %s" % "; ".join(rg["data_or_execution_rejection"]),
        "- Economic: %s" % "; ".join(rg["economic_performance_rejection"]),
        "- Power warning: %s" % rg["insufficient_statistical_power_warning"]["warning"],
        "- Held-out (point 8): decisive=%s — %s"
        % (rg["held_out_segment"]["is_decisive_gate"], rg["held_out_segment"]["role"]),
        "",
        "## Proposed lifecycle gates (not activated)",
    ]
    for g in s["proposed_lifecycle_gates"]:
        lines.append("1. `%s` — %s (token `%s`)" % (g["gate"], g["purpose"], g["human_token"]))
    lines += ["", "## Recommendation", "",
              "**READY_FOR_SECOND_HUMAN_REVIEW_OF_C22_REPLAY_SPEC**"
              if s["verdict"] == _spec.VERDICT_READY
              else "**BLOCKED_BY_UNRESOLVED_REPLAY_SPEC_REQUIREMENTS**", ""]
    return "\n".join(lines)


def _write_atomic(path: Path, blob: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "wb") as fh:
        fh.write(blob)
    os.replace(tmp, path)


def main() -> int:
    s = _spec.build_replay_spec()
    check = _spec.validate_replay_spec(s)
    _write_atomic(REPORT_DIR / (BASENAME + ".json"), _spec.canonical_spec_bytes(s))
    _write_atomic(REPORT_DIR / (BASENAME + ".md"), render_markdown(s).encode("utf-8"))
    print(json.dumps({
        "verdict": s["verdict"], "validator_valid": check["valid"],
        "validator_failures": check["failures"], "spec_sha256": s["spec_sha256"],
        "report_json": str((REPORT_DIR / (BASENAME + ".json")).relative_to(REPO_ROOT)).replace("\\", "/"),
        "report_md": str((REPORT_DIR / (BASENAME + ".md")).relative_to(REPO_ROOT)).replace("\\", "/"),
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

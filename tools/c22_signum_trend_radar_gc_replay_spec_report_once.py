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
    lines = [
        "# C22 Replay Specification — Phase A (spec-only, research-only)",
        "",
        "Freezes *how* a future C22 fee-honest replay would run over the frozen V2 label",
        "evidence. Runs no replay, fetches no data, issues no token, unlocks no gate.",
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
        "- No date after %s; excluded future dates: %s"
        % (ev["no_date_after"], ", ".join(ev["excluded_future_dates"])),
        "- Provenance tiers retained: %s"
        % ", ".join("%s=%d" % (k, v)
                    for k, v in sorted(ev["provenance_tier_counts_retained_in_attribution"].items())),
        "",
        "## Exit methodology (single-sourced from the frozen detector spec)",
        "- Long exit: `%s`; or `%s`" % (s["exit_methodology"]["long_exit_below_upper_band"],
                                        s["exit_methodology"]["long_exit_out_of_radar"]),
        "- Short: stop `%s`; TP `%s`; or out-of-radar"
        % (s["exit_methodology"]["short_stop_close_above_filter"],
           s["exit_methodology"]["short_take_profit"]),
        "- Max holding period in frozen spec: **%s** (only bound = fail-closed END_OF_TEST)"
        % s["exit_methodology"]["max_holding_period_in_frozen_spec"],
        "",
        "## Price-path data — CRITICAL FINDING",
        "- %s" % s["price_path_data_contract"]["critical_finding"],
        "- Missing-data status: **%s** (gate: `%s`)"
        % (inv["status"], inv["gate_required_before_use"]),
        "- Forward exit-path snapshots required 2026-07-16 → END_OF_TEST; %s"
        % inv["hard_rule"],
        "- On disk but out-of-scope until gated: %s"
        % ", ".join(inv["already_on_disk_but_out_of_scope_until_gated"]),
        "",
        "## Execution & cost model (proposed, for human review)",
        "- Entry/exit reference: %s / %s" % (cm["entry_price_reference"], cm["exit_price_reference"]),
        "- Transaction cost: **%.0f bps all-in round-trip** (%s)"
        % (cm["proposed_transaction_cost_all_in_round_trip_bps"],
           "NOT silently inherited; long-appropriate, short-transaction only"),
        "- Short carry (funding if perp / borrow if margin) modeled separately; instrument "
        "UNRESOLVED pending human review",
        "",
        "## Benchmarks",
        "- %s" % ", ".join(s["benchmarks"]["required"]),
        "",
        "## Pre-committed rejection gates",
        "- Integrity: %s" % "; ".join(rg["integrity_rejection"]),
        "- Execution/data: %s" % "; ".join(rg["execution_or_data_rejection"]),
        "- Economic: %s" % "; ".join(rg["economic_performance_rejection"]),
        "- Power warning: %s" % rg["insufficient_statistical_power_warning"]["warning"],
        "",
        "## Proposed lifecycle gates (not activated)",
    ]
    for g in s["proposed_lifecycle_gates"]:
        lines.append("1. `%s` — %s (token `%s`)" % (g["gate"], g["purpose"], g["human_token"]))
    lines += ["", "## Recommendation", "",
              "**READY_FOR_HUMAN_REVIEW_OF_C22_REPLAY_SPEC**" if s["verdict"] == _spec.VERDICT_READY
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

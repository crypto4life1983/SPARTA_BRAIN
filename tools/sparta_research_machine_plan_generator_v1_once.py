"""SPARTA Research Machine Plan Generator v1 -- DRY-RUN / PLANNING ONLY.

Generates a `units.json` plan file for the SPARTA Guarded Research Machine v1 from the
current lane state plus an explicit human decision token -- so the operator does not
hand-write the plan. It is STRICTLY planning: it reads the lane (pure), classifies the
decision token, validates each DECLARED safe bounded unit against the Commit Guard
(explicit-path staging, no data/report artifacts) and the Orchestrator v2 auto-continue
categories, and emits a machine-compatible plan descriptor. It EXECUTES NOTHING: no git,
no shell, no network/fetch, no scheduler, no tests, no trading code, and it creates no
strategy/candidate on its own.

The generated plan is compatible with:
  python tools/sparta_guarded_research_machine_v1_once.py --plan-file <units.json>

It REFUSES:
  * a decision token that is a HARD HUMAN GATE that cannot be auto-planned
    (advance/reject, replay verdict, labels->replay, fetch, optimization/tuning/rescue,
    XAUUSD / new instrument class, scheduler, credentials/private APIs, paper/live/
    broker/order/trading);
  * starting C20 / any new candidate UNLESS the explicit human open-candidate token
    (HUMAN_APPROVED_..._OPEN_CANDIDATE_FAMILY_PROPOSAL) is supplied;
  * any unit whose category is not an Orchestrator v2 auto-continue category;
  * any unit that would stage a data/report artifact or use broad staging.

The only side effect (writing the units.json file) happens in main(); the planning
functions are pure. It pairs with Orchestrator v2, the Commit Guard, Runner v1,
Executor v1, and Machine v1.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sparta_commander.autopilot_research_orchestrator_v2_contract as _aro2  # noqa: E402,E501
import sparta_commander.explicit_allowlist_commit_guard_v1_contract as _cg  # noqa: E402,E501
import sparta_commander.guarded_orchestrator_runner_v1_contract as _gor  # noqa: E402,E501
import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane  # noqa: E402,E501

TOOL_NAME = "sparta_research_machine_plan_generator_v1_once"
IS_DRY_RUN_ONLY = True

# verdicts
VERDICT_PLAN_GENERATED = "PLAN_GENERATED"
VERDICT_REFUSED = "REFUSED_STOP_FOR_HUMAN"

# token classification fragments (upper-cased substring match)
HARD_GATE_TOKEN_FRAGMENTS = (
    "ADVANCE_TO", "REJECT", "AT_REPLAY", "REPLAY_VERDICT", "TO_REPLAY",
    "LABELS_TO_REPLAY", "FETCH", "OPTIMIZE", "OPTIMIS", "TUNE", "RESCUE", "XAUUSD",
    "GOLD", "SCHEDULER", "CREDENTIAL", "PRIVATE_API", "ACCOUNT_API", "PAPER", "LIVE",
    "BROKER", "ORDER", "DEPLOY",
)
NEW_CANDIDATE_TOKEN_FRAGMENTS = ("OPEN_CANDIDATE", "NEW_CANDIDATE", "C20",
                                 "START_CANDIDATE", "ASSIGN_C")
EXPLICIT_OPEN_CANDIDATE_SUFFIX = "OPEN_CANDIDATE_FAMILY_PROPOSAL"

# the final-report requirements the machine plan declares (reused from the runner)
FINAL_REPORT_REQUIREMENTS = list(_gor.FINAL_REPORT_REQUIREMENTS)


def classify_decision_token(decision_token: str | None) -> dict[str, Any]:
    """PURE. Classify the human decision token: is it a hard human gate, a
    new-candidate open, and/or the explicit open-candidate token."""
    tok = (decision_token or "")
    up = tok.upper()
    is_explicit_open = (up.startswith("HUMAN_APPROVED_")
                        and up.endswith(EXPLICIT_OPEN_CANDIDATE_SUFFIX))
    is_new_candidate = any(f in up for f in NEW_CANDIDATE_TOKEN_FRAGMENTS)
    # the explicit open-candidate token is allowed; other hard fragments are gates
    is_hard_gate = (not is_explicit_open) and any(
        f in up for f in HARD_GATE_TOKEN_FRAGMENTS)
    return {
        "decision_token": tok,
        "is_explicit_open_candidate_token": is_explicit_open,
        "is_new_candidate_open": is_new_candidate,
        "is_hard_human_gate": is_hard_gate,
        "is_empty": not tok,
    }


def _explicit_staging_command(expected_files: list) -> str:
    return "git add -- " + " ".join(str(f) for f in expected_files)


def build_unit_descriptor(spec: dict) -> dict[str, Any]:
    """PURE. Turn a declared unit spec into a machine-compatible bounded-unit
    descriptor with an EXPLICIT per-path staging command. Adds a `_errors` list for
    any safety problem (unsafe category, data/report artifact, missing files)."""
    spec = spec or {}
    category = spec.get("category")
    expected_files = [str(f).replace("\\", "/") for f in (spec.get("expected_files")
                                                          or [])]
    relevant_tests = [str(t).replace("\\", "/") for t in (spec.get("relevant_tests")
                                                          or [])]
    exemptions = spec.get("exemptions") or []
    exempt = {str(e.get("path")).replace("\\", "/") for e in exemptions
              if isinstance(e, dict) and e.get("path") and e.get("reviewed_contract")}

    errors: list = []
    if category not in _aro2.AUTO_CONTINUE_CATEGORIES:
        errors.append("category_not_auto_continue__%s" % category)
    if not expected_files:
        errors.append("no_expected_files")
    if not relevant_tests:
        errors.append("no_relevant_tests")
    for f in expected_files:
        if _cg.is_artifact_path(f) and f not in exempt:
            errors.append("data_or_report_artifact__%s" % f)

    staging_command = _explicit_staging_command(expected_files)
    if _cg.is_broad_staging_command(staging_command):       # defensive (never true)
        errors.append("broad_staging_generated")

    descriptor = {
        "category": category,
        "description": spec.get("description") or ("safe bounded research unit (%s)"
                                                   % category),
        "expected_files": expected_files,
        "relevant_tests": relevant_tests,
        "staging_command": staging_command,
        "staged_files": list(expected_files),
        "exemptions": list(exemptions),
        "commit_message_ref": spec.get("commit_message_ref"),
    }
    return {"descriptor": descriptor, "_errors": errors}


def generate_machine_plan(decision_token: str | None, unit_specs: list | None
                          ) -> dict[str, Any]:
    """PURE. Generate the machine plan from the decision token + declared unit specs,
    using the current lane state for context. Returns PLAN_GENERATED with the units
    (machine-compatible) or REFUSED with reasons. Executes nothing; writes nothing."""
    lane = _lane.get_lane_status()
    cls = classify_decision_token(decision_token)
    refusals: list = []

    if cls["is_empty"]:
        refusals.append("missing_decision_token")
    if cls["is_hard_human_gate"]:
        refusals.append("token_is_hard_human_gate_cannot_be_auto_planned")
    if cls["is_new_candidate_open"] and not cls["is_explicit_open_candidate_token"]:
        refusals.append("c20_or_new_candidate_requires_explicit_open_token")

    units: list = []
    if not refusals:
        for spec in (unit_specs or []):
            built = build_unit_descriptor(spec)
            if built["_errors"]:
                refusals.extend(built["_errors"])
            else:
                units.append(built["descriptor"])
        if not units and not refusals:
            refusals.append("no_safe_bounded_unit_specs_supplied")

    verdict = VERDICT_REFUSED if refusals else VERDICT_PLAN_GENERATED
    return {
        "tool": TOOL_NAME, "is_dry_run_only": True, "executes_nothing": True,
        "verdict": verdict,
        "refusal_reasons": refusals,
        "decision_token_classification": cls,
        # the machine-compatible plan (the --plan-file payload is `units`)
        "units": units,
        "plan_file_payload": units,
        "unit_count": len(units),
        "final_report_requirements": list(FINAL_REPORT_REQUIREMENTS),
        # lane context (read-only)
        "lane_active_candidate": lane.get("active_candidate"),
        "lane_last_rejected_candidate": lane.get("last_rejected_candidate"),
        "lane_rejected_ledger_count": lane.get("rejected_ledger_count"),
        "lane_next_required_action": lane.get("next_required_action"),
        # pairing
        "pairs_with": [
            "autopilot_research_orchestrator_v2_contract",
            "explicit_allowlist_commit_guard_v1_contract",
            "guarded_orchestrator_runner_v1_contract",
            "guarded_orchestrator_executor_v1_contract",
            "sparta_guarded_research_machine_v1_once",
        ],
        "compatible_with": (
            "python tools/sparta_guarded_research_machine_v1_once.py "
            "--plan-file <units.json>"),
        "requires_human_approval": True,
        "opening_new_candidate_requires_explicit_token": True,
    }


def main(argv: list | None = None) -> int:
    """Command-line entry point. DRY-RUN / PLANNING ONLY: reads the declared unit
    specs from --unit-spec-file (JSON list), classifies --decision-token, and writes
    the generated machine plan to --out-file (or prints to stdout). No git/shell/
    network/test execution -- the only side effect is writing the plan file."""
    import argparse
    parser = argparse.ArgumentParser(
        description="SPARTA Research Machine Plan Generator v1 -- DRY-RUN. Generates a "
                    "units.json plan for the Guarded Research Machine from the lane "
                    "state + a human decision token.")
    parser.add_argument("--decision-token", required=True,
                        help="the human-approved decision token")
    parser.add_argument("--unit-spec-file", default=None,
                        help="JSON list of declared safe bounded unit specs")
    parser.add_argument("--out-file", default=None,
                        help="where to write the generated units.json (else stdout)")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    unit_specs: list = []
    if args.unit_spec_file:
        with open(args.unit_spec_file, encoding="utf-8") as fh:
            unit_specs = json.load(fh)

    plan = generate_machine_plan(args.decision_token, unit_specs)
    if args.out_file and plan["verdict"] == VERDICT_PLAN_GENERATED:
        with open(args.out_file, "w", encoding="utf-8") as fh:
            json.dump(plan["plan_file_payload"], fh, indent=2, sort_keys=True)
        plan["written_plan_file"] = args.out_file
    print(json.dumps(plan, indent=2))
    return 0 if plan["verdict"] == VERDICT_PLAN_GENERATED else 1


if __name__ == "__main__":
    sys.exit(main())

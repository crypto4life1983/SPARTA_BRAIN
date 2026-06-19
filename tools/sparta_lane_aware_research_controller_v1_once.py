"""SPARTA Lane-Aware Research Controller v1 -- DRY-RUN / PLANNING ONLY.

Sits ABOVE the Research Machine Plan Generator v1 / Guarded Research Machine v1 /
Executor tool / Executor-Runner-Guard-Orchestrator-V2 stack. One command inspects the
current lane state plus a human decision token, derives the correct SCENARIO, builds
the proposed unit specs for it, and asks the Plan Generator to emit a machine-compatible
units.json. It is STRICTLY planning: it reads the lane (pure), produces a PROPOSAL, and
EXECUTES NOTHING -- no git, no shell, no network/fetch, no scheduler, no tests, no
trading code -- and creates no strategy/candidate on its own. The only side effect
(writing the plan file) happens in main().

Supported planning scenarios (token -> scenario -> declared safe bounded unit):
  1. automation-readiness research-only step
  2. active-candidate surface realignment (after a proposal commit)
  3. spec commit/push (after the spec is already built)
  4. detector dry-run commit/push (after the detector is already built)
  5. labels-review commit/push (after the labels evidence is already built)
  6. rejection ledger/surface bundle (after an explicit reject token)
  (+ family-proposal build, ONLY when the explicit open-candidate token is supplied.)

It REFUSES: unsupported / hard human-gate tokens (advance/reject-without-bundle,
replay verdict, labels->replay, fetch, optimization/tuning/rescue, XAUUSD / new
instrument class, scheduler, credentials/private APIs, paper/live/broker/order/trading),
and starting C20 / any new candidate unless the explicit
HUMAN_APPROVED_..._OPEN_CANDIDATE_FAMILY_PROPOSAL token is supplied. Every emitted unit
uses explicit per-path `git add --` staging (delegated to the Plan Generator + Commit
Guard) and stages no data/report artifacts.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane  # noqa: E402,E501
import tools.sparta_research_machine_plan_generator_v1_once as _gen  # noqa: E402,E501

TOOL_NAME = "sparta_lane_aware_research_controller_v1_once"
IS_DRY_RUN_ONLY = True

VERDICT_PLAN_GENERATED = "PLAN_GENERATED"
VERDICT_REFUSED = "REFUSED_STOP_FOR_HUMAN"

SUPPORTED_SCENARIOS = (
    "automation_readiness_step",
    "active_candidate_surface_realignment",
    "spec_commit_push",
    "detector_dry_run_commit_push",
    "labels_review_commit_push",
    "rejection_ledger_surface_bundle",
    "open_candidate_proposal_build",
)

# clean derived generator tokens (NO hard-gate / new-candidate fragments), so the
# strict Plan Generator accepts the safe build even when the human DECISION token
# itself (e.g. a REJECT decision) would otherwise look like a hard gate.
_GENERATOR_TOKENS = {
    "automation_readiness_step": "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY",
    "active_candidate_surface_realignment": "HUMAN_APPROVED_BUILD_SURFACE_REALIGNMENT",
    "spec_commit_push": "HUMAN_APPROVED_BUILD_AND_COMMIT_SPEC_UNIT",
    "detector_dry_run_commit_push":
        "HUMAN_APPROVED_BUILD_AND_COMMIT_DETECTOR_DRY_RUN_UNIT",
    "labels_review_commit_push": "HUMAN_APPROVED_BUILD_AND_COMMIT_LABELS_REVIEW_UNIT",
    "rejection_ledger_surface_bundle": "HUMAN_APPROVED_BUILD_LEDGER_AND_SURFACE_BUNDLE",
}

_SURFACE_FILES = (
    "sparta_commander/crypto_d1_candidate_research_lane_status_v1_contract.py",
    "sparta_commander/automation_readiness_bundle_integration_v1_contract.py",
    "tools/sparta_autopilot_morning_report.py",
    "jarvis_autopilot_morning_panel.py",
    "sparta_commander/human_gate_approval_workflow_v1_contract.py",
)
_SURFACE_TESTS = (
    "tests/test_crypto_d1_candidate_research_lane_status_v1_contract.py",
    "tests/test_automation_readiness_bundle_integration_v1_contract.py",
    "tests/test_sparta_autopilot_morning_report.py",
    "tests/test_jarvis_autopilot_morning_panel.py",
    "tests/test_human_gate_approval_workflow_v1_contract.py",
)
_LEDGER_FILES = (
    "sparta_commander/research_expansion_plan_v1_contract.py",
    "sparta_commander/safe_research_autopilot_v1_contract.py",
    "sparta_commander/research_expansion_autopilot_integration_v1_spec.py",
    "sparta_commander/gate_decision_coordinator_v1_contract.py",
    "sparta_commander/automation_readiness_research_prep_v1_contract.py",
)
_LEDGER_TESTS = (
    "tests/test_research_expansion_plan_v1_contract.py",
    "tests/test_safe_research_autopilot_v1_contract.py",
    "tests/test_research_expansion_autopilot_integration_v1_spec.py",
    "tests/test_gate_decision_coordinator_v1_contract.py",
    "tests/test_automation_readiness_research_prep_v1_contract.py",
)


def _derive_family(lane: dict, family_override: str | None) -> str:
    if family_override:
        return family_override
    det = lane.get("active_candidate_detail") or {}
    if det.get("family"):
        return det["family"]
    rej = lane.get("last_rejected_candidate_detail") or {}
    return rej.get("family") or "candidate_family"


def derive_scenario(decision_token: str | None, lane: dict) -> tuple:
    """PURE. Map the decision token (+ lane) to a supported scenario, or a refusal
    reason. Returns (scenario_or_None, refusal_reason_or_None)."""
    tok = decision_token or ""
    up = tok.upper()
    if not tok:
        return None, "missing_decision_token"
    # explicit open-candidate token first (the only way to plan new-candidate work)
    if (up.startswith("HUMAN_APPROVED_")
            and up.endswith(_gen.EXPLICIT_OPEN_CANDIDATE_SUFFIX)):
        return "open_candidate_proposal_build", None
    # an UNDECIDED advance/reject gate (ADVANCE_TO ... OR_REJECT, or an advance gate)
    # is a hard human gate -- it has not been decided, so it cannot be auto-planned.
    if "ADVANCE_TO" in up or "OR_REJECT" in up:
        return None, "unsupported_hard_human_gate"
    # a DECIDED reject -> the rejection ledger/surface BUNDLE build (a safe step)
    if "REJECT" in up:
        return "rejection_ledger_surface_bundle", None
    if "AUTOMATION_READINESS" in up:
        return "automation_readiness_step", None
    if "SURFACE_REALIGNMENT" in up or "ACTIVE_CANDIDATE_SURFACE" in up:
        return "active_candidate_surface_realignment", None
    if "COMMIT" in up and "DETECTOR" in up:
        return "detector_dry_run_commit_push", None
    if "COMMIT" in up and "LABELS" in up and "REPLAY" not in up:
        return "labels_review_commit_push", None
    if "COMMIT" in up and "SPEC" in up:
        return "spec_commit_push", None
    # new candidate without the explicit open token
    if any(f in up for f in _gen.NEW_CANDIDATE_TOKEN_FRAGMENTS):
        return None, "c20_or_new_candidate_requires_explicit_open_token"
    # any other hard-gate fragment is an unsupported human gate
    if any(f in up for f in _gen.HARD_GATE_TOKEN_FRAGMENTS):
        return None, "unsupported_hard_human_gate"
    return None, "unsupported_or_unrecognized_token"


def build_unit_specs(scenario: str, lane: dict, *, family_override: str | None = None,
                     artifact_slug: str | None = None) -> list[dict]:
    """PURE. The proposed safe bounded unit specs for a scenario. File paths are a
    PROPOSAL derived by convention from the lane context; the operator builds the
    files, then the machine commits exactly them."""
    fam = _derive_family(lane, family_override)
    if scenario == "automation_readiness_step":
        s = artifact_slug or "automation_readiness_research_step"
        return [{
            "category": "research_only_contract_or_test",
            "description": "build an automation-readiness research-only contract + test",
            "expected_files": ["sparta_commander/%s_v1_contract.py" % s,
                               "tests/test_%s_v1_contract.py" % s],
            "relevant_tests": ["tests/test_%s_v1_contract.py" % s],
            "commit_message_ref": "C:/tmp/%s_commit.txt" % s}]
    if scenario == "active_candidate_surface_realignment":
        return [{
            "category": "proposal_surface_realignment",
            "description": "realign lane/integration/morning/panel/human-gate to the "
                           "active candidate after its proposal commit",
            "expected_files": list(_SURFACE_FILES) + list(_SURFACE_TESTS),
            "relevant_tests": list(_SURFACE_TESTS),
            "commit_message_ref": "C:/tmp/surface_realignment_commit.txt"}]
    if scenario == "spec_commit_push":
        c = "sparta_commander/%s_v1_candidate_spec_contract.py" % fam
        t = "tests/test_%s_v1_candidate_spec_contract.py" % fam
        return [{"category": "spec_build_after_explicit_advance",
                 "description": "commit + push the candidate spec unit",
                 "expected_files": [c, t], "relevant_tests": [t],
                 "commit_message_ref": "C:/tmp/spec_commit.txt"}]
    if scenario == "detector_dry_run_commit_push":
        c = "sparta_commander/%s_v1_detector_spec_dry_run_contract.py" % fam
        t = "tests/test_%s_v1_detector_spec_dry_run_contract.py" % fam
        return [{"category": "detector_dry_run_build_after_explicit_advance",
                 "description": "commit + push the detector spec + dry-run unit",
                 "expected_files": [c, t], "relevant_tests": [t],
                 "commit_message_ref": "C:/tmp/detector_commit.txt"}]
    if scenario == "labels_review_commit_push":
        c = "sparta_commander/%s_v1_real_candle_labels_review_contract.py" % fam
        t = "tests/test_%s_v1_real_candle_labels_review_contract.py" % fam
        s = artifact_slug or "c_labels"
        runner = "tools/%s_real_candle_labels_once.py" % s
        rt = "tests/test_%s_real_candle_labels_once_runner_purity.py" % s
        return [{"category": "research_only_contract_or_test",
                 "description": "commit + push the real-candle labels review unit "
                                "(no data artifact committed)",
                 "expected_files": [runner, c, t, rt], "relevant_tests": [t, rt],
                 "commit_message_ref": "C:/tmp/labels_commit.txt"}]
    if scenario == "rejection_ledger_surface_bundle":
        new = ["sparta_commander/%s_v1_rejection_record_contract.py" % fam,
               "tests/test_%s_v1_rejection_record_contract.py" % fam]
        files = (new + list(_LEDGER_FILES) + list(_SURFACE_FILES)
                 + list(_LEDGER_TESTS) + list(_SURFACE_TESTS))
        tests = [new[1]] + list(_LEDGER_TESTS) + list(_SURFACE_TESTS)
        return [{"category": "review_ledger_surface_realignment_after_explicit_reject",
                 "description": "rejection record + ledger bump + surface realignment "
                                "bundle after the explicit reject decision",
                 "expected_files": files, "relevant_tests": tests,
                 "commit_message_ref": "C:/tmp/rejection_bundle_commit.txt"}]
    if scenario == "open_candidate_proposal_build":
        c = "sparta_commander/%s_v1_proposal_contract.py" % fam
        t = "tests/test_%s_v1_proposal_contract.py" % fam
        return [{"category": "research_only_contract_or_test",
                 "description": "build the family-proposal contract + test "
                                "(explicitly human-approved open-candidate)",
                 "expected_files": [c, t], "relevant_tests": [t],
                 "commit_message_ref": "C:/tmp/proposal_commit.txt"}]
    return []


def _generator_token(scenario: str, decision_token: str) -> str:
    if scenario == "open_candidate_proposal_build":
        return decision_token            # the explicit open token (generator allows)
    return _GENERATOR_TOKENS[scenario]


def run_controller(decision_token: str | None, *, family_override: str | None = None,
                   artifact_slug: str | None = None) -> dict[str, Any]:
    """PURE. Inspect the lane + decision token, derive the scenario, build the unit
    specs, and generate the machine plan via the Plan Generator. Executes nothing;
    writes nothing."""
    lane = _lane.get_lane_status()
    scenario, refusal = derive_scenario(decision_token, lane)

    base = {
        "tool": TOOL_NAME, "is_dry_run_only": True, "executes_nothing": True,
        "decision_token": decision_token or "",
        "supported_scenarios": list(SUPPORTED_SCENARIOS),
        "lane_active_candidate": lane.get("active_candidate"),
        "lane_last_rejected_candidate": lane.get("last_rejected_candidate"),
        "lane_rejected_ledger_count": lane.get("rejected_ledger_count"),
        "next_human_gate": lane.get("next_required_action"),
        "pairs_with": [
            "sparta_research_machine_plan_generator_v1_once",
            "sparta_guarded_research_machine_v1_once",
            "guarded_orchestrator_executor_v1_once",
        ],
        "opening_new_candidate_requires_explicit_token": True,
    }

    if scenario is None:
        base.update(verdict=VERDICT_REFUSED, scenario=None,
                    refusal_reasons=[refusal], proposed_unit_specs=[],
                    units_json=[], expected_files=[], tests=[], staging_commands=[],
                    generator_decision_token=None)
        return base

    specs = build_unit_specs(scenario, lane, family_override=family_override,
                             artifact_slug=artifact_slug)
    gen_token = _generator_token(scenario, decision_token)
    plan = _gen.generate_machine_plan(gen_token, specs)

    units = plan.get("units") or []
    expected = sorted({f for u in units for f in u.get("expected_files", [])})
    tests = sorted({t for u in units for t in u.get("relevant_tests", [])})
    staging = [u.get("staging_command") for u in units]

    base.update(
        verdict=plan.get("verdict"),
        scenario=scenario,
        generator_decision_token=gen_token,
        refusal_reasons=plan.get("refusal_reasons") or [],
        proposed_unit_specs=specs,
        units_json=plan.get("plan_file_payload") or [],
        expected_files=expected,
        tests=tests,
        staging_commands=staging,
        final_report_requirements=plan.get("final_report_requirements"),
    )
    return base


def main(argv: list | None = None) -> int:
    """Command-line entry point. DRY-RUN / PLANNING ONLY: inspects the lane + the
    --decision-token, derives the scenario, builds the proposed unit specs, generates
    the machine plan, and writes it to --out-file (or prints). No git/shell/network/
    test execution -- the only side effect is writing the plan file."""
    import argparse
    parser = argparse.ArgumentParser(
        description="SPARTA Lane-Aware Research Controller v1 -- DRY-RUN. Turns one "
                    "human decision token + the lane state into a machine units.json "
                    "plan.")
    parser.add_argument("--decision-token", required=True)
    parser.add_argument("--family", default=None,
                        help="override the candidate family slug (else derived)")
    parser.add_argument("--artifact-slug", default=None)
    parser.add_argument("--out-file", default=None,
                        help="where to write the generated units.json (else stdout)")
    parser.add_argument("--repo-root", default=".")
    args = parser.parse_args(argv)

    out = run_controller(args.decision_token, family_override=args.family,
                         artifact_slug=args.artifact_slug)
    if args.out_file and out["verdict"] == VERDICT_PLAN_GENERATED:
        with open(args.out_file, "w", encoding="utf-8") as fh:
            json.dump(out["units_json"], fh, indent=2, sort_keys=True)
        out["written_plan_file"] = args.out_file
    print(json.dumps(out, indent=2))
    return 0 if out["verdict"] == VERDICT_PLAN_GENERATED else 1


if __name__ == "__main__":
    sys.exit(main())

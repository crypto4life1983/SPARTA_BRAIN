"""Safety tests for the dry-run Lane-Aware Research Controller
(tools/sparta_lane_aware_research_controller_v1_once.py).

The controller touches NO git / shell / network: it reads the lane (pure), derives a
scenario from the decision token, builds proposed unit specs, and emits a
machine-compatible units.json via the Plan Generator. These tests use only in-memory
calls + a temp out-file (pytest tmp_path) and never mutate the real repo.

Verified: the 6 supported planning scenarios (+ explicit open-candidate proposal build);
refusal of unsupported / hard human gates (undecided advance/reject, fetch, replay,
optimization, etc.); refusal of C20 / new candidate without the explicit open token;
every emitted unit uses explicit per-path `git add --` staging and stages no data/report
artifact; the generated units pass the dry-run Guarded Runner; main writes the plan only
on success and executes nothing; no git/subprocess/network in the source."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import sparta_commander.guarded_orchestrator_runner_v1_contract as gor
import sparta_commander.explicit_allowlist_commit_guard_v1_contract as cg
import tools.sparta_lane_aware_research_controller_v1_once as ctl


def _run(tok, **kw):
    return ctl.run_controller(tok, **kw)


# ---- dry-run posture + pairing ---------------------------------------------

def test_dry_run_only_and_pairs_with_stack():
    r = _run("BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY")
    assert r["is_dry_run_only"] is True
    assert r["executes_nothing"] is True
    assert ctl.IS_DRY_RUN_ONLY is True
    for piece in ("sparta_research_machine_plan_generator_v1_once",
                  "sparta_guarded_research_machine_v1_once",
                  "guarded_orchestrator_executor_v1_once"):
        assert piece in r["pairs_with"]
    assert set(ctl.SUPPORTED_SCENARIOS) >= {
        "automation_readiness_step", "active_candidate_surface_realignment",
        "spec_commit_push", "detector_dry_run_commit_push",
        "labels_review_commit_push", "rejection_ledger_surface_bundle"}


# ---- the 6 supported scenarios (+ explicit open) ---------------------------

_SCENARIO_TOKENS = {
    "automation_readiness_step": "BUILD_AUTOMATION_READINESS_STEP_RESEARCH_ONLY",
    "active_candidate_surface_realignment":
        "HUMAN_APPROVED_C19_ACTIVE_CANDIDATE_SURFACE_REALIGNMENT",
    "spec_commit_push": "APPROVE_COMMIT_C19_CANDIDATE_SPEC_UNIT",
    "detector_dry_run_commit_push": "APPROVE_COMMIT_C19_DETECTOR_DRY_RUN_UNIT",
    "labels_review_commit_push": "APPROVE_COMMIT_C19_REAL_CANDLE_LABELS_UNIT",
    "rejection_ledger_surface_bundle": "HUMAN_DECISION_C19_REJECT_AT_REAL_CANDLE_LABELS",
    "open_candidate_proposal_build":
        "HUMAN_APPROVED_C20_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL",
}
_EXPECTED_CATEGORY = {
    "automation_readiness_step": "research_only_contract_or_test",
    "active_candidate_surface_realignment": "proposal_surface_realignment",
    "spec_commit_push": "spec_build_after_explicit_advance",
    "detector_dry_run_commit_push": "detector_dry_run_build_after_explicit_advance",
    "labels_review_commit_push": "research_only_contract_or_test",
    "rejection_ledger_surface_bundle":
        "review_ledger_surface_realignment_after_explicit_reject",
    "open_candidate_proposal_build": "research_only_contract_or_test",
}


def test_all_supported_scenarios_generate_plans():
    for scenario, tok in _SCENARIO_TOKENS.items():
        r = _run(tok, family_override="oos_rv")
        assert r["verdict"] == "PLAN_GENERATED", (scenario, r["refusal_reasons"])
        assert r["scenario"] == scenario
        assert r["units_json"], scenario
        assert r["units_json"][0]["category"] == _EXPECTED_CATEGORY[scenario], scenario
        # explicit per-path staging only
        for sc in r["staging_commands"]:
            assert sc.startswith("git add -- ")
            assert cg.is_broad_staging_command(sc) is False
        # never stages a data/report artifact
        for f in r["expected_files"]:
            assert cg.is_artifact_path(f) is False, (scenario, f)


def test_scenario_outputs_have_required_fields():
    r = _run("APPROVE_COMMIT_C19_CANDIDATE_SPEC_UNIT", family_override="oos_rv")
    for k in ("proposed_unit_specs", "units_json", "expected_files", "tests",
              "staging_commands", "refusal_reasons", "next_human_gate",
              "generator_decision_token", "scenario"):
        assert k in r, k
    assert r["next_human_gate"]   # surfaced from the lane


def test_labels_scenario_includes_runner_and_review_and_no_artifact():
    r = _run("APPROVE_COMMIT_C19_REAL_CANDLE_LABELS_UNIT", family_override="oos_rv",
             artifact_slug="c19_labels")
    files = r["expected_files"]
    assert any("real_candle_labels_review_contract.py" in f for f in files)
    assert any("real_candle_labels_once.py" in f for f in files)
    # the labels artifact (data/...) is NOT in the unit -- only code/tests
    assert all(not f.startswith("data/") for f in files)


def test_rejection_bundle_includes_record_ledger_and_surfaces():
    r = _run("HUMAN_DECISION_C19_REJECT_AT_REAL_CANDLE_LABELS", family_override="oos_rv")
    files = r["expected_files"]
    assert any("rejection_record_contract.py" in f for f in files)
    assert "sparta_commander/research_expansion_plan_v1_contract.py" in files
    assert ("sparta_commander/crypto_d1_candidate_research_lane_status_v1_contract.py"
            in files)


# ---- generated units pass the dry-run runner (pairing proof) ---------------

def test_generated_units_pass_dry_run_runner():
    for tok in _SCENARIO_TOKENS.values():
        r = _run(tok, family_override="oos_rv")
        for unit in r["units_json"]:
            u = dict(unit)
            u.update(
                precheck={"clean_working_tree": True,
                          "head_equals_origin_master": True,
                          "no_mutating_shell_pending": True,
                          "expected_files_only": True},
                tests={"ran": True, "passed": True},
                untracked_clutter_present=True)
            plan = gor.plan_bounded_research_unit(u)
            assert plan["verdict"] == "PLAN_READY_DRY_RUN", (tok, plan["refusal_reasons"])


# ---- refusals --------------------------------------------------------------

def test_refuse_undecided_advance_reject_gate():
    for tok in ("HUMAN_DECISION_C19_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT",
                "HUMAN_DECISION_C18_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"):
        r = _run(tok)
        assert r["verdict"] == "REFUSED_STOP_FOR_HUMAN", tok
        assert r["scenario"] is None
        assert "unsupported_hard_human_gate" in r["refusal_reasons"]


def test_refuse_hard_gates():
    for tok in ("APPROVE_FETCH_DATA", "APPROVE_OPTIMIZE_PARAMS",
                "APPROVE_PAPER_TRADING", "APPROVE_LIVE_BROKER_ORDER",
                "APPROVE_XAUUSD_DATA", "APPROVE_SCHEDULER_CHANGE",
                "APPROVE_CREDENTIALS", "APPROVE_REPLAY_VERDICT"):
        r = _run(tok)
        assert r["verdict"] == "REFUSED_STOP_FOR_HUMAN", tok
        assert r["units_json"] == [], tok


def test_refuse_c20_without_explicit_open_token():
    for tok in ("HUMAN_APPROVED_OPEN_C20", "HUMAN_APPROVED_NEW_CANDIDATE_FAMILY",
                "HUMAN_APPROVED_START_CANDIDATE_C20"):
        r = _run(tok)
        assert r["verdict"] == "REFUSED_STOP_FOR_HUMAN", tok
        assert "c20_or_new_candidate_requires_explicit_open_token" in (
            r["refusal_reasons"]), tok


def test_refuse_unrecognized_and_missing_token():
    assert _run("SOME_RANDOM_TOKEN")["refusal_reasons"] == [
        "unsupported_or_unrecognized_token"]
    assert _run("")["refusal_reasons"] == ["missing_decision_token"]


# ---- main: writes only on success, executes nothing ------------------------

def test_main_writes_plan_file_on_success(tmp_path, capsys):
    out_file = tmp_path / "units.json"
    rc = ctl.main(["--decision-token", "APPROVE_COMMIT_C19_CANDIDATE_SPEC_UNIT",
                   "--family", "oos_rv", "--out-file", str(out_file),
                   "--repo-root", str(tmp_path)])
    assert rc == 0
    assert out_file.exists()
    payload = json.loads(out_file.read_text(encoding="utf-8"))
    assert isinstance(payload, list) and payload
    assert payload[0]["staging_command"].startswith("git add -- ")


def test_main_refused_token_writes_no_file(tmp_path, capsys):
    out_file = tmp_path / "units.json"
    rc = ctl.main(["--decision-token", "APPROVE_FETCH_DATA",
                   "--out-file", str(out_file)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert out["verdict"] == "REFUSED_STOP_FOR_HUMAN"
    assert not out_file.exists()


def test_source_has_no_git_shell_network():
    src = Path(ctl.__file__).read_text(encoding="utf-8")
    for tok in ("subprocess", "import requests", "from requests", "import urllib",
                "import socket", "import ccxt", "os.environ", "getenv", "urlopen",
                "Popen", "check_output", "system("):
        assert tok not in src, tok
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = (node.func.attr if isinstance(node.func, ast.Attribute)
                    else getattr(node.func, "id", ""))
            assert name not in ("run", "Popen", "call", "check_output", "system")

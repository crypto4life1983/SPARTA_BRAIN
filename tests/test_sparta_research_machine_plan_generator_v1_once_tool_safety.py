"""Safety tests for the dry-run Research Machine Plan Generator
(tools/sparta_research_machine_plan_generator_v1_once.py).

The generator touches NO git / shell / network: it reads the lane (pure) and emits a
machine-compatible units.json. These tests use only in-memory specs + a temp out-file
(pytest tmp_path) and never mutate the real repo.

Verified: dry-run / planning only; classifies the decision token; refuses hard human
gates and C20 / new-candidate without the explicit open token; emits only safe bounded
units with explicit per-path `git add --` staging and no data/report artifacts; the
generated units are machine-compatible and pass the dry-run Guarded Runner; main writes
the plan only on success and never executes anything; no git/subprocess/network in the
source."""
from __future__ import annotations

import ast
import json
from pathlib import Path

import sparta_commander.guarded_orchestrator_runner_v1_contract as gor
import tools.sparta_research_machine_plan_generator_v1_once as gen


def _spec(category="research_only_contract_or_test", n=1):
    return {
        "category": category,
        "description": "build a pure contract + test",
        "expected_files": ["sparta_commander/x%d_contract.py" % n,
                            "tests/test_x%d.py" % n],
        "relevant_tests": ["tests/test_x%d.py" % n],
        "commit_message_ref": "C:/tmp/x%d.txt" % n,
    }


# ---- dry-run / planning posture --------------------------------------------

def test_dry_run_only_and_executes_nothing():
    p = gen.generate_machine_plan("HUMAN_APPROVED_BUILD_RESEARCH_ONLY_CONTRACT",
                                  [_spec()])
    assert p["is_dry_run_only"] is True
    assert p["executes_nothing"] is True
    assert gen.IS_DRY_RUN_ONLY is True


def test_pairs_with_full_stack():
    p = gen.generate_machine_plan("HUMAN_APPROVED_BUILD_RESEARCH_ONLY_CONTRACT",
                                  [_spec()])
    for piece in ("autopilot_research_orchestrator_v2_contract",
                  "explicit_allowlist_commit_guard_v1_contract",
                  "guarded_orchestrator_runner_v1_contract",
                  "guarded_orchestrator_executor_v1_contract",
                  "sparta_guarded_research_machine_v1_once"):
        assert piece in p["pairs_with"]
    assert "--plan-file" in p["compatible_with"]


# ---- generate a safe plan --------------------------------------------------

def test_safe_token_generates_machine_compatible_plan():
    p = gen.generate_machine_plan("HUMAN_APPROVED_BUILD_RESEARCH_ONLY_CONTRACT_AND_TEST",
                                  [_spec(n=1), _spec(n=2)])
    assert p["verdict"] == "PLAN_GENERATED"
    assert p["refusal_reasons"] == []
    assert p["unit_count"] == 2
    assert p["plan_file_payload"] == p["units"]
    u = p["units"][0]
    # machine-compatible descriptor keys
    for k in ("category", "expected_files", "relevant_tests", "staging_command",
              "staged_files", "commit_message_ref"):
        assert k in u, k
    # explicit per-path staging (never broad)
    assert u["staging_command"].startswith("git add -- ")
    assert gen._cg.is_broad_staging_command(u["staging_command"]) is False
    assert u["staged_files"] == u["expected_files"]


def test_generated_unit_passes_dry_run_runner():
    p = gen.generate_machine_plan("HUMAN_APPROVED_BUILD_RESEARCH_ONLY_CONTRACT",
                                  [_spec()])
    unit = dict(p["units"][0])
    # supply a clean precheck + green tests snapshot and run the dry-run runner
    unit.update(
        precheck={"clean_working_tree": True, "head_equals_origin_master": True,
                  "no_mutating_shell_pending": True, "expected_files_only": True},
        tests={"ran": True, "passed": True},
        untracked_clutter_present=True)
    plan = gor.plan_bounded_research_unit(unit)
    assert plan["verdict"] == "PLAN_READY_DRY_RUN"
    assert plan["refusal_reasons"] == []


# ---- refuse hard human gates -----------------------------------------------

def test_refuse_hard_human_gate_tokens():
    for tok in ("HUMAN_DECISION_C19_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT",
                "HUMAN_DECISION_C19_REJECT_AT_REAL_CANDLE_LABELS",
                "HUMAN_DECISION_C18_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT",
                "APPROVE_FETCH_BTCUSD", "APPROVE_OPTIMIZE_PARAMS",
                "APPROVE_PAPER_TRADING", "APPROVE_LIVE_BROKER_ORDER",
                "APPROVE_XAUUSD_DATA", "APPROVE_SCHEDULER_CHANGE",
                "APPROVE_CREDENTIALS"):
        p = gen.generate_machine_plan(tok, [_spec()])
        assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN", tok
        assert p["units"] == [], tok


def test_classify_decision_token():
    c = gen.classify_decision_token(
        "HUMAN_DECISION_C19_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT")
    assert c["is_hard_human_gate"] is True
    c2 = gen.classify_decision_token("HUMAN_APPROVED_BUILD_RESEARCH_ONLY_CONTRACT")
    assert c2["is_hard_human_gate"] is False
    assert c2["is_new_candidate_open"] is False


# ---- refuse C20 / new candidate without the explicit open token ------------

def test_refuse_new_candidate_without_explicit_open_token():
    for tok in ("HUMAN_APPROVED_OPEN_C20", "HUMAN_APPROVED_START_CANDIDATE_C20",
                "HUMAN_APPROVED_NEW_CANDIDATE_FAMILY"):
        p = gen.generate_machine_plan(tok, [_spec()])
        assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN", tok
        assert "c20_or_new_candidate_requires_explicit_open_token" in (
            p["refusal_reasons"]), tok


def test_explicit_open_candidate_token_allowed():
    tok = "HUMAN_APPROVED_C20_RESEARCH_DIRECTION__OPEN_CANDIDATE_FAMILY_PROPOSAL"
    c = gen.classify_decision_token(tok)
    assert c["is_explicit_open_candidate_token"] is True
    p = gen.generate_machine_plan(tok, [_spec()])
    assert p["verdict"] == "PLAN_GENERATED"
    assert p["opening_new_candidate_requires_explicit_token"] is True


# ---- refuse unsafe units ---------------------------------------------------

def test_refuse_data_or_report_artifact_unit():
    for art in ("data/labels.csv", "reports/run.md", "x/result.json"):
        spec = {"category": "research_only_contract_or_test",
                "expected_files": ["sparta_commander/x_contract.py", art],
                "relevant_tests": ["tests/test_x.py"], "commit_message_ref": "m"}
        p = gen.generate_machine_plan("HUMAN_APPROVED_BUILD_X", [spec])
        assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN", art
        assert any("artifact" in r for r in p["refusal_reasons"]), art


def test_refuse_non_auto_continue_category():
    spec = {"category": "start_new_candidate_c_number",
            "expected_files": ["sparta_commander/x.py"],
            "relevant_tests": ["tests/test_x.py"], "commit_message_ref": "m"}
    p = gen.generate_machine_plan("HUMAN_APPROVED_BUILD_X", [spec])
    assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN"
    assert any("category_not_auto_continue" in r for r in p["refusal_reasons"])


def test_refuse_missing_token_and_no_units():
    assert gen.generate_machine_plan("", [_spec()])["verdict"] == (
        "REFUSED_STOP_FOR_HUMAN")
    p = gen.generate_machine_plan("HUMAN_APPROVED_BUILD_X", [])
    assert p["verdict"] == "REFUSED_STOP_FOR_HUMAN"
    assert "no_safe_bounded_unit_specs_supplied" in p["refusal_reasons"]


def test_artifact_allowed_with_reviewed_exemption():
    spec = {"category": "data_readiness_contract",
            "expected_files": ["sparta_commander/x_contract.py", "data/frozen.json"],
            "relevant_tests": ["tests/test_x.py"], "commit_message_ref": "m",
            "exemptions": [{"path": "data/frozen.json",
                            "reviewed_contract": "x_data_readiness_contract"}]}
    p = gen.generate_machine_plan("HUMAN_APPROVED_BUILD_DATA_READINESS", [spec])
    assert p["verdict"] == "PLAN_GENERATED"


# ---- main writes only on success; never executes / mutates real repo -------

def test_main_writes_plan_file_on_success(tmp_path, capsys):
    spec_file = tmp_path / "specs.json"
    spec_file.write_text(json.dumps([_spec()]), encoding="utf-8")
    out_file = tmp_path / "units.json"
    rc = gen.main(["--decision-token", "HUMAN_APPROVED_BUILD_RESEARCH_ONLY_CONTRACT",
                   "--unit-spec-file", str(spec_file), "--out-file", str(out_file),
                   "--repo-root", str(tmp_path)])
    assert rc == 0
    assert out_file.exists()
    payload = json.loads(out_file.read_text(encoding="utf-8"))
    assert isinstance(payload, list) and len(payload) == 1
    assert payload[0]["staging_command"].startswith("git add -- ")


def test_main_refused_token_writes_no_file(tmp_path, capsys):
    spec_file = tmp_path / "specs.json"
    spec_file.write_text(json.dumps([_spec()]), encoding="utf-8")
    out_file = tmp_path / "units.json"
    rc = gen.main(["--decision-token",
                   "HUMAN_DECISION_C19_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT",
                   "--unit-spec-file", str(spec_file), "--out-file", str(out_file)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert out["verdict"] == "REFUSED_STOP_FOR_HUMAN"
    assert not out_file.exists()


def test_source_has_no_git_shell_network():
    src = Path(gen.__file__).read_text(encoding="utf-8")
    for tok in ("subprocess", "import requests", "from requests", "import urllib",
                "import socket", "import ccxt", "os.environ", "getenv", "urlopen",
                "Popen", "check_output", "system("):
        assert tok not in src, tok
    # the generator never RUNS git -- it only emits an explicit `git add --` string
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            name = (node.func.attr if isinstance(node.func, ast.Attribute)
                    else getattr(node.func, "id", ""))
            assert name not in ("run", "Popen", "call", "check_output", "system")

"""Tests for the SPARTA Report Artifact & Local Drift Disposition Policy (READ-ONLY).

Every input is a FAKE directory tree under tmp_path; no network, no credentials, no git
command, no subprocess, no file modification, no gate is unlocked. The policy documents
dispositions and classifications only; it changes, stages, and commits nothing."""

from __future__ import annotations

import ast
import json

import sparta_commander.report_artifact_and_drift_disposition_policy_contract as dp

_DIRS_AND_FILES = {
    "reports/crypto_d1_resume_policy_sim": [
        "resume_policy_sim_log.jsonl",
        "resume_policy_sim_report.json",
        "resume_policy_sim_report.md",
    ],
    "reports/crypto_d1_rc1_out_of_sample_replay": [
        "rc1_oos_replay_log.jsonl",
        "rc1_oos_replay_report.json",
        "rc1_oos_replay_report.md",
    ],
    "reports/crypto_d1_rc2_cross_policy_replay": [
        "rc2_cross_policy_replay_log.jsonl",
        "rc2_cross_policy_replay_report.json",
        "rc2_cross_policy_replay_report.md",
    ],
}

_DRIFT_PATHS = {
    "app.py",
    "templates/jarvis.html",
    "spartacus/animation_engine.py",
    "jarvis_conversation_safety.py",
    "jarvis_knowledge_map.py",
    "tests/test_jarvis_ask_contract.py",
    "brain_memory/projects/trading_bot/decisions.md",
    "brain_memory/projects/trading_bot/lessons.md",
    "brain_memory/projects/trading_bot/next_actions.md",
}


def _stage_reports(tmp_path, *, skip_dir=None, skip_file=None):
    for rel, files in _DIRS_AND_FILES.items():
        if rel == skip_dir:
            continue
        d = tmp_path
        for part in rel.split("/"):
            d = d / part
        d.mkdir(parents=True, exist_ok=True)
        for f in files:
            if skip_file and rel + "/" + f == skip_file:
                continue
            (d / f).write_text(json.dumps({"fake": True}), encoding="utf-8")


# --------------------------------------------------------------------------- #
# ready policy: all artifacts present
# --------------------------------------------------------------------------- #
def test_policy_ready_when_all_artifacts_present(tmp_path):
    _stage_reports(tmp_path)
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    assert p["verdict"] == dp.VERDICT_POLICY_READY
    assert p["blockers"] == []
    assert p["any_file_changed_by_this_contract"] is False
    for st in p["report_dir_status"]:
        assert st["directory_present"] is True
        assert st["missing_files"] == []


def test_all_three_dirs_recommended_as_immutable_evidence(tmp_path):
    _stage_reports(tmp_path)
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    assert len(p["report_dir_policies"]) == 3
    assert {d["path"] for d in p["report_dir_policies"]} == set(_DIRS_AND_FILES)
    for d in p["report_dir_policies"]:
        assert d["recommended_disposition"] == (
            "COMMIT_AS_IMMUTABLE_EVIDENCE_VIA_SEPARATE_APPROVAL"
        )
        assert d["rationale"]
        assert d["cited_by"]


def test_headline_answers_are_explicit(tmp_path):
    _stage_reports(tmp_path)
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    assert p["future_commit_may_include_report_artifacts"] is True
    assert p["report_artifacts_only_via_separate_evidence_commit"] is True
    assert p["cleanup_must_be_separate_future_decision"] is True
    assert p["next_required_action"] == "HUMAN_APPROVED_EVIDENCE_COMMIT_OR_NEW_DIRECTIVE"
    assert "drift_files_classified_not_cleaned_or_staged" in p["risk_notes"]
    assert (
        "report_artifacts_must_never_be_bundled_into_code_or_feature_commits"
        in p["risk_notes"]
    )


# --------------------------------------------------------------------------- #
# drift classifications: all nine, classified but untouched
# --------------------------------------------------------------------------- #
def test_all_nine_drift_files_classified():
    classifications = dp.drift_file_classifications()
    assert {c["path"] for c in classifications} == _DRIFT_PATHS
    for c in classifications:
        assert c["classification"]
        assert c["recommended_handling"]
        assert c["evidence"]


def test_drift_classes_match_investigation():
    by_path = {c["path"]: c for c in dp.drift_file_classifications()}
    for p in ("brain_memory/projects/trading_bot/decisions.md",
              "brain_memory/projects/trading_bot/lessons.md",
              "brain_memory/projects/trading_bot/next_actions.md"):
        assert by_path[p]["classification"] == "auto_pytest_marker_hook_appends"
    for p in ("app.py", "templates/jarvis.html", "spartacus/animation_engine.py"):
        assert by_path[p]["classification"] == (
            "pre_existing_session_start_drift_unreviewed"
        )
    for p in ("jarvis_conversation_safety.py", "jarvis_knowledge_map.py",
              "tests/test_jarvis_ask_contract.py"):
        assert by_path[p]["classification"] == (
            "concurrent_local_development_unattributed_to_this_session"
        )


# --------------------------------------------------------------------------- #
# missing artifacts block the policy honestly
# --------------------------------------------------------------------------- #
def test_missing_directory_blocks(tmp_path):
    _stage_reports(tmp_path, skip_dir="reports/crypto_d1_rc1_out_of_sample_replay")
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    assert p["verdict"] == dp.VERDICT_POLICY_BLOCKED
    assert any(
        b == "report_directory_missing:reports/crypto_d1_rc1_out_of_sample_replay"
        for b in p["blockers"]
    )


def test_missing_file_blocks(tmp_path):
    _stage_reports(
        tmp_path,
        skip_file="reports/crypto_d1_rc2_cross_policy_replay/rc2_cross_policy_replay_report.json",
    )
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    assert p["verdict"] == dp.VERDICT_POLICY_BLOCKED
    assert any(b.startswith("report_files_missing:") for b in p["blockers"])


def test_empty_repo_blocks_everything(tmp_path):
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    assert p["verdict"] == dp.VERDICT_POLICY_BLOCKED
    assert len([b for b in p["blockers"] if b.startswith("report_directory_missing:")]) == 3


# --------------------------------------------------------------------------- #
# the evidence-commit path is inert
# --------------------------------------------------------------------------- #
def test_evidence_commit_path_is_inert():
    ecp = dp.evidence_commit_path()
    assert ecp["is_authorization"] is False
    assert ecp["performed_by_this_contract"] is False
    assert ecp["requires_separate_human_approval"] is True
    assert any("never code" in r for r in ecp["rules"])
    assert any("immutable" in r for r in ecp["rules"])
    # mutating the returned copy must not affect the module constant
    ecp["rules"].append("tampered")
    assert "tampered" not in dp.EVIDENCE_COMMIT_PATH["rules"]


def test_accessors_return_copies():
    a = dp.report_dir_policies()
    a[0]["recommended_disposition"] = "tampered"
    assert dp.report_dir_policies()[0]["recommended_disposition"] != "tampered"
    c = dp.drift_file_classifications()
    c[0]["classification"] = "tampered"
    assert dp.drift_file_classifications()[0]["classification"] != "tampered"


# --------------------------------------------------------------------------- #
# the build is read-only: it must not create or change anything on disk
# --------------------------------------------------------------------------- #
def test_build_changes_nothing_on_disk(tmp_path):
    _stage_reports(tmp_path)
    before = sorted(str(f) for f in tmp_path.rglob("*"))
    contents_before = {
        str(f): f.read_text(encoding="utf-8") for f in tmp_path.rglob("*") if f.is_file()
    }
    dp.build_disposition_policy(repo_root=str(tmp_path))
    after = sorted(str(f) for f in tmp_path.rglob("*"))
    contents_after = {
        str(f): f.read_text(encoding="utf-8") for f in tmp_path.rglob("*") if f.is_file()
    }
    assert before == after
    assert contents_before == contents_after


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_blocked(tmp_path):
    _stage_reports(tmp_path)
    ready = dp.build_disposition_policy(repo_root=str(tmp_path))
    blocked = dp.build_disposition_policy(repo_root=str(tmp_path / "missing"))
    assert dp.validate_disposition_policy(ready)["valid"] is True
    assert dp.validate_disposition_policy(blocked)["valid"] is True


def test_validate_rejects_bad_disposition(tmp_path):
    _stage_reports(tmp_path)
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    p["report_dir_policies"][0]["recommended_disposition"] = "DELETE_EVERYTHING"
    v = dp.validate_disposition_policy(p)
    assert v["valid"] is False
    assert any(e.startswith("bad_disposition:") for e in v["errors"])


def test_validate_rejects_missing_drift_classification(tmp_path):
    _stage_reports(tmp_path)
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    p["drift_file_classifications"] = p["drift_file_classifications"][:5]
    v = dp.validate_disposition_policy(p)
    assert v["valid"] is False
    assert "drift_classifications_not_nine" in v["errors"]


def test_validate_rejects_authorizing_evidence_commit(tmp_path):
    _stage_reports(tmp_path)
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    p["evidence_commit_path"]["is_authorization"] = True
    v = dp.validate_disposition_policy(p)
    assert v["valid"] is False
    assert any("evidence_commit_path_claims_authorization" in e for e in v["errors"])


def test_validate_rejects_dropped_separation_invariants(tmp_path):
    _stage_reports(tmp_path)
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    p["report_artifacts_only_via_separate_evidence_commit"] = False
    v = dp.validate_disposition_policy(p)
    assert v["valid"] is False
    assert any("evidence_commit_separation_dropped" in e for e in v["errors"])


def test_validate_rejects_claimed_file_changes(tmp_path):
    _stage_reports(tmp_path)
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    p["any_file_changed_by_this_contract"] = True
    v = dp.validate_disposition_policy(p)
    assert v["valid"] is False
    assert any("contract_claims_to_have_changed_files" in e for e in v["errors"])


def test_validate_rejects_unlocked_gate(tmp_path):
    _stage_reports(tmp_path)
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    p["micro_live_gate_locked"] = False
    v = dp.validate_disposition_policy(p)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_capability_true(tmp_path):
    _stage_reports(tmp_path)
    p = dp.build_disposition_policy(repo_root=str(tmp_path))
    p["stages_or_commits_anything"] = True
    v = dp.validate_disposition_policy(p)
    assert v["valid"] is False
    assert any(
        "capability_not_false:stages_or_commits_anything" in e for e in v["errors"]
    )


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string(tmp_path):
    _stage_reports(tmp_path)
    md = dp.render_disposition_policy_markdown(
        dp.build_disposition_policy(repo_root=str(tmp_path))
    )
    assert md.startswith("# SPARTA Report Artifact & Local Drift Disposition Policy")
    assert "COMMIT_AS_IMMUTABLE_EVIDENCE_VIA_SEPARATE_APPROVAL" in md
    assert "classified, NOT changed" in md
    assert "authorizes nothing" in md
    assert "LOCKED" in md


# --------------------------------------------------------------------------- #
# label / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_label():
    assert dp.get_disposition_policy_label() == dp.DISPOSITION_LABEL
    assert "READ-ONLY" in dp.DISPOSITION_LABEL
    assert dp.DISPOSITION_MODE == "RESEARCH_ONLY"


def test_module_imports_no_network_subprocess_or_credential_modules():
    with open(dp.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)

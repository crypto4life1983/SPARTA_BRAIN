"""Tests for the Explicit-Allowlist Commit Guard v1 policy contract.

Verifies: research-only, pure policy (not a runner), executes nothing; forbids broad
staging (git add . / -A / --all / -u / :/ / *, git commit -a/-am); requires a
declared expected-file allowlist before staging; STOPs on any staged file outside the
allowlist; STOPs on any un-exempted data/report/CSV/JSON/JSONL/log artifact (or
anything under data/); tolerates pre-existing untracked clutter without blocking a
clean explicit-path commit and never deletes/moves/modifies it; capability flags +
scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.explicit_allowlist_commit_guard_v1_contract as cg


_C = cg.build_commit_guard_contract()


def _clean_plan(**over):
    plan = {
        "staging_command": "git add sparta_commander/x_contract.py tests/test_x.py",
        "expected_files": ["sparta_commander/x_contract.py", "tests/test_x.py"],
        "staged_files": ["sparta_commander/x_contract.py", "tests/test_x.py"],
        "exemptions": [],
        "untracked_clutter_present": True,
    }
    plan.update(over)
    return plan


# ---- contract is pure policy and validates ---------------------------------

def test_contract_pure_policy_and_validates():
    assert _C["mode"] == "RESEARCH_ONLY"
    assert _C["is_pure_policy_only"] is True
    assert _C["is_runner"] is False
    assert cg.validate_commit_guard_contract(_C)["valid"] is True


def test_contract_declares_core_policy():
    assert _C["explicit_path_staging_required"] is True
    assert _C["forbids_git_add_dot"] is True
    assert _C["forbids_git_add_all"] is True
    assert _C["requires_declared_expected_files_before_staging"] is True
    assert _C["stops_if_staged_outside_allowlist"] is True
    assert _C["stops_on_unexempted_data_artifact"] is True
    assert _C["tolerates_preexisting_untracked_clutter"] is True
    assert _C["never_deletes_moves_or_modifies_clutter"] is True
    for must in ("git add .", "git add -A"):
        assert must in _C["forbidden_staging_forms"], must
    for ext in (".csv", ".json", ".jsonl", ".log"):
        assert ext in _C["data_artifact_extensions"], ext
    assert "data/" in _C["data_artifact_path_prefixes"]


# ---- approve only a clean explicit-path artifact-free plan -----------------

def test_approve_clean_explicit_plan():
    d = cg.evaluate_staging_plan(_clean_plan())
    assert d["verdict"] == "APPROVE_STAGING"
    assert d["approve_staging"] is True
    assert d["reasons"] == []
    assert d["executes_nothing"] is True


def test_untracked_clutter_does_not_block():
    # the plan stages only two source files; the repo has thousands of untracked
    # clutter files -- that must NOT block a clean explicit-path commit.
    d = cg.evaluate_staging_plan(_clean_plan(untracked_clutter_present=True))
    assert d["verdict"] == "APPROVE_STAGING"
    assert d["untracked_clutter_tolerated"] is True


# ---- forbid broad staging ---------------------------------------------------

def test_forbid_git_add_dot():
    d = cg.evaluate_staging_plan(_clean_plan(staging_command="git add ."))
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "broad_staging_forbidden" in d["reasons"]
    assert d["broad_staging_detected"] is True


def test_forbid_git_add_dash_capital_a():
    d = cg.evaluate_staging_plan(_clean_plan(staging_command="git add -A"))
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "broad_staging_forbidden" in d["reasons"]


def test_forbid_git_add_all_and_update_and_pathspec():
    for cmd in ("git add --all", "git add -u", "git add :/", "git add *"):
        d = cg.evaluate_staging_plan(_clean_plan(staging_command=cmd))
        assert d["verdict"] == "STOP_FOR_HUMAN", cmd
        assert d["broad_staging_detected"] is True, cmd


def test_forbid_git_commit_dash_a():
    for cmd in ("git commit -a -m msg", "git commit -am msg"):
        d = cg.evaluate_staging_plan(_clean_plan(staging_command=cmd))
        assert d["verdict"] == "STOP_FOR_HUMAN", cmd


def test_explicit_multi_path_add_is_allowed():
    assert cg.is_broad_staging_command(
        "git add a/b.py c/d.py tests/e.py") is False
    assert cg.is_broad_staging_command("git add .") is True
    assert cg.is_broad_staging_command("git add -A") is True


# ---- require a declared allowlist ------------------------------------------

def test_stop_when_no_expected_files_declared():
    d = cg.evaluate_staging_plan(_clean_plan(expected_files=[]))
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "no_expected_files_declared" in d["reasons"]


# ---- stop if staged outside allowlist --------------------------------------

def test_stop_on_file_outside_allowlist():
    plan = _clean_plan(
        staged_files=["sparta_commander/x_contract.py", "tests/test_x.py",
                      "sparta_commander/sneaky_extra.py"])
    d = cg.evaluate_staging_plan(plan)
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert any("staged_file_outside_allowlist" in r for r in d["reasons"])
    assert "sparta_commander/sneaky_extra.py" in d["staged_files_outside_allowlist"]


# ---- stop on un-exempted data / report / artifact files --------------------

def test_stop_on_data_dir_artifact():
    plan = _clean_plan(
        expected_files=["sparta_commander/x_contract.py", "data/labels.csv"],
        staged_files=["sparta_commander/x_contract.py", "data/labels.csv"])
    d = cg.evaluate_staging_plan(plan)
    assert d["verdict"] == "STOP_FOR_HUMAN"
    assert "data/labels.csv" in d["artifacts_blocked"]


def test_stop_on_json_jsonl_log_report_artifacts():
    for art in ("reports/run.md", "x/result.json", "x/events.jsonl",
                "x/run.log", "data/anything.bin".replace(".bin", ".csv")):
        plan = _clean_plan(
            expected_files=["sparta_commander/x_contract.py", art],
            staged_files=["sparta_commander/x_contract.py", art])
        d = cg.evaluate_staging_plan(plan)
        assert d["verdict"] == "STOP_FOR_HUMAN", art
        assert art in d["artifacts_blocked"], art


def test_artifact_allowed_only_with_reviewed_contract_exemption():
    plan = _clean_plan(
        expected_files=["sparta_commander/x_contract.py", "data/frozen_pin.json"],
        staged_files=["sparta_commander/x_contract.py", "data/frozen_pin.json"],
        exemptions=[{"path": "data/frozen_pin.json",
                     "reviewed_contract": "x_data_readiness_contract"}])
    d = cg.evaluate_staging_plan(plan)
    assert d["verdict"] == "APPROVE_STAGING"
    assert d["artifacts_blocked"] == []


def test_exemption_without_reviewed_contract_is_rejected():
    plan = _clean_plan(
        expected_files=["sparta_commander/x_contract.py", "data/frozen_pin.json"],
        staged_files=["sparta_commander/x_contract.py", "data/frozen_pin.json"],
        exemptions=[{"path": "data/frozen_pin.json"}])
    d = cg.evaluate_staging_plan(plan)
    assert d["verdict"] == "STOP_FOR_HUMAN"


# ---- artifact path classification ------------------------------------------

def test_is_artifact_path():
    assert cg.is_artifact_path("data/x.csv") is True
    assert cg.is_artifact_path("reports/x.md") is True
    assert cg.is_artifact_path("x/y.json") is True
    assert cg.is_artifact_path("x/y.jsonl") is True
    assert cg.is_artifact_path("x/y.log") is True
    assert cg.is_artifact_path("sparta_commander/x_contract.py") is False
    assert cg.is_artifact_path("tests/test_x.py") is False
    assert cg.is_artifact_path("docs/notes.md") is False


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in cg._CAPABILITY_FLAGS_FALSE:
        assert _C[flag] is False, flag
        bad = {**_C, flag: True}
        assert cg.validate_commit_guard_contract(bad)["valid"] is False, flag


def test_scope_locks_all_true_and_clutter_safe():
    for key, val in _C["scope_locks"].items():
        assert val is True, key
    for must in ("no_broad_staging", "no_git_add_dot", "no_git_add_all",
                 "no_unexempted_data_artifact", "no_clutter_deletion",
                 "no_clutter_move", "no_clutter_stash", "no_clutter_modification"):
        assert _C["scope_locks"][must] is True, must


def test_validator_rejects_policy_tamper():
    for k in ("forbids_git_add_dot", "stops_on_unexempted_data_artifact",
              "tolerates_preexisting_untracked_clutter",
              "never_deletes_moves_or_modifies_clutter"):
        bad = {**_C, k: False}
        assert cg.validate_commit_guard_contract(bad)["valid"] is False, k


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(cg.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    for call in ast.walk(tree):
        if isinstance(call, ast.Call):
            name = (call.func.attr if isinstance(call.func, ast.Attribute)
                    else getattr(call.func, "id", ""))
            assert name not in ("open", "exec", "eval", "compile"), name

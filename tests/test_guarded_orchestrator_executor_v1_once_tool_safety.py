"""Safety tests for the one-off Guarded Executor tool
(tools/guarded_orchestrator_executor_v1_once.py).

These tests NEVER mutate the real repository: every side effect goes through an
injected FAKE command_runner and an explicit temp `repo_root` (pytest tmp_path). The
real subprocess runner is never used; one test even monkeypatches it to raise if
invoked, proving the tool only ever touches the injected runner.

Verified gates: disabled by default; requires explicit human authorization +
EXECUTION_TOKEN + an Executor v1 AUTHORIZED_TO_EXECUTE decision + explicit allowlist +
clean tracked tree + HEAD==origin/master + tests passing before staging; executes only
the bounded phases; refuses the full human-stop set, broad staging, unexpected files,
data/report artifacts, dirty tree, SHA drift, and failing/un-run tests; tolerates
untracked clutter only under explicit-allowlist staging."""
from __future__ import annotations

import json

import sparta_commander.guarded_orchestrator_executor_v1_contract as goe
import tools.guarded_orchestrator_executor_v1_once as tool


def _ok(stdout="", rc=0, stderr=""):
    return {"returncode": rc, "stdout": stdout, "stderr": stderr}


class FakeRunner:
    """Records every (cmd, cwd) and returns canned git/pytest results. Executes
    nothing real."""

    def __init__(self, *, head="h0", origin="h0", status_lines=None, pytest_rc=0,
                 add_rc=0, commit_rc=0, push_rc=0, head_after="h1"):
        self.head = head
        self.origin = origin
        self.status = "\n".join(status_lines if status_lines is not None
                                else ["?? sparta_commander/x_contract.py",
                                      "?? tests/test_x.py",
                                      "?? data/unrelated_clutter.json"])
        self.pytest_rc = pytest_rc
        self.add_rc = add_rc
        self.commit_rc = commit_rc
        self.push_rc = push_rc
        self.head_after = head_after
        self.calls: list = []
        self.committed = False
        self.pushed = False

    def __call__(self, cmd, cwd):
        self.calls.append((list(cmd), cwd))
        if cmd[:3] == ["git", "rev-parse", "HEAD"]:
            return _ok(self.head_after if self.committed else self.head)
        if cmd[:3] == ["git", "rev-parse", "origin/master"]:
            return _ok(self.head_after if self.pushed else self.origin)
        if cmd[:3] == ["git", "status", "--porcelain"]:
            return _ok(self.status)
        if cmd[:3] == ["python", "-m", "pytest"]:
            return _ok("", self.pytest_rc)
        if cmd[:2] == ["git", "add"]:
            return _ok("", self.add_rc)
        if cmd[:2] == ["git", "commit"]:
            self.committed = True
            return _ok("", self.commit_rc)
        if cmd[:2] == ["git", "push"]:
            self.pushed = True
            return _ok("pushed", self.push_rc)
        if cmd[:2] == ["git", "rev-list"]:
            return _ok("0\t0")
        return _ok("", 0)

    def ran(self, *prefix):
        return any(c[:len(prefix)] == list(prefix) for c, _ in self.calls)


def _plan(**over):
    p = {
        "category": "research_only_contract_or_test",
        "description": "build a pure contract + test",
        "expected_files": ["sparta_commander/x_contract.py", "tests/test_x.py"],
        "relevant_tests": ["tests/test_x.py"],
        "staging_command": "git add sparta_commander/x_contract.py tests/test_x.py",
        "commit_message_ref": "C:/tmp/x_msg.txt",
        "exemptions": [],
    }
    p.update(over)
    return p


def _run(plan_spec, fake, tmp_path, **kw):
    kw.setdefault("repo_root", str(tmp_path))
    return tool.execute_bounded_plan(plan_spec, command_runner=fake, **kw)


# ---- disabled by default ----------------------------------------------------

def test_disabled_by_default_does_nothing(tmp_path):
    fake = FakeRunner()
    r = _run(_plan(), fake, tmp_path)  # enabled defaults to False
    assert tool.ENABLED_BY_DEFAULT is False
    assert r["outcome"] == "DISABLED_NO_OP"
    assert r["refusal_reasons"] == ["tool_disabled_by_default"]
    assert fake.calls == []                     # not a single command issued
    assert r["executed_side_effects"] is False


def test_not_a_scheduler_no_overnight(tmp_path):
    assert tool.IS_SCHEDULER is False
    assert tool.RUNS_OVERNIGHT is False


# ---- the only path to real execution ---------------------------------------

def test_authorized_execution_runs_bounded_phases_in_order(tmp_path):
    fake = FakeRunner()
    r = _run(_plan(), fake, tmp_path, enabled=True, human_authorized=True,
             execution_token=goe.EXECUTION_TOKEN)
    assert r["outcome"] == "EXECUTED"
    assert r["phases_performed"] == [
        "safety_precheck", "run_declared_tests",
        "explicit_path_git_add_allowlist_only", "git_commit_declared_message",
        "git_push_origin_master", "post_push_verification", "final_report"]
    assert r["commit_hash"] == "h1"
    assert r["head_equals_origin_master"] is True
    # the git add was explicit per-path for the allowlist only
    add_calls = [c for c, _ in fake.calls if c[:2] == ["git", "add"]]
    assert add_calls == [["git", "add", "--",
                          "sparta_commander/x_contract.py", "tests/test_x.py"]]
    assert fake.ran("git", "commit", "-F")
    assert fake.ran("git", "push", "origin", "master")


def test_requires_enable_token_and_human_auth(tmp_path):
    # enabled but no token -> dry run, no side effects
    f1 = FakeRunner()
    r1 = _run(_plan(), f1, tmp_path, enabled=True, human_authorized=True,
              execution_token=None)
    assert r1["outcome"] == "DRY_RUN_PLAN_ONLY"
    assert not f1.ran("git", "add")
    assert not f1.ran("git", "commit")
    # enabled + token but no human auth -> dry run
    f2 = FakeRunner()
    r2 = _run(_plan(), f2, tmp_path, enabled=True, human_authorized=False,
              execution_token=goe.EXECUTION_TOKEN)
    assert r2["outcome"] == "DRY_RUN_PLAN_ONLY"
    assert not f2.ran("git", "commit")
    # wrong token -> dry run
    f3 = FakeRunner()
    r3 = _run(_plan(), f3, tmp_path, enabled=True, human_authorized=True,
              execution_token="WRONG")
    assert r3["outcome"] == "DRY_RUN_PLAN_ONLY"
    assert not f3.ran("git", "push")


# ---- refuse every human-stop category --------------------------------------

def test_refuse_every_human_stop_category(tmp_path):
    import sparta_commander.autopilot_research_orchestrator_v2_contract as aro2
    for cat in aro2.HUMAN_STOP_CATEGORIES:
        fake = FakeRunner()
        r = _run(_plan(category=cat), fake, tmp_path, enabled=True,
                 human_authorized=True, execution_token=goe.EXECUTION_TOKEN)
        assert r["outcome"] == "REFUSED_STOP_FOR_HUMAN", cat
        # structural refusal happens BEFORE any precheck/test/stage command
        assert fake.calls == [], cat
        assert r["executed_side_effects"] is False, cat


def test_refuse_new_candidate_and_trading_and_fetch(tmp_path):
    for cat in ("start_new_candidate_c_number", "advance_vs_reject_decision",
                "network_fetch_execution", "labels_to_replay_advance",
                "replay_result_decision", "optimization_tuning_or_rescue_variant",
                "add_new_instrument_class",
                "paper_live_broker_order_or_trading_code",
                "scheduler_change_beyond_research_only_reporting",
                "credentials_env_secrets_account_api_or_private_broker_endpoint"):
        fake = FakeRunner()
        r = _run(_plan(category=cat), fake, tmp_path, enabled=True,
                 human_authorized=True, execution_token=goe.EXECUTION_TOKEN)
        assert r["outcome"] == "REFUSED_STOP_FOR_HUMAN", cat


# ---- refuse staging + state hazards ----------------------------------------

def test_refuse_broad_staging(tmp_path):
    fake = FakeRunner()
    r = _run(_plan(staging_command="git add ."), fake, tmp_path, enabled=True,
             human_authorized=True, execution_token=goe.EXECUTION_TOKEN)
    assert r["outcome"] == "REFUSED_STOP_FOR_HUMAN"
    assert fake.calls == []          # refused structurally, before any command
    assert not fake.ran("git", "add")


def test_refuse_data_or_report_artifact(tmp_path):
    for art in ("data/labels.csv", "reports/run.md", "x/result.json"):
        fake = FakeRunner()
        plan = _plan(expected_files=["sparta_commander/x_contract.py", art],
                     staging_command="git add sparta_commander/x_contract.py %s"
                     % art)
        r = _run(plan, fake, tmp_path, enabled=True, human_authorized=True,
                 execution_token=goe.EXECUTION_TOKEN)
        assert r["outcome"] == "REFUSED_STOP_FOR_HUMAN", art
        assert not fake.ran("git", "commit"), art


def test_refuse_dirty_tracked_tree(tmp_path):
    # an UNEXPECTED tracked modification present -> dirty tracked tree
    fake = FakeRunner(status_lines=[" M sparta_commander/UNEXPECTED.py",
                                    "?? sparta_commander/x_contract.py",
                                    "?? tests/test_x.py"])
    r = _run(_plan(), fake, tmp_path, enabled=True, human_authorized=True,
             execution_token=goe.EXECUTION_TOKEN)
    assert r["outcome"] == "REFUSED_STOP_FOR_HUMAN"
    assert "dirty_tracked_tree" in r["refusal_reasons"]
    assert not fake.ran("git", "add")
    assert not fake.ran("git", "commit")


def test_refuse_sha_drift(tmp_path):
    fake = FakeRunner(head="hLOCAL", origin="hREMOTE")
    r = _run(_plan(), fake, tmp_path, enabled=True, human_authorized=True,
             execution_token=goe.EXECUTION_TOKEN)
    assert r["outcome"] == "REFUSED_STOP_FOR_HUMAN"
    assert "sha_drift_head_not_origin_master" in r["refusal_reasons"]
    assert not fake.ran("git", "commit")


def test_refuse_failing_tests_before_staging(tmp_path):
    fake = FakeRunner(pytest_rc=1)
    r = _run(_plan(), fake, tmp_path, enabled=True, human_authorized=True,
             execution_token=goe.EXECUTION_TOKEN)
    assert r["outcome"] == "REFUSED_STOP_FOR_HUMAN"
    assert "failing_or_unrun_tests" in r["refusal_reasons"]
    # tests ran, but NO staging/commit/push happened
    assert fake.ran("python", "-m", "pytest")
    assert not fake.ran("git", "add")
    assert not fake.ran("git", "commit")
    assert not fake.ran("git", "push")


# ---- clutter tolerated only under explicit-allowlist staging ---------------

def test_untracked_clutter_tolerated_under_explicit_staging(tmp_path):
    fake = FakeRunner(status_lines=["?? sparta_commander/x_contract.py",
                                    "?? tests/test_x.py",
                                    "?? data/big_clutter.csv",
                                    "?? reports/old_report.md"])
    r = _run(_plan(), fake, tmp_path, enabled=True, human_authorized=True,
             execution_token=goe.EXECUTION_TOKEN)
    assert r["outcome"] == "EXECUTED"      # clutter present but staging is explicit


def test_clutter_not_a_shield_for_broad_staging(tmp_path):
    fake = FakeRunner()
    r = _run(_plan(staging_command="git add -A"), fake, tmp_path, enabled=True,
             human_authorized=True, execution_token=goe.EXECUTION_TOKEN)
    assert r["outcome"] == "REFUSED_STOP_FOR_HUMAN"


# ---- proof: never touches the real repo ------------------------------------

def test_all_commands_scoped_to_injected_temp_repo(tmp_path):
    fake = FakeRunner()
    _run(_plan(), fake, tmp_path, enabled=True, human_authorized=True,
         execution_token=goe.EXECUTION_TOKEN)
    assert fake.calls, "expected the fake runner to receive commands"
    for _cmd, cwd in fake.calls:
        assert cwd == str(tmp_path)        # never the real repo cwd


def test_real_subprocess_runner_is_never_invoked(monkeypatch, tmp_path):
    def _boom(*a, **k):
        raise AssertionError("real command runner must not be called in tests")
    monkeypatch.setattr(tool, "_real_command_runner", _boom)
    fake = FakeRunner()
    r = _run(_plan(), fake, tmp_path, enabled=True, human_authorized=True,
             execution_token=goe.EXECUTION_TOKEN)
    assert r["outcome"] == "EXECUTED"      # ran entirely through the fake


def test_main_disabled_by_default_is_a_noop(tmp_path, capsys, monkeypatch):
    # main() with the REAL runner but WITHOUT --enable must be a no-op (DISABLED),
    # so it cannot mutate anything. Guard the real runner to be safe anyway.
    monkeypatch.setattr(tool, "_real_command_runner",
                        lambda *a, **k: (_ for _ in ()).throw(
                            AssertionError("real runner called from disabled main")))
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps(_plan()), encoding="utf-8")
    rc = tool.main(["--plan-file", str(plan_file), "--repo-root", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["outcome"] == "DISABLED_NO_OP"
    assert out["executed_side_effects"] is False


# ---- the tool exposes its disabled-by-default safety posture ---------------

def test_tool_exposes_disabled_default_and_contract_pairing():
    assert tool.ENABLED_BY_DEFAULT is False
    # the contract it is gated by certifies it is disabled-by-default
    c = goe.build_executor_contract()
    assert c["real_runner_shipped"] is False
    assert c["tool_runner_disabled_by_default"] is True

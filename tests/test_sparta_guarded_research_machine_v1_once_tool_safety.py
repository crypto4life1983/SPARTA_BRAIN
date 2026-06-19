"""Safety tests for the run-once Guarded Research Machine
(tools/sparta_guarded_research_machine_v1_once.py).

These tests NEVER mutate the real repository: every side effect goes through an
injected FAKE command_runner (driving the REAL executor tool) and an explicit temp
`repo_root` (pytest tmp_path). The real subprocess runner is never used; one test
monkeypatches it to raise if invoked.

Verified: disabled by default; requires --enable + human authorization + a decision
token; loops declared safe bounded units through the guarded executor, recording
commits/pushes/tests; respects the step budget; and HARD STOPS at the next human gate
(human-stop category, or plan exhausted) and on every guard refusal (broad staging,
unexpected files, data artifacts, dirty tree, SHA drift, failing tests)."""
from __future__ import annotations

import json

import sparta_commander.guarded_orchestrator_executor_v1_contract as goe
import tools.sparta_guarded_research_machine_v1_once as machine


def _ok(stdout="", rc=0, stderr=""):
    return {"returncode": rc, "stdout": stdout, "stderr": stderr}


class FakeRunner:
    """Records every (cmd, cwd) and returns canned git/pytest results. Executes
    nothing real. HEAD/origin advance together on commit+push (in sync) unless
    `drift` or a dirty `status` is configured."""

    def __init__(self, *, status="", pytest_rc=0, add_rc=0, commit_rc=0, push_rc=0,
                 drift=False):
        self.calls: list = []
        self.commit_count = 0
        self.status = status
        self.pytest_rc = pytest_rc
        self.add_rc = add_rc
        self.commit_rc = commit_rc
        self.push_rc = push_rc
        self.drift = drift

    def __call__(self, cmd, cwd):
        self.calls.append((list(cmd), cwd))
        head = "h%d" % self.commit_count
        if cmd[:3] == ["git", "rev-parse", "HEAD"]:
            return _ok(head)
        if cmd[:3] == ["git", "rev-parse", "origin/master"]:
            return _ok("DIFFERENT" if self.drift else head)
        if cmd[:3] == ["git", "status", "--porcelain"]:
            return _ok(self.status)
        if cmd[:3] == ["python", "-m", "pytest"]:
            return _ok("", self.pytest_rc)
        if cmd[:2] == ["git", "add"]:
            return _ok("", self.add_rc)
        if cmd[:2] == ["git", "commit"]:
            self.commit_count += 1
            return _ok("", self.commit_rc)
        if cmd[:2] == ["git", "push"]:
            return _ok("pushed", self.push_rc)
        if cmd[:2] == ["git", "rev-list"]:
            return _ok("0\t0")
        return _ok("", 0)

    def ran(self, *prefix):
        return any(c[:len(prefix)] == list(prefix) for c, _ in self.calls)


def _unit(category="research_only_contract_or_test", n=1):
    return {
        "category": category,
        "description": "build a pure contract + test",
        "expected_files": ["sparta_commander/x%d_contract.py" % n,
                            "tests/test_x%d.py" % n],
        "relevant_tests": ["tests/test_x%d.py" % n],
        "staging_command": "git add sparta_commander/x%d_contract.py tests/test_x%d.py"
                           % (n, n),
        "staged_files": ["sparta_commander/x%d_contract.py" % n,
                         "tests/test_x%d.py" % n],
        "exemptions": [],
        "commit_message_ref": "C:/tmp/x%d.txt" % n,
    }


def _run(units, fake, tmp_path, **kw):
    kw.setdefault("repo_root", str(tmp_path))
    return machine.run_machine(units, command_runner=fake, **kw)


# ---- disabled by default ----------------------------------------------------

def test_disabled_by_default_does_nothing(tmp_path):
    fake = FakeRunner()
    r = _run([_unit()], fake, tmp_path)   # enabled defaults to False
    assert machine.ENABLED_BY_DEFAULT is False
    assert r["outcome"] == "DISABLED_NO_OP"
    assert "machine_disabled_by_default" in r["refusal_reasons"]
    assert fake.calls == []
    assert r["executed_side_effects"] is False


def test_not_a_scheduler_no_overnight():
    assert machine.IS_SCHEDULER is False
    assert machine.RUNS_OVERNIGHT is False


# ---- requires human auth + decision token ----------------------------------

def test_requires_human_authorization(tmp_path):
    fake = FakeRunner()
    r = _run([_unit()], fake, tmp_path, enabled=True, human_authorized=False,
             decision_token="TOK")
    assert r["outcome"] == "REFUSED_STOP_FOR_HUMAN"
    assert "missing_human_authorization" in r["refusal_reasons"]
    assert not fake.ran("git", "commit")


def test_requires_decision_token(tmp_path):
    fake = FakeRunner()
    r = _run([_unit()], fake, tmp_path, enabled=True, human_authorized=True,
             decision_token=None)
    assert r["outcome"] == "REFUSED_STOP_FOR_HUMAN"
    assert "missing_decision_token" in r["refusal_reasons"]
    assert not fake.ran("git", "commit")


# ---- the happy path: drive safe bounded units to the next human gate --------

def test_runs_safe_units_then_stops_at_human_gate(tmp_path):
    fake = FakeRunner()
    units = [_unit(n=1), _unit(n=2)]
    r = _run(units, fake, tmp_path, enabled=True, human_authorized=True,
             decision_token="HUMAN_APPROVED_RUN_SAFE_BOUNDED_RESEARCH",
             max_safe_steps=10)
    assert r["outcome"] == "STOPPED_AT_HUMAN_GATE"
    assert r["stopped_at_human_gate"] is True
    assert r["stopped_reason"] == "plan_exhausted_next_is_human_decision"
    assert r["steps_executed"] == 2
    assert len(r["commits"]) == 2
    assert len(r["pushes"]) == 2
    assert r["commits"] == ["h1", "h2"]
    # the explicit per-path git add ran for each unit
    add_calls = [c for c, _ in fake.calls if c[:2] == ["git", "add"]]
    assert len(add_calls) == 2
    assert all(c[2] == "--" for c in add_calls)   # explicit per-path form
    # the next human token is surfaced from the lane
    assert r["next_human"]["next_human_token"]
    assert r["next_human"]["opening_new_candidate_requires_explicit_token"] is True


# ---- hard stop: human-stop category unit -----------------------------------

def test_stops_at_human_stop_category_without_executing(tmp_path):
    fake = FakeRunner()
    units = [_unit(category="start_new_candidate_c_number")]
    r = _run(units, fake, tmp_path, enabled=True, human_authorized=True,
             decision_token="TOK")
    assert r["outcome"] == "STOPPED_AT_HUMAN_GATE"
    assert r["stopped_at_human_gate"] is True
    assert "human_stop_category" in r["stopped_reason"]
    assert fake.calls == []           # stopped before any git command
    assert r["steps_executed"] == 0


def test_stops_at_each_human_stop_category(tmp_path):
    for cat in ("start_new_candidate_c_number", "advance_vs_reject_decision",
                "network_fetch_execution", "labels_to_replay_advance",
                "replay_result_decision", "optimization_tuning_or_rescue_variant",
                "add_new_instrument_class",
                "paper_live_broker_order_or_trading_code",
                "scheduler_change_beyond_research_only_reporting",
                "credentials_env_secrets_account_api_or_private_broker_endpoint"):
        fake = FakeRunner()
        r = _run([_unit(category=cat)], fake, tmp_path, enabled=True,
                 human_authorized=True, decision_token="TOK")
        assert r["outcome"] == "STOPPED_AT_HUMAN_GATE", cat
        assert r["steps_executed"] == 0, cat


# ---- hard stops on guard conditions ----------------------------------------

def test_stops_on_dirty_tracked_tree(tmp_path):
    fake = FakeRunner(status=" M sparta_commander/UNEXPECTED.py")
    r = _run([_unit()], fake, tmp_path, enabled=True, human_authorized=True,
             decision_token="TOK")
    assert r["outcome"] == "STOPPED_ON_GUARD_REFUSAL"
    assert r["stopped_reason"] == "dirty_tracked_tree"
    assert not fake.ran("git", "commit")


def test_stops_on_sha_drift(tmp_path):
    fake = FakeRunner(drift=True)
    r = _run([_unit()], fake, tmp_path, enabled=True, human_authorized=True,
             decision_token="TOK")
    assert r["outcome"] == "STOPPED_ON_GUARD_REFUSAL"
    assert r["stopped_reason"] == "sha_drift_head_not_origin_master"
    assert not fake.ran("git", "commit")


def test_stops_on_broad_staging_unit(tmp_path):
    fake = FakeRunner()
    unit = _unit()
    unit["staging_command"] = "git add ."
    r = _run([unit], fake, tmp_path, enabled=True, human_authorized=True,
             decision_token="TOK")
    assert r["outcome"] == "STOPPED_ON_GUARD_REFUSAL"
    assert not fake.ran("git", "commit")


def test_stops_on_data_artifact_unit(tmp_path):
    fake = FakeRunner()
    unit = _unit()
    unit["expected_files"] = ["sparta_commander/x_contract.py", "data/labels.csv"]
    unit["staged_files"] = unit["expected_files"]
    r = _run([unit], fake, tmp_path, enabled=True, human_authorized=True,
             decision_token="TOK")
    assert r["outcome"] == "STOPPED_ON_GUARD_REFUSAL"
    assert not fake.ran("git", "commit")


def test_stops_on_failing_tests(tmp_path):
    fake = FakeRunner(pytest_rc=1)
    r = _run([_unit()], fake, tmp_path, enabled=True, human_authorized=True,
             decision_token="TOK")
    assert r["outcome"] == "STOPPED_ON_GUARD_REFUSAL"
    assert not fake.ran("git", "commit")


# ---- step budget ------------------------------------------------------------

def test_respects_max_safe_steps(tmp_path):
    fake = FakeRunner()
    units = [_unit(n=1), _unit(n=2), _unit(n=3)]
    r = _run(units, fake, tmp_path, enabled=True, human_authorized=True,
             decision_token="TOK", max_safe_steps=1)
    assert r["outcome"] == "STEP_BUDGET_REACHED"
    assert r["steps_executed"] == 1
    assert len(r["commits"]) == 1


def test_no_units_stops_at_human_gate(tmp_path):
    fake = FakeRunner()
    r = _run([], fake, tmp_path, enabled=True, human_authorized=True,
             decision_token="TOK")
    assert r["outcome"] == "STOPPED_AT_HUMAN_GATE"
    assert r["stopped_reason"] == "no_safe_bounded_unit_declared"
    assert fake.calls == []


# ---- proof: never touches the real repo ------------------------------------

def test_all_commands_scoped_to_injected_temp_repo(tmp_path):
    fake = FakeRunner()
    _run([_unit(n=1), _unit(n=2)], fake, tmp_path, enabled=True,
         human_authorized=True, decision_token="TOK")
    assert fake.calls
    for _cmd, cwd in fake.calls:
        assert cwd == str(tmp_path)


def test_real_subprocess_runner_never_invoked(monkeypatch, tmp_path):
    def _boom(*a, **k):
        raise AssertionError("real command runner must not be called in tests")
    monkeypatch.setattr(machine, "_real_command_runner", _boom)
    fake = FakeRunner()
    r = _run([_unit()], fake, tmp_path, enabled=True, human_authorized=True,
             decision_token="TOK")
    assert r["outcome"] == "STOPPED_AT_HUMAN_GATE"
    assert r["steps_executed"] == 1


def test_main_disabled_by_default_is_a_noop(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(machine, "_real_command_runner",
                        lambda *a, **k: (_ for _ in ()).throw(
                            AssertionError("real runner called from disabled main")))
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps([_unit()]), encoding="utf-8")
    rc = machine.main(["--plan-file", str(plan_file), "--repo-root", str(tmp_path)])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0
    assert out["outcome"] == "DISABLED_NO_OP"
    assert out["executed_side_effects"] is False


def test_exposes_disabled_default_and_execution_token_pairing():
    # the machine uses the executor's separate EXECUTION_TOKEN under the hood
    assert machine.ENABLED_BY_DEFAULT is False
    assert goe.EXECUTION_TOKEN == "EXECUTE_APPROVED_BOUNDED_RESEARCH_UNIT_NOW"

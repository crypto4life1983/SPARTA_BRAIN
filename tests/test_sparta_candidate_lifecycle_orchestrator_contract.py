"""Tests for the SPARTA candidate-lifecycle orchestrator (Bundle D, suggestion-only).

Proves the orchestrator maps the lane state to the correct gate + single suggested human
token (< 20 -> C22_COLLECT_MORE_WINDOWS + collect token; >= 20 -> C22_READY_FOR_FROZEN_
WINDOW_REVIEW + review token; C22 concluded -> C23_MAY_OPEN_AFTER_C22_CONCLUDED + open-C23
token), keeps C23 WAITING while C22 active, and -- critically -- never advances a candidate,
opens C23 as active, runs labels/replay, auto-executes a token, or modifies the repo."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.sparta_candidate_lifecycle_orchestrator_contract as lo
import tools.sparta_candidate_lifecycle_orchestrator_once as runner

_COLLECT = "HUMAN_STAGE_MORE_FROZEN_DAILY_TREND_RADAR_GC_WINDOWS_THEN_REREVIEW_C22_LABELS"
_REVIEW = "HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW"
_C23_OPEN = "HUMAN_DECISION_OPEN_CANDIDATE_23_AFTER_C22_CONCLUDES_OR_HOLD"

_GUARANTEE_FLAGS = ("advances_any_candidate", "opens_c23_as_active", "runs_labels",
                    "runs_replay", "auto_executes_any_token", "modifies_repo")


# ---- under 20/20: COLLECT gate + collect token, C23 waiting -----------------

def test_under_20_collect_gate():
    f = lo.build_lifecycle(collected_windows=1)
    assert f["current_gate"] == "C22_COLLECT_MORE_WINDOWS"
    assert f["c22_gate"] == "C22_COLLECT_MORE_WINDOWS"
    assert f["c23_gate"] == "C23_WAITING_FOR_C22_CONCLUSION"
    assert f["suggested_human_token"] == _COLLECT
    st = f["lifecycle_state"]
    assert st["c22_progress"] == "1/20"
    assert st["c22_state"] == "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
    assert st["c21_closed_rejected"] is True and st["rejected_ledger_count"] == 26
    assert st["c23_on_deck"] is True and st["c23_is_active"] is False
    assert lo.validate_lifecycle(f)["valid"] is True


# ---- 20/20: READY gate + review token --------------------------------------

def test_at_20_ready_gate():
    f = lo.build_lifecycle(collected_windows=20)
    assert f["current_gate"] == "C22_READY_FOR_FROZEN_WINDOW_REVIEW"
    assert f["c23_gate"] == "C23_WAITING_FOR_C22_CONCLUSION"
    assert f["suggested_human_token"] == _REVIEW
    assert f["lifecycle_state"]["c22_ready_for_review"] is True
    assert f["lifecycle_state"]["c22_progress"] == "20/20"
    assert lo.validate_lifecycle(f)["valid"] is True


# ---- C22 concluded: C23 may open + open-C23 token --------------------------

def test_c22_concluded_c23_may_open():
    f = lo.build_lifecycle(collected_windows=20, c22_concluded=True)
    assert f["current_gate"] == "C23_MAY_OPEN_AFTER_C22_CONCLUDED"
    assert f["c23_gate"] == "C23_MAY_OPEN_AFTER_C22_CONCLUDED"
    assert f["suggested_human_token"] == _C23_OPEN
    assert f["lifecycle_state"]["c22_concluded"] is True
    assert f["lifecycle_state"]["c22_active_collection_lane"] is False
    # even when C23 may open, it is NOT opened as active here
    assert f["opens_c23_as_active"] is False
    assert f["lifecycle_state"]["c23_is_active"] is False
    assert lo.validate_lifecycle(f)["valid"] is True


# ---- proof: never advances / opens / runs / executes / modifies ------------

def test_never_advances_or_executes():
    for f in (lo.build_lifecycle(collected_windows=1),
              lo.build_lifecycle(collected_windows=20),
              lo.build_lifecycle(collected_windows=20, c22_concluded=True)):
        for flag in _GUARANTEE_FLAGS:
            assert f[flag] is False, flag
        assert f["advances_nothing"] is True
        assert f["suggested_token_is_suggestion_only"] is True
        for flag in lo._CAPABILITY_FLAGS_FALSE:
            assert f[flag] is False, flag
        for key, val in f["scope_locks"].items():
            assert val is True, key


# ---- anti-tamper -----------------------------------------------------------

def test_tamper_rejected():
    f = lo.build_lifecycle(collected_windows=1)
    # collect gate but review token -> inconsistent
    assert lo.validate_lifecycle(
        {**f, "suggested_human_token": _REVIEW})["valid"] is False
    # claim it advances a candidate -> invalid
    assert lo.validate_lifecycle(
        {**f, "advances_any_candidate": True})["valid"] is False
    # open C23 as active -> invalid
    assert lo.validate_lifecycle({**f, "opens_c23_as_active": True})["valid"] is False
    # wrong gate for the state
    assert lo.validate_lifecycle(
        {**f, "current_gate": "C22_READY_FOR_FROZEN_WINDOW_REVIEW"})["valid"] is False


# ---- runner builds a valid live finding ------------------------------------

def test_runner_builds_valid_finding():
    f = runner.build_lifecycle_finding()
    assert lo.validate_lifecycle(f)["valid"] is True
    # live state: C22 active, not concluded
    assert f["lifecycle_state"]["c22_concluded"] is False
    assert f["current_gate"] in ("C22_COLLECT_MORE_WINDOWS",
                                 "C22_READY_FOR_FROZEN_WINDOW_REVIEW")
    assert f["opens_c23_as_active"] is False


# ---- runner does not advance / activate / execute --------------------------

# actionable advance/execute tokens. The bare word "advance" appears only in the runner's
# descriptive docstring ("never advances it") and is excluded.
_FORBIDDEN_RUNNER_TOKENS = (
    "build_c23_proposal", "open_c23", "run_labels", "run_replay", "c22_concluded=True",
    "git commit", "git push", "place_order", "import requests",
    "Register-ScheduledTask",
)


def test_runner_no_advance_tokens():
    src = Path(runner.__file__).read_text(encoding="utf-8")
    for tok in _FORBIDDEN_RUNNER_TOKENS:
        assert tok not in src, tok
    # runner explicitly passes c22_concluded=False
    assert "c22_concluded=False" in src


# ---- contract module purity ------------------------------------------------

def test_contract_module_purity():
    src = Path(lo.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "Popen", "urlopen", "json.load", "read_text", "glob("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned

"""Bundle 3 tests for the Strategy Factory Run-Queue Reporter v1 (read-only).

The target is loaded BY FILE PATH (not via the package) so these tests stay
runnable with zero dependency on any package __init__ / conftest, matching
the established standalone strategy-factory test pattern.

Coverage:
- mandated safety constants are pinned False,
- render_plan_text / render_plan_markdown / summarize_plan are pure and
  return strings only,
- output is deterministic (same input -> identical string twice),
- output contains every plan row's fields,
- output carries NO forbidden execution / promotion token,
- the input plan dict is never mutated,
- malformed / garbage input returns a single safe fixed string,
- an end-to-end Bundle1 -> Bundle2 -> Bundle3 pipeline renders cleanly,
- the module imports nothing network / subprocess / trading related and
  writes no file.
"""

import ast
import importlib.util
import pathlib

import pytest

_HERE = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = _HERE / "sparta_commander" / "strategy_factory_run_queue_reporter.py"
_PLANNER_PATH = (
    _HERE / "sparta_commander" / "strategy_factory_run_queue_planner.py"
)
_QUEUE_PATH = _HERE / "sparta_commander" / "strategy_factory_run_queue.py"


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load("sfrqr_under_test", _MODPATH)
PLANNER = _load("sfrqp_for_reporter_test", _PLANNER_PATH)
QUEUE = _load("sfrq_for_reporter_test", _QUEUE_PATH)


def _good_queue() -> dict:
    return {
        "schema": QUEUE.SCHEMA,
        "entries": [
            {
                "run_id": "SFR-002",
                "candidate_id": "crypto-d1",
                "phase": "data_contract_gate",
                "status": "READY_FOR_NEXT_PHASE",
                "priority": 2,
                "blockers": [],
            },
            {
                "run_id": "SFR-001",
                "candidate_id": "arb-research",
                "phase": "idea_intake",
                "status": "QUEUED",
                "priority": 1,
                "blockers": [],
            },
            {
                "run_id": "SFR-003",
                "candidate_id": "blocked-one",
                "phase": "hypothesis_spec",
                "status": "BLOCKED",
                "priority": 1,
                "blockers": ["missing operator prereg"],
            },
            {
                "run_id": "SFR-004",
                "candidate_id": "human-one",
                "phase": "offline_backtest_run",
                "status": "AWAITING_HUMAN_REVIEW",
                "priority": 1,
                "blockers": [],
            },
        ],
    }


def _good_plan() -> dict:
    return PLANNER.build_run_plan(_good_queue())


# --- safety constants -------------------------------------------------- #

def test_safety_constants_are_pinned():
    assert MOD.EXECUTES is False
    assert MOD.NETWORK is False
    assert MOD.WRITES_FILES is False
    assert MOD.MUTATES_REGISTRY is False
    assert MOD.SCHEDULER_OR_LOOP is False
    assert MOD.USES_BROKER is False
    assert MOD.USES_EXCHANGE is False
    assert MOD.INVOKES_PHASE_MODULE is False
    assert MOD.RUNS_BACKTEST is False
    assert MOD.CREATES_LIVE_QUEUE_DATA is False
    assert MOD.USES_CREDENTIALS is False
    assert MOD.READS_LOCAL_SECRETS is False
    assert MOD.FETCHES_DATA is False


def test_plan_action_enum_is_reexported_from_bundle2():
    assert MOD.PLAN_ACTION == PLANNER.PLAN_ACTION


# --- return type: strings only ---------------------------------------- #

def test_all_renderers_return_strings():
    plan = _good_plan()
    assert isinstance(MOD.render_plan_text(plan), str)
    assert isinstance(MOD.render_plan_markdown(plan), str)
    assert isinstance(MOD.summarize_plan(plan), str)


# --- determinism ------------------------------------------------------- #

def test_text_output_is_deterministic():
    plan = _good_plan()
    assert MOD.render_plan_text(plan) == MOD.render_plan_text(plan)


def test_markdown_output_is_deterministic():
    plan = _good_plan()
    assert MOD.render_plan_markdown(plan) == MOD.render_plan_markdown(plan)


def test_summary_is_deterministic():
    plan = _good_plan()
    assert MOD.summarize_plan(plan) == MOD.summarize_plan(plan)


# --- completeness: every row's fields appear -------------------------- #

def test_text_contains_every_row_field():
    plan = _good_plan()
    out = MOD.render_plan_text(plan)
    for row in plan["plan"]:
        assert str(row["run_id"]) in out
        assert str(row["candidate_id"]) in out
        assert str(row["action"]) in out
        assert str(row["current_phase"]) in out
    # a blocker reason surfaces in the report
    assert "missing operator prereg" in out


def test_markdown_contains_every_row_field():
    plan = _good_plan()
    out = MOD.render_plan_markdown(plan)
    for row in plan["plan"]:
        assert str(row["run_id"]) in out
        assert str(row["candidate_id"]) in out
        assert str(row["action"]) in out
    # markdown carries a table header
    assert "| run_id |" in out


def test_summary_counts_match_plan_summary():
    plan = _good_plan()
    s = MOD.summarize_plan(plan)
    # the one-line summary reflects the entry count
    assert f"{len(plan['plan'])} entries" in s
    # and names every closed action label
    for action in MOD.PLAN_ACTION:
        assert action in s


# --- no forbidden execution / promotion tokens ------------------------ #

def test_no_forbidden_tokens_in_output():
    plan = _good_plan()
    blob = (
        MOD.render_plan_text(plan)
        + "\n"
        + MOD.render_plan_markdown(plan)
        + "\n"
        + MOD.summarize_plan(plan)
    ).upper()
    forbidden = (
        "PASS", "PROMOTE", " GO ", "GO!", "LIVE", "APPROVE", "WIN",
        "EXECUTE", "PLACE ORDER", "BROKER", "EXCHANGE", "BACKTEST RUN",
    )
    for tok in forbidden:
        assert tok not in blob, f"forbidden token in report: {tok!r}"
    # the only 'READY' permitted is the qualified next-phase status, never a
    # bare promotion 'READY' verdict
    assert "READY_FOR_NEXT_PHASE" in blob or "READY" not in blob


# --- input plan is not mutated ---------------------------------------- #

def test_input_plan_is_not_mutated():
    plan = _good_plan()
    import copy
    before = copy.deepcopy(plan)
    MOD.render_plan_text(plan)
    MOD.render_plan_markdown(plan)
    MOD.summarize_plan(plan)
    assert plan == before


# --- malformed input returns a safe fixed string ---------------------- #

def test_malformed_input_returns_safe_fixed_string():
    for bad in (None, {}, [], 7, "nope", {"plan": "not-a-list"}, {"plan": None}):
        assert MOD.render_plan_text(bad) == MOD._EMPTY_REPORT
        assert MOD.render_plan_markdown(bad) == MOD._EMPTY_REPORT
        assert MOD.summarize_plan(bad) == MOD._EMPTY_REPORT


def test_empty_but_wellformed_plan_renders_without_error():
    empty = {"schema": MOD.SCHEMA, "plan": [], "summary": {}}
    txt = MOD.render_plan_text(empty)
    assert isinstance(txt, str)
    assert "no entries" in txt.lower()


# --- end-to-end pipeline ---------------------------------------------- #

def test_end_to_end_bundle1_2_3_pipeline():
    queue = _good_queue()
    ok, errors = QUEUE.validate_queue(queue)
    assert ok, errors
    plan = PLANNER.build_run_plan(queue)
    out = MOD.render_plan_text(plan)
    assert isinstance(out, str) and out
    # the actionable arb-research entry (priority 1, QUEUED) is described
    assert "SFR-001" in out
    assert "ADVANCE_TO_NEXT_PHASE" in out


# --- import audit: no network / subprocess / trading / file write ----- #

def test_module_imports_are_stdlib_and_inert():
    src = _MODPATH.read_text(encoding="utf-8")
    roots: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {"__future__", "importlib", "pathlib", "typing"}
    assert roots <= allowed, f"unexpected imports: {sorted(roots - allowed)}"

    forbidden = (
        "import socket", "import subprocess", "from subprocess", "urllib",
        "requests", "httpx", "http.client", "asyncio", "Popen", "os.system",
        "place_order", "submit_order", "create_order", "ccxt", "freqtrade",
        "paper_trade", "live_trade",
        # no file-write surface
        "open(", "write_text(", ".write(", "Path.write", "json.dump(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden tokens present: {hits}"

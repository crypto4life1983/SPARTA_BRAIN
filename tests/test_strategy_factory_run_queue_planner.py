"""Bundle 2 tests for the Strategy Factory Run-Queue Planner v1 (read-only).

The target is loaded BY FILE PATH (not via the package) so these tests stay
runnable with zero dependency on any package __init__ / conftest, matching
the established standalone strategy-factory test pattern.

Coverage:
- mandated safety constants are pinned False,
- the PLAN_ACTION enum is exactly the approved closed set with no execution /
  promotion language,
- build_run_plan orders by priority then run_id,
- status -> action mapping is correct (advance / hold / await / terminal),
- BLOCKED -> HOLD_BLOCKED, AWAITING_HUMAN_REVIEW -> AWAIT_HUMAN,
  terminal phase -> TERMINAL_DONE,
- the plan is mutation-safe and never mutates the source queue,
- garbage input yields a safe empty plan,
- the module imports nothing network / subprocess / trading related and
  references no strategy_factory_*phase* module.
"""

import ast
import importlib.util
import pathlib
import re

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_run_queue_planner.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("sfrqp_under_test", _MODPATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def _good_queue() -> dict:
    return {
        "schema": MOD._RQ.SCHEMA,
        "entries": [
            {
                "run_id": "SFR-002",
                "candidate_id": "crypto-d1",
                "phase": "data_contract_gate",
                "status": "READY_FOR_NEXT_PHASE",
                "priority": 2,
                "blockers": [],
                "safety_level": "research_only",
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


def _by_run_id(plan: dict) -> dict:
    return {row["run_id"]: row for row in plan["plan"]}


# --- safety constants -------------------------------------------------- #

def test_safety_constants_are_pinned():
    assert MOD.EXECUTES is False
    assert MOD.NETWORK is False
    assert MOD.MUTATES_REGISTRY is False
    assert MOD.SCHEDULER_OR_LOOP is False
    assert MOD.USES_BROKER is False
    assert MOD.USES_EXCHANGE is False
    assert MOD.WRITES_FILES is False
    assert MOD.INVOKES_PHASE_MODULE is False
    assert MOD.RUNS_BACKTEST is False
    # parity pins
    assert MOD.CREATES_LIVE_QUEUE_DATA is False
    assert MOD.USES_CREDENTIALS is False
    assert MOD.READS_LOCAL_SECRETS is False
    assert MOD.FETCHES_DATA is False


# --- closed PLAN_ACTION enum ------------------------------------------ #

def test_plan_action_enum_is_exactly_the_approved_closed_set():
    assert MOD.PLAN_ACTION == (
        "ADVANCE_TO_NEXT_PHASE",
        "HOLD_BLOCKED",
        "AWAIT_HUMAN",
        "TERMINAL_DONE",
        "NO_ACTION",
    )


def test_plan_action_enum_has_no_execution_or_promotion_language():
    bad_tokens = (
        "RUN", "EXECUTE", "PLACE", "TRADE", "ORDER", "PROMOTE", "GO",
        "LIVE", "APPROVE", "PASS", "READY", "WIN", "START", "LAUNCH",
    )
    for action in MOD.PLAN_ACTION:
        assert action not in MOD.FORBIDDEN_STATUS_VALUES
        for tok in bad_tokens:
            assert tok not in action, f"action {action!r} contains {tok!r}"


# --- priority ordering ------------------------------------------------- #

def test_build_run_plan_orders_by_priority_then_run_id():
    plan = MOD.build_run_plan(_good_queue())
    order = [row["run_id"] for row in plan["plan"]]
    # priority 1 entries first (SFR-001, SFR-003, SFR-004 by run_id), then
    # priority 2 (SFR-002).
    assert order == ["SFR-001", "SFR-003", "SFR-004", "SFR-002"]
    assert plan["entry_count"] == 4
    assert plan["schema"] == MOD.SCHEMA
    assert plan["executes"] is False


# --- successor / actionable mapping ----------------------------------- #

def test_actionable_entry_advances_to_successor_phase():
    rows = _by_run_id(MOD.build_run_plan(_good_queue()))
    # QUEUED at idea_intake -> ADVANCE to hypothesis_spec
    assert rows["SFR-001"]["action"] == "ADVANCE_TO_NEXT_PHASE"
    assert rows["SFR-001"]["next_phase"] == "hypothesis_spec"
    assert rows["SFR-001"]["actionable"] is True
    # READY_FOR_NEXT_PHASE at data_contract_gate -> ADVANCE to
    # offline_backtest_run
    assert rows["SFR-002"]["action"] == "ADVANCE_TO_NEXT_PHASE"
    assert rows["SFR-002"]["next_phase"] == "offline_backtest_run"


def test_blocked_status_maps_to_hold_blocked():
    rows = _by_run_id(MOD.build_run_plan(_good_queue()))
    assert rows["SFR-003"]["action"] == "HOLD_BLOCKED"
    assert rows["SFR-003"]["next_phase"] is None
    assert rows["SFR-003"]["actionable"] is False
    assert rows["SFR-003"]["blockers"] == ["missing operator prereg"]


def test_awaiting_human_maps_to_await_human():
    rows = _by_run_id(MOD.build_run_plan(_good_queue()))
    assert rows["SFR-004"]["action"] == "AWAIT_HUMAN"
    assert rows["SFR-004"]["next_phase"] is None
    assert rows["SFR-004"]["actionable"] is False


def test_actionable_status_with_blockers_is_held_not_advanced():
    q = _good_queue()
    q["entries"][1]["blockers"] = ["waiting on data freeze"]  # QUEUED + blocker
    rows = _by_run_id(MOD.build_run_plan(q))
    assert rows["SFR-001"]["action"] == "HOLD_BLOCKED"
    assert rows["SFR-001"]["next_phase"] is None
    assert rows["SFR-001"]["actionable"] is False


def test_terminal_phase_maps_to_terminal_done():
    q = _good_queue()
    # actionable entry sitting on the terminal phase has no successor
    q["entries"][1]["phase"] = "block_idea_draft"
    rows = _by_run_id(MOD.build_run_plan(q))
    assert rows["SFR-001"]["action"] == "TERMINAL_DONE"
    assert rows["SFR-001"]["next_phase"] is None


def test_done_and_failed_statuses_never_advance():
    q = _good_queue()
    q["entries"][0]["status"] = "DONE"
    q["entries"][1]["status"] = "FAILED"
    rows = _by_run_id(MOD.build_run_plan(q))
    assert rows["SFR-002"]["action"] == "TERMINAL_DONE"
    assert rows["SFR-001"]["action"] == "NO_ACTION"
    assert rows["SFR-001"]["next_phase"] is None
    assert rows["SFR-002"]["next_phase"] is None


def test_forbidden_status_value_is_never_advanced():
    q = _good_queue()
    q["entries"][1]["status"] = "PROMOTE"  # forbidden promotion verb
    rows = _by_run_id(MOD.build_run_plan(q))
    assert rows["SFR-001"]["action"] == "NO_ACTION"
    assert rows["SFR-001"]["next_phase"] is None


def test_summary_counts_match_plan_rows():
    plan = MOD.build_run_plan(_good_queue())
    assert set(plan["summary"]) == set(MOD.PLAN_ACTION)
    assert sum(plan["summary"].values()) == plan["entry_count"]
    assert plan["summary"]["ADVANCE_TO_NEXT_PHASE"] == 2
    assert plan["summary"]["HOLD_BLOCKED"] == 1
    assert plan["summary"]["AWAIT_HUMAN"] == 1


# --- mutation safety --------------------------------------------------- #

def test_build_run_plan_is_mutation_safe():
    q = _good_queue()
    plan = MOD.build_run_plan(q)
    plan["plan"][0]["action"] = "MUTATED"
    plan["plan"][0]["blockers"].append("tampered")
    # the source queue is untouched
    for e in q["entries"]:
        assert e.get("status") != "MUTATED"
        assert "tampered" not in e.get("blockers", [])


# --- garbage input ----------------------------------------------------- #

def test_garbage_input_yields_safe_empty_plan():
    for bad in (None, [], 42, "nope", {"entries": "nope"}, {}):
        plan = MOD.build_run_plan(bad)
        assert plan["plan"] == []
        assert plan["entry_count"] == 0
        assert plan["executes"] is False
        assert sum(plan["summary"].values()) == 0


def test_non_dict_entries_are_skipped():
    q = _good_queue()
    q["entries"].append("not-a-dict")
    q["entries"].append(123)
    plan = MOD.build_run_plan(q)
    assert plan["entry_count"] == 4  # only the 4 dict entries


# --- import audit: no network / subprocess / trading ------------------ #

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
        "os.environ", "os.getenv", "place_order", "submit_order",
        "create_order", "ccxt", "freqtrade", "paper_trade", "live_trade",
        ".write_text(", ".write_bytes(", "smtplib", "telegram",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden tokens present: {hits}"


def test_module_references_no_phase_module():
    src = _MODPATH.read_text(encoding="utf-8")
    # the planner must never name a strategy_factory_*phase* module
    assert not re.search(r"strategy_factory_\w*phase", src), \
        "planner must not reference any strategy_factory_*phase* module"
    # it loads ONLY the Bundle 1 run-queue model by file path
    assert "strategy_factory_run_queue.py" in src

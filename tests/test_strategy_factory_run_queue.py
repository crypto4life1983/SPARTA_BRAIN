"""Bundle 1 tests for the Strategy Factory Run-Queue Model v1 (read-only).

The target is loaded BY FILE PATH (not via the package) so these tests stay
runnable with zero dependency on any package __init__ / conftest, matching
the established standalone strategy-factory test pattern.

Coverage:
- mandated safety constants are pinned,
- the status enum is exactly the approved closed set with no promotion /
  live verdict language,
- the phase chain + successor lookup are correct,
- load_queue reads JSON read-only and raises cleanly on bad input, creating
  no file,
- validate_queue accepts a good queue and flags every malformed shape,
- next_actionable is a pure, priority-ordered, mutation-safe projection,
- the module imports nothing network / subprocess / trading related.
"""

import ast
import importlib.util
import json
import pathlib

import pytest

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_run_queue.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("sfrq_under_test", _MODPATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load()


def _good_queue() -> dict:
    return {
        "schema": MOD.SCHEMA,
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


# --- safety constants -------------------------------------------------- #

def test_safety_constants_are_pinned():
    assert MOD.EXECUTES is False
    assert MOD.NETWORK is False
    assert MOD.MUTATES_REGISTRY is False
    assert MOD.SCHEDULER_OR_LOOP is False
    assert MOD.USES_BROKER is False
    assert MOD.USES_EXCHANGE is False
    assert MOD.WRITES_FILES is False
    assert MOD.CREATES_LIVE_QUEUE_DATA is False
    assert MOD.INVOKES_PHASE_MODULE is False
    assert MOD.RUNS_BACKTEST is False


# --- closed status enum ------------------------------------------------ #

def test_status_enum_is_exactly_the_approved_closed_set():
    assert MOD.QUEUE_STATUS == (
        "QUEUED",
        "BLOCKED",
        "READY_FOR_NEXT_PHASE",
        "AWAITING_HUMAN_REVIEW",
        "DONE",
        "FAILED",
    )


def test_status_enum_has_no_promotion_or_live_language():
    bad_tokens = ("PASS", "PROMOTE", "GO", "LIVE", "APPROVE", "APPROVED", "WIN")
    for status in MOD.QUEUE_STATUS:
        # exact-value check: no status IS a promotion verdict
        assert status not in MOD.FORBIDDEN_STATUS_VALUES
        # token check: the only "READY" usage is the qualified next-phase one
        for tok in bad_tokens:
            assert tok not in status, f"status {status!r} contains {tok!r}"
    assert "READY" in MOD.FORBIDDEN_STATUS_VALUES  # bare READY is forbidden


# --- phase chain ------------------------------------------------------- #

def test_phase_chain_and_successor_lookup():
    assert MOD.PHASES == (
        "idea_intake",
        "hypothesis_spec",
        "backtest_readiness",
        "data_contract_gate",
        "offline_backtest_run",
        "block_idea_draft",
    )
    assert MOD.successor_phase("idea_intake") == "hypothesis_spec"
    assert MOD.successor_phase("offline_backtest_run") == "block_idea_draft"
    assert MOD.successor_phase("block_idea_draft") is None  # terminal
    assert MOD.successor_phase("nope") is None
    assert MOD.successor_phase(None) is None


# --- load_queue (read-only) ------------------------------------------- #

def test_load_queue_reads_json(tmp_path):
    p = tmp_path / "queue.json"
    p.write_text(json.dumps(_good_queue()), encoding="utf-8")
    obj = MOD.load_queue(p)
    assert obj["schema"] == MOD.SCHEMA
    assert len(obj["entries"]) == 4


def test_load_queue_missing_file_raises_and_creates_nothing(tmp_path):
    p = tmp_path / "absent.json"
    with pytest.raises(MOD.RunQueueError):
        MOD.load_queue(p)
    # load_queue must not create the queue file it failed to find
    assert not p.exists()


def test_load_queue_bad_json_raises(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(MOD.RunQueueError):
        MOD.load_queue(p)


def test_load_queue_non_object_root_raises(tmp_path):
    p = tmp_path / "list.json"
    p.write_text("[1, 2, 3]", encoding="utf-8")
    with pytest.raises(MOD.RunQueueError):
        MOD.load_queue(p)


# --- validate_queue ---------------------------------------------------- #

def test_validate_good_queue_passes():
    ok, errors = MOD.validate_queue(_good_queue())
    assert ok, errors
    assert errors == []


def test_validate_rejects_non_dict():
    ok, errors = MOD.validate_queue([])
    assert not ok and errors


def test_validate_rejects_missing_entries():
    ok, errors = MOD.validate_queue({"schema": MOD.SCHEMA})
    assert not ok
    assert any("entries" in e for e in errors)


def test_validate_flags_missing_required_field():
    q = _good_queue()
    del q["entries"][0]["phase"]
    ok, errors = MOD.validate_queue(q)
    assert not ok
    assert any("missing required field 'phase'" in e for e in errors)


def test_validate_flags_forbidden_status_value():
    q = _good_queue()
    q["entries"][0]["status"] = "PROMOTE"
    ok, errors = MOD.validate_queue(q)
    assert not ok
    assert any("forbidden status value" in e for e in errors)


def test_validate_flags_status_outside_enum():
    q = _good_queue()
    q["entries"][0]["status"] = "MAYBE"
    ok, errors = MOD.validate_queue(q)
    assert not ok
    assert any("not in closed enum" in e for e in errors)


def test_validate_flags_unknown_phase():
    q = _good_queue()
    q["entries"][0]["phase"] = "rocket_launch"
    ok, errors = MOD.validate_queue(q)
    assert not ok
    assert any("not in closed phase chain" in e for e in errors)


def test_validate_flags_non_int_and_bool_priority():
    q = _good_queue()
    q["entries"][0]["priority"] = "high"
    ok, errors = MOD.validate_queue(q)
    assert not ok
    assert any("priority must be an integer" in e for e in errors)

    q2 = _good_queue()
    q2["entries"][0]["priority"] = True
    ok2, errors2 = MOD.validate_queue(q2)
    assert not ok2
    assert any("not a bool" in e for e in errors2)


def test_validate_flags_duplicate_run_id():
    q = _good_queue()
    q["entries"][1]["run_id"] = "SFR-002"  # collide with entry[0]
    ok, errors = MOD.validate_queue(q)
    assert not ok
    assert any("duplicate run_id" in e for e in errors)


def test_validate_flags_blocked_without_blockers():
    q = _good_queue()
    q["entries"][2]["blockers"] = []  # BLOCKED entry, now no reason
    ok, errors = MOD.validate_queue(q)
    assert not ok
    assert any("BLOCKED entry must list at least one blocker" in e for e in errors)


def test_validate_flags_bad_safety_level():
    q = _good_queue()
    q["entries"][0]["safety_level"] = "live"
    ok, errors = MOD.validate_queue(q)
    assert not ok
    assert any("safety_level must be" in e for e in errors)


# --- next_actionable (pure projection) -------------------------------- #

def test_next_actionable_orders_by_priority_and_excludes_others():
    out = MOD.next_actionable(_good_queue())
    # only the QUEUED + READY_FOR_NEXT_PHASE entries, in priority order
    assert [e["run_id"] for e in out] == ["SFR-001", "SFR-002"]
    # BLOCKED and AWAITING_HUMAN_REVIEW entries are excluded
    excluded = {"SFR-003", "SFR-004"}
    assert excluded.isdisjoint({e["run_id"] for e in out})


def test_next_actionable_excludes_actionable_status_with_blockers():
    q = _good_queue()
    q["entries"][1]["blockers"] = ["waiting on data freeze"]  # QUEUED + blocker
    out = MOD.next_actionable(q)
    assert [e["run_id"] for e in out] == ["SFR-002"]


def test_next_actionable_is_mutation_safe():
    q = _good_queue()
    out = MOD.next_actionable(q)
    out[0]["status"] = "MUTATED"
    out[0]["candidate_id"] = "tampered"
    # the source queue is untouched
    for e in q["entries"]:
        assert e["status"] != "MUTATED"
        assert e["candidate_id"] != "tampered"


def test_next_actionable_handles_garbage_input():
    assert MOD.next_actionable(None) == []
    assert MOD.next_actionable({"entries": "nope"}) == []
    assert MOD.next_actionable({}) == []


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
    allowed = {"__future__", "json", "pathlib", "typing"}
    assert roots <= allowed, f"unexpected imports: {sorted(roots - allowed)}"

    forbidden = (
        "import socket", "import subprocess", "from subprocess", "urllib",
        "requests", "httpx", "http.client", "asyncio", "Popen", "os.system",
        "place_order", "submit_order", "create_order", "ccxt", "freqtrade",
        "paper_trade", "live_trade",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden tokens present: {hits}"

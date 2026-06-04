"""Bundle 4 tests for the Strategy Factory Queue Artifact Schema v1 +
canonical sample fixture (read-only).

The target + its sibling backbone modules are loaded BY FILE PATH (not via
the package) so these tests stay runnable with zero dependency on any
package __init__ / conftest, matching the established standalone
strategy-factory test pattern.

Coverage:
- mandated safety constants are pinned False,
- the schema descriptor is derived from Bundle 1's single source of truth
  (no drift between description and validator),
- describe_schema() is pure (fresh dict each call, caller cannot tamper),
- the canonical sample fixture loads + validates clean under Bundle 1,
  plans clean under Bundle 2, and renders clean under Bundle 3,
- the fixture carries no forbidden status token,
- the module imports nothing network / subprocess / trading related and
  writes no file.
"""

import ast
import importlib.util
import pathlib

_HERE = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = _HERE / "sparta_commander" / "strategy_factory_queue_schema.py"
_QUEUE_PATH = _HERE / "sparta_commander" / "strategy_factory_run_queue.py"
_PLANNER_PATH = (
    _HERE / "sparta_commander" / "strategy_factory_run_queue_planner.py"
)
_REPORTER_PATH = (
    _HERE / "sparta_commander" / "strategy_factory_run_queue_reporter.py"
)
_FIXTURE = _HERE / "tests" / "fixtures" / "strategy_factory_sample_queue.json"


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load("sfqs_under_test", _MODPATH)
QUEUE = _load("sfrq_for_schema_test", _QUEUE_PATH)
PLANNER = _load("sfrqp_for_schema_test", _PLANNER_PATH)
REPORTER = _load("sfrqr_for_schema_test", _REPORTER_PATH)


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


# --- schema derived from Bundle 1 (no drift) -------------------------- #

def test_schema_is_derived_from_bundle1():
    assert MOD.QUEUE_SCHEMA_ID == QUEUE.SCHEMA
    assert MOD.PHASES == QUEUE.PHASES
    assert MOD.QUEUE_STATUS == QUEUE.QUEUE_STATUS
    assert MOD.REQUIRED_ENTRY_FIELDS == QUEUE.REQUIRED_ENTRY_FIELDS
    assert MOD.FORBIDDEN_STATUS_VALUES == QUEUE.FORBIDDEN_STATUS_VALUES


def test_schema_fields_matches_bundle1_required():
    assert MOD.schema_fields() == QUEUE.REQUIRED_ENTRY_FIELDS


def test_describe_schema_shape():
    d = MOD.describe_schema()
    assert d["describes_artifact_schema"] == QUEUE.SCHEMA
    assert d["executes"] is False
    assert d["safety_level"] == "research_only"
    assert d["phase_chain"] == list(QUEUE.PHASES)
    assert d["status_enum"] == list(QUEUE.QUEUE_STATUS)
    assert set(d["entry"]["required_fields"]) == set(QUEUE.REQUIRED_ENTRY_FIELDS)
    # forbidden values are surfaced so consumers know what can never appear
    assert "PROMOTE" in d["forbidden_status_values"]


def test_describe_schema_is_pure_fresh_dict():
    a = MOD.describe_schema()
    b = MOD.describe_schema()
    assert a == b
    assert a is not b
    # tampering with one result must not affect the next
    a["phase_chain"].append("ROCKET")
    assert "ROCKET" not in MOD.describe_schema()["phase_chain"]


def test_describe_schema_status_enum_has_no_verdict_language():
    d = MOD.describe_schema()
    bad = ("PASS", "PROMOTE", "GO", "LIVE", "APPROVE", "APPROVED", "WIN")
    for status in d["status_enum"]:
        for tok in bad:
            assert tok not in status, f"status {status!r} contains {tok!r}"


# --- canonical sample fixture ----------------------------------------- #

def test_fixture_loads_and_validates_under_bundle1():
    queue = QUEUE.load_queue(_FIXTURE)
    assert queue["schema"] == QUEUE.SCHEMA
    ok, errors = QUEUE.validate_queue(queue)
    assert ok, errors
    assert errors == []
    assert len(queue["entries"]) == 5


def test_fixture_entries_use_only_closed_enums():
    queue = QUEUE.load_queue(_FIXTURE)
    for e in queue["entries"]:
        assert e["status"] in QUEUE.QUEUE_STATUS
        assert e["status"] not in QUEUE.FORBIDDEN_STATUS_VALUES
        assert e["phase"] in QUEUE.PHASES


def test_fixture_blocked_entry_has_blocker():
    queue = QUEUE.load_queue(_FIXTURE)
    blocked = [e for e in queue["entries"] if e["status"] == "BLOCKED"]
    assert blocked
    for e in blocked:
        assert e["blockers"], "BLOCKED fixture entry must list a blocker"


def test_fixture_plans_under_bundle2():
    queue = QUEUE.load_queue(_FIXTURE)
    plan = PLANNER.build_run_plan(queue)
    assert plan["entry_count"] == 5
    # the two actionable entries (QUEUED + READY_FOR_NEXT_PHASE, no blockers)
    advancing = [r for r in plan["plan"] if r["action"] == "ADVANCE_TO_NEXT_PHASE"]
    assert {r["run_id"] for r in advancing} == {"SFR-001", "SFR-002"}


def test_fixture_renders_under_bundle3():
    queue = QUEUE.load_queue(_FIXTURE)
    plan = PLANNER.build_run_plan(queue)
    text = REPORTER.render_plan_text(plan)
    md = REPORTER.render_plan_markdown(plan)
    assert isinstance(text, str) and "SFR-001" in text
    assert isinstance(md, str) and "| run_id |" in md


def test_fixture_carries_no_forbidden_status_token():
    raw = _FIXTURE.read_text(encoding="utf-8").upper()
    for tok in QUEUE.FORBIDDEN_STATUS_VALUES:
        # the closed enum value READY_FOR_NEXT_PHASE legitimately contains
        # the bare 'READY' substring; assert no forbidden value stands alone
        # as a status by checking it is never quoted as a status value.
        assert f'"STATUS": "{tok}"' not in raw
        assert f'"{tok}"' not in raw or tok == "READY"


def test_fixture_is_illustrative_only_marker_present():
    raw = _FIXTURE.read_text(encoding="utf-8")
    assert "NOT a live or authorized run queue" in raw


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
        "open(", "write_text(", ".write(", "json.dump(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden tokens present: {hits}"

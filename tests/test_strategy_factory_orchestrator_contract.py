"""Bundle 5 tests for the Strategy Factory Dry-Run Orchestrator Contract v1
(read-only).

The target + its Bundle 2 source are loaded BY FILE PATH (not via the
package) so these tests stay runnable with zero dependency on any package
__init__ / conftest, matching the established standalone strategy-factory
test pattern.

Coverage:
- mandated safety constants are pinned False,
- the contract action set is derived from Bundle 2's PLAN_ACTION (no drift
  between the contract and the planner that produces the actions),
- describe_orchestrator_contract() is pure (fresh dict each call, caller
  cannot tamper),
- the contract is human-gated where a step would advance, and executes
  nothing,
- no descriptive intent / precondition prose carries an execution or
  promotion verb,
- contract_for_action() is a safe pure lookup (no raise; safe fallback),
- render_contract_markdown() returns a non-empty string and writes nothing,
- the module imports nothing network / subprocess / trading related and
  writes no file.
"""

import ast
import importlib.util
import pathlib
import re

_HERE = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _HERE / "sparta_commander" / "strategy_factory_orchestrator_contract.py"
)
_PLANNER_PATH = (
    _HERE / "sparta_commander" / "strategy_factory_run_queue_planner.py"
)


def _load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _load("sfoc_under_test", _MODPATH)
PLANNER = _load("sfrqp_for_contract_test", _PLANNER_PATH)

# Execution / promotion verbs that must never appear in descriptive prose.
_BAD_TOKENS = (
    "RUN", "EXECUTE", "PLACE", "TRADE",
    "PASS", "PROMOTE", "READY", "GO", "LIVE", "APPROVE", "WIN",
)


def _prose_strings() -> list[str]:
    """Collect every descriptive prose string (intent + preconditions) from
    the contract -- but NOT the forbidden-capability enumeration, which is
    banned-capability data, not a step's own prose."""
    c = MOD.describe_orchestrator_contract()
    out: list[str] = []
    for step in c["steps"].values():
        out.append(step["intent"])
        out.extend(step["preconditions"])
    return out


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


# --- contract derived from Bundle 2 (no drift) ------------------------- #

def test_contract_action_set_is_derived_from_bundle2():
    c = MOD.describe_orchestrator_contract()
    assert set(c["steps"].keys()) == set(PLANNER.PLAN_ACTION)
    assert MOD.PLAN_ACTION == PLANNER.PLAN_ACTION
    assert c["source_schema"] == PLANNER.SCHEMA


def test_describe_shape():
    c = MOD.describe_orchestrator_contract()
    assert c["schema"] == MOD.SCHEMA
    assert c["safety_level"] == "research_only"
    assert c["executes"] is False
    assert c["requires_human_approval"] is True
    assert c["forbidden_capabilities"]  # non-empty
    for action in PLANNER.PLAN_ACTION:
        step = c["steps"][action]
        assert step["action"] == action
        assert isinstance(step["intent"], str) and step["intent"]
        assert isinstance(step["preconditions"], list)
        assert isinstance(step["requires_human_approval"], bool)
        assert step["forbidden"] == list(MOD.FORBIDDEN_CAPABILITIES)


def test_describe_is_pure_fresh_dict():
    a = MOD.describe_orchestrator_contract()
    b = MOD.describe_orchestrator_contract()
    assert a == b
    assert a is not b
    # tampering with one result must not affect the next
    a["forbidden_capabilities"].append("anything")
    a["steps"]["NO_ACTION"]["preconditions"].append("tampered")
    fresh = MOD.describe_orchestrator_contract()
    assert "anything" not in fresh["forbidden_capabilities"]
    assert "tampered" not in fresh["steps"]["NO_ACTION"]["preconditions"]


def test_executes_false_and_advance_is_human_gated():
    c = MOD.describe_orchestrator_contract()
    assert c["executes"] is False
    assert c["steps"]["ADVANCE_TO_NEXT_PHASE"]["requires_human_approval"] is True
    assert c["steps"]["AWAIT_HUMAN"]["requires_human_approval"] is True


def test_prose_has_no_execution_or_promotion_verb():
    for text in _prose_strings():
        upper = text.upper()
        for tok in _BAD_TOKENS:
            assert not re.search(rf"\b{tok}\b", upper), (
                f"prose {text!r} contains forbidden token {tok!r}"
            )


# --- contract_for_action: safe pure lookup ----------------------------- #

def test_contract_for_action_covers_every_action():
    for action in PLANNER.PLAN_ACTION:
        row = MOD.contract_for_action(action)
        assert row["action"] == action
        assert row["forbidden"] == list(MOD.FORBIDDEN_CAPABILITIES)


def test_contract_for_action_unknown_is_safe_fallback():
    for junk in ("ROCKET", "", None, 123, "PROMOTE"):
        row = MOD.contract_for_action(junk)
        assert row["action"] == "UNKNOWN"
        # the safe fallback grants nothing yet still demands a human gate
        assert row["requires_human_approval"] is True
        assert row["forbidden"] == list(MOD.FORBIDDEN_CAPABILITIES)


# --- markdown renderer: strings only ----------------------------------- #

def test_render_contract_markdown_returns_string():
    md = MOD.render_contract_markdown()
    assert isinstance(md, str) and md
    assert "Dry-Run Orchestrator Contract" in md
    assert "ADVANCE_TO_NEXT_PHASE" in md
    # forbidden capabilities are surfaced so a reader sees the banned set
    assert "file_write" in md


def test_render_contract_markdown_has_no_execution_verb_in_prose():
    # The rendered contract content must not read as a command. Heading
    # lines are excluded: the H1 carries the bundle's proper name
    # ("Dry-Run Orchestrator Contract"), where "Run" is the document title,
    # not a step verb. The snake_case forbidden tokens never form a bare
    # word match because they are joined by underscores.
    body = "\n".join(
        ln for ln in MOD.render_contract_markdown().splitlines()
        if not ln.lstrip().startswith("#")
    ).upper()
    for tok in _BAD_TOKENS:
        assert not re.search(rf"\b{tok}\b", body), f"markdown contains {tok!r}"


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

"""Bundle 39 tests for the Strategy Factory Fake Report Renderer Result Review
Contract v1 (informational, read-only, fake-only, review-contract-only,
deterministic, execution-free -- NO written report on disk, NO report file
write, NO report execution beyond reviewing the in-memory fake result object,
NO real dry walk, NO orchestrator, NO real pipeline, NO smoke-test run, NO
runtime state write, NO research, NO data access).

This bundle defines the human/operator result review gate for the Bundle 38
in-memory fake rendered report. It activates only from an active Bundle 38
renderer result whose next_gate is FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED,
whose rendered preview / report sections / safety attestation / placeholder-only
guard all exist, and whose real-artifact scan found nothing.

Bundle 39's production module imports Bundles 11-38 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_fake_report_renderer_result_review_contract import (  # noqa: E501
    RESULT_REVIEW_SCHEMA_VERSION,
    DEFAULT_RESULT_REVIEW_LABEL,
    RESULT_REVIEW_STATUS,
    RESULT_REVIEW_SAFETY_POSTURE,
    RESULT_REVIEW_STATE_ACTIVE,
    RESULT_REVIEW_STATE_BLOCKED,
    RESULT_REVIEW_DECISION_NEEDS_FAKE_REPORT_RENDER_FIX,
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT,
    RESULT_REVIEW_DECISION_PARK,
    RESULT_REVIEW_DECISION_REJECT,
    ALLOWED_RESULT_REVIEW_DECISIONS,
    NEXT_GATE_FAKE_LANE_CLOSURE_CONTRACT_REQUIRED,
    NEXT_GATE_FAKE_REPORT_RENDER_FIX_REQUIRED,
    NEXT_GATE_FAKE_REPORT_RENDERER_PARKED,
    NEXT_GATE_FAKE_REPORT_RENDERER_REJECTED,
    NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION,
    NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT,
    REQUIRED_RENDERED_RESULT_FIELDS,
    REQUIRED_REPORT_SECTION_REVIEW_FIELDS,
    REQUIRED_SAFETY_REVIEW_FIELDS,
    REQUIRED_PLACEHOLDER_GUARD_REVIEW_FIELDS,
    REVIEW_PASS_CRITERIA,
    REVIEW_FAIL_CRITERIA,
    REJECTION_CONDITIONS,
    build_fake_report_renderer_result_review_contract,
    validate_fake_report_renderer_result_review_contract,
    render_fake_report_renderer_result_review_contract_markdown,
)
import sparta_commander.strategy_factory_fake_report_renderer_result_review_contract as RV  # noqa: E501
from sparta_commander.strategy_factory_fake_report_renderer_in_memory import (
    RENDERER_IN_MEMORY_SCHEMA_VERSION,
    RENDERER_IN_MEMORY_SAFETY_POSTURE,
    build_fake_report_renderer_state,
)
from sparta_commander.strategy_factory_fake_report_renderer_contract import (
    build_fake_report_renderer_contract,
)
from sparta_commander.strategy_factory_fake_walk_report_operator_review_gate import (  # noqa: E501
    OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT,
    build_fake_walk_report_operator_review_gate,
)
from sparta_commander.strategy_factory_fake_walk_report_contract import (
    build_fake_walk_report_contract,
)
from sparta_commander.strategy_factory_fake_dry_walk_result_review_contract import (  # noqa: E501
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT,
    build_fake_dry_walk_result_review_contract,
)
from sparta_commander.strategy_factory_fake_dry_walk_in_memory import (
    build_fake_dry_walk_state,
)
from sparta_commander.strategy_factory_fake_dry_walk_implementation_contract import (  # noqa: E501
    build_fake_dry_walk_implementation_contract,
)
from sparta_commander.strategy_factory_fake_dry_walk_operator_review_gate import (
    OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT,
    build_fake_dry_walk_operator_review_gate,
)
from sparta_commander.strategy_factory_fake_artifact_dry_walk_contract import (
    build_fake_artifact_dry_walk_contract,
)
from sparta_commander.strategy_factory_fake_artifact_smoke_test_contract import (
    build_fake_artifact_smoke_test_contract,
)
from sparta_commander.strategy_factory_backbone_closure_report import (
    build_backbone_closure_report,
)
from sparta_commander.strategy_factory_end_to_end_fake_pipeline_contract import (
    build_end_to_end_fake_pipeline_contract,
)
from sparta_commander.strategy_factory_safety_kill_switch_contract import (
    build_safety_kill_switch_contract,
)
from sparta_commander.strategy_factory_decision_ledger_contract import (
    build_decision_ledger_contract,
)
from sparta_commander.strategy_factory_dashboard_registry_feed_contract import (
    build_dashboard_registry_feed_contract,
)
from sparta_commander.strategy_factory_dry_run_orchestrator_contract import (
    build_dry_run_orchestrator_contract,
)
from sparta_commander.strategy_factory_research_runner_contract import (
    build_research_runner_contract,
)
from sparta_commander.strategy_factory_data_qa_contract import (
    build_data_qa_contract,
)
from sparta_commander.strategy_factory_data_contract_planning import (
    build_data_contract_planning,
)
from sparta_commander.strategy_factory_protocol_review_gate import (
    REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING,
    build_protocol_review_gate,
)
from sparta_commander.strategy_factory_research_protocol_draft_contract import (
    build_research_protocol_draft_contract,
)
from sparta_commander.strategy_factory_research_decision_memo_contract import (
    MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
)
from sparta_commander.strategy_factory_research_queue import (
    build_research_queue_item,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_fake_report_renderer_result_review_contract.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

_BAD_VERBS = (
    "RUN", "EXECUTE", "LAUNCH", "SUBMIT", "TRADE", "ORDER",
    "PROMOTE", "DEPLOY", "UPLOAD", "FETCH", "BACKTEST",
)

_AUTH_FLAGS = (
    "approved_for_research", "execution_authorized",
    "paper_trading_authorized", "live_trading_authorized",
    "data_fetch_authorized", "backtest_authorized", "promotion_authorized",
)

_REQUIRED_BLOCKED = (
    "data_fetch", "backtest", "simulation", "broker", "exchange", "order",
    "live_execution", "paper_execution", "upload", "autopilot",
    "promotion", "subprocess", "network", "file_write", "file_read",
    "directory_listing", "dashboard_runtime_update", "registry_file_write",
    "template_edit", "ledger_runtime_write", "runtime_approval_write",
    "runtime_safety_flag_write", "pipeline_execution", "smoke_test_execution",
    "dry_walk_execution", "operator_review_gate_execution",
    "dry_walk_implementation_execution", "result_review_execution",
    "report_file_write", "report_render_execution",
    "report_renderer_implementation_execution",
    "report_renderer_result_review_execution", "runtime_state_write",
)

_EXPECTED_POSTURE_KEYS = {
    "automation_enabled", "live_execution_enabled", "paper_execution_enabled",
    "file_write_enabled", "network_enabled", "subprocess_enabled",
    "strategy_promotion_enabled", "broker_enabled", "exchange_enabled",
    "order_enabled", "data_fetch_enabled", "backtest_enabled",
    "upload_enabled", "autopilot_enabled",
}


def _good_item() -> dict:
    return build_research_queue_item(
        "idea-001",
        "Opening Range Mean Reversion",
        "Price tends to revert toward the opening range midpoint intraday.",
        asset_lane="MNQ",
        timeframe="5m",
    )


def _ready_closure() -> dict:
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(
        draft, review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING)
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    orchestrator = build_dry_run_orchestrator_contract(runner)
    feed = build_dashboard_registry_feed_contract(orchestrator)
    ledger = build_decision_ledger_contract(feed)
    safety_gate = build_safety_kill_switch_contract(ledger)
    pipeline = build_end_to_end_fake_pipeline_contract(safety_gate)
    return build_backbone_closure_report(pipeline)


def _blocked_closure() -> dict:
    draft = build_research_protocol_draft_contract(
        _good_item(),
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    gate = build_protocol_review_gate(draft)  # awaiting, not unlocked
    planning = build_data_contract_planning(gate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    orchestrator = build_dry_run_orchestrator_contract(runner)
    feed = build_dashboard_registry_feed_contract(orchestrator)
    ledger = build_decision_ledger_contract(feed)
    safety_gate = build_safety_kill_switch_contract(ledger)
    pipeline = build_end_to_end_fake_pipeline_contract(safety_gate)
    return build_backbone_closure_report(pipeline)


def _active_walk_state() -> dict:
    smoke = build_fake_artifact_smoke_test_contract(_ready_closure())
    dry_walk = build_fake_artifact_dry_walk_contract(smoke)
    gate = build_fake_dry_walk_operator_review_gate(
        dry_walk,
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
        ),
    )
    contract = build_fake_dry_walk_implementation_contract(gate)
    return build_fake_dry_walk_state(contract)


def _blocked_walk_state() -> dict:
    smoke = build_fake_artifact_smoke_test_contract(_blocked_closure())
    dry_walk = build_fake_artifact_dry_walk_contract(smoke)
    gate = build_fake_dry_walk_operator_review_gate(dry_walk)
    contract = build_fake_dry_walk_implementation_contract(gate)
    return build_fake_dry_walk_state(contract)


def _active_renderer_contract() -> dict:
    review = build_fake_dry_walk_result_review_contract(
        _active_walk_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
        ),
    )
    report = build_fake_walk_report_contract(review)
    gate = build_fake_walk_report_operator_review_gate(
        report,
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT
        ),
    )
    return build_fake_report_renderer_contract(gate)


def _blocked_renderer_contract() -> dict:
    review = build_fake_dry_walk_result_review_contract(
        _blocked_walk_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
        ),
    )
    report = build_fake_walk_report_contract(review)
    gate = build_fake_walk_report_operator_review_gate(
        report,
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT
        ),
    )
    return build_fake_report_renderer_contract(gate)


def _active_renderer_state(**kw) -> dict:
    return build_fake_report_renderer_state(_active_renderer_contract(), **kw)


def _blocked_renderer_state() -> dict:
    return build_fake_report_renderer_state(_blocked_renderer_contract())


def _contract(renderer_state=None, decision=None) -> dict:
    return build_fake_report_renderer_result_review_contract(
        renderer_state if renderer_state is not None
        else _active_renderer_state(),
        result_review_decision=decision,
    )


def _expected_public() -> set[str]:
    return {
        "RESULT_REVIEW_SCHEMA_VERSION",
        "DEFAULT_RESULT_REVIEW_LABEL",
        "RESULT_REVIEW_STATUS",
        "RESULT_REVIEW_SAFETY_POSTURE",
        "RESULT_REVIEW_STATE_ACTIVE",
        "RESULT_REVIEW_STATE_BLOCKED",
        "RESULT_REVIEW_DECISION_NEEDS_FAKE_REPORT_RENDER_FIX",
        "RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT",
        "RESULT_REVIEW_DECISION_PARK",
        "RESULT_REVIEW_DECISION_REJECT",
        "ALLOWED_RESULT_REVIEW_DECISIONS",
        "NEXT_GATE_FAKE_LANE_CLOSURE_CONTRACT_REQUIRED",
        "NEXT_GATE_FAKE_REPORT_RENDER_FIX_REQUIRED",
        "NEXT_GATE_FAKE_REPORT_RENDERER_PARKED",
        "NEXT_GATE_FAKE_REPORT_RENDERER_REJECTED",
        "NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION",
        "NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT",
        "REQUIRED_RENDERED_RESULT_FIELDS",
        "REQUIRED_REPORT_SECTION_REVIEW_FIELDS",
        "REQUIRED_SAFETY_REVIEW_FIELDS",
        "REQUIRED_PLACEHOLDER_GUARD_REVIEW_FIELDS",
        "REVIEW_PASS_CRITERIA",
        "REVIEW_FAIL_CRITERIA",
        "REJECTION_CONDITIONS",
        "build_fake_report_renderer_result_review_contract",
        "validate_fake_report_renderer_result_review_contract",
        "render_fake_report_renderer_result_review_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(RV.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(RV, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        RESULT_REVIEW_SCHEMA_VERSION
        == "strategy_factory_fake_report_renderer_result_review_contract.v1"
    )
    assert (
        DEFAULT_RESULT_REVIEW_LABEL
        == "Strategy Factory Fake Report Renderer Result Review Contract"
    )
    assert (
        RESULT_REVIEW_STATUS
        == "READ_ONLY_FAKE_REPORT_RENDERER_RESULT_REVIEW_CONTRACT"
    )


# 3 -- state / next-gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        RESULT_REVIEW_STATE_ACTIVE
        == "FAKE_REPORT_RENDERER_RESULT_REVIEW_CONTRACT_ACTIVE"
    )
    assert (
        RESULT_REVIEW_STATE_BLOCKED
        == "FAKE_REPORT_RENDERER_RESULT_REVIEW_CONTRACT_BLOCKED"
    )
    assert (
        NEXT_GATE_FAKE_LANE_CLOSURE_CONTRACT_REQUIRED
        == "FAKE_LANE_CLOSURE_CONTRACT_REQUIRED"
    )
    assert (
        NEXT_GATE_FAKE_REPORT_RENDER_FIX_REQUIRED
        == "FAKE_REPORT_RENDER_FIX_REQUIRED"
    )
    assert (
        NEXT_GATE_FAKE_REPORT_RENDERER_PARKED == "FAKE_REPORT_RENDERER_PARKED"
    )
    assert (
        NEXT_GATE_FAKE_REPORT_RENDERER_REJECTED
        == "FAKE_REPORT_RENDERER_REJECTED"
    )
    assert (
        NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION
        == "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION"
    )
    assert (
        NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT
        == "AWAIT_FAKE_REPORT_RENDERER_RESULT"
    )


# 4 -- allowed result review decisions are exactly the expected set.

def test_allowed_result_review_decisions_exact():
    assert ALLOWED_RESULT_REVIEW_DECISIONS == (
        "NEEDS_FAKE_REPORT_RENDER_FIX",
        "READY_FOR_FAKE_LANE_CLOSURE_CONTRACT",
        "PARK",
        "REJECT",
    )


# 5 -- pure stdlib import-root audit: allowed roots only.

def test_import_roots_are_allowed_only():
    src = _MODPATH.read_text(encoding="utf-8")
    roots: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {"__future__", "typing", "sparta_commander"}
    assert roots <= allowed, f"unexpected import roots: {sorted(roots - allowed)}"
    for banned in ("os", "sys", "subprocess", "socket", "requests",
                   "urllib", "pathlib", "json", "http", "asyncio",
                   "datetime", "time", "random", "glob", "importlib",
                   "shutil", "io"):
        assert banned not in roots, f"banned import root present: {banned}"


# 6 -- forbidden-surface audit: no file/network/subprocess/exec/dynamic surface.

def test_no_forbidden_call_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    forbidden = (
        "open(", "write_text(", "write_bytes(", ".write(", "read_text(",
        "read_bytes(", ".read(", "json.dump(", "json.load(",
        "import subprocess", "from subprocess", "Popen", "os.system",
        "os.listdir", "os.scandir", "os.walk", "listdir(", "scandir(",
        "glob(", "iglob(", "import socket", "socket.socket", "urllib",
        "requests", "httpx", "http.client", "asyncio", "place_order",
        "submit_order", "create_order", "cancel_order", "ccxt", "freqtrade",
        "paper_trade", "live_trade", "autopilot(", ".upload(", "datetime.",
        "time.time(", "random.", "subprocess.run", "check_output",
        "importlib", "__import__", "eval(", "exec(", "compile(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


# 7 -- no filesystem read/write surface in source.

def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# 8 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = RESULT_REVIEW_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 9 -- posture keys + values match Bundle 38.

def test_posture_matches_bundle38():
    assert RESULT_REVIEW_SAFETY_POSTURE == RENDERER_IN_MEMORY_SAFETY_POSTURE


# 10 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _contract()
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _contract()
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert RESULT_REVIEW_SAFETY_POSTURE["automation_enabled"] is False


# 11 -- an active Bundle 38 renderer result activates the review contract.

def test_active_renderer_result_activates_contract():
    c = _contract()
    assert c["fake_report_renderer_result_review_contract_active"] is True
    assert (
        c["fake_report_renderer_result_review_contract_state"]
        == "FAKE_REPORT_RENDERER_RESULT_REVIEW_CONTRACT_ACTIVE"
    )
    assert c["fake_report_renderer_active"] is True
    assert (
        c["fake_report_renderer_next_gate"]
        == "FAKE_REPORT_RENDERER_RESULT_REVIEW_REQUIRED"
    )
    assert c["schema_version"] == RESULT_REVIEW_SCHEMA_VERSION
    assert (
        c["fake_report_renderer_in_memory_schema_version"]
        == RENDERER_IN_MEMORY_SCHEMA_VERSION
    )
    # No decision yet -> awaiting decision.
    assert (
        c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION"
    )


# 12 -- a blocked (inactive) upstream renderer does not activate.

def test_blocked_renderer_does_not_activate():
    c = _contract(_blocked_renderer_state())
    assert c["fake_report_renderer_result_review_contract_active"] is False
    assert (
        c["fake_report_renderer_result_review_contract_state"]
        == "FAKE_REPORT_RENDERER_RESULT_REVIEW_CONTRACT_BLOCKED"
    )
    assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT"


# 13 -- active renderer but wrong next_gate does not activate.

def test_wrong_next_gate_does_not_activate():
    import copy
    s = copy.deepcopy(_active_renderer_state())
    s["next_gate"] = "SOMETHING_ELSE"
    c = _contract(s)
    assert c["fake_report_renderer_result_review_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT"


# 14 -- inactive renderer flag does not activate even with right gate.

def test_inactive_renderer_flag_does_not_activate():
    import copy
    s = copy.deepcopy(_active_renderer_state())
    s["fake_report_renderer_active"] = False
    c = _contract(s)
    assert c["fake_report_renderer_result_review_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT"


# 15 -- a non-empty real_artifact_hits scan blocks activation.

def test_real_artifact_hits_block_activation():
    s = _active_renderer_state(
        fake_overrides={
            "fake_walk_summary": {
                "fake_walk_note_placeholder": "see Crypto-D1 data",
            },
        },
    )
    # The Bundle 38 state itself recorded the hit.
    assert s["validation"]["real_artifact_hits"] != ()
    c = _contract(s)
    assert c["fake_report_renderer_result_review_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT"


# 16 -- missing rendered preview / sections / guard blocks activation.

def test_missing_required_renderer_pieces_block_activation():
    import copy
    for key in ("rendered_markdown_preview", "report_sections",
                "fake_safety_attestation", "placeholder_only_guard"):
        s = copy.deepcopy(_active_renderer_state())
        s.pop(key, None)
        c = _contract(s)
        assert (
            c["fake_report_renderer_result_review_contract_active"] is False
        ), key
        assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT", key


# 17 -- malformed input never raises and never activates.

def test_malformed_input_no_raise():
    for bad in (None, 42, "nope", {},
                {"fake_report_renderer_active": True}, []):
        c = build_fake_report_renderer_result_review_contract(bad)
        assert c["fake_report_renderer_result_review_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT"
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 18 -- READY_FOR_FAKE_LANE_CLOSURE_CONTRACT maps to the closure gate.

def test_ready_decision_maps_to_closure_contract():
    c = _contract(decision=(
        RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT))
    assert c["fake_report_renderer_result_review_contract_active"] is True
    assert c["result_review_decision"] == "READY_FOR_FAKE_LANE_CLOSURE_CONTRACT"
    assert c["next_gate"] == "FAKE_LANE_CLOSURE_CONTRACT_REQUIRED"


# 19 -- other decisions never unlock the closure contract.

def test_other_decisions_never_unlock_closure():
    mapping = {
        RESULT_REVIEW_DECISION_NEEDS_FAKE_REPORT_RENDER_FIX:
            "FAKE_REPORT_RENDER_FIX_REQUIRED",
        RESULT_REVIEW_DECISION_PARK: "FAKE_REPORT_RENDERER_PARKED",
        RESULT_REVIEW_DECISION_REJECT: "FAKE_REPORT_RENDERER_REJECTED",
        None: "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION",
        "BOGUS_DECISION": "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW_DECISION",
    }
    for decision, expected_gate in mapping.items():
        c = _contract(decision=decision)
        assert c["next_gate"] == expected_gate, decision
        assert c["next_gate"] != "FAKE_LANE_CLOSURE_CONTRACT_REQUIRED"


# 20 -- a decision on a blocked renderer still cannot unlock closure.

def test_decision_on_blocked_renderer_stays_blocked():
    c = _contract(
        _blocked_renderer_state(),
        decision=RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT,
    )
    assert c["fake_report_renderer_result_review_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT"


# 21 -- required review field tuples are present on the contract.

def test_required_review_field_tuples_present():
    c = _contract()
    assert (
        tuple(c["required_rendered_result_fields"])
        == REQUIRED_RENDERED_RESULT_FIELDS
    )
    assert (
        tuple(c["required_report_section_review_fields"])
        == REQUIRED_REPORT_SECTION_REVIEW_FIELDS
    )
    assert (
        tuple(c["required_safety_review_fields"])
        == REQUIRED_SAFETY_REVIEW_FIELDS
    )
    assert (
        tuple(c["required_placeholder_guard_review_fields"])
        == REQUIRED_PLACEHOLDER_GUARD_REVIEW_FIELDS
    )
    for coll in (REQUIRED_RENDERED_RESULT_FIELDS,
                 REQUIRED_REPORT_SECTION_REVIEW_FIELDS,
                 REQUIRED_SAFETY_REVIEW_FIELDS,
                 REQUIRED_PLACEHOLDER_GUARD_REVIEW_FIELDS):
        assert len(coll) >= 1
        for item in coll:
            assert "placeholder" in item, item


# 22 -- pass / fail / rejection criteria are present and placeholder-only.

def test_pass_fail_rejection_criteria_present():
    c = _contract()
    assert tuple(c["review_pass_criteria"]) == REVIEW_PASS_CRITERIA
    assert tuple(c["review_fail_criteria"]) == REVIEW_FAIL_CRITERIA
    assert tuple(c["rejection_conditions"]) == REJECTION_CONDITIONS
    for coll in (REVIEW_PASS_CRITERIA, REVIEW_FAIL_CRITERIA,
                 REJECTION_CONDITIONS):
        assert len(coll) >= 1
        for item in coll:
            assert "placeholder" in item, item


# 23 -- blocked capabilities include the required set + review-specific ones.

def test_blocked_capabilities():
    c = _contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap
    assert "report_file_write" in blocked
    assert "report_renderer_result_review_execution" in blocked
    assert "fake_lane_closure_execution" in blocked
    assert "runtime_state_write" in blocked


# 24 -- no authorization flag can become True (any state).

def test_authorization_flags_always_false():
    states = [
        _contract(),
        _contract(decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT)),
        _contract(_blocked_renderer_state()),
        build_fake_report_renderer_result_review_contract({}),
    ]
    for c in states:
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["mode"] == "RESEARCH_ONLY"
        assert c["stage"] == "FAKE_RENDER_RESULT_REVIEW_ONLY"


# 25 -- even an active contract authorizes no data/runtime/report-write surface.

def test_active_contract_authorizes_no_runtime_or_report_write():
    c = _contract()
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["promotion_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["file_write_enabled"] is False
    assert c["safety_posture"]["automation_enabled"] is False
    blocked = set(c["blocked_capabilities"])
    assert "report_file_write" in blocked
    assert "runtime_state_write" in blocked
    assert "file_write" in blocked
    assert "file_read" in blocked


# 26 -- the embedded upstream renderer state is preserved.

def test_upstream_renderer_embedded():
    s = _active_renderer_state()
    c = build_fake_report_renderer_result_review_contract(s)
    assert (
        c["fake_report_renderer_in_memory"]["fake_report_renderer_active"]
        is True
    )
    assert c["fake_report_renderer_in_memory"]["read_only"] is True


# 27 -- validate passes for a clean contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _contract()
    v = validate_fake_report_renderer_result_review_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_fake_report_renderer_result_review_contract(
        bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_fake_report_renderer_result_review_contract(
        bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_fake_report_renderer_result_review_contract(
        bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["stage"] = "EXECUTE"
    assert validate_fake_report_renderer_result_review_contract(
        bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["human_approval_required"] = False
    assert validate_fake_report_renderer_result_review_contract(
        bad5)["valid"] is False


# 28 -- validate flags wrong field tuples.

def test_validate_flags_wrong_tuples():
    import copy
    c = _contract()
    for key in ("allowed_result_review_decisions",
                "required_rendered_result_fields",
                "required_report_section_review_fields",
                "required_safety_review_fields",
                "required_placeholder_guard_review_fields"):
        bad = copy.deepcopy(c)
        bad[key] = ("not", "the", "right", "tuple")
        assert validate_fake_report_renderer_result_review_contract(
            bad)["valid"] is False, key


# 29 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_contract())
    c.pop("validation", None)
    v = validate_fake_report_renderer_result_review_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 30 -- a blocked contract still validates (review safety, not activation).

def test_blocked_contract_still_validates():
    c = _contract(_blocked_renderer_state())
    v = validate_fake_report_renderer_result_review_contract(c)
    assert v["valid"] is True
    assert c["fake_report_renderer_result_review_contract_active"] is False


# 31 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    import copy
    c = copy.deepcopy(_contract())
    c.pop("fake_report_renderer_in_memory", None)
    v = validate_fake_report_renderer_result_review_contract(c)
    assert v["valid"] is False
    assert "fake_report_renderer_in_memory" in v["missing_required_fields"]


# 32 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_review_contract_only_and_execution_free():
    c = _contract()
    md = render_fake_report_renderer_result_review_contract_markdown(c)
    assert isinstance(md, str) and md
    assert (
        "# Strategy Factory Fake Report Renderer Result Review Contract" in md
    )
    for descriptor in ("fake-report-renderer-result-review-contract-only",
                       "review-only", "no-report-file-write",
                       "no-runtime-state-write", "research-only",
                       "execution-free"):
        assert descriptor in md, descriptor
    assert "Stage: FAKE_RENDER_RESULT_REVIEW_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "## Source Reference" in md
    assert "## Allowed Result Review Decisions" in md
    assert "## Required Rendered Result Fields" in md
    assert "## Required Report Section Review Fields" in md
    assert "## Required Safety Review Fields" in md
    assert "## Required Placeholder Guard Review Fields" in md
    assert "## Review Pass Criteria" in md
    assert "## Review Fail Criteria" in md
    assert "## Rejection Conditions" in md
    assert "## Blocked Capabilities" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 33 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 34 -- prose verb audit over notes / source ref / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _contract()

    texts.extend(str(x) for x in c["operator_notes"])
    texts.append(
        str(c["source_fake_report_renderer_result_reference_placeholder"]))

    md = render_fake_report_renderer_result_review_contract_markdown(c)
    for ln in md.splitlines():
        stripped = ln.lstrip()
        if stripped.startswith("#") or stripped.startswith("- `"):
            continue
        if stripped.startswith("- ") and "`" in stripped:
            continue
        if re.match(r"^[A-Za-z][A-Za-z0-9 ]*: ", stripped):
            continue
        texts.append(ln)

    for text in texts:
        upper = text.upper()
        for verb in _BAD_VERBS:
            assert not re.search(rf"\b{verb}\b", upper), (
                f"prose {text!r} contains forbidden verb {verb!r}"
            )


# 35 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 36 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_fake_report_renderer_result_review_contract.py"'  # noqa: E501
        in src
    )
    assert (
        '"tests/test_strategy_factory_fake_report_renderer_result_review_contract.py"'  # noqa: E501
        in src
    )


# 37 -- Bundle 38 regression import still works.

def test_bundle38_regression_import_still_works():
    s = build_fake_report_renderer_state({})
    assert s["executes"] is False
    assert s["read_only"] is True
    assert s["fake_report_renderer_active"] is False


# 38 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0

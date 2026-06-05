"""Bundle 40 tests for the Strategy Factory Fake Lane Closure Contract v1
(informational, read-only, fake-only, closure-contract-only, deterministic,
execution-free -- NO written report on disk, NO report file write, NO report
execution, NO real dry walk, NO orchestrator, NO real pipeline, NO smoke-test
run, NO runtime state write, NO research, NO data access, NO real strategy
intake).

This bundle defines the FINAL closure contract for the fake-only Strategy
Factory lane. It activates only from an active Bundle 39 fake report renderer
result review contract whose result_review_decision is
READY_FOR_FAKE_LANE_CLOSURE_CONTRACT and whose next_gate is
FAKE_LANE_CLOSURE_CONTRACT_REQUIRED.

Bundle 40's production module imports Bundles 11-39 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_fake_lane_closure_contract import (
    CLOSURE_SCHEMA_VERSION,
    DEFAULT_CLOSURE_LABEL,
    CLOSURE_STATUS,
    CLOSURE_SAFETY_POSTURE,
    CLOSURE_STATE_ACTIVE,
    CLOSURE_STATE_BLOCKED,
    CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR,
    CLOSURE_DECISION_NEEDS_FAKE_LANE_FIX,
    CLOSURE_DECISION_PARK_FAKE_LANE,
    CLOSURE_DECISION_REJECT_FAKE_LANE,
    ALLOWED_CLOSURE_DECISIONS,
    NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE,
    NEXT_GATE_FAKE_LANE_FIX_REQUIRED,
    NEXT_GATE_FAKE_LANE_PARKED,
    NEXT_GATE_FAKE_LANE_REJECTED,
    NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_DECISION,
    NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW,
    RECOMMENDED_NEXT_PHASE,
    COMPLETED_FAKE_LANE_SEGMENTS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    build_fake_lane_closure_contract,
    validate_fake_lane_closure_contract,
    render_fake_lane_closure_contract_markdown,
)
import sparta_commander.strategy_factory_fake_lane_closure_contract as CL
from sparta_commander.strategy_factory_fake_report_renderer_result_review_contract import (  # noqa: E501
    RESULT_REVIEW_SCHEMA_VERSION,
    RESULT_REVIEW_SAFETY_POSTURE,
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT,
    RESULT_REVIEW_DECISION_NEEDS_FAKE_REPORT_RENDER_FIX,
    build_fake_report_renderer_result_review_contract,
)
from sparta_commander.strategy_factory_fake_report_renderer_in_memory import (
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
    / "strategy_factory_fake_lane_closure_contract.py"
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
    "report_renderer_result_review_execution", "fake_lane_closure_execution",
    "real_strategy_intake", "runtime_state_write",
)

_EXPECTED_POSTURE_KEYS = {
    "automation_enabled", "live_execution_enabled", "paper_execution_enabled",
    "file_write_enabled", "network_enabled", "subprocess_enabled",
    "strategy_promotion_enabled", "broker_enabled", "exchange_enabled",
    "order_enabled", "data_fetch_enabled", "backtest_enabled",
    "upload_enabled", "autopilot_enabled",
}

_REQUIRED_SEGMENTS = (
    "fake_artifact_smoke_test_contract",
    "fake_artifact_dry_walk_contract",
    "fake_dry_walk_operator_review_gate",
    "fake_dry_walk_implementation_contract",
    "fake_dry_walk_in_memory_implementation",
    "fake_dry_walk_result_review_contract",
    "fake_walk_report_contract",
    "fake_walk_report_operator_review_gate",
    "fake_report_renderer_contract",
    "fake_report_renderer_in_memory_implementation",
    "fake_report_renderer_result_review_contract",
)


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


def _active_renderer_state(**kw) -> dict:
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
    contract = build_fake_report_renderer_contract(gate)
    return build_fake_report_renderer_state(contract, **kw)


def _blocked_renderer_state() -> dict:
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
    contract = build_fake_report_renderer_contract(gate)
    return build_fake_report_renderer_state(contract)


def _active_review_contract() -> dict:
    return build_fake_report_renderer_result_review_contract(
        _active_renderer_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT
        ),
    )


def _blocked_review_contract() -> dict:
    return build_fake_report_renderer_result_review_contract(
        _blocked_renderer_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT
        ),
    )


def _contract(review_contract=None, decision=None) -> dict:
    return build_fake_lane_closure_contract(
        review_contract if review_contract is not None
        else _active_review_contract(),
        closure_decision=decision,
    )


def _expected_public() -> set[str]:
    return {
        "CLOSURE_SCHEMA_VERSION",
        "DEFAULT_CLOSURE_LABEL",
        "CLOSURE_STATUS",
        "CLOSURE_SAFETY_POSTURE",
        "CLOSURE_STATE_ACTIVE",
        "CLOSURE_STATE_BLOCKED",
        "CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR",
        "CLOSURE_DECISION_NEEDS_FAKE_LANE_FIX",
        "CLOSURE_DECISION_PARK_FAKE_LANE",
        "CLOSURE_DECISION_REJECT_FAKE_LANE",
        "ALLOWED_CLOSURE_DECISIONS",
        "NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE",
        "NEXT_GATE_FAKE_LANE_FIX_REQUIRED",
        "NEXT_GATE_FAKE_LANE_PARKED",
        "NEXT_GATE_FAKE_LANE_REJECTED",
        "NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_DECISION",
        "NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW",
        "RECOMMENDED_NEXT_PHASE",
        "COMPLETED_FAKE_LANE_SEGMENTS",
        "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
        "build_fake_lane_closure_contract",
        "validate_fake_lane_closure_contract",
        "render_fake_lane_closure_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(CL.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(CL, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        CLOSURE_SCHEMA_VERSION
        == "strategy_factory_fake_lane_closure_contract.v1"
    )
    assert (
        DEFAULT_CLOSURE_LABEL == "Strategy Factory Fake Lane Closure Contract"
    )
    assert CLOSURE_STATUS == "READ_ONLY_FAKE_LANE_CLOSURE_CONTRACT"


# 3 -- state / next-gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert CLOSURE_STATE_ACTIVE == "FAKE_LANE_CLOSURE_CONTRACT_ACTIVE"
    assert CLOSURE_STATE_BLOCKED == "FAKE_LANE_CLOSURE_CONTRACT_BLOCKED"
    assert (
        NEXT_GATE_PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE
        == "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE"
    )
    assert NEXT_GATE_FAKE_LANE_FIX_REQUIRED == "FAKE_LANE_FIX_REQUIRED"
    assert NEXT_GATE_FAKE_LANE_PARKED == "FAKE_LANE_PARKED"
    assert NEXT_GATE_FAKE_LANE_REJECTED == "FAKE_LANE_REJECTED"
    assert (
        NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_DECISION
        == "AWAIT_FAKE_LANE_CLOSURE_DECISION"
    )
    assert (
        NEXT_GATE_AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW
        == "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW"
    )
    assert (
        RECOMMENDED_NEXT_PHASE
        == "OPERATOR_REVIEW_BEFORE_CRYPTO_D1_OR_REAL_STRATEGY_INTAKE"
    )


# 4 -- closure decision values are exactly the expected set.

def test_allowed_closure_decisions_exact():
    assert ALLOWED_CLOSURE_DECISIONS == (
        "FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR",
        "NEEDS_FAKE_LANE_FIX",
        "PARK_FAKE_LANE",
        "REJECT_FAKE_LANE",
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
    posture = CLOSURE_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 9 -- posture keys + values match Bundle 39.

def test_posture_matches_bundle39():
    assert CLOSURE_SAFETY_POSTURE == RESULT_REVIEW_SAFETY_POSTURE


# 10 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _contract()
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _contract()
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert CLOSURE_SAFETY_POSTURE["automation_enabled"] is False


# 11 -- an active Bundle 39 READY review contract activates closure.

def test_active_ready_review_activates_closure():
    c = _contract()
    assert c["fake_lane_closure_contract_active"] is True
    assert (
        c["fake_lane_closure_contract_state"]
        == "FAKE_LANE_CLOSURE_CONTRACT_ACTIVE"
    )
    assert c["fake_report_renderer_result_review_contract_active"] is True
    assert (
        c["fake_report_renderer_result_review_decision"]
        == "READY_FOR_FAKE_LANE_CLOSURE_CONTRACT"
    )
    assert (
        c["fake_report_renderer_result_review_next_gate"]
        == "FAKE_LANE_CLOSURE_CONTRACT_REQUIRED"
    )
    assert c["schema_version"] == CLOSURE_SCHEMA_VERSION
    assert (
        c["fake_report_renderer_result_review_schema_version"]
        == RESULT_REVIEW_SCHEMA_VERSION
    )
    # No closure decision yet -> awaiting decision.
    assert c["next_gate"] == "AWAIT_FAKE_LANE_CLOSURE_DECISION"
    # Recommended next phase defaults when active.
    assert c["recommended_next_phase"] == RECOMMENDED_NEXT_PHASE


# 12 -- a blocked (inactive) upstream review does not activate.

def test_blocked_review_does_not_activate():
    c = _contract(_blocked_review_contract())
    assert c["fake_lane_closure_contract_active"] is False
    assert (
        c["fake_lane_closure_contract_state"]
        == "FAKE_LANE_CLOSURE_CONTRACT_BLOCKED"
    )
    assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW"
    assert c["recommended_next_phase"] != RECOMMENDED_NEXT_PHASE


# 13 -- an active review but NOT-READY decision does not activate closure.

def test_not_ready_review_does_not_activate():
    not_ready = build_fake_report_renderer_result_review_contract(
        _active_renderer_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_NEEDS_FAKE_REPORT_RENDER_FIX
        ),
    )
    assert not_ready["next_gate"] != "FAKE_LANE_CLOSURE_CONTRACT_REQUIRED"
    c = _contract(not_ready)
    assert c["fake_lane_closure_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW"


# 14 -- active review but wrong next_gate does not activate.

def test_wrong_next_gate_does_not_activate():
    import copy
    r = copy.deepcopy(_active_review_contract())
    r["next_gate"] = "SOMETHING_ELSE"
    c = _contract(r)
    assert c["fake_lane_closure_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW"


# 15 -- inactive review flag does not activate even with right gate/decision.

def test_inactive_review_flag_does_not_activate():
    import copy
    r = copy.deepcopy(_active_review_contract())
    r["fake_report_renderer_result_review_contract_active"] = False
    c = _contract(r)
    assert c["fake_lane_closure_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW"


# 16 -- malformed input never raises and never activates.

def test_malformed_input_no_raise():
    for bad in (None, 42, "nope", {},
                {"fake_report_renderer_result_review_contract_active": True},
                []):
        c = build_fake_lane_closure_contract(bad)
        assert c["fake_lane_closure_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW"
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 17 -- FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR maps to the pause/operator gate.

def test_pause_decision_maps_to_operator_review_gate():
    c = _contract(decision=(
        CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR))
    assert c["fake_lane_closure_contract_active"] is True
    assert c["closure_decision"] == "FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR"
    assert (
        c["next_gate"]
        == "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE"
    )
    assert c["recommended_next_phase"] == RECOMMENDED_NEXT_PHASE


# 18 -- other decisions never unlock real strategy intake.

def test_other_decisions_never_unlock_real_intake():
    mapping = {
        CLOSURE_DECISION_NEEDS_FAKE_LANE_FIX: "FAKE_LANE_FIX_REQUIRED",
        CLOSURE_DECISION_PARK_FAKE_LANE: "FAKE_LANE_PARKED",
        CLOSURE_DECISION_REJECT_FAKE_LANE: "FAKE_LANE_REJECTED",
        None: "AWAIT_FAKE_LANE_CLOSURE_DECISION",
        "BOGUS_DECISION": "AWAIT_FAKE_LANE_CLOSURE_DECISION",
    }
    for decision, expected_gate in mapping.items():
        c = _contract(decision=decision)
        assert c["next_gate"] == expected_gate, decision
        assert (
            c["next_gate"]
            != "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE"
        )
        # No decision path ever flips a real-world capability on.
        assert "real_strategy_intake" in set(
            c["remaining_real_world_capabilities_blocked"])


# 19 -- a decision on a blocked review still cannot activate closure.

def test_decision_on_blocked_review_stays_blocked():
    c = _contract(
        _blocked_review_contract(),
        decision=CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR,
    )
    assert c["fake_lane_closure_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_REPORT_RENDERER_RESULT_REVIEW"


# 20 -- all required completed fake-lane segments are present and in order.

def test_required_completed_fake_lane_segments_present():
    c = _contract()
    assert (
        tuple(c["completed_fake_lane_segments"])
        == COMPLETED_FAKE_LANE_SEGMENTS
    )
    assert COMPLETED_FAKE_LANE_SEGMENTS == _REQUIRED_SEGMENTS
    for seg in _REQUIRED_SEGMENTS:
        assert seg in set(c["completed_fake_lane_segments"]), seg


# 21 -- recommended_next_phase is the operator-review phase when active.

def test_recommended_next_phase_when_active():
    c = _contract()
    assert (
        c["recommended_next_phase"]
        == "OPERATOR_REVIEW_BEFORE_CRYPTO_D1_OR_REAL_STRATEGY_INTAKE"
    )
    blocked = _contract(_blocked_review_contract())
    assert (
        blocked["recommended_next_phase"]
        != "OPERATOR_REVIEW_BEFORE_CRYPTO_D1_OR_REAL_STRATEGY_INTAKE"
    )


# 22 -- remaining real-world capabilities are still blocked.

def test_remaining_real_world_capabilities_blocked():
    c = _contract()
    remaining = set(c["remaining_real_world_capabilities_blocked"])
    for cap in ("real_strategy_intake", "real_data_load",
                "real_data_validation", "real_data_transform",
                "real_data_inspection", "real_data_compute",
                "real_qa_run", "real_baseline_run", "real_backtest",
                "real_simulation", "broker", "exchange", "order",
                "live_execution", "paper_execution", "autopilot",
                "automation", "upload", "deploy", "promotion"):
        assert cap in remaining, cap


# 23 -- blocked capabilities include the required set + closure-specific ones.

def test_blocked_capabilities():
    c = _contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap
    assert "report_file_write" in blocked
    assert "fake_lane_closure_execution" in blocked
    assert "real_strategy_intake" in blocked
    assert "runtime_state_write" in blocked
    fake_lane_blocked = set(c["fake_lane_blocked_capabilities"])
    assert "fake_lane_closure_execution" in fake_lane_blocked
    assert "real_strategy_intake" in fake_lane_blocked
    assert "report_file_write" in fake_lane_blocked
    assert "runtime_state_write" in fake_lane_blocked


# 24 -- no authorization flag can become True (any state).

def test_authorization_flags_always_false():
    states = [
        _contract(),
        _contract(decision=(
            CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR)),
        _contract(_blocked_review_contract()),
        build_fake_lane_closure_contract({}),
    ]
    for c in states:
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["mode"] == "RESEARCH_ONLY"
        assert c["stage"] == "FAKE_LANE_CLOSURE_ONLY"


# 25 -- even an active closure authorizes no data/runtime/report-write surface.

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
    assert "real_strategy_intake" in blocked
    assert "file_write" in blocked
    assert "file_read" in blocked


# 26 -- the embedded upstream review contract is preserved.

def test_upstream_review_embedded():
    r = _active_review_contract()
    c = build_fake_lane_closure_contract(r)
    embedded = c["fake_report_renderer_result_review_contract"]
    assert (
        embedded["fake_report_renderer_result_review_contract_active"] is True
    )
    assert embedded["read_only"] is True


# 27 -- validate passes for a clean contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _contract()
    v = validate_fake_lane_closure_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_fake_lane_closure_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_fake_lane_closure_contract(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_fake_lane_closure_contract(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["stage"] = "EXECUTE"
    assert validate_fake_lane_closure_contract(bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["human_approval_required"] = False
    assert validate_fake_lane_closure_contract(bad5)["valid"] is False


# 28 -- validate flags wrong field tuples / collections.

def test_validate_flags_wrong_collections():
    import copy
    c = _contract()
    for key in ("closure_decision_values",
                "completed_fake_lane_segments",
                "remaining_real_world_capabilities_blocked"):
        bad = copy.deepcopy(c)
        bad[key] = ("not", "the", "right", "tuple")
        assert validate_fake_lane_closure_contract(bad)["valid"] is False, key
    bad_summary = copy.deepcopy(c)
    bad_summary["fake_lane_completion_summary"] = {}
    assert validate_fake_lane_closure_contract(
        bad_summary)["valid"] is False
    bad_attest = copy.deepcopy(c)
    bad_attest["fake_lane_safety_attestation"] = {}
    assert validate_fake_lane_closure_contract(
        bad_attest)["valid"] is False


# 29 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_contract())
    c.pop("validation", None)
    v = validate_fake_lane_closure_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 30 -- a blocked contract still validates (closure safety, not activation).

def test_blocked_contract_still_validates():
    c = _contract(_blocked_review_contract())
    v = validate_fake_lane_closure_contract(c)
    assert v["valid"] is True
    assert c["fake_lane_closure_contract_active"] is False


# 31 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    import copy
    c = copy.deepcopy(_contract())
    c.pop("fake_report_renderer_result_review_contract", None)
    v = validate_fake_lane_closure_contract(c)
    assert v["valid"] is False
    assert (
        "fake_report_renderer_result_review_contract"
        in v["missing_required_fields"]
    )


# 32 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_closure_contract_only_and_execution_free():
    c = _contract()
    md = render_fake_lane_closure_contract_markdown(c)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Fake Lane Closure Contract" in md
    for descriptor in ("fake-lane-closure-contract-only",
                       "no-real-strategy-intake-yet", "no-report-file-write",
                       "no-runtime-state-write", "research-only",
                       "execution-free"):
        assert descriptor in md, descriptor
    assert "Stage: FAKE_LANE_CLOSURE_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "## Source Reference" in md
    assert "## Completed Fake Lane Segments" in md
    assert "## Closure Decision Values" in md
    assert "## Fake Lane Completion Summary" in md
    assert "## Fake Lane Safety Attestation" in md
    assert "## Fake Lane Blocked Capabilities" in md
    assert "## Remaining Real-World Capabilities Blocked" in md
    assert "## Blocked Capabilities" in md
    assert "## Human Operator Required Next Steps" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 33 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 34 -- prose verb audit over notes / next-steps / source ref / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _contract()

    texts.extend(str(x) for x in c["operator_notes"])
    texts.extend(str(x) for x in c["human_operator_required_next_steps"])
    texts.append(str(
        c["source_fake_report_renderer_result_review_reference_placeholder"]))

    md = render_fake_lane_closure_contract_markdown(c)
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
        '"sparta_commander/strategy_factory_fake_lane_closure_contract.py"'
        in src
    )
    assert (
        '"tests/test_strategy_factory_fake_lane_closure_contract.py"'
        in src
    )


# 37 -- Bundle 39 regression import still works.

def test_bundle39_regression_import_still_works():
    r = build_fake_report_renderer_result_review_contract({})
    assert r["executes"] is False
    assert r["read_only"] is True
    assert r["fake_report_renderer_result_review_contract_active"] is False


# 38 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0

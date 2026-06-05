"""Bundle 41 tests for the Strategy Factory Crypto-D1 Intake Reconciliation
Contract v1 (informational, read-only, paper-only, reconciliation-contract-only,
deterministic, execution-free -- NO written report on disk, NO report file
write, NO QA run, NO QA verdict, NO baseline run, NO backtest, NO data
inspection, NO dataset read, NO runtime state write, NO real strategy intake).

This bundle defines the first real-lane *paper reconciliation* contract for
Crypto-D1 intake. It activates only from an active Bundle 40 fake lane closure
contract whose closure_decision is FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR, whose
next_gate is PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE, and whose
recommended_next_phase is
OPERATOR_REVIEW_BEFORE_CRYPTO_D1_OR_REAL_STRATEGY_INTAKE.

Bundle 41's production module imports Bundles 11-40 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_crypto_d1_intake_reconciliation_contract import (  # noqa: E501
    CRYPTO_D1_SCHEMA_VERSION,
    DEFAULT_CRYPTO_D1_LABEL,
    CRYPTO_D1_STATUS,
    CRYPTO_D1_SAFETY_POSTURE,
    CRYPTO_D1_STATE_ACTIVE,
    CRYPTO_D1_STATE_BLOCKED,
    RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT,
    RECONCILIATION_DECISION_NEEDS_MORE_CRYPTO_D1_RECONCILIATION,
    RECONCILIATION_DECISION_PARK_CRYPTO_D1,
    RECONCILIATION_DECISION_REJECT_CRYPTO_D1,
    ALLOWED_RECONCILIATION_DECISIONS,
    NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED,
    NEXT_GATE_CRYPTO_D1_RECONCILIATION_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_RECONCILIATION_PARKED,
    NEXT_GATE_CRYPTO_D1_RECONCILIATION_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_DECISION,
    NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW,
    CRYPTO_D1_PENDING_ITEMS,
    CRYPTO_D1_METADATA_ITEMS,
    CRYPTO_D1_EXECUTION_ITEMS_DEFERRED,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    build_crypto_d1_intake_reconciliation_contract,
    validate_crypto_d1_intake_reconciliation_contract,
    render_crypto_d1_intake_reconciliation_contract_markdown,
)
import sparta_commander.strategy_factory_crypto_d1_intake_reconciliation_contract as CD  # noqa: E501
from sparta_commander.strategy_factory_fake_lane_closure_contract import (
    CLOSURE_SCHEMA_VERSION,
    CLOSURE_SAFETY_POSTURE,
    CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR,
    CLOSURE_DECISION_NEEDS_FAKE_LANE_FIX,
    build_fake_lane_closure_contract,
)
from sparta_commander.strategy_factory_fake_report_renderer_result_review_contract import (  # noqa: E501
    RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT,
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
    / "strategy_factory_crypto_d1_intake_reconciliation_contract.py"
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
    "runtime_safety_flag_write", "pipeline_execution", "report_file_write",
    "runtime_state_write", "real_strategy_intake",
)

_EXPECTED_POSTURE_KEYS = {
    "automation_enabled", "live_execution_enabled", "paper_execution_enabled",
    "file_write_enabled", "network_enabled", "subprocess_enabled",
    "strategy_promotion_enabled", "broker_enabled", "exchange_enabled",
    "order_enabled", "data_fetch_enabled", "backtest_enabled",
    "upload_enabled", "autopilot_enabled",
}

_EXPECTED_PENDING = (
    "operator_acquire_decision",
    "source_class",
    "source_name",
    "license_tos_evidence",
    "qa_run",
    "qa_pass_or_accepted_qa_warn",
    "baseline_backtest_output",
)


def _good_item() -> dict:
    return build_research_queue_item(
        "idea-001",
        "Opening Range Mean Reversion",
        "Price tends to revert toward the opening range midpoint intraday.",
        asset_lane="MNQ",
        timeframe="5m",
    )


def _ready_closure_report() -> dict:
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


def _blocked_closure_report() -> dict:
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
    smoke = build_fake_artifact_smoke_test_contract(_ready_closure_report())
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
    smoke = build_fake_artifact_smoke_test_contract(_blocked_closure_report())
    dry_walk = build_fake_artifact_dry_walk_contract(smoke)
    gate = build_fake_dry_walk_operator_review_gate(dry_walk)
    contract = build_fake_dry_walk_implementation_contract(gate)
    return build_fake_dry_walk_state(contract)


def _active_renderer_state() -> dict:
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
    return build_fake_report_renderer_state(contract)


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


def _active_closure() -> dict:
    return build_fake_lane_closure_contract(
        _active_review_contract(),
        closure_decision=CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR,
    )


def _blocked_closure() -> dict:
    return build_fake_lane_closure_contract(
        _blocked_review_contract(),
        closure_decision=CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR,
    )


def _contract(closure_contract=None, decision=None) -> dict:
    return build_crypto_d1_intake_reconciliation_contract(
        closure_contract if closure_contract is not None
        else _active_closure(),
        reconciliation_decision=decision,
    )


def _expected_public() -> set[str]:
    return {
        "CRYPTO_D1_SCHEMA_VERSION",
        "DEFAULT_CRYPTO_D1_LABEL",
        "CRYPTO_D1_STATUS",
        "CRYPTO_D1_SAFETY_POSTURE",
        "CRYPTO_D1_STATE_ACTIVE",
        "CRYPTO_D1_STATE_BLOCKED",
        "RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT",
        "RECONCILIATION_DECISION_NEEDS_MORE_CRYPTO_D1_RECONCILIATION",
        "RECONCILIATION_DECISION_PARK_CRYPTO_D1",
        "RECONCILIATION_DECISION_REJECT_CRYPTO_D1",
        "ALLOWED_RECONCILIATION_DECISIONS",
        "NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_RECONCILIATION_FIX_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_RECONCILIATION_PARKED",
        "NEXT_GATE_CRYPTO_D1_RECONCILIATION_REJECTED",
        "NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_DECISION",
        "NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW",
        "CRYPTO_D1_PENDING_ITEMS",
        "CRYPTO_D1_METADATA_ITEMS",
        "CRYPTO_D1_EXECUTION_ITEMS_DEFERRED",
        "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
        "build_crypto_d1_intake_reconciliation_contract",
        "validate_crypto_d1_intake_reconciliation_contract",
        "render_crypto_d1_intake_reconciliation_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(CD.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(CD, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        CRYPTO_D1_SCHEMA_VERSION
        == "strategy_factory_crypto_d1_intake_reconciliation_contract.v1"
    )
    assert (
        DEFAULT_CRYPTO_D1_LABEL
        == "Strategy Factory Crypto-D1 Intake Reconciliation Contract"
    )
    assert (
        CRYPTO_D1_STATUS == "READ_ONLY_CRYPTO_D1_INTAKE_RECONCILIATION_CONTRACT"
    )


# 3 -- state / next-gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        CRYPTO_D1_STATE_ACTIVE
        == "CRYPTO_D1_INTAKE_RECONCILIATION_CONTRACT_ACTIVE"
    )
    assert (
        CRYPTO_D1_STATE_BLOCKED
        == "CRYPTO_D1_INTAKE_RECONCILIATION_CONTRACT_BLOCKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED
        == "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_RECONCILIATION_FIX_REQUIRED
        == "CRYPTO_D1_RECONCILIATION_FIX_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_RECONCILIATION_PARKED
        == "CRYPTO_D1_RECONCILIATION_PARKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_RECONCILIATION_REJECTED
        == "CRYPTO_D1_RECONCILIATION_REJECTED"
    )
    assert (
        NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_DECISION
        == "AWAIT_CRYPTO_D1_RECONCILIATION_DECISION"
    )
    assert (
        NEXT_GATE_AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW
        == "AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW"
    )


# 4 -- reconciliation decision values are exactly the expected set.

def test_allowed_reconciliation_decisions_exact():
    assert ALLOWED_RECONCILIATION_DECISIONS == (
        "READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT",
        "NEEDS_MORE_CRYPTO_D1_RECONCILIATION",
        "PARK_CRYPTO_D1",
        "REJECT_CRYPTO_D1",
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
    posture = CRYPTO_D1_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 9 -- posture keys + values match Bundle 40.

def test_posture_matches_bundle40():
    assert CRYPTO_D1_SAFETY_POSTURE == CLOSURE_SAFETY_POSTURE


# 10 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _contract()
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _contract()
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert CRYPTO_D1_SAFETY_POSTURE["automation_enabled"] is False


# 11 -- an active Bundle 40 paused closure activates reconciliation.

def test_active_paused_closure_activates_reconciliation():
    c = _contract()
    assert c["crypto_d1_intake_reconciliation_contract_active"] is True
    assert (
        c["crypto_d1_intake_reconciliation_contract_state"]
        == "CRYPTO_D1_INTAKE_RECONCILIATION_CONTRACT_ACTIVE"
    )
    assert c["fake_lane_closure_contract_active"] is True
    assert (
        c["fake_lane_closure_decision"]
        == "FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR"
    )
    assert (
        c["fake_lane_closure_next_gate"]
        == "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE"
    )
    assert (
        c["fake_lane_recommended_next_phase"]
        == "OPERATOR_REVIEW_BEFORE_CRYPTO_D1_OR_REAL_STRATEGY_INTAKE"
    )
    assert c["schema_version"] == CRYPTO_D1_SCHEMA_VERSION
    assert c["fake_lane_closure_schema_version"] == CLOSURE_SCHEMA_VERSION
    # No reconciliation decision yet -> awaiting decision.
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_RECONCILIATION_DECISION"


# 12 -- a blocked (inactive) upstream closure does not activate.

def test_blocked_closure_does_not_activate():
    c = _contract(_blocked_closure())
    assert c["crypto_d1_intake_reconciliation_contract_active"] is False
    assert (
        c["crypto_d1_intake_reconciliation_contract_state"]
        == "CRYPTO_D1_INTAKE_RECONCILIATION_CONTRACT_BLOCKED"
    )
    assert c["next_gate"] == "AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW"


# 13 -- an active closure with a NON-pause decision does not activate.

def test_non_pause_closure_decision_does_not_activate():
    not_paused = build_fake_lane_closure_contract(
        _active_review_contract(),
        closure_decision=CLOSURE_DECISION_NEEDS_FAKE_LANE_FIX,
    )
    assert (
        not_paused["next_gate"]
        != "PAUSE_AND_OPERATOR_REVIEW_BEFORE_REAL_STRATEGY_INTAKE"
    )
    c = _contract(not_paused)
    assert c["crypto_d1_intake_reconciliation_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW"


# 14 -- active closure but wrong next_gate does not activate.

def test_wrong_next_gate_does_not_activate():
    import copy
    r = copy.deepcopy(_active_closure())
    r["next_gate"] = "SOMETHING_ELSE"
    c = _contract(r)
    assert c["crypto_d1_intake_reconciliation_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW"


# 15 -- active closure but wrong recommended phase does not activate.

def test_wrong_recommended_phase_does_not_activate():
    import copy
    r = copy.deepcopy(_active_closure())
    r["recommended_next_phase"] = "SOMETHING_ELSE"
    c = _contract(r)
    assert c["crypto_d1_intake_reconciliation_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW"


# 16 -- inactive closure flag does not activate even with right gate/decision.

def test_inactive_closure_flag_does_not_activate():
    import copy
    r = copy.deepcopy(_active_closure())
    r["fake_lane_closure_contract_active"] = False
    c = _contract(r)
    assert c["crypto_d1_intake_reconciliation_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW"


# 17 -- malformed input never raises and never activates.

def test_malformed_input_no_raise():
    for bad in (None, 42, "nope", {},
                {"fake_lane_closure_contract_active": True},
                []):
        c = build_crypto_d1_intake_reconciliation_contract(bad)
        assert c["crypto_d1_intake_reconciliation_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["next_gate"] == "AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW"
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 18 -- READY decision maps to the acquire-decision-contract gate.

def test_ready_decision_maps_to_acquire_decision_gate():
    c = _contract(decision=(
        RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT))
    assert c["crypto_d1_intake_reconciliation_contract_active"] is True
    assert (
        c["reconciliation_decision"]
        == "READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT"
    )
    assert c["next_gate"] == "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED"
    # Even READY never unlocks QA / baseline / backtest / real intake.
    remaining = set(c["remaining_real_world_capabilities_blocked"])
    assert "real_qa_run" in remaining
    assert "real_baseline_run" in remaining
    assert "real_backtest" in remaining
    assert "real_strategy_intake" in remaining


# 19 -- other decisions never unlock QA/baseline/backtest/real intake.

def test_other_decisions_never_unlock_execution():
    mapping = {
        RECONCILIATION_DECISION_NEEDS_MORE_CRYPTO_D1_RECONCILIATION:
            "CRYPTO_D1_RECONCILIATION_FIX_REQUIRED",
        RECONCILIATION_DECISION_PARK_CRYPTO_D1:
            "CRYPTO_D1_RECONCILIATION_PARKED",
        RECONCILIATION_DECISION_REJECT_CRYPTO_D1:
            "CRYPTO_D1_RECONCILIATION_REJECTED",
        None: "AWAIT_CRYPTO_D1_RECONCILIATION_DECISION",
        "BOGUS_DECISION": "AWAIT_CRYPTO_D1_RECONCILIATION_DECISION",
    }
    for decision, expected_gate in mapping.items():
        c = _contract(decision=decision)
        assert c["next_gate"] == expected_gate, decision
        assert (
            c["next_gate"] != "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED"
        )
        remaining = set(c["remaining_real_world_capabilities_blocked"])
        for cap in ("real_qa_run", "real_baseline_run", "real_backtest",
                    "real_strategy_intake"):
            assert cap in remaining, (decision, cap)


# 20 -- a decision on a blocked closure still cannot activate reconciliation.

def test_decision_on_blocked_closure_stays_blocked():
    c = _contract(
        _blocked_closure(),
        decision=(
            RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT
        ),
    )
    assert c["crypto_d1_intake_reconciliation_contract_active"] is False
    assert c["next_gate"] == "AWAIT_FAKE_LANE_CLOSURE_OPERATOR_REVIEW"


# 21 -- the seven pending items are present, exact, and in order.

def test_pending_items_exact_and_ordered():
    c = _contract()
    assert tuple(c["crypto_d1_pending_items"]) == CRYPTO_D1_PENDING_ITEMS
    assert CRYPTO_D1_PENDING_ITEMS == _EXPECTED_PENDING
    assert len(CRYPTO_D1_PENDING_ITEMS) == 7


# 22 -- metadata items are exactly the first four pending items.

def test_metadata_items_are_first_four():
    assert CRYPTO_D1_METADATA_ITEMS == _EXPECTED_PENDING[:4]
    assert CRYPTO_D1_METADATA_ITEMS == (
        "operator_acquire_decision",
        "source_class",
        "source_name",
        "license_tos_evidence",
    )
    c = _contract()
    assert tuple(c["crypto_d1_metadata_items"]) == CRYPTO_D1_METADATA_ITEMS
    # Required human operator fields equal the metadata (paper) fields.
    assert (
        tuple(c["required_human_operator_fields"]) == CRYPTO_D1_METADATA_ITEMS
    )


# 23 -- execution items deferred are exactly the last three pending items.

def test_execution_items_deferred_are_last_three():
    assert CRYPTO_D1_EXECUTION_ITEMS_DEFERRED == _EXPECTED_PENDING[4:]
    assert CRYPTO_D1_EXECUTION_ITEMS_DEFERRED == (
        "qa_run",
        "qa_pass_or_accepted_qa_warn",
        "baseline_backtest_output",
    )
    c = _contract()
    assert (
        tuple(c["crypto_d1_execution_items_deferred"])
        == CRYPTO_D1_EXECUTION_ITEMS_DEFERRED
    )
    # Metadata and execution items partition the pending items disjointly.
    assert set(CRYPTO_D1_METADATA_ITEMS).isdisjoint(
        set(CRYPTO_D1_EXECUTION_ITEMS_DEFERRED))
    assert (
        set(CRYPTO_D1_METADATA_ITEMS) | set(CRYPTO_D1_EXECUTION_ITEMS_DEFERRED)
        == set(CRYPTO_D1_PENDING_ITEMS)
    )


# 24 -- reconciliation status map: metadata pending, execution deferred.

def test_reconciliation_status_by_item():
    c = _contract()
    status = c["reconciliation_status_by_item"]
    assert isinstance(status, dict)
    for item in CRYPTO_D1_METADATA_ITEMS:
        assert status[item] == "pending_human_operator_metadata_placeholder"
    for item in CRYPTO_D1_EXECUTION_ITEMS_DEFERRED:
        assert status[item] == "blocked_and_deferred_placeholder"
    assert set(status.keys()) == set(CRYPTO_D1_PENDING_ITEMS)


# 25 -- no authorization flag can become True (any state).

def test_authorization_flags_always_false():
    states = [
        _contract(),
        _contract(decision=(
            RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT
        )),
        _contract(_blocked_closure()),
        build_crypto_d1_intake_reconciliation_contract({}),
    ]
    for c in states:
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["mode"] == "RESEARCH_ONLY"
        assert c["stage"] == "CRYPTO_D1_RECONCILIATION_ONLY"


# 26 -- even active reconciliation authorizes no data/qa/baseline/report write.

def test_active_contract_authorizes_no_execution_surface():
    c = _contract(decision=(
        RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT))
    assert c["data_fetch_authorized"] is False
    assert c["backtest_authorized"] is False
    assert c["execution_authorized"] is False
    assert c["promotion_authorized"] is False
    assert c["safety_posture"]["data_fetch_enabled"] is False
    assert c["safety_posture"]["backtest_enabled"] is False
    assert c["safety_posture"]["file_write_enabled"] is False
    assert c["safety_posture"]["automation_enabled"] is False
    blocked = set(c["blocked_capabilities"])
    for cap in ("crypto_d1_qa_run", "crypto_d1_baseline_run",
                "crypto_d1_backtest", "crypto_d1_dataset_read",
                "crypto_d1_data_inspection", "report_file_write",
                "runtime_state_write", "real_strategy_intake",
                "file_write", "file_read"):
        assert cap in blocked, cap
    crypto_blocked = set(c["crypto_d1_blocked_capabilities"])
    assert "crypto_d1_qa_run" in crypto_blocked
    assert "crypto_d1_baseline_run" in crypto_blocked
    assert "real_strategy_intake" in crypto_blocked


# 27 -- blocked capabilities include the required broad set.

def test_blocked_capabilities():
    c = _contract()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 28 -- remaining real-world capabilities are still blocked.

def test_remaining_real_world_capabilities_blocked():
    c = _contract()
    remaining = set(c["remaining_real_world_capabilities_blocked"])
    for cap in ("real_strategy_intake", "real_data_load",
                "real_data_validation", "real_data_transform",
                "real_data_inspection", "real_data_compute",
                "real_market_data_inspection", "real_qa_run",
                "real_baseline_run", "real_backtest", "real_simulation",
                "real_crypto_d1_dataset_inspection", "broker", "exchange",
                "order", "live_execution", "paper_execution", "autopilot",
                "automation", "upload", "deploy", "promotion"):
        assert cap in remaining, cap


# 29 -- the embedded upstream closure contract is preserved.

def test_upstream_closure_embedded():
    r = _active_closure()
    c = build_crypto_d1_intake_reconciliation_contract(r)
    embedded = c["fake_lane_closure_contract"]
    assert embedded["fake_lane_closure_contract_active"] is True
    assert embedded["read_only"] is True


# 30 -- validate passes for a clean contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _contract()
    v = validate_crypto_d1_intake_reconciliation_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_crypto_d1_intake_reconciliation_contract(
        bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_crypto_d1_intake_reconciliation_contract(
        bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_crypto_d1_intake_reconciliation_contract(
        bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["stage"] = "EXECUTE"
    assert validate_crypto_d1_intake_reconciliation_contract(
        bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["human_approval_required"] = False
    assert validate_crypto_d1_intake_reconciliation_contract(
        bad5)["valid"] is False


# 31 -- validate flags wrong field tuples / collections.

def test_validate_flags_wrong_collections():
    import copy
    c = _contract()
    for key in ("allowed_reconciliation_decisions",
                "crypto_d1_pending_items",
                "crypto_d1_metadata_items",
                "crypto_d1_execution_items_deferred",
                "remaining_real_world_capabilities_blocked"):
        bad = copy.deepcopy(c)
        bad[key] = ("not", "the", "right", "tuple")
        assert validate_crypto_d1_intake_reconciliation_contract(
            bad)["valid"] is False, key
    bad_status = copy.deepcopy(c)
    bad_status["reconciliation_status_by_item"] = {}
    assert validate_crypto_d1_intake_reconciliation_contract(
        bad_status)["valid"] is False


# 32 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_contract())
    c.pop("validation", None)
    v = validate_crypto_d1_intake_reconciliation_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 33 -- a blocked contract still validates (reconciliation safety shape).

def test_blocked_contract_still_validates():
    c = _contract(_blocked_closure())
    v = validate_crypto_d1_intake_reconciliation_contract(c)
    assert v["valid"] is True
    assert c["crypto_d1_intake_reconciliation_contract_active"] is False


# 34 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    import copy
    c = copy.deepcopy(_contract())
    c.pop("fake_lane_closure_contract", None)
    v = validate_crypto_d1_intake_reconciliation_contract(c)
    assert v["valid"] is False
    assert "fake_lane_closure_contract" in v["missing_required_fields"]


# 35 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_reconciliation_only_and_execution_free():
    c = _contract()
    md = render_crypto_d1_intake_reconciliation_contract_markdown(c)
    assert isinstance(md, str) and md
    assert (
        "# Strategy Factory Crypto-D1 Intake Reconciliation Contract" in md
    )
    for descriptor in ("crypto-d1-intake-reconciliation-contract-only",
                       "paper-only", "no-qa-run", "no-baseline-run",
                       "no-data-inspection", "no-real-strategy-intake-yet",
                       "research-only", "execution-free"):
        assert descriptor in md, descriptor
    assert "Stage: CRYPTO_D1_RECONCILIATION_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "## Source Reference" in md
    assert "## Crypto-D1 Pending Items" in md
    assert "## Crypto-D1 Metadata Items (Paper Fields)" in md
    assert "## Crypto-D1 Execution Items (Blocked And Deferred)" in md
    assert "## Reconciliation Status By Item" in md
    assert "## Required Human Operator Fields" in md
    assert "## Allowed Reconciliation Decisions" in md
    assert "## Crypto-D1 Blocked Capabilities" in md
    assert "## Remaining Real-World Capabilities Blocked" in md
    assert "## Blocked Capabilities" in md
    assert "## Human Operator Required Next Steps" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 36 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 37 -- prose verb audit over notes / next-steps / source ref / markdown prose.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _contract()

    texts.extend(str(x) for x in c["operator_notes"])
    texts.extend(str(x) for x in c["human_operator_required_next_steps"])
    texts.append(str(c["source_fake_lane_closure_reference_placeholder"]))

    md = render_crypto_d1_intake_reconciliation_contract_markdown(c)
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


# 38 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 39 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_crypto_d1_intake_reconciliation_contract.py"'  # noqa: E501
        in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_intake_reconciliation_contract.py"'  # noqa: E501
        in src
    )


# 40 -- Bundle 40 regression import still works.

def test_bundle40_regression_import_still_works():
    r = build_fake_lane_closure_contract({})
    assert r["executes"] is False
    assert r["read_only"] is True
    assert r["fake_lane_closure_contract_active"] is False


# 41 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0

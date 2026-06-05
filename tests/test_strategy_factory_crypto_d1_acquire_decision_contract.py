"""Bundle 42 tests for the Strategy Factory Crypto-D1 Acquire Decision
Contract v1 (informational, read-only, paper-only,
acquire-decision-contract-only, deterministic, execution-free -- NO written
report on disk, NO report file write, NO data acquisition, NO data inspection,
NO QA run, NO QA verdict, NO baseline run, NO backtest, NO runtime state write,
NO real strategy intake).

This bundle defines the first real-lane *paper acquire-decision* contract for
the Crypto-D1 source. It activates only from an active Bundle 41 crypto-d1
intake reconciliation contract whose reconciliation_decision is
READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT and whose next_gate is
CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED.

Bundle 42's production module imports Bundles 11-41 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_crypto_d1_acquire_decision_contract import (  # noqa: E501
    ACQUIRE_SCHEMA_VERSION,
    DEFAULT_ACQUIRE_LABEL,
    ACQUIRE_STATUS,
    ACQUIRE_SAFETY_POSTURE,
    ACQUIRE_STATE_ACTIVE,
    ACQUIRE_STATE_BLOCKED,
    ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT,
    ACQUIRE_DECISION_NEEDS_MORE_INFO,
    ACQUIRE_DECISION_PARKED,
    ACQUIRE_DECISION_REJECTED,
    ALLOWED_ACQUIRE_DECISIONS,
    NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED,
    NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_PARKED,
    NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION,
    NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT,
    REQUIRED_OPERATOR_DECISION_FIELDS,
    REQUIRED_OPERATOR_ATTESTATION_FIELDS,
    BLOCKED_EXECUTION_ITEMS,
    REMAINING_PENDING_ITEMS_AFTER_DECISION,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    build_crypto_d1_acquire_decision_contract,
    validate_crypto_d1_acquire_decision_contract,
    render_crypto_d1_acquire_decision_contract_markdown,
)
import sparta_commander.strategy_factory_crypto_d1_acquire_decision_contract as AQ  # noqa: E501
from sparta_commander.strategy_factory_crypto_d1_intake_reconciliation_contract import (  # noqa: E501
    CRYPTO_D1_SCHEMA_VERSION,
    CRYPTO_D1_SAFETY_POSTURE,
    RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT,
    RECONCILIATION_DECISION_PARK_CRYPTO_D1,
    build_crypto_d1_intake_reconciliation_contract,
)
from sparta_commander.strategy_factory_fake_lane_closure_contract import (
    CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR,
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
    / "strategy_factory_crypto_d1_acquire_decision_contract.py"
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

_EXPECTED_PENDING_AFTER = (
    "source_class",
    "source_name",
    "license_tos_evidence",
    "qa_run",
    "qa_pass_or_accepted_qa_warn",
    "baseline_backtest_output",
)

_EXPECTED_BLOCKED_EXECUTION = (
    "qa_run",
    "qa_pass_or_accepted_qa_warn",
    "baseline_backtest_output",
)


# --- upstream fake-lane chain helpers (reused from Bundle 41 test) --------

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


# --- Bundle 41 reconciliation helpers (upstream of this bundle) -----------

def _ready_recon() -> dict:
    """Active reconciliation contract at the acquire-decision gate."""
    return build_crypto_d1_intake_reconciliation_contract(
        _active_closure(),
        reconciliation_decision=(
            RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT
        ),
    )


def _await_recon() -> dict:
    """Active reconciliation but no decision -> not at the acquire gate."""
    return build_crypto_d1_intake_reconciliation_contract(_active_closure())


def _parked_recon() -> dict:
    """Active reconciliation parked -> not at the acquire gate."""
    return build_crypto_d1_intake_reconciliation_contract(
        _active_closure(),
        reconciliation_decision=RECONCILIATION_DECISION_PARK_CRYPTO_D1,
    )


def _blocked_recon() -> dict:
    """Inactive reconciliation (upstream closure was blocked)."""
    return build_crypto_d1_intake_reconciliation_contract(_blocked_closure())


def _acq(recon=None, decision=None) -> dict:
    return build_crypto_d1_acquire_decision_contract(
        recon if recon is not None else _ready_recon(),
        acquire_decision=decision,
    )


def _expected_public() -> set[str]:
    return {
        "ACQUIRE_SCHEMA_VERSION",
        "DEFAULT_ACQUIRE_LABEL",
        "ACQUIRE_STATUS",
        "ACQUIRE_SAFETY_POSTURE",
        "ACQUIRE_STATE_ACTIVE",
        "ACQUIRE_STATE_BLOCKED",
        "ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT",
        "ACQUIRE_DECISION_NEEDS_MORE_INFO",
        "ACQUIRE_DECISION_PARKED",
        "ACQUIRE_DECISION_REJECTED",
        "ALLOWED_ACQUIRE_DECISIONS",
        "NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_FIX_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_PARKED",
        "NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_REJECTED",
        "NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION",
        "NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT",
        "REQUIRED_OPERATOR_DECISION_FIELDS",
        "REQUIRED_OPERATOR_ATTESTATION_FIELDS",
        "BLOCKED_EXECUTION_ITEMS",
        "REMAINING_PENDING_ITEMS_AFTER_DECISION",
        "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
        "build_crypto_d1_acquire_decision_contract",
        "validate_crypto_d1_acquire_decision_contract",
        "render_crypto_d1_acquire_decision_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(AQ.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(AQ, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        ACQUIRE_SCHEMA_VERSION
        == "strategy_factory_crypto_d1_acquire_decision_contract.v1"
    )
    assert (
        DEFAULT_ACQUIRE_LABEL
        == "Strategy Factory Crypto-D1 Acquire Decision Contract"
    )
    assert ACQUIRE_STATUS == "READ_ONLY_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT"


# 3 -- state / next-gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        ACQUIRE_STATE_ACTIVE
        == "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_ACTIVE"
    )
    assert (
        ACQUIRE_STATE_BLOCKED
        == "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_BLOCKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED
        == "CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_FIX_REQUIRED
        == "CRYPTO_D1_ACQUIRE_DECISION_FIX_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_PARKED
        == "CRYPTO_D1_ACQUIRE_DECISION_PARKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_ACQUIRE_DECISION_REJECTED
        == "CRYPTO_D1_ACQUIRE_DECISION_REJECTED"
    )
    assert (
        NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION
        == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"
    )
    assert (
        NEXT_GATE_AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT
        == "AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT"
    )


# 4 -- acquire decision values are exactly the expected set.

def test_allowed_acquire_decisions_exact():
    assert ALLOWED_ACQUIRE_DECISIONS == (
        "ACQUIRE_APPROVED_FOR_SOURCE_CLASS_CONTRACT",
        "ACQUIRE_NEEDS_MORE_INFO",
        "ACQUIRE_PARKED",
        "ACQUIRE_REJECTED",
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
    posture = ACQUIRE_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 9 -- posture keys + values match Bundle 41.

def test_posture_matches_bundle41():
    assert ACQUIRE_SAFETY_POSTURE == CRYPTO_D1_SAFETY_POSTURE


# 10 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _acq()
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _acq()
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert ACQUIRE_SAFETY_POSTURE["automation_enabled"] is False


# 11 -- an active Bundle 41 READY reconciliation activates the acquire contract.

def test_active_ready_reconciliation_activates_acquire():
    c = _acq()
    assert c["crypto_d1_acquire_decision_contract_active"] is True
    assert (
        c["crypto_d1_acquire_decision_contract_state"]
        == "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_ACTIVE"
    )
    assert c["crypto_d1_intake_reconciliation_contract_active"] is True
    assert (
        c["crypto_d1_intake_reconciliation_decision"]
        == "READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT"
    )
    assert (
        c["crypto_d1_intake_reconciliation_next_gate"]
        == "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED"
    )
    assert c["schema_version"] == ACQUIRE_SCHEMA_VERSION
    assert (
        c["crypto_d1_intake_reconciliation_schema_version"]
        == CRYPTO_D1_SCHEMA_VERSION
    )
    # No acquire decision yet -> awaiting decision.
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"


# 12 -- a blocked (inactive) reconciliation does not activate.

def test_blocked_reconciliation_does_not_activate():
    c = _acq(_blocked_recon())
    assert c["crypto_d1_acquire_decision_contract_active"] is False
    assert (
        c["crypto_d1_acquire_decision_contract_state"]
        == "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_BLOCKED"
    )
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT"


# 13 -- an active reconciliation with no decision (wrong gate) does not activate.

def test_await_reconciliation_does_not_activate():
    recon = _await_recon()
    assert recon["crypto_d1_intake_reconciliation_contract_active"] is True
    assert recon["next_gate"] != "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED"
    c = _acq(recon)
    assert c["crypto_d1_acquire_decision_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT"


# 14 -- a non-READY (parked) reconciliation decision does not activate.

def test_non_ready_reconciliation_decision_does_not_activate():
    recon = _parked_recon()
    assert recon["crypto_d1_intake_reconciliation_contract_active"] is True
    assert recon["next_gate"] != "CRYPTO_D1_ACQUIRE_DECISION_CONTRACT_REQUIRED"
    c = _acq(recon)
    assert c["crypto_d1_acquire_decision_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT"


# 15 -- active READY reconciliation but tampered next_gate does not activate.

def test_wrong_reconciliation_next_gate_does_not_activate():
    import copy
    r = copy.deepcopy(_ready_recon())
    r["next_gate"] = "SOMETHING_ELSE"
    c = _acq(r)
    assert c["crypto_d1_acquire_decision_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT"


# 16 -- inactive reconciliation flag does not activate even with right gate.

def test_inactive_reconciliation_flag_does_not_activate():
    import copy
    r = copy.deepcopy(_ready_recon())
    r["crypto_d1_intake_reconciliation_contract_active"] = False
    c = _acq(r)
    assert c["crypto_d1_acquire_decision_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT"


# 17 -- malformed input never raises and never activates.

def test_malformed_input_no_raise():
    for bad in (None, 42, "nope", {},
                {"crypto_d1_intake_reconciliation_contract_active": True},
                []):
        c = build_crypto_d1_acquire_decision_contract(bad)
        assert c["crypto_d1_acquire_decision_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["next_gate"] == "AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT"
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 18 -- APPROVED decision maps to the source-class-contract gate.

def test_approved_decision_maps_to_source_class_gate():
    c = _acq(decision=ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT)
    assert c["crypto_d1_acquire_decision_contract_active"] is True
    assert c["acquire_decision"] == "ACQUIRE_APPROVED_FOR_SOURCE_CLASS_CONTRACT"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED"
    # Even APPROVED never unlocks QA / baseline / backtest / real intake.
    remaining = set(c["remaining_real_world_capabilities_blocked"])
    for cap in ("real_qa_run", "real_baseline_run", "real_backtest",
                "real_strategy_intake", "real_data_acquisition",
                "real_data_inspection"):
        assert cap in remaining, cap


# 19 -- other decisions never unlock QA/baseline/backtest/real intake.

def test_other_decisions_never_unlock_execution():
    mapping = {
        ACQUIRE_DECISION_NEEDS_MORE_INFO:
            "CRYPTO_D1_ACQUIRE_DECISION_FIX_REQUIRED",
        ACQUIRE_DECISION_PARKED: "CRYPTO_D1_ACQUIRE_DECISION_PARKED",
        ACQUIRE_DECISION_REJECTED: "CRYPTO_D1_ACQUIRE_DECISION_REJECTED",
        None: "AWAIT_CRYPTO_D1_ACQUIRE_DECISION",
        "BOGUS_DECISION": "AWAIT_CRYPTO_D1_ACQUIRE_DECISION",
    }
    for decision, expected_gate in mapping.items():
        c = _acq(decision=decision)
        assert c["next_gate"] == expected_gate, decision
        assert c["next_gate"] != "CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED"
        remaining = set(c["remaining_real_world_capabilities_blocked"])
        for cap in ("real_qa_run", "real_baseline_run", "real_backtest",
                    "real_strategy_intake"):
            assert cap in remaining, (decision, cap)
        blocked = set(c["blocked_capabilities"])
        for cap in ("crypto_d1_qa_run", "crypto_d1_baseline_run",
                    "crypto_d1_backtest", "crypto_d1_data_inspection"):
            assert cap in blocked, (decision, cap)


# 20 -- a decision on a blocked reconciliation still cannot activate.

def test_decision_on_blocked_reconciliation_stays_blocked():
    c = _acq(
        _blocked_recon(),
        decision=ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT,
    )
    assert c["crypto_d1_acquire_decision_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_RECONCILIATION_CONTRACT"


# 21 -- remaining pending items after the decision are exact + ordered.

def test_remaining_pending_items_after_decision_exact():
    c = _acq()
    assert (
        tuple(c["remaining_pending_items_after_decision"])
        == REMAINING_PENDING_ITEMS_AFTER_DECISION
    )
    assert REMAINING_PENDING_ITEMS_AFTER_DECISION == _EXPECTED_PENDING_AFTER
    assert len(REMAINING_PENDING_ITEMS_AFTER_DECISION) == 6


# 22 -- blocked execution items are exactly the three deferred items.

def test_blocked_execution_items_exact():
    c = _acq()
    assert tuple(c["blocked_execution_items"]) == BLOCKED_EXECUTION_ITEMS
    assert BLOCKED_EXECUTION_ITEMS == _EXPECTED_BLOCKED_EXECUTION
    # The deferred execution items are a subset of the remaining pending items.
    assert set(BLOCKED_EXECUTION_ITEMS).issubset(
        set(REMAINING_PENDING_ITEMS_AFTER_DECISION))


# 23 -- acquire-specific blocked capabilities are present.

def test_acquire_blocked_capabilities_present():
    c = _acq()
    acquire_blocked = set(c["acquire_blocked_capabilities"])
    for cap in ("crypto_d1_acquire_decision_execution",
                "crypto_d1_data_acquisition", "crypto_d1_dataset_read",
                "crypto_d1_data_inspection", "crypto_d1_qa_run",
                "crypto_d1_baseline_run", "crypto_d1_backtest",
                "real_strategy_intake", "report_file_write",
                "runtime_state_write"):
        assert cap in acquire_blocked, cap


# 24 -- no authorization flag can become True (any state).

def test_authorization_flags_always_false():
    states = [
        _acq(),
        _acq(decision=ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT),
        _acq(_blocked_recon()),
        build_crypto_d1_acquire_decision_contract({}),
    ]
    for c in states:
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["mode"] == "RESEARCH_ONLY"
        assert c["stage"] == "CRYPTO_D1_ACQUIRE_DECISION_ONLY"


# 25 -- even an approved acquire authorizes no data/qa/baseline/report write.

def test_active_contract_authorizes_no_execution_surface():
    c = _acq(decision=ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT)
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
                "crypto_d1_data_inspection", "crypto_d1_data_acquisition",
                "report_file_write", "runtime_state_write",
                "real_strategy_intake", "file_write", "file_read"):
        assert cap in blocked, cap


# 26 -- blocked capabilities include the required broad set.

def test_blocked_capabilities():
    c = _acq()
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 27 -- remaining real-world capabilities are still blocked.

def test_remaining_real_world_capabilities_blocked():
    c = _acq()
    remaining = set(c["remaining_real_world_capabilities_blocked"])
    for cap in ("real_strategy_intake", "real_data_acquisition",
                "real_data_load", "real_data_validation",
                "real_data_transform", "real_data_inspection",
                "real_data_compute", "real_market_data_inspection",
                "real_crypto_d1_dataset_inspection", "real_qa_run",
                "real_baseline_run", "real_backtest", "real_simulation",
                "real_data_fetch", "broker", "exchange", "order",
                "live_execution", "paper_execution", "autopilot",
                "automation", "upload", "deploy", "promotion"):
        assert cap in remaining, cap
    assert (
        tuple(c["remaining_real_world_capabilities_blocked"])
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


# 28 -- required operator decision + attestation fields are pinned.

def test_required_operator_fields_pinned():
    c = _acq()
    assert (
        tuple(c["required_operator_decision_fields"])
        == REQUIRED_OPERATOR_DECISION_FIELDS
    )
    assert REQUIRED_OPERATOR_DECISION_FIELDS == (
        "operator_acquire_decision",
        "acquire_decision_rationale",
        "source_class_intent",
    )
    assert (
        tuple(c["required_operator_attestation_fields"])
        == REQUIRED_OPERATOR_ATTESTATION_FIELDS
    )
    assert REQUIRED_OPERATOR_ATTESTATION_FIELDS == (
        "human_operator_identity_attestation",
        "no_data_acquired_attestation",
        "no_data_inspected_attestation",
        "no_qa_run_attestation",
        "no_baseline_run_attestation",
        "read_only_attestation",
    )


# 29 -- the embedded upstream reconciliation contract is preserved.

def test_upstream_reconciliation_embedded():
    recon = _ready_recon()
    c = build_crypto_d1_acquire_decision_contract(recon)
    embedded = c["crypto_d1_intake_reconciliation_contract"]
    assert embedded["crypto_d1_intake_reconciliation_contract_active"] is True
    assert embedded["read_only"] is True


# 30 -- validate passes for a clean contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _acq()
    v = validate_crypto_d1_acquire_decision_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_crypto_d1_acquire_decision_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_crypto_d1_acquire_decision_contract(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_crypto_d1_acquire_decision_contract(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["stage"] = "EXECUTE"
    assert validate_crypto_d1_acquire_decision_contract(bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["human_approval_required"] = False
    assert validate_crypto_d1_acquire_decision_contract(bad5)["valid"] is False


# 31 -- validate flags wrong field tuples / collections.

def test_validate_flags_wrong_collections():
    import copy
    c = _acq()
    for key in ("allowed_acquire_decisions",
                "required_operator_decision_fields",
                "required_operator_attestation_fields",
                "blocked_execution_items",
                "remaining_pending_items_after_decision",
                "remaining_real_world_capabilities_blocked"):
        bad = copy.deepcopy(c)
        bad[key] = ("not", "the", "right", "tuple")
        assert validate_crypto_d1_acquire_decision_contract(
            bad)["valid"] is False, key


# 32 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_acq())
    c.pop("validation", None)
    v = validate_crypto_d1_acquire_decision_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 33 -- a blocked contract still validates (acquire safety shape).

def test_blocked_contract_still_validates():
    c = _acq(_blocked_recon())
    v = validate_crypto_d1_acquire_decision_contract(c)
    assert v["valid"] is True
    assert c["crypto_d1_acquire_decision_contract_active"] is False


# 34 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    import copy
    c = copy.deepcopy(_acq())
    c.pop("crypto_d1_intake_reconciliation_contract", None)
    v = validate_crypto_d1_acquire_decision_contract(c)
    assert v["valid"] is False
    assert (
        "crypto_d1_intake_reconciliation_contract"
        in v["missing_required_fields"]
    )


# 35 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_acquire_only_and_execution_free():
    c = _acq()
    md = render_crypto_d1_acquire_decision_contract_markdown(c)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Crypto-D1 Acquire Decision Contract" in md
    for descriptor in ("crypto-d1-acquire-decision-contract-only",
                       "paper-only", "no-data-acquisition", "no-qa-run",
                       "no-baseline-run", "no-data-inspection",
                       "no-real-strategy-intake-yet", "research-only",
                       "execution-free"):
        assert descriptor in md, descriptor
    assert "Stage: CRYPTO_D1_ACQUIRE_DECISION_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "## Source Reference" in md
    assert "## Allowed Acquire Decisions" in md
    assert "## Required Operator Decision Fields" in md
    assert "## Required Operator Attestation Fields" in md
    assert "## Acquire Decision Rationale" in md
    assert "## Blocked Execution Items" in md
    assert "## Remaining Pending Items After Decision" in md
    assert "## Crypto-D1 Acquire Blocked Capabilities" in md
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


# 37 -- prose verb audit over notes / next-steps / placeholders / markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _acq()

    texts.extend(str(x) for x in c["operator_notes"])
    texts.extend(str(x) for x in c["human_operator_required_next_steps"])
    texts.append(
        str(c["source_reconciliation_contract_reference_placeholder"]))
    texts.append(str(c["acquire_decision_rationale_placeholder"]))

    md = render_crypto_d1_acquire_decision_contract_markdown(c)
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
        '"sparta_commander/strategy_factory_crypto_d1_acquire_decision_contract.py"'  # noqa: E501
        in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_acquire_decision_contract.py"'
        in src
    )


# 40 -- Bundle 41 regression import still works.

def test_bundle41_regression_import_still_works():
    r = build_crypto_d1_intake_reconciliation_contract({})
    assert r["executes"] is False
    assert r["read_only"] is True
    assert r["crypto_d1_intake_reconciliation_contract_active"] is False


# 41 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0

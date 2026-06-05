"""Bundle 43 tests for the Strategy Factory Crypto-D1 Source Class Contract
v1 (informational, read-only, paper-only, source-class-contract-only,
offline-spec-only, deterministic, execution-free -- NO written report on disk,
NO report file write, NO data acquisition, NO data inspection, NO live API, NO
exchange/broker connection, NO QA run, NO QA verdict, NO baseline run, NO
backtest, NO runtime state write, NO real strategy intake).

This bundle defines the first crypto-d1 *source-class* evaluation contract. It
activates only from an active Bundle 42 crypto-d1 acquire decision contract
whose acquire_decision is ACQUIRE_APPROVED_FOR_SOURCE_CLASS_CONTRACT and whose
next_gate is CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED. When active, it evaluates
a paper source-class proposal dict and returns a deterministic verdict; it
acquires no data and unlocks nothing real.

Bundle 43's production module imports Bundles 11-42 via real package imports,
so these tests use normal package imports too. Running under
``python -m pytest`` places the repo root on ``sys.path`` so
``sparta_commander`` resolves.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_crypto_d1_source_class_contract import (  # noqa: E501
    SOURCE_CLASS_SCHEMA_VERSION,
    DEFAULT_SOURCE_CLASS_LABEL,
    SOURCE_CLASS_STATUS,
    SOURCE_CLASS_SAFETY_POSTURE,
    SOURCE_CLASS_STATE_ACTIVE,
    SOURCE_CLASS_STATE_BLOCKED,
    SOURCE_CLASS_VERDICT_APPROVED,
    SOURCE_CLASS_VERDICT_NEEDS_MORE_INFO,
    SOURCE_CLASS_VERDICT_PARKED,
    SOURCE_CLASS_VERDICT_REJECTED,
    SOURCE_CLASS_VERDICT_AWAIT,
    ALLOWED_SOURCE_CLASS_VERDICTS,
    NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED,
    NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_PARKED,
    NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION,
    REQUIRED_SOURCE_CLASS_FIELDS,
    ALLOWED_ASSET_UNIVERSE,
    PARKED_MARKET_TYPES,
    ALLOWED_VENUE_CLASSES,
    ALLOWED_SOURCE_ACCESS_MODES,
    REQUIRED_CANDLE_FIELDS,
    ALLOWED_TIMEFRAME,
    FORBIDDEN_SOURCE_CLASS_CAPABILITIES,
    BLOCKED_EXECUTION_ITEMS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_source_class_proposal,
    build_crypto_d1_source_class_contract,
    validate_crypto_d1_source_class_contract,
    render_crypto_d1_source_class_contract_markdown,
)
import sparta_commander.strategy_factory_crypto_d1_source_class_contract as SC  # noqa: E501
from sparta_commander.strategy_factory_crypto_d1_acquire_decision_contract import (  # noqa: E501
    ACQUIRE_SCHEMA_VERSION,
    ACQUIRE_SAFETY_POSTURE,
    ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT,
    ACQUIRE_DECISION_NEEDS_MORE_INFO,
    build_crypto_d1_acquire_decision_contract,
)
from sparta_commander.strategy_factory_crypto_d1_intake_reconciliation_contract import (  # noqa: E501
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
    / "strategy_factory_crypto_d1_source_class_contract.py"
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

_EXPECTED_BLOCKED_EXECUTION = (
    "qa_run",
    "qa_pass_or_accepted_qa_warn",
    "baseline_backtest_output",
)

_EXPECTED_REQUIRED_FIELDS = (
    "asset_universe",
    "market_type",
    "venue_class",
    "source_access_mode",
    "timeframe",
    "candle_schema",
    "fee_model_presence",
    "coverage_window",
    "reproducibility",
    "provenance_required",
    "checksum_required",
    "session_rule",
)

_EXPECTED_CANDLE_FIELDS = (
    "timestamp", "open", "high", "low", "close", "volume",
)


# --- upstream fake-lane chain helpers (reused from Bundle 42 test) --------

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


# --- Bundle 41 reconciliation helpers -------------------------------------

def _ready_recon() -> dict:
    return build_crypto_d1_intake_reconciliation_contract(
        _active_closure(),
        reconciliation_decision=(
            RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT
        ),
    )


def _parked_recon() -> dict:
    return build_crypto_d1_intake_reconciliation_contract(
        _active_closure(),
        reconciliation_decision=RECONCILIATION_DECISION_PARK_CRYPTO_D1,
    )


def _blocked_recon() -> dict:
    return build_crypto_d1_intake_reconciliation_contract(_blocked_closure())


# --- Bundle 42 acquire-decision helpers (upstream of this bundle) ---------

def _approved_acq() -> dict:
    """Active acquire contract APPROVED at the source-class gate."""
    return build_crypto_d1_acquire_decision_contract(
        _ready_recon(),
        acquire_decision=ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT,
    )


def _await_acq() -> dict:
    """Active acquire contract with no decision -> not at source-class gate."""
    return build_crypto_d1_acquire_decision_contract(_ready_recon())


def _needs_more_acq() -> dict:
    """Active acquire contract NEEDS_MORE_INFO -> not at source-class gate."""
    return build_crypto_d1_acquire_decision_contract(
        _ready_recon(),
        acquire_decision=ACQUIRE_DECISION_NEEDS_MORE_INFO,
    )


def _blocked_acq() -> dict:
    """Inactive acquire contract (upstream reconciliation was blocked)."""
    return build_crypto_d1_acquire_decision_contract(
        _blocked_recon(),
        acquire_decision=ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT,
    )


# --- source-class proposal helpers ----------------------------------------

def _approved_proposal() -> dict:
    return {
        "asset_universe": ["BTC", "ETH", "SOL"],
        "market_type": "spot",
        "venue_class": "vendor_historical_candles",
        "source_access_mode": "offline_fixture",
        "timeframe": "D1",
        "candle_schema": [
            "timestamp", "open", "high", "low", "close", "volume",
        ],
        "fee_model_presence": True,
        "coverage_window": {"start": "2019-01-01", "end": "2025-01-01"},
        "reproducibility": True,
        "provenance_required": True,
        "checksum_required": True,
        "session_rule": "UTC daily candles",
    }


def _perps_proposal() -> dict:
    p = _approved_proposal()
    p["market_type"] = "perp"
    return p


def _live_api_proposal() -> dict:
    p = _approved_proposal()
    p["source_access_mode"] = "live_api"
    return p


def _api_keys_proposal() -> dict:
    p = _approved_proposal()
    p["requires_api_keys"] = True
    return p


def _order_proposal() -> dict:
    p = _approved_proposal()
    p["order_capability"] = True
    return p


def _broker_venue_proposal() -> dict:
    p = _approved_proposal()
    p["venue_class"] = "broker"
    return p


def _non_d1_proposal() -> dict:
    p = _approved_proposal()
    p["timeframe"] = "4h"
    return p


def _missing_field_proposal() -> dict:
    p = _approved_proposal()
    del p["coverage_window"]
    return p


def _sc(acquire=None, proposal=None) -> dict:
    return build_crypto_d1_source_class_contract(
        acquire if acquire is not None else _approved_acq(),
        source_class_proposal=proposal,
    )


def _expected_public() -> set[str]:
    return {
        "SOURCE_CLASS_SCHEMA_VERSION",
        "DEFAULT_SOURCE_CLASS_LABEL",
        "SOURCE_CLASS_STATUS",
        "SOURCE_CLASS_SAFETY_POSTURE",
        "SOURCE_CLASS_STATE_ACTIVE",
        "SOURCE_CLASS_STATE_BLOCKED",
        "SOURCE_CLASS_VERDICT_APPROVED",
        "SOURCE_CLASS_VERDICT_NEEDS_MORE_INFO",
        "SOURCE_CLASS_VERDICT_PARKED",
        "SOURCE_CLASS_VERDICT_REJECTED",
        "SOURCE_CLASS_VERDICT_AWAIT",
        "ALLOWED_SOURCE_CLASS_VERDICTS",
        "NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_PARKED",
        "NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_REJECTED",
        "NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION",
        "REQUIRED_SOURCE_CLASS_FIELDS",
        "ALLOWED_ASSET_UNIVERSE",
        "PARKED_MARKET_TYPES",
        "ALLOWED_VENUE_CLASSES",
        "ALLOWED_SOURCE_ACCESS_MODES",
        "REQUIRED_CANDLE_FIELDS",
        "ALLOWED_TIMEFRAME",
        "FORBIDDEN_SOURCE_CLASS_CAPABILITIES",
        "BLOCKED_EXECUTION_ITEMS",
        "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
        "evaluate_crypto_d1_source_class_proposal",
        "build_crypto_d1_source_class_contract",
        "validate_crypto_d1_source_class_contract",
        "render_crypto_d1_source_class_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(SC.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(SC, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        SOURCE_CLASS_SCHEMA_VERSION
        == "strategy_factory_crypto_d1_source_class_contract.v1"
    )
    assert (
        DEFAULT_SOURCE_CLASS_LABEL
        == "Strategy Factory Crypto-D1 Source Class Contract"
    )
    assert SOURCE_CLASS_STATUS == "READ_ONLY_CRYPTO_D1_SOURCE_CLASS_CONTRACT"


# 3 -- state / next-gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        SOURCE_CLASS_STATE_ACTIVE == "CRYPTO_D1_SOURCE_CLASS_CONTRACT_ACTIVE"
    )
    assert (
        SOURCE_CLASS_STATE_BLOCKED == "CRYPTO_D1_SOURCE_CLASS_CONTRACT_BLOCKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED
        == "CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED
        == "CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_PARKED
        == "CRYPTO_D1_SOURCE_CLASS_PARKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_REJECTED
        == "CRYPTO_D1_SOURCE_CLASS_REJECTED"
    )
    assert (
        NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION
        == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"
    )


# 4 -- source-class verdict values are exactly the expected set + order.

def test_allowed_source_class_verdicts_exact():
    assert ALLOWED_SOURCE_CLASS_VERDICTS == (
        "APPROVED_SOURCE_CLASS",
        "NEEDS_MORE_INFO",
        "PARKED_SOURCE_CLASS",
        "REJECTED_SOURCE_CLASS",
        "AWAIT_CRYPTO_D1_ACQUIRE_DECISION",
    )
    assert SOURCE_CLASS_VERDICT_APPROVED == "APPROVED_SOURCE_CLASS"
    assert SOURCE_CLASS_VERDICT_NEEDS_MORE_INFO == "NEEDS_MORE_INFO"
    assert SOURCE_CLASS_VERDICT_PARKED == "PARKED_SOURCE_CLASS"
    assert SOURCE_CLASS_VERDICT_REJECTED == "REJECTED_SOURCE_CLASS"
    assert (
        SOURCE_CLASS_VERDICT_AWAIT == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"
    )


# 5 -- required source-class fields + candle fields + asset universe pinned.

def test_required_field_collections_pinned():
    assert REQUIRED_SOURCE_CLASS_FIELDS == _EXPECTED_REQUIRED_FIELDS
    assert REQUIRED_CANDLE_FIELDS == _EXPECTED_CANDLE_FIELDS
    assert ALLOWED_ASSET_UNIVERSE == ("BTC", "ETH", "SOL")
    assert ALLOWED_TIMEFRAME == ("D1",)


# 6 -- pure stdlib import-root audit: allowed roots only.

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


# 7 -- forbidden-surface audit: no file/network/subprocess/exec/dynamic surface.

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


# 8 -- no filesystem read/write surface in source.

def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# 9 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = SOURCE_CLASS_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 10 -- posture matches the inherited Bundle 42 posture.

def test_posture_matches_bundle42():
    assert SOURCE_CLASS_SAFETY_POSTURE == ACQUIRE_SAFETY_POSTURE


# 11 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _sc(proposal=_approved_proposal())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _sc(proposal=_approved_proposal())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert SOURCE_CLASS_SAFETY_POSTURE["automation_enabled"] is False


# 12 -- an active Bundle 42 APPROVED acquire activates the source-class contract.

def test_active_approved_acquire_activates_source_class():
    c = _sc(proposal=_approved_proposal())
    assert c["crypto_d1_source_class_contract_active"] is True
    assert (
        c["crypto_d1_source_class_contract_state"]
        == "CRYPTO_D1_SOURCE_CLASS_CONTRACT_ACTIVE"
    )
    assert c["crypto_d1_acquire_decision_contract_active"] is True
    assert (
        c["crypto_d1_acquire_decision"]
        == "ACQUIRE_APPROVED_FOR_SOURCE_CLASS_CONTRACT"
    )
    assert (
        c["crypto_d1_acquire_decision_next_gate"]
        == "CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED"
    )
    assert c["schema_version"] == SOURCE_CLASS_SCHEMA_VERSION
    assert (
        c["crypto_d1_acquire_decision_schema_version"]
        == ACQUIRE_SCHEMA_VERSION
    )


# 13 -- an inactive (blocked) acquire contract does not activate.

def test_blocked_acquire_does_not_activate():
    c = _sc(_blocked_acq(), _approved_proposal())
    assert c["crypto_d1_source_class_contract_active"] is False
    assert (
        c["crypto_d1_source_class_contract_state"]
        == "CRYPTO_D1_SOURCE_CLASS_CONTRACT_BLOCKED"
    )
    assert c["source_class_verdict"] == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"


# 14 -- an active acquire with no decision (wrong gate) does not activate.

def test_await_acquire_does_not_activate():
    acq = _await_acq()
    assert acq["crypto_d1_acquire_decision_contract_active"] is True
    assert acq["next_gate"] != "CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED"
    c = _sc(acq, _approved_proposal())
    assert c["crypto_d1_source_class_contract_active"] is False
    assert c["source_class_verdict"] == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"


# 15 -- a non-APPROVED acquire decision (needs more info) does not activate.

def test_non_approved_acquire_decision_does_not_activate():
    acq = _needs_more_acq()
    assert acq["crypto_d1_acquire_decision_contract_active"] is True
    assert acq["next_gate"] != "CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED"
    c = _sc(acq, _approved_proposal())
    assert c["crypto_d1_source_class_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"


# 16 -- active APPROVED acquire but tampered next_gate does not activate.

def test_wrong_acquire_next_gate_does_not_activate():
    import copy
    a = copy.deepcopy(_approved_acq())
    a["next_gate"] = "SOMETHING_ELSE"
    c = _sc(a, _approved_proposal())
    assert c["crypto_d1_source_class_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"


# 17 -- inactive acquire flag does not activate even with right gate/decision.

def test_inactive_acquire_flag_does_not_activate():
    import copy
    a = copy.deepcopy(_approved_acq())
    a["crypto_d1_acquire_decision_contract_active"] = False
    c = _sc(a, _approved_proposal())
    assert c["crypto_d1_source_class_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"


# 18 -- malformed upstream input never raises and never activates.

def test_malformed_upstream_no_raise():
    for bad in (None, 42, "nope", {},
                {"crypto_d1_acquire_decision_contract_active": True},
                []):
        c = build_crypto_d1_source_class_contract(bad)
        assert c["crypto_d1_source_class_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["source_class_verdict"] == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"
        assert c["next_gate"] == "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 19 -- an approved proposal yields APPROVED + the acquisition-plan gate.

def test_approved_proposal_maps_to_acquisition_plan_gate():
    c = _sc(proposal=_approved_proposal())
    assert c["source_class_verdict"] == "APPROVED_SOURCE_CLASS"
    assert (
        c["next_gate"]
        == "CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED"
    )
    # Even APPROVED never unlocks QA / baseline / backtest / real intake.
    remaining = set(c["remaining_real_world_capabilities_blocked"])
    for cap in ("real_qa_run", "real_baseline_run", "real_backtest",
                "real_strategy_intake", "real_data_acquisition",
                "real_data_inspection"):
        assert cap in remaining, cap


# 20 -- a missing required field yields NEEDS_MORE_INFO + the fix gate.

def test_missing_field_maps_to_needs_more_info():
    c = _sc(proposal=_missing_field_proposal())
    assert c["source_class_verdict"] == "NEEDS_MORE_INFO"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED"
    assert "coverage_window_required" in c["source_class_verdict_reasons"]


# 21 -- a perps/funding market parks (when otherwise safe).

def test_perps_market_parks():
    c = _sc(proposal=_perps_proposal())
    assert c["source_class_verdict"] == "PARKED_SOURCE_CLASS"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_CLASS_PARKED"


# 22 -- live API access mode is rejected (safety-first, not parked).

def test_live_api_access_rejected():
    c = _sc(proposal=_live_api_proposal())
    assert c["source_class_verdict"] == "REJECTED_SOURCE_CLASS"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_CLASS_REJECTED"
    assert "live_source_access_mode" in c["source_class_verdict_reasons"]


# 23 -- API keys / account access requirement is rejected.

def test_api_keys_requirement_rejected():
    c = _sc(proposal=_api_keys_proposal())
    assert c["source_class_verdict"] == "REJECTED_SOURCE_CLASS"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_CLASS_REJECTED"


# 24 -- order capability is rejected.

def test_order_capability_rejected():
    c = _sc(proposal=_order_proposal())
    assert c["source_class_verdict"] == "REJECTED_SOURCE_CLASS"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_CLASS_REJECTED"


# 25 -- a live broker venue class is rejected.

def test_broker_venue_rejected():
    c = _sc(proposal=_broker_venue_proposal())
    assert c["source_class_verdict"] == "REJECTED_SOURCE_CLASS"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_CLASS_REJECTED"


# 26 -- perps PLUS a live capability is rejected (safety beats parking).

def test_perps_plus_live_is_rejected_not_parked():
    p = _perps_proposal()
    p["source_access_mode"] = "live_api"
    c = _sc(proposal=p)
    assert c["source_class_verdict"] == "REJECTED_SOURCE_CLASS"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_CLASS_REJECTED"


# 27 -- a non-D1 timeframe is not approved (needs more info).

def test_non_d1_timeframe_not_approved():
    c = _sc(proposal=_non_d1_proposal())
    assert c["source_class_verdict"] == "NEEDS_MORE_INFO"
    assert "d1_timeframe_required" in c["source_class_verdict_reasons"]
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED"


# 28 -- an empty / missing proposal yields NEEDS_MORE_INFO.

def test_empty_proposal_needs_more_info():
    c = _sc(proposal=None)
    assert c["source_class_verdict"] == "NEEDS_MORE_INFO"
    assert "source_class_proposal_missing" in c["source_class_verdict_reasons"]
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED"


# 29 -- the standalone evaluator is deterministic + matches the builder.

def test_evaluator_deterministic_and_matches_builder():
    for proposal in (_approved_proposal(), _perps_proposal(),
                     _live_api_proposal(), _missing_field_proposal(),
                     _non_d1_proposal()):
        e1 = evaluate_crypto_d1_source_class_proposal(proposal)
        e2 = evaluate_crypto_d1_source_class_proposal(proposal)
        assert e1 == e2
        c = _sc(proposal=proposal)
        assert c["source_class_verdict"] == e1["verdict"]
        assert tuple(c["source_class_verdict_reasons"]) == tuple(e1["reasons"])


# 30 -- no authorization flag can become True (any state / any verdict).

def test_authorization_flags_always_false():
    states = [
        _sc(proposal=_approved_proposal()),
        _sc(proposal=_perps_proposal()),
        _sc(proposal=_live_api_proposal()),
        _sc(proposal=_missing_field_proposal()),
        _sc(_blocked_acq(), _approved_proposal()),
        build_crypto_d1_source_class_contract({}),
    ]
    for c in states:
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["mode"] == "RESEARCH_ONLY"
        assert c["stage"] == "CRYPTO_D1_SOURCE_CLASS_ONLY"


# 31 -- even an approved source class authorizes no execution surface.

def test_approved_source_class_authorizes_no_execution_surface():
    c = _sc(proposal=_approved_proposal())
    assert c["source_class_verdict"] == "APPROVED_SOURCE_CLASS"
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


# 32 -- blocked capabilities include the required broad set.

def test_blocked_capabilities():
    c = _sc(proposal=_approved_proposal())
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 33 -- source-class-specific blocked capabilities present.

def test_source_class_blocked_capabilities_present():
    c = _sc(proposal=_approved_proposal())
    source_blocked = set(c["source_class_blocked_capabilities"])
    for cap in ("crypto_d1_source_class_execution",
                "crypto_d1_data_acquisition", "crypto_d1_live_api_access",
                "crypto_d1_exchange_connection", "crypto_d1_broker_connection",
                "crypto_d1_dataset_read", "crypto_d1_data_inspection",
                "crypto_d1_qa_run", "crypto_d1_baseline_run",
                "crypto_d1_backtest", "real_strategy_intake",
                "report_file_write", "runtime_state_write"):
        assert cap in source_blocked, cap


# 34 -- blocked execution items are exactly the three deferred items.

def test_blocked_execution_items_exact():
    c = _sc(proposal=_approved_proposal())
    assert tuple(c["blocked_execution_items"]) == BLOCKED_EXECUTION_ITEMS
    assert BLOCKED_EXECUTION_ITEMS == _EXPECTED_BLOCKED_EXECUTION


# 35 -- remaining real-world capabilities are still blocked + exact.

def test_remaining_real_world_capabilities_blocked():
    c = _sc(proposal=_approved_proposal())
    remaining = set(c["remaining_real_world_capabilities_blocked"])
    for cap in ("real_strategy_intake", "real_data_acquisition",
                "real_data_load", "real_data_validation",
                "real_data_transform", "real_data_inspection",
                "real_data_compute", "real_market_data_inspection",
                "real_crypto_d1_dataset_inspection", "real_qa_run",
                "real_baseline_run", "real_backtest", "real_simulation",
                "real_data_fetch", "real_exchange_connection",
                "real_broker_connection", "real_live_api_access",
                "broker", "exchange", "order", "live_execution",
                "paper_execution", "autopilot", "automation", "upload",
                "deploy", "promotion"):
        assert cap in remaining, cap
    assert (
        tuple(c["remaining_real_world_capabilities_blocked"])
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


# 36 -- the embedded upstream acquire contract is preserved.

def test_upstream_acquire_embedded():
    acq = _approved_acq()
    c = build_crypto_d1_source_class_contract(acq)
    embedded = c["crypto_d1_acquire_decision_contract"]
    assert embedded["crypto_d1_acquire_decision_contract_active"] is True
    assert embedded["read_only"] is True


# 37 -- the evaluated proposal is echoed back (read-only copy).

def test_evaluated_proposal_echoed():
    p = _approved_proposal()
    c = _sc(proposal=p)
    assert c["evaluated_source_class_proposal"] == p
    # mutate the echo -> source proposal unchanged.
    c["evaluated_source_class_proposal"]["market_type"] = "perp"
    assert p["market_type"] == "spot"


# 38 -- validate passes for a clean contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _sc(proposal=_approved_proposal())
    v = validate_crypto_d1_source_class_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_crypto_d1_source_class_contract(bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_crypto_d1_source_class_contract(bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_crypto_d1_source_class_contract(bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["stage"] = "EXECUTE"
    assert validate_crypto_d1_source_class_contract(bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["human_approval_required"] = False
    assert validate_crypto_d1_source_class_contract(bad5)["valid"] is False


# 39 -- validate flags wrong field tuples / collections.

def test_validate_flags_wrong_collections():
    import copy
    c = _sc(proposal=_approved_proposal())
    for key in ("allowed_source_class_verdicts",
                "required_source_class_fields",
                "allowed_asset_universe",
                "required_candle_fields",
                "allowed_timeframe",
                "blocked_execution_items",
                "remaining_real_world_capabilities_blocked",
                "forbidden_source_class_capabilities"):
        bad = copy.deepcopy(c)
        bad[key] = ("not", "the", "right", "tuple")
        assert validate_crypto_d1_source_class_contract(
            bad)["valid"] is False, key


# 40 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_sc(proposal=_approved_proposal()))
    c.pop("validation", None)
    v = validate_crypto_d1_source_class_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 41 -- a blocked (await) contract still validates (safety shape).

def test_blocked_contract_still_validates():
    c = _sc(_blocked_acq(), _approved_proposal())
    v = validate_crypto_d1_source_class_contract(c)
    assert v["valid"] is True
    assert c["crypto_d1_source_class_contract_active"] is False


# 42 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    import copy
    c = copy.deepcopy(_sc(proposal=_approved_proposal()))
    c.pop("crypto_d1_acquire_decision_contract", None)
    v = validate_crypto_d1_source_class_contract(c)
    assert v["valid"] is False
    assert (
        "crypto_d1_acquire_decision_contract"
        in v["missing_required_fields"]
    )


# 43 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_source_class_only_and_execution_free():
    c = _sc(proposal=_approved_proposal())
    md = render_crypto_d1_source_class_contract_markdown(c)
    assert isinstance(md, str) and md
    assert "# Strategy Factory Crypto-D1 Source Class Contract" in md
    for descriptor in ("crypto-d1-source-class-contract-only",
                       "offline-spec-only", "no-live-api",
                       "no-data-acquisition", "no-qa-run", "no-baseline-run",
                       "no-data-inspection", "no-real-strategy-intake-yet",
                       "research-only", "execution-free"):
        assert descriptor in md, descriptor
    assert "Stage: CRYPTO_D1_SOURCE_CLASS_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "## Source Class Proposal Reference" in md
    assert "## Source Class Verdict Reasons" in md
    assert "## Allowed Source Class Verdicts" in md
    assert "## Required Source Class Fields" in md
    assert "## Allowed Asset Universe" in md
    assert "## Parked Market Types" in md
    assert "## Allowed Venue Classes" in md
    assert "## Allowed Source Access Modes" in md
    assert "## Required Candle Fields" in md
    assert "## Allowed Timeframe" in md
    assert "## Forbidden Source Class Capabilities" in md
    assert "## Source Class Verdict Rationale" in md
    assert "## Blocked Execution Items" in md
    assert "## Source Class Blocked Capabilities" in md
    assert "## Remaining Real-World Capabilities Blocked" in md
    assert "## Blocked Capabilities" in md
    assert "## Human Operator Required Next Steps" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 44 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 45 -- prose verb audit over notes / next-steps / placeholders / markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list[str] = []
    c = _sc(proposal=_approved_proposal())

    texts.extend(str(x) for x in c["operator_notes"])
    texts.extend(str(x) for x in c["human_operator_required_next_steps"])
    texts.append(
        str(c["source_class_proposal_reference_placeholder"]))
    texts.append(str(c["source_class_verdict_rationale_placeholder"]))

    md = render_crypto_d1_source_class_contract_markdown(c)
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


# 46 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 47 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_crypto_d1_source_class_contract.py"'  # noqa: E501
        in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_source_class_contract.py"'
        in src
    )


# 48 -- repeated builds are deterministic (no timestamp / random id).

def test_repeated_builds_are_deterministic():
    a = _sc(proposal=_approved_proposal())
    b = _sc(proposal=_approved_proposal())
    assert a == b


# 49 -- Bundle 42 regression import still works.

def test_bundle42_regression_import_still_works():
    a = build_crypto_d1_acquire_decision_contract({})
    assert a["executes"] is False
    assert a["read_only"] is True
    assert a["crypto_d1_acquire_decision_contract_active"] is False


# 50 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0

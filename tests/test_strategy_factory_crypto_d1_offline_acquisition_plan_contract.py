"""Bundle 45 tests for the Strategy Factory Crypto-D1 Offline Acquisition Plan
Contract v1 (informational, read-only, paper-only,
offline-acquisition-plan-contract-only, offline-plan-only, deterministic,
execution-free -- NO written report on disk, NO report file write, NO data
acquisition, NO data inspection, NO live API, NO exchange/broker connection, NO
QA run, NO QA verdict, NO baseline run, NO backtest, NO runtime state write, NO
real strategy intake).

This bundle defines the crypto-d1 *offline acquisition plan* evaluation
contract. It activates only from an active Bundle 44 crypto-d1 source
specification contract whose source_specification_verdict is
APPROVED_SOURCE_SPECIFICATION and whose next_gate is
CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED (the concrete Bundle 44
signal that an offline acquisition plan contract is required next). When active,
it evaluates a paper offline-acquisition-plan proposal dict and returns a
deterministic verdict; it acquires no data and unlocks nothing real.

Bundle 45's production module imports Bundle 44 via a real package import, so
these tests use normal package imports too. Running under ``python -m pytest``
places the repo root on ``sys.path`` so ``sparta_commander`` resolves.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_crypto_d1_offline_acquisition_plan_contract import (  # noqa: E501
    PLAN_SCHEMA_VERSION,
    DEFAULT_PLAN_LABEL,
    PLAN_STATUS,
    PLAN_SAFETY_POSTURE,
    PLAN_STATE_ACTIVE,
    PLAN_STATE_BLOCKED,
    PLAN_VERDICT_APPROVED,
    PLAN_VERDICT_NEEDS_MORE_INFO,
    PLAN_VERDICT_PARKED,
    PLAN_VERDICT_REJECTED,
    PLAN_VERDICT_AWAIT,
    ALLOWED_PLAN_VERDICTS,
    UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_VERDICT,
    UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_GATE,
    NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED,
    NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_PARKED,
    NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT,
    REQUIRED_PLAN_FIELDS,
    PLAN_NEGATIVE_SAFETY_FLAGS,
    PLAN_FORBIDDEN_CAPABILITY_FLAGS,
    ALLOWED_ASSET_UNIVERSE,
    PARKED_MARKET_TYPES,
    ALLOWED_ACCESS_MODES,
    ALLOWED_OFFLINE_ACQUISITION_MODES,
    ALLOWED_OFFLINE_SOURCE_TYPES,
    REQUIRED_CANDLE_FIELDS,
    ALLOWED_TIMEFRAME,
    BLOCKED_EXECUTION_ITEMS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_offline_acquisition_plan,
    build_crypto_d1_offline_acquisition_plan_contract,
    validate_crypto_d1_offline_acquisition_plan_contract,
    render_crypto_d1_offline_acquisition_plan_contract_markdown,
)
import sparta_commander.strategy_factory_crypto_d1_offline_acquisition_plan_contract as PL  # noqa: E501
from sparta_commander.strategy_factory_crypto_d1_source_specification_contract import (  # noqa: E501
    SPEC_SCHEMA_VERSION,
    SPEC_SAFETY_POSTURE,
    SPEC_VERDICT_APPROVED,
    build_crypto_d1_source_specification_contract,
)
from sparta_commander.strategy_factory_crypto_d1_source_class_contract import (  # noqa: E501
    build_crypto_d1_source_class_contract,
)
from sparta_commander.strategy_factory_crypto_d1_acquire_decision_contract import (  # noqa: E501
    ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT,
    build_crypto_d1_acquire_decision_contract,
)
from sparta_commander.strategy_factory_crypto_d1_intake_reconciliation_contract import (  # noqa: E501
    RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT,
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
    / "strategy_factory_crypto_d1_offline_acquisition_plan_contract.py"
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

_EXPECTED_REQUIRED_FIELDS = (
    "plan_name",
    "source_specification_id",
    "acquisition_mode",
    "allowed_source_type",
    "asset_universe",
    "symbols",
    "market_type",
    "timeframe",
    "expected_columns",
    "coverage_start",
    "coverage_end",
    "timezone",
    "session_rule",
    "destination_policy",
    "freeze_manifest_plan",
    "checksum_plan",
    "provenance_plan",
    "reproducibility_plan",
    "fee_model_plan",
    "slippage_model_plan",
    "missing_candle_policy",
    "duplicate_timestamp_policy",
    "validation_before_use_plan",
    "human_approval_required",
    "no_live_fetch",
    "no_api_keys",
    "no_auth_required",
    "no_account_access",
    "no_order_capability",
    "no_broker_exchange_capability",
    "no_automation_trigger",
    "no_runtime_write",
    "no_registry_write",
    "no_dashboard_write",
)

_EXPECTED_NEGATIVE_SAFETY_FLAGS = (
    "no_live_fetch",
    "no_api_keys",
    "no_auth_required",
    "no_account_access",
    "no_order_capability",
    "no_broker_exchange_capability",
    "no_automation_trigger",
    "no_runtime_write",
    "no_registry_write",
    "no_dashboard_write",
)


# --- upstream fake-lane chain (reused from Bundle 44 test) -----------------

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


def _active_review_contract() -> dict:
    return build_fake_report_renderer_result_review_contract(
        _active_renderer_state(),
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT
        ),
    )


def _active_closure() -> dict:
    return build_fake_lane_closure_contract(
        _active_review_contract(),
        closure_decision=CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR,
    )


def _ready_recon() -> dict:
    return build_crypto_d1_intake_reconciliation_contract(
        _active_closure(),
        reconciliation_decision=(
            RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT
        ),
    )


def _approved_acq() -> dict:
    return build_crypto_d1_acquire_decision_contract(
        _ready_recon(),
        acquire_decision=ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT,
    )


# --- Bundle 43 source-class proposal helpers -------------------------------

def _approved_sc_proposal() -> dict:
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


def _approved_sc() -> dict:
    """Active Bundle 43 source-class contract, APPROVED at the gate."""
    return build_crypto_d1_source_class_contract(
        _approved_acq(), source_class_proposal=_approved_sc_proposal())


# --- Bundle 44 source-specification proposal + contract helpers ------------

def _approved_spec_proposal() -> dict:
    return {
        "source_name": "Vendor Historical Daily Candles",
        "source_class": "vendor_historical_candles",
        "venue_or_vendor_name": "ExampleVendor",
        "asset_universe": ["BTC", "ETH", "SOL"],
        "symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "market_type": "spot",
        "timeframe": "D1",
        "candle_schema": [
            "timestamp", "open", "high", "low", "close", "volume",
        ],
        "timestamp_column": "timestamp",
        "open_column": "open",
        "high_column": "high",
        "low_column": "low",
        "close_column": "close",
        "volume_column": "volume",
        "session_rule": "UTC daily candles",
        "coverage_start": "2019-01-01",
        "coverage_end": "2025-01-01",
        "expected_frequency": "one daily candle per asset per UTC day",
        "missing_candle_policy": "flag and drop incomplete UTC days",
        "duplicate_timestamp_policy": "keep first, log duplicates",
        "fee_model_assumption": "static taker fee placeholder",
        "slippage_model_assumption": "fixed basis-point placeholder",
        "provenance_required": True,
        "checksum_required": True,
        "freeze_manifest_required": True,
        "reproducibility_notes": (
            "deterministic offline fixture with a frozen manifest"
        ),
        "access_mode": "offline_fixture",
        "auth_required": False,
        "api_key_required": False,
        "live_fetch_allowed": False,
        "account_access_allowed": False,
        "order_capability_allowed": False,
        "broker_exchange_capability_allowed": False,
    }


def _approved_sp() -> dict:
    """Active Bundle 44 source-specification contract, APPROVED at the
    acquisition-plan gate -- the concrete signal Bundle 45 activates from."""
    return build_crypto_d1_source_specification_contract(
        _approved_sc(), source_specification=_approved_spec_proposal())


def _needs_more_sp() -> dict:
    """Active source-specification contract with a NEEDS_MORE_INFO verdict."""
    bad = dict(_approved_spec_proposal())
    del bad["fee_model_assumption"]
    return build_crypto_d1_source_specification_contract(
        _approved_sc(), source_specification=bad)


def _parked_sp() -> dict:
    """Active source-specification contract with a PARKED verdict."""
    bad = dict(_approved_spec_proposal())
    bad["market_type"] = "perp"
    return build_crypto_d1_source_specification_contract(
        _approved_sc(), source_specification=bad)


def _blocked_sp() -> dict:
    """Inactive source-specification contract (no upstream approval)."""
    return build_crypto_d1_source_specification_contract({})


# --- offline-acquisition-plan proposal helpers -----------------------------

def _approved_plan() -> dict:
    return {
        "plan_name": "BTC/ETH/SOL Daily Offline Fixture Plan",
        "source_specification_id": "spec-crypto-d1-001",
        "acquisition_mode": "offline_fixture",
        "allowed_source_type": "vendor_historical_file",
        "asset_universe": ["BTC", "ETH", "SOL"],
        "symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "market_type": "spot",
        "timeframe": "D1",
        "expected_columns": [
            "timestamp", "open", "high", "low", "close", "volume",
        ],
        "coverage_start": "2019-01-01",
        "coverage_end": "2025-01-01",
        "timezone": "UTC",
        "session_rule": "UTC daily candles",
        "destination_policy": (
            "human places frozen fixture under a versioned offline folder"
        ),
        "freeze_manifest_plan": "freeze a manifest listing all fixture files",
        "checksum_plan": "record a sha256 checksum per fixture file",
        "provenance_plan": "record vendor name, download date, and file hash",
        "reproducibility_plan": (
            "deterministic offline fixture re-derivable from the manifest"
        ),
        "fee_model_plan": "static taker fee placeholder documented in notes",
        "slippage_model_plan": "fixed basis-point placeholder in notes",
        "missing_candle_policy": "flag and drop incomplete UTC days",
        "duplicate_timestamp_policy": "keep first, log duplicates",
        "validation_before_use_plan": (
            "a later human-approved QA contract validates before any use"
        ),
        "human_approval_required": True,
        "no_live_fetch": True,
        "no_api_keys": True,
        "no_auth_required": True,
        "no_account_access": True,
        "no_order_capability": True,
        "no_broker_exchange_capability": True,
        "no_automation_trigger": True,
        "no_runtime_write": True,
        "no_registry_write": True,
        "no_dashboard_write": True,
    }


def _perps_plan() -> dict:
    p = _approved_plan()
    p["market_type"] = "perp"
    return p


def _alt_asset_plan() -> dict:
    p = _approved_plan()
    p["asset_universe"] = ["DOGE", "XRP"]
    return p


def _live_mode_plan() -> dict:
    p = _approved_plan()
    p["acquisition_mode"] = "live_api"
    return p


def _live_source_plan() -> dict:
    p = _approved_plan()
    p["allowed_source_type"] = "live_exchange_api"
    return p


def _forbidden_capability_plan() -> dict:
    p = _approved_plan()
    p["live_fetch"] = True
    return p


def _disabled_safety_flag_plan() -> dict:
    p = _approved_plan()
    p["no_live_fetch"] = False
    return p


def _non_d1_plan() -> dict:
    p = _approved_plan()
    p["timeframe"] = "4h"
    return p


def _missing_field_plan() -> dict:
    p = _approved_plan()
    del p["fee_model_plan"]
    return p


def _missing_safety_flag_plan() -> dict:
    p = _approved_plan()
    del p["no_runtime_write"]
    return p


def _plan(sp=None, plan=None) -> dict:
    return build_crypto_d1_offline_acquisition_plan_contract(
        sp if sp is not None else _approved_sp(),
        offline_acquisition_plan=plan,
    )


def _expected_public() -> set:
    return {
        "PLAN_SCHEMA_VERSION",
        "DEFAULT_PLAN_LABEL",
        "PLAN_STATUS",
        "PLAN_SAFETY_POSTURE",
        "PLAN_STATE_ACTIVE",
        "PLAN_STATE_BLOCKED",
        "PLAN_VERDICT_APPROVED",
        "PLAN_VERDICT_NEEDS_MORE_INFO",
        "PLAN_VERDICT_PARKED",
        "PLAN_VERDICT_REJECTED",
        "PLAN_VERDICT_AWAIT",
        "ALLOWED_PLAN_VERDICTS",
        "UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_VERDICT",
        "UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_GATE",
        "NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED",  # noqa: E501
        "NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_PARKED",
        "NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED",
        "NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT",
        "REQUIRED_PLAN_FIELDS",
        "PLAN_NEGATIVE_SAFETY_FLAGS",
        "PLAN_FORBIDDEN_CAPABILITY_FLAGS",
        "ALLOWED_ASSET_UNIVERSE",
        "PARKED_MARKET_TYPES",
        "ALLOWED_ACCESS_MODES",
        "ALLOWED_OFFLINE_ACQUISITION_MODES",
        "ALLOWED_OFFLINE_SOURCE_TYPES",
        "REQUIRED_CANDLE_FIELDS",
        "ALLOWED_TIMEFRAME",
        "BLOCKED_EXECUTION_ITEMS",
        "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
        "evaluate_crypto_d1_offline_acquisition_plan",
        "build_crypto_d1_offline_acquisition_plan_contract",
        "validate_crypto_d1_offline_acquisition_plan_contract",
        "render_crypto_d1_offline_acquisition_plan_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(PL.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(PL, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        PLAN_SCHEMA_VERSION
        == "strategy_factory_crypto_d1_offline_acquisition_plan_contract.v1"
    )
    assert (
        DEFAULT_PLAN_LABEL
        == "Strategy Factory Crypto-D1 Offline Acquisition Plan Contract"
    )
    assert (
        PLAN_STATUS
        == "READ_ONLY_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT"
    )


# 3 -- state / next-gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        PLAN_STATE_ACTIVE
        == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT_ACTIVE"
    )
    assert (
        PLAN_STATE_BLOCKED
        == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT_BLOCKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED
        == "CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED
        == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_PARKED
        == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_PARKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED
        == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED"
    )
    assert (
        NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT
        == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
    )


# 4 -- the upstream Bundle 44 activation signal is pinned to the real values.

def test_upstream_activation_signal_pinned():
    assert (
        UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_VERDICT
        == SPEC_VERDICT_APPROVED
    )
    assert (
        UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_VERDICT
        == "APPROVED_SOURCE_SPECIFICATION"
    )
    assert (
        UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_GATE
        == "CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED"
    )


# 5 -- offline-plan verdict values are exactly the expected set + order.

def test_allowed_plan_verdicts_exact():
    assert ALLOWED_PLAN_VERDICTS == (
        "APPROVED_OFFLINE_ACQUISITION_PLAN",
        "NEEDS_MORE_INFO",
        "PARKED_OFFLINE_ACQUISITION_PLAN",
        "REJECTED_OFFLINE_ACQUISITION_PLAN",
        "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT",
    )
    assert PLAN_VERDICT_APPROVED == "APPROVED_OFFLINE_ACQUISITION_PLAN"
    assert PLAN_VERDICT_NEEDS_MORE_INFO == "NEEDS_MORE_INFO"
    assert PLAN_VERDICT_PARKED == "PARKED_OFFLINE_ACQUISITION_PLAN"
    assert PLAN_VERDICT_REJECTED == "REJECTED_OFFLINE_ACQUISITION_PLAN"
    assert (
        PLAN_VERDICT_AWAIT
        == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
    )


# 6 -- required plan fields + safety flags + candle/asset/timeframe pinned.

def test_required_field_collections_pinned():
    assert REQUIRED_PLAN_FIELDS == _EXPECTED_REQUIRED_FIELDS
    assert PLAN_NEGATIVE_SAFETY_FLAGS == _EXPECTED_NEGATIVE_SAFETY_FLAGS
    assert REQUIRED_CANDLE_FIELDS == (
        "timestamp", "open", "high", "low", "close", "volume",
    )
    assert ALLOWED_ASSET_UNIVERSE == ("BTC", "ETH", "SOL")
    assert ALLOWED_TIMEFRAME == ("D1",)
    assert "offline_fixture" in ALLOWED_OFFLINE_ACQUISITION_MODES
    assert "vendor_historical_file" in ALLOWED_OFFLINE_SOURCE_TYPES
    assert "live_fetch" in PLAN_FORBIDDEN_CAPABILITY_FLAGS


# 7 -- pure stdlib import-root audit: allowed roots only.

def test_import_roots_are_allowed_only():
    src = _MODPATH.read_text(encoding="utf-8")
    roots: set = set()
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


# 8 -- forbidden-surface audit: no file/network/subprocess/exec/dynamic surface.

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


# 9 -- no filesystem read/write surface in source.

def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# 10 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = PLAN_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 11 -- posture matches the inherited Bundle 44 posture.

def test_posture_matches_bundle44():
    assert PLAN_SAFETY_POSTURE == SPEC_SAFETY_POSTURE


# 12 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _plan(plan=_approved_plan())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _plan(plan=_approved_plan())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert PLAN_SAFETY_POSTURE["automation_enabled"] is False


# 13 -- an active Bundle 44 APPROVED source-spec activates the plan contract.

def test_active_approved_source_spec_activates_plan():
    c = _plan(plan=_approved_plan())
    assert c["crypto_d1_offline_acquisition_plan_contract_active"] is True
    assert (
        c["crypto_d1_offline_acquisition_plan_contract_state"]
        == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT_ACTIVE"
    )
    assert c["crypto_d1_source_specification_contract_active"] is True
    assert (
        c["crypto_d1_source_specification_verdict"]
        == "APPROVED_SOURCE_SPECIFICATION"
    )
    assert (
        c["crypto_d1_source_specification_next_gate"]
        == "CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED"
    )
    assert c["schema_version"] == PLAN_SCHEMA_VERSION
    assert (
        c["crypto_d1_source_specification_schema_version"]
        == SPEC_SCHEMA_VERSION
    )


# 14 -- an inactive (blocked) source-spec does not activate.

def test_blocked_source_spec_does_not_activate():
    c = _plan(_blocked_sp(), _approved_plan())
    assert c["crypto_d1_offline_acquisition_plan_contract_active"] is False
    assert (
        c["crypto_d1_offline_acquisition_plan_contract_state"]
        == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT_BLOCKED"
    )
    assert (
        c["offline_acquisition_plan_verdict"]
        == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
    )
    assert (
        c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
    )


# 15 -- an active but PARKED source-spec (wrong verdict) does not activate.

def test_parked_source_spec_does_not_activate():
    sp = _parked_sp()
    assert sp["crypto_d1_source_specification_contract_active"] is True
    assert sp["source_specification_verdict"] != SPEC_VERDICT_APPROVED
    c = _plan(sp, _approved_plan())
    assert c["crypto_d1_offline_acquisition_plan_contract_active"] is False
    assert (
        c["offline_acquisition_plan_verdict"]
        == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
    )
    assert (
        c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
    )


# 16 -- an active NEEDS_MORE_INFO source-spec does not activate.

def test_needs_more_source_spec_does_not_activate():
    sp = _needs_more_sp()
    assert sp["crypto_d1_source_specification_contract_active"] is True
    assert sp["source_specification_verdict"] != SPEC_VERDICT_APPROVED
    c = _plan(sp, _approved_plan())
    assert c["crypto_d1_offline_acquisition_plan_contract_active"] is False
    assert (
        c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
    )


# 17 -- active APPROVED source-spec but tampered next_gate does not activate.

def test_wrong_source_spec_next_gate_does_not_activate():
    import copy
    sp = copy.deepcopy(_approved_sp())
    sp["next_gate"] = "SOMETHING_ELSE"
    c = _plan(sp, _approved_plan())
    assert c["crypto_d1_offline_acquisition_plan_contract_active"] is False
    assert (
        c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
    )


# 18 -- tampered source-spec verdict does not activate.

def test_wrong_source_spec_verdict_does_not_activate():
    import copy
    sp = copy.deepcopy(_approved_sp())
    sp["source_specification_verdict"] = "NEEDS_MORE_INFO"
    c = _plan(sp, _approved_plan())
    assert c["crypto_d1_offline_acquisition_plan_contract_active"] is False
    assert (
        c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
    )


# 19 -- inactive source-spec flag does not activate even with right verdict/gate.

def test_inactive_source_spec_flag_does_not_activate():
    import copy
    sp = copy.deepcopy(_approved_sp())
    sp["crypto_d1_source_specification_contract_active"] = False
    c = _plan(sp, _approved_plan())
    assert c["crypto_d1_offline_acquisition_plan_contract_active"] is False
    assert (
        c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
    )


# 20 -- malformed upstream input never raises and never activates.

def test_malformed_upstream_no_raise():
    for bad in (None, 42, "nope", {},
                {"crypto_d1_source_specification_contract_active": True},
                []):
        c = build_crypto_d1_offline_acquisition_plan_contract(bad)
        assert c["crypto_d1_offline_acquisition_plan_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        assert (
            c["offline_acquisition_plan_verdict"]
            == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
        )
        assert (
            c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
        )
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 21 -- an approved plan yields APPROVED + the acquisition-execution gate.

def test_approved_plan_maps_to_execution_plan_gate():
    c = _plan(plan=_approved_plan())
    assert (
        c["offline_acquisition_plan_verdict"]
        == "APPROVED_OFFLINE_ACQUISITION_PLAN"
    )
    assert (
        c["next_gate"]
        == "CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED"
    )
    remaining = set(c["remaining_real_world_capabilities_blocked"])
    for cap in ("real_qa_run", "real_baseline_run", "real_backtest",
                "real_strategy_intake", "real_data_acquisition",
                "real_data_inspection"):
        assert cap in remaining, cap


# 22 -- a missing required field yields NEEDS_MORE_INFO + the fix gate.

def test_missing_field_maps_to_needs_more_info():
    c = _plan(plan=_missing_field_plan())
    assert c["offline_acquisition_plan_verdict"] == "NEEDS_MORE_INFO"
    assert (
        c["next_gate"]
        == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED"
    )
    assert (
        "fee_model_plan_required"
        in c["offline_acquisition_plan_verdict_reasons"]
    )


# 23 -- a missing negative-safety flag yields NEEDS_MORE_INFO (must affirm).

def test_missing_safety_flag_needs_more_info():
    c = _plan(plan=_missing_safety_flag_plan())
    assert c["offline_acquisition_plan_verdict"] == "NEEDS_MORE_INFO"
    assert (
        "no_runtime_write_must_be_affirmed_true"
        in c["offline_acquisition_plan_verdict_reasons"]
    )
    assert (
        c["next_gate"]
        == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED"
    )


# 24 -- a perps/funding market parks (when otherwise safe).

def test_perps_market_parks():
    c = _plan(plan=_perps_plan())
    assert (
        c["offline_acquisition_plan_verdict"]
        == "PARKED_OFFLINE_ACQUISITION_PLAN"
    )
    assert c["next_gate"] == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_PARKED"


# 25 -- an alternative asset universe parks (plausible, not priority).

def test_alt_asset_universe_parks():
    c = _plan(plan=_alt_asset_plan())
    assert (
        c["offline_acquisition_plan_verdict"]
        == "PARKED_OFFLINE_ACQUISITION_PLAN"
    )
    assert c["next_gate"] == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_PARKED"


# 26 -- a live acquisition mode is rejected (safety-first).

def test_live_acquisition_mode_rejected():
    c = _plan(plan=_live_mode_plan())
    assert (
        c["offline_acquisition_plan_verdict"]
        == "REJECTED_OFFLINE_ACQUISITION_PLAN"
    )
    assert c["next_gate"] == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED"
    assert (
        "live_acquisition_mode"
        in c["offline_acquisition_plan_verdict_reasons"]
    )


# 27 -- a live source type is rejected.

def test_live_source_type_rejected():
    c = _plan(plan=_live_source_plan())
    assert (
        c["offline_acquisition_plan_verdict"]
        == "REJECTED_OFFLINE_ACQUISITION_PLAN"
    )
    assert c["next_gate"] == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED"
    assert (
        "live_source_type"
        in c["offline_acquisition_plan_verdict_reasons"]
    )


# 28 -- a forbidden positive capability flag is rejected.

def test_forbidden_capability_flag_rejected():
    c = _plan(plan=_forbidden_capability_plan())
    assert (
        c["offline_acquisition_plan_verdict"]
        == "REJECTED_OFFLINE_ACQUISITION_PLAN"
    )
    assert c["next_gate"] == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED"
    assert (
        "forbidden_capability:live_fetch"
        in c["offline_acquisition_plan_verdict_reasons"]
    )


# 29 -- a negative-safety flag explicitly disabled is rejected.

def test_disabled_safety_flag_rejected():
    c = _plan(plan=_disabled_safety_flag_plan())
    assert (
        c["offline_acquisition_plan_verdict"]
        == "REJECTED_OFFLINE_ACQUISITION_PLAN"
    )
    assert c["next_gate"] == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED"
    assert (
        "safety_flag_not_affirmed:no_live_fetch"
        in c["offline_acquisition_plan_verdict_reasons"]
    )


# 30 -- perps PLUS a live capability is rejected (safety beats parking).

def test_perps_plus_live_is_rejected_not_parked():
    p = _perps_plan()
    p["live_fetch"] = True
    c = _plan(plan=p)
    assert (
        c["offline_acquisition_plan_verdict"]
        == "REJECTED_OFFLINE_ACQUISITION_PLAN"
    )
    assert c["next_gate"] == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED"


# 31 -- a non-D1 timeframe is not approved (needs more info).

def test_non_d1_timeframe_not_approved():
    c = _plan(plan=_non_d1_plan())
    assert c["offline_acquisition_plan_verdict"] == "NEEDS_MORE_INFO"
    assert (
        "d1_timeframe_required"
        in c["offline_acquisition_plan_verdict_reasons"]
    )
    assert (
        c["next_gate"]
        == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED"
    )


# 32 -- an empty / missing plan yields NEEDS_MORE_INFO.

def test_empty_plan_needs_more_info():
    c = _plan(plan=None)
    assert c["offline_acquisition_plan_verdict"] == "NEEDS_MORE_INFO"
    assert (
        "offline_acquisition_plan_missing"
        in c["offline_acquisition_plan_verdict_reasons"]
    )
    assert (
        c["next_gate"]
        == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED"
    )


# 33 -- the standalone evaluator is deterministic + matches the builder.

def test_evaluator_deterministic_and_matches_builder():
    for plan in (_approved_plan(), _perps_plan(), _live_mode_plan(),
                 _missing_field_plan(), _non_d1_plan(), _alt_asset_plan()):
        e1 = evaluate_crypto_d1_offline_acquisition_plan(plan)
        e2 = evaluate_crypto_d1_offline_acquisition_plan(plan)
        assert e1 == e2
        c = _plan(plan=plan)
        assert c["offline_acquisition_plan_verdict"] == e1["verdict"]
        assert (
            tuple(c["offline_acquisition_plan_verdict_reasons"])
            == tuple(e1["reasons"])
        )


# 34 -- no authorization flag can become True (any state / any verdict).

def test_authorization_flags_always_false():
    states = [
        _plan(plan=_approved_plan()),
        _plan(plan=_perps_plan()),
        _plan(plan=_live_mode_plan()),
        _plan(plan=_missing_field_plan()),
        _plan(_blocked_sp(), _approved_plan()),
        build_crypto_d1_offline_acquisition_plan_contract({}),
    ]
    for c in states:
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["mode"] == "RESEARCH_ONLY"
        assert c["stage"] == "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_ONLY"


# 35 -- even an approved plan authorizes no execution surface.

def test_approved_plan_authorizes_no_execution_surface():
    c = _plan(plan=_approved_plan())
    assert (
        c["offline_acquisition_plan_verdict"]
        == "APPROVED_OFFLINE_ACQUISITION_PLAN"
    )
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


# 36 -- blocked capabilities include the required broad set.

def test_blocked_capabilities():
    c = _plan(plan=_approved_plan())
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 37 -- plan-specific blocked capabilities present.

def test_plan_blocked_capabilities_present():
    c = _plan(plan=_approved_plan())
    plan_blocked = set(c["offline_acquisition_plan_blocked_capabilities"])
    for cap in ("crypto_d1_offline_acquisition_plan_execution",
                "crypto_d1_data_acquisition", "crypto_d1_live_api_access",
                "crypto_d1_exchange_connection", "crypto_d1_broker_connection",
                "crypto_d1_dataset_read", "crypto_d1_data_inspection",
                "crypto_d1_qa_run", "crypto_d1_baseline_run",
                "crypto_d1_backtest", "real_strategy_intake",
                "report_file_write", "runtime_state_write"):
        assert cap in plan_blocked, cap


# 38 -- blocked execution items are exactly the three deferred items.

def test_blocked_execution_items_exact():
    c = _plan(plan=_approved_plan())
    assert tuple(c["blocked_execution_items"]) == BLOCKED_EXECUTION_ITEMS
    assert BLOCKED_EXECUTION_ITEMS == (
        "qa_run", "qa_pass_or_accepted_qa_warn", "baseline_backtest_output",
    )


# 39 -- remaining real-world capabilities are still blocked + exact.

def test_remaining_real_world_capabilities_blocked():
    c = _plan(plan=_approved_plan())
    remaining = set(c["remaining_real_world_capabilities_blocked"])
    for cap in ("real_strategy_intake", "real_data_acquisition",
                "real_data_inspection", "real_qa_run", "real_baseline_run",
                "real_backtest", "broker", "exchange", "order",
                "live_execution", "paper_execution", "autopilot",
                "automation", "upload", "deploy", "promotion"):
        assert cap in remaining, cap
    assert (
        tuple(c["remaining_real_world_capabilities_blocked"])
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


# 40 -- the embedded upstream source-spec contract is preserved.

def test_upstream_source_spec_embedded():
    sp = _approved_sp()
    c = build_crypto_d1_offline_acquisition_plan_contract(sp)
    embedded = c["crypto_d1_source_specification_contract"]
    assert embedded["crypto_d1_source_specification_contract_active"] is True
    assert embedded["read_only"] is True


# 41 -- the evaluated plan is echoed back (read-only copy).

def test_evaluated_plan_echoed():
    p = _approved_plan()
    c = _plan(plan=p)
    assert c["evaluated_offline_acquisition_plan"] == p
    c["evaluated_offline_acquisition_plan"]["market_type"] = "perp"
    assert p["market_type"] == "spot"


# 42 -- validate passes for a clean contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _plan(plan=_approved_plan())
    v = validate_crypto_d1_offline_acquisition_plan_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_crypto_d1_offline_acquisition_plan_contract(
        bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_crypto_d1_offline_acquisition_plan_contract(
        bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_crypto_d1_offline_acquisition_plan_contract(
        bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["stage"] = "EXECUTE"
    assert validate_crypto_d1_offline_acquisition_plan_contract(
        bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["human_approval_required"] = False
    assert validate_crypto_d1_offline_acquisition_plan_contract(
        bad5)["valid"] is False


# 43 -- validate flags wrong field tuples / collections.

def test_validate_flags_wrong_collections():
    import copy
    c = _plan(plan=_approved_plan())
    for key in ("allowed_offline_acquisition_plan_verdicts",
                "required_offline_acquisition_plan_fields",
                "plan_negative_safety_flags",
                "plan_forbidden_capability_flags",
                "allowed_asset_universe",
                "required_candle_fields",
                "allowed_timeframe",
                "allowed_offline_acquisition_modes",
                "allowed_offline_source_types",
                "blocked_execution_items",
                "remaining_real_world_capabilities_blocked"):
        bad = copy.deepcopy(c)
        bad[key] = ("not", "the", "right", "tuple")
        assert validate_crypto_d1_offline_acquisition_plan_contract(
            bad)["valid"] is False, key


# 44 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_plan(plan=_approved_plan()))
    c.pop("validation", None)
    v = validate_crypto_d1_offline_acquisition_plan_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 45 -- a blocked (await) contract still validates (safety shape).

def test_blocked_contract_still_validates():
    c = _plan(_blocked_sp(), _approved_plan())
    v = validate_crypto_d1_offline_acquisition_plan_contract(c)
    assert v["valid"] is True
    assert c["crypto_d1_offline_acquisition_plan_contract_active"] is False


# 46 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    import copy
    c = copy.deepcopy(_plan(plan=_approved_plan()))
    c.pop("crypto_d1_source_specification_contract", None)
    v = validate_crypto_d1_offline_acquisition_plan_contract(c)
    assert v["valid"] is False
    assert (
        "crypto_d1_source_specification_contract"
        in v["missing_required_fields"]
    )


# 47 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_plan_only_and_execution_free():
    c = _plan(plan=_approved_plan())
    md = render_crypto_d1_offline_acquisition_plan_contract_markdown(c)
    assert isinstance(md, str) and md
    assert (
        "# Strategy Factory Crypto-D1 Offline Acquisition Plan Contract" in md
    )
    for descriptor in ("crypto-d1-offline-acquisition-plan-contract-only",
                       "offline-plan-only", "no-live-api",
                       "no-data-acquisition", "no-qa-run", "no-baseline-run",
                       "no-data-inspection", "no-real-strategy-intake-yet",
                       "research-only", "execution-free"):
        assert descriptor in md, descriptor
    assert "Stage: CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "## Offline Acquisition Plan Proposal Reference" in md
    assert "## Offline Acquisition Plan Verdict Reasons" in md
    assert "## Allowed Offline Acquisition Plan Verdicts" in md
    assert "## Required Offline Acquisition Plan Fields" in md
    assert "## Plan Negative Safety Flags" in md
    assert "## Plan Forbidden Capability Flags" in md
    assert "## Allowed Asset Universe" in md
    assert "## Parked Market Types" in md
    assert "## Allowed Access Modes" in md
    assert "## Allowed Offline Acquisition Modes" in md
    assert "## Allowed Offline Source Types" in md
    assert "## Required Candle Fields" in md
    assert "## Allowed Timeframe" in md
    assert "## Offline Acquisition Plan Verdict Rationale" in md
    assert "## Blocked Execution Items" in md
    assert "## Offline Acquisition Plan Blocked Capabilities" in md
    assert "## Remaining Real-World Capabilities Blocked" in md
    assert "## Blocked Capabilities" in md
    assert "## Human Operator Required Next Steps" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 48 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 49 -- prose verb audit over notes / next-steps / placeholders / markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list = []
    c = _plan(plan=_approved_plan())

    texts.extend(str(x) for x in c["operator_notes"])
    texts.extend(str(x) for x in c["human_operator_required_next_steps"])
    texts.append(str(c["offline_acquisition_plan_reference_placeholder"]))
    texts.append(
        str(c["offline_acquisition_plan_verdict_rationale_placeholder"])
    )

    md = render_crypto_d1_offline_acquisition_plan_contract_markdown(c)
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


# 50 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 51 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_crypto_d1_offline_acquisition_plan_contract.py"'  # noqa: E501
        in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_offline_acquisition_plan_contract.py"'  # noqa: E501
        in src
    )


# 52 -- repeated builds are deterministic (no timestamp / random id).

def test_repeated_builds_are_deterministic():
    a = _plan(plan=_approved_plan())
    b = _plan(plan=_approved_plan())
    assert a == b


# 53 -- Bundle 44 regression import still works.

def test_bundle44_regression_import_still_works():
    sp = build_crypto_d1_source_specification_contract({})
    assert sp["executes"] is False
    assert sp["read_only"] is True
    assert sp["crypto_d1_source_specification_contract_active"] is False


# 54 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0

"""Bundle 46 tests for the Strategy Factory Crypto-D1 Pre-Acquisition Human
Approval Gate Contract v1 (informational, read-only, paper-only,
crypto-d1-pre-acquisition-human-approval-gate-only, human-approval-only,
deterministic, execution-free -- NO written report on disk, NO report file
write, NO data acquisition, NO data inspection, NO live API, NO exchange/broker
connection, NO QA run, NO QA verdict, NO baseline run, NO backtest, NO runtime
state write, NO real strategy intake, NO automated approval).

This bundle defines the crypto-d1 *pre-acquisition human approval gate*
evaluation contract. It activates only from an active Bundle 45 crypto-d1
offline acquisition plan contract whose offline_acquisition_plan_verdict is
APPROVED_OFFLINE_ACQUISITION_PLAN and whose next_gate is
CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED (the concrete
Bundle 45 signal that a pre-acquisition human approval gate is required next).
When active, it evaluates a paper human-approval packet and returns a
deterministic verdict; it acquires no data, approves nothing real, and unlocks
nothing.

Bundle 46's production module imports Bundle 45 via a real package import, so
these tests use normal package imports too. Running under ``python -m pytest``
places the repo root on ``sys.path`` so ``sparta_commander`` resolves.
"""

import ast
import copy
import pathlib
import re

from sparta_commander.strategy_factory_crypto_d1_pre_acquisition_human_gate_contract import (  # noqa: E501
    GATE_SCHEMA_VERSION,
    DEFAULT_GATE_LABEL,
    GATE_STATUS,
    GATE_SAFETY_POSTURE,
    GATE_STATE_ACTIVE,
    GATE_STATE_BLOCKED,
    GATE_VERDICT_READY,
    GATE_VERDICT_MISSING,
    GATE_VERDICT_INVALID,
    GATE_VERDICT_PARKED,
    GATE_VERDICT_AWAIT,
    ALLOWED_HUMAN_APPROVAL_VERDICTS,
    UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_VERDICT,
    UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_GATE,
    GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_REQUIRED,
    NEXT_GATE_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED,  # noqa: E501
    NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_PARKED,
    NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT,
    REQUIRED_HUMAN_APPROVAL_FIELDS,
    HUMAN_APPROVAL_REQUIRED_TEXT_FIELDS,
    HUMAN_APPROVAL_REQUIRED_AFFIRMATIONS,
    HUMAN_APPROVAL_FORBIDDEN_GRANT_FLAGS,
    AUTOMATED_APPROVAL_MARKERS,
    ALLOWED_ASSET_UNIVERSE,
    PARKED_MARKET_TYPES,
    ALLOWED_ACCESS_MODES,
    ALLOWED_OFFLINE_ACQUISITION_MODES,
    ALLOWED_OFFLINE_SOURCE_TYPES,
    REQUIRED_CANDLE_FIELDS,
    ALLOWED_TIMEFRAME,
    BLOCKED_EXECUTION_ITEMS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_pre_acquisition_human_approval,
    build_crypto_d1_pre_acquisition_human_gate_contract,
    validate_crypto_d1_pre_acquisition_human_gate_contract,
    render_crypto_d1_pre_acquisition_human_gate_contract_markdown,
)
import sparta_commander.strategy_factory_crypto_d1_pre_acquisition_human_gate_contract as GT  # noqa: E501
from sparta_commander.strategy_factory_crypto_d1_offline_acquisition_plan_contract import (  # noqa: E501
    PLAN_SCHEMA_VERSION,
    PLAN_VERDICT_APPROVED,
    build_crypto_d1_offline_acquisition_plan_contract,
)
from sparta_commander.strategy_factory_crypto_d1_source_specification_contract import (  # noqa: E501
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
    / "strategy_factory_crypto_d1_pre_acquisition_human_gate_contract.py"
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

_EXPECTED_POSTURE_KEYS = {
    "automation_enabled", "live_execution_enabled", "paper_execution_enabled",
    "file_write_enabled", "network_enabled", "subprocess_enabled",
    "strategy_promotion_enabled", "broker_enabled", "exchange_enabled",
    "order_enabled", "data_fetch_enabled", "backtest_enabled",
    "upload_enabled", "autopilot_enabled",
}

_EXPECTED_REQUIRED_FIELDS = (
    "approval_packet_id",
    "operator_name_or_id",
    "approval_timestamp",
    "approval_scope",
    "approved_plan_id",
    "approved_source_specification_id",
    "approved_assets",
    "approved_symbols",
    "approved_market_type",
    "approved_timeframe",
    "approved_coverage_window",
    "approved_acquisition_mode",
    "explicit_human_approval",
    "no_automation_approval",
    "no_live_fetch_approval",
    "no_api_key_approval",
    "no_account_access_approval",
    "no_order_capability_approval",
    "no_broker_exchange_approval",
    "no_qa_approval",
    "no_backtest_approval",
    "no_paper_live_approval",
    "no_runtime_write_approval",
    "no_registry_write_approval",
    "no_dashboard_write_approval",
    "risk_acknowledgement",
    "research_only_acknowledgement",
    "next_step_boundary",
)

_EXPECTED_TEXT_FIELDS = (
    "approval_packet_id",
    "operator_name_or_id",
    "approval_timestamp",
    "approval_scope",
    "approved_plan_id",
    "approved_source_specification_id",
    "approved_assets",
    "approved_symbols",
    "approved_market_type",
    "approved_timeframe",
    "approved_coverage_window",
    "approved_acquisition_mode",
    "next_step_boundary",
)

_EXPECTED_AFFIRMATIONS = (
    "explicit_human_approval",
    "no_automation_approval",
    "no_live_fetch_approval",
    "no_api_key_approval",
    "no_account_access_approval",
    "no_order_capability_approval",
    "no_broker_exchange_approval",
    "no_qa_approval",
    "no_backtest_approval",
    "no_paper_live_approval",
    "no_runtime_write_approval",
    "no_registry_write_approval",
    "no_dashboard_write_approval",
    "risk_acknowledgement",
    "research_only_acknowledgement",
)

_GATE_BLOCKED_REQUIRED = (
    "crypto_d1_pre_acquisition_human_gate_execution",
    "crypto_d1_data_acquisition",
    "crypto_d1_live_api_access",
    "crypto_d1_exchange_connection",
    "crypto_d1_broker_connection",
    "crypto_d1_dataset_read",
    "crypto_d1_data_inspection",
    "crypto_d1_qa_run",
    "crypto_d1_baseline_run",
    "crypto_d1_backtest",
    "real_strategy_intake",
    "report_file_write",
    "runtime_state_write",
    "approval_ledger_write",
    "auto_approval",
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


# --- upstream fake-lane chain (reused from Bundle 45 test) ------------------

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
    return build_crypto_d1_source_class_contract(
        _approved_acq(), source_class_proposal=_approved_sc_proposal())


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
    return build_crypto_d1_source_specification_contract(
        _approved_sc(), source_specification=_approved_spec_proposal())


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


def _missing_field_plan() -> dict:
    p = _approved_plan()
    del p["fee_model_plan"]
    return p


def _perps_plan() -> dict:
    p = _approved_plan()
    p["market_type"] = "perp"
    return p


def _live_mode_plan() -> dict:
    p = _approved_plan()
    p["acquisition_mode"] = "live_api"
    return p


# --- Bundle 45 contract builders -------------------------------------------

def _active_plan_contract() -> dict:
    """Active Bundle 45 plan contract, APPROVED at the pre-acquisition human
    gate -- the concrete signal Bundle 46 activates from."""
    return build_crypto_d1_offline_acquisition_plan_contract(
        _approved_sp(), offline_acquisition_plan=_approved_plan())


def _needs_more_plan_contract() -> dict:
    return build_crypto_d1_offline_acquisition_plan_contract(
        _approved_sp(), offline_acquisition_plan=_missing_field_plan())


def _parked_plan_contract() -> dict:
    return build_crypto_d1_offline_acquisition_plan_contract(
        _approved_sp(), offline_acquisition_plan=_perps_plan())


def _rejected_plan_contract() -> dict:
    return build_crypto_d1_offline_acquisition_plan_contract(
        _approved_sp(), offline_acquisition_plan=_live_mode_plan())


def _blocked_plan_contract() -> dict:
    return build_crypto_d1_offline_acquisition_plan_contract({})


# --- human-approval packet helpers -----------------------------------------

def _ready_packet() -> dict:
    return {
        "approval_packet_id": "appr-crypto-d1-001",
        "operator_name_or_id": "Mahmoud",
        "approval_timestamp": "2026-06-05T10:00:00Z",
        "approval_scope": "approve_exact_offline_acquisition_plan",
        "approved_plan_id": "BTC/ETH/SOL Daily Offline Fixture Plan",
        "approved_source_specification_id": "spec-crypto-d1-001",
        "approved_assets": ["BTC", "ETH", "SOL"],
        "approved_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "approved_market_type": "spot",
        "approved_timeframe": "D1",
        "approved_coverage_window": "2019-01-01 to 2025-01-01",
        "approved_acquisition_mode": "offline_fixture",
        "next_step_boundary": (
            "a later human-approved acquisition-execution contract only"
        ),
        "explicit_human_approval": True,
        "no_automation_approval": True,
        "no_live_fetch_approval": True,
        "no_api_key_approval": True,
        "no_account_access_approval": True,
        "no_order_capability_approval": True,
        "no_broker_exchange_approval": True,
        "no_qa_approval": True,
        "no_backtest_approval": True,
        "no_paper_live_approval": True,
        "no_runtime_write_approval": True,
        "no_registry_write_approval": True,
        "no_dashboard_write_approval": True,
        "risk_acknowledgement": True,
        "research_only_acknowledgement": True,
    }


def _gate(op=None, packet=None) -> dict:
    return build_crypto_d1_pre_acquisition_human_gate_contract(
        op if op is not None else _active_plan_contract(),
        human_approval_packet=packet,
    )


def _expected_public() -> set:
    return {
        "GATE_SCHEMA_VERSION",
        "DEFAULT_GATE_LABEL",
        "GATE_STATUS",
        "GATE_SAFETY_POSTURE",
        "GATE_STATE_ACTIVE",
        "GATE_STATE_BLOCKED",
        "GATE_VERDICT_READY",
        "GATE_VERDICT_MISSING",
        "GATE_VERDICT_INVALID",
        "GATE_VERDICT_PARKED",
        "GATE_VERDICT_AWAIT",
        "ALLOWED_HUMAN_APPROVAL_VERDICTS",
        "UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_VERDICT",
        "UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_GATE",
        "GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED",  # noqa: E501
        "NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_FIX_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_PARKED",
        "NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_REJECTED",
        "NEXT_GATE_AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT",
        "REQUIRED_HUMAN_APPROVAL_FIELDS",
        "HUMAN_APPROVAL_REQUIRED_TEXT_FIELDS",
        "HUMAN_APPROVAL_REQUIRED_AFFIRMATIONS",
        "HUMAN_APPROVAL_FORBIDDEN_GRANT_FLAGS",
        "AUTOMATED_APPROVAL_MARKERS",
        "ALLOWED_ASSET_UNIVERSE",
        "PARKED_MARKET_TYPES",
        "ALLOWED_ACCESS_MODES",
        "ALLOWED_OFFLINE_ACQUISITION_MODES",
        "ALLOWED_OFFLINE_SOURCE_TYPES",
        "REQUIRED_CANDLE_FIELDS",
        "ALLOWED_TIMEFRAME",
        "BLOCKED_EXECUTION_ITEMS",
        "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
        "evaluate_crypto_d1_pre_acquisition_human_approval",
        "build_crypto_d1_pre_acquisition_human_gate_contract",
        "validate_crypto_d1_pre_acquisition_human_gate_contract",
        "render_crypto_d1_pre_acquisition_human_gate_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(GT.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(GT, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        GATE_SCHEMA_VERSION
        == "strategy_factory_crypto_d1_pre_acquisition_human_gate_contract.v1"
    )
    assert (
        DEFAULT_GATE_LABEL
        == "Strategy Factory Crypto-D1 Pre-Acquisition Human Approval Gate "
           "Contract"
    )
    assert (
        GATE_STATUS
        == "READ_ONLY_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_CONTRACT"
    )


# 3 -- state constants pinned.

def test_state_constants_pinned():
    assert (
        GATE_STATE_ACTIVE
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_CONTRACT_ACTIVE"
    )
    assert (
        GATE_STATE_BLOCKED
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_CONTRACT_BLOCKED"
    )


# 4 -- verdict values are exactly the expected set + order.

def test_allowed_human_approval_verdicts_exact():
    assert ALLOWED_HUMAN_APPROVAL_VERDICTS == (
        "HUMAN_APPROVAL_READY",
        "HUMAN_APPROVAL_MISSING",
        "HUMAN_APPROVAL_INVALID",
        "HUMAN_APPROVAL_PARKED",
        "AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT",
    )
    assert GATE_VERDICT_READY == "HUMAN_APPROVAL_READY"
    assert GATE_VERDICT_MISSING == "HUMAN_APPROVAL_MISSING"
    assert GATE_VERDICT_INVALID == "HUMAN_APPROVAL_INVALID"
    assert GATE_VERDICT_PARKED == "HUMAN_APPROVAL_PARKED"
    assert (
        GATE_VERDICT_AWAIT
        == "AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT"
    )


# 5 -- the upstream Bundle 45 activation signal is pinned to the real values.

def test_upstream_activation_signal_pinned():
    assert (
        UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_VERDICT
        == PLAN_VERDICT_APPROVED
    )
    assert (
        UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_VERDICT
        == "APPROVED_OFFLINE_ACQUISITION_PLAN"
    )
    assert (
        UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_GATE
        == "CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED"
    )


# 6 -- conceptual gate + next-gate constants pinned.

def test_gate_and_next_gate_constants_pinned():
    assert (
        GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_REQUIRED
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED  # noqa: E501
        == "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED"  # noqa: E501
    )
    assert (
        NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_FIX_REQUIRED
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_FIX_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_PARKED
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_PARKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_REJECTED
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_REJECTED"
    )
    assert (
        NEXT_GATE_AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT
        == "AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT"
    )


# 7 -- required field collections pinned.

def test_required_field_collections_pinned():
    assert REQUIRED_HUMAN_APPROVAL_FIELDS == _EXPECTED_REQUIRED_FIELDS
    assert len(REQUIRED_HUMAN_APPROVAL_FIELDS) == 28
    assert HUMAN_APPROVAL_REQUIRED_TEXT_FIELDS == _EXPECTED_TEXT_FIELDS
    assert HUMAN_APPROVAL_REQUIRED_AFFIRMATIONS == _EXPECTED_AFFIRMATIONS
    assert len(HUMAN_APPROVAL_REQUIRED_AFFIRMATIONS) == 15
    # every text field + every affirmation appears in the full required set
    for f in HUMAN_APPROVAL_REQUIRED_TEXT_FIELDS:
        assert f in REQUIRED_HUMAN_APPROVAL_FIELDS
    for f in HUMAN_APPROVAL_REQUIRED_AFFIRMATIONS:
        assert f in REQUIRED_HUMAN_APPROVAL_FIELDS


# 8 -- forbidden grant flags + automated markers + inherited collections.

def test_forbidden_flags_and_markers_present():
    for flag in ("automated_approval", "live_fetch_approved",
                 "api_key_approved", "order_capability_approved",
                 "broker_exchange_approved", "qa_approved",
                 "backtest_approved", "execution_authorized"):
        assert flag in HUMAN_APPROVAL_FORBIDDEN_GRANT_FLAGS, flag
    for marker in ("automated", "auto", "bot", "robot", "script",
                   "machine", "cron", "scheduler", "system", "agent",
                   "llm", "ai"):
        assert marker in AUTOMATED_APPROVAL_MARKERS, marker
    assert ALLOWED_ASSET_UNIVERSE == ("BTC", "ETH", "SOL")
    assert ALLOWED_TIMEFRAME == ("D1",)
    assert REQUIRED_CANDLE_FIELDS == (
        "timestamp", "open", "high", "low", "close", "volume",
    )
    assert BLOCKED_EXECUTION_ITEMS == (
        "qa_run", "qa_pass_or_accepted_qa_warn", "baseline_backtest_output",
    )


# 9 -- pure stdlib import-root audit: allowed roots only.

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


# 10 -- forbidden-surface audit: no file/network/subprocess/exec/dynamic surface.

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


# 11 -- no filesystem read/write surface in source.

def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# 12 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = GATE_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 13 -- posture matches the inherited Bundle 45 posture.

def test_posture_matches_bundle45():
    from sparta_commander.strategy_factory_crypto_d1_offline_acquisition_plan_contract import (  # noqa: E501
        PLAN_SAFETY_POSTURE,
    )
    assert GATE_SAFETY_POSTURE == PLAN_SAFETY_POSTURE


# 14 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _gate(packet=_ready_packet())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _gate(packet=_ready_packet())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert GATE_SAFETY_POSTURE["automation_enabled"] is False


# 15 -- an active Bundle 45 APPROVED plan activates the gate contract.

def test_active_approved_plan_activates_gate():
    c = _gate(packet=_ready_packet())
    assert c["crypto_d1_pre_acquisition_human_gate_contract_active"] is True
    assert (
        c["crypto_d1_pre_acquisition_human_gate_contract_state"]
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_CONTRACT_ACTIVE"
    )
    assert c["crypto_d1_offline_acquisition_plan_contract_active"] is True
    assert (
        c["crypto_d1_offline_acquisition_plan_verdict"]
        == "APPROVED_OFFLINE_ACQUISITION_PLAN"
    )
    assert (
        c["crypto_d1_offline_acquisition_plan_next_gate"]
        == "CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED"
    )
    assert c["schema_version"] == GATE_SCHEMA_VERSION
    assert (
        c["crypto_d1_offline_acquisition_plan_schema_version"]
        == PLAN_SCHEMA_VERSION
    )
    assert (
        c["pre_acquisition_human_approval_gate_required"]
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_REQUIRED"
    )


# 16 -- an inactive (blocked) plan contract does not activate -> AWAIT.

def test_blocked_plan_does_not_activate():
    c = _gate(_blocked_plan_contract(), _ready_packet())
    assert c["crypto_d1_pre_acquisition_human_gate_contract_active"] is False
    assert (
        c["crypto_d1_pre_acquisition_human_gate_contract_state"]
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_CONTRACT_BLOCKED"
    )
    assert c["human_approval_verdict"] == GATE_VERDICT_AWAIT
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT"
    assert c["pre_acquisition_human_approval_gate_required"] == ""


# 17 -- an active NEEDS_MORE_INFO plan (wrong verdict) does not activate.

def test_needs_more_plan_does_not_activate():
    op = _needs_more_plan_contract()
    assert op["crypto_d1_offline_acquisition_plan_contract_active"] is True
    assert op["offline_acquisition_plan_verdict"] != PLAN_VERDICT_APPROVED
    c = _gate(op, _ready_packet())
    assert c["crypto_d1_pre_acquisition_human_gate_contract_active"] is False
    assert c["human_approval_verdict"] == GATE_VERDICT_AWAIT
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT"


# 18 -- an active PARKED plan does not activate.

def test_parked_plan_does_not_activate():
    op = _parked_plan_contract()
    assert op["crypto_d1_offline_acquisition_plan_contract_active"] is True
    assert op["offline_acquisition_plan_verdict"] != PLAN_VERDICT_APPROVED
    c = _gate(op, _ready_packet())
    assert c["crypto_d1_pre_acquisition_human_gate_contract_active"] is False
    assert c["human_approval_verdict"] == GATE_VERDICT_AWAIT


# 19 -- an active REJECTED plan does not activate.

def test_rejected_plan_does_not_activate():
    op = _rejected_plan_contract()
    assert op["crypto_d1_offline_acquisition_plan_contract_active"] is True
    assert op["offline_acquisition_plan_verdict"] != PLAN_VERDICT_APPROVED
    c = _gate(op, _ready_packet())
    assert c["crypto_d1_pre_acquisition_human_gate_contract_active"] is False
    assert c["human_approval_verdict"] == GATE_VERDICT_AWAIT


# 20 -- active APPROVED plan but tampered next_gate does not activate.

def test_wrong_plan_next_gate_does_not_activate():
    op = copy.deepcopy(_active_plan_contract())
    op["next_gate"] = "SOMETHING_ELSE"
    c = _gate(op, _ready_packet())
    assert c["crypto_d1_pre_acquisition_human_gate_contract_active"] is False
    assert c["human_approval_verdict"] == GATE_VERDICT_AWAIT


# 21 -- tampered plan verdict does not activate.

def test_wrong_plan_verdict_does_not_activate():
    op = copy.deepcopy(_active_plan_contract())
    op["offline_acquisition_plan_verdict"] = "NEEDS_MORE_INFO"
    c = _gate(op, _ready_packet())
    assert c["crypto_d1_pre_acquisition_human_gate_contract_active"] is False
    assert c["human_approval_verdict"] == GATE_VERDICT_AWAIT


# 22 -- inactive plan flag does not activate even with right verdict/gate.

def test_inactive_plan_flag_does_not_activate():
    op = copy.deepcopy(_active_plan_contract())
    op["crypto_d1_offline_acquisition_plan_contract_active"] = False
    c = _gate(op, _ready_packet())
    assert c["crypto_d1_pre_acquisition_human_gate_contract_active"] is False
    assert c["human_approval_verdict"] == GATE_VERDICT_AWAIT


# 23 -- malformed upstream input never raises and never activates.

def test_malformed_upstream_no_raise():
    for bad in (None, 42, "nope", {},
                {"crypto_d1_offline_acquisition_plan_contract_active": True},
                []):
        c = build_crypto_d1_pre_acquisition_human_gate_contract(bad)
        assert (
            c["crypto_d1_pre_acquisition_human_gate_contract_active"] is False
        )
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["human_approval_verdict"] == GATE_VERDICT_AWAIT
        assert (
            c["next_gate"]
            == "AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT"
        )
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 24 -- a full valid packet matching the plan yields READY + execution gate.

def test_ready_packet_maps_to_human_approved_execution_gate():
    c = _gate(packet=_ready_packet())
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_READY"
    assert (
        c["next_gate"]
        == "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED"  # noqa: E501
    )


# 25 -- an empty / missing packet yields MISSING + the fix gate.

def test_empty_packet_maps_to_missing():
    c = _gate(packet=None)
    assert c["crypto_d1_pre_acquisition_human_gate_contract_active"] is True
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_MISSING"
    assert (
        c["next_gate"]
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_FIX_REQUIRED"
    )
    assert (
        "human_approval_packet_missing"
        in c["human_approval_verdict_reasons"]
    )


# 26 -- an absent required affirmation yields MISSING (not invalid).

def test_absent_affirmation_maps_to_missing():
    p = _ready_packet()
    del p["explicit_human_approval"]
    c = _gate(packet=p)
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_MISSING"
    assert (
        "explicit_human_approval_must_be_affirmed_true"
        in c["human_approval_verdict_reasons"]
    )
    assert (
        c["next_gate"]
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_FIX_REQUIRED"
    )


# 27 -- an absent required text field yields MISSING.

def test_absent_text_field_maps_to_missing():
    p = _ready_packet()
    del p["approval_packet_id"]
    c = _gate(packet=p)
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_MISSING"
    assert (
        "approval_packet_id_required"
        in c["human_approval_verdict_reasons"]
    )


# 28 -- an automated approver identity is rejected (INVALID).

def test_automated_approver_rejected():
    p = _ready_packet()
    p["operator_name_or_id"] = "bot"
    c = _gate(packet=p)
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_INVALID"
    assert (
        c["next_gate"]
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_REJECTED"
    )
    assert any(
        r.startswith("automated_approver:")
        for r in c["human_approval_verdict_reasons"]
    )


# 29 -- an automated approval method is rejected (INVALID).

def test_automated_method_rejected():
    p = _ready_packet()
    p["approval_method"] = "automation"
    c = _gate(packet=p)
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_INVALID"


# 30 -- a forbidden positive grant flag is rejected (INVALID).

def test_forbidden_grant_flag_rejected():
    p = _ready_packet()
    p["live_fetch_approved"] = True
    c = _gate(packet=p)
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_INVALID"
    assert (
        "forbidden_grant:live_fetch_approved"
        in c["human_approval_verdict_reasons"]
    )


# 31 -- a present-but-unaffirmed safety affirmation is rejected (INVALID).

def test_present_but_unaffirmed_affirmation_rejected():
    p = _ready_packet()
    p["no_qa_approval"] = False
    c = _gate(packet=p)
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_INVALID"
    assert (
        "affirmation_not_affirmed:no_qa_approval"
        in c["human_approval_verdict_reasons"]
    )


# 32 -- a packet that mismatches the approved plan is rejected (INVALID).

def test_mismatched_packet_rejected():
    p = _ready_packet()
    p["approved_market_type"] = "perp"
    c = _gate(packet=p)
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_INVALID"
    assert (
        "mismatch:approved_market_type"
        in c["human_approval_verdict_reasons"]
    )


# 33 -- a mismatched symbol set is rejected (INVALID).

def test_mismatched_symbols_rejected():
    p = _ready_packet()
    p["approved_symbols"] = ["DOGEUSD"]
    c = _gate(packet=p)
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_INVALID"
    assert (
        "mismatch:approved_symbols"
        in c["human_approval_verdict_reasons"]
    )


# 34 -- an operator who explicitly parks/defers yields PARKED.

def test_operator_parks():
    p = _ready_packet()
    p["operator_decision"] = "park"
    c = _gate(packet=p)
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_PARKED"
    assert (
        c["next_gate"]
        == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_PARKED"
    )


# 35 -- safety beats parking: an unsafe parked packet is INVALID.

def test_unsafe_parked_packet_is_invalid_not_parked():
    p = _ready_packet()
    p["operator_decision"] = "park"
    p["live_fetch_approved"] = True
    c = _gate(packet=p)
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_INVALID"


# 36 -- parking beats completeness: a parked + incomplete packet is PARKED.

def test_parked_incomplete_packet_is_parked_not_missing():
    p = _ready_packet()
    p["operator_decision"] = "defer"
    del p["approval_packet_id"]
    c = _gate(packet=p)
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_PARKED"


# 37 -- the standalone evaluator is deterministic + matches the builder.

def test_evaluator_deterministic_and_matches_builder():
    ref = _active_plan_contract()["evaluated_offline_acquisition_plan"]
    parked = _ready_packet()
    parked["operator_decision"] = "park"
    invalid = _ready_packet()
    invalid["live_fetch_approved"] = True
    missing = _ready_packet()
    del missing["approval_packet_id"]
    for packet in (_ready_packet(), parked, invalid, missing, {}):
        e1 = evaluate_crypto_d1_pre_acquisition_human_approval(packet, ref)
        e2 = evaluate_crypto_d1_pre_acquisition_human_approval(packet, ref)
        assert e1 == e2
        c = _gate(packet=packet)
        assert c["human_approval_verdict"] == e1["verdict"]
        assert (
            tuple(c["human_approval_verdict_reasons"]) == tuple(e1["reasons"])
        )


# 38 -- no authorization flag can become True (any state / any verdict).

def test_authorization_flags_always_false():
    parked = _ready_packet()
    parked["operator_decision"] = "park"
    invalid = _ready_packet()
    invalid["live_fetch_approved"] = True
    states = [
        _gate(packet=_ready_packet()),
        _gate(packet=parked),
        _gate(packet=invalid),
        _gate(packet=None),
        _gate(_blocked_plan_contract(), _ready_packet()),
        build_crypto_d1_pre_acquisition_human_gate_contract({}),
    ]
    for c in states:
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["mode"] == "RESEARCH_ONLY"
        assert (
            c["stage"]
            == "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_ONLY"
        )


# 39 -- even a READY human approval authorizes no execution surface.

def test_ready_authorizes_no_execution_surface():
    c = _gate(packet=_ready_packet())
    assert c["human_approval_verdict"] == "HUMAN_APPROVAL_READY"
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
                "real_strategy_intake", "file_write", "file_read",
                "auto_approval", "approval_ledger_write"):
        assert cap in blocked, cap


# 40 -- blocked capabilities include the required broad set.

def test_blocked_capabilities_broad_set():
    c = _gate(packet=_ready_packet())
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 41 -- gate-specific blocked capabilities present + exact.

def test_gate_blocked_capabilities_present():
    c = _gate(packet=_ready_packet())
    gate_blocked = tuple(
        c["pre_acquisition_human_gate_blocked_capabilities"]
    )
    assert gate_blocked == _GATE_BLOCKED_REQUIRED


# 42 -- blocked execution items are exactly the three deferred items.

def test_blocked_execution_items_exact():
    c = _gate(packet=_ready_packet())
    assert tuple(c["blocked_execution_items"]) == BLOCKED_EXECUTION_ITEMS
    assert BLOCKED_EXECUTION_ITEMS == (
        "qa_run", "qa_pass_or_accepted_qa_warn", "baseline_backtest_output",
    )


# 43 -- remaining real-world capabilities are still blocked + exact.

def test_remaining_real_world_capabilities_blocked():
    c = _gate(packet=_ready_packet())
    assert (
        tuple(c["remaining_real_world_capabilities_blocked"])
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


# 44 -- the embedded upstream Bundle 45 plan contract is preserved.

def test_upstream_plan_embedded():
    op = _active_plan_contract()
    c = build_crypto_d1_pre_acquisition_human_gate_contract(op)
    embedded = c["crypto_d1_offline_acquisition_plan_contract"]
    assert embedded["crypto_d1_offline_acquisition_plan_contract_active"] is True
    assert embedded["read_only"] is True


# 45 -- the evaluated packet + referenced plan are echoed back (read-only copy).

def test_evaluated_packet_echoed():
    p = _ready_packet()
    c = _gate(packet=p)
    assert c["evaluated_human_approval_packet"] == p
    c["evaluated_human_approval_packet"]["approved_market_type"] = "perp"
    assert p["approved_market_type"] == "spot"
    ref = c["referenced_offline_acquisition_plan"]
    assert ref.get("market_type") == "spot"


# 46 -- validate passes for a clean contract + each failure mode.

def test_validate_passes_and_detects_failures():
    c = _gate(packet=_ready_packet())
    v = validate_crypto_d1_pre_acquisition_human_gate_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_crypto_d1_pre_acquisition_human_gate_contract(
        bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_crypto_d1_pre_acquisition_human_gate_contract(
        bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_crypto_d1_pre_acquisition_human_gate_contract(
        bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["stage"] = "EXECUTE"
    assert validate_crypto_d1_pre_acquisition_human_gate_contract(
        bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["human_approval_required"] = False
    assert validate_crypto_d1_pre_acquisition_human_gate_contract(
        bad5)["valid"] is False


# 47 -- validate flags wrong field tuples / collections.

def test_validate_flags_wrong_collections():
    c = _gate(packet=_ready_packet())
    for key in ("allowed_human_approval_verdicts",
                "required_human_approval_fields",
                "human_approval_required_text_fields",
                "human_approval_required_affirmations",
                "human_approval_forbidden_grant_flags",
                "automated_approval_markers",
                "allowed_asset_universe",
                "required_candle_fields",
                "allowed_timeframe",
                "allowed_offline_acquisition_modes",
                "allowed_offline_source_types",
                "blocked_execution_items",
                "remaining_real_world_capabilities_blocked"):
        bad = copy.deepcopy(c)
        bad[key] = ("not", "the", "right", "tuple")
        assert validate_crypto_d1_pre_acquisition_human_gate_contract(
            bad)["valid"] is False, key


# 48 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    c = copy.deepcopy(_gate(packet=_ready_packet()))
    c.pop("validation", None)
    v = validate_crypto_d1_pre_acquisition_human_gate_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 49 -- a blocked (await) contract still validates (safety shape).

def test_blocked_contract_still_validates():
    c = _gate(_blocked_plan_contract(), _ready_packet())
    v = validate_crypto_d1_pre_acquisition_human_gate_contract(c)
    assert v["valid"] is True
    assert c["crypto_d1_pre_acquisition_human_gate_contract_active"] is False


# 50 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    c = copy.deepcopy(_gate(packet=_ready_packet()))
    c.pop("crypto_d1_offline_acquisition_plan_contract", None)
    v = validate_crypto_d1_pre_acquisition_human_gate_contract(c)
    assert v["valid"] is False
    assert (
        "crypto_d1_offline_acquisition_plan_contract"
        in v["missing_required_fields"]
    )


# 51 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_gate_only_and_execution_free():
    c = _gate(packet=_ready_packet())
    md = render_crypto_d1_pre_acquisition_human_gate_contract_markdown(c)
    assert isinstance(md, str) and md
    assert (
        "# Strategy Factory Crypto-D1 Pre-Acquisition Human Approval Gate "
        "Contract" in md
    )
    for descriptor in (
        "crypto-d1-pre-acquisition-human-approval-gate-only",
        "human-approval-only", "no-live-api", "no-data-acquisition",
        "no-qa-run", "no-baseline-run", "no-data-inspection",
        "no-real-strategy-intake-yet", "research-only", "execution-free",
    ):
        assert descriptor in md, descriptor
    assert "Stage: CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    for section in (
        "## Human Approval Packet Reference",
        "## Human Approval Verdict Reasons",
        "## Allowed Human Approval Verdicts",
        "## Required Human Approval Fields",
        "## Human Approval Required Affirmations",
        "## Human Approval Forbidden Grant Flags",
        "## Automated Approval Markers",
        "## Allowed Asset Universe",
        "## Parked Market Types",
        "## Allowed Access Modes",
        "## Allowed Offline Acquisition Modes",
        "## Allowed Offline Source Types",
        "## Required Candle Fields",
        "## Allowed Timeframe",
        "## Human Approval Verdict Rationale",
        "## Blocked Execution Items",
        "## Pre-Acquisition Human Gate Blocked Capabilities",
        "## Remaining Real-World Capabilities Blocked",
        "## Blocked Capabilities",
        "## Human Operator Required Next Steps",
        "## Operator Notes",
        "## Safety",
        "## Validation",
        "## Next Gate",
    ):
        assert section in md, section


# 52 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 53 -- prose verb audit over notes / next-steps / placeholders / markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list = []
    c = _gate(packet=_ready_packet())

    texts.extend(str(x) for x in c["operator_notes"])
    texts.extend(str(x) for x in c["human_operator_required_next_steps"])
    texts.append(str(c["human_approval_packet_reference_placeholder"]))
    texts.append(
        str(c["human_approval_verdict_rationale_placeholder"])
    )

    md = render_crypto_d1_pre_acquisition_human_gate_contract_markdown(c)
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


# 54 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 55 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_crypto_d1_pre_acquisition_human_gate_contract.py"'  # noqa: E501
        in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_pre_acquisition_human_gate_contract.py"'  # noqa: E501
        in src
    )


# 56 -- repeated builds are deterministic (no timestamp / random id).

def test_repeated_builds_are_deterministic():
    a = _gate(packet=_ready_packet())
    b = _gate(packet=_ready_packet())
    assert a == b


# 57 -- Bundle 45 regression import still works.

def test_bundle45_regression_import_still_works():
    op = build_crypto_d1_offline_acquisition_plan_contract({})
    assert op["executes"] is False
    assert op["read_only"] is True
    assert op["crypto_d1_offline_acquisition_plan_contract_active"] is False


# 58 -- Bundle 44 regression import still works.

def test_bundle44_regression_import_still_works():
    sp = build_crypto_d1_source_specification_contract({})
    assert sp["executes"] is False
    assert sp["read_only"] is True
    assert sp["crypto_d1_source_specification_contract_active"] is False

"""Bundle 44 tests for the Strategy Factory Crypto-D1 Source Specification
Contract v1 (informational, read-only, paper-only,
source-specification-contract-only, offline-spec-only, deterministic,
execution-free -- NO written report on disk, NO report file write, NO data
acquisition, NO data inspection, NO live API, NO exchange/broker connection, NO
QA run, NO QA verdict, NO baseline run, NO backtest, NO runtime state write, NO
real strategy intake).

This bundle defines the crypto-d1 *source-specification* evaluation contract. It
activates only from an active Bundle 43 crypto-d1 source class contract whose
source_class_verdict is APPROVED_SOURCE_CLASS and whose next_gate is
CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED (the concrete Bundle 43
signal that a source specification contract is required next). When active, it
evaluates a paper source-specification proposal dict and returns a deterministic
verdict; it acquires no data and unlocks nothing real.

Bundle 44's production module imports Bundle 43 via a real package import, so
these tests use normal package imports too. Running under ``python -m pytest``
places the repo root on ``sys.path`` so ``sparta_commander`` resolves.
"""

import ast
import pathlib
import re

from sparta_commander.strategy_factory_crypto_d1_source_specification_contract import (  # noqa: E501
    SPEC_SCHEMA_VERSION,
    DEFAULT_SPEC_LABEL,
    SPEC_STATUS,
    SPEC_SAFETY_POSTURE,
    SPEC_STATE_ACTIVE,
    SPEC_STATE_BLOCKED,
    SPEC_VERDICT_APPROVED,
    SPEC_VERDICT_NEEDS_MORE_INFO,
    SPEC_VERDICT_PARKED,
    SPEC_VERDICT_REJECTED,
    SPEC_VERDICT_AWAIT,
    ALLOWED_SPEC_VERDICTS,
    NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED,
    NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_PARKED,
    NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT,
    REQUIRED_SPECIFICATION_FIELDS,
    SPEC_CAPABILITY_FLAGS,
    ALLOWED_ASSET_UNIVERSE,
    PARKED_MARKET_TYPES,
    ALLOWED_ACCESS_MODES,
    REQUIRED_CANDLE_FIELDS,
    ALLOWED_TIMEFRAME,
    FORBIDDEN_SPECIFICATION_CAPABILITIES,
    BLOCKED_EXECUTION_ITEMS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_source_specification,
    build_crypto_d1_source_specification_contract,
    validate_crypto_d1_source_specification_contract,
    render_crypto_d1_source_specification_contract_markdown,
)
import sparta_commander.strategy_factory_crypto_d1_source_specification_contract as SP  # noqa: E501
from sparta_commander.strategy_factory_crypto_d1_source_class_contract import (  # noqa: E501
    SOURCE_CLASS_SCHEMA_VERSION,
    SOURCE_CLASS_SAFETY_POSTURE,
    SOURCE_CLASS_VERDICT_APPROVED,
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
    / "strategy_factory_crypto_d1_source_specification_contract.py"
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
    "source_name",
    "source_class",
    "venue_or_vendor_name",
    "asset_universe",
    "symbols",
    "market_type",
    "timeframe",
    "candle_schema",
    "timestamp_column",
    "open_column",
    "high_column",
    "low_column",
    "close_column",
    "volume_column",
    "session_rule",
    "coverage_start",
    "coverage_end",
    "expected_frequency",
    "missing_candle_policy",
    "duplicate_timestamp_policy",
    "fee_model_assumption",
    "slippage_model_assumption",
    "provenance_required",
    "checksum_required",
    "freeze_manifest_required",
    "reproducibility_notes",
    "access_mode",
    "auth_required",
    "api_key_required",
    "live_fetch_allowed",
    "account_access_allowed",
    "order_capability_allowed",
    "broker_exchange_capability_allowed",
)

_EXPECTED_CAPABILITY_FLAGS = (
    "auth_required",
    "api_key_required",
    "live_fetch_allowed",
    "account_access_allowed",
    "order_capability_allowed",
    "broker_exchange_capability_allowed",
)


# --- upstream fake-lane chain (reused from Bundle 43 test) -----------------

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
    """Active acquire contract APPROVED at the source-class gate."""
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


def _perps_sc_proposal() -> dict:
    p = _approved_sc_proposal()
    p["market_type"] = "perp"
    return p


def _missing_sc_proposal() -> dict:
    p = _approved_sc_proposal()
    del p["coverage_window"]
    return p


# --- Bundle 43 source-class contract helpers (upstream of this bundle) ------

def _approved_sc() -> dict:
    """Active Bundle 43 source-class contract, APPROVED at the
    acquisition-plan gate -- the concrete signal Bundle 44 activates from."""
    return build_crypto_d1_source_class_contract(
        _approved_acq(), source_class_proposal=_approved_sc_proposal())


def _parked_sc() -> dict:
    """Active source-class contract with a PARKED (non-APPROVED) verdict."""
    return build_crypto_d1_source_class_contract(
        _approved_acq(), source_class_proposal=_perps_sc_proposal())


def _needs_more_sc() -> dict:
    """Active source-class contract with a NEEDS_MORE_INFO verdict."""
    return build_crypto_d1_source_class_contract(
        _approved_acq(), source_class_proposal=_missing_sc_proposal())


def _blocked_sc() -> dict:
    """Inactive source-class contract (no upstream acquire approval)."""
    return build_crypto_d1_source_class_contract({})


# --- source-specification proposal helpers ---------------------------------

def _approved_spec() -> dict:
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


def _perps_spec() -> dict:
    s = _approved_spec()
    s["market_type"] = "perp"
    return s


def _alt_asset_spec() -> dict:
    s = _approved_spec()
    s["asset_universe"] = ["DOGE", "XRP"]
    return s


def _auth_spec() -> dict:
    s = _approved_spec()
    s["auth_required"] = True
    return s


def _api_key_spec() -> dict:
    s = _approved_spec()
    s["api_key_required"] = True
    return s


def _live_fetch_spec() -> dict:
    s = _approved_spec()
    s["live_fetch_allowed"] = True
    return s


def _account_spec() -> dict:
    s = _approved_spec()
    s["account_access_allowed"] = True
    return s


def _order_spec() -> dict:
    s = _approved_spec()
    s["order_capability_allowed"] = True
    return s


def _broker_spec() -> dict:
    s = _approved_spec()
    s["broker_exchange_capability_allowed"] = True
    return s


def _live_access_mode_spec() -> dict:
    s = _approved_spec()
    s["access_mode"] = "live_api"
    return s


def _non_d1_spec() -> dict:
    s = _approved_spec()
    s["timeframe"] = "4h"
    return s


def _missing_provenance_spec() -> dict:
    s = _approved_spec()
    s["provenance_required"] = False
    return s


def _missing_checksum_spec() -> dict:
    s = _approved_spec()
    s["checksum_required"] = False
    return s


def _missing_freeze_spec() -> dict:
    s = _approved_spec()
    s["freeze_manifest_required"] = False
    return s


def _missing_field_spec() -> dict:
    s = _approved_spec()
    del s["fee_model_assumption"]
    return s


def _spec(sc=None, spec=None) -> dict:
    return build_crypto_d1_source_specification_contract(
        sc if sc is not None else _approved_sc(),
        source_specification=spec,
    )


def _expected_public() -> set:
    return {
        "SPEC_SCHEMA_VERSION",
        "DEFAULT_SPEC_LABEL",
        "SPEC_STATUS",
        "SPEC_SAFETY_POSTURE",
        "SPEC_STATE_ACTIVE",
        "SPEC_STATE_BLOCKED",
        "SPEC_VERDICT_APPROVED",
        "SPEC_VERDICT_NEEDS_MORE_INFO",
        "SPEC_VERDICT_PARKED",
        "SPEC_VERDICT_REJECTED",
        "SPEC_VERDICT_AWAIT",
        "ALLOWED_SPEC_VERDICTS",
        "NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_PARKED",
        "NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED",
        "NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT",
        "REQUIRED_SPECIFICATION_FIELDS",
        "SPEC_CAPABILITY_FLAGS",
        "ALLOWED_ASSET_UNIVERSE",
        "PARKED_MARKET_TYPES",
        "ALLOWED_ACCESS_MODES",
        "REQUIRED_CANDLE_FIELDS",
        "ALLOWED_TIMEFRAME",
        "FORBIDDEN_SPECIFICATION_CAPABILITIES",
        "BLOCKED_EXECUTION_ITEMS",
        "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
        "evaluate_crypto_d1_source_specification",
        "build_crypto_d1_source_specification_contract",
        "validate_crypto_d1_source_specification_contract",
        "render_crypto_d1_source_specification_contract_markdown",
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(SP.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(SP, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert (
        SPEC_SCHEMA_VERSION
        == "strategy_factory_crypto_d1_source_specification_contract.v1"
    )
    assert (
        DEFAULT_SPEC_LABEL
        == "Strategy Factory Crypto-D1 Source Specification Contract"
    )
    assert SPEC_STATUS == "READ_ONLY_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"


# 3 -- state / next-gate constants pinned.

def test_state_and_gate_constants_pinned():
    assert (
        SPEC_STATE_ACTIVE
        == "CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT_ACTIVE"
    )
    assert (
        SPEC_STATE_BLOCKED
        == "CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT_BLOCKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED
        == "CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED
        == "CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_PARKED
        == "CRYPTO_D1_SOURCE_SPECIFICATION_PARKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED
        == "CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED"
    )
    assert (
        NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT
        == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"
    )


# 4 -- source-specification verdict values are exactly the expected set + order.

def test_allowed_spec_verdicts_exact():
    assert ALLOWED_SPEC_VERDICTS == (
        "APPROVED_SOURCE_SPECIFICATION",
        "NEEDS_MORE_INFO",
        "PARKED_SOURCE_SPECIFICATION",
        "REJECTED_SOURCE_SPECIFICATION",
        "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT",
    )
    assert SPEC_VERDICT_APPROVED == "APPROVED_SOURCE_SPECIFICATION"
    assert SPEC_VERDICT_NEEDS_MORE_INFO == "NEEDS_MORE_INFO"
    assert SPEC_VERDICT_PARKED == "PARKED_SOURCE_SPECIFICATION"
    assert SPEC_VERDICT_REJECTED == "REJECTED_SOURCE_SPECIFICATION"
    assert SPEC_VERDICT_AWAIT == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"


# 5 -- required spec fields + capability flags + candle/asset/timeframe pinned.

def test_required_field_collections_pinned():
    assert REQUIRED_SPECIFICATION_FIELDS == _EXPECTED_REQUIRED_FIELDS
    assert SPEC_CAPABILITY_FLAGS == _EXPECTED_CAPABILITY_FLAGS
    assert REQUIRED_CANDLE_FIELDS == (
        "timestamp", "open", "high", "low", "close", "volume",
    )
    assert ALLOWED_ASSET_UNIVERSE == ("BTC", "ETH", "SOL")
    assert ALLOWED_TIMEFRAME == ("D1",)


# 6 -- pure stdlib import-root audit: allowed roots only.

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
    posture = SPEC_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 10 -- posture matches the inherited Bundle 43 posture.

def test_posture_matches_bundle43():
    assert SPEC_SAFETY_POSTURE == SOURCE_CLASS_SAFETY_POSTURE


# 11 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _spec(spec=_approved_spec())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _spec(spec=_approved_spec())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert SPEC_SAFETY_POSTURE["automation_enabled"] is False


# 12 -- an active Bundle 43 APPROVED source-class activates the spec contract.

def test_active_approved_source_class_activates_spec():
    c = _spec(spec=_approved_spec())
    assert c["crypto_d1_source_specification_contract_active"] is True
    assert (
        c["crypto_d1_source_specification_contract_state"]
        == "CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT_ACTIVE"
    )
    assert c["crypto_d1_source_class_contract_active"] is True
    assert c["crypto_d1_source_class_verdict"] == "APPROVED_SOURCE_CLASS"
    assert (
        c["crypto_d1_source_class_next_gate"]
        == "CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED"
    )
    assert c["schema_version"] == SPEC_SCHEMA_VERSION
    assert (
        c["crypto_d1_source_class_schema_version"]
        == SOURCE_CLASS_SCHEMA_VERSION
    )


# 13 -- an inactive (blocked) source-class does not activate.

def test_blocked_source_class_does_not_activate():
    c = _spec(_blocked_sc(), _approved_spec())
    assert c["crypto_d1_source_specification_contract_active"] is False
    assert (
        c["crypto_d1_source_specification_contract_state"]
        == "CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT_BLOCKED"
    )
    assert (
        c["source_specification_verdict"]
        == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"
    )
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"


# 14 -- an active but PARKED source-class (wrong verdict) does not activate.

def test_parked_source_class_does_not_activate():
    sc = _parked_sc()
    assert sc["crypto_d1_source_class_contract_active"] is True
    assert sc["source_class_verdict"] != SOURCE_CLASS_VERDICT_APPROVED
    c = _spec(sc, _approved_spec())
    assert c["crypto_d1_source_specification_contract_active"] is False
    assert (
        c["source_specification_verdict"]
        == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"
    )
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"


# 15 -- an active NEEDS_MORE_INFO source-class does not activate.

def test_needs_more_source_class_does_not_activate():
    sc = _needs_more_sc()
    assert sc["crypto_d1_source_class_contract_active"] is True
    assert sc["source_class_verdict"] != SOURCE_CLASS_VERDICT_APPROVED
    c = _spec(sc, _approved_spec())
    assert c["crypto_d1_source_specification_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"


# 16 -- active APPROVED source-class but tampered next_gate does not activate.

def test_wrong_source_class_next_gate_does_not_activate():
    import copy
    sc = copy.deepcopy(_approved_sc())
    sc["next_gate"] = "SOMETHING_ELSE"
    c = _spec(sc, _approved_spec())
    assert c["crypto_d1_source_specification_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"


# 17 -- tampered source-class verdict does not activate.

def test_wrong_source_class_verdict_does_not_activate():
    import copy
    sc = copy.deepcopy(_approved_sc())
    sc["source_class_verdict"] = "NEEDS_MORE_INFO"
    c = _spec(sc, _approved_spec())
    assert c["crypto_d1_source_specification_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"


# 18 -- inactive source-class flag does not activate even with right verdict/gate.

def test_inactive_source_class_flag_does_not_activate():
    import copy
    sc = copy.deepcopy(_approved_sc())
    sc["crypto_d1_source_class_contract_active"] = False
    c = _spec(sc, _approved_spec())
    assert c["crypto_d1_source_specification_contract_active"] is False
    assert c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"


# 19 -- malformed upstream input never raises and never activates.

def test_malformed_upstream_no_raise():
    for bad in (None, 42, "nope", {},
                {"crypto_d1_source_class_contract_active": True},
                []):
        c = build_crypto_d1_source_specification_contract(bad)
        assert c["crypto_d1_source_specification_contract_active"] is False
        assert c["read_only"] is True
        assert c["executes"] is False
        assert (
            c["source_specification_verdict"]
            == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"
        )
        assert c["next_gate"] == "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"
        for flag in _AUTH_FLAGS:
            assert c[flag] is False


# 20 -- an approved spec yields APPROVED + the acquisition-plan gate.

def test_approved_spec_maps_to_acquisition_plan_gate():
    c = _spec(spec=_approved_spec())
    assert c["source_specification_verdict"] == "APPROVED_SOURCE_SPECIFICATION"
    assert (
        c["next_gate"]
        == "CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED"
    )
    remaining = set(c["remaining_real_world_capabilities_blocked"])
    for cap in ("real_qa_run", "real_baseline_run", "real_backtest",
                "real_strategy_intake", "real_data_acquisition",
                "real_data_inspection"):
        assert cap in remaining, cap


# 21 -- a missing required field yields NEEDS_MORE_INFO + the fix gate.

def test_missing_field_maps_to_needs_more_info():
    c = _spec(spec=_missing_field_spec())
    assert c["source_specification_verdict"] == "NEEDS_MORE_INFO"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED"
    assert (
        "fee_model_assumption_required"
        in c["source_specification_verdict_reasons"]
    )


# 22 -- missing provenance / checksum / freeze-manifest -> NEEDS_MORE_INFO.

def test_missing_provenance_checksum_freeze_needs_more_info():
    for spec, reason in (
        (_missing_provenance_spec(), "provenance_required_true"),
        (_missing_checksum_spec(), "checksum_required_true"),
        (_missing_freeze_spec(), "freeze_manifest_required_true"),
    ):
        c = _spec(spec=spec)
        assert c["source_specification_verdict"] == "NEEDS_MORE_INFO"
        assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED"
        assert reason in c["source_specification_verdict_reasons"]


# 23 -- a perps/funding market parks (when otherwise safe).

def test_perps_market_parks():
    c = _spec(spec=_perps_spec())
    assert c["source_specification_verdict"] == "PARKED_SOURCE_SPECIFICATION"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_PARKED"


# 24 -- an alternative asset universe parks (plausible, not priority).

def test_alt_asset_universe_parks():
    c = _spec(spec=_alt_asset_spec())
    assert c["source_specification_verdict"] == "PARKED_SOURCE_SPECIFICATION"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_PARKED"


# 25 -- auth requirement is rejected (safety-first).

def test_auth_requirement_rejected():
    c = _spec(spec=_auth_spec())
    assert c["source_specification_verdict"] == "REJECTED_SOURCE_SPECIFICATION"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED"


# 26 -- API key requirement is rejected.

def test_api_key_requirement_rejected():
    c = _spec(spec=_api_key_spec())
    assert c["source_specification_verdict"] == "REJECTED_SOURCE_SPECIFICATION"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED"


# 27 -- live fetch capability is rejected.

def test_live_fetch_capability_rejected():
    c = _spec(spec=_live_fetch_spec())
    assert c["source_specification_verdict"] == "REJECTED_SOURCE_SPECIFICATION"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED"


# 28 -- account access capability is rejected.

def test_account_access_capability_rejected():
    c = _spec(spec=_account_spec())
    assert c["source_specification_verdict"] == "REJECTED_SOURCE_SPECIFICATION"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED"


# 29 -- order capability is rejected.

def test_order_capability_rejected():
    c = _spec(spec=_order_spec())
    assert c["source_specification_verdict"] == "REJECTED_SOURCE_SPECIFICATION"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED"


# 30 -- broker / exchange capability is rejected.

def test_broker_exchange_capability_rejected():
    c = _spec(spec=_broker_spec())
    assert c["source_specification_verdict"] == "REJECTED_SOURCE_SPECIFICATION"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED"


# 31 -- a live access mode is rejected.

def test_live_access_mode_rejected():
    c = _spec(spec=_live_access_mode_spec())
    assert c["source_specification_verdict"] == "REJECTED_SOURCE_SPECIFICATION"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED"
    assert "live_access_mode" in c["source_specification_verdict_reasons"]


# 32 -- perps PLUS a live capability is rejected (safety beats parking).

def test_perps_plus_live_is_rejected_not_parked():
    s = _perps_spec()
    s["live_fetch_allowed"] = True
    c = _spec(spec=s)
    assert c["source_specification_verdict"] == "REJECTED_SOURCE_SPECIFICATION"
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED"


# 33 -- a non-D1 timeframe is not approved (needs more info).

def test_non_d1_timeframe_not_approved():
    c = _spec(spec=_non_d1_spec())
    assert c["source_specification_verdict"] == "NEEDS_MORE_INFO"
    assert "d1_timeframe_required" in c["source_specification_verdict_reasons"]
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED"


# 34 -- an empty / missing spec yields NEEDS_MORE_INFO.

def test_empty_spec_needs_more_info():
    c = _spec(spec=None)
    assert c["source_specification_verdict"] == "NEEDS_MORE_INFO"
    assert (
        "source_specification_missing"
        in c["source_specification_verdict_reasons"]
    )
    assert c["next_gate"] == "CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED"


# 35 -- the standalone evaluator is deterministic + matches the builder.

def test_evaluator_deterministic_and_matches_builder():
    for spec in (_approved_spec(), _perps_spec(), _live_fetch_spec(),
                 _missing_field_spec(), _non_d1_spec(), _alt_asset_spec()):
        e1 = evaluate_crypto_d1_source_specification(spec)
        e2 = evaluate_crypto_d1_source_specification(spec)
        assert e1 == e2
        c = _spec(spec=spec)
        assert c["source_specification_verdict"] == e1["verdict"]
        assert (
            tuple(c["source_specification_verdict_reasons"])
            == tuple(e1["reasons"])
        )


# 36 -- no authorization flag can become True (any state / any verdict).

def test_authorization_flags_always_false():
    states = [
        _spec(spec=_approved_spec()),
        _spec(spec=_perps_spec()),
        _spec(spec=_live_fetch_spec()),
        _spec(spec=_missing_field_spec()),
        _spec(_blocked_sc(), _approved_spec()),
        build_crypto_d1_source_specification_contract({}),
    ]
    for c in states:
        for flag in _AUTH_FLAGS:
            assert c[flag] is False
        assert all(v is False for v in c["safety_posture"].values())
        assert c["executes"] is False
        assert c["read_only"] is True
        assert c["human_approval_required"] is True
        assert c["mode"] == "RESEARCH_ONLY"
        assert c["stage"] == "CRYPTO_D1_SOURCE_SPECIFICATION_ONLY"


# 37 -- even an approved specification authorizes no execution surface.

def test_approved_spec_authorizes_no_execution_surface():
    c = _spec(spec=_approved_spec())
    assert c["source_specification_verdict"] == "APPROVED_SOURCE_SPECIFICATION"
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


# 38 -- blocked capabilities include the required broad set.

def test_blocked_capabilities():
    c = _spec(spec=_approved_spec())
    blocked = set(c["blocked_capabilities"])
    for cap in _REQUIRED_BLOCKED:
        assert cap in blocked, cap


# 39 -- spec-specific blocked capabilities present.

def test_spec_blocked_capabilities_present():
    c = _spec(spec=_approved_spec())
    spec_blocked = set(c["source_specification_blocked_capabilities"])
    for cap in ("crypto_d1_source_specification_execution",
                "crypto_d1_data_acquisition", "crypto_d1_live_api_access",
                "crypto_d1_exchange_connection", "crypto_d1_broker_connection",
                "crypto_d1_dataset_read", "crypto_d1_data_inspection",
                "crypto_d1_qa_run", "crypto_d1_baseline_run",
                "crypto_d1_backtest", "real_strategy_intake",
                "report_file_write", "runtime_state_write"):
        assert cap in spec_blocked, cap


# 40 -- blocked execution items are exactly the three deferred items.

def test_blocked_execution_items_exact():
    c = _spec(spec=_approved_spec())
    assert tuple(c["blocked_execution_items"]) == BLOCKED_EXECUTION_ITEMS
    assert BLOCKED_EXECUTION_ITEMS == (
        "qa_run", "qa_pass_or_accepted_qa_warn", "baseline_backtest_output",
    )


# 41 -- remaining real-world capabilities are still blocked + exact.

def test_remaining_real_world_capabilities_blocked():
    c = _spec(spec=_approved_spec())
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


# 42 -- the embedded upstream source-class contract is preserved.

def test_upstream_source_class_embedded():
    sc = _approved_sc()
    c = build_crypto_d1_source_specification_contract(sc)
    embedded = c["crypto_d1_source_class_contract"]
    assert embedded["crypto_d1_source_class_contract_active"] is True
    assert embedded["read_only"] is True


# 43 -- the evaluated spec is echoed back (read-only copy).

def test_evaluated_spec_echoed():
    s = _approved_spec()
    c = _spec(spec=s)
    assert c["evaluated_source_specification"] == s
    c["evaluated_source_specification"]["market_type"] = "perp"
    assert s["market_type"] == "spot"


# 44 -- validate passes for a clean contract + each failure mode.

def test_validate_passes_and_detects_failures():
    import copy
    c = _spec(spec=_approved_spec())
    v = validate_crypto_d1_source_specification_contract(c)
    assert v["valid"] is True
    assert v["missing_required_fields"] == ()

    bad = copy.deepcopy(c)
    bad["execution_authorized"] = True
    assert validate_crypto_d1_source_specification_contract(
        bad)["valid"] is False

    bad2 = copy.deepcopy(c)
    bad2["safety_posture"]["network_enabled"] = True
    assert validate_crypto_d1_source_specification_contract(
        bad2)["valid"] is False

    bad3 = copy.deepcopy(c)
    bad3["mode"] = "LIVE"
    assert validate_crypto_d1_source_specification_contract(
        bad3)["valid"] is False

    bad4 = copy.deepcopy(c)
    bad4["stage"] = "EXECUTE"
    assert validate_crypto_d1_source_specification_contract(
        bad4)["valid"] is False

    bad5 = copy.deepcopy(c)
    bad5["human_approval_required"] = False
    assert validate_crypto_d1_source_specification_contract(
        bad5)["valid"] is False


# 45 -- validate flags wrong field tuples / collections.

def test_validate_flags_wrong_collections():
    import copy
    c = _spec(spec=_approved_spec())
    for key in ("allowed_source_specification_verdicts",
                "required_source_specification_fields",
                "spec_capability_flags",
                "allowed_asset_universe",
                "required_candle_fields",
                "allowed_timeframe",
                "blocked_execution_items",
                "remaining_real_world_capabilities_blocked",
                "forbidden_specification_capabilities"):
        bad = copy.deepcopy(c)
        bad[key] = ("not", "the", "right", "tuple")
        assert validate_crypto_d1_source_specification_contract(
            bad)["valid"] is False, key


# 46 -- validate never requires the contract's own validation field.

def test_validate_does_not_require_validation_field():
    import copy
    c = copy.deepcopy(_spec(spec=_approved_spec()))
    c.pop("validation", None)
    v = validate_crypto_d1_source_specification_contract(c)
    assert "validation" not in v["missing_required_fields"]
    assert v["valid"] is True


# 47 -- a blocked (await) contract still validates (safety shape).

def test_blocked_contract_still_validates():
    c = _spec(_blocked_sc(), _approved_spec())
    v = validate_crypto_d1_source_specification_contract(c)
    assert v["valid"] is True
    assert c["crypto_d1_source_specification_contract_active"] is False


# 48 -- validate flags missing required top-level fields.

def test_validate_flags_missing_required_fields():
    import copy
    c = copy.deepcopy(_spec(spec=_approved_spec()))
    c.pop("crypto_d1_source_class_contract", None)
    v = validate_crypto_d1_source_specification_contract(c)
    assert v["valid"] is False
    assert (
        "crypto_d1_source_class_contract"
        in v["missing_required_fields"]
    )


# 49 -- markdown non-empty, says the required descriptors + sections.

def test_markdown_spec_only_and_execution_free():
    c = _spec(spec=_approved_spec())
    md = render_crypto_d1_source_specification_contract_markdown(c)
    assert isinstance(md, str) and md
    assert (
        "# Strategy Factory Crypto-D1 Source Specification Contract" in md
    )
    for descriptor in ("crypto-d1-source-specification-contract-only",
                       "offline-spec-only", "no-live-api",
                       "no-data-acquisition", "no-qa-run", "no-baseline-run",
                       "no-data-inspection", "no-real-strategy-intake-yet",
                       "research-only", "execution-free"):
        assert descriptor in md, descriptor
    assert "Stage: CRYPTO_D1_SOURCE_SPECIFICATION_ONLY" in md
    assert "Mode: RESEARCH_ONLY" in md
    assert "Read only: True" in md
    assert "Executes: False" in md
    assert "## Source Specification Proposal Reference" in md
    assert "## Source Specification Verdict Reasons" in md
    assert "## Allowed Source Specification Verdicts" in md
    assert "## Required Source Specification Fields" in md
    assert "## Specification Capability Flags" in md
    assert "## Allowed Asset Universe" in md
    assert "## Parked Market Types" in md
    assert "## Allowed Access Modes" in md
    assert "## Required Candle Fields" in md
    assert "## Allowed Timeframe" in md
    assert "## Forbidden Specification Capabilities" in md
    assert "## Source Specification Verdict Rationale" in md
    assert "## Blocked Execution Items" in md
    assert "## Source Specification Blocked Capabilities" in md
    assert "## Remaining Real-World Capabilities Blocked" in md
    assert "## Blocked Capabilities" in md
    assert "## Human Operator Required Next Steps" in md
    assert "## Operator Notes" in md
    assert "## Safety" in md
    assert "## Validation" in md
    assert "## Next Gate" in md


# 50 -- markdown renderer writes nothing (no file surface in module source).

def test_markdown_renderer_writes_nothing():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", "write_text(", "write_bytes("):
        assert tok not in src


# 51 -- prose verb audit over notes / next-steps / placeholders / markdown.

def test_prose_has_no_execution_or_trading_verb():
    texts: list = []
    c = _spec(spec=_approved_spec())

    texts.extend(str(x) for x in c["operator_notes"])
    texts.extend(str(x) for x in c["human_operator_required_next_steps"])
    texts.append(str(c["source_specification_reference_placeholder"]))
    texts.append(str(c["source_specification_verdict_rationale_placeholder"]))

    md = render_crypto_d1_source_specification_contract_markdown(c)
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


# 52 -- scoped dirty-tree guard: this bundle needs no brain_memory edits.

def test_bundle_scope_excludes_brain_memory():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "brain_memory" not in src


# 53 -- commander_2_safety allowlist includes the new module + test paths.

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_crypto_d1_source_specification_contract.py"'  # noqa: E501
        in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_source_specification_contract.py"'  # noqa: E501
        in src
    )


# 54 -- repeated builds are deterministic (no timestamp / random id).

def test_repeated_builds_are_deterministic():
    a = _spec(spec=_approved_spec())
    b = _spec(spec=_approved_spec())
    assert a == b


# 55 -- Bundle 43 regression import still works.

def test_bundle43_regression_import_still_works():
    sc = build_crypto_d1_source_class_contract({})
    assert sc["executes"] is False
    assert sc["read_only"] is True
    assert sc["crypto_d1_source_class_contract_active"] is False


# 56 -- Bundle 11 regression import still works.

def test_bundle11_regression_import_still_works():
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue,
    )
    q = build_research_queue((_good_item(),))
    assert q["executes"] is False
    assert q["approved_for_research_count"] == 0

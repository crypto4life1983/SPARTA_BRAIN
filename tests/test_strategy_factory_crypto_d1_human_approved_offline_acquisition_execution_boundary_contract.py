"""Bundle 47 tests for the Strategy Factory Crypto-D1 Human-Approved Offline
Acquisition Execution Boundary Contract v1 (informational, read-only,
paper-only, crypto-d1-execution-boundary-only, offline-only, deterministic,
execution-free -- NO written report on disk, NO report file write, NO data
acquisition, NO data inspection, NO live API, NO exchange/broker connection, NO
QA run, NO QA verdict, NO baseline run, NO backtest, NO simulation, NO runtime
state write, NO real strategy intake, NO automation).

This bundle defines the crypto-d1 *execution boundary* contract. It activates
only from an active Bundle 46 crypto-d1 pre-acquisition human approval gate
contract whose human_approval_verdict is HUMAN_APPROVAL_READY and whose
next_gate is
CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED (the
concrete Bundle 46 signal that an execution-boundary contract is required
next). When active, it evaluates a paper execution-boundary packet and returns
a deterministic verdict; it acquires no data, authorizes nothing real, and
unlocks nothing.

Bundle 47's production module imports Bundle 46 via a real package import, so
these tests use normal package imports too. Running under ``python -m pytest``
places the repo root on ``sys.path`` so ``sparta_commander`` resolves. Most
tests drive the boundary from a synthetic Bundle 46 gate dict; a single
real-integration test drives it from a genuine Bundle 46 READY gate built from
the full upstream fake-lane + crypto-d1 chain.
"""

import ast
import copy
import pathlib

from sparta_commander.strategy_factory_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract import (  # noqa: E501
    BOUNDARY_SCHEMA_VERSION,
    DEFAULT_BOUNDARY_LABEL,
    BOUNDARY_STATUS,
    BOUNDARY_SAFETY_POSTURE,
    BOUNDARY_STATE_ACTIVE,
    BOUNDARY_STATE_BLOCKED,
    BOUNDARY_VERDICT_READY,
    BOUNDARY_VERDICT_NEEDS_MORE_INFO,
    BOUNDARY_VERDICT_REJECTED,
    BOUNDARY_VERDICT_PARKED,
    BOUNDARY_VERDICT_AWAIT,
    ALLOWED_EXECUTION_BOUNDARY_VERDICTS,
    UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_VERDICT,
    UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_GATE,
    BOUNDARY_CRYPTO_D1_EXECUTION_BOUNDARY_REQUIRED,
    NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED,  # noqa: E501
    NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_PARKED,
    NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE,
    REQUIRED_EXECUTION_BOUNDARY_FIELDS,
    EXECUTION_BOUNDARY_REQUIRED_TEXT_FIELDS,
    EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS,
    EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES,
    EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS,
    EXECUTION_BOUNDARY_FORBIDDEN_ALLOW_FLAGS,
    ALLOWED_EXECUTION_MODES,
    ALLOWED_ACQUISITION_METHODS,
    ALLOWED_DESTINATION_TYPES,
    AUTOMATED_APPROVAL_MARKERS,
    ALLOWED_ASSET_UNIVERSE,
    REQUIRED_CANDLE_FIELDS,
    ALLOWED_TIMEFRAME,
    BLOCKED_EXECUTION_ITEMS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_human_approved_offline_acquisition_execution_boundary as EVAL,  # noqa: E501
    build_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract as BUILD,  # noqa: E501
    validate_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract as VALIDATE,  # noqa: E501
    render_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract_markdown as RENDER,  # noqa: E501
)
import sparta_commander.strategy_factory_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract as BO  # noqa: E501
from sparta_commander.strategy_factory_crypto_d1_pre_acquisition_human_gate_contract import (  # noqa: E501
    GATE_SCHEMA_VERSION,
    GATE_VERDICT_READY,
    build_crypto_d1_pre_acquisition_human_gate_contract,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract.py"  # noqa: E501
)

_EXPECTED_POSTURE_KEYS = {
    "automation_enabled", "live_execution_enabled", "paper_execution_enabled",
    "file_write_enabled", "network_enabled", "subprocess_enabled",
    "strategy_promotion_enabled", "broker_enabled", "exchange_enabled",
    "order_enabled", "data_fetch_enabled", "backtest_enabled",
    "upload_enabled", "autopilot_enabled",
}

_AUTH_FLAGS = (
    "approved_for_research", "execution_authorized",
    "paper_trading_authorized", "live_trading_authorized",
    "data_fetch_authorized", "backtest_authorized", "promotion_authorized",
)

_EXPECTED_REQUIRED_FIELDS = (
    "boundary_packet_id",
    "approved_human_gate_id",
    "approved_plan_id",
    "approved_source_specification_id",
    "execution_mode",
    "execution_scope",
    "acquisition_method",
    "allowed_input_contracts",
    "allowed_output_artifacts",
    "allowed_destination_type",
    "prohibited_live_fetch",
    "prohibited_api_keys",
    "prohibited_account_access",
    "prohibited_order_capability",
    "prohibited_broker_exchange_capability",
    "prohibited_qa_run",
    "prohibited_baseline_run",
    "prohibited_backtest_run",
    "prohibited_simulation_run",
    "prohibited_paper_live",
    "prohibited_automation_trigger",
    "prohibited_runtime_write",
    "prohibited_registry_write",
    "prohibited_dashboard_write",
    "provenance_output_required",
    "checksum_output_required",
    "freeze_manifest_output_required",
    "operator_reconfirmation_required",
    "dry_run_description_required",
    "no_side_effects_acknowledgement",
    "next_step_boundary",
)


# --- synthetic Bundle 46 READY gate + boundary-packet helpers ---------------

def _ref_packet() -> dict:
    """The approved human-approval packet a Bundle 46 READY gate echoes."""
    return {
        "approval_packet_id": "appr-crypto-d1-001",
        "approved_plan_id": "BTC/ETH/SOL Daily Offline Fixture Plan",
        "approved_source_specification_id": "spec-crypto-d1-001",
    }


def _synthetic_gate(
    active: bool = True,
    verdict: str = "HUMAN_APPROVAL_READY",
    next_gate: str = (
        "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED"  # noqa: E501
    ),
    ref: dict | None = None,
) -> dict:
    """A synthetic Bundle 46 gate dict shaped exactly as Bundle 47 reads it."""
    return {
        "crypto_d1_pre_acquisition_human_gate_contract_active": active,
        "human_approval_verdict": verdict,
        "next_gate": next_gate,
        "evaluated_human_approval_packet": (
            _ref_packet() if ref is None else ref
        ),
        "idea_id": "idea-001",
        "title": "Opening Range Mean Reversion",
        "asset_lane": "BTC,ETH,SOL",
        "timeframe_lane": "D1",
    }


def _ready_boundary_packet() -> dict:
    """A complete, valid, offline-only execution-boundary packet."""
    p = {
        "boundary_packet_id": "boundary-crypto-d1-001",
        "approved_human_gate_id": "appr-crypto-d1-001",
        "approved_plan_id": "BTC/ETH/SOL Daily Offline Fixture Plan",
        "approved_source_specification_id": "spec-crypto-d1-001",
        "execution_mode": "offline_only",
        "execution_scope": "load one frozen offline fixture set, nothing else",
        "acquisition_method": "offline_fixture",
        "allowed_input_contracts": [
            "BTC/ETH/SOL Daily Offline Fixture Plan",
            "spec-crypto-d1-001",
        ],
        "allowed_output_artifacts": [
            "frozen_offline_dataset", "provenance_record", "checksum_record",
        ],
        "allowed_destination_type": "frozen_offline_artifact",
        "next_step_boundary": (
            "a separate, later, human-run acquisition-execution step only"
        ),
    }
    for flag in EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS:
        p[flag] = True
    for flag in EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES:
        p[flag] = True
    for flag in EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS:
        p[flag] = True
    return p


def _boundary(gate: dict | None = None, packet: dict | None = None) -> dict:
    return BUILD(
        gate if gate is not None else _synthetic_gate(),
        execution_boundary_packet=packet,
    )


def _expected_public() -> set:
    return {
        "BOUNDARY_SCHEMA_VERSION",
        "DEFAULT_BOUNDARY_LABEL",
        "BOUNDARY_STATUS",
        "BOUNDARY_SAFETY_POSTURE",
        "BOUNDARY_STATE_ACTIVE",
        "BOUNDARY_STATE_BLOCKED",
        "BOUNDARY_VERDICT_READY",
        "BOUNDARY_VERDICT_NEEDS_MORE_INFO",
        "BOUNDARY_VERDICT_REJECTED",
        "BOUNDARY_VERDICT_PARKED",
        "BOUNDARY_VERDICT_AWAIT",
        "ALLOWED_EXECUTION_BOUNDARY_VERDICTS",
        "UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_VERDICT",
        "UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_GATE",
        "BOUNDARY_CRYPTO_D1_EXECUTION_BOUNDARY_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED",  # noqa: E501
        "NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_FIX_REQUIRED",
        "NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_PARKED",
        "NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_REJECTED",
        "NEXT_GATE_AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE",
        "REQUIRED_EXECUTION_BOUNDARY_FIELDS",
        "EXECUTION_BOUNDARY_REQUIRED_TEXT_FIELDS",
        "EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS",
        "EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES",
        "EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS",
        "EXECUTION_BOUNDARY_FORBIDDEN_ALLOW_FLAGS",
        "ALLOWED_EXECUTION_MODES",
        "ALLOWED_ACQUISITION_METHODS",
        "ALLOWED_DESTINATION_TYPES",
        "AUTOMATED_APPROVAL_MARKERS",
        "ALLOWED_ASSET_UNIVERSE",
        "REQUIRED_CANDLE_FIELDS",
        "ALLOWED_TIMEFRAME",
        "BLOCKED_EXECUTION_ITEMS",
        "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
        "evaluate_crypto_d1_human_approved_offline_acquisition_execution_boundary",  # noqa: E501
        "build_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract",  # noqa: E501
        "validate_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract",  # noqa: E501
        "render_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract_markdown",  # noqa: E501
    }


# 1 -- module imports cleanly + public API limited to expected names.

def test_public_api_is_limited_to_expected_names():
    assert set(BO.__all__) == _expected_public()
    for name in _expected_public():
        assert hasattr(BO, name)


# 2 -- schema / label / status pinned.

def test_schema_label_status_pinned():
    assert BOUNDARY_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_human_approved_offline_acquisition_"
        "execution_boundary_contract.v1"
    )
    assert DEFAULT_BOUNDARY_LABEL == (
        "Strategy Factory Crypto-D1 Human-Approved Offline Acquisition "
        "Execution Boundary Contract"
    )
    assert BOUNDARY_STATUS == (
        "READ_ONLY_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_"
        "BOUNDARY_CONTRACT"
    )


# 3 -- state constants pinned.

def test_state_constants_pinned():
    assert BOUNDARY_STATE_ACTIVE == (
        "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_"
        "CONTRACT_ACTIVE"
    )
    assert BOUNDARY_STATE_BLOCKED == (
        "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_"
        "CONTRACT_BLOCKED"
    )


# 4 -- verdict values are exactly the expected set + order.

def test_allowed_execution_boundary_verdicts_exact():
    assert ALLOWED_EXECUTION_BOUNDARY_VERDICTS == (
        "EXECUTION_BOUNDARY_READY",
        "EXECUTION_BOUNDARY_NEEDS_MORE_INFO",
        "EXECUTION_BOUNDARY_REJECTED",
        "EXECUTION_BOUNDARY_PARKED",
        "AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE",
    )
    assert BOUNDARY_VERDICT_READY == "EXECUTION_BOUNDARY_READY"
    assert BOUNDARY_VERDICT_NEEDS_MORE_INFO == "EXECUTION_BOUNDARY_NEEDS_MORE_INFO"
    assert BOUNDARY_VERDICT_REJECTED == "EXECUTION_BOUNDARY_REJECTED"
    assert BOUNDARY_VERDICT_PARKED == "EXECUTION_BOUNDARY_PARKED"
    assert BOUNDARY_VERDICT_AWAIT == (
        "AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE"
    )


# 5 -- the upstream Bundle 46 activation signal is pinned to the real values.

def test_upstream_activation_signal_pinned():
    assert (
        UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_VERDICT
        == GATE_VERDICT_READY
    )
    assert (
        UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_VERDICT
        == "HUMAN_APPROVAL_READY"
    )
    assert (
        UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_GATE
        == "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED"  # noqa: E501
    )


# 6 -- conceptual boundary + next-gate constants pinned.

def test_boundary_and_next_gate_constants_pinned():
    assert BOUNDARY_CRYPTO_D1_EXECUTION_BOUNDARY_REQUIRED == (
        "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_REQUIRED"  # noqa: E501
    )
    assert (
        NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED  # noqa: E501
        == "CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_FIX_REQUIRED
        == "CRYPTO_D1_EXECUTION_BOUNDARY_FIX_REQUIRED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_PARKED
        == "CRYPTO_D1_EXECUTION_BOUNDARY_PARKED"
    )
    assert (
        NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_REJECTED
        == "CRYPTO_D1_EXECUTION_BOUNDARY_REJECTED"
    )
    assert (
        NEXT_GATE_AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE
        == "AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE"
    )


# 7 -- required field collections pinned, 31 fields in instruction order.

def test_required_field_collections_pinned():
    assert REQUIRED_EXECUTION_BOUNDARY_FIELDS == _EXPECTED_REQUIRED_FIELDS
    assert len(REQUIRED_EXECUTION_BOUNDARY_FIELDS) == 31
    assert len(EXECUTION_BOUNDARY_REQUIRED_TEXT_FIELDS) == 11
    assert len(EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS) == 14
    assert len(EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES) == 3
    assert len(EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS) == 3
    for f in EXECUTION_BOUNDARY_REQUIRED_TEXT_FIELDS:
        assert f in REQUIRED_EXECUTION_BOUNDARY_FIELDS
    for f in EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS:
        assert f in REQUIRED_EXECUTION_BOUNDARY_FIELDS
    for f in EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES:
        assert f in REQUIRED_EXECUTION_BOUNDARY_FIELDS
    for f in EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS:
        assert f in REQUIRED_EXECUTION_BOUNDARY_FIELDS


# 8 -- the 14 prohibitions cover every dangerous capability.

def test_prohibitions_cover_dangerous_capabilities():
    for flag in (
        "prohibited_live_fetch", "prohibited_api_keys",
        "prohibited_account_access", "prohibited_order_capability",
        "prohibited_broker_exchange_capability", "prohibited_qa_run",
        "prohibited_baseline_run", "prohibited_backtest_run",
        "prohibited_simulation_run", "prohibited_paper_live",
        "prohibited_automation_trigger", "prohibited_runtime_write",
        "prohibited_registry_write", "prohibited_dashboard_write",
    ):
        assert flag in EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS, flag


# 9 -- output rules + affirmations pinned.

def test_output_rules_and_affirmations_pinned():
    assert EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES == (
        "provenance_output_required",
        "checksum_output_required",
        "freeze_manifest_output_required",
    )
    assert EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS == (
        "operator_reconfirmation_required",
        "dry_run_description_required",
        "no_side_effects_acknowledgement",
    )


# 10 -- forbidden allow flags + automated markers + inherited collections.

def test_forbidden_flags_and_markers_present():
    for flag in (
        "allow_live_fetch", "allow_api_keys", "allow_account_access",
        "allow_order_capability", "allow_broker_exchange", "allow_qa_run",
        "allow_baseline_run", "allow_backtest_run", "allow_simulation_run",
        "allow_paper_live", "allow_automation_trigger", "allow_runtime_write",
        "allow_registry_write", "allow_dashboard_write", "side_effects_allowed",
        "execution_authorized", "live_execution_authorized",
        "autopilot_enabled",
    ):
        assert flag in EXECUTION_BOUNDARY_FORBIDDEN_ALLOW_FLAGS, flag
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


# 11 -- allowed enums are strict offline-only sets.

def test_allowed_enums_are_offline_only():
    assert "offline_only" in ALLOWED_EXECUTION_MODES
    assert "live" not in ALLOWED_EXECUTION_MODES
    assert "live_api" not in ALLOWED_EXECUTION_MODES
    assert "offline_fixture" in ALLOWED_ACQUISITION_METHODS
    assert "live_api" not in ALLOWED_ACQUISITION_METHODS
    assert "frozen_offline_artifact" in ALLOWED_DESTINATION_TYPES
    for d in ALLOWED_DESTINATION_TYPES:
        assert "live" not in d and "broker" not in d and "exchange" not in d


# 12 -- pure stdlib import-root audit: allowed roots only.

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


# 13 -- forbidden-surface audit: no file/network/subprocess/exec/dynamic surface.

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


# 14 -- no filesystem read/write surface in source.

def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# 15 -- all 14 posture keys present + all False.

def test_posture_keys_present_and_all_false():
    posture = BOUNDARY_SAFETY_POSTURE
    assert set(posture.keys()) == _EXPECTED_POSTURE_KEYS
    assert len(posture) == 14
    assert all(v is False for v in posture.values())


# 16 -- posture matches the inherited Bundle 46 posture.

def test_posture_matches_bundle46():
    from sparta_commander.strategy_factory_crypto_d1_pre_acquisition_human_gate_contract import (  # noqa: E501
        GATE_SAFETY_POSTURE,
    )
    assert BOUNDARY_SAFETY_POSTURE == GATE_SAFETY_POSTURE


# 17 -- posture mutation-isolated across calls.

def test_posture_mutation_isolated():
    a = _boundary(packet=_ready_boundary_packet())
    a["safety_posture"]["automation_enabled"] = True
    a["read_only"] = False
    fresh = _boundary(packet=_ready_boundary_packet())
    assert fresh["safety_posture"]["automation_enabled"] is False
    assert fresh["read_only"] is True
    assert BOUNDARY_SAFETY_POSTURE["automation_enabled"] is False


# 18 -- an active READY Bundle 46 gate activates the boundary contract.

def test_active_ready_gate_activates_boundary():
    c = _boundary(packet=_ready_boundary_packet())
    assert c["crypto_d1_execution_boundary_contract_active"] is True
    assert c["crypto_d1_execution_boundary_contract_state"] == (
        "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_"
        "CONTRACT_ACTIVE"
    )
    assert c["crypto_d1_pre_acquisition_human_gate_contract_active"] is True
    assert (
        c["crypto_d1_pre_acquisition_human_approval_verdict"]
        == "HUMAN_APPROVAL_READY"
    )
    assert (
        c["crypto_d1_pre_acquisition_human_approval_next_gate"]
        == "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED"  # noqa: E501
    )
    assert c["schema_version"] == BOUNDARY_SCHEMA_VERSION
    assert (
        c["crypto_d1_pre_acquisition_human_gate_schema_version"]
        == GATE_SCHEMA_VERSION
    )
    assert (
        c["execution_boundary_required"]
        == "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_REQUIRED"  # noqa: E501
    )


# 19 -- a ready boundary packet -> EXECUTION_BOUNDARY_READY + correct next gate.

def test_ready_boundary_packet_is_ready():
    c = _boundary(packet=_ready_boundary_packet())
    assert c["execution_boundary_verdict"] == "EXECUTION_BOUNDARY_READY"
    assert c["next_gate"] == (
        "CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED"
    )
    assert c["validation"]["valid"] is True


# 20 -- inactive gate (wrong verdict) -> AWAIT, never evaluates the packet.

def test_wrong_gate_verdict_does_not_activate():
    gate = _synthetic_gate(verdict="HUMAN_APPROVAL_MISSING")
    c = _boundary(gate, _ready_boundary_packet())
    assert c["crypto_d1_execution_boundary_contract_active"] is False
    assert c["execution_boundary_verdict"] == (
        "AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE"
    )
    assert c["next_gate"] == (
        "AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE"
    )


# 21 -- inactive gate (wrong next_gate) -> AWAIT.

def test_wrong_gate_next_gate_does_not_activate():
    gate = _synthetic_gate(next_gate="SOMETHING_ELSE")
    c = _boundary(gate, _ready_boundary_packet())
    assert c["crypto_d1_execution_boundary_contract_active"] is False
    assert c["execution_boundary_verdict"] == BOUNDARY_VERDICT_AWAIT


# 22 -- inactive gate (active flag False) -> AWAIT.

def test_inactive_gate_flag_does_not_activate():
    gate = _synthetic_gate(active=False)
    c = _boundary(gate, _ready_boundary_packet())
    assert c["crypto_d1_execution_boundary_contract_active"] is False
    assert c["execution_boundary_verdict"] == BOUNDARY_VERDICT_AWAIT


# 23 -- malformed gate inputs never raise -> AWAIT.

def test_malformed_gate_inputs_await():
    for bad in (None, {}, [], "x", 7, 3.14, True, ()):
        c = BUILD(bad, execution_boundary_packet=_ready_boundary_packet())
        assert c["crypto_d1_execution_boundary_contract_active"] is False
        assert c["execution_boundary_verdict"] == BOUNDARY_VERDICT_AWAIT


# 24 -- empty packet on an active gate -> NEEDS_MORE_INFO.

def test_empty_packet_needs_more_info():
    c = _boundary(packet=None)
    assert c["crypto_d1_execution_boundary_contract_active"] is True
    assert c["execution_boundary_verdict"] == BOUNDARY_VERDICT_NEEDS_MORE_INFO
    c2 = _boundary(packet={})
    assert c2["execution_boundary_verdict"] == BOUNDARY_VERDICT_NEEDS_MORE_INFO


# 25 -- each missing text field -> NEEDS_MORE_INFO.

def test_each_missing_text_field_needs_more_info():
    for field in EXECUTION_BOUNDARY_REQUIRED_TEXT_FIELDS:
        p = _ready_boundary_packet()
        del p[field]
        c = _boundary(packet=p)
        assert c["execution_boundary_verdict"] == BOUNDARY_VERDICT_NEEDS_MORE_INFO, field  # noqa: E501
        assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_FIX_REQUIRED  # noqa: E501


# 26 -- each absent required True-flag -> NEEDS_MORE_INFO.

def test_each_absent_required_flag_needs_more_info():
    required = (
        EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS
        + EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES
        + EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS
    )
    for flag in required:
        p = _ready_boundary_packet()
        del p[flag]
        c = _boundary(packet=p)
        assert c["execution_boundary_verdict"] == BOUNDARY_VERDICT_NEEDS_MORE_INFO, flag  # noqa: E501


# 27 -- each forbidden allow flag truthy -> REJECTED.

def test_each_forbidden_allow_flag_rejected():
    for flag in EXECUTION_BOUNDARY_FORBIDDEN_ALLOW_FLAGS:
        p = _ready_boundary_packet()
        p[flag] = True
        c = _boundary(packet=p)
        assert c["execution_boundary_verdict"] == BOUNDARY_VERDICT_REJECTED, flag
        assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_REJECTED


# 28 -- live fetch / API keys / account / order / broker allowed -> REJECTED.

def test_live_api_account_order_broker_allowed_rejected():
    for flag in ("allow_live_fetch", "allow_api_keys", "allow_account_access",
                 "allow_order_capability", "allow_broker_exchange"):
        p = _ready_boundary_packet()
        p[flag] = True
        assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED


# 29 -- qa / baseline / backtest / simulation allowed -> REJECTED.

def test_qa_baseline_backtest_simulation_allowed_rejected():
    for flag in ("allow_qa_run", "allow_baseline_run", "allow_backtest_run",
                 "allow_simulation_run"):
        p = _ready_boundary_packet()
        p[flag] = True
        assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED


# 30 -- runtime / registry / dashboard write allowed -> REJECTED.

def test_runtime_registry_dashboard_write_allowed_rejected():
    for flag in ("allow_runtime_write", "allow_registry_write",
                 "allow_dashboard_write"):
        p = _ready_boundary_packet()
        p[flag] = True
        assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED


# 31 -- automation trigger / paper-live allowed -> REJECTED.

def test_automation_and_paper_live_allowed_rejected():
    for flag in ("allow_automation_trigger", "allow_paper_live",
                 "side_effects_allowed", "execution_authorized"):
        p = _ready_boundary_packet()
        p[flag] = True
        assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED


# 32 -- each prohibition present-but-relaxed (False) -> REJECTED.

def test_each_relaxed_prohibition_rejected():
    for flag in EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS:
        p = _ready_boundary_packet()
        p[flag] = False
        c = _boundary(packet=p)
        assert c["execution_boundary_verdict"] == BOUNDARY_VERDICT_REJECTED, flag


# 33 -- each output rule present-but-disabled -> REJECTED.

def test_each_disabled_output_rule_rejected():
    for flag in EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES:
        p = _ready_boundary_packet()
        p[flag] = False
        assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED


# 34 -- each affirmation present-but-not-affirmed -> REJECTED.

def test_each_unaffirmed_affirmation_rejected():
    for flag in EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS:
        p = _ready_boundary_packet()
        p[flag] = False
        assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED


# 35 -- a disallowed execution_mode -> REJECTED.

def test_disallowed_execution_mode_rejected():
    for bad in ("live", "live_api", "online", "streaming", "paper", "real"):
        p = _ready_boundary_packet()
        p["execution_mode"] = bad
        assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED, bad


# 36 -- a disallowed acquisition_method -> REJECTED.

def test_disallowed_acquisition_method_rejected():
    for bad in ("live_api", "rest_api", "websocket", "exchange_pull"):
        p = _ready_boundary_packet()
        p["acquisition_method"] = bad
        assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED, bad


# 37 -- a disallowed destination_type -> REJECTED.

def test_disallowed_destination_type_rejected():
    for bad in ("live_broker", "exchange_account", "production_db"):
        p = _ready_boundary_packet()
        p["allowed_destination_type"] = bad
        assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED, bad


# 38 -- an automated author -> REJECTED.

def test_automated_author_rejected():
    for key in ("boundary_author_type", "author_type", "operator_name_or_id"):
        for marker in ("automated", "bot", "llm", "ai", "cron", "system"):
            p = _ready_boundary_packet()
            p[key] = marker
            assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED


# 39 -- a packet that lists granted capabilities -> REJECTED.

def test_granted_capabilities_rejected():
    for key in ("grants_capabilities", "authorizes", "granted_capabilities"):
        p = _ready_boundary_packet()
        p[key] = ["live_fetch"]
        assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED


# 40 -- a clear mismatch with the approved gate -> REJECTED.

def test_mismatch_with_approved_gate_rejected():
    for key, bad in (
        ("approved_human_gate_id", "WRONG-GATE"),
        ("approved_plan_id", "WRONG-PLAN"),
        ("approved_source_specification_id", "WRONG-SPEC"),
    ):
        p = _ready_boundary_packet()
        p[key] = bad
        assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED, key


# 41 -- absent mismatch fields are NOT a mismatch (handled as missing).

def test_absent_match_fields_not_a_mismatch():
    p = _ready_boundary_packet()
    del p["approved_plan_id"]
    # missing, not rejected, when otherwise safe
    assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_NEEDS_MORE_INFO


# 42 -- operator parking -> PARKED + parked next gate.

def test_operator_parking_parked():
    for key, val in (
        ("parked", True), ("operator_decision", "parked"),
        ("decision", "deferred"), ("execution_scope", "hold"),
    ):
        p = _ready_boundary_packet()
        p[key] = val
        c = _boundary(packet=p)
        assert c["execution_boundary_verdict"] == BOUNDARY_VERDICT_PARKED, key
        assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_PARKED


# 43 -- REJECTED is checked before parking (unsafe + park -> REJECTED).

def test_rejected_precedes_parking():
    p = _ready_boundary_packet()
    p["parked"] = True
    p["allow_live_fetch"] = True
    assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_REJECTED


# 44 -- parking is checked before completeness (park + missing -> PARKED).

def test_parking_precedes_completeness():
    p = _ready_boundary_packet()
    del p["boundary_packet_id"]
    p["operator_decision"] = "parked"
    assert EVAL(p, _ref_packet())["verdict"] == BOUNDARY_VERDICT_PARKED


# 45 -- no verdict ever flips an authorization flag or the posture.

def test_no_verdict_unlocks_authorization():
    packets = (
        None, {}, _ready_boundary_packet(),
        {**_ready_boundary_packet(), "allow_live_fetch": True},
        {**_ready_boundary_packet(), "parked": True},
    )
    gates = (
        _synthetic_gate(),
        _synthetic_gate(active=False),
        _synthetic_gate(verdict="HUMAN_APPROVAL_MISSING"),
    )
    for g in gates:
        for pk in packets:
            c = BUILD(g, execution_boundary_packet=pk)
            for flag in _AUTH_FLAGS:
                assert c[flag] is False
            assert c["read_only"] is True
            assert c["executes"] is False
            assert c["human_approval_required"] is True
            assert all(v is False for v in c["safety_posture"].values())


# 46 -- evaluate is pure + deterministic across repeated calls.

def test_evaluate_is_deterministic():
    p = _ready_boundary_packet()
    snapshot = copy.deepcopy(p)
    r1 = EVAL(p, _ref_packet())
    r2 = EVAL(p, _ref_packet())
    assert r1 == r2
    assert p == snapshot  # input not mutated


# 47 -- build is deterministic + returns fresh independent dicts.

def test_build_is_deterministic_and_fresh():
    g = _synthetic_gate()
    p = _ready_boundary_packet()
    a = BUILD(g, execution_boundary_packet=p)
    b = BUILD(g, execution_boundary_packet=p)
    assert a == b
    a["execution_boundary_verdict"] = "TAMPERED"
    a["safety_posture"]["automation_enabled"] = True
    c = BUILD(g, execution_boundary_packet=p)
    assert c["execution_boundary_verdict"] == BOUNDARY_VERDICT_READY
    assert c["safety_posture"]["automation_enabled"] is False


# 48 -- evaluate never raises on arbitrary malformed packets.

def test_evaluate_never_raises_on_malformed():
    for bad in (None, [], "x", 7, 3.14, True, (), {"x": object()}):
        out = EVAL(bad, _ref_packet())
        assert out["verdict"] in ALLOWED_EXECUTION_BOUNDARY_VERDICTS


# 49 -- validate accepts a freshly built contract; rejects a tampered one.

def test_validate_accepts_fresh_rejects_tampered():
    c = _boundary(packet=_ready_boundary_packet())
    assert VALIDATE(c)["valid"] is True
    bad = dict(c)
    bad["read_only"] = False
    assert VALIDATE(bad)["valid"] is False
    bad2 = dict(c)
    bad2["execution_authorized"] = True
    assert VALIDATE(bad2)["valid"] is False
    bad3 = dict(c)
    bad3["safety_posture"] = {"automation_enabled": True}
    assert VALIDATE(bad3)["valid"] is False


# 50 -- validate fails when a pinned collection is altered.

def test_validate_fails_on_altered_collection():
    c = _boundary(packet=_ready_boundary_packet())
    bad = dict(c)
    bad["required_execution_boundary_fields"] = ("only_one",)
    assert VALIDATE(bad)["valid"] is False
    bad2 = dict(c)
    bad2["allowed_execution_modes"] = ("live",)
    assert VALIDATE(bad2)["valid"] is False


# 51 -- render returns deterministic, non-empty markdown (no file write).

def test_render_markdown_deterministic_nonempty():
    c = _boundary(packet=_ready_boundary_packet())
    md1 = RENDER(c)
    md2 = RENDER(c)
    assert md1 == md2
    assert isinstance(md1, str) and len(md1) > 200
    assert md1.startswith("# Strategy Factory Crypto-D1 Human-Approved")
    assert "EXECUTION_BOUNDARY_READY" in md1
    assert "Executes: False" in md1
    assert "Read only: True" in md1


# 52 -- render on malformed/blocked contract still yields markdown.

def test_render_handles_blocked_and_garbage():
    blocked = BUILD(None, execution_boundary_packet=None)
    assert isinstance(RENDER(blocked), str) and len(RENDER(blocked)) > 50
    assert isinstance(RENDER({}), str)
    assert isinstance(RENDER({"x": 1}), str)


# 53 -- every contract echoes packet + reference without leaking authority.

def test_contract_echoes_packet_and_reference():
    p = _ready_boundary_packet()
    c = _boundary(packet=p)
    assert c["evaluated_execution_boundary_packet"] == p
    assert c["evaluated_execution_boundary_packet"] is not p
    assert c["referenced_human_approval_packet"] == _ref_packet()
    # echo is a copy: mutating it does not change the source packet
    c["evaluated_execution_boundary_packet"]["boundary_packet_id"] = "X"
    assert p["boundary_packet_id"] == "boundary-crypto-d1-001"


# 54 -- blocked-capability collections are non-empty and contain key blocks.

def test_blocked_capability_collections():
    c = _boundary(packet=_ready_boundary_packet())
    blocked = c["blocked_capabilities"]
    for cap in ("data_fetch", "backtest", "simulation", "broker", "exchange",
                "order", "live_execution", "network", "file_write",
                "crypto_d1_data_acquisition", "crypto_d1_offline_acquisition_execution"):  # noqa: E501
        assert cap in blocked, cap
    boundary_blocked = c["execution_boundary_blocked_capabilities"]
    assert len(boundary_blocked) >= 1
    assert "crypto_d1_offline_acquisition_execution" in boundary_blocked


# 55 -- REAL integration: a genuine Bundle 46 READY gate drives the boundary.

def test_real_bundle46_ready_gate_integration():
    gate = _real_ready_gate()
    # sanity: the real Bundle 46 gate is actually READY at the right next gate
    assert gate["human_approval_verdict"] == "HUMAN_APPROVAL_READY"
    assert gate["next_gate"] == (
        "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED"  # noqa: E501
    )
    ref = gate["evaluated_human_approval_packet"]
    packet = _ready_boundary_packet()
    packet["approved_human_gate_id"] = ref["approval_packet_id"]
    packet["approved_plan_id"] = ref["approved_plan_id"]
    packet["approved_source_specification_id"] = (
        ref["approved_source_specification_id"]
    )
    c = BUILD(gate, execution_boundary_packet=packet)
    assert c["crypto_d1_execution_boundary_contract_active"] is True
    assert c["execution_boundary_verdict"] == "EXECUTION_BOUNDARY_READY"
    assert c["validation"]["valid"] is True
    assert all(c[flag] is False for flag in _AUTH_FLAGS)
    assert c["executes"] is False


# --- real upstream chain (reused from the Bundle 46 test) -------------------

def _real_ready_gate() -> dict:
    """Build a genuine Bundle 46 READY gate from the full upstream chain."""
    from sparta_commander.strategy_factory_crypto_d1_offline_acquisition_plan_contract import (  # noqa: E501
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
    from sparta_commander.strategy_factory_fake_report_renderer_in_memory import (  # noqa: E501
        build_fake_report_renderer_state,
    )
    from sparta_commander.strategy_factory_fake_report_renderer_contract import (  # noqa: E501
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
    from sparta_commander.strategy_factory_fake_dry_walk_operator_review_gate import (  # noqa: E501
        OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT,
        build_fake_dry_walk_operator_review_gate,
    )
    from sparta_commander.strategy_factory_fake_artifact_dry_walk_contract import (  # noqa: E501
        build_fake_artifact_dry_walk_contract,
    )
    from sparta_commander.strategy_factory_fake_artifact_smoke_test_contract import (  # noqa: E501
        build_fake_artifact_smoke_test_contract,
    )
    from sparta_commander.strategy_factory_backbone_closure_report import (
        build_backbone_closure_report,
    )
    from sparta_commander.strategy_factory_end_to_end_fake_pipeline_contract import (  # noqa: E501
        build_end_to_end_fake_pipeline_contract,
    )
    from sparta_commander.strategy_factory_safety_kill_switch_contract import (
        build_safety_kill_switch_contract,
    )
    from sparta_commander.strategy_factory_decision_ledger_contract import (
        build_decision_ledger_contract,
    )
    from sparta_commander.strategy_factory_dashboard_registry_feed_contract import (  # noqa: E501
        build_dashboard_registry_feed_contract,
    )
    from sparta_commander.strategy_factory_dry_run_orchestrator_contract import (  # noqa: E501
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
    from sparta_commander.strategy_factory_research_protocol_draft_contract import (  # noqa: E501
        build_research_protocol_draft_contract,
    )
    from sparta_commander.strategy_factory_research_decision_memo_contract import (  # noqa: E501
        MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
    )
    from sparta_commander.strategy_factory_research_queue import (
        build_research_queue_item,
    )

    item = build_research_queue_item(
        "idea-001",
        "Opening Range Mean Reversion",
        "Price tends to revert toward the opening range midpoint intraday.",
        asset_lane="MNQ",
        timeframe="5m",
    )
    draft = build_research_protocol_draft_contract(
        item,
        memo_decision=MEMO_DECISION_READY_FOR_PROTOCOL_DRAFT,
        human_research_approved=True,
    )
    rgate = build_protocol_review_gate(
        draft, review_decision=REVIEW_STATE_READY_FOR_DATA_CONTRACT_PLANNING)
    planning = build_data_contract_planning(rgate)
    data_qa = build_data_qa_contract(planning)
    runner = build_research_runner_contract(data_qa)
    orchestrator = build_dry_run_orchestrator_contract(runner)
    feed = build_dashboard_registry_feed_contract(orchestrator)
    ledger = build_decision_ledger_contract(feed)
    safety_gate = build_safety_kill_switch_contract(ledger)
    pipeline = build_end_to_end_fake_pipeline_contract(safety_gate)
    closure_report = build_backbone_closure_report(pipeline)

    smoke = build_fake_artifact_smoke_test_contract(closure_report)
    dry_walk = build_fake_artifact_dry_walk_contract(smoke)
    dw_gate = build_fake_dry_walk_operator_review_gate(
        dry_walk,
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_DRY_WALK_IMPLEMENTATION_CONTRACT
        ),
    )
    dw_contract = build_fake_dry_walk_implementation_contract(dw_gate)
    walk_state = build_fake_dry_walk_state(dw_contract)

    review = build_fake_dry_walk_result_review_contract(
        walk_state,
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_WALK_REPORT_CONTRACT
        ),
    )
    report = build_fake_walk_report_contract(review)
    rep_gate = build_fake_walk_report_operator_review_gate(
        report,
        operator_decision=(
            OPERATOR_DECISION_READY_FOR_FAKE_REPORT_RENDERER_CONTRACT
        ),
    )
    rcontract = build_fake_report_renderer_contract(rep_gate)
    renderer_state = build_fake_report_renderer_state(rcontract)

    review2 = build_fake_report_renderer_result_review_contract(
        renderer_state,
        result_review_decision=(
            RESULT_REVIEW_DECISION_READY_FOR_FAKE_LANE_CLOSURE_CONTRACT
        ),
    )
    closure = build_fake_lane_closure_contract(
        review2,
        closure_decision=CLOSURE_DECISION_FAKE_LANE_COMPLETE_PAUSE_FOR_OPERATOR,
    )
    recon = build_crypto_d1_intake_reconciliation_contract(
        closure,
        reconciliation_decision=(
            RECONCILIATION_DECISION_READY_FOR_CRYPTO_D1_ACQUIRE_DECISION_CONTRACT
        ),
    )
    approved_acq = build_crypto_d1_acquire_decision_contract(
        recon,
        acquire_decision=ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT,
    )
    sc = build_crypto_d1_source_class_contract(
        approved_acq,
        source_class_proposal={
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
        },
    )
    sp = build_crypto_d1_source_specification_contract(
        sc,
        source_specification={
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
        },
    )
    plan = build_crypto_d1_offline_acquisition_plan_contract(
        sp,
        offline_acquisition_plan={
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
            "freeze_manifest_plan": "freeze a manifest listing all fixture files",  # noqa: E501
            "checksum_plan": "record a sha256 checksum per fixture file",
            "provenance_plan": "record vendor name, download date, and file hash",  # noqa: E501
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
        },
    )
    human_packet = {
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
    return build_crypto_d1_pre_acquisition_human_gate_contract(
        plan, human_approval_packet=human_packet)

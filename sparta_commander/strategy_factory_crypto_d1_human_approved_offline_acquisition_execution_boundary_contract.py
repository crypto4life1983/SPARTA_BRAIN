"""SPARTA Offline Strategy Factory - CRYPTO-D1 HUMAN-APPROVED OFFLINE
ACQUISITION EXECUTION BOUNDARY CONTRACT.

Bundle 47 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only paper execution-boundary contract template* builder and
evaluator: it consumes a Bundle 46 crypto-d1 PRE-ACQUISITION HUMAN APPROVAL
GATE contract and, only when that gate contract is active with
human_approval_verdict == HUMAN_APPROVAL_READY and next_gate ==
CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED (the
concrete Bundle 46 signal that an execution-boundary contract is required
next), evaluates a proposed execution-boundary packet on paper and returns a
deterministic verdict describing whether a strict, offline-only, side-effect-
free, research-only execution boundary has been fully specified.

This module exists so that a future human-approved offline acquisition step,
if it is ever drafted, can only ever run inside an explicit, pre-declared
boundary that prohibits every live/dangerous capability. Reaching an active
boundary contract maps the upstream approved-gate state to the conceptual
boundary CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_
REQUIRED. Any other upstream shape (blocked, malformed, wrong stage, not ready,
parked, rejected, needs-more-info, or wrong gate) yields the
AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE verdict.

Reaching an active boundary contract and an EXECUTION_BOUNDARY_READY verdict
unlocks NOTHING real. It acquires no data, connects to no exchange, broker, or
live venue, uses no API keys, approves no QA, no baseline, no real backtest, no
simulation, no paper/live activity, and unlocks no real strategy intake. A
ready boundary only records, on paper, the exact, pre-declared limits a future
human-approved offline acquisition step would have to obey; it still requires a
separate, later, human-run step that this module does not authorize.

It never runs Strategy Factory, never acquires data, never inspects, loads,
validates, transforms, or computes on real data, never inspects market data,
never runs QA, never produces a QA verdict, never runs a baseline, never
backtests, never simulates, never reaches for data, never connects to any
exchange, broker, or vendor, never opens or reads any crypto-d1 dataset file,
qa_report, manifest, checksum, freeze record, fees file, or baseline output,
and executes nothing. It opens no network, spawns no subprocess, writes no
file, reads no file, lists no directory, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no decision into any runtime ledger. It
records no timestamp, mints no random id, reads no environment, and
dynamically imports nothing.

Public API:
  - BOUNDARY_SCHEMA_VERSION
  - DEFAULT_BOUNDARY_LABEL
  - BOUNDARY_STATUS
  - BOUNDARY_SAFETY_POSTURE
  - BOUNDARY_STATE_ACTIVE
  - BOUNDARY_STATE_BLOCKED
  - BOUNDARY_VERDICT_READY
  - BOUNDARY_VERDICT_NEEDS_MORE_INFO
  - BOUNDARY_VERDICT_REJECTED
  - BOUNDARY_VERDICT_PARKED
  - BOUNDARY_VERDICT_AWAIT
  - ALLOWED_EXECUTION_BOUNDARY_VERDICTS
  - UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_VERDICT
  - UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_GATE
  - BOUNDARY_CRYPTO_D1_EXECUTION_BOUNDARY_REQUIRED
  - NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED
  - NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_PARKED
  - NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE
  - REQUIRED_EXECUTION_BOUNDARY_FIELDS
  - EXECUTION_BOUNDARY_REQUIRED_TEXT_FIELDS
  - EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS
  - EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES
  - EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS
  - EXECUTION_BOUNDARY_FORBIDDEN_ALLOW_FLAGS
  - ALLOWED_EXECUTION_MODES
  - ALLOWED_ACQUISITION_METHODS
  - ALLOWED_DESTINATION_TYPES
  - AUTOMATED_APPROVAL_MARKERS
  - ALLOWED_ASSET_UNIVERSE
  - REQUIRED_CANDLE_FIELDS
  - ALLOWED_TIMEFRAME
  - BLOCKED_EXECUTION_ITEMS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - evaluate_crypto_d1_human_approved_offline_acquisition_execution_boundary(packet, approved_gate_packet=None)
  - build_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract(pre_acquisition_human_gate_contract, execution_boundary_packet=None)
  - validate_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract(contract)
  - render_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_pre_acquisition_human_gate_contract import (  # noqa: E501
    GATE_SCHEMA_VERSION,
    GATE_SAFETY_POSTURE,
    GATE_VERDICT_READY as _PRE_ACQUISITION_HUMAN_APPROVAL_VERDICT_READY,
    NEXT_GATE_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED as _PRE_ACQUISITION_HUMAN_APPROVAL_READY_GATE,  # noqa: E501
    AUTOMATED_APPROVAL_MARKERS,
    ALLOWED_ASSET_UNIVERSE,
    REQUIRED_CANDLE_FIELDS,
    ALLOWED_TIMEFRAME,
    BLOCKED_EXECUTION_ITEMS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
)

__all__ = [
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
    "evaluate_crypto_d1_human_approved_offline_acquisition_execution_boundary",
    "build_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract",  # noqa: E501
    "validate_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract",  # noqa: E501
    "render_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract_markdown",  # noqa: E501
]

BOUNDARY_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_human_approved_offline_acquisition_execution_"
    "boundary_contract.v1"
)
DEFAULT_BOUNDARY_LABEL = (
    "Strategy Factory Crypto-D1 Human-Approved Offline Acquisition Execution "
    "Boundary Contract"
)
BOUNDARY_STATUS = (
    "READ_ONLY_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_"
    "CONTRACT"
)

BOUNDARY_STATE_ACTIVE = (
    "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_CONTRACT_"
    "ACTIVE"
)
BOUNDARY_STATE_BLOCKED = (
    "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_CONTRACT_"
    "BLOCKED"
)

BOUNDARY_VERDICT_READY = "EXECUTION_BOUNDARY_READY"
BOUNDARY_VERDICT_NEEDS_MORE_INFO = "EXECUTION_BOUNDARY_NEEDS_MORE_INFO"
BOUNDARY_VERDICT_REJECTED = "EXECUTION_BOUNDARY_REJECTED"
BOUNDARY_VERDICT_PARKED = "EXECUTION_BOUNDARY_PARKED"
BOUNDARY_VERDICT_AWAIT = "AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE"

ALLOWED_EXECUTION_BOUNDARY_VERDICTS: tuple[str, ...] = (
    BOUNDARY_VERDICT_READY,
    BOUNDARY_VERDICT_NEEDS_MORE_INFO,
    BOUNDARY_VERDICT_REJECTED,
    BOUNDARY_VERDICT_PARKED,
    BOUNDARY_VERDICT_AWAIT,
)

# The exact upstream Bundle 46 signal this bundle activates from.
UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_VERDICT = (
    _PRE_ACQUISITION_HUMAN_APPROVAL_VERDICT_READY
)
UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_GATE = (
    _PRE_ACQUISITION_HUMAN_APPROVAL_READY_GATE
)

# The conceptual boundary this bundle fulfills once it is active.
BOUNDARY_CRYPTO_D1_EXECUTION_BOUNDARY_REQUIRED = (
    "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_REQUIRED"
)

# A READY boundary still demands a separate, later, human-run execution step.
NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED = (
    "CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_FIX_REQUIRED = (
    "CRYPTO_D1_EXECUTION_BOUNDARY_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_PARKED = (
    "CRYPTO_D1_EXECUTION_BOUNDARY_PARKED"
)
NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_REJECTED = (
    "CRYPTO_D1_EXECUTION_BOUNDARY_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE = (
    "AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-46).
BOUNDARY_SAFETY_POSTURE: dict[str, bool] = dict(GATE_SAFETY_POSTURE)

# Descriptive text fields a human operator records on a boundary packet.
EXECUTION_BOUNDARY_REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
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
    "next_step_boundary",
)

# Prohibition flags that must each be affirmed True. A present-but-not-affirmed
# value is a request to RELAX a prohibition -- a hard REJECTED. An absent value
# is a missing requirement (NEEDS_MORE_INFO).
EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS: tuple[str, ...] = (
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
)

# Output-rule flags the boundary must require (each affirmed True).
EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES: tuple[str, ...] = (
    "provenance_output_required",
    "checksum_output_required",
    "freeze_manifest_output_required",
)

# Operator affirmation flags the boundary must carry (each affirmed True).
EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS: tuple[str, ...] = (
    "operator_reconfirmation_required",
    "dry_run_description_required",
    "no_side_effects_acknowledgement",
)

# Every required True-flag the boundary must affirm (prohibitions + output rules
# + affirmations). A present-but-not-affirmed value forces REJECTED; an absent
# value forces NEEDS_MORE_INFO.
_REQUIRED_TRUE_FLAGS: tuple[str, ...] = (
    EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS
    + EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES
    + EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS
)

# The full set of required boundary-packet fields (instruction order, 31).
REQUIRED_EXECUTION_BOUNDARY_FIELDS: tuple[str, ...] = (
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

# Positive allow/grant flags a boundary must NOT request -- any truthy value
# forces a hard REJECTED. These represent a boundary that tries to permit a
# real, dangerous capability.
EXECUTION_BOUNDARY_FORBIDDEN_ALLOW_FLAGS: tuple[str, ...] = (
    "allow_live_fetch",
    "live_fetch_allowed",
    "allow_api_keys",
    "api_keys_allowed",
    "uses_api_keys",
    "allow_account_access",
    "account_access_allowed",
    "allow_order_capability",
    "order_capability_allowed",
    "allow_broker_exchange",
    "broker_exchange_allowed",
    "allow_qa_run",
    "qa_run_allowed",
    "allow_baseline_run",
    "baseline_run_allowed",
    "allow_backtest_run",
    "backtest_run_allowed",
    "allow_simulation_run",
    "simulation_run_allowed",
    "allow_paper_live",
    "paper_live_allowed",
    "allow_automation_trigger",
    "automation_trigger_allowed",
    "allow_runtime_write",
    "runtime_write_allowed",
    "allow_registry_write",
    "registry_write_allowed",
    "allow_dashboard_write",
    "dashboard_write_allowed",
    "side_effects_allowed",
    "allow_side_effects",
    "execution_authorized",
    "live_execution_authorized",
    "autopilot_enabled",
)

# Allowed strict enumerations. A present-but-not-allowed value is a hard
# REJECTED (the boundary tries to permit something outside offline-only scope).
ALLOWED_EXECUTION_MODES: tuple[str, ...] = (
    "offline_only",
    "offline",
    "offline_fixture",
    "dry_run",
)
ALLOWED_ACQUISITION_METHODS: tuple[str, ...] = (
    "offline_fixture",
    "offline_file",
    "local_fixture",
    "preexisting_local_dataset",
)
ALLOWED_DESTINATION_TYPES: tuple[str, ...] = (
    "frozen_offline_artifact",
    "local_frozen_dataset",
    "offline_research_artifact",
)

# Auth flags (7, all False on every contract).
_AUTH_FLAGS: tuple[str, ...] = (
    "approved_for_research",
    "execution_authorized",
    "paper_trading_authorized",
    "live_trading_authorized",
    "data_fetch_authorized",
    "backtest_authorized",
    "promotion_authorized",
)

# Boundary-specific blocked capabilities (this phase only).
_BOUNDARY_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "crypto_d1_offline_acquisition_execution",
    "crypto_d1_data_acquisition",
    "crypto_d1_live_api_access",
    "crypto_d1_exchange_connection",
    "crypto_d1_broker_connection",
    "crypto_d1_dataset_read",
    "crypto_d1_data_inspection",
    "crypto_d1_qa_run",
    "crypto_d1_baseline_run",
    "crypto_d1_backtest",
    "crypto_d1_simulation",
    "real_strategy_intake",
    "report_file_write",
    "runtime_state_write",
    "registry_file_write",
    "dashboard_runtime_update",
    "boundary_ledger_write",
    "automation_trigger",
)

# Capabilities that stay blocked for every contract, regardless of state.
_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "data_fetch",
    "backtest",
    "simulation",
    "broker",
    "exchange",
    "order",
    "live_execution",
    "paper_execution",
    "upload",
    "autopilot",
    "promotion",
    "subprocess",
    "network",
    "file_write",
    "file_read",
    "directory_listing",
    "dashboard_runtime_update",
    "registry_file_write",
    "template_edit",
    "ledger_runtime_write",
    "runtime_approval_write",
    "runtime_safety_flag_write",
    "pipeline_execution",
    "report_file_write",
    "runtime_state_write",
    "real_strategy_intake",
    "crypto_d1_data_acquisition",
    "crypto_d1_offline_acquisition_plan_execution",
    "crypto_d1_pre_acquisition_human_gate_execution",
    "crypto_d1_offline_acquisition_execution",
    "crypto_d1_live_api_access",
    "crypto_d1_exchange_connection",
    "crypto_d1_broker_connection",
    "crypto_d1_dataset_read",
    "crypto_d1_data_inspection",
    "crypto_d1_market_data_inspection",
    "crypto_d1_qa_run",
    "crypto_d1_qa_verdict",
    "crypto_d1_baseline_run",
    "crypto_d1_backtest",
    "crypto_d1_simulation",
    "automation_trigger",
    "boundary_ledger_write",
)

_BOUNDARY_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 execution-boundary packet is a paper placeholder for the "
    "explicit, pre-declared, offline-only, side-effect-free limits a future "
    "human-approved offline acquisition step would have to obey."
)

_BOUNDARY_VERDICT_RATIONALE_PLACEHOLDER = (
    "Execution-boundary verdict rationale is a paper placeholder for a "
    "human-recorded acceptance, deferral, or refusal and its supporting "
    "reason."
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 human-approved offline acquisition execution boundary "
    "contract template and is execution-free.",
    "It evaluates a paper execution-boundary packet only and writes no report "
    "file.",
    "It writes no runtime state, acquires no data, and inspects no data.",
    "It authorizes no real data acquisition and no live venue access.",
    "A ready boundary only records, on paper, the limits a future step must "
    "obey.",
    "It connects to no exchange, broker, or live venue and uses no API keys.",
    "The deferred items stay blocked: qa, qa acceptance, and baseline output.",
    "No crypto-d1 dataset, qa_report, manifest, checksum, freeze record, or "
    "fees file is opened, inspected, or accessed.",
    "A human operator alone may record this boundary; no automated author is "
    "accepted.",
    "A READY boundary still requires a separate, later, human-run execution "
    "step that this template does not authorize.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must record an execution-boundary verdict with a "
    "supporting rationale on paper.",
    "A human operator must confirm the boundary prohibits every live, API, "
    "exchange, broker, account, order, qa, baseline, backtest, simulation, "
    "paper/live, automation, runtime, registry, and dashboard capability.",
    "A human operator must confirm the boundary matches the approved human "
    "approval gate exactly.",
    "A human operator must decide whether a later, separate, human-run "
    "acquisition-execution step may be drafted.",
    "No automated step may proceed without human sign-off.",
)

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "crypto_d1_pre_acquisition_human_gate_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "crypto_d1_execution_boundary_contract_active",
    "crypto_d1_execution_boundary_contract_state",
    "crypto_d1_pre_acquisition_human_gate_contract_active",
    "crypto_d1_pre_acquisition_human_approval_verdict",
    "crypto_d1_pre_acquisition_human_approval_next_gate",
    "execution_boundary_required",
    "asset_lane",
    "timeframe_lane",
    "execution_boundary_packet_reference_placeholder",
    "execution_boundary_verdict",
    "execution_boundary_verdict_reasons",
    "evaluated_execution_boundary_packet",
    "referenced_human_approval_packet",
    "allowed_execution_boundary_verdicts",
    "required_execution_boundary_fields",
    "execution_boundary_required_text_fields",
    "execution_boundary_required_prohibitions",
    "execution_boundary_required_output_rules",
    "execution_boundary_required_affirmations",
    "execution_boundary_forbidden_allow_flags",
    "allowed_execution_modes",
    "allowed_acquisition_methods",
    "allowed_destination_types",
    "automated_approval_markers",
    "allowed_asset_universe",
    "required_candle_fields",
    "allowed_timeframe",
    "execution_boundary_verdict_rationale_placeholder",
    "blocked_execution_items",
    "execution_boundary_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
    "crypto_d1_pre_acquisition_human_gate_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(BOUNDARY_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(state: Any, key: str) -> str:
    """Read a string field from a possibly-malformed state; safe."""
    return _as_text(state.get(key)) if isinstance(state, dict) else ""


def _truthy(value: Any) -> bool:
    """Deterministic truthiness for packet flags."""
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "required", "y", "1")
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    return False


def _affirm(value: Any) -> bool:
    """Deterministic affirmation test for required True-flags."""
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in (
            "true", "yes", "required", "y", "1", "confirmed", "acknowledged",
            "prohibited",
        )
    return False


def _present(value: Any) -> bool:
    """Deterministic presence test for descriptive packet fields."""
    if value is True:
        return True
    if value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict)):
        return len(value) > 0
    if isinstance(value, (int, float)):
        return True
    return False


def _scalar(value: Any) -> str:
    """Normalize a scalar text value for comparison."""
    return _as_text(value).strip().lower()


def _mismatch_reasons(
    packet: dict[str, Any], ref_packet: dict[str, Any]
) -> tuple[str, ...]:
    """Return mismatch reasons where a present boundary field clearly disagrees
    with the approved human-approval packet. Absent boundary fields are not a
    mismatch (they are handled as missing); only present-but-conflicting values
    are a hard mismatch."""
    if not isinstance(ref_packet, dict) or not ref_packet:
        return ()

    reasons: list[str] = []

    scalar_pairs = (
        ("approved_human_gate_id", "approval_packet_id"),
        ("approved_plan_id", "approved_plan_id"),
        ("approved_source_specification_id", "approved_source_specification_id"),
    )
    for pkey, rkey in scalar_pairs:
        pv = packet.get(pkey)
        rv = ref_packet.get(rkey)
        if _present(pv) and _present(rv) and _scalar(pv) != _scalar(rv):
            reasons.append(f"mismatch:{pkey}")

    return tuple(reasons)


def _reject_reasons(
    packet: dict[str, Any], ref_packet: dict[str, Any]
) -> tuple[str, ...]:
    """Return any hard REJECTED reasons for a boundary packet: a permitted
    dangerous capability, a relaxed prohibition, a disallowed enum value, an
    automated author, granted authority, or a clear mismatch with the approved
    gate."""
    reasons: list[str] = []

    for flag in EXECUTION_BOUNDARY_FORBIDDEN_ALLOW_FLAGS:
        if _truthy(packet.get(flag)):
            reasons.append(f"forbidden_allow:{flag}")

    # A required True-flag that is present but NOT affirmed is a request to
    # relax a safety guarantee -- a hard REJECTED.
    for flag in _REQUIRED_TRUE_FLAGS:
        if flag in packet and not _affirm(packet.get(flag)):
            reasons.append(f"prohibition_relaxed:{flag}")

    enum_pairs = (
        ("execution_mode", ALLOWED_EXECUTION_MODES),
        ("acquisition_method", ALLOWED_ACQUISITION_METHODS),
        ("allowed_destination_type", ALLOWED_DESTINATION_TYPES),
    )
    for key, allowed in enum_pairs:
        value = packet.get(key)
        if _present(value) and _scalar(value) not in allowed:
            reasons.append(f"disallowed_value:{key}")

    for key in (
        "boundary_author_type",
        "author_type",
        "boundary_method",
        "boundary_source",
        "authored_by_type",
        "operator_name_or_id",
    ):
        if _scalar(packet.get(key)) in AUTOMATED_APPROVAL_MARKERS:
            reasons.append(f"automated_author:{key}")

    for key in ("grants_capabilities", "authorizes", "granted_capabilities"):
        listed = packet.get(key)
        if isinstance(listed, (list, tuple)) and len(listed) > 0:
            reasons.append(f"grants_listed:{key}")

    reasons.extend(_mismatch_reasons(packet, ref_packet))

    return tuple(reasons)


def _park_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return parking reasons when an operator explicitly parks or defers."""
    reasons: list[str] = []
    park_values = {
        "park", "parked", "defer", "deferred", "hold", "on_hold",
        "postpone", "postponed",
    }

    for flag in ("park", "parked", "defer", "deferred", "hold"):
        if _truthy(packet.get(flag)):
            reasons.append("operator_parked_execution_boundary")
            break

    if _scalar(packet.get("operator_decision")) in park_values:
        reasons.append("operator_decision_parked")
    if _scalar(packet.get("decision")) in park_values:
        reasons.append("decision_parked")
    if _scalar(packet.get("execution_scope")) in park_values:
        reasons.append("execution_scope_parked")

    return tuple(reasons)


def _missing_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return unmet boundary requirements for an otherwise-safe packet."""
    missing: list[str] = []

    for key in EXECUTION_BOUNDARY_REQUIRED_TEXT_FIELDS:
        if not _present(packet.get(key)):
            missing.append(f"{key}_required")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag not in packet:
            missing.append(f"{flag}_must_be_affirmed_true")

    return tuple(missing)


def evaluate_crypto_d1_human_approved_offline_acquisition_execution_boundary(
    packet: Any,
    approved_gate_packet: Any = None,
) -> dict[str, Any]:
    """Return a deterministic verdict for an execution-boundary packet against
    the approved human-approval packet. Pure; no I/O, no mutation, no timestamp,
    no random id. Unknown/malformed inputs never raise. The verdict is one of
    EXECUTION_BOUNDARY_READY, EXECUTION_BOUNDARY_NEEDS_MORE_INFO,
    EXECUTION_BOUNDARY_REJECTED, or EXECUTION_BOUNDARY_PARKED. It evaluates the
    SHAPE of a paper boundary only and unlocks nothing. REJECTED (permits a
    dangerous capability / relaxes a prohibition / disallowed value / authority-
    granting / mismatched) is checked before parking, and parking before
    completeness, so an unsafe boundary is rejected even when it would otherwise
    park or merely need more info."""
    p = packet if isinstance(packet, dict) else {}
    ref = approved_gate_packet if isinstance(approved_gate_packet, dict) else {}

    if not p:
        return {
            "verdict": BOUNDARY_VERDICT_NEEDS_MORE_INFO,
            "reasons": ("execution_boundary_packet_missing",),
        }

    rejected = _reject_reasons(p, ref)
    if rejected:
        return {
            "verdict": BOUNDARY_VERDICT_REJECTED,
            "reasons": rejected,
        }

    park = _park_reasons(p)
    if park:
        return {
            "verdict": BOUNDARY_VERDICT_PARKED,
            "reasons": park,
        }

    missing = _missing_reasons(p)
    if not missing:
        return {
            "verdict": BOUNDARY_VERDICT_READY,
            "reasons": (
                "offline_only_side_effect_free_research_only_execution_"
                "boundary_fully_specified_and_matches_gate",
            ),
        }

    return {
        "verdict": BOUNDARY_VERDICT_NEEDS_MORE_INFO,
        "reasons": missing,
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == BOUNDARY_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in (
        "BOUNDARY_ONLY",
        "CRYPTO_D1_EXECUTION_BOUNDARY_ONLY",
    )
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    auth_all_false = all(safe.get(flag) is False for flag in _AUTH_FLAGS)
    posture = safe.get("safety_posture")
    safety_all_false = (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )

    verdicts_ok = (
        tuple(safe.get("allowed_execution_boundary_verdicts") or ())
        == ALLOWED_EXECUTION_BOUNDARY_VERDICTS
    )
    fields_ok = (
        tuple(safe.get("required_execution_boundary_fields") or ())
        == REQUIRED_EXECUTION_BOUNDARY_FIELDS
    )
    text_fields_ok = (
        tuple(safe.get("execution_boundary_required_text_fields") or ())
        == EXECUTION_BOUNDARY_REQUIRED_TEXT_FIELDS
    )
    prohibitions_ok = (
        tuple(safe.get("execution_boundary_required_prohibitions") or ())
        == EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS
    )
    output_rules_ok = (
        tuple(safe.get("execution_boundary_required_output_rules") or ())
        == EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES
    )
    affirmations_ok = (
        tuple(safe.get("execution_boundary_required_affirmations") or ())
        == EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS
    )
    forbidden_flags_ok = (
        tuple(safe.get("execution_boundary_forbidden_allow_flags") or ())
        == EXECUTION_BOUNDARY_FORBIDDEN_ALLOW_FLAGS
    )
    exec_modes_ok = (
        tuple(safe.get("allowed_execution_modes") or ())
        == ALLOWED_EXECUTION_MODES
    )
    methods_ok = (
        tuple(safe.get("allowed_acquisition_methods") or ())
        == ALLOWED_ACQUISITION_METHODS
    )
    destinations_ok = (
        tuple(safe.get("allowed_destination_types") or ())
        == ALLOWED_DESTINATION_TYPES
    )
    markers_ok = (
        tuple(safe.get("automated_approval_markers") or ())
        == AUTOMATED_APPROVAL_MARKERS
    )
    assets_ok = (
        tuple(safe.get("allowed_asset_universe") or ())
        == ALLOWED_ASSET_UNIVERSE
    )
    candle_ok = (
        tuple(safe.get("required_candle_fields") or ())
        == REQUIRED_CANDLE_FIELDS
    )
    timeframe_ok = (
        tuple(safe.get("allowed_timeframe") or ()) == ALLOWED_TIMEFRAME
    )
    blocked_execution_ok = (
        tuple(safe.get("blocked_execution_items") or ())
        == BLOCKED_EXECUTION_ITEMS
    )
    remaining_blocked_ok = (
        tuple(safe.get("remaining_real_world_capabilities_blocked") or ())
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )
    verdict_value_ok = (
        safe.get("execution_boundary_verdict")
        in ALLOWED_EXECUTION_BOUNDARY_VERDICTS
    )
    boundary_blocked_ok = (
        len(tuple(
            safe.get("execution_boundary_blocked_capabilities") or ()
        ))
        >= 1
    )
    notes_ok = len(tuple(safe.get("operator_notes") or ())) >= 1
    next_steps_ok = (
        len(tuple(safe.get("human_operator_required_next_steps") or ())) >= 1
    )

    collections_ok = (
        verdicts_ok
        and fields_ok
        and text_fields_ok
        and prohibitions_ok
        and output_rules_ok
        and affirmations_ok
        and forbidden_flags_ok
        and exec_modes_ok
        and methods_ok
        and destinations_ok
        and markers_ok
        and assets_ok
        and candle_ok
        and timeframe_ok
        and blocked_execution_ok
        and remaining_blocked_ok
        and verdict_value_ok
        and boundary_blocked_ok
        and notes_ok
        and next_steps_ok
    )

    valid = bool(
        schema_ok
        and research_only
        and stage_ok
        and read_only
        and executes_false
        and human_required
        and auth_all_false
        and safety_all_false
        and collections_ok
        and not missing
    )

    return {
        "valid": valid,
        "schema_version_ok": schema_ok,
        "read_only": read_only,
        "research_only": research_only,
        "stage_ok": stage_ok,
        "human_approval_required": human_required,
        "executes": False,
        "all_authorization_flags_false": auth_all_false,
        "safety_all_false": safety_all_false,
        "allowed_execution_boundary_verdicts_ok": verdicts_ok,
        "required_execution_boundary_fields_ok": fields_ok,
        "execution_boundary_required_text_fields_ok": text_fields_ok,
        "execution_boundary_required_prohibitions_ok": prohibitions_ok,
        "execution_boundary_required_output_rules_ok": output_rules_ok,
        "execution_boundary_required_affirmations_ok": affirmations_ok,
        "execution_boundary_forbidden_allow_flags_ok": forbidden_flags_ok,
        "allowed_execution_modes_ok": exec_modes_ok,
        "allowed_acquisition_methods_ok": methods_ok,
        "allowed_destination_types_ok": destinations_ok,
        "automated_approval_markers_ok": markers_ok,
        "allowed_asset_universe_ok": assets_ok,
        "required_candle_fields_ok": candle_ok,
        "allowed_timeframe_ok": timeframe_ok,
        "blocked_execution_items_ok": blocked_execution_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "execution_boundary_verdict_value_ok": verdict_value_ok,
        "execution_boundary_blocked_capabilities_present": boundary_blocked_ok,
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract(  # noqa: E501
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 human-approved offline
    acquisition execution boundary contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract(  # noqa: E501
    pre_acquisition_human_gate_contract: Any,
    execution_boundary_packet: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 human-approved offline
    acquisition execution boundary contract template plus a paper verdict for a
    proposed execution-boundary packet.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (crypto_d1_execution_boundary_contract_active=True) solely when the upstream
    Bundle 46 crypto-d1 pre-acquisition human approval gate contract is active
    AND its human_approval_verdict is HUMAN_APPROVAL_READY AND its next_gate is
    the Bundle 46 ready gate
    (CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED --
    the concrete signal an execution-boundary contract is required next). When
    inactive, the verdict is AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE
    regardless of the packet. Even when active and READY, every authorization
    field stays False -- it evaluates the SHAPE of a paper boundary only,
    acquires nothing, connects to nothing, approves no QA, no baseline, and no
    backtest, writes no report file, writes no runtime state, names only
    placeholders, and grants nothing. Returned dicts are fresh."""
    gate = (
        pre_acquisition_human_gate_contract
        if isinstance(pre_acquisition_human_gate_contract, dict)
        else {}
    )

    gate_active = (
        gate.get("crypto_d1_pre_acquisition_human_gate_contract_active") is True
    )
    gate_verdict = _field(gate, "human_approval_verdict")
    gate_next = _field(gate, "next_gate")
    verdict_ok = (
        gate_verdict
        == UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_VERDICT
    )
    gate_ok = (
        gate_next == UPSTREAM_REQUIRED_PRE_ACQUISITION_HUMAN_APPROVAL_GATE
    )

    contract_active = bool(gate_active and verdict_ok and gate_ok)

    ref_packet_raw = gate.get("evaluated_human_approval_packet")
    ref_packet = ref_packet_raw if isinstance(ref_packet_raw, dict) else {}

    if contract_active:
        evaluation = (
            evaluate_crypto_d1_human_approved_offline_acquisition_execution_boundary(  # noqa: E501
                execution_boundary_packet, ref_packet
            )
        )
        verdict = evaluation["verdict"]
        reasons = tuple(evaluation["reasons"])
    else:
        verdict = BOUNDARY_VERDICT_AWAIT
        reasons = ("await_crypto_d1_pre_acquisition_human_approval_gate",)

    state = BOUNDARY_STATE_ACTIVE if contract_active else BOUNDARY_STATE_BLOCKED

    if not contract_active:
        next_gate = NEXT_GATE_AWAIT_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE
    elif verdict == BOUNDARY_VERDICT_READY:
        next_gate = (
            NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED  # noqa: E501
        )
    elif verdict == BOUNDARY_VERDICT_NEEDS_MORE_INFO:
        next_gate = NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_FIX_REQUIRED
    elif verdict == BOUNDARY_VERDICT_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_PARKED
    else:
        next_gate = NEXT_GATE_CRYPTO_D1_EXECUTION_BOUNDARY_REJECTED

    execution_boundary_required = (
        BOUNDARY_CRYPTO_D1_EXECUTION_BOUNDARY_REQUIRED
        if contract_active
        else ""
    )

    echoed_packet = (
        dict(execution_boundary_packet)
        if isinstance(execution_boundary_packet, dict)
        else {}
    )
    referenced_packet = dict(ref_packet) if ref_packet else {}

    contract = {
        "schema_version": BOUNDARY_SCHEMA_VERSION,
        "crypto_d1_pre_acquisition_human_gate_schema_version": (
            GATE_SCHEMA_VERSION
        ),
        "idea_id": _field(pre_acquisition_human_gate_contract, "idea_id"),
        "title": _field(pre_acquisition_human_gate_contract, "title"),
        "label": DEFAULT_BOUNDARY_LABEL,
        "status": BOUNDARY_STATUS,
        "stage": "CRYPTO_D1_EXECUTION_BOUNDARY_ONLY",
        "mode": "RESEARCH_ONLY",
        "crypto_d1_execution_boundary_contract_active": contract_active,
        "crypto_d1_execution_boundary_contract_state": state,
        "crypto_d1_pre_acquisition_human_gate_contract_active": bool(
            gate_active
        ),
        "crypto_d1_pre_acquisition_human_approval_verdict": gate_verdict,
        "crypto_d1_pre_acquisition_human_approval_next_gate": gate_next,
        "execution_boundary_required": execution_boundary_required,
        "asset_lane": _field(
            pre_acquisition_human_gate_contract, "asset_lane"
        ),
        "timeframe_lane": _field(
            pre_acquisition_human_gate_contract, "timeframe_lane"
        ),
        "execution_boundary_packet_reference_placeholder": (
            _BOUNDARY_REFERENCE_PLACEHOLDER
        ),
        "execution_boundary_verdict": verdict,
        "execution_boundary_verdict_reasons": reasons,
        "evaluated_execution_boundary_packet": echoed_packet,
        "referenced_human_approval_packet": referenced_packet,
        "allowed_execution_boundary_verdicts": (
            ALLOWED_EXECUTION_BOUNDARY_VERDICTS
        ),
        "required_execution_boundary_fields": (
            REQUIRED_EXECUTION_BOUNDARY_FIELDS
        ),
        "execution_boundary_required_text_fields": (
            EXECUTION_BOUNDARY_REQUIRED_TEXT_FIELDS
        ),
        "execution_boundary_required_prohibitions": (
            EXECUTION_BOUNDARY_REQUIRED_PROHIBITIONS
        ),
        "execution_boundary_required_output_rules": (
            EXECUTION_BOUNDARY_REQUIRED_OUTPUT_RULES
        ),
        "execution_boundary_required_affirmations": (
            EXECUTION_BOUNDARY_REQUIRED_AFFIRMATIONS
        ),
        "execution_boundary_forbidden_allow_flags": (
            EXECUTION_BOUNDARY_FORBIDDEN_ALLOW_FLAGS
        ),
        "allowed_execution_modes": ALLOWED_EXECUTION_MODES,
        "allowed_acquisition_methods": ALLOWED_ACQUISITION_METHODS,
        "allowed_destination_types": ALLOWED_DESTINATION_TYPES,
        "automated_approval_markers": AUTOMATED_APPROVAL_MARKERS,
        "allowed_asset_universe": ALLOWED_ASSET_UNIVERSE,
        "required_candle_fields": REQUIRED_CANDLE_FIELDS,
        "allowed_timeframe": ALLOWED_TIMEFRAME,
        "execution_boundary_verdict_rationale_placeholder": (
            _BOUNDARY_VERDICT_RATIONALE_PLACEHOLDER
        ),
        "blocked_execution_items": BLOCKED_EXECUTION_ITEMS,
        "execution_boundary_blocked_capabilities": (
            _BOUNDARY_BLOCKED_CAPABILITIES
        ),
        "remaining_real_world_capabilities_blocked": (
            REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
        ),
        "blocked_capabilities": _BLOCKED_CAPABILITIES,
        "safety_posture": _safety_posture(),
        "next_gate": next_gate,
        "operator_notes": _OPERATOR_NOTES,
        "human_operator_required_next_steps": (
            _HUMAN_OPERATOR_REQUIRED_NEXT_STEPS
        ),
        "approved_for_research": False,
        "execution_authorized": False,
        "paper_trading_authorized": False,
        "live_trading_authorized": False,
        "data_fetch_authorized": False,
        "backtest_authorized": False,
        "promotion_authorized": False,
        "human_approval_required": True,
        "read_only": True,
        "executes": False,
        "crypto_d1_pre_acquisition_human_gate_contract": (
            pre_acquisition_human_gate_contract
            if isinstance(pre_acquisition_human_gate_contract, dict)
            else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract_markdown(  # noqa: E501
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 human-approved
    offline acquisition execution boundary contract template. Pure; writes no
    file. Informational only."""
    verdicts = contract.get("allowed_execution_boundary_verdicts") or ()
    fields = contract.get("required_execution_boundary_fields") or ()
    text_fields = contract.get("execution_boundary_required_text_fields") or ()
    prohibitions = (
        contract.get("execution_boundary_required_prohibitions") or ()
    )
    output_rules = (
        contract.get("execution_boundary_required_output_rules") or ()
    )
    affirmations = (
        contract.get("execution_boundary_required_affirmations") or ()
    )
    forbidden_flags = (
        contract.get("execution_boundary_forbidden_allow_flags") or ()
    )
    exec_modes = contract.get("allowed_execution_modes") or ()
    methods = contract.get("allowed_acquisition_methods") or ()
    destinations = contract.get("allowed_destination_types") or ()
    markers = contract.get("automated_approval_markers") or ()
    assets = contract.get("allowed_asset_universe") or ()
    candle_fields = contract.get("required_candle_fields") or ()
    timeframe = contract.get("allowed_timeframe") or ()
    reasons = contract.get("execution_boundary_verdict_reasons") or ()
    blocked_execution = contract.get("blocked_execution_items") or ()
    boundary_blocked = (
        contract.get("execution_boundary_blocked_capabilities") or ()
    )
    remaining_blocked = (
        contract.get("remaining_real_world_capabilities_blocked") or ()
    )
    next_steps = contract.get("human_operator_required_next_steps") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Crypto-D1 Human-Approved Offline Acquisition "
        "Execution Boundary Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a "
        "crypto-d1-execution-boundary-only, paper-only, offline-only, "
        "no-live-api, no-data-acquisition, no-qa-run, no-baseline-run, "
        "no-backtest, no-simulation, no-data-inspection, "
        "no-real-strategy-intake-yet, research-only, and execution-free "
        "template -- it records only a paper execution-boundary verdict, is "
        "not wired into any runtime state, writes no report file, acquires no "
        "data, inspects no data, connects to no venue, names only "
        "placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Pre-acquisition human approval gate schema: "
        f"`{contract.get('crypto_d1_pre_acquisition_human_gate_schema_version', '')}`"  # noqa: E501
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: CRYPTO_D1_EXECUTION_BOUNDARY_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 execution boundary contract active: "
        f"{contract.get('crypto_d1_execution_boundary_contract_active', '')}"
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_execution_boundary_contract_state', '')}"
    )
    lines.append(
        "Execution boundary required: "
        f"{contract.get('execution_boundary_required', '')}"
    )
    lines.append(
        f"Verdict: {contract.get('execution_boundary_verdict', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Execution Boundary Packet Reference")
    lines.append("")
    lines.append(
        "Execution boundary packet reference: "
        f"{contract.get('execution_boundary_packet_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Execution Boundary Verdict Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Execution Boundary Verdicts")
    lines.append("")
    for x in verdicts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Execution Boundary Fields")
    lines.append("")
    for x in fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Execution Boundary Required Text Fields")
    lines.append("")
    for x in text_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Execution Boundary Required Prohibitions")
    lines.append("")
    for x in prohibitions:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Execution Boundary Required Output Rules")
    lines.append("")
    for x in output_rules:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Execution Boundary Required Affirmations")
    lines.append("")
    for x in affirmations:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Execution Boundary Forbidden Allow Flags")
    lines.append("")
    for x in forbidden_flags:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Execution Modes")
    lines.append("")
    for x in exec_modes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Acquisition Methods")
    lines.append("")
    for x in methods:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Destination Types")
    lines.append("")
    for x in destinations:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Automated Approval Markers")
    lines.append("")
    for x in markers:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Asset Universe")
    lines.append("")
    for x in assets:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Candle Fields")
    lines.append("")
    for x in candle_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Timeframe")
    lines.append("")
    for x in timeframe:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Execution Boundary Verdict Rationale")
    lines.append("")
    lines.append(
        "Execution boundary verdict rationale: "
        f"{contract.get('execution_boundary_verdict_rationale_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Blocked Execution Items")
    lines.append("")
    for x in blocked_execution:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Execution Boundary Blocked Capabilities")
    lines.append("")
    for cap in boundary_blocked:
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Remaining Real-World Capabilities Blocked")
    lines.append("")
    for cap in remaining_blocked:
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Blocked Capabilities")
    lines.append("")
    for cap in contract.get("blocked_capabilities") or ():
        lines.append(f"- `{cap}`")
    lines.append("")
    lines.append("## Human Operator Required Next Steps")
    lines.append("")
    for step in next_steps:
        lines.append(f"- {step}")
    lines.append("")
    lines.append("## Operator Notes")
    lines.append("")
    for note in notes:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    for key, value in posture.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    for key, value in validation.items():
        lines.append(f"- `{key}`: `{value}`")
    lines.append("")
    lines.append("## Next Gate")
    lines.append("")
    lines.append(
        "- A human operator must confirm this execution boundary before any "
        "separate, later, human-run acquisition-execution step is drafted."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)

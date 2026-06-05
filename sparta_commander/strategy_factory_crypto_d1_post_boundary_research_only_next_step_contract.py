"""SPARTA Offline Strategy Factory - CRYPTO-D1 POST-BOUNDARY RESEARCH-ONLY
NEXT-STEP CONTRACT.

Bundle 48 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only paper decision contract* builder and evaluator. It
consumes a Bundle 47 crypto-d1 HUMAN-APPROVED OFFLINE ACQUISITION EXECUTION
BOUNDARY contract and, only when that boundary contract is active with
execution_boundary_verdict == EXECUTION_BOUNDARY_READY and next_gate ==
CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED (the
concrete Bundle 47 signal that a post-boundary next step must be decided),
evaluates a proposed post-boundary next-step decision packet on paper and
returns a deterministic verdict describing which research-only future contract
should be built next -- or whether the lane should be parked or rejected.

It exists so the system knows what comes after Bundle 47 WITHOUT accidentally
starting real data work. It only *decides* the next safe, research-only step.
It NEVER acquires data, fetches data, inspects data, loads a dataset, runs QA,
a baseline, a backtest, or a simulation, never executes any offline
acquisition, never reaches a broker/exchange/order/account/API surface, never
trades paper or live, triggers no automation, and writes no runtime, registry,
ledger, dashboard, or report state.

Reaching a PROCEED verdict unlocks NOTHING real. It only records, on paper,
that the next contract a human operator may draft is a research-only,
dry-run-preview-only template -- and even that still requires a separate, later,
human-run step this module does not authorize. Any other upstream shape
(blocked, malformed, wrong stage, not ready, parked, rejected, needs-more-info,
or wrong gate) yields the
AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_CONTRACT
verdict.

It opens no network, spawns no subprocess, writes no file, reads no file, lists
no directory, records no timestamp, mints no random id, reads no environment,
and dynamically imports nothing.

Public API:
  - NEXT_STEP_SCHEMA_VERSION
  - DEFAULT_NEXT_STEP_LABEL
  - NEXT_STEP_STATUS
  - NEXT_STEP_SAFETY_POSTURE
  - NEXT_STEP_STATE_ACTIVE / NEXT_STEP_STATE_BLOCKED
  - NEXT_STEP_VERDICT_PROCEED
  - NEXT_STEP_VERDICT_NEEDS_MORE_INFO
  - NEXT_STEP_VERDICT_REJECTED
  - NEXT_STEP_VERDICT_PARKED
  - NEXT_STEP_VERDICT_AWAIT
  - ALLOWED_NEXT_STEP_VERDICTS
  - UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_VERDICT
  - UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_NEXT_GATE
  - POST_BOUNDARY_NEXT_REQUIRED_ACTION
  - POST_BOUNDARY_CURRENT_STAGE
  - NEXT_STEP_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REQUIRED
  - NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED
  - NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_PARKED
  - NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_CONTRACT
  - REQUIRED_NEXT_STEP_FIELDS
  - NEXT_STEP_REQUIRED_TEXT_FIELDS
  - NEXT_STEP_REQUIRED_PROHIBITIONS
  - NEXT_STEP_REQUIRED_AFFIRMATIONS
  - NEXT_STEP_FORBIDDEN_ALLOW_FLAGS
  - ALLOWED_NEXT_CONTRACT_MODES
  - ALLOWED_NEXT_CONTRACT_TYPES
  - ALLOWED_NEXT_CONTRACT_SCOPES
  - ALLOWED_PROPOSED_NEXT_CONTRACTS
  - AUTOMATED_APPROVAL_MARKERS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - evaluate_crypto_d1_post_boundary_research_only_next_step(packet, boundary_ref_packet=None)
  - build_crypto_d1_post_boundary_research_only_next_step_contract(execution_boundary_contract, next_step_decision_packet=None)
  - validate_crypto_d1_post_boundary_research_only_next_step_contract(contract)
  - render_crypto_d1_post_boundary_research_only_next_step_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_human_approved_offline_acquisition_execution_boundary_contract import (  # noqa: E501
    BOUNDARY_SCHEMA_VERSION,
    BOUNDARY_SAFETY_POSTURE,
    BOUNDARY_VERDICT_READY as _EXECUTION_BOUNDARY_VERDICT_READY,
    NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED as _EXECUTION_BOUNDARY_READY_NEXT_GATE,  # noqa: E501
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
)
from sparta_commander.strategy_factory_mission_flow_bundle_registry import (  # noqa: E501
    CURRENT_STAGE as _REGISTRY_CURRENT_STAGE,
    NEXT_REQUIRED_ACTION as _REGISTRY_NEXT_REQUIRED_ACTION,
)

__all__ = [
    "NEXT_STEP_SCHEMA_VERSION",
    "DEFAULT_NEXT_STEP_LABEL",
    "NEXT_STEP_STATUS",
    "NEXT_STEP_SAFETY_POSTURE",
    "NEXT_STEP_STATE_ACTIVE",
    "NEXT_STEP_STATE_BLOCKED",
    "NEXT_STEP_VERDICT_PROCEED",
    "NEXT_STEP_VERDICT_NEEDS_MORE_INFO",
    "NEXT_STEP_VERDICT_REJECTED",
    "NEXT_STEP_VERDICT_PARKED",
    "NEXT_STEP_VERDICT_AWAIT",
    "ALLOWED_NEXT_STEP_VERDICTS",
    "UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_VERDICT",
    "UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_NEXT_GATE",
    "POST_BOUNDARY_NEXT_REQUIRED_ACTION",
    "POST_BOUNDARY_CURRENT_STAGE",
    "NEXT_STEP_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_FIX_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_PARKED",
    "NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REJECTED",
    "NEXT_GATE_AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_CONTRACT",  # noqa: E501
    "REQUIRED_NEXT_STEP_FIELDS",
    "NEXT_STEP_REQUIRED_TEXT_FIELDS",
    "NEXT_STEP_REQUIRED_PROHIBITIONS",
    "NEXT_STEP_REQUIRED_AFFIRMATIONS",
    "NEXT_STEP_FORBIDDEN_ALLOW_FLAGS",
    "ALLOWED_NEXT_CONTRACT_MODES",
    "ALLOWED_NEXT_CONTRACT_TYPES",
    "ALLOWED_NEXT_CONTRACT_SCOPES",
    "ALLOWED_PROPOSED_NEXT_CONTRACTS",
    "AUTOMATED_APPROVAL_MARKERS",
    "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "evaluate_crypto_d1_post_boundary_research_only_next_step",
    "build_crypto_d1_post_boundary_research_only_next_step_contract",
    "validate_crypto_d1_post_boundary_research_only_next_step_contract",
    "render_crypto_d1_post_boundary_research_only_next_step_contract_markdown",
]

NEXT_STEP_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_post_boundary_research_only_next_step_"
    "contract.v1"
)
DEFAULT_NEXT_STEP_LABEL = (
    "Strategy Factory Crypto-D1 Post-Boundary Research-Only Next-Step Contract"
)
NEXT_STEP_STATUS = (
    "READ_ONLY_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT"
)

NEXT_STEP_STATE_ACTIVE = (
    "CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT_ACTIVE"
)
NEXT_STEP_STATE_BLOCKED = (
    "CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT_BLOCKED"
)

NEXT_STEP_VERDICT_PROCEED = "PROCEED_TO_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT"
NEXT_STEP_VERDICT_NEEDS_MORE_INFO = "NEEDS_MORE_INFO"
NEXT_STEP_VERDICT_REJECTED = "POST_BOUNDARY_REJECTED"
NEXT_STEP_VERDICT_PARKED = "POST_BOUNDARY_PARKED"
NEXT_STEP_VERDICT_AWAIT = (
    "AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_"
    "CONTRACT"
)

ALLOWED_NEXT_STEP_VERDICTS: tuple[str, ...] = (
    NEXT_STEP_VERDICT_PROCEED,
    NEXT_STEP_VERDICT_NEEDS_MORE_INFO,
    NEXT_STEP_VERDICT_REJECTED,
    NEXT_STEP_VERDICT_PARKED,
    NEXT_STEP_VERDICT_AWAIT,
)

# The exact upstream Bundle 47 signal this bundle activates from.
UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_VERDICT = _EXECUTION_BOUNDARY_VERDICT_READY
UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_NEXT_GATE = (
    _EXECUTION_BOUNDARY_READY_NEXT_GATE
)

# Post-boundary next action / stage as published by the mission-flow registry.
POST_BOUNDARY_NEXT_REQUIRED_ACTION = _REGISTRY_NEXT_REQUIRED_ACTION
POST_BOUNDARY_CURRENT_STAGE = _REGISTRY_CURRENT_STAGE

# The conceptual decision this bundle fulfills once it is active.
NEXT_STEP_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REQUIRED = (
    "CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_REQUIRED"
)

# Next-gate outcomes by verdict.
NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_FIX_REQUIRED = (
    "CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_PARKED = (
    "CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_PARKED"
)
NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REJECTED = (
    "CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_CONTRACT = (  # noqa: E501
    "AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_"
    "CONTRACT"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-47).
NEXT_STEP_SAFETY_POSTURE: dict[str, bool] = dict(BOUNDARY_SAFETY_POSTURE)

# Descriptive text fields a human operator records on a decision packet.
NEXT_STEP_REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
    "decision_packet_id",
    "upstream_boundary_id",
    "approved_boundary_stage",
    "proposed_next_contract",
    "proposed_next_contract_scope",
    "proposed_next_contract_mode",
    "proposed_next_contract_type",
    "allowed_research_only_outputs",
    "next_step_reason",
)

# Prohibition flags that must each be affirmed True. A present-but-not-affirmed
# value is a request to RELAX a prohibition -- a hard REJECTED. An absent value
# is a missing requirement (NEEDS_MORE_INFO).
NEXT_STEP_REQUIRED_PROHIBITIONS: tuple[str, ...] = (
    "prohibited_real_data_acquisition",
    "prohibited_data_fetch",
    "prohibited_data_inspection",
    "prohibited_qa_run",
    "prohibited_baseline_run",
    "prohibited_backtest_run",
    "prohibited_simulation_run",
    "prohibited_paper_live",
    "prohibited_broker_exchange",
    "prohibited_order_capability",
    "prohibited_account_access",
    "prohibited_api_keys",
    "prohibited_automation_trigger",
    "prohibited_runtime_write",
    "prohibited_registry_write",
    "prohibited_dashboard_write",
)

# Operator affirmation flags the decision must carry (each affirmed True).
NEXT_STEP_REQUIRED_AFFIRMATIONS: tuple[str, ...] = (
    "human_operator_review_required",
    "research_only_acknowledgement",
    "no_execution_acknowledgement",
)

# Every required True-flag (prohibitions + affirmations). Present-but-not-
# affirmed -> REJECTED; absent -> NEEDS_MORE_INFO.
_REQUIRED_TRUE_FLAGS: tuple[str, ...] = (
    NEXT_STEP_REQUIRED_PROHIBITIONS + NEXT_STEP_REQUIRED_AFFIRMATIONS
)

# The full set of required decision-packet fields (28).
REQUIRED_NEXT_STEP_FIELDS: tuple[str, ...] = (
    NEXT_STEP_REQUIRED_TEXT_FIELDS
    + NEXT_STEP_REQUIRED_PROHIBITIONS
    + NEXT_STEP_REQUIRED_AFFIRMATIONS
)

# Positive allow/grant flags a decision must NOT request -- any truthy value
# forces a hard REJECTED (it tries to permit a real, dangerous capability).
NEXT_STEP_FORBIDDEN_ALLOW_FLAGS: tuple[str, ...] = (
    "allow_real_data_acquisition",
    "real_data_acquisition_allowed",
    "allow_data_fetch",
    "data_fetch_allowed",
    "allow_data_inspection",
    "data_inspection_allowed",
    "allow_dataset_load",
    "dataset_load_allowed",
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
    "allow_broker_exchange",
    "broker_exchange_allowed",
    "allow_order_capability",
    "order_capability_allowed",
    "allow_account_access",
    "account_access_allowed",
    "allow_api_keys",
    "api_keys_allowed",
    "uses_api_keys",
    "allow_automation_trigger",
    "automation_trigger_allowed",
    "allow_runtime_write",
    "runtime_write_allowed",
    "allow_registry_write",
    "registry_write_allowed",
    "allow_dashboard_write",
    "dashboard_write_allowed",
    "execution_authorized",
    "live_execution_authorized",
    "autopilot_enabled",
    "side_effects_allowed",
    "allow_side_effects",
    "proceed_to_real_acquisition",
    "proceed_to_data_fetch",
    "proceed_to_execution",
)

# Allowed strict enumerations. A present-but-not-allowed value is a hard
# REJECTED (the decision tries to permit something outside research-only scope).
ALLOWED_NEXT_CONTRACT_MODES: tuple[str, ...] = (
    "research_only",
    "research-only",
)
ALLOWED_NEXT_CONTRACT_TYPES: tuple[str, ...] = (
    "dry_run_preview",
    "dry_run_preview_contract",
    "research_only_preview",
    "preview_only",
)
ALLOWED_NEXT_CONTRACT_SCOPES: tuple[str, ...] = (
    "dry_run_preview_only",
    "research_only_preview",
    "preview_only",
    "no_data_preview",
    "offline_preview",
)
ALLOWED_PROPOSED_NEXT_CONTRACTS: tuple[str, ...] = (
    "crypto_d1_research_only_dry_run_preview_contract",
    "crypto_d1_dry_run_preview_contract",
    "crypto_d1_post_boundary_research_only_dry_run_preview_contract",
    "research_only_dry_run_preview_contract",
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

# Next-step-phase blocked capabilities.
_NEXT_STEP_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "crypto_d1_real_data_acquisition",
    "crypto_d1_data_fetch",
    "crypto_d1_data_inspection",
    "crypto_d1_dataset_load",
    "crypto_d1_qa_run",
    "crypto_d1_baseline_run",
    "crypto_d1_backtest",
    "crypto_d1_simulation",
    "crypto_d1_offline_acquisition_execution",
    "crypto_d1_live_api_access",
    "crypto_d1_exchange_connection",
    "crypto_d1_broker_connection",
    "crypto_d1_order_capability",
    "crypto_d1_account_access",
    "real_strategy_intake",
    "report_file_write",
    "runtime_state_write",
    "registry_file_write",
    "dashboard_runtime_update",
    "decision_ledger_write",
    "automation_trigger",
)

# Capabilities that stay blocked for every contract, regardless of state.
_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "real_data_acquisition",
    "data_fetch",
    "data_inspection",
    "dataset_load",
    "qa_run",
    "baseline",
    "backtest",
    "simulation",
    "broker",
    "exchange",
    "order",
    "account_access",
    "api_keys",
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
    "runtime_state_write",
    "report_file_write",
    "decision_ledger_write",
    "automation_trigger",
    "real_strategy_intake",
    "crypto_d1_offline_acquisition_execution",
)

_NEXT_STEP_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 post-boundary decision packet is a paper placeholder for a "
    "human operator's choice of which research-only, dry-run-preview-only "
    "contract to draft next after the execution boundary -- it acquires "
    "nothing and executes nothing."
)

_NEXT_STEP_VERDICT_RATIONALE_PLACEHOLDER = (
    "Post-boundary next-step verdict rationale is a paper placeholder for a "
    "human-recorded acceptance, deferral, or refusal and its supporting "
    "reason."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 post-boundary research-only next-step decision "
    "contract template and is execution-free.",
    "It evaluates a paper decision packet only and writes no report file.",
    "It writes no runtime state, acquires no data, and inspects no data.",
    "It only decides which research-only contract should be built next.",
    "A PROCEED verdict points only to a research-only, dry-run-preview-only "
    "next contract; it authorizes no data work.",
    "It connects to no exchange, broker, or live venue and uses no API keys.",
    "QA, baseline, backtest, simulation, paper, and live all stay blocked.",
    "No crypto-d1 dataset, qa_report, manifest, checksum, or fees file is "
    "opened, inspected, or accessed.",
    "A human operator alone may record this decision; no automated author is "
    "accepted.",
    "Any PROCEED still requires a separate, later, human-run step that this "
    "template does not authorize.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must record a post-boundary next-step verdict with a "
    "supporting rationale on paper.",
    "A human operator must confirm the proposed next contract is research-only "
    "and dry-run-preview-only, with no data acquisition, fetch, inspection, "
    "QA, baseline, backtest, simulation, paper/live, broker/exchange, order, "
    "account, API, automation, or runtime/registry/dashboard writes.",
    "A human operator must confirm the decision matches the approved Bundle 47 "
    "execution boundary exactly.",
    "A human operator must decide whether the chosen research-only contract "
    "may actually be drafted next.",
    "No automated step may proceed without human sign-off.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "crypto_d1_execution_boundary_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "crypto_d1_post_boundary_next_step_contract_active",
    "crypto_d1_post_boundary_next_step_contract_state",
    "crypto_d1_execution_boundary_contract_active",
    "crypto_d1_execution_boundary_verdict",
    "crypto_d1_execution_boundary_next_gate",
    "post_boundary_next_step_required",
    "post_boundary_next_required_action",
    "post_boundary_current_stage",
    "asset_lane",
    "timeframe_lane",
    "next_step_packet_reference_placeholder",
    "next_step_verdict",
    "next_step_verdict_reasons",
    "evaluated_next_step_packet",
    "referenced_execution_boundary_packet",
    "allowed_next_step_verdicts",
    "required_next_step_fields",
    "next_step_required_text_fields",
    "next_step_required_prohibitions",
    "next_step_required_affirmations",
    "next_step_forbidden_allow_flags",
    "allowed_next_contract_modes",
    "allowed_next_contract_types",
    "allowed_next_contract_scopes",
    "allowed_proposed_next_contracts",
    "automated_approval_markers",
    "next_step_verdict_rationale_placeholder",
    "next_step_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
    "crypto_d1_execution_boundary_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(NEXT_STEP_SAFETY_POSTURE)


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
    """Return mismatch reasons where a present decision field clearly disagrees
    with the approved Bundle 47 boundary packet. Absent fields are not a
    mismatch; only present-but-conflicting values are a hard mismatch."""
    if not isinstance(ref_packet, dict) or not ref_packet:
        return ()

    reasons: list[str] = []
    pv = packet.get("upstream_boundary_id")
    rv = ref_packet.get("boundary_packet_id")
    if _present(pv) and _present(rv) and _scalar(pv) != _scalar(rv):
        reasons.append("mismatch:upstream_boundary_id")
    return tuple(reasons)


def _reject_reasons(
    packet: dict[str, Any], ref_packet: dict[str, Any]
) -> tuple[str, ...]:
    """Return any hard REJECTED reasons: a permitted dangerous capability, a
    relaxed prohibition, a disallowed enum value, an automated author, granted
    authority, or a clear mismatch with the approved boundary."""
    reasons: list[str] = []

    for flag in NEXT_STEP_FORBIDDEN_ALLOW_FLAGS:
        if _truthy(packet.get(flag)):
            reasons.append(f"forbidden_allow:{flag}")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag in packet and not _affirm(packet.get(flag)):
            reasons.append(f"prohibition_relaxed:{flag}")

    enum_pairs = (
        ("proposed_next_contract_mode", ALLOWED_NEXT_CONTRACT_MODES),
        ("proposed_next_contract_type", ALLOWED_NEXT_CONTRACT_TYPES),
        ("proposed_next_contract_scope", ALLOWED_NEXT_CONTRACT_SCOPES),
        ("proposed_next_contract", ALLOWED_PROPOSED_NEXT_CONTRACTS),
    )
    for key, allowed in enum_pairs:
        value = packet.get(key)
        if _present(value) and _scalar(value) not in allowed:
            reasons.append(f"disallowed_value:{key}")

    for key in (
        "decision_author_type",
        "author_type",
        "decision_method",
        "decision_source",
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
            reasons.append("operator_parked_post_boundary_next_step")
            break

    if _scalar(packet.get("operator_decision")) in park_values:
        reasons.append("operator_decision_parked")
    if _scalar(packet.get("decision")) in park_values:
        reasons.append("decision_parked")

    return tuple(reasons)


def _missing_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return unmet decision requirements for an otherwise-safe packet."""
    missing: list[str] = []

    for key in NEXT_STEP_REQUIRED_TEXT_FIELDS:
        if not _present(packet.get(key)):
            missing.append(f"{key}_required")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag not in packet:
            missing.append(f"{flag}_must_be_affirmed_true")

    return tuple(missing)


def evaluate_crypto_d1_post_boundary_research_only_next_step(
    packet: Any,
    boundary_ref_packet: Any = None,
) -> dict[str, Any]:
    """Return a deterministic verdict for a post-boundary next-step decision
    packet against the approved Bundle 47 boundary packet. Pure; no I/O, no
    mutation, no timestamp, no random id. Unknown/malformed inputs never raise.
    The verdict is one of PROCEED_TO_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT,
    NEEDS_MORE_INFO, POST_BOUNDARY_REJECTED, or POST_BOUNDARY_PARKED. It
    evaluates the SHAPE of a paper decision only and unlocks nothing. REJECTED
    (permits a dangerous capability / relaxes a prohibition / disallowed value /
    authority-granting / mismatched) is checked before parking, and parking
    before completeness, so an unsafe decision is rejected even when it would
    otherwise park or merely need more info."""
    p = packet if isinstance(packet, dict) else {}
    ref = boundary_ref_packet if isinstance(boundary_ref_packet, dict) else {}

    if not p:
        return {
            "verdict": NEXT_STEP_VERDICT_NEEDS_MORE_INFO,
            "reasons": ("post_boundary_next_step_packet_missing",),
        }

    rejected = _reject_reasons(p, ref)
    if rejected:
        return {
            "verdict": NEXT_STEP_VERDICT_REJECTED,
            "reasons": rejected,
        }

    park = _park_reasons(p)
    if park:
        return {
            "verdict": NEXT_STEP_VERDICT_PARKED,
            "reasons": park,
        }

    missing = _missing_reasons(p)
    if not missing:
        return {
            "verdict": NEXT_STEP_VERDICT_PROCEED,
            "reasons": (
                "research_only_dry_run_preview_next_contract_fully_specified_"
                "and_matches_boundary",
            ),
        }

    return {
        "verdict": NEXT_STEP_VERDICT_NEEDS_MORE_INFO,
        "reasons": missing,
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == NEXT_STEP_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") == "CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_ONLY"
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
        tuple(safe.get("allowed_next_step_verdicts") or ())
        == ALLOWED_NEXT_STEP_VERDICTS
    )
    fields_ok = (
        tuple(safe.get("required_next_step_fields") or ())
        == REQUIRED_NEXT_STEP_FIELDS
    )
    text_fields_ok = (
        tuple(safe.get("next_step_required_text_fields") or ())
        == NEXT_STEP_REQUIRED_TEXT_FIELDS
    )
    prohibitions_ok = (
        tuple(safe.get("next_step_required_prohibitions") or ())
        == NEXT_STEP_REQUIRED_PROHIBITIONS
    )
    affirmations_ok = (
        tuple(safe.get("next_step_required_affirmations") or ())
        == NEXT_STEP_REQUIRED_AFFIRMATIONS
    )
    forbidden_flags_ok = (
        tuple(safe.get("next_step_forbidden_allow_flags") or ())
        == NEXT_STEP_FORBIDDEN_ALLOW_FLAGS
    )
    modes_ok = (
        tuple(safe.get("allowed_next_contract_modes") or ())
        == ALLOWED_NEXT_CONTRACT_MODES
    )
    types_ok = (
        tuple(safe.get("allowed_next_contract_types") or ())
        == ALLOWED_NEXT_CONTRACT_TYPES
    )
    scopes_ok = (
        tuple(safe.get("allowed_next_contract_scopes") or ())
        == ALLOWED_NEXT_CONTRACT_SCOPES
    )
    proposed_ok = (
        tuple(safe.get("allowed_proposed_next_contracts") or ())
        == ALLOWED_PROPOSED_NEXT_CONTRACTS
    )
    markers_ok = (
        tuple(safe.get("automated_approval_markers") or ())
        == AUTOMATED_APPROVAL_MARKERS
    )
    remaining_blocked_ok = (
        tuple(safe.get("remaining_real_world_capabilities_blocked") or ())
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )
    verdict_value_ok = (
        safe.get("next_step_verdict") in ALLOWED_NEXT_STEP_VERDICTS
    )
    blocked_present_ok = (
        len(tuple(safe.get("next_step_blocked_capabilities") or ())) >= 1
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
        and affirmations_ok
        and forbidden_flags_ok
        and modes_ok
        and types_ok
        and scopes_ok
        and proposed_ok
        and markers_ok
        and remaining_blocked_ok
        and verdict_value_ok
        and blocked_present_ok
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
        "allowed_next_step_verdicts_ok": verdicts_ok,
        "required_next_step_fields_ok": fields_ok,
        "next_step_required_text_fields_ok": text_fields_ok,
        "next_step_required_prohibitions_ok": prohibitions_ok,
        "next_step_required_affirmations_ok": affirmations_ok,
        "next_step_forbidden_allow_flags_ok": forbidden_flags_ok,
        "allowed_next_contract_modes_ok": modes_ok,
        "allowed_next_contract_types_ok": types_ok,
        "allowed_next_contract_scopes_ok": scopes_ok,
        "allowed_proposed_next_contracts_ok": proposed_ok,
        "automated_approval_markers_ok": markers_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "next_step_verdict_value_ok": verdict_value_ok,
        "next_step_blocked_capabilities_present": blocked_present_ok,
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_post_boundary_research_only_next_step_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 post-boundary research-only
    next-step contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_post_boundary_research_only_next_step_contract(
    execution_boundary_contract: Any,
    next_step_decision_packet: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 post-boundary
    research-only next-step contract template plus a paper verdict for a
    proposed next-step decision packet.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (crypto_d1_post_boundary_next_step_contract_active=True) solely when the
    upstream Bundle 47 crypto-d1 human-approved offline acquisition execution
    boundary contract is active AND its execution_boundary_verdict is
    EXECUTION_BOUNDARY_READY AND its next_gate is the Bundle 47 ready gate
    (CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED). When
    inactive, the verdict is
    AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_CONTRACT
    regardless of the packet. Even when active and PROCEED, every authorization
    field stays False -- it evaluates the SHAPE of a paper decision only,
    acquires nothing, connects to nothing, approves no QA, no baseline, and no
    backtest, writes no report file, writes no runtime state, names only
    placeholders, and grants nothing. Returned dicts are fresh."""
    boundary = (
        execution_boundary_contract
        if isinstance(execution_boundary_contract, dict)
        else {}
    )

    boundary_active = (
        boundary.get("crypto_d1_execution_boundary_contract_active") is True
    )
    boundary_verdict = _field(boundary, "execution_boundary_verdict")
    boundary_next = _field(boundary, "next_gate")
    verdict_ok = (
        boundary_verdict == UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_VERDICT
    )
    gate_ok = (
        boundary_next == UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_NEXT_GATE
    )

    contract_active = bool(boundary_active and verdict_ok and gate_ok)

    ref_packet_raw = boundary.get("evaluated_execution_boundary_packet")
    ref_packet = ref_packet_raw if isinstance(ref_packet_raw, dict) else {}

    if contract_active:
        evaluation = (
            evaluate_crypto_d1_post_boundary_research_only_next_step(
                next_step_decision_packet, ref_packet
            )
        )
        verdict = evaluation["verdict"]
        reasons = tuple(evaluation["reasons"])
    else:
        verdict = NEXT_STEP_VERDICT_AWAIT
        reasons = (
            "await_crypto_d1_human_approved_offline_acquisition_execution_"
            "boundary_contract",
        )

    state = (
        NEXT_STEP_STATE_ACTIVE if contract_active else NEXT_STEP_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = (
            NEXT_GATE_AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_CONTRACT  # noqa: E501
        )
    elif verdict == NEXT_STEP_VERDICT_PROCEED:
        next_gate = (
            NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED
        )
    elif verdict == NEXT_STEP_VERDICT_NEEDS_MORE_INFO:
        next_gate = NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_FIX_REQUIRED
    elif verdict == NEXT_STEP_VERDICT_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_PARKED
    else:
        next_gate = NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REJECTED

    post_boundary_next_step_required = (
        NEXT_STEP_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REQUIRED
        if contract_active
        else ""
    )

    echoed_packet = (
        dict(next_step_decision_packet)
        if isinstance(next_step_decision_packet, dict)
        else {}
    )
    referenced_packet = dict(ref_packet) if ref_packet else {}

    contract = {
        "schema_version": NEXT_STEP_SCHEMA_VERSION,
        "crypto_d1_execution_boundary_schema_version": BOUNDARY_SCHEMA_VERSION,
        "idea_id": _field(execution_boundary_contract, "idea_id"),
        "title": _field(execution_boundary_contract, "title"),
        "label": DEFAULT_NEXT_STEP_LABEL,
        "status": NEXT_STEP_STATUS,
        "stage": "CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_ONLY",
        "mode": "RESEARCH_ONLY",
        "crypto_d1_post_boundary_next_step_contract_active": contract_active,
        "crypto_d1_post_boundary_next_step_contract_state": state,
        "crypto_d1_execution_boundary_contract_active": bool(boundary_active),
        "crypto_d1_execution_boundary_verdict": boundary_verdict,
        "crypto_d1_execution_boundary_next_gate": boundary_next,
        "post_boundary_next_step_required": post_boundary_next_step_required,
        "post_boundary_next_required_action": (
            POST_BOUNDARY_NEXT_REQUIRED_ACTION
        ),
        "post_boundary_current_stage": POST_BOUNDARY_CURRENT_STAGE,
        "asset_lane": _field(execution_boundary_contract, "asset_lane"),
        "timeframe_lane": _field(
            execution_boundary_contract, "timeframe_lane"
        ),
        "next_step_packet_reference_placeholder": (
            _NEXT_STEP_REFERENCE_PLACEHOLDER
        ),
        "next_step_verdict": verdict,
        "next_step_verdict_reasons": reasons,
        "evaluated_next_step_packet": echoed_packet,
        "referenced_execution_boundary_packet": referenced_packet,
        "allowed_next_step_verdicts": ALLOWED_NEXT_STEP_VERDICTS,
        "required_next_step_fields": REQUIRED_NEXT_STEP_FIELDS,
        "next_step_required_text_fields": NEXT_STEP_REQUIRED_TEXT_FIELDS,
        "next_step_required_prohibitions": NEXT_STEP_REQUIRED_PROHIBITIONS,
        "next_step_required_affirmations": NEXT_STEP_REQUIRED_AFFIRMATIONS,
        "next_step_forbidden_allow_flags": NEXT_STEP_FORBIDDEN_ALLOW_FLAGS,
        "allowed_next_contract_modes": ALLOWED_NEXT_CONTRACT_MODES,
        "allowed_next_contract_types": ALLOWED_NEXT_CONTRACT_TYPES,
        "allowed_next_contract_scopes": ALLOWED_NEXT_CONTRACT_SCOPES,
        "allowed_proposed_next_contracts": ALLOWED_PROPOSED_NEXT_CONTRACTS,
        "automated_approval_markers": AUTOMATED_APPROVAL_MARKERS,
        "next_step_verdict_rationale_placeholder": (
            _NEXT_STEP_VERDICT_RATIONALE_PLACEHOLDER
        ),
        "next_step_blocked_capabilities": _NEXT_STEP_BLOCKED_CAPABILITIES,
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
        "crypto_d1_execution_boundary_contract": (
            execution_boundary_contract
            if isinstance(execution_boundary_contract, dict)
            else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_crypto_d1_post_boundary_research_only_next_step_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 post-boundary
    research-only next-step contract template. Pure; writes no file.
    Informational only."""
    verdicts = contract.get("allowed_next_step_verdicts") or ()
    fields = contract.get("required_next_step_fields") or ()
    text_fields = contract.get("next_step_required_text_fields") or ()
    prohibitions = contract.get("next_step_required_prohibitions") or ()
    affirmations = contract.get("next_step_required_affirmations") or ()
    forbidden_flags = contract.get("next_step_forbidden_allow_flags") or ()
    modes = contract.get("allowed_next_contract_modes") or ()
    types = contract.get("allowed_next_contract_types") or ()
    scopes = contract.get("allowed_next_contract_scopes") or ()
    proposed = contract.get("allowed_proposed_next_contracts") or ()
    markers = contract.get("automated_approval_markers") or ()
    reasons = contract.get("next_step_verdict_reasons") or ()
    blocked = contract.get("next_step_blocked_capabilities") or ()
    remaining_blocked = (
        contract.get("remaining_real_world_capabilities_blocked") or ()
    )
    next_steps = contract.get("human_operator_required_next_steps") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Crypto-D1 Post-Boundary Research-Only Next-Step "
        "Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a "
        "crypto-d1-post-boundary-next-step-only, paper-only, research-only, "
        "no-data-acquisition, no-data-fetch, no-data-inspection, no-qa-run, "
        "no-baseline-run, no-backtest, no-simulation, no-paper-live, "
        "no-broker-exchange, no-automation, and execution-free template -- it "
        "records only a paper next-step decision verdict, is not wired into "
        "any runtime state, writes no report file, acquires no data, inspects "
        "no data, connects to no venue, names only placeholders, and grants "
        "no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Execution boundary schema: "
        f"`{contract.get('crypto_d1_execution_boundary_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 post-boundary next-step contract active: "
        f"{contract.get('crypto_d1_post_boundary_next_step_contract_active', '')}"  # noqa: E501
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_post_boundary_next_step_contract_state', '')}"  # noqa: E501
    )
    lines.append(
        "Post-boundary next step required: "
        f"{contract.get('post_boundary_next_step_required', '')}"
    )
    lines.append(
        "Post-boundary next required action: "
        f"{contract.get('post_boundary_next_required_action', '')}"
    )
    lines.append(
        "Post-boundary current stage: "
        f"{contract.get('post_boundary_current_stage', '')}"
    )
    lines.append(f"Verdict: {contract.get('next_step_verdict', '')}")
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Next-Step Packet Reference")
    lines.append("")
    lines.append(
        "Next-step packet reference: "
        f"{contract.get('next_step_packet_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Next-Step Verdict Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Next-Step Verdicts")
    lines.append("")
    for x in verdicts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Next-Step Fields")
    lines.append("")
    for x in fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Next-Step Required Text Fields")
    lines.append("")
    for x in text_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Next-Step Required Prohibitions")
    lines.append("")
    for x in prohibitions:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Next-Step Required Affirmations")
    lines.append("")
    for x in affirmations:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Next-Step Forbidden Allow Flags")
    lines.append("")
    for x in forbidden_flags:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Next-Contract Modes")
    lines.append("")
    for x in modes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Next-Contract Types")
    lines.append("")
    for x in types:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Next-Contract Scopes")
    lines.append("")
    for x in scopes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Proposed Next Contracts")
    lines.append("")
    for x in proposed:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Automated Approval Markers")
    lines.append("")
    for x in markers:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Next-Step Verdict Rationale")
    lines.append("")
    lines.append(
        "Next-step verdict rationale: "
        f"{contract.get('next_step_verdict_rationale_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Next-Step Blocked Capabilities")
    lines.append("")
    for cap in blocked:
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
        "- A human operator must confirm this post-boundary next-step decision "
        "before any research-only dry-run-preview contract is drafted."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)

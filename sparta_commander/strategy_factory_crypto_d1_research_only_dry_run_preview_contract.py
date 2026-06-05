"""SPARTA Offline Strategy Factory - CRYPTO-D1 RESEARCH-ONLY DRY-RUN PREVIEW
CONTRACT.

Bundle 49 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only paper decision contract* builder and evaluator. It
consumes a Bundle 48 crypto-d1 POST-BOUNDARY RESEARCH-ONLY NEXT-STEP contract
and, only when that next-step contract is active with next_step_verdict ==
PROCEED_TO_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT and next_gate ==
CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED (the concrete Bundle
48 signal that a research-only dry-run preview contract must be defined),
evaluates a proposed dry-run preview packet on paper and returns a deterministic
verdict describing whether a future research-only dry-run preview would be
*allowed to be previewed* -- or whether the lane should park, need more info, or
be rejected.

It exists so the system can DEFINE and VALIDATE, on paper, what a future
research-only dry-run preview would be permitted to preview, WITHOUT ever
running that preview. It does NOT perform a dry run. It NEVER acquires data,
fetches data, inspects data, loads a dataset, runs QA, a baseline, a backtest,
or a simulation, never produces a trade signal, never validates market data,
never reaches a broker/exchange/order/account/API surface, never trades paper or
live, triggers no automation, and writes no runtime, registry, ledger,
dashboard, or report state.

Reaching a DRY_RUN_PREVIEW_READY verdict unlocks NOTHING real. It only records,
on paper, that a proposed dry-run preview packet is shaped as research-only,
preview-only, mock/static-metadata-only -- and even that still requires a
separate, later, human-run step this module does not authorize. Any other
upstream shape (blocked, malformed, wrong stage, not ready, parked, rejected,
needs-more-info, or wrong gate) yields the
AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT verdict.

It opens no network, spawns no subprocess, writes no file, reads no file, lists
no directory, records no timestamp, mints no random id, reads no environment,
and dynamically imports nothing.

Public API:
  - PREVIEW_SCHEMA_VERSION
  - DEFAULT_PREVIEW_LABEL
  - PREVIEW_STATUS
  - PREVIEW_SAFETY_POSTURE
  - PREVIEW_STATE_ACTIVE / PREVIEW_STATE_BLOCKED
  - PREVIEW_VERDICT_READY
  - PREVIEW_VERDICT_NEEDS_MORE_INFO
  - PREVIEW_VERDICT_REJECTED
  - PREVIEW_VERDICT_PARKED
  - PREVIEW_VERDICT_AWAIT
  - ALLOWED_PREVIEW_VERDICTS
  - UPSTREAM_REQUIRED_NEXT_STEP_VERDICT
  - UPSTREAM_REQUIRED_NEXT_STEP_NEXT_GATE
  - DRY_RUN_PREVIEW_NEXT_REQUIRED_ACTION
  - DRY_RUN_PREVIEW_CURRENT_STAGE
  - PREVIEW_CRYPTO_D1_DRY_RUN_PREVIEW_REQUIRED
  - NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_HUMAN_RUN_REQUIRED
  - NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_PARKED
  - NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT
  - REQUIRED_PREVIEW_FIELDS
  - PREVIEW_REQUIRED_TEXT_FIELDS
  - PREVIEW_REQUIRED_PROHIBITIONS
  - PREVIEW_REQUIRED_AFFIRMATIONS
  - PREVIEW_FORBIDDEN_ALLOW_FLAGS
  - ALLOWED_PREVIEW_MODES
  - ALLOWED_PREVIEW_SCOPES
  - AUTOMATED_APPROVAL_MARKERS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - evaluate_crypto_d1_research_only_dry_run_preview(packet, next_step_ref_packet=None)
  - build_crypto_d1_research_only_dry_run_preview_contract(post_boundary_next_step_contract, dry_run_preview_packet=None)
  - validate_crypto_d1_research_only_dry_run_preview_contract(contract)
  - render_crypto_d1_research_only_dry_run_preview_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_post_boundary_research_only_next_step_contract import (  # noqa: E501
    NEXT_STEP_SCHEMA_VERSION as POST_BOUNDARY_NEXT_STEP_SCHEMA_VERSION,
    NEXT_STEP_SAFETY_POSTURE as _POST_BOUNDARY_SAFETY_POSTURE,
    NEXT_STEP_VERDICT_PROCEED as _UPSTREAM_NEXT_STEP_VERDICT_PROCEED,
    NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED as _UPSTREAM_DRY_RUN_PREVIEW_GATE,  # noqa: E501
    POST_BOUNDARY_NEXT_REQUIRED_ACTION as _POST_BOUNDARY_NEXT_REQUIRED_ACTION,
    POST_BOUNDARY_CURRENT_STAGE as _POST_BOUNDARY_CURRENT_STAGE,
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
)

__all__ = [
    "PREVIEW_SCHEMA_VERSION",
    "DEFAULT_PREVIEW_LABEL",
    "PREVIEW_STATUS",
    "PREVIEW_SAFETY_POSTURE",
    "PREVIEW_STATE_ACTIVE",
    "PREVIEW_STATE_BLOCKED",
    "PREVIEW_VERDICT_READY",
    "PREVIEW_VERDICT_NEEDS_MORE_INFO",
    "PREVIEW_VERDICT_REJECTED",
    "PREVIEW_VERDICT_PARKED",
    "PREVIEW_VERDICT_AWAIT",
    "ALLOWED_PREVIEW_VERDICTS",
    "UPSTREAM_REQUIRED_NEXT_STEP_VERDICT",
    "UPSTREAM_REQUIRED_NEXT_STEP_NEXT_GATE",
    "DRY_RUN_PREVIEW_NEXT_REQUIRED_ACTION",
    "DRY_RUN_PREVIEW_CURRENT_STAGE",
    "PREVIEW_CRYPTO_D1_DRY_RUN_PREVIEW_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_HUMAN_RUN_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_FIX_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_PARKED",
    "NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_REJECTED",
    "NEXT_GATE_AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT",
    "REQUIRED_PREVIEW_FIELDS",
    "PREVIEW_REQUIRED_TEXT_FIELDS",
    "PREVIEW_REQUIRED_PROHIBITIONS",
    "PREVIEW_REQUIRED_AFFIRMATIONS",
    "PREVIEW_FORBIDDEN_ALLOW_FLAGS",
    "ALLOWED_PREVIEW_MODES",
    "ALLOWED_PREVIEW_SCOPES",
    "AUTOMATED_APPROVAL_MARKERS",
    "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "evaluate_crypto_d1_research_only_dry_run_preview",
    "build_crypto_d1_research_only_dry_run_preview_contract",
    "validate_crypto_d1_research_only_dry_run_preview_contract",
    "render_crypto_d1_research_only_dry_run_preview_contract_markdown",
]

PREVIEW_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_research_only_dry_run_preview_contract.v1"
)
DEFAULT_PREVIEW_LABEL = (
    "Strategy Factory Crypto-D1 Research-Only Dry-Run Preview Contract"
)
PREVIEW_STATUS = (
    "READ_ONLY_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT"
)

PREVIEW_STATE_ACTIVE = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_ACTIVE"
)
PREVIEW_STATE_BLOCKED = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_BLOCKED"
)

PREVIEW_VERDICT_READY = "DRY_RUN_PREVIEW_READY"
PREVIEW_VERDICT_NEEDS_MORE_INFO = "DRY_RUN_PREVIEW_NEEDS_MORE_INFO"
PREVIEW_VERDICT_REJECTED = "DRY_RUN_PREVIEW_REJECTED"
PREVIEW_VERDICT_PARKED = "DRY_RUN_PREVIEW_PARKED"
PREVIEW_VERDICT_AWAIT = (
    "AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT"
)

ALLOWED_PREVIEW_VERDICTS: tuple[str, ...] = (
    PREVIEW_VERDICT_READY,
    PREVIEW_VERDICT_NEEDS_MORE_INFO,
    PREVIEW_VERDICT_REJECTED,
    PREVIEW_VERDICT_PARKED,
    PREVIEW_VERDICT_AWAIT,
)

# The exact upstream Bundle 48 signal this bundle activates from.
UPSTREAM_REQUIRED_NEXT_STEP_VERDICT = _UPSTREAM_NEXT_STEP_VERDICT_PROCEED
UPSTREAM_REQUIRED_NEXT_STEP_NEXT_GATE = _UPSTREAM_DRY_RUN_PREVIEW_GATE

# Next action / stage as published by the mission-flow registry (via Bundle 48).
# This bundle FULFILLS that action on paper; it does not advance the registry.
DRY_RUN_PREVIEW_NEXT_REQUIRED_ACTION = _POST_BOUNDARY_NEXT_REQUIRED_ACTION
DRY_RUN_PREVIEW_CURRENT_STAGE = _POST_BOUNDARY_CURRENT_STAGE

# The conceptual decision this bundle fulfills once it is active.
PREVIEW_CRYPTO_D1_DRY_RUN_PREVIEW_REQUIRED = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_REQUIRED"
)

# Next-gate outcomes by verdict. A READY preview is still only a paper readiness
# verdict; running the preview itself is a separate, later, human step.
NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_HUMAN_RUN_REQUIRED = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_SEPARATE_HUMAN_RUN_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_FIX_REQUIRED = (
    "CRYPTO_D1_DRY_RUN_PREVIEW_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_PARKED = (
    "CRYPTO_D1_DRY_RUN_PREVIEW_PARKED"
)
NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_REJECTED = (
    "CRYPTO_D1_DRY_RUN_PREVIEW_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT = (
    "AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-48).
PREVIEW_SAFETY_POSTURE: dict[str, bool] = dict(_POST_BOUNDARY_SAFETY_POSTURE)

# Descriptive text fields a human operator records on a dry-run preview packet.
PREVIEW_REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
    "preview_packet_id",
    "upstream_next_step_id",
    "proposed_preview_scope",
    "proposed_preview_mode",
    "preview_inputs_description",
    "preview_outputs_description",
    "next_step_boundary",
)

# Prohibition flags that must each be affirmed True. A present-but-not-affirmed
# value is a request to RELAX a prohibition -- a hard REJECTED. An absent value
# is a missing requirement (NEEDS_MORE_INFO).
PREVIEW_REQUIRED_PROHIBITIONS: tuple[str, ...] = (
    "prohibited_real_data_acquisition",
    "prohibited_data_fetch",
    "prohibited_data_inspection",
    "prohibited_dataset_loading",
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

# Operator affirmation flags the preview packet must carry (each affirmed True).
# This includes the "allowed *only*" scope flags and the "preview does not *"
# negative affirmations, which are all required-True markers of a safe preview.
PREVIEW_REQUIRED_AFFIRMATIONS: tuple[str, ...] = (
    "allowed_mock_inputs_only",
    "allowed_static_contract_metadata_only",
    "preview_does_not_execute",
    "preview_does_not_validate_market_data",
    "preview_does_not_produce_trade_signal",
    "human_operator_review_required",
    "research_only_acknowledgement",
)

# Every required True-flag (prohibitions + affirmations). Present-but-not-
# affirmed -> REJECTED; absent -> NEEDS_MORE_INFO.
_REQUIRED_TRUE_FLAGS: tuple[str, ...] = (
    PREVIEW_REQUIRED_PROHIBITIONS + PREVIEW_REQUIRED_AFFIRMATIONS
)

# The full set of required dry-run preview packet fields (31).
REQUIRED_PREVIEW_FIELDS: tuple[str, ...] = (
    PREVIEW_REQUIRED_TEXT_FIELDS
    + PREVIEW_REQUIRED_PROHIBITIONS
    + PREVIEW_REQUIRED_AFFIRMATIONS
)

# Positive allow/grant flags a preview must NOT request -- any truthy value
# forces a hard REJECTED (it tries to permit a real, dangerous capability or to
# actually execute the dry run / produce a signal / validate market data).
PREVIEW_FORBIDDEN_ALLOW_FLAGS: tuple[str, ...] = (
    "allow_real_data_acquisition",
    "real_data_acquisition_allowed",
    "allow_data_fetch",
    "data_fetch_allowed",
    "allow_data_inspection",
    "data_inspection_allowed",
    "allow_dataset_load",
    "dataset_load_allowed",
    "allow_dataset_loading",
    "dataset_loading_allowed",
    "loads_dataset",
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
    "allow_trade_signal",
    "trade_signal_allowed",
    "produces_trade_signal",
    "produces_trade_signals",
    "allow_market_data_validation",
    "market_data_validation_allowed",
    "validates_market_data",
    "allow_dry_run_execution",
    "dry_run_execution_allowed",
    "executes_dry_run",
    "runs_dry_run",
    "performs_dry_run",
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
# REJECTED (the preview tries to permit something outside research-only scope).
ALLOWED_PREVIEW_MODES: tuple[str, ...] = (
    "research_only",
    "research-only",
)
ALLOWED_PREVIEW_SCOPES: tuple[str, ...] = (
    "dry_run_preview_only",
    "research_only_preview",
    "preview_only",
    "no_data_preview",
    "offline_preview",
    "mock_inputs_preview",
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

# Preview-phase blocked capabilities.
_PREVIEW_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "crypto_d1_real_data_acquisition",
    "crypto_d1_data_fetch",
    "crypto_d1_data_inspection",
    "crypto_d1_dataset_load",
    "crypto_d1_qa_run",
    "crypto_d1_baseline_run",
    "crypto_d1_backtest",
    "crypto_d1_simulation",
    "crypto_d1_dry_run_execution",
    "crypto_d1_trade_signal_production",
    "crypto_d1_market_data_validation",
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
    "dry_run_execution",
    "trade_signal_production",
    "market_data_validation",
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
)

_PREVIEW_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 dry-run preview packet is a paper placeholder describing what a "
    "future research-only dry-run preview would be ALLOWED to preview using "
    "mock inputs and static contract metadata only -- it previews nothing now, "
    "acquires nothing, inspects nothing, and executes nothing."
)

_PREVIEW_VERDICT_RATIONALE_PLACEHOLDER = (
    "Dry-run preview verdict rationale is a paper placeholder for a "
    "human-recorded acceptance, deferral, or refusal and its supporting reason."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 research-only dry-run preview decision contract "
    "template and is execution-free.",
    "It DEFINES what a future dry-run preview would be allowed to preview; it "
    "does NOT perform a dry run.",
    "It evaluates a paper preview packet only and writes no report file.",
    "It writes no runtime state, acquires no data, inspects no data, and loads "
    "no dataset.",
    "A READY verdict means only that the preview packet is shaped as "
    "research-only, preview-only, mock/static-metadata-only; it authorizes no "
    "data work and no preview run.",
    "It connects to no exchange, broker, or live venue and uses no API keys.",
    "QA, baseline, backtest, simulation, paper, and live all stay blocked.",
    "It produces no trade signal and validates no market data.",
    "No crypto-d1 dataset, qa_report, manifest, checksum, or fees file is "
    "opened, inspected, loaded, or accessed.",
    "A human operator alone may record this decision; no automated author is "
    "accepted.",
    "Any READY verdict still requires a separate, later, human-run step that "
    "this template does not authorize.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must record a dry-run preview verdict with a supporting "
    "rationale on paper.",
    "A human operator must confirm the proposed preview is research-only and "
    "preview-only, uses mock inputs and static contract metadata only, and "
    "performs no data acquisition, fetch, inspection, dataset loading, QA, "
    "baseline, backtest, simulation, trade-signal production, market-data "
    "validation, paper/live, broker/exchange, order, account, API, automation, "
    "or runtime/registry/dashboard writes.",
    "A human operator must confirm the preview packet matches the approved "
    "Bundle 48 post-boundary next-step decision exactly.",
    "A human operator must decide whether the proposed research-only dry-run "
    "preview may actually be run later as a separate step.",
    "No automated step may proceed without human sign-off.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "crypto_d1_post_boundary_next_step_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "crypto_d1_research_only_dry_run_preview_contract_active",
    "crypto_d1_research_only_dry_run_preview_contract_state",
    "crypto_d1_post_boundary_next_step_contract_active",
    "crypto_d1_post_boundary_next_step_verdict",
    "crypto_d1_post_boundary_next_step_next_gate",
    "dry_run_preview_required",
    "dry_run_preview_next_required_action",
    "dry_run_preview_current_stage",
    "asset_lane",
    "timeframe_lane",
    "preview_packet_reference_placeholder",
    "dry_run_preview_verdict",
    "dry_run_preview_verdict_reasons",
    "evaluated_preview_packet",
    "referenced_next_step_packet",
    "allowed_dry_run_preview_verdicts",
    "required_preview_fields",
    "preview_required_text_fields",
    "preview_required_prohibitions",
    "preview_required_affirmations",
    "preview_forbidden_allow_flags",
    "allowed_preview_modes",
    "allowed_preview_scopes",
    "automated_approval_markers",
    "dry_run_preview_verdict_rationale_placeholder",
    "preview_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
    "crypto_d1_post_boundary_next_step_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(PREVIEW_SAFETY_POSTURE)


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
    """Return mismatch reasons where a present preview field clearly disagrees
    with the approved Bundle 48 next-step packet. Absent fields are not a
    mismatch; only present-but-conflicting values are a hard mismatch."""
    if not isinstance(ref_packet, dict) or not ref_packet:
        return ()

    reasons: list[str] = []
    pv = packet.get("upstream_next_step_id")
    rv = ref_packet.get("decision_packet_id")
    if _present(pv) and _present(rv) and _scalar(pv) != _scalar(rv):
        reasons.append("mismatch:upstream_next_step_id")
    return tuple(reasons)


def _reject_reasons(
    packet: dict[str, Any], ref_packet: dict[str, Any]
) -> tuple[str, ...]:
    """Return any hard REJECTED reasons: a permitted dangerous capability, a
    relaxed prohibition, a disallowed enum value, an automated author, granted
    authority, or a clear mismatch with the approved next-step decision."""
    reasons: list[str] = []

    for flag in PREVIEW_FORBIDDEN_ALLOW_FLAGS:
        if _truthy(packet.get(flag)):
            reasons.append(f"forbidden_allow:{flag}")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag in packet and not _affirm(packet.get(flag)):
            reasons.append(f"prohibition_relaxed:{flag}")

    enum_pairs = (
        ("proposed_preview_mode", ALLOWED_PREVIEW_MODES),
        ("proposed_preview_scope", ALLOWED_PREVIEW_SCOPES),
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
            reasons.append("operator_parked_dry_run_preview")
            break

    if _scalar(packet.get("operator_decision")) in park_values:
        reasons.append("operator_decision_parked")
    if _scalar(packet.get("decision")) in park_values:
        reasons.append("decision_parked")

    return tuple(reasons)


def _missing_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return unmet requirements for an otherwise-safe preview packet."""
    missing: list[str] = []

    for key in PREVIEW_REQUIRED_TEXT_FIELDS:
        if not _present(packet.get(key)):
            missing.append(f"{key}_required")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag not in packet:
            missing.append(f"{flag}_must_be_affirmed_true")

    return tuple(missing)


def evaluate_crypto_d1_research_only_dry_run_preview(
    packet: Any,
    next_step_ref_packet: Any = None,
) -> dict[str, Any]:
    """Return a deterministic verdict for a dry-run preview packet against the
    approved Bundle 48 next-step packet. Pure; no I/O, no mutation, no
    timestamp, no random id. Unknown/malformed inputs never raise. The verdict
    is one of DRY_RUN_PREVIEW_READY, DRY_RUN_PREVIEW_NEEDS_MORE_INFO,
    DRY_RUN_PREVIEW_REJECTED, or DRY_RUN_PREVIEW_PARKED. It evaluates the SHAPE
    of a paper preview only and unlocks nothing. REJECTED (permits a dangerous
    capability / relaxes a prohibition / disallowed value / authority-granting /
    mismatched) is checked before parking, and parking before completeness, so
    an unsafe preview is rejected even when it would otherwise park or merely
    need more info."""
    p = packet if isinstance(packet, dict) else {}
    ref = next_step_ref_packet if isinstance(next_step_ref_packet, dict) else {}

    if not p:
        return {
            "verdict": PREVIEW_VERDICT_NEEDS_MORE_INFO,
            "reasons": ("dry_run_preview_packet_missing",),
        }

    rejected = _reject_reasons(p, ref)
    if rejected:
        return {
            "verdict": PREVIEW_VERDICT_REJECTED,
            "reasons": rejected,
        }

    park = _park_reasons(p)
    if park:
        return {
            "verdict": PREVIEW_VERDICT_PARKED,
            "reasons": park,
        }

    missing = _missing_reasons(p)
    if not missing:
        return {
            "verdict": PREVIEW_VERDICT_READY,
            "reasons": (
                "research_only_dry_run_preview_fully_specified_mock_static_"
                "only_and_matches_next_step",
            ),
        }

    return {
        "verdict": PREVIEW_VERDICT_NEEDS_MORE_INFO,
        "reasons": missing,
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == PREVIEW_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = (
        safe.get("stage") == "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_ONLY"
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
        tuple(safe.get("allowed_dry_run_preview_verdicts") or ())
        == ALLOWED_PREVIEW_VERDICTS
    )
    fields_ok = (
        tuple(safe.get("required_preview_fields") or ())
        == REQUIRED_PREVIEW_FIELDS
    )
    text_fields_ok = (
        tuple(safe.get("preview_required_text_fields") or ())
        == PREVIEW_REQUIRED_TEXT_FIELDS
    )
    prohibitions_ok = (
        tuple(safe.get("preview_required_prohibitions") or ())
        == PREVIEW_REQUIRED_PROHIBITIONS
    )
    affirmations_ok = (
        tuple(safe.get("preview_required_affirmations") or ())
        == PREVIEW_REQUIRED_AFFIRMATIONS
    )
    forbidden_flags_ok = (
        tuple(safe.get("preview_forbidden_allow_flags") or ())
        == PREVIEW_FORBIDDEN_ALLOW_FLAGS
    )
    modes_ok = (
        tuple(safe.get("allowed_preview_modes") or ())
        == ALLOWED_PREVIEW_MODES
    )
    scopes_ok = (
        tuple(safe.get("allowed_preview_scopes") or ())
        == ALLOWED_PREVIEW_SCOPES
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
        safe.get("dry_run_preview_verdict") in ALLOWED_PREVIEW_VERDICTS
    )
    blocked_present_ok = (
        len(tuple(safe.get("preview_blocked_capabilities") or ())) >= 1
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
        and scopes_ok
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
        "allowed_dry_run_preview_verdicts_ok": verdicts_ok,
        "required_preview_fields_ok": fields_ok,
        "preview_required_text_fields_ok": text_fields_ok,
        "preview_required_prohibitions_ok": prohibitions_ok,
        "preview_required_affirmations_ok": affirmations_ok,
        "preview_forbidden_allow_flags_ok": forbidden_flags_ok,
        "allowed_preview_modes_ok": modes_ok,
        "allowed_preview_scopes_ok": scopes_ok,
        "automated_approval_markers_ok": markers_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "dry_run_preview_verdict_value_ok": verdict_value_ok,
        "preview_blocked_capabilities_present": blocked_present_ok,
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_research_only_dry_run_preview_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 research-only dry-run
    preview contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_research_only_dry_run_preview_contract(
    post_boundary_next_step_contract: Any,
    dry_run_preview_packet: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 research-only dry-run
    preview contract template plus a paper verdict for a proposed dry-run
    preview packet.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (crypto_d1_research_only_dry_run_preview_contract_active=True) solely when
    the upstream Bundle 48 crypto-d1 post-boundary research-only next-step
    contract is active AND its next_step_verdict is
    PROCEED_TO_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT AND its next_gate is the
    Bundle 48 ready gate (CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_
    REQUIRED). When inactive, the verdict is
    AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT regardless of
    the packet. Even when active and READY, every authorization field stays
    False -- it evaluates the SHAPE of a paper preview only, performs no dry
    run, acquires nothing, connects to nothing, approves no QA, no baseline, no
    backtest, produces no trade signal, validates no market data, writes no
    report file, writes no runtime state, names only placeholders, and grants
    nothing. Returned dicts are fresh."""
    upstream = (
        post_boundary_next_step_contract
        if isinstance(post_boundary_next_step_contract, dict)
        else {}
    )

    upstream_active = (
        upstream.get("crypto_d1_post_boundary_next_step_contract_active")
        is True
    )
    upstream_verdict = _field(upstream, "next_step_verdict")
    upstream_next = _field(upstream, "next_gate")
    verdict_ok = upstream_verdict == UPSTREAM_REQUIRED_NEXT_STEP_VERDICT
    gate_ok = upstream_next == UPSTREAM_REQUIRED_NEXT_STEP_NEXT_GATE

    contract_active = bool(upstream_active and verdict_ok and gate_ok)

    ref_packet_raw = upstream.get("evaluated_next_step_packet")
    ref_packet = ref_packet_raw if isinstance(ref_packet_raw, dict) else {}

    if contract_active:
        evaluation = evaluate_crypto_d1_research_only_dry_run_preview(
            dry_run_preview_packet, ref_packet
        )
        verdict = evaluation["verdict"]
        reasons = tuple(evaluation["reasons"])
    else:
        verdict = PREVIEW_VERDICT_AWAIT
        reasons = (
            "await_crypto_d1_post_boundary_research_only_next_step_contract",
        )

    state = (
        PREVIEW_STATE_ACTIVE if contract_active else PREVIEW_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = (
            NEXT_GATE_AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT  # noqa: E501
        )
    elif verdict == PREVIEW_VERDICT_READY:
        next_gate = (
            NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_HUMAN_RUN_REQUIRED  # noqa: E501
        )
    elif verdict == PREVIEW_VERDICT_NEEDS_MORE_INFO:
        next_gate = NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_FIX_REQUIRED
    elif verdict == PREVIEW_VERDICT_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_PARKED
    else:
        next_gate = NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_REJECTED

    dry_run_preview_required = (
        PREVIEW_CRYPTO_D1_DRY_RUN_PREVIEW_REQUIRED if contract_active else ""
    )

    echoed_packet = (
        dict(dry_run_preview_packet)
        if isinstance(dry_run_preview_packet, dict)
        else {}
    )
    referenced_packet = dict(ref_packet) if ref_packet else {}

    contract = {
        "schema_version": PREVIEW_SCHEMA_VERSION,
        "crypto_d1_post_boundary_next_step_schema_version": (
            POST_BOUNDARY_NEXT_STEP_SCHEMA_VERSION
        ),
        "idea_id": _field(post_boundary_next_step_contract, "idea_id"),
        "title": _field(post_boundary_next_step_contract, "title"),
        "label": DEFAULT_PREVIEW_LABEL,
        "status": PREVIEW_STATUS,
        "stage": "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_ONLY",
        "mode": "RESEARCH_ONLY",
        "crypto_d1_research_only_dry_run_preview_contract_active": (
            contract_active
        ),
        "crypto_d1_research_only_dry_run_preview_contract_state": state,
        "crypto_d1_post_boundary_next_step_contract_active": bool(
            upstream_active
        ),
        "crypto_d1_post_boundary_next_step_verdict": upstream_verdict,
        "crypto_d1_post_boundary_next_step_next_gate": upstream_next,
        "dry_run_preview_required": dry_run_preview_required,
        "dry_run_preview_next_required_action": (
            DRY_RUN_PREVIEW_NEXT_REQUIRED_ACTION
        ),
        "dry_run_preview_current_stage": DRY_RUN_PREVIEW_CURRENT_STAGE,
        "asset_lane": _field(post_boundary_next_step_contract, "asset_lane"),
        "timeframe_lane": _field(
            post_boundary_next_step_contract, "timeframe_lane"
        ),
        "preview_packet_reference_placeholder": (
            _PREVIEW_REFERENCE_PLACEHOLDER
        ),
        "dry_run_preview_verdict": verdict,
        "dry_run_preview_verdict_reasons": reasons,
        "evaluated_preview_packet": echoed_packet,
        "referenced_next_step_packet": referenced_packet,
        "allowed_dry_run_preview_verdicts": ALLOWED_PREVIEW_VERDICTS,
        "required_preview_fields": REQUIRED_PREVIEW_FIELDS,
        "preview_required_text_fields": PREVIEW_REQUIRED_TEXT_FIELDS,
        "preview_required_prohibitions": PREVIEW_REQUIRED_PROHIBITIONS,
        "preview_required_affirmations": PREVIEW_REQUIRED_AFFIRMATIONS,
        "preview_forbidden_allow_flags": PREVIEW_FORBIDDEN_ALLOW_FLAGS,
        "allowed_preview_modes": ALLOWED_PREVIEW_MODES,
        "allowed_preview_scopes": ALLOWED_PREVIEW_SCOPES,
        "automated_approval_markers": AUTOMATED_APPROVAL_MARKERS,
        "dry_run_preview_verdict_rationale_placeholder": (
            _PREVIEW_VERDICT_RATIONALE_PLACEHOLDER
        ),
        "preview_blocked_capabilities": _PREVIEW_BLOCKED_CAPABILITIES,
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
        "crypto_d1_post_boundary_next_step_contract": (
            post_boundary_next_step_contract
            if isinstance(post_boundary_next_step_contract, dict)
            else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_crypto_d1_research_only_dry_run_preview_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 research-only
    dry-run preview contract template. Pure; writes no file. Informational
    only."""
    verdicts = contract.get("allowed_dry_run_preview_verdicts") or ()
    fields = contract.get("required_preview_fields") or ()
    text_fields = contract.get("preview_required_text_fields") or ()
    prohibitions = contract.get("preview_required_prohibitions") or ()
    affirmations = contract.get("preview_required_affirmations") or ()
    forbidden_flags = contract.get("preview_forbidden_allow_flags") or ()
    modes = contract.get("allowed_preview_modes") or ()
    scopes = contract.get("allowed_preview_scopes") or ()
    markers = contract.get("automated_approval_markers") or ()
    reasons = contract.get("dry_run_preview_verdict_reasons") or ()
    blocked = contract.get("preview_blocked_capabilities") or ()
    remaining_blocked = (
        contract.get("remaining_real_world_capabilities_blocked") or ()
    )
    next_steps = contract.get("human_operator_required_next_steps") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Crypto-D1 Research-Only Dry-Run Preview Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a "
        "crypto-d1-research-only-dry-run-preview-only, paper-only, "
        "no-dry-run, no-data-acquisition, no-data-fetch, no-data-inspection, "
        "no-dataset-loading, no-qa-run, no-baseline-run, no-backtest, "
        "no-simulation, no-trade-signal, no-market-data-validation, "
        "no-paper-live, no-broker-exchange, no-automation, and execution-free "
        "template -- it records only a paper dry-run preview decision verdict, "
        "is not wired into any runtime state, writes no report file, acquires "
        "no data, inspects no data, loads no dataset, connects to no venue, "
        "names only placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Post-boundary next-step schema: "
        f"`{contract.get('crypto_d1_post_boundary_next_step_schema_version', '')}`"  # noqa: E501
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 research-only dry-run preview contract active: "
        f"{contract.get('crypto_d1_research_only_dry_run_preview_contract_active', '')}"  # noqa: E501
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_research_only_dry_run_preview_contract_state', '')}"  # noqa: E501
    )
    lines.append(
        "Dry-run preview required: "
        f"{contract.get('dry_run_preview_required', '')}"
    )
    lines.append(
        "Dry-run preview next required action: "
        f"{contract.get('dry_run_preview_next_required_action', '')}"
    )
    lines.append(
        "Dry-run preview current stage: "
        f"{contract.get('dry_run_preview_current_stage', '')}"
    )
    lines.append(f"Verdict: {contract.get('dry_run_preview_verdict', '')}")
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Preview Packet Reference")
    lines.append("")
    lines.append(
        "Preview packet reference: "
        f"{contract.get('preview_packet_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Dry-Run Preview Verdict Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Dry-Run Preview Verdicts")
    lines.append("")
    for x in verdicts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Preview Fields")
    lines.append("")
    for x in fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Preview Required Text Fields")
    lines.append("")
    for x in text_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Preview Required Prohibitions")
    lines.append("")
    for x in prohibitions:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Preview Required Affirmations")
    lines.append("")
    for x in affirmations:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Preview Forbidden Allow Flags")
    lines.append("")
    for x in forbidden_flags:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Preview Modes")
    lines.append("")
    for x in modes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Preview Scopes")
    lines.append("")
    for x in scopes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Automated Approval Markers")
    lines.append("")
    for x in markers:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Dry-Run Preview Verdict Rationale")
    lines.append("")
    lines.append(
        "Dry-run preview verdict rationale: "
        f"{contract.get('dry_run_preview_verdict_rationale_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Preview Blocked Capabilities")
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
        "- A human operator must confirm this dry-run preview decision before "
        "any research-only dry-run preview is actually run as a separate step."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)

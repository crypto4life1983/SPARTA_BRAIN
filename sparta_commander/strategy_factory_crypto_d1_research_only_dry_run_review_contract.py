"""SPARTA Offline Strategy Factory - CRYPTO-D1 RESEARCH-ONLY DRY-RUN REVIEW
CONTRACT.

Bundle 50 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only paper decision contract* builder and evaluator. It
consumes a Bundle 49 crypto-d1 RESEARCH-ONLY DRY-RUN PREVIEW contract and, only
when that preview contract is active with dry_run_preview_verdict ==
DRY_RUN_PREVIEW_READY and next_gate ==
CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_SEPARATE_HUMAN_RUN_REQUIRED (the
concrete Bundle 49 signal that a research-only dry-run review must be recorded),
evaluates a proposed dry-run REVIEW packet on paper and returns a deterministic
verdict describing whether the proposed research-only dry-run preview was
reviewed as safe -- or whether the lane should park, need more info, or be
rejected.

It exists so the system can REVIEW and VALIDATE, on paper, a research-only
dry-run preview packet WITHOUT ever running a dry run. It does NOT run a dry run.
It NEVER acquires data, fetches data, inspects data, loads a dataset, runs QA, a
baseline, a backtest, or a simulation, never produces a trade signal, never
validates market data, never reaches a broker/exchange/order/account/API
surface, never trades paper or live, triggers no automation, and writes no
runtime, registry, ledger, dashboard, or report state.

Reaching a DRY_RUN_REVIEW_READY verdict unlocks NOTHING real. It only records,
on paper, that a proposed dry-run preview was reviewed by a human as
research-only, mock/static-metadata-only, performing no data work and no
execution -- and even that still requires a separate, later, human-run step this
module does not authorize. Any other upstream shape (blocked, malformed, wrong
stage, not ready, parked, rejected, needs-more-info, or wrong gate) yields the
AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT verdict.

It opens no network, spawns no subprocess, writes no file, reads no file, lists
no directory, records no timestamp, mints no random id, reads no environment,
and dynamically imports nothing.

Public API:
  - REVIEW_SCHEMA_VERSION
  - DEFAULT_REVIEW_LABEL
  - REVIEW_STATUS
  - REVIEW_SAFETY_POSTURE
  - REVIEW_STATE_ACTIVE / REVIEW_STATE_BLOCKED
  - REVIEW_VERDICT_READY
  - REVIEW_VERDICT_NEEDS_MORE_INFO
  - REVIEW_VERDICT_REJECTED
  - REVIEW_VERDICT_PARKED
  - REVIEW_VERDICT_AWAIT
  - ALLOWED_REVIEW_VERDICTS
  - UPSTREAM_REQUIRED_PREVIEW_VERDICT
  - UPSTREAM_REQUIRED_PREVIEW_NEXT_GATE
  - DRY_RUN_REVIEW_NEXT_REQUIRED_ACTION
  - DRY_RUN_REVIEW_CURRENT_STAGE
  - REVIEW_CRYPTO_D1_DRY_RUN_REVIEW_REQUIRED
  - NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_READY_HUMAN_RUN_REQUIRED
  - NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_PARKED
  - NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT
  - REQUIRED_REVIEW_FIELDS
  - REVIEW_REQUIRED_TEXT_FIELDS
  - REVIEW_REQUIRED_AFFIRMATIONS
  - REVIEW_FORBIDDEN_ALLOW_FLAGS
  - ALLOWED_REVIEW_MODES
  - ALLOWED_REVIEW_SCOPES
  - AUTOMATED_APPROVAL_MARKERS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - evaluate_crypto_d1_research_only_dry_run_review(packet, preview_ref_packet=None)
  - build_crypto_d1_research_only_dry_run_review_contract(dry_run_preview_contract, dry_run_review_packet=None)
  - validate_crypto_d1_research_only_dry_run_review_contract(contract)
  - render_crypto_d1_research_only_dry_run_review_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_preview_contract import (  # noqa: E501
    PREVIEW_SCHEMA_VERSION as DRY_RUN_PREVIEW_SCHEMA_VERSION,
    PREVIEW_SAFETY_POSTURE as _PREVIEW_SAFETY_POSTURE,
    PREVIEW_VERDICT_READY as _UPSTREAM_PREVIEW_VERDICT_READY,
    NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_HUMAN_RUN_REQUIRED as _UPSTREAM_DRY_RUN_REVIEW_GATE,  # noqa: E501
    DRY_RUN_PREVIEW_NEXT_REQUIRED_ACTION as _PREVIEW_NEXT_REQUIRED_ACTION,
    DRY_RUN_PREVIEW_CURRENT_STAGE as _PREVIEW_CURRENT_STAGE,
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
)

__all__ = [
    "REVIEW_SCHEMA_VERSION",
    "DEFAULT_REVIEW_LABEL",
    "REVIEW_STATUS",
    "REVIEW_SAFETY_POSTURE",
    "REVIEW_STATE_ACTIVE",
    "REVIEW_STATE_BLOCKED",
    "REVIEW_VERDICT_READY",
    "REVIEW_VERDICT_NEEDS_MORE_INFO",
    "REVIEW_VERDICT_REJECTED",
    "REVIEW_VERDICT_PARKED",
    "REVIEW_VERDICT_AWAIT",
    "ALLOWED_REVIEW_VERDICTS",
    "UPSTREAM_REQUIRED_PREVIEW_VERDICT",
    "UPSTREAM_REQUIRED_PREVIEW_NEXT_GATE",
    "DRY_RUN_REVIEW_NEXT_REQUIRED_ACTION",
    "DRY_RUN_REVIEW_CURRENT_STAGE",
    "REVIEW_CRYPTO_D1_DRY_RUN_REVIEW_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_READY_HUMAN_RUN_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_FIX_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_PARKED",
    "NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_REJECTED",
    "NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT",
    "REQUIRED_REVIEW_FIELDS",
    "REVIEW_REQUIRED_TEXT_FIELDS",
    "REVIEW_REQUIRED_AFFIRMATIONS",
    "REVIEW_FORBIDDEN_ALLOW_FLAGS",
    "ALLOWED_REVIEW_MODES",
    "ALLOWED_REVIEW_SCOPES",
    "AUTOMATED_APPROVAL_MARKERS",
    "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "evaluate_crypto_d1_research_only_dry_run_review",
    "build_crypto_d1_research_only_dry_run_review_contract",
    "validate_crypto_d1_research_only_dry_run_review_contract",
    "render_crypto_d1_research_only_dry_run_review_contract_markdown",
]

REVIEW_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_research_only_dry_run_review_contract.v1"
)
DEFAULT_REVIEW_LABEL = (
    "Strategy Factory Crypto-D1 Research-Only Dry-Run Review Contract"
)
REVIEW_STATUS = (
    "READ_ONLY_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT"
)

REVIEW_STATE_ACTIVE = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT_ACTIVE"
)
REVIEW_STATE_BLOCKED = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT_BLOCKED"
)

REVIEW_VERDICT_READY = "DRY_RUN_REVIEW_READY"
REVIEW_VERDICT_NEEDS_MORE_INFO = "DRY_RUN_REVIEW_NEEDS_MORE_INFO"
REVIEW_VERDICT_REJECTED = "DRY_RUN_REVIEW_REJECTED"
REVIEW_VERDICT_PARKED = "DRY_RUN_REVIEW_PARKED"
REVIEW_VERDICT_AWAIT = (
    "AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT"
)

ALLOWED_REVIEW_VERDICTS: tuple[str, ...] = (
    REVIEW_VERDICT_READY,
    REVIEW_VERDICT_NEEDS_MORE_INFO,
    REVIEW_VERDICT_REJECTED,
    REVIEW_VERDICT_PARKED,
    REVIEW_VERDICT_AWAIT,
)

# The exact upstream Bundle 49 signal this bundle activates from.
UPSTREAM_REQUIRED_PREVIEW_VERDICT = _UPSTREAM_PREVIEW_VERDICT_READY
UPSTREAM_REQUIRED_PREVIEW_NEXT_GATE = _UPSTREAM_DRY_RUN_REVIEW_GATE

# Next action / stage as published by the mission-flow registry (via Bundle 49).
# This bundle FULFILLS that action on paper; it does not advance the registry.
DRY_RUN_REVIEW_NEXT_REQUIRED_ACTION = _PREVIEW_NEXT_REQUIRED_ACTION
DRY_RUN_REVIEW_CURRENT_STAGE = _PREVIEW_CURRENT_STAGE

# The conceptual decision this bundle fulfills once it is active.
REVIEW_CRYPTO_D1_DRY_RUN_REVIEW_REQUIRED = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_REQUIRED"
)

# Next-gate outcomes by verdict. A READY review is still only a paper readiness
# verdict; running the dry run itself is a separate, later, human step.
NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_READY_HUMAN_RUN_REQUIRED = (
    "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_READY_SEPARATE_HUMAN_RUN_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_FIX_REQUIRED = (
    "CRYPTO_D1_DRY_RUN_REVIEW_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_PARKED = (
    "CRYPTO_D1_DRY_RUN_REVIEW_PARKED"
)
NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_REJECTED = (
    "CRYPTO_D1_DRY_RUN_REVIEW_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT = (
    "AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-49).
REVIEW_SAFETY_POSTURE: dict[str, bool] = dict(_PREVIEW_SAFETY_POSTURE)

# Descriptive text fields a human operator records on a dry-run review packet.
REVIEW_REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
    "review_packet_id",
    "upstream_preview_id",
    "preview_contract_version",
    "review_scope",
    "review_mode",
    "reviewed_preview_inputs",
    "reviewed_preview_outputs",
    "reviewer_name_or_id",
    "next_step_boundary",
    "review_notes",
)

# Review affirmation flags the packet must carry (each affirmed True). The
# "reviewed_no_*" flags are positive confirmations that the reviewed preview did
# NOT do the named thing. A present-but-not-affirmed value is a request to admit
# or allow that thing -- a hard REJECTED. An absent value is a missing
# requirement (NEEDS_MORE_INFO).
REVIEW_REQUIRED_AFFIRMATIONS: tuple[str, ...] = (
    "reviewed_mock_inputs_only",
    "reviewed_static_contract_metadata_only",
    "reviewed_no_real_data_acquisition",
    "reviewed_no_data_fetch",
    "reviewed_no_data_inspection",
    "reviewed_no_dataset_loading",
    "reviewed_no_qa_run",
    "reviewed_no_baseline_run",
    "reviewed_no_backtest_run",
    "reviewed_no_simulation_run",
    "reviewed_no_trade_signal",
    "reviewed_no_paper_live",
    "reviewed_no_broker_exchange",
    "reviewed_no_order_capability",
    "reviewed_no_account_access",
    "reviewed_no_api_keys",
    "reviewed_no_automation_trigger",
    "reviewed_no_runtime_write",
    "reviewed_no_registry_write",
    "reviewed_no_dashboard_write",
    "explicit_human_review",
    "research_only_acknowledgement",
    "no_execution_acknowledgement",
)

# Every required True-flag. Present-but-not-affirmed -> REJECTED; absent ->
# NEEDS_MORE_INFO.
_REQUIRED_TRUE_FLAGS: tuple[str, ...] = REVIEW_REQUIRED_AFFIRMATIONS

# The full set of required dry-run review packet fields (33).
REQUIRED_REVIEW_FIELDS: tuple[str, ...] = (
    REVIEW_REQUIRED_TEXT_FIELDS + REVIEW_REQUIRED_AFFIRMATIONS
)

# Positive allow/grant flags a review must NOT request -- any truthy value forces
# a hard REJECTED (it tries to permit a real, dangerous capability or to actually
# execute the dry run / acquire data / produce a signal / validate market data).
REVIEW_FORBIDDEN_ALLOW_FLAGS: tuple[str, ...] = (
    "allow_real_data_acquisition",
    "real_data_acquisition_allowed",
    "approves_real_data_acquisition",
    "allow_data_fetch",
    "data_fetch_allowed",
    "approves_data_fetch",
    "allow_data_inspection",
    "data_inspection_allowed",
    "approves_data_inspection",
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
    "approves_trade_signal",
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
# REJECTED (the review tries to permit something outside research-only scope).
ALLOWED_REVIEW_MODES: tuple[str, ...] = (
    "research_only",
    "research-only",
)
ALLOWED_REVIEW_SCOPES: tuple[str, ...] = (
    "dry_run_review_only",
    "research_only_review",
    "review_only",
    "preview_review",
    "no_data_review",
    "offline_review",
    "mock_inputs_review",
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

# Review-phase blocked capabilities.
_REVIEW_BLOCKED_CAPABILITIES: tuple[str, ...] = (
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

_REVIEW_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 dry-run review packet is a paper placeholder describing how a "
    "human reviewed a research-only dry-run preview packet that uses mock "
    "inputs and static contract metadata only -- it reviews a paper preview "
    "only, runs nothing, acquires nothing, inspects nothing, and executes "
    "nothing."
)

_REVIEW_VERDICT_RATIONALE_PLACEHOLDER = (
    "Dry-run review verdict rationale is a paper placeholder for a "
    "human-recorded acceptance, deferral, or refusal and its supporting reason."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 research-only dry-run review decision contract "
    "template and is execution-free.",
    "It REVIEWS a paper dry-run preview packet; it does NOT run a dry run.",
    "It evaluates a paper review packet only and writes no report file.",
    "It writes no runtime state, acquires no data, inspects no data, and loads "
    "no dataset.",
    "A READY verdict means only that a human reviewed the preview packet as "
    "research-only, mock/static-metadata-only; it authorizes no data work and "
    "no dry-run execution.",
    "It connects to no exchange, broker, or live venue and uses no API keys.",
    "QA, baseline, backtest, simulation, paper, and live all stay blocked.",
    "It produces no trade signal and validates no market data.",
    "No crypto-d1 dataset, qa_report, manifest, checksum, or fees file is "
    "opened, inspected, loaded, or accessed.",
    "A human operator alone may record this review; no automated reviewer is "
    "accepted.",
    "Any READY verdict still requires a separate, later, human-run step that "
    "this template does not authorize.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must record a dry-run review verdict with a supporting "
    "rationale on paper.",
    "A human operator must confirm the reviewed preview is research-only and "
    "preview-only, uses mock inputs and static contract metadata only, and "
    "performed no data acquisition, fetch, inspection, dataset loading, QA, "
    "baseline, backtest, simulation, trade-signal production, market-data "
    "validation, paper/live, broker/exchange, order, account, API, automation, "
    "or runtime/registry/dashboard writes.",
    "A human operator must confirm the review packet matches the approved "
    "Bundle 49 dry-run preview decision exactly.",
    "A human operator must decide whether the reviewed research-only dry-run "
    "preview may actually be run later as a separate step.",
    "No automated step may proceed without human sign-off.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "crypto_d1_dry_run_preview_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "crypto_d1_research_only_dry_run_review_contract_active",
    "crypto_d1_research_only_dry_run_review_contract_state",
    "crypto_d1_research_only_dry_run_preview_contract_active",
    "crypto_d1_dry_run_preview_verdict",
    "crypto_d1_dry_run_preview_next_gate",
    "dry_run_review_required",
    "dry_run_review_next_required_action",
    "dry_run_review_current_stage",
    "asset_lane",
    "timeframe_lane",
    "review_packet_reference_placeholder",
    "dry_run_review_verdict",
    "dry_run_review_verdict_reasons",
    "evaluated_review_packet",
    "referenced_preview_packet",
    "allowed_dry_run_review_verdicts",
    "required_review_fields",
    "review_required_text_fields",
    "review_required_affirmations",
    "review_forbidden_allow_flags",
    "allowed_review_modes",
    "allowed_review_scopes",
    "automated_approval_markers",
    "dry_run_review_verdict_rationale_placeholder",
    "review_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
    "crypto_d1_research_only_dry_run_preview_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(REVIEW_SAFETY_POSTURE)


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
            "reviewed", "verified", "prohibited",
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
    """Return mismatch reasons where a present review field clearly disagrees
    with the approved Bundle 49 preview packet. Absent fields are not a
    mismatch; only present-but-conflicting values are a hard mismatch."""
    if not isinstance(ref_packet, dict) or not ref_packet:
        return ()

    reasons: list[str] = []
    pv = packet.get("upstream_preview_id")
    rv = ref_packet.get("preview_packet_id")
    if _present(pv) and _present(rv) and _scalar(pv) != _scalar(rv):
        reasons.append("mismatch:upstream_preview_id")
    return tuple(reasons)


def _reject_reasons(
    packet: dict[str, Any], ref_packet: dict[str, Any]
) -> tuple[str, ...]:
    """Return any hard REJECTED reasons: a permitted dangerous capability, an
    admitted/relaxed affirmation, a disallowed enum value, an automated
    reviewer, granted authority, or a clear mismatch with the approved preview
    decision."""
    reasons: list[str] = []

    for flag in REVIEW_FORBIDDEN_ALLOW_FLAGS:
        if _truthy(packet.get(flag)):
            reasons.append(f"forbidden_allow:{flag}")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag in packet and not _affirm(packet.get(flag)):
            reasons.append(f"affirmation_relaxed:{flag}")

    enum_pairs = (
        ("review_mode", ALLOWED_REVIEW_MODES),
        ("review_scope", ALLOWED_REVIEW_SCOPES),
    )
    for key, allowed in enum_pairs:
        value = packet.get(key)
        if _present(value) and _scalar(value) not in allowed:
            reasons.append(f"disallowed_value:{key}")

    for key in (
        "reviewer_type",
        "review_author_type",
        "review_method",
        "review_source",
        "authored_by_type",
        "reviewer_name_or_id",
    ):
        if _scalar(packet.get(key)) in AUTOMATED_APPROVAL_MARKERS:
            reasons.append(f"automated_reviewer:{key}")

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
            reasons.append("operator_parked_dry_run_review")
            break

    if _scalar(packet.get("operator_decision")) in park_values:
        reasons.append("operator_decision_parked")
    if _scalar(packet.get("decision")) in park_values:
        reasons.append("decision_parked")

    return tuple(reasons)


def _missing_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return unmet requirements for an otherwise-safe review packet."""
    missing: list[str] = []

    for key in REVIEW_REQUIRED_TEXT_FIELDS:
        if not _present(packet.get(key)):
            missing.append(f"{key}_required")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag not in packet:
            missing.append(f"{flag}_must_be_affirmed_true")

    return tuple(missing)


def evaluate_crypto_d1_research_only_dry_run_review(
    packet: Any,
    preview_ref_packet: Any = None,
) -> dict[str, Any]:
    """Return a deterministic verdict for a dry-run review packet against the
    approved Bundle 49 preview packet. Pure; no I/O, no mutation, no timestamp,
    no random id. Unknown/malformed inputs never raise. The verdict is one of
    DRY_RUN_REVIEW_READY, DRY_RUN_REVIEW_NEEDS_MORE_INFO,
    DRY_RUN_REVIEW_REJECTED, or DRY_RUN_REVIEW_PARKED. It evaluates the SHAPE of
    a paper review only and unlocks nothing. REJECTED (permits a dangerous
    capability / admits a relaxed affirmation / disallowed value /
    authority-granting / automated reviewer / mismatched) is checked before
    parking, and parking before completeness, so an unsafe review is rejected
    even when it would otherwise park or merely need more info."""
    p = packet if isinstance(packet, dict) else {}
    ref = preview_ref_packet if isinstance(preview_ref_packet, dict) else {}

    if not p:
        return {
            "verdict": REVIEW_VERDICT_NEEDS_MORE_INFO,
            "reasons": ("dry_run_review_packet_missing",),
        }

    rejected = _reject_reasons(p, ref)
    if rejected:
        return {
            "verdict": REVIEW_VERDICT_REJECTED,
            "reasons": rejected,
        }

    park = _park_reasons(p)
    if park:
        return {
            "verdict": REVIEW_VERDICT_PARKED,
            "reasons": park,
        }

    missing = _missing_reasons(p)
    if not missing:
        return {
            "verdict": REVIEW_VERDICT_READY,
            "reasons": (
                "research_only_dry_run_review_fully_specified_mock_static_"
                "only_and_matches_preview",
            ),
        }

    return {
        "verdict": REVIEW_VERDICT_NEEDS_MORE_INFO,
        "reasons": missing,
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == REVIEW_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = (
        safe.get("stage") == "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_ONLY"
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
        tuple(safe.get("allowed_dry_run_review_verdicts") or ())
        == ALLOWED_REVIEW_VERDICTS
    )
    fields_ok = (
        tuple(safe.get("required_review_fields") or ())
        == REQUIRED_REVIEW_FIELDS
    )
    text_fields_ok = (
        tuple(safe.get("review_required_text_fields") or ())
        == REVIEW_REQUIRED_TEXT_FIELDS
    )
    affirmations_ok = (
        tuple(safe.get("review_required_affirmations") or ())
        == REVIEW_REQUIRED_AFFIRMATIONS
    )
    forbidden_flags_ok = (
        tuple(safe.get("review_forbidden_allow_flags") or ())
        == REVIEW_FORBIDDEN_ALLOW_FLAGS
    )
    modes_ok = (
        tuple(safe.get("allowed_review_modes") or ())
        == ALLOWED_REVIEW_MODES
    )
    scopes_ok = (
        tuple(safe.get("allowed_review_scopes") or ())
        == ALLOWED_REVIEW_SCOPES
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
        safe.get("dry_run_review_verdict") in ALLOWED_REVIEW_VERDICTS
    )
    blocked_present_ok = (
        len(tuple(safe.get("review_blocked_capabilities") or ())) >= 1
    )
    notes_ok = len(tuple(safe.get("operator_notes") or ())) >= 1
    next_steps_ok = (
        len(tuple(safe.get("human_operator_required_next_steps") or ())) >= 1
    )

    collections_ok = (
        verdicts_ok
        and fields_ok
        and text_fields_ok
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
        "allowed_dry_run_review_verdicts_ok": verdicts_ok,
        "required_review_fields_ok": fields_ok,
        "review_required_text_fields_ok": text_fields_ok,
        "review_required_affirmations_ok": affirmations_ok,
        "review_forbidden_allow_flags_ok": forbidden_flags_ok,
        "allowed_review_modes_ok": modes_ok,
        "allowed_review_scopes_ok": scopes_ok,
        "automated_approval_markers_ok": markers_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "dry_run_review_verdict_value_ok": verdict_value_ok,
        "review_blocked_capabilities_present": blocked_present_ok,
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_research_only_dry_run_review_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 research-only dry-run
    review contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_research_only_dry_run_review_contract(
    dry_run_preview_contract: Any,
    dry_run_review_packet: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 research-only dry-run
    review contract template plus a paper verdict for a proposed dry-run review
    packet.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (crypto_d1_research_only_dry_run_review_contract_active=True) solely when the
    upstream Bundle 49 crypto-d1 research-only dry-run preview contract is active
    AND its dry_run_preview_verdict is DRY_RUN_PREVIEW_READY AND its next_gate is
    the Bundle 49 ready gate
    (CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_SEPARATE_HUMAN_RUN_REQUIRED).
    When inactive, the verdict is
    AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT regardless of the
    packet. Even when active and READY, every authorization field stays False --
    it evaluates the SHAPE of a paper review only, runs no dry run, acquires
    nothing, connects to nothing, approves no QA, no baseline, no backtest,
    produces no trade signal, validates no market data, writes no report file,
    writes no runtime state, names only placeholders, and grants nothing.
    Returned dicts are fresh."""
    upstream = (
        dry_run_preview_contract
        if isinstance(dry_run_preview_contract, dict)
        else {}
    )

    upstream_active = (
        upstream.get("crypto_d1_research_only_dry_run_preview_contract_active")
        is True
    )
    upstream_verdict = _field(upstream, "dry_run_preview_verdict")
    upstream_next = _field(upstream, "next_gate")
    verdict_ok = upstream_verdict == UPSTREAM_REQUIRED_PREVIEW_VERDICT
    gate_ok = upstream_next == UPSTREAM_REQUIRED_PREVIEW_NEXT_GATE

    contract_active = bool(upstream_active and verdict_ok and gate_ok)

    ref_packet_raw = upstream.get("evaluated_preview_packet")
    ref_packet = ref_packet_raw if isinstance(ref_packet_raw, dict) else {}

    if contract_active:
        evaluation = evaluate_crypto_d1_research_only_dry_run_review(
            dry_run_review_packet, ref_packet
        )
        verdict = evaluation["verdict"]
        reasons = tuple(evaluation["reasons"])
    else:
        verdict = REVIEW_VERDICT_AWAIT
        reasons = (
            "await_crypto_d1_research_only_dry_run_preview_contract",
        )

    state = (
        REVIEW_STATE_ACTIVE if contract_active else REVIEW_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = (
            NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT
        )
    elif verdict == REVIEW_VERDICT_READY:
        next_gate = (
            NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_READY_HUMAN_RUN_REQUIRED  # noqa: E501
        )
    elif verdict == REVIEW_VERDICT_NEEDS_MORE_INFO:
        next_gate = NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_FIX_REQUIRED
    elif verdict == REVIEW_VERDICT_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_PARKED
    else:
        next_gate = NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_REJECTED

    dry_run_review_required = (
        REVIEW_CRYPTO_D1_DRY_RUN_REVIEW_REQUIRED if contract_active else ""
    )

    echoed_packet = (
        dict(dry_run_review_packet)
        if isinstance(dry_run_review_packet, dict)
        else {}
    )
    referenced_packet = dict(ref_packet) if ref_packet else {}

    contract = {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "crypto_d1_dry_run_preview_schema_version": (
            DRY_RUN_PREVIEW_SCHEMA_VERSION
        ),
        "idea_id": _field(dry_run_preview_contract, "idea_id"),
        "title": _field(dry_run_preview_contract, "title"),
        "label": DEFAULT_REVIEW_LABEL,
        "status": REVIEW_STATUS,
        "stage": "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_ONLY",
        "mode": "RESEARCH_ONLY",
        "crypto_d1_research_only_dry_run_review_contract_active": (
            contract_active
        ),
        "crypto_d1_research_only_dry_run_review_contract_state": state,
        "crypto_d1_research_only_dry_run_preview_contract_active": bool(
            upstream_active
        ),
        "crypto_d1_dry_run_preview_verdict": upstream_verdict,
        "crypto_d1_dry_run_preview_next_gate": upstream_next,
        "dry_run_review_required": dry_run_review_required,
        "dry_run_review_next_required_action": (
            DRY_RUN_REVIEW_NEXT_REQUIRED_ACTION
        ),
        "dry_run_review_current_stage": DRY_RUN_REVIEW_CURRENT_STAGE,
        "asset_lane": _field(dry_run_preview_contract, "asset_lane"),
        "timeframe_lane": _field(
            dry_run_preview_contract, "timeframe_lane"
        ),
        "review_packet_reference_placeholder": (
            _REVIEW_REFERENCE_PLACEHOLDER
        ),
        "dry_run_review_verdict": verdict,
        "dry_run_review_verdict_reasons": reasons,
        "evaluated_review_packet": echoed_packet,
        "referenced_preview_packet": referenced_packet,
        "allowed_dry_run_review_verdicts": ALLOWED_REVIEW_VERDICTS,
        "required_review_fields": REQUIRED_REVIEW_FIELDS,
        "review_required_text_fields": REVIEW_REQUIRED_TEXT_FIELDS,
        "review_required_affirmations": REVIEW_REQUIRED_AFFIRMATIONS,
        "review_forbidden_allow_flags": REVIEW_FORBIDDEN_ALLOW_FLAGS,
        "allowed_review_modes": ALLOWED_REVIEW_MODES,
        "allowed_review_scopes": ALLOWED_REVIEW_SCOPES,
        "automated_approval_markers": AUTOMATED_APPROVAL_MARKERS,
        "dry_run_review_verdict_rationale_placeholder": (
            _REVIEW_VERDICT_RATIONALE_PLACEHOLDER
        ),
        "review_blocked_capabilities": _REVIEW_BLOCKED_CAPABILITIES,
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
        "crypto_d1_research_only_dry_run_preview_contract": (
            dry_run_preview_contract
            if isinstance(dry_run_preview_contract, dict)
            else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_crypto_d1_research_only_dry_run_review_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 research-only
    dry-run review contract template. Pure; writes no file. Informational
    only."""
    verdicts = contract.get("allowed_dry_run_review_verdicts") or ()
    fields = contract.get("required_review_fields") or ()
    text_fields = contract.get("review_required_text_fields") or ()
    affirmations = contract.get("review_required_affirmations") or ()
    forbidden_flags = contract.get("review_forbidden_allow_flags") or ()
    modes = contract.get("allowed_review_modes") or ()
    scopes = contract.get("allowed_review_scopes") or ()
    markers = contract.get("automated_approval_markers") or ()
    reasons = contract.get("dry_run_review_verdict_reasons") or ()
    blocked = contract.get("review_blocked_capabilities") or ()
    remaining_blocked = (
        contract.get("remaining_real_world_capabilities_blocked") or ()
    )
    next_steps = contract.get("human_operator_required_next_steps") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Crypto-D1 Research-Only Dry-Run Review Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a "
        "crypto-d1-research-only-dry-run-review-only, paper-only, no-dry-run, "
        "no-data-acquisition, no-data-fetch, no-data-inspection, "
        "no-dataset-loading, no-qa-run, no-baseline-run, no-backtest, "
        "no-simulation, no-trade-signal, no-market-data-validation, "
        "no-paper-live, no-broker-exchange, no-automation, and execution-free "
        "template -- it records only a paper dry-run review decision verdict, "
        "is not wired into any runtime state, writes no report file, acquires "
        "no data, inspects no data, loads no dataset, connects to no venue, "
        "names only placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Dry-run preview schema: "
        f"`{contract.get('crypto_d1_dry_run_preview_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 research-only dry-run review contract active: "
        f"{contract.get('crypto_d1_research_only_dry_run_review_contract_active', '')}"  # noqa: E501
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_research_only_dry_run_review_contract_state', '')}"  # noqa: E501
    )
    lines.append(
        "Dry-run review required: "
        f"{contract.get('dry_run_review_required', '')}"
    )
    lines.append(
        "Dry-run review next required action: "
        f"{contract.get('dry_run_review_next_required_action', '')}"
    )
    lines.append(
        "Dry-run review current stage: "
        f"{contract.get('dry_run_review_current_stage', '')}"
    )
    lines.append(f"Verdict: {contract.get('dry_run_review_verdict', '')}")
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Review Packet Reference")
    lines.append("")
    lines.append(
        "Review packet reference: "
        f"{contract.get('review_packet_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Dry-Run Review Verdict Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Dry-Run Review Verdicts")
    lines.append("")
    for x in verdicts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Review Fields")
    lines.append("")
    for x in fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Review Required Text Fields")
    lines.append("")
    for x in text_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Review Required Affirmations")
    lines.append("")
    for x in affirmations:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Review Forbidden Allow Flags")
    lines.append("")
    for x in forbidden_flags:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Review Modes")
    lines.append("")
    for x in modes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Review Scopes")
    lines.append("")
    for x in scopes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Automated Approval Markers")
    lines.append("")
    for x in markers:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Dry-Run Review Verdict Rationale")
    lines.append("")
    lines.append(
        "Dry-run review verdict rationale: "
        f"{contract.get('dry_run_review_verdict_rationale_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Review Blocked Capabilities")
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
        "- A human operator must confirm this dry-run review decision before "
        "any research-only dry-run preview is actually run as a separate step."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)

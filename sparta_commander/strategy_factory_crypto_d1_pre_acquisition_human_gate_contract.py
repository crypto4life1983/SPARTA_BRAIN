"""SPARTA Offline Strategy Factory - CRYPTO-D1 PRE-ACQUISITION HUMAN APPROVAL GATE.

Bundle 46 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only paper pre-acquisition human-approval gate contract
template* builder and evaluator: it consumes a Bundle 45 crypto-d1 OFFLINE
ACQUISITION PLAN contract and, only when that plan contract is active with
offline_acquisition_plan_verdict == APPROVED_OFFLINE_ACQUISITION_PLAN and
next_gate == CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED (the
concrete Bundle 45 signal that the next step is a pre-acquisition human approval
gate), evaluates a proposed human-approval packet on paper and returns a
deterministic verdict describing whether an explicit, human-only, research-only
sign-off has been recorded that matches the approved offline acquisition plan.

This module exists so that NO future acquisition step can ever become eligible
automatically. Reaching an active gate contract maps the upstream approved-plan
state to the conceptual gate
CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_REQUIRED. Any other upstream shape
(blocked, malformed, wrong stage, not approved, parked, rejected, needs-more-
info, or wrong gate) yields the AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT
verdict.

Reaching an active gate contract and a HUMAN_APPROVAL_READY verdict unlocks
NOTHING real. It acquires no data, connects to no exchange, broker, or live
venue, uses no API keys, approves no QA, no baseline, no real backtest, no
paper/live activity, and unlocks no real strategy intake. The deferred items
(qa_run, qa_pass_or_accepted_qa_warn, baseline_backtest_output) stay blocked and
deferred. A ready human approval only records, on paper, that a human operator
explicitly signed off on the exact offline plan; it moves only to a future,
separately-gated human-approved acquisition-execution contract.

It never runs Strategy Factory, never acquires data, never inspects, loads,
validates, transforms, or computes on real data, never inspects market data,
never runs QA, never produces a QA verdict, never runs a baseline, never
backtests, never simulates, never reaches for data, never connects to any
exchange, broker, or vendor, never opens or reads any crypto-d1 dataset file,
qa_report, manifest, checksum, freeze record, fees file, or baseline output,
and executes nothing. It opens no network, spawns no subprocess, writes no
file, reads no file, lists no directory, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision into any runtime
ledger. It records no timestamp, mints no random id, reads no environment, and
dynamically imports nothing.

Public API:
  - GATE_SCHEMA_VERSION
  - DEFAULT_GATE_LABEL
  - GATE_STATUS
  - GATE_SAFETY_POSTURE
  - GATE_STATE_ACTIVE
  - GATE_STATE_BLOCKED
  - GATE_VERDICT_READY
  - GATE_VERDICT_MISSING
  - GATE_VERDICT_INVALID
  - GATE_VERDICT_PARKED
  - GATE_VERDICT_AWAIT
  - ALLOWED_HUMAN_APPROVAL_VERDICTS
  - UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_VERDICT
  - UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_GATE
  - GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_REQUIRED
  - NEXT_GATE_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED
  - NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_PARKED
  - NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT
  - REQUIRED_HUMAN_APPROVAL_FIELDS
  - HUMAN_APPROVAL_REQUIRED_TEXT_FIELDS
  - HUMAN_APPROVAL_REQUIRED_AFFIRMATIONS
  - HUMAN_APPROVAL_FORBIDDEN_GRANT_FLAGS
  - AUTOMATED_APPROVAL_MARKERS
  - ALLOWED_ASSET_UNIVERSE
  - PARKED_MARKET_TYPES
  - ALLOWED_ACCESS_MODES
  - ALLOWED_OFFLINE_ACQUISITION_MODES
  - ALLOWED_OFFLINE_SOURCE_TYPES
  - REQUIRED_CANDLE_FIELDS
  - ALLOWED_TIMEFRAME
  - BLOCKED_EXECUTION_ITEMS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - evaluate_crypto_d1_pre_acquisition_human_approval(packet, approved_plan=None)
  - build_crypto_d1_pre_acquisition_human_gate_contract(offline_acquisition_plan_contract, human_approval_packet=None)
  - validate_crypto_d1_pre_acquisition_human_gate_contract(contract)
  - render_crypto_d1_pre_acquisition_human_gate_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_offline_acquisition_plan_contract import (  # noqa: E501
    PLAN_SCHEMA_VERSION,
    PLAN_SAFETY_POSTURE,
    PLAN_VERDICT_APPROVED as _OFFLINE_ACQUISITION_PLAN_VERDICT_APPROVED,
    NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED as _OFFLINE_ACQUISITION_PLAN_APPROVED_GATE,  # noqa: E501
    ALLOWED_ASSET_UNIVERSE,
    PARKED_MARKET_TYPES,
    ALLOWED_ACCESS_MODES,
    ALLOWED_OFFLINE_ACQUISITION_MODES,
    ALLOWED_OFFLINE_SOURCE_TYPES,
    REQUIRED_CANDLE_FIELDS,
    ALLOWED_TIMEFRAME,
    BLOCKED_EXECUTION_ITEMS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
)

__all__ = [
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
]

GATE_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_pre_acquisition_human_gate_contract.v1"
)
DEFAULT_GATE_LABEL = (
    "Strategy Factory Crypto-D1 Pre-Acquisition Human Approval Gate Contract"
)
GATE_STATUS = (
    "READ_ONLY_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_CONTRACT"
)

GATE_STATE_ACTIVE = (
    "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_CONTRACT_ACTIVE"
)
GATE_STATE_BLOCKED = (
    "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_CONTRACT_BLOCKED"
)

GATE_VERDICT_READY = "HUMAN_APPROVAL_READY"
GATE_VERDICT_MISSING = "HUMAN_APPROVAL_MISSING"
GATE_VERDICT_INVALID = "HUMAN_APPROVAL_INVALID"
GATE_VERDICT_PARKED = "HUMAN_APPROVAL_PARKED"
GATE_VERDICT_AWAIT = "AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT"

ALLOWED_HUMAN_APPROVAL_VERDICTS: tuple[str, ...] = (
    GATE_VERDICT_READY,
    GATE_VERDICT_MISSING,
    GATE_VERDICT_INVALID,
    GATE_VERDICT_PARKED,
    GATE_VERDICT_AWAIT,
)

# The exact upstream Bundle 45 signal this bundle activates from.
UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_VERDICT = (
    _OFFLINE_ACQUISITION_PLAN_VERDICT_APPROVED
)
UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_GATE = (
    _OFFLINE_ACQUISITION_PLAN_APPROVED_GATE
)

# The conceptual gate this bundle fulfills once it is active.
GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_REQUIRED = (
    "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_REQUIRED"
)

NEXT_GATE_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED = (  # noqa: E501
    "CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_FIX_REQUIRED = (
    "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_PARKED = (
    "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_PARKED"
)
NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_REJECTED = (
    "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT = (
    "AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-45).
GATE_SAFETY_POSTURE: dict[str, bool] = dict(PLAN_SAFETY_POSTURE)

# Descriptive text fields a human operator records on an approval packet.
HUMAN_APPROVAL_REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
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

# Affirmation flags an operator must explicitly affirm True to approve. A
# present-but-not-affirmed value forces a hard INVALID (it asks to disable a
# safety guarantee); an absent value is a missing-required (HUMAN_APPROVAL_
# MISSING).
HUMAN_APPROVAL_REQUIRED_AFFIRMATIONS: tuple[str, ...] = (
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

# The full set of required approval-packet fields (instruction order).
REQUIRED_HUMAN_APPROVAL_FIELDS: tuple[str, ...] = (
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

# Positive grant flags an approval must NOT request -- any truthy value forces a
# hard INVALID. These represent an approval that tries to grant real authority.
HUMAN_APPROVAL_FORBIDDEN_GRANT_FLAGS: tuple[str, ...] = (
    "automated_approval",
    "automation_approved",
    "auto_approved",
    "machine_approved",
    "bot_approved",
    "live_fetch_approved",
    "live_fetch_authorized",
    "api_key_approved",
    "api_key_authorized",
    "account_access_approved",
    "order_capability_approved",
    "order_authorized",
    "broker_exchange_approved",
    "exchange_authorized",
    "qa_approved",
    "qa_authorized",
    "backtest_approved",
    "backtest_authorized",
    "paper_trading_approved",
    "live_trading_approved",
    "runtime_write_approved",
    "registry_write_approved",
    "dashboard_write_approved",
    "execution_authorized",
)

# Identity / method markers that indicate a non-human (automated) approver.
AUTOMATED_APPROVAL_MARKERS: tuple[str, ...] = (
    "automated",
    "automation",
    "auto",
    "auto_approve",
    "autopilot",
    "bot",
    "robot",
    "script",
    "machine",
    "cron",
    "scheduler",
    "scheduled",
    "daemon",
    "system",
    "agent",
    "llm",
    "ai",
)

# Pre-acquisition-gate-specific blocked capabilities (this phase only).
_GATE_BLOCKED_CAPABILITIES: tuple[str, ...] = (
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
    "auto_approval",
    "approval_ledger_write",
)

_AUTH_FLAGS: tuple[str, ...] = (
    "approved_for_research",
    "execution_authorized",
    "paper_trading_authorized",
    "live_trading_authorized",
    "data_fetch_authorized",
    "backtest_authorized",
    "promotion_authorized",
)

_GATE_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 human-approval packet is a paper placeholder for a "
    "human-recorded, explicit, research-only pre-acquisition sign-off on an "
    "exact offline acquisition plan."
)

_GATE_VERDICT_RATIONALE_PLACEHOLDER = (
    "Human-approval verdict rationale is a paper placeholder for a "
    "human-recorded acceptance, deferral, or refusal and its supporting "
    "reason."
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 pre-acquisition human approval gate contract template "
    "and is execution-free.",
    "It evaluates a paper human-approval packet only and writes no report "
    "file.",
    "It writes no runtime state, acquires no data, and inspects no data.",
    "It approves no real data acquisition and no live venue access.",
    "A ready human approval only records a human sign-off on paper.",
    "It connects to no exchange, broker, or live venue and uses no API keys.",
    "The deferred items stay blocked: qa, qa acceptance, and baseline output.",
    "No crypto-d1 dataset, qa_report, manifest, checksum, freeze record, or "
    "fees file is opened, inspected, or accessed.",
    "A human operator alone may record this approval; no automated approver is "
    "accepted.",
    "No automated step may proceed without human sign-off.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must record a human-approval verdict with a supporting "
    "rationale on paper.",
    "A human operator must confirm no live API, exchange, broker, account, or "
    "key dependency is present.",
    "A human operator must confirm the approval matches the approved offline "
    "acquisition plan exactly.",
    "A human operator must decide whether a later human-approved "
    "acquisition-execution contract may be drafted.",
    "No automated step may proceed without human sign-off.",
)

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "crypto_d1_offline_acquisition_plan_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "crypto_d1_pre_acquisition_human_gate_contract_active",
    "crypto_d1_pre_acquisition_human_gate_contract_state",
    "crypto_d1_offline_acquisition_plan_contract_active",
    "crypto_d1_offline_acquisition_plan_verdict",
    "crypto_d1_offline_acquisition_plan_next_gate",
    "pre_acquisition_human_approval_gate_required",
    "asset_lane",
    "timeframe_lane",
    "human_approval_packet_reference_placeholder",
    "human_approval_verdict",
    "human_approval_verdict_reasons",
    "evaluated_human_approval_packet",
    "referenced_offline_acquisition_plan",
    "allowed_human_approval_verdicts",
    "required_human_approval_fields",
    "human_approval_required_text_fields",
    "human_approval_required_affirmations",
    "human_approval_forbidden_grant_flags",
    "automated_approval_markers",
    "allowed_asset_universe",
    "parked_market_types",
    "allowed_access_modes",
    "allowed_offline_acquisition_modes",
    "allowed_offline_source_types",
    "required_candle_fields",
    "allowed_timeframe",
    "human_approval_verdict_rationale_placeholder",
    "blocked_execution_items",
    "pre_acquisition_human_gate_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
    "crypto_d1_offline_acquisition_plan_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(GATE_SAFETY_POSTURE)


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
    """Deterministic affirmation test for required affirmation flags."""
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in (
            "true", "yes", "required", "y", "1", "confirmed", "acknowledged",
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


def _normalize_tokens(value: Any) -> tuple[str, ...]:
    """Normalize a symbols/assets value to an uppercase token tuple (sorted)."""
    if isinstance(value, str):
        parts = [a.strip().upper() for a in value.replace(",", " ").split()]
    elif isinstance(value, (list, tuple)):
        parts = [_as_text(a).strip().upper() for a in value]
    else:
        return ()
    return tuple(sorted(a for a in parts if a))


def _scalar(value: Any) -> str:
    """Normalize a scalar text value for comparison."""
    return _as_text(value).strip().lower()


def _mismatch_reasons(
    packet: dict[str, Any], ref_plan: dict[str, Any]
) -> tuple[str, ...]:
    """Return mismatch reasons where a present packet field clearly disagrees
    with the approved offline acquisition plan. Absent packet fields are not a
    mismatch (they are handled as missing); only present-but-conflicting values
    are a hard mismatch."""
    if not isinstance(ref_plan, dict) or not ref_plan:
        return ()

    reasons: list[str] = []

    scalar_pairs = (
        ("approved_timeframe", "timeframe"),
        ("approved_market_type", "market_type"),
        ("approved_acquisition_mode", "acquisition_mode"),
        ("approved_source_specification_id", "source_specification_id"),
        ("approved_plan_id", "plan_name"),
    )
    for pkey, rkey in scalar_pairs:
        pv = packet.get(pkey)
        rv = ref_plan.get(rkey)
        if _present(pv) and _present(rv) and _scalar(pv) != _scalar(rv):
            reasons.append(f"mismatch:{pkey}")

    set_pairs = (
        ("approved_symbols", "symbols"),
        ("approved_assets", "asset_universe"),
    )
    for pkey, rkey in set_pairs:
        pv = packet.get(pkey)
        rv = ref_plan.get(rkey)
        if _present(pv) and _present(rv):
            if _normalize_tokens(pv) != _normalize_tokens(rv):
                reasons.append(f"mismatch:{pkey}")

    window = packet.get("approved_coverage_window")
    start = ref_plan.get("coverage_start")
    end = ref_plan.get("coverage_end")
    if _present(window) and (_present(start) or _present(end)):
        wtext = _as_text(window)
        if _present(start) and _as_text(start) not in wtext:
            reasons.append("mismatch:approved_coverage_window")
        elif _present(end) and _as_text(end) not in wtext:
            reasons.append("mismatch:approved_coverage_window")

    return tuple(reasons)


def _invalid_reasons(
    packet: dict[str, Any], ref_plan: dict[str, Any]
) -> tuple[str, ...]:
    """Return any hard INVALID reasons for an approval packet: automated
    approval, granted real authority, disabled safety affirmations, or a clear
    mismatch with the approved plan."""
    reasons: list[str] = []

    for flag in HUMAN_APPROVAL_FORBIDDEN_GRANT_FLAGS:
        if _truthy(packet.get(flag)):
            reasons.append(f"forbidden_grant:{flag}")

    # A required affirmation that is present but NOT affirmed is a request to
    # disable a safety guarantee -- a hard INVALID.
    for flag in HUMAN_APPROVAL_REQUIRED_AFFIRMATIONS:
        if flag in packet and not _affirm(packet.get(flag)):
            reasons.append(f"affirmation_not_affirmed:{flag}")

    for key in (
        "approval_method",
        "approval_mode",
        "approval_source",
        "approved_by_type",
        "approver_type",
        "operator_name_or_id",
    ):
        if _scalar(packet.get(key)) in AUTOMATED_APPROVAL_MARKERS:
            reasons.append(f"automated_approver:{key}")

    for key in ("grants_capabilities", "authorizes", "granted_capabilities"):
        listed = packet.get(key)
        if isinstance(listed, (list, tuple)) and len(listed) > 0:
            reasons.append(f"grants_listed:{key}")

    reasons.extend(_mismatch_reasons(packet, ref_plan))

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
            reasons.append("operator_parked_acquisition_plan")
            break

    if _scalar(packet.get("operator_decision")) in park_values:
        reasons.append("operator_decision_parked")
    if _scalar(packet.get("decision")) in park_values:
        reasons.append("decision_parked")
    if _scalar(packet.get("approval_scope")) in park_values:
        reasons.append("approval_scope_parked")

    return tuple(reasons)


def _missing_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return unmet approval requirements for an otherwise-safe packet."""
    missing: list[str] = []

    for key in HUMAN_APPROVAL_REQUIRED_TEXT_FIELDS:
        if not _present(packet.get(key)):
            missing.append(f"{key}_required")

    for flag in HUMAN_APPROVAL_REQUIRED_AFFIRMATIONS:
        if flag not in packet:
            missing.append(f"{flag}_must_be_affirmed_true")

    return tuple(missing)


def evaluate_crypto_d1_pre_acquisition_human_approval(
    packet: Any,
    approved_plan: Any = None,
) -> dict[str, Any]:
    """Return a deterministic verdict for a human-approval packet against the
    approved offline acquisition plan. Pure; no I/O, no mutation, no timestamp,
    no random id. Unknown/malformed inputs never raise. The verdict is one of
    HUMAN_APPROVAL_READY, HUMAN_APPROVAL_MISSING, HUMAN_APPROVAL_INVALID, or
    HUMAN_APPROVAL_PARKED. It evaluates the SHAPE of a paper approval only and
    unlocks nothing. INVALID (unsafe / authority-granting / mismatched) is
    checked before parking, and parking before completeness, so an unsafe packet
    is rejected even when it would otherwise park or merely need more info."""
    p = packet if isinstance(packet, dict) else {}
    ref = approved_plan if isinstance(approved_plan, dict) else {}

    if not p:
        return {
            "verdict": GATE_VERDICT_MISSING,
            "reasons": ("human_approval_packet_missing",),
        }

    invalid = _invalid_reasons(p, ref)
    if invalid:
        return {
            "verdict": GATE_VERDICT_INVALID,
            "reasons": invalid,
        }

    park = _park_reasons(p)
    if park:
        return {
            "verdict": GATE_VERDICT_PARKED,
            "reasons": park,
        }

    missing = _missing_reasons(p)
    if not missing:
        return {
            "verdict": GATE_VERDICT_READY,
            "reasons": (
                "explicit_human_only_approval_matches_plan_research_only_"
                "boundary_affirmed",
            ),
        }

    return {
        "verdict": GATE_VERDICT_MISSING,
        "reasons": missing,
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == GATE_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in (
        "GATE_ONLY",
        "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_ONLY",
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
        tuple(safe.get("allowed_human_approval_verdicts") or ())
        == ALLOWED_HUMAN_APPROVAL_VERDICTS
    )
    fields_ok = (
        tuple(safe.get("required_human_approval_fields") or ())
        == REQUIRED_HUMAN_APPROVAL_FIELDS
    )
    text_fields_ok = (
        tuple(safe.get("human_approval_required_text_fields") or ())
        == HUMAN_APPROVAL_REQUIRED_TEXT_FIELDS
    )
    affirmations_ok = (
        tuple(safe.get("human_approval_required_affirmations") or ())
        == HUMAN_APPROVAL_REQUIRED_AFFIRMATIONS
    )
    forbidden_flags_ok = (
        tuple(safe.get("human_approval_forbidden_grant_flags") or ())
        == HUMAN_APPROVAL_FORBIDDEN_GRANT_FLAGS
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
    modes_ok = (
        tuple(safe.get("allowed_offline_acquisition_modes") or ())
        == ALLOWED_OFFLINE_ACQUISITION_MODES
    )
    source_types_ok = (
        tuple(safe.get("allowed_offline_source_types") or ())
        == ALLOWED_OFFLINE_SOURCE_TYPES
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
        safe.get("human_approval_verdict") in ALLOWED_HUMAN_APPROVAL_VERDICTS
    )
    gate_blocked_ok = (
        len(tuple(
            safe.get("pre_acquisition_human_gate_blocked_capabilities") or ()
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
        and affirmations_ok
        and forbidden_flags_ok
        and markers_ok
        and assets_ok
        and candle_ok
        and timeframe_ok
        and modes_ok
        and source_types_ok
        and blocked_execution_ok
        and remaining_blocked_ok
        and verdict_value_ok
        and gate_blocked_ok
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
        "allowed_human_approval_verdicts_ok": verdicts_ok,
        "required_human_approval_fields_ok": fields_ok,
        "human_approval_required_text_fields_ok": text_fields_ok,
        "human_approval_required_affirmations_ok": affirmations_ok,
        "human_approval_forbidden_grant_flags_ok": forbidden_flags_ok,
        "automated_approval_markers_ok": markers_ok,
        "allowed_asset_universe_ok": assets_ok,
        "required_candle_fields_ok": candle_ok,
        "allowed_timeframe_ok": timeframe_ok,
        "allowed_offline_acquisition_modes_ok": modes_ok,
        "allowed_offline_source_types_ok": source_types_ok,
        "blocked_execution_items_ok": blocked_execution_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "human_approval_verdict_value_ok": verdict_value_ok,
        "pre_acquisition_human_gate_blocked_capabilities_present": (
            gate_blocked_ok
        ),
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_pre_acquisition_human_gate_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 pre-acquisition human
    approval gate contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_pre_acquisition_human_gate_contract(
    offline_acquisition_plan_contract: Any,
    human_approval_packet: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 pre-acquisition human
    approval gate contract template plus a paper verdict for a proposed
    human-approval packet.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (crypto_d1_pre_acquisition_human_gate_contract_active=True) solely when the
    upstream Bundle 45 crypto-d1 offline acquisition plan contract is active AND
    its offline_acquisition_plan_verdict is APPROVED_OFFLINE_ACQUISITION_PLAN AND
    its next_gate is the Bundle 45 approved gate
    (CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED -- the
    concrete signal a pre-acquisition human approval gate is required next). When
    inactive, the verdict is AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT
    regardless of the packet. Even when active and READY, every authorization
    field stays False -- it evaluates the SHAPE of a paper approval only,
    acquires nothing, connects to nothing, approves no QA, no baseline, and no
    backtest, writes no report file, writes no runtime state, names only
    placeholders, and grants nothing. Returned dicts are fresh."""
    op = (
        offline_acquisition_plan_contract
        if isinstance(offline_acquisition_plan_contract, dict)
        else {}
    )

    op_active = (
        op.get("crypto_d1_offline_acquisition_plan_contract_active") is True
    )
    op_verdict = _field(op, "offline_acquisition_plan_verdict")
    op_next_gate = _field(op, "next_gate")
    verdict_ok = (
        op_verdict == UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_VERDICT
    )
    gate_ok = op_next_gate == UPSTREAM_REQUIRED_OFFLINE_ACQUISITION_PLAN_GATE

    contract_active = bool(op_active and verdict_ok and gate_ok)

    ref_plan_raw = op.get("evaluated_offline_acquisition_plan")
    ref_plan = ref_plan_raw if isinstance(ref_plan_raw, dict) else {}

    if contract_active:
        evaluation = evaluate_crypto_d1_pre_acquisition_human_approval(
            human_approval_packet, ref_plan
        )
        verdict = evaluation["verdict"]
        reasons = tuple(evaluation["reasons"])
    else:
        verdict = GATE_VERDICT_AWAIT
        reasons = ("await_crypto_d1_offline_acquisition_plan_contract_gate",)

    state = GATE_STATE_ACTIVE if contract_active else GATE_STATE_BLOCKED

    if not contract_active:
        next_gate = NEXT_GATE_AWAIT_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT
    elif verdict == GATE_VERDICT_READY:
        next_gate = (
            NEXT_GATE_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_CONTRACT_REQUIRED  # noqa: E501
        )
    elif verdict == GATE_VERDICT_MISSING:
        next_gate = (
            NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_FIX_REQUIRED
        )
    elif verdict == GATE_VERDICT_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_PARKED
    else:
        next_gate = NEXT_GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_REJECTED

    pre_acquisition_gate_required = (
        GATE_CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_REQUIRED
        if contract_active
        else ""
    )

    echoed_packet = (
        dict(human_approval_packet)
        if isinstance(human_approval_packet, dict)
        else {}
    )
    referenced_plan = dict(ref_plan) if ref_plan else {}

    contract = {
        "schema_version": GATE_SCHEMA_VERSION,
        "crypto_d1_offline_acquisition_plan_schema_version": PLAN_SCHEMA_VERSION,
        "idea_id": _field(offline_acquisition_plan_contract, "idea_id"),
        "title": _field(offline_acquisition_plan_contract, "title"),
        "label": DEFAULT_GATE_LABEL,
        "status": GATE_STATUS,
        "stage": "CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_ONLY",
        "mode": "RESEARCH_ONLY",
        "crypto_d1_pre_acquisition_human_gate_contract_active": (
            contract_active
        ),
        "crypto_d1_pre_acquisition_human_gate_contract_state": state,
        "crypto_d1_offline_acquisition_plan_contract_active": bool(op_active),
        "crypto_d1_offline_acquisition_plan_verdict": op_verdict,
        "crypto_d1_offline_acquisition_plan_next_gate": op_next_gate,
        "pre_acquisition_human_approval_gate_required": (
            pre_acquisition_gate_required
        ),
        "asset_lane": _field(offline_acquisition_plan_contract, "asset_lane"),
        "timeframe_lane": _field(
            offline_acquisition_plan_contract, "timeframe_lane"
        ),
        "human_approval_packet_reference_placeholder": (
            _GATE_REFERENCE_PLACEHOLDER
        ),
        "human_approval_verdict": verdict,
        "human_approval_verdict_reasons": reasons,
        "evaluated_human_approval_packet": echoed_packet,
        "referenced_offline_acquisition_plan": referenced_plan,
        "allowed_human_approval_verdicts": ALLOWED_HUMAN_APPROVAL_VERDICTS,
        "required_human_approval_fields": REQUIRED_HUMAN_APPROVAL_FIELDS,
        "human_approval_required_text_fields": (
            HUMAN_APPROVAL_REQUIRED_TEXT_FIELDS
        ),
        "human_approval_required_affirmations": (
            HUMAN_APPROVAL_REQUIRED_AFFIRMATIONS
        ),
        "human_approval_forbidden_grant_flags": (
            HUMAN_APPROVAL_FORBIDDEN_GRANT_FLAGS
        ),
        "automated_approval_markers": AUTOMATED_APPROVAL_MARKERS,
        "allowed_asset_universe": ALLOWED_ASSET_UNIVERSE,
        "parked_market_types": PARKED_MARKET_TYPES,
        "allowed_access_modes": ALLOWED_ACCESS_MODES,
        "allowed_offline_acquisition_modes": ALLOWED_OFFLINE_ACQUISITION_MODES,
        "allowed_offline_source_types": ALLOWED_OFFLINE_SOURCE_TYPES,
        "required_candle_fields": REQUIRED_CANDLE_FIELDS,
        "allowed_timeframe": ALLOWED_TIMEFRAME,
        "human_approval_verdict_rationale_placeholder": (
            _GATE_VERDICT_RATIONALE_PLACEHOLDER
        ),
        "blocked_execution_items": BLOCKED_EXECUTION_ITEMS,
        "pre_acquisition_human_gate_blocked_capabilities": (
            _GATE_BLOCKED_CAPABILITIES
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
        "crypto_d1_offline_acquisition_plan_contract": (
            offline_acquisition_plan_contract
            if isinstance(offline_acquisition_plan_contract, dict)
            else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_crypto_d1_pre_acquisition_human_gate_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 pre-acquisition
    human approval gate contract template. Pure; writes no file. Informational
    only."""
    verdicts = contract.get("allowed_human_approval_verdicts") or ()
    fields = contract.get("required_human_approval_fields") or ()
    affirmations = contract.get("human_approval_required_affirmations") or ()
    forbidden_flags = contract.get("human_approval_forbidden_grant_flags") or ()
    markers = contract.get("automated_approval_markers") or ()
    assets = contract.get("allowed_asset_universe") or ()
    parked = contract.get("parked_market_types") or ()
    access_modes = contract.get("allowed_access_modes") or ()
    modes = contract.get("allowed_offline_acquisition_modes") or ()
    source_types = contract.get("allowed_offline_source_types") or ()
    candle_fields = contract.get("required_candle_fields") or ()
    timeframe = contract.get("allowed_timeframe") or ()
    reasons = contract.get("human_approval_verdict_reasons") or ()
    blocked_execution = contract.get("blocked_execution_items") or ()
    gate_blocked = (
        contract.get("pre_acquisition_human_gate_blocked_capabilities") or ()
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
        "# Strategy Factory Crypto-D1 Pre-Acquisition Human Approval Gate "
        "Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a "
        "crypto-d1-pre-acquisition-human-approval-gate-only, paper-only, "
        "human-approval-only, no-live-api, no-data-acquisition, no-qa-run, "
        "no-baseline-run, no-data-inspection, no-real-strategy-intake-yet, "
        "research-only, and execution-free template -- it records only a paper "
        "human-approval verdict, is not wired into any runtime state, writes no "
        "report file, acquires no data, inspects no data, connects to no venue, "
        "names only placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Offline acquisition plan schema: "
        f"`{contract.get('crypto_d1_offline_acquisition_plan_schema_version', '')}`"  # noqa: E501
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: CRYPTO_D1_PRE_ACQUISITION_HUMAN_APPROVAL_GATE_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 pre-acquisition human approval gate contract active: "
        f"{contract.get('crypto_d1_pre_acquisition_human_gate_contract_active', '')}"  # noqa: E501
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_pre_acquisition_human_gate_contract_state', '')}"  # noqa: E501
    )
    lines.append(
        "Pre-acquisition human approval gate required: "
        f"{contract.get('pre_acquisition_human_approval_gate_required', '')}"
    )
    lines.append(
        f"Verdict: {contract.get('human_approval_verdict', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Human Approval Packet Reference")
    lines.append("")
    lines.append(
        "Human approval packet reference: "
        f"{contract.get('human_approval_packet_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Human Approval Verdict Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Human Approval Verdicts")
    lines.append("")
    for x in verdicts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Human Approval Fields")
    lines.append("")
    for x in fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Human Approval Required Affirmations")
    lines.append("")
    for x in affirmations:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Human Approval Forbidden Grant Flags")
    lines.append("")
    for x in forbidden_flags:
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
    lines.append("## Parked Market Types")
    lines.append("")
    for x in parked:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Access Modes")
    lines.append("")
    for x in access_modes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Offline Acquisition Modes")
    lines.append("")
    for x in modes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Offline Source Types")
    lines.append("")
    for x in source_types:
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
    lines.append("## Human Approval Verdict Rationale")
    lines.append("")
    lines.append(
        "Human approval verdict rationale: "
        f"{contract.get('human_approval_verdict_rationale_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Blocked Execution Items")
    lines.append("")
    for x in blocked_execution:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Pre-Acquisition Human Gate Blocked Capabilities")
    lines.append("")
    for cap in gate_blocked:
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
        "- A human operator must confirm the explicit human approval before "
        "any acquisition-execution contract is drafted."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)

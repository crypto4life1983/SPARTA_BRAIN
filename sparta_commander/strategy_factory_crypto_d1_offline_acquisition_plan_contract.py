"""SPARTA Offline Strategy Factory - CRYPTO-D1 OFFLINE ACQUISITION PLAN CONTRACT.

Bundle 45 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only paper offline-acquisition-plan contract template* builder
and evaluator: it consumes a Bundle 44 crypto-d1 source SPECIFICATION contract
and, only when that specification contract is active with
source_specification_verdict == APPROVED_SOURCE_SPECIFICATION and next_gate ==
CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED (the concrete Bundle 44
signal that an offline acquisition-plan contract is required next), evaluates a
proposed exact OFFLINE acquisition plan on paper and returns a deterministic
verdict describing whether the offline plan is complete, safe, reproducible, and
ready for a future, human-approved acquisition-execution plan.

Note on the upstream gate: Bundle 44's APPROVED_SOURCE_SPECIFICATION verdict
emits the next_gate string CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED.
Bundle 45 treats that exact active+approved state as the "offline acquisition
plan contract required" condition. Any other upstream shape (blocked, malformed,
wrong stage, not approved, parked, needs-more-info, rejected, or wrong gate)
yields the AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT verdict.

Reaching an active acquisition-plan contract and an
APPROVED_OFFLINE_ACQUISITION_PLAN verdict unlocks NOTHING real. It acquires no
data, connects to no exchange, broker, or live venue, uses no API keys, approves
no QA, no baseline, no real backtest, and unlocks no real strategy intake. The
deferred execution items (qa_run, qa_pass_or_accepted_qa_warn,
baseline_backtest_output) stay blocked and deferred. An approved plan only
describes, on paper, an offline, reproducible, plan-only path; it moves only to a
future acquisition-execution plan contract.

It never runs Strategy Factory, never acquires data, never inspects, loads,
validates, transforms, or computes on real data, never inspects market data,
never runs QA, never produces a QA verdict, never runs a baseline, never
backtests, never simulates, never reaches for data, never connects to any
exchange, broker, or vendor, never opens or reads any crypto-d1 dataset file,
qa_report, manifest, checksum, freeze record, fees file, or baseline output,
and executes nothing. It opens no network, spawns no subprocess, writes no
file, reads no file, lists no directory, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, reads no environment, and dynamically imports
nothing.

Public API:
  - PLAN_SCHEMA_VERSION
  - DEFAULT_PLAN_LABEL
  - PLAN_STATUS
  - PLAN_SAFETY_POSTURE
  - PLAN_STATE_ACTIVE
  - PLAN_STATE_BLOCKED
  - PLAN_VERDICT_APPROVED
  - PLAN_VERDICT_NEEDS_MORE_INFO
  - PLAN_VERDICT_PARKED
  - PLAN_VERDICT_REJECTED
  - PLAN_VERDICT_AWAIT
  - ALLOWED_PLAN_VERDICTS
  - UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_VERDICT
  - UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_GATE
  - NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED
  - NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_PARKED
  - NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT
  - REQUIRED_PLAN_FIELDS
  - PLAN_NEGATIVE_SAFETY_FLAGS
  - PLAN_FORBIDDEN_CAPABILITY_FLAGS
  - ALLOWED_ASSET_UNIVERSE
  - PARKED_MARKET_TYPES
  - ALLOWED_ACCESS_MODES
  - ALLOWED_OFFLINE_ACQUISITION_MODES
  - ALLOWED_OFFLINE_SOURCE_TYPES
  - REQUIRED_CANDLE_FIELDS
  - ALLOWED_TIMEFRAME
  - BLOCKED_EXECUTION_ITEMS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - evaluate_crypto_d1_offline_acquisition_plan(plan)
  - build_crypto_d1_offline_acquisition_plan_contract(source_specification_contract, offline_acquisition_plan=None)
  - validate_crypto_d1_offline_acquisition_plan_contract(contract)
  - render_crypto_d1_offline_acquisition_plan_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_source_specification_contract import (  # noqa: E501
    SPEC_SCHEMA_VERSION,
    SPEC_SAFETY_POSTURE,
    SPEC_VERDICT_APPROVED as _SOURCE_SPECIFICATION_VERDICT_APPROVED,
    NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED as _SOURCE_SPECIFICATION_APPROVED_GATE,  # noqa: E501
    ALLOWED_ASSET_UNIVERSE,
    PARKED_MARKET_TYPES,
    ALLOWED_ACCESS_MODES,
    REQUIRED_CANDLE_FIELDS,
    ALLOWED_TIMEFRAME,
    BLOCKED_EXECUTION_ITEMS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
)

__all__ = [
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
    "NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED",
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
]

PLAN_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_offline_acquisition_plan_contract.v1"
)
DEFAULT_PLAN_LABEL = (
    "Strategy Factory Crypto-D1 Offline Acquisition Plan Contract"
)
PLAN_STATUS = "READ_ONLY_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT"

PLAN_STATE_ACTIVE = "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT_ACTIVE"
PLAN_STATE_BLOCKED = "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_CONTRACT_BLOCKED"

PLAN_VERDICT_APPROVED = "APPROVED_OFFLINE_ACQUISITION_PLAN"
PLAN_VERDICT_NEEDS_MORE_INFO = "NEEDS_MORE_INFO"
PLAN_VERDICT_PARKED = "PARKED_OFFLINE_ACQUISITION_PLAN"
PLAN_VERDICT_REJECTED = "REJECTED_OFFLINE_ACQUISITION_PLAN"
PLAN_VERDICT_AWAIT = "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"

ALLOWED_PLAN_VERDICTS: tuple[str, ...] = (
    PLAN_VERDICT_APPROVED,
    PLAN_VERDICT_NEEDS_MORE_INFO,
    PLAN_VERDICT_PARKED,
    PLAN_VERDICT_REJECTED,
    PLAN_VERDICT_AWAIT,
)

# The exact upstream Bundle 44 signal this bundle activates from.
UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_VERDICT = (
    _SOURCE_SPECIFICATION_VERDICT_APPROVED
)
UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_GATE = (
    _SOURCE_SPECIFICATION_APPROVED_GATE
)

NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED = (
    "CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED = (
    "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_PARKED = (
    "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_PARKED"
)
NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED = (
    "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT = (
    "AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-44).
PLAN_SAFETY_POSTURE: dict[str, bool] = dict(SPEC_SAFETY_POSTURE)

# Exact offline-acquisition-plan fields a human operator records on a proposal.
REQUIRED_PLAN_FIELDS: tuple[str, ...] = (
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

# Negative safety flags an operator must explicitly affirm True to approve. A
# present-but-not-affirmed value forces a hard rejection; an absent value is a
# missing-required for approval (NEEDS_MORE_INFO).
PLAN_NEGATIVE_SAFETY_FLAGS: tuple[str, ...] = (
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

# Positive capability flags a plan must NOT request -- any truthy value forces a
# hard rejection.
PLAN_FORBIDDEN_CAPABILITY_FLAGS: tuple[str, ...] = (
    "live_fetch",
    "live_fetch_allowed",
    "api_key_required",
    "api_keys",
    "auth_required",
    "account_access",
    "account_access_allowed",
    "order_capability",
    "order_capability_allowed",
    "broker_exchange_capability",
    "broker_exchange_capability_allowed",
    "automation_trigger",
    "automation_enabled",
    "runtime_write",
    "registry_write",
    "dashboard_write",
)

# Descriptive text fields required (non-empty) for an approval.
_REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
    "plan_name",
    "source_specification_id",
    "symbols",
    "coverage_start",
    "coverage_end",
    "missing_candle_policy",
    "duplicate_timestamp_policy",
    "fee_model_plan",
    "slippage_model_plan",
    "freeze_manifest_plan",
    "checksum_plan",
    "provenance_plan",
    "reproducibility_plan",
    "validation_before_use_plan",
    "destination_policy",
)

# Acquisition modes that describe an offline, plan-only path (allowed).
ALLOWED_OFFLINE_ACQUISITION_MODES: tuple[str, ...] = (
    "offline",
    "offline_fixture",
    "offline_batch",
    "manual_offline",
    "offline_file",
    "offline_copy",
    "local_fixture",
    "offline_import",
    "offline_archive",
    "manual_fixture",
)

# Acquisition modes that imply a live/automatic pull (rejected).
_LIVE_ACQUISITION_MODES: tuple[str, ...] = (
    "live",
    "live_api",
    "api",
    "rest_api",
    "websocket",
    "ws",
    "streaming",
    "live_fetch",
    "realtime",
    "auto_fetch",
    "auto",
    "scheduled_fetch",
)

# Source types that describe an offline, frozen artifact (allowed).
ALLOWED_OFFLINE_SOURCE_TYPES: tuple[str, ...] = (
    "vendor_historical_file",
    "offline_fixture",
    "manual_csv",
    "static_dump",
    "frozen_dataset",
    "vendor_historical_candles",
    "offline_archive",
    "local_file",
    "csv_dump",
    "parquet_dump",
)

# Source types that imply a live venue/feed (rejected).
_LIVE_SOURCE_TYPES: tuple[str, ...] = (
    "live_exchange_api",
    "exchange_websocket",
    "broker_api",
    "live_feed",
    "rest_api",
    "streaming_api",
    "exchange_rest",
)

# Offline-acquisition-plan-specific blocked capabilities (this phase only).
_PLAN_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "crypto_d1_offline_acquisition_plan_execution",
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

_PLAN_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 offline acquisition plan proposal is a paper placeholder for a "
    "human-recorded, offline, plan-only, exact offline-acquisition-plan "
    "definition."
)

_PLAN_VERDICT_RATIONALE_PLACEHOLDER = (
    "Offline acquisition plan verdict rationale is a paper placeholder for a "
    "human-recorded acceptance, deferral, or refusal and its supporting "
    "reason."
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 offline acquisition plan contract template and is "
    "execution-free.",
    "It evaluates a paper offline-acquisition-plan proposal only and writes no "
    "report file.",
    "It writes no runtime state, acquires no data, and inspects no data.",
    "It approves no real data acquisition and no live venue access.",
    "An approved offline plan only describes an offline, reproducible, "
    "plan-only path.",
    "It connects to no exchange, broker, or live venue and uses no API keys.",
    "The deferred items stay blocked: qa, qa acceptance, and baseline output.",
    "No crypto-d1 dataset, qa_report, manifest, checksum, freeze record, or "
    "fees file is opened, inspected, or accessed.",
    "A human operator must confirm the exact offline plan before any "
    "acquisition-execution plan is drafted.",
    "No automated step may proceed without human sign-off.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must record an offline-acquisition-plan verdict with a "
    "supporting rationale on paper.",
    "A human operator must confirm no live API, exchange, broker, account, or "
    "key dependency is present.",
    "A human operator must decide whether the exact offline plan is approved "
    "for a later acquisition-execution plan contract.",
    "No automated step may proceed without human sign-off.",
)

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "crypto_d1_source_specification_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "crypto_d1_offline_acquisition_plan_contract_active",
    "crypto_d1_offline_acquisition_plan_contract_state",
    "crypto_d1_source_specification_contract_active",
    "crypto_d1_source_specification_verdict",
    "crypto_d1_source_specification_next_gate",
    "asset_lane",
    "timeframe_lane",
    "offline_acquisition_plan_reference_placeholder",
    "offline_acquisition_plan_verdict",
    "offline_acquisition_plan_verdict_reasons",
    "evaluated_offline_acquisition_plan",
    "allowed_offline_acquisition_plan_verdicts",
    "required_offline_acquisition_plan_fields",
    "plan_negative_safety_flags",
    "plan_forbidden_capability_flags",
    "allowed_asset_universe",
    "parked_market_types",
    "allowed_access_modes",
    "allowed_offline_acquisition_modes",
    "allowed_offline_source_types",
    "required_candle_fields",
    "allowed_timeframe",
    "offline_acquisition_plan_verdict_rationale_placeholder",
    "blocked_execution_items",
    "offline_acquisition_plan_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
    "crypto_d1_source_specification_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(PLAN_SAFETY_POSTURE)


def _as_text(value: Any) -> str:
    """Coerce to a clean string; non-strings become empty."""
    return value if isinstance(value, str) else ""


def _field(state: Any, key: str) -> str:
    """Read a string field from a possibly-malformed state; safe."""
    return _as_text(state.get(key)) if isinstance(state, dict) else ""


def _truthy(value: Any) -> bool:
    """Deterministic truthiness for proposal flags."""
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
    """Deterministic affirmation test for negative safety flags."""
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in (
            "true", "yes", "required", "y", "1", "confirmed",
        )
    return False


def _present(value: Any) -> bool:
    """Deterministic presence test for descriptive plan fields."""
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


def _normalize_assets(value: Any) -> tuple[str, ...]:
    """Normalize an asset universe value to an uppercase tuple."""
    if isinstance(value, str):
        parts = [a.strip().upper() for a in value.replace(",", " ").split()]
    elif isinstance(value, (list, tuple)):
        parts = [_as_text(a).strip().upper() for a in value]
    else:
        return ()
    return tuple(a for a in parts if a)


def _is_d1(value: Any) -> bool:
    """True when the timeframe is a daily (D1) timeframe."""
    return _as_text(value).strip().upper() in ("D1", "1D", "DAILY")


def _has_candle_columns(value: Any) -> bool:
    """True when the expected columns name all required OHLCV fields."""
    if isinstance(value, dict):
        fields = {str(k).strip().lower() for k in value.keys()}
    elif isinstance(value, (list, tuple)):
        fields = {_as_text(x).strip().lower() for x in value}
    else:
        return False
    return all(f in fields for f in REQUIRED_CANDLE_FIELDS)


def _is_utc_daily(value: Any) -> bool:
    """True when a UTC rule is named."""
    return "UTC" in _as_text(value).strip().upper()


def _safety_reject_reasons(plan: dict[str, Any]) -> tuple[str, ...]:
    """Return any hard-safety rejection reasons for an offline plan."""
    reasons: list[str] = []

    for flag in PLAN_FORBIDDEN_CAPABILITY_FLAGS:
        if _truthy(plan.get(flag)):
            reasons.append(f"forbidden_capability:{flag}")

    # A negative-safety flag that is present but NOT affirmed is a request to
    # disable a safety guarantee -- a hard rejection.
    for flag in PLAN_NEGATIVE_SAFETY_FLAGS:
        if flag in plan and not _affirm(plan.get(flag)):
            reasons.append(f"safety_flag_not_affirmed:{flag}")

    mode = _as_text(plan.get("acquisition_mode")).strip().lower()
    if mode in _LIVE_ACQUISITION_MODES:
        reasons.append("live_acquisition_mode")

    src = _as_text(plan.get("allowed_source_type")).strip().lower()
    if src in _LIVE_SOURCE_TYPES:
        reasons.append("live_source_type")

    access = _as_text(plan.get("access_mode")).strip().lower()
    if access in _LIVE_ACQUISITION_MODES:
        reasons.append("live_access_mode")

    forbidden = plan.get("forbidden_capabilities")
    if isinstance(forbidden, (list, tuple)) and len(forbidden) > 0:
        reasons.append("forbidden_capabilities_listed")

    if plan.get("reproducible") is False:
        reasons.append("non_reproducible")
    if plan.get("reproducibility") is False:
        reasons.append("non_reproducible")

    return tuple(reasons)


def _park_reasons(plan: dict[str, Any]) -> tuple[str, ...]:
    """Return any 'plausible but not priority now' parking reasons."""
    reasons: list[str] = []

    market = _as_text(plan.get("market_type")).strip().lower()
    if market in PARKED_MARKET_TYPES:
        reasons.append("perps_or_funding_rate_acquisition_plan_parked")

    assets = _normalize_assets(plan.get("asset_universe"))
    if assets and not set(assets) <= set(ALLOWED_ASSET_UNIVERSE):
        reasons.append("alternative_asset_universe_parked")

    return tuple(reasons)


def _missing_for_approval(plan: dict[str, Any]) -> tuple[str, ...]:
    """Return unmet approval requirements for an otherwise-safe plan."""
    missing: list[str] = []

    for key in _REQUIRED_TEXT_FIELDS:
        if not _present(plan.get(key)):
            missing.append(f"{key}_required")

    assets = _normalize_assets(plan.get("asset_universe"))
    if not assets:
        missing.append("asset_universe_required")
    elif not set(assets) <= set(ALLOWED_ASSET_UNIVERSE):
        missing.append("asset_universe_outside_btc_eth_sol")

    market = _as_text(plan.get("market_type")).strip().lower()
    if market != "spot":
        missing.append("market_type_spot_required")

    if not _is_d1(plan.get("timeframe")):
        missing.append("d1_timeframe_required")

    if not _has_candle_columns(plan.get("expected_columns")):
        missing.append("expected_columns_ohlcv_required")

    mode = _as_text(plan.get("acquisition_mode")).strip().lower()
    if mode not in ALLOWED_OFFLINE_ACQUISITION_MODES:
        missing.append("offline_acquisition_mode_required")

    src = _as_text(plan.get("allowed_source_type")).strip().lower()
    if src not in ALLOWED_OFFLINE_SOURCE_TYPES:
        missing.append("offline_source_type_required")

    tz = plan.get("timezone")
    if tz is None:
        tz = plan.get("session_rule")
    if not _is_utc_daily(tz):
        missing.append("utc_daily_timezone_required")

    if plan.get("human_approval_required") is not True:
        missing.append("human_approval_required_true")

    for flag in PLAN_NEGATIVE_SAFETY_FLAGS:
        if flag not in plan:
            missing.append(f"{flag}_must_be_affirmed_true")

    return tuple(missing)


def evaluate_crypto_d1_offline_acquisition_plan(
    plan: Any,
) -> dict[str, Any]:
    """Return a deterministic verdict for an exact offline acquisition plan.
    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. The verdict is one of APPROVED_OFFLINE_ACQUISITION_PLAN,
    NEEDS_MORE_INFO, PARKED_OFFLINE_ACQUISITION_PLAN, or
    REJECTED_OFFLINE_ACQUISITION_PLAN. It evaluates the SHAPE of a paper plan
    only and unlocks nothing. Safety rejection is checked before parking, and
    parking before completeness, so an unsafe plan rejects even when it would
    otherwise park or need more info."""
    p = plan if isinstance(plan, dict) else {}

    if not p:
        return {
            "verdict": PLAN_VERDICT_NEEDS_MORE_INFO,
            "reasons": ("offline_acquisition_plan_missing",),
        }

    reject_reasons = _safety_reject_reasons(p)
    if reject_reasons:
        return {
            "verdict": PLAN_VERDICT_REJECTED,
            "reasons": reject_reasons,
        }

    park_reasons = _park_reasons(p)
    if park_reasons:
        return {
            "verdict": PLAN_VERDICT_PARKED,
            "reasons": park_reasons,
        }

    missing = _missing_for_approval(p)
    if not missing:
        return {
            "verdict": PLAN_VERDICT_APPROVED,
            "reasons": (
                "offline_plan_complete_d1_reproducible_provenance_checksum_"
                "freeze_manifest_fee_slippage",
            ),
        }

    return {
        "verdict": PLAN_VERDICT_NEEDS_MORE_INFO,
        "reasons": missing,
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == PLAN_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in (
        "PLAN_ONLY",
        "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_ONLY",
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
        tuple(safe.get("allowed_offline_acquisition_plan_verdicts") or ())
        == ALLOWED_PLAN_VERDICTS
    )
    fields_ok = (
        tuple(safe.get("required_offline_acquisition_plan_fields") or ())
        == REQUIRED_PLAN_FIELDS
    )
    neg_flags_ok = (
        tuple(safe.get("plan_negative_safety_flags") or ())
        == PLAN_NEGATIVE_SAFETY_FLAGS
    )
    forbidden_flags_ok = (
        tuple(safe.get("plan_forbidden_capability_flags") or ())
        == PLAN_FORBIDDEN_CAPABILITY_FLAGS
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
        safe.get("offline_acquisition_plan_verdict") in ALLOWED_PLAN_VERDICTS
    )
    plan_blocked_ok = (
        len(tuple(
            safe.get("offline_acquisition_plan_blocked_capabilities") or ()
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
        and neg_flags_ok
        and forbidden_flags_ok
        and assets_ok
        and candle_ok
        and timeframe_ok
        and modes_ok
        and source_types_ok
        and blocked_execution_ok
        and remaining_blocked_ok
        and verdict_value_ok
        and plan_blocked_ok
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
        "allowed_offline_acquisition_plan_verdicts_ok": verdicts_ok,
        "required_offline_acquisition_plan_fields_ok": fields_ok,
        "plan_negative_safety_flags_ok": neg_flags_ok,
        "plan_forbidden_capability_flags_ok": forbidden_flags_ok,
        "allowed_asset_universe_ok": assets_ok,
        "required_candle_fields_ok": candle_ok,
        "allowed_timeframe_ok": timeframe_ok,
        "allowed_offline_acquisition_modes_ok": modes_ok,
        "allowed_offline_source_types_ok": source_types_ok,
        "blocked_execution_items_ok": blocked_execution_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "offline_acquisition_plan_verdict_value_ok": verdict_value_ok,
        "offline_acquisition_plan_blocked_capabilities_present": plan_blocked_ok,
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_offline_acquisition_plan_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 offline acquisition plan
    contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_offline_acquisition_plan_contract(
    source_specification_contract: Any,
    offline_acquisition_plan: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 offline acquisition plan
    contract template plus a paper verdict for a proposed exact offline plan.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (crypto_d1_offline_acquisition_plan_contract_active=True) solely when the
    upstream Bundle 44 crypto-d1 source specification contract is active AND its
    source_specification_verdict is APPROVED_SOURCE_SPECIFICATION AND its
    next_gate is the Bundle 44 approved gate
    (CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED -- the concrete signal
    an offline acquisition-plan contract is required next). When inactive, the
    verdict is AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT regardless of the
    plan. Even when active and APPROVED, every authorization field stays False --
    it evaluates the SHAPE of a paper plan only, acquires nothing, connects to
    nothing, approves no QA, no baseline, and no backtest, writes no report
    file, writes no runtime state, names only placeholders, and grants nothing.
    Returned dicts are fresh."""
    sp = (
        source_specification_contract
        if isinstance(source_specification_contract, dict)
        else {}
    )

    sp_active = (
        sp.get("crypto_d1_source_specification_contract_active") is True
    )
    sp_verdict = _field(sp, "source_specification_verdict")
    sp_next_gate = _field(sp, "next_gate")
    verdict_ok = sp_verdict == UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_VERDICT
    gate_ok = sp_next_gate == UPSTREAM_REQUIRED_SOURCE_SPECIFICATION_GATE

    contract_active = bool(sp_active and verdict_ok and gate_ok)

    if contract_active:
        evaluation = evaluate_crypto_d1_offline_acquisition_plan(
            offline_acquisition_plan
        )
        verdict = evaluation["verdict"]
        reasons = tuple(evaluation["reasons"])
    else:
        verdict = PLAN_VERDICT_AWAIT
        reasons = ("await_crypto_d1_source_specification_contract_gate",)

    state = (
        PLAN_STATE_ACTIVE if contract_active else PLAN_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT
    elif verdict == PLAN_VERDICT_APPROVED:
        next_gate = (
            NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_PLAN_CONTRACT_REQUIRED  # noqa: E501
        )
    elif verdict == PLAN_VERDICT_NEEDS_MORE_INFO:
        next_gate = NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_FIX_REQUIRED
    elif verdict == PLAN_VERDICT_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_PARKED
    else:
        next_gate = NEXT_GATE_CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_REJECTED

    echoed_plan = (
        dict(offline_acquisition_plan)
        if isinstance(offline_acquisition_plan, dict)
        else {}
    )

    contract = {
        "schema_version": PLAN_SCHEMA_VERSION,
        "crypto_d1_source_specification_schema_version": SPEC_SCHEMA_VERSION,
        "idea_id": _field(source_specification_contract, "idea_id"),
        "title": _field(source_specification_contract, "title"),
        "label": DEFAULT_PLAN_LABEL,
        "status": PLAN_STATUS,
        "stage": "CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_ONLY",
        "mode": "RESEARCH_ONLY",
        "crypto_d1_offline_acquisition_plan_contract_active": contract_active,
        "crypto_d1_offline_acquisition_plan_contract_state": state,
        "crypto_d1_source_specification_contract_active": bool(sp_active),
        "crypto_d1_source_specification_verdict": sp_verdict,
        "crypto_d1_source_specification_next_gate": sp_next_gate,
        "asset_lane": _field(source_specification_contract, "asset_lane"),
        "timeframe_lane": _field(
            source_specification_contract, "timeframe_lane"
        ),
        "offline_acquisition_plan_reference_placeholder": (
            _PLAN_REFERENCE_PLACEHOLDER
        ),
        "offline_acquisition_plan_verdict": verdict,
        "offline_acquisition_plan_verdict_reasons": reasons,
        "evaluated_offline_acquisition_plan": echoed_plan,
        "allowed_offline_acquisition_plan_verdicts": ALLOWED_PLAN_VERDICTS,
        "required_offline_acquisition_plan_fields": REQUIRED_PLAN_FIELDS,
        "plan_negative_safety_flags": PLAN_NEGATIVE_SAFETY_FLAGS,
        "plan_forbidden_capability_flags": PLAN_FORBIDDEN_CAPABILITY_FLAGS,
        "allowed_asset_universe": ALLOWED_ASSET_UNIVERSE,
        "parked_market_types": PARKED_MARKET_TYPES,
        "allowed_access_modes": ALLOWED_ACCESS_MODES,
        "allowed_offline_acquisition_modes": ALLOWED_OFFLINE_ACQUISITION_MODES,
        "allowed_offline_source_types": ALLOWED_OFFLINE_SOURCE_TYPES,
        "required_candle_fields": REQUIRED_CANDLE_FIELDS,
        "allowed_timeframe": ALLOWED_TIMEFRAME,
        "offline_acquisition_plan_verdict_rationale_placeholder": (
            _PLAN_VERDICT_RATIONALE_PLACEHOLDER
        ),
        "blocked_execution_items": BLOCKED_EXECUTION_ITEMS,
        "offline_acquisition_plan_blocked_capabilities": (
            _PLAN_BLOCKED_CAPABILITIES
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
        "crypto_d1_source_specification_contract": (
            source_specification_contract
            if isinstance(source_specification_contract, dict)
            else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_crypto_d1_offline_acquisition_plan_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 offline
    acquisition plan contract template. Pure; writes no file. Informational
    only."""
    verdicts = contract.get("allowed_offline_acquisition_plan_verdicts") or ()
    fields = contract.get("required_offline_acquisition_plan_fields") or ()
    neg_flags = contract.get("plan_negative_safety_flags") or ()
    forbidden_flags = contract.get("plan_forbidden_capability_flags") or ()
    assets = contract.get("allowed_asset_universe") or ()
    parked = contract.get("parked_market_types") or ()
    access_modes = contract.get("allowed_access_modes") or ()
    modes = contract.get("allowed_offline_acquisition_modes") or ()
    source_types = contract.get("allowed_offline_source_types") or ()
    candle_fields = contract.get("required_candle_fields") or ()
    timeframe = contract.get("allowed_timeframe") or ()
    reasons = contract.get("offline_acquisition_plan_verdict_reasons") or ()
    blocked_execution = contract.get("blocked_execution_items") or ()
    plan_blocked = (
        contract.get("offline_acquisition_plan_blocked_capabilities") or ()
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
        "# Strategy Factory Crypto-D1 Offline Acquisition Plan Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a "
        "crypto-d1-offline-acquisition-plan-contract-only, paper-only, "
        "offline-plan-only, no-live-api, no-data-acquisition, no-qa-run, "
        "no-baseline-run, no-data-inspection, no-real-strategy-intake-yet, "
        "research-only, and execution-free template -- it records only a paper "
        "offline-acquisition-plan verdict, is not wired into any runtime "
        "state, writes no report file, acquires no data, inspects no data, "
        "connects to no venue, names only placeholders, and grants no "
        "capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Source specification schema: "
        f"`{contract.get('crypto_d1_source_specification_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: CRYPTO_D1_OFFLINE_ACQUISITION_PLAN_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 offline acquisition plan contract active: "
        f"{contract.get('crypto_d1_offline_acquisition_plan_contract_active', '')}"  # noqa: E501
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_offline_acquisition_plan_contract_state', '')}"  # noqa: E501
    )
    lines.append(
        f"Verdict: {contract.get('offline_acquisition_plan_verdict', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Offline Acquisition Plan Proposal Reference")
    lines.append("")
    lines.append(
        "Offline acquisition plan proposal reference: "
        f"{contract.get('offline_acquisition_plan_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Offline Acquisition Plan Verdict Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Offline Acquisition Plan Verdicts")
    lines.append("")
    for x in verdicts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Offline Acquisition Plan Fields")
    lines.append("")
    for x in fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Plan Negative Safety Flags")
    lines.append("")
    for x in neg_flags:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Plan Forbidden Capability Flags")
    lines.append("")
    for x in forbidden_flags:
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
    lines.append("## Offline Acquisition Plan Verdict Rationale")
    lines.append("")
    lines.append(
        "Offline acquisition plan verdict rationale: "
        f"{contract.get('offline_acquisition_plan_verdict_rationale_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Blocked Execution Items")
    lines.append("")
    for x in blocked_execution:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Offline Acquisition Plan Blocked Capabilities")
    lines.append("")
    for cap in plan_blocked:
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
        "- A human operator must confirm the exact offline plan before any "
        "acquisition-execution plan is drafted."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)

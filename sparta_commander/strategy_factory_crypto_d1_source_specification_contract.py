"""SPARTA Offline Strategy Factory - CRYPTO-D1 SOURCE SPECIFICATION CONTRACT.

Bundle 44 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only paper source-specification contract template* builder and
evaluator: it consumes a Bundle 43 crypto-d1 source class contract and, only
when that source-class contract is active with source_class_verdict ==
APPROVED_SOURCE_CLASS and next_gate ==
CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED (the concrete Bundle 43
signal that a source SPECIFICATION contract is required next), evaluates a
proposed exact crypto-d1 source specification on paper and returns a
deterministic verdict describing whether the exact specification is complete,
safe, reproducible, and ready for a future offline acquisition-plan contract.

Note on the upstream gate: Bundle 43's APPROVED_SOURCE_CLASS verdict emits the
next_gate string CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED. Bundle 44
treats that exact active+approved state as the "source specification contract
required" condition. Any other upstream shape (blocked, malformed, wrong stage,
not approved, parked, needs-more-info, rejected, or wrong gate) yields the
AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT verdict.

Reaching an active specification contract and an APPROVED_SOURCE_SPECIFICATION
verdict unlocks NOTHING real. It acquires no data, connects to no exchange,
broker, or live venue, uses no API keys, approves no QA, no baseline, no real
backtest, and unlocks no real strategy intake. The deferred execution items
(qa_run, qa_pass_or_accepted_qa_warn, baseline_backtest_output) stay blocked
and deferred. An approved specification only describes, on paper, an offline,
reproducible, spec-only path; it moves only to a future acquisition-plan
contract.

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
  - SPEC_SCHEMA_VERSION
  - DEFAULT_SPEC_LABEL
  - SPEC_STATUS
  - SPEC_SAFETY_POSTURE
  - SPEC_STATE_ACTIVE
  - SPEC_STATE_BLOCKED
  - SPEC_VERDICT_APPROVED
  - SPEC_VERDICT_NEEDS_MORE_INFO
  - SPEC_VERDICT_PARKED
  - SPEC_VERDICT_REJECTED
  - SPEC_VERDICT_AWAIT
  - ALLOWED_SPEC_VERDICTS
  - NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED
  - NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_PARKED
  - NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT
  - REQUIRED_SPECIFICATION_FIELDS
  - SPEC_CAPABILITY_FLAGS
  - ALLOWED_ASSET_UNIVERSE
  - PARKED_MARKET_TYPES
  - ALLOWED_ACCESS_MODES
  - REQUIRED_CANDLE_FIELDS
  - ALLOWED_TIMEFRAME
  - FORBIDDEN_SPECIFICATION_CAPABILITIES
  - BLOCKED_EXECUTION_ITEMS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - evaluate_crypto_d1_source_specification(spec)
  - build_crypto_d1_source_specification_contract(source_class_contract, source_specification=None)
  - validate_crypto_d1_source_specification_contract(contract)
  - render_crypto_d1_source_specification_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_source_class_contract import (  # noqa: E501
    SOURCE_CLASS_SCHEMA_VERSION,
    SOURCE_CLASS_SAFETY_POSTURE,
    SOURCE_CLASS_VERDICT_APPROVED,
    NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED as _SOURCE_CLASS_APPROVED_GATE,  # noqa: E501
    ALLOWED_ASSET_UNIVERSE,
    PARKED_MARKET_TYPES,
    ALLOWED_SOURCE_ACCESS_MODES as ALLOWED_ACCESS_MODES,
    REQUIRED_CANDLE_FIELDS,
    ALLOWED_TIMEFRAME,
    BLOCKED_EXECUTION_ITEMS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
)

__all__ = [
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
]

SPEC_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_source_specification_contract.v1"
)
DEFAULT_SPEC_LABEL = (
    "Strategy Factory Crypto-D1 Source Specification Contract"
)
SPEC_STATUS = "READ_ONLY_CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT"

SPEC_STATE_ACTIVE = "CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT_ACTIVE"
SPEC_STATE_BLOCKED = "CRYPTO_D1_SOURCE_SPECIFICATION_CONTRACT_BLOCKED"

SPEC_VERDICT_APPROVED = "APPROVED_SOURCE_SPECIFICATION"
SPEC_VERDICT_NEEDS_MORE_INFO = "NEEDS_MORE_INFO"
SPEC_VERDICT_PARKED = "PARKED_SOURCE_SPECIFICATION"
SPEC_VERDICT_REJECTED = "REJECTED_SOURCE_SPECIFICATION"
SPEC_VERDICT_AWAIT = "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"

ALLOWED_SPEC_VERDICTS: tuple[str, ...] = (
    SPEC_VERDICT_APPROVED,
    SPEC_VERDICT_NEEDS_MORE_INFO,
    SPEC_VERDICT_PARKED,
    SPEC_VERDICT_REJECTED,
    SPEC_VERDICT_AWAIT,
)

NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED = (
    "CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED = (
    "CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_PARKED = (
    "CRYPTO_D1_SOURCE_SPECIFICATION_PARKED"
)
NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED = (
    "CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT = (
    "AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT"
)

# Inherited all-false safety posture (same 14 keys as Bundles 30-43).
SPEC_SAFETY_POSTURE: dict[str, bool] = dict(SOURCE_CLASS_SAFETY_POSTURE)

# Exact specification fields a human operator records on a proposal.
REQUIRED_SPECIFICATION_FIELDS: tuple[str, ...] = (
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

# Boolean capability flags that must be explicitly declared False to approve;
# a truthy value forces a hard rejection.
SPEC_CAPABILITY_FLAGS: tuple[str, ...] = (
    "auth_required",
    "api_key_required",
    "live_fetch_allowed",
    "account_access_allowed",
    "order_capability_allowed",
    "broker_exchange_capability_allowed",
)

# Descriptive text fields required (non-empty) for an approval.
_REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
    "source_name",
    "source_class",
    "venue_or_vendor_name",
    "symbols",
    "timestamp_column",
    "open_column",
    "high_column",
    "low_column",
    "close_column",
    "volume_column",
    "coverage_start",
    "coverage_end",
    "expected_frequency",
    "missing_candle_policy",
    "duplicate_timestamp_policy",
    "fee_model_assumption",
    "slippage_model_assumption",
    "reproducibility_notes",
)

# Capabilities a specification must NOT request -- presence forces rejection.
FORBIDDEN_SPECIFICATION_CAPABILITIES: tuple[str, ...] = (
    "live_trading",
    "paper_trading",
    "order_capability",
    "order_placement",
    "account_access",
    "api_keys",
    "broker_auth",
    "exchange_auth",
    "automatic_acquisition",
    "live_api_acquisition",
    "live_execution",
    "live_data_pull",
    "non_reproducible_data",
)

# Source-specification-specific blocked capabilities (this phase only).
_SPEC_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "crypto_d1_source_specification_execution",
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
    "crypto_d1_source_specification_execution",
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

_LIVE_ACCESS_MODES: tuple[str, ...] = (
    "live_api",
    "live",
    "api",
    "rest_api",
    "websocket",
    "ws",
    "streaming",
    "live_exchange",
)

_SPEC_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 source-specification proposal is a paper placeholder for a "
    "human-recorded, offline, spec-only, exact source-specification "
    "definition."
)

_SPEC_VERDICT_RATIONALE_PLACEHOLDER = (
    "Source-specification verdict rationale is a paper placeholder for a "
    "human-recorded acceptance, deferral, or refusal and its supporting "
    "reason."
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 source specification contract template and is "
    "execution-free.",
    "It evaluates a paper source-specification proposal only and writes no "
    "report file.",
    "It writes no runtime state, acquires no data, and inspects no data.",
    "It approves no real data acquisition and no live venue access.",
    "An approved source specification only describes an offline, "
    "reproducible, spec-only path.",
    "It connects to no exchange, broker, or live venue and uses no API keys.",
    "The deferred items stay blocked: qa, qa acceptance, and baseline output.",
    "No crypto-d1 dataset, qa_report, manifest, checksum, freeze record, or "
    "fees file is opened, inspected, or accessed.",
    "A human operator must confirm the exact source specification before any "
    "acquisition plan is drafted.",
    "No automated step may proceed without human sign-off.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must record a source-specification verdict with a "
    "supporting rationale on paper.",
    "A human operator must confirm no live API, exchange, broker, account, or "
    "key dependency is present.",
    "A human operator must decide whether the exact source specification is "
    "approved for a later acquisition plan contract.",
    "No automated step may proceed without human sign-off.",
)

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "crypto_d1_source_class_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "crypto_d1_source_specification_contract_active",
    "crypto_d1_source_specification_contract_state",
    "crypto_d1_source_class_contract_active",
    "crypto_d1_source_class_verdict",
    "crypto_d1_source_class_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_specification_reference_placeholder",
    "source_specification_verdict",
    "source_specification_verdict_reasons",
    "evaluated_source_specification",
    "allowed_source_specification_verdicts",
    "required_source_specification_fields",
    "spec_capability_flags",
    "allowed_asset_universe",
    "parked_market_types",
    "allowed_access_modes",
    "required_candle_fields",
    "allowed_timeframe",
    "forbidden_specification_capabilities",
    "source_specification_verdict_rationale_placeholder",
    "blocked_execution_items",
    "source_specification_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
    "crypto_d1_source_class_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(SPEC_SAFETY_POSTURE)


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


def _present(value: Any) -> bool:
    """Deterministic presence test for descriptive specification fields."""
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


def _has_candle_schema(value: Any) -> bool:
    """True when the candle schema names all required OHLCV fields."""
    if isinstance(value, dict):
        fields = {str(k).strip().lower() for k in value.keys()}
    elif isinstance(value, (list, tuple)):
        fields = {_as_text(x).strip().lower() for x in value}
    else:
        return False
    return all(f in fields for f in REQUIRED_CANDLE_FIELDS)


def _is_utc_daily(value: Any) -> bool:
    """True when a UTC session rule is named."""
    return "UTC" in _as_text(value).strip().upper()


def _safety_reject_reasons(spec: dict[str, Any]) -> tuple[str, ...]:
    """Return any hard-safety rejection reasons for a specification."""
    reasons: list[str] = []

    for flag in SPEC_CAPABILITY_FLAGS:
        if _truthy(spec.get(flag)):
            reasons.append(f"forbidden_capability:{flag}")

    access = _as_text(spec.get("access_mode")).strip().lower()
    if access in _LIVE_ACCESS_MODES:
        reasons.append("live_access_mode")

    forbidden = spec.get("forbidden_capabilities")
    if isinstance(forbidden, (list, tuple)) and len(forbidden) > 0:
        reasons.append("forbidden_capabilities_listed")

    if spec.get("reproducible") is False:
        reasons.append("non_reproducible")
    if spec.get("reproducibility") is False:
        reasons.append("non_reproducible")

    return tuple(reasons)


def _park_reasons(spec: dict[str, Any]) -> tuple[str, ...]:
    """Return any 'plausible but not priority now' parking reasons."""
    reasons: list[str] = []

    market = _as_text(spec.get("market_type")).strip().lower()
    if market in PARKED_MARKET_TYPES:
        reasons.append("perps_or_funding_rate_specification_parked")

    assets = _normalize_assets(spec.get("asset_universe"))
    if assets and not set(assets) <= set(ALLOWED_ASSET_UNIVERSE):
        reasons.append("alternative_asset_universe_parked")

    return tuple(reasons)


def _missing_for_approval(spec: dict[str, Any]) -> tuple[str, ...]:
    """Return unmet approval requirements for an otherwise-safe spec."""
    missing: list[str] = []

    for key in _REQUIRED_TEXT_FIELDS:
        if not _present(spec.get(key)):
            missing.append(f"{key}_required")

    assets = _normalize_assets(spec.get("asset_universe"))
    if not assets:
        missing.append("asset_universe_required")
    elif not set(assets) <= set(ALLOWED_ASSET_UNIVERSE):
        missing.append("asset_universe_outside_btc_eth_sol")

    market = _as_text(spec.get("market_type")).strip().lower()
    if market != "spot":
        missing.append("market_type_spot_required")

    if not _is_d1(spec.get("timeframe")):
        missing.append("d1_timeframe_required")

    if not _has_candle_schema(spec.get("candle_schema")):
        missing.append("candle_schema_ohlcv_required")

    session = spec.get("session_rule")
    if session is None:
        session = spec.get("timezone")
    if not _is_utc_daily(session):
        missing.append("utc_daily_session_rule_required")

    access = _as_text(spec.get("access_mode")).strip().lower()
    if access not in ALLOWED_ACCESS_MODES:
        missing.append("offline_access_mode_required")

    if spec.get("provenance_required") is not True:
        missing.append("provenance_required_true")
    if spec.get("checksum_required") is not True:
        missing.append("checksum_required_true")
    if spec.get("freeze_manifest_required") is not True:
        missing.append("freeze_manifest_required_true")

    for flag in SPEC_CAPABILITY_FLAGS:
        if flag not in spec:
            missing.append(f"{flag}_must_be_declared_false")

    return tuple(missing)


def evaluate_crypto_d1_source_specification(
    spec: Any,
) -> dict[str, Any]:
    """Return a deterministic verdict for an exact source specification. Pure;
    no I/O, no mutation, no timestamp, no random id. Unknown/malformed inputs
    never raise. The verdict is one of APPROVED_SOURCE_SPECIFICATION,
    NEEDS_MORE_INFO, PARKED_SOURCE_SPECIFICATION, or
    REJECTED_SOURCE_SPECIFICATION. It evaluates the SHAPE of a paper
    specification only and unlocks nothing. Safety rejection is checked before
    parking, and parking before completeness, so an unsafe spec rejects even
    when it would otherwise park or need more info."""
    p = spec if isinstance(spec, dict) else {}

    if not p:
        return {
            "verdict": SPEC_VERDICT_NEEDS_MORE_INFO,
            "reasons": ("source_specification_missing",),
        }

    reject_reasons = _safety_reject_reasons(p)
    if reject_reasons:
        return {
            "verdict": SPEC_VERDICT_REJECTED,
            "reasons": reject_reasons,
        }

    park_reasons = _park_reasons(p)
    if park_reasons:
        return {
            "verdict": SPEC_VERDICT_PARKED,
            "reasons": park_reasons,
        }

    missing = _missing_for_approval(p)
    if not missing:
        return {
            "verdict": SPEC_VERDICT_APPROVED,
            "reasons": (
                "offline_spec_complete_d1_reproducible_provenance_checksum_"
                "freeze_manifest",
            ),
        }

    return {
        "verdict": SPEC_VERDICT_NEEDS_MORE_INFO,
        "reasons": missing,
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == SPEC_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in (
        "PLAN_ONLY",
        "CRYPTO_D1_SOURCE_SPECIFICATION_ONLY",
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
        tuple(safe.get("allowed_source_specification_verdicts") or ())
        == ALLOWED_SPEC_VERDICTS
    )
    fields_ok = (
        tuple(safe.get("required_source_specification_fields") or ())
        == REQUIRED_SPECIFICATION_FIELDS
    )
    flags_ok = (
        tuple(safe.get("spec_capability_flags") or ())
        == SPEC_CAPABILITY_FLAGS
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
    forbidden_ok = (
        tuple(safe.get("forbidden_specification_capabilities") or ())
        == FORBIDDEN_SPECIFICATION_CAPABILITIES
    )
    verdict_value_ok = (
        safe.get("source_specification_verdict") in ALLOWED_SPEC_VERDICTS
    )
    spec_blocked_ok = (
        len(tuple(safe.get("source_specification_blocked_capabilities") or ()))
        >= 1
    )
    notes_ok = len(tuple(safe.get("operator_notes") or ())) >= 1
    next_steps_ok = (
        len(tuple(safe.get("human_operator_required_next_steps") or ())) >= 1
    )

    collections_ok = (
        verdicts_ok
        and fields_ok
        and flags_ok
        and assets_ok
        and candle_ok
        and timeframe_ok
        and blocked_execution_ok
        and remaining_blocked_ok
        and forbidden_ok
        and verdict_value_ok
        and spec_blocked_ok
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
        "allowed_source_specification_verdicts_ok": verdicts_ok,
        "required_source_specification_fields_ok": fields_ok,
        "spec_capability_flags_ok": flags_ok,
        "allowed_asset_universe_ok": assets_ok,
        "required_candle_fields_ok": candle_ok,
        "allowed_timeframe_ok": timeframe_ok,
        "blocked_execution_items_ok": blocked_execution_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "forbidden_specification_capabilities_ok": forbidden_ok,
        "source_specification_verdict_value_ok": verdict_value_ok,
        "source_specification_blocked_capabilities_present": spec_blocked_ok,
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_source_specification_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 source specification
    contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_source_specification_contract(
    source_class_contract: Any,
    source_specification: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 source specification
    contract template plus a paper verdict for a proposed exact specification.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (crypto_d1_source_specification_contract_active=True) solely when the
    upstream Bundle 43 crypto-d1 source class contract is active AND its
    source_class_verdict is APPROVED_SOURCE_CLASS AND its next_gate is the
    Bundle 43 approved gate (CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED
    -- the concrete signal a specification contract is required next). When
    inactive, the verdict is AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT regardless of
    the specification. Even when active and APPROVED, every authorization field
    stays False -- it evaluates the SHAPE of a paper specification only,
    acquires nothing, connects to nothing, approves no QA, no baseline, and no
    backtest, writes no report file, writes no runtime state, names only
    placeholders, and grants nothing. Returned dicts are fresh."""
    sc = source_class_contract if isinstance(source_class_contract, dict) else {}

    sc_active = (
        sc.get("crypto_d1_source_class_contract_active") is True
    )
    sc_verdict = _field(sc, "source_class_verdict")
    sc_next_gate = _field(sc, "next_gate")
    verdict_ok = sc_verdict == SOURCE_CLASS_VERDICT_APPROVED
    gate_ok = sc_next_gate == _SOURCE_CLASS_APPROVED_GATE

    contract_active = bool(sc_active and verdict_ok and gate_ok)

    if contract_active:
        evaluation = evaluate_crypto_d1_source_specification(
            source_specification
        )
        verdict = evaluation["verdict"]
        reasons = tuple(evaluation["reasons"])
    else:
        verdict = SPEC_VERDICT_AWAIT
        reasons = ("await_crypto_d1_source_class_contract_gate",)

    state = (
        SPEC_STATE_ACTIVE if contract_active else SPEC_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = NEXT_GATE_AWAIT_CRYPTO_D1_SOURCE_CLASS_CONTRACT
    elif verdict == SPEC_VERDICT_APPROVED:
        next_gate = (
            NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED
        )
    elif verdict == SPEC_VERDICT_NEEDS_MORE_INFO:
        next_gate = NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_FIX_REQUIRED
    elif verdict == SPEC_VERDICT_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_PARKED
    else:
        next_gate = NEXT_GATE_CRYPTO_D1_SOURCE_SPECIFICATION_REJECTED

    echoed_spec = (
        dict(source_specification)
        if isinstance(source_specification, dict)
        else {}
    )

    contract = {
        "schema_version": SPEC_SCHEMA_VERSION,
        "crypto_d1_source_class_schema_version": SOURCE_CLASS_SCHEMA_VERSION,
        "idea_id": _field(source_class_contract, "idea_id"),
        "title": _field(source_class_contract, "title"),
        "label": DEFAULT_SPEC_LABEL,
        "status": SPEC_STATUS,
        "stage": "CRYPTO_D1_SOURCE_SPECIFICATION_ONLY",
        "mode": "RESEARCH_ONLY",
        "crypto_d1_source_specification_contract_active": contract_active,
        "crypto_d1_source_specification_contract_state": state,
        "crypto_d1_source_class_contract_active": bool(sc_active),
        "crypto_d1_source_class_verdict": sc_verdict,
        "crypto_d1_source_class_next_gate": sc_next_gate,
        "asset_lane": _field(source_class_contract, "asset_lane"),
        "timeframe_lane": _field(source_class_contract, "timeframe_lane"),
        "source_specification_reference_placeholder": (
            _SPEC_REFERENCE_PLACEHOLDER
        ),
        "source_specification_verdict": verdict,
        "source_specification_verdict_reasons": reasons,
        "evaluated_source_specification": echoed_spec,
        "allowed_source_specification_verdicts": ALLOWED_SPEC_VERDICTS,
        "required_source_specification_fields": REQUIRED_SPECIFICATION_FIELDS,
        "spec_capability_flags": SPEC_CAPABILITY_FLAGS,
        "allowed_asset_universe": ALLOWED_ASSET_UNIVERSE,
        "parked_market_types": PARKED_MARKET_TYPES,
        "allowed_access_modes": ALLOWED_ACCESS_MODES,
        "required_candle_fields": REQUIRED_CANDLE_FIELDS,
        "allowed_timeframe": ALLOWED_TIMEFRAME,
        "forbidden_specification_capabilities": (
            FORBIDDEN_SPECIFICATION_CAPABILITIES
        ),
        "source_specification_verdict_rationale_placeholder": (
            _SPEC_VERDICT_RATIONALE_PLACEHOLDER
        ),
        "blocked_execution_items": BLOCKED_EXECUTION_ITEMS,
        "source_specification_blocked_capabilities": (
            _SPEC_BLOCKED_CAPABILITIES
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
        "crypto_d1_source_class_contract": (
            source_class_contract
            if isinstance(source_class_contract, dict)
            else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_crypto_d1_source_specification_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 source
    specification contract template. Pure; writes no file. Informational
    only."""
    verdicts = contract.get("allowed_source_specification_verdicts") or ()
    fields = contract.get("required_source_specification_fields") or ()
    flags = contract.get("spec_capability_flags") or ()
    assets = contract.get("allowed_asset_universe") or ()
    parked = contract.get("parked_market_types") or ()
    access_modes = contract.get("allowed_access_modes") or ()
    candle_fields = contract.get("required_candle_fields") or ()
    timeframe = contract.get("allowed_timeframe") or ()
    forbidden = contract.get("forbidden_specification_capabilities") or ()
    reasons = contract.get("source_specification_verdict_reasons") or ()
    blocked_execution = contract.get("blocked_execution_items") or ()
    spec_blocked = (
        contract.get("source_specification_blocked_capabilities") or ()
    )
    remaining_blocked = (
        contract.get("remaining_real_world_capabilities_blocked") or ()
    )
    next_steps = contract.get("human_operator_required_next_steps") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Crypto-D1 Source Specification Contract")
    lines.append("")
    lines.append(
        "Template only: this is a "
        "crypto-d1-source-specification-contract-only, paper-only, "
        "offline-spec-only, no-live-api, no-data-acquisition, no-qa-run, "
        "no-baseline-run, no-data-inspection, no-real-strategy-intake-yet, "
        "research-only, and execution-free template -- it records only a paper "
        "source-specification verdict, is not wired into any runtime state, "
        "writes no report file, acquires no data, inspects no data, connects "
        "to no venue, names only placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Source class schema: "
        f"`{contract.get('crypto_d1_source_class_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: CRYPTO_D1_SOURCE_SPECIFICATION_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 source specification contract active: "
        f"{contract.get('crypto_d1_source_specification_contract_active', '')}"
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_source_specification_contract_state', '')}"
    )
    lines.append(
        f"Verdict: {contract.get('source_specification_verdict', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Source Specification Proposal Reference")
    lines.append("")
    lines.append(
        "Source specification proposal reference: "
        f"{contract.get('source_specification_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Source Specification Verdict Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Source Specification Verdicts")
    lines.append("")
    for x in verdicts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Source Specification Fields")
    lines.append("")
    for x in fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Specification Capability Flags")
    lines.append("")
    for x in flags:
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
    lines.append("## Forbidden Specification Capabilities")
    lines.append("")
    for x in forbidden:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Source Specification Verdict Rationale")
    lines.append("")
    lines.append(
        "Source specification verdict rationale: "
        f"{contract.get('source_specification_verdict_rationale_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Blocked Execution Items")
    lines.append("")
    for x in blocked_execution:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Source Specification Blocked Capabilities")
    lines.append("")
    for cap in spec_blocked:
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
        "- A human operator must confirm the exact source specification "
        "before any acquisition plan is drafted."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)

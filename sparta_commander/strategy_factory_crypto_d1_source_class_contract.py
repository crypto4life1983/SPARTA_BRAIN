"""SPARTA Offline Strategy Factory - CRYPTO-D1 SOURCE CLASS CONTRACT.

Bundle 43 of the Strategy Factory automation backbone. This module is a PURE,
stdlib-only *read-only paper source-class contract template* builder and
evaluator: it consumes a Bundle 42 crypto-d1 acquire decision contract and,
only when that acquire contract is active with acquire_decision ==
ACQUIRE_APPROVED_FOR_SOURCE_CLASS_CONTRACT and next_gate ==
CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED, evaluates a proposed crypto-d1 source
class on paper and returns a deterministic verdict describing whether the
proposed source class is acceptable for later, offline, reproducible research.

Reaching an active source-class contract and an APPROVED_SOURCE_CLASS verdict
unlocks NOTHING real. It acquires no data, connects to no exchange, broker, or
live venue, uses no API keys, approves no QA, no baseline, no real-strategy
backtest path, and unlocks no real strategy intake. The deferred execution
items (qa_run, qa_pass_or_accepted_qa_warn, baseline_backtest_output) stay
blocked and deferred. An approved source class only describes, on paper, an
offline, reproducible, spec-only path; it moves only to a future acquisition
plan contract.

It never runs Strategy Factory, never acquires data, never inspects, loads,
validates, transforms, or computes on real data, never inspects market data,
never runs QA, never produces a QA verdict, never runs a baseline, never
backtests, never simulates, never fetches data, never connects to any
exchange, broker, or vendor, never opens or reads any crypto-d1 dataset file,
qa_report, manifest, checksum, freeze record, fees file, or baseline output,
and executes nothing. It opens no network, spawns no subprocess, writes no
file, reads no file, lists no directory, touches no
broker/exchange/order/trading/live/distribution/autopilot surface,
promotes/deploys nothing, and records no approval decision. It records no
timestamp, mints no random id, reads no environment, and dynamically imports
nothing.

Public API:
  - SOURCE_CLASS_SCHEMA_VERSION
  - DEFAULT_SOURCE_CLASS_LABEL
  - SOURCE_CLASS_STATUS
  - SOURCE_CLASS_SAFETY_POSTURE
  - SOURCE_CLASS_STATE_ACTIVE
  - SOURCE_CLASS_STATE_BLOCKED
  - SOURCE_CLASS_VERDICT_APPROVED
  - SOURCE_CLASS_VERDICT_NEEDS_MORE_INFO
  - SOURCE_CLASS_VERDICT_PARKED
  - SOURCE_CLASS_VERDICT_REJECTED
  - SOURCE_CLASS_VERDICT_AWAIT
  - ALLOWED_SOURCE_CLASS_VERDICTS
  - NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED
  - NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_PARKED
  - NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION
  - REQUIRED_SOURCE_CLASS_FIELDS
  - ALLOWED_ASSET_UNIVERSE
  - PARKED_MARKET_TYPES
  - ALLOWED_VENUE_CLASSES
  - ALLOWED_SOURCE_ACCESS_MODES
  - REQUIRED_CANDLE_FIELDS
  - ALLOWED_TIMEFRAME
  - FORBIDDEN_SOURCE_CLASS_CAPABILITIES
  - BLOCKED_EXECUTION_ITEMS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - evaluate_crypto_d1_source_class_proposal(proposal)
  - build_crypto_d1_source_class_contract(acquire_contract, source_class_proposal=None)
  - validate_crypto_d1_source_class_contract(contract)
  - render_crypto_d1_source_class_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_acquire_decision_contract import (  # noqa: E501
    ACQUIRE_SCHEMA_VERSION,
    ACQUIRE_SAFETY_POSTURE,
    ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT,
    NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED,
)

__all__ = [
    "SOURCE_CLASS_SCHEMA_VERSION",
    "DEFAULT_SOURCE_CLASS_LABEL",
    "SOURCE_CLASS_STATUS",
    "SOURCE_CLASS_SAFETY_POSTURE",
    "SOURCE_CLASS_STATE_ACTIVE",
    "SOURCE_CLASS_STATE_BLOCKED",
    "SOURCE_CLASS_VERDICT_APPROVED",
    "SOURCE_CLASS_VERDICT_NEEDS_MORE_INFO",
    "SOURCE_CLASS_VERDICT_PARKED",
    "SOURCE_CLASS_VERDICT_REJECTED",
    "SOURCE_CLASS_VERDICT_AWAIT",
    "ALLOWED_SOURCE_CLASS_VERDICTS",
    "NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_PARKED",
    "NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_REJECTED",
    "NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION",
    "REQUIRED_SOURCE_CLASS_FIELDS",
    "ALLOWED_ASSET_UNIVERSE",
    "PARKED_MARKET_TYPES",
    "ALLOWED_VENUE_CLASSES",
    "ALLOWED_SOURCE_ACCESS_MODES",
    "REQUIRED_CANDLE_FIELDS",
    "ALLOWED_TIMEFRAME",
    "FORBIDDEN_SOURCE_CLASS_CAPABILITIES",
    "BLOCKED_EXECUTION_ITEMS",
    "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "evaluate_crypto_d1_source_class_proposal",
    "build_crypto_d1_source_class_contract",
    "validate_crypto_d1_source_class_contract",
    "render_crypto_d1_source_class_contract_markdown",
]

SOURCE_CLASS_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_source_class_contract.v1"
)
DEFAULT_SOURCE_CLASS_LABEL = (
    "Strategy Factory Crypto-D1 Source Class Contract"
)
SOURCE_CLASS_STATUS = "READ_ONLY_CRYPTO_D1_SOURCE_CLASS_CONTRACT"

SOURCE_CLASS_STATE_ACTIVE = "CRYPTO_D1_SOURCE_CLASS_CONTRACT_ACTIVE"
SOURCE_CLASS_STATE_BLOCKED = "CRYPTO_D1_SOURCE_CLASS_CONTRACT_BLOCKED"

SOURCE_CLASS_VERDICT_APPROVED = "APPROVED_SOURCE_CLASS"
SOURCE_CLASS_VERDICT_NEEDS_MORE_INFO = "NEEDS_MORE_INFO"
SOURCE_CLASS_VERDICT_PARKED = "PARKED_SOURCE_CLASS"
SOURCE_CLASS_VERDICT_REJECTED = "REJECTED_SOURCE_CLASS"
SOURCE_CLASS_VERDICT_AWAIT = "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"

ALLOWED_SOURCE_CLASS_VERDICTS: tuple[str, ...] = (
    SOURCE_CLASS_VERDICT_APPROVED,
    SOURCE_CLASS_VERDICT_NEEDS_MORE_INFO,
    SOURCE_CLASS_VERDICT_PARKED,
    SOURCE_CLASS_VERDICT_REJECTED,
    SOURCE_CLASS_VERDICT_AWAIT,
)

NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED = (
    "CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED = (
    "CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_PARKED = "CRYPTO_D1_SOURCE_CLASS_PARKED"
NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_REJECTED = "CRYPTO_D1_SOURCE_CLASS_REJECTED"
NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION = "AWAIT_CRYPTO_D1_ACQUIRE_DECISION"

# Inherited all-false safety posture (same 14 keys as Bundles 30-42).
SOURCE_CLASS_SAFETY_POSTURE: dict[str, bool] = dict(ACQUIRE_SAFETY_POSTURE)

# Paper spec fields a human operator records on a source-class proposal.
REQUIRED_SOURCE_CLASS_FIELDS: tuple[str, ...] = (
    "asset_universe",
    "market_type",
    "venue_class",
    "source_access_mode",
    "timeframe",
    "candle_schema",
    "fee_model_presence",
    "coverage_window",
    "reproducibility",
    "provenance_required",
    "checksum_required",
    "session_rule",
)

ALLOWED_ASSET_UNIVERSE: tuple[str, ...] = ("BTC", "ETH", "SOL")

PARKED_MARKET_TYPES: tuple[str, ...] = (
    "perp",
    "perps",
    "perpetual",
    "perpetuals",
    "futures",
    "future",
    "funding_rate",
    "funding",
    "swap",
)

ALLOWED_VENUE_CLASSES: tuple[str, ...] = (
    "exchange_historical_candles",
    "vendor_historical_candles",
    "synthetic_fixture",
    "manual_fixture",
    "offline_fixture",
)

ALLOWED_SOURCE_ACCESS_MODES: tuple[str, ...] = (
    "offline_fixture",
    "fixture",
    "spec_only",
    "manual_fixture",
    "synthetic_fixture",
    "offline_spec",
)

REQUIRED_CANDLE_FIELDS: tuple[str, ...] = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
)

ALLOWED_TIMEFRAME: tuple[str, ...] = ("D1",)

# Capabilities a proposal must NOT request -- presence forces a rejection.
FORBIDDEN_SOURCE_CLASS_CAPABILITIES: tuple[str, ...] = (
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
    "non_reproducible_data",
)

# Execution items that stay blocked and deferred -- never approved here.
BLOCKED_EXECUTION_ITEMS: tuple[str, ...] = (
    "qa_run",
    "qa_pass_or_accepted_qa_warn",
    "baseline_backtest_output",
)

# Real-world capabilities that remain blocked even with an active contract and
# an APPROVED_SOURCE_CLASS verdict. None of these is ever unlocked here.
REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED: tuple[str, ...] = (
    "real_strategy_intake",
    "real_data_acquisition",
    "real_data_load",
    "real_data_validation",
    "real_data_transform",
    "real_data_inspection",
    "real_data_compute",
    "real_market_data_inspection",
    "real_crypto_d1_dataset_inspection",
    "real_qa_run",
    "real_baseline_run",
    "real_backtest",
    "real_simulation",
    "real_pipeline_execution",
    "real_orchestrator_execution",
    "real_research_run",
    "real_data_fetch",
    "real_exchange_connection",
    "real_broker_connection",
    "real_live_api_access",
    "broker",
    "exchange",
    "order",
    "live_execution",
    "paper_execution",
    "autopilot",
    "automation",
    "upload",
    "deploy",
    "promotion",
)

# Source-class-specific blocked capabilities (this phase only).
_SOURCE_CLASS_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "crypto_d1_source_class_execution",
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
    "crypto_d1_source_class_execution",
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

# Proposal keys whose truthy presence forces a hard rejection.
_REJECT_FLAG_KEYS: tuple[str, ...] = (
    "requires_api_keys",
    "api_keys",
    "requires_account_access",
    "account_access",
    "requires_broker_auth",
    "broker_auth",
    "requires_exchange_auth",
    "exchange_auth",
    "order_capability",
    "order_placement",
    "paper_trading",
    "live_trading",
    "automatic_acquisition",
    "live_execution",
    "non_reproducible",
)

_LIVE_SOURCE_ACCESS_MODES: tuple[str, ...] = (
    "live_api",
    "live",
    "api",
    "rest_api",
    "websocket",
    "ws",
    "streaming",
    "live_exchange",
)

_LIVE_VENUE_CLASSES: tuple[str, ...] = (
    "live_exchange_api",
    "exchange_account",
    "broker",
    "broker_account",
    "live_api",
    "live_exchange",
)

_SOURCE_CLASS_PROPOSAL_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 source-class proposal is a paper placeholder for a "
    "human-recorded, offline, spec-only source-class definition."
)

_SOURCE_CLASS_VERDICT_RATIONALE_PLACEHOLDER = (
    "Source-class verdict rationale is a paper placeholder for a "
    "human-recorded acceptance, deferral, or refusal and its supporting "
    "reason."
)

# Deterministic, verb-safe operator guidance.
_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 source class contract template and is "
    "execution-free.",
    "It evaluates a paper source-class proposal only and writes no report "
    "file.",
    "It writes no runtime state, acquires no data, and inspects no data.",
    "It approves no real data acquisition and no live venue access.",
    "An approved source class only describes an offline, reproducible, "
    "spec-only path.",
    "It connects to no exchange, broker, or live venue and uses no API keys.",
    "The deferred items stay blocked: qa, qa acceptance, and baseline output.",
    "No crypto-d1 dataset, qa_report, manifest, checksum, freeze record, or "
    "fees file is opened, inspected, or accessed.",
    "A human operator must confirm the source class before any acquisition "
    "plan is drafted.",
    "No automated step may proceed without human sign-off.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must record a source-class verdict with a supporting "
    "rationale on paper.",
    "A human operator must confirm no live API, exchange, broker, account, or "
    "key capability is present.",
    "A human operator must decide whether the source class is approved for a "
    "later acquisition plan contract.",
    "No automated step may proceed without human sign-off.",
)

# Top-level fields required for a contract to validate. "validation" is NOT
# required here -- requiring the contract to embed its own validation result
# would be circular.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "crypto_d1_acquire_decision_schema_version",
    "idea_id",
    "title",
    "label",
    "status",
    "stage",
    "mode",
    "crypto_d1_source_class_contract_active",
    "crypto_d1_source_class_contract_state",
    "crypto_d1_acquire_decision_contract_active",
    "crypto_d1_acquire_decision",
    "crypto_d1_acquire_decision_next_gate",
    "asset_lane",
    "timeframe_lane",
    "source_class_proposal_reference_placeholder",
    "source_class_verdict",
    "source_class_verdict_reasons",
    "evaluated_source_class_proposal",
    "allowed_source_class_verdicts",
    "required_source_class_fields",
    "allowed_asset_universe",
    "parked_market_types",
    "allowed_venue_classes",
    "allowed_source_access_modes",
    "required_candle_fields",
    "allowed_timeframe",
    "forbidden_source_class_capabilities",
    "source_class_verdict_rationale_placeholder",
    "blocked_execution_items",
    "source_class_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
    "crypto_d1_acquire_decision_contract",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(SOURCE_CLASS_SAFETY_POSTURE)


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


def _has_coverage(value: Any) -> bool:
    """True when an explicit coverage window or minimum is present."""
    if isinstance(value, dict):
        start = value.get("start") or value.get("start_date")
        end = value.get("end") or value.get("end_date")
        if start and end:
            return True
        return bool(
            value.get("min_coverage") or value.get("minimum_coverage")
        )
    if isinstance(value, (list, tuple)):
        return len(value) >= 2
    return bool(_as_text(value).strip())


def _is_utc_daily(value: Any) -> bool:
    """True when a UTC session rule is named."""
    return "UTC" in _as_text(value).strip().upper()


def _safety_reject_reasons(proposal: dict[str, Any]) -> tuple[str, ...]:
    """Return any hard-safety rejection reasons for a proposal."""
    reasons: list[str] = []

    access = _as_text(proposal.get("source_access_mode")).strip().lower()
    if access in _LIVE_SOURCE_ACCESS_MODES:
        reasons.append("live_source_access_mode")

    venue = _as_text(proposal.get("venue_class")).strip().lower()
    if venue in _LIVE_VENUE_CLASSES:
        reasons.append("live_venue_class")

    for flag in _REJECT_FLAG_KEYS:
        if _truthy(proposal.get(flag)):
            reasons.append(f"forbidden_capability:{flag}")

    forbidden = proposal.get("forbidden_capabilities")
    if isinstance(forbidden, (list, tuple)) and len(forbidden) > 0:
        reasons.append("forbidden_capabilities_listed")

    if proposal.get("reproducibility") is False:
        reasons.append("non_reproducible")

    return tuple(reasons)


def _missing_for_approval(proposal: dict[str, Any]) -> tuple[str, ...]:
    """Return unmet approval requirements for an otherwise-safe proposal."""
    missing: list[str] = []

    assets = _normalize_assets(proposal.get("asset_universe"))
    if not assets:
        missing.append("asset_universe")
    elif not set(assets) <= set(ALLOWED_ASSET_UNIVERSE):
        missing.append("asset_universe_outside_btc_eth_sol")

    market = _as_text(proposal.get("market_type")).strip().lower()
    if market != "spot":
        missing.append("market_type_spot_required")

    venue = _as_text(proposal.get("venue_class")).strip().lower()
    if venue not in ALLOWED_VENUE_CLASSES:
        missing.append("offline_venue_class_required")

    access = _as_text(proposal.get("source_access_mode")).strip().lower()
    if access not in ALLOWED_SOURCE_ACCESS_MODES:
        missing.append("offline_source_access_mode_required")

    if not _is_d1(proposal.get("timeframe")):
        missing.append("d1_timeframe_required")

    if not _has_candle_schema(proposal.get("candle_schema")):
        missing.append("candle_schema_ohlcv_required")

    if not _truthy(proposal.get("fee_model_presence")):
        missing.append("fee_model_presence_required")

    if not _has_coverage(proposal.get("coverage_window")):
        missing.append("coverage_window_required")

    if not _truthy(proposal.get("reproducibility")):
        missing.append("reproducibility_required")

    if proposal.get("provenance_required") is not True:
        missing.append("provenance_required_true")

    if proposal.get("checksum_required") is not True:
        missing.append("checksum_required_true")

    session = proposal.get("session_rule")
    if session is None:
        session = proposal.get("timezone")
    if not _is_utc_daily(session):
        missing.append("utc_daily_session_rule_required")

    return tuple(missing)


def evaluate_crypto_d1_source_class_proposal(
    proposal: Any,
) -> dict[str, Any]:
    """Return a deterministic verdict for a source-class proposal. Pure; no
    I/O, no mutation, no timestamp, no random id. Unknown/malformed inputs
    never raise. The verdict is one of APPROVED_SOURCE_CLASS, NEEDS_MORE_INFO,
    PARKED_SOURCE_CLASS, or REJECTED_SOURCE_CLASS. It evaluates the SHAPE of a
    paper proposal only and unlocks nothing."""
    p = proposal if isinstance(proposal, dict) else {}

    if not p:
        return {
            "verdict": SOURCE_CLASS_VERDICT_NEEDS_MORE_INFO,
            "reasons": ("source_class_proposal_missing",),
        }

    reject_reasons = _safety_reject_reasons(p)
    if reject_reasons:
        return {
            "verdict": SOURCE_CLASS_VERDICT_REJECTED,
            "reasons": reject_reasons,
        }

    market = _as_text(p.get("market_type")).strip().lower()
    if market in PARKED_MARKET_TYPES:
        return {
            "verdict": SOURCE_CLASS_VERDICT_PARKED,
            "reasons": (
                "perps_or_funding_rate_source_class_parked_until_spot_path_"
                "complete",
            ),
        }

    missing = _missing_for_approval(p)
    if not missing:
        return {
            "verdict": SOURCE_CLASS_VERDICT_APPROVED,
            "reasons": (
                "offline_spec_safe_d1_reproducible_provenance_checksum",
            ),
        }

    return {
        "verdict": SOURCE_CLASS_VERDICT_NEEDS_MORE_INFO,
        "reasons": missing,
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = safe.get("schema_version") == SOURCE_CLASS_SCHEMA_VERSION
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = safe.get("stage") in (
        "PLAN_ONLY",
        "CRYPTO_D1_SOURCE_CLASS_ONLY",
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
        tuple(safe.get("allowed_source_class_verdicts") or ())
        == ALLOWED_SOURCE_CLASS_VERDICTS
    )
    fields_ok = (
        tuple(safe.get("required_source_class_fields") or ())
        == REQUIRED_SOURCE_CLASS_FIELDS
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
        tuple(safe.get("forbidden_source_class_capabilities") or ())
        == FORBIDDEN_SOURCE_CLASS_CAPABILITIES
    )
    verdict_value_ok = (
        safe.get("source_class_verdict") in ALLOWED_SOURCE_CLASS_VERDICTS
    )
    source_blocked_ok = (
        len(tuple(safe.get("source_class_blocked_capabilities") or ())) >= 1
    )
    notes_ok = len(tuple(safe.get("operator_notes") or ())) >= 1
    next_steps_ok = (
        len(tuple(safe.get("human_operator_required_next_steps") or ())) >= 1
    )

    collections_ok = (
        verdicts_ok
        and fields_ok
        and assets_ok
        and candle_ok
        and timeframe_ok
        and blocked_execution_ok
        and remaining_blocked_ok
        and forbidden_ok
        and verdict_value_ok
        and source_blocked_ok
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
        "allowed_source_class_verdicts_ok": verdicts_ok,
        "required_source_class_fields_ok": fields_ok,
        "allowed_asset_universe_ok": assets_ok,
        "required_candle_fields_ok": candle_ok,
        "allowed_timeframe_ok": timeframe_ok,
        "blocked_execution_items_ok": blocked_execution_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "forbidden_source_class_capabilities_ok": forbidden_ok,
        "source_class_verdict_value_ok": verdict_value_ok,
        "source_class_blocked_capabilities_present": source_blocked_ok,
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_source_class_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 source class contract
    template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_source_class_contract(
    acquire_contract: Any,
    source_class_proposal: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 source class contract
    template plus a paper verdict for a proposed source class.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (crypto_d1_source_class_contract_active=True) solely when the upstream
    Bundle 42 crypto-d1 acquire decision contract is active AND its
    acquire_decision is ACQUIRE_APPROVED_FOR_SOURCE_CLASS_CONTRACT AND its
    next_gate is CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED. When inactive, the
    verdict is AWAIT_CRYPTO_D1_ACQUIRE_DECISION regardless of the proposal.
    Even when active and APPROVED, every authorization field stays False -- it
    evaluates the SHAPE of a paper source-class proposal only, acquires
    nothing, connects to nothing, approves no QA, no baseline, and no backtest,
    writes no report file, writes no runtime state, names only placeholders,
    and grants nothing. Returned dicts are fresh."""
    acq = acquire_contract if isinstance(acquire_contract, dict) else {}

    acq_active = (
        acq.get("crypto_d1_acquire_decision_contract_active") is True
    )
    acq_decision = _field(acq, "acquire_decision")
    acq_next_gate = _field(acq, "next_gate")
    decision_ok = (
        acq_decision == ACQUIRE_DECISION_APPROVED_FOR_SOURCE_CLASS_CONTRACT
    )
    gate_ok = (
        acq_next_gate == NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_CONTRACT_REQUIRED
    )

    contract_active = bool(acq_active and decision_ok and gate_ok)

    if contract_active:
        evaluation = evaluate_crypto_d1_source_class_proposal(
            source_class_proposal
        )
        verdict = evaluation["verdict"]
        reasons = tuple(evaluation["reasons"])
    else:
        verdict = SOURCE_CLASS_VERDICT_AWAIT
        reasons = ("await_crypto_d1_acquire_decision_gate",)

    state = (
        SOURCE_CLASS_STATE_ACTIVE
        if contract_active
        else SOURCE_CLASS_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = NEXT_GATE_AWAIT_CRYPTO_D1_ACQUIRE_DECISION
    elif verdict == SOURCE_CLASS_VERDICT_APPROVED:
        next_gate = (
            NEXT_GATE_CRYPTO_D1_SOURCE_ACQUISITION_PLAN_CONTRACT_REQUIRED
        )
    elif verdict == SOURCE_CLASS_VERDICT_NEEDS_MORE_INFO:
        next_gate = NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_FIX_REQUIRED
    elif verdict == SOURCE_CLASS_VERDICT_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_PARKED
    else:
        next_gate = NEXT_GATE_CRYPTO_D1_SOURCE_CLASS_REJECTED

    echoed_proposal = (
        dict(source_class_proposal)
        if isinstance(source_class_proposal, dict)
        else {}
    )

    contract = {
        "schema_version": SOURCE_CLASS_SCHEMA_VERSION,
        "crypto_d1_acquire_decision_schema_version": ACQUIRE_SCHEMA_VERSION,
        "idea_id": _field(acquire_contract, "idea_id"),
        "title": _field(acquire_contract, "title"),
        "label": DEFAULT_SOURCE_CLASS_LABEL,
        "status": SOURCE_CLASS_STATUS,
        "stage": "CRYPTO_D1_SOURCE_CLASS_ONLY",
        "mode": "RESEARCH_ONLY",
        "crypto_d1_source_class_contract_active": contract_active,
        "crypto_d1_source_class_contract_state": state,
        "crypto_d1_acquire_decision_contract_active": bool(acq_active),
        "crypto_d1_acquire_decision": acq_decision,
        "crypto_d1_acquire_decision_next_gate": acq_next_gate,
        "asset_lane": _field(acquire_contract, "asset_lane"),
        "timeframe_lane": _field(acquire_contract, "timeframe_lane"),
        "source_class_proposal_reference_placeholder": (
            _SOURCE_CLASS_PROPOSAL_REFERENCE_PLACEHOLDER
        ),
        "source_class_verdict": verdict,
        "source_class_verdict_reasons": reasons,
        "evaluated_source_class_proposal": echoed_proposal,
        "allowed_source_class_verdicts": ALLOWED_SOURCE_CLASS_VERDICTS,
        "required_source_class_fields": REQUIRED_SOURCE_CLASS_FIELDS,
        "allowed_asset_universe": ALLOWED_ASSET_UNIVERSE,
        "parked_market_types": PARKED_MARKET_TYPES,
        "allowed_venue_classes": ALLOWED_VENUE_CLASSES,
        "allowed_source_access_modes": ALLOWED_SOURCE_ACCESS_MODES,
        "required_candle_fields": REQUIRED_CANDLE_FIELDS,
        "allowed_timeframe": ALLOWED_TIMEFRAME,
        "forbidden_source_class_capabilities": (
            FORBIDDEN_SOURCE_CLASS_CAPABILITIES
        ),
        "source_class_verdict_rationale_placeholder": (
            _SOURCE_CLASS_VERDICT_RATIONALE_PLACEHOLDER
        ),
        "blocked_execution_items": BLOCKED_EXECUTION_ITEMS,
        "source_class_blocked_capabilities": (
            _SOURCE_CLASS_BLOCKED_CAPABILITIES
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
        "crypto_d1_acquire_decision_contract": (
            acquire_contract if isinstance(acquire_contract, dict) else {}
        ),
    }
    contract["validation"] = _validate(contract)
    return contract


def render_crypto_d1_source_class_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 source class
    contract template. Pure; writes no file. Informational only."""
    verdicts = contract.get("allowed_source_class_verdicts") or ()
    fields = contract.get("required_source_class_fields") or ()
    assets = contract.get("allowed_asset_universe") or ()
    parked = contract.get("parked_market_types") or ()
    venues = contract.get("allowed_venue_classes") or ()
    access_modes = contract.get("allowed_source_access_modes") or ()
    candle_fields = contract.get("required_candle_fields") or ()
    timeframe = contract.get("allowed_timeframe") or ()
    forbidden = contract.get("forbidden_source_class_capabilities") or ()
    reasons = contract.get("source_class_verdict_reasons") or ()
    blocked_execution = contract.get("blocked_execution_items") or ()
    source_blocked = contract.get("source_class_blocked_capabilities") or ()
    remaining_blocked = (
        contract.get("remaining_real_world_capabilities_blocked") or ()
    )
    next_steps = contract.get("human_operator_required_next_steps") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append("# Strategy Factory Crypto-D1 Source Class Contract")
    lines.append("")
    lines.append(
        "Template only: this is a "
        "crypto-d1-source-class-contract-only, paper-only, offline-spec-only, "
        "no-live-api, no-data-acquisition, no-qa-run, no-baseline-run, "
        "no-data-inspection, no-real-strategy-intake-yet, research-only, and "
        "execution-free template -- it records only a paper source-class "
        "verdict, is not wired into any runtime state, writes no report file, "
        "acquires no data, inspects no data, connects to no venue, names only "
        "placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Acquire schema: "
        f"`{contract.get('crypto_d1_acquire_decision_schema_version', '')}`"
    )
    lines.append(f"Idea ID: {contract.get('idea_id', '')}")
    lines.append(f"Title: {contract.get('title', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append("Stage: CRYPTO_D1_SOURCE_CLASS_ONLY")
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 source class contract active: "
        f"{contract.get('crypto_d1_source_class_contract_active', '')}"
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_source_class_contract_state', '')}"
    )
    lines.append(f"Verdict: {contract.get('source_class_verdict', '')}")
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append(f"Asset lane: {contract.get('asset_lane', '')}")
    lines.append(f"Timeframe lane: {contract.get('timeframe_lane', '')}")
    lines.append("")
    lines.append("## Source Class Proposal Reference")
    lines.append("")
    lines.append(
        "Source class proposal reference: "
        f"{contract.get('source_class_proposal_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Source Class Verdict Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Source Class Verdicts")
    lines.append("")
    for x in verdicts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Source Class Fields")
    lines.append("")
    for x in fields:
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
    lines.append("## Allowed Venue Classes")
    lines.append("")
    for x in venues:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Source Access Modes")
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
    lines.append("## Forbidden Source Class Capabilities")
    lines.append("")
    for x in forbidden:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Source Class Verdict Rationale")
    lines.append("")
    lines.append(
        "Source class verdict rationale: "
        f"{contract.get('source_class_verdict_rationale_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Blocked Execution Items")
    lines.append("")
    for x in blocked_execution:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Source Class Blocked Capabilities")
    lines.append("")
    for cap in source_blocked:
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
        "- A human operator must confirm the source class before any "
        "acquisition plan is drafted."
    )
    lines.append("- No automated step may proceed without human sign-off.")
    return "\n".join(lines)

"""SPARTA Offline Strategy Factory - CRYPTO-D1 STRATEGY CANDIDATE PROTOCOL
CONTRACT.

A PURE, stdlib-only *read-only paper contract* builder and evaluator that turns
the Crypto-D1 Strategy Candidate Protocol v1 (defined in
``strategy_factory_crypto_d1_next_research_protocol``) into a contract which
VALIDATES whether a proposed candidate-strategy *research plan* follows that
protocol. It consumes the protocol's stable constants and, only when the
upstream protocol is clearly the expected one (protocol_id ==
CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1, protocol_mode == RESEARCH_ONLY,
read_only is True, executes is False, next_required_action ==
BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT), evaluates a proposed
research-plan packet on paper and returns a deterministic verdict describing
whether the plan is ready, needs more info, must be rejected, or is parked.

It evaluates the SHAPE of a proposed plan only. It does NOT acquire, fetch,
inspect, load, validate, transform, or compute on any data, does not run QA,
does not run a baseline, does not backtest, does not simulate, produces no trade
signal, reaches no broker / exchange / order / account / API surface, trades no
paper and no live, triggers no automation, writes no runtime, registry, ledger,
dashboard, or report state, opens no network, spawns no child process, writes no
file, reads no file, lists no directory, records no timestamp, mints no random
id, reads no environment, and dynamically imports nothing.

Reaching a STRATEGY_CANDIDATE_PROTOCOL_READY verdict unlocks NOTHING real. It
only records, on paper, that a proposed research plan matches the protocol's
scope (BTC/ETH/SOL spot, D1, all four candidate families, every real-world
capability still blocked) -- and even that still requires a separate, later,
human step to build the next research-only bundle, which this module does not
authorize. Any upstream protocol shape that is missing, malformed, in the wrong
mode, executable, non-read-only, or not the expected protocol yields the
AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINITION verdict.

Public API:
  - STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION
  - DEFAULT_STRATEGY_CANDIDATE_PROTOCOL_LABEL
  - STRATEGY_CANDIDATE_PROTOCOL_STATUS
  - STRATEGY_CANDIDATE_PROTOCOL_SAFETY_POSTURE
  - STRATEGY_CANDIDATE_PROTOCOL_STATE_ACTIVE
  - STRATEGY_CANDIDATE_PROTOCOL_STATE_BLOCKED
  - STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY
  - STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO
  - STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED
  - STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED
  - STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT
  - ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_VERDICTS
  - UPSTREAM_REQUIRED_PROTOCOL_ID
  - UPSTREAM_REQUIRED_PROTOCOL_MODE
  - UPSTREAM_REQUIRED_PROTOCOL_NEXT_ACTION
  - STRATEGY_CANDIDATE_PROTOCOL_NEXT_REQUIRED_ACTION
  - STRATEGY_CANDIDATE_PROTOCOL_CURRENT_STAGE
  - DECISION_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_REQUIRED
  - NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_READY
  - NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_PARKED
  - NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINITION
  - REQUIRED_RESEARCH_UNIVERSE
  - REQUIRED_MARKET_TYPE
  - REQUIRED_TIMEFRAME
  - REQUIRED_STRATEGY_FAMILIES
  - REQUIRED_STRATEGY_CANDIDATE_PROTOCOL_FIELDS
  - STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_TEXT_FIELDS
  - STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_AFFIRMATIONS
  - STRATEGY_CANDIDATE_PROTOCOL_FORBIDDEN_ALLOW_FLAGS
  - ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_MODES
  - AUTOMATED_APPROVAL_MARKERS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - evaluate_crypto_d1_strategy_candidate_protocol(packet)
  - build_crypto_d1_strategy_candidate_protocol_contract(protocol, candidate_plan_packet=None)
  - validate_crypto_d1_strategy_candidate_protocol_contract(contract)
  - render_crypto_d1_strategy_candidate_protocol_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_next_research_protocol import (
    PROTOCOL_ID as _PROTOCOL_ID,
    PROTOCOL_NAME as _PROTOCOL_NAME,
    PROTOCOL_MODE as _PROTOCOL_MODE,
    PROTOCOL_SCHEMA_VERSION as _PROTOCOL_SCHEMA_VERSION,
    RESEARCH_UNIVERSE as _PROTOCOL_UNIVERSE,
    MARKET_TYPE as _PROTOCOL_MARKET_TYPE,
    TIMEFRAME as _PROTOCOL_TIMEFRAME,
    NEXT_REQUIRED_ACTION as _PROTOCOL_NEXT_ACTION,
    get_candidate_strategy_families as _protocol_candidate_families,
)

__all__ = [
    "STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION",
    "DEFAULT_STRATEGY_CANDIDATE_PROTOCOL_LABEL",
    "STRATEGY_CANDIDATE_PROTOCOL_STATUS",
    "STRATEGY_CANDIDATE_PROTOCOL_SAFETY_POSTURE",
    "STRATEGY_CANDIDATE_PROTOCOL_STATE_ACTIVE",
    "STRATEGY_CANDIDATE_PROTOCOL_STATE_BLOCKED",
    "STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY",
    "STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO",
    "STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED",
    "STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED",
    "STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT",
    "ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_VERDICTS",
    "UPSTREAM_REQUIRED_PROTOCOL_ID",
    "UPSTREAM_REQUIRED_PROTOCOL_MODE",
    "UPSTREAM_REQUIRED_PROTOCOL_NEXT_ACTION",
    "STRATEGY_CANDIDATE_PROTOCOL_NEXT_REQUIRED_ACTION",
    "STRATEGY_CANDIDATE_PROTOCOL_CURRENT_STAGE",
    "DECISION_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_READY",
    "NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_FIX_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_PARKED",
    "NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_REJECTED",
    "NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINITION",
    "REQUIRED_RESEARCH_UNIVERSE",
    "REQUIRED_MARKET_TYPE",
    "REQUIRED_TIMEFRAME",
    "REQUIRED_STRATEGY_FAMILIES",
    "REQUIRED_STRATEGY_CANDIDATE_PROTOCOL_FIELDS",
    "STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_TEXT_FIELDS",
    "STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_AFFIRMATIONS",
    "STRATEGY_CANDIDATE_PROTOCOL_FORBIDDEN_ALLOW_FLAGS",
    "ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_MODES",
    "AUTOMATED_APPROVAL_MARKERS",
    "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "evaluate_crypto_d1_strategy_candidate_protocol",
    "build_crypto_d1_strategy_candidate_protocol_contract",
    "validate_crypto_d1_strategy_candidate_protocol_contract",
    "render_crypto_d1_strategy_candidate_protocol_contract_markdown",
]

STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_strategy_candidate_protocol_contract.v1"
)
DEFAULT_STRATEGY_CANDIDATE_PROTOCOL_LABEL = (
    "Strategy Factory Crypto-D1 Strategy Candidate Protocol Contract"
)
STRATEGY_CANDIDATE_PROTOCOL_STATUS = (
    "READ_ONLY_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT"
)

STRATEGY_CANDIDATE_PROTOCOL_STATE_ACTIVE = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_ACTIVE"
)
STRATEGY_CANDIDATE_PROTOCOL_STATE_BLOCKED = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_BLOCKED"
)

STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY = "STRATEGY_CANDIDATE_PROTOCOL_READY"
STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO = (
    "STRATEGY_CANDIDATE_PROTOCOL_NEEDS_MORE_INFO"
)
STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED = (
    "STRATEGY_CANDIDATE_PROTOCOL_REJECTED"
)
STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED = (
    "STRATEGY_CANDIDATE_PROTOCOL_PARKED"
)
STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT = (
    "AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINITION"
)

ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_VERDICTS: tuple[str, ...] = (
    STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY,
    STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO,
    STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED,
    STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED,
    STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT,
)

# The exact upstream protocol signal this contract activates from. The contract
# only becomes active when the proposed-against protocol is clearly the
# Crypto-D1 Strategy Candidate Protocol v1, in RESEARCH_ONLY mode, read-only,
# non-executing, and asking for exactly this contract to be built.
UPSTREAM_REQUIRED_PROTOCOL_ID = _PROTOCOL_ID
UPSTREAM_REQUIRED_PROTOCOL_MODE = _PROTOCOL_MODE
UPSTREAM_REQUIRED_PROTOCOL_NEXT_ACTION = _PROTOCOL_NEXT_ACTION

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering
# this contract is a separate, later block; importing the registry would also
# risk a circular import).
STRATEGY_CANDIDATE_PROTOCOL_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT"
)
STRATEGY_CANDIDATE_PROTOCOL_CURRENT_STAGE = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_REQUIRED"
)

# The conceptual decision this contract fulfills once it is active.
DECISION_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_REQUIRED = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_REQUIRED"
)

# Next-gate outcomes by verdict. A READY verdict is still only a paper-shape
# verdict; building the next research-only bundle is a separate, later, human
# step.
NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_READY = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_READY_SEPARATE_HUMAN_NEXT_STEP_"
    "REQUIRED"
)
NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_FIX_REQUIRED = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_PARKED = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_PARKED"
)
NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_REJECTED = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINITION = (
    "AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINITION"
)

# Required research scope, read straight from the protocol so the contract can
# never drift from the protocol it enforces.
REQUIRED_RESEARCH_UNIVERSE: tuple[str, ...] = tuple(
    str(asset).strip().upper() for asset in _PROTOCOL_UNIVERSE
)
REQUIRED_MARKET_TYPE = str(_PROTOCOL_MARKET_TYPE).strip().upper()
REQUIRED_TIMEFRAME = str(_PROTOCOL_TIMEFRAME).strip().upper()
REQUIRED_STRATEGY_FAMILIES: tuple[str, ...] = tuple(
    str(family.get("family_id")).strip().upper()
    for family in _protocol_candidate_families()
    if isinstance(family, dict) and family.get("family_id")
)

_REQUIRED_UNIVERSE_SET: frozenset[str] = frozenset(REQUIRED_RESEARCH_UNIVERSE)
_REQUIRED_FAMILY_SET: frozenset[str] = frozenset(REQUIRED_STRATEGY_FAMILIES)

# Accepted scalar values for the committed market-type and timeframe fields. A
# committed value outside these sets is a hard scope violation (e.g. perps,
# futures, margin, funding, or an intraday timeframe).
_ALLOWED_MARKET_TYPE_VALUES: frozenset[str] = frozenset(
    {"spot", "spot_only", "spot-only", "spot only"}
)
_ALLOWED_TIMEFRAME_VALUES: frozenset[str] = frozenset(
    {"d1", "1d", "daily", "day", "d", "daily_candles", "daily candles"}
)

# Read-only, all-false safety posture. Every capability flag stays False; this
# contract evaluates the shape of a proposed plan and unlocks nothing.
STRATEGY_CANDIDATE_PROTOCOL_SAFETY_POSTURE: dict[str, bool] = {
    "acquires_data": False,
    "fetches_data": False,
    "inspects_market_data": False,
    "loads_dataset": False,
    "runs_qa": False,
    "runs_baseline": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "generates_trade_signal": False,
    "paper_or_live": False,
    "order_logic": False,
    "connects_exchange_or_broker": False,
    "account_access": False,
    "uses_api_keys": False,
    "triggers_automation": False,
    "writes_runtime_state": False,
    "writes_registry": False,
    "writes_dashboard": False,
    "writes_ledger": False,
}

# Strings that mark a non-human / automated decider. A packet authored by any of
# these is rejected: only a human operator may record this paper decision.
AUTOMATED_APPROVAL_MARKERS: tuple[str, ...] = (
    "auto",
    "automated",
    "automation",
    "bot",
    "agent",
    "llm",
    "ai",
    "autopilot",
    "script",
    "cron",
    "scheduler",
    "system",
    "robot",
)

# Allowed research-mode enumerations. A present-but-disallowed mode is a hard
# REJECTED (the plan tries to operate outside research-only scope).
ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_MODES: tuple[str, ...] = (
    "research_only",
    "research-only",
    "research only",
)

# Descriptive text fields a human must record on a proposed candidate-plan
# packet. Absent -> NEEDS_MORE_INFO.
STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
    "candidate_protocol_packet_id",
    "upstream_protocol_id",
    "protocol_name",
    "research_universe",
    "market_type",
    "timeframe",
    "proposed_strategy_families",
    "candidate_family_scope",
    "candidate_family_weights_or_priority",
    "family_comparison_method",
    "next_step_boundary",
    "rationale",
)

# Affirmation flags the packet must carry (each affirmed True). The "no_*" flags
# are positive confirmations that the plan does NOT permit the named real-world
# thing. A present-but-not-affirmed value is a request to admit or allow that
# thing -- a hard REJECTED. An absent value is a missing requirement
# (NEEDS_MORE_INFO).
STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_AFFIRMATIONS: tuple[str, ...] = (
    "future_data_requirements_acknowledged",
    "future_validation_steps_acknowledged",
    "pass_watch_fail_rules_acknowledged",
    "safety_gates_acknowledged",
    "human_operator_review_required",
    "research_only_acknowledgement",
    "no_execution_acknowledgement",
    "no_real_data_acquisition",
    "no_data_fetch",
    "no_data_inspection",
    "no_dataset_loading",
    "no_qa_run",
    "no_baseline_run",
    "no_backtest_run",
    "no_simulation_run",
    "no_trade_signal",
    "no_paper_live",
    "no_broker_exchange",
    "no_order_capability",
    "no_account_access",
    "no_api_keys",
    "no_automation_trigger",
    "no_runtime_write",
    "no_registry_write",
    "no_dashboard_write",
)

# Every required True-flag. Present-but-not-affirmed -> REJECTED; absent ->
# NEEDS_MORE_INFO.
_REQUIRED_TRUE_FLAGS: tuple[str, ...] = (
    STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_AFFIRMATIONS
)

# Full set of required candidate-plan packet fields.
REQUIRED_STRATEGY_CANDIDATE_PROTOCOL_FIELDS: tuple[str, ...] = (
    STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_TEXT_FIELDS
    + STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_AFFIRMATIONS
)

# Positive allow/grant flags a candidate-plan packet must NOT request -- any
# truthy value forces a hard REJECTED (it tries to permit a real, dangerous
# capability, to actually run something, or to proceed to a real next contract).
STRATEGY_CANDIDATE_PROTOCOL_FORBIDDEN_ALLOW_FLAGS: tuple[str, ...] = (
    "allow_real_data_acquisition",
    "real_data_acquisition_allowed",
    "approves_real_data_acquisition",
    "acquires_data",
    "allow_data_fetch",
    "data_fetch_allowed",
    "approves_data_fetch",
    "fetches_data",
    "allow_data_inspection",
    "data_inspection_allowed",
    "inspects_market_data",
    "allow_dataset_load",
    "dataset_load_allowed",
    "allow_dataset_loading",
    "dataset_loading_allowed",
    "loads_dataset",
    "allow_qa_run",
    "qa_run_allowed",
    "runs_qa",
    "allow_baseline_run",
    "baseline_run_allowed",
    "runs_baseline",
    "allow_backtest_run",
    "backtest_run_allowed",
    "runs_backtest",
    "allow_simulation_run",
    "simulation_run_allowed",
    "runs_simulation",
    "allow_paper_live",
    "paper_live_allowed",
    "paper_or_live",
    "allow_broker_exchange",
    "broker_exchange_allowed",
    "connects_exchange_or_broker",
    "allow_order_capability",
    "order_capability_allowed",
    "order_logic",
    "allow_account_access",
    "account_access_allowed",
    "account_access",
    "allow_api_keys",
    "api_keys_allowed",
    "uses_api_keys",
    "allow_automation_trigger",
    "automation_trigger_allowed",
    "triggers_automation",
    "allow_runtime_write",
    "runtime_write_allowed",
    "writes_runtime_state",
    "allow_registry_write",
    "registry_write_allowed",
    "writes_registry",
    "allow_dashboard_write",
    "dashboard_write_allowed",
    "writes_dashboard",
    "allow_ledger_write",
    "ledger_write_allowed",
    "writes_ledger",
    "allow_trade_signal",
    "trade_signal_allowed",
    "approves_trade_signal",
    "generates_trade_signal",
    "produces_trade_signal",
    "produces_trade_signals",
    "allow_market_data_validation",
    "market_data_validation_allowed",
    "validates_market_data",
    "allow_intraday",
    "intraday_allowed",
    "uses_intraday",
    "allow_perps",
    "perps_allowed",
    "uses_perps",
    "uses_futures",
    "uses_funding",
    "uses_margin",
    "uses_leverage",
    "non_spot_allowed",
    "execution_authorized",
    "live_execution_authorized",
    "executes_plan",
    "autopilot_enabled",
    "side_effects_allowed",
    "allow_side_effects",
    "proceed_to_real_acquisition",
    "proceed_to_data_fetch",
    "proceed_to_execution",
    "proceed_to_real_run",
    "proceed_to_real_contract",
    "allow_next_real_contract",
    "next_real_contract_allowed",
    "approves_real_next_contract",
    "approves_real_acquisition",
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
    "child_process",
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

# Candidate-protocol-phase blocked capabilities (named for this lane).
_CANDIDATE_PROTOCOL_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "crypto_d1_real_data_acquisition",
    "crypto_d1_data_fetch",
    "crypto_d1_data_inspection",
    "crypto_d1_dataset_load",
    "crypto_d1_qa_run",
    "crypto_d1_baseline_run",
    "crypto_d1_backtest",
    "crypto_d1_simulation",
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

# Real-world capabilities that remain blocked even on a READY verdict.
REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED: tuple[str, ...] = (
    "real_data_acquisition",
    "data_fetch",
    "data_inspection",
    "dataset_loading",
    "qa_run",
    "baseline_run",
    "backtest_run",
    "simulation_run",
    "trade_signal_production",
    "paper_or_live_trading",
    "broker_or_exchange_connection",
    "order_capability",
    "account_access",
    "api_key_use",
    "automation_trigger",
    "runtime_write",
    "registry_write",
    "dashboard_write",
    "ledger_write",
)

_CANDIDATE_PROTOCOL_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 strategy candidate-plan packet is a paper placeholder describing "
    "a proposed research plan: which spot assets, which timeframe, and which "
    "candidate strategy families a future research-only lane would compare, and "
    "how -- it proposes on paper only, runs nothing, acquires nothing, inspects "
    "nothing, and executes nothing."
)

_CANDIDATE_PROTOCOL_VERDICT_RATIONALE_PLACEHOLDER = (
    "Strategy candidate-protocol verdict rationale is a paper placeholder for a "
    "human-recorded judgement of whether a proposed research plan follows the "
    "Crypto-D1 Strategy Candidate Protocol v1, and its supporting reason."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 strategy candidate protocol contract template and is "
    "execution-free.",
    "It validates, on paper, whether a proposed candidate-strategy research "
    "plan follows the Crypto-D1 Strategy Candidate Protocol v1; it runs no "
    "research.",
    "It evaluates a paper candidate-plan packet only and writes no report file.",
    "It writes no runtime state, acquires no data, inspects no data, and loads "
    "no dataset.",
    "A READY verdict means only that a proposed plan matches the protocol scope "
    "(BTC/ETH/SOL spot, D1, all four candidate families) and blocks every "
    "real-world capability; it authorizes no data work and no execution.",
    "It connects to no exchange, broker, or live venue and uses no API keys.",
    "QA, baseline, backtest, simulation, paper, and live all stay blocked.",
    "It produces no trade signal and validates no market data.",
    "A human operator alone may record this candidate-plan verdict; no "
    "automated decider is accepted.",
    "Any READY verdict still requires a separate, later, human step to build "
    "the next research-only bundle, which this template does not authorize.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human operator must record a candidate-plan verdict with a supporting "
    "rationale on paper.",
    "A human operator must confirm the plan stays research-only and paper-only "
    "and performs no data acquisition, fetch, inspection, dataset loading, QA, "
    "baseline, backtest, simulation, trade-signal production, market-data "
    "validation, paper/live, broker/exchange, order, account, API, automation, "
    "or runtime/registry/dashboard writes.",
    "A human operator must confirm the proposed universe is exactly BTC/ETH/"
    "SOL spot on the D1 timeframe.",
    "A human operator must confirm the plan compares all four candidate "
    "strategy families, not a single favored idea dressed up as a comparison.",
    "No automated step may proceed without human sign-off.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "crypto_d1_next_research_protocol_schema_version",
    "label",
    "status",
    "stage",
    "mode",
    "protocol_id",
    "protocol_name",
    "crypto_d1_strategy_candidate_protocol_contract_active",
    "crypto_d1_strategy_candidate_protocol_contract_state",
    "crypto_d1_next_research_protocol_recognized",
    "upstream_protocol_id",
    "upstream_protocol_mode",
    "upstream_protocol_next_required_action",
    "strategy_candidate_protocol_contract_required",
    "strategy_candidate_protocol_next_required_action",
    "strategy_candidate_protocol_current_stage",
    "required_research_universe",
    "required_market_type",
    "required_timeframe",
    "required_strategy_families",
    "candidate_plan_packet_reference_placeholder",
    "strategy_candidate_protocol_verdict",
    "strategy_candidate_protocol_verdict_reasons",
    "evaluated_candidate_plan_packet",
    "allowed_strategy_candidate_protocol_verdicts",
    "required_strategy_candidate_protocol_fields",
    "strategy_candidate_protocol_required_text_fields",
    "strategy_candidate_protocol_required_affirmations",
    "strategy_candidate_protocol_forbidden_allow_flags",
    "allowed_strategy_candidate_protocol_modes",
    "automated_approval_markers",
    "strategy_candidate_protocol_verdict_rationale_placeholder",
    "candidate_protocol_blocked_capabilities",
    "remaining_real_world_capabilities_blocked",
    "blocked_capabilities",
    "safety_posture",
    "next_gate",
    "operator_notes",
    "human_operator_required_next_steps",
    "human_approval_required",
    "read_only",
    "executes",
) + _AUTH_FLAGS


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(STRATEGY_CANDIDATE_PROTOCOL_SAFETY_POSTURE)


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
            "reviewed", "verified", "prohibited", "blocked",
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


def _upper_token_set(value: Any) -> frozenset[str]:
    """Normalize a list/tuple/string of symbols into an upper-cased token set.

    Reads only the given value; never raises."""
    tokens: list[str] = []
    if isinstance(value, (list, tuple, set, frozenset)):
        items: list[Any] = list(value)
    elif isinstance(value, str):
        items = value.replace(",", " ").replace("/", " ").split()
    else:
        items = []
    for item in items:
        if isinstance(item, str):
            token = item.strip().upper()
            if token:
                tokens.append(token)
    return frozenset(tokens)


def _reject_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return any hard REJECTED reasons: a permitted dangerous capability, an
    admitted/relaxed affirmation, a disallowed mode, an off-scope committed
    market-type/timeframe, non-core assets, a non-protocol or single-favorite
    strategy family, an automated decider, or granted authority."""
    reasons: list[str] = []

    for flag in STRATEGY_CANDIDATE_PROTOCOL_FORBIDDEN_ALLOW_FLAGS:
        if _truthy(packet.get(flag)):
            reasons.append(f"forbidden_allow:{flag}")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag in packet and not _affirm(packet.get(flag)):
            reasons.append(f"affirmation_relaxed:{flag}")

    mode = packet.get("research_mode")
    if not _present(mode):
        mode = packet.get("mode")
    if _present(mode) and _scalar(mode) not in (
        ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_MODES
    ):
        reasons.append("disallowed_mode")

    market_type = packet.get("market_type")
    if _present(market_type) and (
        _scalar(market_type) not in _ALLOWED_MARKET_TYPE_VALUES
    ):
        reasons.append("disallowed_market_type")

    timeframe = packet.get("timeframe")
    if _present(timeframe) and (
        _scalar(timeframe) not in _ALLOWED_TIMEFRAME_VALUES
    ):
        reasons.append("disallowed_timeframe")

    universe = _upper_token_set(packet.get("research_universe"))
    extras = universe - _REQUIRED_UNIVERSE_SET
    if extras:
        reasons.append("non_core_assets_in_universe")

    families = _upper_token_set(packet.get("proposed_strategy_families"))
    unknown = families - _REQUIRED_FAMILY_SET
    if unknown:
        reasons.append("non_protocol_strategy_family")
    if len(families) == 1 and _present(
        packet.get("family_comparison_method")
    ):
        reasons.append("single_family_masquerading_as_comparison")

    for key in (
        "operator_type",
        "decision_author_type",
        "decision_method",
        "decision_source",
        "authored_by_type",
        "operator_name_or_id",
    ):
        if _scalar(packet.get(key)) in AUTOMATED_APPROVAL_MARKERS:
            reasons.append(f"automated_decider:{key}")

    for key in ("grants_capabilities", "authorizes", "granted_capabilities"):
        listed = packet.get(key)
        if isinstance(listed, (list, tuple)) and len(listed) > 0:
            reasons.append(f"grants_listed:{key}")

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
            reasons.append("operator_parked_strategy_candidate_protocol")
            break

    if _scalar(packet.get("operator_decision")) in park_values:
        reasons.append("operator_decision_parked")
    if _scalar(packet.get("candidate_plan_decision")) in park_values:
        reasons.append("candidate_plan_decision_parked")

    return tuple(reasons)


def _missing_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return unmet requirements for an otherwise-safe candidate-plan packet:
    absent text fields, unaffirmed flags, an incomplete BTC/ETH/SOL universe,
    or fewer than all four candidate strategy families."""
    missing: list[str] = []

    for key in STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_TEXT_FIELDS:
        if not _present(packet.get(key)):
            missing.append(f"{key}_required")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag not in packet:
            missing.append(f"{flag}_must_be_affirmed_true")

    universe = _upper_token_set(packet.get("research_universe"))
    for asset in REQUIRED_RESEARCH_UNIVERSE:
        if asset not in universe:
            missing.append(f"research_universe_missing_{asset}")

    if _present(packet.get("market_type")) and (
        _scalar(packet.get("market_type")) not in _ALLOWED_MARKET_TYPE_VALUES
    ):
        # Handled as REJECTED elsewhere; not a missing reason.
        pass

    families = _upper_token_set(packet.get("proposed_strategy_families"))
    for family in REQUIRED_STRATEGY_FAMILIES:
        if family not in families:
            missing.append(f"strategy_family_missing_{family}")

    return tuple(missing)


def evaluate_crypto_d1_strategy_candidate_protocol(
    packet: Any,
) -> dict[str, Any]:
    """Return a deterministic verdict for a proposed candidate-plan packet
    against the Crypto-D1 Strategy Candidate Protocol v1. Pure; no I/O, no
    mutation, no timestamp, no random id. Unknown/malformed inputs never raise.
    The verdict is one of STRATEGY_CANDIDATE_PROTOCOL_READY,
    STRATEGY_CANDIDATE_PROTOCOL_NEEDS_MORE_INFO,
    STRATEGY_CANDIDATE_PROTOCOL_REJECTED, or
    STRATEGY_CANDIDATE_PROTOCOL_PARKED. It evaluates the SHAPE of a proposed
    research plan only and unlocks nothing. REJECTED (permits a dangerous
    capability / admits a relaxed affirmation / off-scope committed value /
    non-core asset / non-protocol or single-favorite family / automated decider /
    authority-granting) is checked before parking, and parking before
    completeness, so an unsafe plan is rejected even when it would otherwise park
    or merely need more info."""
    p = packet if isinstance(packet, dict) else {}

    if not p:
        return {
            "verdict": STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO,
            "reasons": ("strategy_candidate_protocol_packet_missing",),
        }

    rejected = _reject_reasons(p)
    if rejected:
        return {
            "verdict": STRATEGY_CANDIDATE_PROTOCOL_VERDICT_REJECTED,
            "reasons": rejected,
        }

    park = _park_reasons(p)
    if park:
        return {
            "verdict": STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED,
            "reasons": park,
        }

    missing = _missing_reasons(p)
    if not missing:
        return {
            "verdict": STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY,
            "reasons": (
                "research_only_candidate_plan_fully_specified_follows_protocol_"
                "btc_eth_sol_spot_d1_all_four_families_and_blocks_every_real_"
                "world_capability",
            ),
        }

    return {
        "verdict": STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO,
        "reasons": missing,
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_ONLY"
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
        tuple(safe.get("allowed_strategy_candidate_protocol_verdicts") or ())
        == ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_VERDICTS
    )
    fields_ok = (
        tuple(safe.get("required_strategy_candidate_protocol_fields") or ())
        == REQUIRED_STRATEGY_CANDIDATE_PROTOCOL_FIELDS
    )
    text_fields_ok = (
        tuple(safe.get("strategy_candidate_protocol_required_text_fields")
              or ())
        == STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_TEXT_FIELDS
    )
    affirmations_ok = (
        tuple(safe.get("strategy_candidate_protocol_required_affirmations")
              or ())
        == STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_AFFIRMATIONS
    )
    forbidden_flags_ok = (
        tuple(safe.get("strategy_candidate_protocol_forbidden_allow_flags")
              or ())
        == STRATEGY_CANDIDATE_PROTOCOL_FORBIDDEN_ALLOW_FLAGS
    )
    modes_ok = (
        tuple(safe.get("allowed_strategy_candidate_protocol_modes") or ())
        == ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_MODES
    )
    markers_ok = (
        tuple(safe.get("automated_approval_markers") or ())
        == AUTOMATED_APPROVAL_MARKERS
    )
    universe_ok = (
        tuple(safe.get("required_research_universe") or ())
        == REQUIRED_RESEARCH_UNIVERSE
    )
    families_ok = (
        tuple(safe.get("required_strategy_families") or ())
        == REQUIRED_STRATEGY_FAMILIES
    )
    market_ok = safe.get("required_market_type") == REQUIRED_MARKET_TYPE
    timeframe_ok = safe.get("required_timeframe") == REQUIRED_TIMEFRAME
    remaining_blocked_ok = (
        tuple(safe.get("remaining_real_world_capabilities_blocked") or ())
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )
    verdict_value_ok = (
        safe.get("strategy_candidate_protocol_verdict")
        in ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_VERDICTS
    )
    blocked_present_ok = (
        len(tuple(safe.get("candidate_protocol_blocked_capabilities") or ()))
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
        and modes_ok
        and markers_ok
        and universe_ok
        and families_ok
        and market_ok
        and timeframe_ok
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
        "allowed_strategy_candidate_protocol_verdicts_ok": verdicts_ok,
        "required_strategy_candidate_protocol_fields_ok": fields_ok,
        "strategy_candidate_protocol_required_text_fields_ok": text_fields_ok,
        "strategy_candidate_protocol_required_affirmations_ok": affirmations_ok,
        "strategy_candidate_protocol_forbidden_allow_flags_ok": (
            forbidden_flags_ok
        ),
        "allowed_strategy_candidate_protocol_modes_ok": modes_ok,
        "automated_approval_markers_ok": markers_ok,
        "required_research_universe_ok": universe_ok,
        "required_strategy_families_ok": families_ok,
        "required_market_type_ok": market_ok,
        "required_timeframe_ok": timeframe_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "strategy_candidate_protocol_verdict_value_ok": verdict_value_ok,
        "candidate_protocol_blocked_capabilities_present": blocked_present_ok,
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_strategy_candidate_protocol_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 strategy candidate
    protocol contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_strategy_candidate_protocol_contract(
    protocol: Any,
    candidate_plan_packet: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 strategy candidate
    protocol contract template plus a paper verdict for a proposed
    candidate-plan packet.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import.
    Unknown/malformed inputs never raise. The contract becomes active
    (crypto_d1_strategy_candidate_protocol_contract_active=True) solely when the
    upstream protocol dict is clearly the Crypto-D1 Strategy Candidate Protocol
    v1: protocol_id == CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1, protocol_mode ==
    RESEARCH_ONLY, read_only is True, executes is False, and next_required_action
    == BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT. When inactive, the
    verdict is AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINITION regardless
    of the packet. Even when active and READY, every authorization field stays
    False -- it evaluates the SHAPE of a proposed plan only, runs nothing,
    acquires nothing, connects to nothing, approves no QA, no baseline, no
    backtest, produces no trade signal, validates no market data, writes no
    report file, writes no runtime state, names only placeholders, and grants
    nothing. Returned dicts are fresh."""
    proto = protocol if isinstance(protocol, dict) else {}

    proto_id = _field(proto, "protocol_id")
    proto_mode = _field(proto, "protocol_mode")
    proto_next = _field(proto, "next_required_action")
    read_only_ok = proto.get("read_only") is True
    executes_false = proto.get("executes") is False
    id_ok = proto_id == UPSTREAM_REQUIRED_PROTOCOL_ID
    mode_ok = proto_mode == UPSTREAM_REQUIRED_PROTOCOL_MODE
    next_ok = proto_next == UPSTREAM_REQUIRED_PROTOCOL_NEXT_ACTION

    contract_active = bool(
        id_ok and mode_ok and next_ok and read_only_ok and executes_false
    )

    if contract_active:
        evaluation = evaluate_crypto_d1_strategy_candidate_protocol(
            candidate_plan_packet
        )
        verdict = evaluation["verdict"]
        reasons = tuple(evaluation["reasons"])
    else:
        verdict = STRATEGY_CANDIDATE_PROTOCOL_VERDICT_AWAIT
        reasons = (
            "await_crypto_d1_strategy_candidate_protocol_definition",
        )

    state = (
        STRATEGY_CANDIDATE_PROTOCOL_STATE_ACTIVE
        if contract_active
        else STRATEGY_CANDIDATE_PROTOCOL_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = (
            NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_DEFINITION
        )
    elif verdict == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_READY:
        next_gate = NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_READY
    elif verdict == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_NEEDS_MORE_INFO:
        next_gate = (
            NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_FIX_REQUIRED
        )
    elif verdict == STRATEGY_CANDIDATE_PROTOCOL_VERDICT_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_PARKED
    else:
        next_gate = NEXT_GATE_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_REJECTED

    strategy_candidate_protocol_contract_required = (
        DECISION_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_REQUIRED
        if contract_active
        else ""
    )

    echoed_packet = (
        dict(candidate_plan_packet)
        if isinstance(candidate_plan_packet, dict)
        else {}
    )

    contract = {
        "schema_version": STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION,
        "crypto_d1_next_research_protocol_schema_version": (
            _PROTOCOL_SCHEMA_VERSION
        ),
        "label": DEFAULT_STRATEGY_CANDIDATE_PROTOCOL_LABEL,
        "status": STRATEGY_CANDIDATE_PROTOCOL_STATUS,
        "stage": "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_ONLY",
        "mode": "RESEARCH_ONLY",
        "protocol_id": UPSTREAM_REQUIRED_PROTOCOL_ID,
        "protocol_name": _PROTOCOL_NAME,
        "crypto_d1_strategy_candidate_protocol_contract_active": (
            contract_active
        ),
        "crypto_d1_strategy_candidate_protocol_contract_state": state,
        "crypto_d1_next_research_protocol_recognized": contract_active,
        "upstream_protocol_id": proto_id,
        "upstream_protocol_mode": proto_mode,
        "upstream_protocol_next_required_action": proto_next,
        "strategy_candidate_protocol_contract_required": (
            strategy_candidate_protocol_contract_required
        ),
        "strategy_candidate_protocol_next_required_action": (
            STRATEGY_CANDIDATE_PROTOCOL_NEXT_REQUIRED_ACTION
        ),
        "strategy_candidate_protocol_current_stage": (
            STRATEGY_CANDIDATE_PROTOCOL_CURRENT_STAGE
        ),
        "required_research_universe": REQUIRED_RESEARCH_UNIVERSE,
        "required_market_type": REQUIRED_MARKET_TYPE,
        "required_timeframe": REQUIRED_TIMEFRAME,
        "required_strategy_families": REQUIRED_STRATEGY_FAMILIES,
        "candidate_plan_packet_reference_placeholder": (
            _CANDIDATE_PROTOCOL_REFERENCE_PLACEHOLDER
        ),
        "strategy_candidate_protocol_verdict": verdict,
        "strategy_candidate_protocol_verdict_reasons": reasons,
        "evaluated_candidate_plan_packet": echoed_packet,
        "allowed_strategy_candidate_protocol_verdicts": (
            ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_VERDICTS
        ),
        "required_strategy_candidate_protocol_fields": (
            REQUIRED_STRATEGY_CANDIDATE_PROTOCOL_FIELDS
        ),
        "strategy_candidate_protocol_required_text_fields": (
            STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_TEXT_FIELDS
        ),
        "strategy_candidate_protocol_required_affirmations": (
            STRATEGY_CANDIDATE_PROTOCOL_REQUIRED_AFFIRMATIONS
        ),
        "strategy_candidate_protocol_forbidden_allow_flags": (
            STRATEGY_CANDIDATE_PROTOCOL_FORBIDDEN_ALLOW_FLAGS
        ),
        "allowed_strategy_candidate_protocol_modes": (
            ALLOWED_STRATEGY_CANDIDATE_PROTOCOL_MODES
        ),
        "automated_approval_markers": AUTOMATED_APPROVAL_MARKERS,
        "strategy_candidate_protocol_verdict_rationale_placeholder": (
            _CANDIDATE_PROTOCOL_VERDICT_RATIONALE_PLACEHOLDER
        ),
        "candidate_protocol_blocked_capabilities": (
            _CANDIDATE_PROTOCOL_BLOCKED_CAPABILITIES
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
    }
    contract["validation"] = _validate(contract)
    return contract


def render_crypto_d1_strategy_candidate_protocol_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 strategy
    candidate protocol contract template. Pure; writes no file. Informational
    only."""
    verdicts = (
        contract.get("allowed_strategy_candidate_protocol_verdicts") or ()
    )
    fields = (
        contract.get("required_strategy_candidate_protocol_fields") or ()
    )
    text_fields = (
        contract.get("strategy_candidate_protocol_required_text_fields") or ()
    )
    affirmations = (
        contract.get("strategy_candidate_protocol_required_affirmations") or ()
    )
    forbidden_flags = (
        contract.get("strategy_candidate_protocol_forbidden_allow_flags") or ()
    )
    modes = contract.get("allowed_strategy_candidate_protocol_modes") or ()
    markers = contract.get("automated_approval_markers") or ()
    universe = contract.get("required_research_universe") or ()
    families = contract.get("required_strategy_families") or ()
    reasons = (
        contract.get("strategy_candidate_protocol_verdict_reasons") or ()
    )
    blocked = contract.get("candidate_protocol_blocked_capabilities") or ()
    remaining_blocked = (
        contract.get("remaining_real_world_capabilities_blocked") or ()
    )
    next_steps = contract.get("human_operator_required_next_steps") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Crypto-D1 Strategy Candidate Protocol Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a crypto-d1-strategy-candidate-protocol-only, "
        "paper-only, no-research, no-data-acquisition, no-data-fetch, "
        "no-data-inspection, no-dataset-loading, no-qa-run, no-baseline-run, "
        "no-backtest, no-simulation, no-trade-signal, no-market-data-"
        "validation, no-paper-live, no-broker-exchange, no-automation, and "
        "execution-free template -- it records only a paper candidate-plan "
        "verdict, is not wired into any runtime state, writes no report file, "
        "acquires no data, inspects no data, loads no dataset, connects to no "
        "venue, names only placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Next research protocol schema: "
        f"`{contract.get('crypto_d1_next_research_protocol_schema_version', '')}`"
    )
    lines.append(f"Protocol ID: {contract.get('protocol_id', '')}")
    lines.append(f"Protocol name: {contract.get('protocol_name', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append(
        "Stage: CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT_ONLY"
    )
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 strategy candidate protocol contract active: "
        f"{contract.get('crypto_d1_strategy_candidate_protocol_contract_active', '')}"
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_strategy_candidate_protocol_contract_state', '')}"
    )
    lines.append(
        "Upstream protocol id: "
        f"{contract.get('upstream_protocol_id', '')}"
    )
    lines.append(
        "Upstream protocol mode: "
        f"{contract.get('upstream_protocol_mode', '')}"
    )
    lines.append(
        "Upstream protocol next required action: "
        f"{contract.get('upstream_protocol_next_required_action', '')}"
    )
    lines.append(
        "Strategy candidate protocol contract required: "
        f"{contract.get('strategy_candidate_protocol_contract_required', '')}"
    )
    lines.append(
        "Strategy candidate protocol next required action: "
        f"{contract.get('strategy_candidate_protocol_next_required_action', '')}"
    )
    lines.append(
        "Strategy candidate protocol current stage: "
        f"{contract.get('strategy_candidate_protocol_current_stage', '')}"
    )
    lines.append(
        "Verdict: "
        f"{contract.get('strategy_candidate_protocol_verdict', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Required Research Scope")
    lines.append("")
    lines.append(f"Required market type: {contract.get('required_market_type', '')}")
    lines.append(f"Required timeframe: {contract.get('required_timeframe', '')}")
    lines.append("Required research universe:")
    for x in universe:
        lines.append(f"- `{x}`")
    lines.append("Required strategy families:")
    for x in families:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Candidate Plan Packet Reference")
    lines.append("")
    lines.append(
        "Candidate plan packet reference: "
        f"{contract.get('candidate_plan_packet_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Strategy Candidate Protocol Verdict Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Strategy Candidate Protocol Verdicts")
    lines.append("")
    for x in verdicts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Strategy Candidate Protocol Fields")
    lines.append("")
    for x in fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Strategy Candidate Protocol Required Text Fields")
    lines.append("")
    for x in text_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Strategy Candidate Protocol Required Affirmations")
    lines.append("")
    for x in affirmations:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Strategy Candidate Protocol Forbidden Allow Flags")
    lines.append("")
    for x in forbidden_flags:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Strategy Candidate Protocol Modes")
    lines.append("")
    for x in modes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Automated Approval Markers")
    lines.append("")
    for x in markers:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Strategy Candidate Protocol Verdict Rationale")
    lines.append("")
    lines.append(
        "Strategy candidate protocol verdict rationale: "
        f"{contract.get('strategy_candidate_protocol_verdict_rationale_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Candidate Protocol Blocked Capabilities")
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
    lines.append("## Safety Posture")
    lines.append("")
    for key in sorted(posture):
        lines.append(f"- `{key}`: {posture[key]}")
    lines.append("")
    lines.append("## Validation")
    lines.append("")
    lines.append(f"- valid: {validation.get('valid', '')}")
    lines.append("")
    return "\n".join(lines)

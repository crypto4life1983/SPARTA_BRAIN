"""SPARTA Offline Strategy Factory - CRYPTO-D1 STRATEGY CANDIDATE RESEARCH PLAN
APPROVAL CONTRACT.

A PURE, stdlib-only *read-only paper contract* builder and evaluator that records,
on paper, the separate human *approval* decision for the external-bot-evidence
research plan after it has already passed the Block 105 Crypto-D1 Strategy
Candidate Research Plan Review Contract. It consumes the stable constants of the
Research Plan Review Contract (Block 105), the External Bot Evidence Research Plan
Contract (Block 103), the Strategy Candidate Family Review Contract (Block 101),
the Family Selection Contract (Block 99), the Strategy Candidate Protocol Contract
(Block 97), and the Next Research Protocol (Block 95), and only when the upstream
research-plan-review signal is clearly the expected READY one
(crypto_d1_strategy_candidate_research_plan_review_contract_active is True,
research_plan_review_verdict == STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_READY,
next_gate ==
CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_READY_SEPARATE_HUMAN_NEXT_STEP_REQUIRED,
mode == RESEARCH_ONLY, read_only is True, executes is False) evaluates a proposed
research-plan-approval packet on paper and returns a deterministic verdict
describing whether the approval is ready, needs more info, must be rejected, or is
parked.

It records the SHAPE of a proposed approval only. It does NOT acquire, fetch,
inspect, load, validate, transform, or compute on any data, does not run QA,
baseline, backtest, or simulation, produces no trade signal, reaches no broker /
exchange / order / account / API surface, trades no paper and no live, triggers no
automation, writes no runtime, registry, ledger, dashboard, or report state, opens
no network, spawns no child process, writes no file, reads no file, lists no
directory, records no timestamp, mints no random id, reads no environment,
dynamically imports nothing, and NEVER modifies the external bot's own repository
or dashboard files. It selects no live trading strategy.

The approval preserves every external-bot-evidence safety stance carried by the
reviewed research plan: external bot evidence stays observation-only and never
becomes permission for paper/live/real execution; SOL is the main candidate but
blocked from execution; XRP is watchlist-only; BTC is dormant and blocked from
expansion; ETH is early-pressure only; adaptive ATR thresholds are an offline
study only with no live threshold change; the four trade-coordinator rules hold;
the multi-asset sync gate (60+ score, 2+ synchronized assets) and the lead-lag /
lagged-sync exclusion hold; a closed-trade proof precedes any promotion; and no
strategy promotion, no paper expansion, and no live activation is authorized.

Reaching a STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_READY verdict unlocks NOTHING
real. It only records, on paper, that a human approved the reviewed research plan
for the next research-only planning step -- and even that still requires a
separate, later, human step. Any upstream research-plan-review signal that is
missing, malformed, not READY, in the wrong mode, executable, non-read-only, or
pointed at a different next gate yields the
AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT verdict.

Public API:
  - RESEARCH_PLAN_APPROVAL_SCHEMA_VERSION
  - DEFAULT_RESEARCH_PLAN_APPROVAL_LABEL
  - RESEARCH_PLAN_APPROVAL_STATUS
  - RESEARCH_PLAN_APPROVAL_SAFETY_POSTURE
  - RESEARCH_PLAN_APPROVAL_STATE_ACTIVE
  - RESEARCH_PLAN_APPROVAL_STATE_BLOCKED
  - RESEARCH_PLAN_APPROVAL_VERDICT_READY
  - RESEARCH_PLAN_APPROVAL_VERDICT_NEEDS_MORE_INFO
  - RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED
  - RESEARCH_PLAN_APPROVAL_VERDICT_PARKED
  - RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT
  - ALLOWED_RESEARCH_PLAN_APPROVAL_VERDICTS
  - UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_VERDICT
  - UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_NEXT_GATE
  - UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_MODE
  - RESEARCH_PLAN_APPROVAL_NEXT_REQUIRED_ACTION
  - RESEARCH_PLAN_APPROVAL_CURRENT_STAGE
  - DECISION_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_CONTRACT_REQUIRED
  - NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_READY
  - NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_PARKED
  - NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_PLAN_REVIEW_CONTRACT
  - REQUIRED_MARKET_TYPE
  - REQUIRED_TIMEFRAME
  - WATCHED_UNIVERSE
  - ASSET_EVIDENCE_STANCES
  - ASSET_EVIDENCE_STANCE_REASONS
  - MIN_MULTI_ASSET_SYNC_SCORE
  - MIN_SYNCHRONIZED_ASSETS
  - TRADE_COORDINATOR_RULES
  - ALLOWED_BOT_STATE_VALUES
  - FORBIDDEN_BOT_STATE_VALUES
  - REQUIRED_RESEARCH_PLAN_APPROVAL_FIELDS
  - RESEARCH_PLAN_APPROVAL_REQUIRED_TEXT_FIELDS
  - RESEARCH_PLAN_APPROVAL_REQUIRED_AFFIRMATIONS
  - RESEARCH_PLAN_APPROVAL_FORBIDDEN_ALLOW_FLAGS
  - ALLOWED_RESEARCH_PLAN_APPROVAL_MODES
  - AUTOMATED_APPROVAL_MARKERS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - evaluate_crypto_d1_strategy_candidate_research_plan_approval(packet)
  - build_crypto_d1_strategy_candidate_research_plan_approval_contract(signal, packet=None)
  - validate_crypto_d1_strategy_candidate_research_plan_approval_contract(contract)
  - render_crypto_d1_strategy_candidate_research_plan_approval_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_next_research_protocol import (
    PROTOCOL_ID as _PROTOCOL_ID,
    PROTOCOL_NAME as _PROTOCOL_NAME,
    PROTOCOL_SCHEMA_VERSION as _PROTOCOL_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_protocol_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_PROTOCOL_SCHEMA_VERSION as _PROTOCOL_CONTRACT_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_family_selection_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_FAMILY_SELECTION_SCHEMA_VERSION as _FAMILY_SELECTION_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_family_review_contract import (  # noqa: E501
    STRATEGY_CANDIDATE_FAMILY_REVIEW_SCHEMA_VERSION as _FAMILY_REVIEW_SCHEMA_VERSION,  # noqa: E501
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_contract import (  # noqa: E501
    BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION as _RESEARCH_PLAN_SCHEMA_VERSION,
)
from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_research_plan_review_contract import (  # noqa: E501
    RESEARCH_PLAN_REVIEW_SCHEMA_VERSION as _RESEARCH_PLAN_REVIEW_SCHEMA_VERSION,
    RESEARCH_PLAN_REVIEW_VERDICT_READY as _RESEARCH_PLAN_REVIEW_VERDICT_READY,
    NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_REVIEW_READY as _NEXT_GATE_RESEARCH_PLAN_REVIEW_READY,  # noqa: E501
    REQUIRED_MARKET_TYPE as _REVIEW_REQUIRED_MARKET_TYPE,
    REQUIRED_TIMEFRAME as _REVIEW_REQUIRED_TIMEFRAME,
    WATCHED_UNIVERSE as _REVIEW_WATCHED_UNIVERSE,
    ASSET_EVIDENCE_STANCES as _REVIEW_ASSET_EVIDENCE_STANCES,
    ASSET_EVIDENCE_STANCE_REASONS as _REVIEW_ASSET_EVIDENCE_STANCE_REASONS,
    MIN_MULTI_ASSET_SYNC_SCORE as _REVIEW_MIN_SYNC_SCORE,
    MIN_SYNCHRONIZED_ASSETS as _REVIEW_MIN_SYNC_ASSETS,
    TRADE_COORDINATOR_RULES as _REVIEW_TRADE_COORDINATOR_RULES,
    ALLOWED_BOT_STATE_VALUES as _REVIEW_ALLOWED_BOT_STATE_VALUES,
    FORBIDDEN_BOT_STATE_VALUES as _REVIEW_FORBIDDEN_BOT_STATE_VALUES,
)

__all__ = [
    "RESEARCH_PLAN_APPROVAL_SCHEMA_VERSION",
    "DEFAULT_RESEARCH_PLAN_APPROVAL_LABEL",
    "RESEARCH_PLAN_APPROVAL_STATUS",
    "RESEARCH_PLAN_APPROVAL_SAFETY_POSTURE",
    "RESEARCH_PLAN_APPROVAL_STATE_ACTIVE",
    "RESEARCH_PLAN_APPROVAL_STATE_BLOCKED",
    "RESEARCH_PLAN_APPROVAL_VERDICT_READY",
    "RESEARCH_PLAN_APPROVAL_VERDICT_NEEDS_MORE_INFO",
    "RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED",
    "RESEARCH_PLAN_APPROVAL_VERDICT_PARKED",
    "RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT",
    "ALLOWED_RESEARCH_PLAN_APPROVAL_VERDICTS",
    "UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_VERDICT",
    "UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_NEXT_GATE",
    "UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_MODE",
    "RESEARCH_PLAN_APPROVAL_NEXT_REQUIRED_ACTION",
    "RESEARCH_PLAN_APPROVAL_CURRENT_STAGE",
    "DECISION_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_CONTRACT_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_READY",
    "NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_FIX_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_PARKED",
    "NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_REJECTED",
    "NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_PLAN_REVIEW_CONTRACT",
    "REQUIRED_MARKET_TYPE",
    "REQUIRED_TIMEFRAME",
    "WATCHED_UNIVERSE",
    "ASSET_EVIDENCE_STANCES",
    "ASSET_EVIDENCE_STANCE_REASONS",
    "MIN_MULTI_ASSET_SYNC_SCORE",
    "MIN_SYNCHRONIZED_ASSETS",
    "TRADE_COORDINATOR_RULES",
    "ALLOWED_BOT_STATE_VALUES",
    "FORBIDDEN_BOT_STATE_VALUES",
    "REQUIRED_RESEARCH_PLAN_APPROVAL_FIELDS",
    "RESEARCH_PLAN_APPROVAL_REQUIRED_TEXT_FIELDS",
    "RESEARCH_PLAN_APPROVAL_REQUIRED_AFFIRMATIONS",
    "RESEARCH_PLAN_APPROVAL_FORBIDDEN_ALLOW_FLAGS",
    "ALLOWED_RESEARCH_PLAN_APPROVAL_MODES",
    "AUTOMATED_APPROVAL_MARKERS",
    "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "evaluate_crypto_d1_strategy_candidate_research_plan_approval",
    "build_crypto_d1_strategy_candidate_research_plan_approval_contract",
    "validate_crypto_d1_strategy_candidate_research_plan_approval_contract",
    "render_crypto_d1_strategy_candidate_research_plan_approval_contract_markdown",  # noqa: E501
]

RESEARCH_PLAN_APPROVAL_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_strategy_candidate_research_plan_approval_contract.v1"  # noqa: E501
)
DEFAULT_RESEARCH_PLAN_APPROVAL_LABEL = (
    "Strategy Factory Crypto-D1 Strategy Candidate Research Plan Approval "
    "Contract"
)
RESEARCH_PLAN_APPROVAL_STATUS = (
    "READ_ONLY_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT"
)

RESEARCH_PLAN_APPROVAL_STATE_ACTIVE = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_ACTIVE"
)
RESEARCH_PLAN_APPROVAL_STATE_BLOCKED = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_BLOCKED"
)

RESEARCH_PLAN_APPROVAL_VERDICT_READY = (
    "STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_READY"
)
RESEARCH_PLAN_APPROVAL_VERDICT_NEEDS_MORE_INFO = (
    "STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_NEEDS_MORE_INFO"
)
RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED = (
    "STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_REJECTED"
)
RESEARCH_PLAN_APPROVAL_VERDICT_PARKED = (
    "STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_PARKED"
)
RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT = (
    "AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT"
)

ALLOWED_RESEARCH_PLAN_APPROVAL_VERDICTS: tuple[str, ...] = (
    RESEARCH_PLAN_APPROVAL_VERDICT_READY,
    RESEARCH_PLAN_APPROVAL_VERDICT_NEEDS_MORE_INFO,
    RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED,
    RESEARCH_PLAN_APPROVAL_VERDICT_PARKED,
    RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT,
)

# The exact upstream research-plan-review signal this contract activates from
# (Block 105). The contract only becomes active when the upstream review contract
# is clearly READY, in RESEARCH_ONLY mode, read-only, non-executing, and pointed
# at exactly this research-plan-approval contract being built next.
UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_VERDICT = (
    _RESEARCH_PLAN_REVIEW_VERDICT_READY
)
UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_NEXT_GATE = (
    _NEXT_GATE_RESEARCH_PLAN_REVIEW_READY
)
UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_MODE = "RESEARCH_ONLY"

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering this
# contract is a separate, later block; importing the registry would also risk a
# circular import).
RESEARCH_PLAN_APPROVAL_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT"
)
RESEARCH_PLAN_APPROVAL_CURRENT_STAGE = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_REQUIRED"
)

DECISION_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_CONTRACT_REQUIRED = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_REQUIRED"
)

NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_READY = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_READY_SEPARATE_HUMAN_"
    "NEXT_STEP_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_FIX_REQUIRED = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_PARKED = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_PARKED"
)
NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_REJECTED = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_PLAN_REVIEW_CONTRACT = (
    "AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT"
)

# Market/timeframe scope reused from Block 105 so this approval can never drift
# from the spot/D1 scope the reviewed research plan interprets evidence against.
REQUIRED_MARKET_TYPE = str(_REVIEW_REQUIRED_MARKET_TYPE).strip().upper()
REQUIRED_TIMEFRAME = str(_REVIEW_REQUIRED_TIMEFRAME).strip().upper()

# The four assets the external bot evidence watches, reused from Block 105.
WATCHED_UNIVERSE: tuple[str, ...] = tuple(_REVIEW_WATCHED_UNIVERSE)
_WATCHED_UNIVERSE_SET: frozenset[str] = frozenset(WATCHED_UNIVERSE)

# Per-asset evidence stance, reused verbatim from Block 105 so the approval can
# never weaken it.
ASSET_EVIDENCE_STANCES: dict[str, str] = dict(_REVIEW_ASSET_EVIDENCE_STANCES)
ASSET_EVIDENCE_STANCE_REASONS: dict[str, str] = dict(
    _REVIEW_ASSET_EVIDENCE_STANCE_REASONS
)

# Multi-asset sync gate, reused from Block 105.
MIN_MULTI_ASSET_SYNC_SCORE = _REVIEW_MIN_SYNC_SCORE
MIN_SYNCHRONIZED_ASSETS = _REVIEW_MIN_SYNC_ASSETS

# Mandatory trade-coordinator rules, reused from Block 105.
TRADE_COORDINATOR_RULES: tuple[str, ...] = tuple(
    _REVIEW_TRADE_COORDINATOR_RULES
)

# Bot-state policy, reused from Block 105. A declared bot state must be one of the
# allowed observe-grade values; any GO/live/execute grade value is a hard
# REJECTED.
ALLOWED_BOT_STATE_VALUES: tuple[str, ...] = tuple(
    _REVIEW_ALLOWED_BOT_STATE_VALUES
)
FORBIDDEN_BOT_STATE_VALUES: tuple[str, ...] = tuple(
    _REVIEW_FORBIDDEN_BOT_STATE_VALUES
)
_ALLOWED_BOT_STATE_SET: frozenset[str] = frozenset(ALLOWED_BOT_STATE_VALUES)
_FORBIDDEN_BOT_STATE_SET: frozenset[str] = frozenset(FORBIDDEN_BOT_STATE_VALUES)

# Read-only, all-false safety posture. Every capability flag stays False; this
# contract records the shape of a proposed approval and unlocks nothing.
RESEARCH_PLAN_APPROVAL_SAFETY_POSTURE: dict[str, bool] = {
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
    "selects_live_strategy": False,
    "triggers_automation": False,
    "writes_runtime_state": False,
    "writes_registry": False,
    "writes_dashboard": False,
    "writes_ledger": False,
    "modifies_external_bot": False,
    "sets_bot_state_go": False,
    "promotes_strategy": False,
    "changes_live_threshold": False,
}

# Strings that mark a non-human / automated approver. A packet authored by any of
# these is rejected: only a human approver may record this paper decision.
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
# REJECTED (the approval tries to operate outside research-only / plan-only
# scope).
ALLOWED_RESEARCH_PLAN_APPROVAL_MODES: tuple[str, ...] = (
    "research_only",
    "research-only",
    "research only",
    "plan_only",
    "plan-only",
    "plan only",
    "research_only_plan_only",
)

# Descriptive text fields a human must record on a proposed research-plan-approval
# packet. Absent -> NEEDS_MORE_INFO.
RESEARCH_PLAN_APPROVAL_REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
    "research_plan_approval_packet_id",
    "upstream_research_plan_review_id",
    "research_plan_review_contract_version",
    "approval_scope",
    "approval_mode",
    "approved_declared_bot_state",
    "approved_watched_universe",
    "approved_asset_stance_summary",
    "approved_multi_asset_sync_interpretation",
    "approved_lead_lag_interpretation",
    "approved_atr_threshold_study_boundary",
    "approved_trade_coordinator_rule_summary",
    "approved_closed_trade_proof_requirement",
    "approver_name_or_id",
    "approval_decision_rationale",
    "next_step_boundary",
    "approval_notes",
)

# Affirmation flags the packet must carry (each affirmed True). The "approved_*"
# flags are positive confirmations that the human approver checked and upholds
# each external-bot-evidence stance carried by the reviewed research plan; the
# "no_*" / "approval_*" flags confirm the approval itself permits no real-world
# thing. A present-but-not-affirmed value is a request to admit or relax that
# thing -- a hard REJECTED. An absent value is a missing requirement
# (NEEDS_MORE_INFO).
RESEARCH_PLAN_APPROVAL_REQUIRED_AFFIRMATIONS: tuple[str, ...] = (
    # Generic approval acknowledgements
    "explicit_human_approval",
    "research_only_acknowledgement",
    "plan_only_acknowledgement",
    "no_execution_acknowledgement",
    # Approval-specific scope acknowledgements
    "approved_research_plan_review_was_ready",
    "approval_is_research_only_human_approved_for_next_planning_only",
    "approval_authorizes_no_execution_or_real_work",
    # Rule 1
    "approved_external_bot_state_is_watch_safe_observe_not_go",
    # Rule 2
    "approved_bot_evidence_is_external_evidence_only",
    "approved_bot_evidence_not_execution_permission",
    # Rule 3
    "approved_failsafe_or_insufficient_data_is_observe_log_only",
    # Rule 4
    "approved_closed_trade_proof_required_before_promotion",
    # Rule 5
    "approved_sol_main_candidate_blocked_from_execution",
    # Rule 6
    "approved_xrp_watchlist_only_insufficient_history",
    # Rule 7
    "approved_btc_dormant_blocked_from_expansion",
    # Rule 8
    "approved_eth_early_pressure_only",
    # Rule 9
    "approved_multi_asset_sync_threshold_required_before_confirmation",
    # Rule 10
    "approved_lead_lag_not_used_as_confirmation",
    "approved_lagged_sync_not_used_as_confirmation",
    # Rule 11
    "approved_adaptive_atr_thresholds_offline_study_only",
    "approved_no_live_threshold_changes",
    # Rule 12
    "approved_trade_coordinator_max_one_open_trade_per_symbol",
    "approved_trade_coordinator_no_same_direction_adds",
    "approved_trade_coordinator_treat_exchanges_as_same_symbol",
    "approved_trade_coordinator_block_opposite_direction",
    # Rule 13
    "approved_no_strategy_promotion",
    "approved_no_paper_expansion",
    "approved_no_live_activation",
    # Generic approval-side no-op acknowledgements
    "no_real_data_acquisition",
    "no_backtest_run",
    "no_runtime_write",
    "no_dashboard_write",
    "no_broker_exchange",
    "do_not_modify_external_bot",
)

# Every required True-flag.
_REQUIRED_TRUE_FLAGS: tuple[str, ...] = (
    RESEARCH_PLAN_APPROVAL_REQUIRED_AFFIRMATIONS
)

# Full set of required research-plan-approval packet fields.
REQUIRED_RESEARCH_PLAN_APPROVAL_FIELDS: tuple[str, ...] = (
    RESEARCH_PLAN_APPROVAL_REQUIRED_TEXT_FIELDS
    + RESEARCH_PLAN_APPROVAL_REQUIRED_AFFIRMATIONS
)

# Positive allow/grant flags an approval packet must NOT request -- any truthy
# value forces a hard REJECTED. Generic capability flags plus
# bot-evidence-specific ones (execution, SOL/BTC unblocking, lead-lag
# confirmation, live thresholds, trade-coordinator overrides, promotion, and
# external-bot modification), plus approval-specific ones (an approval may not
# authorize a real next contract or relax the plan it merely signs off on paper).
RESEARCH_PLAN_APPROVAL_FORBIDDEN_ALLOW_FLAGS: tuple[str, ...] = (
    "allow_real_data_acquisition",
    "real_data_acquisition_allowed",
    "acquires_data",
    "allow_data_fetch",
    "fetches_data",
    "allow_data_inspection",
    "inspects_market_data",
    "allow_dataset_load",
    "loads_dataset",
    "allow_qa_run",
    "runs_qa",
    "allow_baseline_run",
    "runs_baseline",
    "allow_backtest_run",
    "runs_backtest",
    "allow_simulation_run",
    "runs_simulation",
    "allow_paper_live",
    "paper_or_live",
    "allow_broker_exchange",
    "connects_exchange_or_broker",
    "allow_order_capability",
    "order_logic",
    "allow_account_access",
    "account_access",
    "allow_api_keys",
    "uses_api_keys",
    "allow_live_strategy_selection",
    "selects_live_strategy",
    "allow_automation_trigger",
    "triggers_automation",
    "allow_runtime_write",
    "writes_runtime_state",
    "allow_registry_write",
    "writes_registry",
    "allow_dashboard_write",
    "writes_dashboard",
    "allow_ledger_write",
    "writes_ledger",
    "allow_trade_signal",
    "generates_trade_signal",
    "allow_intraday",
    "uses_intraday",
    "allow_perps",
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
    "proceed_to_execution",
    "proceed_to_real_run",
    "proceed_to_real_contract",
    # Bot-evidence-specific
    "allow_execution",
    "bot_state_go",
    "set_bot_state_go",
    "allow_sol_execution",
    "sol_execution_ready",
    "promote_sol",
    "unblock_sol_execution",
    "allow_btc_expansion",
    "unblock_btc_expansion",
    "use_lead_lag_as_confirmation",
    "use_lagged_sync_as_confirmation",
    "allow_live_threshold_change",
    "change_live_threshold",
    "override_trade_coordinator",
    "allow_same_direction_adds",
    "allow_opposite_direction",
    "allow_multiple_open_trades_per_symbol",
    "split_exchanges_as_different_symbols",
    "skip_closed_trade_proof",
    "allow_strategy_promotion",
    "allow_paper_expansion",
    "allow_live_activation",
    "treat_evidence_as_execution_permission",
    "bypass_multi_asset_sync_threshold",
    "modify_external_bot",
    "write_to_external_bot_repo",
    # Approval-specific: an approval may not authorize a real next contract or
    # relax the plan / review it is supposed to merely sign off.
    "approve_plan_for_execution",
    "approves_plan_for_execution",
    "approval_grants_execution",
    "treat_approval_as_execution_permission",
    "proceed_to_real_acquisition",
    "approves_real_next_contract",
    "next_real_contract_allowed",
    "weaken_research_plan",
    "relax_research_plan_safety",
    "weaken_research_plan_review",
    "relax_research_plan_review_safety",
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
    "live_strategy_selection",
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
    "external_bot_modification",
    "external_bot_repo_write",
    "bot_state_go",
    "live_threshold_change",
)

# Research-plan-approval-phase blocked capabilities (named for this lane).
_RESEARCH_PLAN_APPROVAL_BLOCKED_CAPABILITIES: tuple[str, ...] = (
    "crypto_d1_real_data_acquisition",
    "crypto_d1_data_fetch",
    "crypto_d1_data_inspection",
    "crypto_d1_backtest",
    "crypto_d1_simulation",
    "crypto_d1_trade_signal_production",
    "crypto_d1_live_api_access",
    "crypto_d1_exchange_connection",
    "crypto_d1_broker_connection",
    "crypto_d1_order_capability",
    "crypto_d1_account_access",
    "crypto_d1_live_strategy_selection",
    "crypto_d1_strategy_promotion",
    "crypto_d1_paper_expansion",
    "crypto_d1_live_activation",
    "crypto_d1_bot_state_go",
    "crypto_d1_live_threshold_change",
    "external_bot_modification",
    "external_bot_repo_write",
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
    "backtest_run",
    "simulation_run",
    "trade_signal_production",
    "paper_or_live_trading",
    "broker_or_exchange_connection",
    "order_capability",
    "account_access",
    "api_key_use",
    "live_strategy_selection",
    "strategy_promotion",
    "paper_expansion",
    "live_activation",
    "bot_state_go",
    "live_threshold_change",
    "automation_trigger",
    "runtime_write",
    "registry_write",
    "dashboard_write",
    "ledger_write",
    "external_bot_modification",
)

_RESEARCH_PLAN_APPROVAL_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 research-plan-approval packet is a paper placeholder describing a "
    "proposed human approval of the reviewed external-bot-evidence research "
    "plan: whether the declared observe-grade bot state, the BTC/ETH/SOL/XRP "
    "watched universe and per-asset stances, the multi-asset-sync gate, the "
    "lead-lag / lagged-sync exclusion, the offline-only ATR-threshold study "
    "boundary, the mandatory trade-coordinator rules, the closed-trade-proof "
    "requirement, and the no-promotion / no-paper-expansion / no-live-activation "
    "stance are all upheld and approved for the next research-only planning step "
    "-- it approves on paper only, runs nothing, acquires nothing, modifies no "
    "external bot, selects no live strategy, and executes nothing."
)

_RESEARCH_PLAN_APPROVAL_VERDICT_RATIONALE_PLACEHOLDER = (
    "Research-plan-approval verdict rationale is a paper placeholder for a "
    "human-recorded judgement of whether a proposed approval of the reviewed "
    "external-bot-evidence research plan upholds every stance and stays "
    "research-only / human-approved-for-next-planning-only, and its supporting "
    "reason."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 strategy candidate research plan approval contract "
    "template and is execution-free.",
    "It records, on paper, the separate human approval of the reviewed "
    "external-bot-evidence research plan recorded by the Block 105 contract; it "
    "runs no research and touches no external bot.",
    "It records a paper research-plan-approval packet only and writes no report "
    "file.",
    "The approval upholds that external bot evidence stays observation-only and "
    "never becomes permission for paper/live/real execution.",
    "SOL stays blocked from execution, XRP is watchlist-only, BTC is dormant and "
    "blocked from expansion, and ETH is early-pressure only.",
    "Market confirmation stays gated behind a multi-asset sync score of at least "
    "60 with at least 2 synchronized assets; lead-lag and lagged-sync are never "
    "confirmation.",
    "Adaptive ATR thresholds remain an offline study only; no live threshold "
    "change is authorized.",
    "Trade-coordinator rules remain mandatory: max one open trade per symbol, no "
    "same-direction adds, exchanges treated as the same symbol, opposite "
    "direction blocked.",
    "No strategy promotion, no paper expansion, and no live activation is "
    "authorized, and a minimum closed-trade proof remains required before any "
    "promotion.",
    "Approval is research-only and human-approved-for-next-planning only; it "
    "authorizes no execution, no data acquisition, and no real next contract.",
    "It never modifies the external bot's own repository or dashboard files.",
    "A human approver alone may record this verdict; no automated approver is "
    "accepted, and any READY still requires a separate, later, human step.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human approver must record a research-plan-approval verdict with a "
    "supporting rationale on paper.",
    "A human approver must confirm the reviewed research plan keeps the declared "
    "bot state observe-grade (watch / safe_observe / observe) and never GO/live/"
    "execute, and treats bot evidence as observation-only and never as execution "
    "permission.",
    "A human approver must confirm the per-asset stances are upheld: SOL blocked "
    "from execution, XRP watchlist-only, BTC dormant/blocked from expansion, ETH "
    "early-pressure only.",
    "A human approver must confirm market confirmation stays gated behind a 60+ "
    "multi-asset sync score with at least 2 synchronized assets, lead-lag / "
    "lagged-sync are excluded, ATR-threshold work stays offline-only, the four "
    "trade-coordinator rules hold, and a closed-trade proof precedes any "
    "promotion.",
    "A human approver must confirm no strategy promotion, no paper expansion, "
    "and no live activation is authorized, that the approval is research-only "
    "and for the next planning step only, and that it weakens no part of the "
    "research plan or its review.",
    "No automated step, no execution, no promotion, no paper expansion, no live "
    "activation, and no modification of the external bot may proceed.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "crypto_d1_strategy_candidate_research_plan_review_contract_schema_version",
    "crypto_d1_strategy_candidate_research_plan_contract_schema_version",
    "crypto_d1_strategy_candidate_family_review_contract_schema_version",
    "crypto_d1_strategy_candidate_family_selection_contract_schema_version",
    "crypto_d1_strategy_candidate_protocol_contract_schema_version",
    "crypto_d1_next_research_protocol_schema_version",
    "label",
    "status",
    "stage",
    "mode",
    "protocol_id",
    "protocol_name",
    "crypto_d1_strategy_candidate_research_plan_approval_contract_active",
    "crypto_d1_strategy_candidate_research_plan_approval_contract_state",
    "crypto_d1_strategy_candidate_research_plan_review_contract_recognized",
    "upstream_research_plan_review_verdict",
    "upstream_research_plan_review_next_gate",
    "upstream_research_plan_review_mode",
    "research_plan_approval_contract_required",
    "research_plan_approval_next_required_action",
    "research_plan_approval_current_stage",
    "required_market_type",
    "required_timeframe",
    "watched_universe",
    "asset_evidence_stances",
    "asset_evidence_stance_reasons",
    "min_multi_asset_sync_score",
    "min_synchronized_assets",
    "trade_coordinator_rules",
    "allowed_bot_state_values",
    "forbidden_bot_state_values",
    "research_plan_approval_packet_reference_placeholder",
    "research_plan_approval_verdict",
    "research_plan_approval_verdict_reasons",
    "evaluated_research_plan_approval_packet",
    "allowed_research_plan_approval_verdicts",
    "required_research_plan_approval_fields",
    "research_plan_approval_required_text_fields",
    "research_plan_approval_required_affirmations",
    "research_plan_approval_forbidden_allow_flags",
    "allowed_research_plan_approval_modes",
    "automated_approval_markers",
    "research_plan_approval_verdict_rationale_placeholder",
    "research_plan_approval_blocked_capabilities",
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
    return dict(RESEARCH_PLAN_APPROVAL_SAFETY_POSTURE)


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
            "approved", "verified", "prohibited", "blocked",
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


def _as_number(value: Any) -> float | None:
    """Read a numeric scalar; returns None for bools/non-numeric/blank."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


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
    admitted/relaxed affirmation, a disallowed mode, a GO/disallowed approved bot
    state, a market-confirmation claim below the multi-asset-sync gate, a non-core
    asset in the approved watched universe, an automated approver, or granted
    authority."""
    reasons: list[str] = []

    for flag in RESEARCH_PLAN_APPROVAL_FORBIDDEN_ALLOW_FLAGS:
        if _truthy(packet.get(flag)):
            reasons.append(f"forbidden_allow:{flag}")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag in packet and not _affirm(packet.get(flag)):
            reasons.append(f"affirmation_relaxed:{flag}")

    mode = packet.get("approval_mode")
    if not _present(mode):
        mode = packet.get("mode")
    if _present(mode) and _scalar(mode) not in (
        ALLOWED_RESEARCH_PLAN_APPROVAL_MODES
    ):
        reasons.append("disallowed_mode")

    bot_state = packet.get("approved_declared_bot_state")
    if _present(bot_state):
        state_value = _scalar(bot_state)
        if state_value in _FORBIDDEN_BOT_STATE_SET:
            reasons.append("approved_bot_state_go_not_permitted")
        elif state_value not in _ALLOWED_BOT_STATE_SET:
            reasons.append("disallowed_approved_bot_state")

    if _truthy(packet.get("approved_claims_market_confirmation")):
        score = _as_number(packet.get("approved_multi_asset_sync_score"))
        count = _as_number(packet.get("approved_synchronized_asset_count"))
        if (
            score is None
            or score < MIN_MULTI_ASSET_SYNC_SCORE
            or count is None
            or count < MIN_SYNCHRONIZED_ASSETS
        ):
            reasons.append(
                "approved_market_confirmation_below_multi_asset_sync_threshold"
            )

    watched = _upper_token_set(packet.get("approved_watched_universe"))
    extras = watched - _WATCHED_UNIVERSE_SET
    if extras:
        reasons.append("non_core_assets_in_approved_watched_universe")

    for key in (
        "approver_type",
        "approval_author_type",
        "approval_method",
        "approval_source",
        "authored_by_type",
        "approver_name_or_id",
    ):
        if _scalar(packet.get(key)) in AUTOMATED_APPROVAL_MARKERS:
            reasons.append(f"automated_approver:{key}")

    for key in ("grants_capabilities", "authorizes", "granted_capabilities"):
        listed = packet.get(key)
        if isinstance(listed, (list, tuple)) and len(listed) > 0:
            reasons.append(f"grants_listed:{key}")

    return tuple(reasons)


def _park_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return parking reasons when an approver explicitly parks or defers the
    whole research-plan-approval lane."""
    reasons: list[str] = []
    park_values = {
        "park", "parked", "defer", "deferred", "hold", "on_hold",
        "postpone", "postponed",
    }

    for flag in ("park", "parked", "defer", "deferred", "hold"):
        if _truthy(packet.get(flag)):
            reasons.append("approver_parked_research_plan_approval")
            break

    if _scalar(packet.get("approver_decision")) in park_values:
        reasons.append("approver_decision_parked")
    if _scalar(packet.get("approval_decision")) in park_values:
        reasons.append("approval_decision_parked")

    return tuple(reasons)


def _missing_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return unmet requirements for an otherwise-safe research-plan-approval
    packet: absent text fields, unaffirmed flags, or an incomplete
    BTC/ETH/SOL/XRP approved watched universe."""
    missing: list[str] = []

    for key in RESEARCH_PLAN_APPROVAL_REQUIRED_TEXT_FIELDS:
        if not _present(packet.get(key)):
            missing.append(f"{key}_required")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag not in packet:
            missing.append(f"{flag}_must_be_affirmed_true")

    watched = _upper_token_set(packet.get("approved_watched_universe"))
    for asset in WATCHED_UNIVERSE:
        if asset not in watched:
            missing.append(f"approved_watched_universe_missing_{asset}")

    return tuple(missing)


def evaluate_crypto_d1_strategy_candidate_research_plan_approval(
    packet: Any,
) -> dict[str, Any]:
    """Return a deterministic verdict for a proposed research-plan-approval packet.
    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. REJECTED (permits a dangerous capability / relaxes an
    affirmation / off-scope value / GO approved bot state / sub-threshold
    confirmation / non-core asset / automated approver / authority-granting) is
    checked before parking, and parking before completeness, so an unsafe approval
    is rejected even when it would otherwise park or merely need more info."""
    p = packet if isinstance(packet, dict) else {}

    if not p:
        return {
            "verdict": RESEARCH_PLAN_APPROVAL_VERDICT_NEEDS_MORE_INFO,
            "reasons": ("research_plan_approval_packet_missing",),
        }

    rejected = _reject_reasons(p)
    if rejected:
        return {
            "verdict": RESEARCH_PLAN_APPROVAL_VERDICT_REJECTED,
            "reasons": rejected,
        }

    park = _park_reasons(p)
    if park:
        return {
            "verdict": RESEARCH_PLAN_APPROVAL_VERDICT_PARKED,
            "reasons": park,
        }

    missing = _missing_reasons(p)
    if not missing:
        return {
            "verdict": RESEARCH_PLAN_APPROVAL_VERDICT_READY,
            "reasons": (
                "research_only_research_plan_approval_fully_specified_human_"
                "approved_for_next_planning_only_upholds_all_external_bot_"
                "evidence_stances_watch_safe_observe_only_sol_blocked_xrp_"
                "watchlist_btc_dormant_eth_early_pressure_sync_gate_60_2_no_"
                "lead_lag_confirmation_atr_offline_only_trade_coordinator_rules_"
                "no_promotion_paper_or_live_and_blocks_every_real_world_"
                "capability",
            ),
        }

    return {
        "verdict": RESEARCH_PLAN_APPROVAL_VERDICT_NEEDS_MORE_INFO,
        "reasons": missing,
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == RESEARCH_PLAN_APPROVAL_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_ONLY"
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
        tuple(safe.get("allowed_research_plan_approval_verdicts") or ())
        == ALLOWED_RESEARCH_PLAN_APPROVAL_VERDICTS
    )
    fields_ok = (
        tuple(safe.get("required_research_plan_approval_fields") or ())
        == REQUIRED_RESEARCH_PLAN_APPROVAL_FIELDS
    )
    text_fields_ok = (
        tuple(safe.get("research_plan_approval_required_text_fields") or ())
        == RESEARCH_PLAN_APPROVAL_REQUIRED_TEXT_FIELDS
    )
    affirmations_ok = (
        tuple(safe.get("research_plan_approval_required_affirmations") or ())
        == RESEARCH_PLAN_APPROVAL_REQUIRED_AFFIRMATIONS
    )
    forbidden_flags_ok = (
        tuple(safe.get("research_plan_approval_forbidden_allow_flags") or ())
        == RESEARCH_PLAN_APPROVAL_FORBIDDEN_ALLOW_FLAGS
    )
    modes_ok = (
        tuple(safe.get("allowed_research_plan_approval_modes") or ())
        == ALLOWED_RESEARCH_PLAN_APPROVAL_MODES
    )
    markers_ok = (
        tuple(safe.get("automated_approval_markers") or ())
        == AUTOMATED_APPROVAL_MARKERS
    )
    watched_ok = (
        tuple(safe.get("watched_universe") or ()) == WATCHED_UNIVERSE
    )
    stances_ok = safe.get("asset_evidence_stances") == ASSET_EVIDENCE_STANCES
    stance_reasons_ok = (
        safe.get("asset_evidence_stance_reasons")
        == ASSET_EVIDENCE_STANCE_REASONS
    )
    sync_score_ok = (
        safe.get("min_multi_asset_sync_score") == MIN_MULTI_ASSET_SYNC_SCORE
    )
    sync_count_ok = (
        safe.get("min_synchronized_assets") == MIN_SYNCHRONIZED_ASSETS
    )
    coordinator_ok = (
        tuple(safe.get("trade_coordinator_rules") or ())
        == TRADE_COORDINATOR_RULES
    )
    bot_states_ok = (
        tuple(safe.get("allowed_bot_state_values") or ())
        == ALLOWED_BOT_STATE_VALUES
        and tuple(safe.get("forbidden_bot_state_values") or ())
        == FORBIDDEN_BOT_STATE_VALUES
    )
    market_ok = safe.get("required_market_type") == REQUIRED_MARKET_TYPE
    timeframe_ok = safe.get("required_timeframe") == REQUIRED_TIMEFRAME
    remaining_blocked_ok = (
        tuple(safe.get("remaining_real_world_capabilities_blocked") or ())
        == REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )
    verdict_value_ok = (
        safe.get("research_plan_approval_verdict")
        in ALLOWED_RESEARCH_PLAN_APPROVAL_VERDICTS
    )
    blocked_present_ok = (
        len(tuple(safe.get("research_plan_approval_blocked_capabilities") or ()))
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
        and watched_ok
        and stances_ok
        and stance_reasons_ok
        and sync_score_ok
        and sync_count_ok
        and coordinator_ok
        and bot_states_ok
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
        "allowed_research_plan_approval_verdicts_ok": verdicts_ok,
        "required_research_plan_approval_fields_ok": fields_ok,
        "research_plan_approval_required_text_fields_ok": text_fields_ok,
        "research_plan_approval_required_affirmations_ok": affirmations_ok,
        "research_plan_approval_forbidden_allow_flags_ok": forbidden_flags_ok,
        "allowed_research_plan_approval_modes_ok": modes_ok,
        "automated_approval_markers_ok": markers_ok,
        "watched_universe_ok": watched_ok,
        "asset_evidence_stances_ok": stances_ok,
        "asset_evidence_stance_reasons_ok": stance_reasons_ok,
        "min_multi_asset_sync_score_ok": sync_score_ok,
        "min_synchronized_assets_ok": sync_count_ok,
        "trade_coordinator_rules_ok": coordinator_ok,
        "bot_state_values_ok": bot_states_ok,
        "required_market_type_ok": market_ok,
        "required_timeframe_ok": timeframe_ok,
        "remaining_real_world_capabilities_blocked_ok": remaining_blocked_ok,
        "research_plan_approval_verdict_value_ok": verdict_value_ok,
        "research_plan_approval_blocked_capabilities_present": blocked_present_ok,
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_strategy_candidate_research_plan_approval_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 strategy candidate research
    plan approval contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_strategy_candidate_research_plan_approval_contract(
    upstream_research_plan_review_signal: Any,
    research_plan_approval_packet: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 strategy candidate research
    plan approval contract template plus a paper verdict for a proposed approval
    packet.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import, and
    no modification of any external bot. Unknown/malformed inputs never raise. The
    contract becomes active solely when the upstream Block 105
    research-plan-review signal is clearly READY for this gate:
    crypto_d1_strategy_candidate_research_plan_review_contract_active is True,
    research_plan_review_verdict == STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_READY,
    next_gate ==
    CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_READY_SEPARATE_HUMAN_NEXT_STEP_REQUIRED,
    mode == RESEARCH_ONLY, read_only is True, and executes is False. When inactive
    (missing, dirty, ambiguous, or not-READY upstream), the verdict is
    AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_REVIEW_CONTRACT regardless of
    the packet. Even when active and READY, every authorization field stays False.
    Returned dicts are fresh."""
    signal = (
        upstream_research_plan_review_signal
        if isinstance(upstream_research_plan_review_signal, dict)
        else {}
    )

    sig_verdict = _field(signal, "research_plan_review_verdict")
    sig_next_gate = _field(signal, "next_gate")
    sig_mode = _field(signal, "mode")
    active_flag_ok = (
        signal.get(
            "crypto_d1_strategy_candidate_research_plan_review_contract_active"
        )
        is True
    )
    read_only_ok = signal.get("read_only") is True
    executes_false = signal.get("executes") is False
    verdict_ok = (
        sig_verdict == UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_VERDICT
    )
    next_gate_ok = (
        sig_next_gate == UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_NEXT_GATE
    )
    mode_ok = sig_mode == UPSTREAM_REQUIRED_RESEARCH_PLAN_REVIEW_MODE

    contract_active = bool(
        active_flag_ok
        and verdict_ok
        and next_gate_ok
        and mode_ok
        and read_only_ok
        and executes_false
    )

    if contract_active:
        evaluation = (
            evaluate_crypto_d1_strategy_candidate_research_plan_approval(
                research_plan_approval_packet
            )
        )
        verdict = evaluation["verdict"]
        reasons = tuple(evaluation["reasons"])
    else:
        verdict = RESEARCH_PLAN_APPROVAL_VERDICT_AWAIT
        reasons = (
            "await_crypto_d1_strategy_candidate_research_plan_review_contract",
        )

    state = (
        RESEARCH_PLAN_APPROVAL_STATE_ACTIVE
        if contract_active
        else RESEARCH_PLAN_APPROVAL_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_PLAN_REVIEW_CONTRACT
    elif verdict == RESEARCH_PLAN_APPROVAL_VERDICT_READY:
        next_gate = NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_READY
    elif verdict == RESEARCH_PLAN_APPROVAL_VERDICT_NEEDS_MORE_INFO:
        next_gate = NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_FIX_REQUIRED
    elif verdict == RESEARCH_PLAN_APPROVAL_VERDICT_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_PARKED
    else:
        next_gate = NEXT_GATE_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_REJECTED

    research_plan_approval_contract_required = (
        DECISION_CRYPTO_D1_RESEARCH_PLAN_APPROVAL_CONTRACT_REQUIRED
        if contract_active
        else ""
    )

    echoed_packet = (
        dict(research_plan_approval_packet)
        if isinstance(research_plan_approval_packet, dict)
        else {}
    )

    contract = {
        "schema_version": RESEARCH_PLAN_APPROVAL_SCHEMA_VERSION,
        "crypto_d1_strategy_candidate_research_plan_review_contract_schema_version": (  # noqa: E501
            _RESEARCH_PLAN_REVIEW_SCHEMA_VERSION
        ),
        "crypto_d1_strategy_candidate_research_plan_contract_schema_version": (
            _RESEARCH_PLAN_SCHEMA_VERSION
        ),
        "crypto_d1_strategy_candidate_family_review_contract_schema_version": (
            _FAMILY_REVIEW_SCHEMA_VERSION
        ),
        "crypto_d1_strategy_candidate_family_selection_contract_schema_version": (  # noqa: E501
            _FAMILY_SELECTION_SCHEMA_VERSION
        ),
        "crypto_d1_strategy_candidate_protocol_contract_schema_version": (
            _PROTOCOL_CONTRACT_SCHEMA_VERSION
        ),
        "crypto_d1_next_research_protocol_schema_version": (
            _PROTOCOL_SCHEMA_VERSION
        ),
        "label": DEFAULT_RESEARCH_PLAN_APPROVAL_LABEL,
        "status": RESEARCH_PLAN_APPROVAL_STATUS,
        "stage": (
            "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_ONLY"
        ),
        "mode": "RESEARCH_ONLY",
        "protocol_id": _PROTOCOL_ID,
        "protocol_name": _PROTOCOL_NAME,
        "crypto_d1_strategy_candidate_research_plan_approval_contract_active": (
            contract_active
        ),
        "crypto_d1_strategy_candidate_research_plan_approval_contract_state": (
            state
        ),
        "crypto_d1_strategy_candidate_research_plan_review_contract_recognized": (  # noqa: E501
            contract_active
        ),
        "upstream_research_plan_review_verdict": sig_verdict,
        "upstream_research_plan_review_next_gate": sig_next_gate,
        "upstream_research_plan_review_mode": sig_mode,
        "research_plan_approval_contract_required": (
            research_plan_approval_contract_required
        ),
        "research_plan_approval_next_required_action": (
            RESEARCH_PLAN_APPROVAL_NEXT_REQUIRED_ACTION
        ),
        "research_plan_approval_current_stage": (
            RESEARCH_PLAN_APPROVAL_CURRENT_STAGE
        ),
        "required_market_type": REQUIRED_MARKET_TYPE,
        "required_timeframe": REQUIRED_TIMEFRAME,
        "watched_universe": WATCHED_UNIVERSE,
        "asset_evidence_stances": dict(ASSET_EVIDENCE_STANCES),
        "asset_evidence_stance_reasons": dict(ASSET_EVIDENCE_STANCE_REASONS),
        "min_multi_asset_sync_score": MIN_MULTI_ASSET_SYNC_SCORE,
        "min_synchronized_assets": MIN_SYNCHRONIZED_ASSETS,
        "trade_coordinator_rules": TRADE_COORDINATOR_RULES,
        "allowed_bot_state_values": ALLOWED_BOT_STATE_VALUES,
        "forbidden_bot_state_values": FORBIDDEN_BOT_STATE_VALUES,
        "research_plan_approval_packet_reference_placeholder": (
            _RESEARCH_PLAN_APPROVAL_REFERENCE_PLACEHOLDER
        ),
        "research_plan_approval_verdict": verdict,
        "research_plan_approval_verdict_reasons": reasons,
        "evaluated_research_plan_approval_packet": echoed_packet,
        "allowed_research_plan_approval_verdicts": (
            ALLOWED_RESEARCH_PLAN_APPROVAL_VERDICTS
        ),
        "required_research_plan_approval_fields": (
            REQUIRED_RESEARCH_PLAN_APPROVAL_FIELDS
        ),
        "research_plan_approval_required_text_fields": (
            RESEARCH_PLAN_APPROVAL_REQUIRED_TEXT_FIELDS
        ),
        "research_plan_approval_required_affirmations": (
            RESEARCH_PLAN_APPROVAL_REQUIRED_AFFIRMATIONS
        ),
        "research_plan_approval_forbidden_allow_flags": (
            RESEARCH_PLAN_APPROVAL_FORBIDDEN_ALLOW_FLAGS
        ),
        "allowed_research_plan_approval_modes": (
            ALLOWED_RESEARCH_PLAN_APPROVAL_MODES
        ),
        "automated_approval_markers": AUTOMATED_APPROVAL_MARKERS,
        "research_plan_approval_verdict_rationale_placeholder": (
            _RESEARCH_PLAN_APPROVAL_VERDICT_RATIONALE_PLACEHOLDER
        ),
        "research_plan_approval_blocked_capabilities": (
            _RESEARCH_PLAN_APPROVAL_BLOCKED_CAPABILITIES
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


def render_crypto_d1_strategy_candidate_research_plan_approval_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 strategy candidate
    research plan approval contract template. Pure; writes no file. Informational
    only."""
    verdicts = contract.get("allowed_research_plan_approval_verdicts") or ()
    fields = contract.get("required_research_plan_approval_fields") or ()
    text_fields = (
        contract.get("research_plan_approval_required_text_fields") or ()
    )
    affirmations = (
        contract.get("research_plan_approval_required_affirmations") or ()
    )
    forbidden_flags = (
        contract.get("research_plan_approval_forbidden_allow_flags") or ()
    )
    modes = contract.get("allowed_research_plan_approval_modes") or ()
    markers = contract.get("automated_approval_markers") or ()
    watched = contract.get("watched_universe") or ()
    stances = contract.get("asset_evidence_stances") or {}
    reasons = contract.get("research_plan_approval_verdict_reasons") or ()
    blocked = contract.get("research_plan_approval_blocked_capabilities") or ()
    remaining_blocked = (
        contract.get("remaining_real_world_capabilities_blocked") or ()
    )
    coordinator = contract.get("trade_coordinator_rules") or ()
    next_steps = contract.get("human_operator_required_next_steps") or ()
    notes = contract.get("operator_notes") or ()
    posture = contract.get("safety_posture") or {}
    validation = contract.get("validation") or {}

    lines: list[str] = []
    lines.append(
        "# Strategy Factory Crypto-D1 Strategy Candidate Research Plan Approval "
        "Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this is a crypto-d1-strategy-candidate-research-plan-"
        "approval-only, paper-only, no-research, no-data-acquisition, "
        "no-data-fetch, no-data-inspection, no-dataset-loading, no-qa-run, "
        "no-baseline-run, no-backtest, no-simulation, no-trade-signal, "
        "no-market-data-validation, no-paper-live, no-broker-exchange, "
        "no-live-strategy-selection, no-automation, no-external-bot-"
        "modification, and execution-free template -- it records only a paper "
        "research-plan-approval verdict, is not wired into any runtime state, "
        "writes no report file, acquires no data, inspects no data, loads no "
        "dataset, connects to no venue, selects no live strategy, modifies no "
        "external bot, names only placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Research plan review contract schema: "
        f"`{contract.get('crypto_d1_strategy_candidate_research_plan_review_contract_schema_version', '')}`"  # noqa: E501
    )
    lines.append(
        "Research plan contract schema: "
        f"`{contract.get('crypto_d1_strategy_candidate_research_plan_contract_schema_version', '')}`"  # noqa: E501
    )
    lines.append(
        "Family review contract schema: "
        f"`{contract.get('crypto_d1_strategy_candidate_family_review_contract_schema_version', '')}`"  # noqa: E501
    )
    lines.append(
        "Family selection contract schema: "
        f"`{contract.get('crypto_d1_strategy_candidate_family_selection_contract_schema_version', '')}`"  # noqa: E501
    )
    lines.append(
        "Protocol contract schema: "
        f"`{contract.get('crypto_d1_strategy_candidate_protocol_contract_schema_version', '')}`"  # noqa: E501
    )
    lines.append(
        "Next research protocol schema: "
        f"`{contract.get('crypto_d1_next_research_protocol_schema_version', '')}`"  # noqa: E501
    )
    lines.append(f"Protocol ID: {contract.get('protocol_id', '')}")
    lines.append(f"Protocol name: {contract.get('protocol_name', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append(
        "Stage: "
        "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_APPROVAL_CONTRACT_ONLY"
    )
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Crypto-D1 strategy candidate research plan approval contract active: "
        f"{contract.get('crypto_d1_strategy_candidate_research_plan_approval_contract_active', '')}"  # noqa: E501
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_strategy_candidate_research_plan_approval_contract_state', '')}"  # noqa: E501
    )
    lines.append(
        "Upstream research plan review verdict: "
        f"{contract.get('upstream_research_plan_review_verdict', '')}"
    )
    lines.append(
        "Upstream research plan review next gate: "
        f"{contract.get('upstream_research_plan_review_next_gate', '')}"
    )
    lines.append(
        "Upstream research plan review mode: "
        f"{contract.get('upstream_research_plan_review_mode', '')}"
    )
    lines.append(
        "Research plan approval contract required: "
        f"{contract.get('research_plan_approval_contract_required', '')}"
    )
    lines.append(
        "Research plan approval next required action: "
        f"{contract.get('research_plan_approval_next_required_action', '')}"
    )
    lines.append(
        "Research plan approval current stage: "
        f"{contract.get('research_plan_approval_current_stage', '')}"
    )
    lines.append(
        f"Verdict: {contract.get('research_plan_approval_verdict', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Required Research Scope")
    lines.append("")
    lines.append(
        f"Required market type: {contract.get('required_market_type', '')}"
    )
    lines.append(
        f"Required timeframe: {contract.get('required_timeframe', '')}"
    )
    lines.append("Watched universe:")
    for x in watched:
        lines.append(f"- `{x}`")
    lines.append("Asset evidence stances:")
    for asset in sorted(stances):
        lines.append(f"- `{asset}`: {stances[asset]}")
    lines.append(
        "Multi-asset sync score floor: "
        f"{contract.get('min_multi_asset_sync_score', '')}"
    )
    lines.append(
        "Synchronized asset count floor: "
        f"{contract.get('min_synchronized_assets', '')}"
    )
    lines.append("Trade coordinator rules:")
    for x in coordinator:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Research Plan Approval Packet Reference")
    lines.append("")
    lines.append(
        "Research plan approval packet reference: "
        f"{contract.get('research_plan_approval_packet_reference_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Research Plan Approval Verdict Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Research Plan Approval Verdicts")
    lines.append("")
    for x in verdicts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Research Plan Approval Fields")
    lines.append("")
    for x in fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Research Plan Approval Required Text Fields")
    lines.append("")
    for x in text_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Research Plan Approval Required Affirmations")
    lines.append("")
    for x in affirmations:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Research Plan Approval Forbidden Allow Flags")
    lines.append("")
    for x in forbidden_flags:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Research Plan Approval Modes")
    lines.append("")
    for x in modes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Automated Approval Markers")
    lines.append("")
    for x in markers:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Research Plan Approval Verdict Rationale")
    lines.append("")
    lines.append(
        "Research plan approval verdict rationale: "
        f"{contract.get('research_plan_approval_verdict_rationale_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Research Plan Approval Blocked Capabilities")
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

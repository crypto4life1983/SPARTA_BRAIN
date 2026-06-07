"""SPARTA Offline Strategy Factory - CRYPTO-D1 EXTERNAL BOT EVIDENCE RESEARCH
PLAN CONTRACT.

A PURE, stdlib-only *read-only paper contract* builder and evaluator that records
HOW SPARTA_BRAIN should interpret the uploaded external bot evidence (the running
external bot/dashboard repository, which lives entirely outside SPARTA_BRAIN and
which this module NEVER touches). It consumes the stable constants of the Crypto-D1 Strategy Candidate
Family Review Contract (Block 101), the Family Selection Contract (Block 99), the
Strategy Candidate Protocol Contract (Block 97), and the Next Research Protocol
(Block 95), and only when the upstream family-review signal is clearly the
expected one
(crypto_d1_strategy_candidate_family_review_contract_active is True,
strategy_candidate_family_review_verdict ==
STRATEGY_CANDIDATE_FAMILY_REVIEW_READY,
next_gate == CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_REQUIRED,
mode == RESEARCH_ONLY, read_only is True, executes is False) evaluates a proposed
bot-evidence plan packet on paper and returns a deterministic verdict.

It evaluates the SHAPE of a proposed evidence-interpretation plan only. It does
NOT acquire, fetch, inspect, load, validate, transform, or compute on any data,
does not run QA, baseline, backtest, or simulation, produces no trade signal,
reaches no broker / exchange / order / account / API surface, trades no paper and
no live, triggers no automation, writes no runtime, registry, ledger, dashboard,
or report state, opens no network, spawns no child process, writes no file, reads
no file, lists no directory, records no timestamp, mints no random id, reads no
environment, dynamically imports nothing, and NEVER modifies the external bot's
own repository or dashboard files. It selects no live trading strategy.

The contract encodes thirteen external-bot-evidence policy rules:
  1. External bot state is WATCH / SAFE_OBSERVE, never GO.
  2. Bot evidence is external evidence only, not execution permission.
  3. Strategy decisions allowed only because of a fail-safe or insufficient data
     are observe/log only.
  4. A minimum closed-trade proof is mandatory before any promotion.
  5. SOL is the main research candidate but blocked from execution
     (false-expansion/reversal risk, no sync confirmation).
  6. XRP is watchlist-only: strongest but lacks historical confirmation.
  7. BTC is dormant and blocked from expansion logic.
  8. ETH is early-pressure only.
  9. Multi-asset sync must reach 60+ with at least 2 synchronized assets before
     market confirmation can pass.
 10. Lead-lag and lagged-sync cannot be used as confirmation (propagation
     quality/improvement is zero).
 11. Adaptive ATR thresholds may be studied offline only; no live changes.
 12. Trade-coordinator rules are mandatory: max one open trade per symbol, no
     same-direction adds, treat exchanges as the same symbol, block opposite
     direction.
 13. No strategy promotion, no paper expansion, no live activation is authorized.

Reaching a BOT_EVIDENCE_RESEARCH_PLAN_READY verdict unlocks NOTHING real. It only
records, on paper, that a proposed evidence-interpretation plan stays in scope and
honours all thirteen rules -- and even that still requires a separate, later,
human step. Any upstream family-review signal that is missing, malformed, not
READY, in the wrong mode, executable, non-read-only, or pointed at a different
next gate yields the AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT
verdict.

Public API:
  - BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION
  - DEFAULT_BOT_EVIDENCE_RESEARCH_PLAN_LABEL
  - BOT_EVIDENCE_RESEARCH_PLAN_STATUS
  - BOT_EVIDENCE_RESEARCH_PLAN_SAFETY_POSTURE
  - BOT_EVIDENCE_RESEARCH_PLAN_STATE_ACTIVE
  - BOT_EVIDENCE_RESEARCH_PLAN_STATE_BLOCKED
  - BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_READY
  - BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_NEEDS_MORE_INFO
  - BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED
  - BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_PARKED
  - BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT
  - ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_VERDICTS
  - UPSTREAM_REQUIRED_FAMILY_REVIEW_VERDICT
  - UPSTREAM_REQUIRED_FAMILY_REVIEW_NEXT_GATE
  - UPSTREAM_REQUIRED_FAMILY_REVIEW_MODE
  - BOT_EVIDENCE_RESEARCH_PLAN_NEXT_REQUIRED_ACTION
  - BOT_EVIDENCE_RESEARCH_PLAN_CURRENT_STAGE
  - DECISION_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT_REQUIRED
  - NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_READY
  - NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_FIX_REQUIRED
  - NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_PARKED
  - NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_REJECTED
  - NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT
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
  - REQUIRED_BOT_EVIDENCE_RESEARCH_PLAN_FIELDS
  - BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_TEXT_FIELDS
  - BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_AFFIRMATIONS
  - BOT_EVIDENCE_RESEARCH_PLAN_FORBIDDEN_ALLOW_FLAGS
  - ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_MODES
  - AUTOMATED_APPROVAL_MARKERS
  - REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - evaluate_crypto_d1_bot_evidence_research_plan(packet)
  - build_crypto_d1_bot_evidence_research_plan_contract(signal, packet=None)
  - validate_crypto_d1_bot_evidence_research_plan_contract(contract)
  - render_crypto_d1_bot_evidence_research_plan_contract_markdown(contract)
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
    STRATEGY_CANDIDATE_FAMILY_REVIEW_VERDICT_READY as _FAMILY_REVIEW_VERDICT_READY,  # noqa: E501
    STRATEGY_CANDIDATE_FAMILY_REVIEW_SCHEMA_VERSION as _FAMILY_REVIEW_SCHEMA_VERSION,  # noqa: E501
    REQUIRED_MARKET_TYPE as _REVIEW_REQUIRED_MARKET_TYPE,
    REQUIRED_TIMEFRAME as _REVIEW_REQUIRED_TIMEFRAME,
)

__all__ = [
    "BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION",
    "DEFAULT_BOT_EVIDENCE_RESEARCH_PLAN_LABEL",
    "BOT_EVIDENCE_RESEARCH_PLAN_STATUS",
    "BOT_EVIDENCE_RESEARCH_PLAN_SAFETY_POSTURE",
    "BOT_EVIDENCE_RESEARCH_PLAN_STATE_ACTIVE",
    "BOT_EVIDENCE_RESEARCH_PLAN_STATE_BLOCKED",
    "BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_READY",
    "BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_NEEDS_MORE_INFO",
    "BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED",
    "BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_PARKED",
    "BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT",
    "ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_VERDICTS",
    "UPSTREAM_REQUIRED_FAMILY_REVIEW_VERDICT",
    "UPSTREAM_REQUIRED_FAMILY_REVIEW_NEXT_GATE",
    "UPSTREAM_REQUIRED_FAMILY_REVIEW_MODE",
    "BOT_EVIDENCE_RESEARCH_PLAN_NEXT_REQUIRED_ACTION",
    "BOT_EVIDENCE_RESEARCH_PLAN_CURRENT_STAGE",
    "DECISION_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_READY",
    "NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_FIX_REQUIRED",
    "NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_PARKED",
    "NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_REJECTED",
    "NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT",
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
    "REQUIRED_BOT_EVIDENCE_RESEARCH_PLAN_FIELDS",
    "BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_TEXT_FIELDS",
    "BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_AFFIRMATIONS",
    "BOT_EVIDENCE_RESEARCH_PLAN_FORBIDDEN_ALLOW_FLAGS",
    "ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_MODES",
    "AUTOMATED_APPROVAL_MARKERS",
    "REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "evaluate_crypto_d1_bot_evidence_research_plan",
    "build_crypto_d1_bot_evidence_research_plan_contract",
    "validate_crypto_d1_bot_evidence_research_plan_contract",
    "render_crypto_d1_bot_evidence_research_plan_contract_markdown",
]

BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_strategy_candidate_research_plan_contract.v1"
)
DEFAULT_BOT_EVIDENCE_RESEARCH_PLAN_LABEL = (
    "Strategy Factory Crypto-D1 External Bot Evidence Research Plan Contract"
)
BOT_EVIDENCE_RESEARCH_PLAN_STATUS = (
    "READ_ONLY_CRYPTO_D1_EXTERNAL_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT"
)

BOT_EVIDENCE_RESEARCH_PLAN_STATE_ACTIVE = (
    "CRYPTO_D1_EXTERNAL_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT_ACTIVE"
)
BOT_EVIDENCE_RESEARCH_PLAN_STATE_BLOCKED = (
    "CRYPTO_D1_EXTERNAL_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT_BLOCKED"
)

BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_READY = "BOT_EVIDENCE_RESEARCH_PLAN_READY"
BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_NEEDS_MORE_INFO = (
    "BOT_EVIDENCE_RESEARCH_PLAN_NEEDS_MORE_INFO"
)
BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED = (
    "BOT_EVIDENCE_RESEARCH_PLAN_REJECTED"
)
BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_PARKED = "BOT_EVIDENCE_RESEARCH_PLAN_PARKED"
BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT = (
    "AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT"
)

ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_VERDICTS: tuple[str, ...] = (
    BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_READY,
    BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_NEEDS_MORE_INFO,
    BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED,
    BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_PARKED,
    BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT,
)

# The exact upstream family-review signal this contract activates from (Block
# 101). The contract only becomes active when the upstream family-review contract
# is clearly READY, in RESEARCH_ONLY mode, read-only, non-executing, and pointed
# at exactly this research-plan contract being built next.
UPSTREAM_REQUIRED_FAMILY_REVIEW_VERDICT = _FAMILY_REVIEW_VERDICT_READY
UPSTREAM_REQUIRED_FAMILY_REVIEW_NEXT_GATE = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_REQUIRED"
)
UPSTREAM_REQUIRED_FAMILY_REVIEW_MODE = "RESEARCH_ONLY"

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry.
BOT_EVIDENCE_RESEARCH_PLAN_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_EXTERNAL_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT"
)
BOT_EVIDENCE_RESEARCH_PLAN_CURRENT_STAGE = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_REQUIRED"
)

DECISION_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT_REQUIRED = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_REQUIRED"
)

NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_READY = (
    "CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_READY_SEPARATE_HUMAN_NEXT_STEP_"
    "REQUIRED"
)
NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_FIX_REQUIRED = (
    "CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_FIX_REQUIRED"
)
NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_PARKED = (
    "CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_PARKED"
)
NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_REJECTED = (
    "CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_REJECTED"
)
NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT = (
    "AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT"
)

# Market/timeframe scope reused from Block 101 so this contract can never drift
# from the spot/D1 scope it interprets evidence against.
REQUIRED_MARKET_TYPE = str(_REVIEW_REQUIRED_MARKET_TYPE).strip().upper()
REQUIRED_TIMEFRAME = str(_REVIEW_REQUIRED_TIMEFRAME).strip().upper()

# The four assets the external bot evidence watches. Defined LOCALLY (this
# universe intentionally includes XRP and differs from the Block 101 research
# universe).
WATCHED_UNIVERSE: tuple[str, ...] = ("BTC", "ETH", "SOL", "XRP")
_WATCHED_UNIVERSE_SET: frozenset[str] = frozenset(WATCHED_UNIVERSE)

# Per-asset evidence stance (rules 5-8). Every stance is observe/blocked; none is
# an execution authorization.
ASSET_EVIDENCE_STANCES: dict[str, str] = {
    "SOL": "MAIN_CANDIDATE_BLOCKED_FROM_EXECUTION",
    "XRP": "WATCHLIST_ONLY",
    "BTC": "DORMANT_BLOCKED_FROM_EXPANSION",
    "ETH": "EARLY_PRESSURE_ONLY",
}
ASSET_EVIDENCE_STANCE_REASONS: dict[str, str] = {
    "SOL": "false_expansion_reversal_risk_and_no_sync_confirmation",
    "XRP": "strongest_but_insufficient_historical_confirmation",
    "BTC": "dormant_blocked_from_expansion_logic",
    "ETH": "early_pressure_only",
}

# Multi-asset sync gate (rule 9): market confirmation cannot pass below a 60 sync
# score with at least 2 synchronized assets.
MIN_MULTI_ASSET_SYNC_SCORE = 60
MIN_SYNCHRONIZED_ASSETS = 2

# Mandatory trade-coordinator rules (rule 12).
TRADE_COORDINATOR_RULES: tuple[str, ...] = (
    "max_one_open_trade_per_symbol",
    "no_same_direction_adds",
    "treat_exchanges_as_same_symbol",
    "block_opposite_direction",
)

# Bot-state policy (rule 1). A declared bot state must be one of the allowed
# observe-grade values; any GO/live/execute grade value is a hard REJECTED.
ALLOWED_BOT_STATE_VALUES: tuple[str, ...] = (
    "watch",
    "safe_observe",
    "safe-observe",
    "safe observe",
    "observe",
    "observe_only",
    "observe-only",
)
FORBIDDEN_BOT_STATE_VALUES: tuple[str, ...] = (
    "go",
    "go_live",
    "go-live",
    "live",
    "execute",
    "execution",
    "trade",
    "trading",
    "activate",
    "active_execution",
)
_ALLOWED_BOT_STATE_SET: frozenset[str] = frozenset(ALLOWED_BOT_STATE_VALUES)
_FORBIDDEN_BOT_STATE_SET: frozenset[str] = frozenset(FORBIDDEN_BOT_STATE_VALUES)

# Read-only, all-false safety posture. Every capability flag stays False.
BOT_EVIDENCE_RESEARCH_PLAN_SAFETY_POSTURE: dict[str, bool] = {
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

# Strings that mark a non-human / automated planner. A packet authored by any of
# these is rejected: only a human planner may record this paper decision.
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
# REJECTED (the plan tries to operate outside research-only / plan-only scope).
ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_MODES: tuple[str, ...] = (
    "research_only",
    "research-only",
    "research only",
    "plan_only",
    "plan-only",
    "plan only",
    "research_only_plan_only",
)

# Descriptive text fields a human must record on a proposed bot-evidence plan
# packet. Absent -> NEEDS_MORE_INFO.
BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_TEXT_FIELDS: tuple[str, ...] = (
    "evidence_plan_packet_id",
    "upstream_family_review_id",
    "family_review_contract_version",
    "evidence_source_description",
    "plan_scope",
    "plan_mode",
    "declared_bot_state",
    "watched_universe",
    "asset_stance_summary",
    "multi_asset_sync_interpretation",
    "lead_lag_interpretation",
    "atr_threshold_study_boundary",
    "trade_coordinator_rule_summary",
    "closed_trade_proof_requirement",
    "planner_name_or_id",
    "plan_decision_rationale",
    "next_step_boundary",
    "plan_notes",
)

# Affirmation flags the packet must carry (each affirmed True). The thirteen
# external-bot-evidence rules plus the generic research/plan-only acknowledgements.
# A present-but-not-affirmed value is a request to admit or allow that thing -- a
# hard REJECTED. An absent value is a missing requirement (NEEDS_MORE_INFO).
BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_AFFIRMATIONS: tuple[str, ...] = (
    # Rule 1
    "external_bot_state_is_watch_safe_observe_not_go",
    # Rule 2
    "bot_evidence_is_external_evidence_only",
    "bot_evidence_not_execution_permission",
    # Rule 3
    "failsafe_or_insufficient_data_allowed_is_observe_log_only",
    # Rule 4
    "closed_trade_proof_required_before_promotion",
    # Rule 5
    "sol_main_candidate_blocked_from_execution",
    # Rule 6
    "xrp_watchlist_only_insufficient_history",
    # Rule 7
    "btc_dormant_blocked_from_expansion",
    # Rule 8
    "eth_early_pressure_only",
    # Rule 9
    "multi_asset_sync_threshold_required_before_confirmation",
    # Rule 10
    "lead_lag_not_used_as_confirmation",
    "lagged_sync_not_used_as_confirmation",
    # Rule 11
    "adaptive_atr_thresholds_offline_study_only",
    "no_live_threshold_changes",
    # Rule 12
    "trade_coordinator_max_one_open_trade_per_symbol",
    "trade_coordinator_no_same_direction_adds",
    "trade_coordinator_treat_exchanges_as_same_symbol",
    "trade_coordinator_block_opposite_direction",
    # Rule 13
    "no_strategy_promotion",
    "no_paper_expansion",
    "no_live_activation",
    # Generic research/plan-only acknowledgements
    "explicit_human_planning",
    "research_only_acknowledgement",
    "plan_only_acknowledgement",
    "no_execution_acknowledgement",
    "no_real_data_acquisition",
    "no_backtest_run",
    "no_runtime_write",
    "no_dashboard_write",
    "no_broker_exchange",
    "do_not_modify_external_bot",
)

# Every required True-flag.
_REQUIRED_TRUE_FLAGS: tuple[str, ...] = (
    BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_AFFIRMATIONS
)

# Full set of required bot-evidence plan packet fields.
REQUIRED_BOT_EVIDENCE_RESEARCH_PLAN_FIELDS: tuple[str, ...] = (
    BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_TEXT_FIELDS
    + BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_AFFIRMATIONS
)

# Positive allow/grant flags a plan packet must NOT request -- any truthy value
# forces a hard REJECTED. Generic capability flags plus bot-evidence-specific
# ones (execution, SOL/BTC unblocking, lead-lag confirmation, live thresholds,
# trade-coordinator overrides, promotion, and external-bot modification).
BOT_EVIDENCE_RESEARCH_PLAN_FORBIDDEN_ALLOW_FLAGS: tuple[str, ...] = (
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

# Evidence-plan-phase blocked capabilities (named for this lane).
_BOT_EVIDENCE_BLOCKED_CAPABILITIES: tuple[str, ...] = (
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

_BOT_EVIDENCE_REFERENCE_PLACEHOLDER = (
    "Crypto-D1 external-bot-evidence plan packet is a paper placeholder "
    "describing HOW SPARTA_BRAIN should interpret the uploaded bot/dashboard "
    "evidence: the declared observe-grade bot state, the BTC/ETH/SOL/XRP "
    "watched universe and their per-asset stances, the multi-asset-sync gate, "
    "the lead-lag / lagged-sync exclusion, the offline-only ATR-threshold "
    "study boundary, the mandatory trade-coordinator rules, and the "
    "closed-trade-proof requirement -- it plans on paper only, runs nothing, "
    "acquires nothing, modifies no external bot, and executes nothing."
)

_BOT_EVIDENCE_VERDICT_RATIONALE_PLACEHOLDER = (
    "Bot-evidence research-plan verdict rationale is a paper placeholder for a "
    "human-recorded judgement of whether a proposed evidence-interpretation "
    "plan honours all thirteen external-bot-evidence rules, and its supporting "
    "reason."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 external bot evidence research plan contract template "
    "and is execution-free.",
    "It records, on paper, HOW SPARTA_BRAIN interprets the uploaded external "
    "bot evidence; it runs no research and touches no external bot.",
    "It evaluates a paper evidence-plan packet only and writes no report file.",
    "External bot state is WATCH / SAFE_OBSERVE only; it is never GO, and the "
    "evidence is never execution permission.",
    "SOL stays blocked from execution, XRP is watchlist-only, BTC is dormant "
    "and blocked from expansion, and ETH is early-pressure only.",
    "Market confirmation needs a multi-asset sync score of at least "
    "60 with at least 2 synchronized assets; lead-lag and lagged-sync are "
    "never confirmation.",
    "Adaptive ATR thresholds may be studied offline only; no live threshold "
    "change is authorized.",
    "Trade-coordinator rules are mandatory: max one open trade per symbol, no "
    "same-direction adds, exchanges treated as the same symbol, opposite "
    "direction blocked.",
    "No strategy promotion, no paper expansion, and no live activation is "
    "authorized, and a minimum closed-trade proof is required before any "
    "promotion.",
    "It never modifies the external bot's own repository or dashboard files.",
    "A human planner alone may record this verdict; no automated planner is "
    "accepted, and any READY still requires a separate, later, human step.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human planner must record a bot-evidence research-plan verdict with a "
    "supporting rationale on paper.",
    "A human planner must confirm the declared bot state is an observe-grade "
    "value (watch / safe_observe / observe) and never GO/live/execute.",
    "A human planner must confirm the per-asset stances: SOL blocked from "
    "execution, XRP watchlist-only, BTC dormant/blocked from expansion, ETH "
    "early-pressure only.",
    "A human planner must confirm market confirmation stays gated behind a 60+ "
    "multi-asset sync score with at least 2 synchronized assets, and that "
    "lead-lag / lagged-sync are excluded as confirmation.",
    "A human planner must confirm ATR-threshold work stays offline-only, the "
    "four trade-coordinator rules hold, and a closed-trade proof precedes any "
    "promotion.",
    "No automated step, no execution, no promotion, no paper expansion, no "
    "live activation, and no modification of the external bot may proceed.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
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
    "crypto_d1_bot_evidence_research_plan_contract_active",
    "crypto_d1_bot_evidence_research_plan_contract_state",
    "crypto_d1_strategy_candidate_family_review_contract_recognized",
    "upstream_family_review_verdict",
    "upstream_family_review_next_gate",
    "upstream_family_review_mode",
    "bot_evidence_research_plan_contract_required",
    "bot_evidence_research_plan_next_required_action",
    "bot_evidence_research_plan_current_stage",
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
    "evidence_plan_packet_reference_placeholder",
    "bot_evidence_research_plan_verdict",
    "bot_evidence_research_plan_verdict_reasons",
    "evaluated_bot_evidence_plan_packet",
    "allowed_bot_evidence_research_plan_verdicts",
    "required_bot_evidence_research_plan_fields",
    "bot_evidence_research_plan_required_text_fields",
    "bot_evidence_research_plan_required_affirmations",
    "bot_evidence_research_plan_forbidden_allow_flags",
    "allowed_bot_evidence_research_plan_modes",
    "automated_approval_markers",
    "bot_evidence_research_plan_verdict_rationale_placeholder",
    "bot_evidence_research_plan_blocked_capabilities",
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
    return dict(BOT_EVIDENCE_RESEARCH_PLAN_SAFETY_POSTURE)


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
    admitted/relaxed affirmation, a disallowed mode, a GO/disallowed bot state,
    a market-confirmation claim below the multi-asset-sync gate, a non-core asset
    in the watched universe, an automated planner, or granted authority."""
    reasons: list[str] = []

    for flag in BOT_EVIDENCE_RESEARCH_PLAN_FORBIDDEN_ALLOW_FLAGS:
        if _truthy(packet.get(flag)):
            reasons.append(f"forbidden_allow:{flag}")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag in packet and not _affirm(packet.get(flag)):
            reasons.append(f"affirmation_relaxed:{flag}")

    mode = packet.get("plan_mode")
    if not _present(mode):
        mode = packet.get("mode")
    if _present(mode) and _scalar(mode) not in (
        ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_MODES
    ):
        reasons.append("disallowed_mode")

    bot_state = packet.get("declared_bot_state")
    if _present(bot_state):
        state_value = _scalar(bot_state)
        if state_value in _FORBIDDEN_BOT_STATE_SET:
            reasons.append("bot_state_go_not_permitted")
        elif state_value not in _ALLOWED_BOT_STATE_SET:
            reasons.append("disallowed_bot_state")

    if _truthy(packet.get("claims_market_confirmation")):
        score = _as_number(packet.get("claimed_multi_asset_sync_score"))
        count = _as_number(packet.get("claimed_synchronized_asset_count"))
        if (
            score is None
            or score < MIN_MULTI_ASSET_SYNC_SCORE
            or count is None
            or count < MIN_SYNCHRONIZED_ASSETS
        ):
            reasons.append("market_confirmation_below_multi_asset_sync_threshold")

    watched = _upper_token_set(packet.get("watched_universe"))
    extras = watched - _WATCHED_UNIVERSE_SET
    if extras:
        reasons.append("non_core_assets_in_watched_universe")

    for key in (
        "planner_type",
        "plan_author_type",
        "planning_method",
        "plan_source",
        "authored_by_type",
        "planner_name_or_id",
    ):
        if _scalar(packet.get(key)) in AUTOMATED_APPROVAL_MARKERS:
            reasons.append(f"automated_planner:{key}")

    for key in ("grants_capabilities", "authorizes", "granted_capabilities"):
        listed = packet.get(key)
        if isinstance(listed, (list, tuple)) and len(listed) > 0:
            reasons.append(f"grants_listed:{key}")

    return tuple(reasons)


def _park_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return parking reasons when a planner explicitly parks or defers the whole
    bot-evidence research-plan lane."""
    reasons: list[str] = []
    park_values = {
        "park", "parked", "defer", "deferred", "hold", "on_hold",
        "postpone", "postponed",
    }

    for flag in ("park", "parked", "defer", "deferred", "hold"):
        if _truthy(packet.get(flag)):
            reasons.append("planner_parked_bot_evidence_research_plan")
            break

    if _scalar(packet.get("planner_decision")) in park_values:
        reasons.append("planner_decision_parked")
    if _scalar(packet.get("plan_decision")) in park_values:
        reasons.append("plan_decision_parked")

    return tuple(reasons)


def _missing_reasons(packet: dict[str, Any]) -> tuple[str, ...]:
    """Return unmet requirements for an otherwise-safe bot-evidence plan packet:
    absent text fields, unaffirmed flags, or an incomplete BTC/ETH/SOL/XRP
    watched universe."""
    missing: list[str] = []

    for key in BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_TEXT_FIELDS:
        if not _present(packet.get(key)):
            missing.append(f"{key}_required")

    for flag in _REQUIRED_TRUE_FLAGS:
        if flag not in packet:
            missing.append(f"{flag}_must_be_affirmed_true")

    watched = _upper_token_set(packet.get("watched_universe"))
    for asset in WATCHED_UNIVERSE:
        if asset not in watched:
            missing.append(f"watched_universe_missing_{asset}")

    return tuple(missing)


def evaluate_crypto_d1_bot_evidence_research_plan(
    packet: Any,
) -> dict[str, Any]:
    """Return a deterministic verdict for a proposed bot-evidence plan packet.
    Pure; no I/O, no mutation, no timestamp, no random id. Unknown/malformed
    inputs never raise. REJECTED (permits a dangerous capability / relaxes an
    affirmation / off-scope value / GO bot state / sub-threshold confirmation /
    non-core asset / automated planner / authority-granting) is checked before
    parking, and parking before completeness, so an unsafe plan is rejected even
    when it would otherwise park or merely need more info."""
    p = packet if isinstance(packet, dict) else {}

    if not p:
        return {
            "verdict": (
                BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_NEEDS_MORE_INFO
            ),
            "reasons": ("bot_evidence_research_plan_packet_missing",),
        }

    rejected = _reject_reasons(p)
    if rejected:
        return {
            "verdict": BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_REJECTED,
            "reasons": rejected,
        }

    park = _park_reasons(p)
    if park:
        return {
            "verdict": BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_PARKED,
            "reasons": park,
        }

    missing = _missing_reasons(p)
    if not missing:
        return {
            "verdict": BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_READY,
            "reasons": (
                "research_only_bot_evidence_plan_fully_specified_honours_all_"
                "thirteen_rules_watch_safe_observe_only_sol_blocked_xrp_"
                "watchlist_btc_dormant_eth_early_pressure_sync_gate_60_2_no_"
                "lead_lag_confirmation_atr_offline_only_trade_coordinator_"
                "rules_and_blocks_every_real_world_capability",
            ),
        }

    return {
        "verdict": BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_NEEDS_MORE_INFO,
        "reasons": missing,
    }


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_EXTERNAL_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT_ONLY"
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
        tuple(
            safe.get("allowed_bot_evidence_research_plan_verdicts") or ()
        )
        == ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_VERDICTS
    )
    fields_ok = (
        tuple(
            safe.get("required_bot_evidence_research_plan_fields") or ()
        )
        == REQUIRED_BOT_EVIDENCE_RESEARCH_PLAN_FIELDS
    )
    text_fields_ok = (
        tuple(
            safe.get("bot_evidence_research_plan_required_text_fields") or ()
        )
        == BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_TEXT_FIELDS
    )
    affirmations_ok = (
        tuple(
            safe.get("bot_evidence_research_plan_required_affirmations") or ()
        )
        == BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_AFFIRMATIONS
    )
    forbidden_flags_ok = (
        tuple(
            safe.get("bot_evidence_research_plan_forbidden_allow_flags") or ()
        )
        == BOT_EVIDENCE_RESEARCH_PLAN_FORBIDDEN_ALLOW_FLAGS
    )
    modes_ok = (
        tuple(safe.get("allowed_bot_evidence_research_plan_modes") or ())
        == ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_MODES
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
        safe.get("bot_evidence_research_plan_verdict")
        in ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_VERDICTS
    )
    blocked_present_ok = (
        len(
            tuple(
                safe.get("bot_evidence_research_plan_blocked_capabilities")
                or ()
            )
        )
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
        "allowed_bot_evidence_research_plan_verdicts_ok": verdicts_ok,
        "required_bot_evidence_research_plan_fields_ok": fields_ok,
        "bot_evidence_research_plan_required_text_fields_ok": text_fields_ok,
        "bot_evidence_research_plan_required_affirmations_ok": affirmations_ok,
        "bot_evidence_research_plan_forbidden_allow_flags_ok": (
            forbidden_flags_ok
        ),
        "allowed_bot_evidence_research_plan_modes_ok": modes_ok,
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
        "bot_evidence_research_plan_verdict_value_ok": verdict_value_ok,
        "bot_evidence_research_plan_blocked_capabilities_present": (
            blocked_present_ok
        ),
        "operator_notes_present": notes_ok,
        "human_operator_required_next_steps_present": next_steps_ok,
        "missing_required_fields": missing,
    }


def validate_crypto_d1_bot_evidence_research_plan_contract(
    contract: dict[str, Any],
) -> dict[str, Any]:
    """Return deterministic validation of a crypto-d1 external bot evidence
    research plan contract template. Pure; no I/O."""
    return _validate(contract)


def build_crypto_d1_bot_evidence_research_plan_contract(
    upstream_family_review_signal: Any,
    bot_evidence_plan_packet: Any = None,
) -> dict[str, Any]:
    """Return a fresh deterministic read-only crypto-d1 external bot evidence
    research plan contract template plus a paper verdict for a proposed plan
    packet.

    Pure; no I/O, no mutation, no timestamp, no random id, no dynamic import,
    and no modification of any external bot. Unknown/malformed inputs never
    raise. The contract becomes active solely when the upstream Block 101
    family-review signal is clearly READY for this gate:
    crypto_d1_strategy_candidate_family_review_contract_active is True,
    strategy_candidate_family_review_verdict ==
    STRATEGY_CANDIDATE_FAMILY_REVIEW_READY,
    next_gate == CRYPTO_D1_STRATEGY_CANDIDATE_RESEARCH_PLAN_CONTRACT_REQUIRED,
    mode == RESEARCH_ONLY, read_only is True, and executes is False. When
    inactive (missing, dirty, ambiguous, or not-READY upstream), the verdict is
    AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT regardless of the
    packet. Even when active and READY, every authorization field stays False.
    Returned dicts are fresh."""
    signal = (
        upstream_family_review_signal
        if isinstance(upstream_family_review_signal, dict)
        else {}
    )

    sig_verdict = _field(signal, "strategy_candidate_family_review_verdict")
    sig_next_gate = _field(signal, "next_gate")
    sig_mode = _field(signal, "mode")
    active_flag_ok = (
        signal.get(
            "crypto_d1_strategy_candidate_family_review_contract_active"
        )
        is True
    )
    read_only_ok = signal.get("read_only") is True
    executes_false = signal.get("executes") is False
    verdict_ok = sig_verdict == UPSTREAM_REQUIRED_FAMILY_REVIEW_VERDICT
    next_gate_ok = sig_next_gate == UPSTREAM_REQUIRED_FAMILY_REVIEW_NEXT_GATE
    mode_ok = sig_mode == UPSTREAM_REQUIRED_FAMILY_REVIEW_MODE

    contract_active = bool(
        active_flag_ok
        and verdict_ok
        and next_gate_ok
        and mode_ok
        and read_only_ok
        and executes_false
    )

    if contract_active:
        evaluation = evaluate_crypto_d1_bot_evidence_research_plan(
            bot_evidence_plan_packet
        )
        verdict = evaluation["verdict"]
        reasons = tuple(evaluation["reasons"])
    else:
        verdict = BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_AWAIT
        reasons = (
            "await_crypto_d1_strategy_candidate_family_review_contract",
        )

    state = (
        BOT_EVIDENCE_RESEARCH_PLAN_STATE_ACTIVE
        if contract_active
        else BOT_EVIDENCE_RESEARCH_PLAN_STATE_BLOCKED
    )

    if not contract_active:
        next_gate = (
            NEXT_GATE_AWAIT_CRYPTO_D1_STRATEGY_CANDIDATE_FAMILY_REVIEW_CONTRACT
        )
    elif verdict == BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_READY:
        next_gate = NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_READY
    elif verdict == BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_NEEDS_MORE_INFO:
        next_gate = (
            NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_FIX_REQUIRED
        )
    elif verdict == BOT_EVIDENCE_RESEARCH_PLAN_VERDICT_PARKED:
        next_gate = NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_PARKED
    else:
        next_gate = NEXT_GATE_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_REJECTED

    bot_evidence_research_plan_contract_required = (
        DECISION_CRYPTO_D1_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT_REQUIRED
        if contract_active
        else ""
    )

    echoed_packet = (
        dict(bot_evidence_plan_packet)
        if isinstance(bot_evidence_plan_packet, dict)
        else {}
    )

    contract = {
        "schema_version": BOT_EVIDENCE_RESEARCH_PLAN_SCHEMA_VERSION,
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
        "label": DEFAULT_BOT_EVIDENCE_RESEARCH_PLAN_LABEL,
        "status": BOT_EVIDENCE_RESEARCH_PLAN_STATUS,
        "stage": (
            "CRYPTO_D1_EXTERNAL_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT_ONLY"
        ),
        "mode": "RESEARCH_ONLY",
        "protocol_id": _PROTOCOL_ID,
        "protocol_name": _PROTOCOL_NAME,
        "crypto_d1_bot_evidence_research_plan_contract_active": (
            contract_active
        ),
        "crypto_d1_bot_evidence_research_plan_contract_state": state,
        "crypto_d1_strategy_candidate_family_review_contract_recognized": (
            contract_active
        ),
        "upstream_family_review_verdict": sig_verdict,
        "upstream_family_review_next_gate": sig_next_gate,
        "upstream_family_review_mode": sig_mode,
        "bot_evidence_research_plan_contract_required": (
            bot_evidence_research_plan_contract_required
        ),
        "bot_evidence_research_plan_next_required_action": (
            BOT_EVIDENCE_RESEARCH_PLAN_NEXT_REQUIRED_ACTION
        ),
        "bot_evidence_research_plan_current_stage": (
            BOT_EVIDENCE_RESEARCH_PLAN_CURRENT_STAGE
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
        "evidence_plan_packet_reference_placeholder": (
            _BOT_EVIDENCE_REFERENCE_PLACEHOLDER
        ),
        "bot_evidence_research_plan_verdict": verdict,
        "bot_evidence_research_plan_verdict_reasons": reasons,
        "evaluated_bot_evidence_plan_packet": echoed_packet,
        "allowed_bot_evidence_research_plan_verdicts": (
            ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_VERDICTS
        ),
        "required_bot_evidence_research_plan_fields": (
            REQUIRED_BOT_EVIDENCE_RESEARCH_PLAN_FIELDS
        ),
        "bot_evidence_research_plan_required_text_fields": (
            BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_TEXT_FIELDS
        ),
        "bot_evidence_research_plan_required_affirmations": (
            BOT_EVIDENCE_RESEARCH_PLAN_REQUIRED_AFFIRMATIONS
        ),
        "bot_evidence_research_plan_forbidden_allow_flags": (
            BOT_EVIDENCE_RESEARCH_PLAN_FORBIDDEN_ALLOW_FLAGS
        ),
        "allowed_bot_evidence_research_plan_modes": (
            ALLOWED_BOT_EVIDENCE_RESEARCH_PLAN_MODES
        ),
        "automated_approval_markers": AUTOMATED_APPROVAL_MARKERS,
        "bot_evidence_research_plan_verdict_rationale_placeholder": (
            _BOT_EVIDENCE_VERDICT_RATIONALE_PLACEHOLDER
        ),
        "bot_evidence_research_plan_blocked_capabilities": (
            _BOT_EVIDENCE_BLOCKED_CAPABILITIES
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


def render_crypto_d1_bot_evidence_research_plan_contract_markdown(
    contract: dict[str, Any],
) -> str:
    """Return deterministic, non-empty markdown for a crypto-d1 external bot
    evidence research plan contract template. Pure; writes no file.
    Informational only."""
    verdicts = (
        contract.get("allowed_bot_evidence_research_plan_verdicts") or ()
    )
    fields = (
        contract.get("required_bot_evidence_research_plan_fields") or ()
    )
    text_fields = (
        contract.get("bot_evidence_research_plan_required_text_fields") or ()
    )
    affirmations = (
        contract.get("bot_evidence_research_plan_required_affirmations") or ()
    )
    forbidden_flags = (
        contract.get("bot_evidence_research_plan_forbidden_allow_flags") or ()
    )
    modes = contract.get("allowed_bot_evidence_research_plan_modes") or ()
    markers = contract.get("automated_approval_markers") or ()
    watched = contract.get("watched_universe") or ()
    stances = contract.get("asset_evidence_stances") or {}
    coordinator = contract.get("trade_coordinator_rules") or ()
    allowed_states = contract.get("allowed_bot_state_values") or ()
    forbidden_states = contract.get("forbidden_bot_state_values") or ()
    reasons = (
        contract.get("bot_evidence_research_plan_verdict_reasons") or ()
    )
    blocked = (
        contract.get("bot_evidence_research_plan_blocked_capabilities") or ()
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
        "# Strategy Factory Crypto-D1 External Bot Evidence Research Plan "
        "Contract"
    )
    lines.append("")
    lines.append(
        "Template only: this records, on paper, HOW SPARTA_BRAIN interprets "
        "the uploaded external bot evidence. It is research-only / plan-only, "
        "runs nothing, acquires no data, connects to no venue, selects no live "
        "strategy, promotes nothing, modifies no external bot repository, "
        "names only placeholders, and grants no capability."
    )
    lines.append("")
    lines.append(f"Schema: `{contract.get('schema_version', '')}`")
    lines.append(
        "Family review contract schema: "
        f"`{contract.get('crypto_d1_strategy_candidate_family_review_contract_schema_version', '')}`"  # noqa: E501
    )
    lines.append(f"Protocol ID: {contract.get('protocol_id', '')}")
    lines.append(f"Protocol name: {contract.get('protocol_name', '')}")
    lines.append(f"Status: {contract.get('status', '')}")
    lines.append(
        "Stage: CRYPTO_D1_EXTERNAL_BOT_EVIDENCE_RESEARCH_PLAN_CONTRACT_ONLY"
    )
    lines.append("Mode: RESEARCH_ONLY")
    lines.append(
        "Contract active: "
        f"{contract.get('crypto_d1_bot_evidence_research_plan_contract_active', '')}"  # noqa: E501
    )
    lines.append(
        "Contract state: "
        f"{contract.get('crypto_d1_bot_evidence_research_plan_contract_state', '')}"  # noqa: E501
    )
    lines.append(
        "Upstream family review verdict: "
        f"{contract.get('upstream_family_review_verdict', '')}"
    )
    lines.append(
        "Upstream family review next gate: "
        f"{contract.get('upstream_family_review_next_gate', '')}"
    )
    lines.append(
        "Upstream family review mode: "
        f"{contract.get('upstream_family_review_mode', '')}"
    )
    lines.append(
        "Verdict: "
        f"{contract.get('bot_evidence_research_plan_verdict', '')}"
    )
    lines.append(f"Next gate: {contract.get('next_gate', '')}")
    lines.append("Human approval required: True")
    lines.append("Read only: True")
    lines.append("Executes: False")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(
        f"Required market type: {contract.get('required_market_type', '')}"
    )
    lines.append(
        f"Required timeframe: {contract.get('required_timeframe', '')}"
    )
    lines.append(
        "Multi-asset sync gate: "
        f"{contract.get('min_multi_asset_sync_score', '')}+ score with "
        f"{contract.get('min_synchronized_assets', '')}+ synchronized assets"
    )
    lines.append("")
    lines.append("## Watched Universe And Asset Stances")
    lines.append("")
    for asset in watched:
        lines.append(f"- `{asset}`: {stances.get(asset, '')}")
    lines.append("")
    lines.append("## Allowed Bot State Values")
    lines.append("")
    for x in allowed_states:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Forbidden Bot State Values")
    lines.append("")
    for x in forbidden_states:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Trade Coordinator Rules")
    lines.append("")
    for x in coordinator:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Evidence Plan Packet Reference")
    lines.append("")
    lines.append(
        "Evidence plan packet reference: "
        f"{contract.get('evidence_plan_packet_reference_placeholder', '')}"
    )
    lines.append("")
    lines.append("## Verdict Reasons")
    lines.append("")
    for x in reasons:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Verdicts")
    lines.append("")
    for x in verdicts:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Plan Fields")
    lines.append("")
    for x in fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Text Fields")
    lines.append("")
    for x in text_fields:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Required Affirmations")
    lines.append("")
    for x in affirmations:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Forbidden Allow Flags")
    lines.append("")
    for x in forbidden_flags:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Allowed Modes")
    lines.append("")
    for x in modes:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Automated Approval Markers")
    lines.append("")
    for x in markers:
        lines.append(f"- `{x}`")
    lines.append("")
    lines.append("## Verdict Rationale")
    lines.append("")
    lines.append(
        "Verdict rationale: "
        f"{contract.get('bot_evidence_research_plan_verdict_rationale_placeholder', '')}"  # noqa: E501
    )
    lines.append("")
    lines.append("## Blocked Capabilities (Plan Phase)")
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

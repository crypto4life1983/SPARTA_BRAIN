"""SPARTA Offline Strategy Factory - CRYPTO-D1 NEXT RESEARCH PROTOCOL.

A PURE, stdlib-only *read-only protocol specification* for the next Crypto-D1
research lane, defined after the Crypto-D1 research-only dry-run governance lane
was closed/archived (Bundle 54). It is a *plan on paper*: it states which assets,
market type, timeframe, and candidate strategy families a future research lane
should compare, which future data it would require, which future validation it
would run, and the pass/watch/fail rules that would judge a candidate -- all
WITHOUT doing any of it.

It executes NOTHING. It does not run the Strategy Factory, does not acquire,
fetch, inspect, load, validate, transform, or compute on any data, does not run
QA, does not run a baseline, does not backtest, does not simulate, produces no
trade signal, reaches no broker / exchange / order / account / API surface,
trades no paper and no live, triggers no automation, writes no runtime,
registry, ledger, dashboard, or report state, opens no network, spawns no
subprocess, writes no file, reads no file, lists no directory, records no
timestamp, mints no random id, reads no environment, and dynamically imports
nothing.

Defining this protocol unlocks NOTHING real. Every future data, QA, baseline,
backtest, simulation, paper/live, broker/exchange, automation, and runtime/
registry/dashboard write stays blocked and human-gated. The protocol only
recommends the *next* research-only paper bundle to build; it authorizes no
real-world action.

Public API:
  - PROTOCOL_SCHEMA_VERSION
  - PROTOCOL_ID
  - PROTOCOL_NAME
  - PROTOCOL_MODE
  - RESEARCH_UNIVERSE
  - MARKET_TYPE
  - TIMEFRAME
  - NEXT_REQUIRED_ACTION
  - PROTOCOL_SAFETY_POSTURE
  - get_protocol()
  - get_research_universe()
  - get_candidate_strategy_families()
  - get_required_future_data_spec()
  - get_required_future_validation_steps()
  - get_prohibited_actions()
  - get_safety_gates()
  - get_pass_watch_fail_rules()
  - get_next_bundle_recommendation()
  - get_safety_posture()
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "PROTOCOL_SCHEMA_VERSION",
    "PROTOCOL_ID",
    "PROTOCOL_NAME",
    "PROTOCOL_MODE",
    "RESEARCH_UNIVERSE",
    "MARKET_TYPE",
    "TIMEFRAME",
    "NEXT_REQUIRED_ACTION",
    "PROTOCOL_SAFETY_POSTURE",
    "get_protocol",
    "get_research_universe",
    "get_candidate_strategy_families",
    "get_required_future_data_spec",
    "get_required_future_validation_steps",
    "get_prohibited_actions",
    "get_safety_gates",
    "get_pass_watch_fail_rules",
    "get_next_bundle_recommendation",
    "get_safety_posture",
]

PROTOCOL_SCHEMA_VERSION = "strategy_factory_crypto_d1_next_research_protocol.v1"
PROTOCOL_ID = "CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_V1"
PROTOCOL_NAME = "Crypto-D1 Strategy Candidate Protocol v1"
PROTOCOL_MODE = "RESEARCH_ONLY"

# Research universe: spot-only, daily-candle-only, research-only.
RESEARCH_UNIVERSE = ("BTC", "ETH", "SOL")
MARKET_TYPE = "SPOT"
TIMEFRAME = "D1"

# The single next required action this protocol recommends. It only proposes
# BUILDING the next research-only paper contract; it authorizes no real action.
NEXT_REQUIRED_ACTION = "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_PROTOCOL_CONTRACT"

# Read-only safety posture: nothing here can execute or mutate anything; every
# real-world capability stays blocked and human-gated.
PROTOCOL_SAFETY_POSTURE = {
    "mode": PROTOCOL_MODE,
    "read_only": True,
    "executes": False,
    "human_approval_required": True,
    "acquires_data": False,
    "calls_api": False,
    "connects_exchange_or_broker": False,
    "inspects_market_data": False,
    "loads_dataset": False,
    "runs_qa": False,
    "runs_baseline": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "generates_trade_signal": False,
    "paper_or_live": False,
    "order_logic": False,
    "triggers_automation": False,
    "writes_runtime_state": False,
    "writes_registry": False,
    "writes_dashboard": False,
    "writes_ledger": False,
}

# --- candidate strategy families (concept only, nothing is computed) --------

_CANDIDATE_STRATEGY_FAMILIES = (
    {
        "family_id": "MOMENTUM_TREND_CONTINUATION",
        "name": "Momentum / Trend Continuation",
        "concept": (
            "Stay with an established up-trend until it weakens; the edge, if "
            "any, comes from persistence of returns, not prediction."
        ),
        "definition_points": (
            "Trend confirmation before entry (e.g. price above a long moving "
            "average, or positive multi-window return).",
            "Momentum measured by moving-average relationship or return over a "
            "lookback window.",
            "Avoid overfit signals: prefer few, robust, widely-known windows "
            "over many tuned thresholds.",
            "Continuation logic, not bottom-picking.",
        ),
        "possible_later_metrics": (
            "CAGR", "Sharpe", "max_drawdown", "hit_rate",
            "avg_trade_duration", "turnover",
        ),
        "research_only": True,
    },
    {
        "family_id": "BREAKOUT_DONCHIAN_VOLATILITY_EXPANSION",
        "name": "Breakout / Donchian / Volatility Expansion",
        "concept": (
            "Enter when price breaks a recent range high, on the idea that a "
            "range break with expanding volatility can start a directional "
            "move."
        ),
        "definition_points": (
            "Breakout window concept: a rolling N-day high/low channel "
            "(Donchian-style) defines the breakout level.",
            "Volatility confirmation: breakout taken more seriously when range "
            "or true-range is expanding, not contracting.",
            "False-breakout risk: many breakouts fail; a filter or confirmation "
            "is needed to avoid being repeatedly faked out.",
            "Symmetric concept for shorts is out of scope (spot, long-only "
            "research first).",
        ),
        "possible_later_metrics": (
            "CAGR", "Sharpe", "max_drawdown", "false_breakout_rate",
            "profit_factor", "turnover",
        ),
        "research_only": True,
    },
    {
        "family_id": "PULLBACK_MEAN_REVERSION_AFTER_STRONG_TREND",
        "name": "Pullback / Mean Reversion After Strong Trend",
        "concept": (
            "Buy a shallow pullback inside an already-confirmed up-trend; this "
            "is reversion to a trend, not reversion against one."
        ),
        "definition_points": (
            "Only act after an identified trend/regime is up; never in a "
            "down-trend or undefined regime.",
            "Pullback depth concept: a modest retracement (e.g. to a shorter "
            "moving average) rather than a deep collapse.",
            "Avoid knife-catching: no buying free-falling price with no trend "
            "support beneath it.",
            "Exit back toward continuation, not a fixed reversal target.",
        ),
        "possible_later_metrics": (
            "CAGR", "Sharpe", "max_drawdown", "win_rate",
            "avg_adverse_excursion", "turnover",
        ),
        "research_only": True,
    },
    {
        "family_id": "REGIME_FILTER_LAYER",
        "name": "Regime Filter Layer",
        "concept": (
            "A classification layer (bull / bear / range) that gates which "
            "strategy family is allowed to act; it is a filter, not a strategy "
            "by itself."
        ),
        "definition_points": (
            "Classify each asset/day as bull, bear, or range using simple, "
            "stable rules (e.g. long moving-average slope and a volatility/"
            "range band).",
            "Regime may gate which family is active: e.g. momentum/pullback in "
            "bull, breakout in range-to-expansion, stand-aside in bear.",
            "Regime must NOT be optimized into a curve fit: prefer few, "
            "explainable thresholds; treat regime rules as fixed, not tuned per "
            "asset.",
            "The layer is shared across families to keep comparisons fair.",
        ),
        "possible_later_metrics": (
            "regime_stability", "time_in_each_regime",
            "per_regime_return", "per_regime_drawdown",
        ),
        "research_only": True,
    },
)

# --- future data requirements (DEFINED only; nothing is acquired) -----------

_REQUIRED_FUTURE_DATA_SPEC = {
    "assets": ("BTC", "ETH", "SOL"),
    "market_type": "SPOT",
    "timeframe": "D1",
    "fields": ("open", "high", "low", "close", "volume"),
    "timezone": "UTC",
    "candle_boundary": "UTC daily candles",
    "coverage_window": (
        "A clear, fixed multi-year daily window covering at least one bull and "
        "one bear phase per asset (exact dates to be fixed in the data spec "
        "bundle, not here)."
    ),
    "source_provenance_required": True,
    "checksums_required": True,
    "freeze_manifest_required": True,
    "fee_assumptions_required": True,
    "slippage_assumptions_required": True,
    "live_fetch": False,
    "uses_api_keys": False,
    "exchange_account_access": False,
    "acquired": False,
    "inspected": False,
    "loaded": False,
}

# --- future validation plan (DEFINED only; nothing is run) ------------------

_REQUIRED_FUTURE_VALIDATION_STEPS = (
    {
        "step_id": "FUTURE_DATA_QA",
        "name": "Future Data QA",
        "description": (
            "Check the frozen dataset for gaps, duplicates, bad candles, and "
            "timezone alignment before any research uses it."
        ),
        "executed": False,
    },
    {
        "step_id": "FUTURE_BASELINE_TEST",
        "name": "Future Baseline Test",
        "description": (
            "Establish a trivial baseline (e.g. buy-and-hold per asset) so any "
            "candidate is judged against a fair reference."
        ),
        "executed": False,
    },
    {
        "step_id": "FUTURE_CANDIDATE_BACKTEST",
        "name": "Future Candidate Backtest",
        "description": (
            "Backtest each candidate family on the frozen data with realistic "
            "fees/slippage; in-sample only at this stage."
        ),
        "executed": False,
    },
    {
        "step_id": "FUTURE_OOS_SPLIT",
        "name": "Future Out-Of-Sample Split",
        "description": (
            "Hold out a clearly separated out-of-sample window and re-check the "
            "candidate without re-tuning."
        ),
        "executed": False,
    },
    {
        "step_id": "FUTURE_ROBUSTNESS_CHECKS",
        "name": "Future Robustness Checks",
        "description": (
            "Vary parameters mildly and test across all assets to confirm the "
            "result is not a single fragile point."
        ),
        "executed": False,
    },
    {
        "step_id": "FUTURE_PASS_WATCH_FAIL_MEMO",
        "name": "Future Pass/Watch/Fail Decision Memo",
        "description": (
            "Record a written pass/watch/fail decision per candidate, on "
            "paper, for human review."
        ),
        "executed": False,
    },
)

# --- prohibited actions (explicit) ------------------------------------------

_PROHIBITED_ACTIONS = (
    "real data acquisition",
    "API calls",
    "exchange or broker connection",
    "market-data inspection",
    "dataset loading",
    "QA run",
    "baseline run",
    "backtest run",
    "simulation run",
    "paper or live trading",
    "order logic",
    "trade signal generation",
    "dashboard writes",
    "runtime writes",
    "ledger writes",
    "registry writes to disk (beyond this protocol document/module/test)",
    "automation",
)

# --- safety gates (every real-world capability stays blocked) ---------------

_SAFETY_GATES = {
    "real_data": False,
    "api": False,
    "fetch": False,
    "exchange_or_broker": False,
    "market_data_inspection": False,
    "dataset_loading": False,
    "qa": False,
    "baseline": False,
    "backtest": False,
    "simulation": False,
    "paper_or_live": False,
    "order_logic": False,
    "trade_signal": False,
    "automation": False,
    "runtime_writes": False,
    "dashboard_writes": False,
    "ledger_writes": False,
    "registry_writes": False,
}

# --- pass / watch / fail rules (concept only) -------------------------------

_PASS_WATCH_FAIL_RULES = {
    "PASS": (
        "Multiple assets (not one coin only) show reasonable behavior.",
        "Drawdown is controlled, not catastrophic.",
        "Turnover and friction are realistic, not assumed away.",
        "No fragile dependence on a single parameter value.",
        "Out-of-sample performance is not destroyed.",
    ),
    "WATCH": (
        "Promising but mixed across assets.",
        "Depends heavily on the regime classification.",
        "Needs a better risk filter to be trustworthy.",
        "Out-of-sample behavior is unclear and needs more data/checks.",
    ),
    "FAIL": (
        "Looks like one-off luck on a single window.",
        "Clearly overfit to tuned parameters.",
        "High, uncontrolled drawdown.",
        "Fees/slippage destroy the edge.",
        "Unstable across assets.",
        "Requires execution assumptions we cannot support.",
    ),
}

# --- next bundle recommendation ---------------------------------------------

_NEXT_BUNDLE_RECOMMENDATION = {
    "bundle_number": 55,
    "bundle_id": "BUNDLE_55",
    "name": "Crypto-D1 Strategy Candidate Protocol Contract",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "next_required_action": NEXT_REQUIRED_ACTION,
    "rationale": (
        "This module DEFINES the protocol. Bundle 55 should formalize it as a "
        "read-only paper contract in the mission-flow chain (still research-"
        "only, still building nothing real), after which it can be registered "
        "in the mission-flow registry."
    ),
}

_RATIONALE = (
    "The Crypto-D1 research-only dry-run governance lane is now closed/"
    "archived (Bundle 54). Rather than keep adding governance bundles, the next "
    "research-only step is to define WHAT we will actually compare on paper: a "
    "small spot-only, daily-only universe (BTC/ETH/SOL) and four explainable "
    "candidate strategy families judged by clear pass/watch/fail rules. This "
    "protocol commits to that scope without acquiring data, running anything, "
    "or touching any execution surface."
)


def _clone(value: Any) -> Any:
    """Recursively copy nested protocol data into fresh, mutable structures.

    Tuples become lists on the way out so callers always get independent,
    mutation-safe containers; scalars pass through unchanged.
    """
    if isinstance(value, dict):
        return {k: _clone(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clone(v) for v in value]
    return value


def get_research_universe() -> list[str]:
    """The research universe (BTC/ETH/SOL), display-only."""
    return list(RESEARCH_UNIVERSE)


def get_candidate_strategy_families() -> list[dict[str, Any]]:
    """The four candidate strategy families (concept only)."""
    return _clone(_CANDIDATE_STRATEGY_FAMILIES)


def get_required_future_data_spec() -> dict[str, Any]:
    """Future data requirements, DEFINED only (nothing acquired)."""
    return _clone(_REQUIRED_FUTURE_DATA_SPEC)


def get_required_future_validation_steps() -> list[dict[str, Any]]:
    """Future validation steps, DEFINED only (nothing executed)."""
    return _clone(_REQUIRED_FUTURE_VALIDATION_STEPS)


def get_prohibited_actions() -> list[str]:
    """Actions explicitly prohibited by this protocol."""
    return list(_PROHIBITED_ACTIONS)


def get_safety_gates() -> dict[str, bool]:
    """Real-world capability gates; all False (nothing is unlocked)."""
    return dict(_SAFETY_GATES)


def get_pass_watch_fail_rules() -> dict[str, list[str]]:
    """Conceptual pass / watch / fail rules for future candidates."""
    return _clone(_PASS_WATCH_FAIL_RULES)


def get_next_bundle_recommendation() -> dict[str, Any]:
    """The recommended next research-only bundle to build."""
    return _clone(_NEXT_BUNDLE_RECOMMENDATION)


def get_safety_posture() -> dict[str, Any]:
    """Read-only safety posture; every real-world capability stays blocked."""
    return dict(PROTOCOL_SAFETY_POSTURE)


def get_protocol() -> dict[str, Any]:
    """The full, deterministic, read-only protocol specification (no IO)."""
    return {
        "protocol_id": PROTOCOL_ID,
        "protocol_name": PROTOCOL_NAME,
        "protocol_mode": PROTOCOL_MODE,
        "schema_version": PROTOCOL_SCHEMA_VERSION,
        "read_only": True,
        "executes": False,
        "human_approval_required": True,
        "research_universe": get_research_universe(),
        "market_type": MARKET_TYPE,
        "timeframe": TIMEFRAME,
        "candidate_strategy_families": get_candidate_strategy_families(),
        "required_future_data_spec": get_required_future_data_spec(),
        "required_future_validation_steps": (
            get_required_future_validation_steps()
        ),
        "prohibited_actions": get_prohibited_actions(),
        "safety_gates": get_safety_gates(),
        "safety_posture": get_safety_posture(),
        "pass_watch_fail_rules": get_pass_watch_fail_rules(),
        "next_bundle_recommendation": get_next_bundle_recommendation(),
        "next_required_action": NEXT_REQUIRED_ACTION,
        "rationale": _RATIONALE,
    }

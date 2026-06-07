"""SPARTA Offline Strategy Factory - CRYPTO-D1 BITCOIN CYCLE TIMING EVIDENCE.

A PURE, stdlib-only *read-only paper contract* that converts the BTC
364-day / 1064-day cycle idea into *research-only timing evidence*. It takes a
small dict of static, caller-provided observation fields (e.g.
``latest_btc_ath_date``, ``current_observation_date``,
``previous_ath_to_bottom_durations``) and returns a deterministic timing
assessment: days since the latest ATH, distance to the ~364-day cycle-bottom
window, comparisons against previous ATH-to-bottom and bottom-to-next-ATH
durations, an early / active / late / expired cycle-bottom watch zone, an
optional drawdown-from-ATH, and a single research-only evidence stance
(caution / accumulation-watch / recovery-watch / no-signal).

CORE RULE: cycle timing tells us *when to pay attention*, not *when to buy*.

This contract authorizes NOTHING real. It does NOT fetch any BTC data, call any
API, inspect any dataset, acquire any real data, load any file, open any
network, run any QA, baseline, backtest, or simulation, produce any trade
signal, reach any broker / exchange / order / account / API surface, trade any
paper and any live, promote any strategy, unlock any downstream gate, trigger
any automation, write any runtime / registry / ledger / dashboard / report
state, spawn any child process, read any environment, record any wall-clock
time, mint any random id, or dynamically import anything. It ONLY calculates
from the provided/static input fields using pure date and number arithmetic.

Hard timing stances (every one preserves SPARTA safety gates):
  - Cycle timing is external evidence only -- it says when to pay attention,
    never when to buy, and never grants execution permission.
  - A timing watch zone (early/active/late/expired) and an evidence stance
    (caution/accumulation-watch/recovery-watch/no-signal) cannot unlock
    real_data_qa, baseline_backtest, paper trading, live trading,
    broker/exchange, automation, or promotion.
  - Every timing signal must require independent confirmation before any later
    research protocol uses it.
  - No real BTC data is fetched; every number is computed from the static
    observation fields the caller passes in.

Public API:
  - BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION
  - DEFAULT_BITCOIN_CYCLE_TIMING_EVIDENCE_LABEL
  - BITCOIN_CYCLE_TIMING_EVIDENCE_STATUS
  - BITCOIN_CYCLE_TIMING_EVIDENCE_MODE
  - BITCOIN_CYCLE_TIMING_EVIDENCE_SAFETY_POSTURE
  - BITCOIN_CYCLE_TIMING_WATCH_ZONES
  - WATCH_ZONE_EARLY / WATCH_ZONE_ACTIVE / WATCH_ZONE_LATE /
    WATCH_ZONE_EXPIRED / WATCH_ZONE_UNDETERMINED
  - BITCOIN_CYCLE_TIMING_EVIDENCE_STANCES
  - STANCE_CAUTION / STANCE_ACCUMULATION_WATCH / STANCE_RECOVERY_WATCH /
    STANCE_NO_SIGNAL
  - CANONICAL_ATH_TO_BOTTOM_DAYS / CANONICAL_BOTTOM_TO_NEXT_ATH_DAYS
  - BOTTOM_WINDOW_TOLERANCE_DAYS / LATE_WINDOW_EXTRA_DAYS
  - BITCOIN_CYCLE_TIMING_CORE_RULE
  - BITCOIN_CYCLE_TIMING_EVIDENCE_NEXT_REQUIRED_ACTION
  - BITCOIN_CYCLE_TIMING_EVIDENCE_CURRENT_STAGE
  - BITCOIN_CYCLE_TIMING_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
  - BITCOIN_CYCLE_TIMING_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - DEFAULT_SAMPLE_OBSERVATION
  - assess_bitcoin_cycle_timing_evidence(observation)
  - build_crypto_d1_bitcoin_cycle_timing_evidence_contract(observation=None)
  - validate_crypto_d1_bitcoin_cycle_timing_evidence_contract(contract)
  - render_crypto_d1_bitcoin_cycle_timing_evidence_contract_markdown(contract)
"""

from __future__ import annotations

import datetime
from typing import Any

__all__ = [
    "BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION",
    "DEFAULT_BITCOIN_CYCLE_TIMING_EVIDENCE_LABEL",
    "BITCOIN_CYCLE_TIMING_EVIDENCE_STATUS",
    "BITCOIN_CYCLE_TIMING_EVIDENCE_MODE",
    "BITCOIN_CYCLE_TIMING_EVIDENCE_SAFETY_POSTURE",
    "BITCOIN_CYCLE_TIMING_WATCH_ZONES",
    "WATCH_ZONE_EARLY",
    "WATCH_ZONE_ACTIVE",
    "WATCH_ZONE_LATE",
    "WATCH_ZONE_EXPIRED",
    "WATCH_ZONE_UNDETERMINED",
    "BITCOIN_CYCLE_TIMING_EVIDENCE_STANCES",
    "STANCE_CAUTION",
    "STANCE_ACCUMULATION_WATCH",
    "STANCE_RECOVERY_WATCH",
    "STANCE_NO_SIGNAL",
    "CANONICAL_ATH_TO_BOTTOM_DAYS",
    "CANONICAL_BOTTOM_TO_NEXT_ATH_DAYS",
    "BOTTOM_WINDOW_TOLERANCE_DAYS",
    "LATE_WINDOW_EXTRA_DAYS",
    "BITCOIN_CYCLE_TIMING_CORE_RULE",
    "BITCOIN_CYCLE_TIMING_EVIDENCE_NEXT_REQUIRED_ACTION",
    "BITCOIN_CYCLE_TIMING_EVIDENCE_CURRENT_STAGE",
    "BITCOIN_CYCLE_TIMING_EVIDENCE_FORBIDDEN_ALLOW_FLAGS",
    "BITCOIN_CYCLE_TIMING_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "DEFAULT_SAMPLE_OBSERVATION",
    "assess_bitcoin_cycle_timing_evidence",
    "build_crypto_d1_bitcoin_cycle_timing_evidence_contract",
    "validate_crypto_d1_bitcoin_cycle_timing_evidence_contract",
    "render_crypto_d1_bitcoin_cycle_timing_evidence_contract_markdown",
]

BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_bitcoin_cycle_timing_evidence_contract.v1"
)
DEFAULT_BITCOIN_CYCLE_TIMING_EVIDENCE_LABEL = (
    "Strategy Factory Crypto-D1 Bitcoin Cycle Timing Evidence Contract"
)
BITCOIN_CYCLE_TIMING_EVIDENCE_STATUS = (
    "READ_ONLY_CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT"
)
BITCOIN_CYCLE_TIMING_EVIDENCE_MODE = "RESEARCH_ONLY"

BITCOIN_CYCLE_TIMING_CORE_RULE = (
    "Cycle timing tells us when to pay attention, not when to buy."
)

# The four cycle-bottom watch zones (plus an undetermined zone for missing
# data). Order is stable and is the canonical enumeration the contract and its
# validator compare against.
WATCH_ZONE_EARLY = "early"
WATCH_ZONE_ACTIVE = "active"
WATCH_ZONE_LATE = "late"
WATCH_ZONE_EXPIRED = "expired"
WATCH_ZONE_UNDETERMINED = "undetermined"

BITCOIN_CYCLE_TIMING_WATCH_ZONES: tuple[str, ...] = (
    WATCH_ZONE_EARLY,
    WATCH_ZONE_ACTIVE,
    WATCH_ZONE_LATE,
    WATCH_ZONE_EXPIRED,
    WATCH_ZONE_UNDETERMINED,
)
_WATCH_ZONE_SET: frozenset[str] = frozenset(BITCOIN_CYCLE_TIMING_WATCH_ZONES)

# The four research-only evidence stances. Each is an observation stance --
# "watch" / "pay attention" -- never a buy/sell instruction.
STANCE_CAUTION = "caution"
STANCE_ACCUMULATION_WATCH = "accumulation-watch"
STANCE_RECOVERY_WATCH = "recovery-watch"
STANCE_NO_SIGNAL = "no-signal"

BITCOIN_CYCLE_TIMING_EVIDENCE_STANCES: tuple[str, ...] = (
    STANCE_CAUTION,
    STANCE_ACCUMULATION_WATCH,
    STANCE_RECOVERY_WATCH,
    STANCE_NO_SIGNAL,
)
_STANCE_SET: frozenset[str] = frozenset(BITCOIN_CYCLE_TIMING_EVIDENCE_STANCES)

# Canonical BTC cycle durations (in days) used as the static reference. These
# are fixed paper constants -- nothing is fetched.
CANONICAL_ATH_TO_BOTTOM_DAYS = 364
CANONICAL_BOTTOM_TO_NEXT_ATH_DAYS = 1064
# Half-width of the "active" cycle-bottom window centered on the 364-day anchor.
BOTTOM_WINDOW_TOLERANCE_DAYS = 60
# Extra days past the active window that still count as a "late" watch zone.
LATE_WINDOW_EXTRA_DAYS = 120

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering
# this contract is a separate, later block; importing the registry would also
# risk a circular import).
BITCOIN_CYCLE_TIMING_EVIDENCE_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT"
)
BITCOIN_CYCLE_TIMING_EVIDENCE_CURRENT_STAGE = (
    "CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_REQUIRED"
)

# Read-only, all-false safety posture. Every capability flag stays False; this
# contract calculates cycle timing on paper and unlocks nothing.
BITCOIN_CYCLE_TIMING_EVIDENCE_SAFETY_POSTURE: dict[str, bool] = {
    "fetches_btc_data": False,
    "calls_api": False,
    "inspects_dataset": False,
    "acquires_data": False,
    "loads_dataset": False,
    "loads_file": False,
    "opens_network": False,
    "runs_qa": False,
    "runs_baseline": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "generates_trade_signal": False,
    "paper_or_live": False,
    "order_logic": False,
    "places_order": False,
    "connects_exchange_or_broker": False,
    "uses_api_keys": False,
    "sends_telegram_trade_command": False,
    "triggers_automation": False,
    "writes_runtime_state": False,
    "writes_registry": False,
    "writes_dashboard": False,
    "writes_ledger": False,
    "promotes_strategy": False,
    "unlocks_downstream_gate": False,
}

# Capability flags a caller-supplied observation must NOT request. Any truthy
# value is recorded as a forbidden-flag request and never honored. These are
# descriptive paper guards, not runtime switches.
BITCOIN_CYCLE_TIMING_EVIDENCE_FORBIDDEN_ALLOW_FLAGS: tuple[str, ...] = (
    "allow_execution",
    "executes",
    "allow_data_fetch",
    "fetches_btc_data",
    "allow_api_call",
    "calls_api",
    "allow_dataset_inspection",
    "inspects_dataset",
    "allow_real_data",
    "acquires_data",
    "allow_qa",
    "runs_qa",
    "allow_backtest",
    "runs_backtest",
    "allow_paper_live",
    "paper_or_live",
    "allow_broker",
    "connects_exchange_or_broker",
    "allow_order",
    "places_order",
    "allow_automation",
    "triggers_automation",
    "allow_strategy_promotion",
    "promotes_strategy",
    "allow_downstream_gate_unlock",
    "unlocks_downstream_gate",
)
_FORBIDDEN_FLAG_SET: frozenset[str] = frozenset(
    BITCOIN_CYCLE_TIMING_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
)

# Real-world capabilities that remain blocked regardless of timing outcome.
BITCOIN_CYCLE_TIMING_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED: tuple[
    str, ...
] = (
    "btc_data_fetch",
    "api_call",
    "dataset_inspection",
    "real_data_acquisition",
    "file_load",
    "network_open",
    "qa_run",
    "baseline_run",
    "backtest_run",
    "simulation_run",
    "trade_signal_production",
    "order_placement",
    "broker_or_exchange_connection",
    "api_key_use",
    "telegram_trade_command",
    "paper_or_live_trading",
    "strategy_promotion",
    "automation_trigger",
    "downstream_gate_unlock",
    "runtime_write",
    "registry_write",
    "dashboard_write",
    "ledger_write",
)

# The known, recognized input field names. Anything else in the observation is
# preserved but ignored by the timing math.
_OBSERVATION_FIELDS: tuple[str, ...] = (
    "latest_btc_ath_date",
    "latest_btc_ath_price",
    "candidate_cycle_bottom_date",
    "candidate_cycle_bottom_price",
    "current_observation_date",
    "current_observed_price",
    "previous_ath_to_bottom_durations",
    "previous_bottom_to_next_ath_durations",
)

# A deterministic, illustrative paper sample. Lands ~355 days past the ATH ->
# inside the active cycle-bottom window -> accumulation-watch. Nothing here is
# real BTC data; these are static example fields only.
DEFAULT_SAMPLE_OBSERVATION: dict[str, Any] = {
    "latest_btc_ath_date": "2025-01-20",
    "latest_btc_ath_price": 109000.0,
    "candidate_cycle_bottom_date": "2026-01-19",
    "candidate_cycle_bottom_price": 45000.0,
    "current_observation_date": "2026-01-10",
    "current_observed_price": 48000.0,
    "previous_ath_to_bottom_durations": [364, 386, 357],
    "previous_bottom_to_next_ath_durations": [1064, 1050, 1100],
}


def _as_text(value: Any) -> str:
    """Coerce any value to a stripped string; non-str/None -> ''."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _parse_date(value: Any) -> datetime.date | None:
    """Parse an ISO 'YYYY-MM-DD' string into a date. Pure; never raises and
    never reads a clock -- malformed/empty input returns None."""
    text = _as_text(value)
    if not text:
        return None
    try:
        return datetime.date.fromisoformat(text)
    except (ValueError, TypeError):
        return None


def _parse_number(value: Any) -> float | None:
    """Coerce a value to float, or None when not numeric. Pure; never raises."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = _as_text(value)
    if not text:
        return None
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def _days_between(start: datetime.date | None, end: datetime.date | None):
    """Whole days from start to end (end - start). None if either is None."""
    if start is None or end is None:
        return None
    return (end - start).days


def _truthy(value: Any) -> bool:
    """Conservative truthiness for caller-supplied allow flags."""
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1", "on", "allow")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    return False


def _requested_forbidden_flags(observation: dict[str, Any]) -> tuple[str, ...]:
    """Forbidden allow-flags the observation requested as truthy."""
    return tuple(
        f
        for f in BITCOIN_CYCLE_TIMING_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
        if f in observation and _truthy(observation.get(f))
    )


def _duration_comparison(
    durations: Any, canonical_days: int
) -> dict[str, Any] | None:
    """Compare a list of previous durations against a canonical anchor. Pure;
    returns None when no usable numeric samples are present."""
    if not isinstance(durations, (list, tuple)):
        return None
    samples = [n for n in (_parse_number(d) for d in durations) if n is not None]
    if not samples:
        return None
    average = sum(samples) / len(samples)
    return {
        "sample_count": len(samples),
        "samples": list(samples),
        "average_days": average,
        "canonical_days": canonical_days,
        "delta_vs_canonical_days": average - float(canonical_days),
    }


def _watch_zone(days_since_ath: int | None) -> str:
    """Classify days-since-ATH into an early/active/late/expired watch zone.

    The active window is the 364-day anchor +/- BOTTOM_WINDOW_TOLERANCE_DAYS;
    'late' extends LATE_WINDOW_EXTRA_DAYS past it; anything earlier is 'early',
    anything later (or a negative/None value) is expired/undetermined."""
    if days_since_ath is None:
        return WATCH_ZONE_UNDETERMINED
    window_low = CANONICAL_ATH_TO_BOTTOM_DAYS - BOTTOM_WINDOW_TOLERANCE_DAYS
    window_high = CANONICAL_ATH_TO_BOTTOM_DAYS + BOTTOM_WINDOW_TOLERANCE_DAYS
    late_high = window_high + LATE_WINDOW_EXTRA_DAYS
    if days_since_ath < 0:
        return WATCH_ZONE_UNDETERMINED
    if days_since_ath < window_low:
        return WATCH_ZONE_EARLY
    if days_since_ath <= window_high:
        return WATCH_ZONE_ACTIVE
    if days_since_ath <= late_high:
        return WATCH_ZONE_LATE
    return WATCH_ZONE_EXPIRED


def _stance_for_zone(zone: str) -> tuple[str, str]:
    """Map a watch zone to a research-only evidence stance and a reason. Every
    stance is an observation stance -- pay attention, never buy."""
    if zone == WATCH_ZONE_EARLY:
        return (
            STANCE_CAUTION,
            "Post-ATH / pre-bottom-window phase: stay cautious and pay "
            "attention; this is not a buy signal.",
        )
    if zone == WATCH_ZONE_ACTIVE:
        return (
            STANCE_ACCUMULATION_WATCH,
            "Inside the ~364-day cycle-bottom window: watch for accumulation "
            "evidence; this is attention only, never a buy instruction.",
        )
    if zone == WATCH_ZONE_LATE:
        return (
            STANCE_RECOVERY_WATCH,
            "Just past the cycle-bottom window: watch for recovery "
            "confirmation; attention only, never a buy instruction.",
        )
    if zone == WATCH_ZONE_EXPIRED:
        return (
            STANCE_NO_SIGNAL,
            "Outside the cycle-bottom timing window: no cycle-timing signal.",
        )
    return (
        STANCE_NO_SIGNAL,
        "Insufficient or unparseable timing inputs: no cycle-timing signal.",
    )


def assess_bitcoin_cycle_timing_evidence(observation: Any) -> dict[str, Any]:
    """Return a deterministic cycle-timing assessment for one observation dict.
    Pure; no I/O, no data fetch, no clock read, no mutation, no random id.
    Malformed or partial inputs never raise -- missing fields degrade to a
    no-signal/undetermined result. Every output is attention-only evidence and
    authorizes nothing."""
    obs = observation if isinstance(observation, dict) else {}

    ath_date = _parse_date(obs.get("latest_btc_ath_date"))
    bottom_date = _parse_date(obs.get("candidate_cycle_bottom_date"))
    obs_date = _parse_date(obs.get("current_observation_date"))
    ath_price = _parse_number(obs.get("latest_btc_ath_price"))
    obs_price = _parse_number(obs.get("current_observed_price"))

    days_since_ath = _days_between(ath_date, obs_date)
    candidate_bottom_days_from_ath = _days_between(ath_date, bottom_date)

    window_low = CANONICAL_ATH_TO_BOTTOM_DAYS - BOTTOM_WINDOW_TOLERANCE_DAYS
    window_high = CANONICAL_ATH_TO_BOTTOM_DAYS + BOTTOM_WINDOW_TOLERANCE_DAYS
    late_high = window_high + LATE_WINDOW_EXTRA_DAYS

    if days_since_ath is None:
        distance_to_bottom_window_center = None
    else:
        distance_to_bottom_window_center = (
            CANONICAL_ATH_TO_BOTTOM_DAYS - days_since_ath
        )

    zone = _watch_zone(days_since_ath)
    stance, reason = _stance_for_zone(zone)

    if (
        ath_price is not None
        and obs_price is not None
        and ath_price > 0
    ):
        drawdown_from_ath = (obs_price - ath_price) / ath_price
    else:
        drawdown_from_ath = None

    ath_to_bottom_comparison = _duration_comparison(
        obs.get("previous_ath_to_bottom_durations"),
        CANONICAL_ATH_TO_BOTTOM_DAYS,
    )
    bottom_to_next_ath_comparison = _duration_comparison(
        obs.get("previous_bottom_to_next_ath_durations"),
        CANONICAL_BOTTOM_TO_NEXT_ATH_DAYS,
    )

    forbidden = _requested_forbidden_flags(obs)

    return {
        "days_since_ath": days_since_ath,
        "candidate_bottom_days_from_ath": candidate_bottom_days_from_ath,
        "bottom_window": {
            "anchor_days": CANONICAL_ATH_TO_BOTTOM_DAYS,
            "window_low_days": window_low,
            "window_high_days": window_high,
            "late_high_days": late_high,
        },
        "distance_to_bottom_window_center_days": (
            distance_to_bottom_window_center
        ),
        "previous_ath_to_bottom_comparison": ath_to_bottom_comparison,
        "previous_bottom_to_next_ath_comparison": bottom_to_next_ath_comparison,
        "drawdown_from_ath": drawdown_from_ath,
        "watch_zone": zone,
        "evidence_stance": stance,
        "evidence_reason": reason,
        "requested_forbidden_flags": forbidden,
        "authorizes_nothing": True,
    }


_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 Bitcoin cycle-timing evidence contract template and "
    "is execution-free.",
    "It converts the BTC 364-day / 1064-day cycle idea into research-only "
    "timing evidence; it runs nothing, fetches nothing, and connects nowhere.",
    "Core rule: cycle timing tells us when to pay attention, not when to buy.",
    "No BTC data is fetched, no API is called, no dataset is inspected, and no "
    "real data is acquired -- every number is computed from static input "
    "fields only.",
    "The watch zone (early/active/late/expired) and the evidence stance "
    "(caution/accumulation-watch/recovery-watch/no-signal) are attention-only "
    "evidence and never a buy/sell instruction.",
    "Cycle-timing evidence cannot unlock real_data_qa, baseline_backtest, "
    "paper trading, live trading, broker/exchange, automation, or promotion.",
    "Every timing signal needs independent confirmation before any later "
    "research protocol uses it.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human reviewer must read the structured cycle-timing assessment before "
    "any further research-only contract is built.",
    "A human reviewer must confirm the watch zone and stance are treated as "
    "attention-only evidence and are never wired to a data fetch, an API "
    "call, a dataset, a QA run, a backtest, a paper/live trade, a broker or "
    "exchange, an order, or any automation.",
    "A human reviewer must independently confirm every timing signal before it "
    "is trusted as evidence.",
    "A human reviewer must confirm the next step is only to BUILD the next "
    "research-only evidence contract (Daily Alpha Brief research contract), "
    "still on paper.",
    "No execution, BTC data fetch, API call, dataset inspection, data "
    "acquisition, QA, backtest, paper/live, broker/exchange, automation, "
    "promotion, or downstream-gate unlock may proceed.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "stage",
    "mode",
    "core_rule",
    "bitcoin_cycle_timing_next_required_action",
    "bitcoin_cycle_timing_current_stage",
    "watch_zones",
    "evidence_stances",
    "canonical_ath_to_bottom_days",
    "canonical_bottom_to_next_ath_days",
    "forbidden_allow_flags",
    "remaining_real_world_capabilities_blocked",
    "observation",
    "assessment",
    "watch_zone",
    "evidence_stance",
    "requested_forbidden_flags",
    "safety_posture",
    "operator_notes",
    "human_operator_required_next_steps",
    "requires_independent_confirmation",
    "human_approval_required",
    "read_only",
    "executes",
    "authorizes_real_world_action",
    "unlocks_downstream_gate",
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(BITCOIN_CYCLE_TIMING_EVIDENCE_SAFETY_POSTURE)


def _normalized_observation(observation: dict[str, Any]) -> dict[str, Any]:
    """Echo only the recognized observation fields (fresh copy, isolated)."""
    out: dict[str, Any] = {}
    for field in _OBSERVATION_FIELDS:
        if field in observation:
            value = observation[field]
            if isinstance(value, (list, tuple)):
                out[field] = list(value)
            else:
                out[field] = value
    return out


def build_crypto_d1_bitcoin_cycle_timing_evidence_contract(
    observation: Any = None,
) -> dict[str, Any]:
    """Build the read-only Bitcoin cycle-timing evidence contract. Pure; no
    I/O, no data fetch, no mutation of inputs, no clock read, no random id. When
    no observation is given, the static DEFAULT_SAMPLE_OBSERVATION is assessed.
    A fresh dict (with fresh lists/dicts) is returned every call."""
    if observation is None:
        source = dict(DEFAULT_SAMPLE_OBSERVATION)
    elif isinstance(observation, dict):
        source = dict(observation)
    else:
        source = {}

    assessment = assess_bitcoin_cycle_timing_evidence(source)

    contract: dict[str, Any] = {
        "schema_version": BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION,
        "label": DEFAULT_BITCOIN_CYCLE_TIMING_EVIDENCE_LABEL,
        "status": BITCOIN_CYCLE_TIMING_EVIDENCE_STATUS,
        "stage": "CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_ONLY",
        "mode": BITCOIN_CYCLE_TIMING_EVIDENCE_MODE,
        "core_rule": BITCOIN_CYCLE_TIMING_CORE_RULE,
        "bitcoin_cycle_timing_next_required_action": (
            BITCOIN_CYCLE_TIMING_EVIDENCE_NEXT_REQUIRED_ACTION
        ),
        "bitcoin_cycle_timing_current_stage": (
            BITCOIN_CYCLE_TIMING_EVIDENCE_CURRENT_STAGE
        ),
        "watch_zones": BITCOIN_CYCLE_TIMING_WATCH_ZONES,
        "evidence_stances": BITCOIN_CYCLE_TIMING_EVIDENCE_STANCES,
        "canonical_ath_to_bottom_days": CANONICAL_ATH_TO_BOTTOM_DAYS,
        "canonical_bottom_to_next_ath_days": (
            CANONICAL_BOTTOM_TO_NEXT_ATH_DAYS
        ),
        "forbidden_allow_flags": (
            BITCOIN_CYCLE_TIMING_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
        ),
        "remaining_real_world_capabilities_blocked": (
            BITCOIN_CYCLE_TIMING_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
        ),
        "observation": _normalized_observation(source),
        "assessment": assessment,
        "watch_zone": assessment["watch_zone"],
        "evidence_stance": assessment["evidence_stance"],
        "requested_forbidden_flags": assessment["requested_forbidden_flags"],
        "safety_posture": _safety_posture(),
        "operator_notes": list(_OPERATOR_NOTES),
        "human_operator_required_next_steps": list(
            _HUMAN_OPERATOR_REQUIRED_NEXT_STEPS
        ),
        "requires_independent_confirmation": True,
        "human_approval_required": True,
        "read_only": True,
        "executes": False,
        "authorizes_real_world_action": False,
        "unlocks_downstream_gate": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return contract


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version")
        == BITCOIN_CYCLE_TIMING_EVIDENCE_SCHEMA_VERSION
    )
    read_only = safe.get("read_only") is True
    research_only = safe.get("mode") == "RESEARCH_ONLY"
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_BITCOIN_CYCLE_TIMING_EVIDENCE_CONTRACT_ONLY"
    )
    core_rule_ok = safe.get("core_rule") == BITCOIN_CYCLE_TIMING_CORE_RULE
    human_required = safe.get("human_approval_required") is True
    executes_false = safe.get("executes") is False
    authorizes_false = safe.get("authorizes_real_world_action") is False
    unlocks_false = safe.get("unlocks_downstream_gate") is False
    confirmation_required = (
        safe.get("requires_independent_confirmation") is True
    )
    gates_locked = (
        safe.get("real_data_qa_blocked") is True
        and safe.get("baseline_backtest_blocked") is True
        and safe.get("paper_trading_gate_locked") is True
        and safe.get("micro_live_gate_locked") is True
    )

    posture = safe.get("safety_posture")
    safety_all_false = (
        isinstance(posture, dict)
        and len(posture) > 0
        and all(v is False for v in posture.values())
    )

    zones_ok = (
        tuple(safe.get("watch_zones") or ())
        == BITCOIN_CYCLE_TIMING_WATCH_ZONES
    )
    stances_ok = (
        tuple(safe.get("evidence_stances") or ())
        == BITCOIN_CYCLE_TIMING_EVIDENCE_STANCES
    )
    forbidden_ok = (
        tuple(safe.get("forbidden_allow_flags") or ())
        == BITCOIN_CYCLE_TIMING_EVIDENCE_FORBIDDEN_ALLOW_FLAGS
    )
    remaining_ok = (
        tuple(safe.get("remaining_real_world_capabilities_blocked") or ())
        == BITCOIN_CYCLE_TIMING_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )

    zone_ok = safe.get("watch_zone") in _WATCH_ZONE_SET
    stance_ok = safe.get("evidence_stance") in _STANCE_SET

    assessment = safe.get("assessment")
    assessment_ok = (
        isinstance(assessment, dict)
        and assessment.get("authorizes_nothing") is True
        and assessment.get("watch_zone") in _WATCH_ZONE_SET
        and assessment.get("evidence_stance") in _STANCE_SET
    )

    notes_ok = len(tuple(safe.get("operator_notes") or ())) >= 1
    next_steps_ok = (
        len(tuple(safe.get("human_operator_required_next_steps") or ())) >= 1
    )

    valid = (
        not missing
        and schema_ok
        and read_only
        and research_only
        and stage_ok
        and core_rule_ok
        and human_required
        and executes_false
        and authorizes_false
        and unlocks_false
        and confirmation_required
        and gates_locked
        and safety_all_false
        and zones_ok
        and stances_ok
        and forbidden_ok
        and remaining_ok
        and zone_ok
        and stance_ok
        and assessment_ok
        and notes_ok
        and next_steps_ok
    )

    return {
        "valid": bool(valid),
        "missing_fields": missing,
        "schema_ok": schema_ok,
        "read_only": read_only,
        "research_only": research_only,
        "stage_ok": stage_ok,
        "core_rule_ok": core_rule_ok,
        "human_required": human_required,
        "executes_false": executes_false,
        "authorizes_false": authorizes_false,
        "unlocks_false": unlocks_false,
        "confirmation_required": confirmation_required,
        "gates_locked": gates_locked,
        "safety_all_false": safety_all_false,
        "zones_ok": zones_ok,
        "stances_ok": stances_ok,
        "forbidden_ok": forbidden_ok,
        "remaining_ok": remaining_ok,
        "zone_ok": zone_ok,
        "stance_ok": stance_ok,
        "assessment_ok": assessment_ok,
        "notes_ok": notes_ok,
        "next_steps_ok": next_steps_ok,
    }


def validate_crypto_d1_bitcoin_cycle_timing_evidence_contract(
    contract: Any,
) -> dict[str, Any]:
    """Public validation entry point; returns the deterministic verdict dict."""
    return _validate(contract)


def render_crypto_d1_bitcoin_cycle_timing_evidence_contract_markdown(
    contract: Any,
) -> str:
    """Render an informational, read-only markdown summary of the contract.
    Pure; builds and returns a string, writes nothing."""
    safe = contract if isinstance(contract, dict) else {}
    assessment = safe.get("assessment")
    assessment = assessment if isinstance(assessment, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Bitcoin Cycle Timing Evidence Contract")
    lines.append("")
    lines.append("- Mode: " + _as_text(safe.get("mode")))
    lines.append("- Status: " + _as_text(safe.get("status")))
    lines.append("- Core rule: " + _as_text(safe.get("core_rule")))
    lines.append("- Read-only: " + str(safe.get("read_only")))
    lines.append("- Executes: " + str(safe.get("executes")))
    lines.append(
        "- Authorizes real-world action: "
        + str(safe.get("authorizes_real_world_action"))
    )
    lines.append(
        "- Requires independent confirmation: "
        + str(safe.get("requires_independent_confirmation"))
    )
    lines.append(
        "- real_data_qa blocked: " + str(safe.get("real_data_qa_blocked"))
    )
    lines.append(
        "- baseline_backtest blocked: "
        + str(safe.get("baseline_backtest_blocked"))
    )
    lines.append(
        "- paper_trading_gate locked: "
        + str(safe.get("paper_trading_gate_locked"))
    )
    lines.append(
        "- micro_live_gate locked: "
        + str(safe.get("micro_live_gate_locked"))
    )
    lines.append("")
    lines.append("## Timing Assessment")
    lines.append("- Days since ATH: " + str(assessment.get("days_since_ath")))
    lines.append(
        "- Distance to bottom-window center (days): "
        + str(assessment.get("distance_to_bottom_window_center_days"))
    )
    lines.append("- Watch zone: " + _as_text(safe.get("watch_zone")))
    lines.append("- Evidence stance: " + _as_text(safe.get("evidence_stance")))
    lines.append(
        "- Drawdown from ATH: " + str(assessment.get("drawdown_from_ath"))
    )
    lines.append("- Reason: " + _as_text(assessment.get("evidence_reason")))
    return "\n".join(lines)

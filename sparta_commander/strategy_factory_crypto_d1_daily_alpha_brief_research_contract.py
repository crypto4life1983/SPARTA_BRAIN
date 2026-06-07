"""SPARTA Offline Strategy Factory - CRYPTO-D1 DAILY ALPHA BRIEF (RESEARCH).

A PURE, stdlib-only *read-only paper contract* that defines how SPARTA should
assemble a *daily crypto alpha brief* from already-approved, static evidence
payloads only. It takes a small dict of caller-provided evidence lanes
(``external_bot_evidence_intake``, ``hyperliquid_whale_evidence``,
``funding_rate_evidence``, ``bitcoin_cycle_timing_evidence``) and returns a
deterministic, structured brief: an input-evidence summary, a market-context
section, an evidence-alignment section, caution flags, a research watchlist, an
explicit no-execution-authorization section, a missing-evidence section, and a
single research-only operator next step.

CORE RULE: the daily alpha brief tells us *what to watch and research*, never
*what to trade*. The highest stance it can ever produce is WATCH / RESEARCH_ONLY.

This contract authorizes NOTHING real. It does NOT fetch any data, call any API,
inspect any dataset, acquire any real data, load any file, open any network, run
any QA, baseline, backtest, or simulation, produce any trade signal, reach any
broker / exchange / order / account / API surface, trade any paper and any live,
promote any strategy, unlock any downstream gate, trigger any automation, write
any runtime / registry / ledger / dashboard / report state, spawn any child
process, read any environment, record any wall-clock time, mint any random id,
or dynamically import anything. It ONLY organizes the static evidence payloads
the caller passes in, using pure dict/string arithmetic.

Decision behavior (deterministic, always research-only):
  - Missing evidence -> AWAIT / INCOMPLETE_EVIDENCE (never a failure).
  - Conflicting evidence -> MIXED_WATCH / MIXED (never a trade).
  - Strong aligned evidence -> RESEARCH_WATCH_ONLY / RESEARCH_ONLY (never
    paper or live).
  - Neutral / unscored evidence -> NEUTRAL_WATCH / WATCH.
  - The brief NEVER produces a BUY / SELL / LONG / SHORT / ENTRY / EXIT / order
    instruction. The highest stance is WATCH / RESEARCH_ONLY.

Public API:
  - DAILY_ALPHA_BRIEF_SCHEMA_VERSION
  - DAILY_ALPHA_BRIEF_LABEL
  - DAILY_ALPHA_BRIEF_STATUS
  - DAILY_ALPHA_BRIEF_MODE
  - DAILY_ALPHA_BRIEF_CORE_RULE
  - DAILY_ALPHA_BRIEF_SAFETY_POSTURE
  - DAILY_ALPHA_BRIEF_EVIDENCE_LANES
  - DAILY_ALPHA_BRIEF_DECISIONS
  - DECISION_AWAIT / DECISION_MIXED_WATCH / DECISION_NEUTRAL_WATCH /
    DECISION_RESEARCH_WATCH_ONLY
  - DAILY_ALPHA_BRIEF_STANCES
  - STANCE_INCOMPLETE_EVIDENCE / STANCE_MIXED / STANCE_WATCH /
    STANCE_RESEARCH_ONLY
  - DAILY_ALPHA_BRIEF_LANE_STANCES
  - LANE_STANCE_SUPPORTIVE / LANE_STANCE_CAUTIONARY / LANE_STANCE_NEUTRAL /
    LANE_STANCE_UNKNOWN
  - DAILY_ALPHA_BRIEF_FORBIDDEN_ALLOW_FLAGS
  - DAILY_ALPHA_BRIEF_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
  - DAILY_ALPHA_BRIEF_FORBIDDEN_TRADE_TERMS
  - DAILY_ALPHA_BRIEF_NEXT_REQUIRED_ACTION
  - DAILY_ALPHA_BRIEF_CURRENT_STAGE
  - DEFAULT_SAMPLE_EVIDENCE
  - assess_daily_alpha_brief_evidence(evidence)
  - build_crypto_d1_daily_alpha_brief_research_contract(evidence=None)
  - validate_crypto_d1_daily_alpha_brief_research_contract(contract)
  - render_crypto_d1_daily_alpha_brief_research_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "DAILY_ALPHA_BRIEF_SCHEMA_VERSION",
    "DAILY_ALPHA_BRIEF_LABEL",
    "DAILY_ALPHA_BRIEF_STATUS",
    "DAILY_ALPHA_BRIEF_MODE",
    "DAILY_ALPHA_BRIEF_CORE_RULE",
    "DAILY_ALPHA_BRIEF_SAFETY_POSTURE",
    "DAILY_ALPHA_BRIEF_EVIDENCE_LANES",
    "DAILY_ALPHA_BRIEF_DECISIONS",
    "DECISION_AWAIT",
    "DECISION_MIXED_WATCH",
    "DECISION_NEUTRAL_WATCH",
    "DECISION_RESEARCH_WATCH_ONLY",
    "DAILY_ALPHA_BRIEF_STANCES",
    "STANCE_INCOMPLETE_EVIDENCE",
    "STANCE_MIXED",
    "STANCE_WATCH",
    "STANCE_RESEARCH_ONLY",
    "DAILY_ALPHA_BRIEF_LANE_STANCES",
    "LANE_STANCE_SUPPORTIVE",
    "LANE_STANCE_CAUTIONARY",
    "LANE_STANCE_NEUTRAL",
    "LANE_STANCE_UNKNOWN",
    "DAILY_ALPHA_BRIEF_FORBIDDEN_ALLOW_FLAGS",
    "DAILY_ALPHA_BRIEF_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED",
    "DAILY_ALPHA_BRIEF_FORBIDDEN_TRADE_TERMS",
    "DAILY_ALPHA_BRIEF_NEXT_REQUIRED_ACTION",
    "DAILY_ALPHA_BRIEF_CURRENT_STAGE",
    "DEFAULT_SAMPLE_EVIDENCE",
    "assess_daily_alpha_brief_evidence",
    "build_crypto_d1_daily_alpha_brief_research_contract",
    "validate_crypto_d1_daily_alpha_brief_research_contract",
    "render_crypto_d1_daily_alpha_brief_research_contract_markdown",
]

DAILY_ALPHA_BRIEF_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_daily_alpha_brief_research_contract.v1"
)
# The exact contract label required by the bundle spec (Block 125).
DAILY_ALPHA_BRIEF_LABEL = (
    "Block 125 - Crypto-D1 Daily Alpha Brief Research Contract"
)
DAILY_ALPHA_BRIEF_STATUS = (
    "READ_ONLY_CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT"
)
DAILY_ALPHA_BRIEF_MODE = "RESEARCH_ONLY"

DAILY_ALPHA_BRIEF_CORE_RULE = (
    "The daily alpha brief tells us what to watch and research, never what to "
    "trade; the highest stance it can produce is WATCH / RESEARCH_ONLY."
)

# The recognized evidence lanes, in canonical order. The brief organizes only
# these lanes; anything else in the payload is ignored by the brief logic.
DAILY_ALPHA_BRIEF_EVIDENCE_LANES: tuple[str, ...] = (
    "external_bot_evidence_intake",
    "hyperliquid_whale_evidence",
    "funding_rate_evidence",
    "bitcoin_cycle_timing_evidence",
)

# Overall research decisions. Every value is research-only; none is a trade.
DECISION_AWAIT = "AWAIT"
DECISION_MIXED_WATCH = "MIXED_WATCH"
DECISION_NEUTRAL_WATCH = "NEUTRAL_WATCH"
DECISION_RESEARCH_WATCH_ONLY = "RESEARCH_WATCH_ONLY"

DAILY_ALPHA_BRIEF_DECISIONS: tuple[str, ...] = (
    DECISION_AWAIT,
    DECISION_MIXED_WATCH,
    DECISION_NEUTRAL_WATCH,
    DECISION_RESEARCH_WATCH_ONLY,
)
_DECISION_SET: frozenset[str] = frozenset(DAILY_ALPHA_BRIEF_DECISIONS)

# Overall research stances. The highest possible stance is WATCH / RESEARCH_ONLY.
STANCE_INCOMPLETE_EVIDENCE = "INCOMPLETE_EVIDENCE"
STANCE_MIXED = "MIXED"
STANCE_WATCH = "WATCH"
STANCE_RESEARCH_ONLY = "RESEARCH_ONLY"

DAILY_ALPHA_BRIEF_STANCES: tuple[str, ...] = (
    STANCE_INCOMPLETE_EVIDENCE,
    STANCE_MIXED,
    STANCE_WATCH,
    STANCE_RESEARCH_ONLY,
)
_STANCE_SET: frozenset[str] = frozenset(DAILY_ALPHA_BRIEF_STANCES)

_DECISION_TO_STANCE: dict[str, str] = {
    DECISION_AWAIT: STANCE_INCOMPLETE_EVIDENCE,
    DECISION_MIXED_WATCH: STANCE_MIXED,
    DECISION_NEUTRAL_WATCH: STANCE_WATCH,
    DECISION_RESEARCH_WATCH_ONLY: STANCE_RESEARCH_ONLY,
}

# Per-lane research stances. Each is an attention/observation stance, never a
# buy/sell instruction.
LANE_STANCE_SUPPORTIVE = "supportive-watch"
LANE_STANCE_CAUTIONARY = "cautionary-watch"
LANE_STANCE_NEUTRAL = "neutral"
LANE_STANCE_UNKNOWN = "unknown"

DAILY_ALPHA_BRIEF_LANE_STANCES: tuple[str, ...] = (
    LANE_STANCE_SUPPORTIVE,
    LANE_STANCE_CAUTIONARY,
    LANE_STANCE_NEUTRAL,
    LANE_STANCE_UNKNOWN,
)
_LANE_STANCE_SET: frozenset[str] = frozenset(DAILY_ALPHA_BRIEF_LANE_STANCES)

# Caller-supplied lane-stance aliases normalized to the canonical lane stances.
_SUPPORTIVE_ALIASES: frozenset[str] = frozenset(
    {
        "supportive",
        "supportive-watch",
        "accumulation-watch",
        "recovery-watch",
        "constructive",
        "bullish-watch",
        "positive",
    }
)
_CAUTIONARY_ALIASES: frozenset[str] = frozenset(
    {
        "cautionary",
        "cautionary-watch",
        "caution",
        "bearish-watch",
        "negative",
        "risk",
        "overheated",
    }
)
_NEUTRAL_ALIASES: frozenset[str] = frozenset(
    {
        "neutral",
        "no-signal",
        "none",
        "flat",
        "mixed",
    }
)

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering
# this contract is a separate, later block; importing the registry would also
# risk a circular import).
DAILY_ALPHA_BRIEF_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT"
)
DAILY_ALPHA_BRIEF_CURRENT_STAGE = (
    "CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_REQUIRED"
)

# Read-only, all-false safety posture. Every capability flag stays False; this
# contract organizes evidence on paper and unlocks nothing.
DAILY_ALPHA_BRIEF_SAFETY_POSTURE: dict[str, bool] = {
    "fetches_data": False,
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
    "spawns_subprocess": False,
    "dynamic_import": False,
}

# Capability flags a caller-supplied payload must NOT request. Any truthy value
# is recorded as a forbidden-flag request and never honored. These are
# descriptive paper guards, not runtime switches.
DAILY_ALPHA_BRIEF_FORBIDDEN_ALLOW_FLAGS: tuple[str, ...] = (
    "allow_execution",
    "executes",
    "allow_trading",
    "authorizes_trading",
    "allow_data_fetch",
    "fetches_data",
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
    "allow_paper_trading",
    "allow_live_trading",
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
    DAILY_ALPHA_BRIEF_FORBIDDEN_ALLOW_FLAGS
)

# Real-world capabilities that remain blocked regardless of the brief outcome.
DAILY_ALPHA_BRIEF_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED: tuple[
    str, ...
] = (
    "data_fetch",
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
    "paper_trading",
    "live_trading",
    "strategy_promotion",
    "automation_trigger",
    "downstream_gate_unlock",
    "runtime_write",
    "registry_write",
    "dashboard_write",
    "ledger_write",
    "subprocess_spawn",
    "dynamic_import",
)

# Execution verbs the brief's generated guidance must never contain. The brief
# is attention-only; these terms describe trade instructions it cannot issue.
DAILY_ALPHA_BRIEF_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
    "order",
)

# Recognized per-lane input fields. Anything else inside a lane payload is
# ignored by the brief logic (and not echoed into generated guidance).
_LANE_FIELDS: tuple[str, ...] = ("stance", "headline", "metrics", "note")

# A deterministic, illustrative paper sample with all four lanes present and
# aligned-supportive -> RESEARCH_WATCH_ONLY. Nothing here is real data; these
# are static example fields only.
DEFAULT_SAMPLE_EVIDENCE: dict[str, Any] = {
    "external_bot_evidence_intake": {
        "stance": "supportive-watch",
        "headline": "Approved external research notes lean constructive.",
        "metrics": {"approved_sources": 3},
    },
    "hyperliquid_whale_evidence": {
        "stance": "supportive-watch",
        "headline": "Large-wallet accumulation evidence noted (research only).",
        "metrics": {"net_accumulation_score": 0.62},
    },
    "funding_rate_evidence": {
        "stance": "neutral",
        "headline": "Funding rate is balanced; no crowding evidence.",
        "metrics": {"funding_z_score": 0.1},
    },
    "bitcoin_cycle_timing_evidence": {
        "stance": "accumulation-watch",
        "headline": "Inside the ~364-day cycle-bottom watch window.",
        "metrics": {"days_since_ath": 355},
    },
}


def _as_text(value: Any) -> str:
    """Coerce any value to a stripped string; non-str/None -> ''."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _truthy(value: Any) -> bool:
    """Conservative truthiness for caller-supplied allow flags."""
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1", "on", "allow")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    return False


def _requested_forbidden_flags(evidence: dict[str, Any]) -> tuple[str, ...]:
    """Forbidden allow-flags requested as truthy at the top level or inside any
    recognized lane payload. Deterministic order; no duplicates."""
    found: list[str] = []
    scopes: list[dict[str, Any]] = [evidence]
    for lane in DAILY_ALPHA_BRIEF_EVIDENCE_LANES:
        payload = evidence.get(lane)
        if isinstance(payload, dict):
            scopes.append(payload)
    for flag in DAILY_ALPHA_BRIEF_FORBIDDEN_ALLOW_FLAGS:
        for scope in scopes:
            if flag in scope and _truthy(scope.get(flag)):
                found.append(flag)
                break
    return tuple(found)


def _normalize_lane_stance(value: Any) -> str:
    """Map a caller-supplied stance string to a canonical lane stance. An
    unrecognized non-empty value -> 'unknown'; an empty value -> 'unknown'."""
    text = _as_text(value).lower()
    if not text:
        return LANE_STANCE_UNKNOWN
    if text in _SUPPORTIVE_ALIASES:
        return LANE_STANCE_SUPPORTIVE
    if text in _CAUTIONARY_ALIASES:
        return LANE_STANCE_CAUTIONARY
    if text in _NEUTRAL_ALIASES:
        return LANE_STANCE_NEUTRAL
    return LANE_STANCE_UNKNOWN


def _isolated(value: Any) -> Any:
    """Return an isolated (shallow-but-safe) copy of a value so the contract
    never shares mutable references with caller input."""
    if isinstance(value, dict):
        return {k: _isolated(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_isolated(v) for v in value]
    return value


def _lane_summary(lane: str, payload: Any) -> dict[str, Any]:
    """Summarize one evidence lane without executing anything. Pure echo plus a
    normalized stance. A non-dict / absent payload is 'absent'."""
    present = isinstance(payload, dict)
    src = payload if present else {}
    stance = _normalize_lane_stance(src.get("stance")) if present else (
        LANE_STANCE_UNKNOWN
    )
    return {
        "lane": lane,
        "present": present,
        "stance": stance,
        "headline": _as_text(src.get("headline")),
        "note": _as_text(src.get("note")),
        "metrics": _isolated(src.get("metrics")) if isinstance(
            src.get("metrics"), dict
        ) else {},
        "summary": (
            lane
            + ": "
            + ("present" if present else "absent")
            + ", stance="
            + stance
        ),
    }


def assess_daily_alpha_brief_evidence(evidence: Any) -> dict[str, Any]:
    """Return a deterministic daily-alpha-brief assessment for one evidence dict.
    Pure; no I/O, no data fetch, no clock read, no mutation, no random id.
    Malformed or partial inputs never raise -- missing lanes degrade to an
    AWAIT / INCOMPLETE_EVIDENCE result. Every output is attention-only research
    evidence and authorizes nothing."""
    ev = evidence if isinstance(evidence, dict) else {}

    lane_summaries: dict[str, dict[str, Any]] = {}
    present_lanes: list[str] = []
    missing_lanes: list[str] = []
    supportive_lanes: list[str] = []
    cautionary_lanes: list[str] = []
    neutral_lanes: list[str] = []

    for lane in DAILY_ALPHA_BRIEF_EVIDENCE_LANES:
        summary = _lane_summary(lane, ev.get(lane))
        lane_summaries[lane] = summary
        if summary["present"]:
            present_lanes.append(lane)
            if summary["stance"] == LANE_STANCE_SUPPORTIVE:
                supportive_lanes.append(lane)
            elif summary["stance"] == LANE_STANCE_CAUTIONARY:
                cautionary_lanes.append(lane)
            elif summary["stance"] == LANE_STANCE_NEUTRAL:
                neutral_lanes.append(lane)
        else:
            missing_lanes.append(lane)

    conflict = bool(supportive_lanes) and bool(cautionary_lanes)
    has_directional = bool(supportive_lanes) or bool(cautionary_lanes)

    if missing_lanes:
        decision = DECISION_AWAIT
    elif conflict:
        decision = DECISION_MIXED_WATCH
    elif has_directional:
        decision = DECISION_RESEARCH_WATCH_ONLY
    else:
        decision = DECISION_NEUTRAL_WATCH

    alpha_stance = _DECISION_TO_STANCE[decision]

    if conflict:
        aligned_direction = None
    elif supportive_lanes:
        aligned_direction = LANE_STANCE_SUPPORTIVE
    elif cautionary_lanes:
        aligned_direction = LANE_STANCE_CAUTIONARY
    else:
        aligned_direction = None

    forbidden = _requested_forbidden_flags(ev)

    return {
        "decision": decision,
        "alpha_stance": alpha_stance,
        "present_lanes": present_lanes,
        "missing_lanes": missing_lanes,
        "supportive_lanes": supportive_lanes,
        "cautionary_lanes": cautionary_lanes,
        "neutral_lanes": neutral_lanes,
        "conflict": conflict,
        "has_directional": has_directional,
        "aligned_direction": aligned_direction,
        "lane_summaries": lane_summaries,
        "requested_forbidden_flags": forbidden,
        "authorizes_nothing": True,
    }


def _market_context_section(assessment: dict[str, Any]) -> list[str]:
    present = assessment["present_lanes"]
    lanes_text = ", ".join(present) if present else "none"
    return [
        "Recognized evidence lanes present: "
        + str(len(present))
        + " of "
        + str(len(DAILY_ALPHA_BRIEF_EVIDENCE_LANES))
        + " ("
        + lanes_text
        + ").",
        "Overall research decision: " + assessment["decision"] + ".",
        "Overall research stance: "
        + assessment["alpha_stance"]
        + " (attention only).",
        "This is a research-only daily context summary; it is not a trade plan "
        "and it authorizes nothing.",
    ]


def _evidence_alignment_section(assessment: dict[str, Any]) -> list[str]:
    if assessment["decision"] == DECISION_AWAIT:
        return [
            "Evidence is incomplete; alignment cannot be assessed until all "
            "recognized lanes are provided.",
            "Incomplete evidence resolves to AWAIT; it never resolves to an "
            "execution decision.",
        ]
    if assessment["conflict"]:
        return [
            "Lanes conflict: at least one supportive-watch lane and at least "
            "one cautionary-watch lane are present.",
            "Conflicting evidence resolves to a research WATCH only; it never "
            "resolves to an execution decision.",
        ]
    if assessment["has_directional"]:
        direction = assessment["aligned_direction"] or LANE_STANCE_NEUTRAL
        return [
            "Directional lanes agree (" + direction + ").",
            "Aligned evidence resolves to a research WATCH only; aligned "
            "strength still authorizes nothing.",
        ]
    return [
        "All present lanes are neutral or unscored; there is no directional "
        "research signal.",
        "Neutral evidence resolves to a research WATCH only and authorizes "
        "nothing.",
    ]


def _caution_flags_section(assessment: dict[str, Any]) -> list[str]:
    flags: list[str] = []
    for lane in assessment["cautionary_lanes"]:
        flags.append(lane + " is cautionary-watch (attention only).")
    if assessment["conflict"]:
        flags.append(
            "Evidence lanes disagree; treat the brief with extra caution."
        )
    forbidden_count = len(assessment["requested_forbidden_flags"])
    if forbidden_count:
        flags.append(
            "Ignored "
            + str(forbidden_count)
            + " forbidden capability request(s); the brief authorizes none of "
            "them (see requested_forbidden_flags)."
        )
    if not flags:
        flags.append(
            "No caution flags raised; the absence of flags still authorizes "
            "nothing."
        )
    return flags


def _watchlist_section(assessment: dict[str, Any]) -> list[str]:
    items: list[str] = []
    for lane in DAILY_ALPHA_BRIEF_EVIDENCE_LANES:
        summary = assessment["lane_summaries"][lane]
        if summary["present"]:
            items.append(
                lane + ": " + summary["stance"] + " (attention only)"
            )
    if not items:
        items.append("No evidence lanes provided; nothing to watch yet.")
    return items


def _missing_evidence_section(assessment: dict[str, Any]) -> list[str]:
    missing = assessment["missing_lanes"]
    if not missing:
        return ["All recognized evidence lanes were provided."]
    lines = ["Missing evidence lane: " + lane for lane in missing]
    lines.append(
        "Brief returns AWAIT / INCOMPLETE_EVIDENCE until all recognized lanes "
        "are provided."
    )
    return lines


_NO_EXECUTION_AUTHORIZATION_SECTION: tuple[str, ...] = (
    "This daily alpha brief authorizes no trade and no position of any kind.",
    "It permits no data fetch, no API call, no dataset inspection, no QA, no "
    "baseline, and no backtest.",
    "It permits no paper trading, no live trading, no broker or exchange "
    "connection, and no automation.",
    "It writes no runtime, registry, ledger, or dashboard state.",
    "The highest stance it can produce is WATCH / RESEARCH_ONLY; it never "
    "produces an execution instruction.",
)

_OPERATOR_NEXT_STEP = (
    "Research-only: a human reviewer must read this brief as external research "
    "evidence, independently confirm every lane stance, and treat the brief as "
    "attention-only. The single permitted next step is to assemble or review "
    "the next research-only contract on paper. No execution of any kind is "
    "authorized."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 daily alpha brief research contract template and is "
    "execution-free.",
    "It organizes already-approved static evidence lanes into a research-only "
    "daily context summary; it runs nothing, fetches nothing, and connects "
    "nowhere.",
    "Core rule: the brief tells us what to watch and research, never what to "
    "trade.",
    "No data is fetched, no API is called, no dataset is inspected, and no real "
    "data is acquired -- the brief reads only the static evidence payloads the "
    "caller passes in.",
    "Missing evidence resolves to AWAIT; conflicting evidence resolves to "
    "MIXED_WATCH; aligned evidence resolves to RESEARCH_WATCH_ONLY -- never to "
    "paper or live trading.",
    "Every lane stance is attention-only evidence and needs independent "
    "confirmation; the brief never converts evidence into permission.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human reviewer must read the structured daily alpha brief before any "
    "further research-only contract is built.",
    "A human reviewer must confirm each lane stance is treated as "
    "attention-only evidence and is never wired to a data fetch, an API call, "
    "a dataset, a QA run, a backtest, a paper/live trade, a broker or "
    "exchange, an order, or any automation.",
    "A human reviewer must independently confirm every lane stance before it "
    "is trusted as evidence.",
    "A human reviewer must confirm the next step is only to BUILD or review "
    "the next research-only contract, still on paper.",
    "No execution, data fetch, API call, dataset inspection, data acquisition, "
    "QA, backtest, paper/live, broker/exchange, automation, promotion, or "
    "downstream-gate unlock may proceed.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "stage",
    "mode",
    "core_rule",
    "daily_alpha_brief_next_required_action",
    "daily_alpha_brief_current_stage",
    "evidence_lanes",
    "decisions",
    "stances",
    "lane_stances",
    "forbidden_allow_flags",
    "remaining_real_world_capabilities_blocked",
    "forbidden_trade_terms",
    "evidence",
    "assessment",
    "decision",
    "alpha_stance",
    "present_lanes",
    "missing_lanes",
    "input_evidence_summary",
    "market_context_section",
    "evidence_alignment_section",
    "caution_flags_section",
    "watchlist_section",
    "no_execution_authorization_section",
    "missing_evidence_section",
    "operator_next_step",
    "requested_forbidden_flags",
    "safety_posture",
    "operator_notes",
    "human_operator_required_next_steps",
    "requires_independent_confirmation",
    "human_approval_required",
    "read_only",
    "executes",
    "research_only",
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "unlocks_downstream_gate",
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the all-false posture (callers cannot taint)."""
    return dict(DAILY_ALPHA_BRIEF_SAFETY_POSTURE)


def build_crypto_d1_daily_alpha_brief_research_contract(
    evidence: Any = None,
) -> dict[str, Any]:
    """Build the read-only daily alpha brief research contract. Pure; no I/O, no
    data fetch, no mutation of inputs, no clock read, no random id. When no
    evidence is given, the static DEFAULT_SAMPLE_EVIDENCE is organized. A fresh
    dict (with fresh lists/dicts) is returned every call."""
    if evidence is None:
        source = _isolated(DEFAULT_SAMPLE_EVIDENCE)
    elif isinstance(evidence, dict):
        source = _isolated(evidence)
    else:
        source = {}

    assessment = assess_daily_alpha_brief_evidence(source)

    input_evidence_summary = {
        lane: dict(assessment["lane_summaries"][lane])
        for lane in DAILY_ALPHA_BRIEF_EVIDENCE_LANES
    }

    contract: dict[str, Any] = {
        "schema_version": DAILY_ALPHA_BRIEF_SCHEMA_VERSION,
        "label": DAILY_ALPHA_BRIEF_LABEL,
        "status": DAILY_ALPHA_BRIEF_STATUS,
        "stage": "CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_ONLY",
        "mode": DAILY_ALPHA_BRIEF_MODE,
        "core_rule": DAILY_ALPHA_BRIEF_CORE_RULE,
        "daily_alpha_brief_next_required_action": (
            DAILY_ALPHA_BRIEF_NEXT_REQUIRED_ACTION
        ),
        "daily_alpha_brief_current_stage": DAILY_ALPHA_BRIEF_CURRENT_STAGE,
        "evidence_lanes": DAILY_ALPHA_BRIEF_EVIDENCE_LANES,
        "decisions": DAILY_ALPHA_BRIEF_DECISIONS,
        "stances": DAILY_ALPHA_BRIEF_STANCES,
        "lane_stances": DAILY_ALPHA_BRIEF_LANE_STANCES,
        "forbidden_allow_flags": DAILY_ALPHA_BRIEF_FORBIDDEN_ALLOW_FLAGS,
        "remaining_real_world_capabilities_blocked": (
            DAILY_ALPHA_BRIEF_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
        ),
        "forbidden_trade_terms": DAILY_ALPHA_BRIEF_FORBIDDEN_TRADE_TERMS,
        "evidence": _isolated(source),
        "assessment": assessment,
        "decision": assessment["decision"],
        "alpha_stance": assessment["alpha_stance"],
        "present_lanes": list(assessment["present_lanes"]),
        "missing_lanes": list(assessment["missing_lanes"]),
        "input_evidence_summary": input_evidence_summary,
        "market_context_section": _market_context_section(assessment),
        "evidence_alignment_section": _evidence_alignment_section(assessment),
        "caution_flags_section": _caution_flags_section(assessment),
        "watchlist_section": _watchlist_section(assessment),
        "no_execution_authorization_section": list(
            _NO_EXECUTION_AUTHORIZATION_SECTION
        ),
        "missing_evidence_section": _missing_evidence_section(assessment),
        "operator_next_step": _OPERATOR_NEXT_STEP,
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
        "research_only": True,
        "authorizes_trading": False,
        "authorizes_data_fetch": False,
        "authorizes_backtest": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "authorizes_broker_exchange": False,
        "authorizes_automation": False,
        "authorizes_real_world_action": False,
        "unlocks_downstream_gate": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return contract


# Top-level posture flags that must all be exactly False for a valid contract.
_REQUIRED_FALSE_FLAGS: tuple[str, ...] = (
    "executes",
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "unlocks_downstream_gate",
)


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == DAILY_ALPHA_BRIEF_SCHEMA_VERSION
    )
    label_ok = safe.get("label") == DAILY_ALPHA_BRIEF_LABEL
    read_only = safe.get("read_only") is True
    research_only = (
        safe.get("research_only") is True
        and safe.get("mode") == "RESEARCH_ONLY"
    )
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_ONLY"
    )
    core_rule_ok = safe.get("core_rule") == DAILY_ALPHA_BRIEF_CORE_RULE
    human_required = safe.get("human_approval_required") is True
    confirmation_required = (
        safe.get("requires_independent_confirmation") is True
    )
    flags_false = all(
        safe.get(flag) is False for flag in _REQUIRED_FALSE_FLAGS
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

    lanes_ok = (
        tuple(safe.get("evidence_lanes") or ())
        == DAILY_ALPHA_BRIEF_EVIDENCE_LANES
    )
    decisions_ok = (
        tuple(safe.get("decisions") or ()) == DAILY_ALPHA_BRIEF_DECISIONS
    )
    stances_ok = (
        tuple(safe.get("stances") or ()) == DAILY_ALPHA_BRIEF_STANCES
    )
    lane_stances_ok = (
        tuple(safe.get("lane_stances") or ())
        == DAILY_ALPHA_BRIEF_LANE_STANCES
    )
    forbidden_ok = (
        tuple(safe.get("forbidden_allow_flags") or ())
        == DAILY_ALPHA_BRIEF_FORBIDDEN_ALLOW_FLAGS
    )
    remaining_ok = (
        tuple(safe.get("remaining_real_world_capabilities_blocked") or ())
        == DAILY_ALPHA_BRIEF_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )

    decision_ok = safe.get("decision") in _DECISION_SET
    stance_ok = safe.get("alpha_stance") in _STANCE_SET
    stance_consistent = (
        _DECISION_TO_STANCE.get(_as_text(safe.get("decision")))
        == safe.get("alpha_stance")
    )

    assessment = safe.get("assessment")
    assessment_ok = (
        isinstance(assessment, dict)
        and assessment.get("authorizes_nothing") is True
        and assessment.get("decision") in _DECISION_SET
        and assessment.get("alpha_stance") in _STANCE_SET
    )

    no_trade_language = _no_forbidden_trade_terms(safe)

    sections_ok = all(
        len(tuple(safe.get(section) or ())) >= 1
        for section in (
            "market_context_section",
            "evidence_alignment_section",
            "caution_flags_section",
            "watchlist_section",
            "no_execution_authorization_section",
            "missing_evidence_section",
            "operator_notes",
            "human_operator_required_next_steps",
        )
    )
    operator_next_step_ok = bool(_as_text(safe.get("operator_next_step")))

    valid = (
        not missing
        and schema_ok
        and label_ok
        and read_only
        and research_only
        and stage_ok
        and core_rule_ok
        and human_required
        and confirmation_required
        and flags_false
        and gates_locked
        and safety_all_false
        and lanes_ok
        and decisions_ok
        and stances_ok
        and lane_stances_ok
        and forbidden_ok
        and remaining_ok
        and decision_ok
        and stance_ok
        and stance_consistent
        and assessment_ok
        and no_trade_language
        and sections_ok
        and operator_next_step_ok
    )

    return {
        "valid": bool(valid),
        "missing_fields": missing,
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "read_only": read_only,
        "research_only": research_only,
        "stage_ok": stage_ok,
        "core_rule_ok": core_rule_ok,
        "human_required": human_required,
        "confirmation_required": confirmation_required,
        "flags_false": flags_false,
        "gates_locked": gates_locked,
        "safety_all_false": safety_all_false,
        "lanes_ok": lanes_ok,
        "decisions_ok": decisions_ok,
        "stances_ok": stances_ok,
        "lane_stances_ok": lane_stances_ok,
        "forbidden_ok": forbidden_ok,
        "remaining_ok": remaining_ok,
        "decision_ok": decision_ok,
        "stance_ok": stance_ok,
        "stance_consistent": stance_consistent,
        "assessment_ok": assessment_ok,
        "no_trade_language": no_trade_language,
        "sections_ok": sections_ok,
        "operator_next_step_ok": operator_next_step_ok,
    }


# The generated-guidance fields whose text is the brief's own actionable output.
# These must never contain an execution verb. (The raw echoed `evidence` and
# `input_evidence_summary` are caller input, not the brief's guidance, and are
# excluded from this scan.)
_ACTIONABLE_TEXT_FIELDS: tuple[str, ...] = (
    "decision",
    "alpha_stance",
    "operator_next_step",
    "market_context_section",
    "evidence_alignment_section",
    "caution_flags_section",
    "watchlist_section",
    "missing_evidence_section",
    "no_execution_authorization_section",
)


def _contains_forbidden_term(text: str) -> bool:
    """Whole-word check for any forbidden execution verb in a piece of text."""
    lowered = text.lower()
    tokens = set()
    word = []
    for ch in lowered:
        if ch.isalpha():
            word.append(ch)
        else:
            if word:
                tokens.add("".join(word))
                word = []
    if word:
        tokens.add("".join(word))
    return any(term in tokens for term in DAILY_ALPHA_BRIEF_FORBIDDEN_TRADE_TERMS)


def _no_forbidden_trade_terms(contract: dict[str, Any]) -> bool:
    """True when none of the brief's actionable guidance fields contain an
    execution verb as a whole word. Pure; reads only the contract dict."""
    for field in _ACTIONABLE_TEXT_FIELDS:
        value = contract.get(field)
        if isinstance(value, str):
            if _contains_forbidden_term(value):
                return False
        elif isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, str) and _contains_forbidden_term(item):
                    return False
    return True


def validate_crypto_d1_daily_alpha_brief_research_contract(
    contract: Any,
) -> dict[str, Any]:
    """Public validation entry point; returns the deterministic verdict dict."""
    return _validate(contract)


def render_crypto_d1_daily_alpha_brief_research_contract_markdown(
    contract: Any,
) -> str:
    """Render an informational, read-only markdown summary of the contract.
    Pure; builds and returns a string, writes nothing."""
    safe = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Daily Alpha Brief Research Contract")
    lines.append("")
    lines.append("- Label: " + _as_text(safe.get("label")))
    lines.append("- Mode: " + _as_text(safe.get("mode")))
    lines.append("- Status: " + _as_text(safe.get("status")))
    lines.append("- Decision: " + _as_text(safe.get("decision")))
    lines.append("- Research stance: " + _as_text(safe.get("alpha_stance")))
    lines.append("- Read-only: " + str(safe.get("read_only")))
    lines.append("- Executes: " + str(safe.get("executes")))
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
        "- micro_live_gate locked: " + str(safe.get("micro_live_gate_locked"))
    )

    def _emit(title: str, key: str) -> None:
        lines.append("")
        lines.append("## " + title)
        section = safe.get(key)
        if isinstance(section, (list, tuple)) and section:
            for item in section:
                lines.append("- " + _as_text(item))
        else:
            lines.append("- (none)")

    _emit("Market Context", "market_context_section")
    _emit("Evidence Alignment", "evidence_alignment_section")
    _emit("Caution Flags", "caution_flags_section")
    _emit("Watchlist", "watchlist_section")
    _emit("Missing Evidence", "missing_evidence_section")
    _emit("No Execution Authorization", "no_execution_authorization_section")
    lines.append("")
    lines.append("## Operator Next Step")
    lines.append("- " + _as_text(safe.get("operator_next_step")))
    return "\n".join(lines)

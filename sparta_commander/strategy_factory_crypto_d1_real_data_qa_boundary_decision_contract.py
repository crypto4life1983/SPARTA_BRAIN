"""Crypto-D1 Human-Controlled Real Data QA Boundary Decision Contract (Block 134).

A PURE, stdlib-only, *read-only* paper contract. It defines -- on paper only --
the HUMAN boundary decision that must be made BEFORE any Real Data QA work may
even be planned. It is the structured "decision packet / gate" a human reviews
at the mission-flow boundary:

    CURRENT_STAGE        = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    NEXT_REQUIRED_ACTION = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

It executes NOTHING. It does not fetch, acquire, load, inspect, transform, or
compute on any data, runs no QA, no baseline, no backtest, no simulation, touches
no broker / exchange / order / trading / paper / live surface, triggers no
automation, writes no file, reads no file, opens no network, spawns no
subprocess, reads no environment, uses no credential, mints no id, and records no
timestamp. It only reasons over a static, caller-supplied evidence summary.

CORE RULE: this contract NEVER unlocks Real Data QA. Even its most favourable
outcome (READY_FOR_HUMAN_DECISION) only assembles the decision packet for a human
to review; crossing the boundary into Real Data QA *planning* requires a separate,
future, explicitly human-approved step. real_data_qa stays BLOCKED, baseline
stays BLOCKED, and the paper / micro-live gates stay LOCKED here, always.

Evidence quality gate (consumes the recent support contracts):
  - Block 131 Strategy Evidence Scoring  -> required outcome PROMOTE_TO_REVIEW.
  - Block 132 Cohort Independence / Correlation Penalty -> required label
    INDEPENDENT, with at least the minimum independent booked cohort count.
  - Daily Alpha Brief approval chain      -> required verdict APPROVED.
The contract REJECTS (BLOCK) external-evidence-only or empty evidence, and AWAITS
(AWAIT_EVIDENCE) when evidence is open/unrealized-only, correlated, duplicated, or
an insufficient sample, or when any upstream verdict has not yet reached its
required passing value.

Outcomes (exactly one, by precedence BLOCK > AWAIT_EVIDENCE > READY):
  - BLOCK                    : evidence/posture disqualifies a boundary decision.
  - AWAIT_EVIDENCE           : not yet enough independent booked proof to decide.
  - READY_FOR_HUMAN_DECISION : packet assembled; a human must still decide. It
                               still authorizes nothing and unlocks nothing.

Public API:
  - RDQ_BOUNDARY_SCHEMA_VERSION
  - RDQ_BOUNDARY_LABEL
  - RDQ_BOUNDARY_STATUS
  - RDQ_BOUNDARY_MODE
  - RDQ_BOUNDARY_CORE_RULE
  - RDQ_BOUNDARY_NEXT_REQUIRED_ACTION
  - RDQ_BOUNDARY_CURRENT_STAGE
  - RDQ_BOUNDARY_MISSION_FLOW_CURRENT_STAGE
  - RDQ_BOUNDARY_MISSION_FLOW_NEXT_REQUIRED_ACTION
  - RDQ_BOUNDARY_MIN_INDEPENDENT_BOOKED_COHORTS
  - RDQ_BOUNDARY_REQUIRED_EVIDENCE_SCORING_OUTCOME
  - RDQ_BOUNDARY_REQUIRED_COHORT_INDEPENDENCE_LABEL
  - RDQ_BOUNDARY_REQUIRED_DAILY_ALPHA_BRIEF_VERDICT
  - OUTCOME_BLOCK / OUTCOME_AWAIT_EVIDENCE / OUTCOME_READY_FOR_HUMAN_DECISION
  - RDQ_BOUNDARY_OUTCOMES
  - RDQ_BOUNDARY_BLOCK_EVIDENCE_QUALITY_SIGNALS
  - RDQ_BOUNDARY_AWAIT_EVIDENCE_QUALITY_SIGNALS
  - RDQ_BOUNDARY_HUMAN_ACKNOWLEDGEMENTS_REQUIRED
  - RDQ_BOUNDARY_DECISION_OPTIONS
  - RDQ_BOUNDARY_OBSERVATION_ONLY_EVIDENCE_LANES
  - RDQ_BOUNDARY_TRADE_SOURCE_TAGS
  - RDQ_BOUNDARY_EXTERNAL_RESEARCH_SOURCE_TAGS
  - RDQ_BOUNDARY_BOOKED_STATUS_TAGS
  - RDQ_BOUNDARY_OPEN_STATUS_TAGS
  - RDQ_BOUNDARY_AUTHORIZATION_FLAGS
  - RDQ_BOUNDARY_GATE_LOCK_FLAGS
  - RDQ_BOUNDARY_GATE_UNLOCK_REQUEST_FLAGS
  - RDQ_BOUNDARY_FORBIDDEN_PROMOTION_REQUEST_FLAGS
  - RDQ_BOUNDARY_EXECUTABLE_SIGNAL_FIELDS
  - RDQ_BOUNDARY_FORBIDDEN_TRADE_TERMS
  - RDQ_BOUNDARY_SAFETY_POSTURE
  - DEFAULT_SAMPLE_BOUNDARY_INPUT
  - assess_real_data_qa_boundary_decision(payload)
  - build_human_boundary_decision_packet(payload=None)
  - build_crypto_d1_real_data_qa_boundary_decision_contract(payload=None)
  - validate_crypto_d1_real_data_qa_boundary_decision_contract(contract)
  - render_crypto_d1_real_data_qa_boundary_decision_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

RDQ_BOUNDARY_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract.v1"
)
RDQ_BOUNDARY_LABEL = (
    "Block 134 - Crypto-D1 Human-Controlled Real Data QA Boundary Decision "
    "Contract"
)
RDQ_BOUNDARY_STATUS = (
    "READ_ONLY_CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT"
)
RDQ_BOUNDARY_MODE = "RESEARCH_ONLY"

RDQ_BOUNDARY_CORE_RULE = (
    "This contract NEVER unlocks Real Data QA. It only defines the human "
    "decision packet and the gate to review at the boundary. Even a "
    "READY_FOR_HUMAN_DECISION outcome authorizes nothing: crossing into Real "
    "Data QA planning requires a separate, future, explicitly human-approved "
    "step. real_data_qa stays BLOCKED, baseline stays BLOCKED, and the paper / "
    "micro-live gates stay LOCKED here, always."
)

# The action that BUILDING this contract satisfies, and the stage it occupies.
RDQ_BOUNDARY_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT"
)
RDQ_BOUNDARY_CURRENT_STAGE = (
    "CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_REQUIRED"
)

# The current mission-flow truth this contract is anchored to. These mirror the
# read-only mission-flow registry / status modules (the boundary the pipeline has
# reached). The companion test cross-checks them against the live status module
# so they cannot silently drift.
RDQ_BOUNDARY_MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
RDQ_BOUNDARY_MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# Minimum number of INDEPENDENT booked cohorts before a human boundary decision
# may even be assembled. Matches the Block 132 promote-support threshold.
RDQ_BOUNDARY_MIN_INDEPENDENT_BOOKED_COHORTS = 3

# Required passing values from the upstream support contracts. Anything else
# AWAITS (or, for a hard upstream block, BLOCKS).
RDQ_BOUNDARY_REQUIRED_EVIDENCE_SCORING_OUTCOME = "PROMOTE_TO_REVIEW"
RDQ_BOUNDARY_REQUIRED_COHORT_INDEPENDENCE_LABEL = "INDEPENDENT"
RDQ_BOUNDARY_REQUIRED_DAILY_ALPHA_BRIEF_VERDICT = "APPROVED"

# Upstream values that constitute a hard upstream block (not merely "await").
_UPSTREAM_HARD_BLOCK_SCORING_OUTCOMES: frozenset[str] = frozenset({"BLOCK"})

# Boundary-decision outcomes (exactly one assigned), in precedence order.
OUTCOME_BLOCK = "BLOCK"
OUTCOME_AWAIT_EVIDENCE = "AWAIT_EVIDENCE"
OUTCOME_READY_FOR_HUMAN_DECISION = "READY_FOR_HUMAN_DECISION"

RDQ_BOUNDARY_OUTCOMES: tuple[str, ...] = (
    OUTCOME_BLOCK,
    OUTCOME_AWAIT_EVIDENCE,
    OUTCOME_READY_FOR_HUMAN_DECISION,
)
_OUTCOME_PRECEDENCE: dict[str, int] = {
    OUTCOME_BLOCK: 0,
    OUTCOME_AWAIT_EVIDENCE: 1,
    OUTCOME_READY_FOR_HUMAN_DECISION: 2,
}

# Evidence-quality signals that REJECT a boundary decision outright (BLOCK).
RDQ_BOUNDARY_BLOCK_EVIDENCE_QUALITY_SIGNALS: tuple[str, ...] = (
    "no_evidence",
    "external_evidence_only",
)

# Evidence-quality signals that hold the decision (AWAIT_EVIDENCE).
RDQ_BOUNDARY_AWAIT_EVIDENCE_QUALITY_SIGNALS: tuple[str, ...] = (
    "open_unrealized_only",
    "correlated",
    "duplicate",
    "insufficient_sample",
)

# The acknowledgements a human must affirm in the packet before any future step
# could ever authorize Real Data QA planning. They are statements to confirm, not
# actions; affirming them here still authorizes nothing.
RDQ_BOUNDARY_HUMAN_ACKNOWLEDGEMENTS_REQUIRED: tuple[str, ...] = (
    "I confirm real_data_qa is currently BLOCKED and this contract does not "
    "change that.",
    "I have reviewed the Block 131 strategy evidence scoring outcome.",
    "I have reviewed the Block 132 cohort independence / correlation result.",
    "I have reviewed the Daily Alpha Brief approval verdict.",
    "I understand any approval here applies ONLY to planning Real Data QA, "
    "never to data acquisition, QA execution, baseline, backtest, paper, or "
    "live activity.",
    "I understand a separate, future, explicitly human-approved step is "
    "required to actually plan Real Data QA.",
)

# The choices a human may record. APPROVE applies to PLANNING ONLY and still
# does not unlock anything in this contract -- it is recorded for a future step.
RDQ_BOUNDARY_DECISION_OPTIONS: tuple[str, ...] = (
    "AWAIT",
    "DECLINE",
    "APPROVE_REAL_DATA_QA_PLANNING_ONLY",
)
_DECISION_OPTION_SET: frozenset[str] = frozenset(RDQ_BOUNDARY_DECISION_OPTIONS)

# Evidence lanes that remain observation-only at every outcome.
RDQ_BOUNDARY_OBSERVATION_ONLY_EVIDENCE_LANES: tuple[str, ...] = (
    "external_bot_evidence",
    "hyperliquid_whale_evidence",
    "funding_rate_evidence",
    "bitcoin_cycle_timing_evidence",
    "daily_alpha_brief",
    "open_unrealized_pnl",
)

# Source tags treated as first-party trade evidence (booked or open). An empty /
# missing source defaults to trade evidence.
RDQ_BOUNDARY_TRADE_SOURCE_TAGS: tuple[str, ...] = (
    "trade",
    "booked_trade",
    "closed_trade",
    "open_trade",
    "position",
)

# Source tags treated as external research context. These NEVER count as a
# booked independent cohort.
RDQ_BOUNDARY_EXTERNAL_RESEARCH_SOURCE_TAGS: tuple[str, ...] = (
    "external_bot",
    "hyperliquid_whale",
    "whale",
    "funding_rate",
    "bitcoin_cycle_timing",
    "btc_cycle",
    "daily_alpha_brief",
    "daily_alpha",
)

# Record statuses treated as BOOKED (closed / realized) -> can supply proof.
RDQ_BOUNDARY_BOOKED_STATUS_TAGS: tuple[str, ...] = (
    "closed",
    "booked",
    "realized",
    "settled",
)

# Record statuses treated as OPEN (unrealized) -> observation only.
RDQ_BOUNDARY_OPEN_STATUS_TAGS: tuple[str, ...] = (
    "open",
    "unrealized",
    "live",
    "running",
    "floating",
)

# Top-level (or per-record) authorization flags that, if truthy, force a block.
RDQ_BOUNDARY_AUTHORIZATION_FLAGS: tuple[str, ...] = (
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

# Gate-lock flags that MUST be True (blocked / locked). If present and not True,
# the payload tried to unlock a gate -> block.
RDQ_BOUNDARY_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, force a block.
RDQ_BOUNDARY_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
)

# Requests asking the boundary decision to mean execution / live promotion. Any
# truthy value forces a block: this contract can only assemble a human packet.
RDQ_BOUNDARY_FORBIDDEN_PROMOTION_REQUEST_FLAGS: tuple[str, ...] = (
    "force_promote",
    "promote_to_live",
    "promote_to_paper",
    "approve_trade",
    "authorize_trade",
    "execute",
    "place_order",
    "go_live",
)

# Fields whose presence (non-empty) on a record signals an executable order /
# signal instruction rather than historical evidence -> block.
RDQ_BOUNDARY_EXECUTABLE_SIGNAL_FIELDS: tuple[str, ...] = (
    "order",
    "signal",
    "trade_instruction",
    "execution",
    "live_order",
    "place_order",
)

# Execution / promotion verbs the contract's generated guidance must never
# contain as whole words.
RDQ_BOUNDARY_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
    "order",
)

# Read-only safety posture. The three True flags are *posture* facts; every
# capability / authorization / unlock flag is False.
RDQ_BOUNDARY_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "executes": False,
    "human_approval_required": True,
    "authorizes_trading": False,
    "authorizes_data_fetch": False,
    "authorizes_backtest": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_automation": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}

_TRADE_SOURCE_SET: frozenset[str] = frozenset(RDQ_BOUNDARY_TRADE_SOURCE_TAGS)
_EXTERNAL_SOURCE_SET: frozenset[str] = frozenset(
    RDQ_BOUNDARY_EXTERNAL_RESEARCH_SOURCE_TAGS
)
_BOOKED_STATUS_SET: frozenset[str] = frozenset(RDQ_BOUNDARY_BOOKED_STATUS_TAGS)
_OPEN_STATUS_SET: frozenset[str] = frozenset(RDQ_BOUNDARY_OPEN_STATUS_TAGS)


# A deterministic, illustrative paper sample. The evidence is three booked ETH
# records sharing one macro move and the same direction -- promising but
# CORRELATED and an insufficient sample -- and none of the upstream verdicts has
# reached its required value. The default boundary outcome is therefore
# AWAIT_EVIDENCE: the gate holds. Nothing here is real data; static example only.
DEFAULT_SAMPLE_BOUNDARY_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 real data QA boundary input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "research_only": True,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
    "mission_flow_current_stage": (
        "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
    ),
    "mission_flow_next_required_action": (
        "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
    ),
    "evidence_scoring_outcome": "KEEP_WATCH",
    "cohort_independence_label": "CORRELATED",
    "daily_alpha_brief_verdict": "PENDING",
    "independent_booked_cohort_count": 1,
    "human_decision": None,
    "evidence": [
        {
            "id": "E",
            "symbol": "ETH",
            "direction": "short",
            "status": "closed",
            "pnl": 1.4,
            "macro_event": "eth_dump_2026_05",
            "source": "trade",
        },
        {
            "id": "E2",
            "symbol": "ETH",
            "direction": "short",
            "status": "closed",
            "pnl": 0.9,
            "macro_event": "eth_dump_2026_05",
            "source": "trade",
        },
        {
            "id": "F2",
            "symbol": "ETH",
            "direction": "short",
            "status": "closed",
            "pnl": 1.1,
            "macro_event": "eth_dump_2026_05",
            "source": "trade",
        },
    ],
}


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _norm(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


def _upper(value: Any) -> str:
    return str(value).strip().upper() if value is not None else ""


def _is_truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _as_payload(payload: Any) -> dict[str, Any]:
    return dict(payload) if isinstance(payload, dict) else {}


def _as_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    raw = payload.get("evidence")
    if not isinstance(raw, (list, tuple)):
        return []
    return [dict(r) for r in raw if isinstance(r, dict)]


def _source_kind(record: dict[str, Any]) -> str:
    """Classify a record as 'trade', 'external', or 'unknown' by its source."""
    source = _norm(record.get("source"))
    if source == "":
        return "trade"
    if source in _EXTERNAL_SOURCE_SET:
        return "external"
    if source in _TRADE_SOURCE_SET:
        return "trade"
    return "unknown"


def _status_kind(record: dict[str, Any]) -> str:
    status = _norm(record.get("status"))
    if status in _BOOKED_STATUS_SET:
        return "booked"
    if status in _OPEN_STATUS_SET:
        return "open"
    return "unknown"


def _forbidden_flag_hits(payload: dict[str, Any]) -> list[str]:
    """Collect any payload (or per-record) keys that attempt to authorize,
    unlock, promote, or carry an executable instruction."""
    hits: list[str] = []
    scopes: list[dict[str, Any]] = [payload]
    scopes.extend(r for r in _as_records(payload))
    for scope in scopes:
        for flag in RDQ_BOUNDARY_AUTHORIZATION_FLAGS:
            if _is_truthy(scope.get(flag)):
                hits.append(flag)
        for flag in RDQ_BOUNDARY_GATE_UNLOCK_REQUEST_FLAGS:
            if _is_truthy(scope.get(flag)):
                hits.append(flag)
        for flag in RDQ_BOUNDARY_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
            if _is_truthy(scope.get(flag)):
                hits.append(flag)
        for field in RDQ_BOUNDARY_EXECUTABLE_SIGNAL_FIELDS:
            value = scope.get(field)
            if value not in (None, "", [], {}, 0, False):
                hits.append(field)
        # Gate-lock flags, if explicitly present, must remain True.
        for flag in RDQ_BOUNDARY_GATE_LOCK_FLAGS:
            if flag in scope and not _is_truthy(scope.get(flag)):
                hits.append("unlocked:" + flag)
    # stable, de-duplicated order
    seen: set[str] = set()
    ordered: list[str] = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            ordered.append(h)
    return ordered


def _evidence_quality(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Re-derive the Block 131 / 132 style evidence-quality signals from a static
    record set. No grouping is executed against real data; this only reads the
    caller-supplied summary records."""
    trade_records = [r for r in records if _source_kind(r) == "trade"]
    external_records = [r for r in records if _source_kind(r) == "external"]
    booked_trades = [r for r in trade_records if _status_kind(r) == "booked"]
    open_trades = [r for r in trade_records if _status_kind(r) == "open"]

    # duplicate: same symbol+direction appears more than once among booked trades
    sym_dir_counts: dict[tuple[str, str], int] = {}
    for r in booked_trades:
        key = (_norm(r.get("symbol")), _norm(r.get("direction")))
        sym_dir_counts[key] = sym_dir_counts.get(key, 0) + 1
    duplicate = any(c > 1 for c in sym_dir_counts.values())

    # correlated: a shared macro_event collapses booked trades into one event
    macro_counts: dict[str, int] = {}
    for r in booked_trades:
        macro = _norm(r.get("macro_event"))
        if macro:
            macro_counts[macro] = macro_counts.get(macro, 0) + 1
    correlated = any(c > 1 for c in macro_counts.values())

    no_evidence = len(records) == 0
    external_evidence_only = (
        len(records) > 0 and len(trade_records) == 0 and len(external_records) > 0
    )
    open_unrealized_only = (
        len(trade_records) > 0 and len(booked_trades) == 0 and len(open_trades) > 0
    )

    return {
        "record_count": len(records),
        "trade_record_count": len(trade_records),
        "external_record_count": len(external_records),
        "booked_count": len(booked_trades),
        "open_count": len(open_trades),
        "no_evidence": no_evidence,
        "external_evidence_only": external_evidence_only,
        "open_unrealized_only": open_unrealized_only,
        "duplicate": duplicate,
        "correlated": correlated,
    }


# --------------------------------------------------------------------------- #
# assessment
# --------------------------------------------------------------------------- #
def assess_real_data_qa_boundary_decision(payload: Any) -> dict[str, Any]:
    """Assess (read-only) whether a human Real Data QA boundary decision may even
    be assembled. Returns a fresh dict every call. Authorizes nothing and unlocks
    nothing under any outcome."""
    data = _as_payload(payload)
    records = _as_records(data)
    quality = _evidence_quality(records)

    upstream_scoring = _upper(data.get("evidence_scoring_outcome"))
    upstream_cohort = _upper(data.get("cohort_independence_label"))
    upstream_brief = _upper(data.get("daily_alpha_brief_verdict"))
    try:
        independent_booked_cohort_count = int(
            data.get("independent_booked_cohort_count", 0)
        )
    except (TypeError, ValueError):
        independent_booked_cohort_count = 0

    mf_stage = data.get(
        "mission_flow_current_stage", RDQ_BOUNDARY_MISSION_FLOW_CURRENT_STAGE
    )
    mf_action = data.get(
        "mission_flow_next_required_action",
        RDQ_BOUNDARY_MISSION_FLOW_NEXT_REQUIRED_ACTION,
    )
    mission_flow_aligned = (
        str(mf_stage) == RDQ_BOUNDARY_MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == RDQ_BOUNDARY_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_hits = _forbidden_flag_hits(data)

    block_reasons: list[str] = []
    await_reasons: list[str] = []

    # --- hard blocks ---
    if forbidden_hits:
        block_reasons.append(
            "payload requested authorization / unlock / promotion / execution: "
            + ", ".join(forbidden_hits)
        )
    if not mission_flow_aligned:
        block_reasons.append(
            "mission flow is not at the human-controlled real data QA boundary; "
            "no boundary decision may be assembled"
        )
    for sig in RDQ_BOUNDARY_BLOCK_EVIDENCE_QUALITY_SIGNALS:
        if quality.get(sig):
            block_reasons.append("evidence quality block signal: " + sig)
    if upstream_scoring in _UPSTREAM_HARD_BLOCK_SCORING_OUTCOMES:
        block_reasons.append(
            "upstream Block 131 strategy evidence scoring outcome is BLOCK"
        )

    # --- awaits (only matter if not already blocked) ---
    for sig in RDQ_BOUNDARY_AWAIT_EVIDENCE_QUALITY_SIGNALS:
        if quality.get(sig):
            await_reasons.append("evidence quality await signal: " + sig)
    if independent_booked_cohort_count < RDQ_BOUNDARY_MIN_INDEPENDENT_BOOKED_COHORTS:
        await_reasons.append(
            "independent booked cohort count "
            + str(independent_booked_cohort_count)
            + " is below the required minimum "
            + str(RDQ_BOUNDARY_MIN_INDEPENDENT_BOOKED_COHORTS)
        )
    if upstream_scoring != RDQ_BOUNDARY_REQUIRED_EVIDENCE_SCORING_OUTCOME:
        await_reasons.append(
            "Block 131 strategy evidence scoring outcome is not yet "
            + RDQ_BOUNDARY_REQUIRED_EVIDENCE_SCORING_OUTCOME
        )
    if upstream_cohort != RDQ_BOUNDARY_REQUIRED_COHORT_INDEPENDENCE_LABEL:
        await_reasons.append(
            "Block 132 cohort independence label is not yet "
            + RDQ_BOUNDARY_REQUIRED_COHORT_INDEPENDENCE_LABEL
        )
    if upstream_brief != RDQ_BOUNDARY_REQUIRED_DAILY_ALPHA_BRIEF_VERDICT:
        await_reasons.append(
            "Daily Alpha Brief verdict is not yet "
            + RDQ_BOUNDARY_REQUIRED_DAILY_ALPHA_BRIEF_VERDICT
        )

    if block_reasons:
        outcome = OUTCOME_BLOCK
    elif await_reasons:
        outcome = OUTCOME_AWAIT_EVIDENCE
    else:
        outcome = OUTCOME_READY_FOR_HUMAN_DECISION

    upstream_gate = {
        "evidence_scoring_outcome": upstream_scoring or None,
        "evidence_scoring_required": (
            RDQ_BOUNDARY_REQUIRED_EVIDENCE_SCORING_OUTCOME
        ),
        "evidence_scoring_met": (
            upstream_scoring == RDQ_BOUNDARY_REQUIRED_EVIDENCE_SCORING_OUTCOME
        ),
        "cohort_independence_label": upstream_cohort or None,
        "cohort_independence_required": (
            RDQ_BOUNDARY_REQUIRED_COHORT_INDEPENDENCE_LABEL
        ),
        "cohort_independence_met": (
            upstream_cohort == RDQ_BOUNDARY_REQUIRED_COHORT_INDEPENDENCE_LABEL
        ),
        "daily_alpha_brief_verdict": upstream_brief or None,
        "daily_alpha_brief_required": (
            RDQ_BOUNDARY_REQUIRED_DAILY_ALPHA_BRIEF_VERDICT
        ),
        "daily_alpha_brief_met": (
            upstream_brief == RDQ_BOUNDARY_REQUIRED_DAILY_ALPHA_BRIEF_VERDICT
        ),
        "independent_booked_cohort_count": independent_booked_cohort_count,
        "min_independent_booked_cohorts": (
            RDQ_BOUNDARY_MIN_INDEPENDENT_BOOKED_COHORTS
        ),
        "independent_booked_cohorts_met": (
            independent_booked_cohort_count
            >= RDQ_BOUNDARY_MIN_INDEPENDENT_BOOKED_COHORTS
        ),
    }

    return {
        "mode": RDQ_BOUNDARY_MODE,
        "outcome": outcome,
        "mission_flow_current_stage": str(mf_stage),
        "mission_flow_next_required_action": str(mf_action),
        "mission_flow_aligned": mission_flow_aligned,
        "evidence_present": quality["record_count"] > 0,
        "evidence_quality": quality,
        "upstream_gate": upstream_gate,
        "forbidden_flag_hits": list(forbidden_hits),
        "block_reasons": list(block_reasons),
        "await_reasons": list(await_reasons),
        "ready_for_human_decision": outcome == OUTCOME_READY_FOR_HUMAN_DECISION,
        "assesses_research_only": True,
        "unlocks_real_data_qa": False,
        "promotes_beyond_boundary": False,
        "authorizes_nothing": True,
    }


# --------------------------------------------------------------------------- #
# human decision packet
# --------------------------------------------------------------------------- #
def build_human_boundary_decision_packet(payload: Any = None) -> dict[str, Any]:
    """Assemble (read-only) the structured human decision packet for the Real
    Data QA boundary. The packet defines what a human must review and the options
    they may record; it never makes, infers, or applies a decision, and it
    unlocks nothing. A fresh dict is returned every call."""
    data = (
        dict(DEFAULT_SAMPLE_BOUNDARY_INPUT)
        if payload is None
        else _as_payload(payload)
    )
    assessment = assess_real_data_qa_boundary_decision(data)

    raw_decision = data.get("human_decision")
    decision = _upper(raw_decision) if raw_decision not in (None, "") else None
    decision_recognized = decision in _DECISION_OPTION_SET if decision else False
    # A recorded decision is captured verbatim for a FUTURE step. It is never
    # applied here: this contract still unlocks nothing under any decision.
    return {
        "mission_flow_current_stage": (
            assessment["mission_flow_current_stage"]
        ),
        "mission_flow_next_required_action": (
            assessment["mission_flow_next_required_action"]
        ),
        "mission_flow_aligned": assessment["mission_flow_aligned"],
        "outcome": assessment["outcome"],
        "ready_for_human_decision": assessment["ready_for_human_decision"],
        "evidence_quality": dict(assessment["evidence_quality"]),
        "upstream_gate": dict(assessment["upstream_gate"]),
        "block_reasons": list(assessment["block_reasons"]),
        "await_reasons": list(assessment["await_reasons"]),
        "human_acknowledgements_required": list(
            RDQ_BOUNDARY_HUMAN_ACKNOWLEDGEMENTS_REQUIRED
        ),
        "decision_options": list(RDQ_BOUNDARY_DECISION_OPTIONS),
        "human_decision_recorded": decision,
        "human_decision_recognized": decision_recognized,
        "human_decision_applied": False,
        "requires_separate_future_human_approved_step": True,
        "unlocks_real_data_qa": False,
        "authorizes_nothing": True,
    }


# --------------------------------------------------------------------------- #
# contract build
# --------------------------------------------------------------------------- #
def _operator_next_step(assessment: dict[str, Any]) -> str:
    outcome = assessment["outcome"]
    if outcome == OUTCOME_BLOCK:
        return (
            "Hold at the boundary. The evidence or posture disqualifies a human "
            "decision packet right now. Resolve the listed block reasons in "
            "research only; do not acquire data, run QA, baseline, or any "
            "real-money activity."
        )
    if outcome == OUTCOME_AWAIT_EVIDENCE:
        return (
            "Await stronger evidence. Gather more independent booked proof and "
            "let the upstream support contracts reach their required verdicts. "
            "No data acquisition, QA, baseline, or real-money activity is "
            "implied; real_data_qa remains BLOCKED."
        )
    return (
        "Present the assembled packet to a human reviewer. A human may record "
        "AWAIT, DECLINE, or APPROVE_REAL_DATA_QA_PLANNING_ONLY. Even an approval "
        "applies only to planning and unlocks nothing here; a separate, future, "
        "explicitly human-approved step is required before any Real Data QA "
        "planning may begin."
    )


def build_crypto_d1_real_data_qa_boundary_decision_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only Real Data QA Boundary Decision
    Contract record. All capability flags are False and all gate locks are True
    regardless of the assessed outcome."""
    data = (
        dict(DEFAULT_SAMPLE_BOUNDARY_INPUT)
        if payload is None
        else _as_payload(payload)
    )
    assessment = assess_real_data_qa_boundary_decision(data)
    packet = build_human_boundary_decision_packet(data)

    contract: dict[str, Any] = {
        "schema_version": RDQ_BOUNDARY_SCHEMA_VERSION,
        "label": RDQ_BOUNDARY_LABEL,
        "status": RDQ_BOUNDARY_STATUS,
        "stage": RDQ_BOUNDARY_CURRENT_STAGE,
        "mode": RDQ_BOUNDARY_MODE,
        "core_rule": RDQ_BOUNDARY_CORE_RULE,
        "boundary_next_required_action": RDQ_BOUNDARY_NEXT_REQUIRED_ACTION,
        "boundary_current_stage": RDQ_BOUNDARY_CURRENT_STAGE,
        "mission_flow_current_stage": (
            RDQ_BOUNDARY_MISSION_FLOW_CURRENT_STAGE
        ),
        "mission_flow_next_required_action": (
            RDQ_BOUNDARY_MISSION_FLOW_NEXT_REQUIRED_ACTION
        ),
        "mission_flow_aligned": assessment["mission_flow_aligned"],
        "outcomes": list(RDQ_BOUNDARY_OUTCOMES),
        "outcome": assessment["outcome"],
        "ready_for_human_decision": assessment["ready_for_human_decision"],
        "required_evidence_scoring_outcome": (
            RDQ_BOUNDARY_REQUIRED_EVIDENCE_SCORING_OUTCOME
        ),
        "required_cohort_independence_label": (
            RDQ_BOUNDARY_REQUIRED_COHORT_INDEPENDENCE_LABEL
        ),
        "required_daily_alpha_brief_verdict": (
            RDQ_BOUNDARY_REQUIRED_DAILY_ALPHA_BRIEF_VERDICT
        ),
        "min_independent_booked_cohorts": (
            RDQ_BOUNDARY_MIN_INDEPENDENT_BOOKED_COHORTS
        ),
        "block_evidence_quality_signals": list(
            RDQ_BOUNDARY_BLOCK_EVIDENCE_QUALITY_SIGNALS
        ),
        "await_evidence_quality_signals": list(
            RDQ_BOUNDARY_AWAIT_EVIDENCE_QUALITY_SIGNALS
        ),
        "observation_only_evidence_lanes": list(
            RDQ_BOUNDARY_OBSERVATION_ONLY_EVIDENCE_LANES
        ),
        "trade_source_tags": list(RDQ_BOUNDARY_TRADE_SOURCE_TAGS),
        "external_research_source_tags": list(
            RDQ_BOUNDARY_EXTERNAL_RESEARCH_SOURCE_TAGS
        ),
        "booked_status_tags": list(RDQ_BOUNDARY_BOOKED_STATUS_TAGS),
        "open_status_tags": list(RDQ_BOUNDARY_OPEN_STATUS_TAGS),
        "authorization_flags": list(RDQ_BOUNDARY_AUTHORIZATION_FLAGS),
        "gate_lock_flags": list(RDQ_BOUNDARY_GATE_LOCK_FLAGS),
        "gate_unlock_request_flags": list(
            RDQ_BOUNDARY_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_promotion_request_flags": list(
            RDQ_BOUNDARY_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ),
        "executable_signal_fields": list(
            RDQ_BOUNDARY_EXECUTABLE_SIGNAL_FIELDS
        ),
        "forbidden_trade_terms": list(RDQ_BOUNDARY_FORBIDDEN_TRADE_TERMS),
        "decision_options": list(RDQ_BOUNDARY_DECISION_OPTIONS),
        "human_acknowledgements_required": list(
            RDQ_BOUNDARY_HUMAN_ACKNOWLEDGEMENTS_REQUIRED
        ),
        "assessment": assessment,
        "human_decision_packet": packet,
        "evidence_quality": dict(assessment["evidence_quality"]),
        "upstream_gate": dict(assessment["upstream_gate"]),
        "block_reasons": list(assessment["block_reasons"]),
        "await_reasons": list(assessment["await_reasons"]),
        "operator_next_step": _operator_next_step(assessment),
        "operator_notes": (
            "Read-only boundary decision contract. It defines the human packet "
            "and gate before Real Data QA planning. It assembles, it never "
            "decides; even READY_FOR_HUMAN_DECISION authorizes nothing."
        ),
        "human_operator_required_next_steps": [
            "A human reviews the assembled packet and the upstream gate.",
            "A human records AWAIT, DECLINE, or APPROVE_REAL_DATA_QA_PLANNING_"
            "ONLY.",
            "A separate, future, explicitly human-approved step is required "
            "before any Real Data QA planning may begin.",
        ],
        "safety_posture": dict(RDQ_BOUNDARY_SAFETY_POSTURE),
        "requires_independent_confirmation": True,
        "requires_separate_future_human_approved_step": True,
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
        "authorizes_nothing": True,
        "unlocks_downstream_gate": False,
        "unlocks_real_data_qa": False,
        "unlocks_baseline_backtest": False,
        "unlocks_paper_trading": False,
        "unlocks_micro_live": False,
        "promotes_beyond_boundary": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return contract


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "stage",
    "mode",
    "core_rule",
    "mission_flow_current_stage",
    "mission_flow_next_required_action",
    "outcome",
    "outcomes",
    "assessment",
    "human_decision_packet",
    "upstream_gate",
    "operator_next_step",
    "safety_posture",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "unlocks_downstream_gate",
    "unlocks_real_data_qa",
    "unlocks_baseline_backtest",
    "unlocks_paper_trading",
    "unlocks_micro_live",
    "promotes_beyond_boundary",
)

_ALL_GATE_LOCKS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def validate_crypto_d1_real_data_qa_boundary_decision_contract(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built contract. Returns a verdict dict of boolean
    checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == RDQ_BOUNDARY_SCHEMA_VERSION
    label_ok = c.get("label") == RDQ_BOUNDARY_LABEL
    mode_ok = c.get("mode") == RDQ_BOUNDARY_MODE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    human_required = c.get("human_approval_required") is True
    confirmation_required = c.get("requires_independent_confirmation") is True
    future_step_required = (
        c.get("requires_separate_future_human_approved_step") is True
    )
    stage_ok = c.get("stage") == RDQ_BOUNDARY_CURRENT_STAGE
    core_rule_ok = c.get("core_rule") == RDQ_BOUNDARY_CORE_RULE
    outcome_ok = c.get("outcome") in RDQ_BOUNDARY_OUTCOMES
    outcomes_ok = tuple(c.get("outcomes") or ()) == RDQ_BOUNDARY_OUTCOMES
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage")
        == RDQ_BOUNDARY_MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == RDQ_BOUNDARY_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == RDQ_BOUNDARY_SAFETY_POSTURE

    packet = c.get("human_decision_packet")
    packet_ok = (
        isinstance(packet, dict)
        and packet.get("unlocks_real_data_qa") is False
        and packet.get("authorizes_nothing") is True
        and packet.get("human_decision_applied") is False
        and packet.get("requires_separate_future_human_approved_step") is True
        and list(packet.get("human_acknowledgements_required") or [])
        == list(RDQ_BOUNDARY_HUMAN_ACKNOWLEDGEMENTS_REQUIRED)
        and list(packet.get("decision_options") or [])
        == list(RDQ_BOUNDARY_DECISION_OPTIONS)
    )

    # the contract must never directly unlock real data QA
    real_data_qa_stays_blocked = (
        c.get("unlocks_real_data_qa") is False
        and c.get("real_data_qa_blocked") is True
    )

    # generated guidance must carry no execution / trade verbs as whole words
    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in (
            "operator_next_step",
            "operator_notes",
            "core_rule",
        )
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(RDQ_BOUNDARY_FORBIDDEN_TRADE_TERMS))

    sections_ok = isinstance(c.get("operator_next_step"), str) and bool(
        c.get("operator_next_step")
    )

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "mode_ok": mode_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "human_required": human_required,
        "confirmation_required": confirmation_required,
        "future_step_required": future_step_required,
        "stage_ok": stage_ok,
        "core_rule_ok": core_rule_ok,
        "outcome_ok": outcome_ok,
        "outcomes_ok": outcomes_ok,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "packet_ok": packet_ok,
        "real_data_qa_stays_blocked": real_data_qa_stays_blocked,
        "no_trade_language": no_trade_language,
        "sections_ok": sections_ok,
    }
    verdict = dict(checks)
    verdict["missing_fields"] = missing
    verdict["valid"] = (not missing) and all(checks.values())
    return verdict


def _tokenize(text: str) -> list[str]:
    token = []
    out: list[str] = []
    for ch in str(text).lower():
        if ch.isalnum() or ch == "_":
            token.append(ch)
        else:
            if token:
                out.append("".join(token))
                token = []
    if token:
        out.append("".join(token))
    return out


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def _emit(lines: list[str], heading: str, rows: list[str]) -> None:
    lines.append("")
    lines.append("## " + heading)
    if not rows:
        lines.append("- (none)")
        return
    for row in rows:
        lines.append("- " + row)


def render_crypto_d1_real_data_qa_boundary_decision_contract_markdown(
    contract: Any,
) -> str:
    """Render a built contract as a deterministic markdown brief. Pure string
    formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    q = c.get("evidence_quality") or {}
    gate = c.get("upstream_gate") or {}
    lines: list[str] = []
    lines.append(
        "# Crypto-D1 Human-Controlled Real Data QA Boundary Decision Contract"
    )
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Outcome: " + str(c.get("outcome", "")))
    lines.append(
        "- Mission flow stage: " + str(c.get("mission_flow_current_stage", ""))
    )
    lines.append(
        "- Mission flow next action: "
        + str(c.get("mission_flow_next_required_action", ""))
    )
    lines.append(
        "- Records: "
        + str(q.get("record_count", 0))
        + " (booked "
        + str(q.get("booked_count", 0))
        + ", open "
        + str(q.get("open_count", 0))
        + ", external "
        + str(q.get("external_record_count", 0))
        + ")"
    )
    lines.append(
        "- Unlocks real_data_qa: " + str(c.get("unlocks_real_data_qa", False))
    )
    lines.append(
        "- real_data_qa_blocked: " + str(c.get("real_data_qa_blocked", True))
    )
    lines.append(
        "- baseline_backtest_blocked: "
        + str(c.get("baseline_backtest_blocked", True))
    )
    lines.append(
        "- paper_trading_gate_locked: "
        + str(c.get("paper_trading_gate_locked", True))
    )
    lines.append(
        "- micro_live_gate_locked: "
        + str(c.get("micro_live_gate_locked", True))
    )

    _emit(
        lines,
        "Upstream Evidence Gate",
        [
            "Block 131 scoring: "
            + str(gate.get("evidence_scoring_outcome"))
            + " (required "
            + str(gate.get("evidence_scoring_required"))
            + ", met "
            + str(gate.get("evidence_scoring_met"))
            + ")",
            "Block 132 cohort: "
            + str(gate.get("cohort_independence_label"))
            + " (required "
            + str(gate.get("cohort_independence_required"))
            + ", met "
            + str(gate.get("cohort_independence_met"))
            + ")",
            "Daily Alpha Brief: "
            + str(gate.get("daily_alpha_brief_verdict"))
            + " (required "
            + str(gate.get("daily_alpha_brief_required"))
            + ", met "
            + str(gate.get("daily_alpha_brief_met"))
            + ")",
            "Independent booked cohorts: "
            + str(gate.get("independent_booked_cohort_count"))
            + " (min "
            + str(gate.get("min_independent_booked_cohorts"))
            + ", met "
            + str(gate.get("independent_booked_cohorts_met"))
            + ")",
        ],
    )
    _emit(lines, "Block Reasons", list(c.get("block_reasons") or []))
    _emit(lines, "Await Reasons", list(c.get("await_reasons") or []))
    _emit(
        lines,
        "Human Acknowledgements Required",
        list(c.get("human_acknowledgements_required") or []),
    )
    _emit(
        lines,
        "Decision Options",
        list(c.get("decision_options") or []),
    )
    _emit(
        lines,
        "Observation-Only Evidence Lanes",
        list(c.get("observation_only_evidence_lanes") or []),
    )
    _emit(
        lines,
        "No Execution Authorization",
        [
            "authorizes_nothing: " + str(c.get("authorizes_nothing", True)),
            "unlocks_real_data_qa: "
            + str(c.get("unlocks_real_data_qa", False)),
            "requires_separate_future_human_approved_step: "
            + str(
                c.get("requires_separate_future_human_approved_step", True)
            ),
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)

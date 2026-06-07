"""Crypto-D1 Real Data QA Readiness Checklist Contract (Block 136, Phase B).

A PURE, stdlib-only, *read-only* paper contract. It defines -- on paper only --
the READINESS CHECKLIST that must all pass BEFORE a human is even asked to approve
Real Data QA. It is the gate that sits just behind the Human Approval Packet
(Phase A): the packet is the document; this checklist confirms the surrounding
evidence and posture are sound enough to bother a human reviewer.

    CURRENT_STAGE        = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    NEXT_REQUIRED_ACTION = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

It executes NOTHING. It does not fetch, acquire, load, inspect, transform, or
compute on any data, runs no QA, no baseline, no backtest, no simulation, touches
no broker / exchange / order / trading / paper / live surface, triggers no
automation, writes no file, reads no file, opens no network, spawns no
subprocess, reads no environment, uses no credential, mints no id, and records no
timestamp. It only reasons over a static, caller-supplied summary.

CORE RULE: this contract NEVER unlocks Real Data QA. A READY result only means
"the checklist passed; this is ready for a SEPARATE human approval review". It
authorizes nothing. real_data_qa stays BLOCKED, baseline stays BLOCKED, and the
paper / micro-live gates stay LOCKED here, always.

READY is returned ONLY when every checklist item passes:
  1. approval_packet_complete         - the Phase A human approval packet is COMPLETE
  2. evidence_not_external_only        - evidence is not external-research-only
  3. evidence_not_open_unrealized_only - evidence is not open / unrealized only
  4. evidence_not_correlated_only      - evidence is not a single correlated cluster
  5. evidence_not_duplicate_only       - evidence is not duplicate-only
  6. sample_sufficient                 - the booked sample is not insufficient
  7. all_forbidden_flags_false         - no authorization / unlock / promotion flag
  8. mission_flow_boundary_aligned     - mission flow is still at the QA boundary

Outcomes (exactly one, by precedence BLOCK > NOT_READY > READY):
  - BLOCK     : a forbidden authorization / unlock / promotion / order flag was
                set, or the mission flow is no longer at the boundary. These are
                safety failures, not mere "not ready yet" states.
  - NOT_READY : one or more evidence / packet checklist items did not pass.
  - READY     : every checklist item passed. It still authorizes and unlocks
                nothing -- it only means ready for a separate human approval review.

Public API:
  - RDQ_READINESS_SCHEMA_VERSION / RDQ_READINESS_LABEL / RDQ_READINESS_STATUS
  - RDQ_READINESS_MODE / RDQ_READINESS_CORE_RULE
  - RDQ_READINESS_NEXT_REQUIRED_ACTION / RDQ_READINESS_CURRENT_STAGE
  - RDQ_READINESS_MISSION_FLOW_CURRENT_STAGE
  - RDQ_READINESS_MISSION_FLOW_NEXT_REQUIRED_ACTION
  - RDQ_READINESS_MIN_BOOKED_RECORDS
  - RDQ_READINESS_CHECKLIST_ITEMS
  - OUTCOME_BLOCK / OUTCOME_NOT_READY / OUTCOME_READY / RDQ_READINESS_OUTCOMES
  - RDQ_READINESS_AUTHORIZATION_FLAGS / RDQ_READINESS_GATE_LOCK_FLAGS
  - RDQ_READINESS_GATE_UNLOCK_REQUEST_FLAGS
  - RDQ_READINESS_FORBIDDEN_PROMOTION_REQUEST_FLAGS
  - RDQ_READINESS_EXECUTABLE_SIGNAL_FIELDS / RDQ_READINESS_FORBIDDEN_TRADE_TERMS
  - RDQ_READINESS_TRADE_SOURCE_TAGS / RDQ_READINESS_EXTERNAL_RESEARCH_SOURCE_TAGS
  - RDQ_READINESS_BOOKED_STATUS_TAGS / RDQ_READINESS_OPEN_STATUS_TAGS
  - RDQ_READINESS_SAFETY_POSTURE
  - DEFAULT_SAMPLE_READINESS_INPUT
  - assess_real_data_qa_readiness(payload)
  - build_crypto_d1_real_data_qa_readiness_checklist_contract(payload=None)
  - validate_crypto_d1_real_data_qa_readiness_checklist_contract(contract)
  - render_crypto_d1_real_data_qa_readiness_checklist_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

RDQ_READINESS_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_real_data_qa_readiness_checklist_contract.v1"
)
RDQ_READINESS_LABEL = (
    "Block 136 - Crypto-D1 Real Data QA Readiness Checklist Contract"
)
RDQ_READINESS_STATUS = (
    "READ_ONLY_CRYPTO_D1_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT"
)
RDQ_READINESS_MODE = "RESEARCH_ONLY"

RDQ_READINESS_CORE_RULE = (
    "This contract NEVER unlocks Real Data QA. It only confirms a readiness "
    "checklist. Even a READY result authorizes nothing: it means only that the "
    "checklist passed and this is ready for a separate human approval review. "
    "real_data_qa stays BLOCKED, baseline stays BLOCKED, and the paper / "
    "micro-live gates stay LOCKED here, always."
)

# The action that BUILDING this contract satisfies, and the stage it occupies.
RDQ_READINESS_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT"
)
RDQ_READINESS_CURRENT_STAGE = (
    "CRYPTO_D1_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT_REQUIRED"
)

# The current mission-flow truth this contract is anchored to. The companion test
# cross-checks these against the live status module so they cannot silently drift.
RDQ_READINESS_MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
RDQ_READINESS_MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# Minimum number of BOOKED (closed / realized) trade records before the sample is
# considered sufficient. Matches the Block 132 / 134 promote-support threshold.
RDQ_READINESS_MIN_BOOKED_RECORDS = 3

# The eight checklist items (id, human label), in display order. READY requires
# all of them to pass.
RDQ_READINESS_CHECKLIST_ITEMS: tuple[tuple[str, str], ...] = (
    ("approval_packet_complete", "Phase A human approval packet is COMPLETE"),
    ("evidence_not_external_only", "Evidence is not external-research-only"),
    ("evidence_not_open_unrealized_only", "Evidence is not open / unrealized only"),
    ("evidence_not_correlated_only", "Evidence is not a single correlated cluster"),
    ("evidence_not_duplicate_only", "Evidence is not duplicate-only"),
    ("sample_sufficient", "The booked sample is not insufficient"),
    ("all_forbidden_flags_false", "No authorization / unlock / promotion flag set"),
    ("mission_flow_boundary_aligned", "Mission flow is still at the QA boundary"),
)
RDQ_READINESS_CHECKLIST_ITEM_IDS: tuple[str, ...] = tuple(
    item_id for item_id, _label in RDQ_READINESS_CHECKLIST_ITEMS
)

# Readiness outcomes (exactly one assigned), in precedence order.
OUTCOME_BLOCK = "BLOCK"
OUTCOME_NOT_READY = "NOT_READY"
OUTCOME_READY = "READY"

RDQ_READINESS_OUTCOMES: tuple[str, ...] = (
    OUTCOME_BLOCK,
    OUTCOME_NOT_READY,
    OUTCOME_READY,
)

# Top-level (or per-record) authorization flags that, if truthy, force a block.
RDQ_READINESS_AUTHORIZATION_FLAGS: tuple[str, ...] = (
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
RDQ_READINESS_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, force a block.
RDQ_READINESS_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
)

# Requests asking the checklist to mean execution / live promotion. Any truthy
# value forces a block: this contract can only confirm a checklist.
RDQ_READINESS_FORBIDDEN_PROMOTION_REQUEST_FLAGS: tuple[str, ...] = (
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
RDQ_READINESS_EXECUTABLE_SIGNAL_FIELDS: tuple[str, ...] = (
    "order",
    "signal",
    "trade_instruction",
    "execution",
    "live_order",
    "place_order",
)

# Execution / promotion verbs the contract's generated guidance must never
# contain as whole words.
RDQ_READINESS_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
    "order",
)

# Source tags treated as first-party trade evidence (booked or open). An empty /
# missing source defaults to trade evidence.
RDQ_READINESS_TRADE_SOURCE_TAGS: tuple[str, ...] = (
    "trade",
    "booked_trade",
    "closed_trade",
    "open_trade",
    "position",
)

# Source tags treated as external research context. These NEVER count as booked
# trade evidence.
RDQ_READINESS_EXTERNAL_RESEARCH_SOURCE_TAGS: tuple[str, ...] = (
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
RDQ_READINESS_BOOKED_STATUS_TAGS: tuple[str, ...] = (
    "closed",
    "booked",
    "realized",
    "settled",
)

# Record statuses treated as OPEN (unrealized) -> observation only.
RDQ_READINESS_OPEN_STATUS_TAGS: tuple[str, ...] = (
    "open",
    "unrealized",
    "live",
    "running",
    "floating",
)

# Read-only safety posture. The three True flags are *posture* facts; every
# capability / authorization / unlock flag is False.
RDQ_READINESS_SAFETY_POSTURE: dict[str, bool] = {
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

_TRADE_SOURCE_SET: frozenset[str] = frozenset(RDQ_READINESS_TRADE_SOURCE_TAGS)
_EXTERNAL_SOURCE_SET: frozenset[str] = frozenset(
    RDQ_READINESS_EXTERNAL_RESEARCH_SOURCE_TAGS
)
_BOOKED_STATUS_SET: frozenset[str] = frozenset(RDQ_READINESS_BOOKED_STATUS_TAGS)
_OPEN_STATUS_SET: frozenset[str] = frozenset(RDQ_READINESS_OPEN_STATUS_TAGS)


# A deterministic, illustrative paper sample. The approval packet is marked NOT
# complete and the evidence is a single correlated, duplicated ETH cluster, so the
# default checklist is NOT_READY. Nothing here is real data; static example only.
DEFAULT_SAMPLE_READINESS_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 real data QA readiness input (static sample)",
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
    "approval_packet_complete": False,
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
    ],
}


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _norm(value: Any) -> str:
    return str(value).strip().lower() if value is not None else ""


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


def _tokenize(text: str) -> list[str]:
    token: list[str] = []
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


def _source_kind(record: dict[str, Any]) -> str:
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
        for flag in RDQ_READINESS_AUTHORIZATION_FLAGS:
            if _is_truthy(scope.get(flag)):
                hits.append(flag)
        for flag in RDQ_READINESS_GATE_UNLOCK_REQUEST_FLAGS:
            if _is_truthy(scope.get(flag)):
                hits.append(flag)
        for flag in RDQ_READINESS_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
            if _is_truthy(scope.get(flag)):
                hits.append(flag)
        for field in RDQ_READINESS_EXECUTABLE_SIGNAL_FIELDS:
            value = scope.get(field)
            if value not in (None, "", [], {}, 0, False):
                hits.append(field)
        for flag in RDQ_READINESS_GATE_LOCK_FLAGS:
            if flag in scope and not _is_truthy(scope.get(flag)):
                hits.append("unlocked:" + flag)
    seen: set[str] = set()
    ordered: list[str] = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            ordered.append(h)
    return ordered


def _evidence_quality(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Re-derive the Block 131 / 132 / 134 style evidence-quality signals from a
    static record set. No grouping is executed against real data; this only reads
    the caller-supplied summary records."""
    trade_records = [r for r in records if _source_kind(r) == "trade"]
    external_records = [r for r in records if _source_kind(r) == "external"]
    booked_trades = [r for r in trade_records if _status_kind(r) == "booked"]
    open_trades = [r for r in trade_records if _status_kind(r) == "open"]

    sym_dir_counts: dict[tuple[str, str], int] = {}
    for r in booked_trades:
        key = (_norm(r.get("symbol")), _norm(r.get("direction")))
        sym_dir_counts[key] = sym_dir_counts.get(key, 0) + 1
    duplicate = any(c > 1 for c in sym_dir_counts.values())

    macro_counts: dict[str, int] = {}
    for r in booked_trades:
        macro = _norm(r.get("macro_event"))
        if macro:
            macro_counts[macro] = macro_counts.get(macro, 0) + 1
    # correlated-only: there is booked evidence and every booked trade collapses
    # into a single shared macro event (no independent second cluster).
    correlated = (
        len(booked_trades) > 1
        and len(macro_counts) == 1
        and sum(macro_counts.values()) == len(booked_trades)
    )

    no_evidence = len(records) == 0
    external_evidence_only = (
        len(records) > 0 and len(trade_records) == 0 and len(external_records) > 0
    )
    open_unrealized_only = (
        len(trade_records) > 0 and len(booked_trades) == 0 and len(open_trades) > 0
    )
    insufficient_sample = len(booked_trades) < RDQ_READINESS_MIN_BOOKED_RECORDS

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
        "insufficient_sample": insufficient_sample,
    }


# --------------------------------------------------------------------------- #
# assessment
# --------------------------------------------------------------------------- #
def assess_real_data_qa_readiness(payload: Any) -> dict[str, Any]:
    """Assess (read-only) the Real Data QA readiness checklist. Returns a fresh
    dict every call. Authorizes nothing and unlocks nothing under any outcome --
    a READY result only means ready for a separate human approval review."""
    data = _as_payload(payload)
    records = _as_records(data)
    quality = _evidence_quality(records)

    mf_stage = data.get(
        "mission_flow_current_stage", RDQ_READINESS_MISSION_FLOW_CURRENT_STAGE
    )
    mf_action = data.get(
        "mission_flow_next_required_action",
        RDQ_READINESS_MISSION_FLOW_NEXT_REQUIRED_ACTION,
    )
    mission_flow_aligned = (
        str(mf_stage) == RDQ_READINESS_MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == RDQ_READINESS_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_hits = _forbidden_flag_hits(data)
    approval_packet_complete = _is_truthy(data.get("approval_packet_complete"))

    item_results: dict[str, bool] = {
        "approval_packet_complete": approval_packet_complete,
        "evidence_not_external_only": not quality["external_evidence_only"],
        "evidence_not_open_unrealized_only": not quality["open_unrealized_only"],
        "evidence_not_correlated_only": not quality["correlated"],
        "evidence_not_duplicate_only": not quality["duplicate"],
        "sample_sufficient": not quality["insufficient_sample"],
        "all_forbidden_flags_false": len(forbidden_hits) == 0,
        "mission_flow_boundary_aligned": mission_flow_aligned,
    }

    # Per-item human reason strings.
    _reasons = {
        "approval_packet_complete": (
            "approval packet is COMPLETE"
            if approval_packet_complete
            else "approval packet is NOT complete"
        ),
        "evidence_not_external_only": (
            "evidence includes first-party trade records"
            if item_results["evidence_not_external_only"]
            else "evidence is external-research-only"
        ),
        "evidence_not_open_unrealized_only": (
            "evidence includes booked trades"
            if item_results["evidence_not_open_unrealized_only"]
            else "evidence is open / unrealized only"
        ),
        "evidence_not_correlated_only": (
            "evidence is not a single correlated cluster"
            if item_results["evidence_not_correlated_only"]
            else "evidence is a single correlated cluster"
        ),
        "evidence_not_duplicate_only": (
            "evidence is not duplicate-only"
            if item_results["evidence_not_duplicate_only"]
            else "evidence is duplicate-only"
        ),
        "sample_sufficient": (
            "booked sample meets the minimum of "
            + str(RDQ_READINESS_MIN_BOOKED_RECORDS)
            if item_results["sample_sufficient"]
            else "booked sample "
            + str(quality["booked_count"])
            + " is below the minimum "
            + str(RDQ_READINESS_MIN_BOOKED_RECORDS)
        ),
        "all_forbidden_flags_false": (
            "no authorization / unlock / promotion flag set"
            if item_results["all_forbidden_flags_false"]
            else "forbidden flags present: " + ", ".join(forbidden_hits)
        ),
        "mission_flow_boundary_aligned": (
            "mission flow is at the QA boundary"
            if mission_flow_aligned
            else "mission flow is NOT at the QA boundary"
        ),
    }

    checklist = [
        {
            "id": item_id,
            "label": label,
            "passed": item_results[item_id],
            "reason": _reasons[item_id],
        }
        for item_id, label in RDQ_READINESS_CHECKLIST_ITEMS
    ]

    failed_items = [c["id"] for c in checklist if not c["passed"]]

    # Safety failures BLOCK; everything else is merely NOT_READY.
    safety_failed = (not item_results["all_forbidden_flags_false"]) or (
        not item_results["mission_flow_boundary_aligned"]
    )

    if safety_failed:
        outcome = OUTCOME_BLOCK
    elif failed_items:
        outcome = OUTCOME_NOT_READY
    else:
        outcome = OUTCOME_READY

    return {
        "mode": RDQ_READINESS_MODE,
        "outcome": outcome,
        "mission_flow_current_stage": str(mf_stage),
        "mission_flow_next_required_action": str(mf_action),
        "mission_flow_aligned": mission_flow_aligned,
        "approval_packet_complete": approval_packet_complete,
        "evidence_quality": quality,
        "checklist": checklist,
        "checklist_item_ids": list(RDQ_READINESS_CHECKLIST_ITEM_IDS),
        "passed_item_ids": [c["id"] for c in checklist if c["passed"]],
        "failed_item_ids": list(failed_items),
        "forbidden_flag_hits": list(forbidden_hits),
        "ready": outcome == OUTCOME_READY,
        "ready_for_human_approval_review": outcome == OUTCOME_READY,
        "assesses_research_only": True,
        "unlocks_real_data_qa": False,
        "promotes_beyond_boundary": False,
        "authorizes_nothing": True,
    }


# --------------------------------------------------------------------------- #
# contract build
# --------------------------------------------------------------------------- #
def _operator_next_step(assessment: dict[str, Any]) -> str:
    outcome = assessment["outcome"]
    if outcome == OUTCOME_BLOCK:
        return (
            "Reject the readiness check. A forbidden authorization / unlock / "
            "promotion flag was set, or the mission flow has left the boundary. "
            "Resolve the safety failure in research only; do not acquire data, "
            "run QA, baseline, or any real-money activity."
        )
    if outcome == OUTCOME_NOT_READY:
        return (
            "Not ready. Resolve the failing checklist items -- complete the "
            "approval packet and strengthen the evidence -- before asking a human "
            "to review. Nothing is acquired, inspected, or run; real_data_qa "
            "remains BLOCKED."
        )
    return (
        "Ready for a SEPARATE human approval review. Readiness is not approval: a "
        "human reviewer must still decide, and a separate, future, explicitly "
        "human-approved step is required before any Real Data QA planning may "
        "begin. This contract unlocks nothing."
    )


def build_crypto_d1_real_data_qa_readiness_checklist_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only Real Data QA Readiness Checklist
    Contract record. All capability flags are False and all gate locks are True
    regardless of the assessed outcome."""
    data = (
        dict(DEFAULT_SAMPLE_READINESS_INPUT)
        if payload is None
        else _as_payload(payload)
    )
    assessment = assess_real_data_qa_readiness(data)

    contract: dict[str, Any] = {
        "schema_version": RDQ_READINESS_SCHEMA_VERSION,
        "label": RDQ_READINESS_LABEL,
        "status": RDQ_READINESS_STATUS,
        "stage": RDQ_READINESS_CURRENT_STAGE,
        "mode": RDQ_READINESS_MODE,
        "core_rule": RDQ_READINESS_CORE_RULE,
        "readiness_next_required_action": RDQ_READINESS_NEXT_REQUIRED_ACTION,
        "readiness_current_stage": RDQ_READINESS_CURRENT_STAGE,
        "mission_flow_current_stage": (
            RDQ_READINESS_MISSION_FLOW_CURRENT_STAGE
        ),
        "mission_flow_next_required_action": (
            RDQ_READINESS_MISSION_FLOW_NEXT_REQUIRED_ACTION
        ),
        "mission_flow_aligned": assessment["mission_flow_aligned"],
        "outcomes": list(RDQ_READINESS_OUTCOMES),
        "outcome": assessment["outcome"],
        "ready": assessment["ready"],
        "ready_for_human_approval_review": (
            assessment["ready_for_human_approval_review"]
        ),
        "min_booked_records": RDQ_READINESS_MIN_BOOKED_RECORDS,
        "checklist_item_ids": list(RDQ_READINESS_CHECKLIST_ITEM_IDS),
        "checklist": assessment["checklist"],
        "passed_item_ids": list(assessment["passed_item_ids"]),
        "failed_item_ids": list(assessment["failed_item_ids"]),
        "authorization_flags": list(RDQ_READINESS_AUTHORIZATION_FLAGS),
        "gate_lock_flags": list(RDQ_READINESS_GATE_LOCK_FLAGS),
        "gate_unlock_request_flags": list(
            RDQ_READINESS_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_promotion_request_flags": list(
            RDQ_READINESS_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ),
        "executable_signal_fields": list(
            RDQ_READINESS_EXECUTABLE_SIGNAL_FIELDS
        ),
        "forbidden_trade_terms": list(RDQ_READINESS_FORBIDDEN_TRADE_TERMS),
        "trade_source_tags": list(RDQ_READINESS_TRADE_SOURCE_TAGS),
        "external_research_source_tags": list(
            RDQ_READINESS_EXTERNAL_RESEARCH_SOURCE_TAGS
        ),
        "booked_status_tags": list(RDQ_READINESS_BOOKED_STATUS_TAGS),
        "open_status_tags": list(RDQ_READINESS_OPEN_STATUS_TAGS),
        "assessment": assessment,
        "evidence_quality": dict(assessment["evidence_quality"]),
        "operator_next_step": _operator_next_step(assessment),
        "operator_notes": (
            "Read-only readiness checklist contract. It confirms the eight "
            "readiness items; it never approves and never decides. Even a READY "
            "result authorizes nothing."
        ),
        "human_operator_required_next_steps": [
            "A human confirms the readiness checklist passed.",
            "A human reviewer separately decides whether to approve.",
            "A separate, future, explicitly human-approved step is required "
            "before any Real Data QA planning may begin.",
        ],
        "safety_posture": dict(RDQ_READINESS_SAFETY_POSTURE),
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
    "checklist",
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


def validate_crypto_d1_real_data_qa_readiness_checklist_contract(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built contract. Returns a verdict dict of boolean
    checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == RDQ_READINESS_SCHEMA_VERSION
    label_ok = c.get("label") == RDQ_READINESS_LABEL
    mode_ok = c.get("mode") == RDQ_READINESS_MODE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    human_required = c.get("human_approval_required") is True
    confirmation_required = c.get("requires_independent_confirmation") is True
    future_step_required = (
        c.get("requires_separate_future_human_approved_step") is True
    )
    stage_ok = c.get("stage") == RDQ_READINESS_CURRENT_STAGE
    core_rule_ok = c.get("core_rule") == RDQ_READINESS_CORE_RULE
    outcome_ok = c.get("outcome") in RDQ_READINESS_OUTCOMES
    outcomes_ok = tuple(c.get("outcomes") or ()) == RDQ_READINESS_OUTCOMES
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage")
        == RDQ_READINESS_MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == RDQ_READINESS_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == RDQ_READINESS_SAFETY_POSTURE

    checklist = c.get("checklist")
    eight_checklist_items = (
        isinstance(checklist, list)
        and len(checklist) == 8
        and [item.get("id") for item in checklist]
        == list(RDQ_READINESS_CHECKLIST_ITEM_IDS)
    )

    # READY may only appear when every checklist item passed.
    ready_value = c.get("ready") is True
    all_items_passed = isinstance(checklist, list) and all(
        bool(item.get("passed")) for item in checklist
    )
    ready_only_when_all_pass = (not ready_value) or all_items_passed

    # the contract must never directly unlock real data QA
    real_data_qa_stays_blocked = (
        c.get("unlocks_real_data_qa") is False
        and c.get("real_data_qa_blocked") is True
    )

    # generated guidance must carry no execution / trade verbs as whole words
    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "operator_notes", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(RDQ_READINESS_FORBIDDEN_TRADE_TERMS))

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
        "eight_checklist_items": eight_checklist_items,
        "ready_only_when_all_pass": ready_only_when_all_pass,
        "real_data_qa_stays_blocked": real_data_qa_stays_blocked,
        "no_trade_language": no_trade_language,
        "sections_ok": sections_ok,
    }
    verdict = dict(checks)
    verdict["missing_fields"] = missing
    verdict["valid"] = (not missing) and all(checks.values())
    return verdict


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


def render_crypto_d1_real_data_qa_readiness_checklist_contract_markdown(
    contract: Any,
) -> str:
    """Render a built contract as a deterministic markdown brief. Pure string
    formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    q = c.get("evidence_quality") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Real Data QA Readiness Checklist Contract")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Outcome: " + str(c.get("outcome", "")))
    lines.append("- Ready: " + str(c.get("ready", False)))
    lines.append(
        "- Mission flow stage: " + str(c.get("mission_flow_current_stage", ""))
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

    _emit(
        lines,
        "Readiness Checklist",
        [
            str(item.get("id"))
            + ": "
            + ("PASS" if item.get("passed") else "FAIL")
            + " - "
            + str(item.get("reason"))
            for item in (c.get("checklist") or [])
        ],
    )
    _emit(lines, "Failed Items", list(c.get("failed_item_ids") or []))
    _emit(
        lines,
        "No Execution Authorization",
        [
            "authorizes_nothing: " + str(c.get("authorizes_nothing", True)),
            "unlocks_real_data_qa: "
            + str(c.get("unlocks_real_data_qa", False)),
            "requires_separate_future_human_approved_step: "
            + str(c.get("requires_separate_future_human_approved_step", True)),
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)

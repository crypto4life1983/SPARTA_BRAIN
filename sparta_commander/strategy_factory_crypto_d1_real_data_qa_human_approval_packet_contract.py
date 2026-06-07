"""Crypto-D1 Real Data QA Human Approval Packet Contract (Block 136, Phase A).

A PURE, stdlib-only, *read-only* paper contract. It defines -- on paper only --
the structured HUMAN APPROVAL PACKET a person must fill in and sign BEFORE any
Real Data QA may even be planned. It is the document a human completes at the
mission-flow boundary:

    CURRENT_STAGE        = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    NEXT_REQUIRED_ACTION = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

It executes NOTHING. It does not fetch, acquire, load, inspect, transform, or
compute on any data, runs no QA, no baseline, no backtest, no simulation, touches
no broker / exchange / order / trading / paper / live surface, triggers no
automation, writes no file, reads no file, opens no network, spawns no
subprocess, reads no environment, uses no credential, mints no id, and records no
timestamp. It only reasons over a static, caller-supplied packet dict.

CORE RULE: this contract NEVER unlocks Real Data QA. A COMPLETE packet only means
"this packet is filled in correctly and is ready for a separate human approval
review"; it authorizes nothing. real_data_qa stays BLOCKED, baseline stays
BLOCKED, and the paper / micro-live gates stay LOCKED here, always.

The packet a human must complete requires EIGHT fields:
  1. dataset_source_scope    - the exact dataset / source scope
  2. symbols_timeframes       - the symbols and timeframes
  3. date_range               - the date range (start + end)
  4. allowed_qa_checks        - the allowed QA checks (subset of the whitelist)
  5. forbidden_actions        - the forbidden actions (must cover the mandatory set)
  6. qa_only_proof            - explicit proof this is QA only, not backtest/live
  7. rollback_stop_condition  - the rollback / stop condition
  8. human_approval_phrase    - the exact explicit human approval phrase

Outcomes (exactly one, by precedence BLOCK > INCOMPLETE > COMPLETE):
  - BLOCK      : packet requested an authorization / unlock / promotion / order,
                 or the mission flow is not at the boundary, or a QA check or the
                 packet body smuggled a trade/backtest/live term.
  - INCOMPLETE : one or more required fields are missing/empty/invalid, the
                 forbidden-action set is not fully covered, or the approval phrase
                 does not match exactly.
  - COMPLETE   : all eight fields valid and the exact approval phrase present. It
                 still authorizes nothing and unlocks nothing.

Public API:
  - RDQ_APPROVAL_SCHEMA_VERSION / RDQ_APPROVAL_LABEL / RDQ_APPROVAL_STATUS
  - RDQ_APPROVAL_MODE / RDQ_APPROVAL_CORE_RULE
  - RDQ_APPROVAL_NEXT_REQUIRED_ACTION / RDQ_APPROVAL_CURRENT_STAGE
  - RDQ_APPROVAL_MISSION_FLOW_CURRENT_STAGE
  - RDQ_APPROVAL_MISSION_FLOW_NEXT_REQUIRED_ACTION
  - RDQ_APPROVAL_REQUIRED_FIELDS
  - RDQ_APPROVAL_REQUIRED_PHRASE
  - RDQ_APPROVAL_MANDATORY_FORBIDDEN_ACTIONS
  - RDQ_APPROVAL_ALLOWED_QA_CHECK_WHITELIST
  - OUTCOME_BLOCK / OUTCOME_INCOMPLETE / OUTCOME_COMPLETE / RDQ_APPROVAL_OUTCOMES
  - RDQ_APPROVAL_AUTHORIZATION_FLAGS / RDQ_APPROVAL_GATE_LOCK_FLAGS
  - RDQ_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS
  - RDQ_APPROVAL_FORBIDDEN_PROMOTION_REQUEST_FLAGS
  - RDQ_APPROVAL_EXECUTABLE_SIGNAL_FIELDS / RDQ_APPROVAL_FORBIDDEN_TRADE_TERMS
  - RDQ_APPROVAL_SAFETY_POSTURE
  - DEFAULT_SAMPLE_APPROVAL_PACKET
  - assess_real_data_qa_human_approval_packet(payload)
  - build_crypto_d1_real_data_qa_human_approval_packet_contract(payload=None)
  - validate_crypto_d1_real_data_qa_human_approval_packet_contract(contract)
  - render_crypto_d1_real_data_qa_human_approval_packet_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

RDQ_APPROVAL_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract.v1"
)
RDQ_APPROVAL_LABEL = (
    "Block 136 - Crypto-D1 Real Data QA Human Approval Packet Contract"
)
RDQ_APPROVAL_STATUS = (
    "READ_ONLY_CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT"
)
RDQ_APPROVAL_MODE = "RESEARCH_ONLY"

RDQ_APPROVAL_CORE_RULE = (
    "This contract NEVER unlocks Real Data QA. It only defines the human approval "
    "packet a person must complete and sign at the boundary. Even a COMPLETE "
    "packet authorizes nothing: it means only that the packet is filled in "
    "correctly and is ready for a separate human approval review. real_data_qa "
    "stays BLOCKED, baseline stays BLOCKED, and the paper / micro-live gates stay "
    "LOCKED here, always."
)

# The action that BUILDING this contract satisfies, and the stage it occupies.
RDQ_APPROVAL_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT"
)
RDQ_APPROVAL_CURRENT_STAGE = (
    "CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT_REQUIRED"
)

# The current mission-flow truth this contract is anchored to. The companion test
# cross-checks these against the live status module so they cannot silently drift.
RDQ_APPROVAL_MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
RDQ_APPROVAL_MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# The eight required packet fields, with a short human description for each.
RDQ_APPROVAL_REQUIRED_FIELDS: tuple[tuple[str, str], ...] = (
    ("dataset_source_scope", "the exact dataset / source scope"),
    ("symbols_timeframes", "the symbols and timeframes"),
    ("date_range", "the date range (start and end)"),
    ("allowed_qa_checks", "the allowed QA checks (subset of the whitelist)"),
    ("forbidden_actions", "the forbidden actions (must cover the mandatory set)"),
    ("qa_only_proof", "explicit proof this is QA only, not backtest/live trading"),
    ("rollback_stop_condition", "the rollback / stop condition"),
    ("human_approval_phrase", "the exact explicit human approval phrase"),
)
RDQ_APPROVAL_REQUIRED_FIELD_KEYS: tuple[str, ...] = tuple(
    key for key, _desc in RDQ_APPROVAL_REQUIRED_FIELDS
)

# The exact phrase a human must type (case-insensitive, trimmed) to sign.
RDQ_APPROVAL_REQUIRED_PHRASE = (
    "I APPROVE REAL DATA QA PLANNING ONLY - NO BACKTEST, NO PAPER, NO LIVE"
)

# Actions the packet's forbidden_actions list MUST cover. A packet missing any of
# these is INCOMPLETE: the human must explicitly forbid every execution lane.
RDQ_APPROVAL_MANDATORY_FORBIDDEN_ACTIONS: tuple[str, ...] = (
    "backtest",
    "baseline",
    "paper_trading",
    "live_trading",
    "order_placement",
    "broker_exchange",
    "automation",
)

# The only QA checks a packet may allow. Each entry of allowed_qa_checks must be
# one of these read-only data-quality inspections (no execution, no backtest).
RDQ_APPROVAL_ALLOWED_QA_CHECK_WHITELIST: tuple[str, ...] = (
    "schema_validation",
    "null_check",
    "duplicate_row_check",
    "timestamp_monotonicity",
    "gap_detection",
    "range_sanity",
    "row_count",
    "symbol_coverage",
)

# Packet-completeness outcomes (exactly one assigned), in precedence order.
OUTCOME_BLOCK = "BLOCK"
OUTCOME_INCOMPLETE = "INCOMPLETE"
OUTCOME_COMPLETE = "COMPLETE"

RDQ_APPROVAL_OUTCOMES: tuple[str, ...] = (
    OUTCOME_BLOCK,
    OUTCOME_INCOMPLETE,
    OUTCOME_COMPLETE,
)

# Top-level (or per-field) authorization flags that, if truthy, force a block.
RDQ_APPROVAL_AUTHORIZATION_FLAGS: tuple[str, ...] = (
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
# the packet tried to unlock a gate -> block.
RDQ_APPROVAL_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, force a block.
RDQ_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
)

# Requests asking the packet to mean execution / live promotion. Any truthy value
# forces a block: this contract can only define and check a human packet.
RDQ_APPROVAL_FORBIDDEN_PROMOTION_REQUEST_FLAGS: tuple[str, ...] = (
    "force_promote",
    "promote_to_live",
    "promote_to_paper",
    "approve_trade",
    "authorize_trade",
    "execute",
    "place_order",
    "go_live",
)

# Fields whose presence (non-empty) on the packet signals an executable order /
# signal instruction rather than a planning document -> block.
RDQ_APPROVAL_EXECUTABLE_SIGNAL_FIELDS: tuple[str, ...] = (
    "order",
    "signal",
    "trade_instruction",
    "execution",
    "live_order",
    "place_order",
)

# Execution / promotion verbs the contract's generated guidance must never
# contain as whole words.
RDQ_APPROVAL_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
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
RDQ_APPROVAL_SAFETY_POSTURE: dict[str, bool] = {
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

_MANDATORY_FORBIDDEN_SET: frozenset[str] = frozenset(
    RDQ_APPROVAL_MANDATORY_FORBIDDEN_ACTIONS
)
_ALLOWED_QA_CHECK_SET: frozenset[str] = frozenset(
    RDQ_APPROVAL_ALLOWED_QA_CHECK_WHITELIST
)


# A deterministic, illustrative paper sample. Seven of the eight fields are filled
# in correctly, but the human_approval_phrase is intentionally blank, so the
# default packet is INCOMPLETE: it is NOT yet ready for approval review. Nothing
# here is real data or a real approval; static example only.
DEFAULT_SAMPLE_APPROVAL_PACKET: dict[str, Any] = {
    "label": "Crypto-D1 real data QA human approval packet (static sample)",
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
    "dataset_source_scope": (
        "Local CSV export of BTC/ETH/SOL daily candles already on disk; no new "
        "acquisition, no API, no exchange pull."
    ),
    "symbols_timeframes": "BTC, ETH, SOL @ 1d",
    "date_range": "2019-01-01 .. 2025-12-31",
    "allowed_qa_checks": [
        "schema_validation",
        "null_check",
        "duplicate_row_check",
        "timestamp_monotonicity",
        "gap_detection",
        "range_sanity",
        "row_count",
    ],
    "forbidden_actions": list(RDQ_APPROVAL_MANDATORY_FORBIDDEN_ACTIONS),
    "qa_only_proof": (
        "This packet describes read-only data-quality inspection of static files "
        "only. It computes no strategy returns, simulates no fills, places no "
        "trades, and never advances into baseline, backtest, paper, or live."
    ),
    "rollback_stop_condition": (
        "Stop immediately and discard QA outputs if any check would require "
        "fetching new data, computing returns, or touching a broker; QA writes "
        "nothing back into the dataset."
    ),
    "human_approval_phrase": "",
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


def _is_filled(value: Any) -> bool:
    """A field counts as filled when it is a non-empty string or a non-empty
    list/tuple of non-empty strings."""
    if isinstance(value, str):
        return value.strip() != ""
    if isinstance(value, (list, tuple)):
        return len(value) > 0 and all(_norm(v) != "" for v in value)
    return False


def _string_list(value: Any) -> list[str]:
    if isinstance(value, (list, tuple)):
        return [_norm(v) for v in value if _norm(v) != ""]
    if isinstance(value, str) and value.strip():
        return [_norm(value)]
    return []


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


def _forbidden_flag_hits(payload: dict[str, Any]) -> list[str]:
    """Collect any packet keys that attempt to authorize, unlock, promote, or
    carry an executable instruction."""
    hits: list[str] = []
    for flag in RDQ_APPROVAL_AUTHORIZATION_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in RDQ_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in RDQ_APPROVAL_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for field in RDQ_APPROVAL_EXECUTABLE_SIGNAL_FIELDS:
        value = payload.get(field)
        if value not in (None, "", [], {}, 0, False):
            hits.append(field)
    for flag in RDQ_APPROVAL_GATE_LOCK_FLAGS:
        if flag in payload and not _is_truthy(payload.get(flag)):
            hits.append("unlocked:" + flag)
    seen: set[str] = set()
    ordered: list[str] = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            ordered.append(h)
    return ordered


# --------------------------------------------------------------------------- #
# assessment
# --------------------------------------------------------------------------- #
def assess_real_data_qa_human_approval_packet(payload: Any) -> dict[str, Any]:
    """Assess (read-only) whether a human approval packet is complete. Returns a
    fresh dict every call. Authorizes nothing and unlocks nothing under any
    outcome -- a COMPLETE packet is only ready for a separate human review."""
    data = _as_payload(payload)

    mf_stage = data.get(
        "mission_flow_current_stage", RDQ_APPROVAL_MISSION_FLOW_CURRENT_STAGE
    )
    mf_action = data.get(
        "mission_flow_next_required_action",
        RDQ_APPROVAL_MISSION_FLOW_NEXT_REQUIRED_ACTION,
    )
    mission_flow_aligned = (
        str(mf_stage) == RDQ_APPROVAL_MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == RDQ_APPROVAL_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_hits = _forbidden_flag_hits(data)

    # Per-field completeness.
    field_status: dict[str, bool] = {}
    missing_fields: list[str] = []
    for key in RDQ_APPROVAL_REQUIRED_FIELD_KEYS:
        filled = _is_filled(data.get(key))
        field_status[key] = filled
        if not filled:
            missing_fields.append(key)

    # allowed_qa_checks must be a non-empty subset of the whitelist.
    qa_checks = _string_list(data.get("allowed_qa_checks"))
    qa_checks_outside_whitelist = [c for c in qa_checks if c not in _ALLOWED_QA_CHECK_SET]
    qa_checks_ok = len(qa_checks) > 0 and len(qa_checks_outside_whitelist) == 0

    # forbidden_actions must cover the mandatory set.
    forbidden_actions = set(_string_list(data.get("forbidden_actions")))
    missing_forbidden_actions = sorted(
        _MANDATORY_FORBIDDEN_SET - forbidden_actions
    )
    forbidden_actions_ok = len(missing_forbidden_actions) == 0

    # the approval phrase must match exactly (trimmed, case-insensitive).
    phrase_ok = _norm(data.get("human_approval_phrase")) == _norm(
        RDQ_APPROVAL_REQUIRED_PHRASE
    )

    # any allowed_qa_check that smuggles a trade/backtest/live verb is a hard
    # block: the structured QA-check list must contain read-only checks only.
    # (qa_only_proof is free-form prose that must be allowed to NEGATE these
    # terms, e.g. "no backtest", so it is never scanned for forbidden words.)
    smuggled_terms: list[str] = []
    smuggle_tokens = set(_tokenize(" ".join(qa_checks)))
    for term in ("backtest", "baseline", "paper", "live", "order", "buy", "sell"):
        if term in smuggle_tokens:
            smuggled_terms.append(term)

    block_reasons: list[str] = []
    incomplete_reasons: list[str] = []

    # --- hard blocks ---
    if forbidden_hits:
        block_reasons.append(
            "packet requested authorization / unlock / promotion / execution: "
            + ", ".join(forbidden_hits)
        )
    if not mission_flow_aligned:
        block_reasons.append(
            "mission flow is not at the human-controlled real data QA boundary; "
            "no approval packet may be accepted"
        )
    if smuggled_terms:
        block_reasons.append(
            "QA scope smuggled an execution / trade term where only read-only "
            "data-quality checks are allowed: " + ", ".join(sorted(set(smuggled_terms)))
        )

    # --- incompletes (only matter if not already blocked) ---
    for key in missing_fields:
        incomplete_reasons.append("required field is missing or empty: " + key)
    if not qa_checks_ok:
        if len(qa_checks) == 0:
            incomplete_reasons.append("allowed_qa_checks is empty")
        else:
            incomplete_reasons.append(
                "allowed_qa_checks contains non-whitelisted checks: "
                + ", ".join(qa_checks_outside_whitelist)
            )
    if not forbidden_actions_ok:
        incomplete_reasons.append(
            "forbidden_actions does not cover the mandatory set; missing: "
            + ", ".join(missing_forbidden_actions)
        )
    if not phrase_ok:
        incomplete_reasons.append(
            "human_approval_phrase does not match the exact required phrase"
        )

    if block_reasons:
        outcome = OUTCOME_BLOCK
    elif incomplete_reasons:
        outcome = OUTCOME_INCOMPLETE
    else:
        outcome = OUTCOME_COMPLETE

    return {
        "mode": RDQ_APPROVAL_MODE,
        "outcome": outcome,
        "mission_flow_current_stage": str(mf_stage),
        "mission_flow_next_required_action": str(mf_action),
        "mission_flow_aligned": mission_flow_aligned,
        "required_field_keys": list(RDQ_APPROVAL_REQUIRED_FIELD_KEYS),
        "field_status": dict(field_status),
        "missing_fields": list(missing_fields),
        "allowed_qa_checks": list(qa_checks),
        "qa_checks_outside_whitelist": list(qa_checks_outside_whitelist),
        "qa_checks_ok": qa_checks_ok,
        "forbidden_actions_ok": forbidden_actions_ok,
        "missing_forbidden_actions": list(missing_forbidden_actions),
        "approval_phrase_ok": phrase_ok,
        "forbidden_flag_hits": list(forbidden_hits),
        "block_reasons": list(block_reasons),
        "incomplete_reasons": list(incomplete_reasons),
        "packet_complete": outcome == OUTCOME_COMPLETE,
        "ready_for_human_approval_review": outcome == OUTCOME_COMPLETE,
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
            "Reject this packet. It requested authorization, tried to unlock a "
            "gate, or smuggled an execution term into the QA scope. Resolve the "
            "listed block reasons in research only; do not acquire data, run QA, "
            "baseline, or any real-money activity."
        )
    if outcome == OUTCOME_INCOMPLETE:
        return (
            "Return the packet to the human to finish. Fill in every required "
            "field, cover the full mandatory forbidden-action set, keep QA checks "
            "inside the whitelist, and type the exact approval phrase. Nothing is "
            "acquired, inspected, or run; real_data_qa remains BLOCKED."
        )
    return (
        "The packet is complete and ready for a SEPARATE human approval review. "
        "Completeness is not approval: a human reviewer must still decide, and a "
        "separate, future, explicitly human-approved step is required before any "
        "Real Data QA planning may begin. This contract unlocks nothing."
    )


def build_crypto_d1_real_data_qa_human_approval_packet_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only Real Data QA Human Approval Packet
    Contract record. All capability flags are False and all gate locks are True
    regardless of the assessed outcome."""
    data = (
        dict(DEFAULT_SAMPLE_APPROVAL_PACKET)
        if payload is None
        else _as_payload(payload)
    )
    assessment = assess_real_data_qa_human_approval_packet(data)

    contract: dict[str, Any] = {
        "schema_version": RDQ_APPROVAL_SCHEMA_VERSION,
        "label": RDQ_APPROVAL_LABEL,
        "status": RDQ_APPROVAL_STATUS,
        "stage": RDQ_APPROVAL_CURRENT_STAGE,
        "mode": RDQ_APPROVAL_MODE,
        "core_rule": RDQ_APPROVAL_CORE_RULE,
        "approval_next_required_action": RDQ_APPROVAL_NEXT_REQUIRED_ACTION,
        "approval_current_stage": RDQ_APPROVAL_CURRENT_STAGE,
        "mission_flow_current_stage": (
            RDQ_APPROVAL_MISSION_FLOW_CURRENT_STAGE
        ),
        "mission_flow_next_required_action": (
            RDQ_APPROVAL_MISSION_FLOW_NEXT_REQUIRED_ACTION
        ),
        "mission_flow_aligned": assessment["mission_flow_aligned"],
        "outcomes": list(RDQ_APPROVAL_OUTCOMES),
        "outcome": assessment["outcome"],
        "packet_complete": assessment["packet_complete"],
        "ready_for_human_approval_review": (
            assessment["ready_for_human_approval_review"]
        ),
        "required_fields": [
            {"key": key, "description": desc}
            for key, desc in RDQ_APPROVAL_REQUIRED_FIELDS
        ],
        "required_field_keys": list(RDQ_APPROVAL_REQUIRED_FIELD_KEYS),
        "required_approval_phrase": RDQ_APPROVAL_REQUIRED_PHRASE,
        "mandatory_forbidden_actions": list(
            RDQ_APPROVAL_MANDATORY_FORBIDDEN_ACTIONS
        ),
        "allowed_qa_check_whitelist": list(
            RDQ_APPROVAL_ALLOWED_QA_CHECK_WHITELIST
        ),
        "authorization_flags": list(RDQ_APPROVAL_AUTHORIZATION_FLAGS),
        "gate_lock_flags": list(RDQ_APPROVAL_GATE_LOCK_FLAGS),
        "gate_unlock_request_flags": list(
            RDQ_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_promotion_request_flags": list(
            RDQ_APPROVAL_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ),
        "executable_signal_fields": list(
            RDQ_APPROVAL_EXECUTABLE_SIGNAL_FIELDS
        ),
        "forbidden_trade_terms": list(RDQ_APPROVAL_FORBIDDEN_TRADE_TERMS),
        "assessment": assessment,
        "field_status": dict(assessment["field_status"]),
        "missing_fields": list(assessment["missing_fields"]),
        "block_reasons": list(assessment["block_reasons"]),
        "incomplete_reasons": list(assessment["incomplete_reasons"]),
        "operator_next_step": _operator_next_step(assessment),
        "operator_notes": (
            "Read-only human approval packet contract. It defines the eight "
            "fields a human must complete and checks them; it never approves and "
            "never decides. Even a COMPLETE packet authorizes nothing."
        ),
        "human_operator_required_next_steps": [
            "A human completes every required packet field.",
            "A human types the exact required approval phrase.",
            "A separate, future, explicitly human-approved review is required "
            "before any Real Data QA planning may begin.",
        ],
        "safety_posture": dict(RDQ_APPROVAL_SAFETY_POSTURE),
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
    "required_fields",
    "required_approval_phrase",
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


def validate_crypto_d1_real_data_qa_human_approval_packet_contract(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built contract. Returns a verdict dict of boolean
    checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == RDQ_APPROVAL_SCHEMA_VERSION
    label_ok = c.get("label") == RDQ_APPROVAL_LABEL
    mode_ok = c.get("mode") == RDQ_APPROVAL_MODE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    human_required = c.get("human_approval_required") is True
    confirmation_required = c.get("requires_independent_confirmation") is True
    future_step_required = (
        c.get("requires_separate_future_human_approved_step") is True
    )
    stage_ok = c.get("stage") == RDQ_APPROVAL_CURRENT_STAGE
    core_rule_ok = c.get("core_rule") == RDQ_APPROVAL_CORE_RULE
    outcome_ok = c.get("outcome") in RDQ_APPROVAL_OUTCOMES
    outcomes_ok = tuple(c.get("outcomes") or ()) == RDQ_APPROVAL_OUTCOMES
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage")
        == RDQ_APPROVAL_MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == RDQ_APPROVAL_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == RDQ_APPROVAL_SAFETY_POSTURE
    eight_required_fields = (
        list(c.get("required_field_keys") or [])
        == list(RDQ_APPROVAL_REQUIRED_FIELD_KEYS)
        and len(RDQ_APPROVAL_REQUIRED_FIELD_KEYS) == 8
    )
    phrase_ok = c.get("required_approval_phrase") == RDQ_APPROVAL_REQUIRED_PHRASE

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
    no_trade_language = not (tokens & set(RDQ_APPROVAL_FORBIDDEN_TRADE_TERMS))

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
        "eight_required_fields": eight_required_fields,
        "phrase_ok": phrase_ok,
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


def render_crypto_d1_real_data_qa_human_approval_packet_contract_markdown(
    contract: Any,
) -> str:
    """Render a built contract as a deterministic markdown brief. Pure string
    formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    status = c.get("field_status") or {}
    lines: list[str] = []
    lines.append(
        "# Crypto-D1 Real Data QA Human Approval Packet Contract"
    )
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Outcome: " + str(c.get("outcome", "")))
    lines.append("- Packet complete: " + str(c.get("packet_complete", False)))
    lines.append(
        "- Mission flow stage: " + str(c.get("mission_flow_current_stage", ""))
    )
    lines.append(
        "- Mission flow next action: "
        + str(c.get("mission_flow_next_required_action", ""))
    )
    lines.append(
        "- Unlocks real_data_qa: " + str(c.get("unlocks_real_data_qa", False))
    )
    lines.append(
        "- real_data_qa_blocked: " + str(c.get("real_data_qa_blocked", True))
    )

    _emit(
        lines,
        "Required Packet Fields",
        [
            str(item.get("key"))
            + ": "
            + str(item.get("description"))
            + " (filled: "
            + str(bool(status.get(item.get("key"))))
            + ")"
            for item in (c.get("required_fields") or [])
        ],
    )
    _emit(
        lines,
        "Mandatory Forbidden Actions",
        list(c.get("mandatory_forbidden_actions") or []),
    )
    _emit(
        lines,
        "Allowed QA Check Whitelist",
        list(c.get("allowed_qa_check_whitelist") or []),
    )
    _emit(lines, "Block Reasons", list(c.get("block_reasons") or []))
    _emit(lines, "Incomplete Reasons", list(c.get("incomplete_reasons") or []))
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

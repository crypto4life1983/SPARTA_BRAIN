"""Crypto-D1 Real Data QA Boundary Decision Readiness Review (Block 166).

A PURE, stdlib-only, *read-only* paper review. It answers exactly one
research-only question, on paper: are we ready to ASK the human operator to
make the first Real Data QA boundary decision -- i.e. to approve a future,
controlled, read-only Real Data QA step? It NEVER makes that decision, never
crosses the boundary, and never unlocks anything. It only reasons over a static,
caller-supplied summary of the parked boundary and returns a single verdict:

    READY_FOR_HUMAN_BOUNDARY_DECISION  - every required protection is in place,
                                          so a human MAY now be asked to decide.
    HOLD_NEEDS_MORE_PREP               - one or more required protections are
                                          missing, or an unsafe flag is set; do
                                          NOT ask the human yet, fix prep first.

    CURRENT_STAGE        = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    NEXT_REQUIRED_ACTION = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

CORE RULE: this review NEVER unlocks Real Data QA and NEVER authorizes a
boundary crossing. A READY_FOR_HUMAN_BOUNDARY_DECISION verdict only means "the
preparation is sound enough to put the decision in front of a human"; the
decision itself is a separate, future, explicitly human-driven act, and even
that act would, at most, permit a future read-only data QA step -- never any
execution, trading, paper, or live activity. real_data_qa stays BLOCKED,
baseline stays BLOCKED, and the paper / micro-live gates stay LOCKED here,
always.

It executes NOTHING. It does not fetch, acquire, load, inspect, transform, or
compute on any data, runs no QA, no baseline, no backtest, no simulation,
touches no broker / exchange / order / trading / paper / live surface, triggers
no automation, writes no file, reads no file, opens no network, spawns no
subprocess, reads no environment, uses no credential, mints no id, and records
no timestamp. It only reasons over a static, caller-supplied summary.

READY_FOR_HUMAN_BOUNDARY_DECISION is returned ONLY when every readiness item
passes AND no unsafe flag is set:
  1.  boundary_contract_registered         - the boundary-decision contract
                                             exists and is registered
  2.  human_approval_packet_registered     - the human approval packet exists
                                             and is registered
  3.  boundary_decision_registered         - the human-controlled boundary
                                             decision exists and is registered
  4.  jarvis_milestones_shown              - JARVIS shows 152 -> 155 -> 158 ->
                                             161 -> 162/163 correctly
  5.  provider_fetch_modules_parked        - provider/source/fetch/QA modules are
                                             cataloged PARKED / NOT_ACTIVE
  6.  offline_arc_on_hold                  - the offline Strategy Factory arc is
                                             HOLD_ARC and not adopted
  7.  no_active_execution_surface          - no active execution surface exists
  8.  no_fetch_qa_backtest_occurred        - no fetch / QA / backtest has occurred
  9.  gates_blocked_locked                 - real_data_qa / baseline /
                                             paper / micro-live remain blocked / locked
  10. next_decision_is_read_only_qa_only   - the next human decision would
                                             authorize only a future read-only
                                             data QA step, not execution/trading

If any required protection is missing, the verdict is HOLD_NEEDS_MORE_PREP, with
the failing item ids and human reasons attached. If an unsafe flag is set -- an
authorization, gate-unlock, promotion, or executable-instruction field -- the
review records a safety violation and the verdict is still HOLD_NEEDS_MORE_PREP
(never READY): an unsafe payload can never be ready, and the review refuses to
let it through.

Public API:
  - BOUNDARY_READINESS_REVIEW_SCHEMA_VERSION / _LABEL / _STATUS / _MODE
  - BOUNDARY_READINESS_REVIEW_CORE_RULE
  - BOUNDARY_READINESS_REVIEW_NEXT_REQUIRED_ACTION / _CURRENT_STAGE
  - BOUNDARY_READINESS_REVIEW_MISSION_FLOW_CURRENT_STAGE
  - BOUNDARY_READINESS_REVIEW_MISSION_FLOW_NEXT_REQUIRED_ACTION
  - BOUNDARY_READINESS_REVIEW_ITEMS / _ITEM_IDS
  - OUTCOME_READY / OUTCOME_HOLD / BOUNDARY_READINESS_REVIEW_OUTCOMES
  - BOUNDARY_READINESS_REVIEW_AUTHORIZATION_FLAGS / _GATE_LOCK_FLAGS
  - BOUNDARY_READINESS_REVIEW_GATE_UNLOCK_REQUEST_FLAGS
  - BOUNDARY_READINESS_REVIEW_FORBIDDEN_PROMOTION_REQUEST_FLAGS
  - BOUNDARY_READINESS_REVIEW_EXECUTABLE_SIGNAL_FIELDS
  - BOUNDARY_READINESS_REVIEW_FORBIDDEN_TRADE_TERMS
  - BOUNDARY_READINESS_REVIEW_SAFETY_POSTURE
  - DEFAULT_SAMPLE_BOUNDARY_READINESS_INPUT
  - assess_real_data_qa_boundary_readiness(payload)
  - build_crypto_d1_real_data_qa_boundary_readiness_review(payload=None)
  - validate_crypto_d1_real_data_qa_boundary_readiness_review(review)
  - render_crypto_d1_real_data_qa_boundary_readiness_review_markdown(review)
"""

from __future__ import annotations

from typing import Any

BOUNDARY_READINESS_REVIEW_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_real_data_qa_boundary_readiness_review.v1"
)
BOUNDARY_READINESS_REVIEW_LABEL = (
    "Block 166 - Crypto-D1 Real Data QA Boundary Readiness Review"
)
BOUNDARY_READINESS_REVIEW_STATUS = (
    "READ_ONLY_CRYPTO_D1_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW"
)
BOUNDARY_READINESS_REVIEW_MODE = "RESEARCH_ONLY"

BOUNDARY_READINESS_REVIEW_CORE_RULE = (
    "This review NEVER unlocks Real Data QA and NEVER authorizes a boundary "
    "crossing. A READY_FOR_HUMAN_BOUNDARY_DECISION verdict only means the "
    "preparation is sound enough to put the decision in front of a human; the "
    "decision itself is a separate, future, explicitly human-driven act that "
    "would, at most, permit a future read-only data QA step -- never any "
    "execution, trading, paper, or live activity. real_data_qa stays BLOCKED, "
    "baseline stays BLOCKED, and the paper / micro-live gates stay LOCKED here, "
    "always."
)

# The action that BUILDING this review satisfies, and the stage it occupies.
BOUNDARY_READINESS_REVIEW_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW"
)
BOUNDARY_READINESS_REVIEW_CURRENT_STAGE = (
    "CRYPTO_D1_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW_REQUIRED"
)

# The current mission-flow truth this review is anchored to. The companion test
# cross-checks these against the live status module so they cannot silently drift.
BOUNDARY_READINESS_REVIEW_MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
BOUNDARY_READINESS_REVIEW_MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# The ten readiness items (id, human label), in display order. READY requires
# all of them to pass.
BOUNDARY_READINESS_REVIEW_ITEMS: tuple[tuple[str, str], ...] = (
    (
        "boundary_contract_registered",
        "Boundary contract exists and is registered",
    ),
    (
        "human_approval_packet_registered",
        "Human approval packet exists and is registered",
    ),
    (
        "boundary_decision_registered",
        "Human-controlled boundary decision exists and is registered",
    ),
    (
        "jarvis_milestones_shown",
        "JARVIS shows 152 -> 155 -> 158 -> 161 -> 162/163 correctly",
    ),
    (
        "provider_fetch_modules_parked",
        "Provider / source / fetch / QA modules cataloged as PARKED / NOT_ACTIVE",
    ),
    (
        "offline_arc_on_hold",
        "Offline Strategy Factory arc is HOLD_ARC and not adopted",
    ),
    (
        "no_active_execution_surface",
        "No active execution surface exists",
    ),
    (
        "no_fetch_qa_backtest_occurred",
        "No fetch / QA / backtest has occurred",
    ),
    (
        "gates_blocked_locked",
        "real_data_qa / baseline / paper / micro-live remain blocked / locked",
    ),
    (
        "next_decision_is_read_only_qa_only",
        "Next human decision authorizes only a future read-only data QA step, "
        "not execution / trading",
    ),
)
BOUNDARY_READINESS_REVIEW_ITEM_IDS: tuple[str, ...] = tuple(
    item_id for item_id, _label in BOUNDARY_READINESS_REVIEW_ITEMS
)

# Review outcomes (exactly one assigned).
OUTCOME_READY = "READY_FOR_HUMAN_BOUNDARY_DECISION"
OUTCOME_HOLD = "HOLD_NEEDS_MORE_PREP"

BOUNDARY_READINESS_REVIEW_OUTCOMES: tuple[str, ...] = (
    OUTCOME_READY,
    OUTCOME_HOLD,
)

# Top-level (or per-record) authorization flags that, if truthy, are an unsafe
# request -> safety violation -> HOLD.
BOUNDARY_READINESS_REVIEW_AUTHORIZATION_FLAGS: tuple[str, ...] = (
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
# the payload tried to unlock a gate -> safety violation -> HOLD.
BOUNDARY_READINESS_REVIEW_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, are an unsafe request.
BOUNDARY_READINESS_REVIEW_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
)

# Requests asking the review to MEAN execution / live promotion / a boundary
# crossing. Any truthy value is an unsafe request: this review can only ever
# confirm readiness for a human decision.
BOUNDARY_READINESS_REVIEW_FORBIDDEN_PROMOTION_REQUEST_FLAGS: tuple[str, ...] = (
    "force_promote",
    "promote_to_live",
    "promote_to_paper",
    "approve_trade",
    "authorize_trade",
    "execute",
    "place_order",
    "go_live",
    "cross_boundary",
    "auto_approve_boundary",
    "auto_push",
)

# Fields whose presence (non-empty) on the payload signals an executable order /
# signal instruction rather than a static readiness summary -> safety violation.
BOUNDARY_READINESS_REVIEW_EXECUTABLE_SIGNAL_FIELDS: tuple[str, ...] = (
    "order",
    "signal",
    "trade_instruction",
    "execution",
    "live_order",
    "place_order",
)

# Execution / promotion verbs the review's own generated guidance must never
# contain as whole words.
BOUNDARY_READINESS_REVIEW_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
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
BOUNDARY_READINESS_REVIEW_SAFETY_POSTURE: dict[str, bool] = {
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


# A deterministic, illustrative paper sample mirroring the current live boundary
# truth: every required protection is in place, every gate is locked, and no
# unsafe flag is set, so the default review is READY_FOR_HUMAN_BOUNDARY_DECISION.
# Nothing here is real data; static example only.
DEFAULT_SAMPLE_BOUNDARY_READINESS_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 real data QA boundary readiness input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "research_only": True,
    "mission_flow_current_stage": (
        "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
    ),
    "mission_flow_next_required_action": (
        "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
    ),
    "boundary_contract_registered": True,
    "human_approval_packet_registered": True,
    "boundary_decision_registered": True,
    "jarvis_milestones_shown": True,
    "provider_fetch_modules_parked": True,
    "offline_arc_on_hold": True,
    "no_active_execution_surface": True,
    "no_fetch_qa_backtest_occurred": True,
    "next_decision_is_read_only_qa_only": True,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
}


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _is_truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _as_payload(payload: Any) -> dict[str, Any]:
    return dict(payload) if isinstance(payload, dict) else {}


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


def _unsafe_flag_hits(payload: dict[str, Any]) -> list[str]:
    """Collect any payload keys that attempt to authorize, unlock, promote, or
    carry an executable instruction. Pure; reads only the static payload."""
    hits: list[str] = []
    for flag in BOUNDARY_READINESS_REVIEW_AUTHORIZATION_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in BOUNDARY_READINESS_REVIEW_GATE_UNLOCK_REQUEST_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in BOUNDARY_READINESS_REVIEW_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for field in BOUNDARY_READINESS_REVIEW_EXECUTABLE_SIGNAL_FIELDS:
        value = payload.get(field)
        if value not in (None, "", [], {}, 0, False):
            hits.append(field)
    for flag in BOUNDARY_READINESS_REVIEW_GATE_LOCK_FLAGS:
        if flag in payload and not _is_truthy(payload.get(flag)):
            hits.append("unlocked:" + flag)
    seen: set[str] = set()
    ordered: list[str] = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            ordered.append(h)
    return ordered


def _gates_all_locked(payload: dict[str, Any]) -> bool:
    """True only when every gate-lock flag is present AND True."""
    return all(
        _is_truthy(payload.get(flag))
        for flag in BOUNDARY_READINESS_REVIEW_GATE_LOCK_FLAGS
    )


# --------------------------------------------------------------------------- #
# assessment
# --------------------------------------------------------------------------- #
def assess_real_data_qa_boundary_readiness(payload: Any) -> dict[str, Any]:
    """Assess (read-only) the Real Data QA boundary-decision readiness. Returns a
    fresh dict every call. Authorizes nothing and unlocks nothing under any
    outcome -- a READY_FOR_HUMAN_BOUNDARY_DECISION result only means the prep is
    sound enough to ask a human to decide."""
    data = _as_payload(payload)

    mf_stage = data.get(
        "mission_flow_current_stage",
        BOUNDARY_READINESS_REVIEW_MISSION_FLOW_CURRENT_STAGE,
    )
    mf_action = data.get(
        "mission_flow_next_required_action",
        BOUNDARY_READINESS_REVIEW_MISSION_FLOW_NEXT_REQUIRED_ACTION,
    )
    mission_flow_aligned = (
        str(mf_stage) == BOUNDARY_READINESS_REVIEW_MISSION_FLOW_CURRENT_STAGE
        and str(mf_action)
        == BOUNDARY_READINESS_REVIEW_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    unsafe_hits = _unsafe_flag_hits(data)
    gates_locked = _gates_all_locked(data)

    # Each item passes only when the caller's static summary asserts it AND no
    # unsafe flag undermines it. gates_blocked_locked is derived from the four
    # gate-lock flags directly (never trusted as a bare boolean).
    item_results: dict[str, bool] = {
        "boundary_contract_registered": _is_truthy(
            data.get("boundary_contract_registered")
        ),
        "human_approval_packet_registered": _is_truthy(
            data.get("human_approval_packet_registered")
        ),
        "boundary_decision_registered": _is_truthy(
            data.get("boundary_decision_registered")
        ),
        "jarvis_milestones_shown": _is_truthy(
            data.get("jarvis_milestones_shown")
        ),
        "provider_fetch_modules_parked": _is_truthy(
            data.get("provider_fetch_modules_parked")
        ),
        "offline_arc_on_hold": _is_truthy(data.get("offline_arc_on_hold")),
        "no_active_execution_surface": _is_truthy(
            data.get("no_active_execution_surface")
        )
        and len(unsafe_hits) == 0,
        "no_fetch_qa_backtest_occurred": _is_truthy(
            data.get("no_fetch_qa_backtest_occurred")
        ),
        "gates_blocked_locked": gates_locked,
        "next_decision_is_read_only_qa_only": _is_truthy(
            data.get("next_decision_is_read_only_qa_only")
        )
        and mission_flow_aligned,
    }

    _reasons = {
        "boundary_contract_registered": (
            "boundary-decision contract is registered"
            if item_results["boundary_contract_registered"]
            else "boundary-decision contract is NOT registered"
        ),
        "human_approval_packet_registered": (
            "human approval packet is registered"
            if item_results["human_approval_packet_registered"]
            else "human approval packet is NOT registered"
        ),
        "boundary_decision_registered": (
            "human-controlled boundary decision is registered"
            if item_results["boundary_decision_registered"]
            else "human-controlled boundary decision is NOT registered"
        ),
        "jarvis_milestones_shown": (
            "JARVIS shows the 152 -> 155 -> 158 -> 161 -> 162/163 milestones"
            if item_results["jarvis_milestones_shown"]
            else "JARVIS does NOT show the 152 -> 155 -> 158 -> 161 -> 162/163 "
            "milestones"
        ),
        "provider_fetch_modules_parked": (
            "provider / source / fetch / QA modules are cataloged PARKED / "
            "NOT_ACTIVE"
            if item_results["provider_fetch_modules_parked"]
            else "provider / source / fetch / QA modules are NOT confirmed "
            "PARKED"
        ),
        "offline_arc_on_hold": (
            "offline Strategy Factory arc is HOLD_ARC and not adopted"
            if item_results["offline_arc_on_hold"]
            else "offline Strategy Factory arc is NOT confirmed on HOLD_ARC"
        ),
        "no_active_execution_surface": (
            "no active execution surface exists"
            if item_results["no_active_execution_surface"]
            else "an active or unsafe execution surface was detected"
        ),
        "no_fetch_qa_backtest_occurred": (
            "no fetch / QA / backtest has occurred"
            if item_results["no_fetch_qa_backtest_occurred"]
            else "a fetch / QA / backtest is NOT confirmed absent"
        ),
        "gates_blocked_locked": (
            "real_data_qa / baseline / paper / micro-live remain blocked / "
            "locked"
            if item_results["gates_blocked_locked"]
            else "one or more gates are NOT confirmed blocked / locked"
        ),
        "next_decision_is_read_only_qa_only": (
            "the next human decision authorizes only a future read-only data "
            "QA step, and mission flow is still at the boundary"
            if item_results["next_decision_is_read_only_qa_only"]
            else "the next human decision is NOT confirmed read-only-QA-only, "
            "or mission flow has left the boundary"
        ),
    }

    review_items = [
        {
            "id": item_id,
            "label": label,
            "passed": item_results[item_id],
            "reason": _reasons[item_id],
        }
        for item_id, label in BOUNDARY_READINESS_REVIEW_ITEMS
    ]

    failed_items = [c["id"] for c in review_items if not c["passed"]]
    safety_violation = len(unsafe_hits) > 0

    if safety_violation or failed_items:
        outcome = OUTCOME_HOLD
    else:
        outcome = OUTCOME_READY

    return {
        "mode": BOUNDARY_READINESS_REVIEW_MODE,
        "outcome": outcome,
        "mission_flow_current_stage": str(mf_stage),
        "mission_flow_next_required_action": str(mf_action),
        "mission_flow_aligned": mission_flow_aligned,
        "review_items": review_items,
        "review_item_ids": list(BOUNDARY_READINESS_REVIEW_ITEM_IDS),
        "passed_item_ids": [c["id"] for c in review_items if c["passed"]],
        "failed_item_ids": list(failed_items),
        "unsafe_flag_hits": list(unsafe_hits),
        "safety_violation": safety_violation,
        "gates_blocked_locked": gates_locked,
        "ready": outcome == OUTCOME_READY,
        "ready_for_human_boundary_decision": outcome == OUTCOME_READY,
        "assesses_research_only": True,
        "unlocks_real_data_qa": False,
        "crosses_boundary": False,
        "authorizes_nothing": True,
    }


# --------------------------------------------------------------------------- #
# review build
# --------------------------------------------------------------------------- #
def _operator_next_step(assessment: dict[str, Any]) -> str:
    if assessment["outcome"] == OUTCOME_READY:
        return (
            "Ready to ASK the human operator for the Real Data QA boundary "
            "decision. Readiness is not approval: a human must still decide, on "
            "paper, whether to permit a future read-only data QA step. This "
            "review unlocks nothing and crosses no boundary; real_data_qa "
            "remains BLOCKED until a separate, future, explicitly human-approved "
            "step provides authorization."
        )
    if assessment["safety_violation"]:
        return (
            "Hold. An unsafe flag was set (authorization / gate-unlock / "
            "promotion / executable field). Do NOT ask the human yet. Rebuild "
            "the readiness summary as a static, research-only posture; acquire "
            "no data, run no QA, baseline, or any real-money activity. "
            "real_data_qa remains BLOCKED."
        )
    return (
        "Hold. One or more required protections are missing -- resolve every "
        "failing readiness item before asking a human to make the boundary "
        "decision. Nothing is acquired, inspected, or run; real_data_qa remains "
        "BLOCKED."
    )


def build_crypto_d1_real_data_qa_boundary_readiness_review(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only Real Data QA Boundary Readiness
    Review record. All capability flags are False and all gate locks are True
    regardless of the assessed outcome."""
    data = (
        dict(DEFAULT_SAMPLE_BOUNDARY_READINESS_INPUT)
        if payload is None
        else _as_payload(payload)
    )
    assessment = assess_real_data_qa_boundary_readiness(data)

    review: dict[str, Any] = {
        "schema_version": BOUNDARY_READINESS_REVIEW_SCHEMA_VERSION,
        "label": BOUNDARY_READINESS_REVIEW_LABEL,
        "status": BOUNDARY_READINESS_REVIEW_STATUS,
        "stage": BOUNDARY_READINESS_REVIEW_CURRENT_STAGE,
        "mode": BOUNDARY_READINESS_REVIEW_MODE,
        "core_rule": BOUNDARY_READINESS_REVIEW_CORE_RULE,
        "review_next_required_action": (
            BOUNDARY_READINESS_REVIEW_NEXT_REQUIRED_ACTION
        ),
        "review_current_stage": BOUNDARY_READINESS_REVIEW_CURRENT_STAGE,
        "mission_flow_current_stage": (
            BOUNDARY_READINESS_REVIEW_MISSION_FLOW_CURRENT_STAGE
        ),
        "mission_flow_next_required_action": (
            BOUNDARY_READINESS_REVIEW_MISSION_FLOW_NEXT_REQUIRED_ACTION
        ),
        "mission_flow_aligned": assessment["mission_flow_aligned"],
        "outcomes": list(BOUNDARY_READINESS_REVIEW_OUTCOMES),
        "outcome": assessment["outcome"],
        "ready": assessment["ready"],
        "ready_for_human_boundary_decision": (
            assessment["ready_for_human_boundary_decision"]
        ),
        "safety_violation": assessment["safety_violation"],
        "review_item_ids": list(BOUNDARY_READINESS_REVIEW_ITEM_IDS),
        "review_items": assessment["review_items"],
        "passed_item_ids": list(assessment["passed_item_ids"]),
        "failed_item_ids": list(assessment["failed_item_ids"]),
        "unsafe_flag_hits": list(assessment["unsafe_flag_hits"]),
        "authorization_flags": list(
            BOUNDARY_READINESS_REVIEW_AUTHORIZATION_FLAGS
        ),
        "gate_lock_flags": list(BOUNDARY_READINESS_REVIEW_GATE_LOCK_FLAGS),
        "gate_unlock_request_flags": list(
            BOUNDARY_READINESS_REVIEW_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_promotion_request_flags": list(
            BOUNDARY_READINESS_REVIEW_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ),
        "executable_signal_fields": list(
            BOUNDARY_READINESS_REVIEW_EXECUTABLE_SIGNAL_FIELDS
        ),
        "forbidden_trade_terms": list(
            BOUNDARY_READINESS_REVIEW_FORBIDDEN_TRADE_TERMS
        ),
        "assessment": assessment,
        "operator_next_step": _operator_next_step(assessment),
        "operator_notes": (
            "Read-only boundary readiness review. It confirms the ten readiness "
            "items; it never approves, never decides, and never crosses the "
            "boundary. Even a READY_FOR_HUMAN_BOUNDARY_DECISION result "
            "authorizes nothing."
        ),
        "human_operator_required_next_steps": [
            "A human confirms the ten readiness items passed.",
            "A human reviewer separately decides whether to ever permit a "
            "future read-only data QA step.",
            "A separate, future, explicitly human-approved step is required "
            "before any Real Data QA planning may begin.",
        ],
        "safety_posture": dict(BOUNDARY_READINESS_REVIEW_SAFETY_POSTURE),
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
        "crosses_boundary": False,
        "promotes_beyond_boundary": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return review


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
_REQUIRED_REVIEW_FIELDS: tuple[str, ...] = (
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
    "review_items",
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
    "crosses_boundary",
    "promotes_beyond_boundary",
)

_ALL_GATE_LOCKS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def validate_crypto_d1_real_data_qa_boundary_readiness_review(
    review: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built review. Returns a verdict dict of boolean
    checks plus an overall `valid`."""
    c = review if isinstance(review, dict) else {}
    missing = [f for f in _REQUIRED_REVIEW_FIELDS if f not in c]

    schema_ok = (
        c.get("schema_version") == BOUNDARY_READINESS_REVIEW_SCHEMA_VERSION
    )
    label_ok = c.get("label") == BOUNDARY_READINESS_REVIEW_LABEL
    mode_ok = c.get("mode") == BOUNDARY_READINESS_REVIEW_MODE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    human_required = c.get("human_approval_required") is True
    confirmation_required = c.get("requires_independent_confirmation") is True
    future_step_required = (
        c.get("requires_separate_future_human_approved_step") is True
    )
    stage_ok = c.get("stage") == BOUNDARY_READINESS_REVIEW_CURRENT_STAGE
    core_rule_ok = c.get("core_rule") == BOUNDARY_READINESS_REVIEW_CORE_RULE
    outcome_ok = c.get("outcome") in BOUNDARY_READINESS_REVIEW_OUTCOMES
    outcomes_ok = (
        tuple(c.get("outcomes") or ()) == BOUNDARY_READINESS_REVIEW_OUTCOMES
    )
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage")
        == BOUNDARY_READINESS_REVIEW_MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == BOUNDARY_READINESS_REVIEW_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = (
        c.get("safety_posture") == BOUNDARY_READINESS_REVIEW_SAFETY_POSTURE
    )

    items = c.get("review_items")
    ten_review_items = (
        isinstance(items, list)
        and len(items) == 10
        and [item.get("id") for item in items]
        == list(BOUNDARY_READINESS_REVIEW_ITEM_IDS)
    )

    # READY may only appear when every readiness item passed AND no safety
    # violation was recorded.
    ready_value = c.get("ready") is True
    all_items_passed = isinstance(items, list) and all(
        bool(item.get("passed")) for item in items
    )
    no_safety_violation = c.get("safety_violation") is False
    ready_only_when_all_pass = (not ready_value) or (
        all_items_passed and no_safety_violation
    )

    # the review must never directly unlock real data QA or cross the boundary
    real_data_qa_stays_blocked = (
        c.get("unlocks_real_data_qa") is False
        and c.get("real_data_qa_blocked") is True
        and c.get("crosses_boundary") is False
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
    no_trade_language = not (
        tokens & set(BOUNDARY_READINESS_REVIEW_FORBIDDEN_TRADE_TERMS)
    )

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
        "ten_review_items": ten_review_items,
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


def render_crypto_d1_real_data_qa_boundary_readiness_review_markdown(
    review: Any,
) -> str:
    """Render a built review as a deterministic markdown brief. Pure string
    formatting; writes nothing."""
    c = review if isinstance(review, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Real Data QA Boundary Readiness Review")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Outcome: " + str(c.get("outcome", "")))
    lines.append("- Ready: " + str(c.get("ready", False)))
    lines.append("- Safety violation: " + str(c.get("safety_violation", False)))
    lines.append(
        "- Mission flow stage: " + str(c.get("mission_flow_current_stage", ""))
    )
    lines.append(
        "- Unlocks real_data_qa: " + str(c.get("unlocks_real_data_qa", False))
    )
    lines.append("- Crosses boundary: " + str(c.get("crosses_boundary", False)))
    lines.append(
        "- real_data_qa_blocked: " + str(c.get("real_data_qa_blocked", True))
    )

    _emit(
        lines,
        "Readiness Review",
        [
            str(item.get("id"))
            + ": "
            + ("PASS" if item.get("passed") else "FAIL")
            + " - "
            + str(item.get("reason"))
            for item in (c.get("review_items") or [])
        ],
    )
    _emit(lines, "Failed Items", list(c.get("failed_item_ids") or []))
    _emit(lines, "Unsafe Flag Hits", list(c.get("unsafe_flag_hits") or []))
    _emit(
        lines,
        "No Execution Authorization",
        [
            "authorizes_nothing: " + str(c.get("authorizes_nothing", True)),
            "unlocks_real_data_qa: "
            + str(c.get("unlocks_real_data_qa", False)),
            "crosses_boundary: " + str(c.get("crosses_boundary", False)),
            "requires_separate_future_human_approved_step: "
            + str(c.get("requires_separate_future_human_approved_step", True)),
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)

"""Crypto-D1 Human-Controlled Real Data QA Boundary Decision (Block 158).

A PURE, stdlib-only, *read-only* DECISION layer. It is the explicit
human-controlled gate that resolves -- on paper only -- whether SPARTA may
proceed toward the FIRST controlled, read-only Real Data QA PLANNING step at the
parked mission-flow boundary

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

It is DISTINCT from its siblings: the Block 134 boundary decision *contract*
assesses evidence quality to decide whether a human packet may even be assembled;
the Block 136 *contract* is the eight-field approval form; the Block 155 *packet*
is the human-facing decision briefing. THIS module is the decision itself -- it
consumes an explicit human approval input and emits exactly one outcome:

  - BLOCK                      : the input tried to authorize / unlock / promote /
                                 execute, or the mission flow is not parked at the
                                 boundary. Nothing proceeds.
  - HOLD_AWAIT                 : no explicit human approval present (default). The
                                 boundary stays parked; nothing changes.
  - PERMIT_NEXT_PLANNING_STEP  : an explicit human approval is present. This
                                 permits ONLY assembling the next read-only Real
                                 Data QA PLANNING packet -- never execution, never
                                 data fetch, never QA / baseline / backtest, never
                                 a gate unlock.

THIS module executes NOTHING. It does NOT fetch, acquire, download, inspect,
read, or transform any data, runs no QA, no baseline, no backtest, no
simulation, touches no broker / exchange / order / account / paper / live
surface, activates no automation / autopilot, performs no auto-push, opens no
network, reads no .env, inspects no credential, prints / logs / stores no
secret, reads or writes no file, spawns no subprocess, reads no environment
variable, mints no id, and records no timestamp. It only reasons over a static,
caller-supplied human-decision input and returns a fresh record every call.

CORE RULE: under EVERY outcome -- including PERMIT_NEXT_PLANNING_STEP --
real_data_qa stays BLOCKED (it is never auto-unlocked here), baseline stays
BLOCKED, and paper / micro-live stay LOCKED. A PERMIT points only at the next
read-only PLANNING packet, which itself requires a separate, future, explicitly
human-approved review before anything is run.

Public API:
  - DECISION_SCHEMA_VERSION / DECISION_LABEL / DECISION_STATUS / DECISION_MODE
  - DECISION_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - DECISION_APPROVAL_REQUIRED_TOKEN / DECISION_OPTIONS
  - OUTCOME_BLOCK / OUTCOME_HOLD_AWAIT / OUTCOME_PERMIT_NEXT_PLANNING_STEP
  - DECISION_OUTCOMES
  - WHAT_PERMIT_GRANTS / WHAT_REMAINS_FORBIDDEN
  - DECISION_FORBIDDEN_FLAGS / DECISION_FORBIDDEN_TRADE_TERMS
  - DECISION_SAFETY_POSTURE / DEFAULT_DECISION_INPUT
  - build_real_data_qa_boundary_decision(payload=None)
  - validate_real_data_qa_boundary_decision(decision)
  - render_real_data_qa_boundary_decision_markdown(decision)
"""

from __future__ import annotations

from typing import Any

# Single source of truth for the parked boundary constants: re-exported from the
# Block 136 human-approval-packet CONTRACT (a pure, stdlib-only sibling). The
# companion test additionally cross-checks these against the live mission-flow
# status module so neither can silently drift.
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract import (  # noqa: E501
    RDQ_APPROVAL_MISSION_FLOW_CURRENT_STAGE as MISSION_FLOW_CURRENT_STAGE,
    RDQ_APPROVAL_MISSION_FLOW_NEXT_REQUIRED_ACTION as MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

DECISION_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_real_data_qa_boundary_decision.v1"
)
DECISION_LABEL = (
    "Block 158 - Crypto-D1 Human-Controlled Real Data QA Boundary Decision"
)
DECISION_STATUS = "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
DECISION_MODE = "RESEARCH_ONLY"

DECISION_CORE_RULE = (
    "This is the human-controlled boundary decision layer. It REQUIRES an "
    "explicit human approval input. With no approval it outputs HOLD / AWAIT and "
    "changes nothing. With approval present it permits ONLY the next read-only "
    "Real Data QA PLANNING step -- assembling the next planning packet -- never "
    "execution, never data fetch, never QA / baseline / backtest, and never a "
    "gate unlock. Under every outcome real_data_qa stays BLOCKED (never "
    "auto-unlocked here), baseline stays BLOCKED, and paper / micro-live stay "
    "LOCKED; a separate, future, explicitly human-approved step is always "
    "required before anything is run."
)

# The single recorded human-decision value that grants a permit. It is captured
# verbatim and resolved to PERMIT_NEXT_PLANNING_STEP only when the mission flow
# is parked at the boundary and the input carries no forbidden authorization.
DECISION_APPROVAL_REQUIRED_TOKEN = "APPROVE_REAL_DATA_QA_PLANNING_ONLY"

# The values a human may record. Only the approval token grants a permit; AWAIT
# and DECLINE both resolve to HOLD_AWAIT, as does any unrecognized / absent value.
DECISION_OPTIONS: tuple[str, ...] = (
    "AWAIT",
    "DECLINE",
    "APPROVE_REAL_DATA_QA_PLANNING_ONLY",
)
_DECISION_OPTION_SET: frozenset[str] = frozenset(DECISION_OPTIONS)

# Boundary-decision outcomes (exactly one assigned), in precedence order.
OUTCOME_BLOCK = "BLOCK"
OUTCOME_HOLD_AWAIT = "HOLD_AWAIT"
OUTCOME_PERMIT_NEXT_PLANNING_STEP = "PERMIT_NEXT_PLANNING_STEP"

DECISION_OUTCOMES: tuple[str, ...] = (
    OUTCOME_BLOCK,
    OUTCOME_HOLD_AWAIT,
    OUTCOME_PERMIT_NEXT_PLANNING_STEP,
)

# Exactly what a present human approval permits. Deliberately narrow: only the
# next read-only PLANNING packet. Nothing is executed, fetched, or unlocked.
WHAT_PERMIT_GRANTS: tuple[str, ...] = (
    "Permit advancing to the NEXT read-only Real Data QA PLANNING step only -- "
    "assembling the next planning packet that defines scope, read-only checks, "
    "and stop conditions for a future controlled QA step.",
    "The permitted next step is itself a read-only planning packet; it acquires "
    "no data, inspects no dataset, and runs no QA / baseline / backtest.",
    "Require a separate, future, explicitly human-approved review of that next "
    "planning packet before any Real Data QA step is ever run.",
)

# Exactly what stays forbidden at and beyond this boundary, regardless of any
# input or outcome. This module enforces none of these by executing; it only
# states them and keeps every capability flag False and every gate lock True.
WHAT_REMAINS_FORBIDDEN: tuple[str, ...] = (
    "No data fetch, acquisition, or download of any kind.",
    "No dataset inspection or reading of any data file.",
    "No QA run.",
    "No baseline.",
    "No backtest or simulation.",
    "No broker / exchange / order / account endpoint.",
    "No paper trading.",
    "No live trading.",
    "No automation or autopilot activation, and no auto-push.",
    "No API / network / credential / .env access.",
    "No runtime / dashboard / data writes.",
    "No gate unlock of real_data_qa, baseline, paper, or micro-live -- a permit "
    "points only at the next read-only planning step, never an unlock.",
)

# Top-level flags that, if truthy on the input, force a BLOCK. Any of these means
# the caller tried to bend this decision into an authorization / unlock /
# promotion / execution.
DECISION_FORBIDDEN_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "authorizes_qa_baseline",
    "authorizes_data_fetch",
    "unlocks_downstream_gate",
    "print_credentials",
    "expose_secret",
    "inspect_dotenv",
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
    "run_qa_now",
    "run_baseline_now",
    "run_backtest_now",
    "fetch_data_now",
    "activate_autopilot",
    "enable_auto_push",
    "place_order",
    "go_live",
)

# Execution / promotion verbs the authored narrative must never contain as whole
# words.
DECISION_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Read-only safety posture. Posture facts are True; every capability / execution
# flag is False.
DECISION_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "human_decision_required": True,
    "parked_at_boundary": True,
    "executes": False,
    "performs_data_fetch": False,
    "inspects_dataset": False,
    "reads_data_files": False,
    "writes_data_files": False,
    "uses_network": False,
    "reads_dotenv": False,
    "exposes_secret": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "runs_qa": False,
    "runs_baseline": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "activates_automation": False,
    "activates_autopilot": False,
    "performs_auto_push": False,
    "authorizes_trading": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_order_placement": False,
    "authorizes_account_control": False,
    "authorizes_portfolio_control": False,
    "authorizes_strategy_promotion": False,
    "authorizes_automation_trading": False,
    "authorizes_data_fetch": False,
    "authorizes_qa_baseline": False,
    "auto_unlocks_real_data_qa": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}

# Deterministic static input. No real data, no secret, no authorization flag, and
# no human decision -- so the default outcome is HOLD_AWAIT: the gate holds.
DEFAULT_DECISION_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 real data QA boundary decision input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
    "human_decision": None,
}


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _as_payload(payload: Any) -> dict[str, Any]:
    return dict(payload) if isinstance(payload, dict) else {}


def _is_truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _upper(value: Any) -> str:
    return str(value).strip().upper() if value is not None else ""


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


_SECRET_VALUE_TOKENS: tuple[str, ...] = (
    "api_key",
    "apikey",
    "secret",
    "password",
    "private_key",
    "bearer",
    "access_token",
)


def _has_secret_value(obj: Any) -> bool:
    """True if any dict key looks like a secret AND carries a non-empty string
    value. A secret VALUE is always a string; booleans (e.g. *_exposed=False) and
    counts are flags, never secrets."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_l = str(key).lower()
            looks_secret = any(tok in key_l for tok in _SECRET_VALUE_TOKENS)
            if looks_secret and isinstance(value, str) and value.strip():
                return True
            if _has_secret_value(value):
                return True
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            if _has_secret_value(item):
                return True
    return False


# --------------------------------------------------------------------------- #
# decision build
# --------------------------------------------------------------------------- #
def _operator_next_step(outcome: str) -> str:
    if outcome == OUTCOME_BLOCK:
        return (
            "Hold at the boundary. The input attempted an authorization, "
            "unlock, promotion, or execution, or the mission flow is not parked "
            "at the human-controlled real data QA boundary. Resolve the listed "
            "block reasons in research only; acquire no data, run no QA / "
            "baseline / backtest, and touch no real-money surface."
        )
    if outcome == OUTCOME_HOLD_AWAIT:
        return (
            "HOLD / AWAIT. No explicit human approval is present, so the "
            "boundary stays parked and nothing changes. A human must record "
            "APPROVE_REAL_DATA_QA_PLANNING_ONLY to permit only the next "
            "read-only planning step; real_data_qa stays BLOCKED until then."
        )
    return (
        "Approval recorded for PLANNING ONLY. This permits only assembling the "
        "next read-only Real Data QA PLANNING packet -- scope, read-only checks, "
        "and stop conditions. It runs nothing, fetches nothing, and unlocks no "
        "gate; real_data_qa stays BLOCKED and the next planning packet still "
        "requires its own separate, future, explicitly human-approved review."
    )


def build_real_data_qa_boundary_decision(payload: Any = None) -> dict[str, Any]:
    """Build (fresh each call) the read-only human-controlled boundary decision
    record. Every capability flag is False and every gate lock is True regardless
    of the resolved outcome. A PERMIT permits only the next read-only PLANNING
    step; it unlocks nothing and real_data_qa stays BLOCKED under all outcomes."""
    data = (
        dict(DEFAULT_DECISION_INPUT) if payload is None else _as_payload(payload)
    )

    mf_stage = data.get("mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE)
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_flag_hits = [
        f for f in DECISION_FORBIDDEN_FLAGS if _is_truthy(data.get(f))
    ]

    raw_decision = data.get("human_decision")
    decision = _upper(raw_decision) if raw_decision not in (None, "") else None
    decision_recognized = decision in _DECISION_OPTION_SET if decision else False
    approval_token_present = decision == DECISION_APPROVAL_REQUIRED_TOKEN

    block_reasons: list[str] = []
    if forbidden_flag_hits:
        block_reasons.append(
            "input requested authorization / unlock / promotion / execution: "
            + ", ".join(forbidden_flag_hits)
        )
    if not mission_flow_aligned:
        block_reasons.append(
            "mission flow is not parked at the human-controlled real data QA "
            "boundary; no boundary decision may proceed"
        )

    hold_reasons: list[str] = []
    if not block_reasons and not approval_token_present:
        if decision is None:
            hold_reasons.append(
                "no human approval is present; the boundary stays parked"
            )
        elif decision == "DECLINE":
            hold_reasons.append(
                "the human recorded DECLINE; the boundary stays parked"
            )
        elif decision == "AWAIT":
            hold_reasons.append(
                "the human recorded AWAIT; the boundary stays parked"
            )
        else:
            hold_reasons.append(
                "the recorded human decision is not the required approval "
                "token; the boundary stays parked"
            )

    if block_reasons:
        outcome = OUTCOME_BLOCK
    elif approval_token_present:
        outcome = OUTCOME_PERMIT_NEXT_PLANNING_STEP
    else:
        outcome = OUTCOME_HOLD_AWAIT

    permits_next_planning_step = outcome == OUTCOME_PERMIT_NEXT_PLANNING_STEP
    safe = not forbidden_flag_hits and mission_flow_aligned

    next_permitted_step = (
        "Assemble the next read-only Real Data QA PLANNING packet (scope, "
        "read-only checks, and stop conditions only). It runs nothing and "
        "requires its own separate, future, explicitly human-approved review."
        if permits_next_planning_step
        else None
    )

    boundary_decision = {
        "parked_stage": MISSION_FLOW_CURRENT_STAGE,
        "parked_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "approval_required_token": DECISION_APPROVAL_REQUIRED_TOKEN,
        "decision_options": list(DECISION_OPTIONS),
        "human_decision_recorded": decision,
        "human_decision_recognized": decision_recognized,
        "approval_present": permits_next_planning_step,
        "outcome": outcome,
        "permits_next_planning_step": permits_next_planning_step,
        "next_permitted_step": next_permitted_step,
        "what_permit_grants": list(WHAT_PERMIT_GRANTS),
        "what_remains_forbidden": list(WHAT_REMAINS_FORBIDDEN),
        "block_reasons": list(block_reasons),
        "hold_reasons": list(hold_reasons),
        "no_unlock_confirmation": {
            "auto_unlocks_real_data_qa": False,
            "unlocks_real_data_qa": False,
            "unlocks_baseline_backtest": False,
            "unlocks_paper_trading": False,
            "unlocks_micro_live": False,
            "real_data_qa_state": "BLOCKED",
            "baseline_backtest_state": "BLOCKED",
            "paper_live_state": "LOCKED",
        },
    }

    decision_record: dict[str, Any] = {
        "schema_version": DECISION_SCHEMA_VERSION,
        "label": DECISION_LABEL,
        "status": DECISION_STATUS,
        "mode": DECISION_MODE,
        "core_rule": DECISION_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": mission_flow_aligned,
        "outcomes": list(DECISION_OUTCOMES),
        "outcome": outcome,
        "safe": safe,
        "forbidden_flag_hits": list(forbidden_flag_hits),
        "human_decision_recorded": decision,
        "human_decision_recognized": decision_recognized,
        "approval_present": permits_next_planning_step,
        "permits_next_planning_step": permits_next_planning_step,
        "next_permitted_step": next_permitted_step,
        "boundary_decision": boundary_decision,
        "block_reasons": list(block_reasons),
        "hold_reasons": list(hold_reasons),
        "decision_summary": (
            "Human-controlled real data QA boundary decision. With no explicit "
            "approval the outcome is HOLD / AWAIT and nothing changes. With the "
            "approval token present the outcome permits only the next read-only "
            "planning step. No data is fetched or inspected, no QA / baseline / "
            "backtest is run, and no gate is unlocked under any outcome."
        ),
        "operator_next_step": _operator_next_step(outcome),
        "human_operator_required_next_steps": [
            "A human reviews this read-only boundary decision.",
            "A human records AWAIT, DECLINE, or "
            "APPROVE_REAL_DATA_QA_PLANNING_ONLY; only the approval token permits "
            "the next planning step.",
            "Even an approval permits only assembling the next read-only "
            "planning packet, which itself requires a separate, future, "
            "explicitly human-approved review before any Real Data QA step is "
            "run.",
        ],
        "requires_separate_future_human_approved_step": True,
        "human_decision_required": True,
        "this_decision_authorizes_boundary_crossing": False,
        "safety_posture": dict(DECISION_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "human_approval_required": True,
        "read_only": True,
        "research_only": True,
        "executes": False,
        "performs_data_fetch": False,
        "inspects_dataset": False,
        "reads_data_files": False,
        "writes_data_files": False,
        "uses_network": False,
        "reads_dotenv": False,
        "exposes_secret": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
        "runs_qa": False,
        "runs_baseline": False,
        "runs_backtest": False,
        "runs_simulation": False,
        "activates_automation": False,
        "activates_autopilot": False,
        "performs_auto_push": False,
        "authorizes_trading": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "authorizes_broker_exchange": False,
        "authorizes_order_placement": False,
        "authorizes_account_control": False,
        "authorizes_portfolio_control": False,
        "authorizes_strategy_promotion": False,
        "authorizes_automation_trading": False,
        "authorizes_data_fetch": False,
        "authorizes_qa_baseline": False,
        "authorizes_nothing": True,
        "auto_unlocks_real_data_qa": False,
        "unlocks_real_data_qa": False,
        "unlocks_baseline_backtest": False,
        "unlocks_paper_trading": False,
        "unlocks_micro_live": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return decision_record


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
_REQUIRED_DECISION_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "mode",
    "core_rule",
    "mission_flow_current_stage",
    "mission_flow_next_required_action",
    "outcome",
    "outcomes",
    "boundary_decision",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_REQUIRED_BOUNDARY_KEYS: tuple[str, ...] = (
    "parked_stage",
    "parked_next_required_action",
    "approval_required_token",
    "decision_options",
    "human_decision_recorded",
    "human_decision_recognized",
    "approval_present",
    "outcome",
    "permits_next_planning_step",
    "what_permit_grants",
    "what_remains_forbidden",
    "no_unlock_confirmation",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "performs_data_fetch",
    "inspects_dataset",
    "reads_data_files",
    "writes_data_files",
    "uses_network",
    "reads_dotenv",
    "exposes_secret",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
    "runs_qa",
    "runs_baseline",
    "runs_backtest",
    "runs_simulation",
    "activates_automation",
    "activates_autopilot",
    "performs_auto_push",
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_portfolio_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "authorizes_data_fetch",
    "authorizes_qa_baseline",
    "auto_unlocks_real_data_qa",
    "unlocks_real_data_qa",
    "unlocks_baseline_backtest",
    "unlocks_paper_trading",
    "unlocks_micro_live",
)

_ALL_GATE_LOCKS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def validate_real_data_qa_boundary_decision(decision: Any) -> dict[str, Any]:
    """Validate (read-only) a built boundary decision. Returns a verdict dict of
    boolean checks plus an overall `valid`."""
    c = decision if isinstance(decision, dict) else {}
    missing_fields = [f for f in _REQUIRED_DECISION_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == DECISION_SCHEMA_VERSION
    label_ok = c.get("label") == DECISION_LABEL
    status_ok = c.get("status") == DECISION_STATUS
    mode_ok = c.get("mode") == DECISION_MODE
    core_rule_ok = c.get("core_rule") == DECISION_CORE_RULE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    human_required = c.get("human_approval_required") is True
    human_decision_required = c.get("human_decision_required") is True
    future_step_required = (
        c.get("requires_separate_future_human_approved_step") is True
    )
    no_boundary_crossing = (
        c.get("this_decision_authorizes_boundary_crossing") is False
    )
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    outcome_ok = c.get("outcome") in DECISION_OUTCOMES
    outcomes_ok = tuple(c.get("outcomes") or ()) == DECISION_OUTCOMES
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == DECISION_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
    )

    # the decision must never directly unlock or auto-unlock real data QA
    real_data_qa_stays_blocked = (
        c.get("unlocks_real_data_qa") is False
        and c.get("auto_unlocks_real_data_qa") is False
        and c.get("real_data_qa_blocked") is True
    )

    # a PERMIT may permit only the next planning step, never a boundary crossing
    permit_is_planning_only = (
        c.get("outcome") != OUTCOME_PERMIT_NEXT_PLANNING_STEP
        or (
            c.get("permits_next_planning_step") is True
            and c.get("this_decision_authorizes_boundary_crossing") is False
            and c.get("unlocks_real_data_qa") is False
            and c.get("real_data_qa_blocked") is True
        )
    )

    bd = c.get("boundary_decision")
    bd_is_dict = isinstance(bd, dict)
    boundary_keys_ok = bd_is_dict and all(
        k in bd for k in _REQUIRED_BOUNDARY_KEYS
    )
    parked_refs_ok = bd_is_dict and (
        bd.get("parked_stage") == MISSION_FLOW_CURRENT_STAGE
        and bd.get("parked_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    approval_token_ok = bd_is_dict and (
        bd.get("approval_required_token") == DECISION_APPROVAL_REQUIRED_TOKEN
        and list(bd.get("decision_options") or []) == list(DECISION_OPTIONS)
    )
    would_permit_ok = bd_is_dict and bool(bd.get("what_permit_grants"))
    remains_forbidden_ok = bd_is_dict and bool(bd.get("what_remains_forbidden"))

    nuc = bd.get("no_unlock_confirmation") if bd_is_dict else None
    no_unlock_ok = isinstance(nuc, dict) and (
        nuc.get("auto_unlocks_real_data_qa") is False
        and nuc.get("unlocks_real_data_qa") is False
        and nuc.get("unlocks_baseline_backtest") is False
        and nuc.get("unlocks_paper_trading") is False
        and nuc.get("unlocks_micro_live") is False
        and nuc.get("real_data_qa_state") == "BLOCKED"
        and nuc.get("baseline_backtest_state") == "BLOCKED"
        and nuc.get("paper_live_state") == "LOCKED"
    )

    no_secret_value_fields = not _has_secret_value(c)

    # authored narrative must carry no execution / trade verbs as whole words.
    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "decision_summary", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(DECISION_FORBIDDEN_TRADE_TERMS))

    sections_ok = isinstance(c.get("operator_next_step"), str) and bool(
        c.get("operator_next_step")
    )

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "status_ok": status_ok,
        "mode_ok": mode_ok,
        "core_rule_ok": core_rule_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "human_required": human_required,
        "human_decision_required": human_decision_required,
        "future_step_required": future_step_required,
        "no_boundary_crossing": no_boundary_crossing,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "outcome_ok": outcome_ok,
        "outcomes_ok": outcomes_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "real_data_qa_stays_blocked": real_data_qa_stays_blocked,
        "permit_is_planning_only": permit_is_planning_only,
        "boundary_keys_ok": boundary_keys_ok,
        "parked_refs_ok": parked_refs_ok,
        "approval_token_ok": approval_token_ok,
        "would_permit_ok": would_permit_ok,
        "remains_forbidden_ok": remains_forbidden_ok,
        "no_unlock_ok": no_unlock_ok,
        "no_secret_value_fields": no_secret_value_fields,
        "no_trade_language": no_trade_language,
        "sections_ok": sections_ok,
    }
    verdict = dict(checks)
    verdict["missing_fields"] = missing_fields
    verdict["valid"] = (not missing_fields) and all(checks.values())
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


def render_real_data_qa_boundary_decision_markdown(decision: Any) -> str:
    """Render a built boundary decision as a deterministic markdown brief. Pure
    string formatting; writes nothing."""
    c = decision if isinstance(decision, dict) else {}
    bd = c.get("boundary_decision") or {}
    lines: list[str] = []
    lines.append(
        "# Crypto-D1 Human-Controlled Real Data QA Boundary Decision"
    )
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Outcome: " + str(c.get("outcome", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Human decision recorded: "
        + str(c.get("human_decision_recorded"))
    )
    lines.append(
        "- Approval present: " + str(c.get("approval_present", False))
    )
    lines.append(
        "- Permits next planning step: "
        + str(c.get("permits_next_planning_step", False))
    )
    lines.append(
        "- Authorizes boundary crossing: "
        + str(c.get("this_decision_authorizes_boundary_crossing", False))
    )
    lines.append("- Parked stage: " + str(bd.get("parked_stage", "")))
    lines.append(
        "- Parked next action: " + str(bd.get("parked_next_required_action", ""))
    )
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(lines, "Block Reasons", list(c.get("block_reasons") or []))
    _emit(lines, "Hold Reasons", list(c.get("hold_reasons") or []))
    _emit(
        lines,
        "What A Present Approval Permits",
        list(bd.get("what_permit_grants") or []),
    )
    _emit(
        lines,
        "What Remains Forbidden",
        list(bd.get("what_remains_forbidden") or []),
    )
    _emit(
        lines,
        "No-Unlock Confirmation",
        [
            str(k) + ": " + str(v)
            for k, v in (bd.get("no_unlock_confirmation") or {}).items()
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)

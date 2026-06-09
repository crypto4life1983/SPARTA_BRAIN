"""Crypto-D1 Real Data QA Boundary Final Decision Contract (Block 174).

A PURE, stdlib-only, *read-only* FINALIZATION contract for the Real Data QA
boundary. It is the document a human uses to record one final decision after
reviewing the full upstream chain:

    Block 170 - Real Data QA Boundary Decision Packet
    Block 171 - Real Data QA Plan-Only Contract
    Block 172 - Real Data QA Plan Approval Decision Contract

It runs at the same parked mission-flow boundary

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

The single highest permission this contract can grant is
AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT, which authorizes ONLY the
drafting of the next read-only preparation contract as a future candidate. It
does NOT fetch data, does NOT inspect datasets, does NOT run QA / baseline /
backtest, does NOT unlock baseline, does NOT unlock paper / live, does NOT
contact a broker / exchange, does NOT access credentials, does NOT write
runtime / dashboard / storage, does NOT enable automation, and does NOT produce
signals / orders. It does NOT set crosses_boundary and does NOT unlock any gate.
real_data_qa stays BLOCKED, baseline stays BLOCKED, and paper / micro-live stay
LOCKED, always.

THIS contract executes NOTHING. It does NOT fetch, acquire, download, inspect,
read, or transform any data, runs no QA, no baseline, no backtest, no
simulation, touches no broker / exchange / order / account / paper / live
surface, activates no automation, performs no auto-push, opens no network, reads
no .env, inspects no credential, shows no secret, reads or writes no file,
spawns no subprocess, reads no environment variable, mints no id, and records no
timestamp. It only reasons over the static, caller-supplied upstream contracts
and a requested decision, and emits a deterministic verdict.

CORE RULE: recording an authorization here authorizes nothing beyond DRAFTING
the next read-only preparation contract as a future candidate. It crosses no
real-world boundary and unlocks no gate. Any payload or decision that tries to
fetch data, run QA, inspect datasets, unlock real_data_qa / baseline / paper /
live, enable broker / exchange, access credentials, generate signals / orders,
or write runtime / dashboard / storage is REJECTED and performs nothing.

Public API:
  - DECISION_SCHEMA_VERSION / DECISION_LABEL / DECISION_STATUS / DECISION_MODE
  - DECISION_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - ALLOWED_DECISIONS / ALLOWED_DECISION_IDS
  - FORBIDDEN_DECISIONS / FORBIDDEN_DECISION_IDS
  - DECISION_FORBIDDEN_FLAGS / DECISION_FORBIDDEN_TRADE_TERMS
  - DECISION_SAFETY_POSTURE / DEFAULT_DECISION_INPUT
  - assess_requested_decision(option_id)
  - assess_upstream_chain(packet, plan, approval)
  - build_real_data_qa_boundary_final_decision(payload=None)
  - validate_real_data_qa_boundary_final_decision(contract)
  - render_real_data_qa_boundary_final_decision_markdown(contract)
"""

from __future__ import annotations

from typing import Any

# Consume the three upstream contracts directly so this finalization can
# identity-check each one read-only. Block 171 supplies the parked-boundary
# mission-flow constants (the single source of truth this contract shares). All
# three upstream modules are themselves pure stdlib (Block 172 -> Block 171 ->
# human_approval_packet_contract -> stdlib), so these imports keep this contract
# pure and introduce no cycle back to the mission-flow registry.
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_boundary_decision_packet import (  # noqa: E501
    PACKET_LABEL as PACKET_170_LABEL,
    PACKET_SCHEMA_VERSION as PACKET_170_SCHEMA_VERSION,
    build_real_data_qa_boundary_decision_packet as _build_packet_170,
    validate_real_data_qa_boundary_decision_packet as _validate_packet_170,
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_plan_only_contract import (  # noqa: E501
    MISSION_FLOW_CURRENT_STAGE as MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION as MISSION_FLOW_NEXT_REQUIRED_ACTION,
    PLAN_LABEL as PLAN_171_LABEL,
    PLAN_SCHEMA_VERSION as PLAN_171_SCHEMA_VERSION,
    build_real_data_qa_plan_only_contract as _build_plan_171,
    validate_real_data_qa_plan_only_contract as _validate_plan_171,
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_plan_approval_decision_contract import (  # noqa: E501
    DECISION_LABEL as APPROVAL_172_LABEL,
    DECISION_SCHEMA_VERSION as APPROVAL_172_SCHEMA_VERSION,
    build_real_data_qa_plan_approval_decision as _build_approval_172,
    validate_real_data_qa_plan_approval_decision as _validate_approval_172,
)

DECISION_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_real_data_qa_boundary_final_decision_contract.v1"
)
DECISION_LABEL = (
    "Block 174 - Crypto-D1 Real Data QA Boundary Final Decision Contract"
)
DECISION_STATUS = "READ_ONLY_REAL_DATA_QA_BOUNDARY_FINAL_DECISION"
DECISION_MODE = "RESEARCH_ONLY"

DECISION_CORE_RULE = (
    "This contract records one final human decision about the Real Data QA "
    "boundary after reviewing the Block 170 packet, the Block 171 plan, and the "
    "Block 172 plan approval decision. The highest permission it can grant is "
    "AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT, which authorizes only "
    "the drafting of the next read-only preparation contract as a future "
    "candidate; it does not fetch data, inspect datasets, run QA / baseline / "
    "backtest, unlock any gate, contact a broker / exchange, access credentials, "
    "produce signals / orders, enable automation, or write runtime / dashboard / "
    "storage. It crosses no boundary and unlocks no gate. real_data_qa stays "
    "BLOCKED, baseline stays BLOCKED, and paper / micro-live stay LOCKED."
)

# The four allowed final decisions. Only AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_
# PREP_CONTRACT grants anything, and only the drafting of the next read-only
# preparation contract. (id, summary).
ALLOWED_DECISIONS: tuple[tuple[str, str], ...] = (
    (
        "AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT",
        "Authorize ONLY the drafting of the next read-only preparation contract "
        "as a future candidate; this does NOT fetch data, inspect datasets, run "
        "QA / baseline / backtest, unlock any gate, contact a broker / exchange, "
        "access credentials, produce signals / orders, enable automation, or "
        "write runtime / dashboard / storage. It crosses no boundary.",
    ),
    (
        "REQUEST_MORE_RESEARCH",
        "Request more research before any authorization; nothing is authorized "
        "and the boundary stays blocked.",
    ),
    (
        "REJECT_REAL_DATA_QA_PATH_FOR_NOW",
        "Reject the real data QA path for now; nothing is authorized and the "
        "boundary stays blocked.",
    ),
    (
        "KEEP_REAL_DATA_QA_BLOCKED",
        "Take no final decision and keep the real data QA boundary blocked.",
    ),
)
ALLOWED_DECISION_IDS: tuple[str, ...] = tuple(d for d, _ in ALLOWED_DECISIONS)

# Decisions that must always be REJECTED. Requesting any of these marks the
# contract unsafe; none is ever performed or unlocked. (id, why).
FORBIDDEN_DECISIONS: tuple[tuple[str, str], ...] = (
    ("FETCH_DATA", "Would fetch real data -- forbidden."),
    ("RUN_QA", "Would run QA -- forbidden."),
    ("INSPECT_DATASETS", "Would inspect datasets -- forbidden."),
    ("UNLOCK_REAL_DATA_QA", "Would unlock the real_data_qa gate -- forbidden."),
    (
        "UNLOCK_BASELINE_BACKTEST",
        "Would unlock baseline / backtest -- forbidden.",
    ),
    ("UNLOCK_PAPER_LIVE", "Would unlock paper / live trading -- forbidden."),
    (
        "ENABLE_BROKER_EXCHANGE",
        "Would enable a broker / exchange connection -- forbidden.",
    ),
    ("ACCESS_CREDENTIALS", "Would access credentials -- forbidden."),
    (
        "GENERATE_SIGNALS_ORDERS",
        "Would generate trade signals / orders -- forbidden.",
    ),
    (
        "WRITE_RUNTIME_DASHBOARD_STORAGE",
        "Would write runtime / dashboard / storage artifacts -- forbidden.",
    ),
)
FORBIDDEN_DECISION_IDS: tuple[str, ...] = tuple(
    d for d, _ in FORBIDDEN_DECISIONS
)

# Top-level flags that, if truthy on an operator's input, mark it unsafe.
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
    "authorizes_real_data_qa_execution",
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
    "run_simulation_now",
    "fetch_data_now",
    "inspect_dataset_now",
    "access_credentials",
    "activate_automation",
    "enable_auto_push",
    "write_runtime_artifact",
    "write_dashboard_artifact",
    "write_storage_artifact",
    "contact_broker",
    "contact_exchange",
    "generate_trade_signal",
    "generate_order",
    "place_order",
    "go_live",
)

# Execution / promotion verbs the authored narrative must never contain.
DECISION_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Read-only safety posture. Posture facts are True; every capability flag False.
DECISION_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "decision_contract_only": True,
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
    "accesses_credentials": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "writes_storage_outputs": False,
    "runs_qa": False,
    "runs_baseline": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "contacts_broker": False,
    "contacts_exchange": False,
    "activates_automation": False,
    "performs_auto_push": False,
    "generates_trade_signal": False,
    "generates_order": False,
    "approves_real_data_qa_execution": False,
    "crosses_boundary": False,
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
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}

# Deterministic static input. No real data, no secret, no authorization flag. No
# requested decision by default (the operator supplies one separately).
DEFAULT_DECISION_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 real data QA boundary final decision input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
    "requested_decision": None,
    "packet": None,
    "plan": None,
    "approval": None,
}

EFFECTIVE_AWAITING = "AWAITING_HUMAN_DECISION"
EFFECTIVE_REJECTED_UNSAFE = "REJECTED_UNSAFE"


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _as_payload(payload: Any) -> dict[str, Any]:
    return dict(payload) if isinstance(payload, dict) else {}


def _is_truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


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
# decision + upstream-chain assessment
# --------------------------------------------------------------------------- #
def assess_requested_decision(option_id: Any) -> dict[str, Any]:
    """Classify a requested final decision (read-only). An allowed decision
    authorizes at most the drafting of the next read-only preparation contract; a
    forbidden decision is rejected. Assessing a decision performs nothing and
    unlocks nothing."""
    oid = str(option_id) if option_id is not None else ""
    allowed = oid in ALLOWED_DECISION_IDS
    forbidden = oid in FORBIDDEN_DECISION_IDS
    if not oid:
        return {
            "requested": None,
            "recognized": False,
            "allowed": False,
            "rejected": False,
            "approves_execution": False,
            "crosses_boundary": False,
            "reason": "No decision requested; contract is read-only briefing only.",
        }
    if forbidden:
        reason = dict(FORBIDDEN_DECISIONS).get(oid, "Forbidden decision.")
    elif allowed:
        reason = (
            "Allowed decision; authorizes at most the drafting of the next "
            "read-only preparation contract."
        )
    else:
        reason = "Unrecognized decision; treated as not allowed."
    return {
        "requested": oid,
        "recognized": allowed or forbidden,
        "allowed": allowed,
        "rejected": forbidden or (not allowed),
        "approves_execution": False,
        "crosses_boundary": False,
        "reason": reason,
    }


def _assess_one(
    obj: Any,
    expected_label: Any,
    expected_schema: Any,
    validator: Any,
) -> dict[str, Any]:
    is_dict = isinstance(obj, dict)
    label_ok = is_dict and obj.get("label") == expected_label
    schema_ok = is_dict and obj.get("schema_version") == expected_schema
    safe = is_dict and obj.get("safe") is True
    verdict = validator(obj) if is_dict else {"valid": False}
    valid = bool(verdict.get("valid"))
    ok = is_dict and label_ok and schema_ok and safe and valid
    return {
        "present": is_dict,
        "label_ok": label_ok,
        "schema_ok": schema_ok,
        "safe": safe,
        "valid": valid,
        "ok": ok,
    }


def assess_upstream_chain(
    packet: Any, plan: Any, approval: Any
) -> dict[str, Any]:
    """Assess (read-only) the upstream Block 170 packet, Block 171 plan, and
    Block 172 plan approval decision: are they present, identity-matched, valid,
    and marked safe. Assessing the chain runs nothing and reads no data."""
    packet_assessment = _assess_one(
        packet, PACKET_170_LABEL, PACKET_170_SCHEMA_VERSION, _validate_packet_170
    )
    plan_assessment = _assess_one(
        plan, PLAN_171_LABEL, PLAN_171_SCHEMA_VERSION, _validate_plan_171
    )
    approval_assessment = _assess_one(
        approval,
        APPROVAL_172_LABEL,
        APPROVAL_172_SCHEMA_VERSION,
        _validate_approval_172,
    )
    chain_ok = (
        packet_assessment["ok"]
        and plan_assessment["ok"]
        and approval_assessment["ok"]
    )
    return {
        "packet": packet_assessment,
        "plan": plan_assessment,
        "approval": approval_assessment,
        "chain_ok": chain_ok,
    }


# --------------------------------------------------------------------------- #
# build
# --------------------------------------------------------------------------- #
def _allowed_decision_records() -> list[dict[str, Any]]:
    return [
        {
            "id": oid,
            "summary": summary,
            "approves_execution": False,
            "crosses_boundary": False,
            "unlocks_real_data_qa": False,
        }
        for oid, summary in ALLOWED_DECISIONS
    ]


def _forbidden_decision_records() -> list[dict[str, Any]]:
    return [
        {"id": oid, "why_forbidden": why, "rejected": True}
        for oid, why in FORBIDDEN_DECISIONS
    ]


def build_real_data_qa_boundary_final_decision(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only boundary final decision contract.
    Every capability flag is False and every gate lock is True regardless of
    input. crosses_boundary is always False and no gate is ever unlocked."""
    data = dict(DEFAULT_DECISION_INPUT) if payload is None else _as_payload(payload)

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

    # The upstream chain under review: supplied contracts, or freshly built
    # defaults for each missing one.
    supplied_packet = data.get("packet")
    supplied_plan = data.get("plan")
    supplied_approval = data.get("approval")
    packet = supplied_packet if isinstance(supplied_packet, dict) else _build_packet_170()
    plan = supplied_plan if isinstance(supplied_plan, dict) else _build_plan_171()
    approval = (
        supplied_approval
        if isinstance(supplied_approval, dict)
        else _build_approval_172()
    )
    chain_assessment = assess_upstream_chain(packet, plan, approval)
    chain_ok = chain_assessment["chain_ok"]

    requested = data.get("requested_decision")
    decision_assessment = assess_requested_decision(requested)
    requested_rejected = bool(decision_assessment["requested"]) and (
        decision_assessment["rejected"]
    )

    # Determine the effective decision. AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_
    # PREP_CONTRACT only sticks when the full upstream chain is OK; otherwise it
    # downgrades to a request for more research. A forbidden/unrecognized request
    # is rejected. Nothing here ever crosses the boundary or unlocks a gate.
    if requested is None:
        effective_decision = EFFECTIVE_AWAITING
        prep_authorized = False
    elif requested_rejected:
        effective_decision = EFFECTIVE_REJECTED_UNSAFE
        prep_authorized = False
    elif (
        decision_assessment["requested"]
        == "AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT"
    ):
        if chain_ok:
            effective_decision = (
                "AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT"
            )
            prep_authorized = True
        else:
            effective_decision = "REQUEST_MORE_RESEARCH"
            prep_authorized = False
    else:
        effective_decision = str(decision_assessment["requested"])
        prep_authorized = False

    authorization_scope = (
        "NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT_DRAFT_ONLY"
        if prep_authorized
        else "NONE"
    )

    safe = (
        mission_flow_aligned
        and not forbidden_flag_hits
        and not requested_rejected
    )

    decision = {
        "parked_stage": MISSION_FLOW_CURRENT_STAGE,
        "parked_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "packet_under_review_label": PACKET_170_LABEL,
        "plan_under_review_label": PLAN_171_LABEL,
        "approval_under_review_label": APPROVAL_172_LABEL,
        "chain_assessment": chain_assessment,
        "decision_assessment": decision_assessment,
        "allowed_decisions": _allowed_decision_records(),
        "forbidden_decisions": _forbidden_decision_records(),
        "effective_decision": effective_decision,
        "prep_authorized": prep_authorized,
        "authorization_scope": authorization_scope,
        "no_unlock_confirmation": {
            "unlocks_real_data_qa": False,
            "unlocks_baseline_backtest": False,
            "unlocks_paper_trading": False,
            "unlocks_micro_live": False,
            "approves_real_data_qa_execution": False,
            "crosses_boundary": False,
            "real_data_qa_state": "BLOCKED",
            "baseline_backtest_state": "BLOCKED",
            "paper_live_state": "LOCKED",
        },
    }

    contract: dict[str, Any] = {
        "schema_version": DECISION_SCHEMA_VERSION,
        "label": DECISION_LABEL,
        "status": DECISION_STATUS,
        "mode": DECISION_MODE,
        "core_rule": DECISION_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": mission_flow_aligned,
        "safe": safe,
        "forbidden_flag_hits": list(forbidden_flag_hits),
        "decision": decision,
        "effective_decision": effective_decision,
        "prep_authorized": prep_authorized,
        "authorization_scope": authorization_scope,
        "approves_real_data_qa_execution": False,
        "crosses_boundary": False,
        "decision_summary": (
            "Boundary final decision contract: a human records one of four final "
            "decisions after reviewing the Block 170 packet, the Block 171 plan, "
            "and the Block 172 plan approval decision (authorize only the drafting "
            "of the next read-only preparation contract, request more research, "
            "reject the real data QA path for now, or keep the boundary blocked). "
            "The highest grant authorizes only the drafting of the next read-only "
            "preparation contract as a future candidate; it approves no execution, "
            "crosses no boundary, and unlocks no gate. It fetches nothing, inspects "
            "nothing, runs nothing, writes nothing, and unlocks nothing."
        ),
        "operator_next_step": (
            "A human reviews the upstream chain and records one final decision. "
            "Even an AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT decision "
            "authorizes only the drafting of the next read-only preparation "
            "contract as a future candidate; real_data_qa stays BLOCKED until a "
            "separate, future, explicitly human-controlled step is supplied. "
            "Recording a decision acquires no data, runs nothing, and unlocks no "
            "gate."
        ),
        "human_operator_required_next_steps": [
            "A human reviews the Block 170 packet, the Block 171 plan, the Block "
            "172 plan approval decision, and this final decision contract.",
            "A human records exactly one allowed decision; "
            "AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT authorizes only "
            "the drafting of the next read-only preparation contract as a future "
            "candidate.",
            "Any forbidden decision (fetch, run QA, inspect datasets, unlock any "
            "gate, broker / exchange, credentials, signals / orders, runtime / "
            "dashboard / storage write) is rejected and performs nothing.",
        ],
        "requires_separate_future_human_controlled_step": True,
        "human_decision_required": True,
        "this_contract_authorizes_boundary_crossing": False,
        "highest_grant_is_next_read_only_prep_contract_draft_only": True,
        "safety_posture": dict(DECISION_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "real_strategy_intake_state": "BLOCKED",
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
        "accesses_credentials": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
        "writes_storage_outputs": False,
        "runs_qa": False,
        "runs_baseline": False,
        "runs_backtest": False,
        "runs_simulation": False,
        "contacts_broker": False,
        "contacts_exchange": False,
        "activates_automation": False,
        "performs_auto_push": False,
        "generates_trade_signal": False,
        "generates_order": False,
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
        "authorizes_nothing_beyond_next_read_only_prep_contract_draft": True,
        "unlocks_real_data_qa": False,
        "unlocks_baseline_backtest": False,
        "unlocks_paper_trading": False,
        "unlocks_micro_live": False,
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
    "mode",
    "core_rule",
    "mission_flow_current_stage",
    "mission_flow_next_required_action",
    "decision",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_REQUIRED_DECISION_KEYS: tuple[str, ...] = (
    "parked_stage",
    "parked_next_required_action",
    "packet_under_review_label",
    "plan_under_review_label",
    "approval_under_review_label",
    "chain_assessment",
    "decision_assessment",
    "allowed_decisions",
    "forbidden_decisions",
    "effective_decision",
    "prep_authorized",
    "authorization_scope",
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
    "accesses_credentials",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
    "writes_storage_outputs",
    "runs_qa",
    "runs_baseline",
    "runs_backtest",
    "runs_simulation",
    "contacts_broker",
    "contacts_exchange",
    "activates_automation",
    "performs_auto_push",
    "generates_trade_signal",
    "generates_order",
    "approves_real_data_qa_execution",
    "crosses_boundary",
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


def validate_real_data_qa_boundary_final_decision(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built boundary final decision contract. Returns a
    verdict dict of boolean checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing_fields = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

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
        c.get("requires_separate_future_human_controlled_step") is True
    )
    no_boundary_crossing = (
        c.get("this_contract_authorizes_boundary_crossing") is False
        and c.get("crosses_boundary") is False
    )
    no_execution_approval = c.get("approves_real_data_qa_execution") is False
    highest_grant_bounded = (
        c.get("highest_grant_is_next_read_only_prep_contract_draft_only") is True
    )
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = (
        c.get("authorizes_nothing_beyond_next_read_only_prep_contract_draft")
        is True
    )
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == DECISION_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
        and c.get("real_strategy_intake_state") == "BLOCKED"
    )

    d = c.get("decision")
    d_is_dict = isinstance(d, dict)
    decision_keys_ok = d_is_dict and all(
        k in d for k in _REQUIRED_DECISION_KEYS
    )
    parked_refs_ok = d_is_dict and (
        d.get("parked_stage") == MISSION_FLOW_CURRENT_STAGE
        and d.get("parked_next_required_action") == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    allowed_decisions_ok = d_is_dict and (
        isinstance(d.get("allowed_decisions"), list)
        and [o.get("id") for o in (d.get("allowed_decisions") or [])]
        == list(ALLOWED_DECISION_IDS)
        and all(
            o.get("approves_execution") is False
            and o.get("crosses_boundary") is False
            and o.get("unlocks_real_data_qa") is False
            for o in (d.get("allowed_decisions") or [])
        )
    )
    forbidden_decisions_ok = d_is_dict and (
        isinstance(d.get("forbidden_decisions"), list)
        and [o.get("id") for o in (d.get("forbidden_decisions") or [])]
        == list(FORBIDDEN_DECISION_IDS)
        and all(
            o.get("rejected") is True
            for o in (d.get("forbidden_decisions") or [])
        )
    )
    effective_known = d_is_dict and d.get("effective_decision") in (
        set(ALLOWED_DECISION_IDS)
        | {EFFECTIVE_AWAITING, EFFECTIVE_REJECTED_UNSAFE}
    )
    # An authorization may only stand when the effective decision is AUTHORIZE_
    # NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT, and even then it grants only the
    # drafting of the next read-only prep contract (never execution / boundary).
    authorization_consistent = d_is_dict and (
        (d.get("prep_authorized") is True)
        == (
            d.get("effective_decision")
            == "AUTHORIZE_NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT"
        )
    ) and (
        d.get("authorization_scope")
        == "NEXT_READ_ONLY_REAL_DATA_QA_PREP_CONTRACT_DRAFT_ONLY"
        if d.get("prep_authorized")
        else d.get("authorization_scope") == "NONE"
    )

    nuc = d.get("no_unlock_confirmation") if d_is_dict else None
    no_unlock_ok = isinstance(nuc, dict) and (
        nuc.get("unlocks_real_data_qa") is False
        and nuc.get("unlocks_baseline_backtest") is False
        and nuc.get("unlocks_paper_trading") is False
        and nuc.get("unlocks_micro_live") is False
        and nuc.get("approves_real_data_qa_execution") is False
        and nuc.get("crosses_boundary") is False
        and nuc.get("real_data_qa_state") == "BLOCKED"
        and nuc.get("baseline_backtest_state") == "BLOCKED"
        and nuc.get("paper_live_state") == "LOCKED"
    )

    no_secret_value_fields = not _has_secret_value(c)

    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "decision_summary", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(DECISION_FORBIDDEN_TRADE_TERMS))

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
        "no_execution_approval": no_execution_approval,
        "highest_grant_bounded": highest_grant_bounded,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "decision_keys_ok": decision_keys_ok,
        "parked_refs_ok": parked_refs_ok,
        "allowed_decisions_ok": allowed_decisions_ok,
        "forbidden_decisions_ok": forbidden_decisions_ok,
        "effective_known": effective_known,
        "authorization_consistent": authorization_consistent,
        "no_unlock_ok": no_unlock_ok,
        "no_secret_value_fields": no_secret_value_fields,
        "no_trade_language": no_trade_language,
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


def render_real_data_qa_boundary_final_decision_markdown(
    contract: Any,
) -> str:
    """Render a built boundary final decision contract as deterministic markdown.
    Pure string formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    d = c.get("decision") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Real Data QA Boundary Final Decision Contract")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append("- Effective decision: " + str(c.get("effective_decision", "")))
    lines.append("- Prep authorized: " + str(c.get("prep_authorized", False)))
    lines.append("- Authorization scope: " + str(c.get("authorization_scope", "")))
    lines.append(
        "- Approves real_data_qa execution: "
        + str(c.get("approves_real_data_qa_execution", False))
    )
    lines.append("- Crosses boundary: " + str(c.get("crosses_boundary", False)))
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(
        lines,
        "Allowed Decisions",
        [
            str(o.get("id")) + ": " + str(o.get("summary"))
            for o in (d.get("allowed_decisions") or [])
        ],
    )
    _emit(
        lines,
        "Forbidden Decisions (always rejected)",
        [
            str(o.get("id")) + ": " + str(o.get("why_forbidden"))
            for o in (d.get("forbidden_decisions") or [])
        ],
    )
    _emit(
        lines,
        "No-Unlock Confirmation",
        [
            str(k) + ": " + str(v)
            for k, v in (d.get("no_unlock_confirmation") or {}).items()
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)

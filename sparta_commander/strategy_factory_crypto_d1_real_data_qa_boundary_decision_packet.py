"""Crypto-D1 Human-Controlled Real Data QA Boundary Decision Packet (Block 170).

A PURE, stdlib-only, *read-only* OPERATOR DECISION packet. It is the single
document a human operator reads at the parked mission-flow boundary

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

to decide which of FOUR read-only decision options to take. It is distinct from
the Block 155 human-approval briefing: this packet enumerates the explicit
operator decision options, lists the evidence already completed, lists what is
still missing before real_data_qa could ever be safely considered, and rejects
any decision that tries to unlock, execute, fetch, run QA, touch credentials,
write runtime/dashboard/storage, or generate trade signals/orders.

The four ALLOWED decision options are recommendations ONLY. The highest of them
(AUTHORIZE_NEXT_READ_ONLY_CONTRACT_ONLY) authorizes nothing beyond building yet
another pure, read-only, research-only contract; it does NOT cross the boundary,
does NOT unlock real_data_qa, and does NOT enable any execution.

THIS packet executes NOTHING. It does NOT fetch, acquire, download, inspect,
read, or transform any data, runs no QA, no baseline, no backtest, no
simulation, touches no broker / exchange / order / account / paper / live
surface, activates no automation, performs no auto-push, opens no network, reads
no .env, inspects no credential, shows no secret, reads or writes no file, spawns
no subprocess, reads no environment variable, mints no id, and records no
timestamp. It only assembles a static, deterministic decision packet and emits it
for human review.

CORE RULE: assembling or reading this packet authorizes nothing and crosses no
real-world boundary. real_data_qa stays BLOCKED, baseline stays BLOCKED, and
paper / micro-live stay LOCKED. Choosing any allowed option is a SEPARATE, future,
explicitly human-controlled act; none of the allowed options performs a fetch,
QA, backtest, simulation, or trade, and none unlocks a downstream gate.

Public API:
  - PACKET_SCHEMA_VERSION / PACKET_LABEL / PACKET_STATUS / PACKET_MODE / PACKET_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - BOUNDARY_TRUTH
  - EVIDENCE_COMPLETED
  - MISSING_REQUIREMENTS
  - ALLOWED_DECISION_OPTIONS / ALLOWED_DECISION_OPTION_IDS
  - FORBIDDEN_DECISION_OPTIONS / FORBIDDEN_DECISION_OPTION_IDS
  - PACKET_FORBIDDEN_FLAGS / PACKET_FORBIDDEN_TRADE_TERMS
  - PACKET_SAFETY_POSTURE / DEFAULT_PACKET_INPUT
  - assess_requested_decision(option_id)
  - build_real_data_qa_boundary_decision_packet(payload=None)
  - validate_real_data_qa_boundary_decision_packet(packet)
  - render_real_data_qa_boundary_decision_packet_markdown(packet)
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

PACKET_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_real_data_qa_boundary_decision_packet.v1"
)
PACKET_LABEL = (
    "Block 170 - Crypto-D1 Real Data QA Boundary Decision Packet"
)
PACKET_STATUS = "HUMAN_CONTROLLED_BOUNDARY_DECISION_PACKET_ONLY"
PACKET_MODE = "RESEARCH_ONLY"

PACKET_CORE_RULE = (
    "This packet is the human-facing decision packet for the parked real data QA "
    "boundary. Assembling or reading it authorizes nothing and crosses no "
    "real-world boundary: no data is fetched or inspected, no QA / baseline / "
    "backtest / simulation is run, no broker / exchange / order surface is "
    "touched, no automation or auto-push fires, no network is opened, no "
    "credential or .env is read, and no secret is shown. It offers four read-only "
    "decision options that are recommendations only; even the highest option "
    "authorizes nothing beyond building another pure read-only research contract. "
    "real_data_qa stays BLOCKED, baseline stays BLOCKED, and paper / micro-live "
    "stay LOCKED."
)

# Static snapshot of the parked boundary truth this packet briefs. These are
# facts about the live mission-flow backend; the companion test cross-checks the
# stage / action against the live status module so neither can drift.
BOUNDARY_TRUTH: tuple[tuple[str, str], ...] = (
    ("current_stage", MISSION_FLOW_CURRENT_STAGE),
    ("next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION),
    ("real_data_qa", "BLOCKED"),
    ("baseline_backtest", "BLOCKED"),
    ("paper_trading_gate", "LOCKED"),
    ("micro_live_gate", "LOCKED"),
    ("real_strategy_intake", "BLOCKED"),
    ("executes", "False"),
)

# Evidence already completed in the research chain. Each entry is a static fact
# about prior, already-shipped work; this packet asserts it, it performs none of
# it. (label, state, description).
EVIDENCE_COMPLETED: tuple[tuple[str, str, str], ...] = (
    (
        "External Bot Evidence",
        "completed",
        "Read-only external bot research evidence captured and reviewed; no "
        "execution, broker, or order surface was touched.",
    ),
    (
        "Hyperliquid Whale Evidence",
        "completed",
        "Read-only Hyperliquid whale-activity research evidence captured and "
        "reviewed; observational only.",
    ),
    (
        "Funding Rate Evidence",
        "completed",
        "Read-only funding-rate research evidence captured and reviewed; "
        "observational only.",
    ),
    (
        "Bitcoin Cycle Timing Evidence",
        "completed",
        "Read-only Bitcoin cycle-timing research evidence captured and reviewed; "
        "observational only.",
    ),
    (
        "Daily Alpha Brief Research / Review / Approval",
        "completed",
        "Daily alpha brief research produced, human-reviewed, and human-approved "
        "as advisory-only; authorized no execution.",
    ),
    (
        "Selected Read-Only Spot Provider Contract / Runner Dry-Run",
        "completed",
        "Selected read-only spot provider contract (Block 168) and its in-memory "
        "fake-provider fetch-runner dry run (Block 169) shipped, registered, and "
        "reflected; no real provider, endpoint, network, or data acquisition.",
    ),
)

# What is still MISSING before real_data_qa could ever be safely considered.
# Listing a missing requirement neither satisfies it nor unlocks anything; it
# only tells the operator what a separate, future, human-controlled act would
# still need.
MISSING_REQUIREMENTS: tuple[tuple[str, str], ...] = (
    (
        "selected_data_provider_final_human_approval",
        "Final explicit human approval of the single selected read-only data "
        "provider has not been given.",
    ),
    (
        "exact_read_only_data_scope",
        "The exact read-only data scope (symbols, daily timeframe, date range, "
        "instrument type) has not been fixed and approved.",
    ),
    (
        "credentials_boundary_confirmation_if_applicable",
        "If the selected provider requires credentials, the credentials boundary "
        "has not been confirmed; no credential is held or read by this chain.",
    ),
    (
        "dataset_manifest_plan",
        "A dataset manifest plan (what files, layout, checksums) has not been "
        "authored or approved.",
    ),
    (
        "qa_checklist",
        "A read-only QA checklist (schema, nulls, duplicates, monotonic "
        "timestamps, gaps, range sanity, row counts, symbol coverage) has not "
        "been authored or approved.",
    ),
    (
        "failure_rejection_conditions",
        "Explicit failure / rejection conditions that would stop a future QA step "
        "have not been authored or approved.",
    ),
    (
        "rollback_abort_conditions",
        "Explicit rollback / abort conditions for a future QA step have not been "
        "authored or approved.",
    ),
    (
        "proof_no_execution_trading_permissions_enabled",
        "A standing proof that no execution / trading permissions are enabled "
        "must accompany any future step; gates stay BLOCKED / LOCKED and every "
        "capability flag stays False.",
    ),
)

# The FOUR allowed operator decision options. Each is a recommendation only:
# selecting it authorizes no execution and crosses no boundary. (id, summary).
ALLOWED_DECISION_OPTIONS: tuple[tuple[str, str], ...] = (
    (
        "KEEP_BLOCKED",
        "Leave the real data QA boundary BLOCKED and take no further action; the "
        "chain stays parked exactly as it is.",
    ),
    (
        "PREPARE_REAL_DATA_QA_PLAN_ONLY",
        "Authorize PLANNING ONLY of a future read-only Real Data QA step (scope, "
        "checklist, failure / rollback conditions) as a paper document; no data, "
        "QA, or unlock results from this option.",
    ),
    (
        "REQUEST_ADDITIONAL_RESEARCH",
        "Request additional read-only, advisory-only research before any boundary "
        "decision; produces research briefs only, no execution.",
    ),
    (
        "AUTHORIZE_NEXT_READ_ONLY_CONTRACT_ONLY",
        "Authorize building exactly ONE more pure, stdlib-only, read-only / "
        "research-only contract; it authorizes nothing beyond that contract and "
        "does NOT unlock real_data_qa or any gate.",
    ),
)
ALLOWED_DECISION_OPTION_IDS: tuple[str, ...] = tuple(
    opt for opt, _ in ALLOWED_DECISION_OPTIONS
)

# Decision options that must always be REJECTED. Requesting any of these marks
# the packet unsafe; none of them is ever performed or unlocked. (id, why).
FORBIDDEN_DECISION_OPTIONS: tuple[tuple[str, str], ...] = (
    ("UNLOCK_REAL_DATA_QA", "Would unlock the real_data_qa gate -- forbidden."),
    (
        "UNLOCK_BASELINE_BACKTEST",
        "Would unlock baseline / backtest -- forbidden.",
    ),
    ("UNLOCK_PAPER_TRADING", "Would unlock paper trading -- forbidden."),
    ("UNLOCK_LIVE_TRADING", "Would unlock live trading -- forbidden."),
    (
        "ENABLE_BROKER_EXCHANGE",
        "Would enable a broker / exchange connection -- forbidden.",
    ),
    ("FETCH_DATA_NOW", "Would fetch real data now -- forbidden."),
    ("RUN_QA_NOW", "Would run QA now -- forbidden."),
    ("ACCESS_CREDENTIALS", "Would access credentials -- forbidden."),
    (
        "WRITE_RUNTIME_DASHBOARD_STORAGE",
        "Would write runtime / dashboard / storage artifacts -- forbidden.",
    ),
    (
        "GENERATE_TRADE_SIGNALS_ORDERS",
        "Would generate trade signals / orders -- forbidden.",
    ),
)
FORBIDDEN_DECISION_OPTION_IDS: tuple[str, ...] = tuple(
    opt for opt, _ in FORBIDDEN_DECISION_OPTIONS
)

# Top-level flags that, if truthy on an operator's input, mark it unsafe. Any of
# these means the caller tried to bend this packet into an authorization.
PACKET_FORBIDDEN_FLAGS: tuple[str, ...] = (
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
    "run_simulation_now",
    "fetch_data_now",
    "inspect_dataset_now",
    "access_credentials",
    "activate_automation",
    "enable_auto_push",
    "write_runtime_artifact",
    "write_dashboard_artifact",
    "write_storage_artifact",
    "generate_trade_signal",
    "generate_order",
    "place_order",
    "go_live",
)

# Execution / promotion verbs the authored narrative must never contain as whole
# words.
PACKET_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Read-only safety posture. Posture facts are True; every capability / execution
# flag is False.
PACKET_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "decision_packet_only": True,
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

# Deterministic static input. No real data, no secret, no authorization flag, no
# requested decision (operator supplies one separately if desired).
DEFAULT_PACKET_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 real data QA boundary decision packet input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
    "requested_decision": None,
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
    value. A secret VALUE is always a string; booleans and counts are flags."""
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
# decision assessment
# --------------------------------------------------------------------------- #
def assess_requested_decision(option_id: Any) -> dict[str, Any]:
    """Classify a requested decision option (read-only). An allowed option is a
    recommendation only and authorizes nothing; a forbidden option is rejected.
    Selecting or assessing an option performs nothing and unlocks nothing."""
    oid = str(option_id) if option_id is not None else ""
    allowed = oid in ALLOWED_DECISION_OPTION_IDS
    forbidden = oid in FORBIDDEN_DECISION_OPTION_IDS
    if not oid:
        return {
            "requested": None,
            "recognized": False,
            "allowed": False,
            "rejected": False,
            "recommendation_only": True,
            "authorizes_execution": False,
            "crosses_boundary": False,
            "reason": "No decision requested; packet is read-only briefing only.",
        }
    reason = ""
    if forbidden:
        reason = dict(FORBIDDEN_DECISION_OPTIONS).get(oid, "Forbidden option.")
    elif allowed:
        reason = "Allowed option; recommendation only, authorizes no execution."
    else:
        reason = "Unrecognized option; treated as not allowed."
    return {
        "requested": oid,
        "recognized": allowed or forbidden,
        "allowed": allowed,
        "rejected": forbidden or (not allowed),
        "recommendation_only": True,
        "authorizes_execution": False,
        "crosses_boundary": False,
        "reason": reason,
    }


# --------------------------------------------------------------------------- #
# packet build
# --------------------------------------------------------------------------- #
def _evidence_records() -> list[dict[str, Any]]:
    return [
        {"label": label, "state": state, "description": desc}
        for label, state, desc in EVIDENCE_COMPLETED
    ]


def _missing_records() -> list[dict[str, Any]]:
    return [
        {"requirement": req, "description": desc}
        for req, desc in MISSING_REQUIREMENTS
    ]


def _allowed_option_records() -> list[dict[str, Any]]:
    return [
        {
            "id": oid,
            "summary": summary,
            "recommendation_only": True,
            "authorizes_execution": False,
            "crosses_boundary": False,
        }
        for oid, summary in ALLOWED_DECISION_OPTIONS
    ]


def _forbidden_option_records() -> list[dict[str, Any]]:
    return [
        {"id": oid, "why_forbidden": why, "rejected": True}
        for oid, why in FORBIDDEN_DECISION_OPTIONS
    ]


def build_real_data_qa_boundary_decision_packet(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only boundary decision packet. Every
    capability / execution flag is False and every gate lock is True regardless
    of input. The packet authorizes nothing and unlocks nothing."""
    data = dict(DEFAULT_PACKET_INPUT) if payload is None else _as_payload(payload)

    mf_stage = data.get("mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE)
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_flag_hits = [
        f for f in PACKET_FORBIDDEN_FLAGS if _is_truthy(data.get(f))
    ]

    requested_decision_assessment = assess_requested_decision(
        data.get("requested_decision")
    )
    requested_rejected = bool(
        requested_decision_assessment["requested"]
    ) and requested_decision_assessment["rejected"]

    safe = (
        mission_flow_aligned
        and not forbidden_flag_hits
        and not requested_rejected
    )

    boundary_decision = {
        "parked_stage": MISSION_FLOW_CURRENT_STAGE,
        "parked_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "boundary_truth": [list(pair) for pair in BOUNDARY_TRUTH],
        "evidence_completed": _evidence_records(),
        "missing_requirements": _missing_records(),
        "allowed_decision_options": _allowed_option_records(),
        "forbidden_decision_options": _forbidden_option_records(),
        "requested_decision_assessment": requested_decision_assessment,
        "no_unlock_confirmation": {
            "unlocks_real_data_qa": False,
            "unlocks_baseline_backtest": False,
            "unlocks_paper_trading": False,
            "unlocks_micro_live": False,
            "real_data_qa_state": "BLOCKED",
            "baseline_backtest_state": "BLOCKED",
            "paper_live_state": "LOCKED",
        },
    }

    packet: dict[str, Any] = {
        "schema_version": PACKET_SCHEMA_VERSION,
        "label": PACKET_LABEL,
        "status": PACKET_STATUS,
        "mode": PACKET_MODE,
        "core_rule": PACKET_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": mission_flow_aligned,
        "safe": safe,
        "forbidden_flag_hits": list(forbidden_flag_hits),
        "boundary_decision": boundary_decision,
        "packet_summary": (
            "Operator decision packet: the Crypto-D1 chain is parked at the "
            "human-controlled real data QA boundary. It summarizes the boundary "
            "truth, lists completed read-only evidence, lists what is still "
            "missing before real_data_qa could be safely considered, and offers "
            "four recommendation-only decision options while rejecting any "
            "unlock / execute / fetch / QA / credential / write / trade option. "
            "It fetches nothing, inspects nothing, runs nothing, and unlocks "
            "nothing."
        ),
        "operator_next_step": (
            "A human reads this packet and, as a SEPARATE act, selects one of the "
            "four allowed read-only options (keep blocked, prepare a QA plan "
            "document only, request more research, or authorize one more "
            "read-only contract). Reading this packet acquires no data, runs "
            "nothing, and unlocks no gate; real_data_qa stays BLOCKED until a "
            "separate, future, explicitly human-controlled step is supplied."
        ),
        "human_operator_required_next_steps": [
            "A human reviews this read-only boundary decision packet.",
            "A human separately selects exactly one allowed option; the highest "
            "permitted option only authorizes building one more read-only "
            "research contract.",
            "Any forbidden option (unlock, fetch, run QA, broker / exchange, "
            "credentials, runtime / dashboard / storage write, trade signal / "
            "order) is rejected and performs nothing.",
        ],
        "requires_separate_future_human_controlled_step": True,
        "human_decision_required": True,
        "this_packet_authorizes_boundary_crossing": False,
        "highest_option_authorizes_only_read_only_contract": True,
        "safety_posture": dict(PACKET_SAFETY_POSTURE),
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
        "authorizes_nothing": True,
        "unlocks_real_data_qa": False,
        "unlocks_baseline_backtest": False,
        "unlocks_paper_trading": False,
        "unlocks_micro_live": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return packet


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
_REQUIRED_PACKET_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "mode",
    "core_rule",
    "mission_flow_current_stage",
    "mission_flow_next_required_action",
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
    "boundary_truth",
    "evidence_completed",
    "missing_requirements",
    "allowed_decision_options",
    "forbidden_decision_options",
    "requested_decision_assessment",
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


def validate_real_data_qa_boundary_decision_packet(
    packet: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built boundary decision packet. Returns a verdict
    dict of boolean checks plus an overall `valid`."""
    c = packet if isinstance(packet, dict) else {}
    missing_fields = [f for f in _REQUIRED_PACKET_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == PACKET_SCHEMA_VERSION
    label_ok = c.get("label") == PACKET_LABEL
    status_ok = c.get("status") == PACKET_STATUS
    mode_ok = c.get("mode") == PACKET_MODE
    core_rule_ok = c.get("core_rule") == PACKET_CORE_RULE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    human_required = c.get("human_approval_required") is True
    human_decision_required = c.get("human_decision_required") is True
    future_step_required = (
        c.get("requires_separate_future_human_controlled_step") is True
    )
    no_boundary_crossing = (
        c.get("this_packet_authorizes_boundary_crossing") is False
    )
    highest_option_bounded = (
        c.get("highest_option_authorizes_only_read_only_contract") is True
    )
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == PACKET_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
        and c.get("real_strategy_intake_state") == "BLOCKED"
    )

    bd = c.get("boundary_decision")
    bd_is_dict = isinstance(bd, dict)
    boundary_keys_ok = bd_is_dict and all(
        k in bd for k in _REQUIRED_BOUNDARY_KEYS
    )
    parked_refs_ok = bd_is_dict and (
        bd.get("parked_stage") == MISSION_FLOW_CURRENT_STAGE
        and bd.get("parked_next_required_action") == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    evidence_ok = bd_is_dict and (
        isinstance(bd.get("evidence_completed"), list)
        and len(bd.get("evidence_completed") or []) == len(EVIDENCE_COMPLETED)
        and all(
            isinstance(item, dict) and {"label", "state", "description"} <= set(item)
            for item in (bd.get("evidence_completed") or [])
        )
    )
    missing_ok = bd_is_dict and (
        isinstance(bd.get("missing_requirements"), list)
        and len(bd.get("missing_requirements") or []) == len(MISSING_REQUIREMENTS)
        and all(
            isinstance(item, dict) and {"requirement", "description"} <= set(item)
            for item in (bd.get("missing_requirements") or [])
        )
    )
    allowed_options_ok = bd_is_dict and (
        isinstance(bd.get("allowed_decision_options"), list)
        and [o.get("id") for o in (bd.get("allowed_decision_options") or [])]
        == list(ALLOWED_DECISION_OPTION_IDS)
        and all(
            o.get("recommendation_only") is True
            and o.get("authorizes_execution") is False
            and o.get("crosses_boundary") is False
            for o in (bd.get("allowed_decision_options") or [])
        )
    )
    forbidden_options_ok = bd_is_dict and (
        isinstance(bd.get("forbidden_decision_options"), list)
        and [o.get("id") for o in (bd.get("forbidden_decision_options") or [])]
        == list(FORBIDDEN_DECISION_OPTION_IDS)
        and all(
            o.get("rejected") is True
            for o in (bd.get("forbidden_decision_options") or [])
        )
    )

    rda = bd.get("requested_decision_assessment") if bd_is_dict else None
    requested_assessment_ok = isinstance(rda, dict) and (
        rda.get("authorizes_execution") is False
        and rda.get("crosses_boundary") is False
        and rda.get("recommendation_only") is True
    )

    nuc = bd.get("no_unlock_confirmation") if bd_is_dict else None
    no_unlock_ok = isinstance(nuc, dict) and (
        nuc.get("unlocks_real_data_qa") is False
        and nuc.get("unlocks_baseline_backtest") is False
        and nuc.get("unlocks_paper_trading") is False
        and nuc.get("unlocks_micro_live") is False
        and nuc.get("real_data_qa_state") == "BLOCKED"
        and nuc.get("baseline_backtest_state") == "BLOCKED"
        and nuc.get("paper_live_state") == "LOCKED"
    )

    no_secret_value_fields = not _has_secret_value(c)

    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "packet_summary", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(PACKET_FORBIDDEN_TRADE_TERMS))

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
        "highest_option_bounded": highest_option_bounded,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "boundary_keys_ok": boundary_keys_ok,
        "parked_refs_ok": parked_refs_ok,
        "evidence_ok": evidence_ok,
        "missing_ok": missing_ok,
        "allowed_options_ok": allowed_options_ok,
        "forbidden_options_ok": forbidden_options_ok,
        "requested_assessment_ok": requested_assessment_ok,
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


def render_real_data_qa_boundary_decision_packet_markdown(
    packet: Any,
) -> str:
    """Render a built boundary decision packet as a deterministic markdown brief.
    Pure string formatting; writes nothing."""
    c = packet if isinstance(packet, dict) else {}
    bd = c.get("boundary_decision") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Real Data QA Boundary Decision Packet")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Authorizes boundary crossing: "
        + str(c.get("this_packet_authorizes_boundary_crossing", False))
    )
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(
        lines,
        "Boundary Truth",
        [
            str(pair[0]) + ": " + str(pair[1])
            for pair in (bd.get("boundary_truth") or [])
        ],
    )
    _emit(
        lines,
        "Evidence Completed",
        [
            str(item.get("label"))
            + " ("
            + str(item.get("state"))
            + "): "
            + str(item.get("description"))
            for item in (bd.get("evidence_completed") or [])
        ],
    )
    _emit(
        lines,
        "Missing Requirements Before Real Data QA",
        [
            str(item.get("requirement")) + ": " + str(item.get("description"))
            for item in (bd.get("missing_requirements") or [])
        ],
    )
    _emit(
        lines,
        "Allowed Decision Options (recommendations only)",
        [
            str(item.get("id")) + ": " + str(item.get("summary"))
            for item in (bd.get("allowed_decision_options") or [])
        ],
    )
    _emit(
        lines,
        "Forbidden Decision Options (always rejected)",
        [
            str(item.get("id")) + ": " + str(item.get("why_forbidden"))
            for item in (bd.get("forbidden_decision_options") or [])
        ],
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

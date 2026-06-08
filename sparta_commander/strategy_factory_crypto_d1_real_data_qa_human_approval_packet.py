"""Crypto-D1 Real Data QA Boundary Decision -- Human Approval Packet (Block 155).

A PURE, stdlib-only, *read-only* DECISION-BRIEFING packet. It is the single
document a human operator reads at the parked mission-flow boundary

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

before deciding whether to allow the FIRST controlled, read-only Real Data QA
step. It is NOT the eight-field approval FORM (that is the Block 136 contract,
`...real_data_qa_human_approval_packet_contract`), and it is NOT a specific fetch
run spec (that is the Block 144 packet). It is the boundary DECISION briefing:
it states where the chain is parked, confirms the read-only provider / adapter /
autopilot stack (Blocks 152 / 153 / 154) is shipped, registered, and reflected
in the UI, names precisely what a SEPARATE future human approval would permit,
and names precisely what stays forbidden.

THIS packet executes NOTHING. It does NOT fetch, acquire, download, inspect,
read, or transform any data, runs no QA, no baseline, no backtest, no
simulation, touches no broker / exchange / order / account / paper / live
surface, activates no automation / autopilot, performs no auto-push, opens no
network, reads no .env, inspects no credential, prints / logs / stores no
secret, reads or writes no file, spawns no subprocess, reads no environment
variable, mints no id, and records no timestamp. It only assembles a static,
deterministic briefing document and emits it for human review.

CORE RULE: assembling or reading this packet authorizes nothing and crosses no
real-world boundary. real_data_qa stays BLOCKED, baseline stays BLOCKED, and
paper / micro-live stay LOCKED. The human boundary decision this packet briefs
is a SEPARATE, future, explicitly human-approved action; even granting it would
permit only the FIRST controlled, read-only Real Data QA step and would unlock
no downstream gate.

Public API:
  - PACKET_SCHEMA_VERSION / PACKET_LABEL / PACKET_STATUS / PACKET_MODE / PACKET_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - PREREQUISITE_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_LABEL
  - PREREQUISITE_BLOCKS
  - WHAT_HUMAN_APPROVAL_WOULD_PERMIT / WHAT_REMAINS_FORBIDDEN
  - PACKET_FORBIDDEN_FLAGS / PACKET_FORBIDDEN_TRADE_TERMS
  - PACKET_SAFETY_POSTURE / DEFAULT_PACKET_INPUT
  - build_real_data_qa_boundary_decision_human_approval_packet(payload=None)
  - validate_real_data_qa_boundary_decision_human_approval_packet(packet)
  - render_real_data_qa_boundary_decision_human_approval_packet_markdown(packet)
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
    "strategy_factory_crypto_d1_real_data_qa_human_approval_packet.v1"
)
PACKET_LABEL = (
    "Block 155 - Crypto-D1 Real Data QA Boundary Decision Human Approval Packet"
)
PACKET_STATUS = "HUMAN_APPROVAL_PACKET_ONLY"
PACKET_MODE = "RESEARCH_ONLY"

PACKET_CORE_RULE = (
    "This packet is the human-facing decision briefing for the parked real data "
    "QA boundary. Assembling or reading it authorizes nothing and crosses no "
    "real-world boundary: no data is fetched or inspected, no QA / baseline / "
    "backtest is run, no broker / exchange / order surface is touched, no "
    "automation or auto-push fires, no network is opened, no credential or .env "
    "is read, and no secret is shown. The human boundary decision it briefs is a "
    "SEPARATE, future, explicitly human-approved action; even granting it would "
    "permit only the FIRST controlled, read-only Real Data QA step. real_data_qa "
    "stays BLOCKED, baseline stays BLOCKED, and paper / micro-live stay LOCKED."
)

# The read-only provider / adapter / autopilot stack this boundary follows. The
# label string mirrors the live registry's registered Block 152 label; the
# companion test cross-checks it against the live status module.
PREREQUISITE_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_LABEL = (
    "Block 152 - SPARTA Overnight Research Autopilot Controller"
)

# Each prerequisite: (block, state, description). These are facts about prior,
# already-completed work; this packet asserts them, it does not perform them.
PREREQUISITE_BLOCKS: tuple[tuple[str, str, str], ...] = (
    (
        "Block 152",
        "shipped",
        "SPARTA Overnight Research Autopilot Controller -- a research-only "
        "planner that authorizes nothing, executes nothing, and performs no "
        "auto-push.",
    ),
    (
        "Block 153",
        "registered",
        "The controller is registered complete in the mission-flow backend as "
        "an additive side-lane that does NOT advance the human-controlled real "
        "data QA boundary.",
    ),
    (
        "Block 154",
        "reflected",
        "The JARVIS mission-flow UI panel reflects the controller as "
        "complete / registered while the chain stays parked at the boundary, "
        "with no execution or autopilot-activation controls.",
    ),
)

# Exactly what a SEPARATE, future, explicitly human-approved boundary decision
# WOULD permit. Deliberately narrow: planning the first controlled, read-only QA
# step on data already on disk. Nothing here is permitted by THIS packet.
WHAT_HUMAN_APPROVAL_WOULD_PERMIT: tuple[str, ...] = (
    "Begin PLANNING the first controlled, read-only Real Data QA step over "
    "Crypto-D1 daily data that is already on disk -- scope, checks, and stop "
    "conditions only.",
    "Define which read-only data-quality checks (schema, nulls, duplicates, "
    "timestamp monotonicity, gaps, range sanity, row counts, symbol coverage) "
    "would be allowed in that first step.",
    "Require a separate, future, explicitly human-approved review before any "
    "such QA step is actually run.",
)

# Exactly what stays forbidden at and beyond this boundary, regardless of any
# input. This packet enforces none of these by executing; it only states them.
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
    "No gate unlock of real_data_qa, baseline, paper, or micro-live.",
)

# Top-level flags that, if truthy on an operator's input, mark it unsafe. Any of
# these means the caller tried to bend this briefing into an authorization.
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
    "fetch_data_now",
    "activate_autopilot",
    "enable_auto_push",
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
    "human_approval_packet_only": True,
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
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}

# Deterministic static input. No real data, no secret, no authorization flag.
DEFAULT_PACKET_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 real data QA boundary decision packet input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
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
# packet build
# --------------------------------------------------------------------------- #
def _prerequisite_records() -> list[dict[str, Any]]:
    return [
        {"block": block, "state": state, "description": desc}
        for block, state, desc in PREREQUISITE_BLOCKS
    ]


def build_real_data_qa_boundary_decision_human_approval_packet(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only boundary-decision human approval
    packet. Every capability / execution flag is False and every gate lock is
    True regardless of input. The packet authorizes nothing and unlocks nothing."""
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
    safe = mission_flow_aligned and not forbidden_flag_hits

    boundary_decision = {
        "parked_stage": MISSION_FLOW_CURRENT_STAGE,
        "parked_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "prerequisite_stack_label": (
            "Read-only provider / adapter / autopilot stack "
            "(Blocks 152 / 153 / 154)"
        ),
        "prerequisite_blocks": _prerequisite_records(),
        "what_human_approval_would_permit": list(WHAT_HUMAN_APPROVAL_WOULD_PERMIT),
        "what_remains_forbidden": list(WHAT_REMAINS_FORBIDDEN),
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
        "prerequisite_overnight_research_autopilot_controller_label": (
            PREREQUISITE_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER_LABEL
        ),
        "prerequisite_block_152_shipped": True,
        "prerequisite_block_153_registered": True,
        "prerequisite_block_154_reflected": True,
        "packet_summary": (
            "Boundary decision briefing: the Crypto-D1 chain is parked at the "
            "human-controlled real data QA boundary. The read-only provider / "
            "adapter / autopilot stack (Blocks 152 / 153 / 154) is shipped, "
            "registered, and reflected in the UI. This packet states what a "
            "separate future human approval would permit and what stays "
            "forbidden. It fetches nothing, inspects nothing, runs nothing, and "
            "unlocks nothing."
        ),
        "operator_next_step": (
            "A human reviews this briefing and, as a SEPARATE action, decides "
            "whether to permit PLANNING the first controlled, read-only Real "
            "Data QA step. Reading this packet acquires no data, runs nothing, "
            "and unlocks no gate; real_data_qa stays BLOCKED until a separate, "
            "future, explicitly human-approved step is supplied."
        ),
        "human_operator_required_next_steps": [
            "A human reviews this read-only boundary decision briefing.",
            "A human separately decides whether to permit planning the first "
            "controlled, read-only Real Data QA step.",
            "A separate, future, explicitly human-approved review is required "
            "before any Real Data QA step is run; this packet supplies none of "
            "it.",
        ],
        "requires_separate_future_human_approved_step": True,
        "human_decision_required": True,
        "this_packet_authorizes_boundary_crossing": False,
        "safety_posture": dict(PACKET_SAFETY_POSTURE),
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
    "prerequisite_stack_label",
    "prerequisite_blocks",
    "what_human_approval_would_permit",
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


def validate_real_data_qa_boundary_decision_human_approval_packet(
    packet: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built boundary-decision packet. Returns a verdict
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
        c.get("requires_separate_future_human_approved_step") is True
    )
    no_boundary_crossing = (
        c.get("this_packet_authorizes_boundary_crossing") is False
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
    )

    prerequisites_confirmed = (
        c.get("prerequisite_block_152_shipped") is True
        and c.get("prerequisite_block_153_registered") is True
        and c.get("prerequisite_block_154_reflected") is True
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
    prerequisite_blocks_ok = bd_is_dict and (
        isinstance(bd.get("prerequisite_blocks"), list)
        and len(bd.get("prerequisite_blocks") or []) == len(PREREQUISITE_BLOCKS)
        and all(
            isinstance(item, dict)
            and {"block", "state", "description"} <= set(item)
            for item in (bd.get("prerequisite_blocks") or [])
        )
    )
    would_permit_ok = bd_is_dict and bool(
        bd.get("what_human_approval_would_permit")
    )
    remains_forbidden_ok = bd_is_dict and bool(bd.get("what_remains_forbidden"))

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

    # authored narrative must carry no execution / trade verbs as whole words.
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
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "prerequisites_confirmed": prerequisites_confirmed,
        "boundary_keys_ok": boundary_keys_ok,
        "parked_refs_ok": parked_refs_ok,
        "prerequisite_blocks_ok": prerequisite_blocks_ok,
        "would_permit_ok": would_permit_ok,
        "remains_forbidden_ok": remains_forbidden_ok,
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


def render_real_data_qa_boundary_decision_human_approval_packet_markdown(
    packet: Any,
) -> str:
    """Render a built boundary-decision packet as a deterministic markdown
    brief. Pure string formatting; writes nothing."""
    c = packet if isinstance(packet, dict) else {}
    bd = c.get("boundary_decision") or {}
    lines: list[str] = []
    lines.append(
        "# Crypto-D1 Real Data QA Boundary Decision Human Approval Packet"
    )
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Authorizes boundary crossing: "
        + str(c.get("this_packet_authorizes_boundary_crossing", False))
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

    _emit(
        lines,
        "Prerequisite Stack (shipped / registered / reflected)",
        [
            str(item.get("block"))
            + " ("
            + str(item.get("state"))
            + "): "
            + str(item.get("description"))
            for item in (bd.get("prerequisite_blocks") or [])
        ],
    )
    _emit(
        lines,
        "What Human Approval Would Permit",
        list(bd.get("what_human_approval_would_permit") or []),
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

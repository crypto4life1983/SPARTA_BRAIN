"""SPARTA Research Bundle Automation Controller (Block 137).

A PURE, stdlib-only, *read-only* RESEARCH_ONLY workflow controller. Its only job
is to reduce manual operator fatigue when running the SPARTA bundle workflow by
reasoning over a static, caller-supplied mission-flow status summary and telling
the operator -- on paper only -- what the next SAFE research-only step is, which
paths it may touch, which it may not, which scoped tests to run, and what hard
stops apply. It is an advisor, not an actor.

    MISSION_FLOW_CURRENT_STAGE  = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION    = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

It automates ONLY safe research workflow checks and approval packets. It does NOT
automate -- and this controller is structurally incapable of performing -- any of
the following: trading, data acquisition, QA, backtest, broker/exchange, paper or
live trading, runtime/dashboard writes, or gate unlocks.

Hard safety rules (the controller NEVER does any of these): execute git commands,
stage files, commit, push, fetch data, run QA/backtest, call broker/exchange,
place orders, trigger paper/live trading, write runtime/dashboard outputs, unlock
real_data_qa, unlock baseline_backtest, unlock paper/micro-live, or turn any
real-world capability flag True. It executes NOTHING: it opens no file, no
network, no subprocess, reads no environment, uses no credential, mints no id, and
records no timestamp. It only reasons over a static dict.

CORE RULE: this controller NEVER crosses a real-world boundary. When the mission
flow is at the Real Data QA boundary (or any unsafe flag is present), it refuses
automation: automation_allowed is False, the recommendation is to HOLD or prepare
a research-only packet, real_data_qa stays BLOCKED, and paper/live stays LOCKED.

Next-action categories (exactly one is chosen, by precedence):
  - HOLD                            : an unsafe / forbidden flag was present, or
                                      there is no safe automated step right now.
  - HUMAN_BOUNDARY_DECISION_REQUIRED: the mission flow sits at the human-controlled
                                      Real Data QA boundary -- only a human may
                                      decide; the controller holds.
  - UI_SYNC_REQUIRED               : a display/dashboard sync is pending. The
                                      controller will NOT perform it (dashboard
                                      write); it only flags it for a human.
  - REGISTER_RESEARCH_CONTRACT     : a built research-only paper contract still
                                      needs registering in the mission flow.
  - BUILD_RESEARCH_CONTRACT        : the next research-only paper contract has not
                                      been built yet.

automation_allowed is True ONLY for the two pure research-only paper steps
(BUILD_RESEARCH_CONTRACT, REGISTER_RESEARCH_CONTRACT). It is False for UI sync
(a dashboard write), for the human boundary, and for any HOLD.

Public API:
  - CONTROLLER_SCHEMA_VERSION / CONTROLLER_LABEL / CONTROLLER_STATUS
  - CONTROLLER_MODE / CONTROLLER_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - NEXT_ACTION_BUILD / NEXT_ACTION_REGISTER / NEXT_ACTION_UI_SYNC
  - NEXT_ACTION_HUMAN_BOUNDARY / NEXT_ACTION_HOLD / NEXT_ACTION_CATEGORIES
  - RECOMMENDATION_HOLD_OR_PREPARE / CONTROLLER_RECOMMENDATIONS
  - REAL_DATA_QA_STATE_BLOCKED / PAPER_LIVE_STATE_LOCKED
  - CONTROLLER_FORBIDDEN_PATHS / CONTROLLER_SCOPED_TEST_SUFFIXES
  - CONTROLLER_HARD_STOP_RULES / CONTROLLER_FORBIDDEN_TRADE_TERMS
  - CONTROLLER_AUTHORIZATION_FLAGS / CONTROLLER_GATE_LOCK_FLAGS
  - CONTROLLER_GATE_UNLOCK_REQUEST_FLAGS / CONTROLLER_SAFETY_FLAGS
  - DEFAULT_CONTROLLER_INPUT
  - allowed_paths_for_bundle(bundle_type)
  - scoped_tests_for_bundle(bundle_type)
  - assess_research_bundle_automation(payload)
  - build_research_bundle_automation_decision(payload=None)
  - validate_research_bundle_automation_decision(decision)
  - render_research_bundle_automation_decision_markdown(decision)
"""

from __future__ import annotations

from typing import Any

CONTROLLER_SCHEMA_VERSION = (
    "strategy_factory_research_bundle_automation_controller.v1"
)
CONTROLLER_LABEL = "Block 137 - SPARTA Research Bundle Automation Controller"
CONTROLLER_STATUS = "READ_ONLY_RESEARCH_BUNDLE_AUTOMATION_CONTROLLER"
CONTROLLER_MODE = "RESEARCH_ONLY"

CONTROLLER_CORE_RULE = (
    "This controller NEVER crosses a real-world boundary. It automates only safe "
    "research-only workflow checks and approval packets. It never executes git, "
    "never stages, commits, or pushes, never fetches data, never runs QA or "
    "backtest, never touches a broker / exchange, never places a paper / live "
    "instruction, never writes runtime / dashboard outputs, and never unlocks "
    "real_data_qa, baseline, paper, or micro-live. At the human Real Data QA "
    "boundary it holds: automation_allowed is False, real_data_qa stays BLOCKED, "
    "and paper / live stays LOCKED."
)

# The current mission-flow truth this controller is anchored to. The companion
# test cross-checks these against the live status module so they cannot drift.
MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# Next-action categories (exactly one is chosen), in precedence order.
NEXT_ACTION_HOLD = "HOLD"
NEXT_ACTION_HUMAN_BOUNDARY = "HUMAN_BOUNDARY_DECISION_REQUIRED"
NEXT_ACTION_UI_SYNC = "UI_SYNC_REQUIRED"
NEXT_ACTION_REGISTER = "REGISTER_RESEARCH_CONTRACT"
NEXT_ACTION_BUILD = "BUILD_RESEARCH_CONTRACT"

NEXT_ACTION_CATEGORIES: tuple[str, ...] = (
    NEXT_ACTION_HOLD,
    NEXT_ACTION_HUMAN_BOUNDARY,
    NEXT_ACTION_UI_SYNC,
    NEXT_ACTION_REGISTER,
    NEXT_ACTION_BUILD,
)

# The two categories the controller may safely help automate (pure research-only
# paper steps). Everything else holds.
_AUTOMATABLE_CATEGORIES: frozenset[str] = frozenset(
    {NEXT_ACTION_BUILD, NEXT_ACTION_REGISTER}
)

# The special recommendation the controller returns at the human boundary.
RECOMMENDATION_HOLD_OR_PREPARE = "HOLD_OR_PREPARE_RESEARCH_ONLY_PACKET"

# The full set of values recommended_next_action may take.
CONTROLLER_RECOMMENDATIONS: tuple[str, ...] = (
    NEXT_ACTION_BUILD,
    NEXT_ACTION_REGISTER,
    NEXT_ACTION_UI_SYNC,
    RECOMMENDATION_HOLD_OR_PREPARE,
    NEXT_ACTION_HOLD,
)

# This controller never reports anything but blocked / locked for these.
REAL_DATA_QA_STATE_BLOCKED = "BLOCKED"
PAPER_LIVE_STATE_LOCKED = "LOCKED"

# Paths this controller must never recommend touching for a research bundle.
CONTROLLER_FORBIDDEN_PATHS: tuple[str, ...] = (
    "data/",
    "data/databento/",
    "data/databento_cache/",
    "reports/",
    "runtime/",
    "templates/",
    "static/",
    "dashboard/",
    "brain_memory/projects/trading_bot/decisions.md",
    "brain_memory/projects/trading_bot/lessons.md",
    "local_secrets/",
    "broker/",
    "exchange/",
    ".env",
)

# Filename suffixes used to derive scoped tests / module paths for a bundle.
CONTROLLER_SCOPED_TEST_SUFFIXES: tuple[str, ...] = (
    "sparta_commander/commander_2_safety.py",
)

# The verbatim hard-stop rules. The controller obeys all of them, always.
CONTROLLER_HARD_STOP_RULES: tuple[str, ...] = (
    "Never execute git commands.",
    "Never stage files.",
    "Never commit.",
    "Never push.",
    "Never fetch data.",
    "Never run QA / backtest.",
    "Never call broker / exchange.",
    "Never place orders.",
    "Never trigger paper / live trading.",
    "Never write runtime / dashboard outputs.",
    "Never unlock real_data_qa.",
    "Never unlock baseline_backtest.",
    "Never unlock paper / micro-live.",
    "Never turn any real-world capability flag True.",
)

# Execution / promotion verbs the controller's generated guidance must never
# contain as whole words.
CONTROLLER_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
    "order",
)

# Top-level flags that, if truthy in the input, force an unsafe HOLD.
CONTROLLER_AUTHORIZATION_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "authorizes_runtime_write",
    "authorizes_dashboard_write",
    "unlocks_downstream_gate",
)

# Gate-lock flags that MUST be True (blocked / locked). If present and not True,
# the input tried to unlock a gate -> unsafe HOLD.
CONTROLLER_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, force an unsafe HOLD.
CONTROLLER_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
    "force_promote",
    "promote_to_live",
    "promote_to_paper",
    "execute",
    "place_order",
    "go_live",
)

# Read-only safety flags. The posture facts are True; every capability /
# authorization / unlock flag is False.
CONTROLLER_SAFETY_FLAGS: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "human_approval_required": True,
    "executes": False,
    "runs_git": False,
    "stages_files": False,
    "commits": False,
    "pushes": False,
    "fetches_data": False,
    "runs_qa": False,
    "runs_backtest": False,
    "calls_broker_exchange": False,
    "places_orders": False,
    "triggers_paper_trading": False,
    "triggers_live_trading": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "authorizes_trading": False,
    "authorizes_data_fetch": False,
    "authorizes_backtest": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_automation": False,
    "authorizes_real_world_action": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}

# The capability flags that must ALL be False for safety_flags_all_false to hold.
_CAPABILITY_FLAGS: tuple[str, ...] = tuple(
    name for name, value in CONTROLLER_SAFETY_FLAGS.items() if value is False
)

_DEFAULT_BUNDLE_TYPE = "research_contract"


# A deterministic, illustrative paper input. It is anchored to the live mission
# flow, which sits at the human-controlled Real Data QA boundary, so the default
# decision is a HOLD at the boundary. Nothing here is real; static example only.
DEFAULT_CONTROLLER_INPUT: dict[str, Any] = {
    "label": "SPARTA research bundle automation input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "research_only": True,
    "current_stage": MISSION_FLOW_CURRENT_STAGE,
    "next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
    "next_bundle_type": _DEFAULT_BUNDLE_TYPE,
    "next_bundle_slug": "",
    "contract_built": False,
    "contract_registered": False,
    "ui_in_sync": True,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
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


def _slugify(value: Any) -> str:
    out: list[str] = []
    for ch in _norm(value):
        if ch.isalnum() or ch == "_":
            out.append(ch)
        elif ch in (" ", "-"):
            out.append("_")
    slug = "".join(out).strip("_")
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug


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


def _bundle_module_stem(bundle_type: Any, bundle_slug: Any = "") -> str:
    """Derive a research-only module stem for the next bundle. Pure string work;
    this NEVER reads the filesystem and authorizes nothing."""
    slug = _slugify(bundle_slug) or _slugify(bundle_type) or _DEFAULT_BUNDLE_TYPE
    stem = "strategy_factory_" + slug
    if not stem.endswith("_contract"):
        stem = stem + "_contract"
    return stem


def allowed_paths_for_bundle(
    bundle_type: Any, bundle_slug: Any = ""
) -> list[str]:
    """Return the ONLY paths a next research bundle may touch: its paper module,
    its test, and the additive commander_2_safety allowlist lines. Pure; reads no
    filesystem and creates nothing."""
    stem = _bundle_module_stem(bundle_type, bundle_slug)
    return [
        "sparta_commander/" + stem + ".py",
        "tests/test_" + stem + ".py",
        "sparta_commander/commander_2_safety.py (additive allowlist lines only)",
    ]


def scoped_tests_for_bundle(
    bundle_type: Any, bundle_slug: Any = ""
) -> list[str]:
    """Return the scoped tests to run for a next research bundle: its own test
    plus the commander_2_safety allowlist test. Pure string work."""
    stem = _bundle_module_stem(bundle_type, bundle_slug)
    return [
        "tests/test_" + stem + ".py",
        "tests/test_sparta_commander_2_safety.py",
    ]


def _unsafe_flag_hits(payload: dict[str, Any]) -> list[str]:
    """Collect any input keys that attempt to authorize, unlock, or promote a
    real-world capability. Any hit forces an unsafe HOLD."""
    hits: list[str] = []
    for flag in CONTROLLER_AUTHORIZATION_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in CONTROLLER_GATE_UNLOCK_REQUEST_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in CONTROLLER_GATE_LOCK_FLAGS:
        if flag in payload and not _is_truthy(payload.get(flag)):
            hits.append("unlocked:" + flag)
    seen: set[str] = set()
    ordered: list[str] = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            ordered.append(h)
    return ordered


def _at_boundary(payload: dict[str, Any]) -> bool:
    stage = payload.get("current_stage", MISSION_FLOW_CURRENT_STAGE)
    action = payload.get("next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION)
    return (
        str(stage) == MISSION_FLOW_CURRENT_STAGE
        or str(action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )


# --------------------------------------------------------------------------- #
# assessment
# --------------------------------------------------------------------------- #
def assess_research_bundle_automation(payload: Any) -> dict[str, Any]:
    """Assess (read-only) what the next SAFE research-only step is. Returns a fresh
    dict every call. Authorizes nothing and unlocks nothing under any outcome."""
    data = _as_payload(payload)
    unsafe_hits = _unsafe_flag_hits(data)
    at_boundary = _at_boundary(data)

    bundle_type = data.get("next_bundle_type", _DEFAULT_BUNDLE_TYPE)
    bundle_slug = data.get("next_bundle_slug", "")
    contract_built = _is_truthy(data.get("contract_built"))
    contract_registered = _is_truthy(data.get("contract_registered"))
    ui_in_sync = _is_truthy(data.get("ui_in_sync"))

    # Precedence: unsafe -> boundary -> build -> register -> ui sync -> hold.
    if unsafe_hits:
        category = NEXT_ACTION_HOLD
        reason = (
            "Refusing automation: a forbidden authorization / unlock / promotion "
            "flag was present (" + ", ".join(unsafe_hits) + ")."
        )
    elif at_boundary:
        category = NEXT_ACTION_HUMAN_BOUNDARY
        reason = (
            "Mission flow sits at the human-controlled Real Data QA boundary. "
            "Only a human may decide; the controller holds."
        )
    elif not contract_built:
        category = NEXT_ACTION_BUILD
        reason = (
            "The next research-only paper contract has not been built yet."
        )
    elif not contract_registered:
        category = NEXT_ACTION_REGISTER
        reason = (
            "A built research-only paper contract still needs registering in the "
            "mission flow."
        )
    elif not ui_in_sync:
        category = NEXT_ACTION_UI_SYNC
        reason = (
            "A display / dashboard sync is pending. The controller will not "
            "perform it; it only flags it for a human."
        )
    else:
        category = NEXT_ACTION_HOLD
        reason = "No safe automated research step is pending right now."

    automation_allowed = category in _AUTOMATABLE_CATEGORIES

    if category == NEXT_ACTION_HUMAN_BOUNDARY:
        recommended = RECOMMENDATION_HOLD_OR_PREPARE
    elif category == NEXT_ACTION_HOLD:
        recommended = NEXT_ACTION_HOLD
    elif category == NEXT_ACTION_UI_SYNC:
        recommended = NEXT_ACTION_UI_SYNC
    else:
        recommended = category

    return {
        "mode": CONTROLLER_MODE,
        "next_action_category": category,
        "recommended_next_action": recommended,
        "automation_allowed": automation_allowed,
        "at_boundary": at_boundary,
        "unsafe_flag_hits": list(unsafe_hits),
        "reason": reason,
        "next_bundle_type": str(bundle_type),
        "next_bundle_slug": str(bundle_slug),
        "contract_built": contract_built,
        "contract_registered": contract_registered,
        "ui_in_sync": ui_in_sync,
        "real_data_qa_state": REAL_DATA_QA_STATE_BLOCKED,
        "paper_live_state": PAPER_LIVE_STATE_LOCKED,
        "crosses_boundary": False,
        "unlocks_real_data_qa": False,
        "authorizes_nothing": True,
    }


# --------------------------------------------------------------------------- #
# decision build
# --------------------------------------------------------------------------- #
def _approval_packet_text(assessment: dict[str, Any]) -> str:
    """Deterministic research-only approval-packet text. Carries no execution or
    trade verbs and authorizes nothing."""
    category = assessment["next_action_category"]
    recommended = assessment["recommended_next_action"]
    lines = [
        "RESEARCH-ONLY NEXT-STEP PACKET",
        "Recommended next action: " + recommended,
        "Automation allowed: " + str(assessment["automation_allowed"]),
        "Reason: " + assessment["reason"],
        "real_data_qa state: " + REAL_DATA_QA_STATE_BLOCKED,
        "paper / live state: " + PAPER_LIVE_STATE_LOCKED,
    ]
    if category == NEXT_ACTION_HUMAN_BOUNDARY:
        lines.append(
            "Hold here. A human must make the Real Data QA boundary decision. "
            "Prepare a research-only packet if helpful, but cross nothing."
        )
    elif category == NEXT_ACTION_HOLD:
        lines.append(
            "Hold. There is no safe automated research step to prepare right now."
        )
    elif category == NEXT_ACTION_UI_SYNC:
        lines.append(
            "A display sync is pending. Flag it for a human; the controller "
            "writes no dashboard output."
        )
    else:
        lines.append(
            "This is a pure research-only paper step. Prepare the packet, run the "
            "scoped tests, and await explicit human approval before any commit."
        )
    lines.append(
        "This packet authorizes nothing. No git, no data, no QA, no backtest, no "
        "broker / exchange, no paper / live, no runtime / dashboard write, no gate "
        "unlock occurs."
    )
    return "\n".join(lines)


def _operator_checklist(assessment: dict[str, Any]) -> list[str]:
    """Deterministic operator checklist for the recommended step."""
    checklist = [
        "Confirm the mission-flow truth is unchanged (stage and next action).",
        "Confirm real_data_qa is BLOCKED and paper / live is LOCKED.",
        "Confirm no authorization / unlock / promotion flag is set.",
    ]
    category = assessment["next_action_category"]
    if assessment["automation_allowed"]:
        checklist.extend(
            [
                "Confirm the next step touches only the allowed paths.",
                "Run only the scoped tests listed below.",
                "Do not stage, commit, or push without explicit human approval.",
            ]
        )
    elif category == NEXT_ACTION_HUMAN_BOUNDARY:
        checklist.append(
            "Hold at the boundary; escalate to a human for the decision."
        )
    elif category == NEXT_ACTION_UI_SYNC:
        checklist.append(
            "Hand the display sync to a human; the controller writes no UI."
        )
    else:
        checklist.append("Hold; re-check the mission flow before any action.")
    return checklist


def _commit_push_verification_checklist() -> list[str]:
    """Deterministic verification checklist the operator (a human) uses BEFORE any
    commit / push. The controller itself never performs these steps."""
    return [
        "A human reviews the exact changed paths against the allowed-paths list.",
        "A human confirms decisions.md and lessons.md are not staged.",
        "A human confirms no data / reports / runtime / dashboard files are staged.",
        "A human confirms the scoped tests pass.",
        "A human confirms the mission-flow truth is unchanged after the change.",
        "A human explicitly approves before any commit, and again before any push.",
    ]


def build_research_bundle_automation_decision(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only automation decision record. Every
    capability flag is False and every gate lock is reported blocked / locked
    regardless of the assessed category."""
    data = (
        dict(DEFAULT_CONTROLLER_INPUT) if payload is None else _as_payload(payload)
    )
    assessment = assess_research_bundle_automation(data)

    bundle_type = assessment["next_bundle_type"]
    bundle_slug = assessment["next_bundle_slug"]
    allowed = allowed_paths_for_bundle(bundle_type, bundle_slug)
    scoped = scoped_tests_for_bundle(bundle_type, bundle_slug)
    safety_flags_all_false = all(
        CONTROLLER_SAFETY_FLAGS[name] is False for name in _CAPABILITY_FLAGS
    )

    decision: dict[str, Any] = {
        "schema_version": CONTROLLER_SCHEMA_VERSION,
        "label": CONTROLLER_LABEL,
        "status": CONTROLLER_STATUS,
        "mode": CONTROLLER_MODE,
        "core_rule": CONTROLLER_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "at_boundary": assessment["at_boundary"],
        "next_action_categories": list(NEXT_ACTION_CATEGORIES),
        "next_action_category": assessment["next_action_category"],
        "recommendations": list(CONTROLLER_RECOMMENDATIONS),
        # ---- the spec's expected outputs ----
        "automation_allowed": assessment["automation_allowed"],
        "recommended_next_action": assessment["recommended_next_action"],
        "approval_packet_text": _approval_packet_text(assessment),
        "allowed_paths": allowed,
        "forbidden_paths": list(CONTROLLER_FORBIDDEN_PATHS),
        "scoped_tests": scoped,
        "hard_stop_rules": list(CONTROLLER_HARD_STOP_RULES),
        "safety_flags_all_false": safety_flags_all_false,
        "real_data_qa_state": REAL_DATA_QA_STATE_BLOCKED,
        "paper_live_state": PAPER_LIVE_STATE_LOCKED,
        "operator_summary": (
            assessment["recommended_next_action"]
            + " - "
            + assessment["reason"]
            + " real_data_qa stays "
            + REAL_DATA_QA_STATE_BLOCKED
            + "; paper / live stays "
            + PAPER_LIVE_STATE_LOCKED
            + "."
        ),
        # ---- supporting detail ----
        "reason": assessment["reason"],
        "unsafe_flag_hits": list(assessment["unsafe_flag_hits"]),
        "operator_checklist": _operator_checklist(assessment),
        "commit_push_verification_checklist": (
            _commit_push_verification_checklist()
        ),
        "assessment": assessment,
        "safety_flags": dict(CONTROLLER_SAFETY_FLAGS),
        "human_approval_required": True,
        "requires_separate_future_human_approved_step": True,
        "read_only": True,
        "executes": False,
        "research_only": True,
        "runs_git": False,
        "stages_files": False,
        "commits": False,
        "pushes": False,
        "fetches_data": False,
        "runs_qa": False,
        "runs_backtest": False,
        "calls_broker_exchange": False,
        "places_orders": False,
        "triggers_paper_trading": False,
        "triggers_live_trading": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
        "authorizes_trading": False,
        "authorizes_data_fetch": False,
        "authorizes_backtest": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "authorizes_broker_exchange": False,
        "authorizes_automation": False,
        "authorizes_real_world_action": False,
        "authorizes_nothing": True,
        "unlocks_real_data_qa": False,
        "unlocks_baseline_backtest": False,
        "unlocks_paper_trading": False,
        "unlocks_micro_live": False,
        "crosses_boundary": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return decision


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
    "automation_allowed",
    "recommended_next_action",
    "approval_packet_text",
    "allowed_paths",
    "forbidden_paths",
    "scoped_tests",
    "hard_stop_rules",
    "safety_flags_all_false",
    "real_data_qa_state",
    "paper_live_state",
    "operator_summary",
    "safety_flags",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "runs_git",
    "stages_files",
    "commits",
    "pushes",
    "fetches_data",
    "runs_qa",
    "runs_backtest",
    "calls_broker_exchange",
    "places_orders",
    "triggers_paper_trading",
    "triggers_live_trading",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "unlocks_real_data_qa",
    "unlocks_baseline_backtest",
    "unlocks_paper_trading",
    "unlocks_micro_live",
    "crosses_boundary",
)

_ALL_GATE_LOCKS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def validate_research_bundle_automation_decision(
    decision: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built decision. Returns a verdict dict of boolean
    checks plus an overall `valid`."""
    d = decision if isinstance(decision, dict) else {}
    missing = [f for f in _REQUIRED_DECISION_FIELDS if f not in d]

    schema_ok = d.get("schema_version") == CONTROLLER_SCHEMA_VERSION
    label_ok = d.get("label") == CONTROLLER_LABEL
    mode_ok = d.get("mode") == CONTROLLER_MODE
    core_rule_ok = d.get("core_rule") == CONTROLLER_CORE_RULE
    read_only = d.get("read_only") is True
    research_only = d.get("research_only") is True
    executes_false = d.get("executes") is False
    human_required = d.get("human_approval_required") is True
    future_step_required = (
        d.get("requires_separate_future_human_approved_step") is True
    )
    mission_flow_refs_ok = (
        d.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and d.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    recommendation_ok = (
        d.get("recommended_next_action") in CONTROLLER_RECOMMENDATIONS
    )
    category_ok = d.get("next_action_category") in NEXT_ACTION_CATEGORIES
    hard_stops_ok = (
        tuple(d.get("hard_stop_rules") or ()) == CONTROLLER_HARD_STOP_RULES
    )
    flags_false = all(d.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    safety_flags_all_false_ok = d.get("safety_flags_all_false") is True
    authorizes_nothing = d.get("authorizes_nothing") is True
    gates_locked = all(d.get(g) is True for g in _ALL_GATE_LOCKS)
    safety_flags_ok = d.get("safety_flags") == CONTROLLER_SAFETY_FLAGS
    states_blocked_locked = (
        d.get("real_data_qa_state") == REAL_DATA_QA_STATE_BLOCKED
        and d.get("paper_live_state") == PAPER_LIVE_STATE_LOCKED
    )

    # automation_allowed may be True ONLY for the two automatable categories.
    automation_value = d.get("automation_allowed")
    automation_consistent = (automation_value is True) == (
        d.get("next_action_category") in _AUTOMATABLE_CATEGORIES
    )

    # at the human boundary, automation must be False and the recommendation must
    # be the hold-or-prepare packet recommendation.
    boundary_hold_ok = True
    if d.get("next_action_category") == NEXT_ACTION_HUMAN_BOUNDARY:
        boundary_hold_ok = (
            d.get("automation_allowed") is False
            and d.get("recommended_next_action") == RECOMMENDATION_HOLD_OR_PREPARE
            and d.get("real_data_qa_state") == REAL_DATA_QA_STATE_BLOCKED
            and d.get("paper_live_state") == PAPER_LIVE_STATE_LOCKED
        )

    allowed_paths = d.get("allowed_paths")
    allowed_paths_ok = isinstance(allowed_paths, list) and bool(allowed_paths)
    # no allowed path may fall under a forbidden path prefix.
    forbidden = tuple(d.get("forbidden_paths") or ())
    no_forbidden_in_allowed = allowed_paths_ok and not any(
        str(p).startswith(f) for p in allowed_paths for f in forbidden
    )

    scoped_tests = d.get("scoped_tests")
    scoped_tests_ok = isinstance(scoped_tests, list) and bool(scoped_tests)

    # generated guidance must carry no execution / trade verbs as whole words.
    guidance_blob = " ".join(
        str(d.get(k, ""))
        for k in (
            "approval_packet_text",
            "operator_summary",
            "core_rule",
            "reason",
        )
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (d.get("operator_checklist") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(CONTROLLER_FORBIDDEN_TRADE_TERMS))

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "mode_ok": mode_ok,
        "core_rule_ok": core_rule_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "human_required": human_required,
        "future_step_required": future_step_required,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "recommendation_ok": recommendation_ok,
        "category_ok": category_ok,
        "hard_stops_ok": hard_stops_ok,
        "flags_false": flags_false,
        "safety_flags_all_false_ok": safety_flags_all_false_ok,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "safety_flags_ok": safety_flags_ok,
        "states_blocked_locked": states_blocked_locked,
        "automation_consistent": automation_consistent,
        "boundary_hold_ok": boundary_hold_ok,
        "allowed_paths_ok": allowed_paths_ok,
        "no_forbidden_in_allowed": no_forbidden_in_allowed,
        "scoped_tests_ok": scoped_tests_ok,
        "no_trade_language": no_trade_language,
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


def render_research_bundle_automation_decision_markdown(
    decision: Any,
) -> str:
    """Render a built decision as a deterministic markdown brief. Pure string
    formatting; writes nothing."""
    d = decision if isinstance(decision, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Research Bundle Automation Controller")
    lines.append("")
    lines.append("- Label: " + str(d.get("label", "")))
    lines.append("- Mode: " + str(d.get("mode", "")))
    lines.append("- Status: " + str(d.get("status", "")))
    lines.append(
        "- Recommended next action: "
        + str(d.get("recommended_next_action", ""))
    )
    lines.append("- Automation allowed: " + str(d.get("automation_allowed", False)))
    lines.append(
        "- Mission flow stage: " + str(d.get("mission_flow_current_stage", ""))
    )
    lines.append("- real_data_qa state: " + str(d.get("real_data_qa_state", "")))
    lines.append("- paper / live state: " + str(d.get("paper_live_state", "")))
    lines.append(
        "- safety_flags_all_false: " + str(d.get("safety_flags_all_false", False))
    )

    _emit(lines, "Operator Summary", [str(d.get("operator_summary", ""))])
    _emit(lines, "Allowed Paths", list(d.get("allowed_paths") or []))
    _emit(lines, "Forbidden Paths", list(d.get("forbidden_paths") or []))
    _emit(lines, "Scoped Tests", list(d.get("scoped_tests") or []))
    _emit(lines, "Operator Checklist", list(d.get("operator_checklist") or []))
    _emit(
        lines,
        "Commit / Push Verification Checklist",
        list(d.get("commit_push_verification_checklist") or []),
    )
    _emit(lines, "Hard Stop Rules", list(d.get("hard_stop_rules") or []))
    _emit(
        lines,
        "Approval Packet",
        list(str(d.get("approval_packet_text", "")).splitlines()),
    )
    return "\n".join(lines)

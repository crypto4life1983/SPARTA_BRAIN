"""SPARTA Overnight Research Autopilot Controller (Block 152).

A PURE, stdlib-only, *read-only* RESEARCH_ONLY_AUTOPILOT planning controller. Its
only job is to let the SPARTA research-only paper-contract chain keep moving while
the operator is away, by reasoning -- on paper only -- over a static, caller-supplied
status summary and emitting a BOUNDED plan: which safe research-only bundles to
prepare next, which paths each may touch, which it may not, which scoped tests to run,
and -- critically -- a commit / push POLICY that keeps every commit and every push
gated behind explicit per-run human approval. It is a planner, not an actor.

    MISSION_FLOW_CURRENT_STAGE  = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION    = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

It may automate ONLY safe research-only paper work: planning, queuing, and describing
the next research-only contract bundles (module + test), and producing a commit-ready
REVIEW PACKET for a human. It does NOT -- and is structurally incapable of -- doing
any of the following: staging files (git add), committing, pushing, fetching data,
calling a provider / API / network, reading a credential / .env, printing a secret,
running QA / backtest / simulation, touching a broker / exchange / account / order /
portfolio, triggering paper / live trading, writing runtime / dashboard outputs, or
unlocking any gate.

CORE RULE: this controller NEVER crosses a real-world boundary and NEVER auto-pushes.
Any commit is prepared as a review packet ONLY and requires explicit human approval;
any push requires explicit PER-RUN human approval. When any unsafe / forbidden flag is
present, or a real-data / QA / boundary-crossing request is made, it refuses
automation: automation_allowed is False, max_safe_bundles is 0, real_data_qa stays
BLOCKED, baseline stays BLOCKED, and paper / micro-live stays LOCKED.

Decision categories (exactly one is chosen, by precedence):
  - HOLD                          : an unsafe / forbidden flag was present, or a
                                    boundary-crossing request was made, or there is no
                                    safe automated step right now.
  - RUN_BOUNDED_RESEARCH_AUTOPILOT: it is safe to prepare a BOUNDED queue of
                                    research-only paper bundles. Commit / push remain
                                    human-gated for every bundle.

Public API:
  - CONTROLLER_SCHEMA_VERSION / CONTROLLER_LABEL / CONTROLLER_STATUS
  - CONTROLLER_MODE / CONTROLLER_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - DECISION_HOLD / DECISION_RUN / DECISION_CATEGORIES
  - COMMIT_POLICY / PUSH_POLICY
  - MAX_SAFE_BUNDLES_CEILING / DEFAULT_MAX_SAFE_BUNDLES
  - REAL_DATA_QA_STATE_BLOCKED / BASELINE_STATE_BLOCKED / PAPER_LIVE_STATE_LOCKED
  - CONTROLLER_FORBIDDEN_PATHS / CONTROLLER_HARD_STOP_RULES
  - CONTROLLER_FORBIDDEN_TRADE_TERMS / CONTROLLER_AUTHORIZATION_FLAGS
  - CONTROLLER_GATE_LOCK_FLAGS / CONTROLLER_GATE_UNLOCK_REQUEST_FLAGS
  - CONTROLLER_BOUNDARY_CROSSING_FLAGS / CONTROLLER_SAFETY_FLAGS
  - DEFAULT_AUTOPILOT_BUNDLE_QUEUE / DEFAULT_CONTROLLER_INPUT
  - allowed_paths_for_bundle(bundle_type, bundle_slug="")
  - scoped_tests_for_bundle(bundle_type, bundle_slug="")
  - assess_overnight_research_autopilot(payload)
  - build_overnight_research_autopilot_plan(payload=None)
  - validate_overnight_research_autopilot_plan(plan)
  - render_overnight_research_autopilot_plan_markdown(plan)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

CONTROLLER_SCHEMA_VERSION = (
    "strategy_factory_overnight_research_autopilot_controller.v1"
)
CONTROLLER_LABEL = "Block 152 - SPARTA Overnight Research Autopilot Controller"
CONTROLLER_STATUS = "READ_ONLY_OVERNIGHT_RESEARCH_AUTOPILOT_CONTROLLER"
CONTROLLER_MODE = "RESEARCH_ONLY_AUTOPILOT"

CONTROLLER_CORE_RULE = (
    "This controller NEVER crosses a real-world boundary and NEVER auto-pushes. It "
    "plans only safe research-only paper bundles and produces a commit-ready review "
    "packet for a human. It never stages (git add), never commits, never pushes, "
    "never fetches data, never calls a provider / API / network, never reads a "
    "credential / .env, never prints a secret, never runs QA / backtest / "
    "simulation, never touches a broker / exchange / account / portfolio, never "
    "places a paper / live instruction, never writes runtime / dashboard outputs, "
    "and never unlocks real_data_qa, baseline, paper, or micro-live. Every commit "
    "and every push requires explicit human approval; any push requires explicit "
    "per-run human approval. real_data_qa stays BLOCKED, baseline stays BLOCKED, and "
    "paper / live stays LOCKED."
)

# The current mission-flow truth this controller is anchored to. The companion test
# cross-checks these against the live status module so they cannot drift.
# (Imported from the databento read-only fetch execution contract -- single source.)

# Decision categories (exactly one is chosen), in precedence order.
DECISION_HOLD = "HOLD"
DECISION_RUN = "RUN_BOUNDED_RESEARCH_AUTOPILOT"

DECISION_CATEGORIES: tuple[str, ...] = (DECISION_HOLD, DECISION_RUN)

# The commit / push policy strings. These keep BOTH steps human-gated: the autopilot
# prepares a commit-ready review packet only, and never pushes on its own.
COMMIT_POLICY = (
    "PREPARE_EXPLICIT_PATHS_COMMIT_READY_REVIEW_PACKET_ONLY_"
    "NO_AUTO_COMMIT_REQUIRES_EXPLICIT_HUMAN_APPROVAL"
)
PUSH_POLICY = "NO_AUTO_PUSH_REQUIRES_EXPLICIT_PER_RUN_HUMAN_APPROVAL"

# How many safe research-only bundles the autopilot may plan in one overnight run.
MAX_SAFE_BUNDLES_CEILING = 8
DEFAULT_MAX_SAFE_BUNDLES = 5

# This controller never reports anything but blocked / locked for these.
REAL_DATA_QA_STATE_BLOCKED = "BLOCKED"
BASELINE_STATE_BLOCKED = "BLOCKED"
PAPER_LIVE_STATE_LOCKED = "LOCKED"

# Paths this controller must never plan to touch for a research bundle.
CONTROLLER_FORBIDDEN_PATHS: tuple[str, ...] = (
    "data/",
    "data/databento/",
    "data/databento_cache/",
    "data/crypto_d1_spot_cache/",
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
    "app.py",
)

# The verbatim hard-stop rules. The controller obeys all of them, always.
CONTROLLER_HARD_STOP_RULES: tuple[str, ...] = (
    "Stop on any boundary crossing.",
    "Never fetch data.",
    "Never call a provider / API / network.",
    "Never read a credential or .env.",
    "Never print or log a secret.",
    "Never run QA / backtest / simulation.",
    "Never touch a broker / exchange / account / portfolio.",
    "Never place a paper / live instruction.",
    "Never stage files (git add).",
    "Never commit.",
    "Never push.",
    "Never write runtime / dashboard outputs.",
    "Never modify decisions.md or lessons.md.",
    "Never unlock real_data_qa, baseline, paper, or micro-live.",
    "Never turn any real-world capability flag True.",
    "Any commit requires explicit human approval; any push requires explicit "
    "per-run human approval.",
)

# Execution / promotion verbs the controller's generated guidance must never contain
# as whole words.
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
    "authorizes_automation_trading",
    "authorizes_real_world_action",
    "authorizes_runtime_write",
    "authorizes_dashboard_write",
    "authorizes_auto_commit",
    "authorizes_auto_push",
)

# Gate-lock flags that MUST be True (blocked / locked). If present and not True, the
# input tried to unlock a gate -> unsafe HOLD.
CONTROLLER_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock / promotion request flags that, if truthy, force an unsafe HOLD.
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

# Boundary-crossing request flags: any attempt to make the autopilot do real data /
# QA / network / provider / auto-commit / auto-push work forces an unsafe HOLD.
CONTROLLER_BOUNDARY_CROSSING_FLAGS: tuple[str, ...] = (
    "fetch_data_now",
    "call_provider_now",
    "use_network_now",
    "run_qa_now",
    "run_backtest_now",
    "run_simulation_now",
    "read_credentials",
    "read_dotenv",
    "print_secrets",
    "auto_commit_now",
    "auto_push_now",
    "stage_files_now",
    "write_runtime_now",
    "write_dashboard_now",
    "cross_real_data_qa_boundary",
    "make_boundary_decision",
)

# Read-only safety flags. The posture facts are True; every capability /
# authorization / unlock flag is False.
CONTROLLER_SAFETY_FLAGS: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "human_approval_required": True,
    "per_run_push_approval_required": True,
    "executes": False,
    "runs_git": False,
    "stages_files": False,
    "auto_commits": False,
    "auto_pushes": False,
    "fetches_data": False,
    "calls_provider": False,
    "uses_network": False,
    "reads_credentials": False,
    "reads_dotenv": False,
    "exposes_secret": False,
    "runs_qa": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "calls_broker_exchange": False,
    "touches_account_portfolio": False,
    "places_orders": False,
    "triggers_paper_trading": False,
    "triggers_live_trading": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "modifies_decisions_or_lessons": False,
    "authorizes_trading": False,
    "authorizes_data_fetch": False,
    "authorizes_backtest": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_automation_trading": False,
    "authorizes_real_world_action": False,
    "authorizes_auto_commit": False,
    "authorizes_auto_push": False,
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

# The default BOUNDED menu of next SAFE research-only bundles the autopilot may plan
# overnight. Every candidate is RESEARCH_ONLY paper work that crosses NO real-world
# boundary and unlocks nothing. `kind` is context only: BUILD / REGISTER are
# automatable (paper module + test); UI_SYNC is flagged for a human, never performed.
DEFAULT_AUTOPILOT_BUNDLE_QUEUE: tuple[dict[str, Any], ...] = (
    {
        "id": "1",
        "label": "Public read-only spot source evaluation contract",
        "slug": "crypto_d1_public_read_only_spot_source_evaluation",
        "kind": "BUILD",
        "note": (
            "Research-only paper contract that evaluates a candidate PUBLIC "
            "read-only spot data source against the Block 151 adapter rules. Pure "
            "paper module + test; calls nothing, fetches nothing."
        ),
        "research_only": True,
        "crosses_real_data_qa_boundary": False,
    },
    {
        "id": "2",
        "label": "Concrete provider adapter contract (no network)",
        "slug": "crypto_d1_concrete_read_only_spot_provider_adapter_spec",
        "kind": "BUILD",
        "note": (
            "Research-only paper specification of a concrete provider adapter that "
            "would satisfy Block 151 -- described on paper only, with no network and "
            "no implementation. Pure paper module + test."
        ),
        "research_only": True,
        "crosses_real_data_qa_boundary": False,
    },
    {
        "id": "3",
        "label": "Provider runner dry-run tests with a fake provider",
        "slug": "crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run",
        "kind": "BUILD",
        "note": (
            "Research-only paper contract describing dry-run test scenarios for the "
            "Block 150 runner using an in-memory FAKE provider. Pure paper module + "
            "test; injects no real provider and fetches nothing."
        ),
        "research_only": True,
        "crosses_real_data_qa_boundary": False,
    },
    {
        "id": "4",
        "label": "Manual CSV import approval packet",
        "slug": "crypto_d1_manual_csv_spot_import_approval_packet",
        "kind": "BUILD",
        "note": (
            "Research-only static packet describing the scope of a FUTURE, "
            "human-approved manual-CSV spot import (read-only, no network). Pure "
            "paper module + test; imports nothing."
        ),
        "research_only": True,
        "crosses_real_data_qa_boundary": False,
    },
    {
        "id": "5",
        "label": "Strategy evidence ranking continuation",
        "slug": "crypto_d1_strategy_evidence_ranking_continuation",
        "kind": "BUILD",
        "note": (
            "Continue the research-only Crypto-D1 strategy evidence ranking paper "
            "contract chain. Pure paper module + test."
        ),
        "research_only": True,
        "crosses_real_data_qa_boundary": False,
    },
    {
        "id": "6",
        "label": "JARVIS display sync if drift detected",
        "slug": "jarvis_display_sync",
        "kind": "UI_SYNC",
        "note": (
            "If the JARVIS panel has drifted from the mission-flow truth, FLAG a "
            "display sync for a human. The autopilot performs no dashboard write; it "
            "only records that a human should sync the panel."
        ),
        "research_only": True,
        "crosses_real_data_qa_boundary": False,
    },
)

# Bundle kinds the autopilot may actually PLAN to prepare (paper module + test). All
# other kinds (e.g. UI_SYNC) are flagged for a human and never auto-prepared.
_AUTOMATABLE_KINDS: frozenset[str] = frozenset({"BUILD", "REGISTER"})

# A deterministic, illustrative paper input. Anchored to the live mission flow. The
# default plan is a safe bounded autopilot run of research-only paper bundles, with
# commit / push human-gated. Nothing here is real; static example only.
DEFAULT_CONTROLLER_INPUT: dict[str, Any] = {
    "label": "SPARTA overnight research autopilot input (static sample)",
    "mode": "RESEARCH_ONLY_AUTOPILOT",
    "read_only": True,
    "executes": False,
    "research_only": True,
    "current_stage": MISSION_FLOW_CURRENT_STAGE,
    "next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
    "requested_max_bundles": DEFAULT_MAX_SAFE_BUNDLES,
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


def _coerce_int(value: Any, default: int) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        s = value.strip()
        if s.isdigit():
            return int(s)
    return default


def _bundle_module_stem(bundle_type: Any, bundle_slug: Any = "") -> str:
    """Derive a research-only module stem for a bundle. Pure string work; this NEVER
    reads the filesystem and authorizes nothing."""
    slug = _slugify(bundle_slug) or _slugify(bundle_type) or _DEFAULT_BUNDLE_TYPE
    stem = "strategy_factory_" + slug
    if not stem.endswith("_contract"):
        stem = stem + "_contract"
    return stem


def allowed_paths_for_bundle(bundle_type: Any, bundle_slug: Any = "") -> list[str]:
    """Return the ONLY paths a research bundle may touch: its paper module, its test,
    and the additive commander_2_safety allowlist lines. Pure; reads no filesystem
    and creates nothing."""
    stem = _bundle_module_stem(bundle_type, bundle_slug)
    return [
        "sparta_commander/" + stem + ".py",
        "tests/test_" + stem + ".py",
        "sparta_commander/commander_2_safety.py (additive allowlist lines only)",
    ]


def scoped_tests_for_bundle(bundle_type: Any, bundle_slug: Any = "") -> list[str]:
    """Return the scoped tests to run for a research bundle: its own test plus the
    commander_2_safety allowlist test. Pure string work."""
    stem = _bundle_module_stem(bundle_type, bundle_slug)
    return [
        "tests/test_" + stem + ".py",
        "tests/test_sparta_commander_2_safety.py",
    ]


def _autopilot_bundle_queue(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the bounded research-only bundle queue. Accepts a caller override
    (`candidate_bundles`) but defaults to the standard queue. Any candidate that
    claims to cross the real_data_qa boundary or is not research-only is dropped, so
    the queue can never advertise an unsafe option."""
    raw = payload.get("candidate_bundles")
    source: tuple[dict[str, Any], ...] | list[dict[str, Any]]
    if isinstance(raw, (list, tuple)) and raw:
        source = [dict(c) for c in raw if isinstance(c, dict)]
    else:
        source = DEFAULT_AUTOPILOT_BUNDLE_QUEUE
    safe: list[dict[str, Any]] = []
    for c in source:
        candidate = dict(c)
        candidate.setdefault("research_only", True)
        candidate["crosses_real_data_qa_boundary"] = False
        if candidate.get("research_only") is not True:
            continue
        safe.append(candidate)
    return safe


def _unsafe_flag_hits(payload: dict[str, Any]) -> list[str]:
    """Collect any input keys that attempt to authorize, unlock, promote, or force a
    real-world / boundary-crossing capability. Any hit forces an unsafe HOLD."""
    hits: list[str] = []
    for flag in CONTROLLER_AUTHORIZATION_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in CONTROLLER_GATE_UNLOCK_REQUEST_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in CONTROLLER_BOUNDARY_CROSSING_FLAGS:
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


# --------------------------------------------------------------------------- #
# assessment
# --------------------------------------------------------------------------- #
def assess_overnight_research_autopilot(payload: Any) -> dict[str, Any]:
    """Assess (read-only) whether a bounded overnight research-only autopilot run is
    safe, and what the next safe bundle is. Returns a fresh dict every call.
    Authorizes nothing and unlocks nothing under any outcome."""
    data = _as_payload(payload)
    unsafe_hits = _unsafe_flag_hits(data)

    queue = _autopilot_bundle_queue(data)
    automatable = [c for c in queue if c.get("kind") in _AUTOMATABLE_KINDS]

    requested = _coerce_int(
        data.get("requested_max_bundles"), DEFAULT_MAX_SAFE_BUNDLES
    )
    if requested < 0:
        requested = 0

    if unsafe_hits:
        category = DECISION_HOLD
        reason = (
            "Refusing automation: a forbidden authorization / unlock / promotion / "
            "boundary-crossing flag was present (" + ", ".join(unsafe_hits) + ")."
        )
    elif not automatable:
        category = DECISION_HOLD
        reason = "No safe research-only paper bundle is available to prepare."
    else:
        category = DECISION_RUN
        reason = (
            "It is safe to prepare a bounded queue of research-only paper bundles. "
            "Every commit and every push remains gated behind explicit human "
            "approval."
        )

    automation_allowed = category == DECISION_RUN

    if automation_allowed:
        max_safe_bundles = min(
            requested, MAX_SAFE_BUNDLES_CEILING, len(automatable)
        )
        next_safe_bundle = dict(automatable[0]) if max_safe_bundles > 0 else None
        if max_safe_bundles <= 0:
            category = DECISION_HOLD
            automation_allowed = False
            reason = (
                "Bounded bundle budget resolved to zero; holding with no automated "
                "step."
            )
    else:
        max_safe_bundles = 0
        next_safe_bundle = None

    return {
        "mode": CONTROLLER_MODE,
        "decision_category": category,
        "automation_allowed": automation_allowed,
        "unsafe_flag_hits": list(unsafe_hits),
        "reason": reason,
        "requested_max_bundles": requested,
        "max_safe_bundles": max_safe_bundles,
        "queue": queue,
        "automatable_bundles": automatable,
        "next_safe_bundle": next_safe_bundle,
        "real_data_qa_state": REAL_DATA_QA_STATE_BLOCKED,
        "baseline_backtest_state": BASELINE_STATE_BLOCKED,
        "paper_live_state": PAPER_LIVE_STATE_LOCKED,
        "crosses_boundary": False,
        "auto_pushes": False,
        "auto_commits": False,
        "unlocks_real_data_qa": False,
        "authorizes_nothing": True,
    }


# --------------------------------------------------------------------------- #
# plan build
# --------------------------------------------------------------------------- #
def _planned_bundles(assessment: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the bounded, per-bundle plan. Each entry lists the only paths it may
    touch, its scoped tests, and the human-gated commit / push policy. Pure."""
    if not assessment["automation_allowed"]:
        return []
    planned: list[dict[str, Any]] = []
    for candidate in assessment["automatable_bundles"][: assessment["max_safe_bundles"]]:
        slug = candidate.get("slug", candidate.get("id", ""))
        planned.append(
            {
                "id": candidate.get("id"),
                "label": candidate.get("label"),
                "kind": candidate.get("kind"),
                "allowed_paths": allowed_paths_for_bundle(_DEFAULT_BUNDLE_TYPE, slug),
                "scoped_tests": scoped_tests_for_bundle(_DEFAULT_BUNDLE_TYPE, slug),
                "commit_policy": COMMIT_POLICY,
                "push_policy": PUSH_POLICY,
                "requires_human_commit_approval": True,
                "requires_human_push_approval": True,
                "research_only": True,
                "crosses_real_data_qa_boundary": False,
            }
        )
    return planned


def _final_operator_report(assessment: dict[str, Any]) -> str:
    """Deterministic research-only operator report. Carries no execution or trade
    verbs and authorizes nothing."""
    lines = [
        "OVERNIGHT RESEARCH-ONLY AUTOPILOT REPORT",
        "Decision: " + assessment["decision_category"],
        "Automation allowed: " + str(assessment["automation_allowed"]),
        "Max safe bundles: " + str(assessment["max_safe_bundles"]),
        "Reason: " + assessment["reason"],
        "Commit policy: " + COMMIT_POLICY,
        "Push policy: " + PUSH_POLICY,
        "real_data_qa state: " + REAL_DATA_QA_STATE_BLOCKED,
        "baseline state: " + BASELINE_STATE_BLOCKED,
        "paper / live state: " + PAPER_LIVE_STATE_LOCKED,
    ]
    if assessment["automation_allowed"] and assessment["next_safe_bundle"]:
        lines.append(
            "Next safe bundle: "
            + str(assessment["next_safe_bundle"].get("label"))
            + " [" + str(assessment["next_safe_bundle"].get("kind")) + "]"
        )
        lines.append(
            "For every prepared bundle: prepare a commit-ready review packet, run "
            "the scoped tests, then wait for explicit human approval before any "
            "commit, and explicit per-run human approval before any push."
        )
    else:
        lines.append(
            "Holding. No automated research step is prepared. A human reviews the "
            "mission flow before anything proceeds."
        )
    lines.append(
        "This report authorizes nothing. No data, no provider, no network, no "
        "credential, no QA, no backtest, no broker / exchange, no paper / live, no "
        "runtime / dashboard write, no staging, no commit, no push, and no gate "
        "unlock occurs."
    )
    return "\n".join(lines)


def _safety_state(assessment: dict[str, Any]) -> dict[str, Any]:
    """Deterministic safety-state block. Always blocked / locked."""
    return {
        "real_data_qa": REAL_DATA_QA_STATE_BLOCKED,
        "baseline_backtest": BASELINE_STATE_BLOCKED,
        "paper_live": PAPER_LIVE_STATE_LOCKED,
        "crosses_boundary": False,
        "auto_commits": False,
        "auto_pushes": False,
        "human_commit_approval_required": True,
        "human_push_approval_required": True,
        "authorizes_nothing": True,
    }


def build_overnight_research_autopilot_plan(payload: Any = None) -> dict[str, Any]:
    """Build (fresh each call) the read-only overnight autopilot plan. Every
    capability flag is False and every gate lock is reported blocked / locked
    regardless of the assessed decision."""
    data = (
        dict(DEFAULT_CONTROLLER_INPUT) if payload is None else _as_payload(payload)
    )
    assessment = assess_overnight_research_autopilot(data)
    planned = _planned_bundles(assessment)
    safety_flags_all_false = all(
        CONTROLLER_SAFETY_FLAGS[name] is False for name in _CAPABILITY_FLAGS
    )

    plan: dict[str, Any] = {
        "schema_version": CONTROLLER_SCHEMA_VERSION,
        "label": CONTROLLER_LABEL,
        "status": CONTROLLER_STATUS,
        "mode": CONTROLLER_MODE,
        "core_rule": CONTROLLER_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "decision_categories": list(DECISION_CATEGORIES),
        "decision_category": assessment["decision_category"],
        # ---- the spec's expected outputs ----
        "automation_allowed": assessment["automation_allowed"],
        "max_safe_bundles": assessment["max_safe_bundles"],
        "next_safe_bundle": assessment["next_safe_bundle"],
        "planned_bundles": planned,
        "allowed_paths": (
            list(planned[0]["allowed_paths"]) if planned else []
        ),
        "forbidden_paths": list(CONTROLLER_FORBIDDEN_PATHS),
        "scoped_tests": (
            list(planned[0]["scoped_tests"]) if planned else []
        ),
        "commit_policy": COMMIT_POLICY,
        "push_policy": PUSH_POLICY,
        "hard_stop_rules": list(CONTROLLER_HARD_STOP_RULES),
        "safety_state": _safety_state(assessment),
        "final_operator_report": _final_operator_report(assessment),
        "safety_flags_all_false": safety_flags_all_false,
        "real_data_qa_state": REAL_DATA_QA_STATE_BLOCKED,
        "baseline_backtest_state": BASELINE_STATE_BLOCKED,
        "paper_live_state": PAPER_LIVE_STATE_LOCKED,
        # ---- supporting detail ----
        "reason": assessment["reason"],
        "unsafe_flag_hits": list(assessment["unsafe_flag_hits"]),
        "bundle_queue": assessment["queue"],
        "requested_max_bundles": assessment["requested_max_bundles"],
        "max_safe_bundles_ceiling": MAX_SAFE_BUNDLES_CEILING,
        "safety_flags": dict(CONTROLLER_SAFETY_FLAGS),
        "human_approval_required": True,
        "per_run_push_approval_required": True,
        "requires_separate_future_human_approved_step": True,
        "operator_summary": (
            assessment["decision_category"]
            + " - "
            + assessment["reason"]
            + " Commit and push stay human-gated; real_data_qa stays "
            + REAL_DATA_QA_STATE_BLOCKED
            + "; paper / live stays "
            + PAPER_LIVE_STATE_LOCKED
            + "."
        ),
        "read_only": True,
        "executes": False,
        "research_only": True,
        "runs_git": False,
        "stages_files": False,
        "auto_commits": False,
        "auto_pushes": False,
        "fetches_data": False,
        "calls_provider": False,
        "uses_network": False,
        "reads_credentials": False,
        "reads_dotenv": False,
        "exposes_secret": False,
        "runs_qa": False,
        "runs_backtest": False,
        "runs_simulation": False,
        "calls_broker_exchange": False,
        "touches_account_portfolio": False,
        "places_orders": False,
        "triggers_paper_trading": False,
        "triggers_live_trading": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
        "modifies_decisions_or_lessons": False,
        "authorizes_trading": False,
        "authorizes_data_fetch": False,
        "authorizes_backtest": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "authorizes_broker_exchange": False,
        "authorizes_automation_trading": False,
        "authorizes_real_world_action": False,
        "authorizes_auto_commit": False,
        "authorizes_auto_push": False,
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
    return plan


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
_REQUIRED_PLAN_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "mode",
    "core_rule",
    "mission_flow_current_stage",
    "mission_flow_next_required_action",
    "decision_category",
    "automation_allowed",
    "max_safe_bundles",
    "next_safe_bundle",
    "allowed_paths",
    "forbidden_paths",
    "scoped_tests",
    "commit_policy",
    "push_policy",
    "hard_stop_rules",
    "safety_state",
    "final_operator_report",
    "safety_flags_all_false",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
    "safety_flags",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "runs_git",
    "stages_files",
    "auto_commits",
    "auto_pushes",
    "fetches_data",
    "calls_provider",
    "uses_network",
    "reads_credentials",
    "reads_dotenv",
    "exposes_secret",
    "runs_qa",
    "runs_backtest",
    "runs_simulation",
    "calls_broker_exchange",
    "touches_account_portfolio",
    "places_orders",
    "triggers_paper_trading",
    "triggers_live_trading",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
    "modifies_decisions_or_lessons",
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation_trading",
    "authorizes_real_world_action",
    "authorizes_auto_commit",
    "authorizes_auto_push",
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


def validate_overnight_research_autopilot_plan(plan: Any) -> dict[str, Any]:
    """Validate (read-only) a built overnight autopilot plan. Returns a verdict dict
    of boolean checks plus an overall `valid`."""
    d = plan if isinstance(plan, dict) else {}
    missing = [f for f in _REQUIRED_PLAN_FIELDS if f not in d]

    schema_ok = d.get("schema_version") == CONTROLLER_SCHEMA_VERSION
    label_ok = d.get("label") == CONTROLLER_LABEL
    status_ok = d.get("status") == CONTROLLER_STATUS
    mode_ok = d.get("mode") == CONTROLLER_MODE
    core_rule_ok = d.get("core_rule") == CONTROLLER_CORE_RULE
    read_only = d.get("read_only") is True
    research_only = d.get("research_only") is True
    executes_false = d.get("executes") is False
    human_required = d.get("human_approval_required") is True
    per_run_push_required = d.get("per_run_push_approval_required") is True
    future_step_required = (
        d.get("requires_separate_future_human_approved_step") is True
    )
    mission_flow_refs_ok = (
        d.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and d.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    category_ok = d.get("decision_category") in DECISION_CATEGORIES
    commit_policy_ok = d.get("commit_policy") == COMMIT_POLICY
    push_policy_ok = d.get("push_policy") == PUSH_POLICY
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
        and d.get("baseline_backtest_state") == BASELINE_STATE_BLOCKED
        and d.get("paper_live_state") == PAPER_LIVE_STATE_LOCKED
    )

    # safety_state sub-block must report blocked / locked and no auto commit / push.
    ss = d.get("safety_state")
    safety_state_ok = isinstance(ss, dict) and (
        ss.get("real_data_qa") == REAL_DATA_QA_STATE_BLOCKED
        and ss.get("baseline_backtest") == BASELINE_STATE_BLOCKED
        and ss.get("paper_live") == PAPER_LIVE_STATE_LOCKED
        and ss.get("auto_commits") is False
        and ss.get("auto_pushes") is False
        and ss.get("human_push_approval_required") is True
        and ss.get("authorizes_nothing") is True
    )

    # max_safe_bundles must be a non-negative int within the ceiling.
    msb = d.get("max_safe_bundles")
    max_bundles_ok = (
        isinstance(msb, int)
        and not isinstance(msb, bool)
        and 0 <= msb <= MAX_SAFE_BUNDLES_CEILING
    )

    # automation_allowed must agree with the decision category and with whether a
    # next safe bundle / bounded budget exists.
    automation_value = d.get("automation_allowed")
    automation_consistent = (automation_value is True) == (
        d.get("decision_category") == DECISION_RUN
    )
    # when running, there must be a next bundle and a positive budget; when holding,
    # there must be none.
    if automation_value is True:
        run_shape_ok = (
            isinstance(d.get("next_safe_bundle"), dict)
            and isinstance(msb, int)
            and not isinstance(msb, bool)
            and msb > 0
            and bool(d.get("allowed_paths"))
            and bool(d.get("scoped_tests"))
        )
    else:
        run_shape_ok = (
            d.get("next_safe_bundle") is None
            and msb == 0
            and d.get("allowed_paths") == []
            and d.get("scoped_tests") == []
        )

    # no allowed path may fall under a forbidden path prefix.
    allowed_paths = d.get("allowed_paths")
    allowed_paths_is_list = isinstance(allowed_paths, list)
    forbidden = tuple(d.get("forbidden_paths") or ())
    no_forbidden_in_allowed = allowed_paths_is_list and not any(
        str(p).startswith(f) for p in allowed_paths for f in forbidden
    )

    # every planned bundle must keep commit / push human-gated and cross no boundary.
    planned = d.get("planned_bundles")
    planned_ok = isinstance(planned, list) and all(
        isinstance(b, dict)
        and b.get("commit_policy") == COMMIT_POLICY
        and b.get("push_policy") == PUSH_POLICY
        and b.get("requires_human_commit_approval") is True
        and b.get("requires_human_push_approval") is True
        and b.get("crosses_real_data_qa_boundary") is False
        for b in planned
    )

    # the bundle queue must exist and advertise NO unsafe option.
    queue = d.get("bundle_queue")
    queue_ok = (
        isinstance(queue, list)
        and bool(queue)
        and all(
            isinstance(c, dict)
            and c.get("research_only") is True
            and c.get("crosses_real_data_qa_boundary") is False
            for c in queue
        )
    )

    # generated guidance must carry no execution / trade verbs as whole words.
    guidance_blob = " ".join(
        str(d.get(k, ""))
        for k in (
            "final_operator_report",
            "operator_summary",
            "core_rule",
            "reason",
            "commit_policy",
            "push_policy",
        )
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(CONTROLLER_FORBIDDEN_TRADE_TERMS))

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
        "per_run_push_required": per_run_push_required,
        "future_step_required": future_step_required,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "category_ok": category_ok,
        "commit_policy_ok": commit_policy_ok,
        "push_policy_ok": push_policy_ok,
        "hard_stops_ok": hard_stops_ok,
        "flags_false": flags_false,
        "safety_flags_all_false_ok": safety_flags_all_false_ok,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "safety_flags_ok": safety_flags_ok,
        "states_blocked_locked": states_blocked_locked,
        "safety_state_ok": safety_state_ok,
        "max_bundles_ok": max_bundles_ok,
        "automation_consistent": automation_consistent,
        "run_shape_ok": run_shape_ok,
        "no_forbidden_in_allowed": no_forbidden_in_allowed,
        "planned_ok": planned_ok,
        "queue_ok": queue_ok,
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


def render_overnight_research_autopilot_plan_markdown(plan: Any) -> str:
    """Render a built plan as a deterministic markdown brief. Pure string
    formatting; writes nothing."""
    d = plan if isinstance(plan, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Overnight Research Autopilot Controller")
    lines.append("")
    lines.append("- Label: " + str(d.get("label", "")))
    lines.append("- Mode: " + str(d.get("mode", "")))
    lines.append("- Status: " + str(d.get("status", "")))
    lines.append("- Decision: " + str(d.get("decision_category", "")))
    lines.append("- Automation allowed: " + str(d.get("automation_allowed", False)))
    lines.append("- Max safe bundles: " + str(d.get("max_safe_bundles", 0)))
    lines.append("- Commit policy: " + str(d.get("commit_policy", "")))
    lines.append("- Push policy: " + str(d.get("push_policy", "")))
    lines.append("- real_data_qa state: " + str(d.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(d.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(d.get("paper_live_state", "")))
    lines.append(
        "- safety_flags_all_false: " + str(d.get("safety_flags_all_false", False))
    )

    nb = d.get("next_safe_bundle")
    next_label = (
        str(nb.get("label")) + " [" + str(nb.get("kind")) + "]"
        if isinstance(nb, dict)
        else "(none)"
    )
    _emit(lines, "Next Safe Bundle", [next_label])
    _emit(
        lines,
        "Bundle Queue",
        [
            str(c.get("id")) + ". " + str(c.get("label")) + " [" + str(c.get("kind")) + "]"
            for c in (d.get("bundle_queue") or [])
        ],
    )
    _emit(
        lines,
        "Planned Bundles",
        [
            str(b.get("id")) + ". " + str(b.get("label")) + " [" + str(b.get("kind")) + "]"
            for b in (d.get("planned_bundles") or [])
        ],
    )
    _emit(lines, "Allowed Paths (next bundle)", list(d.get("allowed_paths") or []))
    _emit(lines, "Forbidden Paths", list(d.get("forbidden_paths") or []))
    _emit(lines, "Scoped Tests (next bundle)", list(d.get("scoped_tests") or []))
    _emit(lines, "Hard Stop Rules", list(d.get("hard_stop_rules") or []))
    _emit(
        lines,
        "Final Operator Report",
        list(str(d.get("final_operator_report", "")).splitlines()),
    )
    return "\n".join(lines)

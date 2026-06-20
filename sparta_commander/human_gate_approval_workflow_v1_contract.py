"""Dashboard Human-Gate Approval Workflow v1 (PURE, RESEARCH ONLY).

A read-only control surface that turns the candidate-research lane's CURRENT open
human gate into the exact, copyable text the operator should paste next -- so the
human stops having to ask "what do I send now?". It reads the committed lane-status
contract (the single source of truth), maps the lane's current gate to a
recommended SAFE next decision, and emits:

  * the current active candidate / stage / open human gate,
  * the recommended safe next decision (a human decision, never auto-applied),
  * the exact copyable approval text for that gate,
  * what the approval ALLOWS (research-only build steps),
  * what the approval explicitly does NOT allow (data fetch / detection / labels /
    replay / backtest / PnL / optimization / paper / live / broker / order),
  * the repo sync/clean posture and the safety locks,
  * a bypass warning (this surface only generates text; it advances nothing),
  * and a future-ready ready-for-commit field for when a unit is actually built.

It executes NOTHING and decides NOTHING: it generates copyable text only. It does
NOT advance any gate, build any detector/spec, fetch data, detect, label, replay,
backtest, compute PnL, optimize, write, stage, commit, or push, and it touches NO
paper/live/broker/order surface. Every capability flag is pinned False with a full
scope_locks set. The human still pastes the token by hand -- nothing here bypasses
that.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane

HGW_VERSION = "v1"
HGW_MODE = "RESEARCH_ONLY"
HGW_LANE = "crypto_d1_auto_research"

# The bypass guard shown on the surface: this panel only generates text.
GATE_BYPASS_WARNING = (
    "This surface only GENERATES copyable text; it never advances a gate, builds "
    "anything, or runs anything. Any tool or step that tries to advance the "
    "candidate past this gate without the human pasting the token by hand is a "
    "BYPASS and must be refused.")

# Per-gate workflow specs. Keyed by the lane's current next_required_action token.
# Each entry maps a human gate to a recommended SAFE next decision plus the
# research-only allow / forbid lists. Adding a new gate here is the only change
# needed when the lane advances.
_GATE_SPECS: dict[str, dict[str, Any]] = {
    "HUMAN_DECISION_C17_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT": {
        "recommended_decision": "ADVANCE C17 TO DETECTOR SPEC + SYNTHETIC DRY-RUN",
        "stage_after_approval": "detector_spec_dry_run",
        "allows": (
            "build the detector-spec contract (pure, declared)",
            "build synthetic dry-run fixtures + tests",
            "research-only validation",
        ),
        "forbids": (
            "no real data fetch",
            "no real-candle detection",
            "no labels",
            "no replay/backtest/PnL",
            "no optimization",
            "no paper/live/broker/order code",
        ),
    },
    "HUMAN_DECISION_C17_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT": {
        "recommended_decision": (
            "ADVANCE C17 TO REAL-CANDLE LABELS / REVIEW (FROZEN LOCAL DATA ONLY)"),
        "stage_after_approval": "real_candle_labels_review",
        "allows": (
            "build the real-candle labels/review contract ONLY IF existing frozen "
            "local data is used",
            "label/review preparation only",
            "research-only validation",
        ),
        "forbids": (
            "no new data fetch",
            "no replay/backtest/PnL",
            "no optimization",
            "no paper/live/broker/order code",
            "no auto-trading",
        ),
    },
    "HUMAN_DECISION_C20_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT": {
        "recommended_decision": "ADVANCE C20 TO CANDIDATE SPEC",
        "stage_after_approval": "candidate_spec",
        "allows": (
            "build the candidate-spec contract (pure, declared rules)",
            "define the exact same-asset long-spot / short-perp basis + funding "
            "carry construction, the mechanical-neutrality gate-zero, the basis / "
            "funding / entry / exit / stop / turnover / non-overlap / replay-win "
            "rules",
            "research-only validation",
        ),
        "forbids": (
            "no detector build",
            "no real data fetch (use the frozen public BTC/ETH/SOL dataset only)",
            "no new instrument class / XAUUSD",
            "no labels",
            "no replay/backtest/PnL",
            "no optimization / rescue / tuning",
            "no paper/live/broker/order code",
        ),
    },
    "HUMAN_DECISION_C21_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT": {
        "recommended_decision": "ADVANCE C21 TO CANDIDATE SPEC",
        "stage_after_approval": "candidate_spec",
        "allows": (
            "build the candidate-spec contract (pure, declared rules)",
            "define the exact LOW-TURNOVER same-asset long-spot / short-perp funding "
            "carry construction: mechanical-neutrality gate-zero, carry-regime gate, "
            "entry/exit hysteresis, hold-persistence / minimum-hold, turnover & "
            "round-trip limits, rebalance cadence, durable-carry-breakdown exits, "
            "replay-win criteria (74 bps two-leg cost reserved)",
            "research-only validation",
        ),
        "forbids": (
            "no detector build",
            "no real data fetch (use the frozen public BTC/ETH/SOL dataset only)",
            "no new instrument class / XAUUSD",
            "no labels",
            "no replay/backtest/PnL",
            "no optimization / rescue / tuning",
            "no rescue or retune of C20 (C20 stays rejected)",
            "no paper/live/broker/order code",
        ),
    },
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "advances_gate", "auto_advances",
    "auto_applies_decision", "builds_candidate_files", "builds_detector_spec",
    "builds_dry_run", "runs_detector", "runs_labels", "runs_replay",
    "runs_backtest", "computes_pnl", "optimizes_parameters", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "bypasses_human_gate", "advances_without_human_approval", "claims_profitability",
    "claims_edge", "crosses_into_forbidden_gate",
)


def _scope_locks() -> dict[str, bool]:
    return {
        "no_execute": True, "no_write": True, "no_advance_gate": True,
        "no_auto_apply": True, "no_build": True, "no_detector_spec": True,
        "no_dry_run_build": True, "no_detector_run": True, "no_labels": True,
        "no_replay": True, "no_backtest": True, "no_pnl": True,
        "no_optimization": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True, "no_human_gate_bypass": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }


def build_copyable_approval_text(gate_token: str, candidate_name: str,
                                 stage_label: str, decision: str,
                                 stage_after: str, allows: tuple,
                                 forbids: tuple) -> str:
    """PURE. Assemble the exact multi-line text the human should paste to advance
    at this gate. Generates text only -- it applies nothing."""
    allow_lines = "\n".join("- %s" % a for a in allows)
    forbid_lines = "\n".join("- %s" % f for f in forbids)
    return (
        "%s\n\n"
        "Decision: %s.\n\n"
        "Candidate: %s\n"
        "Stage: %s -> %s\n\n"
        "Allowed (research-only):\n%s\n\n"
        "NOT allowed:\n%s\n\n"
        "Do not commit or push; stop before commit."
        % (gate_token, decision, candidate_name, stage_label, stage_after,
           allow_lines, forbid_lines))


def build_reject_text(gate_token: str, candidate_name: str) -> str:
    """PURE. The copyable text to REJECT at this gate instead of advancing."""
    return (
        "%s\n\n"
        "Decision: REJECT %s and keep it on record (no advance).\n\n"
        "Do not commit or push; stop before commit."
        % (gate_token, candidate_name))


def build_commit_approval_text(unit_name: str | None = None,
                               files: list | None = None) -> str | None:
    """PURE, FUTURE-READY. When a unit has actually been built and is committed-
    ready, this formats the safe commit-approval token the human would paste. It
    returns None when no unit is ready (the current case) so the surface shows an
    empty 'ready for commit' field rather than fabricating a token."""
    if not unit_name:
        return None
    token = "APPROVE_COMMIT_%s" % str(unit_name).strip().upper().replace(" ", "_")
    flist = "\n".join("- %s" % f for f in (files or []))
    body = ("\n\nCommit exactly these files:\n%s" % flist) if files else ""
    return ("%s%s\n\nDo not include any untracked repo clutter. "
            "After commit: push, verify, run tests, report. Stop after reporting."
            % (token, body))


def build_human_gate_workflow() -> dict[str, Any]:
    """Assemble the read-only human-gate workflow record from the committed lane
    status. Pure; no I/O. Generates copyable text only; advances nothing."""
    lane = _lane.get_lane_status()
    det = lane.get("active_candidate_detail") or {}
    gate_token = lane.get("next_required_action")
    candidate = lane.get("active_candidate")
    candidate_name = det.get("name")
    stage_label = det.get("stage_label")
    open_gate = lane.get("open_candidate_gate") is True

    spec = _GATE_SPECS.get(gate_token)
    recognized = spec is not None
    _operational_forbids = (
        "no real data fetch", "no detection", "no labels",
        "no replay/backtest/PnL", "no optimization",
        "no paper/live/broker/order code")
    if not open_gate:
        # No open candidate gate (e.g. the last candidate was rejected and the lane
        # is at automation readiness). There is no human approval to paste -- the
        # surface says so plainly and offers no copyable approval text.
        decision = ("NO OPEN CANDIDATE GATE — candidate lane is at automation "
                    "readiness; await the next human-approved research direction")
        stage_after = None
        allows = ()
        forbids = _operational_forbids
        approval_text = None
        reject_text = None
        recognized = False
    elif recognized:
        decision = spec["recommended_decision"]
        stage_after = spec["stage_after_approval"]
        allows = tuple(spec["allows"])
        forbids = tuple(spec["forbids"])
        approval_text = build_copyable_approval_text(
            gate_token, candidate_name, stage_label, decision, stage_after,
            allows, forbids)
        reject_text = build_reject_text(gate_token, candidate_name)
    else:
        # Unrecognized gate -> safe generic: surface the token but recommend
        # nothing concrete and forbid everything operational.
        decision = "AWAIT EXPLICIT HUMAN DECISION (no recommended action mapped)"
        stage_after = None
        allows = ()
        forbids = _operational_forbids
        approval_text = None
        reject_text = None

    downstream_locked = (
        lane.get("real_data_qa_state") == _lane.STATE_BLOCKED
        and lane.get("replay_state") == _lane.STATE_BLOCKED
        and lane.get("paper_trading_state") == _lane.STATE_LOCKED
        and lane.get("live_trading_state") == _lane.STATE_LOCKED)
    sf = lane.get("safety_flags") or {}

    record: dict[str, Any] = {
        "version": HGW_VERSION, "mode": HGW_MODE, "lane": HGW_LANE,
        "is_pure_workflow_only": True,
        "label": (
            "Human-gate approval workflow (READ-ONLY, RESEARCH ONLY). Generates the "
            "exact copyable approval text for the candidate lane's CURRENT open "
            "human gate. Advances nothing, builds nothing, runs nothing."),
        # 1/2/3 -- current active candidate / stage / human gate (from the lane)
        "active_candidate": candidate,
        "active_candidate_name": candidate_name,
        "current_stage_label": stage_label,
        "current_human_gate": gate_token,
        "gate_recognized": recognized,
        "has_open_human_gate": open_gate,
        # 4 -- recommended safe next decision (a HUMAN decision; never auto-applied)
        "recommended_decision": decision,
        "stage_after_approval": stage_after,
        # 5 -- the exact copyable approval text (+ the reject alternative)
        "approval_text_to_paste": approval_text,
        "reject_text_to_paste": reject_text,
        # 6 / 7 -- what the approval allows / forbids
        "approval_allows": list(allows),
        "approval_forbids": list(forbids),
        # 8 -- repo sync/clean posture is shown by the panel's git block; this
        #      surface is repo-independent (it never depends on a clean tree).
        "repo_independent": True,
        # 9 -- safety locks (mirrored from the lane, single source of truth)
        "safety_locks": {
            "real_data_qa": lane.get("real_data_qa_state"),
            "replay": lane.get("replay_state"),
            "paper_trading": lane.get("paper_trading_state"),
            "micro_live": ("LOCKED" if sf.get("micro_live_locked") else "UNLOCKED"),
            "live_trading": lane.get("live_trading_state"),
        },
        "downstream_gates_locked": downstream_locked,
        # 10 -- bypass warning (this surface advances nothing)
        "gate_bypass_warning": GATE_BYPASS_WARNING,
        "would_auto_advance": False,
        "human_paste_required": True,
        # 11 -- future-ready ready-for-commit field (no unit built yet -> None)
        "ready_for_commit": False,
        "ready_for_commit_unit": None,
        "commit_approval_text": build_commit_approval_text(None),
        # posture
        "requires_human_approval": True,
        "executes_nothing": True,
        "advances_c17": False,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def validate_human_gate_workflow(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the workflow is research-only,
    workflow-only, mirrors the lane's CURRENT gate, carries a copyable approval
    text containing the gate token + the recommended decision + the stop-before-
    commit guard, lists the research-only allows and the full forbid set, advances
    nothing (no auto-advance, no C17 advance), keeps downstream gates locked, and
    pins every capability flag False."""
    failures: list = []
    if record.get("mode") != HGW_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_workflow_only") is not True:
        failures.append("not_pure_workflow_only")

    # mirrors the lane's CURRENT directive
    lane = _lane.get_lane_status()
    if record.get("active_candidate") != lane.get("active_candidate"):
        failures.append("active_candidate_mismatch")
    if record.get("current_human_gate") != lane.get("next_required_action"):
        failures.append("current_gate_mismatch")
    if record.get("current_stage_label") != (
            lane.get("active_candidate_detail") or {}).get("stage_label"):
        failures.append("stage_label_mismatch")

    # recommended decision is always present
    if not record.get("recommended_decision"):
        failures.append("recommended_decision_missing")
    has_gate = record.get("has_open_human_gate") is True
    # the workflow must agree with the lane on whether a human gate is open
    if has_gate != (lane.get("open_candidate_gate") is True):
        failures.append("open_gate_state_mismatch")

    if has_gate:
        # an open candidate gate -> a full copyable approval text is required
        txt = record.get("approval_text_to_paste") or ""
        if not txt:
            failures.append("approval_text_missing")
        else:
            if record.get("current_human_gate") not in txt:
                failures.append("approval_text_missing_gate_token")
            if str(record.get("recommended_decision")) not in txt:
                failures.append("approval_text_missing_decision")
            if "Do not commit or push" not in txt:
                failures.append("approval_text_missing_stop_guard")
        # allows (research-only) -- gate-INVARIANT checks
        allows = record.get("approval_allows") or []
        if not allows:
            failures.append("allows_empty")
        if not any("research-only validation" in a for a in allows):
            failures.append("allows_missing_validation")
    else:
        # NO open candidate gate -> there must be NO copyable approval text
        if record.get("approval_text_to_paste") is not None:
            failures.append("approval_text_should_be_none_when_no_gate")
        if record.get("reject_text_to_paste") is not None:
            failures.append("reject_text_should_be_none_when_no_gate")

    # forbids -- gate-INVARIANT (operational forbids present in BOTH states).
    forbids = " || ".join(record.get("approval_forbids") or []).lower()
    # every gate must forbid: real data fetch, replay/backtest/PnL, optimization,
    # and paper/live/broker/order.
    for must in ("data fetch", "replay", "optimization",
                 "paper/live/broker/order"):
        if must not in forbids:
            failures.append("forbids_missing_%s" % must.split("/")[0].strip())

    # advances nothing
    if record.get("would_auto_advance") is not False:
        failures.append("would_auto_advance_true")
    if record.get("advances_c17") is not False:
        failures.append("advances_c17_true")
    if record.get("executes_nothing") is not True:
        failures.append("executes_something")
    if record.get("human_paste_required") is not True:
        failures.append("human_paste_not_required")
    if not record.get("gate_bypass_warning"):
        failures.append("bypass_warning_missing")

    # future-ready commit field empty now
    if record.get("ready_for_commit") is not False:
        failures.append("ready_for_commit_should_be_false")
    if record.get("commit_approval_text") is not None:
        failures.append("commit_text_should_be_none")

    # downstream locked
    if record.get("downstream_gates_locked") is not True:
        failures.append("downstream_not_locked")
    locks = record.get("safety_locks") or {}
    if locks.get("real_data_qa") != _lane.STATE_BLOCKED:
        failures.append("real_data_qa_not_blocked")
    if locks.get("replay") != _lane.STATE_BLOCKED:
        failures.append("replay_not_blocked")
    if locks.get("paper_trading") != _lane.STATE_LOCKED:
        failures.append("paper_not_locked")
    if locks.get("live_trading") != _lane.STATE_LOCKED:
        failures.append("live_not_locked")

    sl = record.get("scope_locks") or {}
    for key in ("no_execute", "no_advance_gate", "no_auto_apply", "no_build",
                "no_detector_spec", "no_dry_run_build", "no_detector_run",
                "no_labels", "no_replay", "no_pnl", "no_optimization",
                "no_data_fetch", "no_commit", "no_push", "no_broker",
                "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_gate_skip", "no_human_gate_bypass"):
        if sl.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}


def summarize_for_panel() -> dict[str, Any]:
    """Pure compact block for the JARVIS panel. Read-only; executes nothing."""
    r = build_human_gate_workflow()
    return {
        "active_candidate": r["active_candidate"],
        "has_open_human_gate": r["has_open_human_gate"],
        "current_stage_label": r["current_stage_label"],
        "current_human_gate": r["current_human_gate"],
        "recommended_decision": r["recommended_decision"],
        "approval_text_to_paste": r["approval_text_to_paste"],
        "reject_text_to_paste": r["reject_text_to_paste"],
        "approval_allows": r["approval_allows"],
        "approval_forbids": r["approval_forbids"],
        "downstream_gates_locked": r["downstream_gates_locked"],
        "gate_bypass_warning": r["gate_bypass_warning"],
        "would_auto_advance": r["would_auto_advance"],
        "ready_for_commit": r["ready_for_commit"],
        "commit_approval_text": r["commit_approval_text"],
        "executes_nothing": r["executes_nothing"],
    }

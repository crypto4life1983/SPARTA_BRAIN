"""SPARTA candidate-lifecycle ORCHESTRATOR -- PURE, READ-ONLY, SUGGESTION-ONLY.

Computes the CURRENT candidate/lane gate and the SUGGESTED next human token from the
committed lane state -- WITHOUT advancing anything. It reads the C22 current morning packet
(which reads the realigned lane-status v2 + tracker) for the lane/progress/C23 facts and
maps them to a single current gate + one suggested human token.

Gates (closed set):
  * C22_COLLECT_MORE_WINDOWS           -- C22 active, < 20/20  -> suggest the collect token;
  * C22_READY_FOR_FROZEN_WINDOW_REVIEW -- C22 active, >= 20/20 -> suggest the review token;
  * C23_WAITING_FOR_C22_CONCLUSION     -- the C23 sub-gate while C22 is still active;
  * C23_MAY_OPEN_AFTER_C22_CONCLUDED   -- ONLY when C22 has concluded -> suggest the open
    C23 decision token.

It is suggestion-only: it NEVER advances a candidate, NEVER opens C23 as active, NEVER runs
labels/replay, NEVER auto-executes a token, and modifies NO repo state. `c22_concluded`
defaults to False (C22 is the active collection lane at HOLD); only an explicit committed
conclusion would set it True -- the orchestrator never decides it. Every dangerous capability
is pinned False.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.sparta_c22_current_morning_packet_contract as _c22cur

LO_SCHEMA_VERSION = 1
LO_MODE = "RESEARCH_ONLY"
LO_LANE = "crypto_d1_auto_research"

COLLECT_TOKEN = _c22cur.COLLECT_TOKEN
REVIEW_TOKEN = _c22cur.REVIEW_TOKEN
C23_OPEN_TOKEN = _c22cur.C23_OPEN_GATE

# gates (closed set)
GATE_C22_COLLECT = "C22_COLLECT_MORE_WINDOWS"
GATE_C22_READY = "C22_READY_FOR_FROZEN_WINDOW_REVIEW"
GATE_C23_WAITING = "C23_WAITING_FOR_C22_CONCLUSION"
GATE_C23_MAY_OPEN = "C23_MAY_OPEN_AFTER_C22_CONCLUDED"
ALL_GATES = (GATE_C22_COLLECT, GATE_C22_READY, GATE_C23_WAITING, GATE_C23_MAY_OPEN)

VERDICT_LIFECYCLE = "SPARTA_CANDIDATE_LIFECYCLE_STATE"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "advances_any_candidate", "opens_c23_as_active", "advances_c22",
    "runs_labels", "runs_replay", "builds_replay", "optimizes_parameters",
    "auto_executes_any_token", "modifies_repo", "modifies_c21_logic",
    "modifies_c22_pipeline", "modifies_c23_proposal", "changes_scheduled_task",
    "installs_scheduler", "fetches_data", "performs_network_io", "connects_signum",
    "uses_mcp", "calls_api", "uses_credentials", "places_orders", "sends_trades",
    "paper_trading", "live_trading", "reopens_c21", "crosses_into_forbidden_gate",
)


def build_lifecycle(collected_windows: int | None = None,
                    c22_concluded: bool = False) -> dict[str, Any]:
    """PURE. Map the committed lane state to the current gate + one suggested human token.
    No I/O; advances nothing. `c22_concluded` is an explicit input (default False = C22 is
    the active collection lane); the orchestrator never decides it."""
    cur = _c22cur.build_c22_current_morning_packet(collected_windows)
    collected = cur["collected_windows"]
    required = cur["required_windows"]
    ready = cur["ready_for_review"]

    if c22_concluded:
        current_gate = GATE_C23_MAY_OPEN
        c23_gate = GATE_C23_MAY_OPEN
        suggested = C23_OPEN_TOKEN
    elif ready:
        current_gate = GATE_C22_READY
        c23_gate = GATE_C23_WAITING
        suggested = REVIEW_TOKEN
    else:
        current_gate = GATE_C22_COLLECT
        c23_gate = GATE_C23_WAITING
        suggested = COLLECT_TOKEN

    record: dict[str, Any] = {
        "schema_version": LO_SCHEMA_VERSION, "mode": LO_MODE, "lane": LO_LANE,
        "is_lifecycle_orchestrator": True, "is_suggestion_only": True,
        "verdict": VERDICT_LIFECYCLE,
        "label": (
            "SPARTA candidate-lifecycle orchestrator (READ-ONLY, SUGGESTION ONLY). Computes "
            "the current gate + one suggested human token from the committed lane state; "
            "advances no candidate, opens no C23, runs no labels/replay, executes no token, "
            "modifies no repo."),
        # current lifecycle state (single-sourced)
        "lifecycle_state": {
            "c21_closed_rejected": cur["c21_closed_rejected"],
            "rejected_ledger_count": cur["rejected_ledger_count"],
            "c22_active_collection_lane": not c22_concluded,
            "c22_state": cur["c22_state"],
            "c22_replay_locked": cur["c22_replay_locked"],
            "c22_collected_windows": collected,
            "c22_required_windows": required,
            "c22_progress": cur["collection_progress"],
            "c22_ready_for_review": ready,
            "c22_concluded": bool(c22_concluded),
            "c23_on_deck": cur["c23_on_deck"],
            "c23_is_active": cur["c23_is_active"],
            "c23_proposal_frozen": cur["c23_proposal_frozen"],
        },
        # gates
        "current_gate": current_gate,
        "c22_gate": (GATE_C23_MAY_OPEN if c22_concluded
                     else (GATE_C22_READY if ready else GATE_C22_COLLECT)),
        "c23_gate": c23_gate,
        # the single suggested human token (suggestion only, never executed)
        "suggested_human_token": suggested,
        "suggested_token_is_suggestion_only": True,
        "token_must_be_pasted_by_human": True,
        # explicit guarantee flags (per the bundle spec)
        "advances_any_candidate": False,
        "opens_c23_as_active": False,
        "runs_labels": False,
        "runs_replay": False,
        "auto_executes_any_token": False,
        "modifies_repo": False,
        "advances_nothing": True, "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_advance_candidate": True, "no_open_c23_active": True,
        "no_advance_c22": True, "no_run_labels": True, "no_replay": True,
        "no_optimization": True, "no_auto_execute_token": True, "no_modify_repo": True,
        "no_modify_c21_logic": True, "no_modify_c22_pipeline": True,
        "no_modify_c23_proposal": True, "no_change_scheduled_task": True,
        "no_install_scheduler": True, "no_data_fetch": True, "no_network_io": True,
        "no_signum_connection": True, "no_mcp": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_reopen_c21": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_lifecycle(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, suggestion-only; the gate is
    from the closed set and consistent with the state (collect < 20 / ready >= 20 / C23 may
    open only when concluded); the suggested token matches the gate; and every advance/open/
    run/execute/modify flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != LO_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_lifecycle_orchestrator") is not True:
        failures.append("not_lifecycle_orchestrator")
    if r.get("is_suggestion_only") is not True:
        failures.append("not_suggestion_only")
    if r.get("verdict") != VERDICT_LIFECYCLE:
        failures.append("bad_verdict")
    if r.get("current_gate") not in ALL_GATES:
        failures.append("bad_current_gate")
    if r.get("c23_gate") not in (GATE_C23_WAITING, GATE_C23_MAY_OPEN):
        failures.append("bad_c23_gate")

    st = r.get("lifecycle_state") or {}
    concluded = st.get("c22_concluded") is True
    ready = st.get("c22_ready_for_review") is True
    collected = st.get("c22_collected_windows")
    required = st.get("c22_required_windows")

    # gate <-> state consistency
    if concluded:
        expected_gate, expected_token, expected_c23 = (
            GATE_C23_MAY_OPEN, C23_OPEN_TOKEN, GATE_C23_MAY_OPEN)
    elif ready:
        expected_gate, expected_token, expected_c23 = (
            GATE_C22_READY, REVIEW_TOKEN, GATE_C23_WAITING)
    else:
        expected_gate, expected_token, expected_c23 = (
            GATE_C22_COLLECT, COLLECT_TOKEN, GATE_C23_WAITING)
    if r.get("current_gate") != expected_gate:
        failures.append("current_gate_inconsistent")
    if r.get("c23_gate") != expected_c23:
        failures.append("c23_gate_inconsistent")
    if r.get("suggested_human_token") != expected_token:
        failures.append("suggested_token_inconsistent")
    # readiness must agree with the count
    if isinstance(collected, int) and isinstance(required, int):
        if ready is not (collected >= required):
            failures.append("ready_inconsistent_with_count")

    # C21 closed / ledger / C23 not active
    if st.get("c21_closed_rejected") is not True:
        failures.append("c21_not_closed")
    if st.get("rejected_ledger_count") != 26:
        failures.append("ledger_not_26")
    if st.get("c23_is_active") is not False:
        failures.append("c23_must_not_be_active")

    # suggestion-only + never-advance guarantee flags
    if r.get("suggested_token_is_suggestion_only") is not True:
        failures.append("token_not_suggestion_only")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")
    for k in ("advances_any_candidate", "opens_c23_as_active", "runs_labels",
              "runs_replay", "auto_executes_any_token", "modifies_repo"):
        if r.get(k) is not False:
            failures.append("guarantee_flag_true_%s" % k)

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_advance_candidate", "no_open_c23_active",
                "no_advance_c22", "no_run_labels", "no_replay", "no_optimization",
                "no_auto_execute_token", "no_modify_repo", "no_modify_c21_logic",
                "no_modify_c22_pipeline", "no_modify_c23_proposal",
                "no_change_scheduled_task", "no_install_scheduler", "no_data_fetch",
                "no_network_io", "no_signum_connection", "no_mcp", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

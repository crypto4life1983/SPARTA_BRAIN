"""Candidate #22 -- Signum Trend Radar GC COLLECTION READINESS WATCHER
-- PURE, LOCAL-ONLY, RESEARCH ONLY.

The PURE decision core for the local readiness watcher. Given the per-window validity facts
the watcher tool gathered from a READ-ONLY scan of the approved dataset folder, it counts how
many VALID distinct frozen daily GC windows exist, reports progress (N/20), and decides:

  * NOT_READY_COLLECTING   -- fewer than the required windows -> keep collecting; surfaces
                              how many more are needed (no actionable token);
  * READY_FOR_HUMAN_REVIEW -- the threshold is reached -> surfaces the EXACT suggested next
                              human token: HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW.

It is a SUGGESTION surface only: it NEVER auto-runs the labels review, NEVER auto-runs
replay, and NEVER auto-sends or auto-executes the suggested token (a human must paste it). It
fetches NOTHING (no Signum / GC / API / MCP / browser / network), touches NO trading / broker
/ order / paper / live / optimizer / C21 / C23 surface, and performs NO I/O itself (the tool
does the read-only scan). Every dangerous capability is pinned False; C22 stays
HOLD_FOR_MORE_FROZEN_DATA_WINDOWS until a human acts.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk

RW_SCHEMA_VERSION = 1
RW_MODE = "RESEARCH_ONLY"
RW_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _trk.CANDIDATE_ID
DATA_DIR = _trk.DATA_DIR
REQUIRED_WINDOWS = _trk.REQUIRED_WINDOWS              # 20 (single-sourced)
C22_STATE = _trk.C22_STATE                            # HOLD_FOR_MORE_FROZEN_DATA_WINDOWS

STATUS_NOT_READY = "NOT_READY_COLLECTING"
STATUS_READY = "READY_FOR_HUMAN_REVIEW"

# the EXACT token a human would paste once enough valid windows exist (NEVER auto-executed).
SUGGESTED_REVIEW_TOKEN = "HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "auto_runs_labels_review", "auto_runs_replay", "auto_sends_token",
    "auto_executes_token", "performs_io", "performs_network_io", "connects_signum",
    "uses_gc_api", "uses_mcp", "uses_browser", "fetches_data", "calls_api",
    "uses_credentials", "uses_api_keys", "mutates_dataset", "runs_labels", "runs_replay",
    "builds_replay", "optimizes_parameters", "installs_scheduler", "triggers_scheduler",
    "modifies_scheduler", "edits_bots", "sends_trades", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "connects_broker", "connects_exchange", "modifies_c22_rules", "starts_c23",
    "reopens_c21", "auto_commits", "auto_pushes", "auto_advances",
    "crosses_into_forbidden_gate",
)


def build_readiness(window_facts: Any) -> dict[str, Any]:
    """PURE. Fold per-window validity facts into the readiness status. Each fact is
    {filename, date, valid}. Counts VALID distinct dates as windows. No I/O."""
    facts = [w for w in (window_facts or []) if isinstance(w, dict)]
    valid_dates = sorted({w.get("date") for w in facts
                          if w.get("valid") is True and w.get("date")})
    invalid_windows = [{"filename": w.get("filename"),
                        "reasons": list(w.get("reasons") or [])}
                       for w in facts if w.get("valid") is not True]

    n_valid = len(valid_dates)
    remaining = max(0, REQUIRED_WINDOWS - n_valid)
    ready = n_valid >= REQUIRED_WINDOWS
    status = STATUS_READY if ready else STATUS_NOT_READY
    progress = "%d/%d" % (n_valid, REQUIRED_WINDOWS)

    record: dict[str, Any] = {
        "schema_version": RW_SCHEMA_VERSION, "mode": RW_MODE, "lane": RW_LANE,
        "candidate_id": CANDIDATE_ID,
        "is_readiness_watcher_only": True, "is_suggestion_only": True,
        "label": (
            "Candidate #22 Signum GC collection readiness watcher (LOCAL-ONLY, RESEARCH "
            "ONLY, SUGGESTION ONLY). Counts valid frozen daily GC windows vs the required "
            "threshold and, when reached, SUGGESTS the human review token. Never auto-runs "
            "review/replay; never auto-executes the token; fetches nothing."),
        "data_dir": DATA_DIR,
        # progress
        "collected_valid_windows": n_valid,
        "valid_window_dates": list(valid_dates),
        "required_windows": REQUIRED_WINDOWS,
        "windows_remaining": remaining,
        "progress": progress,
        "invalid_windows": invalid_windows,
        # readiness
        "ready": ready,
        "status": status,
        # the suggested token is surfaced ONLY when ready; it is NEVER auto-executed
        "suggested_next_token": SUGGESTED_REVIEW_TOKEN if ready else None,
        "review_token_reference": SUGGESTED_REVIEW_TOKEN,
        "token_is_suggestion_for_human_to_paste": True,
        "auto_executes_token": False,
        # current candidate state (unchanged until a human acts)
        "c22_state": C22_STATE,
        "replay_locked": True,
        "advances_nothing": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_auto_run_labels_review": True, "no_auto_run_replay": True,
        "no_auto_send_token": True, "no_auto_execute_token": True, "no_io": True,
        "no_network_io": True, "no_signum_connection": True, "no_gc_api": True,
        "no_mcp": True, "no_browser": True, "no_data_fetch": True, "no_api_keys": True,
        "no_credentials": True, "no_mutate_dataset": True, "no_run_labels": True,
        "no_replay": True, "no_optimization": True, "no_install_scheduler": True,
        "no_trigger_scheduler": True, "no_bot_edits": True, "no_trades": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_broker": True, "no_modify_c22_rules": True, "no_start_c23": True,
        "no_reopen_c21": True, "no_auto_commit": True, "no_auto_push": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_readiness(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, watcher-only, suggestion-only;
    the status matches the valid-window count vs the threshold; the suggested token is the
    exact constant when READY and None when NOT_READY; the token is never auto-executed; no
    labels/replay auto-run; C22 stays HOLD; and every capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != RW_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_readiness_watcher_only") is not True:
        failures.append("not_watcher_only")
    if r.get("is_suggestion_only") is not True:
        failures.append("not_suggestion_only")
    if r.get("status") not in (STATUS_READY, STATUS_NOT_READY):
        failures.append("bad_status")
    if r.get("required_windows") != REQUIRED_WINDOWS:
        failures.append("required_windows_tampered")

    n = r.get("collected_valid_windows")
    if not isinstance(n, int) or n < 0:
        failures.append("bad_window_count")
    else:
        expect_ready = n >= REQUIRED_WINDOWS
        if r.get("ready") is not expect_ready:
            failures.append("ready_inconsistent_with_count")
        if r.get("status") != (STATUS_READY if expect_ready else STATUS_NOT_READY):
            failures.append("status_inconsistent_with_count")
        if r.get("windows_remaining") != max(0, REQUIRED_WINDOWS - n):
            failures.append("windows_remaining_inconsistent")
        # suggested token surfaced ONLY when ready
        if expect_ready and r.get("suggested_next_token") != SUGGESTED_REVIEW_TOKEN:
            failures.append("ready_must_surface_exact_token")
        if (not expect_ready) and r.get("suggested_next_token") is not None:
            failures.append("not_ready_must_not_surface_token")

    if r.get("review_token_reference") != SUGGESTED_REVIEW_TOKEN:
        failures.append("token_reference_tampered")
    if r.get("auto_executes_token") is not False:
        failures.append("token_must_not_auto_execute")
    if r.get("token_is_suggestion_for_human_to_paste") is not True:
        failures.append("token_not_marked_suggestion")

    # state
    if r.get("c22_state") != C22_STATE:
        failures.append("c22_state_wrong")
    if r.get("replay_locked") is not True:
        failures.append("replay_not_locked")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_auto_run_labels_review", "no_auto_run_replay",
                "no_auto_send_token", "no_auto_execute_token", "no_io", "no_network_io",
                "no_signum_connection", "no_gc_api", "no_mcp", "no_browser",
                "no_data_fetch", "no_api_keys", "no_mutate_dataset", "no_run_labels",
                "no_replay", "no_optimization", "no_install_scheduler",
                "no_trigger_scheduler", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_modify_c22_rules", "no_start_c23", "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

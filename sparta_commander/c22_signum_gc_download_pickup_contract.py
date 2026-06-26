"""Candidate #22 -- Signum Trend Radar GC DOWNLOAD PICKUP ORCHESTRATION
-- PURE, LOCAL-ONLY, RESEARCH ONLY.

The PURE decision/summary core for the local download-pickup automation. It reduces the
human step to "download/export the daily GC JSON into a local drop folder (e.g. Downloads)";
SPARTA then scans that approved local folder, validates each candidate with the EXISTING C22
importer rules, copies ONLY valid GC exports into the inbox under the deterministic runDate
name, and chains the existing import automation + readiness watcher.

It is PURE: it classifies an ALREADY-PARSED candidate (the tool reads the local file) and
folds the pickup results + the readiness status into one summary. It performs NO Signum
login, NO fetch (Signum/GC/browser/API/MCP/network), stores NO credentials/cookies/tokens/
session files, never overwrites or mutates, and NEVER auto-executes the suggested human
review token. At the threshold the readiness watcher's suggested token
(HUMAN_APPROVED_C22_SIGNUM_GC_FROZEN_DATA_WINDOW_REVIEW) is surfaced as a suggestion only.
C22 stays HOLD_FOR_MORE_FROZEN_DATA_WINDOWS with replay locked.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.c22_signum_gc_local_export_importer_contract as _imp
import sparta_commander.c22_signum_gc_collection_readiness_watcher_contract as _rw

PK_SCHEMA_VERSION = 1
PK_MODE = "RESEARCH_ONLY"
PK_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _imp.CANDIDATE_ID
INBOX_DIR = _imp.INBOX_DIR
DEST_DIR = _imp.DEST_DIR
C22_STATE = _imp.C22_STATE                              # HOLD_FOR_MORE_FROZEN_DATA_WINDOWS

PICKUP_OK = "PICKUP_OK"
PICKUP_DUPLICATE = "PICKUP_DUPLICATE_WINDOW"
PICKUP_IGNORED_INVALID = "PICKUP_IGNORED_INVALID"

_CAPABILITY_FLAGS_FALSE = (
    "executes_unsafely", "performs_signum_login", "fetches_data",
    "performs_network_io", "performs_browser_automation", "opens_browser", "calls_api",
    "uses_mcp", "connects_signum", "accesses_hyperliquid", "stores_credentials",
    "stores_cookies", "stores_tokens", "stores_passwords", "stores_session_files",
    "uses_api_keys", "mutates_json_contents", "overwrites_destination",
    "scans_outside_approved_folders", "auto_executes_token", "auto_runs_labels_review",
    "auto_runs_replay", "runs_labels", "runs_replay", "builds_replay",
    "optimizes_parameters", "edits_bots", "sends_trades", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "connects_broker",
    "installs_scheduler", "triggers_scheduler", "modifies_c22_rules", "starts_c23",
    "reopens_c21", "auto_commits", "auto_pushes", "auto_advances",
    "crosses_into_forbidden_gate",
)


def classify_drop_candidate(parsed: dict, already_collected_dates: Any,
                            today: Any = None, raw_bytes: Any = None,
                            compact_bytes: Any = None) -> dict[str, Any]:
    """PURE. Classify one parsed drop-folder candidate by reusing the committed importer
    decision: PICKUP_OK (valid + new date), PICKUP_DUPLICATE_WINDOW (valid + already
    collected), PICKUP_IGNORED_INVALID (not a valid GC export, OR future-dated, OR
    anomalous-shape relative to the supplied local date / sizes). Derives the deterministic
    inbox filename from runDate. No I/O; never mutates. When ``today`` and/or ``raw_bytes``
    are supplied, a future-dated OR shape/size-anomalous export is NOT picked up (it never
    enters the inbox), so such files cannot reach active collection."""
    decision = _imp.build_import_decision(parsed, already_collected_dates, today=today,
                                          raw_bytes=raw_bytes, compact_bytes=compact_bytes)
    v = decision["verdict"]
    if v == _imp.VERDICT_IMPORT_OK:
        verdict, should = PICKUP_OK, True
    elif v == _imp.VERDICT_DUPLICATE:
        verdict, should = PICKUP_DUPLICATE, False
    else:  # INVALID / FUTURE_DATED / ANOMALOUS -> ignored, never copied into the inbox
        verdict, should = PICKUP_IGNORED_INVALID, False
    return {
        "verdict": verdict, "should_pickup": should,
        "run_date": decision["run_date"],
        "inbox_filename": decision["destination_filename"],
        "reasons": list(decision["reasons"]),
    }


def summarize_pickup_chain(scanned: int, pickup_results: Any,
                           readiness: dict) -> dict[str, Any]:
    """PURE. Fold the pickup results + the readiness status into one chain summary. No I/O.
    The suggested review token is passed through from the readiness watcher (None unless the
    threshold is reached) and is NEVER auto-executed."""
    res = list(pickup_results or [])
    picked = [r for r in res if r.get("copied") is True]
    dupes = [r for r in res if r.get("verdict") == PICKUP_DUPLICATE]
    ignored = [r for r in res if r.get("verdict") == PICKUP_IGNORED_INVALID]
    rd = readiness or {}
    ready = rd.get("ready") is True
    token = rd.get("suggested_next_token") if ready else None

    record: dict[str, Any] = {
        "schema_version": PK_SCHEMA_VERSION, "mode": PK_MODE, "lane": PK_LANE,
        "candidate_id": CANDIDATE_ID,
        "is_download_pickup_only": True, "local_only": True,
        "label": (
            "Candidate #22 Signum GC download-pickup chain (LOCAL-ONLY, RESEARCH ONLY). "
            "Validates drop-folder candidates with the importer rules, copies only valid GC "
            "exports into the inbox (never overwrite/mutate), then reports the readiness "
            "progress. Suggestion only: never auto-runs review/replay; never auto-executes "
            "the token; no login/fetch/browser/api/mcp/network/credentials."),
        "inbox_dir": INBOX_DIR, "dest_dir": DEST_DIR,
        "scans_only_approved_drop_and_inbox": True,
        # pickup phase
        "drop_scanned": scanned,
        "picked_up": len(picked),
        "duplicates": len(dupes),
        "ignored_invalid": len(ignored),
        "picked_up_filenames": [r.get("inbox_filename") for r in picked],
        "pickup_results": res,
        "never_overwrites": True, "never_mutates_json": True,
        # readiness phase (passed through)
        "readiness": {
            "status": rd.get("status"),
            "progress": rd.get("progress"),
            "collected_valid_windows": rd.get("collected_valid_windows"),
            "required_windows": rd.get("required_windows"),
            "windows_remaining": rd.get("windows_remaining"),
            "ready": ready},
        "overall_status": rd.get("status"),
        "ready_for_human_review": ready,
        "suggested_next_token": token,
        "review_token_reference": _rw.SUGGESTED_REVIEW_TOKEN,
        "token_is_suggestion_for_human_to_paste": True,
        "auto_executes_token": False,
        # state
        "c22_state": C22_STATE, "replay_locked": True,
        "advances_nothing": True, "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_unsafe_execute": True, "no_signum_login": True, "no_fetch": True,
        "no_network_io": True, "no_browser_automation": True, "no_open_browser": True,
        "no_api_call": True, "no_mcp": True, "no_signum_connection": True,
        "no_store_credentials": True, "no_store_cookies": True, "no_store_tokens": True,
        "no_store_session_files": True, "no_api_keys": True, "no_mutate_json": True,
        "no_overwrite_destination": True, "no_scan_outside_approved_folders": True,
        "no_auto_execute_token": True, "no_auto_run_labels_review": True,
        "no_auto_run_replay": True, "no_run_labels": True, "no_replay": True,
        "no_optimization": True, "no_bot_edits": True, "no_trades": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_broker": True, "no_install_scheduler": True, "no_trigger_scheduler": True,
        "no_modify_c22_rules": True, "no_start_c23": True, "no_reopen_c21": True,
        "no_auto_commit": True, "no_auto_push": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_pickup_chain(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, download-pickup-only; the chain
    never overwrites/mutates; the suggested token is surfaced ONLY when ready and is never
    auto-executed; no labels/replay auto-run; only approved folders are touched; C22 stays
    HOLD with replay locked; and every capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != PK_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_download_pickup_only") is not True:
        failures.append("not_download_pickup_only")

    for k in ("drop_scanned", "picked_up", "duplicates", "ignored_invalid"):
        if not isinstance(r.get(k), int) or r.get(k) < 0:
            failures.append("bad_count_%s" % k)

    # no overwrite / no mutate
    if r.get("never_overwrites") is not True:
        failures.append("must_not_overwrite")
    if r.get("never_mutates_json") is not True:
        failures.append("must_not_mutate_json")
    if r.get("overwrites_destination") is not False:
        failures.append("overwrites_flag_true")
    if r.get("mutates_json_contents") is not False:
        failures.append("mutates_flag_true")

    # readiness + token: surfaced only when ready, never auto-executed
    ready = r.get("ready_for_human_review") is True
    rd = r.get("readiness") or {}
    if rd.get("ready") is not ready:
        failures.append("readiness_inconsistent")
    if r.get("overall_status") not in (
            _rw.STATUS_READY, _rw.STATUS_NOT_READY):
        failures.append("bad_overall_status")
    if ready and r.get("suggested_next_token") != _rw.SUGGESTED_REVIEW_TOKEN:
        failures.append("ready_must_surface_exact_token")
    if (not ready) and r.get("suggested_next_token") is not None:
        failures.append("not_ready_must_not_surface_token")
    if r.get("review_token_reference") != _rw.SUGGESTED_REVIEW_TOKEN:
        failures.append("token_reference_tampered")
    if r.get("auto_executes_token") is not False:
        failures.append("token_must_not_auto_execute")

    # state
    if r.get("c22_state") != C22_STATE:
        failures.append("c22_state_wrong")
    if r.get("replay_locked") is not True:
        failures.append("replay_not_locked")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_unsafe_execute", "no_signum_login", "no_fetch", "no_network_io",
                "no_browser_automation", "no_api_call", "no_mcp", "no_store_credentials",
                "no_store_cookies", "no_store_tokens", "no_store_session_files",
                "no_api_keys", "no_mutate_json", "no_overwrite_destination",
                "no_scan_outside_approved_folders", "no_auto_execute_token",
                "no_auto_run_labels_review", "no_auto_run_replay", "no_run_labels",
                "no_replay", "no_optimization", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_modify_c22_rules", "no_start_c23", "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

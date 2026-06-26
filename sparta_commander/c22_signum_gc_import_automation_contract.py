"""Candidate #22 -- Signum Trend Radar GC LOCAL IMPORT AUTOMATION
-- PURE, LOCAL-ONLY, RESEARCH ONLY.

The PURE summary core for the local import automation layer that runs the existing local
importer against the approved inbox and reports ONE clean overall status. It is PURE: it
operates on the per-file import results the importer already produced (the automation tool
does the local scan/import via the committed importer) and folds them into an overall
status. It performs NO file or network I/O, connects to NO Signum / MCP / Hyperliquid,
fetches NO data, and runs NO labels / replay / optimization.

Overall status (closed set):
  * NO_NEW_EXPORT     -- the inbox held nothing to scan;
  * IMPORTED          -- one or more new valid exports were imported this run;
  * DUPLICATE_WINDOW  -- every scanned file was already imported (no new windows);
  * INVALID_ONLY      -- every scanned file was structurally invalid;
  * MIXED_NO_IMPORT   -- a mix of duplicates + invalids, nothing new imported.

The automation is IDEMPOTENT by construction: the underlying importer never overwrites and
never mutates JSON, so re-running after a successful import yields DUPLICATE_WINDOW with zero
new writes. Every dangerous capability is pinned False with a full scope_locks set; C22 stays
HOLD_FOR_MORE_FROZEN_DATA_WINDOWS.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.c22_signum_gc_local_export_importer_contract as _imp

AUTO_SCHEMA_VERSION = 1
AUTO_MODE = "RESEARCH_ONLY"
AUTO_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _imp.CANDIDATE_ID
INBOX_DIR = _imp.INBOX_DIR
DEST_DIR = _imp.DEST_DIR
C22_STATE = _imp.C22_STATE                              # HOLD_FOR_MORE_FROZEN_DATA_WINDOWS

STATUS_NO_NEW_EXPORT = "NO_NEW_EXPORT"
STATUS_IMPORTED = "IMPORTED"
STATUS_DUPLICATE_WINDOW = "DUPLICATE_WINDOW"
STATUS_INVALID_ONLY = "INVALID_ONLY"
STATUS_MIXED_NO_IMPORT = "MIXED_NO_IMPORT"

ALL_STATUSES = (STATUS_NO_NEW_EXPORT, STATUS_IMPORTED, STATUS_DUPLICATE_WINDOW,
                STATUS_INVALID_ONLY, STATUS_MIXED_NO_IMPORT)

_CAPABILITY_FLAGS_FALSE = (
    "executes_unsafely", "performs_network_io", "connects_signum", "uses_mcp",
    "accesses_hyperliquid", "fetches_data", "calls_api", "uses_credentials",
    "uses_api_keys", "mutates_json_contents", "overwrites_destination",
    "scans_outside_approved_inbox", "writes_outside_approved_dataset", "edits_bots",
    "sends_trades", "places_orders", "contains_order_logic", "paper_trading",
    "live_trading", "deploys_capital", "connects_broker", "connects_exchange",
    "creates_claude_routines", "runs_claude_routine", "runs_labels", "runs_replay",
    "builds_replay", "optimizes_parameters", "installs_scheduler", "triggers_scheduler",
    "modifies_scheduler", "modifies_autopilot_config", "modifies_c22_rules", "starts_c23",
    "reopens_c21", "auto_commits", "auto_pushes", "auto_fetches", "auto_promotes",
    "auto_advances", "commits_inbox_or_dataset", "crosses_into_forbidden_gate",
)


def summarize_automation_run(scanned: int, results: Any) -> dict[str, Any]:
    """PURE. Fold the importer's per-file results into ONE clean automation status. No I/O;
    derives nothing from disk."""
    res = list(results or [])
    imported = [r for r in res if r.get("imported") is True]
    duplicates = [r for r in res
                  if r.get("verdict") == _imp.VERDICT_DUPLICATE]
    # A FUTURE_DATED or ANOMALOUS_SHAPE export is rejected (never imported); count it with the
    # invalids so the overall status honestly reflects "nothing valid imported this run".
    invalids = [r for r in res if r.get("verdict") in (
        _imp.VERDICT_INVALID, _imp.VERDICT_FUTURE_DATED, _imp.VERDICT_ANOMALOUS)]
    n_imported = len(imported)
    n_dupes = len(duplicates)
    n_invalid = len(invalids)

    if scanned == 0:
        status = STATUS_NO_NEW_EXPORT
    elif n_imported > 0:
        status = STATUS_IMPORTED
    elif n_dupes > 0 and n_invalid == 0:
        status = STATUS_DUPLICATE_WINDOW
    elif n_invalid > 0 and n_dupes == 0:
        status = STATUS_INVALID_ONLY
    elif n_dupes > 0 and n_invalid > 0:
        status = STATUS_MIXED_NO_IMPORT
    else:
        status = STATUS_NO_NEW_EXPORT

    record: dict[str, Any] = {
        "schema_version": AUTO_SCHEMA_VERSION, "mode": AUTO_MODE, "lane": AUTO_LANE,
        "candidate_id": CANDIDATE_ID,
        "is_import_automation_only": True, "local_only": True,
        "label": (
            "Candidate #22 Signum GC local import automation summary (LOCAL-ONLY, RESEARCH "
            "ONLY). Runs the existing importer against the approved inbox and reports one "
            "clean status. Idempotent: re-running after import yields DUPLICATE_WINDOW with "
            "no new writes. Connects to nothing; runs no labels/replay; advances nothing."),
        "inbox_dir": INBOX_DIR, "dest_dir": DEST_DIR,
        "scans_only_approved_inbox": True,
        "writes_only_approved_dataset": True,
        # counts
        "scanned": scanned,
        "new_imports": n_imported,
        "duplicates": n_dupes,
        "invalid": n_invalid,
        "imported_filenames": [r.get("destination_filename") for r in imported],
        "results": res,
        # status
        "overall_status": status,
        "is_idempotent": True,
        "never_overwrites": True, "never_mutates_json": True,
        "never_commits_inbox_or_dataset": True,
        # current candidate state
        "c22_state": C22_STATE, "replay_locked": True,
        "advances_nothing": True, "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_unsafe_execute": True, "no_network_io": True, "no_signum_connection": True,
        "no_mcp": True, "no_hyperliquid": True, "no_data_fetch": True, "no_api_keys": True,
        "no_credentials": True, "no_mutate_json": True, "no_overwrite_destination": True,
        "no_scan_outside_inbox": True, "no_write_outside_dataset": True,
        "no_bot_edits": True, "no_trades": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
        "no_claude_routine": True, "no_run_labels": True, "no_replay": True,
        "no_optimization": True, "no_install_scheduler": True,
        "no_trigger_scheduler": True, "no_modify_autopilot_config": True,
        "no_modify_c22_rules": True, "no_start_c23": True, "no_reopen_c21": True,
        "no_auto_commit": True, "no_auto_push": True, "no_commit_inbox_or_dataset": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_automation_summary(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, import-automation-only; the
    overall status is from the closed set and consistent with the counts; the run is
    idempotent / never-overwrite / never-mutate / never-commit; only the approved inbox is
    scanned and only the approved dataset written; C22 stays HOLD; and every capability flag
    is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != AUTO_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_import_automation_only") is not True:
        failures.append("not_import_automation_only")
    if r.get("overall_status") not in ALL_STATUSES:
        failures.append("bad_status")

    # status consistent with the counts
    scanned = r.get("scanned")
    n_imp = r.get("new_imports")
    n_dup = r.get("duplicates")
    n_inv = r.get("invalid")
    status = r.get("overall_status")
    if not all(isinstance(x, int) and x >= 0 for x in (scanned, n_imp, n_dup, n_inv)):
        failures.append("bad_counts")
    else:
        if scanned == 0 and status != STATUS_NO_NEW_EXPORT:
            failures.append("empty_scan_must_be_no_new_export")
        if status == STATUS_IMPORTED and n_imp <= 0:
            failures.append("imported_status_without_imports")
        if status == STATUS_DUPLICATE_WINDOW and not (n_imp == 0 and n_dup > 0):
            failures.append("duplicate_status_inconsistent")
        if status == STATUS_INVALID_ONLY and not (n_imp == 0 and n_inv > 0
                                                  and n_dup == 0):
            failures.append("invalid_only_status_inconsistent")
        if status == STATUS_IMPORTED and len(r.get("imported_filenames") or []) != n_imp:
            failures.append("imported_filenames_count_mismatch")

    # approved-folder + safety invariants
    if r.get("inbox_dir") != INBOX_DIR:
        failures.append("inbox_dir_wrong")
    if r.get("dest_dir") != DEST_DIR:
        failures.append("dest_dir_wrong")
    if r.get("scans_only_approved_inbox") is not True:
        failures.append("must_scan_only_inbox")
    if r.get("writes_only_approved_dataset") is not True:
        failures.append("must_write_only_dataset")
    for k in ("is_idempotent", "never_overwrites", "never_mutates_json",
              "never_commits_inbox_or_dataset"):
        if r.get(k) is not True:
            failures.append("missing_invariant_%s" % k)

    # state
    if r.get("c22_state") != C22_STATE:
        failures.append("c22_state_wrong")
    if r.get("replay_locked") is not True:
        failures.append("replay_not_locked")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_unsafe_execute", "no_network_io", "no_signum_connection", "no_mcp",
                "no_hyperliquid", "no_data_fetch", "no_api_keys", "no_mutate_json",
                "no_overwrite_destination", "no_scan_outside_inbox",
                "no_write_outside_dataset", "no_bot_edits", "no_trades",
                "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_claude_routine", "no_run_labels", "no_replay", "no_optimization",
                "no_install_scheduler", "no_trigger_scheduler",
                "no_modify_autopilot_config", "no_modify_c22_rules", "no_start_c23",
                "no_reopen_c21", "no_commit_inbox_or_dataset"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

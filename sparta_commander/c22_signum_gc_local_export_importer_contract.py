"""Candidate #22 -- Signum Trend Radar GC LOCAL EXPORT IMPORTER
-- PURE, LOCAL-ONLY, RESEARCH ONLY.

The PURE decision core for importing a locally-saved Signum Trend Radar GC daily export
JSON (produced by the EXTERNAL read-only Claude Routine) from a local inbox into the C22
dataset folder. It is PURE: it operates on an ALREADY-PARSED JSON dict (the importer tool
reads the local file and passes it in) and on the set of decision-dates the destination
already holds; it performs NO file or network I/O, connects to NO Signum / MCP /
Hyperliquid, fetches NO data, and NEVER mutates the JSON contents.

It validates the export structurally (>=50 rows by `total` or `results` length; every row
detector=gc + assetClass=crypto; a single runDate; indicators.data with latest + previous
closed daily candles carrying gc.trend/upper/filter; marketRank present; cmcRefPriceUsd
present), derives the deterministic destination filename from runDate
(gc_crypto_trendradar_daily_YYYYMMDD.json), and decides:

  * IMPORT_OK        -- valid + the date is not already collected -> copy into the dataset
                        folder under the deterministic name (the TOOL does the byte copy;
                        it never overwrites);
  * DUPLICATE_WINDOW -- valid but the date is already collected -> do not import;
  * INVALID          -- structurally invalid -> do not import, name the failures.

Every dangerous capability (Signum/MCP/Hyperliquid, API keys, trading, bot edits, scheduler,
labels, replay) is pinned False with a full scope_locks set; C22 stays
HOLD_FOR_MORE_FROZEN_DATA_WINDOWS.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any

import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_dataset_validation_contract as _dv  # noqa: E501

IMP_SCHEMA_VERSION = 1
IMP_MODE = "RESEARCH_ONLY"
IMP_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _dv.CANDIDATE_ID

INBOX_DIR = "data/external_signum_trend_radar_gc_inbox"
DEST_DIR = _trk.DATA_DIR                                # data/external_signum_trend_radar_gc
EXPORT_GLOB = _trk.EXPORT_GLOB                          # gc_crypto_trendradar_daily*.json
DEST_FILENAME_PREFIX = _trk.EXPORT_PREFIX              # gc_crypto_trendradar_daily
EXPECTED_ROW_COUNT = _dv.EXPECTED_ROW_COUNT            # 50
EXPECTED_DETECTOR = "gc"
EXPECTED_ASSET_CLASS = "crypto"

VERDICT_IMPORT_OK = "C22_GC_IMPORT_OK"
VERDICT_DUPLICATE = "C22_GC_IMPORT_DUPLICATE_WINDOW"
VERDICT_INVALID = "C22_GC_IMPORT_INVALID"
# Data-integrity guard: a structurally-valid export whose decision date is AFTER the local
# machine date must NEVER enter active collection (future-dated / clock-anomalous export).
VERDICT_FUTURE_DATED = "C22_GC_IMPORT_FUTURE_DATED"
# Data-integrity guard: a structurally-valid SAME-DAY export whose shape does not match the
# canonical daily export (e.g. a full/raw dump, or a non-canonical pretty-printed blob) must
# NOT enter active collection even though its date is fine.
VERDICT_ANOMALOUS = "C22_GC_IMPORT_ANOMALOUS_SHAPE"

# --- canonical daily-export shape envelope (for the same-day anomaly guard) ----------------
# The normal daily GC export has exactly these top-level keys, the top-50 result rows, and a
# ~62 KB MINIFIED payload. Anomaly rejection is judged on the NORMALIZED/minified content
# shape -- NOT on pretty-printing. Pretty-printing alone (large raw bytes but normal minified
# content) is a non-blocking WARNING, never a rejection: the 2026-06-20 bootstrap and the
# 2026-06-26 file are both ~113 KB pretty-printed yet byte-for-byte content-equivalent to a
# normal ~62 KB minified window (same keys, 50 rows, identical schema, ~62 KB compact).
EXPECTED_TOP_LEVEL_KEYS = frozenset(("limited", "results", "total"))
MAX_RESULTS = 60                 # normal = 50; a full/raw dump would carry many more rows
MAX_COMPACT_BYTES = 80_000       # minified-content ceiling; normal ~62 KB. Real extra content
                                 # (longer history / foreign fields) inflates the MINIFIED size;
                                 # pure pretty-printing does NOT (it only inflates raw bytes).
PRETTY_PRINT_WARN_RATIO = 1.30   # raw/minified ratio above this -> formatting WARNING only

# --- Signum top-100 -> top-50 canonicalization (vendor upgraded the radar 50 -> 100 rows) --
# Signum/Michael: "users got a nice upgrade ... if you need 50 simply take the first 50 rows
# only." A CLEAN 100-row export (exactly 100/100, canonical top-level keys, every row valid)
# is REDUCIBLE: the importer derives the canonical 50-row window from the FIRST 50 rows
# (preserving vendor order) and imports THAT, instead of fatally rejecting the file. A
# malformed 100-row file (bad rows, extra keys, wrong count) is NOT reducible and still
# rejects/quarantines.
VERDICT_REDUCIBLE = "C22_GC_IMPORT_REDUCIBLE_TOP100_TO_TOP50"
REDUCIBLE_SOURCE_TOTAL = 100
CANONICAL_TOTAL = EXPECTED_ROW_COUNT          # 50
REDUCER_ID = "first_50_vendor_instruction"

C22_STATE = _trk.C22_STATE                              # HOLD_FOR_MORE_FROZEN_DATA_WINDOWS

_CAPABILITY_FLAGS_FALSE = (
    "executes", "performs_network_io", "connects_signum", "uses_mcp",
    "accesses_hyperliquid", "fetches_data", "calls_api", "uses_credentials",
    "uses_api_keys", "mutates_json_contents", "overwrites_destination", "edits_bots",
    "sends_trades", "places_orders", "contains_order_logic", "paper_trading",
    "live_trading", "deploys_capital", "connects_broker", "connects_exchange",
    "creates_claude_routines", "runs_claude_routine", "runs_labels", "runs_replay",
    "builds_replay", "optimizes_parameters", "installs_scheduler", "triggers_scheduler",
    "modifies_scheduler", "modifies_c22_rules", "starts_c23", "reopens_c21",
    "auto_commits", "auto_pushes", "auto_fetches", "auto_promotes", "auto_advances",
    "crosses_into_forbidden_gate",
)


def extract_run_date(parsed: dict) -> str | None:
    """PURE. The single distinct ISO runDate across the export rows, or None if absent or
    inconsistent (mixed-date export)."""
    results = list((parsed or {}).get("results") or [])
    run_dates = {r.get("runDate") for r in results
                 if isinstance(r, dict) and r.get("runDate")}
    if len(run_dates) == 1:
        return next(iter(run_dates))
    return None


def derive_destination_filename(run_date: str | None) -> str | None:
    """PURE. The deterministic destination filename from an ISO runDate:
    YYYY-MM-DD -> gc_crypto_trendradar_daily_YYYYMMDD.json. None if the date is unusable."""
    if not run_date:
        return None
    digits = str(run_date).replace("-", "")
    if len(digits) == 8 and digits.isdigit():
        return "%s_%s.json" % (DEST_FILENAME_PREFIX, digits)
    return None


def is_future_dated(run_date: Any, today_iso: Any) -> bool:
    """PURE. True iff the export decision date (run_date, ISO YYYY-MM-DD) is strictly AFTER
    the supplied local date (today_iso, ISO YYYY-MM-DD). No clock read, no I/O -- the caller
    supplies today. Returns False if either date is missing/unparseable (structural validity
    handles malformed dates; the runner always supplies a real today)."""
    if not run_date or not today_iso:
        return False
    try:
        rd = _dt.date.fromisoformat(str(run_date)[:10])
        td = _dt.date.fromisoformat(str(today_iso)[:10])
    except ValueError:
        return False
    return rd > td


def check_shape_anomaly(parsed: dict, raw_bytes: Any = None,
                        compact_bytes: Any = None) -> dict[str, Any]:
    """PURE. Reject only TRUE content-shape anomalies -- a full/raw dump or a foreign schema --
    judged on the NORMALIZED/minified content, NOT on pretty-printing. Hard reject reasons:
    unexpected top-level keys, an out-of-band result count, or a minified payload above the
    content ceiling (real extra content). Pure whitespace/pretty-printing (large raw bytes but
    a normal minified payload + normal shape) is reported as a non-blocking WARNING, never a
    rejection. Returns {"anomalous": bool, "reasons": [...], "warnings": [...]}. No I/O."""
    reasons: list = []
    warnings: list = []
    p = parsed or {}
    extra_keys = set(p.keys()) - EXPECTED_TOP_LEVEL_KEYS
    if extra_keys:
        reasons.append("unexpected_top_level_keys:%s" % ",".join(sorted(extra_keys)))
    results = p.get("results")
    n = len(results) if isinstance(results, list) else 0
    total = p.get("total")
    if n > MAX_RESULTS:
        reasons.append("too_many_results:%d_gt_%d" % (n, MAX_RESULTS))
    if isinstance(total, int) and total > MAX_RESULTS:
        reasons.append("total_exceeds_max:%d_gt_%d" % (total, MAX_RESULTS))
    # real extra content shows up in the MINIFIED size; pretty-printing does NOT
    if isinstance(compact_bytes, int) and compact_bytes > MAX_COMPACT_BYTES:
        reasons.append("minified_content_exceeds_ceiling:%d_gt_%d"
                       % (compact_bytes, MAX_COMPACT_BYTES))
    # whitespace/pretty-printing -> WARNING only (content is fine, still imports)
    if isinstance(raw_bytes, int) and raw_bytes > 0 and \
            isinstance(compact_bytes, int) and compact_bytes > 0:
        ratio = raw_bytes / compact_bytes
        if ratio > PRETTY_PRINT_WARN_RATIO:
            warnings.append("pretty_printed_non_canonical_whitespace:ratio_%.2f_gt_%.2f"
                            % (ratio, PRETTY_PRINT_WARN_RATIO))
    return {"anomalous": bool(reasons), "reasons": reasons, "warnings": warnings}


def is_reducible_top100(parsed: dict) -> bool:
    """PURE. True iff this is a CLEAN Signum top-100 export that can be canonicalized to the
    top-50 window: exactly the canonical top-level keys, total == 100, and exactly 100 result
    rows. Row-level validity is checked separately by validate_import_candidate (over all
    rows), so a malformed 100-row file fails that and is rejected -- never reduced. No I/O."""
    p = parsed or {}
    if set(p.keys()) != EXPECTED_TOP_LEVEL_KEYS:
        return False
    results = p.get("results")
    if not isinstance(results, list):
        return False
    return p.get("total") == REDUCIBLE_SOURCE_TOTAL and len(results) == REDUCIBLE_SOURCE_TOTAL


def derive_canonical_top50(parsed: dict) -> dict[str, Any]:
    """PURE. Derive the canonical 50-row window from a reducible top-100 export: the FIRST 50
    rows (preserving vendor order), total = 50, and the SAME top-level shape as the legacy
    50-row files ({limited, results, total}) with NO extra metadata. Returns a NEW dict;
    never mutates the input. Deterministic."""
    p = parsed or {}
    rows = list(p.get("results") or [])[:CANONICAL_TOTAL]
    return {"limited": bool(p.get("limited", False)),
            "results": rows,
            "total": CANONICAL_TOTAL}


def validate_import_candidate(parsed: dict) -> dict[str, Any]:
    """PURE. Structural validity of one parsed export. Reuses the committed dataset-facts
    extractor and adds the import-specific checks (total/length >= 50, assetClass=crypto,
    single runDate). No I/O."""
    facts = _dv.extract_dataset_facts(parsed)
    results = list((parsed or {}).get("results") or [])
    total = (parsed or {}).get("total")
    n = len(results)
    run_date = extract_run_date(parsed)
    all_crypto = (n > 0 and all(
        isinstance(r, dict) and r.get("assetClass") == EXPECTED_ASSET_CLASS
        for r in results))

    checks = {
        "has_50_rows": (isinstance(total, int) and total >= EXPECTED_ROW_COUNT)
        or n >= EXPECTED_ROW_COUNT,
        "all_detector_gc": facts.get("all_detector_gc") is True,
        "all_asset_class_crypto": all_crypto,
        "run_date_present": run_date is not None,
        "indicators_data_present": facts.get("rows_missing_indicators_data") == 0,
        "latest_and_previous_candles_present":
            facts.get("latest_and_previous_candles_present") is True,
        "gc_trend_upper_filter_present":
            facts.get("gc_trend_upper_filter_present") is True,
        "market_rank_present": facts.get("rows_missing_market_rank") == 0 and n > 0,
        "cmc_ref_price_usd_present": facts.get("cmc_ref_price_usd_present") is True,
    }
    failures = [k for k, v in checks.items() if not v]
    return {"valid": not failures, "checks": checks, "failures": failures,
            "run_date": run_date, "n_rows": n, "total": total}


def build_import_decision(parsed: dict, already_collected_dates: Any,
                          action: str = "copy",
                          today: Any = None,
                          raw_bytes: Any = None,
                          compact_bytes: Any = None) -> dict[str, Any]:
    """Assemble the PURE import decision for one parsed export. Decides IMPORT_OK /
    FUTURE_DATED / ANOMALOUS_SHAPE / DUPLICATE_WINDOW / INVALID; the importer TOOL performs
    the actual byte copy (never overwriting). No I/O; never mutates the JSON. When ``today``
    (ISO local date) is supplied a future-dated export is rejected as FUTURE_DATED. When
    ``raw_bytes`` (and optionally the minified ``compact_bytes``) are supplied a same-day but
    non-canonical export (full/raw dump or pretty-printed blob) is rejected as ANOMALOUS_SHAPE.
    Both guards keep clock-/shape-anomalous exports out of active collection."""
    collected = {d for d in (already_collected_dates or set())}
    validity = validate_import_candidate(parsed)
    run_date = validity["run_date"]
    dest_filename = derive_destination_filename(run_date)
    future_dated = today is not None and is_future_dated(run_date, today)
    anomaly = check_shape_anomaly(parsed, raw_bytes, compact_bytes)
    reducible = validity["valid"] and is_reducible_top100(parsed)

    if not validity["valid"] or not dest_filename:
        verdict = VERDICT_INVALID
        reasons = list(validity["failures"]) or ["underivable_destination_filename"]
        should_import = False
    elif future_dated:
        verdict = VERDICT_FUTURE_DATED
        reasons = ["future_dated_run_date:%s_after_local_date:%s" % (run_date, today)]
        should_import = False
    elif reducible:
        # clean 100-row Signum export -> derive + import the canonical top-50 (NOT fatal)
        verdict = VERDICT_REDUCIBLE
        reasons = ["reducible_top100_to_top50:%s" % REDUCER_ID]
        should_import = False          # the RAW 100-row file is never imported as-is
    elif anomaly["anomalous"]:
        verdict = VERDICT_ANOMALOUS
        reasons = list(anomaly["reasons"])
        should_import = False
    elif run_date in collected:
        verdict = VERDICT_DUPLICATE
        reasons = ["duplicate_window_for_date:%s" % run_date]
        should_import = False
    else:
        verdict = VERDICT_IMPORT_OK
        reasons = []
        should_import = True

    record: dict[str, Any] = {
        "schema_version": IMP_SCHEMA_VERSION, "mode": IMP_MODE, "lane": IMP_LANE,
        "candidate_id": CANDIDATE_ID,
        "is_local_importer_only": True, "read_only_source": True,
        "label": (
            "Candidate #22 Signum GC local export importer decision (LOCAL-ONLY, RESEARCH "
            "ONLY). Validates a locally-saved export, derives the destination filename from "
            "runDate, and decides IMPORT_OK / DUPLICATE_WINDOW / INVALID without mutating "
            "the JSON, connecting to Signum/MCP, or overwriting."),
        "inbox_dir": INBOX_DIR, "dest_dir": DEST_DIR,
        "action": "copy" if action != "move" else "move",
        # validity + derivation
        "validity": validity,
        "structurally_valid": validity["valid"],
        "run_date": run_date,
        "today": today,
        "is_future_dated": future_dated,
        "raw_bytes": raw_bytes,
        "compact_bytes": compact_bytes,
        "is_anomalous_shape": anomaly["anomalous"],
        "anomaly_reasons": list(anomaly["reasons"]),
        "shape_warnings": list(anomaly["warnings"]),
        "is_reducible_top100": reducible,
        "reducible_source_total": (validity["total"] if reducible else None),
        "should_reduce_and_import": reducible,
        "reducer": REDUCER_ID if reducible else None,
        "destination_filename": dest_filename,
        "already_collected_dates": sorted(collected),
        # decision
        "verdict": verdict,
        "should_import": should_import,
        "reasons": reasons,
        "never_overwrites": True,
        "never_mutates_json": True,
        # current state
        "c22_state": C22_STATE,
        "replay_locked": True,
        "advances_nothing": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_network_io": True, "no_signum_connection": True,
        "no_mcp": True, "no_hyperliquid": True, "no_data_fetch": True,
        "no_api_keys": True, "no_credentials": True, "no_mutate_json": True,
        "no_overwrite_destination": True, "no_bot_edits": True, "no_trades": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_broker": True, "no_claude_routine": True, "no_run_labels": True,
        "no_replay": True, "no_optimization": True, "no_install_scheduler": True,
        "no_trigger_scheduler": True, "no_modify_c22_rules": True, "no_start_c23": True,
        "no_reopen_c21": True, "no_auto_commit": True, "no_auto_push": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_import_decision(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, local-importer-only; the
    verdict is from the closed set and consistent with the validity + duplicate facts
    (IMPORT_OK requires structurally valid + a derived filename + a non-duplicate date;
    DUPLICATE requires valid + an already-collected date; INVALID otherwise);
    should_import is True only for IMPORT_OK; the JSON is never mutated and the destination
    is never overwritten; C22 stays HOLD; and every capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != IMP_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_local_importer_only") is not True:
        failures.append("not_local_importer_only")
    if r.get("verdict") not in (VERDICT_IMPORT_OK, VERDICT_FUTURE_DATED, VERDICT_ANOMALOUS,
                                VERDICT_REDUCIBLE, VERDICT_DUPLICATE, VERDICT_INVALID):
        failures.append("bad_verdict")

    valid = r.get("structurally_valid") is True
    dest = r.get("destination_filename")
    collected = set(r.get("already_collected_dates") or [])
    run_date = r.get("run_date")
    v = r.get("verdict")

    if v == VERDICT_IMPORT_OK:
        if not (valid and dest and run_date not in collected):
            failures.append("import_ok_without_valid_nonduplicate")
        if r.get("should_import") is not True:
            failures.append("import_ok_must_import")
        if r.get("is_future_dated") is True:
            failures.append("import_ok_but_future_dated")
        if r.get("is_anomalous_shape") is True:
            failures.append("import_ok_but_anomalous_shape")
        if r.get("is_reducible_top100") is True:
            failures.append("import_ok_but_reducible_top100")
    elif v == VERDICT_REDUCIBLE:
        if not (valid and dest):
            failures.append("reducible_requires_valid_export")
        if r.get("is_reducible_top100") is not True:
            failures.append("reducible_flag_not_set")
        if r.get("should_import") is not False:
            failures.append("reducible_raw_must_not_import_as_is")
        if r.get("should_reduce_and_import") is not True:
            failures.append("reducible_must_reduce_and_import")
    elif v == VERDICT_FUTURE_DATED:
        if not (valid and dest):
            failures.append("future_dated_requires_valid_export")
        if r.get("is_future_dated") is not True:
            failures.append("future_dated_flag_not_set")
        if r.get("should_import") is not False:
            failures.append("future_dated_must_not_import")
    elif v == VERDICT_ANOMALOUS:
        if not (valid and dest):
            failures.append("anomalous_requires_valid_export")
        if r.get("is_anomalous_shape") is not True:
            failures.append("anomalous_flag_not_set")
        if r.get("should_import") is not False:
            failures.append("anomalous_must_not_import")
    elif v == VERDICT_DUPLICATE:
        if not (valid and run_date in collected):
            failures.append("duplicate_requires_valid_collected_date")
        if r.get("should_import") is not False:
            failures.append("duplicate_must_not_import")
    else:  # INVALID
        if valid and dest:
            failures.append("invalid_but_structurally_valid")
        if r.get("should_import") is not False:
            failures.append("invalid_must_not_import")

    # destination filename derivation matches runDate
    if dest is not None and dest != derive_destination_filename(run_date):
        failures.append("destination_filename_inconsistent")

    # no mutation / no overwrite invariants
    if r.get("never_mutates_json") is not True:
        failures.append("must_not_mutate_json")
    if r.get("never_overwrites") is not True:
        failures.append("must_not_overwrite")
    if r.get("mutates_json_contents") is not False:
        failures.append("mutates_json_flag_true")
    if r.get("overwrites_destination") is not False:
        failures.append("overwrites_flag_true")

    # state
    if r.get("c22_state") != C22_STATE:
        failures.append("c22_state_wrong")
    if r.get("replay_locked") is not True:
        failures.append("replay_not_locked")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_network_io", "no_signum_connection", "no_mcp",
                "no_hyperliquid", "no_data_fetch", "no_api_keys", "no_mutate_json",
                "no_overwrite_destination", "no_bot_edits", "no_trades", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_claude_routine",
                "no_run_labels", "no_replay", "no_install_scheduler",
                "no_trigger_scheduler", "no_modify_c22_rules", "no_start_c23",
                "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

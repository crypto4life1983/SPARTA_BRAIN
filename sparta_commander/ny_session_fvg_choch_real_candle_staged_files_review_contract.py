"""SPARTA NY-Session FVG+CHOCH REAL-CANDLE STAGED FILES REVIEW (READ-ONLY).

The human-review contract over the one approved staging run: it READS the
staged CSVs and manifest under data/ny_fvg_choch/staged/, re-hashes every
file, re-validates schema/timestamps/OHLCV/provenance row by row, checks the
declared train/OOS split, and certifies whether the staged set is fit for a
LATER, separately approved detector run. It modifies nothing, deletes
nothing, fetches nothing, and runs no detector/replay/scorer/optimizer.
"""

from __future__ import annotations

import datetime as _dt
import hashlib as _hashlib
import pathlib as _pathlib
from typing import Any

from sparta_commander.ny_session_fvg_choch_real_candle_staging_plan import (
    REQUIRED_CANDLE_FIELDS,
    REQUIRED_SYMBOLS,
    REQUIRED_TIMEFRAMES,
    validate_date_range_plan,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)

SR_SCHEMA_VERSION = (
    "ny_session_fvg_choch_real_candle_staged_files_review.v1")
SR_LABEL = ("SPARTA NY-Session FVG+CHOCH Real-Candle Staged Files Review "
            "(READ-ONLY, REVIEW ONLY, MODIFIES NOTHING)")
SR_MODE = "RESEARCH_ONLY"
VERDICT_SR_ACCEPTED = "REAL_CANDLE_STAGED_FILES_ACCEPTED_FOR_DETECTOR_RUN"
VERDICT_SR_REJECTED = "REAL_CANDLE_STAGED_FILES_REJECTED"
VERDICT_SR_BLOCKED = "REAL_CANDLE_STAGED_FILES_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_DETECTOR_RUN_ON_STAGED_CANDLES"

STAGING_ROOT = "data/ny_fvg_choch/staged"
MANIFEST_NAME = "manifest.txt"
EXPECTED_FILE_COUNT = 12
EXPECTED_1M_ROWS = 571
EXPECTED_15M_ROWS = 960
EXPECTED_TOTAL_ROWS = 9186
EXPECTED_PROVENANCE_SOURCE = "binance_public_spot_klines_no_auth"
DECLARED_TRAIN_OOS = {"train_start": "2026-06-01", "train_end": "2026-06-08",
                      "oos_start": "2026-06-09", "oos_end": "2026-06-11",
                      "no_oos_optimization": True}
_SPACING_SECONDS = {"1m": 60, "15m": 900}

REVIEW_CHECKLIST = (
    "staging_dir_and_manifest_present",
    "exactly_12_csv_files",
    "manifest_has_12_well_formed_entries",
    "every_listed_file_exists_and_every_csv_is_listed",
    "sha256_matches_manifest_for_every_file",
    "row_counts_match_manifest_for_every_file",
    "all_6_symbols_and_both_timeframes_covered_once",
    "expected_row_counts_571_960_9186",
    "schema_timestamps_ohlcv_quality_clean",
    "provenance_recorded_on_every_row",
    "no_staged_candle_files_tracked_in_git_index",
    "declared_train_oos_split_valid",
)

FORBIDDEN = (
    "modifying_candle_files", "deleting_candle_files",
    "committing_candle_files",
    "committing_manifest_without_separate_approval",
    "detector_runs", "replay_runs", "scorer_runs", "optimizer_runs",
    "report_artifact_creation", "network_retrieval",
    "broker_exchange_private_api_access", "credentials_or_api_keys",
    "account_wallet_login_access", "trading_endpoints_of_any_kind",
    "paper_live_micro_live_authorization", "gate_unlocks",
)


def get_staged_files_review_label() -> str:
    return SR_LABEL


def _utc(value: str) -> _dt.datetime | None:
    try:
        parsed = _dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        return None
    return parsed


def _inspect_csv(path: _pathlib.Path) -> dict[str, Any]:
    """READ-ONLY single-file inspection: sha256, rows, schema, quality."""
    raw = path.read_bytes()
    info: dict[str, Any] = {
        "sha256_actual": _hashlib.sha256(raw).hexdigest(),
        "row_count_actual": 0, "symbol": None, "timeframe": None,
        "quality_errors": [], "provenance_ok": False,
    }
    lines = raw.decode("utf-8").splitlines()
    if not lines or tuple(lines[0].split(",")) != REQUIRED_CANDLE_FIELDS:
        info["quality_errors"].append("header_schema_invalid")
        return info
    rows = lines[1:]
    info["row_count_actual"] = len(rows)
    previous: _dt.datetime | None = None
    seen: set[str] = set()
    sources_ok = bool(rows)
    symbol = timeframe = None
    for index, line in enumerate(rows):
        where = "row_%d" % index
        parts = line.split(",")
        if len(parts) != len(REQUIRED_CANDLE_FIELDS):
            info["quality_errors"].append(where + ":column_count_invalid")
            continue
        ts_raw, o, h, l, c, v, source, tf, sym = parts
        ts = _utc(ts_raw)
        if ts is None:
            info["quality_errors"].append(where + ":timestamp_not_utc")
            continue
        if ts_raw in seen:
            info["quality_errors"].append(where + ":duplicate_candle")
        seen.add(ts_raw)
        if previous is not None:
            if ts <= previous:
                info["quality_errors"].append(where + ":not_monotonic")
            elif timeframe in _SPACING_SECONDS and (
                    (ts - previous).total_seconds()
                    > _SPACING_SECONDS[timeframe]):
                info["quality_errors"].append(where + ":unflagged_gap")
        previous = ts
        try:
            numbers = [float(x) for x in (o, h, l, c, v)]
        except ValueError:
            info["quality_errors"].append(where + ":non_numeric_ohlcv")
            continue
        if any(n < 0 for n in numbers):
            info["quality_errors"].append(where + ":negative_ohlcv")
        no, nh, nl, nc, _nv = numbers
        if not (nl <= no <= nh and nl <= nc <= nh):
            info["quality_errors"].append(where + ":ohlc_inconsistent")
        if source != EXPECTED_PROVENANCE_SOURCE:
            sources_ok = False
        if symbol is None:
            symbol, timeframe = sym, tf
        elif sym != symbol or tf != timeframe:
            info["quality_errors"].append(where + ":mixed_symbol_or_timeframe")
        if sym not in REQUIRED_SYMBOLS:
            info["quality_errors"].append(where + ":symbol_not_approved")
        if tf not in REQUIRED_TIMEFRAMES:
            info["quality_errors"].append(where + ":timeframe_not_approved")
    info["symbol"], info["timeframe"] = symbol, timeframe
    info["provenance_ok"] = sources_ok
    return info


def observe_staged_files(repo_root: Any,
                         tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY observation of the staged set. tracked_paths is the git
    index listing for the staging folder, supplied by the caller."""
    root = _pathlib.Path(str(repo_root))
    staging = root / STAGING_ROOT
    observation: dict[str, Any] = {
        "staging_dir_exists": staging.is_dir(),
        "manifest_present": False, "manifest_entries": [],
        "manifest_malformed": False, "csv_names": [], "files": {},
        "tracked_staged_paths": [str(p) for p in (tracked_paths or ())],
        "declared_train_oos": dict(DECLARED_TRAIN_OOS),
    }
    if not observation["staging_dir_exists"]:
        return observation
    manifest_path = staging / MANIFEST_NAME
    observation["manifest_present"] = manifest_path.is_file()
    if observation["manifest_present"]:
        for line in manifest_path.read_text(
                encoding="utf-8").strip().splitlines():
            parts = line.split(",")
            if len(parts) != 3 or not parts[0] or len(parts[1]) != 64 \
                    or not parts[2].isdigit():
                observation["manifest_malformed"] = True
                continue
            observation["manifest_entries"].append(
                {"filename": parts[0], "sha256": parts[1],
                 "row_count": int(parts[2])})
    observation["csv_names"] = sorted(
        p.name for p in staging.iterdir() if p.suffix == ".csv")
    for name in observation["csv_names"]:
        observation["files"][name] = _inspect_csv(staging / name)
    return observation


def review_staged_files(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of an observed staged set. Pure."""
    review: dict[str, Any] = {
        "schema_version": SR_SCHEMA_VERSION, "label": SR_LABEL,
        "mode": SR_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "forbidden": list(FORBIDDEN),
        "total_rows": 0,
        "staged_files_remain_untracked_operational_data": True,
        "acceptance_authorizes_detector_run_only_after_separate_human_approval": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "modifies_staged_files": False, "deletes_staged_files": False,
        "runs_detector_now": False, "runs_replay_now": False,
        "scores_now": False, "fetches_data": False, "calls_api": False,
        "uses_network": False, "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False, "authorizes_micro_live": False,
        "authorizes_live_trading": False, "promotes_gate": False,
        "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not isinstance(observation, dict):
        review["verdict"] = VERDICT_SR_BLOCKED
        review["blockers"].append("observation_missing")
        return review
    o = observation
    if not o.get("staging_dir_exists") or not o.get("manifest_present"):
        review["verdict"] = VERDICT_SR_BLOCKED
        review["blockers"].append("staging_dir_or_manifest_missing")
        return review

    r: dict[str, bool] = {}
    files = o.get("files") or {}
    entries = o.get("manifest_entries") or []
    by_name = {e["filename"]: e for e in entries}
    r["staging_dir_and_manifest_present"] = True
    r["exactly_12_csv_files"] = len(o.get("csv_names") or []) == (
        EXPECTED_FILE_COUNT)
    r["manifest_has_12_well_formed_entries"] = (
        len(entries) == EXPECTED_FILE_COUNT
        and not o.get("manifest_malformed")
        and len(by_name) == EXPECTED_FILE_COUNT)
    r["every_listed_file_exists_and_every_csv_is_listed"] = (
        set(by_name) == set(o.get("csv_names") or []))
    r["sha256_matches_manifest_for_every_file"] = bool(by_name) and all(
        name in files and files[name]["sha256_actual"] == entry["sha256"]
        for name, entry in by_name.items())
    r["row_counts_match_manifest_for_every_file"] = bool(by_name) and all(
        name in files and files[name]["row_count_actual"]
        == entry["row_count"] for name, entry in by_name.items())
    pairs = {(info.get("symbol"), info.get("timeframe"))
             for info in files.values()}
    r["all_6_symbols_and_both_timeframes_covered_once"] = (
        len(files) == EXPECTED_FILE_COUNT
        and pairs == {(s, t) for s in REQUIRED_SYMBOLS
                      for t in REQUIRED_TIMEFRAMES})
    total = sum(info["row_count_actual"] for info in files.values())
    review["total_rows"] = total
    r["expected_row_counts_571_960_9186"] = (
        total == EXPECTED_TOTAL_ROWS
        and all(info["row_count_actual"] == (
            EXPECTED_1M_ROWS if info.get("timeframe") == "1m"
            else EXPECTED_15M_ROWS)
            for info in files.values()))
    r["schema_timestamps_ohlcv_quality_clean"] = bool(files) and all(
        not info["quality_errors"] for info in files.values())
    r["provenance_recorded_on_every_row"] = bool(files) and all(
        info["provenance_ok"] for info in files.values())
    r["no_staged_candle_files_tracked_in_git_index"] = not o.get(
        "tracked_staged_paths")
    declared = o.get("declared_train_oos")
    r["declared_train_oos_split_valid"] = (
        declared == DECLARED_TRAIN_OOS
        and validate_date_range_plan(declared).get("acceptable") is True)
    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_SR_REJECTED
        review["blockers"].extend("check_failed:" + n for n in failed)
    else:
        review["verdict"] = VERDICT_SR_ACCEPTED
    return review


def build_staged_files_review(repo_root: Any,
                              tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the staged set read-only and certify it."""
    return review_staged_files(observe_staged_files(repo_root, tracked_paths))


def validate_staged_files_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    if v.get("verdict") not in (VERDICT_SR_ACCEPTED, VERDICT_SR_REJECTED,
                                VERDICT_SR_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_SR_ACCEPTED:
        if v.get("blockers"):
            errors.append("accepted_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("accepted_without_full_passing_checklist")
    if v.get("verdict") in (VERDICT_SR_REJECTED, VERDICT_SR_BLOCKED) \
            and not v.get("blockers"):
        errors.append("non_accepted_without_blockers")
    for key, want in (
        ("staged_files_remain_untracked_operational_data", True),
        ("acceptance_authorizes_detector_run_only_after_separate_human_approval",
         True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if v.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports",
                "modifies_staged_files", "deletes_staged_files",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if v.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}

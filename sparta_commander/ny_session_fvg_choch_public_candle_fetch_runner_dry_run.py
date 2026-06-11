"""SPARTA NY-Session FVG+CHOCH PUBLIC CANDLE FETCH RUNNER - DRY RUN
(READ-ONLY, RESEARCH ONLY, DISABLED BY DEFAULT, NO NETWORK).

The thin one-pass runner SHELL: given an approved source plan and fixture
raw batches, it normalizes rows (symbol/timeframe aliases, epoch or ISO
timestamps -> UTC Z), passes them through the pushed staging dry run, and
builds a file-creation PLAN. It never writes, never calls the network, and
contains NO transport: the real retrieval step is deliberately not built and
every real-run attempt refuses. The file-creation writer and its human token
are never referenced here.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any

from sparta_commander.ny_session_fvg_choch_public_candle_fetch_plan import (
    VERDICT_FP_READY,
    build_public_candle_fetch_plan,
    validate_fetch_source_plan,
    validate_public_candle_fetch_plan,
)
from sparta_commander.ny_session_fvg_choch_real_candle_file_creation_tool import (
    build_file_creation_plan,
)
from sparta_commander.ny_session_fvg_choch_real_candle_staging_dry_run import (
    run_real_candle_staging_dry_run,
)
from sparta_commander.ny_session_fvg_choch_real_candle_staging_plan import (
    REQUIRED_CANDLE_FIELDS,
    REQUIRED_SYMBOLS,
    REQUIRED_TIMEFRAMES,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)

FR_SCHEMA_VERSION = (
    "ny_session_fvg_choch_public_candle_fetch_runner_dry_run.v1")
FR_LABEL = ("SPARTA NY-Session FVG+CHOCH Public Candle Fetch Runner Dry Run "
            "(READ-ONLY, RESEARCH ONLY, DISABLED BY DEFAULT, NO TRANSPORT)")
FR_MODE = "RESEARCH_ONLY"
RUNNER_ENABLED_BY_DEFAULT = False
REAL_TRANSPORT_BUILT = False
NEXT_REQUIRED_ACTION = "HUMAN_RUN_APPROVAL_FOR_REAL_CANDLE_FILE_CREATION"

FETCH_RUNNER_STATUSES = (
    "FETCH_RUNNER_DRY_RUN_READY_FOR_HUMAN_RUN_APPROVAL",
    "FETCH_RUNNER_BLOCKED_UPSTREAM_NOT_READY",
    "FETCH_RUNNER_REJECTED_SOURCE_PLAN_INVALID",
    "FETCH_RUNNER_REJECTED_REQUEST_INVALID",
    "FETCH_RUNNER_REJECTED_FORBIDDEN_CAPABILITY",
    "FETCH_RUNNER_REFUSED_REAL_RUN_NOT_APPROVED",
)

_RAW_ROW_FIELDS = ("timestamp", "open", "high", "low", "close", "volume")
_FORBIDDEN_KEY_TOKENS = ("order", "api_key", "credential", "wallet",
                         "account", "login", "fetch_url", "live_authorized",
                         "paper_authorized", "secret", "password",
                         "auth_header")


def get_public_candle_fetch_runner_label() -> str:
    return FR_LABEL


def _utc_z(value: Any) -> str | None:
    """Normalize an ISO string or epoch seconds/ms to UTC '...Z'."""
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        seconds = float(value) / 1000.0 if float(value) > 1e12 else float(value)
        try:
            parsed = _dt.datetime.fromtimestamp(seconds, tz=_dt.timezone.utc)
        except (OverflowError, OSError, ValueError):
            return None
        return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        parsed = _dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        return None
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (ValueError, TypeError):
        return None


def normalize_raw_batch(source_plan: Any, batch: Any) -> dict[str, Any]:
    """Normalize ONE raw fixture batch to the staging schema. Pure."""
    errors: list[str] = []
    if not isinstance(batch, dict):
        return {"acceptable": False, "errors": ["batch_not_a_dict"],
                "payload": None}
    symbol_mapping = source_plan.get("symbol_mapping") or {}
    timeframe_mapping = source_plan.get("timeframe_mapping") or {}
    source_symbol = batch.get("source_symbol")
    source_timeframe = batch.get("source_timeframe")
    symbol = symbol_mapping.get(source_symbol)
    timeframe = timeframe_mapping.get(source_timeframe)
    if symbol not in REQUIRED_SYMBOLS:
        errors.append("source_symbol_not_mapped:" + str(source_symbol))
    if timeframe not in REQUIRED_TIMEFRAMES:
        errors.append("source_timeframe_not_mapped:" + str(source_timeframe))
    raw_rows = batch.get("rows")
    if not isinstance(raw_rows, list) or not raw_rows:
        errors.append("raw_rows_missing_or_empty")
    if errors:
        return {"acceptable": False, "errors": errors, "payload": None}
    normalized: list[dict[str, Any]] = []
    for index, raw in enumerate(raw_rows):
        where = "raw_row_%d" % index
        if not isinstance(raw, dict):
            errors.append(where + ":not_a_dict")
            continue
        missing = [f for f in _RAW_ROW_FIELDS if f not in raw]
        if missing:
            errors.append(where + ":missing_fields:" + ",".join(missing))
            continue
        ts = _utc_z(raw["timestamp"])
        if ts is None:
            errors.append(where + ":timestamp_not_normalizable")
            continue
        row: dict[str, Any] = {"timestamp": ts}
        for name in ("open", "high", "low", "close", "volume"):
            number = _number(raw[name])
            if number is None:
                errors.append(where + ":non_numeric:" + name)
                break
            row[name] = number
        else:
            row["source"] = str(source_plan.get("source_name"))
            row["timeframe"] = timeframe
            row["symbol"] = symbol
            assert tuple(row) == REQUIRED_CANDLE_FIELDS
            normalized.append(row)
    if errors:
        return {"acceptable": False, "errors": errors, "payload": None}
    payload: dict[str, Any] = {"symbol": symbol, "timeframe": timeframe,
                               "rows": normalized}
    if batch.get("flagged_gaps"):
        payload["flagged_gaps"] = batch["flagged_gaps"]
    return {"acceptable": True, "errors": [], "payload": payload}


def _base_record() -> dict[str, Any]:
    return {
        "schema_version": FR_SCHEMA_VERSION, "label": FR_LABEL,
        "mode": FR_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID,
        "runner_enabled_by_default": RUNNER_ENABLED_BY_DEFAULT,
        "real_transport_built": REAL_TRANSPORT_BUILT,
        "runner_status": None, "errors": [],
        "batches_normalized": 0, "rows_normalized": 0,
        "file_creation_plan_status": None, "planned_files": [],
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
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


def _reject(record: dict[str, Any], status: str,
            errors: list[str]) -> dict[str, Any]:
    record["runner_status"] = status
    record["errors"] = errors
    return record


def run_public_candle_fetch_runner_dry_run(source_plan: Any,
                                           raw_batches: Any) -> dict[str, Any]:
    """ONE deterministic dry run on FIXTURE batches. Pure; no network, no
    files. Real retrieval refuses via attempt_real_fetch_run."""
    record = _base_record()
    plan = build_public_candle_fetch_plan()
    if (plan.get("verdict") != VERDICT_FP_READY
            or not validate_public_candle_fetch_plan(plan).get("valid")):
        return _reject(record, "FETCH_RUNNER_BLOCKED_UPSTREAM_NOT_READY",
                       ["public_candle_fetch_plan_not_ready"])
    source_check = validate_fetch_source_plan(source_plan)
    if not source_check.get("approvable"):
        return _reject(record, "FETCH_RUNNER_REJECTED_SOURCE_PLAN_INVALID",
                       list(source_check.get("errors")
                            or ["source_plan_invalid"]))
    if not isinstance(raw_batches, list) or not raw_batches:
        return _reject(record, "FETCH_RUNNER_REJECTED_REQUEST_INVALID",
                       ["raw_batches_missing_or_empty"])
    for batch in raw_batches:
        if not isinstance(batch, dict):
            return _reject(record, "FETCH_RUNNER_REJECTED_REQUEST_INVALID",
                           ["batch_not_a_dict"])
        for key in batch:
            lowered = str(key).lower()
            for token in _FORBIDDEN_KEY_TOKENS:
                if token in lowered:
                    return _reject(
                        record, "FETCH_RUNNER_REJECTED_FORBIDDEN_CAPABILITY",
                        ["forbidden_batch_field:" + str(key)])
    payloads: list[dict[str, Any]] = []
    rows_total = 0
    for index, batch in enumerate(raw_batches):
        normalized = normalize_raw_batch(source_plan, batch)
        if not normalized["acceptable"]:
            return _reject(record, "FETCH_RUNNER_REJECTED_REQUEST_INVALID",
                           ["batch_%d" % index + ":" + e
                            for e in normalized["errors"]])
        payloads.append(normalized["payload"])
        rows_total += len(normalized["payload"]["rows"])
    proposal = {
        "source_name": source_plan["source_name"],
        "category": source_plan["category"],
        "provenance": source_plan["provenance"],
        "terms_and_limits": source_plan["terms_and_limits"],
        "historical_only": True,
        "requires_login": False, "requires_api_key": False,
        "requires_credentials": False, "uses_private_endpoint": False,
        "is_live_polling": False,
        "symbols": REQUIRED_SYMBOLS, "timeframes": REQUIRED_TIMEFRAMES,
        "output_fields": REQUIRED_CANDLE_FIELDS,
    }
    for payload in payloads:
        staged = run_real_candle_staging_dry_run(proposal, payload)
        if staged["staging_status"] != (
                "STAGING_DRY_RUN_READY_FOR_HUMAN_FILE_APPROVAL"):
            return _reject(record, "FETCH_RUNNER_REJECTED_REQUEST_INVALID",
                           ["staging_dry_run:" + staged["staging_status"]]
                           + staged["errors"])
    fc_plan = build_file_creation_plan(proposal, payloads)
    record["file_creation_plan_status"] = fc_plan["plan_status"]
    if fc_plan["plan_status"] != (
            "FILE_CREATION_PLAN_READY_FOR_HUMAN_RUN_APPROVAL"):
        return _reject(record, "FETCH_RUNNER_REJECTED_REQUEST_INVALID",
                       ["file_creation_plan:" + fc_plan["plan_status"]]
                       + fc_plan["errors"])
    record["planned_files"] = [
        {"target_path": entry["target_path"], "symbol": entry["symbol"],
         "timeframe": entry["timeframe"], "row_count": entry["row_count"],
         "sha256": entry["sha256"]}
        for entry in fc_plan["planned_files"]]
    record["batches_normalized"] = len(payloads)
    record["rows_normalized"] = rows_total
    record["runner_status"] = (
        "FETCH_RUNNER_DRY_RUN_READY_FOR_HUMAN_RUN_APPROVAL")
    assert record["runner_status"] in FETCH_RUNNER_STATUSES
    return record


def attempt_real_fetch_run(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    """Real retrieval ALWAYS refuses: no transport is built, and any future
    transport is its own separately approved block."""
    record = _base_record()
    return _reject(
        record, "FETCH_RUNNER_REFUSED_REAL_RUN_NOT_APPROVED",
        ["real_transport_not_built_requires_future_human_approved_block"])


def validate_fetch_runner_record(record: Any) -> dict[str, Any]:
    """Validate a runner record's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("runner_status") not in FETCH_RUNNER_STATUSES:
        errors.append("bad_runner_status")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("runner_enabled_by_default") is not False:
        errors.append("runner_must_be_disabled_by_default")
    if r.get("real_transport_built") is not False:
        errors.append("real_transport_must_not_exist")
    if (r.get("runner_status")
            == "FETCH_RUNNER_DRY_RUN_READY_FOR_HUMAN_RUN_APPROVAL"
            and r.get("errors")):
        errors.append("ready_with_errors")
    for key, want in (
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}

"""SPARTA NY-Session FVG+CHOCH REAL-CANDLE STAGING DRY RUN (READ-ONLY).

Proves SPARTA can accept an approved no-auth public historical candle source
and validate 1m/15m candle payloads for the six approved symbols -- entirely
in memory. Fetches nothing, writes nothing, creates no directories. The
output is a staging READINESS result, never files; actual file creation
remains behind its own separate human approval.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any

from sparta_commander.ny_session_fvg_choch_candle_source_approval_contract import (
    VERDICT_SA_READY,
    build_candle_source_approval_contract,
    validate_candle_source_approval_contract,
    validate_candle_source_proposal,
)
from sparta_commander.ny_session_fvg_choch_real_candle_staging_plan import (
    REQUIRED_CANDLE_FIELDS,
    REQUIRED_SYMBOLS,
    REQUIRED_TIMEFRAMES,
    VERDICT_SP_READY,
    build_real_candle_staging_plan,
    validate_real_candle_staging_plan,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)

SD_SCHEMA_VERSION = "ny_session_fvg_choch_real_candle_staging_dry_run.v1"
SD_LABEL = ("SPARTA NY-Session FVG+CHOCH Real-Candle Staging Dry Run "
            "(READ-ONLY, RESEARCH ONLY, WRITES NOTHING)")
SD_MODE = "RESEARCH_ONLY"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_REAL_CANDLE_FILE_CREATION"

APPROVED_SOURCE_CATEGORY_FOR_DRY_RUN = (
    "no_auth_public_historical_endpoint_human_approved")

STAGING_DRY_RUN_STATUSES = (
    "STAGING_DRY_RUN_READY_FOR_HUMAN_FILE_APPROVAL",
    "STAGING_DRY_RUN_BLOCKED_UPSTREAM_NOT_READY",
    "STAGING_DRY_RUN_REJECTED_SOURCE_NOT_APPROVED",
    "STAGING_DRY_RUN_REJECTED_FORBIDDEN_CAPABILITY",
    "STAGING_DRY_RUN_REJECTED_PAYLOAD_INVALID",
)

_TIMEFRAME_SECONDS = {"1m": 60, "15m": 900}
_FORBIDDEN_KEY_TOKENS = ("order", "api_key", "credential", "wallet",
                         "account", "login", "fetch_url", "live_authorized",
                         "paper_authorized", "secret", "password")


def get_real_candle_staging_dry_run_label() -> str:
    return SD_LABEL


def _utc(value: Any) -> _dt.datetime | None:
    try:
        parsed = _dt.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    if parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        return None
    return parsed


def _base(payload: Any) -> dict[str, Any]:
    record: dict[str, Any] = {
        "schema_version": SD_SCHEMA_VERSION, "label": SD_LABEL,
        "mode": SD_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID,
        "source_category": APPROVED_SOURCE_CATEGORY_FOR_DRY_RUN,
        "staging_status": None, "errors": [],
        "symbol": None, "timeframe": None,
        "rows_validated": 0, "gaps_flagged_count": 0,
        "produces_files": False, "produces_readiness_result_only": True,
        "actual_file_creation_requires_separate_human_approval": True,
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
    if isinstance(payload, dict):
        record["symbol"] = payload.get("symbol")
        record["timeframe"] = payload.get("timeframe")
    return record


def _reject(record: dict[str, Any], status: str,
            errors: list[str]) -> dict[str, Any]:
    record["staging_status"] = status
    record["errors"] = errors
    return record


def run_real_candle_staging_dry_run(source_proposal: Any,
                                    payload: Any) -> dict[str, Any]:
    """ONE deterministic in-memory staging dry run. Pure; writes nothing."""
    record = _base(payload)

    plan = build_real_candle_staging_plan()
    approval = build_candle_source_approval_contract()
    if (not validate_real_candle_staging_plan(plan).get("valid")
            or plan.get("verdict") != VERDICT_SP_READY
            or not validate_candle_source_approval_contract(approval).get("valid")
            or approval.get("verdict") != VERDICT_SA_READY):
        return _reject(record, "STAGING_DRY_RUN_BLOCKED_UPSTREAM_NOT_READY",
                       ["upstream_plan_or_source_approval_not_ready"])

    proposal_check = validate_candle_source_proposal(source_proposal)
    if not proposal_check.get("approvable"):
        return _reject(record, "STAGING_DRY_RUN_REJECTED_SOURCE_NOT_APPROVED",
                       list(proposal_check.get("errors") or
                            ["source_proposal_invalid"]))
    if source_proposal.get("category") != APPROVED_SOURCE_CATEGORY_FOR_DRY_RUN:
        return _reject(record, "STAGING_DRY_RUN_REJECTED_SOURCE_NOT_APPROVED",
                       ["category_not_approved_for_this_dry_run:"
                        + str(source_proposal.get("category"))])

    if not isinstance(payload, dict):
        return _reject(record, "STAGING_DRY_RUN_REJECTED_PAYLOAD_INVALID",
                       ["payload_not_a_dict"])
    for key in payload:
        lowered = str(key).lower()
        for token in _FORBIDDEN_KEY_TOKENS:
            if token in lowered:
                return _reject(record,
                               "STAGING_DRY_RUN_REJECTED_FORBIDDEN_CAPABILITY",
                               ["forbidden_payload_field:" + str(key)])

    errors: list[str] = []
    symbol = payload.get("symbol")
    timeframe = payload.get("timeframe")
    if symbol not in REQUIRED_SYMBOLS:
        errors.append("symbol_not_in_approved_set:" + str(symbol))
    if timeframe not in REQUIRED_TIMEFRAMES:
        errors.append("timeframe_not_supported:" + str(timeframe))
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        errors.append("rows_missing_or_empty")
    if errors:
        return _reject(record, "STAGING_DRY_RUN_REJECTED_PAYLOAD_INVALID",
                       errors)

    flagged = payload.get("flagged_gaps") or []
    flagged_pairs = {(str(g.get("from_timestamp")), str(g.get("to_timestamp")))
                     for g in flagged if isinstance(g, dict)}
    spacing = _TIMEFRAME_SECONDS[timeframe]
    seen: set[str] = set()
    previous: _dt.datetime | None = None
    previous_raw: str | None = None
    for index, row in enumerate(rows):
        where = "row_%d" % index
        if not isinstance(row, dict):
            errors.append(where + ":not_a_dict")
            continue
        missing = [f for f in REQUIRED_CANDLE_FIELDS if f not in row]
        if missing:
            errors.append(where + ":missing_fields:" + ",".join(missing))
            continue
        ts = _utc(row["timestamp"])
        if ts is None:
            errors.append(where + ":timestamp_not_utc_normalized")
            continue
        raw_ts = str(row["timestamp"])
        if raw_ts in seen:
            errors.append(where + ":duplicate_candle:" + raw_ts)
        seen.add(raw_ts)
        if previous is not None:
            if ts <= previous:
                errors.append(where + ":timestamps_not_monotonic")
            else:
                delta = (ts - previous).total_seconds()
                if delta > spacing and (previous_raw, raw_ts) not in flagged_pairs:
                    errors.append(where + ":unflagged_gap_after:"
                                  + str(previous_raw))
        previous, previous_raw = ts, raw_ts
        bad_value = False
        for name in ("open", "high", "low", "close", "volume"):
            value = row[name]
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(where + ":non_numeric:" + name)
                bad_value = True
            elif value < 0:
                errors.append(where + ":negative_value:" + name)
                bad_value = True
        if not bad_value:
            if not (row["low"] <= row["open"] <= row["high"]
                    and row["low"] <= row["close"] <= row["high"]
                    and row["low"] <= row["high"]):
                errors.append(where + ":ohlc_inconsistent")
        if not str(row["source"] or "").strip():
            errors.append(where + ":source_missing")
        if row["timeframe"] != timeframe:
            errors.append(where + ":timeframe_mismatch_with_declared")
        if row["symbol"] != symbol:
            errors.append(where + ":symbol_mismatch_with_declared")

    if errors:
        return _reject(record, "STAGING_DRY_RUN_REJECTED_PAYLOAD_INVALID",
                       errors)
    record["staging_status"] = "STAGING_DRY_RUN_READY_FOR_HUMAN_FILE_APPROVAL"
    record["rows_validated"] = len(rows)
    record["gaps_flagged_count"] = len(flagged_pairs)
    assert record["staging_status"] in STAGING_DRY_RUN_STATUSES
    return record


def validate_staging_dry_run_record(record: Any) -> dict[str, Any]:
    """Validate a dry-run record's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("staging_status") not in STAGING_DRY_RUN_STATUSES:
        errors.append("bad_staging_status")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("source_category") != APPROVED_SOURCE_CATEGORY_FOR_DRY_RUN:
        errors.append("source_category_tampered")
    if (r.get("staging_status")
            == "STAGING_DRY_RUN_READY_FOR_HUMAN_FILE_APPROVAL"
            and r.get("errors")):
        errors.append("ready_with_errors")
    for key, want in (
        ("produces_files", False),
        ("produces_readiness_result_only", True),
        ("actual_file_creation_requires_separate_human_approval", True),
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

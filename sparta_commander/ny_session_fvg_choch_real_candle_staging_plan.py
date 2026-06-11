"""SPARTA NY-Session FVG+CHOCH REAL-CANDLE STAGING PLAN (READ-ONLY, PLAN ONLY).

How approved historical 1m and 15m candles will LATER be staged for the
detector and replay runner -- reproducibly, with train/OOS discipline, and
with zero fetching, zero files, zero network in this block. The source itself
still needs a later human approval; this is the rulebook the staged data must
meet.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any

from sparta_commander.ny_session_fvg_choch_dry_run_replay_results_review_contract import (
    VERDICT_ACCEPTED as DRY_RUN_ACCEPTED,
    build_dry_run_replay_results_review,
    validate_dry_run_replay_results_review,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)

SP_SCHEMA_VERSION = "ny_session_fvg_choch_real_candle_staging_plan.v1"
SP_LABEL = ("SPARTA NY-Session FVG+CHOCH Real-Candle Staging Plan "
            "(READ-ONLY, PLAN ONLY, STAGES NOTHING)")
SP_MODE = "RESEARCH_ONLY"
VERDICT_SP_READY = "NY_FVG_CHOCH_REAL_CANDLE_STAGING_PLAN_READY"
VERDICT_SP_BLOCKED = "NY_FVG_CHOCH_REAL_CANDLE_STAGING_PLAN_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDLE_SOURCE_FOR_STAGING"

REQUIRED_TIMEFRAMES = ("1m", "15m")
REQUIRED_SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD", "AVAXUSD", "ARBUSD",
                    "XRPUSD")
REQUIRED_CANDLE_FIELDS = ("timestamp", "open", "high", "low", "close",
                          "volume", "source", "timeframe", "symbol")

SESSION_COVERAGE = {
    "session_window": "09:30-13:00 America/New_York",
    "pre_window_minutes": 120,   # 15m context + swing references
    "post_window_minutes": 240,  # target/stop/timeout replay room
}

STAGING_PATH_PATTERNS = {
    "1m": "data/ny_fvg_choch/staged/{symbol}_1m_{date_range}.csv",
    "15m": "data/ny_fvg_choch/staged/{symbol}_15m_{date_range}.csv",
}

DATE_RANGE_PLAN_RULES = (
    "a_train_window_and_an_out_of_sample_window_must_both_be_declared",
    "windows_must_not_overlap_and_oos_must_follow_train",
    "no_parameter_tuning_or_selection_may_ever_use_the_oos_window",
    "oos_results_are_looked_at_once_per_frozen_evaluation",
)

DATA_QUALITY_CHECKS = (
    "timestamps_monotonic_increasing",
    "no_duplicate_candles_per_symbol_timeframe",
    "no_missing_required_fields",
    "no_negative_prices_or_volume",
    "1m_and_15m_series_aligned_on_shared_boundaries",
    "timezone_normalized_to_utc_with_ny_session_mapping_recorded",
    "source_recorded_on_every_row",
    "gaps_explicitly_flagged_never_silently_filled",
)

PROVENANCE_RULES = (
    "source_must_be_human_approved_before_any_staging",
    "no_credentials_no_account_data_no_private_exchange_access",
    "no_live_market_polling_ever",
    "no_network_in_this_block",
)

REPLAY_ELIGIBILITY_RULES = (
    "only_accepted_detector_labels_can_enter_replay",
    "rejected_labels_remain_auditable",
    "fee_spread_slippage_assumptions_required_before_replay",
    "locked_scorer_review_remains_a_future_separate_approval",
)

FORBIDDEN = (
    "data_fetch_in_this_block", "network_calls",
    "broker_or_exchange_api_calls", "credential_access",
    "wallet_account_login_fields", "order_placement",
    "paper_live_micro_live_authorization", "optimizer_execution",
    "overnight_loop", "auto_promotion", "gate_unlocks",
    "report_artifact_creation_in_this_block",
)

_FORBIDDEN_TOKENS = ("order", "api_key", "credential", "wallet", "account",
                     "login", "fetch_url", "live_authorized",
                     "paper_authorized")


def get_real_candle_staging_plan_label() -> str:
    return SP_LABEL


def validate_candle_schema(columns: Any) -> dict[str, Any]:
    """Pure: a proposed candle column set must match the required fields."""
    errors: list[str] = []
    if not isinstance(columns, (list, tuple)) or not columns:
        return {"acceptable": False, "errors": ["columns_missing_or_empty"]}
    names = [str(c).strip().lower() for c in columns]
    for name in names:
        for token in _FORBIDDEN_TOKENS:
            if token in name:
                errors.append("forbidden_field:" + name)
    if errors:
        return {"acceptable": False, "errors": errors}
    for field in REQUIRED_CANDLE_FIELDS:
        if field not in names:
            errors.append("missing_required_field:" + field)
    if len(set(names)) != len(names):
        errors.append("duplicate_column_names")
    return {"acceptable": not errors, "errors": errors}


def validate_candle_row(row: Any) -> dict[str, Any]:
    """Pure OHLCV sanity for one candle row dict."""
    errors: list[str] = []
    if not isinstance(row, dict):
        return {"acceptable": False, "errors": ["row_not_a_dict"]}
    try:
        _dt.datetime.fromisoformat(
            str(row.get("timestamp")).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        errors.append("timestamp_not_utc_iso8601")
    for name in ("open", "high", "low", "close", "volume"):
        raw = row.get(name)
        if not isinstance(raw, (int, float)) or isinstance(raw, bool):
            errors.append("non_numeric:" + name)
        elif raw < 0:
            errors.append("negative_value:" + name)
    if not errors:
        if not (row["low"] <= row["open"] <= row["high"]
                and row["low"] <= row["close"] <= row["high"]):
            errors.append("ohlc_relationship_invalid")
    if not row.get("source"):
        errors.append("source_provenance_missing")
    if row.get("timeframe") not in REQUIRED_TIMEFRAMES:
        errors.append("timeframe_outside_required_set")
    if row.get("symbol") not in REQUIRED_SYMBOLS:
        errors.append("symbol_outside_required_set")
    return {"acceptable": not errors, "errors": errors}


def validate_date_range_plan(plan: Any) -> dict[str, Any]:
    """Pure: train/OOS split must be declared, ordered, non-overlapping, and
    OOS optimization must be explicitly forbidden."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return {"acceptable": False, "errors": ["plan_not_a_dict"]}
    for key in ("train_start", "train_end", "oos_start", "oos_end"):
        if not plan.get(key):
            errors.append("missing_window_bound:" + key)
    if not errors and not (str(plan["train_start"]) < str(plan["train_end"])
                           <= str(plan["oos_start"]) < str(plan["oos_end"])):
        errors.append("windows_overlap_or_misordered")
    if plan.get("no_oos_optimization") is not True:
        errors.append("oos_optimization_not_explicitly_forbidden")
    return {"acceptable": not errors, "errors": errors}


def build_real_candle_staging_plan() -> dict[str, Any]:
    """Assemble the staging plan, gated on the ACCEPTED dry-run review."""
    plan: dict[str, Any] = {
        "schema_version": SP_SCHEMA_VERSION, "label": SP_LABEL, "mode": SP_MODE,
        "lane": "crypto_d1_auto_research", "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "required_timeframes": list(REQUIRED_TIMEFRAMES),
        "required_symbols": list(REQUIRED_SYMBOLS),
        "required_candle_fields": list(REQUIRED_CANDLE_FIELDS),
        "session_coverage": dict(SESSION_COVERAGE),
        "staging_path_patterns": dict(STAGING_PATH_PATTERNS),
        "date_range_plan_rules": list(DATE_RANGE_PLAN_RULES),
        "data_quality_checks": list(DATA_QUALITY_CHECKS),
        "provenance_rules": list(PROVENANCE_RULES),
        "replay_eligibility_rules": list(REPLAY_ELIGIBILITY_RULES),
        "forbidden": list(FORBIDDEN),
        "plan_stages_no_files": True,
        "plan_fetches_nothing": True,
        "future_artifacts_require_separate_human_approval": True,
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
    review = build_dry_run_replay_results_review()
    if (not validate_dry_run_replay_results_review(review).get("valid")
            or review.get("verdict") != DRY_RUN_ACCEPTED):
        plan["verdict"] = VERDICT_SP_BLOCKED
        plan["blockers"].append("dry_run_review_not_accepted")
        return plan
    plan["verdict"] = VERDICT_SP_READY
    return plan


def validate_real_candle_staging_plan(plan: Any) -> dict[str, Any]:
    """Validate the plan's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return {"valid": False, "errors": ["plan_not_a_dict"]}
    p = plan
    if p.get("verdict") not in (VERDICT_SP_READY, VERDICT_SP_BLOCKED):
        errors.append("bad_verdict")
    if p.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(p.get("required_timeframes") or ()) != REQUIRED_TIMEFRAMES:
        errors.append("timeframes_tampered")
    if tuple(p.get("required_symbols") or ()) != REQUIRED_SYMBOLS:
        errors.append("symbols_tampered")
    if tuple(p.get("required_candle_fields") or ()) != REQUIRED_CANDLE_FIELDS:
        errors.append("candle_fields_tampered")
    if p.get("session_coverage") != SESSION_COVERAGE:
        errors.append("session_coverage_tampered")
    if tuple(p.get("date_range_plan_rules") or ()) != DATE_RANGE_PLAN_RULES:
        errors.append("date_range_rules_tampered")
    if tuple(p.get("data_quality_checks") or ()) != DATA_QUALITY_CHECKS:
        errors.append("quality_checks_tampered")
    if tuple(p.get("provenance_rules") or ()) != PROVENANCE_RULES:
        errors.append("provenance_rules_tampered")
    if tuple(p.get("replay_eligibility_rules") or ()) != REPLAY_ELIGIBILITY_RULES:
        errors.append("replay_eligibility_tampered")
    if tuple(p.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    for key, want in (
        ("plan_stages_no_files", True), ("plan_fetches_nothing", True),
        ("future_artifacts_require_separate_human_approval", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if p.get(key) is not want:
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
        if p.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}

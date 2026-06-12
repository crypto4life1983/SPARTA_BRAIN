"""SPARTA CANDIDATE #3 MUTABLE EDIT V1 -- PULLBACK DEFINITION (READ-ONLY,
RESEARCH ONLY, ONE AUTHORIZED EDIT): BTC_SOL_LONG_TREND_CONTINUATION_V1.

Authorized by HUMAN_DECISION_ON_CANDIDATE_3_OUTCOME (2026-06-12, option 1).
Changes EXACTLY ONE rule: the pullback bar definition. Everything else is
locked byte-identical to the pushed detector spec and IMPORTED from it.

WHY (frozen evidence, labels review c3d93409): 711 attempts / 0 accepted;
627/711 died at pullback_too_short because strict consecutive lower-LOW
bars almost never print after a fresh 20-bar closing high on crypto 15m.
The family thesis was never tested. This edit is a structural realism fix,
not a rescue of Candidate #2 (untouched) and not curve-fitting toward
accepts: the floor, trend gate, impulse, entry, and stop rules are all
unchanged, so every accepted V1 label still clears the same honesty bars.

OLD pullback bar rule: each bar has a low strictly below the prior bar's
low (consecutive lower-lows only).
NEW pullback bar rule (the ONLY change): each pullback bar has a lower
LOW *or* a lower CLOSE than the prior bar; the window is still 2-8 bars,
must still hold above the prior swing low, and must still retrace at most
61.8 percent of the impulse leg.

PRE-COMMITTED FAILURE RULES (frozen): zero or near-zero accepts after V1
(fewer than 10 accepted labels across both symbols) -> Candidate #3 is
REJECTED_KEPT_ON_RECORD. Accepts but fee-honest 27 bps replay net-negative
in all target variants -> REJECTED_KEPT_ON_RECORD. No second mutable edit
unless a separate human decision contract explicitly authorizes it.

This module defines rules and the V1 scanner. It runs nothing now,
fetches nothing, and authorizes nothing.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.btc_sol_long_trend_continuation_detector_spec_contract import (
    ATR_STOP_MULTIPLIER,
    IMPULSE_FRESHNESS_BARS,
    IMPULSE_LOOKBACK_BARS,
    MAX_RETRACE_PCT,
    PULLBACK_MAX_BARS,
    PULLBACK_MIN_BARS,
    _empty_label,
    compute_atr14,
    evaluate_trend_qualification,
)
from sparta_commander.btc_sol_long_trend_continuation_real_candle_labels_review_contract import (
    VERDICT_TCL_FROZEN,
    build_tc3_labels_review,
)
from sparta_commander.btc_sol_long_trend_continuation_strategy_spec_contract import (
    CANDIDATE_ID,
    SYMBOLS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    MINIMUM_RISK_DISTANCE_BPS,
    evaluate_setup_cost_viability,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)

M1_SCHEMA_VERSION = (
    "btc_sol_long_trend_continuation_mutable_edit_v1_pullback.v1")
M1_LABEL = ("SPARTA Candidate #3 Mutable Edit V1 -- Pullback Definition "
            "(READ-ONLY, RESEARCH ONLY, ONE AUTHORIZED EDIT, "
            "NOT A RESCUE)")
M1_MODE = "RESEARCH_ONLY"
VERDICT_M1_READY = "CANDIDATE_3_MUTABLE_EDIT_V1_READY"
VERDICT_M1_BLOCKED = "CANDIDATE_3_MUTABLE_EDIT_V1_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_APPROVED_CANDIDATE_3_V1_REDETECTION_ON_STAGED_SAMPLE")

EDIT_VERSION = "v1"
ALLOWED_EDITED_FIELDS = ("pullback_bar_definition",)

V1_NEW_PARAMETERS = {
    "pullback_bar_rule_old": ("each bar has a low strictly below the "
                              "prior bar's low (consecutive lower-lows "
                              "only)"),
    "pullback_bar_rule_new": ("each pullback bar has a lower low OR a "
                              "lower close than the prior bar"),
    "consecutive_lower_low_only_requirement_removed": True,
    "pullback_window_bars_min": PULLBACK_MIN_BARS,   # 2, unchanged
    "pullback_window_bars_max": PULLBACK_MAX_BARS,   # 8, unchanged
    "pullback_must_hold_above_prior_swing_low": True,  # unchanged
    "max_retrace_pct_of_impulse_leg": MAX_RETRACE_PCT,  # 61.8, unchanged
}

LOCKED_UNCHANGED = (
    "symbols_btcusd_solusd_only",
    "direction_long_only",
    "trend_qualification_1h_sma20_above_and_rising",
    "trend_uses_completed_1h_bars_only_no_lookahead",
    "impulse_new_20_bar_closing_high_within_8_bars",
    "entry_on_first_15m_close_above_pullback_high",
    "one_setup_per_impulse",
    "stop_wider_of_structural_and_1_5x_atr14_never_tightened",
    "minimum_risk_distance_81_bps_checked_at_label_time",
    "fee_honest_27_bps_round_trip_for_any_future_replay",
    "maker_execution_never_assumed",
    "label_schema_and_closed_statuses_unchanged",
)

NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS = 10

PRE_COMMITTED_FAILURE_RULES_V1 = (
    "if v1 redetection produces zero or near-zero accepted labels "
    "(fewer than 10 across both symbols), candidate #3 is "
    "REJECTED_KEPT_ON_RECORD",
    "if v1 produces accepted labels but the fee-honest 27 bps replay is "
    "net-negative in all target variants, candidate #3 is "
    "REJECTED_KEPT_ON_RECORD",
    "no second mutable edit unless a separate human decision contract "
    "explicitly authorizes it",
)

FORBIDDEN_CHANGES = (
    "changing_symbols_or_adding_symbols",
    "adding_short_setups",
    "weakening_or_changing_the_1h_trend_qualification",
    "weakening_or_changing_the_impulse_requirement",
    "changing_the_resumption_entry_rule",
    "changing_or_tightening_the_stop_rule",
    "lowering_the_81bps_floor",
    "changing_the_27bps_fee_model_or_assuming_maker_execution",
    "changing_the_label_schema_or_statuses",
    "touching_candidate_1_or_candidate_2_records",
    "running_detector_or_replay_without_separate_human_approval",
)


def get_mutable_edit_v1_label() -> str:
    return M1_LABEL


def scan_tc_setups_v1(bars_15m: list, bars_1h: list,
                      symbol: str) -> list[dict[str, Any]]:
    """The V1 scanner: byte-identical to the pushed scanner except the
    pullback-run rule (lower low OR lower close). All other primitives
    are imported from the pushed detector spec. Pure; labels only."""
    if symbol not in SYMBOLS:
        raise ValueError("symbol_outside_candidate_3_scope:" + str(symbol))
    labels: list[dict[str, Any]] = []
    n = len(bars_15m)
    for j in range(IMPULSE_LOOKBACK_BARS, n):
        closes_before = [float(bars_15m[i]["close"])
                         for i in range(j - IMPULSE_LOOKBACK_BARS + 1, j)]
        if float(bars_15m[j]["close"]) <= max(closes_before):
            continue
        label = _empty_label(symbol, j, bars_15m)
        swing_low = min(float(bars_15m[i]["low"])
                        for i in range(j - IMPULSE_LOOKBACK_BARS, j))
        label["swing_low_price"] = swing_low
        impulse_high = float(bars_15m[j]["high"])
        leg = impulse_high - swing_low
        if leg <= 0:
            label["status"] = "rejected_invalid_geometry"
            labels.append(label)
            continue
        # THE ONLY EDITED RULE: pullback bar = lower low OR lower close
        k = 0
        while j + k + 1 < n:
            nxt = bars_15m[j + k + 1]
            prev = bars_15m[j + k]
            if (float(nxt["low"]) < float(prev["low"])
                    or float(nxt["close"]) < float(prev["close"])):
                k += 1
                if k > PULLBACK_MAX_BARS:
                    break
            else:
                break
        if k < PULLBACK_MIN_BARS:
            label["status"] = "rejected_pullback_too_short"
            labels.append(label)
            continue
        if k > PULLBACK_MAX_BARS:
            label["status"] = "rejected_pullback_too_long"
            labels.append(label)
            continue
        pullback_bars = bars_15m[j + 1:j + 1 + k]
        pullback_low = min(float(b["low"]) for b in pullback_bars)
        pullback_high = max(float(b["high"]) for b in pullback_bars)
        label["pullback_bar_count"] = k
        label["pullback_low_price"] = pullback_low
        label["pullback_high_price"] = pullback_high
        if pullback_low <= swing_low:
            label["status"] = "rejected_pullback_broke_swing_low"
            labels.append(label)
            continue
        retrace_pct = (impulse_high - pullback_low) / leg * 100.0
        label["retrace_pct_of_impulse_leg"] = round(retrace_pct, 6)
        if retrace_pct > MAX_RETRACE_PCT:
            label["status"] = "rejected_retrace_too_deep"
            labels.append(label)
            continue
        resumption_index = None
        for r in range(j + k + 1,
                       min(j + IMPULSE_FRESHNESS_BARS, n - 1) + 1):
            if float(bars_15m[r]["low"]) < pullback_low:
                break
            if float(bars_15m[r]["close"]) > pullback_high:
                resumption_index = r
                break
        if resumption_index is None:
            label["status"] = "rejected_no_resumption_close"
            labels.append(label)
            continue
        r = resumption_index
        label["resumption_bar_time_utc"] = bars_15m[r]["time_utc"]
        trend = evaluate_trend_qualification(
            bars_1h, bars_15m[r]["time_utc"])
        label["trend_1h_completed_bars"] = trend["completed_bars"]
        label["trend_1h_close"] = trend["close"]
        label["trend_1h_sma20"] = trend["sma20"]
        label["trend_1h_sma20_5_bars_ago"] = trend["sma20_5_bars_ago"]
        label["trend_qualified"] = trend["qualified"]
        if trend["insufficient_history"]:
            label["status"] = "rejected_insufficient_1h_history"
            labels.append(label)
            continue
        if not trend["qualified"]:
            label["status"] = "rejected_trend_not_qualified"
            labels.append(label)
            continue
        entry = float(bars_15m[r]["close"])
        atr = compute_atr14(bars_15m, r)
        if atr is None or atr <= 0:
            label["status"] = "rejected_invalid_geometry"
            labels.append(label)
            continue
        structural_stop = pullback_low
        volatility_stop = entry - ATR_STOP_MULTIPLIER * atr
        stop = min(structural_stop, volatility_stop)
        label["entry_price"] = entry
        label["structural_stop_price"] = structural_stop
        label["atr14_15m"] = round(atr, 6)
        label["volatility_stop_price"] = round(volatility_stop, 6)
        label["stop_price"] = round(stop, 6)
        label["stop_source"] = ("structural_pullback_low"
                                if structural_stop <= volatility_stop
                                else "volatility_1_5x_atr14")
        viability = evaluate_setup_cost_viability(entry, stop)
        label["risk_distance_bps"] = viability[
            "entry_to_stop_distance_bps"]
        label["cost_viable"] = viability["viable"]
        if not viability["viable"]:
            label["status"] = "rejected_cost_floor_risk_too_small"
            labels.append(label)
            continue
        risk = entry - stop
        label["target_2r_price"] = round(entry + 2.0 * risk, 6)
        label["target_3r_price"] = round(entry + 3.0 * risk, 6)
        label["target_4r_price"] = round(entry + 4.0 * risk, 6)
        label["status"] = "accepted_for_replay_review"
        labels.append(label)
    return labels


def build_tc3_mutable_edit_v1(repo_root: Any,
                              tracked_paths: Any = ()) -> dict[str, Any]:
    """Assemble the edit contract, gated on the zero-accepts evidence
    freeze being certified and the ledger intact."""
    record: dict[str, Any] = {
        "schema_version": M1_SCHEMA_VERSION, "label": M1_LABEL,
        "mode": M1_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID, "edit_version": EDIT_VERSION,
        "allowed_edited_fields": list(ALLOWED_EDITED_FIELDS),
        "v1_new_parameters": dict(V1_NEW_PARAMETERS),
        "locked_unchanged": list(LOCKED_UNCHANGED),
        "near_zero_threshold_accepted_labels":
            NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS,
        "pre_committed_failure_rules_v1": list(
            PRE_COMMITTED_FAILURE_RULES_V1),
        "forbidden_changes": list(FORBIDDEN_CHANGES),
        "cost_floor_bps": MINIMUM_RISK_DISTANCE_BPS,
        "not_a_rescue_of_candidate_2": True,
        "one_authorized_edit_only": True,
        "second_edit_requires_separate_human_decision": True,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "executes": False, "writes_files": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False, "revives_candidate_2": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if C1_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C2_STATUS != "REJECTED_KEPT_ON_RECORD":
        record["verdict"] = VERDICT_M1_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    review = build_tc3_labels_review(repo_root, tracked_paths)
    if review["verdict"] != VERDICT_TCL_FROZEN:
        record["verdict"] = VERDICT_M1_BLOCKED
        record["blockers"].append(
            "zero_accepts_evidence_not_certified")
        record["blockers"].extend(review["failures"])
        return record
    record["verdict"] = VERDICT_M1_READY
    return record


def validate_tc3_mutable_edit_v1(record: Any) -> dict[str, Any]:
    """Validate shape, edit scope, and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_M1_READY, VERDICT_M1_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("edit_version") != EDIT_VERSION:
        errors.append("edit_version_tampered")
    if tuple(r.get("allowed_edited_fields") or ()) != (
            ALLOWED_EDITED_FIELDS):
        errors.append("edit_scope_widened")
    if r.get("v1_new_parameters") != V1_NEW_PARAMETERS:
        errors.append("v1_parameters_tampered")
    if tuple(r.get("locked_unchanged") or ()) != LOCKED_UNCHANGED:
        errors.append("locked_list_weakened")
    if r.get("near_zero_threshold_accepted_labels") != (
            NEAR_ZERO_THRESHOLD_ACCEPTED_LABELS):
        errors.append("near_zero_threshold_tampered")
    if tuple(r.get("pre_committed_failure_rules_v1") or ()) != (
            PRE_COMMITTED_FAILURE_RULES_V1):
        errors.append("failure_rules_tampered")
    if tuple(r.get("forbidden_changes") or ()) != FORBIDDEN_CHANGES:
        errors.append("forbidden_changes_weakened")
    if r.get("cost_floor_bps") != MINIMUM_RISK_DISTANCE_BPS:
        errors.append("floor_tampered")
    for key in ("not_a_rescue_of_candidate_2",
                "one_authorized_edit_only",
                "second_edit_requires_separate_human_decision",
                "human_review_required", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked"):
        if r.get(key) is not True:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "revives_candidate_2"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}

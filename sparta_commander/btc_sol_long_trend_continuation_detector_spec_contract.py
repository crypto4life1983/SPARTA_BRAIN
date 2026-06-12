"""SPARTA CANDIDATE #3 DETECTOR SPEC + DRY-RUN PATH (READ-ONLY,
RESEARCH ONLY): BTC_SOL_LONG_TREND_CONTINUATION_V1.

Deterministic labeling rules for the Candidate #3 family. The scanner here
is the ONLY rule implementation -- any future real-candle run tool must
IMPORT these functions so rules cannot drift. This module:

  - labels setups; it never outputs buy/sell, never replays, never claims;
  - checks the 81 bps cost floor AT LABEL TIME via the pushed
    evaluate_setup_cost_viability (27 bps fee honesty preserved for any
    future human-approved replay);
  - runs its dry run ONLY on in-memory synthetic fixtures -- it reads no
    files, touches no staged candles, fetches nothing;
  - is gated on the Candidate #3 strategy spec being READY, which itself
    is gated on Candidate #1 and #2 staying REJECTED_KEPT_ON_RECORD.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any

from sparta_commander.btc_sol_long_trend_continuation_strategy_spec_contract import (
    CANDIDATE_ID,
    SYMBOLS,
    VERDICT_TC_READY,
    build_candidate_3_spec,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    MINIMUM_RISK_DISTANCE_BPS,
    evaluate_setup_cost_viability,
)

TCD_SCHEMA_VERSION = "btc_sol_long_trend_continuation_detector_spec.v1"
TCD_LABEL = ("SPARTA Candidate #3 Detector Spec + Dry-Run Path "
             "(READ-ONLY, RESEARCH ONLY, LABELS ONLY, SYNTHETIC FIXTURES "
             "ONLY, NOT A RESCUE)")
TCD_MODE = "RESEARCH_ONLY"
VERDICT_TCD_READY = "CANDIDATE_3_DETECTOR_SPEC_READY"
VERDICT_TCD_BLOCKED = "CANDIDATE_3_DETECTOR_SPEC_BLOCKED"
VERDICT_TCD_DRY_RUN_PASSED = "CANDIDATE_3_DETECTOR_DRY_RUN_PASSED"
VERDICT_TCD_DRY_RUN_FAILED = "CANDIDATE_3_DETECTOR_DRY_RUN_FAILED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_3_DRY_RUN_REVIEW"

ASSUMED_ROUND_TRIP_COST_BPS = 27  # preserved for future fee-honest replay

TC_LABEL_REQUIRED_FIELDS = (
    "setup_id", "candidate_id", "symbol", "direction",
    "execution_timeframe", "trend_timeframe",
    "impulse_bar_time_utc", "impulse_high_price", "swing_low_price",
    "pullback_bar_count", "pullback_low_price", "pullback_high_price",
    "retrace_pct_of_impulse_leg",
    "trend_1h_completed_bars", "trend_1h_close", "trend_1h_sma20",
    "trend_1h_sma20_5_bars_ago", "trend_qualified",
    "resumption_bar_time_utc", "entry_price",
    "structural_stop_price", "atr14_15m", "volatility_stop_price",
    "stop_price", "stop_source", "risk_distance_bps",
    "cost_viability_floor_bps", "cost_viable",
    "target_2r_price", "target_3r_price", "target_4r_price",
    "status", "label_authorizes_nothing",
)

TC_DETECTOR_STATUSES = (
    "accepted_for_replay_review",
    "rejected_insufficient_1h_history",
    "rejected_trend_not_qualified",
    "rejected_pullback_too_short",
    "rejected_pullback_too_long",
    "rejected_pullback_broke_swing_low",
    "rejected_retrace_too_deep",
    "rejected_no_resumption_close",
    "rejected_cost_floor_risk_too_small",
    "rejected_invalid_geometry",
)

IMPULSE_LOOKBACK_BARS = 20
IMPULSE_FRESHNESS_BARS = 8
PULLBACK_MIN_BARS = 2
PULLBACK_MAX_BARS = 8
MAX_RETRACE_PCT = 61.8
SMA_LENGTH_1H = 20
SMA_RISING_LOOKBACK_1H = 5
MIN_COMPLETED_1H_BARS = SMA_LENGTH_1H + SMA_RISING_LOOKBACK_1H
ATR_LENGTH_15M = 14
ATR_STOP_MULTIPLIER = 1.5


def get_candidate_3_detector_label() -> str:
    return TCD_LABEL


def _parse_utc(stamp: str) -> _dt.datetime:
    return _dt.datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=_dt.timezone.utc)


def sma(values: list, length: int) -> float | None:
    if length <= 0 or len(values) < length:
        return None
    return sum(float(v) for v in values[-length:]) / float(length)


def compute_atr14(bars_15m: list, end_index: int) -> float | None:
    """Simple mean of true ranges over the 14 bars ending at end_index
    inclusive. Deterministic; requires a prior close for every bar used."""
    if end_index < ATR_LENGTH_15M:
        return None
    true_ranges = []
    for i in range(end_index - ATR_LENGTH_15M + 1, end_index + 1):
        bar = bars_15m[i]
        prev_close = float(bars_15m[i - 1]["close"])
        true_ranges.append(max(
            float(bar["high"]) - float(bar["low"]),
            abs(float(bar["high"]) - prev_close),
            abs(float(bar["low"]) - prev_close)))
    return sum(true_ranges) / float(ATR_LENGTH_15M)


def aggregate_1h_from_15m(bars_15m: list) -> list:
    """Aggregate 1h bars strictly from 15m bars; complete 4-quarter hours
    only (same discipline the BP V2 experiment used)."""
    buckets: dict[str, list] = {}
    for bar in bars_15m:
        start = _parse_utc(bar["time_utc"])
        key = start.strftime("%Y-%m-%dT%H:00:00Z")
        buckets.setdefault(key, []).append(bar)
    out = []
    for key in sorted(buckets):
        quarter = buckets[key]
        if len(quarter) != 4:
            continue
        out.append({
            "time_utc": key,
            "open": float(quarter[0]["open"]),
            "high": max(float(b["high"]) for b in quarter),
            "low": min(float(b["low"]) for b in quarter),
            "close": float(quarter[-1]["close"])})
    return out


def evaluate_trend_qualification(bars_1h: list,
                                 signal_open_utc: str) -> dict[str, Any]:
    """1h trend gate at the 15m signal bar: only 1h bars COMPLETED before
    the signal bar's open may be used (anti-lookahead). Pure."""
    signal_open = _parse_utc(signal_open_utc)
    completed = [bar for bar in bars_1h
                 if _parse_utc(bar["time_utc"])
                 + _dt.timedelta(hours=1) <= signal_open]
    result: dict[str, Any] = {
        "qualified": False, "completed_bars": len(completed),
        "close": None, "sma20": None, "sma20_5_bars_ago": None,
        "insufficient_history": False}
    if len(completed) < MIN_COMPLETED_1H_BARS:
        result["insufficient_history"] = True
        return result
    closes = [float(bar["close"]) for bar in completed]
    result["close"] = closes[-1]
    result["sma20"] = sma(closes, SMA_LENGTH_1H)
    result["sma20_5_bars_ago"] = sma(
        closes[:-SMA_RISING_LOOKBACK_1H], SMA_LENGTH_1H)
    result["qualified"] = (
        result["close"] > result["sma20"]
        and result["sma20"] > result["sma20_5_bars_ago"])
    return result


def _empty_label(symbol: str, impulse_index: int,
                 bars_15m: list) -> dict[str, Any]:
    impulse_bar = bars_15m[impulse_index]
    label: dict[str, Any] = {field: None
                             for field in TC_LABEL_REQUIRED_FIELDS}
    label.update({
        "setup_id": "%s_%s" % (symbol, impulse_bar["time_utc"]),
        "candidate_id": CANDIDATE_ID, "symbol": symbol,
        "direction": "long", "execution_timeframe": "15m",
        "trend_timeframe": "1h",
        "impulse_bar_time_utc": impulse_bar["time_utc"],
        "impulse_high_price": float(impulse_bar["high"]),
        "cost_viability_floor_bps": MINIMUM_RISK_DISTANCE_BPS,
        "cost_viable": False, "trend_qualified": False,
        "label_authorizes_nothing": True,
    })
    return label


def scan_tc_setups(bars_15m: list, bars_1h: list,
                   symbol: str) -> list[dict[str, Any]]:
    """THE deterministic Candidate #3 scanner. One label per impulse bar
    (one setup per impulse). Labels only; authorizes nothing. Pure."""
    if symbol not in SYMBOLS:
        raise ValueError("symbol_outside_candidate_3_scope:" + str(symbol))
    labels: list[dict[str, Any]] = []
    n = len(bars_15m)
    for j in range(IMPULSE_LOOKBACK_BARS, n):
        closes_before = [float(bars_15m[i]["close"])
                         for i in range(j - IMPULSE_LOOKBACK_BARS + 1, j)]
        if float(bars_15m[j]["close"]) <= max(closes_before):
            continue  # not a new 20-bar closing high
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
        # pullback: maximal run of consecutive lower-low bars after j
        k = 0
        prev_low = float(bars_15m[j]["low"])
        while (j + k + 1 < n
               and float(bars_15m[j + k + 1]["low"]) < prev_low):
            prev_low = float(bars_15m[j + k + 1]["low"])
            k += 1
            if k > PULLBACK_MAX_BARS:
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
        # resumption: first close above pullback high, impulse still fresh
        resumption_index = None
        for r in range(j + k + 1, min(j + IMPULSE_FRESHNESS_BARS, n - 1) + 1):
            if float(bars_15m[r]["low"]) < pullback_low:
                break  # structure failed before resumption
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
        stop = min(structural_stop, volatility_stop)  # WIDER for a long
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


def validate_tc_label(label: Any) -> dict[str, Any]:
    """Schema + closed-status + floor gate over one label. Never raises."""
    errors: list[str] = []
    if not isinstance(label, dict):
        return {"valid": False, "errors": ["label_not_a_dict"]}
    for field in TC_LABEL_REQUIRED_FIELDS:
        if field not in label:
            errors.append("missing_label_field:" + field)
    if errors:
        return {"valid": False, "errors": errors}
    if label.get("status") not in TC_DETECTOR_STATUSES:
        errors.append("status_outside_closed_set:"
                      + str(label.get("status")))
    if label.get("candidate_id") != CANDIDATE_ID:
        errors.append("wrong_candidate_id")
    if label.get("symbol") not in SYMBOLS:
        errors.append("symbol_outside_btc_sol")
    if label.get("direction") != "long":
        errors.append("not_long_only")
    if label.get("cost_viability_floor_bps") != MINIMUM_RISK_DISTANCE_BPS:
        errors.append("floor_tampered")
    if label.get("label_authorizes_nothing") is not True:
        errors.append("label_must_authorize_nothing")
    if label.get("status") == "accepted_for_replay_review":
        risk_bps = label.get("risk_distance_bps")
        if not isinstance(risk_bps, (int, float)) \
                or risk_bps < MINIMUM_RISK_DISTANCE_BPS:
            errors.append("accepted_label_below_81bps_floor")
        if label.get("cost_viable") is not True:
            errors.append("accepted_label_not_cost_viable")
    return {"valid": not errors, "errors": errors}


# --- synthetic fixtures (in-memory only; no files, no staged candles) ------

def _stamp_15m(index: int) -> str:
    base = _dt.datetime(2026, 1, 2, 12, 0, tzinfo=_dt.timezone.utc)
    return (base + _dt.timedelta(minutes=15 * index)).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def _bar(index: int, open_: float, high: float, low: float,
         close: float) -> dict[str, Any]:
    return {"time_utc": _stamp_15m(index), "open": open_, "high": high,
            "low": low, "close": close}


def _fixture_1h(uptrend: bool) -> list:
    bars = []
    base = _dt.datetime(2026, 1, 1, 6, 0, tzinfo=_dt.timezone.utc)
    for i in range(30):
        close = 100.0 + (1.0 * i if uptrend else -1.0 * i)
        bars.append({
            "time_utc": (base + _dt.timedelta(hours=i)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"),
            "open": close - 0.5, "high": close + 0.6,
            "low": close - 0.8, "close": close})
    return bars


def _fixture_15m_accepted() -> list:
    bars = []
    for i in range(24):
        close = 100.0 + 0.05 * i
        bars.append(_bar(i, close - 0.02, close + 0.05,
                         close - 0.10, close))
    bars.append(_bar(24, 102.0, 102.6, 101.95, 102.5))   # impulse
    bars.append(_bar(25, 102.1, 102.2, 101.8, 101.9))
    bars.append(_bar(26, 101.9, 102.0, 101.65, 101.8))
    bars.append(_bar(27, 101.8, 101.9, 101.5, 101.7))    # pullback low
    bars.append(_bar(28, 102.0, 102.45, 101.9, 102.4))   # resumption
    bars.append(_bar(29, 102.4, 102.6, 102.2, 102.5))
    return bars


def _fixture_15m_tight() -> list:
    bars = []
    for i in range(24):
        close = 100.0 + 0.05 * i
        bars.append(_bar(i, close - 0.02, close + 0.05,
                         close - 0.10, close))
    bars.append(_bar(24, 102.35, 102.6, 102.3, 102.5))   # impulse
    bars.append(_bar(25, 102.4, 102.45, 102.25, 102.4))
    bars.append(_bar(26, 102.35, 102.42, 102.2, 102.35))
    bars.append(_bar(27, 102.3, 102.4, 102.15, 102.3))   # shallow low
    bars.append(_bar(28, 102.35, 102.6, 102.3, 102.55))  # resumption
    bars.append(_bar(29, 102.5, 102.7, 102.4, 102.6))
    return bars


def run_tc_detector_dry_run() -> dict[str, Any]:
    """Run the scanner over IN-MEMORY synthetic fixtures only and check
    the expected outcomes. Reads no files; never sees real candles."""
    record: dict[str, Any] = {
        "schema_version": TCD_SCHEMA_VERSION, "label": TCD_LABEL,
        "mode": TCD_MODE, "verdict": None, "failures": [],
        "fixtures": {}, "uses_synthetic_fixtures_only": True,
        "reads_staged_candles": False, "reads_any_files": False,
    }
    failures = record["failures"]
    uptrend_1h = _fixture_1h(uptrend=True)
    downtrend_1h = _fixture_1h(uptrend=False)

    def _summarize(labels):
        return {"labels": len(labels),
                "statuses": sorted(lab["status"] for lab in labels),
                "schema_valid_all": all(
                    validate_tc_label(lab)["valid"] for lab in labels)}

    accepted_run = scan_tc_setups(
        _fixture_15m_accepted(), uptrend_1h, "BTCUSD")
    record["fixtures"]["accepted_fixture"] = _summarize(accepted_run)
    winners = [lab for lab in accepted_run
               if lab["status"] == "accepted_for_replay_review"]
    if len(winners) != 1:
        failures.append("accepted_fixture_expected_exactly_1_accepted")
    else:
        winner = winners[0]
        record["fixtures"]["accepted_fixture"]["risk_distance_bps"] = (
            winner["risk_distance_bps"])
        record["fixtures"]["accepted_fixture"]["stop_source"] = (
            winner["stop_source"])
        if winner["risk_distance_bps"] < MINIMUM_RISK_DISTANCE_BPS:
            failures.append("accepted_fixture_below_floor")
        if winner["stop_source"] != "structural_pullback_low":
            failures.append("accepted_fixture_wrong_stop_source")
        if winner["entry_price"] != 102.4:
            failures.append("accepted_fixture_wrong_entry")
        if winner["stop_price"] != 101.5:
            failures.append("accepted_fixture_wrong_stop")

    tight_run = scan_tc_setups(
        _fixture_15m_tight(), uptrend_1h, "SOLUSD")
    record["fixtures"]["tight_fixture"] = _summarize(tight_run)
    tight_rejects = [lab for lab in tight_run if lab["status"]
                     == "rejected_cost_floor_risk_too_small"]
    if len(tight_rejects) != 1:
        failures.append("tight_fixture_expected_cost_floor_rejection")
    elif any(lab["status"] == "accepted_for_replay_review"
             for lab in tight_run):
        failures.append("tight_fixture_must_accept_nothing")

    downtrend_run = scan_tc_setups(
        _fixture_15m_accepted(), downtrend_1h, "BTCUSD")
    record["fixtures"]["downtrend_fixture"] = _summarize(downtrend_run)
    if any(lab["status"] == "accepted_for_replay_review"
           for lab in downtrend_run):
        failures.append("downtrend_fixture_must_accept_nothing")
    if not any(lab["status"] == "rejected_trend_not_qualified"
               for lab in downtrend_run):
        failures.append("downtrend_fixture_expected_trend_rejection")

    for run in (accepted_run, tight_run, downtrend_run):
        for lab in run:
            if not validate_tc_label(lab)["valid"]:
                failures.append("schema_invalid_label:" + lab["setup_id"])
    record["verdict"] = (VERDICT_TCD_DRY_RUN_PASSED if not failures
                         else VERDICT_TCD_DRY_RUN_FAILED)
    return record


def build_tc_detector_spec_contract() -> dict[str, Any]:
    """Assemble the detector spec contract, gated on the Candidate #3
    strategy spec being READY (itself ledger-gated)."""
    record: dict[str, Any] = {
        "schema_version": TCD_SCHEMA_VERSION, "label": TCD_LABEL,
        "mode": TCD_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "symbols": list(SYMBOLS), "direction": "long_only",
        "label_required_fields": list(TC_LABEL_REQUIRED_FIELDS),
        "detector_statuses": list(TC_DETECTOR_STATUSES),
        "cost_floor_bps": MINIMUM_RISK_DISTANCE_BPS,
        "cost_floor_checked_at_label_time": True,
        "assumed_round_trip_cost_bps": ASSUMED_ROUND_TRIP_COST_BPS,
        "maker_execution_assumed": False,
        "stop_rule": "WIDER_of_structural_and_volatility_stop_always",
        "future_real_run_data_source":
            "existing append-only staged 15m candles only "
            "(separate human approval required before any real run)",
        "dry_run_uses_synthetic_fixtures_only": True,
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
    spec = build_candidate_3_spec()
    if spec["verdict"] != VERDICT_TC_READY:
        record["verdict"] = VERDICT_TCD_BLOCKED
        record["blockers"].append("candidate_3_strategy_spec_not_ready")
        record["blockers"].extend(spec["blockers"])
        return record
    record["verdict"] = VERDICT_TCD_READY
    return record


def validate_tc_detector_spec_contract(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_TCD_READY, VERDICT_TCD_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(r.get("label_required_fields") or ()) != (
            TC_LABEL_REQUIRED_FIELDS):
        errors.append("label_schema_tampered")
    if tuple(r.get("detector_statuses") or ()) != TC_DETECTOR_STATUSES:
        errors.append("statuses_tampered")
    if r.get("cost_floor_bps") != MINIMUM_RISK_DISTANCE_BPS:
        errors.append("floor_tampered")
    if r.get("cost_floor_checked_at_label_time") is not True:
        errors.append("floor_not_label_time")
    if r.get("assumed_round_trip_cost_bps") != 27:
        errors.append("fee_model_tampered")
    if r.get("maker_execution_assumed") is not False:
        errors.append("maker_execution_assumed")
    if r.get("stop_rule") != (
            "WIDER_of_structural_and_volatility_stop_always"):
        errors.append("stop_rule_weakened")
    if r.get("dry_run_uses_synthetic_fixtures_only") is not True:
        errors.append("dry_run_not_synthetic_only")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if r.get(key) is not want:
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

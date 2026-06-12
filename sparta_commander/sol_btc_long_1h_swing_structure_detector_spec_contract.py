"""SPARTA CANDIDATE #4 DETECTOR SPEC + DRY-RUN PATH (READ-ONLY,
RESEARCH ONLY): SOL_BTC_LONG_1H_SWING_STRUCTURE_V1.

Deterministic labeling rules for the Candidate #4 family. The scanner
here is the ONLY rule implementation -- any future real-candle run tool
must IMPORT these functions so rules cannot drift. Shared math (sma, 14-
bar ATR, 15m->1h aggregation) is IMPORTED from the pushed Candidate #3
detector spec for the same reason; this module adds only the 1h->4h
aggregation and the swing-structure rules.

This module:
  - labels setups; it never outputs buy/sell, never replays, never claims;
  - checks the 81 bps cost floor AT LABEL TIME via the pushed
    evaluate_setup_cost_viability (27 bps fee honesty preserved for any
    future human-approved replay);
  - runs its dry run ONLY on in-memory synthetic fixtures -- it reads no
    files, touches no staged candles, fetches nothing;
  - is gated on the Candidate #4 strategy spec being READY, which itself
    is gated on Candidates #1, #2 AND #3 staying REJECTED_KEPT_ON_RECORD;
  - carries the pre-committed reminder that fewer than 10 accepted labels
    in the future real run triggers the rejection path unless a separate
    human contract says otherwise.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any

from sparta_commander.btc_sol_long_trend_continuation_detector_spec_contract import (
    _parse_utc,
    compute_atr14,
    sma,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability import (
    MINIMUM_RISK_DISTANCE_BPS,
    evaluate_setup_cost_viability,
)
from sparta_commander.sol_btc_long_1h_swing_structure_strategy_spec_contract import (
    CANDIDATE_ID,
    SYMBOLS,
    VERDICT_C4_READY,
    build_candidate_4_spec,
)

C4D_SCHEMA_VERSION = "sol_btc_long_1h_swing_structure_detector_spec.v1"
C4D_LABEL = ("SPARTA Candidate #4 Detector Spec + Dry-Run Path "
             "(READ-ONLY, RESEARCH ONLY, LABELS ONLY, SYNTHETIC FIXTURES "
             "ONLY, NOT A RESCUE)")
C4D_MODE = "RESEARCH_ONLY"
VERDICT_C4D_READY = "CANDIDATE_4_DETECTOR_SPEC_READY"
VERDICT_C4D_BLOCKED = "CANDIDATE_4_DETECTOR_SPEC_BLOCKED"
VERDICT_C4D_DRY_RUN_PASSED = "CANDIDATE_4_DETECTOR_DRY_RUN_PASSED"
VERDICT_C4D_DRY_RUN_FAILED = "CANDIDATE_4_DETECTOR_DRY_RUN_FAILED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_4_DRY_RUN_REVIEW"

ASSUMED_ROUND_TRIP_COST_BPS = 27
NEAR_ZERO_RULE_NOTE = (
    "pre-committed: fewer than 10 accepted labels in the future real run "
    "triggers the rejection path unless a separate human contract says "
    "otherwise")

C4_LABEL_REQUIRED_FIELDS = (
    "setup_id", "candidate_id", "symbol", "direction",
    "execution_timeframe", "trend_timeframe",
    "sl1_bar_time_utc", "sl1_low_price",
    "sl2_bar_time_utc", "sl2_low_price",
    "sl2_confirmation_bar_time_utc", "bars_between_swings",
    "inter_swing_high_price",
    "trend_4h_completed_bars", "trend_4h_close", "trend_4h_sma10",
    "trend_4h_sma10_3_bars_ago", "trend_qualified",
    "trigger_bar_time_utc", "entry_price",
    "structural_stop_price", "atr14_1h", "volatility_stop_price",
    "stop_price", "stop_source", "risk_distance_bps",
    "cost_viability_floor_bps", "cost_viable",
    "target_2r_price", "target_3r_price", "target_4r_price",
    "status", "label_authorizes_nothing",
)

C4_DETECTOR_STATUSES = (
    "accepted_for_replay_review",
    "rejected_not_higher_low",
    "rejected_swings_too_far_apart",
    "rejected_sl2_low_broken_before_entry",
    "rejected_no_trigger_close_within_window",
    "rejected_insufficient_4h_history",
    "rejected_trend_not_qualified",
    "rejected_cost_floor_risk_too_small",
    "rejected_invalid_geometry",
)

SWING_WING_BARS = 2          # strictly lowest of 2 bars each side
SWING_CONFIRMATION_LAG = 2   # confirmed only 2 bars later
MAX_BARS_BETWEEN_SWINGS = 48
MAX_BARS_FROM_CONFIRMATION_TO_TRIGGER = 24
SMA_LENGTH_4H = 10
SMA_RISING_LOOKBACK_4H = 3
MIN_COMPLETED_4H_BARS = SMA_LENGTH_4H + SMA_RISING_LOOKBACK_4H
ATR_STOP_MULTIPLIER = 1.5


def get_candidate_4_detector_label() -> str:
    return C4D_LABEL


def aggregate_4h_from_1h(bars_1h: list) -> list:
    """Aggregate 4h bars strictly from 1h bars; complete 4-hour groups
    only (hours 0-3, 4-7, ...)."""
    buckets: dict[str, list] = {}
    for bar in bars_1h:
        start = _parse_utc(bar["time_utc"])
        group_hour = (start.hour // 4) * 4
        key = start.strftime("%Y-%m-%dT") + "%02d:00:00Z" % group_hour
        buckets.setdefault(key, []).append(bar)
    out = []
    for key in sorted(buckets):
        group = buckets[key]
        if len(group) != 4:
            continue
        out.append({
            "time_utc": key,
            "open": float(group[0]["open"]),
            "high": max(float(b["high"]) for b in group),
            "low": min(float(b["low"]) for b in group),
            "close": float(group[-1]["close"])})
    return out


def evaluate_trend_qualification_4h(bars_4h: list,
                                    signal_open_utc: str) -> dict[str, Any]:
    """4h trend gate at the 1h signal bar: only 4h bars COMPLETED before
    the signal bar's open may be used (anti-lookahead). Pure."""
    signal_open = _parse_utc(signal_open_utc)
    completed = [bar for bar in bars_4h
                 if _parse_utc(bar["time_utc"])
                 + _dt.timedelta(hours=4) <= signal_open]
    result: dict[str, Any] = {
        "qualified": False, "completed_bars": len(completed),
        "close": None, "sma10": None, "sma10_3_bars_ago": None,
        "insufficient_history": False}
    if len(completed) < MIN_COMPLETED_4H_BARS:
        result["insufficient_history"] = True
        return result
    closes = [float(bar["close"]) for bar in completed]
    result["close"] = closes[-1]
    result["sma10"] = sma(closes, SMA_LENGTH_4H)
    result["sma10_3_bars_ago"] = sma(
        closes[:-SMA_RISING_LOOKBACK_4H], SMA_LENGTH_4H)
    result["qualified"] = (
        result["close"] > result["sma10"]
        and result["sma10"] > result["sma10_3_bars_ago"])
    return result


def find_confirmed_swing_lows(bars_1h: list) -> list[int]:
    """Indices of confirmed swing lows: bar i is a swing low when its low
    is strictly lower than the lows of the 2 bars before AND the 2 bars
    after it; it is knowable only at bar i+2 close. Pure."""
    indices = []
    n = len(bars_1h)
    for i in range(SWING_WING_BARS, n - SWING_WING_BARS):
        low_i = float(bars_1h[i]["low"])
        wings = [float(bars_1h[i + d]["low"])
                 for d in (-2, -1, 1, 2)]
        if all(low_i < wing for wing in wings):
            indices.append(i)
    return indices


def _empty_label(symbol: str, i1: int, i2: int,
                 bars_1h: list) -> dict[str, Any]:
    label: dict[str, Any] = {field: None
                             for field in C4_LABEL_REQUIRED_FIELDS}
    label.update({
        "setup_id": "%s_%s" % (symbol, bars_1h[i2]["time_utc"]),
        "candidate_id": CANDIDATE_ID, "symbol": symbol,
        "direction": "long", "execution_timeframe": "1h",
        "trend_timeframe": "4h",
        "sl1_bar_time_utc": bars_1h[i1]["time_utc"],
        "sl1_low_price": float(bars_1h[i1]["low"]),
        "sl2_bar_time_utc": bars_1h[i2]["time_utc"],
        "sl2_low_price": float(bars_1h[i2]["low"]),
        "bars_between_swings": i2 - i1,
        "cost_viability_floor_bps": MINIMUM_RISK_DISTANCE_BPS,
        "cost_viable": False, "trend_qualified": False,
        "label_authorizes_nothing": True,
    })
    return label


def scan_c4_setups(bars_1h: list, bars_4h: list,
                   symbol: str) -> list[dict[str, Any]]:
    """THE deterministic Candidate #4 scanner. One label per consecutive
    confirmed swing-low pair. Labels only; authorizes nothing. Pure."""
    if symbol not in SYMBOLS:
        raise ValueError("symbol_outside_candidate_4_scope:" + str(symbol))
    labels: list[dict[str, Any]] = []
    n = len(bars_1h)
    swings = find_confirmed_swing_lows(bars_1h)
    for pair_index in range(len(swings) - 1):
        i1, i2 = swings[pair_index], swings[pair_index + 1]
        label = _empty_label(symbol, i1, i2, bars_1h)
        confirmation = i2 + SWING_CONFIRMATION_LAG
        label["sl2_confirmation_bar_time_utc"] = (
            bars_1h[confirmation]["time_utc"]
            if confirmation < n else None)
        if i2 - i1 > MAX_BARS_BETWEEN_SWINGS:
            label["status"] = "rejected_swings_too_far_apart"
            labels.append(label)
            continue
        sl1_low = float(bars_1h[i1]["low"])
        sl2_low = float(bars_1h[i2]["low"])
        if sl2_low <= sl1_low:
            label["status"] = "rejected_not_higher_low"
            labels.append(label)
            continue
        between = bars_1h[i1 + 1:i2]
        if not between or confirmation >= n:
            label["status"] = "rejected_invalid_geometry"
            labels.append(label)
            continue
        inter_swing_high = max(float(b["high"]) for b in between)
        label["inter_swing_high_price"] = inter_swing_high
        # trigger: first 1h close above the inter-swing high, observable
        # from the SL2 confirmation bar onward, within 24 bars of it;
        # void first if any low breaks the SL2 low
        trigger_index = None
        void = False
        last = min(confirmation + MAX_BARS_FROM_CONFIRMATION_TO_TRIGGER,
                   n - 1)
        for r in range(confirmation, last + 1):
            if float(bars_1h[r]["low"]) < sl2_low:
                void = True
                break
            if float(bars_1h[r]["close"]) > inter_swing_high:
                trigger_index = r
                break
        if void:
            label["status"] = "rejected_sl2_low_broken_before_entry"
            labels.append(label)
            continue
        if trigger_index is None:
            label["status"] = "rejected_no_trigger_close_within_window"
            labels.append(label)
            continue
        r = trigger_index
        label["trigger_bar_time_utc"] = bars_1h[r]["time_utc"]
        trend = evaluate_trend_qualification_4h(
            bars_4h, bars_1h[r]["time_utc"])
        label["trend_4h_completed_bars"] = trend["completed_bars"]
        label["trend_4h_close"] = trend["close"]
        label["trend_4h_sma10"] = trend["sma10"]
        label["trend_4h_sma10_3_bars_ago"] = trend["sma10_3_bars_ago"]
        label["trend_qualified"] = trend["qualified"]
        if trend["insufficient_history"]:
            label["status"] = "rejected_insufficient_4h_history"
            labels.append(label)
            continue
        if not trend["qualified"]:
            label["status"] = "rejected_trend_not_qualified"
            labels.append(label)
            continue
        entry = float(bars_1h[r]["close"])
        atr = compute_atr14(bars_1h, r)
        if atr is None or atr <= 0:
            label["status"] = "rejected_invalid_geometry"
            labels.append(label)
            continue
        structural_stop = sl2_low
        volatility_stop = entry - ATR_STOP_MULTIPLIER * atr
        stop = min(structural_stop, volatility_stop)  # WIDER for a long
        label["entry_price"] = entry
        label["structural_stop_price"] = structural_stop
        label["atr14_1h"] = round(atr, 6)
        label["volatility_stop_price"] = round(volatility_stop, 6)
        label["stop_price"] = round(stop, 6)
        label["stop_source"] = ("structural_sl2_low"
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


def validate_c4_label(label: Any) -> dict[str, Any]:
    """Schema + closed-status + floor gate over one label. Never raises."""
    errors: list[str] = []
    if not isinstance(label, dict):
        return {"valid": False, "errors": ["label_not_a_dict"]}
    for field in C4_LABEL_REQUIRED_FIELDS:
        if field not in label:
            errors.append("missing_label_field:" + field)
    if errors:
        return {"valid": False, "errors": errors}
    if label.get("status") not in C4_DETECTOR_STATUSES:
        errors.append("status_outside_closed_set:"
                      + str(label.get("status")))
    if label.get("candidate_id") != CANDIDATE_ID:
        errors.append("wrong_candidate_id")
    if label.get("symbol") not in SYMBOLS:
        errors.append("symbol_outside_sol_btc")
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
        sl2 = label.get("sl2_low_price")
        sl1 = label.get("sl1_low_price")
        if not (isinstance(sl1, (int, float))
                and isinstance(sl2, (int, float)) and sl2 > sl1):
            errors.append("accepted_label_not_higher_low")
    return {"valid": not errors, "errors": errors}


# --- synthetic fixtures (in-memory only; no files, no staged candles) ------

def _stamp_1h(index: int) -> str:
    base = _dt.datetime(2026, 2, 2, 0, 0, tzinfo=_dt.timezone.utc)
    return (base + _dt.timedelta(hours=index)).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def _bar(index: int, open_: float, high: float, low: float,
         close: float) -> dict[str, Any]:
    return {"time_utc": _stamp_1h(index), "open": open_, "high": high,
            "low": low, "close": close}


def _fixture_4h(uptrend: bool) -> list:
    bars = []
    base = _dt.datetime(2026, 1, 29, 0, 0, tzinfo=_dt.timezone.utc)
    for i in range(20):
        close = 100.0 + (1.0 * i if uptrend else -1.0 * i)
        bars.append({
            "time_utc": (base + _dt.timedelta(hours=4 * i)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"),
            "open": close - 0.5, "high": close + 0.6,
            "low": close - 0.8, "close": close})
    return bars


def _fixture_1h_accepted() -> list:
    bars = []
    for i in range(10):
        close = 100.0 + 0.05 * i
        bars.append(_bar(i, close - 0.02, close + 0.3,
                         close - 0.3, close))
    bars.append(_bar(10, 100.4, 100.6, 99.0, 100.2))   # SL1
    bars.append(_bar(11, 100.2, 100.9, 99.9, 100.7))
    bars.append(_bar(12, 100.7, 101.2, 100.2, 101.0))
    bars.append(_bar(13, 101.0, 101.5, 100.5, 101.2))  # inter-swing high
    bars.append(_bar(14, 101.2, 101.3, 100.4, 100.7))
    bars.append(_bar(15, 100.7, 100.9, 100.1, 100.3))
    bars.append(_bar(16, 100.3, 100.5, 99.8, 100.1))   # SL2 (higher low)
    bars.append(_bar(17, 100.1, 100.8, 100.0, 100.6))
    bars.append(_bar(18, 100.6, 101.0, 100.2, 100.9))  # SL2 confirmation
    bars.append(_bar(19, 100.9, 101.4, 100.5, 101.3))
    bars.append(_bar(20, 101.3, 102.0, 101.0, 101.8))  # trigger close
    bars.append(_bar(21, 101.8, 102.2, 101.4, 102.0))
    bars.append(_bar(22, 102.0, 102.4, 101.7, 102.2))
    bars.append(_bar(23, 102.2, 102.5, 101.9, 102.3))
    return bars


def _fixture_1h_tight() -> list:
    bars = []
    for i in range(10):
        close = 101.5 + 0.02 * i
        bars.append(_bar(i, close - 0.01, close + 0.1,
                         close - 0.1, close))
    bars.append(_bar(10, 101.65, 101.7, 101.0, 101.6))   # SL1
    bars.append(_bar(11, 101.6, 101.8, 101.35, 101.75))
    bars.append(_bar(12, 101.75, 101.9, 101.5, 101.85))  # inter-swing high
    bars.append(_bar(13, 101.85, 101.85, 101.45, 101.5))
    bars.append(_bar(14, 101.5, 101.6, 101.35, 101.45))
    bars.append(_bar(15, 101.45, 101.55, 101.3, 101.4))  # SL2 (higher low)
    bars.append(_bar(16, 101.4, 101.7, 101.4, 101.65))
    bars.append(_bar(17, 101.65, 101.8, 101.5, 101.75))  # SL2 confirmation
    bars.append(_bar(18, 101.75, 102.0, 101.6, 101.95))  # trigger close
    bars.append(_bar(19, 101.95, 102.1, 101.8, 102.0))
    bars.append(_bar(20, 102.0, 102.15, 101.85, 102.05))
    bars.append(_bar(21, 102.05, 102.2, 101.9, 102.1))
    bars.append(_bar(22, 102.1, 102.25, 101.95, 102.15))
    bars.append(_bar(23, 102.15, 102.3, 102.0, 102.2))
    return bars


def run_c4_detector_dry_run() -> dict[str, Any]:
    """Run the scanner over IN-MEMORY synthetic fixtures only and check
    the expected outcomes. Reads no files; never sees real candles."""
    record: dict[str, Any] = {
        "schema_version": C4D_SCHEMA_VERSION, "label": C4D_LABEL,
        "mode": C4D_MODE, "verdict": None, "failures": [],
        "fixtures": {}, "uses_synthetic_fixtures_only": True,
        "reads_staged_candles": False, "reads_any_files": False,
    }
    failures = record["failures"]
    uptrend_4h = _fixture_4h(uptrend=True)
    downtrend_4h = _fixture_4h(uptrend=False)

    def _summarize(labels):
        return {"labels": len(labels),
                "statuses": sorted(lab["status"] for lab in labels),
                "schema_valid_all": all(
                    validate_c4_label(lab)["valid"] for lab in labels)}

    accepted_run = scan_c4_setups(
        _fixture_1h_accepted(), uptrend_4h, "SOLUSD")
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
        if winner["stop_source"] != "structural_sl2_low":
            failures.append("accepted_fixture_wrong_stop_source")
        if winner["entry_price"] != 101.8:
            failures.append("accepted_fixture_wrong_entry")
        if winner["stop_price"] != 99.8:
            failures.append("accepted_fixture_wrong_stop")
        if winner["inter_swing_high_price"] != 101.5:
            failures.append("accepted_fixture_wrong_inter_swing_high")
        if winner["sl1_low_price"] != 99.0 \
                or winner["sl2_low_price"] != 99.8:
            failures.append("accepted_fixture_wrong_swing_lows")

    tight_run = scan_c4_setups(
        _fixture_1h_tight(), uptrend_4h, "BTCUSD")
    record["fixtures"]["tight_fixture"] = _summarize(tight_run)
    tight_rejects = [lab for lab in tight_run if lab["status"]
                     == "rejected_cost_floor_risk_too_small"]
    if len(tight_rejects) != 1:
        failures.append("tight_fixture_expected_cost_floor_rejection")
    if any(lab["status"] == "accepted_for_replay_review"
           for lab in tight_run):
        failures.append("tight_fixture_must_accept_nothing")

    downtrend_run = scan_c4_setups(
        _fixture_1h_accepted(), downtrend_4h, "SOLUSD")
    record["fixtures"]["downtrend_fixture"] = _summarize(downtrend_run)
    if any(lab["status"] == "accepted_for_replay_review"
           for lab in downtrend_run):
        failures.append("downtrend_fixture_must_accept_nothing")
    if not any(lab["status"] == "rejected_trend_not_qualified"
               for lab in downtrend_run):
        failures.append("downtrend_fixture_expected_trend_rejection")

    for run in (accepted_run, tight_run, downtrend_run):
        for lab in run:
            if not validate_c4_label(lab)["valid"]:
                failures.append("schema_invalid_label:" + lab["setup_id"])
    record["verdict"] = (VERDICT_C4D_DRY_RUN_PASSED if not failures
                         else VERDICT_C4D_DRY_RUN_FAILED)
    return record


def build_c4_detector_spec_contract() -> dict[str, Any]:
    """Assemble the detector spec contract, gated on the Candidate #4
    strategy spec being READY (itself triple-ledger-gated)."""
    record: dict[str, Any] = {
        "schema_version": C4D_SCHEMA_VERSION, "label": C4D_LABEL,
        "mode": C4D_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "symbols": list(SYMBOLS), "direction": "long_only",
        "label_required_fields": list(C4_LABEL_REQUIRED_FIELDS),
        "detector_statuses": list(C4_DETECTOR_STATUSES),
        "cost_floor_bps": MINIMUM_RISK_DISTANCE_BPS,
        "cost_floor_checked_at_label_time": True,
        "assumed_round_trip_cost_bps": ASSUMED_ROUND_TRIP_COST_BPS,
        "maker_execution_assumed": False,
        "stop_rule": "WIDER_of_structural_and_volatility_stop_always",
        "near_zero_rule_note": NEAR_ZERO_RULE_NOTE,
        "future_real_run_data_source":
            "existing append-only staged 15m candles only, aggregated "
            "15m->1h->4h by the pushed aggregators (separate human "
            "approval required before any real run)",
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
        "claims_profitability": False, "revives_candidate_3": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    spec = build_candidate_4_spec()
    if spec["verdict"] != VERDICT_C4_READY:
        record["verdict"] = VERDICT_C4D_BLOCKED
        record["blockers"].append("candidate_4_strategy_spec_not_ready")
        record["blockers"].extend(spec["blockers"])
        return record
    record["verdict"] = VERDICT_C4D_READY
    return record


def validate_c4_detector_spec_contract(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C4D_READY, VERDICT_C4D_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(r.get("label_required_fields") or ()) != (
            C4_LABEL_REQUIRED_FIELDS):
        errors.append("label_schema_tampered")
    if tuple(r.get("detector_statuses") or ()) != C4_DETECTOR_STATUSES:
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
    if r.get("near_zero_rule_note") != NEAR_ZERO_RULE_NOTE:
        errors.append("near_zero_rule_note_tampered")
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
                "claims_profitability", "revives_candidate_3"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}

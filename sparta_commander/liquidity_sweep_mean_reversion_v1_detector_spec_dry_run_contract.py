"""SPARTA CANDIDATE #8 DETECTOR SPEC + SYNTHETIC DRY-RUN PATH
(READ-ONLY, RESEARCH ONLY): LIQUIDITY_SWEEP_MEAN_REVERSION_V1.

Loop stage: detector_and_label_review. Pure deterministic scanner
implementing the pushed Candidate #8 frozen spec EXACTLY:

  - universe BTCUSD only, timeframe 15m, direction long-only;
  - ATR(14) over completed 15m bars (simple-mean of true ranges, via
    the C3-shared compute_atr14 primitive);
  - 96-bar reference-low lookback ending at the bar BEFORE the sweep
    event bar (NO same-bar lookahead in the reference);
  - sweep event: the low of the candidate bar is STRICTLY less than
    reference_low - SWEEP_PENETRATION_ATR_MULTIPLIER x ATR(14);
  - reclaim event: within RECLAIM_WINDOW_BARS (4) completed 15m bars
    AFTER the sweep bar, the FIRST bar that closes STRICTLY above the
    swept reference AND closes in the upper third of its own range
    (close >= low + CLOSE_IN_UPPER_THIRD_FRACTION * (high - low));
  - entry at the reclaim-confirmation bar's close (no intrabar entry);
  - evaluation starts the next 15m bar after the reclaim close;
  - structure stop: stop_price = sweep_low -
    STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER (0.20) x ATR(14) at the sweep
    bar; stop_distance = entry - stop_price; INVALID if stop_distance
    is not positive OR stop is not below sweep_low OR stop is not
    below entry; stop is never tightened after entry;
  - target variants 2r / 3r / 4r; target_price = entry +
    r_multiple x stop_distance;
  - 27 bps round-trip fees + 81 bps gross-target-distance floor per
    variant checked at label time before replay eligibility;
  - 8-bar anti-cluster gap per symbol applied at label-emission time
    AFTER the scanner emits accepted setups and BEFORE replay-time
    non-overlap; tie-breaker keeps the earlier accepted event and
    drops the later same-symbol event whose reclaim_index is within
    8 completed 15m bars of the prior kept event. This anti-cluster
    control is the PROPOSAL-LEVEL locked policy from the pushed spec
    review -- it DOES NOT consume the single allowed C8 edit token;
  - sample-size adequacy: a MINIMUM of 20 accepted setups is required
    at the labels-review gate; the dry-run records the count for
    informational propagation only; the threshold is enforced
    structurally at labels-review, not here. This threshold is the
    PROPOSAL-LEVEL locked policy from the pushed spec review -- it
    DOES NOT consume the single allowed C8 edit token.

PURITY LAW: inputs are in-memory candle rows supplied by callers /
tests. No file reads, no real candles, no staged data, no aggregation
execution, no network, fully deterministic, no wall-clock behavior,
no module-level runner, no order / account / trading capability. The
dry run uses ONLY in-memory synthetic fixtures -- no real candle is
touched until the separately human-approved real-candle gate.

Chain-gated live on: the seven-record rejection ledger (C1-C7), the
pushed C8 family proposal, the pushed C8 spec review, the pushed V3
rejected-family blacklist, the pushed Overnight Research Autopilot
V2, the pushed Recommendation V1, and the pushed Autopilot Loop V1.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as _rec
from sparta_commander.btc_sol_long_trend_continuation_detector_spec_contract import (
    compute_atr14,
)
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
    REJECTION_STATUS as C5_STATUS,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C8P_READY,
    build_candidate_8_family_proposal,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_spec_review_contract import (
    VERDICT_C8S_READY,
    build_candidate_8_spec_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (
    REJECTION_STATUS as C6_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)
from sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract import (
    VERDICT_OAP2_READY,
    build_overnight_research_autopilot_v2_contract,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract import (
    VERDICT_BL3_READY,
    build_rejected_family_blacklist_v3,
)
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C8D_SCHEMA_VERSION = (
    "liquidity_sweep_mean_reversion_v1_detector_spec_dry_run.v1")
C8D_LABEL = ("SPARTA Candidate #8 Detector Spec + Dry-Run Path "
             "(READ-ONLY, RESEARCH ONLY, PURE FUNCTIONS, SYNTHETIC "
             "FIXTURES ONLY, NOT A RESCUE, NOT A CLAIM)")
C8D_MODE = "RESEARCH_ONLY"
VERDICT_C8D_READY = "CANDIDATE_8_DETECTOR_SPEC_READY"
VERDICT_C8D_BLOCKED = "CANDIDATE_8_DETECTOR_SPEC_BLOCKED"
VERDICT_C8D_DRY_RUN_PASSED = "CANDIDATE_8_DETECTOR_DRY_RUN_PASSED"
VERDICT_C8D_DRY_RUN_FAILED = "CANDIDATE_8_DETECTOR_DRY_RUN_FAILED"
VERDICT_C8D_SPEC_DRY_RUN_READY = (
    "CANDIDATE_8_DETECTOR_SPEC_DRY_RUN_READY")
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_8_DRY_RUN_REVIEW"
CURRENT_LOOP_STAGE = "detector_and_label_review"

# ---- frozen numerics (mirror pushed spec review exactly) ------------------
UNIVERSE = ("BTCUSD",)
TIMEFRAME = "15m"
DIRECTION = "long_only"
ATR_LENGTH = 14
RANGE_SWING_LOW_LOOKBACK_BARS = 96
SWEEP_PENETRATION_ATR_MULTIPLIER = 0.25
RECLAIM_WINDOW_BARS = 4
CLOSE_IN_UPPER_THIRD_FRACTION = 2.0 / 3.0
STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER = 0.20
FEE_ROUND_TRIP_BPS = 27.0
TARGET_DISTANCE_FLOOR_BPS = 81.0
TARGET_VARIANTS = (("2r", 2.0), ("3r", 3.0), ("4r", 4.0))
ANTI_CLUSTER_MIN_BAR_GAP = 8
ANTI_CLUSTER_TIE_BREAKER = "keep_the_earlier_event_drop_the_later_one"
SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED = 20

C8_SETUP_REQUIRED_FIELDS = (
    "setup_id", "symbol", "timeframe", "direction",
    "sweep_index", "sweep_time", "sweep_low",
    "reference_low", "reference_minus_penetration",
    "atr_at_sweep_bar",
    "reclaim_window_bars_used",
    "reclaim_index", "reclaim_time", "reclaim_close",
    "reclaim_close_strictly_above_reference",
    "close_in_upper_third_passes",
    "upper_third_threshold",
    "event_index", "event_time", "entry_price",
    "stop_buffer_price", "stop_price", "stop_distance",
    "stop_below_entry", "stop_below_sweep_low",
    "target_2r", "target_3r", "target_4r",
    "target_distance_bps_2r", "target_distance_bps_3r",
    "target_distance_bps_4r",
    "geometry_floor_pass_by_variant",
    "accepted_for_labeling_by_variant",
    "replay_start_time", "status", "rejection_reasons",
)

C8_DETECTOR_STATUSES = (
    "accepted_for_replay_review",
    "rejected_no_qualifying_reclaim_within_4_bars",
    "rejected_invalid_stop_geometry",
    "rejected_geometry_floor",
    "rejected_no_evaluation_bar",
    "rejected_clustered_within_8_bars_of_prior_accepted",
)


def get_candidate_8_detector_label() -> str:
    return C8D_LABEL


def validate_detection_context(symbol: str, timeframe: str,
                               direction: str) -> None:
    """Raise ValueError on any context outside the frozen BTCUSD / 15m /
    long_only universe. Pure."""
    if symbol not in UNIVERSE:
        raise ValueError(
            "symbol_outside_candidate_8_universe:" + str(symbol))
    if timeframe != TIMEFRAME:
        raise ValueError(
            "timeframe_outside_candidate_8_universe:" + str(timeframe))
    if direction != DIRECTION:
        raise ValueError(
            "direction_outside_candidate_8_universe:" + str(direction))


# ---- pure numeric primitives ----------------------------------------------

def compute_reference_low(bars: list, sweep_index: int,
                          lookback: int = RANGE_SWING_LOW_LOOKBACK_BARS
                          ) -> float | None:
    """Lowest low across the `lookback` completed 15m bars ending at
    the bar BEFORE `sweep_index`. Returns None if insufficient history.
    Pure -- the sweep bar's own low is NEVER included (no same-bar
    lookahead in the reference)."""
    if sweep_index < lookback:
        return None
    if sweep_index > len(bars):
        return None
    window = bars[sweep_index - lookback:sweep_index]
    return min(float(b["low"]) for b in window)


def check_sweep_at_bar(bars: list, t: int,
                       atr_values: list) -> dict[str, Any]:
    """Check whether bar t is a sweep bar: strict-below
    (reference_low - SWEEP_PENETRATION_ATR_MULTIPLIER * ATR(14)).
    No future bars. Reference uses ONLY prior bars. Pure."""
    out: dict[str, Any] = {
        "is_sweep": False, "reference_low": None,
        "reference_minus_penetration": None, "atr_at_sweep": None,
        "sweep_low": None,
    }
    if t < RANGE_SWING_LOW_LOOKBACK_BARS or t >= len(bars):
        return out
    atr = atr_values[t] if t < len(atr_values) else None
    if atr is None:
        return out
    ref = compute_reference_low(bars, t)
    if ref is None:
        return out
    threshold = ref - SWEEP_PENETRATION_ATR_MULTIPLIER * atr
    low = float(bars[t]["low"])
    out["reference_low"] = ref
    out["reference_minus_penetration"] = threshold
    out["atr_at_sweep"] = atr
    out["sweep_low"] = low
    if low < threshold:
        out["is_sweep"] = True
    return out


def find_reclaim(bars: list, sweep_index: int, reference_low: float,
                 window: int = RECLAIM_WINDOW_BARS,
                 upper_third: float = CLOSE_IN_UPPER_THIRD_FRACTION
                 ) -> dict[str, Any]:
    """Search the next `window` completed 15m bars after `sweep_index`
    for the FIRST bar whose close is STRICTLY above `reference_low` AND
    whose close lies in the upper third of its own range. Returns a
    dict with the first qualifying reclaim (or None) plus per-bar
    diagnostics for the failure-reason fixtures. Pure."""
    n = len(bars)
    out: dict[str, Any] = {
        "reclaim_index": None, "reclaim_time": None,
        "reclaim_close": None,
        "upper_third_threshold": None,
        "close_strictly_above_reference": None,
        "close_in_upper_third_passes": None,
        "per_bar": [],
        "no_qualifying_reclaim_reason": None,
    }
    start = sweep_index + 1
    end = min(n, start + window)
    saw_close_above_ref = False
    saw_close_in_upper_third = False
    for j in range(start, end):
        bar = bars[j]
        high = float(bar["high"])
        low = float(bar["low"])
        close = float(bar["close"])
        rng = high - low
        ut_threshold = (low + upper_third * rng if rng > 0
                        else None)
        close_above = close > reference_low
        close_in_upper = (ut_threshold is not None
                          and close >= ut_threshold)
        if close_above:
            saw_close_above_ref = True
        if close_in_upper:
            saw_close_in_upper_third = True
        out["per_bar"].append({
            "index": j, "time_utc": bar["time_utc"],
            "close": close, "high": high, "low": low,
            "upper_third_threshold": ut_threshold,
            "close_strictly_above_reference": close_above,
            "close_in_upper_third_passes": close_in_upper})
        if close_above and close_in_upper:
            out["reclaim_index"] = j
            out["reclaim_time"] = bar["time_utc"]
            out["reclaim_close"] = close
            out["upper_third_threshold"] = ut_threshold
            out["close_strictly_above_reference"] = True
            out["close_in_upper_third_passes"] = True
            return out
    if not saw_close_above_ref:
        out["no_qualifying_reclaim_reason"] = (
            "no_bar_within_window_closed_strictly_above_swept"
            "_reference")
    elif not saw_close_in_upper_third:
        out["no_qualifying_reclaim_reason"] = (
            "no_bar_within_window_closed_in_upper_third_of_its"
            "_range")
    else:
        out["no_qualifying_reclaim_reason"] = (
            "no_single_bar_passed_both_strict_above_and_upper_third"
            "_in_the_same_bar")
    return out


def compute_stop(entry_price: float, sweep_low: float,
                 atr_at_sweep: float) -> dict[str, Any]:
    """Structure stop: stop_price = sweep_low -
    STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER (0.20) * ATR(14) at the sweep
    bar. Invalid if stop_distance is not positive OR stop is not below
    entry OR stop is not below sweep_low. Pure."""
    buffer = STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * float(atr_at_sweep)
    stop_price = float(sweep_low) - buffer
    stop_distance = float(entry_price) - stop_price
    stop_below_entry = stop_price < float(entry_price)
    stop_below_sweep_low = stop_price < float(sweep_low)
    valid = (stop_distance > 0.0 and stop_below_entry
             and stop_below_sweep_low)
    return {"stop_buffer_price": buffer,
            "stop_price": stop_price,
            "stop_distance": stop_distance,
            "stop_below_entry": stop_below_entry,
            "stop_below_sweep_low": stop_below_sweep_low,
            "valid": valid}


def geometry_floor_by_variant(entry_price: float,
                              stop_distance: float) -> dict[str, Any]:
    """Per-variant 81 bps gross target-distance floor before replay
    eligibility. 27 bps round-trip fees model; no maker rebate, no
    zero-fee assumption. Pure."""
    out: dict[str, Any] = {"targets": {}, "target_distance_bps": {},
                           "floor_pass": {},
                           "any_variant_passes": False}
    for name, multiple in TARGET_VARIANTS:
        distance = multiple * float(stop_distance)
        bps = (distance / float(entry_price)) * 10000.0
        out["targets"][name] = round(
            float(entry_price) + distance, 6)
        out["target_distance_bps"][name] = round(bps, 6)
        out["floor_pass"][name] = bps >= TARGET_DISTANCE_FLOOR_BPS
    out["any_variant_passes"] = any(out["floor_pass"].values())
    return out


# ---- the deterministic scanner ---------------------------------------------

def _precompute_atr(bars: list) -> list:
    """Pure. Returns ATR(14) at every index using the shared
    compute_atr14 primitive."""
    return [compute_atr14(bars, t) for t in range(len(bars))]


def _empty_setup_record() -> dict[str, Any]:
    return {field: None for field in C8_SETUP_REQUIRED_FIELDS}


def scan_c8_setups(bars: list, symbol: str = "BTCUSD",
                   timeframe: str = TIMEFRAME,
                   direction: str = DIRECTION
                   ) -> list[dict[str, Any]]:
    """THE Candidate #8 scanner. bars is an in-memory list of 15m rows
    ({time_utc, open, high, low, close}). The frozen universe is
    BTCUSD / 15m / long_only -- the function rejects any other context
    by raising ValueError. Pure; labels only; anti-cluster filtering is
    applied AFTER label emission in apply_anti_cluster_filter, NOT
    inside this scanner."""
    validate_detection_context(symbol, timeframe, direction)
    if not isinstance(bars, list):
        raise ValueError("bars_must_be_a_list")
    n = len(bars)
    atr_values = _precompute_atr(bars)
    setups: list[dict[str, Any]] = []
    last_sweep_index_emitted = -1
    for t in range(n):
        if t < RANGE_SWING_LOW_LOOKBACK_BARS:
            # not enough lookback history -- silently skip
            continue
        sweep = check_sweep_at_bar(bars, t, atr_values)
        if not sweep["is_sweep"]:
            continue
        if t <= last_sweep_index_emitted:
            continue
        record = _empty_setup_record()
        sweep_bar = bars[t]
        record.update({
            "setup_id": "%s_%s" % (symbol, sweep_bar["time_utc"]),
            "symbol": symbol, "timeframe": TIMEFRAME,
            "direction": DIRECTION,
            "sweep_index": t,
            "sweep_time": sweep_bar["time_utc"],
            "sweep_low": round(float(sweep["sweep_low"]), 6),
            "reference_low":
                round(float(sweep["reference_low"]), 6),
            "reference_minus_penetration":
                round(float(sweep["reference_minus_penetration"]),
                      6),
            "atr_at_sweep_bar":
                round(float(sweep["atr_at_sweep"]), 6),
            "reclaim_window_bars_used": RECLAIM_WINDOW_BARS,
            "rejection_reasons": [],
        })
        reclaim = find_reclaim(bars, t, sweep["reference_low"])
        if reclaim["reclaim_index"] is None:
            record["close_in_upper_third_passes"] = False
            record["reclaim_close_strictly_above_reference"] = False
            record["status"] = (
                "rejected_no_qualifying_reclaim_within_4_bars")
            reason = reclaim["no_qualifying_reclaim_reason"]
            if reason:
                record["rejection_reasons"].append(reason)
            setups.append(record)
            last_sweep_index_emitted = t
            continue
        entry = float(bars[reclaim["reclaim_index"]]["close"])
        record.update({
            "reclaim_index": reclaim["reclaim_index"],
            "reclaim_time": reclaim["reclaim_time"],
            "reclaim_close": round(float(reclaim["reclaim_close"]),
                                   6),
            "reclaim_close_strictly_above_reference": True,
            "close_in_upper_third_passes": True,
            "upper_third_threshold":
                round(float(reclaim["upper_third_threshold"]), 6),
            "event_index": reclaim["reclaim_index"],
            "event_time": reclaim["reclaim_time"],
            "entry_price": entry,
            "replay_start_time":
                (bars[reclaim["reclaim_index"] + 1]["time_utc"]
                 if reclaim["reclaim_index"] + 1 < n else None),
        })
        stop = compute_stop(entry, sweep["sweep_low"],
                            sweep["atr_at_sweep"])
        record.update({
            "stop_buffer_price": round(stop["stop_buffer_price"], 6),
            "stop_price": round(stop["stop_price"], 6),
            "stop_distance": round(stop["stop_distance"], 6),
            "stop_below_entry": stop["stop_below_entry"],
            "stop_below_sweep_low": stop["stop_below_sweep_low"],
        })
        if not stop["valid"]:
            record["status"] = "rejected_invalid_stop_geometry"
            record["rejection_reasons"].append(
                "stop_distance_not_positive_or_stop_not_below_entry"
                "_or_not_below_sweep_low")
            setups.append(record)
            last_sweep_index_emitted = t
            continue
        floor = geometry_floor_by_variant(entry, stop["stop_distance"])
        record["target_2r"] = floor["targets"]["2r"]
        record["target_3r"] = floor["targets"]["3r"]
        record["target_4r"] = floor["targets"]["4r"]
        record["target_distance_bps_2r"] = (
            floor["target_distance_bps"]["2r"])
        record["target_distance_bps_3r"] = (
            floor["target_distance_bps"]["3r"])
        record["target_distance_bps_4r"] = (
            floor["target_distance_bps"]["4r"])
        record["geometry_floor_pass_by_variant"] = dict(
            floor["floor_pass"])
        record["accepted_for_labeling_by_variant"] = dict(
            floor["floor_pass"])
        if record["replay_start_time"] is None:
            record["status"] = "rejected_no_evaluation_bar"
            record["rejection_reasons"].append(
                "no_next_bar_for_evaluation")
            setups.append(record)
            last_sweep_index_emitted = t
            continue
        if not floor["any_variant_passes"]:
            record["status"] = "rejected_geometry_floor"
            record["rejection_reasons"].append(
                "all_variant_target_distances_below_81_bps")
            setups.append(record)
            last_sweep_index_emitted = t
            continue
        record["status"] = "accepted_for_replay_review"
        setups.append(record)
        last_sweep_index_emitted = t
    return setups


def apply_anti_cluster_filter(setups: list) -> dict[str, Any]:
    """Apply the 8-bar same-symbol anti-cluster gap at label-emission
    time on the chronologically-sorted ACCEPTED events. Tie-breaker:
    keep the earlier accepted event and drop the later one whose
    reclaim_index difference is strictly less than
    ANTI_CLUSTER_MIN_BAR_GAP. This is a PROPOSAL-LEVEL locked policy
    -- it does NOT consume the single allowed C8 edit token (see
    contract field `anti_cluster_does_not_consume_edit_token`)."""
    accepted_chrono = sorted(
        (s for s in setups
         if s.get("status") == "accepted_for_replay_review"),
        key=lambda s: s["event_index"])
    kept: list = []
    dropped: list = []
    last_kept_index = None
    for s in accepted_chrono:
        idx = s["event_index"]
        if (last_kept_index is None
                or (idx - last_kept_index)
                >= ANTI_CLUSTER_MIN_BAR_GAP):
            kept.append(s)
            last_kept_index = idx
        else:
            dropped_record = dict(s)
            dropped_record["status"] = (
                "rejected_clustered_within_8_bars_of_prior_accepted")
            dropped_record["rejection_reasons"] = list(
                s.get("rejection_reasons") or []) + [
                "less_than_8_completed_15m_bars_after_prior_accepted"
                "_event_on_same_symbol"]
            dropped.append(dropped_record)
    return {"kept": kept, "dropped": dropped,
            "anti_cluster_min_bar_gap": ANTI_CLUSTER_MIN_BAR_GAP,
            "tie_breaker": ANTI_CLUSTER_TIE_BREAKER,
            "anti_cluster_does_not_consume_edit_token": True}


def check_sample_size_adequacy(
        accepted_setups: list,
        threshold: int = SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED
        ) -> dict[str, Any]:
    """Sample-size adequacy gate. At the dry-run stage this is an
    INFORMATIONAL count; the structural rejection is enforced at the
    labels-review gate. The threshold is PROPOSAL-LEVEL locked and
    does NOT consume the single allowed C8 edit token. Pure."""
    n = len(accepted_setups)
    return {"accepted_count": n,
            "minimum_required_at_labels_review_gate": threshold,
            "below_minimum_at_dry_run": n < threshold,
            "enforced_at_labels_review_gate_only": True,
            "does_not_consume_edit_token": True}


# ---- synthetic fixtures (in-memory only) ----------------------------------

def _stamp(index: int) -> str:
    """Deterministic stamp for synthetic 15m fixtures (offset only;
    no wall-clock). 96 completed 15m bars per UTC day."""
    day = 1 + index // 96
    minute_of_day = (index % 96) * 15
    hour = minute_of_day // 60
    minute = minute_of_day % 60
    return "2026-05-%02dT%02d:%02d:00Z" % (day, hour, minute)


def _bar(index: int, open_price: float, high: float, low: float,
         close: float) -> dict[str, Any]:
    return {"time_utc": _stamp(index),
            "open": float(open_price),
            "high": float(high),
            "low": float(low),
            "close": float(close)}


def _baseline_bar(index: int) -> dict[str, Any]:
    """Stable 15m baseline bar. base=50000, range=50 (high=50025,
    low=49975), close=open=base. TR (with prev_close=base) is exactly
    50, so ATR(14) over 14 baseline bars is exactly 50.0. The 96-bar
    reference low across baseline bars is exactly 49975.0."""
    return _bar(index, 50000.0, 50025.0, 49975.0, 50000.0)


def fixture_happy_path_sweep_and_reclaim(
        baseline_length: int = 100) -> list:
    """100 baseline bars + 1 deep sweep + 1 qualifying reclaim + 1
    trailing bar for replay. Produces exactly one accepted setup with
    all 3 variants passing the 81 bps floor."""
    bars = [_baseline_bar(i) for i in range(baseline_length)]
    # sweep bar at baseline_length: low far below reference - 0.25*ATR.
    # baseline ATR = 50.0, reference = 49975.0, threshold = 49962.5.
    bars.append(_bar(baseline_length, 50000.0, 50025.0, 49600.0,
                     49620.0))
    # reclaim bar: closes strictly above reference and in upper third.
    bars.append(_bar(baseline_length + 1, 49620.0, 50050.0, 49600.0,
                     50030.0))
    # trailing bar for replay_start_time
    bars.append(_bar(baseline_length + 2, 50030.0, 50050.0, 50000.0,
                     50020.0))
    return bars


def fixture_insufficient_history(
        baseline_length: int = 50) -> list:
    """Only 50 baseline bars + 1 deep sweep + 1 reclaim. The scanner
    cannot evaluate because the 96-bar reference lookback is not
    satisfied -- 0 sweep attempts emitted."""
    bars = [_baseline_bar(i) for i in range(baseline_length)]
    bars.append(_bar(baseline_length, 50000.0, 50025.0, 49600.0,
                     49620.0))
    bars.append(_bar(baseline_length + 1, 49620.0, 50050.0, 49600.0,
                     50030.0))
    bars.append(_bar(baseline_length + 2, 50030.0, 50050.0, 50000.0,
                     50020.0))
    return bars


def fixture_equality_at_sweep_threshold(
        baseline_length: int = 100) -> list:
    """100 baseline bars + 1 bar whose low EXACTLY equals
    (reference_low - 0.25 * ATR(14)) and whose own TR is engineered to
    keep ATR(14) at exactly 50.0 (so the threshold computation is
    stable at 49962.5). Strict-below requires low < threshold, so
    equality fails the sweep -- 0 attempts emitted."""
    bars = [_baseline_bar(i) for i in range(baseline_length)]
    # The candidate bar: O=49975, H=50012.5, L=49962.5, C=49975.
    # TR = max(50, 12.5, 37.5) = 50, keeping ATR(14) exactly 50.0.
    bars.append(_bar(baseline_length, 49975.0, 50012.5, 49962.5,
                     49975.0))
    bars.append(_baseline_bar(baseline_length + 1))
    bars.append(_baseline_bar(baseline_length + 2))
    return bars


def fixture_reclaim_too_late(baseline_length: int = 100) -> list:
    """100 baseline + sweep + 4 quiet bars + reclaim at offset 5.
    The 4-bar reclaim window covers offsets 1..4; the only qualifying
    bar is at offset 5, which is OUTSIDE the window. The scanner emits
    one attempt that rejects on
    `rejected_no_qualifying_reclaim_within_4_bars`."""
    bars = [_baseline_bar(i) for i in range(baseline_length)]
    bars.append(_bar(baseline_length, 50000.0, 50025.0, 49600.0,
                     49620.0))
    # 4 quiet baseline bars in the window: their close (50000) IS
    # strictly above the swept reference (49975), but their close is
    # NOT in the upper third of their range (upper_third threshold =
    # 49975 + (2/3)*50 = 50008.33; close 50000 < threshold). So none
    # of bars 101..104 qualifies as reclaim.
    for j in range(1, RECLAIM_WINDOW_BARS + 1):
        bars.append(_baseline_bar(baseline_length + j))
    # The first qualifying reclaim sits at offset 5, OUTSIDE the
    # 4-bar window.
    bars.append(_bar(baseline_length + RECLAIM_WINDOW_BARS + 1,
                     49620.0, 50050.0, 49920.0, 50030.0))
    bars.append(_bar(baseline_length + RECLAIM_WINDOW_BARS + 2,
                     50030.0, 50050.0, 50000.0, 50020.0))
    return bars


def fixture_reclaim_close_equals_reference(
        baseline_length: int = 100) -> list:
    """100 baseline + sweep + ALL FOUR window bars closing EXACTLY at
    the swept reference (49975). Strict-above requires close >
    reference, so equality fails on every candidate bar. No bar in the
    window closes above the reference -- one attempt is emitted with
    rejection reason
    `no_bar_within_window_closed_strictly_above_swept_reference`."""
    bars = [_baseline_bar(i) for i in range(baseline_length)]
    bars.append(_bar(baseline_length, 50000.0, 50025.0, 49600.0,
                     49620.0))
    # All RECLAIM_WINDOW_BARS candidate bars: close = 49975 (= swept
    # reference). Range tight enough that upper-third would pass
    # (close >= low + 2/3 * (high - low)), so the only failing
    # criterion is strict-above.
    for j in range(1, RECLAIM_WINDOW_BARS + 1):
        bars.append(_bar(baseline_length + j,
                         49975.0, 49980.0, 49960.0, 49975.0))
    bars.append(_baseline_bar(baseline_length + RECLAIM_WINDOW_BARS
                              + 1))
    return bars


def fixture_close_not_in_upper_third(
        baseline_length: int = 100) -> list:
    """100 baseline + sweep + reclaim candidate at offset 1 whose
    close IS strictly above the swept reference (49975) but lies in
    the lower 2/3 of its own range (close = 49980, range
    [49900, 50100], upper-third threshold = 50033.33). One attempt
    emitted with reason
    `no_bar_within_window_closed_in_upper_third_of_its_range`."""
    bars = [_baseline_bar(i) for i in range(baseline_length)]
    bars.append(_bar(baseline_length, 50000.0, 50025.0, 49600.0,
                     49620.0))
    # close above reference but not in upper third.
    bars.append(_bar(baseline_length + 1, 49620.0, 50100.0, 49900.0,
                     49980.0))
    # 3 quiet baseline bars (none qualifies).
    for j in range(2, RECLAIM_WINDOW_BARS + 1):
        bars.append(_baseline_bar(baseline_length + j))
    bars.append(_baseline_bar(baseline_length + RECLAIM_WINDOW_BARS
                              + 1))
    return bars


def fixture_geometry_floor_all_variants_fail(
        baseline_length: int = 100) -> list:
    """100 baseline + shallow sweep + qualifying reclaim with very
    small stop distance so that even the 4r target distance is below
    81 bps. One attempt emitted with status
    `rejected_geometry_floor`."""
    bars = [_baseline_bar(i) for i in range(baseline_length)]
    # shallow sweep just below threshold: L=49960 (threshold=49962.5,
    # 49960 < 49962.5 -> True). The sweep bar TR raises ATR slightly;
    # the resulting buffer is small.
    bars.append(_bar(baseline_length, 50000.0, 50025.0, 49960.0,
                     49980.0))
    # reclaim bar: close above 49975 in tight upper-third range.
    bars.append(_bar(baseline_length + 1, 49980.0, 49990.0, 49960.0,
                     49985.0))
    bars.append(_baseline_bar(baseline_length + 2))
    return bars


def fixture_symbol_outside_universe(
        baseline_length: int = 100) -> list:
    """Bars are well-formed -- the universe rejection happens inside
    scan_c8_setups when symbol is not 'BTCUSD'."""
    return fixture_happy_path_sweep_and_reclaim(baseline_length)


# ---- dry run --------------------------------------------------------------

def run_c8_detector_dry_run() -> dict[str, Any]:
    """Run the scanner over IN-MEMORY synthetic fixtures only and check
    expected outcomes. Touches no real candles, no staged data."""
    record: dict[str, Any] = {
        "schema_version": C8D_SCHEMA_VERSION, "label": C8D_LABEL,
        "mode": C8D_MODE, "verdict": None, "failures": [],
        "fixtures": {}, "uses_synthetic_fixtures_only": True,
        "reads_real_candles": False, "reads_staged_data": False,
        "reads_any_files": False,
    }
    failures = record["failures"]

    # Fixture A: valid sweep + qualifying reclaim -> 1 accepted with
    # all 3 floor variants passing.
    bars_a = fixture_happy_path_sweep_and_reclaim()
    setups_a = scan_c8_setups(bars_a, "BTCUSD")
    accepted_a = [s for s in setups_a
                  if s["status"] == "accepted_for_replay_review"]
    record["fixtures"]["valid_sweep_and_reclaim"] = {
        "attempts": len(setups_a),
        "accepted": len(accepted_a),
        "first_accepted_floor_pass": (
            accepted_a[0]["geometry_floor_pass_by_variant"]
            if accepted_a else None)}
    if len(accepted_a) != 1:
        failures.append(
            "valid_sweep_and_reclaim_expected_1_accepted_got_%d"
            % len(accepted_a))
    elif accepted_a[0]["geometry_floor_pass_by_variant"] != {
            "2r": True, "3r": True, "4r": True}:
        failures.append(
            "valid_sweep_and_reclaim_floor_unexpected")
    elif accepted_a[0]["entry_price"] != float(
            bars_a[accepted_a[0]["reclaim_index"]]["close"]):
        failures.append(
            "happy_path_entry_must_equal_reclaim_close")
    elif accepted_a[0]["stop_distance"] <= 0.0:
        failures.append("happy_path_stop_distance_must_be_positive")
    elif not (accepted_a[0]["stop_below_entry"]
              and accepted_a[0]["stop_below_sweep_low"]):
        failures.append("happy_path_stop_geometry_violated")

    # Fixture B: insufficient history -> 0 attempts.
    bars_b = fixture_insufficient_history()
    setups_b = scan_c8_setups(bars_b, "BTCUSD")
    record["fixtures"]["insufficient_history"] = {
        "attempts": len(setups_b)}
    if setups_b:
        failures.append(
            "insufficient_history_must_emit_zero_attempts_got_%d"
            % len(setups_b))

    # Fixture C: low equal to threshold -> strict-below fails, 0
    # attempts.
    bars_c = fixture_equality_at_sweep_threshold()
    setups_c = scan_c8_setups(bars_c, "BTCUSD")
    record["fixtures"]["equality_at_sweep_threshold"] = {
        "attempts": len(setups_c)}
    if setups_c:
        failures.append(
            "equality_at_sweep_threshold_must_not_trigger_a_sweep"
            "_got_%d_attempts" % len(setups_c))

    # Fixture D: reclaim too late -> attempt rejects on no qualifying
    # reclaim within 4 bars.
    bars_d = fixture_reclaim_too_late()
    setups_d = scan_c8_setups(bars_d, "BTCUSD")
    accepted_d = [s for s in setups_d
                  if s["status"] == "accepted_for_replay_review"]
    rejected_d = [s for s in setups_d
                  if s["status"] == (
                      "rejected_no_qualifying_reclaim_within_4_bars")]
    record["fixtures"]["reclaim_too_late"] = {
        "attempts": len(setups_d), "accepted": len(accepted_d),
        "rejected_no_qualifying_reclaim": len(rejected_d)}
    if accepted_d:
        failures.append("reclaim_too_late_should_not_accept")
    if len(rejected_d) != 1:
        failures.append(
            "reclaim_too_late_expected_1_rejection_got_%d"
            % len(rejected_d))
    elif "no_bar_within_window_closed_in_upper_third_of_its_range" \
            not in (rejected_d[0]["rejection_reasons"] or []):
        failures.append(
            "reclaim_too_late_should_record_upper_third_failure_"
            "reason")

    # Fixture E: reclaim close == reference -> strict-above fails.
    bars_e = fixture_reclaim_close_equals_reference()
    setups_e = scan_c8_setups(bars_e, "BTCUSD")
    accepted_e = [s for s in setups_e
                  if s["status"] == "accepted_for_replay_review"]
    rejected_e = [s for s in setups_e
                  if s["status"] == (
                      "rejected_no_qualifying_reclaim_within_4_bars")]
    record["fixtures"]["reclaim_close_equals_reference"] = {
        "attempts": len(setups_e), "accepted": len(accepted_e),
        "rejected_no_qualifying_reclaim": len(rejected_e),
        "rejection_reasons":
            (rejected_e[0]["rejection_reasons"] if rejected_e
             else None)}
    if accepted_e:
        failures.append(
            "reclaim_close_equals_reference_should_not_accept")
    if len(rejected_e) != 1:
        failures.append(
            "reclaim_close_equals_reference_expected_1_rejection")
    elif ("no_bar_within_window_closed_strictly_above_swept"
            "_reference") not in (rejected_e[0]["rejection_reasons"]
                                  or []):
        failures.append(
            "reclaim_close_equals_reference_should_record_strict"
            "_above_failure_reason")

    # Fixture F: close not in upper third -> upper-third fails.
    bars_f = fixture_close_not_in_upper_third()
    setups_f = scan_c8_setups(bars_f, "BTCUSD")
    accepted_f = [s for s in setups_f
                  if s["status"] == "accepted_for_replay_review"]
    rejected_f = [s for s in setups_f
                  if s["status"] == (
                      "rejected_no_qualifying_reclaim_within_4_bars")]
    record["fixtures"]["close_not_in_upper_third"] = {
        "attempts": len(setups_f), "accepted": len(accepted_f),
        "rejected_no_qualifying_reclaim": len(rejected_f),
        "rejection_reasons":
            (rejected_f[0]["rejection_reasons"] if rejected_f
             else None)}
    if accepted_f:
        failures.append("close_not_in_upper_third_should_not_accept")
    if len(rejected_f) != 1:
        failures.append(
            "close_not_in_upper_third_expected_1_rejection")
    elif ("no_bar_within_window_closed_in_upper_third_of_its_range"
            ) not in (rejected_f[0]["rejection_reasons"] or []):
        failures.append(
            "close_not_in_upper_third_should_record_upper_third"
            "_failure_reason")

    # Fixture G: geometry floor fails all variants -> rejected.
    bars_g = fixture_geometry_floor_all_variants_fail()
    setups_g = scan_c8_setups(bars_g, "BTCUSD")
    accepted_g = [s for s in setups_g
                  if s["status"] == "accepted_for_replay_review"]
    rejected_g = [s for s in setups_g
                  if s["status"] == "rejected_geometry_floor"]
    record["fixtures"]["geometry_floor_all_variants_fail"] = {
        "attempts": len(setups_g), "accepted": len(accepted_g),
        "rejected_geometry_floor": len(rejected_g),
        "floor_pass_by_variant":
            (rejected_g[0]["geometry_floor_pass_by_variant"]
             if rejected_g else None)}
    if accepted_g:
        failures.append(
            "geometry_floor_all_variants_fail_should_not_accept")
    if len(rejected_g) != 1:
        failures.append(
            "geometry_floor_all_variants_fail_expected_1_rejection")
    elif rejected_g[0]["geometry_floor_pass_by_variant"] != {
            "2r": False, "3r": False, "4r": False}:
        failures.append(
            "geometry_floor_all_variants_fail_unexpected_floor_map")

    # Fixture H: anti-cluster filter -- earlier kept, within-gap
    # dropped, outside-gap kept. Builds 3 synthetic accepted records
    # at offsets 0, +5, +9 from a base reclaim_index.
    if accepted_a:
        base = dict(accepted_a[0])
    else:
        base = {"setup_id": "synthetic_a", "symbol": "BTCUSD",
                "status": "accepted_for_replay_review",
                "event_index": 200, "rejection_reasons": []}
    later_inside = dict(base)
    later_inside["setup_id"] = "synthetic_b_inside"
    later_inside["event_index"] = base["event_index"] + 5
    later_outside = dict(base)
    later_outside["setup_id"] = "synthetic_c_outside"
    later_outside["event_index"] = base["event_index"] + 9
    cluster_result = apply_anti_cluster_filter(
        [base, later_inside, later_outside])
    record["fixtures"]["anti_cluster"] = {
        "kept_ids": [s["setup_id"] for s in cluster_result["kept"]],
        "dropped_ids": [s["setup_id"]
                        for s in cluster_result["dropped"]],
        "anti_cluster_min_bar_gap":
            cluster_result["anti_cluster_min_bar_gap"],
        "anti_cluster_does_not_consume_edit_token":
            cluster_result[
                "anti_cluster_does_not_consume_edit_token"]}
    kept_ids = set(s["setup_id"] for s in cluster_result["kept"])
    dropped_ids = set(s["setup_id"]
                      for s in cluster_result["dropped"])
    if base["setup_id"] not in kept_ids:
        failures.append("anti_cluster_should_keep_earliest_event")
    if "synthetic_b_inside" not in dropped_ids:
        failures.append(
            "anti_cluster_should_drop_event_within_8_bars_of_prior")
    if "synthetic_c_outside" not in kept_ids:
        failures.append(
            "anti_cluster_should_keep_event_at_or_after_8_bar_gap")
    if cluster_result["anti_cluster_min_bar_gap"] != 8:
        failures.append("anti_cluster_min_bar_gap_must_be_8")
    if cluster_result[
            "anti_cluster_does_not_consume_edit_token"] is not True:
        failures.append("anti_cluster_must_not_consume_edit_token")

    # Fixture I: sample-size adequacy -- below threshold and at
    # threshold cases.
    below = check_sample_size_adequacy([{"event_index": i}
                                        for i in range(3)])
    at_threshold = check_sample_size_adequacy(
        [{"event_index": i}
         for i in range(SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED)])
    record["fixtures"]["sample_size_adequacy"] = {
        "below_minimum_at_dry_run":
            below["below_minimum_at_dry_run"],
        "at_threshold_below_flag":
            at_threshold["below_minimum_at_dry_run"],
        "enforced_at_labels_review_gate_only":
            below["enforced_at_labels_review_gate_only"],
        "does_not_consume_edit_token":
            below["does_not_consume_edit_token"]}
    if below["below_minimum_at_dry_run"] is not True:
        failures.append(
            "sample_size_below_threshold_must_flag_below_minimum")
    if at_threshold["below_minimum_at_dry_run"] is not False:
        failures.append(
            "sample_size_at_threshold_must_clear_below_minimum")
    if below["enforced_at_labels_review_gate_only"] is not True:
        failures.append(
            "sample_size_must_be_enforced_at_labels_review_gate_only")
    if below["does_not_consume_edit_token"] is not True:
        failures.append("sample_size_must_not_consume_edit_token")
    if (below["minimum_required_at_labels_review_gate"]
            != SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED):
        failures.append("sample_size_threshold_must_be_20")

    # Fixture J: symbol / timeframe / direction enforcement.
    universe_blocks = {"symbol_eth": False, "timeframe_1h": False,
                       "direction_short": False}
    try:
        scan_c8_setups(bars_a, "ETHUSD")
    except ValueError:
        universe_blocks["symbol_eth"] = True
    try:
        scan_c8_setups(bars_a, "BTCUSD", timeframe="1h")
    except ValueError:
        universe_blocks["timeframe_1h"] = True
    try:
        scan_c8_setups(bars_a, "BTCUSD", timeframe=TIMEFRAME,
                       direction="short_only")
    except ValueError:
        universe_blocks["direction_short"] = True
    record["fixtures"]["context_enforcement"] = universe_blocks
    if not all(universe_blocks.values()):
        failures.append(
            "context_enforcement_must_raise_on_each_off_universe"
            "_value")

    record["verdict"] = (VERDICT_C8D_DRY_RUN_PASSED if not failures
                         else VERDICT_C8D_DRY_RUN_FAILED)
    return record


# ---- the contract record --------------------------------------------------

CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "promotion_can_only_produce_a_human_review_record",
    "anti_cluster_gap_is_proposal_level_locked_not_edit_token",
    "sample_size_threshold_is_proposal_level_locked_not_edit_token",
    "real_candle_detection_gate_locked",
    "labels_gate_locked",
    "replay_gate_locked",
    "relabel_gate_locked",
)


def build_candidate_8_detector_spec_contract() -> dict[str, Any]:
    """Assemble the C8 detector-spec record. Chain-gated on the
    seven-record ledger, the pushed C8 family proposal, the pushed C8
    spec review, the pushed V3 rejected-family blacklist, the pushed
    Overnight Research Autopilot V2, the pushed Recommendation V1,
    and the pushed Autopilot Loop V1."""
    record: dict[str, Any] = {
        "schema_version": C8D_SCHEMA_VERSION, "label": C8D_LABEL,
        "mode": C8D_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "universe": list(UNIVERSE), "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "atr_length": ATR_LENGTH,
        "range_swing_low_lookback_bars": RANGE_SWING_LOW_LOOKBACK_BARS,
        "sweep_penetration_atr_multiplier":
            SWEEP_PENETRATION_ATR_MULTIPLIER,
        "sweep_rule_strict_below_reference_minus_penetration": True,
        "reclaim_window_bars": RECLAIM_WINDOW_BARS,
        "reclaim_close_strictly_above_swept_reference": True,
        "close_in_upper_third_fraction":
            CLOSE_IN_UPPER_THIRD_FRACTION,
        "structure_stop_buffer_atr_multiplier":
            STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER,
        "stop_distance_formula":
            "entry_price - (sweep_low - "
            "STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * ATR14)",
        "stop_never_tightened_after_entry": True,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "no_maker_rebate_assumption": True,
        "no_zero_fee_assumption": True,
        "target_variants": list(name for name, _ in TARGET_VARIANTS),
        "target_price_formula":
            "entry_price + r_multiple * stop_distance",
        "anti_cluster_min_bar_gap": ANTI_CLUSTER_MIN_BAR_GAP,
        "anti_cluster_tie_breaker": ANTI_CLUSTER_TIE_BREAKER,
        "anti_cluster_does_not_consume_edit_token": True,
        "anti_cluster_applied_at":
            "label_emission_time_before_replay_non_overlap",
        "sample_size_adequacy_threshold_min_accepted":
            SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED,
        "sample_size_adequacy_does_not_consume_edit_token": True,
        "sample_size_adequacy_enforced_at_labels_review_gate_only":
            True,
        "no_fetch_ever": True,
        "no_real_time_data": True,
        "staged_data_never_modified": True,
        "detector_required_fields": list(C8_SETUP_REQUIRED_FIELDS),
        "detector_statuses": list(C8_DETECTOR_STATUSES),
        "claim_locks": list(CLAIM_LOCKS),
        "next_required_action": NEXT_REQUIRED_ACTION,
        "current_loop_stage": CURRENT_LOOP_STAGE,
        "ledger_status_seven_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_synthetic_fixture_dry_run_only": True,
        "is_spec_review_only": False,
        "is_a_rescue_attempt": False,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_real_candle_detection": False,
        "runs_relabel": False, "runs_replay": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "uses_account": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False,
        "contains_portfolio_allocation_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "creates_detector_implementation_now": False,
        "computes_pnl_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_real_candle_detection": False,
        "unlocks_detector_now": False, "unlocks_labels_now": False,
        "unlocks_replay_now": False, "unlocks_relabel_now": False,
        "claims_profitability": False,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS)
    record["ledger_status_seven_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C8D_BLOCKED
        record["blockers"].append("seven_record_ledger_broken")
        return record
    if build_candidate_8_family_proposal()["verdict"] != (
            VERDICT_C8P_READY):
        record["verdict"] = VERDICT_C8D_BLOCKED
        record["blockers"].append("candidate_8_proposal_not_certifying")
        return record
    if build_candidate_8_spec_review()["verdict"] != VERDICT_C8S_READY:
        record["verdict"] = VERDICT_C8D_BLOCKED
        record["blockers"].append(
            "candidate_8_spec_review_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C8D_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C8D_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C8D_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C8D_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C8D_READY
    return record


def build_candidate_8_detector_spec_dry_run() -> dict[str, Any]:
    """Run the dry run AND combine with the spec contract to produce
    the combined detector-spec + dry-run record. The combined verdict
    is CANDIDATE_8_DETECTOR_SPEC_DRY_RUN_READY iff the chain-gated spec
    record is READY AND the dry-run record is DRY_RUN_PASSED."""
    spec_record = build_candidate_8_detector_spec_contract()
    dry_record = run_c8_detector_dry_run()
    combined: dict[str, Any] = dict(spec_record)
    combined["dry_run"] = {
        "verdict": dry_record["verdict"],
        "fixtures": dry_record["fixtures"],
        "failures": dry_record["failures"],
        "uses_synthetic_fixtures_only":
            dry_record["uses_synthetic_fixtures_only"],
        "reads_real_candles": dry_record["reads_real_candles"],
        "reads_staged_data": dry_record["reads_staged_data"],
        "reads_any_files": dry_record["reads_any_files"]}
    if combined["verdict"] != VERDICT_C8D_READY:
        combined["combined_verdict"] = VERDICT_C8D_BLOCKED
    elif dry_record["verdict"] != VERDICT_C8D_DRY_RUN_PASSED:
        combined["combined_verdict"] = VERDICT_C8D_DRY_RUN_FAILED
        combined["blockers"].append("dry_run_failed")
        combined["blockers"].extend(dry_record["failures"])
    else:
        combined["combined_verdict"] = VERDICT_C8D_SPEC_DRY_RUN_READY
    return combined


def validate_candidate_8_detector_spec_dry_run(record: Any
                                               ) -> dict[str, Any]:
    """Validate shape, frozen numerics, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    allowed_verdicts = (VERDICT_C8D_READY, VERDICT_C8D_BLOCKED)
    if r.get("verdict") not in allowed_verdicts:
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("universe") != ["BTCUSD"]:
        errors.append("universe_tampered")
    if r.get("timeframe") != "15m" or r.get("direction") != "long_only":
        errors.append("timeframe_or_direction_tampered")
    if r.get("atr_length") != 14:
        errors.append("atr_length_tampered")
    if r.get("range_swing_low_lookback_bars") != 96:
        errors.append("range_swing_low_lookback_must_be_96")
    if r.get("sweep_penetration_atr_multiplier") != 0.25:
        errors.append("sweep_penetration_must_be_0_25")
    if r.get(
            "sweep_rule_strict_below_reference_minus_penetration"
    ) is not True:
        errors.append("sweep_rule_strict_below_weakened")
    if r.get("reclaim_window_bars") != 4:
        errors.append("reclaim_window_must_be_4")
    if r.get(
            "reclaim_close_strictly_above_swept_reference"
    ) is not True:
        errors.append("reclaim_close_strict_above_weakened")
    if abs((r.get("close_in_upper_third_fraction") or 0)
           - (2.0 / 3.0)) > 1e-12:
        errors.append("close_in_upper_third_fraction_must_be_two"
                      "_thirds")
    if r.get("structure_stop_buffer_atr_multiplier") != 0.20:
        errors.append("structure_stop_buffer_must_be_0_20")
    if r.get("stop_distance_formula") != (
            "entry_price - (sweep_low - "
            "STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * ATR14)"):
        errors.append("stop_distance_formula_tampered")
    if r.get("stop_never_tightened_after_entry") is not True:
        errors.append("stop_tightening_protection_weakened")
    if r.get("fee_round_trip_bps") != 27.0:
        errors.append("fee_27bps_changed")
    if r.get("target_distance_floor_bps") != 81.0:
        errors.append("floor_81bps_changed")
    if r.get("no_maker_rebate_assumption") is not True \
            or r.get("no_zero_fee_assumption") is not True:
        errors.append("fee_assumption_weakened")
    if r.get("target_variants") != ["2r", "3r", "4r"]:
        errors.append("target_variants_tampered")
    if r.get("target_price_formula") != (
            "entry_price + r_multiple * stop_distance"):
        errors.append("target_price_formula_tampered")
    if r.get("anti_cluster_min_bar_gap") != 8:
        errors.append("anti_cluster_gap_must_be_8")
    if r.get("anti_cluster_tie_breaker") != (
            "keep_the_earlier_event_drop_the_later_one"):
        errors.append("anti_cluster_tie_breaker_tampered")
    if r.get("anti_cluster_does_not_consume_edit_token") is not True:
        errors.append("anti_cluster_must_not_consume_edit_token")
    if r.get("anti_cluster_applied_at") != (
            "label_emission_time_before_replay_non_overlap"):
        errors.append("anti_cluster_timing_tampered")
    if r.get("sample_size_adequacy_threshold_min_accepted") != 20:
        errors.append("sample_size_threshold_must_be_20")
    if r.get(
            "sample_size_adequacy_does_not_consume_edit_token"
    ) is not True:
        errors.append("sample_size_must_not_consume_edit_token")
    if r.get(
            "sample_size_adequacy_enforced_at_labels_review_gate_only"
    ) is not True:
        errors.append(
            "sample_size_must_be_enforced_at_labels_review_gate_only")
    if r.get("no_fetch_ever") is not True \
            or r.get("staged_data_never_modified") is not True \
            or r.get("no_real_time_data") is not True:
        errors.append("data_boundary_weakened")
    if list(r.get("detector_required_fields") or ()) != list(
            C8_SETUP_REQUIRED_FIELDS):
        errors.append("detector_required_fields_tampered")
    if list(r.get("detector_statuses") or ()) != list(
            C8_DETECTOR_STATUSES):
        errors.append("detector_statuses_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    if r.get("current_loop_stage") != CURRENT_LOOP_STAGE:
        errors.append("current_loop_stage_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_synthetic_fixture_dry_run_only", True),
                      ("is_spec_review_only", False),
                      ("is_a_rescue_attempt", False)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_relabel", "runs_replay",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_detector_now",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C8D_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}

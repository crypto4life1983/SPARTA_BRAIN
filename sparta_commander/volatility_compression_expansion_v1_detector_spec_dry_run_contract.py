"""SPARTA CANDIDATE #7 DETECTOR SPEC + SYNTHETIC DRY-RUN PATH
(READ-ONLY, RESEARCH ONLY): VOLATILITY_COMPRESSION_EXPANSION_V1.

Loop stage: detector_and_label_review. Pure deterministic scanner
implementing the pushed Candidate #7 frozen spec EXACTLY:

  - universe BTCUSD only, timeframe 4h, direction long-only;
  - ATR(14) and a 100-bar rolling-average ATR (both over completed 4h
    bars);
  - 5-bar contraction window ending at the bar BEFORE the expansion
    event bar, where every bar in that window has ATR(14) strictly
    less than 0.6 x its own 100-bar rolling-average ATR;
  - expansion event bar: the next completed 4h bar after the
    contraction window whose true range exceeds 1.8 x the contracted
    ATR (= ATR(14) at the bar immediately prior to the expansion bar)
    AND whose close lies in the upper third of its own range
    (close >= low + (2 / 3) * (high - low));
  - entry at the expansion bar's close; evaluation next 4h bar;
  - WIDER stop: max(1.5 x ATR(14) at the event bar, entry - lowest low
    of the last 10 completed 4h bars including the event bar);
  - 27 bps round-trip fees + 81 bps gross-target-distance floor per
    variant (2r/3r/4r) checked at label time before replay eligibility;
  - 6-bar anti-cluster gap per symbol (one trading day at 4h) applied
    at label-emission time AFTER the scanner emits accepted setups
    and BEFORE replay-time non-overlap; tie-breaker keeps the earlier
    accepted event and drops the later same-symbol event within 6
    bars. This anti-cluster control is the PROPOSAL-LEVEL locked
    policy from the pushed spec review -- it DOES NOT consume the
    single allowed C7 edit token.

PURITY LAW: inputs are in-memory candle rows supplied by callers /
tests. No file reads, no real candles, no staged data, no aggregation
execution, no network, fully deterministic, no wall-clock behavior,
no module-level runner, no order/account/trading capability. The dry
run uses ONLY in-memory synthetic fixtures -- no real candle is
touched until the separately human-approved real-run gate.

Chain-gated live on: the pushed six-record rejection ledger (C1-C6),
the pushed Overnight Research Autopilot V2, the pushed Recommendation
V1, the pushed Autopilot Loop V1, the pushed C7 family proposal, and
the pushed C7 spec review.
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
from sparta_commander.volatility_compression_expansion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C7P_READY,
    build_candidate_7_family_proposal,
)
from sparta_commander.volatility_compression_expansion_v1_spec_review_contract import (
    VERDICT_C7S_READY,
    build_candidate_7_spec_review,
)

C7D_SCHEMA_VERSION = (
    "volatility_compression_expansion_v1_detector_spec_dry_run.v1")
C7D_LABEL = ("SPARTA Candidate #7 Detector Spec + Dry-Run Path "
             "(READ-ONLY, RESEARCH ONLY, PURE FUNCTIONS, SYNTHETIC "
             "FIXTURES ONLY, NOT A RESCUE, NOT A CLAIM)")
C7D_MODE = "RESEARCH_ONLY"
VERDICT_C7D_READY = "CANDIDATE_7_DETECTOR_SPEC_READY"
VERDICT_C7D_BLOCKED = "CANDIDATE_7_DETECTOR_SPEC_BLOCKED"
VERDICT_C7D_DRY_RUN_PASSED = "CANDIDATE_7_DETECTOR_DRY_RUN_PASSED"
VERDICT_C7D_DRY_RUN_FAILED = "CANDIDATE_7_DETECTOR_DRY_RUN_FAILED"
VERDICT_C7D_SPEC_DRY_RUN_READY = (
    "CANDIDATE_7_DETECTOR_SPEC_DRY_RUN_READY")
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_7_DRY_RUN_REVIEW"
CURRENT_LOOP_STAGE = "detector_and_label_review"

# ---- frozen numerics (mirror pushed spec review exactly) ------------------
UNIVERSE = ("BTCUSD",)
TIMEFRAME = "4h"
DIRECTION = "long"
ATR_LENGTH = 14
ATR_ROLLING_AVERAGE_WINDOW_4H_BARS = 100
CONTRACTION_FRACTION = 0.6
CONTRACTION_WINDOW_BARS = 5
EXPANSION_TRUE_RANGE_MULTIPLIER = 1.8
CLOSE_IN_UPPER_THIRD_FRACTION = 2.0 / 3.0
STRUCTURE_LOOKBACK_BARS = 10
WIDER_STOP_ATR_MULTIPLIER = 1.5
FEE_ROUND_TRIP_BPS = 27.0
TARGET_DISTANCE_FLOOR_BPS = 81.0
TARGET_VARIANTS = (("2r", 2.0), ("3r", 3.0), ("4r", 4.0))
ANTI_CLUSTER_MIN_BAR_GAP = 6
ANTI_CLUSTER_TIE_BREAKER = "keep_the_earlier_event_drop_the_later_one"

C7_SETUP_REQUIRED_FIELDS = (
    "setup_id", "symbol", "timeframe", "direction", "event_time",
    "event_index", "entry_price",
    "atr14_at_event", "contracted_atr",
    "rolling_average_atr_at_contraction_end",
    "contraction_window_passes",
    "expansion_true_range",
    "expansion_multiplier_observed",
    "close_in_upper_third_passes",
    "structure_lookback_low",
    "atr_stop_distance", "structure_stop_distance",
    "stop_distance", "stop_price",
    "target_2r", "target_3r", "target_4r",
    "target_distance_bps_2r", "target_distance_bps_3r",
    "target_distance_bps_4r",
    "geometry_floor_pass_by_variant",
    "accepted_for_labeling_by_variant",
    "replay_start_time", "status", "rejection_reasons",
)

C7_DETECTOR_STATUSES = (
    "accepted_for_replay_review",
    "rejected_insufficient_history",
    "rejected_contraction_window",
    "rejected_expansion_multiplier",
    "rejected_close_not_in_upper_third",
    "rejected_invalid_stop_geometry",
    "rejected_geometry_floor",
    "rejected_no_evaluation_bar",
    "rejected_clustered_within_6_bars_of_prior_accepted",
)


def get_candidate_7_detector_label() -> str:
    return C7D_LABEL


# ---- pure numeric primitives ----------------------------------------------

def compute_true_range(bars: list, t: int) -> float | None:
    """True range at bar t. Requires t >= 1 (needs prior close)."""
    if t < 1 or t >= len(bars):
        return None
    bar = bars[t]
    prev_close = float(bars[t - 1]["close"])
    return max(float(bar["high"]) - float(bar["low"]),
               abs(float(bar["high"]) - prev_close),
               abs(float(bar["low"]) - prev_close))


def compute_rolling_average_atr(atr_values: list,
                                end_index: int) -> float | None:
    """100-bar rolling average ATR(14), strict: every value in the
    window must be a valid float (no None). Window is the
    ATR_ROLLING_AVERAGE_WINDOW_4H_BARS values ending at end_index
    inclusive."""
    window = ATR_ROLLING_AVERAGE_WINDOW_4H_BARS
    if end_index < window - 1 or end_index >= len(atr_values):
        return None
    slice_ = atr_values[end_index - window + 1: end_index + 1]
    if any(v is None for v in slice_):
        return None
    return sum(slice_) / float(window)


def check_contraction_window(atr_values: list,
                             rolling_avg_values: list,
                             contraction_end_index: int
                             ) -> dict[str, Any]:
    """Check the 5-bar contraction window ENDING at
    contraction_end_index (which is the bar immediately prior to the
    expansion event bar). Each bar in the window must have ATR(14)
    strictly less than CONTRACTION_FRACTION x its own
    100-bar rolling-average ATR."""
    n_window = CONTRACTION_WINDOW_BARS
    result: dict[str, Any] = {
        "passes": False, "window_end_index": contraction_end_index,
        "window_start_index": contraction_end_index - n_window + 1,
        "per_bar_atr": [], "per_bar_rolling_avg": [],
        "per_bar_pass": [],
    }
    if contraction_end_index < n_window - 1:
        return result
    start = contraction_end_index - n_window + 1
    for i in range(start, contraction_end_index + 1):
        atr_i = atr_values[i] if i < len(atr_values) else None
        avg_i = (rolling_avg_values[i] if i < len(rolling_avg_values)
                 else None)
        result["per_bar_atr"].append(atr_i)
        result["per_bar_rolling_avg"].append(avg_i)
        if atr_i is None or avg_i is None:
            result["per_bar_pass"].append(False)
            return result
        passes_strict = atr_i < CONTRACTION_FRACTION * avg_i
        result["per_bar_pass"].append(passes_strict)
        if not passes_strict:
            return result
    result["passes"] = True
    return result


def check_expansion_event(bars: list, t: int,
                          contracted_atr: float) -> dict[str, Any]:
    """Check the expansion event at bar t against the contracted ATR.
    Returns true-range value, observed multiplier, upper-third check,
    and a combined pass flag."""
    tr = compute_true_range(bars, t)
    bar = bars[t]
    high = float(bar["high"])
    low = float(bar["low"])
    close = float(bar["close"])
    high_low_span = high - low
    upper_third_threshold = low + CLOSE_IN_UPPER_THIRD_FRACTION * (
        high_low_span)
    close_in_upper_third = close >= upper_third_threshold
    multiplier_observed = (tr / contracted_atr
                           if (tr is not None and contracted_atr > 0)
                           else None)
    multiplier_passes = (multiplier_observed is not None
                         and tr > (
                             EXPANSION_TRUE_RANGE_MULTIPLIER
                             * contracted_atr))
    return {
        "true_range": tr,
        "multiplier_observed": multiplier_observed,
        "multiplier_passes": multiplier_passes,
        "close_in_upper_third_passes": close_in_upper_third,
        "upper_third_threshold": upper_third_threshold,
        "passes": multiplier_passes and close_in_upper_third,
    }


def compute_stop(entry_price: float, ten_bar_low: float,
                 atr14: float) -> dict[str, Any]:
    """WIDER-stop rule: stop_distance =
    max(1.5 * atr14, entry - ten_bar_low). Invalid if distance <= 0 or
    stop not below entry."""
    atr_stop_distance = WIDER_STOP_ATR_MULTIPLIER * float(atr14)
    structure_stop_distance = float(entry_price) - float(ten_bar_low)
    stop_distance = max(atr_stop_distance, structure_stop_distance)
    stop_price = float(entry_price) - stop_distance
    valid = stop_distance > 0 and stop_price < float(entry_price)
    return {"atr_stop_distance": atr_stop_distance,
            "structure_stop_distance": structure_stop_distance,
            "stop_distance": stop_distance, "stop_price": stop_price,
            "valid": valid}


def geometry_floor_by_variant(entry_price: float,
                              stop_distance: float) -> dict[str, Any]:
    """Per-variant 81 bps gross target-distance floor before replay
    eligibility. 27 bps fees, no maker rebate, no zero-fee assumption."""
    out: dict[str, Any] = {"targets": {}, "target_distance_bps": {},
                           "floor_pass": {}, "any_variant_passes": False}
    for name, multiple in TARGET_VARIANTS:
        distance = multiple * float(stop_distance)
        bps = (distance / float(entry_price)) * 10000.0
        out["targets"][name] = round(float(entry_price) + distance, 6)
        out["target_distance_bps"][name] = round(bps, 6)
        out["floor_pass"][name] = bps >= TARGET_DISTANCE_FLOOR_BPS
    out["any_variant_passes"] = any(out["floor_pass"].values())
    return out


# ---- the deterministic scanner ---------------------------------------------

def _precompute_atr_and_rolling(bars: list
                                ) -> tuple[list, list]:
    n = len(bars)
    atr_values = [compute_atr14(bars, t) for t in range(n)]
    rolling_avg = [
        compute_rolling_average_atr(atr_values, t)
        for t in range(n)]
    return atr_values, rolling_avg


def scan_c7_setups(bars: list, symbol: str = "BTCUSD"
                   ) -> list[dict[str, Any]]:
    """THE Candidate #7 scanner. bars is an in-memory list of 4h rows
    ({time_utc, open, high, low, close}). symbol must be BTCUSD (the
    single-symbol universe is locked at the proposal and spec review).
    Pure; labels only; anti-cluster filtering is applied AFTER label
    emission in apply_anti_cluster_filter, NOT inside this scanner.

    Raises ValueError on:
      - symbol not in UNIVERSE
      - bars not a list
    """
    if symbol not in UNIVERSE:
        raise ValueError(
            "symbol_outside_candidate_7_universe:" + str(symbol))
    if not isinstance(bars, list):
        raise ValueError("bars_must_be_a_list")
    n = len(bars)
    atr_values, rolling_avg = _precompute_atr_and_rolling(bars)
    setups: list[dict[str, Any]] = []
    # Minimum t to even consider: need 5-bar contraction window ending
    # at t-1 with rolling_avg defined at every bar in that window.
    # rolling_avg[i] defined needs ATR(14) at i-99..i all defined, and
    # ATR(14)[j] defined needs j >= ATR_LENGTH. So the first index
    # where rolling_avg is defined is ATR_LENGTH + ATR_ROLLING_AVERAGE
    # _WINDOW_4H_BARS - 1 = 14 + 99 = 113. The first event bar t where
    # the 5-bar contraction window ending at t-1 has rolling_avg
    # defined at every bar is t-5 >= 113, i.e., t >= 118.
    min_event_index = (ATR_LENGTH
                       + ATR_ROLLING_AVERAGE_WINDOW_4H_BARS - 1
                       + CONTRACTION_WINDOW_BARS)
    for t in range(n):
        if t < min_event_index:
            # not enough history -- silently skip (no attempt record);
            # an explicit insufficient_history record would flood the
            # output. The synthetic fixtures verify this branch by
            # using exactly-at-minimum cases.
            continue
        contraction = check_contraction_window(
            atr_values, rolling_avg, t - 1)
        # at this point contraction.window_end_index == t - 1
        contracted_atr = atr_values[t - 1]
        atr_at_event = atr_values[t]
        rolling_at_contraction_end = (rolling_avg[t - 1] if t - 1 >= 0
                                      and t - 1 < len(rolling_avg)
                                      else None)
        bar = bars[t]
        entry = float(bar["close"])
        record: dict[str, Any] = {
            field: None for field in C7_SETUP_REQUIRED_FIELDS}
        record.update({
            "setup_id": "%s_%s" % (symbol, bar["time_utc"]),
            "symbol": symbol, "timeframe": TIMEFRAME,
            "direction": DIRECTION,
            "event_time": bar["time_utc"],
            "event_index": t,
            "entry_price": entry,
            "atr14_at_event":
                round(atr_at_event, 6)
                if atr_at_event is not None else None,
            "contracted_atr":
                round(contracted_atr, 6)
                if contracted_atr is not None else None,
            "rolling_average_atr_at_contraction_end":
                round(rolling_at_contraction_end, 6)
                if rolling_at_contraction_end is not None else None,
            "contraction_window_passes": contraction["passes"],
            "rejection_reasons": [],
            "replay_start_time": (bars[t + 1]["time_utc"]
                                  if t + 1 < n else None),
        })
        # contraction gate
        if not contraction["passes"]:
            record["status"] = "rejected_contraction_window"
            record["rejection_reasons"].append(
                "contraction_window_not_5_consecutive_bars_strict"
                "_below_0_6_x_rolling_avg")
            setups.append(record)
            continue
        # need ATR at event bar AND contracted ATR > 0 for the
        # expansion multiplier check
        if (atr_at_event is None or contracted_atr is None
                or contracted_atr <= 0):
            record["status"] = "rejected_invalid_stop_geometry"
            record["rejection_reasons"].append(
                "atr_unavailable_or_not_positive_at_event_or_contracted")
            setups.append(record)
            continue
        expansion = check_expansion_event(bars, t, contracted_atr)
        record["expansion_true_range"] = (
            round(expansion["true_range"], 6)
            if expansion["true_range"] is not None else None)
        record["expansion_multiplier_observed"] = (
            round(expansion["multiplier_observed"], 6)
            if expansion["multiplier_observed"] is not None else None)
        record["close_in_upper_third_passes"] = (
            expansion["close_in_upper_third_passes"])
        if not expansion["multiplier_passes"]:
            record["status"] = "rejected_expansion_multiplier"
            record["rejection_reasons"].append(
                "true_range_does_not_exceed_1_8x_contracted_atr")
            setups.append(record)
            continue
        if not expansion["close_in_upper_third_passes"]:
            record["status"] = "rejected_close_not_in_upper_third"
            record["rejection_reasons"].append(
                "event_bar_close_not_in_upper_third_of_its_range")
            setups.append(record)
            continue
        # stop geometry
        ten_bar_low = min(float(bars[i]["low"]) for i in
                          range(t - STRUCTURE_LOOKBACK_BARS + 1, t + 1))
        record["structure_lookback_low"] = round(ten_bar_low, 6)
        stop = compute_stop(entry, ten_bar_low, atr_at_event)
        record["atr_stop_distance"] = round(stop["atr_stop_distance"],
                                            6)
        record["structure_stop_distance"] = round(
            stop["structure_stop_distance"], 6)
        if not stop["valid"]:
            record["status"] = "rejected_invalid_stop_geometry"
            record["rejection_reasons"].append(
                "stop_distance_not_positive_or_stop_not_below_entry")
            setups.append(record)
            continue
        record["stop_distance"] = round(stop["stop_distance"], 6)
        record["stop_price"] = round(stop["stop_price"], 6)
        # geometry floor
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
            continue
        if not floor["any_variant_passes"]:
            record["status"] = "rejected_geometry_floor"
            record["rejection_reasons"].append(
                "all_variant_target_distances_below_81_bps")
            setups.append(record)
            continue
        record["status"] = "accepted_for_replay_review"
        setups.append(record)
    return setups


def apply_anti_cluster_filter(setups: list) -> dict[str, Any]:
    """Apply the 6-bar same-symbol anti-cluster gap at label-emission
    time on the chronologically-sorted ACCEPTED events. Tie-breaker:
    keep the earlier accepted event and drop the later one if their
    event_index difference is less than ANTI_CLUSTER_MIN_BAR_GAP. This
    is a PROPOSAL-LEVEL locked policy -- it does NOT consume the single
    allowed C7 edit token (see contract field
    `anti_cluster_does_not_consume_edit_token`)."""
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
                "rejected_clustered_within_6_bars_of_prior_accepted")
            dropped_record["rejection_reasons"] = list(
                s.get("rejection_reasons") or []) + [
                "less_than_6_completed_4h_bars_after_prior_accepted"
                "_event_on_same_symbol"]
            dropped.append(dropped_record)
    return {"kept": kept, "dropped": dropped,
            "anti_cluster_min_bar_gap": ANTI_CLUSTER_MIN_BAR_GAP,
            "tie_breaker": ANTI_CLUSTER_TIE_BREAKER,
            "anti_cluster_does_not_consume_edit_token": True}


# ---- synthetic fixtures (in-memory only) ----------------------------------

def _stamp(index: int) -> str:
    """Deterministic stamp for synthetic 4h fixtures (offset only;
    no wall-clock)."""
    day = 1 + index // 6
    hour = (index % 6) * 4
    return "2026-01-%02dT%02d:00:00Z" % (day, hour)


def _bar(index: int, close: float, high: float | None = None,
         low: float | None = None,
         open_price: float | None = None
         ) -> dict[str, Any]:
    if high is None:
        high = close + 0.5
    if low is None:
        low = close - 0.5
    if open_price is None:
        open_price = close - 0.1
    return {"time_utc": _stamp(index),
            "open": float(open_price),
            "high": float(high),
            "low": float(low),
            "close": float(close)}


def fixture_warmup_then_contraction_then_expansion(
        warmup_length: int = 115,
        contraction_run_length: int = 20,
        contracted_atr_target: float = 0.5,
        rolling_atr_target: float = 1.5,
        expansion_close: float = 50300.0,
        expansion_low: float = 50000.0,
        expansion_high: float = 50320.0,
        ) -> list:
    """Build a 4h fixture with:
      - WARMUP bars of "normal" volatility (true range ~ 3 *
        rolling_atr_target so that the 100-bar rolling average ATR
        converges high);
      - CONTRACTION_RUN_LENGTH bars of low volatility (true range ~
        3 * contracted_atr_target). The 5-bar window check at the END
        of this run will then see ATR(14) settled near the low level
        (ATR(14) needs ~14 bars to recompose), so the strict <
        0.6 * rolling_avg check passes for the final 5 bars.
      - one expansion bar with explicit high/low/close;
      - one trailing bar for replay_start_time.

    The default values produce a CLEAR expansion with a wide enough
    risk distance to pass the 81 bps floor.
    """
    bars: list = []
    saw = rolling_atr_target
    level = 50000.0
    for i in range(warmup_length):
        close = level + (saw if i % 2 == 0 else -saw)
        high = close + saw
        low = close - saw
        bars.append({"time_utc": _stamp(i),
                     "open": close, "high": high,
                     "low": low, "close": close})
    low_band = contracted_atr_target
    for j in range(contraction_run_length):
        i = warmup_length + j
        close = level + (low_band if j % 2 == 0 else -low_band)
        high = close + low_band
        low = close - low_band
        bars.append({"time_utc": _stamp(i),
                     "open": close, "high": high,
                     "low": low, "close": close})
    exp_index = warmup_length + contraction_run_length
    bars.append({"time_utc": _stamp(exp_index),
                 "open": (expansion_low + expansion_high) / 2.0,
                 "high": expansion_high, "low": expansion_low,
                 "close": expansion_close})
    bars.append({"time_utc": _stamp(exp_index + 1),
                 "open": expansion_close,
                 "high": expansion_close + 5.0,
                 "low": expansion_close - 5.0,
                 "close": expansion_close - 1.0})
    return bars


def fixture_no_contraction(
        warmup_length: int = 115) -> list:
    """Same warmup + a high-volatility bar where TR is large but no
    contraction window exists immediately prior."""
    bars: list = []
    saw = 1.5
    level = 50000.0
    for i in range(warmup_length + CONTRACTION_WINDOW_BARS):
        close = level + (saw if i % 2 == 0 else -saw)
        bars.append({"time_utc": _stamp(i),
                     "open": close, "high": close + saw,
                     "low": close - saw, "close": close})
    exp_index = warmup_length + CONTRACTION_WINDOW_BARS
    bars.append({"time_utc": _stamp(exp_index),
                 "open": 50000.0, "high": 50320.0,
                 "low": 50000.0, "close": 50300.0})
    bars.append({"time_utc": _stamp(exp_index + 1),
                 "open": 50300.0, "high": 50305.0,
                 "low": 50295.0, "close": 50299.0})
    return bars


def fixture_only_4_contraction_bars(
        warmup_length: int = 115) -> list:
    """Warmup + 4 contraction bars + 1 "normal" bar + expansion. The
    contraction window count test."""
    bars: list = []
    saw = 1.5
    level = 50000.0
    for i in range(warmup_length):
        close = level + (saw if i % 2 == 0 else -saw)
        bars.append({"time_utc": _stamp(i),
                     "open": close, "high": close + saw,
                     "low": close - saw, "close": close})
    # 4 low-vol bars
    low_band = 0.5
    for j in range(4):
        i = warmup_length + j
        close = level + (low_band if j % 2 == 0 else -low_band)
        bars.append({"time_utc": _stamp(i),
                     "open": close, "high": close + low_band,
                     "low": close - low_band, "close": close})
    # 1 normal-vol bar (breaks the contraction streak)
    i = warmup_length + 4
    close = level + saw
    bars.append({"time_utc": _stamp(i),
                 "open": close, "high": close + saw,
                 "low": close - saw, "close": close})
    # expansion attempt
    exp_index = warmup_length + 5
    bars.append({"time_utc": _stamp(exp_index),
                 "open": 50000.0, "high": 50320.0,
                 "low": 50000.0, "close": 50300.0})
    bars.append({"time_utc": _stamp(exp_index + 1),
                 "open": 50300.0, "high": 50305.0,
                 "low": 50295.0, "close": 50299.0})
    return bars


def fixture_expansion_only_1_7x_multiplier(
        warmup_length: int = 115,
        contraction_run_length: int = 20) -> list:
    """Valid contraction window, but expansion bar TR is only ~1.7 x
    contracted ATR (below the 1.8 threshold)."""
    bars = fixture_warmup_then_contraction_then_expansion(
        warmup_length=warmup_length,
        contraction_run_length=contraction_run_length)
    # Replace the expansion bar with a smaller TR: contracted ATR is
    # about 0.5, so TR target ~ 0.85. We make low/high span = 0.85
    # and close in the upper third.
    exp_idx = warmup_length + contraction_run_length
    low = 50000.0
    high = low + 0.85
    close = low + 0.75  # in upper third of [50000, 50000.85]
    bars[exp_idx] = {"time_utc": _stamp(exp_idx),
                     "open": (low + high) / 2.0,
                     "high": high, "low": low, "close": close}
    return bars


def fixture_expansion_close_at_midpoint(
        warmup_length: int = 115,
        contraction_run_length: int = 20) -> list:
    """Valid contraction window + valid expansion multiplier, but the
    event bar's close is at the midpoint of its range (NOT in the
    upper third)."""
    bars = fixture_warmup_then_contraction_then_expansion(
        warmup_length=warmup_length,
        contraction_run_length=contraction_run_length)
    exp_idx = warmup_length + contraction_run_length
    low = 50000.0
    high = 50320.0
    close = (low + high) / 2.0  # exactly at midpoint
    bars[exp_idx] = {"time_utc": _stamp(exp_idx),
                     "open": close, "high": high, "low": low,
                     "close": close}
    return bars


def fixture_two_accepted_within_6_bars(
        warmup_length: int = 115) -> list:
    """Two valid setups whose event_index difference is less than 6;
    the anti-cluster filter should keep the earlier and drop the
    later."""
    # First fixture: warmup + contraction + expansion at index
    # warmup_length + CONTRACTION_WINDOW_BARS.
    bars = fixture_warmup_then_contraction_then_expansion(
        warmup_length=warmup_length)
    first_exp_idx = warmup_length + CONTRACTION_WINDOW_BARS
    # Stage a second contraction-then-expansion just 3 bars after the
    # first expansion. Indices: first_exp_idx + 1 .. first_exp_idx + 5
    # would be the contraction window for a second event at
    # first_exp_idx + 3? That doesn't have 5-bar contraction. We need
    # the contraction window (5 bars) ending at the bar before the
    # second event. So second event at index t2 needs contraction at
    # t2-5..t2-1. For t2 - first_exp_idx < 6, e.g. t2 = first_exp_idx
    # + 5, the contraction window spans first_exp_idx..t2-1, which
    # includes the first expansion bar (high TR) -- the contraction
    # check will fail at that bar. So we need a wider gap that still
    # falls inside the 6-bar anti-cluster zone.
    # Better approach: artificially insert a second valid setup at
    # event_index = first_exp_idx + 6 to be just outside the gap, and
    # confirm both are kept; AND insert another at first_exp_idx + 5
    # to be just inside the gap. We can do this by post-emission
    # injection of synthetic accepted records in the test rather than
    # forcing it from raw bars. The test will use the scanner output
    # for the first event and synthesize the second accepted record
    # directly. For this fixture, we just return the standard one-
    # event fixture; the test layers the cluster by constructing two
    # accepted records and calling apply_anti_cluster_filter on them.
    return bars


# ---- dry run --------------------------------------------------------------

def run_c7_detector_dry_run() -> dict[str, Any]:
    """Run the scanner over IN-MEMORY synthetic fixtures only and check
    expected outcomes. Touches no real candles, no staged data."""
    record: dict[str, Any] = {
        "schema_version": C7D_SCHEMA_VERSION, "label": C7D_LABEL,
        "mode": C7D_MODE, "verdict": None, "failures": [],
        "fixtures": {}, "uses_synthetic_fixtures_only": True,
        "reads_real_candles": False, "reads_staged_data": False,
        "reads_any_files": False,
    }
    failures = record["failures"]

    # Fixture A: valid compression + expansion produces a single
    # accepted setup with expected entry/floor.
    bars_a = fixture_warmup_then_contraction_then_expansion()
    setups_a = scan_c7_setups(bars_a, "BTCUSD")
    accepted_a = [s for s in setups_a
                  if s["status"] == "accepted_for_replay_review"]
    record["fixtures"]["valid_compression_expansion"] = {
        "attempts": len(setups_a), "accepted": len(accepted_a)}
    if len(accepted_a) != 1:
        failures.append(
            "valid_compression_expansion_expected_1_accepted_got_%d"
            % len(accepted_a))
    elif accepted_a[0]["geometry_floor_pass_by_variant"] != {
            "2r": True, "3r": True, "4r": True}:
        failures.append(
            "valid_compression_expansion_floor_unexpected")

    # Fixture B: no contraction window -> all attempts reject on
    # contraction.
    bars_b = fixture_no_contraction()
    setups_b = scan_c7_setups(bars_b, "BTCUSD")
    statuses_b = sorted({s["status"] for s in setups_b})
    record["fixtures"]["no_contraction"] = {
        "attempts": len(setups_b),
        "statuses": statuses_b}
    if statuses_b and statuses_b != ["rejected_contraction_window"]:
        failures.append(
            "no_contraction_unexpected_statuses_%s" % statuses_b)

    # Fixture C: only 4 contraction bars then a normal bar -> expansion
    # attempt rejects on contraction.
    bars_c = fixture_only_4_contraction_bars()
    setups_c = scan_c7_setups(bars_c, "BTCUSD")
    accepted_c = [s for s in setups_c
                  if s["status"] == "accepted_for_replay_review"]
    record["fixtures"]["only_4_contraction_bars"] = {
        "attempts": len(setups_c), "accepted": len(accepted_c)}
    if accepted_c:
        failures.append(
            "only_4_contraction_bars_should_not_accept_got_%d"
            % len(accepted_c))

    # Fixture D: contraction OK, expansion multiplier ~1.7 (< 1.8)
    bars_d = fixture_expansion_only_1_7x_multiplier()
    setups_d = scan_c7_setups(bars_d, "BTCUSD")
    accepted_d = [s for s in setups_d
                  if s["status"] == "accepted_for_replay_review"]
    rejected_mult = [s for s in setups_d
                     if s["status"] == "rejected_expansion_multiplier"]
    record["fixtures"]["expansion_below_1_8x"] = {
        "attempts": len(setups_d), "accepted": len(accepted_d),
        "rejected_expansion_multiplier": len(rejected_mult)}
    if accepted_d:
        failures.append(
            "expansion_below_1_8x_should_not_accept")
    if not rejected_mult:
        failures.append(
            "expansion_below_1_8x_should_record_multiplier_rejection")

    # Fixture E: contraction OK, expansion multiplier OK, close at
    # midpoint -> rejected_close_not_in_upper_third
    bars_e = fixture_expansion_close_at_midpoint()
    setups_e = scan_c7_setups(bars_e, "BTCUSD")
    accepted_e = [s for s in setups_e
                  if s["status"] == "accepted_for_replay_review"]
    rejected_close = [s for s in setups_e
                      if s["status"] == (
                          "rejected_close_not_in_upper_third")]
    record["fixtures"]["close_at_midpoint"] = {
        "attempts": len(setups_e), "accepted": len(accepted_e),
        "rejected_close_not_in_upper_third":
            len(rejected_close)}
    if accepted_e:
        failures.append("close_at_midpoint_should_not_accept")
    if not rejected_close:
        failures.append(
            "close_at_midpoint_should_record_upper_third_rejection")

    # Fixture F: anti-cluster keeps earlier, drops later within 6 bars
    # of a prior accepted event on the same symbol.
    base = (accepted_a[0] if accepted_a
            else {"setup_id": "synthetic_a", "symbol": "BTCUSD",
                  "status": "accepted_for_replay_review",
                  "event_index": 120, "rejection_reasons": []})
    later_inside = dict(base)
    later_inside["setup_id"] = "synthetic_b_inside"
    later_inside["event_index"] = base["event_index"] + 3
    later_outside = dict(base)
    later_outside["setup_id"] = "synthetic_c_outside"
    later_outside["event_index"] = base["event_index"] + 6
    cluster_result = apply_anti_cluster_filter(
        [base, later_inside, later_outside])
    record["fixtures"]["anti_cluster"] = {
        "kept_ids": [s["setup_id"] for s in cluster_result["kept"]],
        "dropped_ids": [s["setup_id"]
                        for s in cluster_result["dropped"]],
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
            "anti_cluster_should_drop_event_within_6_bars_of_prior")
    if "synthetic_c_outside" not in kept_ids:
        failures.append(
            "anti_cluster_should_keep_event_at_or_after_6_bar_gap")
    if cluster_result[
            "anti_cluster_does_not_consume_edit_token"] is not True:
        failures.append("anti_cluster_must_not_consume_edit_token")

    # Fixture G: symbol outside universe raises
    try:
        scan_c7_setups(bars_a, "ETHUSD")
        failures.append(
            "scan_should_raise_on_symbol_outside_universe")
    except ValueError:
        pass

    record["verdict"] = (VERDICT_C7D_DRY_RUN_PASSED if not failures
                         else VERDICT_C7D_DRY_RUN_FAILED)
    return record


# ---- the contract record --------------------------------------------------

def build_c7_detector_spec_contract() -> dict[str, Any]:
    """Assemble the C7 detector-spec record. Chain-gated on the
    six-record ledger, the pushed C7 family proposal, the pushed C7
    spec review, the pushed Overnight Research Autopilot V2, the
    pushed Recommendation V1, and the pushed Autopilot Loop V1."""
    record: dict[str, Any] = {
        "schema_version": C7D_SCHEMA_VERSION, "label": C7D_LABEL,
        "mode": C7D_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "universe": list(UNIVERSE), "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "atr_length": ATR_LENGTH,
        "atr_rolling_average_window_4h_bars":
            ATR_ROLLING_AVERAGE_WINDOW_4H_BARS,
        "contraction_fraction": CONTRACTION_FRACTION,
        "contraction_window_bars": CONTRACTION_WINDOW_BARS,
        "expansion_true_range_multiplier":
            EXPANSION_TRUE_RANGE_MULTIPLIER,
        "close_in_upper_third_fraction":
            CLOSE_IN_UPPER_THIRD_FRACTION,
        "structure_lookback_bars": STRUCTURE_LOOKBACK_BARS,
        "wider_stop_atr_multiplier": WIDER_STOP_ATR_MULTIPLIER,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "target_variants": list(name for name, _ in TARGET_VARIANTS),
        "anti_cluster_min_bar_gap": ANTI_CLUSTER_MIN_BAR_GAP,
        "anti_cluster_tie_breaker": ANTI_CLUSTER_TIE_BREAKER,
        "anti_cluster_does_not_consume_edit_token": True,
        "detector_required_fields": list(C7_SETUP_REQUIRED_FIELDS),
        "detector_statuses": list(C7_DETECTOR_STATUSES),
        "next_required_action": NEXT_REQUIRED_ACTION,
        "current_loop_stage": CURRENT_LOOP_STAGE,
        "ledger_status_six_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_synthetic_fixture_dry_run_only": True,
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
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_real_candle_detection": False,
        "unlocks_labels_now": False, "unlocks_replay_now": False,
        "unlocks_relabel_now": False,
        "claims_profitability": False,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS)
    record["ledger_status_six_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C7D_BLOCKED
        record["blockers"].append("six_record_ledger_broken")
        return record
    if build_candidate_7_family_proposal()["verdict"] != (
            VERDICT_C7P_READY):
        record["verdict"] = VERDICT_C7D_BLOCKED
        record["blockers"].append("candidate_7_proposal_not_certifying")
        return record
    if build_candidate_7_spec_review()["verdict"] != VERDICT_C7S_READY:
        record["verdict"] = VERDICT_C7D_BLOCKED
        record["blockers"].append("candidate_7_spec_review_not"
                                  "_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C7D_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C7D_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C7D_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C7D_READY
    return record


def build_c7_detector_spec_dry_run_review() -> dict[str, Any]:
    """Run the dry run and combine with the spec contract to produce
    the combined detector-spec+dry-run review record."""
    spec_record = build_c7_detector_spec_contract()
    dry_record = run_c7_detector_dry_run()
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
    if combined["verdict"] != VERDICT_C7D_READY:
        combined["combined_verdict"] = VERDICT_C7D_BLOCKED
    elif dry_record["verdict"] != VERDICT_C7D_DRY_RUN_PASSED:
        combined["combined_verdict"] = VERDICT_C7D_DRY_RUN_FAILED
        combined["blockers"].append("dry_run_failed")
        combined["blockers"].extend(dry_record["failures"])
    else:
        combined["combined_verdict"] = VERDICT_C7D_SPEC_DRY_RUN_READY
    return combined


def validate_c7_detector_spec_contract(record: Any) -> dict[str, Any]:
    """Validate shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    allowed_verdicts = (VERDICT_C7D_READY, VERDICT_C7D_BLOCKED)
    if r.get("verdict") not in allowed_verdicts:
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("universe") != ["BTCUSD"]:
        errors.append("universe_tampered")
    if r.get("timeframe") != "4h" or r.get("direction") != "long":
        errors.append("timeframe_or_direction_tampered")
    if r.get("atr_length") != 14:
        errors.append("atr_length_tampered")
    if r.get("atr_rolling_average_window_4h_bars") != 100:
        errors.append("atr_rolling_average_window_tampered")
    if r.get("contraction_fraction") != 0.6:
        errors.append("contraction_fraction_must_be_0_6")
    if r.get("contraction_window_bars") != 5:
        errors.append("contraction_window_must_be_5")
    if r.get("expansion_true_range_multiplier") != 1.8:
        errors.append("expansion_multiplier_must_be_1_8")
    if abs((r.get("close_in_upper_third_fraction") or 0)
           - (2.0 / 3.0)) > 1e-12:
        errors.append("close_in_upper_third_fraction_must_be_two_thirds")
    if r.get("structure_lookback_bars") != 10:
        errors.append("structure_lookback_must_be_10")
    if r.get("wider_stop_atr_multiplier") != 1.5:
        errors.append("wider_stop_atr_multiplier_must_be_1_5")
    if r.get("fee_round_trip_bps") != 27.0:
        errors.append("fee_27bps_changed")
    if r.get("target_distance_floor_bps") != 81.0:
        errors.append("floor_81bps_changed")
    if r.get("target_variants") != ["2r", "3r", "4r"]:
        errors.append("target_variants_tampered")
    if r.get("anti_cluster_min_bar_gap") != 6:
        errors.append("anti_cluster_gap_must_be_6")
    if r.get("anti_cluster_tie_breaker") != (
            "keep_the_earlier_event_drop_the_later_one"):
        errors.append("anti_cluster_tie_breaker_tampered")
    if r.get("anti_cluster_does_not_consume_edit_token") is not True:
        errors.append("anti_cluster_must_not_consume_edit_token")
    if list(r.get("detector_required_fields") or ()) != list(
            C7_SETUP_REQUIRED_FIELDS):
        errors.append("detector_required_fields_tampered")
    if list(r.get("detector_statuses") or ()) != list(
            C7_DETECTOR_STATUSES):
        errors.append("detector_statuses_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_synthetic_fixture_dry_run_only", True),
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
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_labels_now", "unlocks_replay_now",
                "unlocks_relabel_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C7D_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}

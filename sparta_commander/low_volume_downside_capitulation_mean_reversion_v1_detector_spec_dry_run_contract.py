"""SPARTA CANDIDATE #9 DETECTOR SPEC + SYNTHETIC DRY-RUN PATH
(READ-ONLY, RESEARCH ONLY):
LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1.

Loop stage: detector_and_label_review. Pure deterministic scanner
implementing the pushed Candidate #9 frozen spec EXACTLY:

  - universe BTCUSD only, timeframe 15m, direction long-only;
  - rolling stats window: 96 completed 15m bars STRICTLY BEFORE the
    trigger bar (the trigger bar's own values are NEVER included in
    the rolling stats -- no same-bar lookahead);
  - log return: log(close[i] / close[i-1]) for completed 15m bar i;
  - rolling mean + sample std (n-1) of those 96 prior log returns;
  - downside z-score trigger: strict log_return < mean -
    DOWNSIDE_Z_SCORE_THRESHOLD_ABS x std (with
    DOWNSIDE_Z_SCORE_THRESHOLD_ABS = 2.0, threshold = mean - 2.0 *
    std);
  - below-median volume trigger: strict volume < median(volumes over
    the same 96-bar window);
  - JOINT trigger: BOTH conditions must hold on the SAME completed
    trigger bar; neither alone is a trigger;
  - entry: at the CLOSE of the NEXT completed 15m bar after the
    trigger bar (the post-panic confirmation bar); no intrabar
    entry; no same-bar entry;
  - entry-bar invalidation: if the entry bar's close <= the trigger
    bar's low, the setup is rejected on
    `rejected_entry_bar_close_at_or_below_trigger_bar_low` (price
    continued through the panic level, so the order-book asymmetry
    thesis is falsified by that bar);
  - ATR(14) at the trigger bar (simple-mean true range; uses the
    C3-shared compute_atr14 primitive);
  - structure stop: stop_price = trigger_bar_low -
    STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER (0.20) x ATR(14) at the
    trigger bar; stop_distance = entry_price - stop_price; INVALID
    if stop_distance is not positive OR stop is not below entry OR
    stop is not below trigger_bar_low;
  - target variants 2r / 3r / 4r; target_price = entry_price +
    r_multiple x stop_distance;
  - 27 bps round-trip fees + 81 bps gross-target-distance floor per
    variant checked at label time before replay eligibility;
  - 8-bar anti-cluster gap per symbol at label-emission time AFTER
    the scanner emits accepted setups and BEFORE replay-time non-
    overlap; tie-breaker keeps the earlier accepted event and drops
    the later same-symbol event whose entry_index is within 8
    completed 15m bars of the prior kept event. PROPOSAL-LEVEL
    locked, NOT the single C9 edit token;
  - sample-size adequacy: a MINIMUM of 20 accepted setups required
    at the labels-review gate; the dry-run records the count for
    informational propagation only; the threshold is enforced
    structurally at labels-review, not here. PROPOSAL-LEVEL locked,
    NOT the single C9 edit token;
  - explicit edge argument beyond pattern geometry: carried forward
    declaratively. PROPOSAL-LEVEL locked, NOT the single C9 edit
    token.

PURITY LAW: inputs are in-memory candle rows supplied by callers /
tests. No file reads, no real candles, no staged data, no
aggregation execution, no network, fully deterministic, no wall-
clock behavior, no module-level runner, no order / account /
trading capability. The dry run uses ONLY in-memory synthetic
fixtures -- no real candle is touched until the separately human-
approved real-candle gate.

Chain-gated live on: the eight-record rejection ledger (C1-C8), the
pushed C9 family proposal, the pushed C9 spec review, the pushed V4
rejected-family blacklist, the pushed V3 blacklist, the pushed
Overnight Research Autopilot V2, the pushed Recommendation V1, and
the pushed Autopilot Loop V1.
"""

from __future__ import annotations

import math
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
from sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C8_STATUS,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C9P_READY,
    build_candidate_9_family_proposal,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_spec_review_contract import (
    VERDICT_C9S_READY,
    build_candidate_9_spec_review,
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
from sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract import (
    VERDICT_BL4_READY,
    build_rejected_family_blacklist_v4,
)
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C9D_SCHEMA_VERSION = (
    "low_volume_downside_capitulation_mean_reversion_v1_detector"
    "_spec_dry_run.v1")
C9D_LABEL = ("SPARTA Candidate #9 Detector Spec + Dry-Run Path "
             "(READ-ONLY, RESEARCH ONLY, PURE FUNCTIONS, SYNTHETIC "
             "FIXTURES ONLY, NOT A RESCUE, NOT A CLAIM)")
C9D_MODE = "RESEARCH_ONLY"
VERDICT_C9D_READY = "CANDIDATE_9_DETECTOR_SPEC_READY"
VERDICT_C9D_BLOCKED = "CANDIDATE_9_DETECTOR_SPEC_BLOCKED"
VERDICT_C9D_DRY_RUN_PASSED = "CANDIDATE_9_DETECTOR_DRY_RUN_PASSED"
VERDICT_C9D_DRY_RUN_FAILED = "CANDIDATE_9_DETECTOR_DRY_RUN_FAILED"
VERDICT_C9D_SPEC_DRY_RUN_READY = (
    "CANDIDATE_9_DETECTOR_SPEC_DRY_RUN_READY")
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_9_DRY_RUN_REVIEW"
CURRENT_LOOP_STAGE = "detector_and_label_review"

# ---- frozen numerics (mirror pushed spec review exactly) -----------------
UNIVERSE = ("BTCUSD",)
TIMEFRAME = "15m"
DIRECTION = "long_only"
ROLLING_WINDOW_BARS = 96
ATR_LENGTH = 14
DOWNSIDE_Z_SCORE_THRESHOLD_ABS = 2.0
VOLUME_PERCENTILE_THRESHOLD = 50.0
STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER = 0.20
TIMEOUT_BARS = 96
FEE_ROUND_TRIP_BPS = 27.0
TARGET_DISTANCE_FLOOR_BPS = 81.0
TARGET_VARIANTS = (("2r", 2.0), ("3r", 3.0), ("4r", 4.0))
ANTI_CLUSTER_MIN_BAR_GAP = 8
ANTI_CLUSTER_TIE_BREAKER = "keep_the_earlier_event_drop_the_later_one"
SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED = 20

C9_SETUP_REQUIRED_FIELDS = (
    "setup_id", "symbol", "timeframe", "direction",
    "trigger_index", "trigger_time", "trigger_close",
    "trigger_low", "trigger_high",
    "trigger_volume",
    "rolling_window_bars",
    "rolling_mean_log_return", "rolling_std_log_return",
    "rolling_median_volume",
    "trigger_log_return",
    "downside_z_threshold_value", "z_condition_passes",
    "volume_condition_passes", "joint_trigger_passes",
    "atr_at_trigger_bar",
    "entry_index", "entry_time", "entry_price",
    "entry_bar_close_strictly_above_trigger_low",
    "stop_buffer_price", "stop_price", "stop_distance",
    "stop_below_entry", "stop_below_trigger_low",
    "target_2r", "target_3r", "target_4r",
    "target_distance_bps_2r", "target_distance_bps_3r",
    "target_distance_bps_4r",
    "geometry_floor_pass_by_variant",
    "accepted_for_labeling_by_variant",
    "replay_start_time", "status", "rejection_reasons",
)

C9_DETECTOR_STATUSES = (
    "accepted_for_replay_review",
    "rejected_entry_bar_close_at_or_below_trigger_bar_low",
    "rejected_invalid_stop_geometry",
    "rejected_geometry_floor",
    "rejected_no_evaluation_bar",
    "rejected_clustered_within_8_bars_of_prior_accepted",
)


def get_candidate_9_detector_label() -> str:
    return C9D_LABEL


def validate_detection_context(symbol: str, timeframe: str,
                               direction: str) -> None:
    """Raise ValueError on any context outside the frozen BTCUSD /
    15m / long_only universe. Pure."""
    if symbol not in UNIVERSE:
        raise ValueError(
            "symbol_outside_candidate_9_universe:" + str(symbol))
    if timeframe != TIMEFRAME:
        raise ValueError(
            "timeframe_outside_candidate_9_universe:" + str(timeframe))
    if direction != DIRECTION:
        raise ValueError(
            "direction_outside_candidate_9_universe:" + str(direction))


# ---- pure numeric primitives ----------------------------------------------

def _median_of(values: list) -> float:
    """Pure median of a non-empty list of floats. Raises ValueError
    on empty input."""
    if not values:
        raise ValueError("median_of_empty_list")
    s = sorted(values)
    n = len(s)
    if n % 2 == 1:
        return float(s[n // 2])
    return (float(s[n // 2 - 1]) + float(s[n // 2])) / 2.0


def compute_rolling_log_return_stats(bars: list, trigger_index: int,
                                     window: int = ROLLING_WINDOW_BARS
                                     ) -> dict[str, Any]:
    """Mean and sample-std (n-1) of log(close[i]/close[i-1]) for i in
    [trigger_index - window, trigger_index - 1] inclusive. The
    trigger bar's own values are NEVER included. Returns mean/std/
    count or all None if insufficient history. Pure."""
    out: dict[str, Any] = {
        "mean": None, "std": None, "count": 0,
        "rolling_window_bars": window,
        "uses_prior_bars_only_no_same_bar_lookahead": True,
    }
    if trigger_index < window + 1:
        return out
    if trigger_index > len(bars):
        return out
    log_returns: list = []
    for i in range(trigger_index - window, trigger_index):
        if i < 1:
            return out
        prev_close = float(bars[i - 1]["close"])
        if prev_close <= 0.0:
            return out
        curr_close = float(bars[i]["close"])
        if curr_close <= 0.0:
            return out
        log_returns.append(math.log(curr_close / prev_close))
    n = len(log_returns)
    if n < 2:
        return out
    mean_val = sum(log_returns) / n
    var_sum = sum((x - mean_val) ** 2 for x in log_returns)
    sample_var = var_sum / (n - 1)
    std_val = sample_var ** 0.5
    out["mean"] = mean_val
    out["std"] = std_val
    out["count"] = n
    return out


def compute_rolling_volume_median(bars: list, trigger_index: int,
                                  window: int = ROLLING_WINDOW_BARS
                                  ) -> float | None:
    """Median of volumes over the prior `window` completed 15m bars
    BEFORE trigger_index. The trigger bar's own volume is NEVER
    included. Pure."""
    if trigger_index < window:
        return None
    if trigger_index > len(bars):
        return None
    volumes = [float(bars[i]["volume"])
               for i in range(trigger_index - window, trigger_index)]
    if not volumes:
        return None
    return _median_of(volumes)


def compute_trigger_log_return(bars: list,
                               trigger_index: int) -> float | None:
    """log(close[trigger_index] / close[trigger_index - 1]). Pure.
    Returns None if either close is non-positive."""
    if trigger_index < 1 or trigger_index >= len(bars):
        return None
    prev = float(bars[trigger_index - 1]["close"])
    curr = float(bars[trigger_index]["close"])
    if prev <= 0.0 or curr <= 0.0:
        return None
    return math.log(curr / prev)


def check_joint_trigger(bars: list, t: int) -> dict[str, Any]:
    """Joint downside-z-score AND below-median-volume trigger on the
    SAME bar t. Returns a dict with the per-condition results and
    the joint flag. Pure."""
    out: dict[str, Any] = {
        "trigger_index": t, "trigger_log_return": None,
        "rolling_mean_log_return": None,
        "rolling_std_log_return": None,
        "rolling_median_volume": None,
        "downside_z_threshold_value": None,
        "z_condition_passes": False,
        "volume_condition_passes": False,
        "joint_trigger_passes": False,
    }
    if t < ROLLING_WINDOW_BARS + 1 or t >= len(bars):
        return out
    stats = compute_rolling_log_return_stats(bars, t)
    if stats["mean"] is None or stats["std"] is None:
        return out
    if stats["std"] <= 0.0:
        # zero-variance baseline: threshold = mean strictly, any
        # negative deviation triggers; equality does not.
        threshold = float(stats["mean"])
    else:
        threshold = (float(stats["mean"])
                     - DOWNSIDE_Z_SCORE_THRESHOLD_ABS
                     * float(stats["std"]))
    trigger_log_return = compute_trigger_log_return(bars, t)
    if trigger_log_return is None:
        return out
    median_volume = compute_rolling_volume_median(bars, t)
    if median_volume is None:
        return out
    trigger_volume = float(bars[t]["volume"])
    z_pass = trigger_log_return < threshold
    vol_pass = trigger_volume < median_volume
    out["trigger_log_return"] = trigger_log_return
    out["rolling_mean_log_return"] = stats["mean"]
    out["rolling_std_log_return"] = stats["std"]
    out["rolling_median_volume"] = median_volume
    out["downside_z_threshold_value"] = threshold
    out["z_condition_passes"] = z_pass
    out["volume_condition_passes"] = vol_pass
    out["joint_trigger_passes"] = z_pass and vol_pass
    return out


def compute_stop(entry_price: float, trigger_low: float,
                 atr_at_trigger: float) -> dict[str, Any]:
    """Structure stop: stop_price = trigger_low -
    STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER (0.20) * ATR(14) at trigger.
    Invalid if stop_distance is not positive OR stop is not below
    entry OR stop is not below trigger_low. Pure."""
    buffer = STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER * float(
        atr_at_trigger)
    stop_price = float(trigger_low) - buffer
    stop_distance = float(entry_price) - stop_price
    stop_below_entry = stop_price < float(entry_price)
    stop_below_trigger_low = stop_price < float(trigger_low)
    valid = (stop_distance > 0.0 and stop_below_entry
             and stop_below_trigger_low)
    return {"stop_buffer_price": buffer,
            "stop_price": stop_price,
            "stop_distance": stop_distance,
            "stop_below_entry": stop_below_entry,
            "stop_below_trigger_low": stop_below_trigger_low,
            "valid": valid}


def geometry_floor_by_variant(entry_price: float,
                              stop_distance: float) -> dict[str, Any]:
    """Per-variant 81 bps gross target-distance floor. 27 bps round-
    trip fees model; no maker rebate; no zero-fee. Pure."""
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


# ---- the deterministic scanner --------------------------------------------

def _precompute_atr(bars: list) -> list:
    """Pure. ATR(14) at every index via the shared compute_atr14
    primitive."""
    return [compute_atr14(bars, t) for t in range(len(bars))]


def _empty_setup_record() -> dict[str, Any]:
    return {field: None for field in C9_SETUP_REQUIRED_FIELDS}


def scan_c9_setups(bars: list, symbol: str = "BTCUSD",
                   timeframe: str = TIMEFRAME,
                   direction: str = DIRECTION
                   ) -> list[dict[str, Any]]:
    """Candidate #9 scanner. bars: in-memory list of 15m rows
    ({time_utc, open, high, low, close, volume}). Locked to BTCUSD /
    15m / long_only -- raises ValueError on any other context."""
    validate_detection_context(symbol, timeframe, direction)
    if not isinstance(bars, list):
        raise ValueError("bars_must_be_a_list")
    n = len(bars)
    atr_values = _precompute_atr(bars)
    setups: list[dict[str, Any]] = []
    last_trigger_index_emitted = -1
    for t in range(n):
        if t < ROLLING_WINDOW_BARS + 1:
            continue
        trigger = check_joint_trigger(bars, t)
        if not trigger["joint_trigger_passes"]:
            continue
        if t <= last_trigger_index_emitted:
            continue
        atr = atr_values[t]
        if atr is None:
            continue
        record = _empty_setup_record()
        trigger_bar = bars[t]
        record.update({
            "setup_id": "%s_%s" % (symbol, trigger_bar["time_utc"]),
            "symbol": symbol, "timeframe": TIMEFRAME,
            "direction": DIRECTION,
            "trigger_index": t,
            "trigger_time": trigger_bar["time_utc"],
            "trigger_close": round(float(trigger_bar["close"]), 6),
            "trigger_low": round(float(trigger_bar["low"]), 6),
            "trigger_high": round(float(trigger_bar["high"]), 6),
            "trigger_volume": round(float(trigger_bar["volume"]),
                                    6),
            "rolling_window_bars": ROLLING_WINDOW_BARS,
            "rolling_mean_log_return":
                round(float(trigger["rolling_mean_log_return"]), 9),
            "rolling_std_log_return":
                round(float(trigger["rolling_std_log_return"]), 9),
            "rolling_median_volume":
                round(float(trigger["rolling_median_volume"]), 6),
            "trigger_log_return":
                round(float(trigger["trigger_log_return"]), 9),
            "downside_z_threshold_value":
                round(float(trigger["downside_z_threshold_value"]),
                      9),
            "z_condition_passes": True,
            "volume_condition_passes": True,
            "joint_trigger_passes": True,
            "atr_at_trigger_bar": round(float(atr), 6),
            "rejection_reasons": [],
        })
        entry_index = t + 1
        if entry_index >= n:
            record["status"] = "rejected_no_evaluation_bar"
            record["rejection_reasons"].append(
                "no_next_bar_for_entry")
            setups.append(record)
            last_trigger_index_emitted = t
            continue
        entry_bar = bars[entry_index]
        entry_price = float(entry_bar["close"])
        trigger_low = float(trigger_bar["low"])
        entry_above_trigger_low = entry_price > trigger_low
        record.update({
            "entry_index": entry_index,
            "entry_time": entry_bar["time_utc"],
            "entry_price": entry_price,
            "entry_bar_close_strictly_above_trigger_low":
                entry_above_trigger_low,
            "replay_start_time":
                (bars[entry_index + 1]["time_utc"]
                 if entry_index + 1 < n else None),
        })
        if not entry_above_trigger_low:
            record["status"] = (
                "rejected_entry_bar_close_at_or_below_trigger_bar"
                "_low")
            record["rejection_reasons"].append(
                "entry_bar_close_at_or_below_trigger_bar_low_"
                "asymmetry_thesis_falsified")
            setups.append(record)
            last_trigger_index_emitted = t
            continue
        stop = compute_stop(entry_price, trigger_low, atr)
        record.update({
            "stop_buffer_price": round(stop["stop_buffer_price"], 6),
            "stop_price": round(stop["stop_price"], 6),
            "stop_distance": round(stop["stop_distance"], 6),
            "stop_below_entry": stop["stop_below_entry"],
            "stop_below_trigger_low": stop["stop_below_trigger_low"],
        })
        if not stop["valid"]:
            record["status"] = "rejected_invalid_stop_geometry"
            record["rejection_reasons"].append(
                "stop_distance_not_positive_or_stop_not_below_entry"
                "_or_not_below_trigger_low")
            setups.append(record)
            last_trigger_index_emitted = t
            continue
        floor = geometry_floor_by_variant(entry_price,
                                          stop["stop_distance"])
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
                "no_next_bar_for_evaluation_after_entry")
            setups.append(record)
            last_trigger_index_emitted = t
            continue
        if not floor["any_variant_passes"]:
            record["status"] = "rejected_geometry_floor"
            record["rejection_reasons"].append(
                "all_variant_target_distances_below_81_bps")
            setups.append(record)
            last_trigger_index_emitted = t
            continue
        record["status"] = "accepted_for_replay_review"
        setups.append(record)
        last_trigger_index_emitted = t
    return setups


def apply_anti_cluster_filter(setups: list) -> dict[str, Any]:
    """8-bar same-symbol anti-cluster gap at label-emission time on
    the chronologically-sorted ACCEPTED events. Tie-breaker: keep
    the earlier accepted event and drop the later one whose
    entry_index difference is strictly less than
    ANTI_CLUSTER_MIN_BAR_GAP. PROPOSAL-LEVEL locked, NOT the single
    C9 edit token."""
    accepted_chrono = sorted(
        (s for s in setups
         if s.get("status") == "accepted_for_replay_review"),
        key=lambda s: s["entry_index"])
    kept: list = []
    dropped: list = []
    last_kept_index = None
    for s in accepted_chrono:
        idx = s["entry_index"]
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
    """Sample-size adequacy gate. At dry-run stage this is an
    INFORMATIONAL count; the structural rejection is enforced at the
    labels-review gate. PROPOSAL-LEVEL locked, NOT the single C9
    edit token. Pure."""
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
         close: float, volume: float) -> dict[str, Any]:
    return {"time_utc": _stamp(index),
            "open": float(open_price),
            "high": float(high),
            "low": float(low),
            "close": float(close),
            "volume": float(volume)}


def _alternating_baseline_bar(index: int) -> dict[str, Any]:
    """Stable alternating-close 15m bar. Even index: close=50000.
    Odd index: close=50050. high = close + 5, low = close - 5,
    open = close, volume = 100. ATR(14) over a 14-bar alternating
    sequence is exactly 55."""
    if index % 2 == 0:
        return _bar(index, 50000.0, 50005.0, 49995.0, 50000.0, 100.0)
    return _bar(index, 50050.0, 50055.0, 50045.0, 50050.0, 100.0)


def _constant_baseline_bar(index: int) -> dict[str, Any]:
    """Constant-close 15m bar (close=50000, volume=100). Log return
    is exactly zero across the rolling window, so sample-std is
    zero and the downside z threshold collapses to mean = 0 with
    strict-below required."""
    return _bar(index, 50000.0, 50005.0, 49995.0, 50000.0, 100.0)


def fixture_happy_path_joint_trigger(
        baseline_length: int = 100) -> list:
    """100 alternating-close baseline + a deep-down trigger bar on
    LOW volume + an entry bar whose close is strictly above the
    trigger bar's low + a trailing bar for replay. Trigger at an
    even index so prev_close = 50050. Both joint conditions fire.
    The post-floor accepted setup has all variants passing 81 bps."""
    bars = [_alternating_baseline_bar(i)
            for i in range(baseline_length)]
    # trigger at index baseline_length (even): low 49000, close 49100
    bars.append(_bar(baseline_length, 50050.0, 50050.0, 49000.0,
                     49100.0, 50.0))
    # entry bar: close 49200 (> trigger_low 49000) so invalidation
    # does not fire
    bars.append(_bar(baseline_length + 1, 49100.0, 49250.0, 49050.0,
                     49200.0, 100.0))
    # trailing bar for replay_start_time
    bars.append(_bar(baseline_length + 2, 49200.0, 49250.0, 49150.0,
                     49200.0, 100.0))
    return bars


def fixture_insufficient_history(
        baseline_length: int = 50) -> list:
    """Only 50 alternating-close baseline bars + a deep-down trigger
    candidate + entry + trailing. Scanner cannot evaluate because
    the 96-bar rolling window is not satisfied -- 0 attempts."""
    bars = [_alternating_baseline_bar(i)
            for i in range(baseline_length)]
    bars.append(_bar(baseline_length, 50050.0, 50050.0, 49000.0,
                     49100.0, 50.0))
    bars.append(_bar(baseline_length + 1, 49100.0, 49250.0, 49050.0,
                     49200.0, 100.0))
    bars.append(_bar(baseline_length + 2, 49200.0, 49250.0, 49150.0,
                     49200.0, 100.0))
    return bars


def fixture_equality_at_z_threshold(
        baseline_length: int = 100) -> list:
    """100 constant-close baseline (close=50000 always) so rolling
    mean = 0 and rolling sample std = 0; threshold collapses to
    mean = 0; strict-below 0 requires return < 0. The trigger
    candidate at baseline_length has close = 50000 EXACTLY (log
    return = 0) on volume 50. The z condition fails on equality;
    the JOINT trigger does NOT fire -- 0 attempts."""
    bars = [_constant_baseline_bar(i)
            for i in range(baseline_length)]
    bars.append(_bar(baseline_length, 50000.0, 50005.0, 49995.0,
                     50000.0, 50.0))
    bars.append(_constant_baseline_bar(baseline_length + 1))
    bars.append(_constant_baseline_bar(baseline_length + 2))
    return bars


def fixture_equality_at_volume_median(
        baseline_length: int = 100) -> list:
    """100 constant-close + constant-volume (=100) baseline. Trigger
    candidate has a clearly negative log return (close 49900) so
    the z condition fires (strict-below 0), but its volume is
    EXACTLY 100 (= median). Strict-below median fails on equality;
    the JOINT trigger does NOT fire -- 0 attempts."""
    bars = [_constant_baseline_bar(i)
            for i in range(baseline_length)]
    bars.append(_bar(baseline_length, 50000.0, 50005.0, 49890.0,
                     49900.0, 100.0))
    bars.append(_constant_baseline_bar(baseline_length + 1))
    bars.append(_constant_baseline_bar(baseline_length + 2))
    return bars


def fixture_z_only_no_volume(
        baseline_length: int = 100) -> list:
    """100 alternating baseline + trigger candidate whose z fires
    (close 49100 from prev 50050) BUT whose volume is 200 (>
    median 100). The volume condition fails; JOINT does not fire."""
    bars = [_alternating_baseline_bar(i)
            for i in range(baseline_length)]
    bars.append(_bar(baseline_length, 50050.0, 50050.0, 49000.0,
                     49100.0, 200.0))
    bars.append(_alternating_baseline_bar(baseline_length + 1))
    bars.append(_alternating_baseline_bar(baseline_length + 2))
    return bars


def fixture_volume_only_no_z(
        baseline_length: int = 100) -> list:
    """100 alternating baseline + trigger candidate whose volume
    fires (50 < median 100) BUT whose log return is essentially
    flat (close 50050, log return ~ 0 from prev 50000). The z
    condition fails; JOINT does not fire."""
    bars = [_alternating_baseline_bar(i)
            for i in range(baseline_length)]
    # trigger at even index with prev_close=50050. Even bar close
    # would normally be 50000; we set it to 50045 (only a tiny
    # downward move) so log return ~ -0.0001, well above the -0.002
    # threshold.
    bars.append(_bar(baseline_length, 50050.0, 50055.0, 50045.0,
                     50045.0, 50.0))
    bars.append(_alternating_baseline_bar(baseline_length + 1))
    bars.append(_alternating_baseline_bar(baseline_length + 2))
    return bars


def fixture_entry_bar_invalidation(
        baseline_length: int = 100) -> list:
    """Joint trigger fires (deep down + low volume) but the entry
    bar's close (48900) is STRICTLY BELOW the trigger bar's low
    (49000); the entry-gate invalidation fires -- 1 attempt rejected
    on `rejected_entry_bar_close_at_or_below_trigger_bar_low`."""
    bars = [_alternating_baseline_bar(i)
            for i in range(baseline_length)]
    bars.append(_bar(baseline_length, 50050.0, 50050.0, 49000.0,
                     49100.0, 50.0))
    # entry bar close = 48900 (strictly below trigger_low 49000)
    bars.append(_bar(baseline_length + 1, 49100.0, 49100.0, 48800.0,
                     48900.0, 100.0))
    bars.append(_alternating_baseline_bar(baseline_length + 2))
    return bars


def fixture_geometry_floor_all_variants_fail(
        baseline_length: int = 100) -> list:
    """Joint trigger fires barely (close 49945 from prev 50050,
    return ~ -0.00210 < threshold -0.00201) + low volume. Trigger
    bar's low is 49940 (very narrow range). Entry bar's close is
    49942 (just above trigger_low). Stop distance is tiny; all 3
    variants fail the 81 bps floor."""
    bars = [_alternating_baseline_bar(i)
            for i in range(baseline_length)]
    # trigger at even index, prev_close=50050. close 49945 gives
    # log return = log(49945/50050) ~ -0.002101 < threshold.
    bars.append(_bar(baseline_length, 50050.0, 50055.0, 49940.0,
                     49945.0, 50.0))
    # entry bar close 49942 (just above trigger_low 49940)
    bars.append(_bar(baseline_length + 1, 49945.0, 49950.0, 49935.0,
                     49942.0, 100.0))
    bars.append(_alternating_baseline_bar(baseline_length + 2))
    return bars


def fixture_symbol_outside_universe(
        baseline_length: int = 100) -> list:
    """Bars are well-formed -- the universe rejection happens inside
    scan_c9_setups when symbol is not 'BTCUSD'."""
    return fixture_happy_path_joint_trigger(baseline_length)


# ---- dry run --------------------------------------------------------------

def run_c9_detector_dry_run() -> dict[str, Any]:
    """Run the scanner over IN-MEMORY synthetic fixtures only and
    check expected outcomes. Touches no real candles, no staged
    data."""
    record: dict[str, Any] = {
        "schema_version": C9D_SCHEMA_VERSION, "label": C9D_LABEL,
        "mode": C9D_MODE, "verdict": None, "failures": [],
        "fixtures": {}, "uses_synthetic_fixtures_only": True,
        "reads_real_candles": False, "reads_staged_data": False,
        "reads_any_files": False,
    }
    failures = record["failures"]

    # A: happy path -- 1 accepted, all 3 floor variants pass.
    bars_a = fixture_happy_path_joint_trigger()
    setups_a = scan_c9_setups(bars_a, "BTCUSD")
    accepted_a = [s for s in setups_a
                  if s["status"] == "accepted_for_replay_review"]
    record["fixtures"]["happy_path_joint_trigger"] = {
        "attempts": len(setups_a),
        "accepted": len(accepted_a),
        "first_accepted_floor_pass": (
            accepted_a[0]["geometry_floor_pass_by_variant"]
            if accepted_a else None)}
    if len(accepted_a) != 1:
        failures.append(
            "happy_path_joint_trigger_expected_1_accepted_got_%d"
            % len(accepted_a))
    elif accepted_a[0]["geometry_floor_pass_by_variant"] != {
            "2r": True, "3r": True, "4r": True}:
        failures.append("happy_path_floor_unexpected")
    elif accepted_a[0]["entry_price"] != float(
            bars_a[accepted_a[0]["entry_index"]]["close"]):
        failures.append(
            "happy_path_entry_must_equal_next_bar_close")
    elif accepted_a[0]["stop_distance"] <= 0.0:
        failures.append("happy_path_stop_distance_must_be_positive")
    elif not (accepted_a[0]["stop_below_entry"]
              and accepted_a[0]["stop_below_trigger_low"]):
        failures.append("happy_path_stop_geometry_violated")

    # B: insufficient history -> 0 attempts.
    bars_b = fixture_insufficient_history()
    setups_b = scan_c9_setups(bars_b, "BTCUSD")
    record["fixtures"]["insufficient_history"] = {
        "attempts": len(setups_b)}
    if setups_b:
        failures.append(
            "insufficient_history_must_emit_zero_attempts_got_%d"
            % len(setups_b))

    # C: equality at z-threshold -> 0 attempts (strict-below).
    bars_c = fixture_equality_at_z_threshold()
    setups_c = scan_c9_setups(bars_c, "BTCUSD")
    record["fixtures"]["equality_at_z_threshold"] = {
        "attempts": len(setups_c)}
    if setups_c:
        failures.append(
            "equality_at_z_threshold_must_not_trigger_got_%d"
            % len(setups_c))

    # D: equality at volume median -> 0 attempts.
    bars_d = fixture_equality_at_volume_median()
    setups_d = scan_c9_setups(bars_d, "BTCUSD")
    record["fixtures"]["equality_at_volume_median"] = {
        "attempts": len(setups_d)}
    if setups_d:
        failures.append(
            "equality_at_volume_median_must_not_trigger_got_%d"
            % len(setups_d))

    # E: z-only no volume -> 0 attempts.
    bars_e = fixture_z_only_no_volume()
    setups_e = scan_c9_setups(bars_e, "BTCUSD")
    record["fixtures"]["z_only_no_volume"] = {
        "attempts": len(setups_e)}
    if setups_e:
        failures.append(
            "z_only_no_volume_must_not_trigger_got_%d"
            % len(setups_e))

    # F: volume-only no z -> 0 attempts.
    bars_f = fixture_volume_only_no_z()
    setups_f = scan_c9_setups(bars_f, "BTCUSD")
    record["fixtures"]["volume_only_no_z"] = {
        "attempts": len(setups_f)}
    if setups_f:
        failures.append(
            "volume_only_no_z_must_not_trigger_got_%d"
            % len(setups_f))

    # G: entry-bar invalidation -> 1 rejected.
    bars_g = fixture_entry_bar_invalidation()
    setups_g = scan_c9_setups(bars_g, "BTCUSD")
    accepted_g = [s for s in setups_g
                  if s["status"] == "accepted_for_replay_review"]
    rejected_g = [s for s in setups_g
                  if s["status"] == (
                      "rejected_entry_bar_close_at_or_below_trigger"
                      "_bar_low")]
    record["fixtures"]["entry_bar_invalidation"] = {
        "attempts": len(setups_g),
        "accepted": len(accepted_g),
        "rejected_entry_invalidation": len(rejected_g)}
    if accepted_g:
        failures.append(
            "entry_bar_invalidation_should_not_accept")
    if len(rejected_g) != 1:
        failures.append(
            "entry_bar_invalidation_expected_1_rejection_got_%d"
            % len(rejected_g))

    # H: geometry floor all variants fail -> 1 rejected on floor.
    bars_h = fixture_geometry_floor_all_variants_fail()
    setups_h = scan_c9_setups(bars_h, "BTCUSD")
    accepted_h = [s for s in setups_h
                  if s["status"] == "accepted_for_replay_review"]
    rejected_h = [s for s in setups_h
                  if s["status"] == "rejected_geometry_floor"]
    record["fixtures"]["geometry_floor_all_variants_fail"] = {
        "attempts": len(setups_h),
        "accepted": len(accepted_h),
        "rejected_geometry_floor": len(rejected_h),
        "floor_pass_by_variant":
            (rejected_h[0]["geometry_floor_pass_by_variant"]
             if rejected_h else None)}
    if accepted_h:
        failures.append(
            "geometry_floor_all_variants_fail_should_not_accept")
    if len(rejected_h) != 1:
        failures.append(
            "geometry_floor_all_variants_fail_expected_1_rejection")
    elif rejected_h[0]["geometry_floor_pass_by_variant"] != {
            "2r": False, "3r": False, "4r": False}:
        failures.append(
            "geometry_floor_all_variants_fail_unexpected_floor_map")

    # I: anti-cluster filter -- 3 synthetic accepted records at
    # offsets 0/+5/+9. Earlier kept, +5 dropped, +9 kept.
    if accepted_a:
        base = dict(accepted_a[0])
    else:
        base = {"setup_id": "synthetic_a", "symbol": "BTCUSD",
                "status": "accepted_for_replay_review",
                "entry_index": 200, "rejection_reasons": []}
    later_inside = dict(base)
    later_inside["setup_id"] = "synthetic_b_inside"
    later_inside["entry_index"] = base["entry_index"] + 5
    later_outside = dict(base)
    later_outside["setup_id"] = "synthetic_c_outside"
    later_outside["entry_index"] = base["entry_index"] + 9
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

    # J: sample-size adequacy.
    below = check_sample_size_adequacy([{"entry_index": i}
                                        for i in range(3)])
    at_threshold = check_sample_size_adequacy(
        [{"entry_index": i}
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
            "sample_size_must_be_enforced_at_labels_review_gate"
            "_only")
    if below["does_not_consume_edit_token"] is not True:
        failures.append("sample_size_must_not_consume_edit_token")

    # K: context enforcement.
    universe_blocks = {"symbol_eth": False, "timeframe_1h": False,
                       "direction_short": False,
                       "non_list_bars": False}
    bars_for_context = fixture_happy_path_joint_trigger()
    try:
        scan_c9_setups(bars_for_context, "ETHUSD")
    except ValueError:
        universe_blocks["symbol_eth"] = True
    try:
        scan_c9_setups(bars_for_context, "BTCUSD", timeframe="1h")
    except ValueError:
        universe_blocks["timeframe_1h"] = True
    try:
        scan_c9_setups(bars_for_context, "BTCUSD", timeframe=TIMEFRAME,
                       direction="short_only")
    except ValueError:
        universe_blocks["direction_short"] = True
    try:
        scan_c9_setups("not a list", "BTCUSD")
    except ValueError:
        universe_blocks["non_list_bars"] = True
    record["fixtures"]["context_enforcement"] = universe_blocks
    if not all(universe_blocks.values()):
        failures.append(
            "context_enforcement_must_raise_on_each_off_universe"
            "_value")

    record["verdict"] = (VERDICT_C9D_DRY_RUN_PASSED if not failures
                         else VERDICT_C9D_DRY_RUN_FAILED)
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
    "explicit_edge_argument_field_is_proposal_level_locked_not_edit"
    "_token",
    "real_candle_detection_gate_locked",
    "labels_gate_locked",
    "replay_gate_locked",
    "relabel_gate_locked",
)


def build_candidate_9_detector_spec_contract() -> dict[str, Any]:
    """Assemble the C9 detector-spec record. Chain-gated on the
    eight-record ledger, the pushed C9 family proposal, the pushed
    C9 spec review, the pushed V4 rejected-family blacklist, the
    pushed V3, V2, Recommendation V1, and Autopilot V1."""
    record: dict[str, Any] = {
        "schema_version": C9D_SCHEMA_VERSION, "label": C9D_LABEL,
        "mode": C9D_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "universe": list(UNIVERSE), "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "rolling_window_bars": ROLLING_WINDOW_BARS,
        "atr_length": ATR_LENGTH,
        "downside_z_score_threshold_abs":
            DOWNSIDE_Z_SCORE_THRESHOLD_ABS,
        "downside_z_score_threshold_signed": -2.0,
        "volume_percentile_threshold": VOLUME_PERCENTILE_THRESHOLD,
        "volume_strict_below_median": True,
        "joint_trigger_both_conditions_required_on_same_bar": True,
        "entry_rule_close_of_next_completed_bar_after_trigger_bar":
            True,
        "entry_bar_close_must_be_strictly_above_trigger_bar_low":
            True,
        "structure_stop_buffer_atr_multiplier":
            STRUCTURE_STOP_BUFFER_ATR_MULTIPLIER,
        "stop_price_formula":
            "trigger_bar_low - STRUCTURE_STOP_BUFFER_ATR"
            "_MULTIPLIER * ATR14_at_trigger_bar",
        "stop_never_tightened_after_entry": True,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "no_maker_rebate_assumption": True,
        "no_zero_fee_assumption": True,
        "target_variants": list(name for name, _ in TARGET_VARIANTS),
        "target_price_formula":
            "entry_price + r_multiple * stop_distance",
        "timeout_bars": TIMEOUT_BARS,
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
        "explicit_edge_argument_does_not_consume_edit_token": True,
        "no_fetch_ever": True,
        "no_real_time_data": True,
        "staged_data_never_modified": True,
        "detector_required_fields": list(C9_SETUP_REQUIRED_FIELDS),
        "detector_statuses": list(C9_DETECTOR_STATUSES),
        "claim_locks": list(CLAIM_LOCKS),
        "next_required_action": NEXT_REQUIRED_ACTION,
        "current_loop_stage": CURRENT_LOOP_STAGE,
        "ledger_status_eight_records": None,
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
        "creates_runners_now": False, "creates_data_artifacts_now":
            False,
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
                C6_STATUS, C7_STATUS, C8_STATUS)
    record["ledger_status_eight_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C9D_BLOCKED
        record["blockers"].append("eight_record_ledger_broken")
        return record
    if build_candidate_9_family_proposal()["verdict"] != (
            VERDICT_C9P_READY):
        record["verdict"] = VERDICT_C9D_BLOCKED
        record["blockers"].append(
            "candidate_9_proposal_not_certifying")
        return record
    if build_candidate_9_spec_review()["verdict"] != VERDICT_C9S_READY:
        record["verdict"] = VERDICT_C9D_BLOCKED
        record["blockers"].append(
            "candidate_9_spec_review_not_certifying")
        return record
    if build_rejected_family_blacklist_v4()["verdict"] != (
            VERDICT_BL4_READY):
        record["verdict"] = VERDICT_C9D_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C9D_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C9D_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C9D_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C9D_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C9D_READY
    return record


def build_candidate_9_detector_spec_dry_run() -> dict[str, Any]:
    """Run the dry run AND combine with the spec contract. Combined
    verdict is CANDIDATE_9_DETECTOR_SPEC_DRY_RUN_READY iff the
    chain-gated spec record is READY AND the dry-run record is
    DRY_RUN_PASSED."""
    spec_record = build_candidate_9_detector_spec_contract()
    dry_record = run_c9_detector_dry_run()
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
    if combined["verdict"] != VERDICT_C9D_READY:
        combined["combined_verdict"] = VERDICT_C9D_BLOCKED
    elif dry_record["verdict"] != VERDICT_C9D_DRY_RUN_PASSED:
        combined["combined_verdict"] = VERDICT_C9D_DRY_RUN_FAILED
        combined["blockers"].append("dry_run_failed")
        combined["blockers"].extend(dry_record["failures"])
    else:
        combined["combined_verdict"] = VERDICT_C9D_SPEC_DRY_RUN_READY
    return combined


def validate_candidate_9_detector_spec_dry_run(record: Any
                                               ) -> dict[str, Any]:
    """Validate shape, frozen numerics, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    allowed_verdicts = (VERDICT_C9D_READY, VERDICT_C9D_BLOCKED)
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
    if r.get("rolling_window_bars") != 96:
        errors.append("rolling_window_must_be_96")
    if r.get("atr_length") != 14:
        errors.append("atr_length_tampered")
    if r.get("downside_z_score_threshold_abs") != 2.0:
        errors.append("downside_z_threshold_abs_must_be_2_0")
    if r.get("downside_z_score_threshold_signed") != -2.0:
        errors.append("downside_z_threshold_signed_must_be_minus_2_0")
    if r.get("volume_percentile_threshold") != 50.0:
        errors.append("volume_threshold_must_be_50")
    if r.get("volume_strict_below_median") is not True:
        errors.append("volume_strict_below_weakened")
    if r.get(
            "joint_trigger_both_conditions_required_on_same_bar"
    ) is not True:
        errors.append("joint_trigger_same_bar_weakened")
    if r.get(
            "entry_rule_close_of_next_completed_bar_after_trigger"
            "_bar") is not True:
        errors.append("entry_rule_weakened")
    if r.get(
            "entry_bar_close_must_be_strictly_above_trigger_bar_low"
    ) is not True:
        errors.append("entry_invalidation_protection_weakened")
    if r.get("structure_stop_buffer_atr_multiplier") != 0.20:
        errors.append("structure_stop_buffer_must_be_0_20")
    if r.get("stop_price_formula") != (
            "trigger_bar_low - STRUCTURE_STOP_BUFFER_ATR"
            "_MULTIPLIER * ATR14_at_trigger_bar"):
        errors.append("stop_price_formula_tampered")
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
    if r.get("timeout_bars") != 96:
        errors.append("timeout_bars_must_be_96")
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
    if r.get(
            "explicit_edge_argument_does_not_consume_edit_token"
    ) is not True:
        errors.append(
            "explicit_edge_argument_must_not_consume_edit_token")
    if r.get("no_fetch_ever") is not True \
            or r.get("staged_data_never_modified") is not True \
            or r.get("no_real_time_data") is not True:
        errors.append("data_boundary_weakened")
    if list(r.get("detector_required_fields") or ()) != list(
            C9_SETUP_REQUIRED_FIELDS):
        errors.append("detector_required_fields_tampered")
    if list(r.get("detector_statuses") or ()) != list(
            C9_DETECTOR_STATUSES):
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
    if r.get("verdict") == VERDICT_C9D_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}

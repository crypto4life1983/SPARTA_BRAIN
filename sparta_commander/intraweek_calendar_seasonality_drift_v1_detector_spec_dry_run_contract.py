"""SPARTA CANDIDATE #10 DETECTOR SPEC + SYNTHETIC DRY-RUN PATH
(READ-ONLY, RESEARCH ONLY): INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1.

Loop stage: detector_and_label_review. Pure deterministic scanner
implementing the pushed Candidate #10 frozen spec EXACTLY:

  - universe BTCUSD only, timeframe 1d, direction long-only;
  - the ONLY trigger is a SINGLE deterministic ISO-weekday calendar
    condition: a completed daily bar's ISO weekday index equals the
    pre-selected favorable weekday bucket. NO price condition, NO
    volume condition, NO statistical-excursion condition participates.
    The clock is the whole signal;
  - favorable weekday bucket cardinality: 1 (a single ISO weekday);
  - favorable-bucket VALUE is DATA-DETERMINED on the in-sample
    selection window, never hard-coded: the single ISO weekday whose
    mean fixed-horizon forward log return over the in-sample window is
    the HIGHEST AND clears the 81 bps gross target-distance floor;
  - in-sample selection window: 2019-01-01_2022-12-31; out-of-sample
    window: 2023-01-01_2025-12-31; the bucket is selected on the
    in-sample window ONLY and then held FIXED for out-of-sample;
  - entry: a long entry at the CLOSE of the triggering completed daily
    bar (entry_index == trigger_index). NO intrabar entry. NO same-bar
    lookahead beyond the completed close;
  - fixed-horizon exit: 5 completed daily bars after entry (one
    trading week), exit at that bar's close;
  - ATR(14) at the entry/trigger bar (simple-mean true range; the
    C3-shared compute_atr14 primitive on completed daily bars; ATR is
    risk-control only, NEVER an entry trigger);
  - structure stop: stop_price = entry_price -
    STRUCTURE_STOP_ATR_MULTIPLIER (1.5) x ATR(14) at the entry bar;
    stop_distance = entry_price - stop_price; INVALID if stop_distance
    is not positive OR stop is not below entry; stop NEVER tightened;
  - target variants 2r / 3r / 4r; target_price = entry_price +
    r_multiple x stop_distance;
  - 27 bps round-trip fees + 81 bps gross-target-distance floor per
    variant (3 x round-trip) checked at label time before replay
    eligibility;
  - anti-cluster: a weekday bucket fires at most once per ISO week by
    construction, plus a 5-daily-bar (one-week) minimum gap per symbol
    at label-emission time BEFORE replay non-overlap; tie-breaker keeps
    the earlier accepted event. PROPOSAL-LEVEL locked, NOT the single
    C10 edit token;
  - sample-size adequacy: a MINIMUM of 100 accepted setups required at
    the labels-review gate; the dry-run records the count for
    informational propagation only; the structural rejection is
    enforced at labels-review, not here. PROPOSAL-LEVEL locked, NOT the
    single C10 edit token;
  - explicit edge argument beyond pattern geometry: an exogenous
    calendar risk premium driven by recurring weekly liquidity/flow
    cycles; carried forward declaratively. PROPOSAL-LEVEL locked, NOT
    the single C10 edit token.

PURITY LAW: inputs are in-memory candle rows supplied by callers /
tests. Each synthetic bar carries an explicit `iso_weekday` (1-7) and
a lexicographically-sortable ISO `date` ("YYYY-MM-DD") field so the
calendar logic needs NO datetime import and NO wall-clock behavior. No
file reads, no real candles, no staged data, no aggregation execution,
no network, fully deterministic, no module-level runner, no order /
account / trading capability. The dry run uses ONLY in-memory
synthetic fixtures -- no real candle is touched until the separately
human-approved real-candle gate.

Chain-gated live on: the NINE-record rejection ledger (C1-C9 all
REJECTED_KEPT_ON_RECORD), the pushed C10 family proposal, the pushed
C10 spec review, the pushed V5 rejected-family blacklist, the pushed
V4 blacklist, the pushed V3 blacklist, the pushed V2 overnight
autopilot, the pushed Recommendation V1, and the pushed Autopilot Loop
V1.
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
from sparta_commander.intraweek_calendar_seasonality_drift_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY,
    VERDICT_C10P_READY,
    build_candidate_10_family_proposal,
)
from sparta_commander.intraweek_calendar_seasonality_drift_v1_spec_review_contract import (
    VERDICT_C10S_READY,
    build_candidate_10_spec_review,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C8_STATUS,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C9_STATUS,
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
from sparta_commander.strategy_factory_rejected_family_blacklist_v5_contract import (
    VERDICT_BL5_READY,
    build_rejected_family_blacklist_v5,
)
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C10D_SCHEMA_VERSION = (
    "intraweek_calendar_seasonality_drift_v1_detector"
    "_spec_dry_run.v1")
C10D_LABEL = ("SPARTA Candidate #10 Detector Spec + Dry-Run Path "
              "(READ-ONLY, RESEARCH ONLY, PURE FUNCTIONS, SYNTHETIC "
              "FIXTURES ONLY, SINGLE-TRIGGER CALENDAR, NOT A RESCUE, "
              "NOT A CLAIM)")
C10D_MODE = "RESEARCH_ONLY"
VERDICT_C10D_READY = "CANDIDATE_10_DETECTOR_SPEC_READY"
VERDICT_C10D_BLOCKED = "CANDIDATE_10_DETECTOR_SPEC_BLOCKED"
VERDICT_C10D_DRY_RUN_PASSED = "CANDIDATE_10_DETECTOR_DRY_RUN_PASSED"
VERDICT_C10D_DRY_RUN_FAILED = "CANDIDATE_10_DETECTOR_DRY_RUN_FAILED"
VERDICT_C10D_SPEC_DRY_RUN_READY = (
    "CANDIDATE_10_DETECTOR_SPEC_DRY_RUN_READY")
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_10_DRY_RUN_REVIEW"
CURRENT_LOOP_STAGE = "detector_and_label_review"

# ---- frozen numerics (mirror pushed C10 spec review exactly) -------------
UNIVERSE = ("BTCUSD",)
TIMEFRAME = "1d"
DIRECTION = "long_only"
FAVORABLE_WEEKDAY_BUCKET_CARDINALITY = 1
IN_SAMPLE_SELECTION_WINDOW = ("2019-01-01", "2022-12-31")
OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-31")
HOLDING_HORIZON_BARS = 5
ATR_LENGTH = 14
STRUCTURE_STOP_ATR_MULTIPLIER = 1.5
FEE_ROUND_TRIP_BPS = 27.0
TARGET_DISTANCE_FLOOR_BPS = 81.0
TARGET_VARIANTS = (("2r", 2.0), ("3r", 3.0), ("4r", 4.0))
ANTI_CLUSTER_MIN_BAR_GAP = 5
ANTI_CLUSTER_TIE_BREAKER = "keep_the_earlier_event_drop_the_later_one"
SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED = 100
SELECTION_METRIC = (
    "highest_in_sample_mean_fixed_horizon_forward_log_return_among_iso"
    "_weekdays_that_clears_the_81_bps_gross_floor")

C10_SETUP_REQUIRED_FIELDS = (
    "setup_id", "symbol", "timeframe", "direction",
    "trigger_index", "trigger_date", "trigger_time",
    "trigger_iso_weekday", "favorable_weekday_bucket",
    "calendar_condition_passes",
    "uses_no_price_condition", "uses_no_volume_condition",
    "uses_no_excursion_condition",
    "trigger_close", "trigger_high", "trigger_low",
    "atr_at_entry_bar",
    "entry_index", "entry_date", "entry_time", "entry_price",
    "entry_is_at_triggering_bar_close", "entry_is_intrabar",
    "exit_index", "exit_date", "exit_time",
    "holding_horizon_bars",
    "stop_buffer_price", "stop_price", "stop_distance",
    "stop_below_entry",
    "target_2r", "target_3r", "target_4r",
    "target_distance_bps_2r", "target_distance_bps_3r",
    "target_distance_bps_4r",
    "geometry_floor_pass_by_variant",
    "accepted_for_labeling_by_variant",
    "replay_start_time", "status", "rejection_reasons",
)

C10_DETECTOR_STATUSES = (
    "accepted_for_replay_review",
    "rejected_invalid_stop_geometry",
    "rejected_geometry_floor",
    "rejected_no_evaluation_bar",
    "rejected_clustered_within_5_bars_of_prior_accepted",
)


def get_candidate_10_detector_label() -> str:
    return C10D_LABEL


def validate_detection_context(symbol: str, timeframe: str,
                               direction: str) -> None:
    """Raise ValueError on any context outside the frozen BTCUSD / 1d /
    long_only universe. Pure."""
    if symbol not in UNIVERSE:
        raise ValueError(
            "symbol_outside_candidate_10_universe:" + str(symbol))
    if timeframe != TIMEFRAME:
        raise ValueError(
            "timeframe_outside_candidate_10_universe:" + str(timeframe))
    if direction != DIRECTION:
        raise ValueError(
            "direction_outside_candidate_10_universe:" + str(direction))


def _validate_weekday_bucket(favorable_weekday_bucket: Any) -> None:
    """Raise ValueError if the bucket is not a single ISO weekday in
    1..7. Cardinality is fixed at 1. Pure."""
    if not isinstance(favorable_weekday_bucket, int) \
            or isinstance(favorable_weekday_bucket, bool):
        raise ValueError(
            "favorable_weekday_bucket_must_be_int:"
            + str(favorable_weekday_bucket))
    if favorable_weekday_bucket < 1 or favorable_weekday_bucket > 7:
        raise ValueError(
            "favorable_weekday_bucket_out_of_iso_range_1_to_7:"
            + str(favorable_weekday_bucket))


# ---- window membership (string comparison, no datetime) ------------------

def _in_window(date_str: str, window: tuple) -> bool:
    """Lexicographic ISO 'YYYY-MM-DD' membership: window[0] <= date <=
    window[1]. Fixed-width ISO dates sort chronologically. Pure."""
    return window[0] <= str(date_str) <= window[1]


# ---- pure numeric primitives ---------------------------------------------

def compute_forward_log_return(bars: list, t: int,
                               horizon: int = HOLDING_HORIZON_BARS
                               ) -> float | None:
    """log(close[t + horizon] / close[t]) over completed daily bars.
    Returns None if the horizon exit bar does not exist or a close is
    non-positive. Pure."""
    if t < 0 or (t + horizon) >= len(bars):
        return None
    entry_close = float(bars[t]["close"])
    exit_close = float(bars[t + horizon]["close"])
    if entry_close <= 0.0 or exit_close <= 0.0:
        return None
    return math.log(exit_close / entry_close)


def select_favorable_weekday_bucket(
        bars: list,
        in_sample_window: tuple = IN_SAMPLE_SELECTION_WINDOW,
        horizon: int = HOLDING_HORIZON_BARS,
        floor_bps: float = TARGET_DISTANCE_FLOOR_BPS) -> dict[str, Any]:
    """DATA-DETERMINED favorable weekday selection. Groups in-sample
    bars (both the bar AND its horizon-exit bar inside the in-sample
    window) by ISO weekday, computes each weekday's MEAN fixed-horizon
    forward log return in bps, and selects the single ISO weekday with
    the HIGHEST mean that ALSO clears the 81 bps gross floor. Tie-
    breaker: lowest ISO weekday index. The bucket VALUE is NEVER
    hard-coded -- it is computed here on the in-sample window only.
    Pure."""
    per_weekday_returns: dict[int, list] = {}
    n = len(bars)
    for t in range(n):
        bar = bars[t]
        if not _in_window(bar["date"], in_sample_window):
            continue
        exit_index = t + horizon
        if exit_index >= n:
            continue
        if not _in_window(bars[exit_index]["date"], in_sample_window):
            continue
        fwd = compute_forward_log_return(bars, t, horizon)
        if fwd is None:
            continue
        weekday = int(bar["iso_weekday"])
        per_weekday_returns.setdefault(weekday, []).append(fwd)
    per_weekday_mean_bps: dict[int, float] = {}
    for weekday, returns in per_weekday_returns.items():
        mean_log = sum(returns) / len(returns)
        per_weekday_mean_bps[weekday] = mean_log * 10000.0
    eligible = [(weekday, bps)
                for weekday, bps in per_weekday_mean_bps.items()
                if bps >= floor_bps]
    favorable_weekday_bucket = None
    cleared = False
    if eligible:
        best_bps = max(bps for _, bps in eligible)
        winners = sorted(weekday for weekday, bps in eligible
                         if bps == best_bps)
        favorable_weekday_bucket = winners[0]
        cleared = True
    return {
        "favorable_weekday_bucket": favorable_weekday_bucket,
        "favorable_weekday_bucket_cardinality":
            FAVORABLE_WEEKDAY_BUCKET_CARDINALITY,
        "per_weekday_mean_bps": {
            weekday: round(bps, 6)
            for weekday, bps in sorted(per_weekday_mean_bps.items())},
        "per_weekday_sample_count": {
            weekday: len(returns)
            for weekday, returns in sorted(per_weekday_returns.items())},
        "selection_metric": SELECTION_METRIC,
        "floor_bps": floor_bps,
        "cleared_81_bps_floor": cleared,
        "bucket_value_is_data_determined_not_hardcoded": True,
        "selected_on_in_sample_window_only": True,
        "in_sample_window": list(in_sample_window),
    }


def compute_stop(entry_price: float,
                 atr_at_entry: float) -> dict[str, Any]:
    """Structure stop: stop_price = entry_price -
    STRUCTURE_STOP_ATR_MULTIPLIER (1.5) * ATR(14) at the entry bar.
    Invalid if stop_distance is not positive OR stop is not below
    entry. Pure."""
    buffer = STRUCTURE_STOP_ATR_MULTIPLIER * float(atr_at_entry)
    stop_price = float(entry_price) - buffer
    stop_distance = float(entry_price) - stop_price
    stop_below_entry = stop_price < float(entry_price)
    valid = stop_distance > 0.0 and stop_below_entry
    return {"stop_buffer_price": buffer,
            "stop_price": stop_price,
            "stop_distance": stop_distance,
            "stop_below_entry": stop_below_entry,
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


# ---- the deterministic scanner -------------------------------------------

def _precompute_atr(bars: list) -> list:
    """Pure. ATR(14) at every index via the shared compute_atr14
    primitive on completed daily bars."""
    return [compute_atr14(bars, t) for t in range(len(bars))]


def _empty_setup_record() -> dict[str, Any]:
    return {field: None for field in C10_SETUP_REQUIRED_FIELDS}


def scan_c10_setups(bars: list, favorable_weekday_bucket: int,
                    symbol: str = "BTCUSD",
                    timeframe: str = TIMEFRAME,
                    direction: str = DIRECTION,
                    evaluation_window: tuple | None = None
                    ) -> list[dict[str, Any]]:
    """Candidate #10 scanner. bars: in-memory list of daily rows
    ({date, iso_weekday, time_utc, open, high, low, close}). The ONLY
    trigger is the calendar condition iso_weekday == favorable bucket;
    no price/volume/excursion condition is read. Entry at the CLOSE of
    the triggering bar. Locked to BTCUSD / 1d / long_only -- raises
    ValueError on any other context or any non-ISO weekday bucket."""
    validate_detection_context(symbol, timeframe, direction)
    _validate_weekday_bucket(favorable_weekday_bucket)
    if not isinstance(bars, list):
        raise ValueError("bars_must_be_a_list")
    n = len(bars)
    atr_values = _precompute_atr(bars)
    setups: list[dict[str, Any]] = []
    last_entry_index_emitted = -1
    for t in range(n):
        bar = bars[t]
        if evaluation_window is not None \
                and not _in_window(bar["date"], evaluation_window):
            continue
        if int(bar["iso_weekday"]) != favorable_weekday_bucket:
            continue
        if t <= last_entry_index_emitted:
            continue
        atr = atr_values[t]
        if atr is None:
            continue
        record = _empty_setup_record()
        entry_price = float(bar["close"])
        record.update({
            "setup_id": "%s_%s" % (symbol, bar["date"]),
            "symbol": symbol, "timeframe": TIMEFRAME,
            "direction": DIRECTION,
            "trigger_index": t,
            "trigger_date": bar["date"],
            "trigger_time": bar.get("time_utc"),
            "trigger_iso_weekday": int(bar["iso_weekday"]),
            "favorable_weekday_bucket": favorable_weekday_bucket,
            "calendar_condition_passes": True,
            "uses_no_price_condition": True,
            "uses_no_volume_condition": True,
            "uses_no_excursion_condition": True,
            "trigger_close": round(float(bar["close"]), 6),
            "trigger_high": round(float(bar["high"]), 6),
            "trigger_low": round(float(bar["low"]), 6),
            "atr_at_entry_bar": round(float(atr), 6),
            "entry_index": t,
            "entry_date": bar["date"],
            "entry_time": bar.get("time_utc"),
            "entry_price": entry_price,
            "entry_is_at_triggering_bar_close": True,
            "entry_is_intrabar": False,
            "holding_horizon_bars": HOLDING_HORIZON_BARS,
            "rejection_reasons": [],
        })
        exit_index = t + HOLDING_HORIZON_BARS
        if exit_index >= n:
            record["status"] = "rejected_no_evaluation_bar"
            record["rejection_reasons"].append(
                "no_horizon_exit_bar_for_fixed_horizon_exit")
            setups.append(record)
            last_entry_index_emitted = t
            continue
        exit_bar = bars[exit_index]
        record.update({
            "exit_index": exit_index,
            "exit_date": exit_bar["date"],
            "exit_time": exit_bar.get("time_utc"),
            "replay_start_time":
                (bars[t + 1]["date"] if t + 1 < n else None),
        })
        stop = compute_stop(entry_price, atr)
        record.update({
            "stop_buffer_price": round(stop["stop_buffer_price"], 6),
            "stop_price": round(stop["stop_price"], 6),
            "stop_distance": round(stop["stop_distance"], 6),
            "stop_below_entry": stop["stop_below_entry"],
        })
        if not stop["valid"]:
            record["status"] = "rejected_invalid_stop_geometry"
            record["rejection_reasons"].append(
                "stop_distance_not_positive_or_stop_not_below_entry")
            setups.append(record)
            last_entry_index_emitted = t
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
        if not floor["any_variant_passes"]:
            record["status"] = "rejected_geometry_floor"
            record["rejection_reasons"].append(
                "all_variant_target_distances_below_81_bps")
            setups.append(record)
            last_entry_index_emitted = t
            continue
        record["status"] = "accepted_for_replay_review"
        setups.append(record)
        last_entry_index_emitted = t
    return setups


def apply_anti_cluster_filter(setups: list) -> dict[str, Any]:
    """5-daily-bar (one-week) same-symbol anti-cluster gap at label-
    emission time on the chronologically-sorted ACCEPTED events. Tie-
    breaker: keep the earlier accepted event and drop the later one
    whose entry_index difference is strictly less than
    ANTI_CLUSTER_MIN_BAR_GAP. The one-fire-per-ISO-week construction is
    the primary anti-cluster constraint. PROPOSAL-LEVEL locked, NOT the
    single C10 edit token."""
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
                "rejected_clustered_within_5_bars_of_prior_accepted")
            dropped_record["rejection_reasons"] = list(
                s.get("rejection_reasons") or []) + [
                "less_than_5_completed_daily_bars_after_prior_accepted"
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
    labels-review gate. PROPOSAL-LEVEL locked, NOT the single C10 edit
    token. Pure."""
    n = len(accepted_setups)
    return {"accepted_count": n,
            "minimum_required_at_labels_review_gate": threshold,
            "below_minimum_at_dry_run": n < threshold,
            "enforced_at_labels_review_gate_only": True,
            "does_not_consume_edit_token": True}


# ---- synthetic fixtures (in-memory only) ---------------------------------

def _iso_date(start_year: int, index: int) -> str:
    """Deterministic, lexicographically-sortable synthetic ISO date.
    28-day months x 12 months = 336 days/year so every day is a valid
    1..28 / 1..12 value and fixed-width strings sort chronologically.
    No datetime, no wall-clock. Pure."""
    total = index
    year = start_year + total // 336
    rem = total % 336
    month = rem // 28 + 1
    day = rem % 28 + 1
    return "%04d-%02d-%02d" % (year, month, day)


def _daily_bar(start_year: int, index: int, open_price: float,
               high: float, low: float, close: float) -> dict[str, Any]:
    date = _iso_date(start_year, index)
    return {"date": date,
            "iso_weekday": (index % 7) + 1,
            "time_utc": date + "T00:00:00Z",
            "open": float(open_price),
            "high": float(high),
            "low": float(low),
            "close": float(close)}


# weekday-keyed close map: weekday 3 is the UNIQUE in-sample winner.
# forward(weekday w) = log(P[((w-1+5)%7)+1] / P[w]):
#   w=3 -> log(P[1]/P[3]) = log(50500/50000) = +99.5 bps  (clears 81)
#   every other weekday -> <= 0 bps (fails the 81 floor)
_WEEKDAY_CLOSE = {1: 50500.0, 2: 50100.0, 3: 50000.0, 4: 50100.0,
                  5: 50100.0, 6: 50100.0, 7: 50100.0}


def _weekday_close_bar(start_year: int, index: int) -> dict[str, Any]:
    weekday = (index % 7) + 1
    close = _WEEKDAY_CLOSE[weekday]
    return _daily_bar(start_year, index, close, close + 5.0,
                      close - 5.0, close)


def fixture_bucket_selection_data_determined(
        in_sample_length: int = 210,
        oos_length: int = 70) -> list:
    """In-sample bars (start_year 2020, all inside 2019-01-01..
    2022-12-31) whose weekday-keyed closes make ISO weekday 3 the
    UNIQUE forward-return winner clearing 81 bps. Then OOS POISON bars
    (start_year 2024, inside 2023-01-01..2025-12-31) engineered so that
    IF the OOS window were wrongly included, weekday 5 would dominate.
    Proves the bucket is data-determined on the IN-SAMPLE window only
    and that in/out-of-sample are separated."""
    bars = [_weekday_close_bar(2020, i) for i in range(in_sample_length)]
    # OOS poison: huge weekday-5 forward returns. weekday-5 bars sit at
    # index where (i%7)+1 == 5 -> i%7 == 4. Give those a low close and
    # the bar 5 ahead a high close, so a (wrong) OOS inclusion would
    # crown weekday 5. The selector must ignore these entirely.
    for j in range(oos_length):
        weekday = (j % 7) + 1
        if weekday == 5:
            close = 49000.0
        elif weekday == 3:
            close = 50000.0
        else:
            close = 50000.0
        bars.append(_daily_bar(2024, j, close, close + 5.0,
                               close - 5.0, close))
    return bars


def _flat_bar(start_year: int, index: int, close: float = 50000.0,
              half_range: float = 80.0) -> dict[str, Any]:
    """Constant-close daily bar with a symmetric range. Across a
    14-bar run ATR(14) == 2 * half_range (true range each bar is
    high-low == 2*half_range because prev_close == close)."""
    return _daily_bar(start_year, index, close, close + half_range,
                      close - half_range, close)


def fixture_geometry_happy_path() -> list:
    """22 flat daily bars (half_range 80 -> ATR(14)=160). Only the
    weekday-3 bar at index 16 has both ATR(14) available (index>=14)
    and a horizon-exit bar (index+5 < 22), so EXACTLY one accepted
    setup. stop_distance = 1.5*160 = 240; 2r=96 bps / 3r=144 / 4r=192,
    all clear the 81 bps floor."""
    return [_flat_bar(2020, i, 50000.0, 80.0) for i in range(22)]


def fixture_geometry_floor_all_variants_fail() -> list:
    """22 flat daily bars with a TINY range (half_range 2 ->
    ATR(14)=4). The single weekday-3 setup at index 16 has
    stop_distance = 1.5*4 = 6; 2r=2.4 bps, far below 81 -> all variants
    fail the floor -> 1 rejected_geometry_floor."""
    return [_flat_bar(2020, i, 50000.0, 2.0) for i in range(22)]


def fixture_no_price_condition() -> list:
    """22 flat weekday bars. The weekday-3 bar at index 16 triggers on
    the calendar ALONE (flat price). A weekday-4 bar at index 17 is a
    WILD crash (close 30000, huge range) yet does NOT trigger -- proof
    that no price/volume/excursion condition participates."""
    bars = [_flat_bar(2020, i, 50000.0, 80.0) for i in range(22)]
    # index 17 is weekday 4 ((17%7)+1 == 4): replace with a crash bar.
    crash = _daily_bar(2020, 17, 50000.0, 50050.0, 29900.0, 30000.0)
    bars[17] = crash
    return bars


def fixture_in_out_of_sample_separation() -> list:
    """Alias of the bucket-selection fixture -- proves selection uses
    the in-sample window only and ignores out-of-sample poison."""
    return fixture_bucket_selection_data_determined()


def fixture_symbol_outside_universe() -> list:
    """Well-formed bars -- the universe rejection happens inside
    scan_c10_setups when symbol is not 'BTCUSD'."""
    return fixture_geometry_happy_path()


# ---- dry run -------------------------------------------------------------

def run_c10_detector_dry_run() -> dict[str, Any]:
    """Run the scanner / selector over IN-MEMORY synthetic fixtures
    only and check expected outcomes. Touches no real candles, no
    staged data."""
    record: dict[str, Any] = {
        "schema_version": C10D_SCHEMA_VERSION, "label": C10D_LABEL,
        "mode": C10D_MODE, "verdict": None, "failures": [],
        "fixtures": {}, "uses_synthetic_fixtures_only": True,
        "reads_real_candles": False, "reads_staged_data": False,
        "reads_any_files": False,
    }
    failures = record["failures"]

    # A: data-determined bucket selection -> weekday 3, clears floor,
    # in-sample only (OOS poison ignored).
    bars_a = fixture_bucket_selection_data_determined()
    sel_a = select_favorable_weekday_bucket(bars_a)
    record["fixtures"]["bucket_selection_data_determined"] = {
        "favorable_weekday_bucket": sel_a["favorable_weekday_bucket"],
        "cardinality": sel_a["favorable_weekday_bucket_cardinality"],
        "cleared_81_bps_floor": sel_a["cleared_81_bps_floor"],
        "per_weekday_mean_bps": sel_a["per_weekday_mean_bps"],
        "bucket_value_is_data_determined_not_hardcoded":
            sel_a["bucket_value_is_data_determined_not_hardcoded"],
        "selected_on_in_sample_window_only":
            sel_a["selected_on_in_sample_window_only"]}
    if sel_a["favorable_weekday_bucket"] != 3:
        failures.append(
            "bucket_selection_expected_weekday_3_got_%s"
            % str(sel_a["favorable_weekday_bucket"]))
    if sel_a["favorable_weekday_bucket_cardinality"] != 1:
        failures.append("bucket_cardinality_must_be_1")
    if sel_a["cleared_81_bps_floor"] is not True:
        failures.append("bucket_selection_must_clear_81_bps_floor")
    if sel_a["bucket_value_is_data_determined_not_hardcoded"] is not \
            True:
        failures.append("bucket_value_must_be_data_determined")
    # only weekday 3 clears the floor.
    cleared = [w for w, bps in sel_a["per_weekday_mean_bps"].items()
               if bps >= TARGET_DISTANCE_FLOOR_BPS]
    if cleared != [3]:
        failures.append(
            "only_weekday_3_should_clear_floor_got_%s" % str(cleared))

    # B: in/out-of-sample separation -- OOS-only selection differs.
    bars_b = fixture_in_out_of_sample_separation()
    sel_oos = select_favorable_weekday_bucket(
        bars_b, in_sample_window=OUT_OF_SAMPLE_WINDOW)
    record["fixtures"]["in_out_of_sample_separation"] = {
        "in_sample_bucket": sel_a["favorable_weekday_bucket"],
        "oos_window_bucket": sel_oos["favorable_weekday_bucket"],
        "selected_on_in_sample_window_only":
            sel_a["selected_on_in_sample_window_only"]}
    if sel_oos["favorable_weekday_bucket"] == 3:
        failures.append(
            "oos_window_selection_must_not_match_in_sample_poison"
            "_proves_separation")

    # C: geometry happy path -> exactly 1 accepted, all variants pass,
    # entry at triggering bar close, no intrabar.
    bars_c = fixture_geometry_happy_path()
    setups_c = scan_c10_setups(bars_c, 3, "BTCUSD")
    accepted_c = [s for s in setups_c
                  if s["status"] == "accepted_for_replay_review"]
    record["fixtures"]["geometry_happy_path"] = {
        "attempts": len(setups_c),
        "accepted": len(accepted_c),
        "first_accepted_index":
            (accepted_c[0]["entry_index"] if accepted_c else None),
        "first_accepted_floor_pass":
            (accepted_c[0]["geometry_floor_pass_by_variant"]
             if accepted_c else None)}
    if len(accepted_c) != 1:
        failures.append(
            "geometry_happy_path_expected_1_accepted_got_%d"
            % len(accepted_c))
    else:
        a = accepted_c[0]
        if a["geometry_floor_pass_by_variant"] != {
                "2r": True, "3r": True, "4r": True}:
            failures.append("geometry_happy_path_floor_unexpected")
        if a["entry_index"] != a["trigger_index"]:
            failures.append(
                "entry_index_must_equal_trigger_index_close_entry")
        if a["entry_price"] != float(
                bars_c[a["trigger_index"]]["close"]):
            failures.append(
                "entry_price_must_equal_triggering_bar_close")
        if a["entry_is_at_triggering_bar_close"] is not True \
                or a["entry_is_intrabar"] is not False:
            failures.append("entry_must_be_close_only_not_intrabar")
        if a["trigger_iso_weekday"] != 3:
            failures.append("trigger_iso_weekday_must_be_3")
        if a["holding_horizon_bars"] != HOLDING_HORIZON_BARS:
            failures.append("holding_horizon_must_be_5")
        if a["exit_index"] != a["entry_index"] + HOLDING_HORIZON_BARS:
            failures.append("exit_index_must_be_entry_plus_horizon")
        if not (a["uses_no_price_condition"]
                and a["uses_no_volume_condition"]
                and a["uses_no_excursion_condition"]):
            failures.append("setup_must_record_calendar_only_trigger")
        if a["stop_distance"] <= 0.0 or not a["stop_below_entry"]:
            failures.append("geometry_happy_path_stop_geometry_bad")

    # D: geometry floor all variants fail -> 1 rejected on floor.
    bars_d = fixture_geometry_floor_all_variants_fail()
    setups_d = scan_c10_setups(bars_d, 3, "BTCUSD")
    accepted_d = [s for s in setups_d
                  if s["status"] == "accepted_for_replay_review"]
    rejected_d = [s for s in setups_d
                  if s["status"] == "rejected_geometry_floor"]
    record["fixtures"]["geometry_floor_all_variants_fail"] = {
        "attempts": len(setups_d),
        "accepted": len(accepted_d),
        "rejected_geometry_floor": len(rejected_d),
        "floor_pass_by_variant":
            (rejected_d[0]["geometry_floor_pass_by_variant"]
             if rejected_d else None)}
    if accepted_d:
        failures.append(
            "geometry_floor_all_variants_fail_should_not_accept")
    if len(rejected_d) != 1:
        failures.append(
            "geometry_floor_all_variants_fail_expected_1_rejection")
    elif rejected_d[0]["geometry_floor_pass_by_variant"] != {
            "2r": False, "3r": False, "4r": False}:
        failures.append(
            "geometry_floor_all_variants_fail_unexpected_floor_map")

    # E: no-price-condition -- calendar-only trigger; a wild weekday-4
    # crash bar does NOT trigger; the flat weekday-3 bar still does.
    bars_e = fixture_no_price_condition()
    setups_e = scan_c10_setups(bars_e, 3, "BTCUSD")
    accepted_e = [s for s in setups_e
                  if s["status"] == "accepted_for_replay_review"]
    triggered_weekdays_e = sorted(
        set(s["trigger_iso_weekday"] for s in setups_e))
    record["fixtures"]["no_price_condition"] = {
        "attempts": len(setups_e),
        "accepted": len(accepted_e),
        "triggered_weekdays": triggered_weekdays_e}
    if triggered_weekdays_e != [3]:
        failures.append(
            "no_price_condition_only_weekday_3_should_trigger_got_%s"
            % str(triggered_weekdays_e))
    if len(accepted_e) != 1:
        failures.append(
            "no_price_condition_expected_1_accepted_weekday_3_setup")

    # F: anti-cluster filter -- 3 synthetic accepted records at offsets
    # 0/+3/+5. Earlier kept, +3 dropped (gap 3 < 5), +5 kept.
    base = {"setup_id": "synthetic_a", "symbol": "BTCUSD",
            "status": "accepted_for_replay_review",
            "entry_index": 200, "rejection_reasons": []}
    inside = dict(base)
    inside["setup_id"] = "synthetic_b_inside"
    inside["entry_index"] = base["entry_index"] + 3
    outside = dict(base)
    outside["setup_id"] = "synthetic_c_outside"
    outside["entry_index"] = base["entry_index"] + 5
    cluster_result = apply_anti_cluster_filter([base, inside, outside])
    kept_ids = set(s["setup_id"] for s in cluster_result["kept"])
    dropped_ids = set(s["setup_id"] for s in cluster_result["dropped"])
    record["fixtures"]["anti_cluster"] = {
        "kept_ids": sorted(kept_ids),
        "dropped_ids": sorted(dropped_ids),
        "anti_cluster_min_bar_gap":
            cluster_result["anti_cluster_min_bar_gap"],
        "anti_cluster_does_not_consume_edit_token":
            cluster_result["anti_cluster_does_not_consume_edit_token"]}
    if "synthetic_a" not in kept_ids:
        failures.append("anti_cluster_should_keep_earliest_event")
    if "synthetic_b_inside" not in dropped_ids:
        failures.append(
            "anti_cluster_should_drop_event_within_5_bars_of_prior")
    if "synthetic_c_outside" not in kept_ids:
        failures.append(
            "anti_cluster_should_keep_event_at_or_after_5_bar_gap")
    if cluster_result["anti_cluster_min_bar_gap"] != 5:
        failures.append("anti_cluster_min_bar_gap_must_be_5")
    if cluster_result[
            "anti_cluster_does_not_consume_edit_token"] is not True:
        failures.append("anti_cluster_must_not_consume_edit_token")

    # G: sample-size adequacy.
    below = check_sample_size_adequacy([{"entry_index": i}
                                        for i in range(3)])
    at_threshold = check_sample_size_adequacy(
        [{"entry_index": i}
         for i in range(SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED)])
    record["fixtures"]["sample_size_adequacy"] = {
        "below_minimum_at_dry_run": below["below_minimum_at_dry_run"],
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

    # H: no-evaluation-bar -- a weekday-3 trigger with ATR available but
    # no horizon-exit bar is rejected on rejected_no_evaluation_bar.
    # 18 flat bars: weekday-3 at index 16 has ATR(14) but 16+5=21 >= 18.
    bars_h = [_flat_bar(2020, i, 50000.0, 80.0) for i in range(18)]
    setups_h = scan_c10_setups(bars_h, 3, "BTCUSD")
    rejected_h = [s for s in setups_h
                  if s["status"] == "rejected_no_evaluation_bar"]
    accepted_h = [s for s in setups_h
                  if s["status"] == "accepted_for_replay_review"]
    record["fixtures"]["no_evaluation_bar"] = {
        "attempts": len(setups_h),
        "accepted": len(accepted_h),
        "rejected_no_evaluation_bar": len(rejected_h)}
    if accepted_h:
        failures.append("no_evaluation_bar_should_not_accept")
    if len(rejected_h) != 1:
        failures.append(
            "no_evaluation_bar_expected_1_rejection_got_%d"
            % len(rejected_h))

    # I: context enforcement + invalid weekday bucket.
    blocks = {"symbol_eth": False, "timeframe_1h": False,
              "direction_short": False, "non_list_bars": False,
              "bucket_zero": False, "bucket_eight": False}
    bars_ctx = fixture_geometry_happy_path()
    try:
        scan_c10_setups(bars_ctx, 3, "ETHUSD")
    except ValueError:
        blocks["symbol_eth"] = True
    try:
        scan_c10_setups(bars_ctx, 3, "BTCUSD", timeframe="1h")
    except ValueError:
        blocks["timeframe_1h"] = True
    try:
        scan_c10_setups(bars_ctx, 3, "BTCUSD", timeframe=TIMEFRAME,
                        direction="short_only")
    except ValueError:
        blocks["direction_short"] = True
    try:
        scan_c10_setups("not a list", 3, "BTCUSD")
    except ValueError:
        blocks["non_list_bars"] = True
    try:
        scan_c10_setups(bars_ctx, 0, "BTCUSD")
    except ValueError:
        blocks["bucket_zero"] = True
    try:
        scan_c10_setups(bars_ctx, 8, "BTCUSD")
    except ValueError:
        blocks["bucket_eight"] = True
    record["fixtures"]["context_enforcement"] = blocks
    if not all(blocks.values()):
        failures.append(
            "context_enforcement_must_raise_on_each_off_universe_or"
            "_off_bucket_value")

    record["verdict"] = (VERDICT_C10D_DRY_RUN_PASSED if not failures
                         else VERDICT_C10D_DRY_RUN_FAILED)
    return record


# ---- the contract record -------------------------------------------------

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
    "single_trigger_design_is_proposal_level_locked_not_edit_token",
    "favorable_weekday_bucket_value_is_data_determined_not_hardcoded",
    "real_candle_detection_gate_locked",
    "labels_gate_locked",
    "replay_gate_locked",
    "relabel_gate_locked",
)


def build_candidate_10_detector_spec_contract() -> dict[str, Any]:
    """Assemble the C10 detector-spec record. Chain-gated on the NINE-
    record ledger (C1-C9), the pushed C10 family proposal, the pushed
    C10 spec review, the pushed V5/V4/V3 blacklists, the pushed V2
    overnight autopilot, the pushed Recommendation V1, and the pushed
    Autopilot Loop V1."""
    record: dict[str, Any] = {
        "schema_version": C10D_SCHEMA_VERSION, "label": C10D_LABEL,
        "mode": C10D_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "universe": list(UNIVERSE), "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "trigger_is_single_iso_weekday_calendar_condition": True,
        "favorable_weekday_bucket_cardinality":
            FAVORABLE_WEEKDAY_BUCKET_CARDINALITY,
        "favorable_weekday_bucket_value_is_data_determined": True,
        "favorable_weekday_bucket_value_is_hardcoded": False,
        "selection_metric": SELECTION_METRIC,
        "in_sample_selection_window": list(IN_SAMPLE_SELECTION_WINDOW),
        "out_of_sample_window": list(OUT_OF_SAMPLE_WINDOW),
        "bucket_selected_on_in_sample_window_only": True,
        "bucket_held_fixed_for_out_of_sample": True,
        "uses_no_price_condition": True,
        "uses_no_volume_condition": True,
        "uses_no_excursion_condition": True,
        "entry_rule_close_of_triggering_completed_daily_bar": True,
        "entry_index_equals_trigger_index": True,
        "no_intrabar_entry": True,
        "holding_horizon_bars": HOLDING_HORIZON_BARS,
        "fixed_horizon_exit_at_close": True,
        "atr_length": ATR_LENGTH,
        "atr_is_risk_control_only_never_entry_trigger": True,
        "structure_stop_atr_multiplier": STRUCTURE_STOP_ATR_MULTIPLIER,
        "stop_price_formula":
            "entry_price - STRUCTURE_STOP_ATR_MULTIPLIER * "
            "ATR14_at_entry_bar",
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
        "one_fire_per_iso_week_by_construction": True,
        "sample_size_adequacy_threshold_min_accepted":
            SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED,
        "sample_size_adequacy_does_not_consume_edit_token": True,
        "sample_size_adequacy_enforced_at_labels_review_gate_only":
            True,
        "explicit_edge_argument_beyond_pattern_geometry":
            EXPLICIT_EDGE_ARGUMENT_BEYOND_PATTERN_GEOMETRY,
        "explicit_edge_argument_does_not_consume_edit_token": True,
        "single_trigger_design_does_not_consume_edit_token": True,
        "no_fetch_ever": True,
        "no_real_time_data": True,
        "staged_data_never_modified": True,
        "detector_required_fields": list(C10_SETUP_REQUIRED_FIELDS),
        "detector_statuses": list(C10_DETECTOR_STATUSES),
        "claim_locks": list(CLAIM_LOCKS),
        "next_required_action": NEXT_REQUIRED_ACTION,
        "current_loop_stage": CURRENT_LOOP_STAGE,
        "ledger_status_nine_records": None,
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
        "creates_runners_now": False,
        "creates_data_artifacts_now": False,
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
                C6_STATUS, C7_STATUS, C8_STATUS, C9_STATUS)
    record["ledger_status_nine_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C10D_BLOCKED
        record["blockers"].append("nine_record_ledger_broken")
        return record
    if build_candidate_10_family_proposal()["verdict"] != (
            VERDICT_C10P_READY):
        record["verdict"] = VERDICT_C10D_BLOCKED
        record["blockers"].append(
            "candidate_10_proposal_not_certifying")
        return record
    if build_candidate_10_spec_review()["verdict"] != (
            VERDICT_C10S_READY):
        record["verdict"] = VERDICT_C10D_BLOCKED
        record["blockers"].append(
            "candidate_10_spec_review_not_certifying")
        return record
    if build_rejected_family_blacklist_v5()["verdict"] != (
            VERDICT_BL5_READY):
        record["verdict"] = VERDICT_C10D_BLOCKED
        record["blockers"].append("v5_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v4()["verdict"] != (
            VERDICT_BL4_READY):
        record["verdict"] = VERDICT_C10D_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C10D_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C10D_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C10D_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C10D_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C10D_READY
    return record


def build_candidate_10_detector_spec_dry_run() -> dict[str, Any]:
    """Run the dry run AND combine with the spec contract. Combined
    verdict is CANDIDATE_10_DETECTOR_SPEC_DRY_RUN_READY iff the chain-
    gated spec record is READY AND the dry-run record is
    DRY_RUN_PASSED."""
    spec_record = build_candidate_10_detector_spec_contract()
    dry_record = run_c10_detector_dry_run()
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
    if combined["verdict"] != VERDICT_C10D_READY:
        combined["combined_verdict"] = VERDICT_C10D_BLOCKED
    elif dry_record["verdict"] != VERDICT_C10D_DRY_RUN_PASSED:
        combined["combined_verdict"] = VERDICT_C10D_DRY_RUN_FAILED
        combined["blockers"].append("dry_run_failed")
        combined["blockers"].extend(dry_record["failures"])
    else:
        combined["combined_verdict"] = VERDICT_C10D_SPEC_DRY_RUN_READY
    return combined


def validate_candidate_10_detector_spec_dry_run(record: Any
                                                ) -> dict[str, Any]:
    """Validate shape, frozen numerics, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    allowed_verdicts = (VERDICT_C10D_READY, VERDICT_C10D_BLOCKED)
    if r.get("verdict") not in allowed_verdicts:
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("universe") != ["BTCUSD"]:
        errors.append("universe_tampered")
    if r.get("timeframe") != "1d" or r.get("direction") != "long_only":
        errors.append("timeframe_or_direction_tampered")
    if r.get(
            "trigger_is_single_iso_weekday_calendar_condition"
    ) is not True:
        errors.append("single_calendar_trigger_weakened")
    if r.get("favorable_weekday_bucket_cardinality") != 1:
        errors.append("favorable_weekday_bucket_cardinality_must_be_1")
    if r.get("favorable_weekday_bucket_value_is_data_determined") is \
            not True:
        errors.append("bucket_value_must_be_data_determined")
    if r.get("favorable_weekday_bucket_value_is_hardcoded") is not \
            False:
        errors.append("bucket_value_must_not_be_hardcoded")
    if r.get("selection_metric") != SELECTION_METRIC:
        errors.append("selection_metric_tampered")
    if r.get("in_sample_selection_window") != ["2019-01-01",
                                               "2022-12-31"]:
        errors.append("in_sample_window_tampered")
    if r.get("out_of_sample_window") != ["2023-01-01", "2025-12-31"]:
        errors.append("out_of_sample_window_tampered")
    if r.get("bucket_selected_on_in_sample_window_only") is not True:
        errors.append("bucket_selection_window_discipline_weakened")
    if r.get("bucket_held_fixed_for_out_of_sample") is not True:
        errors.append("bucket_must_be_held_fixed_for_oos")
    if r.get("uses_no_price_condition") is not True \
            or r.get("uses_no_volume_condition") is not True \
            or r.get("uses_no_excursion_condition") is not True:
        errors.append("non_calendar_condition_leaked_into_trigger")
    if r.get(
            "entry_rule_close_of_triggering_completed_daily_bar"
    ) is not True:
        errors.append("entry_rule_weakened")
    if r.get("entry_index_equals_trigger_index") is not True:
        errors.append("entry_must_be_at_trigger_bar_close")
    if r.get("no_intrabar_entry") is not True:
        errors.append("intrabar_entry_protection_weakened")
    if r.get("holding_horizon_bars") != 5:
        errors.append("holding_horizon_must_be_5")
    if r.get("fixed_horizon_exit_at_close") is not True:
        errors.append("fixed_horizon_exit_weakened")
    if r.get("atr_length") != 14:
        errors.append("atr_length_tampered")
    if r.get("atr_is_risk_control_only_never_entry_trigger") is not \
            True:
        errors.append("atr_role_weakened")
    if r.get("structure_stop_atr_multiplier") != 1.5:
        errors.append("structure_stop_multiplier_must_be_1_5")
    if r.get("stop_price_formula") != (
            "entry_price - STRUCTURE_STOP_ATR_MULTIPLIER * "
            "ATR14_at_entry_bar"):
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
    if r.get("anti_cluster_min_bar_gap") != 5:
        errors.append("anti_cluster_gap_must_be_5")
    if r.get("anti_cluster_tie_breaker") != (
            "keep_the_earlier_event_drop_the_later_one"):
        errors.append("anti_cluster_tie_breaker_tampered")
    if r.get("anti_cluster_does_not_consume_edit_token") is not True:
        errors.append("anti_cluster_must_not_consume_edit_token")
    if r.get("anti_cluster_applied_at") != (
            "label_emission_time_before_replay_non_overlap"):
        errors.append("anti_cluster_timing_tampered")
    if r.get("one_fire_per_iso_week_by_construction") is not True:
        errors.append("one_fire_per_iso_week_weakened")
    if r.get("sample_size_adequacy_threshold_min_accepted") != 100:
        errors.append("sample_size_threshold_must_be_100")
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
    if r.get(
            "single_trigger_design_does_not_consume_edit_token"
    ) is not True:
        errors.append(
            "single_trigger_design_must_not_consume_edit_token")
    if r.get("no_fetch_ever") is not True \
            or r.get("staged_data_never_modified") is not True \
            or r.get("no_real_time_data") is not True:
        errors.append("data_boundary_weakened")
    if list(r.get("detector_required_fields") or ()) != list(
            C10_SETUP_REQUIRED_FIELDS):
        errors.append("detector_required_fields_tampered")
    if list(r.get("detector_statuses") or ()) != list(
            C10_DETECTOR_STATUSES):
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
    if r.get("verdict") == VERDICT_C10D_READY and r.get("blockers"):
        errors.append("ready_with_blockers")
    return {"valid": not errors, "errors": errors}

"""SPARTA BREAKOUT-PULLBACK-STRUCTURE DETECTOR - DRY RUN (RESEARCH ONLY,
FIXTURE CANDLES ONLY). Candidate #2's first executable piece.

A deterministic scan of PROVIDED in-memory 15m candles implementing the
frozen strategy rules -- 20-bar range, >=10 bps breakout close with >=50%
body, retest within 15 bps of the level with depth <=61.8% of the leg,
25%-of-range failure rule, continuation close beyond the retest extreme,
structural-or-1.5xATR(14) stop whichever is WIDER -- with EVERY outcome
routed through the pushed label_bp_setup gate (closed 10-status set, 81 bps
floor checked at label time). No network, no files, no replay, no PnL, no
orders, no loop. Real staged candles are a future, separately approved run.
"""

from __future__ import annotations

from typing import Any

from sparta_commander.crypto_intraday_breakout_pullback_structure_detector_spec import (
    label_bp_setup,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_strategy_spec_contract import (
    ATR_PERIOD,
    ATR_STOP_MULTIPLIER,
    BREAKOUT_BODY_MIN_FRACTION,
    BREAKOUT_CLOSE_THRESHOLD_BPS,
    BREAKOUT_FAILURE_RANGE_FRACTION,
    MAX_PULLBACK_DEPTH_FRACTION,
    RANGE_LOOKBACK_BARS_15M,
    RETEST_TOLERANCE_BPS,
)

BPR_SCHEMA_VERSION = (
    "crypto_intraday_breakout_pullback_structure_detector_dry_run.v1")
BPR_LABEL = ("SPARTA Breakout-Pullback-Structure Detector Dry Run "
             "(RESEARCH ONLY, FIXTURE CANDLES ONLY)")
BPR_MODE = "RESEARCH_ONLY"
NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_BP_DETECTOR_DRY_RUN"

MIN_CANDLES = RANGE_LOOKBACK_BARS_15M + ATR_PERIOD + 6  # 40
_CANDLE_FIELDS = ("timestamp_utc", "open", "high", "low", "close")
_FORBIDDEN_KEY_TOKENS = ("order", "api_key", "credential", "wallet",
                         "account", "login", "fetch_url", "live_authorized",
                         "paper_authorized", "broker", "secret")


def get_bp_detector_dry_run_label() -> str:
    return BPR_LABEL


def _atr(candles: list, end_index: int) -> float | None:
    """Mean true range of the ATR_PERIOD bars ending BEFORE end_index."""
    if end_index < ATR_PERIOD + 1:
        return None
    total = 0.0
    for j in range(end_index - ATR_PERIOD, end_index):
        previous_close = candles[j - 1]["close"]
        total += max(candles[j]["high"] - candles[j]["low"],
                     abs(candles[j]["high"] - previous_close),
                     abs(candles[j]["low"] - previous_close))
    return total / ATR_PERIOD


def run_bp_detector_dry_run(symbol: Any, session_date: Any,
                            candles: Any) -> dict[str, Any]:
    """ONE deterministic dry-run detection over fixture 15m candles. Pure.
    Returns the FIRST setup attempt's label (accepted or rejected)."""
    base = {"setup_id": "%s_%s_bp_dry_run" % (symbol, session_date),
            "symbol": symbol, "session_date": session_date,
            "direction": "long"}

    if not isinstance(candles, list) or len(candles) < MIN_CANDLES:
        return label_bp_setup(dict(base, sufficient_candles=False))
    for candle in candles:
        if not isinstance(candle, dict) or not all(
                field in candle for field in _CANDLE_FIELDS):
            return label_bp_setup(dict(base, sufficient_candles=False))
        for key in candle:
            lowered = str(key).lower()
            for token in _FORBIDDEN_KEY_TOKENS:
                if token in lowered:
                    return label_bp_setup(dict(base, **{str(key): "x"}))

    threshold = BREAKOUT_CLOSE_THRESHOLD_BPS / 10000.0
    retest_tol = RETEST_TOLERANCE_BPS / 10000.0

    # FIRST close beyond the rolling 20-bar range decides the attempt.
    breakout_index = None
    direction = None
    range_high = range_low = None
    for i in range(RANGE_LOOKBACK_BARS_15M, len(candles)):
        window = candles[i - RANGE_LOOKBACK_BARS_15M:i]
        high = max(c["high"] for c in window)
        low = min(c["low"] for c in window)
        if candles[i]["close"] > high * (1 + threshold):
            breakout_index, direction = i, "long"
            range_high, range_low = high, low
            break
        if candles[i]["close"] < low * (1 - threshold):
            breakout_index, direction = i, "short"
            range_high, range_low = high, low
            break
    if breakout_index is None:
        return label_bp_setup(dict(
            base, sufficient_candles=True, breakout_present=False))

    b = candles[breakout_index]
    sign = 1.0 if direction == "long" else -1.0
    level = range_high if direction == "long" else range_low
    range_height = range_high - range_low
    candle_range = b["high"] - b["low"]
    body_ratio = (abs(b["close"] - b["open"]) / candle_range
                  if candle_range > 0 else 0.0)
    distance_bps = abs(b["close"] - level) / level * 10000.0
    observation: dict[str, Any] = dict(
        base, direction=direction, sufficient_candles=True,
        breakout_present=True,
        range_high=range_high, range_low=range_low,
        breakout_time=b["timestamp_utc"], breakout_level=level,
        breakout_direction=direction, breakout_close=b["close"],
        breakout_distance_bps=round(distance_bps, 6),
        breakout_body_ratio=round(body_ratio, 6))
    if body_ratio < BREAKOUT_BODY_MIN_FRACTION:
        observation["breakout_strong"] = False
        return label_bp_setup(observation)
    observation["breakout_strong"] = True

    failure_level = (level - sign * BREAKOUT_FAILURE_RANGE_FRACTION
                     * range_height)
    leg_origin = range_low if direction == "long" else range_high
    extreme = b["high"] if direction == "long" else b["low"]
    pullback_index = None
    for i in range(breakout_index + 1, len(candles)):
        c = candles[i]
        if (sign * (c["close"] - failure_level)) < 0:  # breakout failure
            observation.update(pullback_present=True, retest_pass=False,
                               pullback_time=c["timestamp_utc"],
                               pullback_level=level)
            return label_bp_setup(observation)
        extreme = (max(extreme, c["high"]) if direction == "long"
                   else min(extreme, c["low"]))
        touch = (c["low"] <= level * (1 + retest_tol)
                 if direction == "long"
                 else c["high"] >= level * (1 - retest_tol))
        if touch:
            pullback_index = i
            break
    if pullback_index is None:
        observation["pullback_present"] = False
        return label_bp_setup(observation)
    p = candles[pullback_index]
    pull_extreme = p["low"] if direction == "long" else p["high"]
    leg = abs(extreme - leg_origin)
    depth_ratio = (abs(extreme - pull_extreme) / leg if leg > 0 else 1.0)
    observation.update(pullback_present=True,
                       pullback_time=p["timestamp_utc"],
                       pullback_level=pull_extreme,
                       pullback_depth_ratio=round(depth_ratio, 6))
    if depth_ratio > MAX_PULLBACK_DEPTH_FRACTION:
        observation["retest_pass"] = False
        return label_bp_setup(observation)
    observation["retest_pass"] = True

    continuation_index = None
    for i in range(pullback_index + 1, len(candles)):
        c = candles[i]
        if (sign * (c["close"] - failure_level)) < 0:
            break  # failure before continuation
        beyond = (c["close"] > p["high"] if direction == "long"
                  else c["close"] < p["low"])
        if beyond:
            continuation_index = i
            break
    if continuation_index is None:
        observation["continuation_confirmed"] = False
        return label_bp_setup(observation)
    c2 = candles[continuation_index]
    observation.update(
        continuation_confirmed=True,
        continuation_time=c2["timestamp_utc"],
        continuation_close=c2["close"],
        structure_confirmation_reference=(
            "%s close %.8g beyond retest candle extreme %.8g forming a "
            "%s versus the pullback extreme"
            % (direction, c2["close"],
               p["high"] if direction == "long" else p["low"],
               "higher low" if direction == "long" else "lower high")))

    atr = _atr(candles, continuation_index)
    if atr is None:
        return label_bp_setup(dict(base, sufficient_candles=False))
    entry = c2["close"]
    structural_stop = pull_extreme
    atr_stop = entry - sign * ATR_STOP_MULTIPLIER * atr
    if direction == "long":
        selected = min(structural_stop, atr_stop)  # wider = lower
    else:
        selected = max(structural_stop, atr_stop)  # wider = higher
    stop_model = ("structural_swing" if selected == structural_stop
                  else "atr_1_5x")
    risk = abs(entry - selected)
    observation.update(
        atr_14_15m=round(atr, 8),
        structural_stop_price=round(structural_stop, 8),
        atr_stop_price=round(atr_stop, 8),
        selected_stop_price=round(selected, 8),
        stop_model=stop_model,
        entry_price=round(entry, 8),
        target_2r_price=round(entry + sign * 2.0 * risk, 8),
        target_3r_price=round(entry + sign * 3.0 * risk, 8),
        target_4r_price=round(entry + sign * 4.0 * risk, 8))
    return label_bp_setup(observation)

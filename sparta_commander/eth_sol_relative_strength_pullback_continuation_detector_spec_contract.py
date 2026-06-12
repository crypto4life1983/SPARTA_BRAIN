"""SPARTA CANDIDATE #5 DETECTOR SPEC + SYNTHETIC DRY-RUN PATH (READ-ONLY,
RESEARCH ONLY): ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION_V1.

Loop stage: detector_and_label_review. Pure deterministic scanner
functions implementing the pushed Candidate #5 spec numerics EXACTLY:
20-bar RS gate, 20-bar up-leg, 2-6 bar shallow pullback (<=38.2 percent
of the up-leg, low above the leg low), first-close-above trigger with RS
still passing, max(1.5xATR14, structure) WIDER stop, 27 bps fees with
the 81 bps gross target-distance floor evaluated PER VARIANT at label
time, 2R/3R/4R only, and per-variant same-symbol non-overlap that can
only remove trades.

PURITY LAW: inputs are in-memory candle rows supplied by callers/tests.
No file I/O, no network, no real dataset reads, fully deterministic, no
wall-clock behavior, no module-level runner, no order/account/trading
capability. The dry run uses ONLY in-memory synthetic fixtures -- no
real candle is read until the separately human-approved real-run gate.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
from sparta_commander.eth_sol_relative_strength_pullback_continuation_spec_review_contract import (
    VERDICT_C5S_READY,
    build_candidate_5_spec_review,
)

C5D_SCHEMA_VERSION = (
    "eth_sol_relative_strength_pullback_continuation_detector_spec.v1")
C5D_LABEL = ("SPARTA Candidate #5 Detector Spec + Dry-Run Path "
             "(READ-ONLY, RESEARCH ONLY, PURE FUNCTIONS, SYNTHETIC "
             "FIXTURES ONLY, NOT A RESCUE)")
C5D_MODE = "RESEARCH_ONLY"
VERDICT_C5D_READY = "CANDIDATE_5_DETECTOR_SPEC_READY"
VERDICT_C5D_BLOCKED = "CANDIDATE_5_DETECTOR_SPEC_BLOCKED"
VERDICT_C5D_DRY_RUN_PASSED = "CANDIDATE_5_DETECTOR_DRY_RUN_PASSED"
VERDICT_C5D_DRY_RUN_FAILED = "CANDIDATE_5_DETECTOR_DRY_RUN_FAILED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_5_DRY_RUN_REVIEW"

SYMBOLS = ("ETHUSD", "SOLUSD")
TIMEFRAME = "1h"
DIRECTION = "long"
RS_LOOKBACK_BARS = 20
PULLBACK_MIN_BARS = 2
PULLBACK_MAX_BARS = 6
MAX_PULLBACK_DEPTH_FRACTION = 0.382
ATR_LENGTH = 14
ATR_MULTIPLIER = 1.5
FEE_ROUND_TRIP_BPS = 27.0
TARGET_DISTANCE_FLOOR_BPS = 81.0
TARGET_VARIANTS = (("2r", 2.0), ("3r", 3.0), ("4r", 4.0))

C5_SETUP_REQUIRED_FIELDS = (
    "setup_id", "symbol", "timeframe", "direction", "trigger_time",
    "entry_price", "pullback_low", "pullback_high", "up_leg_low",
    "up_leg_high", "up_leg_size", "return_20_symbol", "return_20_other",
    "atr14", "stop_distance", "stop_price", "target_2r", "target_3r",
    "target_4r", "target_distance_bps_2r", "target_distance_bps_3r",
    "target_distance_bps_4r", "geometry_floor_pass_by_variant",
    "replay_start_time", "accepted_for_labeling_by_variant", "status",
    "rejection_reasons",
)

C5_DETECTOR_STATUSES = (
    "accepted_for_replay_review",
    "rejected_rs_not_positive",
    "rejected_rs_not_stronger",
    "rejected_pullback_too_short",
    "rejected_pullback_too_long",
    "rejected_pullback_too_deep",
    "rejected_pullback_below_up_leg_low",
    "rejected_geometry_floor",
    "rejected_invalid_geometry",
)


def get_candidate_5_detector_label() -> str:
    return C5D_LABEL


# --- pure numeric primitives ------------------------------------------------

def compute_return_20(bars: list, t: int) -> float | None:
    """return_20 = close[t] / close[t-20] - 1; completed bars only."""
    if t < RS_LOOKBACK_BARS or t >= len(bars):
        return None
    base = float(bars[t - RS_LOOKBACK_BARS]["close"])
    if base <= 0:
        return None
    return float(bars[t]["close"]) / base - 1.0


def rs_gate(bars_symbol: list, bars_other: list, t: int) -> dict[str, Any]:
    """The required entry gate: symbol return_20 positive AND strictly
    greater than the other symbol's. Pure; no future bars."""
    return_symbol = compute_return_20(bars_symbol, t)
    return_other = compute_return_20(bars_other, t)
    result = {"return_20_symbol": return_symbol,
              "return_20_other": return_other,
              "positive": False, "stronger": False, "passes": False}
    if return_symbol is None or return_other is None:
        return result
    result["positive"] = return_symbol > 0
    result["stronger"] = return_symbol > return_other
    result["passes"] = result["positive"] and result["stronger"]
    return result


def compute_atr14(bars: list, end_index: int) -> float | None:
    """Standard true range mean over the 14 completed bars ending at
    end_index; requires a prior close for every bar used."""
    if end_index < ATR_LENGTH or end_index >= len(bars):
        return None
    true_ranges = []
    for i in range(end_index - ATR_LENGTH + 1, end_index + 1):
        bar = bars[i]
        prev_close = float(bars[i - 1]["close"])
        true_ranges.append(max(
            float(bar["high"]) - float(bar["low"]),
            abs(float(bar["high"]) - prev_close),
            abs(float(bar["low"]) - prev_close)))
    return sum(true_ranges) / float(ATR_LENGTH)


def compute_stop(entry_price: float, pullback_low: float,
                 atr14: float) -> dict[str, Any]:
    """WIDER-stop rule: stop_distance = max(1.5*atr, entry - pullback
    low). Invalid if distance <= 0 or stop not below entry."""
    atr_stop_distance = ATR_MULTIPLIER * float(atr14)
    structure_stop_distance = float(entry_price) - float(pullback_low)
    stop_distance = max(atr_stop_distance, structure_stop_distance)
    stop_price = float(entry_price) - stop_distance
    valid = stop_distance > 0 and stop_price < float(entry_price)
    return {"atr_stop_distance": atr_stop_distance,
            "structure_stop_distance": structure_stop_distance,
            "stop_distance": stop_distance, "stop_price": stop_price,
            "valid": valid}


def geometry_floor_by_variant(entry_price: float,
                              stop_distance: float) -> dict[str, Any]:
    """Per-variant 81 bps gross target-distance floor at label time.
    target_distance = r_multiple * stop_distance; bps vs entry. No maker
    rebate, no zero-fee assumption."""
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


def apply_same_symbol_non_overlap(rows: list, variant: str) -> dict[str, Any]:
    """Per-variant same-symbol non-overlap/cooldown over rows that carry
    {symbol, trigger_time, exit_time_by_variant[variant]}. Greedy keep
    in trigger order; can only remove, never add. Pure."""
    kept, removed = [], []
    symbols = sorted({row["symbol"] for row in rows})
    for sym in symbols:
        last_exit = None
        for row in sorted((r for r in rows if r["symbol"] == sym),
                          key=lambda r: r["trigger_time"]):
            if last_exit is not None and row["trigger_time"] < last_exit:
                removed.append(row)
                continue
            kept.append(row)
            last_exit = row["exit_time_by_variant"][variant]
    assert len(kept) + len(removed) == len(rows)
    assert len(kept) <= len(rows)  # reduce-or-keep, never add
    return {"kept": kept, "removed": removed}


# --- the deterministic scanner ----------------------------------------------

def _reject(record: dict, status: str, reason: str) -> dict:
    record["status"] = status
    record["rejection_reasons"].append(reason)
    return record


def scan_c5_setups(bars_symbol: list, bars_other: list,
                   symbol: str) -> list[dict[str, Any]]:
    """THE Candidate #5 scanner. Inputs are aligned in-memory 1h candle
    rows ({time_utc, open, high, low, close}) for the traded symbol and
    the other symbol. One attempt per consumed up-leg-high; no future
    pullback extension after a trigger. Pure; labels only."""
    if symbol not in SYMBOLS:
        raise ValueError("symbol_outside_candidate_5_scope:" + str(symbol))
    n = len(bars_symbol)
    setups: list[dict[str, Any]] = []
    consumed_highs: set[int] = set()
    for t in range(RS_LOOKBACK_BARS, n):
        window_start = t - RS_LOOKBACK_BARS
        # locate the up-leg high BAR among completed bars before t
        # (last occurrence of the max high in t-20 .. t-1)
        high_index = None
        high_value = None
        for i in range(window_start, t):
            bar_high = float(bars_symbol[i]["high"])
            if high_value is None or bar_high >= high_value:
                high_value = bar_high
                high_index = i
        if high_index is None or high_index in consumed_highs:
            continue
        pullback_bars = bars_symbol[high_index + 1:t]
        count = len(pullback_bars)
        if count < 1:
            continue
        pullback_high = max(float(b["high"]) for b in pullback_bars)
        pullback_low = min(float(b["low"]) for b in pullback_bars)
        triggered = float(bars_symbol[t]["close"]) > pullback_high
        too_long_now = count > PULLBACK_MAX_BARS
        if not triggered and not too_long_now:
            continue  # structure still forming; no attempt yet
        consumed_highs.add(high_index)
        # frozen value definitions over t-20 through t
        up_leg_low = min(float(bars_symbol[i]["low"])
                         for i in range(window_start, t + 1))
        up_leg_high = max(float(bars_symbol[i]["high"])
                          for i in range(window_start, t + 1))
        up_leg_size = up_leg_high - up_leg_low
        gate = rs_gate(bars_symbol, bars_other, t)
        record: dict[str, Any] = {
            field: None for field in C5_SETUP_REQUIRED_FIELDS}
        record.update({
            "setup_id": "%s_%s" % (symbol, bars_symbol[t]["time_utc"]),
            "symbol": symbol, "timeframe": TIMEFRAME,
            "direction": DIRECTION,
            "trigger_time": bars_symbol[t]["time_utc"],
            "pullback_low": pullback_low, "pullback_high": pullback_high,
            "up_leg_low": up_leg_low, "up_leg_high": up_leg_high,
            "up_leg_size": up_leg_size,
            "return_20_symbol": gate["return_20_symbol"],
            "return_20_other": gate["return_20_other"],
            "rejection_reasons": [],
            "replay_start_time": (bars_symbol[t + 1]["time_utc"]
                                  if t + 1 < n else None),
        })
        if too_long_now:
            setups.append(_reject(record, "rejected_pullback_too_long",
                                  "pullback_exceeded_6_bars_without"
                                  "_trigger"))
            continue
        if count < PULLBACK_MIN_BARS:
            setups.append(_reject(record, "rejected_pullback_too_short",
                                  "pullback_below_2_bars"))
            continue
        if up_leg_size <= 0:
            setups.append(_reject(record, "rejected_invalid_geometry",
                                  "up_leg_size_not_positive"))
            continue
        if not gate["positive"]:
            setups.append(_reject(record, "rejected_rs_not_positive",
                                  "return_20_not_positive"))
            continue
        if not gate["stronger"]:
            setups.append(_reject(record, "rejected_rs_not_stronger",
                                  "return_20_not_above_other_symbol"))
            continue
        depth = up_leg_high - pullback_low
        if depth <= 0:
            setups.append(_reject(record, "rejected_invalid_geometry",
                                  "pullback_depth_not_positive"))
            continue
        if pullback_low <= up_leg_low:
            setups.append(_reject(
                record, "rejected_pullback_below_up_leg_low",
                "pullback_low_not_above_up_leg_low"))
            continue
        if depth > MAX_PULLBACK_DEPTH_FRACTION * up_leg_size:
            setups.append(_reject(record, "rejected_pullback_too_deep",
                                  "depth_above_38_2_pct_of_up_leg"))
            continue
        entry = float(bars_symbol[t]["close"])
        record["entry_price"] = entry
        atr = compute_atr14(bars_symbol, t)
        if atr is None or atr <= 0:
            setups.append(_reject(record, "rejected_invalid_geometry",
                                  "atr_unavailable_or_not_positive"))
            continue
        record["atr14"] = round(atr, 6)
        stop = compute_stop(entry, pullback_low, atr)
        if not stop["valid"]:
            setups.append(_reject(record, "rejected_invalid_geometry",
                                  "stop_distance_not_positive_or_stop"
                                  "_not_below_entry"))
            continue
        record["stop_distance"] = round(stop["stop_distance"], 6)
        record["stop_price"] = round(stop["stop_price"], 6)
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
            setups.append(_reject(record, "rejected_invalid_geometry",
                                  "no_next_bar_for_evaluation"))
            continue
        if not floor["any_variant_passes"]:
            setups.append(_reject(record, "rejected_geometry_floor",
                                  "all_variant_target_distances_below"
                                  "_81_bps"))
            continue
        record["status"] = "accepted_for_replay_review"
        setups.append(record)
    return setups


# --- synthetic fixtures (in-memory only) -------------------------------------

def _stamp(index: int) -> str:
    return "2026-03-0%dT%02d:00:00Z" % (1 + index // 24, index % 24)


def _bar(index: int, open_: float, high: float, low: float,
         close: float) -> dict[str, Any]:
    return {"time_utc": _stamp(index), "open": open_, "high": high,
            "low": low, "close": close}


def fixture_flat_other(length: int = 32) -> list:
    return [_bar(i, 50.0, 50.05, 49.95, 50.0) for i in range(length)]


def fixture_accepted() -> list:
    bars = []
    for i in range(22):
        close = 100.0 + 0.5 * i
        bars.append(_bar(i, close - 0.2, close + 0.3, close - 0.4, close))
    bars.append(_bar(22, 110.5, 110.6, 109.6, 109.8))
    bars.append(_bar(23, 109.8, 110.0, 109.2, 109.4))
    bars.append(_bar(24, 109.4, 109.6, 108.9, 109.1))   # pullback low
    bars.append(_bar(25, 109.1, 110.75, 109.0, 110.7))  # trigger close
    bars.append(_bar(26, 110.5, 110.6, 110.0, 110.1))
    bars.append(_bar(27, 110.1, 110.2, 109.7, 109.8))
    bars.append(_bar(28, 109.8, 109.9, 109.4, 109.5))
    bars.append(_bar(29, 109.5, 109.6, 109.1, 109.2))
    return bars


def fixture_too_deep() -> list:
    bars = fixture_accepted()
    bars[24] = _bar(24, 109.4, 109.6, 107.0, 109.1)  # depth 3.8 > 38.2%
    return bars


def fixture_below_leg_low() -> list:
    bars = fixture_accepted()
    bars[24] = _bar(24, 109.4, 109.6, 102.0, 109.1)  # below up_leg_low
    return bars


def fixture_too_short() -> list:
    bars = fixture_accepted()
    # bar 23 closes above the bar-22 high (one-bar pullback) while its
    # own high stays below the up-leg high, so no new swing is created
    bars[23] = _bar(23, 109.8, 110.75, 109.5, 110.7)
    return bars


def fixture_too_long() -> list:
    bars = []
    for i in range(22):
        close = 100.0 + 0.5 * i
        bars.append(_bar(i, close - 0.2, close + 0.3, close - 0.4, close))
    drift = (109.8, 109.6, 109.4, 109.3, 109.2, 109.1, 109.0)
    for offset, close in enumerate(drift):  # 7 bars, never close above
        bars.append(_bar(22 + offset, close + 0.1, close + 0.2,
                         close - 0.3, close))
    bars.append(_bar(29, 109.0, 109.1, 108.8, 108.9))
    return bars


def fixture_no_trigger_intrabar_high_only() -> list:
    bars = fixture_accepted()
    # high pierces the pullback high but the CLOSE stays below it
    bars[25] = _bar(25, 109.1, 111.0, 109.0, 110.5)
    bars[26] = _bar(26, 110.5, 110.55, 109.9, 110.0)
    bars[27] = _bar(27, 110.0, 110.1, 109.6, 109.7)
    bars[28] = _bar(28, 109.7, 109.8, 109.3, 109.4)
    bars[29] = _bar(29, 109.4, 109.5, 109.0, 109.1)
    return bars


def fixture_rs_stronger_other(length: int = 32) -> list:
    return [_bar(i, 50.0 + 0.8 * i, 50.1 + 0.8 * i, 49.9 + 0.8 * i,
                 50.0 + 0.8 * i) for i in range(length)]


def fixture_tight_floor() -> list:
    bars = []
    for i in range(22):
        close = 109.6 + 0.05 * i
        bars.append(_bar(i, close - 0.02, close + 0.05, close - 0.06,
                         close))
    bars.append(_bar(22, 110.65, 110.66, 110.45, 110.5))
    bars.append(_bar(23, 110.5, 110.55, 110.37, 110.42))
    bars.append(_bar(24, 110.42, 110.69, 110.4, 110.68))  # trigger
    bars.append(_bar(25, 110.68, 110.7, 110.5, 110.6))
    return bars


def run_c5_detector_dry_run() -> dict[str, Any]:
    """Run the scanner over IN-MEMORY synthetic fixtures only and check
    the expected outcomes. Reads no files; never sees real candles."""
    record: dict[str, Any] = {
        "schema_version": C5D_SCHEMA_VERSION, "label": C5D_LABEL,
        "mode": C5D_MODE, "verdict": None, "failures": [],
        "fixtures": {}, "uses_synthetic_fixtures_only": True,
        "reads_real_candles": False, "reads_any_files": False,
    }
    failures = record["failures"]
    flat = fixture_flat_other()

    def _check(name, bars_symbol, bars_other, symbol,
               expected_statuses):
        setups = scan_c5_setups(bars_symbol, bars_other, symbol)
        statuses = sorted(s["status"] for s in setups)
        record["fixtures"][name] = {
            "attempts": len(setups), "statuses": statuses,
            "accepted": sum(1 for s in setups
                            if s["status"] == "accepted_for_replay"
                            "_review")}
        if statuses != sorted(expected_statuses):
            failures.append("%s_expected_%s_got_%s" % (
                name, expected_statuses, statuses))
        return setups

    eth = _check("eth_accepted", fixture_accepted(), flat, "ETHUSD",
                 ["accepted_for_replay_review"])
    if eth and eth[0]["status"] == "accepted_for_replay_review":
        winner = eth[0]
        record["fixtures"]["eth_accepted"]["entry"] = (
            winner["entry_price"])
        record["fixtures"]["eth_accepted"]["stop_distance"] = (
            winner["stop_distance"])
        if winner["entry_price"] != 110.7:
            failures.append("eth_accepted_wrong_entry")
        if winner["stop_price"] != 108.9:
            failures.append("eth_accepted_wrong_stop")
        if winner["replay_start_time"] != _stamp(26):
            failures.append("eth_accepted_wrong_replay_start")
        if winner["geometry_floor_pass_by_variant"] != {
                "2r": True, "3r": True, "4r": True}:
            failures.append("eth_accepted_floor_unexpected")
    _check("sol_accepted", fixture_accepted(), flat, "SOLUSD",
           ["accepted_for_replay_review"])
    _check("rs_not_stronger", fixture_accepted(),
           fixture_rs_stronger_other(), "ETHUSD",
           ["rejected_rs_not_stronger"])
    _check("pullback_too_short", fixture_too_short(), flat, "ETHUSD",
           ["rejected_pullback_too_short"])
    _check("pullback_too_long", fixture_too_long(), flat, "ETHUSD",
           ["rejected_pullback_too_long"])
    _check("pullback_too_deep", fixture_too_deep(), flat, "ETHUSD",
           ["rejected_pullback_too_deep"])
    _check("pullback_below_leg_low", fixture_below_leg_low(), flat,
           "ETHUSD", ["rejected_pullback_below_up_leg_low"])
    _check("no_trigger_intrabar_only",
           fixture_no_trigger_intrabar_high_only(), flat, "ETHUSD", [])
    tight = _check("tight_floor_partial", fixture_tight_floor(), flat,
                   "ETHUSD", ["accepted_for_replay_review"])
    if tight and tight[0]["status"] == "accepted_for_replay_review":
        floor_pass = tight[0]["geometry_floor_pass_by_variant"]
        record["fixtures"]["tight_floor_partial"]["floor_pass"] = (
            floor_pass)
        if floor_pass["2r"] is not False:
            failures.append("tight_floor_2r_should_fail_81bps")
        if floor_pass["3r"] is not True or floor_pass["4r"] is not True:
            failures.append("tight_floor_3r_4r_should_pass")
    record["verdict"] = (VERDICT_C5D_DRY_RUN_PASSED if not failures
                         else VERDICT_C5D_DRY_RUN_FAILED)
    return record


def build_c5_detector_spec_contract() -> dict[str, Any]:
    """Assemble the detector spec contract, gated on the pushed
    Candidate #5 spec review (itself chain-gated) and the loop."""
    record: dict[str, Any] = {
        "schema_version": C5D_SCHEMA_VERSION, "label": C5D_LABEL,
        "mode": C5D_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,
        "direction": "long_only",
        "rs_lookback_bars": RS_LOOKBACK_BARS,
        "pullback_min_bars": PULLBACK_MIN_BARS,
        "pullback_max_bars": PULLBACK_MAX_BARS,
        "max_pullback_depth_fraction": MAX_PULLBACK_DEPTH_FRACTION,
        "atr_length": ATR_LENGTH, "atr_multiplier": ATR_MULTIPLIER,
        "wider_stop_rule": "max(atr_stop_distance, structure_stop"
                           "_distance)",
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "floor_applies_per_variant_at_label_time": True,
        "no_maker_rebate_no_zero_fee": True,
        "target_variants": [name for name, _m in TARGET_VARIANTS],
        "non_overlap_same_symbol_per_variant_reduce_only": True,
        "replay_starts_next_bar_after_trigger_close": True,
        "setup_required_fields": list(C5_SETUP_REQUIRED_FIELDS),
        "detector_statuses": list(C5_DETECTOR_STATUSES),
        "dry_run_uses_synthetic_fixtures_only": True,
        "future_real_run_data_source":
            "existing staged 15m candles aggregated to 1h by the pushed "
            "aggregators (separate human approval required before any "
            "real run)",
        "current_loop_stage": "detector_and_label_review",
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "executes": False, "writes_files": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "uses_account": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False, "starts_scheduler": False,
        "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    spec = build_candidate_5_spec_review()
    if spec["verdict"] != VERDICT_C5S_READY:
        record["verdict"] = VERDICT_C5D_BLOCKED
        record["blockers"].append("candidate_5_spec_not_certifying")
        record["blockers"].extend(spec["blockers"])
        return record
    loop_contract = _loop.build_autopilot_loop_contract()
    if loop_contract["verdict"] != _loop.VERDICT_AP_READY:
        record["verdict"] = VERDICT_C5D_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C5D_READY
    return record


def validate_c5_detector_spec_contract(record: Any) -> dict[str, Any]:
    """Validate shape, frozen numerics, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C5D_READY, VERDICT_C5D_BLOCKED):
        errors.append("bad_verdict")
    if r.get("symbols") != ["ETHUSD", "SOLUSD"]:
        errors.append("symbols_tampered")
    if r.get("timeframe") != "1h" or r.get("direction") != "long_only":
        errors.append("timeframe_or_direction_tampered")
    if r.get("rs_lookback_bars") != 20:
        errors.append("rs_lookback_tampered")
    if r.get("pullback_min_bars") != 2 \
            or r.get("pullback_max_bars") != 6:
        errors.append("pullback_length_tampered")
    if r.get("max_pullback_depth_fraction") != 0.382:
        errors.append("pullback_depth_tampered")
    if r.get("atr_length") != 14:
        errors.append("atr_length_tampered")
    if r.get("atr_multiplier") != 1.5:
        errors.append("atr_multiplier_tampered")
    if r.get("wider_stop_rule") != (
            "max(atr_stop_distance, structure_stop_distance)"):
        errors.append("wider_stop_rule_tampered")
    if r.get("fee_round_trip_bps") != 27.0:
        errors.append("fee_bps_tampered")
    if r.get("target_distance_floor_bps") != 81.0:
        errors.append("floor_81bps_tampered")
    if r.get("floor_applies_per_variant_at_label_time") is not True:
        errors.append("floor_application_weakened")
    if r.get("no_maker_rebate_no_zero_fee") is not True:
        errors.append("fee_assumptions_weakened")
    if r.get("target_variants") != ["2r", "3r", "4r"]:
        errors.append("target_variants_tampered")
    if r.get(
            "non_overlap_same_symbol_per_variant_reduce_only") is not \
            True:
        errors.append("non_overlap_rule_weakened")
    if r.get("replay_starts_next_bar_after_trigger_close") is not True:
        errors.append("replay_start_rule_weakened")
    if tuple(r.get("setup_required_fields") or ()) != (
            C5_SETUP_REQUIRED_FIELDS):
        errors.append("setup_schema_tampered")
    if tuple(r.get("detector_statuses") or ()) != C5_DETECTOR_STATUSES:
        errors.append("statuses_tampered")
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
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}

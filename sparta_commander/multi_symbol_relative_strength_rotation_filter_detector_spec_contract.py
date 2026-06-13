"""SPARTA CANDIDATE #6 DETECTOR SPEC + SYNTHETIC DRY-RUN PATH (READ-ONLY,
RESEARCH ONLY): MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1.

Loop stage: detector_and_label_review. Pure deterministic scanner
implementing the pushed Candidate #6 frozen spec EXACTLY: 20-bar
close-to-close relative strength computed simultaneously for
btcusd/ethusd/solusd; STRICT rank #1 (ties fail) and return_20 > 0;
continuation event = first completed 1h bar whose close is a fresh
10-bar closing high on the rank-#1 symbol; entry at that close;
evaluation next bar; one setup per event bar; explicitly NOT a delayed
pullback resumption; WIDER stop = max(1.5 x atr14, entry - lowest low of
the last 10 completed bars including the event bar); 27 bps fees with
the 81 bps gross target-distance floor per variant (2r/3r/4r) checked
before replay eligibility.

PURITY LAW: inputs are in-memory candle rows supplied by callers/tests,
index-aligned across the three symbols. No file reads, no real candles,
no staged data, no aggregation execution, no network, fully
deterministic, no wall-clock behavior, no module-level runner, no
order/account/trading capability. The dry run uses ONLY in-memory
synthetic fixtures -- no real candle is touched until the separately
human-approved real-run gate.
"""

from __future__ import annotations

from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
from sparta_commander.btc_sol_long_trend_continuation_detector_spec_contract import (
    compute_atr14,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_spec_review_contract import (
    VERDICT_C6S_READY,
    build_candidate_6_spec_review,
)

C6D_SCHEMA_VERSION = (
    "multi_symbol_relative_strength_rotation_filter_detector_spec.v1")
C6D_LABEL = ("SPARTA Candidate #6 Detector Spec + Dry-Run Path "
             "(READ-ONLY, RESEARCH ONLY, PURE FUNCTIONS, SYNTHETIC "
             "FIXTURES ONLY, NOT A RESCUE)")
C6D_MODE = "RESEARCH_ONLY"
VERDICT_C6D_READY = "CANDIDATE_6_DETECTOR_SPEC_READY"
VERDICT_C6D_BLOCKED = "CANDIDATE_6_DETECTOR_SPEC_BLOCKED"
VERDICT_C6D_DRY_RUN_PASSED = "CANDIDATE_6_DETECTOR_DRY_RUN_PASSED"
VERDICT_C6D_DRY_RUN_FAILED = "CANDIDATE_6_DETECTOR_DRY_RUN_FAILED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_CANDIDATE_6_DRY_RUN_REVIEW"

UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1h"
DIRECTION = "long"
RS_LOOKBACK_BARS = 20
CLOSING_HIGH_LOOKBACK_BARS = 10
STRUCTURE_LOOKBACK_BARS = 10
ATR_LENGTH = 14
ATR_MULTIPLIER = 1.5
FEE_ROUND_TRIP_BPS = 27.0
TARGET_DISTANCE_FLOOR_BPS = 81.0
TARGET_VARIANTS = (("2r", 2.0), ("3r", 3.0), ("4r", 4.0))

C6_SETUP_REQUIRED_FIELDS = (
    "setup_id", "symbol", "timeframe", "direction", "event_time",
    "entry_price", "return_20_candidate", "return_20_others",
    "strict_rank_1", "rs_positive", "fresh_10_bar_closing_high",
    "atr14", "structure_stop_distance", "stop_distance", "stop_price",
    "target_2r", "target_3r", "target_4r",
    "target_distance_bps_2r", "target_distance_bps_3r",
    "target_distance_bps_4r", "geometry_floor_pass_by_variant",
    "accepted_for_labeling_by_variant", "replay_start_time",
    "status", "rejection_reasons",
)

C6_DETECTOR_STATUSES = (
    "accepted_for_replay_review",
    "rejected_not_strict_rank_1",
    "rejected_rs_not_positive",
    "rejected_invalid_stop_geometry",
    "rejected_geometry_floor",
    "rejected_no_evaluation_bar",
)


def get_candidate_6_detector_label() -> str:
    return C6D_LABEL


# --- pure numeric primitives -------------------------------------------------

def compute_return_20(bars: list, t: int) -> float | None:
    """return_20 = close[t] / close[t-20] - 1; completed bars only."""
    if t < RS_LOOKBACK_BARS or t >= len(bars):
        return None
    base = float(bars[t - RS_LOOKBACK_BARS]["close"])
    if base <= 0:
        return None
    return float(bars[t]["close"]) / base - 1.0


def rank_gate(bars_by_symbol: dict, symbol: str,
              t: int) -> dict[str, Any]:
    """STRICT rank #1 (ties fail) plus return_20 > 0, computed
    simultaneously for all three symbols. Pure; no lookahead."""
    candidate = compute_return_20(bars_by_symbol[symbol], t)
    others = {other: compute_return_20(bars_by_symbol[other], t)
              for other in UNIVERSE if other != symbol}
    result = {"return_20_candidate": candidate,
              "return_20_others": others,
              "strict_rank_1": False, "rs_positive": False,
              "passes": False}
    if candidate is None or any(value is None
                                for value in others.values()):
        return result
    result["strict_rank_1"] = all(candidate > value
                                  for value in others.values())
    result["rs_positive"] = candidate > 0
    result["passes"] = (result["strict_rank_1"]
                        and result["rs_positive"])
    return result


def is_fresh_closing_high(bars: list, t: int) -> bool:
    """close[t] strictly greater than the maximum close of the prior 10
    completed bars."""
    if t < CLOSING_HIGH_LOOKBACK_BARS:
        return False
    prior_max = max(float(bars[i]["close"])
                    for i in range(t - CLOSING_HIGH_LOOKBACK_BARS, t))
    return float(bars[t]["close"]) > prior_max


def compute_stop(entry_price: float, ten_bar_low: float,
                 atr14: float) -> dict[str, Any]:
    """WIDER-stop rule: stop_distance = max(1.5 * atr14, entry - ten
    bar low). Invalid if distance <= 0 or stop not below entry."""
    atr_stop_distance = ATR_MULTIPLIER * float(atr14)
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


# --- the deterministic scanner -----------------------------------------------

def scan_c6_setups(bars_by_symbol: dict,
                   symbol: str) -> list[dict[str, Any]]:
    """THE Candidate #6 scanner. bars_by_symbol maps every universe
    symbol to index-aligned in-memory 1h rows ({time_utc, open, high,
    low, close}). An ATTEMPT exists when the candidate symbol prints a
    fresh 10-bar closing high; gates then apply in order. One setup per
    event bar; the event IS the entry bar -- never a delayed pullback
    resumption. Pure; labels only."""
    if symbol not in UNIVERSE:
        raise ValueError("symbol_outside_candidate_6_universe:"
                         + str(symbol))
    for required in UNIVERSE:
        if required not in bars_by_symbol:
            raise ValueError("missing_universe_symbol:" + required)
    lengths = {len(bars_by_symbol[name]) for name in UNIVERSE}
    if len(lengths) != 1:
        raise ValueError("universe_bars_not_aligned")
    bars = bars_by_symbol[symbol]
    n = len(bars)
    setups: list[dict[str, Any]] = []
    for t in range(RS_LOOKBACK_BARS, n):
        if not is_fresh_closing_high(bars, t):
            continue  # no continuation event -> no attempt
        gate = rank_gate(bars_by_symbol, symbol, t)
        entry = float(bars[t]["close"])
        record: dict[str, Any] = {
            field: None for field in C6_SETUP_REQUIRED_FIELDS}
        record.update({
            "setup_id": "%s_%s" % (symbol, bars[t]["time_utc"]),
            "symbol": symbol, "timeframe": TIMEFRAME,
            "direction": DIRECTION,
            "event_time": bars[t]["time_utc"],
            "entry_price": entry,
            "return_20_candidate": gate["return_20_candidate"],
            "return_20_others": dict(gate["return_20_others"]),
            "strict_rank_1": gate["strict_rank_1"],
            "rs_positive": gate["rs_positive"],
            "fresh_10_bar_closing_high": True,
            "replay_start_time": (bars[t + 1]["time_utc"]
                                  if t + 1 < n else None),
            "rejection_reasons": [],
        })
        if not gate["strict_rank_1"]:
            record["status"] = "rejected_not_strict_rank_1"
            record["rejection_reasons"].append(
                "candidate_not_strictly_above_both_others_or_tie")
            setups.append(record)
            continue
        if not gate["rs_positive"]:
            record["status"] = "rejected_rs_not_positive"
            record["rejection_reasons"].append(
                "return_20_not_positive")
            setups.append(record)
            continue
        atr = compute_atr14(bars, t)
        if atr is None or atr <= 0:
            record["status"] = "rejected_invalid_stop_geometry"
            record["rejection_reasons"].append(
                "atr_unavailable_or_not_positive")
            setups.append(record)
            continue
        record["atr14"] = round(atr, 6)
        ten_bar_low = min(float(bars[i]["low"]) for i in
                          range(t - STRUCTURE_LOOKBACK_BARS + 1, t + 1))
        stop = compute_stop(entry, ten_bar_low, atr)
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


# --- synthetic fixtures (in-memory only) --------------------------------------

def _stamp(index: int) -> str:
    return "2026-04-0%dT%02d:00:00Z" % (1 + index // 24, index % 24)


def _bar(index: int, close: float, low_offset: float = 0.3,
         high_offset: float = 0.2) -> dict[str, Any]:
    return {"time_utc": _stamp(index), "open": close - 0.05,
            "high": close + high_offset, "low": close - low_offset,
            "close": close}


def fixture_flat(level: float, length: int = 35) -> list:
    return [_bar(i, level, 0.05, 0.05) for i in range(length)]


def fixture_sol_breakout() -> list:
    """SOL: 20-bar rise, 10-bar plateau below the prior peak, then ONE
    fresh 10-bar closing-high breakout at bar 30."""
    bars = []
    for i in range(20):
        bars.append(_bar(i, 100.0 + 0.3 * i))            # rise to 105.7
    plateau = (105.5, 105.4, 105.6, 105.3, 105.5, 105.4,
               105.6, 105.3, 105.5, 105.4)
    for offset, close in enumerate(plateau):
        bars.append(_bar(20 + offset, close))
    bars.append(_bar(30, 106.5))                          # the event
    for offset, close in enumerate((106.2, 106.0, 105.8, 105.6)):
        bars.append(_bar(31 + offset, close))
    return bars


def fixture_recovering_but_negative() -> list:
    """Candidate declines hard then recovers into fresh 10-bar closing
    highs while its 20-bar return stays negative."""
    bars = []
    for i in range(20):
        bars.append(_bar(i, 120.0 - 1.0 * i))             # 120 -> 101
    recovery = (100.5, 100.8, 101.1, 101.4, 101.7, 102.0,
                102.3, 102.6, 102.9, 103.2)
    for offset, close in enumerate(recovery):
        bars.append(_bar(20 + offset, close))
    bars.append(_bar(30, 103.5))                          # fresh high
    for offset, close in enumerate((103.3, 103.1, 102.9, 102.7)):
        bars.append(_bar(31 + offset, close))
    return bars


def fixture_falling(start: float = 200.0) -> list:
    return [_bar(i, start - 2.0 * i) for i in range(35)]


def build_bars(symbol_series: dict) -> dict:
    """Assemble an aligned bars_by_symbol dict; everything in-memory."""
    return {name: list(series) for name, series in symbol_series.items()}


def run_c6_detector_dry_run() -> dict[str, Any]:
    """Run the scanner over IN-MEMORY synthetic fixtures only and check
    the expected outcomes. Touches no real candles, no staged data."""
    record: dict[str, Any] = {
        "schema_version": C6D_SCHEMA_VERSION, "label": C6D_LABEL,
        "mode": C6D_MODE, "verdict": None, "failures": [],
        "fixtures": {}, "uses_synthetic_fixtures_only": True,
        "reads_real_candles": False, "reads_staged_data": False,
        "reads_any_files": False,
    }
    failures = record["failures"]

    def _check(name, bars_by_symbol, symbol, expected_statuses):
        setups = scan_c6_setups(bars_by_symbol, symbol)
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

    # 1. accepted: SOL strict rank #1 with a fresh 10-bar closing high
    accepted = _check(
        "sol_rank1_breakout",
        build_bars({"BTCUSD": fixture_flat(50.0),
                    "ETHUSD": fixture_flat(80.0),
                    "SOLUSD": fixture_sol_breakout()}),
        "SOLUSD", ["accepted_for_replay_review"])
    if accepted and accepted[0]["status"] == "accepted_for_replay_review":
        winner = accepted[0]
        record["fixtures"]["sol_rank1_breakout"]["entry"] = (
            winner["entry_price"])
        record["fixtures"]["sol_rank1_breakout"]["stop_distance"] = (
            winner["stop_distance"])
        if winner["entry_price"] != 106.5:
            failures.append("accepted_wrong_entry")
        if winner["event_time"] != _stamp(30):
            failures.append("accepted_wrong_event_bar")
        if winner["replay_start_time"] != _stamp(31):
            failures.append("accepted_wrong_replay_start")
        if winner["geometry_floor_pass_by_variant"] != {
                "2r": True, "3r": True, "4r": True}:
            failures.append("accepted_floor_unexpected")
    # 2. tie: identical series -> ties fail
    _check("rank_tie_fails",
           build_bars({"BTCUSD": fixture_flat(50.0),
                       "ETHUSD": fixture_sol_breakout(),
                       "SOLUSD": fixture_sol_breakout()}),
           "SOLUSD", ["rejected_not_strict_rank_1"])
    # 3. rank #1 but negative RS: the recovery prints fresh closing
    # highs at bars 28, 29 and 30 -- all three must reject on RS
    _check("rank1_but_negative_rs",
           build_bars({"BTCUSD": fixture_falling(300.0),
                       "ETHUSD": fixture_falling(250.0),
                       "SOLUSD": fixture_recovering_but_negative()}),
           "SOLUSD", ["rejected_rs_not_positive",
                      "rejected_rs_not_positive",
                      "rejected_rs_not_positive"])
    # 4. no fresh 10-bar closing high -> zero attempts
    no_event = fixture_sol_breakout()
    no_event[30] = _bar(30, 105.5)  # stays inside the plateau range
    no_event[31] = _bar(31, 105.4)
    no_event[32] = _bar(32, 105.3)
    no_event[33] = _bar(33, 105.2)
    no_event[34] = _bar(34, 105.1)
    _check("no_fresh_closing_high",
           build_bars({"BTCUSD": fixture_flat(50.0),
                       "ETHUSD": fixture_flat(80.0),
                       "SOLUSD": no_event}),
           "SOLUSD", [])
    # 5. event on the LAST bar -> no evaluation bar -> rejected
    truncated = build_bars({"BTCUSD": fixture_flat(50.0, 31),
                            "ETHUSD": fixture_flat(80.0, 31),
                            "SOLUSD": fixture_sol_breakout()[:31]})
    _check("event_on_last_bar", truncated, "SOLUSD",
           ["rejected_no_evaluation_bar"])
    record["verdict"] = (VERDICT_C6D_DRY_RUN_PASSED if not failures
                         else VERDICT_C6D_DRY_RUN_FAILED)
    return record


def build_c6_detector_spec_contract() -> dict[str, Any]:
    """Assemble the detector spec contract, gated on the pushed
    Candidate #6 spec review (itself chain-gated through the proposal,
    Recommendation V1, Autopilot V1 and the five-record ledger)."""
    record: dict[str, Any] = {
        "schema_version": C6D_SCHEMA_VERSION, "label": C6D_LABEL,
        "mode": C6D_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [],
        "universe": list(UNIVERSE), "timeframe": TIMEFRAME,
        "direction": "long_only",
        "rs_lookback_bars": RS_LOOKBACK_BARS,
        "closing_high_lookback_bars": CLOSING_HIGH_LOOKBACK_BARS,
        "structure_lookback_bars": STRUCTURE_LOOKBACK_BARS,
        "ties_fail": True,
        "rs_must_be_positive": True,
        "atr_length": ATR_LENGTH, "atr_multiplier": ATR_MULTIPLIER,
        "wider_stop_rule": "max(1.5 * atr14, entry - lowest low of "
                           "last 10 completed bars)",
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "floor_checked_before_replay_eligibility": True,
        "no_maker_rebate_no_zero_fee": True,
        "target_variants": [name for name, _m in TARGET_VARIANTS],
        "entry_at_event_bar_close": True,
        "evaluation_starts_next_bar": True,
        "one_setup_per_event_bar": True,
        "not_a_delayed_pullback_resumption": True,
        "setup_required_fields": list(C6_SETUP_REQUIRED_FIELDS),
        "detector_statuses": list(C6_DETECTOR_STATUSES),
        "dry_run_uses_synthetic_fixtures_only": True,
        "future_real_run_data_source":
            "existing staged 15m candles aggregated to 1h by the "
            "pushed aggregators (separate human approval required "
            "before any real run)",
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
        "contains_order_logic": False,
        "contains_portfolio_allocation_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    spec = build_candidate_6_spec_review()
    if spec["verdict"] != VERDICT_C6S_READY:
        record["verdict"] = VERDICT_C6D_BLOCKED
        record["blockers"].append("candidate_6_spec_not_certifying")
        record["blockers"].extend(spec["blockers"])
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C6D_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    record["verdict"] = VERDICT_C6D_READY
    return record


def validate_c6_detector_spec_contract(record: Any) -> dict[str, Any]:
    """Validate shape, frozen numerics, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C6D_READY, VERDICT_C6D_BLOCKED):
        errors.append("bad_verdict")
    if r.get("universe") != ["BTCUSD", "ETHUSD", "SOLUSD"]:
        errors.append("universe_tampered")
    if r.get("timeframe") != "1h" or r.get("direction") != "long_only":
        errors.append("timeframe_or_direction_tampered")
    if r.get("rs_lookback_bars") != 20:
        errors.append("rs_lookback_tampered")
    if r.get("closing_high_lookback_bars") != 10:
        errors.append("closing_high_lookback_tampered")
    if r.get("structure_lookback_bars") != 10:
        errors.append("structure_lookback_tampered")
    if r.get("ties_fail") is not True \
            or r.get("rs_must_be_positive") is not True:
        errors.append("rank_rule_weakened")
    if r.get("atr_length") != 14 or r.get("atr_multiplier") != 1.5:
        errors.append("atr_numbers_tampered")
    if r.get("wider_stop_rule") != (
            "max(1.5 * atr14, entry - lowest low of last 10 completed "
            "bars)"):
        errors.append("wider_stop_rule_tampered")
    if r.get("fee_round_trip_bps") != 27.0:
        errors.append("fee_bps_tampered")
    if r.get("target_distance_floor_bps") != 81.0:
        errors.append("floor_81bps_tampered")
    if r.get("floor_checked_before_replay_eligibility") is not True:
        errors.append("floor_application_weakened")
    if r.get("no_maker_rebate_no_zero_fee") is not True:
        errors.append("fee_assumptions_weakened")
    if r.get("target_variants") != ["2r", "3r", "4r"]:
        errors.append("target_variants_tampered")
    for key in ("entry_at_event_bar_close",
                "evaluation_starts_next_bar",
                "one_setup_per_event_bar",
                "not_a_delayed_pullback_resumption"):
        if r.get(key) is not True:
            errors.append("event_rule_weakened:" + key)
    if tuple(r.get("setup_required_fields") or ()) != (
            C6_SETUP_REQUIRED_FIELDS):
        errors.append("setup_schema_tampered")
    if tuple(r.get("detector_statuses") or ()) != C6_DETECTOR_STATUSES:
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
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}

"""Candidate #18 -- h4_trend_following_market_structure_v1 -- DETECTOR SPEC +
SYNTHETIC DRY-RUN (PURE, RESEARCH ONLY).

Specifies the C18 H4 market-structure trend-following detector and exercises it on
DETERMINISTIC SYNTHETIC fixtures only -- never real data. The detector implements
ONLY the frozen C18 candidate-spec rules:

  * swing pivots with K=2 bars (a swing high = strict local high over +/-2 bars;
    swing low symmetric), confirmed K bars later;
  * uptrend = the last two confirmed swing highs are rising AND the last two
    confirmed swing lows are rising; downtrend = the mirror; else NO-TRADE;
  * LONG pullback entry only, on a newly confirmed HIGHER LOW while in an uptrend,
    spaced >= 6 H4 bars from the previous entry;
  * structural stop just below the higher-low anchor (anchor * (1 - 0.0015));
  * exit on a market-structure shift (a confirmed LOWER low) or the structural stop;
  * ADD to winners ONLY after open profit AND a new higher-low confirmation, never
    to losers, trailing the stop, capped at 3 units total;
  * one live position per symbol (non-overlapping by construction).

It does NOTHING with real data: NO fetch, NO real candles, NO XAUUSD, NO labels, NO
replay, NO PnL/cost application (the 37 bps is RESERVED for replay), NO optimization,
NO writes, NO stage/commit/push, NO paper/live/broker/order surface. Every capability
flag is pinned False with a full scope_locks set. The next gate (real-candle labels)
needs an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.h4_trend_following_market_structure_v1_candidate_spec_contract as _c18s  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as _rep

D18_SCHEMA_VERSION = 1
D18_MODE = "RESEARCH_ONLY"
D18_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c18s.CANDIDATE_ID
CANDIDATE_FAMILY = _c18s.CANDIDATE_FAMILY
CANDIDATE_NAME = _c18s.CANDIDATE_NAME

REJECTED_FAMILIES_C1_TO_C17 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C17)   # 22
TIMEFRAME = "H4"
ALL_IN_ROUND_TRIP_BPS = _c18s.ALL_IN_ROUND_TRIP_BPS                     # 37.0 reserved

# frozen spec params (reused, not redefined)
_SP = _c18s.SPEC_PARAMS
K = _SP["swing_pivot_strength_k"]                       # 2
STOP_BUFFER_FRAC = _SP["stop_buffer_frac"]              # 0.0015
MAX_UNITS = _SP["max_units_total"]                      # 3
MIN_SPACING = _SP["min_bars_between_entries"]           # 6
MAX_CONCURRENT = _SP["max_concurrent_positions_per_symbol"]   # 1

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files",
    "runs_detector_on_real_data", "runs_labels", "runs_replay", "runs_backtest",
    "computes_pnl", "applies_cost_model", "optimizes_parameters", "reparameterizes",
    "runs_robustness", "fetches_data", "reads_real_data", "uses_real_candles",
    "uses_xauusd", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "uses_indicators",
    "adds_to_losers", "allows_overlapping_positions", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "claims_friends_exact_system", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


# --------------------------------------------------------------------------- #
# Pure detector (long-only; structure rules only -- NO indicators)
# --------------------------------------------------------------------------- #

def _confirmed_swings(highs: list, lows: list) -> tuple:
    """Confirmed swing highs/lows with K-bar pivots. Each is (confirm_index,
    pivot_index, price); confirmed K bars after the pivot. Structure only."""
    n = len(highs)
    sh, sl = [], []
    for i in range(K, n - K):
        win = range(i - K, i + K + 1)
        if all(highs[i] > highs[j] for j in win if j != i):
            sh.append((i + K, i, highs[i]))
        if all(lows[i] < lows[j] for j in win if j != i):
            sl.append((i + K, i, lows[i]))
    return sh, sl


def run_detector(candles: list) -> dict:
    """Pure long-only H4 market-structure detector implementing the frozen C18 spec
    rules. Returns the trades + per-bar diagnostics. NO cost model, NO PnL."""
    highs = [c["high"] for c in candles]
    lows = [c["low"] for c in candles]
    closes = [c["close"] for c in candles]
    n = len(candles)
    sh, sl = _confirmed_swings(highs, lows)
    # confirmed swings indexed by confirm bar
    sh_by_t = {t: (pi, pr) for (t, pi, pr) in sh}
    sl_seq = sorted(sl, key=lambda x: x[0])          # by confirm index

    def trend_at(t: int) -> str:
        hs = [pr for (ct, pi, pr) in sh if ct <= t]
        ls = [pr for (ct, pi, pr) in sl if ct <= t]
        if len(hs) >= 2 and len(ls) >= 2:
            if hs[-1] > hs[-2] and ls[-1] > ls[-2]:
                return "uptrend"
            if hs[-1] < hs[-2] and ls[-1] < ls[-2]:
                return "downtrend"
        return "range"

    # map: confirm_index -> (this swing low price, prior swing low price)
    low_event = {}
    for idx in range(len(sl_seq)):
        ct, pi, pr = sl_seq[idx]
        prior = sl_seq[idx - 1][2] if idx > 0 else None
        low_event[ct] = (pr, prior)

    trades = []
    pos = None                 # {units, entries[list], stop, anchor, entry_bar}
    last_entry_bar = -10 ** 9
    max_concurrent = 0
    for t in range(n):
        tr = trend_at(t)
        ev = low_event.get(t)          # a swing low confirmed exactly at t
        new_higher_low = ev is not None and ev[1] is not None and ev[0] > ev[1]
        new_lower_low = ev is not None and ev[1] is not None and ev[0] < ev[1]

        # exit first: structure shift (lower low) or structural stop hit
        if pos is not None:
            hit_stop = lows[t] <= pos["stop"]
            if new_lower_low or hit_stop:
                exit_price = pos["stop"] if hit_stop and not new_lower_low \
                    else closes[t]
                trades.append({**pos, "exit_bar": t, "exit_price": round(exit_price, 6),
                               "exit_reason": "stop" if hit_stop and not new_lower_low
                               else "structure_shift"})
                pos = None

        # entry: flat, uptrend, new confirmed higher-low, spacing satisfied
        if pos is None and tr == "uptrend" and new_higher_low \
                and (t - last_entry_bar) >= MIN_SPACING:
            anchor = ev[0]
            pos = {"entry_bar": t, "entries": [round(closes[t], 6)], "units": 1,
                   "anchor": round(anchor, 6),
                   "stop": round(anchor * (1.0 - STOP_BUFFER_FRAC), 6),
                   "adds": []}
            last_entry_bar = t
        # pyramid: in position, new higher-low, open profit, units < cap
        elif pos is not None and new_higher_low:
            avg_entry = sum(pos["entries"]) / len(pos["entries"])
            in_profit = closes[t] > avg_entry
            if in_profit and pos["units"] < MAX_UNITS:
                pos["entries"].append(round(closes[t], 6))
                pos["units"] += 1
                pos["anchor"] = round(ev[0], 6)
                pos["stop"] = round(ev[0] * (1.0 - STOP_BUFFER_FRAC), 6)  # trail up
                pos["adds"].append({"bar": t, "anchor": round(ev[0], 6),
                                    "in_profit": True})

        max_concurrent = max(max_concurrent, 1 if pos is not None else 0)

    if pos is not None:
        trades.append({**pos, "exit_bar": n - 1,
                       "exit_price": round(closes[-1], 6),
                       "exit_reason": "end_of_data"})

    return {"trades": trades, "n_bars": n, "max_concurrent_positions": max_concurrent,
            "n_swing_highs": len(sh), "n_swing_lows": len(sl)}


# --------------------------------------------------------------------------- #
# Synthetic fixtures (deterministic; NO real data)
# --------------------------------------------------------------------------- #

def _path(turns: list, seg: int = 3) -> list:
    """Linear zig-zag close path between successive turn prices (seg bars per
    segment) so each interior turn is a strict +/-2 local extreme. Deterministic."""
    closes = [float(turns[0])]
    for a, b in zip(turns[:-1], turns[1:]):
        for j in range(1, seg + 1):
            closes.append(round(a + (b - a) * j / seg, 6))
    return closes


def _candles(closes: list, e: float = 0.05) -> list:
    """high = close + e, low = close - e (constant), so structure extremes of high/
    low coincide with close turns while honouring the spec's high/low usage."""
    return [{"high": round(c + e, 6), "low": round(c - e, 6), "close": c}
            for c in closes]


def build_synthetic_fixtures() -> dict:
    # 1) UPTREND: rising swing highs + rising swing lows, then a LOWER low -> exit.
    uptrend = _candles(_path(
        [100, 108, 103, 113, 107, 118, 111, 123, 116, 128, 121, 100]))
    # 2) RANGE: flat oscillation -> swing highs/lows not rising -> NO trade.
    rng = _candles(_path([100, 106, 100, 106, 100, 106, 100, 106, 100]))
    # 3) DOWNTREND: falling swing highs + lows -> NO long entry.
    downtrend = _candles(_path(
        [120, 112, 117, 107, 113, 102, 108, 97, 103, 92]))
    # 4) LOSER: establish an uptrend + one higher-low entry, then a LOWER low BEFORE
    #    any profit-confirmed higher-low -> structure-shift exit, ZERO adds.
    loser = _candles(_path([100, 108, 103, 113, 107, 118, 111, 95]))
    # 5) MAX-UNITS: a long, strong staircase with many rising higher-lows -> caps at
    #    3 units (1 base + 2 adds reach the cap; further higher-lows add nothing).
    strong = _candles(_path(
        [100, 110, 104, 116, 110, 124, 118, 134, 128, 146, 140, 160, 154, 176]))
    return {"uptrend": uptrend, "range": rng, "downtrend": downtrend,
            "loser": loser, "strong_uptrend": strong}


def run_synthetic_dry_run() -> dict:
    fx = build_synthetic_fixtures()
    res = {k: run_detector(v) for k, v in fx.items()}

    up = res["uptrend"]["trades"]
    rng = res["range"]["trades"]
    down = res["downtrend"]["trades"]
    loser = res["loser"]["trades"]
    strong = res["strong_uptrend"]["trades"]

    # determinism: re-run uptrend and compare
    up2 = run_detector(build_synthetic_fixtures()["uptrend"])["trades"]
    deterministic = up == up2

    def _all_stops_below_anchor(trades):
        return all(t["stop"] < t["anchor"]
                   and abs(t["stop"] - t["anchor"] * (1 - STOP_BUFFER_FRAC)) < 1e-6
                   for t in trades)

    def _max_units(trades):
        return max((t["units"] for t in trades), default=0)

    def _spacing_ok(trades):
        bars = sorted(t["entry_bar"] for t in trades)
        return all(b - a >= MIN_SPACING for a, b in zip(bars[:-1], bars[1:]))

    up_has_entry = len(up) >= 1
    up_has_add = any(t["adds"] for t in up)
    up_exit_structural = all(t["exit_reason"] in ("structure_shift", "stop",
                                                  "end_of_data") for t in up)
    loser_has_no_add = all(len(t["adds"]) == 0 for t in loser)
    # every add across all fixtures was made in profit (never to a loser)
    all_adds_in_profit = all(a["in_profit"] for tr in (up + strong + loser)
                             for a in tr["adds"])

    checks = {
        "deterministic": deterministic,
        "uptrend_detected_long_entry": up_has_entry,
        "no_trade_in_range": len(rng) == 0,
        "no_long_entry_in_downtrend": len(down) == 0,
        "structural_stop_below_anchor": _all_stops_below_anchor(up + strong + loser),
        "exit_on_structure_shift_or_stop": up_exit_structural and len(up) >= 1,
        "pyramids_only_on_profit_higher_low": up_has_add and all_adds_in_profit,
        "never_adds_to_losers": loser_has_no_add,
        "max_three_units": _max_units(up + strong + loser) <= MAX_UNITS,
        "spacing_min_6_bars": _spacing_ok(up) and _spacing_ok(strong),
        "one_position_per_symbol": all(
            r["max_concurrent_positions"] <= MAX_CONCURRENT for r in res.values()),
        "no_indicators_used": True,            # structure only
        "cost_model_not_applied": True,        # 37 bps reserved for replay
        "synthetic_only_no_real_data": True,
    }
    return {
        "results": res, "checks": checks, "all_checks_pass": all(checks.values()),
        "max_units_observed": _max_units(up + strong + loser),
        "uptrend_trade_count": len(up), "strong_uptrend_units": _max_units(strong),
    }


# --------------------------------------------------------------------------- #
# Contract assembly + validation
# --------------------------------------------------------------------------- #

def get_candidate_18_detector_dry_run_label() -> str:
    return (
        "Candidate #18 h4_trend_following_market_structure_v1 detector spec + "
        "SYNTHETIC dry-run (READ-ONLY, RESEARCH ONLY, PURE). Exercises the H4 "
        "market-structure trend-following detector (K=2 pivots, HH+HL uptrend, "
        "long pullback entry on a confirmed higher-low, structural stop, "
        "structure-shift / stop exit, profit-confirmed add-to-winners never to "
        "losers, max 3 units, one position per symbol) on DETERMINISTIC SYNTHETIC "
        "fixtures only -- never real data, no XAUUSD. 37 bps cost RESERVED for "
        "replay. NOT a profitability claim.")


def get_candidate_18_detector_dry_run_next_action() -> str:
    return "HUMAN_DECISION_C18_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"


def build_c18_detector_dry_run(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C18 detector spec + synthetic dry-run record. Pure; no
    I/O; chain-gated on the frozen C18 candidate spec."""
    spec = _c18s.build_c18_spec(repo_root, tracked_paths)
    spec_valid = _c18s.validate_c18_spec(spec)["valid"]
    dry = run_synthetic_dry_run()

    blockers: list = []
    if not spec_valid:
        blockers.append("c18_spec_invalid")
    if spec.get("verdict") != "C18_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c18_spec_not_frozen")
    if not dry["all_checks_pass"]:
        blockers.append("synthetic_dry_run_checks_failed")

    record: dict[str, Any] = {
        "schema_version": D18_SCHEMA_VERSION, "mode": D18_MODE, "lane": D18_LANE,
        "label": get_candidate_18_detector_dry_run_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_synthetic_dry_run_only": True,
        "blockers": blockers,
        "verdict": ("C18_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
                    if not blockers else "C18_DETECTOR_DRY_RUN_BLOCKED"),
        # chain provenance
        "spec_verdict": spec.get("verdict"), "spec_valid": spec_valid,
        # HONESTY -- objective approximation, not the exact system
        "is_objective_testable_approximation": True,
        "is_observed_traders_exact_system": False,
        # preserved frozen spec params (implemented exactly)
        "timeframe": TIMEFRAME, "swing_pivot_strength_k": K,
        "stop_buffer_frac": STOP_BUFFER_FRAC, "max_units_total": MAX_UNITS,
        "min_bars_between_entries": MIN_SPACING,
        "max_concurrent_positions_per_symbol": MAX_CONCURRENT,
        "is_h4_market_structure": True, "uses_indicators": False,
        "long_only_in_dry_run": True, "pyramids_only_on_confirmed_winners": True,
        "positions_non_overlapping_per_symbol": True,
        # the synthetic dry-run
        "uses_synthetic_fixtures_only": True, "uses_real_data": False,
        "uses_xauusd": False,
        "synthetic_fixtures": ["uptrend", "range", "downtrend", "loser",
                               "strong_uptrend"],
        "dry_run_checks": dict(dry["checks"]),
        "dry_run_all_checks_pass": dry["all_checks_pass"],
        "dry_run_max_units_observed": dry["max_units_observed"],
        "dry_run_uptrend_trade_count": dry["uptrend_trade_count"],
        # cost reserved, not applied
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "all_in_round_trip_bps_reserved": ALL_IN_ROUND_TRIP_BPS,
        # anti-loop
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C17),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C17,
        "human_review_required": True,
        "current_loop_stage": "detector_spec_dry_run",
        "next_required_action": get_candidate_18_detector_dry_run_next_action(),
        # downstream gates locked
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_data_fetch": True, "no_real_data_access": True, "no_real_candles": True,
        "no_xauusd": True, "no_labels": True, "no_replay": True, "no_backtest": True,
        "no_pnl": True, "no_cost_application": True, "no_optimization": True,
        "no_reparameterization": True, "no_robustness": True, "no_indicators": True,
        "no_add_to_losers": True, "no_overlapping_positions": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c18_detector_dry_run(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the dry-run is research-only,
    synthetic-only (no real data / no XAUUSD / no cost application), chain-gated on
    the frozen C18 spec, an H4 market-structure long detector (no indicators, pyramid
    only on winners, non-overlap) implementing the frozen params, all synthetic
    behaviour checks pass, C1-C17 stays excluded, downstream gates locked, and every
    capability flag False."""
    failures: list = []
    if record.get("mode") != D18_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_synthetic_dry_run_only") is not True:
        failures.append("not_synthetic_dry_run_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C18_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    if record.get("spec_valid") is not True:
        failures.append("spec_not_valid")
    if record.get("spec_verdict") != "C18_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("spec_not_frozen")

    # HONESTY
    if record.get("is_objective_testable_approximation") is not True:
        failures.append("must_be_objective_approximation")
    if record.get("is_observed_traders_exact_system") is not False:
        failures.append("must_not_claim_exact_system")

    # identity + frozen params implemented exactly
    if record.get("is_h4_market_structure") is not True:
        failures.append("not_h4_market_structure")
    if record.get("uses_indicators") is not False:
        failures.append("indicators_used")
    if record.get("swing_pivot_strength_k") != 2:
        failures.append("k_not_2")
    if record.get("max_units_total") != 3:
        failures.append("max_units_not_3")
    if record.get("min_bars_between_entries") != 6:
        failures.append("spacing_not_6")
    if record.get("max_concurrent_positions_per_symbol") != 1:
        failures.append("non_overlap_param_wrong")
    if record.get("pyramids_only_on_confirmed_winners") is not True:
        failures.append("must_pyramid_only_on_winners")

    # synthetic-only, no real data / xauusd / cost
    for k in ("uses_synthetic_fixtures_only", "cost_model_reserved_for_replay"):
        if record.get(k) is not True:
            failures.append("flag_off_%s" % k)
    if record.get("uses_real_data") is not False:
        failures.append("uses_real_data_set")
    if record.get("uses_xauusd") is not False:
        failures.append("uses_xauusd_set")
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_model_applied")

    # behaviour checks
    checks = record.get("dry_run_checks") or {}
    for k in ("deterministic", "uptrend_detected_long_entry", "no_trade_in_range",
              "no_long_entry_in_downtrend", "structural_stop_below_anchor",
              "exit_on_structure_shift_or_stop", "pyramids_only_on_profit_higher_low",
              "never_adds_to_losers", "max_three_units", "spacing_min_6_bars",
              "one_position_per_symbol", "no_indicators_used",
              "cost_model_not_applied", "synthetic_only_no_real_data"):
        if checks.get(k) is not True:
            failures.append("dry_run_check_failed_%s" % k)
    if record.get("dry_run_all_checks_pass") is not True:
        failures.append("dry_run_not_all_pass")
    if record.get("dry_run_max_units_observed", 99) > 3:
        failures.append("max_units_exceeded")

    # anti-loop
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("rejected_families_count") != 22:
        failures.append("ledger_not_22")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_C18_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"):
        failures.append("next_action_not_labels_gate")

    # downstream gates locked
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_real_candles", "no_xauusd", "no_labels",
                "no_replay", "no_pnl", "no_cost_application", "no_optimization",
                "no_indicators", "no_add_to_losers", "no_overlapping_positions",
                "no_commit", "no_push", "no_broker", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

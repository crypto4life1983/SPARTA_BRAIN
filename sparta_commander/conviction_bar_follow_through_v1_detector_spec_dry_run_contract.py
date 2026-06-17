"""SPARTA Candidate #14 detector specification + synthetic dry-run:
conviction_bar_follow_through_v1.

RESEARCH ONLY. SYNTHETIC FIXTURES ONLY. This module specifies the C14 detector
geometry and exercises it against in-memory synthetic fixtures. It reads NO real
market data, fetches NO data, creates NO real labels, runs NO replay, NO
robustness, NO portfolio compute, NO baseline comparison, and has NO trading /
broker / credential / order capability. It writes nothing and runs nothing
outside its pure functions.

Detector (conviction-bar follow-through), per single asset (BTC/ETH/SOL 1d):
  * Bars are indexed by LIST POSITION and carry ONLY OHLC -- there is NO date and
    NO weekday in the bar shape, so a calendar/weekday trigger is structurally
    impossible.
  * On bar t (after a 14-bar ATR warmup): true_range = max(high-low,
    |high-prev_close|, |low-prev_close|); ATR = ATR(14). A CONVICTION BAR requires
    BOTH true_range >= 1.5*ATR (a volatility-expansion OUTLIER, with NO
    compression precondition) AND close >= low + 0.75*(high-low) (a top-quartile
    close). Entry at the conviction bar's close; stop = close - 1.0*ATR(14);
    reject if stop<=0/not below; targets 1R/1.5R/2R; reject if no variant clears
    the 81 bps gross floor.
  * Exit walk over the <=2-bar hold: stop (low<=stop -> -1R), target
    (high>=target -> +R), same-bar straddle = STOP FIRST (-1R), else HORIZON exit
    at the +2 close -> (exit_close-entry)/stop_distance. Per-asset non-overlap is
    reduce-or-keep-only (drop a later same-asset setup whose entry <= the active
    resolved exit).
  * The structural labels sample-size gate + the early-generalization + anti-drift
    battery (forward-OOS, cross-regime symmetry, cross-asset, must-beat
    buy-and-hold AND random-entry, target-capture dominance / horizon-exit cap)
    stay LOCKED here for the later labels/replay stage; this dry-run does not run
    them.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.conviction_bar_follow_through_v1_candidate_spec_contract import (  # noqa: E501
    ALL_IN_ROUND_TRIP_BPS,
    ATR_LENGTH,
    CLOSE_LOCATION_MIN,
    EARLY_STRUCTURAL_REJECTION_GATES,
    MAX_HOLD_BARS,
    MAX_HORIZON_EXIT_SHARE,
    RANGE_ATR_MULTIPLE,
    STOP_ATR_MULTIPLIER,
    TARGET_DISTANCE_FLOOR_BPS,
    TARGET_R_MULTIPLES,
    VERDICT_C14S_READY,
    build_candidate_14_spec,
)

CANDIDATE_ID = "CONVICTION_BAR_FOLLOW_THROUGH_V1"
CANDIDATE_FAMILY = "conviction_bar_follow_through"
C14D_MODE = "RESEARCH_ONLY"
SYMBOL_UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
MIN_ASSETS = 3
TIMEFRAME = "1d"
DIRECTION = "long_only"

TARGET_VARIANTS = (("1r", 1.0), ("1.5r", 1.5), ("2r", 2.0))
WARMUP = ATR_LENGTH

VERDICT_C14DD_READY = "CANDIDATE_14_DETECTOR_DRY_RUN_READY"
VERDICT_C14DD_BLOCKED = "CANDIDATE_14_DETECTOR_DRY_RUN_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_C14_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")


# --------------------------------------------------------------------------- #
# Pure detector primitives (single asset; no date / no weekday read)
# --------------------------------------------------------------------------- #

def true_range(bars: list, t: int):
    """max(high-low, |high-prev_close|, |low-prev_close|). None if t < 1."""
    if t < 1 or t >= len(bars):
        return None
    hi = float(bars[t]["high"])
    lo = float(bars[t]["low"])
    prev_close = float(bars[t - 1]["close"])
    return max(hi - lo, abs(hi - prev_close), abs(lo - prev_close))


def compute_atr14(bars: list, t: int, length: int = ATR_LENGTH):
    if t < length:
        return None
    trs = []
    for i in range(t - length + 1, t + 1):
        trs.append(true_range(bars, i))
    if any(x is None for x in trs):
        return None
    return sum(trs) / length


def close_location(bar: dict):
    """Fraction of the bar range the close sits at: (close-low)/(high-low).
    None if range is zero."""
    hi = float(bar["high"])
    lo = float(bar["low"])
    if hi <= lo:
        return None
    return (float(bar["close"]) - lo) / (hi - lo)


def is_conviction_bar(bars: list, t: int):
    """True iff true_range >= RANGE_ATR_MULTIPLE*ATR(14) AND close-location >=
    CLOSE_LOCATION_MIN. None if not enough history / undefined range."""
    tr = true_range(bars, t)
    atr = compute_atr14(bars, t)
    if tr is None or atr is None or atr <= 0.0:
        return None
    loc = close_location(bars[t])
    if loc is None:
        return None
    return tr >= RANGE_ATR_MULTIPLE * atr and loc >= CLOSE_LOCATION_MIN


def compute_stop(entry_close: float, atr_at_entry: float) -> dict[str, Any]:
    """stop = entry - STOP_ATR_MULTIPLIER*ATR(14). Rejects zero/negative/at-or-
    above stop distance (e.g. ATR <= 0)."""
    stop_price = float(entry_close) - STOP_ATR_MULTIPLIER * float(atr_at_entry)
    stop_distance = float(entry_close) - stop_price
    below = stop_price < float(entry_close)
    return {"stop_price": stop_price, "stop_distance": stop_distance,
            "stop_below_entry": below,
            "valid": stop_distance > 0.0 and below}


def geometry_floor_by_variant(entry_price: float,
                              stop_distance: float) -> dict[str, Any]:
    out: dict[str, Any] = {"targets": {}, "target_distance_bps": {},
                           "floor_pass": {}, "any_variant_passes": False}
    for name, mult in TARGET_VARIANTS:
        dist = mult * float(stop_distance)
        bps = (dist / float(entry_price)) * 10000.0
        out["targets"][name] = round(float(entry_price) + dist, 6)
        out["target_distance_bps"][name] = round(bps, 6)
        out["floor_pass"][name] = bps >= TARGET_DISTANCE_FLOOR_BPS
    out["any_variant_passes"] = any(out["floor_pass"].values())
    return out


def scan_c14_setups(bars: list, timeframe: str = TIMEFRAME,
                    direction: str = DIRECTION) -> list[dict[str, Any]]:
    """Conviction-bar follow-through scanner over one asset's bars. Returns one
    record per qualifying conviction bar. Raises ValueError for a non-1d /
    non-long-only context. Pure; reads NO date and NO weekday."""
    if timeframe != TIMEFRAME or direction != DIRECTION:
        raise ValueError("c14_detector_locked_to_1d_long_only")
    if not isinstance(bars, list):
        raise ValueError("bars_must_be_a_list")
    n = len(bars)
    setups: list[dict[str, Any]] = []
    for t in range(WARMUP, n):
        conv = is_conviction_bar(bars, t)
        if conv is None or not conv:
            continue
        entry = float(bars[t]["close"])
        atr = compute_atr14(bars, t)
        tr = true_range(bars, t)
        stop = compute_stop(entry, atr)
        rec = {
            "setup_index": t, "true_range": round(tr, 6),
            "atr_at_entry": round(atr, 6),
            "range_atr_ratio": round(tr / atr, 6),
            "close_location": round(close_location(bars[t]), 6),
            "entry_price": round(entry, 6),
            "stop_price": round(stop["stop_price"], 6),
            "stop_distance": round(stop["stop_distance"], 6),
            "uses_weekday_or_calendar_trigger": False,
            "status": None, "rejection_reason": None,
        }
        if not stop["valid"]:
            rec["status"] = "rejected_invalid_stop_geometry"
            rec["rejection_reason"] = "stop_distance_not_positive_or_not_below"
            setups.append(rec)
            continue
        floor = geometry_floor_by_variant(entry, stop["stop_distance"])
        rec["target_1r"] = floor["targets"]["1r"]
        rec["target_1_5r"] = floor["targets"]["1.5r"]
        rec["target_2r"] = floor["targets"]["2r"]
        rec["target_distance_bps"] = floor["target_distance_bps"]
        rec["floor_pass_by_variant"] = floor["floor_pass"]
        if not floor["any_variant_passes"]:
            rec["status"] = "rejected_geometry_floor"
            rec["rejection_reason"] = "all_variant_target_distances_below_81_bps"
            setups.append(rec)
            continue
        rec["status"] = "accepted_for_replay_review"
        setups.append(rec)
    return setups


def evaluate_one_setup_horizon(bars: list, setup: dict,
                               variant_r: float,
                               max_hold: int = MAX_HOLD_BARS) -> dict[str, Any]:
    """Walk one accepted setup over the <=max_hold horizon for one R-multiple.
    Stop-first on straddle; horizon exit at the max_hold bar close. Pure."""
    entry = float(setup["entry_price"])
    stop_price = float(setup["stop_price"])
    stop_distance = float(setup["stop_distance"])
    t = int(setup["setup_index"])
    exit_index = t + max_hold
    target_price = entry + variant_r * stop_distance
    out = {"setup_index": t, "variant_r_multiple": variant_r,
           "outcome": None, "exit_resolved_index": None, "exit_price": None,
           "bars_held": None, "gross_r": None}
    if exit_index >= len(bars):
        out["outcome"] = "horizon_bar_beyond_source"
        return out

    def _finish(outcome, idx, price, gross_r):
        out["outcome"] = outcome
        out["exit_resolved_index"] = idx
        out["exit_price"] = price
        out["bars_held"] = idx - t
        out["gross_r"] = gross_r
        return out

    for i in range(t + 1, exit_index + 1):
        bar = bars[i]
        hit_stop = float(bar["low"]) <= stop_price
        hit_target = float(bar["high"]) >= target_price
        if hit_stop and hit_target:
            return _finish("miss_same_bar_straddle", i, stop_price, -1.0)
        if hit_stop:
            return _finish("miss", i, stop_price, -1.0)
        if hit_target:
            return _finish("hit", i, target_price, float(variant_r))
    exit_close = float(bars[exit_index]["close"])
    return _finish("horizon", exit_index, exit_close,
                   (exit_close - entry) / stop_distance)


def apply_non_overlap(setups_sorted: list, bars: list,
                      variant_r: float = 1.0) -> dict[str, Any]:
    """Per-asset REDUCE-OR-KEEP-ONLY: drop a later setup whose entry_index is <=
    the active resolved exit index. Never add."""
    kept = []
    dropped = []
    active_exit_index = None
    for s in setups_sorted:
        idx = int(s["setup_index"])
        if active_exit_index is not None and idx <= active_exit_index:
            dropped.append({"setup_index": idx,
                            "outcome": "dropped_non_overlap",
                            "blocked_by_active_exit_index": active_exit_index})
            continue
        outcome = evaluate_one_setup_horizon(bars, s, variant_r)
        kept.append({**s, "horizon_outcome": outcome})
        if outcome["exit_resolved_index"] is not None:
            active_exit_index = outcome["exit_resolved_index"]
    return {"kept": kept, "dropped": dropped}


# --------------------------------------------------------------------------- #
# Synthetic fixtures (in-memory; deterministic; NO date / NO weekday / NO RNG)
# --------------------------------------------------------------------------- #

def _flat(n: int, price: float = 100.0, rng: float = 0.01) -> list:
    """Constant-price OHLC bars (each bar's TR ~ 2*rng*price). Bars carry NO date
    and NO weekday -- only OHLC."""
    return [{"open": price, "high": round(price * (1 + rng), 8),
             "low": round(price * (1 - rng), 8), "close": price}
            for _ in range(n)]


def _conviction_bar(price: float, rng: float) -> dict:
    """An outlier wide-range bar that CLOSES near its high (top quartile)."""
    return {"open": price, "high": round(price * (1 + 0.5 * rng), 8),
            "low": round(price * (1 - 3.0 * rng), 8), "close": price}


def _weak_close_bar(price: float, rng: float) -> dict:
    """An outlier wide-range bar that CLOSES near its low (bottom -> NOT a
    conviction bar despite the range outlier)."""
    return {"open": price, "high": round(price * (1 + 3.0 * rng), 8),
            "low": round(price * (1 - 0.5 * rng), 8),
            "close": round(price * (1 - 0.4 * rng), 8)}


_N = 30
_T = 20          # signal index (>= warmup 14), leaving room for the 2-bar horizon


def fixture_valid_conviction_accepted() -> list:
    """Outlier range (TR >= 1.5*ATR) + top-quartile close, normal ATR -> 1R
    clears the 81 bps floor -> ACCEPTED."""
    bars = _flat(_N, 100.0, 0.01)
    bars[_T] = _conviction_bar(100.0, 0.01)
    return bars


def fixture_not_outlier_no_setup() -> list:
    """All flat bars -> TR == ATR (not >= 1.5*ATR) -> NO conviction -> NO setup."""
    return _flat(_N, 100.0, 0.01)


def fixture_weak_close_no_setup() -> list:
    """Outlier range but the close is near the LOW (close-location below the top
    quartile) -> NOT a conviction bar -> NO setup."""
    bars = _flat(_N, 100.0, 0.01)
    bars[_T] = _weak_close_bar(100.0, 0.01)
    return bars


def fixture_below_floor_rejected() -> list:
    """Conviction bar but a microscopic range/ATR -> even 2R below the 81 bps
    floor -> rejected_geometry_floor."""
    bars = _flat(_N, 100.0, 0.0002)
    bars[_T] = _conviction_bar(100.0, 0.0002)
    return bars


def fixture_two_conviction_non_overlap() -> list:
    """Two conviction bars at t and t+1 -> per-asset non-overlap drops the
    later one (within the 2-bar hold)."""
    bars = _flat(_N + 3, 100.0, 0.01)
    bars[_T] = _conviction_bar(100.0, 0.01)
    bars[_T + 1] = _conviction_bar(100.0, 0.01)
    return bars


def _accepted_at_t(fixture):
    return next((s for s in scan_c14_setups(fixture())
                 if s["status"] == "accepted_for_replay_review"
                 and s["setup_index"] == _T), None)


def run_c14_detector_dry_run() -> dict[str, Any]:
    """Run every synthetic fixture and report the outcomes. Pure; in-memory."""
    accepted = _accepted_at_t(fixture_valid_conviction_accepted)
    not_outlier = scan_c14_setups(fixture_not_outlier_no_setup())
    weak_close = scan_c14_setups(fixture_weak_close_no_setup())
    below_floor = next((s for s in scan_c14_setups(fixture_below_floor_rejected())
                        if s["setup_index"] == _T), None)

    invalid_stop_guard = compute_stop(100.0, 0.0)          # zero ATR -> invalid

    def _eth_override(at, bar):
        bars = fixture_valid_conviction_accepted()
        bars[at] = bar
        return bars

    def _scan_override(bars, variant=1.0):
        acc = next((s for s in scan_c14_setups(bars)
                    if s["status"] == "accepted_for_replay_review"
                    and s["setup_index"] == _T), None)
        return (evaluate_one_setup_horizon(bars, acc, variant) if acc else None)

    tgt = _scan_override(_eth_override(
        _T + 1, {"open": 100.0, "high": 1e9, "low": 99.0, "close": 1e8}))
    stp = _scan_override(_eth_override(
        _T + 1, {"open": 100.0, "high": 100.1, "low": 1e-6, "close": 1e-3}))
    strd = _scan_override(_eth_override(
        _T + 1, {"open": 100.0, "high": 1e9, "low": 1e-6, "close": 100.0}))
    hor = (evaluate_one_setup_horizon(fixture_valid_conviction_accepted(),
                                      accepted, 1.0) if accepted else None)

    ov_setups = [s for s in scan_c14_setups(fixture_two_conviction_non_overlap())
                 if s["status"] == "accepted_for_replay_review"]
    ov = apply_non_overlap(sorted(ov_setups, key=lambda s: s["setup_index"]),
                           fixture_two_conviction_non_overlap(), 1.0)

    locked_to_1d_raises = False
    try:
        scan_c14_setups(fixture_valid_conviction_accepted(), timeframe="1h")
    except ValueError:
        locked_to_1d_raises = True

    return {
        "valid_status": (accepted or {}).get("status"),
        "not_outlier_count": len(not_outlier),
        "weak_close_count": len(weak_close),
        "below_floor_status": (below_floor or {}).get("status"),
        "invalid_stop_guard_valid": invalid_stop_guard["valid"],
        "target_outcome": (tgt or {}).get("outcome"),
        "target_gross_r": (tgt or {}).get("gross_r"),
        "stop_outcome": (stp or {}).get("outcome"),
        "stop_gross_r": (stp or {}).get("gross_r"),
        "straddle_outcome": (strd or {}).get("outcome"),
        "straddle_gross_r": (strd or {}).get("gross_r"),
        "horizon_outcome": (hor or {}).get("outcome"),
        "non_overlap_accepted_setups": len(ov_setups),
        "non_overlap_kept": len(ov["kept"]),
        "non_overlap_dropped": len(ov["dropped"]),
        "locked_to_1d_raises": locked_to_1d_raises,
        "uses_no_weekday_or_calendar_trigger": True,
    }


# --------------------------------------------------------------------------- #
# Detector spec + dry-run contract (chain-gated on the C14 spec; pure)
# --------------------------------------------------------------------------- #

C14DD_LABEL = (
    "SPARTA Candidate #14 Detector Spec + Synthetic Dry-Run (READ-ONLY, "
    "RESEARCH ONLY, SYNTHETIC FIXTURES ONLY). conviction_bar_follow_through: "
    "true_range >= 1.5*ATR(14) AND top-quartile close -> long the close; ATR(14) "
    "stop = close - 1.0*ATR; 1R/1.5R/2R; 81 bps floor; <=2-bar hold; stop-first "
    "straddle; per-asset non-overlap. NO date, NO weekday, NO real data, NO "
    "labels, NO replay, NO trading. SAMPLE-SIZE + EARLY GENERALIZATION + "
    "ANTI-DRIFT BATTERY STAYS LOCKED FOR THE LATER LABELS/REPLAY STAGE."
)

_CAPABILITY_FLAGS_FALSE = (
    "reads_real_data", "fetches_data", "stages_data_now", "creates_labels",
    "labels_now", "runs_replay", "runs_replay_now", "runs_robustness",
    "runs_generalization_now", "runs_baseline_comparison_now",
    "runs_portfolio_compute", "calls_api", "uses_network", "uses_credentials",
    "uses_wallet", "uses_account", "connects_broker", "connects_exchange",
    "uses_real_money", "contains_order_logic",
    "contains_portfolio_allocation_logic", "deploys_capital", "starts_scheduler",
    "sends_notifications", "auto_commits", "auto_pushes",
    "uses_weekday_or_calendar_trigger", "is_single_asset_edge",
    "relies_on_long_drift_or_bull_carry", "fits_parameters",
    "is_a_rescue_attempt", "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
    "claims_profitability", "claims_edge", "claims_paper_or_live_readiness",
    "executes", "writes_files",
)


def get_candidate_14_detector_dry_run_label() -> str:
    return C14DD_LABEL


def get_candidate_14_detector_dry_run_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_candidate_14_detector_spec_dry_run(repo_root: Any = ".",
                                             tracked_paths: list | None = None
                                             ) -> dict[str, Any]:
    """Assemble the C14 detector spec + synthetic dry-run record. Chain-gated on
    the READY candidate spec. Runs the synthetic dry-run and pins the required
    proofs. Pure; in-memory; synthetic fixtures only."""
    dry = run_c14_detector_dry_run()
    dry_again = run_c14_detector_dry_run()
    proofs = {
        "valid_conviction_setup_accepted":
            dry["valid_status"] == "accepted_for_replay_review",
        "no_setup_when_not_range_outlier": dry["not_outlier_count"] == 0,
        "no_setup_when_close_not_top_quartile": dry["weak_close_count"] == 0,
        "invalid_stop_guard_rejects": dry["invalid_stop_guard_valid"] is False,
        "below_floor_rejected":
            dry["below_floor_status"] == "rejected_geometry_floor",
        "target_hit_outcome":
            dry["target_outcome"] == "hit" and dry["target_gross_r"] == 1.0,
        "stop_hit_outcome":
            dry["stop_outcome"] == "miss" and dry["stop_gross_r"] == -1.0,
        "same_bar_straddle_is_stop_first":
            dry["straddle_outcome"] == "miss_same_bar_straddle"
            and dry["straddle_gross_r"] == -1.0,
        "horizon_exit_when_neither": dry["horizon_outcome"] == "horizon",
        "per_asset_non_overlap_drops_later":
            dry["non_overlap_accepted_setups"] >= 2
            and dry["non_overlap_kept"] == 1
            and dry["non_overlap_dropped"] >= 1,
        "locked_to_1d_long_only": dry["locked_to_1d_raises"] is True,
        "no_calendar_or_weekday_trigger":
            dry["uses_no_weekday_or_calendar_trigger"] is True,
        "no_labels_replay_baseline_data_fetch_trading": True,
        "deterministic": dry == dry_again,
    }
    record: dict[str, Any] = {
        "schema_version": 1, "label": C14DD_LABEL, "mode": C14D_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_number": 14, "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "symbol_universe": list(SYMBOL_UNIVERSE), "min_assets": MIN_ASSETS,
        "timeframe": TIMEFRAME, "direction": DIRECTION,
        "range_atr_multiple": RANGE_ATR_MULTIPLE,
        "close_location_min": CLOSE_LOCATION_MIN,
        "atr_length": ATR_LENGTH, "stop_atr_multiplier": STOP_ATR_MULTIPLIER,
        "target_variants": [n for n, _ in TARGET_VARIANTS],
        "target_r_multiples": dict(TARGET_R_MULTIPLES),
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "max_hold_bars": MAX_HOLD_BARS,
        "max_horizon_exit_share": MAX_HORIZON_EXIT_SHARE,
        "same_bar_straddle_policy": "stop_first_conservative_miss",
        "non_overlap_policy": "per_asset_resolved_exit_reduce_or_keep_only_never_add",
        "no_compression_precondition": True,
        "synthetic_fixtures_only": True,
        "uses_no_weekday_or_calendar_trigger": True,
        "is_single_asset_edge": False,
        "relies_on_long_drift_or_bull_carry": False,
        "dry_run": dry, "dry_run_proofs": proofs,
        "early_generalization_battery_locked_for_labels_replay":
            list(EARLY_STRUCTURAL_REJECTION_GATES),
        "current_loop_stage": "detector_spec_and_synthetic_dry_run",
        "human_review_required": True,
        "labels_gate_locked": True, "replay_gate_locked": True,
        "baseline_gate_locked": True, "data_fetch_gate_locked": True,
        "robustness_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "synthetic_fixtures_only": True, "no_real_data": True,
        "no_data_fetch": True, "no_labels": True, "no_replay": True,
        "no_baseline_comparison": True, "no_robustness_run": True,
        "no_generalization_run": True, "no_portfolio_compute": True,
        "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_weekday_trigger": True,
        "no_calendar_trigger": True, "no_single_asset_edge": True,
        "no_long_drift_or_bull_carry_reliance": True,
        "no_parameter_fitting": True, "no_profitability_claim": True,
        "no_paper_live_readiness_claim": True, "no_downstream_gate_unlock": True,
    }

    spec = build_candidate_14_spec(repo_root, tracked_paths or [])
    record["spec_verdict"] = spec.get("verdict")
    if spec.get("verdict") != VERDICT_C14S_READY:
        record["verdict"] = VERDICT_C14DD_BLOCKED
        record["blockers"].append("spec_not_ready")
        return record
    if not all(proofs.values()):
        record["verdict"] = VERDICT_C14DD_BLOCKED
        record["blockers"].append("dry_run_proof_failed")
        return record

    record["verdict"] = VERDICT_C14DD_READY
    return record


def validate_candidate_14_detector_spec_dry_run(record: dict[str, Any]
                                                ) -> dict[str, Any]:
    """Anti-tamper validator. READY only when all proofs hold, the detector
    geometry is intact, no compression precondition, no calendar/weekday/single-
    asset/long-drift behavior, and all execution gates are locked."""
    failures: list = []
    if record.get("verdict") != VERDICT_C14DD_READY:
        failures.append("verdict_not_ready")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("spec_verdict") != VERDICT_C14S_READY:
        failures.append("spec_verdict_tampered")

    proofs = record.get("dry_run_proofs") or {}
    for key in ("valid_conviction_setup_accepted",
                "no_setup_when_not_range_outlier",
                "no_setup_when_close_not_top_quartile",
                "invalid_stop_guard_rejects", "below_floor_rejected",
                "target_hit_outcome", "stop_hit_outcome",
                "same_bar_straddle_is_stop_first", "horizon_exit_when_neither",
                "per_asset_non_overlap_drops_later", "locked_to_1d_long_only",
                "no_calendar_or_weekday_trigger",
                "no_labels_replay_baseline_data_fetch_trading", "deterministic"):
        if proofs.get(key) is not True:
            failures.append("proof_failed_%s" % key)

    if len(record.get("symbol_universe") or []) < MIN_ASSETS:
        failures.append("single_asset_universe")
    if record.get("range_atr_multiple") != RANGE_ATR_MULTIPLE:
        failures.append("range_multiple_tampered")
    if record.get("close_location_min") != CLOSE_LOCATION_MIN:
        failures.append("close_location_tampered")
    if record.get("stop_atr_multiplier") != STOP_ATR_MULTIPLIER:
        failures.append("stop_multiplier_tampered")
    if list(record.get("target_variants") or []) != [n for n, _ in TARGET_VARIANTS]:
        failures.append("target_variants_tampered")
    if record.get("target_distance_floor_bps") != TARGET_DISTANCE_FLOOR_BPS:
        failures.append("floor_tampered")
    if record.get("max_hold_bars") != MAX_HOLD_BARS:
        failures.append("max_hold_tampered")
    if record.get("all_in_round_trip_bps") != ALL_IN_ROUND_TRIP_BPS:
        failures.append("cost_tampered")
    if record.get("same_bar_straddle_policy") != "stop_first_conservative_miss":
        failures.append("straddle_policy_tampered")
    if record.get("non_overlap_policy") != (
            "per_asset_resolved_exit_reduce_or_keep_only_never_add"):
        failures.append("non_overlap_policy_tampered")
    if record.get("no_compression_precondition") is not True:
        failures.append("compression_precondition_introduced")
    if record.get("uses_no_weekday_or_calendar_trigger") is not True:
        failures.append("calendar_trigger_flag_tampered")
    if record.get("synthetic_fixtures_only") is not True:
        failures.append("synthetic_only_flag_tampered")
    if record.get("is_single_asset_edge") is not False:
        failures.append("single_asset_flag_tampered")
    if record.get("relies_on_long_drift_or_bull_carry") is not False:
        failures.append("long_drift_flag_tampered")
    if not record.get("early_generalization_battery_locked_for_labels_replay"):
        failures.append("early_generalization_battery_missing")

    locks = record.get("scope_locks") or {}
    for key in ("synthetic_fixtures_only", "no_real_data", "no_data_fetch",
                "no_labels", "no_replay", "no_baseline_comparison",
                "no_portfolio_compute", "no_paper_trading", "no_live_trading",
                "no_calendar_trigger", "no_weekday_trigger",
                "no_single_asset_edge", "no_long_drift_or_bull_carry_reliance",
                "no_paper_live_readiness_claim"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("labels_gate_locked", "replay_gate_locked",
                "baseline_gate_locked", "data_fetch_gate_locked",
                "robustness_gate_locked", "paper_trading_gate_locked",
                "live_gate_locked", "human_review_required"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

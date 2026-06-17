"""SPARTA Candidate #12 detector specification + synthetic dry-run:
failed_breakdown_reclaim_reversal_v1.

RESEARCH ONLY. SYNTHETIC FIXTURES ONLY. This module specifies the C12 detector
geometry and exercises it against in-memory synthetic fixtures. It reads NO real
market data, fetches NO data, creates NO real labels, runs NO replay, NO
robustness, NO portfolio compute, and has NO trading / broker / credential /
order capability. It writes nothing and runs nothing outside its pure functions.

Detector (failed-breakdown reclaim reversal), per single asset (BTC/ETH/SOL 1d):
  * Bars are indexed by LIST POSITION and carry ONLY OHLC -- there is NO date and
    NO weekday in the bar shape, so a calendar/weekday trigger is structurally
    impossible.
  * On each bar t (after a max(K=20, ATR=14) warmup): let L_K = min(low) over the
    prior K=20 bars [t-K .. t-1]. A FAILED-BREAKDOWN RECLAIM requires BOTH
    low[t] < L_K (a new K-day low is pierced) AND close[t] > L_K (the level is
    reclaimed on the close). Confirmation is close-based; no intrabar entry.
  * Entry at the reclaim bar's close; stop = reclaim_bar_low - 0.25*ATR(14);
    reject if stop_distance <= 0 or stop not below entry; targets 1.5R/2R/3R;
    reject if no variant clears the 81 bps gross target-distance floor.
  * Exit walk over the <=3-bar hold: stop (low<=stop -> -1R), target
    (high>=target -> +R), same-bar straddle = STOP FIRST (-1R), else HORIZON exit
    at the +3 close -> (exit_close-entry)/stop_distance. Per-asset non-overlap is
    reduce-or-keep-only (drop a later same-asset setup whose entry <= the active
    resolved exit).
  * The early-generalization + anti-drift battery (forward-OOS, cross-regime
    symmetry, cross-asset, must-beat buy-and-hold AND random-entry, target-
    capture dominance / horizon-exit cap) stays LOCKED here for the later
    labels/replay stage (the C10/C11 lessons); this dry-run does not run it.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.failed_breakdown_reclaim_reversal_v1_candidate_spec_contract import (  # noqa: E501
    ALL_IN_ROUND_TRIP_BPS,
    ATR_LENGTH,
    EARLY_STRUCTURAL_REJECTION_GATES,
    K_DAY_LOW_LOOKBACK,
    MAX_HOLD_BARS,
    MAX_HORIZON_EXIT_SHARE,
    STOP_ATR_BUFFER_MULTIPLIER,
    TARGET_DISTANCE_FLOOR_BPS,
    TARGET_R_MULTIPLES,
    VERDICT_C12S_READY,
    build_candidate_12_spec,
)

CANDIDATE_ID = "FAILED_BREAKDOWN_RECLAIM_REVERSAL_V1"
CANDIDATE_FAMILY = "failed_breakdown_reclaim_reversal"
C12D_MODE = "RESEARCH_ONLY"
SYMBOL_UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
MIN_ASSETS = 3
TIMEFRAME = "1d"
DIRECTION = "long_only"

TARGET_VARIANTS = (("1.5r", 1.5), ("2r", 2.0), ("3r", 3.0))
WARMUP = max(K_DAY_LOW_LOOKBACK, ATR_LENGTH)

VERDICT_C12DD_READY = "CANDIDATE_12_DETECTOR_DRY_RUN_READY"
VERDICT_C12DD_BLOCKED = "CANDIDATE_12_DETECTOR_DRY_RUN_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_C12_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")


# --------------------------------------------------------------------------- #
# Pure detector primitives (single asset; no date / no weekday read)
# --------------------------------------------------------------------------- #

def prior_k_low(bars: list, t: int, k: int = K_DAY_LOW_LOOKBACK):
    """min(low) over the prior k bars [t-k .. t-1]. None if not enough history."""
    if t - k < 0 or t > len(bars):
        return None
    return min(float(bars[i]["low"]) for i in range(t - k, t))


def compute_atr14(bars: list, t: int, length: int = ATR_LENGTH):
    """Simple-mean ATR over the `length` true ranges ending at t. None if not
    enough history."""
    if t < length:
        return None
    trs = []
    for i in range(t - length + 1, t + 1):
        hi = float(bars[i]["high"])
        lo = float(bars[i]["low"])
        prev_close = float(bars[i - 1]["close"])
        trs.append(max(hi - lo, abs(hi - prev_close), abs(lo - prev_close)))
    return sum(trs) / length


def is_failed_breakdown_reclaim(bars: list, t: int,
                                k: int = K_DAY_LOW_LOOKBACK):
    """True iff low[t] < L_K (pierce) AND close[t] > L_K (close-confirmed
    reclaim). None if not enough history."""
    lk = prior_k_low(bars, t, k)
    if lk is None:
        return None
    return float(bars[t]["low"]) < lk and float(bars[t]["close"]) > lk


def compute_stop(entry_close: float, reclaim_low: float,
                 atr_at_entry: float) -> dict[str, Any]:
    """stop = reclaim_low - 0.25*ATR(14). Rejects zero/negative/at-or-above
    stop distance."""
    stop_price = float(reclaim_low) - STOP_ATR_BUFFER_MULTIPLIER * float(
        atr_at_entry)
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


def scan_c12_setups(bars: list, timeframe: str = TIMEFRAME,
                    direction: str = DIRECTION) -> list[dict[str, Any]]:
    """Failed-breakdown reclaim scanner over one asset's aligned synthetic bars.
    Returns one record per qualifying reclaim bar. Pure; reads NO date and NO
    weekday."""
    if timeframe != TIMEFRAME or direction != DIRECTION:
        raise ValueError("c12_detector_locked_to_1d_long_only")
    if not isinstance(bars, list):
        raise ValueError("bars_must_be_a_list")
    n = len(bars)
    setups: list[dict[str, Any]] = []
    for t in range(WARMUP, n):
        lk = prior_k_low(bars, t)
        if lk is None:
            continue
        low_t = float(bars[t]["low"])
        close_t = float(bars[t]["close"])
        if not (low_t < lk and close_t > lk):
            continue  # not a close-confirmed failed-breakdown reclaim
        atr = compute_atr14(bars, t)
        if atr is None:
            continue
        entry = close_t
        stop = compute_stop(entry, low_t, atr)
        rec = {
            "setup_index": t, "prior_k_low": round(lk, 6),
            "reclaim_low": round(low_t, 6), "entry_price": round(entry, 6),
            "atr_at_entry": round(atr, 6),
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
        rec["target_1_5r"] = floor["targets"]["1.5r"]
        rec["target_2r"] = floor["targets"]["2r"]
        rec["target_3r"] = floor["targets"]["3r"]
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
                      variant_r: float = 1.5) -> dict[str, Any]:
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
    """Constant-price OHLC bars; prior-K-low is a flat price*(1-rng). Bars carry
    NO date and NO weekday -- only OHLC."""
    return [{"open": price, "high": round(price * (1 + rng), 8),
             "low": round(price * (1 - rng), 8), "close": price}
            for _ in range(n)]


def _reclaim_bar(price: float, rng: float, pierce: float) -> dict:
    """A bar that pierces below price*(1-rng) intrabar but closes back at price
    (a close-confirmed failed-breakdown reclaim)."""
    return {"open": price, "high": round(price * (1 + rng), 8),
            "low": round(price * (1 - rng - pierce), 8), "close": price}


_T = 25  # reclaim index (>= warmup 20), leaving room for the 3-bar horizon


def fixture_valid_reclaim_accepted() -> list:
    """Clean failed-breakdown reclaim, normal ATR -> 1.5R clears the 81 bps
    floor -> ACCEPTED."""
    bars = _flat(30, 100.0, 0.01)
    bars[_T] = _reclaim_bar(100.0, 0.01, 0.006)
    return bars


def fixture_no_pierce_no_setup() -> list:
    """No bar makes a new K-day low (all flat) -> no reclaim -> NO setup."""
    return _flat(30, 100.0, 0.01)


def fixture_pierce_but_no_close_reclaim() -> list:
    """Bar pierces the K-day low but CLOSES below it (a confirmed breakdown, not
    a reclaim) -> NO setup."""
    bars = _flat(30, 100.0, 0.01)
    bars[_T] = {"open": 100.0, "high": round(100.0 * 1.01, 8),
                "low": round(100.0 * (1 - 0.016), 8),
                "close": round(100.0 * (1 - 0.011), 8)}  # close < L_K (=99.0)
    return bars


def fixture_below_floor_rejected() -> list:
    """Valid reclaim but a microscopic range/ATR -> even 3R target distance is
    below the 81 bps floor -> rejected_geometry_floor."""
    bars = _flat(30, 100.0, 0.0002)
    bars[_T] = _reclaim_bar(100.0, 0.0002, 0.0001)
    return bars


def fixture_target_hit() -> list:
    """Accepted reclaim, then the next bar's high clears the 1.5R target ->
    HIT (+1.5R)."""
    bars = fixture_valid_reclaim_accepted()
    bars[_T + 1] = {"open": 100.0, "high": 200.0, "low": 99.9, "close": 150.0}
    return bars


def fixture_stop_hit() -> list:
    """Accepted reclaim, then the next bar's low pierces the stop -> MISS (-1R)."""
    bars = fixture_valid_reclaim_accepted()
    bars[_T + 1] = {"open": 100.0, "high": 100.1, "low": 50.0, "close": 60.0}
    return bars


def fixture_same_bar_straddle() -> list:
    """Accepted reclaim, then a single bar hits BOTH stop and target -> STOP
    FIRST (-1R, conservative)."""
    bars = fixture_valid_reclaim_accepted()
    bars[_T + 1] = {"open": 100.0, "high": 200.0, "low": 50.0, "close": 100.0}
    return bars


def fixture_horizon_exit() -> list:
    """Accepted reclaim, then 3 flat bars hit neither stop nor target -> HORIZON
    exit at the +3 close (gross_r ~ 0)."""
    return fixture_valid_reclaim_accepted()  # base flat bars after _T


def fixture_two_reclaims_non_overlap() -> list:
    """Two accepted reclaims within the 3-bar hold (t and t+2) -> per-asset
    non-overlap drops the later one."""
    bars = _flat(33, 100.0, 0.01)
    bars[_T] = _reclaim_bar(100.0, 0.01, 0.006)        # low 98.4, close 100
    bars[_T + 2] = _reclaim_bar(100.0, 0.01, 0.020)    # low 97.0 < new L_K
    return bars


def run_c12_detector_dry_run() -> dict[str, Any]:
    """Run every synthetic fixture and report the outcomes. Pure; in-memory."""
    def _last(setups):
        return setups[-1] if setups else None

    accepted = _last(scan_c12_setups(fixture_valid_reclaim_accepted()))
    no_pierce = scan_c12_setups(fixture_no_pierce_no_setup())
    no_reclaim = scan_c12_setups(fixture_pierce_but_no_close_reclaim())
    below_floor = _last(scan_c12_setups(fixture_below_floor_rejected()))

    # invalid-stop guard (a genuine reclaim always has stop_distance > 0, so the
    # guard is proven directly on a degenerate geometry).
    invalid_stop_guard = compute_stop(100.0, 100.0, 0.0)  # zero distance

    def _outcome(fixture):
        # Select the INTENDED first reclaim at index _T (a high-range exit bar
        # can itself qualify as a later reclaim; we evaluate the first one).
        setups = scan_c12_setups(fixture())
        acc = next((s for s in setups
                    if s["status"] == "accepted_for_replay_review"
                    and s["setup_index"] == _T), None)
        return evaluate_one_setup_horizon(fixture(), acc, 1.5) if acc else None

    target = _outcome(fixture_target_hit)
    stop = _outcome(fixture_stop_hit)
    straddle = _outcome(fixture_same_bar_straddle)
    horizon = _outcome(fixture_horizon_exit)

    ov_setups = [s for s in scan_c12_setups(fixture_two_reclaims_non_overlap())
                 if s["status"] == "accepted_for_replay_review"]
    ov = apply_non_overlap(sorted(ov_setups, key=lambda s: s["setup_index"]),
                           fixture_two_reclaims_non_overlap(), 1.5)

    return {
        "valid_reclaim_status": (accepted or {}).get("status"),
        "no_pierce_setup_count": len(no_pierce),
        "no_reclaim_setup_count": len(no_reclaim),
        "below_floor_status": (below_floor or {}).get("status"),
        "invalid_stop_guard_valid": invalid_stop_guard["valid"],
        "target_outcome": (target or {}).get("outcome"),
        "target_gross_r": (target or {}).get("gross_r"),
        "stop_outcome": (stop or {}).get("outcome"),
        "stop_gross_r": (stop or {}).get("gross_r"),
        "straddle_outcome": (straddle or {}).get("outcome"),
        "straddle_gross_r": (straddle or {}).get("gross_r"),
        "horizon_outcome": (horizon or {}).get("outcome"),
        "non_overlap_accepted_setups": len(ov_setups),
        "non_overlap_kept": len(ov["kept"]),
        "non_overlap_dropped": len(ov["dropped"]),
        "uses_no_weekday_or_calendar_trigger": True,
    }


# --------------------------------------------------------------------------- #
# Detector spec + dry-run contract (chain-gated on the C12 spec; pure)
# --------------------------------------------------------------------------- #

C12DD_LABEL = (
    "SPARTA Candidate #12 Detector Spec + Synthetic Dry-Run (READ-ONLY, "
    "RESEARCH ONLY, SYNTHETIC FIXTURES ONLY). failed_breakdown_reclaim_reversal: "
    "close-confirmed reclaim of a pierced K=20 low; ATR(14) stop = reclaim_low - "
    "0.25*ATR; 1.5R/2R/3R; 81 bps floor; <=3-bar hold; stop-first straddle; "
    "per-asset non-overlap. NO date, NO weekday, NO real data, NO labels, NO "
    "replay, NO trading. EARLY GENERALIZATION + ANTI-DRIFT BATTERY STAYS LOCKED "
    "FOR THE LATER LABELS/REPLAY STAGE."
)

_CAPABILITY_FLAGS_FALSE = (
    "reads_real_data", "fetches_data", "stages_data_now", "creates_labels",
    "labels_now", "runs_replay", "runs_replay_now", "runs_robustness",
    "runs_generalization_now", "runs_portfolio_compute", "calls_api",
    "uses_network", "uses_credentials", "uses_wallet", "uses_account",
    "connects_broker", "connects_exchange", "uses_real_money",
    "contains_order_logic", "contains_portfolio_allocation_logic",
    "deploys_capital", "starts_scheduler", "sends_notifications",
    "auto_commits", "auto_pushes", "uses_weekday_or_calendar_trigger",
    "is_single_asset_edge", "relies_on_long_drift_or_bull_carry",
    "fits_parameters", "is_a_rescue_attempt", "authorizes_paper_execution",
    "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
    "unlocks_downstream_gate", "claims_profitability", "claims_edge",
    "claims_paper_or_live_readiness", "executes", "writes_files",
)


def get_candidate_12_detector_dry_run_label() -> str:
    return C12DD_LABEL


def get_candidate_12_detector_dry_run_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_candidate_12_detector_spec_dry_run(repo_root: Any = ".",
                                             tracked_paths: list | None = None
                                             ) -> dict[str, Any]:
    """Assemble the C12 detector spec + synthetic dry-run record. Chain-gated on
    the READY candidate spec. Runs the synthetic dry-run and pins the required
    proofs. Pure; in-memory; synthetic fixtures only."""
    dry = run_c12_detector_dry_run()
    dry_again = run_c12_detector_dry_run()
    proofs = {
        "valid_reclaim_setup_accepted":
            dry["valid_reclaim_status"] == "accepted_for_replay_review",
        "no_setup_when_no_pierce": dry["no_pierce_setup_count"] == 0,
        "no_setup_when_close_does_not_reclaim":
            dry["no_reclaim_setup_count"] == 0,
        "invalid_stop_guard_rejects": dry["invalid_stop_guard_valid"] is False,
        "below_floor_rejected":
            dry["below_floor_status"] == "rejected_geometry_floor",
        "target_hit_outcome":
            dry["target_outcome"] == "hit" and dry["target_gross_r"] == 1.5,
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
        "no_calendar_or_weekday_trigger":
            dry["uses_no_weekday_or_calendar_trigger"] is True,
        "no_labels_replay_data_fetch_trading": True,
        "deterministic": dry == dry_again,
    }
    record: dict[str, Any] = {
        "schema_version": 1, "label": C12DD_LABEL, "mode": C12D_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_number": 12, "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "symbol_universe": list(SYMBOL_UNIVERSE), "min_assets": MIN_ASSETS,
        "timeframe": TIMEFRAME, "direction": DIRECTION,
        "k_day_low_lookback": K_DAY_LOW_LOOKBACK, "atr_length": ATR_LENGTH,
        "stop_atr_buffer_multiplier": STOP_ATR_BUFFER_MULTIPLIER,
        "target_variants": [n for n, _ in TARGET_VARIANTS],
        "target_r_multiples": dict(TARGET_R_MULTIPLES),
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "max_hold_bars": MAX_HOLD_BARS,
        "max_horizon_exit_share": MAX_HORIZON_EXIT_SHARE,
        "same_bar_straddle_policy": "stop_first_conservative_miss",
        "non_overlap_policy": "per_asset_reduce_or_keep_only_never_add",
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
        "data_fetch_gate_locked": True, "robustness_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "synthetic_fixtures_only": True, "no_real_data": True,
        "no_data_fetch": True, "no_labels": True, "no_replay": True,
        "no_robustness_run": True, "no_generalization_run": True,
        "no_portfolio_compute": True, "no_paper_trading": True,
        "no_live_trading": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_weekday_trigger": True,
        "no_calendar_trigger": True, "no_single_asset_edge": True,
        "no_long_drift_or_bull_carry_reliance": True,
        "no_parameter_fitting": True, "no_profitability_claim": True,
        "no_paper_live_readiness_claim": True, "no_downstream_gate_unlock": True,
    }

    spec = build_candidate_12_spec(repo_root, tracked_paths or [])
    record["spec_verdict"] = spec.get("verdict")
    if spec.get("verdict") != VERDICT_C12S_READY:
        record["verdict"] = VERDICT_C12DD_BLOCKED
        record["blockers"].append("spec_not_ready")
        return record
    if not all(proofs.values()):
        record["verdict"] = VERDICT_C12DD_BLOCKED
        record["blockers"].append("dry_run_proof_failed")
        return record

    record["verdict"] = VERDICT_C12DD_READY
    return record


def validate_candidate_12_detector_spec_dry_run(record: dict[str, Any]
                                                ) -> dict[str, Any]:
    """Anti-tamper validator. READY only when all proofs hold, the detector
    geometry is intact, no calendar/weekday/single-asset/long-drift behavior,
    and all execution gates are locked."""
    failures: list = []
    if record.get("verdict") != VERDICT_C12DD_READY:
        failures.append("verdict_not_ready")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("spec_verdict") != VERDICT_C12S_READY:
        failures.append("spec_verdict_tampered")

    proofs = record.get("dry_run_proofs") or {}
    for key in ("valid_reclaim_setup_accepted", "no_setup_when_no_pierce",
                "no_setup_when_close_does_not_reclaim",
                "invalid_stop_guard_rejects", "below_floor_rejected",
                "target_hit_outcome", "stop_hit_outcome",
                "same_bar_straddle_is_stop_first", "horizon_exit_when_neither",
                "per_asset_non_overlap_drops_later",
                "no_calendar_or_weekday_trigger",
                "no_labels_replay_data_fetch_trading", "deterministic"):
        if proofs.get(key) is not True:
            failures.append("proof_failed_%s" % key)

    if len(record.get("symbol_universe") or []) < MIN_ASSETS:
        failures.append("single_asset_universe")
    if record.get("k_day_low_lookback") != K_DAY_LOW_LOOKBACK:
        failures.append("lookback_tampered")
    if record.get("stop_atr_buffer_multiplier") != STOP_ATR_BUFFER_MULTIPLIER:
        failures.append("stop_buffer_tampered")
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
            "per_asset_reduce_or_keep_only_never_add"):
        failures.append("non_overlap_policy_tampered")
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
                "no_labels", "no_replay", "no_portfolio_compute",
                "no_paper_trading", "no_live_trading", "no_calendar_trigger",
                "no_weekday_trigger", "no_single_asset_edge",
                "no_long_drift_or_bull_carry_reliance",
                "no_paper_live_readiness_claim"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("labels_gate_locked", "replay_gate_locked",
                "data_fetch_gate_locked", "robustness_gate_locked",
                "paper_trading_gate_locked", "live_gate_locked",
                "human_review_required"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

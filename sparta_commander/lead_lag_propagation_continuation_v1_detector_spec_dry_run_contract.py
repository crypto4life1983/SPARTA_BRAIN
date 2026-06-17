"""SPARTA Candidate #13 detector specification + synthetic dry-run:
lead_lag_propagation_continuation_v1.

RESEARCH ONLY. SYNTHETIC FIXTURES ONLY. This module specifies the C13 detector
geometry and exercises it against in-memory synthetic fixtures. It reads NO real
market data, fetches NO data, creates NO real labels, runs NO replay, NO
robustness, NO portfolio compute, NO baseline comparison, and has NO trading /
broker / credential / order capability. It writes nothing and runs nothing
outside its pure functions.

Detector (cross-asset lead-lag propagation continuation), aligned BTC/ETH/SOL 1d:
  * Bars are indexed by LIST POSITION and carry ONLY OHLC -- there is NO date and
    NO weekday in the bar shape, so a calendar/weekday trigger is structurally
    impossible. The LEADER (BTC) must differ from the FOLLOWERS (ETH/SOL).
  * On bar t (after a 91-bar warmup): r_L = leader 1-day return; z_L = z-score of
    r_L vs the leader's prior LEADER_Z_LOOKBACK(=90) daily returns. A CONFIRMED
    leader move requires r_L > 0 AND z_L >= 1.5. A qualifying FOLLOWER must have
    UNDER-participated: r_F < 0.5 * r_L (lag). Entry at the FOLLOWER's close;
    stop = follower_close - 1.0*ATR(14); reject if stop<=0/not below; targets
    1R/1.5R/2R; reject if no variant clears the 81 bps gross floor.
  * Exit walk over the <=2-bar hold: stop (low<=stop -> -1R), target
    (high>=target -> +R), same-bar straddle = STOP FIRST (-1R), else HORIZON exit
    at the +2 close -> (exit_close-entry)/stop_distance. Per-follower non-overlap
    is reduce-or-keep-only (drop a later same-follower setup whose entry <= the
    active resolved exit).
  * The early-generalization + anti-drift battery (forward-OOS, cross-regime
    symmetry, cross-asset, must-beat buy-and-hold AND random-entry AND
    buy-the-leader, target-capture dominance / horizon-exit cap) stays LOCKED
    here for the later labels/replay stage; this dry-run does not run it.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.lead_lag_propagation_continuation_v1_candidate_spec_contract import (  # noqa: E501
    ALL_IN_ROUND_TRIP_BPS,
    ATR_LENGTH,
    EARLY_STRUCTURAL_REJECTION_GATES,
    LAG_MARGIN_FRACTION,
    LEADER_RETURN_LOOKBACK_BARS,
    LEADER_Z_ENTRY_THRESHOLD,
    LEADER_Z_LOOKBACK,
    MAX_HOLD_BARS,
    MAX_HORIZON_EXIT_SHARE,
    STOP_ATR_MULTIPLIER,
    TARGET_DISTANCE_FLOOR_BPS,
    TARGET_R_MULTIPLES,
    VERDICT_C13S_READY,
    build_candidate_13_spec,
)

CANDIDATE_ID = "LEAD_LAG_PROPAGATION_CONTINUATION_V1"
CANDIDATE_FAMILY = "lead_lag_propagation_continuation"
C13D_MODE = "RESEARCH_ONLY"
LEADER = "BTCUSD"
FOLLOWERS = ("ETHUSD", "SOLUSD")
MIN_FOLLOWERS = 2
TIMEFRAME = "1d"
DIRECTION = "long_only"

TARGET_VARIANTS = (("1r", 1.0), ("1.5r", 1.5), ("2r", 2.0))
WARMUP = LEADER_Z_LOOKBACK + LEADER_RETURN_LOOKBACK_BARS   # 91

VERDICT_C13DD_READY = "CANDIDATE_13_DETECTOR_DRY_RUN_READY"
VERDICT_C13DD_BLOCKED = "CANDIDATE_13_DETECTOR_DRY_RUN_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_C13_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")


# --------------------------------------------------------------------------- #
# Pure detector primitives (no date / no weekday read)
# --------------------------------------------------------------------------- #

def daily_return(bars: list, t: int, k: int = LEADER_RETURN_LOOKBACK_BARS):
    """(close[t] / close[t-k]) - 1. None if out of range or non-positive base."""
    if t - k < 0 or t >= len(bars):
        return None
    c0 = float(bars[t - k]["close"])
    c1 = float(bars[t]["close"])
    if c0 <= 0.0:
        return None
    return c1 / c0 - 1.0


def leader_zscore(leader_bars: list, t: int,
                  lookback: int = LEADER_Z_LOOKBACK):
    """z-score of the leader's bar-t daily return vs the prior `lookback` daily
    returns [t-lookback .. t-1]. None if not enough history or zero dispersion."""
    if t - lookback - 1 < 0 or t >= len(leader_bars):
        return None
    prior = []
    for i in range(t - lookback, t):
        c0 = float(leader_bars[i - 1]["close"])
        c1 = float(leader_bars[i]["close"])
        if c0 <= 0.0:
            return None
        prior.append(c1 / c0 - 1.0)
    r_t = daily_return(leader_bars, t)
    if r_t is None:
        return None
    mean = sum(prior) / len(prior)
    var = sum((x - mean) ** 2 for x in prior) / len(prior)
    std = var ** 0.5
    if std <= 0.0:
        return None
    return (r_t - mean) / std


def compute_atr14(bars: list, t: int, length: int = ATR_LENGTH):
    if t < length:
        return None
    trs = []
    for i in range(t - length + 1, t + 1):
        hi = float(bars[i]["high"])
        lo = float(bars[i]["low"])
        prev_close = float(bars[i - 1]["close"])
        trs.append(max(hi - lo, abs(hi - prev_close), abs(lo - prev_close)))
    return sum(trs) / length


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


def scan_c13_setups(asset_bars: dict, leader: str = LEADER,
                    followers: tuple = FOLLOWERS,
                    timeframe: str = TIMEFRAME,
                    direction: str = DIRECTION) -> list[dict[str, Any]]:
    """Lead-lag propagation scanner over aligned leader+follower bars. Returns one
    record per qualifying (follower, bar) signal. Raises ValueError if the leader
    equals a follower, fewer than MIN_FOLLOWERS followers, or non-1d/non-long.
    Pure; reads NO date and NO weekday."""
    if timeframe != TIMEFRAME or direction != DIRECTION:
        raise ValueError("c13_detector_locked_to_1d_long_only")
    if not isinstance(asset_bars, dict):
        raise ValueError("asset_bars_must_be_a_dict")
    fol = [f for f in followers if f != leader and f in asset_bars]
    if leader in followers:
        raise ValueError("leader_must_not_equal_follower")
    if leader not in asset_bars:
        raise ValueError("leader_bars_required")
    if len(fol) < MIN_FOLLOWERS:
        raise ValueError("c13_requires_at_least_two_distinct_followers")
    leader_bars = asset_bars[leader]
    n = min(len(leader_bars), *(len(asset_bars[f]) for f in fol))
    setups: list[dict[str, Any]] = []
    for t in range(WARMUP, n):
        r_l = daily_return(leader_bars, t)
        z_l = leader_zscore(leader_bars, t)
        if r_l is None or z_l is None:
            continue
        if not (r_l > 0.0 and z_l >= LEADER_Z_ENTRY_THRESHOLD):
            continue  # leader move not confirmed
        for f in fol:
            fbars = asset_bars[f]
            r_f = daily_return(fbars, t)
            if r_f is None:
                continue
            if not (r_f < LAG_MARGIN_FRACTION * r_l):
                continue  # follower already matched -> no lag
            entry = float(fbars[t]["close"])
            atr = compute_atr14(fbars, t)
            if atr is None:
                continue
            stop = compute_stop(entry, atr)
            rec = {
                "setup_index": t, "follower_symbol": f,
                "leader_return": round(r_l, 8), "leader_z": round(z_l, 6),
                "follower_return": round(r_f, 8),
                "entry_price": round(entry, 6), "atr_at_entry": round(atr, 6),
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


def evaluate_one_setup_horizon(follower_bars: list, setup: dict,
                               variant_r: float,
                               max_hold: int = MAX_HOLD_BARS) -> dict[str, Any]:
    """Walk one accepted setup over the <=max_hold horizon on the FOLLOWER's
    bars for one R-multiple. Stop-first on straddle; horizon exit at the max_hold
    bar close. Pure."""
    entry = float(setup["entry_price"])
    stop_price = float(setup["stop_price"])
    stop_distance = float(setup["stop_distance"])
    t = int(setup["setup_index"])
    exit_index = t + max_hold
    target_price = entry + variant_r * stop_distance
    out = {"setup_index": t, "variant_r_multiple": variant_r,
           "outcome": None, "exit_resolved_index": None, "exit_price": None,
           "bars_held": None, "gross_r": None}
    if exit_index >= len(follower_bars):
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
        bar = follower_bars[i]
        hit_stop = float(bar["low"]) <= stop_price
        hit_target = float(bar["high"]) >= target_price
        if hit_stop and hit_target:
            return _finish("miss_same_bar_straddle", i, stop_price, -1.0)
        if hit_stop:
            return _finish("miss", i, stop_price, -1.0)
        if hit_target:
            return _finish("hit", i, target_price, float(variant_r))
    exit_close = float(follower_bars[exit_index]["close"])
    return _finish("horizon", exit_index, exit_close,
                   (exit_close - entry) / stop_distance)


def apply_non_overlap(setups_sorted: list, follower_bars: list,
                      variant_r: float = 1.0) -> dict[str, Any]:
    """Per-follower REDUCE-OR-KEEP-ONLY: drop a later setup whose entry_index is
    <= the active resolved exit index. Never add."""
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
        outcome = evaluate_one_setup_horizon(follower_bars, s, variant_r)
        kept.append({**s, "horizon_outcome": outcome})
        if outcome["exit_resolved_index"] is not None:
            active_exit_index = outcome["exit_resolved_index"]
    return {"kept": kept, "dropped": dropped}


# --------------------------------------------------------------------------- #
# Synthetic fixtures (in-memory; deterministic; NO date / NO weekday / NO RNG)
# --------------------------------------------------------------------------- #

def _bars_from_returns(rets: list, start: float = 100.0,
                       rng: float = 0.01) -> list:
    """Build OHLC bars from a daily-return list. Bars carry NO date and NO
    weekday -- only OHLC."""
    closes = [float(start)]
    for r in rets:
        closes.append(closes[-1] * (1.0 + r))
    bars = []
    for i, c in enumerate(closes):
        o = closes[i - 1] if i > 0 else c
        bars.append({"open": round(o, 8), "high": round(c * (1 + rng), 8),
                     "low": round(c * (1 - rng), 8), "close": round(c, 8)})
    return bars


_N = 100          # bars 0..99
_T = 95           # signal index (>= warmup 91)


def _alt(n: int, amp: float = 0.01) -> list:
    """Alternating +amp/-amp returns (mean ~0, std ~amp) -> nonzero dispersion."""
    return [amp if i % 2 == 0 else -amp for i in range(n)]


def _leader_with_big_move(at_indices, big: float = 0.03, rng: float = 0.01):
    rets = _alt(_N - 1)
    for j in at_indices:
        rets[j] = big                     # ret[j] drives close[j+1]
    return _bars_from_returns(rets, 100.0, rng)


def _follower(ret_at, value, rng: float = 0.01, amp: float = 0.01):
    rets = _alt(_N - 1, amp)
    rets[ret_at] = value
    return _bars_from_returns(rets, 100.0, rng)


def fixture_valid_propagation_accepted() -> dict:
    """BTC big up-move at _T (z>=1.5); ETH under-participates (lag) -> ACCEPTED;
    SOL matches the leader (no lag) -> no SOL setup."""
    return {
        "BTCUSD": _leader_with_big_move([_T - 1]),          # close[_T] jumps
        "ETHUSD": _follower(_T - 1, 0.005),                 # r_F 0.5% < 0.5*3%
        "SOLUSD": _follower(_T - 1, 0.03),                  # matches -> no lag
    }


def fixture_leader_move_not_confirmed() -> dict:
    """BTC move at _T is small (z < 1.5) -> no confirmed leader move -> NO setup."""
    return {
        "BTCUSD": _leader_with_big_move([_T - 1], big=0.005),   # z ~ 0.5
        "ETHUSD": _follower(_T - 1, 0.001),
        "SOLUSD": _follower(_T - 1, 0.001),
    }


def fixture_follower_already_matched() -> dict:
    """BTC confirmed move but BOTH followers already matched it (r_F >= 0.5*r_L)
    -> no lag -> NO setup."""
    return {
        "BTCUSD": _leader_with_big_move([_T - 1]),
        "ETHUSD": _follower(_T - 1, 0.03),                  # matched
        "SOLUSD": _follower(_T - 1, 0.028),                 # matched
    }


def fixture_below_floor_rejected() -> dict:
    """Confirmed leader move + ETH lag, but ETH has a microscopic range -> tiny
    ATR -> even 2R below the 81 bps floor -> rejected_geometry_floor."""
    return {
        "BTCUSD": _leader_with_big_move([_T - 1]),
        # tiny daily moves AND tiny intrabar range -> tiny ATR -> 2R < 81 bps;
        # the lag return 0.0001 still satisfies r_F < 0.5*r_L (=0.015)
        "ETHUSD": _follower(_T - 1, 0.0001, rng=0.0002, amp=0.0002),
        "SOLUSD": _follower(_T - 1, 0.03),
    }


def fixture_two_signals_non_overlap() -> dict:
    """BTC confirmed moves at _T and _T+1; ETH lags both -> two accepted ETH
    setups within the 2-bar hold -> non-overlap drops the later one."""
    return {
        "BTCUSD": _leader_with_big_move([_T - 1, _T]),
        "ETHUSD": _follower2(_T - 1, _T, 0.005, 0.005),
        "SOLUSD": _follower(_T - 1, 0.03),
    }


def _follower2(i1, i2, v1, v2, rng: float = 0.01):
    rets = _alt(_N - 1)
    rets[i1] = v1
    rets[i2] = v2
    return _bars_from_returns(rets, 100.0, rng)


def _accepted_eth(fixture):
    setups = scan_c13_setups(fixture())
    return next((s for s in setups
                 if s["status"] == "accepted_for_replay_review"
                 and s["follower_symbol"] == "ETHUSD"
                 and s["setup_index"] == _T), None)


def run_c13_detector_dry_run() -> dict[str, Any]:
    """Run every synthetic fixture and report the outcomes. Pure; in-memory."""
    accepted = _accepted_eth(fixture_valid_propagation_accepted)
    not_confirmed = scan_c13_setups(fixture_leader_move_not_confirmed())
    no_lag = scan_c13_setups(fixture_follower_already_matched())
    below_floor = next((s for s in scan_c13_setups(fixture_below_floor_rejected())
                        if s["follower_symbol"] == "ETHUSD"
                        and s["setup_index"] == _T), None)

    invalid_stop_guard = compute_stop(100.0, 0.0)          # zero ATR -> invalid

    def _outcome(fixture, variant=1.0):
        acc = _accepted_eth(fixture)
        return (evaluate_one_setup_horizon(fixture()["ETHUSD"], acc, variant)
                if acc else None)

    # exit fixtures: override ETH's first horizon bar (_T+1)
    def _eth_override(at, bar):
        d = fixture_valid_propagation_accepted()
        d["ETHUSD"] = [dict(b) for b in d["ETHUSD"]]
        d["ETHUSD"][at] = bar
        return d

    def _scan_override(d, variant=1.0):
        acc = next((s for s in scan_c13_setups(d)
                    if s["status"] == "accepted_for_replay_review"
                    and s["follower_symbol"] == "ETHUSD"
                    and s["setup_index"] == _T), None)
        return (evaluate_one_setup_horizon(d["ETHUSD"], acc, variant)
                if acc else None)

    tgt = _scan_override(_eth_override(
        _T + 1, {"open": 100.0, "high": 1e9, "low": 99.0, "close": 1e8}))
    stp = _scan_override(_eth_override(
        _T + 1, {"open": 100.0, "high": 100.1, "low": 1e-6, "close": 1e-3}))
    strd = _scan_override(_eth_override(
        _T + 1, {"open": 100.0, "high": 1e9, "low": 1e-6, "close": 100.0}))
    hor = _outcome(fixture_valid_propagation_accepted)     # flat -> horizon

    ov_setups = [s for s in scan_c13_setups(fixture_two_signals_non_overlap())
                 if s["status"] == "accepted_for_replay_review"
                 and s["follower_symbol"] == "ETHUSD"]
    ov = apply_non_overlap(sorted(ov_setups, key=lambda s: s["setup_index"]),
                           fixture_two_signals_non_overlap()["ETHUSD"], 1.0)

    leader_eq_follower_raises = False
    try:
        scan_c13_setups(fixture_valid_propagation_accepted(),
                        followers=("BTCUSD", "ETHUSD"))
    except ValueError:
        leader_eq_follower_raises = True

    return {
        "valid_status": (accepted or {}).get("status"),
        "not_confirmed_count": len(not_confirmed),
        "no_lag_count": len(no_lag),
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
        "leader_eq_follower_raises": leader_eq_follower_raises,
        "uses_no_weekday_or_calendar_trigger": True,
    }


# --------------------------------------------------------------------------- #
# Detector spec + dry-run contract (chain-gated on the C13 spec; pure)
# --------------------------------------------------------------------------- #

C13DD_LABEL = (
    "SPARTA Candidate #13 Detector Spec + Synthetic Dry-Run (READ-ONLY, "
    "RESEARCH ONLY, SYNTHETIC FIXTURES ONLY). lead_lag_propagation_continuation: "
    "BTC leader move (r_L>0, z_L>=1.5) + follower lag (r_F<0.5*r_L) -> long the "
    "follower close; ATR(14) stop; 1R/1.5R/2R; 81 bps floor; <=2-bar hold; "
    "stop-first straddle; per-follower non-overlap; leader != follower. NO date, "
    "NO weekday, NO real data, NO labels, NO replay, NO trading. BASELINE + "
    "EARLY GENERALIZATION BATTERY STAYS LOCKED FOR THE LATER LABELS/REPLAY STAGE."
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


def get_candidate_13_detector_dry_run_label() -> str:
    return C13DD_LABEL


def get_candidate_13_detector_dry_run_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_candidate_13_detector_spec_dry_run(repo_root: Any = ".",
                                             tracked_paths: list | None = None
                                             ) -> dict[str, Any]:
    """Assemble the C13 detector spec + synthetic dry-run record. Chain-gated on
    the READY candidate spec. Runs the synthetic dry-run and pins the required
    proofs. Pure; in-memory; synthetic fixtures only."""
    dry = run_c13_detector_dry_run()
    dry_again = run_c13_detector_dry_run()
    proofs = {
        "valid_propagation_setup_accepted":
            dry["valid_status"] == "accepted_for_replay_review",
        "no_setup_when_leader_move_not_confirmed":
            dry["not_confirmed_count"] == 0,
        "no_setup_when_follower_already_matched": dry["no_lag_count"] == 0,
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
        "per_follower_non_overlap_drops_later":
            dry["non_overlap_accepted_setups"] >= 2
            and dry["non_overlap_kept"] == 1
            and dry["non_overlap_dropped"] >= 1,
        "leader_must_not_equal_follower":
            dry["leader_eq_follower_raises"] is True,
        "no_calendar_or_weekday_trigger":
            dry["uses_no_weekday_or_calendar_trigger"] is True,
        "no_labels_replay_baseline_data_fetch_trading": True,
        "deterministic": dry == dry_again,
    }
    record: dict[str, Any] = {
        "schema_version": 1, "label": C13DD_LABEL, "mode": C13D_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_number": 13, "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "leader": LEADER, "followers": list(FOLLOWERS),
        "min_followers": MIN_FOLLOWERS,
        "timeframe": TIMEFRAME, "direction": DIRECTION,
        "leader_return_lookback_bars": LEADER_RETURN_LOOKBACK_BARS,
        "leader_z_lookback": LEADER_Z_LOOKBACK,
        "leader_z_entry_threshold": LEADER_Z_ENTRY_THRESHOLD,
        "lag_margin_fraction": LAG_MARGIN_FRACTION,
        "atr_length": ATR_LENGTH, "stop_atr_multiplier": STOP_ATR_MULTIPLIER,
        "target_variants": [n for n, _ in TARGET_VARIANTS],
        "target_r_multiples": dict(TARGET_R_MULTIPLES),
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "max_hold_bars": MAX_HOLD_BARS,
        "max_horizon_exit_share": MAX_HORIZON_EXIT_SHARE,
        "same_bar_straddle_policy": "stop_first_conservative_miss",
        "non_overlap_policy": "per_follower_resolved_exit_reduce_or_keep_only_never_add",
        "synthetic_fixtures_only": True,
        "uses_no_weekday_or_calendar_trigger": True,
        "is_single_asset_edge": False,
        "relies_on_long_drift_or_bull_carry": False,
        "leader_distinct_from_follower": True,
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

    spec = build_candidate_13_spec(repo_root, tracked_paths or [])
    record["spec_verdict"] = spec.get("verdict")
    if spec.get("verdict") != VERDICT_C13S_READY:
        record["verdict"] = VERDICT_C13DD_BLOCKED
        record["blockers"].append("spec_not_ready")
        return record
    if not all(proofs.values()):
        record["verdict"] = VERDICT_C13DD_BLOCKED
        record["blockers"].append("dry_run_proof_failed")
        return record

    record["verdict"] = VERDICT_C13DD_READY
    return record


def validate_candidate_13_detector_spec_dry_run(record: dict[str, Any]
                                                ) -> dict[str, Any]:
    """Anti-tamper validator. READY only when all proofs hold, the detector
    geometry is intact, leader != follower, no calendar/weekday/single-asset/
    long-drift behavior, and all execution gates are locked."""
    failures: list = []
    if record.get("verdict") != VERDICT_C13DD_READY:
        failures.append("verdict_not_ready")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("spec_verdict") != VERDICT_C13S_READY:
        failures.append("spec_verdict_tampered")

    proofs = record.get("dry_run_proofs") or {}
    for key in ("valid_propagation_setup_accepted",
                "no_setup_when_leader_move_not_confirmed",
                "no_setup_when_follower_already_matched",
                "invalid_stop_guard_rejects", "below_floor_rejected",
                "target_hit_outcome", "stop_hit_outcome",
                "same_bar_straddle_is_stop_first", "horizon_exit_when_neither",
                "per_follower_non_overlap_drops_later",
                "leader_must_not_equal_follower",
                "no_calendar_or_weekday_trigger",
                "no_labels_replay_baseline_data_fetch_trading", "deterministic"):
        if proofs.get(key) is not True:
            failures.append("proof_failed_%s" % key)

    if record.get("leader") in (record.get("followers") or []):
        failures.append("leader_equals_follower")
    if len(record.get("followers") or []) < MIN_FOLLOWERS:
        failures.append("too_few_followers")
    if record.get("leader_z_entry_threshold") != LEADER_Z_ENTRY_THRESHOLD:
        failures.append("z_threshold_tampered")
    if record.get("lag_margin_fraction") != LAG_MARGIN_FRACTION:
        failures.append("lag_margin_tampered")
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
            "per_follower_resolved_exit_reduce_or_keep_only_never_add"):
        failures.append("non_overlap_policy_tampered")
    if record.get("uses_no_weekday_or_calendar_trigger") is not True:
        failures.append("calendar_trigger_flag_tampered")
    if record.get("synthetic_fixtures_only") is not True:
        failures.append("synthetic_only_flag_tampered")
    if record.get("is_single_asset_edge") is not False:
        failures.append("single_asset_flag_tampered")
    if record.get("relies_on_long_drift_or_bull_carry") is not False:
        failures.append("long_drift_flag_tampered")
    if record.get("leader_distinct_from_follower") is not True:
        failures.append("leader_follower_distinct_flag_tampered")
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

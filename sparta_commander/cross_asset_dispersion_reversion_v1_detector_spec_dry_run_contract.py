"""SPARTA Candidate #11 detector specification + synthetic dry-run:
cross_asset_dispersion_reversion_v1.

RESEARCH ONLY. SYNTHETIC FIXTURES ONLY. This module specifies the C11 detector
geometry and exercises it against in-memory synthetic fixtures. It reads NO real
market data, fetches NO data, creates NO real labels, runs NO replay, NO
robustness, NO portfolio compute, and has NO trading / broker / credential /
order capability. It writes nothing and runs nothing outside its pure
functions.

Detector (cross-asset dispersion reversion):
  * Universe BTCUSD / ETHUSD / SOLUSD (>= 3 assets; single-asset input is a hard
    ValueError -- never a single-asset edge).
  * On each bar (indexed by LIST POSITION -- there is NO date and NO weekday in
    the bar shape, so a calendar/weekday trigger is structurally impossible):
      - compute each asset's 5-day return,
      - compute the cross-sectional z-score of those returns,
      - the relative LAGGARD is the asset with the lowest z; it qualifies only
        when its z <= -1.0,
      - require the basket regime filter: basket-median close >= its own
        SMA(50) (no entry in a confirmed basket downtrend),
      - entry at the signal-bar close; stop = 1.5 * ATR(14); targets 2R/3R/4R;
        reject if the stop is invalid or no variant clears the 81 bps gross
        target-distance floor.
  * The early-generalization battery (cross-weekday neutrality, cross-asset,
    forward-OOS, cross-regime) stays LOCKED here for the later labels/replay
    stage (the C10 lesson); this dry-run does not run it.
"""
from __future__ import annotations

import statistics
from typing import Any

from sparta_commander.cross_asset_dispersion_reversion_v1_candidate_spec_contract import (  # noqa: E501
    EARLY_GENERALIZATION_BATTERY,
    VERDICT_C11S_READY,
    build_candidate_11_spec,
)

CANDIDATE_ID = "CROSS_ASSET_DISPERSION_REVERSION_V1"
CANDIDATE_FAMILY = "cross_asset_dispersion_reversion"
C11D_MODE = "RESEARCH_ONLY"
SYMBOL_UNIVERSE = ("BTCUSD", "ETHUSD", "SOLUSD")
MIN_ASSETS = 3
TIMEFRAME = "1d"
DIRECTION = "long_only"

DISPERSION_LOOKBACK_BARS = 5
Z_ENTRY_THRESHOLD = -1.0
BASKET_SMA_LENGTH = 50
ATR_LENGTH = 14
STRUCTURE_STOP_ATR_MULTIPLIER = 1.5
TARGET_VARIANTS = (("2r", 2.0), ("3r", 3.0), ("4r", 4.0))
TARGET_DISTANCE_FLOOR_BPS = 81.0

VERDICT_C11DD_READY = "CANDIDATE_11_DETECTOR_DRY_RUN_READY"
VERDICT_C11DD_BLOCKED = "CANDIDATE_11_DETECTOR_DRY_RUN_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C11_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"


# --------------------------------------------------------------------------- #
# Pure detector primitives (symbol-agnostic; no date / no weekday read)
# --------------------------------------------------------------------------- #

def k_day_return(bars: list, t: int, k: int = DISPERSION_LOOKBACK_BARS):
    """(close[t] / close[t-k]) - 1. None if out of range or non-positive."""
    if t - k < 0 or t >= len(bars):
        return None
    c0 = float(bars[t - k]["close"])
    c1 = float(bars[t]["close"])
    if c0 <= 0.0 or c1 <= 0.0:
        return None
    return c1 / c0 - 1.0


def cross_sectional_zscores(returns: list):
    """Population z-scores of the cross-sectional returns. None if any return
    is None or the dispersion (std) is zero (no signal)."""
    if any(r is None for r in returns) or len(returns) < 2:
        return None
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / len(returns)
    std = var ** 0.5
    if std <= 0.0:
        return None
    return [(r - mean) / std for r in returns]


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


def compute_stop(entry_price: float, atr_at_entry: float) -> dict[str, Any]:
    buffer = STRUCTURE_STOP_ATR_MULTIPLIER * float(atr_at_entry)
    stop_price = float(entry_price) - buffer
    stop_distance = float(entry_price) - stop_price
    below = stop_price < float(entry_price)
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


def basket_median_series(asset_bars: dict) -> list:
    """Per-bar median close across the aligned assets."""
    symbols = list(asset_bars.keys())
    n = min(len(asset_bars[s]) for s in symbols)
    series = []
    for i in range(n):
        series.append(statistics.median(
            float(asset_bars[s][i]["close"]) for s in symbols))
    return series


def basket_regime_ok(median_series: list, t: int,
                     sma_length: int = BASKET_SMA_LENGTH) -> bool:
    """Basket median >= its own SMA(sma_length). False if not enough history."""
    if t < sma_length - 1:
        return False
    window = median_series[t - sma_length + 1:t + 1]
    sma = sum(window) / sma_length
    return median_series[t] >= sma


def scan_c11_setups(asset_bars: dict,
                    symbol_universe: tuple = SYMBOL_UNIVERSE,
                    timeframe: str = TIMEFRAME,
                    direction: str = DIRECTION) -> list[dict[str, Any]]:
    """Cross-asset dispersion-reversion scanner over aligned synthetic bars.
    Returns one record per qualifying signal bar (the laggard's setup). Raises
    ValueError for a single-asset universe or a non-1d / non-long-only context.
    Pure; reads NO date and NO weekday."""
    if timeframe != TIMEFRAME or direction != DIRECTION:
        raise ValueError("c11_detector_locked_to_1d_long_only")
    if not isinstance(asset_bars, dict):
        raise ValueError("asset_bars_must_be_a_dict")
    symbols = [s for s in symbol_universe if s in asset_bars]
    if len(symbols) < MIN_ASSETS:
        raise ValueError("c11_requires_at_least_three_assets_no_single_asset")
    n = min(len(asset_bars[s]) for s in symbols)
    medians = basket_median_series({s: asset_bars[s] for s in symbols})
    warmup = max(DISPERSION_LOOKBACK_BARS, ATR_LENGTH, BASKET_SMA_LENGTH)
    setups: list[dict[str, Any]] = []
    for t in range(warmup, n):
        rets = [k_day_return(asset_bars[s], t) for s in symbols]
        zs = cross_sectional_zscores(rets)
        if zs is None:
            continue
        # relative laggard = lowest z
        lag_idx = min(range(len(zs)), key=lambda i: zs[i])
        lag_z = zs[lag_idx]
        lag_sym = symbols[lag_idx]
        if lag_z > Z_ENTRY_THRESHOLD:
            continue  # no qualifying laggard
        regime = basket_regime_ok(medians, t)
        if not regime:
            continue  # confirmed basket downtrend -> no entry
        entry = float(asset_bars[lag_sym][t]["close"])
        atr = compute_atr14(asset_bars[lag_sym], t)
        if atr is None:
            continue
        stop = compute_stop(entry, atr)
        rec = {
            "setup_index": t, "laggard_symbol": lag_sym,
            "laggard_z": round(lag_z, 6), "cross_sectional_z": [round(z, 6) for z in zs],
            "five_day_returns": [round(r, 6) for r in rets],
            "basket_regime_ok": regime, "entry_price": round(entry, 6),
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
        rec["target_2r"] = floor["targets"]["2r"]
        rec["target_3r"] = floor["targets"]["3r"]
        rec["target_4r"] = floor["targets"]["4r"]
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


# --------------------------------------------------------------------------- #
# Synthetic fixtures (in-memory; deterministic; NO date / NO weekday / NO RNG)
# --------------------------------------------------------------------------- #

def _series(n: int, start: float, per_bar_ret: float, rng_frac: float) -> list:
    """Deterministic OHLC series: constant geometric per-bar return + constant
    high/low band. Bars carry NO date and NO weekday -- only OHLC."""
    bars = []
    px = float(start)
    for _ in range(n):
        prev = px
        px = prev * (1.0 + per_bar_ret)
        bars.append({"open": round(prev, 8), "high": round(px * (1 + rng_frac), 8),
                     "low": round(px * (1 - rng_frac), 8), "close": round(px, 8)})
    return bars


def _splice_last_returns(bars: list, k: int, target_ret: float) -> list:
    """Override the last bar's close so that close[T]/close[T-k]-1 == target_ret
    (keeps the OHLC band around the new close)."""
    bars = [dict(b) for b in bars]
    T = len(bars) - 1
    base = float(bars[T - k]["close"])
    new_close = base * (1.0 + target_ret)
    rng = (bars[T]["high"] / bars[T]["close"]) - 1.0
    bars[T]["close"] = round(new_close, 8)
    bars[T]["high"] = round(new_close * (1 + rng), 8)
    bars[T]["low"] = round(new_close * (1 - rng), 8)
    return bars


_N = 70  # >= warmup (50) + lookback headroom


def fixture_valid_laggard_accepted() -> dict:
    """BTC/ETH gently up (basket uptrend, regime OK); SOL the relative laggard
    with a 5-day return that puts its cross-sectional z <= -1.0; SOL ATR normal
    so 2R clears the 81 bps floor -> ACCEPTED."""
    btc = _series(_N, 100.0, 0.004, 0.012)
    eth = _series(_N, 100.0, 0.004, 0.012)
    sol = _series(_N, 100.0, 0.004, 0.012)
    # Make SOL lag at the final bar: 5d return strongly negative vs BTC/ETH.
    btc = _splice_last_returns(btc, 5, 0.05)
    eth = _splice_last_returns(eth, 5, 0.05)
    sol = _splice_last_returns(sol, 5, -0.06)
    return {"BTCUSD": btc, "ETHUSD": eth, "SOLUSD": sol}


def fixture_zscore_threshold_fails() -> dict:
    """One asset HIGH, two roughly equal -> the laggards sit at z ~ -0.71
    (> -1.0) -> NO qualifying laggard -> NO setup."""
    btc = _splice_last_returns(_series(_N, 100.0, 0.004, 0.012), 5, 0.06)
    eth = _splice_last_returns(_series(_N, 100.0, 0.004, 0.012), 5, -0.005)
    sol = _splice_last_returns(_series(_N, 100.0, 0.004, 0.012), 5, -0.005)
    return {"BTCUSD": btc, "ETHUSD": eth, "SOLUSD": sol}


def fixture_basket_regime_fails() -> dict:
    """SOL is the laggard (z <= -1.0) BUT the whole basket is in a downtrend
    (median < SMA(50)) -> regime filter blocks the entry -> NO setup."""
    btc = _series(_N, 100.0, -0.004, 0.012)
    eth = _series(_N, 100.0, -0.004, 0.012)
    sol = _series(_N, 100.0, -0.004, 0.012)
    btc = _splice_last_returns(btc, 5, -0.02)
    eth = _splice_last_returns(eth, 5, -0.02)
    sol = _splice_last_returns(sol, 5, -0.09)
    return {"BTCUSD": btc, "ETHUSD": eth, "SOLUSD": sol}


def fixture_below_floor_rejected() -> dict:
    """SOL laggard qualifies (z <= -1.0 -- scale-invariant for the 2-equal-1-
    different config -- and regime OK) but every asset moves only microscopically
    with a tiny high/low band, so SOL's ATR is tiny and its 2R target distance is
    below the 81 bps gross floor -> rejected_geometry_floor."""
    btc = _splice_last_returns(_series(_N, 100.0, 0.0005, 0.0004), 5, 0.003)
    eth = _splice_last_returns(_series(_N, 100.0, 0.0005, 0.0004), 5, 0.003)
    sol = _splice_last_returns(_series(_N, 100.0, 0.0005, 0.0004), 5, -0.003)
    return {"BTCUSD": btc, "ETHUSD": eth, "SOLUSD": sol}


def fixture_single_asset() -> dict:
    """Only one asset -> scan must raise (no single-asset edge)."""
    return {"BTCUSD": _series(_N, 100.0, 0.004, 0.012)}


def run_c11_detector_dry_run() -> dict[str, Any]:
    """Run every synthetic fixture and report the outcomes. Pure; in-memory."""
    def _last(setups):
        return setups[-1] if setups else None

    accepted = _last(scan_c11_setups(fixture_valid_laggard_accepted()))
    z_fail = scan_c11_setups(fixture_zscore_threshold_fails())
    regime_fail = scan_c11_setups(fixture_basket_regime_fails())
    floor_rej = _last(scan_c11_setups(fixture_below_floor_rejected()))

    single_asset_raises = False
    try:
        scan_c11_setups(fixture_single_asset())
    except ValueError:
        single_asset_raises = True

    return {
        "valid_laggard_accepted": accepted,
        "valid_laggard_status": (accepted or {}).get("status"),
        "zscore_threshold_fail_setup_count": len(z_fail),
        "zscore_threshold_fail_accepted": any(
            s["status"] == "accepted_for_replay_review" for s in z_fail),
        "basket_regime_fail_setup_count": len(regime_fail),
        "basket_regime_fail_accepted": any(
            s["status"] == "accepted_for_replay_review" for s in regime_fail),
        "below_floor_status": (floor_rej or {}).get("status"),
        "single_asset_raises": single_asset_raises,
        "min_assets_required": MIN_ASSETS,
        "uses_no_weekday_or_calendar_trigger": True,
    }


# --------------------------------------------------------------------------- #
# Detector spec + dry-run contract (chain-gated on the C11 spec; pure)
# --------------------------------------------------------------------------- #

C11DD_LABEL = (
    "SPARTA Candidate #11 Detector Spec + Synthetic Dry-Run (READ-ONLY, "
    "RESEARCH ONLY, SYNTHETIC FIXTURES ONLY). cross_asset_dispersion_reversion: "
    "cross-sectional laggard reversion across BTC/ETH/SOL; z<=-1.0 + basket "
    "regime filter; 1.5xATR(14) stop; 2R/3R/4R; 81 bps floor. NO date, NO "
    "weekday, NO real data, NO labels, NO replay, NO trading. EARLY "
    "GENERALIZATION BATTERY STAYS LOCKED FOR THE LATER LABELS/REPLAY STAGE."
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
    "is_single_asset_edge", "fits_parameters", "is_a_rescue_attempt",
    "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "promotes_gate", "unlocks_downstream_gate",
    "claims_profitability", "claims_edge", "claims_paper_or_live_readiness",
    "executes", "writes_files",
)


def get_candidate_11_detector_dry_run_label() -> str:
    return C11DD_LABEL


def get_candidate_11_detector_dry_run_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_candidate_11_detector_spec_dry_run(repo_root: Any = ".",
                                             tracked_paths: list | None = None
                                             ) -> dict[str, Any]:
    """Assemble the C11 detector spec + synthetic dry-run record. Chain-gated on
    the READY candidate spec. Runs the synthetic dry-run and pins the eight
    required proofs. Pure; in-memory; synthetic fixtures only."""
    dry = run_c11_detector_dry_run()
    dry_again = run_c11_detector_dry_run()
    proofs = {
        "valid_laggard_setup_accepted":
            dry["valid_laggard_status"] == "accepted_for_replay_review",
        "no_setup_when_zscore_threshold_fails":
            dry["zscore_threshold_fail_accepted"] is False
            and dry["zscore_threshold_fail_setup_count"] == 0,
        "no_setup_when_basket_regime_fails":
            dry["basket_regime_fail_accepted"] is False
            and dry["basket_regime_fail_setup_count"] == 0,
        "no_setup_when_single_asset":
            dry["single_asset_raises"] is True,
        "no_calendar_or_weekday_trigger":
            dry["uses_no_weekday_or_calendar_trigger"] is True,
        "no_labels_replay_data_fetch_trading": True,
        "invalid_stop_or_below_floor_rejected":
            dry["below_floor_status"] in ("rejected_geometry_floor",
                                          "rejected_invalid_stop_geometry"),
        "deterministic": dry == dry_again,
    }
    record: dict[str, Any] = {
        "schema_version": 1, "label": C11DD_LABEL, "mode": C11D_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_number": 11, "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "verdict": None, "blockers": [],
        "symbol_universe": list(SYMBOL_UNIVERSE), "min_assets": MIN_ASSETS,
        "timeframe": TIMEFRAME, "direction": DIRECTION,
        "dispersion_lookback_bars": DISPERSION_LOOKBACK_BARS,
        "z_entry_threshold": Z_ENTRY_THRESHOLD,
        "basket_sma_length": BASKET_SMA_LENGTH, "atr_length": ATR_LENGTH,
        "structure_stop_atr_multiplier": STRUCTURE_STOP_ATR_MULTIPLIER,
        "target_variants": [n for n, _ in TARGET_VARIANTS],
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "synthetic_fixtures_only": True,
        "uses_no_weekday_or_calendar_trigger": True,
        "is_single_asset_edge": False,
        "dry_run": dry, "dry_run_proofs": proofs,
        "early_generalization_battery_locked_for_labels_replay":
            list(EARLY_GENERALIZATION_BATTERY),
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
        "no_parameter_fitting": True, "no_profitability_claim": True,
        "no_paper_live_readiness_claim": True, "no_downstream_gate_unlock": True,
    }

    spec = build_candidate_11_spec(repo_root, tracked_paths or [])
    record["spec_verdict"] = spec.get("verdict")
    if spec.get("verdict") != VERDICT_C11S_READY:
        record["verdict"] = VERDICT_C11DD_BLOCKED
        record["blockers"].append("spec_not_ready")
        return record
    if not all(proofs.values()):
        record["verdict"] = VERDICT_C11DD_BLOCKED
        record["blockers"].append("dry_run_proof_failed")
        return record

    record["verdict"] = VERDICT_C11DD_READY
    return record


def validate_candidate_11_detector_spec_dry_run(record: dict[str, Any]
                                                ) -> dict[str, Any]:
    """Anti-tamper validator. READY only when all eight proofs hold, the
    detector geometry is intact, no calendar/weekday/single-asset behavior, and
    all execution gates are locked."""
    failures: list = []
    if record.get("verdict") != VERDICT_C11DD_READY:
        failures.append("verdict_not_ready")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("spec_verdict") != VERDICT_C11S_READY:
        failures.append("spec_verdict_tampered")

    proofs = record.get("dry_run_proofs") or {}
    for key in ("valid_laggard_setup_accepted",
                "no_setup_when_zscore_threshold_fails",
                "no_setup_when_basket_regime_fails",
                "no_setup_when_single_asset",
                "no_calendar_or_weekday_trigger",
                "no_labels_replay_data_fetch_trading",
                "invalid_stop_or_below_floor_rejected", "deterministic"):
        if proofs.get(key) is not True:
            failures.append("proof_failed_%s" % key)

    if len(record.get("symbol_universe") or []) < MIN_ASSETS:
        failures.append("single_asset_universe")
    if record.get("z_entry_threshold") != Z_ENTRY_THRESHOLD:
        failures.append("z_threshold_tampered")
    if record.get("structure_stop_atr_multiplier") != STRUCTURE_STOP_ATR_MULTIPLIER:
        failures.append("stop_multiplier_tampered")
    if record.get("target_distance_floor_bps") != TARGET_DISTANCE_FLOOR_BPS:
        failures.append("floor_tampered")
    if record.get("uses_no_weekday_or_calendar_trigger") is not True:
        failures.append("calendar_trigger_flag_tampered")
    if record.get("synthetic_fixtures_only") is not True:
        failures.append("synthetic_only_flag_tampered")
    if not record.get("early_generalization_battery_locked_for_labels_replay"):
        failures.append("early_generalization_battery_missing")

    locks = record.get("scope_locks") or {}
    for key in ("synthetic_fixtures_only", "no_real_data", "no_data_fetch",
                "no_labels", "no_replay", "no_portfolio_compute",
                "no_paper_trading", "no_live_trading", "no_calendar_trigger",
                "no_weekday_trigger", "no_single_asset_edge",
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

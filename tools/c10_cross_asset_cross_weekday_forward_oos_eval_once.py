"""C10 cross-asset / cross-weekday / forward-OOS generalization evaluation
one-off runner (READ-ONLY against FROZEN, SHA-pinned BTC/ETH/SOL 1d sources;
RESEARCH ONLY; NO TRADING; NO NETWORK; NO PnL/PROFITABILITY CLAIM; NO RELABEL OF
THE ORIGINAL C10 RESULT; NO WEEKDAY RE-SELECTION; NO PARAMETER FITTING; NO
OPTIMIZATION; NO DOWNSTREAM GATE UNLOCK).

Tests whether the C10 BTCUSD-Friday-drift result GENERALIZES, using ONLY frozen
data already on disk and the SAME pre-registered C10 geometry. It reuses the
committed detector geometry primitives (_precompute_atr, compute_stop,
geometry_floor_by_variant, apply_anti_cluster_filter) in a generalized scan so
the geometry is identical to C10 -- only the (asset, weekday, window) inputs
change. The committed scan_c10_setups is BTCUSD-locked; this runner does NOT
modify it and does NOT call select_favorable_weekday_bucket (the in-sample
optimizer), so the favorable weekday is never re-fit.

Anti-lookahead / anti-optimization guarantees:
  * The Friday (weekday 5) rule and the 1.5*ATR(14) stop / 5-bar horizon /
    2R-3R-4R targets / 81 bps floor / 27+10 bps cost basis are INHERITED from
    the frozen C10 spec, never re-derived or fitted.
  * Cross-asset (ETH/SOL) and forward-OOS apply the inherited Friday rule as-is.
  * Cross-weekday reports ALL seven weekdays for BTC; NO best weekday is picked
    or promoted -- every cell is reported.
  * Self-validation: the generalized scan must reproduce the frozen 156
    BTCUSD-Friday accepted setups over OOS 2023-2025; aborts otherwise.
  * The original frozen C10 labels/replay/robustness artifacts are NOT mutated
    or relabeled; this is a NEW, separate generalization artifact.

Hard locks (declarative): no_paper_trading, no_micro_live, no_live_trading,
no_broker, no_exchange, no_wallet, no_account, no_credentials, no_order_logic,
no_portfolio_allocation, no_api, no_network, no_fetch, no_notification,
no_scheduler, no_relabel, no_weekday_reselection, no_parameter_fitting,
no_optimization, no_best_cell_selected_as_promotion, no_detector_change,
no_profitability_claim, no_downstream_gate_unlock, no_staging, no_commit,
no_push.

Intentionally untracked; writes only into the gitignored generalization dir.
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.intraweek_calendar_seasonality_drift_v1_detector_spec_dry_run_contract as _det  # noqa: E402,E501

CANDIDATE_ID = "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1"
CANDIDATE_FAMILY = "intraweek_calendar_seasonality_drift"
DIRECTION = "long_only"
TIMEFRAME = "1d"
INHERITED_FRIDAY_BUCKET = 5            # weekday 5 = Friday, inherited (not re-fit)
ALL_WEEKDAYS = (1, 2, 3, 4, 5, 6, 7)
ALL_IN_BPS = 37.0                       # 27 fee + 10 slippage, inherited
VARIANTS = (("2r", 2.0), ("3r", 3.0), ("4r", 4.0))
OOS_WINDOW = ("2023-01-01", "2025-12-31")
FORWARD_WINDOW = ("2026-01-01", "2026-06-08")
HEAD_AT_ROBUSTNESS_REVIEW = "85e2cd6a4b49ec6e07f74ee920caab23516a14ca"
EXPECTED_BTC_FRIDAY_OOS_ACCEPTED = 156  # self-validation anchor

RAW_DIR = REPO_ROOT / "data" / "crypto_d1_spot" / "raw"
SOURCES = {
    "BTC": RAW_DIR / "BTC_1d.csv",
    "ETH": RAW_DIR / "ETH_1d.csv",
    "SOL": RAW_DIR / "SOL_1d.csv",
}
EXPECTED_SHAS = {
    "BTC": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETH": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOL": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

OUT_DIR = (REPO_ROOT / "data" / "intraweek_calendar_seasonality_c10"
           / "cross_asset_weekday_forward_oos")
OUT_PATH = OUT_DIR / "c10_cross_asset_weekday_forward_oos_2023_2026H1.json"


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_bars(path):
    bars = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            d = row["date"]
            bars.append({
                "date": d,
                "iso_weekday": datetime.date.fromisoformat(d).isoweekday(),
                "open": float(row["open"]), "high": float(row["high"]),
                "low": float(row["low"]), "close": float(row["close"]),
            })
    bars.sort(key=lambda b: b["date"])
    return bars


def _in_window(date, window):
    return window[0] <= date <= window[1]


def generalized_scan(bars, bucket, symbol, window):
    """Replicates scan_c10_setups using the committed geometry primitives,
    WITHOUT the BTCUSD context lock. Returns accepted-post-anti-cluster setups.
    Same acceptance criteria: calendar trigger, valid stop, >=1 variant clears
    the 81 bps floor, horizon exit bar exists."""
    atr_values = _det._precompute_atr(bars)
    n = len(bars)
    accepted = []
    last_emitted = -1
    for t in range(n):
        bar = bars[t]
        if not _in_window(bar["date"], window):
            continue
        if int(bar["iso_weekday"]) != bucket:
            continue
        if t <= last_emitted:
            continue
        atr = atr_values[t]
        if atr is None:
            continue
        last_emitted = t
        exit_index = t + _det.HOLDING_HORIZON_BARS
        if exit_index >= n:
            continue                      # rejected_no_evaluation_bar
        entry = float(bar["close"])
        stop = _det.compute_stop(entry, atr)
        if not stop["valid"]:
            continue                      # rejected_invalid_stop_geometry
        floor = _det.geometry_floor_by_variant(entry, stop["stop_distance"])
        if not floor["any_variant_passes"]:
            continue                      # rejected_geometry_floor
        accepted.append({
            "setup_id": "%s_%s" % (symbol, bar["date"]),
            "symbol": symbol, "entry_index": t, "entry_date": bar["date"],
            "entry_year": bar["date"][:4], "entry_price": entry,
            "stop_price": stop["stop_price"],
            "stop_distance": stop["stop_distance"],
            "exit_index": exit_index,
            "target_2r": floor["targets"]["2r"],
            "target_3r": floor["targets"]["3r"],
            "target_4r": floor["targets"]["4r"],
        })
    cluster = _det.apply_anti_cluster_filter(
        [dict(a, status="accepted_for_replay_review") for a in accepted])
    kept_idx = {s["entry_index"] for s in cluster["kept"]}
    return [a for a in accepted if a["entry_index"] in kept_idx]


def _walk_net(bars, setup, variant_r):
    entry = setup["entry_price"]
    stop = setup["stop_price"]
    dist = setup["stop_distance"]
    dist_bps = (dist / entry) * 10000.0
    target = entry + variant_r * dist
    ei, xi = setup["entry_index"], setup["exit_index"]
    for i in range(ei + 1, xi + 1):
        if bars[i]["low"] <= stop:
            gross = -1.0
            break
        if bars[i]["high"] >= target:
            gross = float(variant_r)
            break
    else:
        gross = (bars[xi]["close"] - entry) / dist
    return gross - ALL_IN_BPS / dist_bps


def aggregate(bars, setups, variant_r):
    nets = [_walk_net(bars, s, variant_r) for s in setups]
    by_year = {}
    for s, nr in zip(setups, nets):
        by_year[s["entry_year"]] = by_year.get(s["entry_year"], 0.0) + nr
    n = len(nets)
    total = sum(nets)
    wins = sum(1 for x in nets if x > 0)
    return {
        "trade_count": n,
        "net_r_total": round(total, 4),
        "net_r_mean": round(total / n, 4) if n else None,
        "win_rate": round(wins / n, 4) if n else None,
        "net_positive": total > 0,
        "per_year_net_r": {k: round(v, 4) for k, v in sorted(by_year.items())},
    }


def block(bars, bucket, symbol, window):
    setups = generalized_scan(bars, bucket, symbol, window)
    return {
        "accepted_count": len(setups),
        "by_variant": {name: aggregate(bars, setups, mult)
                       for name, mult in VARIANTS},
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sha_before = {k: compute_sha256(p) for k, p in SOURCES.items()}
    for k, expected in EXPECTED_SHAS.items():
        if sha_before[k] != expected:
            raise RuntimeError("source_sha_pin_mismatch_%s" % k)

    bars = {k: load_bars(p) for k, p in SOURCES.items()}

    # SELF-VALIDATION: generalized scan must reproduce the frozen 156 BTC-Friday
    # accepted setups over OOS -> proves geometry identical to the committed
    # detector before any generalization claim.
    btc_fri_oos = generalized_scan(bars["BTC"], INHERITED_FRIDAY_BUCKET,
                                   "BTCUSD", OOS_WINDOW)
    if len(btc_fri_oos) != EXPECTED_BTC_FRIDAY_OOS_ACCEPTED:
        raise RuntimeError(
            "self_validation_failed_btc_friday_oos_%d" % len(btc_fri_oos))

    # 1. Cross-asset: inherited Friday on ETH / SOL, OOS 2023-2025.
    cross_asset = {
        "ETH": block(bars["ETH"], INHERITED_FRIDAY_BUCKET, "ETHUSD", OOS_WINDOW),
        "SOL": block(bars["SOL"], INHERITED_FRIDAY_BUCKET, "SOLUSD", OOS_WINDOW),
        "BTC_reference": block(bars["BTC"], INHERITED_FRIDAY_BUCKET, "BTCUSD",
                               OOS_WINDOW),
    }
    # 2. Cross-weekday: ALL seven weekdays on BTC, OOS (no best pick).
    cross_weekday = {
        "wd%d" % wd: block(bars["BTC"], wd, "BTCUSD", OOS_WINDOW)
        for wd in ALL_WEEKDAYS
    }
    # 3. Forward-OOS: inherited Friday on BTC / ETH / SOL, 2026-01-01..06-08.
    forward_oos = {
        "BTC": block(bars["BTC"], INHERITED_FRIDAY_BUCKET, "BTCUSD",
                     FORWARD_WINDOW),
        "ETH": block(bars["ETH"], INHERITED_FRIDAY_BUCKET, "ETHUSD",
                     FORWARD_WINDOW),
        "SOL": block(bars["SOL"], INHERITED_FRIDAY_BUCKET, "SOLUSD",
                     FORWARD_WINDOW),
    }

    sha_after = {k: compute_sha256(p) for k, p in SOURCES.items()}
    if sha_after != sha_before:
        raise RuntimeError("sources_mutated_during_generalization")

    # Derived generalization flags (NO best-cell selection).
    def _all_variants_positive(blk):
        return all(blk["by_variant"][n]["net_positive"] for n, _ in VARIANTS)

    friday_net_3r = {wd: cross_weekday["wd%d" % wd]["by_variant"]["3r"]["net_r_total"]
                     for wd in ALL_WEEKDAYS}
    friday_rank_3r = (sorted(ALL_WEEKDAYS, key=lambda wd: friday_net_3r[wd],
                             reverse=True).index(INHERITED_FRIDAY_BUCKET) + 1)
    positive_weekdays_3r = sum(1 for wd in ALL_WEEKDAYS if friday_net_3r[wd] > 0)

    flags = {
        "self_validation_btc_friday_oos_156": True,
        "cross_asset_eth_friday_all_variants_positive":
            _all_variants_positive(cross_asset["ETH"]),
        "cross_asset_sol_friday_all_variants_positive":
            _all_variants_positive(cross_asset["SOL"]),
        "forward_oos_btc_friday_all_variants_positive":
            _all_variants_positive(forward_oos["BTC"]),
        "forward_oos_eth_friday_all_variants_positive":
            _all_variants_positive(forward_oos["ETH"]),
        "forward_oos_sol_friday_all_variants_positive":
            _all_variants_positive(forward_oos["SOL"]),
        "friday_rank_among_weekdays_3r": friday_rank_3r,
        "positive_weekdays_count_3r": positive_weekdays_3r,
        "friday_is_unique_positive_weekday_3r": positive_weekdays_3r == 1,
    }

    scope_locks = {
        "no_paper_trading": True, "no_micro_live": True,
        "no_live_trading": True, "no_broker": True, "no_exchange": True,
        "no_wallet": True, "no_account": True, "no_credentials": True,
        "no_order_logic": True, "no_portfolio_allocation": True,
        "no_api": True, "no_network": True, "no_fetch": True,
        "no_notification": True, "no_scheduler": True, "no_relabel": True,
        "no_weekday_reselection": True, "no_parameter_fitting": True,
        "no_optimization": True, "no_best_cell_selected_as_promotion": True,
        "no_detector_change": True, "no_profitability_claim": True,
        "no_downstream_gate_unlock": True, "no_staging": True,
        "no_commit": True, "no_push": True,
    }
    payload = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "direction": DIRECTION, "timeframe": TIMEFRAME,
        "head_at_robustness_review": HEAD_AT_ROBUSTNESS_REVIEW,
        "inherited_friday_bucket": INHERITED_FRIDAY_BUCKET,
        "all_in_bps": ALL_IN_BPS,
        "oos_window": list(OOS_WINDOW), "forward_window": list(FORWARD_WINDOW),
        "source_sha256": sha_before,
        "sources_unchanged_during_evaluation": sha_after == sha_before,
        "self_validation_btc_friday_oos_accepted": len(btc_fri_oos),
        "cross_asset": cross_asset,
        "cross_weekday": cross_weekday,
        "forward_oos": forward_oos,
        "generalization_flags": flags,
        "honest_framing": (
            "generalization re-walk over FROZEN data with the INHERITED Friday "
            "rule + frozen geometry; no weekday re-selection; no parameter "
            "fitting; no best-cell selection; not a profitability claim; the "
            "original frozen C10 result is unchanged and not relabeled"),
        "scope_locks": scope_locks,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    out_sha = compute_sha256(OUT_PATH)
    if {k: compute_sha256(p) for k, p in SOURCES.items()} != sha_before:
        raise RuntimeError("sources_mutated_after_write")

    report = {
        "out_path": str(OUT_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "out_sha256": out_sha,
        "source_sha256": sha_before,
        "self_validation_btc_friday_oos_accepted": len(btc_fri_oos),
        "cross_asset": cross_asset,
        "cross_weekday_net_3r": friday_net_3r,
        "forward_oos": forward_oos,
        "generalization_flags": flags,
    }
    for key, value in report.items():
        print("%s = %r" % (key, value))
    return report


if __name__ == "__main__":
    main()

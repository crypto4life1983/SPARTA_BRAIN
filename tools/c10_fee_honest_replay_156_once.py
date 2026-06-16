"""C10 fee+slippage-honest replay-evaluation one-off runner (READ-ONLY against
the pushed detector-labels artifact and the frozen BTCUSD 1d source;
RESEARCH ONLY; NO TRADING; NO NETWORK; NO PnL/PROFITABILITY CLAIM; NO RELABEL;
NO EDIT-TOKEN USE; NO DOWNSTREAM GATE UNLOCK).

Walks the 156 accepted-post-anti-cluster setups frozen in
data/intraweek_calendar_seasonality_c10/detector_labels/
c10_detector_labels_2023-01-01_2025-12-31.json against the SAME frozen,
SHA-pinned BTCUSD 1d candles the detection runner read
(data/crypto_d1_spot/raw/BTC_1d.csv). The C10 geometry is a fixed-horizon
trade: long at the trigger-bar close, a 1.5*ATR(14) structure stop, target
variants 2R/3R/4R, and a 5-completed-daily-bar horizon exit.

For every approved R-multiple variant (2R / 3R / 4R) the runner:
  1. SHA-pins the source CSV and the labels + summary artifacts BEFORE reading
     anything; aborts on drift; re-verifies after writing.
  2. For each accepted setup, walks the holding window bars[entry_index+1 ..
     exit_index] (the 5 completed daily bars after entry):
       - MISS:     low  <= stop_price          -> gross_r = -1
       - HIT:      high >= target_price         -> gross_r = +variant_r
       - STRADDLE: both in the same bar         -> STOP FIRST (conservative
                                                   honest convention) -> -1
       - HORIZON:  neither by exit_index        -> exit at exit_index close:
                                                   gross_r = (exit_close -
                                                   entry) / stop_distance
     The HORIZON exit is the DESIGNED exit (not a timeout), so every outcome is
     decisive; all 156 setups carry a full 5-bar horizon inside the OOS window.
  3. Applies a replay-time same-symbol non-overlap policy as REDUCE-OR-KEEP-
     ONLY (drop any later setup whose entry is at/before the active exit;
     Friday spacing 7d > 5-bar hold, so 0 drops are expected -- recorded for
     evidence). Never add.
  4. Applies REALISTIC COSTS as R-units of each setup's stop distance:
       fee_r      = FEE_ROUND_TRIP_BPS      / stop_distance_bps   (27 bps, locked)
       slippage_r = SLIPPAGE_ROUND_TRIP_BPS / stop_distance_bps   (10 bps, declared
                    conservative 5 bps/side constant haircut on BTC daily spot)
       net_r_fee_only = gross_r - fee_r
       net_r_all_in   = gross_r - fee_r - slippage_r
     Preserves the 81 bps gross-target-distance floor (already filtered at
     label time -- recorded for evidence).
  5. Aggregates per variant: counts, trade count, win rate (net_r_all_in > 0),
     hit rate, gross/net average R and total R, max drawdown of the all-in net
     R equity curve, and a per-entry-year breakdown (2023/2024/2025).
  6. Emits two untracked JSON artifacts under
     data/intraweek_calendar_seasonality_c10/replay_results/ with the full
     per-setup-per-variant ledger plus aggregates, and re-verifies every SHA.

Hard locks (declarative): no_paper_trading, no_micro_live, no_live_trading,
no_broker, no_exchange, no_wallet, no_account, no_credentials, no_order_logic,
no_portfolio_allocation, no_api, no_network, no_fetch, no_notification,
no_scheduler, no_relabel, no_detector_change, no_edit_token_use,
no_profitability_claim, no_downstream_gate_unlock, no_staging, no_commit,
no_push.

This module is intentionally untracked at author time and writes only into the
C10 replay-results operational data directory (gitignored). It is invoked
manually under an explicit human-approved replay-evaluation gate.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

CANDIDATE_ID = "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1"
CANDIDATE_FAMILY = "intraweek_calendar_seasonality_drift"
SYMBOL = "BTCUSD"
TIMEFRAME = "1d"
DIRECTION = "long_only"
SAMPLE_TAG = "2023-01-01_2025-12-31"

HOLDING_HORIZON_BARS = 5
FEE_ROUND_TRIP_BPS = 27.0          # locked at spec
SLIPPAGE_ROUND_TRIP_BPS = 10.0     # declared conservative 5 bps/side haircut
TARGET_DISTANCE_FLOOR_BPS = 81.0
VARIANTS = (("2r", 2.0), ("3r", 3.0), ("4r", 4.0))
SAME_BAR_STRADDLE_POLICY = "stop_first_conservative_miss"
NON_OVERLAP_POLICY = "reduce_or_keep_only_never_add"
HEAD_AT_LABELS_REVIEW = "0de0f7c1089a9650204a786a983502b34b0417be"

SOURCE_FILE = REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / "BTC_1d.csv"
EXPECTED_SOURCE_SHA = (
    "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88")
LABELS_INPUT = (REPO_ROOT / "data" / "intraweek_calendar_seasonality_c10"
                / "detector_labels"
                / "c10_detector_labels_2023-01-01_2025-12-31.json")
SUMMARY_INPUT = (REPO_ROOT / "data" / "intraweek_calendar_seasonality_c10"
                 / "detector_labels"
                 / "c10_detector_summary_2023-01-01_2025-12-31.json")
EXPECTED_LABELS_SHA = (
    "8276e9a6ee9bd9b89ff28a41f5c160973934bcc03ad8c5371095e62fb8f9c47d")
EXPECTED_SUMMARY_SHA = (
    "d23d0c34363d4e0cde3413d40266046c8fc4dbcd16a084afbefccfa933a2c8ee")

OUT_DIR = (REPO_ROOT / "data" / "intraweek_calendar_seasonality_c10"
           / "replay_results")
REPLAY_LEDGER_PATH = OUT_DIR / ("c10_replay_ledger_%s.json" % SAMPLE_TAG)
REPLAY_SUMMARY_PATH = OUT_DIR / ("c10_replay_summary_%s.json" % SAMPLE_TAG)


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_bars_from_csv(path):
    """Date-sorted OHLC bars; list index == absolute row index used by the
    labels' entry_index / exit_index."""
    bars = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bars.append({
                "date": row["date"],
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
            })
    bars.sort(key=lambda b: b["date"])
    return bars


def evaluate_one_variant(bars, setup, variant_r):
    """Walk one accepted setup for one R-multiple variant over its fixed
    5-bar horizon. Pure; structural fields only."""
    entry = float(setup["entry_price"])
    stop_price = float(setup["stop_price"])
    stop_distance = float(setup["stop_distance"])
    stop_distance_bps = (stop_distance / entry) * 10000.0
    target_price = entry + variant_r * stop_distance
    target_distance_bps = (variant_r * stop_distance / entry) * 10000.0
    entry_index = int(setup["entry_index"])
    exit_index = int(setup["exit_index"])
    entry_date = setup["entry_date"]
    fee_r = FEE_ROUND_TRIP_BPS / stop_distance_bps
    slippage_r = SLIPPAGE_ROUND_TRIP_BPS / stop_distance_bps
    out = {
        "setup_id": setup["setup_id"],
        "entry_index": entry_index,
        "entry_date": entry_date,
        "entry_year": entry_date[:4],
        "exit_index": exit_index,
        "variant": "%dr" % int(variant_r),
        "variant_r_multiple": variant_r,
        "entry_price": entry,
        "stop_price": stop_price,
        "stop_distance": stop_distance,
        "stop_distance_bps": stop_distance_bps,
        "target_price": target_price,
        "target_distance_bps": target_distance_bps,
        "target_distance_floor_bps_pass":
            target_distance_bps >= TARGET_DISTANCE_FLOOR_BPS,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "fee_round_trip_r": fee_r,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "slippage_round_trip_r": slippage_r,
        "same_bar_straddle_policy": SAME_BAR_STRADDLE_POLICY,
        "outcome": None,
        "exit_resolved_index": None,
        "exit_date": None,
        "exit_price": None,
        "bars_held": None,
        "gross_r": None,
        "net_r_fee_only": None,
        "net_r_all_in": None,
    }
    # Integrity: the labels' absolute index must line up with the frozen bars.
    if entry_index >= len(bars) or bars[entry_index]["date"] != entry_date:
        out["outcome"] = "index_date_mismatch_abort"
        return out
    if exit_index >= len(bars):
        out["outcome"] = "horizon_bar_beyond_source"
        return out

    def _finish(outcome, idx, price, gross_r):
        out["outcome"] = outcome
        out["exit_resolved_index"] = idx
        out["exit_date"] = bars[idx]["date"]
        out["exit_price"] = price
        out["bars_held"] = idx - entry_index
        out["gross_r"] = gross_r
        out["net_r_fee_only"] = gross_r - fee_r
        out["net_r_all_in"] = gross_r - fee_r - slippage_r
        return out

    for i in range(entry_index + 1, exit_index + 1):
        bar = bars[i]
        hit_stop = float(bar["low"]) <= stop_price
        hit_target = float(bar["high"]) >= target_price
        if hit_stop and hit_target:
            return _finish("miss_same_bar_straddle", i, stop_price, -1.0)
        if hit_stop:
            return _finish("miss", i, stop_price, -1.0)
        if hit_target:
            return _finish("hit", i, target_price, float(variant_r))
    # Designed horizon exit at exit_index close.
    exit_close = float(bars[exit_index]["close"])
    gross_r = (exit_close - entry) / stop_distance
    return _finish("horizon", exit_index, exit_close, gross_r)


def apply_non_overlap_per_variant(setups_sorted, bars, variant_r):
    """REDUCE-OR-KEEP-ONLY: drop any later setup whose entry_index is <= the
    active setup's resolved exit index. Never add."""
    kept = []
    dropped_overlap = []
    active_exit_index = None
    for setup in setups_sorted:
        entry_index = int(setup["entry_index"])
        if active_exit_index is not None and entry_index <= active_exit_index:
            dropped_overlap.append({
                "setup_id": setup["setup_id"],
                "entry_index": entry_index,
                "entry_date": setup["entry_date"],
                "variant": "%dr" % int(variant_r),
                "outcome": "dropped_replay_time_non_overlap",
                "blocked_by_active_exit_index": active_exit_index,
            })
            continue
        outcome = evaluate_one_variant(bars, setup, variant_r)
        kept.append(outcome)
        if outcome["exit_resolved_index"] is not None:
            active_exit_index = outcome["exit_resolved_index"]
    return {"kept": kept, "dropped_overlap": dropped_overlap}


def aggregate_variant(kept):
    """Counts + win/hit rates + R sums/means + max drawdown + per-year. Pure.
    All-in net R (fee + slippage) is the headline cost basis."""
    counts = {"hit": 0, "miss": 0, "miss_same_bar_straddle": 0,
              "horizon": 0, "index_date_mismatch_abort": 0,
              "horizon_bar_beyond_source": 0}
    n = 0
    wins = 0
    hits = 0
    gross_sum = 0.0
    net_fee_sum = 0.0
    net_all_in_sum = 0.0
    per_year: dict = {}
    # equity curve in chronological (entry_index) order for drawdown.
    ordered = sorted((o for o in kept if o.get("net_r_all_in") is not None),
                     key=lambda o: o["entry_index"])
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for o in ordered:
        oc = o["outcome"]
        counts[oc] = counts.get(oc, 0) + 1
        n += 1
        gross_sum += o["gross_r"]
        net_fee_sum += o["net_r_fee_only"]
        net_all_in_sum += o["net_r_all_in"]
        if o["net_r_all_in"] > 0:
            wins += 1
        if oc == "hit":
            hits += 1
        equity += o["net_r_all_in"]
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
        yr = o["entry_year"]
        y = per_year.setdefault(yr, {"trades": 0, "wins": 0,
                                     "gross_r_sum": 0.0,
                                     "net_all_in_r_sum": 0.0})
        y["trades"] += 1
        y["wins"] += 1 if o["net_r_all_in"] > 0 else 0
        y["gross_r_sum"] += o["gross_r"]
        y["net_all_in_r_sum"] += o["net_r_all_in"]
    return {
        "counts": counts,
        "trade_count": n,
        "win_count_net_all_in": wins,
        "win_rate_net_all_in": (wins / n if n else None),
        "hit_count": hits,
        "hit_rate": (hits / n if n else None),
        "gross_r_total": gross_sum,
        "net_r_total_fee_only": net_fee_sum,
        "net_r_total_all_in": net_all_in_sum,
        "gross_r_mean": (gross_sum / n if n else None),
        "net_r_mean_fee_only": (net_fee_sum / n if n else None),
        "net_r_mean_all_in": (net_all_in_sum / n if n else None),
        "max_drawdown_r_all_in": max_dd,
        "net_all_in_positive_after_costs": net_all_in_sum > 0,
        "per_year": per_year,
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source_sha_before = compute_sha256(SOURCE_FILE)
    labels_sha_before = compute_sha256(LABELS_INPUT)
    summary_sha_before = compute_sha256(SUMMARY_INPUT)
    if source_sha_before != EXPECTED_SOURCE_SHA:
        raise RuntimeError("source_sha_pin_does_not_match_before_replay")
    if labels_sha_before != EXPECTED_LABELS_SHA:
        raise RuntimeError("labels_sha_pin_does_not_match_before_replay")
    if summary_sha_before != EXPECTED_SUMMARY_SHA:
        raise RuntimeError("summary_sha_pin_does_not_match_before_replay")

    bars = load_bars_from_csv(SOURCE_FILE)
    if not bars:
        raise RuntimeError("no_source_bars")
    with open(LABELS_INPUT, encoding="utf-8") as f:
        labels_payload = json.load(f)
    accepted_setups = labels_payload.get(
        "accepted_setups_post_anti_cluster") or []
    if not accepted_setups:
        raise RuntimeError("no_accepted_setups_in_labels")
    accepted_count = len(accepted_setups)
    setups_sorted = sorted(accepted_setups,
                           key=lambda s: int(s["entry_index"]))

    per_variant = {}
    variant_aggregates = {}
    for name, multiple in VARIANTS:
        result = apply_non_overlap_per_variant(setups_sorted, bars, multiple)
        kept = result["kept"]
        dropped = result["dropped_overlap"]
        agg = aggregate_variant(kept)
        per_variant[name] = {
            "variant_r_multiple": multiple,
            "kept_count": len(kept),
            "dropped_overlap_count": len(dropped),
            "kept": kept,
            "dropped_overlap": dropped,
        }
        variant_aggregates[name] = {
            "variant_r_multiple": multiple,
            "kept_count": len(kept),
            "dropped_overlap_count": len(dropped),
            **agg,
        }

    source_sha_mid = compute_sha256(SOURCE_FILE)
    labels_sha_mid = compute_sha256(LABELS_INPUT)
    summary_sha_mid = compute_sha256(SUMMARY_INPUT)
    inputs_unchanged = (source_sha_mid == source_sha_before
                        and labels_sha_mid == labels_sha_before
                        and summary_sha_mid == summary_sha_before)
    if not inputs_unchanged:
        raise RuntimeError("inputs_mutated_during_replay_evaluation")

    scope_locks = {
        "no_paper_trading": True, "no_micro_live": True,
        "no_live_trading": True, "no_broker": True, "no_exchange": True,
        "no_wallet": True, "no_account": True, "no_credentials": True,
        "no_order_logic": True, "no_portfolio_allocation": True,
        "no_api": True, "no_network": True, "no_fetch": True,
        "no_notification": True, "no_scheduler": True, "no_relabel": True,
        "no_detector_change": True, "no_edit_token_use": True,
        "no_profitability_claim": True, "no_downstream_gate_unlock": True,
        "no_staging": True, "no_commit": True, "no_push": True,
    }
    common = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbol": SYMBOL, "timeframe": TIMEFRAME, "direction": DIRECTION,
        "sample_tag": SAMPLE_TAG,
        "out_of_sample_window": labels_payload.get("out_of_sample_window"),
        "in_sample_selection_window":
            labels_payload.get("in_sample_selection_window"),
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "labels_input_path":
            str(LABELS_INPUT.relative_to(REPO_ROOT)).replace("\\", "/"),
        "labels_input_sha256_before": labels_sha_before,
        "labels_input_sha256_after": labels_sha_mid,
        "summary_input_sha256_before": summary_sha_before,
        "summary_input_sha256_after": summary_sha_mid,
        "source_path":
            str(SOURCE_FILE.relative_to(REPO_ROOT)).replace("\\", "/"),
        "source_sha256_before": source_sha_before,
        "source_sha256_after": source_sha_mid,
        "inputs_unchanged_during_evaluation": inputs_unchanged,
        "accepted_post_anti_cluster_input_count": accepted_count,
        "holding_horizon_bars": HOLDING_HORIZON_BARS,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS,
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "variants": [name for name, _ in VARIANTS],
        "same_bar_straddle_policy": SAME_BAR_STRADDLE_POLICY,
        "non_overlap_policy": NON_OVERLAP_POLICY,
        "scope_locks": scope_locks,
        "honest_framing": (
            "structural out-of-sample replay only; fee+slippage honest; no "
            "live profitability claim; no edge asserted; no relabel; no "
            "edit-token used; no downstream gate unlocked"),
    }
    ledger_payload = dict(common)
    ledger_payload["artifact"] = "c10_replay_ledger"
    ledger_payload["per_variant"] = per_variant
    summary_payload = dict(common)
    summary_payload["artifact"] = "c10_replay_summary"
    summary_payload["variant_aggregates"] = variant_aggregates

    with open(REPLAY_LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger_payload, f, indent=2, sort_keys=True)
    ledger_sha = compute_sha256(REPLAY_LEDGER_PATH)
    summary_payload["ledger_sha256"] = ledger_sha
    summary_payload["ledger_path"] = str(
        REPLAY_LEDGER_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    with open(REPLAY_SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2, sort_keys=True)
    summary_sha = compute_sha256(REPLAY_SUMMARY_PATH)

    source_sha_after = compute_sha256(SOURCE_FILE)
    labels_sha_after = compute_sha256(LABELS_INPUT)
    summary_after_sha = compute_sha256(SUMMARY_INPUT)
    if not (source_sha_after == source_sha_before
            and labels_sha_after == labels_sha_before
            and summary_after_sha == summary_sha_before):
        raise RuntimeError("inputs_mutated_after_replay_artifact_write")

    report = {
        "ledger_path": str(REPLAY_LEDGER_PATH.relative_to(REPO_ROOT)).replace(
            "\\", "/"),
        "ledger_sha256": ledger_sha,
        "summary_path": str(REPLAY_SUMMARY_PATH.relative_to(REPO_ROOT)).replace(
            "\\", "/"),
        "summary_sha256": summary_sha,
        "accepted_post_anti_cluster_input_count": accepted_count,
        "source_sha256_stable": source_sha_before == source_sha_after,
        "labels_sha256_stable": labels_sha_before == labels_sha_after,
        "variant_aggregates": variant_aggregates,
    }
    for key, value in report.items():
        print("%s = %r" % (key, value))
    return report


if __name__ == "__main__":
    main()

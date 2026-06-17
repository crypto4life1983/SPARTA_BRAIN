"""C11 cross-asset dispersion reversion fee+slippage-honest replay one-off runner
(READ-ONLY against the FROZEN, SHA-pinned C11 detector-labels artifact and the
frozen BTC/ETH/SOL 1d sources; RESEARCH ONLY; NO data fetch; NO relabel; NO
detector change; NO PnL/profitability claim; NO robustness; NO portfolio compute;
NO trading / broker / credentials / orders; NO parameter fitting; NO best-asset
selection; NO paper/live readiness claim; NO downstream gate unlock).

Walks the accepted real-candle dispersion-reversion labels frozen in
data/cross_asset_dispersion_reversion_c11/detector_labels/c11_detector_labels.json
against the SAME frozen, SHA-pinned daily candles the detection runner read
(data/crypto_d1_spot/raw/{BTC,ETH,SOL}_1d.csv), re-aligned on their common dates
EXACTLY as detection did so that each label's setup_index lines up.

HUMAN-FIXED REPLAY ASSUMPTION (disclosed): the C11 spec pre-declared entry, stop,
2R/3R/4R targets, the 81 bps floor and the 37 bps cost model, but did NOT
pre-declare a holding horizon. The human fixed a 5-bar / 5-day horizon at the
replay gate (HUMAN_DECISION_C11_ADVANCE_TO_FEE_HONEST_REPLAY_RESEARCH_ONLY),
chosen to match the 5-day dispersion lookback and to avoid reintroducing C10's
long-drift trap. The horizon was NOT optimized after seeing results.

C11 geometry (long the relative laggard): entry at the signal-bar close; stop =
1.5*ATR(14); target variants 2R/3R/4R. For each accepted label and each variant
the runner walks bars[setup_index+1 .. setup_index+5] of the LAGGARD asset:
  - MISS:     low  <= stop_price   -> gross_r = -1
  - HIT:      high >= target_price -> gross_r = +variant_r
  - STRADDLE: both in the same bar -> STOP FIRST (conservative honest) -> -1
  - HORIZON:  neither by bar +5    -> exit at the +5 close:
              gross_r = (exit_close - entry_close) / stop_distance
Every outcome is decisive. Labels whose +5 horizon bar falls beyond the frozen
source (the last few 2026 bars) are recorded as horizon_bar_beyond_source and
excluded from the aggregates (counted for evidence).

One position per asset (the spec's one_position_per_asset rule): a replay-time
per-asset non-overlap = REDUCE-OR-KEEP-ONLY -- drop a later setup on the SAME
asset whose entry is at/before that asset's active resolved exit. Never add.
Different assets may overlap (that is the cross-asset nature of the edge).

Costs as R-units of each setup's stop distance: 27 bps round-trip fee (locked) +
10 bps round-trip slippage (declared conservative 5 bps/side haircut) = 37 bps
all-in. net_r_fee_only = gross_r - fee_r; net_r_all_in = gross_r - fee_r -
slippage_r. The 81 bps gross target-distance floor was already enforced at label
time (re-recorded for evidence).

Aggregates per variant: counts, trade count, win rate (net_all_in > 0), hit rate,
gross/fee-only/all-in average R and total R, max drawdown of the all-in net R
equity curve, worst losing streak, and per-asset / per-regime / per-year /
forward-OOS (>= 2026-01-01) breakdowns of all-in net R. The runner also records
relative-vs-long-drift evidence (regime symmetry + horizon/hit mix).

Writes two untracked JSON artifacts under
data/cross_asset_dispersion_reversion_c11/replay_results/ (gitignored) and
re-verifies every input SHA before, during and after. Invoked manually under an
explicit human-approved replay gate. Side effects only inside main().
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

CANDIDATE_ID = "CROSS_ASSET_DISPERSION_REVERSION_V1"
CANDIDATE_FAMILY = "cross_asset_dispersion_reversion"
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"
DIRECTION = "long_only"

# --- human-fixed replay assumption (disclosed; spec did NOT pre-declare it) ---
HOLDING_HORIZON_BARS = 5
HORIZON_SOURCE = "human_fixed_at_replay_gate_spec_did_not_predeclare"
HORIZON_RATIONALE = (
    "matches the 5-day dispersion lookback; avoids C10 long-drift trap; not "
    "optimized after seeing results")

FEE_ROUND_TRIP_BPS = 27.0          # locked at spec
SLIPPAGE_ROUND_TRIP_BPS = 10.0     # declared conservative 5 bps/side haircut
ALL_IN_ROUND_TRIP_BPS = 37.0
TARGET_DISTANCE_FLOOR_BPS = 81.0
VARIANTS = (("2r", 2.0), ("3r", 3.0), ("4r", 4.0))
SAME_BAR_STRADDLE_POLICY = "stop_first_conservative_miss"
NON_OVERLAP_POLICY = "per_asset_reduce_or_keep_only_never_add"
FORWARD_OOS_START = "2026-01-01"
REGIMES = ("bull", "bear", "chop")

HEAD_AT_LABELS_REVIEW = "8e69956ba10ea1c5dd80c2860b71142e2e9f512a"

SOURCES = {s: REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / ("%s_1d.csv"
           % s.replace("USD", "")) for s in SYMBOLS}
EXPECTED_SOURCE_SHA = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}
LABELS_INPUT = (REPO_ROOT / "data" / "cross_asset_dispersion_reversion_c11"
                / "detector_labels" / "c11_detector_labels.json")
EXPECTED_LABELS_SHA = (
    "2a1273eb9a093a3e75a48748afd6a533954165de403b3dba7ebde291e38dc231")

OUT_DIR = (REPO_ROOT / "data" / "cross_asset_dispersion_reversion_c11"
           / "replay_results")
REPLAY_LEDGER_PATH = OUT_DIR / "c11_replay_ledger.json"
REPLAY_SUMMARY_PATH = OUT_DIR / "c11_replay_summary.json"


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_rows(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({"date": r["date"], "open": float(r["open"]),
                         "high": float(r["high"]), "low": float(r["low"]),
                         "close": float(r["close"])})
    rows.sort(key=lambda b: b["date"])
    return rows


def build_aligned(rows):
    """Re-align the assets on their common dates EXACTLY as the detection runner
    did, so a label's setup_index lines up with aligned[laggard][setup_index]."""
    date_sets = [set(b["date"] for b in rows[s]) for s in SYMBOLS]
    common = sorted(set.intersection(*date_sets))
    by_date = {s: {b["date"]: b for b in rows[s]} for s in SYMBOLS}
    aligned = {s: [by_date[s][d] for d in common] for s in SYMBOLS}
    return common, aligned


def evaluate_one_variant(bars, label, variant_r):
    """Walk one accepted laggard label over the fixed 5-bar horizon for one
    R-multiple variant. Pure; structural fields only."""
    entry = float(label["entry_price"])
    stop_price = float(label["stop_price"])
    stop_distance = float(label["stop_distance"])
    stop_distance_bps = (stop_distance / entry) * 10000.0
    target_price = entry + variant_r * stop_distance
    target_distance_bps = (variant_r * stop_distance / entry) * 10000.0
    entry_index = int(label["setup_index"])
    exit_index = entry_index + HOLDING_HORIZON_BARS
    fee_r = FEE_ROUND_TRIP_BPS / stop_distance_bps
    slippage_r = SLIPPAGE_ROUND_TRIP_BPS / stop_distance_bps
    out = {
        "setup_index": entry_index,
        "entry_date": label["date"],
        "entry_year": label["year"],
        "laggard_symbol": label["laggard_symbol"],
        "regime": label["regime"],
        "in_forward_oos_window": bool(label["in_forward_oos_window"]),
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
    # Integrity: the label's absolute index must line up with the frozen aligned
    # bars (same date + same entry close the detector read).
    if entry_index >= len(bars) or bars[entry_index]["date"] != label["date"]:
        out["outcome"] = "index_date_mismatch_abort"
        return out
    if abs(float(bars[entry_index]["close"]) - entry) > 1e-6:
        out["outcome"] = "entry_close_mismatch_abort"
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
    exit_close = float(bars[exit_index]["close"])
    gross_r = (exit_close - entry) / stop_distance
    return _finish("horizon", exit_index, exit_close, gross_r)


def apply_non_overlap_per_variant(labels_sorted, aligned, variant_r):
    """Per-asset REDUCE-OR-KEEP-ONLY: drop a later setup on the SAME asset whose
    entry_index is <= that asset's active resolved exit index. Different assets
    may overlap. Never add."""
    kept = []
    dropped_overlap = []
    active_exit_index = {s: None for s in SYMBOLS}
    for label in labels_sorted:
        sym = label["laggard_symbol"]
        entry_index = int(label["setup_index"])
        active = active_exit_index.get(sym)
        if active is not None and entry_index <= active:
            dropped_overlap.append({
                "setup_index": entry_index,
                "entry_date": label["date"],
                "laggard_symbol": sym,
                "variant": "%dr" % int(variant_r),
                "outcome": "dropped_replay_time_non_overlap",
                "blocked_by_active_exit_index": active,
            })
            continue
        outcome = evaluate_one_variant(aligned[sym], label, variant_r)
        kept.append(outcome)
        if outcome["exit_resolved_index"] is not None:
            active_exit_index[sym] = outcome["exit_resolved_index"]
    return {"kept": kept, "dropped_overlap": dropped_overlap}


def _bucket():
    return {"trades": 0, "wins": 0, "gross_r_sum": 0.0,
            "net_all_in_r_sum": 0.0}


def _accum(bucket, o):
    bucket["trades"] += 1
    bucket["wins"] += 1 if o["net_r_all_in"] > 0 else 0
    bucket["gross_r_sum"] += o["gross_r"]
    bucket["net_all_in_r_sum"] += o["net_r_all_in"]


def aggregate_variant(kept):
    """Counts + win/hit rates + R sums/means + max drawdown + worst losing
    streak + per-asset / per-regime / per-year / forward-OOS. Pure. All-in net R
    (fee + slippage) is the headline cost basis."""
    counts = {"hit": 0, "miss": 0, "miss_same_bar_straddle": 0, "horizon": 0,
              "index_date_mismatch_abort": 0, "entry_close_mismatch_abort": 0,
              "horizon_bar_beyond_source": 0}
    resolved = [o for o in kept if o.get("net_r_all_in") is not None]
    unresolved = [o for o in kept if o.get("net_r_all_in") is None]
    for o in unresolved:
        counts[o["outcome"]] = counts.get(o["outcome"], 0) + 1
    ordered = sorted(resolved, key=lambda o: o["setup_index"])
    n = 0
    wins = 0
    hits = 0
    gross_sum = 0.0
    net_fee_sum = 0.0
    net_all_in_sum = 0.0
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    cur_loss_streak = 0
    worst_loss_streak = 0
    per_year: dict = {}
    per_asset: dict = {s: _bucket() for s in SYMBOLS}
    per_regime: dict = {r: _bucket() for r in REGIMES}
    forward_oos = {"in_sample": _bucket(), "forward_oos": _bucket()}
    for o in ordered:
        oc = o["outcome"]
        counts[oc] = counts.get(oc, 0) + 1
        n += 1
        gross_sum += o["gross_r"]
        net_fee_sum += o["net_r_fee_only"]
        net_all_in_sum += o["net_r_all_in"]
        if o["net_r_all_in"] > 0:
            wins += 1
            cur_loss_streak = 0
        else:
            cur_loss_streak += 1
            worst_loss_streak = max(worst_loss_streak, cur_loss_streak)
        if oc == "hit":
            hits += 1
        equity += o["net_r_all_in"]
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
        yr = o["entry_year"]
        per_year.setdefault(yr, _bucket())
        _accum(per_year[yr], o)
        _accum(per_asset[o["laggard_symbol"]], o)
        _accum(per_regime[o["regime"]], o)
        _accum(forward_oos["forward_oos" if o["in_forward_oos_window"]
                           else "in_sample"], o)

    def _finalize(b):
        b = dict(b)
        b["win_rate"] = (b["wins"] / b["trades"]) if b["trades"] else None
        return b

    return {
        "counts": counts,
        "trade_count": n,
        "unresolved_horizon_beyond_source":
            counts["horizon_bar_beyond_source"],
        "win_count_net_all_in": wins,
        "win_rate_net_all_in": (wins / n if n else None),
        "hit_count": hits,
        "hit_rate": (hits / n if n else None),
        "horizon_exit_count": counts["horizon"],
        "horizon_exit_share": (counts["horizon"] / n if n else None),
        "gross_r_total": gross_sum,
        "net_r_total_fee_only": net_fee_sum,
        "net_r_total_all_in": net_all_in_sum,
        "gross_r_mean": (gross_sum / n if n else None),
        "net_r_mean_fee_only": (net_fee_sum / n if n else None),
        "net_r_mean_all_in": (net_all_in_sum / n if n else None),
        "max_drawdown_r_all_in": max_dd,
        "worst_losing_streak": worst_loss_streak,
        "net_all_in_positive_after_costs": net_all_in_sum > 0,
        "per_year_net_all_in": {k: _finalize(v)
                                for k, v in sorted(per_year.items())},
        "per_asset_net_all_in": {k: _finalize(v)
                                 for k, v in per_asset.items()},
        "per_regime_net_all_in": {k: _finalize(v)
                                  for k, v in per_regime.items()},
        "forward_oos_net_all_in": {k: _finalize(v)
                                   for k, v in forward_oos.items()},
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source_sha_before = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    labels_sha_before = compute_sha256(LABELS_INPUT)
    if source_sha_before != EXPECTED_SOURCE_SHA:
        raise RuntimeError("source_sha_pins_do_not_match_before_replay")
    if labels_sha_before != EXPECTED_LABELS_SHA:
        raise RuntimeError("labels_sha_pin_does_not_match_before_replay")

    rows = {s: load_rows(SOURCES[s]) for s in SYMBOLS}
    common, aligned = build_aligned(rows)
    if not common:
        raise RuntimeError("no_common_dates_across_assets")

    with open(LABELS_INPUT, encoding="utf-8") as f:
        labels_payload = json.load(f)
    accepted = labels_payload.get("accepted_labels") or []
    if not accepted:
        raise RuntimeError("no_accepted_labels_in_artifact")
    accepted_count = len(accepted)
    labels_sorted = sorted(accepted, key=lambda s: int(s["setup_index"]))

    per_variant = {}
    variant_aggregates = {}
    for name, multiple in VARIANTS:
        result = apply_non_overlap_per_variant(labels_sorted, aligned, multiple)
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

    source_sha_mid = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    labels_sha_mid = compute_sha256(LABELS_INPUT)
    inputs_unchanged = (source_sha_mid == source_sha_before
                        and labels_sha_mid == labels_sha_before)
    if not inputs_unchanged:
        raise RuntimeError("inputs_mutated_during_replay_evaluation")

    # Relative-vs-long-drift evidence (NOT a profitability claim): a relative
    # cross-sectional edge should hold across regimes (esp. bear) and not be
    # explained purely by holding drift in bull. Reported for human review.
    headline = variant_aggregates["3r"]
    pr = headline["per_regime_net_all_in"]
    regimes_positive = {r: (pr[r]["net_all_in_r_sum"] > 0) for r in REGIMES}
    pa = headline["per_asset_net_all_in"]
    assets_positive = {s: (pa[s]["net_all_in_r_sum"] > 0) for s in SYMBOLS}
    relative_evidence = {
        "headline_variant": "3r",
        "regimes_net_positive": regimes_positive,
        "positive_in_bear_regime": regimes_positive.get("bear", False),
        "positive_regime_count": sum(1 for v in regimes_positive.values() if v),
        "assets_net_positive": assets_positive,
        "positive_asset_count": sum(1 for v in assets_positive.values() if v),
        "horizon_exit_share_3r": headline["horizon_exit_share"],
        "hit_rate_3r": headline["hit_rate"],
    }

    scope_locks = {
        "no_paper_trading": True, "no_micro_live": True,
        "no_live_trading": True, "no_broker": True, "no_exchange": True,
        "no_wallet": True, "no_account": True, "no_credentials": True,
        "no_order_logic": True, "no_portfolio_allocation": True,
        "no_portfolio_compute": True, "no_api": True, "no_network": True,
        "no_fetch": True, "no_data_mutation": True, "no_notification": True,
        "no_scheduler": True, "no_relabel": True, "no_detector_change": True,
        "no_parameter_fitting": True, "no_horizon_optimization": True,
        "no_best_asset_selection": True, "no_profitability_claim": True,
        "no_paper_live_readiness_claim": True, "no_downstream_gate_unlock": True,
        "no_staging": True, "no_commit": True, "no_push": True,
    }
    common_meta = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME, "direction": DIRECTION,
        "common_window": [common[0], common[-1]],
        "common_bar_count": len(common),
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "labels_input_path":
            str(LABELS_INPUT.relative_to(REPO_ROOT)).replace("\\", "/"),
        "labels_input_sha256_before": labels_sha_before,
        "labels_input_sha256_after": labels_sha_mid,
        "source_paths": {s: str(SOURCES[s].relative_to(REPO_ROOT)).replace(
            "\\", "/") for s in SYMBOLS},
        "source_sha256_before": source_sha_before,
        "source_sha256_after": source_sha_mid,
        "inputs_unchanged_during_evaluation": inputs_unchanged,
        "accepted_label_input_count": accepted_count,
        "holding_horizon_bars": HOLDING_HORIZON_BARS,
        "horizon_source": HORIZON_SOURCE,
        "horizon_rationale": HORIZON_RATIONALE,
        "spec_predeclared_horizon": False,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "target_distance_floor_bps": TARGET_DISTANCE_FLOOR_BPS,
        "variants": [name for name, _ in VARIANTS],
        "same_bar_straddle_policy": SAME_BAR_STRADDLE_POLICY,
        "non_overlap_policy": NON_OVERLAP_POLICY,
        "forward_oos_start": FORWARD_OOS_START,
        "relative_vs_long_drift_evidence": relative_evidence,
        "scope_locks": scope_locks,
        "honest_framing": (
            "out-of-sample real-candle replay only; fee+slippage honest (37 bps "
            "all-in); 5-bar horizon is a HUMAN-FIXED replay assumption (the C11 "
            "spec did not pre-declare a horizon); relative/cross-sectional edge "
            "(not long-drift) under review; no live profitability claim; no "
            "edge asserted; no relabel; no parameter/horizon fitting; no "
            "best-asset selection; no downstream gate unlocked"),
    }
    ledger_payload = dict(common_meta)
    ledger_payload["artifact"] = "c11_replay_ledger"
    ledger_payload["per_variant"] = per_variant
    summary_payload = dict(common_meta)
    summary_payload["artifact"] = "c11_replay_summary"
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

    source_sha_after = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    labels_sha_after = compute_sha256(LABELS_INPUT)
    if not (source_sha_after == source_sha_before
            and labels_sha_after == labels_sha_before):
        raise RuntimeError("inputs_mutated_after_replay_artifact_write")

    report = {
        "ledger_path": str(REPLAY_LEDGER_PATH.relative_to(REPO_ROOT)).replace(
            "\\", "/"),
        "ledger_sha256": ledger_sha,
        "summary_path": str(REPLAY_SUMMARY_PATH.relative_to(REPO_ROOT)).replace(
            "\\", "/"),
        "summary_sha256": summary_sha,
        "accepted_label_input_count": accepted_count,
        "source_sha256_stable": source_sha_before == source_sha_after,
        "labels_sha256_stable": labels_sha_before == labels_sha_after,
        "variant_aggregates": variant_aggregates,
        "relative_vs_long_drift_evidence": relative_evidence,
    }
    for key, value in report.items():
        print("%s = %r" % (key, value))
    return report


if __name__ == "__main__":
    main()

"""C14 conviction-bar follow-through fee+slippage-honest replay one-off runner
(READ-ONLY against the FROZEN, SHA-pinned C14 detector-labels artifact and the
frozen BTC/ETH/SOL 1d sources; RESEARCH ONLY; NO data fetch; NO relabel; NO
parameter optimization; NO one-edit allowance; NO robustness; NO portfolio
compute; NO trading / broker / credentials / orders; NO paper/live readiness
claim).

Replays the 347 frozen conviction-bar labels (the FROZEN labels artifact) over the
SAME frozen, SHA-pinned daily candles, PER ASSET, with the committed C14 geometry
(entry at the conviction bar's close; stop = close - 1.0*ATR(14); targets
1R/1.5R/2R; <=2-bar hold; stop-first same-bar straddle) and a per-asset
RESOLVED-EXIT non-overlap (reduce-or-keep-only). Costs are 37 bps all-in (27 fee +
10 slippage) as R-units of each setup's stop distance.

It then runs the DECISIVE C14 gates the spec requires at the replay stage:
  * net after costs by variant,
  * MUST BEAT a matched BUY-AND-HOLD baseline (same entry windows, passive hold
    to the +2 close, same cost),
  * MUST BEAT a matched RANDOM-ENTRY baseline (same #trades per asset, random
    entry bars from a FIXED deterministic seed, identical geometry + cost,
    averaged over deterministic resamples),
  * horizon-exit share <= 50% AND target capture dominates (hits > horizons),
  * bull/bear/chop net symmetry (bear and chop must not be structurally weak),
  * forward-OOS 2026 continuation must be net-positive.

NO live/paper claim is made. Writes two untracked JSON artifacts under
data/conviction_bar_follow_through_c14/replay_results/ (gitignored) and re-verifies
every input SHA before/during/after. Side effects only in main().
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.conviction_bar_follow_through_v1_detector_spec_dry_run_contract as det  # noqa: E402,E501

CANDIDATE_ID = "CONVICTION_BAR_FOLLOW_THROUGH_V1"
CANDIDATE_FAMILY = "conviction_bar_follow_through"
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"
DIRECTION = "long_only"
REGIMES = ("bull", "bear", "chop")

FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = 37.0
VARIANTS = (("1r", 1.0), ("1.5r", 1.5), ("2r", 2.0))
MAX_HOLD_BARS = det.MAX_HOLD_BARS
MAX_HORIZON_EXIT_SHARE = det.MAX_HORIZON_EXIT_SHARE   # 0.50
WARMUP = det.WARMUP
FORWARD_OOS_START = "2026-01-01"

RANDOM_MASTER_SEED = 20260617
RANDOM_RESAMPLES = 200

HEAD_AT_LABELS_REVIEW = "bc69e4f0b0cf1e63ed00d6cb02b991f3d9d22ac6"

SOURCES = {s: REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / ("%s_1d.csv"
           % s.replace("USD", "")) for s in SYMBOLS}
EXPECTED_SOURCE_SHA = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}
LABELS_INPUT = (REPO_ROOT / "data" / "conviction_bar_follow_through_c14"
                / "detector_labels" / "c14_detector_labels.json")
EXPECTED_LABELS_SHA = (
    "9797558c96e6b937098ee84447c74f7adb206519a49143b9834af0cd99f372d6")

OUT_DIR = (REPO_ROOT / "data" / "conviction_bar_follow_through_c14"
           / "replay_results")
REPLAY_LEDGER_PATH = OUT_DIR / "c14_replay_ledger.json"
REPLAY_SUMMARY_PATH = OUT_DIR / "c14_replay_summary.json"


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


def _net_from_gross(gross_r, entry, stop_distance):
    bps = (stop_distance / entry) * 10000.0
    return gross_r - FEE_ROUND_TRIP_BPS / bps, gross_r - ALL_IN_ROUND_TRIP_BPS / bps


def _bucket():
    return {"trades": 0, "wins": 0, "net_all_in_r_sum": 0.0, "gross_r_sum": 0.0}


def _accum(b, gross, net_all):
    b["trades"] += 1
    b["wins"] += 1 if net_all > 0 else 0
    b["gross_r_sum"] += gross
    b["net_all_in_r_sum"] += net_all


def replay_variant(labels_by_asset, bars_by_asset, variant_r):
    kept_rows = []
    counts = {"hit": 0, "miss": 0, "miss_same_bar_straddle": 0, "horizon": 0,
              "horizon_bar_beyond_source": 0}
    n = 0
    wins = 0
    gross_sum = net_fee_sum = net_all_sum = 0.0
    per_regime = {r: _bucket() for r in REGIMES}
    per_asset = {s: _bucket() for s in SYMBOLS}
    per_year: dict = {}
    fwd = {"in_sample": _bucket(), "forward_oos": _bucket()}
    bh_net_all_sum = 0.0
    chrono = []

    for s in SYMBOLS:
        bars = bars_by_asset[s]
        setups = sorted(labels_by_asset.get(s, []),
                        key=lambda x: int(x["setup_index"]))
        res = det.apply_non_overlap(setups, bars, variant_r)
        for k in res["kept"]:
            ho = k["horizon_outcome"]
            oc = ho["outcome"]
            counts[oc] = counts.get(oc, 0) + 1
            if ho["gross_r"] is None:
                continue
            entry = float(k["entry_price"])
            sd = float(k["stop_distance"])
            gross = ho["gross_r"]
            net_fee, net_all = _net_from_gross(gross, entry, sd)
            n += 1
            wins += 1 if net_all > 0 else 0
            gross_sum += gross
            net_fee_sum += net_fee
            net_all_sum += net_all
            _accum(per_regime[k["regime"]], gross, net_all)
            _accum(per_asset[s], gross, net_all)
            per_year.setdefault(k["year"], _bucket())
            _accum(per_year[k["year"]], gross, net_all)
            _accum(fwd["forward_oos" if k["in_forward_oos_window"]
                       else "in_sample"], gross, net_all)
            chrono.append((k["date"], net_all))
            t = int(k["setup_index"])
            bh_idx = t + MAX_HOLD_BARS
            if bh_idx < len(bars):
                bh_gross = (float(bars[bh_idx]["close"]) - entry) / sd
                _, bh_net_all = _net_from_gross(bh_gross, entry, sd)
                bh_net_all_sum += bh_net_all
            kept_rows.append({"symbol": s, "setup_index": t, "date": k["date"],
                              "regime": k["regime"],
                              "in_forward_oos": k["in_forward_oos_window"],
                              "outcome": oc, "gross_r": gross,
                              "net_r_all_in": net_all})

    chrono.sort(key=lambda x: x[0])
    equity = peak = max_dd = 0.0
    cur_loss = worst_loss = 0
    for _, net_all in chrono:
        equity += net_all
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
        if net_all > 0:
            cur_loss = 0
        else:
            cur_loss += 1
            worst_loss = max(worst_loss, cur_loss)

    def _fin(b):
        b = dict(b)
        b["win_rate"] = (b["wins"] / b["trades"]) if b["trades"] else None
        return b

    horizon_share = (counts["horizon"] / n) if n else None
    return {
        "variant_r_multiple": variant_r, "counts": counts, "trade_count": n,
        "win_count_net_all_in": wins,
        "win_rate_net_all_in": (wins / n if n else None),
        "hit_count": counts["hit"], "horizon_count": counts["horizon"],
        "hit_rate": (counts["hit"] / n if n else None),
        "horizon_exit_share": horizon_share,
        "target_capture_dominates": counts["hit"] > counts["horizon"],
        "gross_r_total": gross_sum, "net_r_total_fee_only": net_fee_sum,
        "net_r_total_all_in": net_all_sum,
        "net_r_mean_all_in": (net_all_sum / n if n else None),
        "max_drawdown_r_all_in": max_dd, "worst_losing_streak": worst_loss,
        "buy_and_hold_net_all_in_total": bh_net_all_sum,
        "per_regime_net_all_in": {r: _fin(per_regime[r]) for r in REGIMES},
        "per_asset_net_all_in": {s: _fin(per_asset[s]) for s in SYMBOLS},
        "per_year_net_all_in": {k: _fin(v) for k, v in sorted(per_year.items())},
        "forward_oos_net_all_in": {k: _fin(v) for k, v in fwd.items()},
        "_kept_rows": kept_rows,
    }


def _random_entry_total(bars_by_asset, kept_count_by_asset, variant_r, seed):
    rng = random.Random(seed)
    total = 0.0
    for s in SYMBOLS:
        k = kept_count_by_asset.get(s, 0)
        if k <= 0:
            continue
        bars = bars_by_asset[s]
        eligible = list(range(WARMUP, len(bars) - MAX_HOLD_BARS))
        picks = eligible if len(eligible) < k else rng.sample(eligible, k)
        pseudo = []
        for t in sorted(picks):
            entry = float(bars[t]["close"])
            atr = det.compute_atr14(bars, t)
            if atr is None:
                continue
            stop = det.compute_stop(entry, atr)
            if not stop["valid"]:
                continue
            pseudo.append({"setup_index": t, "entry_price": entry,
                           "stop_price": stop["stop_price"],
                           "stop_distance": stop["stop_distance"]})
        res = det.apply_non_overlap(pseudo, bars, variant_r)
        for kk in res["kept"]:
            ho = kk["horizon_outcome"]
            if ho["gross_r"] is None:
                continue
            _, net_all = _net_from_gross(ho["gross_r"], float(kk["entry_price"]),
                                         float(kk["stop_distance"]))
            total += net_all
    return total


def random_entry_baseline(bars_by_asset, kept_count_by_asset, variant_r):
    totals = [_random_entry_total(bars_by_asset, kept_count_by_asset, variant_r,
                                  RANDOM_MASTER_SEED * 1000 + i)
              for i in range(RANDOM_RESAMPLES)]
    return totals


def decisive_gates(agg, bh_total, random_mean, random_pctl):
    pr = agg["per_regime_net_all_in"]
    bull = pr["bull"]["net_all_in_r_sum"]
    bear = pr["bear"]["net_all_in_r_sum"]
    chop = pr["chop"]["net_all_in_r_sum"]
    fo = agg["forward_oos_net_all_in"]["forward_oos"]["net_all_in_r_sum"]
    gates = {
        "net_after_costs_positive": agg["net_r_total_all_in"] > 0,
        "beats_buy_and_hold": agg["net_r_total_all_in"] > bh_total,
        "beats_random_entry_mean": agg["net_r_total_all_in"] > random_mean,
        "random_entry_percentile": random_pctl,
        "horizon_exit_share_within_cap":
            (agg["horizon_exit_share"] is not None
             and agg["horizon_exit_share"] <= MAX_HORIZON_EXIT_SHARE),
        "target_capture_dominates": bool(agg["target_capture_dominates"]),
        "regime_symmetry_all_positive": bull > 0 and bear > 0 and chop > 0,
        "bear_not_structurally_weak": bear >= 0,
        "chop_not_structurally_weak": chop >= 0,
        "forward_oos_2026_positive": fo > 0,
    }
    gates["variant_pass"] = (
        gates["net_after_costs_positive"] and gates["beats_buy_and_hold"]
        and gates["beats_random_entry_mean"]
        and gates["horizon_exit_share_within_cap"]
        and gates["target_capture_dominates"]
        and gates["regime_symmetry_all_positive"]
        and gates["forward_oos_2026_positive"])
    return gates


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source_sha_before = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    labels_sha_before = compute_sha256(LABELS_INPUT)
    if source_sha_before != EXPECTED_SOURCE_SHA:
        raise RuntimeError("source_sha_pins_do_not_match_before_replay")
    if labels_sha_before != EXPECTED_LABELS_SHA:
        raise RuntimeError("labels_sha_pin_does_not_match_before_replay")

    bars_by_asset = {s: load_rows(SOURCES[s]) for s in SYMBOLS}
    with open(LABELS_INPUT, encoding="utf-8") as f:
        labels_payload = json.load(f)
    accepted = labels_payload.get("accepted_labels") or []
    if not accepted:
        raise RuntimeError("no_accepted_labels_in_artifact")
    labels_by_asset: dict = {s: [] for s in SYMBOLS}
    for lab in accepted:
        labels_by_asset[lab["symbol"]].append(lab)

    for s in SYMBOLS:
        for lab in labels_by_asset[s]:
            t = int(lab["setup_index"])
            b = bars_by_asset[s][t]
            if b["date"] != lab["date"] or abs(
                    float(b["close"]) - float(lab["entry_price"])) > 1e-6:
                raise RuntimeError("label_index_date_close_mismatch_%s_%d"
                                   % (s, t))

    per_variant = {}
    variant_gates = {}
    for name, mult in VARIANTS:
        agg = replay_variant(labels_by_asset, bars_by_asset, mult)
        kept_count_by_asset = {
            s: agg["per_asset_net_all_in"][s]["trades"] for s in SYMBOLS}
        totals = random_entry_baseline(bars_by_asset, kept_count_by_asset, mult)
        rb_mean = sum(totals) / len(totals)
        pctl = sum(1 for x in totals
                   if agg["net_r_total_all_in"] > x) / len(totals)
        gates = decisive_gates(agg, agg["buy_and_hold_net_all_in_total"],
                               rb_mean, pctl)
        ledger_rows = agg.pop("_kept_rows")
        per_variant[name] = {
            "aggregates": agg,
            "random_entry_baseline": {
                "resamples": RANDOM_RESAMPLES, "master_seed": RANDOM_MASTER_SEED,
                "mean_net_all_in_total": rb_mean, "min_net_all_in_total": min(totals),
                "max_net_all_in_total": max(totals)},
            "decisive_gates": gates, "kept_rows": ledger_rows}
        variant_gates[name] = gates

    any_variant_pass = any(g["variant_pass"] for g in variant_gates.values())
    structural_rejection_pressure = not any_variant_pass

    source_sha_mid = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    labels_sha_mid = compute_sha256(LABELS_INPUT)
    inputs_unchanged = (source_sha_mid == source_sha_before
                        and labels_sha_mid == labels_sha_before)
    if not inputs_unchanged:
        raise RuntimeError("inputs_mutated_during_replay")

    scope_locks = {
        "no_data_fetch": True, "no_relabel": True,
        "no_parameter_optimization": True, "no_one_edit_allowance_used": True,
        "no_robustness": True, "no_portfolio_compute": True,
        "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_data_mutation": True,
        "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
        "no_downstream_gate_unlock": True, "no_staging": True,
        "no_commit": True, "no_push": True,
    }
    common = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME, "direction": DIRECTION,
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "labels_input_path":
            str(LABELS_INPUT.relative_to(REPO_ROOT)).replace("\\", "/"),
        "labels_input_sha256_before": labels_sha_before,
        "labels_input_sha256_after": labels_sha_mid,
        "source_sha256_before": source_sha_before,
        "source_sha256_after": source_sha_mid,
        "inputs_unchanged_during_replay": inputs_unchanged,
        "replayed_label_count": len(accepted),
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "max_hold_bars": MAX_HOLD_BARS,
        "max_horizon_exit_share": MAX_HORIZON_EXIT_SHARE,
        "variants": [n for n, _ in VARIANTS],
        "same_bar_straddle_policy": "stop_first_conservative_miss",
        "non_overlap_policy": "per_asset_resolved_exit_reduce_or_keep_only",
        "buy_and_hold_baseline": "matched_window_passive_hold_to_plus_max_hold_close",
        "random_entry_baseline":
            "fixed_seed_resampled_random_bars_identical_geometry",
        "forward_oos_start": FORWARD_OOS_START,
        "any_variant_passes_all_decisive_gates": any_variant_pass,
        "structural_rejection_pressure": structural_rejection_pressure,
        "scope_locks": scope_locks,
        "honest_framing": (
            "out-of-sample real-candle replay of the 347 frozen labels; "
            "fee+slippage honest (37 bps); the decisive gates -- beat buy-and-"
            "hold AND random-entry, horizon-exit cap, regime symmetry, "
            "forward-OOS 2026 -- are reported honestly; no relabel; no "
            "optimization; no one-edit; not a profitability or paper/live "
            "readiness claim"),
    }
    ledger_payload = dict(common)
    ledger_payload["artifact"] = "c14_replay_ledger"
    ledger_payload["per_variant"] = per_variant
    summary_payload = dict(common)
    summary_payload["artifact"] = "c14_replay_summary"
    summary_payload["variant_summaries"] = {
        name: {k: v for k, v in pv["aggregates"].items()}
        | {"random_entry_baseline": pv["random_entry_baseline"],
           "decisive_gates": pv["decisive_gates"]}
        for name, pv in per_variant.items()}

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
        "replayed_label_count": len(accepted),
        "source_sha256_stable": source_sha_before == source_sha_after,
        "labels_sha256_stable": labels_sha_before == labels_sha_after,
        "any_variant_passes_all_decisive_gates": any_variant_pass,
        "structural_rejection_pressure": structural_rejection_pressure,
    }
    for key in ("ledger_path", "ledger_sha256", "summary_path", "summary_sha256",
                "replayed_label_count", "source_sha256_stable",
                "labels_sha256_stable", "any_variant_passes_all_decisive_gates",
                "structural_rejection_pressure"):
        print("%s = %r" % (key, report[key]))
    for name, _ in VARIANTS:
        a = per_variant[name]["aggregates"]
        g = per_variant[name]["decisive_gates"]
        rb = per_variant[name]["random_entry_baseline"]
        print("--- %s: trades=%d net_all_in=%.3f bh=%.3f rand_mean=%.3f "
              "pctl=%.2f hit=%d horizon=%d hshare=%.3f bull=%.3f bear=%.3f "
              "chop=%.3f fwd_oos=%.3f PASS=%s" % (
                  name, a["trade_count"], a["net_r_total_all_in"],
                  a["buy_and_hold_net_all_in_total"], rb["mean_net_all_in_total"],
                  g["random_entry_percentile"], a["hit_count"],
                  a["horizon_count"], a["horizon_exit_share"] or 0.0,
                  a["per_regime_net_all_in"]["bull"]["net_all_in_r_sum"],
                  a["per_regime_net_all_in"]["bear"]["net_all_in_r_sum"],
                  a["per_regime_net_all_in"]["chop"]["net_all_in_r_sum"],
                  a["forward_oos_net_all_in"]["forward_oos"]["net_all_in_r_sum"],
                  g["variant_pass"]))
    return report


if __name__ == "__main__":
    main()

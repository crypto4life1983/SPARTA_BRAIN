"""C15 slow vol-targeted time-series momentum FEE-HONEST replay one-off runner
(READ-ONLY against the FROZEN C15 labels + FROZEN local BTC/ETH/SOL 1d data;
RESEARCH ONLY; NO data fetch; NO re-detection of a new label set; NO relabel; NO
parameter optimization; NO robustness expansion; NO portfolio construction; NO
trading / broker / credentials / orders; NO paper/live readiness claim).

Replays ONLY the frozen C15 entry-event labels (SHA-pinned). For each entry it
resolves the position's signal-driven exit by walking the frozen detector state
(flip / flat) with the vol-stop applied intrabar, then computes a FEE-HONEST,
R-unit-normalized net result:

  risk_distance = STOP_ATR_MULT * ATR14[entry]
  gross_r       = side * (exit_price - entry_price) / risk_distance
  cost_r        = ALL_IN_BPS / risk_distance_bps         (37 bps, round trip)
  net_r         = gross_r - cost_r

R-unit results are volatility-scale invariant (vol-targeting scales notional and
risk together), so position_scale cancels and is NOT applied to R. The 37 bps
all-in cost (27 fee + 10 slippage) is applied to EVERY trade and CANNOT be
dropped. Computes a matched buy-and-hold baseline and a deterministic random-entry
baseline (fixed seed, >=200 resamples via an internal LCG -- no RNG import). All
decisive gates are evaluated here; the verdict is recorded for human review.
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

import sparta_commander.slow_vol_targeted_time_series_momentum_v1_detector_spec_dry_run_contract as det  # noqa: E402,E501

CANDIDATE_ID = "SLOW_VOL_TARGETED_TIME_SERIES_MOMENTUM_V1"
CANDIDATE_FAMILY = "slow_vol_targeted_time_series_momentum"
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"

FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS  # 37.0

STOP_ATR_MULT = float(det.SPEC_PARAMS["vol_stop_atr_mult"])  # 3.0
ATR_LEN = int(det.SPEC_PARAMS["atr_lookback_days"])          # 14
FORWARD_OOS_START = "2026-01-01"
RANDOM_MASTER_SEED = 20260617
N_RESAMPLES = 200

HEAD_AT_LABELS_REVIEW = "36df56a32c20bd8e7d50b482450d281ddf1b0e00"

SOURCES = {s: REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / ("%s_1d.csv"
           % s.replace("USD", "")) for s in SYMBOLS}
EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

LABELS_DIR = (REPO_ROOT / "data" / "slow_vol_targeted_time_series_momentum_c15"
              / "detector_labels")
LABELS_PATH = LABELS_DIR / "c15_detector_labels.json"
EXPECTED_LABELS_SHA256 = (
    "d659d970e883f9fc1bc0f921f97cffe70746b03fcd236ba7d425686d26ecb8a4")

OUT_DIR = (REPO_ROOT / "data" / "slow_vol_targeted_time_series_momentum_c15"
           / "replay_results")
LEDGER_PATH = OUT_DIR / "c15_replay_ledger.json"
SUMMARY_PATH = OUT_DIR / "c15_replay_summary.json"


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


def _ema(values, span):
    k = 2.0 / (span + 1.0)
    out, e = [], None
    for v in values:
        e = v if e is None else (v * k + e * (1.0 - k))
        out.append(e)
    return out


def _atr(candles, span):
    tr = []
    for i, bar in enumerate(candles):
        if i == 0:
            tr.append(bar["high"] - bar["low"])
        else:
            pc = candles[i - 1]["close"]
            tr.append(max(bar["high"] - bar["low"], abs(bar["high"] - pc),
                          abs(bar["low"] - pc)))
    return _ema(tr, span)


def _median(xs):
    s = sorted(xs)
    n = len(s)
    if n == 0:
        return 0
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def resolve_trade(bars, states, atr, t, side):
    """Walk the frozen strategy from entry index t to its signal-driven exit
    (flip/flat) with the vol-stop applied intrabar. Returns net_r, gross_r,
    hold_bars. R-unit (scale-invariant); 37 bps cost applied."""
    entry_price = bars[t]["close"]
    risk = STOP_ATR_MULT * atr[t]
    if risk <= 0:
        return None
    entry_state = "long" if side > 0 else "short"
    exit_price, exit_idx = bars[-1]["close"], len(bars) - 1
    for k in range(t + 1, len(bars)):
        if side > 0 and bars[k]["low"] <= entry_price - risk:
            exit_price, exit_idx = entry_price - risk, k
            break
        if side < 0 and bars[k]["high"] >= entry_price + risk:
            exit_price, exit_idx = entry_price + risk, k
            break
        if states[k]["state"] != entry_state:
            exit_price, exit_idx = bars[k]["close"], k
            break
    gross_r = side * (exit_price - entry_price) / risk
    risk_bps = (risk / entry_price) * 10000.0
    cost_r = ALL_IN_ROUND_TRIP_BPS / risk_bps
    return {"gross_r": gross_r, "net_r": gross_r - cost_r,
            "cost_r": cost_r, "hold_bars": exit_idx - t,
            "risk_bps": risk_bps}


def buy_and_hold_r(bars, atr, trades_rf):
    """Matched per-asset buy-and-hold in the SAME R units (whole-window move
    normalized by the asset's representative risk fraction), net of one 37 bps
    round trip."""
    first_t = None
    for i in range(len(bars)):
        if atr[i] > 0:
            first_t = i
            break
    if first_t is None or trades_rf <= 0:
        return 0.0
    move_frac = bars[-1]["close"] / bars[first_t]["close"] - 1.0
    gross_r = move_frac / trades_rf
    cost_r = (ALL_IN_ROUND_TRIP_BPS / 10000.0) / trades_rf
    return gross_r - cost_r


def lcg(seed):
    """Deterministic LCG (Numerical Recipes constants). No RNG import."""
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 0x100000000


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sha_before = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    if sha_before != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("source_sha_pins_do_not_match_before_replay")
    labels_sha = compute_sha256(LABELS_PATH)
    if labels_sha != EXPECTED_LABELS_SHA256:
        raise RuntimeError("labels_sha_pin_does_not_match_before_replay")

    with open(LABELS_PATH, encoding="utf-8") as f:
        labels_doc = json.load(f)
    frozen_labels = labels_doc["accepted_labels"]

    rows = {s: load_rows(SOURCES[s]) for s in SYMBOLS}
    states = {s: det.scan_c15_states(rows[s]) for s in SYMBOLS}
    atrs = {s: _atr(rows[s], ATR_LEN) for s in SYMBOLS}

    ledger = []
    per_asset_rf = {s: [] for s in SYMBOLS}
    for lab in frozen_labels:
        s = lab["symbol"]
        t = lab["setup_index"]
        side = 1 if lab["state"] == "long" else -1
        tr = resolve_trade(rows[s], states[s], atrs[s], t, side)
        if tr is None:
            continue
        rec = {"symbol": s, "setup_index": t, "date": lab["date"],
               "side": lab["state"], "regime": lab["labels_stage_regime"],
               "in_forward_oos_window": lab["in_forward_oos_window"],
               "gross_r": round(tr["gross_r"], 6), "net_r": round(tr["net_r"], 6),
               "cost_r": round(tr["cost_r"], 6), "hold_bars": tr["hold_bars"]}
        ledger.append(rec)
        per_asset_rf[s].append(atrs[s][t] * STOP_ATR_MULT / rows[s][t]["close"])

    ledger.sort(key=lambda r: (r["symbol"], r["setup_index"]))
    n = len(ledger)

    def _sum(items, key="net_r"):
        return round(sum(x[key] for x in items), 6)

    net_total = _sum(ledger)
    gross_total = _sum(ledger, "gross_r")
    per_asset = {s: _sum([x for x in ledger if x["symbol"] == s]) for s in SYMBOLS}
    per_regime = {r: _sum([x for x in ledger if x["regime"] == r])
                  for r in ("bull", "bear", "chop")}
    per_side = {sd: _sum([x for x in ledger if x["side"] == sd])
                for sd in ("long", "short")}
    fwd = [x for x in ledger if x["in_forward_oos_window"]]
    forward_oos_net = _sum(fwd)
    holds = [x["hold_bars"] for x in ledger]
    median_hold = int(_median(holds)) if holds else 0
    avg_hold = round(sum(holds) / n, 4) if n else 0.0

    # matched buy-and-hold per asset (R units), summed
    bh_per_asset = {}
    for s in SYMBOLS:
        rf = _median(per_asset_rf[s]) if per_asset_rf[s] else 0.0
        bh_per_asset[s] = round(buy_and_hold_r(rows[s], atrs[s], rf), 6)
    bh_total = round(sum(bh_per_asset.values()), 6)

    # deterministic random-entry baseline (fixed seed, N_RESAMPLES)
    gen = lcg(RANDOM_MASTER_SEED)
    resample_totals = []
    hold = max(1, median_hold)
    for _ in range(N_RESAMPLES):
        tot = 0.0
        for _j in range(n):
            si = int(next(gen) * len(SYMBOLS)) % len(SYMBOLS)
            s = SYMBOLS[si]
            bars = rows[s]
            lo, hi = ATR_LEN + 1, len(bars) - 2
            t = lo + int(next(gen) * (hi - lo)) if hi > lo else lo
            side = 1 if next(gen) < 0.5 else -1
            risk = STOP_ATR_MULT * atrs[s][t]
            if risk <= 0:
                continue
            entry = bars[t]["close"]
            k = min(t + hold, len(bars) - 1)
            gross_r = side * (bars[k]["close"] - entry) / risk
            risk_bps = (risk / entry) * 10000.0
            tot += gross_r - ALL_IN_ROUND_TRIP_BPS / risk_bps
        resample_totals.append(tot)
    resample_totals.sort()
    rand_mean = round(sum(resample_totals) / len(resample_totals), 6)
    below = sum(1 for x in resample_totals if x < net_total)
    rand_pctl = round(below / len(resample_totals), 4)

    # --- decisive gates ---
    gates = {
        "full_sample_net_positive": net_total > 0,
        "forward_oos_net_positive": forward_oos_net > 0,
        "no_single_regime_dependence": all(per_regime[r] > 0
                                           for r in ("bull", "bear", "chop")),
        "no_single_asset_dependence": all(per_asset[s] > 0 for s in SYMBOLS),
        "no_one_sided_side_fragility": all(per_side[sd] > 0
                                           for sd in ("long", "short")),
        "beats_buy_and_hold": net_total > bh_total,
        "beats_random_entry": net_total > rand_mean,
        "turnover_sane_for_slow_strategy": avg_hold >= 5.0,
    }
    all_gates_pass = all(gates.values())
    gross_only_would_pass = gross_total > 0  # diagnostic: gross ignores cost
    structural_rejection_pressure = not all_gates_pass

    sha_mid = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    if sha_mid != sha_before:
        raise RuntimeError("inputs_mutated_during_replay")

    common = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME,
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "source_sha256": sha_before,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "r_unit_is_volatility_scale_invariant": True,
        "no_parameter_optimization": True,
        "no_one_edit_allowance_used": True,
        "trade_count": n,
        "net_r_total_all_in": net_total,
        "gross_r_total_pre_cost": gross_total,
        "per_asset_net_r": dict(sorted(per_asset.items())),
        "per_regime_net_r": dict(sorted(per_regime.items())),
        "per_side_net_r": dict(sorted(per_side.items())),
        "forward_oos_net_r": forward_oos_net,
        "forward_oos_trade_count": len(fwd),
        "avg_hold_bars": avg_hold, "median_hold_bars": median_hold,
        "buy_and_hold_net_r_per_asset": bh_per_asset,
        "buy_and_hold_net_r_total": bh_total,
        "random_entry_seed": RANDOM_MASTER_SEED,
        "random_entry_resamples": N_RESAMPLES,
        "random_entry_mean_net_r": rand_mean,
        "random_entry_percentile_of_strategy": rand_pctl,
        "decisive_gate_results": gates,
        "all_decisive_gates_pass": all_gates_pass,
        "gross_only_would_pass": gross_only_would_pass,
        "structural_rejection_pressure": structural_rejection_pressure,
        "scope_locks": {
            "no_data_fetch": True, "no_relabel": True, "no_new_label_set": True,
            "no_parameter_optimization": True, "no_robustness": True,
            "no_portfolio_compute": True, "no_paper_trading": True,
            "no_live_trading": True, "no_broker": True, "no_credentials": True,
            "no_order_logic": True, "no_data_mutation": True,
            "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
            "no_downstream_gate_unlock": True, "no_staging": True,
            "no_commit": True, "no_push": True,
        },
        "honest_framing": (
            "fee-honest R-unit replay of the FROZEN C15 entry labels; 37 bps all-in "
            "(27 fee + 10 slippage) applied to every trade and not droppable; "
            "matched buy-and-hold + deterministic random-entry (fixed seed, 200 "
            "resamples) baselines; the decisive gates require net-positive AND "
            "forward-OOS positive AND no single regime/asset/side dependence AND "
            "beats both baselines; not a profitability or paper/live claim"),
    }
    ledger_payload = dict(common)
    ledger_payload["artifact"] = "c15_replay_ledger"
    ledger_payload["trades"] = ledger
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger_payload, f, indent=2, sort_keys=True)
    ledger_sha = compute_sha256(LEDGER_PATH)

    summary_payload = dict(common)
    summary_payload["artifact"] = "c15_replay_summary"
    summary_payload["ledger_path"] = str(
        LEDGER_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    summary_payload["ledger_sha256"] = ledger_sha
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2, sort_keys=True)
    summary_sha = compute_sha256(SUMMARY_PATH)

    sha_after = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    if sha_after != sha_before:
        raise RuntimeError("inputs_mutated_after_replay_artifact_write")

    report = {
        "ledger_path": str(LEDGER_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "ledger_sha256": ledger_sha,
        "summary_path": str(SUMMARY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "summary_sha256": summary_sha,
        "trade_count": n,
        "net_r_total_all_in": net_total,
        "gross_r_total_pre_cost": gross_total,
        "per_asset_net_r": dict(sorted(per_asset.items())),
        "per_regime_net_r": dict(sorted(per_regime.items())),
        "per_side_net_r": dict(sorted(per_side.items())),
        "forward_oos_net_r": forward_oos_net,
        "forward_oos_trade_count": len(fwd),
        "buy_and_hold_net_r_total": bh_total,
        "buy_and_hold_net_r_per_asset": bh_per_asset,
        "random_entry_mean_net_r": rand_mean,
        "random_entry_percentile_of_strategy": rand_pctl,
        "avg_hold_bars": avg_hold,
        "decisive_gate_results": gates,
        "all_decisive_gates_pass": all_gates_pass,
        "gross_only_would_pass": gross_only_would_pass,
        "structural_rejection_pressure": structural_rejection_pressure,
        "source_sha_stable": sha_before == sha_after,
    }
    for k, v in report.items():
        print("%s = %r" % (k, v))
    return report


if __name__ == "__main__":
    main()

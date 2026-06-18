"""C16 cointegration-pairs market-neutral real-candle labels one-off runner
(READ-ONLY against existing FROZEN local BTC/ETH/SOL 1d data; RESEARCH ONLY; NO
data fetch; NO relabel; NO replay; NO PnL; NO cost application; NO baseline; NO
robustness; NO portfolio compute; NO trading/broker/credentials/orders; NO
parameter fitting; NO paper/live readiness claim).

Builds the three pre-registered ratio-spread pairs (ETHBTC / SOLETH / SOLBTC) from
the SHA-pinned local daily candles (aligned on common dates), then applies the
FROZEN C16 detector logic in a ROLLING form (reusing the committed detector's pure
primitives): a rolling-OLS hedge ratio + spread residual, a rolling Engle-Granger
ADF cointegration gate (p <= 0.05), a rolling z-score, and the z-fade trade rules
(enter |z| >= 2.0, take |z| <= 0.5, z-band stop |z| >= 3.5, cointegration-break
invalidation exit). A LABEL is a market-neutral pair-trade ENTRY (dollar/beta-
neutral two legs, no naked directional leg); entries are non-overlapping per pair
by construction.

At the labels stage it runs the STRUCTURAL SAMPLE-SIZE GATE first (the C13 lesson):
>=100 accepted total, >=20 per pair, >=20 per regime, AND a POPULATED forward-OOS
2026 window -- failing it is a labels-stage structural rejection BEFORE any replay.
Regime is classified here ONLY for the labels-stage structural evidence (the BTC
SMA(50)/SMA(200) market regime), never as a trigger. NO replay, NO PnL, NO cost,
NO baseline are computed in this gate; those are reserved for the replay stage.
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

import sparta_commander.cointegration_pairs_market_neutral_v1_detector_spec_dry_run_contract as det  # noqa: E402,E501

CANDIDATE_ID = "COINTEGRATION_PAIRS_MARKET_NEUTRAL_V1"
CANDIDATE_FAMILY = "cointegration_pairs_market_neutral"
LEG_SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"

# pre-registered pairs (numerator / denominator)
PAIRS = (
    {"pair": "ETHBTC", "num": "ETHUSD", "den": "BTCUSD"},
    {"pair": "SOLETH", "num": "SOLUSD", "den": "ETHUSD"},
    {"pair": "SOLBTC", "num": "SOLUSD", "den": "BTCUSD"},
)

# frozen detector thresholds (reused, not redefined)
ENTRY_Z = det.ENTRY_Z          # 2.0
EXIT_Z = det.EXIT_Z            # 0.5
STOP_Z = det.STOP_Z            # 3.5
COINT_PVALUE_MAX = det.COINT_PVALUE_MAX   # 0.05
MAX_ABS_NET_BETA = det.MAX_ABS_NET_BETA   # 0.10

COINT_WINDOW = 180             # rolling cointegration / hedge window (days)
Z_LOOKBACK = 60               # rolling z-score lookback (days)

MIN_LABELS_TOTAL = 100
MIN_PER_PAIR = 20
MIN_PER_REGIME = 20
REGIME_SMA_SHORT = 50
REGIME_SMA_LONG = 200
FORWARD_OOS_START = "2026-01-01"

HEAD_AT_DETECTOR_DRY_RUN = "0c5f27a0e749f0842b99874b95d37f38f88a9887"

SOURCES = {s: REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / ("%s_1d.csv"
           % s.replace("USD", "")) for s in LEG_SYMBOLS}
EXPECTED_SHAS = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

OUT_DIR = (REPO_ROOT / "data" / "cointegration_pairs_market_neutral_c16"
           / "detector_labels")
LABELS_PATH = OUT_DIR / "c16_detector_labels.json"
SUMMARY_PATH = OUT_DIR / "c16_detector_summary.json"


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_rows(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["date"]] = float(r["close"])
    return out


def classify_regime(btc_dates, btc_closes, idx_by_date, date):
    """bull / bear / chop from BTC SMA(50)/SMA(200). Labels-stage only."""
    t = idx_by_date.get(date)
    if t is None or t < REGIME_SMA_LONG:
        return "chop"
    closes = btc_closes
    s_short = sum(closes[t - REGIME_SMA_SHORT + 1:t + 1]) / REGIME_SMA_SHORT
    s_long = sum(closes[t - REGIME_SMA_LONG + 1:t + 1]) / REGIME_SMA_LONG
    if closes[t] > s_long and s_short > s_long:
        return "bull"
    if closes[t] < s_long and s_short < s_long:
        return "bear"
    return "chop"


def rolling_pair_labels(num_closes, den_closes, dates):
    """Apply the FROZEN C16 detector rules in rolling form. Returns the list of
    ENTRY labels for the pair (non-overlapping by construction)."""
    n = len(dates)
    x = det._log(den_closes)
    y = det._log(num_closes)
    labels = []
    state = 0          # 0 flat, +1 long spread, -1 short spread
    warm = COINT_WINDOW
    for i in range(n):
        if i < warm:
            continue
        wx = x[i - COINT_WINDOW + 1:i + 1]
        wy = y[i - COINT_WINDOW + 1:i + 1]
        alpha, hedge = det._ols(wx, wy)
        resid_w = [wy[k] - alpha - hedge * wx[k] for k in range(len(wx))]
        pval = det._pseudo_pvalue(det._adf_tstat(resid_w))
        cointegrated = pval <= COINT_PVALUE_MAX
        zr = resid_w[-Z_LOOKBACK:]
        m = det._mean(zr); sd = det._std(zr)
        zi = ((resid_w[-1] - m) / sd) if sd > 0 else 0.0
        if state == 0:
            if cointegrated and abs(zi) >= ENTRY_Z:
                state = -1 if zi > 0 else 1
                dwx = [wx[k] - wx[k - 1] for k in range(1, len(wx))]
                dwy = [wy[k] - wy[k - 1] for k in range(1, len(wy))]
                _, beta_num_to_den = det._ols(dwx, dwy)
                net_beta = beta_num_to_den - hedge
                labels.append({
                    "setup_index": i, "date": dates[i],
                    "spread_side": "short" if state == -1 else "long",
                    "entry_z": round(zi, 4), "hedge_ratio": round(hedge, 6),
                    "coint_pvalue": pval, "net_beta": round(net_beta, 6),
                    "legs": [
                        {"leg": "numerator", "side": (-1 if state == -1 else 1)},
                        {"leg": "denominator", "side": (1 if state == -1 else -1)}],
                })
        else:
            if not cointegrated:
                state = 0          # cointegration-break invalidation exit
            elif abs(zi) >= STOP_Z:
                state = 0          # z-band stop
            elif abs(zi) <= EXIT_Z:
                state = 0          # reverted take
    return labels


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sha_before = {s: compute_sha256(SOURCES[s]) for s in LEG_SYMBOLS}
    if sha_before != EXPECTED_SHAS:
        raise RuntimeError("source_sha_pins_do_not_match_before_detection")

    close_by_date = {s: load_rows(SOURCES[s]) for s in LEG_SYMBOLS}

    # BTC regime index
    btc_dates = sorted(close_by_date["BTCUSD"].keys())
    btc_closes = [close_by_date["BTCUSD"][d] for d in btc_dates]
    btc_idx = {d: i for i, d in enumerate(btc_dates)}

    labels = []
    per_pair = {}
    per_regime = {}
    per_year = {}
    max_abs_net_beta = 0.0
    forward_oos_count = 0
    pair_windows = {}

    for p in PAIRS:
        num_map = close_by_date[p["num"]]
        den_map = close_by_date[p["den"]]
        common = sorted(set(num_map.keys()) & set(den_map.keys()))
        pair_windows[p["pair"]] = [common[0], common[-1]] if common else [None, None]
        num_closes = [num_map[d] for d in common]
        den_closes = [den_map[d] for d in common]
        pair_labels = rolling_pair_labels(num_closes, den_closes, common)
        for lab in pair_labels:
            d = lab["date"]
            regime = classify_regime(btc_dates, btc_closes, btc_idx, d)
            in_fwd = d >= FORWARD_OOS_START
            forward_oos_count += 1 if in_fwd else 0
            rec = dict(lab)
            rec["pair"] = p["pair"]
            rec["year"] = d[:4]
            rec["regime"] = regime
            rec["in_forward_oos_window"] = in_fwd
            labels.append(rec)
            per_pair[p["pair"]] = per_pair.get(p["pair"], 0) + 1
            per_regime[regime] = per_regime.get(regime, 0) + 1
            per_year[d[:4]] = per_year.get(d[:4], 0) + 1
            max_abs_net_beta = max(max_abs_net_beta, abs(lab["net_beta"]))

    labels.sort(key=lambda r: (r["pair"], r["setup_index"]))
    total = len(labels)
    pair_names = tuple(p["pair"] for p in PAIRS)

    sample_size = {
        "total": total, "min_total": MIN_LABELS_TOTAL,
        "total_ok": total >= MIN_LABELS_TOTAL,
        "per_pair": dict(sorted(per_pair.items())), "min_per_pair": MIN_PER_PAIR,
        "per_pair_ok": all(per_pair.get(p, 0) >= MIN_PER_PAIR for p in pair_names),
        "per_regime": dict(sorted(per_regime.items())),
        "min_per_regime": MIN_PER_REGIME,
        "per_regime_ok": all(per_regime.get(r, 0) >= MIN_PER_REGIME
                             for r in ("bull", "bear", "chop")),
        "forward_oos_label_count": forward_oos_count,
        "forward_oos_populated": forward_oos_count > 0,
    }
    sample_size["passed"] = (sample_size["total_ok"] and sample_size["per_pair_ok"]
                             and sample_size["per_regime_ok"]
                             and sample_size["forward_oos_populated"])
    net_beta_ok = max_abs_net_beta <= MAX_ABS_NET_BETA
    structural_rejection_pressure = not (sample_size["passed"] and net_beta_ok)

    sha_mid = {s: compute_sha256(SOURCES[s]) for s in LEG_SYMBOLS}
    if sha_mid != sha_before:
        raise RuntimeError("sources_mutated_during_detection")

    scope_locks = {
        "no_data_fetch": True, "no_replay": True, "no_pnl": True,
        "no_cost_application": True, "no_baseline_comparison_in_this_gate": True,
        "no_robustness": True, "no_portfolio_compute": True,
        "no_parameter_fitting": True, "no_paper_trading": True,
        "no_live_trading": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_data_mutation": True, "no_relabel": True,
        "no_naked_directional_leg": True, "no_directional_carry_shortcut": True,
        "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
        "no_downstream_gate_unlock": True, "no_staging": True,
        "no_commit": True, "no_push": True,
    }
    common_meta = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "leg_symbols": list(LEG_SYMBOLS), "timeframe": TIMEFRAME,
        "pair_universe": [p["pair"] for p in PAIRS],
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        "source_sha256_before": sha_before, "source_sha256_after": sha_mid,
        "sources_unchanged_during_detection": sha_mid == sha_before,
        "pair_windows": pair_windows,
        "cointegration_window_days": COINT_WINDOW,
        "zscore_lookback_days": Z_LOOKBACK,
        "entry_z": ENTRY_Z, "exit_z": EXIT_Z, "stop_z": STOP_Z,
        "cointegration_pvalue_max": COINT_PVALUE_MAX,
        "max_abs_net_beta_observed": round(max_abs_net_beta, 6),
        "max_abs_net_beta_cap": MAX_ABS_NET_BETA,
        "net_beta_within_cap": net_beta_ok,
        "label_definition": "market_neutral_pair_trade_entry_two_leg_non_overlapping",
        "labels_are_non_overlapping_by_construction": True,
        "accepted_label_count": total,
        "sample_size_requirements": sample_size,
        "structural_rejection_pressure": structural_rejection_pressure,
        "scope_locks": scope_locks,
        "honest_framing": (
            "real-candle market-neutral cointegration-pairs ENTRY labels over "
            "FROZEN local data; a label is a dollar/beta-neutral two-leg pair-trade "
            "entry gated by a rolling cointegration p<=0.05 test; cointegration in "
            "crypto is intermittent so labels may be FEW; the STRUCTURAL "
            "sample-size gate (>=100 / >=20 per pair / >=20 per regime + populated "
            "forward-OOS) AND a net-beta cap are checked BEFORE replay (the C13 "
            "lesson); NO replay; NO PnL; NO cost; NO baseline in this gate; not a "
            "profitability or paper/live-readiness claim"),
    }
    labels_payload = dict(common_meta)
    labels_payload["artifact"] = "c16_detector_labels"
    labels_payload["accepted_labels"] = labels
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels_payload, f, indent=2, sort_keys=True)
    labels_sha = compute_sha256(LABELS_PATH)

    summary_payload = dict(common_meta)
    summary_payload["artifact"] = "c16_detector_summary"
    summary_payload["per_year"] = dict(sorted(per_year.items()))
    summary_payload["labels_path"] = str(
        LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    summary_payload["labels_sha256"] = labels_sha
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2, sort_keys=True)
    summary_sha = compute_sha256(SUMMARY_PATH)

    sha_after = {s: compute_sha256(SOURCES[s]) for s in LEG_SYMBOLS}
    if sha_after != sha_before:
        raise RuntimeError("sources_mutated_after_artifact_write")

    report = {
        "labels_path": str(LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "labels_sha256": labels_sha,
        "summary_path": str(SUMMARY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "summary_sha256": summary_sha,
        "accepted_label_count": total,
        "per_pair": sample_size["per_pair"],
        "per_regime": sample_size["per_regime"],
        "per_year": dict(sorted(per_year.items())),
        "forward_oos_label_count": forward_oos_count,
        "forward_oos_populated": sample_size["forward_oos_populated"],
        "max_abs_net_beta_observed": round(max_abs_net_beta, 6),
        "net_beta_within_cap": net_beta_ok,
        "sample_size_passed": sample_size["passed"],
        "structural_rejection_pressure": structural_rejection_pressure,
        "source_sha_stable": sha_before == sha_after,
        "source_sha256": sha_before,
    }
    for k, v in report.items():
        print("%s = %r" % (k, v))
    return report


if __name__ == "__main__":
    main()

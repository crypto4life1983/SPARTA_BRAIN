"""C17 risk-adjusted portfolio-construction (vol-targeted / risk-parity) real-candle
ALLOCATION-LABELS one-off runner (READ-ONLY against existing FROZEN local
BTC/ETH/SOL 1d data; RESEARCH ONLY; NO data fetch; NO relabel; NO replay; NO
backtest; NO PnL; NO cost application; NO optimization; NO trading/broker/
credentials/orders; NO paper/live readiness claim).

This family is a CONTINUOUS ALLOCATOR, not an entry/exit signal: a "label" here is
one WEEKLY REBALANCE ALLOCATION OBSERVATION (the held long/flat weight vector plus
its diagnostics). It loads the SHA-pinned local daily candles (aligned on the common
date range), then applies the FROZEN C17 allocator (reusing the committed detector
dry-run's pure primitives: 30d realized-vol inverse-vol / equal-risk-contribution
weights, vol-target gross scaling capped at 1.0, weekly rebalance + no-trade band).

At the labels stage it runs the STRUCTURAL gate (the analog of the C13 sample-size
lesson for an allocator): a populated, well-formed allocation series -- enough
weekly rebalance observations, every weight long-only (no shorting), gross exposure
never above the 1.0 cap (no leverage), the vol-target actually scaling exposure, and
a POPULATED forward-OOS 2026 window. Average weekly turnover is measured against the
spec cap and REPORTED (not used to fabricate a pass). Regime (BTC SMA50/200) is
recorded ONLY for labels-stage structural evidence, never as a trigger. NO replay,
NO PnL, NO cost, NO baseline are computed in this gate -- those are reserved for the
fee-honest replay stage.
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

import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_detector_spec_dry_run_contract as det  # noqa: E402,E501

CANDIDATE_ID = "RISK_ADJUSTED_PORTFOLIO_CONSTRUCTION_VOL_TARGETED_ALLOCATION_V1"
CANDIDATE_FAMILY = "risk_adjusted_portfolio_construction_vol_targeted_allocation"
ASSETS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"

# frozen allocator params (reused, not redefined)
VOL_LOOKBACK = det.VOL_LOOKBACK
COV_LOOKBACK = det.COV_LOOKBACK
TARGET_VOL = det.TARGET_VOL
MAX_GROSS = det.MAX_GROSS
NO_TRADE_BAND = det.NO_TRADE_BAND
MAX_AVG_WEEKLY_TURNOVER = det.MAX_AVG_WEEKLY_TURNOVER

MIN_REBALANCES = 100
REGIME_SMA_SHORT = 50
REGIME_SMA_LONG = 200
FORWARD_OOS_START = "2026-01-01"

HEAD_AT_DETECTOR_DRY_RUN = "ff4168aa63bb377cc84b480948678843c32c7e0d"

SOURCES = {s: REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / ("%s_1d.csv"
           % s.replace("USD", "")) for s in ASSETS}
EXPECTED_SHAS = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

OUT_DIR = (REPO_ROOT / "data"
           / "risk_adjusted_portfolio_construction_vol_targeted_allocation_c17"
           / "allocation_labels")
LABELS_PATH = OUT_DIR / "c17_allocation_labels.json"
SUMMARY_PATH = OUT_DIR / "c17_allocation_summary.json"


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


def classify_regime(btc_closes, btc_idx, date):
    """bull / bear / chop from BTC SMA(50)/SMA(200). Labels-stage evidence only."""
    t = btc_idx.get(date)
    if t is None or t < REGIME_SMA_LONG:
        return "chop"
    s_short = sum(btc_closes[t - REGIME_SMA_SHORT + 1:t + 1]) / REGIME_SMA_SHORT
    s_long = sum(btc_closes[t - REGIME_SMA_LONG + 1:t + 1]) / REGIME_SMA_LONG
    if btc_closes[t] > s_long and s_short > s_long:
        return "bull"
    if btc_closes[t] < s_long and s_short < s_long:
        return "bear"
    return "chop"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sha_before = {s: compute_sha256(SOURCES[s]) for s in ASSETS}
    if sha_before != EXPECTED_SHAS:
        raise RuntimeError("source_sha_pins_do_not_match_before_detection")

    close_by_date = {s: load_rows(SOURCES[s]) for s in ASSETS}
    common = sorted(set(close_by_date["BTCUSD"])
                    & set(close_by_date["ETHUSD"])
                    & set(close_by_date["SOLUSD"]))
    closes = {s: [close_by_date[s][d] for d in common] for s in ASSETS}

    # BTC regime index over its own full series
    btc_dates = sorted(close_by_date["BTCUSD"])
    btc_closes = [close_by_date["BTCUSD"][d] for d in btc_dates]
    btc_idx = {d: i for i, d in enumerate(btc_dates)}

    out = det.allocate_c17(closes)
    checkpoints = out["checkpoints"]

    # a return-index i maps to candle date common[i + 1] (returns drop the first bar)
    labels = []
    per_regime = {}
    per_year = {}
    forward_oos_count = 0
    max_gross = 0.0
    min_gross = 1.0
    n_gross_capped = 0
    n_gross_scaled_down = 0
    all_long_only = True
    gross_never_exceeds_cap = True
    rc_ratios = []
    for c in checkpoints:
        di = c["index"] + 1
        date = common[di] if di < len(common) else common[-1]
        regime = classify_regime(btc_closes, btc_idx, date)
        in_fwd = date >= FORWARD_OOS_START
        forward_oos_count += 1 if in_fwd else 0
        g = c["gross_exposure"]
        max_gross = max(max_gross, g)
        min_gross = min(min_gross, g)
        if g > MAX_GROSS + 1e-9:
            gross_never_exceeds_cap = False
        if abs(g - MAX_GROSS) < 1e-9:
            n_gross_capped += 1
        if g < MAX_GROSS - 1e-6:
            n_gross_scaled_down += 1
        for w in c["weights"].values():
            if w < -1e-12:
                all_long_only = False
        rc = [v for v in c["risk_contributions"].values() if v > 0]
        if rc and min(rc) > 0:
            rc_ratios.append(max(rc) / min(rc))
        per_regime[regime] = per_regime.get(regime, 0) + 1
        per_year[date[:4]] = per_year.get(date[:4], 0) + 1
        labels.append({
            "rebalance_index": c["index"], "date": date, "regime": regime,
            "in_forward_oos_window": in_fwd,
            "weights": c["weights"], "gross_exposure": g,
            "executed": c["executed"], "is_initial": c["is_initial"],
            "turnover": c["turnover"], "port_vol_ann": c["port_vol_ann"],
            "vols": c["vols"], "risk_contributions": c["risk_contributions"],
        })

    n_rebalances = len(labels)
    non_initial = [lab for lab in labels if not lab["is_initial"]]
    avg_weekly_turnover = (sum(lab["turnover"] for lab in non_initial)
                           / len(non_initial)) if non_initial else 0.0
    n_executed = sum(1 for lab in labels if lab["executed"])
    n_skipped_by_band = sum(1 for lab in labels
                            if not lab["executed"] and not lab["is_initial"])
    avg_rc_ratio = (sum(rc_ratios) / len(rc_ratios)) if rc_ratios else 99.0

    structural = {
        "n_rebalances": n_rebalances, "min_rebalances": MIN_REBALANCES,
        "rebalances_ok": n_rebalances >= MIN_REBALANCES,
        "all_weights_long_only": all_long_only,
        "gross_never_exceeds_cap": gross_never_exceeds_cap,
        "max_gross_exposure": round(max_gross, 6),
        "min_gross_exposure": round(min_gross, 6),
        "vol_target_active": n_gross_scaled_down > 0,
        "n_gross_scaled_down": n_gross_scaled_down,
        "n_gross_capped_at_one": n_gross_capped,
        "per_regime": dict(sorted(per_regime.items())),
        "forward_oos_rebalance_count": forward_oos_count,
        "forward_oos_populated": forward_oos_count > 0,
        "avg_weekly_turnover": round(avg_weekly_turnover, 6),
        "max_avg_weekly_turnover_cap": MAX_AVG_WEEKLY_TURNOVER,
        "turnover_within_cap": avg_weekly_turnover <= MAX_AVG_WEEKLY_TURNOVER,
        "avg_risk_contribution_ratio": round(avg_rc_ratio, 6),
    }
    structural["passed"] = (
        structural["rebalances_ok"] and structural["all_weights_long_only"]
        and structural["gross_never_exceeds_cap"]
        and structural["vol_target_active"]
        and structural["forward_oos_populated"])

    sha_mid = {s: compute_sha256(SOURCES[s]) for s in ASSETS}
    if sha_mid != sha_before:
        raise RuntimeError("sources_mutated_during_detection")

    scope_locks = {
        "no_data_fetch": True, "no_replay": True, "no_backtest": True,
        "no_pnl": True, "no_cost_application": True, "no_baseline": True,
        "no_optimization": True, "no_robustness": True, "no_data_mutation": True,
        "no_relabel": True, "no_shorting": True, "no_leverage_above_cap": True,
        "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_auto_trading": True,
        "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
        "no_downstream_gate_unlock": True, "no_staging": True,
        "no_commit": True, "no_push": True,
    }
    common_meta = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "assets": list(ASSETS), "timeframe": TIMEFRAME,
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        "source_sha256_before": sha_before, "source_sha256_after": sha_mid,
        "sources_unchanged_during_detection": sha_mid == sha_before,
        "common_window": [common[0], common[-1]],
        "n_common_candles": len(common),
        "vol_lookback_days": VOL_LOOKBACK, "covariance_lookback_days": COV_LOOKBACK,
        "target_portfolio_vol_annualized": TARGET_VOL,
        "max_gross_exposure": MAX_GROSS, "no_trade_band_pct": NO_TRADE_BAND,
        "rebalance_cadence": "weekly",
        "label_definition": "weekly_rebalance_long_flat_allocation_observation",
        "n_rebalances": n_rebalances, "n_executed": n_executed,
        "n_skipped_by_band": n_skipped_by_band,
        "structural_review": structural,
        "structural_passed": structural["passed"],
        "scope_locks": scope_locks,
        "honest_framing": (
            "real-candle vol-targeted / risk-parity ALLOCATION labels over FROZEN "
            "local data; a label is one weekly long/flat rebalance weight vector; "
            "the labels-stage STRUCTURAL gate checks a well-formed, sufficiently "
            "sampled, long-only, gross-capped, vol-targeted allocation with a "
            "populated forward-OOS 2026 window; average weekly turnover is measured "
            "against the cap and reported; NO replay; NO PnL; NO cost; NO baseline "
            "in this gate; not a profitability or paper/live-readiness claim"),
    }
    labels_payload = dict(common_meta)
    labels_payload["artifact"] = "c17_allocation_labels"
    labels_payload["allocation_labels"] = labels
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels_payload, f, indent=2, sort_keys=True)
    labels_sha = compute_sha256(LABELS_PATH)

    summary_payload = dict(common_meta)
    summary_payload["artifact"] = "c17_allocation_summary"
    summary_payload["per_year"] = dict(sorted(per_year.items()))
    summary_payload["labels_path"] = str(
        LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    summary_payload["labels_sha256"] = labels_sha
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2, sort_keys=True)
    summary_sha = compute_sha256(SUMMARY_PATH)

    sha_after = {s: compute_sha256(SOURCES[s]) for s in ASSETS}
    if sha_after != sha_before:
        raise RuntimeError("sources_mutated_after_artifact_write")

    report = {
        "labels_path": str(LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "labels_sha256": labels_sha,
        "summary_path": str(SUMMARY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "summary_sha256": summary_sha,
        "n_common_candles": len(common),
        "common_window": [common[0], common[-1]],
        "n_rebalances": n_rebalances, "n_executed": n_executed,
        "n_skipped_by_band": n_skipped_by_band,
        "structural_review": structural,
        "structural_passed": structural["passed"],
        "source_sha_stable": sha_before == sha_after,
        "source_sha256": sha_before,
    }
    for k, v in report.items():
        print("%s = %r" % (k, v))
    return report


if __name__ == "__main__":
    main()

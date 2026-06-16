"""C11 cross-asset dispersion reversion real-candle detection / labels one-off
runner (READ-ONLY against existing FROZEN local BTC/ETH/SOL 1d data; RESEARCH
ONLY; NO data fetch; NO replay; NO PnL; NO robustness; NO portfolio compute; NO
trading / broker / credentials / orders; NO parameter fitting; NO best-asset
selection; NO paper/live readiness claim).

Runs the committed C11 detector (cross-asset dispersion reversion) over the
SHA-pinned local daily candles for BTCUSD / ETHUSD / SOLUSD, aligned on their
common dates, and freezes a deterministic, SHA-pinned detector-labels artifact +
summary under the gitignored data dir. At the labels stage it also evaluates the
EARLY GENERALIZATION BATTERY (the C10 lesson) -- cross-asset coverage,
cross-regime coverage, no weekday/calendar dependence, and a reserved forward-OOS
window for the later replay stage -- and the sample-size requirements. If the
minimum label/sample rules fail it records STRUCTURAL_REJECTION_PRESSURE.

No replay or PnL is computed in this gate. The detector itself reads no date and
no weekday; regime / weekday / year are classified here ONLY for the labels-stage
generalization evidence, never as a trigger.
"""
from __future__ import annotations

import csv
import datetime
import hashlib
import json
import statistics
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.cross_asset_dispersion_reversion_v1_detector_spec_dry_run_contract as det  # noqa: E402,E501

CANDIDATE_ID = "CROSS_ASSET_DISPERSION_REVERSION_V1"
CANDIDATE_FAMILY = "cross_asset_dispersion_reversion"
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"
DIRECTION = "long_only"

MIN_LABELS_TOTAL = 100
MIN_PER_ASSET = 20
MIN_PER_REGIME = 20
REGIME_SMA_SHORT = 50
REGIME_SMA_LONG = 200
MAX_WEEKDAY_SHARE = 0.25                 # no single weekday may exceed 25%
FORWARD_OOS_START = "2026-01-01"         # reserved for the replay stage

HEAD_AT_DETECTOR_DRY_RUN = "6e1efd2bb6082aef038b6d0de5578e0f0bdd4519"

SOURCES = {s: REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / ("%s_1d.csv"
           % s.replace("USD", "")) for s in SYMBOLS}
EXPECTED_SHAS = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

OUT_DIR = (REPO_ROOT / "data" / "cross_asset_dispersion_reversion_c11"
           / "detector_labels")
LABELS_PATH = OUT_DIR / "c11_detector_labels.json"
SUMMARY_PATH = OUT_DIR / "c11_detector_summary.json"


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


def _classify_regime(median: list, t: int) -> str:
    """bull / bear / chop from the basket-median SMA stack. Labels-stage
    classification only -- never a trigger."""
    if t < REGIME_SMA_LONG:
        return "chop"
    s_short = sum(median[t - REGIME_SMA_SHORT + 1:t + 1]) / REGIME_SMA_SHORT
    s_long = sum(median[t - REGIME_SMA_LONG + 1:t + 1]) / REGIME_SMA_LONG
    if median[t] > s_long and s_short > s_long:
        return "bull"
    if median[t] < s_long and s_short < s_long:
        return "bear"
    return "chop"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sha_before = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    if sha_before != EXPECTED_SHAS:
        raise RuntimeError("source_sha_pins_do_not_match_before_detection")

    rows = {s: load_rows(SOURCES[s]) for s in SYMBOLS}
    date_sets = [set(b["date"] for b in rows[s]) for s in SYMBOLS]
    common = sorted(set.intersection(*date_sets))
    if not common:
        raise RuntimeError("no_common_dates_across_assets")
    by_date = {s: {b["date"]: b for b in rows[s]} for s in SYMBOLS}
    aligned = {s: [by_date[s][d] for d in common] for s in SYMBOLS}

    setups = det.scan_c11_setups(aligned)
    accepted = [s for s in setups if s["status"] == "accepted_for_replay_review"]

    median = [statistics.median([aligned["BTCUSD"][i]["close"],
                                 aligned["ETHUSD"][i]["close"],
                                 aligned["SOLUSD"][i]["close"]])
              for i in range(len(common))]

    labels = []
    per_asset: dict = {}
    per_regime: dict = {}
    per_year: dict = {}
    weekday_counts: dict = {}
    forward_oos_count = 0
    for s in accepted:
        t = s["setup_index"]
        d = common[t]
        wd = datetime.date.fromisoformat(d).isoweekday()
        regime = _classify_regime(median, t)
        in_forward_oos = d >= FORWARD_OOS_START
        forward_oos_count += 1 if in_forward_oos else 0
        rec = dict(s)
        rec["date"] = d
        rec["year"] = d[:4]
        rec["iso_weekday"] = wd
        rec["regime"] = regime
        rec["in_forward_oos_window"] = in_forward_oos
        labels.append(rec)
        per_asset[s["laggard_symbol"]] = per_asset.get(s["laggard_symbol"], 0) + 1
        per_regime[regime] = per_regime.get(regime, 0) + 1
        per_year[d[:4]] = per_year.get(d[:4], 0) + 1
        weekday_counts[wd] = weekday_counts.get(wd, 0) + 1

    total = len(labels)
    # --- sample-size requirements ---
    sample_size = {
        "total": total, "min_total": MIN_LABELS_TOTAL,
        "total_ok": total >= MIN_LABELS_TOTAL,
        "per_asset": dict(sorted(per_asset.items())),
        "min_per_asset": MIN_PER_ASSET,
        "per_asset_ok": all(per_asset.get(s, 0) >= MIN_PER_ASSET
                            for s in SYMBOLS),
        "per_regime": dict(sorted(per_regime.items())),
        "min_per_regime": MIN_PER_REGIME,
        "per_regime_ok": all(per_regime.get(r, 0) >= MIN_PER_REGIME
                             for r in ("bull", "bear", "chop")),
    }
    sample_size["passed"] = (sample_size["total_ok"]
                             and sample_size["per_asset_ok"]
                             and sample_size["per_regime_ok"])

    # --- early generalization battery (labels stage) ---
    max_wd_share = (max(weekday_counts.values()) / total) if total else 1.0
    battery = {
        "cross_asset_coverage_ok": sample_size["per_asset_ok"]
        and len([s for s in SYMBOLS if per_asset.get(s, 0) > 0]) >= 3,
        "cross_regime_coverage_ok": sample_size["per_regime_ok"]
        and len([r for r in ("bull", "bear", "chop")
                 if per_regime.get(r, 0) > 0]) >= 3,
        "no_weekday_dependence_ok": len(weekday_counts) == 7
        and max_wd_share <= MAX_WEEKDAY_SHARE,
        "weekday_distribution": dict(sorted(weekday_counts.items())),
        "max_weekday_share": round(max_wd_share, 4),
        "forward_oos_window_prepared": {
            "forward_oos_start": FORWARD_OOS_START,
            "in_sample_label_count": total - forward_oos_count,
            "forward_oos_label_count": forward_oos_count,
            "prepared_for_replay_stage": True,
        },
    }
    battery["passed"] = (battery["cross_asset_coverage_ok"]
                         and battery["cross_regime_coverage_ok"]
                         and battery["no_weekday_dependence_ok"])

    structural_rejection_pressure = not (sample_size["passed"]
                                         and battery["passed"])

    sha_mid = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    if sha_mid != sha_before:
        raise RuntimeError("sources_mutated_during_detection")

    scope_locks = {
        "no_data_fetch": True, "no_replay": True, "no_pnl": True,
        "no_robustness": True, "no_generalization_run": True,
        "no_portfolio_compute": True, "no_paper_trading": True,
        "no_live_trading": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_parameter_fitting": True,
        "no_best_asset_selection": True, "no_weekday_or_calendar_trigger": True,
        "no_data_mutation": True, "no_profitability_claim": True,
        "no_paper_live_readiness_claim": True, "no_downstream_gate_unlock": True,
        "no_staging": True, "no_commit": True, "no_push": True,
    }
    common_meta = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME, "direction": DIRECTION,
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        "source_sha256_before": sha_before, "source_sha256_after": sha_mid,
        "sources_unchanged_during_detection": sha_mid == sha_before,
        "common_window": [common[0], common[-1]], "common_bar_count": len(common),
        "z_entry_threshold": det.Z_ENTRY_THRESHOLD,
        "dispersion_lookback_bars": det.DISPERSION_LOOKBACK_BARS,
        "basket_sma_length": det.BASKET_SMA_LENGTH,
        "atr_length": det.ATR_LENGTH,
        "structure_stop_atr_multiplier": det.STRUCTURE_STOP_ATR_MULTIPLIER,
        "target_distance_floor_bps": det.TARGET_DISTANCE_FLOOR_BPS,
        "accepted_label_count": total,
        "sample_size_requirements": sample_size,
        "early_generalization_battery": battery,
        "structural_rejection_pressure": structural_rejection_pressure,
        "relative_not_long_drift": True,
        "scope_locks": scope_locks,
        "honest_framing": (
            "real-candle cross-asset dispersion-reversion labels over FROZEN "
            "local data; relative/cross-sectional (not long-drift); no replay; "
            "no PnL; no parameter fitting; no best-asset selection; not a "
            "profitability or paper/live-readiness claim"),
    }
    labels_payload = dict(common_meta)
    labels_payload["artifact"] = "c11_detector_labels"
    labels_payload["accepted_labels"] = labels

    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels_payload, f, indent=2, sort_keys=True)
    labels_sha = compute_sha256(LABELS_PATH)
    summary_payload = dict(common_meta)
    summary_payload["artifact"] = "c11_detector_summary"
    summary_payload["per_year"] = dict(sorted(per_year.items()))
    summary_payload["labels_path"] = str(
        LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    summary_payload["labels_sha256"] = labels_sha
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2, sort_keys=True)
    summary_sha = compute_sha256(SUMMARY_PATH)

    sha_after = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    if sha_after != sha_before:
        raise RuntimeError("sources_mutated_after_artifact_write")

    report = {
        "labels_path": str(LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "labels_sha256": labels_sha,
        "summary_path": str(SUMMARY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "summary_sha256": summary_sha,
        "accepted_label_count": total,
        "per_asset": sample_size["per_asset"],
        "per_regime": sample_size["per_regime"],
        "sample_size_passed": sample_size["passed"],
        "early_generalization_battery_passed": battery["passed"],
        "structural_rejection_pressure": structural_rejection_pressure,
        "source_sha_stable": sha_before == sha_after,
    }
    for k, v in report.items():
        print("%s = %r" % (k, v))
    return report


if __name__ == "__main__":
    main()

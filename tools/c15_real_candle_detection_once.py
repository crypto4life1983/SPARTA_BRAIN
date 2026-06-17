"""C15 slow vol-targeted time-series momentum real-candle labels one-off runner
(READ-ONLY against existing FROZEN local BTC/ETH/SOL 1d data; RESEARCH ONLY; NO
data fetch; NO relabel; NO replay; NO PnL; NO cost application; NO baseline
comparison; NO robustness; NO portfolio compute; NO trading / broker /
credentials / orders; NO parameter fitting; NO paper/live readiness claim).

Runs the committed C15 detector (slow vol-targeted time-series momentum) PER ASSET
over the SHA-pinned local daily candles for BTCUSD / ETHUSD / SOLUSD and extracts
the ENTRY-EVENT labels: a label is a bar where the detector state TRANSITIONS into
an active position (long/short) from a different state (flat / warmup / the
opposite side). Entries are naturally non-overlapping (a new position requires
first leaving the prior state), so no horizon walk and no PnL is computed -- it
stays inside the labels gate.

At the labels stage it runs the STRUCTURAL SAMPLE-SIZE GATE first (the C13
lesson): >=100 accepted total, >=20 per asset, >=20 per regime, AND a POPULATED
forward-OOS 2026 window -- failing it is a labels-stage structural rejection
BEFORE any replay. Regime / year are classified here ONLY for the labels-stage
structural evidence (the asset's own SMA(50)/SMA(200) stack), never as a trigger.
NO replay, NO PnL, NO cost application, and NO baseline comparison are computed in
this gate; those are reserved for the replay stage.
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
DIRECTION = "long_short_symmetric"

MIN_LABELS_TOTAL = 100
MIN_PER_ASSET = 20
MIN_PER_REGIME = 20
REGIME_SMA_SHORT = 50
REGIME_SMA_LONG = 200
FORWARD_OOS_START = "2026-01-01"         # reserved for the replay stage

HEAD_AT_DETECTOR_DRY_RUN = "5399925b1cb60260b5ed750b6ce3b5765e584a0b"

SOURCES = {s: REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / ("%s_1d.csv"
           % s.replace("USD", "")) for s in SYMBOLS}
EXPECTED_SHAS = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

OUT_DIR = (REPO_ROOT / "data" / "slow_vol_targeted_time_series_momentum_c15"
           / "detector_labels")
LABELS_PATH = OUT_DIR / "c15_detector_labels.json"
SUMMARY_PATH = OUT_DIR / "c15_detector_summary.json"

ACTIVE = ("long", "short")


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


def extract_entry_labels(states):
    """A label = a bar whose state TRANSITIONS into an active position from a
    different state. Entries are inherently non-overlapping. No PnL, no horizon
    walk."""
    entries = []
    prev = None
    for s in states:
        st = s["state"]
        if st in ACTIVE and st != prev:
            entries.append(s)
        prev = st
    return entries


def classify_regime(closes: list, t: int) -> str:
    """bull / bear / chop from the asset's OWN SMA(50)/SMA(200) stack.
    Labels-stage classification only -- never a trigger."""
    if t < REGIME_SMA_LONG:
        return "chop"
    s_short = sum(closes[t - REGIME_SMA_SHORT + 1:t + 1]) / REGIME_SMA_SHORT
    s_long = sum(closes[t - REGIME_SMA_LONG + 1:t + 1]) / REGIME_SMA_LONG
    if closes[t] > s_long and s_short > s_long:
        return "bull"
    if closes[t] < s_long and s_short < s_long:
        return "bear"
    return "chop"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sha_before = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    if sha_before != EXPECTED_SHAS:
        raise RuntimeError("source_sha_pins_do_not_match_before_detection")

    rows = {s: load_rows(SOURCES[s]) for s in SYMBOLS}

    labels = []
    per_asset: dict = {}
    per_regime: dict = {}
    per_year: dict = {}
    per_side: dict = {}
    forward_oos_count = 0
    asset_windows = {}

    for s in SYMBOLS:
        bars = rows[s]
        closes = [b["close"] for b in bars]
        asset_windows[s] = [bars[0]["date"], bars[-1]["date"]]
        states = det.scan_c15_states(bars)
        entries = extract_entry_labels(states)
        for st in entries:
            t = st["i"]
            d = bars[t]["date"]
            regime = classify_regime(closes, t)
            in_fwd = d >= FORWARD_OOS_START
            forward_oos_count += 1 if in_fwd else 0
            rec = {
                "symbol": s, "setup_index": t, "date": d, "year": d[:4],
                "state": st["state"], "position_scale": st["position_scale"],
                "momentum": st["momentum"], "realized_vol": st["realized_vol"],
                "detector_w1_regime": st["w1_regime"],
                "labels_stage_regime": regime,
                "in_forward_oos_window": in_fwd,
            }
            labels.append(rec)
            per_asset[s] = per_asset.get(s, 0) + 1
            per_regime[regime] = per_regime.get(regime, 0) + 1
            per_year[d[:4]] = per_year.get(d[:4], 0) + 1
            per_side[st["state"]] = per_side.get(st["state"], 0) + 1

    labels.sort(key=lambda r: (r["symbol"], r["setup_index"]))
    total = len(labels)

    # --- STRUCTURAL sample-size gate (the C13 lesson; BEFORE replay) ---
    sample_size = {
        "total": total, "min_total": MIN_LABELS_TOTAL,
        "total_ok": total >= MIN_LABELS_TOTAL,
        "per_asset": dict(sorted(per_asset.items())),
        "min_per_asset": MIN_PER_ASSET,
        "per_asset_ok": all(per_asset.get(s, 0) >= MIN_PER_ASSET for s in SYMBOLS),
        "per_regime": dict(sorted(per_regime.items())),
        "min_per_regime": MIN_PER_REGIME,
        "per_regime_ok": all(per_regime.get(r, 0) >= MIN_PER_REGIME
                             for r in ("bull", "bear", "chop")),
        "forward_oos_label_count": forward_oos_count,
        "forward_oos_populated": forward_oos_count > 0,
    }
    sample_size["passed"] = (sample_size["total_ok"]
                             and sample_size["per_asset_ok"]
                             and sample_size["per_regime_ok"]
                             and sample_size["forward_oos_populated"])
    structural_rejection_pressure = not sample_size["passed"]

    sha_mid = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    if sha_mid != sha_before:
        raise RuntimeError("sources_mutated_during_detection")

    scope_locks = {
        "no_data_fetch": True, "no_replay": True, "no_pnl": True,
        "no_cost_application": True, "no_baseline_comparison_in_this_gate": True,
        "no_robustness": True, "no_generalization_run": True,
        "no_portfolio_compute": True, "no_paper_trading": True,
        "no_live_trading": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_parameter_fitting": True,
        "no_data_mutation": True, "no_relabel": True,
        "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
        "no_downstream_gate_unlock": True, "no_staging": True,
        "no_commit": True, "no_push": True,
    }
    common_meta = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbols": list(SYMBOLS), "timeframe": TIMEFRAME, "direction": DIRECTION,
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        "source_sha256_before": sha_before, "source_sha256_after": sha_mid,
        "sources_unchanged_during_detection": sha_mid == sha_before,
        "asset_windows": asset_windows,
        "spec_params": dict(det.SPEC_PARAMS),
        "all_in_round_trip_bps_reserved": det.ALL_IN_ROUND_TRIP_BPS,
        "label_definition": "state_transition_into_active_position_entry_event",
        "labels_are_non_overlapping_by_construction": True,
        "accepted_label_count": total,
        "per_side": dict(sorted(per_side.items())),
        "sample_size_requirements": sample_size,
        "structural_rejection_pressure": structural_rejection_pressure,
        "scope_locks": scope_locks,
        "honest_framing": (
            "real-candle slow vol-targeted time-series momentum ENTRY labels over "
            "FROZEN local data; a label is a position-initiation transition (long/"
            "short), not a fixed-horizon setup; slow TSMOM produces FEW entries by "
            "design, so the STRUCTURAL sample-size gate (>=100 / >=20 per asset / "
            ">=20 per regime + populated forward-OOS) is run BEFORE replay (the C13 "
            "lesson); NO replay; NO PnL; NO cost application; NO baseline "
            "comparison in this gate; not a profitability or paper/live-readiness "
            "claim"),
    }
    labels_payload = dict(common_meta)
    labels_payload["artifact"] = "c15_detector_labels"
    labels_payload["accepted_labels"] = labels

    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels_payload, f, indent=2, sort_keys=True)
    labels_sha = compute_sha256(LABELS_PATH)
    summary_payload = dict(common_meta)
    summary_payload["artifact"] = "c15_detector_summary"
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
        "per_side": dict(sorted(per_side.items())),
        "per_year": dict(sorted(per_year.items())),
        "forward_oos_label_count": forward_oos_count,
        "forward_oos_populated": sample_size["forward_oos_populated"],
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

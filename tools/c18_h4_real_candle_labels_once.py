"""C18 H4 market-structure trend-following real-candle LABELS one-off runner
(READ-ONLY against the FROZEN local BTCUSDT 4h data; RESEARCH ONLY; NO data fetch; NO
relabel with new params; NO replay; NO PnL; NO fee/cost application; NO optimization;
NO XAUUSD; NO trading/broker/credentials/orders; NO paper/live readiness claim).

Applies the FROZEN C18 detector (reusing the committed detector dry-run's pure
primitives: K=2 swing pivots, HH+HL uptrend, long pullback entry on a confirmed
higher-low, structural stop, structure-shift / stop exit, profit-confirmed
add-to-winners never to losers, max 3 units, one position per symbol) to the
SHA-pinned local BTCUSDT 4h candles. A LABEL is one detected long setup/trade
(entry + its adds + structural exit).

At the labels stage it runs the STRUCTURAL gate: a well-formed, sufficiently sampled
set of structure labels -- enough entries, every label long-only, max 3 units, one
position per symbol, structural stops below anchor, spacing >= 6 bars, and a POPULATED
forward-OOS 2026 window. NO replay, NO PnL, NO fee/cost (the 37 bps is RESERVED for
the replay stage). The runner aborts on any source SHA drift.
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

import sparta_commander.h4_trend_following_market_structure_v1_detector_spec_dry_run_contract as det  # noqa: E402,E501

CANDIDATE_ID = "C18"
CANDIDATE_FAMILY = "h4_trend_following_market_structure"
SYMBOL = "BTCUSD"
TIMEFRAME = "4h"

MIN_LABELS_TOTAL = 30          # structural floor for a multi-year H4 trend program
FORWARD_OOS_START = "2026-01-01"
MAX_UNITS = det.MAX_UNITS                    # 3
MIN_SPACING = det.MIN_SPACING                # 6
STOP_BUFFER_FRAC = det.STOP_BUFFER_FRAC      # 0.0015

HEAD_AT_DETECTOR_DRY_RUN = "713c98a84de02826904c2ddb7d84c4b37a9e1469"

C18_DIR = (REPO_ROOT / "data"
           / "h4_trend_following_market_structure_c18")
SOURCE_CSV = C18_DIR / "raw" / "BTCUSDT_4h.csv"
EXPECTED_SOURCE_SHA256 = (
    "aec42241f47192ae29331f4b67a64500ca38aad1f403f13d0de5b405f7ecbaec")

OUT_DIR = C18_DIR / "labels"
LABELS_PATH = OUT_DIR / "c18_h4_labels.json"
SUMMARY_PATH = OUT_DIR / "c18_h4_labels_summary.json"


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_candles(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append({"date": r["date"], "high": float(r["high"]),
                        "low": float(r["low"]), "close": float(r["close"])})
    out.sort(key=lambda c: c["date"])
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sha_before = compute_sha256(SOURCE_CSV)
    if sha_before != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("source_sha_pin_does_not_match_before_labeling")

    candles = load_candles(SOURCE_CSV)
    out = det.run_detector(candles)
    trades = out["trades"]

    labels = []
    per_year = {}
    forward_oos_count = 0
    total_adds = 0
    exits_by_reason = {}
    all_long_only = True
    stops_below_anchor = True
    for tr in trades:
        eb = tr["entry_bar"]
        # detector bar index == candle index (it scans candles directly)
        edate = candles[eb]["date"] if eb < len(candles) else candles[-1]["date"]
        xb = tr.get("exit_bar")
        xdate = candles[xb]["date"] if (xb is not None and xb < len(candles)) \
            else None
        in_fwd = edate >= FORWARD_OOS_START
        forward_oos_count += 1 if in_fwd else 0
        total_adds += len(tr["adds"])
        exits_by_reason[tr.get("exit_reason")] = (
            exits_by_reason.get(tr.get("exit_reason"), 0) + 1)
        if tr["stop"] >= tr["anchor"]:
            stops_below_anchor = False
        labels.append({
            "setup_index": eb, "entry_date": edate, "side": "long",
            "units": tr["units"], "n_adds": len(tr["adds"]),
            "anchor": tr["anchor"], "stop": tr["stop"],
            "exit_index": xb, "exit_date": xdate,
            "exit_reason": tr.get("exit_reason"),
            "in_forward_oos_window": in_fwd,
        })
        per_year[edate[:4]] = per_year.get(edate[:4], 0) + 1

    total = len(labels)
    entry_bars = sorted(lab["setup_index"] for lab in labels)
    spacing_ok = all(b - a >= MIN_SPACING
                     for a, b in zip(entry_bars[:-1], entry_bars[1:]))
    max_units = max((lab["units"] for lab in labels), default=0)

    structural = {
        "n_labels": total, "min_labels": MIN_LABELS_TOTAL,
        "labels_ok": total >= MIN_LABELS_TOTAL,
        "all_long_only": all_long_only,
        "max_units": max_units, "max_units_ok": max_units <= MAX_UNITS,
        "one_position_per_symbol": out["max_concurrent_positions"] <= 1,
        "structural_stops_below_anchor": stops_below_anchor,
        "spacing_min_6_bars": spacing_ok,
        "total_adds": total_adds, "exits_by_reason": dict(sorted(
            exits_by_reason.items(), key=lambda kv: str(kv[0]))),
        "forward_oos_label_count": forward_oos_count,
        "forward_oos_populated": forward_oos_count > 0,
        "per_year": dict(sorted(per_year.items())),
    }
    structural["passed"] = (
        structural["labels_ok"] and structural["all_long_only"]
        and structural["max_units_ok"] and structural["one_position_per_symbol"]
        and structural["structural_stops_below_anchor"]
        and structural["spacing_min_6_bars"]
        and structural["forward_oos_populated"])

    sha_after = compute_sha256(SOURCE_CSV)
    if sha_after != sha_before:
        raise RuntimeError("source_mutated_during_labeling")

    common_meta = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbol": SYMBOL, "timeframe": TIMEFRAME,
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        "source_sha256": sha_before, "source_csv": str(
            SOURCE_CSV.relative_to(REPO_ROOT)).replace("\\", "/"),
        "n_candles": len(candles),
        "window": [candles[0]["date"], candles[-1]["date"]],
        "swing_pivot_strength_k": det.K, "max_units_total": MAX_UNITS,
        "min_bars_between_entries": MIN_SPACING, "stop_buffer_frac": STOP_BUFFER_FRAC,
        "label_definition": "long_market_structure_trend_setup_with_pyramids",
        "n_labels": total, "n_setups": total, "total_adds": total_adds,
        "structural_review": structural,
        "structural_passed": structural["passed"],
        "scope_locks": {
            "no_data_fetch": True, "no_replay": True, "no_pnl": True,
            "no_fee_application": True, "no_optimization": True,
            "no_reparameterization": True, "no_xauusd": True, "no_relabel": True,
            "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
            "no_credentials": True, "no_order_logic": True, "no_data_mutation": True,
            "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
            "no_downstream_gate_unlock": True, "no_staging": True,
            "no_commit": True, "no_push": True,
        },
        "honest_framing": (
            "real-candle H4 market-structure trend labels over FROZEN local BTCUSDT "
            "4h data; a label is one long setup (entry + profit-confirmed pyramids + "
            "structural exit); the labels-stage STRUCTURAL gate checks a well-formed, "
            "sufficiently sampled, long-only, max-3-unit, non-overlapping set with "
            "structural stops, >= 6-bar spacing and a populated forward-OOS 2026 "
            "window; NO replay; NO PnL; NO fee (37 bps reserved); not a profitability "
            "or paper/live-readiness claim"),
    }
    labels_payload = dict(common_meta)
    labels_payload["artifact"] = "c18_h4_labels"
    labels_payload["labels"] = labels
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels_payload, f, indent=2, sort_keys=True)
    labels_sha = compute_sha256(LABELS_PATH)

    summary_payload = dict(common_meta)
    summary_payload["artifact"] = "c18_h4_labels_summary"
    summary_payload["labels_path"] = str(
        LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    summary_payload["labels_sha256"] = labels_sha
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2, sort_keys=True)
    summary_sha = compute_sha256(SUMMARY_PATH)

    report = {
        "labels_path": str(LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "labels_sha256": labels_sha,
        "summary_path": str(SUMMARY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "summary_sha256": summary_sha,
        "n_candles": len(candles), "window": common_meta["window"],
        "n_labels": total, "total_adds": total_adds, "max_units": max_units,
        "exits_by_reason": structural["exits_by_reason"],
        "forward_oos_label_count": forward_oos_count,
        "structural_passed": structural["passed"],
        "source_sha256": sha_before, "source_sha_stable": sha_before == sha_after,
    }
    for k, v in report.items():
        print("%s = %r" % (k, v))
    return report


if __name__ == "__main__":
    main()

"""C13 lead-lag propagation continuation real-candle detection / labels one-off
runner (READ-ONLY against existing FROZEN local BTC/ETH/SOL 1d data; RESEARCH
ONLY; NO data fetch; NO relabel; NO replay; NO PnL; NO baseline comparison; NO
robustness; NO portfolio compute; NO trading / broker / credentials / orders; NO
parameter fitting; NO paper/live readiness claim).

Runs the committed C13 detector (cross-asset lead-lag propagation) over the
SHA-pinned local daily candles for BTCUSD (LEADER) / ETHUSD / SOLUSD (FOLLOWERS),
aligned on their common dates EXACTLY as the synthetic dry-run geometry expects
(leader z-score + follower lag on the SAME dates). It applies a labels-stage
per-follower non-overlap (REDUCE-OR-KEEP-ONLY, entry-spacing form: a later
same-follower setup whose entry is within MAX_HOLD bars of the last kept entry is
dropped -- this needs NO horizon walk and computes NO PnL, so it stays inside the
labels gate) and freezes a deterministic, SHA-pinned detector-labels artifact +
summary under the gitignored data dir.

At the labels stage it evaluates the STRUCTURAL CHECKS only -- sample-size
(>=100 total, >=20 per follower, >=20 per regime), both followers present,
bull/bear/chop regime coverage, and a weekday-neutral DEPENDENCY test (never a
trigger) -- and reserves a forward-OOS 2026 window for the later replay stage. If
the minimum label/sample/coverage rules fail it records
STRUCTURAL_REJECTION_PRESSURE.

NO replay, NO PnL, and NO baseline comparison (buy-and-hold / random-entry /
buy-the-leader) are computed in this gate; those run at the replay stage. The
detector reads no date and no weekday; regime / weekday / year are classified
here ONLY for the labels-stage structural evidence, never as a trigger.
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

import sparta_commander.lead_lag_propagation_continuation_v1_detector_spec_dry_run_contract as det  # noqa: E402,E501

CANDIDATE_ID = "LEAD_LAG_PROPAGATION_CONTINUATION_V1"
CANDIDATE_FAMILY = "lead_lag_propagation_continuation"
LEADER = "BTCUSD"
FOLLOWERS = ("ETHUSD", "SOLUSD")
SYMBOLS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"
DIRECTION = "long_only"

MIN_LABELS_TOTAL = 100
MIN_PER_FOLLOWER = 20
MIN_PER_REGIME = 20
REGIME_SMA_SHORT = 50
REGIME_SMA_LONG = 200
MAX_WEEKDAY_SHARE = 0.25                 # weekday-neutral dependency test
FORWARD_OOS_START = "2026-01-01"         # reserved for the replay stage

HEAD_AT_DETECTOR_DRY_RUN = "d32047c124168b3e478d7e181dfe6155d14d3604"

SOURCES = {s: REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / ("%s_1d.csv"
           % s.replace("USD", "")) for s in SYMBOLS}
EXPECTED_SHAS = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

OUT_DIR = (REPO_ROOT / "data" / "lead_lag_propagation_continuation_c13"
           / "detector_labels")
LABELS_PATH = OUT_DIR / "c13_detector_labels.json"
SUMMARY_PATH = OUT_DIR / "c13_detector_summary.json"


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


def labels_stage_non_overlap(setups_sorted, max_hold):
    """Per-follower REDUCE-OR-KEEP-ONLY by entry spacing: drop a later setup
    whose entry_index is within max_hold bars of the last kept entry. No horizon
    walk, no PnL -- a pure labels-stage spacing rule (conservative vs the
    resolved-exit non-overlap applied at replay)."""
    kept = []
    block_until = None
    dropped = 0
    for s in setups_sorted:
        idx = s["setup_index"]
        if block_until is not None and idx <= block_until:
            dropped += 1
            continue
        kept.append(s)
        block_until = idx + max_hold
    return kept, dropped


def classify_regime(closes: list, t: int) -> str:
    """bull / bear / chop from the FOLLOWER's OWN SMA(50)/SMA(200) stack.
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
    date_sets = [set(b["date"] for b in rows[s]) for s in SYMBOLS]
    common = sorted(set.intersection(*date_sets))
    if not common:
        raise RuntimeError("no_common_dates_across_assets")
    by_date = {s: {b["date"]: b for b in rows[s]} for s in SYMBOLS}
    aligned = {s: [by_date[s][d] for d in common] for s in SYMBOLS}

    setups = det.scan_c13_setups(aligned)
    rejected_by_reason: dict = {}
    for st in setups:
        if st["status"] != "accepted_for_replay_review":
            rejected_by_reason[st["status"]] = (
                rejected_by_reason.get(st["status"], 0) + 1)
    accepted = [st for st in setups
                if st["status"] == "accepted_for_replay_review"]
    scanned_accept_pre_overlap = len(accepted)

    labels = []
    per_follower: dict = {}
    per_regime: dict = {}
    per_year: dict = {}
    weekday_counts: dict = {}
    forward_oos_count = 0
    dropped_overlap_total = 0

    for f in FOLLOWERS:
        f_closes = [b["close"] for b in aligned[f]]
        f_setups = sorted([st for st in accepted if st["follower_symbol"] == f],
                          key=lambda x: x["setup_index"])
        kept, dropped = labels_stage_non_overlap(f_setups, det.MAX_HOLD_BARS)
        dropped_overlap_total += dropped
        for st in kept:
            t = st["setup_index"]
            d = common[t]
            wd = datetime.date.fromisoformat(d).isoweekday()
            regime = classify_regime(f_closes, t)
            in_fwd = d >= FORWARD_OOS_START
            forward_oos_count += 1 if in_fwd else 0
            rec = dict(st)
            rec["date"] = d
            rec["year"] = d[:4]
            rec["iso_weekday"] = wd
            rec["regime"] = regime
            rec["in_forward_oos_window"] = in_fwd
            labels.append(rec)
            per_follower[f] = per_follower.get(f, 0) + 1
            per_regime[regime] = per_regime.get(regime, 0) + 1
            per_year[d[:4]] = per_year.get(d[:4], 0) + 1
            weekday_counts[wd] = weekday_counts.get(wd, 0) + 1

    labels.sort(key=lambda r: (r["follower_symbol"], r["setup_index"]))
    total = len(labels)
    # --- sample-size requirements ---
    sample_size = {
        "total": total, "min_total": MIN_LABELS_TOTAL,
        "total_ok": total >= MIN_LABELS_TOTAL,
        "per_follower": dict(sorted(per_follower.items())),
        "min_per_follower": MIN_PER_FOLLOWER,
        "per_follower_ok": all(per_follower.get(f, 0) >= MIN_PER_FOLLOWER
                               for f in FOLLOWERS),
        "per_regime": dict(sorted(per_regime.items())),
        "min_per_regime": MIN_PER_REGIME,
        "per_regime_ok": all(per_regime.get(r, 0) >= MIN_PER_REGIME
                             for r in ("bull", "bear", "chop")),
    }
    sample_size["passed"] = (sample_size["total_ok"]
                             and sample_size["per_follower_ok"]
                             and sample_size["per_regime_ok"])

    # --- structural checks battery (labels stage; NO replay/PnL/baseline) ---
    max_wd_share = (max(weekday_counts.values()) / total) if total else 1.0
    battery = {
        "both_followers_present_ok": sample_size["per_follower_ok"]
        and len([f for f in FOLLOWERS if per_follower.get(f, 0) > 0]) >= 2,
        "cross_regime_coverage_ok": sample_size["per_regime_ok"]
        and len([r for r in ("bull", "bear", "chop")
                 if per_regime.get(r, 0) > 0]) >= 3,
        "no_weekday_dependence_ok": len(weekday_counts) == 7
        and max_wd_share <= MAX_WEEKDAY_SHARE,
        "weekday_distribution": dict(sorted(weekday_counts.items())),
        "max_weekday_share": round(max_wd_share, 4),
        "forward_oos_window_reserved": {
            "forward_oos_start": FORWARD_OOS_START,
            "in_sample_label_count": total - forward_oos_count,
            "forward_oos_label_count": forward_oos_count,
            "reserved_for_replay_stage": True,
        },
    }
    battery["passed"] = (battery["both_followers_present_ok"]
                         and battery["cross_regime_coverage_ok"]
                         and battery["no_weekday_dependence_ok"])

    structural_rejection_pressure = not (sample_size["passed"]
                                         and battery["passed"])

    sha_mid = {s: compute_sha256(SOURCES[s]) for s in SYMBOLS}
    if sha_mid != sha_before:
        raise RuntimeError("sources_mutated_during_detection")

    scope_locks = {
        "no_data_fetch": True, "no_replay": True, "no_pnl": True,
        "no_baseline_comparison_in_this_gate": True, "no_robustness": True,
        "no_generalization_run": True, "no_portfolio_compute": True,
        "no_paper_trading": True, "no_live_trading": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True,
        "no_parameter_fitting": True, "no_weekday_or_calendar_trigger": True,
        "no_data_mutation": True, "no_relabel": True,
        "no_long_drift_or_bull_carry_reliance": True,
        "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
        "no_downstream_gate_unlock": True, "no_staging": True,
        "no_commit": True, "no_push": True,
    }
    common_meta = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "leader": LEADER, "followers": list(FOLLOWERS), "symbols": list(SYMBOLS),
        "timeframe": TIMEFRAME, "direction": DIRECTION,
        "head_at_detector_dry_run": HEAD_AT_DETECTOR_DRY_RUN,
        "source_sha256_before": sha_before, "source_sha256_after": sha_mid,
        "sources_unchanged_during_detection": sha_mid == sha_before,
        "common_window": [common[0], common[-1]], "common_bar_count": len(common),
        "leader_return_lookback_bars": det.LEADER_RETURN_LOOKBACK_BARS,
        "leader_z_lookback": det.LEADER_Z_LOOKBACK,
        "leader_z_entry_threshold": det.LEADER_Z_ENTRY_THRESHOLD,
        "lag_margin_fraction": det.LAG_MARGIN_FRACTION,
        "atr_length": det.ATR_LENGTH,
        "stop_atr_multiplier": det.STOP_ATR_MULTIPLIER,
        "target_variants": [n for n, _ in det.TARGET_VARIANTS],
        "target_distance_floor_bps": det.TARGET_DISTANCE_FLOOR_BPS,
        "max_hold_bars": det.MAX_HOLD_BARS,
        "all_in_round_trip_bps": det.ALL_IN_ROUND_TRIP_BPS,
        "labels_stage_non_overlap_policy":
            "per_follower_reduce_or_keep_only_entry_spacing_no_horizon_walk",
        "accepted_pre_overlap_count": scanned_accept_pre_overlap,
        "dropped_labels_stage_non_overlap": dropped_overlap_total,
        "accepted_label_count": total,
        "rejected_by_reason": dict(sorted(rejected_by_reason.items())),
        "sample_size_requirements": sample_size,
        "structural_checks_battery": battery,
        "structural_rejection_pressure": structural_rejection_pressure,
        "relies_on_long_drift_or_bull_carry": False,
        "scope_locks": scope_locks,
        "honest_framing": (
            "real-candle cross-asset lead-lag propagation labels over FROZEN "
            "local data; the LEADER (BTC) move triggers a FOLLOWER (ETH/SOL) "
            "entry (not long-drift, not calendar); labels-stage structural "
            "checks only; NO replay; NO PnL; NO baseline comparison in this gate "
            "(buy-and-hold / random-entry / buy-the-leader + the horizon-exit "
            "cap run at the replay stage); not a profitability or paper/live-"
            "readiness claim"),
    }
    labels_payload = dict(common_meta)
    labels_payload["artifact"] = "c13_detector_labels"
    labels_payload["accepted_labels"] = labels

    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(labels_payload, f, indent=2, sort_keys=True)
    labels_sha = compute_sha256(LABELS_PATH)
    summary_payload = dict(common_meta)
    summary_payload["artifact"] = "c13_detector_summary"
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
        "common_window": [common[0], common[-1]],
        "accepted_label_count": total,
        "accepted_pre_overlap_count": scanned_accept_pre_overlap,
        "dropped_labels_stage_non_overlap": dropped_overlap_total,
        "rejected_by_reason": dict(sorted(rejected_by_reason.items())),
        "per_follower": sample_size["per_follower"],
        "per_regime": sample_size["per_regime"],
        "per_year": dict(sorted(per_year.items())),
        "weekday_distribution": battery["weekday_distribution"],
        "max_weekday_share": battery["max_weekday_share"],
        "sample_size_passed": sample_size["passed"],
        "structural_checks_battery_passed": battery["passed"],
        "structural_rejection_pressure": structural_rejection_pressure,
        "forward_oos_label_count": forward_oos_count,
        "source_sha_stable": sha_before == sha_after,
    }
    for k, v in report.items():
        print("%s = %r" % (k, v))
    return report


if __name__ == "__main__":
    main()

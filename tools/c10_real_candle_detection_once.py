"""C10 real-candle detection one-off runner (READ-ONLY against
staged data, RESEARCH ONLY, NO TRADING, NO NETWORK, NO REPLAY, NO
PnL).

Scope: a single deterministic scan of the staged canonical BTCUSD
daily candles using the pushed INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1
detector exactly as committed in
sparta_commander/intraweek_calendar_seasonality_drift_v1_detector
_spec_dry_run_contract.py (data-determined favorable-weekday bucket
selected on the in-sample window, then calendar-only OOS detection).

COVERAGE GATE (the reason this runner currently refuses final
detection): the pushed C10 detector REQUIRES an in-sample selection
window of 2019-01-01 .. 2022-12-31. The only authorized canonical
staged source, data/crypto_d1_spot/raw/BTC_1d.csv, begins 2020-01-01,
so the required 2019 in-sample coverage is MISSING. Per the human
blocker decision (C10_REAL_CANDLE_DETECTION_BLOCKER_DECISION) the
runner must NOT silently truncate the in-sample window. Instead it
emits a BLOCKED_MISSING_REQUIRED_IN_SAMPLE_COVERAGE result and does
NOT run the scan, so it produces NO accepted/rejected setup claims.
Final detection stays blocked until full 2019 daily data is staged
through a separately approved data step. The C10 contract is NOT
weakened to accept missing 2019 data.

Hard boundaries:
  - candidate locked to INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1 /
    BTCUSD / 1d / long_only;
  - data source is the single canonical staged CSV only -- NO fetch,
    NO network, NO API, NO credentials, NO wallet, NO broker, NO
    exchange;
  - frozen_regime_inputs source is NOT used (not authorized);
  - no replay, no relabel, no PnL, no scheduler, no notifications,
    no auto-commit, no auto-push;
  - the in-sample/OOS windows, holding horizon, 81 bps floor and
    favorable-weekday selection are taken as committed; the runner
    consumes no C10 edit token and unlocks no downstream gate.

This module is intentionally untracked. It is invoked manually under
an explicit human-approved gate and writes only into the C10
operational data directory.
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

import sparta_commander.intraweek_calendar_seasonality_drift_v1_detector_spec_dry_run_contract as c10d  # noqa: E402

CANDIDATE_ID = "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1"
CANDIDATE_FAMILY = "intraweek_calendar_seasonality_drift"
SYMBOL = "BTCUSD"
TIMEFRAME = "1d"
DIRECTION = "long_only"

# The only authorized canonical staged source (provenance + SHA pinned).
SOURCE_FILE = REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / "BTC_1d.csv"

# Required windows are taken verbatim from the pushed C10 detector.
REQUIRED_IN_SAMPLE_WINDOW = c10d.IN_SAMPLE_SELECTION_WINDOW
REQUIRED_OUT_OF_SAMPLE_WINDOW = c10d.OUT_OF_SAMPLE_WINDOW
REQUIRED_IN_SAMPLE_START = REQUIRED_IN_SAMPLE_WINDOW[0]

OUT_DIR = (REPO_ROOT / "data" / "intraweek_calendar_seasonality_c10"
           / "coverage_blocker")
BLOCKER_PATH = OUT_DIR / "c10_real_candle_coverage_blocker.json"

# Success-path frozen detector artifacts (separate dir from the blocker;
# the covered detection path writes per-setup labels + a summary here so a
# later labels review can recount/certify WITHOUT reading stdout).
DETECTOR_LABELS_DIR = (REPO_ROOT / "data"
                       / "intraweek_calendar_seasonality_c10"
                       / "detector_labels")
OOS_SAMPLE_TAG = "%s_%s" % (REQUIRED_OUT_OF_SAMPLE_WINDOW[0],
                            REQUIRED_OUT_OF_SAMPLE_WINDOW[1])
LABELS_PATH = (DETECTOR_LABELS_DIR
               / ("c10_detector_labels_%s.json" % OOS_SAMPLE_TAG))
SUMMARY_PATH = (DETECTOR_LABELS_DIR
                / ("c10_detector_summary_%s.json" % OOS_SAMPLE_TAG))
MIN_LABELS_REVIEW_THRESHOLD = (
    c10d.SAMPLE_SIZE_ADEQUACY_THRESHOLD_MIN_ACCEPTED)
ARTIFACT_SCHEMA_VERSION_LABELS = "c10_detector_labels_v1"
ARTIFACT_SCHEMA_VERSION_SUMMARY = "c10_detector_summary_v1"

STATUS_BLOCKED = "BLOCKED_MISSING_REQUIRED_IN_SAMPLE_COVERAGE"
STATUS_COVERAGE_OK = "REQUIRED_IN_SAMPLE_COVERAGE_PRESENT"

SCOPE_LOCKS = {
    "no_replay": True, "no_relabel": True, "no_pnl": True,
    "no_fetch": True, "no_network": True, "no_api": True,
    "no_credentials": True, "no_broker": True, "no_exchange": True,
    "no_wallet": True, "no_scheduler": True, "no_paper_trading": True,
    "no_micro_live": True, "no_live_trading": True,
    "no_edit_token_consumed": True,
    "no_downstream_gates_unlocked": True,
    "frozen_regime_inputs_source_not_used": True,
    "c10_contract_not_weakened_for_missing_2019": True,
}


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect_source(path: Path) -> dict:
    """Read the canonical CSV metadata WITHOUT scanning: row count and
    first/last ISO date. Pure read; does not mutate the source."""
    dates: list[str] = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = row.get("date") or row.get("timestamp")
            if d:
                dates.append(str(d))
    dates_sorted = sorted(dates)
    return {
        "source_path":
            str(path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "row_count": len(dates_sorted),
        "first_date": dates_sorted[0] if dates_sorted else None,
        "last_date": dates_sorted[-1] if dates_sorted else None,
        "sha256": compute_sha256(path),
    }


def evaluate_in_sample_coverage(first_date: str | None) -> dict:
    """Determine whether the staged source covers the REQUIRED in-sample
    window start. If the source begins AFTER the required start, the
    required 2019 in-sample coverage is missing and final detection must
    block. Pure -- no I/O, no setup claims."""
    required_start = REQUIRED_IN_SAMPLE_START
    actual_start = first_date
    covered = (actual_start is not None
               and actual_start <= required_start)
    return {
        "required_in_sample_window":
            list(REQUIRED_IN_SAMPLE_WINDOW),
        "required_out_of_sample_window":
            list(REQUIRED_OUT_OF_SAMPLE_WINDOW),
        "required_in_sample_start": required_start,
        "actual_source_start": actual_start,
        "in_sample_coverage_present": covered,
        "missing_2019_in_sample_coverage": not covered,
        "status": STATUS_COVERAGE_OK if covered else STATUS_BLOCKED,
    }


def load_bars_from_csv(path: Path) -> list:
    """Load daily bars in the detector's expected shape. Only reached
    once required coverage is present (it is NOT, today)."""
    bars = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            date = str(row.get("date") or row.get("timestamp"))
            iso_weekday = datetime.date.fromisoformat(date).isoweekday()
            bars.append({
                "date": date,
                "iso_weekday": iso_weekday,
                "time_utc": date + "T00:00:00Z",
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
            })
    return sorted(bars, key=lambda b: b["date"])


def _dump_json(path: Path, obj: dict) -> str:
    """Write a deterministic (sorted-key, no wall-clock) JSON artifact and
    return its SHA-256. Side effect confined to the given path."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
    return compute_sha256(path)


def build_detection_artifacts(*, source_meta: dict, selection: dict,
                              setups: list, cluster: dict,
                              adequacy: dict, sha_before: str,
                              sha_after: str) -> tuple:
    """Pure: assemble the (labels, summary) artifact dicts from an
    already-computed detection result. No I/O. Recount-sufficient -- the
    labels artifact carries every per-setup record plus the aggregate
    counts a labels review needs to re-derive accepted/dropped totals
    without reading stdout. Deterministic: no wall-clock timestamp."""
    accepted_post = list(cluster["kept"])
    dropped = list(cluster["dropped"])
    accepted_pre = [s for s in setups
                    if s.get("status") == "accepted_for_replay_review"]
    status_breakdown: dict = {}
    for s in setups:
        st = s.get("status")
        status_breakdown[st] = status_breakdown.get(st, 0) + 1
    common = {
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "symbol": SYMBOL, "timeframe": TIMEFRAME, "direction": DIRECTION,
        "source_path": source_meta["source_path"],
        "source_sha256_before": sha_before,
        "source_sha256_after": sha_after,
        "source_unchanged_during_detection": sha_before == sha_after,
        "source_first_date": source_meta["first_date"],
        "source_last_date": source_meta["last_date"],
        "source_row_count": source_meta["row_count"],
        "in_sample_selection_window": list(REQUIRED_IN_SAMPLE_WINDOW),
        "out_of_sample_window": list(REQUIRED_OUT_OF_SAMPLE_WINDOW),
        "sample_tag": OOS_SAMPLE_TAG,
        "favorable_weekday_bucket":
            selection["favorable_weekday_bucket"],
        "per_weekday_in_sample_mean_bps":
            selection["per_weekday_mean_bps"],
        "attempts": len(setups),
        "accepted_pre_anti_cluster": len(accepted_pre),
        "accepted_post_anti_cluster": len(accepted_post),
        "anti_cluster_dropped_count": len(dropped),
        "anti_cluster_min_bar_gap": cluster["anti_cluster_min_bar_gap"],
        "anti_cluster_tie_breaker": cluster["tie_breaker"],
        "anti_cluster_does_not_consume_edit_token":
            cluster["anti_cluster_does_not_consume_edit_token"],
        "minimum_labels_review_threshold": MIN_LABELS_REVIEW_THRESHOLD,
        "sample_size_adequacy": adequacy,
        "status_breakdown": status_breakdown,
        "deterministic_no_wallclock_timestamp": True,
        "no_replay": True, "no_pnl": True, "no_trading": True,
        "scope_locks": SCOPE_LOCKS,
    }
    labels = dict(common)
    labels["artifact_schema_version"] = ARTIFACT_SCHEMA_VERSION_LABELS
    labels["selection"] = selection
    labels["accepted_setups_post_anti_cluster"] = accepted_post
    labels["anti_cluster_dropped"] = dropped
    summary = dict(common)
    summary["artifact_schema_version"] = ARTIFACT_SCHEMA_VERSION_SUMMARY
    summary["scope"] = ("real_candle_detection_only_no_replay_no_pnl"
                        "_no_trading")
    summary["labels_path"] = str(
        LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    return labels, summary


def run_detection_when_covered(path: Path, source_meta: dict) -> dict:
    """The full deterministic detection path, GATED behind coverage.
    Scans the OOS window, freezes the per-setup labels + summary
    artifacts under detector_labels/, and returns a COMPACT result
    (counts + artifact paths/SHAs) -- the full per-setup list lives in
    the frozen artifact, not in stdout."""
    sha_before = compute_sha256(path)
    bars = load_bars_from_csv(path)
    selection = c10d.select_favorable_weekday_bucket(bars)
    bucket = selection["favorable_weekday_bucket"]
    if bucket is None:
        raise RuntimeError("no_weekday_bucket_cleared_floor_in_sample")
    setups = c10d.scan_c10_setups(
        bars, bucket, symbol=SYMBOL, timeframe=TIMEFRAME,
        direction=DIRECTION,
        evaluation_window=REQUIRED_OUT_OF_SAMPLE_WINDOW)
    cluster = c10d.apply_anti_cluster_filter(setups)
    adequacy = c10d.check_sample_size_adequacy(cluster["kept"])
    sha_after = compute_sha256(path)
    if sha_before != sha_after:
        raise RuntimeError("staged_source_data_mutated_during_scan")
    labels, summary = build_detection_artifacts(
        source_meta=source_meta, selection=selection, setups=setups,
        cluster=cluster, adequacy=adequacy,
        sha_before=sha_before, sha_after=sha_after)
    labels_sha = _dump_json(LABELS_PATH, labels)
    summary["labels_sha256"] = labels_sha
    summary_sha = _dump_json(SUMMARY_PATH, summary)
    accepted_pre = [s for s in setups
                    if s.get("status") == "accepted_for_replay_review"]
    return {
        "selection": selection,
        "attempts": len(setups),
        "accepted_pre_anti_cluster": len(accepted_pre),
        "accepted_post_anti_cluster": len(cluster["kept"]),
        "anti_cluster_dropped": len(cluster["dropped"]),
        "sample_size_adequacy": adequacy,
        "source_unchanged_during_detection": True,
        "labels_artifact_path": str(
            LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "labels_artifact_sha256": labels_sha,
        "summary_artifact_path": str(
            SUMMARY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "summary_artifact_sha256": summary_sha,
    }


def main() -> dict:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not SOURCE_FILE.exists():
        raise RuntimeError(
            "canonical_staged_source_missing:" + str(SOURCE_FILE))
    source = inspect_source(SOURCE_FILE)
    coverage = evaluate_in_sample_coverage(source["first_date"])
    report = {
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "symbol": SYMBOL, "timeframe": TIMEFRAME,
        "direction": DIRECTION,
        "source": source,
        "coverage": coverage,
        "status": coverage["status"],
        "real_candle_detection_completed": False,
        "no_accepted_or_rejected_setup_claims": True,
        "scope": "real_candle_detection_coverage_gate_only_no_scan"
                 "_no_replay_no_pnl_no_trading",
        "scope_locks": SCOPE_LOCKS,
    }
    if not coverage["in_sample_coverage_present"]:
        report["blocker_reason"] = (
            "pushed C10 detector requires in-sample selection window "
            "%s..%s; canonical staged source %s begins %s, so the "
            "required 2019 in-sample coverage is missing. Final "
            "detection refused; no scan executed; no setup claims "
            "produced. Stage full 2019 daily data via a separately "
            "approved data step to proceed." % (
                REQUIRED_IN_SAMPLE_WINDOW[0],
                REQUIRED_IN_SAMPLE_WINDOW[1],
                source["source_path"], source["first_date"]))
        with open(BLOCKER_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)
        report["blocker_artifact_path"] = (
            str(BLOCKER_PATH.relative_to(REPO_ROOT)).replace("\\", "/"))
        report["blocker_artifact_sha256"] = compute_sha256(BLOCKER_PATH)
        for key, value in report.items():
            print("%s = %r" % (key, value))
        return report
    # Required coverage present -> run detection and freeze artifacts.
    report.update(run_detection_when_covered(SOURCE_FILE, source))
    report["real_candle_detection_completed"] = True
    report["no_accepted_or_rejected_setup_claims"] = False
    report["scope"] = ("real_candle_detection_scan_freezes_detector_labels"
                       "_artifacts_no_replay_no_pnl_no_trading")
    for key, value in report.items():
        print("%s = %r" % (key, value))
    return report


if __name__ == "__main__":
    main()

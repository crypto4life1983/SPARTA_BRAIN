"""s10 D1 MNQ+MGC Step 02c raw-data audit (local-only).

Audits the operator-captured Step 02b output against the sealed-spec DR9 data-
continuity thresholds. Local file reads only. No Databento call. No network.
No OOS return summary. No strategy evaluation. No Sharpe / PnL / drawdown
computation. The script computes structural data-quality metrics ONLY: row
counts per window, column presence, sha256 verification, timestamp boundaries,
calendar coverage, missing-observation counts, and abs(log_return)
consecutive-violation counts.

Sealed spec reference: docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md
Locked DR9 thresholds (carried byte-equivalent):
  DR9_MIN_PCT_EXPECTED_TRADING_DAYS        = 0.95
  DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN       = 0.30
  DR9_MAX_MISSING_OBSERVATIONS             = 5
  DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD  = 5
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


SEALED_SPEC_COMMIT = "9040429"
CANDIDATE_RECORD_ID = "s10-d1-cross-asset-trend-or-meanrev-mnq-mgc-databento-long-history"

INPUT_DIR = Path("data/s10_d1_mnq_mgc_databento_long_history/raw")
MANIFEST_FILENAME = "s10_d1_mnq_mgc_step02b_fetch_manifest.json"

REQUIRED_CSV_COLUMNS = ("ts_event", "open", "high", "low", "close", "volume")

IS_WINDOW_START  = date(2019, 5, 13)
IS_WINDOW_END    = date(2023, 12, 29)
OOS_WINDOW_START = date(2024, 1, 2)
OOS_WINDOW_END   = date(2025, 12, 30)

# Sealed DR9 thresholds.
DR9_MIN_PCT_EXPECTED_TRADING_DAYS        = 0.95
DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN       = 0.30
DR9_MAX_MISSING_OBSERVATIONS             = 5
DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD  = 5

# Expected-trading-day calendar baseline. CME continuous front-month daily bars
# on micro futures emit Sun-evening + Mon-Fri sessions; the observed-row rate
# is typically higher than the 252/year equity baseline. We compute the
# baseline as `calendar_days * (252 / 365.25)` and note that observed counts
# > expected are normal (no DR9 trigger).
TRADING_DAYS_PER_CALENDAR_DAY = 252.0 / 365.25

# Operator-reported reduced-quality dates from Databento BentoWarning.
OPERATOR_REPORTED_REDUCED_QUALITY_DAYS = ("2020-02-27", "2020-02-28", "2020-06-30")


def _sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _expected_trading_days(start_d, end_d):
    """Calendar-based estimate; conservative for CME daily continuous front."""
    cal_days = (end_d - start_d).days + 1
    return max(int(round(cal_days * TRADING_DAYS_PER_CALENDAR_DAY)), 1)


def _read_csv_minimal(path):
    """Read CSV header + parse rows. Returns (columns, list_of_rows_as_dicts).

    Does NOT print or log row contents. Does NOT compute aggregate returns.
    Each row dict contains only the parsed string values needed downstream.
    """
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        for r in reader:
            rows.append(r)
    return columns, rows


def _parse_ts_to_date(ts_str):
    """Parse a Databento ts_event string ('YYYY-MM-DD HH:MM:SS+00:00') to a date."""
    s = ts_str.strip()
    # Accept both with-tz ('+00:00') and naive ('YYYY-MM-DD HH:MM:SS') forms.
    if "+" in s:
        s_date = s.split(" ", 1)[0]
    elif "T" in s:
        s_date = s.split("T", 1)[0]
    else:
        parts = s.split(" ", 1)
        s_date = parts[0]
    y, m, d = s_date.split("-")
    return date(int(y), int(m), int(d))


def _safe_float(s):
    try:
        v = float(s)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    except (ValueError, TypeError):
        return None


def _audit_symbol(sym, csv_path, manifest_record):
    """Run all DR9 checks on one symbol. Return a structured result dict.

    Does NOT print row content. Does NOT compute mean/sum/sharpe over returns.
    abs(log_return) is computed ONLY for the DR9 consecutive-violation
    integrity check, not for any strategy or edge claim.
    """
    result = {
        "symbol": sym,
        "csv_path": str(csv_path).replace("\\", "/"),
    }

    # 1. CSV file sha256 vs manifest
    actual_sha = _sha256_of_file(csv_path)
    expected_sha = manifest_record.get("sha256")
    result["csv_sha256"] = actual_sha
    result["csv_sha256_matches_manifest"] = (actual_sha == expected_sha)

    # 2. Read CSV
    columns, rows = _read_csv_minimal(csv_path)
    result["row_count_observed"] = len(rows)
    result["row_count_manifest"] = manifest_record.get("row_count")
    result["row_count_matches_manifest"] = (len(rows) == manifest_record.get("row_count"))

    # 3. Required columns
    missing_cols = [c for c in REQUIRED_CSV_COLUMNS if c not in columns]
    result["columns_observed_count"] = len(columns)
    result["required_columns_missing"] = missing_cols
    result["required_columns_all_present"] = (len(missing_cols) == 0)

    # 4. Parse timestamps to dates (no return values, no OHLC inspection except for DR9 log-return)
    if missing_cols:
        # Cannot proceed with row-level checks if structural columns missing.
        result["dr9_evaluation"] = {
            "skipped_due_to_missing_columns": True,
            "would_have_fired": True,
            "fire_reason": "required_columns_missing",
        }
        return result

    dates = []
    closes = []
    for r in rows:
        try:
            dates.append(_parse_ts_to_date(r["ts_event"]))
        except Exception:
            dates.append(None)
        closes.append(_safe_float(r.get("close")))

    # Boundary timestamps
    first_d = next((d for d in dates if d is not None), None)
    last_d = next((d for d in reversed(dates) if d is not None), None)
    result["first_date"] = first_d.isoformat() if first_d else None
    result["last_date"] = last_d.isoformat() if last_d else None

    # 5. IS / OOS coverage
    is_rows = sum(1 for d in dates if d is not None and IS_WINDOW_START <= d <= IS_WINDOW_END)
    oos_rows = sum(1 for d in dates if d is not None and OOS_WINDOW_START <= d <= OOS_WINDOW_END)
    pre_is_rows = sum(1 for d in dates if d is not None and d < IS_WINDOW_START)
    post_oos_rows = sum(1 for d in dates if d is not None and d > OOS_WINDOW_END)

    result["is_window_row_count"] = is_rows
    result["oos_window_row_count_LOCKED_NOT_INSPECTED_FOR_RETURNS"] = oos_rows
    result["rows_before_is_window_start"] = pre_is_rows
    result["rows_after_oos_window_end"] = post_oos_rows

    expected_is = _expected_trading_days(IS_WINDOW_START, IS_WINDOW_END)
    expected_oos = _expected_trading_days(OOS_WINDOW_START, OOS_WINDOW_END)
    result["expected_is_trading_days_calendar_baseline"] = expected_is
    result["expected_oos_trading_days_calendar_baseline"] = expected_oos
    result["is_pct_observed"] = round(is_rows / expected_is, 4) if expected_is > 0 else 0
    result["oos_pct_observed_structural_only"] = (
        round(oos_rows / expected_oos, 4) if expected_oos > 0 else 0
    )

    # 6. Missing-observation count (structural; uses sealed threshold)
    # Heuristic: count distinct calendar trading-day gaps > 1 within IS window.
    is_dates_sorted = sorted({d for d in dates if d is not None and IS_WINDOW_START <= d <= IS_WINDOW_END})
    consecutive_gap_violations_is = 0
    if len(is_dates_sorted) >= 2:
        for i in range(1, len(is_dates_sorted)):
            gap = (is_dates_sorted[i] - is_dates_sorted[i - 1]).days
            # Allow weekend (gap=3 over Fri->Mon) + occasional holidays (gap up to 5).
            # Flag any gap > 5 calendar days as a missing-observation candidate.
            if gap > 5:
                consecutive_gap_violations_is += 1
    result["is_window_calendar_gaps_above_5_days_count"] = consecutive_gap_violations_is
    result["dr9_max_missing_observations_threshold"] = DR9_MAX_MISSING_OBSERVATIONS

    # 7. Consecutive abs(log_return) > 0.30 events (close-to-close; IS window only)
    consec_violations_is = 0
    prev_violation = False
    log_return_max_abs_observed_is = 0.0
    log_return_violation_dates_is = []
    for i in range(1, len(dates)):
        d_i = dates[i]
        if d_i is None or not (IS_WINDOW_START <= d_i <= IS_WINDOW_END):
            prev_violation = False
            continue
        c_prev = closes[i - 1]
        c_curr = closes[i]
        if c_prev is None or c_curr is None or c_prev <= 0 or c_curr <= 0:
            prev_violation = False
            continue
        try:
            lr = math.log(c_curr / c_prev)
        except (ValueError, ZeroDivisionError):
            prev_violation = False
            continue
        a = abs(lr)
        if a > log_return_max_abs_observed_is:
            log_return_max_abs_observed_is = a
        is_violation = (a > DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN)
        if is_violation and prev_violation:
            consec_violations_is += 1
            log_return_violation_dates_is.append(d_i.isoformat())
        prev_violation = is_violation

    result["is_consecutive_abs_log_return_violation_count"] = consec_violations_is
    result["is_max_abs_log_return_observed"] = round(log_return_max_abs_observed_is, 6)
    result["is_consecutive_violation_dates"] = log_return_violation_dates_is
    result["dr9_max_consecutive_violation_threshold"] = DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD

    # 8. DR9 verdict per sealed-spec thresholds
    is_pct = result["is_pct_observed"]
    pct_pass = (is_pct >= DR9_MIN_PCT_EXPECTED_TRADING_DAYS)
    missing_pass = (consecutive_gap_violations_is <= DR9_MAX_MISSING_OBSERVATIONS)
    consec_pass = (consec_violations_is <= DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD)
    dr9_fire = (not pct_pass) or (not missing_pass) or (not consec_pass)
    result["dr9_evaluation"] = {
        "dr9_min_pct_expected_trading_days_threshold": DR9_MIN_PCT_EXPECTED_TRADING_DAYS,
        "is_pct_observed": is_pct,
        "is_pct_pass": pct_pass,
        "missing_observations_count": consecutive_gap_violations_is,
        "missing_observations_threshold": DR9_MAX_MISSING_OBSERVATIONS,
        "missing_observations_pass": missing_pass,
        "consecutive_abs_log_return_violation_count": consec_violations_is,
        "consecutive_abs_log_return_violation_threshold": DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD,
        "consecutive_violation_pass": consec_pass,
        "dr9_would_fire": dr9_fire,
        "dr9_fire_decision": "fire" if dr9_fire else "clean",
    }

    return result


def main():
    print(f"=== s10 D1 Step 02c raw-data audit (local-only) ===")
    print(f"sealed_spec_commit_anchor: {SEALED_SPEC_COMMIT}")
    print(f"candidate: {CANDIDATE_RECORD_ID}")
    print(f"input_dir: {INPUT_DIR.resolve()}")
    print(
        f"DR9 thresholds: pct>={DR9_MIN_PCT_EXPECTED_TRADING_DAYS}, "
        f"abs_log_ret<={DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN}, "
        f"missing<={DR9_MAX_MISSING_OBSERVATIONS}, "
        f"consec<={DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD}"
    )
    print(
        f"IS window: {IS_WINDOW_START.isoformat()} -> {IS_WINDOW_END.isoformat()} "
        f"(returns NOT computed)"
    )
    print(
        f"OOS window: {OOS_WINDOW_START.isoformat()} -> {OOS_WINDOW_END.isoformat()} "
        f"(LOCKED; structural row-count only; NO return analysis)"
    )

    manifest_path = INPUT_DIR / MANIFEST_FILENAME
    if not manifest_path.exists():
        sys.stderr.write(f"Manifest not found at {manifest_path}; fail-closed.\n")
        return 2
    manifest_sha = _sha256_of_file(manifest_path)
    manifest = json.load(open(manifest_path, encoding="utf-8"))
    print(f"manifest_sha256: {manifest_sha}")

    if manifest.get("sealed_spec_commit_anchor") != SEALED_SPEC_COMMIT:
        sys.stderr.write(
            f"Manifest sealed_spec_commit_anchor mismatch: "
            f"manifest={manifest.get('sealed_spec_commit_anchor')!r} "
            f"audit_expects={SEALED_SPEC_COMMIT!r}; fail-closed.\n"
        )
        return 3

    audit_results = []
    any_fire = False
    for sym_record in manifest.get("symbols", []):
        sym = sym_record["symbol"]
        csv_filename = sym_record["output_filename"]
        csv_path = INPUT_DIR / csv_filename
        if not csv_path.exists():
            sys.stderr.write(f"CSV not found at {csv_path}; fail-closed.\n")
            return 4
        r = _audit_symbol(sym, csv_path, sym_record)
        audit_results.append(r)
        if r.get("dr9_evaluation", {}).get("dr9_would_fire", False):
            any_fire = True

        # Print SAFE summary per symbol (no row content; no return values
        # beyond the DR9 max-abs-log-return integrity number).
        dre = r["dr9_evaluation"]
        print()
        print(f"--- {sym} audit summary ---")
        print(f"  csv_sha256_matches_manifest        : {r['csv_sha256_matches_manifest']}")
        print(f"  row_count_matches_manifest         : {r['row_count_matches_manifest']}")
        print(f"  required_columns_all_present       : {r['required_columns_all_present']}")
        print(f"  first_date                         : {r['first_date']}")
        print(f"  last_date                          : {r['last_date']}")
        print(f"  is_window_row_count                : {r['is_window_row_count']}")
        print(f"  is_pct_observed                    : {dre['is_pct_observed']}")
        print(f"  is_pct_pass                        : {dre['is_pct_pass']}")
        print(f"  is_window_calendar_gaps_above_5    : {dre['missing_observations_count']}")
        print(f"  missing_observations_pass          : {dre['missing_observations_pass']}")
        print(f"  is_consec_abs_log_ret_viol_count   : {dre['consecutive_abs_log_return_violation_count']}")
        print(f"  is_max_abs_log_return_observed     : {r['is_max_abs_log_return_observed']}")
        print(f"  consecutive_violation_pass         : {dre['consecutive_violation_pass']}")
        print(f"  dr9_fire_decision                  : {dre['dr9_fire_decision']}")
        print(
            f"  oos_window_row_count_structural    : "
            f"{r['oos_window_row_count_LOCKED_NOT_INSPECTED_FOR_RETURNS']} "
            "(no return analysis performed)"
        )

    # Final audit verdict
    print()
    print(f"=== AUDIT_VERDICT ===")
    if any_fire:
        print(f"  verdict: DR9_FIRED_AUDIT_FAIL")
    else:
        print(f"  verdict: AUDIT_PASS_DR9_CLEAN")

    # Emit machine-readable summary on a single line for downstream report.
    summary = {
        "verdict": "AUDIT_PASS_DR9_CLEAN" if not any_fire else "DR9_FIRED_AUDIT_FAIL",
        "any_dr9_fire": any_fire,
        "manifest_sha256": manifest_sha,
        "manifest_path": str(manifest_path).replace("\\", "/"),
        "audit_results": audit_results,
        "operator_reported_reduced_quality_days": list(OPERATOR_REPORTED_REDUCED_QUALITY_DAYS),
        "audit_run_utc": datetime.now(timezone.utc).isoformat(),
    }
    print()
    print("AUDIT_SUMMARY_JSON_BEGIN")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    print("AUDIT_SUMMARY_JSON_END")
    return 0


if __name__ == "__main__":
    sys.exit(main())

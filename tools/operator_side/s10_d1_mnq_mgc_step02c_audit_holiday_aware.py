"""s10 D1 MNQ+MGC Step 02c -- holiday-aware audit refinement (local-only).

Refinement of the strict audit in `s10_d1_mnq_mgc_step02c_audit_raw_data.py`.
Same sealed-spec DR9 thresholds. ONLY the operationalization of
`missing_observations` changes: calendar gaps > 5 days that are explained by
a known US/CME federal-holiday closure are reclassified as "expected closures"
and excluded from the missing-observations count. Genuine vendor-side gaps
(no holiday in the gap span) still count toward the threshold.

DR9 threshold (5) is locked at SEAL; only the heuristic changes here.

Local file reads only. No Databento call. No network. No OOS return summary.
No strategy performance evaluation. No Sharpe / PnL / drawdown / win-rate
computation. abs(log_return) is computed ONLY for the DR9 outlier check.

Sealed spec: docs/s10_d1_mnq_mgc_databento_long_history_tier_n_spec.md
Strict-audit script (predecessor): tools/operator_side/s10_d1_mnq_mgc_step02c_audit_raw_data.py
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

# Sealed DR9 thresholds (LOCKED; not modifiable post-SEAL).
DR9_MIN_PCT_EXPECTED_TRADING_DAYS        = 0.95
DR9_MAX_CONSECUTIVE_ABS_LOG_RETURN       = 0.30
DR9_MAX_MISSING_OBSERVATIONS             = 5
DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD  = 5

TRADING_DAYS_PER_CALENDAR_DAY = 252.0 / 365.25

# Operator-reported reduced-quality dates (Databento BentoWarning).
OPERATOR_REPORTED_REDUCED_QUALITY_DAYS = ("2020-02-27", "2020-02-28", "2020-06-30")

# Hardcoded US / CME-Globex federal-holiday list covering the IS window
# (2019-2023). These are the dates on which CME products either closed fully
# or executed early closes that materially shorten the daily session and
# produce a multi-day calendar gap in the daily-bar emission for some
# continuous-front products.
#
# Sources: US OPM federal-holiday calendar + CME Group holiday schedule
# (public).  This list is BRITTLE: Good-Friday observance varies by product;
# emergency closures (e.g., 9/11, Sandy) are NOT enumerated; Juneteenth was
# added as a federal holiday in 2021. The operator should treat the
# holiday-aware reclassification as a refinement, not a guarantee.
US_CME_FEDERAL_HOLIDAYS_LIST = [
    # ---- 2019 ----
    "2019-01-01",  # New Year's Day (Tue)
    "2019-01-21",  # MLK Day (Mon)
    "2019-02-18",  # Presidents Day (Mon)
    "2019-04-19",  # Good Friday (Fri)
    "2019-05-27",  # Memorial Day (Mon)
    "2019-07-04",  # Independence Day (Thu)
    "2019-09-02",  # Labor Day (Mon)
    "2019-11-28",  # Thanksgiving (Thu)
    "2019-12-25",  # Christmas Day (Wed)
    # ---- 2020 ----
    "2020-01-01",  # New Year's Day (Wed)
    "2020-01-20",  # MLK Day (Mon)
    "2020-02-17",  # Presidents Day (Mon)
    "2020-04-10",  # Good Friday (Fri)
    "2020-05-25",  # Memorial Day (Mon)
    "2020-07-03",  # Independence Day observed (Fri; Jul 4 = Sat)
    "2020-09-07",  # Labor Day (Mon)
    "2020-11-26",  # Thanksgiving (Thu)
    "2020-12-25",  # Christmas Day (Fri)
    # ---- 2021 ----
    "2021-01-01",  # New Year's Day (Fri)
    "2021-01-18",  # MLK Day (Mon)
    "2021-02-15",  # Presidents Day (Mon)
    "2021-04-02",  # Good Friday (Fri)
    "2021-05-31",  # Memorial Day (Mon)
    "2021-07-05",  # Independence Day observed (Mon; Jul 4 = Sun)
    "2021-09-06",  # Labor Day (Mon)
    "2021-11-25",  # Thanksgiving (Thu)
    "2021-12-24",  # Christmas Day observed (Fri; Dec 25 = Sat)
    # ---- 2022 ----
    "2022-01-17",  # MLK Day (Mon)
    "2022-02-21",  # Presidents Day (Mon)
    "2022-04-15",  # Good Friday (Fri)
    "2022-05-30",  # Memorial Day (Mon)
    "2022-06-20",  # Juneteenth observed (Mon; Jun 19 = Sun)
    "2022-07-04",  # Independence Day (Mon)
    "2022-09-05",  # Labor Day (Mon)
    "2022-11-24",  # Thanksgiving (Thu)
    "2022-12-26",  # Christmas Day observed (Mon; Dec 25 = Sun)
    # ---- 2023 ----
    "2023-01-02",  # New Year's Day observed (Mon; Jan 1 = Sun)
    "2023-01-16",  # MLK Day (Mon)
    "2023-02-20",  # Presidents Day (Mon)
    "2023-04-07",  # Good Friday (Fri)
    "2023-05-29",  # Memorial Day (Mon)
    "2023-06-19",  # Juneteenth (Mon)
    "2023-07-04",  # Independence Day (Tue)
    "2023-09-04",  # Labor Day (Mon)
    "2023-11-23",  # Thanksgiving (Thu)
    "2023-12-25",  # Christmas Day (Mon)
]
US_CME_FEDERAL_HOLIDAYS = frozenset(
    date.fromisoformat(s) for s in US_CME_FEDERAL_HOLIDAYS_LIST
)


def _sha256_of_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _expected_trading_days(start_d, end_d):
    cal_days = (end_d - start_d).days + 1
    return max(int(round(cal_days * TRADING_DAYS_PER_CALENDAR_DAY)), 1)


def _read_csv_minimal(path):
    rows = []
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        for r in reader:
            rows.append(r)
    return columns, rows


def _parse_ts_to_date(ts_str):
    s = ts_str.strip()
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


def _gap_holiday_explained(prev_d, curr_d):
    """Return (explained, holidays_in_gap_list).

    A gap is "holiday-explained" iff at least one US/CME federal holiday in
    `US_CME_FEDERAL_HOLIDAYS` falls within the half-open span
    (prev_d, curr_d) -- i.e., between the two observed bar dates exclusive.
    """
    span_start = prev_d + timedelta(days=1)
    span_end = curr_d - timedelta(days=1)
    if span_start > span_end:
        return False, []
    hits = []
    cur = span_start
    while cur <= span_end:
        if cur in US_CME_FEDERAL_HOLIDAYS:
            hits.append(cur.isoformat())
        cur += timedelta(days=1)
    return (len(hits) > 0), hits


def _audit_symbol(sym, csv_path, manifest_record):
    result = {
        "symbol": sym,
        "csv_path": str(csv_path).replace("\\", "/"),
    }

    actual_sha = _sha256_of_file(csv_path)
    expected_sha = manifest_record.get("sha256")
    result["csv_sha256"] = actual_sha
    result["csv_sha256_matches_manifest"] = (actual_sha == expected_sha)

    columns, rows = _read_csv_minimal(csv_path)
    result["row_count_observed"] = len(rows)
    result["row_count_manifest"] = manifest_record.get("row_count")
    result["row_count_matches_manifest"] = (len(rows) == manifest_record.get("row_count"))

    missing_cols = [c for c in REQUIRED_CSV_COLUMNS if c not in columns]
    result["columns_observed_count"] = len(columns)
    result["required_columns_missing"] = missing_cols
    result["required_columns_all_present"] = (len(missing_cols) == 0)

    if missing_cols:
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

    first_d = next((d for d in dates if d is not None), None)
    last_d = next((d for d in reversed(dates) if d is not None), None)
    result["first_date"] = first_d.isoformat() if first_d else None
    result["last_date"] = last_d.isoformat() if last_d else None

    is_rows = sum(1 for d in dates if d is not None and IS_WINDOW_START <= d <= IS_WINDOW_END)
    oos_rows = sum(1 for d in dates if d is not None and OOS_WINDOW_START <= d <= OOS_WINDOW_END)
    pre_is_rows = sum(1 for d in dates if d is not None and d < IS_WINDOW_START)
    post_oos_rows = sum(1 for d in dates if d is not None and d > OOS_WINDOW_END)
    result["is_window_row_count"] = is_rows
    result["oos_window_row_count_LOCKED_NOT_INSPECTED_FOR_RETURNS"] = oos_rows
    result["rows_before_is_window_start"] = pre_is_rows
    result["rows_after_oos_window_end"] = post_oos_rows

    expected_is = _expected_trading_days(IS_WINDOW_START, IS_WINDOW_END)
    result["expected_is_trading_days_calendar_baseline"] = expected_is
    result["is_pct_observed"] = round(is_rows / expected_is, 4) if expected_is > 0 else 0

    # Gap analysis with holiday-aware reclassification
    is_dates_sorted = sorted({d for d in dates if d is not None and IS_WINDOW_START <= d <= IS_WINDOW_END})
    gap_records = []
    strict_gap_count = 0
    holiday_explained_gap_count = 0
    data_quality_gap_count = 0
    if len(is_dates_sorted) >= 2:
        for i in range(1, len(is_dates_sorted)):
            prev_d = is_dates_sorted[i - 1]
            curr_d = is_dates_sorted[i]
            gap = (curr_d - prev_d).days
            if gap > 5:
                strict_gap_count += 1
                explained, holidays_in_span = _gap_holiday_explained(prev_d, curr_d)
                gap_records.append({
                    "prev_observed_date": prev_d.isoformat(),
                    "next_observed_date": curr_d.isoformat(),
                    "gap_calendar_days": gap,
                    "holiday_explained": explained,
                    "holidays_in_span": holidays_in_span,
                })
                if explained:
                    holiday_explained_gap_count += 1
                else:
                    data_quality_gap_count += 1

    result["is_window_strict_gap_count_above_5_days"] = strict_gap_count
    result["is_window_holiday_explained_gap_count"] = holiday_explained_gap_count
    result["is_window_data_quality_gap_count_after_holiday_exclusion"] = data_quality_gap_count
    result["is_window_gap_records"] = gap_records

    # Consecutive abs(log_return) > 0.30 check (unchanged from strict audit)
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

    # DR9 verdict (using holiday-aware data_quality_gap_count for missing_observations)
    is_pct = result["is_pct_observed"]
    pct_pass = (is_pct >= DR9_MIN_PCT_EXPECTED_TRADING_DAYS)
    missing_pass_holiday_aware = (data_quality_gap_count <= DR9_MAX_MISSING_OBSERVATIONS)
    consec_pass = (consec_violations_is <= DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD)
    dr9_fire = (not pct_pass) or (not missing_pass_holiday_aware) or (not consec_pass)

    # Also record what the strict audit would have produced for comparison.
    missing_pass_strict = (strict_gap_count <= DR9_MAX_MISSING_OBSERVATIONS)
    dr9_fire_strict = (not pct_pass) or (not missing_pass_strict) or (not consec_pass)

    result["dr9_evaluation"] = {
        "dr9_min_pct_expected_trading_days_threshold": DR9_MIN_PCT_EXPECTED_TRADING_DAYS,
        "is_pct_observed": is_pct,
        "is_pct_pass": pct_pass,
        "missing_observations_threshold": DR9_MAX_MISSING_OBSERVATIONS,
        "holiday_aware_missing_observations_count": data_quality_gap_count,
        "holiday_aware_missing_observations_pass": missing_pass_holiday_aware,
        "strict_missing_observations_count": strict_gap_count,
        "strict_missing_observations_pass": missing_pass_strict,
        "holiday_explained_gap_count": holiday_explained_gap_count,
        "consecutive_abs_log_return_violation_count": consec_violations_is,
        "consecutive_abs_log_return_violation_threshold": DR9_MAX_CONSECUTIVE_VIOLATION_THRESHOLD,
        "consecutive_violation_pass": consec_pass,
        "dr9_would_fire_holiday_aware": dr9_fire,
        "dr9_would_fire_strict_for_comparison": dr9_fire_strict,
        "dr9_fire_decision_holiday_aware": "fire" if dr9_fire else "clean",
        "dr9_fire_decision_strict_for_comparison": "fire" if dr9_fire_strict else "clean",
    }

    return result


def main():
    print(f"=== s10 D1 Step 02c holiday-aware audit refinement (local-only) ===")
    print(f"sealed_spec_commit_anchor: {SEALED_SPEC_COMMIT}")
    print(f"candidate: {CANDIDATE_RECORD_ID}")
    print(f"input_dir: {INPUT_DIR.resolve()}")
    print(f"holiday_list_count: {len(US_CME_FEDERAL_HOLIDAYS_LIST)} entries (2019-2023)")
    print(
        f"DR9 thresholds (sealed; unchanged): pct>={DR9_MIN_PCT_EXPECTED_TRADING_DAYS}, "
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
        f"(LOCKED; structural only; NO return analysis)"
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
    any_fire_holiday_aware = False
    any_fire_strict = False
    for sym_record in manifest.get("symbols", []):
        sym = sym_record["symbol"]
        csv_filename = sym_record["output_filename"]
        csv_path = INPUT_DIR / csv_filename
        if not csv_path.exists():
            sys.stderr.write(f"CSV not found at {csv_path}; fail-closed.\n")
            return 4
        r = _audit_symbol(sym, csv_path, sym_record)
        audit_results.append(r)
        dre = r.get("dr9_evaluation", {})
        if dre.get("dr9_would_fire_holiday_aware", False):
            any_fire_holiday_aware = True
        if dre.get("dr9_would_fire_strict_for_comparison", False):
            any_fire_strict = True

        print()
        print(f"--- {sym} holiday-aware audit summary ---")
        print(f"  csv_sha256_matches_manifest        : {r['csv_sha256_matches_manifest']}")
        print(f"  row_count_matches_manifest         : {r['row_count_matches_manifest']}")
        print(f"  required_columns_all_present       : {r['required_columns_all_present']}")
        print(f"  first_date                         : {r['first_date']}")
        print(f"  last_date                          : {r['last_date']}")
        print(f"  is_window_row_count                : {r['is_window_row_count']}")
        print(f"  is_pct_observed                    : {dre['is_pct_observed']}")
        print(f"  is_pct_pass                        : {dre['is_pct_pass']}")
        print(f"  strict_missing_obs_count           : {dre['strict_missing_observations_count']}")
        print(f"  holiday_explained_gap_count        : {dre['holiday_explained_gap_count']}")
        print(f"  holiday_aware_missing_obs_count    : {dre['holiday_aware_missing_observations_count']}")
        print(f"  holiday_aware_missing_obs_pass     : {dre['holiday_aware_missing_observations_pass']}")
        print(f"  consecutive_abs_log_ret_viol_count : {dre['consecutive_abs_log_return_violation_count']}")
        print(f"  is_max_abs_log_return_observed     : {r['is_max_abs_log_return_observed']}")
        print(f"  consecutive_violation_pass         : {dre['consecutive_violation_pass']}")
        print(f"  dr9_fire_decision_holiday_aware    : {dre['dr9_fire_decision_holiday_aware']}")
        print(f"  dr9_fire_decision_strict (compare) : {dre['dr9_fire_decision_strict_for_comparison']}")
        # Print gap details with classification (no row content; only dates + holiday classification)
        if r.get("is_window_gap_records"):
            print(f"  gap detail (prev -> next | days | explained? | holidays in span):")
            for g in r["is_window_gap_records"]:
                hols = ",".join(g["holidays_in_span"]) if g["holidays_in_span"] else "-"
                print(
                    f"    {g['prev_observed_date']} -> {g['next_observed_date']} | "
                    f"{g['gap_calendar_days']}d | "
                    f"explained={g['holiday_explained']} | holidays=[{hols}]"
                )
        print(
            f"  oos_window_row_count_structural    : "
            f"{r['oos_window_row_count_LOCKED_NOT_INSPECTED_FOR_RETURNS']} "
            "(no return analysis performed)"
        )

    print()
    print(f"=== AUDIT_VERDICT_HOLIDAY_AWARE ===")
    if any_fire_holiday_aware:
        print(f"  verdict: DR9_FIRED_AUDIT_FAIL_HOLIDAY_AWARE")
    else:
        print(f"  verdict: AUDIT_PASS_DR9_CLEAN_HOLIDAY_AWARE")
    print(f"  comparison_strict_verdict: "
          f"{'DR9_FIRED_AUDIT_FAIL' if any_fire_strict else 'AUDIT_PASS_DR9_CLEAN'}")

    summary = {
        "verdict_holiday_aware": (
            "AUDIT_PASS_DR9_CLEAN_HOLIDAY_AWARE" if not any_fire_holiday_aware
            else "DR9_FIRED_AUDIT_FAIL_HOLIDAY_AWARE"
        ),
        "verdict_strict_for_comparison": (
            "AUDIT_PASS_DR9_CLEAN" if not any_fire_strict else "DR9_FIRED_AUDIT_FAIL"
        ),
        "any_dr9_fire_holiday_aware": any_fire_holiday_aware,
        "any_dr9_fire_strict": any_fire_strict,
        "manifest_sha256": manifest_sha,
        "manifest_path": str(manifest_path).replace("\\", "/"),
        "audit_results": audit_results,
        "operator_reported_reduced_quality_days": list(OPERATOR_REPORTED_REDUCED_QUALITY_DAYS),
        "us_cme_federal_holiday_list_entries_count_2019_2023": len(US_CME_FEDERAL_HOLIDAYS_LIST),
        "audit_run_utc": datetime.now(timezone.utc).isoformat(),
    }
    print()
    print("AUDIT_SUMMARY_JSON_BEGIN")
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    print("AUDIT_SUMMARY_JSON_END")
    return 0


if __name__ == "__main__":
    sys.exit(main())

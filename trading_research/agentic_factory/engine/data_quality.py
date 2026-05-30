"""Offline data-quality scanner for the Agentic Backtest Factory.

OFFLINE / CSV-ONLY: inspects a local CSV and reports whether it is trustworthy
enough to base a backtest read on. It never fetches, downloads, streams, or
connects anywhere. Python standard library only (csv, datetime, collections).

The scanner answers one honest question: *what is this dataset actually good
for* — plumbing test, smoke test, serious research, or a profitability
conclusion. It does not run a backtest and it does not optimize anything.
"""

from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime, time as dtime
from typing import Any, Dict, List, Optional

REQUIRED_OHLC = ["open", "high", "low", "close"]

# Grade gates. Deliberately strict: a handful of holiday-thin sessions must not
# be allowed to masquerade as research-grade evidence.
SERIOUS_RESEARCH_MIN_SESSIONS = 60
PROFITABILITY_MIN_SESSIONS = 200
# A profitability read needs regime spread, not just session count: a single
# rich year (200+ sessions) is still one volatility regime and must not pass.
# Require multiple calendar years OR many distinct months on top of the
# session-count bar.
PROFITABILITY_MIN_DISTINCT_YEARS = 2
PROFITABILITY_MIN_DISTINCT_MONTHS = 18

# Verdict labels.
UNUSABLE = "UNUSABLE"
NEEDS_MORE_DATA = "NEEDS_MORE_DATA"
RESEARCH_OK_NOT_PROFITABILITY = "RESEARCH_OK_NOT_PROFITABILITY_GRADE"
PROFITABILITY_GRADE = "PROFITABILITY_GRADE"


def _parse_time(hhmm: str) -> dtime:
    parts = hhmm.split(":")
    return dtime(int(parts[0]), int(parts[1]))


def _minutes_of(t: dtime) -> int:
    return t.hour * 60 + t.minute


def _try_float(raw: Optional[str]) -> Optional[float]:
    if raw is None:
        return None
    raw = raw.strip()
    if raw == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _try_ts(raw: Optional[str]) -> Optional[datetime]:
    if raw is None:
        return None
    raw = raw.strip()
    if raw == "":
        return None
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def scan_csv(
    csv_path: str,
    timestamp_column: str = "ts_event",
    session_start: str = "14:30",
    session_end: str = "21:00",
    opening_range_minutes: int = 15,
) -> Dict[str, Any]:
    """Inspect a local CSV and return a data-quality report dict (inert)."""
    start_t = _parse_time(session_start)
    end_t = _parse_time(session_end)
    start_m = _minutes_of(start_t)
    end_m = _minutes_of(end_t)
    or_end_m = start_m + int(opening_range_minutes)

    report: Dict[str, Any] = {
        "file_path": csv_path,
        "timestamp_column": timestamp_column,
        "session_window_utc": f"{session_start}-{session_end}",
        "opening_range_minutes": int(opening_range_minutes),
        "row_count": 0,
        "first_timestamp": None,
        "last_timestamp": None,
        "required_columns_present": False,
        "missing_columns": [],
        "duplicate_timestamps": 0,
        "invalid_ohlc_rows": 0,
        "timezone_aware": False,
        "distinct_dates": 0,
        "distinct_years": 0,
        "distinct_months": 0,
        "estimated_bar_interval_minutes": None,
        "session_coverage_pct_avg": 0.0,
        "eligible_rth_sessions": 0,
        "thin_session_warnings": [],
        "readiness": {
            "plumbing_test": False,
            "smoke_test": False,
            "serious_research": False,
            "profitability_conclusion": False,
        },
        "verdict": UNUSABLE,
        "notes": [],
    }

    with open(csv_path, "r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        header_map = {h.lower(): h for h in fieldnames}
        rows = list(reader)

    report["row_count"] = len(rows)

    # Column presence check (case-insensitive).
    missing: List[str] = []
    ts_key = header_map.get(timestamp_column.lower())
    if ts_key is None:
        missing.append(timestamp_column)
    for col in REQUIRED_OHLC:
        if col not in header_map:
            missing.append(col)
    report["missing_columns"] = missing
    report["required_columns_present"] = not missing

    if missing or not rows:
        report["notes"].append(
            "Missing required columns or empty file; nothing further to scan."
        )
        report["verdict"] = UNUSABLE
        return report

    open_k = header_map["open"]
    high_k = header_map["high"]
    low_k = header_map["low"]
    close_k = header_map["close"]

    timestamps: List[datetime] = []
    invalid_ohlc = 0
    aware_seen = False
    naive_seen = False

    for row in rows:
        ts = _try_ts(row.get(ts_key))
        o = _try_float(row.get(open_k))
        h = _try_float(row.get(high_k))
        lo = _try_float(row.get(low_k))
        c = _try_float(row.get(close_k))

        if ts is not None:
            timestamps.append(ts)
            if ts.tzinfo is not None and ts.utcoffset() is not None:
                aware_seen = True
            else:
                naive_seen = True

        bad = (
            o is None or h is None or lo is None or c is None
            or h < lo
            or h < max(o, c)
            or lo > min(o, c)
            or o <= 0 or h <= 0 or lo <= 0 or c <= 0
        )
        if bad:
            invalid_ohlc += 1

    report["invalid_ohlc_rows"] = invalid_ohlc
    report["timezone_aware"] = bool(aware_seen and not naive_seen)
    if aware_seen and naive_seen:
        report["notes"].append("Mixed tz-aware and tz-naive timestamps present.")

    if not timestamps:
        report["notes"].append("No parseable timestamps; dataset unusable.")
        report["verdict"] = UNUSABLE
        return report

    timestamps.sort()
    report["first_timestamp"] = timestamps[0].isoformat()
    report["last_timestamp"] = timestamps[-1].isoformat()

    # Duplicate timestamps: count of extra occurrences beyond the first.
    counts = Counter(timestamps)
    report["duplicate_timestamps"] = sum(n - 1 for n in counts.values() if n > 1)

    # Distinct calendar dates and regime spread (years / months).
    distinct_dates = sorted({t.date() for t in timestamps})
    report["distinct_dates"] = len(distinct_dates)
    report["distinct_years"] = len({d.year for d in distinct_dates})
    report["distinct_months"] = len({(d.year, d.month) for d in distinct_dates})

    # Estimated bar interval: most common gap between consecutive unique stamps.
    uniq = sorted(counts.keys())
    if len(uniq) >= 2:
        gaps = Counter()
        for a, b in zip(uniq, uniq[1:]):
            delta_min = int(round((b - a).total_seconds() / 60.0))
            if delta_min > 0:
                gaps[delta_min] += 1
        if gaps:
            report["estimated_bar_interval_minutes"] = gaps.most_common(1)[0][0]

    interval = report["estimated_bar_interval_minutes"] or 1
    expected_rth_bars = max(1, (end_m - start_m) // interval + 1)

    # Per-date session coverage + eligibility for an opening-range trade.
    by_date: Dict[Any, List[datetime]] = {}
    for t in timestamps:
        by_date.setdefault(t.date(), []).append(t)

    coverage_fractions: List[float] = []
    eligible = 0
    warnings: List[str] = []

    for d in distinct_dates:
        day_stamps = by_date[d]
        in_window = [
            t for t in day_stamps if start_m <= _minutes_of(t.time()) <= end_m
        ]
        coverage = len(in_window) / expected_rth_bars if expected_rth_bars else 0.0
        coverage_fractions.append(coverage)

        or_bars = [t for t in in_window if _minutes_of(t.time()) < or_end_m]
        post_bars = [t for t in in_window if _minutes_of(t.time()) >= or_end_m]
        if or_bars and post_bars:
            eligible += 1

        if in_window and coverage < 0.5:
            warnings.append(
                f"{d.isoformat()}: thin/short session "
                f"({len(in_window)}/{expected_rth_bars} RTH bars, "
                f"{coverage * 100:.0f}% coverage)"
            )
        elif not in_window:
            warnings.append(
                f"{d.isoformat()}: no bars inside RTH window (likely holiday/closed)"
            )

    report["eligible_rth_sessions"] = eligible
    report["thin_session_warnings"] = warnings
    report["session_coverage_pct_avg"] = round(
        (sum(coverage_fractions) / len(coverage_fractions) * 100.0)
        if coverage_fractions else 0.0,
        2,
    )

    # Readiness ladder.
    no_major_errors = bool(invalid_ohlc == 0 and report["duplicate_timestamps"] == 0)
    plumbing = bool(report["row_count"] > 0 and eligible >= 1)
    smoke = bool(plumbing and report["timezone_aware"] and eligible >= 1)
    serious = bool(
        eligible >= SERIOUS_RESEARCH_MIN_SESSIONS
        and report["required_columns_present"]
        and no_major_errors
    )
    # Profitability needs regime spread on top of a high session count: a single
    # rich year is still one regime and must not be called profitability-grade.
    regime_spread = bool(
        report["distinct_years"] >= PROFITABILITY_MIN_DISTINCT_YEARS
        or report["distinct_months"] >= PROFITABILITY_MIN_DISTINCT_MONTHS
    )
    profit = bool(
        serious
        and eligible >= PROFITABILITY_MIN_SESSIONS
        and regime_spread
        and no_major_errors
    )

    report["readiness"] = {
        "plumbing_test": plumbing,
        "smoke_test": smoke,
        "serious_research": serious,
        "profitability_conclusion": profit,
    }

    if not plumbing:
        report["verdict"] = UNUSABLE
    elif not serious:
        report["verdict"] = NEEDS_MORE_DATA
    elif not profit:
        report["verdict"] = RESEARCH_OK_NOT_PROFITABILITY
    else:
        report["verdict"] = PROFITABILITY_GRADE

    return report


def render_markdown(report: Dict[str, Any]) -> str:
    """Render an inert human-readable data-quality report."""
    r = report
    rd = r["readiness"]
    lines = [
        "# Data Quality Scan",
        "",
        f"- file_path: `{r['file_path']}`",
        f"- timestamp_column: `{r['timestamp_column']}`",
        f"- row_count: {r['row_count']}",
        f"- first_timestamp: {r['first_timestamp']}",
        f"- last_timestamp: {r['last_timestamp']}",
        f"- required_columns_present: {r['required_columns_present']}",
        f"- missing_columns: {r['missing_columns']}",
        f"- duplicate_timestamps: {r['duplicate_timestamps']}",
        f"- invalid_ohlc_rows: {r['invalid_ohlc_rows']}",
        f"- timezone_aware: {r['timezone_aware']}",
        f"- distinct_dates: {r['distinct_dates']}",
        f"- distinct_years: {r['distinct_years']}",
        f"- distinct_months: {r['distinct_months']}",
        f"- estimated_bar_interval_minutes: {r['estimated_bar_interval_minutes']}",
        f"- session_window_utc: {r['session_window_utc']}",
        f"- session_coverage_pct_avg: {r['session_coverage_pct_avg']}",
        f"- eligible_rth_sessions: {r['eligible_rth_sessions']}",
        "",
        "## Readiness",
        f"- plumbing_test: {rd['plumbing_test']}",
        f"- smoke_test: {rd['smoke_test']}",
        f"- serious_research: {rd['serious_research']}",
        f"- profitability_conclusion: {rd['profitability_conclusion']}",
        "",
        f"## Verdict: **{r['verdict']}**",
        "",
        "## Thin / holiday-thin session warnings",
    ]
    if r["thin_session_warnings"]:
        lines.extend(f"- {w}" for w in r["thin_session_warnings"])
    else:
        lines.append("- none")
    if r["notes"]:
        lines.append("")
        lines.append("## Notes")
        lines.extend(f"- {n}" for n in r["notes"])
    lines.append("")
    return "\n".join(lines)

"""Input validator for s7 D1 cross-asset daily-bar LoadedSymbol structures.

Pure in-memory checker over the output of the Step 03 canonical loader.
Confirms that a LoadedSymbol (or a dict-of-LoadedSymbol from load_all())
is fit-for-purpose for downstream channel-construction phases, without
itself computing any channel, any rolling statistic, any per-day return,
any cross-asset dependence measure, or any signal-side quantity. (See
the Step 04 spec section 14 for the full forbidden-computation list.)

This module performs NO file IO. It does not call the loader; the caller
loads first and passes the result. It contains no network code, no
vendor SDK, no signal logic, and no in-line OOS numerical inspection.
For the out-of-sample and post-out-of-sample windows, this module
records ONLY bar counts and first/last date coverage; never min/max,
never percentiles, never returns, never any pairwise dependence value.
This preserves the parent spec section 11 invariant that out-of-sample
data must not be inspected until the in-sample run produces a verdict
that authorizes out-of-sample access.

Refusal modes (ValidatorError tree):

  - ValidatorInputError - input is not a LoadedSymbol, or LoadedSymbol
    is structurally invalid (wrong bar count, bad symbol, non-positive
    in-sample price, negative volume).
  - WarmupInsufficientError - fewer than DONCHIAN_ENTRY_LOOKBACK prior
    loaded bars exist before the first in-sample-window bar.
  - WindowMisfitError - a window has zero bars or end < start.
  - ValidatorCrossSymbolAlignmentError - cross-symbol date sets do not
    match (validate_all path).
  - ValidatorError - base class; also raised for any other refusal.

Spec anchor:
  docs/s7_d1_cross_asset_donchian_step_04_input_validator_specification_plan.md
  sha256 c1aad410b50e132540f66ee7c973048967b4f36a3cb0872bb5d55f25683466da
  commit a5acf59f497897c0c579b584e287f0e44139e337
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

# -- Public constants ----------------------------------------------------
DONCHIAN_ENTRY_LOOKBACK = 55
DONCHIAN_EXIT_LOOKBACK = 20

IN_SAMPLE_WINDOW = ("2013-01-01", "2022-12-30")
OUT_OF_SAMPLE_WINDOW = ("2023-01-01", "2025-12-30")
POST_OOS_DIAGNOSTIC_WINDOW = ("2026-01-02", "2026-05-22")

_ALLOWED_SYMBOLS = frozenset({"SPY", "TLT", "GLD", "USO"})
_EXPECTED_BAR_COUNT_TOTAL = 3116
_ALLOWED_VERDICTS = ("PASS", "PASS_WITH_WARMUP_TRUNCATION", "FAIL")


# -- Exception tree ------------------------------------------------------
class ValidatorError(Exception):
    """Base for every validator refusal mode."""


class ValidatorInputError(ValidatorError):
    """Input not a LoadedSymbol or LoadedSymbol structurally invalid."""


class WarmupInsufficientError(ValidatorError):
    """Fewer than DONCHIAN_ENTRY_LOOKBACK prior loaded bars exist."""


class WindowMisfitError(ValidatorError):
    """A window has zero bars or end-date < start-date."""


class ValidatorCrossSymbolAlignmentError(ValidatorError):
    """Cross-symbol date set mismatch (validate_all path only)."""


# -- Report dataclasses (immutable) --------------------------------------
@dataclass(frozen=True)
class ValidationReport:
    """Per-symbol validation outcome."""
    symbol: str
    csv_sha256_observed: str
    bar_count_total: int
    date_first: str
    date_last: str
    bar_count_in_in_sample_window: int
    bar_count_in_oos_window: int
    bar_count_in_post_oos_window: int
    warmup_bars_available_before_first_in_sample_signal_eligible_bar: int
    first_in_sample_signal_eligible_index: int
    first_in_sample_signal_eligible_date: str
    warmup_truncation_at_data_start: bool
    in_sample_volume_summary: Mapping[str, Any]
    in_sample_close_summary: Mapping[str, Any]
    in_sample_adj_close_summary: Mapping[str, Any]
    oos_summary_intentionally_omitted: bool
    post_oos_summary_intentionally_omitted: bool
    check_results: Mapping[str, Any]
    verdict: str


@dataclass(frozen=True)
class CrossSymbolValidationReport:
    """Portfolio-level validation outcome over the four-symbol set."""
    per_symbol: Mapping[str, ValidationReport]
    cross_symbol_dates_aligned: bool
    cross_symbol_bar_count_equal: bool
    cross_symbol_in_sample_bar_count_equal: bool
    cross_symbol_oos_bar_count_equal: bool
    check_results: Mapping[str, Any]
    portfolio_verdict: str


# -- Private helpers -----------------------------------------------------
def _looks_like_loaded_symbol(obj: Any) -> bool:
    """Duck-type check: object exposes the LoadedSymbol fields the
    validator reads. We avoid an explicit isinstance() to keep the
    validator decoupled from the loader module path; tests can pass
    structural-equivalents."""
    return all(
        hasattr(obj, attr)
        for attr in (
            "symbol", "dates", "open", "high", "low",
            "close", "adj_close", "volume",
            "csv_path", "csv_sha256",
        )
    )


def _median(xs):
    """Return median of a non-empty iterable of comparable values."""
    s = sorted(xs)
    n = len(s)
    if n == 0:
        raise ValueError("median of empty sequence")
    if n % 2 == 1:
        return s[n // 2]
    return 0.5 * (s[n // 2 - 1] + s[n // 2])


def _count_in_window(dates: tuple, window: tuple) -> tuple[int, int, int]:
    """Return (count, first_index_in_window_or_-1, last_index_in_window_or_-1).
    Inclusive on both window bounds. Iterates once."""
    lo, hi = window
    first_idx = -1
    last_idx = -1
    count = 0
    for i, d in enumerate(dates):
        if lo <= d <= hi:
            count += 1
            if first_idx == -1:
                first_idx = i
            last_idx = i
    return count, first_idx, last_idx


# -- Public API ----------------------------------------------------------
def validate_loaded_symbol(loaded: Any) -> ValidationReport:
    """Validate one LoadedSymbol. Returns ValidationReport on PASS or
    PASS_WITH_WARMUP_TRUNCATION; raises ValidatorError subclass on
    structural refusal.
    """
    # Input type
    if not _looks_like_loaded_symbol(loaded):
        raise ValidatorInputError(
            f"input does not look like a LoadedSymbol (missing fields); "
            f"got type={type(loaded).__name__}"
        )
    # Symbol
    sym = getattr(loaded, "symbol", None)
    if sym not in _ALLOWED_SYMBOLS:
        raise ValidatorInputError(
            f"unknown symbol {sym!r}; expected one of {sorted(_ALLOWED_SYMBOLS)}"
        )
    dates = loaded.dates
    if not isinstance(dates, tuple):
        raise ValidatorInputError(f"dates must be a tuple; got {type(dates).__name__}")

    check_results: dict[str, Any] = {}

    # W1 bar count total
    bar_count_total = len(dates)
    w1_ok = (bar_count_total == _EXPECTED_BAR_COUNT_TOTAL)
    check_results["W1_bar_count_total_equals_expected"] = w1_ok
    if not w1_ok:
        raise ValidatorInputError(
            f"{sym} bar_count_total={bar_count_total} != "
            f"expected {_EXPECTED_BAR_COUNT_TOTAL}"
        )

    # W2 monotonic 10-char ISO dates
    prev = None
    w2_ok = True
    for i, d in enumerate(dates):
        if not isinstance(d, str) or len(d) != 10:
            w2_ok = False
            break
        if prev is not None and not (d > prev):
            w2_ok = False
            break
        prev = d
    check_results["W2_dates_monotonic_iso"] = w2_ok
    if not w2_ok:
        raise ValidatorInputError(f"{sym} dates failed monotonic ISO check")

    # Window scans
    is_count, is_first, is_last = _count_in_window(dates, IN_SAMPLE_WINDOW)
    oos_count, oos_first, oos_last = _count_in_window(dates, OUT_OF_SAMPLE_WINDOW)
    post_count, post_first, post_last = _count_in_window(dates, POST_OOS_DIAGNOSTIC_WINDOW)

    # First in-sample signal-eligible bar = first IS-window-resident loaded
    # bar that has >= DONCHIAN_ENTRY_LOOKBACK prior loaded bars.
    first_eligible_idx = -1
    for i in range(max(is_first, 0), len(dates)):
        if is_first == -1:
            break
        if dates[i] > IN_SAMPLE_WINDOW[1]:
            break
        if i >= DONCHIAN_ENTRY_LOOKBACK:
            first_eligible_idx = i
            break
    warmup_bars_available = first_eligible_idx if first_eligible_idx >= 0 else 0
    first_eligible_date = dates[first_eligible_idx] if first_eligible_idx >= 0 else ""

    # W3 warmup adequacy
    w3_ok = (first_eligible_idx >= DONCHIAN_ENTRY_LOOKBACK and first_eligible_idx >= 0)
    check_results["W3_warmup_bars_at_least_entry_lookback"] = w3_ok
    if not w3_ok:
        raise WarmupInsufficientError(
            f"{sym} first_in_sample_signal_eligible_index={first_eligible_idx} < "
            f"DONCHIAN_ENTRY_LOOKBACK={DONCHIAN_ENTRY_LOOKBACK}; "
            f"insufficient loaded warmup before the first in-sample window bar"
        )

    # W4
    w4_ok = (0 <= first_eligible_idx < bar_count_total)
    check_results["W4_first_eligible_index_in_range"] = w4_ok
    if not w4_ok:
        raise WarmupInsufficientError(
            f"{sym} first_in_sample_signal_eligible_index={first_eligible_idx} "
            f"out of range [0, {bar_count_total})"
        )

    # B1 in-sample bar count
    b1_ok = (is_count >= DONCHIAN_ENTRY_LOOKBACK + 1)
    check_results["B1_in_sample_bar_count_at_least_56"] = b1_ok
    if not b1_ok:
        raise WindowMisfitError(
            f"{sym} bar_count_in_in_sample_window={is_count} < "
            f"DONCHIAN_ENTRY_LOOKBACK+1={DONCHIAN_ENTRY_LOOKBACK + 1}"
        )

    # B2 oos bar count > 0
    b2_ok = (oos_count > 0)
    check_results["B2_oos_bar_count_positive"] = b2_ok
    if not b2_ok:
        raise WindowMisfitError(
            f"{sym} bar_count_in_oos_window={oos_count} <= 0 "
            f"for OUT_OF_SAMPLE_WINDOW={OUT_OF_SAMPLE_WINDOW}"
        )

    # B3 informational
    check_results["B3_post_oos_bar_count_recorded"] = True

    # S1-S4 in-sample summaries (in-sample window ONLY)
    is_slice_close = [loaded.close[i] for i in range(len(dates))
                      if IN_SAMPLE_WINDOW[0] <= dates[i] <= IN_SAMPLE_WINDOW[1]]
    is_slice_adj   = [loaded.adj_close[i] for i in range(len(dates))
                      if IN_SAMPLE_WINDOW[0] <= dates[i] <= IN_SAMPLE_WINDOW[1]]
    is_slice_vol   = [loaded.volume[i] for i in range(len(dates))
                      if IN_SAMPLE_WINDOW[0] <= dates[i] <= IN_SAMPLE_WINDOW[1]]

    in_sample_close_summary = {
        "min": min(is_slice_close) if is_slice_close else None,
        "max": max(is_slice_close) if is_slice_close else None,
    }
    in_sample_adj_close_summary = {
        "min": min(is_slice_adj) if is_slice_adj else None,
        "max": max(is_slice_adj) if is_slice_adj else None,
    }
    in_sample_volume_summary = {
        "min": min(is_slice_vol) if is_slice_vol else None,
        "median": _median(is_slice_vol) if is_slice_vol else None,
        "max": max(is_slice_vol) if is_slice_vol else None,
        "zero_volume_day_count": sum(1 for v in is_slice_vol if v == 0),
    }

    # S1 / S2 / S3 / S4
    s1_ok = (in_sample_close_summary["min"] is not None
             and in_sample_close_summary["min"] > 0
             and in_sample_close_summary["max"] is not None)
    check_results["S1_in_sample_close_positive_and_finite"] = s1_ok
    if not s1_ok:
        raise ValidatorInputError(f"{sym} in-sample close summary failed S1")
    s2_ok = (in_sample_adj_close_summary["min"] is not None
             and in_sample_adj_close_summary["min"] > 0
             and in_sample_adj_close_summary["max"] is not None)
    check_results["S2_in_sample_adj_close_positive_and_finite"] = s2_ok
    if not s2_ok:
        raise ValidatorInputError(f"{sym} in-sample adj_close summary failed S2")
    s3_ok = (in_sample_volume_summary["min"] is not None
             and in_sample_volume_summary["min"] >= 0
             and in_sample_volume_summary["max"] is not None)
    check_results["S3_in_sample_volume_nonneg_and_finite"] = s3_ok
    if not s3_ok:
        raise ValidatorInputError(f"{sym} in-sample volume summary failed S3")
    check_results["S4_zero_volume_day_count_recorded"] = True

    # G1 no duplicate dates (re-confirmation; loader already enforces)
    g1_ok = (len(set(dates)) == len(dates))
    check_results["G1_no_duplicate_dates"] = g1_ok
    if not g1_ok:
        raise ValidatorInputError(f"{sym} duplicate dates found")

    # G2 calendar-date parseability
    import datetime as _d
    g2_ok = True
    try:
        for d_str in dates:
            _d.date.fromisoformat(d_str)
    except ValueError:
        g2_ok = False
    check_results["G2_dates_parse_as_calendar_dates"] = g2_ok
    if not g2_ok:
        raise ValidatorInputError(f"{sym} a date failed calendar-date parse")

    # G3 gap diagnostic (recorded; not a HALT)
    # Count weekdays between first IS-resident date and last IS-resident date
    if is_first >= 0 and is_last >= 0:
        f = _d.date.fromisoformat(dates[is_first])
        l = _d.date.fromisoformat(dates[is_last])
        weekday_count = 0
        cur = f
        while cur <= l:
            if cur.weekday() < 5:
                weekday_count += 1
            cur = cur + _d.timedelta(days=1)
        gap = weekday_count - is_count
    else:
        weekday_count = 0
        gap = 0
    check_results["G3_in_sample_weekday_gap_recorded"] = True
    check_results["G3_in_sample_weekday_count"] = weekday_count
    check_results["G3_in_sample_observed_sessions"] = is_count
    check_results["G3_in_sample_holiday_estimate_gap"] = gap

    # warmup_truncation_at_data_start
    warmup_truncation_at_data_start = (dates[0] > IN_SAMPLE_WINDOW[0])

    # Verdict
    if warmup_truncation_at_data_start:
        verdict = "PASS_WITH_WARMUP_TRUNCATION"
    else:
        verdict = "PASS"

    return ValidationReport(
        symbol=sym,
        csv_sha256_observed=loaded.csv_sha256,
        bar_count_total=bar_count_total,
        date_first=dates[0],
        date_last=dates[-1],
        bar_count_in_in_sample_window=is_count,
        bar_count_in_oos_window=oos_count,
        bar_count_in_post_oos_window=post_count,
        warmup_bars_available_before_first_in_sample_signal_eligible_bar=warmup_bars_available,
        first_in_sample_signal_eligible_index=first_eligible_idx,
        first_in_sample_signal_eligible_date=first_eligible_date,
        warmup_truncation_at_data_start=warmup_truncation_at_data_start,
        in_sample_volume_summary=in_sample_volume_summary,
        in_sample_close_summary=in_sample_close_summary,
        in_sample_adj_close_summary=in_sample_adj_close_summary,
        oos_summary_intentionally_omitted=True,
        post_oos_summary_intentionally_omitted=True,
        check_results=check_results,
        verdict=verdict,
    )


def validate_all(data: Mapping[str, Any]) -> CrossSymbolValidationReport:
    """Validate the four-symbol portfolio. Calls validate_loaded_symbol
    on each then performs cross-symbol checks.
    """
    check_results: dict[str, Any] = {}

    # A1: exactly four allowed keys
    if not isinstance(data, Mapping):
        raise ValidatorInputError(f"validate_all input must be a Mapping; got {type(data).__name__}")
    a1_ok = (set(data.keys()) == _ALLOWED_SYMBOLS)
    check_results["A1_four_allowed_keys"] = a1_ok
    if not a1_ok:
        raise ValidatorInputError(
            f"validate_all keys {sorted(data.keys())} != "
            f"expected {sorted(_ALLOWED_SYMBOLS)}"
        )

    # Per-symbol validation (raises on any per-symbol failure)
    per_symbol: dict[str, ValidationReport] = {}
    for sym in sorted(_ALLOWED_SYMBOLS):
        per_symbol[sym] = validate_loaded_symbol(data[sym])

    # A2 bar count equal
    counts = {s: r.bar_count_total for s, r in per_symbol.items()}
    a2_ok = (len(set(counts.values())) == 1)
    check_results["A2_bar_count_equal"] = a2_ok
    if not a2_ok:
        raise ValidatorCrossSymbolAlignmentError(
            f"bar_count_total varies across symbols: {counts}"
        )

    # A3 cross-symbol date set aligned
    sets = {s: frozenset(data[s].dates) for s in sorted(_ALLOWED_SYMBOLS)}
    canonical = None
    canonical_sym = None
    a3_ok = True
    for s in sorted(_ALLOWED_SYMBOLS):
        if canonical is None:
            canonical = sets[s]
            canonical_sym = s
        elif sets[s] != canonical:
            a3_ok = False
            diff = sorted(sets[s] ^ canonical)[:10]
            check_results["A3_first_misalignment_diff"] = {
                "symbol": s,
                "canonical_symbol": canonical_sym,
                "first_10_symmetric_differences": diff,
            }
            break
    check_results["A3_cross_symbol_dates_aligned"] = a3_ok
    if not a3_ok:
        raise ValidatorCrossSymbolAlignmentError(
            f"cross-symbol date set mismatch: see check_results A3"
        )

    # A4 / A5 bar counts equal in each window
    is_counts = {s: r.bar_count_in_in_sample_window for s, r in per_symbol.items()}
    oos_counts = {s: r.bar_count_in_oos_window for s, r in per_symbol.items()}
    a4_ok = (len(set(is_counts.values())) == 1)
    a5_ok = (len(set(oos_counts.values())) == 1)
    check_results["A4_in_sample_bar_count_equal"] = a4_ok
    check_results["A5_oos_bar_count_equal"] = a5_ok
    if not a4_ok:
        raise ValidatorCrossSymbolAlignmentError(
            f"in-sample bar counts vary: {is_counts}"
        )
    if not a5_ok:
        raise ValidatorCrossSymbolAlignmentError(
            f"oos bar counts vary: {oos_counts}"
        )

    # A6 portfolio verdict roll-up
    per_verdicts = [r.verdict for r in per_symbol.values()]
    if any(v == "FAIL" for v in per_verdicts):
        portfolio_verdict = "FAIL"
    elif any(v == "PASS_WITH_WARMUP_TRUNCATION" for v in per_verdicts):
        portfolio_verdict = "PASS_WITH_WARMUP_TRUNCATION"
    else:
        portfolio_verdict = "PASS"
    check_results["A6_portfolio_verdict_rollup"] = portfolio_verdict

    return CrossSymbolValidationReport(
        per_symbol=per_symbol,
        cross_symbol_dates_aligned=a3_ok,
        cross_symbol_bar_count_equal=a2_ok,
        cross_symbol_in_sample_bar_count_equal=a4_ok,
        cross_symbol_oos_bar_count_equal=a5_ok,
        check_results=check_results,
        portfolio_verdict=portfolio_verdict,
    )

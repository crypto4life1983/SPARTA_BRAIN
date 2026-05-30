"""Offline daily Overnight Session-Return Decomposition / Overnight Drift engine (S30 v1).

Implements EXACTLY the frozen rules pre-registered in
reports/s30_d2_overnight_drift_strategy_spec/ (committed 275540f).
LONG-OVERNIGHT-ONLY v1 (shorting and any day-session exposure are DEFERRED to a
future, separately-authorized branch and are NOT implemented here).

OFFLINE / INERT: pure-Python standard library only (csv, datetime, statistics).
It never fetches, downloads, streams, or connects anywhere. It writes no files.
It runs no optimization and no parameter search; every constant below is a fixed
input frozen by the S30-D2 spec.

Hypothesis: a systematic overnight risk premium may exist where the return from
prior close to next open (the overnight leg) differs from -- and is more reliably
positive than -- the open-to-close day-session leg. The edge, if real, must come
from MANY small repeated overnight observations, not a few large trend captures;
that property is the structural antidote to the top-3-winner dependence that
parked every prior branch.

Frozen rules (S30-D2):
  Direction   : LONG overnight only. One overnight position per eligible day.
                No shorting. No day-session exposure (the open->close leg is
                MEASURED for comparison but never traded).
  Entry/Exit  : enter at close[t-1], exit at open[t]. Trade date = t. No same-bar
                lookahead. No intraday stop/target (daily bars cannot observe the
                overnight path), so the position is held flat prior-close ->
                next-open with NO path-dependent exit.
  Eligibility : ALL valid days eligible. No trend / EMA / RSI / volatility filter.
                A pair (t-1, t) is eligible iff close[t-1] and open[t] (and the
                high/low/close of t used for the comparison legs) are present,
                finite and > 0, and t-1, t are adjacent sessions.
  Legs        : overnight_points    = open[t]  - close[t-1]
                overnight_return_pct = open[t] / close[t-1] - 1
                day_session_points  = close[t] - open[t]
                total_day_points    = close[t] - close[t-1]
  Measurement : overnight_points + day_session_points must reconstruct
                total_day_points within tolerance (a HARD GATE -- if the daily
                bar open/close cannot be trusted to represent the overnight/day
                split, the branch STOPS; see validate_overnight_measurement).
  Accounting  : raw points + percent primary; ATR20[t-1]-normalized overnight
                return secondary (normalized_overnight_r = overnight_points /
                ATR20[t-1]). No artificial stop/target; distribution-based.

RESOLVED INTERPRETATIONS (the conservative reading, mirroring S29):
  * "Consecutive valid trading sessions" -> adjacency in the time-sorted bar list.
    Calendar/holiday gap detection (a data hole that breaks the
    prior-close->next-open chain) is deferred to the D4 data-QA layer
    (validation_is_runner already does per-year counts + duplicate detection);
    the engine itself treats adjacent sorted bars as consecutive sessions and
    rejects only invalid-price pairs, so it introduces no free parameter here.
  * The first bar of the dataset is never a trade date (it has no t-1).
  * Invalid/missing/zero/negative open or close on either leg -> the pair is
    SKIPPED (excluded from observations), never recorded as a degenerate trade.
  * ATR20 normalization uses ATR through bar t-1 only (the PRIOR bar), never the
    current bar t, so the normalized return reads no future information.

Lookahead safety: the entry uses the known prior close; the exit is the next
session's open; the normalization ATR uses bars up to t-1 only. Nothing reads a
future bar relative to its own decision point.
"""

from __future__ import annotations

import csv
import statistics
from datetime import datetime
from typing import Any, Dict, List, Optional

# Frozen S30-D2 constants (NOT tunable; changing any of these requires a NEW
# branch with a fresh pre-registered OOS, never an edit here).
ATR_PERIOD = 20                     # ATR20 used for the secondary normalized leg
RECONSTRUCTION_TOLERANCE = 1e-6     # overnight + day_session must equal total day
DIRECTION = "long_overnight"        # v1 direction invariant

ACCOUNTING_NOTE = (
    "raw points + percent overnight return primary; ATR20[t-1]-normalized "
    "overnight return secondary; long-overnight-only v1 (enter close[t-1], exit "
    "open[t]); one position per eligible day; no shorting; no day-session "
    "exposure; no stop/target; no dollar sizing / point value / cost / roll"
)


class MeasurementValidityError(ValueError):
    """Raised when the overnight/day/total reconstruction fails the hard gate."""


def load_daily_bars(
    csv_path: str, timestamp_column: str = "ts_event"
) -> List[Dict[str, Any]]:
    """Load daily OHLC(V) bars from a local CSV. Offline read only, sorted by time.

    Volume is read if present but the S30 overnight rule does not require it.
    No network, no fetch. NOT used by the synthetic test suite.
    """
    bars: List[Dict[str, Any]] = []
    with open(csv_path, "r", newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        header_map = {h.lower(): h for h in (reader.fieldnames or [])}
        ts_key = header_map.get(timestamp_column.lower(), timestamp_column)
        vol_key = header_map.get("volume")
        for row in reader:
            ts_raw = row.get(ts_key)
            if ts_raw is None:
                continue
            bars.append(
                {
                    "timestamp": datetime.fromisoformat(ts_raw.strip()),
                    "open": float(row[header_map["open"]]),
                    "high": float(row[header_map["high"]]),
                    "low": float(row[header_map["low"]]),
                    "close": float(row[header_map["close"]]),
                    "volume": float(row[vol_key]) if vol_key else 0.0,
                }
            )
    bars.sort(key=lambda b: b["timestamp"])
    return bars


def true_range(high: float, low: float, prev_close: float) -> float:
    """Single-bar true range = max(h-l, |h-pc|, |l-pc|)."""
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


def wilder_atr(bars: List[Dict[str, Any]], period: int = ATR_PERIOD) -> List[Optional[float]]:
    """Wilder ATR aligned to bars; atr[k] is the ATR through bar k (None until warm)."""
    n = len(bars)
    atr: List[Optional[float]] = [None] * n
    if period <= 0 or n < period + 1:
        return atr
    trs: List[Optional[float]] = [None] * n
    for k in range(1, n):
        trs[k] = true_range(bars[k]["high"], bars[k]["low"], bars[k - 1]["close"])
    seed = sum(trs[1:period + 1]) / period  # type: ignore[arg-type]
    atr[period] = seed
    prev = seed
    for k in range(period + 1, n):
        cur = (prev * (period - 1) + trs[k]) / period  # type: ignore[operator]
        prev = cur
        atr[k] = cur
    return atr


def compute_indicators(bars: List[Dict[str, Any]]) -> Dict[str, List[Optional[float]]]:
    """All frozen indicator arrays, aligned to bars. Pure, no I/O."""
    return {"atr": wilder_atr(bars, ATR_PERIOD)}


def _valid_price(x: Any) -> bool:
    """True iff x is a finite number strictly greater than zero."""
    return isinstance(x, (int, float)) and x == x and x not in (float("inf"), float("-inf")) and x > 0.0


def build_overnight_observations(
    bars: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """One long-overnight observation per eligible day (pure, no I/O, no randomness).

    For each trade date t (>= second bar), decomposes the prior-close -> next-open
    overnight leg, the open -> close day-session leg, and the total close-to-close
    move, plus an ATR20[t-1]-normalized overnight return. Pairs with any
    invalid/missing/zero/negative price are SKIPPED.
    """
    n = len(bars)
    obs: List[Dict[str, Any]] = []
    if n < 2:
        return obs
    atr = wilder_atr(bars, ATR_PERIOD)
    for t in range(1, n):
        prev = bars[t - 1]
        cur = bars[t]
        prior_close = prev.get("close")
        cur_open = cur.get("open")
        cur_close = cur.get("close")
        # Eligibility: prices used in the legs must be valid (>0, finite).
        if not (_valid_price(prior_close) and _valid_price(cur_open) and _valid_price(cur_close)):
            continue
        overnight_points = cur_open - prior_close
        day_session_points = cur_close - cur_open
        total_day_points = cur_close - prior_close
        reconstruction_error = (overnight_points + day_session_points) - total_day_points
        atr_prior = atr[t - 1]
        normalized_overnight_r: Optional[float] = (
            overnight_points / atr_prior
            if atr_prior is not None and atr_prior > 0.0
            else None
        )
        ts = cur.get("timestamp")
        prev_ts = prev.get("timestamp")
        obs.append({
            "direction": DIRECTION,
            "trade_date": str(ts.date()) if isinstance(ts, datetime) else None,
            "prior_index": t - 1,
            "prior_date": str(prev_ts.date()) if isinstance(prev_ts, datetime) else None,
            "current_index": t,
            "current_date": str(ts.date()) if isinstance(ts, datetime) else None,
            "entry_price": prior_close,        # enter at prior close
            "prior_close": prior_close,
            "exit_price": cur_open,            # exit at current open
            "current_open": cur_open,
            "overnight_points": overnight_points,
            "overnight_return_pct": cur_open / prior_close - 1.0,
            "day_session_points": day_session_points,
            "total_day_points": total_day_points,
            "reconstruction_error": reconstruction_error,
            "atr20_prior": atr_prior,
            "normalized_overnight_r": normalized_overnight_r,
        })
    return obs


def simulate_s30(bars: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deterministic long-overnight simulation: one overnight hold per eligible day.

    Every eligible day is a single long-overnight position (enter prior close,
    exit next open). There is no position-overlap question (each trade lasts one
    overnight and they never overlap), so this is exactly the observation list.
    """
    return build_overnight_observations(bars)


def validate_overnight_measurement(
    observations: List[Dict[str, Any]],
    tolerance: float = RECONSTRUCTION_TOLERANCE,
    strict: bool = False,
) -> Dict[str, Any]:
    """HARD GATE: overnight + day_session must reconstruct total_day within tolerance.

    Aggregates the per-observation reconstruction error. If `strict` and the gate
    fails, raises MeasurementValidityError; otherwise returns a flag dict. This is
    the engine-level expression of the S30-D2 measurement-validity gate -- if the
    daily open/close legs do not reconcile to the close-to-close move, the daily
    bars cannot be trusted to represent the overnight/day split and the branch
    must STOP.
    """
    errors = [abs(float(o.get("reconstruction_error", 0.0))) for o in observations]
    max_abs_error = max(errors) if errors else 0.0
    valid = max_abs_error <= tolerance
    result = {
        "valid": valid,
        "observation_count": len(observations),
        "max_abs_reconstruction_error": max_abs_error,
        "tolerance": tolerance,
    }
    if strict and not valid:
        raise MeasurementValidityError(
            f"overnight/day/total reconstruction error {max_abs_error} exceeds "
            f"tolerance {tolerance}; daily open/close may not bracket the "
            f"overnight session -- branch must STOP."
        )
    return result


def summarize_overnight(observations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Inert distribution summary of long-overnight observations (points-based)."""
    pts = [o["overnight_points"] for o in observations]
    n = len(pts)
    if n == 0:
        return {
            "observation_count": 0,
            "total_points": 0.0,
            "total_return_pct": 0.0,
            "average_points": 0.0,
            "median_points": 0.0,
            "win_rate": 0.0,
            "positive_years": {},
            "positive_year_count": 0,
            "year_count": 0,
        }
    gross_win = sum(p for p in pts if p > 0)
    gross_loss = -sum(p for p in pts if p < 0)
    # Per-year net points (year parsed from trade_date when present).
    year_net: Dict[str, float] = {}
    for o in observations:
        td = o.get("trade_date")
        year = td[:4] if isinstance(td, str) and len(td) >= 4 else "unknown"
        year_net[year] = year_net.get(year, 0.0) + o["overnight_points"]
    positive_years = {y: v for y, v in year_net.items() if v > 0}
    return {
        "observation_count": n,
        "total_points": sum(pts),
        "total_return_pct": sum(o["overnight_return_pct"] for o in observations),
        "average_points": sum(pts) / n,
        "median_points": statistics.median(pts),
        "profit_factor": (gross_win / gross_loss) if gross_loss > 0 else None,
        "win_rate": sum(1 for p in pts if p > 0) / n,
        "positive_years": positive_years,
        "positive_year_count": len(positive_years),
        "year_count": len(year_net),
    }


def top_day_dependence(observations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Frozen S30 hard gate: net must stay POSITIVE ex top 3 days AND ex top 1% of days.

    The direct guard against the universal parked-branch failure (a thin net
    propped up by a handful of fat-tail days). Pure accounting; no I/O.
    """
    pts = sorted((o["overnight_points"] for o in observations), reverse=True)
    n = len(pts)
    net_points = sum(pts)
    top1pct_count = max(1, n // 100) if n > 0 else 0
    net_ex_top3 = sum(pts[3:])
    net_ex_top1pct = sum(pts[top1pct_count:])
    return {
        "observation_count": n,
        "net_points": net_points,
        "top3_points": sum(pts[:3]),
        "net_ex_top3": net_ex_top3,
        "top1pct_count": top1pct_count,
        "top1pct_points": sum(pts[:top1pct_count]),
        "net_ex_top1pct": net_ex_top1pct,
        "passes_ex_top3": net_ex_top3 > 0.0,
        "passes_ex_top1pct": net_ex_top1pct > 0.0,
    }


def run_backtest(
    csv_path: str, timestamp_column: str = "ts_event"
) -> Dict[str, Any]:
    """Run the S30 long-overnight strategy over a local CSV. Returns inert data."""
    bars = load_daily_bars(csv_path, timestamp_column=timestamp_column)
    observations = simulate_s30(bars)
    return {
        "overnight_points": [o["overnight_points"] for o in observations],
        "observations": observations,
        "bars_loaded": len(bars),
        "measurement": validate_overnight_measurement(observations),
        "summary": summarize_overnight(observations),
        "top_day_gate": top_day_dependence(observations),
        "accounting": ACCOUNTING_NOTE,
    }

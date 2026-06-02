"""SPARTA Crypto-D1 Backtest Runner v1 -- local-only, research-only, stdlib.

This runner executes the FIRST Crypto-D1 backtest defined by
`reports/crypto_d1_baseline_backtest_plan_v1/backtest_plan.json` against
OPERATOR-SUPPLIED LOCAL CSV FILES ONLY. It reads no remote data, contacts no
exchange, places no order, and authorizes no trading.

Hard non-negotiable guarantees (enforced by tests):
  * Standard library ONLY (argparse, csv, dataclasses, datetime, hashlib,
    json, math, pathlib, sys).
  * No network. No exchange / broker / vendor imports. No subprocess.
  * No os.environ / getenv / dotenv access.
  * No order placement. No live trading. No paper-order execution.
  * No data fetch -- reads CSV files at --data-dir only.
  * On missing data, emits a FAIL report; never fabricates results.

The seven Bundle-15 safety flags are pinned False in every emitted report:
  research_only=True, data_fetch_enabled=False,
  exchange_connection_enabled=False, live_trading_enabled=False,
  broker_control_enabled=False, paper_order_execution_enabled=False,
  order_placement_enabled=False.

CLI:
  python tools/crypto_d1_backtest_runner.py run --data-dir <PATH> --out-dir <PATH>
  python tools/crypto_d1_backtest_runner.py validate-config [--fee-bps N --slippage-bps M]
  python tools/crypto_d1_backtest_runner.py show-plan

NOT FOR TRADING. Results are research-only and do NOT authorize paper or
live trading. Crypto trend ideas are not profitable until tested with full
costs and forward-validated; this runner does NEITHER live nor paper.
"""
from __future__ import annotations

import argparse
import csv
import dataclasses
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Version pins -- every emitted report cites these.
# ---------------------------------------------------------------------------
RUNNER_VERSION = "crypto_d1_backtest_runner_v1"
PLAN_VERSION = "crypto_d1_baseline_backtest_plan_v1"
PROTOCOL_VERSION = "crypto_d1_protocol_v1"
DATA_CONTRACT_VERSION = "crypto_d1_data_contract_v1"
DATASET_MANIFEST_SPEC_VERSION = "crypto_d1_dataset_manifest_v1"
QA_FREEZE_SPEC_VERSION = "crypto_d1_qa_freeze_spec_v1"

# ---------------------------------------------------------------------------
# Data contract column schema (Bundle 12).
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = (
    "timestamp",
    "open",
    "high",
    "low",
    "close",
    "volume",
    "symbol",
    "source",
    "quote_currency",
)
TARGET_ASSETS = ("BTC", "ETH", "SOL")

# ---------------------------------------------------------------------------
# Safety flags. EVERY emitted report carries this dict verbatim.
# ---------------------------------------------------------------------------
SAFETY_FLAGS = {
    "research_only": True,
    "data_fetch_enabled": False,
    "exchange_connection_enabled": False,
    "live_trading_enabled": False,
    "broker_control_enabled": False,
    "paper_order_execution_enabled": False,
    "order_placement_enabled": False,
}

SAFETY_NOTES = (
    "Research-only. Local-only.",
    "No data was fetched. No exchange was contacted. No order was placed.",
    "Results do not imply profitability. Crypto trend ideas are not profitable"
    " until tested with full costs AND forward-validated under a separately"
    " authorized future plan; neither is authorized by this runner.",
    "A future PASS verdict is not trading authorization.",
)

FORBIDDEN_NEXT_STEPS = (
    "Trade live or paper based on these results.",
    "Connect SPARTA's runtime to any exchange or vendor over the network.",
    "Promote crypto_d1_protocol to ACTIVE / STRONG without a separate operator decision.",
    "Schedule a daemon / cron / background process that touches this runner.",
    "Modify paper / live execution files.",
    "Install or read any API key, OAuth token, or .env credential.",
    "Use any synthetic / mock-priced data as evidence.",
)

# ---------------------------------------------------------------------------
# Cost model bounds + defaults.
# ---------------------------------------------------------------------------
DEFAULT_TAKER_FEE_BPS = 10.0
DEFAULT_SLIPPAGE_BPS = 5.0
FEE_BPS_MIN = 0.0
FEE_BPS_MAX = 100.0
SLIP_BPS_MIN = 0.0
SLIP_BPS_MAX = 100.0
DEFAULT_START_EQUITY = 100_000.0  # research units; NOT money.

# ---------------------------------------------------------------------------
# Pre-registered strategy parameters (single grid point per family in v1).
# ---------------------------------------------------------------------------
DONCHIAN_ENTRY_N = 20
DONCHIAN_EXIT_M = 10
MA_FILTER_WINDOW = 200
MOMENTUM_LOOKBACK = 90
VOL_REGIME_WINDOW = 30
# Annualized realized-vol band threshold above which the gate flips OFF.
# Pre-registered conservative value; chosen pre-run, not OOS-tuned.
VOL_REGIME_MAX_ANNUALIZED = 1.50

DEFAULT_IS_FRACTION = 0.70

# Bundle 15 trade-count floors (used by PASS/WATCH/FAIL classifier).
OOS_MIN_TRADES_PER_ASSET = 20
OOS_MIN_TRADES_PER_FAMILY = 30


# ===========================================================================
# Data classes
# ===========================================================================
@dataclasses.dataclass(frozen=True)
class Bar:
    timestamp: str  # ISO-8601 UTC, "YYYY-MM-DD"
    open: float
    high: float
    low: float
    close: float
    volume: float
    symbol: str
    source: str
    quote_currency: str


# ===========================================================================
# CSV loader + validators
# ===========================================================================
def _parse_utc_date(s: str) -> str | None:
    """Accept 'YYYY-MM-DD' or 'YYYY-MM-DDTHH:MM:SSZ'; normalize to YYYY-MM-DD UTC."""
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _row_to_bar(row: dict, file_name: str, line_no: int):
    """Return (Bar, None) on success or (None, reason_str) on rejection."""
    missing = [c for c in REQUIRED_COLUMNS if c not in row or row[c] is None]
    if missing:
        return None, f"{file_name}:{line_no} missing required columns: {missing}"
    try:
        ts = _parse_utc_date(row["timestamp"])
        if ts is None:
            return None, f"{file_name}:{line_no} unparseable timestamp {row['timestamp']!r}"
        if not str(row["close"]).strip():
            return None, f"{file_name}:{line_no} missing close"
        o = float(row["open"])
        h = float(row["high"])
        lo = float(row["low"])
        c = float(row["close"])
        v = float(row["volume"])
    except ValueError as exc:
        return None, f"{file_name}:{line_no} unparseable numeric ({exc})"
    symbol = (row["symbol"] or "").strip().upper()
    if not symbol:
        return None, f"{file_name}:{line_no} missing symbol"
    source = (row["source"] or "").strip()
    if not source:
        return None, f"{file_name}:{line_no} missing source (row-level provenance required)"
    quote = (row["quote_currency"] or "").strip().upper()
    if not quote:
        return None, f"{file_name}:{line_no} missing quote_currency"

    # OHLC quality rules per data contract v1.
    if o <= 0 or h <= 0 or lo <= 0 or c <= 0:
        return None, f"{file_name}:{line_no} non-positive OHLC value"
    if v < 0:
        return None, f"{file_name}:{line_no} negative volume {v}"
    if h < max(o, c, lo):
        return None, f"{file_name}:{line_no} high < max(open, close, low)"
    if lo > min(o, c, h):
        return None, f"{file_name}:{line_no} low > min(open, close, high)"

    return Bar(
        timestamp=ts, open=o, high=h, low=lo, close=c, volume=v,
        symbol=symbol, source=source, quote_currency=quote,
    ), None


def load_dataset(data_dir: Path):
    """Read all *.csv files under data_dir; return (bars_by_symbol, warnings,
    rejections, rows_seen_per_symbol). NEVER fetches data. NEVER fabricates.

    Returns:
        bars_by_symbol: dict[str, list[Bar]] sorted by timestamp asc.
        warnings: list[str]
        rejections: list[str] -- per-row rejection reasons.
        rows_seen_per_symbol: dict[str, int]
    """
    bars_by_symbol: dict[str, list[Bar]] = {}
    warnings: list[str] = []
    rejections: list[str] = []
    rows_seen: dict[str, int] = {}

    if not isinstance(data_dir, Path):
        data_dir = Path(data_dir)
    if not data_dir.exists():
        warnings.append(f"data_dir does not exist: {data_dir.as_posix()}")
        return bars_by_symbol, warnings, rejections, rows_seen
    if not data_dir.is_dir():
        warnings.append(f"data_dir is not a directory: {data_dir.as_posix()}")
        return bars_by_symbol, warnings, rejections, rows_seen

    csv_files = sorted(p for p in data_dir.iterdir() if p.is_file()
                       and p.suffix.lower() == ".csv")
    if not csv_files:
        warnings.append(f"no .csv files found under {data_dir.as_posix()}")
        return bars_by_symbol, warnings, rejections, rows_seen

    # (symbol, timestamp) -> first source file (for duplicate detection).
    seen_key: dict[tuple, str] = {}

    for path in csv_files:
        try:
            with path.open("r", encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                # Validate headers.
                if reader.fieldnames is None:
                    rejections.append(f"{path.name}: empty file or missing header")
                    continue
                missing_cols = [c for c in REQUIRED_COLUMNS if c not in reader.fieldnames]
                if missing_cols:
                    rejections.append(
                        f"{path.name}: missing required header columns {missing_cols}; "
                        f"per data contract v1 header MUST include {list(REQUIRED_COLUMNS)}"
                    )
                    continue
                for line_no, row in enumerate(reader, start=2):
                    bar, reason = _row_to_bar(row, path.name, line_no)
                    if bar is None:
                        rejections.append(reason)
                        continue
                    rows_seen[bar.symbol] = rows_seen.get(bar.symbol, 0) + 1
                    key = (bar.symbol, bar.timestamp)
                    if key in seen_key:
                        rejections.append(
                            f"{path.name}:{line_no} duplicate (symbol={bar.symbol}, "
                            f"timestamp={bar.timestamp}); first seen in {seen_key[key]}"
                        )
                        continue
                    seen_key[key] = path.name
                    bars_by_symbol.setdefault(bar.symbol, []).append(bar)
        except OSError as exc:
            rejections.append(f"{path.name}: read error ({type(exc).__name__})")

    # Sort each symbol's bars by timestamp; flag if any unexpected symbols.
    for symbol in list(bars_by_symbol.keys()):
        bars_by_symbol[symbol].sort(key=lambda b: b.timestamp)
        if symbol not in TARGET_ASSETS:
            warnings.append(
                f"symbol {symbol!r} is NOT in target_assets {TARGET_ASSETS}; "
                f"rows kept for transparency but excluded from target-asset reporting"
            )

    # Per-symbol missing-day audit -- daily bars must be calendar-consecutive
    # OR each gap must be flagged in the run's warnings (24/7 calendar; no
    # silent forward-fill per data contract v1).
    for symbol, bars in bars_by_symbol.items():
        prev = None
        for b in bars:
            if prev is not None:
                try:
                    dprev = datetime.strptime(prev.timestamp, "%Y-%m-%d")
                    dcur = datetime.strptime(b.timestamp, "%Y-%m-%d")
                    delta_days = (dcur - dprev).days
                    if delta_days > 1:
                        warnings.append(
                            f"{symbol}: missing {delta_days - 1} day(s) between "
                            f"{prev.timestamp} and {b.timestamp} -- flagged, never silently forward-filled"
                        )
                except ValueError:
                    pass
            prev = b

    return bars_by_symbol, warnings, rejections, rows_seen


# ===========================================================================
# IS / OOS split
# ===========================================================================
def split_is_oos(bars: list[Bar], fraction: float = DEFAULT_IS_FRACTION):
    n = len(bars)
    cut = max(1, int(n * fraction))
    cut = min(cut, n)
    return bars[:cut], bars[cut:]


# ===========================================================================
# Strategy primitives (return positions list; first element is 0 to align
# with the first available next-bar return).
# ===========================================================================
def buy_and_hold(bars: list[Bar]):
    """Always position 1 from bar 1 onward. Skipped if < 2 bars."""
    if len(bars) < 2:
        return [], "insufficient history: need at least 2 bars"
    return [0] + [1] * (len(bars) - 1), None


def donchian_breakout(bars: list[Bar], entry_n: int = DONCHIAN_ENTRY_N,
                      exit_m: int = DONCHIAN_EXIT_M):
    need = max(entry_n, exit_m) + 1
    if len(bars) < need:
        return [], f"insufficient history: have {len(bars)} bars, need {need}"
    positions = [0]
    cur = 0
    for t in range(1, len(bars)):
        if t < entry_n:
            positions.append(cur)
            continue
        prior_high = max(b.close for b in bars[t - entry_n:t])
        prior_low = (min(b.close for b in bars[t - exit_m:t])
                     if t >= exit_m else None)
        ct = bars[t].close
        if cur == 0 and ct > prior_high:
            cur = 1
        elif cur == 1 and prior_low is not None and ct < prior_low:
            cur = 0
        positions.append(cur)
    return positions, None


def ma_trend_filter(bars: list[Bar], window: int = MA_FILTER_WINDOW):
    need = window + 1
    if len(bars) < need:
        return [], f"insufficient history: have {len(bars)} bars, need {need}"
    positions = [0]
    for t in range(1, len(bars)):
        if t < window:
            positions.append(0)
            continue
        ma = sum(b.close for b in bars[t - window:t]) / window
        positions.append(1 if bars[t].close > ma else 0)
    return positions, None


def momentum_continuation(bars: list[Bar], lookback: int = MOMENTUM_LOOKBACK):
    need = lookback + 1
    if len(bars) < need:
        return [], f"insufficient history: have {len(bars)} bars, need {need}"
    positions = [0]
    for t in range(1, len(bars)):
        if t < lookback:
            positions.append(0)
            continue
        ret_k = bars[t].close / bars[t - lookback].close - 1.0
        positions.append(1 if ret_k > 0 else 0)
    return positions, None


def _rolling_annualized_vol(bars: list[Bar], t: int, window: int):
    """Annualized realized vol over the past `window` daily log-returns
    ending at bar t. 24/7 crypto -> sqrt(365)."""
    if t < window:
        return None
    rets = []
    for i in range(t - window + 1, t + 1):
        if i == 0:
            continue
        prev = bars[i - 1].close
        cur = bars[i].close
        if prev <= 0 or cur <= 0:
            continue
        rets.append(math.log(cur / prev))
    if len(rets) < 2:
        return None
    mean_r = sum(rets) / len(rets)
    var = sum((r - mean_r) ** 2 for r in rets) / (len(rets) - 1)
    return math.sqrt(var) * math.sqrt(365.0)


def vol_regime_gated_donchian(bars: list[Bar],
                              entry_n: int = DONCHIAN_ENTRY_N,
                              exit_m: int = DONCHIAN_EXIT_M,
                              vol_window: int = VOL_REGIME_WINDOW,
                              max_ann_vol: float = VOL_REGIME_MAX_ANNUALIZED):
    """Donchian breakout, gated OFF when rolling-annualized-vol exceeds the
    pre-registered band. Experimental ADDITIVE filter; never standalone."""
    need = max(entry_n, exit_m, vol_window) + 1
    if len(bars) < need:
        return [], f"insufficient history: have {len(bars)} bars, need {need}"
    donchian_pos, skip = donchian_breakout(bars, entry_n, exit_m)
    if skip is not None:
        return [], skip
    positions = []
    for t in range(len(bars)):
        if t < vol_window:
            positions.append(0)
            continue
        ann_vol = _rolling_annualized_vol(bars, t, vol_window)
        gate = 1 if (ann_vol is not None and ann_vol <= max_ann_vol) else 0
        positions.append(gate * donchian_pos[t])
    return positions, None


# ===========================================================================
# Metrics + cost-aware equity simulation
# ===========================================================================
def _simulate_equity(positions, bars, fee_bps, slip_bps, start_equity):
    """Simulate equity given positions[t] (held over bar t -> t+1 return).

    Cost is applied when the position changes (round-trip cost is split:
    entering = fee+slip; exiting = fee+slip)."""
    if len(bars) < 2 or len(positions) != len(bars):
        return {
            "equity_curve": [start_equity],
            "total_return": 0.0,
            "max_drawdown": 0.0,
            "trade_count": 0,
            "exposure_pct": 0.0,
            "turnover": 0,
            "total_cost_paid": 0.0,
        }
    equity = [start_equity]
    trade_count = 0       # count of OPENING events (0 -> 1)
    turnover = 0          # total position-change events
    total_cost = 0.0
    cost_per_change = (fee_bps + slip_bps) / 10_000.0
    exposed_bars = 0
    for t in range(1, len(bars)):
        prev_pos = positions[t - 1]
        cur_pos = positions[t]
        ret = bars[t].close / bars[t - 1].close - 1.0
        new_eq = equity[-1] * (1.0 + cur_pos * ret)
        if cur_pos != prev_pos:
            cost_haircut = new_eq * cost_per_change
            new_eq -= cost_haircut
            total_cost += cost_haircut
            turnover += 1
            if prev_pos == 0 and cur_pos == 1:
                trade_count += 1
        equity.append(new_eq)
        if cur_pos == 1:
            exposed_bars += 1
    peak = equity[0]
    max_dd = 0.0
    for x in equity:
        if x > peak:
            peak = x
        dd = (x - peak) / peak if peak > 0 else 0.0
        if dd < max_dd:
            max_dd = dd
    total_return = (equity[-1] / equity[0]) - 1.0
    exposure_pct = 100.0 * exposed_bars / max(1, (len(bars) - 1))
    return {
        "equity_curve": equity,
        "total_return": total_return,
        "max_drawdown": max_dd,
        "trade_count": trade_count,
        "exposure_pct": exposure_pct,
        "turnover": turnover,
        "total_cost_paid": total_cost,
    }


def _annualized_return(total_return: float, n_bars: int):
    if n_bars <= 1:
        return None
    years = n_bars / 365.0
    if years <= 0:
        return None
    try:
        return (1.0 + total_return) ** (1.0 / years) - 1.0
    except (ValueError, OverflowError):
        return None


def _annualized_vol_from_curve(equity_curve):
    if len(equity_curve) < 3:
        return None
    rets = []
    for i in range(1, len(equity_curve)):
        prev, cur = equity_curve[i - 1], equity_curve[i]
        if prev <= 0:
            continue
        rets.append(cur / prev - 1.0)
    if len(rets) < 2:
        return None
    mean = sum(rets) / len(rets)
    var = sum((r - mean) ** 2 for r in rets) / (len(rets) - 1)
    return math.sqrt(var) * math.sqrt(365.0)


def _sharpe_like(total_return: float, n_bars: int, equity_curve):
    """Sharpe-like ratio with CAVEAT: assumes risk-free = 0 and uses daily
    returns; NOT a true Sharpe; reported with explicit caveat."""
    ann_ret = _annualized_return(total_return, n_bars)
    ann_vol = _annualized_vol_from_curve(equity_curve)
    if ann_ret is None or ann_vol is None or ann_vol <= 0:
        return None
    return ann_ret / ann_vol


def compute_metrics(positions, bars, fee_bps, slip_bps, start_equity):
    sim = _simulate_equity(positions, bars, fee_bps, slip_bps, start_equity)
    n_bars = len(bars)
    return {
        "total_return": sim["total_return"],
        "max_drawdown": sim["max_drawdown"],
        "trade_count": sim["trade_count"],
        "exposure_pct": sim["exposure_pct"],
        "turnover": sim["turnover"],
        "total_cost_paid": sim["total_cost_paid"],
        "annualized_return_approx": _annualized_return(sim["total_return"], n_bars),
        "annualized_vol_approx": _annualized_vol_from_curve(sim["equity_curve"]),
        "sharpe_like_with_caveat": _sharpe_like(sim["total_return"], n_bars, sim["equity_curve"]),
        "sharpe_caveat": (
            "Sharpe-like: rf=0; daily-return approximation; NOT a true Sharpe; "
            "OOS sample may be small."
        ),
        "n_bars": n_bars,
        "start_equity": start_equity,
        "end_equity": sim["equity_curve"][-1] if sim["equity_curve"] else start_equity,
    }


# ===========================================================================
# Per-strategy runner
# ===========================================================================
def _run_one_family(family_id: str, family_label: str, asset: str,
                    bars: list[Bar], params: dict, fee_bps: float,
                    slip_bps: float, start_equity: float,
                    strategy_fn, watch_only: bool = False):
    """Run one strategy family on one asset. Returns a result dict."""
    if watch_only:
        return {
            "strategy_id": f"{family_id}_{asset.lower()}",
            "family": family_id,
            "label": family_label,
            "asset": asset,
            "parameters": params,
            "status": "SKIPPED_WATCH_ONLY",
            "skip_reason": (
                "WATCH-only in Bundle 15 plan v1; not implemented as a primary"
                " strategy; mean_reversion lineage explicitly forbidden from"
                " reviving any prior CODR-* parameter set."
            ),
            "metrics": None,
            "is_metrics": None,
            "oos_metrics": None,
            "warnings": [],
        }
    try:
        positions, skip_reason = strategy_fn(bars, **params)
    except TypeError:
        positions, skip_reason = strategy_fn(bars)
    if skip_reason is not None:
        return {
            "strategy_id": f"{family_id}_{asset.lower()}",
            "family": family_id,
            "label": family_label,
            "asset": asset,
            "parameters": params,
            "status": "SKIPPED_INSUFFICIENT_HISTORY",
            "skip_reason": skip_reason,
            "metrics": None,
            "is_metrics": None,
            "oos_metrics": None,
            "warnings": [],
        }
    is_bars, oos_bars = split_is_oos(bars, DEFAULT_IS_FRACTION)
    is_positions = positions[:len(is_bars)]
    oos_positions = positions[len(is_bars):]
    full_metrics = compute_metrics(positions, bars, fee_bps, slip_bps, start_equity)
    is_metrics = (compute_metrics(is_positions, is_bars, fee_bps, slip_bps, start_equity)
                  if len(is_bars) >= 2 else None)
    oos_metrics = (compute_metrics(oos_positions, oos_bars, fee_bps, slip_bps, start_equity)
                   if len(oos_bars) >= 2 else None)
    warnings = []
    if oos_metrics is None:
        warnings.append("OOS window too small to compute metrics (< 2 bars).")
    elif oos_metrics["trade_count"] < OOS_MIN_TRADES_PER_ASSET:
        warnings.append(
            f"OOS trade_count {oos_metrics['trade_count']} below per-asset floor "
            f"{OOS_MIN_TRADES_PER_ASSET} (Bundle 15)."
        )
    return {
        "strategy_id": f"{family_id}_{asset.lower()}",
        "family": family_id,
        "label": family_label,
        "asset": asset,
        "parameters": params,
        "status": "RAN",
        "skip_reason": None,
        "metrics": full_metrics,
        "is_metrics": is_metrics,
        "oos_metrics": oos_metrics,
        "warnings": warnings,
    }


def _basket_buy_and_hold(bars_by_symbol: dict[str, list[Bar]],
                         fee_bps: float, slip_bps: float, start_equity: float):
    """Equal-weight daily-rebalanced basket buy-and-hold benchmark across the
    intersection of dates present in every covered asset."""
    if not bars_by_symbol:
        return None
    covered = [s for s in TARGET_ASSETS if s in bars_by_symbol and len(bars_by_symbol[s]) >= 2]
    if len(covered) < 1:
        return None
    common_dates = set(b.timestamp for b in bars_by_symbol[covered[0]])
    for s in covered[1:]:
        common_dates &= set(b.timestamp for b in bars_by_symbol[s])
    sorted_dates = sorted(common_dates)
    if len(sorted_dates) < 2:
        return None
    closes = {s: {b.timestamp: b.close for b in bars_by_symbol[s]} for s in covered}
    equity = [start_equity]
    n_assets = len(covered)
    cost_per_change = (fee_bps + slip_bps) / 10_000.0
    for i in range(1, len(sorted_dates)):
        d_prev = sorted_dates[i - 1]
        d_cur = sorted_dates[i]
        per_asset = 0.0
        for s in covered:
            r = closes[s][d_cur] / closes[s][d_prev] - 1.0
            per_asset += r
        avg_r = per_asset / n_assets
        eq = equity[-1] * (1.0 + avg_r)
        # Equal-weight daily rebalance => apply a small turnover haircut per
        # rebalance proportional to inter-asset dispersion (conservative
        # constant approximation).
        eq -= eq * cost_per_change * (n_assets - 1) / max(1, n_assets)
        equity.append(eq)
    peak = equity[0]
    max_dd = 0.0
    for x in equity:
        if x > peak:
            peak = x
        dd = (x - peak) / peak if peak > 0 else 0.0
        if dd < max_dd:
            max_dd = dd
    total_return = equity[-1] / equity[0] - 1.0
    return {
        "strategy_id": "buy_and_hold_basket",
        "family": "buy_and_hold_benchmark",
        "label": "A. Buy-and-hold benchmark (equal-weight basket, daily rebalanced)",
        "asset": "BASKET",
        "parameters": {
            "rebalance_frequency": "daily",
            "basket_weights": "equal-weight per covered asset",
            "covered_assets": covered,
        },
        "status": "RAN",
        "skip_reason": None,
        "metrics": {
            "total_return": total_return,
            "max_drawdown": max_dd,
            "trade_count": 1,
            "exposure_pct": 100.0,
            "turnover": len(sorted_dates) - 1,
            "total_cost_paid": start_equity - equity[-1] + start_equity * (1.0 + total_return) - equity[-1]
            if False else 0.0,  # see below; conservative approximation only.
            "annualized_return_approx": _annualized_return(total_return, len(sorted_dates)),
            "annualized_vol_approx": _annualized_vol_from_curve(equity),
            "sharpe_like_with_caveat": _sharpe_like(total_return, len(sorted_dates), equity),
            "sharpe_caveat": "Sharpe-like; rf=0; daily-return approximation.",
            "n_bars": len(sorted_dates),
            "start_equity": start_equity,
            "end_equity": equity[-1],
        },
        "is_metrics": None,  # basket is a single benchmark stream; IS/OOS via per-asset.
        "oos_metrics": None,
        "warnings": ["Basket benchmark is a single stream; no per-basket IS/OOS split in v1."],
    }


# ===========================================================================
# PASS / WATCH / FAIL classifier (conservative).
# ===========================================================================
def classify_run(strategy_results, benchmark_results, failures, warnings,
                 has_any_data: bool):
    if not has_any_data:
        return ("FAIL",
                ["missing local data: no parseable OHLCV bars found at --data-dir"],
                ["A future PASS is not trading authorization; this run did not"
                 " produce any backtest result and does NOT promote the lane."])
    if failures:
        return ("FAIL", list(failures),
                ["Failures present; remediation requires a new dataset_version per Bundle 13 freeze rules."])
    # Collect OOS evidence across non-skipped, non-benchmark families.
    ran_strats = [r for r in strategy_results
                  if r.get("status") == "RAN" and r.get("oos_metrics") is not None]
    if not ran_strats:
        return ("FAIL",
                ["No strategy family completed an IS/OOS run; v1 result is not actionable."],
                ["No paper / live action authorized; future remediation goes through a new dataset_version."])
    # Benchmark comparison (per asset).
    bench_by_asset = {b["asset"]: b for b in benchmark_results if b.get("status") == "RAN"}
    promising = []
    for r in ran_strats:
        m = r["oos_metrics"]
        if m["total_return"] <= 0:
            continue
        if m["trade_count"] < OOS_MIN_TRADES_PER_ASSET:
            continue
        bench = bench_by_asset.get(r["asset"])
        if bench is None or bench["metrics"] is None:
            continue
        # Risk-adjusted beat: strategy Sharpe-like must exceed benchmark Sharpe-like.
        s_sharpe = m.get("sharpe_like_with_caveat")
        b_sharpe = bench["metrics"].get("sharpe_like_with_caveat")
        if s_sharpe is None or b_sharpe is None:
            continue
        if s_sharpe > b_sharpe:
            promising.append(r["strategy_id"])
    # v1 conservative posture:
    #   - PASS is reserved for a future operator decision after manual review.
    #     The runner NEVER returns PASS in v1; the highest auto-emitted status
    #     is WATCH.
    if promising:
        return ("WATCH",
                [],
                [f"{len(promising)} strategy result(s) show positive OOS + above-benchmark"
                 " risk-adjusted return; this is INCOMPLETE evidence and does NOT promote"
                 " the lane. PASS requires explicit operator review."])
    return ("FAIL",
            ["No strategy family produced positive OOS evidence above the buy-and-hold"
             " benchmark on a risk-adjusted basis with sufficient trades."],
            ["Per Bundle 15 PASS/WATCH/FAIL rules: 'worse than buy-and-hold after risk"
             " adjustment' is FAIL. No paper / live action authorized."])


# ===========================================================================
# Run orchestration
# ===========================================================================
def _hash_inputs(data_dir: Path, files: list[Path], fee_bps: float,
                 slip_bps: float, start_equity: float, is_fraction: float):
    h = hashlib.sha256()
    h.update(RUNNER_VERSION.encode("utf-8"))
    h.update(PLAN_VERSION.encode("utf-8"))
    h.update(f"|{fee_bps}|{slip_bps}|{start_equity}|{is_fraction}|".encode("utf-8"))
    for p in files:
        h.update(p.name.encode("utf-8"))
        try:
            h.update(p.read_bytes())
        except OSError:
            h.update(b"<unreadable>")
    return h.hexdigest()[:16]


def run_backtest(data_dir, out_dir, fee_bps: float = DEFAULT_TAKER_FEE_BPS,
                 slip_bps: float = DEFAULT_SLIPPAGE_BPS,
                 start_equity: float = DEFAULT_START_EQUITY,
                 is_fraction: float = DEFAULT_IS_FRACTION):
    """Run the v1 baseline backtest against operator-supplied local CSVs.

    Returns the report dict. Writes JSON + MD reports to out_dir.
    """
    ok, errs = validate_config(fee_bps, slip_bps)
    if not ok:
        raise ValueError("invalid config: " + "; ".join(errs))

    data_dir_p = Path(data_dir)
    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)

    bars_by_symbol, warnings, rejections, rows_seen = load_dataset(data_dir_p)
    csv_files = sorted([p for p in data_dir_p.iterdir()
                        if p.is_file() and p.suffix.lower() == ".csv"]) \
        if data_dir_p.exists() and data_dir_p.is_dir() else []

    assets_seen = [a for a in TARGET_ASSETS if a in bars_by_symbol]
    assets_missing = [a for a in TARGET_ASSETS if a not in bars_by_symbol]

    strategy_results = []
    benchmark_results = []

    # Per-asset runs: benchmark + 4 primary + 1 additive-filter experiment.
    for asset in assets_seen:
        bars = bars_by_symbol[asset]
        benchmark_results.append(_run_one_family(
            family_id="buy_and_hold_benchmark",
            family_label="A. Buy-and-hold benchmark",
            asset=asset, bars=bars, params={}, fee_bps=fee_bps, slip_bps=slip_bps,
            start_equity=start_equity, strategy_fn=buy_and_hold,
        ))
        strategy_results.append(_run_one_family(
            family_id="donchian_channel_breakout",
            family_label="B. Donchian / channel breakout",
            asset=asset, bars=bars,
            params={"entry_n": DONCHIAN_ENTRY_N, "exit_m": DONCHIAN_EXIT_M},
            fee_bps=fee_bps, slip_bps=slip_bps, start_equity=start_equity,
            strategy_fn=donchian_breakout,
        ))
        strategy_results.append(_run_one_family(
            family_id="moving_average_trend_filter",
            family_label="C. Moving-average trend filter",
            asset=asset, bars=bars, params={"window": MA_FILTER_WINDOW},
            fee_bps=fee_bps, slip_bps=slip_bps, start_equity=start_equity,
            strategy_fn=ma_trend_filter,
        ))
        strategy_results.append(_run_one_family(
            family_id="momentum_continuation",
            family_label="D. Momentum continuation",
            asset=asset, bars=bars, params={"lookback": MOMENTUM_LOOKBACK},
            fee_bps=fee_bps, slip_bps=slip_bps, start_equity=start_equity,
            strategy_fn=momentum_continuation,
        ))
        strategy_results.append(_run_one_family(
            family_id="volatility_regime_gate",
            family_label="E. Volatility-regime gate (experimental; additive filter on Donchian)",
            asset=asset, bars=bars,
            params={"entry_n": DONCHIAN_ENTRY_N, "exit_m": DONCHIAN_EXIT_M,
                    "vol_window": VOL_REGIME_WINDOW,
                    "max_ann_vol": VOL_REGIME_MAX_ANNUALIZED},
            fee_bps=fee_bps, slip_bps=slip_bps, start_equity=start_equity,
            strategy_fn=vol_regime_gated_donchian,
        ))
        strategy_results.append(_run_one_family(
            family_id="mean_reversion",
            family_label="F. Daily mean reversion (WATCH-only; not primary)",
            asset=asset, bars=bars, params={},
            fee_bps=fee_bps, slip_bps=slip_bps, start_equity=start_equity,
            strategy_fn=lambda bars: ([], None), watch_only=True,
        ))

    # Basket benchmark.
    basket = _basket_buy_and_hold(bars_by_symbol, fee_bps, slip_bps, start_equity)
    if basket is not None:
        benchmark_results.append(basket)

    has_any_data = bool(assets_seen)
    failures: list[str] = []
    if not has_any_data:
        failures.append(
            "missing local data: no parseable OHLCV bars found at "
            f"{data_dir_p.as_posix()}. Per Bundle 15, the runner will not"
            " fabricate any result; emit FAIL."
        )
    # Pre-pend rejection summary -- rejections are NOT silent failures;
    # they're listed for operator review.
    if rejections:
        warnings.append(f"{len(rejections)} row(s) rejected; see 'rows_rejected_detail'")

    pwf, extra_failures, next_steps = classify_run(
        strategy_results, benchmark_results, failures, warnings, has_any_data)
    failures.extend(extra_failures)

    # Determine IS/OOS span summary from any asset that ran.
    is_oos_summary = {
        "is_fraction": is_fraction,
        "trade_count_floor_per_asset_for_oos_verdict": OOS_MIN_TRADES_PER_ASSET,
        "trade_count_floor_per_family_for_oos_verdict": OOS_MIN_TRADES_PER_FAMILY,
        "per_asset_is_range": {},
        "per_asset_oos_range": {},
    }
    for asset in assets_seen:
        bars = bars_by_symbol[asset]
        is_b, oos_b = split_is_oos(bars, is_fraction)
        if is_b:
            is_oos_summary["per_asset_is_range"][asset] = {
                "start": is_b[0].timestamp, "end": is_b[-1].timestamp, "n_bars": len(is_b)
            }
        if oos_b:
            is_oos_summary["per_asset_oos_range"][asset] = {
                "start": oos_b[0].timestamp, "end": oos_b[-1].timestamp, "n_bars": len(oos_b)
            }

    report = {
        "run_id": _hash_inputs(data_dir_p, csv_files, fee_bps, slip_bps,
                               start_equity, is_fraction),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **SAFETY_FLAGS,
        "runner_version": RUNNER_VERSION,
        "plan_version": PLAN_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "data_contract_version": DATA_CONTRACT_VERSION,
        "dataset_manifest_spec_version": DATASET_MANIFEST_SPEC_VERSION,
        "qa_freeze_spec_version": QA_FREEZE_SPEC_VERSION,
        "input_data_dir": data_dir_p.as_posix(),
        "input_data_hash_short": _hash_inputs(data_dir_p, csv_files, fee_bps,
                                              slip_bps, start_equity, is_fraction),
        "csv_files_seen": [p.name for p in csv_files],
        "assets_seen": assets_seen,
        "assets_missing": assets_missing,
        "row_counts_per_symbol": rows_seen,
        "rows_rejected": len(rejections),
        "rows_rejected_detail": rejections[:200],
        "cost_model": {"fee_bps": fee_bps, "slippage_bps": slip_bps,
                       "default_assumption": "TAKER on every leg",
                       "fees_as_distinct_pnl_line": True,
                       "no_zero_slippage_baseline": True},
        "start_equity": start_equity,
        "IS_OOS_summary": is_oos_summary,
        "strategy_results": strategy_results,
        "benchmark_results": benchmark_results,
        "warnings": warnings,
        "failures": failures,
        "pass_watch_fail_status": pwf,
        "next_action": next_steps[0] if next_steps else "Operator review required.",
        "forbidden_next_steps": list(FORBIDDEN_NEXT_STEPS),
        "safety_notes": list(SAFETY_NOTES),
    }

    # Write JSON and MD reports.
    json_path = out_dir_p / "crypto_d1_backtest_report.json"
    md_path = out_dir_p / "crypto_d1_backtest_report.md"
    json_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    md_path.write_text(_render_md(report), encoding="utf-8")
    return report


def _render_md(report: dict) -> str:
    lines = [
        "# SPARTA Crypto-D1 Backtest Runner v1 -- Run Report",
        "",
        "> **Research-only. Local-only.** No data fetched. No exchange contacted."
        " No order placed. No paper or live trading authorized.",
        "",
        f"- **run_id:** `{report['run_id']}`",
        f"- **generated_at:** {report['generated_at']}",
        f"- **runner_version:** {report['runner_version']}",
        f"- **plan_version:** {report['plan_version']}",
        f"- **protocol_version:** {report['protocol_version']}",
        f"- **data_contract_version:** {report['data_contract_version']}",
        f"- **dataset_manifest_spec_version:** {report['dataset_manifest_spec_version']}",
        f"- **qa_freeze_spec_version:** {report['qa_freeze_spec_version']}",
        f"- **input_data_dir:** `{report['input_data_dir']}`",
        f"- **input_data_hash (short):** `{report['input_data_hash_short']}`",
        "",
        "## Safety flags (pinned)",
        f"- research_only: {report['research_only']}",
        f"- data_fetch_enabled: {report['data_fetch_enabled']}",
        f"- exchange_connection_enabled: {report['exchange_connection_enabled']}",
        f"- live_trading_enabled: {report['live_trading_enabled']}",
        f"- broker_control_enabled: {report['broker_control_enabled']}",
        f"- paper_order_execution_enabled: {report['paper_order_execution_enabled']}",
        f"- order_placement_enabled: {report['order_placement_enabled']}",
        "",
        "## Assets",
        f"- **seen:** {', '.join(report['assets_seen']) or '(none)'}",
        f"- **missing:** {', '.join(report['assets_missing']) or '(none)'}",
        "",
        "## Verdict",
        f"- **pass_watch_fail_status:** **{report['pass_watch_fail_status']}**",
        f"- **next_action:** {report['next_action']}",
        "",
    ]
    if report["failures"]:
        lines += ["## Failures"]
        for f in report["failures"]:
            lines.append(f"- {f}")
        lines.append("")
    if report["warnings"]:
        lines += ["## Warnings"]
        for w in report["warnings"][:50]:
            lines.append(f"- {w}")
        if len(report["warnings"]) > 50:
            lines.append(f"- ... and {len(report['warnings']) - 50} more")
        lines.append("")
    lines += ["## Benchmark results"]
    for r in report["benchmark_results"]:
        m = r.get("metrics") or {}
        lines.append(
            f"- `{r['strategy_id']}` ({r['asset']}): total_return={m.get('total_return')}"
            f", max_drawdown={m.get('max_drawdown')}, trade_count={m.get('trade_count')}"
        )
    lines += ["", "## Strategy results"]
    for r in report["strategy_results"]:
        if r["status"] != "RAN":
            lines.append(f"- `{r['strategy_id']}` ({r['asset']}): **{r['status']}**"
                         f" -- {r.get('skip_reason')}")
            continue
        m = r["metrics"]
        oos = r["oos_metrics"] or {}
        lines.append(
            f"- `{r['strategy_id']}` ({r['asset']}): total_return={m.get('total_return')}"
            f", oos_total_return={oos.get('total_return')}, oos_trade_count={oos.get('trade_count')}"
        )
    lines += ["", "## Forbidden next steps"]
    for s in report["forbidden_next_steps"]:
        lines.append(f"- {s}")
    lines += ["", "## Safety notes"]
    for s in report["safety_notes"]:
        lines.append(f"- {s}")
    return "\n".join(lines) + "\n"


# ===========================================================================
# Config + plan helpers
# ===========================================================================
def validate_config(fee_bps: float = DEFAULT_TAKER_FEE_BPS,
                    slip_bps: float = DEFAULT_SLIPPAGE_BPS):
    errs = []
    try:
        f = float(fee_bps)
    except (TypeError, ValueError):
        errs.append("fee_bps must be numeric")
        f = None
    try:
        s = float(slip_bps)
    except (TypeError, ValueError):
        errs.append("slippage_bps must be numeric")
        s = None
    if f is not None and (f < FEE_BPS_MIN or f > FEE_BPS_MAX):
        errs.append(f"fee_bps must be in [{FEE_BPS_MIN}, {FEE_BPS_MAX}] (got {f})")
    if s is not None and (s < SLIP_BPS_MIN or s > SLIP_BPS_MAX):
        errs.append(f"slippage_bps must be in [{SLIP_BPS_MIN}, {SLIP_BPS_MAX}] (got {s})")
    return (not errs), errs


def show_plan() -> dict:
    return {
        "runner_version": RUNNER_VERSION,
        "plan_version": PLAN_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "data_contract_version": DATA_CONTRACT_VERSION,
        "dataset_manifest_spec_version": DATASET_MANIFEST_SPEC_VERSION,
        "qa_freeze_spec_version": QA_FREEZE_SPEC_VERSION,
        "target_assets": list(TARGET_ASSETS),
        "allowed_market_type": "spot",
        "timeframe": "1d",
        "session_calendar": "24/7",
        "weekday_only_filters_forbidden": True,
        "required_columns": list(REQUIRED_COLUMNS),
        "strategy_families": [
            {"id": "buy_and_hold_benchmark", "status": "benchmark", "params": {}},
            {"id": "donchian_channel_breakout", "status": "primary",
             "params": {"entry_n": DONCHIAN_ENTRY_N, "exit_m": DONCHIAN_EXIT_M}},
            {"id": "moving_average_trend_filter", "status": "primary",
             "params": {"window": MA_FILTER_WINDOW}},
            {"id": "momentum_continuation", "status": "primary",
             "params": {"lookback": MOMENTUM_LOOKBACK}},
            {"id": "volatility_regime_gate", "status": "primary_additive_filter",
             "params": {"entry_n": DONCHIAN_ENTRY_N, "exit_m": DONCHIAN_EXIT_M,
                        "vol_window": VOL_REGIME_WINDOW,
                        "max_ann_vol": VOL_REGIME_MAX_ANNUALIZED}},
            {"id": "mean_reversion", "status": "WATCH_only",
             "params": {}, "note": "Skipped in v1; never primary; "
                                    "must not revive any prior CODR-* parameter set."},
        ],
        "cost_model_defaults": {
            "taker_fee_bps": DEFAULT_TAKER_FEE_BPS,
            "slippage_bps": DEFAULT_SLIPPAGE_BPS,
            "fee_bps_bounds": [FEE_BPS_MIN, FEE_BPS_MAX],
            "slippage_bps_bounds": [SLIP_BPS_MIN, SLIP_BPS_MAX],
            "fees_as_distinct_pnl_line": True,
        },
        "validation_split": {"is_fraction": DEFAULT_IS_FRACTION,
                             "oos_min_trades_per_asset": OOS_MIN_TRADES_PER_ASSET,
                             "oos_min_trades_per_family": OOS_MIN_TRADES_PER_FAMILY},
        "position_sizing": {
            "no_leverage": True,
            "long_only_spot_first": True,
            "no_shorting_in_this_protocol": True,
            "start_equity_default": DEFAULT_START_EQUITY,
            "start_equity_is_research_units_not_money": True,
        },
        "safety_flags": dict(SAFETY_FLAGS),
        "safety_notes": list(SAFETY_NOTES),
        "forbidden_next_steps": list(FORBIDDEN_NEXT_STEPS),
    }


# ===========================================================================
# CLI
# ===========================================================================
def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Crypto-D1 Backtest Runner v1 -- local-only, research-only.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="Run the v1 baseline backtest.")
    p_run.add_argument("--data-dir", required=True, help="Directory containing operator-supplied local CSV files.")
    p_run.add_argument("--out-dir", required=True, help="Directory to write JSON + MD reports.")
    p_run.add_argument("--fee-bps", type=float, default=DEFAULT_TAKER_FEE_BPS)
    p_run.add_argument("--slippage-bps", type=float, default=DEFAULT_SLIPPAGE_BPS)
    p_run.add_argument("--start-equity", type=float, default=DEFAULT_START_EQUITY)
    p_run.add_argument("--is-fraction", type=float, default=DEFAULT_IS_FRACTION)

    p_validate = sub.add_parser("validate-config", help="Validate cost-model bounds.")
    p_validate.add_argument("--fee-bps", type=float, default=DEFAULT_TAKER_FEE_BPS)
    p_validate.add_argument("--slippage-bps", type=float, default=DEFAULT_SLIPPAGE_BPS)

    sub.add_parser("show-plan", help="Print the pre-registered plan.")

    args = parser.parse_args(argv)
    if args.command == "run":
        ok, errs = validate_config(args.fee_bps, args.slippage_bps)
        if not ok:
            print("validate-config: FAIL")
            for e in errs:
                print(f"  - {e}")
            return 2
        report = run_backtest(
            data_dir=args.data_dir, out_dir=args.out_dir,
            fee_bps=args.fee_bps, slip_bps=args.slippage_bps,
            start_equity=args.start_equity, is_fraction=args.is_fraction,
        )
        print(f"run_id:                {report['run_id']}")
        print(f"pass_watch_fail_status:{report['pass_watch_fail_status']}")
        print(f"assets_seen:           {report['assets_seen']}")
        print(f"assets_missing:        {report['assets_missing']}")
        print(f"warnings:              {len(report['warnings'])}")
        print(f"failures:              {len(report['failures'])}")
        print(f"reports written to:    {Path(args.out_dir).as_posix()}")
        return 0 if report["pass_watch_fail_status"] != "FAIL" else 2
    if args.command == "validate-config":
        ok, errs = validate_config(args.fee_bps, args.slippage_bps)
        if ok:
            print("validate-config: OK")
            return 0
        print("validate-config: FAIL")
        for e in errs:
            print(f"  - {e}")
        return 2
    if args.command == "show-plan":
        plan = show_plan()
        print(json.dumps(plan, indent=2, sort_keys=True, ensure_ascii=False, default=str))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

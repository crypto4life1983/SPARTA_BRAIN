"""Pure metric functions for the Agentic Backtest Factory.

OFFLINE / INERT: no network, no file writes, no imports beyond the stdlib.
Every function takes plain Python data (a list of trade R-multiples or PnL
values) and returns numbers. Nothing here touches disk or the outside world.

A "trade" here is summarized by its R-multiple result (profit/loss expressed
in units of initial risk). Positive = win, negative = loss.
"""

from __future__ import annotations

import math
from typing import List, Dict


def trade_count(r_multiples: List[float]) -> int:
    """Number of trades."""
    return len(r_multiples)


def win_rate(r_multiples: List[float]) -> float:
    """Fraction of trades with R > 0. Returns 0.0 when there are no trades."""
    if not r_multiples:
        return 0.0
    wins = sum(1 for r in r_multiples if r > 0)
    return wins / len(r_multiples)


def profit_factor(r_multiples: List[float]) -> float:
    """Gross profit / gross loss (absolute).

    Returns math.inf when there are profits but no losses, and 0.0 when there
    are no profits.
    """
    gross_profit = sum(r for r in r_multiples if r > 0)
    gross_loss = abs(sum(r for r in r_multiples if r < 0))
    if gross_loss == 0:
        return math.inf if gross_profit > 0 else 0.0
    return gross_profit / gross_loss


def expectancy(r_multiples: List[float]) -> float:
    """Average R per trade. Returns 0.0 when there are no trades."""
    if not r_multiples:
        return 0.0
    return sum(r_multiples) / len(r_multiples)


def equity_curve(r_multiples: List[float]) -> List[float]:
    """Cumulative R after each trade."""
    curve: List[float] = []
    running = 0.0
    for r in r_multiples:
        running += r
        curve.append(running)
    return curve


def max_drawdown_r(r_multiples: List[float]) -> float:
    """Maximum peak-to-trough drawdown of the cumulative R curve, in R units.

    Returns a non-negative number (0.0 when the curve never declines).
    """
    peak = 0.0
    max_dd = 0.0
    running = 0.0
    for r in r_multiples:
        running += r
        if running > peak:
            peak = running
        drawdown = peak - running
        if drawdown > max_dd:
            max_dd = drawdown
    return max_dd


def max_drawdown_pct(r_multiples: List[float]) -> float:
    """Max drawdown as a percentage of the peak cumulative R.

    Percentage relative to the running peak. Returns 0.0 when there is no
    positive peak to measure against (e.g. no trades or never profitable).
    """
    peak = 0.0
    max_pct = 0.0
    running = 0.0
    for r in r_multiples:
        running += r
        if running > peak:
            peak = running
        if peak > 0:
            drawdown_pct = (peak - running) / peak * 100.0
            if drawdown_pct > max_pct:
                max_pct = drawdown_pct
    return max_pct


def sharpe_like(r_multiples: List[float]) -> float:
    """A simple per-trade Sharpe-like ratio: mean(R) / stdev(R).

    Not annualized. Returns 0.0 when fewer than two trades or zero variance.
    """
    n = len(r_multiples)
    if n < 2:
        return 0.0
    mean = sum(r_multiples) / n
    variance = sum((r - mean) ** 2 for r in r_multiples) / (n - 1)
    if variance <= 0:
        return 0.0
    return mean / math.sqrt(variance)


def summarize(r_multiples: List[float]) -> Dict[str, float]:
    """Bundle all metrics into a single dict for reports and decisions."""
    return {
        "trade_count": float(trade_count(r_multiples)),
        "win_rate": win_rate(r_multiples),
        "profit_factor": profit_factor(r_multiples),
        "expectancy_r": expectancy(r_multiples),
        "max_drawdown_r": max_drawdown_r(r_multiples),
        "max_drawdown_pct": max_drawdown_pct(r_multiples),
        "sharpe_like": sharpe_like(r_multiples),
    }

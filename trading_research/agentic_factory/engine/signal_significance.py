"""Entry-rule significance test for the Agentic Backtest Factory.

OFFLINE / INERT: operates on plain in-memory bars and signal indices only. No
network, no broker, no order placement, no file writes, no execution. Python
standard library only (random, statistics).

The question this module answers, BEFORE any exit/stop/sizing optimization:
*does the raw entry signal carry edge?* It measures the forward return after
each entry signal and compares the real signals' mean forward return against a
distribution of same-count RANDOM entries drawn from the same bars. If the real
signal is not meaningfully better than throwing darts, there is no entry edge to
build a strategy around.

A "bar" is either a mapping with a "close" key or a bare number (treated as the
close). Signals are integer indices into the bars list. `horizon` is how many
bars ahead the forward return is measured over.

Determinism: every random draw is seeded, so a run is fully reproducible.
"""

from __future__ import annotations

import random
import statistics
from typing import Any, Dict, List, Sequence

# Verdict labels.
EDGE_LIKELY = "EDGE_LIKELY"
INCONCLUSIVE = "INCONCLUSIVE"
NO_EDGE = "NO_EDGE"
NO_RESULT = "NO_RESULT"  # safe sentinel for empty / too-short inputs


def _close(bar: Any) -> float:
    """Return the close price of a bar (mapping with 'close', or a bare number)."""
    if isinstance(bar, dict):
        return float(bar["close"])
    return float(bar)


def forward_returns(
    bars: Sequence[Any],
    signal_indices: Sequence[int],
    horizon: int,
) -> List[float]:
    """Forward return over `horizon` bars after each signal index.

    For each index i, return (close[i+horizon] - close[i]) / close[i]. Indices
    whose forward window falls outside the data (or which are negative) are
    skipped silently. Returns an empty list when nothing is usable.
    """
    if horizon <= 0:
        return []
    n = len(bars)
    out: List[float] = []
    for i in signal_indices:
        if i < 0 or i + horizon >= n:
            continue
        c0 = _close(bars[i])
        if c0 == 0:
            continue
        c1 = _close(bars[i + horizon])
        out.append((c1 - c0) / c0)
    return out


def _valid_entry_indices(n_bars: int, horizon: int) -> List[int]:
    """Indices that have a full `horizon`-bar forward window inside the data."""
    if horizon <= 0 or n_bars - horizon <= 0:
        return []
    return list(range(0, n_bars - horizon))


def random_entry_baseline(
    bars: Sequence[Any],
    n_signals: int,
    horizon: int,
    n_iter: int,
    seed: int,
) -> List[float]:
    """Distribution of mean forward return for same-count random entries.

    Each of `n_iter` iterations draws exactly `n_signals` random entry indices
    from the pool of indices that have a full forward window, then records the
    mean forward return of that draw. Sampling is without replacement when the
    pool is large enough, otherwise with replacement. Fully seeded.

    Returns a list of `n_iter` means (the baseline distribution), or an empty
    list when there is nothing to sample.
    """
    if n_signals <= 0 or n_iter <= 0:
        return []
    pool = _valid_entry_indices(len(bars), horizon)
    if not pool:
        return []

    rng = random.Random(seed)
    dist: List[float] = []
    for _ in range(n_iter):
        if n_signals <= len(pool):
            picks = rng.sample(pool, n_signals)
        else:
            picks = rng.choices(pool, k=n_signals)
        frs = forward_returns(bars, picks, horizon)
        # picks are all valid, so len(frs) == n_signals.
        dist.append(sum(frs) / len(frs) if frs else 0.0)
    return dist


def permutation_test(
    real_returns: Sequence[float],
    baseline_dist: Sequence[float],
) -> Dict[str, float]:
    """Compare the real signal's mean forward return to a random-entry baseline.

    One-sided test (H1: the real signal beats random). Reports:
      - real_mean, baseline_mean, baseline_std
      - percentile: % of baseline means strictly below the real mean (0..100)
      - p_value: (#baseline >= real_mean + 1) / (n + 1), bounded in (0, 1]

    Returns a safe zeroed result (p_value = 1.0) when either input is empty.
    """
    if not real_returns or not baseline_dist:
        return {
            "real_mean": (sum(real_returns) / len(real_returns)) if real_returns else 0.0,
            "baseline_mean": 0.0,
            "baseline_std": 0.0,
            "percentile": 0.0,
            "p_value": 1.0,
            "n_iter": float(len(baseline_dist)),
        }

    real_mean = sum(real_returns) / len(real_returns)
    n = len(baseline_dist)
    count_ge = sum(1 for b in baseline_dist if b >= real_mean)
    count_lt = sum(1 for b in baseline_dist if b < real_mean)
    p_value = (count_ge + 1) / (n + 1)
    percentile = 100.0 * count_lt / n
    baseline_mean = sum(baseline_dist) / n
    baseline_std = statistics.pstdev(baseline_dist) if n >= 2 else 0.0

    return {
        "real_mean": real_mean,
        "baseline_mean": baseline_mean,
        "baseline_std": baseline_std,
        "percentile": percentile,
        "p_value": p_value,
        "n_iter": float(n),
    }


def _verdict(
    real_count: int,
    baseline_n: int,
    real_mean: float,
    baseline_mean: float,
    percentile: float,
    p_value: float,
) -> str:
    """Map the test result to a single honest verdict."""
    if real_count == 0 or baseline_n == 0:
        return NO_RESULT
    if p_value <= 0.05 and real_mean > baseline_mean and percentile >= 95.0:
        return EDGE_LIKELY
    if real_mean <= baseline_mean or percentile <= 50.0:
        return NO_EDGE
    return INCONCLUSIVE


def summarize_significance(
    bars: Sequence[Any],
    signal_indices: Sequence[int],
    horizon: int,
    n_iter: int = 1000,
    seed: int = 23,
) -> Dict[str, Any]:
    """Run the full entry-rule significance test and return an inert summary.

    Pipeline: real forward returns -> same-count random baseline -> permutation
    test -> verdict. The random baseline is drawn with EXACTLY as many entries
    as the real signal produced usable forward returns (real_count == n_signals).
    """
    real = forward_returns(bars, signal_indices, horizon)
    real_count = len(real)

    baseline = random_entry_baseline(
        bars, n_signals=real_count, horizon=horizon, n_iter=n_iter, seed=seed
    )
    test = permutation_test(real, baseline)

    verdict = _verdict(
        real_count=real_count,
        baseline_n=len(baseline),
        real_mean=test["real_mean"],
        baseline_mean=test["baseline_mean"],
        percentile=test["percentile"],
        p_value=test["p_value"],
    )

    reasons: List[str] = []
    if verdict == NO_RESULT:
        reasons.append(
            f"insufficient data: real_count={real_count}, baseline_n={len(baseline)} "
            f"(need bars longer than horizon={horizon} and >=1 usable signal)"
        )
    else:
        reasons.append(
            f"real_mean {test['real_mean']:.5f} vs baseline_mean "
            f"{test['baseline_mean']:.5f}; percentile {test['percentile']:.1f}; "
            f"p_value {test['p_value']:.4f} over {len(baseline)} random draws"
        )

    return {
        "verdict": verdict,
        "horizon": int(horizon),
        "n_iter": int(n_iter),
        "seed": int(seed),
        "real_count": real_count,
        "n_signals": real_count,  # baseline used exactly this many entries
        "real_mean": test["real_mean"],
        "baseline_mean": test["baseline_mean"],
        "baseline_std": test["baseline_std"],
        "percentile": test["percentile"],
        "p_value": test["p_value"],
        "reasons": reasons,
    }


def render_markdown(summary: Dict[str, Any]) -> str:
    """Render an inert human-readable significance report."""
    s = summary
    lines = [
        "# Entry-Rule Significance",
        "",
        f"## Verdict: **{s['verdict']}**",
        "",
        f"- horizon: {s['horizon']}",
        f"- real_count (signals used): {s['real_count']}",
        f"- baseline entries per draw (n_signals): {s['n_signals']}",
        f"- n_iter (random draws): {s['n_iter']}",
        f"- seed: {s['seed']}",
        f"- real_mean forward return: {s['real_mean']:.5f}",
        f"- baseline_mean forward return: {s['baseline_mean']:.5f}",
        f"- baseline_std: {s['baseline_std']:.5f}",
        f"- percentile vs random: {s['percentile']:.1f}",
        f"- p_value (one-sided): {s['p_value']:.4f}",
        "",
        "## Reasons",
    ]
    lines.extend(f"- {r}" for r in s["reasons"])
    lines.append("")
    return "\n".join(lines)

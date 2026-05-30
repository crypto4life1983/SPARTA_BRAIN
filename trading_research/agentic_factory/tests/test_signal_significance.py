"""Tests for the entry-rule significance module. Offline, stdlib-only, no I/O."""

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine import signal_significance as sig  # noqa: E402


def _flat_with_planted_edge(n=220, horizon=3, step=20, bump=1.10):
    """Flat 100.0 series; every `step`-th index is followed `horizon` bars
    later by a +10% close. Those indices are the (planted) real signals."""
    closes = [100.0] * n
    signals = list(range(step, n - horizon, step))
    for s in signals:
        closes[s + horizon] = 100.0 * bump
    bars = [{"close": c} for c in closes]
    return bars, signals, horizon


def _noise_walk(n=260, seed=2024):
    """Deterministic zero-drift random walk around 100."""
    rng = random.Random(seed)
    closes = [100.0]
    for _ in range(n - 1):
        closes.append(closes[-1] + rng.uniform(-1.0, 1.0))
    return [{"close": c} for c in closes]


def test_deterministic_output_under_fixed_seed():
    bars, _signals, horizon = _flat_with_planted_edge()
    a = sig.random_entry_baseline(bars, n_signals=5, horizon=horizon, n_iter=50, seed=7)
    b = sig.random_entry_baseline(bars, n_signals=5, horizon=horizon, n_iter=50, seed=7)
    assert a == b
    assert len(a) == 50


def test_planted_edge_gives_strong_percentile_and_low_p():
    bars, signals, horizon = _flat_with_planted_edge()
    out = sig.summarize_significance(bars, signals, horizon, n_iter=500, seed=11)
    assert out["verdict"] == sig.EDGE_LIKELY
    assert out["percentile"] >= 95.0
    assert out["p_value"] <= 0.05
    assert out["real_mean"] > out["baseline_mean"]


def test_pure_noise_does_not_falsely_show_edge():
    bars = _noise_walk()
    # Systematic every-10th-index signals: mean forward return ~ population mean,
    # so it must NOT be flagged as edge.
    signals = list(range(0, len(bars) - 5, 10))
    out = sig.summarize_significance(bars, signals, horizon=5, n_iter=500, seed=99)
    assert out["verdict"] != sig.EDGE_LIKELY


def test_random_baseline_uses_same_count_as_real_signal():
    bars, signals, horizon = _flat_with_planted_edge()
    real = sig.forward_returns(bars, signals, horizon)
    out = sig.summarize_significance(bars, signals, horizon, n_iter=100, seed=5)
    # The baseline is configured with exactly the real usable-signal count.
    assert out["n_signals"] == out["real_count"] == len(real)


def test_p_value_is_bounded_between_0_and_1():
    # Direct cases.
    p1 = sig.permutation_test([0.1, 0.1, 0.1], [0.0] * 100)["p_value"]
    p2 = sig.permutation_test([-0.5], [0.0] * 100)["p_value"]
    assert 0.0 <= p1 <= 1.0
    assert 0.0 <= p2 <= 1.0
    # Full-pipeline cases.
    bars, signals, horizon = _flat_with_planted_edge()
    assert 0.0 <= sig.summarize_significance(bars, signals, horizon, n_iter=200, seed=3)["p_value"] <= 1.0
    noise = _noise_walk()
    nsig = list(range(0, len(noise) - 5, 10))
    assert 0.0 <= sig.summarize_significance(noise, nsig, 5, n_iter=200, seed=3)["p_value"] <= 1.0


def test_empty_or_too_short_inputs_return_safe_no_result():
    # forward_returns: empty bars, and bars shorter than the horizon.
    assert sig.forward_returns([], [0, 1], 3) == []
    assert sig.forward_returns([{"close": 1.0}, {"close": 2.0}], [0], 5) == []
    # baseline: nothing to sample.
    assert sig.random_entry_baseline([], n_signals=3, horizon=3, n_iter=10, seed=1) == []
    assert sig.random_entry_baseline([{"close": 1.0}], n_signals=3, horizon=3, n_iter=10, seed=1) == []
    # permutation_test: empty inputs -> safe, p_value = 1.0.
    pt = sig.permutation_test([], [])
    assert pt["p_value"] == 1.0
    # summarize: no signals and too-short bars -> NO_RESULT, no exception.
    s1 = sig.summarize_significance([], [], 3, n_iter=10, seed=1)
    assert s1["verdict"] == sig.NO_RESULT
    s2 = sig.summarize_significance([{"close": 1.0}, {"close": 2.0}], [0, 1], 5, n_iter=10, seed=1)
    assert s2["verdict"] == sig.NO_RESULT
    assert 0.0 <= s2["p_value"] <= 1.0


def test_bare_number_bars_supported():
    # Bars may be bare numbers (treated as closes).
    bars = [100.0, 100.0, 110.0, 110.0]
    fr = sig.forward_returns(bars, [0], 2)
    assert len(fr) == 1
    assert abs(fr[0] - 0.10) < 1e-9

import pytest


def test_trailing_return(harness):
    sig = harness["signal"]
    closes = [float(i + 1) for i in range(260)]
    assert sig.trailing_return(closes, 200, 126, 21) == pytest.approx(180.0 / 54.0 - 1.0)
    assert sig.trailing_return(closes, 146, 126, 21) is None
    assert sig.trailing_return(closes, 147, 126, 21) is not None


def test_rank_and_select(harness):
    sig = harness["signal"]
    assert sig.cross_sectional_rank({"AAA": 0.1, "BBB": 0.3, "CCC": 0.2, "DDD": None}) == ["BBB", "CCC", "AAA"]
    assert sig.select_top_m(["A", "B", "C", "D", "E", "F", "G", "H", "I"], 8) == list("ABCDEFGH")


def test_fidelity_vs_sealed_s21_primitives(harness, synthetic_prices):
    """Mechanic fidelity: paper-harness signal must match the SEALED s21 harness primitives byte-for-byte."""
    import importlib
    sealed = importlib.import_module("external_research_hunter.s21_d1_broader_universe_weekly_relative_strength_rotation_runner_harness.main")
    sig = harness["signal"]
    syms = list(synthetic_prices.keys())
    for i in (160, 200, 260, 300):
        a = {s: sig.trailing_return(synthetic_prices[s], i, 126, 21) for s in syms}
        b = {s: sealed.trailing_return(synthetic_prices[s], i, 126, 21) for s in syms}
        assert a == b
        assert sig.cross_sectional_rank(a) == sealed.cross_sectional_rank(b)
        assert sig.select_top_m(sig.cross_sectional_rank(a), 8) == sealed.select_top_m(sealed.cross_sectional_rank(b), 8)

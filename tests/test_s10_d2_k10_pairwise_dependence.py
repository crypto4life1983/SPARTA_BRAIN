"""Tests for the S10-D2 K10 pairwise-dependence math.

Only the pure functions are tested here (daily_returns, pearson_corr,
avg_pairwise_corr, align_by_date, build_report verdict logic). The
sealed-driver load path is intentionally NOT exercised in this test file
because it would read ~480 .dbn.zst cache files (~130 MB) and slow CI.
The full live evaluation is exercised by running the script's main()
entry point — see the matching K10 sealed report on disk.

Authorized by: operator phrase
    "Authorize S10-D2 K10 pairwise dependence computation."
"""
from __future__ import annotations

import datetime
import math
import sys
from pathlib import Path

import pytest


_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.external_research_hunter.s10_d2_k10_pairwise_dependence import (  # noqa: E402
    K10_THRESHOLD,
    align_by_date,
    avg_pairwise_corr,
    build_report,
    daily_returns,
    pearson_corr,
)


# --- daily_returns --------------------------------------------------------

def test_daily_returns_basic_10pct_steps():
    out = daily_returns([100.0, 110.0, 121.0])
    assert out == pytest.approx([0.10, 0.10], abs=1e-12)


def test_daily_returns_negative_step():
    out = daily_returns([100.0, 90.0])
    assert out == pytest.approx([-0.10], abs=1e-12)


def test_daily_returns_length_minus_one():
    closes = [1.0, 2.0, 3.0, 4.0, 5.0]
    out = daily_returns(closes)
    assert len(out) == len(closes) - 1


def test_daily_returns_empty_and_single():
    assert daily_returns([]) == []
    assert daily_returns([42.0]) == []


def test_daily_returns_rejects_zero_close():
    with pytest.raises(ValueError):
        daily_returns([0.0, 100.0])


def test_daily_returns_rejects_non_finite():
    with pytest.raises(ValueError):
        daily_returns([100.0, float("inf")])


# --- pearson_corr ---------------------------------------------------------

def test_pearson_perfect_positive():
    assert pearson_corr([1.0, 2.0, 3.0, 4.0], [2.0, 4.0, 6.0, 8.0]) == pytest.approx(1.0, abs=1e-12)


def test_pearson_perfect_negative():
    assert pearson_corr([1.0, 2.0, 3.0, 4.0], [4.0, 3.0, 2.0, 1.0]) == pytest.approx(-1.0, abs=1e-12)


def test_pearson_uncorrelated_symmetric():
    # Pair with average product = 0; should be ~0.
    xs = [1.0, -1.0, 1.0, -1.0]
    ys = [1.0, 1.0, -1.0, -1.0]
    assert pearson_corr(xs, ys) == pytest.approx(0.0, abs=1e-12)


def test_pearson_length_mismatch_raises():
    with pytest.raises(ValueError):
        pearson_corr([1.0, 2.0], [1.0])


def test_pearson_too_few_points_raises():
    with pytest.raises(ValueError):
        pearson_corr([1.0], [1.0])


def test_pearson_constant_series_raises():
    with pytest.raises(ValueError):
        pearson_corr([1.0, 1.0, 1.0], [1.0, 2.0, 3.0])


# --- avg_pairwise_corr ----------------------------------------------------

def test_avg_pairwise_corr_3_symbols_all_pairs_perfect_positive():
    s = {
        "A": [1.0, 2.0, 3.0, 4.0],
        "B": [2.0, 4.0, 6.0, 8.0],
        "C": [3.0, 6.0, 9.0, 12.0],
    }
    avg, pairs = avg_pairwise_corr(s)
    assert set(pairs.keys()) == {"A__B", "A__C", "B__C"}
    assert avg == pytest.approx(1.0, abs=1e-12)


def test_avg_pairwise_corr_4_symbols_yields_6_pairs():
    s = {
        "A": [1.0, 2.0, 3.0, 4.0],
        "B": [2.0, 4.0, 6.0, 8.0],
        "C": [1.0, 3.0, 5.0, 7.0],
        "D": [4.0, 3.0, 2.0, 1.0],
    }
    avg, pairs = avg_pairwise_corr(s)
    assert len(pairs) == 6
    # Hand-recompute: A-B = +1, A-C = +1, A-D = -1, B-C = +1, B-D = -1, C-D = -1
    # Sum = 0, avg = 0
    assert pairs["A__B"] == pytest.approx(+1.0, abs=1e-12)
    assert pairs["A__C"] == pytest.approx(+1.0, abs=1e-12)
    assert pairs["A__D"] == pytest.approx(-1.0, abs=1e-12)
    assert pairs["B__C"] == pytest.approx(+1.0, abs=1e-12)
    assert pairs["B__D"] == pytest.approx(-1.0, abs=1e-12)
    assert pairs["C__D"] == pytest.approx(-1.0, abs=1e-12)
    assert avg == pytest.approx(0.0, abs=1e-12)


def test_avg_pairwise_corr_pairs_are_alphabetical():
    s = {
        "ZN": [1.0, 2.0, 3.0],
        "CL": [1.0, 2.0, 3.0],
        "NQ": [1.0, 2.0, 3.0],
        "GC": [1.0, 2.0, 3.0],
    }
    _, pairs = avg_pairwise_corr(s)
    # All pair keys must be sorted alphabetically: a__b with a < b
    for key in pairs:
        a, b = key.split("__")
        assert a < b, f"pair {key} not in alphabetical order"
    # Expect exactly these 6 pairs for the 4-market basket
    assert set(pairs.keys()) == {
        "CL__GC", "CL__NQ", "CL__ZN",
        "GC__NQ", "GC__ZN",
        "NQ__ZN",
    }


def test_avg_pairwise_corr_too_few_symbols_raises():
    with pytest.raises(ValueError):
        avg_pairwise_corr({"only": [1.0, 2.0, 3.0]})


# --- align_by_date --------------------------------------------------------

def test_align_by_date_inner_joins_common_dates_only():
    d = datetime.date
    a = {d(2020, 1, 1): 1.0, d(2020, 1, 2): 2.0, d(2020, 1, 3): 3.0}
    b = {d(2020, 1, 2): 20.0, d(2020, 1, 3): 30.0, d(2020, 1, 4): 40.0}
    dates, per_sym = align_by_date({"A": a, "B": b})
    # Common dates: 2020-01-02 and 2020-01-03
    assert dates == [d(2020, 1, 2), d(2020, 1, 3)]
    assert per_sym["A"] == [2.0, 3.0]
    assert per_sym["B"] == [20.0, 30.0]


def test_align_by_date_preserves_order():
    d = datetime.date
    a = {d(2020, 3, 1): 30.0, d(2020, 1, 1): 10.0, d(2020, 2, 1): 20.0}
    dates, per_sym = align_by_date({"A": a})
    assert dates == [d(2020, 1, 1), d(2020, 2, 1), d(2020, 3, 1)]
    assert per_sym["A"] == [10.0, 20.0, 30.0]


# --- K10 verdict logic + report seal --------------------------------------

def _minimal_inputs_summary():
    return {
        "in_sample_start": "2013-01-01",
        "in_sample_end": "2022-12-30",
        "cache_root": "C:\\SPARTA_BRAIN\\data\\databento_cache",
        "tier_n_spec_seal_sha256_pinned": "0" * 64,
        "plan_lock_seal_sha256_pinned": "0" * 64,
        "phase2_plan_seal_sha256_pinned": "0" * 64,
        "predecessor_seal_sha256_pinned": "0" * 64,
        "expected_cache_bytes_per_market": {"NQ": 1, "GC": 1, "ZN": 1, "CL": 1},
        "expected_files_per_root": 120,
        "cache_assertion_pass": True,
        "seal_assertion_pass": True,
        "symbols_in_canonical_order": ["NQ.c.0", "GC.c.0", "ZN.c.0", "CL.c.0"],
    }


def test_k10_passes_below_threshold():
    body = build_report(
        avg_corr=0.30,
        pair_corrs={"A__B": 0.30, "A__C": 0.30, "B__C": 0.30},
        common_date_count=100,
        per_symbol_obs_count={"A": 100, "B": 100, "C": 100},
        inputs_summary=_minimal_inputs_summary(),
    )
    assert body["verdict"] == "K10_PASS_AVG_PAIRWISE_CORR_AT_OR_BELOW_0_50"
    assert body["k10_evaluation"]["fires"] is False


def test_k10_passes_exactly_at_threshold():
    # Strictly-greater-than rule: 0.50 must PASS (does not fire)
    body = build_report(
        avg_corr=0.50,
        pair_corrs={"A__B": 0.50, "A__C": 0.50, "B__C": 0.50},
        common_date_count=100,
        per_symbol_obs_count={"A": 100, "B": 100, "C": 100},
        inputs_summary=_minimal_inputs_summary(),
    )
    assert body["verdict"] == "K10_PASS_AVG_PAIRWISE_CORR_AT_OR_BELOW_0_50"
    assert body["k10_evaluation"]["fires"] is False


def test_k10_fires_above_threshold():
    body = build_report(
        avg_corr=0.51,
        pair_corrs={"A__B": 0.51, "A__C": 0.51, "B__C": 0.51},
        common_date_count=100,
        per_symbol_obs_count={"A": 100, "B": 100, "C": 100},
        inputs_summary=_minimal_inputs_summary(),
    )
    assert body["verdict"] == "K10_FIRED_AVG_PAIRWISE_CORR_EXCEEDS_0_50"
    assert body["k10_evaluation"]["fires"] is True


def test_k10_threshold_constant_is_0_50():
    assert K10_THRESHOLD == 0.50


def test_report_includes_seal_and_boundaries():
    body = build_report(
        avg_corr=0.10,
        pair_corrs={"A__B": 0.10},
        common_date_count=50,
        per_symbol_obs_count={"A": 50, "B": 50},
        inputs_summary=_minimal_inputs_summary(),
    )
    assert "report_seal_sha256" in body
    assert len(body["report_seal_sha256"]) == 64
    assert all(c in "0123456789abcdef" for c in body["report_seal_sha256"])
    # Posture invariants must be present and correct
    assert body["trading_status"] == "PAUSED"
    assert body["live_status"] == "BLOCKED_AT_6_GATES"
    assert body["frc_granted"] is False
    assert body["advisory_label_permanent"] == "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE"
    # Hard boundaries: a sample of the no_* flags must all be True
    b = body["boundaries_held"]
    for k in (
        "no_databento_call",
        "no_databento_api_key_access",
        "no_external_network_call",
        "no_cache_mutation",
        "no_strategy_optimization_authorized",
        "no_tier_n_spec_mutation",
        "no_live_trading",
        "no_broker_call",
        "no_oos_inspection",
    ):
        assert b[k] is True, f"boundary {k} must be True"


def test_report_seal_is_deterministic_for_same_inputs():
    """Same inputs (except authored_at_utc) -> same sha after seal. We
    canonicalize on the body excluding seal fields; the authored_at_utc
    field is included in the body, so to test determinism we recompute
    twice and compare the body-minus-timestamp shas."""
    import hashlib
    import json as _json
    b1 = build_report(0.42, {"A__B": 0.42}, 10, {"A": 10, "B": 10}, _minimal_inputs_summary())
    b2 = build_report(0.42, {"A__B": 0.42}, 10, {"A": 10, "B": 10}, _minimal_inputs_summary())
    # Strip seal + timestamp fields
    for b in (b1, b2):
        b.pop("report_seal_sha256", None)
        b.pop("seal_method", None)
        b.pop("authored_at_utc", None)
    c1 = hashlib.sha256(_json.dumps(b1, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    c2 = hashlib.sha256(_json.dumps(b2, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    assert c1 == c2

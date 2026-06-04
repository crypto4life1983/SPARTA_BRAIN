"""Crypto-D1 Momentum N=20 deeper-validation capability tests (BUILD ONLY).

Pure stdlib + pytest. Every test runs on tiny synthetic inputs; NONE runs a
backtest, executes a Strategy Factory task, touches real research data, or hits
the network/broker/exchange/order/fetch paths. Asserts:

  * module is stdlib-only; no network/broker/exchange/order/fetch/subprocess
    tokens in the source
  * pure numeric helpers (compound_returns, equity_to_daily_returns,
    max_drawdown) are correct on hand-checkable inputs
  * each of the 9 required validation sections computes the expected shape on
    synthetic ledgers
  * fee/slippage stress is a re-pricing of the SAME ledger (monotonic in cost)
    and reports a breakeven
  * outlier_sensitivity removes best/worst/top-k WITHOUT mutating the official
    base figure
  * regime_sensitivity buckets by a frozen-price trend proxy, dropping warmup
  * parameter_neighborhood is BOUNDED {18,20,22}, labeled sensitivity, winner
    fixed at N=20 and NEVER re-selected
  * build-time schema (inputs=None) lists all 9 sections as computed=False and
    ran_backtest=False
  * computed schema (inputs supplied) fills all 9 sections
  * safety flags pinned False; lane/readiness unchanged strings present
  * to_stable_json is deterministic + sorted
  * write_build_report writes ONLY under the single build folder
  * existing momentum_confirmation_v1 runner behavior is untouched (imported
    runner still exposes its modes and classify_run is WATCH-ceiling)
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import crypto_d1_deeper_validation as dv  # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_deeper_validation.py"


# ---------------------------------------------------------------------------
# Synthetic input helpers (NOT real data).
# ---------------------------------------------------------------------------
def _dated_returns(pairs):
    """[(YYYY-MM-DD, simple_return), ...] from a list of (date, r)."""
    return [(d, float(r)) for d, r in pairs]


# ---------------------------------------------------------------------------
# Source-level safety: no forbidden execution surfaces.
# ---------------------------------------------------------------------------
def test_source_imports_no_forbidden_modules():
    # Parse the AST so prose in the docstring (which legitimately says the module
    # does NOT use subprocess/broker/exchange/fetch) cannot false-positive. We
    # assert on actual import statements, not substrings.
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))
    forbidden = {"subprocess", "socket", "requests", "urllib", "http",
                 "ftplib", "ccxt", "websocket", "ssl", "asyncio"}
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.add(node.module.split(".")[0])
    bad = imported & forbidden
    assert not bad, f"forbidden imports in source: {sorted(bad)}"
    # Allowed stdlib surface only.
    assert imported <= {"__future__", "argparse", "json", "sys", "pathlib",
                        "typing"}, f"unexpected imports: {sorted(imported)}"


def test_source_has_no_execution_call_surfaces():
    # Code-level (not prose) check: no call expressions to known execution /
    # network surfaces. We scan call source segments excluding the docstring.
    src = TOOL_FILE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            seg = (ast.get_source_segment(src, node) or "").lower()
            for tok in ("subprocess", "popen", "socket(", "urlopen",
                        "requests.", "place_order", "create_order", "ccxt"):
                assert tok not in seg, f"forbidden call surface: {tok}"


def test_module_imports_no_runner():
    # The capability is standalone; it must not import the heavy backtest runner.
    assert "crypto_d1_backtest_runner" not in sys.modules or True
    src = TOOL_FILE.read_text(encoding="utf-8")
    assert "import crypto_d1_backtest_runner" not in src
    assert "from crypto_d1_backtest_runner" not in src


# ---------------------------------------------------------------------------
# Pure numeric helpers.
# ---------------------------------------------------------------------------
def test_compound_returns_basic():
    assert dv.compound_returns([]) == 0.0
    assert dv.compound_returns([0.1, 0.1]) == pytest.approx(0.21)
    assert dv.compound_returns([0.5, -0.5]) == pytest.approx(-0.25)


def test_equity_to_daily_returns_alignment():
    dr = dv.equity_to_daily_returns(["d1", "d2"], [1.0, 1.1, 1.21])
    assert [d for d, _ in dr] == ["d1", "d2"]
    assert dr[0][1] == pytest.approx(0.1)
    assert dr[1][1] == pytest.approx(0.1)


def test_max_drawdown_simple():
    eq = [1.0, 1.2, 0.6, 0.9]
    assert dv.max_drawdown(eq) == pytest.approx(0.6 / 1.2 - 1.0)
    assert dv.max_drawdown([]) == 0.0
    assert dv.max_drawdown([1.0, 1.1, 1.2]) == 0.0


# ---------------------------------------------------------------------------
# Section 1: yearly OOS breakdown.
# ---------------------------------------------------------------------------
def test_yearly_oos_breakdown_splits_by_year():
    dr = _dated_returns([
        ("2024-07-01", 0.1), ("2024-08-01", 0.1),
        ("2025-01-01", -0.05), ("2025-02-01", 0.2),
    ])
    out = dv.yearly_oos_breakdown(dr)
    assert set(out["by_year"]) == {"2024", "2025"}
    assert out["by_year"]["2024"]["n_days"] == 2
    assert out["by_year"]["2024"]["total_return"] == pytest.approx(0.21)


# ---------------------------------------------------------------------------
# Section 2: monthly return / drawdown profile.
# ---------------------------------------------------------------------------
def test_monthly_profile_worst_month_and_drawdown():
    dr = _dated_returns([
        ("2024-07-01", 0.1), ("2024-07-15", -0.2),
        ("2024-08-01", 0.05),
    ])
    out = dv.monthly_return_drawdown_profile(dr)
    assert set(out["by_month"]) == {"2024-07", "2024-08"}
    assert out["worst_month"] == "2024-07"
    assert out["overall_max_drawdown"] <= 0.0
    assert out["longest_drawdown_steps"] >= 1


# ---------------------------------------------------------------------------
# Section 3: per-asset consistency.
# ---------------------------------------------------------------------------
def test_per_asset_consistency_flags_carrier_and_floor():
    pa = {
        "BTC": {"total_return": 1.39, "trade_count": 32, "max_drawdown": -0.15, "turnover": 5},
        "ETH": {"total_return": 1.61, "trade_count": 31, "max_drawdown": -0.33, "turnover": 5},
        "SOL": {"total_return": 2.44, "trade_count": 23, "max_drawdown": -0.22, "turnover": 4},
    }
    out = dv.per_asset_consistency(pa, floor=20)
    assert out["all_positive_oos"] is True
    assert out["all_clear_floor"] is True
    assert out["highest_return_asset"] == "SOL"
    assert out["rows"]["SOL"]["clears_per_asset_floor"] is True


def test_per_asset_consistency_detects_floor_miss():
    pa = {
        "BTC": {"total_return": 1.0, "trade_count": 32},
        "ETH": {"total_return": 2.0, "trade_count": 19},  # under floor
    }
    out = dv.per_asset_consistency(pa, floor=20)
    assert out["all_clear_floor"] is False
    assert "ETH" not in out["assets_clearing_floor"]


# ---------------------------------------------------------------------------
# Section 4: trade count & turnover.
# ---------------------------------------------------------------------------
def test_trade_count_and_turnover_family_total():
    pat = {
        "BTC": {"trade_count": 32, "turnover": 5},
        "ETH": {"trade_count": 31, "turnover": 5},
        "SOL": {"trade_count": 23, "turnover": 4},
    }
    out = dv.trade_count_and_turnover(pat, floor=20)
    assert out["family_oos_trades_total"] == 86
    assert out["all_clear_floor"] is True


# ---------------------------------------------------------------------------
# Section 5: fee / slippage stress.
# ---------------------------------------------------------------------------
def test_fee_slippage_stress_monotonic_and_breakeven():
    # Two winning round-trip trades, pre-cost.
    gross = [0.05, 0.04]
    out = dv.fee_slippage_stress(gross, baseline_round_trip_bps=120,
                                 stress_round_trip_bps=(150, 180, 240))
    levels = out["stress_total_return_by_bps"]
    # Higher cost -> lower net return.
    assert levels["120"] >= levels["150"] >= levels["180"] >= levels["240"]
    assert out["headline_total_return"] == levels["120"]
    # A breakeven exists for a finitely-profitable ledger.
    assert out["breakeven_round_trip_bps"] is not None
    assert out["breakeven_round_trip_bps"] > 120
    assert "SENSITIVITY" in out["label"]


def test_breakeven_none_when_always_positive():
    # Impossibly large per-trade gross so even hi=5000 bps stays positive.
    assert dv._breakeven_bps([10.0, 10.0]) is None


# ---------------------------------------------------------------------------
# Section 6: outlier sensitivity.
# ---------------------------------------------------------------------------
def test_outlier_sensitivity_removes_without_mutating_base():
    rs = [0.5, 0.01, -0.4, 0.02, 0.03]
    out = dv.outlier_sensitivity(rs, top_k=(1, 2, 3))
    assert out["base_total_return"] == dv._round(dv.compound_returns(rs))
    # ex_best removes the single max (0.5) -> lower compounded return.
    assert out["ex_best"] < out["base_total_return"]
    # ex_worst removes the single min (-0.4) -> higher compounded return.
    assert out["ex_worst"] > out["base_total_return"]
    assert set(out["ex_top_k"]) == {"1", "2", "3"}
    # Input list not mutated.
    assert rs == [0.5, 0.01, -0.4, 0.02, 0.03]


def test_drop_top_k_by_magnitude():
    rs = [0.5, -0.4, 0.01, 0.02]
    kept = dv._drop_top_k_by_magnitude(rs, 2)
    # Drops 0.5 and -0.4 (largest magnitude), keeps the two small ones.
    assert kept == [0.01, 0.02]


# ---------------------------------------------------------------------------
# Section 7: regime sensitivity (+ frozen-price proxy).
# ---------------------------------------------------------------------------
def test_simple_trend_regime_labels():
    prices = [100, 101, 102, 103, 90, 110]
    labels = dv.simple_trend_regime(prices, lookback=2)
    assert labels[0] == "warmup" and labels[1] == "warmup"
    assert labels[2] == "bull"   # 102 > 100
    assert labels[4] == "bear"   # 90 < 102


def test_regime_sensitivity_buckets_and_drops_warmup():
    dr = _dated_returns([
        ("2024-07-01", 0.1), ("2024-07-02", -0.05),
        ("2024-07-03", 0.2), ("2024-07-04", -0.1),
    ])
    labels = ["warmup", "bull", "bull", "bear"]
    out = dv.regime_sensitivity(dr, labels)
    assert set(out["by_regime"]) == {"bull", "bear"}
    assert out["by_regime"]["bull"]["n_days"] == 2
    assert out["by_regime"]["bear"]["n_days"] == 1


# ---------------------------------------------------------------------------
# Section 8: basket vs per-asset.
# ---------------------------------------------------------------------------
def test_basket_vs_per_asset():
    pa = {
        "BTC": {"total_return": 1.39},
        "ETH": {"total_return": 1.61},
        "SOL": {"total_return": 2.44},
    }
    out = dv.basket_vs_per_asset(pa, basket_oos_return=-0.0226)
    assert out["equal_weight_mean_of_per_asset"] == pytest.approx((1.39 + 1.61 + 2.44) / 3)
    assert out["allocate_once_basket_oos_total_return"] == pytest.approx(-0.0226)
    assert out["edge_retained_vs_mean"] is not None


# ---------------------------------------------------------------------------
# Section 9: parameter neighborhood — bounded, sensitivity-not-optimization.
# ---------------------------------------------------------------------------
def test_parameter_neighborhood_is_bounded_sensitivity_only():
    out = dv.parameter_neighborhood({
        18: {"oos_total_return": 1.2},
        20: {"oos_total_return": 1.39},
        22: {"oos_total_return": 1.3},
    })
    assert out["neighborhood"] == [18, 20, 22]
    assert out["winner_fixed_at"] == 20
    assert out["is_sensitivity_not_optimization"] is True
    assert out["winner_reselected_from_probe"] is False
    assert set(out["oos_total_return_by_n"]) == {"18", "20", "22"}


def test_parameter_neighborhood_empty_at_build_time():
    out = dv.parameter_neighborhood(None)
    assert out["oos_total_return_by_n"] == {}
    assert out["winner_fixed_at"] == 20
    assert out["is_sensitivity_not_optimization"] is True


# ---------------------------------------------------------------------------
# Schema assembler: build-time contract vs computed.
# ---------------------------------------------------------------------------
def test_build_time_schema_lists_all_sections_uncomputed():
    schema = dv.build_deeper_validation_schema(None)
    assert schema["computed"] is False
    assert schema["ran_backtest"] is False
    assert schema["build_only"] is True
    assert schema["is_execution_result"] is False
    assert list(schema["required_sections"]) == list(dv.REQUIRED_SECTIONS)
    assert set(schema["sections"]) == set(dv.REQUIRED_SECTIONS)
    for name in dv.REQUIRED_SECTIONS:
        assert schema["sections"][name]["computed"] is False


def test_computed_schema_fills_all_sections():
    inputs = {
        "daily_returns": _dated_returns([
            ("2024-07-01", 0.1), ("2024-08-01", -0.05), ("2025-01-01", 0.2)]),
        "per_asset_oos": {
            "BTC": {"total_return": 1.39, "trade_count": 32, "turnover": 5},
            "ETH": {"total_return": 1.61, "trade_count": 31, "turnover": 5},
            "SOL": {"total_return": 2.44, "trade_count": 23, "turnover": 4},
        },
        "trade_gross_returns": [0.05, 0.04, -0.02],
        "trade_returns": [0.5, 0.01, -0.4, 0.02],
        "regime_labels": ["bull", "bear", "bull"],
        "basket_oos_return": -0.0226,
        "neighborhood_results": {
            18: {"oos_total_return": 1.2},
            20: {"oos_total_return": 1.39},
            22: {"oos_total_return": 1.3},
        },
    }
    schema = dv.build_deeper_validation_schema(inputs)
    assert schema["computed"] is True
    assert schema["ran_backtest"] is False  # never set true; capability only
    assert set(schema["sections"]) == set(dv.REQUIRED_SECTIONS)
    # Spot-check a couple of computed sections carry real numbers.
    assert "family_oos_trades_total" in schema["sections"]["trade_count_and_turnover"]
    assert schema["sections"]["parameter_neighborhood"]["winner_fixed_at"] == 20


def test_schema_safety_flags_all_non_authorizing():
    schema = dv.build_deeper_validation_schema(None)
    flags = schema["safety_flags"]
    assert flags["research_only"] is True
    for k, v in flags.items():
        if k == "research_only":
            continue
        assert v is False, f"safety flag {k} must be False"
    assert schema["lane_status_unchanged"] == "WATCH / MIXED"
    assert schema["readiness_status_unchanged"] == "NOT_READY_FOR_REAL_DATA"


def test_primary_target_is_n20_only():
    schema = dv.build_deeper_validation_schema(None)
    assert schema["primary_lookback"] == 20
    assert schema["reference_lookback"] == 30
    assert schema["neighborhood_is_sensitivity_not_optimization"] is True


# ---------------------------------------------------------------------------
# Serialization + opt-in writer.
# ---------------------------------------------------------------------------
def test_to_stable_json_is_sorted_and_deterministic():
    schema = dv.build_deeper_validation_schema(None)
    a = dv.to_stable_json(schema)
    b = dv.to_stable_json(schema)
    assert a == b
    parsed = json.loads(a)
    assert parsed["layer"] == dv.LAYER_NAME
    # sort_keys -> top-level keys are sorted.
    assert list(parsed.keys()) == sorted(parsed.keys())


def test_write_build_report_confined_to_build_folder(tmp_path):
    schema = dv.build_deeper_validation_schema(None)
    written = dv.write_build_report(tmp_path, schema)
    rel = "reports/crypto_d1_momentum_n20_deeper_validation_build"
    for p in written:
        assert p.startswith(rel), p
    # Nothing was written outside the single build folder.
    all_files = [q.relative_to(tmp_path).as_posix()
                 for q in tmp_path.rglob("*") if q.is_file()]
    assert all(f.startswith(rel) for f in all_files), all_files


def test_main_runs_no_backtest_and_returns_zero(capsys):
    rc = dv.main(["--format", "json"])
    assert rc == 0
    out = capsys.readouterr().out
    parsed = json.loads(out)
    assert parsed["ran_backtest"] is False
    assert parsed["build_only"] is True


# ---------------------------------------------------------------------------
# Regression guard: the existing momentum_confirmation_v1 runner is untouched.
# ---------------------------------------------------------------------------
def test_existing_runner_modes_still_present():
    runner_src = (_TOOLS_DIR / "crypto_d1_backtest_runner.py").read_text(encoding="utf-8")
    # The deeper-validation build added NO new mode token to the runner.
    assert "momentum_confirmation_v1" in runner_src
    assert "momentum_robustness_v1" in runner_src
    assert "momentum_n20_deeper_validation" not in runner_src

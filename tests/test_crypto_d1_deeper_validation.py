"""Tests for the reconciled Crypto-D1 Momentum N=20 deeper-validation layer.

Pure stdlib + pytest, synthetic fixtures only. Asserts:
  * the deeper-validation mode/config exists and N=20 is the PRIMARY target;
  * the {18,20,22} neighborhood is bounded + labeled sensitivity, not
    optimization (winner never re-selected, primary stays 20);
  * the report schema includes all nine required validation sections;
  * safety flags stay pinned false; non-authorization statement present;
  * no network / no subprocess / no broker / no order / no fetch paths;
  * the module imports the runner only (no parallel cost-model re-implementation
    of _simulate_equity) and runs no full frozen-data backtest;
  * momentum_confirmation_v1 runner behavior is untouched (smoke import check);
  * the deterministic JSON serializer is byte-stable;
  * the opt-in writer is confined to the single build folder;
  * the read-only CLI returns 0 and runs no simulation.
"""
from __future__ import annotations

import ast
import io
import json
import sys
import tokenize
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import crypto_d1_backtest_runner as cbr  # noqa: E402
import crypto_d1_deeper_validation as dv  # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_deeper_validation.py"


# ---------------------------------------------------------------------------
# Synthetic Bar fixture -- deterministic, NEVER touches real research data.
# ---------------------------------------------------------------------------
def _bars(symbol: str, closes, start="2024-06-17"):
    from datetime import datetime, timedelta
    d0 = datetime.strptime(start, "%Y-%m-%d")
    out = []
    for i, c in enumerate(closes):
        ts = (d0 + timedelta(days=i)).strftime("%Y-%m-%d")
        out.append(cbr.Bar(timestamp=ts, open=c, high=c, low=c, close=float(c),
                           volume=1.0, symbol=symbol, source="synthetic",
                           quote_currency="USD"))
    return out


def _trending_closes(n, base=100.0, step=1.0, wobble=0.0):
    """Mild uptrend with optional alternating wobble so momentum opens trades."""
    out = []
    price = base
    for i in range(n):
        price += step + (wobble if i % 2 == 0 else -wobble)
        out.append(price)
    return out


def _three_assets(n=200):
    return [
        {"asset": "BTC", "bars": _bars("BTCUSDT", _trending_closes(n, 100, 1.0, 3.0))},
        {"asset": "ETH", "bars": _bars("ETHUSDT", _trending_closes(n, 50, 0.5, 2.0))},
        {"asset": "SOL", "bars": _bars("SOLUSDT", _trending_closes(n, 20, 0.3, 1.5))},
    ]


# ---------------------------------------------------------------------------
# Identity / mode-exists
# ---------------------------------------------------------------------------
def test_mode_config_exists_and_primary_is_n20():
    assert dv.CONFIG_NAME == "momentum_n20_deeper_validation_v1"
    assert dv.PRIMARY_LOOKBACK == 20
    assert dv.REFERENCE_LOOKBACK == 30
    plan = dv.show_plan()
    assert plan["config_name"] == "momentum_n20_deeper_validation_v1"
    assert plan["primary_lookback"] == 20
    assert plan["build_only"] is True
    assert plan["executes_backtest"] is False


def test_neighborhood_is_bounded_sensitivity_not_optimization():
    assert dv.NEIGHBORHOOD_LOOKBACKS == (18, 20, 22)
    assert 20 in dv.NEIGHBORHOOD_LOOKBACKS
    assert len(dv.NEIGHBORHOOD_LOOKBACKS) == 3
    bars = _bars("BTCUSDT", _trending_closes(120, 100, 1.0, 3.0))
    n = dv.neighborhood_sensitivity(bars, cbr.DEFAULT_START_EQUITY)
    assert n["is_sensitivity_not_optimization"] is True
    assert n["winner_reselected"] is False
    assert n["primary_lookback"] == 20
    assert n["per_lookback"]["20"]["is_primary"] is True
    assert n["per_lookback"]["18"]["is_primary"] is False
    assert n["per_lookback"]["22"]["is_primary"] is False


# ---------------------------------------------------------------------------
# Full report schema -- all nine sections present
# ---------------------------------------------------------------------------
def test_report_has_all_nine_validation_sections():
    rep = dv.build_deeper_validation_report(_three_assets(n=220))
    secs = rep["validation_sections"]
    for key in dv.VALIDATION_SECTION_KEYS:
        assert key in secs, f"missing section {key}"
    assert rep["config_mode"] == "momentum_n20_deeper_validation_v1"
    assert rep["executes_backtest"] is False
    assert rep["primary_lookback"] == 20
    assert rep["verdict_ceiling"] == "WATCH"


def test_report_is_json_serializable_and_deterministic():
    fixt = _three_assets(n=210)
    a = dv.build_deeper_validation_report(fixt)
    b = dv.build_deeper_validation_report(fixt)
    sa = json.dumps(a, sort_keys=True, default=str)
    sb = json.dumps(b, sort_keys=True, default=str)
    assert sa == sb  # pure analysis -> byte-identical


# ---------------------------------------------------------------------------
# Per-section behavior
# ---------------------------------------------------------------------------
def test_yearly_and_monthly_breakdowns_populated():
    bars = _bars("BTCUSDT", _trending_closes(420, 100, 1.0, 3.0))  # spans 2 years
    pos, err = cbr.momentum_continuation(bars, 20)
    assert err is None
    yr = dv.yearly_oos_breakdown(bars, pos, cbr.DEFAULT_START_EQUITY)
    assert len(yr) >= 2
    for d in yr.values():
        assert "total_return" in d and "trade_count" in d and "max_drawdown" in d
    mo = dv.monthly_return_drawdown(bars, pos, cbr.DEFAULT_START_EQUITY)
    assert mo["per_month"]
    assert "longest_drawdown_bars" in mo and "worst_month" in mo


def test_fee_stress_is_additive_and_baseline_120():
    bars = _bars("BTCUSDT", _trending_closes(160, 100, 1.0, 3.0))
    pos, _ = cbr.momentum_continuation(bars, 20)
    s = dv.fee_slippage_stress(bars, pos, cbr.DEFAULT_START_EQUITY)
    assert s["baseline_round_trip_bps"] == 120.0
    assert set(s["stress_levels"]) == {"150", "180", "240"}
    # Higher cost never increases return (monotonic non-increasing).
    base = s["baseline_total_return"]
    assert s["stress_levels"]["150"]["total_return"] <= base + 1e-9
    assert s["stress_levels"]["240"]["total_return"] <= s["stress_levels"]["180"]["total_return"] + 1e-9


def test_outlier_and_regime_sections_shape():
    bars = _bars("BTCUSDT", _trending_closes(180, 100, 1.0, 4.0))
    pos, _ = cbr.momentum_continuation(bars, 20)
    o = dv.outlier_sensitivity(bars, pos)
    assert "compounded_trade_return_all" in o and "edge_outlier_dependent" in o
    r = dv.regime_sensitivity(bars, pos, cbr.DEFAULT_START_EQUITY)
    assert r["proxies"]["look_ahead"] is False
    assert set(("low_vol", "high_vol", "uptrend", "downtrend")).issubset(r["buckets"])


def test_per_asset_consistency_and_basket():
    rep = dv.build_deeper_validation_report(_three_assets(n=220))
    cons = rep["validation_sections"]["3_per_asset_consistency"]
    assert set(cons["per_asset"]) == {"BTC", "ETH", "SOL"}
    basket = rep["validation_sections"]["8_basket_vs_per_asset"]
    assert basket["rebalance"] == "none (allocate once)"
    assert "equal_weight_basket_oos_return" in basket


# ---------------------------------------------------------------------------
# Cost single-source-of-truth
# ---------------------------------------------------------------------------
def test_baseline_round_trip_derived_from_runner_constants():
    expected = 2.0 * (cbr.V002_FALLBACK_FEE_BPS + cbr.V002_FALLBACK_SLIPPAGE_BPS
                      + cbr.V002_FALLBACK_SPREAD_PROXY_BPS)
    assert dv.BASELINE_ROUND_TRIP_BPS == expected == 120.0


# ---------------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------------
def test_safety_flags_pinned_false():
    rep = dv.build_deeper_validation_report(_three_assets(n=120))
    flags = rep["safety_flags"]
    assert flags["research_only"] is True
    for k in ("paper_live_authorized", "broker_path_enabled", "exchange_path_enabled",
              "order_path_enabled", "fetch_live_data_enabled", "dataset_mutation_allowed",
              "active_strong_promoted", "bundle_23_started", "execution_authorized"):
        assert flags[k] is False, f"{k} must be pinned false"
    assert rep["non_authorization_statement"]


def _code_names_and_strings(src: str):
    """Return (code identifiers, code string-literal contents) with comments and
    docstring/prose removed -- so safety PROSE mentioning e.g. 'subprocess' is
    not mistaken for an execution path."""
    names, strings = set(), []
    toks = tokenize.generate_tokens(io.StringIO(src).readline)
    for tok in toks:
        if tok.type == tokenize.NAME:
            names.add(tok.string)
        elif tok.type == tokenize.STRING:
            strings.append(tok.string)
    return names, strings


def test_source_has_no_execution_or_network_paths():
    src = TOOL_FILE.read_text(encoding="utf-8")
    names, strings = _code_names_and_strings(src)
    # Forbidden execution/network identifiers must not appear as CODE names.
    for bad in ("subprocess", "socket", "urllib", "requests", "ccxt", "Popen",
                "system", "popen"):
        assert bad not in names, f"forbidden code identifier: {bad!r}"
    # No URL/exchange/credential literals in actual string constants.
    joined = "".join(strings).lower()
    for bad in ("http://", "https://", "binance.com", "private_key",
                "api_secret", "place_order"):
        assert bad not in joined, f"forbidden string literal: {bad!r}"


def test_module_imports_allowlist_only():
    src = TOOL_FILE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                imported.add(a.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    allowed = {"argparse", "json", "sys", "pathlib", "datetime",
               "crypto_d1_backtest_runner", "__future__"}
    assert imported <= allowed, f"unexpected imports: {imported - allowed}"
    for bad in ("subprocess", "socket", "urllib", "requests", "http", "ccxt"):
        assert bad not in imported, f"unexpected import: {bad}"


def test_source_has_no_execution_call_surfaces():
    src = TOOL_FILE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    forbidden_attrs = {"Popen", "run", "call", "system", "popen", "urlopen",
                       "connect", "request", "place_order", "create_order"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute) and f.attr in forbidden_attrs:
                # cbr._simulate_equity etc are fine; flag os/subprocess/socket attrs.
                root = f.value
                root_name = root.id if isinstance(root, ast.Name) else None
                assert root_name not in ("os", "subprocess", "socket", "urllib"), (
                    f"forbidden call surface: {root_name}.{f.attr}")


def test_reuses_runner_simulator_single_source_of_truth():
    # The helper must delegate cost/equity math to the runner, not re-implement it.
    src = TOOL_FILE.read_text(encoding="utf-8")
    assert "crypto_d1_backtest_runner" in src
    assert "_simulate_equity" in src
    assert "momentum_continuation" in src


def test_runner_confirmation_mode_untouched_smoke():
    # momentum_confirmation_v1 wiring still present & importable (no regression).
    assert cbr.MOMENTUM_CONFIRMATION_CONFIG_NAME == "momentum_confirmation_v1"
    assert cbr.MOMENTUM_CONFIRMATION_LOOKBACKS == (20, 30)


def test_insufficient_history_is_noted_not_crashed():
    # Fewer than lookback+1 bars -> momentum skips; report still assembles.
    short = [{"asset": "BTC", "bars": _bars("BTCUSDT", _trending_closes(10))}]
    rep = dv.build_deeper_validation_report(short)
    assert "BTC" in rep["insufficient_history_notes"]
    assert rep["validation_sections"]["4_trade_count_and_turnover"]["per_asset"] == {}


# ---------------------------------------------------------------------------
# Deterministic serializer + confined writer + read-only CLI
# ---------------------------------------------------------------------------
def test_to_stable_json_is_byte_stable():
    plan = dv.show_plan()
    a = dv.to_stable_json(plan)
    b = dv.to_stable_json(plan)
    assert a == b
    assert a.endswith("\n")
    assert json.loads(a) == plan
    assert a == json.dumps(plan, indent=2, sort_keys=True, ensure_ascii=False,
                           default=str) + "\n"


def test_write_build_report_is_confined_to_build_folder(tmp_path):
    written = dv.write_build_report(tmp_path, dv.show_plan())
    assert written == [
        "reports/crypto_d1_momentum_n20_deeper_validation_build/capability_plan.json"
    ]
    target = tmp_path / written[0]
    assert target.is_file()
    # Nothing written outside the single build folder.
    all_files = [p for p in tmp_path.rglob("*") if p.is_file()]
    assert all_files == [target]
    build_dir = tmp_path / "reports" / "crypto_d1_momentum_n20_deeper_validation_build"
    assert build_dir in target.parents


def test_cli_main_returns_zero_and_runs_no_simulation(capsys):
    rc = dv.main([])
    assert rc == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["config_name"] == "momentum_n20_deeper_validation_v1"
    assert payload["executes_backtest"] is False

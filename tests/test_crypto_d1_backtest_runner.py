"""Bundle 16 -- Crypto-D1 Backtest Runner v1 tests (research-only).

Pure stdlib + pytest. Asserts:
  * runner is stdlib-only; no network/broker/exchange/credentials/subprocess
  * validate-config rejects out-of-bound fee/slippage
  * show-plan emits the pre-registered plan
  * missing data dir fails safely (FAIL, no fabricated metrics)
  * empty data dir fails safely
  * valid tiny BTC-only CSV runs and writes both JSON + MD reports
  * BTC + ETH + SOL coverage runs all strategies on all assets
  * invalid OHLC row is rejected (not silently kept)
  * duplicate (symbol, timestamp) row is rejected
  * negative volume row is rejected
  * missing close cell is rejected
  * missing-asset reporting works
  * buy-and-hold benchmark always exists (when >= 2 bars)
  * Donchian strategy runs when history is sufficient
  * MA filter skips with reason on insufficient history
  * Momentum skips with reason on insufficient history
  * Mean reversion is always SKIPPED_WATCH_ONLY in v1
  * cost model applies on trades (total_cost_paid > 0 when trades happen)
  * fee_bps bounds enforced
  * slippage_bps bounds enforced
  * IS/OOS fields exist on every RAN strategy
  * safety flags pinned False in the emitted report
  * report MD says research-only
  * runner source contains NO paper/live/order-execution code paths
  * deterministic on same input (modulo generated_at)
  * pass_watch_fail_status is set on every report
  * report files land at out_dir
  * no committed CSV / parquet under reports/crypto_d1_backtest_runner_v1/
  * no committed real data files
"""
from __future__ import annotations

import ast
import csv
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import crypto_d1_backtest_runner as cbr  # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_backtest_runner.py"


# ---------------------------------------------------------------------------
# Synthetic CSV fixture helper -- writes a deterministic price series into
# tmp_path. NEVER touches real research data; NEVER hits the network.
# ---------------------------------------------------------------------------
def _write_csv(path: Path, symbol: str, n_days: int,
               start_price: float = 100.0,
               drift: float = 0.0010,
               vol: float = 0.012,
               start_date: str = "2023-01-01",
               source: str = "synthetic_test_fixture",
               quote: str = "USDT",
               extra_rows: list | None = None,
               header_override: list | None = None):
    """Write a deterministic synthetic daily-OHLCV CSV. NOT REAL DATA."""
    base = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    rows = []
    p = start_price
    for i in range(n_days):
        d = base + timedelta(days=i)
        # Deterministic 'price walk': drift + small periodic component.
        delta = drift + vol * math.sin(i * 0.13)
        nxt = max(0.01, p * (1 + delta))
        o = p
        c = nxt
        h = max(o, c) * (1 + 0.003)
        lo = min(o, c) * (1 - 0.003)
        v = 1000.0 + 5.0 * i
        rows.append({
            "timestamp": d.strftime("%Y-%m-%d"),
            "open": f"{o:.6f}",
            "high": f"{h:.6f}",
            "low": f"{lo:.6f}",
            "close": f"{c:.6f}",
            "volume": f"{v:.4f}",
            "symbol": symbol,
            "source": source,
            "quote_currency": quote,
        })
        p = nxt
    if extra_rows:
        rows.extend(extra_rows)
    header = header_override or list(cbr.REQUIRED_COLUMNS)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in header})


def _read_json(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


# ===========================================================================
# Tool safety tests
# ===========================================================================
def test_runner_tool_stdlib_only():
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))
    stdlib_ok = {
        "argparse", "csv", "dataclasses", "datetime", "hashlib", "json",
        "math", "pathlib", "sys", "__future__",
    }
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                seen.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            seen.add((node.module or "").split(".")[0])
    extra = seen - stdlib_ok
    assert not extra, f"unexpected imports: {extra}"


def _runner_source_minus_docstrings() -> str:
    """Parse the runner source and return its textual form with the module
    docstring and every function/class docstring stripped. Docstrings often
    state what is forbidden; the string-scan tests should not false-positive
    on those statements."""
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))

    def _strip(body):
        if (body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            body.pop(0)

    _strip(tree.body)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            _strip(node.body)
    return ast.unparse(tree)


def test_runner_tool_no_network_or_broker_or_exchange_imports():
    """AST-based scan: forbid any Import/ImportFrom of network / broker /
    exchange / credential modules. Docstrings cannot cause false positives
    because Import nodes carry module names, not free text."""
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))
    forbidden_modules = {
        "requests", "urllib", "http", "socket", "ssl", "tiingo", "ccxt",
        "alpaca", "binance", "dotenv", "subprocess", "os",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                root = n.name.split(".")[0]
                assert root not in forbidden_modules, \
                    f"forbidden import: {n.name!r}"
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root not in forbidden_modules, \
                f"forbidden from-import: {node.module!r}"

    # Defense-in-depth: scan NON-docstring source for credential / network
    # attribute access patterns (os.environ, os.getenv, urlopen, telegram URL).
    code = _runner_source_minus_docstrings()
    for tok in ("os.environ", "os.getenv", "getenv(", "urlopen", "api.telegram.org"):
        assert tok not in code, f"forbidden attribute / call in runner code: {tok!r}"


def test_runner_source_has_no_paper_or_live_or_order_execution_code():
    """Scan NON-docstring source for trading-action verbs. Docstrings can
    safely mention what is forbidden without triggering this test."""
    code = _runner_source_minus_docstrings().lower()
    forbidden_verbs = (
        "place_order", "submit_order", "send_order", "route_order",
        "execute_order(", "execute_trade", "place_trade", "submit_trade",
        "broker.place", "broker.send", "broker.execute",
        "alpaca.submit", "alpaca.place",
        "binance.create_order", "binance.place",
        "ibkr.placeorder",
        "paper_order_execution_handler",
    )
    for tok in forbidden_verbs:
        assert tok not in code, f"forbidden trading-action token in runner code: {tok!r}"


# ===========================================================================
# Config / plan CLI tests
# ===========================================================================
def test_validate_config_defaults_ok():
    ok, errs = cbr.validate_config()
    assert ok, errs


def test_validate_config_rejects_high_fee():
    ok, errs = cbr.validate_config(fee_bps=999.0, slip_bps=cbr.DEFAULT_SLIPPAGE_BPS)
    assert not ok
    assert any("fee_bps" in e for e in errs)


def test_validate_config_rejects_high_slippage():
    ok, errs = cbr.validate_config(fee_bps=cbr.DEFAULT_TAKER_FEE_BPS, slip_bps=999.0)
    assert not ok
    assert any("slippage_bps" in e for e in errs)


def test_validate_config_rejects_negative_fee():
    ok, errs = cbr.validate_config(fee_bps=-1.0, slip_bps=cbr.DEFAULT_SLIPPAGE_BPS)
    assert not ok
    assert any("fee_bps" in e for e in errs)


def test_validate_config_rejects_negative_slippage():
    ok, errs = cbr.validate_config(fee_bps=cbr.DEFAULT_TAKER_FEE_BPS, slip_bps=-0.1)
    assert not ok
    assert any("slippage_bps" in e for e in errs)


def test_show_plan_emits_required_fields():
    plan = cbr.show_plan()
    for k in ("runner_version", "plan_version", "protocol_version",
              "data_contract_version", "dataset_manifest_spec_version",
              "qa_freeze_spec_version", "target_assets", "allowed_market_type",
              "timeframe", "strategy_families", "cost_model_defaults",
              "safety_flags", "safety_notes", "forbidden_next_steps"):
        assert k in plan, f"show_plan missing key {k}"
    assert plan["target_assets"] == list(cbr.TARGET_ASSETS)
    assert plan["allowed_market_type"] == "spot"
    assert plan["timeframe"] == "1d"
    for flag, val in cbr.SAFETY_FLAGS.items():
        assert plan["safety_flags"][flag] is val


def test_cli_validate_config_ok():
    assert cbr.main(["validate-config"]) == 0


def test_cli_validate_config_fail_on_bad_fee():
    assert cbr.main(["validate-config", "--fee-bps", "9999"]) == 2


def test_cli_show_plan_ok(capsys):
    assert cbr.main(["show-plan"]) == 0
    out = capsys.readouterr().out
    assert "crypto_d1_backtest_runner_v1" in out
    assert "spot" in out


# ===========================================================================
# Missing / empty / unreadable data dir
# ===========================================================================
def test_missing_data_dir_fails_safely(tmp_path):
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=tmp_path / "no_such_dir", out_dir=out)
    assert report["pass_watch_fail_status"] == "FAIL"
    assert any("missing local data" in f for f in report["failures"]) or \
           any("does not exist" in w for w in report["warnings"])
    assert report["strategy_results"] == []
    assert report["assets_seen"] == []
    # Reports still written.
    assert (out / "crypto_d1_backtest_report.json").exists()
    assert (out / "crypto_d1_backtest_report.md").exists()


def test_empty_data_dir_fails_safely(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    assert report["pass_watch_fail_status"] == "FAIL"
    assert report["assets_seen"] == []


# ===========================================================================
# Valid run paths
# ===========================================================================
def test_valid_btc_only_run(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    assert "BTC" in report["assets_seen"]
    assert "ETH" in report["assets_missing"]
    assert "SOL" in report["assets_missing"]
    # Reports written.
    assert (out / "crypto_d1_backtest_report.json").exists()
    assert (out / "crypto_d1_backtest_report.md").exists()
    j = _read_json(out / "crypto_d1_backtest_report.json")
    # Safety flags pinned False (except research_only=True).
    assert j["research_only"] is True
    for flag in ("data_fetch_enabled", "exchange_connection_enabled",
                 "live_trading_enabled", "broker_control_enabled",
                 "paper_order_execution_enabled", "order_placement_enabled"):
        assert j[flag] is False


def test_valid_btc_eth_sol_run(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300, start_price=100.0)
    _write_csv(data_dir / "eth.csv", "ETH", n_days=300, start_price=50.0)
    _write_csv(data_dir / "sol.csv", "SOL", n_days=300, start_price=10.0)
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    assert set(report["assets_seen"]) == {"BTC", "ETH", "SOL"}
    assert report["assets_missing"] == []
    # Each primary family runs on each asset.
    fams_per_asset = {}
    for r in report["strategy_results"]:
        fams_per_asset.setdefault(r["asset"], set()).add(r["family"])
    for asset in ("BTC", "ETH", "SOL"):
        assert "donchian_channel_breakout" in fams_per_asset[asset]
        assert "moving_average_trend_filter" in fams_per_asset[asset]
        assert "momentum_continuation" in fams_per_asset[asset]
        assert "volatility_regime_gate" in fams_per_asset[asset]
        assert "mean_reversion" in fams_per_asset[asset]


# ===========================================================================
# Rejection / row-level validation
# ===========================================================================
def test_invalid_ohlc_row_rejected(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    bad = {"timestamp": "2024-12-31", "open": "100", "high": "50",
           "low": "120", "close": "80", "volume": "1000",
           "symbol": "BTC", "source": "synthetic_test_fixture",
           "quote_currency": "USDT"}
    _write_csv(data_dir / "btc.csv", "BTC", n_days=100, extra_rows=[bad])
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    assert report["rows_rejected"] >= 1
    assert any("high < max" in d or "low > min" in d for d in report["rows_rejected_detail"])


def test_duplicate_symbol_timestamp_row_rejected(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=100)
    # Build a duplicate timestamp on the SAME symbol via a second file.
    _write_csv(data_dir / "btc_dup.csv", "BTC", n_days=10, start_date="2023-01-01")
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    assert report["rows_rejected"] >= 1
    assert any("duplicate" in d for d in report["rows_rejected_detail"])


def test_negative_volume_rejected(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    bad = {"timestamp": "2024-12-31", "open": "100", "high": "110",
           "low": "90", "close": "105", "volume": "-1",
           "symbol": "BTC", "source": "synthetic_test_fixture",
           "quote_currency": "USDT"}
    _write_csv(data_dir / "btc.csv", "BTC", n_days=50, extra_rows=[bad])
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    assert report["rows_rejected"] >= 1
    assert any("negative volume" in d for d in report["rows_rejected_detail"])


def test_missing_close_rejected(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    bad = {"timestamp": "2024-12-31", "open": "100", "high": "110",
           "low": "90", "close": "",
           "volume": "1000",
           "symbol": "BTC", "source": "synthetic_test_fixture",
           "quote_currency": "USDT"}
    _write_csv(data_dir / "btc.csv", "BTC", n_days=50, extra_rows=[bad])
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    assert report["rows_rejected"] >= 1
    assert any("missing close" in d or "unparseable" in d
               for d in report["rows_rejected_detail"])


def test_missing_required_header_column_rejected(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=10,
               header_override=["timestamp", "open", "close", "symbol"])
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    assert report["rows_rejected"] >= 1
    assert any("missing required header columns" in d
               for d in report["rows_rejected_detail"])


# ===========================================================================
# Strategy presence + skip-with-reason
# ===========================================================================
def test_buy_and_hold_benchmark_exists(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    bh = [r for r in report["benchmark_results"]
          if r["family"] == "buy_and_hold_benchmark"]
    assert any(r["asset"] == "BTC" for r in bh)


def test_donchian_runs_on_sufficient_history(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    donchians = [r for r in report["strategy_results"]
                 if r["family"] == "donchian_channel_breakout" and r["asset"] == "BTC"]
    assert donchians
    assert donchians[0]["status"] == "RAN"


def test_ma_filter_skips_on_insufficient_history(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=100)  # < 201
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    mas = [r for r in report["strategy_results"]
           if r["family"] == "moving_average_trend_filter" and r["asset"] == "BTC"]
    assert mas and mas[0]["status"] == "SKIPPED_INSUFFICIENT_HISTORY"
    assert "insufficient history" in mas[0]["skip_reason"]


def test_momentum_skips_on_insufficient_history(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=50)  # < 91
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    moms = [r for r in report["strategy_results"]
            if r["family"] == "momentum_continuation" and r["asset"] == "BTC"]
    assert moms and moms[0]["status"] == "SKIPPED_INSUFFICIENT_HISTORY"


def test_mean_reversion_is_watch_only(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    mrs = [r for r in report["strategy_results"]
           if r["family"] == "mean_reversion"]
    assert mrs
    for r in mrs:
        assert r["status"] == "SKIPPED_WATCH_ONLY"
        assert "WATCH-only" in r["skip_reason"]


# ===========================================================================
# Cost model
# ===========================================================================
def test_cost_model_applies_on_trades(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    # Sufficient history + small fees so any Donchian crossing produces a cost.
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out,
                              fee_bps=20.0, slip_bps=10.0)
    donchians = [r for r in report["strategy_results"]
                 if r["family"] == "donchian_channel_breakout" and r["asset"] == "BTC"]
    r = donchians[0]
    if r["status"] == "RAN" and r["metrics"]["trade_count"] > 0:
        assert r["metrics"]["total_cost_paid"] > 0, r["metrics"]


def test_run_with_explicit_cost_overrides(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, fee_bps=0.0, slip_bps=0.0)
    assert r["cost_model"]["fee_bps"] == 0.0
    assert r["cost_model"]["slippage_bps"] == 0.0


def test_run_rejects_out_of_bound_fee(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    with pytest.raises(ValueError):
        cbr.run_backtest(data_dir=data_dir, out_dir=out, fee_bps=9999.0)


def test_run_rejects_out_of_bound_slippage(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    with pytest.raises(ValueError):
        cbr.run_backtest(data_dir=data_dir, out_dir=out, slip_bps=9999.0)


# ===========================================================================
# IS / OOS, metrics, verdicts
# ===========================================================================
def test_is_oos_fields_present_on_ran_strategies(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    ran = [r for r in report["strategy_results"] if r["status"] == "RAN"]
    assert ran
    for r in ran:
        assert "is_metrics" in r
        assert "oos_metrics" in r
    iso = report["IS_OOS_summary"]
    assert iso["is_fraction"] == cbr.DEFAULT_IS_FRACTION
    assert "BTC" in iso["per_asset_is_range"]
    assert "BTC" in iso["per_asset_oos_range"]


def test_safety_flags_pinned_false_in_report(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    assert report["research_only"] is True
    for flag in ("data_fetch_enabled", "exchange_connection_enabled",
                 "live_trading_enabled", "broker_control_enabled",
                 "paper_order_execution_enabled", "order_placement_enabled"):
        assert report[flag] is False


def test_pass_watch_fail_status_is_set(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    report = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    assert report["pass_watch_fail_status"] in ("FAIL", "WATCH")
    # PASS is reserved for explicit operator decision in v1.
    assert report["pass_watch_fail_status"] != "PASS"


def test_report_md_says_research_only(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    cbr.run_backtest(data_dir=data_dir, out_dir=out)
    md = (out / "crypto_d1_backtest_report.md").read_text(encoding="utf-8")
    assert "Research-only" in md
    assert "No data fetched" in md
    assert "No order placed" in md
    assert "research_only: True" in md


def test_report_files_land_at_out_dir(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out_nested" / "sub"
    cbr.run_backtest(data_dir=data_dir, out_dir=out)
    assert (out / "crypto_d1_backtest_report.json").exists()
    assert (out / "crypto_d1_backtest_report.md").exists()


# ===========================================================================
# Determinism
# ===========================================================================
def test_deterministic_run_on_same_input(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out1 = tmp_path / "out1"
    out2 = tmp_path / "out2"
    r1 = cbr.run_backtest(data_dir=data_dir, out_dir=out1)
    r2 = cbr.run_backtest(data_dir=data_dir, out_dir=out2)
    # Redact wall-clock fields.
    for r in (r1, r2):
        r.pop("generated_at", None)
    assert r1 == r2, "runs on the same input must be deterministic (modulo generated_at)"
    # run_id is content-derived, so it must match too.
    j1 = _read_json(out1 / "crypto_d1_backtest_report.json")
    j2 = _read_json(out2 / "crypto_d1_backtest_report.json")
    assert j1["run_id"] == j2["run_id"]


# ===========================================================================
# Latent-bug fix: --is-fraction must affect per-strategy IS/OOS metrics,
# not just the display summary (previously _run_one_family hardcoded 0.70).
# ===========================================================================
def test_is_fraction_now_affects_per_strategy_metrics(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out5 = tmp_path / "out5"
    out7 = tmp_path / "out7"
    r5 = cbr.run_backtest(data_dir=data_dir, out_dir=out5, is_fraction=0.5)
    r7 = cbr.run_backtest(data_dir=data_dir, out_dir=out7, is_fraction=0.7)

    def _is_nbars(report):
        ran = [r for r in report["strategy_results"]
               if r["status"] == "RAN" and r["is_metrics"]]
        assert ran, "expected at least one RAN strategy with is_metrics"
        return ran[0]["is_metrics"]["n_bars"]

    n5, n7 = _is_nbars(r5), _is_nbars(r7)
    # 0.5 split -> ~150 IS bars; 0.7 split -> ~210 IS bars. They MUST differ now.
    assert n5 != n7, (n5, n7)
    assert n5 == 150 and n7 == 210, (n5, n7)
    # Summary stays consistent with the per-strategy split.
    assert r5["IS_OOS_summary"]["per_asset_is_range"]["BTC"]["n_bars"] == 150
    assert r7["IS_OOS_summary"]["per_asset_is_range"]["BTC"]["n_bars"] == 210


# ===========================================================================
# Spread-proxy cost model (additive; 0.0 default preserves v1 behavior)
# ===========================================================================
def test_default_cost_model_has_no_spread_key(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out)
    # Default mode: cost_model is byte-compatible with v1 (no spread/round-trip).
    assert "spread_proxy_bps" not in r["cost_model"]
    assert "config_mode" not in r
    assert "strategies_deferred" not in r


def test_simulate_equity_spread_increases_cost():
    # 3-bar up move with one position change -> spread must add cost.
    mk = lambda ts, c: cbr.Bar(timestamp=ts, open=c, high=c * 1.01, low=c * 0.99,
                               close=c, volume=1.0, symbol="BTC",
                               source="t", quote_currency="USDT")
    series = [mk("2023-01-01", 100.0), mk("2023-01-02", 110.0), mk("2023-01-03", 121.0)]
    positions = [0, 1, 1]
    no_spread = cbr._simulate_equity(positions, series, 40.0, 10.0, 100_000.0, 0.0)
    with_spread = cbr._simulate_equity(positions, series, 40.0, 10.0, 100_000.0, 10.0)
    assert with_spread["total_cost_paid"] > no_spread["total_cost_paid"]


def test_validate_config_rejects_high_spread():
    ok, errs = cbr.validate_config(fee_bps=40.0, slip_bps=10.0, spread_bps=999.0)
    assert not ok
    assert any("spread_proxy_bps" in e for e in errs)


def test_validate_config_accepts_v002_costs():
    ok, errs = cbr.validate_config(fee_bps=40.0, slip_bps=10.0, spread_bps=10.0)
    assert ok, errs


# ===========================================================================
# SMA 50/200 crossover strategy (B1) -- distinct from MA200 filter
# ===========================================================================
def test_sma_crossover_skips_on_insufficient_history():
    mk = lambda i: cbr.Bar(timestamp=f"2023-{1 + i // 28:02d}-{1 + i % 28:02d}",
                           open=100.0, high=101.0, low=99.0, close=100.0,
                           volume=1.0, symbol="BTC", source="t",
                           quote_currency="USDT")
    bars = [mk(i) for i in range(50)]  # < slow_window + 1 = 201
    pos, skip = cbr.sma_crossover(bars)
    assert pos == [] and "insufficient history" in skip


def test_sma_crossover_goes_long_on_uptrend():
    # Strictly rising closes -> fast SMA > slow SMA once warmed up -> long.
    bars = []
    base = datetime.strptime("2021-01-01", "%Y-%m-%d")
    for i in range(260):
        c = 100.0 + i  # monotone rising
        d = (base + timedelta(days=i)).strftime("%Y-%m-%d")
        bars.append(cbr.Bar(timestamp=d, open=c, high=c + 1, low=c - 1, close=c,
                            volume=1.0, symbol="BTC", source="t", quote_currency="USDT"))
    pos, skip = cbr.sma_crossover(bars)
    assert skip is None
    # After warmup (>=200) on a monotone uptrend, the strategy is long.
    assert pos[-1] == 1
    # During warmup it is flat.
    assert pos[100] == 0


# ===========================================================================
# Date-window IS/OOS split + missing-day detection
# ===========================================================================
def test_split_is_oos_dates_no_overlap():
    base = datetime.strptime("2021-06-17", "%Y-%m-%d")
    bars = []
    for i in range(400):
        d = (base + timedelta(days=i)).strftime("%Y-%m-%d")
        bars.append(cbr.Bar(timestamp=d, open=1, high=1, low=1, close=1, volume=1,
                            symbol="BTC", source="t", quote_currency="USDT"))
    is_b, oos_b = cbr.split_is_oos_dates(bars, "2021-06-17", "2021-12-31",
                                         "2022-01-01", "2022-07-21")
    is_dates = {b.timestamp for b in is_b}
    oos_dates = {b.timestamp for b in oos_b}
    assert is_dates and oos_dates
    assert is_dates.isdisjoint(oos_dates)
    assert max(is_dates) < min(oos_dates)


def test_detect_missing_days_finds_planted_gap():
    base = datetime.strptime("2024-03-29", "%Y-%m-%d")
    days = ["2024-03-29", "2024-03-30", "2024-04-01", "2024-04-02"]  # 2024-03-31 absent
    bars = [cbr.Bar(timestamp=d, open=1, high=1, low=1, close=1, volume=1,
                    symbol="BTC", source="t", quote_currency="USDT") for d in days]
    missing = cbr._detect_missing_days(bars)
    assert missing == ["2024-03-31"]


# ===========================================================================
# v002_addendum mode -- end-to-end behavior
# ===========================================================================
def _write_v002_dataset(data_dir: Path, write_fees: bool = True):
    """Synthetic V002-shaped dataset spanning a custom IS/OOS range with a
    planted BTC gap. NOT REAL DATA."""
    data_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(data_dir / "btc.csv", "BTC", n_days=900, start_date="2021-06-17",
               start_price=100.0)
    _write_csv(data_dir / "eth.csv", "ETH", n_days=900, start_date="2021-06-17",
               start_price=50.0)
    _write_csv(data_dir / "sol.csv", "SOL", n_days=900, start_date="2021-06-17",
               start_price=10.0)
    if write_fees:
        (data_dir / "fees.json").write_text(json.dumps({
            "venue": "Kraken Pro spot", "taker_fee_bps": 40,
            "slippage_bps": 10, "spread_proxy_bps": 10,
        }), encoding="utf-8")


_V002_KW = dict(config="v002_addendum",
                is_start="2021-06-17", is_end="2022-12-31",
                oos_start="2023-01-01", oos_end="2023-12-03")


def test_v002_runs_only_first_batch(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_V002_KW)
    fams = {x["family"] for x in r["strategy_results"]}
    assert fams == {"sma_50_200_trend_filter", "momentum_30", "momentum_90",
                    "donchian_55_20"}
    # Deferred families MUST NOT appear.
    assert "volatility_regime_gate" not in fams
    assert "mean_reversion" not in fams
    assert r["strategies_deferred"] == ["volatility_regime_gate", "mean_reversion"]
    # B0 benchmark present per asset.
    bench_fams = {x["family"] for x in r["benchmark_results"]}
    assert "buy_and_hold_benchmark" in bench_fams


def test_v002_cost_model_from_fees_json(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir, write_fees=True)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_V002_KW)
    cm = r["cost_model"]
    assert cm["fee_bps"] == 40.0
    assert cm["slippage_bps"] == 10.0
    assert cm["spread_proxy_bps"] == 10.0
    assert cm["total_per_side_bps"] == 60.0
    assert cm["round_trip_bps"] == 120.0
    assert cm["cost_source"] == "v002_fees_json"


def test_v002_cost_model_fallback_when_no_fees_json(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir, write_fees=False)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_V002_KW)
    cm = r["cost_model"]
    assert (cm["fee_bps"], cm["slippage_bps"], cm["spread_proxy_bps"]) == (40.0, 10.0, 10.0)
    assert cm["cost_source"] == "v002_fallback_pins"


def test_v002_uses_date_windows(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_V002_KW)
    iso = r["IS_OOS_summary"]
    assert iso["split_method"] == "explicit_utc_date_windows"
    assert iso["is_window"] == {"start": "2021-06-17", "end": "2022-12-31"}
    assert iso["oos_window"] == {"start": "2023-01-01", "end": "2023-12-03"}
    # Per-asset ranges fall strictly inside their windows.
    rng_is = iso["per_asset_is_range"]["BTC"]
    rng_oos = iso["per_asset_oos_range"]["BTC"]
    assert rng_is["start"] >= "2021-06-17" and rng_is["end"] <= "2022-12-31"
    assert rng_oos["start"] >= "2023-01-01" and rng_oos["end"] <= "2023-12-03"
    assert rng_is["end"] < rng_oos["start"]


def test_v002_default_windows_apply_without_override(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, config="v002_addendum")
    iso = r["IS_OOS_summary"]
    assert iso["is_window"] == {"start": cbr.V002_IS_START, "end": cbr.V002_IS_END}
    assert iso["oos_window"] == {"start": cbr.V002_OOS_START, "end": cbr.V002_OOS_END}


def test_v002_reports_missing_days(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    # Plant a BTC gap by writing two files that skip a day; ETH/SOL complete.
    _write_csv(data_dir / "btc_a.csv", "BTC", n_days=300, start_date="2021-06-17")
    # Resume BTC AFTER a one-day gap: 300 days from 2021-06-17 ends 2022-04-12;
    # restart one day later than contiguous to create a true gap.
    _write_csv(data_dir / "btc_b.csv", "BTC", n_days=300, start_date="2022-04-14")
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, config="v002_addendum",
                         is_start="2021-06-17", is_end="2022-04-13",
                         oos_start="2022-04-14", oos_end="2023-02-07")
    md = r.get("missing_days_per_symbol", {})
    assert "BTC" in md and md["BTC"]["count"] >= 1


def test_v002_safety_flags_pinned(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_V002_KW)
    assert r["research_only"] is True
    for flag in ("data_fetch_enabled", "exchange_connection_enabled",
                 "live_trading_enabled", "broker_control_enabled",
                 "paper_order_execution_enabled", "order_placement_enabled"):
        assert r[flag] is False
    assert r["pass_watch_fail_status"] != "PASS"


def test_v002_default_run_id_unchanged_when_default(tmp_path):
    # Adding spread/config args to the hash must NOT change the default run_id.
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _write_csv(data_dir / "btc.csv", "BTC", n_days=300)
    files = sorted(data_dir.glob("*.csv"))
    legacy = cbr._hash_inputs(data_dir, files, cbr.DEFAULT_TAKER_FEE_BPS,
                              cbr.DEFAULT_SLIPPAGE_BPS, cbr.DEFAULT_START_EQUITY,
                              cbr.DEFAULT_IS_FRACTION)
    with_defaults = cbr._hash_inputs(data_dir, files, cbr.DEFAULT_TAKER_FEE_BPS,
                                     cbr.DEFAULT_SLIPPAGE_BPS, cbr.DEFAULT_START_EQUITY,
                                     cbr.DEFAULT_IS_FRACTION, 0.0, None)
    assert legacy == with_defaults


def test_cli_run_v002_addendum(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    rc = cbr.main(["run", "--data-dir", str(data_dir), "--out-dir", str(out),
                   "--config", "v002_addendum",
                   "--is-start", "2021-06-17", "--is-end", "2022-12-31",
                   "--oos-start", "2023-01-01", "--oos-end", "2023-12-03"])
    assert rc in (0, 2)  # WATCH/PASS->0, FAIL->2; both are valid completions
    j = _read_json(out / "crypto_d1_backtest_report.json")
    assert j["config_mode"] == "v002_addendum"
    assert j["cost_model"]["round_trip_bps"] == 120.0


def test_cli_validate_config_v002_costs_ok():
    assert cbr.main(["validate-config", "--fee-bps", "40",
                     "--slippage-bps", "10"]) == 0


def test_show_plan_includes_v002_mode():
    plan = cbr.show_plan()
    assert "v002_addendum_mode" in plan
    v = plan["v002_addendum_mode"]
    assert v["config_name"] == "v002_addendum"
    ids = {f["id"] for f in v["first_batch"]}
    assert ids == {"buy_and_hold_benchmark", "sma_50_200_trend_filter",
                   "momentum_30", "momentum_90", "donchian_55_20"}
    assert v["deferred"] == ["volatility_regime_gate", "mean_reversion"]


# ===========================================================================
# momentum_robustness_v1 mode -- additive sweep over the SAME V002 dataset.
# ===========================================================================
_ROBUST_KW = dict(config="momentum_robustness_v1",
                  is_start="2021-06-17", is_end="2022-12-31",
                  oos_start="2023-01-01", oos_end="2023-12-03")
_ROBUST_REPORT = "crypto_d1_momentum_robustness_report"


def test_robustness_config_exists():
    # The mode is registered as a constant, a show-plan block, and a CLI choice.
    assert cbr.MOMENTUM_ROBUSTNESS_CONFIG_NAME == "momentum_robustness_v1"
    assert tuple(cbr.MOMENTUM_ROBUSTNESS_LOOKBACKS) == (20, 30, 45, 60, 90)
    plan = cbr.show_plan()
    assert "momentum_robustness_v1_mode" in plan
    m = plan["momentum_robustness_v1_mode"]
    assert m["config_name"] == "momentum_robustness_v1"
    assert m["momentum_lookbacks"] == [20, 30, 45, 60, 90]
    assert m["mutates_v002_addendum"] is False
    assert m["promotes_anything"] is False
    assert m["output_basename"] == _ROBUST_REPORT


def test_robustness_runs_all_five_lookbacks(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_ROBUST_KW)
    fams = {x["family"] for x in r["strategy_results"]}
    assert fams == {"momentum_20", "momentum_30", "momentum_45",
                    "momentum_60", "momentum_90"}
    # Deferred families MUST NOT appear.
    assert "volatility_regime_gate" not in fams
    assert "mean_reversion" not in fams
    assert r["strategies_deferred"] == ["volatility_regime_gate", "mean_reversion"]
    assert r["momentum_robustness_lookbacks"] == [20, 30, 45, 60, 90]
    assert r["config_mode"] == "momentum_robustness_v1"
    # The report lands at the DISTINCT robustness basename, never overwriting
    # the committed v002/default baseline report.
    assert (out / f"{_ROBUST_REPORT}.json").exists()
    assert (out / f"{_ROBUST_REPORT}.md").exists()
    assert not (out / "crypto_d1_backtest_report.json").exists()


def test_robustness_does_not_mutate_v002_addendum(tmp_path):
    # v002_addendum still runs its own B0-B3 batch and daily-rebalanced basket,
    # untouched by the new mode.
    bench, strat, deferred = cbr._v002_family_plan()
    strat_ids = {s["family_id"] for s in strat}
    assert strat_ids == {"sma_50_200_trend_filter", "momentum_30",
                         "momentum_90", "donchian_55_20"}
    assert deferred == ["volatility_regime_gate", "mean_reversion"]
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_V002_KW)
    bench_strat_ids = {b["strategy_id"] for b in r["benchmark_results"]}
    # v002 keeps the daily-rebalanced basket; NOT the allocate-once one.
    assert "buy_and_hold_basket" in bench_strat_ids
    assert "buy_and_hold_basket_equal_weight" not in bench_strat_ids
    assert r["batch_label"] == "B0-B3 first execution batch (v002_addendum)"
    assert (out / "crypto_d1_backtest_report.json").exists()


def test_robustness_is_oos_dates_match_v002(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    # No override -> defaults must equal the V002 addendum pins.
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out,
                         config="momentum_robustness_v1")
    iso = r["IS_OOS_summary"]
    assert iso["split_method"] == "explicit_utc_date_windows"
    assert iso["is_window"] == {"start": cbr.V002_IS_START, "end": cbr.V002_IS_END}
    assert iso["oos_window"] == {"start": cbr.V002_OOS_START, "end": cbr.V002_OOS_END}


def test_robustness_costs_match_v002(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir, write_fees=True)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_ROBUST_KW)
    cm = r["cost_model"]
    assert (cm["fee_bps"], cm["slippage_bps"], cm["spread_proxy_bps"]) == (40.0, 10.0, 10.0)
    assert cm["total_per_side_bps"] == 60.0
    assert cm["round_trip_bps"] == 120.0
    assert cm["cost_source"] == "v002_fees_json"


def test_robustness_reports_btc_gap_not_filled(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    # Plant a true BTC one-day gap; never forward-filled or synthesized.
    _write_csv(data_dir / "btc_a.csv", "BTC", n_days=300, start_date="2021-06-17")
    _write_csv(data_dir / "btc_b.csv", "BTC", n_days=300, start_date="2022-04-14")
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out,
                         config="momentum_robustness_v1",
                         is_start="2021-06-17", is_end="2022-04-13",
                         oos_start="2022-04-14", oos_end="2023-02-07")
    md = r.get("missing_days_per_symbol", {})
    assert "BTC" in md and md["BTC"]["count"] >= 1


def test_robustness_primary_basket_is_allocate_once_not_daily(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_ROBUST_KW)
    bench_ids = {b["strategy_id"] for b in r["benchmark_results"]}
    # The daily-rebalanced basket (volatility-drag artifact) must NOT be the
    # primary basket benchmark for this mode.
    assert "buy_and_hold_basket" not in bench_ids
    assert "buy_and_hold_basket_equal_weight" in bench_ids
    assert r["primary_basket_benchmark"] == "buy_and_hold_basket_equal_weight"
    # The allocate-once basket trades exactly once and never rebalances.
    ew = next(b for b in r["benchmark_results"]
              if b["strategy_id"] == "buy_and_hold_basket_equal_weight")
    assert ew["metrics"]["trade_count"] == 1
    assert ew["metrics"]["turnover"] == 1
    assert "allocate once" in ew["parameters"]["rebalance_frequency"]


def test_robustness_reports_family_oos_trade_counts(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_ROBUST_KW)
    fc = r["family_oos_trade_counts"]
    assert set(fc.keys()) == {"momentum_20", "momentum_30", "momentum_45",
                              "momentum_60", "momentum_90"}
    for fam, d in fc.items():
        assert "oos_trades_total" in d and "per_asset" in d
        assert "meets_family_floor" in d
    # The per-family floor is REPORTED but NOT enforced in classify_run.
    ft = r["family_trade_floor"]
    assert ft["per_family_floor"] == cbr.OOS_MIN_TRADES_PER_FAMILY
    assert ft["enforced_in_classify_run"] is False


def test_robustness_safety_flags_pinned(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_ROBUST_KW)
    assert r["research_only"] is True
    for flag in ("data_fetch_enabled", "exchange_connection_enabled",
                 "live_trading_enabled", "broker_control_enabled",
                 "paper_order_execution_enabled", "order_placement_enabled"):
        assert r[flag] is False
    # The conservative classifier never auto-promotes (WATCH ceiling).
    assert r["pass_watch_fail_status"] != "PASS"


def test_robustness_mode_adds_no_network_or_execution_paths():
    # The whole tool is stdlib-only (asserted elsewhere); pin that the new mode
    # introduced no broker/paper/live/network tokens around its own code.
    src = TOOL_FILE.read_text(encoding="utf-8").lower()
    # locate the robustness family-plan + basket region and scan it.
    start = src.index("_momentum_robustness_family_plan")
    region = src[start:start + 4000]
    for forbidden in ("requests", "urllib", "socket", "http", "fetch(",
                      "place_order", "submit_order", "execute_trade",
                      "broker", "api_key", "secret", "websocket", "subprocess"):
        assert forbidden not in region, \
            f"robustness mode must not reference {forbidden}"


def test_cli_run_momentum_robustness_v1(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    rc = cbr.main(["run", "--data-dir", str(data_dir), "--out-dir", str(out),
                   "--config", "momentum_robustness_v1",
                   "--is-start", "2021-06-17", "--is-end", "2022-12-31",
                   "--oos-start", "2023-01-01", "--oos-end", "2023-12-03"])
    assert rc in (0, 2)
    j = _read_json(out / f"{_ROBUST_REPORT}.json")
    assert j["config_mode"] == "momentum_robustness_v1"
    assert j["momentum_robustness_lookbacks"] == [20, 30, 45, 60, 90]


# ===========================================================================
# momentum_confirmation_v1 mode -- focused N=20/N=30 confirmation + basket OOS fix.
# ===========================================================================
_CONFIRM_KW = dict(config="momentum_confirmation_v1",
                   is_start="2021-06-17", is_end="2022-12-31",
                   oos_start="2023-01-01", oos_end="2023-12-03")
_CONFIRM_REPORT = "crypto_d1_momentum_confirmation_report"


def test_confirmation_config_exists():
    # Registered as a constant, a show-plan block, and a CLI choice.
    assert cbr.MOMENTUM_CONFIRMATION_CONFIG_NAME == "momentum_confirmation_v1"
    assert tuple(cbr.MOMENTUM_CONFIRMATION_LOOKBACKS) == (20, 30)
    plan = cbr.show_plan()
    assert "momentum_confirmation_v1_mode" in plan
    m = plan["momentum_confirmation_v1_mode"]
    assert m["config_name"] == "momentum_confirmation_v1"
    assert m["momentum_lookbacks"] == [20, 30]
    assert m["lookbacks_dropped_as_thin_sample"] == [45, 60, 90]
    assert m["mutates_v002_addendum"] is False
    assert m["mutates_momentum_robustness_v1"] is False
    assert m["promotes_anything"] is False
    assert m["output_basename"] == _CONFIRM_REPORT


def test_confirmation_accepts_only_n20_and_n30(tmp_path):
    # CATEGORY 1 + 2: N=20 and N=30 are accepted; every other lookback (the
    # thin-sample 45/60/90 dropped pre-registration) is EXCLUDED -- no new search.
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_CONFIRM_KW)
    fams = {x["family"] for x in r["strategy_results"]}
    assert fams == {"momentum_20", "momentum_30"}
    for excluded in ("momentum_45", "momentum_60", "momentum_90"):
        assert excluded not in fams
    # Deferred families still excluded.
    assert "volatility_regime_gate" not in fams
    assert "mean_reversion" not in fams
    assert r["momentum_confirmation_lookbacks"] == [20, 30]
    assert r["config_mode"] == "momentum_confirmation_v1"
    # Distinct basename; never overwrites baseline or robustness reports.
    assert (out / f"{_CONFIRM_REPORT}.json").exists()
    assert (out / f"{_CONFIRM_REPORT}.md").exists()
    assert not (out / "crypto_d1_backtest_report.json").exists()
    assert not (out / "crypto_d1_momentum_robustness_report.json").exists()


def test_confirmation_is_additive_does_not_alter_existing_modes(tmp_path):
    # CATEGORY 3: confirmation mode leaves default, v002, and robustness modes
    # byte-for-byte unchanged in behavior.
    # 3a. The family-plan helpers are independent.
    cb, cs, cd = cbr._momentum_confirmation_family_plan()
    confirm_ids = {s["family_id"] for s in cs}
    assert confirm_ids == {"momentum_20", "momentum_30"}
    assert cd == ["volatility_regime_gate", "mean_reversion"]
    rb, rs, rd = cbr._momentum_robustness_family_plan()
    robust_ids = {s["family_id"] for s in rs}
    assert robust_ids == {"momentum_20", "momentum_30", "momentum_45",
                          "momentum_60", "momentum_90"}
    # 3b. v002 still keeps its own batch + daily-rebalanced basket.
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    rv = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_V002_KW)
    v_ids = {b["strategy_id"] for b in rv["benchmark_results"]}
    assert "buy_and_hold_basket" in v_ids
    assert "buy_and_hold_basket_equal_weight" not in v_ids
    assert rv["batch_label"] == "B0-B3 first execution batch (v002_addendum)"
    # 3c. robustness mode (no OOS window passed to basket) still reports None OOS.
    out2 = tmp_path / "out2"
    rr = cbr.run_backtest(data_dir=data_dir, out_dir=out2, **_ROBUST_KW)
    ew_r = next(b for b in rr["benchmark_results"]
                if b["strategy_id"] == "buy_and_hold_basket_equal_weight")
    assert ew_r["oos_metrics"] is None
    assert ew_r["basket_oos_reporting"] == "single_stream_no_split"


def test_confirmation_basket_oos_reporting_is_fixed_and_labeled(tmp_path):
    # CATEGORY 4: the allocate-once basket now reports a benchmark-only OOS
    # figure (Option A), explicitly labeled, instead of OOS_ret=None. The
    # construction is unchanged (still one entry, no rebalance).
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_CONFIRM_KW)
    ew = next(b for b in r["benchmark_results"]
              if b["strategy_id"] == "buy_and_hold_basket_equal_weight")
    # Construction KEPT: allocate once, no rebalance.
    assert ew["metrics"]["trade_count"] == 1
    assert ew["metrics"]["turnover"] == 1
    assert "allocate once" in ew["parameters"]["rebalance_frequency"]
    # OOS reporting fixed and explicitly labeled (never silently None).
    assert ew["oos_metrics"] is not None
    assert ew["basket_oos_reporting"] == "allocate_once_oos_window_split"
    oos = ew["oos_metrics"]
    assert oos["oos_window"] == {"start": "2023-01-01", "end": "2023-12-03"}
    assert "total_return" in oos and "max_drawdown" in oos
    assert oos["n_bars"] >= 2
    # The report-level field mirrors the basket label.
    assert r["basket_oos_reporting"] == "allocate_once_oos_window_split"
    # IS/OOS not silently mixed: the all-history metrics differ from the OOS view
    # (different windows), and IS metrics remain None for this single stream.
    assert ew["is_metrics"] is None


def test_confirmation_safety_flags_pinned(tmp_path):
    # CATEGORY 5: no execution authorization, no paper/live, WATCH ceiling.
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    r = cbr.run_backtest(data_dir=data_dir, out_dir=out, **_CONFIRM_KW)
    assert r["research_only"] is True
    for flag in ("data_fetch_enabled", "exchange_connection_enabled",
                 "live_trading_enabled", "broker_control_enabled",
                 "paper_order_execution_enabled", "order_placement_enabled"):
        assert r[flag] is False
    assert r["pass_watch_fail_status"] != "PASS"


def test_confirmation_mode_adds_no_network_or_execution_paths():
    src = TOOL_FILE.read_text(encoding="utf-8").lower()
    start = src.index("_momentum_confirmation_family_plan")
    region = src[start:start + 4000]
    for forbidden in ("requests", "urllib", "socket", "http", "fetch(",
                      "place_order", "submit_order", "execute_trade",
                      "broker", "api_key", "secret", "websocket", "subprocess"):
        assert forbidden not in region, \
            f"confirmation mode must not reference {forbidden}"


def test_cli_run_momentum_confirmation_v1(tmp_path):
    data_dir = tmp_path / "data"
    _write_v002_dataset(data_dir)
    out = tmp_path / "out"
    rc = cbr.main(["run", "--data-dir", str(data_dir), "--out-dir", str(out),
                   "--config", "momentum_confirmation_v1",
                   "--is-start", "2021-06-17", "--is-end", "2022-12-31",
                   "--oos-start", "2023-01-01", "--oos-end", "2023-12-03"])
    assert rc in (0, 2)
    j = _read_json(out / f"{_CONFIRM_REPORT}.json")
    assert j["config_mode"] == "momentum_confirmation_v1"
    assert j["momentum_confirmation_lookbacks"] == [20, 30]
    assert j["basket_oos_reporting"] == "allocate_once_oos_window_split"


# ===========================================================================
# Repo invariants (no real data files were committed by this bundle).
# ===========================================================================
def test_no_real_data_files_committed_under_bundle_dir():
    bundle_dir = _REPO_ROOT / "reports" / "crypto_d1_backtest_runner_v1"
    if not bundle_dir.exists():
        # Bundle reports may not yet exist while these tests run during build;
        # the test asserts that IF the dir exists, it contains only build-report
        # files (no real OHLCV data).
        return
    forbidden_exts = (".csv", ".parquet", ".pq", ".pickle", ".feather", ".h5",
                      ".npz", ".pkl")
    for p in bundle_dir.iterdir():
        if not p.is_file():
            continue
        for ext in forbidden_exts:
            assert not p.name.lower().endswith(ext), \
                f"unexpected real-data file committed under bundle dir: {p.name}"


def test_no_real_data_files_committed_under_data_crypto_d1_research():
    p = _REPO_ROOT / "data" / "crypto_d1_research"
    if not p.exists():
        return
    forbidden_exts = (".csv", ".parquet", ".pq", ".pickle", ".feather", ".h5",
                      ".npz", ".pkl")
    found = []
    for f in p.rglob("*"):
        if not f.is_file():
            continue
        for ext in forbidden_exts:
            if f.name.lower().endswith(ext):
                found.append(f.as_posix())
    assert not found, ("real data files exist under data/crypto_d1_research/ -- "
                       "this bundle authored a runner, not a dataset; if these "
                       "files exist they were created by a separate operator "
                       "action and should NOT be committed by this bundle: " + str(found))

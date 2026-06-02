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

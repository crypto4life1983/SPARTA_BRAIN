"""Tests for the Crypto-D1 Baseline Backtest Runner (READ-ONLY single approved run).
All inputs are FAKE local CSVs under tmp_path; no network, no credentials, no real
data, no broker/exchange, no orders. The runner only ever marks positions to the
staged closes."""

from __future__ import annotations

import ast

import sparta_commander.strategy_factory_crypto_d1_baseline_backtest_runner as br
import sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner as qa

_CANON = ",".join(qa.QA_REQUIRED_FIELDS)
_SRC = "binance_usdt_spot_frozen_regime_inputs"


def _row(date: str, close: float) -> str:
    # open=close; high/low bracket close so the QA OHLC checks pass; volume > 0.
    return f"{date},{close},{close + 5},{close - 5},{close},1000,{_SRC},spot"


def _csv(closes: list[float]) -> str:
    dates = [f"2024-01-0{i + 1}" for i in range(len(closes))]
    return "\n".join([_CANON] + [_row(d, c) for d, c in zip(dates, closes)])


def _stage_and_qa(tmp_path, closes_by_symbol: dict[str, list[float]]) -> None:
    raw = tmp_path / "data" / "crypto_d1_spot" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for sym, closes in closes_by_symbol.items():
        (raw / (sym + "_1d.csv")).write_text(_csv(closes), encoding="utf-8")
    rep = qa.run_real_data_qa(repo_root=str(tmp_path), write=True)
    assert rep["verdict"] == qa.VERDICT_PASS


def _stage_uniform(tmp_path) -> None:
    _stage_and_qa(
        tmp_path,
        {"BTC": [100, 110, 120], "ETH": [100, 110, 120], "SOL": [100, 110, 120]},
    )


# --------------------------------------------------------------------------- #
# refusal when prep is not READY
# --------------------------------------------------------------------------- #
def test_refuses_to_run_when_prep_not_ready(tmp_path):
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=True)
    assert r["verdict"] == br.VERDICT_BLOCKED_NOT_READY
    assert r["performance"] is None
    assert r["files_written"] == []
    assert "baseline_prep_not_ready" in r["blockers"]


# --------------------------------------------------------------------------- #
# happy path
# --------------------------------------------------------------------------- #
def test_runs_and_reports_performance(tmp_path):
    _stage_uniform(tmp_path)
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=True)
    assert r["verdict"] == br.VERDICT_BASELINE_COMPLETE
    assert r["blockers"] == []
    perf = r["performance"]
    # every symbol 100 -> 120 => portfolio total return 20%
    assert abs(perf["total_return"] - 0.20) < 1e-9
    assert perf["entry_date"] == "2024-01-01" and perf["exit_date"] == "2024-01-03"
    assert perf["trading_days"] == 3
    assert abs(perf["final_value"] - br.INITIAL_CAPITAL * 1.20) < 1e-6
    # monotonically rising equity => no drawdown
    assert perf["max_drawdown"] == 0.0
    assert len(r["equity_curve"]) == 3


def test_trade_summary_is_long_only_buy_and_hold(tmp_path):
    _stage_uniform(tmp_path)
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=True)
    ts = r["trade_summary"]
    assert ts["trade_count"] == 3 and ts["buys"] == 3
    assert ts["sells"] == 0 and ts["rebalances"] == 0
    assert ts["single_pass"] is True


def test_per_symbol_breakdown(tmp_path):
    _stage_and_qa(
        tmp_path,
        {"BTC": [100, 100, 200], "ETH": [100, 100, 100], "SOL": [100, 100, 50]},
    )
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=True)
    by = {s["symbol"]: s for s in r["per_symbol"]}
    assert abs(by["BTC"]["symbol_return"] - 1.0) < 1e-9   # 100 -> 200
    assert abs(by["ETH"]["symbol_return"] - 0.0) < 1e-9   # flat
    assert abs(by["SOL"]["symbol_return"] + 0.5) < 1e-9   # 100 -> 50
    # equal weight: portfolio = (2.0 + 1.0 + 0.5)/3 of capital => +16.6667%
    assert abs(r["performance"]["total_return"] - (3.5 / 3 - 1.0)) < 1e-9
    assert all(abs(s["allocation_weight"] - 1 / 3) < 1e-9 for s in r["per_symbol"])


def test_drawdown_is_negative_when_price_dips(tmp_path):
    _stage_and_qa(
        tmp_path,
        {"BTC": [100, 50, 80], "ETH": [100, 50, 80], "SOL": [100, 50, 80]},
    )
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=True)
    # peak at entry (100% capital), trough at day2 (50%) => -50% drawdown
    assert abs(r["performance"]["max_drawdown"] + 0.50) < 1e-9
    assert r["performance"]["total_return"] < 0  # ends at 80 < 100


# --------------------------------------------------------------------------- #
# artifacts
# --------------------------------------------------------------------------- #
def test_writes_only_baseline_report_artifacts(tmp_path):
    _stage_uniform(tmp_path)
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=True)
    written = r["files_written"]
    assert len(written) == 2
    assert all(br.BASELINE_REPORT_DIR.replace("/", "") in w.replace("\\", "").replace("/", "")
               for w in written)
    assert any(w.endswith("baseline_backtest_report.json") for w in written)
    assert any(w.endswith("baseline_backtest_report.md") for w in written)


def test_write_false_writes_nothing(tmp_path):
    _stage_uniform(tmp_path)
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=False)
    assert r["verdict"] == br.VERDICT_BASELINE_COMPLETE
    assert r["files_written"] == []


# --------------------------------------------------------------------------- #
# safety posture
# --------------------------------------------------------------------------- #
def test_run_unlocks_no_gate(tmp_path):
    _stage_uniform(tmp_path)
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=True)
    assert r["paper_trading_gate_locked"] is True
    assert r["micro_live_gate_locked"] is True
    assert r["executes_orders"] is False
    assert r["ran_optimization"] is False
    assert r["ran_parameter_search"] is False
    assert r["ran_walk_forward"] is False
    assert r["used_lookahead"] is False
    assert r["touches_broker_or_exchange"] is False
    assert r["unlocks_downstream_gate"] is False
    assert r["no_network_used"] is True and r["no_credentials_used"] is True


def test_validate_passes_on_complete_report(tmp_path):
    _stage_uniform(tmp_path)
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=False)
    v = br.validate_baseline_backtest_report(r)
    assert v["valid"] is True and v["errors"] == []


def test_validate_passes_on_blocked_report(tmp_path):
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=False)
    v = br.validate_baseline_backtest_report(r)
    assert v["valid"] is True and v["errors"] == []


def test_validate_rejects_unlocked_gate(tmp_path):
    _stage_uniform(tmp_path)
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=False)
    r["micro_live_gate_locked"] = False
    v = br.validate_baseline_backtest_report(r)
    assert v["valid"] is False
    assert any("gate_not_locked" in e for e in v["errors"])


def test_render_markdown_is_string(tmp_path):
    _stage_uniform(tmp_path)
    r = br.run_baseline_backtest(repo_root=str(tmp_path), write=False)
    md = br.render_baseline_backtest_markdown(r)
    assert md.startswith("# Crypto-D1 Baseline Backtest")
    assert "LOCKED" in md and "Per-symbol breakdown" in md


def test_module_imports_no_network_or_credential_modules():
    with open(br.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {
        "urllib",
        "requests",
        "socket",
        "http",
        "ftplib",
        "ccxt",
        "databento",
        "dotenv",
        "smtplib",
    }
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)

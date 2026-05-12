from __future__ import annotations

from pathlib import Path

import strategy_lab.backtest_wrapper as backtest_wrapper
from strategy_lab.backtest_wrapper import BacktestConfig, BacktestResult, apply_fee_slippage, run_backtest_stub


def test_fee_slippage_calculation():
    result = apply_fee_slippage(1000.0, fee_bps=10.0, slippage_bps=5.0)
    assert result["gross_value"] == 1000.0
    assert result["fees_paid"] == 1.0
    assert result["slippage_cost"] == 0.5
    assert result["net_value"] == 998.5


def test_backtest_result_serialization_round_trip():
    result = BacktestResult(
        candidate_id="cand_01",
        symbol="BTCUSDT",
        total_return=12.5,
        max_drawdown=4.2,
        win_rate=55.0,
        expectancy=0.31,
        sharpe=1.4,
        trades_count=7,
        fees_paid=2.0,
        slippage_cost=1.0,
        status="EXPERIMENTAL",
        notes="stub",
    )
    payload = result.to_dict()
    clone = BacktestResult.from_dict(payload)
    assert clone.to_dict()["candidate_id"] == "cand_01"
    assert clone.to_dict()["symbol"] == "BTCUSDT"
    assert clone.to_dict()["trades_count"] == 7


def test_backtest_stub_persists_result_inside_backtests_root(monkeypatch):
    backtests_root = Path("strategy_lab/data/backtests")
    monkeypatch.setattr(backtest_wrapper, "DATA_ROOT", Path("strategy_lab/data"))
    monkeypatch.setattr(backtest_wrapper, "BACKTESTS_ROOT", backtests_root)
    before = {path.name for path in backtests_root.glob("cand_02__ETHUSDT__1D__2024-01-01_to_2024-12-31__*.json")} if backtests_root.exists() else set()
    result = run_backtest_stub(
        BacktestConfig(
            candidate_id="cand_02",
            symbol="ETHUSDT",
            timeframe="1D",
            start_date="2024-01-01",
            end_date="2024-12-31",
            fee_bps=12.5,
            slippage_bps=6.5,
            initial_capital=50000.0,
        )
    )
    assert result.candidate_id == "cand_02"
    assert backtests_root.exists()
    matches = [path for path in backtests_root.glob("cand_02__ETHUSDT__1D__2024-01-01_to_2024-12-31__*.json") if path.name not in before]
    assert len(matches) == 1
    assert matches[0].resolve().is_relative_to(backtests_root.resolve())
    for path in matches:
        path.unlink(missing_ok=True)


def test_backtest_wrapper_source_has_no_forbidden_language():
    source = Path(backtest_wrapper.__file__).read_text(encoding="utf-8").lower()
    for forbidden in ("broker", "place_order", "submit_order", "execute_order"):
        assert forbidden not in source

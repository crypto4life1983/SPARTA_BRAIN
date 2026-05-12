from __future__ import annotations

from strategy_lab.scorecard import StrategyScorecard


def test_scorecard_defaults():
    card = StrategyScorecard()
    assert card.candidate_id == ""
    assert card.lifecycle_state == "IDEA"
    assert card.trades_count == 0
    assert card.final_grade == "UNRATED"
    assert card.status == "EXPERIMENTAL"


def test_scorecard_serialization_round_trip():
    card = StrategyScorecard(
        candidate_id="donchian_01",
        name="Donchian",
        lifecycle_state="BACKTESTED",
        backtest_return=12.5,
        max_drawdown=4.2,
        win_rate=55.0,
        expectancy=0.31,
        sharpe=1.4,
        trades_count=42,
        oos_score=68.0,
        regime_score=71.5,
        overfit_risk=0.18,
        final_grade="B",
        rejection_reason=None,
    )
    payload = card.to_dict()
    clone = StrategyScorecard.from_dict(payload)
    assert clone.to_dict()["candidate_id"] == "donchian_01"
    assert clone.to_dict()["lifecycle_state"] == "BACKTESTED"
    assert clone.to_dict()["trades_count"] == 42
    assert clone.to_dict()["final_grade"] == "B"


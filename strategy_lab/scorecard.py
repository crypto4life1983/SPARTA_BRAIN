from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class StrategyScorecard:
    candidate_id: str = ""
    name: str = ""
    lifecycle_state: str = "IDEA"
    backtest_return: float | None = None
    max_drawdown: float | None = None
    win_rate: float | None = None
    expectancy: float | None = None
    sharpe: float | None = None
    trades_count: int = 0
    oos_score: float | None = None
    regime_score: float | None = None
    overfit_risk: float | None = None
    final_grade: str = "UNRATED"
    rejection_reason: str | None = None
    generated_at: str = field(default_factory=_utc_now)
    status: str = "EXPERIMENTAL"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "StrategyScorecard":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            name=str(data.get("name") or ""),
            lifecycle_state=str(data.get("lifecycle_state") or "IDEA"),
            backtest_return=data.get("backtest_return"),
            max_drawdown=data.get("max_drawdown"),
            win_rate=data.get("win_rate"),
            expectancy=data.get("expectancy"),
            sharpe=data.get("sharpe"),
            trades_count=int(data.get("trades_count") or 0),
            oos_score=data.get("oos_score"),
            regime_score=data.get("regime_score"),
            overfit_risk=data.get("overfit_risk"),
            final_grade=str(data.get("final_grade") or "UNRATED"),
            rejection_reason=data.get("rejection_reason"),
            generated_at=str(data.get("generated_at") or _utc_now()),
            status=str(data.get("status") or "EXPERIMENTAL"),
        )


def build_scorecard(metrics: dict[str, Any] | None = None, *, strategy_id: str = "", run_id: str = "") -> dict[str, Any]:
    data = dict(metrics or {})
    return {
        "strategy_id": strategy_id,
        "run_id": run_id,
        "status": "EXPERIMENTAL",
        "return_pct": data.get("return_pct"),
        "cagr_pct": data.get("cagr_pct"),
        "profit_factor": data.get("profit_factor"),
        "expectancy": data.get("expectancy"),
        "max_drawdown_pct": data.get("max_drawdown_pct"),
        "win_rate_pct": data.get("win_rate_pct"),
        "average_r": data.get("average_r"),
        "trade_count": int(data.get("trade_count") or 0),
        "sharpe_like_score": data.get("sharpe_like_score"),
        "robustness_score": data.get("robustness_score"),
        "regime_fit_score": data.get("regime_fit_score"),
        "symbol_diversity_score": data.get("symbol_diversity_score"),
        "data_quality_score": data.get("data_quality_score"),
        "confidence_score": data.get("confidence_score"),
        "walk_forward_score": data.get("walk_forward_score"),
        "out_of_sample_score": data.get("out_of_sample_score"),
        "parameter_sensitivity_score": data.get("parameter_sensitivity_score"),
        "generated_at": data.get("generated_at") or _utc_now(),
        "notes": data.get("notes"),
    }


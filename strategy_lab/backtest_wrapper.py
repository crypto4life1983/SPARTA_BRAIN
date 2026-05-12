from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
BACKTESTS_ROOT = DATA_ROOT / "backtests"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned or "candidate"


@dataclass(slots=True)
class BacktestConfig:
    candidate_id: str
    symbol: str
    timeframe: str
    start_date: str
    end_date: str
    fee_bps: float = 0.0
    slippage_bps: float = 0.0
    initial_capital: float = 100000.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "BacktestConfig":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            symbol=str(data.get("symbol") or ""),
            timeframe=str(data.get("timeframe") or ""),
            start_date=str(data.get("start_date") or ""),
            end_date=str(data.get("end_date") or ""),
            fee_bps=float(data.get("fee_bps") or 0.0),
            slippage_bps=float(data.get("slippage_bps") or 0.0),
            initial_capital=float(data.get("initial_capital") or 100000.0),
        )


@dataclass(slots=True)
class BacktestResult:
    candidate_id: str
    symbol: str
    total_return: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    expectancy: float = 0.0
    sharpe: float = 0.0
    trades_count: int = 0
    fees_paid: float = 0.0
    slippage_cost: float = 0.0
    status: str = "EXPERIMENTAL"
    notes: str = ""
    generated_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "BacktestResult":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            symbol=str(data.get("symbol") or ""),
            total_return=float(data.get("total_return") or 0.0),
            max_drawdown=float(data.get("max_drawdown") or 0.0),
            win_rate=float(data.get("win_rate") or 0.0),
            expectancy=float(data.get("expectancy") or 0.0),
            sharpe=float(data.get("sharpe") or 0.0),
            trades_count=int(data.get("trades_count") or 0),
            fees_paid=float(data.get("fees_paid") or 0.0),
            slippage_cost=float(data.get("slippage_cost") or 0.0),
            status=str(data.get("status") or "EXPERIMENTAL"),
            notes=str(data.get("notes") or ""),
            generated_at=str(data.get("generated_at") or _utc_now()),
        )


def apply_fee_slippage(notional_value: float, *, fee_bps: float = 0.0, slippage_bps: float = 0.0) -> dict[str, float]:
    gross = float(notional_value)
    fees_paid = gross * float(fee_bps) / 10_000.0
    slippage_cost = gross * float(slippage_bps) / 10_000.0
    net = gross - fees_paid - slippage_cost
    return {
        "gross_value": gross,
        "fees_paid": fees_paid,
        "slippage_cost": slippage_cost,
        "net_value": net,
    }


def _result_path(config: BacktestConfig) -> Path:
    BACKTESTS_ROOT.mkdir(parents=True, exist_ok=True)
    candidate = assert_approved_path(BACKTESTS_ROOT)
    filename = (
        f"{_slug(config.candidate_id)}__"
        f"{_slug(config.symbol)}__"
        f"{_slug(config.timeframe)}__"
        f"{_slug(config.start_date)}_to_{_slug(config.end_date)}__"
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    return candidate / filename


def run_backtest_stub(config: BacktestConfig | dict[str, Any] | None = None, *, strategy: dict[str, Any] | None = None) -> BacktestResult:
    if isinstance(config, BacktestConfig):
        cfg = config
    else:
        cfg = BacktestConfig.from_dict(config)

    fee_slippage = apply_fee_slippage(cfg.initial_capital, fee_bps=cfg.fee_bps, slippage_bps=cfg.slippage_bps)
    result = BacktestResult(
        candidate_id=cfg.candidate_id,
        symbol=cfg.symbol,
        total_return=0.0,
        max_drawdown=0.0,
        win_rate=0.0,
        expectancy=0.0,
        sharpe=0.0,
        trades_count=0,
        fees_paid=fee_slippage["fees_paid"],
        slippage_cost=fee_slippage["slippage_cost"],
        status="EXPERIMENTAL",
        notes="stub backtest wrapper; no strategy evaluation executed",
    )

    payload = {
        "schema_version": "strategy_lab.backtest_result.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "config": cfg.to_dict(),
        "strategy": dict(strategy or {}),
        "result": result.to_dict(),
    }
    output_path = _result_path(cfg)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return result

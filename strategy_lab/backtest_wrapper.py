from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
BACKTESTS_ROOT = DATA_ROOT / "backtests"

SCHEMA_BACKTEST_V1 = "strategy_lab.backtest.v1"
SCHEMA_BACKTEST_V2 = "strategy_lab.backtest.v2"
REQUIRED_V2_STR_FIELDS = (
    "run_id", "strategy_code_sha256", "exchange", "bar_timeframe",
    "is_sample_start_utc", "is_sample_end_utc",
    "oos_start_utc", "oos_end_utc",
    "oos_bar_returns_path", "oos_bar_returns_sha256",
    "compounding_mode", "fee_model", "slippage_model",
)


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
class WindowMetric:
    """Per (training, testing) walk-forward window result for v2 evidence."""

    train_start_utc: str = ""
    train_end_utc: str = ""
    test_start_utc: str = ""
    test_end_utc: str = ""
    train_bar_count: int = 0
    test_bar_count: int = 0
    train_sharpe: float = 0.0
    test_sharpe: float = 0.0
    train_return: float = 0.0
    test_return: float = 0.0
    train_maxdd: float = 0.0
    test_maxdd: float = 0.0
    trades_count_in_test: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "WindowMetric":
        d = dict(payload or {})
        return cls(
            train_start_utc=str(d.get("train_start_utc") or ""),
            train_end_utc=str(d.get("train_end_utc") or ""),
            test_start_utc=str(d.get("test_start_utc") or ""),
            test_end_utc=str(d.get("test_end_utc") or ""),
            train_bar_count=int(d.get("train_bar_count") or 0),
            test_bar_count=int(d.get("test_bar_count") or 0),
            train_sharpe=float(d.get("train_sharpe") or 0.0),
            test_sharpe=float(d.get("test_sharpe") or 0.0),
            train_return=float(d.get("train_return") or 0.0),
            test_return=float(d.get("test_return") or 0.0),
            train_maxdd=float(d.get("train_maxdd") or 0.0),
            test_maxdd=float(d.get("test_maxdd") or 0.0),
            trades_count_in_test=int(d.get("trades_count_in_test") or 0),
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
    # v2 additive fields. Defaults preserve v1 semantics: a result
    # built v1-style yields schema_version == v1 and is_v2() == False.
    schema_version: str = SCHEMA_BACKTEST_V1
    run_id: str = ""
    strategy_code_sha256: str = ""
    random_seed: int | None = None
    exchange: str = ""
    bar_timeframe: str = ""
    timezone: str = ""
    session: str = ""
    is_sample_start_utc: str = ""
    is_sample_end_utc: str = ""
    oos_start_utc: str = ""
    oos_end_utc: str = ""
    oos_bar_count: int = 0
    oos_bar_returns_path: str = ""
    oos_bar_returns_sha256: str = ""
    starting_equity: float = 1.0
    compounding_mode: str = "compound"
    window_metrics: list[dict[str, Any]] = field(default_factory=list)
    fee_rate_bps: float = 0.0
    fee_model: str = ""
    slippage_rate_bps: float = 0.0
    slippage_model: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-ready dict.

        v1 results (schema_version != v2) emit only the v1 field set so
        that pre-upgrade callers like ``run_backtest_stub`` produce
        byte-shape-identical output to before the upgrade. v2 results
        emit the full field set per ``future_evidence_requirements.md``.
        """
        full = asdict(self)
        if self.schema_version == SCHEMA_BACKTEST_V2:
            return full
        v1_keys = {
            "candidate_id", "symbol", "total_return", "max_drawdown",
            "win_rate", "expectancy", "sharpe", "trades_count",
            "fees_paid", "slippage_cost", "status", "notes", "generated_at",
        }
        return {k: v for k, v in full.items() if k in v1_keys}

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "BacktestResult":
        data = dict(payload or {})
        seed_raw = data.get("random_seed")
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
            schema_version=str(data.get("schema_version") or SCHEMA_BACKTEST_V1),
            run_id=str(data.get("run_id") or ""),
            strategy_code_sha256=str(data.get("strategy_code_sha256") or ""),
            random_seed=(int(seed_raw) if seed_raw is not None else None),
            exchange=str(data.get("exchange") or ""),
            bar_timeframe=str(data.get("bar_timeframe") or ""),
            timezone=str(data.get("timezone") or ""),
            session=str(data.get("session") or ""),
            is_sample_start_utc=str(data.get("is_sample_start_utc") or ""),
            is_sample_end_utc=str(data.get("is_sample_end_utc") or ""),
            oos_start_utc=str(data.get("oos_start_utc") or ""),
            oos_end_utc=str(data.get("oos_end_utc") or ""),
            oos_bar_count=int(data.get("oos_bar_count") or 0),
            oos_bar_returns_path=str(data.get("oos_bar_returns_path") or ""),
            oos_bar_returns_sha256=str(data.get("oos_bar_returns_sha256") or ""),
            starting_equity=(
                float(data["starting_equity"])
                if data.get("starting_equity") is not None
                else 1.0
            ),
            compounding_mode=str(data.get("compounding_mode") or "compound"),
            window_metrics=list(data.get("window_metrics") or []),
            fee_rate_bps=float(data.get("fee_rate_bps") or 0.0),
            fee_model=str(data.get("fee_model") or ""),
            slippage_rate_bps=float(data.get("slippage_rate_bps") or 0.0),
            slippage_model=str(data.get("slippage_model") or ""),
        )

    def is_v2(self) -> bool:
        """Return True iff every v2 contract field is populated and
        schema_version == strategy_lab.backtest.v2."""
        if self.schema_version != SCHEMA_BACKTEST_V2:
            return False
        for name in REQUIRED_V2_STR_FIELDS:
            if not str(getattr(self, name) or ""):
                return False
        if self.timezone != "UTC":
            return False
        if not self.session:
            return False
        if self.oos_bar_count <= 0:
            return False
        if not self.window_metrics:
            return False
        return True


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


def write_bar_returns_csv(path: Path, rows: Iterable[tuple[str, float]]) -> str:
    """Write a 2-column (timestamp_utc, bar_return) CSV at ``path``.

    The header line and 10-decimal float formatting are part of the
    ``strategy_lab.backtest.v2`` wire contract. Returns the hex sha256
    of the file's UTF-8 bytes, which the audit verifies on read.
    """
    lines = ["timestamp_utc,bar_return"]
    for ts, ret in rows:
        lines.append(f"{ts},{float(ret):.10f}")
    text = "\n".join(lines) + "\n"
    blob = text.encode("utf-8")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(blob)
    return hashlib.sha256(blob).hexdigest()


def make_v2_result(
    config: BacktestConfig,
    *,
    run_id: str,
    strategy_code_sha256: str,
    random_seed: int | None,
    exchange: str,
    is_sample_start_utc: str,
    is_sample_end_utc: str,
    oos_start_utc: str,
    oos_end_utc: str,
    bar_returns: list[tuple[str, float]],
    window_metrics: list[WindowMetric],
    bar_returns_dir: Path,
    starting_equity: float = 1.0,
    compounding_mode: str = "compound",
    session: str = "24x7",
    fee_model: str = "linear",
    slippage_model: str = "constant",
    summary_total_return: float = 0.0,
    summary_max_drawdown: float = 0.0,
    summary_win_rate: float = 0.0,
    summary_expectancy: float = 0.0,
    summary_sharpe: float = 0.0,
    trades_count: int = 0,
    fees_paid: float = 0.0,
    slippage_cost: float = 0.0,
    status: str = "OK",
    notes: str = "",
) -> BacktestResult:
    """Construct a ``strategy_lab.backtest.v2`` result and write its
    sibling bar-returns CSV under ``bar_returns_dir``.

    The friction-rate fields (``fee_rate_bps``, ``slippage_rate_bps``)
    are propagated from the ``BacktestConfig`` so that downstream
    friction-stress consumers can scale by rate rather than aggregate
    dollar totals.
    """
    csv_filename = f"{_slug(config.candidate_id)}__{_slug(run_id)}.bar_returns.csv"
    csv_path = bar_returns_dir / csv_filename
    sha256_hex = write_bar_returns_csv(csv_path, bar_returns)
    return BacktestResult(
        candidate_id=config.candidate_id,
        symbol=config.symbol,
        total_return=summary_total_return,
        max_drawdown=summary_max_drawdown,
        win_rate=summary_win_rate,
        expectancy=summary_expectancy,
        sharpe=summary_sharpe,
        trades_count=trades_count,
        fees_paid=fees_paid,
        slippage_cost=slippage_cost,
        status=status,
        notes=notes,
        schema_version=SCHEMA_BACKTEST_V2,
        run_id=run_id,
        strategy_code_sha256=strategy_code_sha256,
        random_seed=random_seed,
        exchange=exchange,
        bar_timeframe=config.timeframe,
        timezone="UTC",
        session=session,
        is_sample_start_utc=is_sample_start_utc,
        is_sample_end_utc=is_sample_end_utc,
        oos_start_utc=oos_start_utc,
        oos_end_utc=oos_end_utc,
        oos_bar_count=len(bar_returns),
        oos_bar_returns_path=csv_filename,
        oos_bar_returns_sha256=sha256_hex,
        starting_equity=starting_equity,
        compounding_mode=compounding_mode,
        window_metrics=[wm.to_dict() for wm in window_metrics],
        fee_rate_bps=config.fee_bps,
        fee_model=fee_model,
        slippage_rate_bps=config.slippage_bps,
        slippage_model=slippage_model,
    )

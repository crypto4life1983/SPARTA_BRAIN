from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
ANTI_OVERFIT_ROOT = DATA_ROOT / "anti_overfit"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned or "candidate"


@dataclass(slots=True)
class AntiOverfitInput:
    candidate_id: str
    in_sample_return: float
    out_of_sample_return: float
    walk_forward_pass_rate: float
    symbol_count_tested: int
    regime_count_tested: int
    trades_count: int
    max_drawdown: float
    parameter_sensitivity_score: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "AntiOverfitInput":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            in_sample_return=float(data.get("in_sample_return") or 0.0),
            out_of_sample_return=float(data.get("out_of_sample_return") or 0.0),
            walk_forward_pass_rate=float(data.get("walk_forward_pass_rate") or 0.0),
            symbol_count_tested=int(data.get("symbol_count_tested") or 0),
            regime_count_tested=int(data.get("regime_count_tested") or 0),
            trades_count=int(data.get("trades_count") or 0),
            max_drawdown=float(data.get("max_drawdown") or 0.0),
            parameter_sensitivity_score=float(data.get("parameter_sensitivity_score") or 0.0),
        )


@dataclass(slots=True)
class AntiOverfitResult:
    candidate_id: str
    passed: bool
    risk_level: str
    score: int
    failure_reasons: list[str] = field(default_factory=list)
    recommendation: str = "reject_or_rework"
    status: str = "EXPERIMENTAL"
    generated_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "AntiOverfitResult":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            passed=bool(data.get("passed") or False),
            risk_level=str(data.get("risk_level") or "HIGH"),
            score=int(data.get("score") or 0),
            failure_reasons=list(data.get("failure_reasons") or []),
            recommendation=str(data.get("recommendation") or "reject_or_rework"),
            status=str(data.get("status") or "EXPERIMENTAL"),
            generated_at=str(data.get("generated_at") or _utc_now()),
        )


def _result_path(candidate_id: str) -> Path:
    ANTI_OVERFIT_ROOT.mkdir(parents=True, exist_ok=True)
    candidate = assert_approved_path(ANTI_OVERFIT_ROOT)
    filename = f"{_slug(candidate_id)}__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    return candidate / filename


def _score_from_input(data: AntiOverfitInput, failures: list[str]) -> int:
    score = 100
    score -= max(0, 30 - min(data.trades_count, 30)) * 2
    score -= max(0, 3 - min(data.symbol_count_tested, 3)) * 10
    score -= max(0, 3 - min(data.regime_count_tested, 3)) * 10
    score -= int(max(0.0, 0.60 - min(data.walk_forward_pass_rate, 1.0)) * 100)
    score -= int(max(0.0, data.max_drawdown - 0.35) * 100)
    score -= int(max(0.0, data.parameter_sensitivity_score - 0.70) * 100)
    if data.out_of_sample_return <= 0:
        score -= 30
    if failures:
        score -= min(25, len(failures) * 5)
    return max(0, min(100, score))


def evaluate_anti_overfit(candidate: AntiOverfitInput | dict[str, Any] | None = None) -> AntiOverfitResult:
    data = candidate if isinstance(candidate, AntiOverfitInput) else AntiOverfitInput.from_dict(candidate)
    failures: list[str] = []

    if data.out_of_sample_return <= 0:
        failures.append("out_of_sample_return_non_positive")
    if data.walk_forward_pass_rate < 0.60:
        failures.append("walk_forward_pass_rate_below_threshold")
    if data.symbol_count_tested < 3:
        failures.append("symbol_count_tested_below_threshold")
    if data.regime_count_tested < 3:
        failures.append("regime_count_tested_below_threshold")
    if data.trades_count < 30:
        failures.append("trades_count_below_threshold")
    if data.max_drawdown > 0.35:
        failures.append("max_drawdown_above_threshold")
    if data.parameter_sensitivity_score > 0.70:
        failures.append("parameter_sensitivity_score_above_threshold")

    passed = not failures
    score = _score_from_input(data, failures)
    if passed and score >= 80:
        risk_level = "LOW"
    elif score >= 60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    recommendation = "continue_research" if passed and risk_level in {"LOW", "MEDIUM"} else "reject_or_rework"

    result = AntiOverfitResult(
        candidate_id=data.candidate_id,
        passed=passed,
        risk_level=risk_level,
        score=score,
        failure_reasons=failures,
        recommendation=recommendation,
    )

    payload = {
        "schema_version": "strategy_lab.anti_overfit_result.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "input": data.to_dict(),
        "result": result.to_dict(),
    }
    output_path = _result_path(data.candidate_id)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return result


from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
REGIME_SCORES_ROOT = DATA_ROOT / "regime_scores"

REGIMES = (
    "TREND",
    "RANGE",
    "HIGH_VOL",
    "LOW_VOL",
    "COMPRESSION",
    "EXPANSION",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned or "candidate"


def _normalize_regime_key(name: str) -> str:
    lookup = {
        "TREND": "trend_return",
        "RANGE": "range_return",
        "HIGH_VOL": "high_vol_return",
        "LOW_VOL": "low_vol_return",
        "COMPRESSION": "compression_return",
        "EXPANSION": "expansion_return",
    }
    key = str(name or "").upper()
    if key not in lookup:
        raise ValueError(f"Unknown regime: {name!r}")
    return lookup[key]


@dataclass(slots=True)
class RegimeTestInput:
    candidate_id: str
    trend_return: float
    range_return: float
    high_vol_return: float
    low_vol_return: float
    compression_return: float
    expansion_return: float
    regime_sample_count: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "RegimeTestInput":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            trend_return=float(data.get("trend_return") or 0.0),
            range_return=float(data.get("range_return") or 0.0),
            high_vol_return=float(data.get("high_vol_return") or 0.0),
            low_vol_return=float(data.get("low_vol_return") or 0.0),
            compression_return=float(data.get("compression_return") or 0.0),
            expansion_return=float(data.get("expansion_return") or 0.0),
            regime_sample_count=int(data.get("regime_sample_count") or 0),
        )


@dataclass(slots=True)
class RegimeScoreResult:
    candidate_id: str
    regime_score: int
    passed: bool
    weak_regimes: list[str] = field(default_factory=list)
    strongest_regime: str = ""
    weakest_regime: str = ""
    recommendation: str = "reject_or_rework"
    status: str = "EXPERIMENTAL"
    generated_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "RegimeScoreResult":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            regime_score=int(data.get("regime_score") or 0),
            passed=bool(data.get("passed") or False),
            weak_regimes=list(data.get("weak_regimes") or []),
            strongest_regime=str(data.get("strongest_regime") or ""),
            weakest_regime=str(data.get("weakest_regime") or ""),
            recommendation=str(data.get("recommendation") or "reject_or_rework"),
            status=str(data.get("status") or "EXPERIMENTAL"),
            generated_at=str(data.get("generated_at") or _utc_now()),
        )


def _result_path(candidate_id: str) -> Path:
    REGIME_SCORES_ROOT.mkdir(parents=True, exist_ok=True)
    candidate = assert_approved_path(REGIME_SCORES_ROOT)
    filename = f"{_slug(candidate_id)}__{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    return candidate / filename


def _score_value(value: float) -> int:
    if value <= 0:
        return 0
    if value < 2:
        return 5
    if value < 5:
        return 10
    if value < 10:
        return 18
    return 25


def _extract_regime_pairs(data: RegimeTestInput) -> list[tuple[str, float]]:
    return [
        ("TREND", data.trend_return),
        ("RANGE", data.range_return),
        ("HIGH_VOL", data.high_vol_return),
        ("LOW_VOL", data.low_vol_return),
        ("COMPRESSION", data.compression_return),
        ("EXPANSION", data.expansion_return),
    ]


def evaluate_regime_score(candidate: RegimeTestInput | dict[str, Any] | None = None) -> RegimeScoreResult:
    data = candidate if isinstance(candidate, RegimeTestInput) else RegimeTestInput.from_dict(candidate)
    pairs = _extract_regime_pairs(data)
    if not pairs:
        raise ValueError("No regime data available")

    strongest_regime = max(pairs, key=lambda item: item[1])[0]
    weakest_regime = min(pairs, key=lambda item: item[1])[0]

    weak_regimes: list[str] = []
    for regime_name, value in pairs:
        if value <= 0 or value < 3.0:
            weak_regimes.append(regime_name)

    passed = data.regime_sample_count >= 3 and all(value > 0 for _, value in pairs)

    balance_penalty = 0
    positive_count = 0
    total_score = 0
    for _, value in pairs:
        if value > 0:
            positive_count += 1
        total_score += _score_value(value)
        if value <= 0:
            balance_penalty += 20
        elif value < 3.0:
            balance_penalty += 5

    regime_score = max(0, min(100, int(round((total_score / len(pairs)) * 4 - balance_penalty))))
    if data.regime_sample_count < 3:
        regime_score = min(regime_score, 35)
        passed = False

    if passed:
        recommendation = "continue_research"
    else:
        recommendation = "reject_or_rework"

    result = RegimeScoreResult(
        candidate_id=data.candidate_id,
        regime_score=regime_score,
        passed=passed,
        weak_regimes=sorted(set(weak_regimes)),
        strongest_regime=strongest_regime,
        weakest_regime=weakest_regime,
        recommendation=recommendation,
    )

    payload = {
        "schema_version": "strategy_lab.regime_score_result.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "input": data.to_dict(),
        "result": result.to_dict(),
    }
    output_path = _result_path(data.candidate_id)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return result


def score_regime_fit(candidate: dict | None = None, regime: str = "") -> dict:
    data = RegimeTestInput.from_dict(candidate)
    key = _normalize_regime_key(regime)
    value = getattr(data, key)
    return {
        "status": "EXPERIMENTAL",
        "candidate_id": data.candidate_id,
        "regime": str(regime or "").upper(),
        "score": _score_value(value),
        "regimes": REGIMES,
    }


from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .registry import get_candidate
from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
RESEARCH_PLANS_ROOT = DATA_ROOT / "research_plans"
PLANS_FILE = RESEARCH_PLANS_ROOT / "plans.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_store() -> dict[str, Any]:
    return {
        "schema_version": "strategy_lab.research_plan.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "plans": [],
    }


def _load_store() -> dict[str, Any]:
    if not PLANS_FILE.exists():
        return _empty_store()
    try:
        payload = json.loads(PLANS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    payload.setdefault("schema_version", "strategy_lab.research_plan.v1")
    payload.setdefault("generated_at", _utc_now())
    payload.setdefault("mode", "EXPERIMENTAL")
    payload.setdefault("plans", [])
    return payload


def _write_store(store: dict[str, Any]) -> None:
    RESEARCH_PLANS_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(RESEARCH_PLANS_ROOT)
    path = approved / PLANS_FILE.name
    path.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")


@dataclass(slots=True)
class ResearchPlan:
    candidate_id: str
    hypothesis: str
    symbols_to_test: list[str] = field(default_factory=list)
    timeframes_to_test: list[str] = field(default_factory=list)
    regimes_to_test: list[str] = field(default_factory=list)
    required_min_trades: int = 0
    required_oos_periods: int = 0
    required_walk_forward_windows: int = 0
    risk_questions: list[str] = field(default_factory=list)
    rejection_conditions: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_utc_now)
    status: str = "EXPERIMENTAL"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "ResearchPlan":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            hypothesis=str(data.get("hypothesis") or ""),
            symbols_to_test=list(data.get("symbols_to_test") or []),
            timeframes_to_test=list(data.get("timeframes_to_test") or []),
            regimes_to_test=list(data.get("regimes_to_test") or []),
            required_min_trades=int(data.get("required_min_trades") or 0),
            required_oos_periods=int(data.get("required_oos_periods") or 0),
            required_walk_forward_windows=int(data.get("required_walk_forward_windows") or 0),
            risk_questions=list(data.get("risk_questions") or []),
            rejection_conditions=list(data.get("rejection_conditions") or []),
            created_at=str(data.get("created_at") or _utc_now()),
            status=str(data.get("status") or "EXPERIMENTAL"),
        )


def load_research_plans() -> list[dict[str, Any]]:
    return list(_load_store().get("plans", []))


def get_research_plan(candidate_id: str) -> dict[str, Any] | None:
    needle = str(candidate_id).strip()
    for plan in load_research_plans():
        if str(plan.get("candidate_id") or "") == needle:
            return plan
    return None


def _requires_in_research(candidate_id: str) -> dict[str, Any]:
    candidate = get_candidate(candidate_id)
    if candidate is None:
        raise KeyError(f"Unknown candidate: {candidate_id}")
    lifecycle_state = str(candidate.get("lifecycle_state") or candidate.get("status") or "IDEA").upper()
    if lifecycle_state != "IN_RESEARCH":
        raise ValueError("Research plans require candidate lifecycle_state = IN_RESEARCH")
    return candidate


def create_research_plan(candidate_id: str) -> dict[str, Any]:
    candidate = _requires_in_research(candidate_id)
    hypothesis = str(candidate.get("description") or candidate.get("notes") or "").strip()
    symbols = []
    notes = candidate.get("notes")
    if isinstance(notes, dict):
        symbols = list(notes.get("symbols") or [])
    symbols = [str(item).strip() for item in symbols if str(item).strip()]
    if not symbols:
        symbols = list(candidate.get("symbols_tested") or [])
    symbols = [str(item).strip() for item in symbols if str(item).strip()]

    timeframes = []
    if isinstance(notes, dict):
        timeframes = list(notes.get("timeframe") and [notes.get("timeframe")] or [])
    if not timeframes:
        timeframes = list(candidate.get("timeframes_tested") or [])
    timeframes = [str(item).strip() for item in timeframes if str(item).strip()]

    regimes = [
        "TREND",
        "RANGE",
        "HIGH_VOL",
        "LOW_VOL",
        "COMPRESSION",
        "EXPANSION",
    ]
    plan = ResearchPlan(
        candidate_id=str(candidate_id).strip(),
        hypothesis=hypothesis,
        symbols_to_test=symbols or ["BTCUSDT", "ETHUSDT", "XRPUSDT"],
        timeframes_to_test=timeframes or ["1D"],
        regimes_to_test=regimes,
        required_min_trades=30,
        required_oos_periods=3,
        required_walk_forward_windows=3,
        risk_questions=[
            "Does the edge survive fees and slippage?",
            "Does performance remain stable across symbols?",
            "Does the edge degrade outside the primary regime?",
        ],
        rejection_conditions=[
            "out_of_sample_return <= 0",
            "walk_forward_pass_rate < 0.60",
            "symbol_count_tested < 3",
            "regime_count_tested < 3",
            "trades_count < 30",
            "max_drawdown > 0.35",
            "parameter_sensitivity_score > 0.70",
        ],
    )

    store = _load_store()
    plans = [item for item in store.get("plans", []) if str(item.get("candidate_id") or "") != plan.candidate_id]
    plans.append(plan.to_dict())
    store["generated_at"] = _utc_now()
    store["plans"] = sorted(plans, key=lambda item: str(item.get("candidate_id") or ""))
    _write_store(store)
    return plan.to_dict()


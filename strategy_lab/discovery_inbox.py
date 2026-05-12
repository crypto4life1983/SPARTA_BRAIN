from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .registry import create_candidate, get_candidate
from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
DISCOVERY_INBOX_ROOT = DATA_ROOT / "discovery_inbox"
IDEAS_FILE = DISCOVERY_INBOX_ROOT / "ideas.json"
REPORT_ROOT = LAB_ROOT / "reports"
SEED_BATCH_REPORT = REPORT_ROOT / "seed_candidate_batch.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_store() -> dict[str, Any]:
    return {
        "schema_version": "strategy_lab.discovery_inbox.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "ideas": [],
    }


def _load_store() -> dict[str, Any]:
    if not IDEAS_FILE.exists():
        return _empty_store()
    try:
        payload = json.loads(IDEAS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    payload.setdefault("schema_version", "strategy_lab.discovery_inbox.v1")
    payload.setdefault("generated_at", _utc_now())
    payload.setdefault("mode", "EXPERIMENTAL")
    payload.setdefault("ideas", [])
    return payload


def _write_store(store: dict[str, Any]) -> None:
    DISCOVERY_INBOX_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(DISCOVERY_INBOX_ROOT)
    path = approved / IDEAS_FILE.name
    path.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")


@dataclass(slots=True)
class StrategyIdea:
    idea_id: str
    title: str
    hypothesis: str
    source: str
    symbols: list[str] = field(default_factory=list)
    timeframe: str = ""
    expected_edge: str = ""
    risk_notes: str = ""
    created_at: str = field(default_factory=_utc_now)
    status: str = "IDEA"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "StrategyIdea":
        data = dict(payload or {})
        return cls(
            idea_id=str(data.get("idea_id") or ""),
            title=str(data.get("title") or ""),
            hypothesis=str(data.get("hypothesis") or ""),
            source=str(data.get("source") or ""),
            symbols=list(data.get("symbols") or []),
            timeframe=str(data.get("timeframe") or ""),
            expected_edge=str(data.get("expected_edge") or ""),
            risk_notes=str(data.get("risk_notes") or ""),
            created_at=str(data.get("created_at") or _utc_now()),
            status=str(data.get("status") or "IDEA"),
        )


def add_idea(idea: StrategyIdea | dict[str, Any]) -> dict[str, Any]:
    record = idea if isinstance(idea, StrategyIdea) else StrategyIdea.from_dict(idea)
    if not record.idea_id:
        raise ValueError("idea_id is required")
    if not record.hypothesis.strip():
        raise ValueError("hypothesis is required")
    record.status = "IDEA"
    store = _load_store()
    ideas = [item for item in store.get("ideas", []) if str(item.get("idea_id") or "") != record.idea_id]
    ideas.append(record.to_dict())
    store["generated_at"] = _utc_now()
    store["ideas"] = sorted(ideas, key=lambda item: str(item.get("idea_id") or ""))
    _write_store(store)
    return record.to_dict()


def load_ideas() -> list[dict[str, Any]]:
    return list(_load_store().get("ideas", []))


def get_idea(idea_id: str) -> dict[str, Any] | None:
    needle = str(idea_id).strip()
    for idea in load_ideas():
        if str(idea.get("idea_id") or "") == needle:
            return idea
    return None


def convert_idea_to_candidate(idea_id: str) -> dict[str, Any]:
    idea = get_idea(idea_id)
    if idea is None:
        raise KeyError(f"Unknown idea: {idea_id}")
    if not str(idea.get("hypothesis") or "").strip():
        raise ValueError("hypothesis is required")
    candidate = create_candidate(
        {
            "candidate_id": str(idea.get("idea_id") or "").strip(),
            "name": str(idea.get("title") or "").strip(),
            "description": str(idea.get("hypothesis") or "").strip(),
            "family": "strategy_lab_discovery",
            "status": "IDEA",
            "lifecycle_state": "IDEA",
            "notes": {
                "source": str(idea.get("source") or ""),
                "expected_edge": str(idea.get("expected_edge") or ""),
                "risk_notes": str(idea.get("risk_notes") or ""),
                "symbols": list(idea.get("symbols") or []),
                "timeframe": str(idea.get("timeframe") or ""),
                "origin_idea_id": str(idea.get("idea_id") or ""),
            },
        }
    )
    return candidate


SEED_IDEA_BATCH: list[StrategyIdea] = [
    StrategyIdea(
        idea_id="seed_donchian_breakout_confirmation",
        title="Donchian Breakout Confirmation",
        hypothesis="A breakout only counts when Donchian expansion is confirmed by ATR expansion and follow-through, reducing false expansion signals.",
        source="seed_batch",
        symbols=["BTCUSDT", "ETHUSDT", "XRPUSDT"],
        timeframe="1D",
        expected_edge="Capture confirmed breakouts after volatility expansion.",
        risk_notes="Can whipsaw in choppy compression regimes and may lag in fast reversals.",
    ),
    StrategyIdea(
        idea_id="seed_atr_compression_expansion",
        title="ATR Compression Expansion",
        hypothesis="Compression in ATR followed by directional release can signal a tradable expansion event before the move becomes crowded.",
        source="seed_batch",
        symbols=["BTCUSDT", "ETHUSDT", "XRPUSDT"],
        timeframe="1D",
        expected_edge="Trade volatility release after a dormant period.",
        risk_notes="May underperform in persistently trendless range conditions.",
    ),
    StrategyIdea(
        idea_id="seed_trend_pullback_continuation",
        title="Trend Pullback Continuation",
        hypothesis="A trend filter plus pullback entry can catch continuation moves after brief retracements without chasing extended moves.",
        source="seed_batch",
        symbols=["BTCUSDT", "ETHUSDT", "XRPUSDT"],
        timeframe="1D",
        expected_edge="Ride trend continuation after orderly pullbacks.",
        risk_notes="Can fail when pullbacks become full reversals or when trend filters lag too much.",
    ),
    StrategyIdea(
        idea_id="seed_extreme_expansion_mean_reversion",
        title="Extreme Expansion Mean Reversion",
        hypothesis="After abnormal expansion, exhaustion often creates a short-term reversion window back toward fair value.",
        source="seed_batch",
        symbols=["BTCUSDT", "ETHUSDT", "XRPUSDT"],
        timeframe="1D",
        expected_edge="Fade exhaustion after abnormal expansion.",
        risk_notes="Can be dangerous in strong trend continuation or news-driven breakouts.",
    ),
    StrategyIdea(
        idea_id="seed_regime_filter_overlay",
        title="Regime Filter Overlay",
        hypothesis="A regime overlay can switch between behavior modes based on volatility regime and suppress poor-fit entries when the market environment is unfavorable.",
        source="seed_batch",
        symbols=["BTCUSDT", "ETHUSDT", "XRPUSDT"],
        timeframe="1D",
        expected_edge="Reduce poor-fit trades through regime-aware behavior switching.",
        risk_notes="Requires reliable regime detection and can over-block if the filter is too strict.",
    ),
]


def seed_candidate_batch() -> dict[str, Any]:
    created_ideas: list[dict[str, Any]] = []
    created_candidates: list[dict[str, Any]] = []
    for idea in SEED_IDEA_BATCH:
        created_ideas.append(add_idea(idea))
        created_candidates.append(convert_idea_to_candidate(idea.idea_id))

    lifecycle_counts: dict[str, int] = {}
    for candidate in created_candidates:
        state = str(candidate.get("lifecycle_state") or candidate.get("status") or "IDEA").upper()
        lifecycle_counts[state] = lifecycle_counts.get(state, 0) + 1

    report = {
        "generated_at": _utc_now(),
        "idea_count": len(created_ideas),
        "candidate_count": len(created_candidates),
        "lifecycle_distribution": lifecycle_counts,
        "seed_ideas": created_ideas,
        "seed_candidates": created_candidates,
    }

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(REPORT_ROOT)
    path = approved / SEED_BATCH_REPORT.name
    lines = [
        "# Strategy Lab Seed Candidate Batch",
        "",
        f"Generated at: {report['generated_at']}",
        f"Idea count: {report['idea_count']}",
        f"Candidate count: {report['candidate_count']}",
        "",
        "## Lifecycle Distribution",
    ]
    for key, value in sorted(lifecycle_counts.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Seed Ideas"])
    for idea in created_ideas:
        lines.extend(
            [
                f"- {idea['idea_id']}: {idea['title']}",
                f"  - hypothesis: {idea['hypothesis']}",
                f"  - symbols: {', '.join(idea.get('symbols') or []) or 'n/a'}",
                f"  - timeframe: {idea.get('timeframe') or 'n/a'}",
                f"  - risk_notes: {idea.get('risk_notes') or 'n/a'}",
            ]
        )
    lines.extend(
        [
            "",
            "## Safety",
            "- isolated: true",
            "- frozen_stack_touched: false",
            "- profit_brain_touched: false",
            "- execution_imports: false",
            "- lifecycle_state: IDEA only",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report

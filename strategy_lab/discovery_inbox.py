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


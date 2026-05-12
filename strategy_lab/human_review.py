from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .lifecycle import transition_strategy
from .registry import get_candidate, update_candidate_state
from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
HUMAN_REVIEW_ROOT = DATA_ROOT / "human_review"
REVIEW_LOG_FILE = HUMAN_REVIEW_ROOT / "review_log.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class HumanReviewDecision:
    candidate_id: str
    reviewer: str
    decision: str
    notes: str
    reviewed_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "HumanReviewDecision":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            reviewer=str(data.get("reviewer") or ""),
            decision=str(data.get("decision") or ""),
            notes=str(data.get("notes") or ""),
            reviewed_at=str(data.get("reviewed_at") or _utc_now()),
        )


def _empty_store() -> dict[str, Any]:
    return {
        "schema_version": "strategy_lab.human_review.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "review_log": [],
    }


def _load_store() -> dict[str, Any]:
    if not REVIEW_LOG_FILE.exists():
        return _empty_store()
    try:
        payload = json.loads(REVIEW_LOG_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    payload.setdefault("schema_version", "strategy_lab.human_review.v1")
    payload.setdefault("generated_at", _utc_now())
    payload.setdefault("mode", "EXPERIMENTAL")
    payload.setdefault("review_log", [])
    return payload


def _write_store(store: dict[str, Any]) -> None:
    HUMAN_REVIEW_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(HUMAN_REVIEW_ROOT)
    path = approved / REVIEW_LOG_FILE.name
    path.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")


def load_review_log() -> list[dict[str, Any]]:
    return list(_load_store().get("review_log", []))


def _append_decision(decision: HumanReviewDecision) -> dict[str, Any]:
    if not decision.reviewer.strip():
        raise ValueError("reviewer is required")
    if not decision.notes.strip():
        raise ValueError("notes is required")
    if not decision.candidate_id.strip():
        raise ValueError("candidate_id is required")
    normalized = decision.decision.strip().upper()
    if normalized not in {"APPROVE_FOR_RESEARCH", "REJECT"}:
        raise ValueError("decision must be APPROVE_FOR_RESEARCH or REJECT")

    store = _load_store()
    entry = decision.to_dict()
    entry["decision"] = normalized
    store["generated_at"] = _utc_now()
    store["review_log"] = list(store.get("review_log", [])) + [entry]
    _write_store(store)
    return entry


def approve_for_research(candidate_id: str, *, reviewer: str, notes: str) -> dict[str, Any]:
    candidate = get_candidate(candidate_id)
    if candidate is None:
        raise KeyError(f"Unknown candidate: {candidate_id}")
    current_state = str(candidate.get("lifecycle_state") or candidate.get("status") or "IDEA").upper()
    if current_state != "IDEA":
        raise ValueError("Human approval can only move IDEA -> IN_RESEARCH")

    decision = HumanReviewDecision(
        candidate_id=str(candidate_id).strip(),
        reviewer=reviewer,
        decision="APPROVE_FOR_RESEARCH",
        notes=notes,
    )
    logged = _append_decision(decision)
    update_candidate_state(candidate_id, "IN_RESEARCH")
    return logged


def reject_candidate(candidate_id: str, *, reviewer: str, notes: str) -> dict[str, Any]:
    if not reviewer.strip():
        raise ValueError("reviewer is required")
    if not notes.strip():
        raise ValueError("notes is required")
    candidate = get_candidate(candidate_id)
    if candidate is None:
        raise KeyError(f"Unknown candidate: {candidate_id}")

    decision = HumanReviewDecision(
        candidate_id=str(candidate_id).strip(),
        reviewer=reviewer,
        decision="REJECT",
        notes=notes,
    )
    logged = _append_decision(decision)
    update_candidate_state(candidate_id, "REJECTED")
    return logged


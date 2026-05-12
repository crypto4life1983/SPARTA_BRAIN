from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evidence_pack import get_latest_evidence_pack
from .registry import get_candidate, update_candidate_state
from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
REPORT_ROOT = LAB_ROOT / "reports"
REVIEW_DECISIONS_ROOT = DATA_ROOT / "review_decisions"
DECISIONS_FILE = REVIEW_DECISIONS_ROOT / "decisions.json"
REPORT_FILE = REPORT_ROOT / "strategy_lab_phase_13_review_decision.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class ReviewDecision:
    candidate_id: str
    reviewer: str
    decision: str
    notes: str
    evidence_recommendation: str
    previous_state: str
    new_state: str
    decided_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "ReviewDecision":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            reviewer=str(data.get("reviewer") or ""),
            decision=str(data.get("decision") or ""),
            notes=str(data.get("notes") or ""),
            evidence_recommendation=str(data.get("evidence_recommendation") or ""),
            previous_state=str(data.get("previous_state") or ""),
            new_state=str(data.get("new_state") or ""),
            decided_at=str(data.get("decided_at") or _utc_now()),
        )


def _empty_store() -> dict[str, Any]:
    return {
        "schema_version": "strategy_lab.review_decision.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "decisions": [],
    }


def _load_store() -> dict[str, Any]:
    if not DECISIONS_FILE.exists():
        return _empty_store()
    try:
        payload = json.loads(DECISIONS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    payload.setdefault("schema_version", "strategy_lab.review_decision.v1")
    payload.setdefault("generated_at", _utc_now())
    payload.setdefault("mode", "EXPERIMENTAL")
    payload.setdefault("decisions", [])
    return payload


def _write_store(store: dict[str, Any]) -> None:
    REVIEW_DECISIONS_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(REVIEW_DECISIONS_ROOT)
    path = approved / DECISIONS_FILE.name
    path.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")


def load_review_decisions() -> list[dict[str, Any]]:
    return list(_load_store().get("decisions", []))


def write_review_decision_report() -> dict[str, Any]:
    store = _load_store()
    _write_report(store)
    return store


def _append_decision(decision: ReviewDecision) -> dict[str, Any]:
    if not decision.reviewer.strip():
        raise ValueError("reviewer is required")
    if not decision.notes.strip():
        raise ValueError("notes is required")
    if not decision.candidate_id.strip():
        raise ValueError("candidate_id is required")
    normalized = decision.decision.strip().upper()
    if normalized not in {"APPROVE_FOR_ROBUST", "REJECT"}:
        raise ValueError("decision must be APPROVE_FOR_ROBUST or REJECT")

    store = _load_store()
    entry = decision.to_dict()
    entry["decision"] = normalized
    store["generated_at"] = _utc_now()
    store["decisions"] = list(store.get("decisions", [])) + [entry]
    _write_store(store)
    return entry


def _load_latest_evidence(candidate_id: str) -> dict[str, Any]:
    pack = get_latest_evidence_pack(candidate_id)
    if not pack:
        raise ValueError(f"No evidence pack available for candidate: {candidate_id}")
    return pack


def approve_backtested_to_robust(candidate_id: str, *, reviewer: str, notes: str) -> dict[str, Any]:
    candidate = get_candidate(candidate_id)
    if candidate is None:
        raise KeyError(f"Unknown candidate: {candidate_id}")
    previous_state = str(candidate.get("lifecycle_state") or candidate.get("status") or "IDEA").upper()
    if previous_state != "BACKTESTED":
        raise ValueError("Approval can only move BACKTESTED -> ROBUST")

    evidence_pack = _load_latest_evidence(candidate_id)
    recommendation = str(evidence_pack.get("recommendation") or "").strip()
    if recommendation != "ready_for_review":
        raise ValueError("Latest evidence pack must recommend ready_for_review")

    decision = ReviewDecision(
        candidate_id=str(candidate_id).strip(),
        reviewer=reviewer,
        decision="APPROVE_FOR_ROBUST",
        notes=notes,
        evidence_recommendation=recommendation,
        previous_state=previous_state,
        new_state="ROBUST",
    )
    logged = _append_decision(decision)
    update_candidate_state(candidate_id, "ROBUST")
    write_review_decision_report()
    return logged


def reject_from_evidence(candidate_id: str, *, reviewer: str, notes: str) -> dict[str, Any]:
    candidate = get_candidate(candidate_id)
    if candidate is None:
        raise KeyError(f"Unknown candidate: {candidate_id}")
    evidence_pack = _load_latest_evidence(candidate_id)
    previous_state = str(candidate.get("lifecycle_state") or candidate.get("status") or "IDEA").upper()
    decision = ReviewDecision(
        candidate_id=str(candidate_id).strip(),
        reviewer=reviewer,
        decision="REJECT",
        notes=notes,
        evidence_recommendation=str(evidence_pack.get("recommendation") or ""),
        previous_state=previous_state,
        new_state="REJECTED",
    )
    logged = _append_decision(decision)
    update_candidate_state(candidate_id, "REJECTED")
    write_review_decision_report()
    return logged


def _write_report(store: dict[str, Any]) -> None:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(REPORT_ROOT)
    path = approved / REPORT_FILE.name
    lines = [
        "# Strategy Lab Phase 13 Review Decision",
        "",
        f"Generated at: {store.get('generated_at') or _utc_now()}",
        f"Decision Count: {len(store.get('decisions', []))}",
        "",
        "## Safety",
        "- isolated: true",
        "- frozen_stack_touched: false",
        "- profit_brain_touched: false",
        "- execution_imports: false",
        "- live_transition_possible: false",
    ]
    for item in store.get("decisions", []):
        lines.extend(
            [
                "",
                f"- {item.get('candidate_id')}: {item.get('decision')} -> {item.get('new_state')}",
                f"  - evidence_recommendation: {item.get('evidence_recommendation')}",
                f"  - reviewer: {item.get('reviewer')}",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    write_review_decision_report()

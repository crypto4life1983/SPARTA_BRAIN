from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .registry import get_candidate, update_candidate_state
from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
REPORT_ROOT = LAB_ROOT / "reports"
WATCHLIST_APPROVAL_ROOT = DATA_ROOT / "watchlist_approvals"
DECISIONS_FILE = WATCHLIST_APPROVAL_ROOT / "decisions.json"
REPORT_FILE = REPORT_ROOT / "strategy_lab_phase_15_watchlist_approval.md"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(slots=True)
class WatchlistDecision:
    candidate_id: str
    reviewer: str
    decision: str
    notes: str
    previous_state: str
    new_state: str
    paper_summary: str
    decided_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "WatchlistDecision":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            reviewer=str(data.get("reviewer") or ""),
            decision=str(data.get("decision") or ""),
            notes=str(data.get("notes") or ""),
            previous_state=str(data.get("previous_state") or ""),
            new_state=str(data.get("new_state") or ""),
            paper_summary=str(data.get("paper_summary") or ""),
            decided_at=str(data.get("decided_at") or _utc_now()),
        )


def _empty_store() -> dict[str, Any]:
    return {
        "schema_version": "strategy_lab.watchlist_approval.v1",
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
    payload.setdefault("schema_version", "strategy_lab.watchlist_approval.v1")
    payload.setdefault("generated_at", _utc_now())
    payload.setdefault("mode", "EXPERIMENTAL")
    payload.setdefault("decisions", [])
    return payload


def _write_store(store: dict[str, Any]) -> None:
    WATCHLIST_APPROVAL_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(WATCHLIST_APPROVAL_ROOT)
    path = approved / DECISIONS_FILE.name
    path.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")


def load_watchlist_decisions() -> list[dict[str, Any]]:
    return list(_load_store().get("decisions", []))


def _append_decision(decision: WatchlistDecision) -> dict[str, Any]:
    if not decision.reviewer.strip():
        raise ValueError("reviewer is required")
    if not decision.notes.strip():
        raise ValueError("notes is required")
    if not decision.paper_summary.strip():
        raise ValueError("paper_summary is required")
    if not decision.candidate_id.strip():
        raise ValueError("candidate_id is required")
    normalized = decision.decision.strip().upper()
    if normalized not in {"APPROVE_FOR_WATCHLIST", "REJECT"}:
        raise ValueError("decision must be APPROVE_FOR_WATCHLIST or REJECT")

    store = _load_store()
    entry = decision.to_dict()
    entry["decision"] = normalized
    store["generated_at"] = _utc_now()
    store["decisions"] = list(store.get("decisions", [])) + [entry]
    _write_store(store)
    return entry


def approve_paper_testing_to_watchlist(candidate_id: str, *, reviewer: str, notes: str, paper_summary: str) -> dict[str, Any]:
    candidate = get_candidate(candidate_id)
    if candidate is None:
        raise KeyError(f"Unknown candidate: {candidate_id}")
    previous_state = str(candidate.get("lifecycle_state") or candidate.get("status") or "IDEA").upper()
    if previous_state != "PAPER_TESTING":
        raise ValueError("Approval can only move PAPER_TESTING -> WATCHLIST")

    decision = WatchlistDecision(
        candidate_id=str(candidate_id).strip(),
        reviewer=reviewer,
        decision="APPROVE_FOR_WATCHLIST",
        notes=notes,
        previous_state=previous_state,
        new_state="WATCHLIST",
        paper_summary=paper_summary,
    )
    logged = _append_decision(decision)
    update_candidate_state(candidate_id, "WATCHLIST")
    write_watchlist_report()
    return logged


def reject_after_paper_testing(candidate_id: str, *, reviewer: str, notes: str, paper_summary: str) -> dict[str, Any]:
    candidate = get_candidate(candidate_id)
    if candidate is None:
        raise KeyError(f"Unknown candidate: {candidate_id}")
    previous_state = str(candidate.get("lifecycle_state") or candidate.get("status") or "IDEA").upper()
    decision = WatchlistDecision(
        candidate_id=str(candidate_id).strip(),
        reviewer=reviewer,
        decision="REJECT",
        notes=notes,
        previous_state=previous_state,
        new_state="REJECTED",
        paper_summary=paper_summary,
    )
    logged = _append_decision(decision)
    update_candidate_state(candidate_id, "REJECTED")
    write_watchlist_report()
    return logged


def _write_report(store: dict[str, Any]) -> None:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(REPORT_ROOT)
    path = approved / REPORT_FILE.name
    lines = [
        "# Strategy Lab Phase 15 Watchlist Approval",
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
        "- watchlist_is_observe_only: true",
    ]
    for item in store.get("decisions", []):
        lines.extend(
            [
                "",
                f"- {item.get('candidate_id')}: {item.get('decision')} -> {item.get('new_state')}",
                f"  - reviewer: {item.get('reviewer')}",
                f"  - paper_summary: {item.get('paper_summary')}",
            ]
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_watchlist_report() -> dict[str, Any]:
    store = _load_store()
    _write_report(store)
    return store


def main() -> None:
    write_watchlist_report()

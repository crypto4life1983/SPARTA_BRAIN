from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .anti_overfit_gate import ANTI_OVERFIT_ROOT
from .backtest_wrapper import BACKTESTS_ROOT
from .paper_arena import PAPER_ARENA_FILE
from .registry import get_candidate
from .regime_score import REGIME_SCORES_ROOT
from .research_plan import RESEARCH_PLANS_ROOT
from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
REPORT_ROOT = LAB_ROOT / "reports"
EVIDENCE_PACKS_ROOT = DATA_ROOT / "evidence_packs"
PACKS_FILE = EVIDENCE_PACKS_ROOT / "packs.json"
REPORT_FILE = REPORT_ROOT / "strategy_lab_phase_12_evidence_pack.md"

REQUIRED_FOR_RESEARCH = ("research_plan", "backtest", "anti_overfit", "regime_score")
REQUIRED_FOR_BACKTESTED = ("backtest", "anti_overfit", "regime_score")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_store() -> dict[str, Any]:
    return {
        "schema_version": "strategy_lab.evidence_pack.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "packs": [],
    }


def _load_store() -> dict[str, Any]:
    if not PACKS_FILE.exists():
        return _empty_store()
    try:
        payload = json.loads(PACKS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    payload.setdefault("schema_version", "strategy_lab.evidence_pack.v1")
    payload.setdefault("generated_at", _utc_now())
    payload.setdefault("mode", "EXPERIMENTAL")
    payload.setdefault("packs", [])
    return payload


def _write_store(store: dict[str, Any]) -> None:
    EVIDENCE_PACKS_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(EVIDENCE_PACKS_ROOT)
    path = approved / PACKS_FILE.name
    path.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")


def _write_report(store: dict[str, Any], pack: dict[str, Any]) -> None:
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(REPORT_ROOT)
    path = approved / REPORT_FILE.name
    lines = [
        "# Strategy Lab Phase 12 Evidence Pack",
        "",
        f"Generated at: {store.get('generated_at') or _utc_now()}",
        f"Candidate: {pack.get('candidate_id') or 'n/a'}",
        f"Lifecycle State: {pack.get('lifecycle_state') or 'n/a'}",
        f"Recommendation: {pack.get('recommendation') or 'collect_more_evidence'}",
        "",
        "## Evidence Summary",
    ]
    summary = pack.get("evidence_summary") if isinstance(pack.get("evidence_summary"), dict) else {}
    for key in (
        "research_plan",
        "backtest",
        "anti_overfit",
        "regime_score",
        "paper_snapshot",
        "complete_required_set",
        "failed_evidence",
    ):
        lines.append(f"- {key}: {summary.get(key)}")
    lines.extend(
        [
            "",
            "## Missing Evidence",
            f"- {', '.join(pack.get('missing_evidence') or []) if pack.get('missing_evidence') else 'none'}",
            "",
            "## Safety",
            "- isolated: true",
            "- frozen_stack_touched: false",
            "- profit_brain_touched: false",
            "- execution_imports: false",
            "- live_deployment_recommended: false",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _latest_json(directory: Path, candidate_id: str) -> dict[str, Any]:
    if not directory.exists():
        return {}
    matches = sorted(
        directory.glob(f"{candidate_id}__*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not matches:
        return {}
    try:
        payload = json.loads(matches[0].read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _extract_block(payload: dict[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("result"), dict):
        return payload["result"]
    return payload


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _load_research_plan(candidate_id: str) -> dict[str, Any]:
    path = RESEARCH_PLANS_ROOT / "plans.json"
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    plans = payload.get("plans", [])
    if not isinstance(plans, list):
        return {}
    for plan in plans:
        if isinstance(plan, dict) and str(plan.get("candidate_id") or "") == candidate_id:
            return plan
    return {}


def _load_paper_snapshot(candidate_id: str) -> dict[str, Any]:
    if not PAPER_ARENA_FILE.exists():
        return {}
    try:
        payload = json.loads(PAPER_ARENA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(payload, dict):
        return {}
    for arena in payload.get("arenas", []) if isinstance(payload.get("arenas", []), list) else []:
        if not isinstance(arena, dict):
            continue
        if str(arena.get("candidate_id") or "") != candidate_id:
            continue
        snapshots = arena.get("snapshots", [])
        if isinstance(snapshots, list) and snapshots:
            latest = snapshots[-1]
            return latest if isinstance(latest, dict) else {}
    return {}


def _candidate_is_allowed(candidate: dict[str, Any]) -> str:
    lifecycle_state = str(candidate.get("lifecycle_state") or candidate.get("status") or "IDEA").upper()
    if lifecycle_state not in {"IN_RESEARCH", "BACKTESTED"}:
        raise ValueError("Evidence packs require candidate lifecycle_state = IN_RESEARCH or BACKTESTED")
    return lifecycle_state


def load_evidence_packs() -> list[dict[str, Any]]:
    return list(_load_store().get("packs", []))


def get_latest_evidence_pack(candidate_id: str | None = None) -> dict[str, Any] | None:
    packs = load_evidence_packs()
    if not packs:
        return None
    if candidate_id is None:
        return max(packs, key=lambda item: str(item.get("created_at") or ""))
    needle = str(candidate_id).strip()
    matches = [pack for pack in packs if str(pack.get("candidate_id") or "") == needle]
    if not matches:
        return None
    return max(matches, key=lambda item: str(item.get("created_at") or ""))


@dataclass(slots=True)
class EvidencePack:
    candidate_id: str
    lifecycle_state: str
    research_plan_found: bool
    backtest_found: bool
    anti_overfit_found: bool
    regime_score_found: bool
    paper_snapshot_found: bool
    missing_evidence: list[str] = field(default_factory=list)
    evidence_summary: dict[str, Any] = field(default_factory=dict)
    recommendation: str = "collect_more_evidence"
    created_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "EvidencePack":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            lifecycle_state=str(data.get("lifecycle_state") or "IDEA"),
            research_plan_found=bool(data.get("research_plan_found") or False),
            backtest_found=bool(data.get("backtest_found") or False),
            anti_overfit_found=bool(data.get("anti_overfit_found") or False),
            regime_score_found=bool(data.get("regime_score_found") or False),
            paper_snapshot_found=bool(data.get("paper_snapshot_found") or False),
            missing_evidence=list(data.get("missing_evidence") or []),
            evidence_summary=dict(data.get("evidence_summary") or {}),
            recommendation=str(data.get("recommendation") or "collect_more_evidence"),
            created_at=str(data.get("created_at") or _utc_now()),
        )


def _required_fields_for_state(lifecycle_state: str) -> tuple[str, ...]:
    if lifecycle_state == "IN_RESEARCH":
        return REQUIRED_FOR_RESEARCH
    return REQUIRED_FOR_BACKTESTED


def _evaluate_failure(backtest: dict[str, Any], anti: dict[str, Any], regime: dict[str, Any]) -> bool:
    failed = False
    if backtest:
        result = _extract_block(backtest)
        total_return = _safe_float(result.get("total_return"))
        if (total_return is not None and total_return <= 0) or str(result.get("status") or "").upper() == "FAILED":
            failed = True
    if anti:
        result = _extract_block(anti)
        if not bool(result.get("passed") or False):
            failed = True
    if regime:
        result = _extract_block(regime)
        if not bool(result.get("passed") or False):
            failed = True
    return failed


def _summarize(candidate_id: str, lifecycle_state: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], bool]:
    research_plan = _load_research_plan(candidate_id)
    backtest = _extract_block(_latest_json(BACKTESTS_ROOT, candidate_id))
    anti = _extract_block(_latest_json(ANTI_OVERFIT_ROOT, candidate_id))
    regime = _extract_block(_latest_json(REGIME_SCORES_ROOT, candidate_id))
    paper_snapshot = _load_paper_snapshot(candidate_id)

    required_fields = _required_fields_for_state(lifecycle_state)
    missing: list[str] = []
    if "research_plan" in required_fields and not research_plan:
        missing.append("research_plan")
    if "backtest" in required_fields and not backtest:
        missing.append("backtest")
    if "anti_overfit" in required_fields and not anti:
        missing.append("anti_overfit")
    if "regime_score" in required_fields and not regime:
        missing.append("regime_score")

    return research_plan, backtest, anti, regime, bool(paper_snapshot), missing


def build_evidence_pack(candidate_id: str) -> dict[str, Any]:
    candidate = get_candidate(candidate_id)
    if candidate is None:
        raise KeyError(f"Unknown candidate: {candidate_id}")
    lifecycle_state = _candidate_is_allowed(candidate)
    research_plan, backtest, anti, regime, paper_snapshot_found, missing_evidence = _summarize(candidate_id, lifecycle_state)

    failed_evidence = _evaluate_failure(backtest, anti, regime)
    required_fields = _required_fields_for_state(lifecycle_state)
    required_complete = not missing_evidence and all(
        (
            research_plan if "research_plan" in required_fields else True,
            backtest if "backtest" in required_fields else True,
            anti if "anti_overfit" in required_fields else True,
            regime if "regime_score" in required_fields else True,
        )
    )

    if failed_evidence:
        recommendation = "reject_or_rework"
    elif missing_evidence:
        recommendation = "collect_more_evidence"
    elif required_complete:
        recommendation = "ready_for_review"
    else:
        recommendation = "collect_more_evidence"

    evidence_summary = {
        "required_for_state": list(required_fields),
        "research_plan": bool(research_plan),
        "backtest": bool(backtest),
        "anti_overfit": bool(anti),
        "regime_score": bool(regime),
        "paper_snapshot": bool(paper_snapshot_found),
        "complete_required_set": required_complete,
        "failed_evidence": failed_evidence,
    }

    pack = EvidencePack(
        candidate_id=str(candidate_id).strip(),
        lifecycle_state=lifecycle_state,
        research_plan_found=bool(research_plan),
        backtest_found=bool(backtest),
        anti_overfit_found=bool(anti),
        regime_score_found=bool(regime),
        paper_snapshot_found=bool(paper_snapshot_found),
        missing_evidence=sorted(set(missing_evidence)),
        evidence_summary=evidence_summary,
        recommendation=recommendation,
    )

    store = _load_store()
    packs = [item for item in store.get("packs", []) if str(item.get("candidate_id") or "") != pack.candidate_id]
    packs.append(pack.to_dict())
    store["generated_at"] = _utc_now()
    store["packs"] = sorted(packs, key=lambda item: str(item.get("candidate_id") or ""))
    _write_store(store)
    _write_report(store, pack.to_dict())
    return pack.to_dict()

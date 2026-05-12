from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .anti_overfit_gate import ANTI_OVERFIT_ROOT
from .backtest_wrapper import BACKTESTS_ROOT
from .paper_arena import PAPER_ARENA_FILE, PAPER_ARENA_ROOT
from .registry import DATA_ROOT as REGISTRY_DATA_ROOT, load_candidates
from .regime_score import REGIME_SCORES_ROOT
from .safety import assert_approved_path
from .scorecard import StrategyScorecard

LAB_ROOT = Path(__file__).resolve().parent
REPORT_ROOT = LAB_ROOT / "reports"
READINESS_JSON = REPORT_ROOT / "strategy_lab_master_readiness.json"
READINESS_MD = REPORT_ROOT / "strategy_lab_master_readiness.md"

READINESS_STATUSES = ("REJECT", "NEEDS_MORE_RESEARCH", "PAPER_READY", "WATCHLIST_READY")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _latest_file(directory: Path, prefix: str) -> Path | None:
    if not directory.exists():
        return None
    candidates = sorted(directory.glob(f"{prefix}*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    return candidates[0] if candidates else None


def _latest_json_payload(directory: Path, prefix: str) -> dict[str, Any]:
    latest = _latest_file(directory, prefix)
    return _safe_load_json(latest) if latest else {}


def _extract_result_block(payload: dict[str, Any]) -> dict[str, Any]:
    if "result" in payload and isinstance(payload["result"], dict):
        return payload["result"]
    return payload


def _load_paper_arena_snapshots(candidate_id: str) -> list[dict[str, Any]]:
    store = _safe_load_json(PAPER_ARENA_FILE)
    arenas = store.get("arenas", []) if isinstance(store, dict) else []
    for arena in arenas:
        if str(arena.get("candidate_id") or "") == candidate_id:
            snapshots = arena.get("snapshots", [])
            return snapshots if isinstance(snapshots, list) else []
    return []


def _classify_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    candidate_id = str(candidate.get("candidate_id") or "").strip()
    lifecycle_state = str(candidate.get("status") or "IDEA").upper()
    anti_payload = _latest_json_payload(ANTI_OVERFIT_ROOT, f"{candidate_id}__")
    regime_payload = _latest_json_payload(REGIME_SCORES_ROOT, f"{candidate_id}__")
    backtest_payload = _latest_json_payload(BACKTESTS_ROOT, f"{candidate_id}__")
    scorecard_payload = candidate.get("current_scorecard")
    if not isinstance(scorecard_payload, dict):
        scorecard_payload = {}
    paper_snapshots = _load_paper_arena_snapshots(candidate_id)

    anti_result = _extract_result_block(anti_payload)
    regime_result = _extract_result_block(regime_payload)
    backtest_result = _extract_result_block(backtest_payload)
    scorecard = StrategyScorecard.from_dict(scorecard_payload)

    anti_passed = bool(anti_result.get("passed") or False)
    anti_recommendation = str(anti_result.get("recommendation") or "").strip()
    regime_passed = bool(regime_result.get("passed") or False)
    regime_recommendation = str(regime_result.get("recommendation") or "").strip()
    paper_ready = bool(paper_snapshots)

    if lifecycle_state in {"REJECTED", "REJECT"}:
        readiness = "REJECT"
    elif not anti_passed:
        readiness = "REJECT"
    elif anti_recommendation == "reject_or_rework":
        readiness = "REJECT"
    elif not regime_passed:
        readiness = "REJECT"
    elif regime_recommendation == "reject_or_rework":
        readiness = "REJECT"
    elif lifecycle_state in {"PAPER_TESTING", "WATCHLIST"} and paper_ready:
        readiness = "WATCHLIST_READY"
    elif lifecycle_state in {"PAPER_TESTING", "WATCHLIST"}:
        readiness = "NEEDS_MORE_RESEARCH"
    elif lifecycle_state in {"ROBUST", "BACKTESTED"} and anti_passed and regime_passed:
        readiness = "PAPER_READY"
    else:
        readiness = "NEEDS_MORE_RESEARCH"

    reasons: list[str] = []
    if not anti_payload:
        reasons.append("missing_anti_overfit_report")
    if not regime_payload:
        reasons.append("missing_regime_score_report")
    if not backtest_payload:
        reasons.append("missing_backtest_report")
    if lifecycle_state in {"PAPER_TESTING", "WATCHLIST"} and not paper_ready:
        reasons.append("missing_paper_arena_snapshots")
    if readiness == "REJECT" and anti_result:
        reasons.extend(list(anti_result.get("failure_reasons") or []))
    if readiness == "REJECT" and regime_result:
        reasons.extend([f"weak_regime:{item}" for item in regime_result.get("weak_regimes") or []])

    evidence_strength = 0
    if anti_passed:
        evidence_strength += 30
    if regime_passed:
        evidence_strength += 30
    if backtest_result:
        evidence_strength += 20
    if paper_ready:
        evidence_strength += 20

    return {
        "candidate_id": candidate_id,
        "name": str(candidate.get("name") or ""),
        "lifecycle_state": lifecycle_state,
        "readiness": readiness,
        "evidence_strength": evidence_strength,
        "scorecard": scorecard.to_dict(),
        "backtest_result": backtest_result,
        "anti_overfit_result": anti_result,
        "regime_score_result": regime_result,
        "paper_arena_snapshots": paper_snapshots,
        "reasons": sorted(set(reasons)),
    }


def build_master_readiness_report() -> dict[str, Any]:
    candidates = load_candidates()
    classified = [_classify_candidate(candidate) for candidate in candidates]
    status_counts = {status: 0 for status in READINESS_STATUSES}
    for row in classified:
        status_counts[row["readiness"]] = status_counts.get(row["readiness"], 0) + 1

    report = {
        "schema_version": "strategy_lab.master_readiness.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "summary": {
            "candidate_count": len(classified),
            "status_counts": status_counts,
            "live_ready": False,
        },
        "candidates": classified,
        "safety": {
            "isolated": True,
            "frozen_stack_touched": False,
            "profit_brain_touched": False,
            "execution_imports": False,
            "live_deployment_recommended": False,
        },
    }
    return report


def write_master_readiness_report() -> dict[str, Any]:
    report = build_master_readiness_report()
    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    approved_root = assert_approved_path(REPORT_ROOT)
    json_path = approved_root / READINESS_JSON.name
    md_path = approved_root / READINESS_MD.name
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Strategy Lab Master Readiness",
        "",
        f"Generated at: {report['generated_at']}",
        f"Candidates: {report['summary']['candidate_count']}",
        f"Live Ready: {report['summary']['live_ready']}",
        "",
        "## Status Counts",
    ]
    for status in READINESS_STATUSES:
        lines.append(f"- {status}: {report['summary']['status_counts'].get(status, 0)}")
    lines.extend(
        [
            "",
            "## Safety",
            "- isolated: true",
            "- frozen_stack_touched: false",
            "- profit_brain_touched: false",
            "- execution_imports: false",
            "- live_deployment_recommended: false",
            "",
            "## Candidates",
        ]
    )
    for candidate in report["candidates"]:
        lines.extend(
            [
                f"- {candidate['candidate_id']} :: {candidate['readiness']} :: {candidate['lifecycle_state']}",
                f"  - evidence_strength: {candidate['evidence_strength']}",
                f"  - reasons: {', '.join(candidate['reasons']) if candidate['reasons'] else 'none'}",
            ]
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report


def main() -> None:
    write_master_readiness_report()


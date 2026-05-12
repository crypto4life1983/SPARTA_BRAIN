from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .lifecycle import can_transition, normalize_status, transition_strategy

LAB_ROOT = Path(__file__).resolve().parent
REPORT_ROOT = LAB_ROOT / "reports"
DATA_ROOT = LAB_ROOT / "data"
LOG_ROOT = LAB_ROOT / "logs"
CANDIDATES_FILE = DATA_ROOT / "candidates.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _empty_store() -> dict[str, Any]:
    return {
        "schema_version": "strategy_lab.registry.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "candidates": [],
    }


def _load_store() -> dict[str, Any]:
    if not CANDIDATES_FILE.exists():
        return _empty_store()
    try:
        payload = json.loads(CANDIDATES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    payload.setdefault("schema_version", "strategy_lab.registry.v1")
    payload.setdefault("generated_at", _utc_now())
    payload.setdefault("mode", "EXPERIMENTAL")
    payload.setdefault("candidates", [])
    return payload


def _write_store(store: dict[str, Any]) -> None:
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    CANDIDATES_FILE.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")


def normalize_strategy_record(entry: dict[str, Any] | None) -> dict[str, Any]:
    data = dict(entry or {})
    status = normalize_status(str(data.get("status") or "IDEA"))
    candidate_id = str(data.get("candidate_id") or data.get("strategy_id") or "").strip()
    return {
        "candidate_id": candidate_id,
        "strategy_id": candidate_id,
        "name": str(data.get("name") or "").strip(),
        "family": str(data.get("family") or "").strip(),
        "status": status,
        "lifecycle_state": status,
        "description": str(data.get("description") or "").strip(),
        "symbols_tested": list(data.get("symbols_tested") or []),
        "timeframes_tested": list(data.get("timeframes_tested") or []),
        "regimes_tested": list(data.get("regimes_tested") or []),
        "parameter_sets_tested": list(data.get("parameter_sets_tested") or []),
        "created_at": str(data.get("created_at") or _utc_now()),
        "last_updated_at": str(data.get("last_updated_at") or _utc_now()),
        "notes": data.get("notes"),
        "current_scorecard": data.get("current_scorecard"),
        "last_backtest_run_id": data.get("last_backtest_run_id"),
        "last_paper_run_id": data.get("last_paper_run_id"),
        "rejection_reason": data.get("rejection_reason"),
        "promotion_reason": data.get("promotion_reason"),
    }


def build_strategy_library(strategies: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    items = [normalize_strategy_record(item) for item in (strategies or [])]
    return {
        "schema_version": "strategy_lab.library.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "strategies": items,
    }


def load_candidates() -> list[dict[str, Any]]:
    return list(_load_store().get("candidates", []))


def get_candidate(candidate_id: str) -> dict[str, Any] | None:
    needle = str(candidate_id).strip()
    for candidate in load_candidates():
        if str(candidate.get("candidate_id") or "") == needle:
            return candidate
    return None


def create_candidate(entry: dict[str, Any]) -> dict[str, Any]:
    candidate = normalize_strategy_record(entry)
    if not candidate["candidate_id"]:
        raise ValueError("candidate_id is required")
    store = _load_store()
    candidates = [item for item in store.get("candidates", []) if str(item.get("candidate_id") or "") != candidate["candidate_id"]]
    candidates.append(candidate)
    store["generated_at"] = _utc_now()
    store["candidates"] = sorted(candidates, key=lambda item: str(item.get("candidate_id") or ""))
    _write_store(store)
    return candidate


def update_candidate_state(candidate_id: str, new_state: str) -> dict[str, Any]:
    current = get_candidate(candidate_id)
    if current is None:
        raise KeyError(f"Unknown candidate: {candidate_id}")
    target = transition_strategy(current.get("status"), new_state)
    updated = dict(current)
    updated["status"] = target
    updated["lifecycle_state"] = target
    updated["last_updated_at"] = _utc_now()
    store = _load_store()
    store["generated_at"] = _utc_now()
    store["candidates"] = [item if str(item.get("candidate_id") or "") != str(candidate_id) else updated for item in store.get("candidates", [])]
    _write_store(store)
    return updated

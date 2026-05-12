"""Read-only Strategy Lab master readiness loader for SPARTA Commander."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .memory import ROOT

LOCAL_STRATEGY_LAB_REPORT = ROOT / "strategy_lab" / "reports" / "strategy_lab_master_readiness.json"
LOCAL_REPORTS_FALLBACK = ROOT / "reports" / "strategy_lab_master_readiness.json"

READINESS_STATUSES = ("REJECT", "NEEDS_MORE_RESEARCH", "PAPER_READY", "WATCHLIST_READY")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _safe_json(path: Path | None) -> dict[str, Any]:
    try:
        if not path or not path.exists() or not path.is_file():
            return {}
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _first_existing(*paths: Path) -> Path | None:
    for path in paths:
        if path.exists() and path.is_file():
            return path
    return None


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except Exception:
        return 0


def _status_counts(payload: dict[str, Any]) -> dict[str, int]:
    summary = payload.get("summary") or {}
    counts = summary.get("status_counts") or {}
    return {status: _safe_int(counts.get(status, 0)) for status in READINESS_STATUSES}


def load_strategy_lab_master_readiness_report() -> dict[str, Any]:
    path = _first_existing(LOCAL_STRATEGY_LAB_REPORT, LOCAL_REPORTS_FALLBACK)
    payload = _safe_json(path) if path else {}
    if not payload:
        return {
            "schema": "sparta_commander.strategy_lab_master_readiness.v1",
            "generated_at": utc_now(),
            "read_only": True,
            "status": "INSUFFICIENT_DATA",
            "candidate_count": 0,
            "status_counts": {status: 0 for status in READINESS_STATUSES},
            "latest_generated_at": None,
            "safety_status": "ISOLATED / READ_ONLY",
            "source_report": {"path": None, "exists": False},
            "candidates": [],
        }

    summary = payload.get("summary") or {}
    report_path = str(path) if path else None
    return {
        "schema": "sparta_commander.strategy_lab_master_readiness.v1",
        "generated_at": utc_now(),
        "read_only": True,
        "status": "READY" if payload.get("candidates") else "INSUFFICIENT_DATA",
        "candidate_count": _safe_int(summary.get("candidate_count")),
        "status_counts": _status_counts(payload),
        "latest_generated_at": payload.get("generated_at"),
        "safety_status": "ISOLATED / READ_ONLY" if (payload.get("safety") or {}).get("isolated", True) else "UNSAFE",
        "source_report": {"path": report_path, "exists": True},
        "candidates": list(payload.get("candidates") or []),
        "summary": summary,
    }


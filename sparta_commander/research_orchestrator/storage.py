"""File-based persistence for research-orchestrator state.

Layout under <root>/:
    candidates/<candidate_id>.json
    pending_decisions/<decision_id>.json
    audit_logs/<YYYY-MM-DD>.jsonl
    action_ledger/<YYYY-MM-DD>.jsonl

All writes are append-or-replace, never destructive of existing keys.
"""

from __future__ import annotations

import datetime as _dt
import json
import pathlib
from typing import Any, Iterator

from .state import CandidateState


class Storage:
    def __init__(self, root: str | pathlib.Path) -> None:
        self.root = pathlib.Path(root)
        for sub in ("candidates", "pending_decisions", "audit_logs", "action_ledger"):
            (self.root / sub).mkdir(parents=True, exist_ok=True)

    # ---- candidates ----

    def _candidate_path(self, candidate_id: str) -> pathlib.Path:
        safe = candidate_id.replace("/", "_")
        return self.root / "candidates" / f"{safe}.json"

    def save_candidate(self, state: CandidateState) -> pathlib.Path:
        p = self._candidate_path(state.candidate_id)
        state.last_updated_utc = _dt.datetime.now(_dt.timezone.utc).isoformat(
            timespec="microseconds"
        )
        p.write_text(
            json.dumps(state.to_dict(), indent=2, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )
        return p

    def load_candidate(self, candidate_id: str) -> CandidateState | None:
        p = self._candidate_path(candidate_id)
        if not p.exists():
            return None
        return CandidateState.from_dict(json.loads(p.read_text(encoding="utf-8")))

    def list_candidates(self) -> list[CandidateState]:
        out: list[CandidateState] = []
        for p in sorted((self.root / "candidates").glob("*.json")):
            try:
                out.append(CandidateState.from_dict(json.loads(p.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, TypeError):
                continue
        return out

    # ---- pending decisions ----

    def save_pending_decision(self, decision: dict[str, Any]) -> pathlib.Path:
        decision_id = decision.get("decision_id") or _dt.datetime.now(
            _dt.timezone.utc
        ).strftime("%Y%m%dT%H%M%S%fZ")
        decision["decision_id"] = decision_id
        decision.setdefault(
            "created_utc",
            _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="microseconds"),
        )
        p = self.root / "pending_decisions" / f"{decision_id}.json"
        p.write_text(
            json.dumps(decision, indent=2, ensure_ascii=False, default=str) + "\n",
            encoding="utf-8",
        )
        return p

    def list_pending_decisions(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for p in sorted((self.root / "pending_decisions").glob("*.json")):
            try:
                out.append(json.loads(p.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                continue
        return out

    def remove_pending_decision(self, decision_id: str) -> bool:
        p = self.root / "pending_decisions" / f"{decision_id}.json"
        if p.exists():
            p.unlink()
            return True
        return False

    # ---- audit logs + action ledger (append-only jsonl) ----

    def _today_path(self, sub: str) -> pathlib.Path:
        today = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%d")
        return self.root / sub / f"{today}.jsonl"

    def append_audit_log(self, entry: dict[str, Any]) -> None:
        entry.setdefault(
            "ts_utc",
            _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="microseconds"),
        )
        p = self._today_path("audit_logs")
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

    def append_action_ledger(self, entry: dict[str, Any]) -> None:
        entry.setdefault(
            "ts_utc",
            _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="microseconds"),
        )
        p = self._today_path("action_ledger")
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")

    def iter_audit_logs(self, days: int = 7) -> Iterator[dict[str, Any]]:
        today = _dt.datetime.now(_dt.timezone.utc).date()
        for i in range(days):
            d = today - _dt.timedelta(days=i)
            p = self.root / "audit_logs" / f"{d.isoformat()}.jsonl"
            if not p.exists():
                continue
            for line in p.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    def iter_action_ledger(self, days: int = 30) -> Iterator[dict[str, Any]]:
        today = _dt.datetime.now(_dt.timezone.utc).date()
        for i in range(days):
            d = today - _dt.timedelta(days=i)
            p = self.root / "action_ledger" / f"{d.isoformat()}.jsonl"
            if not p.exists():
                continue
            for line in p.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

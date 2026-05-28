"""Read-only adapter for the SPARTA Trade Decision Ledger.

This module normalizes existing external trading artifacts into one viewer
payload. It reads only JSON/JSONL files under the external project's data
tree and never imports trading runtime modules.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DEFAULT_EXTERNAL_ROOT = r"C:\Users\mahmo\obsidian-trade-logger"
_EXTERNAL_ROOT_ENV = "SPARTA_TRADE_LEDGER_ROOT"
_MISSING = "MISSING"
_MAX_JSONL_ROWS_PER_FILE = 5_000

_EXPECTED_JSON_SOURCES = (
    ("data/strategy_decision_state.json", "strategy_decision_state"),
    ("data/trade_coordinator_state.json", "trade_coordinator_state"),
    ("data/evidence_gate.json", "evidence_gate"),
    ("data/final_stack_paper_state.json", "final_stack_paper_state"),
)

_RECORD_FIELDS = (
    "timestamp",
    "source_file",
    "source_type",
    "source_hash",
    "symbol",
    "strategy",
    "side",
    "timeframe",
    "candidate_price",
    "candidate_tags",
    "decision_allowed",
    "decision_mode",
    "decision_reason",
    "blocked_reasons",
    "gate_results",
    "risk_checks",
    "coordinator_reason",
    "evidence_state",
    "strategy_state",
    "final_state",
    "paper_trade_id",
    "paper_outcome",
    "pnl_r",
    "raw_ref",
)


def external_root() -> Path:
    return Path(os.getenv(_EXTERNAL_ROOT_ENV, _DEFAULT_EXTERNAL_ROOT))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _hash_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _hash_text(text: str) -> str:
    return _hash_bytes(text.encode("utf-8", errors="replace"))


def _file_hash(path: Path) -> str:
    try:
        return _hash_bytes(path.read_bytes())
    except OSError:
        return _MISSING


def _empty_record(**values: Any) -> dict[str, Any]:
    record = {field: _MISSING for field in _RECORD_FIELDS}
    record["blocked_reasons"] = []
    record["gate_results"] = []
    record["risk_checks"] = []
    record.update(values)
    return record


def _as_list(value: Any) -> list[Any]:
    if value is None or value == _MISSING:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _normalize_side(value: Any) -> Any:
    if value is None:
        return _MISSING
    side = str(value).strip()
    lowered = side.lower()
    if lowered == "buy":
        return "long"
    if lowered == "sell":
        return "short"
    return side or _MISSING


def _safe_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "MISSING"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, f"PARSE_ERROR:{type(exc).__name__}:{exc}"
    if not isinstance(data, dict):
        return None, "PARSE_ERROR:not_json_object"
    return data, None


def _health(path: str, source_type: str, status: str, **extra: Any) -> dict[str, Any]:
    row = {
        "source_file": path,
        "source_type": source_type,
        "status": status,
        "record_count": extra.pop("record_count", 0),
        "parse_errors": extra.pop("parse_errors", 0),
        "detail": extra.pop("detail", ""),
    }
    row.update(extra)
    return row


def _decision_final_state(allowed: Any, blocked: list[Any]) -> str:
    if allowed is False:
        return "BLOCKED"
    if blocked:
        return "BLOCKED"
    if allowed is True:
        return "ALLOWED"
    return "OBSERVATION"


def _strategy_final_state(allowed: Any, reason: Any) -> str:
    reason_s = str(reason or "")
    if allowed is False:
        return "BLOCKED"
    if reason_s.startswith("recommend_block"):
        return "RECOMMENDED_BLOCK"
    if reason_s == "insufficient_data_allowed_temporarily":
        return "OBSERVATION"
    if allowed is True:
        return "ALLOWED"
    return "MISSING"


def _evidence_final_state(go_no_go: Any, status: Any) -> str:
    if go_no_go == "GO":
        return "READY_FOR_PAPER_EXPERIMENT"
    if go_no_go in ("WATCH", "CONDITIONAL"):
        return "OBSERVATION"
    if go_no_go == "NO_GO":
        return "BLOCKED"
    return str(status or _MISSING)


def _source_allowed(path: Path, root: Path) -> bool:
    try:
        rel = path.resolve().relative_to(root.resolve())
    except (OSError, ValueError):
        return False
    parts = rel.parts
    if not parts:
        return False
    if parts[0] != "data":
        return False
    return path.suffix.lower() in {".json", ".jsonl"}


def _normalize_decision_line(
    root: Path,
    path: Path,
    line_no: int,
    raw: str,
    item: dict[str, Any],
) -> dict[str, Any]:
    candidate = item.get("candidate") if isinstance(item.get("candidate"), dict) else {}
    decision = item.get("decision") if isinstance(item.get("decision"), dict) else {}
    blocked = _as_list(decision.get("blocked_reasons"))
    allowed = decision.get("allow_trade", _MISSING)
    source_file = _rel(root, path)
    return _empty_record(
        timestamp=item.get("timestamp", _MISSING),
        source_file=source_file,
        source_type="candidate_decision_jsonl",
        source_hash=_hash_text(raw),
        symbol=(
            candidate.get("pair")
            or candidate.get("symbol")
            or item.get("symbol")
            or _MISSING
        ),
        strategy=candidate.get("strategy") or decision.get("selected_strategy") or _MISSING,
        side=_normalize_side(candidate.get("direction") or candidate.get("side")),
        timeframe=candidate.get("timeframe") or _MISSING,
        candidate_price=candidate.get("price", _MISSING),
        candidate_tags=_as_list(candidate.get("tags")),
        decision_allowed=allowed,
        decision_mode=decision.get("mode", _MISSING),
        decision_reason=decision.get("reason", _MISSING),
        blocked_reasons=blocked,
        strategy_state=decision.get("metadata", {}).get("strategy_known", _MISSING)
        if isinstance(decision.get("metadata"), dict)
        else _MISSING,
        final_state=_decision_final_state(allowed, blocked),
        raw_ref=f"{source_file}:{line_no}",
    )


def _load_decision_jsonl(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    data_dir = root / "data"
    records: list[dict[str, Any]] = []
    health: list[dict[str, Any]] = []
    if not data_dir.exists():
        health.append(_health("data/**/decisions.jsonl", "candidate_decision_jsonl", "MISSING"))
        return records, health

    paths = sorted(data_dir.rglob("decisions.jsonl"))
    if not paths:
        health.append(_health("data/**/decisions.jsonl", "candidate_decision_jsonl", "MISSING"))
        return records, health

    for path in paths:
        source_file = _rel(root, path)
        if not _source_allowed(path, root):
            health.append(_health(source_file, "candidate_decision_jsonl", "SKIPPED", detail="outside_allowed_data_tree"))
            continue
        count = 0
        parse_errors = 0
        try:
            with path.open("r", encoding="utf-8") as fh:
                for line_no, raw in enumerate(fh, start=1):
                    if count >= _MAX_JSONL_ROWS_PER_FILE:
                        break
                    raw_s = raw.strip()
                    if not raw_s:
                        continue
                    try:
                        item = json.loads(raw_s)
                    except ValueError as exc:
                        parse_errors += 1
                        records.append(_empty_record(
                            timestamp=_MISSING,
                            source_file=source_file,
                            source_type="parse_error",
                            source_hash=_hash_text(raw_s),
                            final_state="PARSE_ERROR",
                            decision_reason=f"PARSE_ERROR:{type(exc).__name__}",
                            raw_ref=f"{source_file}:{line_no}",
                        ))
                        continue
                    if not isinstance(item, dict):
                        parse_errors += 1
                        records.append(_empty_record(
                            timestamp=_MISSING,
                            source_file=source_file,
                            source_type="parse_error",
                            source_hash=_hash_text(raw_s),
                            final_state="PARSE_ERROR",
                            decision_reason="PARSE_ERROR:not_json_object",
                            raw_ref=f"{source_file}:{line_no}",
                        ))
                        continue
                    records.append(_normalize_decision_line(root, path, line_no, raw_s, item))
                    count += 1
        except OSError as exc:
            parse_errors += 1
            records.append(_empty_record(
                source_file=source_file,
                source_type="parse_error",
                source_hash=_MISSING,
                final_state="PARSE_ERROR",
                decision_reason=f"READ_ERROR:{type(exc).__name__}",
                raw_ref=source_file,
            ))
        status = "PARSE_ERROR" if parse_errors else "OK"
        health.append(_health(
            source_file,
            "candidate_decision_jsonl",
            status,
            record_count=count,
            parse_errors=parse_errors,
            detail="malformed lines reported as PARSE_ERROR" if parse_errors else "",
        ))
    return records, health


def _normalize_strategy_state(
    root: Path,
    path: Path,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    source_file = _rel(root, path)
    source_hash = _file_hash(path)
    mode = payload.get("mode", _MISSING)
    out: list[dict[str, Any]] = []
    last = payload.get("last_decision")
    if isinstance(last, dict):
        out.append(_empty_record(
            timestamp=last.get("timestamp", payload.get("last_updated", _MISSING)),
            source_file=source_file,
            source_type="strategy_decision_state",
            source_hash=source_hash,
            symbol=last.get("symbol", _MISSING),
            strategy=last.get("strategy", _MISSING),
            side=_normalize_side(last.get("side")),
            decision_allowed=last.get("allowed", _MISSING),
            decision_mode=mode,
            decision_reason=last.get("reason", _MISSING),
            strategy_state=last.get("reason", _MISSING),
            final_state=_strategy_final_state(last.get("allowed"), last.get("reason")),
            raw_ref=f"{source_file}:last_decision",
        ))
    decisions = payload.get("decisions")
    if isinstance(decisions, dict):
        for strategy, item in sorted(decisions.items()):
            if not isinstance(item, dict):
                continue
            out.append(_empty_record(
                timestamp=item.get("last_decision_at", payload.get("last_updated", _MISSING)),
                source_file=source_file,
                source_type="strategy_decision_state",
                source_hash=source_hash,
                strategy=strategy,
                decision_allowed=item.get("allowed", _MISSING),
                decision_mode=mode,
                decision_reason=item.get("reason", _MISSING),
                strategy_state=item.get("reason", _MISSING),
                final_state=_strategy_final_state(item.get("allowed"), item.get("reason")),
                raw_ref=f"{source_file}:decisions.{strategy}",
            ))
    return out


def _normalize_coordinator_state(
    root: Path,
    path: Path,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    source_file = _rel(root, path)
    source_hash = _file_hash(path)
    out: list[dict[str, Any]] = []
    last = payload.get("last_blocked")
    if isinstance(last, dict):
        reason = last.get("reason", _MISSING)
        out.append(_empty_record(
            timestamp=last.get("timestamp", payload.get("updated_at", _MISSING)),
            source_file=source_file,
            source_type="trade_coordinator_state",
            source_hash=source_hash,
            symbol=last.get("symbol", _MISSING),
            strategy=last.get("strategy", _MISSING),
            side=_normalize_side(last.get("requested_side")),
            decision_allowed=False,
            blocked_reasons=[reason] if reason != _MISSING else [],
            coordinator_reason=reason,
            final_state="BLOCKED",
            raw_ref=f"{source_file}:last_blocked",
        ))
    locks = payload.get("open_locks")
    if isinstance(locks, dict):
        for symbol, lock in sorted(locks.items()):
            if not isinstance(lock, dict):
                continue
            out.append(_empty_record(
                timestamp=payload.get("updated_at", _MISSING),
                source_file=source_file,
                source_type="trade_coordinator_state",
                source_hash=source_hash,
                symbol=symbol,
                side=", ".join(str(_normalize_side(s)) for s in _as_list(lock.get("sides"))) or _MISSING,
                gate_results=[{
                    "name": "open_lock",
                    "status": "ACTIVE",
                    "blocks": _as_list(lock.get("blocks")),
                    "trade_ids": _as_list(lock.get("trade_ids")),
                }],
                coordinator_reason="open_symbol_lock",
                final_state="OBSERVATION",
                raw_ref=f"{source_file}:open_locks.{symbol}",
            ))
    return out


def _normalize_evidence_gate(
    root: Path,
    path: Path,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    source_file = _rel(root, path)
    source_hash = _file_hash(path)
    mode = payload.get("mode", _MISSING)
    go_no_go = payload.get("go_no_go_decision", _MISSING)
    global_status = payload.get("global_status", _MISSING)
    out = [
        _empty_record(
            timestamp=payload.get("generated_at", _MISSING),
            source_file=source_file,
            source_type="evidence_gate",
            source_hash=source_hash,
            decision_mode=mode,
            decision_reason=go_no_go,
            evidence_state=global_status,
            gate_results=[{
                "name": "global_evidence_gate",
                "status": global_status,
                "decision": go_no_go,
            }],
            final_state=_evidence_final_state(go_no_go, global_status),
            raw_ref=f"{source_file}:global",
        )
    ]
    symbols = payload.get("symbols")
    if isinstance(symbols, dict):
        for symbol, item in sorted(symbols.items()):
            if not isinstance(item, dict):
                continue
            blockers = _as_list(item.get("blockers"))
            out.append(_empty_record(
                timestamp=payload.get("generated_at", _MISSING),
                source_file=source_file,
                source_type="evidence_gate",
                source_hash=source_hash,
                symbol=symbol,
                decision_mode=mode,
                decision_reason=go_no_go,
                blocked_reasons=blockers,
                gate_results=[{
                    "name": "symbol_evidence_gate",
                    "status": item.get("status", _MISSING),
                    "blockers": blockers,
                    "required_next_confirmations": _as_list(item.get("required_next_confirmations")),
                }],
                evidence_state=item.get("status", _MISSING),
                final_state=_evidence_final_state(go_no_go, item.get("status")),
                raw_ref=f"{source_file}:symbols.{symbol}",
            ))
    return out


def _normalize_final_stack_paper(
    root: Path,
    path: Path,
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    source_file = _rel(root, path)
    source_hash = _file_hash(path)
    symbols = _as_list(payload.get("symbols")) or [_MISSING]
    state = "PAPER_ONLY" if payload.get("paper_only") is True else "OBSERVATION"
    out = []
    for symbol in symbols:
        out.append(_empty_record(
            timestamp=payload.get("generated_at", _MISSING),
            source_file=source_file,
            source_type="final_stack_paper_state",
            source_hash=source_hash,
            symbol=symbol,
            timeframe=payload.get("timeframe", _MISSING),
            decision_mode="PAPER_ONLY" if payload.get("paper_only") is True else _MISSING,
            gate_results=[{
                "name": "final_stack_paper",
                "paper_only": payload.get("paper_only", _MISSING),
                "no_live_execution": payload.get("no_live_execution", _MISSING),
                "candidate_rows": payload.get("candidate_rows", _MISSING),
            }],
            final_state=state,
            raw_ref=f"{source_file}:symbols.{symbol}",
        ))
    return out


def _load_expected_json_sources(root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    health: list[dict[str, Any]] = []
    normalizers = {
        "strategy_decision_state": _normalize_strategy_state,
        "trade_coordinator_state": _normalize_coordinator_state,
        "evidence_gate": _normalize_evidence_gate,
        "final_stack_paper_state": _normalize_final_stack_paper,
    }
    for rel_path, source_type in _EXPECTED_JSON_SOURCES:
        path = root / rel_path
        if not _source_allowed(path, root):
            health.append(_health(rel_path, source_type, "MISSING"))
            continue
        data, err = _safe_json(path)
        if err == "MISSING":
            health.append(_health(rel_path, source_type, "MISSING"))
            continue
        if err:
            records.append(_empty_record(
                source_file=rel_path,
                source_type="parse_error",
                source_hash=_file_hash(path),
                final_state="PARSE_ERROR",
                decision_reason=err,
                raw_ref=rel_path,
            ))
            health.append(_health(rel_path, source_type, "PARSE_ERROR", parse_errors=1, detail=err))
            continue
        assert data is not None
        new_records = normalizers[source_type](root, path, data)
        records.extend(new_records)
        health.append(_health(rel_path, source_type, "OK", record_count=len(new_records)))
    return records, health


def _summarize(records: list[dict[str, Any]], health: list[dict[str, Any]]) -> dict[str, Any]:
    symbols = {
        str(r.get("symbol"))
        for r in records
        if r.get("symbol") not in (None, "", _MISSING)
    }
    blocked = [
        r for r in records
        if r.get("final_state") == "BLOCKED" or _as_list(r.get("blocked_reasons"))
    ]
    allowed_observed = [
        r for r in records
        if r.get("final_state") in (
            "ALLOWED",
            "OBSERVATION",
            "PAPER_ONLY",
            "READY_FOR_PAPER_EXPERIMENT",
            "RECOMMENDED_BLOCK",
        )
    ]
    parse_errors = sum(int(h.get("parse_errors") or 0) for h in health)
    missing_sources = sum(1 for h in health if h.get("status") == "MISSING")
    return {
        "total_records": len(records),
        "symbols_found": len(symbols),
        "blocked_records": len(blocked),
        "allowed_paper_observation_records": len(allowed_observed),
        "parse_errors": parse_errors,
        "missing_sources": missing_sources,
    }


def _empty_payload(status: str = "MISSING", *, errors: list[str] | None = None) -> dict[str, Any]:
    root = external_root()
    health = [
        _health("data/**/decisions.jsonl", "candidate_decision_jsonl", "MISSING"),
        *[
            _health(rel_path, source_type, "MISSING")
            for rel_path, source_type in _EXPECTED_JSON_SOURCES
        ],
    ]
    return {
        "status": status,
        "generated_at": _now_iso(),
        "external_root": str(root),
        "external_root_exists": root.exists(),
        "safety_banner": "READ ONLY  no broker, no exchange, no order placement, no bot control.",
        "summary": _summarize([], health),
        "source_health": health,
        "records": [],
        "errors": list(errors or []),
    }


def load_payload() -> dict[str, Any]:
    """Return the normalized ledger payload. Never raises intentionally."""
    root = external_root()
    if not root.exists():
        payload = _empty_payload(status="MISSING")
        payload["errors"].append(f"external_root_not_found:{root}")
        return payload

    records: list[dict[str, Any]] = []
    health: list[dict[str, Any]] = []

    decision_records, decision_health = _load_decision_jsonl(root)
    records.extend(decision_records)
    health.extend(decision_health)

    state_records, state_health = _load_expected_json_sources(root)
    records.extend(state_records)
    health.extend(state_health)

    summary = _summarize(records, health)
    if summary["parse_errors"]:
        status = "ERROR" if summary["total_records"] == summary["parse_errors"] else "OK"
    elif summary["total_records"]:
        status = "OK"
    else:
        status = "MISSING"

    return {
        "status": status,
        "generated_at": _now_iso(),
        "external_root": str(root),
        "external_root_exists": True,
        "safety_banner": "READ ONLY  no broker, no exchange, no order placement, no bot control.",
        "summary": summary,
        "source_health": health,
        "records": sorted(
            records,
            key=lambda r: (
                str(r.get("timestamp") or ""),
                str(r.get("source_file") or ""),
                str(r.get("raw_ref") or ""),
            ),
            reverse=True,
        ),
        "errors": [],
    }


__all__ = ["load_payload", "external_root", "_empty_payload"]

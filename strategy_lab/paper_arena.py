from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .safety import assert_approved_path

LAB_ROOT = Path(__file__).resolve().parent
DATA_ROOT = LAB_ROOT / "data"
PAPER_ARENA_ROOT = DATA_ROOT / "paper_arena"
PAPER_ARENA_FILE = PAPER_ARENA_ROOT / "paper_arena.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _slug(value: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in value.strip())
    return cleaned or "candidate"


@dataclass(slots=True)
class PaperArenaConfig:
    candidate_id: str
    symbol: str
    timeframe: str
    start_date: str
    initial_equity: float
    max_simulated_risk_per_trade: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "PaperArenaConfig":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            symbol=str(data.get("symbol") or ""),
            timeframe=str(data.get("timeframe") or ""),
            start_date=str(data.get("start_date") or ""),
            initial_equity=float(data.get("initial_equity") or 0.0),
            max_simulated_risk_per_trade=float(data.get("max_simulated_risk_per_trade") or 0.0),
        )


@dataclass(slots=True)
class PaperArenaSnapshot:
    candidate_id: str
    symbol: str
    simulated_equity: float = 0.0
    simulated_open_positions: int = 0
    simulated_closed_trades: int = 0
    simulated_drawdown: float = 0.0
    status: str = "EXPERIMENTAL"
    notes: str = ""
    generated_at: str = field(default_factory=_utc_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: dict[str, Any] | None) -> "PaperArenaSnapshot":
        data = dict(payload or {})
        return cls(
            candidate_id=str(data.get("candidate_id") or ""),
            symbol=str(data.get("symbol") or ""),
            simulated_equity=float(data.get("simulated_equity") or 0.0),
            simulated_open_positions=int(data.get("simulated_open_positions") or 0),
            simulated_closed_trades=int(data.get("simulated_closed_trades") or 0),
            simulated_drawdown=float(data.get("simulated_drawdown") or 0.0),
            status=str(data.get("status") or "EXPERIMENTAL"),
            notes=str(data.get("notes") or ""),
            generated_at=str(data.get("generated_at") or _utc_now()),
        )


def _empty_store() -> dict[str, Any]:
    return {
        "schema_version": "strategy_lab.paper_arena.v1",
        "generated_at": _utc_now(),
        "mode": "EXPERIMENTAL",
        "arenas": [],
    }


def _load_store() -> dict[str, Any]:
    if not PAPER_ARENA_FILE.exists():
        return _empty_store()
    try:
        payload = json.loads(PAPER_ARENA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty_store()
    if not isinstance(payload, dict):
        return _empty_store()
    payload.setdefault("schema_version", "strategy_lab.paper_arena.v1")
    payload.setdefault("generated_at", _utc_now())
    payload.setdefault("mode", "EXPERIMENTAL")
    payload.setdefault("arenas", [])
    return payload


def _write_store(store: dict[str, Any]) -> None:
    PAPER_ARENA_ROOT.mkdir(parents=True, exist_ok=True)
    approved = assert_approved_path(PAPER_ARENA_ROOT)
    path = approved / PAPER_ARENA_FILE.name
    path.write_text(json.dumps(store, indent=2, sort_keys=True), encoding="utf-8")


def create_paper_arena(config: PaperArenaConfig | dict[str, Any] | None = None) -> dict[str, Any]:
    data = config if isinstance(config, PaperArenaConfig) else PaperArenaConfig.from_dict(config)
    if not data.candidate_id:
        raise ValueError("candidate_id is required")
    store = _load_store()
    arenas = [item for item in store.get("arenas", []) if str(item.get("candidate_id") or "") != data.candidate_id]
    arena = {
        "candidate_id": data.candidate_id,
        "symbol": data.symbol,
        "timeframe": data.timeframe,
        "start_date": data.start_date,
        "initial_equity": data.initial_equity,
        "max_simulated_risk_per_trade": data.max_simulated_risk_per_trade,
        "status": "EXPERIMENTAL",
        "generated_at": _utc_now(),
        "snapshots": [],
    }
    arenas.append(arena)
    store["generated_at"] = _utc_now()
    store["arenas"] = sorted(arenas, key=lambda item: str(item.get("candidate_id") or ""))
    _write_store(store)
    return arena


def load_paper_arena(candidate_id: str | None = None) -> dict[str, Any]:
    store = _load_store()
    if candidate_id is None:
        return store
    needle = str(candidate_id).strip()
    for arena in store.get("arenas", []):
        if str(arena.get("candidate_id") or "") == needle:
            return arena
    return {}


def update_paper_snapshot(
    candidate_id: str,
    snapshot: PaperArenaSnapshot | dict[str, Any],
) -> dict[str, Any]:
    record = snapshot if isinstance(snapshot, PaperArenaSnapshot) else PaperArenaSnapshot.from_dict(snapshot)
    if not str(candidate_id).strip():
        raise ValueError("candidate_id is required")
    if str(record.candidate_id or "").strip() != str(candidate_id).strip():
        record = PaperArenaSnapshot(
            candidate_id=str(candidate_id).strip(),
            symbol=record.symbol,
            simulated_equity=record.simulated_equity,
            simulated_open_positions=record.simulated_open_positions,
            simulated_closed_trades=record.simulated_closed_trades,
            simulated_drawdown=record.simulated_drawdown,
            status=record.status,
            notes=record.notes,
        )

    store = _load_store()
    arenas = []
    updated_arena: dict[str, Any] | None = None
    for arena in store.get("arenas", []):
        if str(arena.get("candidate_id") or "") == str(candidate_id).strip():
            updated_arena = dict(arena)
            snapshots = list(updated_arena.get("snapshots", []))
            snapshots.append(record.to_dict())
            updated_arena["snapshots"] = snapshots
            updated_arena["symbol"] = record.symbol or updated_arena.get("symbol", "")
            updated_arena["status"] = record.status
            updated_arena["generated_at"] = _utc_now()
            arenas.append(updated_arena)
        else:
            arenas.append(arena)
    if updated_arena is None:
        updated_arena = {
            "candidate_id": str(candidate_id).strip(),
            "symbol": record.symbol,
            "timeframe": "",
            "start_date": "",
            "initial_equity": 0.0,
            "max_simulated_risk_per_trade": 0.0,
            "status": record.status,
            "generated_at": _utc_now(),
            "snapshots": [record.to_dict()],
        }
        arenas.append(updated_arena)
    store["generated_at"] = _utc_now()
    store["arenas"] = sorted(arenas, key=lambda item: str(item.get("candidate_id") or ""))
    _write_store(store)
    return updated_arena


def run_paper_arena(candidate: dict[str, Any] | None = None, *, symbol: str = "", timeframe: str = "") -> dict[str, Any]:
    record = dict(candidate or {})
    return {
        "status": "EXPERIMENTAL",
        "paper_run_id": record.get("paper_run_id") or "",
        "candidate_id": record.get("candidate_id") or record.get("strategy_id") or "",
        "symbol": symbol,
        "timeframe": timeframe,
        "generated_at": _utc_now(),
        "simulated_signal_count": 0,
        "simulated_trade_count": 0,
        "simulated_metrics": {},
        "simulated_mode": "paper_only",
        "notes": "stub",
    }


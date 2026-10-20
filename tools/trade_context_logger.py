"""Metadata-only trade context logger for future Brain analysis.

This module does not place, block, enter, exit, or mutate trades. It only
normalizes optional context fields and appends JSONL records when called.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LOG_PATH = ROOT / "data" / "trade_context_log.jsonl"

UNKNOWN_TEXT_FIELDS = {
    "regime_at_entry",
    "strategy_name",
    "rejection_reason",
}

CONTEXT_FIELDS = (
    "regime_at_entry",
    "strategy_name",
    "expected_r",
    "atr_at_entry",
    "atr_avg_at_entry",
    "ema20_at_entry",
    "ema50_at_entry",
    "ema200_at_entry",
    "breakout_level",
    "breakout_distance",
    "candle_body_strength",
    "rejection_reason",
)

TRADE_REFERENCE_FIELDS = (
    "trade_id",
    "symbol",
    "side",
    "entry_time",
    "entry_price",
    "setup_id",
)


def build_trade_context_record(
    trade: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
    *,
    event_type: str = "trade_recorded",
    timestamp_utc: str | None = None,
) -> dict[str, Any]:
    """Return a normalized context record without mutating inputs."""
    trade = dict(trade or {})
    context = dict(context or {})
    record: dict[str, Any] = {
        "timestamp_utc": timestamp_utc or _utc_now(),
        "event_type": event_type,
    }
    for field in TRADE_REFERENCE_FIELDS:
        record[field] = _reference_value(context, trade, field)
    for field in CONTEXT_FIELDS:
        value = _first_present(context, trade, field)
        record[field] = _default_value(field) if value is None else value
    return record


def append_trade_context(
    trade: dict[str, Any] | None = None,
    context: dict[str, Any] | None = None,
    *,
    event_type: str = "trade_recorded",
    log_path: str | Path = DEFAULT_LOG_PATH,
) -> dict[str, Any]:
    """Append one JSON object to the context log and return the logged record."""
    record = build_trade_context_record(trade, context, event_type=event_type)
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
    return record


def log_trade_context_passthrough(
    trade: dict[str, Any],
    context: dict[str, Any] | None = None,
    *,
    event_type: str = "trade_recorded",
    log_path: str | Path = DEFAULT_LOG_PATH,
) -> dict[str, Any]:
    """Log context and return the exact original trade object."""
    append_trade_context(trade, context, event_type=event_type, log_path=log_path)
    return trade


def _first_present(primary: dict[str, Any], fallback: dict[str, Any], field: str) -> Any:
    if field in primary and primary[field] is not None:
        return primary[field]
    if field in fallback and fallback[field] is not None:
        return fallback[field]
    return None


def _reference_value(context: dict[str, Any], trade: dict[str, Any], field: str) -> Any:
    value = _first_present(context, trade, field)
    if value is not None:
        return value
    if field == "trade_id":
        return _first_present(context, trade, "id")
    if field == "entry_price":
        return _first_present(context, trade, "entry")
    if field == "entry_time":
        return _first_present(context, trade, "opened_at") or _first_present(context, trade, "open_date")
    if field == "side":
        return _first_present(context, trade, "direction")
    return None


def _default_value(field: str) -> Any:
    return "UNKNOWN" if field in UNKNOWN_TEXT_FIELDS else None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

"""tools/trade_features.py — entry-bar features of paper trades, bucketed for the rule search.

READ ONLY · OBSERVATION ONLY · NO LIVE READINESS CLAIM · NO STRATEGY APPROVAL · NO BROKER / NO ORDER

Source: data/trade_context_log.jsonl, the metadata-only record the paper bot appends at
every open (tools/trade_context_logger.py; event_type trade_entry_recorded). Since
2026-10-20 the bot also writes range_pct, atr_expansion, volume_ratio, range_position,
donchian_width_pct, ema20_dist_atr and ema200_dist_atr; older records carry only
candle_body_strength, atr_at_entry / atr_avg_at_entry and the EMA levels, from which the
buckets below are derived where possible. A trade without a record (or without the field)
simply has no bucket and falls out of that cell.

The buckets are coarse on purpose: the rule search Bonferroni-deflates every cell it tests,
so every extra cut costs power. Thresholds are fixed here, not fitted.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONTEXT_PATH = _REPO_ROOT / "data" / "trade_context_log.jsonl"

FEATURE_FIELDS: tuple[str, ...] = (
    "body_bucket",            # signal-bar body / range
    "atr_expansion_bucket",   # atr14 at entry / mean of the 3 previous atr14
    "volume_bucket",          # signal-bar volume / 20-day mean volume
    "range_pos_bucket",       # price position inside the 20-day range
    "ema20_dist_bucket",      # (close - ema20) / atr14
    "ema200_side",            # close above / below ema200
)

# Fixed thresholds (documented, never fitted). body 0.805 = the bot-side shadow pair's
# full-body cut; the others are round numbers.
BODY_EDGES = ((0.33, "weak"), (0.66, "mid"), (0.805, "strong"))      # else "full"
ATR_EXP_EDGES = ((0.9, "contracting"), (1.1, "flat"))                 # else "expanding"
VOLUME_EDGES = ((0.8, "low"), (1.5, "normal"))                        # else "high"
EMA20_EDGES = ((-1.0, "far_below"), (0.0, "below"), (1.0, "above"))   # else "far_above"


def _edges(value: float, edges, last: str) -> str:
    for edge, label in edges:
        if value < edge:
            return label
    return last


def _f(v: Any) -> float | None:
    try:
        if v is None:
            return None
        x = float(v)
        return None if x != x else x
    except (TypeError, ValueError):
        return None


def load_context(path: str | Path = DEFAULT_CONTEXT_PATH) -> dict[int, dict[str, Any]]:
    """Latest entry record per trade_id. Missing file -> {}. Malformed lines skipped."""
    p = Path(path)
    if not p.exists():
        return {}
    out: dict[int, dict[str, Any]] = {}
    with p.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            tid = rec.get("trade_id")
            if not isinstance(tid, int):
                continue
            if rec.get("event_type") not in (None, "trade_entry_recorded", "trade_recorded"):
                continue
            out[tid] = rec           # later lines win
    return out


def features_from_record(rec: dict[str, Any]) -> dict[str, str | None]:
    """All FEATURE_FIELDS buckets for one context record (None where undefined)."""
    body = _f(rec.get("candle_body_strength"))
    atr_exp = _f(rec.get("atr_expansion"))
    if atr_exp is None:
        a, avg = _f(rec.get("atr_at_entry")), _f(rec.get("atr_avg_at_entry"))
        atr_exp = (a / avg) if (a is not None and avg) else None
    vol = _f(rec.get("volume_ratio"))
    pos = _f(rec.get("range_position"))
    e20 = _f(rec.get("ema20_dist_atr"))
    if e20 is None:
        px, ema20, atr = _f(rec.get("entry_price")), _f(rec.get("ema20_at_entry")), _f(rec.get("atr_at_entry"))
        e20 = ((px - ema20) / atr) if (px is not None and ema20 is not None and atr) else None
    e200 = _f(rec.get("ema200_dist_atr"))
    if e200 is None:
        px, ema200 = _f(rec.get("entry_price")), _f(rec.get("ema200_at_entry"))
        e200 = (px - ema200) if (px is not None and ema200 is not None) else None
    return {
        "body_bucket": None if body is None else _edges(body, BODY_EDGES, "full"),
        "atr_expansion_bucket": None if atr_exp is None else _edges(atr_exp, ATR_EXP_EDGES, "expanding"),
        "volume_bucket": None if vol is None else _edges(vol, VOLUME_EDGES, "high"),
        "range_pos_bucket": None if pos is None else ("bottom" if pos <= 0.15 else ("top" if pos >= 0.85 else "mid")),
        "ema20_dist_bucket": None if e20 is None else _edges(e20, EMA20_EDGES, "far_above"),
        "ema200_side": None if e200 is None else ("above" if e200 > 0 else "below"),
    }


@lru_cache(maxsize=4)
def _cached_features(path: str) -> dict[int, dict[str, str | None]]:
    return {tid: features_from_record(rec) for tid, rec in load_context(path).items()}


def trade_bucket(trade: dict[str, Any], field: str,
                 path: str | Path = DEFAULT_CONTEXT_PATH) -> str | None:
    """Bucket label of `field` for a journal trade row (needs trade['id']), or None."""
    if field not in FEATURE_FIELDS:
        return None
    tid = trade.get("id")
    if not isinstance(tid, int):
        try:
            tid = int(tid)
        except (TypeError, ValueError):
            return None
    return _cached_features(str(path)).get(tid, {}).get(field)


def clear_cache() -> None:
    _cached_features.cache_clear()


def coverage(trades: list[dict[str, Any]], path: str | Path = DEFAULT_CONTEXT_PATH) -> dict[str, int]:
    """How many of `trades` have each bucket defined (for the report's honesty line)."""
    out = {f: 0 for f in FEATURE_FIELDS}
    for t in trades:
        for f in FEATURE_FIELDS:
            if trade_bucket(t, f, path) is not None:
                out[f] += 1
    out["trades"] = len(trades)
    return out

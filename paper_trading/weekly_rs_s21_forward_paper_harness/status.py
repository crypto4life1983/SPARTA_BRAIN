"""Read-only STATUS aggregator for the weekly RS s21 broker-free paper process.

PURE READS ONLY. Reads this package's manifest + the newest runs/dry_cycle_NNN/ outputs that the
cycle already wrote. It NEVER fetches data, NEVER runs a cycle, NEVER sends anything, NEVER connects a
broker. Consumed by both the read-only dashboard card and the dry-run Telegram notifier.

DIAGNOSTIC_ONLY -- FRC NEVER_GRANTED -- Live BLOCKED_AT_6_GATES -- Trading PAUSED.
"""

import datetime as _dt
import json as _json
import pathlib as _pathlib
import re as _re

from .manifest import DATA_SOURCES, DEFAULT_DATA_SOURCE, MANIFEST

HARNESS_DIR = _pathlib.Path(__file__).resolve().parent
RUNS_DIR = HARNESS_DIR / "runs"
_CYCLE_RE = _re.compile(r"^dry_cycle_(\d+)$")

GOVERNANCE_BANNER = ["DIAGNOSTIC_ONLY", "FRC NEVER_GRANTED", "Live BLOCKED_AT_6_GATES", "Trading PAUSED"]


def _read_json(path):
    try:
        return _json.loads(_pathlib.Path(path).read_text(encoding="utf-8"))
    except Exception:
        return None


def _read_jsonl_last(path):
    p = _pathlib.Path(path)
    if not p.exists():
        return None
    last = None
    with open(p, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                last = line
    try:
        return _json.loads(last) if last else None
    except Exception:
        return None


def latest_cycle(runs_dir=RUNS_DIR):
    """Return (n, dir) for the highest dry_cycle_NNN that has a paper_orders.jsonl, else (None, None)."""
    rd = _pathlib.Path(runs_dir)
    if not rd.exists():
        return None, None
    best = None
    for d in rd.iterdir():
        if not d.is_dir():
            continue
        m = _CYCLE_RE.match(d.name)
        if m and (d / "paper_orders.jsonl").exists():
            n = int(m.group(1))
            if best is None or n > best[0]:
                best = (n, d)
    return best if best else (None, None)


def _verdict_from_killswitch(ks_result):
    if not ks_result:
        return "UNKNOWN"
    if ks_result.get("halt"):
        return "HALT"
    if ks_result.get("status") in ("WARN", "REVIEW"):
        return "WARN"
    return "CONTINUE"


def active_data_source(data_source=None):
    key = data_source or DEFAULT_DATA_SOURCE
    src = DATA_SOURCES.get(key, {})
    return {"key": key, "dir": src.get("dir"), "last_date": src.get("last_date"),
            "read_only": bool(src.get("read_only", False))}


def next_expected_anchor(last_anchor):
    """Indicator only: ~5 trading days ~= 7 calendar days after the last traded anchor. The harness
    re-confirms the true rebalance bar at cycle time; this is a display hint, not a trading decision."""
    if not last_anchor:
        return None
    try:
        return (_dt.date.fromisoformat(last_anchor) + _dt.timedelta(days=7)).isoformat()
    except Exception:
        return None


def readiness(last_anchor, source_last_date):
    """READY iff the active data source has a bar strictly newer than the last traded anchor; else STALE.
    Pure ISO-date string compare (read-only). Final rebalance-bar validity is re-checked at cycle time by
    cycle.py (StaleDataError). This is an indicator, never a trigger."""
    if not last_anchor:
        if source_last_date:
            return "READY", "no prior cycle; data available (last bar %s)" % source_last_date
        return "STALE", "no prior cycle and no data source last_date"
    if source_last_date and source_last_date > last_anchor:
        return "READY", "data last bar %s is newer than last anchor %s" % (source_last_date, last_anchor)
    return "STALE", "no bar newer than last anchor %s (source last %s)" % (last_anchor, source_last_date)


def paper_status(data_source=None, runs_dir=RUNS_DIR):
    """One read-only dict with every card/notifier field. No fetch, no cycle, no send, no broker."""
    n, d = latest_cycle(runs_dir)
    order = _read_jsonl_last(d / "paper_orders.jsonl") if d else None
    ks = _read_json(d / "killswitch_status.json") if d else None
    ks_result = (ks or {}).get("result") if ks else None
    order = order or {}
    last_anchor = order.get("signal_date")
    holdings = sorted((order.get("holdings_after") or {}).keys()) or list(order.get("selected_top8") or [])
    src = active_data_source(data_source)
    ready, ready_reason = readiness(last_anchor, src["last_date"])
    st = MANIFEST["status"]
    pb = MANIFEST["permanent_blocks"]
    return {
        "generated_at_utc": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "harness_id": MANIFEST["harness_id"],
        "paper_state": st["paper_state"],
        "trading_status": st["trading_status"],
        "live_status": st["live_status"],
        "frc_status": st["frc_status"],
        "research_label": st["research_label"],
        "last_cycle_number": n,
        "last_anchor_date": last_anchor,
        "next_expected_anchor": next_expected_anchor(last_anchor),
        "latest_equity_usd": order.get("equity_after"),
        "current_holdings": list(holdings),
        "last_cycle_verdict": _verdict_from_killswitch(ks_result),
        "killswitch_status": (ks_result or {}).get("status", "UNKNOWN"),
        "killswitch_reasons": list((ks_result or {}).get("reasons", [])),
        "killswitch_halt": bool((ks_result or {}).get("halt", False)),
        "data_source": src,
        "next_cycle": ready,
        "next_cycle_reason": ready_reason,
        "governance_banner": GOVERNANCE_BANNER,
        "runs_dir_exists": _pathlib.Path(runs_dir).exists(),
        "no_broker": bool(pb["no_broker_connection"]),
        "no_live_trading": bool(pb["no_live_trading"]),
        "no_fetch": bool(pb["no_network_or_data_fetch_by_harness"]),
    }

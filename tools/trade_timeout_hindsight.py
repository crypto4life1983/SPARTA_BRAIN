"""Hindsight for TIMEOUT closes: what would holding longer have done?

The paper bot closes a position once days_held (run date - open_date) reaches
20 when neither stop nor target has been hit. An ``extend_timeout__<H>``
hypothesis in the ledger asks whether holding to H days would have been better.
This module answers that per trade with daily bars fetched read-only from the
Binance public klines endpoint (the source scripts/resolve_ledger_outcomes.py
in the bot already uses) and caches the rows in data/timeout_hindsight.jsonl so
a resolved trade is never fetched twice. Observation only: it never writes to
the bot repo, never touches trades.db, has no order path.

Conventions (mirroring scripts/trade_bot.py; a documented approximation):
- bar day = run date - 1. The close_date run saw bars through close_date - 1,
  so the extension window is the daily bars from day close_date through day
  open_date + H - 1: exactly H - days_held bars.
- per bar, pessimistic order: stop first (long: low <= sl; short: high >= sl),
  then target (long: high >= tp1; short: low <= tp1), else carry. At the end of
  the window exit at that bar's close. A single full exit at tp1 or stop:
  partial take-profits and breakeven trails are NOT simulated, so the target
  case is overstated for F/F2 (three targets) and understated for D/E (half
  off at 2R). The ledger module's docstring carries the same caveat.
- R = (gross - fees) / size_usd with the bot's per-side fee table; risk unit
  |entry - sl|, or 2 * atr14 when the stored stop already sits at breakeven.
- the actual exit is the bot's own pnl_r; the simulated one uses Binance bars
  even for kraken rows (same symbol string). Small basis differences are noise
  next to the question being asked.

Run:  .venv\\Scripts\\python tools\\trade_timeout_hindsight.py [--horizon 40] [--dry-run]
"""
from __future__ import annotations

import json
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from tools.trade_journal_adapter import _coerce_float, _parse_dt  # noqa: E402  (reuse, never modify)

HINDSIGHT_PATH = _REPO_ROOT / "data" / "timeout_hindsight.jsonl"
BINANCE_URL = "https://api.binance.com/api/v3/klines"
SOURCE = "binance_api_v3_klines_1d"
BOT_TIMEOUT_DAYS = 20            # mirrors trade_bot.py timeout_days default
FEES: dict[str, float] = {       # mirrors trade_bot.FEES, per side
    "binance": 0.001,
    "kraken": 0.0026,
}
DEFAULT_FEE = 0.001
MAX_FETCHES_PER_RUN = 40         # public endpoint courtesy cap; the rest wait for the next run
EXIT_STOP, EXIT_TARGET, EXIT_HORIZON = "STOP", "TARGET", "HORIZON"

FetchFn = Callable[[str, date, int], list[dict[str, Any]]]


# ── bars ─────────────────────────────────────────────────────────────────────

def _day_ms(d: date) -> int:
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)


def fetch_daily_bars(symbol: str, start_day: date, limit: int) -> list[dict[str, Any]]:
    """Daily bars from start_day (UTC) on, oldest first. Network, read-only."""
    url = f"{BINANCE_URL}?symbol={symbol}&interval=1d&startTime={_day_ms(start_day)}&limit={int(limit)}"
    req = urllib.request.Request(url, headers={"User-Agent": "sparta-brain/timeout-hindsight"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        rows = json.loads(resp.read())
    return [{"day": datetime.fromtimestamp(int(r[0]) / 1000, tz=timezone.utc).strftime("%Y-%m-%d"),
             "open": float(r[1]), "high": float(r[2]), "low": float(r[3]), "close": float(r[4])}
            for r in rows]


# ── per-trade arithmetic (pure) ───────────────────────────────────────────────

def _day(v: Any) -> date | None:
    dt = _parse_dt(v)
    return None if dt is None else dt.date()


def risk_unit(trade: dict[str, Any]) -> float | None:
    """|entry - sl|; 2*atr14 when the stop sits at breakeven (after a partial)."""
    entry, sl = _coerce_float(trade.get("entry")), _coerce_float(trade.get("sl"))
    if entry is None or sl is None:
        return None
    d = abs(entry - sl)
    if d > 0:
        return d
    atr = _coerce_float(trade.get("atr14"))
    return 2.0 * atr if atr and atr > 0 else None


def pnl_r(trade: dict[str, Any], exit_price: float) -> float | None:
    """The bot's calc_pnl R for a full exit at exit_price (fees both sides)."""
    unit = risk_unit(trade)
    entry, size = _coerce_float(trade.get("entry")), _coerce_float(trade.get("size_usd"))
    if unit is None or entry is None or not size or size <= 0:
        return None
    units = size / unit
    sign = 1.0 if str(trade.get("direction") or "").lower() == "long" else -1.0
    gross = units * (exit_price - entry) * sign
    fee = FEES.get(str(trade.get("exchange") or "").lower(), DEFAULT_FEE)
    fees = units * fee * (entry + exit_price)
    return round((gross - fees) / size, 4)


def extension_window(trade: dict[str, Any], horizon_days: int) -> tuple[date, int] | None:
    """(first bar day, number of bars) a hold to horizon_days would have added."""
    od, cd = _day(trade.get("open_date")), _day(trade.get("close_date"))
    if od is None or cd is None:
        return None
    n = int(horizon_days) - (cd - od).days
    return (cd, n) if n > 0 else None


def is_candidate(trade: dict[str, Any]) -> bool:
    return (str(trade.get("outcome") or "").upper() == "TIMEOUT"
            and _coerce_float(trade.get("pnl_r")) is not None
            and risk_unit(trade) is not None
            and _coerce_float(trade.get("tp1")) is not None
            and _day(trade.get("open_date")) is not None
            and _day(trade.get("close_date")) is not None)


def simulate_extension(trade: dict[str, Any], bars: list[dict[str, Any]],
                       horizon_days: int) -> dict[str, Any]:
    """Walk the extension window bar by bar. Pure. Unresolved when the window
    is not complete yet and nothing was hit."""
    win = extension_window(trade, horizon_days)
    out: dict[str, Any] = {"resolved": False, "exit_reason": None, "exit_price": None,
                           "exit_day": None, "bars_needed": 0, "bars_used": 0}
    if win is None:
        return out
    start, n = win
    out["bars_needed"] = n
    window = sorted((b for b in bars if _day(b.get("day")) is not None and _day(b["day"]) >= start),
                    key=lambda b: b["day"])[:n]
    out["bars_used"] = len(window)
    sl, tp = float(trade["sl"]), float(trade["tp1"])
    long = str(trade.get("direction") or "").lower() == "long"
    for b in window:
        hi, lo = float(b["high"]), float(b["low"])
        if (lo <= sl) if long else (hi >= sl):
            out.update(resolved=True, exit_reason=EXIT_STOP, exit_price=sl, exit_day=b["day"])
            return out
        if (hi >= tp) if long else (lo <= tp):
            out.update(resolved=True, exit_reason=EXIT_TARGET, exit_price=tp, exit_day=b["day"])
            return out
    if len(window) >= n:
        last = window[-1]
        out.update(resolved=True, exit_reason=EXIT_HORIZON, exit_price=float(last["close"]),
                   exit_day=last["day"])
    return out


def hindsight_row(trade: dict[str, Any], bars: list[dict[str, Any]], horizon_days: int,
                  as_of: str, error: str | None = None) -> dict[str, Any]:
    sim = simulate_extension(trade, bars, horizon_days) if error is None else {
        "resolved": False, "exit_reason": None, "exit_price": None, "exit_day": None,
        "bars_needed": (extension_window(trade, horizon_days) or (None, 0))[1], "bars_used": 0}
    actual = _coerce_float(trade.get("pnl_r"))
    sim_r = pnl_r(trade, float(sim["exit_price"])) if sim["resolved"] else None
    return {
        "trade_id": int(trade["id"]), "horizon_days": int(horizon_days),
        "symbol": trade.get("symbol"), "exchange": trade.get("exchange"),
        "strategy": trade.get("strategy"), "direction": trade.get("direction"),
        "open_date": trade.get("open_date"), "close_date": trade.get("close_date"),
        "actual_pnl_r": actual, "resolved": bool(sim["resolved"]),
        "exit_reason": sim["exit_reason"], "exit_price": sim["exit_price"], "exit_day": sim["exit_day"],
        "bars_needed": sim["bars_needed"], "bars_used": sim["bars_used"],
        "sim_pnl_r": sim_r,
        "delta_R": (round(sim_r - actual, 4) if sim_r is not None and actual is not None else None),
        "resolved_as_of": as_of if sim["resolved"] else None,
        "last_checked_as_of": as_of, "source": SOURCE, "error": error,
    }


# ── cache ────────────────────────────────────────────────────────────────────

def load_hindsight(path: Path | None = None) -> list[dict[str, Any]]:
    p = Path(path) if path is not None else HINDSIGHT_PATH
    if not p.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict) and "trade_id" in obj and "horizon_days" in obj:
            rows.append(obj)
    return rows


def hindsight_key(row: dict[str, Any]) -> tuple[int, int]:
    return int(row["trade_id"]), int(row["horizon_days"])


def index_hindsight(rows: list[dict[str, Any]]) -> dict[tuple[int, int], dict[str, Any]]:
    """Last row per (trade_id, horizon) wins."""
    out: dict[tuple[int, int], dict[str, Any]] = {}
    for r in rows:
        try:
            out[hindsight_key(r)] = r
        except (KeyError, TypeError, ValueError):
            continue
    return out


def save_hindsight(rows: list[dict[str, Any]], path: Path | None = None) -> Path:
    p = Path(path) if path is not None else HINDSIGHT_PATH
    p.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(index_hindsight(rows).values(), key=hindsight_key)
    p.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in ordered), encoding="utf-8")
    return p


def refresh(trades: list[dict[str, Any]], horizons: list[int], as_of: str,
            path: Path | None = None, fetch: FetchFn = fetch_daily_bars,
            today: date | None = None, max_fetches: int = MAX_FETCHES_PER_RUN) -> list[dict[str, Any]]:
    """Resolve every TIMEOUT trade for every horizon that is not resolved yet,
    fetching only when at least one bar of its window can exist. Returns the
    full cache (saved). A fetch error leaves the row unresolved with the error
    text; it is retried next run."""
    rows = load_hindsight(path)
    idx = index_hindsight(rows)
    today = today or datetime.now(timezone.utc).date()
    fetches = 0
    for h in sorted({int(x) for x in horizons}):
        for t in sorted((t for t in trades if is_candidate(t)), key=lambda t: int(t["id"])):
            key = (int(t["id"]), h)
            if idx.get(key, {}).get("resolved"):
                continue
            win = extension_window(t, h)
            if win is None:
                continue
            start, n = win
            if start > today - timedelta(days=1):
                continue  # no completed bar in the window yet
            if fetches >= max_fetches:
                break
            fetches += 1
            try:
                bars = fetch(str(t["symbol"]), start, n + 2)
                idx[key] = hindsight_row(t, bars, h, as_of)
            except Exception as exc:  # noqa: BLE001 - never let one symbol stop the run
                idx[key] = hindsight_row(t, [], h, as_of, error=f"{type(exc).__name__}: {exc}")
    out = sorted(idx.values(), key=hindsight_key)
    save_hindsight(out, path)
    return out


def summarize(rows: list[dict[str, Any]], horizon_days: int) -> dict[str, Any]:
    sel = [r for r in index_hindsight(rows).values() if int(r["horizon_days"]) == int(horizon_days)]
    res = [r for r in sel if r.get("resolved") and r.get("delta_R") is not None]
    deltas = [float(r["delta_R"]) for r in res]
    return {
        "horizon_days": int(horizon_days), "n_timeouts": len(sel), "n_resolved": len(res),
        "would_hit_target": sum(1 for r in res if r.get("exit_reason") == EXIT_TARGET),
        "would_hit_stop": sum(1 for r in res if r.get("exit_reason") == EXIT_STOP),
        "still_open_at_horizon": sum(1 for r in res if r.get("exit_reason") == EXIT_HORIZON),
        "sum_delta_R": round(sum(deltas), 4) if deltas else 0.0,
        "mean_delta_R": round(sum(deltas) / len(deltas), 4) if deltas else None,
        "source": SOURCE,
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    from tools.trade_journal_adapter import _REL_TRADES_DB, external_root
    from tools.trade_journal_learning_report import load_journal_ro

    ap = argparse.ArgumentParser(description="Timeout hindsight resolver (observation only)")
    ap.add_argument("--horizon", type=int, nargs="*", default=[40], help="hold horizons in days")
    ap.add_argument("--dry-run", action="store_true", help="resolve into a temp file, print, discard")
    args = ap.parse_args(argv)
    db = external_root().joinpath(*_REL_TRADES_DB)
    if not db.exists():
        print(f"trades.db not found: {db}")
        return 1
    trades, _ = load_journal_ro(db)
    as_of = datetime.now().strftime("%Y-%m-%d")
    path = HINDSIGHT_PATH
    if args.dry_run:
        import tempfile
        path = Path(tempfile.mkdtemp()) / "timeout_hindsight.jsonl"
        if HINDSIGHT_PATH.exists():
            path.write_text(HINDSIGHT_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    rows = refresh(trades, args.horizon, as_of, path=path)
    for h in args.horizon:
        print(json.dumps(summarize(rows, h), sort_keys=True))
    for r in sorted(rows, key=hindsight_key):
        print(f"#{r['trade_id']} {r['symbol']} {r['strategy']} H{r['horizon_days']}: "
              f"{'resolved' if r['resolved'] else 'pending'} {r['exit_reason'] or '-'} "
              f"actual {r['actual_pnl_r']} sim {r['sim_pnl_r']} delta {r['delta_R']}"
              + (f" error={r['error']}" if r.get("error") else ""))
    print(f"{'dry run, discarded' if args.dry_run else 'wrote'} {path}")
    return 0


__all__ = [
    "HINDSIGHT_PATH", "BOT_TIMEOUT_DAYS", "SOURCE", "EXIT_STOP", "EXIT_TARGET", "EXIT_HORIZON",
    "fetch_daily_bars", "risk_unit", "pnl_r", "extension_window", "is_candidate",
    "simulate_extension", "hindsight_row", "load_hindsight", "index_hindsight", "save_hindsight",
    "refresh", "summarize",
]

if __name__ == "__main__":
    sys.exit(main())

"""Weekly paper-cycle orchestrator. BROKER-FREE, NETWORK-FREE: reads operator-provided LOCAL split_only CSVs only.
GATED: refuses to run unless operator_authorized_dry_run=True (a SEPARATE explicit authorization). BUILD never sets it."""

import csv as _csv
import pathlib as _pathlib

from . import safety
from .manifest import MANIFEST
from .signal import trailing_return, cross_sectional_rank, select_top_m
from .portfolio import build_paper_orders, rotation_exits
from .paper_book import PaperBook, DrawdownTracker
from .paper_logging import append_order_record, append_closed_trade
from .report import build_weekly_report


class CycleNotAuthorized(RuntimeError):
    pass


def _load_local_closes(local_csv_dir):
    """Read LOCAL CSVs (date,open,high,low,close,volume) for the locked 48 universe. NO network, NO fetch, NO keys."""
    base = _pathlib.Path(local_csv_dir)
    closes = {}; cal = None
    for sym in MANIFEST["universe_48"]:
        fp = base / ("%s_ohlcv_1d_20190102_20251230.csv" % sym)
        if not fp.exists():
            raise FileNotFoundError("missing LOCAL csv for %s at %s (operator must supply split_only CSVs; harness does NOT fetch)" % (sym, fp))
        rows = []
        with open(fp, "r", encoding="utf-8") as f:
            for r in _csv.DictReader(f):
                rows.append((r["date"], float(r["close"])))
        rows.sort(key=lambda x: x[0]); ds = [d for d, _ in rows]; closes[sym] = [c for _, c in rows]
        if cal is None:
            cal = ds
        if ds != cal:
            raise ValueError("CALENDAR_MISALIGNMENT for %s (NO-TRADE / kill-switch)" % sym)
    return closes, cal


def run_weekly_paper_cycle(local_csv_dir, asof_index, book=None, operator_authorized_dry_run=False, live_mode=False, broker=None):
    """Run ONE weekly paper rebalance against LOCAL data. Requires explicit operator authorization; refuses otherwise.
    This is provided so a future SEPARATE authorization can run a broker-free dry cycle; BUILD does NOT call it."""
    safety.assert_safe_environment(live_mode=live_mode, broker=broker)
    if not operator_authorized_dry_run:
        raise CycleNotAuthorized(
            "PAPER_CYCLE_NOT_AUTHORIZED: a broker-free dry paper cycle requires a SEPARATE explicit operator "
            "authorization (set operator_authorized_dry_run=True). BUILD scope does not authorize running."
        )
    closes, cal = _load_local_closes(local_csv_dir)
    book = book or PaperBook(MANIFEST["locked_mechanic"]["start_cash_usd"])
    L = MANIFEST["locked_mechanic"]["momentum_lookback_L"]; S = MANIFEST["locked_mechanic"]["momentum_skip_S"]
    M = MANIFEST["locked_mechanic"]["top_m_held"]
    cm = MANIFEST["cost_model_S1"]
    sigs = {s: trailing_return(closes[s], asof_index, L, S) for s in MANIFEST["universe_48"]}
    selected = select_top_m(cross_sectional_rank(sigs), M)
    prices = {s: closes[s][asof_index] for s in MANIFEST["universe_48"]}
    equity = book.equity(prices)
    orders = build_paper_orders(book.holdings, selected, prices, equity, m=M,
                                per_share=cm["commission_per_share_usd"], min_comm=cm["min_commission_per_trade_usd"], slip_bps=cm["slippage_proxy_bps"])
    return {"selected": selected, "orders": orders, "equity_before": equity, "signal_date": cal[asof_index]}

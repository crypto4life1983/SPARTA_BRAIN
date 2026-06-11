"""Tests for the SPARTA Arbitrage Factory V1 Scanner (READ-ONLY, ALERTS ONLY).

The scanner reads only staged CSVs, charges the seq-3 model in full, classifies
via the seq-4 schema, and refuses-by-default. Blocked runs write nothing. No
network, no credentials, no orders, no scheduler, no gate movement."""

from __future__ import annotations

import ast
import datetime as dt
from pathlib import Path

import sparta_commander.arbitrage_scanner as sc
import sparta_commander.arbitrage_alert_report_schema_contract as rs

_NOW = dt.datetime.now(dt.timezone.utc)
_TS = _NOW.strftime("%Y-%m-%dT%H:%M:%SZ")


def _stage(tmp_path: Path, skip=(), funding_rate="0.00020000",
           extra_fee_col=None) -> Path:
    staged = tmp_path / "data/arbitrage_factory_v1/staged"
    staged.mkdir(parents=True)
    fee_header = "venue,symbol,taker_fee_pct,maker_fee_pct,withdrawal_flat_fee"
    if extra_fee_col:
        fee_header += "," + extra_fee_col
    files = {
        "funding_BTC_binance.csv":
            "timestamp_utc,symbol,venue,funding_rate_8h,mark_price\n"
            f"{_TS},BTC,binance,{funding_rate},65000.00\n",
        "basis_ETH_bybit.csv":
            "timestamp_utc,symbol,venue,spot_price,perp_price,basis_pct\n"
            f"{_TS},ETH,bybit,1650.00,1651.65,0.1000\n",
        "quotes_SOL_okx.csv":
            "timestamp_utc,symbol,venue,bid,ask,mid\n"
            f"{_TS},SOL,okx,65.00,65.02,65.01\n",
        "fees_kraken.csv":
            fee_header + "\nkraken,BTC,0.0040,0.0025,0.0002\n"
            "kraken,ETH,0.0040,0.0025,0.0035\n",
        "depth_BTC_coinbase.csv":
            "timestamp_utc,symbol,venue,bid_depth_usd_10bps,ask_depth_usd_10bps,spread_bps\n"
            f"{_TS},BTC,coinbase,900000.00,950000.00,1.20\n",
    }
    for name, content in files.items():
        if name in skip:
            continue
        (staged / name).write_text(
            content + ("," * 0), encoding="utf-8") if extra_fee_col is None or not name.startswith("fees") else None
        if extra_fee_col and name.startswith("fees"):
            rows = content.splitlines()
            fixed = [rows[0]] + [r + ",x" for r in rows[1:]]
            (staged / name).write_text("\n".join(fixed) + "\n", encoding="utf-8")
        elif name not in skip:
            (staged / name).write_text(content, encoding="utf-8")
    return tmp_path


def test_complete_staged_data_scan_completes(tmp_path):
    r = sc.run_arbitrage_scan(_stage(tmp_path))
    assert r["verdict"] == sc.VERDICT_SCAN_COMPLETED
    assert r["blockers"] == []
    assert len(r["alerts"]) == 2
    assert r["report_written"] is False  # write=False default


def test_every_alert_passes_the_seq4_schema_and_is_fee_honest(tmp_path):
    r = sc.run_arbitrage_scan(_stage(tmp_path))
    for a in r["alerts"]:
        assert rs.validate_alert_record(a)["acceptable"] is True
        assert a["verdict"] in ("PASS", "WATCH", "FAIL")
        assert a["disclaimer"] == rs.MANDATORY_DISCLAIMER
        assert a["alert_is_research_only_not_a_trade_signal"] is True
        # full cost stack present and charged
        expected = (a["gross_edge_bps"] - 2 * a["taker_fee_bps"]
                    - a["spread_cost_bps"] - a["slippage_bps"]
                    - a["funding_adjustment_bps"]
                    - a["withdrawal_amortization_bps"])
        assert abs(expected - a["net_edge_bps"]) < 1e-9


def test_small_edges_fail_after_fees(tmp_path):
    # 2 bps funding vs 80 bps round-trip taker: honesty means FAIL
    r = sc.run_arbitrage_scan(_stage(tmp_path))
    funding = [a for a in r["alerts"] if "funding" in a["alert_id"]][0]
    assert funding["net_edge_bps"] < 0
    assert funding["verdict"] == "FAIL"


def test_no_trade_instruction_language_anywhere(tmp_path):
    r = sc.run_arbitrage_scan(_stage(tmp_path))
    text = str(r).lower()
    for banned in ("buy now", "sell now", "go long", "go short", "place order",
                   "execute trade", "guaranteed", "proven winning"):
        assert banned not in text, banned


def test_missing_kind_refuses_and_writes_nothing(tmp_path):
    root = _stage(tmp_path, skip=("depth_BTC_coinbase.csv",))
    r = sc.run_arbitrage_scan(root, write=True)
    assert r["verdict"] == sc.VERDICT_SCAN_REFUSED
    assert any("missing_kinds" in b for b in r["blockers"])
    assert r["report_written"] is False
    assert not (root / "reports/arbitrage_factory_v1").exists()


def test_unsafe_fee_column_refuses(tmp_path):
    root = _stage(tmp_path, extra_fee_col="account_balance")
    r = sc.run_arbitrage_scan(root, write=True)
    assert r["verdict"] == sc.VERDICT_SCAN_REFUSED
    assert any("manifest_refused" in b for b in r["blockers"])
    assert r["report_written"] is False


def test_stale_unacknowledged_data_refuses(tmp_path):
    root = tmp_path
    _stage(root)
    staged = root / "data/arbitrage_factory_v1/staged"
    old = (_NOW - dt.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    (staged / "funding_BTC_binance.csv").write_text(
        "timestamp_utc,symbol,venue,funding_rate_8h,mark_price\n"
        f"{old},BTC,binance,0.0001,65000.00\n", encoding="utf-8")
    r = sc.run_arbitrage_scan(root)
    assert r["verdict"] == sc.VERDICT_SCAN_REFUSED
    assert any("stale" in b for b in r["blockers"])


def test_missing_staged_folder_refuses(tmp_path):
    r = sc.run_arbitrage_scan(tmp_path)
    assert r["verdict"] == sc.VERDICT_SCAN_REFUSED
    assert "staged_folder_missing" in r["blockers"]


def test_write_true_produces_one_report_pair_never_overwrites(tmp_path):
    root = _stage(tmp_path)
    r = sc.run_arbitrage_scan(root, write=True)
    assert r["verdict"] == sc.VERDICT_SCAN_COMPLETED
    assert r["report_written"] is True
    assert len(r["report_paths"]) == 2
    md = Path(r["report_paths"][1]).read_text(encoding="utf-8")
    assert rs.MANDATORY_DISCLAIMER in md
    assert "ALERTS ONLY" in md


def test_gates_and_capabilities_inert_on_all_paths(tmp_path):
    for r in (sc.run_arbitrage_scan(_stage(tmp_path)),
              sc.run_arbitrage_scan(tmp_path / "nope")):
        for key in ("executes", "contains_order_logic", "uses_network",
                    "uses_credentials", "starts_scheduler", "promotes_gate",
                    "unlocks_downstream_gate"):
            assert r[key] is False, key
        assert r["paper_trading_gate_locked"] is True
        assert r["micro_live_gate_locked"] is True
        assert r["live_gate_locked"] is True
        assert r["alerts_are_research_only_not_trade_signals"] is True
        assert r["next_required_action"] == "HUMAN_REVIEW_OF_SCAN_REPORT"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in sc.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_scheduler_or_credential_modules():
    with open(sc.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento",
              "dotenv", "smtplib", "subprocess", "websocket", "websockets",
              "aiohttp", "schedule", "apscheduler", "threading",
              "multiprocessing", "asyncio", "sched", "time", "telegram", "email"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)

"""Safety tests for the forward-only Deribit BTC option-chain snapshot collector.

Proves: network surface restricted to the two approved public endpoints (get_instruments,
get_book_summary_by_currency); forbidden fragments (private/account/order/buy/sell/signature/
api_key) rejected; BTC only; writes only under data/deribit_options_chain_universe/; computes
NO greeks/PnL and runs NO backtest; joins instrument metadata with book-summary marks
deterministically. Uses an injected fake http_get -- NO real network."""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

import tools.fetch_deribit_btc_option_chain_snapshot_once as fx


def test_exact_public_endpoints():
    assert fx.INSTRUMENTS_ENDPOINT == "https://www.deribit.com/api/v2/public/get_instruments"
    assert fx.BOOK_SUMMARY_ENDPOINT == (
        "https://www.deribit.com/api/v2/public/get_book_summary_by_currency")
    assert fx.ALLOWED_URL_PREFIXES == (fx.INSTRUMENTS_ENDPOINT, fx.BOOK_SUMMARY_ENDPOINT)
    for e in fx.ALLOWED_URL_PREFIXES:
        assert "/public/" in e and "/private/" not in e
    fx._assert_safe_url(fx.INSTRUMENTS_ENDPOINT + "?currency=BTC&kind=option&expired=false")
    fx._assert_safe_url(fx.BOOK_SUMMARY_ENDPOINT + "?currency=BTC&kind=option")


def test_rejects_private_trading_urls():
    for bad in ("https://www.deribit.com/api/v2/private/buy",
                "https://www.deribit.com/api/v2/private/get_account_summary",
                "https://www.deribit.com/api/v2/public/get_order_book",
                "https://evil.example.com/api/v2/public/get_instruments"):
        with pytest.raises(fx.ChainSnapshotError):
            fx._assert_safe_url(bad)


def test_btc_only():
    assert fx.ALLOWED_CURRENCY == "BTC"


def _fake(calls):
    def g(url):
        calls.append(url)
        if "get_instruments" in url:
            return {"result": [
                {"instrument_name": "BTC-27JUN26-100000-C", "strike": 100000.0,
                 "option_type": "call", "expiration_timestamp": 1782547200000},
                {"instrument_name": "BTC-27JUN26-100000-P", "strike": 100000.0,
                 "option_type": "put", "expiration_timestamp": 1782547200000}]}
        return {"result": [
            {"instrument_name": "BTC-27JUN26-100000-C", "mark_iv": 45.0, "mark_price": 0.05,
             "underlying_price": 101000.0, "open_interest": 120.0, "volume": 5.0},
            {"instrument_name": "BTC-27JUN26-100000-P", "mark_iv": 47.0, "mark_price": 0.04,
             "underlying_price": 101000.0, "open_interest": 90.0, "volume": 3.0}]}
    return g


def test_snapshot_joins_metadata_and_marks():
    calls = []
    rows = fx.build_snapshot_rows(http_get=_fake(calls))
    assert len(rows) == 2
    r = rows[0]
    assert {"instrument_name", "strike", "option_type", "expiration_timestamp", "mark_iv",
            "mark_price", "underlying_index_price", "open_interest", "volume"} <= set(r)
    assert r["mark_iv"] in (45.0, 47.0)
    # only the two allowlisted endpoints were hit
    assert all(("get_instruments" in c or "get_book_summary_by_currency" in c) for c in calls)


def test_write_snapshot_under_dir_and_no_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr(fx, "REPO_ROOT", tmp_path)
    rows = fx.build_snapshot_rows(http_get=_fake([]))
    rec = fx.write_snapshot(rows, "2026-06-23")
    assert rec["rows"] == 2 and len(rec["sha256"]) == 64
    assert "deribit_options_chain_universe/snapshots/2026-06-23" in rec["path"]
    with pytest.raises(fx.ChainSnapshotError):       # immutability: no silent overwrite
        fx.write_snapshot(rows, "2026-06-23")


def test_no_secret_trading_or_backtest_surface():
    src = Path(fx.__file__).read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(src)) or ""
    code = re.sub(r"FORBIDDEN_URL_FRAGMENTS\s*=\s*\([^)]*\)", "", src.replace(doc, "")).lower()
    for bad in ("api_key", "hmac", ".sign(", "/private/", "place_order", "create_order",
                "ccxt", "import keyring", "os.environ", "getenv", "straddle_pnl",
                "delta_hedge(", "sharpe_ratio", "black_scholes"):
        assert bad not in code, bad
    tree = ast.parse(src)
    banned = {"ccxt", "deribit", "telegram", "keyring", "requests", "numpy", "pandas", "scipy"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported
    assert "urllib" in imported


def test_output_subdir_constant():
    assert fx.OUTPUT_SUBDIR == "data/deribit_options_chain_universe"

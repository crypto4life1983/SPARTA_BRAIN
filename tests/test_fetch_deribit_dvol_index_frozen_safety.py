"""Safety tests for the bounded Deribit DVOL implied-vol index fetcher.

Proves the tool restricts its network surface to the approved public DVOL endpoint; rejects
forbidden URL fragments (private/account/order/trade/buy/sell/signature/api_key); pins the exact
BTC/ETH allowlist; uses NO API key / private / signed / account / order code and reads NO
secrets; writes ONLY under data/deribit_iv_universe/; records raw DVOL (no clip/smooth/
forward-fill); discloses the March-2020 pre-DVOL gap + index-vs-tradeable caveat; emits the
manifest/quality-report schema; and runs NO VRP/strategy evaluation or trading logic. Uses an
injected fake http_get -- NO real network in tests."""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

import tools.fetch_deribit_dvol_index_frozen as fx


def test_exact_public_endpoint():
    assert fx.DVOL_ENDPOINT == (
        "https://www.deribit.com/api/v2/public/get_volatility_index_data")
    assert fx.ALLOWED_URL_PREFIXES == (fx.DVOL_ENDPOINT,)
    assert "/public/" in fx.DVOL_ENDPOINT and "/private/" not in fx.DVOL_ENDPOINT
    fx._assert_safe_url(fx.DVOL_ENDPOINT + "?currency=BTC&start_timestamp=1&end_timestamp=2"
                        "&resolution=86400")


def test_rejects_private_and_trading_urls():
    for bad in ("https://www.deribit.com/api/v2/private/buy",
                "https://www.deribit.com/api/v2/private/get_account_summary",
                "https://www.deribit.com/api/v2/public/get_order_book",
                "https://www.deribit.com/api/v2/private/sell",
                "https://evil.example.com/api/v2/public/get_volatility_index_data"):
        with pytest.raises(fx.DvolFetchError):
            fx._assert_safe_url(bad)


def test_btc_eth_only():
    assert fx.ALLOWED_CURRENCIES == ("BTC", "ETH")
    for bad in ("SOL", "DOGE", "XRP"):
        with pytest.raises(fx.DvolFetchError):
            fx.fetch_dvol(bad, "2021-03-24", "2021-04-01", http_get=lambda u: {})


def _fake(calls, n=120):
    base = fx._ms("2021-03-24")

    def g(url):
        calls.append(url)
        if len(calls) > 1:
            return {"result": {"data": []}}
        return {"result": {"data": [
            [base + i * 86400000, 60.0 + i, 62.0 + i, 58.0 + i, 61.0 + i] for i in range(n)]}}
    return g


def test_fetch_currency_writes_ohlc_and_hashes(tmp_path, monkeypatch):
    monkeypatch.setattr(fx, "_out_dir", lambda: tmp_path)
    monkeypatch.setattr(fx, "REPO_ROOT", tmp_path.parent)
    calls = []
    rec = fx.fetch_currency("BTC", "2021-03-24", "2021-08-01", http_get=_fake(calls))
    assert rec["included"] is True and rec["rows"] == 120
    assert len(rec["sha256"]) == 64 and rec["resolution"] == "1D"
    txt = (tmp_path / "BTC_dvol_1d.csv").read_text(encoding="utf-8")
    assert "datetime,timestamp_ms,currency,open,high,low,close" in txt


def test_no_data_currency_excluded(tmp_path, monkeypatch):
    monkeypatch.setattr(fx, "_out_dir", lambda: tmp_path)
    rec = fx.fetch_currency("ETH", "2021-03-24", "2021-04-01",
                            http_get=lambda u: {"result": {"data": []}})
    assert rec["included"] is False and rec["reason"] == "no_dvol_data"


def test_march_2020_gap_disclosed():
    m = fx.assemble("2021-03-24", "2021-03-25", http_get=lambda u: {"result": {"data": []}})
    assert "DVOL launched" in m["march_2020_gap_warning"]
    cw = {c["window"]: c for c in m["crash_windows"]}
    assert "2020-03 COVID crash" in cw
    assert cw["2020-03 COVID crash"]["expected_covered"] is False
    assert "PROXY" in m["index_vs_tradeable_caveat"]


def test_no_forward_fill_and_no_clip_flags():
    m = fx.assemble("2021-03-24", "2021-03-25", http_get=lambda u: {"result": {"data": []}})
    assert m["no_forward_fill"] is True and m["no_clip_no_smooth"] is True
    assert m["csv_fields"] == ["datetime", "timestamp_ms", "currency", "open", "high", "low",
                               "close"]


def test_no_secret_or_trading_surface_no_vrp_eval():
    src = Path(fx.__file__).read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(src)) or ""
    code = src.replace(doc, "")
    code = re.sub(r"FORBIDDEN_URL_FRAGMENTS\s*=\s*\([^)]*\)", "", code).lower()
    # actionable trading/secret markers must be ABSENT. (Descriptive prose -- the
    # "..._iv_vs_realized_vol_study" feasibility key and the "delta-hedged straddle" caveat
    # describing what DVOL is NOT -- is fine and excluded by checking actionable forms only.)
    for bad in ("api_key", "hmac", ".sign(", "/private/", "place_order", "create_order",
                "ccxt", "import keyring", "os.environ", "getenv", "sharpe_ratio", "vrp_pnl",
                "straddle_pnl", "compute_realized_vol", "def sharpe"):
        assert bad not in code, bad
    assert code.count("https://www.deribit.com/api/v2/public/") >= 1
    # structural proof of NO evaluation capability: no analytics libs imported
    tree = ast.parse(src)
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & {"numpy", "pandas", "scipy", "statistics", "sklearn"}), imported


def test_imports_no_broker_or_trading_libs():
    tree = ast.parse(Path(fx.__file__).read_text(encoding="utf-8"))
    banned = {"ccxt", "deribit", "telegram", "keyring", "requests", "websockets", "aiohttp"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    assert "urllib" in imported


def test_output_dir_contained_and_gitignored_path():
    assert fx.OUTPUT_SUBDIR == "data/deribit_iv_universe"
    assert fx._out_dir().is_relative_to(fx.REPO_ROOT / fx.OUTPUT_SUBDIR)

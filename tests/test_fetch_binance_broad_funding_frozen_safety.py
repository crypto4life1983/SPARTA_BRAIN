"""Safety tests for the bounded broad USD-M funding fetcher.

Proves the tool restricts its network surface to the allowlisted public funding endpoint;
rejects forbidden URL fragments (account/order/trade/userdata/signed/signature/apikey/secret/
private); pins the exact 40-symbol allowlist; excludes EOSUSDT/MKRUSDT; uses NO API key/signed/
account/order code and reads NO secrets; writes ONLY under data/broad_crypto_funding_universe/;
records raw funding (no clip/smooth/forward-fill); captures funding cadence and detects non-8h
intervals; and does NOT modify/widen the canonical 3-symbol carry fetcher. Uses an injected fake
http_get -- NO real network in tests."""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

import tools.fetch_binance_broad_funding_frozen as fx


def test_allowlist_is_exactly_40_eos_mkr_excluded():
    expected = (
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "TRXUSDT",
        "LINKUSDT", "AVAXUSDT", "DOTUSDT", "LTCUSDT", "BCHUSDT", "UNIUSDT", "ATOMUSDT", "ETCUSDT",
        "XLMUSDT", "ICPUSDT", "AAVEUSDT", "NEARUSDT", "FILUSDT", "ALGOUSDT", "VETUSDT", "XTZUSDT",
        "THETAUSDT", "HBARUSDT", "EGLDUSDT", "ZECUSDT", "MANAUSDT", "SANDUSDT", "CHZUSDT",
        "ENJUSDT", "ZILUSDT", "KAVAUSDT", "RUNEUSDT", "GRTUSDT", "CRVUSDT", "SNXUSDT", "COMPUSDT",
        "YFIUSDT")
    assert fx.ALLOWED_SYMBOLS == expected
    assert len(fx.ALLOWED_SYMBOLS) == 40 and len(set(fx.ALLOWED_SYMBOLS)) == 40
    assert "EOSUSDT" not in fx.ALLOWED_SYMBOLS and "MKRUSDT" not in fx.ALLOWED_SYMBOLS
    assert set(fx.EXCLUDED_SYMBOLS) == {"EOSUSDT", "MKRUSDT"}


def test_exact_endpoint_and_url_guard():
    assert fx.FUNDING_URL == "https://fapi.binance.com/fapi/v1/fundingRate"
    assert fx.ALLOWED_URL_PREFIXES == (fx.FUNDING_URL,)
    fx._assert_safe_url(fx.FUNDING_URL + "?symbol=BTCUSDT&startTime=1&endTime=2&limit=1000")
    for bad in ("https://fapi.binance.com/fapi/v1/order",
                "https://fapi.binance.com/fapi/v1/account",
                "https://fapi.binance.com/fapi/v2/positionRisk?signed=1",
                "https://api.binance.com/sapi/v1/margin/trade",
                "https://evil.example.com/fapi/v1/fundingRate"):
        with pytest.raises(fx.BroadFundingError):
            fx._assert_safe_url(bad)


def test_non_allowlisted_symbol_refused():
    for bad in ("EOSUSDT", "MKRUSDT", "PEPEUSDT"):
        with pytest.raises(fx.BroadFundingError):
            fx.fetch_funding(bad, 1, 2, http_get=lambda u: [])


def _fake(calls, interval_ms=8 * 3600000, n=120):
    base = fx._ms("2021-01-01")

    def g(url):
        calls.append(url)
        if len(calls) > 1:
            return []
        return [{"symbol": "BTCUSDT", "fundingTime": base + i * interval_ms,
                 "fundingRate": "0.0001", "markPrice": "30000"} for i in range(n)]
    return g


def test_fetch_symbol_writes_csv_and_hashes(tmp_path, monkeypatch):
    monkeypatch.setattr(fx, "_out_dir", lambda: tmp_path)
    monkeypatch.setattr(fx, "REPO_ROOT", tmp_path.parent)
    calls = []
    rec = fx.fetch_symbol("BTCUSDT", "2021-01-01", "2021-03-01", http_get=_fake(calls))
    assert rec["included"] is True and rec["rows"] == 120
    assert len(rec["sha256"]) == 64
    assert rec["dominant_interval_h"] == 8.0 and rec["is_non_8h"] is False
    txt = (tmp_path / "BTCUSDT_funding.csv").read_text(encoding="utf-8")
    assert "datetime,funding_time_ms,symbol,funding_rate,mark_price" in txt


def test_detects_non_8h_cadence(tmp_path, monkeypatch):
    monkeypatch.setattr(fx, "_out_dir", lambda: tmp_path)
    monkeypatch.setattr(fx, "REPO_ROOT", tmp_path.parent)
    calls = []
    rec = fx.fetch_symbol("ETHUSDT", "2021-01-01", "2021-02-01",
                          http_get=_fake(calls, interval_ms=4 * 3600000))
    assert rec["is_non_8h"] is True
    assert rec["dominant_interval_h"] == 4.0


def test_no_data_symbol_excluded(tmp_path, monkeypatch):
    monkeypatch.setattr(fx, "_out_dir", lambda: tmp_path)
    rec = fx.fetch_symbol("ADAUSDT", "2021-01-01", "2021-02-01", http_get=lambda u: [])
    assert rec["included"] is False and rec["reason"] == "no_funding_data"


def test_no_secret_or_trading_surface():
    src = Path(fx.__file__).read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(src)) or ""
    code = src.replace(doc, "")
    code = re.sub(r"FORBIDDEN_URL_FRAGMENTS\s*=\s*\([^)]*\)", "", code).lower()
    for bad in ("api_key", "hmac", ".sign(", "&signature=", "place_order", "create_order",
                "ccxt", "import keyring", "os.environ", "getenv", "private_key",
                "/account", "/order", "/positionrisk", "sapi/"):
        assert bad not in code, bad
    assert code.count("https://fapi.binance.com") >= 1


def test_imports_no_broker_or_trading_libs():
    tree = ast.parse(Path(fx.__file__).read_text(encoding="utf-8"))
    banned = {"ccxt", "binance", "telegram", "keyring", "requests", "websockets", "aiohttp"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    assert "urllib" in imported


def test_output_dir_contained_and_gitignored_path():
    assert fx.OUTPUT_SUBDIR == "data/broad_crypto_funding_universe"
    assert fx._out_dir().is_relative_to(fx.REPO_ROOT / fx.OUTPUT_SUBDIR)


def test_old_3_symbol_carry_fetcher_not_modified_or_widened():
    # the canonical carry fetcher must still pin exactly BTC/ETH/SOL and must NOT import the
    # new broad funding tool
    import tools.crypto_basis_funding_public_fetch_once as old
    assert old.ALLOWED_SYMBOLS == ("BTCUSDT", "ETHUSDT", "SOLUSDT")
    old_src = Path(old.__file__).read_text(encoding="utf-8")
    assert "fetch_binance_broad_funding_frozen" not in old_src

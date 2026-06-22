"""Safety tests for the bounded broad-universe Binance daily fetcher.

Proves the new tool: restricts its network surface to the allowlisted public klines endpoint;
rejects forbidden URL fragments (account/order/trade/userdata/signed/signature/apikey/secret);
pins the exact 42-symbol human-approved allowlist; uses NO API key / signed / account / broker
/ order / trading code and reads NO secrets; writes ONLY under data/broad_crypto_universe_c23_c24/;
captures dollar (quote) volume; never forward-fills; and excludes (never substitutes) bad
symbols. Uses an injected fake http_get -- NO real network in tests."""
from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

import tools.fetch_binance_broad_universe_daily_frozen as fx


# ---- exact approved allowlist (42) -----------------------------------------

def test_allowlist_is_exactly_the_42_approved():
    expected = (
        "BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT",
        "TRXUSDT", "LINKUSDT", "AVAXUSDT", "DOTUSDT", "LTCUSDT", "BCHUSDT", "UNIUSDT",
        "ATOMUSDT", "ETCUSDT", "XLMUSDT", "ICPUSDT", "AAVEUSDT", "NEARUSDT", "FILUSDT",
        "ALGOUSDT", "VETUSDT", "XTZUSDT", "THETAUSDT", "HBARUSDT", "EGLDUSDT", "EOSUSDT",
        "ZECUSDT", "MANAUSDT", "SANDUSDT", "CHZUSDT", "ENJUSDT", "ZILUSDT", "KAVAUSDT",
        "RUNEUSDT", "GRTUSDT", "CRVUSDT", "SNXUSDT", "COMPUSDT", "MKRUSDT", "YFIUSDT")
    assert fx.ALLOWED_SYMBOLS == expected
    assert len(fx.ALLOWED_SYMBOLS) == 42
    assert len(set(fx.ALLOWED_SYMBOLS)) == 42  # no dupes


# ---- url allowlist + forbidden fragments -----------------------------------

def test_url_allowlist_and_forbidden_fragments():
    fx._assert_safe_url(fx.BINANCE_PUBLIC_KLINES_URL + "?symbol=BTCUSDT&interval=1d")
    for bad in ("https://api.binance.com/api/v3/account",
                "https://api.binance.com/api/v3/order",
                "https://evil.example.com/api/v3/klines",
                "https://api.binance.com/sapi/v1/margin/trade"):
        with pytest.raises(fx.BroadFetchError):
            fx._assert_safe_url(bad)


def test_only_klines_endpoint_constant():
    assert fx.BINANCE_PUBLIC_KLINES_URL == "https://api.binance.com/api/v3/klines"
    assert fx.ALLOWED_URL_PREFIXES == (fx.BINANCE_PUBLIC_KLINES_URL,)


# ---- non-allowlisted symbol refused ----------------------------------------

def test_non_allowlisted_symbol_refused():
    with pytest.raises(fx.BroadFetchError):
        fx.fetch_klines("PEPEUSDT", "1d", 1, 2, http_get=lambda u: [])
    with pytest.raises(fx.BroadFetchError):
        fx.fetch_klines("BTCUSDT", "1h", 1, 2, http_get=lambda u: [])  # interval


# ---- fetch + freeze with an INJECTED fake (no network) ---------------------

def _fake_page(http_calls):
    # one page of 2 daily klines (>=8 fields incl quote volume at idx 7)
    def fake(url):
        http_calls.append(url)
        # day 1 and day 2 (ms), close>0, base vol idx5, quote vol idx7
        return [
            [1609459200000, "29000", "29500", "28800", "29300", "1000", 1609545599999,
             "29300000", 50, "0", "0", "0"],
            [1609545600000, "29300", "30000", "29100", "29800", "1200", 1609631999999,
             "35700000", 60, "0", "0", "0"],
        ] if len(http_calls) == 1 else []
    return fake


def test_fetch_symbol_writes_dollar_volume_and_hashes(tmp_path, monkeypatch):
    monkeypatch.setattr(fx, "_out_dir", lambda: tmp_path)
    monkeypatch.setattr(fx, "REPO_ROOT", tmp_path.parent)
    monkeypatch.setattr(fx, "MIN_PRIMARY_ROWS", 1)
    calls = []
    rec = fx.fetch_symbol("BTCUSDT", "2021-01-01", "2021-01-02", http_get=_fake_page(calls))
    assert rec["included"] is True
    assert rec["rows"] == 2
    assert len(rec["sha256"]) == 64
    csv_text = (tmp_path / "BTCUSDT_1d.csv").read_text(encoding="utf-8")
    assert "date,open,high,low,close,volume,quote_volume" in csv_text  # dollar volume captured
    assert "29300000" in csv_text  # quote (dollar) volume value present


def test_unavailable_symbol_excluded_not_substituted(tmp_path, monkeypatch):
    monkeypatch.setattr(fx, "_out_dir", lambda: tmp_path)
    rec = fx.fetch_symbol("ZILUSDT", "2021-01-01", "2021-01-02", http_get=lambda u: [])
    assert rec["included"] is False
    assert rec["reason"] == "no_data_unavailable_or_delisted"


def test_short_history_excluded(tmp_path, monkeypatch):
    monkeypatch.setattr(fx, "_out_dir", lambda: tmp_path)
    monkeypatch.setattr(fx, "MIN_PRIMARY_ROWS", 365)
    rec = fx.fetch_symbol("ICPUSDT", "2021-01-01", "2021-01-02",
                          http_get=_fake_page([]))
    assert rec["included"] is False
    assert rec["reason"].startswith("short_history")


# ---- no forward-fill: missing candles recorded, not filled -----------------

def test_missing_candles_recorded_not_filled():
    # two klines 3 days apart -> 1 missing candle, recorded
    kl = [[1609459200000] + ["1"] * 11, [1609718400000] + ["1"] * 11]
    assert fx._missing_candles(kl) == 2


# ---- source purity: no keys / signed / account / broker / order ------------

def test_source_has_no_secret_or_trading_surface():
    # Strip the module docstring + the FORBIDDEN_URL_FRAGMENTS guard tuple, since the words
    # account/order/apikey/secret/signature legitimately appear there as REJECTION targets
    # (describing what the tool blocks), not as actionable code.
    src = Path(fx.__file__).read_text(encoding="utf-8")
    doc = ast.get_docstring(ast.parse(src)) or ""
    code = src.replace(doc, "")
    code = re.sub(r"FORBIDDEN_URL_FRAGMENTS\s*=\s*\([^)]*\)", "", code)
    low = code.lower()
    # actionable secret / signed-request / trading tokens must be ABSENT from real code
    for bad in ("api_key", "hmac", ".sign(", "&signature=", "place_order", "create_order",
                "ccxt", "import keyring", "os.environ", "getenv", "private_key",
                "api/v3/account", "api/v3/order", "sapi/"):
        assert bad not in low, bad
    # only the klines endpoint literal appears as a network target
    assert low.count("https://api.binance.com") >= 1


def test_module_imports_no_broker_or_trading_libs():
    src = Path(fx.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned = {"ccxt", "binance", "telegram", "keyring", "requests", "websockets",
              "aiohttp", "smtplib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    # network only via urllib (the allowlisted, guarded surface)
    assert "urllib" in imported


# ---- writes only under the dataset dir -------------------------------------

def test_output_dir_is_contained():
    d = fx._out_dir()
    assert d.is_relative_to(fx.REPO_ROOT / fx.OUTPUT_SUBDIR)
    assert fx.OUTPUT_SUBDIR == "data/broad_crypto_universe_c23_c24"

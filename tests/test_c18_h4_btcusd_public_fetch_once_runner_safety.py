"""Safety tests for the C18 H4 BTCUSD public fetch runner
tools/c18_h4_btcusd_public_fetch_once.py.

Proves the runner is SAFE WITHOUT executing any network fetch: importing the module
performs no network call; the URL allowlist + forbidden-fragment guard reject
anything other than the public Binance klines endpoint and reject account/order/
trade/signed/credential fragments; the runner is restricted to symbol BTCUSDT and
interval 4h ONLY; no credential / env / secret reads; no broker/exchange SDK or
trading-endpoint literals in source; side effects (mkdir / file write / urlopen) live
only inside functions called from main(); a main guard exists and main() is not
called at import; writes only into the gitignored C18 H4 data dir; no XAUUSD. The
pure helpers (_build_url / _assert_safe_url / _assert_safe_symbol_interval / _to_ms)
are exercised; the network fetch (fetch_klines / main) is NEVER called here."""
from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "c18_h4_btcusd_public_fetch_once.py"


def _src():
    return RUNNER.read_text(encoding="utf-8")


def _mod():
    # importing the module must NOT make any network call (network lives in
    # functions called from main(), never at import time).
    import sys
    if str(_REPO_ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT / "tools"))
    return importlib.import_module("c18_h4_btcusd_public_fetch_once")


def test_runner_exists_and_imports_without_network():
    assert RUNNER.exists()
    m = _mod()                      # import = no fetch
    assert m.ALLOWED_SYMBOL == "BTCUSDT"
    assert m.ALLOWED_INTERVAL == "4h"


def test_symbol_and_interval_locked():
    m = _mod()
    m._assert_safe_symbol_interval("BTCUSDT", "4h")          # ok
    for bad in (("ETHUSDT", "4h"), ("BTCUSDT", "1d"), ("XAUUSD", "4h"),
                ("BTCUSDT", "1h")):
        with pytest.raises(m.FetchSafetyError):
            m._assert_safe_symbol_interval(*bad)


def test_url_allowlist_and_forbidden_fragments():
    m = _mod()
    # allowlisted public klines url passes
    ok = m._build_url("BTCUSDT", "4h", 1, 2, 1000)
    assert ok.startswith("https://api.binance.com/api/v3/klines")
    m._assert_safe_url(ok)
    # non-allowlisted host rejected
    for bad in ("https://evil.example.com/klines",
                "https://api.binance.com/api/v3/account",
                "https://api.binance.com/api/v3/order",
                "https://api.binance.com/sapi/v1/margin/trade",
                "https://api.binance.com/api/v3/klines?signature=x",
                "https://api.binance.com/api/v3/klines?apikey=x"):
        with pytest.raises(m.FetchSafetyError):
            m._assert_safe_url(bad)


def test_build_url_only_btcusdt_4h():
    m = _mod()
    with pytest.raises(m.FetchSafetyError):
        m._build_url("ETHUSDT", "4h", 1, 2, 10)
    with pytest.raises(m.FetchSafetyError):
        m._build_url("BTCUSDT", "1d", 1, 2, 10)


def test_to_ms_pure_and_deterministic():
    m = _mod()
    assert m._to_ms("1970-01-01") == 0
    assert m._to_ms("2019-01-01") == 1546300800000
    assert m._to_ms("2019-01-01") == m._to_ms("2019-01-01")   # deterministic


def test_no_network_call_at_import_time():
    src = _src()
    tree = ast.parse(src)
    # urlopen must only appear inside a function body, never at module top level
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            seg = ast.get_source_segment(src, node) or ""
            if "urlopen" in seg or "mkdir" in seg or "json.dump" in seg \
                    or "DictWriter" in seg:
                # find enclosing function
                enclosing = [f for f in ast.walk(tree)
                             if isinstance(f, ast.FunctionDef)
                             and f.lineno <= node.lineno
                             <= (f.end_lineno or f.lineno)]
                assert enclosing, "side effect %r at module scope" % seg[:40]
    # module top-level statements never call main()
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            assert getattr(node.value.func, "id", "") != "main"


def test_has_main_guard():
    src = _src()
    assert 'if __name__ == "__main__":' in src


def test_no_credentials_or_secrets_or_trading_usage():
    # ban genuine credential/trading USAGE (not the defensive forbidden-fragment
    # allowlist, which legitimately names order/account/apikey/etc as things to
    # REJECT).
    src = _src().lower()
    for tok in ("os.environ", "getenv", "load_dotenv", ".env", "place_order",
                "create_order", "new_order", "private_key", "hmac", "sign(",
                "_signed_request"):
        assert tok not in src, tok
    # the defensive forbidden-fragment guard MUST exist
    m = _mod()
    for frag in ("account", "order", "trade", "userdata", "signed", "apikey",
                 "secret"):
        assert frag in m.FORBIDDEN_URL_FRAGMENTS, frag


def test_no_broker_or_private_sdk_imports():
    src = _src()
    tree = ast.parse(src)
    banned = {"ccxt", "binance", "requests", "websockets", "aiohttp", "telegram",
              "alpaca", "ib_insync", "oandapyV20", "smtplib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    # urllib (public GET only) is the sole network surface
    assert "urllib" in imported


def test_no_xauusd_no_gold():
    # the runner must not be able to FETCH gold: symbol locked to BTCUSDT, and the
    # only XAU/gold mentions are the NO-XAUUSD safety disclaimer (negated).
    m = _mod()
    assert m.ALLOWED_SYMBOL == "BTCUSDT"
    assert "XAU" not in m.ALLOWED_SYMBOL
    # any line mentioning xau/gold must be a NO-XAUUSD safety disclaimer
    for line in _src().splitlines():
        low = line.lower()
        if "xau" in low or "gold" in low:
            assert "no " in low, "non-negated gold/XAU line: %s" % line.strip()


def test_writes_only_into_c18_h4_dir():
    src = _src()
    assert "h4_trend_following_market_structure_c18" in src
    assert "OUT_DIR" in src and "OUT_CSV" in src and "OUT_PROVENANCE" in src
    # SHA256 provenance required
    assert "compute_sha256" in src and "sha256" in src

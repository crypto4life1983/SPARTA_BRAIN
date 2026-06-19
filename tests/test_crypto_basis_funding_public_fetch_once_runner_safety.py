"""Safety tests for the public spot/perp/funding fetch runner
tools/crypto_basis_funding_public_fetch_once.py.

These tests DO NOT execute any network call. They read the source (AST + literals) and
exercise only the PURE safety guards (_assert_safe_url / _assert_safe_symbol_interval).

Verified: public-market-data-only URL allowlist; no API key / credential / env / secret
reads; no signed / account / order / trade / userdata / private endpoints; no broker /
exchange SDK; symbols restricted to BTCUSDT/ETHUSDT/SOLUSDT and interval 1d; SHA256
provenance required; output under the gitignored research dir; side effects only inside
main() / functions it calls; no network at import time."""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

import tools.crypto_basis_funding_public_fetch_once as fx

_REPO_ROOT = Path(__file__).resolve().parents[1]
RUNNER = _REPO_ROOT / "tools" / "crypto_basis_funding_public_fetch_once.py"


def _src():
    return RUNNER.read_text(encoding="utf-8")


def test_runner_exists():
    assert RUNNER.exists()


def test_no_credential_env_or_secret_reads():
    src = _src()
    for tok in ("os.environ", "getenv", "import dotenv", "load_dotenv",
                "api_key", "apiKey =", "secret =", "Secret(", "hmac", "hashlib.new",
                "sign(", "signature =", "X-MBX-APIKEY", "binance.client",
                "import ccxt", "from ccxt", "import binance", "Spot(", "Client("):
        assert tok not in src, tok


def test_only_public_market_data_url_allowlist():
    src = _src()
    assert "ALLOWED_URL_PREFIXES" in src
    assert "https://api.binance.com/api/v3/klines" in src
    assert "https://fapi.binance.com/fapi/v1/klines" in src
    assert "https://fapi.binance.com/fapi/v1/fundingRate" in src
    # no signed / account / order / userdata endpoint literals anywhere
    for bad in ("/api/v3/order", "/fapi/v1/order", "/sapi/", "/api/v3/account",
                "fapi/v1/account", "userDataStream", "listenKey", "/withdraw",
                "positionRisk", "leverage"):
        assert bad not in src, bad


def test_assert_safe_url_accepts_allowlist_rejects_rest():
    # pure -- no network
    fx._assert_safe_url("https://api.binance.com/api/v3/klines?symbol=BTCUSDT")
    fx._assert_safe_url("https://fapi.binance.com/fapi/v1/klines?symbol=ETHUSDT")
    fx._assert_safe_url("https://fapi.binance.com/fapi/v1/fundingRate?symbol=SOLUSDT")
    for bad in ("https://api.binance.com/api/v3/order?symbol=BTCUSDT",
                "https://fapi.binance.com/fapi/v1/account",
                "https://api.binance.com/sapi/v1/capital/withdraw",
                "https://evil.example.com/klines",
                "https://api.binance.com/api/v3/klines?signature=abc"):
        with pytest.raises(fx.FetchSafetyError):
            fx._assert_safe_url(bad)


def test_symbol_and_interval_restricted():
    for sym in ("BTCUSDT", "ETHUSDT", "SOLUSDT"):
        fx._assert_safe_symbol_interval(sym, "1d")
    for bad_sym in ("XAUUSD", "DOGEUSDT", "BTCUSD"):
        with pytest.raises(fx.FetchSafetyError):
            fx._assert_safe_symbol_interval(bad_sym, "1d")
    for bad_int in ("4h", "1h", "5m"):
        with pytest.raises(fx.FetchSafetyError):
            fx._assert_safe_symbol_interval("BTCUSDT", bad_int)
    assert fx.ALLOWED_SYMBOLS == ("BTCUSDT", "ETHUSDT", "SOLUSDT")
    assert fx.ALLOWED_INTERVAL == "1d"
    # no XAUUSD / gold anywhere (any such line must be a NO-gold disclaimer)
    for line in _src().splitlines():
        low = line.lower()
        if "xau" in low or "gold" in low:
            assert "no xau" in low or "no gold" in low, line.strip()


def test_sha256_provenance_required():
    src = _src()
    assert "compute_sha256" in src
    assert "hashlib.sha256()" in src
    assert "sha256" in src
    assert "manifest_sha256" in src


def test_output_under_gitignored_research_dir():
    src = _src()
    assert "data" in src and "crypto_basis_funding_research" in src and "raw" in src
    # the output dir is gitignored
    out = (_REPO_ROOT / "data" / "crypto_basis_funding_research" / "raw"
           / "BTCUSDT_spot_1d.csv")
    import subprocess
    res = subprocess.run(["git", "check-ignore", str(out)], cwd=str(_REPO_ROOT),
                         capture_output=True, text=True)
    assert res.returncode == 0, "output path must be gitignored"


def test_no_network_at_import_and_main_guarded():
    src = _src()
    assert 'if __name__ == "__main__":' in src
    tree = ast.parse(src)
    # no top-level (module-level) call expressions -> no fetch at import
    for node in tree.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            name = getattr(node.value.func, "id", "")
            assert name != "main", "main() must not run at import"
    # urlopen / csv.writer / json.dump / mkdir only inside function bodies
    func_lines = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef,)):
            func_lines |= set(range(node.lineno,
                                    (node.end_lineno or node.lineno) + 1))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            seg = ast.get_source_segment(src, node) or ""
            if ("urlopen" in seg or "json.dump(" in seg or ".mkdir(" in seg
                    or "csv.writer" in seg):
                assert node.lineno in func_lines, node.lineno


def test_no_orders_no_trading_no_broker():
    src = _src()
    for tok in ("place_order", "create_order", "new_order", "cancel_order",
                "futures_create_order", "set_leverage", "transfer", "withdraw(",
                "buy(", "sell("):
        assert tok not in src, tok

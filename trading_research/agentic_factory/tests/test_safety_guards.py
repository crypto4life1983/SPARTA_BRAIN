"""Safety guard tests.

Scans the module's own Python source for forbidden imports and forbidden path
strings. If any appear, the module is no longer offline/inert and the test
fails loudly.

Scope of the scan: all .py files under the module root EXCEPT this tests
directory. The tests directory is excluded on purpose because this very file
must contain the forbidden tokens (as the list of things to search for) and
the other test files import the engine for legitimate checks.
"""

import os

MODULE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TESTS_DIR = os.path.dirname(os.path.abspath(__file__))

# Forbidden substrings (matched case-insensitively).
FORBIDDEN_TOKENS = [
    "requests",
    "urllib",
    "httpx",
    "aiohttp",
    "websockets",
    "ccxt",
    "bybit",
    "binance",
    "databento",
    "ib_insync",
    "alpaca",
    "local_secrets",
    ".env",
    "api_key",
    "secret",
    r"c:\users\mahmo\obsidian-trade-logger",
]


def _scanned_py_files():
    files = []
    for root, _dirs, names in os.walk(MODULE_ROOT):
        if os.path.abspath(root).startswith(TESTS_DIR):
            continue
        for name in names:
            if name.endswith(".py"):
                files.append(os.path.join(root, name))
    return files


def test_module_has_python_source_to_scan():
    files = _scanned_py_files()
    # Sanity: the engine and loop should exist and be scanned.
    assert any(os.path.join("engine", "metrics.py") in f for f in files)
    assert any(os.path.join("engine", "backtester.py") in f for f in files)
    assert any(os.path.join("loop", "factory_loop.py") in f for f in files)


def test_no_forbidden_tokens_in_module_source():
    offenders = {}
    for path in _scanned_py_files():
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read().lower()
        hits = [tok for tok in FORBIDDEN_TOKENS if tok.lower() in text]
        if hits:
            offenders[path] = hits
    assert not offenders, f"Forbidden tokens found in module source: {offenders}"

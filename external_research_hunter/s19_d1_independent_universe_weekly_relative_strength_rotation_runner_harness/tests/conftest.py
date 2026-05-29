"""pytest fixtures + env guards for s19-d1 independent-universe weekly RS rotation runner harness tests."""

import pathlib
import sys

import pytest


@pytest.fixture(autouse=True)
def _env_guards(monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "invalid")
    monkeypatch.setenv("HTTPS_PROXY", "invalid")
    monkeypatch.delenv("TIINGO_API_KEY", raising=False)
    yield


@pytest.fixture
def synthetic_prices():
    """Deterministic synthetic multi-symbol close series (NOT real data). 6 symbols x 260 bars, distinct rates."""
    n = 260
    rates = {"A": 0.0010, "B": 0.0008, "C": 0.0006, "D": 0.0004, "E": 0.0002, "F": -0.0002}
    out = {}
    for sym, r in rates.items():
        closes = []
        px = 100.0
        for _ in range(n):
            closes.append(round(px, 6))
            px *= (1.0 + r)
        out[sym] = closes
    return out


@pytest.fixture
def synthetic_csv_path():
    return pathlib.Path(__file__).parent / "fixtures" / "synthetic_independent_universe_daily.csv"


@pytest.fixture
def runner_harness_module():
    repo_root = pathlib.Path(__file__).resolve().parents[4]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    pkg = ("external_research_hunter."
           "s19_d1_independent_universe_weekly_relative_strength_rotation_runner_harness")
    import importlib
    return {
        "main": importlib.import_module(pkg + ".main"),
        "execution_guard": importlib.import_module(pkg + ".execution_guard"),
        "in_sample_driver": importlib.import_module(pkg + ".in_sample_driver"),
        "out_of_sample_driver": importlib.import_module(pkg + ".out_of_sample_driver"),
        "walk_forward_driver": importlib.import_module(pkg + ".walk_forward_driver"),
    }

"""pytest fixtures + env guards for s16-d1 Donchian trend runner harness tests."""

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
def synthetic_csv_path():
    return pathlib.Path(__file__).parent / "fixtures" / "synthetic_cross_sector_daily.csv"


@pytest.fixture
def synthetic_csv_rows(synthetic_csv_path):
    import csv
    rows = []
    with open(synthetic_csv_path, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for k in ("open", "high", "low", "close", "volume"):
                if k in row and row[k]:
                    row[k] = float(row[k])
            rows.append(row)
    return rows


@pytest.fixture
def runner_harness_module():
    repo_root = pathlib.Path(__file__).resolve().parents[4]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    pkg = ("external_research_hunter."
           "s16_d1_expanded_cross_sector_cash_equity_donchian_breakout_trend_trailing_stop_runner_harness")
    import importlib
    return {
        "main": importlib.import_module(pkg + ".main"),
        "execution_guard": importlib.import_module(pkg + ".execution_guard"),
        "in_sample_driver": importlib.import_module(pkg + ".in_sample_driver"),
        "out_of_sample_driver": importlib.import_module(pkg + ".out_of_sample_driver"),
    }

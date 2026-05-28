"""pytest fixtures + env guards for s14-d1-cross-sector runner harness tests."""

import pathlib
import sys

import pytest


@pytest.fixture(autouse=True)
def _env_guards(monkeypatch):
    """Hard-deny network and API keys."""
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
        reader = csv.DictReader(f)
        for row in reader:
            for k in ("open", "high", "low", "close", "volume"):
                if k in row and row[k]:
                    row[k] = float(row[k])
            rows.append(row)
    return rows


@pytest.fixture
def runner_harness_module():
    """Import the s14-d1-cross-sector runner harness package."""
    repo_root = pathlib.Path(__file__).resolve().parents[4]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    pkg_name = (
        "external_research_hunter."
        "s14_d1_aapl_jpm_xom_cross_sector_cash_equity_rsi_3_bi_directional_large_cap_long_history_runner_harness"
    )
    import importlib
    return {
        "main": importlib.import_module(pkg_name + ".main"),
        "execution_guard": importlib.import_module(pkg_name + ".execution_guard"),
        "in_sample_driver": importlib.import_module(pkg_name + ".in_sample_driver"),
        "out_of_sample_driver": importlib.import_module(pkg_name + ".out_of_sample_driver"),
    }

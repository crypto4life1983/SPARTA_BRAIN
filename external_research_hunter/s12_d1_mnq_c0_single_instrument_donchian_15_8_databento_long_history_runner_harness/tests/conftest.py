"""pytest fixtures + env guards for s12-d1 runner harness tests.

Env guards (per P1 plan-lock §10):
  - PYTHONPATH=C:\\SPARTA_BRAIN (set by invocation)
  - HTTP_PROXY=invalid (force any network attempt to fail loudly)
  - DATABENTO_API_KEY popped (no key access at test time)
"""

import os
import sys
import pathlib

import pytest


@pytest.fixture(autouse=True)
def _env_guards(monkeypatch):
    """Hard-deny network and API keys for every test."""
    monkeypatch.setenv("HTTP_PROXY", "invalid")
    monkeypatch.setenv("HTTPS_PROXY", "invalid")
    monkeypatch.delenv("DATABENTO_API_KEY", raising=False)
    yield


@pytest.fixture
def synthetic_csv_path():
    """Path to the synthetic MNQ daily fixture CSV (SYNTHETIC_PHASE2_SMOKE_FIXTURE)."""
    return pathlib.Path(__file__).parent / "fixtures" / "synthetic_mnq_daily.csv"


@pytest.fixture
def synthetic_csv_rows(synthetic_csv_path):
    """Read the synthetic CSV into a list of dicts."""
    import csv

    rows = []
    with open(synthetic_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric fields
            for k in ("open", "high", "low", "close", "volume"):
                if k in row and row[k]:
                    row[k] = float(row[k])
            rows.append(row)
    return rows


@pytest.fixture
def runner_harness_module():
    """Import the runner harness package as a module (top-level import test).

    Asserts that main + execution_guard + drivers import without QC or databento at module level.
    """
    # Add repo root to sys.path if not already (typical when invoked with --rootdir)
    repo_root = pathlib.Path(__file__).resolve().parents[4]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    pkg_name = (
        "external_research_hunter."
        "s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness"
    )
    import importlib

    main_mod = importlib.import_module(pkg_name + ".main")
    guard_mod = importlib.import_module(pkg_name + ".execution_guard")
    is_mod = importlib.import_module(pkg_name + ".in_sample_driver")
    oos_mod = importlib.import_module(pkg_name + ".out_of_sample_driver")
    return {
        "main": main_mod,
        "execution_guard": guard_mod,
        "in_sample_driver": is_mod,
        "out_of_sample_driver": oos_mod,
    }

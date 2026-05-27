"""Pytest configuration for the s10-D2 NO-PYRAMID REPARAM-CAP smoke test battery.

Provides the `fixtures_dir` fixture pointing to tests/fixtures/.
Synthetic-only. No real market data. No Databento. No network.
"""
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"

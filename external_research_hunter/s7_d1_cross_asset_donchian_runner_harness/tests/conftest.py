"""Pytest configuration for s7 D1 smoke tests.

PREPARED for P4 -- NOT executed at BUILD time.
"""

from pathlib import Path
import pytest


HARNESS_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(scope="session")
def harness_root() -> Path:
    return HARNESS_ROOT


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES_DIR

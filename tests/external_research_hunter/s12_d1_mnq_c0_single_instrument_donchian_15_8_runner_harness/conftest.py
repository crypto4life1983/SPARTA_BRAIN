"""Pytest config for S12-D1 runner harness smoke battery.

Ensures the repo root is on sys.path so the runner_harness package can
be imported as
`external_research_hunter.s12_d1_mnq_c0_single_instrument_donchian_15_8_runner_harness`.
"""
from __future__ import annotations

import pathlib
import sys


def _add_repo_root_to_sys_path() -> None:
    # __file__ = .../tests/external_research_hunter/.../conftest.py
    here = pathlib.Path(__file__).resolve()
    # Walk up to the repo root (directory containing 'external_research_hunter/')
    for parent in [here.parent] + list(here.parents):
        if (parent / "external_research_hunter").is_dir() and (parent / "data").is_dir():
            sp = str(parent)
            if sp not in sys.path:
                sys.path.insert(0, sp)
            return


_add_repo_root_to_sys_path()

"""S10-D2 OOS driver invariants (P3.6 BUILD-EXTENSION).

Proves:
  1. IS driver source byte-stable through P3.6 (P3 BUILD sha frozen).
  2. OOS driver constants are the expected OOS values.
  3. OOS driver does NOT leak IS-specific paths/dates/byte counts.
  4. Strategy params from runner_main.CONFIG are unchanged.
  5. OOS driver function signature matches expected.
  6. Lazy import patterns preserved (no top-level databento/QC/AlgorithmImports).
"""
from __future__ import annotations

import ast
import datetime
import hashlib
import inspect
import re
from pathlib import Path

import pytest

from external_research_hunter.s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness import (
    in_sample_driver as is_driver,
    out_of_sample_driver as oos_driver,
    main as runner_main,
)


# ---------------------------------------------------------------------------
# 1. IS driver source byte-stable through P3.6
# ---------------------------------------------------------------------------
IS_DRIVER_SHA_P3_BUILD = "19749ada4d98e1b2dbd7bd226699807d6e1adfbc965d033d1ac58795350f9919"


def test_is_driver_source_byte_stable_through_p3_6():
    """IS driver source MUST be byte-identical to its P3 BUILD baseline.
    Authoring the OOS driver must not touch in_sample_driver.py."""
    is_path = Path(is_driver.__file__)
    actual = hashlib.sha256(is_path.read_bytes()).hexdigest()
    assert actual == IS_DRIVER_SHA_P3_BUILD, (
        f"IS driver source drifted from P3 BUILD baseline. "
        f"expected={IS_DRIVER_SHA_P3_BUILD} actual={actual}"
    )


# ---------------------------------------------------------------------------
# 2. OOS driver constants are correct
# ---------------------------------------------------------------------------
def test_oos_driver_cache_root_points_to_oos_dir():
    assert oos_driver.CACHE_ROOT == Path(r"C:\SPARTA_BRAIN\data\databento_cache_oos")


def test_oos_driver_window_start_is_2023_01_01():
    assert oos_driver.OUT_OF_SAMPLE_START == datetime.date(2023, 1, 1)


def test_oos_driver_window_end_is_2025_12_31():
    assert oos_driver.OUT_OF_SAMPLE_END == datetime.date(2025, 12, 31)


def test_oos_driver_expected_files_per_root_is_36():
    assert oos_driver.EXPECTED_FILES_PER_ROOT == 36


def test_oos_driver_expected_cache_bytes_match_oos():
    assert oos_driver.EXPECTED_CACHE_BYTES == {
        "NQ": 19_770_364,
        "GC":    540_803,
        "ZN":  8_573_282,
        "CL": 13_779_406,
    }


# ---------------------------------------------------------------------------
# 3. OOS driver does NOT leak IS-specific values
# ---------------------------------------------------------------------------
def test_oos_driver_does_not_have_is_window_constants():
    assert not hasattr(oos_driver, "IN_SAMPLE_START")
    assert not hasattr(oos_driver, "IN_SAMPLE_END")


def test_oos_driver_does_not_reference_is_cache_dir_in_source():
    src = Path(oos_driver.__file__).read_text(encoding="utf-8")
    # IS cache path should not appear at all in OOS driver
    assert 'r"C:\\SPARTA_BRAIN\\data\\databento_cache"' not in src
    assert 'data\\databento_cache"' not in src
    # OOS cache path must appear
    assert "databento_cache_oos" in src


def test_oos_driver_does_not_reference_is_dates_in_source():
    src = Path(oos_driver.__file__).read_text(encoding="utf-8")
    # 2013 and 2022 are IS-specific dates; should not appear as date constants
    assert "datetime.date(2013," not in src
    assert "datetime.date(2022," not in src


def test_oos_driver_does_not_reference_is_byte_counts_in_source():
    src = Path(oos_driver.__file__).read_text(encoding="utf-8")
    for is_b in ("53_148_359", "2_162_216", "27_939_222", "46_540_654"):
        assert is_b not in src, f"IS byte count {is_b} still present in OOS driver"


def test_oos_driver_does_not_reference_run_in_sample_anywhere():
    src = Path(oos_driver.__file__).read_text(encoding="utf-8")
    assert not re.search(r"\brun_in_sample\b", src)


def test_oos_driver_does_not_have_run_in_sample_function():
    assert not hasattr(oos_driver, "run_in_sample")
    assert hasattr(oos_driver, "run_out_of_sample")


# ---------------------------------------------------------------------------
# 4. Strategy params (runner_main.CONFIG) are identical for both drivers
# ---------------------------------------------------------------------------
def test_runner_main_config_strategy_params_unchanged():
    """Both drivers import the same runner_main.CONFIG, which is the source
    of strategy parameters. P3.6 must not have touched CONFIG."""
    cfg = runner_main.CONFIG
    assert cfg["max_units_per_market"]              == 1
    assert cfg["starting_cash_mnq_equivalent"]      == 500_000
    assert cfg["pyramid_spacing_n_multiplier"]      == 0.5
    assert cfg["stop_n_multiplier"]                 == 2.0
    assert cfg["risk_pct_per_unit"]                 == 0.01


def test_both_drivers_use_same_runner_main_module():
    """The lazy import of runner_main in both drivers must resolve to the
    same module object — same CONFIG, same helpers, same algorithmic logic."""
    is_runner_main = is_driver._import_runner_main()
    oos_runner_main = oos_driver._import_runner_main()
    assert is_runner_main is oos_runner_main


def test_both_drivers_share_seal_constants():
    """The 6 inherited-chain seal constants must be byte-identical between
    IS and OOS drivers — both inherit the same chain."""
    for name in (
        "PREDECESSOR_SEAL_SHA256",
        "TIER_N_SPEC_SEAL_SHA256",
        "PLAN_LOCK_SEAL_SHA256",
        "PHASE2_PLAN_SEAL_SHA256",
        "PHASE2_TEMPLATE_MD_SHA256",
        "PHASE2_TEMPLATE_JSON_SHA256",
    ):
        assert getattr(is_driver, name) == getattr(oos_driver, name), (
            f"Seal constant {name} differs between IS and OOS drivers")


# ---------------------------------------------------------------------------
# 5. OOS driver function signature matches expected
# ---------------------------------------------------------------------------
def test_oos_run_function_signature_matches_is():
    is_sig  = inspect.signature(is_driver.run_in_sample)
    oos_sig = inspect.signature(oos_driver.run_out_of_sample)
    # Both must have the same parameter names and defaults
    assert list(is_sig.parameters.keys()) == list(oos_sig.parameters.keys())
    assert is_sig.parameters["cost_tier"].default == "S1"
    assert oos_sig.parameters["cost_tier"].default == "S1"
    assert is_sig.parameters["expected_seals"].default is None
    assert oos_sig.parameters["expected_seals"].default is None


# ---------------------------------------------------------------------------
# 6. Lazy import patterns preserved (no top-level databento/QC)
# ---------------------------------------------------------------------------
def test_oos_driver_no_top_level_forbidden_imports():
    src = Path(oos_driver.__file__).read_text(encoding="utf-8")
    tree = ast.parse(src)
    forbidden = {"AlgorithmImports", "QuantConnect", "databento"}
    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in forbidden, f"top-level import of {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            mod = (node.module or "").split(".")[0]
            assert mod not in forbidden, f"top-level from-import of {node.module}"


def test_oos_driver_databento_import_is_function_local():
    """databento must only be imported inside load_dbn_local (lazy)."""
    src = Path(oos_driver.__file__).read_text(encoding="utf-8")
    # The import must appear inside the function body
    assert "import databento as db" in src
    # And the lazy-import comment must be preserved
    assert "lazy import" in src or "WPS433" in src


def test_oos_driver_does_not_instantiate_db_historical():
    """db.Historical should NOT appear as an actual call. The IS driver has a
    docstring phrase 'NEVER instantiates db.Historical()' which is the guard
    statement; that phrase legitimately carries over to the OOS driver via
    mechanical substitution and is NOT a real call."""
    src = Path(oos_driver.__file__).read_text(encoding="utf-8")
    suspicious = []
    for line_no, line in enumerate(src.splitlines(), start=1):
        if "db.Historical(" not in line:
            continue
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        # Guard-phrase whitelist (docstring statements about what we do NOT do)
        upper = line.upper()
        if "NEVER" in upper or "DO NOT" in upper or "NOT INSTANTIATE" in upper:
            continue
        suspicious.append((line_no, line))
    assert not suspicious, f"OOS driver appears to invoke db.Historical: {suspicious}"

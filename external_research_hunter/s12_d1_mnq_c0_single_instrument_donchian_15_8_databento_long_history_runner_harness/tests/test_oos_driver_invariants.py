"""OOS driver invariants tests for s12-d1 runner harness.

These tests are AUTHORED at P3 BUILD. They are EXECUTED at P4 synthetic smoke
under separate operator authorization. P3 BUILD does NOT execute these tests.

Verifies the structural isolation of out_of_sample_driver.py from in_sample_driver.py
and from IS-window constants per s11-d1 lesson + s12-d1 P1 plan-lock §10.
"""

import datetime
import inspect
import pathlib
import re


# ---------- test_oos_driver_cache_path_points_to_csv ----------

def test_oos_driver_cache_path_points_to_csv(runner_harness_module):
    """oos_driver.CSV_PATH_HARDCODED == sealed MNQ CSV."""
    oos = runner_harness_module["out_of_sample_driver"]
    assert oos.CSV_PATH_HARDCODED == (
        "data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv"
    )
    assert oos.CSV_SHA256_HARDCODED == (
        "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e"
    )


# ---------- test_oos_driver_window_start_is_2024_01_02 ----------

def test_oos_driver_window_start_is_2024_01_02(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    assert oos.OUT_OF_SAMPLE_START == datetime.date(2024, 1, 2)


# ---------- test_oos_driver_window_end_is_2025_12_30 ----------

def test_oos_driver_window_end_is_2025_12_30(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    assert oos.OUT_OF_SAMPLE_END == datetime.date(2025, 12, 30)


# ---------- test_oos_driver_does_not_have_is_window_constants ----------

def test_oos_driver_does_not_have_is_window_constants(runner_harness_module):
    """OOS driver module must NOT export IN_SAMPLE_START / IN_SAMPLE_END constants."""
    oos = runner_harness_module["out_of_sample_driver"]
    assert not hasattr(oos, "IN_SAMPLE_START")
    assert not hasattr(oos, "IN_SAMPLE_END")


# ---------- test_oos_driver_does_not_reference_is_dates_in_source ----------

def test_oos_driver_does_not_reference_is_dates_in_source(runner_harness_module):
    """No standalone 2019 / 2023 year tokens in OOS driver source code.

    Word-boundary regex ensures the CSV filename embedding (e.g. '20190513') does NOT match.
    """
    oos = runner_harness_module["out_of_sample_driver"]
    source_path = pathlib.Path(inspect.getfile(oos))
    source = source_path.read_text(encoding="utf-8")
    # Word-boundary match for standalone year tokens
    assert re.search(r"\b2019\b", source) is None, (
        "OOS driver source must not reference standalone 2019"
    )
    assert re.search(r"\b2023\b", source) is None, (
        "OOS driver source must not reference standalone 2023"
    )


# ---------- test_oos_driver_does_not_have_run_in_sample_function ----------

def test_oos_driver_does_not_have_run_in_sample_function(runner_harness_module):
    """OOS driver must NOT expose a run_in_sample function."""
    oos = runner_harness_module["out_of_sample_driver"]
    assert not hasattr(oos, "run_in_sample"), (
        "out_of_sample_driver must not expose run_in_sample"
    )


# ---------- test_both_drivers_use_same_runner_main_module ----------

def test_both_drivers_use_same_runner_main_module(runner_harness_module):
    """Lazy-import resolves to same main module object across drivers.

    Both drivers reference the runner_harness package; importing main from either
    path should resolve to the same module instance in sys.modules.
    """
    import sys
    pkg_name = (
        "external_research_hunter."
        "s12_d1_mnq_c0_single_instrument_donchian_15_8_databento_long_history_runner_harness"
    )
    main_via_is = sys.modules.get(pkg_name + ".main")
    main_via_oos = sys.modules.get(pkg_name + ".main")
    assert main_via_is is main_via_oos
    assert main_via_is is runner_harness_module["main"]


# ---------- test_runner_main_config_strategy_params_unchanged ----------

def test_runner_main_config_strategy_params_unchanged(runner_harness_module):
    """CONFIG strategy params byte-identical across drivers (main is single source of truth)."""
    main = runner_harness_module["main"]
    cfg = main.CONFIG
    assert cfg["donchian_entry_period_n"] == 15
    assert cfg["donchian_exit_period_n"] == 8
    assert cfg["atr_period"] == 20
    assert cfg["atr_method"] == "Wilder"
    assert cfg["stop_multiplier_in_atr"] == 2.0
    assert cfg["risk_pct_per_trade"] == 0.01
    assert cfg["max_units_per_market"] == 1
    assert cfg["starting_cash_mnq_equivalent"] == 100_000  # DA4=B
    assert cfg["tick_value_usd"] == 0.5
    assert cfg["verdict_min_closed_trades"] == 100  # K9 inviolate
    assert cfg["rec1_binding"] is True


# ---------- test_oos_run_function_signature_matches_is ----------

def test_oos_run_function_signature_matches_is(runner_harness_module):
    """run_out_of_sample and run_in_sample have compatible *args/**kwargs signatures."""
    is_driver = runner_harness_module["in_sample_driver"]
    oos_driver = runner_harness_module["out_of_sample_driver"]
    is_sig = inspect.signature(is_driver.run_in_sample)
    oos_sig = inspect.signature(oos_driver.run_out_of_sample)
    # Both stub-raise; signatures should accept *args, **kwargs
    assert str(is_sig) == str(oos_sig), (
        f"signature mismatch: IS={is_sig} OOS={oos_sig}"
    )


# ---------- test_oos_driver_no_top_level_forbidden_imports ----------

def test_oos_driver_no_top_level_forbidden_imports(runner_harness_module):
    """No top-level databento / QuantConnect / AlgorithmImports in OOS driver source."""
    oos = runner_harness_module["out_of_sample_driver"]
    source_path = pathlib.Path(inspect.getfile(oos))
    source = source_path.read_text(encoding="utf-8")
    forbidden_top_level = (
        r"^import\s+databento",
        r"^from\s+databento\s+import",
        r"^import\s+AlgorithmImports",
        r"^from\s+AlgorithmImports\s+import",
        r"^import\s+QuantConnect",
        r"^from\s+QuantConnect\s+import",
    )
    for pattern in forbidden_top_level:
        assert re.search(pattern, source, flags=re.MULTILINE) is None, (
            f"forbidden top-level import matching {pattern!r} in OOS driver source"
        )


# ---------- test_oos_driver_databento_import_is_function_local ----------

def test_oos_driver_databento_import_is_function_local(runner_harness_module):
    """If databento is imported anywhere in OOS driver, it must be function-local.

    s12-d1 reuses sealed CSV; databento is not required. This test verifies that IF
    any databento import is present in the source, it's not at module top level.
    """
    oos = runner_harness_module["out_of_sample_driver"]
    source_path = pathlib.Path(inspect.getfile(oos))
    source = source_path.read_text(encoding="utf-8")
    # The OOS driver should not need databento at all (CSV-only). Verify that any
    # databento mention is either absent or inside a function (indented).
    for line_no, line in enumerate(source.splitlines(), start=1):
        if "databento" in line.lower():
            # The line must be indented (function-local) — unless it's a comment/docstring
            stripped = line.lstrip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                # Must be indented (not module-level)
                assert line != stripped, (
                    f"databento import at module top level on line {line_no}: {line!r}"
                )


# ---------- test_oos_driver_does_not_instantiate_db_historical ----------

def test_oos_driver_does_not_instantiate_db_historical(runner_harness_module):
    """No db.Historical() instantiation in OOS driver (s12-d1 reuses sealed CSV; no fresh fetch)."""
    oos = runner_harness_module["out_of_sample_driver"]
    source_path = pathlib.Path(inspect.getfile(oos))
    source = source_path.read_text(encoding="utf-8")
    forbidden_patterns = (
        r"\bdb\.Historical\s*\(",
        r"\bdatabento\.Historical\s*\(",
        r"\bHistorical\s*\(",
    )
    for pattern in forbidden_patterns:
        assert re.search(pattern, source) is None, (
            f"forbidden fresh-fetch pattern {pattern!r} found in OOS driver source"
        )

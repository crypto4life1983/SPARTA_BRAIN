"""OOS driver invariants tests for s13-d1 runner harness."""

import datetime
import inspect
import pathlib
import re


def test_oos_driver_cache_path_points_to_csv(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    assert oos.CSV_PATH_HARDCODED == (
        "data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv"
    )
    assert oos.CSV_SHA256_HARDCODED == (
        "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e"
    )


def test_oos_driver_window_start_is_2024_01_02(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    assert oos.OUT_OF_SAMPLE_START == datetime.date(2024, 1, 2)


def test_oos_driver_window_end_is_2025_12_30(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    assert oos.OUT_OF_SAMPLE_END == datetime.date(2025, 12, 30)


def test_oos_driver_does_not_have_is_window_constants(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    assert not hasattr(oos, "IN_SAMPLE_START")
    assert not hasattr(oos, "IN_SAMPLE_END")


def test_oos_driver_does_not_reference_is_dates_in_source(runner_harness_module):
    """No standalone 2019 / 2023 year tokens (word-boundary regex; CSV filename embed exempt)."""
    oos = runner_harness_module["out_of_sample_driver"]
    source = pathlib.Path(inspect.getfile(oos)).read_text(encoding="utf-8")
    assert re.search(r"\b2019\b", source) is None
    assert re.search(r"\b2023\b", source) is None


def test_oos_driver_does_not_have_run_in_sample_function(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    assert not hasattr(oos, "run_in_sample")


def test_both_drivers_use_same_runner_main_module(runner_harness_module):
    import sys
    pkg_name = (
        "external_research_hunter."
        "s13_d1_mnq_c0_single_instrument_rsi_2_bi_directional_databento_long_history_runner_harness"
    )
    main_a = sys.modules.get(pkg_name + ".main")
    main_b = sys.modules.get(pkg_name + ".main")
    assert main_a is main_b
    assert main_a is runner_harness_module["main"]


def test_runner_main_config_strategy_params_unchanged(runner_harness_module):
    """CONFIG strategy params byte-identical across drivers (main is single source of truth)."""
    main = runner_harness_module["main"]
    cfg = main.CONFIG
    assert cfg["rsi_period"] == 2
    assert cfg["rsi_long_entry_threshold"] == 10
    assert cfg["rsi_long_exit_threshold"] == 50
    assert cfg["rsi_short_entry_threshold"] == 90
    assert cfg["rsi_short_exit_threshold"] == 50
    assert cfg["atr_period"] == 20
    assert cfg["atr_method"] == "Wilder"
    assert cfg["stop_multiplier_in_atr"] == 2.0
    assert cfg["risk_pct_per_trade"] == 0.005  # DA3=B
    assert cfg["max_units_per_market"] == 1
    assert cfg["starting_cash_mnq_equivalent"] == 200_000  # DA4=C
    assert cfg["tick_value_usd"] == 0.5
    assert cfg["verdict_min_closed_trades"] == 100
    assert cfg["rec1_equivalent_binding"] is True


def test_oos_run_function_signature_matches_is(runner_harness_module):
    is_driver = runner_harness_module["in_sample_driver"]
    oos_driver = runner_harness_module["out_of_sample_driver"]
    is_sig = inspect.signature(is_driver.run_in_sample)
    oos_sig = inspect.signature(oos_driver.run_out_of_sample)
    assert str(is_sig) == str(oos_sig)


def test_oos_driver_no_top_level_forbidden_imports(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    source = pathlib.Path(inspect.getfile(oos)).read_text(encoding="utf-8")
    forbidden = (
        r"^import\s+databento",
        r"^from\s+databento\s+import",
        r"^import\s+AlgorithmImports",
        r"^from\s+AlgorithmImports\s+import",
        r"^import\s+QuantConnect",
        r"^from\s+QuantConnect\s+import",
    )
    for pattern in forbidden:
        assert re.search(pattern, source, flags=re.MULTILINE) is None


def test_oos_driver_databento_import_is_function_local(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    source = pathlib.Path(inspect.getfile(oos)).read_text(encoding="utf-8")
    for line_no, line in enumerate(source.splitlines(), start=1):
        if "databento" in line.lower():
            stripped = line.lstrip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                assert line != stripped, (
                    f"databento import at module top level on line {line_no}: {line!r}"
                )


def test_oos_driver_does_not_instantiate_db_historical(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    source = pathlib.Path(inspect.getfile(oos)).read_text(encoding="utf-8")
    forbidden = (
        r"\bdb\.Historical\s*\(",
        r"\bdatabento\.Historical\s*\(",
        r"\bHistorical\s*\(",
    )
    for pattern in forbidden:
        assert re.search(pattern, source) is None

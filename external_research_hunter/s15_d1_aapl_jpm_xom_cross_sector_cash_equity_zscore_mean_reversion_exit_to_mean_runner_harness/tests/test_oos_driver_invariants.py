"""OOS driver invariants tests for s15-d1-cross-sector z-score exit-to-mean runner harness."""

import datetime
import inspect
import pathlib
import re


def test_oos_driver_registry_points_to_three_cross_sector_csvs(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    assert set(oos.CSV_REGISTRY.keys()) == {"AAPL", "JPM", "XOM"}
    assert oos.CSV_REGISTRY["AAPL"]["sha256"] == "f6625ff1a6f8026369344bd50ca82bffcba716f1f3be9cdcfb5b905e35f893a9"
    assert oos.CSV_REGISTRY["JPM"]["sha256"] == "8aa244ab7724b292c659c81171bd8d3cf5ce5684d6c69864ee61e0be90238db7"
    assert oos.CSV_REGISTRY["XOM"]["sha256"] == "fbbc462cbfbd11a68b0aed4d0c3fa72312afea5112cebcc24860689f33b7f77c"


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
        "s15_d1_aapl_jpm_xom_cross_sector_cash_equity_zscore_mean_reversion_exit_to_mean_runner_harness"
    )
    main_a = sys.modules.get(pkg_name + ".main")
    assert main_a is runner_harness_module["main"]


def test_runner_main_config_strategy_params_unchanged(runner_harness_module):
    """CONFIG strategy params byte-identical (main is single source of truth)."""
    main = runner_harness_module["main"]
    cfg = main.CONFIG
    assert cfg["mechanic_family"] == "zscore_bollinger_mean_reversion_exit_to_mean"
    assert cfg["lookback_L"] == 20
    assert cfg["entry_band_k_sigma"] == 2.0
    assert cfg["exit_rule"] == "EXIT_TO_MEAN"
    assert cfg["catastrophe_stop_sigma_multiple"] == 3.5
    assert cfg["catastrophe_stop_is_fixed_2N"] is False
    assert cfg["time_stop_max_hold_bars"] == 10
    assert cfg["sizing_method"] == "vol_normalized"
    assert cfg["risk_pct_per_trade"] == 0.005
    assert cfg["max_total_positions"] == 3
    assert cfg["max_positions_per_name"] == 1
    assert cfg["start_cash_usd"] == 100_000
    assert cfg["warmup_days"] == 30
    assert cfg["verdict_min_closed_trades"] == 100
    assert cfg["adjustment_convention"] == "split_only"
    assert cfg["data_vendor"] == "tiingo"
    assert cfg["rec1_equivalent_binding"] is True


def test_oos_run_function_signature_matches_is(runner_harness_module):
    is_driver = runner_harness_module["in_sample_driver"]
    oos_driver = runner_harness_module["out_of_sample_driver"]
    assert str(inspect.signature(is_driver.run_in_sample)) == str(inspect.signature(oos_driver.run_out_of_sample))


def test_oos_driver_no_top_level_forbidden_imports(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    source = pathlib.Path(inspect.getfile(oos)).read_text(encoding="utf-8")
    forbidden = (
        r"^import\s+tiingo", r"^from\s+tiingo\s+import",
        r"^import\s+databento", r"^from\s+databento\s+import",
        r"^import\s+AlgorithmImports", r"^from\s+AlgorithmImports\s+import",
        r"^import\s+QuantConnect", r"^from\s+QuantConnect\s+import",
    )
    for pattern in forbidden:
        assert re.search(pattern, source, flags=re.MULTILINE) is None


def test_oos_driver_tiingo_reference_is_not_top_level_import(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    source = pathlib.Path(inspect.getfile(oos)).read_text(encoding="utf-8")
    for line_no, line in enumerate(source.splitlines(), start=1):
        if "tiingo" in line.lower():
            stripped = line.lstrip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                assert line != stripped, f"tiingo import at module top level on line {line_no}: {line!r}"


def test_oos_driver_does_not_instantiate_vendor_client(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    source = pathlib.Path(inspect.getfile(oos)).read_text(encoding="utf-8")
    forbidden = (r"\bTiingoClient\s*\(", r"\btiingo\.\w+\s*\(", r"\bdb\.Historical\s*\(", r"\bHistorical\s*\(")
    for pattern in forbidden:
        assert re.search(pattern, source) is None


def test_is_driver_has_three_csv_registry(runner_harness_module):
    is_driver = runner_harness_module["in_sample_driver"]
    assert set(is_driver.CSV_REGISTRY.keys()) == {"AAPL", "JPM", "XOM"}
    assert is_driver.IN_SAMPLE_START == datetime.date(2019, 1, 2)
    assert is_driver.IN_SAMPLE_END == datetime.date(2023, 12, 29)

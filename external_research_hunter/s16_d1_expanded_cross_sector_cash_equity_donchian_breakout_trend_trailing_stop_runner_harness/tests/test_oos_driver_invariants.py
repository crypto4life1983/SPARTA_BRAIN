"""OOS driver invariants tests for s16-d1 Donchian trend runner harness."""

import datetime
import inspect
import pathlib
import re

EXPECT_12 = {"AAPL", "MSFT", "NVDA", "JPM", "XOM", "UNH", "WMT", "KO", "META", "AMZN", "JNJ", "CVX"}


def test_oos_driver_registry_points_to_12_csvs(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    assert set(oos.CSV_REGISTRY.keys()) == EXPECT_12
    assert oos.CSV_REGISTRY["AMZN"]["sha256"] == "d10f4e5ad48e030e769e3d6e1a2228be15d2369850151e75ef050533f63d0317"
    assert oos.CSV_REGISTRY["WMT"]["sha256"] == "aa772f962f3afc712e9b9339b01c0b1f1fcd7cc02bf5ad276c035e1c321a8742"


def test_oos_driver_window_2024_2025(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    assert oos.OUT_OF_SAMPLE_START == datetime.date(2024, 1, 2)
    assert oos.OUT_OF_SAMPLE_END == datetime.date(2025, 12, 30)


def test_oos_driver_no_is_window_constants(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    assert not hasattr(oos, "IN_SAMPLE_START") and not hasattr(oos, "IN_SAMPLE_END")


def test_oos_driver_no_is_year_tokens_in_source(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    source = pathlib.Path(inspect.getfile(oos)).read_text(encoding="utf-8")
    assert re.search(r"\b2019\b", source) is None
    assert re.search(r"\b2023\b", source) is None


def test_oos_driver_no_run_in_sample(runner_harness_module):
    assert not hasattr(runner_harness_module["out_of_sample_driver"], "run_in_sample")


def test_both_drivers_use_same_main(runner_harness_module):
    import sys
    pkg = ("external_research_hunter."
           "s16_d1_expanded_cross_sector_cash_equity_donchian_breakout_trend_trailing_stop_runner_harness")
    assert sys.modules.get(pkg + ".main") is runner_harness_module["main"]


def test_runner_config_strategy_params_unchanged(runner_harness_module):
    cfg = runner_harness_module["main"].CONFIG
    assert cfg["mechanic_family"] == "donchian_breakout_trend_trailing_stop"
    assert cfg["n_entry_donchian"] == 20 and cfg["n_exit_donchian_trailing"] == 10
    assert cfg["exit_rule"] == "TRAILING_DONCHIAN_CHANNEL"
    assert cfg["initial_catastrophe_stop_atr_multiple"] == 2.0 and cfg["stop_is_tight_mean_reversion_stop"] is False
    assert cfg["atr_period"] == 14 and cfg["sizing_method"] == "vol_normalized"
    assert cfg["risk_pct_per_trade"] == 0.005 and cfg["start_cash_usd"] == 100_000
    assert cfg["max_total_positions"] == 6 and cfg["max_positions_per_name"] == 1
    assert cfg["warmup_days"] == 40 and cfg["verdict_min_closed_trades"] == 100
    assert cfg["adjustment_convention"] == "split_only" and cfg["data_vendor"] == "tiingo"
    assert cfg["rec1_equivalent_binding"] is True


def test_oos_run_signature_matches_is(runner_harness_module):
    is_d = runner_harness_module["in_sample_driver"]; oos_d = runner_harness_module["out_of_sample_driver"]
    assert str(inspect.signature(is_d.run_in_sample)) == str(inspect.signature(oos_d.run_out_of_sample))


def test_oos_driver_no_top_level_forbidden_imports(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    source = pathlib.Path(inspect.getfile(oos)).read_text(encoding="utf-8")
    for pat in (r"^import\s+tiingo", r"^from\s+tiingo\s+import", r"^import\s+databento",
                r"^import\s+AlgorithmImports", r"^import\s+QuantConnect"):
        assert re.search(pat, source, flags=re.MULTILINE) is None


def test_oos_driver_no_vendor_client_instantiation(runner_harness_module):
    oos = runner_harness_module["out_of_sample_driver"]
    source = pathlib.Path(inspect.getfile(oos)).read_text(encoding="utf-8")
    for pat in (r"\bTiingoClient\s*\(", r"\btiingo\.\w+\s*\(", r"\bHistorical\s*\("):
        assert re.search(pat, source) is None


def test_is_driver_has_12_csv_registry(runner_harness_module):
    is_d = runner_harness_module["in_sample_driver"]
    assert set(is_d.CSV_REGISTRY.keys()) == EXPECT_12
    assert is_d.IN_SAMPLE_START == datetime.date(2019, 1, 2) and is_d.IN_SAMPLE_END == datetime.date(2023, 12, 29)

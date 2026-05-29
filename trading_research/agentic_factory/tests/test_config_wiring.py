"""Verify factory_loop pulls strategy params from config, not base defaults."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from loop import factory_loop  # noqa: E402


def test_run_once_uses_config_strategy(tmp_path):
    # CSV path intentionally missing -> run_once returns 'no_data' but still
    # echoes the params it would have used, which must come from the config
    # strategy block (not the 09:30/16:00 base defaults).
    cfg_text = (
        "data:\n"
        '  offline_csv: "does_not_exist_smoke_check.csv"\n'
        '  timestamp_column: "ts_event"\n'
        "strategy:\n"
        '  name: "nq_orb"\n'
        "  opening_range_minutes: 15\n"
        '  session_start: "14:30"\n'
        '  session_end: "21:00"\n'
    )
    cfg_file = tmp_path / "cfg.yaml"
    cfg_file.write_text(cfg_text)

    out = factory_loop.run_once(config_path=str(cfg_file))

    assert out["status"] == "no_data"
    assert out["params"]["session_start"] == "14:30"
    assert out["params"]["session_end"] == "21:00"
    assert out["params"]["opening_range_minutes"] == 15


def test_load_config_includes_strategy_block():
    cfg = factory_loop._load_config("config/factory_config.yaml")
    assert "strategy" in cfg
    assert cfg["strategy"]["session_start"] == "14:30"
    assert cfg["strategy"]["session_end"] == "21:00"
    assert cfg["data"]["timestamp_column"] == "ts_event"

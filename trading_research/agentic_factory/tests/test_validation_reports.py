"""Tests for the Factory-D2 validation report schema + writer.

Covers the standard validation-report structure contract: a valid minimal report
passes; missing fields and wrong types are reported; the writer emits a
deterministic report.json + report.md, refuses-before-write on invalid input
(no partial artifacts), creates nested output dirs, renders title/verdict/
forbidden-actions into the markdown, round-trips nested metrics/frozen params
through JSON, and the module source is offline/inert (no network/broker/
subprocess tokens).

Offline only. This exercises STRUCTURE, never trading performance, and runs no
strategy, backtest, IS/OOS, optimization, or data fetch.
"""

import json
import os

import pytest

from engine import validation_reports as VR


def _minimal_report():
    """A structurally valid report with explicit created_utc (so repeat writes
    are byte-identical -- no implicit timestamp)."""
    return VR.make_report(
        branch_id="S29",
        module_id="is_baseline",
        title="Test Report",
        status="COMPLETE",
        verdict="PARK",
        created_utc="2026-05-30T00:00:00+00:00",
        forbidden_actions=["no_oos_peek", "no_optimization"],
    )


# 1 -- a valid minimal report passes validation (empty error list).
def test_valid_minimal_report_passes():
    assert VR.validate_report(_minimal_report()) == []


# 2 -- a missing required field fails validation.
def test_missing_field_fails():
    rep = _minimal_report()
    del rep["verdict"]
    errors = VR.validate_report(rep)
    assert any("verdict" in e for e in errors)


# 3 -- a wrong-typed field fails validation.
def test_wrong_type_fails():
    rep = _minimal_report()
    rep["metrics"] = ["not", "a", "dict"]  # metrics must be a dict
    errors = VR.validate_report(rep)
    assert any("metrics" in e for e in errors)


# 3b -- bool is rejected where a non-bool type is required (bool is int subclass).
def test_bool_where_str_required_fails():
    rep = _minimal_report()
    rep["status"] = True
    errors = VR.validate_report(rep)
    assert any("status" in e and "bool" in e for e in errors)


# 4 -- write_report creates both report.json and report.md.
def test_write_report_creates_both_files(tmp_path):
    out = str(tmp_path / "rep")
    paths = VR.write_report(_minimal_report(), out)
    assert os.path.isfile(paths["report_json"])
    assert os.path.isfile(paths["report_md"])
    assert os.path.basename(paths["report_json"]) == "report.json"
    assert os.path.basename(paths["report_md"]) == "report.md"


# 5 -- JSON is valid and deterministic for repeat writes with the same input.
def test_json_valid_and_deterministic(tmp_path):
    rep = _minimal_report()
    out_a = str(tmp_path / "a")
    out_b = str(tmp_path / "b")
    VR.write_report(rep, out_a)
    VR.write_report(rep, out_b)
    with open(os.path.join(out_a, "report.json"), "r", encoding="utf-8") as fh:
        text_a = fh.read()
    with open(os.path.join(out_b, "report.json"), "r", encoding="utf-8") as fh:
        text_b = fh.read()
    # Valid JSON ...
    assert json.loads(text_a) == rep
    # ... and byte-identical across writes of the same input.
    assert text_a == text_b


# 6 -- markdown contains title, verdict, and forbidden actions.
def test_markdown_contains_key_fields():
    md = VR.render_markdown(_minimal_report())
    assert "Test Report" in md
    assert "PARK" in md
    assert "no_oos_peek" in md
    assert "no_optimization" in md


# 7 -- write_report refuses an invalid report and leaves no partial files.
def test_refuses_invalid_and_no_partial_files(tmp_path):
    rep = _minimal_report()
    del rep["title"]  # now structurally invalid
    out = str(tmp_path / "should_not_exist")
    with pytest.raises(ValueError):
        VR.write_report(rep, out)
    # Refuse-before-write: the directory must not have been created.
    assert not os.path.exists(out)


# 8 -- module source has no network/broker/subprocess/import-risk tokens.
#      NOTE: "git" is intentionally NOT in this list -- the module docstring
#      legitimately says "runs no git command".
def test_module_source_is_offline_inert():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_reports.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "subprocess", "socket", "urllib", "requests", "httpx", "aiohttp",
        "websockets", "ccxt", "binance", "bybit", "alpaca", "ib_insync",
        "broker", "api_key", "os.system", "exec(", "eval(",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in module source: {hits}"


# 9 -- output_dir creation works for a nested, non-existent path.
def test_nested_output_dir_creation(tmp_path):
    out = str(tmp_path / "deep" / "nested" / "missing" / "rep")
    paths = VR.write_report(_minimal_report(), out)
    assert os.path.isfile(paths["report_json"])
    assert os.path.isfile(paths["report_md"])


# 10 -- nested metrics / frozen parameters survive a JSON round-trip.
def test_nested_values_survive_json_roundtrip(tmp_path):
    rep = VR.make_report(
        branch_id="S29",
        module_id="is_baseline",
        title="Nested Test",
        status="COMPLETE",
        verdict="CONTINUE",
        created_utc="2026-05-30T00:00:00+00:00",
        metrics={
            "trade_count": 12,
            "year_by_year_r": {"2014": 2.0, "2015": -1.0},
            "exit_reasons": ["target", "stop", "time_stop"],
        },
        frozen_parameters={
            "EMA_MID": 50,
            "nested": {"a": [1, 2, 3], "b": {"c": True}},
        },
    )
    out = str(tmp_path / "rep")
    VR.write_report(rep, out)
    with open(os.path.join(out, "report.json"), "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    assert loaded["metrics"] == rep["metrics"]
    assert loaded["frozen_parameters"] == rep["frozen_parameters"]
    assert loaded["frozen_parameters"]["nested"]["b"]["c"] is True

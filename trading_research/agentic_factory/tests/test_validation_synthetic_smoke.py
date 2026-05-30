"""Tests for the Factory-D10 synthetic end-to-end validation smoke demo.

Covers sub-folder creation, report.json/report.md presence + schema validity, the
manifest module list, refusal of an empty output dir, an offline-source token scan
+ a no-real-data scan, the fake/deterministic strategy runner, the conservative
final readiness level, the absence of any paper/live/deploy language, and a
two-temp-dir repeat run.

Fake synthetic data only. No real NQ/ES CSVs are read; no real strategy engine is
imported; no real in-sample / out-of-sample market data is used.
"""

import json
import os

import pytest

from engine import validation_synthetic_smoke as SM
from engine import validation_reports as VR


# 1 -- the smoke run creates one sub-folder per expected module.
def test_creates_expected_subfolders(tmp_path):
    dest = str(tmp_path / "run")
    manifest = SM.run_synthetic_validation_smoke(dest)
    for name in SM.EXPECTED_MODULES:
        assert os.path.isdir(os.path.join(dest, name)), f"missing subfolder: {name}"
    assert set(manifest["paths"].keys()) == set(SM.EXPECTED_MODULES)


# 2 -- each module sub-folder contains report.json and report.md.
def test_each_subfolder_has_reports(tmp_path):
    dest = str(tmp_path / "run")
    SM.run_synthetic_validation_smoke(dest)
    for name in SM.EXPECTED_MODULES:
        assert os.path.isfile(os.path.join(dest, name, "report.json"))
        assert os.path.isfile(os.path.join(dest, name, "report.md"))


# 3 -- every written report is structurally valid against the D2 schema.
def test_all_reports_valid(tmp_path):
    dest = str(tmp_path / "run")
    SM.run_synthetic_validation_smoke(dest)
    for name in SM.EXPECTED_MODULES:
        with open(os.path.join(dest, name, "report.json"), "r", encoding="utf-8") as fh:
            report = json.load(fh)
        assert VR.validate_report(report) == [], f"{name} report invalid"


# 4 -- the manifest lists all expected modules and a verdict for each.
def test_manifest_lists_all_modules(tmp_path):
    dest = str(tmp_path / "run")
    manifest = SM.run_synthetic_validation_smoke(dest)
    assert manifest["modules"] == SM.EXPECTED_MODULES
    for name in SM.EXPECTED_MODULES:
        assert name in manifest["verdicts"]
    assert manifest["synthetic"] is True


# 5 -- the smoke refuses a missing / empty output dir.
def test_refuses_empty_output_dir():
    with pytest.raises(ValueError):
        SM.run_synthetic_validation_smoke("")
    with pytest.raises(ValueError):
        SM.run_synthetic_validation_smoke("   ")


# 6 -- the module source reads no real market data (no CSV/data-loading tokens).
def test_module_reads_no_real_data():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_synthetic_smoke.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    for token in [".csv", "data_offline", "load_daily_bars", "load_yearly_csvs", "open("]:
        assert token not in text, f"module references real-data token: {token}"


# 7 -- the demo uses fake synthetic data only (in-memory bars within 2013-2025).
def test_uses_fake_synthetic_data_only():
    bars = SM.make_synthetic_bars()
    assert set(bars.keys()) == {"is", "oos"}
    is_years = {b["timestamp"].year for b in bars["is"]}
    oos_years = {b["timestamp"].year for b in bars["oos"]}
    assert is_years == set(SM.IS_YEARS)
    assert oos_years == set(SM.OOS_YEARS)
    # bars are plain in-memory dicts, not loaded from any path.
    assert all(isinstance(b, dict) and "close" in b for b in bars["is"])


# 8 -- the final-decision report exists and carries a conservative readiness level.
def test_final_decision_conservative_readiness(tmp_path):
    dest = str(tmp_path / "run")
    manifest = SM.run_synthetic_validation_smoke(dest)
    with open(os.path.join(dest, "final_decision", "report.json"), "r", encoding="utf-8") as fh:
        report = json.load(fh)
    readiness = report["metrics"]["readiness_level"]
    assert readiness == manifest["readiness_level"]
    # research-tier only -- the demo can never reach any paper/live tier.
    assert readiness in {"BLOCKED", "RESEARCH_CANDIDATE", "VALIDATION_CANDIDATE"}
    assert readiness not in {"PAPER_REVIEW_CANDIDATE", "PAPER_READY", "LIVE_READY"}


# 9 -- module source is offline/inert (no network/exec/dynamic-import/VC tokens).
def test_module_source_is_offline_inert():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_synthetic_smoke.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    forbidden = [
        "subprocess", "socket", "urllib", "requests", "httpx", "aiohttp",
        "websockets", "ccxt", "binance", "bybit", "alpaca", "ib_insync",
        "broker", "api_key", "os.system", "exec(", "eval(",
        "importlib", "__import__", "git",
    ]
    hits = [tok for tok in forbidden if tok in text]
    assert hits == [], f"forbidden tokens in module source: {hits}"


# 10 -- no paper/live/deploy language anywhere in the module source.
def test_no_paper_live_deploy_language():
    mod_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "engine", "validation_synthetic_smoke.py",
    )
    with open(mod_path, "r", encoding="utf-8") as fh:
        text = fh.read().lower()
    for token in ["paper", "live", "deploy"]:
        assert token not in text, f"module implies operational readiness: {token}"


# 11 -- the synthetic strategy runner is fake and deterministic.
def test_strategy_runner_fake_and_deterministic():
    bars = SM.make_synthetic_bars()["is"]
    a = SM.synthetic_strategy_runner(bars)
    b = SM.synthetic_strategy_runner(bars)
    assert a == b
    assert len(a) > 0
    # every trade is a plain synthetic dict with an R-multiple and an entry index.
    for t in a:
        assert "r_multiple" in t and "entry_index" in t and "year" in t


# 12 -- running the smoke twice into different temp dirs both succeed.
def test_two_independent_runs(tmp_path):
    d1 = str(tmp_path / "run_a")
    d2 = str(tmp_path / "run_b")
    m1 = SM.run_synthetic_validation_smoke(d1)
    m2 = SM.run_synthetic_validation_smoke(d2)
    assert m1["modules"] == m2["modules"]
    assert os.path.isfile(os.path.join(d1, "final_decision", "report.json"))
    assert os.path.isfile(os.path.join(d2, "final_decision", "report.json"))
    # deterministic: same verdicts both runs.
    assert m1["verdicts"] == m2["verdicts"]

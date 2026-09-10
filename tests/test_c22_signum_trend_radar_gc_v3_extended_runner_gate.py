"""C22 V3_EXTENDED runner: profiles are frozen, gate is fail-closed, V2 is never replaced,
post-cutoff windows are tagged EXIT_ONLY, dry run writes nothing."""
from __future__ import annotations

import importlib
import inspect
import json

import pytest

runner = importlib.import_module(
    "tools.c22_signum_trend_radar_gc_v3_extended_multi_window_real_candle_labels_once")
v2run = importlib.import_module(
    "tools.c22_signum_trend_radar_gc_v2_range_multi_window_real_candle_labels_once")
TOKEN = "HUMAN_APPROVED_BUILD_C22_V3_EXTENDED_LABEL_EVIDENCE_ONLY"
V2_TOKEN = "HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"


def test_profiles_are_frozen_and_arithmetically_consistent():
    assert set(runner.RUN_PROFILES) == {"V3_EXTENDED_82W", "V3_EXTENDED_SEG_A_57W", "V3_EXTENDED_SEG_B_24W"}
    p = runner.RUN_PROFILES["V3_EXTENDED_82W"]
    assert (p["start"], p["end"], p["windows"], p["rows"], p["total"]) == ("2026-06-20", "2026-09-09", 82, 50, 4100)
    a = runner.RUN_PROFILES["V3_EXTENDED_SEG_A_57W"]
    assert (a["start"], a["end"], a["windows"], a["total"]) == ("2026-06-20", "2026-08-15", 57, 2850)
    b = runner.RUN_PROFILES["V3_EXTENDED_SEG_B_24W"]
    assert (b["start"], b["end"], b["windows"], b["total"]) == ("2026-08-17", "2026-09-09", 24, 1200)
    for q in runner.RUN_PROFILES.values():
        assert q["windows"] * q["rows"] == q["total"]


def test_entry_cutoff_is_the_accepted_spec_cutoff_and_never_moved():
    assert runner.ENTRY_CUTOFF == "2026-07-15"
    assert runner.MISSING_ADMITTED_WINDOW == "2026-08-16"


def test_gate_refuses_without_option_or_token_and_rejects_v2_token():
    assert runner.authorize_v3_write(False, None)["authorized"] is False
    assert runner.authorize_v3_write(True, None)["reason"] == "missing_v3_build_token"
    assert runner.authorize_v3_write(False, TOKEN)["authorized"] is False
    r = runner.authorize_v3_write(True, V2_TOKEN)
    assert r["authorized"] is False and r["reason"] == "wrong_v3_build_token"


def test_gate_option_plus_exact_token_authorized():
    assert runner.authorize_v3_write(True, TOKEN)["authorized"] is True


def test_gate_signature_cannot_consult_execution_flags():
    assert list(inspect.signature(runner.authorize_v3_write).parameters) == ["execute_build", "token"]


def test_v3_output_dir_is_separate_from_v2_and_names_cannot_collide():
    assert runner.OUT_DIR != v2run.OUT_DIR
    assert runner.OUT_DIR.parent == v2run.OUT_DIR
    v2_name = v2run._v2.v2_artifact_filename(v2run.RUN_START, v2run.RUN_END, v2run.RUN_EXPECTED_WINDOWS)
    for prof in runner.RUN_PROFILES:
        assert runner.artifact_name_for(prof) != v2_name
        assert "_v2_" in runner.artifact_name_for(prof)   # V2 validator requires the v2 basename
    assert runner.artifact_name_for("V3_EXTENDED_82W") == \
        "c22_gc_real_candle_entry_labels_multiwindow_v2_82w_2026-06-20_2026-09-09.json"


def test_source_date_inventory_tags_post_cutoff_windows_exit_only():
    record = {"per_window": [
        {"run_date": "2026-07-15", "reduced_sha256": "a", "provenance_tier": "T", "row_count": 50, "label_counts": {}},
        {"run_date": "2026-07-16", "reduced_sha256": "b", "provenance_tier": "T", "row_count": 50, "label_counts": {}},
        {"run_date": "2026-07-18", "reduced_sha256": "c", "provenance_tier": "T", "row_count": 50, "label_counts": {}},
    ], "expected_dates": ["2026-07-15", "2026-07-16", "2026-07-17", "2026-07-18"]}
    inv = runner.source_date_inventory(record, [])
    roles = {w["run_date"]: w["role"] for w in inv["windows"]}
    assert roles == {"2026-07-15": "ENTRY_WINDOW_UNDER_ACCEPTED_SPEC", "2026-07-16": "EXIT_ONLY", "2026-07-18": "EXIT_ONLY"}
    assert inv["expected_dates_absent"] == ["2026-07-17"]
    assert inv["exit_only_window_count"] == 2
    assert inv["weekend_window_count"] == 1          # 2026-07-18 is a Saturday


def test_dry_run_profile_reports_without_writing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(runner, "OUT_DIR", tmp_path)
    rc = runner.main(["--profile", "V3_EXTENDED_SEG_B_24W"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["mode"] == "DRY_RUN_MANIFEST_ONLY" and out["artifact_written"] is False
    assert out["expected_windows"] == 24 and out["exit_only_window_count"] == out["windows_seen"]
    assert out["replay_authorized"] is False and out["execution_authorized"] is False
    assert list(tmp_path.glob("*.json")) == []   # conftest may create _iso_reports/; the runner must not


def test_token_without_option_still_writes_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(runner, "OUT_DIR", tmp_path)
    runner.main(["--profile", "V3_EXTENDED_SEG_B_24W", "--build-token", TOKEN])
    assert json.loads(capsys.readouterr().out)["artifact_written"] is False
    assert list(tmp_path.glob("*.json")) == []   # conftest may create _iso_reports/; the runner must not


def test_build_refuses_overwrite(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(runner, "OUT_DIR", tmp_path)
    runner.main(["--profile", "V3_EXTENDED_SEG_B_24W", "--execute-build", "--build-token", TOKEN])
    first = json.loads(capsys.readouterr().out)
    if not first["artifact_written"]:
        pytest.skip("segment B not buildable in this checkout: %s" % first.get("build_refused"))
    with pytest.raises(RuntimeError):
        runner.main(["--profile", "V3_EXTENDED_SEG_B_24W", "--execute-build", "--build-token", TOKEN])

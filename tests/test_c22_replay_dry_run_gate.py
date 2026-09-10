"""C22 no-P&L dry run: SHA-pinned V2 cohort, 88-signal reconciliation under both profiles, no
performance, no profile selection, token-gated write, refuses overwrite."""
from __future__ import annotations

import importlib
import inspect
import json

import pytest

dr = importlib.import_module("tools.c22_replay_dry_run_once")
TOKEN = "HUMAN_APPROVED_BUILD_C22_REPLAY_DRY_RUN_NO_PNL"


def test_gate_requires_option_and_exact_token():
    assert dr.authorize_write(False, None)["authorized"] is False
    assert dr.authorize_write(True, None)["reason"] == "missing_dry_run_token"
    assert dr.authorize_write(True, "HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT")["reason"] == "wrong_dry_run_token"
    assert dr.authorize_write(True, TOKEN)["authorized"] is True
    assert list(inspect.signature(dr.authorize_write).parameters) == ["execute_build", "token"]


def test_v2_cohort_is_sha_pinned_and_exactly_88(tmp_path):
    sigs, sha = dr.load_frozen_v2_signals()
    assert sha == dr.V2_FROZEN_SHA256 and len(sigs) == 88
    assert all(s["decision_date"] <= "2026-07-15" for s in sigs)
    bad = tmp_path / "x.json"
    bad.write_text("{}", encoding="utf-8")
    with pytest.raises(RuntimeError):
        dr.load_frozen_v2_signals(bad)


@pytest.fixture(scope="module")
def report():
    return dr.build_dry_run()


def test_dry_run_reconciles_all_88_under_both_profiles_without_pnl(report):
    assert report["performance_computed"] is False and report["profile_selected"] is None
    assert report["decisive_replay_can_run"] is False and report["fee_honest_replayable_now"] == 0
    for p in ("V2_CONTRACT_EXACT", "CRYPTO_CALENDAR_SENSITIVITY"):
        pr = report["profiles"][p]
        rc = pr["reconciliation"]
        assert rc["source_signals"] == 88 and rc["records"] == 88
        assert rc["every_signal_has_exactly_one_record"] and rc["no_silent_drops"]
        assert rc["lifecycle_total"] == 88
        assert pr["ledger_snapshot"]["realized_pnl"] == 0.0 and pr["ledger_snapshot"]["unrealized_pnl"] == 0.0
        assert pr["ledger_validation"]["valid"]
        assert pr["performance_conclusion"] == "NOT_COMPUTED_PNL_DISABLED"
        assert rc["instrument_unverified_records"] == 88
        for rec in pr["records"]:
            assert "pnl" not in rec and "realized" not in rec
            assert rec["lifecycle_status"] in ("PENDING_ENTRY", "OPEN", "CLOSED", "REJECTED", "DATA_GAP",
                                               "MISSING_EXECUTION_PRICE", "INSTRUMENT_UNVERIFIED", "OPEN_AT_END_OF_DATA")


def test_weekend_differences_are_explicit_and_not_selected(report):
    d = report["weekend_profile_differences"]
    assert d["profile_a"] == "V2_CONTRACT_EXACT" and d["profile_b"] == "CRYPTO_CALENDAR_SENSITIVITY"
    assert d["signals_compared"] == 88
    assert isinstance(d["differences"], list) and all({"signal_id", "field", "a", "b"} <= set(x) for x in d["differences"])
    assert report["profiles"]["CRYPTO_CALENDAR_SENSITIVITY"]["role"].startswith("DIAGNOSTIC_SENSITIVITY_ONLY")


def test_open_at_end_of_data_never_force_closed(report):
    for p in report["profiles"].values():
        for x in p["reconciliation"]["positions_open_at_end_of_data"]:
            rec = [r for r in p["records"] if r["signal_id"] == x["signal_id"]][0]
            assert rec["exit_date"] is None and rec["exit_price"] is None
            assert rec["mark_to_market"]["decisive"] is False


def test_missing_evidence_lists_every_required_instrument(report):
    f = report["instrument_feasibility_requirements"]
    sigs, _ = dr.load_frozen_v2_signals()
    assert f["count"] == len({s["symbol"] for s in sigs})
    assert f["short_instruments"] == 22 and f["acquisition_status"] == "NOT_AUTHORIZED"
    assert all(x["fail_closed"] for x in f["instruments"])
    m = report["missing_external_evidence"]
    assert len(m["short_instrument_evidence_for"]) == 22
    assert m["cost_base_case"]["status"] == "C22_COST_BASE_CASE_NOT_FROZEN"


def test_deterministic_rerun_equality(report):
    again = dr.build_dry_run()
    assert dr.canonical_bytes(report) == dr.canonical_bytes(again)


def test_main_stdout_only_without_token(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(dr, "REPORT_DIR", tmp_path)
    dr.main([])
    out = json.loads(capsys.readouterr().out)
    assert out["written"] is False and list(tmp_path.glob("*.json")) == []


def test_write_refuses_overwrite(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(dr, "REPORT_DIR", tmp_path)
    dr.main(["--execute-build", "--build-token", TOKEN])
    assert json.loads(capsys.readouterr().out)["written"] is True
    with pytest.raises(RuntimeError):
        dr.main(["--execute-build", "--build-token", TOKEN])

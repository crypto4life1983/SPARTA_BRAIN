"""Tests for the Crypto-D1 Real Data QA PASS receipt / baseline-prep gate. Pure,
read-only; the qa_report.json used by the cross-check test is a FAKE in-memory
file under tmp_path."""

from __future__ import annotations

import ast
import json
import os

import sparta_commander.strategy_factory_crypto_d1_real_data_qa_pass_receipt as rc


def test_receipt_is_pass_and_records_evidence():
    r = rc.build_qa_pass_receipt()
    assert r["verdict"] == rc.VERDICT_PASS
    assert r["source_tag"] == "binance_usdt_spot_frozen_regime_inputs"
    assert [s["symbol"] for s in r["per_symbol"]] == ["BTC", "ETH", "SOL"]
    btc = next(s for s in r["per_symbol"] if s["symbol"] == "BTC")
    assert btc["row_count"] == 2351 and btc["last_date"] == "2026-06-08"
    assert all(len(s["sha256"]) == 64 for s in r["per_symbol"])


def test_receipt_unlocks_nothing():
    r = rc.build_qa_pass_receipt()
    assert r["real_data_qa_blocked"] is True
    assert r["baseline_backtest_blocked"] is True
    assert r["paper_trading_gate_locked"] is True
    assert r["micro_live_gate_locked"] is True
    assert r["executes"] is False
    assert r["runs_baseline"] is False
    assert r["authorizes_baseline_backtest"] is False
    assert r["baseline_is_human_gated"] is True
    assert r["real_data_qa_gate_state"] == "BLOCKED_PENDING_HUMAN_BASELINE_PREP_POLICY"


def test_next_required_action_is_gated_baseline_prep():
    r = rc.build_qa_pass_receipt()
    assert r["next_required_action"] == "HUMAN_APPROVED_BASELINE_BACKTEST_PREP_GATE"
    assert rc.NEXT_REQUIRED_ACTION == "HUMAN_APPROVED_BASELINE_BACKTEST_PREP_GATE"


def test_validate_passes_on_built_receipt():
    v = rc.validate_qa_pass_receipt(rc.build_qa_pass_receipt())
    assert v["valid"] is True and v["errors"] == []


def test_validate_rejects_unlocked_gate():
    bad = rc.build_qa_pass_receipt()
    bad["paper_trading_gate_locked"] = False
    v = rc.validate_qa_pass_receipt(bad)
    assert v["valid"] is False
    assert any("gate_not_locked" in e for e in v["errors"])


def test_validate_rejects_authorized_baseline():
    bad = rc.build_qa_pass_receipt()
    bad["authorizes_baseline_backtest"] = True
    v = rc.validate_qa_pass_receipt(bad)
    assert v["valid"] is False
    assert any("capability_not_false" in e for e in v["errors"])


def test_validate_rejects_non_dict():
    v = rc.validate_qa_pass_receipt("not a dict")
    assert v["valid"] is False


def _write_qa_report(tmp_path, verdict="PASS", shas=None):
    shas = shas or {e["symbol"]: e["sha256"] for e in rc.RECEIPT_EVIDENCE}
    report = {
        "verdict": verdict,
        "per_symbol": [
            {"symbol": sym, "provenance": {"sha256": sha}}
            for sym, sha in shas.items()
        ],
    }
    p = tmp_path / "reports" / "crypto_d1_real_data_qa"
    p.mkdir(parents=True, exist_ok=True)
    (p / "qa_report.json").write_text(json.dumps(report), encoding="utf-8")


def test_verify_against_qa_report_matches(tmp_path):
    _write_qa_report(tmp_path)
    res = rc.verify_against_qa_report(repo_root=str(tmp_path))
    assert res["report_found"] is True
    assert res["verdict_matches"] is True
    assert res["sha256_matches"] is True
    assert res["mismatches"] == []


def test_verify_flags_missing_report(tmp_path):
    res = rc.verify_against_qa_report(repo_root=str(tmp_path))
    assert res["report_found"] is False
    assert "qa_report_missing" in res["mismatches"]


def test_verify_flags_sha_mismatch(tmp_path):
    shas = {e["symbol"]: e["sha256"] for e in rc.RECEIPT_EVIDENCE}
    shas["BTC"] = "0" * 64
    _write_qa_report(tmp_path, shas=shas)
    res = rc.verify_against_qa_report(repo_root=str(tmp_path))
    assert res["sha256_matches"] is False
    assert any("sha256_mismatch:BTC" in m for m in res["mismatches"])


def test_render_markdown_is_string():
    md = rc.render_qa_pass_receipt_markdown(rc.build_qa_pass_receipt())
    assert md.startswith("# Crypto-D1 Real Data QA PASS Receipt")
    assert "BLOCKED" in md and "LOCKED" in md
    assert "HUMAN_APPROVED_BASELINE_BACKTEST_PREP_GATE" in md


def test_module_imports_no_network_or_credential_modules():
    with open(rc.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {
        "urllib",
        "requests",
        "socket",
        "http",
        "ftplib",
        "ccxt",
        "databento",
        "dotenv",
        "smtplib",
    }
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)


def test_surfaced_in_mission_flow_status():
    import sparta_commander.strategy_factory_mission_flow_status as mf

    status = mf.get_mission_flow_status()
    assert status["latest_completed_real_data_qa_pass_receipt"] == rc.RECEIPT_LABEL
    # gates remain blocked/locked in the surfaced status
    gates = {g["id"]: g for g in status["blocked_gates"]}
    assert gates["real_data_qa"]["state"] == "BLOCKED"
    assert gates["baseline_backtest"]["state"] == "BLOCKED"
    assert gates["paper_trading_gate"]["state"] == "LOCKED"
    assert gates["micro_live_gate"]["state"] == "LOCKED"
    assert status["executes"] is False
    # the global pipeline pointer stays parked at the human-controlled boundary
    assert status["current_stage"] == (
        "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
    )

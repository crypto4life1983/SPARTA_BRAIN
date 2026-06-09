"""Tests for the Crypto-D1 Baseline Backtest Prep Contract (PREP ONLY). All inputs
are FAKE local files under tmp_path; no network, no credentials, no real data, and
nothing is ever run."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_baseline_backtest_prep_contract as bp
import sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner as qa

_CANON = ",".join(qa.QA_REQUIRED_FIELDS)


def _rows(sym_src: str = "binance_usdt_spot_frozen_regime_inputs") -> str:
    return "\n".join(
        [
            _CANON,
            "2024-01-01,100,110,90,105,1000," + sym_src + ",spot",
            "2024-01-02,105,115,100,108,1200," + sym_src + ",spot",
            "2024-01-03,108,120,107,118,1300," + sym_src + ",spot",
        ]
    )


def _stage_and_qa(tmp_path) -> None:
    """Stage three good CSVs and run the real QA runner so the on-disk qa_report
    and provenance reflect the staged files exactly."""
    raw = tmp_path / "data" / "crypto_d1_spot" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for sym in ("BTC", "ETH", "SOL"):
        (raw / (sym + "_1d.csv")).write_text(_rows(), encoding="utf-8")
    rep = qa.run_real_data_qa(repo_root=str(tmp_path), write=True)
    assert rep["verdict"] == qa.VERDICT_PASS


# --------------------------------------------------------------------------- #
# readiness
# --------------------------------------------------------------------------- #
def test_ready_when_staged_files_match_qa(tmp_path):
    _stage_and_qa(tmp_path)
    report = bp.check_baseline_prep_readiness(repo_root=str(tmp_path))
    assert report["verdict"] == bp.VERDICT_READY
    assert report["blockers"] == []
    assert all(s["sha256_matches_qa_report"] for s in report["per_symbol"])
    assert report["qa_report_verdict"] == qa.VERDICT_PASS


def test_not_ready_when_files_missing(tmp_path):
    report = bp.check_baseline_prep_readiness(repo_root=str(tmp_path))
    assert report["verdict"] == bp.VERDICT_NOT_READY
    assert "qa_report_missing" in report["blockers"]
    assert any("staged_file_missing" in b for b in report["blockers"])


def test_not_ready_when_file_tampered_after_qa(tmp_path):
    _stage_and_qa(tmp_path)
    # mutate BTC after QA recorded its provenance -> sha mismatch
    btc = tmp_path / "data" / "crypto_d1_spot" / "raw" / "BTC_1d.csv"
    btc.write_text(
        _rows() + "\n2024-01-04,118,130,117,125,1400,binance_usdt_spot_frozen_regime_inputs,spot",
        encoding="utf-8",
    )
    report = bp.check_baseline_prep_readiness(repo_root=str(tmp_path))
    assert report["verdict"] == bp.VERDICT_NOT_READY
    assert any("BTC:sha256_not_matching_qa_report" in b for b in report["blockers"])


# --------------------------------------------------------------------------- #
# manifest + constraints
# --------------------------------------------------------------------------- #
def test_manifest_summarizes_each_symbol(tmp_path):
    _stage_and_qa(tmp_path)
    m = bp.build_baseline_input_manifest(repo_root=str(tmp_path))
    assert [e["symbol"] for e in m["per_symbol"]] == ["BTC", "ETH", "SOL"]
    btc = next(e for e in m["per_symbol"] if e["symbol"] == "BTC")
    assert btc["schema_ok"] is True and btc["row_count"] == 3
    assert btc["first_date"] == "2024-01-01" and btc["last_date"] == "2024-01-03"


def test_constraints_forbid_optimization_and_execution():
    c = bp.baseline_run_constraints()
    assert c["optimization"] is False
    assert c["parameter_search"] is False
    assert c["allow_shorting"] is False
    assert c["allow_leverage"] is False
    assert c["long_only"] is True
    assert c["touches_broker_or_exchange"] is False


# --------------------------------------------------------------------------- #
# safety posture
# --------------------------------------------------------------------------- #
def test_prep_unlocks_nothing(tmp_path):
    _stage_and_qa(tmp_path)
    r = bp.check_baseline_prep_readiness(repo_root=str(tmp_path))
    assert r["executes"] is False
    assert r["runs_baseline"] is False
    assert r["runs_backtest"] is False
    assert r["runs_optimization"] is False
    assert r["authorizes_baseline_backtest"] is False
    assert r["baseline_backtest_blocked"] is True
    assert r["paper_trading_gate_locked"] is True
    assert r["micro_live_gate_locked"] is True
    assert r["next_required_action"] == "HUMAN_APPROVED_BASELINE_BACKTEST_RUN"


def test_validate_report_passes(tmp_path):
    _stage_and_qa(tmp_path)
    r = bp.check_baseline_prep_readiness(repo_root=str(tmp_path))
    v = bp.validate_baseline_prep_report(r)
    assert v["valid"] is True and v["errors"] == []


def test_validate_rejects_unlocked_gate(tmp_path):
    _stage_and_qa(tmp_path)
    r = bp.check_baseline_prep_readiness(repo_root=str(tmp_path))
    r["baseline_backtest_blocked"] = False
    v = bp.validate_baseline_prep_report(r)
    assert v["valid"] is False
    assert any("gate_not_locked" in e for e in v["errors"])


def test_render_markdown_is_string(tmp_path):
    _stage_and_qa(tmp_path)
    r = bp.check_baseline_prep_readiness(repo_root=str(tmp_path))
    md = bp.render_baseline_prep_markdown(r)
    assert md.startswith("# Crypto-D1 Baseline Backtest Prep (PREP ONLY)")
    assert "BLOCKED" in md and "LOCKED" in md


def test_module_imports_no_network_or_credential_modules():
    with open(bp.__file__, "r", encoding="utf-8") as fh:
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
    assert status["latest_completed_baseline_backtest_prep_contract"] == bp.PREP_LABEL
    gates = {g["id"]: g for g in status["blocked_gates"]}
    assert gates["baseline_backtest"]["state"] == "BLOCKED"
    assert gates["paper_trading_gate"]["state"] == "LOCKED"
    assert gates["micro_live_gate"]["state"] == "LOCKED"
    assert status["executes"] is False

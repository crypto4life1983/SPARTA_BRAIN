"""Tests for the Crypto-D1 Real Data QA runner. All real-data inputs here are FAKE
in-memory CSVs written under tmp_path; no network, no credentials, no real data."""

from __future__ import annotations

import ast
import json
import os

import sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner as qa

_GOOD_HEADER = "date,open,high,low,close,volume,source,instrument_type"


def _good_rows(symbol: str) -> str:
    return "\n".join(
        [
            _GOOD_HEADER,
            "2024-01-01,100,110,90,105,1000,manual_csv,spot",
            "2024-01-02,105,115,100,108,1200,manual_csv,spot",
            "2024-01-03,108,120,107,118,1300,manual_csv,spot",
        ]
    )


def _write(tmp_path, name: str, text: str) -> str:
    raw = tmp_path / "data" / "crypto_d1_spot" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    p = raw / name
    p.write_text(text, encoding="utf-8")
    return str(p)


def _stage_all_good(tmp_path) -> None:
    for sym in ("BTC", "ETH", "SOL"):
        _write(tmp_path, sym + "_1d.csv", _good_rows(sym))


# --------------------------------------------------------------------------- #
# verdicts
# --------------------------------------------------------------------------- #
def test_all_good_passes(tmp_path):
    _stage_all_good(tmp_path)
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    assert report["verdict"] == qa.VERDICT_PASS
    assert all(s["verdict"] == qa.VERDICT_PASS for s in report["per_symbol"])


def test_missing_files_need_data_fix(tmp_path):
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    assert report["verdict"] == qa.VERDICT_NEEDS_DATA_FIX
    assert all(not s["exists"] for s in report["per_symbol"])
    assert all("file_missing" in s["failures"] for s in report["per_symbol"])


def test_partial_missing_need_data_fix(tmp_path):
    _write(tmp_path, "BTC_1d.csv", _good_rows("BTC"))
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    assert report["verdict"] == qa.VERDICT_NEEDS_DATA_FIX


def test_forbidden_field_is_invalid(tmp_path):
    bad = "\n".join(
        [
            "date,open,high,low,close,volume,source,instrument_type,order",
            "2024-01-01,100,110,90,105,1000,manual_csv,spot,BUY",
        ]
    )
    _stage_all_good(tmp_path)
    _write(tmp_path, "BTC_1d.csv", bad)
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    assert report["verdict"] == qa.VERDICT_INVALID
    btc = next(s for s in report["per_symbol"] if s["symbol"] == "BTC")
    assert any("forbidden_fields" in r for r in btc["invalid_reasons"])


def test_non_spot_instrument_is_invalid(tmp_path):
    bad = "\n".join(
        [
            _GOOD_HEADER,
            "2024-01-01,100,110,90,105,1000,manual_csv,perp",
        ]
    )
    _stage_all_good(tmp_path)
    _write(tmp_path, "ETH_1d.csv", bad)
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    assert report["verdict"] == qa.VERDICT_INVALID
    eth = next(s for s in report["per_symbol"] if s["symbol"] == "ETH")
    assert "non_spot_instrument_type" in eth["invalid_reasons"]


def test_bad_ohlc_needs_data_fix(tmp_path):
    bad = "\n".join(
        [
            _GOOD_HEADER,
            "2024-01-01,100,90,110,105,1000,manual_csv,spot",
        ]
    )
    _stage_all_good(tmp_path)
    _write(tmp_path, "SOL_1d.csv", bad)
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    assert report["verdict"] == qa.VERDICT_NEEDS_DATA_FIX
    sol = next(s for s in report["per_symbol"] if s["symbol"] == "SOL")
    assert "ohlc_impossible" in sol["failures"]


def test_duplicate_and_nonascending_dates(tmp_path):
    bad = "\n".join(
        [
            _GOOD_HEADER,
            "2024-01-02,100,110,90,105,1000,manual_csv,spot",
            "2024-01-01,105,115,100,108,1200,manual_csv,spot",
            "2024-01-01,108,120,107,118,1300,manual_csv,spot",
        ]
    )
    _stage_all_good(tmp_path)
    _write(tmp_path, "BTC_1d.csv", bad)
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    btc = next(s for s in report["per_symbol"] if s["symbol"] == "BTC")
    assert "dates_not_strictly_ascending" in btc["failures"]
    assert "duplicate_dates" in btc["failures"]


def test_schema_mismatch_needs_data_fix(tmp_path):
    bad = "\n".join(["date,open,close", "2024-01-01,100,105"])
    _stage_all_good(tmp_path)
    _write(tmp_path, "BTC_1d.csv", bad)
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    btc = next(s for s in report["per_symbol"] if s["symbol"] == "BTC")
    assert "schema_header_mismatch" in btc["failures"]
    assert report["verdict"] == qa.VERDICT_NEEDS_DATA_FIX


def test_negative_volume_and_price(tmp_path):
    bad = "\n".join(
        [
            _GOOD_HEADER,
            "2024-01-01,100,110,90,105,-5,manual_csv,spot",
            "2024-01-02,0,110,90,105,100,manual_csv,spot",
        ]
    )
    _stage_all_good(tmp_path)
    _write(tmp_path, "ETH_1d.csv", bad)
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    eth = next(s for s in report["per_symbol"] if s["symbol"] == "ETH")
    assert "invalid_volume" in eth["failures"]
    assert "non_positive_price" in eth["failures"]


# --------------------------------------------------------------------------- #
# writing + provenance
# --------------------------------------------------------------------------- #
def test_write_creates_only_approved_artifacts(tmp_path):
    _stage_all_good(tmp_path)
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=True)
    for f in report["files_written"]:
        rel = os.path.relpath(f, str(tmp_path)).replace("\\", "/")
        assert rel.startswith("data/crypto_d1_spot/provenance/") or rel.startswith(
            "reports/crypto_d1_real_data_qa/"
        )
    prov = tmp_path / "data" / "crypto_d1_spot" / "provenance" / "BTC_1d.provenance.json"
    assert prov.is_file()
    data = json.loads(prov.read_text(encoding="utf-8"))
    assert data["sha256"] and data["source"] == "manual_csv"
    assert (tmp_path / "reports" / "crypto_d1_real_data_qa" / "qa_report.json").is_file()
    assert (tmp_path / "reports" / "crypto_d1_real_data_qa" / "qa_report.md").is_file()


def test_provenance_mismatch_flags(tmp_path):
    _stage_all_good(tmp_path)
    qa.run_real_data_qa(repo_root=str(tmp_path), write=True)
    # tamper the file after provenance was recorded
    _write(
        tmp_path,
        "BTC_1d.csv",
        _good_rows("BTC") + "\n2024-01-04,118,130,117,125,1400,manual_csv,spot",
    )
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    btc = next(s for s in report["per_symbol"] if s["symbol"] == "BTC")
    assert "provenance_sha256_mismatch" in btc["failures"]


def test_report_passes_validation_and_records_locked_gates(tmp_path):
    _stage_all_good(tmp_path)
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    v = qa.validate_qa_report(report)
    assert v["valid"] is True
    assert report["real_data_qa_blocked"] is True
    assert report["baseline_backtest_blocked"] is True
    assert report["paper_trading_gate_locked"] is True
    assert report["micro_live_gate_locked"] is True
    assert report["executes"] is False


# --------------------------------------------------------------------------- #
# safety: no network / credential imports
# --------------------------------------------------------------------------- #
def test_runner_imports_no_network_or_credential_modules():
    path = qa.__file__
    with open(path, "r", encoding="utf-8") as fh:
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
        "telnetlib",
    }
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned), "runner must not import network/credential modules"


def test_render_markdown_is_string(tmp_path):
    _stage_all_good(tmp_path)
    report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    md = qa.render_qa_report_markdown(report)
    assert md.startswith("# Crypto-D1 Real Data QA Report")
    assert "BLOCKED" in md and "LOCKED" in md

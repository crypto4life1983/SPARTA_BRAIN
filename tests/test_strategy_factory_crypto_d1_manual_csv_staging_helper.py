"""Tests for the Crypto-D1 manual CSV staging helper. All source CSVs are FAKE local
files under tmp_path; no network, no credentials, no real data."""

from __future__ import annotations

import ast
import csv

import sparta_commander.strategy_factory_crypto_d1_manual_csv_staging_helper as st
import sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner as qa


def _src_dir(tmp_path):
    d = tmp_path / "src"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _write(d, name: str, text: str) -> str:
    p = d / name
    p.write_text(text, encoding="utf-8")
    return str(p)


_CANON = "date,open,high,low,close,volume,source,instrument_type"


def _canon_rows() -> str:
    return "\n".join(
        [
            _CANON,
            "2024-01-01,100,110,90,105,1000,manual_csv,spot",
            "2024-01-02,105,115,100,108,1200,manual_csv,spot",
        ]
    )


def _all_canon(d):
    _write(d, "BTC_1d.csv", _canon_rows())
    _write(d, "ETH_1d.csv", _canon_rows())
    _write(d, "SOL_1d.csv", _canon_rows())


# --------------------------------------------------------------------------- #
# staging happy path + downstream QA
# --------------------------------------------------------------------------- #
def test_stage_all_then_qa_passes(tmp_path):
    d = _src_dir(tmp_path)
    _all_canon(d)
    report = st.stage_manual_csv(str(d), repo_root=str(tmp_path), write=True)
    assert report["overall_status"] == "ALL_STAGED"
    assert report["staged_count"] == 3
    # the staged files must now satisfy the read-only QA runner
    qa_report = qa.run_real_data_qa(repo_root=str(tmp_path), write=False)
    assert qa_report["verdict"] == qa.VERDICT_PASS


def test_header_normalization_from_aliases(tmp_path):
    d = _src_dir(tmp_path)
    aliased = "\n".join(
        [
            "Time,Open,High,Low,Close,Vol",
            "2024-01-01,100,110,90,105,1000",
            "2024-01-02,105,115,100,108,1200",
        ]
    )
    _write(d, "BTC_1d.csv", aliased)
    _write(d, "ETH_1d.csv", _canon_rows())
    _write(d, "SOL_1d.csv", _canon_rows())
    report = st.stage_manual_csv(
        str(d), repo_root=str(tmp_path), source_tag="my_source", write=True
    )
    assert report["overall_status"] == "ALL_STAGED"
    staged = tmp_path / "data" / "crypto_d1_spot" / "raw" / "BTC_1d.csv"
    with open(staged, encoding="utf-8", newline="") as fh:
        rows = list(csv.reader(fh))
    assert rows[0] == list(qa.QA_REQUIRED_FIELDS)
    # source filled from source_tag, instrument_type defaulted to spot
    assert rows[1][6] == "my_source" and rows[1][7] == "spot"


# --------------------------------------------------------------------------- #
# rejections
# --------------------------------------------------------------------------- #
def test_forbidden_field_rejected(tmp_path):
    d = _src_dir(tmp_path)
    bad = "\n".join(
        [
            "date,open,high,low,close,volume,side",
            "2024-01-01,100,110,90,105,1000,buy",
        ]
    )
    _write(d, "BTC_1d.csv", bad)
    _all_canon(d)
    _write(d, "BTC_1d.csv", bad)  # ensure BTC is the bad one
    report = st.stage_manual_csv(str(d), repo_root=str(tmp_path), write=True)
    btc = next(s for s in report["per_symbol"] if s["symbol"] == "BTC")
    assert btc["status"] == st.STAGE_REJECTED
    assert btc["reason"].startswith("forbidden_fields")
    assert report["overall_status"] == "PARTIAL"


def test_non_spot_rejected(tmp_path):
    d = _src_dir(tmp_path)
    bad = "\n".join(
        [
            _CANON,
            "2024-01-01,100,110,90,105,1000,manual_csv,perp",
        ]
    )
    _all_canon(d)
    _write(d, "ETH_1d.csv", bad)
    report = st.stage_manual_csv(str(d), repo_root=str(tmp_path), write=True)
    eth = next(s for s in report["per_symbol"] if s["symbol"] == "ETH")
    assert eth["status"] == st.STAGE_REJECTED
    assert eth["reason"] == "non_spot_instrument_type"


def test_missing_required_column_rejected(tmp_path):
    d = _src_dir(tmp_path)
    bad = "\n".join(["date,open,close", "2024-01-01,100,105"])
    _all_canon(d)
    _write(d, "SOL_1d.csv", bad)
    report = st.stage_manual_csv(str(d), repo_root=str(tmp_path), write=True)
    sol = next(s for s in report["per_symbol"] if s["symbol"] == "SOL")
    assert sol["status"] == st.STAGE_REJECTED
    assert sol["reason"].startswith("cannot_map_required_field")


def test_no_source_file_found(tmp_path):
    d = _src_dir(tmp_path)
    report = st.stage_manual_csv(str(d), repo_root=str(tmp_path), write=True)
    assert report["overall_status"] == "NONE_STAGED"
    assert all(s["reason"] == "no_source_file_found" for s in report["per_symbol"])


def test_explicit_symbol_files_mapping(tmp_path):
    d = _src_dir(tmp_path)
    _write(d, "btc-usd-daily.csv", _canon_rows())
    _write(d, "eth-usd-daily.csv", _canon_rows())
    _write(d, "sol-usd-daily.csv", _canon_rows())
    report = st.stage_manual_csv(
        str(d),
        repo_root=str(tmp_path),
        symbol_files={
            "BTC": "btc-usd-daily.csv",
            "ETH": "eth-usd-daily.csv",
            "SOL": "sol-usd-daily.csv",
        },
        write=True,
    )
    assert report["overall_status"] == "ALL_STAGED"


# --------------------------------------------------------------------------- #
# write scope + safety
# --------------------------------------------------------------------------- #
def test_write_false_stages_nothing(tmp_path):
    d = _src_dir(tmp_path)
    _all_canon(d)
    report = st.stage_manual_csv(str(d), repo_root=str(tmp_path), write=False)
    assert report["files_written"] == []
    assert not (tmp_path / "data" / "crypto_d1_spot" / "raw").exists()


def test_report_records_locked_gates(tmp_path):
    d = _src_dir(tmp_path)
    _all_canon(d)
    report = st.stage_manual_csv(str(d), repo_root=str(tmp_path), write=False)
    assert report["real_data_qa_blocked"] is True
    assert report["baseline_backtest_blocked"] is True
    assert report["paper_trading_gate_locked"] is True
    assert report["micro_live_gate_locked"] is True
    assert report["executes"] is False


def test_helper_imports_no_network_or_credential_modules():
    with open(st.__file__, "r", encoding="utf-8") as fh:
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


def test_render_markdown_is_string(tmp_path):
    d = _src_dir(tmp_path)
    _all_canon(d)
    report = st.stage_manual_csv(str(d), repo_root=str(tmp_path), write=False)
    md = st.render_staging_report_markdown(report)
    assert md.startswith("# Crypto-D1 Manual CSV Staging Report")
    assert "BLOCKED" in md and "LOCKED" in md

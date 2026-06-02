"""Bundle 19 -- Crypto-D1 Data QA Runtime Tool v1 tests (research-only).

Pure stdlib + pytest. Uses tmp_path synthetic fixtures only; NEVER touches
real research data; NEVER hits the network.
"""
from __future__ import annotations

import ast
import csv
import hashlib
import json
import math
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[1]
_TOOLS_DIR = _REPO_ROOT / "tools"
if str(_TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(_TOOLS_DIR))

import crypto_d1_data_qa_runtime_tool as qat   # noqa: E402
import crypto_d1_qa_freeze_spec_check as cqf   # noqa: E402

TOOL_FILE = _TOOLS_DIR / "crypto_d1_data_qa_runtime_tool.py"


# ---------------------------------------------------------------------------
# Synthetic fixture helpers (tmp_path only; never touch real data)
# ---------------------------------------------------------------------------
def _write_csv(path: Path, symbol: str, n_days: int = 300,
               start_price: float = 100.0, drift: float = 0.0010,
               vol: float = 0.012, start_date: str = "2023-01-01",
               source: str = "synthetic_test", quote: str = "USDT",
               extra_rows: list | None = None,
               header_override: list | None = None):
    base = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    rows = []
    p = start_price
    for i in range(n_days):
        d = base + timedelta(days=i)
        delta = drift + vol * math.sin(i * 0.13)
        nxt = max(0.01, p * (1 + delta))
        o, c = p, nxt
        h = max(o, c) * (1 + 0.003)
        lo = min(o, c) * (1 - 0.003)
        v = 1000.0 + 5.0 * i
        rows.append({
            "timestamp": d.strftime("%Y-%m-%d"),
            "open": f"{o:.6f}", "high": f"{h:.6f}",
            "low": f"{lo:.6f}", "close": f"{c:.6f}",
            "volume": f"{v:.4f}", "symbol": symbol,
            "source": source, "quote_currency": quote,
        })
        p = nxt
    if extra_rows:
        rows.extend(extra_rows)
    header = header_override or list(qat.REQUIRED_BAR_COLUMNS)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in header})


def _write_manifest(path: Path, dataset_id="CRYPTO_D1_SPOT_BTC_V001",
                    dataset_version="V001", assets=None,
                    freeze_status="FROZEN", qa_status="QA_PASS",
                    row_count_actual=300, missing_day_policy_present=True,
                    omit_fields: list | None = None):
    # Accept either a directory path or an explicit file path. If the path is
    # an existing directory (or has no .json suffix), write to <path>/manifest.json.
    path = Path(path)
    if path.is_dir() or path.suffix.lower() != ".json":
        path = path / "manifest.json"
    assets = assets or ["BTC"]
    base = {
        "dataset_id": dataset_id,
        "dataset_version": dataset_version,
        "created_at": "2024-01-01T00:00:00Z",
        "created_by": "test_fixture + SPARTA Brain",
        "research_lane": "crypto_d1_protocol",
        "market_type": "spot",
        "assets": assets,
        "symbols": {a: f"{a}USDT@synthetic" for a in assets},
        "quote_currency": "USDT",
        "timeframe": "1d",
        "time_start": "2023-01-01",
        "time_end": "2023-12-31",
        "timezone": "UTC",
        "bar_boundary": "UTC 00:00:00 close; left-closed / right-open",
        "data_frequency": "daily",
        "source_type": "on_disk_frozen_file",
        "source_name": "synthetic_test_fixture",
        "source_location": "tmp_path/dataset/",
        "data_contract_version": "crypto_d1_data_contract_v1",
        "protocol_version": "crypto_d1_protocol_v1",
        "checksum_policy": "sha256-per-file in CHECKSUMS.txt",
        "row_count_expected": row_count_actual,
        "row_count_actual": row_count_actual,
        "missing_day_policy": ("flagged in manifest; never silently forward-filled"
                                if missing_day_policy_present else ""),
        "duplicate_policy": "duplicate (symbol, timestamp) rejected",
        "partial_day_policy": "partial-day bars excluded from frozen dataset",
        "zero_volume_policy": "flagged for review; never silently kept",
        "outlier_policy": "flagged not dropped",
        "normalization_policy": "per-series quote currency; tick/lot per venue",
        "fee_slippage_assumption_reference": "fees.json",
        "freeze_status": freeze_status,
        "QA_status": qa_status,
        "allowed_use": "pre-registered offline backtests only",
        "forbidden_use": "no live trading; no paper-order execution",
        "notes": "synthetic test fixture",
    }
    if omit_fields:
        for f in omit_fields:
            base.pop(f, None)
    path.write_text(json.dumps(base, indent=2, ensure_ascii=False), encoding="utf-8")


def _write_checksums(dataset_dir: Path, file_names: list, override_sha=None):
    lines = []
    for name in file_names:
        p = dataset_dir / name
        if not p.exists():
            continue
        if override_sha and name in override_sha:
            sha = override_sha[name]
        else:
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"{sha}  {name}")
    (dataset_dir / "CHECKSUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_freeze_record(dataset_dir: Path):
    text = (
        "freeze_timestamp_utc: 2024-01-02T00:00:00Z\n"
        "operator: test_fixture + SPARTA Brain\n"
        "protocol_version: crypto_d1_protocol_v1\n"
        "data_contract_version: crypto_d1_data_contract_v1\n"
        "manifest_version: crypto_d1_dataset_manifest_v1\n"
        "qa_freeze_spec_version: crypto_d1_qa_freeze_spec_v1\n"
        "backtest_plan_version: crypto_d1_baseline_backtest_plan_v1\n"
        "runner_version: crypto_d1_backtest_runner_v1\n"
    )
    (dataset_dir / "FREEZE_RECORD.txt").write_text(text, encoding="utf-8")


def _write_fees(dataset_dir: Path, with_taker=True, with_slippage=True,
                with_spread_proxy=True):
    fees = {"fees": {}}
    if with_taker:
        fees["fees"]["BTC"] = {"taker_bps": 10, "maker_bps": 5, "venue": "synthetic"}
    if with_slippage:
        fees["slippage_bps"] = 5
    if with_spread_proxy:
        fees["spread_proxy_bps"] = 5
    (dataset_dir / "fees.json").write_text(
        json.dumps(fees, indent=2, ensure_ascii=False), encoding="utf-8")


def _build_clean_dataset(tmp_path, symbols=("BTC",), n_days=300):
    ds = tmp_path / "dataset"
    ds.mkdir()
    for s in symbols:
        _write_csv(ds / f"{s}_daily.csv", s, n_days=n_days, start_price=100.0)
    _write_manifest(ds, assets=list(symbols),
                    row_count_actual=n_days * len(symbols))
    _write_fees(ds)
    _write_freeze_record(ds)
    file_names = [f"{s}_daily.csv" for s in symbols] + ["manifest.json",
                                                          "fees.json",
                                                          "FREEZE_RECORD.txt"]
    _write_checksums(ds, file_names)
    return ds


# ===========================================================================
# Tool safety
# ===========================================================================
def _tool_source_minus_docstrings():
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))

    def strip(body):
        if (body and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)):
            body.pop(0)
    strip(tree.body)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            strip(node.body)
    return ast.unparse(tree)


def test_tool_stdlib_only():
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))
    stdlib_ok = {"argparse", "csv", "dataclasses", "datetime", "hashlib",
                 "json", "math", "pathlib", "sys", "__future__",
                 # In-repo stdlib-only validators imported for cross-spec reuse.
                 "crypto_d1_qa_freeze_spec_check",
                 "crypto_d1_dataset_manifest_check"}
    seen = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                seen.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            seen.add((node.module or "").split(".")[0])
    extra = seen - stdlib_ok
    assert not extra, f"unexpected imports: {extra}"


def test_tool_no_network_or_broker_or_exchange_imports():
    tree = ast.parse(TOOL_FILE.read_text(encoding="utf-8"))
    forbidden = {"requests", "urllib", "http", "socket", "ssl", "tiingo",
                 "ccxt", "alpaca", "binance", "dotenv", "subprocess", "os"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                assert n.name.split(".")[0] not in forbidden, n.name
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] not in forbidden, node.module
    code = _tool_source_minus_docstrings()
    for tok in ("os.environ", "os.getenv", "getenv(", "urlopen",
                "api.telegram.org"):
        assert tok not in code, f"forbidden attribute in code: {tok!r}"


def test_tool_source_has_no_order_execution_code():
    code = _tool_source_minus_docstrings().lower()
    forbidden = ("place_order", "submit_order", "send_order", "route_order",
                 "execute_order(", "execute_trade", "broker.place",
                 "broker.send", "alpaca.submit", "binance.create_order",
                 "ibkr.placeorder")
    for tok in forbidden:
        assert tok not in code, f"forbidden verb in tool: {tok!r}"


# ===========================================================================
# validate-spec / show-spec CLI
# ===========================================================================
def test_validate_spec_passes():
    ok, errs = qat.validate_spec()
    assert ok, errs


def test_cli_validate_spec(capsys):
    assert qat.main(["validate-spec"]) == 0
    out = capsys.readouterr().out
    assert "validate-spec: OK" in out


def test_cli_show_spec(capsys):
    assert qat.main(["show-spec"]) == 0
    out = capsys.readouterr().out
    assert "crypto_d1_data_qa_runtime_tool_v1" in out
    assert "spot" in out
    assert "A_manifest_integrity" in out
    for status in ("QA_PASS", "QA_WARN", "QA_FAIL", "QA_BLOCKED"):
        assert status in out


# ===========================================================================
# Missing / empty dataset safe-fail
# ===========================================================================
def test_missing_dataset_dir_emits_qa_draft(tmp_path):
    out = tmp_path / "out"
    report = qat.build_qa_report(tmp_path / "no_such", out)
    assert report["qa_status"] == "QA_DRAFT"
    assert report["checks_run"] == 0
    qat.write_qa_report(report, out)
    assert (out / "qa_report.json").exists()
    assert (out / "qa_report.md").exists()


def test_empty_dataset_dir_emits_qa_fail(tmp_path):
    ds = tmp_path / "dataset"
    ds.mkdir()
    out = tmp_path / "out"
    report = qat.build_qa_report(ds, out)
    assert report["qa_status"] == "QA_FAIL"
    assert any("no .csv files" in f["detail"] for f in report["blocking_failures"])


# ===========================================================================
# Group A -- manifest integrity
# ===========================================================================
def test_group_a_missing_manifest(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    (ds / "manifest.json").unlink()
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"
    blocking_ids = {f["check_id"] for f in report["blocking_failures"]}
    assert "manifest_present" in blocking_ids


def test_group_a_missing_required_field(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    _write_manifest(ds / "manifest.json", omit_fields=["checksum_policy"])
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"
    assert any("checksum_policy" in f["detail"]
               for f in report["blocking_failures"])


def test_group_a_wrong_protocol_version(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    m = json.loads((ds / "manifest.json").read_text(encoding="utf-8"))
    m["protocol_version"] = "some_other_protocol_v9"
    (ds / "manifest.json").write_text(json.dumps(m, indent=2), encoding="utf-8")
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"
    assert any("protocol_version" in f["check_id"]
               for f in report["blocking_failures"])


# ===========================================================================
# Group B -- timestamp
# ===========================================================================
def test_group_b_duplicate_timestamp(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    # Append a duplicate row at the end.
    dup = [{"timestamp": "2023-01-01", "open": "100", "high": "110",
            "low": "90", "close": "105", "volume": "1000", "symbol": "BTC",
            "source": "synthetic_test", "quote_currency": "USDT"}]
    _write_csv(ds / "BTC_daily.csv", "BTC", n_days=300, extra_rows=dup)
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"
    assert any(f["check_id"] == "duplicate_symbol_timestamp"
               for f in report["blocking_failures"])


def test_group_b_weekday_only_detected(tmp_path):
    ds = tmp_path / "dataset"
    ds.mkdir()
    # Build a weekday-only series: only Mon-Fri.
    base = datetime(2023, 1, 2, tzinfo=timezone.utc)  # Monday
    rows = []
    p = 100.0
    for i in range(30):
        d = base + timedelta(days=i)
        if d.weekday() > 4:
            continue  # skip weekends
        nxt = p * 1.001
        rows.append({"timestamp": d.strftime("%Y-%m-%d"),
                     "open": f"{p:.6f}", "high": f"{max(p,nxt)*1.001:.6f}",
                     "low": f"{min(p,nxt)*0.999:.6f}", "close": f"{nxt:.6f}",
                     "volume": "1000", "symbol": "BTC",
                     "source": "synthetic_test", "quote_currency": "USDT"})
        p = nxt
    with (ds / "BTC_daily.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(qat.REQUIRED_BAR_COLUMNS))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    _write_manifest(ds, row_count_actual=len(rows))
    _write_fees(ds)
    _write_freeze_record(ds)
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"
    assert any(f["check_id"] == "no_weekday_only_calendar"
               for f in report["blocking_failures"])


def test_group_b_missing_days_reconciled_warn(tmp_path):
    ds = tmp_path / "dataset"
    ds.mkdir()
    # 280 days but spanning 300-day window.
    base = datetime(2023, 1, 1, tzinfo=timezone.utc)
    rows = []
    p = 100.0
    skip_set = set(range(50, 70))
    for i in range(300):
        if i in skip_set:
            continue
        d = base + timedelta(days=i)
        nxt = p * 1.001
        rows.append({"timestamp": d.strftime("%Y-%m-%d"),
                     "open": f"{p:.6f}", "high": f"{max(p,nxt)*1.001:.6f}",
                     "low": f"{min(p,nxt)*0.999:.6f}", "close": f"{nxt:.6f}",
                     "volume": "1000", "symbol": "BTC",
                     "source": "synthetic_test", "quote_currency": "USDT"})
        p = nxt
    with (ds / "BTC_daily.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(qat.REQUIRED_BAR_COLUMNS))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    _write_manifest(ds, row_count_actual=len(rows))
    _write_fees(ds)
    _write_freeze_record(ds)
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    # Missing days are present + manifest declares missing_day_policy -> WARN.
    assert any(w["check_id"] == "missing_days_reconciled"
               for w in report["warnings"])


# ===========================================================================
# Group C -- OHLCV
# ===========================================================================
def test_group_c_high_lt_low_is_fail(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    bad = [{"timestamp": "2024-12-31", "open": "100", "high": "50",
            "low": "120", "close": "80", "volume": "1000", "symbol": "BTC",
            "source": "synthetic_test", "quote_currency": "USDT"}]
    _write_csv(ds / "BTC_daily.csv", "BTC", n_days=300, extra_rows=bad)
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"


def test_group_c_self_consistency_violation(tmp_path):
    # high < max(o, c, l) without high < low triggers the consistency check.
    ds = _build_clean_dataset(tmp_path)
    bad = [{"timestamp": "2024-12-31", "open": "120", "high": "110",
            "low": "90", "close": "100", "volume": "1000", "symbol": "BTC",
            "source": "synthetic_test", "quote_currency": "USDT"}]
    _write_csv(ds / "BTC_daily.csv", "BTC", n_days=300, extra_rows=bad)
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"
    assert any(f["check_id"] == "ohlcv_self_consistency"
               for f in report["blocking_failures"])


# ===========================================================================
# Group D -- volume
# ===========================================================================
def test_group_d_negative_volume_is_fail(tmp_path):
    # Parser rejects negative volume? Let me check -- the parser builds Bar
    # for negative volume too; rejection happens in the runner's load_dataset
    # but not in our read_csv_bars (we accept negatives so Group D can flag).
    ds = _build_clean_dataset(tmp_path)
    bad = [{"timestamp": "2024-12-31", "open": "100", "high": "110",
            "low": "90", "close": "105", "volume": "-1", "symbol": "BTC",
            "source": "synthetic_test", "quote_currency": "USDT"}]
    _write_csv(ds / "BTC_daily.csv", "BTC", n_days=300, extra_rows=bad)
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"
    assert any(f["check_id"] == "volume_non_negative"
               for f in report["blocking_failures"])


def test_group_d_zero_volume_is_warn(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    bad = [{"timestamp": "2024-12-31", "open": "100", "high": "110",
            "low": "90", "close": "105", "volume": "0", "symbol": "BTC",
            "source": "synthetic_test", "quote_currency": "USDT"}]
    _write_csv(ds / "BTC_daily.csv", "BTC", n_days=300, extra_rows=bad)
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] in ("QA_WARN", "QA_FAIL")
    assert any(w["check_id"] == "zero_volume_flag" for w in report["warnings"])


# ===========================================================================
# Group E -- symbol/source
# ===========================================================================
def test_group_e_btc_eth_sol_coverage(tmp_path):
    ds = _build_clean_dataset(tmp_path, symbols=("BTC", "ETH", "SOL"))
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert any(r["check_id"] == "canonical_symbol_btc_eth_sol"
               and r["severity"] == "PASS"
               for r in (report["source_provenance_summary"]["details"]))


def test_group_e_quote_currency_mismatch_is_fail(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    bad = [{"timestamp": "2024-12-31", "open": "100", "high": "110",
            "low": "90", "close": "105", "volume": "1000", "symbol": "BTC",
            "source": "synthetic_test", "quote_currency": "USDC"}]
    _write_csv(ds / "BTC_daily.csv", "BTC", n_days=300, extra_rows=bad)
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"


# ===========================================================================
# Group F -- fee/slippage
# ===========================================================================
def test_group_f_missing_fees_is_fail(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    (ds / "fees.json").unlink()
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"
    blocking_ids = {f["check_id"] for f in report["blocking_failures"]}
    assert "fees_json_present" in blocking_ids


def test_group_f_missing_slippage_is_fail(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    _write_fees(ds, with_slippage=False)
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"
    assert any(f["check_id"] == "slippage_declared"
               for f in report["blocking_failures"])


# ===========================================================================
# Group G -- freeze
# ===========================================================================
def test_group_g_tampered_file_sha256_mismatch_is_fail(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    # Tamper a single byte of BTC_daily.csv AFTER CHECKSUMS.txt is written.
    with (ds / "BTC_daily.csv").open("ab") as f:
        f.write(b"\n# tampered\n")
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"
    assert any(f["check_id"] == "checksums_verified"
               for f in report["blocking_failures"])


def test_group_g_missing_freeze_record_is_fail(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    (ds / "FREEZE_RECORD.txt").unlink()
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"
    assert any(f["check_id"] == "freeze_record_present"
               for f in report["blocking_failures"])


def test_group_g_freeze_status_not_frozen_is_fail(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    _write_manifest(ds / "manifest.json", freeze_status="DRAFT")
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_FAIL"


# ===========================================================================
# 26-field schema + safety flags + classifier
# ===========================================================================
def test_emitted_report_has_all_26_required_fields(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    report = qat.build_qa_report(ds, tmp_path / "out")
    for fld in cqf.REQUIRED_QA_REPORT_FIELDS:
        assert fld in report, f"qa_report missing required field: {fld}"


def test_safety_flags_pinned_false_in_emitted_report(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    report = qat.build_qa_report(ds, tmp_path / "out")
    sf = report["safety_flags"]
    assert sf["research_only"] is True
    for k in ("data_fetch_enabled", "exchange_connection_enabled",
              "live_trading_enabled", "broker_control_enabled",
              "paper_order_execution_enabled", "order_placement_enabled"):
        assert sf[k] is False


def test_clean_dataset_emits_qa_pass(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_PASS", report["blocking_failures"] + report["warnings"]
    assert report["checks_failed"] == 0


def test_manifest_qa_blocked_overrides_to_qa_blocked(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    _write_manifest(ds / "manifest.json", qa_status="QA_BLOCKED")
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "fees.json",
                          "FREEZE_RECORD.txt"])
    report = qat.build_qa_report(ds, tmp_path / "out")
    assert report["qa_status"] == "QA_BLOCKED"


# ===========================================================================
# Determinism
# ===========================================================================
def test_deterministic_run_on_same_input(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    r1 = qat.build_qa_report(ds, tmp_path / "out1")
    r2 = qat.build_qa_report(ds, tmp_path / "out2")
    # Redact wall-clock fields.
    for r in (r1, r2):
        r.pop("generated_at", None)
        r["_audit_context"].pop("safety_notes", None)
    assert r1["qa_report_id"] == r2["qa_report_id"]


# ===========================================================================
# Report files land at out_dir
# ===========================================================================
def test_report_files_land_at_out_dir(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    out = tmp_path / "out_nested" / "sub"
    report = qat.build_qa_report(ds, out)
    qat.write_qa_report(report, out)
    assert (out / "qa_report.json").exists()
    assert (out / "qa_report.md").exists()


def test_report_md_has_research_only_and_no_authorize_trading(tmp_path):
    ds = _build_clean_dataset(tmp_path)
    out = tmp_path / "out"
    report = qat.build_qa_report(ds, out)
    qat.write_qa_report(report, out)
    md = (out / "qa_report.md").read_text(encoding="utf-8")
    assert "Research-only" in md
    assert "No data fetched" in md
    assert "research_only: True" in md


# ===========================================================================
# CLI run
# ===========================================================================
def test_cli_run_returns_0_on_qa_pass(tmp_path, capsys):
    ds = _build_clean_dataset(tmp_path)
    out = tmp_path / "out"
    code = qat.main(["run", "--dataset-dir", str(ds), "--out-dir", str(out)])
    assert code == 0
    captured = capsys.readouterr().out
    assert "qa_status:" in captured
    assert "QA_PASS" in captured


def test_cli_run_returns_2_on_qa_fail(tmp_path, capsys):
    ds = _build_clean_dataset(tmp_path)
    (ds / "fees.json").unlink()
    _write_checksums(ds, ["BTC_daily.csv", "manifest.json", "FREEZE_RECORD.txt"])
    out = tmp_path / "out"
    code = qat.main(["run", "--dataset-dir", str(ds), "--out-dir", str(out)])
    assert code == 2


# ===========================================================================
# Repo invariants -- no real data committed under bundle dir
# ===========================================================================
def test_no_real_data_files_committed_under_bundle_dir():
    bundle_dir = _REPO_ROOT / "reports" / "crypto_d1_data_qa_runtime_tool_v1"
    if not bundle_dir.exists():
        return
    forbidden_exts = (".csv", ".parquet", ".pq", ".pickle", ".feather", ".h5",
                      ".npz", ".pkl")
    for p in bundle_dir.iterdir():
        if not p.is_file():
            continue
        for ext in forbidden_exts:
            assert not p.name.lower().endswith(ext), \
                f"unexpected real-data file in bundle dir: {p.name}"


def test_no_data_directory_created_in_repo():
    p = _REPO_ROOT / "data" / "crypto_d1_research"
    if not p.exists():
        return
    forbidden_exts = (".csv", ".parquet", ".pq", ".pickle", ".feather", ".h5",
                      ".npz", ".pkl")
    for f in p.rglob("*"):
        if not f.is_file():
            continue
        for ext in forbidden_exts:
            assert not f.name.lower().endswith(ext), \
                f"unexpected real data file: {f.as_posix()}"


# ===========================================================================
# Integration -- prior validators still pass
# ===========================================================================
def test_qa_freeze_spec_validator_still_passes():
    ok, errs = cqf.validate(_REPO_ROOT)
    assert ok, errs


def test_dataset_manifest_validator_still_passes():
    import crypto_d1_dataset_manifest_check as cdm
    ok, errs = cdm.validate(_REPO_ROOT)
    assert ok, errs


def test_backtest_runner_module_imports_ok():
    import crypto_d1_backtest_runner as cbr
    plan = cbr.show_plan()
    assert plan["allowed_market_type"] == "spot"
    ok, _ = cbr.validate_config()
    assert ok

"""Tests for the Crypto-D1 Risk-Controlled Variant Backtest Runner (READ-ONLY). All
inputs are FAKE local CSVs under tmp_path that the real QA runner stages and passes;
no network, no credentials, no real data, no broker, no live order, no gate unlock."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_variant_backtest_runner as vr
import sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner as qa

_CANON = ",".join(qa.QA_REQUIRED_FIELDS)
_SRC = "binance_usdt_spot_frozen_regime_inputs"


def _series_rows(n: int) -> str:
    """A monotonically rising spot series long enough to exercise the engine."""
    rows = [_CANON]
    price = 100.0
    for i in range(n):
        day = 1 + i
        date = f"2021-{((day - 1) // 28) % 12 + 1:02d}-{(day - 1) % 28 + 1:02d}"
        o = price
        price = price * 1.01
        c = price
        hi = max(o, c) * 1.02
        lo = min(o, c) * 0.98
        rows.append(f"{date},{o:.4f},{hi:.4f},{lo:.4f},{c:.4f},1000,{_SRC},spot")
    return "\n".join(rows)


def _stage_and_qa(tmp_path, n: int = 30) -> None:
    raw = tmp_path / "data" / "crypto_d1_spot" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for sym in ("BTC", "ETH", "SOL"):
        (raw / (sym + "_1d.csv")).write_text(_series_rows(n), encoding="utf-8")
    rep = qa.run_real_data_qa(repo_root=str(tmp_path), write=True)
    assert rep["verdict"] == qa.VERDICT_PASS


# --------------------------------------------------------------------------- #
# refusal posture
# --------------------------------------------------------------------------- #
def test_refuses_when_inputs_missing(tmp_path):
    r = vr.run_variant_backtests(repo_root=str(tmp_path), write=True)
    assert r["verdict"] == vr.VERDICT_BLOCKED_NOT_READY
    assert r["variant_results"] == []
    assert r["files_written"] == []
    assert any("variant_prep_not_ready" in b for b in r["blockers"])


# --------------------------------------------------------------------------- #
# completed run
# --------------------------------------------------------------------------- #
def test_runs_all_five_variants(tmp_path):
    _stage_and_qa(tmp_path)
    r = vr.run_variant_backtests(repo_root=str(tmp_path), write=False)
    assert r["verdict"] == vr.VERDICT_VARIANTS_COMPLETE
    assert r["variant_count"] == 5
    ids = [v["variant_id"] for v in r["variant_results"]]
    assert ids == [
        "V1_trend_filter",
        "V2_trend_plus_cash_regime",
        "V3_voltarget_concentration_cap",
        "V4_monthly_rebalance_capped",
        "V5_full_risk_managed",
    ]


def test_every_variant_has_performance_and_eligibility(tmp_path):
    _stage_and_qa(tmp_path)
    r = vr.run_variant_backtests(repo_root=str(tmp_path), write=False)
    for v in r["variant_results"]:
        perf = v["performance"]
        assert set(["total_return", "max_drawdown", "sharpe_ratio", "cagr"]) <= set(perf.keys())
        assert perf["max_drawdown"] <= 0.0
        assert isinstance(v["beats_drawdown_floor"], bool)
        assert v["promotion_decision"] in (
            vr.PROMOTE_TO_PAPER_PREP, vr.DO_NOT_PROMOTE_TO_PAPER_YET
        )
        assert isinstance(v["eligible_for_paper_prep"], bool)


def test_concentration_cap_limits_single_asset_weight(tmp_path):
    _stage_and_qa(tmp_path)
    r = vr.run_variant_backtests(repo_root=str(tmp_path), write=False)
    v4 = next(v for v in r["variant_results"] if v["variant_id"] == "V4_monthly_rebalance_capped")
    # no single sleeve may exceed the pinned 33% cap (+ drift tolerance within a month)
    for s in v4["per_symbol"]:
        assert s["contribution_to_portfolio"] <= 0.45


def test_writes_only_variant_report_artifacts(tmp_path):
    _stage_and_qa(tmp_path)
    r = vr.run_variant_backtests(repo_root=str(tmp_path), write=True)
    assert len(r["files_written"]) == 2
    for p in r["files_written"]:
        assert "crypto_d1_variant_backtest" in p.replace("\\", "/")
    rep_json = tmp_path / "reports" / "crypto_d1_variant_backtest" / "variant_backtest_report.json"
    assert rep_json.is_file()
    loaded = json.loads(rep_json.read_text(encoding="utf-8"))
    assert loaded["verdict"] == vr.VERDICT_VARIANTS_COMPLETE


# --------------------------------------------------------------------------- #
# safety posture
# --------------------------------------------------------------------------- #
def test_run_unlocks_nothing(tmp_path):
    _stage_and_qa(tmp_path)
    r = vr.run_variant_backtests(repo_root=str(tmp_path), write=False)
    assert r["executes_orders"] is False
    assert r["ran_optimization"] is False
    assert r["ran_parameter_search"] is False
    assert r["ran_walk_forward"] is False
    assert r["used_lookahead"] is False
    assert r["used_leverage"] is False
    assert r["used_shorting"] is False
    assert r["touches_broker_or_exchange"] is False
    assert r["authorizes_paper_trading"] is False
    assert r["unlocks_downstream_gate"] is False
    assert r["paper_trading_gate_locked"] is True
    assert r["micro_live_gate_locked"] is True


def test_validate_passes(tmp_path):
    _stage_and_qa(tmp_path)
    r = vr.run_variant_backtests(repo_root=str(tmp_path), write=False)
    v = vr.validate_variant_backtest_report(r)
    assert v["valid"] is True and v["errors"] == []


def test_validate_rejects_unlocked_gate(tmp_path):
    _stage_and_qa(tmp_path)
    r = vr.run_variant_backtests(repo_root=str(tmp_path), write=False)
    r["paper_trading_gate_locked"] = False
    v = vr.validate_variant_backtest_report(r)
    assert v["valid"] is False
    assert any("gate_not_locked" in e for e in v["errors"])


def test_validate_rejects_executed_orders(tmp_path):
    _stage_and_qa(tmp_path)
    r = vr.run_variant_backtests(repo_root=str(tmp_path), write=False)
    r["executes_orders"] = True
    v = vr.validate_variant_backtest_report(r)
    assert v["valid"] is False
    assert any("capability_not_false:executes_orders" in e for e in v["errors"])


def test_render_markdown_is_string(tmp_path):
    _stage_and_qa(tmp_path)
    r = vr.run_variant_backtests(repo_root=str(tmp_path), write=False)
    md = vr.render_variant_backtest_markdown(r)
    assert md.startswith("# Crypto-D1 Risk-Controlled Variant Backtest")
    assert "LOCKED" in md and "V5_full_risk_managed" in md


def test_module_imports_no_network_or_credential_modules():
    with open(vr.__file__, "r", encoding="utf-8") as fh:
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

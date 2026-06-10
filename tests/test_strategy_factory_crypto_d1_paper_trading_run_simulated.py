"""Tests for the Crypto-D1 V2 SIMULATED Paper-Trading Runner (NO LIVE MONEY).

Every input is a FAKE local CSV written under tmp_path, plus a FAKE in-memory variant
report that satisfies the paper-prep readiness gate. No network, no credentials, no real
data, no broker, no exchange, no real order, no gate is unlocked. The simulation runs
entirely on synthetic prices."""

from __future__ import annotations

import ast
import datetime
import json

import sparta_commander.strategy_factory_crypto_d1_paper_trading_run_simulated as pr
import sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner as qa

_SRC = "binance_usdt_spot_frozen_regime_inputs"
_CANON = ",".join(qa.QA_REQUIRED_FIELDS)


def _csv_from_closes(closes: list[float]) -> str:
    rows = [_CANON]
    start = datetime.date(2021, 1, 1)
    prev = closes[0]
    for i, c in enumerate(closes):
        d = (start + datetime.timedelta(days=i)).isoformat()
        o = prev
        hi = max(o, c) * 1.02
        lo = min(o, c) * 0.98
        rows.append(f"{d},{o:.6f},{hi:.6f},{lo:.6f},{c:.6f},1000,{_SRC},spot")
        prev = c
    return "\n".join(rows)


def _variant(vid, *, max_dd, sharpe=1.10, total_return=2.0, trading_days=2128,
             eligible, blockers=None, beats_floor=None):
    if beats_floor is None:
        beats_floor = max_dd >= -0.50
    return {
        "variant_id": vid,
        "description": vid,
        "controls": ["trend_filter"],
        "performance": {
            "max_drawdown": max_dd, "sharpe_ratio": sharpe,
            "total_return": total_return, "trading_days": trading_days, "cagr": 0.50,
        },
        "beats_drawdown_floor": beats_floor,
        "promotion_decision": "PROMOTE_TO_PAPER_PREP" if eligible else "DO_NOT_PROMOTE_TO_PAPER_YET",
        "eligible_for_paper_prep": eligible,
        "eligibility_blockers": list(blockers or []),
    }


def _report_v2_eligible():
    return {
        "verdict": "VARIANTS_COMPLETE",
        "variant_count": 5,
        "variant_results": [
            _variant("V1_trend_filter", max_dd=-0.5349, sharpe=0.92,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V2_trend_plus_cash_regime", max_dd=-0.4816, sharpe=1.10,
                     total_return=11.5528, eligible=True),
            _variant("V3_voltarget_concentration_cap", max_dd=-0.8512, sharpe=0.99,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V4_monthly_rebalance_capped", max_dd=-0.8438, sharpe=1.04,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V5_full_risk_managed", max_dd=-0.5085, sharpe=1.07,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
        ],
        "eligible_for_paper_prep": ["V2_trend_plus_cash_regime"],
        "any_variant_eligible_for_paper_prep": True,
    }


def _stage_review(tmp_path, report):
    rep_dir = tmp_path / "reports" / "crypto_d1_variant_backtest"
    rep_dir.mkdir(parents=True, exist_ok=True)
    (rep_dir / "variant_backtest_report.json").write_text(json.dumps(report), encoding="utf-8")


def _stage_csvs(tmp_path, closes):
    raw = tmp_path / "data" / "crypto_d1_spot" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    for sym in ("BTC", "ETH", "SOL"):
        (raw / (sym + "_1d.csv")).write_text(_csv_from_closes(closes), encoding="utf-8")


def _rising(n: int, step: float = 1.01, start: float = 100.0):
    out, p = [], start
    for _ in range(n):
        out.append(p)
        p *= step
    return out


def _ready(tmp_path, closes):
    _stage_review(tmp_path, _report_v2_eligible())
    _stage_csvs(tmp_path, closes)


# --------------------------------------------------------------------------- #
# refusal posture
# --------------------------------------------------------------------------- #
def test_refuses_when_paper_prep_not_ready(tmp_path):
    _stage_csvs(tmp_path, _rising(230))  # CSVs present but NO approved variant review
    r = pr.run_simulated_paper(repo_root=str(tmp_path), write=True)
    assert r["verdict"] == pr.VERDICT_BLOCKED_NOT_READY
    assert any("paper_prep_not_ready" in b for b in r["blockers"])
    assert r["files_written"] == []


# --------------------------------------------------------------------------- #
# completed simulated run
# --------------------------------------------------------------------------- #
def test_completes_and_trades_when_ready(tmp_path):
    _ready(tmp_path, _rising(230))
    r = pr.run_simulated_paper(repo_root=str(tmp_path), write=False)
    assert r["verdict"] == pr.VERDICT_PAPER_RUN_COMPLETE
    assert r["selected_variant_id"] == "V2_trend_plus_cash_regime"
    assert r["trade_summary"]["simulated_trades"] > 0
    assert r["trade_summary"]["real_orders_placed"] == 0
    assert r["performance"]["final_equity"] > 0
    assert r["kill_switch_triggered"] is False


def test_run_executes_no_real_orders_and_locks_gates(tmp_path):
    _ready(tmp_path, _rising(230))
    r = pr.run_simulated_paper(repo_root=str(tmp_path), write=False)
    assert r["uses_real_money"] is False
    assert r["connects_broker"] is False
    assert r["connects_exchange"] is False
    assert r["executes_real_orders"] is False
    assert r["simulated_orders_only"] is True
    assert r["uses_network"] is False
    assert r["uses_credentials"] is False
    assert r["used_leverage"] is False
    assert r["used_shorting"] is False
    assert r["used_margin"] is False
    assert r["paper_trading_gate_locked"] is True
    assert r["micro_live_gate_locked"] is True
    assert r["live_gate_locked"] is True
    assert r["unlocks_downstream_gate"] is False


def test_writes_only_paper_prep_artifacts(tmp_path):
    _ready(tmp_path, _rising(230))
    r = pr.run_simulated_paper(repo_root=str(tmp_path), write=True)
    assert len(r["files_written"]) == 3
    for p in r["files_written"]:
        assert "crypto_d1_paper_prep" in p.replace("\\", "/")
    out = tmp_path / "reports" / "crypto_d1_paper_prep"
    assert (out / "paper_run_log.jsonl").is_file()
    assert (out / "paper_run_report.json").is_file()
    assert (out / "paper_run_report.md").is_file()
    # every logged evaluation records a simulated (never real) order
    for line in (out / "paper_run_log.jsonl").read_text(encoding="utf-8").splitlines():
        assert json.loads(line)["real_order_placed"] is False


# --------------------------------------------------------------------------- #
# kill switch
# --------------------------------------------------------------------------- #
def test_daily_loss_halt_triggers_and_stays_halted(tmp_path):
    closes = _rising(209) + [_rising(209)[-1] * 0.85] + [_rising(209)[-1] * 0.85] * 3
    _ready(tmp_path, closes)
    r = pr.run_simulated_paper(repo_root=str(tmp_path), write=False)
    assert r["kill_switch_triggered"] is True
    assert r["halted_at_end"] is True
    reasons = [e["reason"] for e in r["kill_switch_events"]]
    assert "daily_loss_halt" in reasons


def test_hard_drawdown_kill_triggers(tmp_path):
    top = _rising(240)
    last = top[-1]
    decline = []
    p = last
    for _ in range(8):  # -9.9%/day: each day above the -10% daily halt, cumulative crosses -50%
        p *= 0.901
        decline.append(p)
    _ready(tmp_path, top + decline)
    r = pr.run_simulated_paper(repo_root=str(tmp_path), write=False)
    assert r["kill_switch_triggered"] is True
    assert r["halted_at_end"] is True
    reasons = [e["reason"] for e in r["kill_switch_events"]]
    assert "hard_drawdown_kill" in reasons


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_complete_and_blocked(tmp_path):
    _ready(tmp_path, _rising(230))
    complete = pr.run_simulated_paper(repo_root=str(tmp_path), write=False)
    blocked = pr.run_simulated_paper(repo_root=str(tmp_path / "missing"), write=False)
    assert pr.validate_paper_run_report(complete)["valid"] is True
    assert pr.validate_paper_run_report(blocked)["valid"] is True


def test_validate_rejects_unlocked_gate(tmp_path):
    _ready(tmp_path, _rising(230))
    r = pr.run_simulated_paper(repo_root=str(tmp_path), write=False)
    r["micro_live_gate_locked"] = False
    v = pr.validate_paper_run_report(r)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_real_order_capability(tmp_path):
    _ready(tmp_path, _rising(230))
    r = pr.run_simulated_paper(repo_root=str(tmp_path), write=False)
    r["executes_real_orders"] = True
    v = pr.validate_paper_run_report(r)
    assert v["valid"] is False
    assert any("capability_not_false:executes_real_orders" in e for e in v["errors"])


def test_validate_rejects_real_orders_placed(tmp_path):
    _ready(tmp_path, _rising(230))
    r = pr.run_simulated_paper(repo_root=str(tmp_path), write=False)
    r["trade_summary"]["real_orders_placed"] = 1
    v = pr.validate_paper_run_report(r)
    assert v["valid"] is False
    assert any("real_orders_placed_nonzero" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string(tmp_path):
    _ready(tmp_path, _rising(230))
    md = pr.render_paper_run_markdown(pr.run_simulated_paper(repo_root=str(tmp_path), write=False))
    assert md.startswith("# Crypto-D1 V2 SIMULATED Paper-Trading Run")
    assert "NO LIVE MONEY" in md and "LOCKED" in md
    assert "V2_trend_plus_cash_regime" in md


# --------------------------------------------------------------------------- #
# no network / credential imports
# --------------------------------------------------------------------------- #
def test_module_imports_no_network_or_credential_modules():
    with open(pr.__file__, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read())
    banned = {"urllib", "requests", "socket", "http", "ftplib", "ccxt", "databento", "dotenv", "smtplib"}
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imported.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not (imported & banned)

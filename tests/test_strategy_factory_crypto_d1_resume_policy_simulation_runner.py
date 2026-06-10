"""Tests for the Crypto-D1 V2 Resume-Policy SIMULATION Runner (READ-ONLY, NO LIVE MONEY).

Every input is a FAKE local CSV written under tmp_path plus a FAKE in-memory variant report
that satisfies the paper-prep readiness gate. No network, no credentials, no real data, no
broker, no exchange, no real order, no optimization, no gate unlocked. The simulation runs
entirely on synthetic prices over the FIXED regime windows from the research plan."""

from __future__ import annotations

import ast
import datetime
import json

import sparta_commander.strategy_factory_crypto_d1_resume_policy_simulation_runner as rs
import sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner as qa

_SRC = "binance_usdt_spot_frozen_regime_inputs"
_CANON = ",".join(qa.QA_REQUIRED_FIELDS)


def _csv_from_closes(closes: list[float]) -> str:
    rows = [_CANON]
    start = datetime.date(2020, 1, 1)
    prev = closes[0]
    for i, c in enumerate(closes):
        d = (start + datetime.timedelta(days=i)).isoformat()
        o = prev
        hi = max(o, c) * 1.02
        lo = min(o, c) * 0.98
        rows.append(f"{d},{o:.6f},{hi:.6f},{lo:.6f},{c:.6f},1000,{_SRC},spot")
        prev = c
    return "\n".join(rows)


def _variant(vid, *, max_dd, sharpe=1.10, total_return=2.0, trading_days=2128, eligible,
             blockers=None, beats_floor=None):
    if beats_floor is None:
        beats_floor = max_dd >= -0.50
    return {
        "variant_id": vid, "description": vid, "controls": ["trend_filter"],
        "performance": {"max_drawdown": max_dd, "sharpe_ratio": sharpe,
                        "total_return": total_return, "trading_days": trading_days, "cagr": 0.50},
        "beats_drawdown_floor": beats_floor,
        "promotion_decision": "PROMOTE_TO_PAPER_PREP" if eligible else "DO_NOT_PROMOTE_TO_PAPER_YET",
        "eligible_for_paper_prep": eligible, "eligibility_blockers": list(blockers or []),
    }


def _report_v2_eligible():
    return {
        "verdict": "VARIANTS_COMPLETE", "variant_count": 5,
        "variant_results": [
            _variant("V1_trend_filter", max_dd=-0.5349, sharpe=0.92, eligible=False,
                     blockers=["max_drawdown_exceeds_limit"]),
            _variant("V2_trend_plus_cash_regime", max_dd=-0.4816, sharpe=1.10,
                     total_return=11.5528, eligible=True),
            _variant("V3_voltarget_concentration_cap", max_dd=-0.8512, sharpe=0.99,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V4_monthly_rebalance_capped", max_dd=-0.8438, sharpe=1.04,
                     eligible=False, blockers=["max_drawdown_exceeds_limit"]),
            _variant("V5_full_risk_managed", max_dd=-0.5085, sharpe=1.07, eligible=False,
                     blockers=["max_drawdown_exceeds_limit"]),
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


def _rising(n: int, step: float = 1.006, start: float = 100.0):
    out, p = [], start
    for _ in range(n):
        out.append(p)
        p *= step
    return out


def _crash_then_recover():
    """Long rise (SMA warmed), a one-day crash that trips the daily-loss halt and pushes
    price below the 200-day SMA, then a recovery rally that brings breadth back -> a resume
    can fire. All three sleeves share this series."""
    out = _rising(320, step=1.006)
    p = out[-1]
    for _ in range(5):          # ~-14%/day -> below SMA200, first day trips daily-loss halt
        p *= 0.86
        out.append(p)
    for _ in range(150):        # recovery -> breadth returns -> policies may resume
        p *= 1.02
        out.append(p)
    return out


def _ready_full(tmp_path):
    _stage_review(tmp_path, _report_v2_eligible())
    _stage_csvs(tmp_path, _rising(2400))


# --------------------------------------------------------------------------- #
# refusal posture
# --------------------------------------------------------------------------- #
def test_refuses_when_paper_prep_not_ready(tmp_path):
    _stage_csvs(tmp_path, _rising(2400))  # CSVs present but NO approved variant review
    r = rs.run_resume_policy_simulations(repo_root=str(tmp_path), write=True)
    assert r["verdict"] == rs.VERDICT_BLOCKED_NOT_READY
    assert any("paper_prep_not_ready" in b for b in r["blockers"])
    assert r["files_written"] == []


# --------------------------------------------------------------------------- #
# completed reruns: 6 policies x 4 regimes
# --------------------------------------------------------------------------- #
def test_completes_all_policies_and_regimes(tmp_path):
    _ready_full(tmp_path)
    r = rs.run_resume_policy_simulations(repo_root=str(tmp_path), write=False)
    assert r["verdict"] == rs.VERDICT_RERUNS_COMPLETE
    assert r["selected_variant_id"] == "V2_trend_plus_cash_regime"
    assert len(r["policy_results"]) == 6
    ids = [p["policy_id"] for p in r["policy_results"]]
    assert ids == [
        "RP1_wait_7d_trend_on", "RP2_wait_14d_trend_on", "RP3_wait_30d_trend_on",
        "RP4_breadth_2of3_above_sma200", "RP5_half_then_full_on_confirmation",
        "RP6_resume_after_volatility_cools",
    ]
    for p in r["policy_results"]:
        assert len(p["regime_results"]) == 4
        for rr in p["regime_results"]:
            assert rr["evaluated"] is True
            assert rr["metrics"]["real_orders_placed"] == 0


def test_rankings_present(tmp_path):
    _ready_full(tmp_path)
    r = rs.run_resume_policy_simulations(repo_root=str(tmp_path), write=False)
    rk = r["rankings"]
    valid = {p["policy_id"] for p in r["policy_results"]}
    assert rk["best_by_mean_return"] in valid
    assert rk["best_by_worst_drawdown"] in valid
    assert rk["best_by_mean_sharpe"] in valid


# --------------------------------------------------------------------------- #
# safety posture: nothing real, no gate unlocked, no optimization
# --------------------------------------------------------------------------- #
def test_run_is_read_only_and_locks_gates(tmp_path):
    _ready_full(tmp_path)
    r = rs.run_resume_policy_simulations(repo_root=str(tmp_path), write=False)
    for key in ("uses_real_money", "connects_broker", "connects_exchange",
                "executes_real_orders", "uses_network", "uses_credentials",
                "ran_optimization", "ran_parameter_search",
                "parameters_changed_based_on_results", "used_leverage", "used_shorting",
                "used_margin", "unlocks_downstream_gate", "authorizes_live_trading"):
        assert r[key] is False
    assert r["simulated_orders_only"] is True
    assert r["paper_trading_gate_locked"] is True
    assert r["micro_live_gate_locked"] is True
    assert r["live_gate_locked"] is True


def test_writes_only_resume_policy_sim_artifacts(tmp_path):
    _ready_full(tmp_path)
    r = rs.run_resume_policy_simulations(repo_root=str(tmp_path), write=True)
    assert len(r["files_written"]) == 3
    for p in r["files_written"]:
        assert "crypto_d1_resume_policy_sim" in p.replace("\\", "/")
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    assert (out / "resume_policy_sim_log.jsonl").is_file()
    assert (out / "resume_policy_sim_report.json").is_file()
    assert (out / "resume_policy_sim_report.md").is_file()
    for line in (out / "resume_policy_sim_log.jsonl").read_text(encoding="utf-8").splitlines():
        assert json.loads(line)["real_orders_placed"] == 0


# --------------------------------------------------------------------------- #
# kill + resume cycle actually exercised
# --------------------------------------------------------------------------- #
def test_kill_then_resume_in_crash_regime(tmp_path):
    _stage_review(tmp_path, _report_v2_eligible())
    _stage_csvs(tmp_path, _crash_then_recover())
    r = rs.run_resume_policy_simulations(repo_root=str(tmp_path), write=False)
    rp4 = next(p for p in r["policy_results"] if p["policy_id"] == "RP4_breadth_2of3_above_sma200")
    crash = next(rr for rr in rp4["regime_results"] if rr["regime_id"] == "2021_bull_then_may_crash")
    assert crash["evaluated"] is True
    m = crash["metrics"]
    assert m["num_kill_events"] >= 1
    assert m["num_resume_events"] >= 1
    assert m["real_orders_placed"] == 0


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_complete_and_blocked(tmp_path):
    _ready_full(tmp_path)
    complete = rs.run_resume_policy_simulations(repo_root=str(tmp_path), write=False)
    blocked = rs.run_resume_policy_simulations(repo_root=str(tmp_path / "missing"), write=False)
    assert rs.validate_resume_policy_simulation_report(complete)["valid"] is True
    assert rs.validate_resume_policy_simulation_report(blocked)["valid"] is True


def test_validate_rejects_unlocked_gate(tmp_path):
    _ready_full(tmp_path)
    r = rs.run_resume_policy_simulations(repo_root=str(tmp_path), write=False)
    r["micro_live_gate_locked"] = False
    v = rs.validate_resume_policy_simulation_report(r)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_optimization_flag(tmp_path):
    _ready_full(tmp_path)
    r = rs.run_resume_policy_simulations(repo_root=str(tmp_path), write=False)
    r["ran_optimization"] = True
    v = rs.validate_resume_policy_simulation_report(r)
    assert v["valid"] is False
    assert any("capability_not_false:ran_optimization" in e for e in v["errors"])


def test_validate_rejects_params_changed_flag(tmp_path):
    _ready_full(tmp_path)
    r = rs.run_resume_policy_simulations(repo_root=str(tmp_path), write=False)
    r["parameters_changed_based_on_results"] = True
    v = rs.validate_resume_policy_simulation_report(r)
    assert v["valid"] is False
    assert any("capability_not_false:parameters_changed_based_on_results" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string(tmp_path):
    _ready_full(tmp_path)
    md = rs.render_resume_policy_simulation_markdown(
        rs.run_resume_policy_simulations(repo_root=str(tmp_path), write=False))
    assert md.startswith("# Crypto-D1 V2 Resume-Policy SIMULATION")
    assert "NO LIVE MONEY" in md and "LOCKED" in md
    assert "RP4_breadth_2of3_above_sma200" in md


# --------------------------------------------------------------------------- #
# no network / credential imports
# --------------------------------------------------------------------------- #
def test_module_imports_no_network_or_credential_modules():
    with open(rs.__file__, "r", encoding="utf-8") as fh:
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

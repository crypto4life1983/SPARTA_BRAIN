"""Tests for the Crypto-D1 V2 RC1 Out-of-Sample REPLAY Runner (READ-ONLY, NO LIVE MONEY).

Every input is a FAKE local CSV / report written under tmp_path. No network, no
credentials, no real data, no broker, no exchange, no real order, no optimization, no gate
unlocked. The runner replays the single evidence-leading resume policy with parameters
UNCHANGED over the FIXED Block 180 windows and preserves DO_NOT_PROMOTE_RESUME_POLICY_YET."""

from __future__ import annotations

import ast
import datetime
import json

import sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_replay_runner as rp
import sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner as qa
import sparta_commander.strategy_factory_crypto_d1_resume_policy_simulation_runner as rs

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


def _policy(pid, *, mean_ret, worst_dd, mean_sharpe, regimes=4, real_orders=0):
    regime_results = []
    for k in range(regimes):
        regime_results.append({
            "regime_id": f"regime_{k}", "window": "2021-01-01..2021-12-31",
            "evaluated": True,
            "metrics": {
                "total_return": mean_ret, "max_drawdown": worst_dd,
                "sharpe_ratio": mean_sharpe, "real_orders_placed": real_orders,
                "num_kill_events": 1, "num_resume_events": 1, "halted_at_end": False,
            },
        })
    return {
        "policy_id": pid, "description": pid, "reentry_exposure": "FULL",
        "regime_results": regime_results,
        "aggregate": {
            "regimes_evaluated": regimes, "mean_total_return": mean_ret,
            "min_total_return": mean_ret, "worst_max_drawdown": worst_dd,
            "mean_sharpe_ratio": mean_sharpe,
        },
    }


def _sim_report(*, rankings_leader="RP6_resume_after_volatility_cools"):
    from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import build_paper_prep_config
    rep = rs._base_report(build_paper_prep_config())
    rep.update({
        "verdict": rs.VERDICT_RERUNS_COMPLETE,
        "blockers": [],
        "selected_variant_id": "V2_trend_plus_cash_regime",
        "symbols": ["BTC", "ETH", "SOL"],
        "policy_results": [
            _policy("RP1_wait_7d_trend_on", mean_ret=0.68, worst_dd=-0.61, mean_sharpe=0.09),
            _policy("RP6_resume_after_volatility_cools", mean_ret=1.55, worst_dd=-0.32,
                    mean_sharpe=0.57),
        ],
        "rankings": {
            "best_by_mean_return": rankings_leader,
            "best_by_worst_drawdown": rankings_leader,
            "best_by_mean_sharpe": rankings_leader,
        },
        "files_read": [], "files_written": [],
    })
    return rep


def _stage_review(tmp_path):
    rep_dir = tmp_path / "reports" / "crypto_d1_variant_backtest"
    rep_dir.mkdir(parents=True, exist_ok=True)
    (rep_dir / "variant_backtest_report.json").write_text(
        json.dumps(_report_v2_eligible()), encoding="utf-8"
    )


def _stage_sim_report(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "resume_policy_sim_report.json").write_text(
        json.dumps(_sim_report()), encoding="utf-8"
    )


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


def _ready_full(tmp_path):
    _stage_review(tmp_path)
    _stage_sim_report(tmp_path)
    _stage_csvs(tmp_path, _rising(2400))


# --------------------------------------------------------------------------- #
# refusal posture: blocked runs write nothing
# --------------------------------------------------------------------------- #
def test_refuses_when_paper_prep_not_ready(tmp_path):
    _stage_sim_report(tmp_path)
    _stage_csvs(tmp_path, _rising(2400))  # no approved variant review
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=True)
    assert r["verdict"] == rp.VERDICT_BLOCKED_NOT_READY
    assert any("paper_prep_not_ready" in b for b in r["blockers"])
    assert r["files_written"] == []
    assert not (tmp_path / "reports" / "crypto_d1_rc1_out_of_sample_replay").exists()


def test_refuses_when_rc1_spec_not_ready(tmp_path):
    _stage_review(tmp_path)
    _stage_csvs(tmp_path, _rising(2400))  # no resume-policy sim report -> spec BLOCKED
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=True)
    assert r["verdict"] == rp.VERDICT_BLOCKED_NOT_READY
    assert any("rc1_spec_not_ready" in b for b in r["blockers"])
    assert r["files_written"] == []
    assert not (tmp_path / "reports" / "crypto_d1_rc1_out_of_sample_replay").exists()


# --------------------------------------------------------------------------- #
# completed replays: RP6 unchanged over the 4 fixed Block 180 windows
# --------------------------------------------------------------------------- #
def test_completes_all_windows_with_leading_policy(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False)
    assert r["verdict"] == rp.VERDICT_REPLAYS_COMPLETE
    assert r["selected_variant_id"] == "V2_trend_plus_cash_regime"
    assert r["policy_id"] == "RP6_resume_after_volatility_cools"
    assert r["policy_parameters_changed"] is False
    assert len(r["window_results"]) == 4
    ids = [w["window_id"] for w in r["window_results"]]
    assert ids == [
        "OOS_W1_2020_early_held_out", "OOS_W2_2021H2_2022H1_straddle",
        "OOS_W3_2022H2_2023H1_straddle", "OOS_W4_2024H2_2025H1_straddle",
    ]
    for wr in r["window_results"]:
        assert wr["evaluated"] is True
        assert wr["metrics"]["real_orders_placed"] == 0


def test_held_out_window_uses_btc_eth_only(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False)
    held = next(w for w in r["window_results"]
                if w["window_id"] == "OOS_W1_2020_early_held_out")
    assert held["symbols"] == ["BTC", "ETH"]
    straddle = next(w for w in r["window_results"]
                    if w["window_id"] == "OOS_W2_2021H2_2022H1_straddle")
    assert straddle["symbols"] == ["BTC", "ETH", "SOL"]


def test_carries_in_sample_reference_without_recompute(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False)
    ref = r["in_sample_reference"]
    # carried verbatim from the staged fake evidence (RP6 aggregate)
    assert ref["mean_total_return"] == 1.55
    assert ref["worst_max_drawdown"] == -0.32


def test_preserves_do_not_promote(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False)
    assert r["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert r["promotes_resume_policy"] is False
    assert r["next_required_action"] == "HUMAN_REVIEW_OF_RC1_OUT_OF_SAMPLE_RESULTS"


# --------------------------------------------------------------------------- #
# safety posture: nothing real, no gate unlocked, no optimization
# --------------------------------------------------------------------------- #
def test_run_is_read_only_and_locks_gates(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False)
    for key in ("uses_real_money", "connects_broker", "connects_exchange",
                "executes_real_orders", "uses_network", "uses_credentials",
                "ran_optimization", "ran_parameter_search",
                "parameters_changed_based_on_results", "used_leverage", "used_shorting",
                "used_margin", "unlocks_downstream_gate", "authorizes_live_trading",
                "promotes_resume_policy"):
        assert r[key] is False, key
    assert r["simulated_orders_only"] is True
    assert r["paper_trading_gate_locked"] is True
    assert r["micro_live_gate_locked"] is True
    assert r["live_gate_locked"] is True


def test_writes_only_rc1_replay_artifacts(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=True)
    assert len(r["files_written"]) == 3
    for p in r["files_written"]:
        assert "crypto_d1_rc1_out_of_sample_replay" in p.replace("\\", "/")
    out = tmp_path / "reports" / "crypto_d1_rc1_out_of_sample_replay"
    assert (out / "rc1_oos_replay_log.jsonl").is_file()
    assert (out / "rc1_oos_replay_report.json").is_file()
    assert (out / "rc1_oos_replay_report.md").is_file()
    for line in (out / "rc1_oos_replay_log.jsonl").read_text(encoding="utf-8").splitlines():
        assert json.loads(line)["real_orders_placed"] == 0
    # it never touches the Block 176 report directory
    sim_dir = tmp_path / "reports" / "crypto_d1_resume_policy_sim"
    assert sorted(p.name for p in sim_dir.iterdir()) == ["resume_policy_sim_report.json"]


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_complete_and_blocked(tmp_path):
    _ready_full(tmp_path)
    complete = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False)
    blocked = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path / "missing"), write=False)
    assert rp.validate_rc1_out_of_sample_replay_report(complete)["valid"] is True
    assert rp.validate_rc1_out_of_sample_replay_report(blocked)["valid"] is True


def test_validate_rejects_unlocked_gate(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False)
    r["micro_live_gate_locked"] = False
    v = rp.validate_rc1_out_of_sample_replay_report(r)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_promote_decision(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False)
    r["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = rp.validate_rc1_out_of_sample_replay_report(r)
    assert v["valid"] is False
    assert any("human_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_changed_parameters(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False)
    r["policy_parameters_changed"] = True
    v = rp.validate_rc1_out_of_sample_replay_report(r)
    assert v["valid"] is False
    assert any("policy_parameters_changed" in e for e in v["errors"])


def test_validate_rejects_optimization_flag(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False)
    r["ran_optimization"] = True
    v = rp.validate_rc1_out_of_sample_replay_report(r)
    assert v["valid"] is False
    assert any("capability_not_false:ran_optimization" in e for e in v["errors"])


def test_validate_rejects_missing_held_out_evaluation(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False)
    for wr in r["window_results"]:
        if wr["window_id"] == "OOS_W1_2020_early_held_out":
            wr["evaluated"] = False
    v = rp.validate_rc1_out_of_sample_replay_report(r)
    assert v["valid"] is False
    assert "held_out_window_not_evaluated" in v["errors"]


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string(tmp_path):
    _ready_full(tmp_path)
    md = rp.render_rc1_out_of_sample_replay_markdown(
        rp.run_rc1_out_of_sample_replays(repo_root=str(tmp_path), write=False))
    assert md.startswith("# Crypto-D1 V2 RC1 Out-of-Sample REPLAY")
    assert "NO LIVE MONEY" in md and "LOCKED" in md
    assert "OOS_W1_2020_early_held_out" in md
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md


# --------------------------------------------------------------------------- #
# label / no network or credential imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert rp.get_rc1_replay_label() == rp.RC1_REPLAY_LABEL
    assert "READ-ONLY" in rp.RC1_REPLAY_LABEL
    assert rp.RC1_REPLAY_MODE == "RESEARCH_ONLY"


def test_module_imports_no_network_or_credential_modules():
    with open(rp.__file__, "r", encoding="utf-8") as fh:
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

"""Tests for the Crypto-D1 V2 RC2 Cross-Policy REPLAY Runner (READ-ONLY, NO LIVE MONEY).

Every input is a FAKE local CSV / report written under tmp_path. No network, no
credentials, no real data, no broker, no exchange, no real order, no optimization, no gate
unlocked. The runner replays all six fixed policies with parameters UNCHANGED over the
fixed Block 184 windows and preserves DO_NOT_PROMOTE_RESUME_POLICY_YET."""

from __future__ import annotations

import ast
import datetime
import json

import sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_replay_runner as rc1rp
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_replay_runner as rp
import sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner as qa

_SRC = "binance_usdt_spot_frozen_regime_inputs"
_CANON = ",".join(qa.QA_REQUIRED_FIELDS)

_POLICY_IDS = [
    "RP1_wait_7d_trend_on", "RP2_wait_14d_trend_on", "RP3_wait_30d_trend_on",
    "RP4_breadth_2of3_above_sma200", "RP5_half_then_full_on_confirmation",
    "RP6_resume_after_volatility_cools",
]


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


def _window(wid, wtype, *, ret, dd, sharpe, symbols=None, kills=0, resumes=0):
    return {
        "window_id": wid, "window": "2020-01-01..2020-08-10", "window_type": wtype,
        "symbols": symbols or ["BTC", "ETH", "SOL"],
        "evaluated": True,
        "metrics": {
            "total_return": ret, "max_drawdown": dd, "sharpe_ratio": sharpe,
            "real_orders_placed": 0, "num_kill_events": kills,
            "num_resume_events": resumes, "halted_at_end": False,
        },
    }


def _rc1_replay_report():
    """A fake persisted RC1 replay report satisfying the Block 182/183/184 chain."""
    from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import build_paper_prep_config
    rep = rc1rp._base_report(build_paper_prep_config())
    rep.update({
        "verdict": rc1rp.VERDICT_REPLAYS_COMPLETE,
        "blockers": [],
        "selected_variant_id": "V2_trend_plus_cash_regime",
        "policy_id": "RP6_resume_after_volatility_cools",
        "policy_parameters_changed": False,
        "window_results": [
            _window("OOS_W1_2020_early_held_out", "held_out_early_history",
                    ret=0.4774, dd=-0.0498, sharpe=3.16, symbols=["BTC", "ETH"]),
            _window("OOS_W2_2021H2_2022H1_straddle", "boundary_straddling_robustness",
                    ret=0.3208, dd=-0.4535, sharpe=0.81, kills=1, resumes=1),
            _window("OOS_W3_2022H2_2023H1_straddle", "boundary_straddling_robustness",
                    ret=0.3432, dd=-0.2386, sharpe=1.03),
            _window("OOS_W4_2024H2_2025H1_straddle", "boundary_straddling_robustness",
                    ret=-0.0344, dd=-0.2590, sharpe=0.10),
        ],
        "in_sample_reference": {
            "regimes_evaluated": 4, "mean_total_return": 1.5538,
            "min_total_return": 1.5538, "worst_max_drawdown": -0.3236,
            "mean_sharpe_ratio": 0.57,
        },
        "risk_notes": [], "files_read": [], "files_written": [],
    })
    return rep


def _stage_review(tmp_path):
    rep_dir = tmp_path / "reports" / "crypto_d1_variant_backtest"
    rep_dir.mkdir(parents=True, exist_ok=True)
    (rep_dir / "variant_backtest_report.json").write_text(
        json.dumps(_report_v2_eligible()), encoding="utf-8"
    )


def _stage_rc1_report(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_rc1_out_of_sample_replay"
    out.mkdir(parents=True, exist_ok=True)
    (out / "rc1_oos_replay_report.json").write_text(
        json.dumps(_rc1_replay_report()), encoding="utf-8"
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
    _stage_rc1_report(tmp_path)
    _stage_csvs(tmp_path, _rising(2400))


# --------------------------------------------------------------------------- #
# refusal posture: blocked runs write nothing
# --------------------------------------------------------------------------- #
def test_refuses_when_paper_prep_not_ready(tmp_path):
    _stage_rc1_report(tmp_path)
    _stage_csvs(tmp_path, _rising(2400))  # no approved variant review
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=True)
    assert r["verdict"] == rp.VERDICT_BLOCKED_NOT_READY
    assert any("paper_prep_not_ready" in b for b in r["blockers"])
    assert r["files_written"] == []
    assert not (tmp_path / "reports" / "crypto_d1_rc2_cross_policy_replay").exists()


def test_refuses_when_rc2_spec_not_ready(tmp_path):
    _stage_review(tmp_path)
    _stage_csvs(tmp_path, _rising(2400))  # no RC1 replay report -> spec BLOCKED
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=True)
    assert r["verdict"] == rp.VERDICT_BLOCKED_NOT_READY
    assert any("rc2_spec_not_ready" in b for b in r["blockers"])
    assert r["files_written"] == []
    assert not (tmp_path / "reports" / "crypto_d1_rc2_cross_policy_replay").exists()


# --------------------------------------------------------------------------- #
# completed replays: 6 policies x 4 fixed windows
# --------------------------------------------------------------------------- #
def test_completes_all_policies_and_windows(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
    assert r["verdict"] == rp.VERDICT_REPLAYS_COMPLETE
    assert r["selected_variant_id"] == "V2_trend_plus_cash_regime"
    assert r["policy_parameters_changed"] is False
    assert [p["policy_id"] for p in r["policy_results"]] == _POLICY_IDS
    for p in r["policy_results"]:
        assert len(p["window_results"]) == 4
        for wr in p["window_results"]:
            assert wr["evaluated"] is True
            assert wr["metrics"]["real_orders_placed"] == 0


def test_held_out_window_uses_btc_eth_only_for_every_policy(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
    for p in r["policy_results"]:
        held = next(w for w in p["window_results"]
                    if w["window_id"] == "OOS_W1_2020_early_held_out")
        assert held["symbols"] == ["BTC", "ETH"]


def test_rankings_and_leader_stability_present(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
    rk = r["rankings"]
    valid = {p["policy_id"] for p in r["policy_results"]}
    assert rk["best_by_mean_return"] in valid
    assert rk["best_by_worst_drawdown"] in valid
    assert rk["best_by_mean_sharpe"] in valid
    ls = r["leader_stability"]
    assert ls["rc1_leader_policy_id"] == "RP6_resume_after_volatility_cools"
    assert isinstance(ls["categories_led_by_rc1_leader"], list)
    assert isinstance(ls["rc1_leader_leads_all_categories"], bool)
    assert isinstance(ls["rc1_leader_leads_any_category"], bool)


def test_preserves_do_not_promote(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
    assert r["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert r["promotes_resume_policy"] is False
    assert r["next_required_action"] == "HUMAN_REVIEW_OF_RC2_CROSS_POLICY_RESULTS"


# --------------------------------------------------------------------------- #
# safety posture: nothing real, no gate unlocked, no optimization
# --------------------------------------------------------------------------- #
def test_run_is_read_only_and_locks_gates(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
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


def test_writes_only_rc2_replay_artifacts(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=True)
    assert len(r["files_written"]) == 3
    for p in r["files_written"]:
        assert "crypto_d1_rc2_cross_policy_replay" in p.replace("\\", "/")
    out = tmp_path / "reports" / "crypto_d1_rc2_cross_policy_replay"
    assert (out / "rc2_cross_policy_replay_log.jsonl").is_file()
    assert (out / "rc2_cross_policy_replay_report.json").is_file()
    assert (out / "rc2_cross_policy_replay_report.md").is_file()
    for line in (out / "rc2_cross_policy_replay_log.jsonl").read_text(encoding="utf-8").splitlines():
        assert json.loads(line)["real_orders_placed"] == 0
    # it never touches the RC1 report directory
    rc1_dir = tmp_path / "reports" / "crypto_d1_rc1_out_of_sample_replay"
    assert sorted(p.name for p in rc1_dir.iterdir()) == ["rc1_oos_replay_report.json"]


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_complete_and_blocked(tmp_path):
    _ready_full(tmp_path)
    complete = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
    blocked = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path / "missing"), write=False)
    assert rp.validate_rc2_cross_policy_replay_report(complete)["valid"] is True
    assert rp.validate_rc2_cross_policy_replay_report(blocked)["valid"] is True


def test_validate_rejects_unlocked_gate(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
    r["micro_live_gate_locked"] = False
    v = rp.validate_rc2_cross_policy_replay_report(r)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_promote_decision(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
    r["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = rp.validate_rc2_cross_policy_replay_report(r)
    assert v["valid"] is False
    assert any("human_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_changed_parameters(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
    r["policy_parameters_changed"] = True
    v = rp.validate_rc2_cross_policy_replay_report(r)
    assert v["valid"] is False
    assert any("policy_parameters_changed" in e for e in v["errors"])


def test_validate_rejects_single_policy(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
    r["policy_results"] = r["policy_results"][:1]
    pid = r["policy_results"][0]["policy_id"]
    r["rankings"] = {"best_by_mean_return": pid, "best_by_worst_drawdown": pid,
                     "best_by_mean_sharpe": pid}
    v = rp.validate_rc2_cross_policy_replay_report(r)
    assert v["valid"] is False
    assert "fewer_than_two_policies_compared" in v["errors"]


def test_validate_rejects_missing_held_out_evaluation(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
    for wr in r["policy_results"][0]["window_results"]:
        if wr["window_type"] == "held_out_early_history":
            wr["evaluated"] = False
    v = rp.validate_rc2_cross_policy_replay_report(r)
    assert v["valid"] is False
    assert any(e.startswith("held_out_window_not_evaluated:") for e in v["errors"])


def test_validate_rejects_unknown_ranking(tmp_path):
    _ready_full(tmp_path)
    r = rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False)
    r["rankings"]["best_by_mean_return"] = "RP99_not_a_policy"
    v = rp.validate_rc2_cross_policy_replay_report(r)
    assert v["valid"] is False
    assert any("ranking_missing_or_unknown:best_by_mean_return" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string(tmp_path):
    _ready_full(tmp_path)
    md = rp.render_rc2_cross_policy_replay_markdown(
        rp.run_rc2_cross_policy_replays(repo_root=str(tmp_path), write=False))
    assert md.startswith("# Crypto-D1 V2 RC2 Cross-Policy REPLAY")
    assert "NO LIVE MONEY" in md and "LOCKED" in md
    assert "RP6_resume_after_volatility_cools" in md
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md
    assert "RC1 leader" in md


# --------------------------------------------------------------------------- #
# label / no network or credential imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert rp.get_rc2_replay_label() == rp.RC2_REPLAY_LABEL
    assert "READ-ONLY" in rp.RC2_REPLAY_LABEL
    assert rp.RC2_REPLAY_MODE == "RESEARCH_ONLY"


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

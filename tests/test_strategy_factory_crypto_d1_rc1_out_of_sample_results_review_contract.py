"""Tests for the Crypto-D1 V2 RC1 Out-of-Sample Results Review Contract (READ-ONLY).

Every report consumed here is a FAKE in-memory dict (or one written under tmp_path); no
network, no credentials, no real data, no broker, no exchange, no real order, no replay,
no simulation, no file write, no gate is unlocked. The contract reviews RC1 out-of-sample
replay results as research evidence only and always keeps DO_NOT_PROMOTE_RESUME_POLICY_YET."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_replay_runner as rp
import sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_results_review_contract as rv


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


def _replay_report(*, complete=True, override=None):
    """A valid Block 181 replay report mirroring the committed real evidence shape."""
    from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import build_paper_prep_config
    rep = rp._base_report(build_paper_prep_config())
    rep.update({
        "verdict": rp.VERDICT_REPLAYS_COMPLETE if complete else rp.VERDICT_BLOCKED_NOT_READY,
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
    if override:
        rep.update(override)
    return rep


def _stage_report(tmp_path, report=None):
    out = tmp_path / "reports" / "crypto_d1_rc1_out_of_sample_replay"
    out.mkdir(parents=True, exist_ok=True)
    (out / "rc1_oos_replay_report.json").write_text(
        json.dumps(report or _replay_report()), encoding="utf-8"
    )


# --------------------------------------------------------------------------- #
# the real outcome -> REVIEW COMPLETE, DO NOT PROMOTE, degradation acknowledged
# --------------------------------------------------------------------------- #
def test_review_complete_keeps_do_not_promote():
    d = rv.review_rc1_oos_results(_replay_report())
    assert d["verdict"] == rv.VERDICT_RC1_REVIEW_COMPLETE
    assert d["promotion_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert d["approved_for_execution"] is False
    assert d["human_review_required"] is True
    assert d["policy_id"] == "RP6_resume_after_volatility_cools"
    assert d["results_valid"] is True
    assert d["next_required_action"] == "HUMAN_DECISION_ON_RC1_OUT_OF_SAMPLE_EVIDENCE"
    # only the structural blocker remains on a complete review
    assert d["blockers"] == ["execution_promotion_requires_separate_human_review"]


def test_review_acknowledges_useful_but_degraded_oos_evidence():
    d = rv.review_rc1_oos_results(_replay_report())
    deg = d["degradation"]
    # useful: the truly held-out window was evaluated and positive
    assert deg["held_out_window_evaluated"] is True
    assert deg["held_out_window_positive"] is True
    assert "held_out_window_evidence_useful_policy_survived_unseen_history" in d["risk_notes"]
    # degraded: OOS mean return far below in-sample, OOS worst DD worse than in-sample
    assert deg["return_materially_degraded"] is True
    assert deg["drawdown_worse_than_in_sample"] is True
    assert deg["materially_degraded_versus_in_sample"] is True
    assert "oos_performance_materially_degraded_versus_in_sample" in d["risk_notes"]
    assert "oos_mean_return_materially_below_in_sample" in d["risk_notes"]
    assert "oos_worst_drawdown_worse_than_in_sample" in d["risk_notes"]
    assert "negative_return_window:OOS_W4_2024H2_2025H1_straddle" in d["risk_notes"]
    assert "oos_evidence_supports_keeping_do_not_promote" in d["risk_notes"]


def test_degradation_numbers_are_pure_arithmetic():
    d = rv.review_rc1_oos_results(_replay_report())
    deg = d["degradation"]
    assert deg["oos_windows_evaluated"] == 4
    expected_mean = (0.4774 + 0.3208 + 0.3432 - 0.0344) / 4
    assert abs(deg["oos_mean_total_return"] - expected_mean) < 1e-12
    assert deg["oos_worst_max_drawdown"] == -0.4535
    assert deg["in_sample_mean_total_return"] == 1.5538
    assert deg["in_sample_worst_max_drawdown"] == -0.3236


# --------------------------------------------------------------------------- #
# the review unlocks nothing
# --------------------------------------------------------------------------- #
def test_review_unlocks_nothing():
    d = rv.review_rc1_oos_results(_replay_report())
    assert d["paper_trading_gate_locked"] is True
    assert d["micro_live_gate_locked"] is True
    assert d["live_gate_locked"] is True
    for key in (
        "executes", "writes_files", "runs_replay", "runs_simulation", "runs_backtest",
        "runs_optimization", "ran_parameter_search", "parameters_changed_based_on_results",
        "fetches_data", "connects_broker", "connects_exchange", "uses_real_money",
        "uses_network", "uses_credentials", "authorizes_paper_execution",
        "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
        "promotes_resume_policy", "unlocks_downstream_gate",
    ):
        assert d[key] is False, key


# --------------------------------------------------------------------------- #
# invalid / missing upstream input
# --------------------------------------------------------------------------- #
def test_missing_report_blocks():
    d = rv.review_rc1_oos_results(None)
    assert d["verdict"] == rv.VERDICT_RC1_REVIEW_BLOCKED
    assert "rc1_oos_replay_report_missing" in d["blockers"]
    assert d["promotion_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


def test_incomplete_replay_blocks():
    d = rv.review_rc1_oos_results(_replay_report(complete=False))
    assert d["verdict"] == rv.VERDICT_RC1_REVIEW_BLOCKED
    assert "rc1_oos_replay_not_complete" in d["blockers"]


def test_invalid_replay_safety_blocks():
    rep = _replay_report()
    rep["micro_live_gate_locked"] = False  # breaks Block 181's own validator
    d = rv.review_rc1_oos_results(rep)
    assert d["verdict"] == rv.VERDICT_RC1_REVIEW_BLOCKED
    assert "rc1_oos_replay_safety_invalid" in d["blockers"]


def test_real_orders_block():
    rep = _replay_report()
    rep["window_results"][1]["metrics"]["real_orders_placed"] = 1
    d = rv.review_rc1_oos_results(rep)
    assert d["verdict"] == rv.VERDICT_RC1_REVIEW_BLOCKED
    assert any(b.startswith("real_orders_detected:") for b in d["blockers"])


def test_changed_parameters_block():
    rep = _replay_report()
    rep["policy_parameters_changed"] = True
    d = rv.review_rc1_oos_results(rep)
    assert d["verdict"] == rv.VERDICT_RC1_REVIEW_BLOCKED
    assert "policy_parameters_changed" in d["blockers"]


def test_missing_held_out_window_blocks():
    rep = _replay_report()
    for wr in rep["window_results"]:
        if wr["window_type"] == "held_out_early_history":
            wr["evaluated"] = False
            wr["metrics"] = None
    d = rv.review_rc1_oos_results(rep)
    assert d["verdict"] == rv.VERDICT_RC1_REVIEW_BLOCKED
    assert "held_out_window_not_evaluated" in d["blockers"]


# --------------------------------------------------------------------------- #
# disk-backed build
# --------------------------------------------------------------------------- #
def test_build_reads_local_report(tmp_path):
    _stage_report(tmp_path)
    d = rv.build_rc1_oos_results_review_decision(repo_root=str(tmp_path))
    assert d["rc1_oos_replay_report_found"] is True
    assert d["verdict"] == rv.VERDICT_RC1_REVIEW_COMPLETE
    assert d["promotion_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


def test_build_handles_missing_local_report(tmp_path):
    d = rv.build_rc1_oos_results_review_decision(repo_root=str(tmp_path))
    assert d["rc1_oos_replay_report_found"] is False
    assert d["verdict"] == rv.VERDICT_RC1_REVIEW_BLOCKED
    assert "rc1_oos_replay_report_missing" in d["blockers"]


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_complete_and_blocked():
    complete = rv.review_rc1_oos_results(_replay_report())
    blocked = rv.review_rc1_oos_results(None)
    assert rv.validate_rc1_oos_results_review_decision(complete)["valid"] is True
    assert rv.validate_rc1_oos_results_review_decision(blocked)["valid"] is True
    # every decision carries the structural promotion blocker
    assert "execution_promotion_requires_separate_human_review" in complete["blockers"]
    assert "execution_promotion_requires_separate_human_review" in blocked["blockers"]


def test_validate_rejects_unlocked_gate():
    d = rv.review_rc1_oos_results(_replay_report())
    d["micro_live_gate_locked"] = False
    v = rv.validate_rc1_oos_results_review_decision(d)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_promote_decision():
    d = rv.review_rc1_oos_results(_replay_report())
    d["promotion_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = rv.validate_rc1_oos_results_review_decision(d)
    assert v["valid"] is False
    assert any("promotion_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_marked_approved():
    d = rv.review_rc1_oos_results(_replay_report())
    d["approved_for_execution"] = True
    v = rv.validate_rc1_oos_results_review_decision(d)
    assert v["valid"] is False
    assert any("decision_marked_approved" in e for e in v["errors"])


def test_validate_rejects_missing_structural_blocker():
    d = rv.review_rc1_oos_results(_replay_report())
    d["blockers"] = []
    v = rv.validate_rc1_oos_results_review_decision(d)
    assert v["valid"] is False
    assert any("missing_structural_promotion_blocker" in e for e in v["errors"])


def test_validate_rejects_capability_true():
    d = rv.review_rc1_oos_results(_replay_report())
    d["runs_replay"] = True
    v = rv.validate_rc1_oos_results_review_decision(d)
    assert v["valid"] is False
    assert any("capability_not_false:runs_replay" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = rv.render_rc1_oos_results_review_markdown(
        rv.review_rc1_oos_results(_replay_report())
    )
    assert md.startswith("# Crypto-D1 V2 RC1 Out-of-Sample Results Review")
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md and "LOCKED" in md
    assert "OOS_W1_2020_early_held_out" in md
    assert "Materially degraded versus in-sample: True" in md


# --------------------------------------------------------------------------- #
# label / no network or credential imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert rv.get_rc1_oos_results_review_label() == rv.RC1_REVIEW_LABEL
    assert "READ-ONLY" in rv.RC1_REVIEW_LABEL
    assert rv.RC1_REVIEW_MODE == "RESEARCH_ONLY"


def test_module_imports_no_network_or_credential_modules():
    with open(rv.__file__, "r", encoding="utf-8") as fh:
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

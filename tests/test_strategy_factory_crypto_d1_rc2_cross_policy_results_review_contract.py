"""Tests for the Crypto-D1 V2 RC2 Cross-Policy Results Review Contract (READ-ONLY).

Every report consumed here is a FAKE in-memory dict (or one written under tmp_path); no
network, no credentials, no real data, no broker, no exchange, no real order, no replay,
no simulation, no file write, no gate is unlocked. The contract reviews RC2 cross-policy
replay results as research evidence only, records the leadership flip honestly, and always
keeps DO_NOT_PROMOTE_RESUME_POLICY_YET."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_replay_runner as rp
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_results_review_contract as rv

_WINDOW_IDS = [
    ("OOS_W1_2020_early_held_out", "held_out_early_history"),
    ("OOS_W2_2021H2_2022H1_straddle", "boundary_straddling_robustness"),
    ("OOS_W3_2022H2_2023H1_straddle", "boundary_straddling_robustness"),
    ("OOS_W4_2024H2_2025H1_straddle", "boundary_straddling_robustness"),
]


def _policy(pid, *, mean_ret, worst_dd, mean_sharpe, real_orders=0):
    window_results = []
    for wid, wtype in _WINDOW_IDS:
        window_results.append({
            "window_id": wid, "window": "2020-01-01..2020-08-10", "window_type": wtype,
            "symbols": ["BTC", "ETH"], "evaluated": True,
            "metrics": {
                "total_return": mean_ret, "max_drawdown": worst_dd,
                "sharpe_ratio": mean_sharpe, "real_orders_placed": real_orders,
                "num_kill_events": 0, "num_resume_events": 0, "halted_at_end": False,
            },
        })
    return {
        "policy_id": pid, "description": pid, "reentry_exposure": "FULL",
        "window_results": window_results,
        "aggregate": {
            "windows_evaluated": 4, "mean_total_return": mean_ret,
            "min_total_return": mean_ret, "worst_max_drawdown": worst_dd,
            "mean_sharpe_ratio": mean_sharpe,
        },
    }


def _replay_report(*, complete=True, leader_flipped=True):
    """A fake Block 185 report mirroring the committed real evidence: RP6 (RC1 leader)
    leads nothing; RP4/RP5 lead the categories."""
    from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import build_paper_prep_config
    rep = rp._base_report(build_paper_prep_config())
    results = [
        _policy("RP1_wait_7d_trend_on", mean_ret=0.4089, worst_dd=-0.4141, mean_sharpe=1.43),
        _policy("RP2_wait_14d_trend_on", mean_ret=0.3404, worst_dd=-0.4141, mean_sharpe=1.36),
        _policy("RP3_wait_30d_trend_on", mean_ret=0.3002, worst_dd=-0.4147, mean_sharpe=1.31),
        _policy("RP4_breadth_2of3_above_sma200", mean_ret=0.4206, worst_dd=-0.4141, mean_sharpe=1.43),
        _policy("RP5_half_then_full_on_confirmation", mean_ret=0.4187, worst_dd=-0.4140, mean_sharpe=1.44),
        _policy("RP6_resume_after_volatility_cools", mean_ret=0.2767, worst_dd=-0.4535, mean_sharpe=1.28),
    ]
    if leader_flipped:
        rankings = {
            "best_by_mean_return": "RP4_breadth_2of3_above_sma200",
            "best_by_worst_drawdown": "RP5_half_then_full_on_confirmation",
            "best_by_mean_sharpe": "RP5_half_then_full_on_confirmation",
        }
        stability = {
            "rc1_leader_policy_id": "RP6_resume_after_volatility_cools",
            "categories_led_by_rc1_leader": [],
            "rc1_leader_leads_all_categories": False,
            "rc1_leader_leads_any_category": False,
        }
    else:
        rankings = {
            "best_by_mean_return": "RP6_resume_after_volatility_cools",
            "best_by_worst_drawdown": "RP6_resume_after_volatility_cools",
            "best_by_mean_sharpe": "RP6_resume_after_volatility_cools",
        }
        stability = {
            "rc1_leader_policy_id": "RP6_resume_after_volatility_cools",
            "categories_led_by_rc1_leader": [
                "mean_total_return", "worst_max_drawdown", "mean_sharpe_ratio"
            ],
            "rc1_leader_leads_all_categories": True,
            "rc1_leader_leads_any_category": True,
        }
    rep.update({
        "verdict": rp.VERDICT_REPLAYS_COMPLETE if complete else rp.VERDICT_BLOCKED_NOT_READY,
        "blockers": [],
        "selected_variant_id": "V2_trend_plus_cash_regime",
        "policy_parameters_changed": False,
        "policy_results": results,
        "rankings": rankings,
        "leader_stability": stability,
        "risk_notes": [], "files_read": [], "files_written": [],
    })
    return rep


def _stage_report(tmp_path, report=None):
    out = tmp_path / "reports" / "crypto_d1_rc2_cross_policy_replay"
    out.mkdir(parents=True, exist_ok=True)
    (out / "rc2_cross_policy_replay_report.json").write_text(
        json.dumps(report or _replay_report()), encoding="utf-8"
    )


# --------------------------------------------------------------------------- #
# the real outcome -> REVIEW COMPLETE, DO NOT PROMOTE, leadership flip recorded
# --------------------------------------------------------------------------- #
def test_review_complete_keeps_do_not_promote():
    d = rv.review_rc2_cross_policy_results(_replay_report())
    assert d["verdict"] == rv.VERDICT_RC2_REVIEW_COMPLETE
    assert d["promotion_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert d["approved_for_execution"] is False
    assert d["human_review_required"] is True
    assert d["results_valid"] is True
    assert d["next_required_action"] == "HUMAN_DECISION_ON_RC2_CROSS_POLICY_EVIDENCE"
    assert d["blockers"] == ["execution_promotion_requires_separate_human_review"]


def test_review_records_leadership_flip():
    d = rv.review_rc2_cross_policy_results(_replay_report())
    la = d["leadership_analysis"]
    assert la["rc1_leader_policy_id"] == "RP6_resume_after_volatility_cools"
    assert la["leadership_flip_confirmed"] is True
    assert la["categories_led_by_rc1_leader"] == []
    assert la["current_category_leaders"]["best_by_mean_return"] == (
        "RP4_breadth_2of3_above_sma200"
    )
    # on this evidence every other fixed candidate dominates RP6 on all categories
    assert set(la["policies_dominating_rc1_leader"]) == {
        "RP1_wait_7d_trend_on", "RP2_wait_14d_trend_on", "RP3_wait_30d_trend_on",
        "RP4_breadth_2of3_above_sma200", "RP5_half_then_full_on_confirmation",
    }
    assert "rc1_leader_leads_zero_oos_categories" in d["risk_notes"]
    assert "in_sample_leadership_did_not_survive_out_of_sample" in d["risk_notes"]
    assert (
        "policy_dominates_rc1_leader_out_of_sample:RP4_breadth_2of3_above_sma200"
        in d["risk_notes"]
    )
    assert "rankings_are_research_evidence_only_not_selection" in d["risk_notes"]
    assert "choosing_any_successor_policy_is_a_separate_human_decision" in d["risk_notes"]
    assert "oos_evidence_supports_keeping_do_not_promote" in d["risk_notes"]


def test_review_handles_stable_leader_without_flip_notes():
    d = rv.review_rc2_cross_policy_results(_replay_report(leader_flipped=False))
    la = d["leadership_analysis"]
    assert la["leadership_flip_confirmed"] is False
    assert la["rc1_leader_leads_all_categories"] is True
    assert "rc1_leader_kept_full_lead_out_of_sample" in d["risk_notes"]
    assert "rc1_leader_leads_zero_oos_categories" not in d["risk_notes"]
    # even a stable leader is never promoted by this review
    assert d["promotion_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


# --------------------------------------------------------------------------- #
# the review unlocks nothing
# --------------------------------------------------------------------------- #
def test_review_unlocks_nothing():
    d = rv.review_rc2_cross_policy_results(_replay_report())
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
    d = rv.review_rc2_cross_policy_results(None)
    assert d["verdict"] == rv.VERDICT_RC2_REVIEW_BLOCKED
    assert "rc2_replay_report_missing" in d["blockers"]
    assert "execution_promotion_requires_separate_human_review" in d["blockers"]
    assert d["promotion_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


def test_incomplete_replay_blocks():
    d = rv.review_rc2_cross_policy_results(_replay_report(complete=False))
    assert d["verdict"] == rv.VERDICT_RC2_REVIEW_BLOCKED
    assert "rc2_replay_not_complete" in d["blockers"]


def test_invalid_replay_safety_blocks():
    rep = _replay_report()
    rep["micro_live_gate_locked"] = False  # breaks Block 185's own validator
    d = rv.review_rc2_cross_policy_results(rep)
    assert d["verdict"] == rv.VERDICT_RC2_REVIEW_BLOCKED
    assert "rc2_replay_safety_invalid" in d["blockers"]


def test_real_orders_block():
    rep = _replay_report()
    rep["policy_results"][2]["window_results"][1]["metrics"]["real_orders_placed"] = 1
    d = rv.review_rc2_cross_policy_results(rep)
    assert d["verdict"] == rv.VERDICT_RC2_REVIEW_BLOCKED
    assert any(b.startswith("real_orders_detected:") for b in d["blockers"])


def test_changed_parameters_block():
    rep = _replay_report()
    rep["policy_parameters_changed"] = True
    d = rv.review_rc2_cross_policy_results(rep)
    assert d["verdict"] == rv.VERDICT_RC2_REVIEW_BLOCKED
    assert "policy_parameters_changed" in d["blockers"]


# --------------------------------------------------------------------------- #
# disk-backed build
# --------------------------------------------------------------------------- #
def test_build_reads_local_report(tmp_path):
    _stage_report(tmp_path)
    d = rv.build_rc2_cross_policy_results_review_decision(repo_root=str(tmp_path))
    assert d["rc2_replay_report_found"] is True
    assert d["verdict"] == rv.VERDICT_RC2_REVIEW_COMPLETE
    assert d["leadership_analysis"]["leadership_flip_confirmed"] is True


def test_build_handles_missing_local_report(tmp_path):
    d = rv.build_rc2_cross_policy_results_review_decision(repo_root=str(tmp_path))
    assert d["rc2_replay_report_found"] is False
    assert d["verdict"] == rv.VERDICT_RC2_REVIEW_BLOCKED
    assert "rc2_replay_report_missing" in d["blockers"]


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_complete_and_blocked():
    complete = rv.review_rc2_cross_policy_results(_replay_report())
    blocked = rv.review_rc2_cross_policy_results(None)
    assert rv.validate_rc2_cross_policy_results_review_decision(complete)["valid"] is True
    assert rv.validate_rc2_cross_policy_results_review_decision(blocked)["valid"] is True


def test_validate_rejects_unlocked_gate():
    d = rv.review_rc2_cross_policy_results(_replay_report())
    d["micro_live_gate_locked"] = False
    v = rv.validate_rc2_cross_policy_results_review_decision(d)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_promote_decision():
    d = rv.review_rc2_cross_policy_results(_replay_report())
    d["promotion_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = rv.validate_rc2_cross_policy_results_review_decision(d)
    assert v["valid"] is False
    assert any("promotion_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_marked_approved():
    d = rv.review_rc2_cross_policy_results(_replay_report())
    d["approved_for_execution"] = True
    v = rv.validate_rc2_cross_policy_results_review_decision(d)
    assert v["valid"] is False
    assert any("decision_marked_approved" in e for e in v["errors"])


def test_validate_rejects_missing_structural_blocker():
    d = rv.review_rc2_cross_policy_results(_replay_report())
    d["blockers"] = []
    v = rv.validate_rc2_cross_policy_results_review_decision(d)
    assert v["valid"] is False
    assert any("missing_structural_promotion_blocker" in e for e in v["errors"])


def test_validate_rejects_capability_true():
    d = rv.review_rc2_cross_policy_results(_replay_report())
    d["runs_replay"] = True
    v = rv.validate_rc2_cross_policy_results_review_decision(d)
    assert v["valid"] is False
    assert any("capability_not_false:runs_replay" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = rv.render_rc2_cross_policy_results_review_markdown(
        rv.review_rc2_cross_policy_results(_replay_report())
    )
    assert md.startswith("# Crypto-D1 V2 RC2 Cross-Policy Results Review")
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md and "LOCKED" in md
    assert "Leadership flip confirmed: True" in md
    assert "RP4_breadth_2of3_above_sma200" in md


# --------------------------------------------------------------------------- #
# label / no network or credential imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert rv.get_rc2_cross_policy_results_review_label() == rv.RC2_REVIEW_LABEL
    assert "READ-ONLY" in rv.RC2_REVIEW_LABEL
    assert rv.RC2_REVIEW_MODE == "RESEARCH_ONLY"


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

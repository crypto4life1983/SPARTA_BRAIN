"""Tests for the Crypto-D1 V2 RC3 Findings HUMAN DECISION Contract (READ-ONLY).

Every input consumed here is a FAKE in-memory dict (or one written under tmp_path); no
network, no credentials, no real data, no broker, no exchange, no real order, no replay,
no simulation, no file write, no gate is unlocked. The contract records the human's
thread-closing decision over the RC3 findings, structurally requires fresh evidence
before any reconsideration, never selects a successor, and always keeps
DO_NOT_PROMOTE_RESUME_POLICY_YET."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_replay_runner as rc1rp
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_human_evidence_decision_contract as rc2hd
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_replay_runner as rc2rp
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_results_review_contract as rv186
import sparta_commander.strategy_factory_crypto_d1_rc3_failure_mode_characterization_research_contract as rc3
import sparta_commander.strategy_factory_crypto_d1_rc3_findings_human_decision_contract as hd

_WINDOW_IDS = [
    ("OOS_W1_2020_early_held_out", "held_out_early_history"),
    ("OOS_W2_2021H2_2022H1_straddle", "boundary_straddling_robustness"),
    ("OOS_W3_2022H2_2023H1_straddle", "boundary_straddling_robustness"),
    ("OOS_W4_2024H2_2025H1_straddle", "boundary_straddling_robustness"),
]


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


def _rc1_report():
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


def _policy(pid, *, mean_ret, worst_dd, mean_sharpe):
    window_results = []
    for wid, wtype in _WINDOW_IDS:
        window_results.append(_window(wid, wtype, ret=mean_ret, dd=worst_dd,
                                      sharpe=mean_sharpe, symbols=["BTC", "ETH"]))
    return {
        "policy_id": pid, "description": pid, "reentry_exposure": "FULL",
        "window_results": window_results,
        "aggregate": {
            "windows_evaluated": 4, "mean_total_return": mean_ret,
            "min_total_return": mean_ret, "worst_max_drawdown": worst_dd,
            "mean_sharpe_ratio": mean_sharpe,
        },
    }


def _rc2_report():
    from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import build_paper_prep_config
    rep = rc2rp._base_report(build_paper_prep_config())
    rep.update({
        "verdict": rc2rp.VERDICT_REPLAYS_COMPLETE,
        "blockers": [],
        "selected_variant_id": "V2_trend_plus_cash_regime",
        "policy_parameters_changed": False,
        "policy_results": [
            _policy("RP1_wait_7d_trend_on", mean_ret=0.4089, worst_dd=-0.4141, mean_sharpe=1.43),
            _policy("RP2_wait_14d_trend_on", mean_ret=0.3404, worst_dd=-0.4141, mean_sharpe=1.36),
            _policy("RP3_wait_30d_trend_on", mean_ret=0.3002, worst_dd=-0.4147, mean_sharpe=1.31),
            _policy("RP4_breadth_2of3_above_sma200", mean_ret=0.4206, worst_dd=-0.4141, mean_sharpe=1.43),
            _policy("RP5_half_then_full_on_confirmation", mean_ret=0.4187, worst_dd=-0.4140, mean_sharpe=1.44),
            _policy("RP6_resume_after_volatility_cools", mean_ret=0.2767, worst_dd=-0.4535, mean_sharpe=1.28),
        ],
        "rankings": {
            "best_by_mean_return": "RP4_breadth_2of3_above_sma200",
            "best_by_worst_drawdown": "RP5_half_then_full_on_confirmation",
            "best_by_mean_sharpe": "RP5_half_then_full_on_confirmation",
        },
        "leader_stability": {
            "rc1_leader_policy_id": "RP6_resume_after_volatility_cools",
            "categories_led_by_rc1_leader": [],
            "rc1_leader_leads_all_categories": False,
            "rc1_leader_leads_any_category": False,
        },
        "risk_notes": [], "files_read": [], "files_written": [],
    })
    return rep


def _characterization():
    """A valid Block 188 COMPLETE characterization built from fake evidence."""
    review = rv186.review_rc2_cross_policy_results(_rc2_report())
    review["rc2_replay_report_found"] = True
    hed = rc2hd.record_rc2_cross_policy_human_evidence_decision(review)
    return rc3.characterize_failure_modes(_rc1_report(), _rc2_report(), hed)


# --------------------------------------------------------------------------- #
# the real outcome -> RECORDED, thread closed with lessons, DO NOT PROMOTE
# --------------------------------------------------------------------------- #
def test_records_decision_closes_thread_with_lessons():
    d = hd.record_rc3_findings_human_decision(_characterization())
    assert d["verdict"] == hd.VERDICT_DECISION_RECORDED
    assert d["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert d["approved_for_execution"] is False
    assert d["human_review_required"] is True
    assert d["selected_outcome"] == "CLOSE_RESUME_POLICY_RESEARCH_THREAD_WITH_LESSONS"
    assert d["thread_closed"] is True
    assert list(d["lessons_recorded"]) == list(hd.THREAD_LESSONS)
    assert d["next_required_action"] == "AWAIT_NEW_HUMAN_RESEARCH_DIRECTIVE"
    assert d["blockers"] == []


def test_fresh_evidence_requirement_is_structural():
    d = hd.record_rc3_findings_human_decision(_characterization())
    assert d["fresh_evidence_required_for_reconsideration"] is True
    assert d["reconsideration_requirement"] == (
        "REQUIRE_FRESH_EVIDENCE_VALIDATION_BEFORE_ANY_RECONSIDERATION"
    )
    assert (
        "any_future_reconsideration_requires_genuinely_fresh_evidence_not_rc1_rc2_windows"
        in d["risk_notes"]
    )


def test_decision_acknowledges_all_findings():
    d = hd.record_rc3_findings_human_decision(_characterization())
    notes = d["risk_notes"]
    for fid in rc3.FAILURE_MODE_IDS:
        assert ("acknowledged_supported_failure_mode:" + fid) in notes
    assert (
        "acknowledged_rc1_leader_failed_oos_leadership:RP6_resume_after_volatility_cools"
        in notes
    )
    assert "acknowledged_strongest_oos_evidence:RP4_breadth_2of3_above_sma200" in notes
    assert "acknowledged_strongest_oos_evidence:RP5_half_then_full_on_confirmation" in notes
    assert "strongest_policies_are_evidence_only_not_selected_successors" in notes
    assert d["successors_selected"] is False
    assert set(d["supported_failure_modes"]) == set(rc3.FAILURE_MODE_IDS)


# --------------------------------------------------------------------------- #
# outcome handling
# --------------------------------------------------------------------------- #
def test_each_allowed_outcome_is_accepted():
    for outcome in hd.ALLOWED_OUTCOMES:
        d = hd.record_rc3_findings_human_decision(
            _characterization(), selected_outcome=outcome
        )
        assert d["verdict"] == hd.VERDICT_DECISION_RECORDED
        assert d["selected_outcome"] == outcome


def test_non_close_outcomes_do_not_close_thread():
    d = hd.record_rc3_findings_human_decision(
        _characterization(), selected_outcome=hd.OUTCOME_KEEP_THREAD_OPEN
    )
    assert d["thread_closed"] is False
    assert d["lessons_recorded"] == []
    # fresh evidence is still structurally required either way
    assert d["fresh_evidence_required_for_reconsideration"] is True


def test_invalid_outcome_blocks():
    d = hd.record_rc3_findings_human_decision(
        _characterization(), selected_outcome="PROMOTE_RP5_NOW"
    )
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert any(b.startswith("invalid_selected_outcome:") for b in d["blockers"])
    assert d["selected_outcome"] is None
    assert d["thread_closed"] is False
    assert d["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


# --------------------------------------------------------------------------- #
# invalid / missing upstream input
# --------------------------------------------------------------------------- #
def test_missing_characterization_blocks():
    d = hd.record_rc3_findings_human_decision(None)
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert "rc3_characterization_missing" in d["blockers"]
    assert d["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


def test_blocked_characterization_blocks():
    blocked = rc3.characterize_failure_modes(None, None, None)
    d = hd.record_rc3_findings_human_decision(blocked)
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert "rc3_characterization_not_complete" in d["blockers"]


def test_invalid_characterization_blocks():
    ch = _characterization()
    ch["micro_live_gate_locked"] = False  # breaks Block 188's own validator
    d = hd.record_rc3_findings_human_decision(ch)
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert "rc3_characterization_invalid" in d["blockers"]


def test_overturned_characterization_decision_blocks():
    ch = _characterization()
    ch["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    d = hd.record_rc3_findings_human_decision(ch)
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert "characterization_decision_not_do_not_promote" in d["blockers"]


# --------------------------------------------------------------------------- #
# the decision unlocks nothing
# --------------------------------------------------------------------------- #
def test_decision_unlocks_nothing():
    d = hd.record_rc3_findings_human_decision(_characterization())
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
# disk-backed build
# --------------------------------------------------------------------------- #
def _stage_reports(tmp_path):
    rc1_dir = tmp_path / "reports" / "crypto_d1_rc1_out_of_sample_replay"
    rc1_dir.mkdir(parents=True, exist_ok=True)
    (rc1_dir / "rc1_oos_replay_report.json").write_text(
        json.dumps(_rc1_report()), encoding="utf-8"
    )
    rc2_dir = tmp_path / "reports" / "crypto_d1_rc2_cross_policy_replay"
    rc2_dir.mkdir(parents=True, exist_ok=True)
    (rc2_dir / "rc2_cross_policy_replay_report.json").write_text(
        json.dumps(_rc2_report()), encoding="utf-8"
    )


def test_build_reads_local_reports(tmp_path):
    _stage_reports(tmp_path)
    d = hd.build_rc3_findings_human_decision(repo_root=str(tmp_path))
    assert d["verdict"] == hd.VERDICT_DECISION_RECORDED
    assert d["rc3_characterization_verdict"] == rc3.VERDICT_RC3_COMPLETE
    assert d["thread_closed"] is True


def test_build_handles_missing_local_reports(tmp_path):
    d = hd.build_rc3_findings_human_decision(repo_root=str(tmp_path))
    assert d["verdict"] == hd.VERDICT_DECISION_BLOCKED
    assert d["thread_closed"] is False


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_recorded():
    d = hd.record_rc3_findings_human_decision(_characterization())
    assert hd.validate_rc3_findings_human_decision(d)["valid"] is True


def test_validate_passes_on_blocked():
    d = hd.record_rc3_findings_human_decision(None)
    assert hd.validate_rc3_findings_human_decision(d)["valid"] is True


def test_validate_rejects_unlocked_gate():
    d = hd.record_rc3_findings_human_decision(_characterization())
    d["micro_live_gate_locked"] = False
    v = hd.validate_rc3_findings_human_decision(d)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_promote_decision():
    d = hd.record_rc3_findings_human_decision(_characterization())
    d["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = hd.validate_rc3_findings_human_decision(d)
    assert v["valid"] is False
    assert any("human_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_dropped_fresh_evidence_requirement():
    d = hd.record_rc3_findings_human_decision(_characterization())
    d["fresh_evidence_required_for_reconsideration"] = False
    v = hd.validate_rc3_findings_human_decision(d)
    assert v["valid"] is False
    assert any("fresh_evidence_requirement_dropped" in e for e in v["errors"])


def test_validate_rejects_selected_successor():
    d = hd.record_rc3_findings_human_decision(_characterization())
    d["successors_selected"] = True
    v = hd.validate_rc3_findings_human_decision(d)
    assert v["valid"] is False
    assert any("successor_policy_marked_selected" in e for e in v["errors"])


def test_validate_rejects_closed_thread_without_lessons():
    d = hd.record_rc3_findings_human_decision(_characterization())
    d["lessons_recorded"] = []
    v = hd.validate_rc3_findings_human_decision(d)
    assert v["valid"] is False
    assert any("thread_closed_without_lessons" in e for e in v["errors"])


def test_validate_rejects_capability_true():
    d = hd.record_rc3_findings_human_decision(_characterization())
    d["runs_replay"] = True
    v = hd.validate_rc3_findings_human_decision(d)
    assert v["valid"] is False
    assert any("capability_not_false:runs_replay" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = hd.render_rc3_findings_human_decision_markdown(
        hd.record_rc3_findings_human_decision(_characterization())
    )
    assert md.startswith("# Crypto-D1 V2 RC3 Findings Human Decision")
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md and "LOCKED" in md
    assert "CLOSE_RESUME_POLICY_RESEARCH_THREAD_WITH_LESSONS" in md
    assert "REQUIRE_FRESH_EVIDENCE_VALIDATION_BEFORE_ANY_RECONSIDERATION" in md
    assert "Thread closed: True" in md
    assert "NOT selected successors" in md


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert hd.get_rc3_findings_human_decision_label() == hd.RC3_DECISION_LABEL
    assert "READ-ONLY" in hd.RC3_DECISION_LABEL
    assert hd.RC3_DECISION_MODE == "RESEARCH_ONLY"
    assert hd.allowed_outcomes() == hd.ALLOWED_OUTCOMES
    assert hd.thread_lessons() == hd.THREAD_LESSONS


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in hd.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_or_credential_modules():
    with open(hd.__file__, "r", encoding="utf-8") as fh:
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

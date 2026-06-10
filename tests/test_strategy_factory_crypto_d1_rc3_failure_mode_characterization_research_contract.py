"""Tests for the Crypto-D1 V2 RC3 Failure-Mode Characterization Research Contract
(READ-ONLY).

Every report consumed here is a FAKE in-memory dict (or one written under tmp_path); no
network, no credentials, no real data, no broker, no exchange, no real order, no replay,
no simulation, no file write, no gate is unlocked. The contract is purely descriptive over
already-persisted evidence, recomputes nothing, selects no successor, and always keeps
DO_NOT_PROMOTE_RESUME_POLICY_YET."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_replay_runner as rc1rp
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_human_evidence_decision_contract as hd
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_replay_runner as rc2rp
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_results_review_contract as rv186
import sparta_commander.strategy_factory_crypto_d1_rc3_failure_mode_characterization_research_contract as rc3

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
    """A fake Block 181 report mirroring the committed real RC1 evidence for RP6."""
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
    """A fake Block 185 report mirroring the committed real RC2 evidence."""
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


def _human_decision(**kwargs):
    """A valid Block 187 RECORDED decision (RC3 direction by default)."""
    review = rv186.review_rc2_cross_policy_results(_rc2_report())
    review["rc2_replay_report_found"] = True
    review["rc2_replay_report_path"] = (
        "reports/crypto_d1_rc2_cross_policy_replay/rc2_cross_policy_replay_report.json"
    )
    return hd.record_rc2_cross_policy_human_evidence_decision(review, **kwargs)


def _characterize():
    return rc3.characterize_failure_modes(_rc1_report(), _rc2_report(), _human_decision())


# --------------------------------------------------------------------------- #
# the real outcome -> COMPLETE, all four failure modes supported
# --------------------------------------------------------------------------- #
def test_characterization_complete_keeps_do_not_promote():
    d = _characterize()
    assert d["verdict"] == rc3.VERDICT_RC3_COMPLETE
    assert d["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert d["approved_for_execution"] is False
    assert d["human_review_required"] is True
    assert d["successors_selected"] is False
    assert d["rc1_leader_policy_id"] == "RP6_resume_after_volatility_cools"
    assert d["next_required_action"] == "HUMAN_DECISION_ON_RC3_FINDINGS"
    assert d["blockers"] == []


def test_all_four_failure_modes_supported_on_committed_evidence():
    d = _characterize()
    assert set(d["supported_failure_modes"]) == set(rc3.FAILURE_MODE_IDS)
    by_id = {fm["failure_mode_id"]: fm for fm in d["failure_modes"]}
    assert by_id["FM1_volatility_cooldown_overfit"]["supported"] is True
    assert by_id["FM2_regime_sensitivity"]["supported"] is True
    assert by_id["FM3_delayed_or_over_filtered_reentry"]["supported"] is True
    assert by_id["FM4_ranking_instability"]["supported"] is True
    # evidence cites concrete numbers from the persisted reports
    fm1_ev = " ".join(by_id["FM1_volatility_cooldown_overfit"]["evidence"])
    assert "155.38%" in fm1_ev and "27.67%" in fm1_ev
    fm2_ev = " ".join(by_id["FM2_regime_sensitivity"]["evidence"])
    assert "OOS_W4_2024H2_2025H1_straddle" in fm2_ev


def test_strength_analysis_is_evidence_only():
    d = _characterize()
    sa = d["strength_analysis"]
    assert sa["evidence_only_not_selected_successors"] is True
    assert sorted(sa["strongest_evidence_policies"]) == [
        "RP4_breadth_2of3_above_sma200", "RP5_half_then_full_on_confirmation",
    ]
    assert any("fresh evidence" in o for o in sa["observations"])
    assert "strongest_policies_are_evidence_only_not_selected_successors" in d["risk_notes"]
    assert "characterization_is_descriptive_only_no_recompute" in d["risk_notes"]


def test_stable_leader_marks_fm1_and_fm4_unsupported():
    rc2 = _rc2_report()
    rc2["rankings"] = {k: "RP6_resume_after_volatility_cools" for k in rc2["rankings"]}
    rc2["leader_stability"].update({
        "categories_led_by_rc1_leader": [
            "mean_total_return", "worst_max_drawdown", "mean_sharpe_ratio"
        ],
        "rc1_leader_leads_all_categories": True,
        "rc1_leader_leads_any_category": True,
    })
    review = rv186.review_rc2_cross_policy_results(rc2)
    review["rc2_replay_report_found"] = True
    hed = hd.record_rc2_cross_policy_human_evidence_decision(review)
    d = rc3.characterize_failure_modes(_rc1_report(), rc2, hed)
    by_id = {fm["failure_mode_id"]: fm for fm in d["failure_modes"]}
    assert by_id["FM1_volatility_cooldown_overfit"]["supported"] is False
    assert by_id["FM4_ranking_instability"]["supported"] is False


# --------------------------------------------------------------------------- #
# gating / missing inputs
# --------------------------------------------------------------------------- #
def test_missing_human_decision_blocks():
    d = rc3.characterize_failure_modes(_rc1_report(), _rc2_report(), None)
    assert d["verdict"] == rc3.VERDICT_RC3_BLOCKED
    assert "rc2_human_evidence_decision_missing" in d["blockers"]
    assert d["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


def test_wrong_direction_blocks():
    hed = _human_decision(selected_direction=hd.DIRECTION_FURTHER_VALIDATION)
    d = rc3.characterize_failure_modes(_rc1_report(), _rc2_report(), hed)
    assert d["verdict"] == rc3.VERDICT_RC3_BLOCKED
    assert "rc3_direction_not_selected_by_human" in d["blockers"]


def test_missing_rc1_report_blocks():
    d = rc3.characterize_failure_modes(None, _rc2_report(), _human_decision())
    assert d["verdict"] == rc3.VERDICT_RC3_BLOCKED
    assert "rc1_oos_replay_report_missing" in d["blockers"]


def test_missing_rc2_report_blocks():
    d = rc3.characterize_failure_modes(_rc1_report(), None, _human_decision())
    assert d["verdict"] == rc3.VERDICT_RC3_BLOCKED
    assert "rc2_cross_policy_replay_report_missing" in d["blockers"]


def test_invalid_rc2_report_blocks():
    rc2 = _rc2_report()
    rc2["micro_live_gate_locked"] = False  # breaks Block 185's own validator
    d = rc3.characterize_failure_modes(_rc1_report(), rc2, _human_decision())
    assert d["verdict"] == rc3.VERDICT_RC3_BLOCKED
    assert "rc2_cross_policy_replay_report_invalid" in d["blockers"]


# --------------------------------------------------------------------------- #
# the characterization unlocks nothing
# --------------------------------------------------------------------------- #
def test_characterization_unlocks_nothing():
    d = _characterize()
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
    d = rc3.build_rc3_failure_mode_characterization(repo_root=str(tmp_path))
    assert d["verdict"] == rc3.VERDICT_RC3_COMPLETE
    assert d["rc1_oos_replay_report_found"] is True
    assert d["rc2_replay_report_found"] is True
    assert d["human_evidence_decision_verdict"] == hd.VERDICT_DECISION_RECORDED
    assert set(d["supported_failure_modes"]) == set(rc3.FAILURE_MODE_IDS)


def test_build_handles_missing_local_reports(tmp_path):
    d = rc3.build_rc3_failure_mode_characterization(repo_root=str(tmp_path))
    assert d["verdict"] == rc3.VERDICT_RC3_BLOCKED
    assert d["rc1_oos_replay_report_found"] is False
    assert d["rc2_replay_report_found"] is False


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_complete_and_blocked():
    complete = _characterize()
    blocked = rc3.characterize_failure_modes(None, None, None)
    assert rc3.validate_rc3_failure_mode_characterization(complete)["valid"] is True
    assert rc3.validate_rc3_failure_mode_characterization(blocked)["valid"] is True


def test_validate_rejects_unlocked_gate():
    d = _characterize()
    d["micro_live_gate_locked"] = False
    v = rc3.validate_rc3_failure_mode_characterization(d)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_promote_decision():
    d = _characterize()
    d["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = rc3.validate_rc3_failure_mode_characterization(d)
    assert v["valid"] is False
    assert any("human_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_selected_successor():
    d = _characterize()
    d["successors_selected"] = True
    v = rc3.validate_rc3_failure_mode_characterization(d)
    assert v["valid"] is False
    assert any("successor_policy_marked_selected" in e for e in v["errors"])


def test_validate_rejects_catalog_mismatch():
    d = _characterize()
    d["failure_modes"] = d["failure_modes"][:2]
    v = rc3.validate_rc3_failure_mode_characterization(d)
    assert v["valid"] is False
    assert "failure_mode_catalog_mismatch" in v["errors"]


def test_validate_rejects_strength_not_evidence_only():
    d = _characterize()
    d["strength_analysis"]["evidence_only_not_selected_successors"] = False
    v = rc3.validate_rc3_failure_mode_characterization(d)
    assert v["valid"] is False
    assert any("strength_analysis_not_marked_evidence_only" in e for e in v["errors"])


def test_validate_rejects_capability_true():
    d = _characterize()
    d["runs_replay"] = True
    v = rc3.validate_rc3_failure_mode_characterization(d)
    assert v["valid"] is False
    assert any("capability_not_false:runs_replay" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = rc3.render_rc3_failure_mode_characterization_markdown(_characterize())
    assert md.startswith("# Crypto-D1 V2 RC3 Failure-Mode Characterization")
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md and "LOCKED" in md
    assert "FM1_volatility_cooldown_overfit" in md
    assert "NOT successors" in md


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert rc3.get_rc3_failure_mode_characterization_label() == rc3.RC3_LABEL
    assert "READ-ONLY" in rc3.RC3_LABEL
    assert rc3.RC3_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rc3.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_or_credential_modules():
    with open(rc3.__file__, "r", encoding="utf-8") as fh:
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

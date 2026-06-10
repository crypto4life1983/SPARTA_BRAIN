"""Tests for the Crypto-D1 V2 RC2 Cross-Policy Stability Research Contract (READ-ONLY).

Every decision consumed here is a FAKE in-memory dict (or one derived under tmp_path); no
network, no credentials, no real data, no broker, no exchange, no real order, no replay,
no simulation, no file write, no gate is unlocked. The contract is a spec only: a fixed,
pre-registered cross-policy comparison plan that preserves DO_NOT_PROMOTE_RESUME_POLICY_YET
and runs nothing."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_rc1_oos_human_evidence_decision_contract as hd
import sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_replay_runner as rp
import sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_results_review_contract as rv
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_stability_research_contract as rc2


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


def _replay_report():
    from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import build_paper_prep_config
    rep = rp._base_report(build_paper_prep_config())
    rep.update({
        "verdict": rp.VERDICT_REPLAYS_COMPLETE,
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


def _review_decision():
    d = rv.review_rc1_oos_results(_replay_report())
    d["rc1_oos_replay_report_found"] = True
    d["rc1_oos_replay_report_path"] = (
        "reports/crypto_d1_rc1_out_of_sample_replay/rc1_oos_replay_report.json"
    )
    return d


def _human_decision(**kwargs):
    """A valid Block 183 RECORDED human evidence decision."""
    return hd.record_rc1_oos_human_evidence_decision(_review_decision(), **kwargs)


# --------------------------------------------------------------------------- #
# recorded RC2 selection -> READY spec, DO_NOT_PROMOTE preserved
# --------------------------------------------------------------------------- #
def test_record_ready_spec_preserves_do_not_promote():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    assert s["verdict"] == rc2.VERDICT_RC2_SPEC_READY
    assert s["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert s["approved_for_execution"] is False
    assert s["human_review_required"] is True
    assert s["selected_direction_id"] == "CONTINUE_RESEARCH_VIA_RC2_CROSS_POLICY_STABILITY"
    assert s["next_required_action"] == "HUMAN_APPROVED_RC2_CROSS_POLICY_REPLAY"
    assert s["blockers"] == []


def test_spec_frames_leader_status_as_the_question():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    assert s["rc1_leader_policy_id"] == "RP6_resume_after_volatility_cools"
    assert "rc1_evidence_leader_to_test:RP6_resume_after_volatility_cools" in s["risk_notes"]
    assert "leader_status_is_the_question_not_the_assumption" in s["risk_notes"]
    assert "RP1..RP5" in s["rc2_stability_question"]
    assert "candidate_parameters_verbatim_from_block_175_no_fitting" in s["risk_notes"]
    assert "windows_verbatim_from_block_180_same_as_rc1" in s["risk_notes"]
    assert "ranking_categories_fixed_before_any_run" in s["risk_notes"]


def test_candidates_are_the_six_fixed_policies_unchanged():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    assert s["candidate_policy_ids"] == [
        "RP1_wait_7d_trend_on", "RP2_wait_14d_trend_on", "RP3_wait_30d_trend_on",
        "RP4_breadth_2of3_above_sma200", "RP5_half_then_full_on_confirmation",
        "RP6_resume_after_volatility_cools",
    ]
    assert s["candidate_parameters_changed"] is False
    # candidate parameters are verbatim deep copies of the Block 175 plan
    from sparta_commander.strategy_factory_crypto_d1_resume_policy_research_plan import (
        RESUME_POLICY_CANDIDATES,
    )
    assert s["candidate_policies"] == RESUME_POLICY_CANDIDATES


def test_windows_are_the_same_four_rc1_windows():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    ids = [w["window_id"] for w in s["evaluation_windows"]]
    assert ids == [
        "OOS_W1_2020_early_held_out", "OOS_W2_2021H2_2022H1_straddle",
        "OOS_W3_2022H2_2023H1_straddle", "OOS_W4_2024H2_2025H1_straddle",
    ]
    from sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_robustness_research_contract import (
        OUT_OF_SAMPLE_WINDOWS,
    )
    assert s["evaluation_windows"] == OUT_OF_SAMPLE_WINDOWS


def test_planned_replays_cover_every_policy_and_run_nothing():
    replays = rc2.planned_cross_policy_replays()
    assert len(replays) == 6
    pids = {r["policy_id"] for r in replays}
    assert pids == set(p["policy_id"] for p in rc2.candidate_policies())
    for r in replays:
        assert r["is_run"] is False
        assert r["requires_human_command"] is True
        assert r["policy_parameters_changed"] is False
        assert r["data_scope"] == "QA_PASSED_LOCAL_CSV_ONLY"
        assert r["authorization_required"] == rc2.NEXT_REQUIRED_ACTION
        assert len(r["windows_to_cover"]) == 4


def test_accessors_return_copies():
    a = rc2.candidate_policies()
    a[0]["policy_id"] = "tampered"
    assert rc2.candidate_policies()[0]["policy_id"] != "tampered"
    w = rc2.evaluation_windows()
    w[0]["window_id"] = "tampered"
    assert rc2.evaluation_windows()[0]["window_id"] != "tampered"


# --------------------------------------------------------------------------- #
# invalid / missing upstream input
# --------------------------------------------------------------------------- #
def test_missing_decision_blocks():
    s = rc2.record_rc2_cross_policy_stability_spec(None)
    assert s["verdict"] == rc2.VERDICT_RC2_SPEC_BLOCKED
    assert "human_evidence_decision_missing" in s["blockers"]
    assert s["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


def test_blocked_decision_blocks():
    blocked = hd.record_rc1_oos_human_evidence_decision(None)
    s = rc2.record_rc2_cross_policy_stability_spec(blocked)
    assert s["verdict"] == rc2.VERDICT_RC2_SPEC_BLOCKED
    assert "human_evidence_decision_not_recorded" in s["blockers"]


def test_different_direction_blocks():
    other = _human_decision(selected_direction=hd.DIRECTION_FURTHER_VALIDATION)
    s = rc2.record_rc2_cross_policy_stability_spec(other)
    assert s["verdict"] == rc2.VERDICT_RC2_SPEC_BLOCKED
    assert "rc2_direction_not_selected_by_human" in s["blockers"]


def test_overturned_decision_blocks():
    hed = _human_decision()
    hed["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    s = rc2.record_rc2_cross_policy_stability_spec(hed)
    assert s["verdict"] == rc2.VERDICT_RC2_SPEC_BLOCKED
    assert "human_decision_not_do_not_promote" in s["blockers"]
    # the spec's own carried decision stays DO_NOT_PROMOTE regardless
    assert s["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


def test_invalid_decision_blocks():
    hed = _human_decision()
    hed["micro_live_gate_locked"] = False  # breaks Block 183's own validator
    s = rc2.record_rc2_cross_policy_stability_spec(hed)
    assert s["verdict"] == rc2.VERDICT_RC2_SPEC_BLOCKED
    assert "human_evidence_decision_invalid" in s["blockers"]


# --------------------------------------------------------------------------- #
# the spec unlocks nothing and runs nothing
# --------------------------------------------------------------------------- #
def test_spec_unlocks_nothing():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    assert s["paper_trading_gate_locked"] is True
    assert s["micro_live_gate_locked"] is True
    assert s["live_gate_locked"] is True
    for key in (
        "executes", "writes_files", "runs_replay", "runs_simulation", "runs_backtest",
        "runs_optimization", "ran_parameter_search", "parameters_changed_based_on_results",
        "fetches_data", "connects_broker", "connects_exchange", "uses_real_money",
        "uses_network", "uses_credentials", "authorizes_paper_execution",
        "authorizes_micro_live", "authorizes_live_trading", "promotes_gate",
        "promotes_resume_policy", "unlocks_downstream_gate",
    ):
        assert s[key] is False, key


# --------------------------------------------------------------------------- #
# disk-backed build
# --------------------------------------------------------------------------- #
def test_build_reads_local_report(tmp_path):
    out = tmp_path / "reports" / "crypto_d1_rc1_out_of_sample_replay"
    out.mkdir(parents=True, exist_ok=True)
    (out / "rc1_oos_replay_report.json").write_text(
        json.dumps(_replay_report()), encoding="utf-8"
    )
    s = rc2.build_rc2_cross_policy_stability_spec(repo_root=str(tmp_path))
    assert s["verdict"] == rc2.VERDICT_RC2_SPEC_READY
    assert s["human_evidence_decision_verdict"] == hd.VERDICT_DECISION_RECORDED
    assert s["rc1_oos_replay_report_found"] is True


def test_build_blocks_when_no_local_report(tmp_path):
    s = rc2.build_rc2_cross_policy_stability_spec(repo_root=str(tmp_path))
    assert s["verdict"] == rc2.VERDICT_RC2_SPEC_BLOCKED
    assert "human_evidence_decision_not_recorded" in s["blockers"]
    assert s["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_blocked():
    ready = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    blocked = rc2.record_rc2_cross_policy_stability_spec(None)
    assert rc2.validate_rc2_cross_policy_stability_spec(ready)["valid"] is True
    assert rc2.validate_rc2_cross_policy_stability_spec(blocked)["valid"] is True


def test_validate_rejects_unlocked_gate():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    s["micro_live_gate_locked"] = False
    v = rc2.validate_rc2_cross_policy_stability_spec(s)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_promote_decision():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    s["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = rc2.validate_rc2_cross_policy_stability_spec(s)
    assert v["valid"] is False
    assert any("human_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_replay_marked_run():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    s["planned_replays"][0]["is_run"] = True
    v = rc2.validate_rc2_cross_policy_stability_spec(s)
    assert v["valid"] is False
    assert any(e.startswith("replay_marked_run:") for e in v["errors"])


def test_validate_rejects_changed_parameters():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    s["planned_replays"][0]["policy_parameters_changed"] = True
    v = rc2.validate_rc2_cross_policy_stability_spec(s)
    assert v["valid"] is False
    assert any(e.startswith("replay_changes_parameters:") for e in v["errors"])


def test_validate_rejects_single_candidate():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    only = s["candidate_policies"][:1]
    s["candidate_policies"] = only
    s["planned_replays"] = [r for r in s["planned_replays"]
                            if r["policy_id"] == only[0]["policy_id"]]
    v = rc2.validate_rc2_cross_policy_stability_spec(s)
    assert v["valid"] is False
    assert "fewer_than_two_candidates" in v["errors"]


def test_validate_rejects_missing_held_out_window():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    for w in s["evaluation_windows"]:
        w["window_type"] = "boundary_straddling_robustness"
    v = rc2.validate_rc2_cross_policy_stability_spec(s)
    assert v["valid"] is False
    assert "no_truly_held_out_window" in v["errors"]


def test_validate_rejects_capability_true():
    s = rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    s["runs_replay"] = True
    v = rc2.validate_rc2_cross_policy_stability_spec(s)
    assert v["valid"] is False
    assert any("capability_not_false:runs_replay" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = rc2.render_rc2_cross_policy_stability_spec_markdown(
        rc2.record_rc2_cross_policy_stability_spec(_human_decision())
    )
    assert md.startswith("# Crypto-D1 V2 RC2 Cross-Policy Stability Research Spec")
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md and "LOCKED" in md
    assert "RP6_resume_after_volatility_cools" in md
    assert "RC2_REPLAY_RP1_wait_7d_trend_on" in md


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert rc2.get_rc2_cross_policy_stability_contract_label() == rc2.RC2_LABEL
    assert "READ-ONLY" in rc2.RC2_LABEL
    assert rc2.RC2_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rc2.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_or_credential_modules():
    with open(rc2.__file__, "r", encoding="utf-8") as fh:
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

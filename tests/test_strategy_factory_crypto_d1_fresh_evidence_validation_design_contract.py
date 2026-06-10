"""Tests for the Crypto-D1 V2 Fresh-Evidence Validation Design Contract (READ-ONLY).

Every input consumed here is a FAKE in-memory dict (or one written under tmp_path); no
network, no credentials, no real data, no broker, no exchange, no real order, no replay,
no simulation, no file write, no gate is unlocked. The contract pre-registers frozen
evidence criteria before any qualifying data exists, never evaluates, never promotes,
and always keeps DO_NOT_PROMOTE_RESUME_POLICY_YET."""

from __future__ import annotations

import ast
import json

import sparta_commander.strategy_factory_crypto_d1_fresh_evidence_validation_design_contract as fd
import sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_replay_runner as rc1rp
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_human_evidence_decision_contract as rc2hd
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_replay_runner as rc2rp
import sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_results_review_contract as rv186
import sparta_commander.strategy_factory_crypto_d1_rc3_failure_mode_characterization_research_contract as rc3
import sparta_commander.strategy_factory_crypto_d1_rc3_findings_human_decision_contract as hd189

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


def _findings_decision(**kwargs):
    """A valid Block 189 RECORDED, thread-closed findings decision."""
    review = rv186.review_rc2_cross_policy_results(_rc2_report())
    review["rc2_replay_report_found"] = True
    hed = rc2hd.record_rc2_cross_policy_human_evidence_decision(review)
    ch = rc3.characterize_failure_modes(_rc1_report(), _rc2_report(), hed)
    return hd189.record_rc3_findings_human_decision(ch, **kwargs)


# --------------------------------------------------------------------------- #
# closed thread -> READY design with frozen criteria
# --------------------------------------------------------------------------- #
def test_record_ready_design_preserves_do_not_promote():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    assert d["verdict"] == fd.VERDICT_DESIGN_READY
    assert d["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"
    assert d["approved_for_execution"] is False
    assert d["human_review_required"] is True
    assert d["successors_selected"] is False
    assert d["next_required_action"] == "AWAIT_FRESH_EVIDENCE_ACCRUAL"
    assert d["blockers"] == []


def test_criteria_are_frozen_and_pass_promotes_nothing():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    assert d["criteria_frozen"] is True
    assert d["passing_promotes_nothing"] is True
    assert "criteria_frozen_before_any_qualifying_candle_exists" in d["risk_notes"]
    assert "passing_qualifies_for_reconsideration_only_never_promotes" in d["risk_notes"]
    assert "manual_csv_staging_only_no_fetch_ever" in d["risk_notes"]


def test_evidence_source_rules_are_fixed():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    src = d["evidence_source_rules"]
    assert d["fresh_evidence_cutoff_date"] == "2026-06-08"
    assert src["window_must_start_after"] == "2026-06-08"
    assert src["source"] == "MANUALLY_STAGED_DAILY_CSV_ONLY"
    assert src["fetch_allowed"] is False
    assert src["overlap_with_rc1_rc2_windows_allowed"] is False
    assert src["evaluation_runs_once_per_window"] is True
    assert src["bars_frozen_by_this_design"] is True
    assert d["min_fresh_window_days"] == 180
    assert d["preferred_fresh_window_days"] == 365


def test_pass_fail_bars_are_complete_and_strict():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    bars = d["pass_fail_bars"]
    assert bars["min_total_return"] == 0.0
    assert bars["max_acceptable_drawdown"] == -0.35
    assert bars["min_sharpe_ratio"] == 0.8
    assert bars["stability_min_rank_top_half_all_categories"] is True
    assert bars["all_bars_must_pass"] is True


def test_candidate_eligibility_covers_the_fixed_six_only():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    elig = d["candidate_eligibility"]
    assert set(elig["eligible_candidate_ids"]) == {
        "RP1_wait_7d_trend_on", "RP2_wait_14d_trend_on", "RP3_wait_30d_trend_on",
        "RP4_breadth_2of3_above_sma200", "RP5_half_then_full_on_confirmation",
        "RP6_resume_after_volatility_cools",
    }
    assert elig["parameters_must_be_verbatim_block_175"] is True
    assert elig["parameter_change_disqualifies"] is True
    assert elig["new_candidates_require_their_own_preregistered_design"] is True
    # RP4/RP5 enter on the same bars as everyone else
    assert "no head start" in elig["rp4_rp5_have_no_special_status"] or (
        "not a head start" in elig["rp4_rp5_have_no_special_status"]
    )


def test_rejection_rules_are_explicit():
    rules = fd.rejection_rules()
    assert len(rules) >= 5
    joined = " ".join(rules)
    assert "no_partial_credit" in joined
    assert "wait_do_not_peek" in joined
    assert "tainted" in joined
    assert "parameter_change" in joined
    assert "different_bars_is_forbidden" in joined
    assert "promotes_nothing" in joined


def test_lessons_are_carried_from_block_189():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    assert list(d["lessons_carried"]) == list(hd189.THREAD_LESSONS)


# --------------------------------------------------------------------------- #
# gating / missing inputs
# --------------------------------------------------------------------------- #
def test_missing_decision_blocks():
    d = fd.record_fresh_evidence_validation_design(None)
    assert d["verdict"] == fd.VERDICT_DESIGN_BLOCKED
    assert "rc3_findings_decision_missing" in d["blockers"]
    assert d["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


def test_blocked_decision_blocks():
    blocked = hd189.record_rc3_findings_human_decision(None)
    d = fd.record_fresh_evidence_validation_design(blocked)
    assert d["verdict"] == fd.VERDICT_DESIGN_BLOCKED
    assert "rc3_findings_decision_not_recorded" in d["blockers"]


def test_open_thread_blocks():
    open_thread = _findings_decision(
        selected_outcome=hd189.OUTCOME_KEEP_THREAD_OPEN
    )
    d = fd.record_fresh_evidence_validation_design(open_thread)
    assert d["verdict"] == fd.VERDICT_DESIGN_BLOCKED
    assert "resume_policy_thread_not_closed" in d["blockers"]


def test_invalid_decision_blocks():
    bad = _findings_decision()
    bad["micro_live_gate_locked"] = False  # breaks Block 189's own validator
    d = fd.record_fresh_evidence_validation_design(bad)
    assert d["verdict"] == fd.VERDICT_DESIGN_BLOCKED
    assert "rc3_findings_decision_invalid" in d["blockers"]


# --------------------------------------------------------------------------- #
# the design unlocks nothing
# --------------------------------------------------------------------------- #
def test_design_unlocks_nothing():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    assert d["paper_trading_gate_locked"] is True
    assert d["micro_live_gate_locked"] is True
    assert d["live_gate_locked"] is True
    for key in (
        "executes", "writes_files", "runs_evaluation", "runs_replay", "runs_simulation",
        "runs_backtest", "runs_optimization", "ran_parameter_search",
        "parameters_changed_based_on_results", "fetches_data", "connects_broker",
        "connects_exchange", "uses_real_money", "uses_network", "uses_credentials",
        "authorizes_real_data_qa", "authorizes_baseline_backtest",
        "authorizes_paper_execution", "authorizes_micro_live",
        "authorizes_live_trading", "promotes_gate", "promotes_resume_policy",
        "unlocks_downstream_gate",
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
    d = fd.build_fresh_evidence_validation_design(repo_root=str(tmp_path))
    assert d["verdict"] == fd.VERDICT_DESIGN_READY
    assert d["rc3_findings_decision_verdict"] == hd189.VERDICT_DECISION_RECORDED
    assert d["criteria_frozen"] is True


def test_build_handles_missing_local_reports(tmp_path):
    d = fd.build_fresh_evidence_validation_design(repo_root=str(tmp_path))
    assert d["verdict"] == fd.VERDICT_DESIGN_BLOCKED
    assert d["human_decision"] == "DO_NOT_PROMOTE_RESUME_POLICY_YET"


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_passes_on_ready_and_blocked():
    ready = fd.record_fresh_evidence_validation_design(_findings_decision())
    blocked = fd.record_fresh_evidence_validation_design(None)
    assert fd.validate_fresh_evidence_validation_design(ready)["valid"] is True
    assert fd.validate_fresh_evidence_validation_design(blocked)["valid"] is True


def test_validate_rejects_unfrozen_criteria():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    d["criteria_frozen"] = False
    v = fd.validate_fresh_evidence_validation_design(d)
    assert v["valid"] is False
    assert any("criteria_not_frozen" in e for e in v["errors"])


def test_validate_rejects_pass_as_promotion():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    d["passing_promotes_nothing"] = False
    v = fd.validate_fresh_evidence_validation_design(d)
    assert v["valid"] is False
    assert any("pass_treated_as_promotion" in e for e in v["errors"])


def test_validate_rejects_fetch_allowed():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    d["evidence_source_rules"]["fetch_allowed"] = True
    v = fd.validate_fresh_evidence_validation_design(d)
    assert v["valid"] is False
    assert any("source_rules_allow_fetch" in e for e in v["errors"])


def test_validate_rejects_tainted_overlap():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    d["evidence_source_rules"]["overlap_with_rc1_rc2_windows_allowed"] = True
    v = fd.validate_fresh_evidence_validation_design(d)
    assert v["valid"] is False
    assert any("source_rules_allow_tainted_overlap" in e for e in v["errors"])


def test_validate_rejects_short_min_window():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    d["min_fresh_window_days"] = 30
    v = fd.validate_fresh_evidence_validation_design(d)
    assert v["valid"] is False
    assert any("min_window_below_floor" in e for e in v["errors"])


def test_validate_rejects_partial_credit():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    d["pass_fail_bars"]["all_bars_must_pass"] = False
    v = fd.validate_fresh_evidence_validation_design(d)
    assert v["valid"] is False
    assert any("partial_credit_allowed" in e for e in v["errors"])


def test_validate_rejects_modified_candidate_set():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    d["candidate_eligibility"]["eligible_candidate_ids"].append("RP7_new_idea")
    v = fd.validate_fresh_evidence_validation_design(d)
    assert v["valid"] is False
    assert any("eligible_candidates_not_the_fixed_six" in e for e in v["errors"])


def test_validate_rejects_promote_decision():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    d["human_decision"] = "PROMOTE_RESUME_POLICY_FOR_EXECUTION"
    v = fd.validate_fresh_evidence_validation_design(d)
    assert v["valid"] is False
    assert any("human_decision_not_do_not_promote" in e for e in v["errors"])


def test_validate_rejects_unlocked_gate():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    d["micro_live_gate_locked"] = False
    v = fd.validate_fresh_evidence_validation_design(d)
    assert v["valid"] is False
    assert any("gate_not_locked:micro_live_gate_locked" in e for e in v["errors"])


def test_validate_rejects_capability_true():
    d = fd.record_fresh_evidence_validation_design(_findings_decision())
    d["runs_evaluation"] = True
    v = fd.validate_fresh_evidence_validation_design(d)
    assert v["valid"] is False
    assert any("capability_not_false:runs_evaluation" in e for e in v["errors"])


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_markdown_is_string():
    md = fd.render_fresh_evidence_validation_design_markdown(
        fd.record_fresh_evidence_validation_design(_findings_decision())
    )
    assert md.startswith("# Crypto-D1 V2 Fresh-Evidence Validation Design")
    assert "DO_NOT_PROMOTE_RESUME_POLICY_YET" in md and "LOCKED" in md
    assert "2026-06-08" in md
    assert "frozen NOW, before the data exists" in md
    assert "RP4_breadth_2of3_above_sma200" in md


# --------------------------------------------------------------------------- #
# label / posture / no banned imports
# --------------------------------------------------------------------------- #
def test_label_is_read_only_research_label():
    assert fd.get_fresh_evidence_validation_design_label() == fd.DESIGN_LABEL
    assert "READ-ONLY" in fd.DESIGN_LABEL
    assert fd.DESIGN_MODE == "RESEARCH_ONLY"


def test_action_carries_no_execution_or_promotion_verbs():
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE", "EXECUTION",
                   "BACKTEST", "BASELINE", "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in fd.NEXT_REQUIRED_ACTION.upper(), banned


def test_module_imports_no_network_or_credential_modules():
    with open(fd.__file__, "r", encoding="utf-8") as fh:
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

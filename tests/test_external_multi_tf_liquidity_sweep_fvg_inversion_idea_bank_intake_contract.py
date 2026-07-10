"""Minimal integrity test for the multi-TF liquidity-sweep + FVG-inversion IDEA-BANK record.

Covers only the integrity of the record: it validates, states the required conclusions,
cites the real overlapping rejected families, keeps options out of scope, does not mark the
realistic prior as proven, is not a candidate/proposal, and pins every capability flag False.
"""
import sparta_commander.external_multi_tf_liquidity_sweep_fvg_inversion_idea_bank_intake_contract as ib


def test_record_builds_and_validates():
    r = ib.build_idea_bank_record()
    assert r["verdict"] == ib.VERDICT_IDEA_BANK_DIAGNOSTIC_ONLY
    assert not r["blockers"]
    assert ib.validate_idea_bank_record(r)["valid"] is True


def test_states_required_conclusions():
    r = ib.build_idea_bank_record()
    fams = {x["family"] for x in r["overlapping_rejected_families"]}
    assert {"liquidity_sweep_mean_reversion", "failed_breakdown_reclaim_reversal",
            "h4_trend_following_market_structure", "ny_session_fvg_choch"} <= fams
    assert r["claims_payouts_winrates_trader_results_are_non_evidence"] is True
    assert r["mechanically_testable_as_presented"] is False
    assert r["new_return_engine_axis_demonstrated"] is False
    assert r["options_zero_dte_out_of_scope"] is True
    assert r["realistic_prior_is_proven_for_es_nq"] is False
    assert tuple(r["retained_hypothesis_diagnostic_ablation"]) == (
        "fixed_higher_timeframe_sweep", "fixed_rapid_imbalance_failure",
        "optional_fixed_retracement")
    for pre in ("mechanically_frozen_definitions", "provenance_sealed_es_nq_one_minute_data",
                "strict_no_lookahead_handling", "next_bar_conservative_execution",
                "commissions_and_slippage", "minimum_sample_gate",
                "random_entry_and_appropriate_benchmark_comparisons",
                "explicit_new_human_approval"):
        assert pre in r["future_study_blocked_until"]


def test_record_only_no_candidate_no_state_change():
    r = ib.build_idea_bank_record()
    assert r["is_idea_bank_record_only"] is True
    assert r["is_candidate"] is False and r["is_proposal"] is False
    for flag in ib._CAPABILITY_FLAGS_FALSE:
        assert r[flag] is False, flag
    for k in ("creates_candidate", "modifies_c12", "modifies_c18", "modifies_c22",
              "opens_options_lane", "changes_research_standards", "runs_backtest",
              "fetches_data", "touches_nq_mnq_opening_range_lab", "auto_commits", "auto_pushes"):
        assert r[k] is False


def test_validator_rejects_tamper_to_candidate():
    r = ib.build_idea_bank_record()
    r["is_proposal"] = True
    assert ib.validate_idea_bank_record(r)["valid"] is False


def test_validator_rejects_claims_as_evidence_or_proven_prior():
    r = ib.build_idea_bank_record()
    r["claims_payouts_winrates_trader_results_are_non_evidence"] = False
    assert ib.validate_idea_bank_record(r)["valid"] is False
    r2 = ib.build_idea_bank_record()
    r2["realistic_prior_is_proven_for_es_nq"] = True
    assert ib.validate_idea_bank_record(r2)["valid"] is False

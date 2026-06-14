"""Tests for the Strategy Factory Rejected Family Blacklist V5
contract (extends V4 with the C9 family rejection).

Verifies: chain-gate on the nine-record ledger + C9 rejection record
+ V4 + V3 + V2 + Recommendation V1 + Autopilot V1; nine-family
blacklist; V4 is a strict subset of V5 with exactly +1 entry; new
entry = low_volume_downside_capitulation_mean_reversion; C10
proposal requirements include the new C9 lesson (joint/intersection-
trigger sample-size pre-justification); inherited lessons C1-C9;
downstream execution surface remains locked; AST/purity green."""

from __future__ import annotations

import ast
import copy

import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_rejection_record as rj9
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3
import sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract as bl4
import sparta_commander.strategy_factory_rejected_family_blacklist_v5_contract as bl5


_R = bl5.build_rejected_family_blacklist_v5()


# ---- chain gate + ready verdict -------------------------------------------

def test_blacklist_v5_ready_and_chain_gates_all_certify():
    assert rj9.build_c9_rejection_record()["verdict"] == (
        rj9.VERDICT_RJ9_RECORDED)
    assert bl4.build_rejected_family_blacklist_v4()["verdict"] == (
        bl4.VERDICT_BL4_READY)
    assert bl3.build_rejected_family_blacklist_v3()["verdict"] == (
        bl3.VERDICT_BL3_READY)
    assert oap2.build_overnight_research_autopilot_v2_contract()[
        "verdict"] == oap2.VERDICT_OAP2_READY
    assert rec.build_candidate_recommendation()["verdict"] == (
        rec.VERDICT_CR_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    assert _R["verdict"] == bl5.VERDICT_BL5_READY
    assert _R["blockers"] == []
    assert bl5.validate_rejected_family_blacklist_v5(
        _R)["valid"] is True


def test_nine_record_ledger_intact():
    assert _R["ledger_status_nine_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 9
    assert _R["ledger_all_rejected_kept_on_record"] is True


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.strategy_factory_rejected_family_blacklist_v5_contract as mod
    originals = {k: getattr(mod, k) for k in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS",
                  "C4_STATUS", "C5_STATUS", "C6_STATUS",
                  "C7_STATUS", "C8_STATUS", "C9_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_rejected_family_blacklist_v5()
            assert record["verdict"] == bl5.VERDICT_BL5_BLOCKED, key
            assert "nine_record_ledger_broken" in record[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for k, v in originals.items():
            setattr(mod, k, v)
    assert mod.build_rejected_family_blacklist_v5()["verdict"] == (
        bl5.VERDICT_BL5_READY)


# ---- nine-family blacklist + V4 strict-subset ----------------------------

def test_blacklist_has_nine_families_and_includes_c9():
    blacklist = tuple(_R["rejected_family_logic_blacklist_v5"])
    assert len(blacklist) == 9
    assert _R["blacklist_length"] == 9
    assert "low_volume_downside_capitulation_mean_reversion" in (
        blacklist)
    assert _R["new_entry_added"] == (
        "low_volume_downside_capitulation_mean_reversion")
    for expected_family in (
            "ny_session_fvg_choch_v3",
            "crypto_intraday_breakout_pullback_structure_v2",
            "btc_sol_long_trend_continuation_v1",
            "sol_btc_long_1h_swing_structure",
            "eth_sol_relative_strength_pullback_continuation_v1",
            "multi_symbol_relative_strength_rotation_filter",
            "volatility_compression_expansion",
            "liquidity_sweep_mean_reversion",
            "low_volume_downside_capitulation_mean_reversion"):
        assert expected_family in blacklist, expected_family


def test_v4_strict_subset_of_v5_with_exactly_one_new_entry():
    prior_v4 = set(_R["prior_v4_blacklist"])
    v5 = set(_R["rejected_family_logic_blacklist_v5"])
    assert prior_v4.issubset(v5)
    assert v5 - prior_v4 == {
        "low_volume_downside_capitulation_mean_reversion"}
    assert len(v5) == len(prior_v4) + 1


def test_c9_rejection_status_and_reason_carried_forward():
    assert _R["c9_rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert "EDIT_SPENT" in _R["c9_rejection_reason"]
    assert "RELAXED_DOWNSIDE_Z_SCORE_THRESHOLD" in _R[
        "c9_rejection_reason"]
    assert "SAMPLE_SIZE_STILL_BELOW_THRESHOLD" in _R[
        "c9_rejection_reason"]
    assert _R["c9_future_family_blacklist_addition"] == (
        "low_volume_downside_capitulation_mean_reversion")


# ---- per-family rejection reasons ----------------------------------------

def test_per_family_rejection_reason_complete_for_c1_through_c9():
    reasons = _R["per_family_rejection_reason"]
    for key in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8",
                "C9"):
        assert key in reasons, key
        assert len(reasons[key]) > 50, key
    c9 = reasons["C9"]
    assert "low volume downside capitulation mean reversion" in c9
    assert "1 accepted-post-anti-cluster" in c9
    assert "5 accepted-post post-edit" in c9
    assert "downside z-score threshold from -2.0 to -1.5" in c9
    assert "sample-size adequacy STILL failed (5 < 20" in c9
    assert ("volume condition (the structural microstructure edge) "
            "is the binding constraint") in c9


def test_ledger_family_labels_complete():
    labels = _R["ledger_family_labels"]
    assert labels == {
        "C1": "ny_session_fvg_choch_v3",
        "C2": "crypto_intraday_breakout_pullback_structure_v2",
        "C3": "btc_sol_long_trend_continuation_v1",
        "C4": "sol_btc_long_1h_swing_structure",
        "C5": "eth_sol_relative_strength_pullback_continuation_v1",
        "C6": "multi_symbol_relative_strength_rotation_filter",
        "C7": "volatility_compression_expansion",
        "C8": "liquidity_sweep_mean_reversion",
        "C9": "low_volume_downside_capitulation_mean_reversion"}


# ---- C10 proposal requirements -------------------------------------------

def test_c10_proposal_requirements_include_c9_lesson():
    reqs = _R["c10_proposal_requirements"]
    assert ("joint_or_intersection_trigger_sample_size_pre"
            "_justification") in reqs["required_fields"]
    assert reqs[
        "joint_or_intersection_trigger_sample_size_pre"
        "_justification_required"] is True
    assert reqs[
        "must_not_rely_on_overly_narrow_intersection_of_trigger"
        "_conditions_unless_sample_size_adequacy_is_pre_justified"
    ] is True
    assert reqs[
        "explicit_edge_argument_beyond_pattern_geometry_required"
    ] is True
    assert reqs[
        "fee_assumption_must_equal_27_bps_round_trip"] is True
    assert reqs["minimum_floor_must_equal_81_bps"] is True
    assert reqs[
        "anti_cluster_protection_must_be_built_in_at_proposal_time"
    ] is True
    assert reqs[
        "sample_size_adequacy_must_be_assessed_at_proposal_time"
    ] is True
    assert reqs["must_not_reuse_any_rejected_family_logic"] is True
    assert reqs["human_review_required_at_every_gate"] is True
    assert reqs["plan_is_not_a_promotion"] is True
    # differentiation must address every rejected family (incl. C9)
    diff_targets = tuple(
        reqs["differentiation_must_address_each_of"])
    assert len(diff_targets) == 9
    assert "low_volume_downside_capitulation_mean_reversion" in (
        diff_targets)


def test_inherited_lessons_include_c9_joint_trigger_sparsity():
    lessons = _R["inherited_lessons"]
    assert len(lessons) == 9
    joined = " || ".join(lessons)
    assert "c1_lesson:" in joined
    assert "c2_lesson:" in joined
    assert "c3_lesson:" in joined
    assert "c4_lesson:" in joined
    assert "c5_lesson:" in joined
    assert "c6_lesson:" in joined
    assert "c7_lesson:" in joined
    assert "c8_lesson:" in joined
    assert "c9_lesson:" in joined
    assert ("joint price-AND-volume thresholds can be structurally "
            "too sparse") in joined
    assert ("must not rely on an overly narrow intersection of "
            "trigger conditions unless sample-size adequacy is pre-"
            "justified") in joined
    assert ("C10 must clear the V5 blacklist and be materially "
            "different from C1-C9") in joined


# ---- downstream gates locked ---------------------------------------------

def test_no_downstream_unlocks_or_candidate_10_generation():
    assert _R["human_review_required"] is True
    assert _R["paper_trading_gate_locked"] is True
    assert _R["micro_live_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    for key in ("executes", "writes_files",
                "runs_detector", "runs_real_candle_detection",
                "runs_relabel", "runs_replay", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "generates_candidate_10_proposal_now",
                "generates_morning_report_now",
                "drafts_candidate_10_in_this_gate",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability",
                "uses_external_data_source"):
        assert _R[key] is False, key
        tampered = copy.deepcopy(_R)
        tampered[key] = True
        assert bl5.validate_rejected_family_blacklist_v5(
            tampered)["valid"] is False, key


def test_claim_locks_present():
    locks = _R["claim_locks"]
    for required in ("no_profitability_claim", "no_paper_approval",
                     "no_live_approval", "no_execution_approval",
                     "no_winner_wording", "no_promotion_by_v5",
                     "no_unlock_by_v5", "no_scheduler_activation",
                     "no_auto_commit", "no_auto_push",
                     "no_candidate_10_generation_in_this_gate",
                     "no_candidate_10_proposal_drafting_in_this"
                     "_gate"):
        assert required in locks, required
    tampered = copy.deepcopy(_R)
    tampered["claim_locks"] = []
    assert bl5.validate_rejected_family_blacklist_v5(
        tampered)["valid"] is False


def test_next_required_action_and_label_text():
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_DRAFT_CANDIDATE_10_FAMILY_PROPOSAL_USING_V5"
        "_BLACKLIST")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in bl5.NEXT_REQUIRED_ACTION.upper(), banned
    assert bl5.get_blacklist_v5_label() == bl5.BL5_LABEL
    assert bl5.BL5_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "NO EXECUTION", "NO TRADING",
                   "NO AUTO-PUSH", "NO SCHEDULER",
                   "NOT A PROFITABILITY CLAIM",
                   "NINE-FAMILY BLACKLIST"):
        assert phrase in bl5.BL5_LABEL, phrase


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(bl5.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir",
                 "rmdir", "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv",
                   "pandas", "pathlib", "os", "io", "json", "shutil",
                   "databento", "ssl", "ftplib", "hashlib",
                   "datetime", "statistics", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods), imported & banned_mods
    for call in ast.walk(tree):
        if not isinstance(call, ast.Call):
            continue
        name = (call.func.attr if isinstance(call.func, ast.Attribute)
                else getattr(call.func, "id", ""))
        assert name not in ("open", "exec", "eval", "compile"), name

"""Tests for the Candidate #9 family proposal contract
(LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1).

Verifies: chain-gate on the eight-record ledger + V4 + V3 + V2 +
Recommendation V1 + Autopilot Loop V1; V4 blacklist clearance;
single-symbol BTCUSD 15m long-only; explicit edge argument beyond
pattern geometry (V4-required field); material differences from
each of the 8 rejected families incl. C8; proposal-level
anti-cluster + sample-size adequacy + explicit-edge-argument
policies all locked NOT the edit token; 27/81 bps fee + floor;
human review required at every gate; all downstream capability
flags False; AST/purity green."""

from __future__ import annotations

import ast

import sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record as rj8
import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract as c9p
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as rec
import sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract as oap2
import sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract as bl3
import sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract as bl4


def _record():
    return c9p.build_candidate_9_family_proposal()


# ---- chain gate + ready verdict -------------------------------------------

def test_proposal_ready_and_chain_gates_all_certify():
    assert rj8.build_c8_rejection_record()["verdict"] == (
        rj8.VERDICT_RJ8_RECORDED)
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
    record = _record()
    assert record["verdict"] == c9p.VERDICT_C9P_READY
    assert record["blockers"] == []
    assert c9p.validate_candidate_9_family_proposal(
        record)["valid"] is True


def test_eight_record_ledger_intact():
    record = _record()
    assert record["ledger_status_eight_records"] == [
        "REJECTED_KEPT_ON_RECORD"] * 8
    assert record["ledger_all_rejected_kept_on_record"] is True


def test_chain_blocks_when_ledger_breaks():
    import sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_family_proposal_contract as mod
    originals = {k: getattr(mod, k) for k in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS",
                  "C4_STATUS", "C5_STATUS", "C6_STATUS",
                  "C7_STATUS", "C8_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            record = mod.build_candidate_9_family_proposal()
            assert record["verdict"] == c9p.VERDICT_C9P_BLOCKED, key
            assert "eight_record_ledger_broken" in record[
                "blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for k, v in originals.items():
            setattr(mod, k, v)
    assert mod.build_candidate_9_family_proposal()["verdict"] == (
        c9p.VERDICT_C9P_READY)


# ---- V4 blacklist clearance ----------------------------------------------

def test_v4_blacklist_clearance_and_v3_v2_certification():
    record = _record()
    assert record["v4_blacklist_clearance"] is True
    assert record["v4_blacklist_verdict"] == bl4.VERDICT_BL4_READY
    assert record["v3_blacklist_verdict"] == bl3.VERDICT_BL3_READY
    assert record["v2_verdict"] == oap2.VERDICT_OAP2_READY
    assert record["recommendation_verdict"] == rec.VERDICT_CR_READY
    assert record["autopilot_loop_verdict"] == ap.VERDICT_AP_READY


def test_family_name_not_in_any_rejected_tuple():
    record = _record()
    family = record["candidate_family"]
    assert family == "low_volume_downside_capitulation_mean_reversion"
    assert family not in (
        bl4.REJECTED_FAMILY_LOGIC_BLACKLIST_V4)
    assert family not in (
        bl3.REJECTED_FAMILY_LOGIC_BLACKLIST_V3)
    assert family not in oap2.REJECTED_FAMILY_LOGIC_BLACKLIST
    assert family not in ap.REJECTED_FAMILIES
    assert family not in rec.ALL_REJECTED_FAMILIES


# ---- universe / timeframe / direction / sample window --------------------

def test_universe_timeframe_direction_sample_window_locked():
    record = _record()
    assert record["symbols"] == ["BTCUSD"]
    assert record["timeframe"] == "15m"
    assert record["direction"] == "long_only"
    assert record["sample_window_proposal"] == "2026-05-02_2026-06-10"
    for field, value in (("symbols", ["BTCUSD", "ETHUSD"]),
                         ("symbols", []),
                         ("timeframe", "1h"),
                         ("timeframe", "4h"),
                         ("direction", "long_or_short"),
                         ("direction", "short_only"),
                         ("sample_window_proposal", "2025-01-01")):
        tampered = _record()
        tampered[field] = value
        assert c9p.validate_candidate_9_family_proposal(
            tampered)["valid"] is False, (field, value)


# ---- explicit edge argument beyond pattern geometry (V4-required) -------

def test_explicit_edge_argument_beyond_pattern_geometry_present():
    record = _record()
    edge = record["explicit_edge_argument_beyond_pattern_geometry"]
    # Must be a substantive multi-paragraph argument
    assert len(edge) > 1000
    assert "MICROSTRUCTURAL, NOT VISUAL" in edge
    assert "order-book asymmetry" in edge.lower() or (
        "ORDER-BOOK" in edge.upper())
    assert "27 BPS + 81 BPS" in edge or "27 bps" in edge.lower()
    assert "WHY THIS IS NOT C8" in edge
    assert "HOW THIS RESPECTS THE C8 LESSON" in edge
    # The argument must explain WHY the edge survives fees, not just
    # describe a pattern.
    for token in ("microstructural", "asymmetry", "deeper book",
                  "panic", "rever"):
        assert token in edge.lower(), token
    tampered = _record()
    tampered["explicit_edge_argument_beyond_pattern_geometry"] = (
        "just a chart pattern")
    assert c9p.validate_candidate_9_family_proposal(
        tampered)["valid"] is False


def test_explicit_edge_argument_policy_locked_and_not_edit_token():
    policy = _record()["explicit_edge_argument_policy"]
    assert policy["built_in_at_proposal_time"] is True
    assert policy["v4_required_field"] is True
    assert policy["argument_is_microstructural_not_visual"] is True
    assert policy[
        "argument_is_falsifiable_by_per_variant_net_r_sums"] is True
    assert policy["is_not_the_single_allowed_c9_edit"] is True
    tampered = _record()
    tampered["explicit_edge_argument_policy"][
        "is_not_the_single_allowed_c9_edit"] = False
    assert c9p.validate_candidate_9_family_proposal(
        tampered)["valid"] is False


def test_edge_source_hypothesis_frozen():
    record = _record()
    eh = record["edge_source_hypothesis"]
    assert "order-book" in eh.lower() or "ORDER-BOOK" in eh.upper()
    assert "ASYMMETRY" in eh.upper()
    assert "deeper book" in eh.lower()
    assert "27 bps" in eh.lower() and "81 bps" in eh.lower()


# ---- material differences from all 8 rejected families ------------------

def test_material_differences_from_each_rejected_family():
    record = _record()
    diff = record["difference_from_rejected_families"]
    # All 8 prior families must be explicitly addressed
    assert "ny-session fvg/choch" in diff
    assert "breakout-pullback" in diff
    assert "btc/sol long trend continuation" in diff
    assert "sol/btc 1h swing structure" in diff
    assert "eth/sol relative-strength pullback continuation" in diff
    assert "multi-symbol relative-strength rotation" in diff
    assert "volatility compression-expansion" in diff
    assert "liquidity sweep mean reversion" in diff
    # And the JOINT price-AND-volume distinction
    assert "JOINT price-and-volume" in diff
    assert "microstructure asymmetry" in diff


def test_explicit_non_reuse_of_rejected_family_logic_covers_c1_c8():
    nonreuse = _record()[
        "explicit_non_reuse_of_rejected_family_logic"]
    joined = " || ".join(nonreuse)
    for c in ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"):
        assert c in joined, c
    assert "ny-session" in joined
    assert "range-breakout" in joined
    assert "trend-continuation" in joined
    assert "swing-pivot" in joined
    assert "relative-strength" in joined
    assert "multi-symbol rank" in joined
    assert "atr contraction" in joined
    assert "sweep-below-prior-low" in joined
    assert "no C1-C8 setup_ids" in joined


# ---- locked fee / floor / anti-cluster / sample-size / human-review -----

def test_fee_and_floor_locked_27_and_81_bps():
    fee = _record()["fee_aware_geometry_policy"]
    assert fee["fee_model_round_trip_bps"] == 27
    assert fee["minimum_gross_target_distance_floor_bps"] == 81
    assert fee["floor_is_3x_round_trip_fees"] is True
    assert fee["no_maker_rebate_assumption"] is True
    assert fee["no_zero_fee_assumption"] is True
    for value in (0, 5, 13, 26, 28, 50, 100):
        tampered = _record()
        tampered["fee_aware_geometry_policy"]["fee_model_round_trip"
                                              "_bps"] = value
        assert c9p.validate_candidate_9_family_proposal(
            tampered)["valid"] is False, value
    for value in (0, 27, 80, 82, 162):
        tampered = _record()
        tampered["fee_aware_geometry_policy"][
            "minimum_gross_target_distance_floor_bps"] = value
        assert c9p.validate_candidate_9_family_proposal(
            tampered)["valid"] is False, value


def test_anti_cluster_policy_proposal_locked_not_edit_token():
    policy = _record()["anti_cluster_policy"]
    assert policy["built_in_at_label_emission_time"] is True
    assert policy[
        "scope"] == "per_symbol_minimum_bar_gap_between_accepted_events"
    assert policy["is_not_the_single_allowed_c9_edit"] is True
    assert policy[
        "applies_before_replay_time_non_overlap"] is True
    assert policy["replay_time_non_overlap_unchanged"] is True
    tampered = _record()
    tampered["anti_cluster_policy"][
        "is_not_the_single_allowed_c9_edit"] = False
    assert c9p.validate_candidate_9_family_proposal(
        tampered)["valid"] is False


def test_sample_size_adequacy_policy_proposal_locked_not_edit_token():
    policy = _record()["sample_size_adequacy_policy"]
    assert policy["built_in_at_proposal_time"] is True
    assert policy[
        "applies_at_labels_review_gate"] is True
    assert policy[
        "below_threshold_triggers_structural_rejection_without_edit"
        "_token"] is True
    assert policy["is_not_the_single_allowed_c9_edit"] is True
    tampered = _record()
    tampered["sample_size_adequacy_policy"][
        "is_not_the_single_allowed_c9_edit"] = False
    assert c9p.validate_candidate_9_family_proposal(
        tampered)["valid"] is False


def test_edit_allowance_one_token_must_target_different_parameter():
    record = _record()
    edit = record["edit_allowance_policy"]
    assert "ONE pre-committed edit" in edit
    assert "REJECTED_KEPT_ON_RECORD" in edit
    assert "anti-cluster policy" in edit
    assert "sample-size adequacy" in edit
    assert "explicit-edge-argument field" in edit
    assert "different structural parameter" in edit


def test_human_review_required_at_every_gate():
    record = _record()
    assert record["human_review_required"] is True
    assert record["human_review_required_at_every_gate"] is True
    assert record["plan_is_not_a_promotion"] is True
    for key in ("human_review_required",
                "human_review_required_at_every_gate",
                "plan_is_not_a_promotion"):
        tampered = _record()
        tampered[key] = False
        assert c9p.validate_candidate_9_family_proposal(
            tampered)["valid"] is False, key


# ---- trigger family / stop family ---------------------------------------

def test_trigger_family_is_joint_price_and_volume_microstructure():
    trigger = _record()["trigger_family"]
    assert trigger["name"] == "low_volume_downside_capitulation_event"
    assert "z-score" in trigger["definition"]
    assert "median volume" in trigger["definition"]
    assert "JOINT" in trigger["definition"]
    assert trigger[
        "is_a_joint_price_and_volume_microstructure_trigger"] is True
    assert trigger["is_not_a_cross_symbol_rs_filter"] is True
    assert trigger["is_not_a_session_anchored_trigger"] is True
    assert trigger["is_not_a_breakout_pullback_trigger"] is True
    assert trigger["is_not_a_trend_ma_filter"] is True
    assert trigger["is_not_a_swing_pivot_trigger"] is True
    assert trigger[
        "is_not_an_atr_contraction_expansion_trigger"] is True
    assert trigger[
        "is_not_a_relative_strength_rotation_trigger"] is True
    assert trigger["is_not_a_sweep_reclaim_trigger"] is True
    assert trigger["uses_completed_15m_bars_only"] is True
    assert trigger["no_future_bars"] is True
    assert trigger["no_same_bar_lookahead"] is True
    assert trigger["no_intrabar_entry"] is True


def test_stop_family_structure_based_below_trigger_low():
    stop = _record()["stop_family"]
    assert "trigger_bar_low" in stop["rule"]
    assert stop["never_tightened_after_entry"] is True
    assert stop["stop_must_be_below_entry"] is True
    assert stop["invalid_if_stop_distance_not_positive"] is True


def test_target_variants_2r_3r_4r():
    targets = _record()["target_policy"]
    assert targets["variants"] == ["2r", "3r", "4r"]
    assert targets["target_price_formula"] == (
        "entry_price + r_multiple * stop_distance")
    assert targets["no_new_variants_after_label_freeze"] is True


# ---- proposal-only safety / capability flags ----------------------------

def test_proposal_only_with_all_downstream_locked():
    record = _record()
    assert record["is_proposal_only"] is True
    assert record["is_a_rescue_attempt"] is False
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for key in ("runs_spec_review_now", "runs_detector",
                "runs_real_candle_detection",
                "runs_real_detection_now",
                "labels_now", "runs_replay", "runs_replay_now",
                "runs_relabel", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "uses_account",
                "connects_broker", "connects_exchange",
                "uses_real_money", "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_label_replay_files_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "executes", "writes_files"):
        assert record[key] is False, key
        tampered = _record()
        tampered[key] = True
        assert c9p.validate_candidate_9_family_proposal(
            tampered)["valid"] is False, key


def test_label_and_next_required_action():
    record = _record()
    assert record["candidate_family"] == (
        "low_volume_downside_capitulation_mean_reversion")
    assert record["candidate_id"] == (
        "LOW_VOLUME_DOWNSIDE_CAPITULATION_MEAN_REVERSION_V1")
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_9_SPEC_REVIEW")
    assert record["next_loop_stage"] == "candidate_spec"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH",
                   "EXECUTE", "EXECUTION", "BACKTEST", "BASELINE",
                   "PAPER", "LIVE", "BROKER", "EXCHANGE",
                   "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c9p.NEXT_REQUIRED_ACTION.upper(), banned
    assert c9p.get_candidate_9_proposal_label() == c9p.C9P_LABEL
    assert c9p.C9P_MODE == "RESEARCH_ONLY"
    for phrase in ("READ-ONLY", "RESEARCH ONLY",
                   "PROPOSAL GATE ONLY",
                   "EXPLICIT EDGE ARGUMENT BEYOND PATTERN GEOMETRY",
                   "NOT A RESCUE", "NOT A CLAIM"):
        assert phrase in c9p.C9P_LABEL, phrase
    for banned_phrase in ("WINNER", "PROFITABLE",
                          "EDGE CONFIRMED",
                          "APPROVED FOR PAPER",
                          "APPROVED FOR LIVE"):
        assert banned_phrase not in c9p.C9P_LABEL.upper(), (
            banned_phrase)


# ---- safety claims + seeds never rescue ----------------------------------

def test_safety_and_no_claim_complete():
    safety = _record()["safety_and_no_claim"]
    joined = " || ".join(safety)
    for required in ("no trading", "no paper trading",
                     "no live trading",
                     "no wallet, account, api, or order capability",
                     "no auto-push, no auto-commit",
                     "no scheduler activation",
                     "no profitability claim and no winner wording",
                     "every stage requires evidence freeze and "
                     "explicit human gates"):
        assert required in joined, required


def test_seeds_are_inspiration_never_rescue():
    record = _record()
    assert record["seeds_are_never_rescue_paths"] is True
    seeds = " || ".join(record["seed_usage"])
    assert "c6_clustering_lesson_is_inspiration" in seeds
    assert "c7_sample_size_adequacy_lesson_is_inspiration" in seeds
    assert "c8_explicit_edge_argument_lesson_is_inspiration" in seeds
    assert ("the_btcusd_15m_volume_column_in_the_staged_data_is_a"
            "_new_input_that_c1_through_c8_did_not_consume"
            "_structurally") in seeds
    assert ("no_c1_c8_setup_ids_replay_rows_labels_edited_labels_or"
            "_replay_results_may_be_reused") in seeds


def test_rationale_paragraph_mentions_c1_c8_and_volume_column():
    rationale = _record()["rationale_paragraph"]
    assert "C1-C8" in rationale or "C1-C5" in rationale
    assert "volume column" in rationale
    assert "order-book asymmetry" in rationale.lower() or (
        "ORDER-BOOK" in rationale.upper())
    assert "2026-05-02_2026-06-10" in rationale
    # The 27 bps + 81 bps fee/floor numerics are locked separately in
    # FEE_AWARE_GEOMETRY_POLICY; the rationale paragraph references
    # the fee-aware/fee-honest framing rather than repeating the
    # numerics.
    assert "fee-aware" in rationale.lower() or (
        "fee-honest" in rationale.lower())


# ---- module purity --------------------------------------------------------

def test_module_purity_no_banned_imports_no_open_no_main():
    src = open(c9p.__file__, encoding="utf-8").read()
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

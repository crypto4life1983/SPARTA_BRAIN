"""Tests for the Candidate #7 single pre-committed edit
(relaxed contraction fraction 0.6 -> 0.7).

Coverage: certifies APPROVED when the full upstream chain holds and
the labels review certifies zero accepted setups; any second-edit
attempt rejects; any inviolable rule mutation rejects (ATR length /
rolling window / contraction window count / expansion multiplier /
upper-third / structure lookback / WIDER stop multiplier / target
variants / fee 27 / floor 81 / universe / timeframe / direction /
anti-cluster 6 / sample tag); the edit rule is exactly the 0.6->0.7
relaxation; review fails if any frozen motivation fact changes;
downstream replay/relabel/paper/live/profitability all remain locked;
no trading-adjacent capability; AST/purity green. Commander safety
suite runs alongside."""

from __future__ import annotations

import ast

import sparta_commander.volatility_compression_expansion_v1_single_edit_relaxed_contraction_decision_contract as c7e


REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_record():
    return c7e.build_c7_single_edit_relaxed_contraction(
        REPO_ROOT, tracked_paths=[])


# (1) certifies APPROVED end-to-end ---------------------------------------

def test_1_single_edit_certifies_approved():
    record = _good_record()
    assert record["verdict"] == c7e.VERDICT_C7E_APPROVED
    assert record["blockers"] == []
    assert c7e.validate_c7_single_edit_relaxed_contraction(
        record)["valid"] is True
    assert _good_record() == record  # determinism
    assert record["edit_token_used"] == 1
    assert record["edits_remaining_after_this"] == 0
    assert record["this_is_the_only_allowed_c7_edit"] is True
    assert record["edit_token_spent_by_this_contract"] is True
    assert record["edit_kind"] == (
        "relaxed_contraction_fraction_only")
    assert record["is_a_rescue_attempt"] is False
    assert record["is_single_controlled_relaxation"] is True
    assert record["is_a_rescue_bundle"] is False


# (2) only CONTRACTION_FRACTION changes (0.6 -> 0.7), nothing else --------

def test_2_only_contraction_fraction_changes_0_6_to_0_7():
    record = _good_record()
    assert record["edit_parameter_name"] == "CONTRACTION_FRACTION"
    assert record["edit_parameter_old_value"] == 0.6
    assert record["edit_parameter_new_value"] == 0.7
    rule = record["edit_rule"]
    assert rule["parameter"] == "CONTRACTION_FRACTION"
    assert rule["old_value"] == 0.6
    assert rule["new_value"] == 0.7
    assert rule[
        "is_a_single_controlled_relaxation_not_a_bundle"] is True
    assert rule["no_other_detector_change"] is True
    for field, value in (
            ("edit_parameter_name", "OTHER_PARAM"),
            ("edit_parameter_old_value", 0.5),
            ("edit_parameter_new_value", 0.8),
            ("edit_parameter_new_value", 0.6)):  # no-op rejects too
        tampered = _good_record()
        tampered[field] = value
        assert c7e.validate_c7_single_edit_relaxed_contraction(
            tampered)["valid"] is False, (field, value)


# (3) any second edit rejects --------------------------------------------

def test_3_rejects_any_second_edit():
    for field, value in (
            ("edit_token_used", 2), ("edit_token_used", 0),
            ("edits_remaining_after_this", 1),
            ("edits_remaining_after_this", 2),
            ("this_is_the_only_allowed_c7_edit", False),
            ("edit_token_spent_by_this_contract", False)):
        tampered = _good_record()
        tampered[field] = value
        result = c7e.validate_c7_single_edit_relaxed_contraction(
            tampered)
        assert result["valid"] is False, field
    triggers = _good_record()["post_edit_auto_rejection_triggers"]
    assert "any_attempt_to_spend_a_second_edit_on_this_family" in (
        triggers)


# (4) ATR length / rolling window / contraction window count locked -------

def test_4_rejects_changing_atr_or_window_numerics():
    rec = _good_record()
    invio = rec["inviolable_rules"]
    assert invio["atr_length"] == 14
    assert invio["atr_rolling_average_window_4h_bars"] == 100
    assert invio["contraction_window_bars"] == 5
    for mutation in ({"atr_length": 7}, {"atr_length": 21},
                     {"atr_rolling_average_window_4h_bars": 50},
                     {"atr_rolling_average_window_4h_bars": 200},
                     {"contraction_window_bars": 3},
                     {"contraction_window_bars": 7},
                     {"contraction_window_bars": 0}):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], **mutation)
        assert c7e.validate_c7_single_edit_relaxed_contraction(
            tampered)["valid"] is False, mutation


# (5) expansion multiplier / upper-third locked ---------------------------

def test_5_rejects_changing_expansion_or_upper_third():
    rec = _good_record()
    invio = rec["inviolable_rules"]
    assert invio["expansion_true_range_multiplier"] == 1.8
    assert invio["close_in_upper_third_required"] is True
    for mutation in ({"expansion_true_range_multiplier": 1.5},
                     {"expansion_true_range_multiplier": 2.5},
                     {"close_in_upper_third_required": False}):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], **mutation)
        assert c7e.validate_c7_single_edit_relaxed_contraction(
            tampered)["valid"] is False, mutation


# (6) WIDER stop multiplier / structure lookback / formula locked ---------

def test_6_rejects_changing_stop_geometry():
    rec = _good_record()
    invio = rec["inviolable_rules"]
    assert invio["wider_stop_atr_multiplier"] == 1.5
    assert invio["structure_lookback_bars"] == 10
    assert invio["stop_distance_formula"] == (
        "max(wider_stop_atr_multiplier * atr14, "
        "structure_stop_distance)")
    for mutation in ({"wider_stop_atr_multiplier": 1.0},
                     {"wider_stop_atr_multiplier": 2.0},
                     {"structure_lookback_bars": 5},
                     {"structure_lookback_bars": 20},
                     {"stop_distance_formula": "1.5*atr14"},
                     {"stop_distance_formula":
                          "min(1.5*atr14, structure_stop_distance)"}):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], **mutation)
        assert c7e.validate_c7_single_edit_relaxed_contraction(
            tampered)["valid"] is False, mutation


# (7) target variants / fee 27 / floor 81 locked --------------------------

def test_7_rejects_changing_targets_fee_or_floor():
    rec = _good_record()
    invio = rec["inviolable_rules"]
    assert invio["target_variants"] == ["2r", "3r", "4r"]
    assert invio["fee_round_trip_bps"] == 27
    assert invio["minimum_gross_target_distance_floor_bps"] == 81
    for mutation in ({"target_variants": ["2r", "3r"]},
                     {"target_variants": ["1r", "2r", "3r"]},
                     {"fee_round_trip_bps": 0},
                     {"fee_round_trip_bps": 50},
                     {"minimum_gross_target_distance_floor_bps": 0},
                     {"minimum_gross_target_distance_floor_bps": 100},
                     {"no_maker_rebate_assumption": False},
                     {"no_zero_fee_assumption": False}):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], **mutation)
        assert c7e.validate_c7_single_edit_relaxed_contraction(
            tampered)["valid"] is False, mutation


# (8) universe / timeframe / direction / sample-tag locked ---------------

def test_8_rejects_changing_universe_timeframe_direction_sample():
    rec = _good_record()
    invio = rec["inviolable_rules"]
    assert invio["universe"] == ["BTCUSD"]
    assert invio["timeframe"] == "4h"
    assert invio["direction"] == "long_only"
    assert invio["sample_tag"] == "2026-05-02_2026-06-10"
    for mutation in ({"universe": ["BTCUSD", "ETHUSD"]},
                     {"universe": ["SOLUSD"]},
                     {"timeframe": "1h"}, {"timeframe": "1d"},
                     {"direction": "long_or_short"},
                     {"direction": "short_only"},
                     {"sample_tag": "2026-04-01_2026-05-01"}):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], **mutation)
        assert c7e.validate_c7_single_edit_relaxed_contraction(
            tampered)["valid"] is False, mutation


# (9) anti-cluster gap remains proposal-level locked, not edit token -----

def test_9_anti_cluster_remains_proposal_level_locked():
    rec = _good_record()
    invio = rec["inviolable_rules"]
    assert invio["anti_cluster_min_bar_gap"] == 6
    assert invio[
        "anti_cluster_is_proposal_level_locked_not_edit_token"] is True
    for mutation in ({"anti_cluster_min_bar_gap": 1},
                     {"anti_cluster_min_bar_gap": 24},
                     {"anti_cluster_is_proposal_level_locked_not"
                      "_edit_token": False}):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], **mutation)
        assert c7e.validate_c7_single_edit_relaxed_contraction(
            tampered)["valid"] is False, mutation
    # the claim locks must include this
    locks = rec["claim_locks"]
    assert (
        "anti_cluster_gap_remains_proposal_level_locked_not_edit_token"
        in locks)


# (10) review fails if any frozen motivation fact changes -----------------

def test_10_review_fails_on_motivation_changes():
    record = _good_record()
    ev = record["frozen_labels_review_evidence_for_edit"]
    assert ev["total_attempts"] == 122
    assert ev["accepted_pre_anti_cluster"] == 0
    assert ev["accepted_post_anti_cluster"] == 0
    assert ev["rejected_by_scanner"] == 122
    assert ev["dropped_by_anti_cluster"] == 0
    assert ev["status_breakdown"] == {
        "rejected_contraction_window": 122}
    assert ev["floor_pass_counts"] == {
        "2r": 0, "3r": 0, "4r": 0}
    assert ev["all_attempts_rejected_on_contraction_window"] is True
    assert ev["zero_accepted_setups"] is True
    assert ev["zero_floor_pass_at_any_variant"] is True
    assert ev["edit_token_unused_before_this_decision"] is True
    assert ev["no_replay_run"] is True
    assert ev["no_pnl_computed"] is True
    for mutation in (
            {"total_attempts": 100},
            {"accepted_pre_anti_cluster": 5},
            {"accepted_post_anti_cluster": 5},
            {"rejected_by_scanner": 100},
            {"dropped_by_anti_cluster": 3},
            {"status_breakdown":
             {"rejected_expansion_multiplier": 122}},
            {"floor_pass_counts": {"2r": 1, "3r": 0, "4r": 0}},
            {"all_attempts_rejected_on_contraction_window": False},
            {"zero_accepted_setups": False},
            {"zero_floor_pass_at_any_variant": False},
            {"edit_token_unused_before_this_decision": False},
            {"no_replay_run": False},
            {"no_pnl_computed": False}):
        tampered = _good_record()
        tampered["frozen_labels_review_evidence_for_edit"] = dict(
            tampered["frozen_labels_review_evidence_for_edit"],
            **mutation)
        assert c7e.validate_c7_single_edit_relaxed_contraction(
            tampered)["valid"] is False, mutation


# (11) downstream replay/relabel/paper/live/profit/PnL all locked --------

def test_11_downstream_gates_all_remain_locked():
    record = _good_record()
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for key in ("runs_real_candle_detection",
                "runs_edited_real_candle_detection",
                "runs_relabel", "runs_replay",
                "labels_now", "runs_real_detection_now",
                "runs_replay_now", "modifies_detector_artifacts",
                "modifies_labels_artifacts", "computes_pnl_now",
                "authorizes_edited_real_candle_detection",
                "authorizes_relabel", "authorizes_replay",
                "authorizes_pnl_now",
                "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_replay_gate", "unlocks_relabel_gate",
                "unlocks_paper_gate", "unlocks_micro_live_gate",
                "unlocks_live_gate", "claims_profitability"):
        assert record[key] is False, key
        tampered = _good_record()
        tampered[key] = True
        assert c7e.validate_c7_single_edit_relaxed_contraction(
            tampered)["valid"] is False, key


# (12) no trading-adjacent capability and zero I/O -----------------------

def test_12_no_trading_adjacent_capability_zero_io():
    record = _good_record()
    for key in ("executes", "writes_files", "scores_now",
                "stages_data_now", "fetches_data", "calls_api",
                "uses_network", "uses_credentials", "uses_wallet",
                "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes",
                "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data"):
        assert record[key] is False, key
        tampered = _good_record()
        tampered[key] = True
        assert c7e.validate_c7_single_edit_relaxed_contraction(
            tampered)["valid"] is False, key
    # claim locks contain the no-paper/no-live/no-profit/no-rescue
    locks = record["claim_locks"]
    for lock in (
            "edit_is_single_parameter_relaxation_only_no_bundle",
            "edit_does_not_authorize_edited_real_candle_detection"
            "_by_itself",
            "edit_does_not_authorize_relabel",
            "edit_does_not_authorize_replay",
            "edit_does_not_authorize_pnl_computation",
            "edit_does_not_authorize_paper_or_live_or_execution",
            "edit_is_not_a_rescue_attempt",
            "no_profitability_claim", "no_winner_wording",
            "automatic_rejection_if_any_post_edit_trigger_fires",
            "single_pre_committed_edit_token_spent_no_further_"
            "edits_allowed"):
        assert lock in locks, lock


# (13) next gate is edited real-candle detection only --------------------

def test_13_next_gate_is_edited_real_candle_detection_only():
    record = _good_record()
    assert record["next_required_action"] == (
        "HUMAN_APPROVED_CANDIDATE_7_EDITED_REAL_CANDLE_DETECTION"
        "_RELAXED_CONTRACTION")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c7e.NEXT_REQUIRED_ACTION.upper(), banned


# (14) AST/purity --------------------------------------------------------

def test_14_ast_purity_and_no_writers_or_runners():
    assert c7e.get_c7_single_edit_label() == c7e.C7E_LABEL
    assert "READ-ONLY" in c7e.C7E_LABEL
    assert "RESEARCH ONLY" in c7e.C7E_LABEL
    assert "SINGLE PARAMETER RELAXATION ONLY" in c7e.C7E_LABEL
    assert "NOT A RESCUE" in c7e.C7E_LABEL
    assert "NOT A CLAIM" in c7e.C7E_LABEL
    assert c7e.C7E_MODE == "RESEARCH_ONLY"
    assert c7e.VERDICT_C7E_APPROVED == (
        "CANDIDATE_7_SINGLE_EDIT_RELAXED_CONTRACTION_APPROVED")
    src = open(c7e.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "random" not in src
    assert "now(" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "subprocess", "Popen", "system("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "pathlib", "os", "io", "json", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "hashlib", "statistics",
                   "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))


# (15) chain blocks when ledger breaks -----------------------------------

def test_15_blocks_when_ledger_breaks():
    import sparta_commander.volatility_compression_expansion_v1_single_edit_relaxed_contraction_decision_contract as mod
    originals = {key: getattr(mod, key) for key in
                 ("C1_STATUS", "C2_STATUS", "C3_STATUS", "C4_STATUS",
                  "C5_STATUS", "C6_STATUS")}
    try:
        for key in originals:
            setattr(mod, key, "APPROVED_FOR_TRADING")
            rec = mod.build_c7_single_edit_relaxed_contraction(
                REPO_ROOT, tracked_paths=[])
            assert rec["verdict"] == c7e.VERDICT_C7E_BLOCKED, key
            assert "six_record_ledger_broken" in rec["blockers"], key
            setattr(mod, key, originals[key])
    finally:
        for key, value in originals.items():
            setattr(mod, key, value)
    assert mod.build_c7_single_edit_relaxed_contraction(
        REPO_ROOT, tracked_paths=[])["verdict"] == (
            c7e.VERDICT_C7E_APPROVED)

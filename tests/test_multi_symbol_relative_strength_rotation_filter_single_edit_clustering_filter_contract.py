"""Tests for the Candidate #6 single pre-committed edit
(same-symbol clustering filter at label time).

Coverage:
 (1) one clustering-filter edit passes,
 (2) any second edit rejects,
 (3-10) every inviolable upstream rule rejects mutation,
 (11) target/stop/profitability manipulation rejects,
 (12) motivated by the frozen replay evidence (334 overlap skips and
      all variants net-negative),
 (13) replay/edit/rejection/paper/live remain behind later explicit
      gates,
 (14) no trading-adjacent capability,
 (15) AST/purity (no network, api, order, wallet, account, credential,
      scheduler, runner, write verbs, `__main__`, random, wall clock,
      banned token in NEXT_REQUIRED_ACTION).
Commander safety suite runs alongside (12 tests).
"""

from __future__ import annotations

import ast
import copy

import sparta_commander.multi_symbol_relative_strength_rotation_filter_single_edit_clustering_filter_contract as c6e
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap


REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_record():
    return c6e.build_c6_single_edit_clustering_filter(
        REPO_ROOT, tracked_paths=[])


# (1) - the single clustering-filter edit certifies READY end-to-end ---------

def test_1_single_clustering_filter_edit_certifies_ready():
    record = _good_record()
    assert record["verdict"] == c6e.VERDICT_C6E_READY
    assert record["blockers"] == []
    assert c6e.validate_c6_single_edit_clustering_filter(
        record)["valid"] is True
    # determinism
    assert _good_record() == record
    # this is the only allowed C6 edit
    assert record["edit_token_used"] == 1
    assert record["edits_remaining_after_this"] == 0
    assert record["this_is_the_only_allowed_c6_edit"] is True
    assert record["edit_token_spent_by_this_contract"] is True
    # the edit is structure-only and not a rescue
    assert record["edit_kind"] == (
        "label_time_same_symbol_minimum_bar_gap_clustering_filter")
    assert record["is_a_rescue_attempt"] is False


# (2) - rejects any second edit on this family --------------------------------

def test_2_rejects_any_second_edit():
    for field, value in (
            ("edit_token_used", 2),
            ("edit_token_used", 0),
            ("edits_remaining_after_this", 1),
            ("edits_remaining_after_this", 2),
            ("this_is_the_only_allowed_c6_edit", False),
            ("edit_token_spent_by_this_contract", False)):
        tampered = _good_record()
        tampered[field] = value
        result = c6e.validate_c6_single_edit_clustering_filter(tampered)
        assert result["valid"] is False, field
    # explicit second-edit attempt -> capability lock fires
    tampered = _good_record()
    tampered["edit_token_used"] = 2
    errors = c6e.validate_c6_single_edit_clustering_filter(
        tampered)["errors"]
    assert "edit_token_used_must_be_exactly_1" in errors
    # one of the post-edit triggers enforces this at the rule level too
    triggers = _good_record()["post_edit_auto_rejection_triggers"]
    assert "any_attempt_to_spend_a_second_edit_on_this_family" in (
        triggers)


# (3) - rejects changing the RS metric or the 20-bar RS lookback --------------

def test_3_rejects_changing_rs_metric_or_lookback():
    rec = _good_record()
    assert rec["inviolable_rules"]["rs_metric"] == "close_to_close_return"
    assert rec["inviolable_rules"]["rs_lookback_bars_1h"] == 20
    for mutation in ({"rs_metric": "momentum_oscillator"},
                     {"rs_lookback_bars_1h": 5},
                     {"rs_lookback_bars_1h": 50},
                     {"rs_formula": "return_5 = close[t]/close[t-5] - 1"}):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], **mutation)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, mutation


# (4) - rejects changing strict-rank-#1 tie handling --------------------------

def test_4_rejects_changing_strict_rank_tie_handling():
    rec = _good_record()
    assert rec["inviolable_rules"][
        "rank_rule"] == "strict_rank_1_ties_fail"
    assert rec["inviolable_rules"][
        "rank_additional_rule"] == "return_20(candidate) > 0"
    for value in ("strict_rank_1_ties_pass", "ranked_2_or_better",
                  "no_rank_requirement", "ties_keep_both"):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], rank_rule=value)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, value
    # weakening the > 0 floor on the leader return also rejects
    tampered = _good_record()
    tampered["inviolable_rules"] = dict(
        tampered["inviolable_rules"],
        rank_additional_rule="no_floor_on_leader_return")
    assert c6e.validate_c6_single_edit_clustering_filter(
        tampered)["valid"] is False


# (5) - rejects changing the 10-bar fresh-closing-high continuation rule ------

def test_5_rejects_changing_continuation_fresh_high_rule():
    rec = _good_record()
    assert rec["inviolable_rules"][
        "continuation_event_closing_high_lookback_bars"] == 10
    for value in (3, 5, 20, 50, 100):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"],
            continuation_event_closing_high_lookback_bars=value)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, value
    # weakening entry-price or evaluation-start rules
    for mutation in (
            {"continuation_entry_price": "midprice"},
            {"continuation_entry_price": "next_bar_open"},
            {"continuation_evaluation_starts":
                "same_bar_as_event_close"}):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], **mutation)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, mutation


# (6) - rejects changing the WIDER-stop formula -------------------------------

def test_6_rejects_changing_wider_stop_formula():
    rec = _good_record()
    assert rec["inviolable_rules"]["stop_distance_formula"] == (
        "max(1.5 * atr14, structure_stop_distance)")
    assert rec["inviolable_rules"]["structure_lookback_bars"] == 10
    for value in ("min(1.5 * atr14, structure_stop_distance)",
                  "1.0 * atr14",
                  "0.5 * structure_stop_distance",
                  "fixed_2_percent"):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], stop_distance_formula=value)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, value
    # the 10-bar structure lookback is locked too
    for value in (3, 5, 20, 50):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], structure_lookback_bars=value)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, value


# (7) - rejects changing the ATR period or multiplier -------------------------

def test_7_rejects_changing_atr_period_or_multiplier():
    rec = _good_record()
    assert rec["inviolable_rules"]["atr_length"] == 14
    assert rec["inviolable_rules"]["atr_multiplier"] == 1.5
    for value in (7, 21, 30, 100):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], atr_length=value)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, value
    for value in (0.5, 1.0, 2.0, 3.0):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], atr_multiplier=value)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, value


# (8) - rejects changing the 27 bps round-trip fee ----------------------------

def test_8_rejects_changing_27_bps_fee():
    rec = _good_record()
    assert rec["inviolable_rules"]["fee_round_trip_bps"] == 27
    assert rec["inviolable_rules"]["no_maker_rebate_assumption"] is True
    assert rec["inviolable_rules"]["no_zero_fee_assumption"] is True
    for value in (0, 5, 13, 20, 26, 28, 50, 100):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], fee_round_trip_bps=value)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, value
    for assumption in ("no_maker_rebate_assumption",
                       "no_zero_fee_assumption"):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], **{assumption: False})
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, assumption


# (9) - rejects changing the 81 bps gross-target-distance floor ---------------

def test_9_rejects_changing_81_bps_floor():
    rec = _good_record()
    assert rec["inviolable_rules"][
        "minimum_gross_target_distance_floor_bps"] == 81
    for value in (0, 27, 54, 80, 82, 100, 162):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"],
            minimum_gross_target_distance_floor_bps=value)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, value


# (10) - rejects changing the universe ----------------------------------------

def test_10_rejects_changing_universe():
    rec = _good_record()
    assert rec["inviolable_rules"]["universe"] == [
        "BTCUSD", "ETHUSD", "SOLUSD"]
    for value in (["BTCUSD"], ["BTCUSD", "ETHUSD"],
                  ["BTCUSD", "ETHUSD", "SOLUSD", "DOGEUSD"],
                  ["SOLUSD", "ETHUSD", "BTCUSD"]):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], universe=value)
        result = c6e.validate_c6_single_edit_clustering_filter(tampered)
        assert result["valid"] is False, value
        assert "universe_changed" in result["errors"] or (
            "inviolable_rules_tampered" in result["errors"]), value


# (11) - rejects target/stop/fee/profitability manipulation -------------------

def test_11_rejects_target_stop_profitability_manipulation():
    # target variants
    rec = _good_record()
    assert rec["inviolable_rules"]["target_variants"] == [
        "2r", "3r", "4r"]
    for value in (["1r"], ["5r", "10r"], ["2r", "3r"],
                  ["2r", "3r", "4r", "5r"]):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], target_variants=value)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, value
    # target price formula
    for value in (
            "entry_price + 1.0 * stop_distance",
            "entry_price + 5.0 * stop_distance",
            "fixed_take_profit_at_3_percent"):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], target_price_formula=value)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, value
    # direction
    for value in ("long_or_short", "short_only", "either_side"):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], direction=value)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, value
    # profitability/winner claim flips
    for field in ("claims_profitability",
                  "authorizes_paper_execution",
                  "authorizes_live_trading",
                  "authorizes_relabel", "authorizes_replay",
                  "promotes_gate", "unlocks_downstream_gate",
                  "is_a_rescue_attempt"):
        tampered = _good_record()
        tampered[field] = True
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, field
    # claim locks tamper
    tampered = _good_record()
    tampered["claim_locks"] = []
    assert c6e.validate_c6_single_edit_clustering_filter(
        tampered)["valid"] is False


# (12) - motivated by the frozen replay evidence (334 + net-negative) ---------

def test_12_motivation_is_frozen_replay_evidence():
    ev = _good_record()["frozen_replay_evidence_for_edit"]
    # the 334 overlap skips number is preserved verbatim
    assert ev["total_overlap_skips_across_variants"] == 334
    assert ev["variant_2r_skipped_overlap"] == 109
    assert ev["variant_3r_skipped_overlap"] == 111
    assert ev["variant_4r_skipped_overlap"] == 114
    assert (ev["variant_2r_skipped_overlap"]
            + ev["variant_3r_skipped_overlap"]
            + ev["variant_4r_skipped_overlap"]) == 334
    # eligible setups are the original 135
    assert ev["eligible_setups_after_label_freeze"] == 135
    # kept-after-non-overlap matches the pushed replay review
    assert ev["variant_2r_kept_after_non_overlap"] == 26
    assert ev["variant_3r_kept_after_non_overlap"] == 24
    assert ev["variant_4r_kept_after_non_overlap"] == 21
    # honest verdict matches the pushed replay review verbatim
    assert ev["honest_verdict"] == (
        "edge_failed_all_variants_net_negative")
    # all variants are NET negative
    assert ev["all_variants_net_negative"] is True
    assert ev["all_variants_gross_negative"] is True
    assert ev["all_hit_rates_below_gross_breakeven"] is True
    assert ev["variant_2r_net_r_total"] == -11.08529
    assert ev["variant_3r_net_r_total"] == -10.846129
    assert ev["variant_4r_net_r_total"] == -8.340989
    # mutating the motivation rejects
    for mutation in (
            {"total_overlap_skips_across_variants": 0},
            {"total_overlap_skips_across_variants": 100},
            {"honest_verdict": "edge_confirmed"},
            {"all_variants_net_negative": False},
            {"variant_2r_net_r_total": 5.0}):
        tampered = _good_record()
        tampered["frozen_replay_evidence_for_edit"] = dict(
            tampered["frozen_replay_evidence_for_edit"], **mutation)
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, mutation
    # rationale for 24 names a structural reason (RS + structure
    # lookbacks); also asserts the chosen value
    assert _good_record()["edit_rule"][
        "min_bars_between_same_symbol_accepted_events_1h"] == 24
    rationale = _good_record()["edit_rationale_for_24_bars"]
    assert "24" in rationale
    assert "20" in rationale  # RS lookback
    assert "10" in rationale  # structure / continuation lookback


# (13) - replay / edit / rejection / paper / live behind later gates ----------

def test_13_replay_edit_rejection_paper_live_behind_later_gates():
    record = _good_record()
    # this contract does NOT authorize relabel, replay, paper, micro,
    # or live
    assert record["authorizes_relabel"] is False
    assert record["authorizes_replay"] is False
    assert record["authorizes_paper_execution"] is False
    assert record["authorizes_micro_live"] is False
    assert record["authorizes_live_trading"] is False
    # gate latches stay locked
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    # this contract does not promote or unlock anything
    assert record["promotes_gate"] is False
    assert record["unlocks_downstream_gate"] is False
    # this contract does not run the detector or replay now
    assert record["runs_real_detection_now"] is False
    assert record["runs_replay_now"] is False
    assert record["labels_now"] is False
    # the post-edit auto-rejection triggers cover every escape hatch
    triggers = record["post_edit_auto_rejection_triggers"]
    for trigger in (
            "any_variant_net_negative_after_edited_relabel_and_replay",
            "any_variant_gross_negative_after_edited_relabel_and_replay",
            "any_variant_hit_rate_below_gross_breakeven_after_edited_"
            "relabel_and_replay",
            "any_variant_kept_set_size_drops_below_minimum_"
            "evaluable_count",
            "any_artifact_hash_or_gate_mismatch_in_edited_pipeline",
            "any_attempt_to_change_an_inviolable_upstream_rule",
            "any_attempt_to_spend_a_second_edit_on_this_family"):
        assert trigger in triggers, trigger
    # autopilot loop's pushed AUTO_REJECTION_RULES still attached
    assert record["rejection_conditions"] == list(
        ap.AUTO_REJECTION_RULES)
    # claim locks
    locks = record["claim_locks"]
    for lock in (
            "edit_is_structure_filter_only_no_target_or_fee_"
            "manipulation",
            "edit_does_not_authorize_relabel",
            "edit_does_not_authorize_replay",
            "edit_does_not_authorize_paper_or_live_or_execution",
            "edit_is_not_a_rescue_attempt",
            "no_profitability_claim", "no_winner_wording",
            "automatic_rejection_if_any_post_edit_trigger_fires",
            "single_pre_committed_edit_token_spent_no_further_"
            "edits_allowed"):
        assert lock in locks, lock
    # the next required action is HUMAN-only, no banned tokens
    assert c6e.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_C6_RELABEL_WITH_EDIT_OR_CLOSE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c6e.NEXT_REQUIRED_ACTION.upper(), banned


# (14) - no trading-adjacent capability ---------------------------------------

def test_14_no_trading_adjacent_capability():
    record = _good_record()
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "authorizes_relabel", "authorizes_replay",
                "authorizes_paper_execution",
                "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    # flipping any single capability to True invalidates
    for key in ("calls_api", "uses_network", "uses_credentials",
                "connects_broker", "connects_exchange",
                "contains_order_logic",
                "modifies_staged_market_data",
                "starts_scheduler", "auto_pushes"):
        tampered = _good_record()
        tampered[key] = True
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, key


# (15) - AST/purity and module hygiene ---------------------------------------

def test_15_ast_purity_no_writers_no_runners_no_main():
    assert c6e.get_c6_single_edit_label() == c6e.C6E_LABEL
    assert "READ-ONLY" in c6e.C6E_LABEL
    assert "RESEARCH ONLY" in c6e.C6E_LABEL
    assert "STRUCTURE FILTER ONLY" in c6e.C6E_LABEL
    assert "NOT A RESCUE" in c6e.C6E_LABEL
    assert "NOT A CLAIM" in c6e.C6E_LABEL
    assert c6e.C6E_MODE == "RESEARCH_ONLY"
    assert c6e.VERDICT_C6E_READY == (
        "C6_SINGLE_EDIT_CLUSTERING_FILTER_FROZEN_READY_FOR_HUMAN_REVIEW")
    assert c6e.VERDICT_C6E_BLOCKED == (
        "C6_SINGLE_EDIT_CLUSTERING_FILTER_BLOCKED")
    src = open(c6e.__file__, encoding="utf-8").read()
    # no main entry point, no random, no wall clock, no writers, no
    # runners
    assert "__main__" not in src
    assert "random" not in src
    assert "now(" not in src
    assert "schedule" not in src.lower() or (
        "scheduler" in src.lower() and "starts_scheduler" in src)
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
    # no open() anywhere
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))


# (16) - chain gate: blocked if any upstream gate not certifying -------------

def test_16_blocked_when_any_upstream_link_breaks():
    # baseline READY
    record = _good_record()
    assert record["verdict"] == c6e.VERDICT_C6E_READY
    # simulate every blocker by re-pointing the relevant build function
    # in this module (NOT mutating shared state). We poke the local
    # module attribute to force the blocked branch.
    import sparta_commander.multi_symbol_relative_strength_rotation_filter_single_edit_clustering_filter_contract as mod
    original = {
        "build_candidate_6_family_proposal":
            mod.build_candidate_6_family_proposal,
        "build_candidate_6_spec_review": mod.build_candidate_6_spec_review,
        "build_c6_dry_run_review": mod.build_c6_dry_run_review,
        "build_c6_labels_review": mod.build_c6_labels_review,
        "build_c6_replay_results_review":
            mod.build_c6_replay_results_review,
    }
    try:
        # the dry-run review takes no args; failing it produces a
        # BLOCKED verdict with the dry-run blocker
        mod.build_c6_dry_run_review = lambda: {"verdict": "X"}
        rec = mod.build_c6_single_edit_clustering_filter(
            REPO_ROOT, tracked_paths=[])
        assert rec["verdict"] == c6e.VERDICT_C6E_BLOCKED
        assert "dry_run_review_not_certifying" in rec["blockers"]
    finally:
        for name, fn in original.items():
            setattr(mod, name, fn)
    # restored back to READY
    assert mod.build_c6_single_edit_clustering_filter(
        REPO_ROOT, tracked_paths=[])["verdict"] == c6e.VERDICT_C6E_READY


# (17) - filter rule shape: min_bars, scope, label-time, tie-breaker ----------

def test_17_filter_rule_shape_and_constants_frozen():
    record = _good_record()
    rule = record["edit_rule"]
    assert rule["applies_at"] == "label_emission_time_before_replay"
    assert rule["scope"] == "per_symbol"
    assert rule[
        "min_bars_between_same_symbol_accepted_events_1h"] == 24
    assert rule[
        "tie_breaker"] == "keep_the_earlier_event_drop_the_later_one"
    assert rule["applies_to_all_variants_uniformly"] is True
    assert rule["applies_before_replay_time_non_overlap"] is True
    assert rule["replay_time_non_overlap_unchanged"] is True
    assert rule["leaves_15m_raw_data_unchanged"] is True
    assert rule["no_intrabar_state"] is True
    assert rule["no_lookahead"] is True
    assert rule["deterministic"] is True
    assert rule["no_other_detector_change"] is True
    # mutating any of these flips the validator
    string_or_int_fields = ("applies_at", "scope",
                             "min_bars_between_same_symbol_accepted"
                             "_events_1h", "tie_breaker")
    bool_fields = ("applies_to_all_variants_uniformly",
                   "applies_before_replay_time_non_overlap",
                   "replay_time_non_overlap_unchanged",
                   "leaves_15m_raw_data_unchanged", "no_intrabar_state",
                   "no_lookahead", "deterministic",
                   "no_other_detector_change")
    # string-or-int fields: any wrong value (string or int) must reject
    for key in string_or_int_fields:
        for value in (None, "anything_else", 99999):
            tampered = _good_record()
            tampered["edit_rule"] = dict(tampered["edit_rule"], **{
                key: value})
            assert c6e.validate_c6_single_edit_clustering_filter(
                tampered)["valid"] is False, (key, value)
    # bool fields: None/False/string reject (avoid 0/1 since Python
    # aliases bool<->int and dict equality would not detect that)
    for key in bool_fields:
        for value in (None, False, "anything_else"):
            tampered = _good_record()
            tampered["edit_rule"] = dict(tampered["edit_rule"], **{
                key: value})
            assert c6e.validate_c6_single_edit_clustering_filter(
                tampered)["valid"] is False, (key, value)


# (18) - immutable scope: no new escape hatches, no claim-lock weakening -----

def test_18_immutable_scope_and_locks_cannot_be_weakened():
    rec = _good_record()
    # claim_locks tuple cannot be weakened or reordered
    weakened = copy.deepcopy(rec)
    weakened["claim_locks"] = [lock for lock in weakened["claim_locks"]
                               if lock != "no_profitability_claim"]
    assert c6e.validate_c6_single_edit_clustering_filter(
        weakened)["valid"] is False
    # post-edit auto-rejection triggers cannot be weakened
    weakened = copy.deepcopy(rec)
    weakened["post_edit_auto_rejection_triggers"] = [
        t for t in weakened["post_edit_auto_rejection_triggers"]
        if t !=
        "any_attempt_to_spend_a_second_edit_on_this_family"]
    assert c6e.validate_c6_single_edit_clustering_filter(
        weakened)["valid"] is False
    # rejection_conditions tuple cannot drift from autopilot loop
    weakened = copy.deepcopy(rec)
    weakened["rejection_conditions"] = []
    assert c6e.validate_c6_single_edit_clustering_filter(
        weakened)["valid"] is False
    # data boundary cannot be weakened
    for assumption in ("no_fetch_ever", "staged_data_never_modified"):
        tampered = _good_record()
        tampered["inviolable_rules"] = dict(
            tampered["inviolable_rules"], **{assumption: False})
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, assumption
    # verdict cannot be forged
    for fake in ("CANDIDATE_6_APPROVED", "C6_PROMOTED",
                 "EDIT_AUTHORIZED_PAPER", "READY"):
        tampered = _good_record()
        tampered["verdict"] = fake
        assert c6e.validate_c6_single_edit_clustering_filter(
            tampered)["valid"] is False, fake

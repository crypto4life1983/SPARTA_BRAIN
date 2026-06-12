"""Tests for the Candidate #5 strategy spec review contract.

Verifies: proposal + Autopilot V1 + four-record ledger certify live; all
numeric definitions exactly as frozen; no lookahead in RS/ATR/pullback/
trigger; WIDER-stop rule; 81 bps geometry floor before replay; 2R/3R/4R
only; non-overlap built in at policy time; edit limits; rejection and
promotion conditions; zero capability; no claims. Tamper tests on every
numeric. Commander safety suite runs alongside."""

from __future__ import annotations

import ast

import sparta_commander.eth_sol_relative_strength_pullback_continuation_spec_review_contract as c5s
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap


def test_spec_ready_and_gated_on_proposal_loop_and_ledger():
    import sparta_commander.eth_sol_relative_strength_pullback_continuation_family_proposal_contract as c5p
    assert c5p.build_candidate_5_family_proposal()["verdict"] == (
        c5p.VERDICT_C5P_READY)
    assert ap.build_autopilot_loop_contract()["verdict"] == (
        ap.VERDICT_AP_READY)
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
        REJECTION_STATUS as C4)
    assert C1 == C2 == C3 == C4 == "REJECTED_KEPT_ON_RECORD"
    record = c5s.build_candidate_5_spec_review()
    assert record["verdict"] == c5s.VERDICT_C5S_READY
    assert record["blockers"] == []
    assert c5s.validate_candidate_5_spec_review(record)["valid"] is True
    assert c5s.build_candidate_5_spec_review() == record  # determinism


def test_identity_frozen():
    record = c5s.build_candidate_5_spec_review()
    identity = record["identity"]
    assert identity["family_id"] == (
        "ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION_V1")
    assert identity["symbols"] == ["ETHUSD", "SOLUSD"]
    assert identity["timeframe"] == "1h"
    assert identity["direction"] == "long_only"
    assert identity["current_loop_stage"] == "candidate_spec"
    assert record["current_loop_stage"] == ap.LOOP_STAGES[0]


def test_rs_gate_numeric_and_no_lookahead():
    rs = c5s.RS_GATE
    assert rs["lookback_bars"] == 20
    assert rs["return_formula"] == (
        "return_20 = close[t] / close[t-20] - 1")
    assert rs["pass_rule_1"] == "return_20(symbol) > 0"
    assert rs["pass_rule_2"] == (
        "return_20(symbol) > return_20(other_symbol)")
    assert rs["uses_completed_1h_bars_only"] is True
    assert rs["no_future_bars"] is True
    assert rs["no_same_bar_lookahead"] is True
    assert rs[
        "required_entry_gate_not_rescue_or_post_failure_score"] is True
    tampered = c5s.build_candidate_5_spec_review()
    tampered["rs_gate"] = dict(c5s.RS_GATE, lookback_bars=10)
    check = c5s.validate_candidate_5_spec_review(tampered)
    assert check["valid"] is False
    assert "rs_gate_tampered" in check["errors"]


def test_up_leg_and_pullback_numeric():
    up_leg = c5s.UP_LEG
    assert up_leg["up_leg_size"] == "up_leg_high - up_leg_low"
    assert up_leg["up_leg_size_must_be_positive"] is True
    assert up_leg["reject_if_up_leg_size_not_positive"] is True
    pullback = c5s.PULLBACK
    assert pullback["min_bars"] == 2
    assert pullback["max_bars"] == 6
    assert pullback["bars_must_be_completed_1h"] is True
    assert pullback["must_occur_after_prior_up_leg_high"] is True
    assert pullback["valid_rule_1"] == "pullback_depth > 0"
    assert pullback["valid_rule_2_max_depth_pct_of_up_leg"] == 38.2
    assert pullback["valid_rule_3"] == "pullback_low > up_leg_low"
    assert "rescue" in pullback["purpose"]
    for mutated in (dict(pullback, max_bars=12),
                    dict(pullback, min_bars=1),
                    dict(pullback,
                         valid_rule_2_max_depth_pct_of_up_leg=61.8)):
        tampered = c5s.build_candidate_5_spec_review()
        tampered["pullback"] = mutated
        assert c5s.validate_candidate_5_spec_review(
            tampered)["valid"] is False


def test_trigger_no_lookahead():
    trigger = c5s.TRIGGER
    assert "first completed 1h close above pullback_high" in (
        trigger["rule"])
    assert "rs gate still passes" in trigger["rule"]
    assert trigger["entry_price"] == "trigger_candle_close"
    assert trigger["evaluation_starts"] == (
        "next_1h_bar_after_trigger_close")
    assert trigger["no_intrabar_trigger_entry"] is True
    assert trigger["no_future_pullback_extension_after_trigger"] is True
    tampered = c5s.build_candidate_5_spec_review()
    tampered["trigger"] = dict(
        c5s.TRIGGER, evaluation_starts="same_bar")
    assert c5s.validate_candidate_5_spec_review(
        tampered)["valid"] is False


def test_stop_logic_wider_rule_and_numerics():
    stop = c5s.STOP_LOGIC
    assert stop["atr_length"] == 14
    assert stop["atr_multiplier"] == 1.5
    assert stop[
        "atr_uses_completed_1h_bars_only_standard_true_range"] is True
    assert stop["stop_distance"] == (
        "max(atr_stop_distance, structure_stop_distance)")
    assert stop["stop_price"] == "entry_price - stop_distance"
    assert stop["stop_must_be_below_entry"] is True
    assert stop["invalid_if_stop_distance_not_positive"] is True
    assert stop[
        "wider_stop_rule_mandatory_no_tightening_to_improve_r"] is True
    for mutated in (dict(stop, atr_length=7),
                    dict(stop, atr_multiplier=1.0),
                    dict(stop, stop_distance=(
                        "min(atr_stop_distance, "
                        "structure_stop_distance)"))):
        tampered = c5s.build_candidate_5_spec_review()
        tampered["stop_logic"] = mutated
        assert c5s.validate_candidate_5_spec_review(
            tampered)["valid"] is False


def test_fee_geometry_floor_before_replay():
    fee = c5s.FEE_GEOMETRY
    assert fee["fee_model_round_trip_bps"] == 27
    assert fee["label_time_minimum_gross_target_distance_bps"] == 81
    assert fee["floor_is_3x_round_trip_fees"] is True
    assert 27 * 3 == 81
    assert fee["applies_per_target_variant_being_evaluated"] is True
    assert fee["checked_before_any_replay_is_authorized"] is True
    assert fee["no_maker_rebate_assumption"] is True
    assert fee["no_zero_fee_assumption"] is True
    assert "not eligible for replay labeling" in fee["rule"]
    for mutated in (dict(fee, fee_model_round_trip_bps=10),
                    dict(fee,
                         label_time_minimum_gross_target_distance_bps=54),
                    dict(fee,
                         checked_before_any_replay_is_authorized=False)):
        tampered = c5s.build_candidate_5_spec_review()
        tampered["fee_geometry"] = mutated
        assert c5s.validate_candidate_5_spec_review(
            tampered)["valid"] is False


def test_target_variants_2r_3r_4r_only():
    assert c5s.TARGET_VARIANTS == ("2r", "3r", "4r")
    record = c5s.build_candidate_5_spec_review()
    targets = record["target_rules"]
    assert targets["variants"] == ["2r", "3r", "4r"]
    assert targets["no_new_variants_after_label_freeze"] is True
    assert targets["target_price_formula"] == (
        "entry_price + r_multiple * stop_distance")
    tampered = c5s.build_candidate_5_spec_review()
    tampered["target_rules"] = dict(
        tampered["target_rules"], variants=["2r", "3r", "4r", "8r"])
    assert c5s.validate_candidate_5_spec_review(
        tampered)["valid"] is False


def test_non_overlap_built_in_per_variant():
    overlap = c5s.NON_OVERLAP
    assert overlap["built_in_at_label_replay_policy_time"] is True
    assert "prior kept same-symbol setup's exit under the same variant" \
        in overlap["rule"]
    assert overlap["evaluated_per_variant_because_exits_differ"] is True
    assert overlap[
        "may_only_reduce_or_keep_trade_count_never_add"] is True
    assert overlap["is_not_an_edit_or_rescue_path"] is True
    tampered = c5s.build_candidate_5_spec_review()
    tampered["non_overlap"] = dict(
        c5s.NON_OVERLAP, may_only_reduce_or_keep_trade_count_never_add=False)
    assert c5s.validate_candidate_5_spec_review(
        tampered)["valid"] is False


def test_edit_policy_limits():
    edit = c5s.EDIT_POLICY
    assert edit["maximum_pre_committed_edits"] == 1
    assert edit[
        "edit_must_be_filter_only_or_structure_only_as_pre_authorized"
    ] is True
    assert edit["edit_may_never"] == (
        "weaken_entries", "add_symbols",
        "add_trades_after_labels_are_frozen", "remove_fees",
        "loosen_no_overlap", "change_target_variants")
    assert edit["edit_requires_separate_human_approval"] is True
    for field, value in (
            ("edit_policy", {"maximum_pre_committed_edits": 2,
                             "edit_may_never": [],
                             "edit_requires_separate_human_approval":
                                 True}),):
        tampered = c5s.build_candidate_5_spec_review()
        tampered[field] = value
        assert c5s.validate_candidate_5_spec_review(
            tampered)["valid"] is False, field


def test_rejection_and_promotion_conditions():
    record = c5s.build_candidate_5_spec_review()
    assert record["rejection_conditions"] == list(
        ap.AUTO_REJECTION_RULES)
    promo = record["promotion_conditions"]
    assert "fee_honest_net_positive_after_replay" in promo
    assert "gross_positive_before_fees" in promo
    assert "hit_rate_above_breakeven" in promo
    assert "non_overlap_adjusted_result_remains_acceptable" in promo
    assert "sample_size_not_near_zero" in promo
    assert "no_concentration_only_result" in promo
    assert any("no_profitability_claim" in item for item in promo)
    for field in ("rejection_conditions", "promotion_conditions",
                  "safety_no_claim"):
        tampered = c5s.build_candidate_5_spec_review()
        tampered[field] = []
        assert c5s.validate_candidate_5_spec_review(
            tampered)["valid"] is False, field


def test_safety_no_claim_and_zero_capability():
    safety = c5s.SAFETY_NO_CLAIM
    for item in ("no_trading", "no_paper_trading", "no_live_trading",
                 "no_wallet_account_api_order_capability",
                 "no_auto_push", "no_auto_commit",
                 "no_profitability_or_winner_claim",
                 "no_paper_or_live_approval_from_this_spec"):
        assert item in safety, item
    record = c5s.build_candidate_5_spec_review()
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    for field, value in (("claims_profitability", True),
                         ("auto_pushes", True),
                         ("modifies_staged_market_data", True),
                         ("live_gate_locked", False)):
        tampered = c5s.build_candidate_5_spec_review()
        tampered[field] = value
        assert c5s.validate_candidate_5_spec_review(
            tampered)["valid"] is False, field


def test_verdict_string_next_stage_and_module_purity():
    assert c5s.VERDICT_C5S_READY == "CANDIDATE_5_SPEC_REVIEW_READY"
    tampered = c5s.build_candidate_5_spec_review()
    tampered["verdict"] = "CANDIDATE_5_APPROVED_FOR_TRADING"
    assert c5s.validate_candidate_5_spec_review(
        tampered)["valid"] is False
    record = c5s.build_candidate_5_spec_review()
    assert record["next_loop_stage"] == "detector_and_label_review"
    assert record["next_loop_stage"] == ap.LOOP_STAGES[1]
    assert c5s.NEXT_REQUIRED_ACTION == (
        "HUMAN_APPROVED_CANDIDATE_5_DETECTOR_SPEC_AND_DRY_RUN_PATH")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in c5s.NEXT_REQUIRED_ACTION.upper(), banned
    assert c5s.get_candidate_5_spec_review_label() == c5s.C5S_LABEL
    assert "READ-ONLY" in c5s.C5S_LABEL
    assert c5s.C5S_MODE == "RESEARCH_ONLY"
    src = open(c5s.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "pathlib", "os", "io", "json", "shutil", "databento",
                   "ssl", "ftplib", "datetime", "hashlib", "statistics"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))

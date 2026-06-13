"""Tests for the formal Candidate #6 rejection record (sixth ledger
entry).

Covers all 19 commanded requirements: REJECTED_KEPT_ON_RECORD status;
EDIT_SPENT_AND_STILL_NEGATIVE_EDGE_FAILURE reason; exact original and
edited net/gross R values; hit-rate-vs-breakeven facts; verdict
strings; spent-edit invariants; clustering reduction `334 → 37`;
labels `135 → 36` and removed = 99; auto-rejection triggers
satisfied; full pushed C6 evidence chain live; prior five-record
ledger unchanged; ledger now six records; tamper failure on any
frozen-fact change; no paper/live/profit wording; no trading-adjacent
capability; AST/purity. Commander safety suite runs alongside (12
tests)."""

from __future__ import annotations

import ast

import sparta_commander.multi_symbol_relative_strength_rotation_filter_edited_real_candle_labels_review_contract as c6el
import sparta_commander.multi_symbol_relative_strength_rotation_filter_edited_replay_results_review_contract as c6eer
import sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract as rj6
import sparta_commander.multi_symbol_relative_strength_rotation_filter_replay_results_review_contract as c6rr
import sparta_commander.multi_symbol_relative_strength_rotation_filter_single_edit_clustering_filter_contract as c6e
import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as ap

REPO_ROOT = "C:/SPARTA_BRAIN"


def _record():
    return rj6.build_c6_rejection_record(REPO_ROOT, tracked_paths=[])


# (1) status = REJECTED_KEPT_ON_RECORD ---------------------------------------

def test_1_rejection_status_is_rejected_kept_on_record():
    assert rj6.REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    record = _record()
    assert record["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert record["verdict"] == rj6.VERDICT_RJ6_RECORDED
    assert record["blockers"] == []
    assert rj6.validate_c6_rejection_record(record)["valid"] is True


# (2) reason = EDIT_SPENT_AND_STILL_NEGATIVE_EDGE_FAILURE -------------------

def test_2_rejection_reason_is_edit_spent_and_still_negative_edge_failure():
    assert rj6.REJECTION_REASON == (
        "EDIT_SPENT_AND_STILL_NEGATIVE_EDGE_FAILURE")
    record = _record()
    assert record["rejection_reason"] == (
        "EDIT_SPENT_AND_STILL_NEGATIVE_EDGE_FAILURE")
    assert rj6.VERDICT_RJ6_RECORDED == (
        "C6_REJECTED_KEPT_ON_RECORD_EDIT_SPENT_AND_STILL_NEGATIVE_EDGE"
        "_FAILURE")


# (3) original net R values exactly -----------------------------------------

def test_3_original_net_r_values_exact():
    record = _record()
    orig = record["expected_original_replay"]["variants"]
    assert orig["2r"]["net_r"] == -11.085290
    assert orig["3r"]["net_r"] == -10.846129
    assert orig["4r"]["net_r"] == -8.340989
    # they mirror the pushed original-replay-review exactly
    assert orig["2r"]["net_r"] == c6rr.EXPECTED_VARIANTS["2r"][
        "net_r_total"]
    assert orig["3r"]["net_r"] == c6rr.EXPECTED_VARIANTS["3r"][
        "net_r_total"]
    assert orig["4r"]["net_r"] == c6rr.EXPECTED_VARIANTS["4r"][
        "net_r_total"]
    for name in ("2r", "3r", "4r"):
        assert orig[name]["net_r"] < 0, name


# (4) edited net R values exactly -------------------------------------------

def test_4_edited_net_r_values_exact():
    record = _record()
    ed = record["expected_edited_replay"]["variants"]
    assert ed["2r"]["net_r"] == -12.897835
    assert ed["3r"]["net_r"] == -14.793291
    assert ed["4r"]["net_r"] == -14.464742
    # they mirror the pushed edited-replay-review exactly
    assert ed["2r"]["net_r"] == c6eer.EXPECTED_VARIANTS["2r"][
        "net_r_total"]
    assert ed["3r"]["net_r"] == c6eer.EXPECTED_VARIANTS["3r"][
        "net_r_total"]
    assert ed["4r"]["net_r"] == c6eer.EXPECTED_VARIANTS["4r"][
        "net_r_total"]
    for name in ("2r", "3r", "4r"):
        assert ed[name]["net_r"] < 0, name


# (5) edited gross R values exactly -----------------------------------------

def test_5_edited_gross_r_values_exact():
    record = _record()
    ed = record["expected_edited_replay"]["variants"]
    assert ed["2r"]["gross_r"] == -8.666284
    assert ed["3r"]["gross_r"] == -10.666284
    assert ed["4r"]["gross_r"] == -10.666284
    for name in ("2r", "3r", "4r"):
        assert ed[name]["gross_r"] < 0, name


# (6) edited hit rates and breakeven comparisons exactly ------------------

def test_6_edited_hit_rates_and_breakeven_comparisons():
    record = _record()
    ed = record["expected_edited_replay"]["variants"]
    assert ed["2r"]["hit_rate_pct"] == 20.0
    assert ed["3r"]["hit_rate_pct"] == 12.5
    assert ed["4r"]["hit_rate_pct"] == 9.1
    assert ed["2r"]["gross_breakeven_rate_pct"] == 33.3
    assert ed["3r"]["gross_breakeven_rate_pct"] == 25.0
    assert ed["4r"]["gross_breakeven_rate_pct"] == 20.0
    for name in ("2r", "3r", "4r"):
        assert ed[name]["hit_rate_pct"] < ed[name][
            "gross_breakeven_rate_pct"], name


# (7) original verdict = edge_failed_all_variants_net_negative -------------

def test_7_original_verdict_exact():
    record = _record()
    assert record["expected_original_replay"]["verdict"] == (
        "edge_failed_all_variants_net_negative")
    assert record["expected_original_replay"][
        "verdict"] == c6rr.HONEST_VERDICT


# (8) edited verdict = edited_edge_failed ---------------------------------

def test_8_edited_verdict_exact():
    record = _record()
    assert record["expected_edited_replay"]["verdict"] == (
        "edited_edge_failed")
    assert record["expected_edited_replay"][
        "verdict"] == c6eer.HONEST_VERDICT


# (9) edit token was spent and zero edits remain --------------------------

def test_9_edit_token_spent_and_zero_remaining():
    record = _record()
    ed = record["expected_edit"]
    assert ed["edit_token_used"] == 1
    assert ed["edits_remaining_after_this"] == 0
    assert ed["edit_kind"] == (
        "label_time_same_symbol_minimum_bar_gap_clustering_filter")
    assert ed["min_bars_between_same_symbol_accepted_events_1h"] == 24
    assert record["edit_allowance_spent"] is True
    assert record["candidate_6_may_receive_another_edit"] is False
    # the pushed single-edit contract still asserts the same numbers
    assert c6e.EDIT_TOKEN_USED == 1
    assert c6e.EDITS_REMAINING_AFTER_THIS == 0


# (10) clustering edit reduced overlap skips 334 → 37 ---------------------

def test_10_clustering_reduced_overlap_skips_334_to_37():
    record = _record()
    ed = record["expected_edit"]
    assert ed["original_overlap_skipped_total"] == 334
    assert ed["edited_overlap_skipped_total"] == 37
    # both numbers mirror the pushed review contracts
    assert ed["original_overlap_skipped_total"] == (
        c6rr.EXPECTED_OVERLAP_SKIPPED_TOTAL)
    assert ed["edited_overlap_skipped_total"] == (
        c6eer.EXPECTED_OVERLAP_SKIPPED_TOTAL)
    assert ed["edit_worked_structurally_but_did_not_rescue_edge"] is (
        True)


# (11) edited labels 135 → 36 and removed = 99 ---------------------------

def test_11_edited_labels_135_to_36_removed_99():
    record = _record()
    ed = record["expected_edit"]
    assert ed["original_accepted_labels"] == 135
    assert ed["edited_accepted_labels"] == 36
    assert ed["removed_by_clustering"] == 99
    assert (ed["original_accepted_labels"]
            - ed["edited_accepted_labels"]
            == ed["removed_by_clustering"])
    # per-symbol counts mirror the pushed edited-labels review
    assert ed["per_symbol_edited"] == {
        sym: dict(v) for sym, v
        in c6el.EXPECTED_PER_SYMBOL_EDITED.items()}


# (12) auto-rejection triggers are all satisfied -------------------------

def test_12_auto_rejection_triggers_all_satisfied():
    record = _record()
    triggers = record["auto_rejection_triggers_satisfied"]
    assert triggers["any_variant_net_negative"] is True
    assert triggers["any_variant_gross_negative"] is True
    assert triggers["any_variant_hit_rate_below_gross_breakeven"] is True
    assert triggers["filter_or_edit_spent_and_still_negative"] is True
    assert triggers["gross_negative_and_net_negative_after_replay"] is (
        True)
    assert triggers["below_breakeven_hit_rate"] is True
    # mirror the pushed-loop's AUTO_REJECTION_RULES tuple
    for trigger in (
            "gross_negative_and_net_negative_after_replay",
            "below_breakeven_hit_rate",
            "filter_or_edit_spent_and_still_negative"):
        assert trigger in ap.AUTO_REJECTION_RULES, trigger


# (13) full pushed C6 evidence chain certifies live ----------------------

def test_13_full_pushed_chain_certifies_live():
    # build_c6_rejection_record only returns RJ6_RECORDED if the full
    # chain certifies; assert the verdict and the named pushed chain
    record = _record()
    assert record["verdict"] == rj6.VERDICT_RJ6_RECORDED
    assert record["blockers"] == []
    assert tuple(record["pushed_evidence_chain"]) == (
        rj6.PUSHED_EVIDENCE_CHAIN)
    # the 11 named upstream contracts must all be reachable
    expected_chain = (
        "multi_symbol_relative_strength_rotation_filter_family_proposal",
        "multi_symbol_relative_strength_rotation_filter_spec_review",
        "multi_symbol_relative_strength_rotation_filter_detector_spec",
        "multi_symbol_relative_strength_rotation_filter_dry_run_review",
        "multi_symbol_relative_strength_rotation_filter_real_candle"
        "_labels_review",
        "multi_symbol_relative_strength_rotation_filter_replay_results"
        "_review",
        "multi_symbol_relative_strength_rotation_filter_single_edit"
        "_clustering_filter",
        "multi_symbol_relative_strength_rotation_filter_edited_real"
        "_candle_labels_review",
        "multi_symbol_relative_strength_rotation_filter_edited_replay"
        "_results_review",
        "strategy_factory_candidate_recommendation_v1",
        "strategy_factory_autopilot_research_loop_v1")
    assert tuple(record["pushed_evidence_chain"]) == expected_chain


# (14) prior five rejected records remain unchanged ---------------------

def test_14_prior_five_rejected_records_unchanged():
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C3)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C2)
    from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C5)
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C1)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (  # noqa: E501
        REJECTION_STATUS as C4)
    for status in (C1, C2, C3, C4, C5):
        assert status == "REJECTED_KEPT_ON_RECORD"
    record = _record()
    assert record["prior_five_records_unchanged"] is True


# (15) ledger now contains six rejected records -------------------------

def test_15_ledger_now_contains_six_rejected_records():
    # the C6 rejection record exports REJECTION_STATUS the same way as
    # C1-C5; the sixth ledger entry is now visible to any future C7+
    # contract that imports it
    assert rj6.REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    record = _record()
    assert record["ledger_position"] == 6
    assert record["ledger_now_contains_six_records"] is True
    # enumerate all six rejection record modules to prove they each
    # export REJECTION_STATUS = REJECTED_KEPT_ON_RECORD
    ledger_modules = (
        "sparta_commander.ny_session_fvg_choch_v3_result_and_candidate"
        "_rejection_record_contract",
        "sparta_commander.crypto_intraday_breakout_pullback_structure_v2"
        "_result_and_rejection_record_contract",
        "sparta_commander.btc_sol_long_trend_continuation_v1_result_and"
        "_rejection_record_contract",
        "sparta_commander.sol_btc_long_1h_swing_structure_rejection"
        "_record_contract",
        "sparta_commander.eth_sol_relative_strength_rejection_record"
        "_contract",
        "sparta_commander.multi_symbol_relative_strength_rotation_filter"
        "_rejection_record_contract")
    statuses = []
    for module_path in ledger_modules:
        mod = __import__(module_path, fromlist=["REJECTION_STATUS"])
        statuses.append(mod.REJECTION_STATUS)
    assert len(statuses) == 6
    assert all(s == "REJECTED_KEPT_ON_RECORD" for s in statuses)


# (16) rejection record fails on any frozen-fact change ----------------

def test_16_rejection_record_fails_on_any_frozen_fact_change():
    for field, value in (
            ("rejection_status", "APPROVED"),
            ("rejection_reason", "PROFITABLE"),
            ("edit_classification", "tampered"),
            ("replay_review_classification", "tampered"),
            ("head_at_edited_replay_review", "00" * 20),
            ("ledger_position", 5),
            ("expected_original_replay", {}),
            ("expected_edit", {}),
            ("expected_edited_replay", {}),
            ("auto_rejection_triggers_satisfied", {}),
            ("rejection_facts", []),
            ("evidence_notes", []),
            ("seeds_for_future_families_only", []),
            ("seeds_are_never_rescue_paths", False),
            ("pushed_evidence_chain", []),
            ("edit_allowance_spent", False),
            ("candidate_6_may_continue_as_is", True),
            ("candidate_6_may_receive_another_edit", True),
            ("further_replays_authorized", True),
            ("ledger_now_contains_six_records", False),
            ("prior_five_records_unchanged", False),
            ("authorizes_paper_execution", True),
            ("authorizes_live_trading", True),
            ("claims_profitability", True),
            ("live_gate_locked", False),
            ("verdict", "C6_APPROVED_FOR_TRADING")):
        tampered = _record()
        tampered[field] = value
        assert rj6.validate_c6_rejection_record(
            tampered)["valid"] is False, field


# (17) no paper/live/profit/winner wording ----------------------------

def test_17_no_paper_live_profit_or_winner_wording():
    record = _record()
    assert record["authorizes_paper_execution"] is False
    assert record["authorizes_micro_live"] is False
    assert record["authorizes_live_trading"] is False
    assert record["claims_profitability"] is False
    assert record["paper_trading_gate_locked"] is True
    assert record["micro_live_gate_locked"] is True
    assert record["live_gate_locked"] is True
    facts = record["rejection_facts"]
    for fact in ("no paper approval", "no live approval",
                 "no profitability claim permitted",
                 "no winner wording permitted"):
        assert fact in facts, fact
    # the label must include the read-only / not-a-profitability-claim
    # framing and must not include any banned wording
    label = rj6.RJ6_LABEL
    assert "READ-ONLY" in label
    assert "REJECTED KEPT ON RECORD" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    for banned_phrase in ("WINNER", "PROFITABLE", "EDGE CONFIRMED",
                          "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned_phrase not in label.upper(), banned_phrase


# (18) no trading-adjacent capability ----------------------------------

def test_18_no_trading_adjacent_capability():
    record = _record()
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "auto_commits", "auto_pushes",
                "creates_runners_now", "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        assert record[key] is False, key


# (19) AST / purity ----------------------------------------------------

def test_19_ast_purity_and_no_writers_or_runners():
    assert rj6.get_c6_rejection_record_label() == rj6.RJ6_LABEL
    assert rj6.RJ6_MODE == "RESEARCH_ONLY"
    assert rj6.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rj6.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(rj6.__file__, encoding="utf-8").read()
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


# determinism check (bonus) ------------------------------------------

def test_determinism():
    a = _record()
    b = _record()
    assert a == b

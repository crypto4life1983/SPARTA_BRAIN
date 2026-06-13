"""Tests for the Candidate #5 formal rejection record.

Verifies: replay review certifies live; edit + baseline artifact shas;
baseline-vs-edit counts; zero new accepted ids; original 6 byte-identical;
the edit changed only pullback max 6->10; edit allowance spent; replay
unchanged and all variants net-negative; rejection verdict string; no
paper/live/trading/claims; untracked runner/artifacts; future-family-only
seeds; permanence locks. Tamper tests on every frozen block. Commander
safety suite runs alongside."""

from __future__ import annotations

import ast
import copy

import pytest

import sparta_commander.eth_sol_relative_strength_rejection_record_contract as rj5

REPO_ROOT = "C:/SPARTA_BRAIN"


def _good_observation():
    return {
        "edit_artifacts_exist": True,
        "edit_labels_sha256": rj5.EXPECTED_EDIT_LABELS_SHA256,
        "edit_replay_sha256": rj5.EXPECTED_EDIT_REPLAY_SHA256,
        "edit_summary_sha256": rj5.EXPECTED_EDIT_SUMMARY_SHA256,
        "baseline_labels_sha_ok": True,
        "baseline_replay_sha_ok": True,
        "baseline_vs_edit": {
            key: value for key, value
            in rj5.EXPECTED_BASELINE_VS_EDIT.items()},
        "failure_statuses_present": True,
        "edit_replay_variants": copy.deepcopy(
            rj5.EXPECTED_EDIT_REPLAY_VARIANTS),
        "removed_setup_ids": {
            "2r": (rj5.EXPECTED_REMOVED_SETUP_ID,),
            "3r": (rj5.EXPECTED_REMOVED_SETUP_ID,),
            "4r": (rj5.EXPECTED_REMOVED_SETUP_ID,)},
        "edit_classification":
            "C5_EDIT_V1_TRIGGER_WINDOW_FAILED_REJECT_NEXT",
        "original_6_byte_identical": True,
        "artifacts_tracked_in_git": [],
    }


def test_certify_passes_on_expected_observation():
    result = rj5.certify_c5_rejection(_good_observation())
    assert result["certified"] is True
    assert result["failures"] == []


def test_certify_failure_modes():
    cases = (
        ({"edit_artifacts_exist": False}, "edit_artifacts_missing"),
        ({"edit_labels_sha256": "00" * 32}, "edit_labels_sha_mismatch"),
        ({"edit_replay_sha256": "00" * 32}, "edit_replay_sha_mismatch"),
        ({"edit_summary_sha256": "00" * 32},
         "edit_summary_sha_mismatch"),
        ({"baseline_labels_sha_ok": False},
         "baseline_labels_sha_changed"),
        ({"baseline_replay_sha_ok": False},
         "baseline_replay_sha_changed"),
        ({"edit_classification": "C5_EDIT_V1_POSITIVE"},
         "edit_classification_mismatch"),
        ({"original_6_byte_identical": False},
         "original_6_not_byte_identical"),
        ({"failure_statuses_present": False},
         "failure_explanation_statuses_missing"),
        ({"artifacts_tracked_in_git": [rj5.EDIT_RUNNER_PATH]},
         "runner_and_artifacts_must_stay_untracked"),
    )
    for override, expected_failure in cases:
        observation = _good_observation()
        observation.update(override)
        result = rj5.certify_c5_rejection(observation)
        assert result["certified"] is False, expected_failure
        assert expected_failure in result["failures"], expected_failure
    # baseline-vs-edit tampers: counts, new ids, too_long counts
    for key, value, expected in (
            ("baseline_accepted", 7,
             "baseline_vs_edit_mismatch:baseline_accepted"),
            ("edit_accepted", 8,
             "baseline_vs_edit_mismatch:edit_accepted"),
            ("new_accepted_ids", ("X",),
             "baseline_vs_edit_mismatch:new_accepted_ids"),
            ("baseline_pullback_too_long", 100,
             "baseline_vs_edit_mismatch:baseline_pullback_too_long"),
            ("edit_pullback_too_long", 100,
             "baseline_vs_edit_mismatch:edit_pullback_too_long")):
        observation = _good_observation()
        observation["baseline_vs_edit"][key] = value
        result = rj5.certify_c5_rejection(observation)
        assert expected in result["failures"], expected
    # replay tampers: net R per variant
    for variant in ("2r", "3r", "4r"):
        observation = _good_observation()
        observation["edit_replay_variants"][variant]["net_r"] = 0.5
        result = rj5.certify_c5_rejection(observation)
        assert ("edit_replay_mismatch:%s:net_r" % variant
                in result["failures"])
        assert ("edit_replay_not_net_negative:" + variant
                in result["failures"])
    bad_removed = _good_observation()
    bad_removed["removed_setup_ids"]["2r"] = ()
    assert "removed_setup_mismatch:2r" in rj5.certify_c5_rejection(
        bad_removed)["failures"]
    assert rj5.certify_c5_rejection(None)["certified"] is False


def test_frozen_baseline_vs_edit_table():
    bve = rj5.EXPECTED_BASELINE_VS_EDIT
    assert bve["baseline_attempts"] == 411
    assert bve["edit_attempts"] == 406
    assert bve["baseline_accepted"] == 6
    assert bve["edit_accepted"] == 6
    assert bve["edit_accepted_set_identical_to_baseline"] is True
    assert bve["new_accepted_ids"] == ()
    assert bve["original_6_still_accepted_byte_identical"] is True
    assert bve["baseline_pullback_too_long"] == 372
    assert bve["edit_pullback_too_long"] == 365
    assert bve[
        "too_long_rejections_converted_by_window_extension"] == 7
    assert bve["converted_rejections_became_accepted"] == 0
    assert 372 - 365 == 7  # internal consistency
    explanation = rj5.FROZEN_FAILURE_EXPLANATION
    assert any("did not close above the pullback high" in fact
               for fact in explanation)
    assert any("rs_not_stronger" in fact for fact in explanation)
    assert any("below_up_leg_low" in fact for fact in explanation)
    assert any("structures simply do not resume" in fact
               for fact in explanation)


def test_frozen_edit_facts_one_parameter_only():
    facts = rj5.FROZEN_EDIT_FACTS
    assert any("structure-only trigger-window extension" in fact
               for fact in facts)
    assert any("single authorized edit allowance was spent" in fact
               for fact in facts)
    assert any("exactly one parameter: pullback_max_bars 6 to 10"
               in fact for fact in facts)
    assert any("pullback minimum stayed 2" in fact for fact in facts)
    assert any("rs gate unchanged" in fact
               and "fee floor unchanged" in fact
               and "wider-stop rule unchanged" in fact
               for fact in facts)
    assert any("restored to 6 after run" in fact for fact in facts)
    assert any("attempts 411, accepted 6, pullback_too_long 372"
               in fact for fact in facts)


def test_frozen_edit_replay_unchanged_and_net_negative():
    variants = rj5.EXPECTED_EDIT_REPLAY_VARIANTS
    assert variants["2r"] == {
        "kept": 5, "removed": 1, "hits": 2, "stops": 3, "timeouts": 0,
        "gross_r": 1.000001, "net_r": -0.269641}
    assert variants["3r"]["net_r"] == -2.269641
    assert variants["4r"]["net_r"] == -1.269641
    for name, row in variants.items():
        assert row["net_r"] < 0, name
        assert row["kept"] == 5 and row["removed"] == 1, name
        assert row["hits"] + row["stops"] + row["timeouts"] == 5, name
    assert rj5.EXPECTED_REMOVED_SETUP_ID == (
        "SOLUSD_2026-05-06T06:00:00Z")
    facts = rj5.FROZEN_EDIT_REPLAY_FACTS
    assert any("identical to the frozen baseline replay" in fact
               for fact in facts)
    assert any("-3.861515r" in fact for fact in facts)
    assert any("concentrated in one week" in fact for fact in facts)
    # cross-check against the pushed baseline replay review constants
    import sparta_commander.eth_sol_relative_strength_replay_results_review_contract as c5rr
    for name in ("2r", "3r", "4r"):
        assert variants[name]["net_r"] == (
            c5rr.EXPECTED_VARIANTS[name]["net_r"])
        assert variants[name]["gross_r"] == (
            c5rr.EXPECTED_VARIANTS[name]["gross_r"])


def test_rejection_constants_facts_and_evidence_notes():
    assert rj5.REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    assert rj5.REJECTION_REASON == (
        "SMALL_SAMPLE_NET_NEGATIVE_AND_EDIT_ADDED_NOTHING")
    assert rj5.EDIT_CLASSIFICATION == (
        "C5_EDIT_V1_TRIGGER_WINDOW_FAILED_REJECT_NEXT")
    assert rj5.VERDICT_RJ5_RECORDED == (
        "C5_REJECTED_KEPT_ON_RECORD_SMALL_SAMPLE_NET_NEGATIVE_AND"
        "_EDIT_ADDED_NOTHING")
    facts = rj5.REJECTION_FACTS
    assert "candidate #5 is rejected" in facts
    assert "rejection is kept on record" in facts
    assert any("zero new accepted setups" in fact for fact in facts)
    assert "the edit allowance is now spent" in facts
    assert "candidate #5 may not continue as-is" in facts
    assert "candidate #5 may not receive another edit" in facts
    assert "further replays are not authorized" in facts
    assert "no paper approval" in facts
    assert "no live approval" in facts
    assert "no profitability claim permitted" in facts
    assert "no winner wording permitted" in facts
    notes = rj5.EVIDENCE_NOTES
    assert any("first family to show gross-positive 2r" in note
               for note in notes)
    assert any("fees turned 2r negative" in note for note in notes)
    assert any("4r was gross-flat" in note for note in notes)
    assert any("eth contributed only losses" in note for note in notes)
    assert any("too small and too concentrated" in note
               for note in notes)
    assert any("dedup removed a winner" in note for note in notes)
    assert any("did not solve scarcity" in note for note in notes)


def test_seeds_future_family_only():
    seeds = rj5.SEEDS_FOR_FUTURE_FAMILIES_ONLY
    assert len(seeds) == 7
    assert any("inspire_new_hypotheses_only" in seed for seed in seeds)
    assert any("filtered_earlier" in seed for seed in seeds)
    assert any("structural_lesson" in seed for seed in seeds)
    assert any("can_remove_winners" in seed for seed in seeds)
    assert any("not_edge_evidence" in seed for seed in seeds)
    assert "do_not_reuse_c5_as_is" in seeds
    assert any("new_clean_hypothesis_through_the_autopilot_loop"
               in seed for seed in seeds)
    assert rj5.SEEDS_ARE_NEVER_RESCUE_PATHS is True


def test_real_artifacts_certify_when_present():
    import pathlib
    if not (pathlib.Path(REPO_ROOT) / rj5.EDIT_SUMMARY_PATH).is_file():
        pytest.skip("candidate #5 edit artifacts not present")
    record = rj5.build_c5_rejection_record(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] == rj5.VERDICT_RJ5_RECORDED
    assert record["failures"] == []
    assert rj5.validate_c5_rejection_record(record)["valid"] is True


def test_record_tampering_invalidates():
    record = rj5.build_c5_rejection_record(REPO_ROOT, tracked_paths=[])
    for field, value in (
            ("rejection_status", "ACCEPTED"),
            ("rejection_reason", "NONE"),
            ("edit_classification", "C5_EDIT_V1_POSITIVE"),
            ("expected_edit_labels_sha256", "00" * 32),
            ("expected_edit_replay_sha256", "00" * 32),
            ("expected_edit_summary_sha256", "00" * 32),
            ("baseline_labels_sha256", "00" * 32),
            ("baseline_replay_sha256", "00" * 32),
            ("expected_baseline_vs_edit", {}),
            ("frozen_edit_facts", []),
            ("frozen_failure_explanation", []),
            ("expected_edit_replay_variants", {}),
            ("expected_removed_setup_id", "NONE"),
            ("rejection_facts", []),
            ("evidence_notes", []),
            ("seeds_for_future_families_only", []),
            ("seeds_are_never_rescue_paths", False),
            ("edit_allowance_spent", False),
            ("candidate_5_may_continue_as_is", True),
            ("candidate_5_may_receive_another_edit", True),
            ("further_replays_authorized", True),
            ("claims_profitability", True),
            ("authorizes_paper_execution", True),
            ("authorizes_live_trading", True),
            ("live_gate_locked", False),
            ("verdict", "C5_APPROVED")):
        tampered = rj5.build_c5_rejection_record(REPO_ROOT,
                                                 tracked_paths=[])
        tampered[field] = value
        assert rj5.validate_c5_rejection_record(
            tampered)["valid"] is False, field
    recorded_with_failures = rj5.build_c5_rejection_record(
        REPO_ROOT, tracked_paths=[])
    recorded_with_failures["failures"] = ["fake"]
    assert rj5.validate_c5_rejection_record(
        recorded_with_failures)["valid"] is False


def test_chain_gate_and_capabilities():
    import sparta_commander.eth_sol_relative_strength_replay_results_review_contract as c5rr
    review = c5rr.build_c5_replay_results_review(REPO_ROOT,
                                                 tracked_paths=[])
    assert review["verdict"] == (
        "C5_REPLAY_RESULTS_REVIEW_INFORMATION_ONLY_FROZEN")
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_STATUS as C1)
    from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
        REJECTION_STATUS as C2)
    from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
        REJECTION_STATUS as C3)
    from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
        REJECTION_STATUS as C4)
    assert C1 == C2 == C3 == C4 == "REJECTED_KEPT_ON_RECORD"
    record = rj5.build_c5_rejection_record(REPO_ROOT, tracked_paths=[])
    assert record["verdict"] != rj5.VERDICT_RJ5_BLOCKED
    assert record["edit_allowance_spent"] is True
    assert record["candidate_5_may_continue_as_is"] is False
    assert record["candidate_5_may_receive_another_edit"] is False
    assert record["further_replays_authorized"] is False
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


def test_label_action_and_module_purity():
    assert rj5.get_c5_rejection_record_label() == rj5.RJ5_LABEL
    assert "READ-ONLY" in rj5.RJ5_LABEL
    assert "REJECTED KEPT ON RECORD" in rj5.RJ5_LABEL
    assert "NOT A PROFITABILITY CLAIM" in rj5.RJ5_LABEL
    assert rj5.RJ5_MODE == "RESEARCH_ONLY"
    assert rj5.NEXT_REQUIRED_ACTION == (
        "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY")
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rj5.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(rj5.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt",
                   "smtplib", "subprocess", "websockets", "aiohttp",
                   "schedule", "apscheduler", "threading", "asyncio",
                   "time", "sched", "telegram", "email", "csv", "pandas",
                   "os", "io", "shutil", "databento", "ssl", "ftplib",
                   "datetime", "statistics", "random"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(
        call.func.attr == "open" if isinstance(call.func, ast.Attribute)
        else getattr(call.func, "id", "") == "open"
        for call in ast.walk(tree) if isinstance(call, ast.Call))

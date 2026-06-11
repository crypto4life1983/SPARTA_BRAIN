"""Tests for the SPARTA NY FVG+CHOCH Fee-Honest Replay Results Review.

Proves the evidence freeze: NET -21.04R at 27 bps round-trip costs over
exactly the 7 frozen setup_ids -- and that any tampering (net R, costs,
scope, profitability claims, paper/live claims, prior-output mutation)
REJECTS. The candidate is not approved for paper/live, ever, here.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.ny_session_fvg_choch_fee_honest_replay_results_review_contract as rr


def _result(setup_id, status, exit_reason, gross_r, net_r):
    symbol = setup_id.split("_")[0]
    date = setup_id.split("_")[1]
    record = {
        "setup_id": setup_id, "symbol": symbol,
        "session_date": "%s-%s-%s" % (date[:4], date[4:6], date[6:8]),
        "replay_status": status, "exit_reason": exit_reason,
        "gross_r": gross_r, "net_r_after_costs": net_r,
        "rejection_reason": (None if status
                             == "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW"
                             else "entry_level_never_traded_in_window"),
        "cost_assumptions_bps": {"fees_bps": 20.0, "spread_bps": 2.0,
                                 "slippage_bps": 5.0},
        "replay_window": {"start": "x", "end": "y",
                          "anti_lookahead_minutes": 3},
        "runner_authorizes_nothing": True,
    }
    return record


def _results():
    return [_result(sid, *row) for sid, row in
            sorted(rr.EXPECTED_PER_LABEL.items())]


def _summary(**overrides):
    summary = {
        "replay_scope": sorted(rr.EXPECTED_PER_LABEL),
        "labels_replayed": 7,
        "cost_assumptions_bps": {"fees_bps": 20.0, "spread_bps": 2.0,
                                 "slippage_bps": 5.0},
        "anti_lookahead_minutes": 3,
        "completed_replays": 6, "no_entry_rejections": 1,
        "total_net_r_after_costs": -21.040902,
        "wins_net_positive": 1, "losses_net_negative": 5,
        "honesty_note": ("research replay on a 7-setup sample; net figures "
                         "include 27 bps round-trip costs; NO profitability "
                         "claim is made or permitted from a sample this "
                         "small; no trade signal; human review required"),
        "replay_authorizes_nothing": True,
        "no_orders_no_credentials_no_paper_no_live": True,
    }
    summary.update(overrides)
    return summary


def _observation(**overrides):
    observation = {
        "results_present": True, "summary_present": True,
        "results": overrides.pop("results", None) or _results(),
        "summary": overrides.pop("summary", None) or _summary(),
        "results_sha256": rr.EXPECTED_RESULTS_SHA256,
        "summary_sha256": rr.EXPECTED_SUMMARY_SHA256,
        "accepted_labels_review_verdict":
            "ACCEPTED_LABELS_HUMAN_REVIEW_APPROVED_FOR_REPLAY_DECISION",
        "tracked_output_paths": [],
        "baseline_files_sha256": dict(rr.BASELINE_PROTECTED_FILES),
        "batch2_manifest_sha256": rr.BATCH2_MANIFEST_SHA256,
        "expanded_labels_sha256": rr.EXPANDED_LABELS_SHA256,
    }
    observation.update(overrides)
    return observation


def test_valid_replay_evidence_accepts():
    review = rr.certify_replay_results(_observation())
    assert review["verdict"] == rr.VERDICT_RR_ACCEPTED
    assert review["blockers"] == []
    assert review["total_net_r_after_costs"] == -21.040902
    assert review["candidate_approved_for_paper_or_live"] is False
    assert review["profitability_claim_permitted"] is False
    assert all(review["checklist_results"][n] is True
               for n in rr.REVIEW_CHECKLIST)
    assert len(rr.REVIEW_CHECKLIST) == 14
    assert rr.validate_fee_honest_replay_results_review(review)[
        "valid"] is True


def test_real_replay_artifacts_review_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + rr.RESULTS_PATH):
        pytest.skip("real replay artifacts absent on this machine")
    review = rr.build_fee_honest_replay_results_review(
        "C:/SPARTA_BRAIN", tracked_paths=[])
    assert review["verdict"] == rr.VERDICT_RR_ACCEPTED
    assert review["total_net_r_after_costs"] == -21.040902
    assert rr.validate_fee_honest_replay_results_review(review)[
        "valid"] is True


def test_tampering_net_r_away_from_minus_21_04_rejects():
    results = _results()
    for record in results:
        if record["setup_id"] == "SOLUSD_20260520_editv1exp_setup02_touch1":
            record["net_r_after_costs"] = 12.0  # fake a big winner
    review = rr.certify_replay_results(_observation(results=results))
    assert review["verdict"] == rr.VERDICT_RR_REJECTED
    assert ("check_failed:per_label_and_total_net_match_frozen_minus_21"
            "_04_r" in review["blockers"])
    bad_summary = rr.certify_replay_results(_observation(
        summary=_summary(total_net_r_after_costs=5.0)))
    assert bad_summary["verdict"] == rr.VERDICT_RR_REJECTED
    accepted = rr.certify_replay_results(_observation())
    accepted["total_net_r_after_costs"] = 5.0
    assert rr.validate_fee_honest_replay_results_review(accepted)[
        "valid"] is False


def test_removing_costs_rejects():
    results = _results()
    for record in results:
        record["cost_assumptions_bps"] = {"fees_bps": 0.0,
                                          "spread_bps": 0.0,
                                          "slippage_bps": 0.0}
    review = rr.certify_replay_results(_observation(results=results))
    assert review["verdict"] == rr.VERDICT_RR_REJECTED
    assert ("check_failed:costs_27bps_round_trip_charged_on_every_replay"
            in review["blockers"])
    # gross == net would also betray missing costs
    results2 = _results()
    for record in results2:
        if record["gross_r"] is not None:
            record["net_r_after_costs"] = record["gross_r"]
    review2 = rr.certify_replay_results(_observation(results=results2))
    assert ("check_failed:net_below_gross_on_every_completed_replay"
            in review2["blockers"])


def test_changing_cost_bps_rejects():
    results = _results()
    for record in results:
        record["cost_assumptions_bps"] = {"fees_bps": 1.0,
                                          "spread_bps": 0.5,
                                          "slippage_bps": 0.5}
    review = rr.certify_replay_results(_observation(results=results))
    assert review["verdict"] == rr.VERDICT_RR_REJECTED
    bad_summary = rr.certify_replay_results(_observation(
        summary=_summary(cost_assumptions_bps={"fees_bps": 1.0,
                                               "spread_bps": 0.5,
                                               "slippage_bps": 0.5})))
    assert bad_summary["verdict"] == rr.VERDICT_RR_REJECTED
    assert sum(rr.EXPECTED_COSTS_BPS.values()) == 27.0


def test_adding_extra_setup_ids_rejects():
    extra = _results() + [_result(
        "DOGEUSD_20260520_editv1exp_setup01_touch1",
        "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW", "target_4r_hit", 4.0, 3.9)]
    review = rr.certify_replay_results(_observation(results=extra))
    assert review["verdict"] == rr.VERDICT_RR_REJECTED
    assert ("check_failed:scope_exactly_the_7_frozen_setup_ids_no_extras"
            in review["blockers"])
    assert ("check_failed:no_rejected_labels_were_replayed"
            in review["blockers"])


def test_replaying_rejected_labels_rejects():
    results = _results()
    results[0]["setup_id"] = "ARBUSD_20260514_editv1exp_setup01_touch1"
    review = rr.certify_replay_results(_observation(results=results))
    assert review["verdict"] == rr.VERDICT_RR_REJECTED
    assert ("check_failed:no_rejected_labels_were_replayed"
            in review["blockers"])


def test_claiming_paper_live_authorization_rejects():
    bad = rr.certify_replay_results(_observation(
        summary=_summary(no_orders_no_credentials_no_paper_no_live=False)))
    assert bad["verdict"] == rr.VERDICT_RR_REJECTED
    assert ("check_failed:no_paper_live_authorization_and_no_profitability"
            "_claim" in bad["blockers"])
    tampered = rr.certify_replay_results(_observation())
    tampered["candidate_approved_for_paper_or_live"] = True
    assert rr.validate_fee_honest_replay_results_review(tampered)[
        "valid"] is False
    tampered2 = rr.certify_replay_results(_observation())
    tampered2["authorizes_live_trading"] = True
    assert rr.validate_fee_honest_replay_results_review(tampered2)[
        "valid"] is False


def test_claiming_profitability_rejects():
    no_note = rr.certify_replay_results(_observation(
        summary=_summary(honesty_note="strategy is profitable")))
    assert no_note["verdict"] == rr.VERDICT_RR_REJECTED
    claimed = rr.certify_replay_results(_observation(
        summary=_summary(profitability_claim="huge edge")))
    assert claimed["verdict"] == rr.VERDICT_RR_REJECTED
    tampered = rr.certify_replay_results(_observation())
    tampered["profitability_claim_permitted"] = True
    assert rr.validate_fee_honest_replay_results_review(tampered)[
        "valid"] is False


def test_mutating_prior_labels_candles_or_manifests_rejects():
    mutated = dict(rr.BASELINE_PROTECTED_FILES)
    mutated[next(iter(mutated))] = "0" * 64
    review = rr.certify_replay_results(_observation(
        baseline_files_sha256=mutated))
    assert ("check_failed:prior_outputs_and_candles_byte_identical"
            in review["blockers"])
    review2 = rr.certify_replay_results(_observation(
        batch2_manifest_sha256="0" * 64))
    assert ("check_failed:prior_outputs_and_candles_byte_identical"
            in review2["blockers"])
    review3 = rr.certify_replay_results(_observation(
        expanded_labels_sha256="0" * 64))
    assert ("check_failed:prior_outputs_and_candles_byte_identical"
            in review3["blockers"])
    review4 = rr.certify_replay_results(_observation(
        results_sha256="f" * 64))
    assert ("check_failed:replay_artifacts_present_and_sha_pinned"
            in review4["blockers"])


def test_btc_no_entry_and_counts_frozen():
    review = rr.certify_replay_results(_observation())
    assert review["checklist_results"][
        "btcusd_2026_06_09_was_no_entry"] is True
    results = _results()
    for record in results:
        if record["setup_id"].startswith("BTCUSD"):
            record["replay_status"] = "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW"
            record["exit_reason"] = "target_4r_hit"
            record["gross_r"] = 4.0
            record["net_r_after_costs"] = 3.9
    review2 = rr.certify_replay_results(_observation(results=results))
    assert review2["verdict"] == rr.VERDICT_RR_REJECTED
    assert rr.EXPECTED_COMPLETED == 6
    assert rr.EXPECTED_GROSS_TARGET_HITS == 2
    assert rr.EXPECTED_WINS_NET_POSITIVE == 1


def test_scorer_candidate_detector_instructions_unchanged():
    from sparta_commander.crypto_d1_auto_research_strategy_optimizer_contract import (
        FORBIDDEN_FOREVER, LOCKED_HUMAN_INSTRUCTIONS, LOCKED_SCORING_RULES)
    assert len(LOCKED_HUMAN_INSTRUCTIONS) == 7
    assert len(LOCKED_SCORING_RULES) == 9
    assert len(FORBIDDEN_FOREVER) == 12
    from sparta_commander.ny_session_fvg_choch_detector_spec import (
        DETECTOR_STATUSES, LABEL_REQUIRED_FIELDS)
    assert len(LABEL_REQUIRED_FIELDS) == 29
    assert len(DETECTOR_STATUSES) == 9
    from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 import (
        NEW_PARAMETERS)
    assert NEW_PARAMETERS["max_fvg_age_bars"] == 24
    review = rr.certify_replay_results(_observation())
    assert review["checklist_results"][
        "frozen_rules_unchanged_no_drift"] is True
    assert review["this_review_changes_no_rules"] is True


def test_honest_interpretation_frozen():
    review = rr.certify_replay_results(_observation())
    interpretation = review["honest_interpretation"]
    assert ("current_entry_stop_geometry_is_cost_broken" in interpretation)
    assert ("ethusd_2026_05_13_hit_full_4r_target_and_still_lost_6_2r_net"
            in interpretation)
    assert ("current_candidate_is_not_approved_for_paper_or_live"
            in interpretation)
    assert ("no_profitability_claim_is_allowed" in interpretation)
    tampered = rr.certify_replay_results(_observation())
    tampered["honest_interpretation"] = ["all_good"]
    assert rr.validate_fee_honest_replay_results_review(tampered)[
        "valid"] is False
    tampered2 = rr.certify_replay_results(_observation())
    tampered2["expected_per_label"] = {}
    assert rr.validate_fee_honest_replay_results_review(tampered2)[
        "valid"] is False


def test_capabilities_false_gates_locked_and_deterministic():
    review = rr.certify_replay_results(_observation())
    for key in ("executes", "writes_files", "writes_reports",
                "modifies_labels", "deletes_labels", "modifies_staged_files",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        assert review[key] is False, key
    assert review["paper_trading_gate_locked"] is True
    assert review["micro_live_gate_locked"] is True
    assert review["live_gate_locked"] is True
    tampered = rr.certify_replay_results(_observation())
    tampered["forbidden"] = tampered["forbidden"][:3]
    assert rr.validate_fee_honest_replay_results_review(tampered)[
        "valid"] is False
    for item in ("running_another_replay", "new_pnl_calculation",
                 "optimizer_runs", "candidate_rule_changes",
                 "scorer_or_instruction_changes", "profitability_claims",
                 "paper_live_micro_live_authorization",
                 "modifying_labels_candles_or_manifests",
                 "broker_exchange_credential_access", "order_endpoints",
                 "gate_unlocks"):
        assert item in rr.FORBIDDEN, item
    assert (rr.certify_replay_results(_observation())
            == rr.certify_replay_results(_observation()))
    assert rr.certify_replay_results(None)["verdict"] == (
        rr.VERDICT_RR_BLOCKED)
    assert rr.certify_replay_results(_observation(results_present=False))[
        "verdict"] == rr.VERDICT_RR_BLOCKED


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_accepted_labels_human_review_contract as al
    assert len(al.FROZEN_ACCEPTED_SETUP_IDS) == 7
    import sparta_commander.ny_session_fvg_choch_expanded_sample_redetection_review_contract as ex
    assert ex.EXPECTED_ACCEPTED == 7 and ex.EXPECTED_TOTAL_LABELS == 619
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.ny_session_fvg_choch_replay_runner_dry_run import (
        get_replay_runner_dry_run_label)
    assert "Replay Runner" in get_replay_runner_dry_run_label()
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_read_only_and_imports_clean():
    assert rr.get_fee_honest_replay_results_review_label() == rr.RR_LABEL
    assert "READ-ONLY" in rr.RR_LABEL and rr.RR_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in rr.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(rr.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    assert "while true" not in src.lower() and "sleep(" not in src.lower()
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch("):
        assert verb not in src, verb
    tree = ast.parse(src)
    sparta_imports = {node.module for node in ast.walk(tree)
                      if isinstance(node, ast.ImportFrom) and node.module
                      and node.module.startswith("sparta_commander")}
    for module in sparta_imports:
        for fragment in ("replay_runner", "replay_spec", "optimizer"):
            assert fragment not in module, module
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "os", "io", "shutil",
                   "databento", "ssl", "ftplib", "datetime"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))
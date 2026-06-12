"""Tests for the SPARTA NY FVG+CHOCH V2 Cost-Viability Result Review.

Proves the evidence freeze: byte-for-byte reproduction, 619/377/7 counts,
7-of-7 cost rejections, zero survivors, the seven frozen risk distances --
and that any tampering (survivors, counts, params, hashes, claims) REJECTS.
"""

from __future__ import annotations

import ast
import os.path

import pytest

import sparta_commander.ny_session_fvg_choch_v2_cost_viability_result_review_contract as v2r


def _eligibility():
    return [{"setup_id": setup_id, "symbol": setup_id.split("_")[0],
             "session_date": "2026-05-13",
             "entry_to_stop_distance_bps": bps,
             "minimum_required_bps": 81,
             "v2_replay_eligible": False,
             "reason": "cost_dominated_setup_rejected:distance_below_81_bps"}
            for setup_id, bps in
            sorted(v2r.EXPECTED_RISK_DISTANCES_BPS.items())]


def _artifact(**overrides):
    artifact = {
        "edit_id": ("NY_SESSION_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V2_COST"
                    "_VIABILITY_FILTER"),
        "v2_parameters_active": {
            "reject_cost_dominated_setups": True,
            "round_trip_cost_bps": 27,
            "minimum_risk_to_round_trip_cost_multiple": 3,
            "minimum_risk_distance_bps": 81,
            "require_entry_to_stop_distance_bps_gte_minimum": True},
        "v1_freshness_controls_active": {
            "max_fvg_age_bars": 24,
            "require_fresh_unmitigated_15m_fvg": True,
            "max_zone_touches_before_invalidation": 2},
        "detection_reproduced_frozen_expanded_run_exactly": True,
        "labels_total": 619,
        "stale_fvg_controls": {"zones_with_session_touch": 5573,
                               "zones_filtered_stale_age": 4824,
                               "zones_filtered_mitigated": 372,
                               "zones_eligible_fresh": 377,
                               "touches_capped_beyond_limit": 715},
        "detector_accepted": 7,
        "rejected_by_cost_viability_filter": 7,
        "accepted_surviving_v2": 0,
        "surviving_setup_ids": [],
        "per_accepted_label_eligibility": _eligibility(),
        "comparison_vs_v1_expanded_run": {"v1_labels": 619,
                                          "v1_eligible_fresh_zones": 377,
                                          "v1_accepted": 7,
                                          "v1_replay_net_r_after_costs":
                                              -21.040902,
                                          "v2_labels": 619,
                                          "v2_accepted_surviving": 0},
        "replay_ready": False,
        "replay_requires_separate_human_approval": True,
        "no_pnl_no_scoring_no_replay": True,
        "labels_authorize_nothing": True,
    }
    artifact.update(overrides)
    return artifact


def _observation(**overrides):
    observation = {
        "artifact_present": True,
        "artifact": overrides.pop("artifact", None) or _artifact(),
        "artifact_sha256": v2r.EXPECTED_ARTIFACT_SHA256,
        "v2_edit_verdict": "NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V2_READY",
        "tracked_output_paths": [],
        "baseline_files_sha256": dict(v2r.BASELINE_PROTECTED_FILES),
        "batch2_manifest_sha256": v2r.BATCH2_MANIFEST_SHA256,
        "expanded_labels_sha256": v2r.EXPANDED_LABELS_SHA256,
        "replay_results_sha256": v2r.REPLAY_RESULTS_SHA256,
    }
    observation.update(overrides)
    return observation


def test_valid_v2_result_certifies_rejected_all_labels():
    review = v2r.certify_v2_result(_observation())
    assert review["verdict"] == v2r.VERDICT_V2R_REJECTED_ALL
    assert review["blockers"] == []
    assert review["replay_ready"] is False
    assert review["replay_authorized"] is False
    assert review["candidate_approved_for_paper_or_live"] is False
    assert review["profitability_claim_permitted"] is False
    assert all(review["checklist_results"][n] is True
               for n in v2r.REVIEW_CHECKLIST)
    assert len(v2r.REVIEW_CHECKLIST) == 14
    assert v2r.validate_v2_result_review(review)["valid"] is True


def test_real_v2_artifact_review_when_present():
    if not os.path.isfile("C:/SPARTA_BRAIN/" + v2r.ARTIFACT_PATH):
        pytest.skip("real V2 artifact absent on this machine")
    review = v2r.build_v2_result_review("C:/SPARTA_BRAIN",
                                        tracked_paths=[])
    assert review["verdict"] == v2r.VERDICT_V2R_REJECTED_ALL
    assert v2r.validate_v2_result_review(review)["valid"] is True


def test_expected_counts_validate():
    assert v2r.EXPECTED_TOTAL_LABELS == 619
    assert v2r.EXPECTED_ELIGIBLE_FRESH_ZONES == 377
    assert v2r.EXPECTED_DETECTOR_ACCEPTED == 7
    assert v2r.EXPECTED_REJECTED_BY_COST_FILTER == 7
    assert v2r.EXPECTED_SURVIVING == 0
    short = v2r.certify_v2_result(_observation(
        artifact=_artifact(labels_total=618)))
    assert "check_failed:total_setup_attempts_619" in short["blockers"]
    zones = v2r.certify_v2_result(_observation(artifact=_artifact(
        stale_fvg_controls={"zones_eligible_fresh": 1})))
    assert "check_failed:eligible_fresh_zones_377" in zones["blockers"]
    accepted = v2r.certify_v2_result(_observation(
        artifact=_artifact(detector_accepted=6)))
    assert ("check_failed:detector_accepted_before_v2_was_7"
            in accepted["blockers"])


def test_any_surviving_label_changes_verdict():
    survivor = v2r.certify_v2_result(_observation(artifact=_artifact(
        accepted_surviving_v2=1,
        surviving_setup_ids=["SOLUSD_20260513_editv1exp_setup02_touch1"])))
    assert survivor["verdict"] == v2r.VERDICT_V2R_REVIEW_REJECTED
    assert ("check_failed:v2_rejected_7_of_7_and_zero_survivors"
            in survivor["blockers"])
    eligibility = _eligibility()
    eligibility[0]["v2_replay_eligible"] = True
    sneaky = v2r.certify_v2_result(_observation(artifact=_artifact(
        per_accepted_label_eligibility=eligibility)))
    assert sneaky["verdict"] == v2r.VERDICT_V2R_REVIEW_REJECTED
    ready = v2r.certify_v2_result(_observation(
        artifact=_artifact(replay_ready=True)))
    assert "check_failed:replay_ready_false" in ready["blockers"]


def test_replay_pnl_scorer_claims_reject():
    bad = v2r.certify_v2_result(_observation(
        artifact=_artifact(no_pnl_no_scoring_no_replay=False)))
    assert bad["verdict"] == v2r.VERDICT_V2R_REVIEW_REJECTED
    eligibility = _eligibility()
    eligibility[2]["net_pnl"] = 5.0
    leak = v2r.certify_v2_result(_observation(artifact=_artifact(
        per_accepted_label_eligibility=eligibility)))
    assert ("check_failed:no_replay_pnl_scorer_or_optimizer_execution"
            in leak["blockers"])
    tampered = v2r.certify_v2_result(_observation())
    tampered["profitability_claim_permitted"] = True
    assert v2r.validate_v2_result_review(tampered)["valid"] is False
    tampered2 = v2r.certify_v2_result(_observation())
    tampered2["replay_authorized"] = True
    assert v2r.validate_v2_result_review(tampered2)["valid"] is False
    tampered3 = v2r.certify_v2_result(_observation())
    tampered3["candidate_approved_for_paper_or_live"] = True
    assert v2r.validate_v2_result_review(tampered3)["valid"] is False


def test_hardcoded_or_tampered_params_reject():
    wrong = v2r.certify_v2_result(_observation(artifact=_artifact(
        v2_parameters_active={"minimum_risk_distance_bps": 5})))
    assert ("check_failed:v2_params_read_from_pushed_asset_not_hardcoded"
            in wrong["blockers"])
    wrong_edit = v2r.certify_v2_result(_observation(
        artifact=_artifact(edit_id="AD_HOC_EDIT")))
    assert ("check_failed:v2_params_read_from_pushed_asset_not_hardcoded"
            in wrong_edit["blockers"])
    not_ready = v2r.certify_v2_result(_observation(
        v2_edit_verdict="NY_FVG_CHOCH_MUTABLE_CANDIDATE_EDIT_V2_BLOCKED"))
    assert ("check_failed:v2_params_read_from_pushed_asset_not_hardcoded"
            in not_ready["blockers"])
    v1_lost = v2r.certify_v2_result(_observation(artifact=_artifact(
        v1_freshness_controls_active={"max_fvg_age_bars": 999})))
    assert "check_failed:v1_controls_remained_intact" in v1_lost["blockers"]


def test_missing_baseline_hash_proof_rejects():
    not_reproduced = v2r.certify_v2_result(_observation(artifact=_artifact(
        detection_reproduced_frozen_expanded_run_exactly=False)))
    assert ("check_failed:detection_reproduced_frozen_expanded_run_byte_for"
            "_byte" in not_reproduced["blockers"])
    wrong_hash = v2r.certify_v2_result(_observation(
        expanded_labels_sha256="0" * 64))
    assert ("check_failed:expanded_labels_hash_matches_pinned_reference"
            in wrong_hash["blockers"])
    wrong_artifact = v2r.certify_v2_result(_observation(
        artifact_sha256="f" * 64))
    assert ("check_failed:v2_artifact_present_and_sha_pinned"
            in wrong_artifact["blockers"])
    missing = v2r.certify_v2_result(_observation(artifact_present=False))
    assert missing["verdict"] == v2r.VERDICT_V2R_BLOCKED
    assert v2r.certify_v2_result(None)["verdict"] == v2r.VERDICT_V2R_BLOCKED


def test_missing_or_changed_risk_distance_table_rejects():
    assert v2r.EXPECTED_RISK_DISTANCES_BPS[
        "ETHUSD_20260513_editv1exp_setup01_touch2"] == 2.645024
    assert v2r.EXPECTED_RISK_DISTANCES_BPS[
        "SOLUSD_20260513_editv1exp_setup02_touch1"] == 33.15758
    assert max(v2r.EXPECTED_RISK_DISTANCES_BPS.values()) < 81
    eligibility = _eligibility()
    eligibility[0]["entry_to_stop_distance_bps"] = 95.0
    widened = v2r.certify_v2_result(_observation(artifact=_artifact(
        per_accepted_label_eligibility=eligibility)))
    assert ("check_failed:risk_distance_table_matches_frozen_evidence"
            in widened["blockers"])
    missing_row = v2r.certify_v2_result(_observation(artifact=_artifact(
        per_accepted_label_eligibility=_eligibility()[:-1])))
    assert ("check_failed:risk_distance_table_matches_frozen_evidence"
            in missing_row["blockers"])
    tampered = v2r.certify_v2_result(_observation())
    tampered["expected_risk_distances_bps"] = {}
    assert v2r.validate_v2_result_review(tampered)["valid"] is False


def test_missing_artifact_provenance_rejects():
    mutated = dict(v2r.BASELINE_PROTECTED_FILES)
    mutated[next(iter(mutated))] = "0" * 64
    review = v2r.certify_v2_result(_observation(
        baseline_files_sha256=mutated))
    assert ("check_failed:prior_outputs_and_candles_byte_identical"
            in review["blockers"])
    review2 = v2r.certify_v2_result(_observation(
        batch2_manifest_sha256="0" * 64))
    assert ("check_failed:prior_outputs_and_candles_byte_identical"
            in review2["blockers"])
    review3 = v2r.certify_v2_result(_observation(
        replay_results_sha256="0" * 64))
    assert ("check_failed:prior_outputs_and_candles_byte_identical"
            in review3["blockers"])
    tracked = v2r.certify_v2_result(_observation(
        tracked_output_paths=["data/ny_fvg_choch/detector_labels/x.json"]))
    assert ("check_failed:artifacts_untracked_and_no_trading_capability"
            in tracked["blockers"])


def test_wallet_api_order_private_endpoint_fields_reject():
    for bad in ("wallet_address", "api_key_env", "order_id",
                "private_endpoint_url", "login_token"):
        eligibility = _eligibility()
        eligibility[3][bad] = "x"
        review = v2r.certify_v2_result(_observation(artifact=_artifact(
            per_accepted_label_eligibility=eligibility)))
        assert review["verdict"] == v2r.VERDICT_V2R_REVIEW_REJECTED, bad
        assert ("check_failed:no_replay_pnl_scorer_or_optimizer_execution"
                in review["blockers"]), bad


def test_honest_conclusion_frozen():
    review = v2r.certify_v2_result(_observation())
    conclusion = review["honest_research_conclusion"]
    assert ("exact_1m_fvg_impulse_candle_stop_geometry_is_not_viable_under"
            "_27bps_taker_execution" in conclusion)
    assert "option_1_rejection_kept_on_record" in conclusion
    assert "option_2_v3_wider_structural_stop_research" in conclusion
    assert ("option_3_separate_lower_cost_maker_execution_research_not"
            "_assumed_here" in conclusion)
    tampered = v2r.certify_v2_result(_observation())
    tampered["honest_research_conclusion"] = ["strategy_is_fine"]
    assert v2r.validate_v2_result_review(tampered)["valid"] is False


def test_capabilities_false_gates_locked_and_deterministic():
    review = v2r.certify_v2_result(_observation())
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
    assert review["v3_or_rejection_is_a_human_decision"] is True
    tampered = v2r.certify_v2_result(_observation())
    tampered["forbidden"] = tampered["forbidden"][:3]
    assert v2r.validate_v2_result_review(tampered)["valid"] is False
    for item in ("replay_runs", "pnl_calculation", "profitability_claims",
                 "scorer_or_optimizer_runs", "rule_changes",
                 "candidate_asset_changes",
                 "modifying_labels_candles_or_artifacts",
                 "deleting_prior_outputs",
                 "broker_exchange_credential_access", "order_endpoints",
                 "paper_live_micro_live_authorization", "gate_unlocks"):
        assert item in v2r.FORBIDDEN, item
    assert (v2r.certify_v2_result(_observation())
            == v2r.certify_v2_result(_observation()))


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v2_cost_viability as m2
    assert m2.MINIMUM_RISK_DISTANCE_BPS == 81
    import sparta_commander.ny_session_fvg_choch_fee_honest_replay_results_review_contract as rr
    assert rr.EXPECTED_TOTAL_NET_R == -21.040902
    import sparta_commander.ny_session_fvg_choch_accepted_labels_human_review_contract as al
    assert len(al.FROZEN_ACCEPTED_SETUP_IDS) == 7
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
        FIB_LEVEL, RISK_REWARD_TARGET)
    assert FIB_LEVEL == 0.618 and RISK_REWARD_TARGET == 4.0
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_read_only_and_imports_clean():
    assert v2r.get_v2_result_review_label() == v2r.V2R_LABEL
    assert "READ-ONLY" in v2r.V2R_LABEL and v2r.V2R_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in v2r.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(v2r.__file__, encoding="utf-8").read()
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
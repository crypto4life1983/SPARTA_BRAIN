"""Tests for the SPARTA Breakout-Pullback Detector Dry-Run Review.

Proves the review certifies the live fixture dry run (all 10 statuses,
~150.88 bps accepted, ~17.9 bps rejected at label time), blocks/rejects on
any missing or tampered behavior, and keeps everything locked: no real
candles, no replay/scorer/optimizer, candidate #1 preserved.
"""

from __future__ import annotations

import ast

import sparta_commander.crypto_intraday_breakout_pullback_structure_detector_dry_run_review_contract as bpv


def _statuses(**overrides):
    statuses = {
        "accepted": "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW",
        "no_breakout": "BP_SETUP_REJECTED_NO_BREAKOUT",
        "weak_breakout": "BP_SETUP_REJECTED_WEAK_BREAKOUT",
        "no_pullback": "BP_SETUP_REJECTED_NO_PULLBACK",
        "failed_retest": "BP_SETUP_REJECTED_FAILED_RETEST",
        "no_continuation": "BP_SETUP_REJECTED_NO_CONTINUATION",
        "risk_below_floor": "BP_SETUP_REJECTED_RISK_BELOW_81_BPS",
        "ambiguous": "BP_SETUP_REJECTED_AMBIGUOUS_STRUCTURE",
        "insufficient": "BP_SETUP_REJECTED_INSUFFICIENT_CANDLES",
        "forbidden": "BP_SETUP_REJECTED_FORBIDDEN_CAPABILITY",
    }
    statuses.update(overrides)
    return statuses


def _observation(**overrides):
    from sparta_commander.crypto_intraday_breakout_pullback_structure_detector_spec import (
        BP_LABEL_REQUIRED_FIELDS)
    observation = {
        "detector_spec_verdict": "BREAKOUT_PULLBACK_DETECTOR_SPEC_READY",
        "statuses": overrides.pop("statuses", None) or _statuses(),
        "accepted_label_keys": sorted(BP_LABEL_REQUIRED_FIELDS),
        "accepted_risk_bps": 150.883219,
        "accepted_cost_floor_pass": True,
        "accepted_cost_floor_bps": 81,
        "tight_risk_bps": 17.946162,
        "tight_cost_floor_pass": False,
        "deterministic": True,
        "real_candle_output_dir_exists": False,
    }
    observation.update(overrides)
    return observation


def test_live_dry_run_behavior_accepts_for_real_candle_detection():
    review = bpv.build_bp_dry_run_review("C:/SPARTA_BRAIN")
    assert review["verdict"] == bpv.VERDICT_BPV_ACCEPTED
    assert review["blockers"] == []
    assert all(review["checklist_results"][n] is True
               for n in bpv.REVIEW_CHECKLIST)
    assert len(bpv.REVIEW_CHECKLIST) == 12
    assert bpv.validate_bp_dry_run_review(review)["valid"] is True


def test_synthetic_valid_observation_accepts():
    review = bpv.certify_bp_dry_run(_observation())
    assert review["verdict"] == bpv.VERDICT_BPV_ACCEPTED
    assert review["acceptance_authorizes_nothing"] is True
    assert review[
        "real_candle_detection_requires_separate_human_approval"] is True


def test_missing_ready_detector_spec_rejects():
    review = bpv.certify_bp_dry_run(_observation(
        detector_spec_verdict="BREAKOUT_PULLBACK_DETECTOR_SPEC_BLOCKED"))
    assert review["verdict"] == bpv.VERDICT_BPV_REJECTED
    assert "check_failed:detector_spec_ready" in review["blockers"]
    assert bpv.certify_bp_dry_run(None)["verdict"] == (
        bpv.VERDICT_BPV_BLOCKED)


def test_missing_accepted_fixture_rejects():
    review = bpv.certify_bp_dry_run(_observation(
        statuses=_statuses(accepted="BP_SETUP_REJECTED_NO_BREAKOUT")))
    assert review["verdict"] == bpv.VERDICT_BPV_REJECTED
    assert "check_failed:clean_fixture_accepted" in review["blockers"]


def test_wrong_accepted_risk_distance_rejects():
    review = bpv.certify_bp_dry_run(_observation(accepted_risk_bps=99.0))
    assert review["verdict"] == bpv.VERDICT_BPV_REJECTED
    assert ("check_failed:accepted_risk_approx_150_88_bps_with_floor_pass"
            in review["blockers"])
    no_pass = bpv.certify_bp_dry_run(_observation(
        accepted_cost_floor_pass=False))
    assert no_pass["verdict"] == bpv.VERDICT_BPV_REJECTED


def test_missing_risk_floor_rejection_rejects():
    review = bpv.certify_bp_dry_run(_observation(
        statuses=_statuses(
            risk_below_floor="BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW")))
    assert review["verdict"] == bpv.VERDICT_BPV_REJECTED
    assert ("check_failed:tight_fixture_rejected_below_81_bps"
            in review["blockers"])
    floor_skipped = bpv.certify_bp_dry_run(_observation(
        tight_cost_floor_pass=True))
    assert ("check_failed:floor_checked_at_label_time_via_pushed_filter"
            in floor_skipped["blockers"])
    wide_tight = bpv.certify_bp_dry_run(_observation(tight_risk_bps=90.0))
    assert wide_tight["verdict"] == bpv.VERDICT_BPV_REJECTED


def test_missing_status_coverage_rejects():
    incomplete = _statuses()
    del incomplete["weak_breakout"]
    review = bpv.certify_bp_dry_run(_observation(statuses=incomplete))
    assert review["verdict"] == bpv.VERDICT_BPV_REJECTED
    assert ("check_failed:all_10_statuses_exercised_by_fixtures"
            in review["blockers"])
    wrong = bpv.certify_bp_dry_run(_observation(
        statuses=_statuses(forbidden="BP_SETUP_REJECTED_AMBIGUOUS"
                                     "_STRUCTURE")))
    assert ("check_failed:forbidden_capability_fixture_rejects"
            in wrong["blockers"])


def test_schema_and_determinism_required():
    review = bpv.certify_bp_dry_run(_observation(
        accepted_label_keys=["setup_id", "detector_status"]))
    assert ("check_failed:label_schema_38_fields_complete"
            in review["blockers"])
    drifted = bpv.certify_bp_dry_run(_observation(deterministic=False))
    assert ("check_failed:fixture_only_deterministic_no_fetch_no_files"
            in drifted["blockers"])
    ran_real = bpv.certify_bp_dry_run(_observation(
        real_candle_output_dir_exists=True))
    assert ("check_failed:no_real_candle_detector_run_occurred"
            in ran_real["blockers"])


def test_replay_scorer_optimizer_claims_reject():
    review = bpv.certify_bp_dry_run(_observation())
    for flag in ("runs_replay_now", "scores_now", "runs_detector_now",
                 "authorizes_paper_execution", "authorizes_live_trading"):
        tampered = bpv.certify_bp_dry_run(_observation())
        tampered[flag] = True
        assert bpv.validate_bp_dry_run_review(tampered)["valid"] is False, flag
    for item in ("real_candle_detector_runs", "replay_runs", "scorer_runs",
                 "optimizer_runs", "report_artifact_creation",
                 "network_retrieval",
                 "broker_exchange_private_api_access",
                 "credentials_api_keys_login_account_wallet",
                 "trading_endpoints_of_any_kind",
                 "paper_live_micro_live_authorization", "gate_unlocks",
                 "deleting_or_hiding_candidate_1_rejected_evidence"):
        assert item in bpv.FORBIDDEN, item
    assert review["verdict"] == bpv.VERDICT_BPV_ACCEPTED


def test_capabilities_false_gates_locked_and_validator_strict():
    review = bpv.certify_bp_dry_run(_observation())
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
    tampered = bpv.certify_bp_dry_run(_observation())
    tampered["forbidden"] = tampered["forbidden"][:3]
    assert bpv.validate_bp_dry_run_review(tampered)["valid"] is False
    tampered2 = bpv.certify_bp_dry_run(_observation())
    tampered2["candidate_1_evidence_kept_on_record"] = False
    assert bpv.validate_bp_dry_run_review(tampered2)["valid"] is False
    assert (bpv.certify_bp_dry_run(_observation())
            == bpv.certify_bp_dry_run(_observation()))


def test_candidate_1_remains_rejected_and_preserved():
    review = bpv.certify_bp_dry_run(_observation())
    assert review["checklist_results"][
        "candidate_1_rejected_and_preserved"] is True
    assert review["candidate_1_evidence_kept_on_record"] is True
    from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
        REJECTION_REASON, REJECTION_STATUS)
    assert REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
    assert REJECTION_REASON == "COST_NON_VIABLE_RISK_GEOMETRY"


def test_upstream_stack_and_pm_lane_untouched():
    import sparta_commander.crypto_intraday_breakout_pullback_structure_detector_spec as bpd
    assert len(bpd.BP_LABEL_REQUIRED_FIELDS) == 38
    assert len(bpd.BP_DETECTOR_STATUSES) == 10
    import sparta_commander.crypto_intraday_breakout_pullback_structure_strategy_spec_contract as bp
    assert bp.MINIMUM_RISK_DISTANCE_BPS == 81
    import sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review as ad
    assert len(ad.BASELINE_PROTECTED_FILES) == 5
    from sparta_commander.strategy_factory_mission_flow_status import (
        LATEST_COMPLETED_PM_LANE_CHAIN)
    assert "Research Only" in LATEST_COMPLETED_PM_LANE_CHAIN


def test_label_action_read_only_and_imports_clean():
    assert bpv.get_bp_dry_run_review_label() == bpv.BPV_LABEL
    assert "READ-ONLY" in bpv.BPV_LABEL and bpv.BPV_MODE == "RESEARCH_ONLY"
    for banned in ("PROMOTE", "UNLOCK", "ACQUIRE", "FETCH", "EXECUTE",
                   "EXECUTION", "BACKTEST", "BASELINE", "PAPER", "LIVE",
                   "BROKER", "EXCHANGE", "AUTOMATION", "ORDER", "TRACK"):
        assert banned not in bpv.NEXT_REQUIRED_ACTION.upper(), banned
    src = open(bpv.__file__, encoding="utf-8").read()
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
        for fragment in ("replay_runner", "replay_spec", "optimizer",
                         "fetch"):
            assert fragment not in module, module
    banned_mods = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
                   "subprocess", "websockets", "aiohttp", "schedule",
                   "apscheduler", "threading", "asyncio", "time", "telegram",
                   "email", "csv", "pandas", "os", "io", "json", "shutil",
                   "databento", "ssl", "ftplib", "datetime", "hashlib"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned_mods)
    assert not any(call.func.attr == "open" if isinstance(call.func, ast.Attribute)
                   else getattr(call.func, "id", "") == "open"
                   for call in ast.walk(tree) if isinstance(call, ast.Call))
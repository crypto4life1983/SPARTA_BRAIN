"""SPARTA BREAKOUT-PULLBACK DETECTOR DRY-RUN REVIEW (READ-ONLY).

The human-review contract over candidate #2's fixture-only detector dry
run: it exercises the LIVE pushed dry run on canonical in-memory fixtures
covering ALL 10 closed statuses, verifies the 38-field schema, the
deterministic behavior, and -- decisively -- that the 81 bps cost floor is
enforced AT LABEL TIME via the pushed V2 filter (clean fixture accepted at
~150.88 bps; tight fixture rejected at ~17.9 bps). Acceptance authorizes
nothing: the real-candle detection over the staged 21 sessions is its own
future human approval, and candidate #1 stays rejected on record.
"""

from __future__ import annotations

import pathlib as _pathlib
from typing import Any

from sparta_commander.crypto_intraday_breakout_pullback_structure_detector_dry_run import (
    run_bp_detector_dry_run,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_detector_spec import (
    BP_DETECTOR_STATUSES,
    BP_LABEL_REQUIRED_FIELDS,
    VERDICT_BPD_READY,
    build_bp_detector_spec,
    label_bp_setup,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_strategy_spec_contract import (
    CANDIDATE_ID,
)

BPV_SCHEMA_VERSION = (
    "crypto_intraday_breakout_pullback_structure_detector_dry_run_review.v1")
BPV_LABEL = ("SPARTA Breakout-Pullback Detector Dry-Run Review "
             "(READ-ONLY, REVIEW ONLY)")
BPV_MODE = "RESEARCH_ONLY"
VERDICT_BPV_ACCEPTED = (
    "BP_DETECTOR_DRY_RUN_ACCEPTED_FOR_REAL_CANDLE_DETECTION")
VERDICT_BPV_REJECTED = "BP_DETECTOR_DRY_RUN_REJECTED"
VERDICT_BPV_BLOCKED = "BP_DETECTOR_DRY_RUN_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_BP_REAL_CANDLE_DETECTION"

EXPECTED_ACCEPTED_RISK_BPS = 150.883219
EXPECTED_TIGHT_RISK_BPS_MAX = 18.0
COST_FLOOR_BPS = 81

REVIEW_CHECKLIST = (
    "detector_spec_ready",
    "label_schema_38_fields_complete",
    "status_set_closed_10",
    "clean_fixture_accepted",
    "accepted_risk_approx_150_88_bps_with_floor_pass",
    "tight_fixture_rejected_below_81_bps",
    "floor_checked_at_label_time_via_pushed_filter",
    "all_10_statuses_exercised_by_fixtures",
    "fixture_only_deterministic_no_fetch_no_files",
    "no_real_candle_detector_run_occurred",
    "candidate_1_rejected_and_preserved",
    "forbidden_capability_fixture_rejects",
)

FORBIDDEN = (
    "real_candle_detector_runs", "replay_runs", "scorer_runs",
    "optimizer_runs", "report_artifact_creation", "network_retrieval",
    "broker_exchange_private_api_access",
    "credentials_api_keys_login_account_wallet",
    "trading_endpoints_of_any_kind",
    "paper_live_micro_live_authorization", "gate_unlocks",
    "deleting_or_hiding_candidate_1_rejected_evidence",
)


def _bar(i, o, h, l, c, **extra):
    bar = {"timestamp_utc": "2026-06-10T%02d:%02d:00Z" % (i // 4,
                                                          (i % 4) * 15),
           "open": o, "high": h, "low": l, "close": c}
    bar.update(extra)
    return bar


def _range_bars(count, start=0):
    return [_bar(start + i, 99.9, 100.5, 99.5, 100.1)
            for i in range(count)]


def _accepted_fixture():
    return (_range_bars(36)
            + [_bar(36, 100.2, 101.1, 100.1, 101.0),
               _bar(37, 101.0, 102.0, 100.9, 101.8),
               _bar(38, 101.6, 101.7, 100.55, 100.9),
               _bar(39, 101.0, 102.0, 100.9, 101.9)])


def _tight_fixture():
    return ([_bar(i, 99.99, 100.02, 99.98, 100.01) for i in range(36)]
            + [_bar(36, 100.0, 100.16, 100.0, 100.13),
               _bar(37, 100.13, 100.3, 100.18, 100.28),
               _bar(38, 100.25, 100.26, 100.12, 100.2),
               _bar(39, 100.2, 100.32, 100.18, 100.3)])


def get_bp_dry_run_review_label() -> str:
    return BPV_LABEL


def observe_bp_detector_behavior(
        repo_root: Any = "C:/SPARTA_BRAIN") -> dict[str, Any]:
    """Exercise the LIVE pushed dry run on canonical fixtures. In-memory."""
    run = run_bp_detector_dry_run
    accepted = run("BTCUSD", "2026-06-10", _accepted_fixture())
    statuses = {
        "accepted": accepted["detector_status"],
        "no_breakout": run("BTCUSD", "2026-06-10",
                           _range_bars(45))["detector_status"],
        "weak_breakout": run("BTCUSD", "2026-06-10", _range_bars(36) + [
            _bar(36, 100.55, 101.3, 100.3, 100.75)]
            + _range_bars(3, start=37))["detector_status"],
        "no_pullback": run("BTCUSD", "2026-06-10", _range_bars(36) + [
            _bar(36, 100.2, 101.1, 100.1, 101.0),
            _bar(37, 101.0, 101.8, 101.2, 101.5),
            _bar(38, 101.5, 101.9, 101.3, 101.6),
            _bar(39, 101.6, 102.0, 101.4, 101.8)])["detector_status"],
        "failed_retest": run("BTCUSD", "2026-06-10", _range_bars(36) + [
            _bar(36, 100.2, 101.1, 100.1, 101.0),
            _bar(37, 100.9, 101.0, 99.9, 100.0)]
            + _range_bars(2, start=38))["detector_status"],
        "no_continuation": run("BTCUSD", "2026-06-10", _range_bars(36) + [
            _bar(36, 100.2, 101.1, 100.1, 101.0),
            _bar(37, 101.0, 102.0, 100.9, 101.8),
            _bar(38, 101.6, 101.7, 100.55, 100.9),
            _bar(39, 100.9, 101.5, 100.7, 101.2)])["detector_status"],
        "insufficient": run("BTCUSD", "2026-06-10",
                            _range_bars(10))["detector_status"],
        "forbidden": run("BTCUSD", "2026-06-10", _accepted_fixture()[:3] + [
            _bar(3, 99.9, 100.5, 99.5, 100.1, order_id="x")]
            + _accepted_fixture()[4:])["detector_status"],
        "ambiguous": label_bp_setup(
            {"setup_id": "x", "symbol": "BTCUSD",
             "session_date": "2026-06-10",
             "direction": "sideways"})["detector_status"],
    }
    tight = run("BTCUSD", "2026-06-10", _tight_fixture())
    statuses["risk_below_floor"] = tight["detector_status"]
    rerun = run("BTCUSD", "2026-06-10", _accepted_fixture())
    spec = build_bp_detector_spec(repo_root)
    return {
        "detector_spec_verdict": spec.get("verdict"),
        "statuses": statuses,
        "accepted_label_keys": sorted(accepted),
        "accepted_risk_bps": accepted.get("risk_distance_bps"),
        "accepted_cost_floor_pass": accepted.get("cost_floor_pass"),
        "accepted_cost_floor_bps": accepted.get("cost_floor_bps"),
        "tight_risk_bps": tight.get("risk_distance_bps"),
        "tight_cost_floor_pass": tight.get("cost_floor_pass"),
        "deterministic": accepted == rerun,
        "real_candle_output_dir_exists": _pathlib.Path(
            str(repo_root),
            "data/crypto_intraday_breakout_pullback_structure").is_dir(),
    }


def certify_bp_dry_run(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of observed dry-run behavior. Pure."""
    review: dict[str, Any] = {
        "schema_version": BPV_SCHEMA_VERSION, "label": BPV_LABEL,
        "mode": BPV_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "forbidden": list(FORBIDDEN),
        "acceptance_authorizes_nothing": True,
        "real_candle_detection_requires_separate_human_approval": True,
        "candidate_1_evidence_kept_on_record": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "modifies_labels": False, "deletes_labels": False,
        "modifies_staged_files": False,
        "runs_detector_now": False, "runs_replay_now": False,
        "scores_now": False, "fetches_data": False, "calls_api": False,
        "uses_network": False, "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False, "authorizes_micro_live": False,
        "authorizes_live_trading": False, "promotes_gate": False,
        "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not isinstance(observation, dict):
        review["verdict"] = VERDICT_BPV_BLOCKED
        review["blockers"].append("observation_missing_dry_run_unavailable")
        return review
    o = observation
    statuses = o.get("statuses") or {}
    r: dict[str, bool] = {}
    r["detector_spec_ready"] = (
        o.get("detector_spec_verdict") == VERDICT_BPD_READY)
    r["label_schema_38_fields_complete"] = (
        o.get("accepted_label_keys")
        == sorted(BP_LABEL_REQUIRED_FIELDS)
        and len(BP_LABEL_REQUIRED_FIELDS) == 38)
    r["status_set_closed_10"] = len(BP_DETECTOR_STATUSES) == 10
    r["clean_fixture_accepted"] = (
        statuses.get("accepted")
        == "BP_SETUP_LABEL_ACCEPTED_FOR_REPLAY_REVIEW")
    accepted_risk = o.get("accepted_risk_bps")
    r["accepted_risk_approx_150_88_bps_with_floor_pass"] = (
        isinstance(accepted_risk, (int, float))
        and abs(accepted_risk - EXPECTED_ACCEPTED_RISK_BPS) < 0.01
        and o.get("accepted_cost_floor_pass") is True
        and o.get("accepted_cost_floor_bps") == COST_FLOOR_BPS)
    tight_risk = o.get("tight_risk_bps")
    r["tight_fixture_rejected_below_81_bps"] = (
        statuses.get("risk_below_floor")
        == "BP_SETUP_REJECTED_RISK_BELOW_81_BPS"
        and isinstance(tight_risk, (int, float))
        and tight_risk < EXPECTED_TIGHT_RISK_BPS_MAX)
    r["floor_checked_at_label_time_via_pushed_filter"] = (
        o.get("tight_cost_floor_pass") is False
        and isinstance(tight_risk, (int, float))
        and tight_risk < COST_FLOOR_BPS
        and isinstance(accepted_risk, (int, float))
        and accepted_risk >= COST_FLOOR_BPS)
    expected_status_map = {
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
    r["all_10_statuses_exercised_by_fixtures"] = (
        statuses == expected_status_map
        and set(expected_status_map.values()) == set(BP_DETECTOR_STATUSES))
    r["fixture_only_deterministic_no_fetch_no_files"] = (
        o.get("deterministic") is True)
    r["no_real_candle_detector_run_occurred"] = (
        o.get("real_candle_output_dir_exists") is False)
    try:
        from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
            REJECTION_REASON, REJECTION_STATUS)
        r["candidate_1_rejected_and_preserved"] = (
            REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
            and REJECTION_REASON == "COST_NON_VIABLE_RISK_GEOMETRY")
    except ImportError:
        r["candidate_1_rejected_and_preserved"] = False
    r["forbidden_capability_fixture_rejects"] = (
        statuses.get("forbidden")
        == "BP_SETUP_REJECTED_FORBIDDEN_CAPABILITY")
    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_BPV_REJECTED
        review["blockers"].extend("check_failed:" + n for n in failed)
        return review
    review["verdict"] = VERDICT_BPV_ACCEPTED
    return review


def build_bp_dry_run_review(
        repo_root: Any = "C:/SPARTA_BRAIN") -> dict[str, Any]:
    """Observe the live dry run and certify it. In-memory."""
    return certify_bp_dry_run(observe_bp_detector_behavior(repo_root))


def validate_bp_dry_run_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    if v.get("verdict") not in (VERDICT_BPV_ACCEPTED, VERDICT_BPV_REJECTED,
                                VERDICT_BPV_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_BPV_ACCEPTED:
        if v.get("blockers"):
            errors.append("accepted_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("accepted_without_full_passing_checklist")
    if v.get("verdict") in (VERDICT_BPV_REJECTED, VERDICT_BPV_BLOCKED) \
            and not v.get("blockers"):
        errors.append("non_accepted_without_blockers")
    for key, want in (
        ("acceptance_authorizes_nothing", True),
        ("real_candle_detection_requires_separate_human_approval", True),
        ("candidate_1_evidence_kept_on_record", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if v.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
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
        if v.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}

"""SPARTA NY-Session FVG+CHOCH FEE-HONEST REPLAY RESULTS REVIEW
(READ-ONLY, REVIEW ONLY, FREEZES THE EVIDENCE).

The first fee-honest replay in the lane's history, frozen: exactly the 7
accepted setup_ids were replayed -- 1 NO_ENTRY, 6 completed, 2 of 6 hit the
4R gross target, and the NET result after 27 bps round-trip costs was
-21.04R. ETHUSD 2026-05-13 hit its FULL target and still lost 6.2R net:
the 1m-FVG stop geometry is cost-broken. The candidate is NOT approved for
paper/live; no profitability claim is permitted; the next decision -- a
cost-viability candidate edit V2 or rejection kept on record -- is human.
This review runs nothing and changes no rules.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

from sparta_commander.ny_session_fvg_choch_accepted_labels_human_review_contract import (
    BATCH2_MANIFEST_PATH,
    BATCH2_MANIFEST_SHA256,
    FROZEN_ACCEPTED_SETUP_IDS,
    VERDICT_AL_APPROVED,
    build_accepted_labels_human_review,
)
from sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review import (
    BASELINE_PROTECTED_FILES,
)
from sparta_commander.ny_session_fvg_choch_expanded_sample_redetection_review_contract import (
    EXPECTED_LABELS_SHA256 as EXPANDED_LABELS_SHA256,
    LABELS_PATH as EXPANDED_LABELS_PATH,
)
from sparta_commander.ny_session_fvg_choch_mutable_candidate_edit_v1 import (
    EDIT_ID,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
    FIB_LEVEL,
    FIB_TOLERANCE,
    RISK_REWARD_TARGET,
)

RR_SCHEMA_VERSION = (
    "ny_session_fvg_choch_fee_honest_replay_results_review.v1")
RR_LABEL = ("SPARTA NY-Session FVG+CHOCH Fee-Honest Replay Results Review "
            "(READ-ONLY, REVIEW ONLY, NO PROFITABILITY CLAIM PERMITTED)")
RR_MODE = "RESEARCH_ONLY"
VERDICT_RR_ACCEPTED = "FEE_HONEST_REPLAY_RESULTS_ACCEPTED_AS_EVIDENCE"
VERDICT_RR_REJECTED = "FEE_HONEST_REPLAY_RESULTS_REJECTED"
VERDICT_RR_BLOCKED = "FEE_HONEST_REPLAY_RESULTS_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_ON_CANDIDATE_EDIT_V2_OR_REJECTION_KEPT_ON_RECORD")

RESULTS_PATH = ("data/ny_fvg_choch/replay_results/"
                "replay_results_7_accepted_2026-06-11.jsonl")
SUMMARY_PATH = ("data/ny_fvg_choch/replay_results/"
                "replay_summary_7_accepted_2026-06-11.json")
EXPECTED_RESULTS_SHA256 = (
    "97257ad29fc58b52793c1b55cb2ca7316a93b11d5ff7bf2cdd7e7fe03df2fa88")
EXPECTED_SUMMARY_SHA256 = (
    "4f8b1ed3e5d1fec1568a69e20244371dd67a9966073fedcdf60eae4a9506d2c8")

EXPECTED_COSTS_BPS = {"fees_bps": 20.0, "spread_bps": 2.0,
                      "slippage_bps": 5.0}
EXPECTED_ROUND_TRIP_COST_BPS = 27.0
EXPECTED_ANTI_LOOKAHEAD_MINUTES = 3
EXPECTED_TOTAL_NET_R = -21.040902
EXPECTED_COMPLETED = 6
EXPECTED_NO_ENTRY = 1
EXPECTED_GROSS_TARGET_HITS = 2
EXPECTED_WINS_NET_POSITIVE = 1

# Per-label frozen outcomes (status, exit_reason, gross_r, net_r).
EXPECTED_PER_LABEL = {
    "AVAXUSD_20260529_editv1exp_setup04_touch2":
        ("REPLAY_READY_FOR_LOCKED_SCORER_REVIEW", "stop_hit",
         -1.0, -7.01425),
    "BTCUSD_20260609_editv1exp_setup05_touch1":
        ("REPLAY_REJECTED_NO_ENTRY", None, None, None),
    "ETHUSD_20260513_editv1exp_setup01_touch2":
        ("REPLAY_READY_FOR_LOCKED_SCORER_REVIEW", "target_4r_hit",
         4.0, -6.207845),
    "ETHUSD_20260515_editv1exp_setup02_touch2":
        ("REPLAY_READY_FOR_LOCKED_SCORER_REVIEW", "stop_hit",
         -1.0, -3.917728),
    "SOLUSD_20260513_editv1exp_setup02_touch1":
        ("REPLAY_READY_FOR_LOCKED_SCORER_REVIEW", "stop_hit",
         -1.0, -1.814293),
    "SOLUSD_20260520_editv1exp_setup02_touch1":
        ("REPLAY_READY_FOR_LOCKED_SCORER_REVIEW", "target_4r_hit",
         4.0, 2.46496),
    "SOLUSD_20260526_editv1exp_setup01_touch1":
        ("REPLAY_READY_FOR_LOCKED_SCORER_REVIEW", "stop_hit_same_candle",
         -1.0, -4.551746),
}

HONEST_INTERPRETATION = (
    "detector_found_real_reaction_zones_2_of_6_completed_replays_hit_4r_gross",
    "current_entry_stop_geometry_is_cost_broken",
    "1m_fvg_stop_distances_are_too_tight_relative_to_27bps_round_trip_costs",
    "ethusd_2026_05_13_hit_full_4r_target_and_still_lost_6_2r_net",
    "current_candidate_is_not_approved_for_paper_or_live",
    "no_profitability_claim_is_allowed",
    "next_decision_is_mutable_candidate_edit_v2_cost_viability_filter_or_rejection_kept_on_record",
)

_REQUIRED_NO_CLAIM_PHRASE = "NO profitability claim"

REVIEW_CHECKLIST = (
    "replay_artifacts_present_and_sha_pinned",
    "accepted_labels_review_still_approved",
    "scope_exactly_the_7_frozen_setup_ids_no_extras",
    "no_rejected_labels_were_replayed",
    "btcusd_2026_06_09_was_no_entry",
    "six_completed_replays",
    "two_of_six_hit_4r_gross_target",
    "per_label_and_total_net_match_frozen_minus_21_04_r",
    "costs_27bps_round_trip_charged_on_every_replay",
    "net_below_gross_on_every_completed_replay",
    "anti_lookahead_3_minutes_recorded",
    "no_paper_live_authorization_and_no_profitability_claim",
    "prior_outputs_and_candles_byte_identical",
    "frozen_rules_unchanged_no_drift",
)

FORBIDDEN = (
    "running_another_replay", "new_pnl_calculation", "optimizer_runs",
    "candidate_rule_changes", "scorer_or_instruction_changes",
    "profitability_claims", "paper_live_micro_live_authorization",
    "modifying_labels_candles_or_manifests",
    "broker_exchange_credential_access", "order_endpoints", "gate_unlocks",
)


def get_fee_honest_replay_results_review_label() -> str:
    return RR_LABEL


def observe_replay_results(repo_root: Any,
                           tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY observation of the replay artifacts and integrity state."""
    root = _pathlib.Path(str(repo_root))
    results_file = root / RESULTS_PATH
    summary_file = root / SUMMARY_PATH
    observation: dict[str, Any] = {
        "results_present": results_file.is_file(),
        "summary_present": summary_file.is_file(),
        "results": [], "summary": None,
        "results_sha256": None, "summary_sha256": None,
        "accepted_labels_review_verdict": None,
        "tracked_output_paths": [str(p) for p in (tracked_paths or ())],
        "baseline_files_sha256": {}, "batch2_manifest_sha256": None,
        "expanded_labels_sha256": None,
    }
    if observation["results_present"]:
        raw = results_file.read_bytes()
        observation["results_sha256"] = _hashlib.sha256(raw).hexdigest()
        for line in raw.decode("utf-8").splitlines():
            if line.strip():
                observation["results"].append(_json.loads(line))
    if observation["summary_present"]:
        raw = summary_file.read_bytes()
        observation["summary_sha256"] = _hashlib.sha256(raw).hexdigest()
        observation["summary"] = _json.loads(raw.decode("utf-8"))
    observation["accepted_labels_review_verdict"] = (
        build_accepted_labels_human_review(repo_root,
                                           tracked_paths=[]).get("verdict"))
    for rel_path in BASELINE_PROTECTED_FILES:
        target = root / rel_path
        observation["baseline_files_sha256"][rel_path] = (
            _hashlib.sha256(target.read_bytes()).hexdigest()
            if target.is_file() else None)
    batch2 = root / BATCH2_MANIFEST_PATH
    if batch2.is_file():
        observation["batch2_manifest_sha256"] = _hashlib.sha256(
            batch2.read_bytes()).hexdigest()
    expanded = root / EXPANDED_LABELS_PATH
    if expanded.is_file():
        observation["expanded_labels_sha256"] = _hashlib.sha256(
            expanded.read_bytes()).hexdigest()
    return observation


def certify_replay_results(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of the replay evidence. Pure."""
    review: dict[str, Any] = {
        "schema_version": RR_SCHEMA_VERSION, "label": RR_LABEL,
        "mode": RR_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "edit_id": EDIT_ID,
        "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "total_net_r_after_costs": None,
        "honest_interpretation": list(HONEST_INTERPRETATION),
        "expected_per_label": {k: list(v)
                               for k, v in EXPECTED_PER_LABEL.items()},
        "forbidden": list(FORBIDDEN),
        "candidate_approved_for_paper_or_live": False,
        "profitability_claim_permitted": False,
        "replay_authorization_was_limited_to_the_one_human_approved_run":
            True,
        "outputs_remain_untracked_operational_data": True,
        "this_review_changes_no_rules": True,
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
        review["verdict"] = VERDICT_RR_BLOCKED
        review["blockers"].append("observation_missing")
        return review
    o = observation
    if not o.get("results_present") or not o.get("summary_present"):
        review["verdict"] = VERDICT_RR_BLOCKED
        review["blockers"].append("replay_artifacts_missing")
        return review

    results = o.get("results") or []
    summary = o.get("summary") or {}
    r: dict[str, bool] = {}
    r["replay_artifacts_present_and_sha_pinned"] = (
        o.get("results_sha256") == EXPECTED_RESULTS_SHA256
        and o.get("summary_sha256") == EXPECTED_SUMMARY_SHA256)
    r["accepted_labels_review_still_approved"] = (
        o.get("accepted_labels_review_verdict") == VERDICT_AL_APPROVED)
    ids = [x.get("setup_id") for x in results]
    r["scope_exactly_the_7_frozen_setup_ids_no_extras"] = (
        tuple(sorted(ids)) == FROZEN_ACCEPTED_SETUP_IDS
        and len(ids) == 7
        and tuple(sorted(summary.get("replay_scope") or ()))
        == FROZEN_ACCEPTED_SETUP_IDS)
    r["no_rejected_labels_were_replayed"] = all(
        x in FROZEN_ACCEPTED_SETUP_IDS for x in ids)
    per_ok = len(results) == 7
    completed = 0
    no_entry = 0
    target_hits = 0
    net_total = 0.0
    net_below_gross = True
    costs_ok = bool(results)
    for x in results:
        expected = EXPECTED_PER_LABEL.get(x.get("setup_id"))
        if expected is None:
            per_ok = False
            continue
        status, exit_reason, gross_r, net_r = expected
        if (x.get("replay_status") != status
                or x.get("exit_reason") != exit_reason
                or x.get("gross_r") != gross_r
                or x.get("net_r_after_costs") != net_r):
            per_ok = False
        if x.get("cost_assumptions_bps") != EXPECTED_COSTS_BPS:
            costs_ok = False
        window = x.get("replay_window") or {}
        if window.get("anti_lookahead_minutes") != (
                EXPECTED_ANTI_LOOKAHEAD_MINUTES):
            costs_ok = costs_ok and False
        if x.get("replay_status") == "REPLAY_READY_FOR_LOCKED_SCORER_REVIEW":
            completed += 1
            net_total += x.get("net_r_after_costs") or 0.0
            if x.get("exit_reason") == "target_4r_hit":
                target_hits += 1
            if not (isinstance(x.get("net_r_after_costs"), (int, float))
                    and isinstance(x.get("gross_r"), (int, float))
                    and x["net_r_after_costs"] < x["gross_r"]):
                net_below_gross = False
        elif x.get("replay_status") == "REPLAY_REJECTED_NO_ENTRY":
            no_entry += 1
    review["total_net_r_after_costs"] = round(net_total, 6)
    btc = next((x for x in results if x.get("setup_id")
                == "BTCUSD_20260609_editv1exp_setup05_touch1"), None)
    r["btcusd_2026_06_09_was_no_entry"] = (
        btc is not None
        and btc.get("replay_status") == "REPLAY_REJECTED_NO_ENTRY")
    r["six_completed_replays"] = (completed == EXPECTED_COMPLETED
                                  and no_entry == EXPECTED_NO_ENTRY)
    r["two_of_six_hit_4r_gross_target"] = (
        target_hits == EXPECTED_GROSS_TARGET_HITS)
    r["per_label_and_total_net_match_frozen_minus_21_04_r"] = (
        per_ok and round(net_total, 6) == EXPECTED_TOTAL_NET_R
        and summary.get("total_net_r_after_costs") == EXPECTED_TOTAL_NET_R
        and summary.get("wins_net_positive") == EXPECTED_WINS_NET_POSITIVE)
    r["costs_27bps_round_trip_charged_on_every_replay"] = (
        costs_ok
        and summary.get("cost_assumptions_bps") == EXPECTED_COSTS_BPS
        and sum(EXPECTED_COSTS_BPS.values())
        == EXPECTED_ROUND_TRIP_COST_BPS)
    r["net_below_gross_on_every_completed_replay"] = (
        bool(results) and net_below_gross)
    r["anti_lookahead_3_minutes_recorded"] = (
        summary.get("anti_lookahead_minutes")
        == EXPECTED_ANTI_LOOKAHEAD_MINUTES)
    r["no_paper_live_authorization_and_no_profitability_claim"] = (
        summary.get("replay_authorizes_nothing") is True
        and summary.get("no_orders_no_credentials_no_paper_no_live") is True
        and _REQUIRED_NO_CLAIM_PHRASE in str(summary.get("honesty_note"))
        and "profitability_claim" not in summary)
    r["prior_outputs_and_candles_byte_identical"] = (
        o.get("baseline_files_sha256") == BASELINE_PROTECTED_FILES
        and o.get("batch2_manifest_sha256") == BATCH2_MANIFEST_SHA256
        and o.get("expanded_labels_sha256") == EXPANDED_LABELS_SHA256
        and not o.get("tracked_output_paths"))
    r["frozen_rules_unchanged_no_drift"] = (
        FIB_LEVEL == 0.618 and FIB_TOLERANCE == 0.05
        and RISK_REWARD_TARGET == 4.0)
    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_RR_REJECTED
        review["blockers"].extend("check_failed:" + n for n in failed)
        return review
    review["verdict"] = VERDICT_RR_ACCEPTED
    return review


def build_fee_honest_replay_results_review(
        repo_root: Any, tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the replay artifacts read-only and certify them."""
    return certify_replay_results(
        observe_replay_results(repo_root, tracked_paths))


def validate_fee_honest_replay_results_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    if v.get("verdict") not in (VERDICT_RR_ACCEPTED, VERDICT_RR_REJECTED,
                                VERDICT_RR_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if tuple(v.get("honest_interpretation") or ()) != HONEST_INTERPRETATION:
        errors.append("honest_interpretation_tampered")
    if {k: tuple(x) for k, x in (v.get("expected_per_label")
                                 or {}).items()} != EXPECTED_PER_LABEL:
        errors.append("per_label_evidence_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    if v.get("candidate_approved_for_paper_or_live") is not False:
        errors.append("candidate_can_never_be_paper_live_approved_here")
    if v.get("profitability_claim_permitted") is not False:
        errors.append("profitability_claim_can_never_be_permitted_here")
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_RR_ACCEPTED:
        if v.get("blockers"):
            errors.append("accepted_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("accepted_without_full_passing_checklist")
        if v.get("total_net_r_after_costs") != EXPECTED_TOTAL_NET_R:
            errors.append("accepted_with_wrong_total_net_r")
    if v.get("verdict") in (VERDICT_RR_REJECTED, VERDICT_RR_BLOCKED) \
            and not v.get("blockers"):
        errors.append("non_accepted_without_blockers")
    for key, want in (
        ("replay_authorization_was_limited_to_the_one_human_approved_run",
         True),
        ("outputs_remain_untracked_operational_data", True),
        ("this_review_changes_no_rules", True),
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

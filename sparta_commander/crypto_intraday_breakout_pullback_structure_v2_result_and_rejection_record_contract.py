"""SPARTA BP V2 RESULT + FORMAL CANDIDATE #2 REJECTION RECORD
(READ-ONLY, EVIDENCE FREEZE, RUNS NOTHING).

The honest end of candidate #2. The one authorized experiment -- the 1h
SMA(20) trend filter -- worked as a filter (105 -> 64 survivors, hit rates
up, net/trade improved 16-40%) and still lost gross AND net in every
variant (25.0% vs 33.3% needed, 21.9% vs 25.0%, 17.2% vs 20.0%). Per the
pre-committed failure rule, candidate #2 is REJECTED_KEPT_ON_RECORD:
EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_EXPERIMENT. No further mutable
edits, no continuation, no paper/live, no profitability claims -- ever.
The BTC/SOL/long-side observations are preserved strictly as FUTURE
candidate-family seeds, never as rescue paths. Two candidates, two honest
deaths, zero money risked.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

from sparta_commander.crypto_intraday_breakout_pullback_structure_mutable_edit_v2_1h_trend_filter import (
    EDIT_BV2_ID,
    VERDICT_BV2_READY,
    build_bp_mutable_edit_v2,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_real_candle_detector_labels_review_contract import (
    EXPECTED_LABELS_SHA256,
    LABELS_PATH,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_replay_results_review_contract import (
    VERDICT_BPR2_FROZEN,
    build_bp_replay_results_review,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_strategy_spec_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
)
from sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review import (
    BASELINE_PROTECTED_FILES,
)

RJ2_SCHEMA_VERSION = (
    "crypto_intraday_breakout_pullback_structure_v2_result_and_rejection"
    "_record.v1")
RJ2_LABEL = ("SPARTA BP V2 Result + Candidate #2 Rejection Record "
             "(READ-ONLY, EVIDENCE FREEZE, REJECTED KEPT ON RECORD)")
RJ2_MODE = "RESEARCH_ONLY"
VERDICT_RJ2_RECORDED = (
    "BP_V2_RESULT_FROZEN_AND_CANDIDATE_2_REJECTED_KEPT_ON_RECORD")
VERDICT_RJ2_REVIEW_REJECTED = "BP_V2_REJECTION_RECORD_REVIEW_REJECTED"
VERDICT_RJ2_BLOCKED = "BP_V2_REJECTION_RECORD_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"

V2_RESULTS_PATH = ("data/breakout_pullback/v2_1h_filter/"
                   "bp_v2_replay_results_2026-05-12_2026-06-10.jsonl")
V2_SUMMARY_PATH = ("data/breakout_pullback/v2_1h_filter/"
                   "bp_v2_summary_2026-05-12_2026-06-10.json")
EXPECTED_V2_RESULTS_SHA256 = (
    "3a415c6da9002f5966da6cca6bc916caf4342cb1a10c4c0a8ec054fefab87a68")
EXPECTED_V2_SUMMARY_SHA256 = (
    "c61557d2b72e9ec2b5ebe03caa0624096e69c6324093ef2e73f970eaf45daee2")

EXPECTED_ATTEMPTS = 559
EXPECTED_BASE_ACCEPTED = 105
EXPECTED_V2_SURVIVORS = 64
EXPECTED_COST_BPS = 27.0
# Per-variant: (hits, stops, timeouts, gross, net, net_per_trade)
EXPECTED_V2_VARIANTS = {
    "2r": (16, 46, 2, -13.403583, -28.520186, -0.445628),
    "3r": (14, 48, 2, -5.403583, -20.520186, -0.320628),
    "4r": (11, 51, 2, -6.403583, -21.520186, -0.336253),
}
BREAKEVEN_TABLE = {
    "2r": {"needed": 1 / 3, "observed": 16 / 64},
    "3r": {"needed": 1 / 4, "observed": 14 / 64},
    "4r": {"needed": 1 / 5, "observed": 11 / 64},
}

REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
REJECTION_REASON = (
    "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_EXPERIMENT")
REJECTION_CONCLUSION = (
    "the 15m breakout-pullback-continuation signal lost gross and net in "
    "every variant both unfiltered (105 trades) and with the authorized 1h "
    "SMA(20) trend filter (64 trades); the filter improved results but hit "
    "rates stayed below gross breakeven; per the pre-committed failure "
    "rule the candidate is rejected")

FUTURE_SEEDS_NOT_RESCUE_PATHS = (
    "btc_was_net_positive_in_all_variants_small_sample",
    "sol_was_net_positive_at_3r_and_4r",
    "long_side_was_materially_stronger_than_shorts",
    "these_observations_seed_future_new_candidate_families_only_and_are"
    "_never_rescue_paths_for_candidate_2",
)

REVIEW_CHECKLIST = (
    "v2_artifacts_present_and_sha_pinned",
    "v2_edit_ready_and_replay_freeze_frozen",
    "counts_559_105_64_and_filter_only_proof",
    "survivors_unique_and_cost_27bps_on_every_trade",
    "per_variant_arithmetic_matches_frozen_table",
    "below_gross_breakeven_in_all_variants",
    "no_paper_live_or_profitability_claim",
    "prior_evidence_byte_identical",
    "candidate_1_rejection_preserved",
    "seeds_recorded_as_non_rescue_only",
)

FORBIDDEN = (
    "continuing_candidate_2_as_is",
    "another_mutable_edit_for_candidate_2",
    "new_detector_or_replay_runs", "scorer_or_optimizer_runs",
    "profitability_claims", "paper_live_micro_live_authorization",
    "using_seed_observations_to_rescue_candidate_2",
    "modifying_labels_candles_or_artifacts", "deleting_prior_outputs",
    "broker_exchange_credential_access",
    "trading_endpoints_of_any_kind", "gate_unlocks",
    "deleting_or_hiding_rejected_evidence",
)


def get_bp_v2_rejection_record_label() -> str:
    return RJ2_LABEL


def observe_bp_v2_result(repo_root: Any,
                         tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY observation of the V2 artifacts and evidence state."""
    root = _pathlib.Path(str(repo_root))
    results_file = root / V2_RESULTS_PATH
    summary_file = root / V2_SUMMARY_PATH
    observation: dict[str, Any] = {
        "results_present": results_file.is_file(),
        "summary_present": summary_file.is_file(),
        "results": [], "summary": None,
        "results_sha256": None, "summary_sha256": None,
        "labels_sha256": None,
        "v2_edit_verdict": None, "replay_freeze_verdict": None,
        "tracked_output_paths": [str(p) for p in (tracked_paths or ())],
        "baseline_files_sha256": {},
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
    labels_file = root / LABELS_PATH
    if labels_file.is_file():
        observation["labels_sha256"] = _hashlib.sha256(
            labels_file.read_bytes()).hexdigest()
    observation["v2_edit_verdict"] = build_bp_mutable_edit_v2(
        repo_root).get("verdict")
    observation["replay_freeze_verdict"] = build_bp_replay_results_review(
        repo_root, tracked_paths=[]).get("verdict")
    for rel_path in BASELINE_PROTECTED_FILES:
        target = root / rel_path
        observation["baseline_files_sha256"][rel_path] = (
            _hashlib.sha256(target.read_bytes()).hexdigest()
            if target.is_file() else None)
    return observation


def certify_bp_v2_rejection(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of the V2 result + formal rejection."""
    record: dict[str, Any] = {
        "schema_version": RJ2_SCHEMA_VERSION, "label": RJ2_LABEL,
        "mode": RJ2_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "edit_id": EDIT_BV2_ID,
        "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "rejection_status": REJECTION_STATUS,
        "rejection_reason": REJECTION_REASON,
        "rejection_conclusion": REJECTION_CONCLUSION,
        "expected_v2_variants": {k: list(v)
                                 for k, v in EXPECTED_V2_VARIANTS.items()},
        "breakeven_table": {k: dict(v) for k, v in BREAKEVEN_TABLE.items()},
        "future_seeds_not_rescue_paths": list(
            FUTURE_SEEDS_NOT_RESCUE_PATHS),
        "forbidden": list(FORBIDDEN),
        "candidate_2_may_continue_as_is": False,
        "candidate_2_may_receive_another_mutable_edit": False,
        "candidate_approved_for_paper_or_live": False,
        "profitability_claim_permitted": False,
        "evidence_deleted_or_hidden": False,
        "rejected_evidence_kept_on_record": True,
        "outputs_remain_untracked_operational_data": True,
        "this_record_changes_no_rules": True,
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
        record["verdict"] = VERDICT_RJ2_BLOCKED
        record["blockers"].append("observation_missing")
        return record
    o = observation
    if not o.get("results_present") or not o.get("summary_present"):
        record["verdict"] = VERDICT_RJ2_BLOCKED
        record["blockers"].append("v2_artifacts_missing")
        return record

    results = o.get("results") or []
    summary = o.get("summary") or {}
    proof = summary.get("filter_only_proof") or {}
    r: dict[str, bool] = {}
    r["v2_artifacts_present_and_sha_pinned"] = (
        o.get("results_sha256") == EXPECTED_V2_RESULTS_SHA256
        and o.get("summary_sha256") == EXPECTED_V2_SUMMARY_SHA256)
    r["v2_edit_ready_and_replay_freeze_frozen"] = (
        o.get("v2_edit_verdict") == VERDICT_BV2_READY
        and o.get("replay_freeze_verdict") == VERDICT_BPR2_FROZEN)
    r["counts_559_105_64_and_filter_only_proof"] = (
        summary.get("attempts_total") == EXPECTED_ATTEMPTS
        and summary.get("base_accepted") == EXPECTED_BASE_ACCEPTED
        and summary.get("v2_survivors") == EXPECTED_V2_SURVIVORS
        and len(results) == EXPECTED_V2_SURVIVORS
        and proof.get("attempts_lte_559") is True
        and proof.get("survivors_lte_105") is True
        and proof.get("survivors_subset_of_frozen_105") is True)
    r["survivors_unique_and_cost_27bps_on_every_trade"] = (
        len({x.get("setup_id") for x in results})
        == EXPECTED_V2_SURVIVORS
        and bool(results)
        and all(x.get("cost_bps_charged") == EXPECTED_COST_BPS
                for x in results))
    recomputed_ok = bool(results)
    below_breakeven = True
    for name, (hits, stops, timeouts, gross, net, mean) in (
            EXPECTED_V2_VARIANTS.items()):
        h = s = t = 0
        g = n = 0.0
        for x in results:
            v = (x.get("variants") or {}).get(name) or {}
            reason = v.get("exit_reason")
            if reason == "target_hit":
                h += 1
            elif reason in ("stop_hit", "stop_gap_open"):
                s += 1
            elif reason == "timeout_end_of_data":
                t += 1
            g += v.get("gross_r", 0.0)
            n += v.get("net_r_after_costs", 0.0)
        if (h, s, t) != (hits, stops, timeouts) \
                or abs(g - gross) > 0.001 or abs(n - net) > 0.001 \
                or abs(n / max(len(results), 1) - mean) > 0.001:
            recomputed_ok = False
        if len(results) and h / len(results) >= BREAKEVEN_TABLE[name][
                "needed"]:
            below_breakeven = False
        if g >= 0:
            below_breakeven = False
    r["per_variant_arithmetic_matches_frozen_table"] = recomputed_ok
    r["below_gross_breakeven_in_all_variants"] = (
        below_breakeven and recomputed_ok)
    r["no_paper_live_or_profitability_claim"] = (
        summary.get("replay_authorizes_nothing") is True
        and summary.get("no_orders_no_credentials_no_paper_no_live") is True
        and "NO profitability claim" in str(summary.get("honesty_note"))
        and "profitability_claim" not in summary)
    r["prior_evidence_byte_identical"] = (
        o.get("baseline_files_sha256") == BASELINE_PROTECTED_FILES
        and o.get("labels_sha256") == EXPECTED_LABELS_SHA256
        and not o.get("tracked_output_paths"))
    try:
        from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
            REJECTION_REASON as C1_REASON,
            REJECTION_STATUS as C1_STATUS)
        r["candidate_1_rejection_preserved"] = (
            C1_STATUS == "REJECTED_KEPT_ON_RECORD"
            and C1_REASON == "COST_NON_VIABLE_RISK_GEOMETRY")
    except ImportError:
        r["candidate_1_rejection_preserved"] = False
    r["seeds_recorded_as_non_rescue_only"] = (
        "these_observations_seed_future_new_candidate_families_only_and"
        "_are_never_rescue_paths_for_candidate_2"
        in FUTURE_SEEDS_NOT_RESCUE_PATHS)
    record["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        record["verdict"] = VERDICT_RJ2_REVIEW_REJECTED
        record["blockers"].extend("check_failed:" + n for n in failed)
        return record
    record["verdict"] = VERDICT_RJ2_RECORDED
    return record


def build_bp_v2_rejection_record(repo_root: Any,
                                 tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the V2 result read-only and certify the rejection record."""
    return certify_bp_v2_rejection(
        observe_bp_v2_result(repo_root, tracked_paths))


def validate_bp_v2_rejection_record(record: Any) -> dict[str, Any]:
    """Validate the record's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    v = record
    if v.get("verdict") not in (VERDICT_RJ2_RECORDED,
                                VERDICT_RJ2_REVIEW_REJECTED,
                                VERDICT_RJ2_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if v.get("rejection_status") != REJECTION_STATUS:
        errors.append("rejection_status_tampered")
    if v.get("rejection_reason") != REJECTION_REASON:
        errors.append("rejection_reason_tampered")
    if v.get("rejection_conclusion") != REJECTION_CONCLUSION:
        errors.append("rejection_conclusion_tampered")
    if {k: tuple(x) for k, x in (v.get("expected_v2_variants")
                                 or {}).items()} != EXPECTED_V2_VARIANTS:
        errors.append("variant_evidence_tampered")
    if tuple(v.get("future_seeds_not_rescue_paths") or ()) != (
            FUTURE_SEEDS_NOT_RESCUE_PATHS):
        errors.append("seed_observations_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    for key in ("candidate_2_may_continue_as_is",
                "candidate_2_may_receive_another_mutable_edit",
                "candidate_approved_for_paper_or_live",
                "profitability_claim_permitted",
                "evidence_deleted_or_hidden"):
        if v.get(key) is not False:
            errors.append("must_be_false_forever:" + key)
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_RJ2_RECORDED:
        if v.get("blockers"):
            errors.append("recorded_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("recorded_without_full_passing_checklist")
    if v.get("verdict") in (VERDICT_RJ2_REVIEW_REJECTED,
                            VERDICT_RJ2_BLOCKED) and not v.get("blockers"):
        errors.append("non_recorded_without_blockers")
    for key, want in (
        ("rejected_evidence_kept_on_record", True),
        ("outputs_remain_untracked_operational_data", True),
        ("this_record_changes_no_rules", True),
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

"""SPARTA BREAKOUT-PULLBACK FEE-HONEST REPLAY RESULTS REVIEW
(READ-ONLY, EVIDENCE FREEZE, CANDIDATE #2 REJECTED AS-IS).

The arithmetic, frozen: 105 floor-clearing setups replayed at 27 bps with
anti-lookahead and conservative ordering -- and every variant lost GROSS
(2R: 22.9% hits vs 33.3% needed; 3R: 17.1% vs 25.0%; 4R: 12.4% vs 20.0%).
Net: -55.61R / -55.61R / -62.61R. This is an EDGE failure, not a cost
failure: candidate #1 died of costs, candidate #2 dies of signal. The
candidate is REJECTED AS-IS -- not paper approved, not live approved, not
scalable. ONE mutable V2 experiment is authorized: the 1h trend filter the
original concept specified but the detector never implemented (a stricter
filter, not curve-fit loosening). Fail again -> rejection kept on record.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

from sparta_commander.crypto_intraday_breakout_pullback_structure_real_candle_detector_labels_review_contract import (
    EXPECTED_LABELS_SHA256,
    LABELS_PATH,
    VERDICT_BPL_ACCEPTED,
    build_bp_detector_labels_review,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_strategy_spec_contract import (
    CANDIDATE_ID,
)
from sparta_commander.ny_session_fvg_choch_additional_session_days_staged_candles_review import (
    BASELINE_PROTECTED_FILES,
)

BPR2_SCHEMA_VERSION = (
    "crypto_intraday_breakout_pullback_structure_replay_results_review.v1")
BPR2_LABEL = ("SPARTA Breakout-Pullback Replay Results Review (READ-ONLY, "
              "EVIDENCE FREEZE, NO PROFITABILITY CLAIM PERMITTED)")
BPR2_MODE = "RESEARCH_ONLY"
VERDICT_BPR2_FROZEN = (
    "BP_REPLAY_RESULTS_FROZEN_CANDIDATE_REJECTED_AS_IS")
VERDICT_BPR2_REVIEW_REJECTED = "BP_REPLAY_RESULTS_REVIEW_REJECTED"
VERDICT_BPR2_BLOCKED = "BP_REPLAY_RESULTS_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_BP_MUTABLE_V2_1H_TREND_FILTER_EDIT"

RESULTS_PATH = ("data/breakout_pullback/replay_results/"
                "bp_replay_results_2026-05-12_2026-06-10.jsonl")
SUMMARY_PATH = ("data/breakout_pullback/replay_results/"
                "bp_replay_summary_2026-05-12_2026-06-10.json")
EXPECTED_RESULTS_SHA256 = (
    "9757cdda22b7dc0ad41e48d803df192dbe510c8af08ae4cb478197ad59e98806")
EXPECTED_SUMMARY_SHA256 = (
    "b7db4819c9c7506e73dd9a7068733f93d1bc9c43e208162b40d5059d69b4d1f4")
EXPECTED_SCOPE_SHA256 = (
    "0070968cbaac7dbaf53edf1debdd9210f54fe74240d8641405b6f77a3dbab23a")

EXPECTED_TRADES = 105
EXPECTED_COST_BPS = 27.0
# Per-variant frozen arithmetic: (target_hits, stop_exits, timeouts,
#                                 gross_r_total, net_r_total_after_costs)
EXPECTED_VARIANTS = {
    "2r": (24, 79, 2, -30.403584, -55.607231),
    "3r": (18, 85, 2, -30.403583, -55.60723),
    "4r": (13, 90, 2, -37.403583, -62.60723),
}
# Breakeven GROSS win rates vs observed hit rates (the decisive line).
BREAKEVEN_TABLE = {
    "2r": {"needed_gross_win_rate": 1 / 3, "observed_hit_rate": 24 / 105},
    "3r": {"needed_gross_win_rate": 1 / 4, "observed_hit_rate": 18 / 105},
    "4r": {"needed_gross_win_rate": 1 / 5, "observed_hit_rate": 13 / 105},
}

REJECTION_AS_IS_STATUS = "REJECTED_AS_IS_PENDING_ONE_V2_EXPERIMENT"
FAILURE_CLASSIFICATION = "EDGE_FAILURE_NOT_COST_FAILURE"

HONEST_INTERPRETATION = (
    "every_variant_lost_gross_before_costs_the_signal_has_no_edge_in_this"
    "_sample",
    "observed_hit_rates_22_9_17_1_12_4_pct_vs_gross_breakeven_33_3_25_0"
    "_20_0_pct",
    "the_cost_geometry_fix_worked_costs_added_only_about_0_24r_per_trade",
    "candidate_1_died_of_costs_candidate_2_dies_of_signal_both_caught"
    "_before_real_money",
    "the_original_concept_specified_1h_context_but_the_detector_was_15m"
    "_only",
    "one_v2_experiment_authorized_add_the_1h_trend_filter_a_stricter"
    "_filter_not_loosening",
    "if_v2_also_fails_fee_honest_replay_the_candidate_is_rejected_and"
    "_kept_on_record",
)

REVIEW_CHECKLIST = (
    "replay_artifacts_present_and_sha_pinned",
    "labels_review_still_accepted_and_labels_sha_pinned",
    "scope_was_exactly_the_105_frozen_setup_ids",
    "cost_27bps_charged_on_every_trade",
    "per_variant_arithmetic_matches_frozen_table",
    "gross_negative_in_all_variants_edge_failure",
    "hit_rates_below_gross_breakeven_in_all_variants",
    "anti_lookahead_and_conservative_rules_recorded",
    "no_paper_live_authorization_and_no_profitability_claim",
    "prior_evidence_byte_identical",
    "candidate_1_rejection_preserved",
    "one_v2_experiment_scope_recorded",
)

FORBIDDEN = (
    "another_replay_run", "scorer_runs", "optimizer_runs",
    "continuing_candidate_2_as_is", "profitability_claims",
    "paper_live_micro_live_authorization",
    "modifying_labels_candles_or_artifacts", "deleting_prior_outputs",
    "broker_exchange_credential_access",
    "trading_endpoints_of_any_kind", "gate_unlocks",
    "deleting_or_hiding_candidate_1_rejected_evidence",
)


def get_bp_replay_results_review_label() -> str:
    return BPR2_LABEL


def observe_bp_replay_results(repo_root: Any,
                              tracked_paths: Any = ()) -> dict[str, Any]:
    """READ-ONLY observation of the replay artifacts and evidence state."""
    root = _pathlib.Path(str(repo_root))
    results_file = root / RESULTS_PATH
    summary_file = root / SUMMARY_PATH
    observation: dict[str, Any] = {
        "results_present": results_file.is_file(),
        "summary_present": summary_file.is_file(),
        "results": [], "summary": None,
        "results_sha256": None, "summary_sha256": None,
        "labels_sha256": None, "labels_review_verdict": None,
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
    observation["labels_review_verdict"] = build_bp_detector_labels_review(
        repo_root, tracked_paths=[]).get("verdict")
    for rel_path in BASELINE_PROTECTED_FILES:
        target = root / rel_path
        observation["baseline_files_sha256"][rel_path] = (
            _hashlib.sha256(target.read_bytes()).hexdigest()
            if target.is_file() else None)
    return observation


def certify_bp_replay_results(observation: Any) -> dict[str, Any]:
    """DETERMINISTIC certification of the replay evidence. Pure."""
    review: dict[str, Any] = {
        "schema_version": BPR2_SCHEMA_VERSION, "label": BPR2_LABEL,
        "mode": BPR2_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "verdict": None, "blockers": [],
        "checklist": list(REVIEW_CHECKLIST), "checklist_results": {},
        "rejection_as_is_status": REJECTION_AS_IS_STATUS,
        "failure_classification": FAILURE_CLASSIFICATION,
        "expected_variants": {k: list(v)
                              for k, v in EXPECTED_VARIANTS.items()},
        "breakeven_table": {k: dict(v)
                            for k, v in BREAKEVEN_TABLE.items()},
        "honest_interpretation": list(HONEST_INTERPRETATION),
        "one_v2_experiment_scope": "add_1h_trend_filter_only",
        "forbidden": list(FORBIDDEN),
        "candidate_approved_for_paper_or_live": False,
        "profitability_claim_permitted": False,
        "candidate_2_may_continue_as_is": False,
        "candidate_1_evidence_kept_on_record": True,
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
        review["verdict"] = VERDICT_BPR2_BLOCKED
        review["blockers"].append("observation_missing")
        return review
    o = observation
    if not o.get("results_present") or not o.get("summary_present"):
        review["verdict"] = VERDICT_BPR2_BLOCKED
        review["blockers"].append("replay_artifacts_missing")
        return review

    results = o.get("results") or []
    summary = o.get("summary") or {}
    r: dict[str, bool] = {}
    r["replay_artifacts_present_and_sha_pinned"] = (
        o.get("results_sha256") == EXPECTED_RESULTS_SHA256
        and o.get("summary_sha256") == EXPECTED_SUMMARY_SHA256)
    r["labels_review_still_accepted_and_labels_sha_pinned"] = (
        o.get("labels_review_verdict") == VERDICT_BPL_ACCEPTED
        and o.get("labels_sha256") == EXPECTED_LABELS_SHA256)
    r["scope_was_exactly_the_105_frozen_setup_ids"] = (
        len(results) == EXPECTED_TRADES
        and len({x.get("setup_id") for x in results}) == EXPECTED_TRADES
        and summary.get("scope_sha256_of_sorted_ids")
        == EXPECTED_SCOPE_SHA256
        and summary.get("labels_replayed") == EXPECTED_TRADES)
    r["cost_27bps_charged_on_every_trade"] = bool(results) and all(
        x.get("cost_bps_charged") == EXPECTED_COST_BPS for x in results)
    # recompute the per-variant arithmetic from the raw records
    recomputed_ok = bool(results)
    gross_negative = True
    for name, (hits, stops, timeouts, gross, net) in (
            EXPECTED_VARIANTS.items()):
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
                or abs(g - gross) > 0.001 or abs(n - net) > 0.001:
            recomputed_ok = False
        if g >= 0:
            gross_negative = False
    r["per_variant_arithmetic_matches_frozen_table"] = recomputed_ok
    r["gross_negative_in_all_variants_edge_failure"] = (
        gross_negative and recomputed_ok)
    r["hit_rates_below_gross_breakeven_in_all_variants"] = all(
        row["observed_hit_rate"] < row["needed_gross_win_rate"]
        for row in BREAKEVEN_TABLE.values())
    r["anti_lookahead_and_conservative_rules_recorded"] = (
        "anti-lookahead" in str(summary.get("entry_model"))
        and "stop before target" in str(summary.get("conservative_rules")))
    r["no_paper_live_authorization_and_no_profitability_claim"] = (
        summary.get("replay_authorizes_nothing") is True
        and summary.get("no_orders_no_credentials_no_paper_no_live") is True
        and "NO profitability claim" in str(summary.get("honesty_note"))
        and "profitability_claim" not in summary)
    r["prior_evidence_byte_identical"] = (
        o.get("baseline_files_sha256") == BASELINE_PROTECTED_FILES
        and not o.get("tracked_output_paths"))
    try:
        from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
            REJECTION_REASON, REJECTION_STATUS)
        r["candidate_1_rejection_preserved"] = (
            REJECTION_STATUS == "REJECTED_KEPT_ON_RECORD"
            and REJECTION_REASON == "COST_NON_VIABLE_RISK_GEOMETRY")
    except ImportError:
        r["candidate_1_rejection_preserved"] = False
    r["one_v2_experiment_scope_recorded"] = (
        review["one_v2_experiment_scope"] == "add_1h_trend_filter_only")
    review["checklist_results"] = r
    failed = [name for name, ok in r.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_BPR2_REVIEW_REJECTED
        review["blockers"].extend("check_failed:" + n for n in failed)
        return review
    review["verdict"] = VERDICT_BPR2_FROZEN
    return review


def build_bp_replay_results_review(repo_root: Any,
                                   tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe the replay artifacts read-only and certify them."""
    return certify_bp_replay_results(
        observe_bp_replay_results(repo_root, tracked_paths))


def validate_bp_replay_results_review(review: Any) -> dict[str, Any]:
    """Validate the review's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    v = review
    if v.get("verdict") not in (VERDICT_BPR2_FROZEN,
                                VERDICT_BPR2_REVIEW_REJECTED,
                                VERDICT_BPR2_BLOCKED):
        errors.append("bad_verdict")
    if v.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if tuple(v.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")
    if v.get("rejection_as_is_status") != REJECTION_AS_IS_STATUS:
        errors.append("rejection_status_tampered")
    if v.get("failure_classification") != FAILURE_CLASSIFICATION:
        errors.append("failure_classification_tampered")
    if {k: tuple(x) for k, x in (v.get("expected_variants")
                                 or {}).items()} != EXPECTED_VARIANTS:
        errors.append("variant_evidence_tampered")
    if tuple(v.get("honest_interpretation") or ()) != HONEST_INTERPRETATION:
        errors.append("honest_interpretation_tampered")
    if v.get("one_v2_experiment_scope") != "add_1h_trend_filter_only":
        errors.append("v2_experiment_scope_tampered")
    if tuple(v.get("forbidden") or ()) != FORBIDDEN:
        errors.append("forbidden_list_weakened")
    for key in ("candidate_approved_for_paper_or_live",
                "profitability_claim_permitted",
                "candidate_2_may_continue_as_is"):
        if v.get(key) is not False:
            errors.append("must_be_false_forever:" + key)
    results = v.get("checklist_results") or {}
    if v.get("verdict") == VERDICT_BPR2_FROZEN:
        if v.get("blockers"):
            errors.append("frozen_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST) or not all(
                results.get(n) is True for n in REVIEW_CHECKLIST):
            errors.append("frozen_without_full_passing_checklist")
    if v.get("verdict") in (VERDICT_BPR2_REVIEW_REJECTED,
                            VERDICT_BPR2_BLOCKED) and not v.get("blockers"):
        errors.append("non_frozen_without_blockers")
    for key, want in (
        ("candidate_1_evidence_kept_on_record", True),
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

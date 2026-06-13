"""SPARTA CANDIDATE #5 FORMAL REJECTION RECORD (READ-ONLY, RESEARCH
ONLY): ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION_V1.

THE LEDGER ENTRY: Candidate #5 is REJECTED_KEPT_ON_RECORD, reason
SMALL_SAMPLE_NET_NEGATIVE_AND_EDIT_ADDED_NOTHING.

The fee-honest replay of the 6 frozen labels was net-negative in every
variant on only 5 kept trades, and the single authorized structure-only
edit (pullback max 6 -> 10 bars) added ZERO new accepted setups -- the
most conclusive edit failure possible, because it cleanly rules out the
window-length hypothesis: the converted structures simply did not
resume. The edit allowance is now SPENT.

Honest evidence notes, frozen: C5 was the FIRST family of five to show
gross-positive 2R before fees (40.0% hit rate vs 33.3% breakeven) -- but
on 5 kept trades, with fees turning it negative, 4R gross-flat, ETH
contributing only losses, SOL's positive contribution concentrated in
one week, and the dedup rule removing a winner. Information, never a
claim.

Frozen consequences (validator-permanent): candidate #5 may not continue
as-is; may not receive another edit; further replays are not authorized;
no paper, no live, no profitability claim, no winner wording. Seeds are
preserved STRICTLY for future families and are never rescue paths.

This module observes the untracked edit artifacts READ-ONLY, re-verifies
every sha (edit AND baseline), recomputes the baseline-vs-edit facts
from the artifacts themselves, and certifies the frozen record. It runs
nothing, fetches nothing, and authorizes nothing.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.eth_sol_relative_strength_pullback_continuation_family_proposal_contract import (
    CANDIDATE_ID,
)
from sparta_commander.eth_sol_relative_strength_real_candle_labels_review_contract import (
    EXPECTED_LABELS_SHA256 as BASELINE_LABELS_SHA256,
    EXPECTED_SUMMARY_SHA256 as BASELINE_LABELS_SUMMARY_SHA256,
    LABELS_PATH as BASELINE_LABELS_PATH,
)
from sparta_commander.eth_sol_relative_strength_replay_results_review_contract import (
    EXPECTED_RESULTS_SHA256 as BASELINE_REPLAY_SHA256,
    EXPECTED_SETUP_IDS as BASELINE_ACCEPTED_IDS,
    EXPECTED_SUMMARY_SHA256 as BASELINE_REPLAY_SUMMARY_SHA256,
    VERDICT_C5RR_FROZEN,
    build_c5_replay_results_review,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)

RJ5_SCHEMA_VERSION = (
    "eth_sol_relative_strength_rejection_record.v1")
RJ5_LABEL = ("SPARTA Candidate #5 Formal Rejection Record "
             "(READ-ONLY, RESEARCH ONLY, REJECTED KEPT ON RECORD, "
             "NOT A PROFITABILITY CLAIM)")
RJ5_MODE = "RESEARCH_ONLY"
VERDICT_RJ5_RECORDED = (
    "C5_REJECTED_KEPT_ON_RECORD_SMALL_SAMPLE_NET_NEGATIVE_AND_EDIT"
    "_ADDED_NOTHING")
VERDICT_RJ5_REVIEW_REJECTED = "C5_REJECTION_RECORD_REVIEW_REJECTED"
VERDICT_RJ5_BLOCKED = "C5_REJECTION_RECORD_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"

REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
REJECTION_REASON = (
    "SMALL_SAMPLE_NET_NEGATIVE_AND_EDIT_ADDED_NOTHING")
EDIT_CLASSIFICATION = "C5_EDIT_V1_TRIGGER_WINDOW_FAILED_REJECT_NEXT"
REPLAY_REVIEW_CLASSIFICATION = (
    "C5_REPLAY_SMALL_SAMPLE_NEGATIVE_REJECT_OR_EDIT_DECISION")

HEAD_AT_EDIT_EVALUATION = "24c0cb8eaf9fd735c84e057c0151485fd5e1b012"
EDIT_RUNNER_PATH = "tools/c5_edit_v1_trigger_window_eval_once.py"
EDIT_LABELS_PATH = ("data/relative_strength_c5/edit_v1/"
                    "c5_edit_v1_labels_2026-05-02_2026-06-10.jsonl")
EDIT_REPLAY_PATH = ("data/relative_strength_c5/edit_v1/"
                    "c5_edit_v1_replay_2026-05-02_2026-06-10.jsonl")
EDIT_SUMMARY_PATH = ("data/relative_strength_c5/edit_v1/"
                     "c5_edit_v1_summary_2026-05-02_2026-06-10.json")
EXPECTED_EDIT_LABELS_SHA256 = (
    "cde44fd9b17358c5936fe511689bc6be16ecf73cfc387ffce3239e4b34366aa4")
EXPECTED_EDIT_REPLAY_SHA256 = (
    "ce21e8b36069d1ab8cc1eefdda5a665d7bd155f412b02c3aa68b7276a73a6ab6")
EXPECTED_EDIT_SUMMARY_SHA256 = (
    "5390d3d0082c7382c5c03a8bacd413de5a90a9e266511efe7986916a05eee537")

EXPECTED_BASELINE_VS_EDIT = {
    "baseline_attempts": 411, "edit_attempts": 406,
    "baseline_accepted": 6, "edit_accepted": 6,
    "edit_accepted_set_identical_to_baseline": True,
    "new_accepted_ids": (),
    "original_6_still_accepted_byte_identical": True,
    "baseline_pullback_too_long": 372,
    "edit_pullback_too_long": 365,
    "too_long_rejections_converted_by_window_extension": 7,
    "converted_rejections_became_accepted": 0,
}

FROZEN_EDIT_FACTS = (
    "edit type: structure-only trigger-window extension",
    "single authorized edit allowance was spent",
    "edit changed exactly one parameter: pullback_max_bars 6 to 10",
    "pullback minimum stayed 2",
    "rs gate unchanged; fee floor unchanged; target variants "
    "unchanged; wider-stop rule unchanged; same-symbol non-overlap "
    "unchanged; symbols ethusd/solusd only; long-only",
    "no fetch; no baseline artifact modification; no staged-data "
    "modification; scanner constant restored to 6 after run",
    "baseline drift-proof reproduced the frozen baseline: attempts "
    "411, accepted 6, pullback_too_long 372, exact frozen accepted "
    "setup_ids",
)

FROZEN_FAILURE_EXPLANATION = (
    "converted structures did not close above the pullback high",
    "some dissolved into rs_not_stronger",
    "some dissolved into below_up_leg_low",
    "some became later or merged too_long emissions",
    "scarcity is not the 6-bar window length; the structures simply "
    "do not resume",
)

EXPECTED_EDIT_REPLAY_VARIANTS = {
    "2r": {"kept": 5, "removed": 1, "hits": 2, "stops": 3,
           "timeouts": 0, "gross_r": 1.000001, "net_r": -0.269641},
    "3r": {"kept": 5, "removed": 1, "hits": 1, "stops": 4,
           "timeouts": 0, "gross_r": -0.999999, "net_r": -2.269641},
    "4r": {"kept": 5, "removed": 1, "hits": 1, "stops": 4,
           "timeouts": 0, "gross_r": 0.000001, "net_r": -1.269641},
}
EXPECTED_REMOVED_SETUP_ID = "SOLUSD_2026-05-06T06:00:00Z"

FROZEN_EDIT_REPLAY_FACTS = (
    "replay result is identical to the frozen baseline replay",
    "same 6 labels; same 5 kept / 1 removed after non-overlap; same "
    "removed setup solusd_2026-05-06t06:00",
    "same best/worst trades",
    "same eth negative contribution: 3 trades, 0 hits, -3.861515r",
    "same sol concentration: 2 kept trades, positive contribution "
    "concentrated in one week",
)

REJECTION_FACTS = (
    "candidate #5 is rejected",
    "rejection is kept on record",
    "reason: small sample, all variants net-negative after fee-honest "
    "replay, and the only authorized edit added zero new accepted "
    "setups",
    "the edit allowance is now spent",
    "candidate #5 may not continue as-is",
    "candidate #5 may not receive another edit",
    "further replays are not authorized",
    "no paper approval",
    "no live approval",
    "no profitability claim permitted",
    "no winner wording permitted",
)

EVIDENCE_NOTES = (
    "c5 was the first family to show gross-positive 2r before fees, "
    "but only on 5 kept trades",
    "fees turned 2r negative",
    "4r was gross-flat and net-negative",
    "eth contributed only losses",
    "sol showed concentrated positive contribution but too small and "
    "too concentrated",
    "dedup removed a winner, showing the honest cost of non-overlap",
    "trigger-window extension did not solve scarcity",
)

SEEDS_FOR_FUTURE_FAMILIES_ONLY = (
    "sol_side_relative_strength_recurrence_across_c4_and_c5_can"
    "_inspire_new_hypotheses_only",
    "fee_sensitivity_on_thin_risk_setups_must_be_filtered_earlier",
    "trigger_resumption_scarcity_is_a_structural_lesson",
    "same_symbol_non_overlap_can_remove_winners_and_should_be"
    "_evaluated_carefully",
    "eth_side_underperformance_in_this_sample_is_not_edge_evidence",
    "do_not_reuse_c5_as_is",
    "any_future_candidate_must_be_a_new_clean_hypothesis_through_the"
    "_autopilot_loop",
)
SEEDS_ARE_NEVER_RESCUE_PATHS = True


def get_c5_rejection_record_label() -> str:
    return RJ5_LABEL


def observe_c5_edit_result(repo_root: Any,
                           tracked_paths: Any = ()) -> dict[str, Any]:
    """Read the edit artifacts READ-ONLY, re-verify all shas (edit and
    baseline), and recompute the baseline-vs-edit facts. Never raises on
    missing files."""
    observation: dict[str, Any] = {
        "edit_artifacts_exist": False,
        "edit_labels_sha256": None, "edit_replay_sha256": None,
        "edit_summary_sha256": None,
        "baseline_labels_sha_ok": None,
        "baseline_replay_sha_ok": None,
        "baseline_vs_edit": None, "failure_statuses_present": None,
        "edit_replay_variants": None, "removed_setup_ids": None,
        "edit_classification": None,
        "original_6_byte_identical": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/") for p in (tracked_paths or ())}
    for rel in (EDIT_LABELS_PATH, EDIT_REPLAY_PATH, EDIT_SUMMARY_PATH,
                EDIT_RUNNER_PATH):
        if rel in tracked:
            observation["artifacts_tracked_in_git"].append(rel)
    edit_labels_file = root / EDIT_LABELS_PATH
    edit_replay_file = root / EDIT_REPLAY_PATH
    edit_summary_file = root / EDIT_SUMMARY_PATH
    if not (edit_labels_file.is_file() and edit_replay_file.is_file()
            and edit_summary_file.is_file()):
        return observation
    observation["edit_artifacts_exist"] = True
    raw_labels = edit_labels_file.read_bytes()
    raw_replay = edit_replay_file.read_bytes()
    raw_summary = edit_summary_file.read_bytes()
    observation["edit_labels_sha256"] = _hashlib.sha256(
        raw_labels).hexdigest()
    observation["edit_replay_sha256"] = _hashlib.sha256(
        raw_replay).hexdigest()
    observation["edit_summary_sha256"] = _hashlib.sha256(
        raw_summary).hexdigest()
    baseline_labels_file = root / BASELINE_LABELS_PATH
    observation["baseline_labels_sha_ok"] = (
        baseline_labels_file.is_file()
        and _hashlib.sha256(baseline_labels_file.read_bytes()
                            ).hexdigest() == BASELINE_LABELS_SHA256)
    baseline_replay_file = root / (
        "data/relative_strength_c5/replay_results/"
        "c5_replay_results_2026-05-02_2026-06-10.jsonl")
    observation["baseline_replay_sha_ok"] = (
        baseline_replay_file.is_file()
        and _hashlib.sha256(baseline_replay_file.read_bytes()
                            ).hexdigest() == BASELINE_REPLAY_SHA256)
    summary = _json.loads(raw_summary.decode("utf-8"))
    observation["edit_classification"] = summary.get("classification")
    baseline_block = summary.get("baseline") or {}
    edit_block = summary.get("edit_v1") or {}
    edit_accepted_ids = tuple(sorted(
        edit_block.get("accepted_setup_ids") or ()))
    observation["baseline_vs_edit"] = {
        "baseline_attempts": baseline_block.get("attempts"),
        "edit_attempts": edit_block.get("attempts"),
        "baseline_accepted": baseline_block.get("accepted"),
        "edit_accepted": edit_block.get("accepted"),
        "edit_accepted_set_identical_to_baseline": (
            edit_accepted_ids == tuple(sorted(BASELINE_ACCEPTED_IDS))),
        "new_accepted_ids": tuple(
            summary.get("new_accepted_setup_ids") or ()),
        "original_6_still_accepted_byte_identical": None,  # below
        "baseline_pullback_too_long": (
            baseline_block.get("status_breakdown") or {}).get(
            "rejected_pullback_too_long"),
        "edit_pullback_too_long": (
            edit_block.get("status_breakdown") or {}).get(
            "rejected_pullback_too_long"),
        "too_long_rejections_converted_by_window_extension": None,
        "converted_rejections_became_accepted": None,
    }
    bve = observation["baseline_vs_edit"]
    if isinstance(bve["baseline_pullback_too_long"], int) \
            and isinstance(bve["edit_pullback_too_long"], int):
        bve["too_long_rejections_converted_by_window_extension"] = (
            bve["baseline_pullback_too_long"]
            - bve["edit_pullback_too_long"])
        bve["converted_rejections_became_accepted"] = len(
            bve["new_accepted_ids"])
    # byte-identical check: accepted label objects equal across files
    edit_accepted = {label["setup_id"]: label for label in
                     (_json.loads(line) for line in
                      raw_labels.decode("utf-8").splitlines())
                     if label["status"] == "accepted_for_replay_review"}
    if observation["baseline_labels_sha_ok"]:
        baseline_accepted = {
            label["setup_id"]: label for label in
            (_json.loads(line) for line in
             baseline_labels_file.read_bytes().decode(
                 "utf-8").splitlines())
            if label["status"] == "accepted_for_replay_review"}
        observation["original_6_byte_identical"] = (
            edit_accepted == baseline_accepted)
        bve["original_6_still_accepted_byte_identical"] = (
            observation["original_6_byte_identical"])
    # edit failure statuses present in the explanation set
    edit_breakdown = edit_block.get("status_breakdown") or {}
    observation["failure_statuses_present"] = (
        edit_breakdown.get("rejected_rs_not_stronger", 0) >= 5
        and edit_breakdown.get(
            "rejected_pullback_below_up_leg_low", 0) >= 1)
    # replay variants from the summary's information-only block
    replay_block = summary.get("replay_information_only") or {}
    variants = {}
    removed_ids = {}
    for name in ("2r", "3r", "4r"):
        block = replay_block.get(name) or {}
        variants[name] = {
            "kept": block.get("kept"), "removed": block.get("removed"),
            "hits": block.get("hits"), "stops": block.get("stops"),
            "timeouts": block.get("timeouts"),
            "gross_r": block.get("gross_r_total"),
            "net_r": block.get("net_r_total")}
        removed_ids[name] = tuple(block.get("removed_setup_ids") or ())
    observation["edit_replay_variants"] = variants
    observation["removed_setup_ids"] = removed_ids
    return observation


def certify_c5_rejection(observation: Any) -> dict[str, Any]:
    """Pure certification of an observation against the frozen facts."""
    failures: list[str] = []
    if not isinstance(observation, dict):
        return {"certified": False,
                "failures": ["observation_not_a_dict"]}
    o = observation
    if not o.get("edit_artifacts_exist"):
        return {"certified": False,
                "failures": ["edit_artifacts_missing"]}
    if o.get("edit_labels_sha256") != EXPECTED_EDIT_LABELS_SHA256:
        failures.append("edit_labels_sha_mismatch")
    if o.get("edit_replay_sha256") != EXPECTED_EDIT_REPLAY_SHA256:
        failures.append("edit_replay_sha_mismatch")
    if o.get("edit_summary_sha256") != EXPECTED_EDIT_SUMMARY_SHA256:
        failures.append("edit_summary_sha_mismatch")
    if o.get("baseline_labels_sha_ok") is not True:
        failures.append("baseline_labels_sha_changed")
    if o.get("baseline_replay_sha_ok") is not True:
        failures.append("baseline_replay_sha_changed")
    if o.get("edit_classification") != EDIT_CLASSIFICATION:
        failures.append("edit_classification_mismatch")
    bve = o.get("baseline_vs_edit") or {}
    for key, value in EXPECTED_BASELINE_VS_EDIT.items():
        got = bve.get(key)
        if isinstance(value, tuple):
            got = tuple(got or ())
        if got != value:
            failures.append("baseline_vs_edit_mismatch:" + key)
    if o.get("original_6_byte_identical") is not True:
        failures.append("original_6_not_byte_identical")
    if o.get("failure_statuses_present") is not True:
        failures.append("failure_explanation_statuses_missing")
    variants = o.get("edit_replay_variants") or {}
    for name, expected in EXPECTED_EDIT_REPLAY_VARIANTS.items():
        got = variants.get(name) or {}
        for key, value in expected.items():
            if got.get(key) != value:
                failures.append(
                    "edit_replay_mismatch:%s:%s" % (name, key))
        net = got.get("net_r")
        if not (isinstance(net, (int, float)) and net < 0):
            failures.append("edit_replay_not_net_negative:" + name)
    removed_ids = o.get("removed_setup_ids") or {}
    for name in ("2r", "3r", "4r"):
        if removed_ids.get(name) != (EXPECTED_REMOVED_SETUP_ID,):
            failures.append("removed_setup_mismatch:" + name)
    if o.get("artifacts_tracked_in_git"):
        failures.append("runner_and_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c5_rejection_record(repo_root: Any,
                              tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe read-only and certify; record the formal rejection. Gated
    on the four-record ledger, the replay review, and the loop."""
    record: dict[str, Any] = {
        "schema_version": RJ5_SCHEMA_VERSION, "label": RJ5_LABEL,
        "mode": RJ5_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "rejection_status": REJECTION_STATUS,
        "rejection_reason": REJECTION_REASON,
        "edit_classification": EDIT_CLASSIFICATION,
        "replay_review_classification": REPLAY_REVIEW_CLASSIFICATION,
        "head_at_edit_evaluation": HEAD_AT_EDIT_EVALUATION,
        "edit_runner_path_untracked_only": EDIT_RUNNER_PATH,
        "expected_edit_labels_sha256": EXPECTED_EDIT_LABELS_SHA256,
        "expected_edit_replay_sha256": EXPECTED_EDIT_REPLAY_SHA256,
        "expected_edit_summary_sha256": EXPECTED_EDIT_SUMMARY_SHA256,
        "baseline_labels_sha256": BASELINE_LABELS_SHA256,
        "baseline_labels_summary_sha256":
            BASELINE_LABELS_SUMMARY_SHA256,
        "baseline_replay_sha256": BASELINE_REPLAY_SHA256,
        "baseline_replay_summary_sha256":
            BASELINE_REPLAY_SUMMARY_SHA256,
        "expected_baseline_vs_edit": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in EXPECTED_BASELINE_VS_EDIT.items()},
        "frozen_edit_facts": list(FROZEN_EDIT_FACTS),
        "frozen_failure_explanation": list(FROZEN_FAILURE_EXPLANATION),
        "expected_edit_replay_variants": {
            key: dict(value) for key, value
            in EXPECTED_EDIT_REPLAY_VARIANTS.items()},
        "expected_removed_setup_id": EXPECTED_REMOVED_SETUP_ID,
        "frozen_edit_replay_facts": list(FROZEN_EDIT_REPLAY_FACTS),
        "rejection_facts": list(REJECTION_FACTS),
        "evidence_notes": list(EVIDENCE_NOTES),
        "seeds_for_future_families_only": list(
            SEEDS_FOR_FUTURE_FAMILIES_ONLY),
        "seeds_are_never_rescue_paths": SEEDS_ARE_NEVER_RESCUE_PATHS,
        "edit_allowance_spent": True,
        "candidate_5_may_continue_as_is": False,
        "candidate_5_may_receive_another_edit": False,
        "further_replays_authorized": False,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "uses_account": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False, "starts_scheduler": False,
        "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if C1_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C2_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C3_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C4_STATUS != "REJECTED_KEPT_ON_RECORD":
        record["verdict"] = VERDICT_RJ5_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    replay_review = build_c5_replay_results_review(repo_root,
                                                   tracked_paths)
    if replay_review["verdict"] != VERDICT_C5RR_FROZEN:
        record["verdict"] = VERDICT_RJ5_BLOCKED
        record["blockers"].append("replay_review_not_certifying")
        record["blockers"].extend(replay_review["failures"])
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_RJ5_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observation = observe_c5_edit_result(repo_root, tracked_paths)
    result = certify_c5_rejection(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_RJ5_RECORDED if result["certified"]
                         else VERDICT_RJ5_REVIEW_REJECTED)
    return record


def validate_c5_rejection_record(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, permanence flags. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_RJ5_RECORDED,
                                VERDICT_RJ5_REVIEW_REJECTED,
                                VERDICT_RJ5_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("rejection_status") != REJECTION_STATUS:
        errors.append("rejection_status_tampered")
    if r.get("rejection_reason") != REJECTION_REASON:
        errors.append("rejection_reason_tampered")
    if r.get("edit_classification") != EDIT_CLASSIFICATION:
        errors.append("edit_classification_tampered")
    if r.get("replay_review_classification") != (
            REPLAY_REVIEW_CLASSIFICATION):
        errors.append("replay_classification_tampered")
    if r.get("head_at_edit_evaluation") != HEAD_AT_EDIT_EVALUATION:
        errors.append("head_tampered")
    for field, expected in (
            ("expected_edit_labels_sha256", EXPECTED_EDIT_LABELS_SHA256),
            ("expected_edit_replay_sha256", EXPECTED_EDIT_REPLAY_SHA256),
            ("expected_edit_summary_sha256",
             EXPECTED_EDIT_SUMMARY_SHA256),
            ("baseline_labels_sha256", BASELINE_LABELS_SHA256),
            ("baseline_labels_summary_sha256",
             BASELINE_LABELS_SUMMARY_SHA256),
            ("baseline_replay_sha256", BASELINE_REPLAY_SHA256),
            ("baseline_replay_summary_sha256",
             BASELINE_REPLAY_SUMMARY_SHA256)):
        if r.get(field) != expected:
            errors.append(field + "_tampered")
    expected_bve = {
        key: (list(value) if isinstance(value, tuple) else value)
        for key, value in EXPECTED_BASELINE_VS_EDIT.items()}
    if r.get("expected_baseline_vs_edit") != expected_bve:
        errors.append("baseline_vs_edit_tampered")
    if tuple(r.get("frozen_edit_facts") or ()) != FROZEN_EDIT_FACTS:
        errors.append("edit_facts_tampered")
    if tuple(r.get("frozen_failure_explanation") or ()) != (
            FROZEN_FAILURE_EXPLANATION):
        errors.append("failure_explanation_tampered")
    expected_variants = {key: dict(value) for key, value
                         in EXPECTED_EDIT_REPLAY_VARIANTS.items()}
    if r.get("expected_edit_replay_variants") != expected_variants:
        errors.append("edit_replay_variants_tampered")
    if r.get("expected_removed_setup_id") != EXPECTED_REMOVED_SETUP_ID:
        errors.append("removed_setup_tampered")
    if tuple(r.get("frozen_edit_replay_facts") or ()) != (
            FROZEN_EDIT_REPLAY_FACTS):
        errors.append("edit_replay_facts_tampered")
    if tuple(r.get("rejection_facts") or ()) != REJECTION_FACTS:
        errors.append("rejection_facts_tampered")
    if tuple(r.get("evidence_notes") or ()) != EVIDENCE_NOTES:
        errors.append("evidence_notes_tampered")
    if tuple(r.get("seeds_for_future_families_only") or ()) != (
            SEEDS_FOR_FUTURE_FAMILIES_ONLY):
        errors.append("seeds_tampered")
    if r.get("seeds_are_never_rescue_paths") is not True:
        errors.append("seeds_must_never_be_rescue_paths")
    if r.get("edit_allowance_spent") is not True:
        errors.append("edit_allowance_must_be_spent")
    for key in ("candidate_5_may_continue_as_is",
                "candidate_5_may_receive_another_edit",
                "further_replays_authorized"):
        if r.get(key) is not False:
            errors.append("permanence_flag_wrong:" + key)
    if r.get("verdict") == VERDICT_RJ5_RECORDED and r.get("failures"):
        errors.append("recorded_with_failures")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
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
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}

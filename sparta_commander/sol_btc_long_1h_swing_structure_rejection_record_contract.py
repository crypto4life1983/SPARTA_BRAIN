"""SPARTA CANDIDATE #4 FORMAL REJECTION RECORD (READ-ONLY, RESEARCH
ONLY): SOL_BTC_LONG_1H_SWING_STRUCTURE_V1.

THE LEDGER ENTRY: Candidate #4 is REJECTED_KEPT_ON_RECORD, reason
EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_ONLY_EDIT.

The candidate lost GROSS and NET at every target in the fee-honest
replay of its 22 frozen labels. The single pre-committed filter-only
edit (same-symbol no-overlap/cooldown) was spent: it was VALID as a
filter (reduce-or-equal counts, no new trades, entries untouched, full
kept/removed accounting, zero overlaps after) and it removed the
correlated duplicate losses exactly as the frozen warning predicted --
but every filtered variant REMAINED gross-negative and net-negative.
The overlap was amplifying the failure, not causing it. Hit rates stayed
below gross breakeven in all variants. The edit allowance is now SPENT.

No paper approval, no live approval, no profitability claim -- there is
nothing to claim. Seeds are preserved STRICTLY for future families and
are never rescue paths.

This module observes the untracked filter-evaluation artifact READ-ONLY,
re-verifies its sha and arithmetic, and certifies the frozen facts. It
reruns nothing, fetches nothing, and authorizes nothing.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_replay_results_review_contract import (
    VERDICT_C4RR_FROZEN,
    build_c4_replay_results_review,
)
from sparta_commander.sol_btc_long_1h_swing_structure_strategy_spec_contract import (
    CANDIDATE_ID,
)

RJ4_SCHEMA_VERSION = (
    "sol_btc_long_1h_swing_structure_rejection_record.v1")
RJ4_LABEL = ("SPARTA Candidate #4 Formal Rejection Record "
             "(READ-ONLY, RESEARCH ONLY, REJECTED KEPT ON RECORD, "
             "NOT A PROFITABILITY CLAIM)")
RJ4_MODE = "RESEARCH_ONLY"
VERDICT_RJ4_RECORDED = (
    "C4_REJECTED_KEPT_ON_RECORD_EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED"
    "_FILTER_ONLY_EDIT")
VERDICT_RJ4_REVIEW_REJECTED = "C4_REJECTION_RECORD_REVIEW_REJECTED"
VERDICT_RJ4_BLOCKED = "C4_REJECTION_RECORD_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_NEXT_CANDIDATE_FAMILY"

REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"
REJECTION_REASON = (
    "EDGE_FAILURE_SURVIVED_ONE_AUTHORIZED_FILTER_ONLY_EDIT")
FILTER_CLASSIFICATION = "C4_FILTER_ONLY_EDIT_FAILED_REJECT_NEXT"

FILTER_EVAL_PATH = ("data/swing_structure_c4/filter_edit_v1/"
                    "c4_filter_edit_eval_2026-05-02_2026-06-10.json")
FILTER_RUNNER_PATH = "tools/c4_filter_only_edit_eval_once.py"
EXPECTED_FILTER_EVAL_SHA256 = (
    "b93c432463cf40cb0b0a444980238ea2a4d585b7fcd12772958691569f1fae67")

UPSTREAM_FROZEN_FACTS = {
    "head_at_decision": "71e8904b16205e2da503f3863fb2ba167f360ffa",
    "replay_review_verdict":
        "C4_REPLAY_RESULTS_REVIEW_CONTRACT_FROZEN_REJECTION_PRESSURE",
    "filter_was_the_single_authorized_pre_committed_edit": True,
    "edit_allowance_now_spent": True,
}

FILTER_VALIDITY_FACTS = (
    "filter type: same-symbol no-overlap/cooldown filter",
    "trade count reduced-or-equal in every variant",
    "no new trades added",
    "entries not weakened",
    "detector logic untouched",
    "labels untouched",
    "frozen replay rows used; nothing recomputed",
    "kept and removed setup_ids fully accounted",
    "kept union removed equals the original 22 setup_ids",
    "kept intersection removed is empty",
    "overlap count after filtering is 0 in every variant",
    "but all filtered variants remain gross-negative and net-negative",
)

EXPECTED_FILTERED_VARIANTS = {
    "2r": {"original_trades": 22, "filtered_trades": 8,
           "removed_trades": 14, "hits": 2, "stops": 6, "timeouts": 0,
           "hit_rate_pct": 25.0, "gross_breakeven_rate_pct": 33.3,
           "gross_r": -2.0, "fee_r": 1.29908, "net_r": -3.29908,
           "overlaps_after": 0},
    "3r": {"original_trades": 22, "filtered_trades": 7,
           "removed_trades": 15, "hits": 1, "stops": 6, "timeouts": 0,
           "hit_rate_pct": 14.3, "gross_breakeven_rate_pct": 25.0,
           "gross_r": -3.0, "fee_r": 1.232028, "net_r": -4.232028,
           "overlaps_after": 0},
    "4r": {"original_trades": 22, "filtered_trades": 7,
           "removed_trades": 15, "hits": 1, "stops": 6, "timeouts": 0,
           "hit_rate_pct": 14.3, "gross_breakeven_rate_pct": 20.0,
           "gross_r": -2.0, "fee_r": 1.232028, "net_r": -3.232028,
           "overlaps_after": 0},
}

COMPARISON_TO_UNFILTERED = {
    "2r": {"unfiltered_net_r": -11.666507, "filtered_net_r": -3.29908},
    "3r": {"unfiltered_net_r": -18.666507, "filtered_net_r": -4.232028},
    "4r": {"unfiltered_net_r": -16.666507, "filtered_net_r": -3.232028},
    "statements": (
        "the filter improved losses by removing correlated duplicate "
        "losses, but did not turn the candidate positive",
        "the overlap was amplifying the failure, not causing it",
        "hit rates stayed below gross breakeven in all variants"),
}

FROZEN_SYMBOL_FACTS = (
    "btc kept 3 trades, 0 hits, approximately -3.48R net in every "
    "variant",
    "sol kept 5/4/4 trades by 2r/3r/4r",
    "sol was marginally positive only at 2r and 4r, but on only 4-5 "
    "trades and not enough to save the whole candidate",
    "sol 3r stayed negative",
    "this is noise-level, not a strategy approval signal",
)

REJECTION_FACTS = (
    "candidate #4 is rejected",
    "rejection is kept on record",
    "reason: edge failure, not cost failure",
    "gross-negative before filter at every target",
    "gross-negative after filter at every target",
    "net-negative before and after filter",
    "one authorized filter-only edit was spent and failed",
    "no paper approval",
    "no live approval",
    "no profitability claim permitted",
)

SEEDS_FOR_FUTURE_FAMILIES_ONLY = (
    "same_symbol_no_overlap_cooldown_is_validated_useful_filtering"
    "_machinery",
    "future_families_should_consider_non_overlap_at_label_replay_time"
    "_not_as_rescue_after_failure",
    "sol_deduplicated_core_may_be_a_clue_but_is_too_small_noisy_and"
    "_cannot_be_promoted",
    "btc_contribution_was_persistently_negative_and_is_not_evidence"
    "_of_edge",
    "structural_stop_geometry_and_overlap_clustering_are_failure_mode"
    "_lessons",
)
SEEDS_ARE_NEVER_RESCUE_PATHS = True


def get_c4_rejection_record_label() -> str:
    return RJ4_LABEL


def observe_filter_edit_result(repo_root: Any,
                               tracked_paths: Any = ()) -> dict[str, Any]:
    """Read the filter-evaluation artifact READ-ONLY and extract/recheck
    the facts. Never raises on missing files."""
    observation: dict[str, Any] = {
        "eval_exists": False, "eval_sha256": None,
        "classification": None, "variants": None,
        "accounting_ok": None, "all_gross_negative": None,
        "all_net_negative": None, "all_overlaps_zero": None,
        "all_counts_reduce_or_equal": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/") for p in (tracked_paths or ())}
    for rel in (FILTER_EVAL_PATH, FILTER_RUNNER_PATH):
        if rel in tracked:
            observation["artifacts_tracked_in_git"].append(rel)
    eval_file = root / FILTER_EVAL_PATH
    if not eval_file.is_file():
        return observation
    observation["eval_exists"] = True
    raw = eval_file.read_bytes()
    observation["eval_sha256"] = _hashlib.sha256(raw).hexdigest()
    data = _json.loads(raw.decode("utf-8"))
    observation["classification"] = data.get("classification")
    variants: dict[str, Any] = {}
    accounting_ok = True
    gross_negative = []
    net_negative = []
    overlaps_zero = []
    reduce_or_equal = []
    for name in ("2r", "3r", "4r"):
        block = (data.get("variants") or {}).get(name) or {}
        agg = block.get("aggregate") or {}
        kept = set(block.get("kept_setup_ids") or ())
        removed = {item[0] for item in
                   (block.get("removed_setup_ids") or ())}
        if len(kept) + len(removed) != 22 or (kept & removed) \
                or len(kept) != block.get("filtered_trades"):
            accounting_ok = False
        variants[name] = {
            "original_trades": block.get("original_trades"),
            "filtered_trades": block.get("filtered_trades"),
            "removed_trades": block.get("removed_trades"),
            "hits": agg.get("hits"), "stops": agg.get("stops"),
            "timeouts": agg.get("timeouts"),
            "hit_rate_pct": agg.get("hit_rate_pct"),
            "gross_breakeven_rate_pct": agg.get(
                "gross_breakeven_rate_pct"),
            "gross_r": agg.get("gross_r"), "fee_r": agg.get("fee_r"),
            "net_r": agg.get("net_r"),
            "overlaps_after": agg.get("overlap_count_after_filter")}
        gross_negative.append(isinstance(agg.get("gross_r"),
                                         (int, float))
                              and agg.get("gross_r") < 0)
        net_negative.append(isinstance(agg.get("net_r"), (int, float))
                            and agg.get("net_r") < 0)
        overlaps_zero.append(agg.get("overlap_count_after_filter") == 0)
        reduce_or_equal.append(
            isinstance(block.get("filtered_trades"), int)
            and block.get("filtered_trades") <= 22)
    observation["variants"] = variants
    observation["accounting_ok"] = accounting_ok
    observation["all_gross_negative"] = all(gross_negative)
    observation["all_net_negative"] = all(net_negative)
    observation["all_overlaps_zero"] = all(overlaps_zero)
    observation["all_counts_reduce_or_equal"] = all(reduce_or_equal)
    return observation


def certify_c4_rejection(observation: Any) -> dict[str, Any]:
    """Pure certification of an observation against the frozen facts."""
    failures: list[str] = []
    if not isinstance(observation, dict):
        return {"certified": False,
                "failures": ["observation_not_a_dict"]}
    o = observation
    if not o.get("eval_exists"):
        return {"certified": False,
                "failures": ["filter_eval_artifact_missing"]}
    if o.get("eval_sha256") != EXPECTED_FILTER_EVAL_SHA256:
        failures.append("filter_eval_sha_mismatch")
    if o.get("classification") != FILTER_CLASSIFICATION:
        failures.append("classification_mismatch")
    variants = o.get("variants") or {}
    for name, expected in EXPECTED_FILTERED_VARIANTS.items():
        got = variants.get(name) or {}
        for key, value in expected.items():
            if got.get(key) != value:
                failures.append(
                    "filtered_fact_mismatch:%s:%s" % (name, key))
        if (got.get("hits") or 0) + (got.get("stops") or 0) \
                + (got.get("timeouts") or 0) != (
                got.get("filtered_trades") or -1):
            failures.append("filtered_counts_inconsistent:" + name)
    if o.get("accounting_ok") is not True:
        failures.append("kept_removed_accounting_broken")
    if o.get("all_gross_negative") is not True:
        failures.append("gross_negative_fact_broken")
    if o.get("all_net_negative") is not True:
        failures.append("net_negative_fact_broken")
    if o.get("all_overlaps_zero") is not True:
        failures.append("overlaps_not_zero_after_filter")
    if o.get("all_counts_reduce_or_equal") is not True:
        failures.append("filter_increased_trades_invalid")
    for name, pair in COMPARISON_TO_UNFILTERED.items():
        if name == "statements":
            continue
        got = variants.get(name) or {}
        if got.get("net_r") != pair["filtered_net_r"]:
            failures.append("comparison_mismatch:" + name)
        if not pair["filtered_net_r"] > pair["unfiltered_net_r"]:
            failures.append("comparison_direction_impossible:" + name)
    if o.get("artifacts_tracked_in_git"):
        failures.append("runner_and_artifact_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c4_rejection_record(repo_root: Any,
                              tracked_paths: Any = ()) -> dict[str, Any]:
    """Observe read-only and certify; record the formal rejection. Gated
    on the three-record ledger AND the replay review still certifying."""
    record: dict[str, Any] = {
        "schema_version": RJ4_SCHEMA_VERSION, "label": RJ4_LABEL,
        "mode": RJ4_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "rejection_status": REJECTION_STATUS,
        "rejection_reason": REJECTION_REASON,
        "filter_classification": FILTER_CLASSIFICATION,
        "filter_eval_path": FILTER_EVAL_PATH,
        "filter_runner_path_untracked_only": FILTER_RUNNER_PATH,
        "expected_filter_eval_sha256": EXPECTED_FILTER_EVAL_SHA256,
        "upstream_frozen_facts": dict(UPSTREAM_FROZEN_FACTS),
        "filter_validity_facts": list(FILTER_VALIDITY_FACTS),
        "expected_filtered_variants": {
            key: dict(value) for key, value
            in EXPECTED_FILTERED_VARIANTS.items()},
        "comparison_to_unfiltered": {
            key: (dict(value) if isinstance(value, dict)
                  else list(value))
            for key, value in COMPARISON_TO_UNFILTERED.items()},
        "frozen_symbol_facts": list(FROZEN_SYMBOL_FACTS),
        "rejection_facts": list(REJECTION_FACTS),
        "seeds_for_future_families_only": list(
            SEEDS_FOR_FUTURE_FAMILIES_ONLY),
        "seeds_are_never_rescue_paths": SEEDS_ARE_NEVER_RESCUE_PATHS,
        "edit_allowance_spent": True,
        "candidate_4_may_continue_as_is": False,
        "candidate_4_may_receive_another_edit": False,
        "further_replays_authorized": False,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "executes": False, "writes_files": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False, "revives_candidate_3": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if C1_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C2_STATUS != "REJECTED_KEPT_ON_RECORD" \
            or C3_STATUS != "REJECTED_KEPT_ON_RECORD":
        record["verdict"] = VERDICT_RJ4_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    replay_review = build_c4_replay_results_review(repo_root,
                                                   tracked_paths)
    if replay_review["verdict"] != VERDICT_C4RR_FROZEN:
        record["verdict"] = VERDICT_RJ4_BLOCKED
        record["blockers"].append("replay_review_not_certified")
        record["blockers"].extend(replay_review["failures"])
        return record
    observation = observe_filter_edit_result(repo_root, tracked_paths)
    result = certify_c4_rejection(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_RJ4_RECORDED if result["certified"]
                         else VERDICT_RJ4_REVIEW_REJECTED)
    return record


def validate_c4_rejection_record(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, permanence flags. Never raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_RJ4_RECORDED,
                                VERDICT_RJ4_REVIEW_REJECTED,
                                VERDICT_RJ4_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("rejection_status") != REJECTION_STATUS:
        errors.append("rejection_status_tampered")
    if r.get("rejection_reason") != REJECTION_REASON:
        errors.append("rejection_reason_tampered")
    if r.get("filter_classification") != FILTER_CLASSIFICATION:
        errors.append("filter_classification_tampered")
    if r.get("expected_filter_eval_sha256") != (
            EXPECTED_FILTER_EVAL_SHA256):
        errors.append("filter_eval_sha_tampered")
    if r.get("upstream_frozen_facts") != UPSTREAM_FROZEN_FACTS:
        errors.append("upstream_facts_tampered")
    if tuple(r.get("filter_validity_facts") or ()) != (
            FILTER_VALIDITY_FACTS):
        errors.append("filter_validity_facts_tampered")
    expected_variants = {key: dict(value) for key, value
                         in EXPECTED_FILTERED_VARIANTS.items()}
    if r.get("expected_filtered_variants") != expected_variants:
        errors.append("filtered_variant_table_tampered")
    expected_comparison = {
        key: (dict(value) if isinstance(value, dict) else list(value))
        for key, value in COMPARISON_TO_UNFILTERED.items()}
    if r.get("comparison_to_unfiltered") != expected_comparison:
        errors.append("comparison_tampered")
    if tuple(r.get("frozen_symbol_facts") or ()) != FROZEN_SYMBOL_FACTS:
        errors.append("symbol_facts_tampered")
    if tuple(r.get("rejection_facts") or ()) != REJECTION_FACTS:
        errors.append("rejection_facts_tampered")
    if tuple(r.get("seeds_for_future_families_only") or ()) != (
            SEEDS_FOR_FUTURE_FAMILIES_ONLY):
        errors.append("seeds_tampered")
    if r.get("seeds_are_never_rescue_paths") is not True:
        errors.append("seeds_must_never_be_rescue_paths")
    if r.get("edit_allowance_spent") is not True:
        errors.append("edit_allowance_must_be_spent")
    for key in ("candidate_4_may_continue_as_is",
                "candidate_4_may_receive_another_edit",
                "further_replays_authorized"):
        if r.get(key) is not False:
            errors.append("permanence_flag_wrong:" + key)
    if r.get("verdict") == VERDICT_RJ4_RECORDED and r.get("failures"):
        errors.append("recorded_with_failures")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "runs_real_detection_now",
                "runs_replay_now", "scores_now", "stages_data_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "claims_profitability", "revives_candidate_3"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}

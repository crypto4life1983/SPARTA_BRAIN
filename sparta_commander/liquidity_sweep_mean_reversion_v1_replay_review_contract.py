"""SPARTA CANDIDATE #8 REPLAY REVIEW / EVIDENCE FREEZE (READ-ONLY,
RESEARCH ONLY, IN-SAMPLE STRUCTURAL FINDING ONLY, NOT A
PROFITABILITY CLAIM): LIQUIDITY_SWEEP_MEAN_REVERSION_V1.

Freezes the first replay-time evaluation of the 51 accepted-post-
anti-cluster real-candle setups from the pushed C8 labels review
gate (commit fb208252a5551937cb431eb25706b96ca92d43b7). The
untracked runner tools/c8_replay_once.py walked each setup against
the same staged BTCUSD 15m candles the detection runner read,
applying:

  - the inherited replay-time same-symbol non-overlap policy as
    REDUCE-OR-KEEP-ONLY (never add);
  - the proposal-locked 27 bps round-trip fee and the proposal-
    locked 81 bps gross target-distance floor;
  - the conservative STOP-FIRST same-bar straddle convention;
  - a 96-bar (24h at 15m) per-setup evaluation window.

Headline structural in-sample finding for the
2026-05-02_2026-06-10 BTCUSD 15m window:

  - 2R variant: 51 evaluated, 0 overlap drops; 11 HIT, 38 MISS, 0
    same-bar straddle, 2 TIMEOUT, 0 open-at-end;
      gross R sum = -15.814923512147077;
      net  R sum after 27 bps fees = -45.77781173130582;
      structurally_net_positive_in_sample_decisive_only = False.
  - 3R variant: 51 evaluated, 0 overlap drops;  3 HIT, 42 MISS, 0
    same-bar straddle, 6 TIMEOUT, 0 open-at-end;
      gross R sum = -28.876621100398147;
      net  R sum = -58.83950931955688;
      structurally_net_positive_in_sample_decisive_only = False.
  - 4R variant: 51 evaluated, 0 overlap drops;  0 HIT, 43 MISS, 0
    same-bar straddle, 8 TIMEOUT, 0 open-at-end;
      gross R sum = -35.82079188422728;
      net  R sum = -65.78368010338602;
      structurally_net_positive_in_sample_decisive_only = False.

ALL THREE VARIANTS ARE STRUCTURALLY NET-NEGATIVE IN THIS IN-SAMPLE
WINDOW. THIS IS NOT A PROFITABILITY CLAIM. NO EDGE HAS BEEN
DEMONSTRATED. NO LIVE PROFITABILITY IS CLAIMED. NO PAPER, MICRO-
LIVE, OR LIVE APPROVAL IS GRANTED. THE SINGLE C8 EDIT TOKEN HAS NOT
YET BEEN CONSUMED.

The HUMAN decision after this review is captured by the
NEXT_REQUIRED_ACTION token below:
HUMAN_DECISION_C8_SPEND_SINGLE_EDIT_OR_REJECT_ON_NET_NEGATIVE_IN
_SAMPLE. The two structural options are (1) spend the single C8 edit
token on a different structural parameter (sweep multiplier, reclaim
window, structure-stop buffer multiplier, or 96-bar lookback) and
re-detect + re-replay, OR (2) reject Candidate #8 on this in-sample
result and add the family to the rejected-family blacklist.

This module observes the UNTRACKED replay artifacts READ-ONLY,
re-verifies every SHA-256 pin (replay ledger + replay summary +
detector labels + detector summary + the two staged BTCUSD 15m
CSVs), and certifies every frozen counts and R-sum field against
the live re-read of the summary JSON. It runs nothing, fetches
nothing, modifies nothing, and authorizes nothing.

Chain-gated live on: the pushed seven-record rejection ledger
(C1-C7), the pushed C8 family proposal, the pushed C8 spec review,
the pushed C8 detector spec + synthetic dry-run, the pushed C8
dry-run review, the pushed C8 real-candle labels review, the pushed
V3 rejected-family blacklist, the pushed Overnight Research
Autopilot V2, the pushed Recommendation V1, and the pushed Autopilot
Loop V1.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as _rec
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
    REJECTION_STATUS as C5_STATUS,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_detector_dry_run_review_contract import (
    VERDICT_C8R_FROZEN,
    build_candidate_8_dry_run_review,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_detector_spec_dry_run_contract import (
    VERDICT_C8D_READY,
    build_candidate_8_detector_spec_contract,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C8P_READY,
    build_candidate_8_family_proposal,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_real_candle_labels_review_contract import (
    VERDICT_C8L_FROZEN,
    build_c8_labels_review,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_spec_review_contract import (
    VERDICT_C8S_READY,
    build_candidate_8_spec_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (
    REJECTION_STATUS as C6_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)
from sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract import (
    VERDICT_OAP2_READY,
    build_overnight_research_autopilot_v2_contract,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract import (
    VERDICT_BL3_READY,
    build_rejected_family_blacklist_v3,
)
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C8RR_SCHEMA_VERSION = (
    "liquidity_sweep_mean_reversion_v1_replay_review.v1")
C8RR_LABEL = ("SPARTA Candidate #8 Replay Review / Evidence Freeze "
              "(READ-ONLY, RESEARCH ONLY, ALL VARIANTS NET-NEGATIVE "
              "IN-SAMPLE, NO EDGE DEMONSTRATED, NOT A PROFITABILITY "
              "CLAIM, NOT A RESCUE)")
C8RR_MODE = "RESEARCH_ONLY"
VERDICT_C8RR_FROZEN = "CANDIDATE_8_REPLAY_REVIEW_FROZEN"
VERDICT_C8RR_REJECTED = "CANDIDATE_8_REPLAY_REVIEW_REJECTED"
VERDICT_C8RR_BLOCKED = "CANDIDATE_8_REPLAY_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_C8_SPEND_SINGLE_EDIT_OR_REJECT_ON_NET"
    "_NEGATIVE_IN_SAMPLE")
CURRENT_LOOP_STAGE = "detector_and_label_review"

HEAD_AT_REPLAY = "fb208252a5551937cb431eb25706b96ca92d43b7"
RUNNER_PATH = "tools/c8_replay_once.py"
LEDGER_PATH = ("data/liquidity_sweep_c8/replay_results/"
               "c8_replay_ledger_2026-05-02_2026-06-10.json")
SUMMARY_PATH = ("data/liquidity_sweep_c8/replay_results/"
                "c8_replay_summary_2026-05-02_2026-06-10.json")
EXPECTED_LEDGER_SHA256 = (
    "b7b12b8ef9ffe9bf3ab587ba4bd2b097d391a78f6761e52c7103146de58dfb92")
EXPECTED_SUMMARY_SHA256 = (
    "2be19e38195a7a2414c661b6d3ec84a5fdc371c05e6cc7d461199683944454db")

# Detector-labels + detector-summary input pins (pulled forward
# from the pushed labels review)
EXPECTED_DETECTOR_LABELS_PATH = (
    "data/liquidity_sweep_c8/detector_labels/"
    "c8_detector_labels_2026-05-02_2026-06-10.json")
EXPECTED_DETECTOR_SUMMARY_PATH = (
    "data/liquidity_sweep_c8/detector_labels/"
    "c8_detector_summary_2026-05-02_2026-06-10.json")
EXPECTED_DETECTOR_LABELS_SHA256 = (
    "f323ff7188b672a9af2521e30d3b7a4052217d86c7bbb0f8c0e86405cb81fee3")
EXPECTED_DETECTOR_SUMMARY_SHA256 = (
    "d1655123990b0080ef741bda49ea5baa20d6640c4b2d4476986f29deb2e4ae90")

EXPECTED_STAGED_SHAS = {
    "data/ny_fvg_choch/staged/BTCUSD_15m_2026-05-02_2026-06-09.csv":
        "4ee373b28caeafa47d463e0fc2582f1958b877a8f05df0714a0afd"
        "1298ee9f14",
    "data/ny_fvg_choch/staged/BTCUSD_15m_2026-06-01_2026-06-10.csv":
        "4bb50873df5194de65315bf44f1823d17922e445745401eb01aa16"
        "70aed4956d",
}

EXPECTED_SAMPLE_TAG = "2026-05-02_2026-06-10"
EXPECTED_START_INCLUSIVE_UTC = "2026-05-02T00:00:00Z"
EXPECTED_END_INCLUSIVE_UTC = "2026-06-10T23:45:00Z"

EXPECTED_REPLAY_POLICY = {
    "timeout_bars": 96,
    "fee_round_trip_bps": 27.0,
    "target_distance_floor_bps": 81.0,
    "variants": ("2r", "3r", "4r"),
    "same_bar_straddle_policy": "stop_first_conservative_miss",
    "non_overlap_policy": "reduce_or_keep_only_never_add",
    "evaluation_horizon_hours_at_15m": 24.0,
}

EXPECTED_ACCEPTED_INPUT_COUNT = 51

EXPECTED_VARIANT_2R_AGGREGATE = {
    "variant_r_multiple": 2.0,
    "kept_count": 51,
    "dropped_overlap_count": 0,
    "decisive_count": 51,
    "open_or_truncated_count": 0,
    "counts": {
        "hit": 11, "miss": 38, "miss_same_bar_straddle": 0,
        "timeout": 2, "open_at_sample_end": 0,
        "no_start_bar_in_sample": 0,
    },
    "gross_r_sum_decisive": -15.814923512147077,
    "net_r_sum_decisive": -45.77781173130582,
    "gross_r_sum_including_truncated": -15.814923512147077,
    "net_r_sum_including_truncated": -45.77781173130582,
    "decisive_mean_gross_r": -0.31009653945386423,
    "decisive_mean_net_r": -0.8976041515942317,
    "structurally_net_positive_in_sample_decisive_only": False,
}

EXPECTED_VARIANT_3R_AGGREGATE = {
    "variant_r_multiple": 3.0,
    "kept_count": 51,
    "dropped_overlap_count": 0,
    "decisive_count": 51,
    "open_or_truncated_count": 0,
    "counts": {
        "hit": 3, "miss": 42, "miss_same_bar_straddle": 0,
        "timeout": 6, "open_at_sample_end": 0,
        "no_start_bar_in_sample": 0,
    },
    "gross_r_sum_decisive": -28.876621100398147,
    "net_r_sum_decisive": -58.83950931955688,
    "gross_r_sum_including_truncated": -28.876621100398147,
    "net_r_sum_including_truncated": -58.83950931955688,
    "decisive_mean_gross_r": -0.5662082568705519,
    "decisive_mean_net_r": -1.1537158690109193,
    "structurally_net_positive_in_sample_decisive_only": False,
}

EXPECTED_VARIANT_4R_AGGREGATE = {
    "variant_r_multiple": 4.0,
    "kept_count": 51,
    "dropped_overlap_count": 0,
    "decisive_count": 51,
    "open_or_truncated_count": 0,
    "counts": {
        "hit": 0, "miss": 43, "miss_same_bar_straddle": 0,
        "timeout": 8, "open_at_sample_end": 0,
        "no_start_bar_in_sample": 0,
    },
    "gross_r_sum_decisive": -35.82079188422728,
    "net_r_sum_decisive": -65.78368010338602,
    "gross_r_sum_including_truncated": -35.82079188422728,
    "net_r_sum_including_truncated": -65.78368010338602,
    "decisive_mean_gross_r": -0.702368468318182,
    "decisive_mean_net_r": -1.2898760804585494,
    "structurally_net_positive_in_sample_decisive_only": False,
}

EXPECTED_VARIANT_AGGREGATES = {
    "2r": EXPECTED_VARIANT_2R_AGGREGATE,
    "3r": EXPECTED_VARIANT_3R_AGGREGATE,
    "4r": EXPECTED_VARIANT_4R_AGGREGATE,
}

EXPECTED_PER_VARIANT_IDENTITY_CHECKS = {
    "2r_counts_sum_equals_kept": 11 + 38 + 0 + 2 + 0 + 0 == 51,
    "3r_counts_sum_equals_kept": 3 + 42 + 0 + 6 + 0 + 0 == 51,
    "4r_counts_sum_equals_kept": 0 + 43 + 0 + 8 + 0 + 0 == 51,
    "2r_kept_plus_overlap_equals_accepted_input":
        51 + 0 == EXPECTED_ACCEPTED_INPUT_COUNT,
    "3r_kept_plus_overlap_equals_accepted_input":
        51 + 0 == EXPECTED_ACCEPTED_INPUT_COUNT,
    "4r_kept_plus_overlap_equals_accepted_input":
        51 + 0 == EXPECTED_ACCEPTED_INPUT_COUNT,
}

EXPECTED_HEADLINE_FINDING = {
    "all_three_variants_structurally_net_negative_in_sample": True,
    "any_variant_structurally_net_positive_in_sample_decisive_only":
        False,
    "no_edge_demonstrated": True,
    "no_live_profitability_claimed": True,
    "no_winner_designation": True,
    "no_paper_approval": True,
    "no_micro_live_approval": True,
    "no_live_approval": True,
    "no_edit_token_consumed_by_this_gate": True,
    "no_downstream_gate_unlocked_by_this_gate": True,
}

EXPECTED_SUMMARY_SELF_CLAIMS = {
    "candidate_id": "LIQUIDITY_SWEEP_MEAN_REVERSION_V1",
    "candidate_family": "liquidity_sweep_mean_reversion",
    "symbol": "BTCUSD",
    "timeframe": "15m",
    "direction": "long_only",
    "sample_tag": EXPECTED_SAMPLE_TAG,
    "start_inclusive_utc": EXPECTED_START_INCLUSIVE_UTC,
    "end_inclusive_utc": EXPECTED_END_INCLUSIVE_UTC,
    "head_at_labels_review": HEAD_AT_REPLAY,
    "timeout_bars": 96,
    "fee_round_trip_bps": 27.0,
    "target_distance_floor_bps": 81.0,
    "variants": ["2r", "3r", "4r"],
    "same_bar_straddle_policy": "stop_first_conservative_miss",
    "non_overlap_policy": "reduce_or_keep_only_never_add",
    "accepted_post_anti_cluster_input_count":
        EXPECTED_ACCEPTED_INPUT_COUNT,
    "inputs_unchanged_during_evaluation": True,
}

EXPECTED_SCOPE_LOCKS = {
    "no_paper_trading": True, "no_micro_live": True,
    "no_live_trading": True, "no_broker": True,
    "no_exchange": True, "no_wallet": True, "no_account": True,
    "no_credentials": True, "no_order_logic": True,
    "no_portfolio_allocation": True, "no_api": True,
    "no_network": True, "no_fetch": True,
    "no_notification": True, "no_scheduler": True,
    "no_relabel": True, "no_detector_change": True,
    "no_edit_token_use": True, "no_profitability_claim": True,
    "no_downstream_gate_unlock": True, "no_staging": True,
    "no_commit": True, "no_push": True,
}

FROZEN_REVIEW_FINDINGS = (
    "51 accepted-post-anti-cluster setups from the pushed C8 "
    "labels review (commit fb208252) walked forward against the "
    "same staged btcusd 15m bars; no detector change, no relabel, "
    "no data fetch",
    "replay-time same-symbol non-overlap is REDUCE-OR-KEEP-ONLY "
    "never add; same-bar straddle is STOP-FIRST conservative miss; "
    "evaluation horizon is 96 bars (24h at 15m)",
    "27 bps round-trip fee and 81 bps gross target-distance floor "
    "are the same proposal-locked values; the floor was enforced "
    "at label time and is preserved here for evidence",
    "variant 2r: 11 hit, 38 miss, 0 same-bar, 2 timeout, 0 open-"
    "at-end; gross_r_sum = -15.81; net_r_sum after fees = -45.78; "
    "structurally_net_positive_in_sample_decisive_only = False",
    "variant 3r:  3 hit, 42 miss, 0 same-bar, 6 timeout, 0 open-"
    "at-end; gross_r_sum = -28.88; net_r_sum after fees = -58.84; "
    "structurally_net_positive_in_sample_decisive_only = False",
    "variant 4r:  0 hit, 43 miss, 0 same-bar, 8 timeout, 0 open-"
    "at-end; gross_r_sum = -35.82; net_r_sum after fees = -65.78; "
    "structurally_net_positive_in_sample_decisive_only = False",
    "all three variants are structurally net-negative in this in-"
    "sample window; this is NOT a live profitability claim, NO "
    "edge has been demonstrated, NO winner designation is granted",
    "single c8 edit token has NOT been consumed by this review; "
    "anti-cluster gap remains proposal-level locked and does NOT "
    "consume the edit token; sample-size adequacy threshold "
    "remains proposal-level locked and does NOT consume the edit "
    "token",
    "next human decision: spend the single c8 edit token on a "
    "different structural parameter (sweep multiplier, reclaim "
    "window, structure-stop buffer multiplier, or 96-bar lookback) "
    "and re-detect + re-replay; OR reject candidate 8 on this in-"
    "sample result and add the family to the rejected-family "
    "blacklist",
    "this review authorizes NO paper, NO micro-live, NO live, NO "
    "broker, NO exchange, NO order, NO portfolio, NO fetch, NO "
    "api, NO network, NO scheduler, NO notification, NO relabel, "
    "NO detector change, NO commit, NO push",
)

CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "no_replay_re_run_authorized_by_this_gate",
    "no_relabel_authorized_by_this_gate",
    "no_detector_change_authorized_by_this_gate",
    "no_edit_token_applied_by_this_gate",
    "no_rejection_decision_made_by_this_gate",
    "anti_cluster_gap_remains_proposal_level_locked",
    "sample_size_threshold_remains_proposal_level_locked",
)


def get_candidate_8_replay_review_label() -> str:
    return C8RR_LABEL


def observe_c8_replay(repo_root: Any,
                      tracked_paths: Any = ()
                      ) -> dict[str, Any]:
    """Read the untracked replay artifacts READ-ONLY and recount the
    facts. Never raises on missing files; reports absence instead."""
    observation: dict[str, Any] = {
        "ledger_exists": False, "summary_exists": False,
        "ledger_sha256": None, "summary_sha256": None,
        "summary_variant_aggregates": None,
        "summary_self_claims": None,
        "summary_scope_locks": None,
        "summary_labels_input_sha256_before": None,
        "summary_labels_input_sha256_after": None,
        "summary_summary_input_sha256_before": None,
        "summary_summary_input_sha256_after": None,
        "summary_source_files_sha256_before": None,
        "summary_source_files_sha256_after": None,
        "summary_inputs_unchanged_during_evaluation": None,
        "summary_ledger_sha256": None,
        "staged_shas_now": None,
        "staged_shas_match": None,
        "detector_labels_sha_now": None,
        "detector_labels_sha_matches_pin": None,
        "detector_summary_sha_now": None,
        "detector_summary_sha_matches_pin": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/")
               for p in (tracked_paths or ())}
    for rel in (LEDGER_PATH, SUMMARY_PATH, RUNNER_PATH):
        if rel in tracked:
            observation["artifacts_tracked_in_git"].append(rel)
    staged_now: dict[str, Any] = {}
    for rel in EXPECTED_STAGED_SHAS:
        target = root / rel
        staged_now[rel] = (_hashlib.sha256(
            target.read_bytes()).hexdigest()
            if target.is_file() else None)
    observation["staged_shas_now"] = staged_now
    observation["staged_shas_match"] = (
        staged_now == EXPECTED_STAGED_SHAS)
    det_labels_file = root / EXPECTED_DETECTOR_LABELS_PATH
    det_summary_file = root / EXPECTED_DETECTOR_SUMMARY_PATH
    if det_labels_file.is_file():
        observation["detector_labels_sha_now"] = _hashlib.sha256(
            det_labels_file.read_bytes()).hexdigest()
        observation["detector_labels_sha_matches_pin"] = (
            observation["detector_labels_sha_now"]
            == EXPECTED_DETECTOR_LABELS_SHA256)
    if det_summary_file.is_file():
        observation["detector_summary_sha_now"] = _hashlib.sha256(
            det_summary_file.read_bytes()).hexdigest()
        observation["detector_summary_sha_matches_pin"] = (
            observation["detector_summary_sha_now"]
            == EXPECTED_DETECTOR_SUMMARY_SHA256)
    summary_file = root / SUMMARY_PATH
    ledger_file = root / LEDGER_PATH
    if summary_file.is_file():
        observation["summary_exists"] = True
        raw_summary = summary_file.read_bytes()
        observation["summary_sha256"] = _hashlib.sha256(
            raw_summary).hexdigest()
        summary = _json.loads(raw_summary.decode("utf-8"))
        observation["summary_variant_aggregates"] = summary.get(
            "variant_aggregates")
        self_claims: dict[str, Any] = {}
        for key in EXPECTED_SUMMARY_SELF_CLAIMS:
            self_claims[key] = summary.get(key)
        observation["summary_self_claims"] = self_claims
        observation["summary_scope_locks"] = summary.get(
            "scope_locks")
        observation["summary_labels_input_sha256_before"] = (
            summary.get("labels_input_sha256_before"))
        observation["summary_labels_input_sha256_after"] = (
            summary.get("labels_input_sha256_after"))
        observation["summary_summary_input_sha256_before"] = (
            summary.get("summary_input_sha256_before"))
        observation["summary_summary_input_sha256_after"] = (
            summary.get("summary_input_sha256_after"))
        observation["summary_source_files_sha256_before"] = (
            summary.get("source_files_sha256_before"))
        observation["summary_source_files_sha256_after"] = (
            summary.get("source_files_sha256_after"))
        observation[
            "summary_inputs_unchanged_during_evaluation"] = (
            summary.get("inputs_unchanged_during_evaluation"))
        observation["summary_ledger_sha256"] = summary.get(
            "ledger_sha256")
    if ledger_file.is_file():
        observation["ledger_exists"] = True
        observation["ledger_sha256"] = _hashlib.sha256(
            ledger_file.read_bytes()).hexdigest()
    return observation


def certify_c8_replay_review(observation: Any) -> dict[str, Any]:
    """Pure certification of an observation against the frozen facts.
    Never raises."""
    failures: list[str] = []
    if not isinstance(observation, dict):
        return {"certified": False,
                "failures": ["observation_not_a_dict"]}
    o = observation
    if not o.get("ledger_exists"):
        failures.append("ledger_artifact_missing")
    if not o.get("summary_exists"):
        failures.append("summary_artifact_missing")
    if failures:
        return {"certified": False, "failures": failures}
    if o.get("ledger_sha256") != EXPECTED_LEDGER_SHA256:
        failures.append("ledger_sha_mismatch")
    if o.get("summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_mismatch")
    if o.get("summary_ledger_sha256") != EXPECTED_LEDGER_SHA256:
        failures.append("summary_self_reported_ledger_sha_mismatch")
    if o.get("summary_variant_aggregates") != (
            EXPECTED_VARIANT_AGGREGATES):
        failures.append("variant_aggregates_mismatch")
    if o.get("summary_self_claims") != EXPECTED_SUMMARY_SELF_CLAIMS:
        failures.append("summary_self_claims_mismatch")
    if o.get("summary_scope_locks") != EXPECTED_SCOPE_LOCKS:
        failures.append("summary_scope_locks_mismatch")
    if o.get(
            "summary_labels_input_sha256_before"
    ) != EXPECTED_DETECTOR_LABELS_SHA256:
        failures.append("summary_labels_input_sha_before_mismatch")
    if o.get(
            "summary_labels_input_sha256_after"
    ) != EXPECTED_DETECTOR_LABELS_SHA256:
        failures.append("summary_labels_input_sha_after_mismatch")
    if o.get(
            "summary_summary_input_sha256_before"
    ) != EXPECTED_DETECTOR_SUMMARY_SHA256:
        failures.append(
            "summary_detector_summary_sha_before_mismatch")
    if o.get(
            "summary_summary_input_sha256_after"
    ) != EXPECTED_DETECTOR_SUMMARY_SHA256:
        failures.append(
            "summary_detector_summary_sha_after_mismatch")
    if o.get(
            "summary_source_files_sha256_before"
    ) != EXPECTED_STAGED_SHAS:
        failures.append("summary_source_sha_before_mismatch")
    if o.get(
            "summary_source_files_sha256_after"
    ) != EXPECTED_STAGED_SHAS:
        failures.append("summary_source_sha_after_mismatch")
    if o.get(
            "summary_inputs_unchanged_during_evaluation"
    ) is not True:
        failures.append("inputs_changed_during_evaluation")
    if o.get("staged_shas_match") is not True:
        failures.append("staged_data_shas_changed_post_replay")
    if o.get("detector_labels_sha_matches_pin") is not True:
        failures.append("detector_labels_sha_drifted_post_replay")
    if o.get("detector_summary_sha_matches_pin") is not True:
        failures.append("detector_summary_sha_drifted_post_replay")
    if o.get("artifacts_tracked_in_git"):
        failures.append("runner_and_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c8_replay_review(repo_root: Any,
                           tracked_paths: Any = ()
                           ) -> dict[str, Any]:
    """Observe read-only and certify; chain-gated on the full pushed
    C8 lane through the labels review plus V3 blacklist + V2 +
    Recommendation V1 + Autopilot V1 + seven-record rejection ledger."""
    record: dict[str, Any] = {
        "schema_version": C8RR_SCHEMA_VERSION, "label": C8RR_LABEL,
        "mode": C8RR_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "head_at_replay": HEAD_AT_REPLAY,
        "runner_path_untracked_only": RUNNER_PATH,
        "ledger_path": LEDGER_PATH, "summary_path": SUMMARY_PATH,
        "expected_ledger_sha256": EXPECTED_LEDGER_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_detector_labels_path":
            EXPECTED_DETECTOR_LABELS_PATH,
        "expected_detector_summary_path":
            EXPECTED_DETECTOR_SUMMARY_PATH,
        "expected_detector_labels_sha256":
            EXPECTED_DETECTOR_LABELS_SHA256,
        "expected_detector_summary_sha256":
            EXPECTED_DETECTOR_SUMMARY_SHA256,
        "expected_staged_shas": dict(EXPECTED_STAGED_SHAS),
        "expected_sample_tag": EXPECTED_SAMPLE_TAG,
        "expected_start_inclusive_utc":
            EXPECTED_START_INCLUSIVE_UTC,
        "expected_end_inclusive_utc": EXPECTED_END_INCLUSIVE_UTC,
        "expected_replay_policy": {
            key: (list(value) if isinstance(value, tuple) else value)
            for key, value in EXPECTED_REPLAY_POLICY.items()},
        "expected_accepted_input_count":
            EXPECTED_ACCEPTED_INPUT_COUNT,
        "expected_variant_aggregates": {
            name: dict(value)
            for name, value in EXPECTED_VARIANT_AGGREGATES.items()},
        "expected_per_variant_identity_checks":
            dict(EXPECTED_PER_VARIANT_IDENTITY_CHECKS),
        "expected_headline_finding":
            dict(EXPECTED_HEADLINE_FINDING),
        "expected_summary_self_claims":
            dict(EXPECTED_SUMMARY_SELF_CLAIMS),
        "expected_scope_locks": dict(EXPECTED_SCOPE_LOCKS),
        "frozen_review_findings": list(FROZEN_REVIEW_FINDINGS),
        "claim_locks": list(CLAIM_LOCKS),
        "ledger_status_seven_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_review_only": True,
        "is_a_rescue_attempt": False,
        "edit_token_applied_by_this_gate": False,
        "rejection_decision_made_by_this_gate": False,
        "replay_re_run_authorized_by_this_gate": False,
        "relabel_authorized_by_this_gate": False,
        "detector_change_authorized_by_this_gate": False,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_real_candle_detection": False,
        "runs_relabel": False, "runs_replay": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False, "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "uses_account": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False,
        "contains_portfolio_allocation_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "creates_detector_implementation_now": False,
        "computes_pnl_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_real_candle_detection": False,
        "unlocks_replay_now": False, "unlocks_relabel_now": False,
        "unlocks_edit_token_now": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "current_loop_stage": CURRENT_LOOP_STAGE,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS)
    record["ledger_status_seven_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C8RR_BLOCKED
        record["blockers"].append("seven_record_ledger_broken")
        return record
    if build_candidate_8_family_proposal()["verdict"] != (
            VERDICT_C8P_READY):
        record["verdict"] = VERDICT_C8RR_BLOCKED
        record["blockers"].append(
            "candidate_8_proposal_not_certifying")
        return record
    if build_candidate_8_spec_review()["verdict"] != VERDICT_C8S_READY:
        record["verdict"] = VERDICT_C8RR_BLOCKED
        record["blockers"].append(
            "candidate_8_spec_review_not_certifying")
        return record
    if build_candidate_8_detector_spec_contract()["verdict"] != (
            VERDICT_C8D_READY):
        record["verdict"] = VERDICT_C8RR_BLOCKED
        record["blockers"].append(
            "candidate_8_detector_spec_not_certifying")
        return record
    if build_candidate_8_dry_run_review()["verdict"] != (
            VERDICT_C8R_FROZEN):
        record["verdict"] = VERDICT_C8RR_BLOCKED
        record["blockers"].append(
            "candidate_8_dry_run_review_not_certifying")
        return record
    if build_c8_labels_review(repo_root, tracked_paths)[
            "verdict"] != VERDICT_C8L_FROZEN:
        record["verdict"] = VERDICT_C8RR_BLOCKED
        record["blockers"].append(
            "candidate_8_labels_review_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C8RR_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C8RR_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C8RR_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C8RR_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observation = observe_c8_replay(repo_root, tracked_paths)
    result = certify_c8_replay_review(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C8RR_FROZEN if result["certified"]
                         else VERDICT_C8RR_REJECTED)
    return record


def validate_c8_replay_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C8RR_FROZEN,
                                VERDICT_C8RR_REJECTED,
                                VERDICT_C8RR_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("head_at_replay") != HEAD_AT_REPLAY:
        errors.append("head_at_replay_tampered")
    if r.get("expected_ledger_sha256") != EXPECTED_LEDGER_SHA256:
        errors.append("ledger_sha_tampered")
    if r.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        errors.append("summary_sha_tampered")
    if r.get("expected_detector_labels_sha256") != (
            EXPECTED_DETECTOR_LABELS_SHA256):
        errors.append("detector_labels_sha_tampered")
    if r.get("expected_detector_summary_sha256") != (
            EXPECTED_DETECTOR_SUMMARY_SHA256):
        errors.append("detector_summary_sha_tampered")
    if r.get("expected_staged_shas") != EXPECTED_STAGED_SHAS:
        errors.append("staged_shas_tampered")
    if r.get("expected_sample_tag") != EXPECTED_SAMPLE_TAG:
        errors.append("sample_tag_tampered")
    expected_policy = {
        key: (list(value) if isinstance(value, tuple) else value)
        for key, value in EXPECTED_REPLAY_POLICY.items()}
    if r.get("expected_replay_policy") != expected_policy:
        errors.append("replay_policy_tampered")
    if r.get("expected_accepted_input_count") != (
            EXPECTED_ACCEPTED_INPUT_COUNT):
        errors.append("accepted_input_count_tampered")
    expected_variants = {
        name: dict(value)
        for name, value in EXPECTED_VARIANT_AGGREGATES.items()}
    if r.get("expected_variant_aggregates") != expected_variants:
        errors.append("variant_aggregates_tampered")
    if r.get("expected_per_variant_identity_checks") != (
            EXPECTED_PER_VARIANT_IDENTITY_CHECKS):
        errors.append("identity_checks_tampered")
    if r.get("expected_headline_finding") != (
            EXPECTED_HEADLINE_FINDING):
        errors.append("headline_finding_tampered")
    if r.get("expected_summary_self_claims") != (
            EXPECTED_SUMMARY_SELF_CLAIMS):
        errors.append("summary_self_claims_tampered")
    if r.get("expected_scope_locks") != EXPECTED_SCOPE_LOCKS:
        errors.append("scope_locks_tampered")
    if tuple(r.get("frozen_review_findings") or ()) != (
            FROZEN_REVIEW_FINDINGS):
        errors.append("frozen_review_findings_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    if r.get("current_loop_stage") != CURRENT_LOOP_STAGE:
        errors.append("current_loop_stage_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_review_only", True),
                      ("is_a_rescue_attempt", False)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("edit_token_applied_by_this_gate",
                "rejection_decision_made_by_this_gate",
                "replay_re_run_authorized_by_this_gate",
                "relabel_authorized_by_this_gate",
                "detector_change_authorized_by_this_gate"):
        if r.get(key) is not False:
            errors.append("downstream_lock_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_relabel", "runs_replay",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_replay_now", "unlocks_relabel_now",
                "unlocks_edit_token_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C8RR_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
    return {"valid": not errors, "errors": errors}

"""Candidate #15 -- slow_vol_targeted_time_series_momentum_v1 -- FORMAL REJECTION /
CLOSEOUT RECORD (PURE, RESEARCH ONLY).

Records the formal closeout of Candidate #15 as REJECTED_KEPT_ON_RECORD after the
fee-honest replay. Chain-gated on the FROZEN replay-results review carrying
decisive_outcome == REJECT_C15 and all_decisive_gates_pass == False (and the
genuine beats-random-entry positive intact).

It does NOTHING else: it does NOT re-run replay, NOT re-detect, NOT relabel, NOT
optimize, NOT run robustness / portfolio, NOT write files, NOT stage / commit /
push, and NOT touch any paper / live / broker / order surface. It only PRESERVES
the honest result and records the rejection + the research lesson. Every capability
flag is pinned False with a full scope_locks set.

HONEST RESULT PRESERVED: net-POSITIVE full sample (+111.03 R after 37 bps) and
BEATS the random-entry baseline (mean -4.31 R; 100th percentile) -- a real timing
signal -- BUT LOSES to matched buy-and-hold (111.03 vs 286.53 R), the BEAR regime
is net-negative (-0.91 R), and the SHORT side is net-negative (-1.16 R).

LESSON: a positive timing signal is not enough if it is just long-bull crypto
carry that underperforms buy-and-hold; beating random entry is necessary but not
sufficient. Same carry signature as C14.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.slow_vol_targeted_time_series_momentum_v1_replay_results_review_contract as _r15  # noqa: E501

RJ15_SCHEMA_VERSION = 1
RJ15_MODE = "RESEARCH_ONLY"
RJ15_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _r15.CANDIDATE_ID
CANDIDATE_FAMILY = _r15.CANDIDATE_FAMILY
CANDIDATE_NAME = _r15.CANDIDATE_NAME

VERDICT_RJ15_RECORDED = "C15_REJECTED_KEPT_ON_RECORD_FAILED_FEE_HONEST_REPLAY"
VERDICT_C15RR_FROZEN = _r15.VERDICT_C15RR_FROZEN
REJECTION_STATUS = "REJECTED_KEPT_ON_RECORD"

NEXT_REQUIRED_ACTION = (
    "NONE__C15_CLOSED__KEPT_ON_RECORD_AS_LONG_BULL_CARRY_UNDERPERFORMING_"
    "BUY_AND_HOLD_RESEARCH_LESSON")

CONCLUSION = (
    "A positive timing signal is not enough: slow vol-targeted time-series "
    "momentum on crypto-D1 is essentially long-bull carry that underperforms "
    "buy-and-hold, so beating random entry does not make it a durable tradeable "
    "edge.")

# --- pinned honest aggregates (from the frozen replay review) ---------------
NET_R_TOTAL_ALL_IN = _r15.NET_R_TOTAL_ALL_IN          # +111.034046
FORWARD_OOS_NET_R = _r15.FORWARD_OOS_NET_R            # +0.269899
PER_ASSET_NET_R = dict(_r15.PER_ASSET_NET_R)
PER_REGIME_NET_R = dict(_r15.PER_REGIME_NET_R)
PER_SIDE_NET_R = dict(_r15.PER_SIDE_NET_R)
BUY_AND_HOLD_NET_R_TOTAL = _r15.BUY_AND_HOLD_NET_R_TOTAL  # +286.528781
RANDOM_ENTRY_MEAN_NET_R = _r15.RANDOM_ENTRY_MEAN_NET_R    # -4.309887
RANDOM_ENTRY_PERCENTILE = _r15.RANDOM_ENTRY_PERCENTILE    # 1.0

# --- pushed evidence chain (the gates committed + pushed on origin) ----------
PUSHED_EVIDENCE_CHAIN = (
    {"stage": "strategy_family_tournament_proposal",
     "commit": "703ef52ce7917319a11f0881218b560c5f34c2e9"},
    {"stage": "candidate_family_spec",
     "commit": "601c984d857e3d61700d2c98dd12b98872ce60cf"},
    {"stage": "detector_spec_and_synthetic_dry_run",
     "commit": "5399925b1cb60260b5ed750b6ce3b5765e584a0b"},
    {"stage": "real_candle_labels_review",
     "commit": "36df56a32c20bd8e7d50b482450d281ddf1b0e00"},
    {"stage": "fee_honest_replay_results_review",
     "commit": "aaaa3a693b4077b2da68af009a498b35f9672552"},
)

# This rejected family would extend the canonical rejected ledger to 20 (C1-C15).
# Applying that bump to the REP / SARA ledgers is a SEPARATE authorized change.
REJECTED_FAMILY_NAME = "slow_vol_targeted_time_series_momentum"
PROPOSED_LEDGER_BUMP = {
    "from_count": 19, "to_count": 20, "add_family": REJECTED_FAMILY_NAME,
    "applied_here": False,
    "requires_separate_token": "UPDATE_REJECTED_LEDGERS_ADD_C15",
}

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_runs_replay", "re_detects", "relabels",
    "runs_labels", "runs_backtest", "optimizes_parameters", "runs_robustness",
    "runs_portfolio_compute", "fetches_data", "reads_real_data", "mutates_data",
    "stages_data", "auto_commits", "auto_pushes", "drops_cost_model",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "reactivates_candidate", "parks_as_active", "uses_one_edit_allowance",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def get_candidate_15_rejection_record_label() -> str:
    return (
        "Candidate #15 slow_vol_targeted_time_series_momentum_v1 rejection record "
        "(READ-ONLY, RESEARCH ONLY). REJECTED_KEPT_ON_RECORD after fee-honest "
        "replay -- NOT AN ACTIVE CANDIDATE. Net-positive and beats random, but "
        "loses to buy-and-hold with a net-negative bear regime and short side: "
        "long-bull carry, not a durable edge. NOT a profitability claim. NOT a "
        "paper/live-readiness claim.")


def get_candidate_15_rejection_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c15_rejection_record(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C15 rejection / closeout record. Pure; no I/O; chain-
    gated on the frozen REJECT_C15 replay review."""
    replay = _r15.build_c15_replay_review(repo_root, tracked_paths)
    replay_valid = _r15.validate_c15_replay_review(replay)["valid"]

    blockers: list = []
    if not replay_valid:
        blockers.append("c15_replay_review_invalid")
    if replay.get("verdict") != VERDICT_C15RR_FROZEN:
        blockers.append("c15_replay_review_not_frozen")
    if replay.get("decisive_outcome") != "REJECT_C15":
        blockers.append("c15_replay_outcome_not_reject")
    if replay.get("all_decisive_gates_pass") is not False:
        blockers.append("c15_replay_unexpectedly_passes")

    g = replay.get("decisive_gate_results") or {}
    record: dict[str, Any] = {
        "schema_version": RJ15_SCHEMA_VERSION, "mode": RJ15_MODE, "lane": RJ15_LANE,
        "label": get_candidate_15_rejection_record_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_rejection_record_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_RJ15_RECORDED if not blockers
                    else "C15_REJECTION_BLOCKED"),
        "rejection_status": REJECTION_STATUS,
        "is_active_candidate": False,
        "parked_as_active": False,
        "kept_on_record": True,
        "original_frozen_c15_result_unchanged": True,
        "added_to_rejected_family_ledger": True,
        # chain provenance
        "replay_review_verdict": replay.get("verdict"),
        "replay_decisive_outcome": replay.get("decisive_outcome"),
        "replay_all_decisive_gates_pass": replay.get("all_decisive_gates_pass"),
        "replay_beats_random_entry": g.get("beats_random_entry"),
        "replay_beats_buy_and_hold": g.get("beats_buy_and_hold"),
        # verbatim conclusion + lesson
        "conclusion": CONCLUSION,
        "kept_on_record_as": [
            "a positive ENTRY-TIMING signal (beats random entry) is NOT a durable "
            "edge on its own",
            "slow vol-targeted TSMOM on crypto-D1 is essentially LONG-BULL CARRY "
            "that underperforms BUY-AND-HOLD",
            "beating random is necessary but NOT sufficient -- the same carry "
            "signature that rejected C14",
        ],
        # preserved positives (do not erase)
        "key_positive_findings": [
            "full-sample net is POSITIVE after 37 bps (+111.034046 R)",
            "BEATS the random-entry baseline (mean -4.31 R) at the 100th percentile",
            "all three assets individually net-positive "
            "(BTC +41.26 / ETH +35.37 / SOL +34.40 R)",
            "turnover sane for a slow strategy (avg hold ~23 bars)",
            "forward-OOS 2026 marginally net-positive (+0.269899 R over 5 trades)",
        ],
        # preserved decisive rejection reasons (do not erase)
        "rejection_reasons": [
            "LOSES to matched buy-and-hold in R units (111.034046 vs 286.528781)",
            "BEAR regime net-NEGATIVE (-0.914353 R): single-regime dependence",
            "SHORT side net-NEGATIVE (-1.15739 R): one-sided / long-only fragility",
        ],
        "evidence_headline": {
            "net_positive_full_sample": True,
            "beats_random_entry": True,
            "all_assets_positive": True,
            "loses_to_buy_and_hold": True,
            "bear_regime_negative": True,
            "short_side_negative": True,
            "forward_oos_positive_but_thin": True,
        },
        # pinned numbers
        "net_r_total_all_in": NET_R_TOTAL_ALL_IN,
        "forward_oos_net_r": FORWARD_OOS_NET_R,
        "per_asset_net_r": dict(sorted(PER_ASSET_NET_R.items())),
        "per_regime_net_r": dict(sorted(PER_REGIME_NET_R.items())),
        "per_side_net_r": dict(sorted(PER_SIDE_NET_R.items())),
        "buy_and_hold_net_r_total": BUY_AND_HOLD_NET_R_TOTAL,
        "random_entry_mean_net_r": RANDOM_ENTRY_MEAN_NET_R,
        "random_entry_percentile_of_strategy": RANDOM_ENTRY_PERCENTILE,
        "all_in_round_trip_bps": _r15.ALL_IN_ROUND_TRIP_BPS,
        # evidence chain
        "pushed_evidence_chain": [dict(e) for e in PUSHED_EVIDENCE_CHAIN],
        "rejected_family_name": REJECTED_FAMILY_NAME,
        "proposed_ledger_bump": dict(PROPOSED_LEDGER_BUMP),
        "claim_locks": [
            "no_profitability_claim", "kept_on_record_not_active_candidate",
            "not_parked_as_active", "no_new_replay",
            "beats_random_entry_positive_preserved",
            "loses_to_buy_and_hold_disclosed", "bear_regime_negative_disclosed",
            "short_side_negative_disclosed", "conclusion_recorded_precisely",
        ],
        "human_review_required": True,
        "current_loop_stage": "rejection_record",
        "next_required_action": NEXT_REQUIRED_ACTION,
        # gates locked
        "robustness_gate_locked": True, "relabel_gate_locked": True,
        "replay_gate_locked": True, "one_edit_gate_locked": True,
        "portfolio_gate_locked": True, "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_new_replay": True, "no_re_detect": True, "no_relabel": True,
        "no_optimization": True, "no_one_edit": True, "no_robustness_run": True,
        "no_portfolio_compute": True, "no_data_fetch": True, "no_data_mutation": True,
        "no_reactivation": True, "no_parking_as_active": True,
        "no_stage": True, "no_commit": True, "no_push": True,
        "no_auto_commit": True, "no_auto_push": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c15_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only,
    rejection-record-only, chain-gated on the frozen REJECT_C15 replay review,
    keeps the candidate not-active / not-parked / kept-on-record, preserves the
    verbatim conclusion + the beats-random positive AND the buy-and-hold / bear /
    short rejection reasons (none can be flipped), cites the 5 pushed gate commits,
    and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != RJ15_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_rejection_record_only") is not True:
        failures.append("not_rejection_record_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_RJ15_RECORDED:
        failures.append("verdict_not_recorded")
    if record.get("rejection_status") != REJECTION_STATUS:
        failures.append("status_not_rejected_kept_on_record")

    # not active / not parked / kept on record
    if record.get("is_active_candidate") is not False:
        failures.append("must_not_be_active")
    if record.get("parked_as_active") is not False:
        failures.append("must_not_be_parked")
    if record.get("kept_on_record") is not True:
        failures.append("must_be_kept_on_record")
    if record.get("original_frozen_c15_result_unchanged") is not True:
        failures.append("frozen_result_changed")

    # chain gate on the REJECT replay review
    if record.get("replay_review_verdict") != VERDICT_C15RR_FROZEN:
        failures.append("replay_review_not_frozen")
    if record.get("replay_decisive_outcome") != "REJECT_C15":
        failures.append("replay_outcome_not_reject")
    if record.get("replay_all_decisive_gates_pass") is not False:
        failures.append("replay_unexpectedly_passes")

    # verbatim conclusion
    if record.get("conclusion") != CONCLUSION:
        failures.append("conclusion_tampered")

    # preserved positive: beats random (both the gate flag and the headline)
    if record.get("replay_beats_random_entry") is not True:
        failures.append("beats_random_positive_must_remain")
    eh = record.get("evidence_headline") or {}
    if eh.get("beats_random_entry") is not True:
        failures.append("headline_beats_random_must_remain")
    if eh.get("net_positive_full_sample") is not True:
        failures.append("headline_net_positive_must_remain")

    # preserved decisive negatives: cannot be flipped
    if record.get("replay_beats_buy_and_hold") is not False:
        failures.append("loses_to_buy_and_hold_must_remain")
    for k in ("loses_to_buy_and_hold", "bear_regime_negative",
              "short_side_negative"):
        if eh.get(k) is not True:
            failures.append("rejection_finding_cleared_%s" % k)

    # pinned numbers intact
    if record.get("net_r_total_all_in") != NET_R_TOTAL_ALL_IN:
        failures.append("net_total_tampered")
    if record.get("buy_and_hold_net_r_total") != BUY_AND_HOLD_NET_R_TOTAL:
        failures.append("bh_total_tampered")
    if (record.get("per_regime_net_r") or {}).get("bear", 0) >= 0:
        failures.append("bear_regime_sign_tampered")
    if (record.get("per_side_net_r") or {}).get("short", 0) >= 0:
        failures.append("short_side_sign_tampered")
    if record.get("all_in_round_trip_bps") != 37.0:
        failures.append("cost_model_tampered")

    # pushed evidence chain: 5 gate commits, each a 40-char sha
    chain = record.get("pushed_evidence_chain") or []
    stages = {e.get("stage"): e.get("commit") for e in chain}
    for required in ("strategy_family_tournament_proposal",
                     "candidate_family_spec",
                     "detector_spec_and_synthetic_dry_run",
                     "real_candle_labels_review",
                     "fee_honest_replay_results_review"):
        if required not in stages:
            failures.append("pushed_chain_missing_%s" % required)
        elif not (isinstance(stages[required], str)
                  and len(stages[required]) == 40):
            failures.append("pushed_chain_bad_commit_%s" % required)

    # ledger bump not applied here (separate token)
    pb = record.get("proposed_ledger_bump") or {}
    if pb.get("applied_here") is not False:
        failures.append("ledger_bump_must_not_be_applied_here")

    # gates locked
    for gate in ("robustness_gate_locked", "relabel_gate_locked",
                 "replay_gate_locked", "one_edit_gate_locked",
                 "portfolio_gate_locked", "paper_trading_gate_locked",
                 "micro_live_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_new_replay", "no_re_detect", "no_relabel", "no_optimization",
                "no_robustness_run", "no_portfolio_compute", "no_reactivation",
                "no_commit", "no_push", "no_auto_commit", "no_auto_push",
                "no_broker", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

"""SPARTA CANDIDATE #6 EDITED INFORMATIONAL REPLAY RESULTS REVIEW /
EVIDENCE FREEZE (READ-ONLY, RESEARCH ONLY,
ALL VARIANTS NET NEGATIVE, NOT A PROFITABILITY CLAIM):
MULTI_SYMBOL_RELATIVE_STRENGTH_ROTATION_FILTER_V1.

Freezes the completed post-edit fee-honest replay of the 36 kept
edited accepted labels. THE ARITHMETIC, honestly, over the non-overlap
KEPT set per variant:

  2R: 5 hits / 18 stops / 2 timeouts on 25 kept
      gross -8.666284 R, fees -4.231551 R, NET -12.897835 R
  3R: 3 / 19 / 2 on 24 kept
      gross -10.666284 R, fees -4.127007 R, NET -14.793291 R
  4R: 2 / 18 / 2 on 22 kept
      gross -10.666284 R, fees -3.798458 R, NET -14.464742 R

ALL VARIANTS NET-NEGATIVE AND GROSS-NEGATIVE. Hit rates 20.0% / 12.5%
/ 9.1% sit below the 33.3% / 25.0% / 20.0% gross breakeven rates at
every target. Same-symbol non-overlap reduced 36 eligible kept setups
to 25/24/22 closed trades and skipped 37 total across the three
variants -- ~30% of variant slots vs the original 82% (the 24-bar
clustering filter worked structurally to reduce density). Max drawdown
EXCEEDS the total net loss in every variant (-17.46 / -17.45 / -17.45
R), so the curve spent time deeper underwater than its final result.

EDITED RESULTS WORSENED VERSUS ORIGINAL:
  2R hit rate 23.1% -> 20.0%; net R -11.085290 -> -12.897835
  3R hit rate 16.7% -> 12.5%; net R -10.846129 -> -14.793291
  4R hit rate 14.3% ->  9.1%; net R  -8.340989 -> -14.464742

The 24-bar clustering filter reduced overlap density as designed, but
did NOT rescue per-trade edge. The family hypothesis (cross-sectional
rank-#1 as edge on BTCUSD/ETHUSD/SOLUSD over this ~40-day window) is
twice unsupported: once on the original 135-label sample, and once on
the post-edit 36-label sample. The family's single edit token is
permanently spent on origin/master and cannot be refunded.

THIS CANNOT PROMOTE, cannot approve paper/live, cannot create the
rejection record, and cannot support a profitability claim or winner
wording. Whether to formally author the sixth rejection record or
close the family without one is the HUMAN decision at the next gate.

This module observes the untracked edited-replay artifacts READ-ONLY,
recounts every aggregate from the raw rows (re-applying the pushed
non-overlap filter), and certifies the frozen facts. It reruns
nothing, fetches nothing, and authorizes nothing.
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
from sparta_commander.eth_sol_relative_strength_pullback_continuation_detector_spec_contract import (
    apply_same_symbol_non_overlap,
)
from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
    REJECTION_STATUS as C5_STATUS,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_dry_run_review_contract import (
    VERDICT_C6R_FROZEN,
    build_c6_dry_run_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_edited_real_candle_labels_review_contract import (
    EXPECTED_KEPT_ACCEPTED_SETUP_IDS,
    EXPECTED_LABELS_SHA256 as EDITED_LABELS_SHA256,
    EXPECTED_SUMMARY_SHA256 as EDITED_SUMMARY_SHA256,
    VERDICT_C6EL_FROZEN,
    build_c6_edited_labels_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_family_proposal_contract import (
    CANDIDATE_ID,
    VERDICT_C6P_READY,
    build_candidate_6_family_proposal,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_real_candle_labels_review_contract import (
    VERDICT_C6L_FROZEN,
    build_c6_labels_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_replay_results_review_contract import (
    EXPECTED_VARIANTS as ORIGINAL_REPLAY_VARIANTS,
    HONEST_VERDICT as ORIGINAL_REPLAY_VERDICT,
    VERDICT_C6RR_FROZEN,
    build_c6_replay_results_review,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_single_edit_clustering_filter_contract import (
    VERDICT_C6E_READY,
    build_c6_single_edit_clustering_filter,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_spec_review_contract import (
    VERDICT_C6S_READY,
    build_candidate_6_spec_review,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)

C6EER_SCHEMA_VERSION = (
    "multi_symbol_relative_strength_rotation_filter_edited_replay"
    "_results_review.v1")
C6EER_LABEL = (
    "SPARTA Candidate #6 Edited Informational Replay Results Review / "
    "Evidence Freeze (READ-ONLY, RESEARCH ONLY, ALL VARIANTS NET "
    "NEGATIVE, NOT A PROFITABILITY CLAIM)")
C6EER_MODE = "RESEARCH_ONLY"
VERDICT_C6EER_FROZEN = (
    "C6_EDITED_REPLAY_RESULTS_REVIEW_INFORMATION_ONLY_FROZEN")
VERDICT_C6EER_REJECTED = (
    "C6_EDITED_REPLAY_RESULTS_REVIEW_REJECTED")
VERDICT_C6EER_BLOCKED = (
    "C6_EDITED_REPLAY_RESULTS_REVIEW_BLOCKED")
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_C6_REJECTION_RECORD_OR_CLOSE_FAMILY")

HONEST_VERDICT = "edited_edge_failed"

HEAD_AT_EDITED_REPLAY = "e4e818bd2887790a5c18089e352197d73d52e7a3"
RUNNER_PATH = "tools/c6_edited_fee_honest_replay_36_once.py"
RESULTS_PATH = ("data/rs_rotation_c6/edited_replay/"
                "c6_edited_replay_results_2026-05-02_2026-06-10.jsonl")
SUMMARY_PATH = ("data/rs_rotation_c6/edited_replay/"
                "c6_edited_replay_summary_2026-05-02_2026-06-10.json")
EXPECTED_RESULTS_SHA256 = (
    "b83a4d697219fe8c3635bac7f6ca7baf86e5ecb29b99a35693446bafa7f884f0")
EXPECTED_SUMMARY_SHA256 = (
    "150cb5483107fd88474a8989798450209da696b148dd79b9fda1b55bd6434fc6")

EXPECTED_INPUTS = {
    "edited_labels_sha256": EDITED_LABELS_SHA256,
    "edited_summary_sha256": EDITED_SUMMARY_SHA256,
    "edited_accepted_count_BTCUSD": 9,
    "edited_accepted_count_ETHUSD": 11,
    "edited_accepted_count_SOLUSD": 16,
    "edited_accepted_count_total": 36,
}

EXPECTED_VARIANTS = {
    "2r": {"eligible_setups": 36, "skipped_overlap": 11,
           "kept": 25, "hits": 5, "stops": 18, "timeouts": 2,
           "hit_rate_pct": 20.0, "gross_breakeven_rate_pct": 33.3,
           "gross_r_total": -8.666284, "fee_r_total": 4.231551,
           "net_r_total": -12.897835, "avg_net_r": -0.515913,
           "max_drawdown_r": -17.464416},
    "3r": {"eligible_setups": 36, "skipped_overlap": 12,
           "kept": 24, "hits": 3, "stops": 19, "timeouts": 2,
           "hit_rate_pct": 12.5, "gross_breakeven_rate_pct": 25.0,
           "gross_r_total": -10.666284, "fee_r_total": 4.127007,
           "net_r_total": -14.793291, "avg_net_r": -0.616387,
           "max_drawdown_r": -17.448356},
    "4r": {"eligible_setups": 36, "skipped_overlap": 14,
           "kept": 22, "hits": 2, "stops": 18, "timeouts": 2,
           "hit_rate_pct": 9.1, "gross_breakeven_rate_pct": 20.0,
           "gross_r_total": -10.666284, "fee_r_total": 3.798458,
           "net_r_total": -14.464742, "avg_net_r": -0.657488,
           "max_drawdown_r": -17.448356},
}

EXPECTED_PER_SYMBOL = {
    "BTCUSD": {"2r_trades": 5, "2r_net": -5.409106,
               "3r_trades": 5, "3r_net": -5.409106,
               "4r_trades": 5, "4r_net": -5.409106},
    "ETHUSD": {"2r_trades": 9, "2r_net": -4.867937,
               "3r_trades": 9, "3r_net": -6.867937,
               "4r_trades": 9, "4r_net": -5.867937},
    "SOLUSD": {"2r_trades": 11, "2r_net": -2.620792,
               "3r_trades": 10, "3r_net": -2.516248,
               "4r_trades": 8, "4r_net": -3.187699},
}

EXPECTED_OVERLAP_SKIPPED_TOTAL = 37  # 11 + 12 + 14

# auto-rejection triggers fired by the post-edit replay
EXPECTED_AUTO_REJECTION_TRIGGERS = {
    "any_variant_net_negative": True,
    "any_variant_gross_negative": True,
    "any_variant_hit_rate_below_gross_breakeven": True,
    "any_variant_kept_set_below_minimum_evaluable_count": False,
    "minimum_evaluable_kept_per_variant": 10,
    "edited_labels_sha_mismatch": False,
    "edited_summary_sha_mismatch": False,
    "staged_data_sha_mismatch": False,
    "any_inviolable_rule_changed": False,
    "any_second_edit_attempted": False,
}

# worsened-vs-original comparison (locked)
EXPECTED_WORSENED_VS_ORIGINAL = {
    "2r": {
        "original_net_r": ORIGINAL_REPLAY_VARIANTS["2r"]["net_r_total"],
        "edited_net_r": -12.897835,
        "net_r_delta_deeper": True,
        "original_hit_rate_pct":
            ORIGINAL_REPLAY_VARIANTS["2r"]["hit_rate_pct"],
        "edited_hit_rate_pct": 20.0,
        "hit_rate_worsened": True},
    "3r": {
        "original_net_r": ORIGINAL_REPLAY_VARIANTS["3r"]["net_r_total"],
        "edited_net_r": -14.793291,
        "net_r_delta_deeper": True,
        "original_hit_rate_pct":
            ORIGINAL_REPLAY_VARIANTS["3r"]["hit_rate_pct"],
        "edited_hit_rate_pct": 12.5,
        "hit_rate_worsened": True},
    "4r": {
        "original_net_r": ORIGINAL_REPLAY_VARIANTS["4r"]["net_r_total"],
        "edited_net_r": -14.464742,
        "net_r_delta_deeper": True,
        "original_hit_rate_pct":
            ORIGINAL_REPLAY_VARIANTS["4r"]["hit_rate_pct"],
        "edited_hit_rate_pct": 9.1,
        "hit_rate_worsened": True},
}

FROZEN_REPLAY_RULES = (
    "round-trip fee 27 bps; variants 2r/3r/4r only",
    "same-symbol non-overlap applied per variant after the pushed "
    "24-bar label-time clustering filter",
    "entry/stop/target from frozen edited labels only; no detector "
    "rerun, no label changes",
    "replay starts on the bar after the event bar; no same-bar entry; "
    "no lookahead",
    "conservative stop-before-target same-bar ordering",
    "adverse gaps at the open count fully against the trade; "
    "favorable gaps capped at the target price",
    "no edit, no paper, no live, no profitability claim, no "
    "rejection record in this gate",
)

FROZEN_REVIEW_FINDINGS = (
    "all variants net-negative after 27 bps fees",
    "all variants gross-negative before fees",
    "hit rates below the gross breakeven rate at 2r, 3r, and 4r",
    "the 24-bar clustering filter reduced replay-time overlap from "
    "334 to 37 total skips (~82% to ~30% of variant slots) as "
    "designed",
    "the clustering filter did not rescue per-trade edge; hit rates "
    "and net R worsened versus the original 135-label replay at "
    "every variant",
    "max drawdown exceeds the total net loss in each variant",
    "sample size after non-overlap is 22-25 independent kept trades "
    "per variant -- above the minimum_evaluable_kept_per_variant "
    "threshold but small",
    "the family hypothesis (cross-sectional ranking as edge) is now "
    "twice unsupported on this sample window: once on the original "
    "135-label sample and once on the post-edit 36-label sample",
    "auto-rejection triggers fired: net-negative, gross-negative, "
    "hit-rate-below-breakeven at every variant",
    "no profitability, winner, or paper/live claim is allowed; this "
    "gate does NOT author the rejection record",
)

CLAIM_LOCKS = (
    "no_edit_authorized_by_this_gate",
    "no_second_edit_possible",
    "no_rejection_record_created_by_this_gate",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_profitability_claim",
    "no_winner_wording",
)


def get_c6_edited_replay_review_label() -> str:
    return C6EER_LABEL


def observe_c6_edited_replay_results(repo_root: Any,
                                     tracked_paths: Any = ()
                                     ) -> dict[str, Any]:
    """Read the edited-replay artifacts READ-ONLY and recompute every
    aggregate from the raw rows, re-applying the pushed non-overlap
    filter. Never raises on missing files."""
    observation: dict[str, Any] = {
        "results_exists": False, "summary_exists": False,
        "results_sha256": None, "summary_sha256": None,
        "row_count": None, "setup_ids": None,
        "variants": None, "per_symbol": None,
        "overlap_skipped_total": None,
        "all_variants_net_negative": None,
        "all_variants_gross_negative": None,
        "all_hit_rates_below_breakeven": None,
        "max_drawdown_exceeds_net_loss_per_variant": None,
        "summary_honest_verdict": None,
        "summary_auto_rejection_triggers": None,
        "summary_replayed_setup_ids": None,
        "summary_no_second_edit_attempted": None,
        "summary_no_detector_rerun": None,
        "summary_no_label_change": None,
        "summary_no_rejection_record_in_this_gate": None,
        "summary_no_paper_or_live_authorization": None,
        "summary_no_profitability_claim": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/") for p in (tracked_paths or ())}
    for rel in (RESULTS_PATH, SUMMARY_PATH, RUNNER_PATH):
        if rel in tracked:
            observation["artifacts_tracked_in_git"].append(rel)
    summary_file = root / SUMMARY_PATH
    results_file = root / RESULTS_PATH
    if summary_file.is_file():
        observation["summary_exists"] = True
        raw_summary = summary_file.read_bytes()
        observation["summary_sha256"] = _hashlib.sha256(
            raw_summary).hexdigest()
        summary = _json.loads(raw_summary.decode("utf-8"))
        observation["summary_honest_verdict"] = summary.get(
            "honest_verdict")
        observation["summary_auto_rejection_triggers"] = summary.get(
            "auto_rejection_triggers")
        observation["summary_replayed_setup_ids"] = tuple(sorted(
            summary.get("replayed_setup_ids") or ()))
        observation["summary_no_second_edit_attempted"] = summary.get(
            "no_second_edit_attempted")
        observation["summary_no_detector_rerun"] = summary.get(
            "no_detector_rerun")
        observation["summary_no_label_change"] = summary.get(
            "no_label_change")
        observation["summary_no_rejection_record_in_this_gate"] = (
            summary.get("no_rejection_record_in_this_gate"))
        observation["summary_no_paper_or_live_authorization"] = (
            summary.get("no_paper_or_live_authorization"))
        observation["summary_no_profitability_claim"] = summary.get(
            "no_profitability_claim")
    if not results_file.is_file():
        return observation
    observation["results_exists"] = True
    raw = results_file.read_bytes()
    observation["results_sha256"] = _hashlib.sha256(raw).hexdigest()
    rows = [_json.loads(line)
            for line in raw.decode("utf-8").splitlines()]
    observation["row_count"] = len(rows)
    observation["setup_ids"] = tuple(sorted(
        row["setup_id"] for row in rows))
    variants: dict[str, Any] = {}
    per_symbol: dict[str, Any] = {sym: {} for sym in
                                  ("BTCUSD", "ETHUSD", "SOLUSD")}
    overlap_skipped_total = 0
    net_negative = []
    gross_negative = []
    below_breakeven = []
    mdd_exceeds = []
    for name in ("2r", "3r", "4r"):
        overlap = apply_same_symbol_non_overlap(rows, name)
        kept, removed = overlap["kept"], overlap["removed"]
        overlap_skipped_total += len(removed)
        outcomes = [(row, row["variants"][name]) for row in kept]
        hits = sum(1 for _r, v in outcomes if v["outcome"] == "target")
        stops = sum(1 for _r, v in outcomes if v["outcome"] == "stop")
        timeouts = sum(1 for _r, v in outcomes
                       if v["outcome"] == "timeout")
        gross = round(sum(v["gross_r"] for _r, v in outcomes), 6)
        fees = round(sum(row["cost_r"] for row, _v in outcomes), 6)
        net = round(sum(v["net_r"] for _r, v in outcomes), 6)
        avg = round(net / len(outcomes), 6) if outcomes else None
        chrono = sorted(kept, key=lambda r: r["variants"][name][
            "exit_time_utc"])
        cum, peak, mdd = 0.0, 0.0, 0.0
        for row in chrono:
            cum += row["variants"][name]["net_r"]
            peak = max(peak, cum)
            mdd = min(mdd, cum - peak)
        mdd = round(mdd, 6)
        variants[name] = {
            "eligible_setups": len(rows),
            "skipped_overlap": len(removed),
            "kept": len(kept),
            "hits": hits, "stops": stops, "timeouts": timeouts,
            "hit_rate_pct": (round(hits / len(kept) * 100.0, 1)
                             if kept else None),
            "gross_breakeven_rate_pct": EXPECTED_VARIANTS[name][
                "gross_breakeven_rate_pct"],
            "gross_r_total": gross, "fee_r_total": fees,
            "net_r_total": net, "avg_net_r": avg,
            "max_drawdown_r": mdd}
        net_negative.append(net < 0)
        gross_negative.append(gross < 0)
        below_breakeven.append(
            variants[name]["hit_rate_pct"] is not None
            and variants[name]["hit_rate_pct"]
            < EXPECTED_VARIANTS[name]["gross_breakeven_rate_pct"])
        mdd_exceeds.append(mdd < net)
        for sym in ("BTCUSD", "ETHUSD", "SOLUSD"):
            sym_rows = [(row, v) for row, v in outcomes
                        if row["symbol"] == sym]
            per_symbol[sym][name + "_trades"] = len(sym_rows)
            per_symbol[sym][name + "_net"] = round(
                sum(v["net_r"] for _r, v in sym_rows), 6)
    observation["variants"] = variants
    observation["per_symbol"] = per_symbol
    observation["overlap_skipped_total"] = overlap_skipped_total
    observation["all_variants_net_negative"] = all(net_negative)
    observation["all_variants_gross_negative"] = all(gross_negative)
    observation["all_hit_rates_below_breakeven"] = all(below_breakeven)
    observation["max_drawdown_exceeds_net_loss_per_variant"] = all(
        mdd_exceeds)
    return observation


def certify_c6_edited_replay_results(observation: Any
                                     ) -> dict[str, Any]:
    """Pure certification of an observation against the frozen facts."""
    failures: list[str] = []
    if not isinstance(observation, dict):
        return {"certified": False,
                "failures": ["observation_not_a_dict"]}
    o = observation
    if not o.get("results_exists"):
        failures.append("edited_results_artifact_missing")
    if not o.get("summary_exists"):
        failures.append("edited_summary_artifact_missing")
    if failures:
        return {"certified": False, "failures": failures}
    if o.get("results_sha256") != EXPECTED_RESULTS_SHA256:
        failures.append("edited_results_sha_mismatch")
    if o.get("summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("edited_summary_sha_mismatch")
    if o.get("row_count") != 36:
        failures.append("row_count_not_36")
    if o.get("setup_ids") != tuple(sorted(
            EXPECTED_KEPT_ACCEPTED_SETUP_IDS)):
        failures.append("setup_ids_do_not_match_frozen_kept_set")
    if o.get("summary_replayed_setup_ids") != tuple(sorted(
            EXPECTED_KEPT_ACCEPTED_SETUP_IDS)):
        failures.append("summary_replayed_setup_ids_mismatch")
    variants = o.get("variants") or {}
    for name, expected in EXPECTED_VARIANTS.items():
        got = variants.get(name) or {}
        for key, value in expected.items():
            if got.get(key) != value:
                failures.append(
                    "variant_fact_mismatch:%s:%s" % (name, key))
        if (got.get("hits") or 0) + (got.get("stops") or 0) \
                + (got.get("timeouts") or 0) != got.get("kept"):
            failures.append("variant_counts_inconsistent:" + name)
    if o.get("per_symbol") != EXPECTED_PER_SYMBOL:
        failures.append("per_symbol_mismatch")
    if o.get("overlap_skipped_total") != EXPECTED_OVERLAP_SKIPPED_TOTAL:
        failures.append("overlap_skipped_total_mismatch")
    if o.get("all_variants_net_negative") is not True:
        failures.append("net_negative_fact_broken")
    if o.get("all_variants_gross_negative") is not True:
        failures.append("gross_negative_fact_broken")
    if o.get("all_hit_rates_below_breakeven") is not True:
        failures.append("hit_rates_below_breakeven_fact_broken")
    if o.get("max_drawdown_exceeds_net_loss_per_variant") is not True:
        failures.append("max_drawdown_exceeds_net_loss_fact_broken")
    if o.get("summary_honest_verdict") != HONEST_VERDICT:
        failures.append("summary_honest_verdict_mismatch")
    triggers = o.get("summary_auto_rejection_triggers") or {}
    for key, expected_value in EXPECTED_AUTO_REJECTION_TRIGGERS.items():
        if triggers.get(key) != expected_value:
            failures.append(
                "auto_rejection_trigger_mismatch:" + key)
    if o.get("summary_no_second_edit_attempted") is not True:
        failures.append("summary_must_record_no_second_edit_attempted")
    if o.get("summary_no_detector_rerun") is not True:
        failures.append("summary_must_record_no_detector_rerun")
    if o.get("summary_no_label_change") is not True:
        failures.append("summary_must_record_no_label_change")
    if o.get("summary_no_rejection_record_in_this_gate") is not True:
        failures.append(
            "summary_must_record_no_rejection_record_in_this_gate")
    if o.get("summary_no_paper_or_live_authorization") is not True:
        failures.append("summary_must_record_no_paper_or_live")
    if o.get("summary_no_profitability_claim") is not True:
        failures.append("summary_must_record_no_profitability_claim")
    if o.get("artifacts_tracked_in_git"):
        failures.append(
            "edited_runner_and_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c6_edited_replay_results_review(repo_root: Any,
                                          tracked_paths: Any = ()
                                          ) -> dict[str, Any]:
    """Observe read-only and certify; chain-gated on the full pushed
    C6 lane (proposal -> spec -> dry-run -> original labels -> original
    replay -> single-edit -> edited labels) plus Recommendation V1,
    Autopilot V1, and the five-record rejection ledger."""
    record: dict[str, Any] = {
        "schema_version": C6EER_SCHEMA_VERSION, "label": C6EER_LABEL,
        "mode": C6EER_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "honest_verdict": HONEST_VERDICT,
        "head_at_edited_replay": HEAD_AT_EDITED_REPLAY,
        "runner_path_untracked_only": RUNNER_PATH,
        "results_path": RESULTS_PATH, "summary_path": SUMMARY_PATH,
        "expected_results_sha256": EXPECTED_RESULTS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_inputs": dict(EXPECTED_INPUTS),
        "expected_variants": {key: dict(value) for key, value
                              in EXPECTED_VARIANTS.items()},
        "expected_per_symbol": {sym: dict(value) for sym, value
                                in EXPECTED_PER_SYMBOL.items()},
        "expected_overlap_skipped_total":
            EXPECTED_OVERLAP_SKIPPED_TOTAL,
        "expected_auto_rejection_triggers":
            dict(EXPECTED_AUTO_REJECTION_TRIGGERS),
        "expected_worsened_vs_original":
            {name: dict(value) for name, value
             in EXPECTED_WORSENED_VS_ORIGINAL.items()},
        "frozen_replay_rules": list(FROZEN_REPLAY_RULES),
        "frozen_review_findings": list(FROZEN_REVIEW_FINDINGS),
        "claim_locks": list(CLAIM_LOCKS),
        "edit_authorized_by_this_gate": False,
        "second_edit_possible": False,
        "rejection_record_created_by_this_gate": False,
        "structure_filter_modified_by_this_gate": False,
        "detector_changed_by_this_gate": False,
        "labels_changed_by_this_gate": False,
        "replay_rerun_by_this_gate": False,
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
        "contains_order_logic": False,
        "contains_portfolio_allocation_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False, "creates_data_artifacts_now": False,
        "modifies_staged_market_data": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    if not (C1_STATUS == C2_STATUS == C3_STATUS == C4_STATUS
            == C5_STATUS == "REJECTED_KEPT_ON_RECORD"):
        record["verdict"] = VERDICT_C6EER_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    if build_candidate_6_family_proposal()["verdict"] != (
            VERDICT_C6P_READY):
        record["verdict"] = VERDICT_C6EER_BLOCKED
        record["blockers"].append("family_proposal_not_certifying")
        return record
    if build_candidate_6_spec_review()["verdict"] != VERDICT_C6S_READY:
        record["verdict"] = VERDICT_C6EER_BLOCKED
        record["blockers"].append("spec_review_not_certifying")
        return record
    if build_c6_dry_run_review()["verdict"] != VERDICT_C6R_FROZEN:
        record["verdict"] = VERDICT_C6EER_BLOCKED
        record["blockers"].append("dry_run_review_not_certifying")
        return record
    labels_review = build_c6_labels_review(repo_root, tracked_paths)
    if labels_review["verdict"] != VERDICT_C6L_FROZEN:
        record["verdict"] = VERDICT_C6EER_BLOCKED
        record["blockers"].append(
            "original_labels_review_not_certifying")
        record["blockers"].extend(labels_review["failures"])
        return record
    replay_review = build_c6_replay_results_review(
        repo_root, tracked_paths)
    if replay_review["verdict"] != VERDICT_C6RR_FROZEN:
        record["verdict"] = VERDICT_C6EER_BLOCKED
        record["blockers"].append(
            "original_replay_results_review_not_certifying")
        record["blockers"].extend(replay_review["failures"])
        return record
    if replay_review.get("honest_verdict") != ORIGINAL_REPLAY_VERDICT:
        record["verdict"] = VERDICT_C6EER_BLOCKED
        record["blockers"].append(
            "original_replay_honest_verdict_mismatch")
        return record
    single_edit = build_c6_single_edit_clustering_filter(
        repo_root, tracked_paths)
    if single_edit["verdict"] != VERDICT_C6E_READY:
        record["verdict"] = VERDICT_C6EER_BLOCKED
        record["blockers"].append(
            "single_edit_contract_not_certifying")
        return record
    edited_labels = build_c6_edited_labels_review(
        repo_root, tracked_paths)
    if edited_labels["verdict"] != VERDICT_C6EL_FROZEN:
        record["verdict"] = VERDICT_C6EER_BLOCKED
        record["blockers"].append(
            "edited_labels_review_not_certifying")
        record["blockers"].extend(edited_labels["failures"])
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C6EER_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C6EER_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observation = observe_c6_edited_replay_results(
        repo_root, tracked_paths)
    result = certify_c6_edited_replay_results(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C6EER_FROZEN if result["certified"]
                         else VERDICT_C6EER_REJECTED)
    return record


def validate_c6_edited_replay_results_review(record: Any
                                             ) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C6EER_FROZEN,
                                VERDICT_C6EER_REJECTED,
                                VERDICT_C6EER_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("honest_verdict") != HONEST_VERDICT:
        errors.append("honest_verdict_tampered")
    if r.get("head_at_edited_replay") != HEAD_AT_EDITED_REPLAY:
        errors.append("head_tampered")
    if r.get("expected_results_sha256") != EXPECTED_RESULTS_SHA256:
        errors.append("results_sha_tampered")
    if r.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        errors.append("summary_sha_tampered")
    if r.get("expected_inputs") != EXPECTED_INPUTS:
        errors.append("inputs_tampered")
    expected_variants = {key: dict(value) for key, value
                         in EXPECTED_VARIANTS.items()}
    if r.get("expected_variants") != expected_variants:
        errors.append("variant_table_tampered")
    expected_split = {sym: dict(value) for sym, value
                      in EXPECTED_PER_SYMBOL.items()}
    if r.get("expected_per_symbol") != expected_split:
        errors.append("per_symbol_tampered")
    if r.get("expected_overlap_skipped_total") != (
            EXPECTED_OVERLAP_SKIPPED_TOTAL):
        errors.append("overlap_skipped_total_tampered")
    if r.get("expected_auto_rejection_triggers") != (
            EXPECTED_AUTO_REJECTION_TRIGGERS):
        errors.append("auto_rejection_triggers_tampered")
    expected_compare = {name: dict(value) for name, value
                        in EXPECTED_WORSENED_VS_ORIGINAL.items()}
    if r.get("expected_worsened_vs_original") != expected_compare:
        errors.append("worsened_vs_original_tampered")
    if tuple(r.get("frozen_replay_rules") or ()) != FROZEN_REPLAY_RULES:
        errors.append("replay_rules_tampered")
    if tuple(r.get("frozen_review_findings") or ()) != (
            FROZEN_REVIEW_FINDINGS):
        errors.append("review_findings_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    for key in ("edit_authorized_by_this_gate",
                "second_edit_possible",
                "rejection_record_created_by_this_gate",
                "structure_filter_modified_by_this_gate",
                "detector_changed_by_this_gate",
                "labels_changed_by_this_gate",
                "replay_rerun_by_this_gate"):
        if r.get(key) is not False:
            errors.append("downstream_lock_wrong:" + key)
    if r.get("verdict") == VERDICT_C6EER_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
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
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "modifies_staged_market_data",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading", "promotes_gate",
                "unlocks_downstream_gate", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    return {"valid": not errors, "errors": errors}

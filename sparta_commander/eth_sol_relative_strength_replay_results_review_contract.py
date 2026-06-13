"""SPARTA CANDIDATE #5 INFORMATIONAL REPLAY RESULTS REVIEW / EVIDENCE
FREEZE (READ-ONLY, RESEARCH ONLY):
ETH_SOL_RELATIVE_STRENGTH_PULLBACK_CONTINUATION_V1.

Freezes the completed fee-honest INFORMATIONAL replay of the 6 frozen
labels. THE ARITHMETIC, honestly, over the non-overlap KEPT set of 5:

  2R: 2 hits / 3 stops / 0 timeouts (40.0% vs 33.3% gross breakeven)
      gross +1.000001 R, fees -1.269642 R, NET -0.269641 R
  3R: 1 / 4 / 0 (20.0% vs 25.0%)  gross -0.999999, NET -2.269641 R
  4R: 1 / 4 / 0 (20.0% vs 20.0%)  gross +0.000001, NET -1.269641 R

ALL VARIANTS NET-NEGATIVE -- but 2R is GROSS-POSITIVE and 4R gross-flat:
fees, not gross edge, made 2R negative, and the margin (-0.27R) sits on
FIVE kept trades, which is noise-level. The non-overlap rule removed
SOLUSD_2026-05-06T06:00 (itself a winner) in every variant -- the honest
cost of the dedup rule, frozen as such. All replay signal concentrates
in 2 SOL trades from one week; ETH contributed only stops.

THIS CANNOT PROMOTE, cannot approve paper/live, and cannot support a
profitability claim. The family's single pre-committed edit remains
UNSPENT; replay/edit/reject remains the human decision. The structural
evidence points at trigger-window scarcity (372/411 pullback_too_long),
not at the floor or the RS gate.

This module observes the untracked replay artifacts READ-ONLY, recomputes
every aggregate from the raw per-trade rows (re-applying the pushed
non-overlap filter), and certifies the frozen facts. It reruns nothing,
fetches nothing, and authorizes nothing.
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
from sparta_commander.eth_sol_relative_strength_pullback_continuation_detector_spec_contract import (
    apply_same_symbol_non_overlap,
)
from sparta_commander.eth_sol_relative_strength_pullback_continuation_family_proposal_contract import (
    CANDIDATE_ID,
)
from sparta_commander.eth_sol_relative_strength_real_candle_labels_review_contract import (
    EXPECTED_LABELS_SHA256 as LABELS_ARTIFACT_SHA256,
    EXPECTED_SUMMARY_SHA256 as LABELS_SUMMARY_SHA256,
    VERDICT_C5L_FROZEN,
    build_c5_labels_review,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)

C5RR_SCHEMA_VERSION = (
    "eth_sol_relative_strength_replay_results_review.v1")
C5RR_LABEL = ("SPARTA Candidate #5 Informational Replay Results Review "
              "/ Evidence Freeze (READ-ONLY, RESEARCH ONLY, SMALL "
              "SAMPLE, ALL VARIANTS NET NEGATIVE, NOT A PROFITABILITY "
              "CLAIM)")
C5RR_MODE = "RESEARCH_ONLY"
VERDICT_C5RR_FROZEN = (
    "C5_REPLAY_RESULTS_REVIEW_INFORMATION_ONLY_FROZEN")
VERDICT_C5RR_REJECTED = "C5_REPLAY_RESULTS_REVIEW_REJECTED"
VERDICT_C5RR_BLOCKED = "C5_REPLAY_RESULTS_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C5_EDIT_OR_REJECT_AFTER_REPLAY"

CLASSIFICATION = (
    "C5_REPLAY_SMALL_SAMPLE_NEGATIVE_REJECT_OR_EDIT_DECISION")

HEAD_AT_REPLAY = "1216a9f4a6e0aea1f70ce99685bc9baf9fd61fac"
RUNNER_PATH = "tools/c5_fee_honest_replay_6_once.py"
RESULTS_PATH = ("data/relative_strength_c5/replay_results/"
                "c5_replay_results_2026-05-02_2026-06-10.jsonl")
SUMMARY_PATH = ("data/relative_strength_c5/replay_results/"
                "c5_replay_summary_2026-05-02_2026-06-10.json")
EXPECTED_RESULTS_SHA256 = (
    "bedf9f2aec45ec67762b202eb2e7c5adcc23f3214d6ef9c6c31639b12f4da65b")
EXPECTED_SUMMARY_SHA256 = (
    "0af4664a59b0753221f2e616f2f4300708ff41e8b9e3da7e276668363c05d4b1")

EXPECTED_SETUP_IDS = (
    "ETHUSD_2026-05-13T08:00:00Z",
    "ETHUSD_2026-05-24T01:00:00Z",
    "ETHUSD_2026-05-25T14:00:00Z",
    "SOLUSD_2026-05-06T01:00:00Z",
    "SOLUSD_2026-05-06T06:00:00Z",
    "SOLUSD_2026-05-09T01:00:00Z",
)
EXPECTED_REMOVED_SETUP_ID = "SOLUSD_2026-05-06T06:00:00Z"

EXPECTED_VARIANTS = {
    "2r": {"frozen_labels": 6, "replayed": 6, "kept": 5, "removed": 1,
           "hits": 2, "stops": 3, "timeouts": 0,
           "hit_rate_pct": 40.0, "gross_breakeven_rate_pct": 33.3,
           "gross_r": 1.000001, "fee_r": 1.269642,
           "net_r": -0.269641},
    "3r": {"frozen_labels": 6, "replayed": 6, "kept": 5, "removed": 1,
           "hits": 1, "stops": 4, "timeouts": 0,
           "hit_rate_pct": 20.0, "gross_breakeven_rate_pct": 25.0,
           "gross_r": -0.999999, "fee_r": 1.269642,
           "net_r": -2.269641},
    "4r": {"frozen_labels": 6, "replayed": 6, "kept": 5, "removed": 1,
           "hits": 1, "stops": 4, "timeouts": 0,
           "hit_rate_pct": 20.0, "gross_breakeven_rate_pct": 20.0,
           "gross_r": 0.000001, "fee_r": 1.269642,
           "net_r": -1.269641},
}

EXPECTED_PER_SYMBOL = {
    "ETHUSD": {"trades": 3,
               "net_r": {"2r": -3.861515, "3r": -3.861515,
                         "4r": -3.861515},
               "hits": {"2r": 0, "3r": 0, "4r": 0}},
    "SOLUSD": {"trades": 2,
               "net_r": {"2r": 3.591874, "3r": 1.591874,
                         "4r": 2.591874},
               "hits": {"2r": 2, "3r": 1, "4r": 1}},
}

EXPECTED_BEST_WORST = {
    "2r": {"best": {"setup_id": "SOLUSD_2026-05-09T01:00:00Z",
                    "net_r": 1.858159},
           "worst": {"setup_id": "ETHUSD_2026-05-25T14:00:00Z",
                     "net_r": -1.357148}},
    "3r": {"best": {"setup_id": "SOLUSD_2026-05-06T01:00:00Z",
                    "net_r": 2.733715},
           "worst": {"setup_id": "ETHUSD_2026-05-25T14:00:00Z",
                     "net_r": -1.357148}},
    "4r": {"best": {"setup_id": "SOLUSD_2026-05-06T01:00:00Z",
                    "net_r": 3.733715},
           "worst": {"setup_id": "ETHUSD_2026-05-25T14:00:00Z",
                     "net_r": -1.357148}},
}

FROZEN_REPLAY_FACTS = (
    "informational replay only; exactly 6 frozen setup_ids replayed; "
    "zero skipped",
    "fee model 27 bps round-trip; entry at the frozen trigger candle "
    "close; replay starts the next 1h bar after trigger close",
    "conservative stop-before-target same-bar ordering; adverse gaps "
    "at open count against the trade; favorable gaps capped at target; "
    "timeout at last close; variants 2r/3r/4r only",
    "same-symbol non-overlap applied per variant at replay-policy "
    "time; SOLUSD_2026-05-06T06:00 removed in all variants because it "
    "overlapped the prior kept same-symbol sol hold",
    "non-overlap removed a winner; this is an honest cost of the dedup "
    "rule",
    "kept set size 5 and removed set size 1 for every variant",
    "worst trade reason: thinnest 75.6 bps risk, fees bit hardest",
)

FROZEN_CLASSIFICATION_FACTS = (
    "all variants net-negative",
    "2r is gross-positive but net-negative",
    "4r is gross-flat but net-negative",
    "fees made 2r negative, but the sample is only 5 kept trades after "
    "non-overlap",
    "margin is noise-level: -0.27r at 2r",
    "this cannot promote, cannot approve paper or live, and cannot "
    "support a profitability claim",
    "the family's single pre-committed edit remains unspent",
    "replay/edit/reject remains the human decision",
    "structural scarcity: 372/411 attempts died at pullback_too_long; "
    "the sample is starved at the trigger window, not at the floor or "
    "the rs gate",
    "all replay signal is concentrated in 2 sol trades from one week; "
    "eth contributed only stops",
)

SEED_OBSERVATIONS_NOT_CLAIMS = (
    "sol_side_rs_strength_recurs_across_c4_and_c5",
    "thin_risk_fee_sensitivity_matters",
    "dedup_can_remove_winners",
    "eth_side_contribution_was_negative_in_this_sample",
)


def get_c5_replay_review_label() -> str:
    return C5RR_LABEL


def observe_c5_replay_results(repo_root: Any,
                              tracked_paths: Any = ()) -> dict[str, Any]:
    """Read the replay artifacts READ-ONLY and recompute every aggregate
    from the raw rows, re-applying the pushed non-overlap filter. Never
    raises on missing files."""
    observation: dict[str, Any] = {
        "results_exists": False, "summary_exists": False,
        "results_sha256": None, "summary_sha256": None,
        "row_count": None, "setup_ids": None, "skipped_count": None,
        "variants": None, "per_symbol": None, "best_worst": None,
        "removed_ids_by_variant": None,
        "all_variants_net_negative": None,
        "gross_positive_2r": None, "gross_flat_4r": None,
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
        observation["skipped_count"] = len(
            _json.loads(raw_summary.decode("utf-8")).get(
                "skipped_setup_ids", [None]))
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
    per_symbol: dict[str, Any] = {}
    best_worst: dict[str, Any] = {}
    removed_ids: dict[str, Any] = {}
    net_negative = []
    for name in ("2r", "3r", "4r"):
        overlap = apply_same_symbol_non_overlap(rows, name)
        kept, removed = overlap["kept"], overlap["removed"]
        removed_ids[name] = sorted(r["setup_id"] for r in removed)
        outcomes = [(row, row["variants"][name]) for row in kept]
        hits = sum(1 for _r, v in outcomes if v["outcome"] == "target")
        stops = sum(1 for _r, v in outcomes if v["outcome"] == "stop")
        timeouts = sum(1 for _r, v in outcomes
                       if v["outcome"] == "timeout")
        gross = round(sum(v["gross_r"] for _r, v in outcomes), 6)
        fees = round(sum(row["cost_r"] for row, _v in outcomes), 6)
        net = round(sum(v["net_r"] for _r, v in outcomes), 6)
        variants[name] = {
            "frozen_labels": 6, "replayed": len(rows),
            "kept": len(kept), "removed": len(removed),
            "hits": hits, "stops": stops, "timeouts": timeouts,
            "hit_rate_pct": (round(hits / len(kept) * 100.0, 1)
                             if kept else None),
            "gross_breakeven_rate_pct": EXPECTED_VARIANTS[name][
                "gross_breakeven_rate_pct"],
            "gross_r": gross, "fee_r": fees, "net_r": net}
        net_negative.append(net < 0)
        if outcomes:
            best = max(outcomes, key=lambda rv: rv[1]["net_r"])
            worst = min(outcomes, key=lambda rv: rv[1]["net_r"])
            best_worst[name] = {
                "best": {"setup_id": best[0]["setup_id"],
                         "net_r": best[1]["net_r"]},
                "worst": {"setup_id": worst[0]["setup_id"],
                          "net_r": worst[1]["net_r"]}}
        if name == "2r":
            for sym in ("ETHUSD", "SOLUSD"):
                per_symbol[sym] = {
                    "trades": sum(1 for row in kept
                                  if row["symbol"] == sym),
                    "net_r": {}, "hits": {}}
        for sym in ("ETHUSD", "SOLUSD"):
            sym_rows = [v for row, v in outcomes
                        if row["symbol"] == sym]
            per_symbol[sym]["net_r"][name] = round(
                sum(v["net_r"] for v in sym_rows), 6)
            per_symbol[sym]["hits"][name] = sum(
                1 for v in sym_rows if v["outcome"] == "target")
    observation["variants"] = variants
    observation["per_symbol"] = per_symbol
    observation["best_worst"] = best_worst
    observation["removed_ids_by_variant"] = removed_ids
    observation["all_variants_net_negative"] = all(net_negative)
    observation["gross_positive_2r"] = variants["2r"]["gross_r"] > 0
    observation["gross_flat_4r"] = abs(variants["4r"]["gross_r"]) < 0.01
    return observation


def certify_c5_replay_results(observation: Any) -> dict[str, Any]:
    """Pure certification of an observation against the frozen facts."""
    failures: list[str] = []
    if not isinstance(observation, dict):
        return {"certified": False,
                "failures": ["observation_not_a_dict"]}
    o = observation
    if not o.get("results_exists"):
        failures.append("results_artifact_missing")
    if not o.get("summary_exists"):
        failures.append("summary_artifact_missing")
    if failures:
        return {"certified": False, "failures": failures}
    if o.get("results_sha256") != EXPECTED_RESULTS_SHA256:
        failures.append("results_sha_mismatch")
    if o.get("summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_mismatch")
    if o.get("row_count") != 6:
        failures.append("row_count_not_6")
    if o.get("setup_ids") != tuple(sorted(EXPECTED_SETUP_IDS)):
        failures.append("setup_ids_mismatch")
    if o.get("skipped_count") != 0:
        failures.append("skipped_count_not_zero")
    variants = o.get("variants") or {}
    for name, expected in EXPECTED_VARIANTS.items():
        got = variants.get(name) or {}
        for key, value in expected.items():
            if got.get(key) != value:
                failures.append(
                    "variant_fact_mismatch:%s:%s" % (name, key))
        if (got.get("hits") or 0) + (got.get("stops") or 0) \
                + (got.get("timeouts") or 0) != (got.get("kept") or -1):
            failures.append("variant_counts_inconsistent:" + name)
    removed_ids = o.get("removed_ids_by_variant") or {}
    for name in ("2r", "3r", "4r"):
        if removed_ids.get(name) != [EXPECTED_REMOVED_SETUP_ID]:
            failures.append("non_overlap_removal_mismatch:" + name)
    if o.get("per_symbol") != EXPECTED_PER_SYMBOL:
        failures.append("per_symbol_mismatch")
    if o.get("best_worst") != EXPECTED_BEST_WORST:
        failures.append("best_worst_mismatch")
    if o.get("all_variants_net_negative") is not True:
        failures.append("net_negative_fact_broken")
    if o.get("gross_positive_2r") is not True:
        failures.append("gross_positive_2r_fact_broken")
    if o.get("gross_flat_4r") is not True:
        failures.append("gross_flat_4r_fact_broken")
    if o.get("artifacts_tracked_in_git"):
        failures.append("runner_and_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c5_replay_results_review(repo_root: Any,
                                   tracked_paths: Any = ()
                                   ) -> dict[str, Any]:
    """Observe read-only and certify; gated on the four-record ledger,
    the labels freeze, and the loop all certifying live."""
    record: dict[str, Any] = {
        "schema_version": C5RR_SCHEMA_VERSION, "label": C5RR_LABEL,
        "mode": C5RR_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "classification": CLASSIFICATION,
        "head_at_replay": HEAD_AT_REPLAY,
        "runner_path_untracked_only": RUNNER_PATH,
        "results_path": RESULTS_PATH, "summary_path": SUMMARY_PATH,
        "expected_results_sha256": EXPECTED_RESULTS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "labels_artifact_sha256": LABELS_ARTIFACT_SHA256,
        "labels_summary_sha256": LABELS_SUMMARY_SHA256,
        "expected_setup_ids": list(EXPECTED_SETUP_IDS),
        "expected_removed_setup_id": EXPECTED_REMOVED_SETUP_ID,
        "expected_variants": {key: dict(value) for key, value
                              in EXPECTED_VARIANTS.items()},
        "expected_per_symbol": {
            sym: {"trades": split["trades"],
                  "net_r": dict(split["net_r"]),
                  "hits": dict(split["hits"])}
            for sym, split in EXPECTED_PER_SYMBOL.items()},
        "expected_best_worst": {
            name: {"best": dict(pair["best"]),
                   "worst": dict(pair["worst"])}
            for name, pair in EXPECTED_BEST_WORST.items()},
        "frozen_replay_facts": list(FROZEN_REPLAY_FACTS),
        "frozen_classification_facts": list(
            FROZEN_CLASSIFICATION_FACTS),
        "seed_observations_not_claims": list(
            SEED_OBSERVATIONS_NOT_CLAIMS),
        "information_only_no_promotion_possible": True,
        "edit_allowance_unspent": True,
        "edit_or_reject_is_human_decision": True,
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
        record["verdict"] = VERDICT_C5RR_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    labels_review = build_c5_labels_review(repo_root, tracked_paths)
    if labels_review["verdict"] != VERDICT_C5L_FROZEN:
        record["verdict"] = VERDICT_C5RR_BLOCKED
        record["blockers"].append("labels_freeze_not_certifying")
        record["blockers"].extend(labels_review["failures"])
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C5RR_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observation = observe_c5_replay_results(repo_root, tracked_paths)
    result = certify_c5_replay_results(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C5RR_FROZEN if result["certified"]
                         else VERDICT_C5RR_REJECTED)
    return record


def validate_c5_replay_results_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C5RR_FROZEN,
                                VERDICT_C5RR_REJECTED,
                                VERDICT_C5RR_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("classification") != CLASSIFICATION:
        errors.append("classification_tampered")
    if r.get("head_at_replay") != HEAD_AT_REPLAY:
        errors.append("head_tampered")
    if r.get("expected_results_sha256") != EXPECTED_RESULTS_SHA256:
        errors.append("results_sha_tampered")
    if r.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        errors.append("summary_sha_tampered")
    if r.get("labels_artifact_sha256") != LABELS_ARTIFACT_SHA256:
        errors.append("labels_sha_tampered")
    if r.get("labels_summary_sha256") != LABELS_SUMMARY_SHA256:
        errors.append("labels_summary_sha_tampered")
    if tuple(r.get("expected_setup_ids") or ()) != EXPECTED_SETUP_IDS:
        errors.append("setup_ids_tampered")
    if r.get("expected_removed_setup_id") != EXPECTED_REMOVED_SETUP_ID:
        errors.append("removed_setup_tampered")
    expected_variants = {key: dict(value) for key, value
                         in EXPECTED_VARIANTS.items()}
    if r.get("expected_variants") != expected_variants:
        errors.append("variant_table_tampered")
    expected_split = {
        sym: {"trades": split["trades"], "net_r": dict(split["net_r"]),
              "hits": dict(split["hits"])}
        for sym, split in EXPECTED_PER_SYMBOL.items()}
    if r.get("expected_per_symbol") != expected_split:
        errors.append("per_symbol_tampered")
    expected_bw = {name: {"best": dict(pair["best"]),
                          "worst": dict(pair["worst"])}
                   for name, pair in EXPECTED_BEST_WORST.items()}
    if r.get("expected_best_worst") != expected_bw:
        errors.append("best_worst_tampered")
    if tuple(r.get("frozen_replay_facts") or ()) != FROZEN_REPLAY_FACTS:
        errors.append("replay_facts_tampered")
    if tuple(r.get("frozen_classification_facts") or ()) != (
            FROZEN_CLASSIFICATION_FACTS):
        errors.append("classification_facts_tampered")
    if tuple(r.get("seed_observations_not_claims") or ()) != (
            SEED_OBSERVATIONS_NOT_CLAIMS):
        errors.append("seed_observations_tampered")
    for key in ("information_only_no_promotion_possible",
                "edit_allowance_unspent",
                "edit_or_reject_is_human_decision",
                "human_review_required", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked"):
        if r.get(key) is not True:
            errors.append("constitution_flag_wrong:" + key)
    if r.get("verdict") == VERDICT_C5RR_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
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

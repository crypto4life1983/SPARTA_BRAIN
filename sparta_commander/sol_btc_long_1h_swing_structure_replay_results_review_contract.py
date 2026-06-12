"""SPARTA CANDIDATE #4 FEE-HONEST REPLAY RESULTS REVIEW / EVIDENCE
FREEZE (READ-ONLY, RESEARCH ONLY): SOL_BTC_LONG_1H_SWING_STRUCTURE_V1.

Freezes the completed fee-honest replay of the 22 frozen accepted labels.
THE ARITHMETIC, honestly: every variant lost GROSS and NET --

  2R: 5 hits / 17 stops / 0 timeouts  (22.7% vs 33.3% gross breakeven)
      gross -7.0 R, fees -4.666507 R, NET -11.666507 R
  3R: 2 / 20 / 0  (9.1% vs 25.0%)   gross -14.0, NET -18.666507 R
  4R: 2 / 20 / 0  (9.1% vs 20.0%)   gross -12.0, NET -16.666507 R

This is EDGE FAILURE, NOT COST FAILURE: gross-negative at every target,
so a zero-fee replay would still lose. Same failure-mode class as
Candidate #2. Material concentration warning: 14 of 22 trades overlap a
prior same-symbol hold in every variant -- higher-low swing chains fire
in clusters, losses are correlated, and the effective independent sample
is materially smaller than 22.

REJECTION PRESSURE is recorded. The family's single pre-committed
filter-only edit allowance remains unspent; whether to spend it or issue
the formal rejection is the HUMAN decision at the next gate. No paper,
no live, no profitability claim -- there is nothing to claim.

This module observes the untracked replay artifacts READ-ONLY, recomputes
every aggregate from the raw per-trade rows, and certifies the frozen
facts. It reruns nothing, fetches nothing, and authorizes nothing.
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
from sparta_commander.sol_btc_long_1h_swing_structure_real_candle_labels_review_contract import (
    EXPECTED_LABELS_SHA256,
    LABELS_PATH,
    VERDICT_C4L_FROZEN,
    build_c4_labels_review,
)
from sparta_commander.sol_btc_long_1h_swing_structure_strategy_spec_contract import (
    CANDIDATE_ID,
)

C4RR_SCHEMA_VERSION = (
    "sol_btc_long_1h_swing_structure_replay_results_review.v1")
C4RR_LABEL = ("SPARTA Candidate #4 Replay Results Review / Evidence "
              "Freeze (READ-ONLY, RESEARCH ONLY, ALL VARIANTS NET "
              "NEGATIVE, NOT A PROFITABILITY CLAIM)")
C4RR_MODE = "RESEARCH_ONLY"
VERDICT_C4RR_FROZEN = (
    "C4_REPLAY_RESULTS_REVIEW_CONTRACT_FROZEN_REJECTION_PRESSURE")
VERDICT_C4RR_REJECTED = "C4_REPLAY_RESULTS_REVIEW_REJECTED"
VERDICT_C4RR_BLOCKED = "C4_REPLAY_RESULTS_REVIEW_BLOCKED"
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C4_FILTER_ONLY_EDIT_OR_REJECT"

RESULTS_PATH = ("data/swing_structure_c4/replay_results/"
                "c4_replay_results_2026-05-02_2026-06-10.jsonl")
SUMMARY_PATH = ("data/swing_structure_c4/replay_results/"
                "c4_replay_summary_2026-05-02_2026-06-10.json")
RUNNER_PATH = "tools/c4_fee_honest_replay_22_once.py"

EXPECTED_RESULTS_SHA256 = (
    "74450b16a0c397adff75b74ef9ef66748e7b07cf089ace46edcec675bd031eb6")
EXPECTED_SUMMARY_SHA256 = (
    "b156ac9e440aa2f8c010aaca0b7fc9d0944ae336e10e77b40ef60f2f14a60e32")

UPSTREAM_FROZEN_FACTS = {
    "labels_review_commit": "8cf8136aef277b92cc780960aa6c20be3a581376",
    "labels_review_verdict":
        "CANDIDATE_4_REAL_CANDLE_LABELS_FROZEN_ACCEPTED_FOR_REPLAY_REVIEW",
    "accepted_count": 22,
    "label_recount": 275,
    "replay_has_run_was_false_before_replay_gate": True,
    "zero_skips_in_replay": True,
}

FROZEN_REPLAY_RULES = (
    "fee model: 27 bps round-trip charged as cost_R = 27 / risk_bps",
    "entry at the trigger candle close",
    "replay starts on the next 1h bar after the trigger close",
    "conservative stop-before-target ordering inside the same bar",
    "adverse gaps at the open count fully against the trade",
    "favorable gaps are capped at the target price",
    "timeout exits at the last available close",
    "1h bars re-aggregated from sha-verified staged 15m by the pushed "
    "aggregator",
    "all exactly 22 accepted setup_ids replayed; zero skipped",
)

EXPECTED_VARIANTS = {
    "2r": {"hits": 5, "stops": 17, "timeouts": 0,
           "hit_rate_pct": 22.7, "gross_breakeven_rate_pct": 33.3,
           "gross_r": -7.0, "fee_r": 4.666507, "net_r": -11.666507},
    "3r": {"hits": 2, "stops": 20, "timeouts": 0,
           "hit_rate_pct": 9.1, "gross_breakeven_rate_pct": 25.0,
           "gross_r": -14.0, "fee_r": 4.666507, "net_r": -18.666507},
    "4r": {"hits": 2, "stops": 20, "timeouts": 0,
           "hit_rate_pct": 9.1, "gross_breakeven_rate_pct": 20.0,
           "gross_r": -12.0, "fee_r": 4.666507, "net_r": -16.666507},
}

EXPECTED_SYMBOL_SPLIT = {
    "SOLUSD": {"trades": 12,
               "net_r": {"2r": -2.396186, "3r": -6.396186,
                         "4r": -4.396186},
               "hits": {"2r": 4, "3r": 2, "4r": 2}},
    "BTCUSD": {"trades": 10,
               "net_r": {"2r": -9.270321, "3r": -12.270321,
                         "4r": -12.270321},
               "hits": {"2r": 1, "3r": 0, "4r": 0}},
}

EXPECTED_BEST_WORST = {
    "2r": {"best": {"setup_id": "SOLUSD_2026-05-08T23:00:00Z",
                    "net_r": 1.858159},
           "worst": {"setup_id": "SOLUSD_2026-05-30T08:00:00Z",
                     "net_r": -1.319719}},
    "3r": {"best": {"setup_id": "SOLUSD_2026-05-05T16:00:00Z",
                    "net_r": 2.843273},
           "worst": {"setup_id": "BTCUSD_2026-05-09T07:00:00Z",
                     "net_r": -1.321963}},
    "4r": {"best": {"setup_id": "SOLUSD_2026-05-05T16:00:00Z",
                    "net_r": 3.843273},
           "worst": {"setup_id": "BTCUSD_2026-05-09T07:00:00Z",
                     "net_r": -1.321963}},
}

EXPECTED_OVERLAPS_PER_VARIANT = 14

FROZEN_WARNINGS = (
    "material concentration/correlation warning: 14 of 22 trades "
    "overlap a prior same-symbol hold in every variant",
    "the effective independent sample is materially smaller than 22",
    "higher-low swing chains fire in clusters",
    "losses are correlated",
    "gross-negative at every target: this is EDGE FAILURE, not cost "
    "failure",
    "fees deepen the loss, but a zero-fee replay would still be "
    "negative",
    "same failure-mode class as candidate #2",
    "no paper or live approval exists or is implied",
    "no profitability claim is permitted",
)


def get_c4_replay_review_label() -> str:
    return C4RR_LABEL


def observe_c4_replay_results(repo_root: Any,
                              tracked_paths: Any = ()) -> dict[str, Any]:
    """Read the replay artifacts READ-ONLY and recompute every aggregate
    from the raw rows. Never raises on missing files."""
    observation: dict[str, Any] = {
        "results_exists": False, "summary_exists": False,
        "results_sha256": None, "summary_sha256": None,
        "row_count": None, "setup_ids_unique": None,
        "setup_ids_match_frozen_accepted_set": None,
        "variants": None, "symbol_split": None, "best_worst": None,
        "overlaps_per_variant": None,
        "all_variants_gross_negative": None,
        "all_variants_net_negative": None,
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
        observation["summary_sha256"] = _hashlib.sha256(
            summary_file.read_bytes()).hexdigest()
    if not results_file.is_file():
        return observation
    observation["results_exists"] = True
    raw = results_file.read_bytes()
    observation["results_sha256"] = _hashlib.sha256(raw).hexdigest()
    rows = [_json.loads(line) for line in raw.decode("utf-8").splitlines()]
    observation["row_count"] = len(rows)
    setup_ids = [row["setup_id"] for row in rows]
    observation["setup_ids_unique"] = len(set(setup_ids)) == len(setup_ids)
    labels_file = root / LABELS_PATH
    if labels_file.is_file():
        labels_raw = labels_file.read_bytes()
        if _hashlib.sha256(labels_raw).hexdigest() == (
                EXPECTED_LABELS_SHA256):
            accepted_ids = {
                label["setup_id"] for label in
                (_json.loads(line) for line in
                 labels_raw.decode("utf-8").splitlines())
                if label["status"] == "accepted_for_replay_review"}
            observation["setup_ids_match_frozen_accepted_set"] = (
                set(setup_ids) == accepted_ids)
    variants: dict[str, Any] = {}
    best_worst: dict[str, Any] = {}
    overlaps: dict[str, int] = {}
    gross_negative = []
    net_negative = []
    for name in ("2r", "3r", "4r"):
        outcomes = [(row, row["variants"][name]) for row in rows]
        hits = sum(1 for _r, v in outcomes if v["outcome"] == "target")
        stops = sum(1 for _r, v in outcomes if v["outcome"] == "stop")
        timeouts = sum(1 for _r, v in outcomes
                       if v["outcome"] == "timeout")
        gross = round(sum(v["gross_r"] for _r, v in outcomes), 6)
        fees = round(sum(row["cost_r"] for row, _v in outcomes), 6)
        net = round(sum(v["net_r"] for _r, v in outcomes), 6)
        variants[name] = {
            "hits": hits, "stops": stops, "timeouts": timeouts,
            "hit_rate_pct": round(hits / len(rows) * 100.0, 1),
            "gross_r": gross, "fee_r": fees, "net_r": net}
        gross_negative.append(gross < 0)
        net_negative.append(net < 0)
        best = max(outcomes, key=lambda rv: rv[1]["net_r"])
        worst = min(outcomes, key=lambda rv: rv[1]["net_r"])
        best_worst[name] = {
            "best": {"setup_id": best[0]["setup_id"],
                     "net_r": best[1]["net_r"]},
            "worst": {"setup_id": worst[0]["setup_id"],
                      "net_r": worst[1]["net_r"]}}
        count = 0
        for sym in ("SOLUSD", "BTCUSD"):
            sym_rows = sorted(
                (row for row in rows if row["symbol"] == sym),
                key=lambda row: row["trigger_bar_time_utc"])
            for prev, cur in zip(sym_rows, sym_rows[1:]):
                if cur["trigger_bar_time_utc"] < (
                        prev["variants"][name]["exit_time_utc"]):
                    count += 1
        overlaps[name] = count
    symbol_split: dict[str, Any] = {}
    for sym in ("SOLUSD", "BTCUSD"):
        sym_rows = [row for row in rows if row["symbol"] == sym]
        symbol_split[sym] = {
            "trades": len(sym_rows),
            "net_r": {name: round(sum(
                row["variants"][name]["net_r"] for row in sym_rows), 6)
                for name in ("2r", "3r", "4r")},
            "hits": {name: sum(
                1 for row in sym_rows
                if row["variants"][name]["outcome"] == "target")
                for name in ("2r", "3r", "4r")}}
    observation["variants"] = variants
    observation["symbol_split"] = symbol_split
    observation["best_worst"] = best_worst
    observation["overlaps_per_variant"] = overlaps
    observation["all_variants_gross_negative"] = all(gross_negative)
    observation["all_variants_net_negative"] = all(net_negative)
    return observation


def certify_c4_replay_results(observation: Any) -> dict[str, Any]:
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
    if o.get("row_count") != 22:
        failures.append("row_count_not_22")
    if o.get("setup_ids_unique") is not True:
        failures.append("setup_ids_not_unique")
    if o.get("setup_ids_match_frozen_accepted_set") is not True:
        failures.append("setup_ids_do_not_match_frozen_accepted_set")
    variants = o.get("variants") or {}
    for name, expected in EXPECTED_VARIANTS.items():
        got = variants.get(name) or {}
        for key in ("hits", "stops", "timeouts", "hit_rate_pct",
                    "gross_r", "fee_r", "net_r"):
            if got.get(key) != expected[key]:
                failures.append("variant_fact_mismatch:%s:%s" % (name, key))
        if got.get("hits", 0) + got.get("stops", 0) \
                + got.get("timeouts", 0) != 22:
            failures.append("variant_counts_do_not_sum_to_22:" + name)
    if o.get("symbol_split") != EXPECTED_SYMBOL_SPLIT:
        failures.append("symbol_split_mismatch")
    if o.get("best_worst") != EXPECTED_BEST_WORST:
        failures.append("best_worst_mismatch")
    overlaps = o.get("overlaps_per_variant") or {}
    for name in ("2r", "3r", "4r"):
        if overlaps.get(name) != EXPECTED_OVERLAPS_PER_VARIANT:
            failures.append("overlap_count_mismatch:" + name)
    if o.get("all_variants_gross_negative") is not True:
        failures.append("gross_negative_fact_broken")
    if o.get("all_variants_net_negative") is not True:
        failures.append("net_negative_fact_broken")
    if o.get("artifacts_tracked_in_git"):
        failures.append("runner_and_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c4_replay_results_review(repo_root: Any,
                                   tracked_paths: Any = ()
                                   ) -> dict[str, Any]:
    """Observe read-only and certify; gated on the three-record ledger
    AND the upstream labels freeze still certifying."""
    record: dict[str, Any] = {
        "schema_version": C4RR_SCHEMA_VERSION, "label": C4RR_LABEL,
        "mode": C4RR_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "results_path": RESULTS_PATH, "summary_path": SUMMARY_PATH,
        "runner_path_untracked_only": RUNNER_PATH,
        "expected_results_sha256": EXPECTED_RESULTS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "upstream_frozen_facts": dict(UPSTREAM_FROZEN_FACTS),
        "frozen_replay_rules": list(FROZEN_REPLAY_RULES),
        "expected_variants": {key: dict(value) for key, value
                              in EXPECTED_VARIANTS.items()},
        "expected_symbol_split": {
            sym: {"trades": split["trades"],
                  "net_r": dict(split["net_r"]),
                  "hits": dict(split["hits"])}
            for sym, split in EXPECTED_SYMBOL_SPLIT.items()},
        "expected_best_worst": {
            name: {"best": dict(pair["best"]),
                   "worst": dict(pair["worst"])}
            for name, pair in EXPECTED_BEST_WORST.items()},
        "expected_overlaps_per_variant": EXPECTED_OVERLAPS_PER_VARIANT,
        "frozen_warnings": list(FROZEN_WARNINGS),
        "failure_classification": "EDGE_FAILURE_NOT_COST_FAILURE",
        "single_filter_only_edit_allowance_unspent": True,
        "edit_or_reject_is_human_decision": True,
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
        record["verdict"] = VERDICT_C4RR_BLOCKED
        record["blockers"].append("ledger_broken")
        return record
    labels_review = build_c4_labels_review(repo_root, tracked_paths)
    if labels_review["verdict"] != VERDICT_C4L_FROZEN:
        record["verdict"] = VERDICT_C4RR_BLOCKED
        record["blockers"].append("upstream_labels_freeze_not_certified")
        record["blockers"].extend(labels_review["failures"])
        return record
    observation = observe_c4_replay_results(repo_root, tracked_paths)
    result = certify_c4_replay_results(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C4RR_FROZEN if result["certified"]
                         else VERDICT_C4RR_REJECTED)
    return record


def validate_c4_replay_results_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C4RR_FROZEN,
                                VERDICT_C4RR_REJECTED,
                                VERDICT_C4RR_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("expected_results_sha256") != EXPECTED_RESULTS_SHA256:
        errors.append("results_sha_tampered")
    if r.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        errors.append("summary_sha_tampered")
    if r.get("upstream_frozen_facts") != UPSTREAM_FROZEN_FACTS:
        errors.append("upstream_facts_tampered")
    if tuple(r.get("frozen_replay_rules") or ()) != FROZEN_REPLAY_RULES:
        errors.append("replay_rules_tampered")
    expected_variants = {key: dict(value) for key, value
                         in EXPECTED_VARIANTS.items()}
    if r.get("expected_variants") != expected_variants:
        errors.append("variant_table_tampered")
    expected_split = {
        sym: {"trades": split["trades"], "net_r": dict(split["net_r"]),
              "hits": dict(split["hits"])}
        for sym, split in EXPECTED_SYMBOL_SPLIT.items()}
    if r.get("expected_symbol_split") != expected_split:
        errors.append("symbol_split_tampered")
    expected_bw = {name: {"best": dict(pair["best"]),
                          "worst": dict(pair["worst"])}
                   for name, pair in EXPECTED_BEST_WORST.items()}
    if r.get("expected_best_worst") != expected_bw:
        errors.append("best_worst_tampered")
    if r.get("expected_overlaps_per_variant") != (
            EXPECTED_OVERLAPS_PER_VARIANT):
        errors.append("overlap_warning_tampered")
    if tuple(r.get("frozen_warnings") or ()) != FROZEN_WARNINGS:
        errors.append("warnings_tampered")
    if r.get("failure_classification") != (
            "EDGE_FAILURE_NOT_COST_FAILURE"):
        errors.append("failure_classification_tampered")
    for key in ("single_filter_only_edit_allowance_unspent",
                "edit_or_reject_is_human_decision",
                "human_review_required", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked"):
        if r.get(key) is not True:
            errors.append("constitution_flag_wrong:" + key)
    if r.get("verdict") == VERDICT_C4RR_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
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

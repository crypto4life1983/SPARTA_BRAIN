"""Candidate #10 (INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1) cross-asset /
cross-weekday / forward-OOS generalization review / evidence-freeze contract.

RESEARCH ONLY. Reviews the FROZEN, SHA-pinned generalization artifact produced
by tools/c10_cross_asset_cross_weekday_forward_oos_eval_once.py against the
pushed, chain-gated C10 robustness review. Pure, in-memory evidence record: NO
file I/O, NO network, NO trading, NO PnL, NO relabel of the original C10 result,
NO weekday re-selection, NO parameter fitting, NO best-cell selection, NO
downstream gate unlock. It does NOT claim profitability and does NOT approve
paper or live.

Chain gate: build_c10_generalization_review() requires build_c10_robustness_review()
to return the FROZEN robustness verdict.

Honest finding encoded here:
  * SELF-VALIDATION passed: the generalized scan reproduces the frozen 156
    BTCUSD-Friday accepted setups over OOS -> geometry identical to the
    committed detector before any claim.
  * CROSS-ASSET (inherited Friday, OOS 2023-2025): ETH and SOL are net-positive
    on every variant, but FAR WEAKER than BTC and NEGATIVE in 2025 -- the same
    decaying long-drift, not independent confirmation.
  * CROSS-WEEKDAY (BTC, OOS): Friday ranks #1 BUT 6 of 7 weekdays are
    net-positive (only Wednesday negative). Friday is NOT a unique positive
    weekday -> the 'Friday edge' is largely GENERAL BULLISH LONG-DRIFT, not a
    Friday-SPECIFIC calendar anomaly. The original in-sample weekday selection
    captured the strongest of many positive days.
  * FORWARD-OOS (inherited Friday, 2026-01-01..2026-06-08, truly post-training):
    NEGATIVE on BTC, ETH, and SOL -- the edge did NOT continue forward.
  * Verdict: C10_DOES_NOT_GENERALIZE. The Friday-specific hypothesis fails
    (general drift, not Friday) and the edge does not persist forward.
    Recommended disposition: REJECT or PARK; do NOT promote.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.intraweek_calendar_seasonality_drift_v1_robustness_review_contract import (  # noqa: E501
    VERDICT_C10ROB_FROZEN,
    build_c10_robustness_review,
)

C10GEN_SCHEMA_VERSION = 1
C10GEN_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1"
CANDIDATE_FAMILY = "intraweek_calendar_seasonality_drift"
DIRECTION = "long_only"
TIMEFRAME = "1d"

# Allowed verdicts (only one is asserted by this frozen record).
VERDICT_C10GEN_FROZEN = "C10_GENERALIZATION_FROZEN_FOR_HUMAN_REVIEW"
VERDICT_C10GEN_GENERALIZES = "C10_GENERALIZES_WEAK_OR_STRONG"
VERDICT_C10GEN_DOES_NOT_GENERALIZE = "C10_DOES_NOT_GENERALIZE"
VERDICT_C10GEN_INCONCLUSIVE = "C10_GENERALIZATION_INCONCLUSIVE"
VERDICT_C10GEN_BLOCKED = "C10_GENERALIZATION_BLOCKED"

NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C10_REJECT_OR_PARK"
RECOMMENDED_DISPOSITION = (
    "REJECT_OR_PARK_DO_NOT_PROMOTE__FRIDAY_EDGE_IS_GENERAL_DRIFT_AND_"
    "FORWARD_OOS_NEGATIVE")

HEAD_AT_ROBUSTNESS_REVIEW = "85e2cd6a4b49ec6e07f74ee920caab23516a14ca"

EXPECTED_SOURCE_SHA256 = {
    "BTC": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETH": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOL": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}
EXPECTED_GENERALIZATION_SHA256 = (
    "cf27fca30dd0017b1c0505d9f457437c625b1542a642668c4d61408eff8fb2b5")
GENERALIZATION_PATH = (
    "data/intraweek_calendar_seasonality_c10/cross_asset_weekday_forward_oos/"
    "c10_cross_asset_weekday_forward_oos_2023_2026H1.json")

INHERITED_FRIDAY_BUCKET = 5
ALL_IN_BPS = 37.0
SELF_VALIDATION_BTC_FRIDAY_OOS_ACCEPTED = 156

# Frozen generalization findings (net R totals, 37 bps all-in, out-of-sample).
CROSS_ASSET_FRIDAY_OOS = {
    "BTC_reference": {"2r": 14.98, "3r": 22.48, "4r": 24.52,
                      "all_variants_positive": True, "net_2025_negative": True},
    "ETH": {"2r": 1.93, "3r": 5.41, "4r": 5.36,
            "all_variants_positive": True, "net_2025_negative": True},
    "SOL": {"2r": 7.51, "3r": 7.58, "4r": 8.24,
            "all_variants_positive": True, "net_2025_negative": True},
}
CROSS_WEEKDAY_BTC_OOS_NET_3R = {
    "1_mon": 5.39, "2_tue": 6.63, "3_wed": -0.45, "4_thu": 13.52,
    "5_fri": 22.48, "6_sat": 18.23, "7_sun": 7.17,
}
CROSS_WEEKDAY_SUMMARY = {
    "friday_rank_3r": 1,
    "positive_weekdays_count_3r": 6,
    "friday_is_unique_positive_weekday": False,
    "interpretation": "general_long_drift_not_friday_specific",
}
FORWARD_OOS_FRIDAY_2026 = {
    "BTC": {"2r": -0.13, "3r": -0.47, "4r": -0.47, "trades": 22,
            "all_variants_positive": False},
    "ETH": {"2r": -0.40, "3r": -0.55, "4r": -0.55, "trades": 22,
            "all_variants_positive": False},
    "SOL": {"2r": -4.23, "3r": -4.23, "4r": -4.23, "trades": 22,
            "all_variants_positive": False},
}

HONEST_CAVEATS = (
    "Generalization re-walk over FROZEN data with the INHERITED Friday rule and "
    "frozen geometry; no weekday re-selection, no parameter fitting, no "
    "best-cell selection; not a profitability claim; the original frozen C10 "
    "result was not changed or relabeled.",
    "Self-validation passed: the generalized scan reproduced the frozen 156 "
    "BTCUSD-Friday accepted setups over OOS -- geometry is identical to the "
    "committed detector.",
    "Cross-asset: ETH and SOL Friday are net-positive over 2023-2025 but FAR "
    "weaker than BTC and NEGATIVE in 2025 -- the same decaying long-drift, not "
    "independent confirmation.",
    "Cross-weekday: Friday ranks #1 but 6 of 7 BTC weekdays are net-positive -- "
    "Friday is NOT a unique positive weekday, so the edge is general bullish "
    "long-drift, not a Friday-specific calendar anomaly.",
    "Forward-OOS (2026 H1, truly post-training): NEGATIVE on BTC, ETH, and SOL "
    "-- the edge did not continue forward.",
    "Conclusion: the Friday-specific calendar hypothesis does NOT generalize "
    "and does NOT persist forward; the apparent edge is decaying long-drift.",
)

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_execution_approval", "no_capital_deployment", "no_portfolio_allocation",
    "no_weekday_reselection_applied", "no_parameter_fitting_applied",
    "no_best_cell_selected_as_promotion", "no_relabel_of_original_result",
    "original_frozen_c10_result_unchanged",
    "friday_specificity_failed_disclosed", "forward_oos_negative_disclosed",
    "promotion_to_paper_or_live_barred",
)

C10GEN_LABEL = (
    "C10 GENERALIZATION (READ-ONLY, RESEARCH ONLY). FRIDAY EDGE DOES NOT "
    "GENERALIZE: IT IS GENERAL LONG-DRIFT (6 OF 7 WEEKDAYS POSITIVE), WEAK ON "
    "ETH/SOL, AND NEGATIVE IN FORWARD-OOS 2026 ON ALL THREE ASSETS. NOT A "
    "PROFITABILITY CLAIM. NOT AN APPROVAL FOR PAPER OR LIVE. RECOMMEND "
    "REJECT OR PARK."
)

_CAPABILITY_FLAGS_FALSE = (
    "runs_real_candle_detection", "runs_detection_now", "labels_now",
    "relabels_original_result", "reselects_weekday", "fits_parameters",
    "optimizes", "selects_best_cell_as_promotion", "runs_replay_now",
    "scores_live", "stages_data_now", "fetches_data", "calls_api",
    "uses_network", "uses_credentials", "uses_wallet", "uses_account",
    "connects_broker", "connects_exchange", "uses_real_money",
    "contains_order_logic", "contains_portfolio_allocation_logic",
    "deploys_capital", "starts_scheduler", "sends_notifications",
    "auto_commits", "auto_pushes", "modifies_frozen_labels",
    "modifies_replay_artifacts", "modifies_robustness_artifact",
    "modifies_generalization_artifact", "computes_live_pnl",
    "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "promotes_to_paper_or_live", "promotes_gate",
    "unlocks_downstream_gate", "claims_profitability", "claims_edge",
    "executes", "writes_files",
)


def get_candidate_10_generalization_review_label() -> str:
    return C10GEN_LABEL


def get_candidate_10_generalization_review_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c10_generalization_review(repo_root: Any,
                                    tracked_paths: list) -> dict[str, Any]:
    """Assemble the C10 generalization review record. Chain-gated on the pushed
    FROZEN robustness review. Pure; no I/O."""
    record: dict[str, Any] = {
        "schema_version": C10GEN_SCHEMA_VERSION,
        "label": C10GEN_LABEL, "mode": C10GEN_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "direction": DIRECTION, "timeframe": TIMEFRAME,
        "verdict": None, "blockers": [], "failures": [],
        "head_at_robustness_review": HEAD_AT_ROBUSTNESS_REVIEW,
        "expected_source_sha256": EXPECTED_SOURCE_SHA256,
        "expected_generalization_sha256": EXPECTED_GENERALIZATION_SHA256,
        "generalization_path": GENERALIZATION_PATH,
        "inherited_friday_bucket": INHERITED_FRIDAY_BUCKET,
        "all_in_bps": ALL_IN_BPS,
        "self_validation_btc_friday_oos_accepted":
            SELF_VALIDATION_BTC_FRIDAY_OOS_ACCEPTED,
        "self_validation_passed": True,
        "cross_asset_friday_oos_net_r": CROSS_ASSET_FRIDAY_OOS,
        "cross_weekday_btc_oos_net_3r": CROSS_WEEKDAY_BTC_OOS_NET_3R,
        "cross_weekday_summary": CROSS_WEEKDAY_SUMMARY,
        "forward_oos_friday_2026_net_r": FORWARD_OOS_FRIDAY_2026,
        "honest_caveats": list(HONEST_CAVEATS),
        "claim_locks": list(CLAIM_LOCKS),
        # generalization findings
        "friday_specificity_holds": False,
        "friday_is_general_long_drift": True,
        "cross_asset_independent_confirmation": False,
        "forward_oos_positive_any_asset": False,
        "recommended_disposition": RECOMMENDED_DISPOSITION,
        "promotion_to_paper_or_live_barred": True,
        "original_frozen_c10_result_unchanged": True,
        "is_generalization_review_only": True,
        "current_loop_stage": "cross_asset_weekday_forward_oos_review",
        "human_review_required": True,
        "relabel_gate_locked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_paper_trading": True, "no_micro_live": True,
        "no_live_trading": True, "no_broker": True, "no_exchange": True,
        "no_wallet": True, "no_account": True, "no_credentials": True,
        "no_order_logic": True, "no_portfolio_allocation": True,
        "no_api": True, "no_network": True, "no_fetch": True,
        "no_notification": True, "no_scheduler": True, "no_relabel": True,
        "no_weekday_reselection": True, "no_parameter_fitting": True,
        "no_optimization": True, "no_best_cell_selected_as_promotion": True,
        "no_detector_change": True, "no_profitability_claim": True,
        "no_downstream_gate_unlock": True,
    }

    rob = build_c10_robustness_review(repo_root, tracked_paths)
    record["robustness_review_verdict"] = rob["verdict"]
    if rob["verdict"] != VERDICT_C10ROB_FROZEN:
        record["verdict"] = VERDICT_C10GEN_BLOCKED
        record["blockers"].append("robustness_review_not_frozen")
        return record

    tracked = set(tracked_paths or [])
    if GENERALIZATION_PATH in tracked:
        record["verdict"] = VERDICT_C10GEN_BLOCKED
        record["blockers"].append("generalization_artifact_tracked")
        return record

    record["verdict"] = VERDICT_C10GEN_DOES_NOT_GENERALIZE
    return record


def validate_c10_generalization_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. The DOES_NOT_GENERALIZE finding + honest framing +
    locks + capability locks must be intact."""
    failures: list = []
    if record.get("verdict") not in (
            VERDICT_C10GEN_FROZEN, VERDICT_C10GEN_GENERALIZES,
            VERDICT_C10GEN_DOES_NOT_GENERALIZE, VERDICT_C10GEN_INCONCLUSIVE):
        failures.append("verdict_not_in_allowed_set")
    if record.get("verdict") != VERDICT_C10GEN_DOES_NOT_GENERALIZE:
        failures.append("verdict_not_does_not_generalize")
    if record.get("blockers"):
        failures.append("has_blockers")

    for field, expected in (
            ("expected_generalization_sha256", EXPECTED_GENERALIZATION_SHA256),):
        v = record.get(field)
        if not isinstance(v, str) or len(v) != 64 or v != expected:
            failures.append("bad_sha_%s" % field)
    src = record.get("expected_source_sha256") or {}
    for k, expected in EXPECTED_SOURCE_SHA256.items():
        if src.get(k) != expected:
            failures.append("bad_source_sha_%s" % k)
    if record.get("head_at_robustness_review") != HEAD_AT_ROBUSTNESS_REVIEW:
        failures.append("head_tampered")

    # Self-validation must hold.
    if record.get("self_validation_passed") is not True:
        failures.append("self_validation_flag_tampered")
    if record.get("self_validation_btc_friday_oos_accepted") != 156:
        failures.append("self_validation_count_tampered")

    # Honest finding flags must be intact.
    if record.get("friday_specificity_holds") is not False:
        failures.append("friday_specificity_flag_tampered")
    if record.get("friday_is_general_long_drift") is not True:
        failures.append("general_drift_flag_tampered")
    if record.get("forward_oos_positive_any_asset") is not False:
        failures.append("forward_oos_flag_tampered")
    if record.get("promotion_to_paper_or_live_barred") is not True:
        failures.append("promotion_bar_removed")
    if record.get("original_frozen_c10_result_unchanged") is not True:
        failures.append("original_result_unchanged_flag_tampered")
    if record.get("recommended_disposition") != RECOMMENDED_DISPOSITION:
        failures.append("disposition_tampered")

    # Cross-weekday: Friday must NOT be the unique positive weekday.
    cw = record.get("cross_weekday_summary") or {}
    if cw.get("friday_is_unique_positive_weekday") is not False:
        failures.append("cross_weekday_specificity_tampered")
    if not (isinstance(cw.get("positive_weekdays_count_3r"), int)
            and cw["positive_weekdays_count_3r"] >= 2):
        failures.append("cross_weekday_count_tampered")

    # Forward-OOS: no asset positive.
    fwd = record.get("forward_oos_friday_2026_net_r") or {}
    for asset in ("BTC", "ETH", "SOL"):
        v = fwd.get(asset) or {}
        if v.get("all_variants_positive") is not False:
            failures.append("forward_oos_positive_tampered_%s" % asset)

    locks = record.get("scope_locks") or {}
    for key, val in locks.items():
        if val is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("relabel_gate_locked", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked",
                "human_review_required", "is_generalization_review_only"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    for required in ("no_profitability_claim", "promotion_to_paper_or_live_barred",
                     "no_relabel_of_original_result",
                     "friday_specificity_failed_disclosed",
                     "forward_oos_negative_disclosed"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    return {"valid": not failures, "failures": failures}

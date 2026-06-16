"""Candidate #10 (INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1) robustness /
sensitivity evaluation review / evidence-freeze contract.

RESEARCH ONLY. Reviews the FROZEN, SHA-pinned robustness artifact produced by
tools/c10_robustness_eval_once.py against the pushed, chain-gated C10
replay-results review. Pure, in-memory evidence record: NO file I/O, NO network,
NO trading, NO PnL, NO relabel, NO parameter fitting, NO optimization, NO
downstream gate unlock. It does NOT claim profitability and does NOT approve
paper or live. It freezes the robustness findings + a human-review verdict and
locks every downstream gate.

Chain gate: build_c10_robustness_review() requires build_c10_replay_review() to
return the FROZEN replay verdict; any broken upstream gate short-circuits to a
BLOCKED verdict.

Honest disposition encoded here (NOT a promotion to execution):
  * The edge SURVIVES realistic cost stress (all variants net-positive through
    75 bps all-in; 3R/4R through 100 bps; 2R turns negative only at 100 bps).
  * The edge is HORIZON-ROBUST (net-positive at 3/5/7/10-bar horizons; the
    pre-registered 5-bar 'one trading week' horizon is the strongest -- not
    fitted).
  * BUT the edge is FRONT-LOADED and DECAYING: first-half net R dwarfs the
    second half; net R declines monotonically 2023 -> 2024 -> 2025; 2025 is
    NEGATIVE for every variant. The 2025 decay is driven by ELEVATED STOP-OUTS
    (13 misses vs the ~10/yr average) with collapsed target hits, even though
    the 5-day horizon drift itself stayed mildly POSITIVE -- risk, not a sign
    flip, eroded 2025.
  * 2025 decay classification: WARNING (regime-dependence) -- NOT a hard
    blocker and NOT an automatic rejection, but enough to BAR promotion to
    paper/live. Recommended disposition: KEEP FOR FURTHER RESEARCH ONLY.
"""
from __future__ import annotations

from typing import Any

from sparta_commander.intraweek_calendar_seasonality_drift_v1_replay_results_review_contract import (  # noqa: E501
    VERDICT_C10RR_FROZEN,
    build_c10_replay_review,
)

C10ROB_SCHEMA_VERSION = 1
C10ROB_MODE = "RESEARCH_ONLY"
CANDIDATE_ID = "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1"
CANDIDATE_FAMILY = "intraweek_calendar_seasonality_drift"
SYMBOL = "BTCUSD"
TIMEFRAME = "1d"
DIRECTION = "long_only"
SAMPLE_TAG = "2023-01-01_2025-12-31"

# Allowed verdicts (only one is asserted by this frozen record).
VERDICT_C10ROB_FROZEN = "C10_ROBUSTNESS_FROZEN_FOR_HUMAN_REVIEW"
VERDICT_C10ROB_REJECTED = "C10_REJECTED_AFTER_ROBUSTNESS_REVIEW"
VERDICT_C10ROB_INCONCLUSIVE = "C10_ROBUSTNESS_INCONCLUSIVE"
VERDICT_C10ROB_BLOCKED = "C10_ROBUSTNESS_BLOCKED"

NEXT_REQUIRED_ACTION = "HUMAN_DECISION_C10_KEEP_FOR_FURTHER_RESEARCH_OR_REJECT"
DECAY_2025_CLASSIFICATION = "WARNING_NOT_BLOCKER_NOT_AUTOREJECTION"
RECOMMENDED_DISPOSITION = (
    "KEEP_FOR_FURTHER_RESEARCH_ONLY_DO_NOT_PROMOTE_TO_PAPER_OR_LIVE")

HEAD_AT_REPLAY_REVIEW = "9a03e638610c371efe8bde1255f958277f7b5bbe"

EXPECTED_REPLAY_LEDGER_SHA256 = (
    "4675f0fd28fc94db9504294a94186cff2576422802bc7f8fb38199aa8251c3ba")
EXPECTED_ROBUSTNESS_SHA256 = (
    "f97e3a74b450d92609be30deea9f5a4d96ab38e994f73134bdd538a1bae7a411")
ROBUSTNESS_PATH = ("data/intraweek_calendar_seasonality_c10/robustness_eval/"
                   "c10_robustness_eval_2023-01-01_2025-12-31.json")

CANONICAL_ALL_IN_BPS = 37.0
COST_STRESS_BPS = (37.0, 50.0, 75.0, 100.0)
HORIZON_SENSITIVITY_BARS = (3, 5, 7, 10)

# Frozen robustness findings (from tools/c10_robustness_eval_once.py over the
# SHA-pinned inputs; net R totals, out-of-sample). Rounded for the record.
COST_STRESS_NET_R = {
    "2r": {"37": 14.98, "50": 10.86, "75": 2.95, "100": -4.96},
    "3r": {"37": 22.48, "50": 18.37, "75": 10.46, "100": 2.55},
    "4r": {"37": 24.52, "50": 20.41, "75": 12.50, "100": 4.59},
}
SUB_PERIOD_NET_R = {
    "2r": {"2023": 11.16, "2024": 7.10, "2025": -3.29,
           "first_half": 14.52, "second_half": 0.46},
    "3r": {"2023": 16.79, "2024": 8.98, "2025": -3.29,
           "first_half": 21.57, "second_half": 0.91},
    "4r": {"2023": 16.83, "2024": 10.98, "2025": -3.29,
           "first_half": 22.61, "second_half": 1.91},
}
DRAWDOWN = {
    "2r": {"max_drawdown_r": 6.34, "worst_losing_streak_trades": 6,
           "worst_year": ["2025", -3.29], "worst_quarter": ["2025-Q1", -4.46],
           "worst_month": ["2025-01", -4.39]},
    "3r": {"max_drawdown_r": 7.15, "worst_losing_streak_trades": 6,
           "worst_year": ["2025", -3.29], "worst_quarter": ["2025-Q1", -5.27],
           "worst_month": ["2025-01", -4.39]},
    "4r": {"max_drawdown_r": 7.15, "worst_losing_streak_trades": 6,
           "worst_year": ["2025", -3.29], "worst_quarter": ["2025-Q1", -5.27],
           "worst_month": ["2025-01", -4.39]},
}
HORIZON_SENSITIVITY_NET_R = {
    "2r": {"h3": 8.33, "h5": 14.98, "h7": 9.45, "h10": 10.00},
    "3r": {"h3": 10.77, "h5": 22.48, "h7": 16.10, "h10": 16.50},
    "4r": {"h3": 11.06, "h5": 24.52, "h7": 22.94, "h10": 24.05},
}
REGIME_2025 = {
    "2r": {"trades": 52, "net_r_total": -3.29, "net_r_mean": -0.063,
           "win_rate": 0.46, "miss": 13, "hit": 2, "horizon": 37,
           "horizon_exit_mean_gross_r": 0.27},
    "3r": {"trades": 52, "net_r_total": -3.29, "net_r_mean": -0.063,
           "win_rate": 0.46, "miss": 13, "hit": 0, "horizon": 39,
           "horizon_exit_mean_gross_r": 0.35},
    "4r": {"trades": 52, "net_r_total": -3.29, "net_r_mean": -0.063,
           "win_rate": 0.46, "miss": 13, "hit": 0, "horizon": 39,
           "horizon_exit_mean_gross_r": 0.35},
}
SURVIVAL_FLAGS = {
    "survives_cost_50bps_all_variants": True,
    "survives_cost_75bps_all_variants": True,
    "survives_cost_100bps_all_variants": False,   # 2r turns negative
    "survives_cost_100bps_3r_and_4r": True,
    "all_horizons_3_to_10_net_positive_all_variants": True,
    "canonical_5bar_horizon_is_strongest": True,
    "all_individual_years_positive": False,        # 2025 negative
    "decay_2025_negative_all_variants": True,
    "edge_front_loaded_first_half_dominant": True,
}

HONEST_CAVEATS = (
    "Robustness/sensitivity over FROZEN inputs only; no relabel, no weekday "
    "change, no parameter fitting; not a profitability claim.",
    "The edge SURVIVES realistic cost stress (net-positive through 75 bps "
    "all-in for all variants; 3R/4R through 100 bps; 2R negative only at 100 "
    "bps).",
    "The edge is HORIZON-ROBUST: net-positive at 3/5/7/10-bar horizons; the "
    "pre-registered 5-bar horizon is the strongest but was not fitted.",
    "The edge is FRONT-LOADED and DECAYING: first-half net R dwarfs the second "
    "half and net R falls monotonically 2023 -> 2024 -> 2025; 2025 is NEGATIVE "
    "for every variant.",
    "2025 decay is driven by ELEVATED STOP-OUTS (13 misses vs ~10/yr) with "
    "collapsed target hits, even though the 5-day horizon drift itself stayed "
    "mildly POSITIVE -- risk, not a sign flip, eroded 2025.",
    "Single asset (BTCUSD), single weekday (Friday); no cross-asset or "
    "cross-weekday robustness demonstrated; the per-trade net edge is thin.",
)

CLAIM_LOCKS = (
    "no_profitability_claim", "no_paper_approval", "no_live_approval",
    "no_execution_approval", "no_capital_deployment", "no_portfolio_allocation",
    "no_winner_wording", "no_parameter_fitting_applied",
    "no_weekday_change_applied", "no_best_cell_selected_as_promotion",
    "regime_decay_2025_disclosed_as_warning",
    "promotion_to_paper_or_live_barred",
)

C10ROB_LABEL = (
    "C10 ROBUSTNESS / SENSITIVITY (READ-ONLY, RESEARCH ONLY). "
    "COST-ROBUST (NET POSITIVE THROUGH 75 BPS; 3R/4R THROUGH 100 BPS) AND "
    "HORIZON-ROBUST (3-10 BARS), BUT FRONT-LOADED AND DECAYING WITH A NEGATIVE "
    "2025 (REGIME WARNING). NOT A PROFITABILITY CLAIM. NOT AN APPROVAL FOR "
    "PAPER OR LIVE. KEEP FOR FURTHER RESEARCH ONLY."
)

_CAPABILITY_FLAGS_FALSE = (
    "runs_real_candle_detection", "runs_detection_now", "labels_now",
    "runs_replay_now", "runs_relabel", "relabels_now", "fits_parameters",
    "changes_weekday", "optimizes", "selects_best_cell_as_promotion",
    "scores_live", "stages_data_now", "fetches_data", "calls_api",
    "uses_network", "uses_credentials", "uses_wallet", "uses_account",
    "connects_broker", "connects_exchange", "uses_real_money",
    "contains_order_logic", "contains_portfolio_allocation_logic",
    "deploys_capital", "starts_scheduler", "sends_notifications",
    "auto_commits", "auto_pushes", "modifies_frozen_labels",
    "modifies_replay_artifacts", "modifies_robustness_artifact",
    "computes_live_pnl", "authorizes_paper_execution", "authorizes_micro_live",
    "authorizes_live_trading", "promotes_to_paper_or_live", "promotes_gate",
    "unlocks_downstream_gate", "claims_profitability", "claims_edge",
    "executes", "writes_files",
)


def get_candidate_10_robustness_review_label() -> str:
    return C10ROB_LABEL


def get_candidate_10_robustness_review_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c10_robustness_review(repo_root: Any,
                                tracked_paths: list) -> dict[str, Any]:
    """Assemble the C10 robustness review record. Chain-gated on the pushed
    FROZEN replay-results review. Pure; no I/O."""
    record: dict[str, Any] = {
        "schema_version": C10ROB_SCHEMA_VERSION,
        "label": C10ROB_LABEL, "mode": C10ROB_MODE,
        "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbol": SYMBOL, "timeframe": TIMEFRAME, "direction": DIRECTION,
        "sample_tag": SAMPLE_TAG,
        "verdict": None, "blockers": [], "failures": [],
        "head_at_replay_review": HEAD_AT_REPLAY_REVIEW,
        "expected_replay_ledger_sha256": EXPECTED_REPLAY_LEDGER_SHA256,
        "expected_robustness_sha256": EXPECTED_ROBUSTNESS_SHA256,
        "robustness_path": ROBUSTNESS_PATH,
        "canonical_all_in_bps": CANONICAL_ALL_IN_BPS,
        "cost_stress_bps": list(COST_STRESS_BPS),
        "horizon_sensitivity_bars": list(HORIZON_SENSITIVITY_BARS),
        "cost_stress_net_r": COST_STRESS_NET_R,
        "sub_period_net_r": SUB_PERIOD_NET_R,
        "drawdown": DRAWDOWN,
        "horizon_sensitivity_net_r": HORIZON_SENSITIVITY_NET_R,
        "regime_decay_2025": REGIME_2025,
        "survival_flags": SURVIVAL_FLAGS,
        "honest_caveats": list(HONEST_CAVEATS),
        "claim_locks": list(CLAIM_LOCKS),
        "survives_realistic_cost_stress": True,
        "decay_2025_classification": DECAY_2025_CLASSIFICATION,
        "decay_2025_is_blocker": False,
        "decay_2025_is_auto_rejection": False,
        "decay_2025_is_warning": True,
        "recommended_disposition": RECOMMENDED_DISPOSITION,
        "promotion_to_paper_or_live_barred": True,
        "is_robustness_review_only": True,
        "current_loop_stage": "robustness_sensitivity_review",
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
        "no_detector_change": True, "no_edit_token_use": True,
        "no_parameter_fitting": True, "no_weekday_change": True,
        "no_profitability_claim": True, "no_downstream_gate_unlock": True,
    }

    replay = build_c10_replay_review(repo_root, tracked_paths)
    record["replay_review_verdict"] = replay["verdict"]
    if replay["verdict"] != VERDICT_C10RR_FROZEN:
        record["verdict"] = VERDICT_C10ROB_BLOCKED
        record["blockers"].append("replay_review_not_frozen")
        return record
    if replay.get("expected_replay_ledger_sha256") != (
            EXPECTED_REPLAY_LEDGER_SHA256):
        record["verdict"] = VERDICT_C10ROB_BLOCKED
        record["blockers"].append("replay_ledger_sha_mismatch")
        return record

    tracked = set(tracked_paths or [])
    if ROBUSTNESS_PATH in tracked:
        record["verdict"] = VERDICT_C10ROB_BLOCKED
        record["blockers"].append("robustness_artifact_tracked")
        return record

    record["verdict"] = VERDICT_C10ROB_FROZEN
    return record


def validate_c10_robustness_review(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. FROZEN is valid only when the honest decay
    framing, cost-survival facts, locks, and capability locks are intact."""
    failures: list = []
    if record.get("verdict") != VERDICT_C10ROB_FROZEN:
        failures.append("verdict_not_frozen")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") not in (
            VERDICT_C10ROB_FROZEN, VERDICT_C10ROB_REJECTED,
            VERDICT_C10ROB_INCONCLUSIVE):
        failures.append("verdict_not_in_allowed_set")

    for field, expected in (
            ("expected_replay_ledger_sha256", EXPECTED_REPLAY_LEDGER_SHA256),
            ("expected_robustness_sha256", EXPECTED_ROBUSTNESS_SHA256)):
        v = record.get(field)
        if not isinstance(v, str) or len(v) != 64 or v != expected:
            failures.append("bad_sha_%s" % field)
    if record.get("head_at_replay_review") != HEAD_AT_REPLAY_REVIEW:
        failures.append("head_tampered")

    # Honest decay framing must be intact.
    if record.get("decay_2025_is_warning") is not True:
        failures.append("decay_warning_flag_tampered")
    if record.get("decay_2025_is_blocker") is not False:
        failures.append("decay_blocker_flag_tampered")
    if record.get("decay_2025_classification") != DECAY_2025_CLASSIFICATION:
        failures.append("decay_classification_tampered")
    if record.get("promotion_to_paper_or_live_barred") is not True:
        failures.append("promotion_bar_removed")
    if record.get("recommended_disposition") != RECOMMENDED_DISPOSITION:
        failures.append("disposition_tampered")

    sf = record.get("survival_flags") or {}
    if sf.get("survives_cost_75bps_all_variants") is not True:
        failures.append("cost75_survival_tampered")
    if sf.get("decay_2025_negative_all_variants") is not True:
        failures.append("2025_negative_flag_tampered")
    if sf.get("all_individual_years_positive") is not False:
        failures.append("all_years_positive_flag_tampered")

    # Per-variant 2025 must stay negative; first-half must dominate second.
    sub = record.get("sub_period_net_r") or {}
    for name in ("2r", "3r", "4r"):
        v = sub.get(name) or {}
        if not (isinstance(v.get("2025"), (int, float)) and v["2025"] < 0):
            failures.append("2025_sign_tampered_%s" % name)
        if not (isinstance(v.get("first_half"), (int, float))
                and isinstance(v.get("second_half"), (int, float))
                and v["first_half"] > v["second_half"]):
            failures.append("front_loading_tampered_%s" % name)

    # Horizon robustness: every horizon positive for every variant.
    hs = record.get("horizon_sensitivity_net_r") or {}
    for name in ("2r", "3r", "4r"):
        v = hs.get(name) or {}
        if not all(isinstance(v.get(h), (int, float)) and v[h] > 0
                   for h in ("h3", "h5", "h7", "h10")):
            failures.append("horizon_positivity_tampered_%s" % name)

    locks = record.get("scope_locks") or {}
    for key, val in locks.items():
        if val is not True:
            failures.append("scope_lock_false_%s" % key)
    for key in ("relabel_gate_locked", "paper_trading_gate_locked",
                "micro_live_gate_locked", "live_gate_locked",
                "human_review_required", "is_robustness_review_only"):
        if record.get(key) is not True:
            failures.append("gate_flag_tampered_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    for required in ("no_profitability_claim", "promotion_to_paper_or_live_barred",
                     "regime_decay_2025_disclosed_as_warning"):
        if required not in (record.get("claim_locks") or []):
            failures.append("claim_lock_missing_%s" % required)

    return {"valid": not failures, "failures": failures}

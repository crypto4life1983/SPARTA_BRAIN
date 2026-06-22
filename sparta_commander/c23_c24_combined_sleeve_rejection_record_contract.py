"""C23 + C24 COMBINED PORTFOLIO-SLEEVE REJECTION RECORD (PURE, RESEARCH ONLY).

Records the formal combined REJECTION of Candidate #23 (cross-sectional low-volatility,
beta-neutral) and Candidate #24 (cross-sectional illiquidity / Amihud, beta-neutral) AS
PORTFOLIO SLEEVES, based on the pushed exploratory evaluation evidence (commit 81654725) over
the local frozen broad crypto universe (manifest SHA 6dde4028...).

SCOPE NOTE: this is a PORTFOLIO-SLEEVE-LANE finding (advisory). It does NOT modify the official
candidate-pipeline rejected-family ledger, does NOT change the C23/C24 pipeline proposal
status, does NOT advance C22 (which remains the active HOLD lane at 3/20), and does NOT
activate or promote C23 or C24. It is a kept-on-record research artifact only.

HONEST EVIDENCE (exploratory, survivorship-biased Binance-public liquid-major universe -- NOT
a deployment claim):
  C23 low-vol neutral sleeve: net CAGR -3.8%, Sharpe -0.02, maxDD -45.9%, total -19%. The
    short high-vol leg bled badly (high-vol crypto melts up), annualized turnover 14.8x and
    cost drag 29.5%. The long low-vol leg ALONE was positive -- but that is a directional tilt,
    NOT the approved dollar-neutral C23 sleeve.
  C24 illiquidity sleeve: net base-cost CAGR +5.9%, Sharpe 0.36, maxDD -60.5%, total +36% --
    BUT the entire return is a 2021 alt-season artifact (2021 +150.3%; ex-2021 compounded
    -45.7%; 2024 -26.2%, 2025 -33.2%, 2026 -6.2%). Non-stationary; fails top-period-removal /
    forward-OOS robustness; does NOT beat BTC buy-and-hold risk-adjusted. The feared cost
    paradox was mild (low turnover, liquid universe) -- durability, not cost, was the killer.

COMBINED DECISION: REJECT C23 and C24 as neutral cross-sectional portfolio sleeves. Neither is
a reliable return engine; the portfolio return-engine gap remains UNRESOLVED. The only confirmed
sleeve remains the always-on neutral carry null (a USEFUL_DIVERSIFIER dampener, not an engine).

It does NOTHING else: NO re-eval, NO replay, NO relabel, NO optimization, NO data fetch, NO
writes, NO paper/live/broker/order; it does not advance C22 and does not activate/promote
C23/C24. Every capability flag is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

RJ_SCHEMA_VERSION = 1
RJ_MODE = "RESEARCH_ONLY"
RJ_LANE = "portfolio_sleeve_evaluation"

RECORD_ID = "C23_C24_COMBINED_SLEEVE_REJECTION"
VERDICT_RECORDED = "REJECT_C23_AND_C24_AS_CROSS_SECTIONAL_PORTFOLIO_SLEEVES"
REJECTION_STATUS = "REJECTED_AS_PORTFOLIO_SLEEVES_KEPT_ON_RECORD"
REJECTED_AT_STAGE = "exploratory_portfolio_sleeve_evaluation"

# anchors: the pushed eval-evidence commit + the frozen data manifest hash
EVIDENCE_COMMIT = "816547254692b83b6c66993f656bc75498532368"
DATA_MANIFEST_SHA256 = (
    "6dde40284e089a1a8b59ee6a06a801818a44f44d617930cf4cb1e3284a000f99")

# --- pinned honest metrics (from the pushed exploratory evaluations) --------
C23_METRICS = {
    "net_cagr": -0.038, "sharpe": -0.02, "max_dd": -0.459, "total_return": -0.19,
    "annualized_turnover": 14.8, "cost_drag": 0.295,
}
C24_METRICS = {
    "net_base_cagr": 0.059, "sharpe": 0.36, "max_dd": -0.605, "total_return": 0.36,
    "y2021": 1.503, "ex_2021_compounded": -0.457,
    "y2024": -0.262, "y2025": -0.332, "y2026": -0.062,
}
BTC_BENCH_SHARPE = 0.49   # C24 Sharpe 0.36 < BTC 0.49 (does not beat risk-adjusted)

C23_MAIN_FAILURE = (
    "net-negative after cost: the short high-vol leg bled badly (high-vol crypto melts up), "
    "with 14.8x annualized turnover and 29.5% cost drag. The long low-vol leg alone was "
    "positive but that is a directional tilt, NOT the approved dollar-neutral C23 sleeve.")
C24_MAIN_FAILURE = (
    "not durable: the entire +36% is a 2021 alt-season artifact (2021 +150.3%; ex-2021 "
    "-45.7%; negative every year 2024-2026); fails top-period-removal / forward-OOS "
    "robustness and does not beat BTC buy-and-hold risk-adjusted. The cost paradox was mild "
    "-- durability, not cost, was the killer.")

COMBINED_REASONS = (
    "C23 is net-negative after cost (CAGR -3.8%, Sharpe -0.02).",
    "C24 is not durable (2021-only; ex-2021 -45.7%; negative 2024-2026) and fails "
    "forward-OOS / top-period-removal robustness.",
    "C24 does not beat BTC buy-and-hold risk-adjusted (Sharpe 0.36 vs 0.49).",
    "Neither qualifies as a reliable return engine.",
    "The portfolio return-engine gap remains unresolved; the only confirmed sleeve is the "
    "always-on neutral carry null (a dampener, not an engine).",
    "C22 remains the active HOLD lane; C23/C24 must not become active.",
)

CONCLUSION = (
    "Exploratory portfolio-sleeve evaluation over the frozen broad crypto universe rejects "
    "BOTH C23 (low-vol, net-negative after cost) and C24 (illiquidity, a non-stationary "
    "2021-only artifact that fails forward-OOS robustness and does not beat BTC risk-adjusted) "
    "as neutral cross-sectional portfolio sleeves. Results are survivorship-biased "
    "(Binance-public, liquid majors) and NOT a deployment claim. The return-engine gap is "
    "unresolved; the carry null remains the only confirmed (diversifier-grade) sleeve.")

NEXT_REQUIRED_ACTION = (
    "NONE__C23_AND_C24_REJECTED_AS_PORTFOLIO_SLEEVES__KEPT_ON_RECORD__RETURN_ENGINE_GAP_"
    "UNRESOLVED__ANY_FURTHER_TEST_NEEDS_A_SURVIVORSHIP_AWARE_DATA_PHASE_UNDER_SEPARATE_HUMAN_"
    "APPROVAL")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_evaluates", "re_replays", "computes_pnl", "re_detects",
    "relabels", "runs_labels", "runs_backtest", "optimizes_parameters", "reparameterizes",
    "runs_robustness", "fetches_data", "reads_real_data", "mutates_data", "stages_data",
    "auto_commits", "auto_pushes", "commits_data_files", "modifies_official_ledger",
    "modifies_lifecycle", "modifies_lane_status", "advances_c22", "activates_c23",
    "activates_c24", "promotes_c23", "promotes_c24", "parks_as_active", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials", "connects_broker",
    "connects_exchange", "uses_real_money", "places_orders", "contains_order_logic",
    "paper_trading", "live_trading", "deploys_capital", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "claims_survivorship_free",
    "crosses_into_forbidden_gate",
)


def get_combined_rejection_label() -> str:
    return (
        "C23 + C24 combined portfolio-sleeve rejection record (READ-ONLY, RESEARCH ONLY, "
        "EXPLORATORY). REJECTED_AS_PORTFOLIO_SLEEVES_KEPT_ON_RECORD -- NOT ACTIVE. C23 low-vol "
        "neutral sleeve was net-negative after cost (CAGR -3.8%, Sharpe -0.02); C24 illiquidity "
        "sleeve was a non-stationary 2021-only artifact (ex-2021 -45.7%) that fails forward-OOS "
        "robustness and does not beat BTC risk-adjusted. Survivorship-biased exploratory data; "
        "NOT a deployment claim. C22 remains active HOLD; C23/C24 not activated/promoted; "
        "official ledger/lifecycle unchanged; return-engine gap unresolved.")


def get_combined_rejection_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_c23_c24_sleeve_rejection_record() -> dict[str, Any]:
    """Assemble the frozen combined C23/C24 portfolio-sleeve rejection record. Pure; no I/O;
    rejection-record only; advisory sleeve-lane finding that changes no official status."""
    blockers: list = []
    if len(EVIDENCE_COMMIT) != 40:
        blockers.append("evidence_commit_not_sha")
    if len(DATA_MANIFEST_SHA256) != 64:
        blockers.append("manifest_hash_not_sha256")
    # the evidence must actually be a rejection (consistency guard)
    if not (C23_METRICS["net_cagr"] < 0 and C23_METRICS["sharpe"] < 0):
        blockers.append("c23_not_actually_negative")
    if not (C24_METRICS["ex_2021_compounded"] < 0 and C24_METRICS["sharpe"] < BTC_BENCH_SHARPE):
        blockers.append("c24_not_actually_failing")

    record: dict[str, Any] = {
        "schema_version": RJ_SCHEMA_VERSION, "mode": RJ_MODE, "lane": RJ_LANE,
        "record_id": RECORD_ID,
        "label": get_combined_rejection_label(),
        "is_rejection_record_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_RECORDED if not blockers else "C23_C24_REJECTION_BLOCKED"),
        "rejection_status": REJECTION_STATUS,
        "rejected_at_stage": REJECTED_AT_STAGE,
        # anchors
        "anchored_to_evidence_commit": EVIDENCE_COMMIT,
        "data_manifest_sha256": DATA_MANIFEST_SHA256,
        # pinned metrics
        "c23_metrics": dict(C23_METRICS),
        "c24_metrics": dict(C24_METRICS),
        "btc_bench_sharpe": BTC_BENCH_SHARPE,
        "c23_main_failure": C23_MAIN_FAILURE,
        "c24_main_failure": C24_MAIN_FAILURE,
        # decisive failure facts (cannot be flipped)
        "evidence_headline": {
            "c23_net_negative_after_cost": C23_METRICS["net_cagr"] < 0,
            "c24_return_is_2021_artifact": C24_METRICS["ex_2021_compounded"] < 0,
            "c24_negative_recent_years": (C24_METRICS["y2024"] < 0
                                          and C24_METRICS["y2025"] < 0
                                          and C24_METRICS["y2026"] < 0),
            "c24_does_not_beat_btc_risk_adjusted":
                C24_METRICS["sharpe"] < BTC_BENCH_SHARPE,
            "neither_is_a_return_engine": True,
        },
        "combined_decision": "REJECT",
        "combined_reasons": list(COMBINED_REASONS),
        "conclusion": CONCLUSION,
        "c23_long_leg_positive_but_not_neutral_sleeve": True,
        "c24_cost_paradox_was_mild_durability_was_killer": True,
        "return_engine_gap_unresolved": True,
        "only_confirmed_sleeve_is_carry_null_dampener": True,
        # exploratory / survivorship caveats
        "is_exploratory_only": True,
        "is_survivorship_biased": True,
        "is_survivorship_free": False,
        "is_deployment_grade": False,
        # preservation guarantees (no official-status change)
        "c22_progress_unchanged": "3/20",
        "c22_state_unchanged": "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS",
        "does_not_advance_c22": True,
        "c23_is_active": False,
        "c24_is_active": False,
        "does_not_activate_c23": True,
        "does_not_activate_c24": True,
        "does_not_promote_c23": True,
        "does_not_promote_c24": True,
        "does_not_modify_official_rejected_family_ledger": True,
        "does_not_modify_lifecycle": True,
        "does_not_modify_lane_status": True,
        "kept_on_record": True,
        "claim_locks": [
            "no_profitability_claim", "no_edge_claim", "no_survivorship_free_claim",
            "kept_on_record_not_active", "c22_unchanged", "official_ledger_unchanged",
            "exploratory_only_disclosed", "survivorship_bias_disclosed",
        ],
        "human_review_required": True,
        "current_loop_stage": "combined_sleeve_rejection_record",
        "next_required_action": NEXT_REQUIRED_ACTION,
        # gates locked
        "sleeve_promote_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_re_evaluate": True, "no_replay": True, "no_pnl": True, "no_relabel": True,
        "no_optimization": True, "no_reparameterization": True, "no_robustness_run": True,
        "no_data_fetch": True, "no_data_mutation": True, "no_commit_data": True,
        "no_modify_official_ledger": True, "no_modify_lifecycle": True,
        "no_modify_lane_status": True, "no_advance_c22": True, "no_activate_c23": True,
        "no_activate_c24": True, "no_promote_c23": True, "no_promote_c24": True,
        "no_parking_as_active": True, "no_stage": True, "no_commit": True, "no_push": True,
        "no_broker": True, "no_credentials": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_survivorship_free_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c23_c24_sleeve_rejection_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only, rejection-record-
    only, a sleeve-lane REJECT of BOTH C23 and C24 anchored to the pushed evidence commit +
    data manifest hash; preserves the decisive failure facts (C23 net-negative; C24 a 2021
    artifact, negative recent years, does not beat BTC risk-adjusted) which cannot be flipped;
    keeps C23/C24 not-active/not-promoted, C22 unchanged at 3/20 HOLD, and the official
    ledger/lifecycle/lane-status unmodified; discloses exploratory + survivorship bias and makes
    no survivorship-free/profitability claim; and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != RJ_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_rejection_record_only") is not True:
        failures.append("not_rejection_record_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_RECORDED:
        failures.append("verdict_not_reject_c23_c24")
    if record.get("rejection_status") != REJECTION_STATUS:
        failures.append("status_wrong")
    if record.get("combined_decision") != "REJECT":
        failures.append("decision_not_reject")

    # anchors
    if record.get("anchored_to_evidence_commit") != EVIDENCE_COMMIT:
        failures.append("evidence_commit_tampered")
    if record.get("data_manifest_sha256") != DATA_MANIFEST_SHA256:
        failures.append("manifest_hash_tampered")

    # decisive failure facts cannot be flipped
    eh = record.get("evidence_headline") or {}
    for k in ("c23_net_negative_after_cost", "c24_return_is_2021_artifact",
              "c24_negative_recent_years", "c24_does_not_beat_btc_risk_adjusted",
              "neither_is_a_return_engine"):
        if eh.get(k) is not True:
            failures.append("rejection_finding_cleared_%s" % k)
    c23 = record.get("c23_metrics") or {}
    c24 = record.get("c24_metrics") or {}
    if not (c23.get("net_cagr", 0) < 0 and c23.get("sharpe", 0) < 0):
        failures.append("c23_metrics_inconsistent_with_rejection")
    if not (c24.get("ex_2021_compounded", 0) < 0):
        failures.append("c24_durability_metric_inconsistent")
    if not (c24.get("sharpe", 9) < record.get("btc_bench_sharpe", 0)):
        failures.append("c24_does_not_underperform_btc")
    if len(record.get("combined_reasons") or []) < 4:
        failures.append("reasons_missing")
    if record.get("conclusion") != CONCLUSION:
        failures.append("conclusion_tampered")
    if record.get("return_engine_gap_unresolved") is not True:
        failures.append("must_state_gap_unresolved")

    # exploratory / survivorship disclosure
    if record.get("is_exploratory_only") is not True:
        failures.append("must_be_exploratory")
    if record.get("is_survivorship_biased") is not True:
        failures.append("must_disclose_survivorship_bias")
    if record.get("is_survivorship_free") is not False:
        failures.append("must_not_claim_survivorship_free")
    if record.get("is_deployment_grade") is not False:
        failures.append("must_not_claim_deployment_grade")

    # preservation: no official-status change
    if record.get("c22_progress_unchanged") != "3/20":
        failures.append("c22_progress_changed")
    if record.get("c22_state_unchanged") != "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS":
        failures.append("c22_state_changed")
    for k in ("does_not_advance_c22", "does_not_activate_c23", "does_not_activate_c24",
              "does_not_promote_c23", "does_not_promote_c24",
              "does_not_modify_official_rejected_family_ledger", "does_not_modify_lifecycle",
              "does_not_modify_lane_status", "kept_on_record"):
        if record.get(k) is not True:
            failures.append("preservation_off_%s" % k)
    if record.get("c23_is_active") is not False or record.get("c24_is_active") is not False:
        failures.append("c23_or_c24_marked_active")

    for gate in ("sleeve_promote_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_re_evaluate", "no_replay", "no_optimization", "no_data_fetch",
                "no_commit_data", "no_modify_official_ledger", "no_modify_lifecycle",
                "no_advance_c22", "no_activate_c23", "no_activate_c24", "no_promote_c23",
                "no_promote_c24", "no_commit", "no_push", "no_broker", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_survivorship_free_claim"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

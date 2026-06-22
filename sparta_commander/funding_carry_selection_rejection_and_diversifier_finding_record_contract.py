"""FUNDING-CARRY SELECTION REJECTION + ALWAYS-ON DIVERSIFIER FINDING RECORD (PURE, RESEARCH ONLY).

A dual sleeve-lane record (advisory) anchored to the pushed cross-sectional funding-carry
evaluation evidence (commit 6939826b):

  (A) REJECTS cross_sectional_crypto_funding_carry_market_neutral_v1 as a return-engine
      SELECTION candidate -- the selection/timing does NOT beat the always-on broad funding
      null after cost and is 2021-concentrated (ex-2021 +0.3%; 2024-2026 +1.2%). This is the
      C21 lesson (timing adds no edge over always-on) recurring on the funding axis.

  (B) PRESERVES the always-on broad multi-asset funding carry as a USEFUL_DIVERSIFIER /
      DAMPENER finding -- positive, low-vol, genuinely uncorrelated to BTC (~0.05), and durable
      ex-2021 (+12.1%) and in the recent regime (+8.3%) -- but a LOW-RETURN dampener, NOT a
      high-return engine; it does NOT close the 25-40% return-engine gap.

SCOPE: this is a PORTFOLIO-SLEEVE-LANE finding (advisory). It does NOT modify the official
candidate-pipeline rejected-family ledger or lifecycle, does NOT advance C22 (active HOLD at
3/20), does NOT reactivate C23/C24, and activates/promotes NOTHING. Every capability flag is
pinned False with a full scope_locks set.

CAVEATS (required, preserved): exploratory only; survivorship-biased Binance-public universe;
FUNDING-CASHFLOW-ONLY delta-neutral approximation (basis mark-to-market not reconstructable);
NO deployment/paper/live claim; deployment-grade validation would need perp-basis
mark-to-market AND survivorship-aware data.
"""
from __future__ import annotations

from typing import Any

RJ_SCHEMA_VERSION = 1
RJ_MODE = "RESEARCH_ONLY"
RJ_LANE = "portfolio_sleeve_evaluation"

RECORD_ID = "FUNDING_CARRY_SELECTION_REJECTION_AND_DIVERSIFIER_FINDING"
VERDICT = ("REJECT_FUNDING_CARRY_SELECTION_AS_RETURN_ENGINE__"
           "KEEP_ALWAYS_ON_BROAD_FUNDING_NULL_AS_DIVERSIFIER_FINDING")

EVIDENCE_COMMIT = "6939826b09c117d392f5791a9f5520a1f39090e3"

SELECTION_FAMILY = "cross_sectional_crypto_funding_carry_market_neutral"
ALWAYS_ON_FINDING = "always_on_broad_multi_asset_neutral_funding_carry"

# --- pinned honest metrics --------------------------------------------------
SELECTION_METRICS = {
    "net_74bps_cagr": 0.070, "sharpe": 2.66, "max_dd": -0.067, "total_return": 0.442,
    "ex_2021_compounded": 0.003, "y2024_2026": 0.012,
}
ALWAYS_ON_NULL_METRICS = {
    "cagr": 0.087, "sharpe": 5.23, "max_dd": -0.059, "total_return": 0.567,
    "ex_2021": 0.121, "y2024_2026": 0.083, "corr_to_btc": 0.05,
}

SELECTION_FAILURE_REASON = (
    "the cross-sectional SELECTION/timing does NOT beat the always-on broad funding null after "
    "cost (net CAGR 7.0% < null 8.7%; Sharpe 2.66 < 5.23) -- its ~10x/yr turnover at 74 bps "
    "two-leg cost negates its gross carry advantage -- AND the return is 2021-concentrated "
    "(ex-2021 +0.3%; 2024-2026 +1.2%). This is the C21 lesson (timing adds no edge over "
    "always-on carry) recurring on the funding axis.")
DIVERSIFIER_FINDING = (
    "the always-on broad multi-asset neutral funding carry is a POSITIVE, low-vol, genuinely "
    "uncorrelated (corr-to-BTC ~0.05) and durable (ex-2021 +12.1%; 2024-2026 +8.3%) "
    "USEFUL_DIVERSIFIER / dampener -- but a LOW-RETURN dampener, NOT a high-return engine; it "
    "does NOT close the 25-40% return-engine gap.")

CAVEATS = (
    "exploratory only",
    "survivorship-biased Binance-public universe (currently-listed perps; EOS/MKR excluded)",
    "FUNDING-CASHFLOW-ONLY delta-neutral approximation (spot-only OHLCV + sparse early "
    "mark_price -> basis mark-to-market not reconstructable; omits basis P&L, funding-crowding "
    "compression, real execution -> an upper-ish bound)",
    "no deployment or paper/live claim",
    "deployment-grade validation would need perp-basis mark-to-market AND survivorship-aware "
    "data",
)

CONCLUSION = (
    "Exploratory funding-cashflow-only evaluation REJECTS the cross-sectional funding-carry "
    "SELECTION as a return engine (it does not beat its own always-on null and is "
    "2021-concentrated) and PRESERVES the always-on broad funding carry as a useful but "
    "low-return uncorrelated diversifier/dampener. The 25-40% return-engine gap remains "
    "UNRESOLVED. Survivorship-biased; not a deployment claim.")

NEXT_REQUIRED_ACTION = (
    "NONE__FUNDING_CARRY_SELECTION_REJECTED__ALWAYS_ON_FUNDING_CARRY_KEPT_AS_DIVERSIFIER_"
    "FINDING__RETURN_ENGINE_GAP_UNRESOLVED__ANY_DEPLOYMENT_GRADE_TEST_NEEDS_PERP_BASIS_AND_"
    "SURVIVORSHIP_AWARE_DATA_UNDER_SEPARATE_HUMAN_APPROVAL")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "re_evaluates", "re_replays", "computes_pnl", "fetches_data",
    "runs_labels", "runs_replay", "runs_backtest", "optimizes_parameters", "reparameterizes",
    "mutates_data", "stages_data", "commits_data_files", "modifies_official_ledger",
    "modifies_lifecycle", "modifies_lane_status", "advances_c22", "reactivates_c23",
    "reactivates_c24", "activates_any_candidate", "promotes_any_candidate", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials", "connects_broker",
    "connects_exchange", "places_orders", "contains_order_logic", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "advances_without_human_approval", "claims_profitability",
    "claims_return_engine", "claims_survivorship_free", "claims_deployment_grade",
    "crosses_into_forbidden_gate",
)


def get_record_label() -> str:
    return (
        "Funding-carry selection rejection + always-on diversifier finding record (READ-ONLY, "
        "RESEARCH ONLY, EXPLORATORY). REJECTS the cross-sectional funding-carry SELECTION as a "
        "return engine (does not beat its always-on null; 2021-concentrated) and PRESERVES the "
        "always-on broad funding carry as a useful low-return uncorrelated diversifier/dampener. "
        "Funding-cashflow-only, survivorship-biased; NOT a deployment claim. C22 unchanged; "
        "C23/C24 not reactivated; official ledger/lifecycle unchanged; return-engine gap "
        "unresolved.")


def get_record_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_funding_carry_decision_record() -> dict[str, Any]:
    """Assemble the frozen dual record: REJECT the selection candidate + KEEP the always-on
    funding carry as a diversifier finding. Pure; no I/O; advisory; changes no official status."""
    blockers: list = []
    if len(EVIDENCE_COMMIT) != 40:
        blockers.append("evidence_commit_not_sha")
    if not (SELECTION_METRICS["ex_2021_compounded"] < 0.05
            and SELECTION_METRICS["net_74bps_cagr"] < ALWAYS_ON_NULL_METRICS["cagr"]):
        blockers.append("selection_not_actually_failing")
    if not (ALWAYS_ON_NULL_METRICS["cagr"] > 0 and ALWAYS_ON_NULL_METRICS["ex_2021"] > 0):
        blockers.append("diversifier_not_actually_positive")

    record: dict[str, Any] = {
        "schema_version": RJ_SCHEMA_VERSION, "mode": RJ_MODE, "lane": RJ_LANE,
        "record_id": RECORD_ID,
        "label": get_record_label(),
        "is_decision_record_only": True,
        "blockers": blockers,
        "verdict": (VERDICT if not blockers else "FUNDING_CARRY_DECISION_BLOCKED"),
        "anchored_to_evidence_commit": EVIDENCE_COMMIT,
        # (A) selection rejection
        "selection_family": SELECTION_FAMILY,
        "selection_rejected_as_return_engine": True,
        "selection_metrics": dict(SELECTION_METRICS),
        "selection_failure_reason": SELECTION_FAILURE_REASON,
        # (B) diversifier finding (kept, not promoted)
        "always_on_finding_family": ALWAYS_ON_FINDING,
        "always_on_is_useful_diversifier": True,
        "always_on_is_return_engine": False,
        "always_on_metrics": dict(ALWAYS_ON_NULL_METRICS),
        "diversifier_finding": DIVERSIFIER_FINDING,
        # decisive facts (cannot be flipped)
        "evidence_headline": {
            "selection_does_not_beat_always_on_null":
                SELECTION_METRICS["net_74bps_cagr"] < ALWAYS_ON_NULL_METRICS["cagr"],
            "selection_is_2021_concentrated": SELECTION_METRICS["ex_2021_compounded"] < 0.05,
            "always_on_is_positive_and_durable":
                ALWAYS_ON_NULL_METRICS["ex_2021"] > 0
                and ALWAYS_ON_NULL_METRICS["y2024_2026"] > 0,
            "always_on_is_uncorrelated_to_btc": abs(ALWAYS_ON_NULL_METRICS["corr_to_btc"]) < 0.2,
            "always_on_is_a_dampener_not_an_engine": True,
        },
        "conclusion": CONCLUSION,
        "return_engine_gap_unresolved": True,
        # caveats
        "caveats": list(CAVEATS),
        "is_exploratory_only": True,
        "is_survivorship_biased": True,
        "is_funding_cashflow_only_approximation": True,
        "is_survivorship_free": False,
        "is_deployment_grade": False,
        # preservation
        "c22_progress_unchanged": "3/20",
        "c22_state_unchanged": "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS",
        "does_not_advance_c22": True,
        "does_not_reactivate_c23": True,
        "does_not_reactivate_c24": True,
        "activates_no_candidate": True,
        "promotes_no_candidate": True,
        "does_not_modify_official_ledger": True,
        "does_not_modify_lifecycle": True,
        "does_not_modify_lane_status": True,
        "kept_on_record": True,
        "human_review_required": True,
        "current_loop_stage": "funding_carry_decision_record",
        "next_required_action": NEXT_REQUIRED_ACTION,
        "promote_gate_locked": True, "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_re_evaluate": True, "no_replay": True, "no_pnl": True, "no_relabel": True,
        "no_optimization": True, "no_data_fetch": True, "no_data_mutation": True,
        "no_commit_data": True, "no_modify_official_ledger": True, "no_modify_lifecycle": True,
        "no_modify_lane_status": True, "no_advance_c22": True, "no_reactivate_c23": True,
        "no_reactivate_c24": True, "no_activate_candidate": True, "no_promote_candidate": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_broker": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_return_engine_claim": True, "no_survivorship_free_claim": True,
        "no_deployment_grade_claim": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_funding_carry_decision_record(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only, decision-record-only;
    a sleeve-lane REJECT of the funding-carry SELECTION as a return engine + a KEEP of the
    always-on funding carry as a (non-engine) diversifier finding; anchored to the pushed
    evidence commit; preserves the decisive facts (selection does not beat the always-on null,
    is 2021-concentrated; the always-on carry is positive/durable/uncorrelated but a dampener
    not an engine) which cannot be flipped; discloses the exploratory + survivorship +
    funding-cashflow-only caveats and makes no deployment/return-engine/survivorship-free claim;
    keeps C22 at 3/20 HOLD, C23/C24 not reactivated, official ledger/lifecycle/lane-status
    unchanged, activates/promotes nothing; and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != RJ_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_decision_record_only") is not True:
        failures.append("not_decision_record_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT:
        failures.append("verdict_wrong")
    if record.get("anchored_to_evidence_commit") != EVIDENCE_COMMIT:
        failures.append("evidence_commit_tampered")

    # (A) selection rejection
    if record.get("selection_rejected_as_return_engine") is not True:
        failures.append("selection_not_rejected")
    sm = record.get("selection_metrics") or {}
    am = record.get("always_on_metrics") or {}
    if not (sm.get("net_74bps_cagr", 9) < am.get("cagr", 0)):
        failures.append("selection_metrics_inconsistent")
    if not (sm.get("ex_2021_compounded", 9) < 0.05):
        failures.append("selection_not_2021_concentrated")

    # (B) diversifier finding (kept, not an engine)
    if record.get("always_on_is_useful_diversifier") is not True:
        failures.append("diversifier_not_kept")
    if record.get("always_on_is_return_engine") is not False:
        failures.append("must_not_call_always_on_an_engine")
    if not (am.get("ex_2021", 0) > 0 and am.get("y2024_2026", 0) > 0):
        failures.append("diversifier_not_durable")
    if not (abs(am.get("corr_to_btc", 1)) < 0.2):
        failures.append("diversifier_not_uncorrelated")

    eh = record.get("evidence_headline") or {}
    for k in ("selection_does_not_beat_always_on_null", "selection_is_2021_concentrated",
              "always_on_is_positive_and_durable", "always_on_is_uncorrelated_to_btc",
              "always_on_is_a_dampener_not_an_engine"):
        if eh.get(k) is not True:
            failures.append("fact_cleared_%s" % k)
    if record.get("conclusion") != CONCLUSION:
        failures.append("conclusion_tampered")
    if record.get("return_engine_gap_unresolved") is not True:
        failures.append("must_state_gap_unresolved")

    # caveats
    if len(record.get("caveats") or []) < 4:
        failures.append("caveats_incomplete")
    cav = " ".join(record.get("caveats") or []).lower()
    if "survivorship" not in cav or "funding-cashflow-only" not in cav:
        failures.append("required_caveat_missing")
    for k in ("is_exploratory_only", "is_survivorship_biased",
              "is_funding_cashflow_only_approximation"):
        if record.get(k) is not True:
            failures.append("disclosure_off_%s" % k)
    if record.get("is_survivorship_free") is not False:
        failures.append("must_not_claim_survivorship_free")
    if record.get("is_deployment_grade") is not False:
        failures.append("must_not_claim_deployment_grade")

    # preservation
    if record.get("c22_progress_unchanged") != "3/20":
        failures.append("c22_progress_changed")
    if record.get("c22_state_unchanged") != "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS":
        failures.append("c22_state_changed")
    for k in ("does_not_advance_c22", "does_not_reactivate_c23", "does_not_reactivate_c24",
              "activates_no_candidate", "promotes_no_candidate",
              "does_not_modify_official_ledger", "does_not_modify_lifecycle",
              "does_not_modify_lane_status", "kept_on_record"):
        if record.get(k) is not True:
            failures.append("preservation_off_%s" % k)
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_action_wrong")

    locks = record.get("scope_locks") or {}
    for key in ("no_re_evaluate", "no_replay", "no_optimization", "no_data_fetch",
                "no_commit_data", "no_modify_official_ledger", "no_modify_lifecycle",
                "no_advance_c22", "no_reactivate_c23", "no_reactivate_c24",
                "no_activate_candidate", "no_promote_candidate", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_return_engine_claim", "no_survivorship_free_claim",
                "no_deployment_grade_claim"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

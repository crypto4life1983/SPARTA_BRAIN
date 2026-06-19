"""SPARTA Orthogonal Residual-Alpha Ensemble Meta-Study v1
(PURE, READ-ONLY, RESEARCH ONLY).

A descriptive, research-only meta-study over the ALREADY-COMMITTED, rejected C1-C19
evidence. Before any decision to open C20, it asks ONE question: viewed together, do
any of the rejected candidate signal families contain a durable, ORTHOGONAL residual
alpha worth a future candidate? It summarizes why C16-C19 failed, classifies the
recurring failure modes, gives an honest orthogonal-residual assessment, and produces
an ADVISORY three-way recommendation. The human decides.

It does NOTHING beyond reading committed contract state: it does NOT assign C20, does
NOT create a candidate / family proposal, fetches NO new data, runs NO replay / PnL
(it only SUMMARIZES values already pinned in the committed replay/labels review
contracts), runs NO optimization / tuning / rescue, and touches NO paper/live/broker/
order/trading surface. Every capability flag is pinned False with a full scope_locks
set. It is descriptive and NEVER traded.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep

MS_VERSION = "v1"
MS_MODE = "RESEARCH_ONLY"
MS_LANE = "crypto_d1_auto_research"

REJECTED_FAMILIES_C1_TO_C19 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C19)   # 24
REJECTED_FAMILY_LESSONS = dict(_rep.REJECTED_FAMILY_LESSONS)

# The advisory recommendation options (the COMPLETE allowlist).
OPTION_OPEN_C20 = "open_c20_with_a_new_family"
OPTION_STRONGER_MACHINE = "build_a_stronger_automation_machine_layer_first"
OPTION_EXPAND_UNIVERSE = (
    "stop_and_expand_research_universe_or_data_only_with_explicit_approval")
ALL_OPTIONS = (OPTION_OPEN_C20, OPTION_STRONGER_MACHINE, OPTION_EXPAND_UNIVERSE)

# The honest recommended option (advisory; the human decides). The two LIVE failure
# roots -- losing to buy-and-hold in a 3-asset crypto bull, and return/price-beta
# neutrality not persisting out of sample in a 3-asset universe -- are universe/data
# limited, not fixable by re-spinning another D1 BTC/ETH/SOL family.
RECOMMENDED_OPTION = OPTION_EXPAND_UNIVERSE

NEXT_REQUIRED_ACTION = (
    "AWAIT_HUMAN_DECISION_ON_META_STUDY_RECOMMENDATION__NO_C20_ASSIGNED")

# --- why C16-C19 failed (verbatim honest summaries) -------------------------
FAILURE_SUMMARIES = {
    "C16": ("cointegration_pairs_market_neutral -- NEUTRALITY FAILED OUT OF SAMPLE: a "
            "level-OLS hedge was not return-beta-neutral OOS (net beta 2.82 >> 0.10) "
            "and cointegration windows were too few (43 < 100); rejected at the labels "
            "gate before replay."),
    "C17": ("risk_adjusted_portfolio_construction_vol_targeted_allocation -- LOWER "
            "DRAWDOWN BUT FAILED THE RISK-ADJUSTED BUY-AND-HOLD COMPARISON: cut max "
            "drawdown to -37.8% yet did not beat SOL buy-and-hold (Sharpe 0.80 vs 1.08, "
            "Calmar 0.47 vs 0.83) or the equal-weight basket risk-adjusted, and the "
            "2026 forward-OOS edge did not hold; rejected at fee-honest replay."),
    "C18": ("h4_trend_following_market_structure -- H4 APPROXIMATION FAILED THE "
            "RISK-ADJUSTED REPLAY: made +95.4% but did not beat BTC buy-and-hold "
            "risk-adjusted (Sharpe 0.52 vs 0.93, Calmar 0.25 vs 0.60), had negative "
            "expectancy (win 15.2%, total R -101.4) and a failed 2026 forward-OOS; "
            "rejected at fee-honest replay. (Rejects the approximation, not the "
            "observed trader's exact system.)"),
    "C19": ("oos_validated_beta_neutral_cross_sectional_relative_value -- NEUTRALITY "
            "FAILED THE LABELS GATE: clean mechanics but only 41 tradeable entries "
            "(< 100 sample gate) and OOS beta-neutrality held on only 862/1977 bars "
            "(~44%), with 15 neutrality-break exits; rejected at the real-candle labels "
            "/ neutrality gate (no replay run)."),
}

# --- the recurring failure modes across C1-C19 ------------------------------
COMMON_FAILURE_MODES = (
    "BUY-AND-HOLD RISK-ADJUSTED TRAP: long-biased families reduce to crypto beta and "
    "lose to simply holding on a risk-adjusted basis (C14, C15, C17, C18).",
    "OOS-NEUTRALITY INSTABILITY: market-neutral families fail because return/price-beta "
    "neutrality does NOT persist out of sample (C16 net beta 2.82; C19 neutral on only "
    "~44% of bars).",
    "STRUCTURAL RARITY / FORWARD-OOS COLLAPSE: too few valid events to clear the "
    ">=100 sample gate and/or the forward-OOS edge does not hold (C13, C16, C19).",
    "LOWER DRAWDOWN IS NOT AN EDGE: risk management that cuts drawdown without beating "
    "the baseline risk-adjusted is not a durable edge (C17, C18).",
)

# --- orthogonal residual-alpha assessment (descriptive; never traded) -------
RESIDUAL_ASSESSMENT_BY_GROUP = {
    "timing_signals_c14_c15": (
        "Conviction-bar / time-series-momentum timing had genuine signal vs "
        "random-entry, but NO orthogonal residual survived the buy-and-hold and "
        "forward-OOS bar -- the 'edge' was directional crypto beta, not a residual."),
    "market_neutral_rv_c16_c19": (
        "Cointegration / beta-neutral relative value IS a residual-alpha construction, "
        "but its neutrality is UNSTABLE out of sample, so the residual is not "
        "persistently orthogonal -- the precondition for the alpha fails before the "
        "alpha can be measured."),
    "allocation_overlay_c17": (
        "Vol-targeted / risk-parity allocation is RISK MANAGEMENT, not a residual "
        "alpha source; it lowered drawdown but produced no orthogonal return."),
    "directional_timing_c1_c13_c18": (
        "FVG/CHoCH, breakout-pullback, trend-continuation, swing, relative-strength, "
        "vol-compression, sweep/capitulation reversion, calendar, lead-lag and the H4 "
        "approximation were all directional/MR timing signals with no orthogonal "
        "residual after costs and forward-OOS."),
}

# Honest overall finding: NO rejected family exhibited a durable orthogonal residual
# alpha worth a future candidate; combining unstable / failed signals would not
# create alpha.
ANY_FAMILY_WITH_RESIDUAL_ALPHA_WORTH_CANDIDATE = False

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "assigns_c20", "creates_candidate",
    "creates_candidate_id", "creates_family_proposal", "opens_candidate",
    "runs_detector", "runs_labels", "runs_replay", "computes_pnl",
    "applies_cost_model", "optimizes_parameters", "tunes_parameters", "runs_rescue",
    "runs_robustness", "fetches_data", "reads_real_data_beyond_committed",
    "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "reproposes_rejected_family", "trades_the_ensemble", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def get_meta_study_label() -> str:
    return (
        "Orthogonal residual-alpha ensemble meta-study v1 (READ-ONLY, RESEARCH ONLY, "
        "DESCRIPTIVE). Over the committed C1-C19 (24) rejected evidence: no rejected "
        "family shows a durable orthogonal residual alpha worth a future candidate; "
        "the recurring rocks are buy-and-hold-risk-adjusted and OOS-neutrality "
        "instability in a 3-asset D1 universe. Advisory recommendation: expand the "
        "research universe / data with explicit approval rather than re-spin another "
        "similar family. Does NOT assign C20, creates no candidate, fetches no data, "
        "runs no replay/optimization, and is never traded. NOT a profitability claim.")


def get_meta_study_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_meta_study() -> dict[str, Any]:
    """Assemble the frozen meta-study record from the committed rejected-ledger
    evidence. Pure; no I/O; assigns no C20; creates no candidate; trades nothing."""
    none_reproposed = all(opt not in REJECTED_FAMILIES_C1_TO_C19 for opt in ())
    record: dict[str, Any] = {
        "version": MS_VERSION, "mode": MS_MODE, "lane": MS_LANE,
        "is_meta_study_only": True,
        "label": get_meta_study_label(),
        # hard guarantees
        "assigns_c20": False, "c20_assigned": False, "candidate_id": None,
        "creates_candidate": False, "creates_family_proposal": False,
        "is_descriptive_never_traded": True,
        "uses_committed_evidence_only": True,
        "no_new_data_fetch": True,
        "no_optimization_tuning_rescue": True,
        "no_replay_or_pnl_beyond_committed_artifacts": True,
        # the evidence base (committed, rejected)
        "rejected_ledger_count": len(REJECTED_FAMILIES_C1_TO_C19),
        "rejected_families": list(REJECTED_FAMILIES_C1_TO_C19),
        "evidence_source": "committed C1-C19 proposal/spec/detector/labels/replay/"
                           "rejection contracts (REP rejected-ledger lessons)",
        # why C16-C19 failed
        "failure_summaries": dict(FAILURE_SUMMARIES),
        "common_failure_modes": list(COMMON_FAILURE_MODES),
        # orthogonal residual-alpha assessment
        "residual_assessment_by_group": dict(RESIDUAL_ASSESSMENT_BY_GROUP),
        "any_family_with_residual_alpha_worth_candidate":
            ANY_FAMILY_WITH_RESIDUAL_ALPHA_WORTH_CANDIDATE,
        "orthogonal_residual_finding": (
            "NO rejected C1-C19 family exhibited a durable, orthogonal residual alpha "
            "that persists out of sample. Long-biased families' 'edge' was crypto "
            "beta (lost to buy-and-hold); market-neutral families' residual was not "
            "persistently neutral OOS; allocation/overlay was risk management, not "
            "alpha. Combining unstable or failed signals would not manufacture alpha."),
        "no_rejected_family_reproposed": none_reproposed,
        # the advisory recommendation (the human decides)
        "recommendation": {
            "options": list(ALL_OPTIONS),
            "recommended_option": RECOMMENDED_OPTION,
            "rationale": (
                "Four consecutive rejections (C16-C19) split cleanly into two live "
                "failure roots: (a) long-biased constructions lose to buy-and-hold "
                "risk-adjusted in a 3-asset crypto bull (C17, C18), and (b) "
                "return/price-beta neutrality does not persist out of sample in a "
                "3-asset universe (C16, C19). Both roots are UNIVERSE/DATA limited. "
                "Option 1 (open C20 with another D1 BTC/ETH/SOL family) would most "
                "likely repeat one of these failures. Option 2 (stronger machine "
                "layer) is largely DONE -- the guarded controller/generator/machine/"
                "executor stack is built and tested. Therefore the highest-leverage "
                "next step is Option 3: expand the research universe / data (more "
                "instruments, or a structurally different return source such as "
                "funding/basis/volatility -- which need NEW data and SEPARATE "
                "approval) so a market-neutral or non-beta edge has room to exist."),
            "explicitly_not_recommended": [OPTION_OPEN_C20],
            "secondary_option": OPTION_STRONGER_MACHINE,
            "is_advisory_human_decides": True,
            "requires_explicit_human_approval_for_any_data_expansion": True,
        },
        "human_review_required": True,
        "current_loop_stage": "pre_c20_meta_study",
        "next_required_action": NEXT_REQUIRED_ACTION,
        # downstream posture (unchanged)
        "requires_human_approval_before_c20": True,
        "opening_c20_requires_explicit_open_candidate_token": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_write": True, "no_assign_c20": True,
        "no_create_candidate": True, "no_family_proposal": True,
        "no_open_candidate": True, "no_detector": True, "no_labels": True,
        "no_replay": True, "no_pnl": True, "no_optimization": True, "no_tuning": True,
        "no_rescue": True, "no_data_fetch": True, "no_real_data_beyond_committed": True,
        "no_repropose_rejected_family": True, "no_trade_the_ensemble": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_meta_study(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the study is research-only,
    meta-study-only, descriptive/never-traded, uses committed evidence only (no fetch /
    optimization / replay-beyond-committed), assigns NO C20 and creates no candidate,
    carries the four honest C16-C19 failure summaries and the recurring failure modes,
    preserves the honest 'no durable orthogonal residual alpha' finding (cannot be
    flipped to claim alpha), recommends exactly one of the three options (advisory),
    and pins every capability flag False with the scope locks."""
    failures: list = []
    if record.get("mode") != MS_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_meta_study_only") is not True:
        failures.append("not_meta_study_only")

    # hard guarantees: no C20 / no candidate / descriptive / evidence-only
    for k in ("assigns_c20", "c20_assigned", "creates_candidate",
              "creates_family_proposal"):
        if record.get(k) is not False:
            failures.append("must_be_false_%s" % k)
    if record.get("candidate_id") is not None:
        failures.append("candidate_id_must_be_none")
    for k in ("is_descriptive_never_traded", "uses_committed_evidence_only",
              "no_new_data_fetch", "no_optimization_tuning_rescue",
              "no_replay_or_pnl_beyond_committed_artifacts"):
        if record.get(k) is not True:
            failures.append("guarantee_off_%s" % k)

    # evidence base
    if record.get("rejected_ledger_count") != 24:
        failures.append("ledger_not_24")
    if record.get("no_rejected_family_reproposed") is not True:
        failures.append("a_rejected_family_reproposed")

    # the four honest C16-C19 failure summaries
    fs = record.get("failure_summaries") or {}
    for cid, frag in (("C16", "NEUTRALITY FAILED OUT OF SAMPLE"),
                      ("C17", "RISK-ADJUSTED BUY-AND-HOLD"),
                      ("C18", "RISK-ADJUSTED REPLAY"),
                      ("C19", "NEUTRALITY FAILED THE LABELS GATE")):
        if cid not in fs:
            failures.append("failure_summary_missing_%s" % cid)
        elif frag not in fs[cid]:
            failures.append("failure_summary_tampered_%s" % cid)
    if len(record.get("common_failure_modes") or []) < 4:
        failures.append("common_failure_modes_missing")

    # the honest orthogonal-residual finding cannot be flipped to claim alpha
    if record.get("any_family_with_residual_alpha_worth_candidate") is not False:
        failures.append("residual_alpha_falsely_claimed")
    if not record.get("orthogonal_residual_finding"):
        failures.append("residual_finding_missing")
    if "NO rejected" not in str(record.get("orthogonal_residual_finding", "")):
        failures.append("residual_finding_tampered")

    # the advisory recommendation: exactly one of the three options
    rec = record.get("recommendation") or {}
    if set(rec.get("options") or []) != set(ALL_OPTIONS):
        failures.append("recommendation_options_tampered")
    if rec.get("recommended_option") not in ALL_OPTIONS:
        failures.append("recommended_option_not_in_allowlist")
    if rec.get("is_advisory_human_decides") is not True:
        failures.append("recommendation_not_advisory")
    if not rec.get("rationale"):
        failures.append("recommendation_rationale_missing")
    if OPTION_OPEN_C20 not in (rec.get("explicitly_not_recommended") or []):
        failures.append("must_not_recommend_opening_c20_outright")

    # no C20 + human gate preserved
    if record.get("requires_human_approval_before_c20") is not True:
        failures.append("missing_human_approval_before_c20")
    if record.get("opening_c20_requires_explicit_open_candidate_token") is not True:
        failures.append("c20_open_token_requirement_missing")
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_action_wrong")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_assign_c20", "no_create_candidate",
                "no_family_proposal", "no_detector", "no_labels", "no_replay",
                "no_optimization", "no_data_fetch", "no_repropose_rejected_family",
                "no_trade_the_ensemble", "no_commit", "no_push", "no_paper_trading",
                "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

"""SPARTA Portfolio Sleeve Lane v1 -- PURE, READ-ONLY, ADDITIVE DESIGN (NOT a candidate).

A second, PARALLEL evaluation path that sits BESIDE -- never replaces -- the existing
candidate pipeline. It exists for strategies that may NOT beat BTC/SOL buy-and-hold
STANDALONE but may still serve the user's real objective:

  "Build a diversified set of strategies capable of targeting ~25%-40% annual return after
   costs with controlled drawdown."

It changes NO existing SPARTA rule, NO existing rejection gate, and NO candidate status; it
promotes NOTHING and reclassifies NOTHING (C13/C15/C17/C20/C21 stay exactly as they are). It
is a DESIGN: it declares the lane's two clearly-separated tracks (Standalone Strategy
Candidate vs Portfolio Sleeve Candidate), the rigour-preserving sleeve qualification criteria,
the watchlist buckets, a PURE classifier over ALREADY-GATHERED declared evidence, the future
(separately-gated) correlation-measurement PLAN over EXISTING frozen artifacts, and the three
initial measurement targets -- WITHOUT running the measurement, WITHOUT computing any
portfolio result, and WITHOUT fetching anything.

Rigor is preserved: the lane only swaps the STANDALONE "must beat buy-and-hold risk-adjusted"
lens for a PORTFOLIO "must durably contribute (low-correlation, risk-adjusted-positive)" lens.
Every other hard gate (positive-after-cost, forward-OOS, top-decile-winner-removal robustness,
no-overfit, >=100 structural sample) is KEPT. A watchlist tag is advisory only -- it is NOT
promotion, NOT deployment, and NOT an official-status change.

It runs NO correlation, NO portfolio compute, NO replay, NO labels, NO optimization, NO data
fetch; it does NOT touch the C22 replay lock, does NOT advance C22, does NOT activate C23/C24;
it builds NO broker/order/execution surface; and it commits/pushes NOTHING. Every capability
flag is pinned False with a full scope_locks set.
"""
from __future__ import annotations

from typing import Any

PSL_SCHEMA_VERSION = 1
PSL_MODE = "RESEARCH_ONLY"
PSL_LANE = "portfolio_sleeve_evaluation"

LANE_ID = "PORTFOLIO_SLEEVE_LANE_V1"
DESIGN_TOKEN = "APPROVAL_TOKEN_DESIGN_PORTFOLIO_SLEEVE_LANE_ONLY"

USER_OBJECTIVE = (
    "Build a diversified set of strategies capable of targeting approximately 25%-40% annual "
    "return after costs with controlled drawdown.")

# --- the two CLEARLY-SEPARATED tracks ---------------------------------------
TRACKS = {
    "standalone_strategy_candidate": {
        "name": "Standalone Strategy Candidate",
        "must_beat_benchmark": True,
        "benchmark": "its relevant benchmark (directional -> BTC/SOL buy-and-hold "
                     "risk-adjusted; market-neutral -> random-neutral null)",
        "purpose": "a strategy intended to be deployed on its own",
        "gate_lens": "DOMINANCE: must beat the relevant benchmark risk-adjusted, net of cost",
        "this_lane_changes_it": False,
    },
    "portfolio_sleeve_candidate": {
        "name": "Portfolio Sleeve Candidate",
        "must_beat_btc_sol_standalone": False,
        "purpose": "a stream intended to CONTRIBUTE to a diversified basket, not to win alone",
        "gate_lens": "CONTRIBUTION: must durably improve the diversified portfolio "
                     "(low-correlation + risk-adjusted-positive), net of cost",
        "this_lane_evaluates_it": True,
    },
}

# --- rigour-preserving sleeve qualification criteria (ALL required) ----------
SLEEVE_CRITERIA = (
    {"key": "positive_after_realistic_costs",
     "test": "net return > 0 at the existing 37 bps all-in cost model (UNCHANGED)"},
    {"key": "not_obviously_overfit",
     "test": "cleared the existing pipeline self-audit (no hidden tuning/optimization)"},
    {"key": "not_outlier_dependent",
     "test": "survives the existing top-decile-winner-removal robustness gate"},
    {"key": "not_structurally_broken",
     "test": "clean detector / alignment / fee / lookahead (existing audit categories)"},
    {"key": "acceptable_or_positive_forward_oos_or_hold",
     "test": "forward-OOS >= 0, OR marginally negative with a documented regime/sample reason "
             "AND a multi-window re-test plan, OR explicitly tagged HOLD_FOR_MORE_FROZEN_DATA"},
    {"key": "plausibly_diversifying_vs_btc_sol",
     "test": "low correlation to BTC/SOL buy-and-hold (the NEW evaluation axis; measured "
             "later under a separate gate, or KNOWN neutral-by-construction)"},
    {"key": "expected_portfolio_level_improvement",
     "test": "expected to improve portfolio-level Sharpe, Calmar, drawdown, or capital "
             "efficiency when added at a sensible weight"},
)

# --- watchlist buckets (advisory; NOT official status) ----------------------
BUCKETS = (
    "REJECT",
    "HOLD_FOR_MORE_DATA",
    "PORTFOLIO_SLEEVE_WATCHLIST",
    "PORTFOLIO_SLEEVE_WATCHLIST_PENDING_MEASUREMENT",
    "INSUFFICIENT_EVIDENCE",
)

# --- the future (separately-gated) correlation-measurement PLAN -------------
# Declared ONLY. NOT run here. Operates over EXISTING frozen artifacts; no fetch.
CORRELATION_MEASUREMENT_PLAN = {
    "status": "DECLARED_NOT_RUN",
    "requires_separate_human_token": True,
    "inputs_existing_frozen_only": (
        "committed C20/C21 replay ledgers (carry-null daily series) + the committed C15 replay "
        "ledger (per-trade -> daily series) + the 9 SHA-frozen public BTC/ETH/SOL OHLCV files "
        "already pinned in the C20/C21 records"),
    "measurements": (
        "pearson_and_spearman_corr_to_BTC",
        "pearson_and_spearman_corr_to_ETH",
        "pearson_and_spearman_corr_to_SOL",
        "sleeve_to_sleeve_corr_carry_null_vs_c15",
        "rolling_90d_correlation_persistence",
        "downside_conditional_correlation_on_btc_down_days",
    ),
    "no_data_fetch": True,
    "no_optimization": True,
    "no_parameter_fit": True,
    "computable_now": ("always_on_neutral_carry_null", "c15_time_series_momentum"),
    "not_computable_yet": ("c13_cross_asset_lead_lag",),   # never replayed -> no ledger
}

# --- the three initial measurement targets (FUTURE GATED WORK ONLY) ---------
# Each carries the evidence ALREADY committed (from the prior read-only audits) and the
# PROVISIONAL lane bucket the pure classifier yields. NOTHING here changes official status.
INITIAL_TARGETS = (
    {"target": "always_on_neutral_carry_null",
     "official_status": "DERIVED_FROM_C20_C21_REJECTIONS_NOT_A_CANDIDATE",
     "evidence": {
         "positive_after_cost": True,            # +21.2%, Sharpe 1.09
         "forward_oos_state": "ACCEPTABLE_MARGINAL",   # 2026 -0.5%, single window
         "outlier_dependent": False,             # continuous always-on
         "overfit": False,                       # trivial baseline (anti-overfit)
         "structurally_broken": False,           # mechanically neutral by construction
         "diversification": "NEUTRAL_BY_CONSTRUCTION",
         "expected_portfolio_improvement": True,
         "sample_sufficient": True},
     "provisional_bucket": "PORTFOLIO_SLEEVE_WATCHLIST",
     "priority": 1},
    {"target": "c15_time_series_momentum",
     "official_status": "REJECTED_C15",
     "evidence": {
         "positive_after_cost": True,            # net-positive, beats random
         "forward_oos_state": "POSITIVE",        # +0.27R
         "outlier_dependent": False,             # 200 trades
         "overfit": False,
         "structurally_broken": False,
         "diversification": "UNMEASURED",        # long-bull signature -> suspect
         "expected_portfolio_improvement": None,
         "sample_sufficient": True},
     "provisional_bucket": "PORTFOLIO_SLEEVE_WATCHLIST_PENDING_MEASUREMENT",
     "priority": 2},
    {"target": "c13_cross_asset_lead_lag",
     "official_status": "REJECTED_C13",
     "evidence": {
         "positive_after_cost": None,            # never replayed (41 labels < 100)
         "forward_oos_state": "NOT_MEASURED",
         "outlier_dependent": None,
         "overfit": None,
         "structurally_broken": None,
         "diversification": "UNMEASURED",
         "expected_portfolio_improvement": None,
         "sample_sufficient": False},            # 41 < 100
     "provisional_bucket": "HOLD_FOR_MORE_DATA",
     "priority": 3},
)

NEXT_HUMAN_GATE = (
    "HUMAN_APPROVED_RUN_PORTFOLIO_SLEEVE_CORRELATION_MEASUREMENT_FROM_EXISTING_ARTIFACTS_ONLY")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "runs_correlation_measurement", "computes_portfolio_results",
    "runs_replay", "runs_labels", "runs_detector", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "tunes_parameters", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "changes_existing_rule", "changes_existing_gate",
    "changes_candidate_status", "promotes_candidate", "promotes_rejected_candidate",
    "reclassifies_rejected_candidate", "reclassifies_c13", "reclassifies_c15",
    "reclassifies_c17", "reclassifies_c20", "reclassifies_c21", "touches_c22_replay_lock",
    "advances_c22", "activates_c23", "activates_c24", "auto_commits", "auto_pushes",
    "modifies_scheduler", "installs_scheduler", "sends_notifications", "calls_api",
    "uses_network", "uses_credentials", "uses_api_keys", "connects_signum", "uses_mcp",
    "connects_broker", "connects_exchange", "sends_trades", "places_orders",
    "contains_order_logic", "creates_execution_code", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def classify_sleeve_candidate(evidence: dict) -> dict[str, Any]:
    """PURE. Map ALREADY-GATHERED declared evidence to an advisory lane bucket. Computes
    NOTHING -- it consumes declared facts (no correlation run, no portfolio compute, no I/O)
    and applies the rigour-preserving sleeve criteria. The result is a WATCHLIST tag, never an
    official-status change."""
    e = dict(evidence or {})
    reasons: list = []

    # Never-evaluated / insufficient sample -> HOLD (cannot even be scored).
    if e.get("sample_sufficient") is False or e.get("positive_after_cost") is None:
        return {"bucket": "HOLD_FOR_MORE_DATA",
                "reasons": ["never_evaluated_or_insufficient_sample"],
                "is_official_status_change": False, "advisory_only": True}

    # Hard disqualifiers (existing gates, KEPT): cost / broken / overfit / outlier.
    if e.get("positive_after_cost") is False:
        reasons.append("net_negative_after_cost")
    if e.get("structurally_broken") is True:
        reasons.append("structurally_broken")
    if e.get("overfit") is True:
        reasons.append("overfit")
    if e.get("outlier_dependent") is True:
        reasons.append("outlier_dependent")
    # Forward-OOS: only a clearly NEGATIVE (non-marginal) OOS is a hard durability fail.
    if e.get("forward_oos_state") == "NEGATIVE":
        reasons.append("forward_oos_negative")
    if reasons:
        return {"bucket": "REJECT", "reasons": reasons,
                "is_official_status_change": False, "advisory_only": True}

    # Diversification lens (the NEW axis).
    div = e.get("diversification")
    if div == "HIGH_MEASURED":
        return {"bucket": "REJECT", "reasons": ["high_correlation_not_diversifying"],
                "is_official_status_change": False, "advisory_only": True}
    if div == "UNMEASURED":
        return {"bucket": "PORTFOLIO_SLEEVE_WATCHLIST_PENDING_MEASUREMENT",
                "reasons": ["passes_all_but_correlation_unmeasured"],
                "is_official_status_change": False, "advisory_only": True}
    if div in ("NEUTRAL_BY_CONSTRUCTION", "LOW_MEASURED"):
        if e.get("forward_oos_state") in ("POSITIVE", "ACCEPTABLE_MARGINAL"):
            return {"bucket": "PORTFOLIO_SLEEVE_WATCHLIST",
                    "reasons": ["positive_after_cost_diversifying_durable"],
                    "is_official_status_change": False, "advisory_only": True}
    return {"bucket": "INSUFFICIENT_EVIDENCE", "reasons": ["criteria_incomplete"],
            "is_official_status_change": False, "advisory_only": True}


def build_portfolio_sleeve_lane_design() -> dict[str, Any]:
    """Assemble the frozen Portfolio Sleeve Lane v1 DESIGN record. Pure; no I/O; design only;
    additive; changes no rule/gate/status; runs no measurement."""
    targets = []
    for t in INITIAL_TARGETS:
        provisional = classify_sleeve_candidate(t["evidence"])
        targets.append({**{k: t[k] for k in
                           ("target", "official_status", "evidence",
                            "provisional_bucket", "priority")},
                        "classifier_bucket": provisional["bucket"],
                        "classifier_consistent": provisional["bucket"] == t["provisional_bucket"]})

    record: dict[str, Any] = {
        "schema_version": PSL_SCHEMA_VERSION, "mode": PSL_MODE, "lane": PSL_LANE,
        "lane_id": LANE_ID,
        "is_pure_design_only": True,
        "is_additive": True,
        "approved_via": DESIGN_TOKEN,
        "verdict": "PORTFOLIO_SLEEVE_LANE_V1_DESIGN_FROZEN_FOR_HUMAN_REVIEW",
        "user_objective": USER_OBJECTIVE,
        # the two clearly-separated tracks
        "tracks": {k: dict(v) for k, v in TRACKS.items()},
        "standalone_track_unchanged": True,
        "sleeve_track_does_not_require_beating_btc_sol_standalone": True,
        # rigour-preserving criteria + buckets
        "sleeve_criteria": [dict(c) for c in SLEEVE_CRITERIA],
        "buckets": list(BUCKETS),
        # the future, separately-gated measurement plan (declared, not run)
        "correlation_measurement_plan": {
            k: (list(v) if isinstance(v, tuple) else v)
            for k, v in CORRELATION_MEASUREMENT_PLAN.items()},
        "measurement_run_here": False,
        "portfolio_results_computed_here": False,
        # the three initial targets with provisional (advisory) buckets
        "initial_targets": targets,
        # explicit preservation guarantees
        "changes_no_existing_rule": True,
        "changes_no_existing_gate": True,
        "changes_no_candidate_status": True,
        "promotes_nothing": True,
        "reclassifies_nothing": True,
        "c13_c15_c17_c20_c21_unchanged": True,
        "c22_replay_lock_untouched": True,
        "does_not_advance_c22": True,
        "does_not_activate_c23": True,
        "does_not_activate_c24": True,
        "rigor_preserved_only_swaps_standalone_lens_for_contribution_lens": True,
        "watchlist_is_advisory_not_promotion": True,
        "next_human_gate": NEXT_HUMAN_GATE,
        "advances_nothing": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_run_correlation": True, "no_compute_portfolio": True,
        "no_replay": True, "no_labels": True, "no_detector": True, "no_backtest": True,
        "no_pnl": True, "no_optimization": True, "no_tuning": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_mutate_data": True, "no_change_rule": True,
        "no_change_gate": True, "no_change_candidate_status": True, "no_promote": True,
        "no_reclassify_rejected": True, "no_touch_c22_replay_lock": True,
        "no_advance_c22": True, "no_activate_c23": True, "no_activate_c24": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_signum_connection": True, "no_mcp": True,
        "no_api_keys": True, "no_credentials": True, "no_broker": True,
        "no_order_logic": True, "no_execution_code": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_portfolio_sleeve_lane_design(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only, design-only,
    additive; declares BOTH tracks with the sleeve track NOT requiring it to beat BTC/SOL
    standalone while the standalone track is unchanged; carries all seven rigour-preserving
    sleeve criteria; keeps the correlation measurement DECLARED-NOT-RUN with no fetch; carries
    the three initial targets with classifier-consistent provisional buckets; changes no
    rule/gate/status, promotes/reclassifies nothing, leaves C13/C15/C17/C20/C21 and the C22
    replay lock untouched, and does not activate C23/C24; and pins every capability flag
    False."""
    failures: list = []
    if record.get("mode") != PSL_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_pure_design_only") is not True:
        failures.append("not_design_only")
    if record.get("is_additive") is not True:
        failures.append("not_additive")
    if record.get("verdict") != "PORTFOLIO_SLEEVE_LANE_V1_DESIGN_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_wrong")

    # two clearly-separated tracks
    tracks = record.get("tracks") or {}
    st = tracks.get("standalone_strategy_candidate") or {}
    sl = tracks.get("portfolio_sleeve_candidate") or {}
    if st.get("must_beat_benchmark") is not True:
        failures.append("standalone_track_must_keep_benchmark")
    if st.get("this_lane_changes_it") is not False:
        failures.append("standalone_track_must_be_unchanged")
    if sl.get("must_beat_btc_sol_standalone") is not False:
        failures.append("sleeve_track_must_not_require_btc_sol_standalone")
    if record.get("sleeve_track_does_not_require_beating_btc_sol_standalone") is not True:
        failures.append("sleeve_separation_flag_off")

    # all seven rigour-preserving criteria present
    crit_keys = {c.get("key") for c in (record.get("sleeve_criteria") or [])}
    for must in ("positive_after_realistic_costs", "not_obviously_overfit",
                 "not_outlier_dependent", "not_structurally_broken",
                 "acceptable_or_positive_forward_oos_or_hold",
                 "plausibly_diversifying_vs_btc_sol",
                 "expected_portfolio_level_improvement"):
        if must not in crit_keys:
            failures.append("criterion_missing_%s" % must)

    # measurement declared, NOT run; no fetch
    cmp_ = record.get("correlation_measurement_plan") or {}
    if cmp_.get("status") != "DECLARED_NOT_RUN":
        failures.append("measurement_must_be_declared_not_run")
    if cmp_.get("no_data_fetch") is not True:
        failures.append("measurement_must_not_fetch")
    if record.get("measurement_run_here") is not False:
        failures.append("measurement_must_not_run_here")
    if record.get("portfolio_results_computed_here") is not False:
        failures.append("portfolio_results_must_not_compute_here")

    # three initial targets, classifier-consistent provisional buckets
    targets = record.get("initial_targets") or []
    if len(targets) != 3:
        failures.append("initial_targets_not_three")
    by_name = {t.get("target"): t for t in targets}
    expect = {
        "always_on_neutral_carry_null": "PORTFOLIO_SLEEVE_WATCHLIST",
        "c15_time_series_momentum": "PORTFOLIO_SLEEVE_WATCHLIST_PENDING_MEASUREMENT",
        "c13_cross_asset_lead_lag": "HOLD_FOR_MORE_DATA",
    }
    for name, want in expect.items():
        t = by_name.get(name)
        if not t:
            failures.append("missing_target_%s" % name)
            continue
        if t.get("provisional_bucket") != want:
            failures.append("wrong_bucket_%s" % name)
        if t.get("classifier_bucket") != want:
            failures.append("classifier_bucket_wrong_%s" % name)
        if t.get("classifier_consistent") is not True:
            failures.append("classifier_inconsistent_%s" % name)
        if name != "always_on_neutral_carry_null" and "REJECT" == t.get("official_status"):
            failures.append("must_not_restate_status_as_changed_%s" % name)

    # preservation guarantees
    for k in ("changes_no_existing_rule", "changes_no_existing_gate",
              "changes_no_candidate_status", "promotes_nothing", "reclassifies_nothing",
              "c13_c15_c17_c20_c21_unchanged", "c22_replay_lock_untouched",
              "does_not_advance_c22", "does_not_activate_c23", "does_not_activate_c24",
              "watchlist_is_advisory_not_promotion", "advances_nothing"):
        if record.get(k) is not True:
            failures.append("preservation_off_%s" % k)
    if record.get("next_human_gate") != NEXT_HUMAN_GATE:
        failures.append("next_gate_wrong")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_run_correlation", "no_compute_portfolio", "no_replay",
                "no_labels", "no_optimization", "no_data_fetch", "no_change_rule",
                "no_change_gate", "no_change_candidate_status", "no_promote",
                "no_reclassify_rejected", "no_touch_c22_replay_lock", "no_advance_c22",
                "no_activate_c23", "no_activate_c24", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_execution_code", "no_paper_trading",
                "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

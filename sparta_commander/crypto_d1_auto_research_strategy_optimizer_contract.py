"""SPARTA Crypto-D1 AUTO RESEARCH STRATEGY OPTIMIZER Contract (READ-ONLY).

The constitutional spec for a future automated research loop that may work
while the operator is away -- and can NEVER touch live money, credentials, or
its own rules. This block is CONTRACT ONLY: no detector, labeler, backtest,
runner, or optimizer execution exists yet; each is a future, separately
human-approved block.

THE THREE-FILE ARCHITECTURE (frozen here):
  1. LOCKED HUMAN INSTRUCTIONS  -- human-owned rules; the optimizer can never
     modify them. Immutability is structural: they live as frozen constants
     and the validator rejects any deviation.
  2. MUTABLE STRATEGY CANDIDATE ASSET -- the ONLY object the optimizer may
     ever propose changes to (in future blocks), and even then the changes
     are research proposals awaiting human review, never live config.
  3. LOCKED SCORING/EVALUATION MECHANISM -- the optimizer can never modify
     how it is graded. Scoring charges costs/slippage, requires independent
     trades, bounds drawdown, penalizes concentration/correlation/cluster-only
     profit, rejects overfit, and demands out-of-sample validation before any
     promotion REVIEW (review by a human; promotion itself needs more).
"""

from __future__ import annotations

from typing import Any

OPT_SCHEMA_VERSION = "crypto_d1_auto_research_strategy_optimizer_contract.v1"
OPT_LABEL = ("SPARTA Crypto-D1 Auto Research Strategy Optimizer "
             "(READ-ONLY, CONTRACT ONLY)")
OPT_MODE = "RESEARCH_ONLY"
VERDICT_OPT_CONTRACT_READY = "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_READY"
VERDICT_OPT_CONTRACT_BLOCKED = "CRYPTO_D1_AUTO_RESEARCH_OPTIMIZER_CONTRACT_BLOCKED"
VERDICT_SCORE_ACCEPTED = "CANDIDATE_ACCEPTED_FOR_RESEARCH_REVIEW"
VERDICT_SCORE_REJECTED = "CANDIDATE_REJECTED"
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_MUTABLE_CANDIDATE_ASSET_SPEC"

# --- 1. LOCKED HUMAN INSTRUCTIONS (immutable; optimizer may never edit) -----
LOCKED_HUMAN_INSTRUCTIONS = (
    "research_only_no_live_money_ever_without_top_level_authorization",
    "the_optimizer_may_only_propose_changes_to_the_mutable_candidate_asset",
    "every_replay_or_evaluation_run_needs_its_own_human_approval",
    "rejected_experiments_are_recorded_never_hidden",
    "do_not_promote_resume_policy_yet_remains_preserved",
    "frozen_block_190_fresh_evidence_bars_remain_untouched",
    "human_approval_required_before_any_promotion_review_and_again_before_promotion",
)

# --- 2. MUTABLE STRATEGY CANDIDATE ASSET (the only editable object) ---------
MUTABLE_CANDIDATE_ASSET_SPEC = {
    "asset_name": "crypto_d1_strategy_candidate_asset",
    "editable_by_optimizer": True,
    "edits_are_research_proposals_awaiting_human_review": True,
    "edits_never_touch_live_trading_config": True,
    "allowed_fields": ("candidate_id", "hypothesis_text", "entry_rule_text",
                       "exit_rule_text", "risk_rule_text", "parameters",
                       "rationale", "parent_candidate_id"),
}

# --- 3. LOCKED SCORING MECHANISM (immutable; optimizer may never edit) ------
LOCKED_SCORING_RULES = (
    "net_scoring_only_after_fees_spread_and_slippage",
    "minimum_independent_trade_count_required",
    "maximum_drawdown_bounded",
    "symbol_and_day_concentration_checked",
    "correlation_penalty_against_existing_evidence",
    "cluster_only_profit_penalized",
    "overfit_candidates_rejected_on_oos_degradation",
    "out_of_sample_validation_required_before_promotion_review",
    "acceptance_saves_a_research_candidate_it_promotes_nothing",
)
MIN_INDEPENDENT_TRADES = 60
MAX_DRAWDOWN = -0.35                 # aligned with the frozen Block 190 bar
MAX_SINGLE_SYMBOL_PROFIT_SHARE = 0.60
MAX_SINGLE_DAY_PROFIT_SHARE = 0.20
MAX_CORRELATION_WITHOUT_PENALTY = 0.70
MAX_CLUSTER_PROFIT_SHARE = 0.50
MAX_OOS_DEGRADATION_PCT = 50.0

FORBIDDEN_FOREVER = (
    "placing_orders",
    "broker_or_exchange_credential_access",
    "broker_or_exchange_api_calls",
    "modifying_live_trading_config",
    "modifying_the_locked_scoring_logic",
    "modifying_the_locked_human_instructions",
    "auto_promoting_a_candidate_to_paper_or_live",
    "auto_pushing_commits",
    "hiding_rejected_experiments",
    "network_calls_of_any_kind",
    "bypassing_human_approval",
    "unlocking_paper_micro_live_or_live_gates",
)

REQUIRED_AUDIT_TRAIL = (
    "every_accepted_candidate_recorded_with_full_score_breakdown",
    "every_rejected_candidate_recorded_with_rejection_reasons",
    "audit_records_belong_to_later_separately_approved_report_blocks",
)

_REQUIRED_METRICS = (
    "net_edge_after_costs_bps", "independent_trade_count", "max_drawdown",
    "single_symbol_profit_share", "single_day_profit_share",
    "correlation_to_existing_evidence", "cluster_profit_share",
    "oos_validated", "oos_degradation_pct",
)


def get_crypto_d1_auto_research_optimizer_label() -> str:
    return OPT_LABEL


def evaluate_candidate_score(metrics: Any) -> dict[str, Any]:
    """THE LOCKED SCORER. Pure; never raises. Grades a candidate's research
    metrics against the frozen gates. Acceptance means only 'saved as a
    research candidate awaiting human review' -- it promotes NOTHING."""
    result: dict[str, Any] = {
        "verdict": None, "rejection_reasons": [], "penalties": [],
        "acceptance_promotes_nothing": True,
        "human_approval_required_before_promotion_review": True,
    }
    if not isinstance(metrics, dict):
        result["verdict"] = VERDICT_SCORE_REJECTED
        result["rejection_reasons"].append("metrics_not_a_dict")
        return result
    reasons = result["rejection_reasons"]
    for name in _REQUIRED_METRICS:
        if name not in metrics:
            reasons.append("missing_metric:" + name)
    if reasons:
        result["verdict"] = VERDICT_SCORE_REJECTED
        return result

    def num(name):
        raw = metrics.get(name)
        return float(raw) if isinstance(raw, (int, float)) and not isinstance(
            raw, bool) else None

    net = num("net_edge_after_costs_bps")
    if net is None or net <= 0:
        reasons.append("net_edge_after_costs_not_positive")
    trades = num("independent_trade_count")
    if trades is None or trades < MIN_INDEPENDENT_TRADES:
        reasons.append("independent_trade_count_below_minimum")
    dd = num("max_drawdown")
    if dd is None or dd < MAX_DRAWDOWN:
        reasons.append("max_drawdown_beyond_bound")
    sym = num("single_symbol_profit_share")
    if sym is None or sym > MAX_SINGLE_SYMBOL_PROFIT_SHARE:
        reasons.append("symbol_concentration_too_high")
    day = num("single_day_profit_share")
    if day is None or day > MAX_SINGLE_DAY_PROFIT_SHARE:
        reasons.append("single_day_concentration_too_high")
    corr = num("correlation_to_existing_evidence")
    if corr is None:
        reasons.append("correlation_missing")
    elif corr > MAX_CORRELATION_WITHOUT_PENALTY:
        result["penalties"].append("correlation_penalty_applied")
    cluster = num("cluster_profit_share")
    if cluster is None:
        reasons.append("cluster_share_missing")
    elif cluster > MAX_CLUSTER_PROFIT_SHARE:
        result["penalties"].append("cluster_only_profit_penalty_applied")
        reasons.append("profit_concentrated_in_one_cluster")
    if metrics.get("oos_validated") is not True:
        reasons.append("out_of_sample_validation_missing")
    deg = num("oos_degradation_pct")
    if deg is None or deg > MAX_OOS_DEGRADATION_PCT:
        reasons.append("overfit_rejected_oos_degradation_too_large")

    result["verdict"] = (VERDICT_SCORE_REJECTED if reasons
                         else VERDICT_SCORE_ACCEPTED)
    return result


def build_optimizer_contract() -> dict[str, Any]:
    """Assemble the optimizer constitution. PURE: defines, never acts."""
    return {
        "schema_version": OPT_SCHEMA_VERSION, "label": OPT_LABEL,
        "mode": OPT_MODE, "lane": "crypto_d1_auto_research",
        "verdict": VERDICT_OPT_CONTRACT_READY, "blockers": [],
        "locked_human_instructions": list(LOCKED_HUMAN_INSTRUCTIONS),
        "mutable_candidate_asset_spec": dict(MUTABLE_CANDIDATE_ASSET_SPEC),
        "locked_scoring_rules": list(LOCKED_SCORING_RULES),
        "forbidden_forever": list(FORBIDDEN_FOREVER),
        "required_audit_trail": list(REQUIRED_AUDIT_TRAIL),
        "min_independent_trades": MIN_INDEPENDENT_TRADES,
        "max_drawdown": MAX_DRAWDOWN,
        "max_oos_degradation_pct": MAX_OOS_DEGRADATION_PCT,
        "instructions_locked": True, "scorer_locked": True,
        "only_candidate_asset_is_mutable": True,
        "optimizer_execution_not_built_yet": True,
        "modifies_mission_flow": False,
        "modifies_pm_lane": False,
        "modifies_crypto_d1_sealed_chain": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "runs_scanner": False, "runs_backtest_now": False,
        "runs_optimization_now": False, "fetches_data": False,
        "calls_api": False, "uses_network": False, "uses_credentials": False,
        "uses_wallet": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False, "starts_scheduler": False,
        "sends_notifications": False, "authorizes_paper_execution": False,
        "authorizes_micro_live": False, "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def validate_optimizer_contract(contract: Any) -> dict[str, Any]:
    """Validate the constitution. Tampering with ANY locked structure --
    instructions, scorer rules, thresholds, forbidden list -- is an error."""
    errors: list[str] = []
    if not isinstance(contract, dict):
        return {"valid": False, "errors": ["contract_not_a_dict"]}
    c = contract
    if c.get("verdict") != VERDICT_OPT_CONTRACT_READY:
        errors.append("bad_verdict")
    if c.get("lane") != "crypto_d1_auto_research":
        errors.append("wrong_lane")
    if tuple(c.get("locked_human_instructions") or ()) != LOCKED_HUMAN_INSTRUCTIONS:
        errors.append("locked_instructions_modified")
    if tuple(c.get("locked_scoring_rules") or ()) != LOCKED_SCORING_RULES:
        errors.append("locked_scorer_modified")
    if tuple(c.get("forbidden_forever") or ()) != FORBIDDEN_FOREVER:
        errors.append("forbidden_forever_weakened")
    if tuple(c.get("required_audit_trail") or ()) != REQUIRED_AUDIT_TRAIL:
        errors.append("audit_trail_weakened")
    asset = c.get("mutable_candidate_asset_spec") or {}
    if asset != MUTABLE_CANDIDATE_ASSET_SPEC:
        errors.append("candidate_asset_spec_tampered")
    if c.get("min_independent_trades") != MIN_INDEPENDENT_TRADES:
        errors.append("trade_count_threshold_tampered")
    if c.get("max_drawdown") != MAX_DRAWDOWN:
        errors.append("drawdown_bound_tampered")
    if c.get("max_oos_degradation_pct") != MAX_OOS_DEGRADATION_PCT:
        errors.append("overfit_bound_tampered")
    for key, want in (
        ("instructions_locked", True), ("scorer_locked", True),
        ("only_candidate_asset_is_mutable", True),
        ("optimizer_execution_not_built_yet", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("modifies_crypto_d1_sealed_chain", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if c.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports", "runs_scanner",
                "runs_backtest_now", "runs_optimization_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials", "uses_wallet",
                "connects_broker", "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if c.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}

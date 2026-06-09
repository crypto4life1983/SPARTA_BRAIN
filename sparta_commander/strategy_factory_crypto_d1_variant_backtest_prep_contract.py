"""Crypto-D1 Risk-Controlled Variant Backtest Prep Contract (PREP ONLY).

A PURE, stdlib-only, read-only module that PREPARES (but never runs) the five
pre-registered, risk-controlled variant backtests defined by the risk-profile
revision plan:
  V1 trend_filter
  V2 trend_filter + cash_regime
  V3 volatility_cap + sol_concentration_cap
  V4 periodic_rebalance + sol_concentration_cap
  V5 full risk-managed (all controls)

It pins each control's EXACT fixed parameters (a single pre-registered
parameterization -- NOT a search space), builds a fully-specified manifest per
variant, confirms the QA-passed staged inputs are still intact, and emits a
READY / NOT_READY prep verdict.

It RUNS NOTHING: no variant backtest, no optimization, no parameter search, no
walk-forward, no lookahead, no paper/live/micro-live, no broker/exchange. It
fetches no data, accesses no credentials, touches no network, and UNLOCKS no gate.
paper / micro-live stay LOCKED until a SEPARATE explicit human command authorizes
an actual variant run.

Public API:
  - VARIANT_PREP_SCHEMA_VERSION / VARIANT_PREP_LABEL / VARIANT_PREP_MODE
  - VERDICT_READY / VERDICT_NOT_READY
  - CONTROL_PARAMETERS / NEXT_REQUIRED_ACTION
  - get_variant_backtest_prep_label()
  - control_parameters()
  - build_variant_manifests()
  - check_variant_prep_readiness(repo_root)
  - validate_variant_prep_report(report)
  - render_variant_prep_markdown(report)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_runner import (
    QA_REQUIRED_SYMBOLS,
)
from sparta_commander.strategy_factory_crypto_d1_baseline_backtest_prep_contract import (
    BASELINE_STRATEGY_ID,
    VERDICT_READY as BASELINE_VERDICT_READY,
    check_baseline_prep_readiness,
)
from sparta_commander.strategy_factory_crypto_d1_risk_profile_revision_plan import (
    proposed_backtest_variants,
    variant_constraints,
)
from sparta_commander.strategy_factory_crypto_d1_baseline_backtest_review_contract import (
    DO_NOT_PROMOTE_TO_PAPER_YET,
    build_baseline_review_decision,
)

VARIANT_PREP_SCHEMA_VERSION = "strategy_factory_crypto_d1_variant_backtest_prep_contract.v1"
VARIANT_PREP_LABEL = "Crypto-D1 Risk-Controlled Variant Backtest Prep Contract (PREP ONLY)"
VARIANT_PREP_MODE = "RESEARCH_ONLY"

VERDICT_READY = "READY"
VERDICT_NOT_READY = "NOT_READY"

NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_RISK_CONTROLLED_VARIANT_BACKTEST_RUN"

# Exact, pre-registered fixed parameters per control. ONE value each -- this is the
# committed parameterization, NOT a grid. Any future run uses exactly these.
CONTROL_PARAMETERS: dict[str, dict[str, Any]] = {
    "trend_filter": {"sma_window_days": 200},
    "cash_regime": {"min_sleeves_in_trend": 2, "total_sleeves": 3},
    "volatility_cap": {"vol_lookback_days": 30, "gross_exposure_cap": 1.0},
    "stop_risk_off": {"drawdown_stop": -0.25, "reentry": "trend_reconfirm"},
    "periodic_rebalance": {"cadence": "monthly"},
    "sol_concentration_cap": {"max_weight_per_asset": 0.33},
}


def get_variant_backtest_prep_label() -> str:
    """Human label for the recognized Crypto-D1 variant backtest prep contract."""
    return VARIANT_PREP_LABEL


def control_parameters() -> dict[str, dict[str, Any]]:
    """Return a fresh copy of the pre-registered control parameters. Pure."""
    return {cid: dict(params) for cid, params in CONTROL_PARAMETERS.items()}


def build_variant_manifests() -> list[dict[str, Any]]:
    """Resolve each pre-registered variant into a fully-specified manifest: its
    controls with their exact fixed parameters, the input symbols, and the run
    constraints. Pure; reads nothing from disk."""
    params = control_parameters()
    constraints = variant_constraints()
    manifests: list[dict[str, Any]] = []
    for v in proposed_backtest_variants():
        controls = list(v.get("controls") or [])
        resolved = {c: params[c] for c in controls if c in params}
        unresolved = [c for c in controls if c not in params]
        manifests.append(
            {
                "variant_id": v.get("id"),
                "description": v.get("description"),
                "base_strategy_id": BASELINE_STRATEGY_ID,
                "controls": controls,
                "fixed_parameters": resolved,
                "unresolved_controls": unresolved,
                "fully_specified": not unresolved,
                "symbols": list(QA_REQUIRED_SYMBOLS),
                "constraints": constraints,
                "hypothesis": v.get("hypothesis"),
            }
        )
    return manifests


def check_variant_prep_readiness(repo_root: str = ".") -> dict[str, Any]:
    """Decide whether the risk-controlled variant backtests are PREPARED (not run).
    READY requires: the QA-passed staged inputs are still intact (baseline prep
    READY) and every variant manifest is fully specified. Reads only what the
    baseline-prep and review checks read; writes nothing; runs no backtest."""
    baseline_prep = check_baseline_prep_readiness(repo_root)
    review = build_baseline_review_decision(repo_root)
    manifests = build_variant_manifests()

    blockers: list[str] = []
    if baseline_prep["verdict"] != BASELINE_VERDICT_READY:
        blockers.append("baseline_inputs_not_ready")
        blockers.extend("baseline:" + b for b in baseline_prep.get("blockers", []))
    if not manifests:
        blockers.append("no_variants")
    for m in manifests:
        if not m["fully_specified"]:
            blockers.append("variant_not_fully_specified:" + str(m["variant_id"]))

    verdict = VERDICT_READY if not blockers else VERDICT_NOT_READY
    return {
        "schema_version": VARIANT_PREP_SCHEMA_VERSION,
        "label": VARIANT_PREP_LABEL,
        "mode": VARIANT_PREP_MODE,
        "verdict": verdict,
        "blockers": blockers,
        "baseline_inputs_ready": baseline_prep["verdict"] == BASELINE_VERDICT_READY,
        "revision_motivated": review.get("promotion_decision") == DO_NOT_PROMOTE_TO_PAPER_YET,
        "review_promotion_decision": review.get("promotion_decision"),
        "variant_manifests": manifests,
        "variant_count": len(manifests),
        "variant_constraints": variant_constraints(),
        # Capability posture (this contract executes / authorizes nothing):
        "executes": False,
        "runs_variant_backtest": False,
        "runs_optimization": False,
        "runs_parameter_search": False,
        "runs_walk_forward": False,
        "authorizes_variant_run": False,
        "authorizes_paper_trading": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this prep):
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "no_network_used": True,
        "no_credentials_used": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def validate_variant_prep_report(report: Any) -> dict[str, Any]:
    """Validate (read-only) a variant prep report's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"valid": False, "errors": ["report_not_a_dict"]}
    r = report

    if r.get("verdict") not in (VERDICT_READY, VERDICT_NOT_READY):
        errors.append("bad_verdict")
    if r.get("schema_version") != VARIANT_PREP_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    manifests = r.get("variant_manifests")
    if not isinstance(manifests, list) or not manifests:
        errors.append("no_variant_manifests")

    constraints = r.get("variant_constraints")
    if not isinstance(constraints, dict):
        errors.append("variant_constraints_missing")
    else:
        for key in ("optimization", "parameter_search", "walk_forward",
                    "allow_shorting", "allow_leverage", "lookahead_allowed"):
            if constraints.get(key) is not False:
                errors.append("constraint_not_false:" + key)

    must_be_locked = (
        "baseline_backtest_blocked",
        "paper_trading_gate_locked",
        "micro_live_gate_locked",
    )
    for key in must_be_locked:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "runs_variant_backtest",
        "runs_optimization",
        "runs_parameter_search",
        "runs_walk_forward",
        "authorizes_variant_run",
        "authorizes_paper_trading",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_variant_prep_markdown(report: Any) -> str:
    """Render a variant prep report as deterministic markdown. Pure string work."""
    r = report if isinstance(report, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Risk-Controlled Variant Backtest Prep (PREP ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Baseline inputs ready: " + str(r.get("baseline_inputs_ready", "")))
    lines.append("- Revision motivated: " + str(r.get("revision_motivated", "")))
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    blockers = r.get("blockers") or []
    lines.append("- Blockers: " + ("none" if not blockers else ", ".join(blockers)))
    lines.append("")
    lines.append("## Variant manifests")
    for m in r.get("variant_manifests", []):
        lines.append("- " + str(m.get("variant_id")) + ": " + str(m.get("description")))
        lines.append("  - controls: " + ", ".join(m.get("controls") or []))
        lines.append("  - fixed_parameters: " + str(m.get("fixed_parameters")))
        lines.append("  - fully_specified: " + str(m.get("fully_specified")))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- baseline_backtest: BLOCKED")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    return "\n".join(lines)

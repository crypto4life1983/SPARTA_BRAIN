"""SPARTA Arbitrage Factory V1 - Data-Contract Chain RESULTS REVIEW (READ-ONLY).

Step 5 (final step) of signed batch batch_aeb83ad9d637: the review contract over
the step-4 in-memory dry walk of the lane's contract chain (seq 0 readiness ->
seq 1 scanner spec -> seq 2 data contract).

Because the dry walk was deliberately in-memory (it persisted nothing), this
review RE-DERIVES the same chain deterministically through the real builders
and applies the same findings checklist the dry walk reported:
  - every link READY and valid under its own validator,
  - explicit-gating result identical to the standalone rebuild (no hidden state),
  - downstream links REFUSE when an upstream link is tampered (negative checks),
  - the handoff of next-required-actions is exactly seq0->seq1->seq2->seq3,
  - capabilities all False and trading gates all LOCKED on every chain object.

What acceptance means -- and does not mean (validator-enforced):
  - ACCEPTED means only: the chain is coherent and the lane may, after a
    SEPARATE human approval, proceed to roadmap seq 3 (the fee/slippage model).
  - ACCEPTED is NOT that approval. It authorizes nothing, builds nothing,
    runs no scanner, reads no staged file, promotes nothing, unlocks nothing.

Public API:
  - REVIEW_SCHEMA_VERSION / REVIEW_LABEL / REVIEW_MODE
  - VERDICT_REVIEW_ACCEPTED / VERDICT_REVIEW_BLOCKED
  - REVIEW_CHECKLIST / NEXT_REQUIRED_ACTION
  - get_data_contract_results_review_label()
  - review_chain(readiness, scanner_spec, data_contract)
  - build_data_contract_results_review()
  - validate_data_contract_results_review(review)
  - render_data_contract_results_review_markdown(review)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.arbitrage_factory_v1_research_readiness_contract import (
    VERDICT_READINESS_READY,
    build_arbitrage_factory_v1_readiness,
    validate_arbitrage_factory_v1_readiness,
)
from sparta_commander.arbitrage_scanner_spec_contract import (
    VERDICT_SPEC_READY,
    record_arbitrage_scanner_spec,
    validate_arbitrage_scanner_spec,
)
from sparta_commander.arbitrage_data_contract import (
    VERDICT_DATA_CONTRACT_READY,
    record_arbitrage_data_contract,
    validate_arbitrage_data_contract,
)

REVIEW_SCHEMA_VERSION = "arbitrage_factory_v1_data_contract_results_review.v1"
REVIEW_LABEL = (
    "SPARTA Arbitrage Factory V1 Data-Contract Chain Results Review "
    "(READ-ONLY, REVIEW ONLY)"
)
REVIEW_MODE = "RESEARCH_ONLY"

VERDICT_REVIEW_ACCEPTED = "ARBITRAGE_DATA_CONTRACT_CHAIN_REVIEW_ACCEPTED"
VERDICT_REVIEW_BLOCKED = "ARBITRAGE_DATA_CONTRACT_CHAIN_REVIEW_BLOCKED"

# Roadmap seq 3 stays behind its own separate human approval.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_FEE_SLIPPAGE_MODEL"

# The findings checklist this review applies (mirrors the step-4 dry walk).
REVIEW_CHECKLIST = (
    "seq0_readiness_ready_and_valid",
    "seq1_scanner_spec_ready_and_valid",
    "seq2_data_contract_ready_and_valid",
    "explicit_gating_identical_to_standalone_rebuild",
    "tampered_upstream_refuses_downstream",
    "next_action_handoff_is_seq0_seq1_seq2_seq3",
    "capabilities_all_false_across_chain",
    "trading_gates_all_locked_across_chain",
)

_CHAIN_CAPABILITY_KEYS = (
    "executes", "runs_scanner", "fetches_data", "calls_api", "connects_broker",
    "connects_exchange", "uses_network", "uses_credentials",
    "contains_order_logic", "promotes_gate", "unlocks_downstream_gate",
)
_GATE_KEYS = (
    "paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked",
)


def get_data_contract_results_review_label() -> str:
    """Human label for the recognized data-contract chain results review."""
    return REVIEW_LABEL


def _base_review() -> dict[str, Any]:
    return {
        "schema_version": REVIEW_SCHEMA_VERSION,
        "label": REVIEW_LABEL,
        "mode": REVIEW_MODE,
        "lane": "arbitrage_factory_v1",
        "reviews_batch_step": 5,
        "covered_batch_id": "batch_aeb83ad9d637",
        "verdict": None,
        "blockers": [],
        "checklist": list(REVIEW_CHECKLIST),
        "checklist_results": {},
        "seq_verdicts": {},
        # What acceptance means, stated structurally:
        "acceptance_means_chain_coherence_only": True,
        "acceptance_is_not_seq3_authorization": True,
        "seq3_requires_its_own_human_approval": True,
        "review_reads_no_staged_files": True,
        "review_persists_nothing": True,
        "human_review_required": True,
        # Capability posture:
        "executes": False,
        "writes_files": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "starts_scheduler": False,
        "starts_daemon": False,
        "starts_background_worker": False,
        "runs_loop": False,
        "fetches_data": False,
        "calls_api": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "contains_order_logic": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNTOUCHED):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def review_chain(
    readiness: Any, scanner_spec: Any, data_contract: Any
) -> dict[str, Any]:
    """Review (read-only, in-memory) a seq0->seq1->seq2 chain against the
    findings checklist. PURE: never raises, reads no file, runs nothing."""
    review = _base_review()
    results: dict[str, bool] = {}

    objs = (readiness, scanner_spec, data_contract)
    if not all(isinstance(o, dict) for o in objs):
        review["verdict"] = VERDICT_REVIEW_BLOCKED
        review["blockers"].append("chain_objects_missing_or_not_dicts")
        return review

    review["seq_verdicts"] = {
        "seq0_readiness": readiness.get("verdict"),
        "seq1_scanner_spec": scanner_spec.get("verdict"),
        "seq2_data_contract": data_contract.get("verdict"),
    }

    results["seq0_readiness_ready_and_valid"] = (
        readiness.get("verdict") == VERDICT_READINESS_READY
        and validate_arbitrage_factory_v1_readiness(readiness).get("valid") is True
    )
    results["seq1_scanner_spec_ready_and_valid"] = (
        scanner_spec.get("verdict") == VERDICT_SPEC_READY
        and validate_arbitrage_scanner_spec(scanner_spec).get("valid") is True
    )
    results["seq2_data_contract_ready_and_valid"] = (
        data_contract.get("verdict") == VERDICT_DATA_CONTRACT_READY
        and validate_arbitrage_data_contract(data_contract).get("valid") is True
    )

    # Explicit-gating vs standalone rebuild (no hidden state).
    rebuilt_spec = record_arbitrage_scanner_spec(readiness)
    rebuilt_contract = record_arbitrage_data_contract(rebuilt_spec)
    results["explicit_gating_identical_to_standalone_rebuild"] = (
        rebuilt_spec == scanner_spec and rebuilt_contract == data_contract
    )

    # Negative checks: a tampered upstream must refuse downstream.
    tampered_readiness = dict(readiness)
    tampered_readiness["execution_capability_exists"] = True
    tampered_spec_result = record_arbitrage_scanner_spec(tampered_readiness)
    tampered_spec = dict(scanner_spec)
    tampered_spec["runs_scanner"] = True
    tampered_contract_result = record_arbitrage_data_contract(tampered_spec)
    results["tampered_upstream_refuses_downstream"] = (
        tampered_spec_result.get("verdict") != VERDICT_SPEC_READY
        and tampered_contract_result.get("verdict") != VERDICT_DATA_CONTRACT_READY
    )

    results["next_action_handoff_is_seq0_seq1_seq2_seq3"] = (
        readiness.get("next_required_action")
        == "HUMAN_APPROVED_ARBITRAGE_SCANNER_SPEC"
        and scanner_spec.get("next_required_action")
        == "HUMAN_APPROVED_ARBITRAGE_DATA_CONTRACT"
        and data_contract.get("next_required_action") == NEXT_REQUIRED_ACTION
    )

    results["capabilities_all_false_across_chain"] = all(
        o.get(k) is False for o in objs for k in _CHAIN_CAPABILITY_KEYS if k in o
    )
    results["trading_gates_all_locked_across_chain"] = all(
        o.get(k) is True for o in objs for k in _GATE_KEYS
    )

    review["checklist_results"] = results
    failed = [name for name, ok in results.items() if not ok]
    if failed:
        review["verdict"] = VERDICT_REVIEW_BLOCKED
        review["blockers"].extend("check_failed:" + name for name in failed)
    else:
        review["verdict"] = VERDICT_REVIEW_ACCEPTED
    return review


def build_data_contract_results_review() -> dict[str, Any]:
    """Re-derive the real chain deterministically and review it. Pure."""
    readiness = build_arbitrage_factory_v1_readiness()
    scanner_spec = record_arbitrage_scanner_spec(readiness)
    data_contract = record_arbitrage_data_contract(scanner_spec)
    return review_chain(readiness, scanner_spec, data_contract)


def validate_data_contract_results_review(review: Any) -> dict[str, Any]:
    """Validate (read-only) a review's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(review, dict):
        return {"valid": False, "errors": ["review_not_a_dict"]}
    r = review

    verdict = r.get("verdict")
    if verdict not in (VERDICT_REVIEW_ACCEPTED, VERDICT_REVIEW_BLOCKED):
        errors.append("bad_verdict")
    if tuple(r.get("checklist") or ()) != REVIEW_CHECKLIST:
        errors.append("checklist_tampered")

    results = r.get("checklist_results") or {}
    if verdict == VERDICT_REVIEW_ACCEPTED:
        if r.get("blockers"):
            errors.append("accepted_with_blockers")
        if set(results) != set(REVIEW_CHECKLIST):
            errors.append("accepted_without_full_checklist")
        elif not all(results.get(name) is True for name in REVIEW_CHECKLIST):
            errors.append("accepted_with_failed_check")
    if verdict == VERDICT_REVIEW_BLOCKED and not r.get("blockers"):
        errors.append("blocked_without_blockers")

    if r.get("lane") != "arbitrage_factory_v1":
        errors.append("wrong_lane")
    if r.get("reviews_batch_step") != 5:
        errors.append("wrong_batch_step")
    if r.get("covered_batch_id") != "batch_aeb83ad9d637":
        errors.append("wrong_batch_id")

    for key, err in (
        ("acceptance_means_chain_coherence_only", "acceptance_overclaims"),
        ("acceptance_is_not_seq3_authorization", "acceptance_claims_authorization"),
        ("seq3_requires_its_own_human_approval", "seq3_approval_dropped"),
        ("review_reads_no_staged_files", "review_reads_staged_files"),
        ("review_persists_nothing", "review_persists"),
        ("human_review_required", "human_review_dropped"),
    ):
        if r.get(key) is not True:
            errors.append(err)

    for key in _GATE_KEYS:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "starts_scheduler",
        "starts_daemon",
        "starts_background_worker",
        "runs_loop",
        "fetches_data",
        "calls_api",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "contains_order_logic",
        "authorizes_paper_execution",
        "authorizes_micro_live",
        "authorizes_live_trading",
        "promotes_gate",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_data_contract_results_review_markdown(review: Any) -> str:
    """Render a review as deterministic markdown. Pure string work."""
    r = review if isinstance(review, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Arbitrage Factory V1 Data-Contract Chain Results Review")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Lane: " + str(r.get("lane", "")) + " | batch "
                 + str(r.get("covered_batch_id")) + " step "
                 + str(r.get("reviews_batch_step")))
    lines.append("- Acceptance means chain coherence ONLY; seq 3 needs its own "
                 "separate human approval")
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    lines.append("")
    blockers = r.get("blockers") or []
    if blockers:
        lines.append("## Blockers (review does not accept the chain)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    lines.append("## Sequence verdicts")
    for k, v in (r.get("seq_verdicts") or {}).items():
        lines.append("- " + str(k) + ": " + str(v))
    lines.append("")
    lines.append("## Checklist results")
    results = r.get("checklist_results") or {}
    for name in r.get("checklist") or []:
        mark = "PASS" if results.get(name) else "FAIL"
        lines.append("- [" + mark + "] " + str(name))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)

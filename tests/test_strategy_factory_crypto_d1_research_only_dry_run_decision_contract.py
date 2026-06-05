"""Tests for the Strategy Factory Crypto-D1 Research-Only Dry-Run Decision
Contract (Bundle 51).

Bundle 51 is a PURE, stdlib-only, read-only *paper decision contract* builder.
It consumes a Bundle 50 crypto-d1 research-only dry-run REVIEW contract and,
only when that review contract is active + carries the Bundle 50 READY verdict
+ the Bundle 50 ready next-gate, evaluates a proposed dry-run DECISION packet
and returns a deterministic verdict describing whether a human decided, on
paper, that the next research-only paper contract is safe -- or whether the lane
should park, need more info, or be rejected. It performs NO dry run, decides on
paper only, acquires nothing, fetches nothing, inspects nothing, loads no
dataset, runs no QA/baseline/backtest/simulation, produces no trade signal,
validates no market data, reaches no broker/exchange/order/account/API surface,
triggers no automation, and writes nothing. A READY verdict unlocks NOTHING
real and still requires a separate, later, human step to build the proposed
next contract.

Coverage:
- schema / label / status / state constants stable
- verdict + gate constants stable; ordering
- activation strictly gated on Bundle 50 active + READY + ready-gate
- every verdict path: READY, NEEDS_MORE_INFO, REJECTED, PARKED, AWAIT
- each REJECTED category (forbidden allow flag, relaxed affirmation, disallowed
  enum value, automated decider, granted authority, upstream-id mismatch)
- missing field -> NEEDS_MORE_INFO; ordering reject>park>missing
- no verdict performs acquisition / unlocks any capability
- read_only True, executes False, human_approval_required True, auth/posture
  all False on every build (active or inactive)
- determinism + mutation isolation
- markdown is non-empty and writes no file
- pure stdlib import-root audit + forbidden-surface audit + no-IO audit
- commander_2_safety allowlist includes the new module + test paths
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_decision_contract import (  # noqa: E501
    DECISION_SCHEMA_VERSION,
    DEFAULT_DECISION_LABEL,
    DECISION_STATUS,
    DECISION_SAFETY_POSTURE,
    DECISION_STATE_ACTIVE,
    DECISION_STATE_BLOCKED,
    DECISION_VERDICT_READY,
    DECISION_VERDICT_NEEDS_MORE_INFO,
    DECISION_VERDICT_REJECTED,
    DECISION_VERDICT_PARKED,
    DECISION_VERDICT_AWAIT,
    ALLOWED_DECISION_VERDICTS,
    UPSTREAM_REQUIRED_REVIEW_VERDICT,
    UPSTREAM_REQUIRED_REVIEW_NEXT_GATE,
    DRY_RUN_DECISION_NEXT_REQUIRED_ACTION,
    DRY_RUN_DECISION_CURRENT_STAGE,
    DECISION_CRYPTO_D1_DRY_RUN_DECISION_REQUIRED,
    NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_READY_HUMAN_NEXT_CONTRACT_REQUIRED,  # noqa: E501
    NEXT_GATE_CRYPTO_D1_DRY_RUN_DECISION_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_DECISION_PARKED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_DECISION_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT,
    REQUIRED_DECISION_FIELDS,
    DECISION_REQUIRED_TEXT_FIELDS,
    DECISION_REQUIRED_AFFIRMATIONS,
    DECISION_FORBIDDEN_ALLOW_FLAGS,
    ALLOWED_DECISION_MODES,
    ALLOWED_DECISION_SCOPES,
    ALLOWED_PROPOSED_NEXT_CONTRACT_MODES,
    ALLOWED_PROPOSED_NEXT_CONTRACT_SCOPES,
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_research_only_dry_run_decision,
    build_crypto_d1_research_only_dry_run_decision_contract,
    validate_crypto_d1_research_only_dry_run_decision_contract,
    render_crypto_d1_research_only_dry_run_decision_contract_markdown,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_review_contract import (  # noqa: E501
    REVIEW_REQUIRED_AFFIRMATIONS,
    build_crypto_d1_research_only_dry_run_review_contract,
)
from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_preview_contract import (  # noqa: E501
    PREVIEW_REQUIRED_PROHIBITIONS,
    PREVIEW_REQUIRED_AFFIRMATIONS,
    UPSTREAM_REQUIRED_NEXT_STEP_VERDICT,
    UPSTREAM_REQUIRED_NEXT_STEP_NEXT_GATE,
    build_crypto_d1_research_only_dry_run_preview_contract,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_research_only_dry_run_decision_contract.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

_AUTH_FLAGS = (
    "approved_for_research",
    "execution_authorized",
    "paper_trading_authorized",
    "live_trading_authorized",
    "data_fetch_authorized",
    "backtest_authorized",
    "promotion_authorized",
)

_REVIEW_PACKET_ID = "RP-1"


# --- fixtures --------------------------------------------------------------

def _synthetic_next_step_contract():
    """A Bundle-48-shaped dict that activates the real Bundle 49 build."""
    return {
        "crypto_d1_post_boundary_next_step_contract_active": True,
        "next_step_verdict": UPSTREAM_REQUIRED_NEXT_STEP_VERDICT,
        "next_gate": UPSTREAM_REQUIRED_NEXT_STEP_NEXT_GATE,
        "evaluated_next_step_packet": {"decision_packet_id": "B48-NS-1"},
        "idea_id": "IDEA-1",
        "title": "Crypto-D1 lane",
        "asset_lane": "crypto",
        "timeframe_lane": "1d",
    }


def _valid_preview_packet():
    """A complete, safe, research-only dry-run preview packet (Bundle 49)."""
    p = {
        "preview_packet_id": "PP-1",
        "upstream_next_step_id": "B48-NS-1",
        "proposed_preview_scope": "dry_run_preview_only",
        "proposed_preview_mode": "research_only",
        "preview_inputs_description": "mock inputs and static metadata only",
        "preview_outputs_description": "paper preview markdown only",
        "next_step_boundary": "separate later human-run step required",
    }
    for flag in PREVIEW_REQUIRED_PROHIBITIONS + PREVIEW_REQUIRED_AFFIRMATIONS:
        p[flag] = True
    return p


def _active_preview_contract():
    """A real Bundle 49 contract that is active + READY + ready-gate."""
    return build_crypto_d1_research_only_dry_run_preview_contract(
        _synthetic_next_step_contract(), _valid_preview_packet()
    )


def _good_review_packet():
    """A complete, safe, research-only dry-run review packet (Bundle 50)."""
    p = {
        "review_packet_id": _REVIEW_PACKET_ID,
        "upstream_preview_id": "PP-1",
        "preview_contract_version": "preview.v1",
        "review_scope": "dry_run_review_only",
        "review_mode": "research_only",
        "reviewed_preview_inputs": "mock inputs and static metadata reviewed",
        "reviewed_preview_outputs": "paper preview markdown reviewed",
        "reviewer_name_or_id": "Mahmoud (human operator)",
        "next_step_boundary": "separate later human-run step required",
        "review_notes": "reviewed as research-only; no data work observed",
    }
    for flag in REVIEW_REQUIRED_AFFIRMATIONS:
        p[flag] = True
    return p


def _active_review_contract(review_packet=None):
    """A real Bundle 50 contract that is active + READY + ready-gate."""
    return build_crypto_d1_research_only_dry_run_review_contract(
        _active_preview_contract(),
        review_packet if review_packet is not None
        else _good_review_packet(),
    )


def _good_decision_packet():
    """A complete, safe, research-only dry-run decision packet (Bundle 51)."""
    p = {
        "decision_packet_id": "DP-1",
        "upstream_review_id": _REVIEW_PACKET_ID,
        "review_contract_version": "review.v1",
        "decision_scope": "dry_run_decision_only",
        "decision_mode": "research_only",
        "reviewed_findings_summary": "research-only dry-run review findings",
        "proposed_next_contract": "another research-only paper contract",
        "proposed_next_contract_scope": "research_only_paper_contract",
        "proposed_next_contract_mode": "research_only",
        "decision_rationale": "the next safe step is another paper contract",
        "next_step_boundary": "separate later human-run step required",
        "operator_name_or_id": "Mahmoud (human operator)",
        "decision_notes": "decided on paper; no data work, no execution",
    }
    for flag in DECISION_REQUIRED_AFFIRMATIONS:
        p[flag] = True
    return p


def _build(upstream=None, packet=None):
    return build_crypto_d1_research_only_dry_run_decision_contract(
        upstream if upstream is not None else _active_review_contract(),
        packet if packet is not None else _good_decision_packet(),
    )


# --- 1: schema / label / status / state constants --------------------------

def test_schema_version_stable():
    assert DECISION_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_research_only_dry_run_decision_contract.v1"
    )


def test_label_and_status_stable():
    assert DEFAULT_DECISION_LABEL == (
        "Strategy Factory Crypto-D1 Research-Only Dry-Run Decision Contract"
    )
    assert DECISION_STATUS == (
        "READ_ONLY_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_CONTRACT"
    )


def test_state_constants_stable():
    assert DECISION_STATE_ACTIVE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_CONTRACT_ACTIVE"
    )
    assert DECISION_STATE_BLOCKED == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_CONTRACT_BLOCKED"
    )


# --- 2: verdict + gate constants -------------------------------------------

def test_verdict_constants_stable():
    assert DECISION_VERDICT_READY == (
        "DRY_RUN_DECISION_READY_FOR_NEXT_RESEARCH_ONLY_CONTRACT"
    )
    assert DECISION_VERDICT_NEEDS_MORE_INFO == "DRY_RUN_DECISION_NEEDS_MORE_INFO"
    assert DECISION_VERDICT_REJECTED == "DRY_RUN_DECISION_REJECTED"
    assert DECISION_VERDICT_PARKED == "DRY_RUN_DECISION_PARKED"
    assert DECISION_VERDICT_AWAIT == (
        "AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT"
    )


def test_allowed_verdicts_order():
    assert ALLOWED_DECISION_VERDICTS == (
        DECISION_VERDICT_READY,
        DECISION_VERDICT_NEEDS_MORE_INFO,
        DECISION_VERDICT_REJECTED,
        DECISION_VERDICT_PARKED,
        DECISION_VERDICT_AWAIT,
    )


def test_upstream_required_signal_constants():
    assert UPSTREAM_REQUIRED_REVIEW_VERDICT == "DRY_RUN_REVIEW_READY"
    assert UPSTREAM_REQUIRED_REVIEW_NEXT_GATE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_READY_SEPARATE_HUMAN_RUN_"
        "REQUIRED"
    )


def test_next_gate_constants_stable():
    assert NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_READY_HUMAN_NEXT_CONTRACT_REQUIRED == (  # noqa: E501
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_READY_SEPARATE_HUMAN_NEXT_"
        "CONTRACT_REQUIRED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_DECISION_FIX_REQUIRED == (
        "CRYPTO_D1_DRY_RUN_DECISION_FIX_REQUIRED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_DECISION_PARKED == (
        "CRYPTO_D1_DRY_RUN_DECISION_PARKED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_DECISION_REJECTED == (
        "CRYPTO_D1_DRY_RUN_DECISION_REJECTED"
    )
    assert NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT == (
        "AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT"
    )


def test_next_required_action_and_stage_are_strings():
    assert isinstance(DRY_RUN_DECISION_NEXT_REQUIRED_ACTION, str)
    assert isinstance(DRY_RUN_DECISION_CURRENT_STAGE, str)
    assert DECISION_CRYPTO_D1_DRY_RUN_DECISION_REQUIRED == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_REQUIRED"
    )


# --- 3: required-field collections -----------------------------------------

def test_required_text_fields_exact():
    assert DECISION_REQUIRED_TEXT_FIELDS == (
        "decision_packet_id",
        "upstream_review_id",
        "review_contract_version",
        "decision_scope",
        "decision_mode",
        "reviewed_findings_summary",
        "proposed_next_contract",
        "proposed_next_contract_scope",
        "proposed_next_contract_mode",
        "decision_rationale",
        "next_step_boundary",
        "operator_name_or_id",
        "decision_notes",
    )


def test_required_affirmations_complete():
    for flag in (
        "explicit_human_decision",
        "research_only_acknowledgement",
        "no_execution_acknowledgement",
        "no_real_data_acquisition",
        "no_data_fetch",
        "no_data_inspection",
        "no_dataset_loading",
        "no_qa_run",
        "no_baseline_run",
        "no_backtest_run",
        "no_simulation_run",
        "no_trade_signal",
        "no_paper_live",
        "no_broker_exchange",
        "no_order_capability",
        "no_account_access",
        "no_api_keys",
        "no_automation_trigger",
        "no_runtime_write",
        "no_registry_write",
        "no_dashboard_write",
    ):
        assert flag in DECISION_REQUIRED_AFFIRMATIONS, flag
    assert len(DECISION_REQUIRED_AFFIRMATIONS) == 21


def test_required_decision_fields_is_union():
    assert REQUIRED_DECISION_FIELDS == (
        DECISION_REQUIRED_TEXT_FIELDS + DECISION_REQUIRED_AFFIRMATIONS
    )
    assert len(REQUIRED_DECISION_FIELDS) == 34


def test_allowed_modes_and_scopes():
    assert ALLOWED_DECISION_MODES == ("research_only", "research-only")
    assert "dry_run_decision_only" in ALLOWED_DECISION_SCOPES
    assert "research_only_decision" in ALLOWED_DECISION_SCOPES


def test_allowed_proposed_next_contract_modes_and_scopes():
    assert ALLOWED_PROPOSED_NEXT_CONTRACT_MODES == (
        "research_only", "research-only"
    )
    assert "research_only_paper_contract" in ALLOWED_PROPOSED_NEXT_CONTRACT_SCOPES
    assert "paper_contract" in ALLOWED_PROPOSED_NEXT_CONTRACT_SCOPES


def test_safety_posture_all_false():
    assert len(DECISION_SAFETY_POSTURE) > 0
    assert all(v is False for v in DECISION_SAFETY_POSTURE.values())


def test_forbidden_allow_flags_cover_real_capabilities():
    for flag in (
        "allow_real_data_acquisition",
        "allow_data_fetch",
        "allow_dataset_loading",
        "allow_qa_run",
        "allow_backtest_run",
        "allow_simulation_run",
        "allow_trade_signal",
        "allow_dry_run_execution",
        "approves_real_data_acquisition",
        "approves_data_fetch",
        "approves_trade_signal",
        "allow_next_real_contract",
        "next_real_contract_allowed",
        "approves_real_next_contract",
        "proceed_to_real_contract",
        "proceed_to_real_run",
    ):
        assert flag in DECISION_FORBIDDEN_ALLOW_FLAGS, flag


# --- 4: activation gating --------------------------------------------------

def test_active_when_upstream_ready_and_gate():
    c = _build()
    assert c["crypto_d1_research_only_dry_run_decision_contract_active"] is True
    assert c["crypto_d1_research_only_dry_run_decision_contract_state"] == (
        DECISION_STATE_ACTIVE
    )
    assert c["dry_run_decision_required"] == (
        DECISION_CRYPTO_D1_DRY_RUN_DECISION_REQUIRED
    )


def test_inactive_when_upstream_empty():
    c = build_crypto_d1_research_only_dry_run_decision_contract({}, {})
    assert c["crypto_d1_research_only_dry_run_decision_contract_active"] is False
    assert c["dry_run_decision_verdict"] == DECISION_VERDICT_AWAIT
    assert c["next_gate"] == (
        NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT
    )


def test_inactive_when_upstream_not_active():
    up = _active_review_contract()
    up["crypto_d1_research_only_dry_run_review_contract_active"] = False
    c = build_crypto_d1_research_only_dry_run_decision_contract(
        up, _good_decision_packet()
    )
    assert c["crypto_d1_research_only_dry_run_decision_contract_active"] is False
    assert c["dry_run_decision_verdict"] == DECISION_VERDICT_AWAIT


def test_inactive_when_wrong_verdict():
    up = _active_review_contract()
    up["dry_run_review_verdict"] = "DRY_RUN_REVIEW_NEEDS_MORE_INFO"
    c = build_crypto_d1_research_only_dry_run_decision_contract(
        up, _good_decision_packet()
    )
    assert c["crypto_d1_research_only_dry_run_decision_contract_active"] is False
    assert c["dry_run_decision_verdict"] == DECISION_VERDICT_AWAIT


def test_inactive_when_wrong_gate():
    up = _active_review_contract()
    up["next_gate"] = "SOMETHING_ELSE"
    c = build_crypto_d1_research_only_dry_run_decision_contract(
        up, _good_decision_packet()
    )
    assert c["crypto_d1_research_only_dry_run_decision_contract_active"] is False
    assert c["dry_run_decision_verdict"] == DECISION_VERDICT_AWAIT


def test_inactive_when_upstream_garbage():
    for bad in (None, [], "x", 7, {"foo": "bar"}):
        c = build_crypto_d1_research_only_dry_run_decision_contract(
            bad, _good_decision_packet()
        )
        assert (
            c["crypto_d1_research_only_dry_run_decision_contract_active"]
            is False
        )
        assert c["dry_run_decision_verdict"] == DECISION_VERDICT_AWAIT


def test_await_verdict_ignores_packet_shape():
    # Even a packet that would otherwise REJECT yields AWAIT when inactive.
    bad_packet = {**_good_decision_packet(), "allow_data_fetch": True}
    c = build_crypto_d1_research_only_dry_run_decision_contract({}, bad_packet)
    assert c["dry_run_decision_verdict"] == DECISION_VERDICT_AWAIT


# --- 5: READY path ---------------------------------------------------------

def test_ready_when_complete_and_safe():
    c = _build()
    assert c["dry_run_decision_verdict"] == DECISION_VERDICT_READY
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_READY_HUMAN_NEXT_CONTRACT_REQUIRED  # noqa: E501
    )


def test_evaluate_ready_direct():
    ev = evaluate_crypto_d1_research_only_dry_run_decision(
        _good_decision_packet(),
        {"review_packet_id": _REVIEW_PACKET_ID},
    )
    assert ev["verdict"] == DECISION_VERDICT_READY


def test_ready_validation_valid():
    c = _build()
    assert c["validation"]["valid"] is True


def test_ready_research_dash_only_mode_accepted():
    pkt = {**_good_decision_packet(), "decision_mode": "research-only"}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_READY


# --- 6: NEEDS_MORE_INFO path -----------------------------------------------

def test_empty_packet_needs_more_info():
    ev = evaluate_crypto_d1_research_only_dry_run_decision({}, {})
    assert ev["verdict"] == DECISION_VERDICT_NEEDS_MORE_INFO
    assert ev["reasons"] == ("dry_run_decision_packet_missing",)


def test_missing_each_text_field_needs_more_info():
    for key in DECISION_REQUIRED_TEXT_FIELDS:
        pkt = _good_decision_packet()
        del pkt[key]
        ev = evaluate_crypto_d1_research_only_dry_run_decision(
            pkt, {"review_packet_id": _REVIEW_PACKET_ID}
        )
        assert ev["verdict"] == DECISION_VERDICT_NEEDS_MORE_INFO, key
        assert f"{key}_required" in ev["reasons"], key


def test_missing_each_affirmation_needs_more_info():
    for flag in DECISION_REQUIRED_AFFIRMATIONS:
        pkt = _good_decision_packet()
        del pkt[flag]
        ev = evaluate_crypto_d1_research_only_dry_run_decision(
            pkt, {"review_packet_id": _REVIEW_PACKET_ID}
        )
        assert ev["verdict"] == DECISION_VERDICT_NEEDS_MORE_INFO, flag
        assert f"{flag}_must_be_affirmed_true" in ev["reasons"], flag


def test_build_needs_more_info_sets_fix_gate():
    pkt = _good_decision_packet()
    del pkt["decision_notes"]
    c = _build(_active_review_contract(), pkt)
    assert c["dry_run_decision_verdict"] == DECISION_VERDICT_NEEDS_MORE_INFO
    assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_DRY_RUN_DECISION_FIX_REQUIRED


# --- 7: REJECTED path ------------------------------------------------------

def test_reject_each_forbidden_allow_flag():
    for flag in DECISION_FORBIDDEN_ALLOW_FLAGS:
        pkt = {**_good_decision_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_decision(
            pkt, {"review_packet_id": _REVIEW_PACKET_ID}
        )
        assert ev["verdict"] == DECISION_VERDICT_REJECTED, flag
        assert f"forbidden_allow:{flag}" in ev["reasons"], flag


def test_reject_real_data_acquisition_allow_flag():
    pkt = {**_good_decision_packet(), "allow_real_data_acquisition": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


def test_reject_data_fetch_allow_flag():
    pkt = {**_good_decision_packet(), "approves_data_fetch": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


def test_reject_data_inspection_allow_flag():
    pkt = {**_good_decision_packet(), "allow_data_inspection": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


def test_reject_dataset_loading_allow_flag():
    pkt = {**_good_decision_packet(), "allow_dataset_loading": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


def test_reject_qa_baseline_backtest_simulation_allow_flags():
    for flag in (
        "allow_qa_run",
        "allow_baseline_run",
        "allow_backtest_run",
        "allow_simulation_run",
    ):
        pkt = {**_good_decision_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
        assert ev["verdict"] == DECISION_VERDICT_REJECTED, flag


def test_reject_trade_signal_allow_flag():
    pkt = {**_good_decision_packet(), "approves_trade_signal": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


def test_reject_market_data_validation_allow_flag():
    pkt = {**_good_decision_packet(), "validates_market_data": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


def test_reject_paper_live_broker_order_account_api_flags():
    for flag in (
        "allow_paper_live",
        "allow_broker_exchange",
        "allow_order_capability",
        "allow_account_access",
        "allow_api_keys",
    ):
        pkt = {**_good_decision_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
        assert ev["verdict"] == DECISION_VERDICT_REJECTED, flag


def test_reject_automation_trigger_allow_flag():
    pkt = {**_good_decision_packet(), "allow_automation_trigger": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


def test_reject_runtime_registry_dashboard_write_flags():
    for flag in (
        "allow_runtime_write",
        "allow_registry_write",
        "allow_dashboard_write",
    ):
        pkt = {**_good_decision_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
        assert ev["verdict"] == DECISION_VERDICT_REJECTED, flag


def test_reject_dry_run_execution_allow_flag():
    pkt = {**_good_decision_packet(), "executes_dry_run": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


def test_reject_proceed_to_real_contract_flag():
    pkt = {**_good_decision_packet(), "proceed_to_real_contract": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


def test_reject_next_real_contract_flag():
    pkt = {**_good_decision_packet(), "allow_next_real_contract": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


def test_reject_relaxed_each_affirmation():
    for flag in DECISION_REQUIRED_AFFIRMATIONS:
        pkt = {**_good_decision_packet(), flag: False}
        ev = evaluate_crypto_d1_research_only_dry_run_decision(
            pkt, {"review_packet_id": _REVIEW_PACKET_ID}
        )
        assert ev["verdict"] == DECISION_VERDICT_REJECTED, flag
        assert f"affirmation_relaxed:{flag}" in ev["reasons"], flag


def test_reject_disallowed_decision_mode():
    pkt = {**_good_decision_packet(), "decision_mode": "live"}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED
    assert "disallowed_value:decision_mode" in ev["reasons"]


def test_reject_disallowed_decision_scope():
    pkt = {**_good_decision_packet(), "decision_scope": "full_execution"}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED
    assert "disallowed_value:decision_scope" in ev["reasons"]


def test_reject_disallowed_proposed_next_contract_mode():
    pkt = {**_good_decision_packet(), "proposed_next_contract_mode": "live"}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED
    assert "disallowed_value:proposed_next_contract_mode" in ev["reasons"]


def test_reject_disallowed_proposed_next_contract_scope():
    pkt = {
        **_good_decision_packet(),
        "proposed_next_contract_scope": "real_live_trading",
    }
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED
    assert "disallowed_value:proposed_next_contract_scope" in ev["reasons"]


def test_reject_automated_decider_operator():
    pkt = {**_good_decision_packet(), "operator_name_or_id": "automation"}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED
    assert "automated_decider:operator_name_or_id" in ev["reasons"]


def test_reject_automated_decider_type_key():
    pkt = {**_good_decision_packet(), "decider_type": "bot"}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED
    assert "automated_decider:decider_type" in ev["reasons"]


def test_reject_granted_authority():
    pkt = {**_good_decision_packet(), "grants_capabilities": ["data_fetch"]}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED
    assert "grants_listed:grants_capabilities" in ev["reasons"]


def test_reject_upstream_id_mismatch():
    pkt = {**_good_decision_packet(), "upstream_review_id": "WRONG"}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(
        pkt, {"review_packet_id": _REVIEW_PACKET_ID}
    )
    assert ev["verdict"] == DECISION_VERDICT_REJECTED
    assert "mismatch:upstream_review_id" in ev["reasons"]


def test_no_mismatch_when_ref_absent():
    pkt = {**_good_decision_packet(), "upstream_review_id": "ANYTHING"}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_READY


def test_build_rejected_sets_reject_gate():
    pkt = {**_good_decision_packet(), "allow_data_fetch": True}
    c = _build(_active_review_contract(), pkt)
    assert c["dry_run_decision_verdict"] == DECISION_VERDICT_REJECTED
    assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_DRY_RUN_DECISION_REJECTED


def test_reject_takes_priority_over_missing():
    pkt = {**_good_decision_packet(), "allow_data_fetch": True}
    del pkt["decision_notes"]
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


def test_reject_takes_priority_over_park():
    pkt = {**_good_decision_packet(), "allow_data_fetch": True, "park": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_REJECTED


# --- 8: PARKED path --------------------------------------------------------

def test_park_via_flag():
    pkt = {**_good_decision_packet(), "park": True}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_PARKED


def test_park_via_operator_decision():
    pkt = {**_good_decision_packet(), "operator_decision": "deferred"}
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_PARKED


def test_build_parked_sets_park_gate():
    pkt = {**_good_decision_packet(), "parked": True}
    c = _build(_active_review_contract(), pkt)
    assert c["dry_run_decision_verdict"] == DECISION_VERDICT_PARKED
    assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_DRY_RUN_DECISION_PARKED


def test_park_takes_priority_over_missing():
    pkt = {**_good_decision_packet(), "park": True}
    del pkt["decision_notes"]
    ev = evaluate_crypto_d1_research_only_dry_run_decision(pkt, {})
    assert ev["verdict"] == DECISION_VERDICT_PARKED


# --- 9: safety invariants --------------------------------------------------

def test_no_verdict_authorizes_or_executes():
    cases = [
        _good_decision_packet(),                                  # READY
        {**_good_decision_packet(), "allow_data_fetch": True},    # REJECTED
        {**_good_decision_packet(), "park": True},                # PARKED
        {},                                                       # NEEDS_MORE
    ]
    for pkt in cases:
        c = _build(_active_review_contract(), pkt)
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["human_approval_required"] is True
        for flag in _AUTH_FLAGS:
            assert c[flag] is False, flag
        assert all(v is False for v in c["safety_posture"].values())
    # Inactive too.
    c = build_crypto_d1_research_only_dry_run_decision_contract({}, {})
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    for flag in _AUTH_FLAGS:
        assert c[flag] is False, flag
    assert all(v is False for v in c["safety_posture"].values())


def test_contract_mode_always_research_only():
    assert _build()["mode"] == "RESEARCH_ONLY"
    assert build_crypto_d1_research_only_dry_run_decision_contract(
        {}, {}
    )["mode"] == "RESEARCH_ONLY"


def test_contract_stage_always_decision_only():
    assert _build()["stage"] == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_ONLY"
    )
    assert build_crypto_d1_research_only_dry_run_decision_contract(
        {}, {}
    )["stage"] == "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_ONLY"


def test_blocked_capabilities_present_and_nonempty():
    c = _build()
    assert len(c["decision_blocked_capabilities"]) >= 1
    assert len(c["blocked_capabilities"]) >= 1
    assert tuple(c["remaining_real_world_capabilities_blocked"]) == (
        REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


def test_no_verdict_carries_real_capability_marker():
    for pkt in (
        _good_decision_packet(),
        {},
        {**_good_decision_packet(), "park": True},
    ):
        c = _build(_active_review_contract(), pkt)
        for flag in DECISION_FORBIDDEN_ALLOW_FLAGS:
            assert c.get(flag) in (None, False), flag


def test_no_verdict_unlocks_upstream_capability():
    # Building never flips any authorization flag on the echoed upstream
    # review contract, and never adds new top-level allow_* keys.
    c = _build()
    up = c["crypto_d1_research_only_dry_run_review_contract"]
    for flag in _AUTH_FLAGS:
        assert up[flag] is False


# --- 10: validation --------------------------------------------------------

def test_validate_public_matches_embedded():
    c = _build()
    v = validate_crypto_d1_research_only_dry_run_decision_contract(c)
    assert v == c["validation"]
    assert v["valid"] is True


def test_validate_rejects_tampered_schema():
    c = _build()
    c["schema_version"] = "tampered"
    v = validate_crypto_d1_research_only_dry_run_decision_contract(c)
    assert v["valid"] is False
    assert v["schema_version_ok"] is False


def test_validate_rejects_missing_field():
    c = _build()
    del c["safety_posture"]
    v = validate_crypto_d1_research_only_dry_run_decision_contract(c)
    assert v["valid"] is False
    assert "safety_posture" in v["missing_required_fields"]


def test_validate_rejects_executes_true():
    c = _build()
    c["executes"] = True
    v = validate_crypto_d1_research_only_dry_run_decision_contract(c)
    assert v["valid"] is False


def test_validate_rejects_tampered_posture():
    c = _build()
    c["safety_posture"]["prohibited_data_fetch"] = True
    v = validate_crypto_d1_research_only_dry_run_decision_contract(c)
    assert v["valid"] is False
    assert v["safety_all_false"] is False


def test_validate_handles_garbage():
    for bad in (None, {}, [], "x", 7):
        v = validate_crypto_d1_research_only_dry_run_decision_contract(bad)
        assert v["valid"] is False


# --- 11: determinism + mutation isolation ----------------------------------

def test_build_is_deterministic():
    a = _build()
    b = _build()
    a.pop("crypto_d1_research_only_dry_run_review_contract", None)
    b.pop("crypto_d1_research_only_dry_run_review_contract", None)
    assert a == b


def test_evaluate_is_deterministic():
    p = _good_decision_packet()
    assert (
        evaluate_crypto_d1_research_only_dry_run_decision(p, {})
        == evaluate_crypto_d1_research_only_dry_run_decision(p, {})
    )


def test_safety_posture_copy_is_isolated():
    c = _build()
    c["safety_posture"]["prohibited_data_fetch"] = True
    assert all(v is False for v in DECISION_SAFETY_POSTURE.values())
    assert all(v is False for v in _build()["safety_posture"].values())


def test_input_packet_not_mutated():
    p = _good_decision_packet()
    snapshot = dict(p)
    _build(_active_review_contract(), p)
    assert p == snapshot


# --- 12: markdown ----------------------------------------------------------

def test_markdown_nonempty_and_titled():
    md = render_crypto_d1_research_only_dry_run_decision_contract_markdown(
        _build()
    )
    assert isinstance(md, str)
    assert md.startswith(
        "# Strategy Factory Crypto-D1 Research-Only Dry-Run Decision Contract"
    )
    assert "RESEARCH_ONLY" in md
    assert "Executes: False" in md


def test_markdown_handles_minimal_contract():
    md = render_crypto_d1_research_only_dry_run_decision_contract_markdown({})
    assert isinstance(md, str) and len(md) > 0


# --- 13: pure stdlib import-root audit -------------------------------------

def test_import_roots_are_allowed_only():
    src = _MODPATH.read_text(encoding="utf-8")
    roots: set[str] = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    allowed = {"__future__", "typing", "sparta_commander"}
    assert roots <= allowed, f"unexpected import roots: {sorted(roots - allowed)}"  # noqa: E501
    for banned in ("os", "sys", "subprocess", "socket", "requests",
                   "urllib", "pathlib", "json", "http", "asyncio",
                   "datetime", "time", "random", "glob", "importlib",
                   "shutil", "io"):
        assert banned not in roots, f"banned import root present: {banned}"


# --- 14: forbidden-surface + no-IO audit -----------------------------------

def test_no_forbidden_call_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    forbidden = (
        "open(", "write_text(", "write_bytes(", ".write(", "read_text(",
        "read_bytes(", ".read(", "json.dump(", "json.load(",
        "import subprocess", "from subprocess", "Popen", "os.system",
        "os.listdir", "os.scandir", "os.walk", "listdir(", "scandir(",
        "glob(", "iglob(", "import socket", "socket.socket", "urllib",
        "requests", "httpx", "http.client", "asyncio", "place_order",
        "submit_order", "create_order", "cancel_order", "ccxt", "freqtrade",
        "paper_trade", "live_trade", "autopilot(", ".upload(", "datetime.",
        "time.time(", "random.", "subprocess.run", "check_output",
        "importlib", "__import__", "eval(", "exec(", "compile(",
    )
    hits = [tok for tok in forbidden if tok in src]
    assert hits == [], f"forbidden surface tokens present: {hits}"


def test_no_filesystem_surface():
    src = _MODPATH.read_text(encoding="utf-8")
    for tok in ("open(", ".write(", ".read(", "write_text(", "read_text(",
                "write_bytes(", "read_bytes(", "Path(", "pathlib"):
        assert tok not in src, tok


# --- 15: commander_2_safety allowlist --------------------------------------

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_crypto_d1_research_only_dry_run_'
        'decision_contract.py"' in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_research_only_dry_run_'
        'decision_contract.py"' in src
    )

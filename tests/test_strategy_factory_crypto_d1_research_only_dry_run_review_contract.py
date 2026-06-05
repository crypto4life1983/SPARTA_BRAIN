"""Tests for the Strategy Factory Crypto-D1 Research-Only Dry-Run Review
Contract (Bundle 50).

Bundle 50 is a PURE, stdlib-only, read-only *paper decision contract* builder.
It consumes a Bundle 49 crypto-d1 research-only dry-run PREVIEW contract and,
only when that preview contract is active + carries the Bundle 49 READY verdict
+ the Bundle 49 ready next-gate, evaluates a proposed dry-run REVIEW packet and
returns a deterministic verdict describing whether the reviewed research-only
dry-run preview was reviewed as safe -- or whether the lane should park, need
more info, or be rejected. It performs NO dry run, acquires nothing, fetches
nothing, inspects nothing, loads no dataset, runs no QA/baseline/backtest/
simulation, produces no trade signal, validates no market data, reaches no
broker/exchange/order/account/API surface, triggers no automation, and writes
nothing. A READY verdict unlocks NOTHING real.

Coverage:
- schema / label / status / state constants stable
- verdict + gate constants stable; ordering
- activation strictly gated on Bundle 49 active + READY + ready-gate
- every verdict path: READY, NEEDS_MORE_INFO, REJECTED, PARKED, AWAIT
- each REJECTED category (forbidden allow flag, relaxed affirmation, disallowed
  enum value, automated reviewer, granted authority, upstream-id mismatch)
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

from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_review_contract import (  # noqa: E501
    REVIEW_SCHEMA_VERSION,
    DEFAULT_REVIEW_LABEL,
    REVIEW_STATUS,
    REVIEW_SAFETY_POSTURE,
    REVIEW_STATE_ACTIVE,
    REVIEW_STATE_BLOCKED,
    REVIEW_VERDICT_READY,
    REVIEW_VERDICT_NEEDS_MORE_INFO,
    REVIEW_VERDICT_REJECTED,
    REVIEW_VERDICT_PARKED,
    REVIEW_VERDICT_AWAIT,
    ALLOWED_REVIEW_VERDICTS,
    UPSTREAM_REQUIRED_PREVIEW_VERDICT,
    UPSTREAM_REQUIRED_PREVIEW_NEXT_GATE,
    DRY_RUN_REVIEW_NEXT_REQUIRED_ACTION,
    DRY_RUN_REVIEW_CURRENT_STAGE,
    REVIEW_CRYPTO_D1_DRY_RUN_REVIEW_REQUIRED,
    NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_READY_HUMAN_RUN_REQUIRED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_PARKED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT,
    REQUIRED_REVIEW_FIELDS,
    REVIEW_REQUIRED_TEXT_FIELDS,
    REVIEW_REQUIRED_AFFIRMATIONS,
    REVIEW_FORBIDDEN_ALLOW_FLAGS,
    ALLOWED_REVIEW_MODES,
    ALLOWED_REVIEW_SCOPES,
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_research_only_dry_run_review,
    build_crypto_d1_research_only_dry_run_review_contract,
    validate_crypto_d1_research_only_dry_run_review_contract,
    render_crypto_d1_research_only_dry_run_review_contract_markdown,
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
    / "strategy_factory_crypto_d1_research_only_dry_run_review_contract.py"
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

_PREVIEW_PACKET_ID = "PP-1"


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
        "preview_packet_id": _PREVIEW_PACKET_ID,
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


def _active_preview_contract(preview_packet=None):
    """A real Bundle 49 contract that is active + READY + ready-gate."""
    return build_crypto_d1_research_only_dry_run_preview_contract(
        _synthetic_next_step_contract(),
        preview_packet if preview_packet is not None
        else _valid_preview_packet(),
    )


def _good_review_packet():
    """A complete, safe, research-only dry-run review packet."""
    p = {
        "review_packet_id": "RP-1",
        "upstream_preview_id": _PREVIEW_PACKET_ID,
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


def _build(upstream=None, packet=None):
    return build_crypto_d1_research_only_dry_run_review_contract(
        upstream if upstream is not None else _active_preview_contract(),
        packet if packet is not None else _good_review_packet(),
    )


# --- 1: schema / label / status / state constants --------------------------

def test_schema_version_stable():
    assert REVIEW_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_research_only_dry_run_review_contract.v1"
    )


def test_label_and_status_stable():
    assert DEFAULT_REVIEW_LABEL == (
        "Strategy Factory Crypto-D1 Research-Only Dry-Run Review Contract"
    )
    assert REVIEW_STATUS == (
        "READ_ONLY_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT"
    )


def test_state_constants_stable():
    assert REVIEW_STATE_ACTIVE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT_ACTIVE"
    )
    assert REVIEW_STATE_BLOCKED == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_CONTRACT_BLOCKED"
    )


# --- 2: verdict + gate constants -------------------------------------------

def test_verdict_constants_stable():
    assert REVIEW_VERDICT_READY == "DRY_RUN_REVIEW_READY"
    assert REVIEW_VERDICT_NEEDS_MORE_INFO == "DRY_RUN_REVIEW_NEEDS_MORE_INFO"
    assert REVIEW_VERDICT_REJECTED == "DRY_RUN_REVIEW_REJECTED"
    assert REVIEW_VERDICT_PARKED == "DRY_RUN_REVIEW_PARKED"
    assert REVIEW_VERDICT_AWAIT == (
        "AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT"
    )


def test_allowed_verdicts_order():
    assert ALLOWED_REVIEW_VERDICTS == (
        REVIEW_VERDICT_READY,
        REVIEW_VERDICT_NEEDS_MORE_INFO,
        REVIEW_VERDICT_REJECTED,
        REVIEW_VERDICT_PARKED,
        REVIEW_VERDICT_AWAIT,
    )


def test_upstream_required_signal_constants():
    assert UPSTREAM_REQUIRED_PREVIEW_VERDICT == "DRY_RUN_PREVIEW_READY"
    assert UPSTREAM_REQUIRED_PREVIEW_NEXT_GATE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_SEPARATE_HUMAN_RUN_"
        "REQUIRED"
    )


def test_next_gate_constants_stable():
    assert NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_READY_HUMAN_RUN_REQUIRED == (  # noqa: E501
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_READY_SEPARATE_HUMAN_RUN_"
        "REQUIRED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_FIX_REQUIRED == (
        "CRYPTO_D1_DRY_RUN_REVIEW_FIX_REQUIRED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_PARKED == (
        "CRYPTO_D1_DRY_RUN_REVIEW_PARKED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_REJECTED == (
        "CRYPTO_D1_DRY_RUN_REVIEW_REJECTED"
    )
    assert NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT == (
        "AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT"
    )


def test_next_required_action_and_stage_are_strings():
    assert isinstance(DRY_RUN_REVIEW_NEXT_REQUIRED_ACTION, str)
    assert isinstance(DRY_RUN_REVIEW_CURRENT_STAGE, str)
    assert REVIEW_CRYPTO_D1_DRY_RUN_REVIEW_REQUIRED == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_REQUIRED"
    )


# --- 3: required-field collections -----------------------------------------

def test_required_text_fields_exact():
    assert REVIEW_REQUIRED_TEXT_FIELDS == (
        "review_packet_id",
        "upstream_preview_id",
        "preview_contract_version",
        "review_scope",
        "review_mode",
        "reviewed_preview_inputs",
        "reviewed_preview_outputs",
        "reviewer_name_or_id",
        "next_step_boundary",
        "review_notes",
    )


def test_required_affirmations_complete():
    for flag in (
        "reviewed_mock_inputs_only",
        "reviewed_static_contract_metadata_only",
        "reviewed_no_real_data_acquisition",
        "reviewed_no_data_fetch",
        "reviewed_no_data_inspection",
        "reviewed_no_dataset_loading",
        "reviewed_no_qa_run",
        "reviewed_no_baseline_run",
        "reviewed_no_backtest_run",
        "reviewed_no_simulation_run",
        "reviewed_no_trade_signal",
        "reviewed_no_paper_live",
        "reviewed_no_broker_exchange",
        "reviewed_no_order_capability",
        "reviewed_no_account_access",
        "reviewed_no_api_keys",
        "reviewed_no_automation_trigger",
        "reviewed_no_runtime_write",
        "reviewed_no_registry_write",
        "reviewed_no_dashboard_write",
        "explicit_human_review",
        "research_only_acknowledgement",
        "no_execution_acknowledgement",
    ):
        assert flag in REVIEW_REQUIRED_AFFIRMATIONS, flag
    assert len(REVIEW_REQUIRED_AFFIRMATIONS) == 23


def test_required_review_fields_is_union():
    assert REQUIRED_REVIEW_FIELDS == (
        REVIEW_REQUIRED_TEXT_FIELDS + REVIEW_REQUIRED_AFFIRMATIONS
    )
    assert len(REQUIRED_REVIEW_FIELDS) == 33


def test_allowed_modes_and_scopes():
    assert ALLOWED_REVIEW_MODES == ("research_only", "research-only")
    assert "dry_run_review_only" in ALLOWED_REVIEW_SCOPES
    assert "research_only_review" in ALLOWED_REVIEW_SCOPES


def test_safety_posture_all_false():
    assert len(REVIEW_SAFETY_POSTURE) > 0
    assert all(v is False for v in REVIEW_SAFETY_POSTURE.values())


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
    ):
        assert flag in REVIEW_FORBIDDEN_ALLOW_FLAGS, flag


# --- 4: activation gating --------------------------------------------------

def test_active_when_upstream_ready_and_gate():
    c = _build()
    assert c["crypto_d1_research_only_dry_run_review_contract_active"] is True
    assert c["crypto_d1_research_only_dry_run_review_contract_state"] == (
        REVIEW_STATE_ACTIVE
    )
    assert c["dry_run_review_required"] == (
        REVIEW_CRYPTO_D1_DRY_RUN_REVIEW_REQUIRED
    )


def test_inactive_when_upstream_empty():
    c = build_crypto_d1_research_only_dry_run_review_contract({}, {})
    assert c["crypto_d1_research_only_dry_run_review_contract_active"] is False
    assert c["dry_run_review_verdict"] == REVIEW_VERDICT_AWAIT
    assert c["next_gate"] == (
        NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT
    )


def test_inactive_when_upstream_not_active():
    up = _active_preview_contract()
    up["crypto_d1_research_only_dry_run_preview_contract_active"] = False
    c = build_crypto_d1_research_only_dry_run_review_contract(
        up, _good_review_packet()
    )
    assert c["crypto_d1_research_only_dry_run_review_contract_active"] is False
    assert c["dry_run_review_verdict"] == REVIEW_VERDICT_AWAIT


def test_inactive_when_wrong_verdict():
    up = _active_preview_contract()
    up["dry_run_preview_verdict"] = "DRY_RUN_PREVIEW_NEEDS_MORE_INFO"
    c = build_crypto_d1_research_only_dry_run_review_contract(
        up, _good_review_packet()
    )
    assert c["crypto_d1_research_only_dry_run_review_contract_active"] is False
    assert c["dry_run_review_verdict"] == REVIEW_VERDICT_AWAIT


def test_inactive_when_wrong_gate():
    up = _active_preview_contract()
    up["next_gate"] = "SOMETHING_ELSE"
    c = build_crypto_d1_research_only_dry_run_review_contract(
        up, _good_review_packet()
    )
    assert c["crypto_d1_research_only_dry_run_review_contract_active"] is False
    assert c["dry_run_review_verdict"] == REVIEW_VERDICT_AWAIT


def test_inactive_when_upstream_garbage():
    for bad in (None, [], "x", 7, {"foo": "bar"}):
        c = build_crypto_d1_research_only_dry_run_review_contract(
            bad, _good_review_packet()
        )
        assert (
            c["crypto_d1_research_only_dry_run_review_contract_active"] is False
        )
        assert c["dry_run_review_verdict"] == REVIEW_VERDICT_AWAIT


def test_await_verdict_ignores_packet_shape():
    # Even a packet that would otherwise REJECT yields AWAIT when inactive.
    bad_packet = {**_good_review_packet(), "allow_data_fetch": True}
    c = build_crypto_d1_research_only_dry_run_review_contract({}, bad_packet)
    assert c["dry_run_review_verdict"] == REVIEW_VERDICT_AWAIT


# --- 5: READY path ---------------------------------------------------------

def test_ready_when_complete_and_safe():
    c = _build()
    assert c["dry_run_review_verdict"] == REVIEW_VERDICT_READY
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_READY_HUMAN_RUN_REQUIRED
    )


def test_evaluate_ready_direct():
    ev = evaluate_crypto_d1_research_only_dry_run_review(
        _good_review_packet(),
        {"preview_packet_id": _PREVIEW_PACKET_ID},
    )
    assert ev["verdict"] == REVIEW_VERDICT_READY


def test_ready_validation_valid():
    c = _build()
    assert c["validation"]["valid"] is True


# --- 6: NEEDS_MORE_INFO path -----------------------------------------------

def test_empty_packet_needs_more_info():
    ev = evaluate_crypto_d1_research_only_dry_run_review({}, {})
    assert ev["verdict"] == REVIEW_VERDICT_NEEDS_MORE_INFO
    assert ev["reasons"] == ("dry_run_review_packet_missing",)


def test_missing_each_text_field_needs_more_info():
    for key in REVIEW_REQUIRED_TEXT_FIELDS:
        pkt = _good_review_packet()
        del pkt[key]
        ev = evaluate_crypto_d1_research_only_dry_run_review(
            pkt, {"preview_packet_id": _PREVIEW_PACKET_ID}
        )
        assert ev["verdict"] == REVIEW_VERDICT_NEEDS_MORE_INFO, key
        assert f"{key}_required" in ev["reasons"], key


def test_missing_each_affirmation_needs_more_info():
    for flag in REVIEW_REQUIRED_AFFIRMATIONS:
        pkt = _good_review_packet()
        del pkt[flag]
        ev = evaluate_crypto_d1_research_only_dry_run_review(
            pkt, {"preview_packet_id": _PREVIEW_PACKET_ID}
        )
        assert ev["verdict"] == REVIEW_VERDICT_NEEDS_MORE_INFO, flag
        assert f"{flag}_must_be_affirmed_true" in ev["reasons"], flag


def test_build_needs_more_info_sets_fix_gate():
    pkt = _good_review_packet()
    del pkt["review_notes"]
    c = _build(_active_preview_contract(), pkt)
    assert c["dry_run_review_verdict"] == REVIEW_VERDICT_NEEDS_MORE_INFO
    assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_FIX_REQUIRED


# --- 7: REJECTED path ------------------------------------------------------

def test_reject_each_forbidden_allow_flag():
    for flag in REVIEW_FORBIDDEN_ALLOW_FLAGS:
        pkt = {**_good_review_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_review(
            pkt, {"preview_packet_id": _PREVIEW_PACKET_ID}
        )
        assert ev["verdict"] == REVIEW_VERDICT_REJECTED, flag
        assert f"forbidden_allow:{flag}" in ev["reasons"], flag


def test_reject_real_data_acquisition_allow_flag():
    pkt = {**_good_review_packet(), "allow_real_data_acquisition": True}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED


def test_reject_data_fetch_allow_flag():
    pkt = {**_good_review_packet(), "approves_data_fetch": True}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED


def test_reject_dataset_loading_allow_flag():
    pkt = {**_good_review_packet(), "allow_dataset_loading": True}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED


def test_reject_qa_baseline_backtest_simulation_allow_flags():
    for flag in (
        "allow_qa_run",
        "allow_baseline_run",
        "allow_backtest_run",
        "allow_simulation_run",
    ):
        pkt = {**_good_review_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
        assert ev["verdict"] == REVIEW_VERDICT_REJECTED, flag


def test_reject_trade_signal_allow_flag():
    pkt = {**_good_review_packet(), "approves_trade_signal": True}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED


def test_reject_paper_live_broker_order_account_api_flags():
    for flag in (
        "allow_paper_live",
        "allow_broker_exchange",
        "allow_order_capability",
        "allow_account_access",
        "allow_api_keys",
    ):
        pkt = {**_good_review_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
        assert ev["verdict"] == REVIEW_VERDICT_REJECTED, flag


def test_reject_automation_trigger_allow_flag():
    pkt = {**_good_review_packet(), "allow_automation_trigger": True}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED


def test_reject_runtime_registry_dashboard_write_flags():
    for flag in (
        "allow_runtime_write",
        "allow_registry_write",
        "allow_dashboard_write",
    ):
        pkt = {**_good_review_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
        assert ev["verdict"] == REVIEW_VERDICT_REJECTED, flag


def test_reject_dry_run_execution_allow_flag():
    pkt = {**_good_review_packet(), "executes_dry_run": True}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED


def test_reject_relaxed_each_affirmation():
    for flag in REVIEW_REQUIRED_AFFIRMATIONS:
        pkt = {**_good_review_packet(), flag: False}
        ev = evaluate_crypto_d1_research_only_dry_run_review(
            pkt, {"preview_packet_id": _PREVIEW_PACKET_ID}
        )
        assert ev["verdict"] == REVIEW_VERDICT_REJECTED, flag
        assert f"affirmation_relaxed:{flag}" in ev["reasons"], flag


def test_reject_disallowed_mode():
    pkt = {**_good_review_packet(), "review_mode": "live"}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED
    assert "disallowed_value:review_mode" in ev["reasons"]


def test_reject_disallowed_scope():
    pkt = {**_good_review_packet(), "review_scope": "full_execution"}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED
    assert "disallowed_value:review_scope" in ev["reasons"]


def test_reject_automated_reviewer():
    pkt = {**_good_review_packet(), "reviewer_name_or_id": "automation"}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED
    assert "automated_reviewer:reviewer_name_or_id" in ev["reasons"]


def test_reject_automated_reviewer_type_key():
    pkt = {**_good_review_packet(), "reviewer_type": "bot"}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED
    assert "automated_reviewer:reviewer_type" in ev["reasons"]


def test_reject_granted_authority():
    pkt = {**_good_review_packet(), "grants_capabilities": ["data_fetch"]}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED
    assert "grants_listed:grants_capabilities" in ev["reasons"]


def test_reject_upstream_id_mismatch():
    pkt = {**_good_review_packet(), "upstream_preview_id": "WRONG"}
    ev = evaluate_crypto_d1_research_only_dry_run_review(
        pkt, {"preview_packet_id": _PREVIEW_PACKET_ID}
    )
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED
    assert "mismatch:upstream_preview_id" in ev["reasons"]


def test_no_mismatch_when_ref_absent():
    pkt = {**_good_review_packet(), "upstream_preview_id": "ANYTHING"}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_READY


def test_build_rejected_sets_reject_gate():
    pkt = {**_good_review_packet(), "allow_data_fetch": True}
    c = _build(_active_preview_contract(), pkt)
    assert c["dry_run_review_verdict"] == REVIEW_VERDICT_REJECTED
    assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_REJECTED


def test_reject_takes_priority_over_missing():
    pkt = {**_good_review_packet(), "allow_data_fetch": True}
    del pkt["review_notes"]
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED


def test_reject_takes_priority_over_park():
    pkt = {**_good_review_packet(), "allow_data_fetch": True, "park": True}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_REJECTED


# --- 8: PARKED path --------------------------------------------------------

def test_park_via_flag():
    pkt = {**_good_review_packet(), "park": True}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_PARKED


def test_park_via_operator_decision():
    pkt = {**_good_review_packet(), "operator_decision": "deferred"}
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_PARKED


def test_build_parked_sets_park_gate():
    pkt = {**_good_review_packet(), "parked": True}
    c = _build(_active_preview_contract(), pkt)
    assert c["dry_run_review_verdict"] == REVIEW_VERDICT_PARKED
    assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_DRY_RUN_REVIEW_PARKED


def test_park_takes_priority_over_missing():
    pkt = {**_good_review_packet(), "park": True}
    del pkt["review_notes"]
    ev = evaluate_crypto_d1_research_only_dry_run_review(pkt, {})
    assert ev["verdict"] == REVIEW_VERDICT_PARKED


# --- 9: safety invariants --------------------------------------------------

def test_no_verdict_authorizes_or_executes():
    cases = [
        _good_review_packet(),                                  # READY
        {**_good_review_packet(), "allow_data_fetch": True},    # REJECTED
        {**_good_review_packet(), "park": True},                # PARKED
        {},                                                     # NEEDS_MORE
    ]
    for pkt in cases:
        c = _build(_active_preview_contract(), pkt)
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["human_approval_required"] is True
        for flag in _AUTH_FLAGS:
            assert c[flag] is False, flag
        assert all(v is False for v in c["safety_posture"].values())
    # Inactive too.
    c = build_crypto_d1_research_only_dry_run_review_contract({}, {})
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    for flag in _AUTH_FLAGS:
        assert c[flag] is False, flag
    assert all(v is False for v in c["safety_posture"].values())


def test_contract_mode_always_research_only():
    assert _build()["mode"] == "RESEARCH_ONLY"
    assert build_crypto_d1_research_only_dry_run_review_contract(
        {}, {}
    )["mode"] == "RESEARCH_ONLY"


def test_contract_stage_always_review_only():
    assert _build()["stage"] == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_ONLY"
    )
    assert build_crypto_d1_research_only_dry_run_review_contract(
        {}, {}
    )["stage"] == "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_REVIEW_ONLY"


def test_blocked_capabilities_present_and_nonempty():
    c = _build()
    assert len(c["review_blocked_capabilities"]) >= 1
    assert len(c["blocked_capabilities"]) >= 1
    assert tuple(c["remaining_real_world_capabilities_blocked"]) == (
        REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


def test_no_verdict_carries_real_capability_marker():
    for pkt in (
        _good_review_packet(),
        {},
        {**_good_review_packet(), "park": True},
    ):
        c = _build(_active_preview_contract(), pkt)
        for flag in REVIEW_FORBIDDEN_ALLOW_FLAGS:
            assert c.get(flag) in (None, False), flag


def test_no_verdict_unlocks_upstream_capability():
    # Building never flips any authorization flag on the echoed upstream
    # preview contract, and never adds new top-level allow_* keys.
    c = _build()
    for flag in _AUTH_FLAGS:
        assert c["crypto_d1_research_only_dry_run_preview_contract"][flag] is (
            False
        )


# --- 10: validation --------------------------------------------------------

def test_validate_public_matches_embedded():
    c = _build()
    v = validate_crypto_d1_research_only_dry_run_review_contract(c)
    assert v == c["validation"]
    assert v["valid"] is True


def test_validate_rejects_tampered_schema():
    c = _build()
    c["schema_version"] = "tampered"
    v = validate_crypto_d1_research_only_dry_run_review_contract(c)
    assert v["valid"] is False
    assert v["schema_version_ok"] is False


def test_validate_rejects_missing_field():
    c = _build()
    del c["safety_posture"]
    v = validate_crypto_d1_research_only_dry_run_review_contract(c)
    assert v["valid"] is False
    assert "safety_posture" in v["missing_required_fields"]


def test_validate_rejects_executes_true():
    c = _build()
    c["executes"] = True
    v = validate_crypto_d1_research_only_dry_run_review_contract(c)
    assert v["valid"] is False


def test_validate_rejects_tampered_posture():
    c = _build()
    c["safety_posture"]["prohibited_data_fetch"] = True
    v = validate_crypto_d1_research_only_dry_run_review_contract(c)
    assert v["valid"] is False
    assert v["safety_all_false"] is False


def test_validate_handles_garbage():
    for bad in (None, {}, [], "x", 7):
        v = validate_crypto_d1_research_only_dry_run_review_contract(bad)
        assert v["valid"] is False


# --- 11: determinism + mutation isolation ----------------------------------

def test_build_is_deterministic():
    a = _build()
    b = _build()
    a.pop("crypto_d1_research_only_dry_run_preview_contract", None)
    b.pop("crypto_d1_research_only_dry_run_preview_contract", None)
    assert a == b


def test_evaluate_is_deterministic():
    p = _good_review_packet()
    assert (
        evaluate_crypto_d1_research_only_dry_run_review(p, {})
        == evaluate_crypto_d1_research_only_dry_run_review(p, {})
    )


def test_safety_posture_copy_is_isolated():
    c = _build()
    c["safety_posture"]["prohibited_data_fetch"] = True
    assert all(v is False for v in REVIEW_SAFETY_POSTURE.values())
    assert all(v is False for v in _build()["safety_posture"].values())


def test_input_packet_not_mutated():
    p = _good_review_packet()
    snapshot = dict(p)
    _build(_active_preview_contract(), p)
    assert p == snapshot


# --- 12: markdown ----------------------------------------------------------

def test_markdown_nonempty_and_titled():
    md = render_crypto_d1_research_only_dry_run_review_contract_markdown(
        _build()
    )
    assert isinstance(md, str)
    assert md.startswith(
        "# Strategy Factory Crypto-D1 Research-Only Dry-Run Review Contract"
    )
    assert "RESEARCH_ONLY" in md
    assert "Executes: False" in md


def test_markdown_handles_minimal_contract():
    md = render_crypto_d1_research_only_dry_run_review_contract_markdown({})
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
        'review_contract.py"' in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_research_only_dry_run_review_'
        'contract.py"' in src
    )

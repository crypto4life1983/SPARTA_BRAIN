"""Tests for the Strategy Factory Crypto-D1 Research-Only Dry-Run Final
Decision Contract (Bundle 53).

Bundle 53 is a PURE, stdlib-only, read-only *paper final-decision contract*
builder. It consumes a Bundle 52 crypto-d1 research-only dry-run DECISION REVIEW
contract and, only when that decision-review contract is active + carries the
Bundle 52 READY verdict (DRY_RUN_DECISION_REVIEW_READY) + the Bundle 52 ready
next-gate
(CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_REVIEW_READY_SEPARATE_HUMAN_NEXT_CONTRACT_REQUIRED),
evaluates a proposed dry-run FINAL DECISION packet and returns a deterministic
verdict describing whether a human recorded, on paper, a FINAL decision that the
research-only dry-run sequence is safe to archive (or carry to a next paper-only
boundary) -- or whether the lane should park, need more info, or be rejected. It
performs NO dry run, decides on paper only, acquires nothing, fetches nothing,
inspects nothing, loads no dataset, runs no QA/baseline/backtest/simulation,
produces no trade signal, validates no market data, reaches no
broker/exchange/order/account/API surface, triggers no automation, and writes
nothing. A READY-for-archive verdict unlocks NOTHING real and still requires a
separate, later, human step to act on the archive or boundary.

Coverage:
- schema / label / status / state constants stable
- verdict + gate constants stable; ordering
- activation strictly gated on Bundle 52 active + READY + ready-gate
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
- a real Bundle 49->50->51->52 chain activates Bundle 53 end-to-end
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_final_decision_contract import (  # noqa: E501
    FINAL_DECISION_SCHEMA_VERSION,
    DEFAULT_FINAL_DECISION_LABEL,
    FINAL_DECISION_STATUS,
    FINAL_DECISION_SAFETY_POSTURE,
    FINAL_DECISION_STATE_ACTIVE,
    FINAL_DECISION_STATE_BLOCKED,
    FINAL_DECISION_VERDICT_READY_FOR_ARCHIVE,
    FINAL_DECISION_VERDICT_NEEDS_MORE_INFO,
    FINAL_DECISION_VERDICT_REJECTED,
    FINAL_DECISION_VERDICT_PARKED,
    FINAL_DECISION_VERDICT_AWAIT,
    ALLOWED_FINAL_DECISION_VERDICTS,
    UPSTREAM_REQUIRED_DECISION_REVIEW_VERDICT,
    UPSTREAM_REQUIRED_DECISION_REVIEW_NEXT_GATE,
    DRY_RUN_FINAL_DECISION_NEXT_REQUIRED_ACTION,
    DRY_RUN_FINAL_DECISION_CURRENT_STAGE,
    DECISION_CRYPTO_D1_DRY_RUN_FINAL_DECISION_REQUIRED,
    NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_READY_RESEARCH_ARCHIVE,  # noqa: E501
    NEXT_GATE_CRYPTO_D1_DRY_RUN_FINAL_DECISION_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_FINAL_DECISION_PARKED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_FINAL_DECISION_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_REVIEW_CONTRACT,
    REQUIRED_FINAL_DECISION_FIELDS,
    FINAL_DECISION_REQUIRED_TEXT_FIELDS,
    FINAL_DECISION_REQUIRED_AFFIRMATIONS,
    FINAL_DECISION_FORBIDDEN_ALLOW_FLAGS,
    ALLOWED_FINAL_DECISION_MODES,
    ALLOWED_FINAL_DECISION_SCOPES,
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_research_only_dry_run_final_decision,
    build_crypto_d1_research_only_dry_run_final_decision_contract,
    validate_crypto_d1_research_only_dry_run_final_decision_contract,
    render_crypto_d1_research_only_dry_run_final_decision_contract_markdown,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_research_only_dry_run_final_decision_contract.py"  # noqa: E501
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

_DECISION_REVIEW_PACKET_ID = "DRP-1"


# --- fixtures --------------------------------------------------------------

def _synthetic_decision_review_contract():
    """A Bundle-52-shaped dict that activates the Bundle 53 build."""
    return {
        "crypto_d1_research_only_dry_run_decision_review_contract_active": True,
        "dry_run_decision_review_verdict": (
            UPSTREAM_REQUIRED_DECISION_REVIEW_VERDICT
        ),
        "next_gate": UPSTREAM_REQUIRED_DECISION_REVIEW_NEXT_GATE,
        "evaluated_decision_review_packet": {
            "decision_review_packet_id": _DECISION_REVIEW_PACKET_ID,
        },
        "idea_id": "IDEA-1",
        "title": "Crypto-D1 lane",
        "asset_lane": "crypto",
        "timeframe_lane": "1d",
    }


def _good_final_decision_packet():
    """A complete, safe, research-only dry-run final-decision packet."""
    p = {
        "final_decision_packet_id": "FDP-1",
        "upstream_decision_review_id": _DECISION_REVIEW_PACKET_ID,
        "decision_review_contract_version": "decision_review.v1",
        "final_decision_scope": "dry_run_final_decision_only",
        "final_decision_mode": "research_only",
        "reviewed_decision_review_summary": (
            "research-only dry-run decision review confirmed"
        ),
        "final_research_outcome": "safe research archive of the dry-run lane",
        "final_decision_rationale": "the safe outcome is a research archive",
        "final_operator_name_or_id": "Mahmoud (human operator)",
        "archive_or_next_boundary": "research archive; separate later human step",
        "final_notes": "decided on paper; no data work, no execution observed",
    }
    for flag in FINAL_DECISION_REQUIRED_AFFIRMATIONS:
        p[flag] = True
    return p


def _build(upstream=None, packet=None):
    return build_crypto_d1_research_only_dry_run_final_decision_contract(
        upstream
        if upstream is not None
        else _synthetic_decision_review_contract(),
        packet if packet is not None else _good_final_decision_packet(),
    )


# --- 1: schema / label / status / state constants --------------------------

def test_schema_version_stable():
    assert FINAL_DECISION_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_research_only_dry_run_final_decision_"
        "contract.v1"
    )


def test_label_and_status_stable():
    assert DEFAULT_FINAL_DECISION_LABEL == (
        "Strategy Factory Crypto-D1 Research-Only Dry-Run Final Decision "
        "Contract"
    )
    assert FINAL_DECISION_STATUS == (
        "READ_ONLY_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_CONTRACT"
    )


def test_state_constants_stable():
    assert FINAL_DECISION_STATE_ACTIVE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_CONTRACT_ACTIVE"
    )
    assert FINAL_DECISION_STATE_BLOCKED == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_CONTRACT_BLOCKED"
    )


# --- 2: verdict + gate constants -------------------------------------------

def test_verdict_constants_stable():
    assert FINAL_DECISION_VERDICT_READY_FOR_ARCHIVE == (
        "DRY_RUN_FINAL_DECISION_READY_FOR_RESEARCH_ARCHIVE"
    )
    assert FINAL_DECISION_VERDICT_NEEDS_MORE_INFO == (
        "DRY_RUN_FINAL_DECISION_NEEDS_MORE_INFO"
    )
    assert FINAL_DECISION_VERDICT_REJECTED == "DRY_RUN_FINAL_DECISION_REJECTED"
    assert FINAL_DECISION_VERDICT_PARKED == "DRY_RUN_FINAL_DECISION_PARKED"
    assert FINAL_DECISION_VERDICT_AWAIT == (
        "AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_REVIEW_CONTRACT"
    )


def test_allowed_verdicts_order():
    assert ALLOWED_FINAL_DECISION_VERDICTS == (
        FINAL_DECISION_VERDICT_READY_FOR_ARCHIVE,
        FINAL_DECISION_VERDICT_NEEDS_MORE_INFO,
        FINAL_DECISION_VERDICT_REJECTED,
        FINAL_DECISION_VERDICT_PARKED,
        FINAL_DECISION_VERDICT_AWAIT,
    )


def test_upstream_required_signal_constants():
    assert UPSTREAM_REQUIRED_DECISION_REVIEW_VERDICT == (
        "DRY_RUN_DECISION_REVIEW_READY"
    )
    assert UPSTREAM_REQUIRED_DECISION_REVIEW_NEXT_GATE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_REVIEW_READY_SEPARATE_HUMAN_"
        "NEXT_CONTRACT_REQUIRED"
    )


def test_next_gate_constants_stable():
    assert NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_READY_RESEARCH_ARCHIVE == (  # noqa: E501
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_READY_FOR_RESEARCH_"
        "ARCHIVE_SEPARATE_HUMAN_NEXT_STEP_REQUIRED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_FINAL_DECISION_FIX_REQUIRED == (
        "CRYPTO_D1_DRY_RUN_FINAL_DECISION_FIX_REQUIRED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_FINAL_DECISION_PARKED == (
        "CRYPTO_D1_DRY_RUN_FINAL_DECISION_PARKED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_FINAL_DECISION_REJECTED == (
        "CRYPTO_D1_DRY_RUN_FINAL_DECISION_REJECTED"
    )
    assert NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_REVIEW_CONTRACT == (  # noqa: E501
        "AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_REVIEW_CONTRACT"
    )


def test_next_required_action_and_stage_are_strings():
    assert isinstance(DRY_RUN_FINAL_DECISION_NEXT_REQUIRED_ACTION, str)
    assert isinstance(DRY_RUN_FINAL_DECISION_CURRENT_STAGE, str)
    assert DECISION_CRYPTO_D1_DRY_RUN_FINAL_DECISION_REQUIRED == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_REQUIRED"
    )


def test_next_required_action_is_what_this_bundle_fulfills():
    assert DRY_RUN_FINAL_DECISION_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_CONTRACT"
    )
    assert DRY_RUN_FINAL_DECISION_CURRENT_STAGE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_CONTRACT_REQUIRED"
    )


# --- 3: required-field collections -----------------------------------------

def test_required_text_fields_exact():
    assert FINAL_DECISION_REQUIRED_TEXT_FIELDS == (
        "final_decision_packet_id",
        "upstream_decision_review_id",
        "decision_review_contract_version",
        "final_decision_scope",
        "final_decision_mode",
        "reviewed_decision_review_summary",
        "final_research_outcome",
        "final_decision_rationale",
        "final_operator_name_or_id",
        "archive_or_next_boundary",
        "final_notes",
    )


def test_required_affirmations_complete():
    for flag in (
        "explicit_human_final_decision",
        "research_only_acknowledgement",
        "no_execution_acknowledgement",
        "final_no_real_data_acquisition",
        "final_no_data_fetch",
        "final_no_data_inspection",
        "final_no_dataset_loading",
        "final_no_qa_run",
        "final_no_baseline_run",
        "final_no_backtest_run",
        "final_no_simulation_run",
        "final_no_trade_signal",
        "final_no_paper_live",
        "final_no_broker_exchange",
        "final_no_order_capability",
        "final_no_account_access",
        "final_no_api_keys",
        "final_no_automation_trigger",
        "final_no_runtime_write",
        "final_no_registry_write",
        "final_no_dashboard_write",
    ):
        assert flag in FINAL_DECISION_REQUIRED_AFFIRMATIONS, flag
    assert len(FINAL_DECISION_REQUIRED_AFFIRMATIONS) == 21


def test_required_final_decision_fields_is_union():
    assert REQUIRED_FINAL_DECISION_FIELDS == (
        FINAL_DECISION_REQUIRED_TEXT_FIELDS
        + FINAL_DECISION_REQUIRED_AFFIRMATIONS
    )
    assert len(REQUIRED_FINAL_DECISION_FIELDS) == 32


def test_allowed_modes_and_scopes():
    assert ALLOWED_FINAL_DECISION_MODES == ("research_only", "research-only")
    assert "dry_run_final_decision_only" in ALLOWED_FINAL_DECISION_SCOPES
    assert "final_decision" in ALLOWED_FINAL_DECISION_SCOPES


def test_safety_posture_all_false():
    assert len(FINAL_DECISION_SAFETY_POSTURE) > 0
    assert all(v is False for v in FINAL_DECISION_SAFETY_POSTURE.values())


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
        "final_approves_execution",
        "final_allows_real_data",
        "final_unlocks_qa",
        "final_approves_real_acquisition",
        "archive_with_real_data",
        "proceed_to_live_after_archive",
    ):
        assert flag in FINAL_DECISION_FORBIDDEN_ALLOW_FLAGS, flag


# --- 4: activation gating --------------------------------------------------

def test_active_when_upstream_ready_and_gate():
    c = _build()
    assert c[
        "crypto_d1_research_only_dry_run_final_decision_contract_active"
    ] is True
    assert c[
        "crypto_d1_research_only_dry_run_final_decision_contract_state"
    ] == FINAL_DECISION_STATE_ACTIVE
    assert c["dry_run_final_decision_required"] == (
        DECISION_CRYPTO_D1_DRY_RUN_FINAL_DECISION_REQUIRED
    )


def test_inactive_when_upstream_empty():
    c = build_crypto_d1_research_only_dry_run_final_decision_contract({}, {})
    assert c[
        "crypto_d1_research_only_dry_run_final_decision_contract_active"
    ] is False
    assert c["dry_run_final_decision_verdict"] == FINAL_DECISION_VERDICT_AWAIT
    assert c["next_gate"] == (
        NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_DECISION_REVIEW_CONTRACT
    )


def test_inactive_when_upstream_not_active():
    up = _synthetic_decision_review_contract()
    up["crypto_d1_research_only_dry_run_decision_review_contract_active"] = False
    c = _build(up, _good_final_decision_packet())
    assert c[
        "crypto_d1_research_only_dry_run_final_decision_contract_active"
    ] is False
    assert c["dry_run_final_decision_verdict"] == FINAL_DECISION_VERDICT_AWAIT


def test_inactive_when_wrong_verdict():
    up = _synthetic_decision_review_contract()
    up["dry_run_decision_review_verdict"] = "DRY_RUN_DECISION_REVIEW_NEEDS_MORE_INFO"  # noqa: E501
    c = _build(up, _good_final_decision_packet())
    assert c[
        "crypto_d1_research_only_dry_run_final_decision_contract_active"
    ] is False
    assert c["dry_run_final_decision_verdict"] == FINAL_DECISION_VERDICT_AWAIT


def test_inactive_when_wrong_gate():
    up = _synthetic_decision_review_contract()
    up["next_gate"] = "SOMETHING_ELSE"
    c = _build(up, _good_final_decision_packet())
    assert c[
        "crypto_d1_research_only_dry_run_final_decision_contract_active"
    ] is False
    assert c["dry_run_final_decision_verdict"] == FINAL_DECISION_VERDICT_AWAIT


def test_inactive_when_upstream_garbage():
    for bad in (None, [], "x", 7, {"foo": "bar"}):
        c = build_crypto_d1_research_only_dry_run_final_decision_contract(
            bad, _good_final_decision_packet()
        )
        assert c[
            "crypto_d1_research_only_dry_run_final_decision_contract_active"
        ] is False
        assert c["dry_run_final_decision_verdict"] == (
            FINAL_DECISION_VERDICT_AWAIT
        )


def test_await_verdict_ignores_packet_shape():
    # Even a packet that would otherwise REJECT yields AWAIT when inactive.
    bad_packet = {**_good_final_decision_packet(), "allow_data_fetch": True}
    c = build_crypto_d1_research_only_dry_run_final_decision_contract(
        {}, bad_packet
    )
    assert c["dry_run_final_decision_verdict"] == FINAL_DECISION_VERDICT_AWAIT


# --- 5: READY path ---------------------------------------------------------

def test_ready_when_complete_and_safe():
    c = _build()
    assert c["dry_run_final_decision_verdict"] == (
        FINAL_DECISION_VERDICT_READY_FOR_ARCHIVE
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_READY_RESEARCH_ARCHIVE  # noqa: E501
    )


def test_evaluate_ready_direct():
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(
        _good_final_decision_packet(),
        {"decision_review_packet_id": _DECISION_REVIEW_PACKET_ID},
    )
    assert ev["verdict"] == FINAL_DECISION_VERDICT_READY_FOR_ARCHIVE


def test_ready_validation_valid():
    c = _build()
    assert c["validation"]["valid"] is True


def test_ready_research_dash_only_mode_accepted():
    pkt = {**_good_final_decision_packet(), "final_decision_mode": "research-only"}  # noqa: E501
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_READY_FOR_ARCHIVE


# --- 6: NEEDS_MORE_INFO path -----------------------------------------------

def test_empty_packet_needs_more_info():
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision({}, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_NEEDS_MORE_INFO
    assert ev["reasons"] == ("dry_run_final_decision_packet_missing",)


def test_missing_each_text_field_needs_more_info():
    for key in FINAL_DECISION_REQUIRED_TEXT_FIELDS:
        pkt = _good_final_decision_packet()
        del pkt[key]
        ev = evaluate_crypto_d1_research_only_dry_run_final_decision(
            pkt, {"decision_review_packet_id": _DECISION_REVIEW_PACKET_ID}
        )
        assert ev["verdict"] == FINAL_DECISION_VERDICT_NEEDS_MORE_INFO, key
        assert f"{key}_required" in ev["reasons"], key


def test_missing_each_affirmation_needs_more_info():
    for flag in FINAL_DECISION_REQUIRED_AFFIRMATIONS:
        pkt = _good_final_decision_packet()
        del pkt[flag]
        ev = evaluate_crypto_d1_research_only_dry_run_final_decision(
            pkt, {"decision_review_packet_id": _DECISION_REVIEW_PACKET_ID}
        )
        assert ev["verdict"] == FINAL_DECISION_VERDICT_NEEDS_MORE_INFO, flag
        assert f"{flag}_must_be_affirmed_true" in ev["reasons"], flag


def test_build_needs_more_info_sets_fix_gate():
    pkt = _good_final_decision_packet()
    del pkt["final_notes"]
    c = _build(_synthetic_decision_review_contract(), pkt)
    assert c["dry_run_final_decision_verdict"] == (
        FINAL_DECISION_VERDICT_NEEDS_MORE_INFO
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_DRY_RUN_FINAL_DECISION_FIX_REQUIRED
    )


# --- 7: REJECTED path ------------------------------------------------------

def test_reject_each_forbidden_allow_flag():
    for flag in FINAL_DECISION_FORBIDDEN_ALLOW_FLAGS:
        pkt = {**_good_final_decision_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_final_decision(
            pkt, {"decision_review_packet_id": _DECISION_REVIEW_PACKET_ID}
        )
        assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED, flag
        assert f"forbidden_allow:{flag}" in ev["reasons"], flag


def test_reject_real_data_acquisition_allow_flag():
    pkt = {**_good_final_decision_packet(), "allow_real_data_acquisition": True}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


def test_reject_data_fetch_allow_flag():
    pkt = {**_good_final_decision_packet(), "approves_data_fetch": True}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


def test_reject_data_inspection_allow_flag():
    pkt = {**_good_final_decision_packet(), "allow_data_inspection": True}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


def test_reject_dataset_loading_allow_flag():
    pkt = {**_good_final_decision_packet(), "allow_dataset_loading": True}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


def test_reject_qa_baseline_backtest_simulation_allow_flags():
    for flag in (
        "allow_qa_run",
        "allow_baseline_run",
        "allow_backtest_run",
        "allow_simulation_run",
    ):
        pkt = {**_good_final_decision_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
        assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED, flag


def test_reject_trade_signal_allow_flag():
    pkt = {**_good_final_decision_packet(), "approves_trade_signal": True}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


def test_reject_market_data_validation_allow_flag():
    pkt = {**_good_final_decision_packet(), "validates_market_data": True}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


def test_reject_paper_live_broker_order_account_api_flags():
    for flag in (
        "allow_paper_live",
        "allow_broker_exchange",
        "allow_order_capability",
        "allow_account_access",
        "allow_api_keys",
    ):
        pkt = {**_good_final_decision_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
        assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED, flag


def test_reject_automation_trigger_allow_flag():
    pkt = {**_good_final_decision_packet(), "allow_automation_trigger": True}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


def test_reject_runtime_registry_dashboard_write_flags():
    for flag in (
        "allow_runtime_write",
        "allow_registry_write",
        "allow_dashboard_write",
    ):
        pkt = {**_good_final_decision_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
        assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED, flag


def test_reject_dry_run_execution_allow_flag():
    pkt = {**_good_final_decision_packet(), "executes_dry_run": True}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


def test_reject_final_decision_specific_allow_flags():
    for flag in (
        "final_approves_execution",
        "final_allows_real_data",
        "final_unlocks_qa",
        "final_approves_real_acquisition",
        "final_decision_approves_execution",
        "final_decision_allows_real_data",
        "final_decision_unlocks_qa",
        "archive_with_real_data",
        "proceed_to_live_after_archive",
    ):
        pkt = {**_good_final_decision_packet(), flag: True}
        ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
        assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED, flag


def test_reject_proceed_to_real_contract_flag():
    pkt = {**_good_final_decision_packet(), "proceed_to_real_contract": True}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


def test_reject_next_real_contract_flag():
    pkt = {**_good_final_decision_packet(), "allow_next_real_contract": True}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


def test_reject_relaxed_each_affirmation():
    for flag in FINAL_DECISION_REQUIRED_AFFIRMATIONS:
        pkt = {**_good_final_decision_packet(), flag: False}
        ev = evaluate_crypto_d1_research_only_dry_run_final_decision(
            pkt, {"decision_review_packet_id": _DECISION_REVIEW_PACKET_ID}
        )
        assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED, flag
        assert f"affirmation_relaxed:{flag}" in ev["reasons"], flag


def test_reject_disallowed_final_decision_mode():
    pkt = {**_good_final_decision_packet(), "final_decision_mode": "live"}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED
    assert "disallowed_value:final_decision_mode" in ev["reasons"]


def test_reject_disallowed_final_decision_scope():
    pkt = {**_good_final_decision_packet(), "final_decision_scope": "full_execution"}  # noqa: E501
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED
    assert "disallowed_value:final_decision_scope" in ev["reasons"]


def test_reject_automated_decider_name():
    pkt = {**_good_final_decision_packet(), "final_operator_name_or_id": "automation"}  # noqa: E501
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED
    assert "automated_decider:final_operator_name_or_id" in ev["reasons"]


def test_reject_automated_decider_type_key():
    pkt = {**_good_final_decision_packet(), "decision_author_type": "bot"}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED
    assert "automated_decider:decision_author_type" in ev["reasons"]


def test_reject_granted_authority():
    pkt = {
        **_good_final_decision_packet(),
        "grants_capabilities": ["data_fetch"],
    }
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED
    assert "grants_listed:grants_capabilities" in ev["reasons"]


def test_reject_upstream_id_mismatch():
    pkt = {**_good_final_decision_packet(), "upstream_decision_review_id": "WRONG"}  # noqa: E501
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(
        pkt, {"decision_review_packet_id": _DECISION_REVIEW_PACKET_ID}
    )
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED
    assert "mismatch:upstream_decision_review_id" in ev["reasons"]


def test_no_mismatch_when_ref_absent():
    pkt = {**_good_final_decision_packet(), "upstream_decision_review_id": "ANYTHING"}  # noqa: E501
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_READY_FOR_ARCHIVE


def test_build_rejected_sets_reject_gate():
    pkt = {**_good_final_decision_packet(), "allow_data_fetch": True}
    c = _build(_synthetic_decision_review_contract(), pkt)
    assert c["dry_run_final_decision_verdict"] == (
        FINAL_DECISION_VERDICT_REJECTED
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_DRY_RUN_FINAL_DECISION_REJECTED
    )


def test_reject_takes_priority_over_missing():
    pkt = {**_good_final_decision_packet(), "allow_data_fetch": True}
    del pkt["final_notes"]
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


def test_reject_takes_priority_over_park():
    pkt = {
        **_good_final_decision_packet(),
        "allow_data_fetch": True,
        "park": True,
    }
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_REJECTED


# --- 8: PARKED path --------------------------------------------------------

def test_park_via_flag():
    pkt = {**_good_final_decision_packet(), "park": True}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_PARKED


def test_park_via_operator_decision():
    pkt = {**_good_final_decision_packet(), "operator_decision": "deferred"}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_PARKED


def test_park_via_final_decision_value():
    pkt = {**_good_final_decision_packet(), "final_decision": "parked"}
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_PARKED


def test_build_parked_sets_park_gate():
    pkt = {**_good_final_decision_packet(), "parked": True}
    c = _build(_synthetic_decision_review_contract(), pkt)
    assert c["dry_run_final_decision_verdict"] == FINAL_DECISION_VERDICT_PARKED
    assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_DRY_RUN_FINAL_DECISION_PARKED


def test_park_takes_priority_over_missing():
    pkt = {**_good_final_decision_packet(), "park": True}
    del pkt["final_notes"]
    ev = evaluate_crypto_d1_research_only_dry_run_final_decision(pkt, {})
    assert ev["verdict"] == FINAL_DECISION_VERDICT_PARKED


# --- 9: safety invariants --------------------------------------------------

def test_no_verdict_authorizes_or_executes():
    cases = [
        _good_final_decision_packet(),                                # READY
        {**_good_final_decision_packet(), "allow_data_fetch": True},  # REJECT
        {**_good_final_decision_packet(), "park": True},              # PARKED
        {},                                                           # MORE
    ]
    for pkt in cases:
        c = _build(_synthetic_decision_review_contract(), pkt)
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["human_approval_required"] is True
        for flag in _AUTH_FLAGS:
            assert c[flag] is False, flag
        assert all(v is False for v in c["safety_posture"].values())
    # Inactive too.
    c = build_crypto_d1_research_only_dry_run_final_decision_contract({}, {})
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    for flag in _AUTH_FLAGS:
        assert c[flag] is False, flag
    assert all(v is False for v in c["safety_posture"].values())


def test_contract_mode_always_research_only():
    assert _build()["mode"] == "RESEARCH_ONLY"
    assert build_crypto_d1_research_only_dry_run_final_decision_contract(
        {}, {}
    )["mode"] == "RESEARCH_ONLY"


def test_contract_stage_always_final_decision_only():
    assert _build()["stage"] == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_ONLY"
    )
    assert build_crypto_d1_research_only_dry_run_final_decision_contract(
        {}, {}
    )["stage"] == "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_ONLY"


def test_blocked_capabilities_present_and_nonempty():
    c = _build()
    assert len(c["final_decision_blocked_capabilities"]) >= 1
    assert len(c["blocked_capabilities"]) >= 1
    assert tuple(c["remaining_real_world_capabilities_blocked"]) == (
        REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


def test_no_verdict_carries_real_capability_marker():
    for pkt in (
        _good_final_decision_packet(),
        {},
        {**_good_final_decision_packet(), "park": True},
    ):
        c = _build(_synthetic_decision_review_contract(), pkt)
        for flag in FINAL_DECISION_FORBIDDEN_ALLOW_FLAGS:
            assert c.get(flag) in (None, False), flag


def test_no_verdict_unlocks_upstream_capability():
    # Building never flips any authorization flag on the echoed upstream
    # decision-review contract.
    up = _synthetic_decision_review_contract()
    up["approved_for_research"] = False
    c = _build(up, _good_final_decision_packet())
    echoed = c["crypto_d1_research_only_dry_run_decision_review_contract"]
    assert echoed.get("approved_for_research") is False


# --- 10: validation --------------------------------------------------------

def test_validate_public_matches_embedded():
    c = _build()
    v = validate_crypto_d1_research_only_dry_run_final_decision_contract(c)
    assert v == c["validation"]
    assert v["valid"] is True


def test_validate_rejects_tampered_schema():
    c = _build()
    c["schema_version"] = "tampered"
    v = validate_crypto_d1_research_only_dry_run_final_decision_contract(c)
    assert v["valid"] is False
    assert v["schema_version_ok"] is False


def test_validate_rejects_missing_field():
    c = _build()
    del c["safety_posture"]
    v = validate_crypto_d1_research_only_dry_run_final_decision_contract(c)
    assert v["valid"] is False
    assert "safety_posture" in v["missing_required_fields"]


def test_validate_rejects_executes_true():
    c = _build()
    c["executes"] = True
    v = validate_crypto_d1_research_only_dry_run_final_decision_contract(c)
    assert v["valid"] is False


def test_validate_rejects_tampered_posture():
    c = _build()
    c["safety_posture"]["live_execution_enabled"] = True
    v = validate_crypto_d1_research_only_dry_run_final_decision_contract(c)
    assert v["valid"] is False
    assert v["safety_all_false"] is False


def test_validate_handles_garbage():
    for bad in (None, {}, [], "x", 7):
        v = validate_crypto_d1_research_only_dry_run_final_decision_contract(
            bad
        )
        assert v["valid"] is False


# --- 11: determinism + mutation isolation ----------------------------------

def test_build_is_deterministic():
    a = _build()
    b = _build()
    a.pop("crypto_d1_research_only_dry_run_decision_review_contract", None)
    b.pop("crypto_d1_research_only_dry_run_decision_review_contract", None)
    assert a == b


def test_evaluate_is_deterministic():
    p = _good_final_decision_packet()
    assert (
        evaluate_crypto_d1_research_only_dry_run_final_decision(p, {})
        == evaluate_crypto_d1_research_only_dry_run_final_decision(p, {})
    )


def test_safety_posture_copy_is_isolated():
    c = _build()
    c["safety_posture"]["live_execution_enabled"] = True
    assert all(v is False for v in FINAL_DECISION_SAFETY_POSTURE.values())
    assert all(v is False for v in _build()["safety_posture"].values())


def test_input_packet_not_mutated():
    p = _good_final_decision_packet()
    snapshot = dict(p)
    _build(_synthetic_decision_review_contract(), p)
    assert p == snapshot


# --- 12: markdown ----------------------------------------------------------

def test_markdown_nonempty_and_titled():
    md = render_crypto_d1_research_only_dry_run_final_decision_contract_markdown(  # noqa: E501
        _build()
    )
    assert isinstance(md, str)
    assert md.startswith(
        "# Strategy Factory Crypto-D1 Research-Only Dry-Run Final Decision "
        "Contract"
    )
    assert "RESEARCH_ONLY" in md
    assert "Executes: False" in md


def test_markdown_handles_minimal_contract():
    md = render_crypto_d1_research_only_dry_run_final_decision_contract_markdown(  # noqa: E501
        {}
    )
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


def test_does_not_import_mission_flow_registry():
    """Bundle 53 must not import the registry (the registry imports it lazily;
    importing back would create a circular import)."""
    src = _MODPATH.read_text(encoding="utf-8")
    assert "strategy_factory_mission_flow_bundle_registry" not in src
    assert "strategy_factory_mission_flow_status" not in src


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
        'final_decision_contract.py"' in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_research_only_dry_run_'
        'final_decision_contract.py"' in src
    )


# --- 16: real upstream chain -----------------------------------------------

def test_real_bundle_52_chain_activates_bundle_53():
    """Build a REAL Bundle 49->50->51->52 contract and confirm it activates
    Bundle 53 end-to-end (no synthetic upstream)."""
    from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_preview_contract import (  # noqa: E501
        PREVIEW_REQUIRED_PROHIBITIONS,
        PREVIEW_REQUIRED_AFFIRMATIONS,
        UPSTREAM_REQUIRED_NEXT_STEP_VERDICT,
        UPSTREAM_REQUIRED_NEXT_STEP_NEXT_GATE,
        build_crypto_d1_research_only_dry_run_preview_contract,
    )
    from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_review_contract import (  # noqa: E501
        REVIEW_REQUIRED_AFFIRMATIONS,
        build_crypto_d1_research_only_dry_run_review_contract,
    )
    from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_decision_contract import (  # noqa: E501
        DECISION_REQUIRED_AFFIRMATIONS,
        build_crypto_d1_research_only_dry_run_decision_contract,
    )
    from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_decision_review_contract import (  # noqa: E501
        DECISION_REVIEW_REQUIRED_AFFIRMATIONS,
        DECISION_REVIEW_VERDICT_READY,
        build_crypto_d1_research_only_dry_run_decision_review_contract,
    )

    next_step = {
        "crypto_d1_post_boundary_next_step_contract_active": True,
        "next_step_verdict": UPSTREAM_REQUIRED_NEXT_STEP_VERDICT,
        "next_gate": UPSTREAM_REQUIRED_NEXT_STEP_NEXT_GATE,
        "evaluated_next_step_packet": {"decision_packet_id": "B48-NS-1"},
        "idea_id": "IDEA-1",
        "title": "Crypto-D1 lane",
        "asset_lane": "crypto",
        "timeframe_lane": "1d",
    }
    preview_packet = {
        "preview_packet_id": "PP-1",
        "upstream_next_step_id": "B48-NS-1",
        "proposed_preview_scope": "dry_run_preview_only",
        "proposed_preview_mode": "research_only",
        "preview_inputs_description": "mock inputs and static metadata only",
        "preview_outputs_description": "paper preview markdown only",
        "next_step_boundary": "separate later human-run step required",
    }
    for flag in PREVIEW_REQUIRED_PROHIBITIONS + PREVIEW_REQUIRED_AFFIRMATIONS:
        preview_packet[flag] = True
    preview = build_crypto_d1_research_only_dry_run_preview_contract(
        next_step, preview_packet
    )

    review_packet = {
        "review_packet_id": "RP-1",
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
        review_packet[flag] = True
    review = build_crypto_d1_research_only_dry_run_review_contract(
        preview, review_packet
    )

    decision_packet = {
        "decision_packet_id": "DP-1",
        "upstream_review_id": "RP-1",
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
        decision_packet[flag] = True
    decision = build_crypto_d1_research_only_dry_run_decision_contract(
        review, decision_packet
    )

    decision_review_packet = {
        "decision_review_packet_id": "DRP-1",
        "upstream_decision_id": "DP-1",
        "decision_contract_version": "decision.v1",
        "review_scope": "dry_run_decision_review_only",
        "review_mode": "research_only",
        "reviewed_decision_summary": "research-only dry-run decision reviewed",
        "reviewed_proposed_next_contract": "another research-only paper "
        "contract",
        "reviewed_decision_rationale": "the proposed next step is paper-only",
        "reviewer_name_or_id": "Mahmoud (human operator)",
        "next_step_boundary": "separate later human step required",
        "review_notes": "reviewed as research-only; no data work observed",
    }
    for flag in DECISION_REVIEW_REQUIRED_AFFIRMATIONS:
        decision_review_packet[flag] = True
    decision_review = (
        build_crypto_d1_research_only_dry_run_decision_review_contract(
            decision, decision_review_packet
        )
    )

    # Sanity: the real Bundle 52 contract is active + READY + ready-gate.
    assert decision_review[
        "crypto_d1_research_only_dry_run_decision_review_contract_active"
    ] is True
    assert decision_review["dry_run_decision_review_verdict"] == (
        DECISION_REVIEW_VERDICT_READY
    )
    assert decision_review["next_gate"] == (
        UPSTREAM_REQUIRED_DECISION_REVIEW_NEXT_GATE
    )

    final_packet = {**_good_final_decision_packet(),
                    "upstream_decision_review_id": "DRP-1"}
    c = build_crypto_d1_research_only_dry_run_final_decision_contract(
        decision_review, final_packet
    )
    assert c[
        "crypto_d1_research_only_dry_run_final_decision_contract_active"
    ] is True
    assert c["dry_run_final_decision_verdict"] == (
        FINAL_DECISION_VERDICT_READY_FOR_ARCHIVE
    )
    assert c["validation"]["valid"] is True

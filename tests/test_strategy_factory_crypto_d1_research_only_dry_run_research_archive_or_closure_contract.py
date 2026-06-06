"""Tests for the Strategy Factory Crypto-D1 Research-Only Dry-Run Research
Archive or Closure Contract (Bundle 54).

Bundle 54 is a PURE, stdlib-only, read-only *paper archive-or-closure contract*
builder. It consumes a Bundle 53 crypto-d1 research-only dry-run FINAL DECISION
contract and, only when that final-decision contract is active + carries the
Bundle 53 READY verdict (DRY_RUN_FINAL_DECISION_READY_FOR_RESEARCH_ARCHIVE) +
the Bundle 53 ready next-gate
(CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_READY_FOR_RESEARCH_ARCHIVE_SEPARATE_HUMAN_NEXT_STEP_REQUIRED),
evaluates a proposed ARCHIVE-OR-CLOSURE packet and returns a deterministic
verdict describing whether a human chose, on paper, to archive the research-only
dry-run sequence (paper/source-only) or to formally close the lane -- or whether
the lane should park, need more info, or be rejected. It performs NO dry run,
decides on paper only, acquires nothing, fetches nothing, inspects nothing,
loads no dataset, runs no QA/baseline/backtest/simulation, produces no trade
signal, validates no market data, reaches no broker/exchange/order/account/API
surface, triggers no automation, and writes nothing. An ARCHIVE_READY or
CLOSURE_READY verdict unlocks NOTHING real and still requires a separate, later,
human step to act on the archive or closure.

Coverage:
- schema / label / status / state constants stable
- verdict + gate constants stable; ordering
- activation strictly gated on Bundle 53 active + READY + ready-gate
- every verdict path: ARCHIVE_READY, CLOSURE_READY, NEEDS_MORE_INFO, REJECTED,
  PARKED, AWAIT
- choice resolution (archive synonyms, closure synonyms, unresolvable)
- conditional fields per chosen path
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
- a real Bundle 49->50->51->52->53 chain activates Bundle 54 end-to-end
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_research_archive_or_closure_contract import (  # noqa: E501
    ARCHIVE_OR_CLOSURE_SCHEMA_VERSION,
    DEFAULT_ARCHIVE_OR_CLOSURE_LABEL,
    ARCHIVE_OR_CLOSURE_STATUS,
    ARCHIVE_OR_CLOSURE_SAFETY_POSTURE,
    ARCHIVE_OR_CLOSURE_STATE_ACTIVE,
    ARCHIVE_OR_CLOSURE_STATE_BLOCKED,
    ARCHIVE_OR_CLOSURE_VERDICT_ARCHIVE_READY,
    ARCHIVE_OR_CLOSURE_VERDICT_CLOSURE_READY,
    ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO,
    ARCHIVE_OR_CLOSURE_VERDICT_REJECTED,
    ARCHIVE_OR_CLOSURE_VERDICT_PARKED,
    ARCHIVE_OR_CLOSURE_VERDICT_AWAIT,
    ALLOWED_ARCHIVE_OR_CLOSURE_VERDICTS,
    UPSTREAM_REQUIRED_FINAL_DECISION_VERDICT,
    UPSTREAM_REQUIRED_FINAL_DECISION_NEXT_GATE,
    ARCHIVE_OR_CLOSURE_NEXT_REQUIRED_ACTION,
    ARCHIVE_OR_CLOSURE_CURRENT_STAGE,
    DECISION_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_REQUIRED,
    NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_ARCHIVE_READY,
    NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_CLOSURE_READY,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_PARKED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_CONTRACT,
    REQUIRED_ARCHIVE_OR_CLOSURE_FIELDS,
    ARCHIVE_OR_CLOSURE_REQUIRED_TEXT_FIELDS,
    ARCHIVE_OR_CLOSURE_REQUIRED_AFFIRMATIONS,
    ARCHIVE_CONDITIONAL_FIELDS,
    CLOSURE_CONDITIONAL_FIELDS,
    ARCHIVE_OR_CLOSURE_FORBIDDEN_ALLOW_FLAGS,
    ALLOWED_ARCHIVE_OR_CLOSURE_MODES,
    ALLOWED_ARCHIVE_OR_CLOSURE_SCOPES,
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_research_only_dry_run_research_archive_or_closure,
    build_crypto_d1_research_only_dry_run_research_archive_or_closure_contract,
    validate_crypto_d1_research_only_dry_run_research_archive_or_closure_contract,  # noqa: E501
    render_crypto_d1_research_only_dry_run_research_archive_or_closure_contract_markdown,  # noqa: E501
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_research_only_dry_run_research_archive_or_closure_contract.py"  # noqa: E501
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

_FINAL_DECISION_PACKET_ID = "FDP-1"

build = (
    build_crypto_d1_research_only_dry_run_research_archive_or_closure_contract
)
evaluate = (
    evaluate_crypto_d1_research_only_dry_run_research_archive_or_closure
)
validate = (
    validate_crypto_d1_research_only_dry_run_research_archive_or_closure_contract
)
render = (
    render_crypto_d1_research_only_dry_run_research_archive_or_closure_contract_markdown  # noqa: E501
)


# --- fixtures --------------------------------------------------------------

def _synthetic_final_decision_contract():
    """A Bundle-53-shaped dict that activates the Bundle 54 build."""
    return {
        "crypto_d1_research_only_dry_run_final_decision_contract_active": True,
        "dry_run_final_decision_verdict": (
            UPSTREAM_REQUIRED_FINAL_DECISION_VERDICT
        ),
        "next_gate": UPSTREAM_REQUIRED_FINAL_DECISION_NEXT_GATE,
        "evaluated_final_decision_packet": {
            "final_decision_packet_id": _FINAL_DECISION_PACKET_ID,
        },
        "idea_id": "IDEA-1",
        "title": "Crypto-D1 lane",
        "asset_lane": "crypto",
        "timeframe_lane": "1d",
    }


def _base_packet():
    """Common safe text fields + affirmations (no choice-conditional yet)."""
    p = {
        "archive_or_closure_packet_id": "AOC-1",
        "upstream_final_decision_id": _FINAL_DECISION_PACKET_ID,
        "final_decision_contract_version": "final_decision.v1",
        "archive_or_closure_scope": "archive_or_closure_only",
        "archive_or_closure_mode": "research_only",
        "research_outcome_summary": "research-only dry-run sequence concluded",
        "final_decision_summary": "human finally decided a safe research archive",
        "operator_name_or_id": "Mahmoud (human operator)",
        "follow_up_boundary": "separate later human step required",
        "final_notes": "decided on paper; no data work, no execution observed",
    }
    for flag in ARCHIVE_OR_CLOSURE_REQUIRED_AFFIRMATIONS:
        p[flag] = True
    return p


def _good_archive_packet():
    """A complete, safe, research-only archive packet."""
    p = _base_packet()
    p["archive_or_closure_choice"] = "archive"
    p["archive_reason"] = "preserve the research-only dry-run source and metadata"
    p["archive_reference_policy"] = (
        "source-code and metadata only; no future real-world action"
    )
    return p


def _good_closure_packet():
    """A complete, safe, research-only closure packet."""
    p = _base_packet()
    p["archive_or_closure_choice"] = "closure"
    p["closure_reason"] = "cleanly stop the research-only dry-run lane"
    p["closure_state"] = "closed; no future real-world action"
    return p


def _build(upstream=None, packet=None, kind="archive"):
    if packet is None:
        packet = (
            _good_archive_packet()
            if kind == "archive"
            else _good_closure_packet()
        )
    return build(
        upstream
        if upstream is not None
        else _synthetic_final_decision_contract(),
        packet,
    )


# --- 1: schema / label / status / state constants --------------------------

def test_schema_version_stable():
    assert ARCHIVE_OR_CLOSURE_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_research_only_dry_run_research_archive_or_"
        "closure_contract.v1"
    )


def test_label_and_status_stable():
    assert DEFAULT_ARCHIVE_OR_CLOSURE_LABEL == (
        "Strategy Factory Crypto-D1 Research-Only Dry-Run Research Archive or "
        "Closure Contract"
    )
    assert ARCHIVE_OR_CLOSURE_STATUS == (
        "READ_ONLY_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_ARCHIVE_OR_"
        "CLOSURE_CONTRACT"
    )


def test_state_constants_stable():
    assert ARCHIVE_OR_CLOSURE_STATE_ACTIVE.endswith("_ACTIVE")
    assert ARCHIVE_OR_CLOSURE_STATE_BLOCKED.endswith("_BLOCKED")
    assert ARCHIVE_OR_CLOSURE_STATE_ACTIVE != ARCHIVE_OR_CLOSURE_STATE_BLOCKED


# --- 2: verdict + gate constants -------------------------------------------

def test_verdict_constants_stable():
    assert ARCHIVE_OR_CLOSURE_VERDICT_ARCHIVE_READY == (
        "DRY_RUN_RESEARCH_ARCHIVE_READY"
    )
    assert ARCHIVE_OR_CLOSURE_VERDICT_CLOSURE_READY == (
        "DRY_RUN_RESEARCH_CLOSURE_READY"
    )
    assert ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO == (
        "DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_NEEDS_MORE_INFO"
    )
    assert ARCHIVE_OR_CLOSURE_VERDICT_REJECTED == (
        "DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_REJECTED"
    )
    assert ARCHIVE_OR_CLOSURE_VERDICT_PARKED == (
        "DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_PARKED"
    )
    assert ARCHIVE_OR_CLOSURE_VERDICT_AWAIT == (
        "AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_CONTRACT"
    )


def test_allowed_verdicts_order():
    assert ALLOWED_ARCHIVE_OR_CLOSURE_VERDICTS == (
        ARCHIVE_OR_CLOSURE_VERDICT_ARCHIVE_READY,
        ARCHIVE_OR_CLOSURE_VERDICT_CLOSURE_READY,
        ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO,
        ARCHIVE_OR_CLOSURE_VERDICT_REJECTED,
        ARCHIVE_OR_CLOSURE_VERDICT_PARKED,
        ARCHIVE_OR_CLOSURE_VERDICT_AWAIT,
    )


def test_allowed_verdicts_unique():
    assert len(ALLOWED_ARCHIVE_OR_CLOSURE_VERDICTS) == len(
        set(ALLOWED_ARCHIVE_OR_CLOSURE_VERDICTS)
    )


def test_upstream_required_signal_constants():
    assert UPSTREAM_REQUIRED_FINAL_DECISION_VERDICT == (
        "DRY_RUN_FINAL_DECISION_READY_FOR_RESEARCH_ARCHIVE"
    )
    assert UPSTREAM_REQUIRED_FINAL_DECISION_NEXT_GATE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_READY_FOR_RESEARCH_"
        "ARCHIVE_SEPARATE_HUMAN_NEXT_STEP_REQUIRED"
    )


def test_next_gate_constants_stable():
    gates = {
        NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_ARCHIVE_READY,
        NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_CLOSURE_READY,
        NEXT_GATE_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_FIX_REQUIRED,
        NEXT_GATE_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_PARKED,
        NEXT_GATE_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_REJECTED,
        NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_CONTRACT,
    }
    assert len(gates) == 6
    assert NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_ARCHIVE_READY.endswith(  # noqa: E501
        "SEPARATE_HUMAN_NEXT_STEP_REQUIRED"
    )
    assert NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_CLOSURE_READY.endswith(  # noqa: E501
        "SEPARATE_HUMAN_NEXT_STEP_REQUIRED"
    )


def test_next_required_action_and_stage_are_strings():
    assert isinstance(ARCHIVE_OR_CLOSURE_NEXT_REQUIRED_ACTION, str)
    assert isinstance(ARCHIVE_OR_CLOSURE_CURRENT_STAGE, str)
    assert ARCHIVE_OR_CLOSURE_NEXT_REQUIRED_ACTION


def test_next_required_action_is_what_this_bundle_fulfills():
    assert ARCHIVE_OR_CLOSURE_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_"
        "CONTRACT"
    )
    assert ARCHIVE_OR_CLOSURE_CURRENT_STAGE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_CONTRACT_"
        "REQUIRED"
    )


def test_decision_required_constant():
    assert DECISION_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_REQUIRED == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_REQUIRED"
    )


# --- 3: required fields -----------------------------------------------------

def test_required_text_fields_exact():
    assert ARCHIVE_OR_CLOSURE_REQUIRED_TEXT_FIELDS == (
        "archive_or_closure_packet_id",
        "upstream_final_decision_id",
        "final_decision_contract_version",
        "archive_or_closure_scope",
        "archive_or_closure_mode",
        "research_outcome_summary",
        "final_decision_summary",
        "archive_or_closure_choice",
        "operator_name_or_id",
        "follow_up_boundary",
        "final_notes",
    )


def test_required_affirmations_complete():
    expected = {
        "explicit_human_archive_or_closure_decision",
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
    }
    assert set(ARCHIVE_OR_CLOSURE_REQUIRED_AFFIRMATIONS) == expected
    assert len(ARCHIVE_OR_CLOSURE_REQUIRED_AFFIRMATIONS) == 21


def test_conditional_fields_exact():
    assert ARCHIVE_CONDITIONAL_FIELDS == (
        "archive_reason",
        "archive_reference_policy",
    )
    assert CLOSURE_CONDITIONAL_FIELDS == (
        "closure_reason",
        "closure_state",
    )


def test_required_fields_is_union_of_36():
    assert REQUIRED_ARCHIVE_OR_CLOSURE_FIELDS == (
        ARCHIVE_OR_CLOSURE_REQUIRED_TEXT_FIELDS
        + ARCHIVE_CONDITIONAL_FIELDS
        + CLOSURE_CONDITIONAL_FIELDS
        + ARCHIVE_OR_CLOSURE_REQUIRED_AFFIRMATIONS
    )
    assert len(REQUIRED_ARCHIVE_OR_CLOSURE_FIELDS) == 36


def test_allowed_modes_and_scopes():
    assert ALLOWED_ARCHIVE_OR_CLOSURE_MODES == ("research_only", "research-only")
    assert "archive_or_closure_only" in ALLOWED_ARCHIVE_OR_CLOSURE_SCOPES
    assert "archive_only" in ALLOWED_ARCHIVE_OR_CLOSURE_SCOPES
    assert "closure_only" in ALLOWED_ARCHIVE_OR_CLOSURE_SCOPES


def test_safety_posture_all_false():
    assert len(ARCHIVE_OR_CLOSURE_SAFETY_POSTURE) > 0
    assert all(v is False for v in ARCHIVE_OR_CLOSURE_SAFETY_POSTURE.values())


def test_forbidden_allow_flags_cover_real_capabilities():
    for flag in (
        "allow_real_data_acquisition",
        "allow_data_fetch",
        "allow_data_inspection",
        "allow_dataset_loading",
        "allow_qa_run",
        "allow_baseline_run",
        "allow_backtest_run",
        "allow_simulation_run",
        "allow_paper_live",
        "allow_broker_exchange",
        "allow_order_capability",
        "allow_account_access",
        "allow_api_keys",
        "allow_automation_trigger",
        "allow_runtime_write",
        "allow_registry_write",
        "allow_dashboard_write",
        "allow_trade_signal",
        "execution_authorized",
        "archive_with_real_data",
        "proceed_to_live_after_archive",
        "proceed_to_live_after_closure",
        "reopen_for_real_acquisition",
    ):
        assert flag in ARCHIVE_OR_CLOSURE_FORBIDDEN_ALLOW_FLAGS, flag


# --- 4: activation gating ---------------------------------------------------

def test_active_when_upstream_ready_and_gate():
    c = _build()
    assert c[
        "crypto_d1_research_only_dry_run_research_archive_or_closure_contract_active"  # noqa: E501
    ] is True
    assert c[
        "crypto_d1_research_only_dry_run_research_archive_or_closure_contract_state"  # noqa: E501
    ] == ARCHIVE_OR_CLOSURE_STATE_ACTIVE


def test_inactive_when_upstream_empty():
    c = build({}, _good_archive_packet())
    assert c[
        "crypto_d1_research_only_dry_run_research_archive_or_closure_contract_active"  # noqa: E501
    ] is False
    assert c["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_AWAIT
    )


def test_inactive_when_upstream_not_active():
    up = _synthetic_final_decision_contract()
    up["crypto_d1_research_only_dry_run_final_decision_contract_active"] = False
    c = build(up, _good_archive_packet())
    assert c["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_AWAIT
    )


def test_inactive_when_wrong_verdict():
    up = _synthetic_final_decision_contract()
    up["dry_run_final_decision_verdict"] = "SOMETHING_ELSE"
    c = build(up, _good_archive_packet())
    assert c["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_AWAIT
    )


def test_inactive_when_wrong_gate():
    up = _synthetic_final_decision_contract()
    up["next_gate"] = "WRONG_GATE"
    c = build(up, _good_archive_packet())
    assert c["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_AWAIT
    )


def test_inactive_when_upstream_garbage():
    for bad in (None, 5, "x", [], object()):
        c = build(bad, _good_archive_packet())
        assert c["dry_run_research_archive_or_closure_verdict"] == (
            ARCHIVE_OR_CLOSURE_VERDICT_AWAIT
        )
        assert c[
            "crypto_d1_research_only_dry_run_research_archive_or_closure_contract_active"  # noqa: E501
        ] is False


def test_await_verdict_ignores_packet_shape():
    c = build({}, {"allow_real_data_acquisition": True})
    assert c["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_AWAIT
    )


def test_await_sets_await_gate():
    c = build({}, _good_archive_packet())
    assert c["next_gate"] == (
        NEXT_GATE_AWAIT_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_FINAL_DECISION_CONTRACT
    )


# --- 5: ARCHIVE_READY path --------------------------------------------------

def test_archive_ready_when_complete_and_safe():
    c = _build(kind="archive")
    assert c["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_ARCHIVE_READY
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_ARCHIVE_READY
    )


def test_archive_ready_validation_valid():
    c = _build(kind="archive")
    assert c["validation"]["valid"] is True


def test_evaluate_archive_ready_direct():
    res = evaluate(_good_archive_packet(), {
        "final_decision_packet_id": _FINAL_DECISION_PACKET_ID,
    })
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_ARCHIVE_READY


def test_archive_synonyms_resolve():
    for syn in (
        "archive",
        "research_archive",
        "dry_run_research_archive",
        "research_only_archive",
        "archive_path",
    ):
        p = _good_archive_packet()
        p["archive_or_closure_choice"] = syn
        res = evaluate(p)
        assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_ARCHIVE_READY, syn


def test_archive_choice_uppercase_resolves():
    p = _good_archive_packet()
    p["archive_or_closure_choice"] = "ARCHIVE"
    assert evaluate(p)["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_ARCHIVE_READY


# --- 6: CLOSURE_READY path --------------------------------------------------

def test_closure_ready_when_complete_and_safe():
    c = _build(kind="closure")
    assert c["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_CLOSURE_READY
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_CLOSURE_READY
    )


def test_closure_ready_validation_valid():
    c = _build(kind="closure")
    assert c["validation"]["valid"] is True


def test_evaluate_closure_ready_direct():
    res = evaluate(_good_closure_packet(), {
        "final_decision_packet_id": _FINAL_DECISION_PACKET_ID,
    })
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_CLOSURE_READY


def test_closure_synonyms_resolve():
    for syn in (
        "closure",
        "close",
        "research_closure",
        "dry_run_research_closure",
        "stop",
        "pause",
        "research_only_closure",
        "closure_path",
    ):
        p = _good_closure_packet()
        p["archive_or_closure_choice"] = syn
        res = evaluate(p)
        assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_CLOSURE_READY, syn


def test_research_dash_only_mode_accepted():
    p = _good_archive_packet()
    p["archive_or_closure_mode"] = "research-only"
    assert evaluate(p)["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_ARCHIVE_READY


# --- 7: NEEDS_MORE_INFO -----------------------------------------------------

def test_empty_packet_needs_more_info():
    res = evaluate({})
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO


def test_missing_each_base_text_field_needs_more_info():
    for key in ARCHIVE_OR_CLOSURE_REQUIRED_TEXT_FIELDS:
        p = _good_archive_packet()
        del p[key]
        res = evaluate(p)
        assert res["verdict"] == (
            ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO
        ), key


def test_missing_each_affirmation_needs_more_info():
    for flag in ARCHIVE_OR_CLOSURE_REQUIRED_AFFIRMATIONS:
        p = _good_archive_packet()
        del p[flag]
        res = evaluate(p)
        assert res["verdict"] == (
            ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO
        ), flag
        assert f"{flag}_must_be_affirmed_true" in res["reasons"]


def test_unresolvable_choice_needs_more_info():
    p = _good_archive_packet()
    p["archive_or_closure_choice"] = "banana"
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO
    assert (
        "archive_or_closure_choice_must_be_archive_or_closure"
        in res["reasons"]
    )


def test_archive_choice_missing_archive_reason():
    p = _good_archive_packet()
    del p["archive_reason"]
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO
    assert "archive_reason_required" in res["reasons"]


def test_archive_choice_missing_reference_policy():
    p = _good_archive_packet()
    del p["archive_reference_policy"]
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO
    assert "archive_reference_policy_required" in res["reasons"]


def test_closure_choice_missing_closure_reason():
    p = _good_closure_packet()
    del p["closure_reason"]
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO
    assert "closure_reason_required" in res["reasons"]


def test_closure_choice_missing_closure_state():
    p = _good_closure_packet()
    del p["closure_state"]
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO
    assert "closure_state_required" in res["reasons"]


def test_archive_choice_does_not_require_closure_fields():
    p = _good_archive_packet()  # carries no closure_reason / closure_state
    assert "closure_reason" not in p
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_ARCHIVE_READY


def test_closure_choice_does_not_require_archive_fields():
    p = _good_closure_packet()  # carries no archive_reason / policy
    assert "archive_reason" not in p
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_CLOSURE_READY


def test_build_needs_more_info_sets_fix_gate():
    p = _good_archive_packet()
    del p["final_notes"]
    c = _build(packet=p)
    assert c["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_NEEDS_MORE_INFO
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_FIX_REQUIRED
    )


# --- 8: REJECTED ------------------------------------------------------------

def test_reject_each_forbidden_allow_flag():
    for flag in ARCHIVE_OR_CLOSURE_FORBIDDEN_ALLOW_FLAGS:
        p = _good_archive_packet()
        p[flag] = True
        res = evaluate(p)
        assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED, flag
        assert f"forbidden_allow:{flag}" in res["reasons"]


def test_reject_real_data_acquisition_allow_flag():
    p = _good_archive_packet()
    p["allow_real_data_acquisition"] = True
    assert evaluate(p)["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED


def test_reject_qa_baseline_backtest_simulation_allow_flags():
    for flag in (
        "allow_qa_run",
        "allow_baseline_run",
        "allow_backtest_run",
        "allow_simulation_run",
    ):
        p = _good_closure_packet()
        p[flag] = True
        assert evaluate(p)["verdict"] == (
            ARCHIVE_OR_CLOSURE_VERDICT_REJECTED
        ), flag


def test_reject_paper_live_broker_order_account_api_flags():
    for flag in (
        "allow_paper_live",
        "allow_broker_exchange",
        "allow_order_capability",
        "allow_account_access",
        "allow_api_keys",
    ):
        p = _good_archive_packet()
        p[flag] = True
        assert evaluate(p)["verdict"] == (
            ARCHIVE_OR_CLOSURE_VERDICT_REJECTED
        ), flag


def test_reject_runtime_registry_dashboard_write_flags():
    for flag in (
        "allow_runtime_write",
        "allow_registry_write",
        "allow_dashboard_write",
    ):
        p = _good_archive_packet()
        p[flag] = True
        assert evaluate(p)["verdict"] == (
            ARCHIVE_OR_CLOSURE_VERDICT_REJECTED
        ), flag


def test_reject_archive_with_real_data_flag():
    p = _good_archive_packet()
    p["archive_with_real_data"] = True
    assert evaluate(p)["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED


def test_reject_proceed_to_live_after_closure_flag():
    p = _good_closure_packet()
    p["proceed_to_live_after_closure"] = True
    assert evaluate(p)["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED


def test_reject_reopen_for_execution_flag():
    p = _good_closure_packet()
    p["reopen_for_execution"] = True
    assert evaluate(p)["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED


def test_reject_relaxed_each_affirmation():
    for flag in ARCHIVE_OR_CLOSURE_REQUIRED_AFFIRMATIONS:
        p = _good_archive_packet()
        p[flag] = "no"
        res = evaluate(p)
        assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED, flag
        assert f"affirmation_relaxed:{flag}" in res["reasons"]


def test_reject_disallowed_mode():
    p = _good_archive_packet()
    p["archive_or_closure_mode"] = "live"
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED
    assert "disallowed_value:archive_or_closure_mode" in res["reasons"]


def test_reject_disallowed_scope():
    p = _good_archive_packet()
    p["archive_or_closure_scope"] = "real_acquisition"
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED
    assert "disallowed_value:archive_or_closure_scope" in res["reasons"]


def test_reject_automated_decider_name():
    p = _good_archive_packet()
    p["operator_name_or_id"] = next(iter(AUTOMATED_APPROVAL_MARKERS))
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED
    assert any(r.startswith("automated_decider:") for r in res["reasons"])


def test_reject_automated_decider_type_key():
    p = _good_archive_packet()
    p["operator_type"] = next(iter(AUTOMATED_APPROVAL_MARKERS))
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED
    assert "automated_decider:operator_type" in res["reasons"]


def test_reject_granted_authority():
    p = _good_archive_packet()
    p["grants_capabilities"] = ["data_fetch"]
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED
    assert "grants_listed:grants_capabilities" in res["reasons"]


def test_reject_upstream_id_mismatch():
    p = _good_archive_packet()
    p["upstream_final_decision_id"] = "WRONG"
    res = evaluate(p, {"final_decision_packet_id": _FINAL_DECISION_PACKET_ID})
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED
    assert "mismatch:upstream_final_decision_id" in res["reasons"]


def test_no_mismatch_when_ref_absent():
    p = _good_archive_packet()
    p["upstream_final_decision_id"] = "WHATEVER"
    res = evaluate(p, None)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_ARCHIVE_READY


def test_build_rejected_sets_reject_gate():
    p = _good_archive_packet()
    p["allow_real_data_acquisition"] = True
    c = _build(packet=p)
    assert c["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_REJECTED
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_REJECTED
    )


def test_reject_takes_priority_over_missing():
    p = {"allow_real_data_acquisition": True}
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED


def test_reject_takes_priority_over_park():
    p = _good_archive_packet()
    p["park"] = True
    p["allow_real_data_acquisition"] = True
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_REJECTED


# --- 9: PARKED --------------------------------------------------------------

def test_park_via_flag():
    p = _good_archive_packet()
    p["park"] = True
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_PARKED


def test_park_via_operator_decision():
    p = _good_closure_packet()
    p["operator_decision"] = "defer"
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_PARKED


def test_park_via_archive_or_closure_decision_value():
    p = _good_archive_packet()
    p["archive_or_closure_decision"] = "hold"
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_PARKED


def test_build_parked_sets_park_gate():
    p = _good_archive_packet()
    p["parked"] = True
    c = _build(packet=p)
    assert c["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_PARKED
    )
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_PARKED
    )


def test_park_takes_priority_over_missing():
    p = {"park": True}
    res = evaluate(p)
    assert res["verdict"] == ARCHIVE_OR_CLOSURE_VERDICT_PARKED


# --- 10: no verdict authorizes / unlocks ------------------------------------

def test_no_verdict_authorizes_or_executes():
    packets = (
        None,
        {},
        _good_archive_packet(),
        _good_closure_packet(),
        {"allow_real_data_acquisition": True},
        {"park": True},
    )
    upstreams = (None, {}, _synthetic_final_decision_contract())
    for up in upstreams:
        for pk in packets:
            c = build(up, pk)
            for flag in _AUTH_FLAGS:
                assert c[flag] is False
            assert c["read_only"] is True
            assert c["executes"] is False
            assert c["human_approval_required"] is True
            assert all(
                v is False for v in c["safety_posture"].values()
            )


def test_contract_mode_always_research_only():
    assert _build()["mode"] == "RESEARCH_ONLY"
    assert build({}, {})["mode"] == "RESEARCH_ONLY"


def test_contract_stage_always_archive_or_closure_only():
    assert _build()["stage"] == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_ONLY"
    )


def test_blocked_capabilities_present_and_nonempty():
    c = _build()
    assert len(c["archive_or_closure_blocked_capabilities"]) >= 1
    assert len(c["blocked_capabilities"]) >= 1


def test_no_verdict_carries_real_capability_marker():
    c = _build()
    for flag in ARCHIVE_OR_CLOSURE_FORBIDDEN_ALLOW_FLAGS:
        assert c.get(flag) in (None, False)


def test_required_action_and_stage_present_only_when_active():
    active = _build()
    assert active["dry_run_research_archive_or_closure_required"] == (
        DECISION_CRYPTO_D1_DRY_RUN_RESEARCH_ARCHIVE_OR_CLOSURE_REQUIRED
    )
    inactive = build({}, _good_archive_packet())
    assert inactive["dry_run_research_archive_or_closure_required"] == ""


# --- 11: validation ---------------------------------------------------------

def test_validate_public_matches_embedded():
    c = _build()
    assert validate(c) == c["validation"]


def test_validate_rejects_tampered_schema():
    c = _build()
    c["schema_version"] = "x"
    assert validate(c)["valid"] is False


def test_validate_rejects_missing_field():
    c = _build()
    del c["safety_posture"]
    assert validate(c)["valid"] is False


def test_validate_rejects_executes_true():
    c = _build()
    c["executes"] = True
    assert validate(c)["valid"] is False


def test_validate_rejects_tampered_posture():
    c = _build()
    c["safety_posture"] = {"x": True}
    assert validate(c)["valid"] is False


def test_validate_rejects_auth_flag_true():
    c = _build()
    c["execution_authorized"] = True
    assert validate(c)["valid"] is False


def test_validate_handles_garbage():
    for bad in (None, 5, "x", []):
        out = validate(bad)
        assert out["valid"] is False


# --- 12: determinism + isolation --------------------------------------------

def test_build_is_deterministic():
    a = _build()
    b = _build()
    a.pop("crypto_d1_research_only_dry_run_final_decision_contract", None)
    b.pop("crypto_d1_research_only_dry_run_final_decision_contract", None)
    assert a == b


def test_evaluate_is_deterministic():
    p = _good_archive_packet()
    assert evaluate(p) == evaluate(p)


def test_safety_posture_copy_is_isolated():
    c = _build()
    c["safety_posture"]["execution_authorized"] = True
    assert all(v is False for v in ARCHIVE_OR_CLOSURE_SAFETY_POSTURE.values())


def test_input_packet_not_mutated():
    p = _good_archive_packet()
    snapshot = dict(p)
    _build(packet=p)
    assert p == snapshot


# --- 13: markdown -----------------------------------------------------------

def test_markdown_nonempty_and_titled():
    md = render(_build())
    assert md.startswith(
        "# Strategy Factory Crypto-D1 Research-Only Dry-Run Research Archive "
        "or Closure Contract"
    )
    assert "## Allowed Dry-Run Archive Or Closure Verdicts" in md
    assert "## Archive Conditional Fields" in md
    assert "## Closure Conditional Fields" in md


def test_markdown_handles_minimal_contract():
    md = render({})
    assert isinstance(md, str)
    assert md


# --- 14: pure stdlib import-root + forbidden-surface audit ------------------

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
    src = _MODPATH.read_text(encoding="utf-8")
    assert "strategy_factory_mission_flow_bundle_registry" not in src
    assert "strategy_factory_mission_flow_status" not in src


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
        'research_archive_or_closure_contract.py"' in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_research_only_dry_run_'
        'research_archive_or_closure_contract.py"' in src
    )


# --- 16: real upstream chain -----------------------------------------------

def test_real_bundle_53_chain_activates_bundle_54():
    """Build a REAL Bundle 49->50->51->52->53 contract and confirm it activates
    Bundle 54 end-to-end (no synthetic upstream)."""
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
        build_crypto_d1_research_only_dry_run_decision_review_contract,
    )
    from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_final_decision_contract import (  # noqa: E501
        FINAL_DECISION_REQUIRED_AFFIRMATIONS,
        FINAL_DECISION_VERDICT_READY_FOR_ARCHIVE,
        build_crypto_d1_research_only_dry_run_final_decision_contract,
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

    final_packet = {
        "final_decision_packet_id": "FDP-REAL-1",
        "upstream_decision_review_id": "DRP-1",
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
        final_packet[flag] = True
    final_decision = (
        build_crypto_d1_research_only_dry_run_final_decision_contract(
            decision_review, final_packet
        )
    )

    # Sanity: the real Bundle 53 contract is active + READY + ready-gate.
    assert final_decision[
        "crypto_d1_research_only_dry_run_final_decision_contract_active"
    ] is True
    assert final_decision["dry_run_final_decision_verdict"] == (
        FINAL_DECISION_VERDICT_READY_FOR_ARCHIVE
    )
    assert final_decision["next_gate"] == (
        UPSTREAM_REQUIRED_FINAL_DECISION_NEXT_GATE
    )

    archive_packet = {**_good_archive_packet(),
                      "upstream_final_decision_id": "FDP-REAL-1"}
    c = build(final_decision, archive_packet)
    assert c[
        "crypto_d1_research_only_dry_run_research_archive_or_closure_contract_active"  # noqa: E501
    ] is True
    assert c["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_ARCHIVE_READY
    )
    assert c["validation"]["valid"] is True

    # And a closure packet against the same real chain.
    closure_packet = {**_good_closure_packet(),
                      "upstream_final_decision_id": "FDP-REAL-1"}
    c2 = build(final_decision, closure_packet)
    assert c2["dry_run_research_archive_or_closure_verdict"] == (
        ARCHIVE_OR_CLOSURE_VERDICT_CLOSURE_READY
    )
    assert c2["validation"]["valid"] is True

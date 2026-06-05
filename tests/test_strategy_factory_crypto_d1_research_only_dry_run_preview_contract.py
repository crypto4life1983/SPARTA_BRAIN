"""Tests for the Strategy Factory Crypto-D1 Research-Only Dry-Run Preview
Contract (Bundle 49).

Bundle 49 is a PURE, stdlib-only, read-only *paper decision contract* builder.
It consumes a Bundle 48 crypto-d1 post-boundary research-only next-step contract
and, only when that next-step contract is active + carries the Bundle 48 PROCEED
verdict + the Bundle 48 ready next-gate, evaluates a proposed dry-run preview
packet and returns a deterministic verdict describing whether a future
research-only dry-run preview would be ALLOWED to be previewed -- or whether the
lane should park, need more info, or be rejected. It performs NO dry run,
acquires nothing, fetches nothing, inspects nothing, loads no dataset, runs no
QA/baseline/backtest/simulation, produces no trade signal, validates no market
data, reaches no broker/exchange/order/account/API surface, triggers no
automation, and writes nothing. A READY verdict unlocks NOTHING real.

Coverage:
- schema / label / status / state constants stable
- verdict + gate constants stable; ordering
- activation strictly gated on Bundle 48 active + PROCEED + ready-gate
- every verdict path: READY, NEEDS_MORE_INFO, REJECTED, PARKED, AWAIT
- each REJECTED category (forbidden allow flag, relaxed prohibition, relaxed
  affirmation, disallowed enum value, automated author, granted authority,
  upstream-id mismatch)
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

from sparta_commander.strategy_factory_crypto_d1_research_only_dry_run_preview_contract import (  # noqa: E501
    PREVIEW_SCHEMA_VERSION,
    DEFAULT_PREVIEW_LABEL,
    PREVIEW_STATUS,
    PREVIEW_SAFETY_POSTURE,
    PREVIEW_STATE_ACTIVE,
    PREVIEW_STATE_BLOCKED,
    PREVIEW_VERDICT_READY,
    PREVIEW_VERDICT_NEEDS_MORE_INFO,
    PREVIEW_VERDICT_REJECTED,
    PREVIEW_VERDICT_PARKED,
    PREVIEW_VERDICT_AWAIT,
    ALLOWED_PREVIEW_VERDICTS,
    UPSTREAM_REQUIRED_NEXT_STEP_VERDICT,
    UPSTREAM_REQUIRED_NEXT_STEP_NEXT_GATE,
    DRY_RUN_PREVIEW_NEXT_REQUIRED_ACTION,
    DRY_RUN_PREVIEW_CURRENT_STAGE,
    PREVIEW_CRYPTO_D1_DRY_RUN_PREVIEW_REQUIRED,
    NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_HUMAN_RUN_REQUIRED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_PARKED,
    NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT,
    REQUIRED_PREVIEW_FIELDS,
    PREVIEW_REQUIRED_TEXT_FIELDS,
    PREVIEW_REQUIRED_PROHIBITIONS,
    PREVIEW_REQUIRED_AFFIRMATIONS,
    PREVIEW_FORBIDDEN_ALLOW_FLAGS,
    ALLOWED_PREVIEW_MODES,
    ALLOWED_PREVIEW_SCOPES,
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_research_only_dry_run_preview,
    build_crypto_d1_research_only_dry_run_preview_contract,
    validate_crypto_d1_research_only_dry_run_preview_contract,
    render_crypto_d1_research_only_dry_run_preview_contract_markdown,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_research_only_dry_run_preview_contract.py"
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


# --- fixtures (plain dicts; no upstream module dependency) ------------------

def _active_upstream(ref=None):
    """A Bundle-48-shaped contract that is active + PROCEED + ready-gate."""
    return {
        "crypto_d1_post_boundary_next_step_contract_active": True,
        "next_step_verdict": UPSTREAM_REQUIRED_NEXT_STEP_VERDICT,
        "next_gate": UPSTREAM_REQUIRED_NEXT_STEP_NEXT_GATE,
        "evaluated_next_step_packet": (
            ref if ref is not None else {"decision_packet_id": "B48-NS-1"}
        ),
        "idea_id": "IDEA-1",
        "title": "Crypto-D1 lane",
        "asset_lane": "crypto",
        "timeframe_lane": "1d",
    }


def _good_packet():
    """A complete, safe, research-only dry-run preview packet."""
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


def _build(upstream=None, packet=None):
    return build_crypto_d1_research_only_dry_run_preview_contract(
        upstream if upstream is not None else _active_upstream(),
        packet if packet is not None else _good_packet(),
    )


# --- 1: schema / label / status / state constants --------------------------

def test_schema_version_stable():
    assert PREVIEW_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_research_only_dry_run_preview_contract.v1"
    )


def test_label_and_status_stable():
    assert DEFAULT_PREVIEW_LABEL == (
        "Strategy Factory Crypto-D1 Research-Only Dry-Run Preview Contract"
    )
    assert PREVIEW_STATUS == (
        "READ_ONLY_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT"
    )


def test_state_constants_stable():
    assert PREVIEW_STATE_ACTIVE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_ACTIVE"
    )
    assert PREVIEW_STATE_BLOCKED == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_BLOCKED"
    )


# --- 2: verdict / gate / upstream constants --------------------------------

def test_verdict_constants_stable():
    assert PREVIEW_VERDICT_READY == "DRY_RUN_PREVIEW_READY"
    assert PREVIEW_VERDICT_NEEDS_MORE_INFO == "DRY_RUN_PREVIEW_NEEDS_MORE_INFO"
    assert PREVIEW_VERDICT_REJECTED == "DRY_RUN_PREVIEW_REJECTED"
    assert PREVIEW_VERDICT_PARKED == "DRY_RUN_PREVIEW_PARKED"
    assert PREVIEW_VERDICT_AWAIT == (
        "AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT"
    )


def test_allowed_verdicts_order():
    assert ALLOWED_PREVIEW_VERDICTS == (
        PREVIEW_VERDICT_READY,
        PREVIEW_VERDICT_NEEDS_MORE_INFO,
        PREVIEW_VERDICT_REJECTED,
        PREVIEW_VERDICT_PARKED,
        PREVIEW_VERDICT_AWAIT,
    )


def test_upstream_required_signal_constants():
    assert UPSTREAM_REQUIRED_NEXT_STEP_VERDICT == (
        "PROCEED_TO_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT"
    )
    assert UPSTREAM_REQUIRED_NEXT_STEP_NEXT_GATE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED"
    )


def test_next_gate_constants_stable():
    assert NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_HUMAN_RUN_REQUIRED == (  # noqa: E501
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_SEPARATE_HUMAN_RUN_"
        "REQUIRED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_FIX_REQUIRED == (
        "CRYPTO_D1_DRY_RUN_PREVIEW_FIX_REQUIRED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_PARKED == (
        "CRYPTO_D1_DRY_RUN_PREVIEW_PARKED"
    )
    assert NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_REJECTED == (
        "CRYPTO_D1_DRY_RUN_PREVIEW_REJECTED"
    )
    assert NEXT_GATE_AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT == (  # noqa: E501
        "AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT"
    )


def test_next_required_action_and_stage_constants():
    assert DRY_RUN_PREVIEW_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT"
    )
    assert DRY_RUN_PREVIEW_CURRENT_STAGE == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED"
    )
    assert PREVIEW_CRYPTO_D1_DRY_RUN_PREVIEW_REQUIRED == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_REQUIRED"
    )


# --- 3: required-field tuples shape ----------------------------------------

def test_required_text_fields_exact():
    assert PREVIEW_REQUIRED_TEXT_FIELDS == (
        "preview_packet_id",
        "upstream_next_step_id",
        "proposed_preview_scope",
        "proposed_preview_mode",
        "preview_inputs_description",
        "preview_outputs_description",
        "next_step_boundary",
    )


def test_required_prohibitions_complete():
    for flag in (
        "prohibited_real_data_acquisition",
        "prohibited_data_fetch",
        "prohibited_data_inspection",
        "prohibited_dataset_loading",
        "prohibited_qa_run",
        "prohibited_baseline_run",
        "prohibited_backtest_run",
        "prohibited_simulation_run",
        "prohibited_paper_live",
        "prohibited_broker_exchange",
        "prohibited_order_capability",
        "prohibited_account_access",
        "prohibited_api_keys",
        "prohibited_automation_trigger",
        "prohibited_runtime_write",
        "prohibited_registry_write",
        "prohibited_dashboard_write",
    ):
        assert flag in PREVIEW_REQUIRED_PROHIBITIONS, flag
    assert len(PREVIEW_REQUIRED_PROHIBITIONS) == 17


def test_required_affirmations_complete():
    for flag in (
        "allowed_mock_inputs_only",
        "allowed_static_contract_metadata_only",
        "preview_does_not_execute",
        "preview_does_not_validate_market_data",
        "preview_does_not_produce_trade_signal",
        "human_operator_review_required",
        "research_only_acknowledgement",
    ):
        assert flag in PREVIEW_REQUIRED_AFFIRMATIONS, flag
    assert len(PREVIEW_REQUIRED_AFFIRMATIONS) == 7


def test_required_preview_fields_is_union():
    assert REQUIRED_PREVIEW_FIELDS == (
        PREVIEW_REQUIRED_TEXT_FIELDS
        + PREVIEW_REQUIRED_PROHIBITIONS
        + PREVIEW_REQUIRED_AFFIRMATIONS
    )
    assert len(REQUIRED_PREVIEW_FIELDS) == 31


def test_allowed_modes_and_scopes():
    assert ALLOWED_PREVIEW_MODES == ("research_only", "research-only")
    assert "dry_run_preview_only" in ALLOWED_PREVIEW_SCOPES
    assert "preview_only" in ALLOWED_PREVIEW_SCOPES


# --- 4: safety posture is all-false, 14 keys -------------------------------

def test_safety_posture_all_false():
    assert len(PREVIEW_SAFETY_POSTURE) >= 1
    assert all(v is False for v in PREVIEW_SAFETY_POSTURE.values())


# --- 5: activation gating ---------------------------------------------------

def test_active_when_upstream_proceed_and_gate():
    c = _build()
    assert c["crypto_d1_research_only_dry_run_preview_contract_active"] is True
    assert c["crypto_d1_research_only_dry_run_preview_contract_state"] == (
        PREVIEW_STATE_ACTIVE
    )
    assert c["dry_run_preview_required"] == (
        PREVIEW_CRYPTO_D1_DRY_RUN_PREVIEW_REQUIRED
    )


def test_inactive_when_upstream_empty():
    c = build_crypto_d1_research_only_dry_run_preview_contract({}, _good_packet())
    assert c["crypto_d1_research_only_dry_run_preview_contract_active"] is False
    assert c["crypto_d1_research_only_dry_run_preview_contract_state"] == (
        PREVIEW_STATE_BLOCKED
    )
    assert c["dry_run_preview_verdict"] == PREVIEW_VERDICT_AWAIT
    assert c["next_gate"] == (
        NEXT_GATE_AWAIT_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT
    )
    assert c["dry_run_preview_required"] == ""


def test_inactive_when_upstream_not_active():
    up = _active_upstream()
    up["crypto_d1_post_boundary_next_step_contract_active"] = False
    c = _build(up, _good_packet())
    assert c["dry_run_preview_verdict"] == PREVIEW_VERDICT_AWAIT


def test_inactive_when_wrong_verdict():
    up = _active_upstream()
    up["next_step_verdict"] = "POST_BOUNDARY_PARKED"
    c = _build(up, _good_packet())
    assert c["dry_run_preview_verdict"] == PREVIEW_VERDICT_AWAIT


def test_inactive_when_wrong_gate():
    up = _active_upstream()
    up["next_gate"] = "SOME_OTHER_GATE"
    c = _build(up, _good_packet())
    assert c["dry_run_preview_verdict"] == PREVIEW_VERDICT_AWAIT


def test_inactive_when_upstream_garbage():
    for bad in (None, [], "x", 7, {"foo": "bar"}):
        c = build_crypto_d1_research_only_dry_run_preview_contract(
            bad, _good_packet()
        )
        assert c["dry_run_preview_verdict"] == PREVIEW_VERDICT_AWAIT
        assert c["crypto_d1_research_only_dry_run_preview_contract_active"] is (
            False
        )


def test_await_verdict_ignores_packet_shape():
    # Even a dangerous packet yields AWAIT when upstream is inactive.
    p = _good_packet()
    p["allow_data_fetch"] = True
    c = build_crypto_d1_research_only_dry_run_preview_contract({}, p)
    assert c["dry_run_preview_verdict"] == PREVIEW_VERDICT_AWAIT


# --- 6: READY ---------------------------------------------------------------

def test_ready_when_complete_and_safe():
    c = _build()
    assert c["dry_run_preview_verdict"] == PREVIEW_VERDICT_READY
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_READY_HUMAN_RUN_REQUIRED
    )


def test_evaluate_ready_direct():
    r = evaluate_crypto_d1_research_only_dry_run_preview(
        _good_packet(), {"decision_packet_id": "B48-NS-1"}
    )
    assert r["verdict"] == PREVIEW_VERDICT_READY


def test_ready_validation_valid():
    c = _build()
    assert c["validation"]["valid"] is True


# --- 7: NEEDS_MORE_INFO -----------------------------------------------------

def test_empty_packet_needs_more_info():
    r = evaluate_crypto_d1_research_only_dry_run_preview({}, {})
    assert r["verdict"] == PREVIEW_VERDICT_NEEDS_MORE_INFO
    assert r["reasons"] == ("dry_run_preview_packet_missing",)


def test_missing_each_text_field_needs_more_info():
    for key in PREVIEW_REQUIRED_TEXT_FIELDS:
        p = _good_packet()
        del p[key]
        r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
        assert r["verdict"] == PREVIEW_VERDICT_NEEDS_MORE_INFO, key
        assert any(f"{key}_required" in x for x in r["reasons"]), key


def test_missing_required_true_flag_needs_more_info():
    p = _good_packet()
    del p["prohibited_data_fetch"]
    r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    assert r["verdict"] == PREVIEW_VERDICT_NEEDS_MORE_INFO
    assert any("prohibited_data_fetch_must_be_affirmed_true" in x
               for x in r["reasons"])


def test_build_needs_more_info_sets_fix_gate():
    p = _good_packet()
    del p["preview_packet_id"]
    c = _build(_active_upstream(), p)
    assert c["dry_run_preview_verdict"] == PREVIEW_VERDICT_NEEDS_MORE_INFO
    assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_FIX_REQUIRED


# --- 8: REJECTED categories ------------------------------------------------

def test_reject_each_forbidden_allow_flag():
    for flag in PREVIEW_FORBIDDEN_ALLOW_FLAGS:
        p = _good_packet()
        p[flag] = True
        r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
        assert r["verdict"] == PREVIEW_VERDICT_REJECTED, flag
        assert any(flag in x for x in r["reasons"]), flag


def test_reject_dataset_loading_allow_flag():
    p = _good_packet()
    p["allow_dataset_loading"] = True
    r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    assert r["verdict"] == PREVIEW_VERDICT_REJECTED


def test_reject_trade_signal_allow_flag():
    p = _good_packet()
    p["produces_trade_signal"] = True
    r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    assert r["verdict"] == PREVIEW_VERDICT_REJECTED


def test_reject_market_data_validation_allow_flag():
    p = _good_packet()
    p["validates_market_data"] = True
    r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    assert r["verdict"] == PREVIEW_VERDICT_REJECTED


def test_reject_dry_run_execution_allow_flag():
    p = _good_packet()
    p["executes_dry_run"] = True
    r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    assert r["verdict"] == PREVIEW_VERDICT_REJECTED


def test_reject_relaxed_each_prohibition():
    for flag in PREVIEW_REQUIRED_PROHIBITIONS:
        p = _good_packet()
        p[flag] = False
        r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
        assert r["verdict"] == PREVIEW_VERDICT_REJECTED, flag
        assert any("prohibition_relaxed:" + flag in x
                   for x in r["reasons"]), flag


def test_reject_relaxed_each_affirmation():
    for flag in PREVIEW_REQUIRED_AFFIRMATIONS:
        p = _good_packet()
        p[flag] = False
        r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
        assert r["verdict"] == PREVIEW_VERDICT_REJECTED, flag


def test_reject_disallowed_mode():
    p = _good_packet()
    p["proposed_preview_mode"] = "live"
    r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    assert r["verdict"] == PREVIEW_VERDICT_REJECTED
    assert any("disallowed_value:proposed_preview_mode" in x
               for x in r["reasons"])


def test_reject_disallowed_scope():
    p = _good_packet()
    p["proposed_preview_scope"] = "real_data_fetch"
    r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    assert r["verdict"] == PREVIEW_VERDICT_REJECTED
    assert any("disallowed_value:proposed_preview_scope" in x
               for x in r["reasons"])


def test_reject_automated_author():
    for key in ("decision_author_type", "author_type", "decision_method",
                "decision_source", "authored_by_type", "operator_name_or_id"):
        p = _good_packet()
        p[key] = "bot"
        r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
        assert r["verdict"] == PREVIEW_VERDICT_REJECTED, key
        assert any("automated_author" in x for x in r["reasons"]), key


def test_reject_granted_authority():
    for key in ("grants_capabilities", "authorizes", "granted_capabilities"):
        p = _good_packet()
        p[key] = ["crypto_d1_data_fetch"]
        r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
        assert r["verdict"] == PREVIEW_VERDICT_REJECTED, key
        assert any("grants_listed" in x for x in r["reasons"]), key


def test_reject_upstream_id_mismatch():
    p = _good_packet()
    p["upstream_next_step_id"] = "WRONG-ID"
    r = evaluate_crypto_d1_research_only_dry_run_preview(
        p, {"decision_packet_id": "B48-NS-1"}
    )
    assert r["verdict"] == PREVIEW_VERDICT_REJECTED
    assert any("mismatch:upstream_next_step_id" in x for x in r["reasons"])


def test_no_mismatch_when_ref_absent():
    p = _good_packet()
    p["upstream_next_step_id"] = "ANYTHING"
    r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    assert r["verdict"] == PREVIEW_VERDICT_READY


def test_build_rejected_sets_reject_gate():
    p = _good_packet()
    p["allow_real_data_acquisition"] = True
    c = _build(_active_upstream(), p)
    assert c["dry_run_preview_verdict"] == PREVIEW_VERDICT_REJECTED
    assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_REJECTED


def test_reject_takes_priority_over_missing():
    p = _good_packet()
    del p["next_step_boundary"]
    p["allow_data_fetch"] = True
    r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    assert r["verdict"] == PREVIEW_VERDICT_REJECTED


def test_reject_takes_priority_over_park():
    p = _good_packet()
    p["operator_decision"] = "parked"
    p["allow_data_fetch"] = True
    r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    assert r["verdict"] == PREVIEW_VERDICT_REJECTED


# --- 9: PARKED -------------------------------------------------------------

def test_park_via_flag():
    for flag in ("park", "parked", "defer", "deferred", "hold"):
        p = _good_packet()
        p[flag] = True
        r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
        assert r["verdict"] == PREVIEW_VERDICT_PARKED, flag


def test_park_via_operator_decision():
    p = _good_packet()
    p["operator_decision"] = "deferred"
    r = evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    assert r["verdict"] == PREVIEW_VERDICT_PARKED


def test_build_parked_sets_park_gate():
    p = _good_packet()
    p["decision"] = "park"
    c = _build(_active_upstream(), p)
    assert c["dry_run_preview_verdict"] == PREVIEW_VERDICT_PARKED
    assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_DRY_RUN_PREVIEW_PARKED


# --- 10: no verdict unlocks anything real ----------------------------------

def test_no_verdict_authorizes_or_executes():
    cases = [
        _good_packet(),                                   # READY
        {**_good_packet(), "allow_data_fetch": True},     # REJECTED
        {**_good_packet(), "park": True},                 # PARKED
        {},                                               # NEEDS_MORE_INFO
    ]
    for pkt in cases:
        c = _build(_active_upstream(), pkt)
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["human_approval_required"] is True
        for flag in _AUTH_FLAGS:
            assert c[flag] is False, flag
        assert all(v is False for v in c["safety_posture"].values())
    # Inactive too.
    c = build_crypto_d1_research_only_dry_run_preview_contract({}, {})
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    for flag in _AUTH_FLAGS:
        assert c[flag] is False, flag
    assert all(v is False for v in c["safety_posture"].values())


def test_contract_mode_always_research_only():
    assert _build()["mode"] == "RESEARCH_ONLY"
    assert build_crypto_d1_research_only_dry_run_preview_contract(
        {}, {}
    )["mode"] == "RESEARCH_ONLY"


def test_contract_stage_always_preview_only():
    assert _build()["stage"] == (
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_ONLY"
    )
    assert build_crypto_d1_research_only_dry_run_preview_contract(
        {}, {}
    )["stage"] == "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_ONLY"


def test_blocked_capabilities_present_and_nonempty():
    c = _build()
    assert len(c["preview_blocked_capabilities"]) >= 1
    assert len(c["blocked_capabilities"]) >= 1
    assert tuple(c["remaining_real_world_capabilities_blocked"]) == (
        REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


def test_no_verdict_carries_real_capability_marker():
    # No build output exposes a truthy 'allow_*' / executes-dry-run capability.
    for pkt in (_good_packet(), {}, {**_good_packet(), "park": True}):
        c = _build(_active_upstream(), pkt)
        for flag in PREVIEW_FORBIDDEN_ALLOW_FLAGS:
            assert c.get(flag) in (None, False), flag


# --- 11: validation --------------------------------------------------------

def test_validate_public_matches_embedded():
    c = _build()
    v = validate_crypto_d1_research_only_dry_run_preview_contract(c)
    assert v == c["validation"]
    assert v["valid"] is True


def test_validate_rejects_tampered_schema():
    c = _build()
    c["schema_version"] = "tampered"
    v = validate_crypto_d1_research_only_dry_run_preview_contract(c)
    assert v["valid"] is False
    assert v["schema_version_ok"] is False


def test_validate_rejects_missing_field():
    c = _build()
    del c["safety_posture"]
    v = validate_crypto_d1_research_only_dry_run_preview_contract(c)
    assert v["valid"] is False
    assert "safety_posture" in v["missing_required_fields"]


def test_validate_rejects_executes_true():
    c = _build()
    c["executes"] = True
    v = validate_crypto_d1_research_only_dry_run_preview_contract(c)
    assert v["valid"] is False


def test_validate_rejects_tampered_posture():
    c = _build()
    c["safety_posture"]["prohibited_data_fetch"] = True
    v = validate_crypto_d1_research_only_dry_run_preview_contract(c)
    assert v["valid"] is False
    assert v["safety_all_false"] is False


def test_validate_handles_garbage():
    for bad in (None, {}, [], "x", 7):
        v = validate_crypto_d1_research_only_dry_run_preview_contract(bad)
        assert v["valid"] is False


# --- 12: determinism + mutation isolation ----------------------------------

def test_build_is_deterministic():
    a = _build()
    b = _build()
    a.pop("crypto_d1_post_boundary_next_step_contract", None)
    b.pop("crypto_d1_post_boundary_next_step_contract", None)
    assert a == b


def test_evaluate_is_deterministic():
    p = _good_packet()
    assert (
        evaluate_crypto_d1_research_only_dry_run_preview(p, {})
        == evaluate_crypto_d1_research_only_dry_run_preview(p, {})
    )


def test_safety_posture_copy_is_isolated():
    c = _build()
    c["safety_posture"]["prohibited_data_fetch"] = True
    assert all(v is False for v in PREVIEW_SAFETY_POSTURE.values())
    assert all(v is False for v in _build()["safety_posture"].values())


def test_input_packet_not_mutated():
    p = _good_packet()
    snapshot = dict(p)
    _build(_active_upstream(), p)
    assert p == snapshot


# --- 13: markdown ----------------------------------------------------------

def test_markdown_nonempty_and_titled():
    md = render_crypto_d1_research_only_dry_run_preview_contract_markdown(
        _build()
    )
    assert isinstance(md, str)
    assert md.startswith(
        "# Strategy Factory Crypto-D1 Research-Only Dry-Run Preview Contract"
    )
    assert "RESEARCH_ONLY" in md
    assert "Executes: False" in md


def test_markdown_handles_minimal_contract():
    md = render_crypto_d1_research_only_dry_run_preview_contract_markdown({})
    assert isinstance(md, str) and len(md) > 0


# --- 14: pure stdlib import-root audit -------------------------------------

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


# --- 15: forbidden-surface + no-IO audit -----------------------------------

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


# --- 16: commander_2_safety allowlist --------------------------------------

def test_commander_2_safety_allowlist_includes_new_paths():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert (
        '"sparta_commander/strategy_factory_crypto_d1_research_only_dry_run_'
        'preview_contract.py"' in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_research_only_dry_run_preview_'
        'contract.py"' in src
    )

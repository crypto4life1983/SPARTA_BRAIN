"""Tests for the Strategy Factory Crypto-D1 Post-Boundary Research-Only
Next-Step Contract (Bundle 48).

Bundle 48 is a PURE, stdlib-only, read-only *paper decision contract* builder.
It consumes a Bundle 47 crypto-d1 human-approved offline acquisition execution
boundary contract and, only when that boundary is active + READY + carries the
Bundle 47 ready next-gate, evaluates a proposed post-boundary next-step decision
packet and returns a deterministic verdict describing which research-only future
contract should be drafted next -- or whether the lane should be parked or
rejected. It acquires nothing, executes nothing, and unlocks nothing real.

Coverage:
- schema / label / status / state constants stable
- verdict + gate constants stable; ordering
- activation strictly gated on Bundle 47 active + READY + ready-gate
- every verdict path: PROCEED, NEEDS_MORE_INFO, REJECTED, PARKED, AWAIT
- each REJECTED category (forbidden allow flag, relaxed prohibition, disallowed
  enum value, automated author, granted authority, boundary mismatch)
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

from sparta_commander.strategy_factory_crypto_d1_post_boundary_research_only_next_step_contract import (  # noqa: E501
    NEXT_STEP_SCHEMA_VERSION,
    DEFAULT_NEXT_STEP_LABEL,
    NEXT_STEP_STATUS,
    NEXT_STEP_SAFETY_POSTURE,
    NEXT_STEP_STATE_ACTIVE,
    NEXT_STEP_STATE_BLOCKED,
    NEXT_STEP_VERDICT_PROCEED,
    NEXT_STEP_VERDICT_NEEDS_MORE_INFO,
    NEXT_STEP_VERDICT_REJECTED,
    NEXT_STEP_VERDICT_PARKED,
    NEXT_STEP_VERDICT_AWAIT,
    ALLOWED_NEXT_STEP_VERDICTS,
    UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_VERDICT,
    UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_NEXT_GATE,
    POST_BOUNDARY_NEXT_REQUIRED_ACTION,
    POST_BOUNDARY_CURRENT_STAGE,
    NEXT_STEP_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REQUIRED,
    NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED,
    NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_FIX_REQUIRED,
    NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_PARKED,
    NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REJECTED,
    NEXT_GATE_AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_CONTRACT,  # noqa: E501
    REQUIRED_NEXT_STEP_FIELDS,
    NEXT_STEP_REQUIRED_TEXT_FIELDS,
    NEXT_STEP_REQUIRED_PROHIBITIONS,
    NEXT_STEP_REQUIRED_AFFIRMATIONS,
    NEXT_STEP_FORBIDDEN_ALLOW_FLAGS,
    ALLOWED_NEXT_CONTRACT_MODES,
    ALLOWED_NEXT_CONTRACT_TYPES,
    ALLOWED_NEXT_CONTRACT_SCOPES,
    ALLOWED_PROPOSED_NEXT_CONTRACTS,
    AUTOMATED_APPROVAL_MARKERS,
    REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    evaluate_crypto_d1_post_boundary_research_only_next_step,
    build_crypto_d1_post_boundary_research_only_next_step_contract,
    validate_crypto_d1_post_boundary_research_only_next_step_contract,
    render_crypto_d1_post_boundary_research_only_next_step_contract_markdown,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_post_boundary_research_only_next_step_contract.py"  # noqa: E501
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

def _active_boundary(ref=None):
    """A Bundle-47-shaped contract that is active + READY + ready-gate."""
    return {
        "crypto_d1_execution_boundary_contract_active": True,
        "execution_boundary_verdict": UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_VERDICT,  # noqa: E501
        "next_gate": UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_NEXT_GATE,
        "evaluated_execution_boundary_packet": (
            ref if ref is not None else {"boundary_packet_id": "B47-PKT-1"}
        ),
        "idea_id": "IDEA-1",
        "title": "Crypto-D1 lane",
        "asset_lane": "crypto",
        "timeframe_lane": "1d",
    }


def _good_packet():
    """A complete, safe, research-only post-boundary next-step packet."""
    p = {
        "decision_packet_id": "DP-1",
        "upstream_boundary_id": "B47-PKT-1",
        "approved_boundary_stage": "CRYPTO_D1_EXECUTION_BOUNDARY_ONLY",
        "proposed_next_contract": (
            "crypto_d1_research_only_dry_run_preview_contract"
        ),
        "proposed_next_contract_scope": "dry_run_preview_only",
        "proposed_next_contract_mode": "research_only",
        "proposed_next_contract_type": "dry_run_preview",
        "allowed_research_only_outputs": "preview markdown only",
        "next_step_reason": (
            "define a research-only dry-run preview, no execution, no data"
        ),
    }
    for flag in NEXT_STEP_REQUIRED_PROHIBITIONS + NEXT_STEP_REQUIRED_AFFIRMATIONS:
        p[flag] = True
    return p


def _build(boundary=None, packet=None):
    return build_crypto_d1_post_boundary_research_only_next_step_contract(
        boundary if boundary is not None else _active_boundary(),
        packet if packet is not None else _good_packet(),
    )


# --- 1: schema / label / status / state constants --------------------------

def test_schema_version_stable():
    assert NEXT_STEP_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_post_boundary_research_only_next_step_"
        "contract.v1"
    )


def test_label_and_status_stable():
    assert DEFAULT_NEXT_STEP_LABEL == (
        "Strategy Factory Crypto-D1 Post-Boundary Research-Only Next-Step "
        "Contract"
    )
    assert NEXT_STEP_STATUS == (
        "READ_ONLY_CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT"
    )


def test_state_constants_stable():
    assert NEXT_STEP_STATE_ACTIVE == (
        "CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT_ACTIVE"
    )
    assert NEXT_STEP_STATE_BLOCKED == (
        "CRYPTO_D1_POST_BOUNDARY_RESEARCH_ONLY_NEXT_STEP_CONTRACT_BLOCKED"
    )


# --- 2: verdict / gate / upstream constants --------------------------------

def test_verdict_constants_stable():
    assert NEXT_STEP_VERDICT_PROCEED == (
        "PROCEED_TO_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT"
    )
    assert NEXT_STEP_VERDICT_NEEDS_MORE_INFO == "NEEDS_MORE_INFO"
    assert NEXT_STEP_VERDICT_REJECTED == "POST_BOUNDARY_REJECTED"
    assert NEXT_STEP_VERDICT_PARKED == "POST_BOUNDARY_PARKED"
    assert NEXT_STEP_VERDICT_AWAIT == (
        "AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_"
        "CONTRACT"
    )


def test_allowed_verdicts_order():
    assert ALLOWED_NEXT_STEP_VERDICTS == (
        NEXT_STEP_VERDICT_PROCEED,
        NEXT_STEP_VERDICT_NEEDS_MORE_INFO,
        NEXT_STEP_VERDICT_REJECTED,
        NEXT_STEP_VERDICT_PARKED,
        NEXT_STEP_VERDICT_AWAIT,
    )


def test_upstream_required_signal_constants():
    assert UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_VERDICT == (
        "EXECUTION_BOUNDARY_READY"
    )
    assert UPSTREAM_REQUIRED_EXECUTION_BOUNDARY_NEXT_GATE == (
        "CRYPTO_D1_OFFLINE_ACQUISITION_EXECUTION_SEPARATE_HUMAN_RUN_REQUIRED"
    )


def test_next_gate_constants_stable():
    assert NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED == (  # noqa: E501
        "CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED"
    )
    assert NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_FIX_REQUIRED == (
        "CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_FIX_REQUIRED"
    )
    assert NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_PARKED == (
        "CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_PARKED"
    )
    assert NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REJECTED == (
        "CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REJECTED"
    )
    assert NEXT_GATE_AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_CONTRACT == (  # noqa: E501
        "AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_"
        "CONTRACT"
    )


def test_post_boundary_action_and_stage_from_registry():
    assert POST_BOUNDARY_NEXT_REQUIRED_ACTION == (
        "DEFINE_NEXT_RESEARCH_ONLY_CRYPTO_D1_POST_BOUNDARY_CONTRACT"
    )
    assert "STILL_BLOCKED" in POST_BOUNDARY_CURRENT_STAGE


# --- 3: required field schedules -------------------------------------------

def test_required_text_fields():
    assert NEXT_STEP_REQUIRED_TEXT_FIELDS == (
        "decision_packet_id",
        "upstream_boundary_id",
        "approved_boundary_stage",
        "proposed_next_contract",
        "proposed_next_contract_scope",
        "proposed_next_contract_mode",
        "proposed_next_contract_type",
        "allowed_research_only_outputs",
        "next_step_reason",
    )


def test_required_prohibitions_complete():
    assert NEXT_STEP_REQUIRED_PROHIBITIONS == (
        "prohibited_real_data_acquisition",
        "prohibited_data_fetch",
        "prohibited_data_inspection",
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
    )


def test_required_affirmations():
    assert NEXT_STEP_REQUIRED_AFFIRMATIONS == (
        "human_operator_review_required",
        "research_only_acknowledgement",
        "no_execution_acknowledgement",
    )


def test_required_fields_is_union_in_order():
    assert REQUIRED_NEXT_STEP_FIELDS == (
        NEXT_STEP_REQUIRED_TEXT_FIELDS
        + NEXT_STEP_REQUIRED_PROHIBITIONS
        + NEXT_STEP_REQUIRED_AFFIRMATIONS
    )
    assert len(REQUIRED_NEXT_STEP_FIELDS) == 28


def test_allowed_enums_are_research_only():
    assert "research_only" in ALLOWED_NEXT_CONTRACT_MODES
    assert all("preview" in t or "dry_run" in t for t in ALLOWED_NEXT_CONTRACT_TYPES)  # noqa: E501
    assert all("preview" in s for s in ALLOWED_NEXT_CONTRACT_SCOPES)
    assert all(c.endswith("preview_contract") for c in ALLOWED_PROPOSED_NEXT_CONTRACTS)  # noqa: E501
    for banned in ("live", "paper", "real", "fetch", "acquire", "execute"):
        assert banned not in ALLOWED_NEXT_CONTRACT_MODES


# --- 4: safety posture all false -------------------------------------------

def test_safety_posture_all_false():
    assert isinstance(NEXT_STEP_SAFETY_POSTURE, dict)
    assert len(NEXT_STEP_SAFETY_POSTURE) >= 1
    assert all(v is False for v in NEXT_STEP_SAFETY_POSTURE.values())


# --- 5: activation gate (build) --------------------------------------------

def test_active_boundary_ready_activates():
    c = _build()
    assert c["crypto_d1_post_boundary_next_step_contract_active"] is True
    assert c["crypto_d1_post_boundary_next_step_contract_state"] == (
        NEXT_STEP_STATE_ACTIVE
    )
    assert c["post_boundary_next_step_required"] == (
        NEXT_STEP_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REQUIRED
    )


def test_inactive_when_boundary_not_active():
    b = _active_boundary()
    b["crypto_d1_execution_boundary_contract_active"] = False
    c = _build(b, _good_packet())
    assert c["crypto_d1_post_boundary_next_step_contract_active"] is False
    assert c["next_step_verdict"] == NEXT_STEP_VERDICT_AWAIT
    assert c["crypto_d1_post_boundary_next_step_contract_state"] == (
        NEXT_STEP_STATE_BLOCKED
    )


def test_inactive_when_wrong_boundary_verdict():
    b = _active_boundary()
    b["execution_boundary_verdict"] = "EXECUTION_BOUNDARY_NEEDS_MORE_INFO"
    c = _build(b, _good_packet())
    assert c["crypto_d1_post_boundary_next_step_contract_active"] is False
    assert c["next_step_verdict"] == NEXT_STEP_VERDICT_AWAIT


def test_inactive_when_wrong_next_gate():
    b = _active_boundary()
    b["next_gate"] = "CRYPTO_D1_EXECUTION_BOUNDARY_FIX_REQUIRED"
    c = _build(b, _good_packet())
    assert c["crypto_d1_post_boundary_next_step_contract_active"] is False
    assert c["next_step_verdict"] == NEXT_STEP_VERDICT_AWAIT


def test_inactive_for_empty_or_malformed_boundary():
    for bad in ({}, None, [], "x", 7):
        c = build_crypto_d1_post_boundary_research_only_next_step_contract(
            bad, _good_packet()
        )
        assert c["crypto_d1_post_boundary_next_step_contract_active"] is False
        assert c["next_step_verdict"] == NEXT_STEP_VERDICT_AWAIT
        assert c["next_gate"] == (
            NEXT_GATE_AWAIT_CRYPTO_D1_HUMAN_APPROVED_OFFLINE_ACQUISITION_EXECUTION_BOUNDARY_CONTRACT  # noqa: E501
        )


def test_await_ignores_packet_shape():
    # Even a dangerous packet stays AWAIT when boundary is inactive.
    bad = _good_packet()
    bad["allow_data_fetch"] = True
    c = build_crypto_d1_post_boundary_research_only_next_step_contract(
        {}, bad
    )
    assert c["next_step_verdict"] == NEXT_STEP_VERDICT_AWAIT
    assert c["crypto_d1_post_boundary_next_step_contract_active"] is False


# --- 6: evaluate verdict paths ---------------------------------------------

def test_evaluate_empty_packet_needs_more_info():
    r = evaluate_crypto_d1_post_boundary_research_only_next_step({}, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_NEEDS_MORE_INFO


def test_evaluate_good_packet_proceeds():
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(
        _good_packet(), {"boundary_packet_id": "B47-PKT-1"}
    )
    assert r["verdict"] == NEXT_STEP_VERDICT_PROCEED


def test_build_good_packet_proceeds_and_validates():
    c = _build()
    assert c["next_step_verdict"] == NEXT_STEP_VERDICT_PROCEED
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_RESEARCH_ONLY_DRY_RUN_PREVIEW_CONTRACT_REQUIRED
    )
    assert c["validation"]["valid"] is True


def test_missing_field_needs_more_info():
    p = _good_packet()
    del p["next_step_reason"]
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_NEEDS_MORE_INFO
    assert any("next_step_reason" in x for x in r["reasons"])


def test_missing_affirmation_needs_more_info():
    p = _good_packet()
    del p["no_execution_acknowledgement"]
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_NEEDS_MORE_INFO


def test_build_needs_more_info_sets_fix_gate():
    p = _good_packet()
    del p["decision_packet_id"]
    c = _build(_active_boundary(), p)
    assert c["next_step_verdict"] == NEXT_STEP_VERDICT_NEEDS_MORE_INFO
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_FIX_REQUIRED
    )


# --- 7: REJECTED categories ------------------------------------------------

def test_reject_each_forbidden_allow_flag():
    for flag in NEXT_STEP_FORBIDDEN_ALLOW_FLAGS:
        p = _good_packet()
        p[flag] = True
        r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
        assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED, flag
        assert any(flag in x for x in r["reasons"]), flag


def test_reject_relaxed_prohibition():
    p = _good_packet()
    p["prohibited_data_fetch"] = False
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED
    assert any("prohibition_relaxed" in x for x in r["reasons"])


def test_reject_relaxed_affirmation():
    p = _good_packet()
    p["no_execution_acknowledgement"] = False
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED


def test_reject_disallowed_mode():
    p = _good_packet()
    p["proposed_next_contract_mode"] = "live"
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED
    assert any("disallowed_value:proposed_next_contract_mode" in x
               for x in r["reasons"])


def test_reject_disallowed_type():
    p = _good_packet()
    p["proposed_next_contract_type"] = "live_execution"
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED


def test_reject_disallowed_scope():
    p = _good_packet()
    p["proposed_next_contract_scope"] = "real_data_fetch"
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED


def test_reject_disallowed_proposed_contract():
    p = _good_packet()
    p["proposed_next_contract"] = "crypto_d1_real_data_acquisition_contract"
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED


def test_reject_automated_author():
    for key in ("decision_author_type", "author_type", "decision_method",
                "decision_source", "authored_by_type", "operator_name_or_id"):
        p = _good_packet()
        p[key] = "bot"
        r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
        assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED, key
        assert any("automated_author" in x for x in r["reasons"]), key


def test_reject_granted_authority():
    for key in ("grants_capabilities", "authorizes", "granted_capabilities"):
        p = _good_packet()
        p[key] = ["crypto_d1_data_fetch"]
        r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
        assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED, key
        assert any("grants_listed" in x for x in r["reasons"]), key


def test_reject_boundary_mismatch():
    p = _good_packet()
    p["upstream_boundary_id"] = "WRONG-ID"
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(
        p, {"boundary_packet_id": "B47-PKT-1"}
    )
    assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED
    assert any("mismatch:upstream_boundary_id" in x for x in r["reasons"])


def test_build_rejected_sets_reject_gate():
    p = _good_packet()
    p["allow_real_data_acquisition"] = True
    c = _build(_active_boundary(), p)
    assert c["next_step_verdict"] == NEXT_STEP_VERDICT_REJECTED
    assert c["next_gate"] == (
        NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_REJECTED
    )


def test_reject_takes_priority_over_missing():
    # Dangerous AND incomplete -> still REJECTED.
    p = _good_packet()
    del p["next_step_reason"]
    p["allow_data_fetch"] = True
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED


def test_reject_takes_priority_over_park():
    p = _good_packet()
    p["operator_decision"] = "parked"
    p["allow_data_fetch"] = True
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_REJECTED


# --- 8: PARKED -------------------------------------------------------------

def test_park_via_flag():
    for flag in ("park", "parked", "defer", "deferred", "hold"):
        p = _good_packet()
        p[flag] = True
        r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
        assert r["verdict"] == NEXT_STEP_VERDICT_PARKED, flag


def test_park_via_operator_decision():
    p = _good_packet()
    p["operator_decision"] = "deferred"
    r = evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    assert r["verdict"] == NEXT_STEP_VERDICT_PARKED


def test_build_parked_sets_park_gate():
    p = _good_packet()
    p["decision"] = "park"
    c = _build(_active_boundary(), p)
    assert c["next_step_verdict"] == NEXT_STEP_VERDICT_PARKED
    assert c["next_gate"] == NEXT_GATE_CRYPTO_D1_POST_BOUNDARY_NEXT_STEP_PARKED


# --- 9: no verdict unlocks anything real -----------------------------------

def test_no_verdict_authorizes_or_executes():
    cases = [
        _good_packet(),                                   # PROCEED
        {**_good_packet(), "allow_data_fetch": True},     # REJECTED
        {**_good_packet(), "park": True},                 # PARKED
        {},                                               # NEEDS_MORE_INFO
    ]
    for pkt in cases:
        c = _build(_active_boundary(), pkt)
        assert c["read_only"] is True
        assert c["executes"] is False
        assert c["human_approval_required"] is True
        for flag in _AUTH_FLAGS:
            assert c[flag] is False, flag
        assert all(v is False for v in c["safety_posture"].values())
    # Inactive too.
    c = build_crypto_d1_post_boundary_research_only_next_step_contract({}, {})
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["human_approval_required"] is True
    for flag in _AUTH_FLAGS:
        assert c[flag] is False, flag
    assert all(v is False for v in c["safety_posture"].values())


def test_contract_mode_always_research_only():
    assert _build()["mode"] == "RESEARCH_ONLY"
    assert build_crypto_d1_post_boundary_research_only_next_step_contract(
        {}, {}
    )["mode"] == "RESEARCH_ONLY"


def test_blocked_capabilities_present_and_nonempty():
    c = _build()
    assert len(c["next_step_blocked_capabilities"]) >= 1
    assert len(c["blocked_capabilities"]) >= 1
    assert tuple(c["remaining_real_world_capabilities_blocked"]) == (
        REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


# --- 10: validation --------------------------------------------------------

def test_validate_public_matches_embedded():
    c = _build()
    v = validate_crypto_d1_post_boundary_research_only_next_step_contract(c)
    assert v == c["validation"]
    assert v["valid"] is True


def test_validate_rejects_tampered_schema():
    c = _build()
    c["schema_version"] = "tampered"
    v = validate_crypto_d1_post_boundary_research_only_next_step_contract(c)
    assert v["valid"] is False
    assert v["schema_version_ok"] is False


def test_validate_rejects_missing_field():
    c = _build()
    del c["safety_posture"]
    v = validate_crypto_d1_post_boundary_research_only_next_step_contract(c)
    assert v["valid"] is False
    assert "safety_posture" in v["missing_required_fields"]


def test_validate_rejects_executes_true():
    c = _build()
    c["executes"] = True
    v = validate_crypto_d1_post_boundary_research_only_next_step_contract(c)
    assert v["valid"] is False


def test_validate_handles_garbage():
    for bad in (None, {}, [], "x", 7):
        v = validate_crypto_d1_post_boundary_research_only_next_step_contract(
            bad
        )
        assert v["valid"] is False


# --- 11: determinism + mutation isolation ----------------------------------

def test_build_is_deterministic():
    a = _build()
    b = _build()
    a.pop("crypto_d1_execution_boundary_contract", None)
    b.pop("crypto_d1_execution_boundary_contract", None)
    assert a == b


def test_evaluate_is_deterministic():
    p = _good_packet()
    assert (
        evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
        == evaluate_crypto_d1_post_boundary_research_only_next_step(p, {})
    )


def test_safety_posture_copy_is_isolated():
    c = _build()
    c["safety_posture"]["prohibited_data_fetch"] = True
    assert all(v is False for v in NEXT_STEP_SAFETY_POSTURE.values())
    assert all(v is False for v in _build()["safety_posture"].values())


def test_input_packet_not_mutated():
    p = _good_packet()
    snapshot = dict(p)
    _build(_active_boundary(), p)
    assert p == snapshot


# --- 12: markdown ----------------------------------------------------------

def test_markdown_nonempty_and_titled():
    md = render_crypto_d1_post_boundary_research_only_next_step_contract_markdown(  # noqa: E501
        _build()
    )
    assert isinstance(md, str)
    assert md.startswith(
        "# Strategy Factory Crypto-D1 Post-Boundary Research-Only Next-Step"
    )
    assert "RESEARCH_ONLY" in md
    assert "Executes: False" in md


def test_markdown_handles_minimal_contract():
    md = render_crypto_d1_post_boundary_research_only_next_step_contract_markdown(  # noqa: E501
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
        '"sparta_commander/strategy_factory_crypto_d1_post_boundary_research_'
        'only_next_step_contract.py"' in src
    )
    assert (
        '"tests/test_strategy_factory_crypto_d1_post_boundary_research_only_'
        'next_step_contract.py"' in src
    )

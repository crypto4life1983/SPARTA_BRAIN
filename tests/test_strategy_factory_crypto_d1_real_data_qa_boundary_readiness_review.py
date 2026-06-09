"""Tests for the Crypto-D1 Real Data QA Boundary Decision Readiness Review
(Block 166).

The review is a pure, stdlib-only, read-only paper review. It answers exactly
one research-only question, on paper: are we ready to ASK the human operator to
approve the first controlled, read-only Real Data QA step? It assesses a static
caller-supplied summary into exactly ONE of two outcomes
(READY_FOR_HUMAN_BOUNDARY_DECISION / HOLD_NEEDS_MORE_PREP) and authorizes /
unlocks nothing under either outcome -- even READY only means "the prep is sound
enough to put the decision in front of a human." These tests assert the schema,
the ten readiness items, the READY-only-when-all-pass model, every missing-prep
HOLD case, the safety-violation tripwire (any authorization / gate-unlock /
promotion / executable field forces HOLD with a recorded violation), the
all-capability-flags-False / gates-locked posture, the mission-flow truth sync
against the live status module, determinism, isolation, validation, render, AST
purity, and the two additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import copy
import pathlib

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_boundary_readiness_review import (  # noqa: E501
    BOUNDARY_READINESS_REVIEW_AUTHORIZATION_FLAGS,
    BOUNDARY_READINESS_REVIEW_CORE_RULE,
    BOUNDARY_READINESS_REVIEW_CURRENT_STAGE,
    BOUNDARY_READINESS_REVIEW_EXECUTABLE_SIGNAL_FIELDS,
    BOUNDARY_READINESS_REVIEW_FORBIDDEN_PROMOTION_REQUEST_FLAGS,
    BOUNDARY_READINESS_REVIEW_FORBIDDEN_TRADE_TERMS,
    BOUNDARY_READINESS_REVIEW_GATE_LOCK_FLAGS,
    BOUNDARY_READINESS_REVIEW_GATE_UNLOCK_REQUEST_FLAGS,
    BOUNDARY_READINESS_REVIEW_ITEM_IDS,
    BOUNDARY_READINESS_REVIEW_ITEMS,
    BOUNDARY_READINESS_REVIEW_LABEL,
    BOUNDARY_READINESS_REVIEW_MISSION_FLOW_CURRENT_STAGE,
    BOUNDARY_READINESS_REVIEW_MISSION_FLOW_NEXT_REQUIRED_ACTION,
    BOUNDARY_READINESS_REVIEW_MODE,
    BOUNDARY_READINESS_REVIEW_NEXT_REQUIRED_ACTION,
    BOUNDARY_READINESS_REVIEW_OUTCOMES,
    BOUNDARY_READINESS_REVIEW_SAFETY_POSTURE,
    BOUNDARY_READINESS_REVIEW_SCHEMA_VERSION,
    BOUNDARY_READINESS_REVIEW_STATUS,
    DEFAULT_SAMPLE_BOUNDARY_READINESS_INPUT,
    OUTCOME_HOLD,
    OUTCOME_READY,
    assess_real_data_qa_boundary_readiness,
    build_crypto_d1_real_data_qa_boundary_readiness_review,
    render_crypto_d1_real_data_qa_boundary_readiness_review_markdown,
    validate_crypto_d1_real_data_qa_boundary_readiness_review,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_real_data_qa_boundary_readiness_review.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_real_data_qa_boundary_readiness_review.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_real_data_qa_boundary_readiness_review.py"
)

_ASSESS = assess_real_data_qa_boundary_readiness
_BUILD = build_crypto_d1_real_data_qa_boundary_readiness_review
_VALIDATE = validate_crypto_d1_real_data_qa_boundary_readiness_review
_RENDER = render_crypto_d1_real_data_qa_boundary_readiness_review_markdown


def _ready_input(**overrides):
    """A payload where all ten readiness items pass and no unsafe flag is set, so
    the assessment reaches READY unless an override degrades it."""
    payload = copy.deepcopy(DEFAULT_SAMPLE_BOUNDARY_READINESS_INPUT)
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert BOUNDARY_READINESS_REVIEW_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_real_data_qa_boundary_readiness_review.v1"
    )
    assert BOUNDARY_READINESS_REVIEW_LABEL == (
        "Block 166 - Crypto-D1 Real Data QA Boundary Readiness Review"
    )
    assert BOUNDARY_READINESS_REVIEW_STATUS == (
        "READ_ONLY_CRYPTO_D1_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW"
    )
    assert BOUNDARY_READINESS_REVIEW_MODE == "RESEARCH_ONLY"
    assert "NEVER unlocks Real Data QA" in BOUNDARY_READINESS_REVIEW_CORE_RULE


def test_next_action_and_stage_are_build_only():
    assert BOUNDARY_READINESS_REVIEW_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW"
    )
    assert BOUNDARY_READINESS_REVIEW_CURRENT_STAGE == (
        "CRYPTO_D1_REAL_DATA_QA_BOUNDARY_READINESS_REVIEW_REQUIRED"
    )


def test_outcomes_are_exactly_two_ready_or_hold():
    assert BOUNDARY_READINESS_REVIEW_OUTCOMES == (OUTCOME_READY, OUTCOME_HOLD)
    assert OUTCOME_READY == "READY_FOR_HUMAN_BOUNDARY_DECISION"
    assert OUTCOME_HOLD == "HOLD_NEEDS_MORE_PREP"


def test_ten_review_items_are_exactly_the_spec_items():
    assert len(BOUNDARY_READINESS_REVIEW_ITEM_IDS) == 10
    assert BOUNDARY_READINESS_REVIEW_ITEM_IDS == (
        "boundary_contract_registered",
        "human_approval_packet_registered",
        "boundary_decision_registered",
        "jarvis_milestones_shown",
        "provider_fetch_modules_parked",
        "offline_arc_on_hold",
        "no_active_execution_surface",
        "no_fetch_qa_backtest_occurred",
        "gates_blocked_locked",
        "next_decision_is_read_only_qa_only",
    )
    for item_id, label in BOUNDARY_READINESS_REVIEW_ITEMS:
        assert isinstance(label, str) and label


def test_safety_posture_three_true_facts_all_else_false():
    posture = BOUNDARY_READINESS_REVIEW_SAFETY_POSTURE
    assert posture["read_only"] is True
    assert posture["research_only"] is True
    assert posture["human_approval_required"] is True
    assert posture["executes"] is False
    for key, value in posture.items():
        if key in ("read_only", "research_only", "human_approval_required"):
            continue
        assert value is False, key


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert (
        BOUNDARY_READINESS_REVIEW_MISSION_FLOW_CURRENT_STAGE
        == status.CURRENT_STAGE
    )
    assert (
        BOUNDARY_READINESS_REVIEW_MISSION_FLOW_NEXT_REQUIRED_ACTION
        == status.NEXT_REQUIRED_ACTION
    )


# --------------------------------------------------------------------------- #
# Readiness model
# --------------------------------------------------------------------------- #
def test_default_sample_is_ready():
    result = _ASSESS(DEFAULT_SAMPLE_BOUNDARY_READINESS_INPUT)
    assert result["outcome"] == OUTCOME_READY
    assert result["ready"] is True
    assert result["ready_for_human_boundary_decision"] is True
    assert result["failed_item_ids"] == []
    assert len(result["passed_item_ids"]) == 10
    assert result["unsafe_flag_hits"] == []
    assert result["safety_violation"] is False
    # READY still authorizes and unlocks nothing.
    assert result["authorizes_nothing"] is True
    assert result["unlocks_real_data_qa"] is False
    assert result["crosses_boundary"] is False


def test_default_build_is_ready():
    review = _BUILD()
    assert review["outcome"] == OUTCOME_READY
    assert review["ready"] is True


def test_each_missing_readiness_item_forces_hold():
    boolean_items = [
        item_id
        for item_id in BOUNDARY_READINESS_REVIEW_ITEM_IDS
        if item_id != "gates_blocked_locked"
    ]
    for item_id in boolean_items:
        result = _ASSESS(_ready_input(**{item_id: False}))
        assert result["outcome"] == OUTCOME_HOLD, item_id
        assert item_id in result["failed_item_ids"], item_id
        assert result["ready"] is False, item_id


def test_missing_boundary_contract_is_hold():
    result = _ASSESS(_ready_input(boundary_contract_registered=False))
    assert result["outcome"] == OUTCOME_HOLD
    assert "boundary_contract_registered" in result["failed_item_ids"]
    assert result["safety_violation"] is False


def test_missing_human_approval_packet_is_hold():
    result = _ASSESS(_ready_input(human_approval_packet_registered=False))
    assert result["outcome"] == OUTCOME_HOLD
    assert "human_approval_packet_registered" in result["failed_item_ids"]


def test_missing_boundary_decision_is_hold():
    result = _ASSESS(_ready_input(boundary_decision_registered=False))
    assert result["outcome"] == OUTCOME_HOLD
    assert "boundary_decision_registered" in result["failed_item_ids"]


# --------------------------------------------------------------------------- #
# Safety-violation tripwire: an unsafe flag can never be READY
# --------------------------------------------------------------------------- #
def test_authorization_flag_forces_hold_with_violation():
    for flag in BOUNDARY_READINESS_REVIEW_AUTHORIZATION_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_HOLD, flag
        assert result["safety_violation"] is True, flag
        assert flag in result["unsafe_flag_hits"], flag
        assert result["ready"] is False, flag


def test_gate_unlock_request_forces_hold_with_violation():
    for flag in BOUNDARY_READINESS_REVIEW_GATE_UNLOCK_REQUEST_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_HOLD, flag
        assert result["safety_violation"] is True, flag
        assert flag in result["unsafe_flag_hits"], flag


def test_unlocking_a_locked_gate_forces_hold_with_violation():
    for flag in BOUNDARY_READINESS_REVIEW_GATE_LOCK_FLAGS:
        result = _ASSESS(_ready_input(**{flag: False}))
        assert result["outcome"] == OUTCOME_HOLD, flag
        assert result["safety_violation"] is True, flag
        assert ("unlocked:" + flag) in result["unsafe_flag_hits"], flag
        # the derived gates_blocked_locked item also fails
        assert "gates_blocked_locked" in result["failed_item_ids"], flag


def test_forbidden_promotion_request_forces_hold_with_violation():
    for flag in BOUNDARY_READINESS_REVIEW_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_HOLD, flag
        assert result["safety_violation"] is True, flag
        assert flag in result["unsafe_flag_hits"], flag


def test_executable_signal_field_forces_hold_with_violation():
    for field in BOUNDARY_READINESS_REVIEW_EXECUTABLE_SIGNAL_FIELDS:
        result = _ASSESS(_ready_input(**{field: "do something"}))
        assert result["outcome"] == OUTCOME_HOLD, field
        assert result["safety_violation"] is True, field
        assert field in result["unsafe_flag_hits"], field


def test_unsafe_flag_also_fails_no_active_execution_surface_item():
    result = _ASSESS(_ready_input(authorizes_trading=True))
    assert "no_active_execution_surface" in result["failed_item_ids"]


def test_mission_flow_misalignment_fails_read_only_qa_item():
    result = _ASSESS(_ready_input(mission_flow_current_stage="SOMETHING_ELSE"))
    assert result["outcome"] == OUTCOME_HOLD
    assert result["mission_flow_aligned"] is False
    assert "next_decision_is_read_only_qa_only" in result["failed_item_ids"]


def test_safety_violation_with_missing_item_still_holds():
    result = _ASSESS(
        _ready_input(boundary_contract_registered=False, authorizes_trading=True)
    )
    assert result["outcome"] == OUTCOME_HOLD
    assert result["safety_violation"] is True


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_assessment_is_deterministic():
    payload = _ready_input()
    assert _ASSESS(payload) == _ASSESS(payload)


def test_build_does_not_mutate_caller_payload():
    payload = _ready_input()
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


def test_default_sample_is_not_shared_between_builds():
    c1 = _BUILD()
    c2 = _BUILD()
    c1["failed_item_ids"].append("tampered")
    assert "tampered" not in c2["failed_item_ids"]
    assert DEFAULT_SAMPLE_BOUNDARY_READINESS_INPUT[
        "boundary_contract_registered"
    ] is True


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def test_default_review_validates():
    verdict = _VALIDATE(_BUILD())
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == []
    assert verdict["no_trade_language"] is True
    assert verdict["flags_false"] is True
    assert verdict["gates_locked"] is True
    assert verdict["authorizes_nothing"] is True
    assert verdict["mission_flow_refs_ok"] is True
    assert verdict["ten_review_items"] is True
    assert verdict["ready_only_when_all_pass"] is True
    assert verdict["real_data_qa_stays_blocked"] is True
    assert verdict["outcomes_ok"] is True


def test_every_outcome_path_validates():
    payloads = [
        DEFAULT_SAMPLE_BOUNDARY_READINESS_INPUT,            # ready
        _ready_input(boundary_contract_registered=False),  # hold (missing prep)
        _ready_input(authorizes_trading=True),             # hold (violation)
        _ready_input(real_data_qa_blocked=False),          # hold (gate unlock)
        _ready_input(mission_flow_current_stage="X"),      # hold (misaligned)
    ]
    for payload in payloads:
        verdict = _VALIDATE(_BUILD(payload))
        assert verdict["valid"] is True, payload


def test_validate_rejects_tampered_review():
    review = _BUILD()
    review["executes"] = True
    verdict = _VALIDATE(review)
    assert verdict["valid"] is False
    assert verdict["executes_false"] is False


def test_validate_rejects_unlocked_real_data_qa():
    review = _BUILD()
    review["unlocks_real_data_qa"] = True
    verdict = _VALIDATE(review)
    assert verdict["valid"] is False
    assert verdict["real_data_qa_stays_blocked"] is False


def test_validate_rejects_ready_without_all_items_passing():
    review = _BUILD(_ready_input(boundary_contract_registered=False))
    assert review["outcome"] == OUTCOME_HOLD
    review["ready"] = True
    verdict = _VALIDATE(review)
    assert verdict["valid"] is False
    assert verdict["ready_only_when_all_pass"] is False


def test_validate_rejects_ready_with_safety_violation():
    review = _BUILD(_ready_input(authorizes_trading=True))
    assert review["outcome"] == OUTCOME_HOLD
    review["ready"] = True
    verdict = _VALIDATE(review)
    assert verdict["valid"] is False
    assert verdict["ready_only_when_all_pass"] is False


def test_ready_review_unlocks_no_gate():
    review = _BUILD(_ready_input())
    assert review["outcome"] == OUTCOME_READY
    assert review["ready"] is True
    assert review["promotes_beyond_boundary"] is False
    assert review["unlocks_real_data_qa"] is False
    assert review["unlocks_baseline_backtest"] is False
    assert review["unlocks_paper_trading"] is False
    assert review["unlocks_micro_live"] is False
    assert review["crosses_boundary"] is False
    assert review["real_data_qa_blocked"] is True
    assert review["baseline_backtest_blocked"] is True
    assert review["paper_trading_gate_locked"] is True
    assert review["micro_live_gate_locked"] is True
    assert review["authorizes_nothing"] is True
    assert review["requires_separate_future_human_approved_step"] is True


def test_all_capability_flags_false_under_every_outcome():
    flags = (
        "authorizes_trading",
        "authorizes_data_fetch",
        "authorizes_backtest",
        "authorizes_paper_trading",
        "authorizes_live_trading",
        "authorizes_broker_exchange",
        "authorizes_automation",
        "authorizes_real_world_action",
        "unlocks_downstream_gate",
        "unlocks_real_data_qa",
        "unlocks_baseline_backtest",
        "unlocks_paper_trading",
        "unlocks_micro_live",
        "crosses_boundary",
        "promotes_beyond_boundary",
        "executes",
    )
    for payload in (None, _ready_input(authorizes_trading=True)):
        review = _BUILD(payload)
        for flag in flags:
            assert review[flag] is False, (payload, flag)
        for gate in BOUNDARY_READINESS_REVIEW_GATE_LOCK_FLAGS:
            assert review[gate] is True, (payload, gate)


# --------------------------------------------------------------------------- #
# Render
# --------------------------------------------------------------------------- #
def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith(
        "# Crypto-D1 Real Data QA Boundary Readiness Review"
    )
    assert "## Readiness Review" in text
    assert "## No Execution Authorization" in text
    assert "## Operator Next Step" in text


def test_generated_guidance_has_no_execution_verbs():
    review = _BUILD()
    blob = " ".join(
        str(review.get(k, ""))
        for k in ("operator_next_step", "operator_notes", "core_rule")
    )
    blob += " " + " ".join(
        str(s) for s in review.get("human_operator_required_next_steps", [])
    )
    tokens = set(
        "".join(
            ch if (ch.isalnum() or ch == "_") else " " for ch in blob.lower()
        ).split()
    )
    for term in BOUNDARY_READINESS_REVIEW_FORBIDDEN_TRADE_TERMS:
        assert term not in tokens, term


# --------------------------------------------------------------------------- #
# AST purity: stdlib-only, no I/O, no forbidden imports
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORTS = {"__future__", "typing"}
_FORBIDDEN_CALL_NAMES = {"open", "__import__", "eval", "exec", "compile", "input"}
_FORBIDDEN_MODULE_TOKENS = {
    "os",
    "sys",
    "subprocess",
    "socket",
    "shutil",
    "pathlib",
    "requests",
    "http",
    "urllib",
    "importlib",
    "pandas",
    "numpy",
    "ccxt",
    "datetime",
    "time",
    "random",
    "pickle",
    "sqlite3",
}


def _module_ast():
    return ast.parse(_MODPATH.read_text(encoding="utf-8"))


def test_module_imports_are_stdlib_typing_only():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in _ALLOWED_IMPORTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORTS, node.module


def test_module_has_no_forbidden_calls():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in _FORBIDDEN_CALL_NAMES, node.func.id


def test_module_has_no_forbidden_module_tokens():
    imported_roots = set()
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported_roots.add((node.module or "").split(".")[0])
    assert not (imported_roots & _FORBIDDEN_MODULE_TOKENS)


def test_module_does_not_import_the_registry():
    # The review must stay pure so the registry can import IT (no circular dep).
    src = _MODPATH.read_text(encoding="utf-8")
    assert "strategy_factory_mission_flow_bundle_registry" not in src
    assert "strategy_factory_mission_flow_status" not in src


def test_building_writes_no_files(tmp_path):
    before = set(tmp_path.iterdir())
    _BUILD()
    _BUILD(_ready_input())
    after = set(tmp_path.iterdir())
    assert before == after


# --------------------------------------------------------------------------- #
# commander_2_safety allowlist (exactly two additive lines)
# --------------------------------------------------------------------------- #
def test_commander_safety_allowlist_includes_the_two_additive_entries():
    from sparta_commander.commander_2_safety import (
        COMMANDER_2_MODULES,
        COMMANDER_2_TESTS,
    )

    assert _MODULE_ALLOWLIST_LINE in COMMANDER_2_MODULES
    assert _TEST_ALLOWLIST_LINE in COMMANDER_2_TESTS
    assert COMMANDER_2_MODULES.count(_MODULE_ALLOWLIST_LINE) == 1
    assert COMMANDER_2_TESTS.count(_TEST_ALLOWLIST_LINE) == 1


def test_commander_safety_only_two_new_lines_for_this_module():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert src.count(_MODULE_ALLOWLIST_LINE) == 1
    assert src.count(_TEST_ALLOWLIST_LINE) == 1

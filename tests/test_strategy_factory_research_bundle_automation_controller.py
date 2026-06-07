"""Tests for the SPARTA Research Bundle Automation Controller (Block 137).

The controller is a pure, stdlib-only, read-only RESEARCH_ONLY workflow advisor.
It reasons over a static, caller-supplied mission-flow status summary and returns
the next SAFE research-only step, the allowed / forbidden paths, the scoped tests,
the hard-stop rules, and an approval packet -- authorizing and unlocking nothing.
These tests assert the schema, the next-action classification model, the
boundary-hold behavior (the live state sits at the human Real Data QA boundary),
the unsafe-flag refusals, every expected output, safety_flags_all_false, the
mission-flow truth sync against the live status module, determinism, isolation,
validation, render, AST purity, and the two additive commander_2_safety allowlist
entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_research_bundle_automation_controller import (  # noqa: E501
    CONTROLLER_AUTHORIZATION_FLAGS,
    CONTROLLER_CORE_RULE,
    CONTROLLER_FORBIDDEN_PATHS,
    CONTROLLER_FORBIDDEN_TRADE_TERMS,
    CONTROLLER_GATE_LOCK_FLAGS,
    CONTROLLER_GATE_UNLOCK_REQUEST_FLAGS,
    CONTROLLER_HARD_STOP_RULES,
    CONTROLLER_LABEL,
    CONTROLLER_MODE,
    CONTROLLER_RECOMMENDATIONS,
    CONTROLLER_SAFETY_FLAGS,
    CONTROLLER_SCHEMA_VERSION,
    CONTROLLER_STATUS,
    DEFAULT_CONTROLLER_INPUT,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
    NEXT_ACTION_BUILD,
    NEXT_ACTION_CATEGORIES,
    NEXT_ACTION_HOLD,
    NEXT_ACTION_HUMAN_BOUNDARY,
    NEXT_ACTION_REGISTER,
    NEXT_ACTION_UI_SYNC,
    PAPER_LIVE_STATE_LOCKED,
    REAL_DATA_QA_STATE_BLOCKED,
    RECOMMENDATION_HOLD_OR_PREPARE,
    allowed_paths_for_bundle,
    assess_research_bundle_automation,
    build_research_bundle_automation_decision,
    render_research_bundle_automation_decision_markdown,
    scoped_tests_for_bundle,
    validate_research_bundle_automation_decision,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_research_bundle_automation_controller.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_research_bundle_automation_controller.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_research_bundle_automation_controller.py"
)

_ASSESS = assess_research_bundle_automation
_BUILD = build_research_bundle_automation_decision
_VALIDATE = validate_research_bundle_automation_decision
_RENDER = render_research_bundle_automation_decision_markdown


def _flow_input(**overrides):
    """A safe, non-boundary input: the mission flow has moved OFF the Real Data QA
    boundary to a generic research stage, all gates locked, no contract built yet,
    UI in sync. This reaches BUILD_RESEARCH_CONTRACT unless an override changes
    it. Boundary tests override current_stage / next_required_action."""
    payload = {
        "current_stage": "CRYPTO_D1_NEXT_RESEARCH_STAGE",
        "next_required_action": "BUILD_NEXT_RESEARCH_CONTRACT",
        "next_bundle_type": "research_contract",
        "next_bundle_slug": "crypto_d1_example_research",
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "contract_built": False,
        "contract_registered": False,
        "ui_in_sync": True,
    }
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert CONTROLLER_SCHEMA_VERSION == (
        "strategy_factory_research_bundle_automation_controller.v1"
    )
    assert CONTROLLER_LABEL == (
        "Block 137 - SPARTA Research Bundle Automation Controller"
    )
    assert CONTROLLER_STATUS == "READ_ONLY_RESEARCH_BUNDLE_AUTOMATION_CONTROLLER"
    assert CONTROLLER_MODE == "RESEARCH_ONLY"
    assert "NEVER crosses a real-world boundary" in CONTROLLER_CORE_RULE


def test_next_action_categories_are_exactly_the_five_in_precedence_order():
    assert NEXT_ACTION_CATEGORIES == (
        NEXT_ACTION_HOLD,
        NEXT_ACTION_HUMAN_BOUNDARY,
        NEXT_ACTION_UI_SYNC,
        NEXT_ACTION_REGISTER,
        NEXT_ACTION_BUILD,
    )


def test_recommendations_include_the_boundary_hold_or_prepare():
    assert RECOMMENDATION_HOLD_OR_PREPARE in CONTROLLER_RECOMMENDATIONS
    assert RECOMMENDATION_HOLD_OR_PREPARE == "HOLD_OR_PREPARE_RESEARCH_ONLY_PACKET"


def test_real_data_qa_and_paper_live_state_constants():
    assert REAL_DATA_QA_STATE_BLOCKED == "BLOCKED"
    assert PAPER_LIVE_STATE_LOCKED == "LOCKED"


def test_hard_stop_rules_are_the_full_verbatim_set():
    assert "Never execute git commands." in CONTROLLER_HARD_STOP_RULES
    assert "Never stage files." in CONTROLLER_HARD_STOP_RULES
    assert "Never commit." in CONTROLLER_HARD_STOP_RULES
    assert "Never push." in CONTROLLER_HARD_STOP_RULES
    assert "Never fetch data." in CONTROLLER_HARD_STOP_RULES
    assert "Never run QA / backtest." in CONTROLLER_HARD_STOP_RULES
    assert "Never call broker / exchange." in CONTROLLER_HARD_STOP_RULES
    assert "Never place orders." in CONTROLLER_HARD_STOP_RULES
    assert "Never trigger paper / live trading." in CONTROLLER_HARD_STOP_RULES
    assert (
        "Never write runtime / dashboard outputs." in CONTROLLER_HARD_STOP_RULES
    )
    assert "Never unlock real_data_qa." in CONTROLLER_HARD_STOP_RULES
    assert "Never unlock baseline_backtest." in CONTROLLER_HARD_STOP_RULES
    assert "Never unlock paper / micro-live." in CONTROLLER_HARD_STOP_RULES
    assert (
        "Never turn any real-world capability flag True."
        in CONTROLLER_HARD_STOP_RULES
    )


def test_safety_flags_posture_true_facts_all_capability_false():
    flags = CONTROLLER_SAFETY_FLAGS
    assert flags["read_only"] is True
    assert flags["research_only"] is True
    assert flags["human_approval_required"] is True
    posture_true = {"read_only", "research_only", "human_approval_required"}
    for key, value in flags.items():
        if key in posture_true:
            continue
        assert value is False, key


# --------------------------------------------------------------------------- #
# Mission-flow truth sync
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# Boundary-hold behavior (the live state sits at the boundary)
# --------------------------------------------------------------------------- #
def test_default_input_holds_at_the_human_boundary():
    result = _ASSESS(DEFAULT_CONTROLLER_INPUT)
    assert result["next_action_category"] == NEXT_ACTION_HUMAN_BOUNDARY
    assert result["automation_allowed"] is False
    assert result["recommended_next_action"] == RECOMMENDATION_HOLD_OR_PREPARE
    assert result["real_data_qa_state"] == REAL_DATA_QA_STATE_BLOCKED
    assert result["paper_live_state"] == PAPER_LIVE_STATE_LOCKED
    assert result["at_boundary"] is True


def test_default_build_holds_at_the_human_boundary():
    decision = _BUILD()
    assert decision["next_action_category"] == NEXT_ACTION_HUMAN_BOUNDARY
    assert decision["automation_allowed"] is False
    assert decision["recommended_next_action"] == RECOMMENDATION_HOLD_OR_PREPARE
    assert decision["real_data_qa_state"] == REAL_DATA_QA_STATE_BLOCKED
    assert decision["paper_live_state"] == PAPER_LIVE_STATE_LOCKED


def test_boundary_by_stage_holds():
    result = _ASSESS(
        _flow_input(current_stage=MISSION_FLOW_CURRENT_STAGE)
    )
    assert result["next_action_category"] == NEXT_ACTION_HUMAN_BOUNDARY
    assert result["automation_allowed"] is False
    assert result["recommended_next_action"] == RECOMMENDATION_HOLD_OR_PREPARE


def test_boundary_by_next_required_action_holds():
    result = _ASSESS(
        _flow_input(next_required_action=MISSION_FLOW_NEXT_REQUIRED_ACTION)
    )
    assert result["next_action_category"] == NEXT_ACTION_HUMAN_BOUNDARY
    assert result["automation_allowed"] is False


# --------------------------------------------------------------------------- #
# Next-action classification (off the boundary)
# --------------------------------------------------------------------------- #
def test_unbuilt_contract_recommends_build():
    result = _ASSESS(_flow_input(contract_built=False))
    assert result["next_action_category"] == NEXT_ACTION_BUILD
    assert result["recommended_next_action"] == NEXT_ACTION_BUILD
    assert result["automation_allowed"] is True


def test_built_unregistered_contract_recommends_register():
    result = _ASSESS(
        _flow_input(contract_built=True, contract_registered=False)
    )
    assert result["next_action_category"] == NEXT_ACTION_REGISTER
    assert result["recommended_next_action"] == NEXT_ACTION_REGISTER
    assert result["automation_allowed"] is True


def test_registered_contract_with_pending_ui_recommends_ui_sync():
    result = _ASSESS(
        _flow_input(
            contract_built=True, contract_registered=True, ui_in_sync=False
        )
    )
    assert result["next_action_category"] == NEXT_ACTION_UI_SYNC
    assert result["recommended_next_action"] == NEXT_ACTION_UI_SYNC
    # UI sync is a dashboard write -> the controller will NOT automate it.
    assert result["automation_allowed"] is False


def test_fully_done_bundle_holds():
    result = _ASSESS(
        _flow_input(
            contract_built=True, contract_registered=True, ui_in_sync=True
        )
    )
    assert result["next_action_category"] == NEXT_ACTION_HOLD
    assert result["recommended_next_action"] == NEXT_ACTION_HOLD
    assert result["automation_allowed"] is False


# --------------------------------------------------------------------------- #
# Unsafe-flag refusals (force a HOLD regardless of stage)
# --------------------------------------------------------------------------- #
def test_authorization_flag_forces_unsafe_hold():
    for flag in CONTROLLER_AUTHORIZATION_FLAGS:
        result = _ASSESS(_flow_input(**{flag: True}))
        assert result["next_action_category"] == NEXT_ACTION_HOLD, flag
        assert result["automation_allowed"] is False, flag
        assert flag in result["unsafe_flag_hits"], flag


def test_gate_unlock_request_forces_unsafe_hold():
    for flag in CONTROLLER_GATE_UNLOCK_REQUEST_FLAGS:
        result = _ASSESS(_flow_input(**{flag: True}))
        assert result["next_action_category"] == NEXT_ACTION_HOLD, flag
        assert result["automation_allowed"] is False, flag


def test_unlocking_a_locked_gate_forces_unsafe_hold():
    for flag in CONTROLLER_GATE_LOCK_FLAGS:
        result = _ASSESS(_flow_input(**{flag: False}))
        assert result["next_action_category"] == NEXT_ACTION_HOLD, flag
        assert result["automation_allowed"] is False, flag
        assert ("unlocked:" + flag) in result["unsafe_flag_hits"], flag


def test_unsafe_hold_takes_precedence_over_boundary():
    # At the boundary AND with an unsafe flag -> still an unsafe HOLD.
    result = _ASSESS(
        _flow_input(
            current_stage=MISSION_FLOW_CURRENT_STAGE, authorizes_trading=True
        )
    )
    assert result["next_action_category"] == NEXT_ACTION_HOLD
    assert result["automation_allowed"] is False


# --------------------------------------------------------------------------- #
# Expected outputs are all present
# --------------------------------------------------------------------------- #
def test_decision_exposes_every_expected_output():
    decision = _BUILD(_flow_input())
    for key in (
        "automation_allowed",
        "recommended_next_action",
        "approval_packet_text",
        "allowed_paths",
        "forbidden_paths",
        "scoped_tests",
        "hard_stop_rules",
        "safety_flags_all_false",
        "real_data_qa_state",
        "paper_live_state",
        "operator_summary",
    ):
        assert key in decision, key
    assert decision["safety_flags_all_false"] is True
    assert isinstance(decision["approval_packet_text"], str)
    assert decision["approval_packet_text"]
    assert isinstance(decision["operator_summary"], str)
    assert decision["operator_summary"]


def test_allowed_paths_are_only_module_test_and_safety():
    paths = allowed_paths_for_bundle("research_contract", "crypto_d1_example")
    assert len(paths) == 3
    assert paths[0].startswith("sparta_commander/strategy_factory_")
    assert paths[0].endswith(".py")
    assert paths[1].startswith("tests/test_strategy_factory_")
    assert "commander_2_safety.py" in paths[2]


def test_scoped_tests_include_its_own_test_and_safety_test():
    tests = scoped_tests_for_bundle("research_contract", "crypto_d1_example")
    assert len(tests) == 2
    assert tests[0].startswith("tests/test_strategy_factory_")
    assert tests[1] == "tests/test_sparta_commander_2_safety.py"


def test_no_allowed_path_falls_under_a_forbidden_prefix():
    decision = _BUILD(_flow_input())
    for path in decision["allowed_paths"]:
        for forbidden in CONTROLLER_FORBIDDEN_PATHS:
            assert not str(path).startswith(forbidden), (path, forbidden)


def test_forbidden_paths_cover_the_dangerous_surfaces():
    fp = CONTROLLER_FORBIDDEN_PATHS
    assert "data/" in fp
    assert "reports/" in fp
    assert "runtime/" in fp
    assert "templates/" in fp
    assert "brain_memory/projects/trading_bot/decisions.md" in fp
    assert "brain_memory/projects/trading_bot/lessons.md" in fp


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_assessment_is_deterministic():
    payload = _flow_input()
    assert _ASSESS(payload) == _ASSESS(payload)


def test_build_does_not_mutate_caller_payload():
    import copy

    payload = _flow_input()
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


def test_default_input_is_not_shared_between_builds():
    d1 = _BUILD()
    d2 = _BUILD()
    d1["allowed_paths"].append("tampered")
    assert "tampered" not in d2["allowed_paths"]
    assert DEFAULT_CONTROLLER_INPUT["contract_built"] is False


# --------------------------------------------------------------------------- #
# Validation / render
# --------------------------------------------------------------------------- #
def test_default_decision_validates():
    verdict = _VALIDATE(_BUILD())
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == []
    assert verdict["no_trade_language"] is True
    assert verdict["flags_false"] is True
    assert verdict["gates_locked"] is True
    assert verdict["authorizes_nothing"] is True
    assert verdict["mission_flow_refs_ok"] is True
    assert verdict["hard_stops_ok"] is True
    assert verdict["safety_flags_all_false_ok"] is True
    assert verdict["boundary_hold_ok"] is True
    assert verdict["states_blocked_locked"] is True


def test_every_category_path_validates():
    payloads = [
        DEFAULT_CONTROLLER_INPUT,                                  # boundary
        _flow_input(),                                             # build
        _flow_input(contract_built=True),                         # register
        _flow_input(
            contract_built=True, contract_registered=True, ui_in_sync=False
        ),                                                         # ui sync
        _flow_input(
            contract_built=True, contract_registered=True, ui_in_sync=True
        ),                                                         # hold
        _flow_input(authorizes_trading=True),                     # unsafe hold
    ]
    for payload in payloads:
        verdict = _VALIDATE(_BUILD(payload))
        assert verdict["valid"] is True, payload


def test_validate_rejects_tampered_decision():
    decision = _BUILD()
    decision["executes"] = True
    verdict = _VALIDATE(decision)
    assert verdict["valid"] is False
    assert verdict["executes_false"] is False


def test_validate_rejects_unlocked_real_data_qa():
    decision = _BUILD()
    decision["unlocks_real_data_qa"] = True
    verdict = _VALIDATE(decision)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_automation_allowed_at_boundary():
    decision = _BUILD()
    assert decision["next_action_category"] == NEXT_ACTION_HUMAN_BOUNDARY
    decision["automation_allowed"] = True
    verdict = _VALIDATE(decision)
    assert verdict["valid"] is False
    assert verdict["boundary_hold_ok"] is False
    assert verdict["automation_consistent"] is False


def test_build_decision_keeps_all_gates_locked_in_every_category():
    for payload in (
        DEFAULT_CONTROLLER_INPUT,
        _flow_input(),
        _flow_input(contract_built=True),
        _flow_input(
            contract_built=True, contract_registered=True, ui_in_sync=True
        ),
    ):
        decision = _BUILD(payload)
        assert decision["real_data_qa_blocked"] is True
        assert decision["baseline_backtest_blocked"] is True
        assert decision["paper_trading_gate_locked"] is True
        assert decision["micro_live_gate_locked"] is True
        assert decision["unlocks_real_data_qa"] is False
        assert decision["crosses_boundary"] is False
        assert decision["authorizes_nothing"] is True
        assert decision["real_data_qa_state"] == REAL_DATA_QA_STATE_BLOCKED
        assert decision["paper_live_state"] == PAPER_LIVE_STATE_LOCKED


def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith("# SPARTA Research Bundle Automation Controller")
    assert "## Operator Summary" in text
    assert "## Allowed Paths" in text
    assert "## Forbidden Paths" in text
    assert "## Scoped Tests" in text
    assert "## Hard Stop Rules" in text
    assert "## Approval Packet" in text


def test_generated_guidance_has_no_execution_verbs():
    decision = _BUILD(_flow_input())
    blob = " ".join(
        str(decision.get(k, ""))
        for k in (
            "approval_packet_text",
            "operator_summary",
            "core_rule",
            "reason",
        )
    )
    blob += " " + " ".join(str(s) for s in decision.get("operator_checklist", []))
    tokens = set(
        "".join(
            c if (c.isalnum() or c == "_") else " " for c in blob.lower()
        ).split()
    )
    for term in CONTROLLER_FORBIDDEN_TRADE_TERMS:
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


def test_building_writes_no_files(tmp_path):
    before = set(tmp_path.iterdir())
    _BUILD()
    _BUILD(_flow_input())
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

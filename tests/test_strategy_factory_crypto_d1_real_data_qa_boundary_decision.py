"""Tests for the Crypto-D1 Human-Controlled Real Data QA Boundary Decision
(Block 158).

The module is a pure, stdlib-only, read-only DECISION layer. It consumes an
explicit human approval input at the parked mission-flow boundary and resolves
exactly one outcome:

  - BLOCK                      : input tried to authorize / unlock / promote /
                                 execute, or the mission flow is not parked.
  - HOLD_AWAIT                 : no explicit human approval present (default).
  - PERMIT_NEXT_PLANNING_STEP  : approval token present -> permits ONLY the next
                                 read-only planning packet, never execution.

These tests assert: schema / label / mode / status; the parked mission-flow truth
synced against the live status module; the three outcome paths (HOLD_AWAIT with no
approval, PERMIT_NEXT_PLANNING_STEP with the approval token, BLOCK on forbidden
flags and on mission-flow misalignment); that even a PERMIT keeps real_data_qa
BLOCKED / baseline BLOCKED / paper-live LOCKED and unlocks nothing; every
capability flag False; what-permit-grants and what-remains-forbidden sections;
determinism / mutation isolation; no trade language; no secret values; validation;
render; AST purity (only typing / sparta_commander roots, no os / network /
credential modules, no filesystem-write capability); and the two additive
commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_boundary_decision import (  # noqa: E501
    DECISION_APPROVAL_REQUIRED_TOKEN,
    DECISION_CORE_RULE,
    DECISION_FORBIDDEN_FLAGS,
    DECISION_FORBIDDEN_TRADE_TERMS,
    DECISION_LABEL,
    DECISION_MODE,
    DECISION_OPTIONS,
    DECISION_OUTCOMES,
    DECISION_SAFETY_POSTURE,
    DECISION_SCHEMA_VERSION,
    DECISION_STATUS,
    DEFAULT_DECISION_INPUT,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
    OUTCOME_BLOCK,
    OUTCOME_HOLD_AWAIT,
    OUTCOME_PERMIT_NEXT_PLANNING_STEP,
    WHAT_PERMIT_GRANTS,
    WHAT_REMAINS_FORBIDDEN,
    build_real_data_qa_boundary_decision,
    render_real_data_qa_boundary_decision_markdown,
    validate_real_data_qa_boundary_decision,
)

_BUILD = build_real_data_qa_boundary_decision
_VALIDATE = validate_real_data_qa_boundary_decision
_RENDER = render_real_data_qa_boundary_decision_markdown

_APPROVED_INPUT = {
    **DEFAULT_DECISION_INPUT,
    "human_decision": DECISION_APPROVAL_REQUIRED_TOKEN,
}

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_real_data_qa_boundary_decision.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_real_data_qa_boundary_decision.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_real_data_qa_boundary_decision.py"
)


# --------------------------------------------------------------------------- #
# schema / identity
# --------------------------------------------------------------------------- #
def test_schema_label_mode_status():
    assert DECISION_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_real_data_qa_boundary_decision.v1"
    )
    assert DECISION_LABEL == (
        "Block 158 - Crypto-D1 Human-Controlled Real Data QA Boundary Decision"
    )
    assert DECISION_MODE == "RESEARCH_ONLY"
    assert DECISION_STATUS == "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"


def test_build_carries_identity():
    d = _BUILD()
    assert d["schema_version"] == DECISION_SCHEMA_VERSION
    assert d["label"] == DECISION_LABEL
    assert d["mode"] == DECISION_MODE
    assert d["status"] == DECISION_STATUS
    assert d["core_rule"] == DECISION_CORE_RULE


def test_outcomes_constant_in_precedence_order():
    assert DECISION_OUTCOMES == (
        OUTCOME_BLOCK,
        OUTCOME_HOLD_AWAIT,
        OUTCOME_PERMIT_NEXT_PLANNING_STEP,
    )


# --------------------------------------------------------------------------- #
# mission-flow truth synced against the live status module
# --------------------------------------------------------------------------- #
def test_parked_mission_flow_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert MISSION_FLOW_NEXT_REQUIRED_ACTION == status.NEXT_REQUIRED_ACTION
    assert (
        MISSION_FLOW_CURRENT_STAGE
        == "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
    )
    assert (
        MISSION_FLOW_NEXT_REQUIRED_ACTION
        == "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
    )


def test_build_anchors_parked_stage():
    d = _BUILD()
    assert d["mission_flow_current_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert d["mission_flow_next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION
    assert d["mission_flow_aligned"] is True
    bd = d["boundary_decision"]
    assert bd["parked_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert bd["parked_next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# outcome: HOLD_AWAIT with no approval (default)
# --------------------------------------------------------------------------- #
def test_default_outcome_is_hold_await():
    d = _BUILD()
    assert d["outcome"] == OUTCOME_HOLD_AWAIT
    assert d["approval_present"] is False
    assert d["permits_next_planning_step"] is False
    assert d["next_permitted_step"] is None
    assert d["safe"] is True
    assert d["hold_reasons"]
    assert d["block_reasons"] == []


def test_decline_and_await_both_hold():
    for value in ("DECLINE", "AWAIT", "decline", "await", "maybe", "unknown_value"):
        d = _BUILD({**DEFAULT_DECISION_INPUT, "human_decision": value})
        assert d["outcome"] == OUTCOME_HOLD_AWAIT, value
        assert d["permits_next_planning_step"] is False, value
        assert d["real_data_qa_blocked"] is True, value
        assert d["unlocks_real_data_qa"] is False, value


# --------------------------------------------------------------------------- #
# outcome: PERMIT_NEXT_PLANNING_STEP with the approval token
# --------------------------------------------------------------------------- #
def test_approval_token_permits_only_next_planning_step():
    d = _BUILD(_APPROVED_INPUT)
    assert d["outcome"] == OUTCOME_PERMIT_NEXT_PLANNING_STEP
    assert d["approval_present"] is True
    assert d["permits_next_planning_step"] is True
    assert isinstance(d["next_permitted_step"], str) and d["next_permitted_step"]
    # the permitted next step is read-only planning only.
    blob = d["next_permitted_step"].lower()
    assert "read-only" in blob
    assert "plan" in blob
    # a permit is never a boundary crossing or an unlock.
    assert d["this_decision_authorizes_boundary_crossing"] is False
    assert d["authorizes_nothing"] is True


def test_permit_keeps_all_gates_blocked_and_locked():
    d = _BUILD(_APPROVED_INPUT)
    assert d["real_data_qa_state"] == "BLOCKED"
    assert d["baseline_backtest_state"] == "BLOCKED"
    assert d["paper_live_state"] == "LOCKED"
    assert d["real_data_qa_blocked"] is True
    assert d["baseline_backtest_blocked"] is True
    assert d["paper_trading_gate_locked"] is True
    assert d["micro_live_gate_locked"] is True
    assert d["unlocks_real_data_qa"] is False
    assert d["auto_unlocks_real_data_qa"] is False


def test_permit_requires_separate_future_human_approved_step():
    d = _BUILD(_APPROVED_INPUT)
    assert d["requires_separate_future_human_approved_step"] is True
    assert d["human_decision_required"] is True
    assert d["human_approval_required"] is True


def test_approval_token_with_forbidden_flag_still_blocks():
    d = _BUILD({**_APPROVED_INPUT, "unlock_real_data_qa": True})
    assert d["outcome"] == OUTCOME_BLOCK
    assert d["permits_next_planning_step"] is False
    assert d["real_data_qa_blocked"] is True
    assert d["unlocks_real_data_qa"] is False


# --------------------------------------------------------------------------- #
# outcome: BLOCK on forbidden flags / misalignment
# --------------------------------------------------------------------------- #
def test_each_forbidden_flag_blocks():
    for flag in DECISION_FORBIDDEN_FLAGS:
        d = _BUILD({**DEFAULT_DECISION_INPUT, flag: True})
        assert d["outcome"] == OUTCOME_BLOCK, flag
        assert d["safe"] is False, flag
        assert flag in d["forbidden_flag_hits"], flag
        # even a blocked input never flips a gate or a capability flag.
        assert d["real_data_qa_blocked"] is True
        assert d["unlocks_real_data_qa"] is False
        assert d["authorizes_nothing"] is True
        assert d["permits_next_planning_step"] is False


def test_mission_flow_misalignment_blocks():
    d = _BUILD(
        {**DEFAULT_DECISION_INPUT, "mission_flow_current_stage": "SOMEWHERE_ELSE"}
    )
    assert d["mission_flow_aligned"] is False
    assert d["outcome"] == OUTCOME_BLOCK
    assert d["safe"] is False
    assert d["real_data_qa_blocked"] is True


# --------------------------------------------------------------------------- #
# what permit grants / what remains forbidden
# --------------------------------------------------------------------------- #
def test_what_permit_grants_present_and_narrow():
    bd = _BUILD()["boundary_decision"]
    grants = bd["what_permit_grants"]
    assert grants == list(WHAT_PERMIT_GRANTS)
    assert len(grants) >= 1
    blob = " ".join(grants).lower()
    assert "read-only" in blob
    assert "plan" in blob


def test_what_remains_forbidden_covers_the_hard_lanes():
    forbidden = " ".join(
        _BUILD()["boundary_decision"]["what_remains_forbidden"]
    ).lower()
    assert forbidden == " ".join(WHAT_REMAINS_FORBIDDEN).lower()
    for needle in (
        "no data fetch",
        "no qa run",
        "no baseline",
        "no backtest",
        "no broker",
        "no paper",
        "no live",
        "auto-push",
        "no api",
        "no gate unlock",
    ):
        assert needle in forbidden, needle


def test_no_unlock_confirmation_block_locked():
    nuc = _BUILD(_APPROVED_INPUT)["boundary_decision"]["no_unlock_confirmation"]
    assert nuc["auto_unlocks_real_data_qa"] is False
    assert nuc["unlocks_real_data_qa"] is False
    assert nuc["unlocks_baseline_backtest"] is False
    assert nuc["unlocks_paper_trading"] is False
    assert nuc["unlocks_micro_live"] is False
    assert nuc["real_data_qa_state"] == "BLOCKED"
    assert nuc["baseline_backtest_state"] == "BLOCKED"
    assert nuc["paper_live_state"] == "LOCKED"


def test_approval_required_token_and_options():
    bd = _BUILD()["boundary_decision"]
    assert bd["approval_required_token"] == DECISION_APPROVAL_REQUIRED_TOKEN
    assert bd["decision_options"] == list(DECISION_OPTIONS)
    assert DECISION_APPROVAL_REQUIRED_TOKEN in DECISION_OPTIONS


# --------------------------------------------------------------------------- #
# capability flags
# --------------------------------------------------------------------------- #
def test_every_capability_flag_is_false_under_every_outcome():
    for payload in (DEFAULT_DECISION_INPUT, _APPROVED_INPUT,
                    {**DEFAULT_DECISION_INPUT, "place_order": True}):
        d = _BUILD(payload)
        for flag, value in DECISION_SAFETY_POSTURE.items():
            if value is False:
                assert d.get(flag) is False, (flag, d["outcome"])
        assert d["authorizes_nothing"] is True
        assert d["this_decision_authorizes_boundary_crossing"] is False


def test_safety_posture_passthrough():
    assert _BUILD()["safety_posture"] == DECISION_SAFETY_POSTURE
    for key in (
        "read_only",
        "research_only",
        "human_decision_required",
        "parked_at_boundary",
    ):
        assert DECISION_SAFETY_POSTURE[key] is True
    assert DECISION_SAFETY_POSTURE["executes"] is False
    assert DECISION_SAFETY_POSTURE["auto_unlocks_real_data_qa"] is False
    assert DECISION_SAFETY_POSTURE["performs_auto_push"] is False


# --------------------------------------------------------------------------- #
# determinism / mutation isolation
# --------------------------------------------------------------------------- #
def test_build_is_deterministic_and_isolated():
    a = _BUILD()
    b = _BUILD()
    assert a == b
    a["boundary_decision"]["what_remains_forbidden"].append("MUTATED")
    a["safety_posture"]["executes"] = True
    c = _BUILD()
    assert c["boundary_decision"]["what_remains_forbidden"] == list(
        WHAT_REMAINS_FORBIDDEN
    )
    assert c["safety_posture"]["executes"] is False


def test_default_input_not_mutated_by_build():
    snapshot = dict(DEFAULT_DECISION_INPUT)
    _BUILD()
    _BUILD(_APPROVED_INPUT)
    assert DEFAULT_DECISION_INPUT == snapshot


# --------------------------------------------------------------------------- #
# narrative purity
# --------------------------------------------------------------------------- #
def test_narrative_has_no_trade_language():
    for payload in (DEFAULT_DECISION_INPUT, _APPROVED_INPUT):
        d = _BUILD(payload)
        blob = " ".join(
            [
                d["operator_next_step"],
                d["decision_summary"],
                d["core_rule"],
                *d["human_operator_required_next_steps"],
            ]
        ).lower()
        tokens = set()
        word = []
        for ch in blob:
            if ch.isalnum() or ch == "_":
                word.append(ch)
            elif word:
                tokens.add("".join(word))
                word = []
        if word:
            tokens.add("".join(word))
        assert not (tokens & set(DECISION_FORBIDDEN_TRADE_TERMS))


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
def test_validate_each_outcome_is_valid():
    for payload in (
        DEFAULT_DECISION_INPUT,
        _APPROVED_INPUT,
        {**DEFAULT_DECISION_INPUT, "place_order": True},
    ):
        verdict = _VALIDATE(_BUILD(payload))
        assert verdict["valid"] is True, payload
        assert verdict["missing_fields"] == []
        for key, value in verdict.items():
            if key in ("valid", "missing_fields"):
                continue
            assert value is True, key


def test_validate_rejects_non_dict():
    assert _VALIDATE("not a decision")["valid"] is False


def test_validate_rejects_tampered_gate():
    d = _BUILD()
    d["real_data_qa_blocked"] = False
    verdict = _VALIDATE(d)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_validate_rejects_flipped_capability_flag():
    d = _BUILD()
    d["executes"] = True
    verdict = _VALIDATE(d)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_unlock_real_data_qa():
    d = _BUILD()
    d["unlocks_real_data_qa"] = True
    verdict = _VALIDATE(d)
    assert verdict["valid"] is False
    assert verdict["real_data_qa_stays_blocked"] is False


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_is_deterministic_markdown():
    d = _BUILD(_APPROVED_INPUT)
    md1 = _RENDER(d)
    md2 = _RENDER(d)
    assert md1 == md2
    assert md1.startswith(
        "# Crypto-D1 Human-Controlled Real Data QA Boundary Decision"
    )
    assert "## What A Present Approval Permits" in md1
    assert "## What Remains Forbidden" in md1
    assert "## No-Unlock Confirmation" in md1
    assert "BLOCKED" in md1
    assert "LOCKED" in md1


def test_render_handles_non_dict():
    assert _RENDER("x").startswith(
        "# Crypto-D1 Human-Controlled Real Data QA Boundary Decision"
    )


# --------------------------------------------------------------------------- #
# AST purity
# --------------------------------------------------------------------------- #
_ALLOWED_IMPORT_ROOTS = {"__future__", "typing", "sparta_commander"}
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
    "databento",
    "dotenv",
    "datetime",
    "time",
    "random",
    "pickle",
    "sqlite3",
}


def _module_ast():
    return ast.parse(_MODPATH.read_text(encoding="utf-8"))


def test_module_imports_are_within_allowed_roots():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in _ALLOWED_IMPORT_ROOTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORT_ROOTS, node.module


def test_module_imports_no_os_network_or_credential_modules():
    imported_roots = set()
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported_roots.add((node.module or "").split(".")[0])
    assert not (imported_roots & _FORBIDDEN_MODULE_TOKENS), (
        imported_roots & _FORBIDDEN_MODULE_TOKENS
    )


def test_module_never_reads_environment():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Attribute):
            assert node.attr not in {"environ", "getenv", "environb"}, node.attr


def test_module_has_no_eval_exec_import_dunder():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"eval", "exec", "compile", "__import__", "input"}


def test_module_has_no_filesystem_write_capability_of_its_own():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "open(" not in src
    assert ".write_text(" not in src
    assert ".write_bytes(" not in src
    assert "write_json(" not in src
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id != "open"
            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"write_text", "write_bytes", "write_json"}


def test_building_writes_no_files(tmp_path):
    before = set(tmp_path.iterdir())
    _BUILD()
    _BUILD(_APPROVED_INPUT)
    _BUILD({**DEFAULT_DECISION_INPUT, "authorizes_trading": True})
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
    assert src.count(_MODULE_ALLOWLIST_LINE + '"') == 1
    assert src.count(_TEST_ALLOWLIST_LINE + '"') == 1

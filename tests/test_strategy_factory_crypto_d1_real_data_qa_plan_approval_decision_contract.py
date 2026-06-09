"""Tests for the Crypto-D1 Real Data QA Plan Approval Decision Contract (Block 172).

The module is a pure, stdlib-only, read-only APPROVAL/DENIAL contract for the
Block 171 Real Data QA Plan-Only Contract. A human records exactly one of four
decisions about the *plan*: APPROVE_PLAN_ONLY (approve the plan text/scope as a
future candidate), REJECT_PLAN, REQUEST_PLAN_REVISION, or KEEP_BOUNDARY_BLOCKED.
The single highest grant is APPROVE_PLAN_ONLY, which approves only the plan text
and scope; it approves no real_data_qa execution, crosses no boundary, and unlocks
no gate. It executes nothing, fetches nothing, inspects nothing, and writes
nothing.

These tests assert: schema / label / mode / status; the parked mission-flow truth
synced against the live status module; that a valid Block 171 plan can be approved
ONLY as APPROVE_PLAN_ONLY; that a missing / unsafe / tampered plan is rejected or
downgraded to a revision request; that forbidden decisions and forbidden-flag
inputs mark the contract unsafe without ever unlocking anything; gates BLOCKED /
LOCKED; every capability flag False; determinism / mutation isolation; no trade
language; no secret values; validation; render; AST purity (only typing /
sparta_commander roots, no os / network / credential modules, no filesystem-write
capability); and the two additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_plan_approval_decision_contract import (  # noqa: E501
    ALLOWED_DECISION_IDS,
    ALLOWED_DECISIONS,
    DECISION_CORE_RULE,
    DECISION_FORBIDDEN_FLAGS,
    DECISION_FORBIDDEN_TRADE_TERMS,
    DECISION_LABEL,
    DECISION_MODE,
    DECISION_SAFETY_POSTURE,
    DECISION_SCHEMA_VERSION,
    DECISION_STATUS,
    DEFAULT_DECISION_INPUT,
    EFFECTIVE_AWAITING,
    EFFECTIVE_REJECTED_UNSAFE,
    FORBIDDEN_DECISION_IDS,
    FORBIDDEN_DECISIONS,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
    assess_plan,
    assess_requested_decision,
    build_real_data_qa_plan_approval_decision,
    render_real_data_qa_plan_approval_decision_markdown,
    validate_real_data_qa_plan_approval_decision,
)
from sparta_commander.strategy_factory_crypto_d1_real_data_qa_plan_only_contract import (  # noqa: E501
    build_real_data_qa_plan_only_contract as _build_plan_171,
)

_BUILD = build_real_data_qa_plan_approval_decision
_VALIDATE = validate_real_data_qa_plan_approval_decision
_RENDER = render_real_data_qa_plan_approval_decision_markdown

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_real_data_qa_plan_approval_decision_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/"
    "strategy_factory_crypto_d1_real_data_qa_plan_approval_decision_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/"
    "test_strategy_factory_crypto_d1_real_data_qa_plan_approval_decision_contract.py"
)


def _approve(plan=None):
    return {**DEFAULT_DECISION_INPUT, "requested_decision": "APPROVE_PLAN_ONLY",
            "plan": plan}


# --------------------------------------------------------------------------- #
# schema / identity
# --------------------------------------------------------------------------- #
def test_schema_label_mode_status():
    assert DECISION_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_real_data_qa_plan_approval_decision_contract.v1"
    )
    assert DECISION_LABEL == (
        "Block 172 - Crypto-D1 Real Data QA Plan Approval Decision Contract"
    )
    assert DECISION_MODE == "RESEARCH_ONLY"
    assert DECISION_STATUS == "READ_ONLY_REAL_DATA_QA_PLAN_APPROVAL_DECISION"


def test_build_carries_identity():
    c = _BUILD()
    assert c["schema_version"] == DECISION_SCHEMA_VERSION
    assert c["label"] == DECISION_LABEL
    assert c["mode"] == DECISION_MODE
    assert c["status"] == DECISION_STATUS
    assert c["core_rule"] == DECISION_CORE_RULE


def test_allowed_and_forbidden_decision_ids():
    assert ALLOWED_DECISION_IDS == (
        "APPROVE_PLAN_ONLY",
        "REJECT_PLAN",
        "REQUEST_PLAN_REVISION",
        "KEEP_BOUNDARY_BLOCKED",
    )
    for needle in (
        "FETCH_DATA",
        "RUN_QA",
        "INSPECT_DATASETS",
        "UNLOCK_REAL_DATA_QA",
        "UNLOCK_BASELINE_BACKTEST",
        "UNLOCK_PAPER_LIVE",
        "ENABLE_BROKER_EXCHANGE",
        "ACCESS_CREDENTIALS",
        "GENERATE_SIGNALS_ORDERS",
        "WRITE_RUNTIME_DASHBOARD_STORAGE",
    ):
        assert needle in FORBIDDEN_DECISION_IDS, needle


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
    c = _BUILD()
    assert c["mission_flow_current_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert c["mission_flow_next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION
    assert c["mission_flow_aligned"] is True
    d = c["decision"]
    assert d["parked_stage"] == MISSION_FLOW_CURRENT_STAGE
    assert d["parked_next_required_action"] == MISSION_FLOW_NEXT_REQUIRED_ACTION


# --------------------------------------------------------------------------- #
# decision + plan assessment helpers
# --------------------------------------------------------------------------- #
def test_assess_requested_decision_classifies():
    none_a = assess_requested_decision(None)
    assert none_a["requested"] is None and none_a["allowed"] is False
    assert none_a["rejected"] is False

    for oid in ALLOWED_DECISION_IDS:
        a = assess_requested_decision(oid)
        assert a["allowed"] is True and a["rejected"] is False
        assert a["approves_execution"] is False
        assert a["crosses_boundary"] is False

    for oid in FORBIDDEN_DECISION_IDS:
        a = assess_requested_decision(oid)
        assert a["allowed"] is False and a["rejected"] is True
        assert a["approves_execution"] is False
        assert a["crosses_boundary"] is False

    bogus = assess_requested_decision("SOMETHING_ELSE")
    assert bogus["recognized"] is False
    assert bogus["allowed"] is False and bogus["rejected"] is True


def test_assess_plan_accepts_valid_block_171_plan():
    a = assess_plan(_build_plan_171())
    assert a["present"] is True
    assert a["label_ok"] is True
    assert a["schema_ok"] is True
    assert a["plan_safe"] is True
    assert a["valid"] is True
    assert a["plan_ok"] is True


def test_assess_plan_rejects_non_dict_and_tampered():
    assert assess_plan(None)["plan_ok"] is False
    assert assess_plan("nope")["plan_ok"] is False

    tampered = _build_plan_171()
    tampered["label"] = "not block 171"
    a = assess_plan(tampered)
    assert a["label_ok"] is False
    assert a["plan_ok"] is False

    unsafe = _build_plan_171()
    unsafe["safe"] = False
    assert assess_plan(unsafe)["plan_ok"] is False


# --------------------------------------------------------------------------- #
# REQUIRED PROOF: a valid Block 171 plan can be approved ONLY as APPROVE_PLAN_ONLY
# --------------------------------------------------------------------------- #
def test_valid_plan_approved_only_as_plan_only_default():
    # No supplied plan -> module builds a fresh, valid Block 171 plan.
    c = _BUILD(_approve(plan=None))
    assert c["effective_decision"] == "APPROVE_PLAN_ONLY"
    assert c["plan_approved"] is True
    assert c["approval_scope"] == "PLAN_TEXT_AND_SCOPE_ONLY"
    # The highest grant never crosses the boundary or approves execution.
    assert c["approves_real_data_qa_execution"] is False
    assert c["crosses_boundary"] is False
    assert c["this_contract_authorizes_boundary_crossing"] is False
    assert c["highest_grant_is_plan_text_and_scope_only"] is True
    assert c["authorizes_nothing_beyond_plan_text_and_scope"] is True
    assert c["safe"] is True


def test_valid_supplied_plan_approved_as_plan_only():
    c = _BUILD(_approve(plan=_build_plan_171()))
    assert c["effective_decision"] == "APPROVE_PLAN_ONLY"
    assert c["plan_approved"] is True
    assert c["approval_scope"] == "PLAN_TEXT_AND_SCOPE_ONLY"
    # Even an approval keeps every gate blocked/locked.
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_approval_never_unlocks_in_no_unlock_block():
    nuc = _BUILD(_approve())["decision"]["no_unlock_confirmation"]
    assert nuc["unlocks_real_data_qa"] is False
    assert nuc["unlocks_baseline_backtest"] is False
    assert nuc["unlocks_paper_trading"] is False
    assert nuc["unlocks_micro_live"] is False
    assert nuc["approves_real_data_qa_execution"] is False
    assert nuc["crosses_boundary"] is False
    assert nuc["real_data_qa_state"] == "BLOCKED"
    assert nuc["baseline_backtest_state"] == "BLOCKED"
    assert nuc["paper_live_state"] == "LOCKED"


# --------------------------------------------------------------------------- #
# REQUIRED PROOF: missing / unsafe / tampered plan is rejected or revision-requested
# --------------------------------------------------------------------------- #
def test_approve_with_missing_plan_downgrades_to_revision():
    c = _BUILD({**DEFAULT_DECISION_INPUT,
                "requested_decision": "APPROVE_PLAN_ONLY",
                "plan": {"not": "a real plan"}})
    assert c["effective_decision"] == "REQUEST_PLAN_REVISION"
    assert c["plan_approved"] is False
    assert c["approval_scope"] == "NONE"
    assert c["crosses_boundary"] is False


def test_approve_with_unsafe_plan_downgrades_to_revision():
    unsafe = _build_plan_171()
    unsafe["safe"] = False
    c = _BUILD(_approve(plan=unsafe))
    assert c["effective_decision"] == "REQUEST_PLAN_REVISION"
    assert c["plan_approved"] is False
    assert c["approval_scope"] == "NONE"


def test_approve_with_tampered_identity_downgrades_to_revision():
    tampered = _build_plan_171()
    tampered["schema_version"] = "evil.v9"
    c = _BUILD(_approve(plan=tampered))
    assert c["effective_decision"] == "REQUEST_PLAN_REVISION"
    assert c["plan_approved"] is False


def test_forbidden_decision_is_rejected_unsafe():
    for oid in FORBIDDEN_DECISION_IDS:
        c = _BUILD({**DEFAULT_DECISION_INPUT, "requested_decision": oid})
        assert c["effective_decision"] == EFFECTIVE_REJECTED_UNSAFE
        assert c["plan_approved"] is False
        assert c["safe"] is False
        assert c["crosses_boundary"] is False
        assert c["real_data_qa_blocked"] is True
        assert c["unlocks_real_data_qa"] is False


def test_unrecognized_decision_is_rejected_unsafe():
    c = _BUILD({**DEFAULT_DECISION_INPUT, "requested_decision": "WHATEVER"})
    assert c["effective_decision"] == EFFECTIVE_REJECTED_UNSAFE
    assert c["plan_approved"] is False
    assert c["safe"] is False


def test_no_decision_is_awaiting():
    c = _BUILD()
    assert c["effective_decision"] == EFFECTIVE_AWAITING
    assert c["plan_approved"] is False
    assert c["approval_scope"] == "NONE"
    assert c["safe"] is True


def test_reject_and_keep_blocked_pass_through_without_approval():
    for oid in ("REJECT_PLAN", "REQUEST_PLAN_REVISION", "KEEP_BOUNDARY_BLOCKED"):
        c = _BUILD({**DEFAULT_DECISION_INPUT, "requested_decision": oid})
        assert c["effective_decision"] == oid
        assert c["plan_approved"] is False
        assert c["approval_scope"] == "NONE"
        assert c["safe"] is True


# --------------------------------------------------------------------------- #
# REQUIRED PROOF: gates BLOCKED/LOCKED + capability flags False (every path)
# --------------------------------------------------------------------------- #
def test_top_level_gate_states_blocked_and_locked():
    c = _BUILD()
    assert c["real_data_qa_state"] == "BLOCKED"
    assert c["baseline_backtest_state"] == "BLOCKED"
    assert c["paper_live_state"] == "LOCKED"
    assert c["real_strategy_intake_state"] == "BLOCKED"
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_every_capability_flag_is_false_across_inputs():
    inputs = [
        None,
        _approve(),
        {**DEFAULT_DECISION_INPUT, "requested_decision": "FETCH_DATA"},
        {**DEFAULT_DECISION_INPUT, "requested_decision": "KEEP_BOUNDARY_BLOCKED"},
        {**DEFAULT_DECISION_INPUT, "authorizes_real_data_qa_execution": True},
        {**DEFAULT_DECISION_INPUT, "unlock_real_data_qa": True},
    ]
    for payload in inputs:
        c = _BUILD() if payload is None else _BUILD(payload)
        for flag, value in DECISION_SAFETY_POSTURE.items():
            if value is False:
                assert c.get(flag) is False, (flag, payload)
        assert c["approves_real_data_qa_execution"] is False
        assert c["crosses_boundary"] is False
        assert c["executes"] is False
        assert c["real_data_qa_blocked"] is True


def test_safety_posture_passthrough():
    assert _BUILD()["safety_posture"] == DECISION_SAFETY_POSTURE
    for key in (
        "read_only",
        "research_only",
        "decision_contract_only",
        "human_decision_required",
        "parked_at_boundary",
    ):
        assert DECISION_SAFETY_POSTURE[key] is True
    assert DECISION_SAFETY_POSTURE["executes"] is False
    assert DECISION_SAFETY_POSTURE["approves_real_data_qa_execution"] is False
    assert DECISION_SAFETY_POSTURE["crosses_boundary"] is False


# --------------------------------------------------------------------------- #
# forbidden-flag inputs mark unsafe (but never unlock anything)
# --------------------------------------------------------------------------- #
def test_default_contract_is_safe():
    c = _BUILD()
    assert c["safe"] is True
    assert c["forbidden_flag_hits"] == []


def test_each_forbidden_flag_marks_unsafe():
    for flag in DECISION_FORBIDDEN_FLAGS:
        c = _BUILD({**DEFAULT_DECISION_INPUT, flag: True})
        assert c["safe"] is False, flag
        assert flag in c["forbidden_flag_hits"], flag
        assert c["real_data_qa_blocked"] is True
        assert c["unlocks_real_data_qa"] is False
        assert c["crosses_boundary"] is False


def test_mission_flow_misalignment_marks_unsafe():
    c = _BUILD({**DEFAULT_DECISION_INPUT,
                "mission_flow_current_stage": "SOMEWHERE_ELSE"})
    assert c["mission_flow_aligned"] is False
    assert c["safe"] is False
    assert c["real_data_qa_blocked"] is True


# --------------------------------------------------------------------------- #
# determinism / mutation isolation
# --------------------------------------------------------------------------- #
def test_build_is_deterministic_and_isolated():
    a = _BUILD()
    b = _BUILD()
    assert a == b
    a["decision"]["allowed_decisions"].append({"x": 1})
    a["safety_posture"]["executes"] = True
    c = _BUILD()
    assert len(c["decision"]["allowed_decisions"]) == len(ALLOWED_DECISIONS)
    assert c["safety_posture"]["executes"] is False


def test_default_input_not_mutated_by_build():
    snapshot = dict(DEFAULT_DECISION_INPUT)
    _BUILD()
    _BUILD(_approve())
    assert DEFAULT_DECISION_INPUT == snapshot


# --------------------------------------------------------------------------- #
# narrative purity
# --------------------------------------------------------------------------- #
def test_narrative_has_no_trade_language():
    c = _BUILD()
    blob = " ".join(
        [
            c["operator_next_step"],
            c["decision_summary"],
            c["core_rule"],
            *c["human_operator_required_next_steps"],
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
def test_validate_default_contract_is_valid():
    verdict = _VALIDATE(_BUILD())
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == []
    for key, value in verdict.items():
        if key in ("valid", "missing_fields"):
            continue
        assert value is True, key


def test_validate_approved_plan_only_contract_is_valid():
    verdict = _VALIDATE(_BUILD(_approve()))
    assert verdict["valid"] is True
    assert verdict["approval_consistent"] is True


def test_validate_rejects_non_dict():
    assert _VALIDATE("not a contract")["valid"] is False


def test_validate_rejects_tampered_gate():
    c = _BUILD()
    c["real_data_qa_blocked"] = False
    verdict = _VALIDATE(c)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_validate_rejects_flipped_capability_flag():
    c = _BUILD()
    c["crosses_boundary"] = True
    verdict = _VALIDATE(c)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False
    assert verdict["no_boundary_crossing"] is False


def test_validate_rejects_forged_approval():
    # plan_approved True but effective decision is not APPROVE_PLAN_ONLY.
    c = _BUILD()
    c["decision"]["plan_approved"] = True
    verdict = _VALIDATE(c)
    assert verdict["valid"] is False
    assert verdict["approval_consistent"] is False


def test_validate_rejects_forged_execution_approval():
    c = _BUILD(_approve())
    c["approves_real_data_qa_execution"] = True
    verdict = _VALIDATE(c)
    assert verdict["valid"] is False
    assert verdict["no_execution_approval"] is False


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def test_render_is_deterministic_markdown():
    c = _BUILD(_approve())
    md1 = _RENDER(c)
    md2 = _RENDER(c)
    assert md1 == md2
    assert md1.startswith(
        "# Crypto-D1 Real Data QA Plan Approval Decision Contract"
    )
    assert "## Allowed Decisions" in md1
    assert "## Forbidden Decisions (always rejected)" in md1
    assert "## No-Unlock Confirmation" in md1
    assert "## Operator Next Step" in md1
    assert "BLOCKED" in md1
    assert "LOCKED" in md1
    assert "APPROVE_PLAN_ONLY" in md1


def test_render_handles_non_dict():
    assert _RENDER("x").startswith(
        "# Crypto-D1 Real Data QA Plan Approval Decision Contract"
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
    _BUILD(_approve())
    _BUILD({**DEFAULT_DECISION_INPUT, "requested_decision": "FETCH_DATA"})
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

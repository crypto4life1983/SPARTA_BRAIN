"""Tests for the Crypto-D1 Real Data QA Human Approval Packet Contract
(Block 136, Phase A).

The contract is a pure, stdlib-only, read-only paper contract. It defines -- on
paper only -- the structured HUMAN APPROVAL PACKET (eight required fields plus an
exact approval phrase) that a person must complete BEFORE any Real Data QA may
even be planned. It assesses a static packet into exactly one outcome
(BLOCK / INCOMPLETE / COMPLETE) and authorizes / unlocks nothing under any
outcome. These tests assert the schema, the eight-field completeness model, the
exact approval phrase, the mandatory forbidden-action coverage, the QA-check
whitelist, hard-block refusals, the mission-flow truth sync against the live
status module, determinism, source isolation, validation, render, and the two
additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract import (  # noqa: E501
    DEFAULT_SAMPLE_APPROVAL_PACKET,
    OUTCOME_BLOCK,
    OUTCOME_COMPLETE,
    OUTCOME_INCOMPLETE,
    RDQ_APPROVAL_ALLOWED_QA_CHECK_WHITELIST,
    RDQ_APPROVAL_AUTHORIZATION_FLAGS,
    RDQ_APPROVAL_CORE_RULE,
    RDQ_APPROVAL_CURRENT_STAGE,
    RDQ_APPROVAL_EXECUTABLE_SIGNAL_FIELDS,
    RDQ_APPROVAL_FORBIDDEN_PROMOTION_REQUEST_FLAGS,
    RDQ_APPROVAL_FORBIDDEN_TRADE_TERMS,
    RDQ_APPROVAL_GATE_LOCK_FLAGS,
    RDQ_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS,
    RDQ_APPROVAL_LABEL,
    RDQ_APPROVAL_MANDATORY_FORBIDDEN_ACTIONS,
    RDQ_APPROVAL_MISSION_FLOW_CURRENT_STAGE,
    RDQ_APPROVAL_MISSION_FLOW_NEXT_REQUIRED_ACTION,
    RDQ_APPROVAL_MODE,
    RDQ_APPROVAL_NEXT_REQUIRED_ACTION,
    RDQ_APPROVAL_OUTCOMES,
    RDQ_APPROVAL_REQUIRED_FIELD_KEYS,
    RDQ_APPROVAL_REQUIRED_FIELDS,
    RDQ_APPROVAL_REQUIRED_PHRASE,
    RDQ_APPROVAL_SAFETY_POSTURE,
    RDQ_APPROVAL_SCHEMA_VERSION,
    RDQ_APPROVAL_STATUS,
    assess_real_data_qa_human_approval_packet,
    build_crypto_d1_real_data_qa_human_approval_packet_contract,
    render_crypto_d1_real_data_qa_human_approval_packet_contract_markdown,
    validate_crypto_d1_real_data_qa_human_approval_packet_contract,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract.py"
)

_ASSESS = assess_real_data_qa_human_approval_packet
_BUILD = build_crypto_d1_real_data_qa_human_approval_packet_contract
_VALIDATE = validate_crypto_d1_real_data_qa_human_approval_packet_contract
_RENDER = render_crypto_d1_real_data_qa_human_approval_packet_contract_markdown


def _complete_packet(**overrides):
    """A packet with all eight fields valid and the exact approval phrase, so the
    assessment reaches COMPLETE unless an override degrades it."""
    packet = {
        "mission_flow_current_stage": RDQ_APPROVAL_MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": (
            RDQ_APPROVAL_MISSION_FLOW_NEXT_REQUIRED_ACTION
        ),
        "dataset_source_scope": "Local BTC/ETH/SOL daily CSVs already on disk",
        "symbols_timeframes": "BTC, ETH, SOL @ 1d",
        "date_range": "2019-01-01 .. 2025-12-31",
        "allowed_qa_checks": ["schema_validation", "null_check", "gap_detection"],
        "forbidden_actions": list(RDQ_APPROVAL_MANDATORY_FORBIDDEN_ACTIONS),
        "qa_only_proof": (
            "Read-only data-quality inspection of static files; computes no "
            "returns and touches no execution lane."
        ),
        "rollback_stop_condition": "Stop and discard outputs if any fetch is needed",
        "human_approval_phrase": RDQ_APPROVAL_REQUIRED_PHRASE,
    }
    packet.update(overrides)
    return packet


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert RDQ_APPROVAL_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_real_data_qa_human_approval_packet_contract.v1"
    )
    assert RDQ_APPROVAL_LABEL == (
        "Block 136 - Crypto-D1 Real Data QA Human Approval Packet Contract"
    )
    assert RDQ_APPROVAL_STATUS == (
        "READ_ONLY_CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT"
    )
    assert RDQ_APPROVAL_MODE == "RESEARCH_ONLY"
    assert "NEVER unlocks Real Data QA" in RDQ_APPROVAL_CORE_RULE


def test_next_action_and_stage_are_build_only():
    assert RDQ_APPROVAL_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT"
    )
    assert RDQ_APPROVAL_CURRENT_STAGE == (
        "CRYPTO_D1_REAL_DATA_QA_HUMAN_APPROVAL_PACKET_CONTRACT_REQUIRED"
    )


def test_outcomes_are_exactly_the_three_in_precedence_order():
    assert RDQ_APPROVAL_OUTCOMES == (
        OUTCOME_BLOCK,
        OUTCOME_INCOMPLETE,
        OUTCOME_COMPLETE,
    )


def test_eight_required_fields_are_exactly_the_spec_fields():
    assert len(RDQ_APPROVAL_REQUIRED_FIELD_KEYS) == 8
    assert RDQ_APPROVAL_REQUIRED_FIELD_KEYS == (
        "dataset_source_scope",
        "symbols_timeframes",
        "date_range",
        "allowed_qa_checks",
        "forbidden_actions",
        "qa_only_proof",
        "rollback_stop_condition",
        "human_approval_phrase",
    )
    # every field has a human description
    for key, desc in RDQ_APPROVAL_REQUIRED_FIELDS:
        assert isinstance(desc, str) and desc


def test_required_phrase_is_qa_planning_only_no_execution():
    phrase = RDQ_APPROVAL_REQUIRED_PHRASE.upper()
    assert "QA" in phrase
    assert "NO BACKTEST" in phrase
    assert "NO PAPER" in phrase
    assert "NO LIVE" in phrase


def test_mandatory_forbidden_actions_cover_all_execution_lanes():
    for lane in (
        "backtest",
        "baseline",
        "paper_trading",
        "live_trading",
        "order_placement",
        "broker_exchange",
        "automation",
    ):
        assert lane in RDQ_APPROVAL_MANDATORY_FORBIDDEN_ACTIONS


def test_qa_whitelist_is_read_only_checks_only():
    for check in RDQ_APPROVAL_ALLOWED_QA_CHECK_WHITELIST:
        assert "trade" not in check
        assert "backtest" not in check
        assert "order" not in check


def test_safety_posture_three_true_facts_all_else_false():
    posture = RDQ_APPROVAL_SAFETY_POSTURE
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

    assert RDQ_APPROVAL_MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert (
        RDQ_APPROVAL_MISSION_FLOW_NEXT_REQUIRED_ACTION
        == status.NEXT_REQUIRED_ACTION
    )


# --------------------------------------------------------------------------- #
# Completeness model
# --------------------------------------------------------------------------- #
def test_default_sample_is_incomplete_missing_phrase():
    result = _ASSESS(DEFAULT_SAMPLE_APPROVAL_PACKET)
    assert result["outcome"] == OUTCOME_INCOMPLETE
    assert result["packet_complete"] is False
    assert result["approval_phrase_ok"] is False
    assert result["block_reasons"] == []
    assert any("approval_phrase" in r for r in result["incomplete_reasons"])
    assert result["authorizes_nothing"] is True
    assert result["unlocks_real_data_qa"] is False


def test_default_build_is_incomplete():
    contract = _BUILD()
    assert contract["outcome"] == OUTCOME_INCOMPLETE
    assert contract["packet_complete"] is False


def test_complete_packet_reaches_complete():
    result = _ASSESS(_complete_packet())
    assert result["outcome"] == OUTCOME_COMPLETE
    assert result["packet_complete"] is True
    assert result["ready_for_human_approval_review"] is True
    # COMPLETE still authorizes and unlocks nothing.
    assert result["unlocks_real_data_qa"] is False
    assert result["promotes_beyond_boundary"] is False
    assert result["authorizes_nothing"] is True


def test_each_missing_required_field_makes_incomplete():
    for key in RDQ_APPROVAL_REQUIRED_FIELD_KEYS:
        result = _ASSESS(_complete_packet(**{key: ""}))
        assert result["outcome"] == OUTCOME_INCOMPLETE, key
        assert key in result["missing_fields"], key


def test_wrong_approval_phrase_is_incomplete():
    result = _ASSESS(_complete_packet(human_approval_phrase="yes do it"))
    assert result["outcome"] == OUTCOME_INCOMPLETE
    assert result["approval_phrase_ok"] is False


def test_phrase_match_is_case_insensitive_and_trimmed():
    messy = "  i approve real data qa planning only - no backtest, no paper, no live  "
    result = _ASSESS(_complete_packet(human_approval_phrase=messy))
    assert result["approval_phrase_ok"] is True
    assert result["outcome"] == OUTCOME_COMPLETE


def test_missing_mandatory_forbidden_action_is_incomplete():
    partial = ["backtest", "paper_trading"]
    result = _ASSESS(_complete_packet(forbidden_actions=partial))
    assert result["outcome"] == OUTCOME_INCOMPLETE
    assert result["forbidden_actions_ok"] is False
    assert "live_trading" in result["missing_forbidden_actions"]


def test_empty_qa_checks_is_incomplete():
    result = _ASSESS(_complete_packet(allowed_qa_checks=[]))
    assert result["outcome"] == OUTCOME_INCOMPLETE
    assert result["qa_checks_ok"] is False


def test_non_whitelisted_benign_qa_check_is_incomplete():
    result = _ASSESS(
        _complete_packet(allowed_qa_checks=["schema_validation", "made_up_check"])
    )
    assert result["outcome"] == OUTCOME_INCOMPLETE
    assert "made_up_check" in result["qa_checks_outside_whitelist"]


# --------------------------------------------------------------------------- #
# Hard-block refusals
# --------------------------------------------------------------------------- #
def test_authorization_flag_forces_block():
    for flag in RDQ_APPROVAL_AUTHORIZATION_FLAGS:
        result = _ASSESS(_complete_packet(**{flag: True}))
        assert result["outcome"] == OUTCOME_BLOCK, flag
        assert flag in result["forbidden_flag_hits"], flag


def test_gate_unlock_request_forces_block():
    for flag in RDQ_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS:
        result = _ASSESS(_complete_packet(**{flag: True}))
        assert result["outcome"] == OUTCOME_BLOCK, flag


def test_unlocking_a_locked_gate_forces_block():
    for flag in RDQ_APPROVAL_GATE_LOCK_FLAGS:
        result = _ASSESS(_complete_packet(**{flag: False}))
        assert result["outcome"] == OUTCOME_BLOCK, flag


def test_forbidden_promotion_request_forces_block():
    for flag in RDQ_APPROVAL_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        result = _ASSESS(_complete_packet(**{flag: True}))
        assert result["outcome"] == OUTCOME_BLOCK, flag


def test_executable_signal_field_forces_block():
    for field in RDQ_APPROVAL_EXECUTABLE_SIGNAL_FIELDS:
        result = _ASSESS(_complete_packet(**{field: "do something"}))
        assert result["outcome"] == OUTCOME_BLOCK, field
        assert field in result["forbidden_flag_hits"], field


def test_smuggled_execution_term_in_qa_checks_blocks():
    result = _ASSESS(
        _complete_packet(allowed_qa_checks=["schema_validation", "backtest"])
    )
    assert result["outcome"] == OUTCOME_BLOCK
    assert any("smuggled" in r for r in result["block_reasons"])


def test_qa_only_proof_may_negate_execution_terms():
    # The proof prose legitimately says "no backtest, no paper, no live"; that
    # must NOT trip the smuggle block.
    result = _ASSESS(
        _complete_packet(
            qa_only_proof="Strictly QA. No backtest, no paper, no live trading."
        )
    )
    assert result["outcome"] == OUTCOME_COMPLETE


def test_mission_flow_misalignment_blocks():
    result = _ASSESS(_complete_packet(mission_flow_current_stage="SOMETHING_ELSE"))
    assert result["outcome"] == OUTCOME_BLOCK
    assert result["mission_flow_aligned"] is False


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_assessment_is_deterministic():
    payload = _complete_packet()
    assert _ASSESS(payload) == _ASSESS(payload)


def test_build_does_not_mutate_caller_payload():
    import copy

    payload = _complete_packet()
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


def test_default_sample_is_not_shared_between_builds():
    c1 = _BUILD()
    c2 = _BUILD()
    c1["block_reasons"].append("tampered")
    assert "tampered" not in c2["block_reasons"]
    assert DEFAULT_SAMPLE_APPROVAL_PACKET["human_approval_phrase"] == ""


# --------------------------------------------------------------------------- #
# Validation / render
# --------------------------------------------------------------------------- #
def test_default_contract_validates():
    verdict = _VALIDATE(_BUILD())
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == []
    assert verdict["no_trade_language"] is True
    assert verdict["flags_false"] is True
    assert verdict["gates_locked"] is True
    assert verdict["authorizes_nothing"] is True
    assert verdict["mission_flow_refs_ok"] is True
    assert verdict["eight_required_fields"] is True
    assert verdict["phrase_ok"] is True
    assert verdict["real_data_qa_stays_blocked"] is True


def test_every_outcome_path_validates():
    payloads = [
        DEFAULT_SAMPLE_APPROVAL_PACKET,                  # incomplete
        _complete_packet(),                              # complete
        _complete_packet(dataset_source_scope=""),       # incomplete
        _complete_packet(authorizes_trading=True),       # block (auth flag)
        _complete_packet(mission_flow_current_stage="X"),  # block (misaligned)
    ]
    for payload in payloads:
        verdict = _VALIDATE(_BUILD(payload))
        assert verdict["valid"] is True, payload


def test_validate_rejects_tampered_contract():
    contract = _BUILD()
    contract["executes"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["executes_false"] is False


def test_validate_rejects_unlocked_real_data_qa():
    contract = _BUILD()
    contract["unlocks_real_data_qa"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["real_data_qa_stays_blocked"] is False


def test_complete_contract_unlocks_no_gate():
    contract = _BUILD(_complete_packet())
    assert contract["outcome"] == OUTCOME_COMPLETE
    assert contract["packet_complete"] is True
    assert contract["promotes_beyond_boundary"] is False
    assert contract["unlocks_real_data_qa"] is False
    assert contract["unlocks_baseline_backtest"] is False
    assert contract["unlocks_paper_trading"] is False
    assert contract["unlocks_micro_live"] is False
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["authorizes_nothing"] is True


def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith(
        "# Crypto-D1 Real Data QA Human Approval Packet Contract"
    )
    assert "## Required Packet Fields" in text
    assert "## Mandatory Forbidden Actions" in text
    assert "## No Execution Authorization" in text


def test_generated_guidance_has_no_execution_verbs():
    contract = _BUILD()
    blob = " ".join(
        str(contract.get(k, ""))
        for k in ("operator_next_step", "operator_notes", "core_rule")
    )
    blob += " " + " ".join(
        str(s) for s in contract.get("human_operator_required_next_steps", [])
    )
    tokens = set(
        "".join(c if (c.isalnum() or c == "_") else " " for c in blob.lower()).split()
    )
    for term in RDQ_APPROVAL_FORBIDDEN_TRADE_TERMS:
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
    _BUILD(_complete_packet())
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

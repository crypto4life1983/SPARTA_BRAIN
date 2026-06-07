"""Tests for the Crypto-D1 Real Data QA Readiness Checklist Contract
(Block 136, Phase B).

The contract is a pure, stdlib-only, read-only paper contract. It defines -- on
paper only -- the eight-item READINESS CHECKLIST that must ALL pass before a human
is even asked to approve Real Data QA. It assesses a static payload into exactly
one outcome (BLOCK / NOT_READY / READY) and authorizes / unlocks nothing under any
outcome -- even READY only means "ready for a separate human approval review".
These tests assert the schema, the eight-item checklist, the READY-only-when-all-
pass model, the evidence-quality NOT_READY cases, hard-block refusals, the
mission-flow truth sync against the live status module, determinism, isolation,
validation, render, AST purity, and the two additive commander_2_safety allowlist
entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_readiness_checklist_contract import (  # noqa: E501
    DEFAULT_SAMPLE_READINESS_INPUT,
    OUTCOME_BLOCK,
    OUTCOME_NOT_READY,
    OUTCOME_READY,
    RDQ_READINESS_AUTHORIZATION_FLAGS,
    RDQ_READINESS_CHECKLIST_ITEM_IDS,
    RDQ_READINESS_CHECKLIST_ITEMS,
    RDQ_READINESS_CORE_RULE,
    RDQ_READINESS_CURRENT_STAGE,
    RDQ_READINESS_EXECUTABLE_SIGNAL_FIELDS,
    RDQ_READINESS_FORBIDDEN_PROMOTION_REQUEST_FLAGS,
    RDQ_READINESS_FORBIDDEN_TRADE_TERMS,
    RDQ_READINESS_GATE_LOCK_FLAGS,
    RDQ_READINESS_GATE_UNLOCK_REQUEST_FLAGS,
    RDQ_READINESS_LABEL,
    RDQ_READINESS_MIN_BOOKED_RECORDS,
    RDQ_READINESS_MISSION_FLOW_CURRENT_STAGE,
    RDQ_READINESS_MISSION_FLOW_NEXT_REQUIRED_ACTION,
    RDQ_READINESS_MODE,
    RDQ_READINESS_NEXT_REQUIRED_ACTION,
    RDQ_READINESS_OUTCOMES,
    RDQ_READINESS_SAFETY_POSTURE,
    RDQ_READINESS_SCHEMA_VERSION,
    RDQ_READINESS_STATUS,
    assess_real_data_qa_readiness,
    build_crypto_d1_real_data_qa_readiness_checklist_contract,
    render_crypto_d1_real_data_qa_readiness_checklist_contract_markdown,
    validate_crypto_d1_real_data_qa_readiness_checklist_contract,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_real_data_qa_readiness_checklist_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_real_data_qa_readiness_checklist_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_real_data_qa_readiness_checklist_contract.py"
)

_ASSESS = assess_real_data_qa_readiness
_BUILD = build_crypto_d1_real_data_qa_readiness_checklist_contract
_VALIDATE = validate_crypto_d1_real_data_qa_readiness_checklist_contract
_RENDER = render_crypto_d1_real_data_qa_readiness_checklist_contract_markdown


def _ready_input(**overrides):
    """A payload where all eight checklist items pass, so the assessment reaches
    READY unless an override degrades it: approval packet complete, plus three
    distinct booked trades (distinct symbol/direction pairs, distinct macro
    events) so the evidence is not external-only, open-only, duplicate-only,
    correlated-only, or an insufficient sample."""
    payload = {
        "mission_flow_current_stage": RDQ_READINESS_MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": (
            RDQ_READINESS_MISSION_FLOW_NEXT_REQUIRED_ACTION
        ),
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "approval_packet_complete": True,
        "evidence": [
            {
                "id": "B1",
                "symbol": "BTC",
                "direction": "long",
                "status": "closed",
                "pnl": 2.1,
                "macro_event": "btc_breakout_2026_03",
                "source": "trade",
            },
            {
                "id": "E1",
                "symbol": "ETH",
                "direction": "short",
                "status": "closed",
                "pnl": 1.4,
                "macro_event": "eth_dump_2026_05",
                "source": "trade",
            },
            {
                "id": "S1",
                "symbol": "SOL",
                "direction": "long",
                "status": "closed",
                "pnl": 0.8,
                "macro_event": "sol_rotation_2026_06",
                "source": "trade",
            },
        ],
    }
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert RDQ_READINESS_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_real_data_qa_readiness_checklist_contract.v1"
    )
    assert RDQ_READINESS_LABEL == (
        "Block 136 - Crypto-D1 Real Data QA Readiness Checklist Contract"
    )
    assert RDQ_READINESS_STATUS == (
        "READ_ONLY_CRYPTO_D1_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT"
    )
    assert RDQ_READINESS_MODE == "RESEARCH_ONLY"
    assert "NEVER unlocks Real Data QA" in RDQ_READINESS_CORE_RULE


def test_next_action_and_stage_are_build_only():
    assert RDQ_READINESS_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT"
    )
    assert RDQ_READINESS_CURRENT_STAGE == (
        "CRYPTO_D1_REAL_DATA_QA_READINESS_CHECKLIST_CONTRACT_REQUIRED"
    )


def test_outcomes_are_exactly_the_three_in_precedence_order():
    assert RDQ_READINESS_OUTCOMES == (
        OUTCOME_BLOCK,
        OUTCOME_NOT_READY,
        OUTCOME_READY,
    )


def test_eight_checklist_items_are_exactly_the_spec_items():
    assert len(RDQ_READINESS_CHECKLIST_ITEM_IDS) == 8
    assert RDQ_READINESS_CHECKLIST_ITEM_IDS == (
        "approval_packet_complete",
        "evidence_not_external_only",
        "evidence_not_open_unrealized_only",
        "evidence_not_correlated_only",
        "evidence_not_duplicate_only",
        "sample_sufficient",
        "all_forbidden_flags_false",
        "mission_flow_boundary_aligned",
    )
    # every item has a human label
    for item_id, label in RDQ_READINESS_CHECKLIST_ITEMS:
        assert isinstance(label, str) and label


def test_min_booked_records_threshold():
    assert RDQ_READINESS_MIN_BOOKED_RECORDS == 3


def test_safety_posture_three_true_facts_all_else_false():
    posture = RDQ_READINESS_SAFETY_POSTURE
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

    assert RDQ_READINESS_MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    assert (
        RDQ_READINESS_MISSION_FLOW_NEXT_REQUIRED_ACTION
        == status.NEXT_REQUIRED_ACTION
    )


# --------------------------------------------------------------------------- #
# Readiness model
# --------------------------------------------------------------------------- #
def test_default_sample_is_not_ready():
    result = _ASSESS(DEFAULT_SAMPLE_READINESS_INPUT)
    assert result["outcome"] == OUTCOME_NOT_READY
    assert result["ready"] is False
    assert result["forbidden_flag_hits"] == []
    # default fails packet, duplicate, correlated, and sample sufficiency
    assert "approval_packet_complete" in result["failed_item_ids"]
    assert "sample_sufficient" in result["failed_item_ids"]
    assert result["authorizes_nothing"] is True
    assert result["unlocks_real_data_qa"] is False


def test_default_build_is_not_ready():
    contract = _BUILD()
    assert contract["outcome"] == OUTCOME_NOT_READY
    assert contract["ready"] is False


def test_all_items_pass_reaches_ready():
    result = _ASSESS(_ready_input())
    assert result["outcome"] == OUTCOME_READY
    assert result["ready"] is True
    assert result["ready_for_human_approval_review"] is True
    assert result["failed_item_ids"] == []
    assert len(result["passed_item_ids"]) == 8
    # READY still authorizes and unlocks nothing.
    assert result["unlocks_real_data_qa"] is False
    assert result["promotes_beyond_boundary"] is False
    assert result["authorizes_nothing"] is True


def test_incomplete_approval_packet_is_not_ready():
    result = _ASSESS(_ready_input(approval_packet_complete=False))
    assert result["outcome"] == OUTCOME_NOT_READY
    assert "approval_packet_complete" in result["failed_item_ids"]


def test_external_only_evidence_is_not_ready():
    payload = _ready_input(
        evidence=[
            {"id": "x1", "source": "hyperliquid_whale", "note": "whale moved"},
            {"id": "x2", "source": "funding_rate", "note": "funding flipped"},
        ]
    )
    result = _ASSESS(payload)
    assert result["outcome"] == OUTCOME_NOT_READY
    assert "evidence_not_external_only" in result["failed_item_ids"]


def test_open_unrealized_only_evidence_is_not_ready():
    payload = _ready_input(
        evidence=[
            {
                "id": "o1",
                "symbol": "BTC",
                "direction": "long",
                "status": "open",
                "source": "trade",
            },
            {
                "id": "o2",
                "symbol": "ETH",
                "direction": "short",
                "status": "open",
                "source": "trade",
            },
        ]
    )
    result = _ASSESS(payload)
    assert result["outcome"] == OUTCOME_NOT_READY
    assert "evidence_not_open_unrealized_only" in result["failed_item_ids"]


def test_correlated_only_evidence_is_not_ready():
    # Three distinct symbol/direction pairs (no duplicate) but every booked trade
    # collapses into a single shared macro event -> correlated-only.
    payload = _ready_input(
        evidence=[
            {
                "id": "c1",
                "symbol": "BTC",
                "direction": "long",
                "status": "closed",
                "macro_event": "global_risk_off_2026_05",
                "source": "trade",
            },
            {
                "id": "c2",
                "symbol": "ETH",
                "direction": "short",
                "status": "closed",
                "macro_event": "global_risk_off_2026_05",
                "source": "trade",
            },
            {
                "id": "c3",
                "symbol": "SOL",
                "direction": "long",
                "status": "closed",
                "macro_event": "global_risk_off_2026_05",
                "source": "trade",
            },
        ]
    )
    result = _ASSESS(payload)
    assert result["outcome"] == OUTCOME_NOT_READY
    assert "evidence_not_correlated_only" in result["failed_item_ids"]


def test_duplicate_only_evidence_is_not_ready():
    # Same symbol/direction repeated -> duplicate-only.
    payload = _ready_input(
        evidence=[
            {
                "id": "d1",
                "symbol": "BTC",
                "direction": "long",
                "status": "closed",
                "macro_event": "m1",
                "source": "trade",
            },
            {
                "id": "d2",
                "symbol": "BTC",
                "direction": "long",
                "status": "closed",
                "macro_event": "m2",
                "source": "trade",
            },
            {
                "id": "d3",
                "symbol": "BTC",
                "direction": "long",
                "status": "closed",
                "macro_event": "m3",
                "source": "trade",
            },
        ]
    )
    result = _ASSESS(payload)
    assert result["outcome"] == OUTCOME_NOT_READY
    assert "evidence_not_duplicate_only" in result["failed_item_ids"]


def test_insufficient_sample_is_not_ready():
    # Two distinct booked trades -> below the minimum of three.
    payload = _ready_input(
        evidence=[
            {
                "id": "i1",
                "symbol": "BTC",
                "direction": "long",
                "status": "closed",
                "macro_event": "m1",
                "source": "trade",
            },
            {
                "id": "i2",
                "symbol": "ETH",
                "direction": "short",
                "status": "closed",
                "macro_event": "m2",
                "source": "trade",
            },
        ]
    )
    result = _ASSESS(payload)
    assert result["outcome"] == OUTCOME_NOT_READY
    assert "sample_sufficient" in result["failed_item_ids"]


def test_no_evidence_is_not_ready():
    result = _ASSESS(_ready_input(evidence=[]))
    assert result["outcome"] == OUTCOME_NOT_READY
    assert "sample_sufficient" in result["failed_item_ids"]


# --------------------------------------------------------------------------- #
# Hard-block refusals (safety failures, not "not ready yet")
# --------------------------------------------------------------------------- #
def test_authorization_flag_forces_block():
    for flag in RDQ_READINESS_AUTHORIZATION_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_BLOCK, flag
        assert flag in result["forbidden_flag_hits"], flag


def test_gate_unlock_request_forces_block():
    for flag in RDQ_READINESS_GATE_UNLOCK_REQUEST_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_BLOCK, flag


def test_unlocking_a_locked_gate_forces_block():
    for flag in RDQ_READINESS_GATE_LOCK_FLAGS:
        result = _ASSESS(_ready_input(**{flag: False}))
        assert result["outcome"] == OUTCOME_BLOCK, flag


def test_forbidden_promotion_request_forces_block():
    for flag in RDQ_READINESS_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        result = _ASSESS(_ready_input(**{flag: True}))
        assert result["outcome"] == OUTCOME_BLOCK, flag


def test_executable_signal_field_forces_block():
    for field in RDQ_READINESS_EXECUTABLE_SIGNAL_FIELDS:
        result = _ASSESS(_ready_input(**{field: "do something"}))
        assert result["outcome"] == OUTCOME_BLOCK, field
        assert field in result["forbidden_flag_hits"], field


def test_mission_flow_misalignment_blocks():
    result = _ASSESS(_ready_input(mission_flow_current_stage="SOMETHING_ELSE"))
    assert result["outcome"] == OUTCOME_BLOCK
    assert result["mission_flow_aligned"] is False
    assert "mission_flow_boundary_aligned" in result["failed_item_ids"]


def test_block_takes_precedence_over_not_ready():
    # An incomplete packet (would be NOT_READY) plus a forbidden flag must BLOCK.
    result = _ASSESS(
        _ready_input(approval_packet_complete=False, authorizes_trading=True)
    )
    assert result["outcome"] == OUTCOME_BLOCK


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_assessment_is_deterministic():
    payload = _ready_input()
    assert _ASSESS(payload) == _ASSESS(payload)


def test_build_does_not_mutate_caller_payload():
    import copy

    payload = _ready_input()
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


def test_default_sample_is_not_shared_between_builds():
    c1 = _BUILD()
    c2 = _BUILD()
    c1["failed_item_ids"].append("tampered")
    assert "tampered" not in c2["failed_item_ids"]
    assert DEFAULT_SAMPLE_READINESS_INPUT["approval_packet_complete"] is False


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
    assert verdict["eight_checklist_items"] is True
    assert verdict["ready_only_when_all_pass"] is True
    assert verdict["real_data_qa_stays_blocked"] is True


def test_every_outcome_path_validates():
    payloads = [
        DEFAULT_SAMPLE_READINESS_INPUT,                    # not_ready
        _ready_input(),                                    # ready
        _ready_input(approval_packet_complete=False),      # not_ready
        _ready_input(authorizes_trading=True),             # block (auth flag)
        _ready_input(mission_flow_current_stage="X"),      # block (misaligned)
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


def test_validate_rejects_ready_without_all_items_passing():
    # A NOT_READY contract whose ready flag was flipped True must fail validation.
    contract = _BUILD()
    assert contract["outcome"] == OUTCOME_NOT_READY
    contract["ready"] = True
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["ready_only_when_all_pass"] is False


def test_ready_contract_unlocks_no_gate():
    contract = _BUILD(_ready_input())
    assert contract["outcome"] == OUTCOME_READY
    assert contract["ready"] is True
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
    assert contract["requires_separate_future_human_approved_step"] is True


def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith(
        "# Crypto-D1 Real Data QA Readiness Checklist Contract"
    )
    assert "## Readiness Checklist" in text
    assert "## No Execution Authorization" in text
    assert "## Operator Next Step" in text


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
    for term in RDQ_READINESS_FORBIDDEN_TRADE_TERMS:
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

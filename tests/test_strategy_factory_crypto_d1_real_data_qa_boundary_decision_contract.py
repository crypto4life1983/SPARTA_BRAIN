"""Tests for the Crypto-D1 Human-Controlled Real Data QA Boundary Decision
Contract (Block 134).

The contract is a pure, stdlib-only, read-only paper contract. It defines -- on
paper only -- the HUMAN boundary decision that must be made BEFORE any Real Data
QA may even be planned. It assesses a static evidence summary into exactly one
outcome (BLOCK / AWAIT_EVIDENCE / READY_FOR_HUMAN_DECISION), assembles the human
decision packet, and authorizes / unlocks nothing under any outcome. These tests
assert the schema, the boundary-decision model, evidence-quality refusals, the
mission-flow truth sync against the live status module, determinism, source
isolation (no file writes / no forbidden imports), validation, render, and the
two additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract import (  # noqa: E501
    DEFAULT_SAMPLE_BOUNDARY_INPUT,
    OUTCOME_AWAIT_EVIDENCE,
    OUTCOME_BLOCK,
    OUTCOME_READY_FOR_HUMAN_DECISION,
    RDQ_BOUNDARY_AUTHORIZATION_FLAGS,
    RDQ_BOUNDARY_AWAIT_EVIDENCE_QUALITY_SIGNALS,
    RDQ_BOUNDARY_BLOCK_EVIDENCE_QUALITY_SIGNALS,
    RDQ_BOUNDARY_BOOKED_STATUS_TAGS,
    RDQ_BOUNDARY_CORE_RULE,
    RDQ_BOUNDARY_CURRENT_STAGE,
    RDQ_BOUNDARY_DECISION_OPTIONS,
    RDQ_BOUNDARY_EXECUTABLE_SIGNAL_FIELDS,
    RDQ_BOUNDARY_EXTERNAL_RESEARCH_SOURCE_TAGS,
    RDQ_BOUNDARY_FORBIDDEN_PROMOTION_REQUEST_FLAGS,
    RDQ_BOUNDARY_FORBIDDEN_TRADE_TERMS,
    RDQ_BOUNDARY_GATE_LOCK_FLAGS,
    RDQ_BOUNDARY_GATE_UNLOCK_REQUEST_FLAGS,
    RDQ_BOUNDARY_HUMAN_ACKNOWLEDGEMENTS_REQUIRED,
    RDQ_BOUNDARY_LABEL,
    RDQ_BOUNDARY_MIN_INDEPENDENT_BOOKED_COHORTS,
    RDQ_BOUNDARY_MISSION_FLOW_CURRENT_STAGE,
    RDQ_BOUNDARY_MISSION_FLOW_NEXT_REQUIRED_ACTION,
    RDQ_BOUNDARY_MODE,
    RDQ_BOUNDARY_NEXT_REQUIRED_ACTION,
    RDQ_BOUNDARY_OBSERVATION_ONLY_EVIDENCE_LANES,
    RDQ_BOUNDARY_OPEN_STATUS_TAGS,
    RDQ_BOUNDARY_OUTCOMES,
    RDQ_BOUNDARY_REQUIRED_COHORT_INDEPENDENCE_LABEL,
    RDQ_BOUNDARY_REQUIRED_DAILY_ALPHA_BRIEF_VERDICT,
    RDQ_BOUNDARY_REQUIRED_EVIDENCE_SCORING_OUTCOME,
    RDQ_BOUNDARY_SAFETY_POSTURE,
    RDQ_BOUNDARY_SCHEMA_VERSION,
    RDQ_BOUNDARY_STATUS,
    RDQ_BOUNDARY_TRADE_SOURCE_TAGS,
    assess_real_data_qa_boundary_decision,
    build_crypto_d1_real_data_qa_boundary_decision_contract,
    build_human_boundary_decision_packet,
    render_crypto_d1_real_data_qa_boundary_decision_contract_markdown,
    validate_crypto_d1_real_data_qa_boundary_decision_contract,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract.py"
)

_ASSESS = assess_real_data_qa_boundary_decision
_PACKET = build_human_boundary_decision_packet
_BUILD = build_crypto_d1_real_data_qa_boundary_decision_contract
_VALIDATE = validate_crypto_d1_real_data_qa_boundary_decision_contract
_RENDER = render_crypto_d1_real_data_qa_boundary_decision_contract_markdown


def _rec(rid, symbol=None, direction=None, status="closed", pnl=0.0, **extra):
    record = {"id": rid, "status": status, "pnl": pnl, "source": "trade"}
    if symbol is not None:
        record["symbol"] = symbol
    if direction is not None:
        record["direction"] = direction
    record.update(extra)
    return record


def _passing_payload(**overrides):
    """A payload whose upstream verdicts and evidence all pass, so the assessment
    reaches READY_FOR_HUMAN_DECISION unless an override degrades it."""
    payload = {
        "mission_flow_current_stage": RDQ_BOUNDARY_MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": (
            RDQ_BOUNDARY_MISSION_FLOW_NEXT_REQUIRED_ACTION
        ),
        "evidence_scoring_outcome": RDQ_BOUNDARY_REQUIRED_EVIDENCE_SCORING_OUTCOME,
        "cohort_independence_label": (
            RDQ_BOUNDARY_REQUIRED_COHORT_INDEPENDENCE_LABEL
        ),
        "daily_alpha_brief_verdict": RDQ_BOUNDARY_REQUIRED_DAILY_ALPHA_BRIEF_VERDICT,
        "independent_booked_cohort_count": (
            RDQ_BOUNDARY_MIN_INDEPENDENT_BOOKED_COHORTS
        ),
        "evidence": [
            _rec("i1", "BTC", "buy_side", "closed", 1.0, macro_event="m1"),
            _rec("i2", "ETH", "sell_side", "closed", 1.0, macro_event="m2"),
            _rec("i3", "SOL", "buy_side", "closed", 1.0, macro_event="m3"),
        ],
    }
    payload.update(overrides)
    return payload


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert RDQ_BOUNDARY_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_real_data_qa_boundary_decision_contract.v1"
    )
    assert RDQ_BOUNDARY_LABEL == (
        "Block 134 - Crypto-D1 Human-Controlled Real Data QA Boundary Decision "
        "Contract"
    )
    assert RDQ_BOUNDARY_STATUS == (
        "READ_ONLY_CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT"
    )
    assert RDQ_BOUNDARY_MODE == "RESEARCH_ONLY"
    assert "NEVER unlocks Real Data QA" in RDQ_BOUNDARY_CORE_RULE


def test_next_action_and_stage_are_build_only():
    assert RDQ_BOUNDARY_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT"
    )
    assert RDQ_BOUNDARY_CURRENT_STAGE == (
        "CRYPTO_D1_REAL_DATA_QA_BOUNDARY_DECISION_CONTRACT_REQUIRED"
    )


def test_outcomes_are_exactly_the_three_in_precedence_order():
    assert RDQ_BOUNDARY_OUTCOMES == (
        OUTCOME_BLOCK,
        OUTCOME_AWAIT_EVIDENCE,
        OUTCOME_READY_FOR_HUMAN_DECISION,
    )
    assert set(RDQ_BOUNDARY_OUTCOMES) == {
        "BLOCK",
        "AWAIT_EVIDENCE",
        "READY_FOR_HUMAN_DECISION",
    }


def test_required_upstream_values_and_threshold():
    assert RDQ_BOUNDARY_REQUIRED_EVIDENCE_SCORING_OUTCOME == "PROMOTE_TO_REVIEW"
    assert RDQ_BOUNDARY_REQUIRED_COHORT_INDEPENDENCE_LABEL == "INDEPENDENT"
    assert RDQ_BOUNDARY_REQUIRED_DAILY_ALPHA_BRIEF_VERDICT == "APPROVED"
    assert RDQ_BOUNDARY_MIN_INDEPENDENT_BOOKED_COHORTS == 3


def test_evidence_quality_signal_families():
    assert set(RDQ_BOUNDARY_BLOCK_EVIDENCE_QUALITY_SIGNALS) == {
        "no_evidence",
        "external_evidence_only",
    }
    assert set(RDQ_BOUNDARY_AWAIT_EVIDENCE_QUALITY_SIGNALS) == {
        "open_unrealized_only",
        "correlated",
        "duplicate",
        "insufficient_sample",
    }


def test_decision_options_are_planning_only():
    assert RDQ_BOUNDARY_DECISION_OPTIONS == (
        "AWAIT",
        "DECLINE",
        "APPROVE_REAL_DATA_QA_PLANNING_ONLY",
    )


def test_human_acknowledgements_are_present():
    acks = RDQ_BOUNDARY_HUMAN_ACKNOWLEDGEMENTS_REQUIRED
    assert len(acks) == 6
    assert any("BLOCKED" in a for a in acks)
    assert any("separate, future" in a for a in acks)


def test_source_and_status_tag_families():
    assert "trade" in RDQ_BOUNDARY_TRADE_SOURCE_TAGS
    for tag in ("whale", "funding_rate", "btc_cycle", "daily_alpha"):
        assert tag in RDQ_BOUNDARY_EXTERNAL_RESEARCH_SOURCE_TAGS
    assert "closed" in RDQ_BOUNDARY_BOOKED_STATUS_TAGS
    assert "booked" in RDQ_BOUNDARY_BOOKED_STATUS_TAGS
    assert "open" in RDQ_BOUNDARY_OPEN_STATUS_TAGS
    assert "unrealized" in RDQ_BOUNDARY_OPEN_STATUS_TAGS


def test_safety_posture_three_true_facts_all_else_false():
    posture = RDQ_BOUNDARY_SAFETY_POSTURE
    assert posture["read_only"] is True
    assert posture["research_only"] is True
    assert posture["human_approval_required"] is True
    assert posture["executes"] is False
    for key, value in posture.items():
        if key in ("read_only", "research_only", "human_approval_required"):
            continue
        assert value is False, key


def test_observation_only_lanes_include_open_pnl_and_external_sources():
    lanes = RDQ_BOUNDARY_OBSERVATION_ONLY_EVIDENCE_LANES
    assert "open_unrealized_pnl" in lanes
    assert "daily_alpha_brief" in lanes
    assert "hyperliquid_whale_evidence" in lanes


# --------------------------------------------------------------------------- #
# Mission-flow truth sync (cannot silently drift from the live status module)
# --------------------------------------------------------------------------- #
def test_mission_flow_truth_matches_live_status_module():
    from sparta_commander import strategy_factory_mission_flow_status as status

    assert (
        RDQ_BOUNDARY_MISSION_FLOW_CURRENT_STAGE == status.CURRENT_STAGE
    )
    assert (
        RDQ_BOUNDARY_MISSION_FLOW_NEXT_REQUIRED_ACTION
        == status.NEXT_REQUIRED_ACTION
    )


# --------------------------------------------------------------------------- #
# Boundary-decision model behavior
# --------------------------------------------------------------------------- #
def test_default_sample_awaits_evidence():
    result = _ASSESS(DEFAULT_SAMPLE_BOUNDARY_INPUT)
    assert result["outcome"] == OUTCOME_AWAIT_EVIDENCE
    assert result["ready_for_human_decision"] is False
    assert result["unlocks_real_data_qa"] is False
    assert result["authorizes_nothing"] is True
    assert result["await_reasons"]
    assert result["block_reasons"] == []


def test_default_build_awaits_evidence():
    contract = _BUILD()
    assert contract["outcome"] == OUTCOME_AWAIT_EVIDENCE
    assert contract["ready_for_human_decision"] is False


def test_passing_payload_reaches_ready_for_human_decision():
    result = _ASSESS(_passing_payload())
    assert result["outcome"] == OUTCOME_READY_FOR_HUMAN_DECISION
    assert result["ready_for_human_decision"] is True
    # READY still authorizes and unlocks nothing.
    assert result["unlocks_real_data_qa"] is False
    assert result["promotes_beyond_boundary"] is False
    assert result["authorizes_nothing"] is True


def test_no_evidence_blocks():
    result = _ASSESS(_passing_payload(evidence=[]))
    assert result["outcome"] == OUTCOME_BLOCK
    assert any("no_evidence" in r for r in result["block_reasons"])


def test_external_evidence_only_blocks():
    payload = _passing_payload(
        evidence=[
            _rec("w", "BTC", None, "closed", 5.0, source="whale"),
            _rec("f", "BTC", None, "closed", 0.0, source="funding_rate"),
        ]
    )
    result = _ASSESS(payload)
    assert result["outcome"] == OUTCOME_BLOCK
    assert any("external_evidence_only" in r for r in result["block_reasons"])


def test_open_unrealized_only_awaits():
    payload = _passing_payload(
        evidence=[
            _rec("o1", "AVAX", "sell_side", "open", 2.0),
            _rec("o2", "SOL", "sell_side", "unrealized", 1.0),
        ]
    )
    result = _ASSESS(payload)
    assert result["outcome"] == OUTCOME_AWAIT_EVIDENCE
    assert any("open_unrealized_only" in r for r in result["await_reasons"])


def test_correlated_evidence_awaits():
    payload = _passing_payload(
        evidence=[
            _rec("c1", "ETH", "sell_side", "closed", 1.0, macro_event="dump"),
            _rec("c2", "BTC", "buy_side", "closed", 1.0, macro_event="dump"),
        ]
    )
    result = _ASSESS(payload)
    assert result["outcome"] == OUTCOME_AWAIT_EVIDENCE
    assert any("correlated" in r for r in result["await_reasons"])


def test_duplicate_evidence_awaits():
    payload = _passing_payload(
        evidence=[
            _rec("d1", "AVAX", "sell_side", "closed", 1.0),
            _rec("d2", "AVAX", "sell_side", "closed", 0.5),
        ]
    )
    result = _ASSESS(payload)
    assert result["outcome"] == OUTCOME_AWAIT_EVIDENCE
    assert any("duplicate" in r for r in result["await_reasons"])


def test_insufficient_independent_cohort_count_awaits():
    result = _ASSESS(_passing_payload(independent_booked_cohort_count=1))
    assert result["outcome"] == OUTCOME_AWAIT_EVIDENCE
    assert any("independent booked cohort count" in r for r in result["await_reasons"])


def test_upstream_scoring_not_promote_awaits():
    result = _ASSESS(_passing_payload(evidence_scoring_outcome="KEEP_WATCH"))
    assert result["outcome"] == OUTCOME_AWAIT_EVIDENCE
    assert result["upstream_gate"]["evidence_scoring_met"] is False


def test_upstream_scoring_block_blocks():
    result = _ASSESS(_passing_payload(evidence_scoring_outcome="BLOCK"))
    assert result["outcome"] == OUTCOME_BLOCK


def test_upstream_cohort_not_independent_awaits():
    result = _ASSESS(_passing_payload(cohort_independence_label="CORRELATED"))
    assert result["outcome"] == OUTCOME_AWAIT_EVIDENCE
    assert result["upstream_gate"]["cohort_independence_met"] is False


def test_upstream_brief_not_approved_awaits():
    result = _ASSESS(_passing_payload(daily_alpha_brief_verdict="PENDING"))
    assert result["outcome"] == OUTCOME_AWAIT_EVIDENCE
    assert result["upstream_gate"]["daily_alpha_brief_met"] is False


def test_mission_flow_misalignment_blocks():
    result = _ASSESS(_passing_payload(mission_flow_current_stage="SOMETHING_ELSE"))
    assert result["outcome"] == OUTCOME_BLOCK
    assert result["mission_flow_aligned"] is False


# --------------------------------------------------------------------------- #
# Block / safety refusal
# --------------------------------------------------------------------------- #
def test_authorization_flag_forces_block():
    for flag in RDQ_BOUNDARY_AUTHORIZATION_FLAGS:
        result = _ASSESS(_passing_payload(**{flag: True}))
        assert result["outcome"] == OUTCOME_BLOCK, flag
        assert flag in result["forbidden_flag_hits"], flag


def test_gate_unlock_request_forces_block():
    for flag in RDQ_BOUNDARY_GATE_UNLOCK_REQUEST_FLAGS:
        result = _ASSESS(_passing_payload(**{flag: True}))
        assert result["outcome"] == OUTCOME_BLOCK, flag


def test_unlocking_a_locked_gate_forces_block():
    for flag in RDQ_BOUNDARY_GATE_LOCK_FLAGS:
        result = _ASSESS(_passing_payload(**{flag: False}))
        assert result["outcome"] == OUTCOME_BLOCK, flag


def test_forbidden_promotion_request_forces_block():
    for flag in RDQ_BOUNDARY_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        result = _ASSESS(_passing_payload(**{flag: True}))
        assert result["outcome"] == OUTCOME_BLOCK, flag


def test_executable_signal_field_on_a_record_forces_block():
    for field in RDQ_BOUNDARY_EXECUTABLE_SIGNAL_FIELDS:
        record = _rec("x", "ETH", "sell_side", "closed", 1.0, macro_event="m9")
        record[field] = "do something"
        payload = _passing_payload(evidence=[record])
        result = _ASSESS(payload)
        assert result["outcome"] == OUTCOME_BLOCK, field
        assert field in result["forbidden_flag_hits"], field


# --------------------------------------------------------------------------- #
# Human decision packet
# --------------------------------------------------------------------------- #
def test_packet_unlocks_nothing_by_default():
    packet = _PACKET()
    assert packet["unlocks_real_data_qa"] is False
    assert packet["authorizes_nothing"] is True
    assert packet["human_decision_applied"] is False
    assert packet["requires_separate_future_human_approved_step"] is True
    assert packet["human_decision_recorded"] is None
    assert list(packet["decision_options"]) == list(RDQ_BOUNDARY_DECISION_OPTIONS)
    assert list(packet["human_acknowledgements_required"]) == list(
        RDQ_BOUNDARY_HUMAN_ACKNOWLEDGEMENTS_REQUIRED
    )


def test_recorded_approval_is_captured_but_never_applied():
    payload = _passing_payload(
        human_decision="APPROVE_REAL_DATA_QA_PLANNING_ONLY"
    )
    packet = _PACKET(payload)
    assert packet["human_decision_recorded"] == "APPROVE_REAL_DATA_QA_PLANNING_ONLY"
    assert packet["human_decision_recognized"] is True
    # recording an approval still applies nothing and unlocks nothing
    assert packet["human_decision_applied"] is False
    assert packet["unlocks_real_data_qa"] is False
    assert packet["authorizes_nothing"] is True


def test_unrecognized_decision_is_not_recognized():
    packet = _PACKET(_passing_payload(human_decision="JUST_DO_IT"))
    assert packet["human_decision_recognized"] is False
    assert packet["unlocks_real_data_qa"] is False


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_assessment_is_deterministic():
    payload = _passing_payload()
    assert _ASSESS(payload) == _ASSESS(payload)


def test_build_does_not_mutate_caller_payload():
    import copy

    payload = _passing_payload()
    snapshot = copy.deepcopy(payload)
    _BUILD(payload)
    assert payload == snapshot


def test_default_sample_is_not_shared_between_builds():
    c1 = _BUILD()
    c2 = _BUILD()
    c1["block_reasons"].append("tampered")
    assert "tampered" not in c2["block_reasons"]
    assert DEFAULT_SAMPLE_BOUNDARY_INPUT["evidence"][0]["id"] == "E"


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
    assert verdict["packet_ok"] is True
    assert verdict["real_data_qa_stays_blocked"] is True


def test_every_outcome_path_validates():
    payloads = [
        DEFAULT_SAMPLE_BOUNDARY_INPUT,                       # await
        _passing_payload(),                                  # ready
        _passing_payload(evidence=[]),                       # block (no evidence)
        _passing_payload(                                    # block (external only)
            evidence=[_rec("w", "BTC", None, "closed", 5.0, source="whale")]
        ),
        _passing_payload(authorizes_trading=True),           # block (auth flag)
        _passing_payload(independent_booked_cohort_count=1),  # await
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


def test_validate_rejects_unlocked_gate():
    contract = _BUILD()
    contract["real_data_qa_blocked"] = False
    verdict = _VALIDATE(contract)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_render_is_a_readonly_markdown_string():
    text = _RENDER(_BUILD())
    assert isinstance(text, str)
    assert text.startswith(
        "# Crypto-D1 Human-Controlled Real Data QA Boundary Decision Contract"
    )
    assert "## Upstream Evidence Gate" in text
    assert "## Human Acknowledgements Required" in text
    assert "## No Execution Authorization" in text


def test_ready_contract_unlocks_no_gate():
    contract = _BUILD(_passing_payload())
    assert contract["outcome"] == OUTCOME_READY_FOR_HUMAN_DECISION
    assert contract["ready_for_human_decision"] is True
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
    for term in RDQ_BOUNDARY_FORBIDDEN_TRADE_TERMS:
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
                root = alias.name.split(".")[0]
                assert root in _ALLOWED_IMPORTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORTS, node.module


def test_module_has_no_forbidden_calls():
    for node in ast.walk(_module_ast()):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                assert func.id not in _FORBIDDEN_CALL_NAMES, func.id


def test_module_has_no_forbidden_module_tokens():
    tree = _module_ast()
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported_roots.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            imported_roots.add((node.module or "").split(".")[0])
    assert not (imported_roots & _FORBIDDEN_MODULE_TOKENS)


def test_building_writes_no_files(tmp_path):
    before = set(tmp_path.iterdir())
    _BUILD()
    _BUILD(_passing_payload())
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

"""Tests for the Crypto-D1 External Human Trader Evidence Contract (Block 163).

The contract is a pure, stdlib-only, read-only paper contract. It classifies a
static set of external human-trader evidence records into exactly one
research-only verdict (LOG_AS_OBSERVATION / DISCARD_HYPE / NO_EVIDENCE / BLOCK)
plus a per-record observation lane, and authorizes nothing -- such evidence
never counts as booked proof. These tests assert the schema, the classification
model, determinism, source isolation (no file writes / no forbidden imports),
validation, render, and the two additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_external_human_trader_evidence_contract import (  # noqa: E501
    DEFAULT_SAMPLE_HUMAN_TRADER_EVIDENCE,
    LANE_HYPE_DISCARD,
    LANE_RESEARCH_NOTE,
    LANE_RISKY_UNVERIFIED,
    OUTCOME_BLOCK,
    OUTCOME_DISCARD_HYPE,
    OUTCOME_LOG_AS_OBSERVATION,
    OUTCOME_NO_EVIDENCE,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_AUTHORIZATION_FLAGS,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_CORE_RULE,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_CURRENT_STAGE,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_EXECUTABLE_SIGNAL_FIELDS,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_TRADE_TERMS,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_LOCK_FLAGS,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_UNLOCK_REQUEST_FLAGS,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_LABEL,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_LANES,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_MODE,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_NEXT_REQUIRED_ACTION,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_OBSERVATION_ONLY_EVIDENCE_LANES,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_OUTCOMES,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_SAFETY_POSTURE,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_SCHEMA_VERSION,
    EXTERNAL_HUMAN_TRADER_EVIDENCE_STATUS,
    assess_external_human_trader_evidence,
    build_crypto_d1_external_human_trader_evidence_contract,
    render_crypto_d1_external_human_trader_evidence_contract_markdown,
    validate_crypto_d1_external_human_trader_evidence_contract,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_external_human_trader_evidence_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_external_human_trader_evidence_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_external_human_trader_evidence_contract.py"
)


def _rec(rid, note, source="external_human_trader_call", **extra):
    record = {"id": rid, "note": note, "source": source}
    record.update(extra)
    return record


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert EXTERNAL_HUMAN_TRADER_EVIDENCE_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_external_human_trader_evidence_contract.v1"
    )
    assert EXTERNAL_HUMAN_TRADER_EVIDENCE_LABEL == (
        "Block 163 - Crypto-D1 External Human Trader Evidence Contract"
    )
    assert EXTERNAL_HUMAN_TRADER_EVIDENCE_STATUS == (
        "READ_ONLY_CRYPTO_D1_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT"
    )
    assert EXTERNAL_HUMAN_TRADER_EVIDENCE_MODE == "RESEARCH_ONLY"
    assert "authorizes nothing" in EXTERNAL_HUMAN_TRADER_EVIDENCE_CORE_RULE
    assert "never counts as proof" in EXTERNAL_HUMAN_TRADER_EVIDENCE_CORE_RULE


def test_next_action_and_stage_are_build_only():
    assert EXTERNAL_HUMAN_TRADER_EVIDENCE_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT"
    )
    assert EXTERNAL_HUMAN_TRADER_EVIDENCE_CURRENT_STAGE == (
        "CRYPTO_D1_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT_REQUIRED"
    )


def test_outcomes_are_exactly_the_four_allowed_verdicts():
    assert EXTERNAL_HUMAN_TRADER_EVIDENCE_OUTCOMES == (
        OUTCOME_BLOCK,
        OUTCOME_NO_EVIDENCE,
        OUTCOME_DISCARD_HYPE,
        OUTCOME_LOG_AS_OBSERVATION,
    )
    assert set(EXTERNAL_HUMAN_TRADER_EVIDENCE_OUTCOMES) == {
        "BLOCK",
        "NO_EVIDENCE",
        "DISCARD_HYPE",
        "LOG_AS_OBSERVATION",
    }


def test_lanes_are_exactly_the_three_observation_lanes():
    assert EXTERNAL_HUMAN_TRADER_EVIDENCE_LANES == (
        LANE_RESEARCH_NOTE,
        LANE_RISKY_UNVERIFIED,
        LANE_HYPE_DISCARD,
    )


def test_safety_posture_three_true_facts_all_else_false():
    posture = EXTERNAL_HUMAN_TRADER_EVIDENCE_SAFETY_POSTURE
    assert posture["read_only"] is True
    assert posture["research_only"] is True
    assert posture["human_approval_required"] is True
    assert posture["executes"] is False
    for key, value in posture.items():
        if key in ("read_only", "research_only", "human_approval_required"):
            continue
        assert value is False, key


def test_observation_only_lanes_include_open_pnl_and_human_sources():
    lanes = EXTERNAL_HUMAN_TRADER_EVIDENCE_OBSERVATION_ONLY_EVIDENCE_LANES
    assert "open_unrealized_pnl" in lanes
    assert "signal_group_call" in lanes
    assert "influencer_call" in lanes
    assert "screenshot_pnl_evidence" in lanes


# --------------------------------------------------------------------------- #
# Classification model behavior
# --------------------------------------------------------------------------- #
def test_verifiable_note_is_a_research_note():
    a = assess_external_human_trader_evidence(
        [_rec("a", "BTC thesis with an on-chain timestamped track record")]
    )
    assert a["outcome"] == OUTCOME_LOG_AS_OBSERVATION
    assert a["research_note_count"] == 1
    assert a["classified_records"][0]["lane"] == LANE_RESEARCH_NOTE


def test_verifiable_field_flag_makes_a_research_note():
    a = assess_external_human_trader_evidence(
        [_rec("a", "a plain call", verifiable=True)]
    )
    assert a["classified_records"][0]["lane"] == LANE_RESEARCH_NOTE


def test_bare_call_is_risky_unverified():
    a = assess_external_human_trader_evidence(
        [_rec("a", "a plain directional call shared without proof")]
    )
    assert a["outcome"] == OUTCOME_LOG_AS_OBSERVATION
    assert a["risky_unverified_count"] == 1
    assert a["classified_records"][0]["lane"] == LANE_RISKY_UNVERIFIED


def test_hype_claim_is_discarded():
    a = assess_external_human_trader_evidence(
        [_rec("a", "guaranteed 100x risk-free returns, financial freedom")]
    )
    assert a["outcome"] == OUTCOME_DISCARD_HYPE
    assert a["hype_discard_count"] == 1
    assert a["classified_records"][0]["lane"] == LANE_HYPE_DISCARD


def test_all_hype_is_discard_hype_verdict():
    a = assess_external_human_trader_evidence(
        [
            _rec("a", "easy money, cant lose"),
            _rec("b", "to the moon, lambo"),
        ]
    )
    assert a["outcome"] == OUTCOME_DISCARD_HYPE
    assert a["usable_observation_count"] == 0


def test_mixed_set_logs_as_observation():
    a = assess_external_human_trader_evidence(
        [
            _rec("a", "verifiable audited track record"),
            _rec("b", "a bare call"),
            _rec("c", "guaranteed easy money"),
        ]
    )
    assert a["outcome"] == OUTCOME_LOG_AS_OBSERVATION
    assert a["research_note_count"] == 1
    assert a["risky_unverified_count"] == 1
    assert a["hype_discard_count"] == 1
    assert a["usable_observation_count"] == 2


def test_empty_payload_is_no_evidence():
    assert (
        assess_external_human_trader_evidence([])["outcome"]
        == OUTCOME_NO_EVIDENCE
    )
    assert (
        assess_external_human_trader_evidence({})["outcome"]
        == OUTCOME_NO_EVIDENCE
    )
    assert (
        assess_external_human_trader_evidence(None)["outcome"]
        == OUTCOME_NO_EVIDENCE
    )


def test_default_sample_logs_as_observation():
    contract = build_crypto_d1_external_human_trader_evidence_contract()
    assert contract["outcome"] == OUTCOME_LOG_AS_OBSERVATION
    assert contract["research_note_count"] == 1
    assert contract["risky_unverified_count"] == 1
    assert contract["hype_discard_count"] == 1


def test_log_as_observation_authorizes_nothing_and_is_not_proof():
    contract = build_crypto_d1_external_human_trader_evidence_contract(
        [_rec("a", "verifiable audited track record")]
    )
    assert contract["outcome"] == OUTCOME_LOG_AS_OBSERVATION
    assert contract["counts_as_proof"] is False
    assert contract["promotes_beyond_review"] is False
    assert contract["unlocks_real_data_qa"] is False
    assert contract["unlocks_baseline_backtest"] is False
    assert contract["unlocks_paper_trading"] is False
    assert contract["unlocks_micro_live"] is False
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["assessment"]["authorizes_nothing"] is True
    assert contract["assessment"]["counts_as_proof"] is False


# --------------------------------------------------------------------------- #
# BLOCK / safety refusal
# --------------------------------------------------------------------------- #
def test_authorization_flag_forces_block():
    recs = [_rec("a", "verifiable audited track record")]
    for flag in EXTERNAL_HUMAN_TRADER_EVIDENCE_AUTHORIZATION_FLAGS:
        a = assess_external_human_trader_evidence(
            {"evidence": recs, flag: True}
        )
        assert a["outcome"] == OUTCOME_BLOCK, flag
        assert a["block_reasons"]


def test_gate_unlock_request_forces_block():
    for flag in EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_UNLOCK_REQUEST_FLAGS:
        a = assess_external_human_trader_evidence(
            {"evidence": [], flag: True}
        )
        assert a["outcome"] == OUTCOME_BLOCK, flag


def test_unlocking_a_locked_gate_forces_block():
    for flag in EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_LOCK_FLAGS:
        a = assess_external_human_trader_evidence(
            {"evidence": [], flag: False}
        )
        assert a["outcome"] == OUTCOME_BLOCK, flag


def test_forbidden_promotion_request_forces_block():
    for flag in EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        a = assess_external_human_trader_evidence(
            {"evidence": [], flag: True}
        )
        assert a["outcome"] == OUTCOME_BLOCK, flag


def test_executable_signal_field_on_a_record_forces_block():
    for field in EXTERNAL_HUMAN_TRADER_EVIDENCE_EXECUTABLE_SIGNAL_FIELDS:
        record = _rec("x", "verifiable audited track record")
        record[field] = "do something"
        a = assess_external_human_trader_evidence([record])
        assert a["outcome"] == OUTCOME_BLOCK, field


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_assessment_is_deterministic():
    recs = [
        _rec("a", "verifiable audited track record"),
        _rec("b", "a bare call"),
    ]
    assert assess_external_human_trader_evidence(
        recs
    ) == assess_external_human_trader_evidence(recs)


def test_lane_order_independent_of_input_order():
    a = [
        _rec("a", "verifiable audited track record"),
        _rec("b", "a bare call"),
        _rec("c", "guaranteed easy money"),
    ]
    b = list(reversed(a))
    ra = assess_external_human_trader_evidence(a)
    rb = assess_external_human_trader_evidence(b)
    assert ra["outcome"] == rb["outcome"]
    assert ra["lane_summaries"] == rb["lane_summaries"]


def test_build_does_not_mutate_caller_payload():
    payload = {"evidence": [_rec("a", "verifiable audited track record")]}
    import copy

    snapshot = copy.deepcopy(payload)
    build_crypto_d1_external_human_trader_evidence_contract(payload)
    assert payload == snapshot


def test_default_sample_is_not_shared_between_builds():
    c1 = build_crypto_d1_external_human_trader_evidence_contract()
    c2 = build_crypto_d1_external_human_trader_evidence_contract()
    c1["penalty_findings"].append("tampered")
    assert "tampered" not in c2["penalty_findings"]
    assert DEFAULT_SAMPLE_HUMAN_TRADER_EVIDENCE["evidence"][0]["id"] == "h1"


# --------------------------------------------------------------------------- #
# Validation / render
# --------------------------------------------------------------------------- #
def test_default_contract_validates():
    contract = build_crypto_d1_external_human_trader_evidence_contract()
    verdict = validate_crypto_d1_external_human_trader_evidence_contract(
        contract
    )
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == ()
    assert verdict["no_trade_language"] is True
    assert verdict["flags_false"] is True
    assert verdict["gates_locked"] is True
    assert verdict["record_lanes_ok"] is True


def test_every_outcome_path_validates():
    payloads = [
        [],  # NO_EVIDENCE
        [_rec("a", "guaranteed easy money")],  # DISCARD_HYPE
        [_rec("a", "verifiable audited track record")],  # LOG_AS_OBSERVATION
        {"evidence": [], "authorizes_trading": True},  # BLOCK
    ]
    for payload in payloads:
        contract = build_crypto_d1_external_human_trader_evidence_contract(
            payload
        )
        verdict = validate_crypto_d1_external_human_trader_evidence_contract(
            contract
        )
        assert verdict["valid"] is True, contract["outcome"]


def test_validate_rejects_tampered_contract():
    contract = build_crypto_d1_external_human_trader_evidence_contract()
    contract["executes"] = True
    verdict = validate_crypto_d1_external_human_trader_evidence_contract(
        contract
    )
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_proof_claim():
    contract = build_crypto_d1_external_human_trader_evidence_contract()
    contract["counts_as_proof"] = True
    verdict = validate_crypto_d1_external_human_trader_evidence_contract(
        contract
    )
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_unlocked_gate():
    contract = build_crypto_d1_external_human_trader_evidence_contract()
    contract["real_data_qa_blocked"] = False
    verdict = validate_crypto_d1_external_human_trader_evidence_contract(
        contract
    )
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_render_is_a_readonly_markdown_string():
    contract = build_crypto_d1_external_human_trader_evidence_contract()
    text = render_crypto_d1_external_human_trader_evidence_contract_markdown(
        contract
    )
    assert isinstance(text, str)
    assert text.startswith(
        "# Crypto-D1 External Human Trader Evidence Contract"
    )
    assert "## Assessment Summary" in text
    assert "## No Execution Authorization" in text


def test_actionable_guidance_has_no_execution_verbs():
    contract = build_crypto_d1_external_human_trader_evidence_contract()
    for field in (
        "assessment_summary_section",
        "assessment_findings_section",
        "observation_only_section",
        "no_execution_authorization_section",
        "assessment_explanations",
    ):
        for line in contract[field]:
            tokens = set(
                "".join(c if c.isalpha() else " " for c in line.lower()).split()
            )
            for term in EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_TRADE_TERMS:
                assert term not in tokens, (field, term, line)


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
    build_crypto_d1_external_human_trader_evidence_contract()
    build_crypto_d1_external_human_trader_evidence_contract(
        [_rec("a", "verifiable audited track record")]
    )
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

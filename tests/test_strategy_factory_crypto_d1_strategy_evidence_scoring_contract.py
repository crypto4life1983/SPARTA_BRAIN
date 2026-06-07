"""Tests for the Crypto-D1 Strategy Evidence Scoring Contract (Block 131).

The contract is a pure, stdlib-only, read-only paper contract. It scores a
static set of evidence records into exactly one research-only verdict
(PROMOTE_TO_REVIEW / KEEP_WATCH / NEEDS_MORE_DATA / BLOCK) and authorizes
nothing. These tests assert the schema, the scoring model, determinism, source
isolation (no file writes / no forbidden imports), validation, render, and the
two additive commander_2_safety allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_strategy_evidence_scoring_contract import (  # noqa: E501
    DEFAULT_SAMPLE_EVIDENCE,
    OUTCOME_BLOCK,
    OUTCOME_KEEP_WATCH,
    OUTCOME_NEEDS_MORE_DATA,
    OUTCOME_PROMOTE_TO_REVIEW,
    STRATEGY_EVIDENCE_SCORING_AUTHORIZATION_FLAGS,
    STRATEGY_EVIDENCE_SCORING_BOOKED_STATUS_TAGS,
    STRATEGY_EVIDENCE_SCORING_CORE_RULE,
    STRATEGY_EVIDENCE_SCORING_CURRENT_STAGE,
    STRATEGY_EVIDENCE_SCORING_EXECUTABLE_SIGNAL_FIELDS,
    STRATEGY_EVIDENCE_SCORING_EXTERNAL_RESEARCH_SOURCE_TAGS,
    STRATEGY_EVIDENCE_SCORING_FORBIDDEN_PROMOTION_REQUEST_FLAGS,
    STRATEGY_EVIDENCE_SCORING_FORBIDDEN_TRADE_TERMS,
    STRATEGY_EVIDENCE_SCORING_GATE_LOCK_FLAGS,
    STRATEGY_EVIDENCE_SCORING_GATE_UNLOCK_REQUEST_FLAGS,
    STRATEGY_EVIDENCE_SCORING_LABEL,
    STRATEGY_EVIDENCE_SCORING_MIN_INDEPENDENT_COHORTS_FOR_PROMOTE,
    STRATEGY_EVIDENCE_SCORING_MODE,
    STRATEGY_EVIDENCE_SCORING_NEXT_REQUIRED_ACTION,
    STRATEGY_EVIDENCE_SCORING_OBSERVATION_ONLY_EVIDENCE_LANES,
    STRATEGY_EVIDENCE_SCORING_OPEN_STATUS_TAGS,
    STRATEGY_EVIDENCE_SCORING_OUTCOMES,
    STRATEGY_EVIDENCE_SCORING_SAFETY_POSTURE,
    STRATEGY_EVIDENCE_SCORING_SCHEMA_VERSION,
    STRATEGY_EVIDENCE_SCORING_STATUS,
    STRATEGY_EVIDENCE_SCORING_TRADE_SOURCE_TAGS,
    build_crypto_d1_strategy_evidence_scoring_contract,
    render_crypto_d1_strategy_evidence_scoring_contract_markdown,
    score_strategy_evidence,
    validate_crypto_d1_strategy_evidence_scoring_contract,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_strategy_evidence_scoring_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_strategy_evidence_scoring_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_strategy_evidence_scoring_contract.py"
)


def _rec(rid, symbol, direction, status, pnl, macro_event=None, source="trade"):
    record = {
        "id": rid,
        "symbol": symbol,
        "direction": direction,
        "status": status,
        "pnl": pnl,
        "source": source,
    }
    if macro_event is not None:
        record["macro_event"] = macro_event
    return record


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert STRATEGY_EVIDENCE_SCORING_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_strategy_evidence_scoring_contract.v1"
    )
    assert STRATEGY_EVIDENCE_SCORING_LABEL == (
        "Block 131 - Crypto-D1 Strategy Evidence Scoring Contract"
    )
    assert STRATEGY_EVIDENCE_SCORING_STATUS == (
        "READ_ONLY_CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT"
    )
    assert STRATEGY_EVIDENCE_SCORING_MODE == "RESEARCH_ONLY"
    assert "authorizes nothing" in STRATEGY_EVIDENCE_SCORING_CORE_RULE


def test_next_action_and_stage_are_build_only():
    assert STRATEGY_EVIDENCE_SCORING_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT"
    )
    assert STRATEGY_EVIDENCE_SCORING_CURRENT_STAGE == (
        "CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT_REQUIRED"
    )


def test_outcomes_are_exactly_the_four_allowed_verdicts():
    assert STRATEGY_EVIDENCE_SCORING_OUTCOMES == (
        OUTCOME_BLOCK,
        OUTCOME_NEEDS_MORE_DATA,
        OUTCOME_KEEP_WATCH,
        OUTCOME_PROMOTE_TO_REVIEW,
    )
    assert set(STRATEGY_EVIDENCE_SCORING_OUTCOMES) == {
        "BLOCK",
        "NEEDS_MORE_DATA",
        "KEEP_WATCH",
        "PROMOTE_TO_REVIEW",
    }


def test_min_independent_cohorts_threshold():
    assert STRATEGY_EVIDENCE_SCORING_MIN_INDEPENDENT_COHORTS_FOR_PROMOTE == 3


def test_source_and_status_tag_families():
    assert "trade" in STRATEGY_EVIDENCE_SCORING_TRADE_SOURCE_TAGS
    for tag in (
        "external_bot",
        "hyperliquid_whale",
        "funding_rate",
        "bitcoin_cycle_timing",
        "daily_alpha_brief",
    ):
        assert tag in STRATEGY_EVIDENCE_SCORING_EXTERNAL_RESEARCH_SOURCE_TAGS
    assert "closed" in STRATEGY_EVIDENCE_SCORING_BOOKED_STATUS_TAGS
    assert "booked" in STRATEGY_EVIDENCE_SCORING_BOOKED_STATUS_TAGS
    assert "open" in STRATEGY_EVIDENCE_SCORING_OPEN_STATUS_TAGS
    assert "unrealized" in STRATEGY_EVIDENCE_SCORING_OPEN_STATUS_TAGS


def test_safety_posture_three_true_facts_all_else_false():
    posture = STRATEGY_EVIDENCE_SCORING_SAFETY_POSTURE
    assert posture["read_only"] is True
    assert posture["research_only"] is True
    assert posture["human_approval_required"] is True
    assert posture["executes"] is False
    for key, value in posture.items():
        if key in ("read_only", "research_only", "human_approval_required"):
            continue
        assert value is False, key


def test_observation_only_lanes_include_open_pnl_and_external_sources():
    lanes = STRATEGY_EVIDENCE_SCORING_OBSERVATION_ONLY_EVIDENCE_LANES
    assert "open_unrealized_pnl" in lanes
    assert "daily_alpha_brief" in lanes
    assert "hyperliquid_whale_evidence" in lanes


# --------------------------------------------------------------------------- #
# Scoring model behavior (the user's example cases)
# --------------------------------------------------------------------------- #
def test_correlated_booked_cluster_is_needs_more_data():
    # ETH E/E2/F2: same symbol, same direction, same macro move -> one cohort.
    eth = [
        _rec("E", "ETH", "short", "closed", 1.4, "eth_dump"),
        _rec("E2", "ETH", "short", "closed", 0.9, "eth_dump"),
        _rec("F2", "ETH", "short", "closed", 1.1, "eth_dump"),
    ]
    score = score_strategy_evidence(eth)
    assert score["outcome"] == OUTCOME_NEEDS_MORE_DATA
    assert score["independent_cohorts"] == 1
    assert score["independent_positive_cohorts"] == 1
    assert score["correlated_record_count"] == 2
    assert score["booked_count"] == 3


def test_single_booked_positive_needs_more_samples():
    # ADA short F: promising but a single sample.
    score = score_strategy_evidence([_rec("F", "ADA", "short", "closed", 0.8)])
    assert score["outcome"] == OUTCOME_NEEDS_MORE_DATA
    assert score["independent_positive_cohorts"] == 1


def test_flat_booked_evidence_is_weak_keep_watch():
    # XRP long G: booked but no positive edge -> weak.
    score = score_strategy_evidence([_rec("G", "XRP", "long", "closed", 0.0)])
    assert score["outcome"] == OUTCOME_KEEP_WATCH
    assert score["independent_positive_cohorts"] == 0


def test_open_only_evidence_is_watch_not_booked_proof():
    # AVAX/SOL/ARB open shorts: observation only, not booked proof.
    opens = [
        _rec("a", "AVAX", "short", "open", 0.3),
        _rec("b", "SOL", "short", "open", 0.2),
        _rec("c", "ARB", "short", "open", 0.4),
    ]
    score = score_strategy_evidence(opens)
    assert score["outcome"] == OUTCOME_KEEP_WATCH
    assert score["booked_count"] == 0
    assert score["open_count"] == 3
    assert score["open_pnl_observation_only_count"] == 3


def test_open_plus_one_booked_positive_needs_more_booked():
    # XRP D2 (open) + F2 (booked positive): weak unless more booked appears.
    score = score_strategy_evidence(
        [
            _rec("D2", "XRP", "short", "open", 0.5),
            _rec("F2", "XRP", "short", "closed", 0.6),
        ]
    )
    assert score["outcome"] == OUTCOME_NEEDS_MORE_DATA
    assert score["booked_count"] == 1
    assert score["open_count"] == 1


def test_three_independent_positive_cohorts_promote_to_review():
    promo = [
        _rec("p1", "ETH", "short", "closed", 1.0, "eth_dump"),
        _rec("p2", "BTC", "long", "closed", 1.0, "btc_pump"),
        _rec("p3", "SOL", "short", "closed", 1.0, "sol_dump"),
    ]
    score = score_strategy_evidence(promo)
    assert score["outcome"] == OUTCOME_PROMOTE_TO_REVIEW
    assert score["independent_positive_cohorts"] == 3


def test_promote_to_review_authorizes_nothing():
    promo = [
        _rec("p1", "ETH", "short", "closed", 1.0, "eth_dump"),
        _rec("p2", "BTC", "long", "closed", 1.0, "btc_pump"),
        _rec("p3", "SOL", "short", "closed", 1.0, "sol_dump"),
    ]
    contract = build_crypto_d1_strategy_evidence_scoring_contract(promo)
    assert contract["outcome"] == OUTCOME_PROMOTE_TO_REVIEW
    assert contract["promotes_beyond_review"] is False
    assert contract["unlocks_real_data_qa"] is False
    assert contract["unlocks_baseline_backtest"] is False
    assert contract["unlocks_paper_trading"] is False
    assert contract["unlocks_micro_live"] is False
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["scoring"]["authorizes_nothing"] is True


def test_external_research_evidence_never_counts_as_proof():
    # Many external "wins" can never make a candidate reviewable.
    ext = [
        _rec("w1", "ETH", "short", "closed", 5.0, "m1", source="hyperliquid_whale"),
        _rec("w2", "BTC", "long", "closed", 5.0, "m2", source="funding_rate"),
        _rec("w3", "SOL", "short", "closed", 5.0, "m3", source="daily_alpha_brief"),
        _rec("w4", "ADA", "short", "closed", 5.0, "m4", source="external_bot"),
    ]
    score = score_strategy_evidence(ext)
    assert score["outcome"] == OUTCOME_KEEP_WATCH
    assert score["booked_count"] == 0
    assert score["external_record_count"] == 4
    assert score["independent_positive_cohorts"] == 0


def test_empty_payload_is_needs_more_data():
    assert score_strategy_evidence([])["outcome"] == OUTCOME_NEEDS_MORE_DATA
    assert score_strategy_evidence({})["outcome"] == OUTCOME_NEEDS_MORE_DATA
    assert score_strategy_evidence(None)["outcome"] == OUTCOME_NEEDS_MORE_DATA


def test_macro_event_collapses_many_symbols_into_one_event():
    # One macro move counted across many symbols is ONE correlated event.
    macro = [
        _rec("m1", "ETH", "short", "closed", 1.0, "btc_flash_crash"),
        _rec("m2", "SOL", "short", "closed", 1.0, "btc_flash_crash"),
        _rec("m3", "AVAX", "short", "closed", 1.0, "btc_flash_crash"),
    ]
    score = score_strategy_evidence(macro)
    assert score["independent_cohorts"] == 1
    assert score["outcome"] == OUTCOME_NEEDS_MORE_DATA


def test_same_symbol_and_direction_penalties_reported():
    eth = [
        _rec("E", "ETH", "short", "closed", 1.4, "eth_dump"),
        _rec("E2", "ETH", "short", "closed", 0.9, "eth_dump"),
        _rec("F2", "ETH", "short", "closed", 1.1, "eth_dump"),
    ]
    score = score_strategy_evidence(eth)
    assert score["same_symbol_duplicate_count"] == 2
    assert score["same_direction_pileup_count"] == 2
    assert score["small_sample"] is True
    assert any("correlation penalty" in p for p in score["penalty_findings"])
    assert any("small-sample penalty" in p for p in score["penalty_findings"])


# --------------------------------------------------------------------------- #
# BLOCK / safety refusal
# --------------------------------------------------------------------------- #
def test_authorization_flag_forces_block():
    promo = [
        _rec("p1", "ETH", "short", "closed", 1.0, "eth_dump"),
        _rec("p2", "BTC", "long", "closed", 1.0, "btc_pump"),
        _rec("p3", "SOL", "short", "closed", 1.0, "sol_dump"),
    ]
    for flag in STRATEGY_EVIDENCE_SCORING_AUTHORIZATION_FLAGS:
        score = score_strategy_evidence({"evidence": promo, flag: True})
        assert score["outcome"] == OUTCOME_BLOCK, flag
        assert score["block_reasons"]


def test_gate_unlock_request_forces_block():
    for flag in STRATEGY_EVIDENCE_SCORING_GATE_UNLOCK_REQUEST_FLAGS:
        score = score_strategy_evidence({"evidence": [], flag: True})
        assert score["outcome"] == OUTCOME_BLOCK, flag


def test_unlocking_a_locked_gate_forces_block():
    for flag in STRATEGY_EVIDENCE_SCORING_GATE_LOCK_FLAGS:
        score = score_strategy_evidence({"evidence": [], flag: False})
        assert score["outcome"] == OUTCOME_BLOCK, flag


def test_forbidden_promotion_request_forces_block():
    for flag in STRATEGY_EVIDENCE_SCORING_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        score = score_strategy_evidence({"evidence": [], flag: True})
        assert score["outcome"] == OUTCOME_BLOCK, flag


def test_executable_signal_field_on_a_record_forces_block():
    for field in STRATEGY_EVIDENCE_SCORING_EXECUTABLE_SIGNAL_FIELDS:
        record = _rec("x", "ETH", "short", "closed", 1.0, "eth_dump")
        record[field] = "do something"
        score = score_strategy_evidence([record])
        assert score["outcome"] == OUTCOME_BLOCK, field


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_scoring_is_deterministic():
    eth = [
        _rec("E", "ETH", "short", "closed", 1.4, "eth_dump"),
        _rec("E2", "ETH", "short", "closed", 0.9, "eth_dump"),
    ]
    first = score_strategy_evidence(eth)
    second = score_strategy_evidence(eth)
    assert first == second


def test_cohort_order_independent_of_input_order():
    a = [
        _rec("p1", "ETH", "short", "closed", 1.0, "eth_dump"),
        _rec("p2", "BTC", "long", "closed", 1.0, "btc_pump"),
        _rec("p3", "SOL", "short", "closed", 1.0, "sol_dump"),
    ]
    b = list(reversed(a))
    sa = score_strategy_evidence(a)
    sb = score_strategy_evidence(b)
    assert sa["outcome"] == sb["outcome"]
    assert sa["cohort_summaries"] == sb["cohort_summaries"]


def test_build_does_not_mutate_caller_payload():
    payload = {
        "evidence": [_rec("E", "ETH", "short", "closed", 1.4, "eth_dump")],
    }
    import copy

    snapshot = copy.deepcopy(payload)
    build_crypto_d1_strategy_evidence_scoring_contract(payload)
    assert payload == snapshot


def test_default_sample_is_not_shared_between_builds():
    c1 = build_crypto_d1_strategy_evidence_scoring_contract()
    c2 = build_crypto_d1_strategy_evidence_scoring_contract()
    c1["penalty_findings"].append("tampered")
    assert "tampered" not in c2["penalty_findings"]
    assert DEFAULT_SAMPLE_EVIDENCE["evidence"][0]["id"] == "E"


# --------------------------------------------------------------------------- #
# Validation / render
# --------------------------------------------------------------------------- #
def test_default_contract_validates():
    contract = build_crypto_d1_strategy_evidence_scoring_contract()
    verdict = validate_crypto_d1_strategy_evidence_scoring_contract(contract)
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == ()
    assert verdict["no_trade_language"] is True
    assert verdict["flags_false"] is True
    assert verdict["gates_locked"] is True


def test_every_outcome_path_validates():
    payloads = [
        [],  # NEEDS_MORE_DATA (empty)
        [_rec("F", "ADA", "short", "closed", 0.8)],  # NEEDS_MORE_DATA
        [_rec("G", "XRP", "long", "closed", 0.0)],  # KEEP_WATCH
        [
            _rec("p1", "ETH", "short", "closed", 1.0, "eth_dump"),
            _rec("p2", "BTC", "long", "closed", 1.0, "btc_pump"),
            _rec("p3", "SOL", "short", "closed", 1.0, "sol_dump"),
        ],  # PROMOTE_TO_REVIEW
        {"evidence": [], "authorizes_trading": True},  # BLOCK
    ]
    for payload in payloads:
        contract = build_crypto_d1_strategy_evidence_scoring_contract(payload)
        verdict = validate_crypto_d1_strategy_evidence_scoring_contract(contract)
        assert verdict["valid"] is True, contract["outcome"]


def test_validate_rejects_tampered_contract():
    contract = build_crypto_d1_strategy_evidence_scoring_contract()
    contract["executes"] = True
    verdict = validate_crypto_d1_strategy_evidence_scoring_contract(contract)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_unlocked_gate():
    contract = build_crypto_d1_strategy_evidence_scoring_contract()
    contract["real_data_qa_blocked"] = False
    verdict = validate_crypto_d1_strategy_evidence_scoring_contract(contract)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_render_is_a_readonly_markdown_string():
    contract = build_crypto_d1_strategy_evidence_scoring_contract()
    text = render_crypto_d1_strategy_evidence_scoring_contract_markdown(contract)
    assert isinstance(text, str)
    assert text.startswith("# Crypto-D1 Strategy Evidence Scoring Contract")
    assert "## Scoring Summary" in text
    assert "## No Execution Authorization" in text


def test_actionable_guidance_has_no_execution_verbs():
    # Build with the ETH "short" cluster; the contract's own guidance fields must
    # still never emit an execution verb even though the echoed evidence does.
    contract = build_crypto_d1_strategy_evidence_scoring_contract()
    for field in (
        "scoring_summary_section",
        "observation_only_section",
        "no_execution_authorization_section",
        "score_explanations",
    ):
        for line in contract[field]:
            tokens = set(
                "".join(c if c.isalpha() else " " for c in line.lower()).split()
            )
            for term in STRATEGY_EVIDENCE_SCORING_FORBIDDEN_TRADE_TERMS:
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
    build_crypto_d1_strategy_evidence_scoring_contract()
    build_crypto_d1_strategy_evidence_scoring_contract(
        [_rec("E", "ETH", "short", "closed", 1.4, "eth_dump")]
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

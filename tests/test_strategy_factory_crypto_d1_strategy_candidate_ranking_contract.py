"""Tests for the Crypto-D1 Strategy Candidate Ranking Contract (Block 162).

The contract is a pure, stdlib-only, read-only paper contract. It ranks a static
set of already-scored strategy candidates into exactly one research-only verdict
(SHORTLIST_FOR_REVIEW / NO_SHORTLIST / NEEDS_MORE_CANDIDATES / BLOCK) plus a
per-candidate review tier, and authorizes nothing. These tests assert the
schema, the ranking model, determinism, source isolation (no file writes / no
forbidden imports), validation, render, and the two additive commander_2_safety
allowlist entries.
"""

from __future__ import annotations

import ast
import pathlib

from sparta_commander.strategy_factory_crypto_d1_strategy_candidate_ranking_contract import (  # noqa: E501
    DEFAULT_SAMPLE_CANDIDATES,
    OUTCOME_BLOCK,
    OUTCOME_NEEDS_MORE_CANDIDATES,
    OUTCOME_NO_SHORTLIST,
    OUTCOME_SHORTLIST_FOR_REVIEW,
    STRATEGY_CANDIDATE_RANKING_AUTHORIZATION_FLAGS,
    STRATEGY_CANDIDATE_RANKING_CORE_RULE,
    STRATEGY_CANDIDATE_RANKING_CURRENT_STAGE,
    STRATEGY_CANDIDATE_RANKING_EVIDENCE_OUTCOMES,
    STRATEGY_CANDIDATE_RANKING_EXECUTABLE_SIGNAL_FIELDS,
    STRATEGY_CANDIDATE_RANKING_FORBIDDEN_PROMOTION_REQUEST_FLAGS,
    STRATEGY_CANDIDATE_RANKING_FORBIDDEN_TRADE_TERMS,
    STRATEGY_CANDIDATE_RANKING_GATE_LOCK_FLAGS,
    STRATEGY_CANDIDATE_RANKING_GATE_UNLOCK_REQUEST_FLAGS,
    STRATEGY_CANDIDATE_RANKING_LABEL,
    STRATEGY_CANDIDATE_RANKING_MIN_INDEPENDENT_COHORTS_FOR_SHORTLIST,
    STRATEGY_CANDIDATE_RANKING_MODE,
    STRATEGY_CANDIDATE_RANKING_NEXT_REQUIRED_ACTION,
    STRATEGY_CANDIDATE_RANKING_OBSERVATION_ONLY_EVIDENCE_LANES,
    STRATEGY_CANDIDATE_RANKING_OUTCOMES,
    STRATEGY_CANDIDATE_RANKING_SAFETY_POSTURE,
    STRATEGY_CANDIDATE_RANKING_SCHEMA_VERSION,
    STRATEGY_CANDIDATE_RANKING_SHORTLIST_ELIGIBLE_EVIDENCE_OUTCOMES,
    STRATEGY_CANDIDATE_RANKING_STATUS,
    STRATEGY_CANDIDATE_RANKING_TIERS,
    TIER_BLOCK,
    TIER_HOLD,
    TIER_REVIEW_SHORTLIST,
    TIER_WATCH,
    build_crypto_d1_strategy_candidate_ranking_contract,
    rank_strategy_candidates,
    render_crypto_d1_strategy_candidate_ranking_contract_markdown,
    validate_crypto_d1_strategy_candidate_ranking_contract,
)

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
_MODPATH = (
    _REPO_ROOT
    / "sparta_commander"
    / "strategy_factory_crypto_d1_strategy_candidate_ranking_contract.py"
)
_SAFETY_PATH = _REPO_ROOT / "sparta_commander" / "commander_2_safety.py"

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/strategy_factory_crypto_d1_strategy_candidate_ranking_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/test_strategy_factory_crypto_d1_strategy_candidate_ranking_contract.py"
)


def _cand(cid, evidence_outcome, cohorts=0, booked=0, family="trend_d1",
          universe="BTC"):
    return {
        "id": cid,
        "family": family,
        "universe": universe,
        "evidence_outcome": evidence_outcome,
        "independent_positive_cohorts": cohorts,
        "booked_count": booked,
    }


# --------------------------------------------------------------------------- #
# Schema / constants
# --------------------------------------------------------------------------- #
def test_schema_version_and_labels():
    assert STRATEGY_CANDIDATE_RANKING_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_strategy_candidate_ranking_contract.v1"
    )
    assert STRATEGY_CANDIDATE_RANKING_LABEL == (
        "Block 162 - Crypto-D1 Strategy Candidate Ranking Contract"
    )
    assert STRATEGY_CANDIDATE_RANKING_STATUS == (
        "READ_ONLY_CRYPTO_D1_STRATEGY_CANDIDATE_RANKING_CONTRACT"
    )
    assert STRATEGY_CANDIDATE_RANKING_MODE == "RESEARCH_ONLY"
    assert "authorizes nothing" in STRATEGY_CANDIDATE_RANKING_CORE_RULE


def test_next_action_and_stage_are_build_only():
    assert STRATEGY_CANDIDATE_RANKING_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RANKING_CONTRACT"
    )
    assert STRATEGY_CANDIDATE_RANKING_CURRENT_STAGE == (
        "CRYPTO_D1_STRATEGY_CANDIDATE_RANKING_CONTRACT_REQUIRED"
    )


def test_outcomes_are_exactly_the_four_allowed_verdicts():
    assert STRATEGY_CANDIDATE_RANKING_OUTCOMES == (
        OUTCOME_BLOCK,
        OUTCOME_NEEDS_MORE_CANDIDATES,
        OUTCOME_NO_SHORTLIST,
        OUTCOME_SHORTLIST_FOR_REVIEW,
    )
    assert set(STRATEGY_CANDIDATE_RANKING_OUTCOMES) == {
        "BLOCK",
        "NEEDS_MORE_CANDIDATES",
        "NO_SHORTLIST",
        "SHORTLIST_FOR_REVIEW",
    }


def test_tiers_are_exactly_the_four_review_tiers():
    assert STRATEGY_CANDIDATE_RANKING_TIERS == (
        TIER_BLOCK,
        TIER_HOLD,
        TIER_WATCH,
        TIER_REVIEW_SHORTLIST,
    )


def test_min_independent_cohorts_threshold():
    assert (
        STRATEGY_CANDIDATE_RANKING_MIN_INDEPENDENT_COHORTS_FOR_SHORTLIST == 3
    )


def test_only_promote_to_review_is_shortlist_eligible():
    assert STRATEGY_CANDIDATE_RANKING_SHORTLIST_ELIGIBLE_EVIDENCE_OUTCOMES == (
        "PROMOTE_TO_REVIEW",
    )
    assert set(STRATEGY_CANDIDATE_RANKING_EVIDENCE_OUTCOMES) == {
        "BLOCK",
        "NEEDS_MORE_DATA",
        "KEEP_WATCH",
        "PROMOTE_TO_REVIEW",
    }


def test_safety_posture_three_true_facts_all_else_false():
    posture = STRATEGY_CANDIDATE_RANKING_SAFETY_POSTURE
    assert posture["read_only"] is True
    assert posture["research_only"] is True
    assert posture["human_approval_required"] is True
    assert posture["executes"] is False
    for key, value in posture.items():
        if key in ("read_only", "research_only", "human_approval_required"):
            continue
        assert value is False, key


def test_observation_only_lanes_include_open_pnl_and_external_sources():
    lanes = STRATEGY_CANDIDATE_RANKING_OBSERVATION_ONLY_EVIDENCE_LANES
    assert "open_unrealized_pnl" in lanes
    assert "daily_alpha_brief" in lanes
    assert "external_human_trader_evidence" in lanes
    assert "hyperliquid_whale_evidence" in lanes


# --------------------------------------------------------------------------- #
# Ranking model behavior
# --------------------------------------------------------------------------- #
def test_promote_with_enough_cohorts_is_shortlist():
    ranking = rank_strategy_candidates(
        [_cand("a", "PROMOTE_TO_REVIEW", cohorts=3, booked=5)]
    )
    assert ranking["outcome"] == OUTCOME_SHORTLIST_FOR_REVIEW
    assert ranking["shortlist_count"] == 1
    assert ranking["ranked_shortlist_ids"] == ["a"]
    assert ranking["tiered_candidates"][0]["tier"] == TIER_REVIEW_SHORTLIST


def test_promote_with_too_few_cohorts_is_hold_not_shortlist():
    ranking = rank_strategy_candidates(
        [_cand("a", "PROMOTE_TO_REVIEW", cohorts=2, booked=5)]
    )
    assert ranking["outcome"] == OUTCOME_NO_SHORTLIST
    assert ranking["hold_count"] == 1
    assert ranking["tiered_candidates"][0]["tier"] == TIER_HOLD
    assert any(
        "thin-shortlist penalty" in p for p in ranking["penalty_findings"]
    )


def test_needs_more_data_candidate_is_hold():
    ranking = rank_strategy_candidates(
        [_cand("a", "NEEDS_MORE_DATA", cohorts=1, booked=2)]
    )
    assert ranking["outcome"] == OUTCOME_NO_SHORTLIST
    assert ranking["tiered_candidates"][0]["tier"] == TIER_HOLD


def test_keep_watch_candidate_is_watch():
    ranking = rank_strategy_candidates([_cand("a", "KEEP_WATCH")])
    assert ranking["outcome"] == OUTCOME_NO_SHORTLIST
    assert ranking["watch_count"] == 1
    assert ranking["tiered_candidates"][0]["tier"] == TIER_WATCH


def test_block_evidence_candidate_is_tier_block():
    ranking = rank_strategy_candidates([_cand("a", "BLOCK")])
    assert ranking["outcome"] == OUTCOME_NO_SHORTLIST
    assert ranking["blocked_candidate_count"] == 1
    assert ranking["tiered_candidates"][0]["tier"] == TIER_BLOCK


def test_unknown_evidence_outcome_defaults_to_watch():
    ranking = rank_strategy_candidates([_cand("a", "nonsense")])
    assert ranking["tiered_candidates"][0]["evidence_outcome"] == "KEEP_WATCH"
    assert ranking["tiered_candidates"][0]["tier"] == TIER_WATCH


def test_shortlist_ordered_by_cohorts_then_booked_then_id():
    ranking = rank_strategy_candidates(
        [
            _cand("low", "PROMOTE_TO_REVIEW", cohorts=3, booked=4),
            _cand("high", "PROMOTE_TO_REVIEW", cohorts=5, booked=4),
            _cand("mid_b", "PROMOTE_TO_REVIEW", cohorts=4, booked=9),
            _cand("mid_a", "PROMOTE_TO_REVIEW", cohorts=4, booked=9),
        ]
    )
    # 5 cohorts first, then the two 4-cohort tied on booked break by id, then 3.
    assert ranking["ranked_shortlist_ids"] == ["high", "mid_a", "mid_b", "low"]


def test_empty_payload_is_needs_more_candidates():
    assert (
        rank_strategy_candidates([])["outcome"]
        == OUTCOME_NEEDS_MORE_CANDIDATES
    )
    assert (
        rank_strategy_candidates({})["outcome"]
        == OUTCOME_NEEDS_MORE_CANDIDATES
    )
    assert (
        rank_strategy_candidates(None)["outcome"]
        == OUTCOME_NEEDS_MORE_CANDIDATES
    )


def test_all_hold_or_watch_is_no_shortlist():
    ranking = rank_strategy_candidates(
        [
            _cand("a", "NEEDS_MORE_DATA", cohorts=1),
            _cand("b", "KEEP_WATCH"),
            _cand("c", "PROMOTE_TO_REVIEW", cohorts=1),
        ]
    )
    assert ranking["outcome"] == OUTCOME_NO_SHORTLIST
    assert ranking["shortlist_count"] == 0


def test_default_sample_shortlists_only_the_strong_candidate():
    contract = build_crypto_d1_strategy_candidate_ranking_contract()
    assert contract["outcome"] == OUTCOME_SHORTLIST_FOR_REVIEW
    assert contract["ranked_shortlist_ids"] == ["cand_btc_trend"]
    assert contract["shortlist_count"] == 1


def test_shortlist_for_review_authorizes_nothing():
    contract = build_crypto_d1_strategy_candidate_ranking_contract(
        [_cand("a", "PROMOTE_TO_REVIEW", cohorts=3, booked=5)]
    )
    assert contract["outcome"] == OUTCOME_SHORTLIST_FOR_REVIEW
    assert contract["promotes_beyond_review"] is False
    assert contract["unlocks_real_data_qa"] is False
    assert contract["unlocks_baseline_backtest"] is False
    assert contract["unlocks_paper_trading"] is False
    assert contract["unlocks_micro_live"] is False
    assert contract["real_data_qa_blocked"] is True
    assert contract["baseline_backtest_blocked"] is True
    assert contract["paper_trading_gate_locked"] is True
    assert contract["micro_live_gate_locked"] is True
    assert contract["ranking"]["authorizes_nothing"] is True


# --------------------------------------------------------------------------- #
# BLOCK / safety refusal
# --------------------------------------------------------------------------- #
def test_authorization_flag_forces_block():
    cands = [_cand("a", "PROMOTE_TO_REVIEW", cohorts=3, booked=5)]
    for flag in STRATEGY_CANDIDATE_RANKING_AUTHORIZATION_FLAGS:
        ranking = rank_strategy_candidates({"candidates": cands, flag: True})
        assert ranking["outcome"] == OUTCOME_BLOCK, flag
        assert ranking["block_reasons"]


def test_gate_unlock_request_forces_block():
    for flag in STRATEGY_CANDIDATE_RANKING_GATE_UNLOCK_REQUEST_FLAGS:
        ranking = rank_strategy_candidates({"candidates": [], flag: True})
        assert ranking["outcome"] == OUTCOME_BLOCK, flag


def test_unlocking_a_locked_gate_forces_block():
    for flag in STRATEGY_CANDIDATE_RANKING_GATE_LOCK_FLAGS:
        ranking = rank_strategy_candidates({"candidates": [], flag: False})
        assert ranking["outcome"] == OUTCOME_BLOCK, flag


def test_forbidden_promotion_request_forces_block():
    for flag in STRATEGY_CANDIDATE_RANKING_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        ranking = rank_strategy_candidates({"candidates": [], flag: True})
        assert ranking["outcome"] == OUTCOME_BLOCK, flag


def test_executable_signal_field_on_a_candidate_forces_block():
    for field in STRATEGY_CANDIDATE_RANKING_EXECUTABLE_SIGNAL_FIELDS:
        cand = _cand("x", "PROMOTE_TO_REVIEW", cohorts=3, booked=5)
        cand[field] = "do something"
        ranking = rank_strategy_candidates([cand])
        assert ranking["outcome"] == OUTCOME_BLOCK, field


# --------------------------------------------------------------------------- #
# Determinism / isolation
# --------------------------------------------------------------------------- #
def test_ranking_is_deterministic():
    cands = [
        _cand("a", "PROMOTE_TO_REVIEW", cohorts=3, booked=5),
        _cand("b", "KEEP_WATCH"),
    ]
    assert rank_strategy_candidates(cands) == rank_strategy_candidates(cands)


def test_ranking_order_independent_of_input_order():
    a = [
        _cand("a", "PROMOTE_TO_REVIEW", cohorts=5, booked=4),
        _cand("b", "PROMOTE_TO_REVIEW", cohorts=3, booked=4),
        _cand("c", "PROMOTE_TO_REVIEW", cohorts=4, booked=4),
    ]
    b = list(reversed(a))
    ra = rank_strategy_candidates(a)
    rb = rank_strategy_candidates(b)
    assert ra["outcome"] == rb["outcome"]
    assert ra["ranked_shortlist_ids"] == rb["ranked_shortlist_ids"]
    assert ra["tier_summaries"] == rb["tier_summaries"]


def test_build_does_not_mutate_caller_payload():
    payload = {
        "candidates": [_cand("a", "PROMOTE_TO_REVIEW", cohorts=3, booked=5)],
    }
    import copy

    snapshot = copy.deepcopy(payload)
    build_crypto_d1_strategy_candidate_ranking_contract(payload)
    assert payload == snapshot


def test_default_sample_is_not_shared_between_builds():
    c1 = build_crypto_d1_strategy_candidate_ranking_contract()
    c2 = build_crypto_d1_strategy_candidate_ranking_contract()
    c1["penalty_findings"].append("tampered")
    assert "tampered" not in c2["penalty_findings"]
    assert DEFAULT_SAMPLE_CANDIDATES["candidates"][0]["id"] == "cand_btc_trend"


# --------------------------------------------------------------------------- #
# Validation / render
# --------------------------------------------------------------------------- #
def test_default_contract_validates():
    contract = build_crypto_d1_strategy_candidate_ranking_contract()
    verdict = validate_crypto_d1_strategy_candidate_ranking_contract(contract)
    assert verdict["valid"] is True
    assert verdict["missing_fields"] == ()
    assert verdict["no_trade_language"] is True
    assert verdict["flags_false"] is True
    assert verdict["gates_locked"] is True
    assert verdict["tiers_ok"] is True


def test_every_outcome_path_validates():
    payloads = [
        [],  # NEEDS_MORE_CANDIDATES (empty)
        [_cand("a", "KEEP_WATCH")],  # NO_SHORTLIST
        [_cand("a", "PROMOTE_TO_REVIEW", cohorts=3, booked=5)],  # SHORTLIST
        {"candidates": [], "authorizes_trading": True},  # BLOCK
    ]
    for payload in payloads:
        contract = build_crypto_d1_strategy_candidate_ranking_contract(payload)
        verdict = validate_crypto_d1_strategy_candidate_ranking_contract(
            contract
        )
        assert verdict["valid"] is True, contract["outcome"]


def test_validate_rejects_tampered_contract():
    contract = build_crypto_d1_strategy_candidate_ranking_contract()
    contract["executes"] = True
    verdict = validate_crypto_d1_strategy_candidate_ranking_contract(contract)
    assert verdict["valid"] is False
    assert verdict["flags_false"] is False


def test_validate_rejects_unlocked_gate():
    contract = build_crypto_d1_strategy_candidate_ranking_contract()
    contract["real_data_qa_blocked"] = False
    verdict = validate_crypto_d1_strategy_candidate_ranking_contract(contract)
    assert verdict["valid"] is False
    assert verdict["gates_locked"] is False


def test_render_is_a_readonly_markdown_string():
    contract = build_crypto_d1_strategy_candidate_ranking_contract()
    text = render_crypto_d1_strategy_candidate_ranking_contract_markdown(
        contract
    )
    assert isinstance(text, str)
    assert text.startswith("# Crypto-D1 Strategy Candidate Ranking Contract")
    assert "## Ranking Summary" in text
    assert "## No Execution Authorization" in text


def test_actionable_guidance_has_no_execution_verbs():
    contract = build_crypto_d1_strategy_candidate_ranking_contract()
    for field in (
        "ranking_summary_section",
        "ranking_findings_section",
        "observation_only_section",
        "no_execution_authorization_section",
        "ranking_explanations",
    ):
        for line in contract[field]:
            tokens = set(
                "".join(c if c.isalpha() else " " for c in line.lower()).split()
            )
            for term in STRATEGY_CANDIDATE_RANKING_FORBIDDEN_TRADE_TERMS:
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
    build_crypto_d1_strategy_candidate_ranking_contract()
    build_crypto_d1_strategy_candidate_ranking_contract(
        [_cand("a", "PROMOTE_TO_REVIEW", cohorts=3, booked=5)]
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

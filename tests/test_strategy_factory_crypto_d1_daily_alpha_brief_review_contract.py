"""Tests for the Crypto-D1 Daily Alpha Brief Review Contract (Bundle 65
Block 127). Verifies the read-only review of a daily alpha brief research
result: it judges whether the brief is safe, complete, and research-only, with
outcome precedence REJECTED > PARKED > NEEDS_MORE_INFO > READY > AWAIT. The
review fetches no data, calls no API, inspects no dataset, authorizes nothing,
never promotes a brief beyond WATCH / RESEARCH_ONLY, and unlocks no gate. The
highest stance it can hold is WATCH / RESEARCH_ONLY."""

from __future__ import annotations

import ast
import pathlib
import re

from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_review_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION,
    DAILY_ALPHA_BRIEF_REVIEW_LABEL,
    DAILY_ALPHA_BRIEF_REVIEW_STATUS,
    DAILY_ALPHA_BRIEF_REVIEW_MODE,
    DAILY_ALPHA_BRIEF_REVIEW_CORE_RULE,
    DAILY_ALPHA_BRIEF_REVIEW_SAFETY_POSTURE,
    DAILY_ALPHA_BRIEF_REVIEW_OBSERVATION_ONLY_EVIDENCE_LANES,
    DAILY_ALPHA_BRIEF_REVIEW_OUTCOMES,
    OUTCOME_REJECTED,
    OUTCOME_PARKED,
    OUTCOME_NEEDS_MORE_INFO,
    OUTCOME_READY,
    OUTCOME_AWAIT,
    DAILY_ALPHA_BRIEF_REVIEW_STANCE,
    DAILY_ALPHA_BRIEF_REVIEW_AUTHORIZATION_FLAGS,
    DAILY_ALPHA_BRIEF_REVIEW_GATE_LOCK_FLAGS,
    DAILY_ALPHA_BRIEF_REVIEW_GATE_UNLOCK_REQUEST_FLAGS,
    DAILY_ALPHA_BRIEF_REVIEW_FORBIDDEN_TRADE_TERMS,
    DAILY_ALPHA_BRIEF_REVIEW_NEXT_REQUIRED_ACTION,
    DAILY_ALPHA_BRIEF_REVIEW_CURRENT_STAGE,
    DEFAULT_SAMPLE_UPSTREAM,
    review_daily_alpha_brief,
    build_crypto_d1_daily_alpha_brief_review_contract,
    validate_crypto_d1_daily_alpha_brief_review_contract,
    render_crypto_d1_daily_alpha_brief_review_contract_markdown,
)
from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_research_contract import (  # noqa: E501
    build_crypto_d1_daily_alpha_brief_research_contract,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_daily_alpha_brief_review_contract.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/"
    "strategy_factory_crypto_d1_daily_alpha_brief_review_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/"
    "test_strategy_factory_crypto_d1_daily_alpha_brief_review_contract.py"
)


def _valid_upstream(**overrides):
    """A complete, safe, research-only upstream brief result -> reviews READY."""
    base = dict(DEFAULT_SAMPLE_UPSTREAM)
    base.update(overrides)
    return base


# --------------------------------------------------------------------------
# Schema / constants
# --------------------------------------------------------------------------

def test_schema_version_is_v1():
    assert DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_daily_alpha_brief_review_contract.v1"
    )


def test_contract_label_is_exact_block_127():
    assert DAILY_ALPHA_BRIEF_REVIEW_LABEL == (
        "Block 127 - Crypto-D1 Daily Alpha Brief Review Contract"
    )
    c = build_crypto_d1_daily_alpha_brief_review_contract()
    assert c["label"] == DAILY_ALPHA_BRIEF_REVIEW_LABEL


def test_mode_is_research_only():
    assert DAILY_ALPHA_BRIEF_REVIEW_MODE == "RESEARCH_ONLY"
    c = build_crypto_d1_daily_alpha_brief_review_contract()
    assert c["mode"] == "RESEARCH_ONLY"


def test_status_constant():
    assert DAILY_ALPHA_BRIEF_REVIEW_STATUS == (
        "READ_ONLY_CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT"
    )


def test_core_rule_watch_not_trade():
    rule = DAILY_ALPHA_BRIEF_REVIEW_CORE_RULE.lower()
    assert "never promotes" in rule
    assert "watch / research_only" in rule
    assert "authorizes nothing" in rule


def test_next_action_and_stage_constants():
    assert DAILY_ALPHA_BRIEF_REVIEW_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT"
    )
    assert DAILY_ALPHA_BRIEF_REVIEW_CURRENT_STAGE == (
        "CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_REQUIRED"
    )


def test_outcome_precedence_enumeration():
    assert DAILY_ALPHA_BRIEF_REVIEW_OUTCOMES == (
        OUTCOME_REJECTED,
        OUTCOME_PARKED,
        OUTCOME_NEEDS_MORE_INFO,
        OUTCOME_READY,
        OUTCOME_AWAIT,
    )


# --------------------------------------------------------------------------
# (1) Valid research output reviews as READY, still WATCH / RESEARCH_ONLY
# --------------------------------------------------------------------------

def test_valid_research_output_reviews_as_ready_and_stays_watch():
    # Feed the REAL upstream research contract output.
    upstream = build_crypto_d1_daily_alpha_brief_research_contract()
    c = build_crypto_d1_daily_alpha_brief_review_contract(upstream)
    assert c["outcome"] == OUTCOME_READY
    assert c["review_stance"] == "WATCH"
    assert c["mode"] == "RESEARCH_ONLY"
    # still authorizes nothing
    assert c["executes"] is False
    assert c["authorizes_trading"] is False
    assert c["promotes_beyond_watch"] is False


def test_default_sample_upstream_reviews_as_ready():
    c = build_crypto_d1_daily_alpha_brief_review_contract()
    assert c["outcome"] == OUTCOME_READY
    assert c["upstream_present"] is True
    assert c["review_stance"] == DAILY_ALPHA_BRIEF_REVIEW_STANCE


# --------------------------------------------------------------------------
# (2) Missing upstream -> AWAIT / NEEDS_MORE_INFO
# --------------------------------------------------------------------------

def test_missing_upstream_returns_await():
    assert review_daily_alpha_brief(None)["outcome"] == OUTCOME_AWAIT
    assert review_daily_alpha_brief({})["outcome"] == OUTCOME_AWAIT
    c = build_crypto_d1_daily_alpha_brief_review_contract(None)
    # None falls back to the default sample (READY); explicit {} is AWAIT
    assert c["outcome"] == OUTCOME_READY
    c_empty = build_crypto_d1_daily_alpha_brief_review_contract({})
    assert c_empty["outcome"] == OUTCOME_AWAIT
    assert c_empty["upstream_present"] is False


def test_non_dict_upstream_returns_await():
    c = build_crypto_d1_daily_alpha_brief_review_contract(["nope"])
    assert c["outcome"] == OUTCOME_AWAIT
    assert c["upstream_present"] is False


# --------------------------------------------------------------------------
# (3) executes=True is rejected
# --------------------------------------------------------------------------

def test_executes_true_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_review_contract(
        _valid_upstream(executes=True)
    )
    assert c["outcome"] == OUTCOME_REJECTED
    assert any("executes" in r for r in c["rejection_reasons"])
    # rejection unlocks nothing
    assert c["unlocks_downstream_gate"] is False
    assert c["real_data_qa_blocked"] is True


# --------------------------------------------------------------------------
# (4) research_only=False is rejected
# --------------------------------------------------------------------------

def test_research_only_false_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_review_contract(
        _valid_upstream(research_only=False)
    )
    assert c["outcome"] == OUTCOME_REJECTED
    assert any("research_only" in r for r in c["rejection_reasons"])


# --------------------------------------------------------------------------
# (5) any authorization flag True is rejected
# --------------------------------------------------------------------------

def test_each_authorization_flag_true_is_rejected():
    for flag in DAILY_ALPHA_BRIEF_REVIEW_AUTHORIZATION_FLAGS:
        c = build_crypto_d1_daily_alpha_brief_review_contract(
            _valid_upstream(**{flag: True})
        )
        assert c["outcome"] == OUTCOME_REJECTED, flag
        assert any(flag in r for r in c["rejection_reasons"]), flag


# --------------------------------------------------------------------------
# (6) any promotion beyond WATCH is rejected
# --------------------------------------------------------------------------

def test_promotion_via_stance_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_review_contract(
        _valid_upstream(alpha_stance="STRONG")
    )
    assert c["outcome"] == OUTCOME_REJECTED
    assert any("promote" in r.lower() for r in c["rejection_reasons"])


def test_promotion_via_decision_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_review_contract(
        _valid_upstream(decision="PASS")
    )
    assert c["outcome"] == OUTCOME_REJECTED


def test_promotion_via_explicit_flag_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_review_contract(
        _valid_upstream(promote=True)
    )
    assert c["outcome"] == OUTCOME_REJECTED
    # the review never promotes its own stance regardless
    assert c["review_stance"] == "WATCH"
    assert c["promotes_beyond_watch"] is False


# --------------------------------------------------------------------------
# (7) any gate unlock request is rejected
# --------------------------------------------------------------------------

def test_gate_lock_flipped_false_is_rejected():
    for flag in DAILY_ALPHA_BRIEF_REVIEW_GATE_LOCK_FLAGS:
        c = build_crypto_d1_daily_alpha_brief_review_contract(
            _valid_upstream(**{flag: False})
        )
        assert c["outcome"] == OUTCOME_REJECTED, flag
    # the review's own gate states stay locked
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_gate_unlock_request_flag_is_rejected():
    for flag in DAILY_ALPHA_BRIEF_REVIEW_GATE_UNLOCK_REQUEST_FLAGS:
        c = build_crypto_d1_daily_alpha_brief_review_contract(
            _valid_upstream(**{flag: True})
        )
        assert c["outcome"] == OUTCOME_REJECTED, flag


# --------------------------------------------------------------------------
# (8) evidence lanes remain observation-only
# --------------------------------------------------------------------------

def test_observation_only_evidence_lanes_constant():
    assert DAILY_ALPHA_BRIEF_REVIEW_OBSERVATION_ONLY_EVIDENCE_LANES == (
        "external_bot_evidence",
        "hyperliquid_whale_evidence",
        "funding_rate_evidence",
        "bitcoin_cycle_timing_evidence",
        "daily_alpha_brief_research",
    )


def test_evidence_lanes_observation_only_across_every_outcome():
    payloads = [
        None,                                    # READY (default sample)
        {},                                      # AWAIT
        _valid_upstream(),                       # READY
        _valid_upstream(missing_lanes=["funding_rate_evidence"]),  # NMI
        _valid_upstream(executes=True),          # REJECTED
        _valid_upstream(requested_forbidden_flags=["places_order"]),  # PARKED
    ]
    for payload in payloads:
        c = build_crypto_d1_daily_alpha_brief_review_contract(payload)
        assert tuple(c["observation_only_evidence_lanes"]) == (
            DAILY_ALPHA_BRIEF_REVIEW_OBSERVATION_ONLY_EVIDENCE_LANES
        )
        text = " ".join(c["observation_only_section"]).lower()
        assert "observation-only" in text
        assert "wired" in text and "automation" in text


# --------------------------------------------------------------------------
# (9) highest possible stance is WATCH
# --------------------------------------------------------------------------

def test_review_stance_is_always_watch():
    payloads = [
        None,
        {},
        _valid_upstream(),
        _valid_upstream(executes=True),
        _valid_upstream(alpha_stance="STRONG"),
        _valid_upstream(missing_lanes=["funding_rate_evidence"]),
        _valid_upstream(requested_forbidden_flags=["allow_execution"]),
    ]
    for payload in payloads:
        c = build_crypto_d1_daily_alpha_brief_review_contract(payload)
        assert c["review_stance"] == "WATCH"
        assert c["promotes_beyond_watch"] is False
        assert c["review"]["authorizes_nothing"] is True


def test_outcome_precedence_rejected_beats_park_and_nmi():
    # An unsafe + incomplete + forbidden-flagged upstream still REJECTS.
    c = build_crypto_d1_daily_alpha_brief_review_contract(
        _valid_upstream(
            executes=True,
            missing_lanes=["funding_rate_evidence"],
            requested_forbidden_flags=["places_order"],
        )
    )
    assert c["outcome"] == OUTCOME_REJECTED


def test_park_beats_needs_more_info():
    c = build_crypto_d1_daily_alpha_brief_review_contract(
        _valid_upstream(
            missing_lanes=["funding_rate_evidence"],
            requested_forbidden_flags=["places_order"],
        )
    )
    assert c["outcome"] == OUTCOME_PARKED


def test_needs_more_info_for_incomplete_but_safe_upstream():
    c = build_crypto_d1_daily_alpha_brief_review_contract(
        _valid_upstream(
            decision="AWAIT",
            alpha_stance="INCOMPLETE_EVIDENCE",
            missing_lanes=["funding_rate_evidence"],
            present_lanes=["external_bot_evidence_intake"],
        )
    )
    assert c["outcome"] == OUTCOME_NEEDS_MORE_INFO


# --------------------------------------------------------------------------
# Posture flags / safety posture object
# --------------------------------------------------------------------------

def test_contract_posture_flags():
    c = build_crypto_d1_daily_alpha_brief_review_contract()
    assert c["read_only"] is True
    assert c["executes"] is False
    assert c["research_only"] is True
    assert c["human_approval_required"] is True
    assert c["authorizes_trading"] is False
    assert c["authorizes_data_fetch"] is False
    assert c["authorizes_backtest"] is False
    assert c["authorizes_paper_trading"] is False
    assert c["authorizes_live_trading"] is False
    assert c["authorizes_broker_exchange"] is False
    assert c["authorizes_automation"] is False
    assert c["authorizes_real_world_action"] is False
    assert c["unlocks_downstream_gate"] is False
    assert c["requires_independent_confirmation"] is True


def test_gates_remain_blocked_and_locked():
    c = build_crypto_d1_daily_alpha_brief_review_contract()
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_safety_posture_object_proves_required_values():
    posture = DAILY_ALPHA_BRIEF_REVIEW_SAFETY_POSTURE
    assert posture["read_only"] is True
    assert posture["research_only"] is True
    assert posture["executes"] is False
    assert posture["human_approval_required"] is True
    assert posture["authorizes_trading"] is False
    assert posture["authorizes_data_fetch"] is False
    assert posture["authorizes_backtest"] is False
    assert posture["authorizes_paper_trading"] is False
    assert posture["authorizes_live_trading"] is False
    assert posture["authorizes_broker_exchange"] is False
    assert posture["authorizes_automation"] is False
    c = build_crypto_d1_daily_alpha_brief_review_contract()
    assert c["safety_posture"] == posture


def test_safety_posture_is_isolated_copy():
    c = build_crypto_d1_daily_alpha_brief_review_contract()
    c["safety_posture"]["executes"] = True
    fresh = build_crypto_d1_daily_alpha_brief_review_contract()
    assert fresh["safety_posture"]["executes"] is False
    assert DAILY_ALPHA_BRIEF_REVIEW_SAFETY_POSTURE["executes"] is False


# --------------------------------------------------------------------------
# No trade language in actionable output
# --------------------------------------------------------------------------

_ACTIONABLE_FIELDS = (
    "outcome",
    "review_stance",
    "operator_next_step",
    "review_summary_section",
    "observation_only_section",
    "no_execution_authorization_section",
)


def _iter_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _iter_strings(item)


def _has_forbidden_word(text):
    words = set(re.findall(r"[a-z]+", text.lower()))
    return {t for t in DAILY_ALPHA_BRIEF_REVIEW_FORBIDDEN_TRADE_TERMS if t in words}


def test_no_forbidden_trade_verbs_in_actionable_output():
    payloads = [
        None,
        {},
        _valid_upstream(),
        _valid_upstream(missing_lanes=["funding_rate_evidence"]),
        _valid_upstream(requested_forbidden_flags=["allow_execution"]),
    ]
    for payload in payloads:
        c = build_crypto_d1_daily_alpha_brief_review_contract(payload)
        for field in _ACTIONABLE_FIELDS:
            for text in _iter_strings(c.get(field)):
                hits = _has_forbidden_word(text)
                assert not hits, (field, text, hits)


def test_forbidden_trade_terms_constant():
    assert DAILY_ALPHA_BRIEF_REVIEW_FORBIDDEN_TRADE_TERMS == (
        "buy",
        "sell",
        "long",
        "short",
        "entry",
        "exit",
        "order",
    )


# --------------------------------------------------------------------------
# Determinism / isolation
# --------------------------------------------------------------------------

def test_deterministic_output():
    a = build_crypto_d1_daily_alpha_brief_review_contract(_valid_upstream())
    b = build_crypto_d1_daily_alpha_brief_review_contract(_valid_upstream())
    assert a == b


def test_caller_input_not_mutated():
    ev = _valid_upstream(requested_forbidden_flags=["places_order"])
    snapshot = _valid_upstream(requested_forbidden_flags=["places_order"])
    build_crypto_d1_daily_alpha_brief_review_contract(ev)
    assert ev == snapshot


def test_returned_contract_is_isolated():
    c = build_crypto_d1_daily_alpha_brief_review_contract(_valid_upstream())
    c["review_summary_section"].append("TAMPERED")
    c["safety_posture"]["executes"] = True
    fresh = build_crypto_d1_daily_alpha_brief_review_contract(_valid_upstream())
    assert "TAMPERED" not in fresh["review_summary_section"]
    assert fresh["safety_posture"]["executes"] is False


def test_default_sample_upstream_not_mutated_by_default_build():
    before = dict(DEFAULT_SAMPLE_UPSTREAM)
    build_crypto_d1_daily_alpha_brief_review_contract()
    assert DEFAULT_SAMPLE_UPSTREAM == before


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def test_ready_contract_validates():
    c = build_crypto_d1_daily_alpha_brief_review_contract()
    v = validate_crypto_d1_daily_alpha_brief_review_contract(c)
    assert v["valid"] is True
    assert v["missing_fields"] == ()
    assert v["no_trade_language"] is True
    assert v["posture_ok"] is True
    assert v["label_ok"] is True
    assert v["gates_locked"] is True


def test_every_outcome_branch_validates():
    for payload in (
        None,
        {},
        _valid_upstream(),
        _valid_upstream(missing_lanes=["funding_rate_evidence"]),
        _valid_upstream(requested_forbidden_flags=["places_order"]),
    ):
        c = build_crypto_d1_daily_alpha_brief_review_contract(payload)
        v = validate_crypto_d1_daily_alpha_brief_review_contract(c)
        assert v["valid"] is True, (payload, v)


def test_validation_rejects_tampered_executes_flag():
    c = build_crypto_d1_daily_alpha_brief_review_contract()
    c["executes"] = True
    v = validate_crypto_d1_daily_alpha_brief_review_contract(c)
    assert v["valid"] is False
    assert v["flags_false"] is False


def test_validation_rejects_tampered_review_stance():
    c = build_crypto_d1_daily_alpha_brief_review_contract()
    c["review_stance"] = "STRONG"
    v = validate_crypto_d1_daily_alpha_brief_review_contract(c)
    assert v["valid"] is False
    assert v["stance_ok"] is False


def test_validation_rejects_non_dict():
    v = validate_crypto_d1_daily_alpha_brief_review_contract("nope")
    assert v["valid"] is False


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def test_render_is_readonly_markdown_string():
    c = build_crypto_d1_daily_alpha_brief_review_contract()
    md = render_crypto_d1_daily_alpha_brief_review_contract_markdown(c)
    assert isinstance(md, str)
    assert "# Crypto-D1 Daily Alpha Brief Review Contract" in md
    assert DAILY_ALPHA_BRIEF_REVIEW_LABEL in md
    assert "Outcome: READY" in md
    assert "Review stance: WATCH" in md


def test_render_has_no_forbidden_trade_verbs():
    for payload in (None, _valid_upstream(), {}):
        c = build_crypto_d1_daily_alpha_brief_review_contract(payload)
        md = render_crypto_d1_daily_alpha_brief_review_contract_markdown(c)
        for line in md.splitlines():
            assert not _has_forbidden_word(line), line


# --------------------------------------------------------------------------
# (10) (11) Pure-stdlib / no-IO source posture (AST-level)
# --------------------------------------------------------------------------

_ALLOWED_IMPORTS = {"__future__", "typing"}

_FORBIDDEN_CALL_NAMES = {
    "open",
    "__import__",
    "eval",
    "exec",
    "compile",
    "input",
}
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


def _module_tree():
    return ast.parse(_MODPATH.read_text(encoding="utf-8"))


def test_module_imports_are_pure_stdlib_only():
    tree = _module_tree()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root in _ALLOWED_IMPORTS, alias.name
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or "").split(".")[0]
            assert root in _ALLOWED_IMPORTS, node.module


def test_module_has_no_io_network_subprocess_or_dynamic_import_calls():
    tree = _module_tree()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Name):
                assert func.id not in _FORBIDDEN_CALL_NAMES, func.id
            if isinstance(func, ast.Attribute):
                value = func.value
                if isinstance(value, ast.Name):
                    assert value.id not in _FORBIDDEN_MODULE_TOKENS, (
                        value.id + "." + func.attr
                    )


def test_module_source_has_no_dunder_import_or_open():
    src = _MODPATH.read_text(encoding="utf-8")
    assert "__import__(" not in src
    assert "open(" not in src
    assert "import subprocess" not in src
    assert "import socket" not in src
    assert "import os" not in src
    assert "import requests" not in src


# --------------------------------------------------------------------------
# (12) commander_2_safety allowlist: exactly two additive lines
# --------------------------------------------------------------------------

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

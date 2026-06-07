"""Tests for the Crypto-D1 Daily Alpha Brief Approval Contract (Bundle 66
Block 129). Verifies the read-only approval of a daily alpha brief *review*
result: it judges whether the reviewed brief may be filed as research evidence,
with outcome precedence REJECTED > PARKED > NEEDS_MORE_INFO > APPROVED > AWAIT.
An APPROVED verdict means ONLY
DAILY_ALPHA_BRIEF_APPROVED_FOR_RESEARCH_RECORD; it never unlocks real-data QA,
baseline, backtest, paper trading, live trading, broker/exchange, automation,
or any runtime/dashboard write, never promotes a brief beyond WATCH /
RESEARCH_ONLY, and authorizes nothing. The approval fetches no data, calls no
API, inspects no dataset, and runs no QA/backtest/simulation."""

from __future__ import annotations

import ast
import pathlib
import re

from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_approval_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION,
    DAILY_ALPHA_BRIEF_APPROVAL_LABEL,
    DAILY_ALPHA_BRIEF_APPROVAL_STATUS,
    DAILY_ALPHA_BRIEF_APPROVAL_MODE,
    DAILY_ALPHA_BRIEF_APPROVAL_CORE_RULE,
    DAILY_ALPHA_BRIEF_APPROVAL_RESULT,
    DAILY_ALPHA_BRIEF_APPROVAL_SAFETY_POSTURE,
    DAILY_ALPHA_BRIEF_APPROVAL_OBSERVATION_ONLY_EVIDENCE_LANES,
    DAILY_ALPHA_BRIEF_APPROVAL_OUTCOMES,
    OUTCOME_REJECTED,
    OUTCOME_PARKED,
    OUTCOME_NEEDS_MORE_INFO,
    OUTCOME_APPROVED,
    OUTCOME_AWAIT,
    DAILY_ALPHA_BRIEF_APPROVAL_STANCE,
    DAILY_ALPHA_BRIEF_APPROVAL_AUTHORIZATION_FLAGS,
    DAILY_ALPHA_BRIEF_APPROVAL_GATE_LOCK_FLAGS,
    DAILY_ALPHA_BRIEF_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS,
    DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_APPROVAL_REQUEST_FLAGS,
    DAILY_ALPHA_BRIEF_APPROVAL_EXECUTABLE_SIGNAL_FIELDS,
    DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_TRADE_TERMS,
    DAILY_ALPHA_BRIEF_APPROVAL_NEXT_REQUIRED_ACTION,
    DAILY_ALPHA_BRIEF_APPROVAL_CURRENT_STAGE,
    DEFAULT_SAMPLE_UPSTREAM,
    approve_daily_alpha_brief,
    build_crypto_d1_daily_alpha_brief_approval_contract,
    validate_crypto_d1_daily_alpha_brief_approval_contract,
    render_crypto_d1_daily_alpha_brief_approval_contract_markdown,
)
from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_review_contract import (  # noqa: E501
    build_crypto_d1_daily_alpha_brief_review_contract,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_daily_alpha_brief_approval_contract.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/"
    "strategy_factory_crypto_d1_daily_alpha_brief_approval_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/"
    "test_strategy_factory_crypto_d1_daily_alpha_brief_approval_contract.py"
)


def _valid_upstream(**overrides):
    """A complete, safe, research-only upstream review result -> APPROVED."""
    base = dict(DEFAULT_SAMPLE_UPSTREAM)
    base.update(overrides)
    return base


# --------------------------------------------------------------------------
# Schema / constants
# --------------------------------------------------------------------------

def test_schema_version_is_v1():
    assert DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_daily_alpha_brief_approval_contract.v1"
    )


def test_contract_label_is_exact_block_129():
    assert DAILY_ALPHA_BRIEF_APPROVAL_LABEL == (
        "Block 129 - Crypto-D1 Daily Alpha Brief Approval Contract"
    )
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    assert c["label"] == DAILY_ALPHA_BRIEF_APPROVAL_LABEL


def test_mode_is_research_only():
    assert DAILY_ALPHA_BRIEF_APPROVAL_MODE == "RESEARCH_ONLY"
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    assert c["mode"] == "RESEARCH_ONLY"


def test_status_constant():
    assert DAILY_ALPHA_BRIEF_APPROVAL_STATUS == (
        "READ_ONLY_CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT"
    )


def test_core_rule_watch_not_trade():
    rule = DAILY_ALPHA_BRIEF_APPROVAL_CORE_RULE.lower()
    assert "never promotes" in rule
    assert "watch / research_only" in rule
    assert "authorizes nothing" in rule


def test_next_action_and_stage_constants():
    assert DAILY_ALPHA_BRIEF_APPROVAL_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT"
    )
    assert DAILY_ALPHA_BRIEF_APPROVAL_CURRENT_STAGE == (
        "CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_REQUIRED"
    )


def test_outcome_precedence_enumeration():
    assert DAILY_ALPHA_BRIEF_APPROVAL_OUTCOMES == (
        OUTCOME_REJECTED,
        OUTCOME_PARKED,
        OUTCOME_NEEDS_MORE_INFO,
        OUTCOME_APPROVED,
        OUTCOME_AWAIT,
    )


# --------------------------------------------------------------------------
# (1) Valid review output is approved only as research-only record approval
# --------------------------------------------------------------------------

def test_valid_review_output_approved_as_research_record_only():
    # Feed the REAL upstream review contract output.
    upstream = build_crypto_d1_daily_alpha_brief_review_contract()
    c = build_crypto_d1_daily_alpha_brief_approval_contract(upstream)
    assert c["outcome"] == OUTCOME_APPROVED
    assert c["approval_stance"] == "WATCH"
    assert c["mode"] == "RESEARCH_ONLY"
    # the approval means ONLY a research-record approval
    assert c["approval_result"] == DAILY_ALPHA_BRIEF_APPROVAL_RESULT
    assert c["approval"]["approves_research_record_only"] is True
    assert c["approval"]["authorizes_nothing"] is True
    # still authorizes nothing / unlocks nothing
    assert c["executes"] is False
    assert c["authorizes_trading"] is False
    assert c["promotes_beyond_watch"] is False
    assert c["unlocks_real_data_qa"] is False
    assert c["unlocks_baseline_backtest"] is False
    assert c["unlocks_paper_trading"] is False
    assert c["unlocks_micro_live"] is False


def test_default_sample_upstream_is_approved():
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    assert c["outcome"] == OUTCOME_APPROVED
    assert c["upstream_present"] is True
    assert c["approval_stance"] == DAILY_ALPHA_BRIEF_APPROVAL_STANCE
    assert c["approval_result"] == DAILY_ALPHA_BRIEF_APPROVAL_RESULT


def test_approval_result_meaning_is_research_record_only():
    assert DAILY_ALPHA_BRIEF_APPROVAL_RESULT == (
        "DAILY_ALPHA_BRIEF_APPROVED_FOR_RESEARCH_RECORD"
    )
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    assert c["approval_result_meaning"] == DAILY_ALPHA_BRIEF_APPROVAL_RESULT


def test_non_approved_outcomes_carry_empty_approval_result():
    for payload in (
        {},                                     # AWAIT
        _valid_upstream(executes=True),         # REJECTED
        _valid_upstream(outcome="PARKED"),      # PARKED
        _valid_upstream(outcome="AWAIT"),       # NEEDS_MORE_INFO
    ):
        c = build_crypto_d1_daily_alpha_brief_approval_contract(payload)
        assert c["outcome"] != OUTCOME_APPROVED
        assert c["approval_result"] == ""


# --------------------------------------------------------------------------
# (2) Missing upstream -> AWAIT (or NEEDS_MORE_INFO)
# --------------------------------------------------------------------------

def test_missing_upstream_returns_await():
    assert approve_daily_alpha_brief(None)["outcome"] == OUTCOME_AWAIT
    assert approve_daily_alpha_brief({})["outcome"] == OUTCOME_AWAIT
    # None falls back to the default sample (APPROVED); explicit {} is AWAIT
    c = build_crypto_d1_daily_alpha_brief_approval_contract(None)
    assert c["outcome"] == OUTCOME_APPROVED
    c_empty = build_crypto_d1_daily_alpha_brief_approval_contract({})
    assert c_empty["outcome"] in (OUTCOME_AWAIT, OUTCOME_NEEDS_MORE_INFO)
    assert c_empty["upstream_present"] is False


def test_non_dict_upstream_returns_await():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(["nope"])
    assert c["outcome"] == OUTCOME_AWAIT
    assert c["upstream_present"] is False


# --------------------------------------------------------------------------
# (3) Non-ready upstream cannot be approved
# --------------------------------------------------------------------------

def test_non_ready_upstream_is_not_approved():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(outcome="AWAIT")
    )
    assert c["outcome"] != OUTCOME_APPROVED
    assert c["outcome"] == OUTCOME_NEEDS_MORE_INFO


def test_upstream_with_rejection_reasons_is_not_approved():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(
            outcome="AWAIT", rejection_reasons=["upstream had a problem"]
        )
    )
    assert c["outcome"] != OUTCOME_APPROVED


def test_rejected_upstream_outcome_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(outcome="REJECTED")
    )
    assert c["outcome"] == OUTCOME_REJECTED


# --------------------------------------------------------------------------
# (4) executes=True is rejected
# --------------------------------------------------------------------------

def test_executes_true_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(executes=True)
    )
    assert c["outcome"] == OUTCOME_REJECTED
    assert any("executes" in r for r in c["rejection_reasons"])
    # rejection unlocks nothing
    assert c["unlocks_real_data_qa"] is False
    assert c["real_data_qa_blocked"] is True


# --------------------------------------------------------------------------
# (5) research_only=False is rejected
# --------------------------------------------------------------------------

def test_research_only_false_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(research_only=False)
    )
    assert c["outcome"] == OUTCOME_REJECTED
    assert any("research_only" in r for r in c["rejection_reasons"])


# --------------------------------------------------------------------------
# (6) read_only=False is rejected
# --------------------------------------------------------------------------

def test_read_only_false_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(read_only=False)
    )
    assert c["outcome"] == OUTCOME_REJECTED
    assert any("read_only" in r for r in c["rejection_reasons"])


# --------------------------------------------------------------------------
# (7) any authorization flag True is rejected
# --------------------------------------------------------------------------

def test_each_authorization_flag_true_is_rejected():
    for flag in DAILY_ALPHA_BRIEF_APPROVAL_AUTHORIZATION_FLAGS:
        c = build_crypto_d1_daily_alpha_brief_approval_contract(
            _valid_upstream(**{flag: True})
        )
        assert c["outcome"] == OUTCOME_REJECTED, flag
        assert any(flag in r for r in c["rejection_reasons"]), flag


# --------------------------------------------------------------------------
# (8) any gate unlock is rejected
# --------------------------------------------------------------------------

def test_gate_lock_flipped_false_is_rejected():
    for flag in DAILY_ALPHA_BRIEF_APPROVAL_GATE_LOCK_FLAGS:
        c = build_crypto_d1_daily_alpha_brief_approval_contract(
            _valid_upstream(**{flag: False})
        )
        assert c["outcome"] == OUTCOME_REJECTED, flag
    # the approval's own gate states stay locked
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_gate_unlock_request_flag_is_rejected():
    for flag in DAILY_ALPHA_BRIEF_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS:
        c = build_crypto_d1_daily_alpha_brief_approval_contract(
            _valid_upstream(**{flag: True})
        )
        assert c["outcome"] == OUTCOME_REJECTED, flag


# --------------------------------------------------------------------------
# (9) any request to approve real_data_qa/baseline/paper/live/automation
#     is rejected
# --------------------------------------------------------------------------

def test_each_forbidden_approval_request_is_rejected():
    for flag in DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_APPROVAL_REQUEST_FLAGS:
        c = build_crypto_d1_daily_alpha_brief_approval_contract(
            _valid_upstream(**{flag: True})
        )
        assert c["outcome"] == OUTCOME_REJECTED, flag
        assert any(
            "forbidden approval request" in r for r in c["rejection_reasons"]
        ), flag
    # an APPROVED verdict can ONLY ever mean the research-record meaning
    assert "DAILY_ALPHA_BRIEF_APPROVED_FOR_RESEARCH_RECORD" == (
        DAILY_ALPHA_BRIEF_APPROVAL_RESULT
    )


# --------------------------------------------------------------------------
# (10) any promotion beyond WATCH is rejected
# --------------------------------------------------------------------------

def test_promotion_via_stance_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(review_stance="STRONG")
    )
    assert c["outcome"] == OUTCOME_REJECTED
    assert any("promote" in r.lower() for r in c["rejection_reasons"])


def test_promotion_via_outcome_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(outcome="PASS")
    )
    assert c["outcome"] == OUTCOME_REJECTED


def test_promotion_via_explicit_flag_is_rejected():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(promotes_beyond_watch=True)
    )
    assert c["outcome"] == OUTCOME_REJECTED
    # the approval never promotes its own stance regardless
    assert c["approval_stance"] == "WATCH"
    assert c["promotes_beyond_watch"] is False


# --------------------------------------------------------------------------
# (11) any executable signal/order/trade field is rejected
# --------------------------------------------------------------------------

def test_each_executable_signal_field_is_rejected():
    sample_values = {
        "signal": "BUY",
        "order": {"qty": 1},
        "trade": "do it",
        "trade_instruction": "execute",
        "execution": "now",
        "position": "flat",
        "entry": 100.0,
        "exit": 110.0,
        "side": "BID",
    }
    for field in DAILY_ALPHA_BRIEF_APPROVAL_EXECUTABLE_SIGNAL_FIELDS:
        value = sample_values.get(field, "x")
        c = build_crypto_d1_daily_alpha_brief_approval_contract(
            _valid_upstream(**{field: value})
        )
        assert c["outcome"] == OUTCOME_REJECTED, field
        assert any(
            "executable signal/order/trade field" in r
            for r in c["rejection_reasons"]
        ), field


# --------------------------------------------------------------------------
# (12) evidence lanes remain observation-only
# --------------------------------------------------------------------------

def test_observation_only_evidence_lanes_constant():
    assert DAILY_ALPHA_BRIEF_APPROVAL_OBSERVATION_ONLY_EVIDENCE_LANES == (
        "external_bot_evidence",
        "hyperliquid_whale_evidence",
        "funding_rate_evidence",
        "bitcoin_cycle_timing_evidence",
        "daily_alpha_brief_research",
        "daily_alpha_brief_review",
    )


def test_evidence_lanes_observation_only_across_every_outcome():
    payloads = [
        None,                                    # APPROVED (default sample)
        {},                                      # AWAIT
        _valid_upstream(),                       # APPROVED
        _valid_upstream(outcome="AWAIT"),        # NEEDS_MORE_INFO
        _valid_upstream(executes=True),          # REJECTED
        _valid_upstream(outcome="PARKED"),       # PARKED
    ]
    for payload in payloads:
        c = build_crypto_d1_daily_alpha_brief_approval_contract(payload)
        assert tuple(c["observation_only_evidence_lanes"]) == (
            DAILY_ALPHA_BRIEF_APPROVAL_OBSERVATION_ONLY_EVIDENCE_LANES
        )
        text = " ".join(c["observation_only_section"]).lower()
        assert "observation-only" in text
        assert "wired" in text and "automation" in text


# --------------------------------------------------------------------------
# (13) highest possible stance is WATCH
# --------------------------------------------------------------------------

def test_approval_stance_is_always_watch():
    payloads = [
        None,
        {},
        _valid_upstream(),
        _valid_upstream(executes=True),
        _valid_upstream(review_stance="STRONG"),
        _valid_upstream(outcome="AWAIT"),
        _valid_upstream(outcome="PARKED"),
        _valid_upstream(approve_live_trading=True),
    ]
    for payload in payloads:
        c = build_crypto_d1_daily_alpha_brief_approval_contract(payload)
        assert c["approval_stance"] == "WATCH"
        assert c["promotes_beyond_watch"] is False
        assert c["approval"]["authorizes_nothing"] is True


def test_outcome_precedence_rejected_beats_park_and_nmi():
    # An unsafe + parked + incomplete upstream still REJECTS.
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(
            executes=True,
            outcome="PARKED",
            rejection_reasons=["x"],
        )
    )
    assert c["outcome"] == OUTCOME_REJECTED


def test_park_beats_needs_more_info():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(
            outcome="PARKED",
            needs_more_info_reasons=["incomplete"],
        )
    )
    assert c["outcome"] == OUTCOME_PARKED


def test_needs_more_info_for_incomplete_but_safe_upstream():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(
        _valid_upstream(outcome="NEEDS_MORE_INFO")
    )
    assert c["outcome"] == OUTCOME_NEEDS_MORE_INFO


# --------------------------------------------------------------------------
# Posture flags / safety posture object
# --------------------------------------------------------------------------

def test_contract_posture_flags():
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
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
    assert c["unlocks_real_data_qa"] is False
    assert c["unlocks_baseline_backtest"] is False
    assert c["unlocks_paper_trading"] is False
    assert c["unlocks_micro_live"] is False
    assert c["requires_independent_confirmation"] is True


def test_gates_remain_blocked_and_locked():
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_safety_posture_object_proves_required_values():
    posture = DAILY_ALPHA_BRIEF_APPROVAL_SAFETY_POSTURE
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
    assert posture["unlocks_real_data_qa"] is False
    assert posture["unlocks_baseline_backtest"] is False
    assert posture["unlocks_paper_trading"] is False
    assert posture["unlocks_micro_live"] is False
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    assert c["safety_posture"] == posture


def test_safety_posture_is_isolated_copy():
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    c["safety_posture"]["executes"] = True
    fresh = build_crypto_d1_daily_alpha_brief_approval_contract()
    assert fresh["safety_posture"]["executes"] is False
    assert DAILY_ALPHA_BRIEF_APPROVAL_SAFETY_POSTURE["executes"] is False


# --------------------------------------------------------------------------
# No trade language in actionable output
# --------------------------------------------------------------------------

_ACTIONABLE_FIELDS = (
    "outcome",
    "approval_result",
    "approval_stance",
    "operator_next_step",
    "approval_summary_section",
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
    return {
        t for t in DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_TRADE_TERMS if t in words
    }


def test_no_forbidden_trade_verbs_in_actionable_output():
    # Non-rejected outcomes only; a REJECTED findings section may legitimately
    # quote an offending upstream term while explaining the rejection.
    payloads = [
        None,
        {},
        _valid_upstream(),
        _valid_upstream(outcome="AWAIT"),
        _valid_upstream(outcome="PARKED"),
    ]
    for payload in payloads:
        c = build_crypto_d1_daily_alpha_brief_approval_contract(payload)
        assert c["outcome"] != OUTCOME_REJECTED
        for field in _ACTIONABLE_FIELDS:
            for text in _iter_strings(c.get(field)):
                hits = _has_forbidden_word(text)
                assert not hits, (field, text, hits)


def test_forbidden_trade_terms_constant():
    assert DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_TRADE_TERMS == (
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
    a = build_crypto_d1_daily_alpha_brief_approval_contract(_valid_upstream())
    b = build_crypto_d1_daily_alpha_brief_approval_contract(_valid_upstream())
    assert a == b


def test_caller_input_not_mutated():
    ev = _valid_upstream(rejection_reasons=["x"])
    snapshot = _valid_upstream(rejection_reasons=["x"])
    build_crypto_d1_daily_alpha_brief_approval_contract(ev)
    assert ev == snapshot


def test_returned_contract_is_isolated():
    c = build_crypto_d1_daily_alpha_brief_approval_contract(_valid_upstream())
    c["approval_summary_section"].append("TAMPERED")
    c["safety_posture"]["executes"] = True
    fresh = build_crypto_d1_daily_alpha_brief_approval_contract(_valid_upstream())
    assert "TAMPERED" not in fresh["approval_summary_section"]
    assert fresh["safety_posture"]["executes"] is False


def test_default_sample_upstream_not_mutated_by_default_build():
    before = dict(DEFAULT_SAMPLE_UPSTREAM)
    build_crypto_d1_daily_alpha_brief_approval_contract()
    assert DEFAULT_SAMPLE_UPSTREAM == before


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def test_approved_contract_validates():
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    v = validate_crypto_d1_daily_alpha_brief_approval_contract(c)
    assert v["valid"] is True
    assert v["missing_fields"] == ()
    assert v["no_trade_language"] is True
    assert v["posture_ok"] is True
    assert v["label_ok"] is True
    assert v["gates_locked"] is True
    assert v["result_ok"] is True
    assert v["approval_ok"] is True


def test_every_outcome_branch_validates():
    for payload in (
        None,                                    # APPROVED
        {},                                      # AWAIT
        _valid_upstream(),                       # APPROVED
        _valid_upstream(outcome="AWAIT"),        # NEEDS_MORE_INFO
        _valid_upstream(outcome="PARKED"),       # PARKED
        _valid_upstream(executes=True),          # REJECTED
    ):
        c = build_crypto_d1_daily_alpha_brief_approval_contract(payload)
        v = validate_crypto_d1_daily_alpha_brief_approval_contract(c)
        assert v["valid"] is True, (payload, v)


def test_validation_rejects_tampered_executes_flag():
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    c["executes"] = True
    v = validate_crypto_d1_daily_alpha_brief_approval_contract(c)
    assert v["valid"] is False
    assert v["flags_false"] is False


def test_validation_rejects_tampered_approval_stance():
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    c["approval_stance"] = "STRONG"
    v = validate_crypto_d1_daily_alpha_brief_approval_contract(c)
    assert v["valid"] is False
    assert v["stance_ok"] is False


def test_validation_rejects_tampered_approval_result():
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    # APPROVED contract but result blanked -> result_ok False
    c["approval_result"] = ""
    v = validate_crypto_d1_daily_alpha_brief_approval_contract(c)
    assert v["valid"] is False
    assert v["result_ok"] is False


def test_validation_rejects_non_dict():
    v = validate_crypto_d1_daily_alpha_brief_approval_contract("nope")
    assert v["valid"] is False


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def test_render_is_readonly_markdown_string():
    c = build_crypto_d1_daily_alpha_brief_approval_contract()
    md = render_crypto_d1_daily_alpha_brief_approval_contract_markdown(c)
    assert isinstance(md, str)
    assert "# Crypto-D1 Daily Alpha Brief Approval Contract" in md
    assert DAILY_ALPHA_BRIEF_APPROVAL_LABEL in md
    assert "Outcome: APPROVED" in md
    assert "Approval stance: WATCH" in md


def test_render_has_no_forbidden_trade_verbs():
    for payload in (None, _valid_upstream(), {}):
        c = build_crypto_d1_daily_alpha_brief_approval_contract(payload)
        md = render_crypto_d1_daily_alpha_brief_approval_contract_markdown(c)
        for line in md.splitlines():
            assert not _has_forbidden_word(line), line


# --------------------------------------------------------------------------
# (14) Pure-stdlib imports only (no imports outside allowed roots)
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


# --------------------------------------------------------------------------
# (15) No file/network/runtime/dashboard/storage side effects (AST-level)
# --------------------------------------------------------------------------

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


def test_building_contract_writes_no_files(tmp_path):
    before = set(p.name for p in tmp_path.iterdir())
    build_crypto_d1_daily_alpha_brief_approval_contract()
    build_crypto_d1_daily_alpha_brief_approval_contract(_valid_upstream())
    approve_daily_alpha_brief(_valid_upstream())
    after = set(p.name for p in tmp_path.iterdir())
    assert before == after


# --------------------------------------------------------------------------
# (16) commander_2_safety allowlist: exactly two additive lines
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

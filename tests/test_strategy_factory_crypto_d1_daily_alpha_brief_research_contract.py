"""Tests for the Crypto-D1 Daily Alpha Brief Research Contract (Bundle 65
Block 125). Verifies the read-only assembly of a daily crypto alpha brief from
already-approved static evidence lanes (external_bot_evidence_intake,
hyperliquid_whale_evidence, funding_rate_evidence, bitcoin_cycle_timing_evidence)
into a structured research-only brief: input-evidence summary, market context,
evidence alignment, caution flags, watchlist, no-execution-authorization,
missing-evidence, and a research-only operator next step. The contract fetches
no data, calls no API, inspects no dataset, authorizes nothing, never produces a
trade instruction, and unlocks no gate. The highest stance it can produce is
WATCH / RESEARCH_ONLY."""

from __future__ import annotations

import ast
import pathlib
import re

from sparta_commander.strategy_factory_crypto_d1_daily_alpha_brief_research_contract import (  # noqa: E501
    DAILY_ALPHA_BRIEF_SCHEMA_VERSION,
    DAILY_ALPHA_BRIEF_LABEL,
    DAILY_ALPHA_BRIEF_STATUS,
    DAILY_ALPHA_BRIEF_MODE,
    DAILY_ALPHA_BRIEF_CORE_RULE,
    DAILY_ALPHA_BRIEF_SAFETY_POSTURE,
    DAILY_ALPHA_BRIEF_EVIDENCE_LANES,
    DAILY_ALPHA_BRIEF_DECISIONS,
    DECISION_AWAIT,
    DECISION_MIXED_WATCH,
    DECISION_NEUTRAL_WATCH,
    DECISION_RESEARCH_WATCH_ONLY,
    DAILY_ALPHA_BRIEF_STANCES,
    STANCE_INCOMPLETE_EVIDENCE,
    STANCE_MIXED,
    STANCE_WATCH,
    STANCE_RESEARCH_ONLY,
    DAILY_ALPHA_BRIEF_LANE_STANCES,
    LANE_STANCE_SUPPORTIVE,
    LANE_STANCE_CAUTIONARY,
    LANE_STANCE_NEUTRAL,
    LANE_STANCE_UNKNOWN,
    DAILY_ALPHA_BRIEF_FORBIDDEN_ALLOW_FLAGS,
    DAILY_ALPHA_BRIEF_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED,
    DAILY_ALPHA_BRIEF_FORBIDDEN_TRADE_TERMS,
    DAILY_ALPHA_BRIEF_NEXT_REQUIRED_ACTION,
    DAILY_ALPHA_BRIEF_CURRENT_STAGE,
    DEFAULT_SAMPLE_EVIDENCE,
    assess_daily_alpha_brief_evidence,
    build_crypto_d1_daily_alpha_brief_research_contract,
    validate_crypto_d1_daily_alpha_brief_research_contract,
    render_crypto_d1_daily_alpha_brief_research_contract_markdown,
)

_MODPATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "strategy_factory_crypto_d1_daily_alpha_brief_research_contract.py"
)
_SAFETY_PATH = (
    pathlib.Path(__file__).resolve().parents[1]
    / "sparta_commander"
    / "commander_2_safety.py"
)

_MODULE_ALLOWLIST_LINE = (
    "sparta_commander/"
    "strategy_factory_crypto_d1_daily_alpha_brief_research_contract.py"
)
_TEST_ALLOWLIST_LINE = (
    "tests/"
    "test_strategy_factory_crypto_d1_daily_alpha_brief_research_contract.py"
)

# Evidence lanes that produce a fully present, supportive, aligned brief.
_ALIGNED_SUPPORTIVE = {
    "external_bot_evidence_intake": {"stance": "supportive-watch"},
    "hyperliquid_whale_evidence": {"stance": "supportive-watch"},
    "funding_rate_evidence": {"stance": "supportive-watch"},
    "bitcoin_cycle_timing_evidence": {"stance": "accumulation-watch"},
}


def _all_present(**overrides):
    base = {lane: {"stance": "neutral"} for lane in DAILY_ALPHA_BRIEF_EVIDENCE_LANES}
    base.update(overrides)
    return base


# --------------------------------------------------------------------------
# Schema / constants
# --------------------------------------------------------------------------

def test_schema_version_is_v1():
    assert DAILY_ALPHA_BRIEF_SCHEMA_VERSION == (
        "strategy_factory_crypto_d1_daily_alpha_brief_research_contract.v1"
    )


def test_contract_label_is_exact_block_125():
    assert DAILY_ALPHA_BRIEF_LABEL == (
        "Block 125 - Crypto-D1 Daily Alpha Brief Research Contract"
    )
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    assert c["label"] == DAILY_ALPHA_BRIEF_LABEL


def test_mode_is_research_only():
    assert DAILY_ALPHA_BRIEF_MODE == "RESEARCH_ONLY"


def test_status_constant():
    assert DAILY_ALPHA_BRIEF_STATUS == (
        "READ_ONLY_CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT"
    )


def test_core_rule_watch_not_trade():
    rule = DAILY_ALPHA_BRIEF_CORE_RULE.lower()
    assert "what to watch" in rule
    assert "never what to trade" in rule
    assert "watch / research_only" in rule


def test_next_action_and_stage_constants():
    assert DAILY_ALPHA_BRIEF_NEXT_REQUIRED_ACTION == (
        "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT"
    )
    assert DAILY_ALPHA_BRIEF_CURRENT_STAGE == (
        "CRYPTO_D1_DAILY_ALPHA_BRIEF_RESEARCH_CONTRACT_REQUIRED"
    )


def test_evidence_lanes_are_the_four_expected():
    assert DAILY_ALPHA_BRIEF_EVIDENCE_LANES == (
        "external_bot_evidence_intake",
        "hyperliquid_whale_evidence",
        "funding_rate_evidence",
        "bitcoin_cycle_timing_evidence",
    )


def test_decisions_and_stances_enumerations():
    assert DAILY_ALPHA_BRIEF_DECISIONS == (
        DECISION_AWAIT,
        DECISION_MIXED_WATCH,
        DECISION_NEUTRAL_WATCH,
        DECISION_RESEARCH_WATCH_ONLY,
    )
    assert DAILY_ALPHA_BRIEF_STANCES == (
        STANCE_INCOMPLETE_EVIDENCE,
        STANCE_MIXED,
        STANCE_WATCH,
        STANCE_RESEARCH_ONLY,
    )
    assert DAILY_ALPHA_BRIEF_LANE_STANCES == (
        LANE_STANCE_SUPPORTIVE,
        LANE_STANCE_CAUTIONARY,
        LANE_STANCE_NEUTRAL,
        LANE_STANCE_UNKNOWN,
    )


def test_highest_stance_is_watch_or_research_only():
    # No stance in the enumeration is a trade stance; the top of the ladder is
    # WATCH / RESEARCH_ONLY.
    for stance in DAILY_ALPHA_BRIEF_STANCES:
        for term in DAILY_ALPHA_BRIEF_FORBIDDEN_TRADE_TERMS:
            assert term not in stance.lower()
    assert STANCE_RESEARCH_ONLY == "RESEARCH_ONLY"
    assert STANCE_WATCH == "WATCH"


# --------------------------------------------------------------------------
# Posture flags
# --------------------------------------------------------------------------

def test_contract_posture_flags():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
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
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    assert c["real_data_qa_blocked"] is True
    assert c["baseline_backtest_blocked"] is True
    assert c["paper_trading_gate_locked"] is True
    assert c["micro_live_gate_locked"] is True


def test_safety_posture_all_false():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    posture = c["safety_posture"]
    assert isinstance(posture, dict) and posture
    assert all(v is False for v in posture.values())
    # the module-level constant is all-false too
    assert all(v is False for v in DAILY_ALPHA_BRIEF_SAFETY_POSTURE.values())


def test_safety_posture_is_isolated_copy():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    c["safety_posture"]["fetches_data"] = True
    fresh = build_crypto_d1_daily_alpha_brief_research_contract()
    assert fresh["safety_posture"]["fetches_data"] is False
    assert DAILY_ALPHA_BRIEF_SAFETY_POSTURE["fetches_data"] is False


# --------------------------------------------------------------------------
# Decision behavior
# --------------------------------------------------------------------------

def test_default_sample_is_aligned_research_watch_only():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    assert c["decision"] == DECISION_RESEARCH_WATCH_ONLY
    assert c["alpha_stance"] == STANCE_RESEARCH_ONLY
    # the default sample provides all four lanes
    assert c["missing_lanes"] == []
    assert set(c["present_lanes"]) == set(DAILY_ALPHA_BRIEF_EVIDENCE_LANES)


def test_missing_evidence_returns_await_incomplete():
    c = build_crypto_d1_daily_alpha_brief_research_contract(
        {"funding_rate_evidence": {"stance": "supportive-watch"}}
    )
    assert c["decision"] == DECISION_AWAIT
    assert c["alpha_stance"] == STANCE_INCOMPLETE_EVIDENCE
    assert "external_bot_evidence_intake" in c["missing_lanes"]
    assert "hyperliquid_whale_evidence" in c["missing_lanes"]
    assert "bitcoin_cycle_timing_evidence" in c["missing_lanes"]
    # missing-evidence section names every absent lane and never errors
    joined = " ".join(c["missing_evidence_section"]).lower()
    assert "missing evidence lane" in joined
    assert "await" in joined


def test_empty_evidence_returns_await_not_failure():
    c = build_crypto_d1_daily_alpha_brief_research_contract({})
    assert c["decision"] == DECISION_AWAIT
    assert c["alpha_stance"] == STANCE_INCOMPLETE_EVIDENCE
    assert c["missing_lanes"] == list(DAILY_ALPHA_BRIEF_EVIDENCE_LANES)
    # no exception, watchlist degrades gracefully
    assert c["watchlist_section"]


def test_none_evidence_uses_default_sample():
    assert build_crypto_d1_daily_alpha_brief_research_contract(None) == (
        build_crypto_d1_daily_alpha_brief_research_contract()
    )


def test_non_dict_evidence_degrades_to_await():
    c = build_crypto_d1_daily_alpha_brief_research_contract(["not", "a", "dict"])
    assert c["decision"] == DECISION_AWAIT
    assert c["alpha_stance"] == STANCE_INCOMPLETE_EVIDENCE


def test_conflicting_evidence_returns_mixed_watch():
    ev = _all_present(
        hyperliquid_whale_evidence={"stance": "supportive-watch"},
        funding_rate_evidence={"stance": "cautionary-watch"},
    )
    c = build_crypto_d1_daily_alpha_brief_research_contract(ev)
    assert c["decision"] == DECISION_MIXED_WATCH
    assert c["alpha_stance"] == STANCE_MIXED
    assert c["assessment"]["conflict"] is True
    align = " ".join(c["evidence_alignment_section"]).lower()
    assert "conflict" in align
    assert "watch only" in align


def test_strong_aligned_supportive_is_research_watch_only_but_authorizes_nothing():
    c = build_crypto_d1_daily_alpha_brief_research_contract(_ALIGNED_SUPPORTIVE)
    assert c["decision"] == DECISION_RESEARCH_WATCH_ONLY
    assert c["alpha_stance"] == STANCE_RESEARCH_ONLY
    # strong + aligned still authorizes nothing
    assert c["authorizes_trading"] is False
    assert c["authorizes_paper_trading"] is False
    assert c["authorizes_live_trading"] is False
    assert c["executes"] is False
    assert c["assessment"]["authorizes_nothing"] is True


def test_strong_aligned_cautionary_is_research_watch_only():
    ev = _all_present(
        external_bot_evidence_intake={"stance": "cautionary-watch"},
        hyperliquid_whale_evidence={"stance": "cautionary-watch"},
    )
    # remaining two are neutral -> directional lanes all cautionary, no conflict
    c = build_crypto_d1_daily_alpha_brief_research_contract(ev)
    assert c["decision"] == DECISION_RESEARCH_WATCH_ONLY
    assert c["alpha_stance"] == STANCE_RESEARCH_ONLY
    assert c["assessment"]["aligned_direction"] == LANE_STANCE_CAUTIONARY


def test_all_neutral_present_is_neutral_watch():
    c = build_crypto_d1_daily_alpha_brief_research_contract(_all_present())
    assert c["decision"] == DECISION_NEUTRAL_WATCH
    assert c["alpha_stance"] == STANCE_WATCH


def test_unknown_stance_is_non_directional():
    ev = _all_present(
        funding_rate_evidence={"stance": "this-is-not-a-known-stance"},
    )
    summary = assess_daily_alpha_brief_evidence(ev)["lane_summaries"]
    assert summary["funding_rate_evidence"]["stance"] == LANE_STANCE_UNKNOWN
    # all others neutral, unknown is non-directional -> neutral watch
    c = build_crypto_d1_daily_alpha_brief_research_contract(ev)
    assert c["decision"] == DECISION_NEUTRAL_WATCH


def test_lane_stance_aliases_normalize():
    assess = assess_daily_alpha_brief_evidence(
        _all_present(
            bitcoin_cycle_timing_evidence={"stance": "recovery-watch"},
            hyperliquid_whale_evidence={"stance": "bearish-watch"},
        )
    )
    lanes = assess["lane_summaries"]
    assert lanes["bitcoin_cycle_timing_evidence"]["stance"] == (
        LANE_STANCE_SUPPORTIVE
    )
    assert lanes["hyperliquid_whale_evidence"]["stance"] == (
        LANE_STANCE_CAUTIONARY
    )


# --------------------------------------------------------------------------
# Sections and summaries
# --------------------------------------------------------------------------

def test_all_required_sections_present_and_nonempty():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    for key in (
        "input_evidence_summary",
        "market_context_section",
        "evidence_alignment_section",
        "caution_flags_section",
        "watchlist_section",
        "no_execution_authorization_section",
        "missing_evidence_section",
        "operator_next_step",
    ):
        assert key in c
        assert c[key]


def test_input_evidence_summary_summarizes_each_lane_without_executing():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    summary = c["input_evidence_summary"]
    assert set(summary.keys()) == set(DAILY_ALPHA_BRIEF_EVIDENCE_LANES)
    for lane, row in summary.items():
        assert row["lane"] == lane
        assert row["present"] is True
        assert row["stance"] in DAILY_ALPHA_BRIEF_LANE_STANCES
    # the brief never sets any execution flag while summarizing
    assert c["executes"] is False
    assert c["authorizes_real_world_action"] is False


def test_no_execution_authorization_section_disclaims_everything():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    text = " ".join(c["no_execution_authorization_section"]).lower()
    assert "authorizes no trade" in text
    assert "no paper trading" in text
    assert "no live trading" in text
    assert "no broker or exchange" in text
    assert "no automation" in text
    assert "watch / research_only" in text


def test_operator_next_step_stays_research_only():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    step = c["operator_next_step"].lower()
    assert "research-only" in step
    assert "no execution" in step
    # the only forward action is to build/review the next research-only contract
    assert "research-only contract" in step


# --------------------------------------------------------------------------
# No trade language in actionable output
# --------------------------------------------------------------------------

_ACTIONABLE_FIELDS = (
    "decision",
    "alpha_stance",
    "operator_next_step",
    "market_context_section",
    "evidence_alignment_section",
    "caution_flags_section",
    "watchlist_section",
    "missing_evidence_section",
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
    return {t for t in DAILY_ALPHA_BRIEF_FORBIDDEN_TRADE_TERMS if t in words}


def test_no_forbidden_trade_verbs_in_actionable_output():
    # Exercise every decision branch and assert NONE of the brief's actionable
    # guidance fields contain BUY/SELL/LONG/SHORT/ENTRY/EXIT/order as a word.
    payloads = [
        None,
        {},
        _ALIGNED_SUPPORTIVE,
        _all_present(),
        _all_present(
            hyperliquid_whale_evidence={"stance": "supportive-watch"},
            funding_rate_evidence={"stance": "cautionary-watch"},
        ),
        # a payload that requests forbidden capability flags
        _all_present(places_order=True, allow_live_trading="yes"),
    ]
    for payload in payloads:
        c = build_crypto_d1_daily_alpha_brief_research_contract(payload)
        for field in _ACTIONABLE_FIELDS:
            for text in _iter_strings(c.get(field)):
                hits = _has_forbidden_word(text)
                assert not hits, (field, text, hits)


def test_forbidden_trade_terms_constant():
    assert DAILY_ALPHA_BRIEF_FORBIDDEN_TRADE_TERMS == (
        "buy",
        "sell",
        "long",
        "short",
        "entry",
        "exit",
        "order",
    )


# --------------------------------------------------------------------------
# Forbidden capability requests are recorded but never honored
# --------------------------------------------------------------------------

def test_forbidden_flag_requests_recorded_but_not_honored():
    ev = _all_present(places_order=True, allow_execution="yes")
    c = build_crypto_d1_daily_alpha_brief_research_contract(ev)
    assert "places_order" in c["requested_forbidden_flags"]
    assert "allow_execution" in c["requested_forbidden_flags"]
    # nothing is unlocked
    assert c["executes"] is False
    assert c["authorizes_real_world_action"] is False
    assert c["unlocks_downstream_gate"] is False
    # caution flags note the ignored requests by count, not by echoing tokens
    caution = " ".join(c["caution_flags_section"]).lower()
    assert "forbidden capability request" in caution


def test_forbidden_flag_inside_lane_payload_is_detected():
    ev = _all_present(
        funding_rate_evidence={"stance": "neutral", "allow_backtest": True},
    )
    c = build_crypto_d1_daily_alpha_brief_research_contract(ev)
    assert "allow_backtest" in c["requested_forbidden_flags"]


def test_forbidden_allow_flags_and_blocked_capabilities_exposed():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    assert tuple(c["forbidden_allow_flags"]) == (
        DAILY_ALPHA_BRIEF_FORBIDDEN_ALLOW_FLAGS
    )
    assert tuple(c["remaining_real_world_capabilities_blocked"]) == (
        DAILY_ALPHA_BRIEF_REMAINING_REAL_WORLD_CAPABILITIES_BLOCKED
    )


# --------------------------------------------------------------------------
# Determinism / isolation
# --------------------------------------------------------------------------

def test_deterministic_output():
    a = build_crypto_d1_daily_alpha_brief_research_contract(_ALIGNED_SUPPORTIVE)
    b = build_crypto_d1_daily_alpha_brief_research_contract(_ALIGNED_SUPPORTIVE)
    assert a == b


def test_caller_input_not_mutated():
    ev = {
        "funding_rate_evidence": {
            "stance": "supportive-watch",
            "metrics": {"z": 1},
        }
    }
    snapshot = {
        "funding_rate_evidence": {
            "stance": "supportive-watch",
            "metrics": {"z": 1},
        }
    }
    build_crypto_d1_daily_alpha_brief_research_contract(ev)
    assert ev == snapshot


def test_returned_contract_is_isolated():
    c = build_crypto_d1_daily_alpha_brief_research_contract(_ALIGNED_SUPPORTIVE)
    c["watchlist_section"].append("TAMPERED")
    c["present_lanes"].append("TAMPERED")
    c["safety_posture"]["places_order"] = True
    fresh = build_crypto_d1_daily_alpha_brief_research_contract(
        _ALIGNED_SUPPORTIVE
    )
    assert "TAMPERED" not in fresh["watchlist_section"]
    assert "TAMPERED" not in fresh["present_lanes"]
    assert fresh["safety_posture"]["places_order"] is False


def test_default_sample_evidence_not_mutated_by_default_build():
    before = {
        "external_bot_evidence_intake": {
            "stance": "supportive-watch",
            "headline": "Approved external research notes lean constructive.",
            "metrics": {"approved_sources": 3},
        },
    }
    build_crypto_d1_daily_alpha_brief_research_contract()
    # the module-level default sample must be unchanged
    assert DEFAULT_SAMPLE_EVIDENCE["external_bot_evidence_intake"] == (
        before["external_bot_evidence_intake"]
    )


# --------------------------------------------------------------------------
# Validation
# --------------------------------------------------------------------------

def test_default_contract_validates():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    v = validate_crypto_d1_daily_alpha_brief_research_contract(c)
    assert v["valid"] is True
    assert v["missing_fields"] == ()
    assert v["no_trade_language"] is True
    assert v["safety_all_false"] is True
    assert v["label_ok"] is True


def test_every_decision_branch_validates():
    for payload in (
        None,
        {},
        _ALIGNED_SUPPORTIVE,
        _all_present(),
        _all_present(
            hyperliquid_whale_evidence={"stance": "supportive-watch"},
            funding_rate_evidence={"stance": "cautionary-watch"},
        ),
    ):
        c = build_crypto_d1_daily_alpha_brief_research_contract(payload)
        v = validate_crypto_d1_daily_alpha_brief_research_contract(c)
        assert v["valid"] is True, (payload, v)


def test_validation_rejects_tampered_executes_flag():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    c["executes"] = True
    v = validate_crypto_d1_daily_alpha_brief_research_contract(c)
    assert v["valid"] is False
    assert v["flags_false"] is False


def test_validation_rejects_tampered_label():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    c["label"] = "Block 999 - Buy Everything Now"
    v = validate_crypto_d1_daily_alpha_brief_research_contract(c)
    assert v["valid"] is False
    assert v["label_ok"] is False


def test_validation_rejects_injected_trade_language():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    c["operator_next_step"] = "Place a BUY order now."
    v = validate_crypto_d1_daily_alpha_brief_research_contract(c)
    assert v["valid"] is False
    assert v["no_trade_language"] is False


def test_validation_rejects_non_dict():
    v = validate_crypto_d1_daily_alpha_brief_research_contract("nope")
    assert v["valid"] is False


# --------------------------------------------------------------------------
# Render
# --------------------------------------------------------------------------

def test_render_is_readonly_markdown_string():
    c = build_crypto_d1_daily_alpha_brief_research_contract()
    md = render_crypto_d1_daily_alpha_brief_research_contract_markdown(c)
    assert isinstance(md, str)
    assert "# Crypto-D1 Daily Alpha Brief Research Contract" in md
    assert DAILY_ALPHA_BRIEF_LABEL in md
    assert "Research stance: RESEARCH_ONLY" in md


def test_render_has_no_forbidden_trade_verbs():
    for payload in (None, _ALIGNED_SUPPORTIVE, {}):
        c = build_crypto_d1_daily_alpha_brief_research_contract(payload)
        md = render_crypto_d1_daily_alpha_brief_research_contract_markdown(c)
        # the label legitimately contains no trade verbs; scan the body lines
        for line in md.splitlines():
            assert not _has_forbidden_word(line), line


# --------------------------------------------------------------------------
# Pure-stdlib / no-IO source posture (AST-level)
# --------------------------------------------------------------------------

_ALLOWED_IMPORTS = {"__future__", "typing"}

# Names that, if called, would imply I/O, network, subprocess, or dynamic import.
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
                # reject attribute calls on forbidden modules (e.g. os.system)
                value = func.value
                if isinstance(value, ast.Name):
                    assert value.id not in _FORBIDDEN_MODULE_TOKENS, (
                        value.id + "." + func.attr
                    )


def test_module_source_has_no_dunder_import_or_open():
    src = _MODPATH.read_text(encoding="utf-8")
    # guard against obvious dynamic-import / IO primitives. (Bare substrings
    # like "subprocess" appear only as descriptive all-false posture keys, so
    # we assert on real import/usage forms instead.)
    assert "__import__(" not in src
    assert "open(" not in src
    assert "import subprocess" not in src
    assert "import socket" not in src
    assert "import os" not in src
    assert "import requests" not in src


# --------------------------------------------------------------------------
# commander_2_safety allowlist
# --------------------------------------------------------------------------

def test_commander_safety_allowlist_includes_the_two_additive_entries():
    from sparta_commander.commander_2_safety import (
        COMMANDER_2_MODULES,
        COMMANDER_2_TESTS,
    )

    assert _MODULE_ALLOWLIST_LINE in COMMANDER_2_MODULES
    assert _TEST_ALLOWLIST_LINE in COMMANDER_2_TESTS
    # exactly one entry each -- additive, not duplicated
    assert COMMANDER_2_MODULES.count(_MODULE_ALLOWLIST_LINE) == 1
    assert COMMANDER_2_TESTS.count(_TEST_ALLOWLIST_LINE) == 1


def test_commander_safety_only_two_new_lines_for_this_module():
    src = _SAFETY_PATH.read_text(encoding="utf-8")
    assert src.count(_MODULE_ALLOWLIST_LINE) == 1
    assert src.count(_TEST_ALLOWLIST_LINE) == 1

"""Tests for the H4 discretionary trend-following research BACKLOG NOTE contract.

Verifies: research-only, backlog-note-only, executes nothing; it is NOT a candidate
and assigns NO candidate number (no C18); status BACKLOG_ONLY_NOT_CANDIDATE_YET;
records the observed H4 / BTCUSD+XAUUSD setup + the trader's no-indicator
trend-following / patience / add-to-winners style; the evidence source is observed
screenshots/conversation only (0 chart examples on hand, evidence bar NOT met); the
6 possible objective families to test later; the 3-5-annotated-chart evidence bar
required before promotion; promotion is human-gated; capability flags + scope locks;
validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.h4_discretionary_trend_following_research_backlog_note_v1_contract as note  # noqa: E501


_R = note.build_h4_backlog_note()


def test_research_only_backlog_note_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["kind"] == "research_backlog_note"
    assert _R["is_research_backlog_note_only"] is True
    assert _R["status"] == "BACKLOG_ONLY_NOT_CANDIDATE_YET"
    assert note.validate_h4_backlog_note(_R)["valid"] is True


# ---- NOT a candidate; no C18 assigned --------------------------------------

def test_not_a_candidate_no_c18():
    assert _R["is_candidate"] is False
    assert _R["candidate_number_assigned"] is None
    assert _R["no_c18_assigned"] is True
    assert _R["assigns_candidate_number"] is False
    assert _R["enters_candidate_lifecycle"] is False
    assert _R["promotes_to_candidate"] is False
    for bad in ({"is_candidate": True}, {"candidate_number_assigned": "C18"},
                {"no_c18_assigned": False}):
        assert note.validate_h4_backlog_note({**_R, **bad})["valid"] is False, bad


# ---- the observation -------------------------------------------------------

def test_observation_recorded():
    assert _R["observed_timeframe"] == "H4"
    assert _R["observed_instruments"] == ["BTCUSD", "XAUUSD"]
    claims = " || ".join(_R["trader_claims"]).lower()
    for must in ("no indicators", "trend", "patient", "overtrade", "add"):
        assert must in claims, must
    assert _R["claims_are_unverified"] is True
    bad = {**_R, "observed_instruments": ["BTCUSD"]}
    assert note.validate_h4_backlog_note(bad)["valid"] is False


# ---- evidence source = screenshots/conversation only -----------------------

def test_evidence_source_no_chart_examples_yet():
    assert "screenshots" in _R["evidence_source"].lower()
    assert "no direct chart examples" in _R["evidence_source"].lower()
    assert _R["chart_examples_currently_available"] == 0
    assert _R["evidence_bar_met"] is False
    # tamper: claiming the evidence bar is met must fail (no charts on hand)
    bad = {**_R, "evidence_bar_met": True}
    assert note.validate_h4_backlog_note(bad)["valid"] is False


# ---- the 6 possible objective families -------------------------------------

def test_six_objective_families():
    fams = _R["possible_objective_families"]
    assert len(fams) == 6
    blob = " || ".join(fams).lower()
    for must in ("market-structure trend continuation", "breakout-and-retest",
                 "pullback in trend", "pyramiding / add-to-winners",
                 "daily trend filter + h4 entry", "btc/xau strong-trend regime"):
        assert must in blob, must
    assert _R["objective_families_are_declared_not_built"] is True
    bad = {**_R, "possible_objective_families": fams[:4]}
    assert note.validate_h4_backlog_note(bad)["valid"] is False


# ---- evidence bar required before promotion (human-gated) ------------------

def test_evidence_bar_and_human_gated_promotion():
    ev = _R["required_evidence_before_promotion"].lower()
    for must in ("entry", "stop", "add", "exit"):
        assert must in ev, must
    assert _R["min_chart_examples"] == 3
    assert _R["max_chart_examples"] == 5
    assert _R["promotion_requires_explicit_human_decision"] is True
    nra = note.get_h4_backlog_note_next_action()
    assert nra == _R["next_required_action"]
    assert nra.startswith("NONE__BACKLOG_ONLY")
    assert "HUMAN_DECISION" in nra or "HUMAN" in nra


def test_label_no_candidate_no_profit_claim():
    label = note.get_h4_backlog_note_label()
    assert "BACKLOG NOTE" in label
    assert "NOT a candidate" in label
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())
    assert "NO C18" in label.upper()          # explicitly no candidate number
    # ("profitable trader" is an honest observation, not a strategy claim)
    for banned in ("EDGE CONFIRMED", "READY FOR LIVE", "APPROVED FOR LIVE"):
        assert banned not in label.upper(), banned


# ---- capability flags + scope locks ----------------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in note._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert note.validate_h4_backlog_note(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_execute", "no_candidate_creation", "no_lifecycle_entry",
                 "no_detector", "no_labels", "no_replay", "no_optimization",
                 "no_data_fetch", "no_commit", "no_push", "no_broker",
                 "no_order_logic", "no_paper_trading", "no_live_trading",
                 "no_promotion_without_human"):
        assert _R["scope_locks"][must] is True, must


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(note.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned
    for call in ast.walk(tree):
        if isinstance(call, ast.Call):
            name = (call.func.attr if isinstance(call.func, ast.Attribute)
                    else getattr(call.func, "id", ""))
            assert name not in ("open", "exec", "eval", "compile"), name

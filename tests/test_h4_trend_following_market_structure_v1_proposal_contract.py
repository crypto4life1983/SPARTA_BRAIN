"""Tests for the Candidate #18 family-proposal contract
(h4_trend_following_market_structure_v1).

Verifies: research-only, pure-proposal-only, executes nothing; chain-gated on the
valid H4 backlog note (BACKLOG_ONLY_NOT_CANDIDATE_YET); the HONESTY rule (NOT the
observed trader's exact system; exact entries/stops unavailable; objective testable
approximation) and that it cannot be flipped; H4 market-structure identity (no
indicators primary, low-frequency/patience, pyramids only on winners); materially
different from C1-C17 and NOT in the 22-family ledger; the six sub-families; the
future-data-requirements record (nothing fetched; H4/XAUUSD not local; lane limits
respected); risk-adjusted evaluation + OOS; gate sequence preserved; downstream
gates locked; capability flags + scope locks; validator anti-tamper; module
purity."""
from __future__ import annotations

import ast

import sparta_commander.h4_trend_following_market_structure_v1_proposal_contract as c18  # noqa: E501


_R = c18.build_c18_proposal(".", [])


def test_proposal_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_proposal_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C18_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert c18.validate_c18_proposal(_R)["valid"] is True


def test_candidate_identity_is_c18():
    assert _R["candidate_id"] == "C18"
    assert _R["candidate_family"] == "h4_trend_following_market_structure"
    assert _R["candidate_name"] == "h4_trend_following_market_structure_v1"
    assert _R["current_loop_stage"] == "family_proposal"


# ---- chain gate on the H4 backlog note -------------------------------------

def test_chain_gated_on_backlog_note():
    assert _R["promoted_from_backlog_note"] == (
        "BACKLOG_H4_DISCRETIONARY_TREND_FOLLOWING_V1")
    assert _R["source_note_valid"] is True
    assert _R["source_note_status"] == "BACKLOG_ONLY_NOT_CANDIDATE_YET"
    bad = {**_R, "source_note_status": "PROMOTED"}
    assert c18.validate_c18_proposal(bad)["valid"] is False


# ---- HONESTY rule: NOT the friend's exact system ---------------------------

def test_honesty_not_exact_system_is_approximation():
    assert _R["is_observed_traders_exact_system"] is False
    assert _R["is_objective_testable_approximation"] is True
    h = _R["honesty"]
    assert h["is_observed_traders_exact_system"] is False
    assert h["exact_entries_stops_add_points_available"] is False
    assert h["is_objective_testable_approximation_of_observed_behaviour"] is True
    assert "NOT the observed trader's exact system" in h["statement"]
    assert "approximation" in h["statement"].lower()
    # tamper: claiming it IS the exact system must fail
    bad = {**_R, "is_observed_traders_exact_system": True}
    assert c18.validate_c18_proposal(bad)["valid"] is False
    bad2 = {**_R, "honesty": {**h, "exact_entries_stops_add_points_available": True}}
    assert c18.validate_c18_proposal(bad2)["valid"] is False


# ---- H4 market-structure identity ------------------------------------------

def test_h4_market_structure_identity():
    assert _R["is_h4_timeframe"] is True
    assert _R["observed_timeframe"] == "H4"
    assert _R["is_market_structure_based"] is True
    assert _R["uses_indicators_as_primary"] is False
    assert _R["is_low_frequency_patience_gated"] is True
    assert _R["pyramids_only_on_confirmed_winners"] is True
    for bad_key in ("is_h4_timeframe", "is_market_structure_based",
                    "is_low_frequency_patience_gated",
                    "pyramids_only_on_confirmed_winners"):
        bad = {**_R, bad_key: False}
        assert c18.validate_c18_proposal(bad)["valid"] is False, bad_key
    bad = {**_R, "uses_indicators_as_primary": True}
    assert c18.validate_c18_proposal(bad)["valid"] is False


# ---- anti-loop: different from C1-C17, not in ledger -----------------------

def test_anti_loop_not_in_ledger_22():
    assert _R["rejected_families_count"] == 22
    assert _R["candidate_not_in_rejected_ledger"] is True
    assert len(_R["why_different_from_c1_c17"]) >= 5
    md = " || ".join(_R["why_different_from_c1_c17"]).lower()
    assert "h4" in md
    assert "structure" in md
    bad = {**_R, "rejected_families_count": 21}
    assert c18.validate_c18_proposal(bad)["valid"] is False


# ---- observed universe + lane/data limitation ------------------------------

def test_observed_universe_and_lane_limits():
    assert _R["observed_instruments"] == ["BTCUSD", "XAUUSD"]
    assert _R["xauusd_outside_current_lane"] is True
    assert "crypto H4" in _R["initial_testable_scope"]
    bad = {**_R, "observed_instruments": ["BTCUSD"]}
    assert c18.validate_c18_proposal(bad)["valid"] is False


# ---- the six sub-families --------------------------------------------------

def test_six_sub_families():
    subs = _R["sub_families"]
    assert len(subs) == 6
    keys = {s["key"] for s in subs}
    for must in ("h4_market_structure_trend_continuation",
                 "h4_breakout_and_retest_continuation", "h4_pullback_in_trend",
                 "h4_pyramiding_add_to_winners",
                 "daily_trend_filter_plus_h4_entry", "strong_trend_regime_filter"):
        assert must in keys, must
    bad = {**_R, "sub_families": subs[:5]}
    assert c18.validate_c18_proposal(bad)["valid"] is False


# ---- FUTURE data requirements recorded, nothing fetched --------------------

def test_future_data_requirements_no_fetch():
    dr = _R["data_requirements"]
    assert dr["no_data_fetched_here"] is True
    assert dr["h4_ohlc_btcusd"]["available_locally"] is False
    assert dr["h4_ohlc_xauusd"]["available_locally"] is False
    assert dr["data_sourcing_requires_separate_human_approval"] is True
    assert _R["fetches_data"] is False
    bad = {**_R, "data_requirements": {**dr, "no_data_fetched_here": False}}
    assert c18.validate_c18_proposal(bad)["valid"] is False


# ---- risk-adjusted evaluation + cost reserved ------------------------------

def test_evaluation_risk_adjusted_cost_reserved():
    em = _R["evaluation_metrics"]
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        assert m in em["primary_risk_adjusted"]
    assert "risk-adjusted" in em["win_condition"].lower()
    ct = _R["cost_assumptions"]
    assert ct["crypto_all_in_round_trip_bps"] == 37.0
    assert ct["cost_applied_only_at_replay_gate"] is True
    bad = {**_R, "cost_assumptions": {**ct, "crypto_all_in_round_trip_bps": 5.0}}
    assert c18.validate_c18_proposal(bad)["valid"] is False


# ---- gate sequence + downstream locks + next gate --------------------------

def test_gate_sequence_and_downstream_locks():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c18.validate_c18_proposal(bad)["valid"] is False, gate
    nra = c18.get_candidate_18_proposal_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C18_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT"


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c18._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c18.validate_c18_proposal(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                 "no_optimization", "no_data_fetch", "no_commit", "no_push",
                 "no_indicators_as_primary", "no_add_to_losers", "no_paper_trading",
                 "no_live_trading", "no_friends_exact_system_claim"):
        assert _R["scope_locks"][must] is True, must


def test_label_no_profitability_or_exact_system_claim():
    label = c18.get_candidate_18_proposal_label()
    assert "RESEARCH ONLY" in label
    assert "NOT their exact system" in label or "NOT a profitability claim" in label
    for banned in ("PROFITABLE STRATEGY", "EDGE CONFIRMED", "READY FOR LIVE",
                   "EXACT SYSTEM REPRODUCED"):
        assert banned not in label.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c18.__file__, encoding="utf-8").read()
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

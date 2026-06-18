"""Tests for the Candidate #18 candidate-spec contract
(h4_trend_following_market_structure_v1).

Verifies: research-only, pure-spec-only, executes nothing; chain-gated on the frozen
C18 proposal; the honesty disclosure (objective approximation, NOT the observed
trader's exact system); the seven EXACT rules (trend / entry / stop / exit /
pyramiding / invalidation / non-overlap) with the H4 market-structure identity (no
indicators primary, low frequency, pyramids only on winners, non-overlap); H4
timeframe + lane/data limitations (XAUUSD out of lane, nothing fetched); reserved
37 bps replay cost; risk-adjusted evaluation + OOS + rejection criteria; gate
sequence preserved; downstream gates locked; capability flags + scope locks;
validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.h4_trend_following_market_structure_v1_candidate_spec_contract as c18s  # noqa: E501


_R = c18s.build_c18_spec(".", [])


def test_spec_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_spec_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C18_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert c18s.validate_c18_spec(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C18"
    assert _R["candidate_family"] == "h4_trend_following_market_structure"
    assert _R["current_loop_stage"] == "candidate_spec"


def test_chain_gated_on_frozen_proposal():
    assert _R["source_proposal_verdict"] == "C18_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["source_proposal_valid"] is True
    bad = {**_R, "source_proposal_verdict": "C18_PROPOSAL_BLOCKED"}
    assert c18s.validate_c18_spec(bad)["valid"] is False


# ---- HONESTY: objective approximation, not the exact system ----------------

def test_honesty_objective_approximation():
    assert _R["is_objective_testable_approximation"] is True
    assert _R["is_observed_traders_exact_system"] is False
    assert "approximation" in _R["honesty_statement"].lower()
    bad = {**_R, "is_observed_traders_exact_system": True}
    assert c18s.validate_c18_spec(bad)["valid"] is False


# ---- the SEVEN exact rules -------------------------------------------------

def test_seven_exact_rules_present():
    for field in ("trend_rule", "entry_rule", "stop_rule", "exit_rule",
                  "pyramid_rule", "invalidation_rule", "non_overlap_rule"):
        assert _R[field], field
    assert "no indicators" in _R["trend_rule"].lower()
    assert "higher low" in _R["entry_rule"].lower()
    assert "structural stop" in _R["stop_rule"].lower()
    assert "structure" in _R["exit_rule"].lower()
    # pyramiding: profit-confirmed, never to losers
    pyr = _R["pyramid_rule"].lower()
    assert "profit" in pyr
    assert "never add to losers" in pyr
    assert "opposite" in _R["invalidation_rule"].lower()
    assert "non-overlapping" in _R["non_overlap_rule"].lower()
    for bad_field in ("trend_rule", "pyramid_rule", "non_overlap_rule"):
        bad = {**_R, bad_field: ""}
        assert c18s.validate_c18_spec(bad)["valid"] is False, bad_field


def test_h4_market_structure_identity_and_params():
    assert _R["is_h4_market_structure"] is True
    assert _R["uses_indicators_as_primary"] is False
    assert _R["is_low_frequency_patience_gated"] is True
    assert _R["pyramids_only_on_confirmed_winners"] is True
    assert _R["positions_non_overlapping_per_symbol"] is True
    sp = _R["spec_params"]
    assert sp["uses_indicators"] is False
    assert sp["max_concurrent_positions_per_symbol"] == 1
    assert sp["max_units_total"] == 3            # base + up to 2 profit-confirmed adds
    assert sp["no_parameter_optimization"] is True
    for bad_key in ("uses_indicators_as_primary",):
        bad = {**_R, bad_key: True}
        assert c18s.validate_c18_spec(bad)["valid"] is False
    bad = {**_R, "spec_params": {**sp, "max_concurrent_positions_per_symbol": 3}}
    assert c18s.validate_c18_spec(bad)["valid"] is False


# ---- timeframe + lane/data limitations -------------------------------------

def test_timeframe_and_lane_data_limits():
    assert _R["timeframe"] == "H4"
    assert _R["initial_testable_symbols"] == ["BTCUSD"]
    assert _R["observed_but_out_of_lane"] == ["XAUUSD"]
    dr = _R["data_requirements"]
    assert dr["no_data_fetched_here"] is True
    assert dr["h4_ohlc_btcusd"]["available_locally"] is False
    assert dr["h4_ohlc_xauusd"]["available_locally"] is False
    assert _R["fetches_data"] is False
    bad = {**_R, "data_requirements": {**dr, "no_data_fetched_here": False}}
    assert c18s.validate_c18_spec(bad)["valid"] is False


# ---- reserved 37 bps replay cost (not applied here) ------------------------

def test_cost_reserved_for_replay():
    cr = _R["cost_reserved"]
    assert cr["crypto_all_in_round_trip_bps"] == 37.0
    assert cr["applied_here"] is False
    assert cr["applied_at_replay_gate_only"] is True
    assert _R["all_in_round_trip_bps"] == 37.0
    bad = {**_R, "cost_reserved": {**cr, "applied_here": True}}
    assert c18s.validate_c18_spec(bad)["valid"] is False


# ---- risk-adjusted evaluation + OOS + rejection criteria -------------------

def test_evaluation_oos_rejection():
    em = _R["evaluation_metrics"]
    for m in ("sharpe_ratio", "calmar_ratio", "max_drawdown"):
        assert m in em["primary_risk_adjusted"]
    assert "risk-adjusted" in em["win_condition"].lower()
    assert _R["oos_validation"]["forward_oos_required"] is True
    rc = _R["rejection_criteria"]
    assert rc["reject_if_not_beat_buy_and_hold_risk_adjusted"] is True
    assert rc["reject_if_forward_oos_risk_adjusted_edge_fails"] is True
    assert rc["reject_if_trade_frequency_not_low"] is True
    assert rc["reject_if_pyramiding_adds_to_losers"] is True
    assert rc["raw_return_alone_is_not_sufficient"] is True
    bad = {**_R, "rejection_criteria": {**rc, "reject_if_pyramiding_adds_to_losers": False}}
    assert c18s.validate_c18_spec(bad)["valid"] is False


# ---- gate sequence + downstream locks + next gate --------------------------

def test_gate_sequence_downstream_locks_next_gate():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c18s.validate_c18_spec(bad)["valid"] is False, gate
    nra = c18s.get_candidate_18_spec_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C18_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c18s._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c18s.validate_c18_spec(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                 "no_optimization", "no_data_fetch", "no_commit", "no_push",
                 "no_indicators_as_primary", "no_add_to_losers",
                 "no_overlapping_positions", "no_paper_trading", "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_label_no_profitability_or_exact_system_claim():
    label = c18s.get_candidate_18_spec_label()
    assert "RESEARCH ONLY" in label
    assert "NOT their exact system" in label or "NOT a profitability claim" in label
    for banned in ("EDGE CONFIRMED", "READY FOR LIVE", "EXACT SYSTEM REPRODUCED"):
        assert banned not in label.upper(), banned


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c18s.__file__, encoding="utf-8").read()
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

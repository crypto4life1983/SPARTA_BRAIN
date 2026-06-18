"""Tests for the Candidate #16 candidate-spec contract
(cointegration_pairs_market_neutral_v1).

Verifies: research-only, pure-spec-only; chain-gated on the frozen C16 proposal
(selected statistical_arbitrage_pairs); deterministic pair universe;
cointegration/spread + entry/exit + long/short leg + stop/risk logic; two-leg
74 bps cost reserved; MARKET-NEUTRAL baselines (random + zero-edge null, NOT
buy-and-hold); the FORBIDDEN directional-carry / buy-and-hold shortcut; dollar/
beta-neutral identity; excluded from C1-C15 + not reusing C15; both windows;
downstream gates locked; a Gate-Decision-Coordinator-style decision-ready report;
capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.cointegration_pairs_market_neutral_v1_spec_contract as c16s  # noqa: E501


_R = c16s.build_c16_spec(".", [])


# ---- core: research-only, pure, frozen, validates --------------------------

def test_spec_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_spec_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C16_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert c16s.validate_c16_spec(_R)["valid"] is True


def test_chain_gated_on_frozen_proposal():
    assert _R["proposal_valid"] is True
    assert _R["proposal_verdict"] == "C16_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["selected_tournament_family"] == "statistical_arbitrage_pairs"


# ---- deterministic pair universe -------------------------------------------

def test_deterministic_pair_universe():
    assert _R["pair_universe_is_deterministic"] is True
    pairs = {p["pair"] for p in _R["pair_universe"]}
    assert pairs == {"ETHBTC", "SOLETH", "SOLBTC"}
    for p in _R["pair_universe"]:
        assert p["numerator"] in ("BTCUSD", "ETHUSD", "SOLUSD")
        assert p["denominator"] in ("BTCUSD", "ETHUSD", "SOLUSD")


# ---- cointegration / entry / exit / leg / stop logic -----------------------

def test_cointegration_and_trade_logic_present():
    assert "cointegrat" in _R["cointegration_logic"].lower()
    assert "z-score" in _R["cointegration_logic"].lower() or "z-score" in _R["entry_logic"].lower()
    assert "long the cheap leg" in _R["entry_logic"].lower()
    assert "short the rich leg" in _R["entry_logic"].lower()
    assert "revert" in _R["exit_logic"].lower()
    assert "dollar-neutral" in _R["long_short_leg_handling"].lower()
    assert "invalidation" in _R["stop_risk_logic"].lower() or "stop" in _R["stop_risk_logic"].lower()
    assert _R["uses_cointegration_validity_gate"] is True
    sp = _R["spec_params"]
    assert sp["entry_z"] == 2.0 and sp["exit_z"] == 0.5 and sp["stop_z"] == 3.5
    assert sp["fixed_horizon"] is None


# ---- two-leg fee/slippage (74 bps) -----------------------------------------

def test_two_leg_cost_reserved():
    assert _R["all_in_per_leg_round_trip_bps"] == 37.0
    assert _R["fee_per_leg_round_trip_bps"] + _R["slippage_per_leg_round_trip_bps"] == 37.0
    assert _R["legs_per_pair_trade"] == 2
    assert _R["all_in_pair_round_trip_bps"] == 74.0
    bad = {**_R, "all_in_pair_round_trip_bps": 5.0}
    assert c16s.validate_c16_spec(bad)["valid"] is False
    bad2 = {**_R, "legs_per_pair_trade": 1}
    assert c16s.validate_c16_spec(bad2)["valid"] is False


# ---- market-neutral baselines (NOT buy-and-hold) ---------------------------

def test_market_neutral_baselines():
    br = _R["baselines_required"]
    assert br["random_entry"]["required"] is True
    assert br["zero_edge_spread_null"]["required"] is True
    assert br["buy_and_hold"]["is_comparator"] is False
    assert _R["forward_oos"]["required"] is True
    bad = {**_R, "baselines_required": {**br,
           "buy_and_hold": {"is_comparator": True}}}
    assert c16s.validate_c16_spec(bad)["valid"] is False


# ---- forbidden directional-carry / buy-and-hold shortcut -------------------

def test_forbidden_carry_shortcut():
    fc = _R["forbidden_carry_shortcut"]
    assert fc["net_directional_exposure_must_be_near_zero"] is True
    assert fc["must_not_rely_on_long_leg_drift"] is True
    assert fc["must_not_rely_on_buy_and_hold_carry"] is True
    assert fc["max_abs_net_beta"] <= 0.1
    dg = _R["decisive_replay_gates"]
    assert dg["no_directional_carry_shortcut"] is True
    assert dg["market_neutral_net_beta_near_zero"] is True
    assert dg["must_beat_random_entry"] is True
    assert dg["must_beat_zero_edge_spread_null"] is True
    assert dg["must_be_net_positive_after_two_leg_cost"] is True
    assert _R["relies_on_directional_carry"] is False
    for bad_key in ("net_directional_exposure_must_be_near_zero",
                    "must_not_rely_on_buy_and_hold_carry"):
        bad = {**_R, "forbidden_carry_shortcut": {**fc, bad_key: False}}
        assert c16s.validate_c16_spec(bad)["valid"] is False, bad_key


# ---- market-neutral identity + anti-loop -----------------------------------

def test_market_neutral_identity_and_anti_loop():
    assert _R["is_market_neutral"] is True
    assert _R["is_dollar_neutral"] is True and _R["is_beta_neutral"] is True
    assert _R["is_directional"] is False
    assert _R["candidate_not_in_rejected_ledger"] is True
    assert _R["does_not_reuse_c15"] is True
    assert _R["rejected_families_count"] == 20
    for bad_key in ("is_market_neutral", "is_dollar_neutral"):
        bad = {**_R, bad_key: False}
        assert c16s.validate_c16_spec(bad)["valid"] is False, bad_key
    bad2 = {**_R, "is_directional": True}
    assert c16s.validate_c16_spec(bad2)["valid"] is False


# ---- both windows ----------------------------------------------------------

def test_durability_and_recent_relevance_windows():
    w = _R["evaluation_windows"]
    assert w["durability_window_days"] == 1095
    assert w["recent_relevance_window_days_min"] == 90
    assert w["recent_relevance_window_days_max"] == 180
    assert w["forward_oos_required"] is True


# ---- decision-ready report (Gate Decision Coordinator v1) ------------------

def test_decision_ready_report_uses_coordinator():
    rep = c16s.decision_ready_report(_R)
    assert rep["uses_gate_decision_coordinator_v1"] is True
    assert rep["section"] == "gate_decision_coordinator"
    assert rep["decision_ready"] is True
    assert rep["candidate_id"] == "C16"
    assert rep["next_gate"] == (
        "HUMAN_DECISION_C16_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT")
    # the coordinator sees C16 as the open gate and recommends its decision token
    assert rep["recommendation_kind"] == "RECOMMEND_GATE_DECISION"
    assert rep["paste_this"].startswith("HUMAN_DECISION_C16_")
    assert rep["requires_human_approval"] is True
    assert rep["executes_nothing"] is True
    # C15 stays summarized as closed + excluded
    c15 = next(c for c in rep["closed_excluded"] if c["candidate"] == "C15")
    assert c15["excluded_from_reproposal"] is True


# ---- downstream gates locked + flags + scope locks -------------------------

def test_downstream_gates_locked():
    for gate in ("detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c16s.validate_c16_spec(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c16s._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c16s.validate_c16_spec(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_detector", "no_labels", "no_replay",
                 "no_optimization", "no_commit", "no_push", "no_broker",
                 "no_paper_trading", "no_live_trading", "no_reuse_of_c15",
                 "no_directional_carry_shortcut"):
        assert _R["scope_locks"][must] is True, must


def test_label_and_next_action_no_readiness():
    label = c16s.get_candidate_16_spec_label()
    assert "RESEARCH ONLY" in label
    assert "NOT a profitability claim" in label or "NOT A PROFITABILITY" in label.upper()
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned
    nra = c16s.get_candidate_16_spec_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C16_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT"
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c16s.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random"}
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

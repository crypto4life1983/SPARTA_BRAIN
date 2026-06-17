"""Tests for the Strategy Family Tournament v1 family-proposal contract.

Verifies: research-only, pure-proposal-only, executes nothing; the gate sequence
is preserved; exactly the 7 required families are included with every required
per-family field (core idea / symbols / timeframes / regime / entry / exit / risk
/ difference-from-C1-C14 / failure mode); market making is excluded with a reason;
durability is weighted above recent relevance (C14 lesson) and drives the ranking;
the durability(3yr)/recent-relevance(3-6mo)/forward-OOS/regime-tag windows are
present; the portfolio objective (low-corr / capital-efficient / low-overlap /
different holding periods) is declared not computed; the recommended first family
is trend following; capability flags + scope locks; validator anti-tamper; purity."""
from __future__ import annotations

import ast

import sparta_commander.strategy_family_tournament_v1_proposal_contract as sft


_R = sft.build_strategy_family_tournament_proposal(".", [])


# ---- core: research-only, pure, validates ----------------------------------

def test_proposal_pure_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_proposal_only"] is True
    assert sft.validate_strategy_family_tournament_proposal(_R)["valid"] is True


def test_gate_sequence_preserved():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    assert _R["gate_sequence_preserved_unchanged"] is True


# ---- the 7 families + full per-family spec ---------------------------------

def test_seven_included_families():
    assert set(_R["included_family_keys"]) == {
        "trend_following", "breakout_trading", "mean_reversion",
        "momentum_relative_strength", "statistical_arbitrage_pairs",
        "swing_trading", "position_trading"}
    assert len(_R["included_family_keys"]) == 7


def test_every_family_has_full_spec():
    fields = ("core_idea", "symbols", "timeframes", "expected_regime",
              "entry_logic", "exit_logic", "risk_logic",
              "difference_from_c1_c14", "expected_failure_mode")
    for f in _R["families"]:
        for field in fields:
            assert f.get(field), "%s missing %s" % (f.get("key"), field)
    bad = {**_R, "anti_loop_each_family_differs_from_c1_c14": False}
    assert sft.validate_strategy_family_tournament_proposal(bad)["valid"] is False


# ---- market making excluded ------------------------------------------------

def test_market_making_excluded_with_reason():
    assert "market_making" in _R["excluded_family_keys"]
    assert "market_making" not in _R["included_family_keys"]
    mm = next(f for f in _R["excluded_families"] if f["key"] == "market_making")
    assert mm["included"] is False
    reason = mm["exclusion_reason"].lower()
    assert "order-book" in reason or "order book" in reason
    assert "spread" in reason and "infrastructure" in reason
    assert _R["scope_locks"]["no_market_making"] is True
    assert _R["market_making"] is False


# ---- durability weighted above relevance (C14 lesson) ----------------------

def test_durability_weighted_above_recent_relevance():
    sw = _R["scoring_weights"]
    assert sw["durability_3yr"] > sw["recent_relevance"]
    assert _R["durability_weighted_above_relevance"] is True
    assert _R["c14_lesson"]
    bad = {**_R, "scoring_weights": {"durability_3yr": 0.1,
                                     "recent_relevance": 0.9}}
    assert sft.validate_strategy_family_tournament_proposal(bad)["valid"] is False


# ---- evaluation windows (requirement 7) ------------------------------------

def test_evaluation_windows_present():
    w = _R["evaluation_windows"]
    assert w["durability_window_days"] == 1095            # 3 years
    assert w["recent_relevance_window_days_min"] == 90    # 3 months
    assert w["recent_relevance_window_days_max"] == 180   # 6 months
    assert w["forward_oos_required"] is True
    assert w["regime_specific_tagging_required"] is True
    assert set(w["regimes"]) == {"bull", "bear", "chop"}
    bad = {**_R, "evaluation_windows": {**w, "forward_oos_required": False}}
    assert sft.validate_strategy_family_tournament_proposal(bad)["valid"] is False


# ---- portfolio objective (requirement 8) -----------------------------------

def test_portfolio_objective_declared_not_computed():
    po = _R["portfolio_objective"]
    for k in ("prefer_low_correlation", "prefer_capital_efficient",
              "prefer_low_overlap", "prefer_different_holding_periods"):
        assert po[k] is True
    assert po["computed_in_this_contract"] is False
    for dim in ("return_stream_correlation", "capital_efficiency",
                "trade_time_overlap", "holding_period_bucket"):
        assert dim in po["tracked_dimensions"]
    bad = {**_R, "portfolio_objective": {**po, "computed_in_this_contract": True}}
    assert sft.validate_strategy_family_tournament_proposal(bad)["valid"] is False


# ---- scoring + ranking + recommended first ---------------------------------

def test_scoring_excludes_market_making():
    mm = sft.score_family({"key": "market_making", "included": False})
    assert mm["scorable"] is False
    assert mm["reason"] == "family_excluded_not_suitable_now"


def test_ranking_is_sorted_desc_and_complete():
    ranked = _R["ranking"]
    assert len(ranked) == 7
    scores = [r["priority_score"] for r in ranked]
    assert scores == sorted(scores, reverse=True)


def test_recommended_first_family_is_trend_following():
    first = _R["recommended_first_family"]
    assert first["key"] == "trend_following"
    # it must out-rank every other included family
    ranked = _R["ranking"]
    assert ranked[0]["key"] == "trend_following"
    others = [r["priority_score"] for r in ranked[1:]]
    assert all(first["priority_score"] >= s for s in others)


def test_rejected_ledger_is_19_and_anti_loop_set():
    assert _R["rejected_families_count"] == 19
    assert "conviction_bar_follow_through" in _R["rejected_families_c1_to_c14"]
    assert _R["anti_loop_each_family_differs_from_c1_c14"] is True


# ---- capability flags + scope locks + label --------------------------------

def test_capability_flags_all_false_and_tamper_rejected():
    for flag in sft._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert sft.validate_strategy_family_tournament_proposal(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_data_fetch", "no_backtest", "no_labels",
                 "no_replay", "no_commit", "no_push", "no_paper_trading",
                 "no_live_trading", "no_broker", "no_market_making",
                 "no_rejected_family_repropose"):
        assert _R["scope_locks"][must] is True, must


def test_label_and_next_action_no_readiness():
    label = sft.get_strategy_family_tournament_label()
    assert "RESEARCH ONLY" in label
    assert "PROPOSAL ONLY" in label.upper() or "PURE PROPOSAL" in label.upper()
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE",
                   "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned not in label.upper(), banned
    nra = sft.get_strategy_family_tournament_next_action()
    assert nra == _R["next_required_action"]
    assert nra.startswith("HUMAN_DECISION_")
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(sft.__file__, encoding="utf-8").read()
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

"""Tests for the Candidate #17 fee-honest replay results review contract
(risk_adjusted_portfolio_construction_vol_targeted_allocation_v1).

Verifies: research-only, replay-review-only, executes nothing; chain-gated on the
frozen C17 labels review; uses FROZEN local data only and pins the exact source +
labels + artifact SHAs; APPLIES the reserved 37 bps cost (cannot be dropped); pins
the real-candle risk-adjusted metrics (Sharpe / Calmar / max-drawdown / net-return /
turnover-cost / 2026 forward-OOS) for the strategy, per-asset buy-and-hold, and the
equal-weight basket; records the HONEST decisive verdict (REJECTION -- does not beat
either baseline risk-adjusted; the only win is lower drawdown) and cannot be flipped
to a pass; makes NO profitability claim; downstream gates locked; capability flags +
scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_replay_results_review_contract as r17  # noqa: E501


_R = r17.build_c17_replay_review(".", [])


# ---- core: research-only, replay-review-only, frozen, validates ------------

def test_review_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_replay_review_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C17_REPLAY_FROZEN_FOR_HUMAN_REVIEW"
    assert r17.validate_c17_replay_review(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C17"
    assert _R["candidate_family"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation")


# ---- chain gate on the frozen C17 labels review ----------------------------

def test_chain_gated_on_frozen_labels_review():
    assert _R["labels_review_verdict"] == "C17_LABELS_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["labels_review_valid"] is True
    bad = {**_R, "labels_review_verdict": "C17_LABELS_BLOCKED"}
    assert r17.validate_c17_replay_review(bad)["valid"] is False


# ---- frozen local data only + pinned SHAs ----------------------------------

def test_frozen_local_data_and_pinned_shas():
    assert _R["uses_frozen_local_data_only"] is True
    assert _R["expected_source_sha256"]["BTCUSD"] == (
        "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88")
    assert len(_R["expected_ledger_sha256"]) == 64
    assert len(_R["expected_summary_sha256"]) == 64
    assert _R["expected_labels_sha256"] == (
        "32ffb538c09d0158027071df19ec4749e894bd568225f7503a4fa7d2f349a7c7")
    bad = {**_R, "expected_ledger_sha256": "0" * 64}
    assert r17.validate_c17_replay_review(bad)["valid"] is False


# ---- the reserved 37 bps cost is APPLIED and not droppable -----------------

def test_cost_model_applied_37bps():
    assert _R["all_in_round_trip_bps"] == 37.0
    assert _R["fee_round_trip_bps"] + _R["slippage_round_trip_bps"] == 37.0
    assert _R["one_way_cost_bps"] == 18.5
    assert _R["cost_model_applied_here"] is True
    assert _R["total_cost_drag"] > 0.0
    bad = {**_R, "all_in_round_trip_bps": 0.0}
    assert r17.validate_c17_replay_review(bad)["valid"] is False
    bad2 = {**_R, "cost_model_applied_here": False}
    assert r17.validate_c17_replay_review(bad2)["valid"] is False


# ---- pinned risk-adjusted metrics ------------------------------------------

def test_pinned_metrics_sharpe_calmar_mdd_netreturn():
    s = _R["strategy_metrics"]
    assert s["sharpe"] == 0.80148
    assert s["calmar"] == 0.466046
    assert s["max_drawdown"] == -0.377617
    assert s["net_return"] == 1.503209
    assert abs(s["ann_vol"] - 0.20) < 0.10          # ~20% vol target, realized 23.8%
    bh = _R["buy_and_hold_metrics"]
    assert set(bh.keys()) == {"BTCUSD", "ETHUSD", "SOLUSD"}
    assert bh["SOLUSD"]["sharpe"] == 1.079089
    ew = _R["equal_weight_basket_metrics"]
    assert ew["sharpe"] == 1.035569
    assert ew["calmar"] == 0.743794
    # 2026 forward-OOS metrics present
    assert _R["strategy_forward_oos_metrics"]["n_days"] == 159
    assert _R["equal_weight_basket_forward_oos_metrics"]["sharpe"] == -1.600638


def test_drawdown_materially_lower_than_baselines():
    s = _R["strategy_metrics"]
    bh = _R["buy_and_hold_metrics"]
    ew = _R["equal_weight_basket_metrics"]
    # the strategy's only structural win: much smaller drawdown
    assert s["max_drawdown"] > ew["max_drawdown"]                  # less negative
    assert all(s["max_drawdown"] > bh[a]["max_drawdown"] for a in bh)


# ---- HONEST decisive REJECTION verdict -------------------------------------

def test_decisive_rejection_honest_and_frozen():
    g = _R["decisive_gate_results"]
    assert g["beats_buy_and_hold_risk_adjusted"] is False
    assert g["beats_equal_weight_basket_risk_adjusted"] is False
    assert g["max_drawdown_no_worse_than_buy_and_hold"] is True
    assert g["max_drawdown_no_worse_than_equal_weight"] is True
    assert g["forward_oos_risk_adjusted_edge_holds"] is False
    assert _R["all_decisive_gates_pass"] is False
    assert _R["decisive_rejection_pressure"] is True
    assert _R["only_win_is_lower_drawdown"] is True
    assert _R["raw_return_alone_is_not_sufficient"] is True
    assert _R["rejection_reasons"]
    # the honest rejection cannot be flipped to a pass
    bad = {**_R, "all_decisive_gates_pass": True}
    assert r17.validate_c17_replay_review(bad)["valid"] is False
    bad2 = {**_R, "decisive_gate_results": {
        **g, "beats_equal_weight_basket_risk_adjusted": True}}
    assert r17.validate_c17_replay_review(bad2)["valid"] is False


def test_next_action_reject_or_review():
    nra = r17.get_candidate_17_replay_review_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C17_REJECT_AT_REPLAY_OR_REVIEW"


def test_label_no_profitability_claim():
    label = r17.get_candidate_17_replay_review_label()
    assert "RESEARCH ONLY" in label
    assert "REJECTED" in label
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "BEATS BUY-AND-HOLD",
                   "READY FOR LIVE", "APPROVED FOR PAPER"):
        assert banned not in label.upper(), banned


# ---- downstream gates locked + flags + scope locks -------------------------

def test_downstream_gates_locked():
    for gate in ("promote_gate_locked", "robustness_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert r17.validate_c17_replay_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in r17._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert r17.validate_c17_replay_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_re_replay", "no_relabel", "no_re_allocate",
                 "no_optimization", "no_reparameterization", "no_cost_drop",
                 "no_commit", "no_push", "no_auto_trading", "no_paper_trading",
                 "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(r17.__file__, encoding="utf-8").read()
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

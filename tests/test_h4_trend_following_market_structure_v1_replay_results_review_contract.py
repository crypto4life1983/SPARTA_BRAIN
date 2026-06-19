"""Tests for the Candidate #18 fee-honest replay results review contract
(h4_trend_following_market_structure_v1).

Verifies: research-only, replay-review-only, executes nothing; chain-gated on the
frozen C18 labels review; uses FROZEN local data only and pins the exact source +
labels + artifact SHAs; APPLIES the reserved 37 bps cost (cannot be dropped); pins the
real-candle risk-adjusted metrics (Sharpe / Calmar / max-drawdown / net-return /
win-rate / R / cost-drag / 2026 forward-OOS) for the strategy and BTC buy-and-hold;
records the HONEST decisive verdict (REJECTION -- does not beat buy-and-hold
risk-adjusted; only win is lower drawdown) and cannot be flipped to a pass; no
optimization / re-parameterization / parameter sweep; no XAUUSD; downstream gates
locked; capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.h4_trend_following_market_structure_v1_replay_results_review_contract as r18  # noqa: E501


_R = r18.build_c18_replay_review(".", [])


def test_review_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_replay_review_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C18_REPLAY_FROZEN_FOR_HUMAN_REVIEW"
    assert r18.validate_c18_replay_review(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C18"
    assert _R["candidate_family"] == "h4_trend_following_market_structure"


def test_chain_gated_on_frozen_labels_review():
    assert _R["labels_review_verdict"] == "C18_LABELS_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["labels_review_valid"] is True
    bad = {**_R, "labels_review_verdict": "C18_LABELS_BLOCKED"}
    assert r18.validate_c18_replay_review(bad)["valid"] is False


def test_frozen_local_data_and_pinned_shas():
    assert _R["uses_frozen_local_data_only"] is True
    assert _R["expected_source_sha256"] == (
        "aec42241f47192ae29331f4b67a64500ca38aad1f403f13d0de5b405f7ecbaec")
    assert _R["expected_labels_sha256"] == (
        "907705d9506b1db79141118618b627248753cecab383d30564fbf5b7d8bc9e11")
    assert len(_R["expected_ledger_sha256"]) == 64
    assert len(_R["expected_summary_sha256"]) == 64
    bad = {**_R, "expected_ledger_sha256": "0" * 64}
    assert r18.validate_c18_replay_review(bad)["valid"] is False


def test_cost_model_applied_37bps():
    assert _R["all_in_round_trip_bps"] == 37.0
    assert _R["fee_round_trip_bps"] + _R["slippage_round_trip_bps"] == 37.0
    assert _R["one_way_cost_bps"] == 18.5
    assert _R["cost_model_applied_here"] is True
    assert _R["total_cost_drag"] > 0.0
    bad = {**_R, "all_in_round_trip_bps": 0.0}
    assert r18.validate_c18_replay_review(bad)["valid"] is False
    bad2 = {**_R, "cost_model_applied_here": False}
    assert r18.validate_c18_replay_review(bad2)["valid"] is False


def test_pinned_metrics_and_btc_buy_and_hold():
    s = _R["strategy_metrics"]
    assert s["sharpe"] == 0.5158
    assert s["calmar"] == 0.246771
    assert s["max_drawdown"] == -0.382027
    assert s["net_return"] == 0.954079
    bh = _R["buy_and_hold_metrics"]
    assert bh["sharpe"] == 0.933316
    assert bh["calmar"] == 0.602886
    assert bh["max_drawdown"] == -0.770434
    assert _R["win_rate"] == 0.151671
    assert _R["total_R"] == -101.4122
    assert _R["trade_count"] == 389
    # 2026 forward-OOS present for both
    assert _R["strategy_forward_oos_metrics"]["n_bars"] == 949
    assert _R["buy_and_hold_forward_oos_metrics"]["sharpe"] == -1.467162


def test_drawdown_lower_than_buy_and_hold():
    s = _R["strategy_metrics"]
    bh = _R["buy_and_hold_metrics"]
    # the strategy's only structural win: much smaller drawdown
    assert s["max_drawdown"] > bh["max_drawdown"]                 # less negative
    assert s["ann_vol"] < bh["ann_vol"]


def test_decisive_rejection_honest_and_frozen():
    g = _R["decisive_gate_results"]
    assert g["beats_buy_and_hold_risk_adjusted"] is False
    assert g["max_drawdown_no_worse_than_buy_and_hold"] is True
    assert g["forward_oos_risk_adjusted_edge_holds"] is False
    assert _R["all_decisive_gates_pass"] is False
    assert _R["decisive_rejection_pressure"] is True
    assert _R["only_win_is_lower_drawdown"] is True
    assert _R["raw_return_alone_is_not_sufficient"] is True
    assert _R["rejection_reasons"]
    # the honest rejection cannot be flipped to a pass
    bad = {**_R, "all_decisive_gates_pass": True}
    assert r18.validate_c18_replay_review(bad)["valid"] is False
    bad2 = {**_R, "decisive_gate_results": {
        **g, "beats_buy_and_hold_risk_adjusted": True}}
    assert r18.validate_c18_replay_review(bad2)["valid"] is False


def test_no_optimization_or_sweep():
    assert _R["no_parameter_optimization"] is True
    assert _R["no_reparameterization"] is True
    assert _R["no_parameter_sweep"] is True
    assert _R["runs_optimization"] is False
    assert _R["runs_parameter_sweep"] is False
    assert _R["uses_xauusd"] is False
    bad = {**_R, "no_parameter_sweep": False}
    assert r18.validate_c18_replay_review(bad)["valid"] is False


def test_next_action_reject_or_review():
    nra = r18.get_candidate_18_replay_review_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C18_REJECT_AT_REPLAY_OR_REVIEW"
    label = r18.get_candidate_18_replay_review_label()
    assert "REJECTED" in label
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())


def test_downstream_gates_locked():
    for gate in ("promote_gate_locked", "robustness_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert r18.validate_c18_replay_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in r18._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert r18.validate_c18_replay_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_re_replay", "no_relabel", "no_re_detect",
                 "no_optimization", "no_reparameterization", "no_parameter_sweep",
                 "no_xauusd", "no_cost_drop", "no_commit", "no_push",
                 "no_paper_trading", "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(r18.__file__, encoding="utf-8").read()
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

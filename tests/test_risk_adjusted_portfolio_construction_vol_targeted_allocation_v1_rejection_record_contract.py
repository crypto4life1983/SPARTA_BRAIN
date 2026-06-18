"""Tests for the Candidate #17 formal rejection / closeout record contract
(risk_adjusted_portfolio_construction_vol_targeted_allocation_v1).

Verifies: research-only, rejection-record-only, executes nothing; chain-gated on the
frozen decisive-rejection replay review; records REJECT_C17_AT_FEE_HONEST_REPLAY,
not active / not parked / kept on record; anchored to the pushed replay-review commit
329b56ce and preserves the labels-review commit 20648497; preserves the verbatim
conclusion + the risk-adjusted failure facts (cannot be flipped); cites the 5 pushed
gate commits; the ledger bump is 21 -> 22; downstream gates locked; capability flags
+ scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_rejection_record_contract as rj17  # noqa: E501


_R = rj17.build_c17_rejection_record(".", [])


def test_record_research_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_rejection_record_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "REJECT_C17_AT_FEE_HONEST_REPLAY"
    assert rj17.validate_c17_rejection_record(_R)["valid"] is True


def test_candidate_identity_and_status():
    assert _R["candidate_id"] == "C17"
    assert _R["rejection_status"] == "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD"
    assert _R["rejected_at_stage"] == "fee_honest_replay"
    assert _R["is_active_candidate"] is False
    assert _R["parked_as_active"] is False
    assert _R["kept_on_record"] is True


def test_chain_gated_on_frozen_replay_review():
    assert _R["replay_review_verdict"] == "C17_REPLAY_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["replay_review_valid"] is True
    assert _R["replay_all_decisive_gates_pass"] is False
    assert _R["replay_decisive_rejection_pressure"] is True


def test_anchored_to_pushed_commits():
    assert _R["anchored_to_replay_review_commit"] == (
        "329b56ce87de23899aa5ceb510d66eb1959bd3bf")
    assert _R["labels_review_commit"] == (
        "2064849719e7b09077ce2e983c6ecff22a24cd63")
    bad = {**_R, "anchored_to_replay_review_commit": "0" * 40}
    assert rj17.validate_c17_rejection_record(bad)["valid"] is False


def test_pushed_evidence_chain_five_gates():
    chain = {e["stage"]: e["commit"] for e in _R["pushed_evidence_chain"]}
    for stage in ("family_proposal", "candidate_spec",
                  "detector_spec_and_synthetic_dry_run", "real_candle_labels_review",
                  "fee_honest_replay_review"):
        assert stage in chain
        assert len(chain[stage]) == 40


def test_honest_rejection_facts_preserved():
    eh = _R["evidence_headline"]
    assert eh["did_not_beat_buy_and_hold_risk_adjusted"] is True
    assert eh["did_not_beat_equal_weight_risk_adjusted"] is True
    assert eh["forward_oos_edge_failed"] is True
    assert eh["only_win_is_lower_drawdown"] is True
    assert eh["cost_model_applied_37bps"] is True
    assert _R["raw_return_alone_is_not_sufficient"] is True
    assert len(_R["rejection_reasons"]) >= 3
    assert _R["conclusion"] == rj17.CONCLUSION
    # the honest rejection cannot be flipped: a headline finding cleared -> invalid
    bad = {**_R, "evidence_headline": {
        **eh, "did_not_beat_equal_weight_risk_adjusted": False}}
    assert rj17.validate_c17_rejection_record(bad)["valid"] is False


def test_pinned_metrics_consistent_with_rejection():
    s = _R["strategy_metrics"]
    ew = _R["equal_weight_basket_metrics"]
    assert s["sharpe"] == 0.80148
    # strategy is genuinely worse risk-adjusted than the basket
    assert s["sharpe"] < ew["sharpe"]
    assert s["calmar"] < ew["calmar"]
    # but had the lower drawdown
    assert s["max_drawdown"] > ew["max_drawdown"]
    bad = {**_R, "strategy_metrics": {**s, "sharpe": 9.9, "calmar": 9.9}}
    assert rj17.validate_c17_rejection_record(bad)["valid"] is False


def test_ledger_bump_21_to_22():
    lb = _R["ledger_bump"]
    assert lb["from_count"] == 21
    assert lb["to_count"] == 22
    assert lb["add_family"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation")
    assert lb["applied_in_this_bundle"] is True


def test_next_action_closed_and_label():
    nra = rj17.get_candidate_17_rejection_record_next_action()
    assert nra == _R["next_required_action"]
    assert nra.startswith("NONE__C17_CLOSED")
    label = rj17.get_candidate_17_rejection_record_label()
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_downstream_gates_locked():
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "promote_gate_locked", "paper_trading_gate_locked",
                 "micro_live_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert rj17.validate_c17_rejection_record(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rj17._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert rj17.validate_c17_rejection_record(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_re_replay", "no_pnl", "no_re_allocate", "no_optimization",
                 "no_reparameterization", "no_reactivation", "no_commit",
                 "no_push", "no_auto_trading", "no_paper_trading",
                 "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rj17.__file__, encoding="utf-8").read()
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

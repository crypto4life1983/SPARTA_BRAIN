"""Tests for the Candidate #18 formal rejection / closeout record contract
(h4_trend_following_market_structure_v1).

Verifies: research-only, rejection-record-only, executes nothing; chain-gated on the
frozen decisive-rejection replay review; records REJECT_C18_AT_FEE_HONEST_REPLAY,
not active / not parked / kept on record; anchored to the pushed replay-review commit
e2251052 and preserves the labels-review commit 0e137728; preserves the verbatim
conclusion + the risk-adjusted / forward-OOS / negative-expectancy failure facts
(cannot be flipped); states it rejects the OBJECTIVE approximation and NOT the
observed trader's exact system; cites the 5 pushed gate commits; the ledger bump is
22 -> 23; downstream gates locked; capability flags + scope locks; validator
anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.h4_trend_following_market_structure_v1_rejection_record_contract as rj18  # noqa: E501


_R = rj18.build_c18_rejection_record(".", [])


def test_record_research_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_rejection_record_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "REJECT_C18_AT_FEE_HONEST_REPLAY"
    assert rj18.validate_c18_rejection_record(_R)["valid"] is True


def test_candidate_identity_and_status():
    assert _R["candidate_id"] == "C18"
    assert _R["candidate_family"] == "h4_trend_following_market_structure"
    assert _R["rejection_status"] == "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD"
    assert _R["rejected_at_stage"] == "fee_honest_replay"
    assert _R["is_active_candidate"] is False
    assert _R["parked_as_active"] is False
    assert _R["kept_on_record"] is True


def test_rejects_approximation_not_traders_exact_system():
    assert _R["rejects_objective_approximation_only"] is True
    assert _R["does_not_reject_observed_traders_exact_system"] is True
    assert _R["is_objective_approximation_not_exact_system"] is True
    bad = {**_R, "does_not_reject_observed_traders_exact_system": False}
    assert rj18.validate_c18_rejection_record(bad)["valid"] is False
    bad2 = {**_R, "rejects_objective_approximation_only": False}
    assert rj18.validate_c18_rejection_record(bad2)["valid"] is False


def test_chain_gated_on_frozen_replay_review():
    assert _R["replay_review_verdict"] == "C18_REPLAY_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["replay_review_valid"] is True
    assert _R["replay_all_decisive_gates_pass"] is False
    assert _R["replay_decisive_rejection_pressure"] is True


def test_anchored_to_pushed_commits():
    assert _R["anchored_to_replay_review_commit"] == (
        "e22510521c9d954b36e52200c1dbcee498be5f82")
    assert _R["labels_review_commit"] == (
        "0e1377284ea865ac33a7988c61b5da7dc2417230")
    bad = {**_R, "anchored_to_replay_review_commit": "0" * 40}
    assert rj18.validate_c18_rejection_record(bad)["valid"] is False


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
    assert eh["forward_oos_edge_failed"] is True
    assert eh["negative_expectancy_under_costs"] is True
    assert eh["only_win_is_lower_drawdown"] is True
    assert eh["cost_model_applied_37bps"] is True
    assert _R["raw_return_alone_is_not_sufficient"] is True
    assert len(_R["rejection_reasons"]) >= 3
    assert _R["conclusion"] == rj18.CONCLUSION
    # the honest rejection cannot be flipped: a headline finding cleared -> invalid
    bad = {**_R, "evidence_headline": {
        **eh, "did_not_beat_buy_and_hold_risk_adjusted": False}}
    assert rj18.validate_c18_rejection_record(bad)["valid"] is False


def test_pinned_metrics_consistent_with_rejection():
    s = _R["strategy_metrics"]
    bh = _R["buy_and_hold_metrics"]
    assert s["sharpe"] == 0.5158
    assert s["net_return"] == 0.954079        # +95.4% raw
    # strategy is genuinely worse risk-adjusted than buy-and-hold
    assert s["sharpe"] < bh["sharpe"]
    assert s["calmar"] < bh["calmar"]
    # but had the lower drawdown
    assert s["max_drawdown"] > bh["max_drawdown"]
    # negative expectancy under honest costs
    assert _R["total_R"] < 0 and _R["avg_R"] < 0
    bad = {**_R, "strategy_metrics": {**s, "sharpe": 9.9, "calmar": 9.9}}
    assert rj18.validate_c18_rejection_record(bad)["valid"] is False


def test_negative_expectancy_cannot_be_flipped():
    bad = {**_R, "total_R": 50.0, "avg_R": 0.5}
    assert rj18.validate_c18_rejection_record(bad)["valid"] is False


def test_ledger_bump_22_to_23():
    lb = _R["ledger_bump"]
    assert lb["from_count"] == 22
    assert lb["to_count"] == 23
    assert lb["add_family"] == "h4_trend_following_market_structure"
    assert lb["applied_in_this_bundle"] is True


def test_next_action_closed_and_label():
    nra = rj18.get_candidate_18_rejection_record_next_action()
    assert nra == _R["next_required_action"]
    assert nra.startswith("NONE__C18_CLOSED")
    label = rj18.get_candidate_18_rejection_record_label()
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())
    for banned in ("EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_downstream_gates_locked():
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "promote_gate_locked", "paper_trading_gate_locked",
                 "micro_live_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert rj18.validate_c18_rejection_record(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rj18._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert rj18.validate_c18_rejection_record(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_re_replay", "no_pnl", "no_re_allocate", "no_optimization",
                 "no_reparameterization", "no_reactivation", "no_commit",
                 "no_push", "no_auto_trading", "no_paper_trading",
                 "no_live_trading", "no_xauusd"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rj18.__file__, encoding="utf-8").read()
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

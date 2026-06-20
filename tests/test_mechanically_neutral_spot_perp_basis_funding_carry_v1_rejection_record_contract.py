"""Tests for the Candidate #20 formal rejection / closeout record contract
(mechanically_neutral_spot_perp_basis_funding_carry_v1).

Verifies: research-only, rejection-record-only, executes nothing; chain-gated on the
frozen replay review carrying all-fail decisive gates + REJECT; records
REJECT_C20_AT_FEE_HONEST_REPLAY, not active / not parked / kept on record; anchored to the
pushed replay-review commit 59de8da7 and preserves the labels commit ead1bdb7; preserves
the verbatim conclusion + the positive carry lesson + the replay-failure facts (cannot be
flipped to a profitability claim); cites the 5 pushed gate commits; the ledger bump is
24 -> 25; does NOT start C21 or pivot to a new family; downstream gates locked; capability
flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_rejection_record_contract as rj20  # noqa: E501


_R = rj20.build_c20_rejection_record(".", [])


def test_record_research_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_rejection_record_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "REJECT_C20_AT_FEE_HONEST_REPLAY"
    assert rj20.validate_c20_rejection_record(_R)["valid"] is True


def test_candidate_identity_and_status():
    assert _R["candidate_id"] == "C20"
    assert _R["candidate_family"] == (
        "mechanically_neutral_spot_perp_basis_funding_carry")
    assert _R["rejection_status"] == (
        "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD")
    assert _R["rejected_at_stage"] == "fee_honest_replay"
    assert _R["is_active_candidate"] is False
    assert _R["parked_as_active"] is False
    assert _R["kept_on_record"] is True


def test_chain_gated_on_frozen_replay_review():
    assert _R["replay_review_valid"] is True
    assert _R["replay_review_verdict"] == "C20_REPLAY_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["replay_all_decisive_gates_pass"] is False
    assert _R["replay_recommended_decision"] == "REJECT"


def test_anchored_and_labels_commit_preserved():
    assert _R["anchored_to_replay_review_commit"] == (
        "59de8da7deb3cc25f951702bce63155235313052")
    assert _R["preserved_labels_commit"] == (
        "ead1bdb72ef5f9a78c1489f2a7701b5cd6e60c68")
    bad = {**_R, "anchored_to_replay_review_commit": "0" * 40}
    assert rj20.validate_c20_rejection_record(bad)["valid"] is False
    bad2 = {**_R, "preserved_labels_commit": "0" * 40}
    assert rj20.validate_c20_rejection_record(bad2)["valid"] is False


def test_five_pushed_gate_commits():
    chain = {e["stage"]: e["commit"] for e in _R["pushed_evidence_chain"]}
    for stage in ("family_proposal", "candidate_spec", "detector_spec_dry_run",
                  "real_candle_labels_review", "fee_honest_replay_review"):
        assert stage in chain
        assert len(chain[stage]) == 40


def test_ledger_bump_24_to_25():
    lb = _R["ledger_bump"]
    assert lb["from_count"] == 24
    assert lb["to_count"] == 25
    assert lb["add_family"] == "mechanically_neutral_spot_perp_basis_funding_carry"
    bad = {**_R, "ledger_bump": {**lb, "to_count": 24}}
    assert rj20.validate_c20_rejection_record(bad)["valid"] is False


def test_honest_failure_facts_preserved_and_cannot_be_flipped():
    eh = _R["evidence_headline"]
    assert eh["strategy_net_negative_after_cost"] is True
    assert eh["all_decisive_gates_failed"] is True
    assert eh["forward_oos_failed"] is True
    assert eh["loses_to_random_null_carry"] is True
    assert eh["cost_drag_dominates_funding"] is True
    assert eh["carry_thesis_real_null_positive"] is True
    assert _R["strategy_net_return"] == -0.7452
    assert _R["strategy_sharpe"] == -12.836936
    assert _R["random_null_net_return"] == 0.211648
    assert _R["random_null_sharpe"] == 1.087808
    # cannot flip the strategy to profitable / the null to non-positive
    bad = {**_R, "strategy_net_return": 0.5}
    assert rj20.validate_c20_rejection_record(bad)["valid"] is False
    bad2 = {**_R, "random_null_net_return": -0.1}
    assert rj20.validate_c20_rejection_record(bad2)["valid"] is False


def test_rejects_timing_not_carry_thesis_and_positive_lesson():
    assert _R["rejects_timing_not_carry_thesis"] is True
    assert _R["carry_thesis_vindicated_by_positive_null"] is True
    assert _R["low_turnover_carry_is_separate_future_candidate_only_with_approval"] is True
    assert "always-on" in _R["preserved_positive_lesson"].lower()
    assert "low-turnover" in _R["preserved_positive_lesson"].lower()
    assert "separate future candidate" in _R["preserved_positive_lesson"].lower()
    assert "explicit human" in _R["preserved_positive_lesson"].lower()
    # cannot drop the carry-thesis-real / timing-scope honesty
    bad = {**_R, "rejects_timing_not_carry_thesis": False}
    assert rj20.validate_c20_rejection_record(bad)["valid"] is False


def test_conclusion_verbatim():
    assert _R["conclusion"] == rj20.CONCLUSION
    bad = {**_R, "conclusion": "different"}
    assert rj20.validate_c20_rejection_record(bad)["valid"] is False


def test_no_c21_no_pivot_and_gates_locked():
    assert _R["does_not_start_c21"] is True
    assert _R["c21_candidate_id"] is None
    assert _R["does_not_pivot_to_new_family"] is True
    assert _R["next_required_action"].startswith("NONE__C20_CLOSED")
    for gate in ("labels_gate_locked", "replay_gate_locked", "robustness_gate_locked",
                 "promote_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert rj20.validate_c20_rejection_record(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rj20._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert rj20.validate_c20_rejection_record(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_replay", "no_re_replay", "no_change_fee", "no_drop_cost",
                 "no_optimization", "no_tuning", "no_rescue", "no_parameter_sweep",
                 "no_data_fetch", "no_data_commit", "no_xauusd",
                 "no_pivot_to_new_family", "no_paper_trading", "no_live_trading",
                 "no_start_c21"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rj20.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen"):
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

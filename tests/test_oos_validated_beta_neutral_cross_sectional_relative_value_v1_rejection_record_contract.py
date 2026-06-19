"""Tests for the Candidate #19 formal rejection / closeout record contract
(oos_validated_beta_neutral_cross_sectional_relative_value_v1).

Verifies: research-only, rejection-record-only, executes nothing; chain-gated on the
frozen labels review carrying the structural concern (sample gate not met AND OOS
neutrality not majority); records REJECT_C19_AT_REAL_CANDLE_LABELS, not active / not
parked / kept on record; anchored to the pushed labels-review commit c9470c08; confirms
NO fee-honest replay was run; preserves the verbatim conclusion + the labels/neutrality
failure facts (cannot be flipped); cites the 4 pushed gate commits; the ledger bump is
23 -> 24; does NOT start C20; downstream gates locked; capability flags + scope locks;
validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.oos_validated_beta_neutral_cross_sectional_relative_value_v1_rejection_record_contract as rj19  # noqa: E501


_R = rj19.build_c19_rejection_record(".", [])


def test_record_research_only_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_rejection_record_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "REJECT_C19_AT_REAL_CANDLE_LABELS"
    assert rj19.validate_c19_rejection_record(_R)["valid"] is True


def test_candidate_identity_and_status():
    assert _R["candidate_id"] == "C19"
    assert _R["candidate_family"] == (
        "oos_validated_beta_neutral_cross_sectional_relative_value")
    assert _R["rejection_status"] == (
        "REJECTED_AT_REAL_CANDLE_LABELS_NEUTRALITY_GATE_KEPT_ON_RECORD")
    assert _R["rejected_at_stage"] == "real_candle_labels_neutrality_gate"
    assert _R["is_active_candidate"] is False
    assert _R["parked_as_active"] is False
    assert _R["kept_on_record"] is True


def test_rejected_at_labels_no_replay_run():
    assert _R["no_fee_honest_replay_run"] is True
    assert _R["evidence_headline"]["no_replay_run"] is True
    bad = {**_R, "no_fee_honest_replay_run": False}
    assert rj19.validate_c19_rejection_record(bad)["valid"] is False


def test_chain_gated_on_frozen_labels_review():
    assert _R["labels_review_verdict"] == "C19_LABELS_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["labels_review_valid"] is True
    assert _R["labels_structural_concern"] is True
    assert _R["labels_meets_min_sample_gate"] is False
    assert _R["labels_neutrality_holds_majority"] is False


def test_anchored_to_pushed_labels_commit():
    assert _R["anchored_to_labels_review_commit"] == (
        "c9470c085555bbbb0928b178a86181a95a76088e")
    bad = {**_R, "anchored_to_labels_review_commit": "0" * 40}
    assert rj19.validate_c19_rejection_record(bad)["valid"] is False


def test_pushed_evidence_chain_four_gates():
    chain = {e["stage"]: e["commit"] for e in _R["pushed_evidence_chain"]}
    for stage in ("family_proposal", "candidate_spec", "detector_spec_dry_run",
                  "real_candle_labels_review"):
        assert stage in chain
        assert len(chain[stage]) == 40
    # rejected at labels -> there is NO fee_honest_replay gate in the chain
    assert "fee_honest_replay_review" not in chain


def test_honest_labels_neutrality_facts_preserved():
    eh = _R["evidence_headline"]
    assert eh["mechanics_clean"] is True
    assert eh["sample_gate_failed"] is True
    assert eh["oos_neutrality_did_not_persist"] is True
    assert eh["closed_by_neutrality_break"] is True
    assert eh["echoes_c16_neutrality_failure"] is True
    assert len(_R["rejection_reasons"]) >= 3
    assert _R["conclusion"] == rj19.CONCLUSION
    bad = {**_R, "evidence_headline": {**eh, "sample_gate_failed": False}}
    assert rj19.validate_c19_rejection_record(bad)["valid"] is False


def test_pinned_numbers_consistent_with_rejection():
    assert _R["entry_count"] == 41
    assert _R["min_entries_structural_gate"] == 100
    assert _R["entry_count"] < _R["min_entries_structural_gate"]
    assert _R["neutrality_pass_count"] == 862
    assert _R["neutrality_fail_count"] == 1115
    assert _R["neutrality_pass_count"] < _R["neutrality_fail_count"]
    assert _R["exit_neutrality_break"] == 15
    bad = {**_R, "entry_count": 500}
    assert rj19.validate_c19_rejection_record(bad)["valid"] is False


def test_ledger_bump_23_to_24():
    lb = _R["ledger_bump"]
    assert lb["from_count"] == 23
    assert lb["to_count"] == 24
    assert lb["add_family"] == (
        "oos_validated_beta_neutral_cross_sectional_relative_value")
    assert lb["applied_in_this_bundle"] is True


def test_next_action_closed_no_c20():
    nra = rj19.get_candidate_19_rejection_record_next_action()
    assert nra == _R["next_required_action"]
    assert nra.startswith("NONE__C19_CLOSED")
    assert _R["does_not_start_c20"] is True
    assert _R["c20_candidate_id"] is None
    label = rj19.get_candidate_19_rejection_record_label()
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())


def test_downstream_gates_locked():
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "robustness_gate_locked", "promote_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert rj19.validate_c19_rejection_record(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rj19._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert rj19.validate_c19_rejection_record(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_replay", "no_pnl", "no_re_detect", "no_optimization",
                 "no_tuning", "no_rescue", "no_data_fetch", "no_data_commit",
                 "no_xauusd", "no_reactivation", "no_commit", "no_push",
                 "no_auto_trading", "no_paper_trading", "no_live_trading",
                 "no_start_c20"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rj19.__file__, encoding="utf-8").read()
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

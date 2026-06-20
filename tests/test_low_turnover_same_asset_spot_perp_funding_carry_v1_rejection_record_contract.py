"""Tests for the Candidate #21 formal rejection / closeout record contract
(low_turnover_same_asset_spot_perp_funding_carry_v1).

Verifies: research-only, rejection-record-only, executes nothing; chain-gated on the
frozen C21 replay review carrying NOT-all-pass decisive gates + REJECT + does-not-beat-
null; records REJECT_C21_AT_FEE_HONEST_REPLAY / REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_
RECORD with the canonical reason code; the HONEST C21 shape is preserved (net-POSITIVE
+20.2% -- the low-turnover design worked -- but loses to the always-on null and the
forward-OOS fails, so it cannot be flipped to a profitability/edge/beats-null claim);
BOTH research lessons preserved (low-turnover fixes churn; carry timing adds no edge);
audit-clean (not a pipeline artifact); 4 pushed gate commits cited; ledger bump 25->26;
active candidate none / next = C22 proposal readiness only; NOT a C20 rescue; does not
start C22 or pivot; capability flags + scope locks; validator anti-tamper; module
purity."""
from __future__ import annotations

import ast

import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_rejection_record_contract as rj21  # noqa: E501


_R = rj21.build_c21_rejection_record(".", [])


def test_rejection_record_recorded_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_rejection_record_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "REJECT_C21_AT_FEE_HONEST_REPLAY"
    assert _R["rejection_status"] == "REJECTED_AT_FEE_HONEST_REPLAY_KEPT_ON_RECORD"
    assert _R["rejected_at_stage"] == "fee_honest_replay"
    assert _R["rejection_reason_code"] == (
        "EDGE_DOES_NOT_BEAT_ALWAYS_ON_NEUTRAL_CARRY_NULL_AND_FORWARD_OOS_FAILS")
    assert rj21.validate_c21_rejection_record(_R)["valid"] is True


def test_not_active_kept_on_record():
    assert _R["is_active_candidate"] is False
    assert _R["parked_as_active"] is False
    assert _R["kept_on_record"] is True
    assert _R["candidate_id"] == "C21"
    for bad_kv in (("is_active_candidate", True), ("parked_as_active", True),
                   ("kept_on_record", False)):
        bad = {**_R, bad_kv[0]: bad_kv[1]}
        assert rj21.validate_c21_rejection_record(bad)["valid"] is False, bad_kv[0]


def test_chain_gated_on_frozen_replay_review():
    assert _R["replay_review_verdict"] == "C21_REPLAY_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["replay_review_valid"] is True
    assert _R["replay_all_decisive_gates_pass"] is False
    assert _R["replay_recommended_decision"] == "REJECT"
    assert _R["replay_strategy_beats_null"] is False


def test_honest_c21_shape_net_positive_but_loses_to_null():
    # the low-turnover design WORKED -- net positive (unlike C20's -74.5%)
    assert _R["strategy_net_return"] == 0.202382
    assert _R["strategy_net_return"] > 0
    assert _R["low_turnover_design_worked"] is True
    # but it does NOT beat the always-on null and OOS fails
    assert _R["strategy_net_return"] < _R["random_null_net_return"]
    assert _R["strategy_sharpe"] < _R["random_null_sharpe"]
    assert _R["forward_oos_net_return"] < 0
    assert _R["random_null_net_return"] > 0   # carry source is real
    eh = _R["evidence_headline"]
    assert eh["low_turnover_preserved_carry_net_positive"] is True
    assert eh["does_not_beat_always_on_null"] is True
    assert eh["all_decisive_gates_passed"] is False
    assert eh["forward_oos_failed"] is True
    assert eh["not_a_pipeline_artifact"] is True


def test_cannot_be_flipped_to_profit_or_beats_null():
    # tamper: claim it beats the null net -> must fail
    bad = {**_R, "strategy_net_return": 0.30}
    assert rj21.validate_c21_rejection_record(bad)["valid"] is False
    # tamper: positive OOS -> must fail
    bad2 = {**_R, "forward_oos_net_return": 0.05}
    assert rj21.validate_c21_rejection_record(bad2)["valid"] is False
    # tamper: replay said it beats null -> must fail
    bad3 = {**_R, "replay_strategy_beats_null": True}
    assert rj21.validate_c21_rejection_record(bad3)["valid"] is False
    # tamper: evidence claims all gates passed -> must fail
    eh = {**_R["evidence_headline"], "all_decisive_gates_passed": True}
    bad4 = {**_R, "evidence_headline": eh}
    assert rj21.validate_c21_rejection_record(bad4)["valid"] is False


def test_both_lessons_preserved():
    lt = _R["preserved_lesson_low_turnover_fixes_churn"]
    ne = _R["preserved_lesson_no_timing_edge_over_null"]
    assert "LOW TURNOVER FIXES THE CHURN" in lt
    assert "NO EDGE" in ne
    assert _R["rejects_lack_of_edge_not_the_carry_source"] is True
    assert _R["carry_source_is_real_but_free_and_oos_fragile"] is True
    for bad_key in ("preserved_lesson_low_turnover_fixes_churn",
                    "preserved_lesson_no_timing_edge_over_null", "conclusion"):
        bad = {**_R, bad_key: "tampered"}
        assert rj21.validate_c21_rejection_record(bad)["valid"] is False, bad_key


def test_not_a_c20_rescue():
    assert _R["is_rescue_or_retune_of_c20"] is False
    assert _R["c20_remains_rejected"] is True
    assert _R["rescues_c20"] is False
    assert _R["retunes_rejected_candidate"] is False
    for bad_kv in (("is_rescue_or_retune_of_c20", True),
                   ("c20_remains_rejected", False)):
        bad = {**_R, bad_kv[0]: bad_kv[1]}
        assert rj21.validate_c21_rejection_record(bad)["valid"] is False, bad_kv[0]


def test_pushed_evidence_chain_four_commits():
    chain = {e["stage"]: e["commit"] for e in _R["pushed_evidence_chain"]}
    for stage in ("family_proposal", "candidate_spec", "detector_spec_dry_run",
                  "real_candle_labels_review"):
        assert stage in chain
        assert len(chain[stage]) == 40
    assert _R["preserved_labels_commit"] == (
        "668d06f20d6824cd62f07bc8b06f15f10576f46d")


def test_ledger_bump_25_to_26():
    lb = _R["ledger_bump"]
    assert lb["from_count"] == 25
    assert lb["to_count"] == 26
    assert lb["add_family"] == "low_turnover_same_asset_spot_perp_funding_carry"
    bad = {**_R, "ledger_bump": {**lb, "to_count": 25}}
    assert rj21.validate_c21_rejection_record(bad)["valid"] is False


def test_active_none_next_is_c22_proposal_readiness_only():
    assert _R["active_candidate_after_rejection"] is None
    assert _R["next_stage"] == "candidate_22_proposal_readiness"
    assert _R["c22_proposal_readiness_only_not_implementation"] is True
    assert _R["does_not_start_c22"] is True
    assert _R["c22_candidate_id"] is None
    nra = rj21.get_candidate_21_rejection_record_next_action()
    assert nra == _R["next_required_action"]
    assert "CANDIDATE_22_PROPOSAL_READINESS_ONLY" in nra
    for bad_kv in (("next_stage", "candidate_22_implementation"),
                   ("c22_proposal_readiness_only_not_implementation", False),
                   ("does_not_start_c22", False)):
        bad = {**_R, bad_kv[0]: bad_kv[1]}
        assert rj21.validate_c21_rejection_record(bad)["valid"] is False, bad_kv[0]


def test_gates_locked_and_capability_flags_false():
    for gate in ("labels_gate_locked", "replay_gate_locked", "robustness_gate_locked",
                 "promote_gate_locked", "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
    for flag in rj21._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert rj21.validate_c21_rejection_record(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_replay", "no_relabel", "no_optimization", "no_tuning",
                 "no_rescue", "no_rescue_c20", "no_data_fetch", "no_commit",
                 "no_push", "no_paper_trading", "no_live_trading", "no_start_c22"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rj21.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open(", "subprocess", "Popen"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "os", "io", "shutil",
              "ssl", "ftplib", "datetime", "random", "numpy", "pandas"}
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

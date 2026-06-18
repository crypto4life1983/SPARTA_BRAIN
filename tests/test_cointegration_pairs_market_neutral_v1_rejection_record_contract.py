"""Tests for the Candidate #16 formal rejection / closeout record contract
(cointegration_pairs_market_neutral_v1).

Verifies: research-only, rejection-record-only; chain-gated on the FROZEN
structural-rejection labels review; verdict REJECT_C16_AT_LABELS; rejected at the
labels stage with NO replay/PnL run; not active / not parked; the verbatim
conclusion; the preserved decisive facts (43 < 100, every pair < 20, chop < 20,
forward-OOS 9 populated-but-insufficient, net beta 2.82 > 0.10) -- none can be
flipped; the 4 pushed gate commits; the ledger bump deferred; gates locked;
anti-tamper; purity."""
from __future__ import annotations

import ast

import sparta_commander.cointegration_pairs_market_neutral_v1_rejection_record_contract as rj16  # noqa: E501


_R = rj16.build_c16_rejection_record(".", [])


# ---- verdict + status -------------------------------------------------------

def test_record_recorded_and_validates():
    assert _R["verdict"] == rj16.VERDICT_RJ16_RECORDED
    assert _R["verdict"] == "REJECT_C16_AT_LABELS"
    assert _R["blockers"] == []
    assert _R["rejection_status"] == "REJECTED_AT_LABELS_KEPT_ON_RECORD"
    assert _R["rejected_at_stage"] == "real_candle_labels"
    assert rj16.validate_c16_rejection_record(_R)["valid"] is True


def test_not_active_not_parked_no_replay():
    assert _R["is_active_candidate"] is False
    assert _R["parked_as_active"] is False
    assert _R["kept_on_record"] is True
    assert _R["no_replay_was_run"] is True
    assert _R["no_pnl_was_run"] is True
    assert _R["added_to_rejected_family_ledger"] is True
    for bad_key in ("is_active_candidate", "parked_as_active"):
        bad = {**_R, bad_key: True}
        assert rj16.validate_c16_rejection_record(bad)["valid"] is False, bad_key
    bad = {**_R, "no_replay_was_run": False}
    assert rj16.validate_c16_rejection_record(bad)["valid"] is False


# ---- chain gate on the structural-rejection labels review ------------------

def test_chain_gate_on_labels_structural_rejection():
    assert _R["labels_review_verdict"] == rj16.VERDICT_C16L_FROZEN
    assert _R["labels_structural_rejection_pressure"] is True
    assert _R["labels_structural_sample_size_passed"] is False
    assert _R["labels_net_beta_within_cap"] is False
    bad = {**_R, "labels_structural_rejection_pressure": False}
    assert rj16.validate_c16_rejection_record(bad)["valid"] is False
    bad2 = {**_R, "labels_net_beta_within_cap": True}
    assert rj16.validate_c16_rejection_record(bad2)["valid"] is False


# ---- verbatim conclusion + lesson ------------------------------------------

def test_verbatim_conclusion_and_lesson():
    assert _R["conclusion"] == (
        "Market-neutrality avoided the carry trap that rejected C14 and C15, but "
        "cointegration in crypto is too intermittent to generate enough valid "
        "pair-trade entries, and a level-OLS hedge ratio is not return-beta-neutral "
        "out of sample, so a market-neutral cointegration-pairs program is not "
        "structurally supportable on daily crypto.")
    lesson = " || ".join(_R["kept_on_record_as"]).lower()
    assert "market-neutrality avoided" in lesson
    assert "intermittent" in lesson
    assert "not return-beta-neutral" in lesson
    bad = {**_R, "conclusion": "edge confirmed"}
    assert rj16.validate_c16_rejection_record(bad)["valid"] is False


# ---- preserved decisive failure facts --------------------------------------

def test_decisive_failure_facts_preserved():
    eh = _R["evidence_headline"]
    assert eh["total_below_100"] is True
    assert eh["every_pair_below_20"] is True
    assert eh["chop_regime_below_20"] is True
    assert eh["forward_oos_populated_but_insufficient"] is True
    assert eh["net_beta_exceeds_cap"] is True
    assert eh["no_replay_or_pnl_run"] is True
    for bad_key in ("total_below_100", "every_pair_below_20",
                    "chop_regime_below_20", "net_beta_exceeds_cap"):
        bad = {**_R, "evidence_headline": {**eh, bad_key: False}}
        assert rj16.validate_c16_rejection_record(bad)["valid"] is False, bad_key


def test_pinned_numbers_intact():
    assert _R["accepted_label_count"] == 43
    assert _R["per_pair"] == {"ETHBTC": 17, "SOLBTC": 15, "SOLETH": 11}
    assert _R["per_regime"] == {"bear": 21, "bull": 18, "chop": 4}
    assert _R["forward_oos_label_count"] == 9
    assert _R["max_abs_net_beta_observed"] == 2.824495
    assert _R["max_abs_net_beta_cap"] == 0.10
    for bad_key, val in (("accepted_label_count", 200),
                         ("max_abs_net_beta_observed", 0.01),
                         ("forward_oos_label_count", 0)):
        bad = {**_R, bad_key: val}
        assert rj16.validate_c16_rejection_record(bad)["valid"] is False, bad_key


def test_rejection_reasons_preserved():
    joined = " || ".join(_R["rejection_reasons"]).lower()
    assert "insufficient sample size" in joined
    assert "net-beta failure" in joined
    assert "intermittent cointegration" in joined


# ---- pushed evidence chain --------------------------------------------------

def test_pushed_evidence_chain_cites_four_gates():
    chain = _R["pushed_evidence_chain"]
    stages = {e["stage"]: e for e in chain}
    for required, commit in (
            ("family_proposal", "38ccce6296e93b92dffcfa4a46d02349ebe40e76"),
            ("candidate_spec", "9c2b39cc64e156167d28621403e1b5892e2a308a"),
            ("detector_spec_and_synthetic_dry_run",
             "0c5f27a0e749f0842b99874b95d37f38f88a9887"),
            ("real_candle_labels_review",
             "ae16daf0a8c139cee1f6a1bb177ca99be027d198")):
        assert required in stages, required
        assert stages[required]["commit"] == commit, required
        assert len(stages[required]["commit"]) == 40


def test_ledger_bump_deferred_not_applied():
    pb = _R["proposed_ledger_bump"]
    assert pb["applied_here"] is False
    assert pb["add_family"] == "cointegration_pairs_market_neutral"
    assert pb["to_count"] == 21
    assert pb["requires_separate_token"] == "UPDATE_REJECTED_LEDGERS_ADD_C16"


# ---- gates locked + flags + claim locks + next action ----------------------

def test_all_gates_locked():
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "relabel_gate_locked", "portfolio_gate_locked",
                 "paper_trading_gate_locked", "micro_live_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rj16._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert rj16.validate_c16_rejection_record(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim",
                     "kept_on_record_not_active_candidate",
                     "not_parked_as_active", "no_replay_was_run",
                     "insufficient_sample_size_disclosed",
                     "net_beta_failure_disclosed",
                     "market_neutral_does_not_hold_disclosed",
                     "conclusion_recorded_precisely"):
        assert required in _R["claim_locks"], required
    label = rj16.get_candidate_16_rejection_record_label()
    assert "RESEARCH ONLY" in label
    assert "REJECTED_AT_LABELS_KEPT_ON_RECORD" in label
    assert "NOT AN ACTIVE CANDIDATE" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_next_action_is_closed_no_execution_token():
    nra = rj16.get_candidate_16_rejection_record_next_action()
    assert nra == _R["next_required_action"]
    assert nra.startswith("NONE__C16_CLOSED")
    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "PROMOTE", "UNLOCK", "REPLAY"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rj16.__file__, encoding="utf-8").read()
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

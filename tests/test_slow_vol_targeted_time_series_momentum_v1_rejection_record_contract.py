"""Tests for the Candidate #15 formal rejection / closeout record contract
(slow_vol_targeted_time_series_momentum_v1).

Verifies: research-only, rejection-record-only; chain-gated on the FROZEN
REJECT_C15 replay review; verdict RECORDED = REJECTED_KEPT_ON_RECORD; not active /
not parked; the verbatim conclusion; the preserved positives (net-positive, beats
random) AND the preserved decisive negatives (loses to buy-and-hold, bear regime
negative, short side negative) -- none can be flipped; pinned numbers; the 5
pushed gate commits; the ledger bump deferred; gates locked; anti-tamper; purity."""
from __future__ import annotations

import ast

import sparta_commander.slow_vol_targeted_time_series_momentum_v1_rejection_record_contract as rj15  # noqa: E501


_R = rj15.build_c15_rejection_record(".", [])


# ---- verdict + status -------------------------------------------------------

def test_record_recorded_and_validates():
    assert _R["verdict"] == rj15.VERDICT_RJ15_RECORDED
    assert _R["verdict"] == "C15_REJECTED_KEPT_ON_RECORD_FAILED_FEE_HONEST_REPLAY"
    assert _R["blockers"] == []
    assert _R["rejection_status"] == "REJECTED_KEPT_ON_RECORD"
    assert rj15.validate_c15_rejection_record(_R)["valid"] is True


def test_not_active_not_parked_kept_on_record():
    assert _R["is_active_candidate"] is False
    assert _R["parked_as_active"] is False
    assert _R["kept_on_record"] is True
    assert _R["original_frozen_c15_result_unchanged"] is True
    assert _R["added_to_rejected_family_ledger"] is True
    for bad_key in ("is_active_candidate", "parked_as_active"):
        bad = {**_R, bad_key: True}
        assert rj15.validate_c15_rejection_record(bad)["valid"] is False, bad_key


# ---- chain gate on the REJECT replay review --------------------------------

def test_chain_gate_on_replay_reject():
    assert _R["replay_review_verdict"] == rj15.VERDICT_C15RR_FROZEN
    assert _R["replay_decisive_outcome"] == "REJECT_C15"
    assert _R["replay_all_decisive_gates_pass"] is False
    assert _R["replay_beats_random_entry"] is True
    assert _R["replay_beats_buy_and_hold"] is False
    bad = {**_R, "replay_decisive_outcome": "ADVANCE_C15"}
    assert rj15.validate_c15_rejection_record(bad)["valid"] is False


# ---- verbatim conclusion + lesson ------------------------------------------

def test_verbatim_conclusion_and_lesson():
    assert _R["conclusion"] == (
        "A positive timing signal is not enough: slow vol-targeted time-series "
        "momentum on crypto-D1 is essentially long-bull carry that underperforms "
        "buy-and-hold, so beating random entry does not make it a durable "
        "tradeable edge.")
    lesson = " || ".join(_R["kept_on_record_as"]).lower()
    assert "long-bull carry" in lesson
    assert "buy-and-hold" in lesson
    assert "necessary but not sufficient" in lesson
    bad = {**_R, "conclusion": "edge confirmed"}
    assert rj15.validate_c15_rejection_record(bad)["valid"] is False


# ---- preserved positives ----------------------------------------------------

def test_key_positive_findings_preserved():
    joined = " || ".join(_R["key_positive_findings"]).lower()
    assert "net is positive after 37 bps" in joined
    assert "beats the random-entry baseline" in joined
    assert "all three assets individually net-positive" in joined
    eh = _R["evidence_headline"]
    assert eh["net_positive_full_sample"] is True
    assert eh["beats_random_entry"] is True
    assert eh["all_assets_positive"] is True
    # the beats-random positive cannot be cleared
    bad = {**_R, "replay_beats_random_entry": False}
    assert rj15.validate_c15_rejection_record(bad)["valid"] is False
    bad2 = {**_R, "evidence_headline": {**eh, "beats_random_entry": False}}
    assert rj15.validate_c15_rejection_record(bad2)["valid"] is False


# ---- preserved decisive rejection reasons ----------------------------------

def test_rejection_reasons_preserved():
    joined = " || ".join(_R["rejection_reasons"]).lower()
    assert "loses to matched buy-and-hold" in joined
    assert "bear regime net-negative" in joined
    assert "short side net-negative" in joined
    eh = _R["evidence_headline"]
    assert eh["loses_to_buy_and_hold"] is True
    assert eh["bear_regime_negative"] is True
    assert eh["short_side_negative"] is True
    for bad_key in ("loses_to_buy_and_hold", "bear_regime_negative",
                    "short_side_negative"):
        bad = {**_R, "evidence_headline": {**eh, bad_key: False}}
        assert rj15.validate_c15_rejection_record(bad)["valid"] is False, bad_key
    # flipping the buys-and-hold gate flag to "beats" is invalid
    bad2 = {**_R, "replay_beats_buy_and_hold": True}
    assert rj15.validate_c15_rejection_record(bad2)["valid"] is False


# ---- pinned numbers ---------------------------------------------------------

def test_pinned_numbers_intact():
    assert _R["net_r_total_all_in"] == 111.034046
    assert _R["forward_oos_net_r"] == 0.269899
    assert _R["per_asset_net_r"] == {"BTCUSD": 41.262908, "ETHUSD": 35.369613,
                                     "SOLUSD": 34.401525}
    assert _R["per_regime_net_r"]["bear"] == -0.914353
    assert _R["per_side_net_r"]["short"] == -1.15739
    assert _R["buy_and_hold_net_r_total"] == 286.528781
    assert _R["random_entry_mean_net_r"] == -4.309887
    assert _R["all_in_round_trip_bps"] == 37.0
    # tampering a sign is rejected
    bad = {**_R, "per_regime_net_r": {**_R["per_regime_net_r"], "bear": 5.0}}
    assert rj15.validate_c15_rejection_record(bad)["valid"] is False


# ---- pushed evidence chain --------------------------------------------------

def test_pushed_evidence_chain_cites_five_gates():
    chain = _R["pushed_evidence_chain"]
    stages = {e["stage"]: e for e in chain}
    for required, commit in (
            ("strategy_family_tournament_proposal",
             "703ef52ce7917319a11f0881218b560c5f34c2e9"),
            ("candidate_family_spec",
             "601c984d857e3d61700d2c98dd12b98872ce60cf"),
            ("detector_spec_and_synthetic_dry_run",
             "5399925b1cb60260b5ed750b6ce3b5765e584a0b"),
            ("real_candle_labels_review",
             "36df56a32c20bd8e7d50b482450d281ddf1b0e00"),
            ("fee_honest_replay_results_review",
             "aaaa3a693b4077b2da68af009a498b35f9672552")):
        assert required in stages, required
        assert stages[required]["commit"] == commit, required
        assert len(stages[required]["commit"]) == 40


def test_ledger_bump_deferred_not_applied():
    pb = _R["proposed_ledger_bump"]
    assert pb["applied_here"] is False
    assert pb["add_family"] == "slow_vol_targeted_time_series_momentum"
    assert pb["to_count"] == 20
    assert pb["requires_separate_token"] == "UPDATE_REJECTED_LEDGERS_ADD_C15"


# ---- gates locked + flags + claim locks + next action ----------------------

def test_all_gates_locked():
    for gate in ("robustness_gate_locked", "relabel_gate_locked",
                 "replay_gate_locked", "one_edit_gate_locked",
                 "portfolio_gate_locked", "paper_trading_gate_locked",
                 "micro_live_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
    for key, val in _R["scope_locks"].items():
        assert val is True, key


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in rj15._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert rj15.validate_c15_rejection_record(bad)["valid"] is False, flag


def test_claim_locks_and_label_no_readiness():
    for required in ("no_profitability_claim",
                     "kept_on_record_not_active_candidate",
                     "not_parked_as_active", "no_new_replay",
                     "beats_random_entry_positive_preserved",
                     "loses_to_buy_and_hold_disclosed",
                     "bear_regime_negative_disclosed",
                     "short_side_negative_disclosed",
                     "conclusion_recorded_precisely"):
        assert required in _R["claim_locks"], required
    label = rj15.get_candidate_15_rejection_record_label()
    assert "RESEARCH ONLY" in label
    assert "REJECTED_KEPT_ON_RECORD" in label
    assert "NOT AN ACTIVE CANDIDATE" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_next_action_is_closed_no_execution_token():
    nra = rj15.get_candidate_15_rejection_record_next_action()
    assert nra == _R["next_required_action"]
    assert nra.startswith("NONE__C15_CLOSED")
    for banned in ("APPROVE", "PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER",
                   "PROMOTE", "UNLOCK"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(rj15.__file__, encoding="utf-8").read()
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

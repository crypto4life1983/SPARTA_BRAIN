"""Tests for the Candidate #16 family-proposal contract
(cointegration_pairs_market_neutral_v1).

Verifies: research-only, pure-proposal-only; the next family is selected as
statistical_arbitrage_pairs via the tournament ranking (trend_following already
attempted as C15); the candidate is market-neutral, materially different from
C1-C15, NOT in the rejected ledger (20), and does not reuse C15; the proposal-level
declaration is complete; gate sequence preserved; downstream gates locked;
capability flags + scope locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.cointegration_pairs_market_neutral_v1_proposal_contract as c16  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as rep


_R = c16.build_c16_family_proposal(".", [])


# ---- core: research-only, pure, frozen, validates --------------------------

def test_proposal_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_pure_proposal_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C16_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"
    assert c16.validate_c16_family_proposal(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C16"
    assert _R["candidate_family"] == "cointegration_pairs_market_neutral"
    assert _R["candidate_name"] == "cointegration_pairs_market_neutral_v1"


# ---- selection via the automation stack ------------------------------------

def test_selected_statistical_arbitrage_pairs_via_tournament():
    sel = c16.select_next_family()
    assert sel["selected_tournament_family"] == "statistical_arbitrage_pairs"
    assert sel["tournament_rank"] == 2            # absolute rank (behind #1 C15)
    assert sel["tournament_score"] == 0.675
    assert "trend_following" in sel["already_attempted"]
    assert _R["tournament_family_key"] == "statistical_arbitrage_pairs"
    assert _R["tournament_proposal_valid"] is True


# ---- anti-loop: excluded, not reusing C15 ----------------------------------

def test_excluded_from_rejected_ledger_and_not_c15():
    assert _R["candidate_not_in_rejected_ledger"] is True
    assert _R["does_not_reuse_c15"] is True
    assert _R["candidate_family"] != "slow_vol_targeted_time_series_momentum"
    assert _R["candidate_family"] not in rep.REJECTED_FAMILIES_C1_TO_C15
    assert _R["rejected_families_count"] == 20
    assert "slow_vol_targeted_time_series_momentum" in _R["rejected_families_c1_to_c15"]


def test_validator_rejects_a_rejected_or_reused_family():
    bad = {**_R, "candidate_not_in_rejected_ledger": False}
    assert c16.validate_c16_family_proposal(bad)["valid"] is False
    bad2 = {**_R, "does_not_reuse_c15": False}
    assert c16.validate_c16_family_proposal(bad2)["valid"] is False


# ---- market-neutral + materially different (carry-trap avoidance) ----------

def test_market_neutral_and_materially_different():
    assert _R["is_market_neutral"] is True
    assert _R["is_directional"] is False
    md = " || ".join(_R["material_difference_from_c1_c15"]).lower()
    assert "market-neutral" in md
    assert "c11" in md
    assert "c15" in md
    assert "carry trap" in md
    bad = {**_R, "is_market_neutral": False}
    assert c16.validate_c16_family_proposal(bad)["valid"] is False
    bad2 = {**_R, "is_directional": True}
    assert c16.validate_c16_family_proposal(bad2)["valid"] is False


# ---- full proposal-level declaration ---------------------------------------

def test_proposal_declaration_complete():
    assert _R["symbols"] == ["ETH/BTC", "SOL/ETH", "SOL/BTC"]
    assert _R["timeframe"] == "D1"
    for field in ("core_idea", "entry_logic_sketch", "exit_logic_sketch",
                  "risk_logic_sketch", "expected_failure_mode", "why_selected"):
        assert _R[field]
    assert "cointegration" in _R["core_idea"].lower()


def test_gate_sequence_preserved():
    assert _R["gate_sequence"] == [
        "family_proposal", "candidate_spec", "detector_spec_dry_run",
        "real_candle_labels_review", "fee_honest_replay_review",
        "rejection_or_promote_decision"]
    assert _R["gate_sequence_preserved_unchanged"] is True


# ---- downstream gates locked + flags + scope locks -------------------------

def test_downstream_gates_locked():
    for gate in ("spec_gate_locked", "detector_gate_locked", "labels_gate_locked",
                 "replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert c16.validate_c16_family_proposal(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c16._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert c16.validate_c16_family_proposal(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_build", "no_detector", "no_labels", "no_replay",
                 "no_optimization", "no_commit", "no_push", "no_broker",
                 "no_paper_trading", "no_live_trading", "no_reuse_of_c15"):
        assert _R["scope_locks"][must] is True, must


def test_label_and_next_action_no_readiness():
    label = c16.get_candidate_16_proposal_label()
    assert "RESEARCH ONLY" in label
    assert "PROPOSAL ONLY" in label.upper() or "PURE PROPOSAL" in label.upper()
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE",
                   "APPROVED FOR PAPER", "APPROVED FOR LIVE"):
        assert banned not in label.upper(), banned
    nra = c16.get_candidate_16_proposal_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C16_ADVANCE_TO_CANDIDATE_SPEC_OR_REJECT"
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH",
                   "DETECTOR", "LABELS", "REPLAY"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c16.__file__, encoding="utf-8").read()
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

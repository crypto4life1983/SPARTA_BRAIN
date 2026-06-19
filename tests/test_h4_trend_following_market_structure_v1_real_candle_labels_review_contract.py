"""Tests for the Candidate #18 real-candle labels review contract
(h4_trend_following_market_structure_v1).

Verifies: research-only, labels-review-only, executes nothing; chain-gated on the
frozen C18 detector dry-run; uses FROZEN local BTCUSDT 4h data only and pins the exact
source + artifact SHAs; pins the real-candle structural aggregates and records the
HONEST structural verdict (PASS -- 389 long setups, all long-only, max 3 units,
non-overlapping, structural stops, >=6-bar spacing, forward-OOS populated); applies NO
fee/PnL and makes NO profitability claim; no XAUUSD; next gate is the fee-honest
replay decision; downstream gates locked; capability flags + scope locks; validator
anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.h4_trend_following_market_structure_v1_real_candle_labels_review_contract as l18  # noqa: E501


_R = l18.build_c18_labels_review(".", [])


def test_review_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_labels_review_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C18_LABELS_FROZEN_FOR_HUMAN_REVIEW"
    assert l18.validate_c18_labels_review(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C18"
    assert _R["candidate_family"] == "h4_trend_following_market_structure"


def test_chain_gated_on_frozen_detector_dry_run():
    assert _R["detector_dry_run_verdict"] == (
        "C18_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW")
    assert _R["detector_dry_run_valid"] is True
    bad = {**_R, "detector_dry_run_verdict": "C18_DETECTOR_DRY_RUN_BLOCKED"}
    assert l18.validate_c18_labels_review(bad)["valid"] is False


def test_frozen_local_data_and_pinned_shas():
    assert _R["uses_frozen_local_data_only"] is True
    assert _R["expected_source_sha256"] == (
        "aec42241f47192ae29331f4b67a64500ca38aad1f403f13d0de5b405f7ecbaec")
    assert len(_R["expected_labels_sha256"]) == 64
    assert len(_R["expected_summary_sha256"]) == 64
    assert _R["symbol"] == "BTCUSD"
    assert _R["timeframe"] == "4h"
    bad = {**_R, "expected_labels_sha256": "0" * 64}
    assert l18.validate_c18_labels_review(bad)["valid"] is False


def test_pinned_aggregates():
    assert _R["n_labels"] == 389
    assert _R["total_adds"] == 243
    assert _R["max_units"] == 3
    assert _R["exits_by_reason"] == {"stop": 330, "structure_shift": 59}
    assert _R["forward_oos_label_count"] == 23
    assert _R["n_candles"] == 16286
    assert _R["window"][0].startswith("2019-01-01")


def test_structural_pass_verdict_honest():
    sv = _R["structural_review"]
    assert sv["labels_ok"] is True
    assert sv["all_long_only"] is True
    assert sv["max_units_ok"] is True and sv["max_units"] <= 3
    assert sv["one_position_per_symbol"] is True
    assert sv["structural_stops_below_anchor"] is True
    assert sv["spacing_min_6_bars"] is True
    assert sv["forward_oos_populated"] is True
    assert sv["passed"] is True
    assert _R["structural_passed"] is True
    assert _R["structural_rejection_pressure"] is False
    assert _R["pass_reasons"]
    # the verdict must stay internally consistent
    bad = {**_R, "structural_passed": False}
    assert l18.validate_c18_labels_review(bad)["valid"] is False


def test_structural_invariant_tamper_rejected():
    sv = _R["structural_review"]
    for bad_key in ("all_long_only", "one_position_per_symbol",
                    "structural_stops_below_anchor", "spacing_min_6_bars",
                    "forward_oos_populated"):
        bad = {**_R, "structural_review": {**sv, bad_key: False},
               "structural_passed": False}
        assert l18.validate_c18_labels_review(bad)["valid"] is False, bad_key
    # max units above the cap is rejected
    bad = {**_R, "structural_review": {**sv, "max_units": 5, "max_units_ok": False},
           "structural_passed": False}
    assert l18.validate_c18_labels_review(bad)["valid"] is False


def test_no_fee_no_profitability_claim_next_is_replay():
    assert _R["fee_applied_here"] is False
    assert _R["cost_model_reserved_for_replay"] is True
    assert _R["not_yet_validated"]
    assert "risk-adjusted" in _R["not_yet_validated"].lower()
    nra = l18.get_candidate_18_labels_review_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C18_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"
    label = l18.get_candidate_18_labels_review_label()
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "BEATS BUY-AND-HOLD",
                   "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_downstream_gates_locked():
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert l18.validate_c18_labels_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in l18._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert l18.validate_c18_labels_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_re_detect", "no_relabel", "no_replay",
                 "no_pnl", "no_fee_application", "no_optimization", "no_xauusd",
                 "no_add_to_losers", "no_commit", "no_push", "no_paper_trading",
                 "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(l18.__file__, encoding="utf-8").read()
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

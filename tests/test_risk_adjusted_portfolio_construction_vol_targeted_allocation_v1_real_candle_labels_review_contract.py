"""Tests for the Candidate #17 real-candle labels review contract
(risk_adjusted_portfolio_construction_vol_targeted_allocation_v1).

Verifies: research-only, labels-review-only, executes nothing; chain-gated on the
frozen C17 detector dry-run; uses FROZEN local data only and pins the exact source +
artifact SHAs; pins the real-candle structural aggregates and records the HONEST
structural verdict (PASS -- well-formed, sufficiently sampled, long-only, gross-
capped, vol-targeted allocation with a populated forward-OOS window); applies NO
PnL/cost and makes NO profitability claim; the next gate is the fee-honest replay
decision; downstream gates locked; capability flags + scope locks; validator anti-
tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.risk_adjusted_portfolio_construction_vol_targeted_allocation_v1_real_candle_labels_review_contract as l17  # noqa: E501


_R = l17.build_c17_labels_review(".", [])


# ---- core: research-only, labels-review-only, frozen, validates ------------

def test_review_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_labels_review_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C17_LABELS_FROZEN_FOR_HUMAN_REVIEW"
    assert l17.validate_c17_labels_review(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C17"
    assert _R["candidate_family"] == (
        "risk_adjusted_portfolio_construction_vol_targeted_allocation")


# ---- chain gate on the frozen C17 detector dry-run -------------------------

def test_chain_gated_on_frozen_detector_dry_run():
    assert _R["detector_dry_run_verdict"] == (
        "C17_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW")
    assert _R["detector_dry_run_valid"] is True
    bad = {**_R, "detector_dry_run_verdict": "C17_DETECTOR_DRY_RUN_BLOCKED"}
    assert l17.validate_c17_labels_review(bad)["valid"] is False


# ---- frozen local data only + pinned SHAs ----------------------------------

def test_frozen_local_data_only_and_pinned_shas():
    assert _R["uses_frozen_local_data_only"] is True
    assert _R["expected_source_sha256"]["BTCUSD"] == (
        "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88")
    assert _R["expected_source_sha256"]["ETHUSD"] == (
        "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3")
    assert _R["expected_source_sha256"]["SOLUSD"] == (
        "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113")
    assert len(_R["expected_labels_sha256"]) == 64
    assert len(_R["expected_summary_sha256"]) == 64
    # tamper: changing a pinned SHA invalidates
    bad = {**_R, "expected_labels_sha256": "0" * 64}
    assert l17.validate_c17_labels_review(bad)["valid"] is False


# ---- pinned real-candle aggregates -----------------------------------------

def test_pinned_aggregates():
    assert _R["n_rebalances"] == 296
    assert _R["common_window"] == ["2020-08-11", "2026-06-08"]
    assert _R["n_common_candles"] == 2128
    assert _R["label_definition"] == (
        "weekly_rebalance_long_flat_allocation_observation")
    assert _R["per_regime"] == {"bear": 105, "bull": 153, "chop": 38}
    assert _R["forward_oos_rebalance_count"] == 23


# ---- HONEST structural PASS verdict ----------------------------------------

def test_structural_pass_verdict_honest():
    sv = _R["structural_review"]
    assert sv["rebalances_ok"] is True
    assert sv["all_weights_long_only"] is True
    assert sv["gross_never_exceeds_cap"] is True
    assert sv["max_gross_exposure"] <= 1.0
    assert sv["vol_target_active"] is True
    assert sv["forward_oos_populated"] is True
    assert sv["turnover_within_cap"] is True
    assert sv["avg_weekly_turnover"] <= 0.20
    assert sv["passed"] is True
    assert _R["structural_passed"] is True
    assert _R["structural_rejection_pressure"] is False
    assert _R["pass_reasons"]
    # the verdict must stay internally consistent: a tampered "passed" with the
    # structural rules still True is rejected
    bad = {**_R, "structural_passed": False}
    assert l17.validate_c17_labels_review(bad)["valid"] is False


def test_gross_cap_and_long_only_tamper_rejected():
    sv = _R["structural_review"]
    for bad_key in ("all_weights_long_only", "gross_never_exceeds_cap",
                    "vol_target_active", "forward_oos_populated"):
        bad = {**_R, "structural_review": {**sv, bad_key: False},
               "structural_passed": False}
        assert l17.validate_c17_labels_review(bad)["valid"] is False, bad_key
    # turnover above the cap is rejected
    bad = {**_R, "structural_review": {**sv, "avg_weekly_turnover": 0.9}}
    assert l17.validate_c17_labels_review(bad)["valid"] is False


# ---- no PnL / cost / profitability claim; next gate = replay ---------------

def test_no_pnl_no_profitability_claim_next_is_replay():
    assert _R["cost_model_applied_here"] is False
    assert _R["cost_model_reserved_for_replay"] is True
    assert _R["not_yet_validated"]
    assert "risk-adjusted" in _R["not_yet_validated"].lower()
    nra = l17.get_candidate_17_labels_review_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C17_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"
    label = l17.get_candidate_17_labels_review_label()
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "BEATS BUY-AND-HOLD",
                   "READY FOR LIVE"):
        assert banned not in label.upper(), banned


# ---- downstream gates locked + flags + scope locks -------------------------

def test_downstream_gates_locked():
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "portfolio_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert l17.validate_c17_labels_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in l17._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert l17.validate_c17_labels_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_re_detect", "no_relabel", "no_replay",
                 "no_backtest", "no_pnl", "no_cost_application", "no_baseline",
                 "no_optimization", "no_shorting", "no_leverage_above_cap",
                 "no_commit", "no_push", "no_auto_trading", "no_paper_trading",
                 "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(l17.__file__, encoding="utf-8").read()
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

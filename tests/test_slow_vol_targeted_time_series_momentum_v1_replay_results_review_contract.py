"""Tests for the Candidate #15 fee-honest replay results review contract
(slow_vol_targeted_time_series_momentum_v1).

Verifies: research-only, replay-review-only; chain-gated on the frozen labels
review; SHA pins; the FROZEN aggregates; the HONEST REJECT_C15 outcome (net-
positive + beats random, but loses to buy-and-hold, short side and bear regime
net-negative -> 3/8 gates fail); the pure gate evaluator on honest PASS and honest
REJECT fixtures; costs cannot be dropped or reduced; forward-OOS failure rejects;
baseline failure rejects; no gate can pass from gross-only results; anti-tamper;
artifacts untracked; module purity. Deterministic."""
from __future__ import annotations

import ast
import subprocess

import sparta_commander.slow_vol_targeted_time_series_momentum_v1_replay_results_review_contract as r15  # noqa: E501


_R = r15.build_c15_replay_review(".", [])


def _tracked_paths():
    return subprocess.check_output(["git", "ls-files"]).decode("utf-8").splitlines()


def _passing_metrics():
    """Synthetic metrics where EVERY decisive gate passes (honest PASS case)."""
    return {
        "net_r_total_all_in": 120.0,
        "forward_oos_net_r": 8.0,
        "per_asset_net_r": {"BTCUSD": 40.0, "ETHUSD": 40.0, "SOLUSD": 40.0},
        "per_regime_net_r": {"bull": 50.0, "bear": 30.0, "chop": 40.0},
        "per_side_net_r": {"long": 70.0, "short": 50.0},
        "buy_and_hold_net_r_total": 100.0,   # strategy 120 > 100
        "random_entry_mean_net_r": -3.0,
        "avg_hold_bars": 20.0,
    }


# ---- core: frozen + validates + honest REJECT ------------------------------

def test_replay_review_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_replay_review_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == r15.VERDICT_C15RR_FROZEN
    assert r15.validate_c15_replay_review(_R)["valid"] is True


def test_honest_reject_outcome():
    assert _R["decisive_outcome"] == "REJECT_C15"
    assert _R["all_decisive_gates_pass"] is False
    assert _R["advance_recommended"] is False
    assert _R["structural_rejection_pressure"] is True


def test_chain_gated_on_frozen_labels_review():
    assert _R["labels_review_valid"] is True
    assert _R["labels_review_verdict"] == "C15_LABELS_FROZEN_FOR_HUMAN_REVIEW"


# ---- SHA pins + cost model --------------------------------------------------

def test_sha_pins_frozen():
    assert _R["expected_ledger_sha256"] == r15.EXPECTED_LEDGER_SHA256
    assert _R["expected_summary_sha256"] == r15.EXPECTED_SUMMARY_SHA256
    assert _R["expected_labels_sha256"] == r15.EXPECTED_LABELS_SHA256
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert _R["expected_source_sha256"][s] == r15.EXPECTED_SOURCE_SHA256[s]
    bad = {**_R, "expected_ledger_sha256": "0" * 64}
    assert r15.validate_c15_replay_review(bad)["valid"] is False


def test_cost_model_cannot_be_dropped_or_reduced():
    assert _R["all_in_round_trip_bps"] == 37.0
    assert _R["fee_round_trip_bps"] + _R["slippage_round_trip_bps"] == 37.0
    assert _R["drops_cost_model"] is False
    assert _R["scope_locks"]["no_cost_drop"] is True
    for val in (0.0, 5.0, 36.9):
        bad = {**_R, "all_in_round_trip_bps": val}
        assert r15.validate_c15_replay_review(bad)["valid"] is False, val


# ---- frozen aggregates ------------------------------------------------------

def test_frozen_aggregates():
    assert _R["trade_count"] == 200
    assert _R["net_r_total_all_in"] == 111.034046
    assert _R["per_asset_net_r"] == {"BTCUSD": 41.262908, "ETHUSD": 35.369613,
                                     "SOLUSD": 34.401525}
    assert _R["per_regime_net_r"]["bear"] < 0
    assert _R["per_side_net_r"]["short"] < 0
    assert _R["buy_and_hold_net_r_total"] == 286.528781
    assert _R["random_entry_mean_net_r"] == -4.309887
    assert _R["random_entry_percentile_of_strategy"] == 1.0


# ---- the pure gate evaluator: honest PASS ----------------------------------

def test_gate_evaluator_honest_pass():
    d = r15.evaluate_decision_gates(_passing_metrics())
    assert d["all_pass"] is True
    assert d["decisive_outcome"] == "ADVANCE_C15"
    assert all(d["gates"].values())


# ---- the pure gate evaluator: honest REJECT variants -----------------------

def test_gate_evaluator_forward_oos_failure_rejects():
    m = _passing_metrics()
    m["forward_oos_net_r"] = -0.01      # forward-OOS negative
    d = r15.evaluate_decision_gates(m)
    assert d["gates"]["forward_oos_net_positive"] is False
    assert d["all_pass"] is False
    assert d["decisive_outcome"] == "REJECT_C15"


def test_gate_evaluator_buy_and_hold_failure_rejects():
    m = _passing_metrics()
    m["buy_and_hold_net_r_total"] = 999.0   # cannot beat buy-and-hold
    d = r15.evaluate_decision_gates(m)
    assert d["gates"]["beats_buy_and_hold"] is False
    assert d["all_pass"] is False


def test_gate_evaluator_random_failure_rejects():
    m = _passing_metrics()
    m["random_entry_mean_net_r"] = 999.0    # cannot beat random
    d = r15.evaluate_decision_gates(m)
    assert d["gates"]["beats_random_entry"] is False
    assert d["all_pass"] is False


def test_gate_evaluator_regime_and_side_dependence_reject():
    m = _passing_metrics()
    m["per_regime_net_r"] = {"bull": 80.0, "bear": -1.0, "chop": 40.0}
    assert r15.evaluate_decision_gates(m)["all_pass"] is False
    m2 = _passing_metrics()
    m2["per_side_net_r"] = {"long": 120.0, "short": -1.0}
    assert r15.evaluate_decision_gates(m2)["all_pass"] is False
    m3 = _passing_metrics()
    m3["per_asset_net_r"] = {"BTCUSD": 120.0, "ETHUSD": -1.0, "SOLUSD": 1.0}
    assert r15.evaluate_decision_gates(m3)["all_pass"] is False


def test_no_gate_passes_from_gross_only_results():
    # gross is positive but NET is non-positive -> must REJECT (cost not droppable)
    m = _passing_metrics()
    m["net_r_total_all_in"] = -2.0       # net negative after costs
    d = r15.evaluate_decision_gates(m)
    assert d["gates"]["full_sample_net_positive"] is False
    assert d["all_pass"] is False
    # the actual frozen record: gross is positive yet the outcome is REJECT
    assert _R["gross_r_total_pre_cost"] > 0
    assert _R["gross_only_would_pass_diagnostic"] is True
    assert _R["decisive_outcome"] == "REJECT_C15"
    assert _R["gate_uses_net_not_gross"] is True


# ---- anti-tamper: cannot flip negatives or clear the positive --------------

def test_cannot_flip_negatives_or_force_advance():
    # forcing all-pass / advance while gates fail -> invalid
    bad = {**_R, "all_decisive_gates_pass": True}
    assert r15.validate_c15_replay_review(bad)["valid"] is False
    bad2 = {**_R, "decisive_outcome": "ADVANCE_C15"}
    assert r15.validate_c15_replay_review(bad2)["valid"] is False
    bad3 = {**_R, "advance_recommended": True}
    assert r15.validate_c15_replay_review(bad3)["valid"] is False
    # flipping a pinned negative aggregate desyncs the gates -> invalid
    bad4 = {**_R, "buy_and_hold_net_r_total": 1.0}
    assert r15.validate_c15_replay_review(bad4)["valid"] is False


def test_beats_random_positive_must_remain_disclosed():
    g = dict(_R["decisive_gate_results"])
    g["beats_random_entry"] = False
    bad = {**_R, "decisive_gate_results": g}
    assert r15.validate_c15_replay_review(bad)["valid"] is False


def test_positives_and_rejection_reasons_preserved():
    pos = " || ".join(_R["notable_positives"]).lower()
    assert "beats the random-entry baseline" in pos
    assert "net is positive" in pos
    rej = " || ".join(_R["rejection_reasons"]).lower()
    assert "loses to matched buy-and-hold" in rej
    assert "short side is net-negative" in rej
    assert "bear regime is net-negative" in rej
    caveats = " || ".join(_R["honest_caveats"]).lower()
    assert "carry signature" in caveats
    for required in ("carry_signature_disclosed", "cost_model_not_droppable",
                     "gates_use_net_not_gross", "loses_to_buy_and_hold_disclosed"):
        assert required in _R["claim_locks"], required


# ---- downstream gates locked + flags + scope locks + label -----------------

def test_downstream_gates_locked():
    for gate in ("robustness_gate_locked", "relabel_gate_locked",
                 "portfolio_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert r15.validate_c15_replay_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in r15._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert r15.validate_c15_replay_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_relabel", "no_re_replay",
                 "no_parameter_optimization", "no_robustness",
                 "no_portfolio_compute", "no_cost_drop", "no_gross_only_pass",
                 "no_commit", "no_push", "no_broker", "no_paper_trading",
                 "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_label_and_next_action_no_readiness():
    label = r15.get_candidate_15_replay_review_label()
    assert "RESEARCH ONLY" in label
    assert "NOT A PROFITABILITY CLAIM" in label.upper()
    assert "REJECT_C15" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned
    nra = r15.get_candidate_15_replay_review_next_action()
    assert nra == _R["next_required_action"]
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH"):
        assert banned not in nra.upper(), banned


# ---- artifacts remain untracked --------------------------------------------

def test_replay_artifacts_remain_untracked():
    tracked = _tracked_paths()
    assert r15.LEDGER_PATH not in tracked
    assert r15.SUMMARY_PATH not in tracked
    for p in tracked:
        assert not p.startswith(
            "data/slow_vol_targeted_time_series_momentum_c15/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(r15.__file__, encoding="utf-8").read()
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

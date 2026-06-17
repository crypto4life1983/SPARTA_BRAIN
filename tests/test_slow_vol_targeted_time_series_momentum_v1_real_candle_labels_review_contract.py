"""Tests for the Candidate #15 real-candle labels review contract
(slow_vol_targeted_time_series_momentum_v1).

Verifies: research-only, labels-review-only, executes nothing; chain-gated on the
frozen C15 detector dry-run; the SHA pins of the labels + summary + 3 sources; the
frozen aggregates (200 labels; per-asset / per-regime / per-side); the structural
sample-size gate PASSES with no rejection pressure; the long/short split is
balanced; no PnL / cost applied; downstream gates locked; capability flags + scope
locks; validator anti-tamper; the artifacts stay untracked; module purity."""
from __future__ import annotations

import ast
import subprocess

import sparta_commander.slow_vol_targeted_time_series_momentum_v1_real_candle_labels_review_contract as l15  # noqa: E501


_R = l15.build_c15_labels_review(".", [])


def _tracked_paths():
    return subprocess.check_output(["git", "ls-files"]).decode("utf-8").splitlines()


# ---- core: frozen + validates ----------------------------------------------

def test_labels_review_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_labels_review_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == l15.VERDICT_C15L_FROZEN
    assert _R["verdict"] == "C15_LABELS_FROZEN_FOR_HUMAN_REVIEW"
    assert l15.validate_c15_labels_review(_R)["valid"] is True


def test_chain_gated_on_frozen_detector_dry_run():
    assert _R["detector_dry_run_valid"] is True
    assert _R["detector_dry_run_verdict"] == (
        "C15_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW")


# ---- SHA pins ---------------------------------------------------------------

def test_sha_pins_frozen():
    assert _R["expected_labels_sha256"] == l15.EXPECTED_LABELS_SHA256
    assert _R["expected_summary_sha256"] == l15.EXPECTED_SUMMARY_SHA256
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert _R["expected_source_sha256"][s] == l15.EXPECTED_SOURCE_SHA256[s]
    assert _R["head_at_detector_dry_run"] == (
        "5399925b1cb60260b5ed750b6ce3b5765e584a0b")
    bad = {**_R, "expected_labels_sha256": "0" * 64}
    assert l15.validate_c15_labels_review(bad)["valid"] is False


# ---- frozen aggregates ------------------------------------------------------

def test_frozen_aggregates():
    assert _R["accepted_label_count"] == 200
    assert _R["per_asset"] == {"BTCUSD": 77, "ETHUSD": 59, "SOLUSD": 64}
    assert _R["per_regime"] == {"bear": 66, "bull": 74, "chop": 60}
    assert _R["per_side"] == {"long": 97, "short": 103}
    assert _R["forward_oos_label_count"] == 5
    assert _R["label_definition"] == (
        "state_transition_into_active_position_entry_event")
    for bad_key, val in (("accepted_label_count", 5),
                         ("per_asset", {"BTCUSD": 1}),
                         ("per_side", {"long": 1, "short": 1})):
        bad = {**_R, bad_key: val}
        assert l15.validate_c15_labels_review(bad)["valid"] is False, bad_key


# ---- structural sample-size verdict PASSES ---------------------------------

def test_structural_gate_passes():
    sv = _R["structural_sample_size"]
    assert sv["passed"] is True
    assert sv["total_ok"] is True
    assert sv["per_asset_ok"] is True
    assert sv["per_regime_ok"] is True
    assert sv["forward_oos_populated"] is True
    assert _R["structural_sample_size_passed"] is True
    assert _R["structural_rejection_pressure"] is False
    bad = {**_R, "structural_rejection_pressure": True}
    assert l15.validate_c15_labels_review(bad)["valid"] is False


def test_long_short_balanced():
    assert _R["long_short_balanced"] is True
    # near-50/50 split confirms the symmetric design
    assert abs(_R["per_side"]["long"] - _R["per_side"]["short"]) < 20


# ---- no PnL / cost applied --------------------------------------------------

def test_no_pnl_or_cost_applied():
    assert _R["cost_model_applied_here"] is False
    assert _R["cost_model_reserved_for_replay"] is True
    assert _R["computes_pnl"] is False
    assert _R["applies_cost_model"] is False
    assert _R["runs_replay"] is False


# ---- downstream gates locked + flags + scope locks -------------------------

def test_downstream_gates_locked():
    for gate in ("replay_gate_locked", "robustness_gate_locked",
                 "portfolio_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert l15.validate_c15_labels_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in l15._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert l15.validate_c15_labels_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_relabel", "no_replay", "no_pnl",
                 "no_cost_application", "no_baseline", "no_commit", "no_push",
                 "no_broker", "no_paper_trading", "no_live_trading",
                 "no_parameter_fitting"):
        assert _R["scope_locks"][must] is True, must


def test_label_and_next_action_no_readiness():
    label = l15.get_candidate_15_labels_review_label()
    assert "RESEARCH ONLY" in label
    assert "NOT a profitability claim" in label or "NOT A PROFITABILITY" in label.upper()
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned
    nra = l15.get_candidate_15_labels_review_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C15_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"


# ---- artifacts remain untracked --------------------------------------------

def test_label_artifacts_remain_untracked():
    tracked = _tracked_paths()
    assert l15.LABELS_PATH not in tracked
    assert l15.SUMMARY_PATH not in tracked
    for p in tracked:
        assert not p.startswith(
            "data/slow_vol_targeted_time_series_momentum_c15/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(l15.__file__, encoding="utf-8").read()
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

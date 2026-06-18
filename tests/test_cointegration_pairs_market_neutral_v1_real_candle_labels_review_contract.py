"""Tests for the Candidate #16 real-candle labels review contract
(cointegration_pairs_market_neutral_v1).

Verifies: research-only, labels-review-only; chain-gated on the frozen C16 detector
dry-run; SHA pins; the FROZEN aggregates (43 labels; per-pair / per-regime;
forward-OOS 9; net beta 2.82); the HONEST labels-stage STRUCTURAL REJECTION
(sample-size failed AND net-beta cap exceeded -> cannot be flipped to passed); the
3 rejection reasons; no PnL/cost; downstream gates locked; artifacts untracked;
anti-tamper; module purity. Deterministic."""
from __future__ import annotations

import ast
import subprocess

import sparta_commander.cointegration_pairs_market_neutral_v1_real_candle_labels_review_contract as l16  # noqa: E501


_R = l16.build_c16_labels_review(".", [])


def _tracked_paths():
    return subprocess.check_output(["git", "ls-files"]).decode("utf-8").splitlines()


# ---- core: frozen + validates ----------------------------------------------

def test_labels_review_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_labels_review_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == l16.VERDICT_C16L_FROZEN
    assert l16.validate_c16_labels_review(_R)["valid"] is True


def test_chain_gated_on_frozen_detector_dry_run():
    assert _R["detector_dry_run_valid"] is True
    assert _R["detector_dry_run_verdict"] == (
        "C16_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW")


# ---- SHA pins ---------------------------------------------------------------

def test_sha_pins_frozen():
    assert _R["expected_labels_sha256"] == l16.EXPECTED_LABELS_SHA256
    assert _R["expected_summary_sha256"] == l16.EXPECTED_SUMMARY_SHA256
    for s in ("BTCUSD", "ETHUSD", "SOLUSD"):
        assert _R["expected_source_sha256"][s] == l16.EXPECTED_SOURCE_SHA256[s]
    assert _R["head_at_detector_dry_run"] == (
        "0c5f27a0e749f0842b99874b95d37f38f88a9887")
    bad = {**_R, "expected_labels_sha256": "0" * 64}
    assert l16.validate_c16_labels_review(bad)["valid"] is False


# ---- frozen aggregates ------------------------------------------------------

def test_frozen_aggregates():
    assert _R["accepted_label_count"] == 43
    assert _R["per_pair"] == {"ETHBTC": 17, "SOLBTC": 15, "SOLETH": 11}
    assert _R["per_regime"] == {"bear": 21, "bull": 18, "chop": 4}
    assert _R["forward_oos_label_count"] == 9
    assert _R["max_abs_net_beta_observed"] == 2.824495
    assert _R["pair_universe"] == ["ETHBTC", "SOLETH", "SOLBTC"]
    for bad_key, val in (("accepted_label_count", 200),
                         ("per_pair", {"ETHBTC": 50, "SOLBTC": 50, "SOLETH": 50}),
                         ("max_abs_net_beta_observed", 0.01)):
        bad = {**_R, bad_key: val}
        assert l16.validate_c16_labels_review(bad)["valid"] is False, bad_key


# ---- honest STRUCTURAL REJECTION -------------------------------------------

def test_structural_rejection_recorded_honestly():
    sv = _R["structural_sample_size"]
    assert sv["passed"] is False
    assert sv["total_ok"] is False           # 43 < 100
    assert sv["per_pair_ok"] is False        # all pairs < 20
    assert sv["per_regime_ok"] is False      # chop < 20
    assert sv["forward_oos_populated"] is True   # 9 > 0
    assert sv["net_beta_within_cap"] is False    # 2.82 > 0.10
    assert _R["structural_sample_size_passed"] is False
    assert _R["structural_rejection_pressure"] is True
    assert _R["net_beta_within_cap"] is False


def test_structural_failure_cannot_be_flipped_to_pass():
    bad = {**_R, "structural_rejection_pressure": False}
    assert l16.validate_c16_labels_review(bad)["valid"] is False
    bad2 = {**_R, "structural_sample_size_passed": True}
    assert l16.validate_c16_labels_review(bad2)["valid"] is False
    bad3 = {**_R, "net_beta_within_cap": True}
    assert l16.validate_c16_labels_review(bad3)["valid"] is False
    sv = dict(_R["structural_sample_size"])
    sv["passed"] = True
    bad4 = {**_R, "structural_sample_size": sv}
    assert l16.validate_c16_labels_review(bad4)["valid"] is False


def test_rejection_reasons_preserved():
    joined = " || ".join(_R["rejection_reasons"]).lower()
    assert "insufficient sample size" in joined
    assert "market-neutral construction fails" in joined
    assert "net beta" in joined
    assert "cointegration in crypto is intermittent" in joined


# ---- no PnL / cost ----------------------------------------------------------

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
        assert l16.validate_c16_labels_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in l16._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert l16.validate_c16_labels_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_relabel", "no_replay", "no_pnl",
                 "no_cost_application", "no_baseline", "no_commit", "no_push",
                 "no_broker", "no_paper_trading", "no_live_trading",
                 "no_market_neutral_claim"):
        assert _R["scope_locks"][must] is True, must


def test_label_and_next_action_no_readiness():
    label = l16.get_candidate_16_labels_review_label()
    assert "RESEARCH ONLY" in label
    assert "REJECTED" in label.upper()
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned
    nra = l16.get_candidate_16_labels_review_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C16_REJECT_AT_LABELS_OR_REVIEW"
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH"):
        assert banned not in nra.upper(), banned


# ---- artifacts remain untracked --------------------------------------------

def test_label_artifacts_remain_untracked():
    tracked = _tracked_paths()
    assert l16.LABELS_PATH not in tracked
    assert l16.SUMMARY_PATH not in tracked
    for p in tracked:
        assert not p.startswith(
            "data/cointegration_pairs_market_neutral_c16/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(l16.__file__, encoding="utf-8").read()
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

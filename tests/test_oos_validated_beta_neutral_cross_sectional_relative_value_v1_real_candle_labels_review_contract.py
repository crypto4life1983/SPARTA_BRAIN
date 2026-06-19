"""Tests for the Candidate #19 real-candle labels review contract
(oos_validated_beta_neutral_cross_sectional_relative_value_v1).

Verifies: research-only, labels-review-only, executes nothing; chain-gated on the
frozen C19 detector dry-run; uses ONLY the frozen cached BTC/ETH/SOL D1 data (no fetch,
SHA-pinned source + gitignored artifacts not committed); honours the exact return-space
market-neutral params; pins the honest frozen aggregates (2128 candles, 41 entries,
862/1115 neutrality pass/fail) and a structural verdict that is mechanics-clean but
carries the honest sample-size + OOS-neutrality concern (the C16 echo) -- it cannot be
flipped to clear the >=100 sample gate while entry_count is 41; reserves the 37 bps (no
fee applied); downstream gates locked; does NOT start C20; capability flags + scope
locks; validator anti-tamper; module purity."""
from __future__ import annotations

import ast

import sparta_commander.oos_validated_beta_neutral_cross_sectional_relative_value_v1_real_candle_labels_review_contract as l19  # noqa: E501


_R = l19.build_c19_labels_review(".", [])


def test_labels_review_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_labels_review_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C19_LABELS_FROZEN_FOR_HUMAN_REVIEW"
    assert l19.validate_c19_labels_review(_R)["valid"] is True


def test_candidate_identity_and_chain_gate():
    assert _R["candidate_id"] == "C19"
    assert _R["candidate_family"] == (
        "oos_validated_beta_neutral_cross_sectional_relative_value")
    assert _R["detector_dry_run_valid"] is True
    assert _R["detector_dry_run_verdict"] == (
        "C19_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW")


def test_frozen_cached_data_no_fetch_sha_pinned():
    assert _R["uses_frozen_cached_data_only"] is True
    assert _R["no_new_data_fetch"] is True
    assert _R["uses_xauusd"] is False
    assert _R["common_window"] == ["2020-08-11", "2026-06-08"]
    assert _R["n_common_candles"] == 2128
    src = _R["expected_source_sha256"]
    assert src["BTCUSD"] == (
        "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88")
    assert src["ETHUSD"] == (
        "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3")
    assert src["SOLUSD"] == (
        "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113")
    bad = {**_R, "expected_source_sha256": {**src, "BTCUSD": "0" * 64}}
    assert l19.validate_c19_labels_review(bad)["valid"] is False


def test_artifacts_gitignored_not_committed():
    assert _R["artifacts_gitignored_not_committed"] is True
    assert _R["labels_path"].startswith("data/")
    assert _R["summary_path"].startswith("data/")
    assert len(_R["expected_labels_sha256"]) == 64
    assert len(_R["expected_summary_sha256"]) == 64
    bad = {**_R, "artifacts_gitignored_not_committed": False}
    assert l19.validate_c19_labels_review(bad)["valid"] is False


def test_exact_params_honoured():
    assert _R["beta_estimation_window_bars"] == 90
    assert _R["oos_neutrality_window_bars"] == 60
    assert _R["net_residual_beta_tolerance"] == 0.10
    assert _R["residual_zscore_window_bars"] == 60
    assert _R["entry_zscore_threshold"] == 2.0
    assert _R["max_gross_exposure"] == 1.0
    assert _R["min_bars_between_rebalances"] == 5
    assert _R["uses_price_level_hedge"] is False
    assert _R["oos_neutrality_is_gate_zero"] is True


def test_labels_count_summary():
    sv = _R["structural_verdict"]
    assert sv["n_eval_bars"] == 1977
    assert sv["neutrality_pass_count"] == 862
    assert sv["neutrality_fail_count"] == 1115
    assert sv["setup_count"] == 46
    assert sv["entry_count"] == 41
    assert sv["exit_mean_reversion"] == 26
    assert sv["exit_divergence_stop"] == 0
    assert sv["exit_neutrality_break"] == 15
    assert sv["max_gross_observed"] == 1.0
    assert sv["max_concurrent_positions"] == 1


def test_oos_neutrality_gate_pass_fail_counts():
    sv = _R["structural_verdict"]
    # gate-zero OOS neutrality holds on only a MINORITY of bars (the C16 echo)
    assert sv["neutrality_pass_count"] + sv["neutrality_fail_count"] == 1977
    assert sv["neutrality_holds_majority"] is False
    assert sv["neutrality_pass_rate"] == round(862 / 1977, 4)


def test_structural_verdict_mechanics_clean_but_concern():
    sv = _R["structural_verdict"]
    # mechanics are clean
    assert sv["gross_cap_respected"] is True
    assert sv["non_overlap_ok"] is True
    assert sv["spacing_ok"] is True
    assert sv["mechanics_clean"] is True
    # but the structural sample gate is NOT met (41 < 100) and neutrality intermittent
    assert sv["meets_min_sample_gate"] is False
    assert sv["min_entries_structural_gate"] == 100
    assert _R["structural_concern"] is True
    assert _R["meets_min_sample_gate"] is False
    assert _R["neutrality_holds_majority"] is False
    reasons = sv["structural_concern_reasons"]
    assert any("below_min" in r for r in reasons)
    assert any("neutrality_holds_only" in r for r in reasons)


def test_honest_findings_cannot_be_flipped():
    sv = _R["structural_verdict"]
    bad1 = {**_R, "structural_verdict": {**sv, "meets_min_sample_gate": True}}
    assert l19.validate_c19_labels_review(bad1)["valid"] is False
    bad2 = {**_R, "structural_verdict": {**sv, "neutrality_holds_majority": True}}
    assert l19.validate_c19_labels_review(bad2)["valid"] is False
    bad3 = {**_R, "structural_concern": False}
    assert l19.validate_c19_labels_review(bad3)["valid"] is False
    bad4 = {**_R, "structural_verdict": {**sv, "entry_count": 500}}
    assert l19.validate_c19_labels_review(bad4)["valid"] is False


def test_cost_reserved_not_applied():
    assert _R["cost_model_reserved_for_replay"] is True
    assert _R["cost_model_applied_here"] is False
    assert _R["fee_applied"] is False
    assert _R["all_in_round_trip_bps_reserved"] == 37.0
    bad = {**_R, "fee_applied": True}
    assert l19.validate_c19_labels_review(bad)["valid"] is False


def test_next_action_replay_gate_and_downstream_locked_no_c20():
    nra = l19.get_candidate_19_labels_review_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C19_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"
    assert _R["does_not_start_c20"] is True
    assert _R["c20_candidate_id"] is None
    for gate in ("replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert l19.validate_c19_labels_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in l19._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert l19.validate_c19_labels_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_replay", "no_pnl", "no_cost_application", "no_optimization",
                 "no_tuning", "no_rescue", "no_data_fetch", "no_data_commit",
                 "no_xauusd", "no_price_level_hedge", "no_commit", "no_push",
                 "no_paper_trading", "no_live_trading", "no_start_c20"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(l19.__file__, encoding="utf-8").read()
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

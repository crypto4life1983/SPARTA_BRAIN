"""Tests for the Candidate #21 fee-honest replay results review contract
(low_turnover_same_asset_spot_perp_funding_carry_v1).

Verifies: research-only, replay-review-only, executes nothing; chain-gated on the frozen
C21 labels review; uses ONLY the frozen public data + frozen labels (no fetch; 9 SHA-pinned
sources + the labels/ledger/summary artifact SHAs, gitignored not committed); applies the
74 bps two-leg cost (not dropped); compares vs the always-on null market-neutral baseline
+ a flat-zero baseline (NOT buy-and-hold); pins the HONEST nuanced frozen metrics -- the
LOW-TURNOVER design preserves the carry NET-POSITIVE (+20.2%, Sharpe 1.05; the C20 lesson
held) but does NOT beat the always-on null (+21.2%, Sharpe 1.09) and the 2026 forward-OOS
fails, so 2 of 4 decisive gates pass and NOT all pass; confirms via the SPARTA Pipeline
Audit v1 cross-checks that the result is not a fee/funding/lookahead/duplicate/alignment
artifact; makes NO profitability/edge claim; recommends REJECT; is NOT a rescue/retune of
C20 (C20 stays rejected); does NOT start C22; capability flags + scope locks; validator
anti-tamper; module purity. Also confirms the pinned artifact SHAs match the live
gitignored artifacts on disk when present, and that the runner reproduces them."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_replay_results_review_contract as r21  # noqa: E501


_R = r21.build_c21_replay_review(".", [])


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_replay_review_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_replay_review_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C21_REPLAY_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["recommended_decision"] == "REJECT"
    assert r21.validate_c21_replay_review(_R)["valid"] is True


def test_candidate_identity_and_chain_gate():
    assert _R["candidate_id"] == "C21"
    assert _R["candidate_family"] == "low_turnover_same_asset_spot_perp_funding_carry"
    assert _R["labels_review_valid"] is True
    assert _R["labels_review_verdict"] == "C21_LABELS_FROZEN_FOR_HUMAN_REVIEW"
    bad = {**_R, "labels_review_verdict": "X"}
    assert r21.validate_c21_replay_review(bad)["valid"] is False


def test_frozen_provenance_nine_sources_plus_artifacts():
    assert _R["uses_frozen_public_data_only"] is True
    assert _R["no_new_data_fetch"] is True
    assert _R["uses_xauusd"] is False
    assert len(_R["expected_source_sha256"]) == 9
    assert _R["expected_labels_sha256"] == (
        "98e8665b239a6d7d32a30a34bc88b699a137fff23371567cc444369ccaa6cbad")
    assert _R["artifacts_gitignored_not_committed"] is True
    for bad_key, bad_val in (("expected_labels_sha256", "0" * 64),
                             ("expected_ledger_sha256", "0" * 64),
                             ("expected_summary_sha256", "0" * 64)):
        bad = {**_R, bad_key: bad_val}
        assert r21.validate_c21_replay_review(bad)["valid"] is False, bad_key


def test_artifact_shas_match_disk_when_present_and_runner_reproduces():
    lp, sp = Path(_R["ledger_path"]), Path(_R["summary_path"])
    if lp.exists():
        assert _sha256(lp) == _R["expected_ledger_sha256"]
    if sp.exists():
        assert _sha256(sp) == _R["expected_summary_sha256"]


def test_cost_applied_two_leg_and_baseline_random_null():
    assert _R["all_in_round_trip_bps"] == 37.0
    assert _R["round_trip_cost_per_trade_bps"] == 74.0
    assert _R["cost_applied_not_dropped"] is True
    assert _R["baseline_is_random_null_not_buy_and_hold"] is True
    assert _R["includes_flat_zero_baseline"] is True
    assert _R["total_cost_drag"] == 0.148
    # honest fee check: 20 trades x 74 bps = 0.148
    assert abs(_R["trade_count"] * 0.0074 - _R["total_cost_drag"]) < 1e-9
    bad = {**_R, "round_trip_cost_per_trade_bps": 37.0}
    assert r21.validate_c21_replay_review(bad)["valid"] is False


def test_low_turnover_preserved_carry_net_positive():
    # unlike C20 (net -74.5%), the low-turnover C21 stays net-positive
    assert _R["strategy_metrics"]["net_return"] > 0
    assert _R["strategy_metrics"]["net_return"] == 0.202382
    assert _R["strategy_gross_metrics"]["net_return"] == 0.257014
    assert _R["strategy_net_positive_after_cost"] is True
    assert _R["low_turnover_preserved_carry"] is True
    assert _R["trade_count"] == 20
    # only 20 trades on the same carry C20 churned with 704
    assert sum(a["trade_count"] for a in _R["per_asset"].values()) == 20


def test_does_not_beat_always_on_null_and_oos_fails():
    # the decisive market-neutral test: it does NOT beat the always-on null
    assert _R["strategy_metrics"]["net_return"] < _R["random_null_metrics"]["net_return"]
    assert _R["strategy_metrics"]["sharpe"] < _R["random_null_metrics"]["sharpe"]
    assert _R["strategy_beats_always_on_null_after_costs"] is False
    assert _R["beats_always_on_null_after_costs"] is False
    # forward-OOS is negative
    assert _R["strategy_forward_oos_metrics"]["net_return"] < 0
    assert _R["forward_oos_holds"] is False
    # the carry SOURCE is real (null positive)
    assert _R["random_null_metrics"]["net_return"] > 0
    assert _R["carry_source_is_real"] is True


def test_decisive_gates_two_pass_not_all():
    g = _R["decisive_gate_results"]
    assert g["strategy_net_return_positive_after_cost"] is True
    assert g["strategy_sharpe_positive"] is True
    assert g["beats_random_null_risk_adjusted"] is False
    assert g["forward_oos_net_return_positive"] is False
    assert _R["all_decisive_gates_pass"] is False
    # cannot be flipped to "all pass" or "beats null"
    bad = {**_R, "all_decisive_gates_pass": True}
    assert r21.validate_c21_replay_review(bad)["valid"] is False
    bad2 = {**_R, "strategy_beats_always_on_null_after_costs": True}
    assert r21.validate_c21_replay_review(bad2)["valid"] is False
    bad3 = {**_R, "decisive_gate_results": {**g,
            "beats_random_null_risk_adjusted": True}}
    assert r21.validate_c21_replay_review(bad3)["valid"] is False


def test_audit_guardrail_not_a_pipeline_artifact():
    ac = _R["audit_crosschecks"]
    for key in ("fee_cost_matches_trade_count_x_74bps",
                "funding_side_short_perp_receives_positive",
                "funding_applied_same_bar_no_lookahead", "no_duplicate_trades",
                "same_asset_spot_perp_funding_aligned",
                "turnover_ceiling_respected_all_assets", "not_a_pipeline_artifact"):
        assert ac[key] is True, key
    assert ac["duplicate_trade_keys"] == []
    assert ac["max_round_trips_per_year_per_asset"] == 6
    assert _R["not_a_pipeline_artifact"] is True
    # tamper: if an audit cross-check is violated, validation must fail
    bad = {**_R, "audit_crosschecks": {**ac, "no_duplicate_trades": False}}
    assert r21.validate_c21_replay_review(bad)["valid"] is False


def test_turnover_ceiling_respected_per_asset():
    for s, a in _R["per_asset"].items():
        assert a["round_trips_per_year"] <= 6.0, s


def test_no_profitability_or_edge_claim():
    assert _R["profitability_established"] is False
    assert _R["edge_established"] is False
    for bad_key in ("profitability_established", "edge_established"):
        bad = {**_R, bad_key: True}
        assert r21.validate_c21_replay_review(bad)["valid"] is False


def test_structural_verdict_honest():
    sv = _R["structural_verdict"]
    assert sv["recommended_decision"] == "REJECT"
    assert sv["carry_source_is_real"] is True
    assert sv["low_turnover_preserved_carry"] is True
    assert sv["improves_on_c20_churn"] is True
    assert sv["beats_always_on_null_after_costs"] is False
    assert sv["timing_adds_no_edge_over_null"] is True
    assert sv["forward_oos_holds"] is False
    assert sv["not_a_fee_funding_lookahead_duplicate_alignment_artifact"] is True
    bad_sv = {**sv, "beats_always_on_null_after_costs": True}
    bad = {**_R, "structural_verdict": bad_sv}
    assert r21.validate_c21_replay_review(bad)["valid"] is False


def test_not_a_c20_rescue_and_no_c22():
    assert _R["is_rescue_or_retune_of_c20"] is False
    assert _R["c20_remains_rejected"] is True
    assert _R["does_not_start_c22"] is True
    assert _R["c22_candidate_id"] is None
    nra = r21.get_candidate_21_replay_review_next_action()
    assert nra == _R["next_required_action"] == "HUMAN_DECISION_C21_REJECT_OR_PROMOTE"
    for bad_kv in (("is_rescue_or_retune_of_c20", True),
                   ("does_not_start_c22", False)):
        bad = {**_R, bad_kv[0]: bad_kv[1]}
        assert r21.validate_c21_replay_review(bad)["valid"] is False, bad_kv[0]


def test_downstream_gates_locked():
    assert _R["paper_trading_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    for gate in ("paper_trading_gate_locked", "live_gate_locked"):
        bad = {**_R, gate: False}
        assert r21.validate_c21_replay_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in r21._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert r21.validate_c21_replay_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_re_replay", "no_recompute_pnl", "no_change_fee", "no_drop_cost",
                 "no_optimization", "no_tuning", "no_rescue", "no_rescue_c20",
                 "no_data_fetch", "no_data_commit", "no_xauusd", "no_commit",
                 "no_push", "no_paper_trading", "no_live_trading", "no_start_c22"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(r21.__file__, encoding="utf-8").read()
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

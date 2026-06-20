"""Tests for the Candidate #21 real-candle labels review contract
(low_turnover_same_asset_spot_perp_funding_carry_v1).

Verifies: research-only, labels-review-only, executes nothing; chain-gated on the frozen
C21 detector dry-run; uses ONLY the frozen public data + frozen labels (no fetch; 9
SHA-pinned sources + gitignored artifacts not committed); applies the FROZEN detector
rules with NO re-parameterization; pins the frozen per-asset + total aggregates (6704
eval bars, 133 detected setups, 20 accepted / 113 rejected, round-trips under the 6/yr
ceiling, mechanical neutrality 6704/6704); a genuinely-LOW-TURNOVER structural verdict
that makes NO performance / profitability / fee-honest claim (replay still LOCKED); NOT a
rescue/retune of C20 (C20 stays rejected); reserves the 37/74 bps (no fee applied);
downstream gates locked; next gate is replay approval/rejection only; does NOT start C22;
capability flags + scope locks; validator anti-tamper; module purity. Also confirms the
pinned artifact SHAs match the live gitignored artifact on disk."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_real_candle_labels_review_contract as l21  # noqa: E501


_R = l21.build_c21_labels_review(".", [])


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def test_labels_review_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_labels_review_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C21_LABELS_FROZEN_FOR_HUMAN_REVIEW"
    assert l21.validate_c21_labels_review(_R)["valid"] is True


def test_candidate_identity_and_chain_gate():
    assert _R["candidate_id"] == "C21"
    assert _R["candidate_family"] == (
        "low_turnover_same_asset_spot_perp_funding_carry")
    assert _R["detector_dry_run_valid"] is True
    assert _R["detector_dry_run_verdict"] == (
        "C21_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW")
    bad = {**_R, "detector_dry_run_verdict": "X"}
    assert l21.validate_c21_labels_review(bad)["valid"] is False


def test_frozen_public_data_no_fetch_nine_shas_pinned():
    assert _R["uses_frozen_public_data_only"] is True
    assert _R["no_new_data_fetch"] is True
    assert _R["uses_xauusd"] is False
    assert len(_R["expected_source_sha256"]) == 9
    bad = {**_R, "expected_source_sha256": {**_R["expected_source_sha256"],
                                            "BTCUSDT_spot": "0" * 64}}
    assert l21.validate_c21_labels_review(bad)["valid"] is False


def test_artifacts_gitignored_sha_pinned_and_match_disk():
    assert _R["artifacts_gitignored_not_committed"] is True
    assert _R["labels_path"].startswith(
        "data/low_turnover_same_asset_spot_perp_funding_carry_c21/")
    assert _R["expected_labels_sha256"] == (
        "98e8665b239a6d7d32a30a34bc88b699a137fff23371567cc444369ccaa6cbad")
    assert _R["expected_summary_sha256"] == (
        "37ba8cc8e9e20c18dc2e8336cf87eb73d76f16948b78056d0f324bf70424777c")
    lp, sp = Path(_R["labels_path"]), Path(_R["summary_path"])
    if lp.exists():
        assert _sha256(lp) == _R["expected_labels_sha256"]
    if sp.exists():
        assert _sha256(sp) == _R["expected_summary_sha256"]
    bad = {**_R, "expected_labels_sha256": "0" * 64}
    assert l21.validate_c21_labels_review(bad)["valid"] is False


def test_frozen_detector_rules_reused_no_reparameterization():
    assert _R["rules_frozen_reused_from_committed_detector"] is True
    assert _R["no_parameter_optimization"] is True
    assert _R["annualized_carry_enter_bps"] == 100.0
    assert _R["min_hold_bars"] == 20
    assert _R["max_round_trips_per_year_per_asset"] == 6
    assert _R["is_mechanically_neutral_same_asset"] is True
    assert _R["is_low_turnover"] is True
    assert _R["uses_basis_z_stop"] is False
    assert _R["uses_drawdown_stop"] is False
    for bad_flag, val in (("is_low_turnover", False),
                          ("uses_basis_z_stop", True),
                          ("uses_drawdown_stop", True)):
        bad = {**_R, bad_flag: val}
        assert l21.validate_c21_labels_review(bad)["valid"] is False, bad_flag


def test_label_counts_pinned_and_reconcile():
    assert _R["total_eval_bars"] == 6704
    assert _R["total_detected_setup_count"] == 133
    assert _R["total_accepted_label_count"] == 20
    assert _R["total_rejected_label_count"] == 113
    assert _R["total_round_trips"] == 20
    assert _R["total_exit_counts"] == {"durable_carry_regime_breakdown": 17,
                                       "end_of_data": 3}
    assert _R["total_mechanical_neutral_pass"] == 6704
    assert _R["total_mechanical_neutral_fail"] == 0
    assert _R["total_forward_oos_accepted_count"] == 3
    # accepted + rejected == detected; exits == accepted
    assert (_R["total_accepted_label_count"] + _R["total_rejected_label_count"]
            == _R["total_detected_setup_count"])
    assert sum(_R["total_exit_counts"].values()) == _R["total_accepted_label_count"]
    bad = {**_R, "total_accepted_label_count": 999}
    assert l21.validate_c21_labels_review(bad)["valid"] is False


def test_per_asset_low_turnover_pinned():
    pa = _R["per_asset"]
    assert set(pa) == {"BTCUSDT", "ETHUSDT", "SOLUSDT"}
    assert pa["BTCUSDT"]["accepted_label_count"] == 6
    assert pa["ETHUSDT"]["accepted_label_count"] == 5
    assert pa["SOLUSDT"]["accepted_label_count"] == 9
    assert sum(pa[s]["accepted_label_count"] for s in pa) == 20
    # genuinely low turnover: every asset well under the 6/yr ceiling, long holds
    for s in pa:
        assert pa[s]["round_trips_per_year"] <= 6
        assert pa[s]["avg_hold_bars"] >= 20      # persistence: long holds
        assert pa[s]["mechanical_neutral_fail"] == 0
        assert pa[s]["max_concurrent_positions"] <= 1
    bad_pa = {s: dict(v) for s, v in pa.items()}
    bad_pa["BTCUSDT"] = {**bad_pa["BTCUSDT"], "accepted_label_count": 99}
    bad = {**_R, "per_asset": bad_pa}
    assert l21.validate_c21_labels_review(bad)["valid"] is False


def test_structural_verdict_low_turnover_no_performance_claim():
    sv = _R["structural_verdict"]
    assert sv["is_genuinely_low_turnover"] is True
    assert sv["round_trips_under_ceiling"] is True
    assert sv["mechanical_neutrality_holds"] is True
    assert sv["mechanics_clean"] is True
    assert sv["labels_reconcile"] is True
    assert sv["exits_reconcile_with_accepted"] is True
    assert sv["fewer_trades_than_c20_high_turnover"] is True
    # the labels stage NEVER claims performance / profitability / fee-honest result
    assert sv["profitability_established"] is False
    assert sv["edge_established"] is False
    assert sv["fee_honest_performance_claimed"] is False
    assert sv["decisive_gate_is_fee_honest_replay"] is True
    assert sv["replay_remains_locked"] is True
    assert _R["profitability_established"] is False
    assert _R["fee_honest_performance_claimed"] is False
    assert _R["claims_profitability"] is False
    assert _R["claims_fee_honest_performance"] is False
    bad_sv = {**sv, "profitability_established": True}
    bad = {**_R, "structural_verdict": bad_sv}
    assert l21.validate_c21_labels_review(bad)["valid"] is False


def test_not_a_c20_rescue_c20_stays_rejected():
    assert _R["is_rescue_or_retune_of_c20"] is False
    assert _R["c20_remains_rejected"] is True
    bad = {**_R, "is_rescue_or_retune_of_c20": True}
    assert l21.validate_c21_labels_review(bad)["valid"] is False


def test_cost_reserved_no_fee_replay_locked():
    assert _R["cost_model_applied_here"] is False
    assert _R["fee_applied"] is False
    assert _R["all_in_round_trip_bps_reserved"] == 37.0
    assert _R["round_trip_cost_per_trade_bps_reserved"] == 74.0
    assert _R["replay_remains_locked"] is True
    assert _R["replay_gate_locked"] is True
    bad = {**_R, "fee_applied": True}
    assert l21.validate_c21_labels_review(bad)["valid"] is False


def test_next_action_replay_gate_and_no_c22():
    nra = l21.get_candidate_21_labels_review_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C21_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"
    assert _R["does_not_start_c22"] is True
    assert _R["c22_candidate_id"] is None
    for gate in ("replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert l21.validate_c21_labels_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in l21._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert l21.validate_c21_labels_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_replay", "no_pnl", "no_cost_application", "no_optimization",
                 "no_tuning", "no_rescue", "no_rescue_c20", "no_data_fetch",
                 "no_data_commit", "no_xauusd", "no_high_turnover", "no_basis_z_stop",
                 "no_drawdown_stop", "no_fee_honest_performance_claim",
                 "no_paper_trading", "no_live_trading", "no_start_c22"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(l21.__file__, encoding="utf-8").read()
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

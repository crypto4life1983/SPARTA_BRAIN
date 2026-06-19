"""Tests for the Candidate #20 real-candle labels review contract
(mechanically_neutral_spot_perp_basis_funding_carry_v1).

Verifies: research-only, labels-review-only, executes nothing; chain-gated on the frozen
C20 detector dry-run; uses ONLY the frozen PUBLIC BTC/ETH/SOL spot+perp+funding data (no
fetch, 9 SHA-pinned sources + gitignored artifacts not committed); honours the exact
same-asset basis/funding params; pins the frozen per-asset + total aggregates (6614 eval
bars, 704 entries, 688/16 funding/basis entry reasons, mechanical neutrality 6614/6614,
35 forward-OOS 2026 entries) and a STRUCTURALLY-HEALTHY verdict that explicitly does NOT
claim profitability/edge (reserved for replay); reserves the 37 bps (no fee applied);
downstream gates locked; does NOT start C21; capability flags + scope locks; validator
anti-tamper; module purity. Also confirms the pinned artifact SHAs match the live
gitignored artifact on disk."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_real_candle_labels_review_contract as l20  # noqa: E501


_R = l20.build_c20_labels_review(".", [])


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
    assert _R["verdict"] == "C20_LABELS_FROZEN_FOR_HUMAN_REVIEW"
    assert l20.validate_c20_labels_review(_R)["valid"] is True


def test_candidate_identity_and_chain_gate():
    assert _R["candidate_id"] == "C20"
    assert _R["candidate_family"] == (
        "mechanically_neutral_spot_perp_basis_funding_carry")
    assert _R["detector_dry_run_valid"] is True
    assert _R["detector_dry_run_verdict"] == (
        "C20_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW")
    bad = {**_R, "detector_dry_run_verdict": "X"}
    assert l20.validate_c20_labels_review(bad)["valid"] is False


def test_frozen_public_data_no_fetch_nine_shas_pinned():
    assert _R["uses_frozen_public_data_only"] is True
    assert _R["no_new_data_fetch"] is True
    assert _R["uses_xauusd"] is False
    assert _R["universe"] == ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
    src = _R["expected_source_sha256"]
    assert len(src) == 9
    for k, v in src.items():
        assert len(v) == 64, k
    assert src["BTCUSDT_spot"] == (
        "0a214e5fae7f7b73b632193c23d633ab87114b7559e75111fa9ed7f1ef998f1a")
    assert src["SOLUSDT_perp"] == (
        "a9810dfab32f210d18dd6a428f424a769eaf9c5449367adf795c95374c7c49a0")
    bad = {**_R, "expected_source_sha256": {**src, "BTCUSDT_spot": "0" * 64}}
    assert l20.validate_c20_labels_review(bad)["valid"] is False


def test_artifacts_gitignored_sha_pinned_and_match_disk():
    assert _R["artifacts_gitignored_not_committed"] is True
    assert _R["labels_path"].startswith(
        "data/mechanically_neutral_spot_perp_basis_funding_carry_c20/")
    assert _R["expected_labels_sha256"] == (
        "e8282933ea1b07f14c7a09b72cc71632de2880d88e9105d3d0e91fe2702ca842")
    assert _R["expected_summary_sha256"] == (
        "f371b18a214eb5f1f52ffdccebda726bad6d11a0f3ca5796594d61fe424d48b5")
    # the pinned SHAs match the live gitignored artifact on disk (deterministic run)
    lp, sp = Path(_R["labels_path"]), Path(_R["summary_path"])
    if lp.exists():
        assert _sha256(lp) == _R["expected_labels_sha256"]
    if sp.exists():
        assert _sha256(sp) == _R["expected_summary_sha256"]
    bad = {**_R, "expected_labels_sha256": "0" * 64}
    assert l20.validate_c20_labels_review(bad)["valid"] is False


def test_exact_params_and_mechanical_identity():
    assert _R["basis_zscore_window_bars"] == 60
    assert _R["funding_lookback_bars"] == 30
    assert _R["entry_basis_zscore_threshold"] == 2.0
    assert _R["entry_min_annualized_carry_bps"] == 50.0
    assert _R["max_gross_exposure"] == 1.0
    assert _R["basis_formula"] == "(perp_close - spot_close) / spot_close"
    assert _R["is_mechanically_neutral_same_asset"] is True
    assert _R["is_estimated_cross_asset_neutral"] is False
    assert _R["mechanical_neutrality_is_gate_zero"] is True
    for bad_flag, val in (("is_mechanically_neutral_same_asset", False),
                          ("is_estimated_cross_asset_neutral", True)):
        bad = {**_R, bad_flag: val}
        assert l20.validate_c20_labels_review(bad)["valid"] is False, bad_flag


def test_per_asset_aggregates_pinned():
    pa = _R["per_asset"]
    assert set(pa) == {"BTCUSDT", "ETHUSDT", "SOLUSDT"}
    assert pa["BTCUSDT"]["entry_count"] == 243
    assert pa["ETHUSDT"]["entry_count"] == 255
    assert pa["SOLUSDT"]["entry_count"] == 206
    assert pa["BTCUSDT"]["common_window"] == ["2020-01-02", "2026-06-08"]
    assert pa["SOLUSDT"]["common_window"] == ["2020-09-14", "2026-06-08"]
    # per-asset entries sum to the pinned total
    assert sum(pa[s]["entry_count"] for s in pa) == _R["total_entry_count"] == 704
    # every asset is mechanically neutral on every eval bar (0 fails)
    for s in pa:
        assert pa[s]["mechanical_neutral_fail"] == 0
        assert pa[s]["max_concurrent_positions"] <= 1
        assert pa[s]["spacing_ok"] is True
    # tamper: per-asset entries that no longer sum to the total fail
    bad_pa = {s: dict(v) for s, v in pa.items()}
    bad_pa["BTCUSDT"] = {**bad_pa["BTCUSDT"], "entry_count": 999}
    bad = {**_R, "per_asset": bad_pa}
    assert l20.validate_c20_labels_review(bad)["valid"] is False


def test_total_label_counts_pinned():
    assert _R["total_eval_bars"] == 6614
    assert _R["total_setup_count"] == 1430
    assert _R["total_entry_count"] == 704
    assert _R["total_entry_reason_counts"] == {"funding_carry": 688,
                                               "basis_convergence": 16}
    assert _R["total_exit_counts"] == {"convergence": 640, "carry_decay": 12,
                                       "negative_carry": 20, "divergence_stop": 30,
                                       "neutrality_break": 0, "end_of_data": 2}
    assert _R["total_mechanical_neutral_pass"] == 6614
    assert _R["total_mechanical_neutral_fail"] == 0
    assert _R["total_forward_oos_entry_count"] == 35
    # exits + reasons reconcile to the entry total
    assert sum(_R["total_exit_counts"].values()) == 704
    assert sum(_R["total_entry_reason_counts"].values()) == 704
    for bad_key, bad_val in (("total_entry_reason_counts",
                              {"funding_carry": 1, "basis_convergence": 1}),
                             ("total_exit_counts", {"convergence": 1})):
        bad = {**_R, bad_key: bad_val}
        assert l20.validate_c20_labels_review(bad)["valid"] is False, bad_key


def test_structural_verdict_healthy_but_not_profitability_claim():
    sv = _R["structural_verdict"]
    assert sv["meets_min_sample_gate"] is True            # 704 >= 100
    assert sv["mechanical_neutrality_holds"] is True       # 0 fails by construction
    assert sv["mechanics_clean"] is True
    assert sv["structurally_healthy"] is True
    assert sv["has_forward_oos_coverage"] is True
    assert sv["exits_reconcile_with_entries"] is True
    assert sv["entry_reasons_reconcile_with_entries"] is True
    assert sv["carry_dominated_by_funding"] is True
    # the labels stage NEVER claims profitability / edge
    assert sv["profitability_established"] is False
    assert sv["edge_established"] is False
    assert sv["decisive_gate_is_fee_honest_replay"] is True
    assert _R["profitability_established"] is False
    assert _R["claims_profitability"] is False
    assert _R["claims_edge"] is False
    # tamper: cannot flip to a profitability claim
    bad_sv = {**sv, "profitability_established": True}
    bad = {**_R, "structural_verdict": bad_sv}
    assert l20.validate_c20_labels_review(bad)["valid"] is False


def test_forward_oos_2026_coverage():
    assert _R["total_forward_oos_entry_count"] == 35
    pa = _R["per_asset"]
    assert (pa["BTCUSDT"]["forward_oos_entry_count"]
            + pa["ETHUSDT"]["forward_oos_entry_count"]
            + pa["SOLUSDT"]["forward_oos_entry_count"]) == 35


def test_cost_reserved_no_fee_applied():
    assert _R["cost_model_applied_here"] is False
    assert _R["fee_applied"] is False
    assert _R["all_in_round_trip_bps_reserved"] == 37.0
    assert _R["perp_frictions_reserved_for_replay"] is True
    bad = {**_R, "fee_applied": True}
    assert l20.validate_c20_labels_review(bad)["valid"] is False


def test_next_action_replay_gate_and_no_c21():
    nra = l20.get_candidate_20_labels_review_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C20_ADVANCE_TO_FEE_HONEST_REPLAY_OR_REJECT"
    assert _R["does_not_start_c21"] is True
    assert _R["c21_candidate_id"] is None
    for gate in ("replay_gate_locked", "paper_trading_gate_locked",
                 "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert l20.validate_c20_labels_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in l20._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert l20.validate_c20_labels_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_replay", "no_pnl", "no_cost_application", "no_optimization",
                 "no_tuning", "no_rescue", "no_data_fetch", "no_data_commit",
                 "no_xauusd", "no_estimated_cross_asset_hedge",
                 "no_overlapping_positions", "no_paper_trading", "no_live_trading",
                 "no_start_c21"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(l20.__file__, encoding="utf-8").read()
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

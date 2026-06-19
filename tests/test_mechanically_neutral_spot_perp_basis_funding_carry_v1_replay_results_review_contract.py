"""Tests for the Candidate #20 fee-honest replay results review contract
(mechanically_neutral_spot_perp_basis_funding_carry_v1).

Verifies: research-only, replay-review-only, executes nothing; chain-gated on the frozen
C20 labels review; uses ONLY the frozen public data + frozen labels (no fetch; 9
SHA-pinned sources + gitignored replay artifacts not committed); applies the 74 bps
two-leg cost (37 bps per leg, doubled), not dropped; compares vs a random/null
market-neutral baseline (NOT buy-and-hold); pins the HONEST frozen metrics (portfolio net
-74.5%, Sharpe -12.8, all four decisive gates fail) plus the finding that the always-on
null is positive (carry thesis real); recommends REJECT; cannot be flipped to a
profitability claim; no optimization/tuning; does NOT start C21 or pivot to a new family;
downstream gates locked; capability flags + scope locks; validator anti-tamper; module
purity. Also confirms the pinned replay artifact SHAs match the live gitignored artifact
on disk."""
from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_replay_results_review_contract as r20  # noqa: E501


_R = r20.build_c20_replay_review(".", [])


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
    assert _R["verdict"] == "C20_REPLAY_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["recommended_decision"] == "REJECT"
    assert r20.validate_c20_replay_review(_R)["valid"] is True


def test_candidate_identity_and_chain_gate():
    assert _R["candidate_id"] == "C20"
    assert _R["candidate_family"] == (
        "mechanically_neutral_spot_perp_basis_funding_carry")
    assert _R["labels_review_valid"] is True
    assert _R["labels_review_verdict"] == "C20_LABELS_FROZEN_FOR_HUMAN_REVIEW"
    bad = {**_R, "labels_review_verdict": "X"}
    assert r20.validate_c20_replay_review(bad)["valid"] is False


def test_frozen_provenance_nine_sources_plus_replay_shas():
    assert _R["no_new_data_fetch"] is True
    assert _R["uses_xauusd"] is False
    assert len(_R["expected_source_sha256"]) == 9
    assert _R["expected_labels_sha256"] == (
        "e8282933ea1b07f14c7a09b72cc71632de2880d88e9105d3d0e91fe2702ca842")
    assert _R["expected_ledger_sha256"] == (
        "d0f5463a9c47b969a4461b7803f6b82e08c50dfd98f1c239df7dd7a7ee4b3daa")
    assert _R["expected_summary_sha256"] == (
        "cf6bedf9e5ed0a22ea4163fae51f54ad7ac4a16f16d3efdeb37232e949980b2c")
    assert _R["artifacts_gitignored_not_committed"] is True
    for bad_key in ("expected_ledger_sha256", "expected_summary_sha256",
                    "expected_labels_sha256"):
        bad = {**_R, bad_key: "0" * 64}
        assert r20.validate_c20_replay_review(bad)["valid"] is False, bad_key


def test_pinned_shas_match_live_replay_artifact():
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
    for bad_key, val in (("round_trip_cost_per_trade_bps", 37.0),
                         ("cost_applied_not_dropped", False),
                         ("baseline_is_random_null_not_buy_and_hold", False)):
        bad = {**_R, bad_key: val}
        assert r20.validate_c20_replay_review(bad)["valid"] is False, bad_key


def test_strategy_fails_all_decisive_gates():
    assert _R["all_decisive_gates_pass"] is False
    g = _R["decisive_gate_results"]
    assert g["strategy_net_return_positive_after_cost"] is False
    assert g["strategy_sharpe_positive"] is False
    assert g["beats_random_null_risk_adjusted"] is False
    assert g["forward_oos_net_return_positive"] is False
    assert _R["strategy_metrics"]["net_return"] == -0.7452
    assert _R["strategy_metrics"]["sharpe"] == -12.836936
    assert _R["strategy_forward_oos_metrics"]["net_return"] == -0.082992
    assert _R["fails_all_decisive_gates"] is True
    # cannot flip a gate to true while keeping the all-fail finding
    bad = {**_R, "decisive_gate_results": {**g,
                                           "strategy_net_return_positive_after_cost": True}}
    assert r20.validate_c20_replay_review(bad)["valid"] is False
    bad2 = {**_R, "all_decisive_gates_pass": True}
    assert r20.validate_c20_replay_review(bad2)["valid"] is False


def test_honest_carry_real_but_timing_churns():
    # the always-on null is POSITIVE -> the carry thesis is real
    assert _R["random_null_metrics"]["net_return"] == 0.211648
    assert _R["random_null_metrics"]["sharpe"] == 1.087808
    assert _R["carry_thesis_vindicated_by_positive_null"] is True
    sv = _R["structural_verdict"]
    assert sv["recommended_decision"] == "REJECT"
    assert sv["carry_thesis_vindicated_by_positive_null"] is True
    assert sv["rejects_timing_not_carry_thesis"] is True
    assert sv["cost_drag_dominates_funding"] is True
    assert sv["strategy_worse_than_always_on_null"] is True
    # the cost drag (521%) exceeds the gross funding collected (~80%)
    assert _R["total_cost_drag"] == 5.2096
    assert _R["funding_contribution_total"] == 0.797538


def test_contribution_split_and_trade_stats():
    assert _R["trade_count"] == 704
    assert _R["win_rate"] == 0.03267
    assert _R["avg_trade_net"] == -0.00626227
    assert _R["forward_oos_trade_count"] == 35
    assert _R["forward_oos_win_rate"] == 0.0
    assert _R["funding_contribution_total"] == 0.797538
    assert _R["basis_convergence_contribution_total"] == 0.003424


def test_per_asset_results_pinned():
    pa = _R["per_asset"]
    assert set(pa) == {"BTCUSDT", "ETHUSDT", "SOLUSDT"}
    assert sum(pa[s]["trade_count"] for s in pa) == 704
    # every asset's timed strategy loses; BTC/ETH null is strongly positive
    for s in pa:
        assert pa[s]["strategy_net"] < 0
    assert pa["BTCUSDT"]["null_net"] > 0 and pa["BTCUSDT"]["null_sharpe"] > 0
    assert pa["ETHUSDT"]["null_net"] > 0 and pa["ETHUSDT"]["null_sharpe"] > 0
    # tamper: per-asset trades must sum to the pinned total
    bad_pa = {s: dict(v) for s, v in pa.items()}
    bad_pa["BTCUSDT"] = {**bad_pa["BTCUSDT"], "trade_count": 1}
    bad = {**_R, "per_asset": bad_pa}
    assert r20.validate_c20_replay_review(bad)["valid"] is False


def test_not_a_profitability_claim():
    assert _R["profitability_established"] is False
    assert _R["edge_established"] is False
    assert _R["claims_profitability"] is False
    assert _R["claims_edge"] is False
    assert _R["strategy_net_negative_after_cost"] is True


def test_no_optimization_no_pivot_next_gate_and_locks():
    assert _R["no_parameter_optimization"] is True
    assert _R["no_parameter_tuning"] is True
    assert _R["no_rescue"] is True
    assert _R["no_parameter_sweep"] is True
    assert _R["does_not_pivot_to_new_family_here"] is True
    assert _R["does_not_start_c21"] is True
    assert _R["c21_candidate_id"] is None
    nra = r20.get_candidate_20_replay_review_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C20_REJECT_OR_PROMOTE"
    for gate in ("paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert r20.validate_c20_replay_review(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in r20._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert r20.validate_c20_replay_review(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_re_replay", "no_recompute_pnl", "no_change_fee", "no_drop_cost",
                 "no_optimization", "no_tuning", "no_rescue", "no_parameter_sweep",
                 "no_data_fetch", "no_data_commit", "no_xauusd",
                 "no_pivot_to_new_family", "no_paper_trading", "no_live_trading",
                 "no_start_c21"):
        assert _R["scope_locks"][must] is True, must


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(r20.__file__, encoding="utf-8").read()
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

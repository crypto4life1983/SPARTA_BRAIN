"""Tests for the Candidate #10 fee+slippage-honest replay-results review /
evidence-freeze contract (INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1).

Verifies: chain-gate on the pushed FROZEN labels-review; frozen SHA pins of the
source, labels, and the two untracked replay artifacts; the frozen replay
aggregates (156 trades; per-variant gross/net/win-rate/total-R/drawdown/
per-year); the HONEST framing (net-positive full sample but NEGATIVE in 2025 for
every variant -> regime_decay_2025); all downstream gates locked; no
profitability claim; the replay artifacts remain untracked; AST/purity green.

Optimization: the shared C10 build chain is memoized once at import via the same
once-per-original deepcopy pattern used by the other C10 contract tests."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.intraweek_calendar_seasonality_drift_v1_replay_results_review_contract as c10rr  # noqa: E501


def _tracked_paths():
    return subprocess.check_output(
        ["git", "ls-files"]).decode("utf-8").splitlines()


# ---- one-time memoization of the pure build-gate chain --------------------
def _install_pure_gate_memoization():
    cache: dict = {}
    wrappers: dict = {}
    restore: list = []

    def _make(orig):
        def _wrapped(*args, **kwargs):
            if args or kwargs:
                return orig(*args, **kwargs)
            oid = id(orig)
            if oid not in cache:
                cache[oid] = orig()
            return copy.deepcopy(cache[oid])
        return _wrapped

    def _is_target(fn) -> bool:
        return inspect.isfunction(fn) and (
            fn.__name__.startswith("build_")
            or fn.__name__ == "_recompute_live_dry_run")

    for _mname, _mod in list(sys.modules.items()):
        if _mod is None or not _mname.startswith("sparta_commander"):
            continue
        for _orig in list(vars(_mod).values()):
            if _is_target(_orig) and id(_orig) not in wrappers:
                wrappers[id(_orig)] = _make(_orig)
    for _mname, _mod in list(sys.modules.items()):
        if _mod is None or not _mname.startswith("sparta_commander"):
            continue
        for _attr, _val in list(vars(_mod).items()):
            if inspect.isfunction(_val) and id(_val) in wrappers:
                restore.append((_mod, _attr, _val))
                setattr(_mod, _attr, wrappers[id(_val)])
    return restore


_memo_restore = _install_pure_gate_memoization()
try:
    _R = c10rr.build_c10_replay_review(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + frozen verdict -------------------------------------------

def test_review_frozen_and_validates():
    assert _R["verdict"] == c10rr.VERDICT_C10RR_FROZEN
    assert _R["blockers"] == []
    assert _R["labels_review_verdict"] == c10rr.VERDICT_C10L_FROZEN
    assert c10rr.validate_c10_replay_review(_R)["valid"] is True


def test_sha_pins_frozen():
    assert _R["expected_labels_sha256"] == c10rr.EXPECTED_LABELS_SHA256
    assert _R["expected_source_sha256"] == c10rr.EXPECTED_SOURCE_SHA256
    assert _R["expected_replay_ledger_sha256"] == (
        c10rr.EXPECTED_REPLAY_LEDGER_SHA256)
    assert _R["expected_replay_summary_sha256"] == (
        c10rr.EXPECTED_REPLAY_SUMMARY_SHA256)
    assert _R["head_at_labels_review"] == (
        "0de0f7c1089a9650204a786a983502b34b0417be")
    for field in ("expected_replay_ledger_sha256",
                  "expected_replay_summary_sha256", "head_at_labels_review"):
        bad = copy.deepcopy(_R)
        bad[field] = "0" * 64 if "sha" in field else "deadbeef"
        assert c10rr.validate_c10_replay_review(bad)["valid"] is False, field


# ---- cost basis ------------------------------------------------------------

def test_cost_basis_fee_plus_slippage_all_in():
    assert _R["fee_round_trip_bps"] == 27.0
    assert _R["slippage_round_trip_bps"] == 10.0
    assert _R["all_in_round_trip_bps"] == 37.0
    bad = copy.deepcopy(_R)
    bad["slippage_round_trip_bps"] = 0.0
    assert c10rr.validate_c10_replay_review(bad)["valid"] is False


# ---- frozen aggregates -----------------------------------------------------

def test_replay_aggregates_156_trades_all_variants():
    agg = _R["replay_aggregates"]
    for name in ("2r", "3r", "4r"):
        assert agg[name]["trade_count"] == 156
        assert agg[name]["net_all_in_positive_full_sample"] is True
        assert agg[name]["miss"] == 30
        assert agg[name]["straddle"] == 0


def test_hit_rates_decline_with_target_distance():
    agg = _R["replay_aggregates"]
    assert agg["2r"]["hit"] == 16
    assert agg["3r"]["hit"] == 8
    assert agg["4r"]["hit"] == 4
    # horizon exits dominate
    for name in ("2r", "3r", "4r"):
        assert agg[name]["horizon"] >= 110


def test_full_sample_net_positive_after_costs():
    agg = _R["replay_aggregates"]
    assert _R["all_variants_net_positive_after_costs_full_sample"] is True
    for name in ("2r", "3r", "4r"):
        assert agg[name]["net_r_total_all_in"] > 0


def test_2025_regime_decay_is_disclosed_and_negative():
    assert _R["regime_decay_2025"] is True
    assert _R["any_variant_net_positive_in_2025"] is False
    agg = _R["replay_aggregates"]
    for name in ("2r", "3r", "4r"):
        assert agg[name]["per_year_net_all_in"]["2025"] < 0
        # 2023 + 2024 carry the positive contribution
        assert agg[name]["per_year_net_all_in"]["2023"] > 0
        assert agg[name]["per_year_net_all_in"]["2024"] > 0
    # tampering away the decay disclosure invalidates
    bad = copy.deepcopy(_R)
    bad["regime_decay_2025"] = False
    assert c10rr.validate_c10_replay_review(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["replay_aggregates"]["3r"]["per_year_net_all_in"]["2025"] = 5.0
    assert c10rr.validate_c10_replay_review(bad2)["valid"] is False


def test_drawdown_and_means_present():
    agg = _R["replay_aggregates"]
    for name in ("2r", "3r", "4r"):
        assert agg[name]["max_drawdown_r_all_in"] > 0
        assert "net_r_mean_all_in" in agg[name]
        assert "win_rate_net_all_in" in agg[name]


# ---- honest caveats + claim locks ------------------------------------------

def test_honest_caveats_present():
    joined = " || ".join(_R["honest_caveats"]).lower()
    assert "not a profitability claim" in joined
    assert "decays to negative in 2025" in joined or "regime_decay_2025" in joined
    assert "single asset" in joined
    assert "horizon exits dominate" in joined


def test_claim_locks_present():
    for required in ("no_profitability_claim", "no_paper_approval",
                     "no_live_approval", "regime_decay_2025_disclosed",
                     "single_asset_single_weekday_disclosed"):
        assert required in _R["claim_locks"], required
    bad = copy.deepcopy(_R)
    bad["claim_locks"] = []
    assert c10rr.validate_c10_replay_review(bad)["valid"] is False


# ---- downstream locks + capability flags -----------------------------------

def test_all_downstream_gates_locked():
    assert _R["is_replay_review_only"] is True
    assert _R["current_loop_stage"] == "replay_evaluation_review"
    assert _R["human_review_required"] is True
    assert _R["relabel_gate_locked"] is True
    assert _R["paper_trading_gate_locked"] is True
    assert _R["micro_live_gate_locked"] is True
    assert _R["live_gate_locked"] is True
    for key, val in _R["scope_locks"].items():
        assert val is True, key


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c10rr._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c10rr.validate_c10_replay_review(bad)["valid"] is False, flag


def test_next_action_and_label_no_banned_tokens():
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C10_PROMOTE_TO_ROBUSTNESS_OR_REJECT")
    label = c10rr.get_candidate_10_replay_review_label()
    assert "RESEARCH ONLY" in label
    assert "NOT A PROFITABILITY CLAIM" in label
    assert "REGIME DECAY" in label
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "EDGE CONFIRMED",
                   "PROFITABLE", "WINNER"):
        assert banned not in label.upper(), banned


# ---- artifacts remain untracked --------------------------------------------

def test_replay_artifacts_remain_untracked():
    tracked = _tracked_paths()
    assert c10rr.LEDGER_PATH not in tracked
    assert c10rr.SUMMARY_PATH not in tracked
    for p in tracked:
        assert not p.startswith(
            "data/intraweek_calendar_seasonality_c10/replay_results/"), p


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c10rr.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib"}
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

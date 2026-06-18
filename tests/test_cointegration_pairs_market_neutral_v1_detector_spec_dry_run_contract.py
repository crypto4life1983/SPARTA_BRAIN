"""Tests for the Candidate #16 detector spec + SYNTHETIC dry-run contract
(cointegration_pairs_market_neutral_v1).

Proves on deterministic synthetic fixtures: rolling-OLS hedge ratio is
deterministic; residual z-score entry at |z| >= 2.0, exit at |z| <= 0.5, stop at
|z| >= 3.5; cointegration p-value gate <= 0.05 (a cointegrated pair trades, a
non-cointegrated pair does NOT); dollar/beta-neutral two-leg construction; net
beta near zero (|net beta| <= 0.10); no naked directional leg; pair universe
ETHBTC/SOLETH/SOLBTC only; rejected C1-C15 stay excluded; no carry/buy-and-hold
shortcut; cost model reserved (not applied). Plus chain gate, downstream locks,
capability flags, validator anti-tamper, module purity. Deterministic."""
from __future__ import annotations

import ast

import sparta_commander.cointegration_pairs_market_neutral_v1_detector_spec_dry_run_contract as d16  # noqa: E501


_R = d16.build_c16_detector_dry_run(".", [])


# ---- core: research-only, synthetic, frozen, validates ---------------------

def test_dry_run_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_synthetic_dry_run_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C16_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert d16.validate_c16_detector_dry_run(_R)["valid"] is True


def test_chain_gated_on_frozen_spec():
    assert _R["spec_valid"] is True
    assert _R["spec_verdict"] == "C16_SPEC_FROZEN_FOR_HUMAN_REVIEW"


# ---- synthetic only / no real data / cost reserved -------------------------

def test_synthetic_only_cost_reserved():
    assert _R["uses_synthetic_fixtures_only"] is True
    assert _R["uses_real_data"] is False
    assert _R["cost_model_reserved_for_replay"] is True
    assert _R["cost_model_applied_here"] is False
    assert _R["all_in_pair_round_trip_bps_reserved"] == 74.0
    assert _R["applies_cost_model"] is False
    bad = {**_R, "uses_real_data": True}
    assert d16.validate_c16_detector_dry_run(bad)["valid"] is False


# ---- all behaviour checks pass ---------------------------------------------

def test_all_dry_run_checks_pass():
    assert _R["dry_run_all_checks_pass"] is True
    for k in ("hedge_ratio_deterministic", "cointegrated_pair_is_tradeable",
              "noncointegrated_pair_not_tradeable", "entry_at_z_ge_2",
              "exit_at_z_le_0_5", "stop_at_z_ge_3_5", "dollar_neutral_two_legs",
              "no_naked_directional_leg", "net_beta_near_zero",
              "pair_universe_only", "cost_model_not_applied"):
        assert _R["dry_run_checks"][k] is True, k


# ---- deterministic hedge ratio ---------------------------------------------

def test_hedge_ratio_deterministic():
    fx = d16.build_synthetic_fixtures()
    a = d16.scan_c16_pair(fx["ETHBTC"]["num"], fx["ETHBTC"]["den"])
    b = d16.scan_c16_pair(fx["ETHBTC"]["num"], fx["ETHBTC"]["den"])
    assert a["hedge_ratio"] == b["hedge_ratio"]
    assert abs(a["hedge_ratio"] - 1.0) < 0.05      # recovers ~beta_true=1


# ---- z entry / exit / stop at 2.0 / 0.5 / 3.5 ------------------------------

def test_z_entry_exit_stop_thresholds():
    res = _R["dry_run_results"]
    eth = res["ETHBTC"]
    assert eth["tradeable"] is True
    assert eth["n_trades"] >= 1
    assert eth["max_abs_entry_z"] >= 2.0
    assert eth["had_take"] is True            # exit at |z| <= 0.5
    sol = res["SOLETH"]
    assert sol["had_stop"] is True            # stop at |z| >= 3.5
    # every recorded entry fired at |z| >= entry_z
    for t in eth["trades"]:
        assert abs(t["entry_z"]) >= 2.0


# ---- cointegration p-value gate (<= 0.05) ----------------------------------

def test_cointegration_pvalue_gate():
    res = _R["dry_run_results"]
    assert res["ETHBTC"]["coint_pvalue"] <= 0.05 and res["ETHBTC"]["tradeable"] is True
    assert res["SOLBTC"]["coint_pvalue"] > 0.05 and res["SOLBTC"]["tradeable"] is False
    assert res["SOLBTC"]["n_trades"] == 0     # non-cointegrated -> no trades
    assert _R["uses_cointegration_validity_gate"] is True


# ---- dollar/beta-neutral, net beta near zero, no naked leg -----------------

def test_dollar_beta_neutral_and_no_naked_leg():
    res = _R["dry_run_results"]
    assert _R["dry_run_max_abs_net_beta"] <= 0.10
    for pair in ("ETHBTC", "SOLETH"):
        for t in res[pair]["trades"]:
            sides = {leg["side"] for leg in t["legs"]}
            assert sides == {1, -1}            # one long leg + one short leg
            assert len(t["legs"]) == 2         # never a single naked leg
    assert _R["is_market_neutral"] is True and _R["is_directional"] is False
    assert _R["relies_on_directional_carry"] is False


# ---- pair universe + anti-loop (no carry shortcut, C1-C15 excluded) --------

def test_pair_universe_only_and_anti_loop():
    assert set(_R["pair_universe"]) == {"ETHBTC", "SOLETH", "SOLBTC"}
    assert _R["candidate_not_in_rejected_ledger"] is True
    assert _R["does_not_reuse_c15"] is True
    assert _R["rejected_families_count"] == 20
    bad = {**_R, "pair_universe": ["ETHBTC", "DOGEBTC"]}
    assert d16.validate_c16_detector_dry_run(bad)["valid"] is False


def test_no_carry_or_buy_and_hold_shortcut():
    # the detector never carries net directional exposure: net beta stays tiny and
    # no single-leg (directional) trade exists.
    assert _R["dry_run_max_abs_net_beta"] <= 0.10
    res = _R["dry_run_results"]
    for pair in ("ETHBTC", "SOLETH"):
        for t in res[pair]["trades"]:
            assert len(t["legs"]) == 2
    # tampering net beta above the cap is rejected
    bad = {**_R, "dry_run_max_abs_net_beta": 0.9}
    assert d16.validate_c16_detector_dry_run(bad)["valid"] is False


# ---- downstream gates locked + flags + scope locks -------------------------

def test_downstream_gates_locked():
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert d16.validate_c16_detector_dry_run(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in d16._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert d16.validate_c16_detector_dry_run(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_real_candles", "no_labels", "no_replay",
                 "no_pnl", "no_cost_application", "no_optimization", "no_commit",
                 "no_push", "no_broker", "no_paper_trading", "no_live_trading",
                 "no_directional_carry_shortcut"):
        assert _R["scope_locks"][must] is True, must


def test_label_and_next_action_no_readiness():
    label = d16.get_candidate_16_detector_dry_run_label()
    assert "RESEARCH ONLY" in label
    assert "SYNTHETIC" in label.upper()
    for banned in ("PROFITABLE", "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned
    nra = d16.get_candidate_16_detector_dry_run_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C16_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"
    for banned in ("PAPER", "LIVE", "EXECUTE", "BROKER", "ORDER", "FETCH",
                   "REPLAY"):
        assert banned not in nra.upper(), banned


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(d16.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "smtplib",
              "subprocess", "websockets", "aiohttp", "schedule", "threading",
              "asyncio", "telegram", "csv", "hashlib", "os", "io", "shutil",
              "ssl", "ftplib", "pathlib", "datetime", "random", "math",
              "statistics", "numpy"}
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

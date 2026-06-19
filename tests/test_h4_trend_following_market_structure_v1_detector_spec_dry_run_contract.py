"""Tests for the Candidate #18 detector-spec + synthetic dry-run contract
(h4_trend_following_market_structure_v1).

Verifies: research-only, synthetic-only (NO real data / NO XAUUSD / NO cost), executes
nothing; chain-gated on the frozen C18 candidate spec; the detector implements the
frozen spec rules (K=2 pivots, HH+HL uptrend, long pullback entry on a confirmed
higher-low, structural stop, structure-shift / stop exit, profit-confirmed
add-to-winners never to losers, max 3 units, one position per symbol, no indicators);
the synthetic dry-run proves all of these behaviours on deterministic fixtures
(uptrend / range / downtrend / loser / strong_uptrend); downstream gates locked;
capability flags + scope locks; validator anti-tamper; module purity; determinism."""
from __future__ import annotations

import ast

import sparta_commander.h4_trend_following_market_structure_v1_detector_spec_dry_run_contract as d18  # noqa: E501


_R = d18.build_c18_detector_dry_run(".", [])


def test_dry_run_frozen_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_synthetic_dry_run_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"] == "C18_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
    assert d18.validate_c18_detector_dry_run(_R)["valid"] is True


def test_candidate_identity():
    assert _R["candidate_id"] == "C18"
    assert _R["candidate_family"] == "h4_trend_following_market_structure"


def test_chain_gated_on_frozen_spec():
    assert _R["spec_verdict"] == "C18_SPEC_FROZEN_FOR_HUMAN_REVIEW"
    assert _R["spec_valid"] is True
    bad = {**_R, "spec_verdict": "C18_SPEC_BLOCKED"}
    assert d18.validate_c18_detector_dry_run(bad)["valid"] is False


def test_synthetic_only_no_real_data_no_xauusd_no_cost():
    assert _R["uses_synthetic_fixtures_only"] is True
    assert _R["uses_real_data"] is False
    assert _R["uses_xauusd"] is False
    assert _R["cost_model_applied_here"] is False
    assert _R["cost_model_reserved_for_replay"] is True
    assert _R["all_in_round_trip_bps_reserved"] == 37.0
    assert _R["fetches_data"] is False
    assert _R["uses_real_candles"] is False
    for bad_key in ("uses_real_data", "uses_xauusd"):
        bad = {**_R, bad_key: True}
        assert d18.validate_c18_detector_dry_run(bad)["valid"] is False, bad_key


def test_frozen_spec_params_implemented():
    assert _R["timeframe"] == "H4"
    assert _R["swing_pivot_strength_k"] == 2
    assert _R["stop_buffer_frac"] == 0.0015
    assert _R["max_units_total"] == 3
    assert _R["min_bars_between_entries"] == 6
    assert _R["max_concurrent_positions_per_symbol"] == 1
    assert _R["uses_indicators"] is False
    assert _R["is_h4_market_structure"] is True
    bad = {**_R, "uses_indicators": True}
    assert d18.validate_c18_detector_dry_run(bad)["valid"] is False


# ---- the synthetic behaviour checks (the whole point) ----------------------

def test_all_synthetic_checks_pass():
    checks = _R["dry_run_checks"]
    for k in ("deterministic", "uptrend_detected_long_entry", "no_trade_in_range",
              "no_long_entry_in_downtrend", "structural_stop_below_anchor",
              "exit_on_structure_shift_or_stop", "pyramids_only_on_profit_higher_low",
              "never_adds_to_losers", "max_three_units", "spacing_min_6_bars",
              "one_position_per_symbol", "no_indicators_used",
              "cost_model_not_applied", "synthetic_only_no_real_data"):
        assert checks[k] is True, k
    assert _R["dry_run_all_checks_pass"] is True
    bad = {**_R, "dry_run_checks": {**checks, "never_adds_to_losers": False}}
    assert d18.validate_c18_detector_dry_run(bad)["valid"] is False


def test_fixtures_cover_the_rules():
    assert set(_R["synthetic_fixtures"]) == {
        "uptrend", "range", "downtrend", "loser", "strong_uptrend"}
    dry = d18.run_synthetic_dry_run()
    res = dry["results"]
    # range -> no trade; downtrend -> no long entry
    assert len(res["range"]["trades"]) == 0
    assert len(res["downtrend"]["trades"]) == 0
    # uptrend -> one trade with profit-confirmed adds
    up = res["uptrend"]["trades"]
    assert len(up) == 1
    assert up[0]["units"] >= 2 and len(up[0]["adds"]) >= 1
    assert all(a["in_profit"] for a in up[0]["adds"])
    # loser -> one trade, ZERO adds (never add to a loser)
    loser = res["loser"]["trades"]
    assert len(loser) == 1 and len(loser[0]["adds"]) == 0
    # strong uptrend -> capped at 3 units
    assert max(t["units"] for t in res["strong_uptrend"]["trades"]) == 3
    # one position per symbol everywhere
    assert all(r["max_concurrent_positions"] <= 1 for r in res.values())


def test_structural_stop_below_anchor():
    dry = d18.run_synthetic_dry_run()
    for name in ("uptrend", "loser", "strong_uptrend"):
        for t in dry["results"][name]["trades"]:
            assert t["stop"] < t["anchor"]
            assert abs(t["stop"] - t["anchor"] * (1 - 0.0015)) < 1e-6


def test_max_units_capped_at_three():
    assert _R["dry_run_max_units_observed"] <= 3
    bad = {**_R, "dry_run_max_units_observed": 5}
    assert d18.validate_c18_detector_dry_run(bad)["valid"] is False


def test_determinism():
    a = d18.run_synthetic_dry_run()
    b = d18.run_synthetic_dry_run()
    assert a["results"]["uptrend"]["trades"] == b["results"]["uptrend"]["trades"]
    assert a["checks"]["deterministic"] is True


def test_anti_loop_and_next_gate():
    assert _R["candidate_not_in_rejected_ledger"] is True
    assert _R["rejected_families_count"] == 22
    nra = d18.get_candidate_18_detector_dry_run_next_action()
    assert nra == _R["next_required_action"]
    assert nra == "HUMAN_DECISION_C18_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"
    for banned in ("PAPER", "LIVE", "BROKER", "ORDER", "REPLAY", "PNL", "FETCH"):
        assert banned not in nra.upper(), banned
    bad = {**_R, "rejected_families_count": 21}
    assert d18.validate_c18_detector_dry_run(bad)["valid"] is False


def test_downstream_gates_locked():
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
        bad = {**_R, gate: False}
        assert d18.validate_c18_detector_dry_run(bad)["valid"] is False, gate


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in d18._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = {**_R, flag: True}
        assert d18.validate_c18_detector_dry_run(bad)["valid"] is False, flag


def test_scope_locks_all_true():
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    for must in ("no_data_fetch", "no_real_candles", "no_xauusd", "no_labels",
                 "no_replay", "no_pnl", "no_cost_application", "no_optimization",
                 "no_indicators", "no_add_to_losers", "no_overlapping_positions",
                 "no_commit", "no_push", "no_paper_trading", "no_live_trading"):
        assert _R["scope_locks"][must] is True, must


def test_label_no_profitability_claim():
    label = d18.get_candidate_18_detector_dry_run_label()
    assert "RESEARCH ONLY" in label
    assert "SYNTHETIC" in label
    assert "NOT a profitability claim" in label or (
        "NOT A PROFITABILITY" in label.upper())
    for banned in ("PROFITABLE STRATEGY", "EDGE CONFIRMED", "READY FOR LIVE"):
        assert banned not in label.upper(), banned


def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(d18.__file__, encoding="utf-8").read()
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "rmdir",
                 "rename", "touch(", "open("):
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

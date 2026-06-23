"""Tests for the per-strike options data phase PLAN.

Proves the record is PURE / PLAN-ONLY: states free public data is INSUFFICIENT and paid/forward
is required (PAID primary, FORWARD fallback); lists the required per-strike fields (incl. IV +
delta/gamma/vega/theta); is BTC-first; defines the MVP delta-hedged backtest design with hard
tail gates + cost model + no-optimization (design-only, not run); lists crash windows (incl.
March-2020 paid-only); FETCHES/BUYS NOTHING; activates/promotes nothing and changes no
C22/C23/C24/funding-selection/ledger/lifecycle state; pins every capability flag False."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.per_strike_options_data_phase_plan_v1_contract as ps

_R = ps.build_per_strike_options_phase_plan()


def test_builds_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_plan_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"].startswith("PER_STRIKE_OPTIONS_DATA_PHASE_PLANNED")
    assert ps.validate_per_strike_options_phase_plan(_R)["valid"] is True


def test_free_insufficient_paid_or_forward():
    assert _R["free_data_sufficient"] is False
    assert _R["is_feasible_with_free_data"] is False
    assert _R["paid_or_forward_required"] is True
    paths = {p["path"]: p for p in _R["data_paths"]}
    assert paths["paid_historical"]["recommended_primary"] is True
    assert paths["paid_historical"]["covers_march_2020"] is True
    assert "forward_only_daily_snapshots" in paths
    assert paths["forward_only_daily_snapshots"]["recommended_primary"] is False
    assert "limited_public_approximation" in paths


def test_required_fields_incl_greeks():
    rf = _R["required_fields"]
    assert "implied_vol(mark_iv)" in rf
    for g in ("greeks.delta", "greeks.gamma", "greeks.vega", "greeks.theta"):
        assert g in rf
    assert "strike" in rf and "option_type(call/put)" in rf and "expiration_timestamp" in rf


def test_btc_first_and_mvp_design():
    assert _R["btc_first_scope"]["primary"] == "BTC"
    m = _R["mvp_backtest_design"]
    assert m["scope"] == "BTC only first"
    assert m["no_optimization"] is True
    assert m["is_design_only_not_run"] is True
    assert m["hard_tail_gates"] and m["cost_model"]
    assert "delta-hedged" in m["structure"]


def test_crash_windows_march_2020_paid_only():
    cw = {c["window"]: c for c in _R["crash_stress_windows"]}
    m20 = [c for w, c in cw.items() if "2020-03" in w]
    assert m20 and "paid" in m20[0]["coverable"].lower()
    assert any("FTX" in w or "2022-11" in w for w in cw)
    assert any("2021-05" in w for w in cw)


def test_layout_and_probe_finding():
    assert _R["proposed_data_dir"].startswith("data/deribit_options")
    assert _R["data_will_be_gitignored"] is True
    assert "last-expiry" in _R["probe_finding"].lower() or "no multi-year" in _R["probe_finding"].lower()
    assert _R["no_existing_per_strike_infra"] is True


def test_fetches_buys_nothing_and_preserves_state():
    for k in ("fetches_nothing_in_this_phase", "buys_nothing_in_this_phase", "activates_nothing",
              "c22_unchanged", "c23_c24_not_reactivated", "funding_selection_not_reactivated",
              "does_not_modify_official_ledger", "does_not_modify_lifecycle",
              "does_not_modify_lane_status", "data_procurement_gate_locked", "backtest_gate_locked"):
        assert _R[k] is True, k
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_CHOOSE_PER_STRIKE_OPTIONS_DATA_PATH_PAID_OR_FORWARD_FOR_BTC_VRP")


def test_capabilities_false_and_tamper_rejected():
    for flag in ps._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        assert ps.validate_per_strike_options_phase_plan({**_R, flag: True})["valid"] is False
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    # cannot flip free->sufficient, drop the buys-nothing flag, or claim deployment-grade
    assert ps.validate_per_strike_options_phase_plan(
        {**_R, "free_data_sufficient": True})["valid"] is False
    assert ps.validate_per_strike_options_phase_plan(
        {**_R, "buys_nothing_in_this_phase": False})["valid"] is False
    assert ps.validate_per_strike_options_phase_plan(
        {**_R, "is_deployment_grade": True})["valid"] is False


def test_module_purity():
    src = Path(ps.__file__).read_text(encoding="utf-8")
    assert "__main__" not in src
    for verb in ("write_bytes", "write_text", "unlink", "mkdir", "open(",
                 "subprocess", "urlopen", "urllib", "requests.", "json.load", "read_text"):
        assert verb not in src, verb
    tree = ast.parse(src)
    banned = {"urllib", "requests", "socket", "http", "ccxt", "subprocess",
              "os", "io", "shutil", "json", "hashlib", "pathlib", "numpy", "pandas"}
    imported = {n.name.split(".")[0] for node in ast.walk(tree)
                if isinstance(node, ast.Import) for n in node.names} | {
        node.module.split(".")[0] for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module}
    assert not (imported & banned), imported & banned

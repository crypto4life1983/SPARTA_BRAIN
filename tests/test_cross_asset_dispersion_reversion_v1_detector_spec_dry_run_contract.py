"""Tests for the Candidate #11 detector spec + synthetic dry-run contract
(cross_asset_dispersion_reversion_v1).

Synthetic fixtures only. Proves the eight required dry-run cases:
  1. valid laggard setup accepted,
  2. no setup when z-score threshold fails,
  3. no setup when basket regime filter fails,
  4. no setup when only one asset exists (hard ValueError),
  5. no calendar/weekday trigger exists (bars carry no date/weekday),
  6. no labels/replay/data-fetch/trading occurs,
  7. invalid stop or below 81 bps floor is rejected,
  8. detector is deterministic.
Also: chain-gate on the READY C11 spec; the C10 early-generalization battery
stays locked for the later labels/replay stage; AST/purity green."""
from __future__ import annotations

import ast
import copy
import inspect
import subprocess
import sys

import sparta_commander.cross_asset_dispersion_reversion_v1_detector_spec_dry_run_contract as c11d  # noqa: E501


def _tracked_paths():
    return subprocess.check_output(
        ["git", "ls-files"]).decode("utf-8").splitlines()


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
    _R = c11d.build_candidate_11_detector_spec_dry_run(".", _tracked_paths())
finally:
    for _mod, _attr, _orig in _memo_restore:
        setattr(_mod, _attr, _orig)


# ---- chain gate + verdict --------------------------------------------------

def test_dry_run_ready_and_validates():
    assert _R["verdict"] == c11d.VERDICT_C11DD_READY
    assert _R["blockers"] == []
    assert _R["spec_verdict"] == c11d.VERDICT_C11S_READY
    assert c11d.validate_candidate_11_detector_spec_dry_run(_R)["valid"] is True


# ---- the 8 required dry-run proofs ----------------------------------------

def test_proof_1_valid_laggard_accepted():
    assert _R["dry_run_proofs"]["valid_laggard_setup_accepted"] is True
    acc = _R["dry_run"]["valid_laggard_accepted"]
    assert acc["status"] == "accepted_for_replay_review"
    assert acc["laggard_symbol"] == "SOLUSD"
    assert acc["laggard_z"] <= -1.0
    assert acc["basket_regime_ok"] is True


def test_proof_2_no_setup_when_zscore_fails():
    assert _R["dry_run_proofs"]["no_setup_when_zscore_threshold_fails"] is True
    assert _R["dry_run"]["zscore_threshold_fail_setup_count"] == 0
    assert _R["dry_run"]["zscore_threshold_fail_accepted"] is False


def test_proof_3_no_setup_when_regime_fails():
    assert _R["dry_run_proofs"]["no_setup_when_basket_regime_fails"] is True
    assert _R["dry_run"]["basket_regime_fail_accepted"] is False


def test_proof_4_no_setup_when_single_asset():
    assert _R["dry_run_proofs"]["no_setup_when_single_asset"] is True
    import pytest
    with pytest.raises(ValueError):
        c11d.scan_c11_setups(c11d.fixture_single_asset())


def test_proof_5_no_calendar_or_weekday_trigger():
    assert _R["dry_run_proofs"]["no_calendar_or_weekday_trigger"] is True
    # STRUCTURAL: bars carry NO date and NO weekday field at all, so a
    # calendar/weekday trigger is impossible.
    bars = c11d.fixture_valid_laggard_accepted()["BTCUSD"]
    assert set(bars[0].keys()) == {"open", "high", "low", "close"}
    # CODE-LEVEL: the detector never accesses a date/weekday field or calls a
    # weekday function (checked as code-access patterns, not docstring prose).
    src = open(c11d.__file__, encoding="utf-8").read()
    for tok in ('["date"]', "['date']", '["weekday"]', "['weekday']",
                '["iso_weekday"]', "['iso_weekday']", ".isoweekday(",
                ".weekday(", "import datetime", "from datetime"):
        assert tok not in src, tok


def test_proof_6_no_labels_replay_data_fetch_trading():
    assert _R["dry_run_proofs"]["no_labels_replay_data_fetch_trading"] is True
    src = open(c11d.__file__, encoding="utf-8").read()
    for tok in ("open(", "requests", "urllib", "socket", "ccxt", "binance",
                "subprocess", "place_order", "create_order"):
        assert tok not in src, tok


def test_proof_7_invalid_stop_or_below_floor_rejected():
    assert _R["dry_run_proofs"]["invalid_stop_or_below_floor_rejected"] is True
    assert _R["dry_run"]["below_floor_status"] == "rejected_geometry_floor"
    # invalid stop branch (atr=0) is also rejected
    st = c11d.compute_stop(100.0, 0.0)
    assert st["valid"] is False


def test_proof_8_deterministic():
    assert _R["dry_run_proofs"]["deterministic"] is True
    a = c11d.run_c11_detector_dry_run()
    b = c11d.run_c11_detector_dry_run()
    assert a == b


# ---- detector geometry intact ---------------------------------------------

def test_detector_geometry_constants():
    assert _R["z_entry_threshold"] == -1.0
    assert _R["dispersion_lookback_bars"] == 5
    assert _R["basket_sma_length"] == 50
    assert _R["atr_length"] == 14
    assert _R["structure_stop_atr_multiplier"] == 1.5
    assert _R["target_variants"] == ["2r", "3r", "4r"]
    assert _R["target_distance_floor_bps"] == 81.0
    assert set(_R["symbol_universe"]) == {"BTCUSD", "ETHUSD", "SOLUSD"}
    assert _R["min_assets"] == 3
    assert _R["is_single_asset_edge"] is False


def test_cross_sectional_z_is_relative_not_long_drift():
    # the z-scores are relative (sum ~ 0); the laggard is the most negative
    zs = _R["dry_run"]["valid_laggard_accepted"]["cross_sectional_z"]
    assert abs(sum(zs)) < 1e-6
    assert min(zs) <= -1.0


# ---- C10 lesson: early generalization battery stays locked -----------------

def test_early_generalization_battery_locked_for_later_stage():
    battery = _R["early_generalization_battery_locked_for_labels_replay"]
    for chk in ("cross_weekday_neutrality_required_early",
                "cross_asset_multiple_laggards_required_early",
                "forward_oos_continuation_required_early",
                "cross_regime_bull_bear_chop_stability_required_early"):
        assert chk in battery, chk


# ---- locks + capability flags ----------------------------------------------

def test_all_execution_gates_locked():
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "data_fetch_gate_locked", "robustness_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        assert _R[gate] is True, gate
    for lock in ("synthetic_fixtures_only", "no_real_data", "no_data_fetch",
                 "no_labels", "no_replay", "no_portfolio_compute",
                 "no_calendar_trigger", "no_single_asset_edge",
                 "no_paper_live_readiness_claim"):
        assert _R["scope_locks"][lock] is True, lock


def test_capability_flags_all_false_and_tamper_rejected():
    for flag in c11d._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        bad = copy.deepcopy(_R)
        bad[flag] = True
        assert c11d.validate_candidate_11_detector_spec_dry_run(
            bad)["valid"] is False, flag


def test_validator_rejects_tampered_proof():
    bad = copy.deepcopy(_R)
    bad["dry_run_proofs"]["valid_laggard_setup_accepted"] = False
    assert c11d.validate_candidate_11_detector_spec_dry_run(bad)["valid"] is False
    bad2 = copy.deepcopy(_R)
    bad2["z_entry_threshold"] = 0.0
    assert c11d.validate_candidate_11_detector_spec_dry_run(bad2)["valid"] is False


def test_label_no_readiness_claim():
    label = c11d.get_candidate_11_detector_dry_run_label()
    assert "SYNTHETIC FIXTURES ONLY" in label
    assert "NO real data" in label or "NO REAL DATA" in label.upper()
    for banned in ("APPROVED FOR PAPER", "APPROVED FOR LIVE", "PROFITABLE",
                   "EDGE CONFIRMED", "GUARANTEE"):
        assert banned not in label.upper(), banned


def test_next_action():
    assert _R["next_required_action"] == (
        "HUMAN_DECISION_C11_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")


# ---- chain blocks when spec not ready --------------------------------------

def test_chain_blocks_when_spec_not_ready(monkeypatch):
    monkeypatch.setattr(c11d, "build_candidate_11_spec",
                        lambda repo_root, tracked: {"verdict": "NOPE"})
    blocked = c11d.build_candidate_11_detector_spec_dry_run(".", [])
    assert blocked["verdict"] == c11d.VERDICT_C11DD_BLOCKED
    assert "spec_not_ready" in blocked["blockers"]


# ---- module purity ---------------------------------------------------------

def test_module_purity_no_io_no_main_no_banned_imports():
    src = open(c11d.__file__, encoding="utf-8").read()
    assert "__main__" not in src
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

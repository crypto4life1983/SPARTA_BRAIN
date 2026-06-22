"""Tests for the options/implied-vol data phase PLAN.

Proves the record is PURE / PLAN-ONLY: names the PUBLIC Deribit endpoints (never /private/) and
requires a NEW bounded fetcher; proposes BTC/ETH + the phased free(Phase1)/paid(Phase2)
feasibility; specifies required fields (incl. implied_vol + delta), a frozen gitignored dir,
data-quality risks (DVOL pre-history gap + index-vs-tradeable proxy), and crash-stress windows
(incl. the March-2020 DVOL gap and FTX); fetches NOTHING; activates/promotes nothing and changes
no C22/C23/C24/funding-selection/ledger/lifecycle state; pins every capability flag False."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.options_iv_data_phase_plan_v1_contract as op

_R = op.build_options_iv_phase_plan()


def test_builds_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_plan_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"].startswith("OPTIONS_IV_DATA_PHASE_PLANNED")
    assert op.validate_options_iv_phase_plan(_R)["valid"] is True


def test_public_deribit_source_no_private():
    for e in _R["public_endpoints"]:
        assert e.startswith("https://www.deribit.com/api/v2/public/")
        assert "/private/" not in e
    assert _R["dvol_endpoint"].endswith("get_volatility_index_data")
    assert _R["uses_public_endpoints_only"] is True
    assert _R["must_not_use_private_endpoints"] is True
    assert _R["requires_new_bounded_fetcher"] is True
    assert _R["no_existing_options_iv_infra"] is True


def test_symbols_and_phased_feasibility():
    assert set(_R["proposed_symbols"]) == {"BTC", "ETH"}
    assert _R["phase_1"]["free"] is True and _R["phase_1"]["feasible"] is True
    assert _R["phase_2"]["free"] is False
    assert _R["paid_data_likely_for_phase_2"] is True
    assert _R["proposed_date_range"]["start"] == "2021-03-24"


def test_required_fields_present():
    full = _R["required_fields_full_vrp"]
    assert "implied_vol(mark_iv)" in full
    assert any("delta" in f for f in full)
    assert "strike" in full and "option_type(call/put)" in full and "expiration_timestamp" in full


def test_risks_and_crash_windows():
    risks = " ".join(_R["data_quality_risks"]).upper()
    assert "DVOL" in risks and "PROXY" in risks
    cw = _R["crash_stress_windows"]
    march = [c for c in cw if "2020-03" in c["window"]]
    assert march and march[0]["in_dvol"] is False        # March-2020 DVOL gap flagged
    assert any("FTX" in c["window"] or "2022-11" in c["window"] for c in cw)
    assert any("2021-05" in c["window"] for c in cw)


def test_frozen_layout_and_gitignore():
    assert _R["proposed_data_dir"].startswith("data/deribit_iv")
    assert "dvol_close" in _R["proposed_csv_fields_phase1"]
    assert _R["data_will_be_gitignored"] is True
    assert _R["no_forward_fill"] is True


def test_fetches_nothing_and_preserves_state():
    for k in ("fetches_nothing_in_this_phase", "activates_nothing", "c22_unchanged",
              "c23_c24_not_reactivated", "funding_selection_not_reactivated",
              "does_not_modify_official_ledger", "does_not_modify_lifecycle",
              "does_not_modify_lane_status", "full_fetch_gate_locked"):
        assert _R[k] is True, k
    assert _R["next_required_action"] == (
        "HUMAN_APPROVED_CREATE_BOUNDED_DERIBIT_DVOL_IV_INDEX_FETCHER_AND_ASSEMBLE_FROZEN_DATA_ONLY")


def test_capabilities_false_and_tamper_rejected():
    for flag in op._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        assert op.validate_options_iv_phase_plan({**_R, flag: True})["valid"] is False
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    # cannot mark phase 2 free, drop the March-2020 gap flag, or claim deployment-grade
    assert op.validate_options_iv_phase_plan(
        {**_R, "phase_2": {**_R["phase_2"], "free": True}})["valid"] is False
    assert op.validate_options_iv_phase_plan(
        {**_R, "is_deployment_grade": True})["valid"] is False
    assert op.validate_options_iv_phase_plan(
        {**_R, "fetches_nothing_in_this_phase": False})["valid"] is False


def test_module_purity():
    src = Path(op.__file__).read_text(encoding="utf-8")
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

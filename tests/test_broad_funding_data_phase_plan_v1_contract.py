"""Tests for the broad multi-asset funding data phase PLAN.

Proves the record is PURE / PLAN-ONLY: names the PUBLIC Binance funding endpoint and requires a
NEW bounded fetcher (never widening the 3-symbol carry fetcher); proposes the 40-symbol
perp-available allowlist (EOS/MKR excluded) aligned to the 42-symbol OHLCV universe; specifies a
frozen gitignored dir / manifest / quality report / CSV fields with per-symbol funding-interval
capture and no forward-fill; discloses survivorship + non-8h-interval risks; fetches NOTHING;
activates/promotes nothing and changes no C22/C23/C24/ledger/lifecycle state; pins every
capability flag False."""
from __future__ import annotations

import ast
from pathlib import Path

import sparta_commander.broad_funding_data_phase_plan_v1_contract as fp

_R = fp.build_funding_phase_plan()


def test_builds_and_validates():
    assert _R["mode"] == "RESEARCH_ONLY"
    assert _R["is_plan_only"] is True
    assert _R["blockers"] == []
    assert _R["verdict"].startswith("BROAD_FUNDING_DATA_PHASE_PLANNED_AND_FEASIBLE")
    assert fp.validate_funding_phase_plan(_R)["valid"] is True


def test_public_source_and_no_widening():
    assert _R["funding_endpoint"] == "https://fapi.binance.com/fapi/v1/fundingRate"
    assert _R["uses_public_endpoint_only"] is True
    assert _R["must_not_widen_3_symbol_carry_fetcher"] is True
    assert _R["requires_new_bounded_fetcher"] is True
    assert _R["existing_funding_tool"] == "tools/crypto_basis_funding_public_fetch_once.py"


def test_allowlist_40_perp_available_eos_mkr_excluded():
    al = _R["proposed_funding_allowlist"]
    assert len(al) == 40
    assert "EOSUSDT" not in al and "MKRUSDT" not in al
    assert set(_R["excluded_symbols"]) == {"EOSUSDT", "MKRUSDT"}
    assert len(al) + len(_R["excluded_symbols"]) == 42
    assert _R["aligned_to_broad_ohlcv_universe"] is True
    # the excluded reasons cite delisting / no current perp
    for sym, reason in _R["excluded_symbols"].items():
        assert "perp" in reason.lower()


def test_frozen_layout_and_interval_capture():
    assert _R["proposed_data_dir"].startswith("data/broad_crypto_funding")
    assert "funding_rate" in _R["proposed_csv_fields"]
    assert _R["captures_per_symbol_funding_interval"] is True  # the non-8h mitigation
    assert _R["no_forward_fill"] is True
    assert _R["data_will_be_gitignored"] is True
    assert _R["proposed_date_range"] == {"start": "2021-01-01", "end": "2026-06-21"}


def test_risks_disclosed():
    risks = " ".join(_R["data_quality_risks"]).upper()
    assert "SURVIVORSHIP" in risks
    assert "8H" in risks or "INTERVAL" in risks   # non-uniform funding cadence
    assert _R["is_feasible"] is True
    assert _R["is_survivorship_free"] is False
    assert _R["is_deployment_grade"] is False


def test_fetches_nothing_and_preserves_state():
    for k in ("fetches_nothing_in_this_phase", "activates_nothing", "c22_unchanged",
              "c23_c24_not_reactivated", "does_not_modify_official_ledger",
              "does_not_modify_lifecycle", "does_not_modify_lane_status",
              "full_fetch_gate_locked"):
        assert _R[k] is True, k
    assert _R["next_required_action"] == (
        "HUMAN_APPROVED_CREATE_BOUNDED_BROAD_FUNDING_FETCHER_AND_ASSEMBLE_FROZEN_DATA_ONLY")


def test_capabilities_false_and_tamper_rejected():
    for flag in fp._CAPABILITY_FLAGS_FALSE:
        assert _R[flag] is False, flag
        assert fp.validate_funding_phase_plan({**_R, flag: True})["valid"] is False
    for key, val in _R["scope_locks"].items():
        assert val is True, key
    # cannot widen allowlist to include the delisted pair, nor claim survivorship-free, nor fetch
    bad_al = list(_R["proposed_funding_allowlist"]) + ["EOSUSDT"]
    assert fp.validate_funding_phase_plan(
        {**_R, "proposed_funding_allowlist": bad_al})["valid"] is False
    assert fp.validate_funding_phase_plan(
        {**_R, "is_survivorship_free": True})["valid"] is False
    assert fp.validate_funding_phase_plan(
        {**_R, "fetches_nothing_in_this_phase": False})["valid"] is False


def test_module_purity():
    src = Path(fp.__file__).read_text(encoding="utf-8")
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

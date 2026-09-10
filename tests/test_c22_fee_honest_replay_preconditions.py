"""C22 fee-honest replay precondition shell: fail-closed today, every blocker enumerated,
per-instrument evidence evaluation follows the B2/B3 hierarchy, present-day availability rejected."""
from __future__ import annotations

import importlib
import json

import sparta_commander.c22_execution_data_short_instrument_feasibility_contract as X
import sparta_commander.c22_historical_evidence_acquisition_plan_contract as B3

fr = importlib.import_module("tools.c22_fee_honest_replay_once")


def test_preconditions_enumerate_every_blocker_and_fail_closed_today():
    p = fr.check_preconditions()
    for k in ("replay_spec_accepted", "forward_exit_contract_accepted", "execution_data_contract_accepted",
              "dry_run_accepted", "short_instrument_selected", "cost_base_case_frozen", "weekend_session_rule_ruled",
              "basis_alignment_reviewed", "historical_evidence_admitted", "all_required_instruments_evidenced", "all_satisfied"):
        assert k in p
    assert p["all_satisfied"] is False and p["fee_honest_replayable_trades_now"] == 0
    assert p["instruments_required"] >= 22 and p["short_instruments_required"] == 22
    assert p["instruments_with_admitted_evidence"] == 0
    assert "short_instrument_selected" in p["unsatisfied"] and "cost_base_case_frozen" in p["unsatisfied"]


def test_cost_components_are_the_contract_ones():
    assert fr.COST_COMPONENTS == X.COST_COMPONENTS and fr.RESULT_LEVELS == X.COST_RESULT_LEVELS
    assert fr.SENSITIVITY_37BPS == X.THIRTY_SEVEN_BPS_STATUS == "SENSITIVITY_CASE_NOT_BASE_CASE"
    assert fr.DECISIVE_MIN_TIER == B3.DECISIVE_MIN_TIER and fr.SOURCE_TIERS == tuple(B3.SOURCE_HIERARCHY)


def _manifest(fields, tier="T1_OFFICIAL_VENUE_HISTORICAL_FILES_OR_OFFICIAL_API_DOCS", admitted=True, basis="HISTORICAL_RECORD"):
    m = {f: {"source_tier": tier, "sha256": "ab" * 32, "evidence_basis": basis} for f in fields}
    if admitted:
        m["admission_token"] = fr.GATE_TOKENS["historical_evidence_admitted"]
    return m


def test_instrument_evidence_fail_closed_missing_manifest(tmp_path, monkeypatch):
    monkeypatch.setattr(fr, "MANIFEST_DIR", tmp_path)
    inst = {"symbol": "BINANCE:TRXUSDT", "sides": ["SHORT"]}
    e = fr.evaluate_instrument_evidence(inst)
    assert e["manifest_present"] is False and e["satisfied"] is False
    assert set(e["missing"]) == set(fr.EVIDENCE_FIELDS_ALL) | set(fr.EVIDENCE_FIELDS_SHORT_ONLY)


def test_instrument_evidence_satisfied_only_with_all_fields_decisive_tier_and_admission(tmp_path, monkeypatch):
    monkeypatch.setattr(fr, "MANIFEST_DIR", tmp_path)
    inst = {"symbol": "BINANCE:TRXUSDT", "sides": ["SHORT"]}
    path = fr._manifest_path(inst["symbol"])
    fields = list(fr.EVIDENCE_FIELDS_ALL) + list(fr.EVIDENCE_FIELDS_SHORT_ONLY)
    path.write_text(json.dumps(_manifest(fields)), encoding="utf-8")
    assert fr.evaluate_instrument_evidence(inst)["satisfied"] is True
    # non-decisive tier (T5) -> not satisfied
    path.write_text(json.dumps(_manifest(fields, tier="T5_UNSUPPORTED_THIRD_PARTY_EXPLORATORY_ONLY_NOT_DECISIVE")), encoding="utf-8")
    e = fr.evaluate_instrument_evidence(inst)
    assert e["satisfied"] is False and len(e["non_decisive_tier"]) == len(fields)
    # present-day availability offered as proof -> rejected
    path.write_text(json.dumps(_manifest(fields, basis="PRESENT_DAY_AVAILABILITY")), encoding="utf-8")
    e = fr.evaluate_instrument_evidence(inst)
    assert e["satisfied"] is False and len(e["present_day_only_rejected"]) == len(fields)
    # missing admission token -> not satisfied
    path.write_text(json.dumps(_manifest(fields, admitted=False)), encoding="utf-8")
    assert fr.evaluate_instrument_evidence(inst)["satisfied"] is False
    # long-only instrument needs no shortability/funding fields
    long_inst = {"symbol": "COINBASE:AEROUSD", "sides": ["LONG"]}
    fr._manifest_path(long_inst["symbol"]).write_text(json.dumps(_manifest(list(fr.EVIDENCE_FIELDS_ALL))), encoding="utf-8")
    assert fr.evaluate_instrument_evidence(long_inst)["satisfied"] is True


def test_main_refuses_even_with_exact_token_while_preconditions_unsatisfied(capsys):
    fr.main(["--advance-token", fr.ADVANCE_TOKEN])
    out = json.loads(capsys.readouterr().out)
    assert out["result"] == "REPLAY_BLOCKED_PRECONDITIONS_UNSATISFIED" and out["advance_token_exact"] is True
    assert out["cost_base_case"] == "C22_COST_BASE_CASE_NOT_FROZEN"

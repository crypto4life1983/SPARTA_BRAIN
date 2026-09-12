"""C22 fee-honest replay precondition shell: fail-closed today, every blocker enumerated,
per-instrument evidence evaluation follows the B2/B3 hierarchy, present-day availability rejected."""
from __future__ import annotations

import importlib
import json

import sparta_commander.c22_execution_data_short_instrument_feasibility_contract as X
import sparta_commander.c22_historical_evidence_acquisition_plan_contract as B3

fr = importlib.import_module("tools.c22_fee_honest_replay_once")


def test_preconditions_enumerate_every_gate_and_report_exclusions():
    p = fr.check_preconditions()
    for k in ("replay_spec_accepted", "forward_exit_contract_accepted", "execution_data_contract_accepted",
              "dry_run_accepted", "short_instrument_selected", "cost_base_case_frozen", "weekend_session_rule_ruled",
              "basis_alignment_reviewed", "historical_evidence_admitted", "all_required_instruments_evidenced",
              "all_satisfied", "governance_excluded_instruments"):
        assert k in p
    ex = {x["symbol"]: x for x in fr.excluded_instruments()}
    assert set(ex) == {"BYBIT:TELUSDT", "COINBASE:MORPHOUSD"}
    assert ex["BYBIT:TELUSDT"]["remaining_sides"] == [] and ex["COINBASE:MORPHOUSD"]["remaining_sides"] == ["LONG"]
    for x in ex.values():
        assert "Stage One" in x["basis"] or "HOME_VENUE_ONLY" in x["basis"]
    req = {i["symbol"]: i for i in fr.required_instruments()}
    assert "BYBIT:TELUSDT" not in req and req["COINBASE:MORPHOUSD"]["sides"] == ["LONG"]
    # 22 short instruments in the frozen cohort, less the two terminally excluded by governance
    assert p["instruments_required"] >= 22 and p["short_instruments_required"] == 20
    # every required instrument must be evidenced for the gate to open; none may be skipped
    assert p["instruments_with_admitted_evidence"] == p["instruments_required"]
    assert p["all_required_instruments_evidenced"] is True and not p["unsatisfied"]


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


def test_main_refuses_without_the_exact_advance_token(capsys):
    fr.main(["--advance-token", "HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT=REJECT"])
    out = json.loads(capsys.readouterr().out)
    assert out["result"] == "REPLAY_BLOCKED_PRECONDITIONS_UNSATISFIED" or out["advance_token_exact"] is False
    fr.main([])
    out2 = json.loads(capsys.readouterr().out)
    assert out2["advance_token_supplied"] is False and out2["result"] != "REPLAY_EXECUTED"


def test_shell_itself_never_computes_results():
    """The gate module reports only; results are produced by the separate driver under --compute."""
    import inspect
    src = inspect.getsource(fr.main)
    assert "run_fee_honest_replay" not in src

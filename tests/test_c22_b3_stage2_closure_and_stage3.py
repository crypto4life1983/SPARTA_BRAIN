"""C22 B3 Stage Two governance closure (LEO pair-specific rule, MORPHO/TEL classification) and
Stage Three (frozen step identity, coverage logic, per-signal outcomes, fail-closed)."""
from __future__ import annotations

import importlib

import pytest

import sparta_commander.c22_historical_evidence_acquisition_plan_contract as B3

gc = importlib.import_module("tools.c22_b3_stage2_governance_closure_once")
s3 = importlib.import_module("tools.c22_b3_stage3_historical_ohlc_once")


# --- LEO pair-specific rule ----------------------------------------------------------------------
def _series(short_min=100.0, cred_min=50.0, dates=("2026-07-15", "2026-07-16")):
    return {"pair_short_position_size_1m": {d: {"points": 1440, "min": short_min, "max": short_min + 1} for d in dates},
            "pair_funding_credits_used_1m": {d: {"points": 1440, "min": cred_min, "max": cred_min + 1} for d in dates},
            "pair_short_position_size_1d": {}, "pair_funding_credits_used_1d": {}}


def test_leo_pass_requires_pair_specific_short_positions_and_credits_on_every_date():
    r = gc.leo_verdict(["2026-07-15", "2026-07-16"], _series())
    assert r["verdict"] == "PASS_HISTORICAL_SHORTABILITY"
    assert r["checks"]["present_day_margin_flag_used"] is False and r["checks"]["general_borrow_market_inference_used_as_decisive"] is False


def test_leo_unresolved_when_short_size_zero_or_absent_or_credits_absent():
    s = _series(); s["pair_short_position_size_1m"]["2026-07-16"]["min"] = 0.0
    assert gc.leo_verdict(["2026-07-15", "2026-07-16"], s)["verdict"] == "UNRESOLVED_HISTORICAL_MARGIN_STATE"
    s = _series(); del s["pair_short_position_size_1m"]["2026-07-16"]
    assert gc.leo_verdict(["2026-07-15", "2026-07-16"], s)["verdict"] == "UNRESOLVED_HISTORICAL_MARGIN_STATE"
    s = _series(); s["pair_funding_credits_used_1m"]["2026-07-15"]["min"] = 0.0
    assert gc.leo_verdict(["2026-07-15", "2026-07-16"], s)["verdict"] == "UNRESOLVED_HISTORICAL_MARGIN_STATE"
    assert gc.leo_verdict(["2026-07-15"], {"pair_short_position_size_1m": None, "pair_funding_credits_used_1m": None})["verdict"] == "UNRESOLVED_HISTORICAL_MARGIN_STATE"


def test_closure_classifies_morpho_excluded_tel_preserved_and_never_uses_performance():
    stage2 = {"assets": [
        {"c22_asset": "COINBASE:MORPHOUSD", "per_signal": [{"decision_date": "2026-07-01", "signal": "BEAR_SHORT", "stage1_verdict": "PASS_HISTORICAL_EXISTENCE", "stage2_verdict": "PENDING_VENUE_POLICY", "execution_path_used": None, "passing_instruments": []}]},
        {"c22_asset": "BYBIT:TELUSDT", "per_signal": [{"decision_date": "2026-07-09", "signal": "BEAR_SHORT", "stage1_verdict": "FAIL_WRONG_INSTRUMENT_TYPE", "stage2_verdict": "NOT_EVALUATED_STAGE_ONE_NOT_PASSED", "execution_path_used": None, "passing_instruments": []}]},
        {"c22_asset": "BITFINEX:LEOUSD", "per_signal": [{"decision_date": "2026-07-15", "signal": "BEAR_SHORT", "stage1_verdict": "PASS_HISTORICAL_EXISTENCE", "stage2_verdict": "PASS_HISTORICAL_SHORTABILITY", "execution_path_used": "SPOT_MARGIN_BORROW", "passing_instruments": ["tLEOUSD"]}]},
        {"c22_asset": "BINANCE:TRXUSDT", "per_signal": [{"decision_date": "2026-07-06", "signal": "BEAR_SHORT", "stage1_verdict": "PASS_HISTORICAL_EXISTENCE", "stage2_verdict": "PASS_HISTORICAL_SHORTABILITY", "execution_path_used": "DERIVATIVE_PERPETUAL_OR_FUTURES", "passing_instruments": ["TRXUSDT"]}]},
    ]}
    leo = {"verdict": "UNRESOLVED_HISTORICAL_MARGIN_STATE", "reason": "x", "checks": {}}
    art = gc.build_closure(stage2, leo, [], "T")
    by = {p["c22_asset"]: p["decisive_execution_status"] for p in art["per_signal"]}
    assert by["COINBASE:MORPHOUSD"] == "EXCLUDED_VENUE_POLICY" and by["BYBIT:TELUSDT"] == "ELIMINATED_STAGE_ONE_PRESERVED"
    assert by["BITFINEX:LEOUSD"] == "UNRESOLVED_HISTORICAL_MARGIN_STATE" and by["BINANCE:TRXUSDT"] == "PASS_HISTORICAL_SHORTABILITY"
    assert art["decision_1_venue_policy"]["policy"] == "HOME_VENUE_ONLY"
    assert art["decision_1_venue_policy"]["morpho"]["not_classified_as"] == "instrument_nonexistent"
    assert art["performance_information_consulted"] is False and art["performance_exists"] is False
    assert art["final_stage_two_funnel"]["decisive_executable_short_signals_after_stage_two"] == 1
    assert art["historical_evidence_modified"] is False and art["sealed_reports_rewritten"] is False


# --- Stage Three ------------------------------------------------------------------------------------
def test_stage3_is_exactly_the_frozen_step_four():
    assert s3.FROZEN_STEP == B3.ACQUISITION_ORDER[3] == "4_historical_ohlc"
    assert s3.FROZEN_TOKEN == "HUMAN_DECISION_C22_EXECUTION_OHLC_FETCH_AUTHORIZE"
    assert s3.FROZEN_CATEGORY_PERP in B3.PERP_EVIDENCE_CATEGORIES and s3.FROZEN_CATEGORY_MARGIN in B3.MARGIN_EVIDENCE_CATEGORIES
    assert s3.RANGE_START == B3.MIN_ACQUISITION_RANGE_START == "2026-06-20"
    assert str(s3.OHLC_DIR).replace("\\", "/").endswith(B3.PROPOSED_LAYOUT["ohlc"].rsplit("/<asset>/", 1)[0])


def test_required_end_date_uses_frozen_extension_math_and_last_complete_day():
    h = s3.required_end_date("2026-09-11")
    assert h["extension_index"] == 2 and h["extension_range"]["end"] == "2026-09-13"
    assert h["fetch_end"] == "2026-09-10" and h["required_coverage_end"] == "2026-09-09"
    assert s3.required_end_date("2026-09-20")["fetch_end"] == "2026-09-13"


def test_coverage_detects_gaps_and_malformed_rows():
    rows = [{"date": "2026-07-01", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1},
            {"date": "2026-07-03", "open": 1, "high": None, "low": 1, "close": 1, "volume": 1}]
    c = s3.coverage(rows, "2026-07-01", "2026-07-03")
    assert c["missing_days"] == ["2026-07-02"] and c["malformed_days"] == ["2026-07-03"] and c["complete"] is False
    assert s3.coverage(rows[:1], "2026-07-01", "2026-07-01")["complete"] is True


def test_signal_windows_take_max_across_profiles_and_boundary_when_open():
    dr = {"profiles": {
        "A": {"records": [{"side": "SHORT", "signal_id": "s1", "symbol": "X", "decision_date": "2026-07-01", "exit_date": "2026-07-10", "lifecycle_status": "CLOSED", "entry_date": "2026-07-02", "entry_fill": {"fill_date": "2026-07-02"}},
                          {"side": "LONG", "signal_id": "l1", "symbol": "Y", "decision_date": "2026-07-01", "exit_date": None, "lifecycle_status": "OPEN_AT_END_OF_DATA", "entry_date": "2026-07-02", "entry_fill": {}}]},
        "B": {"records": [{"side": "SHORT", "signal_id": "s1", "symbol": "X", "decision_date": "2026-07-01", "exit_date": None, "lifecycle_status": "OPEN_AT_END_OF_DATA", "entry_date": "2026-07-02", "entry_fill": {"fill_date": "2026-07-02"}}]}}}
    w = s3.signal_windows(dr)
    assert set(w) == {"s1"} and w["s1"]["required_end"] == s3.REPLAY_BOUNDARY


def test_url_allowlist_rejects_non_ohlc_endpoints():
    s3._assert_safe_url("https://fapi.binance.com/fapi/v1/klines?symbol=TRXUSDT")
    for bad in ("https://fapi.binance.com/fapi/v1/fundingRate?symbol=X", "https://fapi.binance.com/fapi/v1/account", "https://api.coingecko.com/x"):
        with pytest.raises(s3.Stage3Error):
            s3._assert_safe_url(bad)


def test_stage3_live_report_if_present_reconciles_and_changes_no_admission():
    files = sorted(s3.REPORT_DIR.glob("c22_b3_stage3_historical_ohlc_*.json")) if s3.REPORT_DIR.exists() else []
    if not files:
        pytest.skip("no sealed stage three report in this checkout")
    import json
    r = json.loads(files[-1].read_bytes().decode("utf-8"))
    assert sum(r["verdict_counts"].values()) == 75 and r["funnel"]["frozen_v2_signals"] == 88
    assert r["funnel"]["fee_honestly_replayable_trades"] == 0 and r["admission_state_changed"] is False
    assert r["c22_performance_computed"] is False and r["next_step_started"] is False
    fr = importlib.import_module("tools.c22_fee_honest_replay_once")
    assert fr.check_preconditions()["all_satisfied"] is False

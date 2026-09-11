"""C22 B3 Stage Four: frozen step identity, fail-closed per-signal verdict (fees/constraints/
liquidity/spread all required), evidence classes, trade-window summary, URL allowlist, and the
sealed live report (if present) reconciles to 75 with no assumption selected."""
from __future__ import annotations

import importlib
import json

import pytest

import sparta_commander.c22_historical_evidence_acquisition_plan_contract as B3

s4 = importlib.import_module("tools.c22_b3_stage4_fees_liquidity_once")


def test_stage_four_is_exactly_frozen_steps_five_and_six():
    assert s4.FROZEN_STEPS == (B3.ACQUISITION_ORDER[4], B3.ACQUISITION_ORDER[5]) == ("5_fee_tick_lot_minimum_rules", "6_liquidity_and_spread_evidence")
    assert s4.FROZEN_TOKEN == "HUMAN_DECISION_C22_FEES_AND_LIQUIDITY_FETCH_AUTHORIZE"
    assert str(s4.FEES_DIR).replace("\\", "/").endswith("c22_short_instrument_evidence/fees")


def _fee(status):
    return {"historical_status": status, "current_status": s4.FEE_CURRENT_ONLY, "class": s4.OBSERVED}


def _con(status):
    return {"historical_status": status, "current_status": s4.CON_CURRENT_ONLY, "class": s4.OBSERVED}


def _liq(status, spread):
    return {"fill_date": "2026-07-06", "trades_status": status, "spread_status": spread}


FILLS = [{"kind": "ENTRY", "date": "2026-07-06", "profile": "A"}]


def test_verdict_pass_only_when_every_frozen_element_is_historically_proven():
    ok = s4.signal_verdict(_fee(s4.FEE_HIST_PROVEN), _con(s4.CON_HIST_PROVEN), FILLS, {"2026-07-06": _liq(s4.LIQ_OBSERVED, s4.SPREAD_DEPTH_PROXY)})
    assert ok["verdict"] == "PASS_STAGE_FOUR" and ok["missing"] == []


def test_verdict_fail_closed_on_each_missing_element_and_current_never_counts():
    assert s4.signal_verdict(_fee(s4.FEE_HIST_UNRESOLVED), _con(s4.CON_HIST_PROVEN), FILLS, {"2026-07-06": _liq(s4.LIQ_OBSERVED, s4.SPREAD_DEPTH_PROXY)})["verdict"] == "UNRESOLVED_HISTORICAL_FEE"
    assert s4.signal_verdict(_fee(s4.FEE_CURRENT_ONLY), _con(s4.CON_HIST_PROVEN), FILLS, {"2026-07-06": _liq(s4.LIQ_OBSERVED, s4.SPREAD_DEPTH_PROXY)})["verdict"] == "UNRESOLVED_HISTORICAL_FEE"
    assert s4.signal_verdict(_fee(s4.FEE_HIST_PROVEN), _con(s4.CON_HIST_UNRESOLVED), FILLS, {"2026-07-06": _liq(s4.LIQ_OBSERVED, s4.SPREAD_DEPTH_PROXY)})["verdict"] == "UNRESOLVED_HISTORICAL_CONSTRAINT"
    assert s4.signal_verdict(_fee(s4.FEE_HIST_PROVEN), _con(s4.CON_HIST_PROVEN), FILLS, {"2026-07-06": _liq(s4.LIQ_UNRESOLVED, s4.SPREAD_DEPTH_PROXY)})["verdict"] == "UNRESOLVED_LIQUIDITY_EVIDENCE"
    assert s4.signal_verdict(_fee(s4.FEE_HIST_PROVEN), _con(s4.CON_HIST_PROVEN), FILLS, {"2026-07-06": _liq(s4.LIQ_OBSERVED, s4.SPREAD_UNRESOLVED)})["verdict"] == "UNRESOLVED_SPREAD_EVIDENCE"
    assert s4.signal_verdict(_fee(s4.FEE_HIST_PROVEN), _con(s4.CON_HIST_PROVEN), FILLS, {})["verdict"] == "UNRESOLVED_LIQUIDITY_EVIDENCE"


def test_verdict_fails_when_no_market_activity_in_fill_window_regardless_of_fees():
    r = s4.signal_verdict(_fee(s4.FEE_HIST_UNRESOLVED), _con(s4.CON_HIST_UNRESOLVED), FILLS, {"2026-07-06": _liq(s4.LIQ_NONE_IN_WINDOW, s4.SPREAD_UNRESOLVED)})
    assert r["verdict"] == "FAIL_NO_MARKET_ACTIVITY_AT_FILL"


def test_no_executed_fill_is_reported_not_passed():
    r = s4.signal_verdict(_fee(s4.FEE_HIST_PROVEN), _con(s4.CON_HIST_PROVEN), [{"kind": "NO_EXECUTION", "date": None, "profile": "A"}], {})
    assert r["verdict"] != "PASS_STAGE_FOUR" and "no_executed_fill_in_lifecycle" in r["missing"]


def test_trade_summary_is_derived_and_never_infers_fill_at_open():
    t0 = s4.S1._ms("2026-07-06")
    s = s4._summarise_trades([(t0 + 5000, 10.0, 2.0), (t0 + 65000, 11.0, 1.0)])
    assert s["trade_count"] == 2 and s["quote_notional"] == pytest.approx(31.0) and s["vwap"] == pytest.approx(31.0 / 3.0)
    assert s["seconds_from_open_to_first_trade"] == pytest.approx(5.0)
    assert s4._summarise_trades([]) == {"trade_count": 0}


def test_url_allowlist():
    s4._assert_safe_url("https://data.binance.vision/data/futures/um/daily/bookDepth/TRXUSDT/TRXUSDT-bookDepth-2026-07-07.zip")
    s4._assert_safe_url("https://api-pub.bitfinex.com/v2/trades/tLEOUSD/hist?start=1&end=2")
    s4._assert_safe_url("https://futures.kraken.com/api/history/v3/market/PF_KASUSD/executions?since=1&before=2")
    for bad in ("https://fapi.binance.com/fapi/v1/account", "https://api.coingecko.com/x", "https://api.bybit.com/v5/account/fee-rate"):
        with pytest.raises(s4.Stage4Error):
            s4._assert_safe_url(bad)


def test_evidence_classes_are_the_five_required_labels():
    assert {s4.OBSERVED, s4.DERIVED, s4.ASSUMPTION, s4.SENSITIVITY, s4.UNRESOLVED} == {
        "OBSERVED_FIRST_PARTY", "DERIVED_FROM_OBSERVED_DATA", "FROZEN_CONSERVATIVE_ASSUMPTION", "SENSITIVITY_ONLY", "UNRESOLVED"}


def test_live_stage4_report_if_present_reconciles_and_selects_no_assumption():
    files = sorted(s4.REPORT_DIR.glob("c22_b3_stage4_fees_liquidity_*.json")) if s4.REPORT_DIR.exists() else []
    if not files:
        pytest.skip("no sealed stage four report in this checkout")
    r = json.loads(files[-1].read_bytes().decode("utf-8"))
    assert sum(r["verdict_counts"].values()) == 75 and r["verdict_counts"]["PASS_STAGE_FOUR"] == 0
    assert r["coverage"]["fee_evidence"]["historical_fee_proven"] == 0
    assert r["coverage"]["tick_lot_minimum_evidence"]["historical_constraint_proven"] == 0
    assert r["coverage"]["spread_evidence"]["bbo_spread_observed"] == 0
    assert r["assumptions_selected"] == [] and r["assumption_selection_against_pnl"] is False
    assert r["funnel"]["fee_honestly_replayable_trades"] == 0 and r["admission_state_changed"] is False
    assert r["c22_performance_computed"] is False and r["cost_arithmetic_performed"] is False
    for x in r["step6_per_fill"]:
        assert set(x["never_inferred"]) == {"zero_spread", "infinite_liquidity", "full_fill_at_candle_open", "zero_market_impact"}
    fr = importlib.import_module("tools.c22_fee_honest_replay_once")
    assert fr.check_preconditions()["all_satisfied"] is False

"""C22 B3 Stage 4A: fail-closed grading from dated official records, current values never
upgraded to historical, Bybit tick reconstruction, Kraken orderbook evidence, sealed Stage Four
untouched, no assumption selected."""
from __future__ import annotations

import hashlib
import importlib
import json

import pytest

s4a = importlib.import_module("tools.c22_b3_stage4a_t2_recovery_once")
s4 = importlib.import_module("tools.c22_b3_stage4_fees_liquidity_once")


def test_fee_grades_are_fail_closed_and_current_is_never_historical():
    dates = ["2026-07-06", "2026-07-07"]
    assert s4a.grade_fee("BINANCE", dates)["grade"] == "UNRESOLVED"
    assert s4a.grade_fee("BYBIT", dates)["grade"] == "CURRENT_ONLY"
    assert s4a.grade_fee("OKX", dates)["grade"] == "CURRENT_ONLY"
    g = s4a.grade_fee("GATE", dates)
    assert g["grade"] == "UNRESOLVED" and g["conflict"] is True and g["contract_api_current_taker"] == 0.00075
    k = s4a.grade_fee("KRAKEN_FUTURES", dates)
    assert k["grade"] == "T2_HISTORICAL_FEE_BRACKETED" and k["reconstructed_taker"] == 0.0005 and k["pre_window_record"] and k["post_window_record"]
    b = s4a.grade_fee("BITFINEX", ["2026-07-15", "2026-07-16"])
    assert b["grade"] == "T2_HISTORICAL_FEE_BRACKETED" and b["reconstructed_taker"] == 0.0 and b["reconstructed_maker"] == 0.0
    for v in ("BYBIT", "OKX"):
        assert s4a.grade_fee(v, dates)["reconstructed_taker"] is None       # CURRENT_ONLY carries no reconstructed value


def test_constraint_grades_reconstruct_bybit_tick_from_dated_notice_and_refuse_backprojection():
    c = s4a.grade_constraints("BYBIT", "GRAMUSDT", ["2026-07-05", "2026-07-09"], {"tick_size": 0.001, "lot_step": 0.1, "min_qty": 0.1, "min_notional": 5.0})
    assert c["tick"]["grade"] == "T2_HISTORICAL_CONSTRAINT_RECONSTRUCTED" and c["tick"]["historical"] == 0.0001 and c["tick"]["current"] == 0.001
    assert c["lot_min"]["grade"] == "CURRENT_ONLY" and c["lot_min"]["historical"] is None
    b = s4a.grade_constraints("BINANCE", "TRXUSDT", ["2026-07-06"], {"tick_size": 1e-05, "lot_step": 1.0, "min_qty": 1.0, "min_notional": 5.0})
    assert b["tick"]["grade"] == "CURRENT_ONLY" and b["tick"]["historical"] is None
    g = s4a.grade_constraints("GATE", "GT_USDT", ["2026-07-04"], {"tick_size": 0.001, "lot_step": 1.0, "min_qty": 1.0, "change_timestamp": "2026-09-09"})
    assert g["tick"]["grade"] == "UNRESOLVED" and g["lot_min"]["grade"] == "UNRESOLVED"
    k = s4a.grade_constraints("KRAKEN_FUTURES", "PF_KASUSD", ["2026-07-05"], {"tick_size": 1e-05, "impact_mid_size": 64600.0})
    assert k["tick"]["grade"] == "CURRENT_ONLY" and k["lot_min"]["grade"] == "CURRENT_ONLY"


def test_fully_historical_requires_every_element():
    fee_ok = {"grade": "T2_HISTORICAL_FEE_BRACKETED"}
    con_ok = {"tick": {"grade": "T2_HISTORICAL_CONSTRAINT_RECONSTRUCTED"}, "lot_min": {"grade": "T2_BRACKETED_UNCHANGED"}}
    assert s4a.fully_historical(fee_ok, con_ok, "OBSERVED_ORDERBOOK", "DERIVED_SPREAD_FROM_BBO") is True
    assert s4a.fully_historical({"grade": "CURRENT_ONLY"}, con_ok, "OBSERVED_ORDERBOOK", "DERIVED_SPREAD_FROM_BBO") is False
    assert s4a.fully_historical(fee_ok, {"tick": {"grade": "CURRENT_ONLY"}, "lot_min": {"grade": "T2_BRACKETED_UNCHANGED"}}, "OBSERVED_ORDERBOOK", "DERIVED_SPREAD_FROM_BBO") is False
    assert s4a.fully_historical(fee_ok, con_ok, "TRADE_ACTIVITY_ONLY", "UNRESOLVED") is False
    assert s4a.fully_historical(fee_ok, con_ok, "DEPTH_PROXY_ONLY", "DEPTH_PROXY_ONLY") is False   # depth proxy is not spread


def test_url_allowlist_allows_kraken_analytics_orderbook_but_not_account_paths():
    s4a._assert_safe_url("https://futures.kraken.com/api/charts/v1/analytics/PF_KASUSD/orderbook?since=1&to=2&interval=60")
    s4a._assert_safe_url("https://support.kraken.com/articles/360048917612-fee-schedule")
    for bad in ("https://www.binance.com/en/my/orders", "https://www.coingecko.com/", "https://www.tradingview.com/x", "https://futures.kraken.com/derivatives/api/v3/accounts"):
        with pytest.raises(s4a.Stage4AError):
            s4a._assert_safe_url(bad)


def test_source_registry_is_first_party_only_and_dated_where_decisive():
    hosts = {s["url"].split("/")[2] for s in s4a.SOURCES}
    assert hosts <= set(s4a.ALLOWED_HOSTS)
    for s in s4a.SOURCES:
        assert s["role"] and s["captured"] and s["title"]
        if s["role"].startswith("fee_schedule_dated") or s["role"] == "constraint_change_notice":
            assert s["published"] or s["effective"], s["id"]


def test_live_stage4a_report_if_present_preserves_sealed_stage4_and_selects_nothing():
    files = sorted(s4a.REPORT_DIR.glob("c22_b3_stage4a_t2_recovery_*.json")) if s4a.REPORT_DIR.exists() else []
    if not files:
        pytest.skip("no sealed stage 4A report in this checkout")
    r = json.loads(files[-1].read_bytes().decode("utf-8"))
    assert r["counts"]["fully_historical_after_4a"] + r["counts"]["still_requiring_conservative_assumptions"] + r["counts"]["not_eligible"] == 75
    assert r["assumptions_selected"] == [] and r["performance_computed"] is False and r["stage4_artifacts_modified"] is False
    assert r["kas_supplemental_result"]["applied_to_sealed_stage4"] is False and r["kas_supplemental_result"]["stage4_verdict"] == "FAIL_NO_MARKET_ACTIVITY_AT_FILL"
    assert hashlib.sha256(s4a.STAGE4_REPORT.read_bytes()).hexdigest() == s4a.STAGE4_REPORT_SHA256
    assert r["coverage"]["fee"]["T1_HISTORICAL_FEE_EXACT"] == 0
    for rec in r["official_records"].values():
        assert rec["preservation"] in ("RAW_HTML_PRESERVED", "RENDERED_TEXT_CAPTURE_NOT_RAW_HTML")
        if rec["preservation"] == "RAW_HTML_PRESERVED":
            assert rec["raw_sha256"] and rec["raw_path"]

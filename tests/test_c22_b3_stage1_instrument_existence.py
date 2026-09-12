"""C22 B3 Stage One: pure verdict logic (fail-closed, date-aware, present-day never PASS),
URL allowlist, raw preservation never overwrites, offline end-to-end with injected responses
reconciles all 75 short signals, and the Stage One manifest never satisfies the fee-honest shell."""
from __future__ import annotations

import importlib
import json

import pytest

s1 = importlib.import_module("tools.c22_b3_stage1_instrument_existence_once")


def _cand(**kw):
    base = {"source_ok": True, "instrument_absent": False, "identity_ok": True, "identity_collision_unresolved": False,
            "instrument_type_ok": True, "existence_date": "2026-06-01", "existence_evidence": s1.EVIDENCE_LAUNCH_TS,
            "delisted_date": None}
    base.update(kw)
    return base


def test_verdict_pass_and_date_aware_fail():
    # instrument launched July 5: June 30 signal fails, July 10 signal passes
    c = _cand(existence_date="2026-07-05")
    assert s1.verdict_for_date(c, "2026-06-30", ["2026-07-01"])["verdict"] == "FAIL_LISTED_AFTER_SIGNAL"
    assert s1.verdict_for_date(c, "2026-07-10", ["2026-07-11"])["verdict"] == "PASS_HISTORICAL_EXISTENCE"
    assert s1.verdict_for_date(c, "2026-07-05", ["2026-07-06"])["verdict"] == "PASS_HISTORICAL_EXISTENCE"   # on-date inclusive


def test_verdict_present_day_only_never_passes():
    c = _cand(existence_date=None, existence_evidence=s1.EVIDENCE_PRESENT_ONLY)
    assert s1.verdict_for_date(c, "2026-07-10", [])["verdict"] == "UNRESOLVED_NO_AUTHORITATIVE_DATE"
    c2 = _cand(existence_date="2026-06-01", existence_evidence=s1.EVIDENCE_PRESENT_ONLY)
    assert s1.verdict_for_date(c2, "2026-07-10", [])["verdict"] == "UNRESOLVED_NO_AUTHORITATIVE_DATE"


def test_verdict_fail_closed_order():
    assert s1.verdict_for_date(_cand(source_ok=False), "2026-07-10", [])["verdict"] == "UNRESOLVED_SOURCE_INSUFFICIENT"
    assert s1.verdict_for_date(_cand(instrument_absent=True), "2026-07-10", [])["verdict"] == "FAIL_NO_SUCH_INSTRUMENT_AT_VENUE"
    assert s1.verdict_for_date(_cand(identity_collision_unresolved=True), "2026-07-10", [])["verdict"] == "UNRESOLVED_IDENTITY_COLLISION"
    assert s1.verdict_for_date(_cand(identity_ok=False), "2026-07-10", [])["verdict"] == "FAIL_WRONG_ASSET"
    assert s1.verdict_for_date(_cand(instrument_type_ok=False), "2026-07-10", [])["verdict"] == "FAIL_WRONG_INSTRUMENT_TYPE"
    assert s1.verdict_for_date(_cand(delisted_date="2026-07-11"), "2026-07-10", ["2026-07-11"])["verdict"] == "FAIL_DELISTED_BEFORE_SIGNAL"
    assert s1.verdict_for_date(_cand(delisted_date="2026-08-01"), "2026-07-10", ["2026-07-11"])["verdict"] == "PASS_HISTORICAL_EXISTENCE"


def test_url_allowlist_and_forbidden_fragments():
    s1._assert_safe_url("https://fapi.binance.com/fapi/v1/exchangeInfo")
    s1._assert_safe_url("https://futures.kraken.com/api/charts/v1/trade/PF_KASUSD/1d?from=1&to=2")
    for bad in ("http://fapi.binance.com/fapi/v1/exchangeInfo", "https://fapi.binance.com/fapi/v1/account",
                "https://api.bybit.com/v5/order/create", "https://www.coingecko.com/api", "https://api.bybit.com/v5/market/kline?apiKey=x"):
        with pytest.raises(s1.Stage1Error):
            s1._assert_safe_url(bad)


def test_required_short_cohort_is_75_over_22_assets_with_fill_dates():
    shorts = s1.required_short_signals()
    assert len(shorts) == 75
    assets = s1.assets_with_dates(shorts)
    assert len(assets) == 22
    fri = next(s for s in shorts if s["decision_date"] == "2026-07-03")   # Friday
    assert fri["fill_date_calendar"] == "2026-07-04" and fri["fill_date_weekday"] == "2026-07-06"


def test_preserve_raw_never_overwrites_and_hashes(tmp_path, monkeypatch):
    monkeypatch.setattr(s1, "RAW_DIR", tmp_path)
    resp = {"url": "https://api.gateio.ws/api/v4/futures/usdt/contracts/GT_USDT", "status": 200,
            "retrieved_utc": "2026-09-10T22:00:00+00:00", "raw_bytes": b'{"name":"GT_USDT"}'}
    meta = s1.preserve_raw("GATE", "GT", "futures_usdt_contract", resp, {"contract": "GT_USDT"}, "RUNX")
    p = tmp_path / "GATE" / "GT"
    raw = [x for x in p.iterdir() if x.name.endswith(".raw.json")]
    assert len(raw) == 1 and meta["raw_sha256"] == s1._sha(b'{"name":"GT_USDT"}')
    assert (raw[0].with_suffix(".json.sha256")).read_text().strip() == meta["raw_sha256"]
    assert json.loads((p / raw[0].name.replace(".raw.json", ".meta.json")).read_text())["endpoint"] == "https://api.gateio.ws/api/v4/futures/usdt/contracts/GT_USDT"
    with pytest.raises(s1.Stage1Error):
        s1.preserve_raw("GATE", "GT", "futures_usdt_contract", resp, {"contract": "GT_USDT"}, "RUNX")


# --- offline end-to-end with injected official-shaped responses ---------------------------------
def _fake_get_factory():
    launch_2026_07_05 = 1783036800000   # 2026-07-05T00:00:00Z
    def fake(url):
        b = None
        if url.startswith("https://fapi.binance.com/fapi/v1/exchangeInfo"):
            syms = []
            for base in ("AAVE", "CRV", "IMX", "INJ", "LINK", "PENDLE", "QNT", "SOL", "SUN", "TIA", "TRX", "VIRTUAL", "ZEC"):
                syms.append({"symbol": base + "USDT", "baseAsset": base, "quoteAsset": "USDT", "contractType": "PERPETUAL",
                             "status": "TRADING", "onboardDate": (launch_2026_07_05 if base == "QNT" else 1600000000000), "deliveryDate": 4133404800000})
            b = json.dumps({"symbols": syms})
        elif "instruments-info?category=linear" in url:
            sym = url.split("symbol=")[1]
            b = json.dumps({"retCode": 0, "result": {"list": ([] if sym == "TELUSDT" else [{"symbol": sym, "contractType": "LinearPerpetual", "status": "Trading",
                                                                                              "baseCoin": sym[:-4], "quoteCoin": "USDT", "launchTime": "1782121594000", "deliveryTime": "0"}])}})
        elif "instruments-info?category=spot" in url:
            sym = url.split("symbol=")[1]
            b = json.dumps({"retCode": 0, "result": {"list": [{"symbol": sym, "baseCoin": sym[:-4], "quoteCoin": "USDT", "status": "Trading",
                                                              "marginTrading": ("none" if sym == "TELUSDT" else "utaOnly")}]}})
        elif "market/kline" in url:
            b = json.dumps({"retCode": 0, "result": {"list": [["1780000000000", "1", "1", "1", "1", "1", "1"], ["1780086400000", "1", "1", "1", "1", "1", "1"]]}})
        elif "okx.com" in url:
            inst = url.split("instId=")[1]
            b = json.dumps({"code": "0", "data": [{"instId": inst, "instType": ("SWAP" if inst.endswith("SWAP") else "MARGIN"), "baseCcy": ("" if inst.endswith("SWAP") else "OKB"),
                                                  "ctValCcy": "OKB", "instFamily": "OKB-USDT", "ctType": "linear", "state": "live", "listTime": "1611907686000", "expTime": ""}]})
        elif "gateio" in url:
            name = url.rsplit("/", 1)[1]
            b = json.dumps({"name": name, "type": "direct", "status": "trading", "in_delisting": False, "create_time": 1647734400, "launch_time": 1647734400})
        elif "api.exchange.coinbase.com/products/" in url:
            b = json.dumps({"id": "MORPHO-USD", "base_currency": "MORPHO", "quote_currency": "USD", "margin_enabled": False, "status": "online"})
        elif "candles?granularity=ONE_DAY" in url:
            b = json.dumps({"aggregations": [{"start": "2026-06-02T00:00:00Z"}, {"start": "2026-06-01T00:00:00Z"}]})
        elif "api.international.coinbase.com/api/v1/instruments/" in url:
            b = json.dumps({"symbol": "MORPHO-PERP", "type": "PERP", "mode": "STANDARD", "base_asset_name": "MORPHO", "quote_asset_name": "USDC"})
        elif "futures.kraken.com/derivatives/api/v3/instruments" in url:
            b = json.dumps({"instruments": [
                {"symbol": "PF_KASUSD", "type": "flexible_futures", "openingDate": "2024-01-09T12:57:13Z", "base": "KAS", "quote": "USD", "pair": "KAS:USD", "category": "Layer 1", "tradfi": False, "isExpired": False, "tradeable": True},
                {"symbol": "PF_SPXUSD", "type": "flexible_futures", "openingDate": "2024-12-19T16:40:21Z", "base": "SPX", "quote": "USD", "pair": "SPX:USD", "category": "Meme", "tradfi": False, "isExpired": False, "tradeable": True}]})
        elif "charts/v1/trade" in url:
            b = json.dumps({"candles": [{"time": 1780000000000}]})
        elif "AssetPairs" in url:
            pair = url.split("pair=")[1]
            b = json.dumps({"error": [], "result": {pair: {"base": pair[:-3], "wsname": pair[:-3] + "/USD", "leverage_sell": [2, 3], "status": "online"}}})
        elif "bitfinex.com/v2/candles" in url:
            b = json.dumps([[1780000000000, 1, 1, 1, 1, 1], [1780086400000, 1, 1, 1, 1, 1]])
        elif "pub:list:pair:margin" in url:
            b = json.dumps([["LEOUSD", "BTCUSD"]])
        else:
            raise AssertionError("unexpected url " + url)
        return {"url": url, "status": 200, "retrieved_utc": "2026-09-10T22:00:00+00:00", "raw_bytes": b.encode("utf-8")}
    return fake


@pytest.fixture
def offline(tmp_path, monkeypatch):
    monkeypatch.setattr(s1, "RAW_DIR", tmp_path / "raw")
    monkeypatch.setattr(s1, "REGISTRY_DIR", tmp_path / "registry")
    monkeypatch.setattr(s1, "MANIFEST_DIR", tmp_path / "manifests")
    monkeypatch.setattr(s1, "REPORT_DIR", tmp_path / "reports")
    return tmp_path


def test_offline_end_to_end_reconciles_75_and_is_date_aware(offline):
    r = s1.run_stage1(get=_fake_get_factory(), run_id="TESTRUN", sleep_s=0)
    assert r["short_signals_required"] == 75 and r["short_assets_required"] == 22
    assert r["surviving_stage1"] + r["eliminated"] + r["unresolved"] == 75
    by = {a["c22_asset"]: a for a in r["assets"]}
    # QNT perp "launched" 2026-07-05 in the fixture: signals before that date FAIL, on/after PASS
    q = {p["decision_date"]: p["signal_verdict"] for p in by["BINANCE:QNTUSDT"]["per_signal"]}
    assert q["2026-06-20"] == "FAIL_LISTED_AFTER_SIGNAL" and all(v == "PASS_HISTORICAL_EXISTENCE" for d, v in q.items() if d >= "2026-07-05")
    # TEL: no perp, spot margin none -> eliminated, with the absent-instrument verdict on the perp candidate
    t = by["BYBIT:TELUSDT"]["per_signal"][0]
    assert t["signal_verdict"] == "FAIL_WRONG_INSTRUMENT_TYPE"
    assert {v["verdict"] for v in t["candidate_verdicts"]} == {"FAIL_NO_SUCH_INSTRUMENT_AT_VENUE", "FAIL_WRONG_INSTRUMENT_TYPE"}
    # SPX: futures candidate resolves the collision via first-party classification; spot candidate stays collision-unresolved
    spx = by["KRAKEN:SPXUSD"]["candidates"]
    assert any(c["venue"] == "KRAKEN_FUTURES" and c["identity_ok"] and not c["identity_collision_unresolved"] for c in spx)
    assert any(c["venue"] == "KRAKEN" and c["identity_collision_unresolved"] for c in spx)
    assert "identity_collision_unresolved_on_a_candidate" in by["KRAKEN:SPXUSD"]["second_source_recommended"]
    # candle-based existence is labelled as "seen since", never as a launch timestamp
    leo = by["BITFINEX:LEOUSD"]["candidates"][0]
    assert leo["existence_date_semantics"] == s1.SEM_SEEN_SINCE and leo["existence_evidence"] == s1.EVIDENCE_HIST_DATA
    # present-day-only Kraken spot margin never passes
    kas_spot = [v for p in by["KRAKEN:KASUSD"]["per_signal"] for v in p["candidate_verdicts"] if v["venue"] == "KRAKEN"]
    assert all(v["verdict"] == "UNRESOLVED_NO_AUTHORITATIVE_DATE" for v in kas_spot)
    # every registry record carries a normalized hash and provenance to raw hashes
    for a in r["assets"]:
        assert len(a["normalized_evidence_sha256"]) == 64
        assert all(len(m["raw_sha256"]) == 64 for c in a["candidates"] for m in c["evidence_sources"])
    assert r["stage_two_started"] is False and r["c22_performance_computed"] is False


def test_offline_report_writes_once_and_stage1_manifest_is_not_an_admission(offline):
    r = s1.run_stage1(get=_fake_get_factory(), run_id="TESTRUN2", sleep_s=0)
    w = s1.write_report(r)
    assert (offline / "reports" / "c22_b3_stage1_instrument_existence_TESTRUN2.json").exists()
    with pytest.raises(s1.Stage1Error):
        s1.write_report(r)
    man = json.loads((offline / "manifests" / "stage1_run_manifest__TESTRUN2.json").read_text())
    # the invariant this stage protects: a RUN manifest, never an admission manifest, so the
    # replay gate can only be opened later by a separately recorded human admission decision
    assert "not an admission manifest" in man["note"]
    assert "admission_token" not in json.dumps(man)


def test_rerun_with_same_bytes_is_deterministic(offline):
    a = s1.run_stage1(get=_fake_get_factory(), run_id="D1", sleep_s=0)
    b = s1.run_stage1(get=_fake_get_factory(), run_id="D2", sleep_s=0)
    strip = lambda r: [(x["c22_asset"], x["normalized_evidence_sha256"], [p["signal_verdict"] for p in x["per_signal"]]) for x in r["assets"]]
    assert strip(a) == strip(b)

"""Arbitrage Factory V1 - PUBLIC NO-AUTH staged-data fetch (human-approved runs only).

Executes the acquisition plan's 'future_no_auth_public_endpoint' path under an
explicit human approval (Mahmoud, 2026-06-11: "YOU have my approval to do it all").

Hard guarantees:
  - Public GET only, NO key, NO login, NO account, NO order/position endpoint.
  - Writes ONLY rows into the 5 existing header-only CSVs under
    data/arbitrage_factory_v1/staged/ (headers must already match the contracts).
  - Refuses to run unless the lane's chain (acquisition plan) is READY.
  - fees_kraken.csv is filled from the locally reviewed fees.json values +
    conservative public withdrawal fees (never zero), no network needed.
  - One pass, no loop, no scheduler. Run only on an explicit human command.
"""
from __future__ import annotations

import datetime as dt
import json
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STAGED = REPO / "data" / "arbitrage_factory_v1" / "staged"

ENDPOINTS = {  # public, no-auth, market data only
    "funding": "https://fapi.binance.com/fapi/v1/fundingRate?symbol=BTCUSDT&limit=6",
    "mark": "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT",
    "bybit_perp": "https://api.bybit.com/v5/market/tickers?category=linear&symbol=ETHUSDT",
    "bybit_spot": "https://api.bybit.com/v5/market/tickers?category=spot&symbol=ETHUSDT",
    "okx_ticker": "https://www.okx.com/api/v5/market/ticker?instId=SOL-USDT",
    "cb_book": "https://api.exchange.coinbase.com/products/BTC-USD/book?level=2",
}
for url in ENDPOINTS.values():  # structural no-auth guarantee
    assert url.startswith("https://") and "key" not in url.lower() and "secret" not in url.lower()


def _get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "sparta-research-readonly/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def _utc(ms: float | None = None) -> str:
    t = (dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc) if ms
         else dt.datetime.now(dt.timezone.utc))
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _append(name: str, expected_header: str, rows: list[str]) -> None:
    path = STAGED / name
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert lines and lines[0] == expected_header, f"header mismatch in {name}"
    with open(path, "a", encoding="utf-8", newline="") as fh:
        for row in rows:
            fh.write(row + "\n")
    print(f"  wrote {len(rows)} row(s) -> {name}")


def main() -> None:
    from sparta_commander.arbitrage_read_only_data_acquisition_plan_contract import (
        build_data_acquisition_plan)
    plan = build_data_acquisition_plan()
    assert plan["verdict"] == "ARBITRAGE_DATA_ACQUISITION_PLAN_READY", "chain not ready"
    assert STAGED.is_dir(), "staged folder missing"
    results: dict[str, str] = {}

    # 1) fees_kraken.csv -- local reviewed fees.json + conservative withdrawals
    try:
        fees = json.loads((REPO / "data/crypto_d1_research/CRYPTO_D1_SPOT_BTC_ETH_SOL_V001/V002/fees.json").read_text())
        taker = fees["taker_fee_bps"] / 10000.0
        maker = fees["maker_fee_bps"] / 10000.0
        wd = {"BTC": "0.0002", "ETH": "0.0035", "SOL": "0.01"}  # conservative, public page values
        _append("fees_kraken.csv", "venue,symbol,taker_fee_pct,maker_fee_pct,withdrawal_flat_fee",
                [f"kraken,{s},{taker:.4f},{maker:.4f},{wd[s]}" for s in ("BTC", "ETH", "SOL")])
        results["fee_schedule"] = "ok (local reviewed fees.json + conservative withdrawals)"
    except Exception as e:  # noqa: BLE001
        results["fee_schedule"] = "FAILED: " + str(e)

    # 2) funding_BTC_binance.csv -- public funding history + public mark price
    try:
        funding = _get(ENDPOINTS["funding"])
        mark = float(_get(ENDPOINTS["mark"])["markPrice"])
        rows = [f"{_utc(f['fundingTime'])},BTC,binance,{float(f['fundingRate']):.8f},{mark:.2f}"
                for f in funding]
        _append("funding_BTC_binance.csv",
                "timestamp_utc,symbol,venue,funding_rate_8h,mark_price", rows)
        results["funding_rates"] = "ok (binance public fundingRate + premiumIndex)"
    except Exception as e:  # noqa: BLE001
        results["funding_rates"] = "FAILED: " + str(e)

    # 3) basis_ETH_bybit.csv -- same-instant public spot + perp tickers
    try:
        perp = float(_get(ENDPOINTS["bybit_perp"])["result"]["list"][0]["lastPrice"])
        spot = float(_get(ENDPOINTS["bybit_spot"])["result"]["list"][0]["lastPrice"])
        basis_pct = (perp - spot) / spot * 100.0
        _append("basis_ETH_bybit.csv",
                "timestamp_utc,symbol,venue,spot_price,perp_price,basis_pct",
                [f"{_utc()},ETH,bybit,{spot:.2f},{perp:.2f},{basis_pct:.4f}"])
        results["spot_perp_basis"] = "ok (bybit public spot+linear tickers, same instant)"
    except Exception as e:  # noqa: BLE001
        results["spot_perp_basis"] = "FAILED: " + str(e)

    # 4) quotes_SOL_okx.csv -- public top-of-book
    try:
        t = _get(ENDPOINTS["okx_ticker"])["data"][0]
        bid, ask = float(t["bidPx"]), float(t["askPx"])
        _append("quotes_SOL_okx.csv", "timestamp_utc,symbol,venue,bid,ask,mid",
                [f"{_utc()},SOL,okx,{bid:.2f},{ask:.2f},{(bid + ask) / 2:.3f}"])
        results["cross_exchange_quotes"] = "ok (okx public ticker)"
    except Exception as e:  # noqa: BLE001
        results["cross_exchange_quotes"] = "FAILED: " + str(e)

    # 5) depth_BTC_coinbase.csv -- public level-2 book, depth within 10 bps
    try:
        book = _get(ENDPOINTS["cb_book"])
        best_bid, best_ask = float(book["bids"][0][0]), float(book["asks"][0][0])
        mid = (best_bid + best_ask) / 2
        lo, hi = mid * (1 - 0.0010), mid * (1 + 0.0010)
        bid_usd = sum(float(p) * float(q) for p, q, *_ in book["bids"] if float(p) >= lo)
        ask_usd = sum(float(p) * float(q) for p, q, *_ in book["asks"] if float(p) <= hi)
        spread_bps = (best_ask - best_bid) / mid * 10000
        _append("depth_BTC_coinbase.csv",
                "timestamp_utc,symbol,venue,bid_depth_usd_10bps,ask_depth_usd_10bps,spread_bps",
                [f"{_utc()},BTC,coinbase,{bid_usd:.2f},{ask_usd:.2f},{spread_bps:.2f}"])
        results["liquidity_depth"] = "ok (coinbase public level-2 book)"
    except Exception as e:  # noqa: BLE001
        results["liquidity_depth"] = "FAILED: " + str(e)

    print("\nFETCH SUMMARY (public no-auth, one pass, no scheduler):")
    for kind, status in results.items():
        print(f"  {kind:24s}: {status}")


if __name__ == "__main__":
    main()

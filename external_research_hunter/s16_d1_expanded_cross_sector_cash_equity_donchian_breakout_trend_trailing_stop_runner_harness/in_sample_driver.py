"""s16-d1 in-sample driver. Filters reused 12-name DR9-passed CSVs to IS window. NO execution."""

import datetime as _dt
import hashlib as _hashlib

IN_SAMPLE_START = _dt.date(2019, 1, 2)
IN_SAMPLE_END = _dt.date(2023, 12, 29)
TS_KEY = "date"

_BASE = "data/s16_d1_expanded_cross_sector_cash_equity_long_history/raw"
_SHAS = {
    "AAPL": "f6625ff1a6f8026369344bd50ca82bffcba716f1f3be9cdcfb5b905e35f893a9",
    "MSFT": "3ec6981f5bc4c37d56017a5542fd0d0d0ac6e9ecb132a4d5cc7668e0ddf112ce",
    "NVDA": "d974a054567921f03e66644c6ebfa18c98ae30d32da5138a60d26887c3194ee8",
    "JPM": "8aa244ab7724b292c659c81171bd8d3cf5ce5684d6c69864ee61e0be90238db7",
    "XOM": "fbbc462cbfbd11a68b0aed4d0c3fa72312afea5112cebcc24860689f33b7f77c",
    "UNH": "7b9d502e78bd2eaa8fbac08872865855e4d92ad43b1b3066881fa29f94115394",
    "WMT": "aa772f962f3afc712e9b9339b01c0b1f1fcd7cc02bf5ad276c035e1c321a8742",
    "KO": "0d00194723903bfa4724f7d3641499da6d165edb6bf8514a10e88233206d7d24",
    "META": "4cd3487376b07dd0149b12dec4154c0786ffdeaaa4ad0334f693aa8cd3dc69f5",
    "AMZN": "d10f4e5ad48e030e769e3d6e1a2228be15d2369850151e75ef050533f63d0317",
    "JNJ": "d8565742778fd015d9e5f1a3659e664baf8f6542d7f06362d5fb7116787215b5",
    "CVX": "b322748f188faf30e3daa8b96d4dd4667954fe077ca39a8198df75728337b960",
}
CSV_REGISTRY = {s: {"path": f"{_BASE}/{s}_ohlcv_1d_20190102_20251230.csv", "sha256": sha} for s, sha in _SHAS.items()}


def verify_csv_sha256(symbol):
    entry = CSV_REGISTRY[symbol]
    with open(entry["path"], "rb") as f:
        actual = _hashlib.sha256(f.read()).hexdigest()
    if actual != entry["sha256"]:
        raise Exception(f"S16_D1_CSV_SHA_MISMATCH: symbol={symbol} expected {entry['sha256']} got {actual} path={entry['path']!r}")
    return True


def filter_rows_to_is_window(rows, ts_key=TS_KEY):
    out = []
    for row in rows:
        ts_raw = row.get(ts_key)
        if ts_raw is None:
            continue
        ts_str = str(ts_raw)
        try:
            d = _dt.datetime.fromisoformat(ts_str.replace("Z", "+00:00")).date()
        except ValueError:
            try:
                d = _dt.date.fromisoformat(ts_str[:10])
            except ValueError:
                continue
        if IN_SAMPLE_START <= d <= IN_SAMPLE_END:
            out.append(row)
    return out


def run_in_sample(*args, **kwargs):
    raise RuntimeError(
        "P6_IS_NOT_AUTHORIZED: run_in_sample() is gated by separate operator authorization "
        "(Authorize s16-d1 expanded-universe trend/breakout P6 IS diagnostic only). P3 BUILD scope "
        "does NOT authorize any signal computation, backtest, or simulator run."
    )

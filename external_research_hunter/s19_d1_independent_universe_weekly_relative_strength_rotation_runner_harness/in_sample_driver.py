"""s19-d1 in-sample driver. Filters the s19 independent-universe DR9-passed CSVs (574fa9e) to the IS window. NO execution."""

import datetime as _dt
import hashlib as _hashlib

IN_SAMPLE_START = _dt.date(2019, 1, 2)
IN_SAMPLE_END = _dt.date(2023, 12, 29)
TS_KEY = "date"

_BASE = "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw"
_SHAS = {
    "ORCL": "145e739ab01bfa830f9ba46d56bc7248c47acb637da3a9976031d0d9190b8eda",
    "CSCO": "1f28be4829c0905f35b0f4bb953c69cfbe09515123249a76fa61ebabe3ce833c",
    "ADBE": "8d013f7294d6d4d5e1649db3d595ccd90ca5695616802bfc6485981063c1af38",
    "CRM": "6302b2c2055c2ab38a6166f7f8b607971cd8ced2d5bdb1794e50176a1d999f6e",
    "AMD": "3e354e930bc78f78d8ad89d8c60a2e43f01c35796d07b2899b83c2a30212e51a",
    "NFLX": "df671942de1c7568e00e100fd213384b0656cf813890f9389e62771a39e10d56",
    "TMUS": "220f5f0c6b177c17911297ff1e95a809359dbf92631708f4c4cecbfbfafc5413",
    "CMCSA": "10df467f0c2d92e8ee6958f8be20cbd47fc18b4d2b693c3d4b0b1d263246629c",
    "MCD": "d2f960892ae0252027f4a5e40bc266a71a1167a16a42c6ecefe490d886ffd50f",
    "NKE": "1507b7a4990a02c9b04bb68bb90b8414d7426e07def9a0d1d2d8f781c2e606ab",
    "LOW": "e2db1c784e0631dc9fac15a5771db938ea8a4f7321b24fac577c625c1a3a8178",
    "PEP": "037cc3d106a903bf6779702a3e09f5f18081404f587013be621a817f46a578d8",
    "PM": "fbfe0e20e4852bca8ef5296f81a3eddb8649dab78ee5a94dd9b8dfa438ad6aec",
    "MDLZ": "ba80da7b70067d8b810c135a8ebc870ab3096f0bd8aec63ad1ccff32f1dd013e",
    "GS": "35d6b1e8588d8d8fdd3c7c32e0a9c780c2ac400608997731c3b2df703ad6361b",
    "MS": "f63a808918fca000f6f5cd5a8d8fbbf94b0354059b42b329e79fbf3f0c3bfd1c",
    "WFC": "633a1d2c8cd10f9121d1008d07bfda8adf9d9f211acf566b4552ec630f297147",
    "AXP": "70de5e40d15b49e4c04106d8cb96c72b2ee3b1648e7d5e3c9a16bffd942c9abe",
    "LLY": "8137023ae61d70430c3e59a0c27f90ed649ef919085f4778e353065fdc7ba01f",
    "ABT": "3982be7f12fcd7fb1067ab2c446bf35c6f6985ac759932cf3bb47baaa7155bfa",
    "TMO": "df92465bbf7467c5f48791f1f05897bd233472d4a841215ff29b676d6e7c0f6a",
    "SLB": "c0a027cce5fbe16fdf1b484502cba7d6b96a0e0dad99eb3c328ce9aae9ee75fe",
    "EOG": "5acea5c3adfa55ebdc6e8d10ca8ced834c2b06f654323b373271186cd9a9d696",
    "HON": "3e041e00a74a902ae67392ab533bb67078bcdcd4199270bced9e2d94b8e37031",
}
CSV_REGISTRY = {s: {"path": f"{_BASE}/{s}_ohlcv_1d_20190102_20251230.csv", "sha256": sha} for s, sha in _SHAS.items()}


def verify_csv_sha256(symbol):
    entry = CSV_REGISTRY[symbol]
    with open(entry["path"], "rb") as f:
        actual = _hashlib.sha256(f.read()).hexdigest()
    if actual != entry["sha256"]:
        raise Exception(f"S19_D1_CSV_SHA_MISMATCH: symbol={symbol} expected {entry['sha256']} got {actual} path={entry['path']!r}")
    return True


def _parse_date(ts_raw):
    ts_str = str(ts_raw)
    try:
        return _dt.datetime.fromisoformat(ts_str.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return _dt.date.fromisoformat(ts_str[:10])
        except ValueError:
            return None


def filter_rows_to_is_window(rows, ts_key=TS_KEY):
    out = []
    for row in rows:
        ts_raw = row.get(ts_key)
        if ts_raw is None:
            continue
        d = _parse_date(ts_raw)
        if d is not None and IN_SAMPLE_START <= d <= IN_SAMPLE_END:
            out.append(row)
    return out


def run_in_sample(*args, **kwargs):
    raise RuntimeError(
        "P6_IS_NOT_AUTHORIZED: run_in_sample() is gated by separate operator authorization "
        "(Authorize s19-d1 ... P6 IS diagnostic only). P3 BUILD scope does NOT authorize any signal "
        "computation, backtest, or simulator run."
    )

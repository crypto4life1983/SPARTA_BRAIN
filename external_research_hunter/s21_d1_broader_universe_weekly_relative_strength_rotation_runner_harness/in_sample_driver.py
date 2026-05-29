"""s21-d1 in-sample driver. Fresh 48-name CSV registry (DR9-passed d76c999). NO execution."""

import datetime as _dt
import hashlib as _hashlib

IN_SAMPLE_START = _dt.date(2019, 1, 2)
IN_SAMPLE_END = _dt.date(2023, 12, 29)
TS_KEY = "date"

CSV_REGISTRY = {
    "ADI": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/ADI_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "7fb323b8b6e54528309a053cbf79b99335bb7072556149a2cda34280cad4eb90"
    },
    "AMAT": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/AMAT_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "94b8341c2a1e35a00b4f079fb1a161b3ea3056c99c404a3ff14320f9d5b33498"
    },
    "AMGN": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/AMGN_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "4e1222be67e2e5067e3f343a53e1effeac163a171634fe6c8e62e8ce341adc4e"
    },
    "AVGO": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/AVGO_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "68bbb13e4310ac08c887f0cf5d45c51be843cb6b8e425cf99768919a2e6679e8"
    },
    "BA": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/BA_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "e31c194c0b14bf3e7e8b790b953f4eccde280375dbd3b27b50829a3905593cb7"
    },
    "BKNG": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/BKNG_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "b50ea1a872e7a9c63e6d27801bdbfc8ca822ec732152830b0567f3610bf52ed6"
    },
    "BLK": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/BLK_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "bf1d34b60dbdbe872316ea1e28e7f3b6ac56938292051b821bcee8e2481c5ba3"
    },
    "BMY": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/BMY_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "30113066c07a989a5ed1cf51deb0f75a96a1a9c1e234dcd7212b23e67c99738c"
    },
    "C": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/C_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "ab26551fc4e7a9236c412800ad7104c50f61bf8d598768d87d2653e6d5477425"
    },
    "CB": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/CB_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "b3a62d042d147e24106c1d4ee98cc497dc7fbcb2ee718436a9a82b1273c30e8f"
    },
    "CHTR": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/CHTR_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "533831f11601b235b13c3f129b6621c1eb9b2f753abce4ece72cc263577801da"
    },
    "CI": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/CI_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "a26038c2cbca768e3fb62bd1dbab213efc1cf7ebc5376964597287402634e3d3"
    },
    "CL": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/CL_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "11d5e67de72a7e47c00873ba37cc47c59b65ed63d3941fc27503b3c54f23fd67"
    },
    "CVS": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/CVS_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "04a8280240d324f322651a3ac1eccc83deb1083293b090515a4d163f32f2feed"
    },
    "DE": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/DE_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "f7dce71beee2b11a8bba08dd96c7cc22df9174cc86ab39e4ae8184960561e127"
    },
    "EA": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/EA_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "8b04ef283bd07c68e267e054b905d248d37b3f38da5bfc4961920600e80169d4"
    },
    "GILD": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/GILD_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "8f8908e64037836893ac662e9d6ec02f40498b4fcc91af093de691b025aa2ea7"
    },
    "GIS": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/GIS_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "d74c9f1fb1829c84b84cd8dc539ccced9e0e3dee25de55ed8548e7065225a33a"
    },
    "GM": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/GM_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "8bc84c699e770d4395a4c278db8ad60108ad65147e637e7229c73b02d2444751"
    },
    "IBM": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/IBM_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "94b7419303ebeab7c54378e06fbc3c79e1f0a0eaa68445531a19adaa7ef3e0d8"
    },
    "INTC": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/INTC_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "abc780ebf8b0531dd086bed7f2d347466b7d140ecddb5b29efb8d3893baff6d6"
    },
    "INTU": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/INTU_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "80dfa7ec89eab1199258994cb3b2f381e045cdef6159a29872821846b9bb2690"
    },
    "ISRG": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/ISRG_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "2b0a25598537f054b00bf6f8e9fb90bee84d4d480917a2c6d724d8aa08db12d3"
    },
    "ITW": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/ITW_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "5af3ba07d45a7868f2e76eaea70e61d9c6bd908e6b5afe16cb549703b59d5298"
    },
    "KMB": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/KMB_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "bc513f7c3d9226c489477860263735130a9d3426964b805a8bfe04e3917a2c9c"
    },
    "LMT": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/LMT_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "8a91e97d0498c2616080bfcf6e05ba300ff42f7c547563af5e6c681877e017d6"
    },
    "MAR": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/MAR_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "64513461896b59b8f994b967920cf59b791d3fcc5e4884aeebb8136e7d44b211"
    },
    "MO": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/MO_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "3531911098cf28d4ee46c2503f379af5f01dbd937f1c7c402bebb6b8b9e898e1"
    },
    "MU": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/MU_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "2ca80464f44c7bf6b1fbf9eb839481901672640fa8a9c32de149ba8618073773"
    },
    "NOW": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/NOW_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "e7764f62dbb203cca689ef8523fcca8f414665b153718c90722b6005c3a60660"
    },
    "PFE": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/PFE_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "70e2b8d635c38c90734e5443f2903d60a70cd880207e2c2b3bdeb466be1a2508"
    },
    "PSX": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/PSX_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "0d7c27d5b7df833371298f6ec61d1ffbb756235de56433e3339580fc147d8565"
    },
    "QCOM": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/QCOM_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "543ceee152c3b5e730f4e2cc00bf829742914fa2c7da10759161222eb84d969f"
    },
    "ROST": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/ROST_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "4d75144944a89e25a619d9a77ec96decff6dd799e59cd8b0ea31731604399e01"
    },
    "RTX": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/RTX_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "801950c6bbce5fd51e77ebc8d7af57cfdb611237f80d014476698e2b0d57a94a"
    },
    "SBUX": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/SBUX_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "27403d2a4bcddc4ff43329a9d94a37d68aaa92cf8f7e85512e8e0c3986f405c3"
    },
    "SCHW": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/SCHW_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "cbad5329f294914011b6ea356d09aea7bafc36eae6a655c733318dc4948a306d"
    },
    "SPGI": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/SPGI_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "8975765a5d3aeefe33a103ef62564d78c1a6c1c26e33e1b1119b8561a0b08ce9"
    },
    "STZ": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/STZ_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "c0f4729bc03695825547d39015e5cbbc5e389ac9e2b65ec6e947597e1094af7e"
    },
    "SYK": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/SYK_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "ee083a748a898d7c226d7c7703fbdbded52afd8f430809ca1ca149d5019ca317"
    },
    "T": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/T_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "ac0ef1b7662e168c114bce833b8a586c76bc64a630c2205c64d13456f1e5ab1b"
    },
    "TGT": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/TGT_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "4431a9826b474cd4f36fb88d5c389ebfe515be704cd8a49939bf4e965881ef17"
    },
    "TJX": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/TJX_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "2a8eb58939285005fd498521ac6960316af75e878be1b1652db3a5c39e3b8693"
    },
    "TXN": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/TXN_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "96e11822ee810d710257fe76ba7bed120964d2208ee369af511a071de812c152"
    },
    "UPS": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/UPS_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "c894d14865fe5fc5a400d1d45f053ec74bdf8d80be92993013609b323a1a78b3"
    },
    "USB": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/USB_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "3caaa30619bb4b34439d971a7b27d719c5ac5fb901700ca3bac8f80fd017dafb"
    },
    "VLO": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/VLO_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "40267e609352498509ece48f1f57ab495b7fc02722bc30b5f4101d4fe4e32b04"
    },
    "VZ": {
        "path": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw/VZ_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "2adbd18a7b375124f9ee981f4c45f2ced10891a297de4745c4bfeba77c62daa9"
    }
}


def verify_csv_sha256(symbol):
    entry = CSV_REGISTRY[symbol]
    with open(entry["path"], "rb") as f:
        actual = _hashlib.sha256(f.read()).hexdigest()
    if actual != entry["sha256"]:
        raise Exception(f"S21_D1_CSV_SHA_MISMATCH: symbol={symbol} expected {entry['sha256']} got {actual} path={entry['path']!r}")
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
        "P6_IS_NOT_AUTHORIZED: run_in_sample() is gated by separate operator authorization (P6 IS diagnostic). "
        "P3 BUILD scope does NOT authorize any signal computation, backtest, or simulator run."
    )

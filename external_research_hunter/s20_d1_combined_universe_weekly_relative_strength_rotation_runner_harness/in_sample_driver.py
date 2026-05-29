"""s20-d1 in-sample driver. Merged 48-name CSV registry across BOTH DR9-passed dirs (s18: d86e5d1; s19: 574fa9e). NO execution."""

import datetime as _dt
import hashlib as _hashlib

IN_SAMPLE_START = _dt.date(2019, 1, 2)
IN_SAMPLE_END = _dt.date(2023, 12, 29)
TS_KEY = "date"

# 48-name union: s18 names resolve under the s17-broad dir; s19 names under the s19 dir. Per-name path locked.
CSV_REGISTRY = {
    "AAPL": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/AAPL_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "f6625ff1a6f8026369344bd50ca82bffcba716f1f3be9cdcfb5b905e35f893a9"
    },
    "ABBV": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/ABBV_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "73e2f33b5359cc18d6e4da46d004d32423001b8d56b925bc61cb947af5189af6"
    },
    "ABT": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/ABT_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "3982be7f12fcd7fb1067ab2c446bf35c6f6985ac759932cf3bb47baaa7155bfa"
    },
    "ADBE": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/ADBE_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "8d013f7294d6d4d5e1649db3d595ccd90ca5695616802bfc6485981063c1af38"
    },
    "AMD": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/AMD_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "3e354e930bc78f78d8ad89d8c60a2e43f01c35796d07b2899b83c2a30212e51a"
    },
    "AMZN": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/AMZN_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "d10f4e5ad48e030e769e3d6e1a2228be15d2369850151e75ef050533f63d0317"
    },
    "AXP": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/AXP_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "70de5e40d15b49e4c04106d8cb96c72b2ee3b1648e7d5e3c9a16bffd942c9abe"
    },
    "BAC": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/BAC_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "96f5b27f136b2489283a5f62dd0c734790829aa210c535eefbfac515c640ec65"
    },
    "CAT": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/CAT_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "55a0db01e31ddb478883612203fb8de3f35c34f465d5632d1b08e018bfc30079"
    },
    "CMCSA": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/CMCSA_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "10df467f0c2d92e8ee6958f8be20cbd47fc18b4d2b693c3d4b0b1d263246629c"
    },
    "COP": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/COP_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "bb9f792be977202963c11a1aed5762f68852d1e94da2247c41bb089c57fcd4b9"
    },
    "COST": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/COST_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "b2e502e51d6b3bc666c3279584cdea81895499da3c10ed2adf66d21c74daa131"
    },
    "CRM": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/CRM_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "6302b2c2055c2ab38a6166f7f8b607971cd8ced2d5bdb1794e50176a1d999f6e"
    },
    "CSCO": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/CSCO_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "1f28be4829c0905f35b0f4bb953c69cfbe09515123249a76fa61ebabe3ce833c"
    },
    "CVX": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/CVX_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "b322748f188faf30e3daa8b96d4dd4667954fe077ca39a8198df75728337b960"
    },
    "DIS": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/DIS_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "5a5340c7894ce8cab03be48e84e4ae37dd846c3e8b2395bfaa749df7a2758b80"
    },
    "EOG": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/EOG_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "5acea5c3adfa55ebdc6e8d10ca8ced834c2b06f654323b373271186cd9a9d696"
    },
    "GOOGL": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/GOOGL_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "eb65064a12597161e0bfb32303ecc479549f9cee2b276b790b1bddf1012732fe"
    },
    "GS": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/GS_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "35d6b1e8588d8d8fdd3c7c32e0a9c780c2ac400608997731c3b2df703ad6361b"
    },
    "HD": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/HD_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "43d8ac33ad9e5c9159cae8be97a398aa920a4ef862420f852186ac8990faa759"
    },
    "HON": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/HON_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "3e041e00a74a902ae67392ab533bb67078bcdcd4199270bced9e2d94b8e37031"
    },
    "JNJ": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/JNJ_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "d8565742778fd015d9e5f1a3659e664baf8f6542d7f06362d5fb7116787215b5"
    },
    "JPM": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/JPM_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "8aa244ab7724b292c659c81171bd8d3cf5ce5684d6c69864ee61e0be90238db7"
    },
    "KO": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/KO_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "0d00194723903bfa4724f7d3641499da6d165edb6bf8514a10e88233206d7d24"
    },
    "LLY": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/LLY_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "8137023ae61d70430c3e59a0c27f90ed649ef919085f4778e353065fdc7ba01f"
    },
    "LOW": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/LOW_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "e2db1c784e0631dc9fac15a5771db938ea8a4f7321b24fac577c625c1a3a8178"
    },
    "MA": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/MA_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "9dbea25a40ac7399d873a8b8f7246bb1a24f1ce39abaf0f58cb90227a70ba4ee"
    },
    "MCD": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/MCD_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "d2f960892ae0252027f4a5e40bc266a71a1167a16a42c6ecefe490d886ffd50f"
    },
    "MDLZ": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/MDLZ_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "ba80da7b70067d8b810c135a8ebc870ab3096f0bd8aec63ad1ccff32f1dd013e"
    },
    "META": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/META_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "4cd3487376b07dd0149b12dec4154c0786ffdeaaa4ad0334f693aa8cd3dc69f5"
    },
    "MRK": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/MRK_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "3ee12b393c7a4a8288c4677c51b28cd1510ce00ba1c1216e5c523e75ed4e21ae"
    },
    "MS": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/MS_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "f63a808918fca000f6f5cd5a8d8fbbf94b0354059b42b329e79fbf3f0c3bfd1c"
    },
    "MSFT": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/MSFT_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "3ec6981f5bc4c37d56017a5542fd0d0d0ac6e9ecb132a4d5cc7668e0ddf112ce"
    },
    "NFLX": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/NFLX_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "df671942de1c7568e00e100fd213384b0656cf813890f9389e62771a39e10d56"
    },
    "NKE": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/NKE_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "1507b7a4990a02c9b04bb68bb90b8414d7426e07def9a0d1d2d8f781c2e606ab"
    },
    "NVDA": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/NVDA_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "d974a054567921f03e66644c6ebfa18c98ae30d32da5138a60d26887c3194ee8"
    },
    "ORCL": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/ORCL_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "145e739ab01bfa830f9ba46d56bc7248c47acb637da3a9976031d0d9190b8eda"
    },
    "PEP": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/PEP_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "037cc3d106a903bf6779702a3e09f5f18081404f587013be621a817f46a578d8"
    },
    "PG": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/PG_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "2416ef9443ab9340b7576aa0e1c5a4f5a7dc01162e9d2ae2df7ef1e8c5c77754"
    },
    "PM": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/PM_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "fbfe0e20e4852bca8ef5296f81a3eddb8649dab78ee5a94dd9b8dfa438ad6aec"
    },
    "SLB": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/SLB_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "c0a027cce5fbe16fdf1b484502cba7d6b96a0e0dad99eb3c328ce9aae9ee75fe"
    },
    "TMO": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/TMO_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "df92465bbf7467c5f48791f1f05897bd233472d4a841215ff29b676d6e7c0f6a"
    },
    "TMUS": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/TMUS_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "220f5f0c6b177c17911297ff1e95a809359dbf92631708f4c4cecbfbfafc5413"
    },
    "UNH": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/UNH_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "7b9d502e78bd2eaa8fbac08872865855e4d92ad43b1b3066881fa29f94115394"
    },
    "V": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/V_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "9b496414f796f8558422d2a2130ec31cab73aa9088e785133bbc5db2ea407cd3"
    },
    "WFC": {
        "path": "data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/WFC_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "633a1d2c8cd10f9121d1008d07bfda8adf9d9f211acf566b4552ec630f297147"
    },
    "WMT": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/WMT_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "aa772f962f3afc712e9b9339b01c0b1f1fcd7cc02bf5ad276c035e1c321a8742"
    },
    "XOM": {
        "path": "data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/XOM_ohlcv_1d_20190102_20251230.csv",
        "row_count": 1759,
        "sha256": "fbbc462cbfbd11a68b0aed4d0c3fa72312afea5112cebcc24860689f33b7f77c"
    }
}


def verify_csv_sha256(symbol):
    entry = CSV_REGISTRY[symbol]
    with open(entry["path"], "rb") as f:
        actual = _hashlib.sha256(f.read()).hexdigest()
    if actual != entry["sha256"]:
        raise Exception(f"S20_D1_CSV_SHA_MISMATCH: symbol={symbol} expected {entry['sha256']} got {actual} path={entry['path']!r}")
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
        "(P6 IS diagnostic). P3 BUILD scope does NOT authorize any signal computation, backtest, or simulator run."
    )

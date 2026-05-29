"""s20-d1 combined-universe (s18 union s19, 48-name) WEEKLY relative-strength rotation algorithm.

Inherits Phase 2 safety contracts (C1-C8). FRESH sample-size candidate: holds the IDENTICAL byte-locked s18/s19
weekly mechanic (R=5, top-8, M=8 UNCHANGED) and ranks over the 48-name UNION of the two DR9-passed baskets.
ONLY the universe differs. Pre-SEAL K9 MEASURED-PASS incl OOS 134/67.2y (breadth solves the s19 OOS-K9 blocker).
The EDGE is untested (re-proven at s20 P6 IS; NOT inherited from s18/s19). SELECTION caveat binding (union
includes the known-OOS-good s18 basket -> positive result is weak generalization evidence).

Anchors:
  tier_n_spec_seal     = e6f801085bb14fc8f16f819fe5f085105772dadf816613b568f7c8163c4fc924
  plan_lock_seal       = 48a6d3ee923c4ed2f37ca1578e87048e4f35568b40dae60ef35a2d287dd70d34
  p2_phase2_plan_seal  = 63eb162afbe842da0e420af726e1998af8cb8bcdabdc273a33d2fa7b812712f3

P3 BUILD scope: structural skeleton + CONFIG + primitives. NO backtest execution authorized.
"""

import datetime as _dt
import hashlib as _hashlib

try:
    from AlgorithmImports import QCAlgorithm as _QCAlgorithmBase  # type: ignore
    _QC_AVAILABLE = True
except ImportError:
    _QC_AVAILABLE = False

    class _QCAlgorithmBase:
        def __init__(self):
            self.LiveMode = False
            self.StartDate = None
            self.EndDate = None
            self.Time = None
            self.Securities = {}
            self.Portfolio = type("Portfolio", (), {"TotalPortfolioValue": 0.0})()

        def SetStartDate(self, *a):
            pass

        def SetEndDate(self, *a):
            pass

        def SetCash(self, *a):
            pass

        def AddEquity(self, *a, **k):
            pass

        def Debug(self, *a, **k):
            pass

        def Log(self, *a, **k):
            pass


# K13 walk-forward fold scheme LOCKED byte-equivalent at SEAL (DA22; identical calendar to s18/s19; UNSEARCHED).
K13_FOLD_SCHEME = {
    "n_folds": 5, "window_mode": "rolling", "warmup_bars": 160, "fold_length_bars": 319,
    "folds": [
        {"fold": "F1", "idx_start": 160, "idx_end": 478, "date_start": "2019-08-21", "date_end": "2020-11-23", "bars": 319},
        {"fold": "F2", "idx_start": 479, "idx_end": 797, "date_start": "2020-11-24", "date_end": "2022-03-02", "bars": 319},
        {"fold": "F3", "idx_start": 798, "idx_end": 1116, "date_start": "2022-03-03", "date_end": "2023-06-08", "bars": 319},
        {"fold": "F4", "idx_start": 1117, "idx_end": 1435, "date_start": "2023-06-09", "date_end": "2024-09-16", "bars": 319},
        {"fold": "F5", "idx_start": 1436, "idx_end": 1758, "date_start": "2024-09-17", "date_end": "2025-12-30", "bars": 323},
    ],
    "supermajority_threshold": "ceil(0.6*5)=3 of 5",
    "boundaries_searched": False, "per_fold_refit": False,
}

CONFIG = {
    "candidate_record_id": "s20-d1-combined-universe-weekly-relative-strength-rotation-48name-large-cap-long-history",
    "phase_prefix": "PHASE2-S20-D1-COMBINED-WEEKLY-RS",
    "algo_version_for_run_id": "s20_d1_combined_weekly_rs_rotation_v0_1_0",
    "title": "s20-d1 combined-universe (48-name union) weekly relative-strength rotation FRESH sample-size candidate (paper-research-only; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE)",
    "tier_spec_seal": "e6f801085bb14fc8f16f819fe5f085105772dadf816613b568f7c8163c4fc924",
    "plan_lock_seal": "48a6d3ee923c4ed2f37ca1578e87048e4f35568b40dae60ef35a2d287dd70d34",
    "p2_phase2_plan_seal": "63eb162afbe842da0e420af726e1998af8cb8bcdabdc273a33d2fa7b812712f3",
    "plan_doc_sha256": None,
    "asset_class": "cash_equity",
    "universe": ["AAPL", "MSFT", "NVDA", "JPM", "XOM", "UNH", "WMT", "KO", "META", "AMZN", "JNJ", "CVX", "GOOGL", "V", "MA", "HD", "PG", "COST", "ABBV", "MRK", "BAC", "CAT", "DIS", "COP", "ORCL", "CSCO", "ADBE", "CRM", "AMD", "NFLX", "TMUS", "CMCSA", "MCD", "NKE", "LOW", "PEP", "PM", "MDLZ", "GS", "MS", "WFC", "AXP", "LLY", "ABT", "TMO", "SLB", "EOG", "HON"],
    "resolution": "daily",
    "brokerage_model_name": "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6",
    "start_date_is": (2019, 1, 2), "end_date_is": (2023, 12, 29),
    "start_date_oos": (2024, 1, 2), "end_date_oos": (2025, 12, 30),
    "plan_lock_window_ceiling": (2025, 12, 30),
    "mechanic_family": "cross_sectional_relative_strength_rotation_weekly_long_only",  # DA2 (identical to s18/s19)
    "momentum_lookback_L": 126,  # DA6
    "momentum_skip_S": 21,  # DA8
    "ranking_rule": "rank_48_by_trailing_return_126_21_desc",  # DA9
    "top_m_held": 8,  # DA10 (M=8 UNCHANGED)
    "rebalance_cadence_R_days": 5,  # DA11 (WEEKLY)
    "exit_rule": "ROTATION_RELATIVE_RANK",  # DA12
    "exit_is_trailing_or_atr_stop": False,  # DA12 invariant
    "sizing_method": "equal_weight",  # DA3
    "per_position_weight_fraction": 1.0 / 8.0,  # 1/M
    "signal_direction": "long-only",  # DA20
    "shorting_enabled": False, "leverage": "NONE",
    "max_positions_per_name": 1,
    "max_total_positions": 8,  # DA10/DA18
    "inter_name_signal_coordination": "cross_sectional_ranking_only",  # DA18
    "pyramid_method": "NONE",  # DA18
    "regime_overlay": "NONE", "vol_targeting": "NONE",
    "leverage_cap": "NONE_unlevered_cash_equity_DR11_not_in_chain",
    "start_cash_usd": 100000,  # DA4=B
    "dollar_per_point_per_share": 1.0, "share_lot_size": 1,
    "rth_safe_window_open": (9, 30), "rth_safe_window_close": (16, 0), "eod_cancel_time": (16, 0),
    "rth_window_tz": "America/New_York", "intraday_data_used": False, "daily_bars_only": True,
    "commission_per_share_usd": 0.005, "min_commission_per_trade_usd": 1.0,
    "slippage_model": "half_bid_ask_spread_proxy", "slippage_proxy_bps": 1.0,
    "cost_stress_tiers": [
        {"tier": "S0", "cost_scalar": 0.0, "slippage_scalar": 0.0},
        {"tier": "S1", "cost_scalar": 1.0, "slippage_scalar": 1.0},
        {"tier": "S2", "cost_scalar": 1.5, "slippage_scalar": 1.5},
        {"tier": "S3", "cost_scalar": 2.0, "slippage_scalar": 2.0},
        {"tier": "S4", "cost_scalar": 3.0, "slippage_scalar": 3.0},
    ],
    "warmup_days": 160,  # DA19
    "verdict_min_closed_trades": 100,  # K9
    "verdict_oos_min_closed_trades_per_year": 50,  # K9 OOS floor
    "verdict_max_drawdown_pct_magnitude_concern": 0.30,
    "verdict_max_drawdown_pct_magnitude_fail_safety": 0.50,  # DA5
    "adjustment_convention": "split_only",  # DA15
    "known_corporate_actions": [
        {
                "symbol": "AAPL",
                "date": "2020-08-31",
                "type": "split",
                "factor": 4.0,
                "applied": true,
                "dr9_verified": true
        },
        {
                "symbol": "NVDA",
                "date": "2021-07-20",
                "type": "split",
                "factor": 4.0,
                "applied": true,
                "dr9_verified": true
        },
        {
                "symbol": "NVDA",
                "date": "2024-06-10",
                "type": "split",
                "factor": 10.0,
                "applied": true,
                "dr9_verified": true
        },
        {
                "symbol": "AMZN",
                "date": "2022-06-06",
                "type": "split",
                "factor": 20.0,
                "applied": true,
                "dr9_verified": true
        },
        {
                "symbol": "WMT",
                "date": "2024-02-26",
                "type": "split",
                "factor": 3.0,
                "applied": true,
                "dr9_verified": true
        },
        {
                "symbol": "GOOGL",
                "date": "2022-07-18",
                "type": "split",
                "factor": 20.0,
                "applied": true,
                "dr9_verified": true
        },
        {
                "symbol": "MRK",
                "date": "2021-06-03",
                "type": "spinoff_factor",
                "factor": 1.048,
                "applied": true,
                "dr9_verified": true,
                "note": "Organon spin-off; Tiingo encodes in splitFactor stream; applied under split_only -> return-continuous"
        },
        {
                "symbol": "NFLX",
                "date": "2025-11-17",
                "type": "split",
                "factor": 10.0,
                "applied": true,
                "dr9_verified": true
        },
        {
                "symbol": "HON",
                "date": "2025-10-30",
                "type": "spinoff_factor",
                "factor": 1.061,
                "applied": true,
                "dr9_verified": true,
                "note": "Solstice Advanced Materials spin-off; Tiingo encodes in splitFactor stream; applied under split_only -> return-continuous"
        }
],
    "dividends_adjusted": False,
    "k13_fold_scheme": K13_FOLD_SCHEME,
    "data_csv_registry": {
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
},
    "data_vendor": "tiingo", "data_ts_key": "date",
    "output_schema_id": "sparta.s20.d1.combined_weekly_rs_rotation.diagnostic_run_report.v1",
    "rec1_equivalent_oos_k9_disclosure": (
        "OOS K9 >=50/y. Pre-SEAL OOS turnover MEASURED 134 (67.2/y) clears the floor; the TRUE OOS K9 (with P&L) "
        "is confirmed only at P10; if measured OOS <50/y at P10, terminal. The chain shall NOT relax K9."
    ),
    "rec1_equivalent_binding": True,
    "permanent_live_block": True, "live_promotion_blocked_at_6_gates_permanently": True,
    "research_diagnostic_only": True, "diagnostic_only_not_live_grade_label": True,
    "is_combined_universe_sample_size_test": True,
    "is_s18_or_s19_revN": False,
    "edge_not_inherited_from_s18_s19": True,  # combined edge UNTESTED; re-prove at P6 IS
    "selection_bias_caveat_binding": True,  # union includes the known-OOS-good s18 basket -> weak generalization evidence
}


# --- Cross-sectional relative-strength primitives (IDENTICAL to s18/s19; NO execution, NO order placement) ---

def trailing_return(closes, i, lookback=126, skip=21):
    """126-21 skip-month relative-strength signal at bar i: close[i-skip]/close[i-skip-lookback]-1. None if insufficient."""
    j = i - skip
    k = i - skip - lookback
    if k < 0 or j < 0 or j >= len(closes) or k >= len(closes):
        return None
    if closes[k] is None or closes[j] is None or closes[k] <= 0:
        return None
    return closes[j] / closes[k] - 1.0


def cross_sectional_rank(signals):
    """signals: dict symbol -> signal (None excluded). Returns symbols sorted by signal DESC; deterministic tie-break by symbol."""
    valid = [(s, v) for s, v in signals.items() if v is not None]
    valid.sort(key=lambda x: (-x[1], x[0]))
    return [s for s, _ in valid]


def select_top_m(ranked, m):
    if m <= 0:
        return []
    return list(ranked[:m])


def equal_weight_targets(selected, equity, m):
    """Equal-weight 1/M dollar target per selected name (NOT 1/len; cash held if fewer than M qualify)."""
    if not selected or m <= 0 or equity <= 0:
        return {}
    w = equity / m
    return {s: w for s in selected}


def is_rebalance_bar(i, warmup, rebalance_days):
    if rebalance_days <= 0:
        raise ValueError("rebalance_days must be > 0")
    return i >= warmup and (i - warmup) % rebalance_days == 0


def rotation_exits(prev_holdings, new_selected):
    new_set = set(new_selected)
    return [s for s in prev_holdings if s not in new_set]


def rotation_entries(prev_holdings, new_selected):
    prev_set = set(prev_holdings)
    return [s for s in new_selected if s not in prev_set]


def commission_cost(shares, per_share=0.005, min_per_trade=1.0, scalar=1.0):
    n = abs(shares)
    if n <= 0 or scalar <= 0:
        return 0.0
    return max(min_per_trade, n * per_share) * scalar


def slippage_cost(shares, price, bps=1.0, scalar=1.0):
    n = abs(shares)
    if n <= 0 or price <= 0 or scalar <= 0:
        return 0.0
    return n * price * (bps / 10000.0) * scalar


def add_pyramid_unit(*args, **kwargs):
    raise RuntimeError(
        "PYRAMID_FORBIDDEN: s20-d1 holds the top-M rotation set with one lot per name; pyramiding is structurally "
        "forbidden per SEAL invariant no_pyramid_per_signal (DA18)."
    )


def open_short_position(*args, **kwargs):
    raise RuntimeError(
        "SHORTING_FORBIDDEN: s20-d1 is long-only (DA20); the short leg is structurally forbidden per SEAL."
    )


class Algo(_QCAlgorithmBase):
    """s20-d1 combined-universe weekly relative-strength rotation algorithm. P3 BUILD scope; NO backtest."""

    def Initialize(self):  # noqa: N802
        if self.LiveMode:
            raise Exception(
                "LIVE_PATH_DETECTED: s20-d1-combined-universe-weekly-relative-strength-rotation is paper-only "
                "forever; refuse to run in live mode."
            )
        self.config = dict(CONFIG)
        self._stale_fill_warning_count = 0
        self._forbidden_action_attempts = []
        self._forbidden_action_attempts_detected = self._forbidden_action_attempts
        self._rebalance_count = 0
        self._rotation_exit_count = 0
        self._rotation_entry_count = 0
        self._holdings = []
        self._signal_dates_seen = set()
        self._operational_status = "ACTIVE_RESEARCH"
        if _QC_AVAILABLE and self.StartDate is not None and self.EndDate is not None:
            self._initialize_date_cross_check()

    def all_safety_warnings_zero(self):
        return self._stale_fill_warning_count == 0

    def held_count(self):
        return len(self._holdings)

    def _initialize_date_cross_check(self):
        cfg_is_start = _dt.date(*self.config["start_date_is"])
        cfg_is_end = _dt.date(*self.config["end_date_is"])
        cfg_oos_start = _dt.date(*self.config["start_date_oos"])
        cfg_oos_end = _dt.date(*self.config["end_date_oos"])
        es = self.StartDate.date() if hasattr(self.StartDate, "date") else self.StartDate
        ee = self.EndDate.date() if hasattr(self.EndDate, "date") else self.EndDate
        if (es == cfg_is_start and ee == cfg_is_end) or (es == cfg_oos_start and ee == cfg_oos_end):
            return
        raise Exception(
            f"CONFIG_START_DATE_MISMATCH_OR_CONFIG_END_DATE_MISMATCH: engine start={es} end={ee} "
            f"matches neither CONFIG IS ({cfg_is_start}..{cfg_is_end}) nor OOS ({cfg_oos_start}..{cfg_oos_end})"
        )

    @staticmethod
    def compute_deterministic_run_id(tier_spec_seal, plan_lock_seal, plan_doc_sha256, phase_literal_tag,
                                     algo_version_for_run_id, engine_start_date, engine_end_date):
        h = _hashlib.sha256()
        for piece in (tier_spec_seal, plan_lock_seal, plan_doc_sha256 or "", phase_literal_tag,
                      algo_version_for_run_id, str(engine_start_date), str(engine_end_date)):
            h.update(piece if isinstance(piece, bytes) else str(piece).encode("utf-8"))
            h.update(b"|")
        return h.hexdigest()[:12]

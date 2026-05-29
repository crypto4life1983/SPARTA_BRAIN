"""s21-d1 broader-universe (fresh 48-name) WEEKLY relative-strength rotation algorithm.

Inherits Phase 2 safety contracts (C1-C8). FRESH clean-generalization candidate: holds the IDENTICAL byte-locked
s18/s19/s20 weekly mechanic (R=5, top-8, M=8 UNCHANGED) on a FRESH 48-name universe with ZERO overlap vs s17/s18/s19.
Pre-SEAL K9 MEASURED-PASS incl OOS 171/85.8y (OOS-K9 generalizes to fresh names). The EDGE is untested (re-proven at
s21 P6 IS; NOT inherited). 0/48 names ever backtested -> a positive result is genuine independent generalization
(resolves the s20 selection caveat).

Anchors:
  tier_n_spec_seal     = 0057308a4b8d6b9aa4f7126537fca43389336579871960330e4045d60444244f
  plan_lock_seal       = 369a4fce800c9d3525bd65a50e717fe065224fca27e4a0ac9f553b3cba16af3b
  p2_phase2_plan_seal  = f55d898d5d292a3647c98ba640a30cdb5612d59fe8b328ae585c0ffc9df8186e

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
    "candidate_record_id": "s21-d1-broader-universe-weekly-relative-strength-rotation-48name-fresh-large-cap-long-history",
    "phase_prefix": "PHASE2-S21-D1-FRESH-WEEKLY-RS",
    "algo_version_for_run_id": "s21_d1_fresh_weekly_rs_rotation_v0_1_0",
    "title": "s21-d1 broader-universe (fresh 48-name) weekly relative-strength rotation FRESH clean-generalization candidate (paper-research-only; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE)",
    "tier_spec_seal": "0057308a4b8d6b9aa4f7126537fca43389336579871960330e4045d60444244f",
    "plan_lock_seal": "369a4fce800c9d3525bd65a50e717fe065224fca27e4a0ac9f553b3cba16af3b",
    "p2_phase2_plan_seal": "f55d898d5d292a3647c98ba640a30cdb5612d59fe8b328ae585c0ffc9df8186e",
    "plan_doc_sha256": None,
    "asset_class": "cash_equity",
    "universe": ["AVGO", "QCOM", "TXN", "INTC", "MU", "AMAT", "IBM", "INTU", "NOW", "ADI", "VZ", "T", "CHTR", "EA", "SBUX", "TGT", "BKNG", "MAR", "GM", "TJX", "ROST", "MO", "CL", "KMB", "GIS", "STZ", "PFE", "BMY", "AMGN", "GILD", "CVS", "CI", "ISRG", "SYK", "C", "USB", "SCHW", "BLK", "SPGI", "CB", "BA", "ITW", "UPS", "RTX", "LMT", "DE", "PSX", "VLO"],
    "resolution": "daily",
    "brokerage_model_name": "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6",
    "start_date_is": (2019, 1, 2), "end_date_is": (2023, 12, 29),
    "start_date_oos": (2024, 1, 2), "end_date_oos": (2025, 12, 30),
    "plan_lock_window_ceiling": (2025, 12, 30),
    "mechanic_family": "cross_sectional_relative_strength_rotation_weekly_long_only",  # DA2 (identical to s18/s19/s20)
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
    "known_corporate_actions": [{'symbol': 'AVGO', 'date': '2024-07-15', 'type': 'split', 'factor': 10.0, 'applied': True, 'dr9_verified': True}, {'symbol': 'IBM', 'date': '2021-11-04', 'type': 'split', 'factor': 1.046, 'applied': True, 'dr9_verified': True}, {'symbol': 'NOW', 'date': '2025-12-18', 'type': 'split', 'factor': 5.0, 'applied': True, 'dr9_verified': True}, {'symbol': 'T', 'date': '2022-04-11', 'type': 'split', 'factor': 1.324, 'applied': True, 'dr9_verified': True}, {'symbol': 'PFE', 'date': '2020-11-17', 'type': 'split', 'factor': 1.054, 'applied': True, 'dr9_verified': True}, {'symbol': 'ISRG', 'date': '2021-10-05', 'type': 'split', 'factor': 3.0, 'applied': True, 'dr9_verified': True}, {'symbol': 'RTX', 'date': '2020-04-03', 'type': 'split', 'factor': 1.589, 'applied': True, 'dr9_verified': True}],
    "dividends_adjusted": False,
    "k13_fold_scheme": K13_FOLD_SCHEME,
    "data_csv_registry": {
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
},
    "data_vendor": "tiingo", "data_ts_key": "date",
    "output_schema_id": "sparta.s21.d1.fresh_weekly_rs_rotation.diagnostic_run_report.v1",
    "rec1_equivalent_oos_k9_disclosure": (
        "OOS K9 >=50/y. Pre-SEAL OOS turnover MEASURED 171 (85.8/y) clears the floor; the TRUE OOS K9 (with P&L) "
        "is confirmed only at P10; if measured OOS <50/y at P10, terminal. The chain shall NOT relax K9."
    ),
    "rec1_equivalent_binding": True,
    "permanent_live_block": True, "live_promotion_blocked_at_6_gates_permanently": True,
    "research_diagnostic_only": True, "diagnostic_only_not_live_grade_label": True,
    "is_clean_generalization_test": True,
    "is_s18_s19_s20_revN": False,
    "edge_not_inherited_from_s18_s19_s20": True,  # fresh edge UNTESTED; re-prove at P6 IS
    "clean_generalization_no_selection_bias": True,  # 0/48 ever backtested under this mechanic
}


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
    valid = [(s, v) for s, v in signals.items() if v is not None]
    valid.sort(key=lambda x: (-x[1], x[0]))
    return [s for s, _ in valid]


def select_top_m(ranked, m):
    if m <= 0:
        return []
    return list(ranked[:m])


def equal_weight_targets(selected, equity, m):
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
        "PYRAMID_FORBIDDEN: s21-d1 holds the top-M rotation set with one lot per name; pyramiding is structurally "
        "forbidden per SEAL invariant no_pyramid_per_signal (DA18)."
    )


def open_short_position(*args, **kwargs):
    raise RuntimeError(
        "SHORTING_FORBIDDEN: s21-d1 is long-only (DA20); the short leg is structurally forbidden per SEAL."
    )


class Algo(_QCAlgorithmBase):
    """s21-d1 fresh-universe weekly relative-strength rotation algorithm. P3 BUILD scope; NO backtest."""

    def Initialize(self):  # noqa: N802
        if self.LiveMode:
            raise Exception(
                "LIVE_PATH_DETECTED: s21-d1-broader-universe-weekly-relative-strength-rotation is paper-only "
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

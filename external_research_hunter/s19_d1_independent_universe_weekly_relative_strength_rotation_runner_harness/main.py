"""s19-d1 independent-universe WEEKLY relative-strength rotation algorithm.

Inherits Phase 2 safety contracts (C1-C8). REPLICATION of the OOS_CONFIRMED s18 weekly mechanic on an INDEPENDENT
24-name universe (zero overlap with s17/s18). Mechanic byte-identical to s18 (R=5, top-8); only the universe differs.
Pre-SEAL K9 gate measured-PASS (226 IS); the EDGE is untested (re-proven at s19 P6 IS; NOT inherited from s18).

Anchors:
  tier_n_spec_seal     = 648793b40995f9fb2678ed1cff874299f8a28dd14063a68464a84ee3cf2de76b
  plan_lock_seal       = 5832d5cb0ad7c3bad2f00b915c725792d3496dfef6ab1874beed45bbf74e9e8b
  p2_phase2_plan_seal  = b0f5a5dd3f3acdfab1dda4acf474f481f84e1c1281c73bb350b08e85b2576080

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


# K13 walk-forward fold scheme LOCKED byte-equivalent at SEAL (DA22; identical to s18 on the s19 calendar; UNSEARCHED).
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
    "candidate_record_id": "s19-d1-independent-universe-weekly-relative-strength-rotation-24name-large-cap-long-history",
    "phase_prefix": "PHASE2-S19-D1-INDEPENDENT-WEEKLY-RS",
    "algo_version_for_run_id": "s19_d1_independent_weekly_rs_rotation_v0_1_0",
    "title": "s19-d1 independent-universe weekly relative-strength rotation REPLICATION of s18 (paper-research-only; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE)",
    "tier_spec_seal": "648793b40995f9fb2678ed1cff874299f8a28dd14063a68464a84ee3cf2de76b",
    "plan_lock_seal": "5832d5cb0ad7c3bad2f00b915c725792d3496dfef6ab1874beed45bbf74e9e8b",
    "p2_phase2_plan_seal": "b0f5a5dd3f3acdfab1dda4acf474f481f84e1c1281c73bb350b08e85b2576080",
    "plan_doc_sha256": None,
    "asset_class": "cash_equity",
    "universe": ["ORCL", "CSCO", "ADBE", "CRM", "AMD", "NFLX", "TMUS", "CMCSA", "MCD", "NKE", "LOW", "PEP",
                 "PM", "MDLZ", "GS", "MS", "WFC", "AXP", "LLY", "ABT", "TMO", "SLB", "EOG", "HON"],
    "resolution": "daily",
    "brokerage_model_name": "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6",
    "start_date_is": (2019, 1, 2), "end_date_is": (2023, 12, 29),
    "start_date_oos": (2024, 1, 2), "end_date_oos": (2025, 12, 30),
    "plan_lock_window_ceiling": (2025, 12, 30),
    "mechanic_family": "cross_sectional_relative_strength_rotation_weekly_long_only",  # DA2 (identical to s18)
    "momentum_lookback_L": 126,  # DA6
    "momentum_skip_S": 21,  # DA8
    "ranking_rule": "rank_24_by_trailing_return_126_21_desc",  # DA9
    "top_m_held": 8,  # DA10
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
        {"symbol": "NFLX", "date": "2025-11-17", "type": "split", "factor": 10.0, "applied": True, "dr9_verified": True},
        {"symbol": "HON", "date": "2025-10-30", "type": "spinoff_factor", "factor": 1.061, "applied": True, "dr9_verified": True,
         "note": "Solstice Advanced Materials spin-off; Tiingo encodes in splitFactor stream; applied under split_only -> return-continuous"},
    ],
    "dividends_adjusted": False,
    "k13_fold_scheme": K13_FOLD_SCHEME,
    "data_csv_registry": {
        s: {"path": f"data/s19_d1_weekly_rs_rotation_independent_universe_long_history/raw/{s}_ohlcv_1d_20190102_20251230.csv", "sha256": sha, "row_count": 1759}
        for s, sha in [
            ("ORCL", "145e739ab01bfa830f9ba46d56bc7248c47acb637da3a9976031d0d9190b8eda"),
            ("CSCO", "1f28be4829c0905f35b0f4bb953c69cfbe09515123249a76fa61ebabe3ce833c"),
            ("ADBE", "8d013f7294d6d4d5e1649db3d595ccd90ca5695616802bfc6485981063c1af38"),
            ("CRM", "6302b2c2055c2ab38a6166f7f8b607971cd8ced2d5bdb1794e50176a1d999f6e"),
            ("AMD", "3e354e930bc78f78d8ad89d8c60a2e43f01c35796d07b2899b83c2a30212e51a"),
            ("NFLX", "df671942de1c7568e00e100fd213384b0656cf813890f9389e62771a39e10d56"),
            ("TMUS", "220f5f0c6b177c17911297ff1e95a809359dbf92631708f4c4cecbfbfafc5413"),
            ("CMCSA", "10df467f0c2d92e8ee6958f8be20cbd47fc18b4d2b693c3d4b0b1d263246629c"),
            ("MCD", "d2f960892ae0252027f4a5e40bc266a71a1167a16a42c6ecefe490d886ffd50f"),
            ("NKE", "1507b7a4990a02c9b04bb68bb90b8414d7426e07def9a0d1d2d8f781c2e606ab"),
            ("LOW", "e2db1c784e0631dc9fac15a5771db938ea8a4f7321b24fac577c625c1a3a8178"),
            ("PEP", "037cc3d106a903bf6779702a3e09f5f18081404f587013be621a817f46a578d8"),
            ("PM", "fbfe0e20e4852bca8ef5296f81a3eddb8649dab78ee5a94dd9b8dfa438ad6aec"),
            ("MDLZ", "ba80da7b70067d8b810c135a8ebc870ab3096f0bd8aec63ad1ccff32f1dd013e"),
            ("GS", "35d6b1e8588d8d8fdd3c7c32e0a9c780c2ac400608997731c3b2df703ad6361b"),
            ("MS", "f63a808918fca000f6f5cd5a8d8fbbf94b0354059b42b329e79fbf3f0c3bfd1c"),
            ("WFC", "633a1d2c8cd10f9121d1008d07bfda8adf9d9f211acf566b4552ec630f297147"),
            ("AXP", "70de5e40d15b49e4c04106d8cb96c72b2ee3b1648e7d5e3c9a16bffd942c9abe"),
            ("LLY", "8137023ae61d70430c3e59a0c27f90ed649ef919085f4778e353065fdc7ba01f"),
            ("ABT", "3982be7f12fcd7fb1067ab2c446bf35c6f6985ac759932cf3bb47baaa7155bfa"),
            ("TMO", "df92465bbf7467c5f48791f1f05897bd233472d4a841215ff29b676d6e7c0f6a"),
            ("SLB", "c0a027cce5fbe16fdf1b484502cba7d6b96a0e0dad99eb3c328ce9aae9ee75fe"),
            ("EOG", "5acea5c3adfa55ebdc6e8d10ca8ced834c2b06f654323b373271186cd9a9d696"),
            ("HON", "3e041e00a74a902ae67392ab533bb67078bcdcd4199270bced9e2d94b8e37031"),
        ]
    },
    "data_vendor": "tiingo", "data_ts_key": "date",
    "output_schema_id": "sparta.s19.d1.independent_weekly_rs_rotation.diagnostic_run_report.v1",
    "rec1_equivalent_oos_k9_disclosure": (
        "OOS K9 >=50/y. Pre-SEAL turnover measurement projects ~90-117/2y (clears marginally) but the TRUE OOS K9 "
        "is confirmed only at P10; if measured OOS < 50/y at P10, terminal. The chain shall NOT relax K9."
    ),
    "rec1_equivalent_binding": True,
    "permanent_live_block": True, "live_promotion_blocked_at_6_gates_permanently": True,
    "research_diagnostic_only": True, "diagnostic_only_not_live_grade_label": True,
    "replication_of_s18": True, "edge_not_inherited_from_s18": True,  # s19 edge UNTESTED; re-prove at P6 IS
}


# --- Cross-sectional relative-strength primitives (IDENTICAL to s18; NO execution, NO order placement) ---

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
        "PYRAMID_FORBIDDEN: s19-d1 holds the top-M rotation set with one lot per name; pyramiding is structurally "
        "forbidden per SEAL invariant no_pyramid_per_signal (DA18)."
    )


def open_short_position(*args, **kwargs):
    raise RuntimeError(
        "SHORTING_FORBIDDEN: s19-d1 is long-only (DA20); the short leg is structurally forbidden per SEAL."
    )


class Algo(_QCAlgorithmBase):
    """s19-d1 independent-universe weekly relative-strength rotation algorithm. P3 BUILD scope; NO backtest."""

    def Initialize(self):  # noqa: N802
        if self.LiveMode:
            raise Exception(
                "LIVE_PATH_DETECTED: s19-d1-independent-universe-weekly-relative-strength-rotation is paper-only "
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

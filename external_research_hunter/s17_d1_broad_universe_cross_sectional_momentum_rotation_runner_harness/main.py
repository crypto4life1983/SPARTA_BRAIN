"""s17-d1 broad-universe cross-sectional momentum rotation algorithm.

Inherits Phase 2 safety contracts (C1-C8). Cross-sectional (relative-strength) momentum family; long-only.
First candidate under the walk-forward K13 discipline.

Anchors:
  tier_n_spec_seal     = ff4b237436cf116b5ab3f1f28cfbd966a99d21020589bec4a1892004fc16b5dc
  plan_lock_seal       = e848b7c4efe900f029ebc51222c7b15bb6652a21a7f306cc38327f21303888ae
  p2_phase2_plan_seal  = 4b92816c9d1825924c87554e13534e2fc74b59fbcb73569078cd3edb1bc85115

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


# K13 walk-forward fold scheme LOCKED byte-equivalent at SEAL (DA22; uniform tiling; UNSEARCHED).
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
    "candidate_record_id": "s17-d1-broad-universe-cross-sectional-momentum-rotation-24name-large-cap-long-history",
    "phase_prefix": "PHASE2-S17-D1-BROAD-UNIVERSE-XMOM",
    "algo_version_for_run_id": "s17_d1_broad_universe_xmom_v0_1_0",
    "title": "s17-d1 broad-universe cross-sectional momentum rotation fresh-candidate (paper-research-only; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE)",
    "tier_spec_seal": "ff4b237436cf116b5ab3f1f28cfbd966a99d21020589bec4a1892004fc16b5dc",
    "plan_lock_seal": "e848b7c4efe900f029ebc51222c7b15bb6652a21a7f306cc38327f21303888ae",
    "p2_phase2_plan_seal": "4b92816c9d1825924c87554e13534e2fc74b59fbcb73569078cd3edb1bc85115",
    "plan_doc_sha256": None,
    "asset_class": "cash_equity",
    "universe": ["AAPL", "MSFT", "NVDA", "JPM", "XOM", "UNH", "WMT", "KO", "META", "AMZN", "JNJ", "CVX",
                 "GOOGL", "V", "MA", "HD", "PG", "COST", "ABBV", "MRK", "BAC", "CAT", "DIS", "COP"],
    "resolution": "daily",
    "brokerage_model_name": "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6",
    "start_date_is": (2019, 1, 2), "end_date_is": (2023, 12, 29),
    "start_date_oos": (2024, 1, 2), "end_date_oos": (2025, 12, 30),
    "plan_lock_window_ceiling": (2025, 12, 30),
    # Strategy params (LOCKED at SEAL; cross-sectional momentum rotation)
    "mechanic_family": "cross_sectional_momentum_rotation_long_only",  # DA2
    "momentum_lookback_L": 126,  # DA6
    "momentum_skip_S": 21,  # DA8
    "ranking_rule": "rank_24_by_trailing_return_126_21_desc",  # DA9
    "top_m_held": 6,  # DA10
    "rebalance_cadence_R_days": 21,  # DA11
    "exit_rule": "ROTATION_RELATIVE_RANK",  # DA12
    "exit_is_trailing_or_atr_stop": False,  # DA12 invariant (no trailing/ATR stop)
    "sizing_method": "equal_weight",  # DA3
    "per_position_weight_fraction": 1.0 / 6.0,  # 1/M
    "signal_direction": "long-only",  # DA20
    "shorting_enabled": False, "leverage": "NONE",
    "max_positions_per_name": 1,  # one lot per name
    "max_total_positions": 6,  # DA10/DA18
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
        {"symbol": "AAPL", "date": "2020-08-31", "type": "split", "factor": 4.0, "applied": True, "dr9_verified": True},
        {"symbol": "NVDA", "date": "2021-07-20", "type": "split", "factor": 4.0, "applied": True, "dr9_verified": True},
        {"symbol": "NVDA", "date": "2024-06-10", "type": "split", "factor": 10.0, "applied": True, "dr9_verified": True},
        {"symbol": "AMZN", "date": "2022-06-06", "type": "split", "factor": 20.0, "applied": True, "dr9_verified": True},
        {"symbol": "WMT", "date": "2024-02-26", "type": "split", "factor": 3.0, "applied": True, "dr9_verified": True},
        {"symbol": "GOOGL", "date": "2022-07-18", "type": "split", "factor": 20.0, "applied": True, "dr9_verified": True},
        {"symbol": "MRK", "date": "2021-06-03", "type": "spinoff_factor", "factor": 1.048, "applied": True, "dr9_verified": True,
         "note": "Organon spin-off; Tiingo encodes in splitFactor stream; applied under split_only -> return-continuous"},
    ],
    "dividends_adjusted": False,
    "k13_fold_scheme": K13_FOLD_SCHEME,
    "data_csv_registry": {
        s: {"path": f"data/s17_d1_broad_universe_cross_sectional_momentum_long_history/raw/{s}_ohlcv_1d_20190102_20251230.csv", "sha256": sha, "row_count": 1759}
        for s, sha in [
            ("AAPL", "f6625ff1a6f8026369344bd50ca82bffcba716f1f3be9cdcfb5b905e35f893a9"),
            ("MSFT", "3ec6981f5bc4c37d56017a5542fd0d0d0ac6e9ecb132a4d5cc7668e0ddf112ce"),
            ("NVDA", "d974a054567921f03e66644c6ebfa18c98ae30d32da5138a60d26887c3194ee8"),
            ("JPM", "8aa244ab7724b292c659c81171bd8d3cf5ce5684d6c69864ee61e0be90238db7"),
            ("XOM", "fbbc462cbfbd11a68b0aed4d0c3fa72312afea5112cebcc24860689f33b7f77c"),
            ("UNH", "7b9d502e78bd2eaa8fbac08872865855e4d92ad43b1b3066881fa29f94115394"),
            ("WMT", "aa772f962f3afc712e9b9339b01c0b1f1fcd7cc02bf5ad276c035e1c321a8742"),
            ("KO", "0d00194723903bfa4724f7d3641499da6d165edb6bf8514a10e88233206d7d24"),
            ("META", "4cd3487376b07dd0149b12dec4154c0786ffdeaaa4ad0334f693aa8cd3dc69f5"),
            ("AMZN", "d10f4e5ad48e030e769e3d6e1a2228be15d2369850151e75ef050533f63d0317"),
            ("JNJ", "d8565742778fd015d9e5f1a3659e664baf8f6542d7f06362d5fb7116787215b5"),
            ("CVX", "b322748f188faf30e3daa8b96d4dd4667954fe077ca39a8198df75728337b960"),
            ("GOOGL", "eb65064a12597161e0bfb32303ecc479549f9cee2b276b790b1bddf1012732fe"),
            ("V", "9b496414f796f8558422d2a2130ec31cab73aa9088e785133bbc5db2ea407cd3"),
            ("MA", "9dbea25a40ac7399d873a8b8f7246bb1a24f1ce39abaf0f58cb90227a70ba4ee"),
            ("HD", "43d8ac33ad9e5c9159cae8be97a398aa920a4ef862420f852186ac8990faa759"),
            ("PG", "2416ef9443ab9340b7576aa0e1c5a4f5a7dc01162e9d2ae2df7ef1e8c5c77754"),
            ("COST", "b2e502e51d6b3bc666c3279584cdea81895499da3c10ed2adf66d21c74daa131"),
            ("ABBV", "73e2f33b5359cc18d6e4da46d004d32423001b8d56b925bc61cb947af5189af6"),
            ("MRK", "3ee12b393c7a4a8288c4677c51b28cd1510ce00ba1c1216e5c523e75ed4e21ae"),
            ("BAC", "96f5b27f136b2489283a5f62dd0c734790829aa210c535eefbfac515c640ec65"),
            ("CAT", "55a0db01e31ddb478883612203fb8de3f35c34f465d5632d1b08e018bfc30079"),
            ("DIS", "5a5340c7894ce8cab03be48e84e4ae37dd846c3e8b2395bfaa749df7a2758b80"),
            ("COP", "bb9f792be977202963c11a1aed5762f68852d1e94da2247c41bb089c57fcd4b9"),
        ]
    },
    "data_vendor": "tiingo", "data_ts_key": "date",
    "output_schema_id": "sparta.s17.d1.broad_universe.xmom.diagnostic_run_report.v1",
    "rec1_equivalent_oos_k9_disclosure": (
        "OOS K9 (>=50/y) is AT RISK for a monthly top-6 rotation (~24-72 over 2y). If observed effective OOS "
        "trade count < 50/y, OOS K9 is unreachable -> the candidate is K9-BLOCKED (terminal), NOT rescued by "
        "cadence change. The chain shall NOT relax K9 at OOS."
    ),
    "rec1_equivalent_binding": True,
    "permanent_live_block": True, "live_promotion_blocked_at_6_gates_permanently": True,
    "research_diagnostic_only": True, "diagnostic_only_not_live_grade_label": True,
}


# --- Cross-sectional momentum primitives (NO execution, NO order placement) ---

def trailing_return(closes, i, lookback=126, skip=21):
    """126-21 skip-month momentum at bar i: close[i-skip] / close[i-skip-lookback] - 1.

    Uses only data through bar (i-skip) -> no look-ahead at execution bar i. None if insufficient history.
    """
    j = i - skip
    k = i - skip - lookback
    if k < 0 or j < 0 or j >= len(closes) or k >= len(closes):
        return None
    if closes[k] is None or closes[j] is None or closes[k] <= 0:
        return None
    return closes[j] / closes[k] - 1.0


def cross_sectional_rank(signals):
    """signals: dict symbol -> signal (None excluded). Returns symbols sorted by signal DESC.

    Deterministic tie-break by symbol name ascending.
    """
    valid = [(s, v) for s, v in signals.items() if v is not None]
    valid.sort(key=lambda x: (-x[1], x[0]))
    return [s for s, _ in valid]


def select_top_m(ranked, m):
    """Top-M symbols from a ranked list."""
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
    """True if bar i is a scheduled rebalance bar: i>=warmup and (i-warmup) % R == 0."""
    if rebalance_days <= 0:
        raise ValueError("rebalance_days must be > 0")
    return i >= warmup and (i - warmup) % rebalance_days == 0


def rotation_exits(prev_holdings, new_selected):
    """Names held previously but NOT in the new top-M selection = closed trades (DA12 rotation exit)."""
    new_set = set(new_selected)
    return [s for s in prev_holdings if s not in new_set]


def rotation_entries(prev_holdings, new_selected):
    """Names newly entering the top-M selection = new lots."""
    prev_set = set(prev_holdings)
    return [s for s in new_selected if s not in prev_set]


def commission_cost(shares, per_share=0.005, min_per_trade=1.0, scalar=1.0):
    """Per-share commission with per-trade minimum, scaled by a cost-stress scalar. 0 if no shares traded."""
    n = abs(shares)
    if n <= 0 or scalar <= 0:
        return 0.0
    return max(min_per_trade, n * per_share) * scalar


def slippage_cost(shares, price, bps=1.0, scalar=1.0):
    """Half-bid-ask-spread slippage proxy in dollars, scaled by a cost-stress scalar."""
    n = abs(shares)
    if n <= 0 or price <= 0 or scalar <= 0:
        return 0.0
    return n * price * (bps / 10000.0) * scalar


def add_pyramid_unit(*args, **kwargs):
    """Pyramid FORBIDDEN (DA18)."""
    raise RuntimeError(
        "PYRAMID_FORBIDDEN: s17-d1 holds the top-M rotation set with one lot per name; pyramiding/adding to "
        "winners is structurally forbidden per SEAL invariant no_pyramid_per_signal (DA18)."
    )


def open_short_position(*args, **kwargs):
    """Shorting FORBIDDEN (DA20 long-only)."""
    raise RuntimeError(
        "SHORTING_FORBIDDEN: s17-d1 is long-only (DA20); the short leg is structurally forbidden per SEAL."
    )


class Algo(_QCAlgorithmBase):
    """s17-d1 broad-universe cross-sectional momentum rotation algorithm. P3 BUILD scope; NO backtest."""

    def Initialize(self):  # noqa: N802
        if self.LiveMode:
            raise Exception(
                "LIVE_PATH_DETECTED: s17-d1-broad-universe-cross-sectional-momentum-rotation is paper-only "
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

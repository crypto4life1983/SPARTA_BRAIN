"""s16-d1 expanded-universe Donchian breakout TREND (trailing-stop) algorithm.

Inherits Phase 2 safety contracts (C1-C8). NON-mean-reversion trend family (the fix after s14/s15).

Anchors:
  tier_n_spec_seal     = 359aea43df85c153c8cbf2b7a84ddeaa78d6516fe43769e34b052b4f88c60df8
  plan_lock_seal       = 957ca333d59a24e942a1c5f6c40375035942e2fcc53bc461c0ffbe5684d60f86
  p2_phase2_plan_seal  = 3fa8634d3c5c4317ae27a498542cac7757a50029de766967d2a729cddcf73df5

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


CONFIG = {
    "candidate_record_id": "s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop-large-cap-long-history",
    "phase_prefix": "PHASE2-S16-D1-EXPANDED-DONCHIAN-TREND",
    "algo_version_for_run_id": "s16_d1_expanded_donchian_trend_v0_1_0",
    "title": "s16-d1 expanded-universe Donchian breakout trend (trailing-stop) fresh-candidate (paper-research-only; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE)",
    "tier_spec_seal": "359aea43df85c153c8cbf2b7a84ddeaa78d6516fe43769e34b052b4f88c60df8",
    "plan_lock_seal": "957ca333d59a24e942a1c5f6c40375035942e2fcc53bc461c0ffbe5684d60f86",
    "p2_phase2_plan_seal": "3fa8634d3c5c4317ae27a498542cac7757a50029de766967d2a729cddcf73df5",
    "plan_doc_sha256": None,
    "asset_class": "cash_equity",
    "universe": ["AAPL", "MSFT", "NVDA", "JPM", "XOM", "UNH", "WMT", "KO", "META", "AMZN", "JNJ", "CVX"],
    "resolution": "daily",
    "brokerage_model_name": "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6",
    "start_date_is": (2019, 1, 2), "end_date_is": (2023, 12, 29),
    "start_date_oos": (2024, 1, 2), "end_date_oos": (2025, 12, 30),
    "plan_lock_window_ceiling": (2025, 12, 30),
    # Strategy params (LOCKED at SEAL; Donchian trend)
    "mechanic_family": "donchian_breakout_trend_trailing_stop",  # DA2
    "n_entry_donchian": 20,  # DA6
    "n_exit_donchian_trailing": 10,  # DA8
    "exit_rule": "TRAILING_DONCHIAN_CHANNEL",  # DA9
    "atr_period": 14,  # DA11
    "initial_catastrophe_stop_atr_multiple": 2.0,  # DA10
    "stop_is_tight_mean_reversion_stop": False,  # DA10 invariant
    "stop_method": "trailing_donchian_plus_2atr_initial_floor",
    "sizing_method": "vol_normalized",  # DA12
    "risk_pct_per_trade": 0.005,  # DA3=B
    "max_positions_per_name": 1,  # DA18
    "max_total_positions": 6,  # DA18
    "inter_name_signal_coordination": "NONE",  # DA18
    "pyramid_method": "NONE",  # DA18
    "regime_overlay": "NONE", "vol_targeting": "NONE",
    "leverage_cap": "NONE_unlevered_cash_equity_DR11_not_in_chain",
    "signal_direction": "bi-directional",  # DA20
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
    "warmup_days": 40,  # DA19
    "verdict_min_closed_trades": 100,
    "verdict_max_drawdown_pct_magnitude_concern": 0.30,
    "verdict_max_drawdown_pct_magnitude_fail_safety": 0.50,  # DA5
    "adjustment_convention": "split_only",  # DA15
    "known_corporate_actions": [
        {"symbol": "AAPL", "date": "2020-08-31", "type": "split", "factor": 4.0, "applied": True, "dr9_verified": True},
        {"symbol": "NVDA", "date": "2021-07-20", "type": "split", "factor": 4.0, "applied": True, "dr9_verified": True},
        {"symbol": "NVDA", "date": "2024-06-10", "type": "split", "factor": 10.0, "applied": True, "dr9_verified": True},
        {"symbol": "AMZN", "date": "2022-06-06", "type": "split", "factor": 20.0, "applied": True, "dr9_verified": True},
        {"symbol": "WMT", "date": "2024-02-26", "type": "split", "factor": 3.0, "applied": True, "dr9_verified": True},
    ],
    "dividends_adjusted": False,
    "data_csv_registry": {
        s: {"path": f"data/s16_d1_expanded_cross_sector_cash_equity_long_history/raw/{s}_ohlcv_1d_20190102_20251230.csv", "sha256": sha, "row_count": 1759}
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
        ]
    },
    "data_vendor": "tiingo", "data_ts_key": "date",
    "output_schema_id": "sparta.s16.d1.expanded.donchian_trend.diagnostic_run_report.v1",
    "rec1_equivalent_oos_k9_disclosure": (
        "OOS K9 reachable on the 12-name basket (expected ~96-180/y). If observed effective IS rate "
        "falls below 25/y basket-summed, OOS K9 unreachability becomes structurally probable -> "
        "PARKED_SAFE_BUT_OOS_INDETERMINATE per precedent. The chain shall NOT relax K9 at OOS."
    ),
    "rec1_equivalent_binding": True,
    "permanent_live_block": True, "live_promotion_blocked_at_6_gates_permanently": True,
    "research_diagnostic_only": True, "diagnostic_only_not_live_grade_label": True,
}


# --- Donchian trend primitives (NO execution, NO order placement) ---

def channel_high(highs, n):
    """Highest high over the last n values; None if insufficient."""
    if len(highs) < n:
        return None
    return max(highs[-n:])


def channel_low(lows, n):
    """Lowest low over the last n values; None if insufficient."""
    if len(lows) < n:
        return None
    return min(lows[-n:])


def long_entry_breakout(close, prior_channel_high):
    """Enter long when close breaks above the prior N_entry-day high."""
    if prior_channel_high is None:
        return False
    return close > prior_channel_high


def short_entry_breakout(close, prior_channel_low):
    """Enter short when close breaks below the prior N_entry-day low."""
    if prior_channel_low is None:
        return False
    return close < prior_channel_low


def long_trailing_exit(close, prior_exit_channel_low):
    """TRAILING exit long when close falls below the prior N_exit-day low."""
    if prior_exit_channel_low is None:
        return False
    return close < prior_exit_channel_low


def short_trailing_exit(close, prior_exit_channel_high):
    """TRAILING exit short when close rises above the prior N_exit-day high."""
    if prior_exit_channel_high is None:
        return False
    return close > prior_exit_channel_high


def compute_true_range(high, low, prev_close):
    if prev_close is None:
        return high - low
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


def wilder_atr(true_ranges, period=14):
    if len(true_ranges) < period:
        return None
    seed = sum(true_ranges[:period]) / period
    atr = seed
    for tr in true_ranges[period:]:
        atr = (atr * (period - 1) + tr) / period
    return atr


def compute_initial_stop(entry_price, atr, side, atr_multiple=2.0):
    """2N initial catastrophe stop (vol-scaled floor; NOT a tight mean-reversion stop)."""
    if side == "long":
        return entry_price - atr_multiple * atr
    if side == "short":
        return entry_price + atr_multiple * atr
    raise ValueError(f"Unknown side: {side!r}")


def compute_position_shares_vol_normalized(equity, atr, atr_multiple=2.0, risk_pct=0.005):
    """Vol-normalized sizing keyed to the 2N initial-stop distance: floor(risk$/(2*ATR))."""
    if atr is None or atr <= 0 or atr_multiple <= 0:
        return 0
    return int((risk_pct * equity) / (atr_multiple * atr))


def portfolio_can_open(open_position_count, max_total_positions=6):
    """DA18 portfolio cap gate."""
    return open_position_count < max_total_positions


def add_pyramid_unit(*args, **kwargs):
    """Pyramid FORBIDDEN (DA18)."""
    raise RuntimeError(
        "PYRAMID_FORBIDDEN: s16-d1 max_positions_per_name = 1; pyramid mechanism is structurally "
        "forbidden per SEAL invariant no_pyramid_per_signal (DA18)."
    )


class Algo(_QCAlgorithmBase):
    """s16-d1 expanded-universe Donchian breakout trend algorithm. P3 BUILD scope; NO backtest."""

    def Initialize(self):  # noqa: N802
        if self.LiveMode:
            raise Exception(
                "LIVE_PATH_DETECTED: s16-d1-expanded-cross-sector-cash-equity-donchian-breakout-trend-trailing-stop "
                "is paper-only forever; refuse to run in live mode."
            )
        self.config = dict(CONFIG)
        self._stale_fill_warning_count = 0
        self._forbidden_action_attempts = []
        self._forbidden_action_attempts_detected = self._forbidden_action_attempts
        self._breakout_signal_count = 0
        self._trailing_exit_count = 0
        self._initial_stop_breach_count = 0
        self._open_positions = {}
        self._signal_dates_seen = set()
        self._operational_status = "ACTIVE_RESEARCH"
        if _QC_AVAILABLE and self.StartDate is not None and self.EndDate is not None:
            self._initialize_date_cross_check()

    def all_safety_warnings_zero(self):
        return self._stale_fill_warning_count == 0

    def open_position_count(self):
        return sum(1 for v in self._open_positions.values() if v)

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

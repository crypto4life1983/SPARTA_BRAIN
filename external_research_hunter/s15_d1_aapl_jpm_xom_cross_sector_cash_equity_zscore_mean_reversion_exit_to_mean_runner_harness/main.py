"""s15-d1-cross-sector cash-equity AAPL/JPM/XOM z-score mean-reversion EXIT-TO-MEAN algorithm.

Inherits Phase 2 safety contracts (C1-C8). Only safety contracts inherited; no foreign strategy logic.

The exit/stop is first-principles aligned with the mean-reversion thesis (the fix after
s14-d1-cross-sector FAIL_SAFETY): EXIT-TO-MEAN (close on re-cross of SMA_L) + vol-scaled catastrophe
stop (entry -/+ 3.5*sigma_L; NOT a fixed 2N) + time-stop fallback + vol-normalized sizing.

Anchors:
  tier_n_spec_seal     = 1a89df0f07c4360cb1969f02889cd6fa973b93e81b21f0b3e27c6adc3ff0903d
  plan_lock_seal       = d1355589e0c43f9a19ae575fabb87458b7e86d33184de8b33f082cf3c9d383a3
  p2_phase2_plan_seal  = 6579f5cab302f5bf46c57184a196645755e1149941b614239cb8e9ad29488a40

P3 BUILD scope: structural skeleton + CONFIG + primitives. NO backtest execution authorized.
"""

import datetime as _dt
import hashlib as _hashlib
import math as _math

# --- QC compatibility shim ---
try:
    from AlgorithmImports import QCAlgorithm as _QCAlgorithmBase  # type: ignore
    _QC_AVAILABLE = True
except ImportError:
    _QC_AVAILABLE = False

    class _QCAlgorithmBase:
        """Minimal stub of QCAlgorithm for module-level testability without QC runtime."""

        def __init__(self):
            self.LiveMode = False
            self.StartDate = None
            self.EndDate = None
            self.Time = None
            self.Securities = {}
            self.Portfolio = type("Portfolio", (), {"TotalPortfolioValue": 0.0})()

        def SetStartDate(self, *args):
            pass

        def SetEndDate(self, *args):
            pass

        def SetCash(self, *args):
            pass

        def AddEquity(self, *args, **kwargs):
            pass

        def Debug(self, *args, **kwargs):
            pass

        def Log(self, *args, **kwargs):
            pass


# --- CONFIG (all locked values from SEAL 597a49b + P1 c8d6dd5 + P2 5b36ac8; DA1-DA20) ---

CONFIG = {
    # Identity (C2)
    "candidate_record_id": "s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean",
    "phase_prefix": "PHASE2-S15-D1-CROSS-SECTOR-ZSCORE-EXIT-TO-MEAN",
    "algo_version_for_run_id": "s15_d1_cross_sector_zscore_exit_to_mean_v0_1_0",
    "title": (
        "s15-d1-cross-sector cash-equity AAPL/JPM/XOM z-score mean-reversion exit-to-mean fresh-candidate "
        "(paper-research-only; diagnostic-only; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE)"
    ),
    # Sealed chain (C2)
    "tier_spec_seal": "1a89df0f07c4360cb1969f02889cd6fa973b93e81b21f0b3e27c6adc3ff0903d",
    "plan_lock_seal": "d1355589e0c43f9a19ae575fabb87458b7e86d33184de8b33f082cf3c9d383a3",
    "p2_phase2_plan_seal": "6579f5cab302f5bf46c57184a196645755e1149941b614239cb8e9ad29488a40",
    "plan_doc_sha256": None,
    # Instrument (DA17 cross-sector universe; reused DR9-passed CSVs)
    "asset_class": "cash_equity",
    "universe": ["AAPL", "JPM", "XOM"],
    "universe_sectors": {"AAPL": "Information Technology", "JPM": "Financials", "XOM": "Energy"},
    "resolution": "daily",
    "brokerage_model_name": "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6",
    # Window
    "start_date_is": (2019, 1, 2),
    "end_date_is": (2023, 12, 29),
    "start_date_oos": (2024, 1, 2),
    "end_date_oos": (2025, 12, 30),
    "plan_lock_window_ceiling": (2025, 12, 30),
    # Strategy params (LOCKED at SEAL; z-score mean-reversion exit-to-mean)
    "mechanic_family": "zscore_bollinger_mean_reversion_exit_to_mean",  # DA2
    "lookback_L": 20,  # DA6 (Bollinger standard)
    "entry_band_k_sigma": 2.0,  # DA8 (entry long z<=-2.0, short z>=+2.0)
    "exit_rule": "EXIT_TO_MEAN",  # DA9 (close re-crosses SMA_L midline)
    "catastrophe_stop_sigma_multiple": 3.5,  # DA10 (vol-scaled; NOT fixed 2N)
    "catastrophe_stop_is_fixed_2N": False,  # DA10 invariant
    "stop_method": "vol_scaled_catastrophe_sigma",  # NOT fixed_2N_atr
    "time_stop_max_hold_bars": 10,  # DA11
    "sizing_method": "vol_normalized",  # DA12
    "risk_pct_per_trade": 0.005,  # DA3=B
    "max_positions_per_name": 1,  # DA18
    "max_total_positions": 3,  # DA18
    "inter_name_signal_coordination": "NONE",  # DA18
    "pyramid_method": "NONE",  # DA18
    "regime_overlay": "NONE",
    "vol_targeting": "NONE",
    "leverage_cap": "NONE_unlevered_cash_equity_DR11_not_in_chain",
    # Sizing (DA4=B)
    "start_cash_usd": 100000,  # DA4=B
    "dollar_per_point_per_share": 1.0,
    "share_lot_size": 1,
    # RTH (C4; daily-bar)
    "rth_safe_window_open": (9, 30),
    "rth_safe_window_close": (16, 0),
    "eod_cancel_time": (16, 0),  # MUST equal rth_safe_window_close
    "rth_window_tz": "America/New_York",
    "intraday_data_used": False,
    "daily_bars_only": True,
    # Costs (cost_surface from SEAL)
    "commission_per_share_usd": 0.005,
    "min_commission_per_trade_usd": 1.0,
    "slippage_model": "half_bid_ask_spread_proxy",
    "slippage_proxy_bps": 1.0,
    "cost_stress_tiers": [  # DA7
        {"tier": "S0", "cost_scalar": 0.0, "slippage_scalar": 0.0},
        {"tier": "S1", "cost_scalar": 1.0, "slippage_scalar": 1.0},
        {"tier": "S2", "cost_scalar": 1.5, "slippage_scalar": 1.5},
        {"tier": "S3", "cost_scalar": 2.0, "slippage_scalar": 2.0},
        {"tier": "S4", "cost_scalar": 3.0, "slippage_scalar": 3.0},
    ],
    # Warmup (DA19)
    "warmup_days": 30,
    # Verdict thresholds (C7)
    "verdict_min_closed_trades": 100,  # K9 inviolate (basket-summed)
    "verdict_max_drawdown_pct_magnitude_concern": 0.30,
    "verdict_max_drawdown_pct_magnitude_fail_safety": 0.50,  # DA5 K4
    # Corporate actions (C5; split_only DA15 — documented + applied; reuse)
    "adjustment_convention": "split_only",
    "known_corporate_actions": [
        {"symbol": "AAPL", "date": "2020-08-31", "type": "split", "factor": 4.0, "applied": True, "dr9_verified": True},
    ],
    "dividends_adjusted": False,
    # Data anchors (DR9-passed sealed cross-sector CSVs; reuse byte-equivalent, no fresh fetch)
    "data_csv_registry": {
        "AAPL": {"path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/AAPL_ohlcv_1d_20190102_20251230.csv", "sha256": "f6625ff1a6f8026369344bd50ca82bffcba716f1f3be9cdcfb5b905e35f893a9", "row_count": 1759},
        "JPM": {"path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/JPM_ohlcv_1d_20190102_20251230.csv", "sha256": "8aa244ab7724b292c659c81171bd8d3cf5ce5684d6c69864ee61e0be90238db7", "row_count": 1759},
        "XOM": {"path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/XOM_ohlcv_1d_20190102_20251230.csv", "sha256": "fbbc462cbfbd11a68b0aed4d0c3fa72312afea5112cebcc24860689f33b7f77c", "row_count": 1759},
    },
    "data_vendor": "tiingo",
    "data_ts_key": "date",
    # Output schema
    "output_schema_id": "sparta.s15.d1.cross_sector.zscore_exit_to_mean.diagnostic_run_report.v1",
    # REC1-equivalent OOS K9 disclosure (BINDING)
    "rec1_equivalent_oos_k9_disclosure": (
        "OOS K9 reachable on the cross-sector basket (expected ~60-105/y basket-summed). If observed "
        "effective IS rate falls below 25/y basket-summed, OOS K9 unreachability becomes structurally "
        "probable -> PARKED_SAFE_BUT_OOS_INDETERMINATE per precedent. The chain shall NOT relax K9 at OOS."
    ),
    "rec1_equivalent_binding": True,
    # Permanent live block
    "permanent_live_block": True,
    "live_promotion_blocked_at_6_gates_permanently": True,
    "research_diagnostic_only": True,
    "diagnostic_only_not_live_grade_label": True,
}


# --- Strategy primitives (z-score mean-reversion exit-to-mean; NO execution, NO order placement) ---

def rolling_mean(closes, lookback):
    """Simple moving average of the last `lookback` closes; None if insufficient data."""
    if len(closes) < lookback:
        return None
    window = closes[-lookback:]
    return sum(window) / lookback


def rolling_std(closes, lookback):
    """Sample standard deviation (ddof=1) of the last `lookback` closes; None if insufficient."""
    if len(closes) < lookback or lookback < 2:
        return None
    window = closes[-lookback:]
    m = sum(window) / lookback
    var = sum((x - m) ** 2 for x in window) / (lookback - 1)
    return _math.sqrt(var)


def zscore(closes, lookback):
    """z = (latest_close - SMA_L) / std_L; None if insufficient data or std==0."""
    m = rolling_mean(closes, lookback)
    s = rolling_std(closes, lookback)
    if m is None or s is None or s == 0:
        return None
    return (closes[-1] - m) / s


def long_entry_signal(z, k=2.0):
    """Oversold: z <= -k triggers long entry."""
    if z is None:
        return False
    return z <= -k


def short_entry_signal(z, k=2.0):
    """Overbought: z >= +k triggers short entry."""
    if z is None:
        return False
    return z >= k


def long_exit_to_mean(close, mean):
    """EXIT-TO-MEAN long: close has recovered to / above the rolling mean."""
    if mean is None:
        return False
    return close >= mean


def short_exit_to_mean(close, mean):
    """EXIT-TO-MEAN short: close has fallen to / below the rolling mean."""
    if mean is None:
        return False
    return close <= mean


def compute_catastrophe_stop(entry_price, sigma, side, sigma_multiple=3.5):
    """Vol-scaled catastrophe stop (NOT a fixed 2N): entry -/+ sigma_multiple * sigma."""
    if side == "long":
        return entry_price - sigma_multiple * sigma
    if side == "short":
        return entry_price + sigma_multiple * sigma
    raise ValueError(f"Unknown side: {side!r}")


def compute_position_shares_vol_normalized(equity, sigma, sigma_multiple=3.5, risk_pct=0.005):
    """Vol-normalized sizing keyed to the catastrophe-stop distance.

    risk_dollars = risk_pct * equity
    risk_per_share = sigma_multiple * sigma  (the catastrophe-stop distance, $ per share)
    shares = floor(risk_dollars / risk_per_share)
    """
    if sigma is None or sigma <= 0 or sigma_multiple <= 0:
        return 0
    risk_per_share = sigma_multiple * sigma
    return int((risk_pct * equity) / risk_per_share)


def time_stop_hit(bars_held, max_hold_bars=10):
    """Time-stop fallback: True once a position has been held >= max_hold_bars."""
    return bars_held >= max_hold_bars


def portfolio_can_open(open_position_count, max_total_positions=3):
    """DA18 portfolio cap gate: True iff a new position can be opened."""
    return open_position_count < max_total_positions


def add_pyramid_unit(*args, **kwargs):
    """Pyramid is FORBIDDEN. Raises RuntimeError per DA18."""
    raise RuntimeError(
        "PYRAMID_FORBIDDEN: s15-d1-cross-sector max_positions_per_name = 1; pyramid mechanism "
        "is structurally forbidden per SEAL invariant no_pyramid_per_signal (DA18)."
    )


# --- Algo class ---

class Algo(_QCAlgorithmBase):
    """s15-d1-cross-sector cash-equity z-score mean-reversion exit-to-mean algorithm.

    P3 BUILD scope: structural skeleton + safety contracts. NO backtest execution authorized.
    """

    def Initialize(self):  # noqa: N802 (QC API name)
        # C1: LiveMode refusal
        if self.LiveMode:
            raise Exception(
                "LIVE_PATH_DETECTED: s15-d1-aapl-jpm-xom-cross-sector-cash-equity-zscore-mean-reversion-exit-to-mean "
                "is paper-only forever; refuse to run in live mode."
            )

        self.config = dict(CONFIG)

        # C3: safety counters
        self._stale_fill_warning_count = 0
        self._forbidden_action_attempts = []
        self._forbidden_action_attempts_detected = self._forbidden_action_attempts
        self._zscore_signal_count = 0
        self._catastrophe_stop_breach_count = 0
        self._exit_to_mean_count = 0
        self._time_stop_count = 0
        self._open_positions = {}
        self._signal_dates_seen = set()

        # C8 lifecycle
        self._operational_status = "ACTIVE_RESEARCH"

        # C2: engine-truth date cross-check
        if _QC_AVAILABLE and self.StartDate is not None and self.EndDate is not None:
            self._initialize_date_cross_check()

    def all_safety_warnings_zero(self):
        """C3 universal safety counter rollup."""
        return self._stale_fill_warning_count == 0

    def open_position_count(self):
        """Number of currently-open positions across the basket (DA18 cap input)."""
        return sum(1 for v in self._open_positions.values() if v)

    def _initialize_date_cross_check(self):
        """C2 engine-truth Initialize cross-check."""
        cfg_is_start = _dt.date(*self.config["start_date_is"])
        cfg_is_end = _dt.date(*self.config["end_date_is"])
        cfg_oos_start = _dt.date(*self.config["start_date_oos"])
        cfg_oos_end = _dt.date(*self.config["end_date_oos"])
        engine_start = self.StartDate.date() if hasattr(self.StartDate, "date") else self.StartDate
        engine_end = self.EndDate.date() if hasattr(self.EndDate, "date") else self.EndDate
        if engine_start == cfg_is_start and engine_end == cfg_is_end:
            return
        if engine_start == cfg_oos_start and engine_end == cfg_oos_end:
            return
        raise Exception(
            f"CONFIG_START_DATE_MISMATCH_OR_CONFIG_END_DATE_MISMATCH: engine "
            f"start={engine_start} end={engine_end} matches neither CONFIG IS "
            f"({cfg_is_start}..{cfg_is_end}) nor CONFIG OOS ({cfg_oos_start}..{cfg_oos_end})"
        )

    @staticmethod
    def compute_deterministic_run_id(
        tier_spec_seal, plan_lock_seal, plan_doc_sha256, phase_literal_tag,
        algo_version_for_run_id, engine_start_date, engine_end_date,
    ):
        """C2 deterministic run_id."""
        h = _hashlib.sha256()
        for piece in (
            tier_spec_seal, plan_lock_seal, plan_doc_sha256 or "", phase_literal_tag,
            algo_version_for_run_id, str(engine_start_date), str(engine_end_date),
        ):
            if isinstance(piece, bytes):
                h.update(piece)
            else:
                h.update(str(piece).encode("utf-8"))
            h.update(b"|")
        return h.hexdigest()[:12]

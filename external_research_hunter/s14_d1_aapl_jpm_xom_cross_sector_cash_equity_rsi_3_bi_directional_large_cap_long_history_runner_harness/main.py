"""s14-d1-cross-sector cash-equity AAPL/JPM/XOM RSI(3) bi-directional algorithm.

Inherits Phase 2 safety contracts (C1-C8) from docs/phase2_safety_contract_template.md.
Only safety contracts inherited; no foreign strategy logic.

s14-d1-cross-sector specific adaptations:
  - asset_class = cash_equity (3-name cross-sector basket AAPL/JPM/XOM)
  - C5 split_only (DA17): AAPL 2020-08-31 4:1 applied+verified; JPM/XOM no splits; dividends NOT adjusted
  - C3 extended_hours / unsupported_order_type NOT_APPLICABLE (daily bars)
  - C4 US equity RTH session boundary
  - DA20 portfolio caps: max_positions_per_name=1, max_total_positions=3, no inter-name coordination, no pyramid
  - REC1-equivalent + DA3=B (0.5%) + DA4=B ($100k) + K9-reachability carried binding in C6

Anchors:
  tier_n_spec_seal     = 862c00a5ffcc470580b6defe9c31ce89c4a43114ad418b4b6b4dfb991500569c
  plan_lock_seal       = fa6c2c52fb0befd5ec2345d3d74f4fd4ad4577ec4f4857193c288171692bcd00
  p2_phase2_plan_seal  = 89717a4a60ff6b704c5922683d0a46e34e59e4032a5d38eba8b1bf841f819d67

P3 BUILD scope: module structure + CONFIG + Algo class + RSI(3) bi-directional signal primitives.
NO backtest, NO fetch, NO broker calls. Strategy execution requires separate operator authorization
(P4 smoke / P6 IS / P10 OOS) and remains BLOCKED at 6 gates regardless of any future verdict.
"""

import datetime as _dt
import hashlib as _hashlib

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


# --- CONFIG (all locked values from SEAL 53cb804 + P1 02b77d8 + P2 27dbddc; DA1-DA20) ---

CONFIG = {
    # Identity (C2)
    "candidate_record_id": "s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional-large-cap-long-history",
    "phase_prefix": "PHASE2-S14-D1-CROSS-SECTOR-RSI-3-BIDIR",
    "algo_version_for_run_id": "s14_d1_cross_sector_v0_1_0",
    "title": (
        "s14-d1-cross-sector cash-equity AAPL/JPM/XOM RSI(3) bi-directional fresh-candidate "
        "(paper-research-only; diagnostic-only; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE)"
    ),
    # Sealed chain (C2)
    "tier_spec_seal": "862c00a5ffcc470580b6defe9c31ce89c4a43114ad418b4b6b4dfb991500569c",
    "plan_lock_seal": "fa6c2c52fb0befd5ec2345d3d74f4fd4ad4577ec4f4857193c288171692bcd00",
    "p2_phase2_plan_seal": "89717a4a60ff6b704c5922683d0a46e34e59e4032a5d38eba8b1bf841f819d67",
    "plan_doc_sha256": None,
    # Instrument (DA19 cross-sector universe)
    "asset_class": "cash_equity",
    "universe": ["AAPL", "JPM", "XOM"],
    "universe_sectors": {
        "AAPL": "Information Technology",
        "JPM": "Financials",
        "XOM": "Energy",
    },
    "resolution": "daily",
    "brokerage_model_name": "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6",
    # Window
    "start_date_is": (2019, 1, 2),
    "end_date_is": (2023, 12, 29),
    "start_date_oos": (2024, 1, 2),
    "end_date_oos": (2025, 12, 30),
    "plan_lock_window_ceiling": (2025, 12, 30),
    # Strategy params (LOCKED at PLAN/SEAL; DA6/DA8-DA11/DA12/DA13/DA3)
    "rsi_period": 3,  # DA6
    "rsi_method": "Connors_RSI_3_Wilder_smoothing",
    "rsi_long_entry_threshold": 15,  # DA8
    "rsi_long_exit_threshold": 55,  # DA9
    "rsi_short_entry_threshold": 85,  # DA10
    "rsi_short_exit_threshold": 45,  # DA11
    "atr_period": 14,  # DA12 (equity-standard)
    "atr_method": "Wilder",
    "stop_multiplier_in_atr": 2.0,  # DA13 (2N stop)
    "risk_pct_per_trade": 0.005,  # DA3=B
    "max_positions_per_name": 1,  # DA20
    "max_total_positions": 3,  # DA20
    "inter_name_signal_coordination": "NONE",  # DA20
    "pyramid_method": "NONE",  # DA20
    "regime_overlay": "NONE",
    "correlation_filter": "NONE_K10_LOAD_BEARING_DIAGNOSTIC_ONLY",
    "vol_targeting": "NONE",
    "leverage_cap": "NONE_unlevered_cash_equity_DR11_not_in_chain",
    # Sizing (DA4=B)
    "start_cash_usd": 100000,  # DA4=B
    "dollar_per_point_per_share": 1.0,  # cash equity: $1 PnL per $1 price move per share
    "share_lot_size": 1,
    "contract_multiplier_note": "cash equity: 1 share, $1 per $1 price move (no contract multiplier)",
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
    # Warmup (DA16)
    "warmup_days": 30,
    # Verdict thresholds (C7)
    "verdict_min_closed_trades": 100,  # K9 inviolate (basket-summed)
    "verdict_max_drawdown_pct_magnitude_concern": 0.30,
    "verdict_max_drawdown_pct_magnitude_fail_safety": 0.50,  # DA5 K4
    # Corporate actions (C5; split_only DA17 — documented + applied, NOT structurally absent)
    "adjustment_convention": "split_only",
    "known_corporate_actions": [
        {"symbol": "AAPL", "date": "2020-08-31", "type": "split", "factor": 4.0, "applied": True, "dr9_verified": True},
    ],
    "dividends_adjusted": False,
    # Data anchors (DR9-passed sealed cross-sector CSVs; reuse byte-equivalent, no fresh fetch post-seal)
    "data_csv_registry": {
        "AAPL": {
            "path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/AAPL_ohlcv_1d_20190102_20251230.csv",
            "sha256": "f6625ff1a6f8026369344bd50ca82bffcba716f1f3be9cdcfb5b905e35f893a9",
            "row_count": 1759,
        },
        "JPM": {
            "path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/JPM_ohlcv_1d_20190102_20251230.csv",
            "sha256": "8aa244ab7724b292c659c81171bd8d3cf5ce5684d6c69864ee61e0be90238db7",
            "row_count": 1759,
        },
        "XOM": {
            "path": "data/s14_d1_aapl_jpm_xom_cross_sector_cash_equity_long_history/raw/XOM_ohlcv_1d_20190102_20251230.csv",
            "sha256": "fbbc462cbfbd11a68b0aed4d0c3fa72312afea5112cebcc24860689f33b7f77c",
            "row_count": 1759,
        },
    },
    "data_vendor": "tiingo",
    "data_ts_key": "date",
    # Output schema
    "output_schema_id": "sparta.s14.d1.cross_sector.rsi_3_bidir.diagnostic_run_report.v1",
    # REC1-equivalent OOS K9 disclosure (BINDING per operator authorization)
    "rec1_equivalent_oos_k9_disclosure": (
        "OOS K9 reachable with improved margin vs all-tech (cross-sector higher signal independence "
        "~75% vs all-tech ~60%; expected effective rate 45-79/y vs 50/y OOS floor). If observed "
        "effective IS rate falls below 25/y basket-summed, OOS K9 unreachability becomes structurally "
        "probable -> PARKED_SAFE_BUT_OOS_INDETERMINATE per s10-d2/s12-d1 precedent. The chain shall "
        "NOT relax K9 at OOS."
    ),
    "rec1_equivalent_binding": True,
    # Diversification metrics (A7/K10 LOAD-BEARING)
    "a7_effective_independent_bets_thesis": "expected A7 ~2.3-2.8 (cross-sector) vs ~1.5-2.0 all-tech",
    "k10_avg_pairwise_corr_expected": "0.30-0.50 (cross-sector); LOAD-BEARING",
    # Permanent live block
    "permanent_live_block": True,
    "live_promotion_blocked_at_6_gates_permanently": True,
    "research_diagnostic_only": True,
    "diagnostic_only_not_live_grade_label": True,
}


# --- Strategy primitives (RSI(3) bi-directional; NO execution, NO order placement) ---

def compute_close_to_close_returns(closes):
    """Returns list of (close[i] - close[i-1]) for i >= 1; len = len(closes) - 1."""
    return [closes[i] - closes[i - 1] for i in range(1, len(closes))]


def wilder_rsi(closes, period=3):
    """Connors RSI(period) using Wilder smoothing on close-to-close changes.

    Returns the latest RSI value in [0, 100] or None if insufficient data.
    """
    if len(closes) < period + 1:
        return None
    diffs = compute_close_to_close_returns(closes)
    gains = [max(d, 0.0) for d in diffs]
    losses = [max(-d, 0.0) for d in diffs]
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for g, l in zip(gains[period:], losses[period:]):
        avg_gain = (avg_gain * (period - 1) + g) / period
        avg_loss = (avg_loss * (period - 1) + l) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def wilder_atr(true_ranges, period=14):
    """Wilder ATR with smoothing."""
    if len(true_ranges) < period:
        return None
    seed = sum(true_ranges[:period]) / period
    atr = seed
    for tr in true_ranges[period:]:
        atr = (atr * (period - 1) + tr) / period
    return atr


def compute_true_range(high, low, prev_close):
    if prev_close is None:
        return high - low
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


def long_entry_signal(rsi, threshold=15):
    """RSI < threshold triggers long entry (oversold)."""
    if rsi is None:
        return False
    return rsi < threshold


def long_exit_signal(rsi, threshold=55):
    """RSI > threshold triggers long exit (mean-reversion complete)."""
    if rsi is None:
        return False
    return rsi > threshold


def short_entry_signal(rsi, threshold=85):
    """RSI > threshold triggers short entry (overbought)."""
    if rsi is None:
        return False
    return rsi > threshold


def short_exit_signal(rsi, threshold=45):
    """RSI < threshold triggers short exit (mean-reversion complete)."""
    if rsi is None:
        return False
    return rsi < threshold


def compute_stop_price(entry_price, atr_entry, side, multiplier=2.0):
    """ATR-based 2N stop placement."""
    if side == "long":
        return entry_price - multiplier * atr_entry
    if side == "short":
        return entry_price + multiplier * atr_entry
    raise ValueError(f"Unknown side: {side!r}")


def compute_position_shares(equity, atr_entry, stop_multiplier=2.0, risk_pct=0.005):
    """0.5% per-trade risk sizing (DA3=B) in SHARES (cash equity).

    risk_dollars = risk_pct * equity
    risk_per_share = stop_multiplier * atr_entry  (the 2N stop distance, $ per share)
    shares = floor(risk_dollars / risk_per_share)
    """
    if atr_entry is None or atr_entry <= 0 or stop_multiplier <= 0:
        return 0
    risk_per_share = stop_multiplier * atr_entry
    raw = (risk_pct * equity) / risk_per_share
    return int(raw)


def portfolio_can_open(open_position_count, max_total_positions=3):
    """DA20 portfolio cap gate: True iff a new position can be opened."""
    return open_position_count < max_total_positions


def add_pyramid_unit(*args, **kwargs):
    """Pyramid is FORBIDDEN. Raises RuntimeError per DA20."""
    raise RuntimeError(
        "PYRAMID_FORBIDDEN: s14-d1-cross-sector max_positions_per_name = 1; pyramid mechanism "
        "is structurally forbidden per SEAL invariant no_pyramid_per_signal (DA20)."
    )


# --- Algo class ---

class Algo(_QCAlgorithmBase):
    """s14-d1-cross-sector cash-equity AAPL/JPM/XOM RSI(3) bi-directional algorithm.

    P3 BUILD scope: structural skeleton + safety contracts. NO backtest execution authorized.
    """

    def Initialize(self):  # noqa: N802 (QC API name)
        # C1: LiveMode refusal
        if self.LiveMode:
            raise Exception(
                "LIVE_PATH_DETECTED: s14-d1-aapl-jpm-xom-cross-sector-cash-equity-rsi-3-bi-directional "
                "is paper-only forever; refuse to run in live mode."
            )

        self.config = dict(CONFIG)

        # C3: safety counters
        self._stale_fill_warning_count = 0
        self._forbidden_action_attempts = []
        self._forbidden_action_attempts_detected = self._forbidden_action_attempts
        # cross-sector specific disclosure counters
        self._rsi_3_signal_count = 0
        self._atr_stop_breach_count = 0
        self._rsi_long_count = 0
        self._rsi_short_count = 0
        self._open_positions = {}  # per-symbol open position state
        # unique-day counters
        self._signal_dates_seen = set()
        self._stop_breach_dates_seen = set()

        # C8 lifecycle
        self._operational_status = "ACTIVE_RESEARCH"

        # C2: engine-truth date cross-check
        if _QC_AVAILABLE and self.StartDate is not None and self.EndDate is not None:
            self._initialize_date_cross_check()

    def all_safety_warnings_zero(self):
        """C3 universal safety counter rollup."""
        return self._stale_fill_warning_count == 0

    def open_position_count(self):
        """Number of currently-open positions across the basket (DA20 cap input)."""
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
            f"({cfg_is_start}..{cfg_is_end}) nor CONFIG OOS "
            f"({cfg_oos_start}..{cfg_oos_end})"
        )

    @staticmethod
    def compute_deterministic_run_id(
        tier_spec_seal,
        plan_lock_seal,
        plan_doc_sha256,
        phase_literal_tag,
        algo_version_for_run_id,
        engine_start_date,
        engine_end_date,
    ):
        """C2 deterministic run_id."""
        h = _hashlib.sha256()
        for piece in (
            tier_spec_seal,
            plan_lock_seal,
            plan_doc_sha256 or "",
            phase_literal_tag,
            algo_version_for_run_id,
            str(engine_start_date),
            str(engine_end_date),
        ):
            if isinstance(piece, bytes):
                h.update(piece)
            else:
                h.update(str(piece).encode("utf-8"))
            h.update(b"|")
        return h.hexdigest()[:12]

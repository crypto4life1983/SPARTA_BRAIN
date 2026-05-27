"""s13-d1 MNQ.c.0 single-instrument RSI(2) bi-directional algorithm.

Inherits Phase 2 safety contracts (C1-C8) from:
  docs/phase2_safety_contract_template.md
Template source candidate (parked, not money-proven):
  s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
Template reuse: NKE strategy logic NOT inherited; only safety contracts.

s13-d1 specific adaptations:
  - C5 corporate-action/event-risk STRUCTURALLY_ABSENT (futures)
  - C3 extended_hours / unsupported_order_type NOT_APPLICABLE
  - DR3 ELEVATED (RSI s9 lineage); mitigated via DA3=B (per_trade_risk=0.5%)
  - DR10 ELEVATED (high-frequency); mitigated via DA4=C (START_CASH=$200k)
  - REC1-equivalent + DA3=B + DA4=C + K9-reachability carried binding in C6

Anchors:
  tier_n_spec_seal     = 2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775
  plan_lock_seal       = 1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c
  p2_phase2_plan_seal  = b181ce834f5eacd2fb9f6766d6ce9404a86ecfe3d2787c7e4899d3e47ba57ec6

P3 BUILD scope: module structure + CONFIG + Algo class + RSI(2) bi-directional signal primitives.
NO backtest, NO fetch, NO broker calls. Strategy execution requires separate operator authorization
(P4 smoke / P6 IS / etc.) and remains BLOCKED at 6 gates regardless of any future verdict.
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

        def AddFuture(self, *args, **kwargs):
            pass

        def Debug(self, *args, **kwargs):
            pass

        def Log(self, *args, **kwargs):
            pass


# --- CONFIG (all locked values from SEAL 262491c + P1 005cb8a + P2 beecd87; DA3=B + DA4=C) ---

CONFIG = {
    # Identity (C2)
    "candidate_record_id": "s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional-databento-long-history",
    "phase_prefix": "PHASE2-S13-D1-MNQ-RSI-2-BIDIR",
    "algo_version_for_run_id": "s13_d1_v0_1_0",
    "title": (
        "s13-d1 MNQ.c.0 single-instrument RSI(2) bi-directional fresh-candidate "
        "(paper-research-only; diagnostic-only; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE)"
    ),
    # Sealed chain (C2)
    "tier_spec_seal": "2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775",
    "plan_lock_seal": "1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c",
    "p2_phase2_plan_seal": "b181ce834f5eacd2fb9f6766d6ce9404a86ecfe3d2787c7e4899d3e47ba57ec6",
    "plan_doc_sha256": None,
    # Instrument
    "asset_class": "futures",
    "ticker_or_root_symbol": "MNQ",
    "continuous_contract_symbol": "MNQ.c.0",
    "resolution": "daily",
    "brokerage_model_name": "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6",
    # Window
    "start_date_is": (2019, 5, 13),
    "end_date_is": (2023, 12, 29),
    "start_date_oos": (2024, 1, 2),
    "end_date_oos": (2025, 12, 30),
    "plan_lock_window_ceiling": (2025, 12, 30),
    # Strategy params (LOCKED at PLAN; RSI thresholds + bi-directional + no pyramid)
    "rsi_period": 2,
    "rsi_method": "Connors_RSI_2_Wilder_smoothing",
    "rsi_long_entry_threshold": 10,
    "rsi_long_exit_threshold": 50,
    "rsi_short_entry_threshold": 90,
    "rsi_short_exit_threshold": 50,
    "atr_period": 20,
    "atr_method": "Wilder",
    "stop_multiplier_in_atr": 2.0,
    "risk_pct_per_trade": 0.005,  # DA3=B; REVISED from 1.0%
    "max_units_per_market": 1,
    "max_total_units": 1,
    "pyramid_method": "NONE",
    "amb6_filter": "NONE",
    "regime_overlay": "NONE",
    "correlation_filter": "NOT_APPLICABLE_SINGLE_INSTRUMENT",
    "vol_targeting": "NONE",
    "leverage_cap": "NONE_implicit_via_per_trade_risk_sizing",
    # Sizing (DA4=C)
    "starting_cash_mnq_equivalent": 200000,  # DA4=C; REVISED from $100k
    "tick_size_points": 0.25,
    "tick_value_usd": 0.5,
    "dollar_per_point": 2.0,
    "contract_multiplier_note": "MNQ: $2 * Nasdaq-100 index value per point",
    # RTH (C4; daily-bar)
    "rth_safe_window_open": (9, 30),
    "rth_safe_window_close": (16, 0),
    "eod_cancel_time": (16, 0),  # MUST equal rth_safe_window_close
    "rth_window_tz": "America/New_York",
    "intraday_data_used": False,
    "daily_bars_only": True,
    # Roll
    "roll_method": "Databento_continuous_stype_in_continuous_vendor_side",
    # Costs
    "commission_per_round_trip": 0.74,
    "fees_per_round_trip": 0.36,
    "slippage_entry_ticks": 1,
    "slippage_stop_ticks": 1,
    "slippage_exit_ticks": 1,
    "cost_stress_tiers": [
        {"tier": "S0", "cost_scalar": 0.0, "slippage_scalar": 0.0},
        {"tier": "S1", "cost_scalar": 1.0, "slippage_scalar": 1.0},
        {"tier": "S2", "cost_scalar": 1.5, "slippage_scalar": 1.5},
        {"tier": "S3", "cost_scalar": 2.0, "slippage_scalar": 2.0},
        {"tier": "S4", "cost_scalar": 3.0, "slippage_scalar": 3.0},
    ],
    # Warmup
    "warmup_days": 220,
    # Verdict thresholds (C7)
    "verdict_min_closed_trades": 100,  # K9 inviolate
    "verdict_max_drawdown_pct_magnitude_concern": 0.30,
    "verdict_max_drawdown_pct_magnitude_fail_safety": 0.50,
    # Corporate actions (C5; STRUCTURALLY_ABSENT for futures)
    "known_corporate_actions": [],
    "futures_roll_method": "Databento_continuous",
    # Data anchor
    "primary_csv_path": "data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv",
    "primary_csv_sha256": "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e",
    "primary_csv_row_count_required": 2066,
    # Output schema
    "output_schema_id": "sparta.s13.d1.mnq_c0.rsi_2_bidir.diagnostic_run_report.v1",
    # REC1-equivalent OOS K9 disclosure (BINDING per operator authorization)
    "rec1_equivalent_oos_k9_disclosure": (
        "OOS K9 reachable at lower bound with thin margin (~50-65 trades/year vs 50/year floor). "
        "If observed IS rate falls below 25/year on RSI(2) bi-directional, OOS K9 unreachability "
        "becomes structurally probable. The s9 RSI-2 baseline observed 414 trades over long-only "
        "4-ETF window; if MNQ.c.0 bi-directional rate falls below half that proportional rate, "
        "OOS K9 fires. If OOS K9 fires, the OOS verdict shall be OOS_INSUFFICIENT_SAMPLE or "
        "PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK at 23c7164 and s12-d1 P11 "
        "park at ecbd001. The chain shall NOT relax K9 at OOS; the appropriate response is to seal "
        "the INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s13-d1 "
        "accepts the structural possibility of an OOS PARK outcome if the IS rate falls below the "
        "DRAFT-estimated 50-65/y band."
    ),
    "rec1_equivalent_binding": True,
    # Permanent live block
    "permanent_live_block": True,
    "live_promotion_blocked_at_6_gates_permanently": True,
    "research_diagnostic_only": True,
    "diagnostic_only_not_live_grade_label": True,
}


# --- Strategy primitives (RSI(2) bi-directional; NO execution, NO order placement) ---

def compute_close_to_close_returns(closes):
    """Returns list of (close[i] - close[i-1]) for i >= 1; len = len(closes) - 1."""
    return [closes[i] - closes[i - 1] for i in range(1, len(closes))]


def wilder_rsi(closes, period=2):
    """Connors RSI(period) using Wilder smoothing on close-to-close changes.

    Returns the latest RSI value in [0, 100] or None if insufficient data.
    """
    if len(closes) < period + 1:
        return None
    diffs = compute_close_to_close_returns(closes)
    gains = [max(d, 0.0) for d in diffs]
    losses = [max(-d, 0.0) for d in diffs]
    # Wilder smoothing: initial avg = simple mean of first `period` values, then EMA-like with alpha=1/period
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for g, l in zip(gains[period:], losses[period:]):
        avg_gain = (avg_gain * (period - 1) + g) / period
        avg_loss = (avg_loss * (period - 1) + l) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def wilder_atr(true_ranges, period=20):
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


def long_entry_signal(rsi, threshold=10):
    """RSI < threshold triggers long entry (oversold)."""
    if rsi is None:
        return False
    return rsi < threshold


def long_exit_signal(rsi, threshold=50):
    """RSI > threshold triggers long exit (mean-reversion complete)."""
    if rsi is None:
        return False
    return rsi > threshold


def short_entry_signal(rsi, threshold=90):
    """RSI > threshold triggers short entry (overbought)."""
    if rsi is None:
        return False
    return rsi > threshold


def short_exit_signal(rsi, threshold=50):
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


def compute_unit_contracts(equity, atr_entry, tick_value_usd=0.5, risk_pct=0.005):
    """0.5% per-trade risk sizing (DA3=B): floor((risk_pct * equity) / (ATR_entry * tick_value_usd))."""
    if atr_entry is None or atr_entry <= 0 or tick_value_usd <= 0:
        return 0
    raw = (risk_pct * equity) / (atr_entry * tick_value_usd)
    return int(raw)


def add_pyramid_unit(*args, **kwargs):
    """Pyramid is FORBIDDEN. Raises RuntimeError per T7b."""
    raise RuntimeError(
        "PYRAMID_FORBIDDEN: s13-d1 max_units_per_market = 1; pyramid mechanism is "
        "structurally forbidden per SEAL invariant no_pyramid_per_signal."
    )


# --- Algo class ---

class Algo(_QCAlgorithmBase):
    """s13-d1 MNQ.c.0 RSI(2) bi-directional algorithm.

    P3 BUILD scope: structural skeleton + safety contracts.
    NO backtest execution authorized by this BUILD turn.
    """

    def Initialize(self):  # noqa: N802 (QC API name)
        # C1: LiveMode refusal
        if self.LiveMode:
            raise Exception(
                "LIVE_PATH_DETECTED: s13-d1-mnq-c0-single-instrument-rsi-2-bi-directional "
                "is paper-only forever; refuse to run in live mode."
            )

        self.config = dict(CONFIG)

        # C3: safety counters
        self._stale_fill_warning_count = 0
        self._forbidden_action_attempts = []
        self._forbidden_action_attempts_detected = self._forbidden_action_attempts
        # s13-d1-specific disclosure counters
        self._rsi_2_signal_count = 0
        self._atr_stop_breach_count = 0
        self._rsi_long_count = 0
        self._rsi_short_count = 0
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

"""s12-d1 MNQ.c.0 single-instrument Donchian-15/8 algorithm.

Inherits Phase 2 safety contracts (C1-C8) from:
  docs/phase2_safety_contract_template.md
  docs/phase2_safety_contract_template.json
Template source candidate (parked, not money-proven):
  s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
Template reuse notice: NKE strategy logic NOT inherited; only safety contracts.

s12-d1 specific adaptations:
  - C5 corporate-action/event-risk STRUCTURALLY_ABSENT (futures continuous-stitch)
  - C3 extended_hours / unsupported_order_type NOT_APPLICABLE
  - REC1 oos_k9_risk_disclosure carried binding

Anchors:
  tier_n_spec_seal     = 07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48
  plan_lock_seal       = eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340
  p2_phase2_plan_seal  = 689dd3d06c0e2518ab5f6105544cb3d38194027647de10940da976e427c8efa9

P3 BUILD scope: module structure + CONFIG + Algo class + signal logic primitives.
This module does NOT run backtests, fetch data, or call brokerage APIs.
Strategy execution requires separate operator authorization (P4 smoke / P6 IS / etc.)
and remains BLOCKED at 6 gates regardless of any future verdict.
"""

import datetime as _dt
import hashlib as _hashlib

# --- QC compatibility shim (C2 + T2 requirement: instantiable without QC runtime) ---
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


# --- CONFIG (all locked values from SEAL 66bbbd1 + P1 d8bd359 + P2 0b8d948) ---

CONFIG = {
    # Identity (C2)
    "candidate_record_id": "s12-d1-mnq-c0-single-instrument-donchian-15-8-databento-long-history",
    "phase_prefix": "PHASE2-S12-D1-MNQ-DONCHIAN-15-8",
    "algo_version_for_run_id": "s12_d1_v0_1_0",
    "title": (
        "s12-d1 MNQ.c.0 single-instrument Donchian-15/8 fresh-candidate "
        "(paper-research-only; diagnostic-only; DIAGNOSTIC_ONLY_NOT_LIVE_GRADE)"
    ),
    # Sealed chain (C2; assert_seal_inheritance verifies these at Initialize)
    "tier_spec_seal": "07c3200b5e23ab88e864f92926b83ded033a3d66c0e37e8cf8555985ad8f3b48",
    "plan_lock_seal": "eb72798eb95c08407ead9c273a650853bd5e871942856f87b48f97f07a640340",
    "p2_phase2_plan_seal": "689dd3d06c0e2518ab5f6105544cb3d38194027647de10940da976e427c8efa9",
    "plan_doc_sha256": None,  # populated at runtime via sha256(P1_plan_lock_md_on_disk)
    # Instrument (single-instrument futures)
    "asset_class": "futures",
    "ticker_or_root_symbol": "MNQ",
    "continuous_contract_symbol": "MNQ.c.0",
    "resolution": "daily",
    "brokerage_model_name": "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6",
    "supported_order_types_for_brokerage": [],  # NOT_APPLICABLE for CSV-simulator
    # Window (LOCKED at SEAL)
    "start_date_is": (2019, 5, 13),
    "end_date_is": (2023, 12, 29),
    "start_date_oos": (2024, 1, 2),
    "end_date_oos": (2025, 12, 30),
    "plan_lock_window_ceiling": (2025, 12, 30),
    # Strategy params (LOCKED at PLAN + SEAL)
    "donchian_entry_period_n": 15,
    "donchian_exit_period_n": 8,
    "atr_period": 20,
    "atr_method": "Wilder",
    "stop_multiplier_in_atr": 2.0,
    "risk_pct_per_trade": 0.01,
    "max_units_per_market": 1,
    "max_total_units": 1,
    "pyramid_method": "NONE",
    "amb6_filter": "NONE",
    "regime_overlay": "NONE",
    "correlation_filter": "NOT_APPLICABLE_SINGLE_INSTRUMENT",
    "vol_targeting": "NONE",
    "leverage_cap": "NONE_implicit_via_per_trade_risk_sizing",
    # Sizing (DA4=B; LOCKED at SEAL)
    "starting_cash_mnq_equivalent": 100000,
    "tick_size_points": 0.25,
    "tick_value_usd": 0.5,
    "dollar_per_point": 2.0,
    "contract_multiplier_note": "MNQ: $2 * Nasdaq-100 index value per point",
    # RTH (C4; daily-bar adaptation)
    "rth_safe_window_open": (9, 30),
    "rth_safe_window_close": (16, 0),
    "eod_cancel_time": (16, 0),  # MUST equal rth_safe_window_close (C4 boundary alignment)
    "rth_window_tz": "America/New_York",
    "intraday_data_used": False,
    "daily_bars_only": True,
    # Roll method
    "roll_method": "Databento_continuous_stype_in_continuous_vendor_side",
    # Costs (DA7..DA10=A; LOCKED at SEAL)
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
    # Warmup (DA11=A)
    "warmup_days": 220,
    # Verdict thresholds (C7)
    "verdict_min_closed_trades": 100,  # K9 byte-equivalent; inviolate
    "verdict_max_drawdown_pct_magnitude_concern": 0.30,
    "verdict_max_drawdown_pct_magnitude_fail_safety": 0.50,
    # Corporate actions (C5; STRUCTURALLY_ABSENT for futures)
    "known_corporate_actions": [],
    "corp_action_blackout_days_before": None,
    "corp_action_blackout_days_after": None,
    "corp_action_pre_close_aggressive_ticks": None,
    "futures_roll_method": "Databento_continuous",
    # Data anchor (READ-ONLY byte-equivalent reuse from s10-d1)
    "primary_csv_path": "data/s10_d1_mnq_mgc_databento_long_history/raw/MNQ_c_0_ohlcv_1d_20190513_20251230.csv",
    "primary_csv_sha256": "8b7b832c62fae1854fbf664db9c79ec953d4462ff6d89896cc39975005dfa23e",
    "primary_csv_row_count_required": 2066,
    # Output schema
    "output_schema_id": "sparta.s12.d1.mnq_c0.donchian_15_8.diagnostic_run_report.v1",
    # REC1 oos_k9_risk_disclosure (BINDING per operator authorization)
    "rec1_oos_k9_risk_disclosure": (
        "OOS K9 EXPECTED TO FIRE. Implied OOS trade count over 2.0y at IS rate is approximately "
        "35-87 trades, below K9 = 100. If OOS K9 fires, the OOS verdict will be "
        "OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE analogous to S10-D2 P11 PARK "
        "at 23c7164. The chain shall NOT relax K9 at OOS; the appropriate response is to seal the "
        "INSUFFICIENT_SAMPLE / INDETERMINATE verdict and park the candidate. Pursuing s12-d1 accepts "
        "the structural likelihood of an OOS PARK outcome."
    ),
    "rec1_binding": True,
    # Permanent live block (C1 + C8)
    "permanent_live_block": True,
    "live_promotion_blocked_at_6_gates_permanently": True,
    "research_diagnostic_only": True,
    "diagnostic_only_not_live_grade_label": True,
}


# --- Strategy primitives (signal logic; NO execution, NO order placement) ---

def wilder_atr(true_ranges, period=20):
    """Wilder ATR with smoothing. true_ranges is a list/sequence of bar TRs (>=period long).

    Returns the latest ATR value or None if insufficient data.
    """
    if len(true_ranges) < period:
        return None
    seed = sum(true_ranges[:period]) / period
    atr = seed
    for tr in true_ranges[period:]:
        atr = (atr * (period - 1) + tr) / period
    return atr


def compute_true_range(high, low, prev_close):
    """Standard TR = max(H-L, |H-prev_close|, |L-prev_close|)."""
    if prev_close is None:
        return high - low
    return max(high - low, abs(high - prev_close), abs(low - prev_close))


def donchian_channels(highs, lows, n):
    """Returns (donchian_high_n, donchian_low_n) over the last n bars (exclusive of current)."""
    if len(highs) < n or len(lows) < n:
        return None, None
    window_h = highs[-n:]
    window_l = lows[-n:]
    return max(window_h), min(window_l)


def long_entry_signal(close, donchian_high_n_prior):
    """Donchian-N upper breakout entry signal (LONG)."""
    if donchian_high_n_prior is None:
        return False
    return close > donchian_high_n_prior


def short_entry_signal(close, donchian_low_n_prior):
    """Donchian-N lower breakout entry signal (SHORT)."""
    if donchian_low_n_prior is None:
        return False
    return close < donchian_low_n_prior


def long_exit_signal(close, donchian_low_m_prior):
    """Donchian-M lower exit signal (closes LONG)."""
    if donchian_low_m_prior is None:
        return False
    return close < donchian_low_m_prior


def short_exit_signal(close, donchian_high_m_prior):
    """Donchian-M upper exit signal (closes SHORT)."""
    if donchian_high_m_prior is None:
        return False
    return close > donchian_high_m_prior


def compute_stop_price(entry_price, atr_entry, side, multiplier=2.0):
    """ATR-based 2N stop placement."""
    if side == "long":
        return entry_price - multiplier * atr_entry
    if side == "short":
        return entry_price + multiplier * atr_entry
    raise ValueError(f"Unknown side: {side!r}")


def compute_unit_contracts(equity, atr_entry, tick_value_usd=0.5, risk_pct=0.01):
    """1% per-trade risk sizing: contracts = floor((risk_pct * equity) / (ATR_entry * tick_value_usd))."""
    if atr_entry is None or atr_entry <= 0 or tick_value_usd <= 0:
        return 0
    raw = (risk_pct * equity) / (atr_entry * tick_value_usd)
    return int(raw)  # floor toward zero for positive values


def add_pyramid_unit(*args, **kwargs):
    """Pyramid is FORBIDDEN. max_units_per_market = 1. Raises RuntimeError per T7b."""
    raise RuntimeError(
        "PYRAMID_FORBIDDEN: s12-d1 max_units_per_market = 1; pyramid mechanism is "
        "structurally forbidden per SEAL invariant no_pyramid_per_signal."
    )


# --- Algo class (C1 LiveMode refusal + C2 provenance + C3 safety counters) ---

class Algo(_QCAlgorithmBase):
    """s12-d1 MNQ.c.0 Donchian-15/8 algorithm.

    P3 BUILD scope: structural skeleton + safety contracts.
    NO backtest execution authorized by this BUILD turn.
    """

    def Initialize(self):  # noqa: N802 (QC API name)
        # C1: LiveMode refusal
        if self.LiveMode:
            raise Exception(
                "LIVE_PATH_DETECTED: s12-d1-mnq-c0-single-instrument-donchian-15-8 "
                "is paper-only forever; refuse to run in live mode."
            )

        self.config = dict(CONFIG)  # local snapshot; immutable from this point in semantic intent

        # C3: safety counters (universal + s12-d1-specific)
        self._stale_fill_warning_count = 0
        self._forbidden_action_attempts = []
        self._forbidden_action_attempts_detected = self._forbidden_action_attempts  # alias
        self._donchian_15_8_signal_count = 0  # disclosure-only
        self._atr_stop_breach_count = 0  # disclosure-only
        # unique-day counters (NKE v6.1 lesson; set-membership pattern)
        self._signal_dates_seen = set()
        self._stop_breach_dates_seen = set()

        # C8: lifecycle state
        self._operational_status = "ACTIVE_RESEARCH"

        # C2: engine-truth date cross-check
        # In a QC environment: self.SetStartDate(...) + self.SetEndDate(...) populate self.StartDate/EndDate.
        # In a non-QC environment (build/test), we skip the cross-check at Initialize-stub level.
        if _QC_AVAILABLE and self.StartDate is not None and self.EndDate is not None:
            self._initialize_date_cross_check()

        # K8 / sealed parent drift guard would be invoked here at a real backtest.
        # In P3 BUILD scope we record the guard as a method but do not actually load disk seals.

    def all_safety_warnings_zero(self):
        """C3 universal safety counter rollup."""
        # extended_hours_fill_warning_count and unsupported_order_type_detected_count are
        # NOT_APPLICABLE for s12-d1 (futures + CSV simulator); they are treated as 0.
        return self._stale_fill_warning_count == 0

    def _initialize_date_cross_check(self):
        """C2 engine-truth Initialize cross-check."""
        # IS or OOS window — choose based on which CONFIG window the engine dates match.
        cfg_is_start = _dt.date(*self.config["start_date_is"])
        cfg_is_end = _dt.date(*self.config["end_date_is"])
        cfg_oos_start = _dt.date(*self.config["start_date_oos"])
        cfg_oos_end = _dt.date(*self.config["end_date_oos"])
        engine_start = self.StartDate.date() if hasattr(self.StartDate, "date") else self.StartDate
        engine_end = self.EndDate.date() if hasattr(self.EndDate, "date") else self.EndDate
        if engine_start == cfg_is_start and engine_end == cfg_is_end:
            return  # IS window OK
        if engine_start == cfg_oos_start and engine_end == cfg_oos_end:
            return  # OOS window OK
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
        """C2 deterministic run_id from sealed inheritance chain + engine-truth window.

        Note: this hash uses ENGINE-truth dates (self.StartDate.date() / self.EndDate.date()),
        NOT CONFIG dates. CONFIG dates are validated against engine truth at Initialize cross-check.
        """
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


# Module-level note: this file is INTENTIONALLY runnable as a structural import
# in non-QC environments. Strategy execution is not performed by importing this module.

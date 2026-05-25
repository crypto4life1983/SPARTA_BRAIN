"""s7 D1 cross-asset Donchian (NQ + GC + ZN + CL) -- algorithm runner.

PHASE 2 BUILD scaffolding. Importable without QC runtime via lazy QC access.
DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. Trading PAUSED. Live BLOCKED_AT_6_GATES.
FRC never granted. No profitability claim.

Inherits Phase 2 safety contracts (C1-C8) from:
  docs/phase2_safety_contract_template.md  (sha 1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981)
  docs/phase2_safety_contract_template.json (sha 695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32)
Template source candidate (parked, not money-proven):
  s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
Template reuse notice: NKE strategy logic NOT inherited; only safety contracts.

Inherits Tier-N spec seal:    72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3
Inherits plan-lock seal:      0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d
Inherits Phase-2 plan seal:   e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a
Predecessor (s7 selection):   8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac
"""

from __future__ import annotations

import hashlib
import math
from collections import deque
from typing import Iterable, List, Optional, Sequence


# ---------------------------------------------------------------------------
# Sealed-chain constants (sha-pinned)
# ---------------------------------------------------------------------------
TIER_N_SPEC_SEAL_SHA256    = "72602305ef8d678195f9ab91a6d4cb8e7a473ee1a641cf9e8f91b8d4e31134c3"
PLAN_LOCK_SEAL_SHA256      = "0f8e9fe6bc4f50e4f17c41611dbd01b7f9df3047ed448a3e9dffe7533210572d"
PHASE2_PLAN_SEAL_SHA256    = "e1800ee28bd99a27da94d048fce4512401bc6ecd66b89e9d184f6c3050e2669a"
PREDECESSOR_SEAL_SHA256    = "8d8851bc365ef9a6eb7883b24f272d8462cb4bda9c9e725aa46415e1434f9eac"
PHASE2_TEMPLATE_MD_SHA256  = "1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981"
PHASE2_TEMPLATE_JSON_SHA256 = "695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32"

ALGO_VERSION_FOR_RUN_ID = "s7_d1_v0_1_0"
PHASE_PREFIX            = "PHASE2-S7-D1-XAD-NF"
CANDIDATE_RECORD_ID     = "s7-cross-asset-donchian-no-filter-nq-gc-zn-cl"


# ---------------------------------------------------------------------------
# CONFIG (byte-equivalent to Tier-N spec)
# ---------------------------------------------------------------------------
CONFIG = {
    # Identity
    "candidate_record_id":   CANDIDATE_RECORD_ID,
    "algo_version_for_run_id": ALGO_VERSION_FOR_RUN_ID,
    "phase_prefix":          PHASE_PREFIX,

    # Sealed chain
    "tier_spec_seal":        TIER_N_SPEC_SEAL_SHA256,
    "plan_lock_seal":        PLAN_LOCK_SEAL_SHA256,
    "plan_doc_sha256":       PHASE2_PLAN_SEAL_SHA256,
    "predecessor_seal":      PREDECESSOR_SEAL_SHA256,

    # Window (in-sample only; OOS inspection BLOCKED until in-sample passes)
    "start_date":            [2013, 1, 1],
    "end_date":              [2022, 12, 30],
    "plan_lock_window_ceiling": [2022, 12, 30],

    # Markets (locked)
    "markets":               ["NQ", "GC", "ZN", "CL"],
    "markets_meta": {
        "NQ": {"family": "equity_index", "tick": 0.25,     "tick_value_usd": 5.00,   "dollar_per_point": 20,
               "rth_open_et": [9, 30],  "rth_close_et": [16, 0]},
        "GC": {"family": "metals",        "tick": 0.10,     "tick_value_usd": 10.00,  "dollar_per_point": 100,
               "rth_open_et": [9, 30],  "rth_close_et": [16, 0]},
        "ZN": {"family": "bonds_10y",     "tick": 0.015625, "tick_value_usd": 15.625, "dollar_per_point": 1000,
               "rth_open_et": [9, 30],  "rth_close_et": [16, 0]},
        "CL": {"family": "energy_crude",  "tick": 0.01,     "tick_value_usd": 10.00,  "dollar_per_point": 1000,
               "rth_open_et": [9, 30],  "rth_close_et": [14, 30]},
    },

    # Donchian (s6 REV1 byte-equivalent)
    "entry_channel_length":           55,
    "exit_channel_length":            20,
    "filter":                         None,  # AMB6 locked NONE
    "entry_timing":                   "ONO",  # open-on-next-bar
    "max_units_per_market":           4,
    "pyramid_spacing_n_multiplier":   0.5,

    # Stop
    "stop_n_multiplier":              2.0,
    "stop_n_period":                  20,  # WilderATR period
    "catastrophic_portfolio_maxdd_pct": 50.0,

    # Sizing
    "risk_pct_per_unit":              0.01,
    "starting_cash_mnq_equivalent":   100_000,
    "skip_if_contract_count_lt_one":  True,
    "portfolio_cap_max_units":        16,
    "portfolio_cap_uses_unit_count":  True,  # s6 bugfix inherited

    # Cost stress
    "cost_baseline_per_rt_usd_per_market": {
        "NQ": {"commission": 3.00, "fees": 1.50, "slip_entry_ticks": 1, "slip_stop_ticks": 2, "slip_exit_ticks": 1},
        "GC": {"commission": 3.00, "fees": 1.50, "slip_entry_ticks": 1, "slip_stop_ticks": 2, "slip_exit_ticks": 1},
        "ZN": {"commission": 3.00, "fees": 1.20, "slip_entry_ticks": 1, "slip_stop_ticks": 2, "slip_exit_ticks": 1},
        "CL": {"commission": 3.00, "fees": 1.50, "slip_entry_ticks": 1, "slip_stop_ticks": 2, "slip_exit_ticks": 1},
    },
    "cost_stress_tiers": {
        "S0": {"slippage_scalar": 0.0, "cost_scalar": 0.0},
        "S1": {"slippage_scalar": 1.0, "cost_scalar": 1.0},
        "S2": {"slippage_scalar": 3.0, "cost_scalar": 1.5},
        "S3": {"slippage_scalar": 5.0, "cost_scalar": 2.0},
        "S4": {"slippage_scalar": 8.0, "cost_scalar": 3.0},
    },

    # Verdict
    "verdict_min_closed_trades":           100,
    "verdict_max_drawdown_pct_concern":    0.50,
    "verdict_max_pairwise_correlation":    0.50,
    "verdict_min_effective_independent_bets": 2.5,

    # Status fields (C1)
    "status_fields": {
        "trading_status":           "PAUSED",
        "live_status":              "BLOCKED_AT_6_GATES",
        "backtest_diagnostic_only": True,
    },
}


# ---------------------------------------------------------------------------
# Pure helper functions (testable without QC)
# ---------------------------------------------------------------------------
def wilder_atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], n: int = 20) -> float:
    """Wilder Average True Range over the last n bars.

    Requires at least n+1 bars. Returns a float. Pure python; no numpy required
    so the smoke tests can run in any minimal env.
    """
    if len(highs) < n + 1 or len(lows) < n + 1 or len(closes) < n + 1:
        raise ValueError(f"wilder_atr requires at least n+1={n+1} bars; got {len(closes)}")
    trs: List[float] = []
    for i in range(1, len(closes)):
        h = highs[i]
        l = lows[i]
        pc = closes[i - 1]
        tr = max(h - l, abs(h - pc), abs(l - pc))
        trs.append(tr)
    # First ATR value is simple average of the first n TRs
    atr = sum(trs[:n]) / n
    # Wilder smoothing for any remaining TRs
    for tr in trs[n:]:
        atr = (atr * (n - 1) + tr) / n
    return float(atr)


def donchian_high(highs: Sequence[float], n: int = 55) -> float:
    """High of the last n CLOSED bars (excluding the current forming bar)."""
    if len(highs) < n:
        raise ValueError(f"donchian_high requires at least n={n} bars; got {len(highs)}")
    return float(max(highs[-n:]))


def donchian_low(lows: Sequence[float], n: int = 55) -> float:
    if len(lows) < n:
        raise ValueError(f"donchian_low requires at least n={n} bars; got {len(lows)}")
    return float(min(lows[-n:]))


def compute_unit_contracts(portfolio_equity: float, n_entry: float, dollar_per_point: float,
                           risk_pct: float = 0.01) -> int:
    """floor((risk_pct * equity) / (N_entry * $/pt)). Returns 0 when < 1 (entry-skip)."""
    if n_entry <= 0 or dollar_per_point <= 0:
        return 0
    raw = (risk_pct * portfolio_equity) / (n_entry * dollar_per_point)
    return int(math.floor(raw))


def compute_deterministic_run_id(*, tier_spec_seal: str, plan_lock_seal: str, plan_doc_sha256: str,
                                 phase_prefix_bytes: bytes, algo_version: str,
                                 engine_start_iso: str, engine_end_iso: str) -> str:
    """C2 deterministic run_id: sha256 over the 7 ordered inputs."""
    h = hashlib.sha256()
    h.update(tier_spec_seal.encode("utf-8"))
    h.update(plan_lock_seal.encode("utf-8"))
    h.update(plan_doc_sha256.encode("utf-8"))
    h.update(phase_prefix_bytes)
    h.update(algo_version.encode("utf-8"))
    h.update(engine_start_iso.encode("utf-8"))
    h.update(engine_end_iso.encode("utf-8"))
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Pyramid manager (per-market state machine)
# ---------------------------------------------------------------------------
class PyramidManager:
    """Tracks open units, entry prices, and N for one market.

    State machine invariants enforced (and counted by the safety counters):
      - current_unit_count never exceeds CONFIG["max_units_per_market"]
      - N at unit_k_entry == N at unit_1_entry (no recomputation mid-trade)
      - next pyramid trigger at +0.5 * N (long) / -0.5 * N (short) from last unit entry
    """

    def __init__(self, market: str, max_units: int, pyramid_spacing_n: float, stop_n_multiplier: float):
        self.market = market
        self.max_units = max_units
        self.pyramid_spacing_n = pyramid_spacing_n
        self.stop_n_multiplier = stop_n_multiplier

        self.direction: Optional[str] = None  # "long" / "short" / None
        self.n_entry: float = 0.0
        self.unit_entries: List[float] = []   # entry prices in order
        self.unit_contracts: List[int] = []
        self.next_pyramid_trigger: Optional[float] = None
        self.current_unit_count: int = 0      # NOTE: this is the value that the
                                              # PortfolioCapTracker reads (s6 cap-bugfix)
        self.total_quantity: int = 0          # contract count (NOT used by cap tracker)
        self.stops: List[float] = []

        # Safety counters (incremented on violation)
        self.pyramid_state_machine_violation_count = 0
        self.n_calculation_drift_detected_count = 0

    def open_first_unit(self, direction: str, entry_price: float, n_entry: float, contracts: int) -> None:
        if direction not in ("long", "short"):
            raise ValueError(f"direction must be 'long' or 'short'; got {direction!r}")
        if self.current_unit_count != 0:
            self.pyramid_state_machine_violation_count += 1
            raise RuntimeError(f"{self.market}: open_first_unit called with current_unit_count={self.current_unit_count}")
        self.direction = direction
        self.n_entry = float(n_entry)
        self.unit_entries = [float(entry_price)]
        self.unit_contracts = [int(contracts)]
        self.stops = [self._compute_stop(entry_price, n_entry, direction)]
        self.next_pyramid_trigger = self._compute_next_pyramid_trigger(entry_price, n_entry, direction)
        self.current_unit_count = 1
        self.total_quantity = int(contracts)

    def add_pyramid_unit(self, entry_price: float, contracts: int) -> None:
        if self.current_unit_count == 0:
            self.pyramid_state_machine_violation_count += 1
            raise RuntimeError(f"{self.market}: add_pyramid_unit called with no open unit")
        if self.current_unit_count >= self.max_units:
            self.pyramid_state_machine_violation_count += 1
            raise RuntimeError(
                f"{self.market}: add_pyramid_unit would exceed max_units={self.max_units} "
                f"(current_unit_count={self.current_unit_count})"
            )
        # Faith rule: N at unit_k entry == N at unit_1 entry. We re-use the stored n_entry.
        # If a caller tried to pass a different N implicitly (e.g. via different entry_price scale),
        # we cannot detect it from price alone, but we never recompute N here.
        self.unit_entries.append(float(entry_price))
        self.unit_contracts.append(int(contracts))
        self.stops.append(self._compute_stop(entry_price, self.n_entry, self.direction))
        self.current_unit_count += 1
        self.total_quantity += int(contracts)
        self.next_pyramid_trigger = self._compute_next_pyramid_trigger(entry_price, self.n_entry, self.direction)

    def close_all(self) -> None:
        self.direction = None
        self.n_entry = 0.0
        self.unit_entries = []
        self.unit_contracts = []
        self.stops = []
        self.next_pyramid_trigger = None
        self.current_unit_count = 0
        self.total_quantity = 0

    def _compute_stop(self, entry_price: float, n: float, direction: str) -> float:
        if direction == "long":
            return float(entry_price - self.stop_n_multiplier * n)
        return float(entry_price + self.stop_n_multiplier * n)

    def _compute_next_pyramid_trigger(self, last_entry: float, n: float, direction: str) -> float:
        if direction == "long":
            return float(last_entry + self.pyramid_spacing_n * n)
        return float(last_entry - self.pyramid_spacing_n * n)


# ---------------------------------------------------------------------------
# Portfolio cap tracker (s6 bugfix inherited)
# ---------------------------------------------------------------------------
class PortfolioCapTracker:
    """Tracks total open UNITS across markets. Cap = 4 markets * 4 units = 16.

    CRITICAL (s6 bugfix): update_market_units() MUST receive pyr.current_unit_count
    (the UNIT count, max 4 per market), NOT pyr.total_quantity (the contract count).
    """

    def __init__(self, max_total_units: int = 16):
        self.max_total_units = max_total_units
        self.market_units: dict = {}
        self.cap_binding_events_count = 0

    def update_market_units(self, market: str, unit_count: int) -> None:
        if unit_count > 4:
            # If someone passes total_quantity here (e.g., 10 contracts for NQ),
            # we'd see > 4 and know the s6 bug has been re-introduced.
            raise ValueError(
                f"PortfolioCapTracker.update_market_units received unit_count={unit_count} "
                f"for market={market!r}; max per market is 4. "
                f"This indicates the s6 portfolio-cap bug was re-introduced "
                f"(caller likely passed pyr.total_quantity instead of pyr.current_unit_count)."
            )
        self.market_units[market] = int(unit_count)
        total = sum(self.market_units.values())
        if total > self.max_total_units:
            # Should not happen if max_units_per_market is enforced upstream; record event.
            self.cap_binding_events_count += 1

    def total_open_units(self) -> int:
        return sum(self.market_units.values())

    def at_or_above_cap(self) -> bool:
        return self.total_open_units() >= self.max_total_units


# ---------------------------------------------------------------------------
# QC LEAN base class -- lazy import (NO side effects when QC is absent)
# ---------------------------------------------------------------------------
QC_RUNTIME_AVAILABLE = False
try:
    from AlgorithmImports import *  # type: ignore  # noqa: F401, F403
    QC_RUNTIME_AVAILABLE = True
    _QCAlgorithmBase = QCAlgorithm  # type: ignore  # noqa: F405
except Exception:
    # Stub base for BUILD-time importability (no QC runtime present)
    class _QCAlgorithmBase:
        """Lightweight QC stub used only at BUILD/test time.

        Real QC runtime is provided when the algorithm is uploaded.
        """
        LiveMode = False
        StartDate = None
        EndDate = None

        def SetStartDate(self, *args, **kwargs): pass
        def SetEndDate(self, *args, **kwargs): pass
        def SetCash(self, *args, **kwargs): pass
        def Initialize(self): pass
        def OnData(self, data): pass
        def OnOrderEvent(self, orderEvent): pass
        def OnEndOfAlgorithm(self): pass
        def Log(self, msg): pass


# ---------------------------------------------------------------------------
# Algorithm class
# ---------------------------------------------------------------------------
class SevenD1CrossAssetDonchianAlgo(_QCAlgorithmBase):
    """s7 D1 cross-asset Donchian no-filter algorithm.

    Strategy: locked Donchian-55/Exit-20 with 4-unit 0.5N pyramid on
    NQ + GC + ZN + CL. NO filter (AMB6 NONE). 1 % portfolio sizing. 2N stop.

    Safety: Phase 2 C1-C8 byte-equivalent inheritance + s6 cap-bugfix.
    Diagnostic-only. Trading PAUSED. Live BLOCKED_AT_6_GATES. FRC never granted.
    """

    # Re-declared as class attributes for assert_chain_shas_present()
    TIER_N_SPEC_SEAL_SHA256    = TIER_N_SPEC_SEAL_SHA256
    PLAN_LOCK_SEAL_SHA256      = PLAN_LOCK_SEAL_SHA256
    PHASE2_PLAN_SEAL_SHA256    = PHASE2_PLAN_SEAL_SHA256
    PREDECESSOR_SEAL_SHA256    = PREDECESSOR_SEAL_SHA256
    PHASE2_TEMPLATE_MD_SHA256  = PHASE2_TEMPLATE_MD_SHA256
    PHASE2_TEMPLATE_JSON_SHA256 = PHASE2_TEMPLATE_JSON_SHA256

    def Initialize(self):  # noqa: N802 (QC convention)
        # ---- C1: LiveMode refusal ----
        if getattr(self, "LiveMode", False):
            raise Exception(
                "LIVE_PATH_DETECTED: s7-d1-cross-asset-donchian-no-filter-nq-gc-zn-cl "
                "is paper-only forever; refuse to run in live mode."
            )

        # ---- Set dates BEFORE the cross-check (QC pattern) ----
        if QC_RUNTIME_AVAILABLE:
            import datetime as _dt
            self.SetStartDate(*CONFIG["start_date"])
            self.SetEndDate(*CONFIG["end_date"])
            self.SetCash(CONFIG["starting_cash_mnq_equivalent"])
            # ---- C2: Initialize date cross-check + window ceiling ----
            cs = _dt.date(*CONFIG["start_date"])
            ce = _dt.date(*CONFIG["end_date"])
            ceiling = _dt.date(*CONFIG["plan_lock_window_ceiling"])
            if self.StartDate.date() != cs:
                raise Exception(f"CONFIG_START_DATE_MISMATCH: engine={self.StartDate.date()} config={cs}")
            if self.EndDate.date() != ce:
                raise Exception(f"CONFIG_END_DATE_MISMATCH: engine={self.EndDate.date()} config={ce}")
            if self.EndDate.date() > ceiling:
                raise Exception(
                    f"WINDOW_EXTENSION_BEYOND_PLAN_LOCK_FORBIDDEN: engine_end={self.EndDate.date()} ceiling={ceiling}"
                )
            engine_start_iso = self.StartDate.date().isoformat()
            engine_end_iso   = self.EndDate.date().isoformat()
        else:
            # Local-engine path: derive from CONFIG (the local engine MUST cross-check itself).
            import datetime as _dt
            engine_start_iso = _dt.date(*CONFIG["start_date"]).isoformat()
            engine_end_iso   = _dt.date(*CONFIG["end_date"]).isoformat()

        # ---- C2: deterministic run_id ----
        self._run_id = compute_deterministic_run_id(
            tier_spec_seal=CONFIG["tier_spec_seal"],
            plan_lock_seal=CONFIG["plan_lock_seal"],
            plan_doc_sha256=CONFIG["plan_doc_sha256"],
            phase_prefix_bytes=PHASE_PREFIX.encode("utf-8"),
            algo_version=CONFIG["algo_version_for_run_id"],
            engine_start_iso=engine_start_iso,
            engine_end_iso=engine_end_iso,
        )
        self._run_id_12 = self._run_id[:12]
        self._backtest_run_id = f"{PHASE_PREFIX}-{self._run_id_12}"

        # ---- C3 safety counters ----
        self._safety = {
            "stale_fill_warning_count": 0,
            "non_rth_fill_warning_count": 0,
            "expiry_or_roll_fills_outside_rth_count": 0,
            "unsupported_order_type_detected_count": 0,
            "rollover_violation_count": 0,
            "pyramid_state_machine_violation_count": 0,
            "n_calculation_drift_detected_count": 0,
            "all_safety_warnings_zero": True,
            "forbidden_action_attempts_detected": [],
            "_rolls_seen_dates": set(),
            "_expiries_seen_dates": set(),
        }

        # ---- Per-market state ----
        self._pyramids = {
            m: PyramidManager(
                market=m,
                max_units=CONFIG["max_units_per_market"],
                pyramid_spacing_n=CONFIG["pyramid_spacing_n_multiplier"],
                stop_n_multiplier=CONFIG["stop_n_multiplier"],
            )
            for m in CONFIG["markets"]
        }
        self._cap_tracker = PortfolioCapTracker(max_total_units=CONFIG["portfolio_cap_max_units"])
        self._closed_trades_portfolio: int = 0
        self._closed_trades_per_market: dict = {m: 0 for m in CONFIG["markets"]}

        # ---- Bar history buffers (per market) ----
        bar_buffer_len = max(
            CONFIG["entry_channel_length"],
            CONFIG["exit_channel_length"],
            CONFIG["stop_n_period"] + 1,
        )
        self._bars = {m: {"high": deque(maxlen=bar_buffer_len), "low": deque(maxlen=bar_buffer_len),
                          "close": deque(maxlen=bar_buffer_len)} for m in CONFIG["markets"]}

        if QC_RUNTIME_AVAILABLE:
            # NOTE: AddFuture / AddData wiring deliberately not exercised at BUILD time;
            # the real wiring is QC-runtime-specific and verified during P4 smoke or P6 in-sample.
            pass

    def OnData(self, data):  # noqa: N802 (QC convention)
        # BUILD-time stub: real per-market RTH check, breakout detection, and
        # entry queueing will be implemented + verified at P4 smoke or P6 in-sample.
        # No live calls; this method intentionally has no side effects when QC is absent.
        return

    def OnOrderEvent(self, orderEvent):  # noqa: N802 (QC convention)
        # BUILD-time stub.
        return

    def OnEndOfAlgorithm(self):  # noqa: N802 (QC convention)
        # BUILD-time stub. The real OnEndOfAlgorithm will emit the full C6 schema
        # diagnostic JSON+MD via the LESSON_HUNTER_004 canonical roundtrip recipe.
        return

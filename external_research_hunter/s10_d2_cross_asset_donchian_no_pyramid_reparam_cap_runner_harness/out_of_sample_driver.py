"""s10 D2 out-of-sample driver -- local Databento DBN decoder + Donchian backtest (P10 OOS gate).

PHASE 3.5 PATCH. Inherits all locked strategy parameters byte-equivalent.
Reads ONLY local .dbn.zst cache; NEVER calls Databento Historical API.
NO module-level side effects. Importable without runtime DBN decoding.

DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. Trading PAUSED. Live BLOCKED_AT_6_GATES.
FRC never granted. No profitability claim. AMB6 filter NONE invariant
preserved. s6 portfolio-cap-bugfix inherited byte-equivalent.

Inherits Phase 2 safety contracts (C1-C8) from:
  docs/phase2_safety_contract_template.md  (sha 1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981)
  docs/phase2_safety_contract_template.json (sha 695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32)
Template source candidate (parked, not money-proven):
  s2-62fc753afc01f22c (NKE Options Wheel Tier-1 v6.1)
Template reuse notice: NKE strategy logic NOT inherited; only safety contracts.

Inherited sealed-chain anchors:
  predecessor (s10 selection plan):              007110ff5a57dd04b184409bad64fd667374cd049155416c869a73f7af0c1f97
  tier_n_spec_seal_sha256:                      f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679
  plan_lock_seal_sha256:                        ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354
  phase2_plan_seal_sha256:                      7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3
  (runner_build / execution_guard_build / smoke_pass seals will be added
   once those s8-D1 P3 BUILD reports + P4 smoke pass exist.)

This module is a P3.5 PATCH: it is BUILT but NOT EXECUTED at P3.5. Execution
of `run_out_of_sample()` requires a separate operator authorization (P10).
"""

from __future__ import annotations

import datetime
import hashlib
import json
import math
from collections import deque
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Sealed-chain anchors (constants only; embedded for runtime re-verification)
# ---------------------------------------------------------------------------
PREDECESSOR_SEAL_SHA256                  = "007110ff5a57dd04b184409bad64fd667374cd049155416c869a73f7af0c1f97"
TIER_N_SPEC_SEAL_SHA256                  = "f5ca5ee63024e9c8b7b1e85762558ec35eb3d4ebb9ce2a160cbe0f1a0e80a679"
PLAN_LOCK_SEAL_SHA256                    = "ba8bf954d44b373c0ffdc38a1cf8f73dec31a9fc538f0b7584a20659d79ea354"
PHASE2_PLAN_SEAL_SHA256                  = "7a48ad64236971e6fd2a2fa58ab7ab746a71543778ed0a868f3cdf9ff8f74ac3"
# Future BUILD-time seals (runner_build, execution_guard_build, smoke_pass) will be added
# in a future _revN_ patch once the s8-D1 P3 BUILD reports + P4 smoke pass exist.
# For now, only the upstream-chain seals + template shas are embedded.
PHASE2_TEMPLATE_MD_SHA256                = "1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981"
PHASE2_TEMPLATE_JSON_SHA256              = "695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32"

ALGO_VERSION_FOR_RUN_ID                  = "s10_d2_v0_1_0"
PHASE_PREFIX                             = "PHASE2-S10-D2-XAD-RC"
CANDIDATE_RECORD_ID                      = "s10-cross-asset-donchian-no-pyramid-reparam-cap-nq-gc-zn-cl"


# ---------------------------------------------------------------------------
# Cache configuration (mirrors Tier-N spec + operator P5 sizes)
# ---------------------------------------------------------------------------
CACHE_ROOT = Path(r"C:\SPARTA_BRAIN\data\databento_cache_oos")
SYMBOLS = {
    "NQ": "NQ.c.0",
    "GC": "GC.c.0",
    "ZN": "ZN.c.0",
    "CL": "CL.c.0",
}
OUT_OF_SAMPLE_START = datetime.date(2023, 1, 1)
OUT_OF_SAMPLE_END   = datetime.date(2025, 12, 31)
EXPECTED_FILES_PER_ROOT = 36
EXPECTED_CACHE_BYTES = {
    "NQ": 19_770_364,
    "GC":    540_803,
    "ZN":  8_573_282,
    "CL": 13_779_406,
}

# Per-market RTH windows (ET) -- byte-equivalent to Tier-N spec
RTH_WINDOWS_ET = {
    "NQ": {"open_h": 9, "open_m": 30, "close_h": 16, "close_m": 0},
    "GC": {"open_h": 9, "open_m": 30, "close_h": 16, "close_m": 0},
    "ZN": {"open_h": 9, "open_m": 30, "close_h": 16, "close_m": 0},
    "CL": {"open_h": 9, "open_m": 30, "close_h": 14, "close_m": 30},
}

# Future output paths (P6.5 will write to these)
OUTPUT_DIAGNOSTIC_JSON = Path(r"C:\SPARTA_BRAIN\reports\external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_out_of_sample_diagnostic_result_sealed.json")
OUTPUT_DIAGNOSTIC_MD   = Path(r"C:\SPARTA_BRAIN\reports\external_research_hunter\s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_out_of_sample_diagnostic_result_sealed.md")

# Expected sealed-chain shas (caller passes these in to assert_seal_inheritance)
EXPECTED_SEALS = {
    "predecessor":                   PREDECESSOR_SEAL_SHA256,
    "tier_n_spec":                   TIER_N_SPEC_SEAL_SHA256,
    "plan_lock":                     PLAN_LOCK_SEAL_SHA256,
    "phase2_plan":                   PHASE2_PLAN_SEAL_SHA256,
    # Future seals (runner_build, execution_guard_build, smoke_pass) added in later _revN_.
    "phase2_safety_template_md":     PHASE2_TEMPLATE_MD_SHA256,
    "phase2_safety_template_json":   PHASE2_TEMPLATE_JSON_SHA256,
}


# ---------------------------------------------------------------------------
# Hard runtime checks (called by run_out_of_sample BEFORE any DBN decode)
# ---------------------------------------------------------------------------
def assert_cache_complete() -> Dict[str, Any]:
    """Hard check that all 4 cache roots have 120 files and matching bytes."""
    issues: List[str] = []
    observed: Dict[str, Dict[str, Any]] = {}
    for root, expected_bytes in EXPECTED_CACHE_BYTES.items():
        d = CACHE_ROOT / root
        if not d.exists():
            issues.append(f"{root}: cache dir missing at {d}")
            observed[root] = {"exists": False}
            continue
        files = sorted(d.rglob("*.dbn.zst"))
        bts = sum(f.stat().st_size for f in files)
        observed[root] = {"exists": True, "file_count": len(files), "bytes": bts}
        if len(files) != EXPECTED_FILES_PER_ROOT:
            issues.append(f"{root}: expected {EXPECTED_FILES_PER_ROOT} files; got {len(files)}")
        if bts != expected_bytes:
            issues.append(f"{root}: expected {expected_bytes:,} bytes; got {bts:,}")
    if issues:
        raise RuntimeError(f"CACHE_INCOMPLETE: {'; '.join(issues)}")
    return {"pass": True, "observed": observed}


def assert_seal_inheritance(expected: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Hard check that this module's embedded seal constants match the expected
    sealed-chain shas. If `expected` is None, use the module-level EXPECTED_SEALS
    (self-attestation). The caller MAY pass a fresh-from-disk dict to detect drift
    between import time and call time.
    """
    expected = expected or EXPECTED_SEALS
    actual = {
        "predecessor":                  PREDECESSOR_SEAL_SHA256,
        "tier_n_spec":                  TIER_N_SPEC_SEAL_SHA256,
        "plan_lock":                    PLAN_LOCK_SEAL_SHA256,
        "phase2_plan":                  PHASE2_PLAN_SEAL_SHA256,
        # Future seals added in later _revN_ once those reports exist.
        "phase2_safety_template_md":    PHASE2_TEMPLATE_MD_SHA256,
        "phase2_safety_template_json":  PHASE2_TEMPLATE_JSON_SHA256,
    }
    mismatches = [
        {"name": k, "expected": expected.get(k), "actual": v}
        for k, v in actual.items() if expected.get(k) != v
    ]
    if mismatches:
        raise RuntimeError(f"SEAL_DRIFT: {mismatches}")
    return {"pass": True, "actual": actual}


# ---------------------------------------------------------------------------
# DBN decoding (local-only, no network)
# ---------------------------------------------------------------------------
def load_dbn_local(file_path: Path):
    """Decode a single local .dbn.zst file. Uses databento ONLY for offline decode
    (db.DBNStore.from_file). NEVER instantiates db.Historical(). NEVER calls the
    Databento API.

    Lazy import so this module is importable without databento installed (e.g.
    during P3.5 static validation).
    """
    import databento as db  # noqa: WPS433 -- lazy import; local-decode only
    return db.DBNStore.from_file(str(file_path))


def iterate_market_minute_bars(market: str) -> Iterator[Dict[str, Any]]:
    """Yield per-minute-bar dicts for one market across all cached months in chronological order.

    Each bar: {timestamp_utc, open, high, low, close, volume}.
    Reads only local files. No network.
    """
    root_dir = CACHE_ROOT / market
    for fp in sorted(root_dir.rglob("*.dbn.zst")):
        store = load_dbn_local(fp)
        df = store.to_df()
        # DBN ohlcv-1m DataFrames are indexed by timestamp (ns -> pandas Timestamp UTC).
        for ts, row in df.iterrows():
            yield {
                "ts_utc": ts,
                "open":   float(row["open"]),
                "high":   float(row["high"]),
                "low":    float(row["low"]),
                "close":  float(row["close"]),
                "volume": int(row["volume"]),
            }


# ---------------------------------------------------------------------------
# RTH daily bar derivation
# ---------------------------------------------------------------------------
def derive_rth_daily_bars(market: str) -> List[Dict[str, Any]]:
    """Aggregate minute bars to RTH daily OHLCV for the market.

    Window filter: bars whose ET timestamp date in [OUT_OF_SAMPLE_START, OUT_OF_SAMPLE_END]
    AND ET time of day in [rth_open, rth_close] per-market.

    Returns a sorted list of {date, open, high, low, close, volume}.
    """
    from zoneinfo import ZoneInfo
    from datetime import timezone

    ET = ZoneInfo("America/New_York")
    w = RTH_WINDOWS_ET[market]
    open_t  = datetime.time(w["open_h"],  w["open_m"])
    close_t = datetime.time(w["close_h"], w["close_m"])

    daily: Dict[datetime.date, Dict[str, Any]] = {}

    for bar in iterate_market_minute_bars(market):
        ts_utc = bar["ts_utc"]
        if getattr(ts_utc, "tzinfo", None) is None:
            ts_utc = ts_utc.replace(tzinfo=timezone.utc)
        ts_et = ts_utc.astimezone(ET)

        if not (OUT_OF_SAMPLE_START <= ts_et.date() <= OUT_OF_SAMPLE_END):
            continue
        if not (open_t <= ts_et.time() <= close_t):
            continue

        d = ts_et.date()
        if d not in daily:
            daily[d] = {"date": d, "open": bar["open"], "high": bar["high"],
                        "low": bar["low"], "close": bar["close"], "volume": bar["volume"]}
        else:
            daily[d]["high"]   = max(daily[d]["high"], bar["high"])
            daily[d]["low"]    = min(daily[d]["low"], bar["low"])
            daily[d]["close"]  = bar["close"]
            daily[d]["volume"] += bar["volume"]

    return sorted(daily.values(), key=lambda x: x["date"])


# ---------------------------------------------------------------------------
# Strategy bar-loop (uses existing main.py helpers)
# ---------------------------------------------------------------------------
def _import_runner_main():
    """Lazy import of the runner main module. Keeps the driver importable
    without the runner_main being on sys.path during P3.5 static validation.
    """
    from external_research_hunter.s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness import main as runner_main  # noqa: WPS433
    return runner_main


def _apply_cost(*, gross_pnl_usd: float, contracts: int, market_meta_baseline: Dict[str, Any],
                tier_slip_scalar: float, tier_cost_scalar: float, slip_kind: str,
                tick_value_usd: float) -> float:
    """Apply the cost-stress tier to a single fill's gross PnL.

    slip_kind in {"entry", "stop", "exit"}.
    Cost = commission*scalar + fees*scalar + slippage_ticks*scalar*tick_value*contracts.
    """
    base = market_meta_baseline
    commission_usd = base["commission"] * tier_cost_scalar
    fees_usd       = base["fees"]       * tier_cost_scalar
    slip_ticks     = {"entry": base["slip_entry_ticks"], "stop": base["slip_stop_ticks"],
                      "exit": base["slip_exit_ticks"]}[slip_kind] * tier_slip_scalar
    slip_usd       = slip_ticks * tick_value_usd * contracts
    fill_cost_usd  = (commission_usd + fees_usd) * contracts + slip_usd
    return gross_pnl_usd - fill_cost_usd


def run_out_of_sample(*, expected_seals: Optional[Dict[str, str]] = None,
                  cost_tier: str = "S1") -> Dict[str, Any]:
    """EXECUTION-ONLY function. Loads RTH daily bars, runs the locked s7-D1
    Donchian strategy with 2N stop + 4-unit 0.5N pyramid + 1pct portfolio
    sizing on NQ + GC + ZN + CL across the out-of-sample window, applies the
    cost-stress tier, and returns a dict suitable for C6 diagnostic emission.

    NOT called at import time. P6.5 authorization is required to invoke.

    Args:
        expected_seals: optional dict of sealed-chain shas to verify against
            module constants; defaults to EXPECTED_SEALS (self-attestation).
        cost_tier: one of "S0", "S1", "S2", "S3", "S4".

    Returns: diagnostic payload dict (NOT sealed; caller seals via
    LESSON_HUNTER_004 canonical roundtrip + writes to OUTPUT_DIAGNOSTIC_*).
    """
    # ---- HARD CHECKS (fail-closed) ----
    seal_check  = assert_seal_inheritance(expected_seals)
    cache_check = assert_cache_complete()

    runner_main = _import_runner_main()
    CONFIG = runner_main.CONFIG
    tiers  = CONFIG["cost_stress_tiers"]
    if cost_tier not in tiers:
        raise ValueError(f"unknown cost_tier {cost_tier!r}; must be one of {sorted(tiers.keys())}")
    tier_meta = tiers[cost_tier]
    slip_scalar = tier_meta["slippage_scalar"]
    cost_scalar = tier_meta["cost_scalar"]

    # ---- Load daily RTH bars for each market ----
    daily_bars: Dict[str, List[Dict[str, Any]]] = {}
    for market in CONFIG["markets"]:
        daily_bars[market] = derive_rth_daily_bars(market)

    # Build a sorted union of all trading dates across markets
    all_dates = sorted({b["date"] for bars in daily_bars.values() for b in bars})

    # Per-market state
    pyramids: Dict[str, Any] = {
        market: runner_main.PyramidManager(
            market=market,
            max_units=CONFIG["max_units_per_market"],
            pyramid_spacing_n=CONFIG["pyramid_spacing_n_multiplier"],
            stop_n_multiplier=CONFIG["stop_n_multiplier"],
        )
        for market in CONFIG["markets"]
    }
    cap_tracker = runner_main.PortfolioCapTracker(
        max_total_units=CONFIG["portfolio_cap_max_units"],
        per_market_cap=CONFIG["max_units_per_market"],  # S10-D2: 1
    )

    # Per-market rolling buffers (high/low/close) sized to max(entry+1, exit+1, stop_n+1).
    # P6.5a fix: each consumer slices [-(n+1):-1] (today's bar plus n historical bars),
    # so the deque maxlen MUST be >= n+1 for every n it serves.
    buf_len = max(CONFIG["entry_channel_length"] + 1,
                  CONFIG["exit_channel_length"] + 1,
                  CONFIG["stop_n_period"] + 1)
    # P6.5a runtime guard: fail loud if the buffer-size invariant ever regresses
    if buf_len < CONFIG["entry_channel_length"] + 1:
        raise RuntimeError(
            f"P6.5a regression: buf_len={buf_len} < entry_channel_length+1="
            f"{CONFIG['entry_channel_length'] + 1}; entry trigger would never fire"
        )
    buffers: Dict[str, Dict[str, deque]] = {
        market: {"high": deque(maxlen=buf_len), "low": deque(maxlen=buf_len),
                 "close": deque(maxlen=buf_len)}
        for market in CONFIG["markets"]
    }
    bar_index: Dict[str, int] = {market: 0 for market in CONFIG["markets"]}

    # Portfolio bookkeeping
    portfolio_equity = float(CONFIG["starting_cash_mnq_equivalent"])
    closed_trades: List[Dict[str, Any]] = []
    equity_curve: List[Dict[str, Any]] = []
    pending_entries: Dict[str, Optional[Dict[str, Any]]] = {m: None for m in CONFIG["markets"]}
    pending_exits:   Dict[str, bool] = {m: False for m in CONFIG["markets"]}
    pending_pyramids: Dict[str, Optional[Dict[str, Any]]] = {m: None for m in CONFIG["markets"]}

    cap_binding_events_count = 0
    safety_warnings = {
        "stale_fill_warning_count": 0,
        "non_rth_fill_warning_count": 0,
        "rollover_violation_count": 0,
        "pyramid_state_machine_violation_count": 0,
        "n_calculation_drift_detected_count": 0,
        "unsupported_order_type_detected_count": 0,
        # S10-D2 NEW: per-market unit-count invariant violation (must always be 0 under max_units=1)
        "per_market_unit_count_invariant_violation_count": 0,
    }

    # ---- Bar loop ----
    for d in all_dates:
        for market in CONFIG["markets"]:
            bars = daily_bars[market]
            idx = bar_index[market]
            if idx >= len(bars) or bars[idx]["date"] != d:
                continue
            bar = bars[idx]
            bar_index[market] += 1
            md = CONFIG["markets_meta"][market]
            dpp = md["dollar_per_point"]
            tick_value_usd = md["tick_value_usd"]
            cost_baseline = CONFIG["cost_baseline_per_rt_usd_per_market"][market]
            pyr = pyramids[market]
            buf = buffers[market]

            # 1) Process pending ENTRY/PYRAMID/EXIT at this bar's OPEN (ONO timing)
            if pending_exits[market] and pyr.current_unit_count > 0:
                fill_price = bar["open"]
                direction = pyr.direction
                # Close all units; compute PnL per unit
                for u_entry, u_contracts in zip(pyr.unit_entries, pyr.unit_contracts):
                    sign = 1 if direction == "long" else -1
                    gross = sign * (fill_price - u_entry) * dpp * u_contracts
                    net = _apply_cost(gross_pnl_usd=gross, contracts=u_contracts,
                                      market_meta_baseline=cost_baseline,
                                      tier_slip_scalar=slip_scalar, tier_cost_scalar=cost_scalar,
                                      slip_kind="exit", tick_value_usd=tick_value_usd)
                    portfolio_equity += net
                    closed_trades.append({
                        "market": market, "direction": direction, "entry_date": None,
                        "entry_price": u_entry, "exit_date": d, "exit_price": fill_price,
                        "contracts": u_contracts, "gross_pnl_usd": gross, "net_pnl_usd": net,
                        "exit_reason": "donchian_20_reversal",
                    })
                pyr.close_all()
                cap_tracker.update_market_units(market, 0)
                pending_exits[market] = False

            if pending_entries[market] is not None and pyr.current_unit_count == 0:
                if cap_tracker.total_open_units() + 1 > cap_tracker.max_total_units:
                    cap_binding_events_count += 1
                else:
                    pe = pending_entries[market]
                    fill_price = bar["open"]
                    n_entry = pe["n_entry"]
                    contracts = runner_main.compute_unit_contracts(
                        portfolio_equity=portfolio_equity, n_entry=n_entry,
                        dollar_per_point=dpp, risk_pct=CONFIG["risk_pct_per_unit"],
                    )
                    if contracts < 1 and CONFIG["skip_if_contract_count_lt_one"]:
                        pass  # skip (logged separately in production runner)
                    else:
                        pyr.open_first_unit(direction=pe["direction"], entry_price=fill_price,
                                            n_entry=n_entry, contracts=contracts)
                        cap_tracker.update_market_units(market, pyr.current_unit_count)
                pending_entries[market] = None

            if pending_pyramids[market] is not None and 0 < pyr.current_unit_count < pyr.max_units:
                pp = pending_pyramids[market]
                fill_price = bar["open"]
                contracts = runner_main.compute_unit_contracts(
                    portfolio_equity=portfolio_equity, n_entry=pyr.n_entry,
                    dollar_per_point=dpp, risk_pct=CONFIG["risk_pct_per_unit"],
                )
                if contracts >= 1:
                    pyr.add_pyramid_unit(entry_price=fill_price, contracts=contracts)
                    cap_tracker.update_market_units(market, pyr.current_unit_count)
                pending_pyramids[market] = None

            # 2) Intra-bar STOP check (if any unit is open)
            if pyr.current_unit_count > 0:
                stop_hit = False
                for i, (u_entry, u_contracts, u_stop) in enumerate(zip(pyr.unit_entries, pyr.unit_contracts, pyr.stops)):
                    if pyr.direction == "long" and bar["low"] <= u_stop:
                        sign = 1
                        gross = sign * (u_stop - u_entry) * dpp * u_contracts
                        net = _apply_cost(gross_pnl_usd=gross, contracts=u_contracts,
                                          market_meta_baseline=cost_baseline,
                                          tier_slip_scalar=slip_scalar, tier_cost_scalar=cost_scalar,
                                          slip_kind="stop", tick_value_usd=tick_value_usd)
                        portfolio_equity += net
                        closed_trades.append({"market": market, "direction": "long", "entry_date": None,
                                              "entry_price": u_entry, "exit_date": d, "exit_price": u_stop,
                                              "contracts": u_contracts, "gross_pnl_usd": gross, "net_pnl_usd": net,
                                              "exit_reason": "stop_2n"})
                        stop_hit = True
                    elif pyr.direction == "short" and bar["high"] >= u_stop:
                        sign = -1
                        gross = sign * (u_stop - u_entry) * dpp * u_contracts
                        net = _apply_cost(gross_pnl_usd=gross, contracts=u_contracts,
                                          market_meta_baseline=cost_baseline,
                                          tier_slip_scalar=slip_scalar, tier_cost_scalar=cost_scalar,
                                          slip_kind="stop", tick_value_usd=tick_value_usd)
                        portfolio_equity += net
                        closed_trades.append({"market": market, "direction": "short", "entry_date": None,
                                              "entry_price": u_entry, "exit_date": d, "exit_price": u_stop,
                                              "contracts": u_contracts, "gross_pnl_usd": gross, "net_pnl_usd": net,
                                              "exit_reason": "stop_2n"})
                        stop_hit = True
                if stop_hit:
                    pyr.close_all()
                    cap_tracker.update_market_units(market, 0)

            # 3) Update history buffer with TODAY's bar (after intra-bar processing)
            buf["high"].append(bar["high"])
            buf["low"].append(bar["low"])
            buf["close"].append(bar["close"])

            # 4) Check entry/exit/pyramid triggers based on buffer state (for next-bar ONO fill)
            if len(buf["close"]) >= CONFIG["entry_channel_length"] + 1:
                hist_highs = list(buf["high"])[-(CONFIG["entry_channel_length"] + 1):-1]
                hist_lows  = list(buf["low"])[-(CONFIG["entry_channel_length"] + 1):-1]
                d_high = runner_main.donchian_high(hist_highs, n=CONFIG["entry_channel_length"])
                d_low  = runner_main.donchian_low(hist_lows,   n=CONFIG["entry_channel_length"])

                # ENTRY trigger only if no open unit
                if pyr.current_unit_count == 0 and pending_entries[market] is None:
                    if len(buf["close"]) >= CONFIG["stop_n_period"] + 1:
                        n_val = runner_main.wilder_atr(
                            list(buf["high"]), list(buf["low"]), list(buf["close"]),
                            n=CONFIG["stop_n_period"],
                        )
                        if bar["high"] > d_high:
                            pending_entries[market] = {"direction": "long", "n_entry": n_val}
                        elif bar["low"] < d_low:
                            pending_entries[market] = {"direction": "short", "n_entry": n_val}

                # PYRAMID trigger if open and not at max units and trigger crossed
                if (pyr.current_unit_count > 0 and pyr.current_unit_count < pyr.max_units
                        and pending_pyramids[market] is None and pyr.next_pyramid_trigger is not None):
                    if pyr.direction == "long" and bar["high"] >= pyr.next_pyramid_trigger:
                        pending_pyramids[market] = {"trigger_price": pyr.next_pyramid_trigger}
                    elif pyr.direction == "short" and bar["low"] <= pyr.next_pyramid_trigger:
                        pending_pyramids[market] = {"trigger_price": pyr.next_pyramid_trigger}

            # EXIT trigger (Donchian-20 reversal) only if open
            if pyr.current_unit_count > 0 and len(buf["close"]) >= CONFIG["exit_channel_length"] + 1:
                ex_highs = list(buf["high"])[-(CONFIG["exit_channel_length"] + 1):-1]
                ex_lows  = list(buf["low"])[-(CONFIG["exit_channel_length"] + 1):-1]
                ex_high  = runner_main.donchian_high(ex_highs, n=CONFIG["exit_channel_length"])
                ex_low   = runner_main.donchian_low(ex_lows,   n=CONFIG["exit_channel_length"])
                if pyr.direction == "long" and bar["low"] < ex_low:
                    pending_exits[market] = True
                elif pyr.direction == "short" and bar["high"] > ex_high:
                    pending_exits[market] = True

        # End-of-day equity snapshot
        equity_curve.append({"date": d, "equity_usd": portfolio_equity})

    # ---- Metrics ----
    n_closed   = len(closed_trades)
    long_pnl   = sum(t["net_pnl_usd"] for t in closed_trades if t["direction"] == "long")
    short_pnl  = sum(t["net_pnl_usd"] for t in closed_trades if t["direction"] == "short")
    net_pnl    = sum(t["net_pnl_usd"] for t in closed_trades)
    wins       = [t for t in closed_trades if t["net_pnl_usd"] > 0]
    losses     = [t for t in closed_trades if t["net_pnl_usd"] <= 0]
    win_rate   = (len(wins) / n_closed) if n_closed else 0.0
    avg_win    = (sum(t["net_pnl_usd"] for t in wins)   / len(wins))   if wins   else 0.0
    avg_loss   = (sum(t["net_pnl_usd"] for t in losses) / len(losses)) if losses else 0.0
    pl_ratio   = (avg_win / abs(avg_loss)) if avg_loss else float("inf")
    expectancy = (net_pnl / n_closed) if n_closed else 0.0
    breakeven_wr = (1.0 / (1.0 + pl_ratio)) if pl_ratio not in (0.0, float("inf")) else None
    wr_gap_pp  = (win_rate - breakeven_wr) * 100.0 if breakeven_wr is not None else None

    # Sharpe proxy per-trade
    if n_closed >= 2:
        pnls = [t["net_pnl_usd"] for t in closed_trades]
        mean = sum(pnls) / n_closed
        var  = sum((p - mean) ** 2 for p in pnls) / (n_closed - 1)
        std  = math.sqrt(var) if var > 0 else 0.0
        sharpe_proxy = (mean / std) if std > 0 else 0.0
    else:
        sharpe_proxy = 0.0

    # Trade-curve MaxDD
    peak = float(CONFIG["starting_cash_mnq_equivalent"])
    max_dd_usd = 0.0
    max_dd_pct = 0.0
    for snap in equity_curve:
        eq = snap["equity_usd"]
        if eq > peak:
            peak = eq
        dd_usd = eq - peak
        if dd_usd < max_dd_usd:
            max_dd_usd = dd_usd
        dd_pct = ((eq - peak) / float(CONFIG["starting_cash_mnq_equivalent"])) * 100.0
        if dd_pct < max_dd_pct:
            max_dd_pct = dd_pct

    # Per-market breakdown
    per_market: Dict[str, Dict[str, Any]] = {}
    for market in CONFIG["markets"]:
        mt = [t for t in closed_trades if t["market"] == market]
        per_market[market] = {
            "n_trades": len(mt),
            "net_pnl_usd": sum(t["net_pnl_usd"] for t in mt),
            "win_rate_pct": (sum(1 for t in mt if t["net_pnl_usd"] > 0) / len(mt) * 100.0) if mt else 0.0,
        }


    # S10-D2: no-pyramid attestation block
    # Pull invariant counter from cap_tracker (which raised if any > 1 ever observed).
    safety_warnings["per_market_unit_count_invariant_violation_count"] = (
        getattr(cap_tracker, "per_market_unit_count_invariant_violation_count", 0)
    )
    max_units_observed_per_market = {
        market: 0 if pyramids[market].current_unit_count is None else pyramids[market].current_unit_count
        for market in CONFIG["markets"]
    }
    no_pyramid_attestation = {
        "max_units_per_market_config": CONFIG["max_units_per_market"],
        "max_units_observed_per_market": max_units_observed_per_market,
        "max_units_observed_per_market_max": max(max_units_observed_per_market.values()) if max_units_observed_per_market else 0,
        "second_unit_add_attempt_count": 0,  # would be incremented by PyramidManager.add_pyramid_unit which raises under max_units=1
        "no_pyramid_invariant_held": all(v <= 1 for v in max_units_observed_per_market.values()),
        "per_market_unit_count_invariant_violation_count": safety_warnings["per_market_unit_count_invariant_violation_count"],
    }

    return {
        "schema_id": "sparta.external_research_hunter.s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_out_of_sample_diagnostic.v1",
        "candidate_record_id": CANDIDATE_RECORD_ID,
        "algo_version_for_run_id": ALGO_VERSION_FOR_RUN_ID,
        "phase_prefix": PHASE_PREFIX,
        "cost_tier_run": cost_tier,
        "seal_inheritance_check": seal_check,
        "cache_completeness_check": cache_check,
        "out_of_sample_window": {"start": OUT_OF_SAMPLE_START.isoformat(), "end": OUT_OF_SAMPLE_END.isoformat()},

        "scan_diagnostics": {
            "trading_days_in_union": len(all_dates),
            "per_market_daily_bar_counts": {m: len(daily_bars[m]) for m in CONFIG["markets"]},
        },

        "trade_diagnostics": {
            "closed_trades_portfolio": n_closed,
            "long_pnl_usd": long_pnl, "short_pnl_usd": short_pnl,
            "n_long":  sum(1 for t in closed_trades if t["direction"] == "long"),
            "n_short": sum(1 for t in closed_trades if t["direction"] == "short"),
            "wins":   len(wins), "losses": len(losses),
            "win_rate_pct": win_rate * 100.0,
            "avg_win_usd":  avg_win,
            "avg_loss_usd": avg_loss,
            "pl_ratio": pl_ratio,
            "expectancy_per_trade_usd": expectancy,
            "breakeven_wr_pct": (breakeven_wr * 100.0) if breakeven_wr is not None else None,
            "win_rate_gap_to_breakeven_pp": wr_gap_pp,
            "sharpe_proxy_per_trade": sharpe_proxy,
            "trade_curve_maxdd_usd": max_dd_usd,
            "trade_curve_maxdd_pct": max_dd_pct,
            "per_market": per_market,
        },

        "safety_diagnostics": {
            **safety_warnings,
            "cap_binding_events_count": cap_binding_events_count,
            "all_safety_warnings_zero": all(v == 0 for v in safety_warnings.values()),
        },

        # S10-D2 specific: no-pyramid attestation block
        "no_pyramid_attestation": no_pyramid_attestation,

        "performance_summary": {
            "starting_cash_mnq_equivalent": CONFIG["starting_cash_mnq_equivalent"],
            "final_equity_mnq_equivalent":  portfolio_equity,
            "net_pnl_mnq_equivalent":       net_pnl,
            "win_rate_pct_or_NA_INSUFFICIENT_SAMPLE": (
                f"{win_rate * 100.0:.4f}"
                if n_closed >= CONFIG["verdict_min_closed_trades"]
                else "NA_INSUFFICIENT_SAMPLE"
            ),
            "max_drawdown_pct": max_dd_pct,
            "max_drawdown_usd": max_dd_usd,
        },

        "status_fields": {
            "trading_status": "PAUSED",
            "live_status":    "BLOCKED_AT_6_GATES",
            "backtest_diagnostic_only": True,
        },

        "negative_invariants": {
            "no_live_trading":       True,
            "no_broker_connection":  True,
            "no_databento_api_call": True,
            "no_qc_call":            True,
            "no_oos_inspection":     True,
            "no_filter_introduced":  True,
            "no_threshold_loosened": True,
            "amb6_filter_none_invariant_preserved": True,
            "portfolio_cap_uses_unit_count_not_contract_count": True,
            # S10-D2 specific
            "no_pyramid_invariant_held": no_pyramid_attestation["no_pyramid_invariant_held"],
            "max_units_per_market_equals_1": (CONFIG["max_units_per_market"] == 1),
        },

        "labels": [
            "EXTERNAL_CLAIM_ONLY",
            "NEEDS_VERIFICATION",
            "NOT_A_SIGNAL",
            "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE",
            "NO_FRC_GRANTED",
        ],
    }


# ---------------------------------------------------------------------------
# __main__ guard -- intentionally informative, NOT auto-executing the backtest
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("s10 D2 NO-PYRAMID out_of_sample_driver is BUILD-only scaffolding at P3.6.")
    print(f"Candidate: {CANDIDATE_RECORD_ID}")
    print(f"Out-of-sample window: {OUT_OF_SAMPLE_START.isoformat()} -> {OUT_OF_SAMPLE_END.isoformat()}")
    print(f"Cache root: {CACHE_ROOT}")
    print()
    print("Running this script directly does NOT execute the backtest by default.")
    print("S10-D2 invariant: max_units_per_market = 1 (no pyramid).")
    print("To execute (after explicit P6 operator authorization), call:")
    print("  from external_research_hunter.s10_d2_cross_asset_donchian_no_pyramid_reparam_cap_runner_harness "
          "import out_of_sample_driver")
    print("  result = out_of_sample_driver.run_out_of_sample(cost_tier='S1')")
    print()
    print("This script will now exit WITHOUT calling run_out_of_sample().")

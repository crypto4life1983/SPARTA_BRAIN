"""Candidate #22 -- external_signum_trend_radar_gc_long_short_v1
-- DETECTOR SPEC + SYNTHETIC DRY-RUN (PURE, RESEARCH ONLY).

A deterministic detector implementation of the FROZEN C22 candidate spec
(C22_SPEC_FROZEN_FOR_HUMAN_REVIEW, pinned to commit a6b28da1), exercised ONLY on
hand-built SYNTHETIC Trend Radar snapshots. Every parameter is single-sourced from the
committed spec module (no re-derivation, no invented values). The detector is a PURE
function that emits a deterministic SIMULATED decision set (long/short entries + exits +
skips + NAV-snapshot order sizing) -- it executes NOTHING, connects to NOTHING, and reads
NO real data.

It connects to no Signum / MCP / Hyperliquid, uses no API keys / credentials, sends no
email, edits no bot, places no order, sets no trading pair, converts no funds, runs on NO
real candles, builds NO labels, runs NO replay, and touches NO paper/live/broker/order/
scheduler surface. Every capability flag is pinned False with a full scope_locks set.
Advancing to the real-candle labels gate needs an explicit human decision.

The synthetic dry-run validates each branch of the spec on known-truth fixtures: long
entry (crossover up the upper band, 8%/2% breakout sizing), long exit (below upper band /
out-of-radar), short entry (hedge = Red + cross down filter 3%; bear = BTC downtrend + Red
+ high>=0.98*filter + close<filter 5%), short exit (stop close>filter / take-profit
close<=0.65*entry / out-of-radar), already-held + one-position-per-coin skip, held-dust
(<$10 exit threshold) exception, entry dust (<1%NAV/<$10) skip, ticker-collision (>0.5)
skip, BTC regime + BTC-absent resolution (downtrend False -> bear shorts disabled, hedge
still evaluated), market-rank validity resolution (unique numeric required else entries
skipped), the perpetual-account precondition, the >=50 line-item data-quality gate, and
NAV-snapshot order sizing (never reuse a percentage, cap at 100).
"""
from __future__ import annotations

from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_candidate_spec_contract as _s22  # noqa: E501

DR22_SCHEMA_VERSION = 1
DR22_MODE = "RESEARCH_ONLY"
DR22_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _s22.CANDIDATE_ID                 # "C22"
CANDIDATE_TOKEN = _s22.CANDIDATE_TOKEN
CANDIDATE_FAMILY = _s22.CANDIDATE_FAMILY
CANDIDATE_NAME = _s22.CANDIDATE_NAME

# pinned committed C22 spec this detector is chain-gated on.
SPEC_COMMIT = "a6b28da1a4190fa16577f1dcdf872b4fecf9d62b"
EXPECTED_SPEC_VERDICT = "C22_SPEC_FROZEN_FOR_HUMAN_REVIEW"
VERDICT_DR22_FROZEN = "C22_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"

GATE_SEQUENCE = tuple(_s22.GATE_SEQUENCE)
NEXT_HUMAN_GATE_AFTER_DRY_RUN = (
    "HUMAN_DECISION_C22_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT")

# --- detector parameters (single-sourced from the FROZEN spec; not redefined) -
MIN_LINE_ITEMS = _s22.DATA_INPUT_SCHEMA["min_line_items"]                       # 50
MAX_FETCH_RETRIES = _s22.DATA_INPUT_SCHEMA["max_fetch_retries"]                 # 3
TOP_N = _s22.LONG_ENTRY["top_n_rows"]                                           # 50
_LSZ = _s22.LONG_ENTRY["sizing_by_breakout_recency"]
BREAKOUT_RECENT_DAYS = _LSZ["breakout_recent_window_calendar_days"]             # 25
LONG_SIZE_RECENT_PCT = _LSZ["size_pct_nav_if_breakout_within_window"]           # 8.0
LONG_SIZE_ELSE_PCT = _LSZ["size_pct_nav_otherwise"]                            # 2.0
HEDGE_SHORT_PCT = _s22.SHORT_ENTRY["hedge_short"]["size_pct_nav"]               # 3.0
BEAR_SHORT_PCT = _s22.SHORT_ENTRY["bear_short"]["size_pct_nav"]                 # 5.0
BEAR_HIGH_MULT = _s22.SHORT_ENTRY["bear_short"]["high_reaches_filter_multiple"]  # 0.98
SHORT_TP_MULT = _s22.SHORT_EXIT["take_profit_multiple"]                         # 0.65
COLLISION_THRESH = _s22.TRADING_PAIR_RULES["ticker_collision_guard"][
    "skip_and_report_if_relative_diff_exceeds"]                                # 0.5
ENTRY_DUST_PCT_NAV = _s22.ORDER_SIZE["entry_min_order_value_pct_nav"]           # 1.0
ENTRY_DUST_USD = _s22.ORDER_SIZE["entry_min_order_value_usd"]                   # 10
EXIT_DUST_USD = _s22.ORDER_SIZE["exit_min_order_value_usd"]                     # 10
HELD_DUST_USD = _s22.LONG_ENTRY["held_dust_resolution"]["held_dust_threshold_usd"]  # 10
LEVERAGE = 1

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "runs_detector_on_real_candles", "runs_labels",
    "runs_replay", "runs_backtest", "computes_pnl", "optimizes_parameters",
    "reparameterizes", "tunes_parameters", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "installs_scheduler", "sends_notifications", "sends_email", "calls_api",
    "uses_network", "uses_credentials", "uses_api_keys", "connects_signum", "uses_mcp",
    "accesses_hyperliquid", "connects_broker", "connects_exchange", "sends_trades",
    "sends_signal", "edits_bots", "edits_bot_title", "sets_trading_pair",
    "converts_funds", "creates_claude_routines", "uses_real_money", "places_orders",
    "contains_order_logic", "adds_new_instrument_class", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "advances_without_human_approval", "invents_rule_values",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


# ===========================================================================
# PURE DETECTOR -- operates on a SYNTHETIC run snapshot; executes nothing.
# ===========================================================================

def _is_number(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _usd_reference(row: dict) -> Any:
    """The asset's USD reference: indicators.cmcRefPriceUsd, else the newest closed
    candle's ohlc.c (per the spec's ticker-collision rule)."""
    ref = row.get("usd_reference")
    if ref is None:
        cs = row.get("candles") or []
        ref = cs[-1].get("c") if cs else None
    return ref


def _collision_reason(row: dict) -> Any:
    price = row.get("pair_price_usd")
    ref = _usd_reference(row)
    if price is None or ref is None or ref == 0:
        return "ticker_collision_missing_price_or_reference"
    if abs(price - ref) / abs(ref) > COLLISION_THRESH:
        return "ticker_collision_relative_diff_exceeds_0_5"
    return None


def run_detector(run_input: dict) -> dict[str, Any]:
    """PURE. Apply the FROZEN C22 spec to ONE synthetic Trend Radar run snapshot and
    return a deterministic SIMULATED decision set. Executes nothing; reads no real data.

    run_input = {
      nav, trading_account ('perpetual' or other), btc_symbol,
      rows: [ {symbol, market_rank, breakout_age_days,
               pair_price_usd, usd_reference,
               candles: [ {h, c, gc_trend, gc_upper, gc_filter}, ... ]} ],
      holdings: [ {symbol, side 'LONG'/'SHORT', usd_notional,
                   collateral_quote, unrealized_pnl_quote, size_base} ],
    }
    """
    nav = float(run_input.get("nav", 0.0))
    account = run_input.get("trading_account")
    rows = list(run_input.get("rows") or [])
    holdings = list(run_input.get("holdings") or [])
    btc_symbol = run_input.get("btc_symbol", "BTC")

    base: dict[str, Any] = {
        "aborted_not_perpetual": False,
        "data_quality": {"n_line_items": len(rows), "min_required": MIN_LINE_ITEMS,
                         "sufficient": len(rows) >= MIN_LINE_ITEMS,
                         "max_fetch_retries": MAX_FETCH_RETRIES},
        "btc": {"present": False, "downtrend": False},
        "market_rank_valid": False,
        "entries_invalid_no_market_rank": False,
        "long_exits": [], "short_exits": [],
        "long_entries": [], "short_entries": [], "skips": [],
        "order_sizing_simulation": [],
        "nav_snapshot": nav, "nav_recomputed_midrun": False,
        "one_position_per_coin_enforced_per_run": True,
        "entry_blocked_symbols": [],
    }

    # === STEP 1 precondition: perpetual account required (else STOP) ==========
    if account != "perpetual":
        base["aborted_not_perpetual"] = True
        base["abort_reason"] = "STOP_ROUTINE_CANNOT_SHORT_NOT_PERPETUAL"
        return base

    present = {r["symbol"] for r in rows}
    rowmap = {r["symbol"]: r for r in rows}

    # === STEP 3 BTC regime (+ human BTC-absent resolution) ===================
    btc_row = rowmap.get(btc_symbol)
    cs = (btc_row or {}).get("candles") or []
    btc_present = bool(cs and cs[-1].get("c") is not None
                       and cs[-1].get("gc_filter") is not None)
    if btc_present:
        btc_downtrend = cs[-1]["c"] < cs[-1]["gc_filter"]
    else:
        btc_downtrend = False   # human resolution: absent/incomplete -> not downtrend
    base["btc"] = {"present": btc_present, "downtrend": btc_downtrend}

    # === STEP 4 LONG EXITS ===================================================
    long_exited: set = set()
    for h in holdings:
        if h.get("side") != "LONG":
            continue
        sym = h["symbol"]
        if sym not in present:
            base["long_exits"].append({"symbol": sym, "close_pct": 100,
                                       "target_position_size": 0,
                                       "reason": "out_of_trend_radar"})
            long_exited.add(sym)
            continue
        latest = rowmap[sym]["candles"][-1]
        if latest["c"] < latest["gc_upper"]:
            base["long_exits"].append({"symbol": sym, "close_pct": 100,
                                       "target_position_size": 0,
                                       "reason": "close_below_upper_gc_band"})
            long_exited.add(sym)

    # === STEP 5 SHORT EXITS ==================================================
    short_exited: set = set()
    for h in holdings:
        if h.get("side") != "SHORT":
            continue
        sym = h["symbol"]
        if sym not in present:
            base["short_exits"].append({"symbol": sym, "close_pct": 100,
                                        "target_position_size": 0,
                                        "reason": "out_of_trend_radar"})
            short_exited.add(sym)
            continue
        latest = rowmap[sym]["candles"][-1]
        if latest["c"] > latest["gc_filter"]:
            base["short_exits"].append({"symbol": sym, "close_pct": 100,
                                        "target_position_size": 0,
                                        "reason": "stop_close_above_gc_filter"})
            short_exited.add(sym)
            continue
        entry_price = ((h["collateral_quote"] + h["unrealized_pnl_quote"])
                       / h["size_base"])
        if latest["c"] <= SHORT_TP_MULT * entry_price:
            base["short_exits"].append({"symbol": sym, "close_pct": 100,
                                        "target_position_size": 0,
                                        "reason": "take_profit_close_le_0_65x_entry",
                                        "derived_entry_price": round(entry_price, 8)})
            short_exited.add(sym)

    # === one-position-per-coin: block coins held-active OR touched this run ===
    held_active = {h["symbol"] for h in holdings
                   if float(h.get("usd_notional", 0.0)) >= HELD_DUST_USD}
    entry_blocked = set(held_active) | long_exited | short_exited

    # === market-rank validity resolution (unique numeric required) ===========
    ranks = [r.get("market_rank") for r in rows]
    numeric = [x for x in ranks if _is_number(x)]
    market_rank_valid = (len(numeric) == len(rows) and len(rows) > 0
                         and len(set(numeric)) == len(rows))
    base["market_rank_valid"] = market_rank_valid

    order_seq: list = []
    if not market_rank_valid:
        base["entries_invalid_no_market_rank"] = True
    else:
        top = sorted(rows, key=lambda r: r["market_rank"])[:TOP_N]

        # === STEP 6 LONG ENTRIES =============================================
        for r in top:
            sym = r["symbol"]
            if sym in entry_blocked:
                base["skips"].append({"symbol": sym, "stage": "long_entry",
                                      "reason": "already_held_or_touched_this_run"})
                continue
            cc = r.get("candles") or []
            if len(cc) < 2 or cc[-1].get("gc_upper") is None \
                    or cc[-2].get("gc_upper") is None:
                base["skips"].append({"symbol": sym, "stage": "long_entry",
                                      "reason": "missing_indicator_data"})
                continue
            coll = _collision_reason(r)
            if coll is not None:
                base["skips"].append({"symbol": sym, "stage": "long_entry",
                                      "reason": coll})
                continue
            latest, prev = cc[-1], cc[-2]
            if latest["c"] > latest["gc_upper"] and prev["c"] <= prev["gc_upper"]:
                age = r.get("breakout_age_days")
                recent = age is not None and age <= BREAKOUT_RECENT_DAYS
                size_pct = LONG_SIZE_RECENT_PCT if recent else LONG_SIZE_ELSE_PCT
                order_value = size_pct / 100.0 * nav
                if order_value < ENTRY_DUST_PCT_NAV / 100.0 * nav \
                        or order_value < ENTRY_DUST_USD:
                    base["skips"].append({"symbol": sym, "stage": "long_entry",
                                          "reason": "dust_below_entry_threshold"})
                    continue
                base["long_entries"].append({
                    "symbol": sym, "side": "LONG", "target_position_size_sign": 1,
                    "size_pct_nav": size_pct, "order_value_usd": round(order_value, 8),
                    "leverage": LEVERAGE, "breakout_recent": recent,
                    "reason": "crossover_up_through_upper_gc_band"})
                entry_blocked.add(sym)
                order_seq.append((sym, "LONG", order_value))

        # === STEP 7 SHORT ENTRIES ===========================================
        for r in top:
            sym = r["symbol"]
            if sym in entry_blocked:
                base["skips"].append({"symbol": sym, "stage": "short_entry",
                                      "reason": "already_held_or_touched_this_run"})
                continue
            cc = r.get("candles") or []
            if len(cc) < 2 or cc[-1].get("gc_filter") is None \
                    or cc[-2].get("gc_filter") is None:
                base["skips"].append({"symbol": sym, "stage": "short_entry",
                                      "reason": "missing_indicator_data"})
                continue
            coll = _collision_reason(r)
            if coll is not None:
                base["skips"].append({"symbol": sym, "stage": "short_entry",
                                      "reason": coll})
                continue
            latest, prev = cc[-1], cc[-2]
            kind = None
            size_pct = None
            if latest.get("gc_trend") == "Red" and latest["c"] < latest["gc_filter"] \
                    and prev["c"] >= prev["gc_filter"]:
                kind, size_pct = "hedge", HEDGE_SHORT_PCT
            elif (btc_downtrend and latest.get("gc_trend") == "Red"
                  and latest["h"] >= BEAR_HIGH_MULT * latest["gc_filter"]
                  and latest["c"] < latest["gc_filter"]):
                kind, size_pct = "bear", BEAR_SHORT_PCT
            if kind is None:
                continue
            order_value = size_pct / 100.0 * nav
            if order_value < ENTRY_DUST_PCT_NAV / 100.0 * nav \
                    or order_value < ENTRY_DUST_USD:
                base["skips"].append({"symbol": sym, "stage": "short_entry",
                                      "reason": "dust_below_entry_threshold"})
                continue
            base["short_entries"].append({
                "symbol": sym, "side": "SHORT", "target_position_size_sign": -1,
                "size_pct_nav": size_pct, "order_value_usd": round(order_value, 8),
                "leverage": LEVERAGE, "kind": kind,
                "reason": "hedge_cross_down_filter" if kind == "hedge"
                          else "bear_btc_downtrend_high_reaches_filter_close_below"})
            entry_blocked.add(sym)
            order_seq.append((sym, "SHORT", order_value))

    # === NAV-snapshot order sizing simulation (never reuse %, cap 100) =======
    quote_balance = nav   # NAV snapshot from step 1; never recomputed mid-run
    for sym, side, val in order_seq:
        pct = (val / quote_balance * 100.0) if quote_balance > 0 else 0.0
        capped = min(pct, 100.0)
        spend = min(val, quote_balance)
        quote_balance -= spend
        base["order_sizing_simulation"].append({
            "symbol": sym, "side": side, "target_value_usd": round(val, 8),
            "ordersize_pct_of_quote": round(capped, 6),
            "capped_at_100": pct > 100.0,
            "quote_balance_after": round(quote_balance, 8)})
    base["entry_blocked_symbols"] = sorted(entry_blocked)
    return base


# ===========================================================================
# SYNTHETIC fixtures (known-truth) + the dry-run that self-verifies them.
# ===========================================================================

def _c(h: float, close: float, trend: str, upper: float, filt: float) -> dict:
    return {"h": h, "c": close, "gc_trend": trend, "gc_upper": upper, "gc_filter": filt}


def _row(symbol: str, rank: int, candles: list, breakout_age_days: Any = None,
         pair_price_usd: Any = None, usd_reference: Any = None) -> dict:
    return {"symbol": symbol, "market_rank": rank, "candles": candles,
            "breakout_age_days": breakout_age_days,
            "pair_price_usd": pair_price_usd, "usd_reference": usd_reference}


def build_synthetic_fixtures() -> dict[str, dict]:
    """Hand-built SYNTHETIC run snapshots, one per spec branch. No real data."""
    # a clean non-colliding row needs pair_price ~= reference (use latest close).
    def clean_long_cross(sym, rank, age):
        # prev close <= upper (10 <= 10), latest close > upper (12 > 10): crossover up
        return _row(sym, rank,
                    [_c(11, 10.0, "Green", 10.0, 8.0), _c(13, 12.0, "Green", 10.0, 8.0)],
                    breakout_age_days=age, pair_price_usd=12.0, usd_reference=12.0)

    return {
        # 1) LONG ENTRY, breakout recent -> 8% NAV
        "long_entry_recent_8pct": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [clean_long_cross("AAA", 1, 10)], "holdings": []},
        # 2) LONG ENTRY, breakout NOT recent (age>25 / None) -> 2% NAV
        "long_entry_else_2pct": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [clean_long_cross("BBB", 1, 40)], "holdings": []},
        # 3) LONG EXIT: held long, close below upper band; + out-of-radar
        "long_exit_below_band_and_out": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [_row("HELDL", 1,
                          [_c(9, 8.0, "Grey", 10.0, 7.0), _c(9, 7.5, "Grey", 10.0, 7.0)],
                          pair_price_usd=7.5, usd_reference=7.5)],
            "holdings": [{"symbol": "HELDL", "side": "LONG", "usd_notional": 500.0},
                         {"symbol": "GONE", "side": "LONG", "usd_notional": 500.0}]},
        # 4) SHORT EXITS: stop (close>filter), take-profit (close<=0.65*entry), out
        "short_exit_stop_tp_out": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [
                _row("STOPS", 1, [_c(11, 9.0, "Red", 12.0, 8.0),
                                  _c(11, 9.0, "Red", 12.0, 8.0)],
                     pair_price_usd=9.0, usd_reference=9.0),
                _row("TPS", 2, [_c(7, 6.0, "Red", 12.0, 8.0),
                                _c(7, 6.0, "Red", 12.0, 8.0)],
                     pair_price_usd=6.0, usd_reference=6.0)],
            "holdings": [
                # stop: close 9 > filter 8 -> exit
                {"symbol": "STOPS", "side": "SHORT", "usd_notional": 300.0,
                 "collateral_quote": 100.0, "unrealized_pnl_quote": 0.0,
                 "size_base": 10.0},   # entry 10; close 9 not <= 6.5 but stop fires
                # take-profit: entry (100+0)/10 = 10; 0.65*10=6.5; close 6 <= 6.5 -> tp
                {"symbol": "TPS", "side": "SHORT", "usd_notional": 300.0,
                 "collateral_quote": 100.0, "unrealized_pnl_quote": 0.0,
                 "size_base": 10.0},
                # out of radar
                {"symbol": "SGONE", "side": "SHORT", "usd_notional": 300.0,
                 "collateral_quote": 100.0, "unrealized_pnl_quote": 0.0,
                 "size_base": 10.0}]},
        # 5) HEDGE SHORT: Red + cross DOWN through filter -> 3% NAV
        "hedge_short_3pct": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [_row("HED", 1, [_c(11, 9.0, "Red", 12.0, 8.0),
                                     _c(9, 7.0, "Red", 12.0, 8.0)],
                          pair_price_usd=7.0, usd_reference=7.0)],
            "holdings": []},
        # 6) BEAR SHORT: BTC downtrend + Red + high>=0.98*filter + close<filter -> 5%
        "bear_short_5pct": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [
                # BTC downtrend: close 90 < filter 100
                _row("BTC", 1, [_c(95, 90.0, "Red", 110.0, 100.0),
                                _c(95, 90.0, "Red", 110.0, 100.0)],
                     pair_price_usd=90.0, usd_reference=90.0),
                # bear: high 7.95 >= 0.98*8=7.84, close 7 < filter 8, prev close 7 < filter
                # (so hedge cross-down NOT met: prev 7 < 8) -> falls to bear
                _row("BEAR", 2, [_c(7.95, 7.0, "Red", 12.0, 8.0),
                                 _c(7.95, 7.0, "Red", 12.0, 8.0)],
                     pair_price_usd=7.0, usd_reference=7.0)],
            "holdings": []},
        # 7) BTC ABSENT -> downtrend False -> bear disabled; hedge still works
        "btc_absent_disables_bear_hedge_ok": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [
                # would-be bear (no prev cross), but BTC absent -> no short
                _row("WBEAR", 1, [_c(7.95, 7.0, "Red", 12.0, 8.0),
                                  _c(7.95, 7.0, "Red", 12.0, 8.0)],
                     pair_price_usd=7.0, usd_reference=7.0),
                # hedge still triggers (cross down filter)
                _row("WHED", 2, [_c(11, 9.0, "Red", 12.0, 8.0),
                                 _c(9, 7.0, "Red", 12.0, 8.0)],
                     pair_price_usd=7.0, usd_reference=7.0)],
            "holdings": []},
        # 8) ALREADY-HELD skip (active >=$10) vs HELD-DUST exception (<$10 allows entry)
        "held_active_skip_vs_held_dust_entry": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [clean_long_cross("ACTV", 1, 5), clean_long_cross("DUSTH", 2, 5)],
            "holdings": [{"symbol": "ACTV", "side": "LONG", "usd_notional": 500.0},
                         {"symbol": "DUSTH", "side": "LONG", "usd_notional": 4.0}]},
        # 9) ENTRY DUST skip: tiny NAV so 2% order < $10
        "entry_dust_skip": {
            "nav": 200.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [clean_long_cross("TINY", 1, 40)], "holdings": []},
        # 10) TICKER COLLISION skip: price vs ref diff > 0.5; + missing price
        "ticker_collision_skip": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [
                # |30 - 12| / 12 = 1.5 > 0.5 -> collision skip
                _row("COLL", 1, [_c(11, 10.0, "Green", 10.0, 8.0),
                                 _c(13, 12.0, "Green", 10.0, 8.0)],
                     breakout_age_days=5, pair_price_usd=30.0, usd_reference=12.0),
                # missing pair price -> collision-missing skip
                _row("NOPRICE", 2, [_c(11, 10.0, "Green", 10.0, 8.0),
                                    _c(13, 12.0, "Green", 10.0, 8.0)],
                     breakout_age_days=5, pair_price_usd=None, usd_reference=12.0)],
            "holdings": []},
        # 11) MARKET-RANK invalid (duplicate ranks) -> entries skipped/rejected
        "market_rank_invalid_skips_entries": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [clean_long_cross("R1", 1, 5), clean_long_cross("R2", 1, 5)],
            "holdings": []},
        # 12) NOT PERPETUAL -> aborted
        "not_perpetual_aborts": {
            "nav": 10000.0, "trading_account": "spot", "btc_symbol": "BTC",
            "rows": [clean_long_cross("X", 1, 5)], "holdings": []},
        # 13) NAV-snapshot sizing across two entries (never reuse %, cap behaviour)
        "nav_snapshot_two_entries": {
            "nav": 1000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [clean_long_cross("E1", 1, 5), clean_long_cross("E2", 2, 5)],
            "holdings": []},
        # 14) INSUFFICIENT line items (<50) flagged
        "insufficient_line_items": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [clean_long_cross("ONE", 1, 5)], "holdings": []},
        # 15) MISSING indicator (only 1 candle) -> skip
        "missing_indicator_skip": {
            "nav": 10000.0, "trading_account": "perpetual", "btc_symbol": "BTC",
            "rows": [_row("MISS", 1, [_c(13, 12.0, "Green", 10.0, 8.0)],
                          breakout_age_days=5, pair_price_usd=12.0, usd_reference=12.0)],
            "holdings": []},
    }


def _syms(items: list) -> set:
    return {i["symbol"] for i in items}


def run_synthetic_dry_run() -> dict[str, Any]:
    """Run the detector on every synthetic fixture and self-verify each against its
    known-truth expectation. Returns per-fixture result + pass flag. Pure."""
    fx = build_synthetic_fixtures()
    out: dict[str, Any] = {}

    def rec(name: str, checks: dict, result: dict) -> None:
        out[name] = {"checks": checks, "all_pass": all(checks.values()),
                     "result": result}

    r = run_detector(fx["long_entry_recent_8pct"])
    rec("long_entry_recent_8pct", {
        "one_long_entry": len(r["long_entries"]) == 1,
        "size_8pct": r["long_entries"][0]["size_pct_nav"] == LONG_SIZE_RECENT_PCT,
        "long_side": r["long_entries"][0]["target_position_size_sign"] == 1,
        "leverage_1x": r["long_entries"][0]["leverage"] == 1,
        "no_short": r["short_entries"] == []}, r)

    r = run_detector(fx["long_entry_else_2pct"])
    rec("long_entry_else_2pct", {
        "one_long_entry": len(r["long_entries"]) == 1,
        "size_2pct": r["long_entries"][0]["size_pct_nav"] == LONG_SIZE_ELSE_PCT}, r)

    r = run_detector(fx["long_exit_below_band_and_out"])
    rec("long_exit_below_band_and_out", {
        "two_long_exits": len(r["long_exits"]) == 2,
        "exits_HELDL_and_GONE": _syms(r["long_exits"]) == {"HELDL", "GONE"},
        "reasons": {e["reason"] for e in r["long_exits"]} ==
        {"close_below_upper_gc_band", "out_of_trend_radar"}}, r)

    r = run_detector(fx["short_exit_stop_tp_out"])
    rec("short_exit_stop_tp_out", {
        "three_short_exits": len(r["short_exits"]) == 3,
        "stop_present": any(e["reason"] == "stop_close_above_gc_filter"
                            for e in r["short_exits"]),
        "tp_present": any(e["reason"] == "take_profit_close_le_0_65x_entry"
                          for e in r["short_exits"]),
        "out_present": any(e["reason"] == "out_of_trend_radar"
                           for e in r["short_exits"])}, r)

    r = run_detector(fx["hedge_short_3pct"])
    rec("hedge_short_3pct", {
        "one_short": len(r["short_entries"]) == 1,
        "kind_hedge": r["short_entries"][0]["kind"] == "hedge",
        "size_3pct": r["short_entries"][0]["size_pct_nav"] == HEDGE_SHORT_PCT,
        "short_side": r["short_entries"][0]["target_position_size_sign"] == -1}, r)

    r = run_detector(fx["bear_short_5pct"])
    rec("bear_short_5pct", {
        "btc_downtrend": r["btc"]["downtrend"] is True,
        "one_bear_short": len([s for s in r["short_entries"]
                               if s["kind"] == "bear"]) == 1,
        "size_5pct": any(s["size_pct_nav"] == BEAR_SHORT_PCT
                         for s in r["short_entries"])}, r)

    r = run_detector(fx["btc_absent_disables_bear_hedge_ok"])
    rec("btc_absent_disables_bear_hedge_ok", {
        "btc_absent": r["btc"]["present"] is False,
        "downtrend_false": r["btc"]["downtrend"] is False,
        "no_bear": all(s["kind"] != "bear" for s in r["short_entries"]),
        "hedge_still_fires": any(s["kind"] == "hedge"
                                 for s in r["short_entries"])}, r)

    r = run_detector(fx["held_active_skip_vs_held_dust_entry"])
    rec("held_active_skip_vs_held_dust_entry", {
        "actv_skipped": any(s["symbol"] == "ACTV" and s["stage"] == "long_entry"
                            for s in r["skips"]),
        "dusth_entered": any(e["symbol"] == "DUSTH" for e in r["long_entries"])}, r)

    r = run_detector(fx["entry_dust_skip"])
    rec("entry_dust_skip", {
        "no_entry": r["long_entries"] == [],
        "dust_skip": any(s["reason"] == "dust_below_entry_threshold"
                         for s in r["skips"])}, r)

    r = run_detector(fx["ticker_collision_skip"])
    rec("ticker_collision_skip", {
        "no_entry": r["long_entries"] == [],
        "collision_skip": any("ticker_collision" in s["reason"]
                              for s in r["skips"])}, r)

    r = run_detector(fx["market_rank_invalid_skips_entries"])
    rec("market_rank_invalid_skips_entries", {
        "market_rank_invalid": r["market_rank_valid"] is False,
        "entries_invalid_flag": r["entries_invalid_no_market_rank"] is True,
        "no_entries": r["long_entries"] == [] and r["short_entries"] == []}, r)

    r = run_detector(fx["not_perpetual_aborts"])
    rec("not_perpetual_aborts", {
        "aborted": r["aborted_not_perpetual"] is True,
        "no_entries": r["long_entries"] == [] and r["short_entries"] == []}, r)

    r = run_detector(fx["nav_snapshot_two_entries"])
    sim = r["order_sizing_simulation"]
    rec("nav_snapshot_two_entries", {
        "two_orders": len(sim) == 2,
        "nav_not_recomputed": r["nav_recomputed_midrun"] is False,
        "balance_decrements": (len(sim) == 2
                               and sim[1]["quote_balance_after"]
                               < sim[0]["quote_balance_after"]),
        "ordersize_pct_not_reused": (len(sim) == 2
                                     and sim[0]["ordersize_pct_of_quote"]
                                     != sim[1]["ordersize_pct_of_quote"])}, r)

    r = run_detector(fx["insufficient_line_items"])
    rec("insufficient_line_items", {
        "flagged_insufficient": r["data_quality"]["sufficient"] is False,
        "min_required_50": r["data_quality"]["min_required"] == MIN_LINE_ITEMS}, r)

    r = run_detector(fx["missing_indicator_skip"])
    rec("missing_indicator_skip", {
        "no_entry": r["long_entries"] == [],
        "missing_skip": any(s["reason"] == "missing_indicator_data"
                            for s in r["skips"])}, r)

    return out


# ===========================================================================
# the dry-run record + validator.
# ===========================================================================

def get_candidate_22_detector_dry_run_label() -> str:
    return (
        "Candidate #22 external_signum_trend_radar_gc_long_short_v1 detector spec + "
        "synthetic dry-run (READ-ONLY, RESEARCH ONLY). A deterministic detector of the "
        "FROZEN C22 spec, exercised ONLY on synthetic Trend Radar fixtures: long entry "
        "(upper-band crossover, 8%/2% breakout sizing), long exit (below band / "
        "out-of-radar), hedge short (Red + cross-down-filter 3%), bear short (BTC "
        "downtrend + Red + high>=0.98x filter + close<filter 5%), short exits "
        "(stop/0.65x take-profit/out), already-held + one-position-per-coin skip, "
        "held-dust (<$10) exception, entry-dust skip, ticker-collision (>0.5) skip, "
        "BTC-absent resolution (downtrend False / bear off / hedge on), market-rank "
        "validity, perpetual precondition, >=50 line-item gate, and NAV-snapshot order "
        "sizing (never reuse %, cap 100). Connects to NOTHING, runs on NO real candles, "
        "executes NOTHING. PARAMS single-sourced from the frozen spec; NO values "
        "invented. NOT a profitability claim.")


def get_candidate_22_detector_dry_run_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_DRY_RUN


def build_c22_detector_dry_run() -> dict[str, Any]:
    """Assemble the frozen C22 detector-spec + synthetic dry-run record. Pure; no I/O.
    Chain-gated on the committed C22 spec (verdict frozen)."""
    spec = _s22.build_c22_spec()
    spec_valid = _s22.validate_c22_spec(spec)["valid"]
    spec_verdict = spec.get("verdict")

    blockers: list = []
    if not spec_valid:
        blockers.append("c22_spec_invalid")
    if spec_verdict != EXPECTED_SPEC_VERDICT:
        blockers.append("c22_spec_not_frozen")

    dry = run_synthetic_dry_run()
    all_fixtures_pass = all(v["all_pass"] for v in dry.values())

    record: dict[str, Any] = {
        "schema_version": DR22_SCHEMA_VERSION, "mode": DR22_MODE, "lane": DR22_LANE,
        "label": get_candidate_22_detector_dry_run_label(),
        "candidate_id": CANDIDATE_ID, "candidate_token": CANDIDATE_TOKEN,
        "candidate_family": CANDIDATE_FAMILY, "candidate_name": CANDIDATE_NAME,
        "is_detector_dry_run_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_DR22_FROZEN if not blockers and all_fixtures_pass
                    else "C22_DETECTOR_DRY_RUN_BLOCKED"),
        # chain provenance (gated on the frozen spec)
        "spec_valid": spec_valid, "spec_verdict": spec_verdict,
        "chain_gated_on_c22_spec": not blockers,
        "spec_commit": SPEC_COMMIT,
        # the detector is synthetic-only + research-only
        "uses_synthetic_fixtures_only": True,
        "runs_on_real_candles": False,
        "params_single_sourced_from_frozen_spec": True,
        "no_values_invented": True,
        "rules_reused_from_committed_spec": True,
        # detector parameters echoed (single-sourced)
        "detector_params": {
            "min_line_items": MIN_LINE_ITEMS, "max_fetch_retries": MAX_FETCH_RETRIES,
            "top_n_rows": TOP_N, "breakout_recent_days": BREAKOUT_RECENT_DAYS,
            "long_size_recent_pct": LONG_SIZE_RECENT_PCT,
            "long_size_else_pct": LONG_SIZE_ELSE_PCT,
            "hedge_short_pct": HEDGE_SHORT_PCT, "bear_short_pct": BEAR_SHORT_PCT,
            "bear_high_multiple": BEAR_HIGH_MULT, "short_take_profit_multiple":
            SHORT_TP_MULT, "collision_threshold": COLLISION_THRESH,
            "entry_dust_pct_nav": ENTRY_DUST_PCT_NAV, "entry_dust_usd": ENTRY_DUST_USD,
            "exit_dust_usd": EXIT_DUST_USD, "held_dust_usd": HELD_DUST_USD,
            "leverage": LEVERAGE},
        # the synthetic dry-run results (self-verified)
        "synthetic_fixtures": sorted(build_synthetic_fixtures().keys()),
        "dry_run_results": dry,
        "all_fixtures_pass": all_fixtures_pass,
        # identity
        "is_directional": True, "is_long_short_symmetric": True,
        "gate_sequence": list(GATE_SEQUENCE),
        "human_review_required": True,
        "current_loop_stage": "detector_spec_dry_run",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_DRY_RUN,
        "advances_nothing": True,
        # downstream gates locked
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_real_candle_detection": True, "no_labels": True, "no_replay": True,
        "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_data_fetch": True, "no_real_data_access": True, "no_invent_values": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_scheduler_install": True,
        "no_signum_connection": True, "no_mcp": True, "no_hyperliquid": True,
        "no_api_keys": True, "no_credentials": True, "no_send_email": True,
        "no_bot_edits": True, "no_set_trading_pair": True, "no_convert_funds": True,
        "no_claude_routines": True, "no_send_trades": True, "no_send_signal": True,
        "no_broker": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True, "no_downstream_gate_unlock": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c22_detector_dry_run(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the unit is research-only,
    detector-dry-run-only, chain-gated on the frozen C22 spec (verdict + pinned commit),
    SYNTHETIC-only (no real candles), with detector params single-sourced from the frozen
    spec (every value matching, none invented), ALL synthetic fixtures passing their
    known-truth checks (long/short entry+exit, skip, dust, collision, BTC regime+absent,
    market-rank, NAV-snapshot sizing), downstream gates locked, advancing nothing, with
    every capability flag False."""
    failures: list = []
    if record.get("mode") != DR22_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_detector_dry_run_only") is not True:
        failures.append("not_detector_dry_run_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_DR22_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate on the frozen, pinned spec
    if record.get("spec_valid") is not True:
        failures.append("spec_not_valid")
    if record.get("spec_verdict") != EXPECTED_SPEC_VERDICT:
        failures.append("spec_not_frozen")
    if record.get("chain_gated_on_c22_spec") is not True:
        failures.append("not_chain_gated_on_spec")
    if record.get("spec_commit") != SPEC_COMMIT:
        failures.append("spec_commit_not_pinned")

    # synthetic-only + params single-sourced + nothing invented
    if record.get("uses_synthetic_fixtures_only") is not True:
        failures.append("not_synthetic_only")
    if record.get("runs_on_real_candles") is not False:
        failures.append("must_not_run_real_candles")
    if record.get("params_single_sourced_from_frozen_spec") is not True:
        failures.append("params_not_single_sourced")
    if record.get("no_values_invented") is not True:
        failures.append("values_may_be_invented")

    # detector params must match the frozen spec values exactly
    p = record.get("detector_params") or {}
    expected = {
        "min_line_items": 50, "max_fetch_retries": 3, "top_n_rows": 50,
        "breakout_recent_days": 25, "long_size_recent_pct": 8.0,
        "long_size_else_pct": 2.0, "hedge_short_pct": 3.0, "bear_short_pct": 5.0,
        "bear_high_multiple": 0.98, "short_take_profit_multiple": 0.65,
        "collision_threshold": 0.5, "entry_dust_pct_nav": 1.0, "entry_dust_usd": 10,
        "exit_dust_usd": 10, "held_dust_usd": 10, "leverage": 1}
    for k, v in expected.items():
        if p.get(k) != v:
            failures.append("param_mismatch_%s" % k)

    # ALL synthetic fixtures present and passing their known-truth checks
    dry = record.get("dry_run_results") or {}
    required_fixtures = {
        "long_entry_recent_8pct", "long_entry_else_2pct",
        "long_exit_below_band_and_out", "short_exit_stop_tp_out", "hedge_short_3pct",
        "bear_short_5pct", "btc_absent_disables_bear_hedge_ok",
        "held_active_skip_vs_held_dust_entry", "entry_dust_skip",
        "ticker_collision_skip", "market_rank_invalid_skips_entries",
        "not_perpetual_aborts", "nav_snapshot_two_entries", "insufficient_line_items",
        "missing_indicator_skip"}
    for fx in required_fixtures:
        if fx not in dry:
            failures.append("fixture_missing_%s" % fx)
        elif dry[fx].get("all_pass") is not True:
            failures.append("fixture_failed_%s" % fx)
    if record.get("all_fixtures_pass") is not True:
        failures.append("not_all_fixtures_pass")

    # gate sequence + downstream locks + advances nothing
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_DRY_RUN:
        failures.append("next_action_not_labels_gate")
    if record.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_real_candle_detection", "no_labels", "no_replay",
                "no_pnl", "no_data_fetch", "no_invent_values", "no_commit", "no_push",
                "no_signum_connection", "no_mcp", "no_hyperliquid", "no_api_keys",
                "no_credentials", "no_send_email", "no_bot_edits", "no_set_trading_pair",
                "no_convert_funds", "no_claude_routines", "no_send_trades",
                "no_order_logic", "no_paper_trading", "no_live_trading", "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

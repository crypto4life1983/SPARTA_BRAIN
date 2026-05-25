"""s8 D1 NO-PYRAMID execution guard -- runtime safety invariants.

NO MODULE-LEVEL SIDE EFFECTS. Pure declarations + functions only.
No broker / exchange / network / wallet imports anywhere in this file.
No Databento / QuantConnect API calls.

Inherits Phase 2 safety contracts (C1-C8) byte-equivalent.
DIAGNOSTIC_ONLY_NOT_LIVE_GRADE. Trading PAUSED. Live BLOCKED_AT_6_GATES.
"""

from __future__ import annotations

# Sealed-chain shas (sha-pinned; re-verified at Initialize):
TIER_N_SPEC_SEAL_SHA256    = "8cff6babf8e4a451adf02e94a684924ff8b32a7e0f5a795a13c65c845a12e0f4"
PLAN_LOCK_SEAL_SHA256      = "612abbbda7235c8c01239000cf997c804cd8178d88d2afbb9752004aed34e0a1"
PHASE2_PLAN_SEAL_SHA256    = "5e6fccd1aeb40db7daf850ab60eff2947a03a082a6bcb5b332c967e2d8f9c826"
PREDECESSOR_SEAL_SHA256    = "6b7bdb4c350f4a779611546dcb32f6a83db2371c66d7b6ba0118121783801441"
PHASE2_TEMPLATE_MD_SHA256  = "1812f4854a23e7a148257c88133042ea1e383725f4875e762475260ae3658981"
PHASE2_TEMPLATE_JSON_SHA256 = "695a9fb6e0cb6ae5395d467471f2c55d3d90a7030443ca87e4c1d220335f4a32"

# Forbidden imports (any presence in the runtime sys.modules of these is a hard fail):
FORBIDDEN_IMPORTS = (
    "ccxt",
    "kraken",
    "binance",
    "binance_client",
    "alpaca",
    "alpaca_trade_api",
    "ibapi",
    "ib_insync",
    "interactive_brokers",
    "MetaTrader5",
    "oanda",
    "tradier",
    "tradestation",
    "polygon",
    "iexcloud",
    "yfinance",
    "alpha_vantage",
    "databento",
)

# Forbidden output strings (any of these appearing in any diagnostic output is a hard fail):
FORBIDDEN_OUTPUT_TOKENS = (
    "BUY_NOW", "SELL_NOW", "ENTER_LIVE", "EXECUTE_LIVE", "PLACE_ORDER",
    "FRC_GRANTED", "LIVE_TRADING_ENABLED", "READY_FOR_LIVE",
    "PROFITABLE_STRATEGY", "MONEY_PROVEN",
)

# Status strings that MUST appear in every diagnostic JSON:
REQUIRED_OUTPUT_STRINGS = (
    "PAUSED",
    "BLOCKED_AT_6_GATES",
    "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE",
)


class GuardViolation(RuntimeError):
    """Raised when any invariant is violated. Should fail closed."""


def assert_no_forbidden_imports(modules_iter) -> dict:
    """Check sys.modules (or any iterable of module names) for forbidden brokers.

    Returns a dict with 'pass' bool and 'matches' list. Does NOT raise on its own
    so the caller (algorithm Initialize) can decide whether to raise or log.
    """
    names = set(modules_iter)
    hits = [m for m in FORBIDDEN_IMPORTS if m in names or any(name.startswith(m + ".") for name in names)]
    return {"pass": len(hits) == 0, "matches": hits}


def assert_no_forbidden_output_strings(blob: str) -> dict:
    """Scan a string (typically the JSON serialization of a diagnostic) for forbidden tokens."""
    hits = [t for t in FORBIDDEN_OUTPUT_TOKENS if t in blob]
    return {"pass": len(hits) == 0, "matches": hits}


def assert_required_output_strings(blob: str) -> dict:
    """Confirm the required status strings appear at least once in the diagnostic blob."""
    missing = [t for t in REQUIRED_OUTPUT_STRINGS if t not in blob]
    return {"pass": len(missing) == 0, "missing": missing}


def assert_live_mode_refused(algo_obj) -> dict:
    """Verify the algorithm refuses LiveMode. Caller passes self (or self.LiveMode)."""
    live = getattr(algo_obj, "LiveMode", None)
    if live is None:
        # Local-engine path: LiveMode not present. Pass.
        return {"pass": True, "live_mode": None, "note": "no_qc_runtime"}
    if bool(live):
        return {"pass": False, "live_mode": True, "note": "LIVE_PATH_DETECTED"}
    return {"pass": True, "live_mode": False, "note": "paper_only"}


def assert_chain_shas_present(constants_module) -> dict:
    """Confirm the four chain shas + two template shas are embedded in the runtime constants."""
    required = [
        ("TIER_N_SPEC_SEAL_SHA256",      TIER_N_SPEC_SEAL_SHA256),
        ("PLAN_LOCK_SEAL_SHA256",        PLAN_LOCK_SEAL_SHA256),
        ("PHASE2_PLAN_SEAL_SHA256",      PHASE2_PLAN_SEAL_SHA256),
        ("PREDECESSOR_SEAL_SHA256",      PREDECESSOR_SEAL_SHA256),
        ("PHASE2_TEMPLATE_MD_SHA256",    PHASE2_TEMPLATE_MD_SHA256),
        ("PHASE2_TEMPLATE_JSON_SHA256",  PHASE2_TEMPLATE_JSON_SHA256),
    ]
    mismatches = []
    for name, expected in required:
        actual = getattr(constants_module, name, None)
        if actual != expected:
            mismatches.append({"name": name, "expected": expected, "actual": actual})
    return {"pass": len(mismatches) == 0, "mismatches": mismatches}


def assert_window_ceiling(engine_end_date, ceiling_tuple) -> dict:
    """Confirm engine EndDate <= plan_lock_window_ceiling (C2 ceiling check)."""
    import datetime as _dt
    ceiling = _dt.date(*ceiling_tuple)
    if engine_end_date > ceiling:
        return {"pass": False, "engine_end_date": str(engine_end_date), "ceiling": str(ceiling)}
    return {"pass": True, "engine_end_date": str(engine_end_date), "ceiling": str(ceiling)}


def assert_engine_dates_match_config(engine_start, engine_end, config_start_tuple, config_end_tuple) -> dict:
    """C2 Initialize cross-check."""
    import datetime as _dt
    cs = _dt.date(*config_start_tuple)
    ce = _dt.date(*config_end_tuple)
    if engine_start != cs:
        return {"pass": False, "error": "CONFIG_START_DATE_MISMATCH", "engine": str(engine_start), "config": str(cs)}
    if engine_end != ce:
        return {"pass": False, "error": "CONFIG_END_DATE_MISMATCH", "engine": str(engine_end), "config": str(ce)}
    return {"pass": True, "engine_start": str(engine_start), "engine_end": str(engine_end)}


def full_guard_check(*, algo_obj, modules_iter, diagnostic_blob, constants_module,
                     engine_start, engine_end, config_start_tuple, config_end_tuple,
                     ceiling_tuple) -> dict:
    """One-stop guard check for use at OnEndOfAlgorithm.

    Returns a dict of all sub-checks plus overall_pass.
    Does NOT raise; caller decides the action.
    """
    results = {
        "no_forbidden_imports":      assert_no_forbidden_imports(modules_iter),
        "no_forbidden_output_tokens": assert_no_forbidden_output_strings(diagnostic_blob),
        "required_output_strings":   assert_required_output_strings(diagnostic_blob),
        "live_mode_refused":         assert_live_mode_refused(algo_obj),
        "chain_shas_present":        assert_chain_shas_present(constants_module),
        "engine_dates_match_config": assert_engine_dates_match_config(engine_start, engine_end, config_start_tuple, config_end_tuple),
        "window_ceiling_ok":         assert_window_ceiling(engine_end, ceiling_tuple),
    }
    overall = all(r.get("pass", False) for r in results.values())
    results["overall_pass"] = overall
    return results

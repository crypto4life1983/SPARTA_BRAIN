"""s16-d1 execution guard. C1-C8 attestation; trend exit/stop guards. NO execution/order/fetch."""

EXPECTED_TIER_SPEC_SEAL = "359aea43df85c153c8cbf2b7a84ddeaa78d6516fe43769e34b052b4f88c60df8"
EXPECTED_PLAN_LOCK_SEAL = "957ca333d59a24e942a1c5f6c40375035942e2fcc53bc461c0ffbe5684d60f86"
EXPECTED_P2_PHASE2_PLAN_SEAL = "3fa8634d3c5c4317ae27a498542cac7757a50029de766967d2a729cddcf73df5"

S16_DR9_RESULT_SEAL = "ec856253a28f7d538704b2610da8d1c3b13823335d741c356dd41259488b12e9"
S15_D1_P7_TERMINAL_COMMIT = "8abcd31"
S14_D1_CROSS_SECTOR_P7_TERMINAL_COMMIT = "6485ea9"
FRAMEWORK_DR10_V2_COMMIT = "78cd22e"

LOCKED_UNIVERSE = ["AAPL", "MSFT", "NVDA", "JPM", "XOM", "UNH", "WMT", "KO", "META", "AMZN", "JNJ", "CVX"]


def assert_seal_inheritance(config):
    for key, expected in (("tier_spec_seal", EXPECTED_TIER_SPEC_SEAL), ("plan_lock_seal", EXPECTED_PLAN_LOCK_SEAL), ("p2_phase2_plan_seal", EXPECTED_P2_PHASE2_PLAN_SEAL)):
        if config.get(key) != expected:
            raise Exception(f"K8_SEALED_PARENT_DRIFT: CONFIG[{key!r}]={config.get(key)!r} expected {expected!r}")


def assert_no_forbidden_order_paths(config):
    if config.get("brokerage_model_name") != "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6":
        raise Exception("BROKERAGE_MODEL_FORBIDDEN: s16-d1 P3 BUILD authorizes only CSV-simulator at P6.")
    if config.get("permanent_live_block") is not True:
        raise Exception("PERMANENT_LIVE_BLOCK_NOT_SET: invariant violation")


def assert_rec1_equivalent_binding_preserved(config):
    if not config.get("rec1_equivalent_binding"):
        raise Exception("REC1_EQUIVALENT_BINDING_NOT_SET: invariant violation")
    if "OOS K9 reachable" not in (config.get("rec1_equivalent_oos_k9_disclosure") or ""):
        raise Exception("REC1_EQUIVALENT_OOS_K9_RISK_DISCLOSURE_MISSING_OR_DEMOTED")


def assert_locked_strategy_params(config):
    expected = {
        "mechanic_family": "donchian_breakout_trend_trailing_stop",  # DA2
        "n_entry_donchian": 20,  # DA6
        "n_exit_donchian_trailing": 10,  # DA8
        "exit_rule": "TRAILING_DONCHIAN_CHANNEL",  # DA9
        "initial_catastrophe_stop_atr_multiple": 2.0,  # DA10
        "stop_is_tight_mean_reversion_stop": False,  # DA10 invariant
        "atr_period": 14,  # DA11
        "sizing_method": "vol_normalized",  # DA12
        "risk_pct_per_trade": 0.005,  # DA3=B
        "max_positions_per_name": 1,  # DA18
        "max_total_positions": 6,  # DA18
        "pyramid_method": "NONE",  # DA18
        "start_cash_usd": 100000,  # DA4=B
        "warmup_days": 40,  # DA19
        "verdict_min_closed_trades": 100,  # K9
        "adjustment_convention": "split_only",  # DA15
        "data_vendor": "tiingo",  # DA16
    }
    for key, want in expected.items():
        if config.get(key) != want:
            raise Exception(f"LOCKED_PARAM_DRIFT: CONFIG[{key!r}]={config.get(key)!r} expected {want!r}")


def assert_trailing_donchian_exit(config):
    """DA9: exit MUST be the trailing Donchian channel (NOT an oscillator-threshold / exit-to-mean rule)."""
    if config.get("exit_rule") != "TRAILING_DONCHIAN_CHANNEL":
        raise Exception(f"EXIT_RULE_DRIFT: CONFIG['exit_rule']={config.get('exit_rule')!r} expected 'TRAILING_DONCHIAN_CHANNEL'")
    if not (isinstance(config.get("n_exit_donchian_trailing"), int) and config.get("n_exit_donchian_trailing") > 0):
        raise Exception("TRAILING_EXIT_CHANNEL_INVALID")


def assert_initial_stop_2atr_not_tight(config):
    """DA10: initial stop MUST be the 2xATR vol-scaled floor, NOT a tight mean-reversion stop."""
    if config.get("stop_is_tight_mean_reversion_stop") is not False:
        raise Exception("STOP_DESIGN_DRIFT: stop_is_tight_mean_reversion_stop must be False")
    if config.get("initial_catastrophe_stop_atr_multiple") != 2.0:
        raise Exception(f"INITIAL_STOP_ATR_MULTIPLE_DRIFT: {config.get('initial_catastrophe_stop_atr_multiple')!r} expected 2.0")
    if config.get("stop_method") != "trailing_donchian_plus_2atr_initial_floor":
        raise Exception(f"STOP_METHOD_DRIFT: {config.get('stop_method')!r}")


def assert_boundary_alignment(config):
    if config.get("eod_cancel_time") != config.get("rth_safe_window_close"):
        raise Exception("C4_BOUNDARY_MISALIGNED")


def assert_split_only_convention(config):
    if config.get("asset_class") != "cash_equity":
        raise Exception("C5_ASSET_CLASS_NOT_CASH_EQUITY")
    if config.get("adjustment_convention") != "split_only":
        raise Exception("C5_ADJUSTMENT_CONVENTION_NOT_SPLIT_ONLY")
    if config.get("dividends_adjusted") is not False:
        raise Exception("C5_DIVIDENDS_MUST_NOT_BE_ADJUSTED_UNDER_SPLIT_ONLY")
    actions = config.get("known_corporate_actions") or []
    for sym, ex, fac in (("AMZN", "2022-06-06", 20.0), ("WMT", "2024-02-26", 3.0)):
        a = next((x for x in actions if x.get("symbol") == sym and x.get("date") == ex), None)
        if a is None or not (a.get("applied") and a.get("dr9_verified")):
            raise Exception(f"C5_{sym}_SPLIT_NOT_DOCUMENTED_OR_NOT_VERIFIED")


def assert_universe_locked(config):
    if list(config.get("universe") or []) != LOCKED_UNIVERSE:
        raise Exception(f"UNIVERSE_DRIFT: CONFIG['universe']={config.get('universe')!r} expected {LOCKED_UNIVERSE!r}")


def assert_no_leverage_cap(config):
    if "unlevered_cash_equity" not in (config.get("leverage_cap") or ""):
        raise Exception("K11_LEVERAGE_CAP_UNEXPECTEDLY_SET_FOR_CASH_EQUITY")


def full_guard_check(config, safety_counters=None):
    results = {"checks": {}, "errors": [], "overall_pass": False}

    def _run(name, fn):
        try:
            fn(config)
            results["checks"][name] = True
        except Exception as exc:
            results["checks"][name] = False
            results["errors"].append(f"{name}: {type(exc).__name__}: {exc}")

    _run("assert_seal_inheritance", assert_seal_inheritance)
    _run("assert_no_forbidden_order_paths", assert_no_forbidden_order_paths)
    _run("assert_rec1_equivalent_binding_preserved", assert_rec1_equivalent_binding_preserved)
    _run("assert_locked_strategy_params", assert_locked_strategy_params)
    _run("assert_trailing_donchian_exit", assert_trailing_donchian_exit)
    _run("assert_initial_stop_2atr_not_tight", assert_initial_stop_2atr_not_tight)
    _run("assert_boundary_alignment", assert_boundary_alignment)
    _run("assert_split_only_convention", assert_split_only_convention)
    _run("assert_universe_locked", assert_universe_locked)
    _run("assert_no_leverage_cap", assert_no_leverage_cap)
    if safety_counters is not None:
        stale = safety_counters.get("stale_fill_warning_count", 0)
        results["checks"]["safety_counters_all_zero"] = (stale == 0)
        if stale != 0:
            results["errors"].append(f"safety_counters_all_zero: stale_fill_warning_count={stale}")
    results["overall_pass"] = all(results["checks"].values()) and not results["errors"]
    return results

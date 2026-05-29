"""s18-d1 execution guard. C1-C8 attestation; weekly RS rotation guards; K13 fold-scheme + no-refit guards. NO execution/order/fetch."""

EXPECTED_TIER_SPEC_SEAL = "06e96e3cc7902a196cba33cc5cb57587fb4fd3c1034737715b85aebaf546940e"
EXPECTED_PLAN_LOCK_SEAL = "22584b83561a5ca53524c8f36205690224822fb71fca603d5abde47581c5be35"
EXPECTED_P2_PHASE2_PLAN_SEAL = "c988cefaaa60c8e38d649a301fed7ed47065a1f91925a61c290c179cd85732c7"

S17_DR9_RESULT_SEAL = "85667ab3238a27b2f020c3644e4b7e2643b64be48d2a3f21cd75123b9b7677e3"
WALK_FORWARD_K13_SEAL = "4268d6f75bbc095a795510f7d8ccc50c2d8886eef36f50f769b79342002893d2"
FRAMEWORK_DR10_V2_COMMIT = "78cd22e"
S17_D1_P7_P11_TERMINAL_COMMIT = "7592e18"

LOCKED_UNIVERSE = ["AAPL", "MSFT", "NVDA", "JPM", "XOM", "UNH", "WMT", "KO", "META", "AMZN", "JNJ", "CVX",
                   "GOOGL", "V", "MA", "HD", "PG", "COST", "ABBV", "MRK", "BAC", "CAT", "DIS", "COP"]

EXPECTED_K13_FOLDS = [
    ("F1", 160, 478), ("F2", 479, 797), ("F3", 798, 1116), ("F4", 1117, 1435), ("F5", 1436, 1758),
]


def assert_seal_inheritance(config):
    for key, expected in (("tier_spec_seal", EXPECTED_TIER_SPEC_SEAL), ("plan_lock_seal", EXPECTED_PLAN_LOCK_SEAL), ("p2_phase2_plan_seal", EXPECTED_P2_PHASE2_PLAN_SEAL)):
        if config.get(key) != expected:
            raise Exception(f"K8_SEALED_PARENT_DRIFT: CONFIG[{key!r}]={config.get(key)!r} expected {expected!r}")


def assert_no_forbidden_order_paths(config):
    if config.get("brokerage_model_name") != "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6":
        raise Exception("BROKERAGE_MODEL_FORBIDDEN: s18-d1 P3 BUILD authorizes only CSV-simulator at P6.")
    if config.get("permanent_live_block") is not True:
        raise Exception("PERMANENT_LIVE_BLOCK_NOT_SET: invariant violation")


def assert_rec1_equivalent_binding_preserved(config):
    if not config.get("rec1_equivalent_binding"):
        raise Exception("REC1_EQUIVALENT_BINDING_NOT_SET: invariant violation")
    if "OOS K9" not in (config.get("rec1_equivalent_oos_k9_disclosure") or ""):
        raise Exception("REC1_EQUIVALENT_OOS_K9_RISK_DISCLOSURE_MISSING_OR_DEMOTED")


def assert_locked_strategy_params(config):
    expected = {
        "mechanic_family": "cross_sectional_relative_strength_rotation_weekly_long_only",  # DA2
        "momentum_lookback_L": 126,  # DA6
        "momentum_skip_S": 21,  # DA8
        "top_m_held": 8,  # DA10
        "rebalance_cadence_R_days": 5,  # DA11 (WEEKLY)
        "exit_rule": "ROTATION_RELATIVE_RANK",  # DA12
        "exit_is_trailing_or_atr_stop": False,  # DA12 invariant
        "sizing_method": "equal_weight",  # DA3
        "signal_direction": "long-only",  # DA20
        "shorting_enabled": False,  # DA20
        "max_total_positions": 8,  # DA10/DA18
        "pyramid_method": "NONE",  # DA18
        "start_cash_usd": 100000,  # DA4=B
        "warmup_days": 160,  # DA19
        "verdict_min_closed_trades": 100,  # K9
        "adjustment_convention": "split_only",  # DA15
        "data_vendor": "tiingo",  # DA16
    }
    for key, want in expected.items():
        if config.get(key) != want:
            raise Exception(f"LOCKED_PARAM_DRIFT: CONFIG[{key!r}]={config.get(key)!r} expected {want!r}")


def assert_rotation_exit(config):
    if config.get("exit_rule") != "ROTATION_RELATIVE_RANK":
        raise Exception(f"EXIT_RULE_DRIFT: CONFIG['exit_rule']={config.get('exit_rule')!r} expected 'ROTATION_RELATIVE_RANK'")
    if config.get("exit_is_trailing_or_atr_stop") is not False:
        raise Exception("EXIT_DESIGN_DRIFT: exit_is_trailing_or_atr_stop must be False (relative-rank exit only)")


def assert_equal_weight_sizing(config):
    if config.get("sizing_method") != "equal_weight":
        raise Exception(f"SIZING_DRIFT: {config.get('sizing_method')!r} expected 'equal_weight'")
    if abs((config.get("per_position_weight_fraction") or 0) - (1.0 / 8.0)) > 1e-9:
        raise Exception("PER_POSITION_WEIGHT_DRIFT: expected 1/8")


def assert_long_only(config):
    if config.get("signal_direction") != "long-only":
        raise Exception(f"SIGNAL_DIRECTION_DRIFT: {config.get('signal_direction')!r} expected 'long-only'")
    if config.get("shorting_enabled") is not False:
        raise Exception("SHORTING_ENABLED_MUST_BE_FALSE")
    if config.get("leverage") != "NONE":
        raise Exception("LEVERAGE_MUST_BE_NONE")


def assert_momentum_params_locked(config):
    for key, want in (("momentum_lookback_L", 126), ("momentum_skip_S", 21), ("top_m_held", 8), ("rebalance_cadence_R_days", 5)):
        if config.get(key) != want:
            raise Exception(f"MOMENTUM_PARAM_DRIFT: CONFIG[{key!r}]={config.get(key)!r} expected {want!r}")


def assert_weekly_cadence(config):
    """DA11: rebalance cadence MUST be weekly (R=5); NOT tuned after the pre-SEAL K9 measurement."""
    if config.get("rebalance_cadence_R_days") != 5:
        raise Exception(f"CADENCE_DRIFT: rebalance_cadence_R_days={config.get('rebalance_cadence_R_days')!r} expected 5 (weekly)")


def assert_k13_fold_scheme_locked(config):
    scheme = config.get("k13_fold_scheme") or {}
    if scheme.get("n_folds") != 5:
        raise Exception(f"K13_N_FOLDS_DRIFT: {scheme.get('n_folds')!r} expected 5")
    if scheme.get("boundaries_searched") is not False:
        raise Exception("K13_FOLD_BOUNDARIES_SEARCHED_MUST_BE_FALSE")
    folds = scheme.get("folds") or []
    got = [(f.get("fold"), f.get("idx_start"), f.get("idx_end")) for f in folds]
    if got != EXPECTED_K13_FOLDS:
        raise Exception(f"K13_FOLD_BOUNDARY_DRIFT: {got!r} expected {EXPECTED_K13_FOLDS!r}")
    for a, b in zip(EXPECTED_K13_FOLDS, EXPECTED_K13_FOLDS[1:]):
        if b[1] != a[2] + 1:
            raise Exception(f"K13_FOLDS_NOT_CONTIGUOUS: {a} -> {b}")


def assert_no_per_fold_refit(config):
    scheme = config.get("k13_fold_scheme") or {}
    if scheme.get("per_fold_refit") is not False:
        raise Exception("K13_PER_FOLD_REFIT_MUST_BE_FALSE (validation-not-optimization invariant)")


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
    for sym, ex, fac in (("GOOGL", "2022-07-18", 20.0), ("AMZN", "2022-06-06", 20.0)):
        a = next((x for x in actions if x.get("symbol") == sym and x.get("date") == ex), None)
        if a is None or not (a.get("applied") and a.get("dr9_verified")):
            raise Exception(f"C5_{sym}_SPLIT_NOT_DOCUMENTED_OR_NOT_VERIFIED")


def assert_universe_locked(config):
    if list(config.get("universe") or []) != LOCKED_UNIVERSE:
        raise Exception(f"UNIVERSE_DRIFT: CONFIG['universe']={config.get('universe')!r} expected 24-name locked universe")


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
    _run("assert_rotation_exit", assert_rotation_exit)
    _run("assert_equal_weight_sizing", assert_equal_weight_sizing)
    _run("assert_long_only", assert_long_only)
    _run("assert_momentum_params_locked", assert_momentum_params_locked)
    _run("assert_weekly_cadence", assert_weekly_cadence)
    _run("assert_k13_fold_scheme_locked", assert_k13_fold_scheme_locked)
    _run("assert_no_per_fold_refit", assert_no_per_fold_refit)
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

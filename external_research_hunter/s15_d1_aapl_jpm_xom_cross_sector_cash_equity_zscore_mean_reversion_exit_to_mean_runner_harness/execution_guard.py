"""s15-d1-cross-sector execution guard.

C1-C8 attestation utilities. Used at Initialize (K8 sealed parent drift) and at safety_zero rollup
(C3). NO execution, NO order submission, NO data fetch. Includes the s15-specific exit/stop
first-principles guards (exit-to-mean + vol-scaled catastrophe stop, NOT a fixed 2N).
"""

# Sealed chain constants (s15-d1)
EXPECTED_TIER_SPEC_SEAL = "1a89df0f07c4360cb1969f02889cd6fa973b93e81b21f0b3e27c6adc3ff0903d"
EXPECTED_PLAN_LOCK_SEAL = "d1355589e0c43f9a19ae575fabb87458b7e86d33184de8b33f082cf3c9d383a3"
EXPECTED_P2_PHASE2_PLAN_SEAL = "6579f5cab302f5bf46c57184a196645755e1149941b614239cb8e9ad29488a40"

# Sealed predecessor / sibling references (READ-ONLY; informational)
PREDECESSOR_S14_D1_CROSS_SECTOR_P7_TERMINAL_COMMIT = "6485ea9"
SIBLING_ALL_TECH_DRAFT_COMMIT = "214bae0"
CROSS_SECTOR_DR9_RESULT_SEAL = "a8ff91263e64529d52ac8b974ec01d8517d4bc7187df124b9938323870078a9c"
FRAMEWORK_DR10_V2_COMMIT = "78cd22e"

LOCKED_UNIVERSE = ["AAPL", "JPM", "XOM"]


def assert_seal_inheritance(config):
    """K8 sealed parent drift check. Raises if any sealed-chain constant mismatches."""
    checks = (
        ("tier_spec_seal", EXPECTED_TIER_SPEC_SEAL),
        ("plan_lock_seal", EXPECTED_PLAN_LOCK_SEAL),
        ("p2_phase2_plan_seal", EXPECTED_P2_PHASE2_PLAN_SEAL),
    )
    for key, expected in checks:
        actual = config.get(key)
        if actual != expected:
            raise Exception(f"K8_SEALED_PARENT_DRIFT: CONFIG[{key!r}]={actual!r} expected {expected!r}")


def assert_no_forbidden_order_paths(config):
    """C1+C7 attestation."""
    if config.get("brokerage_model_name") != "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6":
        raise Exception("BROKERAGE_MODEL_FORBIDDEN: s15-d1 P3 BUILD authorizes only CSV-simulator at P6.")
    if config.get("permanent_live_block") is not True:
        raise Exception("PERMANENT_LIVE_BLOCK_NOT_SET: invariant violation")


def assert_rec1_equivalent_binding_preserved(config):
    """REC1-equivalent binding must be present and non-empty."""
    if not config.get("rec1_equivalent_binding"):
        raise Exception("REC1_EQUIVALENT_BINDING_NOT_SET: invariant violation")
    rec1 = config.get("rec1_equivalent_oos_k9_disclosure") or ""
    if "OOS K9 reachable" not in rec1:
        raise Exception("REC1_EQUIVALENT_OOS_K9_RISK_DISCLOSURE_MISSING_OR_DEMOTED")


def assert_locked_strategy_params(config):
    """SEAL+P1 strategy parameter inviolate check (z-score exit-to-mean DA register)."""
    expected = {
        "mechanic_family": "zscore_bollinger_mean_reversion_exit_to_mean",  # DA2
        "lookback_L": 20,  # DA6
        "entry_band_k_sigma": 2.0,  # DA8
        "exit_rule": "EXIT_TO_MEAN",  # DA9
        "catastrophe_stop_sigma_multiple": 3.5,  # DA10
        "catastrophe_stop_is_fixed_2N": False,  # DA10 invariant
        "time_stop_max_hold_bars": 10,  # DA11
        "sizing_method": "vol_normalized",  # DA12
        "risk_pct_per_trade": 0.005,  # DA3=B
        "max_positions_per_name": 1,  # DA18
        "max_total_positions": 3,  # DA18
        "pyramid_method": "NONE",  # DA18
        "start_cash_usd": 100000,  # DA4=B
        "warmup_days": 30,  # DA19
        "verdict_min_closed_trades": 100,  # K9
        "adjustment_convention": "split_only",  # DA15
        "data_vendor": "tiingo",  # DA16
    }
    for key, want in expected.items():
        got = config.get(key)
        if got != want:
            raise Exception(f"LOCKED_PARAM_DRIFT: CONFIG[{key!r}]={got!r} expected {want!r}")


def assert_exit_to_mean_rule(config):
    """DA9: exit rule MUST be EXIT_TO_MEAN (NOT an oscillator-threshold exit — the s14-d1 failed design)."""
    if config.get("exit_rule") != "EXIT_TO_MEAN":
        raise Exception(f"EXIT_RULE_DRIFT: CONFIG['exit_rule']={config.get('exit_rule')!r} expected 'EXIT_TO_MEAN'")


def assert_catastrophe_stop_vol_scaled_not_2N(config):
    """DA10: stop MUST be the vol-scaled catastrophe brake, NOT a fixed 2N ATR (the s14-d1 failed design)."""
    if config.get("catastrophe_stop_is_fixed_2N") is not False:
        raise Exception("STOP_DESIGN_DRIFT: catastrophe_stop_is_fixed_2N must be False (no fixed-2N stop)")
    if config.get("stop_method") != "vol_scaled_catastrophe_sigma":
        raise Exception(f"STOP_METHOD_DRIFT: CONFIG['stop_method']={config.get('stop_method')!r} expected 'vol_scaled_catastrophe_sigma'")
    mult = config.get("catastrophe_stop_sigma_multiple")
    if not isinstance(mult, (int, float)) or mult <= config.get("entry_band_k_sigma", 0):
        raise Exception(f"CATASTROPHE_STOP_NOT_WIDER_THAN_ENTRY_BAND: sigma_multiple={mult!r} must exceed entry_band_k_sigma")


def assert_boundary_alignment(config):
    """C4 boundary alignment: eod_cancel_time MUST equal rth_safe_window_close."""
    if config.get("eod_cancel_time") != config.get("rth_safe_window_close"):
        raise Exception("C4_BOUNDARY_MISALIGNED")


def assert_split_only_convention(config):
    """C5 cash-equity split_only attestation (DA15)."""
    if config.get("asset_class") != "cash_equity":
        raise Exception("C5_ASSET_CLASS_NOT_CASH_EQUITY")
    if config.get("adjustment_convention") != "split_only":
        raise Exception("C5_ADJUSTMENT_CONVENTION_NOT_SPLIT_ONLY")
    if config.get("dividends_adjusted") is not False:
        raise Exception("C5_DIVIDENDS_MUST_NOT_BE_ADJUSTED_UNDER_SPLIT_ONLY")
    actions = config.get("known_corporate_actions") or []
    aapl_split = next((a for a in actions if a.get("symbol") == "AAPL" and a.get("type") == "split"), None)
    if aapl_split is None:
        raise Exception("C5_AAPL_SPLIT_NOT_DOCUMENTED")
    if not (aapl_split.get("applied") and aapl_split.get("dr9_verified")):
        raise Exception("C5_AAPL_SPLIT_NOT_APPLIED_OR_NOT_DR9_VERIFIED")


def assert_universe_locked(config):
    """DA17 universe lock: exactly {AAPL, JPM, XOM} in order; no widening/substitution."""
    if list(config.get("universe") or []) != LOCKED_UNIVERSE:
        raise Exception(f"UNIVERSE_DRIFT: CONFIG['universe']={config.get('universe')!r} expected {LOCKED_UNIVERSE!r}")


def assert_no_leverage_cap(config):
    """K11 NOT_APPLICABLE / DR11 not-in-chain attestation (unlevered cash equity)."""
    cap = config.get("leverage_cap") or ""
    if "unlevered_cash_equity" not in cap:
        raise Exception("K11_LEVERAGE_CAP_UNEXPECTEDLY_SET_FOR_CASH_EQUITY")


def full_guard_check(config, safety_counters=None):
    """Full guard rollup."""
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
    _run("assert_exit_to_mean_rule", assert_exit_to_mean_rule)
    _run("assert_catastrophe_stop_vol_scaled_not_2N", assert_catastrophe_stop_vol_scaled_not_2N)
    _run("assert_boundary_alignment", assert_boundary_alignment)
    _run("assert_split_only_convention", assert_split_only_convention)
    _run("assert_universe_locked", assert_universe_locked)
    _run("assert_no_leverage_cap", assert_no_leverage_cap)

    if safety_counters is not None:
        stale = safety_counters.get("stale_fill_warning_count", 0)
        all_zero = stale == 0
        results["checks"]["safety_counters_all_zero"] = all_zero
        if not all_zero:
            results["errors"].append(f"safety_counters_all_zero: stale_fill_warning_count={stale}")

    results["overall_pass"] = all(results["checks"].values()) and not results["errors"]
    return results

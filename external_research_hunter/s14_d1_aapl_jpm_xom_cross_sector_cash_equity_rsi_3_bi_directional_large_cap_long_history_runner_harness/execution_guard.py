"""s14-d1-cross-sector execution guard.

Implements per-Phase-2 C1-C8 attestation utilities. Used at Initialize (K8 sealed parent drift)
and at safety_zero rollup (C3). NO execution, NO order submission, NO data fetch.
"""

# Sealed chain constants (s14-d1-cross-sector)
EXPECTED_TIER_SPEC_SEAL = "862c00a5ffcc470580b6defe9c31ce89c4a43114ad418b4b6b4dfb991500569c"
EXPECTED_PLAN_LOCK_SEAL = "fa6c2c52fb0befd5ec2345d3d74f4fd4ad4577ec4f4857193c288171692bcd00"
EXPECTED_P2_PHASE2_PLAN_SEAL = "89717a4a60ff6b704c5922683d0a46e34e59e4032a5d38eba8b1bf841f819d67"

# Sealed predecessor / sibling references (READ-ONLY; informational)
SIBLING_ALL_TECH_DRAFT_COMMIT = "214bae0"
SIBLING_MULTI_INSTRUMENT_PLAN_COMMIT = "5376de7"
PREDECESSOR_PARK_REF_S12_D1 = "ecbd001"
PREDECESSOR_TERMINAL_S13_D1_SEAL = "2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775"
FRAMEWORK_DR10_V2_COMMIT = "78cd22e"
CROSS_SECTOR_DR9_RESULT_SEAL = "a8ff91263e64529d52ac8b974ec01d8517d4bc7187df124b9938323870078a9c"

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
            raise Exception(
                f"K8_SEALED_PARENT_DRIFT: CONFIG[{key!r}]={actual!r} expected {expected!r}"
            )


def assert_no_forbidden_order_paths(config):
    """C1+C7 attestation."""
    if config.get("brokerage_model_name") != "NOT_APPLICABLE_CSV_SIMULATOR_AT_P6":
        raise Exception(
            "BROKERAGE_MODEL_FORBIDDEN: s14-d1-cross-sector P3 BUILD authorizes only CSV-simulator at P6."
        )
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
    """SEAL+P1 strategy parameter inviolate check (DA register locked byte-equivalent)."""
    expected = {
        "rsi_period": 3,  # DA6
        "rsi_long_entry_threshold": 15,  # DA8
        "rsi_long_exit_threshold": 55,  # DA9
        "rsi_short_entry_threshold": 85,  # DA10
        "rsi_short_exit_threshold": 45,  # DA11
        "atr_period": 14,  # DA12
        "atr_method": "Wilder",
        "stop_multiplier_in_atr": 2.0,  # DA13
        "risk_pct_per_trade": 0.005,  # DA3=B
        "max_positions_per_name": 1,  # DA20
        "max_total_positions": 3,  # DA20
        "pyramid_method": "NONE",  # DA20
        "start_cash_usd": 100000,  # DA4=B
        "warmup_days": 30,  # DA16
        "verdict_min_closed_trades": 100,  # K9
        "adjustment_convention": "split_only",  # DA17
        "data_vendor": "tiingo",  # DA18
    }
    for key, want in expected.items():
        got = config.get(key)
        if got != want:
            raise Exception(
                f"LOCKED_PARAM_DRIFT: CONFIG[{key!r}]={got!r} expected {want!r}"
            )


def assert_boundary_alignment(config):
    """C4 boundary alignment: eod_cancel_time MUST equal rth_safe_window_close."""
    if config.get("eod_cancel_time") != config.get("rth_safe_window_close"):
        raise Exception("C4_BOUNDARY_MISALIGNED")


def assert_split_only_convention(config):
    """C5 cash-equity split_only attestation (DA17).

    Splits documented + applied (NOT structurally-absent like futures). AAPL 2020-08-31 4:1 must be
    present, applied, and DR9-verified; dividends must NOT be adjusted.
    """
    if config.get("asset_class") != "cash_equity":
        raise Exception("C5_ASSET_CLASS_NOT_CASH_EQUITY")
    if config.get("adjustment_convention") != "split_only":
        raise Exception("C5_ADJUSTMENT_CONVENTION_NOT_SPLIT_ONLY")
    if config.get("dividends_adjusted") is not False:
        raise Exception("C5_DIVIDENDS_MUST_NOT_BE_ADJUSTED_UNDER_SPLIT_ONLY")
    actions = config.get("known_corporate_actions") or []
    aapl_split = next(
        (a for a in actions if a.get("symbol") == "AAPL" and a.get("type") == "split"), None
    )
    if aapl_split is None:
        raise Exception("C5_AAPL_SPLIT_NOT_DOCUMENTED")
    if not (aapl_split.get("applied") and aapl_split.get("dr9_verified")):
        raise Exception("C5_AAPL_SPLIT_NOT_APPLIED_OR_NOT_DR9_VERIFIED")


def assert_universe_locked(config):
    """DA19 universe lock: exactly {AAPL, JPM, XOM} in order; no widening/substitution."""
    if list(config.get("universe") or []) != LOCKED_UNIVERSE:
        raise Exception(
            f"UNIVERSE_DRIFT: CONFIG['universe']={config.get('universe')!r} expected {LOCKED_UNIVERSE!r}"
        )


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

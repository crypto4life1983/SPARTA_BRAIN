"""s13-d1 execution guard.

Implements per-Phase-2 C1-C8 attestation utilities. Used at Initialize (K8 sealed parent drift)
and at safety_zero rollup (C3). NO execution, NO order submission, NO data fetch.
"""

# Sealed chain constants (s13-d1)
EXPECTED_TIER_SPEC_SEAL = "2f9d176388fe0b66c9ced19f33c68e079bb08112f3d52f3f20a9aba7d91bf775"
EXPECTED_PLAN_LOCK_SEAL = "1cac253cbbbf4cdab87e777edbe0bca00739e925de382bd1d687faae9731052c"
EXPECTED_P2_PHASE2_PLAN_SEAL = "b181ce834f5eacd2fb9f6766d6ce9404a86ecfe3d2787c7e4899d3e47ba57ec6"

# Sealed predecessor references (READ-ONLY; informational)
PREDECESSOR_PARK_REF_S12_D1 = "ecbd001"
PREDECESSOR_PARK_REF_S10_D1 = "1a9acec"
PREDECESSOR_PARK_REF_S10_D2 = "23c7164"
PREDECESSOR_SEAL_REF_S11_D1_V1 = "077e29e62f23dbc31823bad8447e5ef8d6f1a8c350d4f0c130c4f8f08be61a24"
PREDECESSOR_SEAL_REF_S11_D1_REV2 = "46659b4a8a73cb72fbe0153efed80aaf97b40557f8dfed51a9ba3199c243ed8d"


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
            "BROKERAGE_MODEL_FORBIDDEN: s13-d1 P3 BUILD authorizes only CSV-simulator at P6."
        )
    if config.get("permanent_live_block") is not True:
        raise Exception("PERMANENT_LIVE_BLOCK_NOT_SET: invariant violation")


def assert_rec1_equivalent_binding_preserved(config):
    """REC1-equivalent binding must be present and non-empty."""
    if not config.get("rec1_equivalent_binding"):
        raise Exception("REC1_EQUIVALENT_BINDING_NOT_SET: invariant violation")
    rec1 = config.get("rec1_equivalent_oos_k9_disclosure") or ""
    if "OOS K9 reachable at lower bound" not in rec1:
        raise Exception("REC1_EQUIVALENT_OOS_K9_RISK_DISCLOSURE_MISSING_OR_DEMOTED")


def assert_locked_strategy_params(config):
    """SEAL+P1 strategy parameter inviolate check (DA3=B + DA4=C + RSI thresholds locked)."""
    expected = {
        "rsi_period": 2,
        "rsi_long_entry_threshold": 10,
        "rsi_long_exit_threshold": 50,
        "rsi_short_entry_threshold": 90,
        "rsi_short_exit_threshold": 50,
        "atr_period": 20,
        "atr_method": "Wilder",
        "stop_multiplier_in_atr": 2.0,
        "risk_pct_per_trade": 0.005,  # DA3=B
        "max_units_per_market": 1,
        "max_total_units": 1,
        "pyramid_method": "NONE",
        "starting_cash_mnq_equivalent": 200000,  # DA4=C
        "tick_size_points": 0.25,
        "tick_value_usd": 0.5,
        "dollar_per_point": 2.0,
        "verdict_min_closed_trades": 100,
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


def assert_no_corporate_actions_for_futures(config):
    """C5 STRUCTURALLY_ABSENT attestation."""
    if config.get("asset_class") == "futures":
        actions = config.get("known_corporate_actions")
        if actions != []:
            raise Exception(
                "C5_FUTURES_STRUCTURALLY_ABSENT_VIOLATION: known_corporate_actions must be []"
            )


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
    _run("assert_no_corporate_actions_for_futures", assert_no_corporate_actions_for_futures)

    if safety_counters is not None:
        stale = safety_counters.get("stale_fill_warning_count", 0)
        all_zero = stale == 0
        results["checks"]["safety_counters_all_zero"] = all_zero
        if not all_zero:
            results["errors"].append(f"safety_counters_all_zero: stale_fill_warning_count={stale}")

    results["overall_pass"] = all(results["checks"].values()) and not results["errors"]
    return results

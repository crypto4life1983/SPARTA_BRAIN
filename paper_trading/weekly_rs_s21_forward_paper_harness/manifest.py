"""Locked s21 mechanic + universe + cost model + gate thresholds + governance status. Single source of truth for the harness."""

LOCKED_UNIVERSE_48 = ["AVGO", "QCOM", "TXN", "INTC", "MU", "AMAT", "IBM", "INTU", "NOW", "ADI", "VZ", "T", "CHTR", "EA", "SBUX", "TGT", "BKNG", "MAR", "GM", "TJX", "ROST", "MO", "CL", "KMB", "GIS", "STZ", "PFE", "BMY", "AMGN", "GILD", "CVS", "CI", "ISRG", "SYK", "C", "USB", "SCHW", "BLK", "SPGI", "CB", "BA", "ITW", "UPS", "RTX", "LMT", "DE", "PSX", "VLO"]

# Configurable LOCAL data sources (read-only). The harness NEVER fetches; the operator supplies these split_only CSVs.
# Each entry: dir (relative to repo root) + filename_suffix appended to the symbol. The sealed_baseline is READ-ONLY and
# MUST NOT be overwritten. The forward cycle defaults to the refreshed source.
DATA_SOURCES = {
    "sealed_baseline_20251230": {
        "dir": "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/raw",
        "filename_suffix": "_ohlcv_1d_20190102_20251230.csv",
        "last_date": "2025-12-30", "read_only": True,
        "note": "sealed DR9 set (commit d76c999); ends 2025-12-30; immutable baseline; NEVER overwrite",
    },
    "refreshed_20260528": {
        "dir": "data/s21_weekly_rs_paper_refresh/raw",
        "filename_suffix": "_ohlcv_1d_20190102_20260528.csv",
        "last_date": "2026-05-28", "read_only": False,
        "note": "refreshed full-history split_only set through 2026-05-28 (RUN_BOOK 115f4f2); BKNG 25:1 2026-04-06 documented; overlap reproduces sealed 47/48 (BKNG re-scaled)",
    },
}
DEFAULT_DATA_SOURCE = "refreshed_20260528"

MANIFEST = {
    "harness_id": "weekly_rs_s21_forward_paper_harness",
    "purpose": "broker-free SIMULATED forward paper test of the s21 weekly RS diagnostic edge (no broker, no live, no FRC)",
    "source_plan_commit": "3dd8b3c",
    "source_diagnostic": {
        "candidate_record_id": "s21-d1-broader-universe-weekly-relative-strength-rotation-48name-fresh-large-cap-long-history",
        "tier_n_spec_seal_commit": "ae11479", "p11_commit": "7e12e56", "dr9_result_commit": "d76c999",
    },
    "locked_mechanic": {
        "momentum_lookback_L": 126, "momentum_skip_S": 21, "top_m_held": 8, "rebalance_cadence_R_days": 5,
        "exit_rule": "ROTATION_RELATIVE_RANK", "exit_is_trailing_or_atr_stop": False, "sizing_method": "equal_weight",
        "per_position_weight_fraction": 1.0 / 8.0, "signal_direction": "long-only", "shorting_enabled": False,
        "leverage": "NONE", "pyramid_method": "NONE", "max_total_positions": 8, "start_cash_usd": 100000,
        "warmup_days": 160, "adjustment_convention": "split_only", "data_vendor_for_local_csv": "tiingo (split_only; operator-provided LOCAL CSVs only; NO fetch by this harness)",
    },
    "cost_model_S1": {"commission_per_share_usd": 0.005, "min_commission_per_trade_usd": 1.0, "slippage_proxy_bps": 1.0},
    "universe_48": LOCKED_UNIVERSE_48,
    "weekly_anchor_policy": "ONE fixed weekly session, locked before week 1 (e.g., Friday-close signal -> Monday-open fill, or same-close); never changed mid-test",
    "gate_thresholds": {
        "drawdown_warn": 0.15, "drawdown_review": 0.25, "drawdown_kill": 0.30, "k4_fail_safety": 0.50,
        "annualized_cost_drag_max": 0.05, "implementation_shortfall_max_bps": 25.0,
        "oos_k9_per_year_floor": 50, "gate_12wk_min_closed_trades": 15, "gate_24wk_min_closed_trades": 35,
    },
    "status": {
        "trading_status": "PAUSED", "live_status": "BLOCKED_AT_6_GATES", "frc_status": "NEVER_GRANTED",
        "research_label": "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE", "paper_state": "HARNESS_BUILT_NOT_YET_RUN",
        "s21_remains_diagnostic_only_until_paper_gates_pass": True,
    },
    "permanent_blocks": {
        "no_broker_connection": True, "no_live_trading": True, "no_paper_trading_via_broker": True,
        "no_frc_grant": True, "no_strategy_lab_promotion": True, "no_network_or_data_fetch_by_harness": True,
        "no_api_keys": True, "no_parameter_tuning": True, "no_universe_change": True, "no_cadence_tuning": True,
    },
}

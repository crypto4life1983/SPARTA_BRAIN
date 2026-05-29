def test_manifest_locks_s21_mechanic(harness):
    M = harness["manifest"].MANIFEST
    lm = M["locked_mechanic"]
    assert (lm["momentum_lookback_L"], lm["momentum_skip_S"], lm["top_m_held"], lm["rebalance_cadence_R_days"]) == (126, 21, 8, 5)
    assert lm["signal_direction"] == "long-only" and lm["exit_rule"] == "ROTATION_RELATIVE_RANK"
    assert lm["adjustment_convention"] == "split_only" and lm["start_cash_usd"] == 100000
    assert len(M["universe_48"]) == 48 and len(set(M["universe_48"])) == 48
    assert M["status"]["frc_status"] == "NEVER_GRANTED" and M["status"]["live_status"] == "BLOCKED_AT_6_GATES"
    assert all(M["permanent_blocks"].values())
    assert M["cost_model_S1"] == {"commission_per_share_usd": 0.005, "min_commission_per_trade_usd": 1.0, "slippage_proxy_bps": 1.0}

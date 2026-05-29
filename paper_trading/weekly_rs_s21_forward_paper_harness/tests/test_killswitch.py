def test_drawdown_thresholds(harness):
    ks = harness["killswitch"].check_killswitch
    assert ks({"current_drawdown": 0.10})["status"] == "GREEN"
    assert ks({"current_drawdown": 0.16})["status"] == "WARN"
    assert ks({"current_drawdown": 0.26})["status"] == "REVIEW"
    r = ks({"current_drawdown": 0.31}); assert r["status"] == "TRIGGERED" and r["halt"] is True


def test_cost_and_data_and_drift_triggers(harness):
    ks = harness["killswitch"].check_killswitch
    assert ks({"annualized_cost_drag": 0.06})["halt"] is True
    assert ks({"data_integrity_ok": False})["halt"] is True
    assert ks({"mechanic_drift": True})["halt"] is True
    assert ks({"manual_stop": True})["halt"] is True
    assert ks({"mean_shortfall_bps": 30.0})["halt"] is True


def test_edge_divergence_is_review_not_auto_halt(harness):
    ks = harness["killswitch"].check_killswitch
    r = ks({"trailing_expectancy": -5.0})
    assert r["status"] == "REVIEW" and r["halt"] is False

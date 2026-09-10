"""C22 cost engine: components match the frozen contract, 37 bps stays sensitivity-only, no
frozen base case exists, funding/borrow/slippage/fees are separate and signed correctly."""
from __future__ import annotations

import pytest

import sparta_commander.c22_replay_cost_engine_contract as C
import sparta_commander.c22_execution_data_short_instrument_feasibility_contract as X


def test_component_names_and_levels_are_the_frozen_contract_ones():
    assert C.COST_COMPONENTS == X.COST_COMPONENTS
    assert C.RESULT_LEVELS == X.COST_RESULT_LEVELS
    assert C.SENSITIVITY_37BPS_STATUS == X.THIRTY_SEVEN_BPS_STATUS == "SENSITIVITY_CASE_NOT_BASE_CASE"


def test_37bps_model_is_sensitivity_only_and_never_decisive():
    m = C.SENSITIVITY_37BPS_MODEL
    assert m["status"] == "SENSITIVITY_ONLY" and m["decisive"] is False and m["label"] == C.SENSITIVITY_37BPS_STATUS
    assert 2 * m["trading_fee_bps_per_side"] + m["entry_slippage_bps"] + m["exit_slippage_bps"] == 37.0
    assert C.validate_model(m)["valid"]
    bad = dict(m, decisive=True)
    assert "non_frozen_model_cannot_be_decisive" in C.validate_model(bad)["failures"]


def test_no_frozen_base_case_exists():
    f = C.frozen_base_case()
    assert f["status"] == "C22_COST_BASE_CASE_NOT_FROZEN" and f["model"] is None and f["decisive"] is False


def test_zero_model_produces_zero_everywhere():
    b = C.cost_breakdown("LONG", 1000.0, 1100.0, C.ZERO_COST_MODEL)
    assert all(v == 0.0 for v in b["components"].values())
    assert b["cost_at_level"] == {"gross": 0.0, "transaction_cost_only_net": 0.0, "fully_net_after_funding_or_borrow": 0.0}


def test_fees_and_slippage_separate_under_37bps():
    b = C.cost_breakdown("LONG", 10000.0, 10000.0, C.SENSITIVITY_37BPS_MODEL)
    c = b["components"]
    assert c["entry_exchange_fee"] == pytest.approx(13.5) and c["exit_exchange_fee"] == pytest.approx(13.5)
    assert c["entry_slippage"] == pytest.approx(5.0) and c["exit_slippage"] == pytest.approx(5.0)
    assert b["cost_at_level"]["transaction_cost_only_net"] == pytest.approx(37.0)
    assert b["cost_at_level"]["fully_net_after_funding_or_borrow"] == pytest.approx(37.0)
    assert tuple(c.keys()) == tuple(X.COST_COMPONENTS)


def test_funding_sign_short_receives_when_rate_positive_and_borrow_is_always_cost():
    assert C.funding_cost("LONG", 10000.0, [("a", 0.0001), ("b", 0.0001)]) == pytest.approx(2.0)
    assert C.funding_cost("SHORT", 10000.0, [("a", 0.0001), ("b", 0.0001)]) == pytest.approx(-2.0)
    assert C.funding_cost("SHORT", 10000.0, []) == 0.0
    assert C.borrow_cost(10000.0, [("d1", 0.0002), ("d2", 0.0002)]) == pytest.approx(4.0)
    b = C.cost_breakdown("SHORT", 10000.0, 9000.0, C.SENSITIVITY_37BPS_MODEL,
                         funding_rates=[("a", 0.0001)], borrow_rates=[("d1", 0.0002)])
    assert b["components"]["funding_or_borrow_cost"] == pytest.approx(-1.0 + 2.0)
    assert b["cost_at_level"]["fully_net_after_funding_or_borrow"] > b["cost_at_level"]["transaction_cost_only_net"]


def test_slippage_direction_on_price():
    m = C.SENSITIVITY_37BPS_MODEL
    assert C.apply_slippage_to_price(100.0, "LONG", "entry", m) == pytest.approx(100.05)
    assert C.apply_slippage_to_price(100.0, "LONG", "exit", m) == pytest.approx(99.95)
    assert C.apply_slippage_to_price(100.0, "SHORT", "entry", m) == pytest.approx(99.95)
    assert C.apply_slippage_to_price(100.0, "SHORT", "exit", m) == pytest.approx(100.05)
    with pytest.raises(ValueError):
        C.slippage_cost(1.0, m, "middle")

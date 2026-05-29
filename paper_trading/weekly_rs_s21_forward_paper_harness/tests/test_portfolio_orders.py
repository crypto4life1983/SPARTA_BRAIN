import pytest


def test_equal_weight_targets(harness):
    pf = harness["portfolio"]
    t = pf.equal_weight_targets(list("ABCDEFGH"), 100000.0, 8)
    assert all(v == pytest.approx(12500.0) for v in t.values()) and sum(t.values()) == pytest.approx(100000.0)


def test_rotation(harness):
    pf = harness["portfolio"]
    assert pf.rotation_exits(list("ABCDEFGH"), list("ABCDEFGI")) == ["H"]
    assert pf.rotation_entries(list("ABCDEFGH"), list("ABCDEFGI")) == ["I"]


def test_cost_model_s1(harness):
    pf = harness["portfolio"]
    assert pf.commission_cost(10, 0.005, 1.0) == pytest.approx(1.0)
    assert pf.commission_cost(1000, 0.005, 1.0) == pytest.approx(5.0)
    assert pf.slippage_cost(100, 50.0, 1.0) == pytest.approx(0.5)


def test_build_paper_orders_enter_exit(harness):
    pf = harness["portfolio"]
    holdings = {"H": {"shares": 10.0}}
    prices = {s: 100.0 for s in list("ABCDEFGHI")}
    selected = list("ABCDEFGI")  # H rotates out, I enters
    orders = pf.build_paper_orders(holdings, selected, prices, 100000.0, m=8)
    acts = {o["symbol"]: o["action"] for o in orders}
    assert acts["H"] == "EXIT" and acts["I"] == "ENTER"
    assert any(o["action"] == "ENTER" for o in orders)
    # long-only: entries buy (negative cashflow), exit sells (positive minus cost)
    enter = next(o for o in orders if o["symbol"] == "I")
    assert enter["shares"] > 0 and enter["cashflow_usd"] < 0


def test_build_orders_refuses_bad_price(harness):
    pf = harness["portfolio"]
    with pytest.raises(ValueError):
        pf.build_paper_orders({}, ["A"], {"A": 0.0}, 100000.0, m=8)

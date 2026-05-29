import pytest


def test_append_only_orders_and_trades(harness, tmp_path):
    log = harness["paper_logging"]
    op = tmp_path / "paper_orders.jsonl"; tp = tmp_path / "paper_trades_closed.jsonl"
    log.append_order_record(str(op), {"week": 1, "x": 1})
    log.append_order_record(str(op), {"week": 2, "x": 2})
    log.append_closed_trade(str(tp), {"symbol": "AVGO", "net_pnl_usd": 10.0})
    assert len(log.read_all(op)) == 2 and log.read_all(op)[0]["week"] == 1 and log.read_all(op)[1]["week"] == 2
    assert len(log.read_all(tp)) == 1


def test_append_only_mode_guard(harness):
    log = harness["paper_logging"]
    assert log.assert_append_only("a") is True
    for bad in ("w", "w+", "r+", "wb"):
        with pytest.raises(log.AppendOnlyViolation):
            log.assert_append_only(bad)

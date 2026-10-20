"""tools/replay_portfolio_rules.py book model, on synthetic signals (no real data)."""
import sys

import pytest

sys.path.insert(0, r"C:\SPARTA_BRAIN")
from tools.replay_portfolio_rules import simulate  # noqa: E402


def _t(date, exit_date, R, direction="long", sym="A", strat="D"):
    return dict(sym=sym, strat=strat, direction=direction, date=date, exit_date=exit_date, R=R)


def test_same_direction_cap_skips_only_same_side_while_positions_are_open():
    trades = [
        _t("2026-01-01", "2026-01-10", 1.0, "long", "A"),
        _t("2026-01-02", "2026-01-10", 1.0, "long", "B"),      # cap 1 full -> skipped
        _t("2026-01-02", "2026-01-10", -1.0, "short", "C"),    # other side -> taken
        _t("2026-01-10", "2026-01-15", 1.0, "long", "D"),      # A exits 01-10 inclusive -> still open -> skipped
        _t("2026-01-11", "2026-01-15", 1.0, "long", "E"),      # A rolled off -> taken
    ]
    recs = simulate(trades, dict(kind="same_dir_cap", N=1))
    assert [r["taken"] for r in recs] == [True, False, True, False, True]
    assert recs[1]["booked_R"] is None and recs[4]["booked_R"] == 1.0


def test_total_cap_counts_both_sides():
    trades = [
        _t("2026-01-01", "2026-01-05", 1.0, "long", "A"),
        _t("2026-01-01", "2026-01-05", 1.0, "short", "B"),
        _t("2026-01-02", "2026-01-05", 1.0, "long", "C"),      # 2 open, cap 2 -> skipped
        _t("2026-01-06", "2026-01-08", 1.0, "long", "D"),      # both exited -> taken
    ]
    recs = simulate(trades, dict(kind="total_cap", N=2))
    assert [r["taken"] for r in recs] == [True, True, False, True]


def test_rolling_filter_uses_only_trades_closed_strictly_before_the_signal_day():
    # three losers closing on 01-05; a signal on 01-05 must not see them, a signal on 01-06 must
    losers = [_t(f"2026-01-0{i}", "2026-01-05", -1.0, sym=f"L{i}") for i in (1, 2, 3)]
    same_day = _t("2026-01-05", "2026-01-09", 1.0, sym="S")
    next_day = _t("2026-01-06", "2026-01-09", 1.0, sym="N")
    for source in ("pool", "book"):
        recs = simulate(losers + [same_day, next_day], dict(kind="rolling", mode="skip", window=3, source=source))
        assert recs[3]["taken"] is True          # window not yet closed on the signal day
        assert recs[4]["taken"] is False         # mean of the last 3 closed = -1 < 0 -> skipped


def test_pool_source_refreshes_the_window_from_skipped_signals_but_book_source_locks():
    losers = [_t(f"2026-01-0{i}", "2026-01-05", -1.0, sym=f"L{i}") for i in (1, 2, 3)]
    # three winners the filter skips (window negative), closing 01-12; then a signal on 01-13
    skipped_winners = [_t(f"2026-01-0{i}", "2026-01-12", 2.0, sym=f"W{i}") for i in (6, 7, 8)]
    later = _t("2026-01-13", "2026-01-20", 1.0, sym="X")
    pool = simulate(losers + skipped_winners + [later], dict(kind="rolling", mode="skip", window=3, source="pool"))
    book = simulate(losers + skipped_winners + [later], dict(kind="rolling", mode="skip", window=3, source="book"))
    assert [r["taken"] for r in pool[3:6]] == [False, False, False]
    assert pool[6]["taken"] is True          # pool window now = the three skipped winners -> mean 2 -> trade again
    assert book[6]["taken"] is False         # book never closed anything new -> window stays negative -> locked


def test_rolling_half_books_half_size_and_keeps_full_size_in_the_window():
    losers = [_t(f"2026-01-0{i}", "2026-01-05", -1.0, sym=f"L{i}") for i in (1, 2, 3)]
    winner = _t("2026-01-06", "2026-01-07", 2.0, sym="W")
    later = _t("2026-01-08", "2026-01-09", 1.0, sym="X")
    recs = simulate(losers + [winner, later], dict(kind="rolling", mode="half", window=3))
    assert recs[3]["taken"] is True and recs[3]["booked_R"] == pytest.approx(1.0)
    assert recs[3]["full_R"] == 2.0
    # window for the last signal = last 3 closed by exit date: L2, L3, W (full 2.0) -> mean 0 -> not < 0
    assert recs[4]["booked_R"] == pytest.approx(1.0)

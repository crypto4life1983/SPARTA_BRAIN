"""tools/trade_exit_pairs.py: paired exits on identical entries."""
import sys

sys.path.insert(0, r"C:\SPARTA_BRAIN")
from tools import trade_exit_pairs as ep  # noqa: E402


def _t(i, strategy, r, symbol="BTCUSDT", open_date="2026-09-20", direction="long", exchange="binance"):
    return dict(id=i, exchange=exchange, symbol=symbol, strategy=strategy, direction=direction,
                open_date=open_date, close_date="2026-10-01", pnl_r=r)


def test_groups_closed_rows_by_entry_and_keeps_first_row_per_strategy():
    trades = [_t(1, "D", 0.5), _t(2, "F", 1.2), _t(3, "F2", -1.0), _t(4, "D", 9.9),
              _t(5, "D", 0.1, open_date="2026-09-21"), dict(_t(6, "F", 0.3), close_date=None)]
    g = ep.group_entries(trades)
    assert g[("binance", "BTCUSDT", "2026-09-20", "long")] == {"D": 0.5, "F": 1.2, "F2": -1.0}
    assert g[("binance", "BTCUSDT", "2026-09-21", "long")] == {"D": 0.1}
    assert all("F" not in v or k[2] != "2026-09-21" for k, v in g.items())


def test_pair_stats_delta_sign_and_windows():
    trades = [_t(1, "D", 0.5), _t(2, "F", 1.2),                                   # post-fix: F - D = +0.7
              _t(3, "D", 1.0, open_date="2026-08-01"), _t(4, "F", 0.0, open_date="2026-08-01")]  # retired: -1.0
    g = ep.group_entries(trades)
    allw = ep.pair_stats(g, "F", "D")
    assert allw["n"] == 2 and abs(allw["mean_delta_R"] - (-0.15)) < 1e-9
    post = ep.pair_stats(g, "F", "D", since="2026-09-15")
    assert post["n"] == 1 and post["mean_delta_R"] == 0.7 and post["a_wins"] == 1
    ret = ep.pair_stats(g, "F", "D", before="2026-09-15")
    assert ret["n"] == 1 and ret["mean_delta_R"] == -1.0
    assert ep.pair_stats(g, "F2", "D")["n"] == 0


def test_best_of_bias_measures_the_dedup_convention():
    trades = [_t(1, "D", -1.0), _t(2, "F", 0.4), _t(3, "F2", -1.0)]
    b = ep.best_of_bias(ep.group_entries(trades))
    assert b["n_entries"] == 1 and b["best_of_mean_R"] == 0.4
    assert abs(b["all_rows_mean_R"] - (-0.533)) < 1e-3


def test_render_has_banner_and_no_forbidden_words():
    trades = [_t(1, "D", 0.5), _t(2, "F", 1.2)]
    md = ep.render(ep.build(trades, "2026-10-20"))
    assert ep.BANNER in md and "F-D" in md
    assert ep.forbidden_words_found(md) == []

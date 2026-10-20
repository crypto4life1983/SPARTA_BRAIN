"""tools/replay_bot_rules.py: the replay's exit simulators must book the same R as the
paper bot's own manage_de / manage_f on identical bars. This is the check that makes the
2026-10-20 replay numbers mean something; it runs against the bot's real code and is
skipped when the bot repo is not on this machine."""
import importlib
import random
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

BOT = Path(r"C:\Users\mahmo\obsidian-trade-logger")
pytestmark = pytest.mark.skipif(not (BOT / "scripts" / "trade_bot.py").exists(), reason="bot repo absent")


@pytest.fixture(scope="module")
def mods():
    import logging
    logging.disable(logging.CRITICAL)
    sys.path.insert(0, str(BOT))
    sys.path.insert(0, r"C:\SPARTA_BRAIN")
    rep = importlib.import_module("tools.replay_bot_rules")
    db = importlib.import_module("scripts.db")
    tb = importlib.import_module("scripts.trade_bot")
    return rep, db, tb


def _bot_R(db, tb, tmp_path, sig, bars, strategy, timeout, tag):
    """Feed bars[1:] to the bot's exit engine day by day; return (R, outcome)."""
    conn = db.init_db(tmp_path / f"{tag}.db")
    db.insert_trade(conn, dict(exchange="binance", symbol="TST", strategy=strategy,
                               direction=sig["direction"], entry=sig["entry"], sl=sig["sl"],
                               tp1=sig["tp1"], tp2=sig.get("tp2"), tp3=sig.get("tp3"),
                               atr14=sig["atr14"], size_usd=100000.0, open_date="2026-01-01"))
    d0 = date(2026, 1, 1)
    manage = tb.manage_f if strategy in ("F", "F2") else tb.manage_de
    for j in range(1, len(bars)):
        t = db.get_open_trade(conn, "binance", strategy)
        o, h, l, c = bars[j]
        ev = manage(conn, t, c, (d0 + timedelta(days=j)).isoformat(), timeout,
                    bar_open=o, bar_high=h, bar_low=l)
        if ev and ev.get("outcome"):
            return ev["pnl_r"], ev["outcome"]
    return None, "OPEN"


def _random_case(rng, strategy):
    direction = rng.choice(["long", "short"])
    entry = 100.0
    atr = rng.uniform(1.0, 4.0)
    sd = 2 * atr
    sl = entry - sd if direction == "long" else entry + sd
    if strategy in ("F", "F2"):
        ks = (1.618, 2.618, 4.236)
    else:
        ks = (3.0 if strategy == "D" else 5.0, None, None)
    tps = [None if k is None else (entry + k * sd if direction == "long" else entry - k * sd) for k in ks]
    sig = dict(direction=direction, entry=entry, sl=sl, tp1=tps[0], tp2=tps[1], tp3=tps[2], atr14=atr)
    bars = [(entry, entry, entry, entry)]
    px = entry
    for _ in range(45):
        o = px * (1 + rng.gauss(0, 0.004))
        c = o * (1 + rng.gauss(0, 0.02))
        h = max(o, c) * (1 + abs(rng.gauss(0, 0.01)))
        l = min(o, c) * (1 - abs(rng.gauss(0, 0.01)))
        bars.append((o, h, l, c))
        px = c
    return sig, bars


@pytest.mark.parametrize("strategy", ["D", "E", "F"])
def test_simulators_match_the_bot_exit_engines(mods, tmp_path, strategy):
    rep, db, tb = mods
    rng = random.Random(20261020 + len(strategy))
    compared = 0
    for k in range(60):
        sig, bars = _random_case(rng, strategy)
        for timeout in (20, 40):
            sim = rep.sim_f(bars, 0, sig, timeout) if strategy == "F" else rep.sim_de(bars, 0, sig, timeout)
            bot_r, bot_out = _bot_R(db, tb, tmp_path, sig, bars, strategy, timeout, f"{strategy}{k}{timeout}")
            if sim is None:
                assert bot_out == "OPEN"
                continue
            assert bot_out == sim["outcome"], (k, timeout, bot_out, sim)
            assert abs(bot_r - sim["R"]) < 2e-3, (k, timeout, bot_r, sim["R"])
            compared += 1
    assert compared >= 80


def test_f_rung_variant_only_moves_the_first_rung(mods):
    rep, _, _ = mods
    sig = dict(direction="long", entry=100.0, sl=96.0, tp1=106.472, tp2=110.472, tp3=116.944, atr14=2.0)
    # runs to +1.2R, never reaches 1.618R, then drifts back to just above entry and times out:
    # the 1R rung banks 40% at +1R, the 1.618R ladder banks nothing and times out near flat
    bars = [(100, 100, 100, 100), (100.5, 104.8, 100.2, 104.6)] + [(100.3, 100.4, 100.1, 100.2)] * 20
    base = rep.sim_f(bars, 0, sig, 20)
    one_r = rep.sim_f(bars, 0, sig, 20, rungs=(1.0, 2.618, 4.236))
    assert base["outcome"] == "TIMEOUT" and one_r["outcome"] == "TIMEOUT"
    assert abs(base["R"]) < 0.1 and 0.35 < one_r["R"] < 0.5
    # and when price holds above 1R to the timeout, the 1R rung gives part of the move back
    hold = [(100, 100, 100, 100), (100.5, 104.8, 100.2, 104.6)] + [(104.6, 104.7, 104.5, 104.6)] * 20
    assert rep.sim_f(hold, 0, sig, 20, rungs=(1.0, 2.618, 4.236))["R"] < rep.sim_f(hold, 0, sig, 20)["R"]

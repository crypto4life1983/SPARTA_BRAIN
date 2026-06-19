"""C18 H4 market-structure trend-following FEE-HONEST replay one-off runner
(READ-ONLY against the SHA-frozen local BTCUSDT 4h data + the FROZEN C18 labels;
RESEARCH ONLY; NO data fetch; NO relabel; NO re-detection with new params; NO
optimization / re-parameterization / parameter sweep; NO XAUUSD; NO trading / broker /
credentials / orders; NO paper/live readiness claim).

Replays ONLY the FROZEN C18 detector output (reusing the committed detector's pure
run_detector with the FROZEN params -- this is NOT re-parameterization) over the
SHA-pinned BTCUSDT 4h candles, and CROSS-CHECKS it against the SHA-pinned frozen
labels artifact (same setup count + entry bars). It then builds a per-bar,
mark-to-market EQUITY CURVE: a long position sized at 1/3 of equity per unit (so a
full 3-unit pyramid = 100% gross, NO leverage), held only during a trade, in cash
between trades. The reserved 37 bps all-in cost is APPLIED as 18.5 bps one-way on each
unit's entry leg and exit leg -- not droppable.

It computes risk-adjusted metrics (net return, CAGR, Sharpe, Calmar, max drawdown,
win rate, total/avg R, cost drag / turnover) for the strategy and for a matched BTC
buy-and-hold over the same window, full-window and on the 2026 forward-OOS sub-window.
The decisive RISK-ADJUSTED gates (beat buy-and-hold on Sharpe and/or Calmar with no
worse drawdown, and a holding forward-OOS edge) are evaluated; the verdict is recorded
for human review. NO parameter is fitted or changed.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.h4_trend_following_market_structure_v1_detector_spec_dry_run_contract as det  # noqa: E402,E501

CANDIDATE_ID = "C18"
CANDIDATE_FAMILY = "h4_trend_following_market_structure"
SYMBOL = "BTCUSD"
TIMEFRAME = "4h"

FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS  # 37.0
ONE_WAY_COST = (ALL_IN_ROUND_TRIP_BPS / 2.0) / 10000.0               # 18.5 bps
UNIT_FRACTION = 1.0 / det.MAX_UNITS          # 1/3 of equity per unit; max gross 1.0

ANNUALIZATION_BARS = 365 * 6                 # H4 -> 6 bars/day
_ANN = ANNUALIZATION_BARS ** 0.5
FORWARD_OOS_START = "2026-01-01"

HEAD_AT_LABELS_REVIEW = "0e1377284ea865ac33a7988c61b5da7dc2417230"

C18_DIR = REPO_ROOT / "data" / "h4_trend_following_market_structure_c18"
SOURCE_CSV = C18_DIR / "raw" / "BTCUSDT_4h.csv"
LABELS_PATH = C18_DIR / "labels" / "c18_h4_labels.json"
EXPECTED_SOURCE_SHA256 = (
    "aec42241f47192ae29331f4b67a64500ca38aad1f403f13d0de5b405f7ecbaec")
EXPECTED_LABELS_SHA256 = (
    "907705d9506b1db79141118618b627248753cecab383d30564fbf5b7d8bc9e11")

OUT_DIR = C18_DIR / "replay_results"
LEDGER_PATH = OUT_DIR / "c18_h4_replay_ledger.json"
SUMMARY_PATH = OUT_DIR / "c18_h4_replay_summary.json"


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_candles(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append({"date": r["date"], "high": float(r["high"]),
                        "low": float(r["low"]), "close": float(r["close"])})
    out.sort(key=lambda c: c["date"])
    return out


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs):
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return (sum((v - m) ** 2 for v in xs) / (len(xs) - 1)) ** 0.5


def _max_drawdown(equity):
    peak, mdd = (equity[0] if equity else 1.0), 0.0
    for v in equity:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1.0)
    return mdd


def _metrics(daily_rets):
    if not daily_rets:
        return {"n_bars": 0, "net_return": 0.0, "cagr": 0.0, "ann_vol": 0.0,
                "sharpe": 0.0, "max_drawdown": 0.0, "calmar": 0.0}
    eq = [1.0]
    for r in daily_rets:
        eq.append(eq[-1] * (1.0 + r))
    n = len(daily_rets)
    net = eq[-1] - 1.0
    cagr = (eq[-1] ** (ANNUALIZATION_BARS / n)) - 1.0 if n > 0 else 0.0
    vol = _std(daily_rets) * _ANN
    sharpe = (_mean(daily_rets) / _std(daily_rets) * _ANN) if _std(daily_rets) > 0 \
        else 0.0
    mdd = _max_drawdown(eq)
    calmar = (cagr / abs(mdd)) if mdd < 0 else 0.0
    return {"n_bars": n, "net_return": round(net, 6), "cagr": round(cagr, 6),
            "ann_vol": round(vol, 6), "sharpe": round(sharpe, 6),
            "max_drawdown": round(mdd, 6), "calmar": round(calmar, 6)}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sha_src = compute_sha256(SOURCE_CSV)
    if sha_src != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("source_sha_pin_does_not_match_before_replay")
    sha_labels = compute_sha256(LABELS_PATH)
    if sha_labels != EXPECTED_LABELS_SHA256:
        raise RuntimeError("labels_sha_pin_does_not_match_before_replay")

    candles = load_candles(SOURCE_CSV)
    closes = [c["close"] for c in candles]
    dates = [c["date"] for c in candles]
    n = len(candles)
    with open(LABELS_PATH, encoding="utf-8") as f:
        frozen_labels = json.load(f)["labels"]

    # re-run the FROZEN detector for full trade prices; cross-check vs frozen labels
    trades = det.run_detector(candles)["trades"]
    if len(trades) != len(frozen_labels):
        raise RuntimeError("replay_trades_do_not_match_frozen_labels_count")
    for tr, lab in zip(sorted(trades, key=lambda t: t["entry_bar"]),
                       sorted(frozen_labels, key=lambda l: l["setup_index"])):
        if tr["entry_bar"] != lab["setup_index"]:
            raise RuntimeError("replay_entry_bars_do_not_match_frozen_labels")

    # per-bar mark-to-market net-return series (strategy) + per-trade stats
    f = UNIT_FRACTION
    net_bar = [0.0] * n
    total_cost = 0.0
    per_trade = []
    for tr in trades:
        eb, xb = tr["entry_bar"], tr["exit_bar"]
        entries = tr["entries"]                      # [base, add1, add2...]
        add_bars = [a["bar"] for a in tr["adds"]]
        unit_bars = [eb] + add_bars                  # bar each unit was entered
        exit_price = tr["stop"] if tr["exit_reason"] == "stop" else closes[xb]
        # entry-leg costs (one-way per unit)
        for ub in unit_bars:
            net_bar[ub] -= f * ONE_WAY_COST
            total_cost += f * ONE_WAY_COST
        # exit-leg cost (one-way per unit, all units)
        net_bar[xb] -= len(unit_bars) * f * ONE_WAY_COST
        total_cost += len(unit_bars) * f * ONE_WAY_COST
        # held exposure per bar from entry+1..exit
        for b in range(eb + 1, xb + 1):
            units_b = 1 + sum(1 for ab in add_bars if ab < b)
            net_bar[b] += units_b * f * (closes[b] / closes[b - 1] - 1.0)
        # per-trade stats (base unit R + net pnl fraction on deployed capital)
        base_entry = entries[0]
        risk = base_entry - tr["stop"]
        r_mult = ((exit_price - base_entry) / risk) if risk > 0 else 0.0
        trade_net = (sum(f * (exit_price / e - 1.0) for e in entries)
                     - len(entries) * f * ONE_WAY_COST * 2.0)
        per_trade.append({"entry_bar": eb, "exit_bar": xb, "units": tr["units"],
                          "exit_reason": tr["exit_reason"], "r_multiple": round(r_mult, 4),
                          "trade_net_fraction": round(trade_net, 6),
                          "in_forward_oos": dates[eb] >= FORWARD_OOS_START})

    # strategy metric series (skip the first bar -> returns start at index 1)
    strat_rets = net_bar[1:]
    fwd_idx = [i for i in range(1, n) if dates[i] >= FORWARD_OOS_START]
    strat_fwd = [net_bar[i] for i in fwd_idx]

    # matched BTC buy-and-hold (long 100%, one entry-leg cost), same windows
    bh_rets = [closes[i] / closes[i - 1] - 1.0 for i in range(1, n)]
    if bh_rets:
        bh_rets = list(bh_rets)
        bh_rets[0] -= ONE_WAY_COST
    bh_fwd = [closes[i] / closes[i - 1] - 1.0 for i in fwd_idx]

    strat = _metrics(strat_rets)
    strat_oos = _metrics(strat_fwd)
    bh = _metrics(bh_rets)
    bh_oos = _metrics(bh_fwd)

    wins = sum(1 for t in per_trade if t["trade_net_fraction"] > 0)
    win_rate = round(wins / len(per_trade), 6) if per_trade else 0.0
    total_R = round(sum(t["r_multiple"] for t in per_trade), 4)
    avg_R = round(total_R / len(per_trade), 4) if per_trade else 0.0
    fwd_trades = [t for t in per_trade if t["in_forward_oos"]]
    fwd_win_rate = round(
        sum(1 for t in fwd_trades if t["trade_net_fraction"] > 0)
        / len(fwd_trades), 6) if fwd_trades else 0.0

    no_worse_mdd = strat["max_drawdown"] >= bh["max_drawdown"]
    beats_bh = ((strat["sharpe"] > bh["sharpe"] or strat["calmar"] > bh["calmar"])
                and no_worse_mdd)
    fwd_edge = strat_oos["sharpe"] > bh_oos["sharpe"]
    cost_tolerable = round(total_cost, 6) < abs(strat["net_return"]) \
        if strat["net_return"] != 0 else True
    gates = {
        "beats_buy_and_hold_risk_adjusted": beats_bh,
        "max_drawdown_no_worse_than_buy_and_hold": no_worse_mdd,
        "forward_oos_risk_adjusted_edge_holds": fwd_edge,
        "turnover_cost_drag_tolerable": cost_tolerable,
    }
    all_pass = all(gates.values())

    sha_after = compute_sha256(SOURCE_CSV)
    if sha_after != sha_src:
        raise RuntimeError("inputs_mutated_during_replay")

    common = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbol": SYMBOL, "timeframe": TIMEFRAME,
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "source_sha256": sha_src, "labels_sha256": sha_labels,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "one_way_cost_bps": round(ONE_WAY_COST * 10000.0, 4),
        "unit_fraction_of_equity": round(UNIT_FRACTION, 6),
        "cost_convention": "37bps round trip = 18.5bps one-way per unit leg; max "
                           "gross 1.0 (3 units x 1/3), no leverage",
        "no_parameter_optimization": True, "no_reparameterization": True,
        "no_parameter_sweep": True,
        "window": [dates[0], dates[-1]], "n_bars": n,
        "trade_count": len(per_trade),
        "win_rate": win_rate, "total_R": total_R, "avg_R": avg_R,
        "forward_oos_trade_count": len(fwd_trades),
        "forward_oos_win_rate": fwd_win_rate,
        "total_cost_drag": round(total_cost, 6),
        "strategy_metrics": strat, "strategy_forward_oos_metrics": strat_oos,
        "buy_and_hold_metrics": bh, "buy_and_hold_forward_oos_metrics": bh_oos,
        "decisive_gate_results": gates, "all_decisive_gates_pass": all_pass,
        "scope_locks": {
            "no_data_fetch": True, "no_relabel": True, "no_redetect_new_params": True,
            "no_optimization": True, "no_reparameterization": True,
            "no_parameter_sweep": True, "no_xauusd": True, "no_paper_trading": True,
            "no_live_trading": True, "no_broker": True, "no_credentials": True,
            "no_order_logic": True, "no_data_mutation": True, "no_cost_drop": True,
            "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
            "no_downstream_gate_unlock": True, "no_staging": True,
            "no_commit": True, "no_push": True,
        },
        "honest_framing": (
            "fee-honest EQUITY-CURVE replay of the FROZEN C18 H4 setups; 37 bps "
            "all-in applied as 18.5 bps one-way per unit leg, not droppable; long "
            "1/3-per-unit sizing (max gross 1.0, no leverage); vs matched BTC "
            "buy-and-hold; the decisive gates require a RISK-ADJUSTED win (Sharpe "
            "and/or Calmar, no worse drawdown) AND a holding forward-OOS edge; raw "
            "return alone is not sufficient; not a profitability or paper/live claim"),
    }
    ledger = dict(common)
    ledger["artifact"] = "c18_h4_replay_ledger"
    ledger["trades"] = per_trade
    with open(LEDGER_PATH, "w", encoding="utf-8") as fp:
        json.dump(ledger, fp, indent=2, sort_keys=True)
    ledger_sha = compute_sha256(LEDGER_PATH)

    summary = dict(common)
    summary["artifact"] = "c18_h4_replay_summary"
    summary["ledger_path"] = str(LEDGER_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    summary["ledger_sha256"] = ledger_sha
    with open(SUMMARY_PATH, "w", encoding="utf-8") as fp:
        json.dump(summary, fp, indent=2, sort_keys=True)
    summary_sha = compute_sha256(SUMMARY_PATH)

    report = {
        "ledger_path": str(LEDGER_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "ledger_sha256": ledger_sha,
        "summary_path": str(SUMMARY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "summary_sha256": summary_sha,
        "window": [dates[0], dates[-1]], "trade_count": len(per_trade),
        "win_rate": win_rate, "total_R": total_R, "avg_R": avg_R,
        "total_cost_drag": round(total_cost, 6),
        "strategy_metrics": strat, "strategy_forward_oos_metrics": strat_oos,
        "buy_and_hold_metrics": bh, "buy_and_hold_forward_oos_metrics": bh_oos,
        "decisive_gate_results": gates, "all_decisive_gates_pass": all_pass,
        "source_sha_stable": sha_src == sha_after,
    }
    for k, v in report.items():
        print("%s = %r" % (k, v))
    return report


if __name__ == "__main__":
    main()

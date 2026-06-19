"""Candidate #20 FEE-HONEST replay one-off runner
(READ-ONLY against the 9 SHA-frozen PUBLIC BTC/ETH/SOL spot+perp+funding files + the
FROZEN C20 labels artifact; RESEARCH ONLY; NO data fetch; NO relabel; NO re-detection
with new params; NO optimization / re-parameterization / parameter sweep; NO XAUUSD; NO
trading / broker / credentials / orders; NO paper/live readiness claim).

Replays ONLY the FROZEN C20 labels (the committed real-candle entries, per asset) over
the SHA-pinned spot/perp/funding candles and builds a per-asset, daily mark-to-market
EQUITY CURVE for the mechanically-neutral position (long 0.5 spot / short 0.5 perp of the
SAME asset, gross 1.0, no leverage). It applies ALL replay frictions honestly and NOT
droppable:

  * TWO-LEG TRADING COST: the reserved 37 bps all-in round-trip, charged PER LEG, so a
    round-trip trade costs 2 x 37 bps = 74 bps (the spec's "counts double"); split as
    37 bps at entry and 37 bps at exit;
  * FUNDING paid/received: the short-perp leg receives the daily funding when positive,
    pays when negative (on its 0.5 notional);
  * BASIS-CONVERGENCE execution: both legs marked at the D1 close each held bar (the
    price PnL is the realized spot-vs-perp basis move);
  * (the spec defines no separate perp borrow / liquidation haircut beyond funding +
    the all-in cost; none is invented here).

It computes net-of-cost RISK-ADJUSTED metrics (net return, CAGR, Sharpe, Calmar, max
drawdown, win rate, avg trade return, funding-vs-basis contribution, cost drag) for the
strategy and for a RANDOM/NULL MARKET-NEUTRAL baseline (the always-on neutral carry =
zero timing skill) -- NOT buy-and-hold -- full-window and on the 2026 forward-OOS
sub-window, per asset and equal-weight portfolio. The decisive gates (net-positive after
cost, positive Sharpe, beats the null risk-adjusted, holding forward-OOS) are evaluated
and recorded for human review. NO parameter is fitted or changed.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_detector_spec_dry_run_contract as _d20  # noqa: E402,E501

CANDIDATE_ID = "C20"
CANDIDATE_FAMILY = "mechanically_neutral_spot_perp_basis_funding_carry"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
TIMEFRAME = "D1"

RAW_DIR = REPO_ROOT / "data" / "crypto_basis_funding_research" / "raw"
C20_DIR = REPO_ROOT / "data" / "mechanically_neutral_spot_perp_basis_funding_carry_c20"
LABELS_PATH = C20_DIR / "labels" / "c20_labels.json"
OUT_DIR = C20_DIR / "replay_results"
LEDGER_PATH = OUT_DIR / "c20_replay_ledger.json"
SUMMARY_PATH = OUT_DIR / "c20_replay_summary.json"

HEAD_AT_LABELS_REVIEW = "ead1bdb72ef5f9a78c1489f2a7701b5cd6e60c68"

# cost model -- the reserved 37 bps all-in round-trip, PER LEG (two legs -> doubled).
ALL_IN_ROUND_TRIP_BPS = _d20.ALL_IN_ROUND_TRIP_BPS          # 37.0
NUM_LEGS = 2                                                # spot + perp
LEG_NOTIONAL = 0.5                                          # gross 1.0 split two legs
# round-trip cost per trade = 2 legs x 37 bps = 74 bps; split half at entry, half exit.
ROUND_TRIP_COST = NUM_LEGS * ALL_IN_ROUND_TRIP_BPS / 10000.0   # 0.0074
ENTRY_COST = ROUND_TRIP_COST / 2.0                            # 0.0037 at entry
EXIT_COST = ROUND_TRIP_COST / 2.0                            # 0.0037 at exit

FUNDING_ANNUALIZATION_DAYS = _d20.FUNDING_ANNUALIZATION_DAYS   # 365
_ANN = FUNDING_ANNUALIZATION_DAYS ** 0.5
FORWARD_OOS_START = "2026-01-01"

EXPECTED_SOURCE_SHA256 = {
    "BTCUSDT_spot": "0a214e5fae7f7b73b632193c23d633ab87114b7559e75111fa9ed7f1ef998f1a",
    "BTCUSDT_perp": "bfbaccb9056b2ea4c2136182333040bf9efca612f0440de902f79e5c31068a95",
    "BTCUSDT_funding": "7071f1484b3cd2e8d1ebe4abd1df93434f99646b1c9fd464a12251ac72d6869e",
    "ETHUSDT_spot": "45e6616e0753f7edf2c0e3aae03c9435e08a06999a6876c728a8b8237093554b",
    "ETHUSDT_perp": "e02bb1a874001932064ac00a31eafcdd41d7841702c2ac0d315c87a2b4cb5bed",
    "ETHUSDT_funding": "32804816434bcab09709086d7171c46136b2986affba5c19b7b0ef5b898531ed",
    "SOLUSDT_spot": "b1ac44dc763eb987b03265ca6d293b0ce2f29acdb6ab02eca1fbe744e55bb227",
    "SOLUSDT_perp": "a9810dfab32f210d18dd6a428f424a769eaf9c5449367adf795c95374c7c49a0",
    "SOLUSDT_funding": "520d28ebdd8142967bc1f9159a16934dc606621ad4c530315af6f2f608dcc759",
}
EXPECTED_LABELS_SHA256 = (
    "e8282933ea1b07f14c7a09b72cc71632de2880d88e9105d3d0e91fe2702ca842")


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_closes(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split(",")
        di, ci = header.index("date"), header.index("close")
        for line in f:
            p = line.rstrip("\n").split(",")
            if len(p) > ci:
                out[p[di]] = float(p[ci])
    return out


def _read_daily_funding(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split(",")
        dti, fri = header.index("datetime"), header.index("funding_rate")
        for line in f:
            p = line.rstrip("\n").split(",")
            if len(p) <= fri:
                continue
            date = p[dti].split(" ")[0]
            try:
                out[date] = out.get(date, 0.0) + float(p[fri])
            except ValueError:
                continue
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
    cagr = (eq[-1] ** (FUNDING_ANNUALIZATION_DAYS / n)) - 1.0 if n > 0 else 0.0
    vol = _std(daily_rets) * _ANN
    sd = _std(daily_rets)
    sharpe = (_mean(daily_rets) / sd * _ANN) if sd > 0 else 0.0
    mdd = _max_drawdown(eq)
    calmar = (cagr / abs(mdd)) if mdd < 0 else 0.0
    return {"n_bars": n, "net_return": round(net, 6), "cagr": round(cagr, 6),
            "ann_vol": round(vol, 6), "sharpe": round(sharpe, 6),
            "max_drawdown": round(mdd, 6), "calmar": round(calmar, 6)}


def _replay_asset(sym, entries):
    spot = _read_closes(RAW_DIR / ("%s_spot_1d.csv" % sym))
    perp = _read_closes(RAW_DIR / ("%s_perp_1d.csv" % sym))
    fund = _read_daily_funding(RAW_DIR / ("%s_funding.csv" % sym))
    common = sorted(set(spot) & set(perp) & set(fund))
    n = len(common)
    s = [spot[d] for d in common]
    p = [perp[d] for d in common]
    fu = [fund[d] for d in common]

    held = [False] * n           # bar index in a position (entry+1 .. exit inclusive)
    entry_bars = set()
    exit_bars = set()
    for e in entries:
        eb, xb = e["entry_bar"], e["exit_bar"]
        entry_bars.add(eb)
        exit_bars.add(xb)
        for b in range(eb + 1, xb + 1):
            held[b] = True

    # strategy daily net return series + funding/basis contribution split + cost
    strat = [0.0] * n
    funding_pnl = [0.0] * n
    basis_pnl = [0.0] * n
    total_cost = 0.0
    for t in range(1, n):
        if held[t]:
            price = LEG_NOTIONAL * (s[t] / s[t - 1] - 1.0) \
                + LEG_NOTIONAL * (1.0 - p[t] / p[t - 1])
            fund_t = LEG_NOTIONAL * fu[t]      # short perp receives positive funding
            basis_pnl[t] += price
            funding_pnl[t] += fund_t
            strat[t] += price + fund_t
    for eb in entry_bars:
        strat[eb] -= ENTRY_COST
        total_cost += ENTRY_COST
    for xb in exit_bars:
        strat[xb] -= EXIT_COST
        total_cost += EXIT_COST

    # RANDOM/NULL market-neutral baseline: the ALWAYS-ON neutral carry (zero timing
    # skill) -- in position every bar, same funding/basis mechanics, ONE round-trip
    # at the window boundaries (no churn). NOT buy-and-hold.
    null = [0.0] * n
    for t in range(1, n):
        price = LEG_NOTIONAL * (s[t] / s[t - 1] - 1.0) \
            + LEG_NOTIONAL * (1.0 - p[t] / p[t - 1])
        null[t] = price + LEG_NOTIONAL * fu[t]
    null[1] -= ENTRY_COST
    null[n - 1] -= EXIT_COST

    # per-trade net (for win rate / avg trade)
    per_trade = []
    for e in entries:
        eb, xb = e["entry_bar"], e["exit_bar"]
        tnet = -ROUND_TRIP_COST
        for b in range(eb + 1, xb + 1):
            tnet += LEG_NOTIONAL * (s[b] / s[b - 1] - 1.0) \
                + LEG_NOTIONAL * (1.0 - p[b] / p[b - 1]) + LEG_NOTIONAL * fu[b]
        per_trade.append({"entry_bar": eb, "exit_bar": xb,
                          "entry_date": common[eb], "exit_date": common[xb],
                          "entry_reason": e.get("entry_reason"),
                          "trade_net": round(tnet, 8),
                          "in_forward_oos": common[eb] >= FORWARD_OOS_START})

    fwd_idx = [i for i in range(1, n) if common[i] >= FORWARD_OOS_START]
    return {
        "symbol": sym, "window": [common[0], common[-1]], "n_bars": n,
        "strat_daily": strat, "null_daily": null,
        "strat_fwd": [strat[i] for i in fwd_idx],
        "null_fwd": [null[i] for i in fwd_idx],
        "funding_pnl_total": round(sum(funding_pnl), 6),
        "basis_pnl_total": round(sum(basis_pnl), 6),
        "total_cost_drag": round(total_cost, 6),
        "per_trade": per_trade,
        "trade_count": len(per_trade),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # verify 9 source SHAs + labels SHA BEFORE reading anything
    files = {}
    for sym in SYMBOLS:
        files["%s_spot" % sym] = RAW_DIR / ("%s_spot_1d.csv" % sym)
        files["%s_perp" % sym] = RAW_DIR / ("%s_perp_1d.csv" % sym)
        files["%s_funding" % sym] = RAW_DIR / ("%s_funding.csv" % sym)
    sha_src = {k: compute_sha256(v) for k, v in files.items()}
    if sha_src != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("source_sha_pin_does_not_match_before_replay")
    sha_labels = compute_sha256(LABELS_PATH)
    if sha_labels != EXPECTED_LABELS_SHA256:
        raise RuntimeError("labels_sha_pin_does_not_match_before_replay")

    with open(LABELS_PATH, encoding="utf-8") as f:
        labels = json.load(f)
    detail = labels["per_asset_detail"]

    per_asset = {sym: _replay_asset(sym, detail[sym]["entries"]) for sym in SYMBOLS}

    # equal-weight portfolio daily return = mean of the per-asset daily returns over
    # the aligned tail (each asset on its own 1.0 capital; 1/3 allocation each).
    min_n = min(per_asset[s]["n_bars"] for s in SYMBOLS)
    port_strat, port_null = [], []
    for t in range(1, min_n):
        port_strat.append(_mean([per_asset[s]["strat_daily"][-min_n + t]
                                 for s in SYMBOLS]))
        port_null.append(_mean([per_asset[s]["null_daily"][-min_n + t]
                                for s in SYMBOLS]))

    all_trades = [t for s in SYMBOLS for t in per_asset[s]["per_trade"]]
    fwd_trades = [t for t in all_trades if t["in_forward_oos"]]
    wins = sum(1 for t in all_trades if t["trade_net"] > 0)
    win_rate = round(wins / len(all_trades), 6) if all_trades else 0.0
    avg_trade = round(_mean([t["trade_net"] for t in all_trades]), 8) \
        if all_trades else 0.0
    fwd_win_rate = round(sum(1 for t in fwd_trades if t["trade_net"] > 0)
                         / len(fwd_trades), 6) if fwd_trades else 0.0
    total_funding = round(sum(per_asset[s]["funding_pnl_total"] for s in SYMBOLS), 6)
    total_basis = round(sum(per_asset[s]["basis_pnl_total"] for s in SYMBOLS), 6)
    total_cost = round(sum(per_asset[s]["total_cost_drag"] for s in SYMBOLS), 6)

    # metrics: equal-weight portfolio + per asset, full-window + 2026 OOS
    strat_metrics = _metrics(port_strat)
    null_metrics = _metrics(port_null)
    # forward-OOS portfolio
    # (align per-asset fwd on common length; equal weight)
    min_fwd = min(len(per_asset[s]["strat_fwd"]) for s in SYMBOLS)
    port_strat_fwd, port_null_fwd = [], []
    for t in range(min_fwd):
        port_strat_fwd.append(_mean([per_asset[s]["strat_fwd"][-min_fwd + t]
                                     for s in SYMBOLS]))
        port_null_fwd.append(_mean([per_asset[s]["null_fwd"][-min_fwd + t]
                                    for s in SYMBOLS]))
    strat_oos = _metrics(port_strat_fwd)
    null_oos = _metrics(port_null_fwd)

    per_asset_metrics = {
        s: {"window": per_asset[s]["window"],
            "trade_count": per_asset[s]["trade_count"],
            "strategy": _metrics(per_asset[s]["strat_daily"][1:]),
            "null": _metrics(per_asset[s]["null_daily"][1:]),
            "strategy_forward_oos": _metrics(per_asset[s]["strat_fwd"]),
            "funding_pnl_total": per_asset[s]["funding_pnl_total"],
            "basis_pnl_total": per_asset[s]["basis_pnl_total"],
            "total_cost_drag": per_asset[s]["total_cost_drag"]}
        for s in SYMBOLS}

    # decisive gates (market-neutral: vs random/null, NOT buy-and-hold)
    gates = {
        "strategy_net_return_positive_after_cost": strat_metrics["net_return"] > 0,
        "strategy_sharpe_positive": strat_metrics["sharpe"] > 0,
        "beats_random_null_risk_adjusted":
            strat_metrics["sharpe"] > null_metrics["sharpe"],
        "forward_oos_net_return_positive": strat_oos["net_return"] > 0,
    }
    all_pass = all(gates.values())

    sha_after = {k: compute_sha256(v) for k, v in files.items()}
    if sha_after != sha_src:
        raise RuntimeError("inputs_mutated_during_replay")

    common = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "universe": list(SYMBOLS), "timeframe": TIMEFRAME,
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "source_sha256": sha_src, "labels_sha256": sha_labels,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "round_trip_cost_per_trade_bps": round(ROUND_TRIP_COST * 10000.0, 4),
        "cost_convention": ("37 bps all-in round-trip PER LEG; two legs (spot+perp) so "
                            "74 bps round-trip per trade (counts double); split 37 bps "
                            "entry / 37 bps exit; funding paid/received on the 0.5 "
                            "short-perp notional; basis marked at the D1 close; no perp "
                            "borrow/liquidation haircut is invented beyond this"),
        "baseline": "random/null market-neutral = always-on neutral carry (zero timing "
                    "skill); NOT buy-and-hold",
        "no_parameter_optimization": True, "no_reparameterization": True,
        "no_parameter_sweep": True, "no_tuning": True, "no_rescue": True,
        "trade_count": len(all_trades),
        "win_rate": win_rate, "avg_trade_net": avg_trade,
        "forward_oos_trade_count": len(fwd_trades),
        "forward_oos_win_rate": fwd_win_rate,
        "funding_contribution_total": total_funding,
        "basis_convergence_contribution_total": total_basis,
        "total_cost_drag": total_cost,
        "strategy_metrics": strat_metrics,
        "random_null_metrics": null_metrics,
        "strategy_forward_oos_metrics": strat_oos,
        "random_null_forward_oos_metrics": null_oos,
        "per_asset": per_asset_metrics,
        "decisive_gate_results": gates, "all_decisive_gates_pass": all_pass,
        "honest_framing": (
            "fee-honest equity-curve replay of the FROZEN C20 mechanically-neutral "
            "basis/funding-carry labels; 74 bps round-trip per trade (two legs x 37 "
            "bps), not droppable; funding paid/received; vs a random/null market-"
            "neutral baseline (always-on carry), NOT buy-and-hold; the decisive gates "
            "require net-positive-after-cost, positive Sharpe, beating the null "
            "risk-adjusted, and a holding forward-OOS edge; raw carry before cost is "
            "not the edge; not a profitability or paper/live claim"),
        "scope_locks": {
            "no_data_fetch": True, "no_relabel": True, "no_redetect_new_params": True,
            "no_optimization": True, "no_reparameterization": True,
            "no_parameter_sweep": True, "no_tuning": True, "no_rescue": True,
            "no_xauusd": True, "no_paper_trading": True, "no_live_trading": True,
            "no_broker": True, "no_credentials": True, "no_order_logic": True,
            "no_data_mutation": True, "no_cost_drop": True,
            "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
            "no_downstream_gate_unlock": True, "no_staging": True,
            "no_commit": True, "no_push": True,
        },
    }
    ledger = dict(common)
    ledger["artifact"] = "c20_replay_ledger"
    ledger["trades"] = all_trades
    with open(LEDGER_PATH, "w", encoding="utf-8") as fp:
        json.dump(ledger, fp, indent=2, sort_keys=True)
    ledger_sha = compute_sha256(LEDGER_PATH)

    summary = dict(common)
    summary["artifact"] = "c20_replay_summary"
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
        "trade_count": len(all_trades), "win_rate": win_rate,
        "avg_trade_net": avg_trade,
        "funding_contribution_total": total_funding,
        "basis_convergence_contribution_total": total_basis,
        "total_cost_drag": total_cost,
        "strategy_metrics": strat_metrics, "random_null_metrics": null_metrics,
        "strategy_forward_oos_metrics": strat_oos,
        "random_null_forward_oos_metrics": null_oos,
        "per_asset": per_asset_metrics,
        "decisive_gate_results": gates, "all_decisive_gates_pass": all_pass,
        "source_sha_stable": sha_src == sha_after,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    main()

"""C17 risk-adjusted portfolio-construction FEE-HONEST replay one-off runner
(READ-ONLY against the FROZEN C17 allocation labels + FROZEN local BTC/ETH/SOL 1d
data; RESEARCH ONLY; NO data fetch; NO relabel; NO re-allocation with new params;
NO optimization / re-parameterization; NO robustness expansion; NO trading / broker
/ credentials / orders; NO paper/live readiness claim).

Replays ONLY the FROZEN C17 weekly allocation labels (SHA-pinned): it forward-fills
the frozen held weight vectors over the SHA-pinned daily candles, compounds a daily
EQUITY CURVE of the long/flat basket, and charges the reserved 37 bps all-in cost as
18.5 bps ONE-WAY on each rebalance's turnover (Sum|dw|) -- a full 37 bps round trip
accumulates over a position's open+close legs. Cash (1 - gross) earns nothing.

It then computes risk-adjusted metrics (Sharpe, Calmar, max drawdown, net return,
annualized vol, turnover/cost drag) for the strategy and for two baselines on the
SAME window: per-asset buy-and-hold (BTC/ETH/SOL) and a weekly-rebalanced
equal-weight (1/3 each) basket, each net of the same cost model. The 2026 forward-OOS
sub-window is evaluated the same way. The decisive RISK-ADJUSTED gates (beat
buy-and-hold AND the equal-weight basket on Sharpe and/or Calmar with no worse max
drawdown, and the forward-OOS edge holds) are evaluated; the verdict is recorded for
human review. NO parameter is fitted or changed -- the frozen labels are replayed
exactly.
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

CANDIDATE_ID = "RISK_ADJUSTED_PORTFOLIO_CONSTRUCTION_VOL_TARGETED_ALLOCATION_V1"
CANDIDATE_FAMILY = "risk_adjusted_portfolio_construction_vol_targeted_allocation"
ASSETS = ("BTCUSD", "ETHUSD", "SOLUSD")
TIMEFRAME = "1d"

FEE_ROUND_TRIP_BPS = 27.0
SLIPPAGE_ROUND_TRIP_BPS = 10.0
ALL_IN_ROUND_TRIP_BPS = FEE_ROUND_TRIP_BPS + SLIPPAGE_ROUND_TRIP_BPS  # 37.0
ONE_WAY_COST = (ALL_IN_ROUND_TRIP_BPS / 2.0) / 10000.0               # 18.5 bps
ANNUALIZATION_DAYS = 365
_ANN = ANNUALIZATION_DAYS ** 0.5
FORWARD_OOS_START = "2026-01-01"

HEAD_AT_LABELS_REVIEW = "2064849719e7b09077ce2e983c6ecff22a24cd63"

SOURCES = {s: REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / ("%s_1d.csv"
           % s.replace("USD", "")) for s in ASSETS}
EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

C17_DIR = (REPO_ROOT / "data"
           / "risk_adjusted_portfolio_construction_vol_targeted_allocation_c17")
LABELS_PATH = C17_DIR / "allocation_labels" / "c17_allocation_labels.json"
EXPECTED_LABELS_SHA256 = (
    "32ffb538c09d0158027071df19ec4749e894bd568225f7503a4fa7d2f349a7c7")

OUT_DIR = C17_DIR / "replay_results"
LEDGER_PATH = OUT_DIR / "c17_replay_ledger.json"
SUMMARY_PATH = OUT_DIR / "c17_replay_summary.json"


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_closes(path):
    out = {}
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["date"]] = float(r["close"])
    return out


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs):
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return (sum((v - m) ** 2 for v in xs) / (len(xs) - 1)) ** 0.5


def _max_drawdown(equity):
    peak = equity[0] if equity else 1.0
    mdd = 0.0
    for v in equity:
        peak = max(peak, v)
        mdd = min(mdd, v / peak - 1.0)
    return mdd


def _metrics(daily_rets, dates):
    """Sharpe / Calmar / max-drawdown / net-return / annualized vol from a daily
    net-return series. Pure."""
    if not daily_rets:
        return {"n_days": 0, "net_return": 0.0, "cagr": 0.0, "ann_vol": 0.0,
                "sharpe": 0.0, "max_drawdown": 0.0, "calmar": 0.0}
    equity = [1.0]
    for r in daily_rets:
        equity.append(equity[-1] * (1.0 + r))
    n = len(daily_rets)
    net_return = equity[-1] - 1.0
    cagr = (equity[-1] ** (ANNUALIZATION_DAYS / n)) - 1.0 if n > 0 else 0.0
    ann_vol = _std(daily_rets) * _ANN
    sharpe = (_mean(daily_rets) / _std(daily_rets) * _ANN) if _std(daily_rets) > 0 \
        else 0.0
    mdd = _max_drawdown(equity)
    calmar = (cagr / abs(mdd)) if mdd < 0 else 0.0
    return {"n_days": n, "net_return": round(net_return, 6),
            "cagr": round(cagr, 6), "ann_vol": round(ann_vol, 6),
            "sharpe": round(sharpe, 6), "max_drawdown": round(mdd, 6),
            "calmar": round(calmar, 6)}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sha_before = {s: compute_sha256(SOURCES[s]) for s in ASSETS}
    if sha_before != EXPECTED_SOURCE_SHA256:
        raise RuntimeError("source_sha_pins_do_not_match_before_replay")
    labels_sha = compute_sha256(LABELS_PATH)
    if labels_sha != EXPECTED_LABELS_SHA256:
        raise RuntimeError("labels_sha_pin_does_not_match_before_replay")

    with open(LABELS_PATH, encoding="utf-8") as f:
        labels_doc = json.load(f)
    frozen_labels = sorted(labels_doc["allocation_labels"], key=lambda r: r["date"])

    closes = {s: load_closes(SOURCES[s]) for s in ASSETS}
    common = sorted(set(closes["BTCUSD"]) & set(closes["ETHUSD"])
                    & set(closes["SOLUSD"]))
    idx = {d: i for i, d in enumerate(common)}
    daily_ret = {s: {} for s in ASSETS}
    for s in ASSETS:
        for i in range(1, len(common)):
            d0, d1 = common[i - 1], common[i]
            daily_ret[s][d1] = closes[s][d1] / closes[s][d0] - 1.0

    # rebalance map: date -> (weights, executed, is_initial, turnover)
    reb = {lab["date"]: lab for lab in frozen_labels}
    first_date = frozen_labels[0]["date"]
    start_i = idx[first_date]
    window_dates = common[start_i + 1:]   # returns start the day after first weights

    # --- strategy equity (forward-filled frozen weights, cost on turnover) ---
    cur_w = dict(frozen_labels[0]["weights"])
    strat_rets, strat_dates = [], []
    fwd_rets, fwd_dates = [], []
    total_cost_drag = 0.0
    total_turnover = 0.0
    for d in window_dates:
        cost = 0.0
        if d in reb:
            lab = reb[d]
            cur_w = dict(lab["weights"])
            if lab["executed"] and not lab["is_initial"]:
                cost = lab["turnover"] * ONE_WAY_COST
                total_cost_drag += cost
                total_turnover += lab["turnover"]
        gross_ret = sum(cur_w[s] * daily_ret[s][d] for s in ASSETS)
        net = gross_ret - cost
        strat_rets.append(net)
        strat_dates.append(d)
        if d >= FORWARD_OOS_START:
            fwd_rets.append(net)
            fwd_dates.append(d)

    # --- baselines on the SAME window ---
    # per-asset buy-and-hold (100% asset, drift, one initial one-way cost)
    bh = {}
    for s in ASSETS:
        rets = [daily_ret[s][d] for d in window_dates]
        if rets:
            rets = list(rets)
            rets[0] = rets[0] - ONE_WAY_COST
        bh[s] = _metrics(rets, window_dates)
    # weekly-rebalanced equal-weight basket (1/3 each), net of turnover cost
    ew_rets = []
    ew_w = {s: 1.0 / 3.0 for s in ASSETS}
    for d in window_dates:
        cost = 0.0
        if d in reb:   # rebalance cadence matches the strategy (weekly)
            # turnover to restore 1/3 weights after drift since last rebalance
            drift_turn = sum(abs(ew_w[s] - 1.0 / 3.0) for s in ASSETS)
            cost = drift_turn * ONE_WAY_COST
            ew_w = {s: 1.0 / 3.0 for s in ASSETS}
        gret = sum(ew_w[s] * daily_ret[s][d] for s in ASSETS)
        ew_rets.append(gret - cost)
        # drift the weights by today's returns for the next day
        nav = sum(ew_w[s] * (1.0 + daily_ret[s][d]) for s in ASSETS)
        if nav > 0:
            ew_w = {s: ew_w[s] * (1.0 + daily_ret[s][d]) / nav for s in ASSETS}

    strat = _metrics(strat_rets, strat_dates)
    strat_fwd = _metrics(fwd_rets, fwd_dates)
    ew = _metrics(ew_rets, window_dates)
    bh_best_sharpe = max(bh[s]["sharpe"] for s in ASSETS)
    bh_best_calmar = max(bh[s]["calmar"] for s in ASSETS)
    bh_worst_mdd = min(bh[s]["max_drawdown"] for s in ASSETS)   # most negative
    # forward-OOS baselines
    bh_fwd = {}
    for s in ASSETS:
        rets = [daily_ret[s][d] for d in fwd_dates]
        bh_fwd[s] = _metrics(rets, fwd_dates)
    ew_fwd_rets = [ew_rets[window_dates.index(d)] for d in fwd_dates]
    ew_fwd = _metrics(ew_fwd_rets, fwd_dates)

    cost_drag_total = round(total_cost_drag, 6)
    avg_turnover_per_reb = round(
        total_turnover / max(1, sum(1 for d in window_dates if d in reb
                                    and reb[d]["executed"]
                                    and not reb[d]["is_initial"])), 6)

    # --- decisive RISK-ADJUSTED gates ---
    no_worse_mdd_than_bh = strat["max_drawdown"] >= bh_worst_mdd   # less negative
    no_worse_mdd_than_ew = strat["max_drawdown"] >= ew["max_drawdown"]
    beats_bh_risk_adj = ((strat["sharpe"] > bh_best_sharpe
                          or strat["calmar"] > bh_best_calmar)
                         and no_worse_mdd_than_bh)
    beats_ew_risk_adj = ((strat["sharpe"] > ew["sharpe"]
                          or strat["calmar"] > ew["calmar"])
                         and no_worse_mdd_than_ew)
    fwd_edge_holds = (strat_fwd["sharpe"] > ew_fwd["sharpe"]
                      or strat_fwd["sharpe"] > max(bh_fwd[s]["sharpe"]
                                                   for s in ASSETS))
    gates = {
        "beats_buy_and_hold_risk_adjusted": beats_bh_risk_adj,
        "beats_equal_weight_basket_risk_adjusted": beats_ew_risk_adj,
        "max_drawdown_no_worse_than_buy_and_hold": no_worse_mdd_than_bh,
        "max_drawdown_no_worse_than_equal_weight": no_worse_mdd_than_ew,
        "forward_oos_risk_adjusted_edge_holds": fwd_edge_holds,
        "turnover_cost_drag_tolerable": cost_drag_total < abs(strat["net_return"])
        if strat["net_return"] != 0 else True,
    }
    all_gates_pass = all(gates.values())

    sha_mid = {s: compute_sha256(SOURCES[s]) for s in ASSETS}
    if sha_mid != sha_before:
        raise RuntimeError("inputs_mutated_during_replay")

    common_meta = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "assets": list(ASSETS), "timeframe": TIMEFRAME,
        "head_at_labels_review": HEAD_AT_LABELS_REVIEW,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "source_sha256": sha_before,
        "fee_round_trip_bps": FEE_ROUND_TRIP_BPS,
        "slippage_round_trip_bps": SLIPPAGE_ROUND_TRIP_BPS,
        "all_in_round_trip_bps": ALL_IN_ROUND_TRIP_BPS,
        "one_way_cost_bps": round(ONE_WAY_COST * 10000.0, 4),
        "cost_convention": "37bps round trip = 18.5bps one-way on turnover Sum|dw|",
        "no_parameter_optimization": True, "no_reparameterization": True,
        "replay_window": [window_dates[0], window_dates[-1]],
        "n_days": len(window_dates),
        "strategy_metrics": strat,
        "strategy_forward_oos_metrics": strat_fwd,
        "buy_and_hold_metrics_per_asset": bh,
        "buy_and_hold_forward_oos_metrics_per_asset": bh_fwd,
        "equal_weight_basket_metrics": ew,
        "equal_weight_basket_forward_oos_metrics": ew_fwd,
        "total_cost_drag": cost_drag_total,
        "total_turnover": round(total_turnover, 6),
        "avg_turnover_per_executed_rebalance": avg_turnover_per_reb,
        "decisive_gate_results": gates,
        "all_decisive_gates_pass": all_gates_pass,
        "scope_locks": {
            "no_data_fetch": True, "no_relabel": True, "no_reallocation_new_params": True,
            "no_optimization": True, "no_reparameterization": True,
            "no_robustness": True, "no_paper_trading": True, "no_live_trading": True,
            "no_broker": True, "no_credentials": True, "no_order_logic": True,
            "no_auto_trading": True, "no_data_mutation": True,
            "no_profitability_claim": True, "no_paper_live_readiness_claim": True,
            "no_downstream_gate_unlock": True, "no_staging": True,
            "no_commit": True, "no_push": True,
        },
        "honest_framing": (
            "fee-honest EQUITY-CURVE replay of the FROZEN C17 weekly allocation "
            "labels; 37 bps all-in applied as 18.5 bps one-way on turnover and not "
            "droppable; vs per-asset buy-and-hold and a weekly-rebalanced "
            "equal-weight basket on the same window; the decisive gates require a "
            "RISK-ADJUSTED win (Sharpe and/or Calmar with no worse max drawdown) vs "
            "BOTH baselines AND a holding forward-OOS edge; the vol-target runs the "
            "strategy at ~20% vol so its RETURN is far below buy-and-hold crypto by "
            "design -- the claim is risk-adjusted, not raw return; not a "
            "profitability or paper/live-readiness claim"),
    }
    ledger_payload = dict(common_meta)
    ledger_payload["artifact"] = "c17_replay_ledger"
    ledger_payload["strategy_daily_returns"] = [
        {"date": d, "net_return": round(r, 8)}
        for d, r in zip(strat_dates, strat_rets)]
    with open(LEDGER_PATH, "w", encoding="utf-8") as f:
        json.dump(ledger_payload, f, indent=2, sort_keys=True)
    ledger_sha = compute_sha256(LEDGER_PATH)

    summary_payload = dict(common_meta)
    summary_payload["artifact"] = "c17_replay_summary"
    summary_payload["ledger_path"] = str(
        LEDGER_PATH.relative_to(REPO_ROOT)).replace("\\", "/")
    summary_payload["ledger_sha256"] = ledger_sha
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary_payload, f, indent=2, sort_keys=True)
    summary_sha = compute_sha256(SUMMARY_PATH)

    sha_after = {s: compute_sha256(SOURCES[s]) for s in ASSETS}
    if sha_after != sha_before:
        raise RuntimeError("inputs_mutated_after_replay_artifact_write")

    report = {
        "ledger_path": str(LEDGER_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "ledger_sha256": ledger_sha,
        "summary_path": str(SUMMARY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "summary_sha256": summary_sha,
        "replay_window": [window_dates[0], window_dates[-1]],
        "n_days": len(window_dates),
        "strategy_metrics": strat,
        "strategy_forward_oos_metrics": strat_fwd,
        "buy_and_hold_metrics_per_asset": bh,
        "equal_weight_basket_metrics": ew,
        "equal_weight_basket_forward_oos_metrics": ew_fwd,
        "total_cost_drag": cost_drag_total,
        "total_turnover": round(total_turnover, 6),
        "decisive_gate_results": gates,
        "all_decisive_gates_pass": all_gates_pass,
        "source_sha_stable": sha_before == sha_after,
    }
    for k, v in report.items():
        print("%s = %r" % (k, v))
    return report


if __name__ == "__main__":
    main()

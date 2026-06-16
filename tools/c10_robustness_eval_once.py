"""C10 robustness / sensitivity evaluation one-off runner (READ-ONLY against
the FROZEN, SHA-pinned C10 replay ledger/summary, detector labels, and BTCUSD
1d source; RESEARCH ONLY; NO TRADING; NO NETWORK; NO PnL/PROFITABILITY CLAIM;
NO RELABEL; NO PARAMETER FITTING; NO OPTIMIZATION; NO DOWNSTREAM GATE UNLOCK).

Stress-tests the frozen C10 fee+slippage-honest replay results. Everything is a
RE-AGGREGATION of already-frozen per-setup outcomes, except the horizon
sensitivity, which RE-WALKS the SAME frozen, SHA-pinned source candles at
alternative fixed horizons over the SAME Friday entries (no weekday change, no
relabel, no detector re-run, no data fetch). No parameter is fit; no best
variant/horizon/cost is selected as a promotion claim -- every cell is reported.

Checks:
  1. COST STRESS: recompute net R per variant at 37 (current) / 50 / 75 / 100
     bps all-in, using each setup's frozen gross_r and stop_distance_bps:
         net_r = gross_r - cost_bps / stop_distance_bps
  2. SUB-PERIOD: per-year (2023/2024/2025) and first-half vs second-half (by
     chronological entry order) net R at the canonical 37 bps.
  3. VARIANT STABILITY: 2R / 3R / 4R side by side.
  4. HORIZON SENSITIVITY: re-walk frozen source at horizons 3/5/7/10 bars over
     the same entries (canonical horizon stays 5; alternatives are sensitivity
     only) -> total net R at 37 bps; confirms 5-day-drift dependence.
  5. DRAWDOWN: max drawdown, worst losing streak (consecutive net<0), and worst
     month / quarter / year net R (canonical 37 bps, 5-bar horizon).
  6. REGIME DECAY: 2025 sub-stats per variant (win rate, mean R, hit/miss/
     horizon counts, total net) to explain the negative 2025.

Hard locks (declarative): no_paper_trading, no_micro_live, no_live_trading,
no_broker, no_exchange, no_wallet, no_account, no_credentials, no_order_logic,
no_portfolio_allocation, no_api, no_network, no_fetch, no_notification,
no_scheduler, no_relabel, no_detector_change, no_edit_token_use,
no_parameter_fitting, no_weekday_change, no_profitability_claim,
no_downstream_gate_unlock, no_staging, no_commit, no_push.

Intentionally untracked; writes only into the gitignored robustness data dir.
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

CANDIDATE_ID = "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1"
CANDIDATE_FAMILY = "intraweek_calendar_seasonality_drift"
SYMBOL = "BTCUSD"
TIMEFRAME = "1d"
DIRECTION = "long_only"
SAMPLE_TAG = "2023-01-01_2025-12-31"

CANONICAL_HORIZON_BARS = 5
CANONICAL_ALL_IN_BPS = 37.0
COST_STRESS_BPS = (37.0, 50.0, 75.0, 100.0)
HORIZON_SENSITIVITY_BARS = (3, 5, 7, 10)
VARIANTS = (("2r", 2.0), ("3r", 3.0), ("4r", 4.0))
HEAD_AT_REPLAY_REVIEW = "9a03e638610c371efe8bde1255f958277f7b5bbe"

DATA_DIR = REPO_ROOT / "data" / "intraweek_calendar_seasonality_c10"
LEDGER_INPUT = DATA_DIR / "replay_results" / ("c10_replay_ledger_%s.json"
                                              % SAMPLE_TAG)
SUMMARY_INPUT = DATA_DIR / "replay_results" / ("c10_replay_summary_%s.json"
                                               % SAMPLE_TAG)
LABELS_INPUT = DATA_DIR / "detector_labels" / ("c10_detector_labels_%s.json"
                                               % SAMPLE_TAG)
SOURCE_FILE = REPO_ROOT / "data" / "crypto_d1_spot" / "raw" / "BTC_1d.csv"

EXPECTED_LEDGER_SHA = (
    "4675f0fd28fc94db9504294a94186cff2576422802bc7f8fb38199aa8251c3ba")
EXPECTED_SUMMARY_SHA = (
    "78ca7dafcd3fe46ec252a43fa4153ec48cd32d2878cd7bebb54ebd5dad839d61")
EXPECTED_LABELS_SHA = (
    "8276e9a6ee9bd9b89ff28a41f5c160973934bcc03ad8c5371095e62fb8f9c47d")
EXPECTED_SOURCE_SHA = (
    "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88")

OUT_DIR = DATA_DIR / "robustness_eval"
ROBUSTNESS_PATH = OUT_DIR / ("c10_robustness_eval_%s.json" % SAMPLE_TAG)


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_bars(path):
    bars = []
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            bars.append({"date": row["date"], "high": float(row["high"]),
                         "low": float(row["low"]), "close": float(row["close"])})
    bars.sort(key=lambda b: b["date"])
    return bars


def _quarter(month):
    return (month - 1) // 3 + 1


# ---- 1. cost stress (re-aggregation of frozen per-setup outcomes) ---------

def cost_stress(per_variant):
    out = {}
    for name, _mult in VARIANTS:
        kept = per_variant[name]["kept"]
        per_cost = {}
        for cost in COST_STRESS_BPS:
            nets = [o["gross_r"] - cost / o["stop_distance_bps"]
                    for o in kept if o.get("gross_r") is not None]
            n = len(nets)
            total = sum(nets)
            wins = sum(1 for x in nets if x > 0)
            per_cost["%dbps" % int(cost)] = {
                "all_in_bps": cost,
                "trade_count": n,
                "net_r_total": round(total, 4),
                "net_r_mean": round(total / n, 4) if n else None,
                "win_rate": round(wins / n, 4) if n else None,
                "net_positive": total > 0,
            }
        out[name] = per_cost
    return out


# ---- 2/5. sub-period + drawdown (canonical 37 bps, frozen 5-bar outcomes) --

def _net_all_in(o):
    return o["gross_r"] - CANONICAL_ALL_IN_BPS / o["stop_distance_bps"]


def subperiod_and_drawdown(per_variant):
    sub = {}
    dd = {}
    for name, _mult in VARIANTS:
        kept = sorted((o for o in per_variant[name]["kept"]
                       if o.get("gross_r") is not None),
                      key=lambda o: o["entry_index"])
        per_year = {}
        per_month = {}
        per_quarter = {}
        for o in kept:
            nr = _net_all_in(o)
            y = o["entry_date"][:4]
            m = o["entry_date"][:7]
            q = "%s-Q%d" % (y, _quarter(int(o["entry_date"][5:7])))
            per_year[y] = per_year.get(y, 0.0) + nr
            per_month[m] = per_month.get(m, 0.0) + nr
            per_quarter[q] = per_quarter.get(q, 0.0) + nr
        half = len(kept) // 2
        first = sum(_net_all_in(o) for o in kept[:half])
        second = sum(_net_all_in(o) for o in kept[half:])
        sub[name] = {
            "per_year": {k: round(v, 4) for k, v in sorted(per_year.items())},
            "first_half_net_r": round(first, 4),
            "second_half_net_r": round(second, 4),
            "first_half_trades": half,
            "second_half_trades": len(kept) - half,
        }
        # drawdown + worst losing streak on the chronological net curve
        equity = peak = max_dd = 0.0
        streak = worst_streak = 0
        for o in kept:
            nr = _net_all_in(o)
            equity += nr
            peak = max(peak, equity)
            max_dd = max(max_dd, peak - equity)
            if nr < 0:
                streak += 1
                worst_streak = max(worst_streak, streak)
            else:
                streak = 0
        worst_month = min(per_month.items(), key=lambda kv: kv[1])
        worst_quarter = min(per_quarter.items(), key=lambda kv: kv[1])
        worst_year = min(per_year.items(), key=lambda kv: kv[1])
        dd[name] = {
            "max_drawdown_r": round(max_dd, 4),
            "worst_losing_streak_trades": worst_streak,
            "worst_month": [worst_month[0], round(worst_month[1], 4)],
            "worst_quarter": [worst_quarter[0], round(worst_quarter[1], 4)],
            "worst_year": [worst_year[0], round(worst_year[1], 4)],
        }
    return sub, dd


# ---- 4. horizon sensitivity (re-walk frozen source, same entries) ----------

def _walk(bars, setup, variant_r, horizon):
    entry = float(setup["entry_price"])
    stop = float(setup["stop_price"])
    dist = float(setup["stop_distance"])
    dist_bps = (dist / entry) * 10000.0
    target = entry + variant_r * dist
    ei = int(setup["entry_index"])
    xi = ei + horizon
    if xi >= len(bars) or bars[ei]["date"] != setup["entry_date"]:
        return None
    for i in range(ei + 1, xi + 1):
        if bars[i]["low"] <= stop:
            gross = -1.0
            break
        if bars[i]["high"] >= target:
            gross = float(variant_r)
            break
    else:
        gross = (bars[xi]["close"] - entry) / dist
    return gross - CANONICAL_ALL_IN_BPS / dist_bps


def horizon_sensitivity(bars, accepted):
    out = {}
    for name, mult in VARIANTS:
        per_h = {}
        for h in HORIZON_SENSITIVITY_BARS:
            nets = [v for v in (_walk(bars, s, mult, h) for s in accepted)
                    if v is not None]
            n = len(nets)
            total = sum(nets)
            wins = sum(1 for x in nets if x > 0)
            per_h["h%d" % h] = {
                "horizon_bars": h,
                "is_canonical": h == CANONICAL_HORIZON_BARS,
                "trade_count": n,
                "net_r_total_37bps": round(total, 4),
                "win_rate": round(wins / n, 4) if n else None,
                "net_positive": total > 0,
            }
        out[name] = per_h
    return out


# ---- 6. regime decay 2025 --------------------------------------------------

def regime_decay_2025(per_variant):
    out = {}
    for name, _mult in VARIANTS:
        kept = [o for o in per_variant[name]["kept"]
                if o.get("gross_r") is not None and o["entry_date"][:4] == "2025"]
        n = len(kept)
        nets = [_net_all_in(o) for o in kept]
        counts = {"hit": 0, "miss": 0, "miss_same_bar_straddle": 0,
                  "horizon": 0}
        for o in kept:
            counts[o["outcome"]] = counts.get(o["outcome"], 0) + 1
        horizon_gross = [o["gross_r"] for o in kept if o["outcome"] == "horizon"]
        out[name] = {
            "trade_count": n,
            "net_r_total": round(sum(nets), 4),
            "net_r_mean": round(sum(nets) / n, 4) if n else None,
            "win_rate": round(sum(1 for x in nets if x > 0) / n, 4) if n else None,
            "counts": counts,
            "horizon_exit_mean_gross_r":
                round(sum(horizon_gross) / len(horizon_gross), 4)
                if horizon_gross else None,
        }
    return out


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sha_before = {
        "ledger": compute_sha256(LEDGER_INPUT),
        "summary": compute_sha256(SUMMARY_INPUT),
        "labels": compute_sha256(LABELS_INPUT),
        "source": compute_sha256(SOURCE_FILE),
    }
    expected = {"ledger": EXPECTED_LEDGER_SHA, "summary": EXPECTED_SUMMARY_SHA,
                "labels": EXPECTED_LABELS_SHA, "source": EXPECTED_SOURCE_SHA}
    if sha_before != expected:
        raise RuntimeError("input_sha_pins_do_not_match_before_robustness")

    with open(LEDGER_INPUT, encoding="utf-8") as f:
        ledger = json.load(f)
    per_variant = ledger["per_variant"]
    with open(LABELS_INPUT, encoding="utf-8") as f:
        labels = json.load(f)
    accepted = labels["accepted_setups_post_anti_cluster"]
    bars = load_bars(SOURCE_FILE)

    cs = cost_stress(per_variant)
    sub, dd = subperiod_and_drawdown(per_variant)
    hs = horizon_sensitivity(bars, accepted)
    regime = regime_decay_2025(per_variant)

    sha_after = {
        "ledger": compute_sha256(LEDGER_INPUT),
        "summary": compute_sha256(SUMMARY_INPUT),
        "labels": compute_sha256(LABELS_INPUT),
        "source": compute_sha256(SOURCE_FILE),
    }
    if sha_after != sha_before:
        raise RuntimeError("inputs_mutated_during_robustness_evaluation")

    # Derived survival flags (NO optimization; every cell is reported).
    survives_50 = all(cs[n]["50bps"]["net_positive"] for n, _ in VARIANTS)
    survives_75 = all(cs[n]["75bps"]["net_positive"] for n, _ in VARIANTS)
    survives_100 = all(cs[n]["100bps"]["net_positive"] for n, _ in VARIANTS)
    all_years_positive = all(
        all(v > 0 for v in sub[n]["per_year"].values()) for n, _ in VARIANTS)
    decay_2025_all_negative = all(regime[n]["net_r_total"] < 0
                                  for n, _ in VARIANTS)

    scope_locks = {
        "no_paper_trading": True, "no_micro_live": True,
        "no_live_trading": True, "no_broker": True, "no_exchange": True,
        "no_wallet": True, "no_account": True, "no_credentials": True,
        "no_order_logic": True, "no_portfolio_allocation": True,
        "no_api": True, "no_network": True, "no_fetch": True,
        "no_notification": True, "no_scheduler": True, "no_relabel": True,
        "no_detector_change": True, "no_edit_token_use": True,
        "no_parameter_fitting": True, "no_weekday_change": True,
        "no_profitability_claim": True, "no_downstream_gate_unlock": True,
        "no_staging": True, "no_commit": True, "no_push": True,
    }
    payload = {
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "symbol": SYMBOL, "timeframe": TIMEFRAME, "direction": DIRECTION,
        "sample_tag": SAMPLE_TAG,
        "head_at_replay_review": HEAD_AT_REPLAY_REVIEW,
        "input_sha256": sha_before,
        "inputs_unchanged_during_evaluation": sha_after == sha_before,
        "canonical_horizon_bars": CANONICAL_HORIZON_BARS,
        "canonical_all_in_bps": CANONICAL_ALL_IN_BPS,
        "cost_stress_bps": list(COST_STRESS_BPS),
        "horizon_sensitivity_bars": list(HORIZON_SENSITIVITY_BARS),
        "cost_stress": cs,
        "sub_period": sub,
        "drawdown": dd,
        "horizon_sensitivity": hs,
        "regime_decay_2025": regime,
        "survival_flags": {
            "survives_cost_50bps_all_variants": survives_50,
            "survives_cost_75bps_all_variants": survives_75,
            "survives_cost_100bps_all_variants": survives_100,
            "all_individual_years_positive": all_years_positive,
            "decay_2025_negative_all_variants": decay_2025_all_negative,
        },
        "honest_framing": (
            "robustness/sensitivity re-aggregation + horizon re-walk over "
            "FROZEN inputs only; no relabel; no weekday change; no parameter "
            "fitting; no best-cell selection as a promotion claim; not a "
            "profitability claim; no downstream gate unlocked"),
        "scope_locks": scope_locks,
    }
    with open(ROBUSTNESS_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, sort_keys=True)
    robustness_sha = compute_sha256(ROBUSTNESS_PATH)

    if compute_sha256(SOURCE_FILE) != EXPECTED_SOURCE_SHA:
        raise RuntimeError("source_mutated_after_robustness_write")

    report = {
        "robustness_path":
            str(ROBUSTNESS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "robustness_sha256": robustness_sha,
        "survives_cost_50bps_all_variants": survives_50,
        "survives_cost_75bps_all_variants": survives_75,
        "survives_cost_100bps_all_variants": survives_100,
        "all_individual_years_positive": all_years_positive,
        "decay_2025_negative_all_variants": decay_2025_all_negative,
        "cost_stress": cs,
        "sub_period": sub,
        "drawdown": dd,
        "horizon_sensitivity": hs,
        "regime_decay_2025": regime,
    }
    for key, value in report.items():
        print("%s = %r" % (key, value))
    return report


if __name__ == "__main__":
    main()

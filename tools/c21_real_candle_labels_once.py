"""Candidate #21 -- real-candle LABELS runner (ONE-OFF, LABELS STAGE ONLY).

Reads the EXISTING, FROZEN, PUBLIC BTC/ETH/SOL spot + USDT-perp + funding D1 dataset
(no fetch), verifies the 9 source SHA256 provenance hashes against the committed
data-readiness review BEFORE reading anything, and applies the FROZEN C21 detector rules
EXACTLY (reusing the committed detector's pure run_detector -- this is NOT
re-parameterization) to produce real-candle LABELS only, PER ASSET:

  * same-asset basis = (perp_close - spot_close) / spot_close (diagnostic; no basis-z);
  * D1 funding -> 30-bar annualized carry; mechanical-neutrality GATE ZERO (equal-notional
    long-spot / short-same-asset-perp);
  * CARRY-REGIME gate (enter when annualized carry >= 100 bps), wide enter/exit
    hysteresis, HOLD PERSISTENCE (min hold >= 20 bars), durable carry-regime breakdown
    exit ONLY (>= 7 consecutive negative-carry bars), rebalance cadence 30 bars, hard
    turnover ceiling <= 6 round-trips/year/asset; NO basis-z stop, NO drawdown stop.

It emits ONLY labels (per-asset detected setups = accepted entries + rejected/blocked
candidate signals, hold lengths, exit-reason counts, mechanical-neutrality counts,
turnover/round-trips, forward-OOS 2026 counts) into a GITIGNORED data artifact. It runs
NO replay, NO PnL, applies NO fee (37/74 bps RESERVED for replay), does NO optimization /
tuning / rescue / parameter change, touches NO XAUUSD, does NOT rescue/retune C20, and
writes NO tracked file. All side effects happen only in main(); the artifact stays
untracked.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# the frozen C21 detector (pure run_detector + params; reused, not redefined)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_detector_spec_dry_run_contract as _d21  # noqa: E402,E501

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "crypto_basis_funding_research" / "raw"
OUT_DIR = (REPO_ROOT / "data"
           / "low_turnover_same_asset_spot_perp_funding_carry_c21" / "labels")
LABELS_PATH = OUT_DIR / "c21_labels.json"
SUMMARY_PATH = OUT_DIR / "c21_labels_summary.json"

SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
SPOT = {s: RAW_DIR / ("%s_spot_1d.csv" % s) for s in SYMBOLS}
PERP = {s: RAW_DIR / ("%s_perp_1d.csv" % s) for s in SYMBOLS}
FUNDING = {s: RAW_DIR / ("%s_funding.csv" % s) for s in SYMBOLS}

# the 9 frozen source SHA256 hashes pinned in the committed data-readiness review.
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

# frozen detector params (reused, never redefined here)
CARRY_REGIME_WINDOW = _d21.CARRY_REGIME_WINDOW          # 30
ENTER_CARRY_BPS = _d21.ENTER_CARRY_BPS                 # 100.0
BREAKDOWN_BARS = _d21.BREAKDOWN_BARS                   # 7
MIN_HOLD_BARS = _d21.MIN_HOLD_BARS                     # 20
REBALANCE_CADENCE = _d21.REBALANCE_CADENCE            # 30
MAX_ROUND_TRIPS_PER_YEAR = _d21.MAX_ROUND_TRIPS_PER_YEAR   # 6
MAX_GROSS = _d21.MAX_GROSS                            # 1.0
FUNDING_ANNUALIZATION_DAYS = _d21.FUNDING_ANNUALIZATION_DAYS   # 365
FORWARD_OOS_FROM = "2026-01-01"


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_closes(path: Path) -> dict:
    out: dict = {}
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split(",")
        di, ci = header.index("date"), header.index("close")
        for line in f:
            parts = line.rstrip("\n").split(",")
            if len(parts) <= ci:
                continue
            out[parts[di]] = float(parts[ci])
    return out


def _read_daily_funding(path: Path) -> dict:
    out: dict = {}
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split(",")
        dti, fri = header.index("datetime"), header.index("funding_rate")
        for line in f:
            parts = line.rstrip("\n").split(",")
            if len(parts) <= fri:
                continue
            date = parts[dti].split(" ")[0]
            try:
                out[date] = out.get(date, 0.0) + float(parts[fri])
            except ValueError:
                continue
    return out


def _label_asset(sym: str, spot: dict, perp: dict, funding_daily: dict) -> dict:
    """Apply the FROZEN C21 detector to ONE asset's aligned real candles, then derive
    labels: detected candidate setups (accepted entries + rejected/blocked signals),
    hold lengths, exit-reason counts, mechanical-neutrality counts, turnover. Mechanical
    neutrality holds by construction (same-asset, equal-notional)."""
    common = sorted(set(spot) & set(perp) & set(funding_daily))
    n = len(common)
    s = [spot[d] for d in common]
    p = [perp[d] for d in common]
    fu = [funding_daily[d] for d in common]

    res = _d21.run_detector(s, p, fu, same_asset=True, equal_notional=True)
    trades = res["trades"]

    accepted = len(trades)                              # entries taken (accepted labels)
    rejected = (res["blocked_by_cadence"]
                + res["blocked_by_turnover_ceiling"])   # blocked candidate signals
    detected = accepted + rejected                      # total detected candidate setups
    hold_lengths = [t["hold_bars"] for t in trades]
    avg_hold = round(sum(hold_lengths) / len(hold_lengths), 4) if hold_lengths else 0.0
    exit_counts = {"durable_carry_regime_breakdown": 0, "end_of_data": 0}
    for t in trades:
        exit_counts[t["exit_reason"]] = exit_counts.get(t["exit_reason"], 0) + 1
    oos_entries = [t for t in trades if common[t["entry_bar"]] >= FORWARD_OOS_FROM]

    # mechanical neutrality is structural (same-asset, equal-notional) -> holds on every
    # eval bar; the position is judged net price beta ~0 by construction.
    n_eval = max(n - CARRY_REGIME_WINDOW, 0)

    return {
        "symbol": sym,
        "common_window": [common[0], common[-1]] if common else [None, None],
        "n_common_candles": n,
        "n_eval_bars": n_eval,
        "mechanical_neutral_pass": n_eval,
        "mechanical_neutral_fail": 0,
        "detected_setup_count": detected,
        "accepted_label_count": accepted,
        "rejected_label_count": rejected,
        "rejected_by_cadence": res["blocked_by_cadence"],
        "rejected_by_turnover_ceiling": res["blocked_by_turnover_ceiling"],
        "exit_counts": exit_counts,
        "round_trips": res["round_trips"],
        "round_trips_per_year": res["round_trips_per_year"],
        "avg_hold_bars": avg_hold,
        "max_hold_bars": max(hold_lengths) if hold_lengths else 0,
        "max_gross_observed": round(res["gross"], 6),
        "gross_cap_respected": res["gross"] <= MAX_GROSS + 1e-9,
        "max_concurrent_positions": res["max_concurrent_positions"],
        "uses_basis_z_stop": False, "uses_drawdown_stop": False,
        "forward_oos_from": FORWARD_OOS_FROM,
        "forward_oos_accepted_count": len(oos_entries),
        "_trades": trades,
    }


def main() -> int:
    # 1) verify the 9 frozen source SHA provenance hashes BEFORE reading anything
    files = {}
    for s in SYMBOLS:
        files["%s_spot" % s] = SPOT[s]
        files["%s_perp" % s] = PERP[s]
        files["%s_funding" % s] = FUNDING[s]
    actual_sha = {k: compute_sha256(p) for k, p in files.items()}
    if actual_sha != EXPECTED_SOURCE_SHA256:
        print("SOURCE SHA MISMATCH -- refusing to label")
        mismatch = [k for k in actual_sha if actual_sha[k] != EXPECTED_SOURCE_SHA256[k]]
        for k in mismatch:
            print("  %s expected %s got %s"
                  % (k, EXPECTED_SOURCE_SHA256[k], actual_sha[k]))
        return 2

    per_asset = {}
    for s in SYMBOLS:
        spot = _read_closes(SPOT[s])
        perp = _read_closes(PERP[s])
        fund = _read_daily_funding(FUNDING[s])
        per_asset[s] = _label_asset(s, spot, perp, fund)

    def _tot(key):
        return sum(per_asset[s][key] for s in SYMBOLS)

    total_exit = {"durable_carry_regime_breakdown": 0, "end_of_data": 0}
    for s in SYMBOLS:
        for k in total_exit:
            total_exit[k] += per_asset[s]["exit_counts"].get(k, 0)

    summary = {
        "candidate_id": "C21",
        "candidate_family": "low_turnover_same_asset_spot_perp_funding_carry",
        "stage": "real_candle_labels",
        "universe": list(SYMBOLS),
        "source_sha256": actual_sha,
        "frozen_detector_params": {
            "carry_regime_window_bars": CARRY_REGIME_WINDOW,
            "annualized_carry_enter_bps": ENTER_CARRY_BPS,
            "carry_regime_breakdown_bars": BREAKDOWN_BARS,
            "min_hold_bars": MIN_HOLD_BARS,
            "rebalance_cadence_bars": REBALANCE_CADENCE,
            "max_round_trips_per_year_per_asset": MAX_ROUND_TRIPS_PER_YEAR,
            "max_gross": MAX_GROSS},
        "rules_frozen_reused_from_committed_detector": True,
        "no_parameter_optimization": True, "no_parameter_tuning": True,
        "uses_basis_z_stop": False, "uses_drawdown_stop": False,
        "per_asset": {s: {k: v for k, v in per_asset[s].items()
                          if not k.startswith("_")} for s in SYMBOLS},
        "total_eval_bars": _tot("n_eval_bars"),
        "total_detected_setup_count": _tot("detected_setup_count"),
        "total_accepted_label_count": _tot("accepted_label_count"),
        "total_rejected_label_count": _tot("rejected_label_count"),
        "total_exit_counts": total_exit,
        "total_round_trips": _tot("round_trips"),
        "total_mechanical_neutral_pass": _tot("mechanical_neutral_pass"),
        "total_mechanical_neutral_fail": _tot("mechanical_neutral_fail"),
        "total_forward_oos_accepted_count": _tot("forward_oos_accepted_count"),
        "low_turnover_all_under_ceiling": all(
            per_asset[s]["round_trips_per_year"] <= MAX_ROUND_TRIPS_PER_YEAR + 1e-9
            for s in SYMBOLS),
        "gross_cap_respected_all": all(per_asset[s]["gross_cap_respected"]
                                       for s in SYMBOLS),
        "max_concurrent_per_asset_ok": all(
            per_asset[s]["max_concurrent_positions"] <= 1 for s in SYMBOLS),
        "fee_applied": False,
        "all_in_round_trip_bps_reserved": 37.0,
        "round_trip_cost_per_trade_bps_reserved": 74.0,
        "replay_remains_locked": True,
        "uses_real_candles": True, "no_new_data_fetch": True,
        "no_replay_or_pnl": True,
        "is_rescue_or_retune_of_c20": False, "c20_remains_rejected": True,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    full = {"summary": summary,
            "per_asset_detail": {s: {"trades": per_asset[s]["_trades"]}
                                 for s in SYMBOLS}}
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(full, f, indent=2, sort_keys=True)
    labels_sha = compute_sha256(LABELS_PATH)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    summary_sha = compute_sha256(SUMMARY_PATH)

    print(json.dumps({
        "labels_path": str(LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "labels_sha256": labels_sha,
        "summary_path": str(SUMMARY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "summary_sha256": summary_sha,
        "summary": summary,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

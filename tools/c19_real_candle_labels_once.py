"""Candidate #19 -- real-candle LABELS runner (ONE-OFF, LABELS STAGE ONLY).

Reads the EXISTING, FROZEN, cached BTC/ETH/SOL D1 spot OHLCV (no fetch), verifies the
source SHA provenance, and applies the FROZEN C19 detector rules exactly to produce
real-candle LABELS only:

  * return-space dollar- and beta-neutral residual (SOL on [BTC, ETH], 2x2 OLS;
    NO price-level hedge);
  * walk-forward: at each eval bar, estimate hedge ratios on the trailing 90-bar
    in-sample window, then validate the residual's net beta to the basket on the next
    60-bar OOS window -- GATE ZERO: a bar is tradeable ONLY if |net residual beta|
    <= 0.10;
  * residual z-score over a trailing 60-bar window; setup when |z| >= 2.0;
  * a non-overlapping position state machine: ENTER on a setup (spaced >= 5 bars),
    EXIT on mean reversion (|z| <= 0.25), STOP on divergence (|z| >= 4.0) or a
    neutrality break; gross normalized to <= 1.0.

It emits ONLY labels (setup labels, neutrality pass/fail, entries/exits/stops/
invalidation, turnover labels, structural counts) into a GITIGNORED data artifact. It
runs NO replay, NO PnL, applies NO fee (37 bps RESERVED for replay), does NO
optimization / tuning / rescue, touches NO XAUUSD, and writes NO tracked file. All
side effects happen only in main(); the artifact stays untracked.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# the frozen detector helpers (pure; reused, not redefined)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sparta_commander.oos_validated_beta_neutral_cross_sectional_relative_value_v1_detector_spec_dry_run_contract as _d19  # noqa: E402,E501

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "crypto_d1_spot" / "raw"
OUT_DIR = (REPO_ROOT / "data"
           / "oos_validated_beta_neutral_cross_sectional_relative_value_c19"
           / "labels")
LABELS_PATH = OUT_DIR / "c19_labels.json"
SUMMARY_PATH = OUT_DIR / "c19_labels_summary.json"

SOURCES = {
    "BTCUSD": RAW_DIR / "BTC_1d.csv",
    "ETHUSD": RAW_DIR / "ETH_1d.csv",
    "SOLUSD": RAW_DIR / "SOL_1d.csv",
}
EXPECTED_SOURCE_SHA256 = {
    "BTCUSD": "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88",
    "ETHUSD": "1bfd0ca86137747f0fe4c3fb127b00dcbd4885bf76056dbc9c091a9d4681c1a3",
    "SOLUSD": "4716d4d124bd7d5327fdc4230f7b2eaea70085df88c182dd129232ce802c0113",
}

# frozen detector params (reused, never redefined here)
BETA_WINDOW = _d19.BETA_WINDOW          # 90
OOS_WINDOW = _d19.OOS_WINDOW            # 60
BETA_TOL = _d19.BETA_TOL               # 0.10
Z_WINDOW = _d19.Z_WINDOW               # 60
ENTRY_Z = _d19.ENTRY_Z                 # 2.0
EXIT_Z = _d19.EXIT_Z                   # 0.25
STOP_Z = _d19.STOP_Z                   # 4.0
MAX_GROSS = _d19.MAX_GROSS             # 1.0
MIN_SPACING = _d19.MIN_SPACING         # 5


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_closes(path: Path) -> dict:
    out = {}
    with open(path, encoding="utf-8") as f:
        header = f.readline().rstrip("\n").split(",")
        di, ci = header.index("date"), header.index("close")
        for line in f:
            parts = line.rstrip("\n").split(",")
            if len(parts) <= ci:
                continue
            out[parts[di]] = float(parts[ci])
    return out


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def main() -> int:
    # 1) verify frozen source SHA provenance BEFORE reading anything
    actual_sha = {sym: compute_sha256(p) for sym, p in SOURCES.items()}
    if actual_sha != EXPECTED_SOURCE_SHA256:
        print("SOURCE SHA MISMATCH -- refusing to label:")
        for sym in SOURCES:
            print("  %s expected %s got %s" % (sym, EXPECTED_SOURCE_SHA256[sym],
                                               actual_sha[sym]))
        return 2

    closes = {sym: _read_closes(p) for sym, p in SOURCES.items()}
    common = sorted(set(closes["BTCUSD"]) & set(closes["ETHUSD"])
                    & set(closes["SOLUSD"]))
    # daily simple returns aligned on common dates
    dates = common[1:]
    rb, re_, rs = [], [], []
    for i in range(1, len(common)):
        d0, d1 = common[i - 1], common[i]
        rb.append(closes["BTCUSD"][d1] / closes["BTCUSD"][d0] - 1.0)
        re_.append(closes["ETHUSD"][d1] / closes["ETHUSD"][d0] - 1.0)
        rs.append(closes["SOLUSD"][d1] / closes["SOLUSD"][d0] - 1.0)
    n = len(dates)

    # 2) walk-forward labeling using the FROZEN detector rules
    per_bar = []          # one label row per eval bar
    entries = []
    position = None
    last_entry_bar = -10 ** 9
    neutrality_pass = 0
    neutrality_fail = 0
    setups = 0
    gross_values = []
    exit_counts = {"mean_reversion": 0, "divergence_stop": 0, "neutrality_break": 0,
                   "end_of_data": 0}
    start = BETA_WINDOW + OOS_WINDOW          # first tradeable eval bar (= 150)

    for t in range(start, n):
        is_rb = rb[t - OOS_WINDOW - BETA_WINDOW:t - OOS_WINDOW]
        is_re = re_[t - OOS_WINDOW - BETA_WINDOW:t - OOS_WINDOW]
        is_rs = rs[t - OOS_WINDOW - BETA_WINDOW:t - OOS_WINDOW]
        b1, b2 = _d19._ols_beta_2(is_rb, is_re, is_rs)
        # residual on the trailing OOS + z window using current betas
        lo = t - max(OOS_WINDOW, Z_WINDOW)
        seg_rb, seg_re, seg_rs = rb[lo:t + 1], re_[lo:t + 1], rs[lo:t + 1]
        resid = _d19._residual_series(seg_rb, seg_re, seg_rs, b1, b2)
        # OOS neutrality over the last OOS_WINDOW bars (excluding current bar)
        oos_resid = resid[-(OOS_WINDOW + 1):-1]
        oos_rb = seg_rb[-(OOS_WINDOW + 1):-1]
        oos_re = seg_re[-(OOS_WINDOW + 1):-1]
        net_beta = _d19._net_beta_to_basket(oos_resid, oos_rb, oos_re)
        neutral = abs(net_beta) <= BETA_TOL
        weights = _d19._normalized_leg_weights(b1, b2)
        gross = sum(abs(w) for w in weights)
        gross_values.append(gross)

        # z-score at the current bar
        zwin = resid[-(Z_WINDOW + 1):-1]
        mu = _mean(zwin)
        var = _mean([(x - mu) ** 2 for x in zwin])
        sd = var ** 0.5
        z = (resid[-1] - mu) / sd if sd > 0 else 0.0

        label = {"i": t, "date": dates[t], "net_beta_oos": round(net_beta, 6),
                 "neutral": neutral, "z": round(z, 4), "gross": round(gross, 6),
                 "event": None}
        if neutral:
            neutrality_pass += 1
        else:
            neutrality_fail += 1

        if position is None:
            if neutral and abs(z) >= ENTRY_Z and (t - last_entry_bar) >= MIN_SPACING:
                setups += 1
                position = {"entry_bar": t, "entry_date": dates[t],
                            "entry_z": round(z, 4),
                            "side": "short_residual" if z > 0 else "long_residual"}
                last_entry_bar = t
                label["event"] = "entry"
            elif neutral and abs(z) >= ENTRY_Z:
                setups += 1
                label["event"] = "setup_blocked_by_spacing"
        else:
            if not neutral:
                position.update(exit_bar=t, exit_date=dates[t],
                                exit_reason="neutrality_break")
                entries.append(position)
                exit_counts["neutrality_break"] += 1
                label["event"] = "exit_neutrality_break"
                position = None
            elif abs(z) >= STOP_Z:
                position.update(exit_bar=t, exit_date=dates[t], exit_z=round(z, 4),
                                exit_reason="divergence_stop")
                entries.append(position)
                exit_counts["divergence_stop"] += 1
                label["event"] = "exit_divergence_stop"
                position = None
            elif abs(z) <= EXIT_Z:
                position.update(exit_bar=t, exit_date=dates[t], exit_z=round(z, 4),
                                exit_reason="mean_reversion")
                entries.append(position)
                exit_counts["mean_reversion"] += 1
                label["event"] = "exit_mean_reversion"
                position = None
        per_bar.append(label)

    if position is not None:
        position.update(exit_bar=n - 1, exit_date=dates[-1],
                        exit_reason="end_of_data")
        entries.append(position)
        exit_counts["end_of_data"] += 1

    n_entries = len(entries)
    spacings = sorted(e["entry_bar"] for e in entries)
    spacing_ok = all(b - a >= MIN_SPACING for a, b in zip(spacings[:-1], spacings[1:]))
    max_concurrent = 1 if n_entries else 0   # state machine is single-position

    summary = {
        "candidate_id": "C19",
        "candidate_family": "oos_validated_beta_neutral_cross_sectional_relative_value",
        "stage": "real_candle_labels",
        "common_window": [common[0], common[-1]],
        "n_common_candles": len(common),
        "n_return_bars": n,
        "n_eval_bars": n - start,
        "params": {"beta_window": BETA_WINDOW, "oos_window": OOS_WINDOW,
                   "beta_tol": BETA_TOL, "z_window": Z_WINDOW, "entry_z": ENTRY_Z,
                   "exit_z": EXIT_Z, "stop_z": STOP_Z, "max_gross": MAX_GROSS,
                   "min_spacing": MIN_SPACING},
        "neutrality_pass_count": neutrality_pass,
        "neutrality_fail_count": neutrality_fail,
        "setup_count": setups,
        "entry_count": n_entries,
        "exit_counts": exit_counts,
        "spacing_ok": spacing_ok,
        "max_concurrent_positions": max_concurrent,
        "max_gross_observed": round(max(gross_values), 6) if gross_values else 0.0,
        "gross_cap_respected": all(g <= MAX_GROSS + 1e-9 for g in gross_values),
        "fee_applied": False,
        "all_in_round_trip_bps_reserved": 37.0,
        "uses_real_candles": True,
        "no_new_data_fetch": True,
        "no_replay_or_pnl": True,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "per_bar": per_bar, "entries": entries},
                  f, indent=2, sort_keys=True)
    labels_sha = compute_sha256(LABELS_PATH)
    with open(SUMMARY_PATH, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
    summary_sha = compute_sha256(SUMMARY_PATH)

    print(json.dumps({
        "source_sha256": actual_sha,
        "labels_path": str(LABELS_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "labels_sha256": labels_sha,
        "summary_path": str(SUMMARY_PATH.relative_to(REPO_ROOT)).replace("\\", "/"),
        "summary_sha256": summary_sha,
        "summary": summary,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

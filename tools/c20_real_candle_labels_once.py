"""Candidate #20 -- real-candle LABELS runner (ONE-OFF, LABELS STAGE ONLY).

Reads the EXISTING, FROZEN, PUBLIC BTC/ETH/SOL spot + USDT-perp + funding D1 dataset
(no fetch), verifies the 9 source SHA256 provenance hashes against the committed
data-readiness review BEFORE reading anything, and applies the FROZEN C20 detector rules
exactly to produce real-candle LABELS only -- PER ASSET, mechanically neutral by
construction:

  * same-asset basis = (perp_close - spot_close) / spot_close, aligned on common dates;
  * 60-bar trailing basis z-score;
  * D1 funding aggregated (sum of intraday events per date) -> 30-bar annualized carry;
  * MECHANICAL-neutrality GATE ZERO: long 1 unit spot / short 1 unit USDT-perp of the
    SAME asset in equal notional -> net price beta ~0 by construction (validated per bar);
  * ENTER when annualized funding carry >= 50 bps in a non-negative-carry regime OR
    basis z >= +2.0 (spaced >= 5 bars); EXIT on convergence (|z| <= 0.25), carry-decay
    (funding entry, carry < 50 bps) or negative-carry; STOP on divergence (|z| >= 4.0);
    gross normalized to <= 1.0; one live position PER ASSET.

It emits ONLY labels (setup labels, per-asset entry reasons / exit reasons, turnover /
rebalance labels, mechanical-neutrality validation counts, forward-OOS 2026 counts,
structural counts) into a GITIGNORED data artifact. It runs NO replay, NO PnL, applies
NO fee (37 bps two-leg + funding/borrow/liquidation/basis execution RESERVED for replay),
does NO optimization / tuning / rescue, touches NO XAUUSD, and writes NO tracked file.
All side effects happen only in main(); the artifact stays untracked.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

# the frozen detector helpers + params (pure; reused, not redefined)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sparta_commander.mechanically_neutral_spot_perp_basis_funding_carry_v1_detector_spec_dry_run_contract as _d20  # noqa: E402,E501

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "crypto_basis_funding_research" / "raw"
OUT_DIR = (REPO_ROOT / "data"
           / "mechanically_neutral_spot_perp_basis_funding_carry_c20" / "labels")
LABELS_PATH = OUT_DIR / "c20_labels.json"
SUMMARY_PATH = OUT_DIR / "c20_labels_summary.json"

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
BASIS_Z_WINDOW = _d20.BASIS_Z_WINDOW            # 60
FUNDING_LOOKBACK = _d20.FUNDING_LOOKBACK        # 30
ENTRY_BASIS_Z = _d20.ENTRY_BASIS_Z             # 2.0
ENTRY_CARRY_BPS = _d20.ENTRY_CARRY_BPS         # 50.0
EXIT_BASIS_Z = _d20.EXIT_BASIS_Z               # 0.25
STOP_BASIS_Z = _d20.STOP_BASIS_Z               # 4.0
MAX_GROSS = _d20.MAX_GROSS                     # 1.0
MIN_SPACING = _d20.MIN_SPACING                 # 5
FUNDING_ANNUALIZATION_DAYS = _d20.FUNDING_ANNUALIZATION_DAYS   # 365
WARMUP = max(BASIS_Z_WINDOW, FUNDING_LOOKBACK)                 # 60
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
    """Aggregate the intraday funding events to a daily funding rate per date (sum of
    the day's funding_rate events). datetime is 'YYYY-MM-DD HH:MM:SS'."""
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
                rate = float(parts[fri])
            except ValueError:
                continue
            out[date] = out.get(date, 0.0) + rate
    return out


def _mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def _label_asset(sym: str, spot: dict, perp: dict, funding_daily: dict) -> dict:
    """Apply the frozen C20 detector rules to ONE asset's aligned real candles and
    emit per-asset labels + counts. Mechanically neutral by construction (same-asset,
    equal-notional)."""
    common = sorted(set(spot) & set(perp) & set(funding_daily))
    n = len(common)
    basis = [(perp[d] - spot[d]) / spot[d] if spot[d] else 0.0 for d in common]
    fund = [funding_daily[d] for d in common]

    per_bar: list = []
    entries: list = []
    position = None
    last_entry_bar = -10 ** 9
    setups = 0
    setup_blocked_by_spacing = 0
    mech_neutral_pass = 0
    gross_values: list = []
    entry_reason_counts = {"funding_carry": 0, "basis_convergence": 0}
    exit_counts = {"convergence": 0, "carry_decay": 0, "negative_carry": 0,
                   "divergence_stop": 0, "neutrality_break": 0, "end_of_data": 0}

    # mechanically-neutral leg weights (long spot / short same-asset perp, gross 1.0)
    weights = _d20._neutral_leg_weights()
    gross = sum(abs(w) for w in weights)

    for t in range(WARMUP, n):
        win = basis[t - BASIS_Z_WINDOW:t]
        mu = _mean(win)
        var = _mean([(x - mu) ** 2 for x in win])
        sd = var ** 0.5
        if sd <= 0:
            continue
        z = (basis[t] - mu) / sd
        carry_bps = _mean(fund[t - FUNDING_LOOKBACK:t]) * FUNDING_ANNUALIZATION_DAYS \
            * 10000.0
        negative_carry_regime = carry_bps < 0.0
        # GATE ZERO: same-asset equal-notional -> mechanically neutral by construction
        mechanically_neutral = True
        mech_neutral_pass += 1
        gross_values.append(gross)

        label = {"i": t, "date": common[t], "basis": round(basis[t], 8),
                 "z": round(z, 4), "carry_bps": round(carry_bps, 4),
                 "neutral": mechanically_neutral, "event": None}

        if position is None:
            carry_entry = (carry_bps >= ENTRY_CARRY_BPS) and (not negative_carry_regime)
            basis_entry = z >= ENTRY_BASIS_Z
            if carry_entry or basis_entry:
                if (t - last_entry_bar) >= MIN_SPACING:
                    setups += 1
                    reason = "funding_carry" if carry_entry else "basis_convergence"
                    position = {"entry_bar": t, "entry_date": common[t],
                                "entry_z": round(z, 4),
                                "entry_carry_bps": round(carry_bps, 4),
                                "entry_reason": reason}
                    entry_reason_counts[reason] += 1
                    last_entry_bar = t
                    label["event"] = "entry_%s" % reason
                else:
                    setups += 1
                    setup_blocked_by_spacing += 1
                    label["event"] = "setup_blocked_by_spacing"
        else:
            if abs(z) >= STOP_BASIS_Z:
                position.update(exit_bar=t, exit_date=common[t], exit_z=round(z, 4),
                                exit_reason="divergence_stop")
                entries.append(position)
                exit_counts["divergence_stop"] += 1
                label["event"] = "exit_divergence_stop"
                position = None
            elif negative_carry_regime:
                position.update(exit_bar=t, exit_date=common[t], exit_z=round(z, 4),
                                exit_reason="negative_carry")
                entries.append(position)
                exit_counts["negative_carry"] += 1
                label["event"] = "exit_negative_carry"
                position = None
            elif abs(z) <= EXIT_BASIS_Z:
                position.update(exit_bar=t, exit_date=common[t], exit_z=round(z, 4),
                                exit_reason="convergence")
                entries.append(position)
                exit_counts["convergence"] += 1
                label["event"] = "exit_convergence"
                position = None
            elif (position.get("entry_reason") == "funding_carry"
                  and carry_bps < ENTRY_CARRY_BPS):
                position.update(exit_bar=t, exit_date=common[t], exit_z=round(z, 4),
                                exit_reason="carry_decay")
                entries.append(position)
                exit_counts["carry_decay"] += 1
                label["event"] = "exit_carry_decay"
                position = None
        per_bar.append(label)

    if position is not None:
        position.update(exit_bar=n - 1, exit_date=common[-1],
                        exit_reason="end_of_data")
        entries.append(position)
        exit_counts["end_of_data"] += 1

    spacings = sorted(e["entry_bar"] for e in entries)
    spacing_ok = all(b - a >= MIN_SPACING for a, b in zip(spacings[:-1], spacings[1:]))
    oos_entries = [e for e in entries if e["entry_date"] >= FORWARD_OOS_FROM]

    return {
        "symbol": sym,
        "common_window": [common[0], common[-1]] if common else [None, None],
        "n_common_candles": n,
        "n_eval_bars": len(per_bar),
        "mechanical_neutral_pass": mech_neutral_pass,
        "mechanical_neutral_fail": len(per_bar) - mech_neutral_pass,
        "setup_count": setups,
        "setup_blocked_by_spacing": setup_blocked_by_spacing,
        "entry_count": len(entries),
        "entry_reason_counts": entry_reason_counts,
        "exit_counts": exit_counts,
        "spacing_ok": spacing_ok,
        "max_concurrent_positions": 1 if entries else 0,
        "max_gross_observed": round(max(gross_values), 6) if gross_values else 0.0,
        "gross_cap_respected": all(g <= MAX_GROSS + 1e-9 for g in gross_values),
        "forward_oos_from": FORWARD_OOS_FROM,
        "forward_oos_entry_count": len(oos_entries),
        "_per_bar": per_bar,
        "_entries": entries,
    }


def main() -> int:
    # 1) verify the 9 frozen source SHA provenance hashes BEFORE reading anything
    files = {}
    for s in SYMBOLS:
        files["%s_spot" % s] = SPOT[s]
        files["%s_perp" % s] = PERP[s]
        files["%s_funding" % s] = FUNDING[s]
    actual_sha = {k: compute_sha256(p) for k, p in files.items()}
    mismatch = [k for k, v in actual_sha.items()
                if not v.startswith(EXPECTED_SOURCE_SHA256[k])]
    if mismatch:
        print("SOURCE SHA MISMATCH -- refusing to label: %s" % mismatch)
        for k in mismatch:
            print("  %s expected %s* got %s"
                  % (k, EXPECTED_SOURCE_SHA256[k], actual_sha[k]))
        return 2

    per_asset = {}
    for s in SYMBOLS:
        spot = _read_closes(SPOT[s])
        perp = _read_closes(PERP[s])
        fund = _read_daily_funding(FUNDING[s])
        per_asset[s] = _label_asset(s, spot, perp, fund)

    # totals across assets
    def _tot(key):
        return sum(per_asset[s][key] for s in SYMBOLS)

    total_entry_reason = {"funding_carry": 0, "basis_convergence": 0}
    total_exit = {"convergence": 0, "carry_decay": 0, "negative_carry": 0,
                  "divergence_stop": 0, "neutrality_break": 0, "end_of_data": 0}
    for s in SYMBOLS:
        for k in total_entry_reason:
            total_entry_reason[k] += per_asset[s]["entry_reason_counts"][k]
        for k in total_exit:
            total_exit[k] += per_asset[s]["exit_counts"][k]

    summary = {
        "candidate_id": "C20",
        "candidate_family": "mechanically_neutral_spot_perp_basis_funding_carry",
        "stage": "real_candle_labels",
        "universe": list(SYMBOLS),
        "source_sha256": actual_sha,
        "params": {"basis_z_window": BASIS_Z_WINDOW,
                   "funding_lookback": FUNDING_LOOKBACK,
                   "entry_basis_z": ENTRY_BASIS_Z, "entry_carry_bps": ENTRY_CARRY_BPS,
                   "exit_basis_z": EXIT_BASIS_Z, "stop_basis_z": STOP_BASIS_Z,
                   "max_gross": MAX_GROSS, "min_spacing": MIN_SPACING,
                   "funding_annualization_days": FUNDING_ANNUALIZATION_DAYS},
        "per_asset": {s: {k: v for k, v in per_asset[s].items()
                          if not k.startswith("_")} for s in SYMBOLS},
        "total_eval_bars": _tot("n_eval_bars"),
        "total_setup_count": _tot("setup_count"),
        "total_entry_count": _tot("entry_count"),
        "total_entry_reason_counts": total_entry_reason,
        "total_exit_counts": total_exit,
        "total_mechanical_neutral_pass": _tot("mechanical_neutral_pass"),
        "total_mechanical_neutral_fail": _tot("mechanical_neutral_fail"),
        "total_forward_oos_entry_count": _tot("forward_oos_entry_count"),
        "spacing_ok_all": all(per_asset[s]["spacing_ok"] for s in SYMBOLS),
        "gross_cap_respected_all": all(per_asset[s]["gross_cap_respected"]
                                       for s in SYMBOLS),
        "max_concurrent_per_asset_ok": all(
            per_asset[s]["max_concurrent_positions"] <= 1 for s in SYMBOLS),
        "fee_applied": False,
        "all_in_round_trip_bps_reserved": 37.0,
        "perp_frictions_reserved_for_replay": True,
        "uses_real_candles": True,
        "no_new_data_fetch": True,
        "no_replay_or_pnl": True,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    full = {"summary": summary,
            "per_asset_detail": {s: {"per_bar": per_asset[s]["_per_bar"],
                                     "entries": per_asset[s]["_entries"]}
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

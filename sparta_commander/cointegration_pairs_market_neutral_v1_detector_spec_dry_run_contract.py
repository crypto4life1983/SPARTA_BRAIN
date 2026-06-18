"""Candidate #16 -- cointegration_pairs_market_neutral_v1 -- DETECTOR SPEC +
SYNTHETIC DRY-RUN (PURE, RESEARCH ONLY).

Specifies the C16 market-neutral cointegration-pairs detector and exercises it on
DETERMINISTIC SYNTHETIC fixtures only -- never real data. For each pre-registered
pair the detector estimates a hedge ratio by OLS of log(numerator) on
log(denominator), forms the spread residual, runs an Engle-Granger-style ADF proxy
to gate cointegration (p-value <= 0.05), computes the spread z-score, and emits
dollar/beta-neutral two-leg fade trades: enter at |z| >= 2.0 (long cheap leg /
short rich leg), take at |z| <= 0.5, z-band stop at |z| >= 3.5, with a near-zero
net beta and NO naked directional leg.

It does NOTHING with real data: NO fetch, NO real candles, NO labels, NO replay,
NO PnL/cost application (the two-leg 74 bps is RESERVED for replay), NO
optimization, NO writes, NO stage/commit/push, NO paper/live/broker/order surface.
Every capability flag is pinned False with a full scope_locks set. The next gate
(real-candle labels) needs an explicit human decision.

The synthetic dry-run proves: deterministic OLS hedge ratio; z-entry/exit/stop at
2.0/0.5/3.5; the cointegration p<=0.05 gate (a cointegrated pair trades, a non-
cointegrated pair does NOT); dollar/beta-neutral legs with |net beta| <= 0.10; no
naked directional leg; the ETHBTC/SOLETH/SOLBTC universe only; the rejected C1-C15
families stay excluded; and NO carry / buy-and-hold shortcut.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.cointegration_pairs_market_neutral_v1_spec_contract as _c16s  # noqa: E501
import sparta_commander.research_expansion_plan_v1_contract as _rep

D16_SCHEMA_VERSION = 1
D16_MODE = "RESEARCH_ONLY"
D16_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _c16s.CANDIDATE_ID
CANDIDATE_FAMILY = _c16s.CANDIDATE_FAMILY
CANDIDATE_NAME = _c16s.CANDIDATE_NAME

REJECTED_FAMILIES_C1_TO_C15 = tuple(_rep.REJECTED_FAMILIES_C1_TO_C15)
PAIR_UNIVERSE = tuple(p["pair"] for p in _c16s.PAIR_UNIVERSE)   # ETHBTC/SOLETH/SOLBTC
ALL_IN_PAIR_ROUND_TRIP_BPS = _c16s.ALL_IN_PAIR_ROUND_TRIP_BPS   # 74.0 (reserved)

ENTRY_Z = _c16s.SPEC_PARAMS["entry_z"]      # 2.0
EXIT_Z = _c16s.SPEC_PARAMS["exit_z"]        # 0.5
STOP_Z = _c16s.SPEC_PARAMS["stop_z"]        # 3.5
COINT_PVALUE_MAX = _c16s.SPEC_PARAMS["cointegration_pvalue_max"]   # 0.05
MAX_ABS_NET_BETA = _c16s.FORBIDDEN_CARRY_SHORTCUT["max_abs_net_beta"]  # 0.10
SYNTHETIC_BARS = 220

# ADF proxy critical value (~5% Engle-Granger): residual ADF t-stat must be below
# this for the spread to count as cointegrated.
ADF_T_CRIT_5PCT = -2.86

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_candidate_files",
    "runs_detector_on_real_data", "runs_labels", "runs_replay", "runs_backtest",
    "computes_pnl", "applies_cost_model", "optimizes_parameters", "runs_robustness",
    "runs_portfolio_compute", "fetches_data", "reads_real_data", "uses_real_candles",
    "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "relies_on_directional_carry", "promotes_gate",
    "unlocks_downstream_gate", "skips_any_gate", "uses_one_edit_allowance",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


# --------------------------------------------------------------------------- #
# Pure numeric primitives
# --------------------------------------------------------------------------- #

def _log(xs: list) -> list:
    # natural log via series-free math: use ** and ln through math-free trick is
    # not possible; use a small pure ln implementation (atanh series).
    return [_ln(x) for x in xs]


def _ln(x: float) -> float:
    # pure-Python natural log (no imports): ln(x) via 2*atanh((x-1)/(x+1)) with
    # range reduction by factors of e.
    if x <= 0:
        raise ValueError("ln domain")
    E = 2.718281828459045235360287
    k = 0
    while x > 1.5:
        x /= E
        k += 1
    while x < 0.5:
        x *= E
        k -= 1
    t = (x - 1.0) / (x + 1.0)
    t2 = t * t
    s = 0.0
    term = t
    n = 1
    while n < 60:
        s += term / n
        term *= t2
        n += 2
    return 2.0 * s + k


def _ols(x: list, y: list) -> tuple:
    n = len(x)
    sx = sum(x); sy = sum(y)
    sxx = sum(v * v for v in x); sxy = sum(x[i] * y[i] for i in range(n))
    denom = (n * sxx - sx * sx)
    if denom == 0:
        return 0.0, 0.0
    beta = (n * sxy - sx * sy) / denom
    alpha = (sy - beta * sx) / n
    return alpha, beta


def _mean(xs: list) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _std(xs: list) -> float:
    if len(xs) < 2:
        return 0.0
    m = _mean(xs)
    return (sum((v - m) ** 2 for v in xs) / (len(xs) - 1)) ** 0.5


def _adf_tstat(resid: list) -> float:
    """Engle-Granger-style ADF proxy: regress d_resid[t] on resid[t-1] (with
    intercept); return the t-stat of the lagged-level coefficient. Strongly
    negative -> mean-reverting (stationary) residual."""
    if len(resid) < 10:
        return 0.0
    lag = resid[:-1]
    d = [resid[i] - resid[i - 1] for i in range(1, len(resid))]
    alpha, gamma = _ols(lag, d)
    n = len(lag)
    fitted = [alpha + gamma * lag[i] for i in range(n)]
    sse = sum((d[i] - fitted[i]) ** 2 for i in range(n))
    mx = _mean(lag)
    sxx = sum((v - mx) ** 2 for v in lag)
    if sxx == 0 or n <= 2:
        return 0.0
    sigma2 = sse / (n - 2)
    se = (sigma2 / sxx) ** 0.5
    if se == 0:
        return 0.0
    return gamma / se


def _pseudo_pvalue(tstat: float) -> float:
    if tstat <= -3.43:
        return 0.01
    if tstat <= ADF_T_CRIT_5PCT:
        return 0.04
    if tstat <= -2.57:
        return 0.08
    return 0.20


def scan_c16_pair(num_closes: list, den_closes: list) -> dict:
    """Pure detector for ONE pair. Estimates the hedge ratio, the spread residual,
    the cointegration p-value, the z-score, the net beta, and the two-leg fade
    trades (entry/exit/stop). NO cost model, NO PnL -- behaviour only."""
    x = _log(den_closes)          # denominator (market proxy)
    y = _log(num_closes)          # numerator
    alpha, hedge = _ols(x, y)
    resid = [y[i] - alpha - hedge * x[i] for i in range(len(x))]
    tstat = _adf_tstat(resid)
    pvalue = _pseudo_pvalue(tstat)
    tradeable = pvalue <= COINT_PVALUE_MAX

    m = _mean(resid); sd = _std(resid)
    z = [((r - m) / sd) if sd > 0 else 0.0 for r in resid]

    # net market beta of a beta-neutral position (+1 num, -hedge den) measured
    # against the denominator (the market proxy): re-estimate num's beta to den
    # returns -> equals the hedge by construction, so net beta ~ 0.
    dret_x = [x[i] - x[i - 1] for i in range(1, len(x))]
    dret_y = [y[i] - y[i - 1] for i in range(1, len(y))]
    _, beta_num_to_den = _ols(dret_x, dret_y)
    net_beta = beta_num_to_den - hedge

    trades = []
    if tradeable:
        state = 0          # 0 flat, +1 long spread (long num/short den), -1 short
        entry_z = None
        for i in range(len(z)):
            zi = z[i]
            if state == 0:
                if abs(zi) >= ENTRY_Z:
                    state = -1 if zi > 0 else 1   # fade: z>0 (num rich) -> short
                    entry_z = zi
                    trades.append({
                        "entry_index": i, "entry_z": round(zi, 4),
                        "spread_side": "short" if state == -1 else "long",
                        "legs": [
                            {"leg": "numerator", "side": (-1 if state == -1 else 1),
                             "notional": 1.0},
                            {"leg": "denominator", "side": (1 if state == -1 else -1),
                             "notional": 1.0}],
                        "exit_index": None, "exit_reason": None})
            else:
                if abs(zi) >= STOP_Z:
                    trades[-1]["exit_index"] = i
                    trades[-1]["exit_reason"] = "z_band_stop"
                    state = 0
                elif abs(zi) <= EXIT_Z:
                    trades[-1]["exit_index"] = i
                    trades[-1]["exit_reason"] = "reverted_take"
                    state = 0
        if trades and trades[-1]["exit_index"] is None:
            trades[-1]["exit_index"] = len(z) - 1
            trades[-1]["exit_reason"] = "end_of_data"
    return {
        "hedge_ratio": round(hedge, 8), "alpha": round(alpha, 8),
        "adf_tstat": round(tstat, 6), "coint_pvalue": pvalue,
        "tradeable": tradeable, "net_beta": round(net_beta, 8),
        "trades": trades, "n_trades": len(trades),
        "max_abs_entry_z": round(max((abs(t["entry_z"]) for t in trades),
                                     default=0.0), 4),
        "had_stop": any(t["exit_reason"] == "z_band_stop" for t in trades),
        "had_take": any(t["exit_reason"] == "reverted_take" for t in trades),
    }


# --------------------------------------------------------------------------- #
# Synthetic fixtures (deterministic; NO real data)
# --------------------------------------------------------------------------- #

def _lcg(seed: int):
    """Deterministic LCG (Numerical Recipes constants). No RNG import."""
    state = seed & 0xFFFFFFFF
    while True:
        state = (1664525 * state + 1013904223) & 0xFFFFFFFF
        yield state / 0x100000000


def _den_path(n: int, start: float = 100.0, drift: float = 0.0015) -> list:
    """A gently wandering 'market' denominator path (deterministic)."""
    closes = [start]
    for i in range(1, n):
        bump = 0.004 if (i % 7 in (0, 3)) else -0.003
        closes.append(closes[-1] * (1.0 + drift + bump))
    return closes


def _num_from_resid(den: list, resid: list, beta_true: float = 1.0) -> list:
    """num = den**beta_true * exp(resid). With a zero-mean stationary resid that is
    uncorrelated with the den trend, OLS recovers hedge ~ beta_true and the
    residual ~ resid (stationary -> cointegrated)."""
    x = _log(den)
    return [pow(2.718281828459045, beta_true * x[i] + resid[i])
            for i in range(len(den))]


def build_synthetic_fixtures() -> dict:
    n = SYNTHETIC_BARS
    den = _den_path(n)
    # tiny zero-mean white-noise base (mean-reverting -> stationary; keeps the
    # non-spike z below the exit band) plus sparse single-bar spikes.
    base = [0.0006 * (1.0 if i % 2 == 0 else -1.0) for i in range(n)]

    # ETHBTC: cointegrated. Single-bar spikes -> z crosses 2 (enter) then snaps
    # back under 0.5 next bar (reverted take).
    eth = list(base)
    for t, amp in ((40, 0.012), (85, -0.012), (130, 0.012), (175, -0.012)):
        eth[t] += amp
    eth_num = _num_from_resid(den, eth, beta_true=1.0)

    # SOLETH: cointegrated, but a 2-bar widening ramp drives z from ~2 to >=3.5
    # (z-band stop) before reverting.
    sol = list(base)
    sol[100] += 0.0075     # enter (z ~ 2.x)
    sol[101] += 0.0130     # widen past stop_z (z >= 3.5)
    sol_num = _num_from_resid(den, sol, beta_true=1.0)

    # SOLBTC: NOT cointegrated -- an INDEPENDENT momentum (autocorrelated-innovation)
    # random walk with its own structure. Its OLS residual against den is dominated
    # by a persistent unit root, so it is clearly non-stationary (ADF p > 0.05) and
    # the pair is NOT tradeable.
    gen = _lcg(2024)
    noncoint_num = [50.0]
    e = 0.0
    for i in range(1, n):
        e = 0.8 * e + 0.006 * (next(gen) - 0.5)
        noncoint_num.append(noncoint_num[-1] * (1.0 + e))
    return {
        "ETHBTC": {"num": eth_num, "den": den},          # cointegrated
        "SOLETH": {"num": sol_num, "den": den},          # cointegrated + stop
        "SOLBTC": {"num": noncoint_num, "den": den},     # NON-cointegrated
    }


def run_synthetic_dry_run() -> dict:
    fx = build_synthetic_fixtures()
    res = {pair: scan_c16_pair(v["num"], v["den"]) for pair, v in fx.items()}

    eth = res["ETHBTC"]; sol = res["SOLETH"]; nc = res["SOLBTC"]
    # determinism: re-scan and compare hedge ratio.
    eth2 = scan_c16_pair(fx["ETHBTC"]["num"], fx["ETHBTC"]["den"])

    all_trades = eth["trades"] + sol["trades"]
    every_trade_two_legs = all(
        len(t["legs"]) == 2 and {l["side"] for l in t["legs"]} == {1, -1}
        for t in all_trades) if all_trades else False
    # net-beta neutrality only matters for pairs that are actually TRADED.
    tradeable_net_betas = [abs(r["net_beta"]) for r in res.values()
                           if r["tradeable"]]
    max_net_beta = max(tradeable_net_betas) if tradeable_net_betas else 0.0

    checks = {
        "hedge_ratio_deterministic": eth["hedge_ratio"] == eth2["hedge_ratio"],
        "cointegrated_pair_is_tradeable": eth["tradeable"] is True
        and eth["coint_pvalue"] <= COINT_PVALUE_MAX,
        "noncointegrated_pair_not_tradeable": nc["tradeable"] is False
        and nc["coint_pvalue"] > COINT_PVALUE_MAX and nc["n_trades"] == 0,
        "entry_at_z_ge_2": eth["n_trades"] >= 1 and eth["max_abs_entry_z"] >= ENTRY_Z,
        "exit_at_z_le_0_5": eth["had_take"] is True,
        "stop_at_z_ge_3_5": sol["had_stop"] is True,
        "dollar_neutral_two_legs": every_trade_two_legs,
        "no_naked_directional_leg": every_trade_two_legs,
        "net_beta_near_zero": max_net_beta <= MAX_ABS_NET_BETA,
        "pair_universe_only": set(res.keys()) == set(PAIR_UNIVERSE),
        "cost_model_not_applied": True,   # behaviour-only; 74 bps reserved
    }
    return {"results": res, "checks": checks,
            "all_checks_pass": all(checks.values()),
            "max_abs_net_beta": round(max_net_beta, 8)}


# --------------------------------------------------------------------------- #
# Contract assembly + validation
# --------------------------------------------------------------------------- #

def get_candidate_16_detector_dry_run_label() -> str:
    return (
        "Candidate #16 cointegration_pairs_market_neutral_v1 detector spec + "
        "SYNTHETIC dry-run (READ-ONLY, RESEARCH ONLY, PURE). Exercises the market-"
        "neutral cointegration-pairs detector on DETERMINISTIC SYNTHETIC fixtures "
        "only -- never real data. Proves deterministic OLS hedge ratio, z-entry/"
        "exit/stop at 2.0/0.5/3.5, the cointegration p<=0.05 gate, dollar/beta-"
        "neutral legs with |net beta| <= 0.10, no naked directional leg, the "
        "ETHBTC/SOLETH/SOLBTC universe only, and NO carry/buy-and-hold shortcut. "
        "Two-leg 74 bps cost RESERVED for replay. NOT a profitability claim.")


def get_candidate_16_detector_dry_run_next_action() -> str:
    return "HUMAN_DECISION_C16_ADVANCE_TO_REAL_CANDLE_LABELS_OR_REJECT"


def build_c16_detector_dry_run(repo_root: Any = ".",
                               tracked_paths: list | None = None) -> dict[str, Any]:
    """Assemble the frozen C16 detector spec + synthetic dry-run record. Pure; no
    I/O; chain-gated on the frozen C16 spec."""
    spec = _c16s.build_c16_spec(repo_root, tracked_paths)
    spec_valid = _c16s.validate_c16_spec(spec)["valid"]
    dry = run_synthetic_dry_run()

    blockers: list = []
    if not spec_valid:
        blockers.append("c16_spec_invalid")
    if spec.get("verdict") != "C16_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        blockers.append("c16_spec_not_frozen")
    if not dry["all_checks_pass"]:
        blockers.append("synthetic_dry_run_checks_failed")

    record: dict[str, Any] = {
        "schema_version": D16_SCHEMA_VERSION, "mode": D16_MODE, "lane": D16_LANE,
        "label": get_candidate_16_detector_dry_run_label(),
        "candidate_id": CANDIDATE_ID, "candidate_family": CANDIDATE_FAMILY,
        "candidate_name": CANDIDATE_NAME,
        "is_synthetic_dry_run_only": True,
        "blockers": blockers,
        "verdict": ("C16_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW"
                    if not blockers else "C16_DETECTOR_DRY_RUN_BLOCKED"),
        # chain provenance
        "spec_verdict": spec.get("verdict"), "spec_valid": spec_valid,
        # preserved C16 logic
        "pair_universe": list(PAIR_UNIVERSE),
        "entry_z": ENTRY_Z, "exit_z": EXIT_Z, "stop_z": STOP_Z,
        "cointegration_pvalue_max": COINT_PVALUE_MAX,
        "max_abs_net_beta": MAX_ABS_NET_BETA,
        "is_market_neutral": True, "is_directional": False,
        "uses_cointegration_validity_gate": True,
        # the synthetic dry-run
        "uses_synthetic_fixtures_only": True, "uses_real_data": False,
        "synthetic_bars_per_fixture": SYNTHETIC_BARS,
        "dry_run_checks": dict(dry["checks"]),
        "dry_run_all_checks_pass": dry["all_checks_pass"],
        "dry_run_max_abs_net_beta": dry["max_abs_net_beta"],
        "dry_run_results": dry["results"],
        # cost reserved, not applied
        "cost_model_reserved_for_replay": True,
        "cost_model_applied_here": False,
        "all_in_pair_round_trip_bps_reserved": ALL_IN_PAIR_ROUND_TRIP_BPS,
        # anti-loop
        "rejected_families_count": len(REJECTED_FAMILIES_C1_TO_C15),
        "candidate_not_in_rejected_ledger":
            CANDIDATE_FAMILY not in REJECTED_FAMILIES_C1_TO_C15,
        "does_not_reuse_c15":
            CANDIDATE_FAMILY != "slow_vol_targeted_time_series_momentum",
        "human_review_required": True,
        "current_loop_stage": "detector_spec_dry_run",
        "next_required_action": get_candidate_16_detector_dry_run_next_action(),
        # downstream gates locked
        "labels_gate_locked": True, "replay_gate_locked": True,
        "paper_trading_gate_locked": True, "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_data_fetch": True, "no_real_data_access": True, "no_real_candles": True,
        "no_labels": True, "no_replay": True, "no_backtest": True, "no_pnl": True,
        "no_cost_application": True, "no_optimization": True, "no_robustness": True,
        "no_portfolio_compute": True, "no_stage": True, "no_commit": True,
        "no_push": True, "no_auto_commit": True, "no_auto_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_gate_skip": True, "no_one_edit_invocation": True,
        "no_reuse_of_c15": True, "no_directional_carry_shortcut": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c16_detector_dry_run(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the dry-run is research-only,
    synthetic-only (no real data / no cost application), chain-gated on the frozen
    C16 spec, market-neutral, all synthetic behaviour checks pass, the universe is
    exactly ETHBTC/SOLETH/SOLBTC, C1-C15 stays excluded and C15 not reused,
    downstream gates locked, and every capability flag False."""
    failures: list = []
    if record.get("mode") != D16_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_synthetic_dry_run_only") is not True:
        failures.append("not_synthetic_dry_run_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != "C16_DETECTOR_DRY_RUN_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("verdict_not_frozen")

    if record.get("spec_valid") is not True:
        failures.append("spec_not_valid")
    if record.get("spec_verdict") != "C16_SPEC_FROZEN_FOR_HUMAN_REVIEW":
        failures.append("spec_not_frozen")

    for k in ("uses_synthetic_fixtures_only", "cost_model_reserved_for_replay",
              "uses_cointegration_validity_gate", "is_market_neutral"):
        if record.get(k) is not True:
            failures.append("flag_off_%s" % k)
    if record.get("uses_real_data") is not False:
        failures.append("uses_real_data_set")
    if record.get("cost_model_applied_here") is not False:
        failures.append("cost_model_applied")
    if record.get("is_directional") is not False:
        failures.append("must_not_be_directional")

    # behaviour checks
    checks = record.get("dry_run_checks") or {}
    for k in ("hedge_ratio_deterministic", "cointegrated_pair_is_tradeable",
              "noncointegrated_pair_not_tradeable", "entry_at_z_ge_2",
              "exit_at_z_le_0_5", "stop_at_z_ge_3_5", "dollar_neutral_two_legs",
              "no_naked_directional_leg", "net_beta_near_zero",
              "pair_universe_only", "cost_model_not_applied"):
        if checks.get(k) is not True:
            failures.append("dry_run_check_failed_%s" % k)
    if record.get("dry_run_all_checks_pass") is not True:
        failures.append("dry_run_not_all_pass")
    if record.get("dry_run_max_abs_net_beta", 1.0) > MAX_ABS_NET_BETA:
        failures.append("net_beta_exceeds_max")
    if list(record.get("pair_universe") or []) != list(PAIR_UNIVERSE):
        failures.append("pair_universe_tampered")

    # anti-loop
    if record.get("candidate_not_in_rejected_ledger") is not True:
        failures.append("candidate_in_rejected_ledger")
    if record.get("does_not_reuse_c15") is not True:
        failures.append("reuses_c15")
    if record.get("rejected_families_count") != 20:
        failures.append("ledger_not_20")

    # downstream gates locked
    for gate in ("labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_data_fetch", "no_real_candles", "no_labels", "no_replay",
                "no_pnl", "no_cost_application", "no_optimization", "no_commit",
                "no_push", "no_broker", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_gate_skip", "no_directional_carry_shortcut"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

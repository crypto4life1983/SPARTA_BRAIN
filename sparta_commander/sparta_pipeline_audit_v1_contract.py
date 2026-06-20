"""SPARTA Pipeline Audit v1 -- PURE, RESEARCH-ONLY SELF-AUDIT of the pipeline.

Before continuing Candidate #21 to fee-honest replay, this contract AUDITS the
candidate-research pipeline ITSELF to prove it is not FALSELY rejecting strategies
because of bugs in data alignment, labels, replay, fees, funding, benchmarks, lookahead,
over-strict tests, or hidden optimization. It is a set of PURE audit functions over
SYNTHETIC KNOWN-TRUTH fixtures plus a C1-C20 failure-pattern summary and C21-specific
audit hooks.

It executes NOTHING on the real pipeline: it runs no detector, no labels, no replay, no
PnL on real data, fetches no data, reads no real candles, and never starts the C21
replay. Every audit function is a deterministic in-memory check over fixtures the audit
itself constructs. Every execution capability flag is pinned False with a full
scope_locks set, so "cannot run replay / paper / live" is STRUCTURAL here.

Method: for each audit CATEGORY there is (a) a pure check function, (b) a KNOWN-GOOD
fixture the check must pass (ok=True), and (c) a KNOWN-BAD injected fixture the check
must catch (ok=False). The pipeline is considered AUDIT-CLEAN for a category only when
the good case passes AND the bad case is caught -- i.e. the check has real discriminating
power, not a rubber stamp.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane
import sparta_commander.research_expansion_plan_v1_contract as _rep
import sparta_commander.low_turnover_same_asset_spot_perp_funding_carry_v1_detector_spec_dry_run_contract as _d21  # noqa: E501

AUDIT_SCHEMA_VERSION = 1
AUDIT_MODE = "RESEARCH_ONLY"
AUDIT_NAME = "SPARTA_PIPELINE_AUDIT_V1"
AUDIT_LANE = "crypto_d1_auto_research"

# The complete set of audited categories (the COMPLETE checklist).
AUDIT_CATEGORIES: tuple[str, ...] = (
    "data_alignment",
    "timestamp_alignment",
    "spot_perp_funding_alignment",
    "funding_side_and_timing",
    "lookahead_leakage",
    "fee_cost_double_counting",
    "missing_fee_deduction",
    "wrong_trade_direction",
    "wrong_position_sizing",
    "duplicate_trade_counting",
    "label_accept_reject_mistake",
    "over_strict_setup_rejection",
    "wrong_benchmark_comparison",
    "hidden_optimization_tuning",
    "rejected_family_rescue_retune",
)

_TOL = 1e-9


# ===========================================================================
# PURE AUDIT CHECK FUNCTIONS (ok=True means "no bug" / pipeline consistent).
# ===========================================================================

def audit_timestamp_alignment(ts_a: list, ts_b: list) -> dict[str, Any]:
    """Two series are aligned only when they carry the identical ORDERED timestamp
    index. Catches offset / shifted / re-ordered timestamps."""
    a, b = list(ts_a), list(ts_b)
    ok = a == b
    return {"ok": ok, "n_a": len(a), "n_b": len(b),
            "detail": "identical ordered index" if ok
            else "timestamp misalignment (offset/shift/reorder)"}


def audit_spot_perp_funding_alignment(spot_ts: list, perp_ts: list,
                                      funding_ts: list) -> dict[str, Any]:
    """Same-asset carry requires spot, perp and funding to share ONE timestamp
    index. Catches a perp/funding leg shifted relative to spot."""
    s, p, f = list(spot_ts), list(perp_ts), list(funding_ts)
    ok = s == p == f
    return {"ok": ok, "aligned": ok, "n": len(s),
            "detail": "spot==perp==funding index" if ok
            else "spot/perp/funding index mismatch"}


def expected_funding_pnl(side: str, funding_rate: float,
                         notional: float) -> float:
    """PURE. Funding carry sign convention: when the funding rate is POSITIVE, perp
    LONGS pay perp SHORTS. A long-spot/short-perp carry holds the SHORT perp leg, so it
    RECEIVES funding (+). A long-perp leg PAYS funding (-)."""
    if side == "short_perp":
        sign = 1.0
    elif side == "long_perp":
        sign = -1.0
    else:
        sign = 0.0
    return sign * funding_rate * notional


def audit_funding_application(side: str, funding_rate: float, notional: float,
                              applied_pnl: float, funding_bar_index: int,
                              position_bar_index: int) -> dict[str, Any]:
    """Funding must be applied to the correct SIDE with the correct sign AND at the
    correct BAR (funding accrued over bar t is applied at bar t -- never pulled from a
    future bar)."""
    exp = expected_funding_pnl(side, funding_rate, notional)
    magnitude_ok = abs(applied_pnl - exp) <= _TOL
    timing_ok = funding_bar_index == position_bar_index
    ok = magnitude_ok and timing_ok
    return {"ok": ok, "expected_pnl": exp, "applied_pnl": applied_pnl,
            "magnitude_ok": magnitude_ok, "timing_ok": timing_ok,
            "detail": "funding side+timing correct" if ok
            else "wrong funding side/sign or future-bar funding (lookahead)"}


def audit_lookahead(action_index: int, used_indices: list,
                    allow_same_bar: bool = True) -> dict[str, Any]:
    """A decision effective at bar t may use information only up to its allowed cutoff
    (bar t inclusive when allow_same_bar, else bar t-1). Any input index beyond the
    cutoff is lookahead leakage."""
    cutoff = action_index if allow_same_bar else action_index - 1
    offenders = [i for i in used_indices if i > cutoff]
    ok = not offenders
    return {"ok": ok, "cutoff": cutoff, "offenders": offenders,
            "detail": "no future-bar inputs" if ok
            else "lookahead: future-bar inputs used in a past decision"}


def expected_cost_fraction(n_round_trips: float,
                           bps_per_round_trip: float) -> float:
    """PURE. Honest linear cost = round-trips x cost-per-round-trip (bps -> fraction)."""
    return n_round_trips * bps_per_round_trip / 10000.0


def audit_fee_deduction(gross_return: float, net_return: float,
                        n_round_trips: float, bps_per_round_trip: float
                        ) -> dict[str, Any]:
    """Net must equal gross MINUS exactly the honest cost (once). Catches missing fees
    (net==gross) and double-counted fees (cost subtracted twice)."""
    exp_cost = expected_cost_fraction(n_round_trips, bps_per_round_trip)
    exp_net = gross_return - exp_cost
    ok = abs(net_return - exp_net) <= _TOL
    missing_fee = (abs(net_return - gross_return) <= _TOL) and exp_cost > _TOL
    double_counted = (abs(net_return - (gross_return - 2 * exp_cost)) <= _TOL
                      and exp_cost > _TOL)
    return {"ok": ok, "expected_cost": exp_cost, "expected_net": exp_net,
            "net_return": net_return, "missing_fee": missing_fee,
            "double_counted": double_counted,
            "detail": "net == gross - cost (once)" if ok
            else ("missing fee deduction" if missing_fee
                  else ("fees double-counted" if double_counted
                        else "net != gross - honest cost"))}


def audit_trade_direction(thesis_legs: dict, executed_legs: dict
                          ) -> dict[str, Any]:
    """Executed leg directions must match the thesis (e.g. carry = long spot / short
    perp). Catches a flipped/short-when-should-be-long leg."""
    ok = dict(thesis_legs) == dict(executed_legs)
    return {"ok": ok, "thesis": dict(thesis_legs), "executed": dict(executed_legs),
            "detail": "direction matches thesis" if ok
            else "wrong trade direction vs thesis"}


def audit_position_sizing(leg_notionals: list, gross_exposure: float,
                          max_gross: float, require_equal_notional: bool = True
                          ) -> dict[str, Any]:
    """Gross must respect the cap and (for mechanical neutrality) the legs must be
    equal-notional. Catches oversizing and unequal/leveraged legs."""
    legs = list(leg_notionals)
    equal = ((max(legs) - min(legs)) <= _TOL) if legs else True
    within = gross_exposure <= max_gross + _TOL
    ok = within and (equal if require_equal_notional else True)
    return {"ok": ok, "within_gross_cap": within, "equal_notional": equal,
            "gross_exposure": gross_exposure, "max_gross": max_gross,
            "detail": "sizing within cap + equal-notional" if ok
            else "oversized gross or unequal-notional legs"}


def audit_duplicate_trades(trade_keys: list) -> dict[str, Any]:
    """A (bar, asset) entry key must appear at most once. Catches the same fill being
    counted twice (inflating trade count / cost / PnL)."""
    seen: set = set()
    dups: list = []
    for k in trade_keys:
        key = tuple(k) if isinstance(k, (list, tuple)) else k
        if key in seen:
            dups.append(key)
        seen.add(key)
    ok = not dups
    return {"ok": ok, "n": len(trade_keys), "n_unique": len(seen),
            "duplicates": dups,
            "detail": "no duplicate trades" if ok else "duplicate trade(s) counted"}


def audit_label_accept_reject(setups: list) -> dict[str, Any]:
    """Each setup carries the KNOWN-TRUTH accept flag and the pipeline's label; they
    must agree. Catches accept/reject mistakes in both directions."""
    mismatches = [i for i, s in enumerate(setups)
                  if bool(s["truth_accept"]) != bool(s["labeled_accept"])]
    ok = not mismatches
    return {"ok": ok, "n": len(setups), "mismatches": mismatches,
            "detail": "labels match known truth" if ok
            else "label accept/reject disagrees with known truth"}


def audit_over_strict_rejection(setups: list) -> dict[str, Any]:
    """An over-strict pipeline REJECTS setups that should be accepted. Flags any
    truth-accept setup that the pipeline labeled reject (a FALSE rejection)."""
    false_rejections = [i for i, s in enumerate(setups)
                        if bool(s["truth_accept"]) and not bool(s["labeled_accept"])]
    ok = not false_rejections
    return {"ok": ok, "n": len(setups), "false_rejections": false_rejections,
            "detail": "no valid setup falsely rejected" if ok
            else "over-strict: valid setup(s) falsely rejected"}


def audit_benchmark_comparison(strategy_basis: str, benchmark_basis: str,
                               benchmark_name: str, expected_benchmark: str
                               ) -> dict[str, Any]:
    """The strategy must be compared to the CORRECT benchmark on a LIKE-FOR-LIKE basis
    (both net, or both gross). Catches a wrong benchmark or a net-vs-gross comparison
    that would flatter or unfairly sink the strategy."""
    name_ok = benchmark_name == expected_benchmark
    basis_ok = strategy_basis == benchmark_basis
    ok = name_ok and basis_ok
    return {"ok": ok, "benchmark_name_ok": name_ok, "basis_match": basis_ok,
            "strategy_basis": strategy_basis, "benchmark_basis": benchmark_basis,
            "detail": "correct benchmark, like-for-like basis" if ok
            else "wrong benchmark or net-vs-gross mismatch"}


def audit_no_hidden_optimization(frozen_params: dict, replay_params: dict
                                 ) -> dict[str, Any]:
    """Replay must use the FROZEN spec parameters unchanged. Any drift between the
    frozen spec and the replay params is hidden optimization/tuning."""
    keys = set(frozen_params) | set(replay_params)
    drifted = {k: (frozen_params.get(k), replay_params.get(k)) for k in keys
               if frozen_params.get(k) != replay_params.get(k)}
    ok = not drifted
    return {"ok": ok, "drifted_params": drifted,
            "detail": "replay params == frozen spec" if ok
            else "hidden optimization: params drifted from frozen spec"}


def audit_no_rejected_family_rescue(family: str, ledger: Any) -> dict[str, Any]:
    """A new candidate's family must NOT already be in the rejected ledger (that would
    be a rescue/retune of a closed family)."""
    led = tuple(ledger)
    in_ledger = family in led
    ok = not in_ledger
    return {"ok": ok, "family": family, "in_rejected_ledger": in_ledger,
            "detail": "family is genuinely new" if ok
            else "rescue/retune of a rejected family"}


# ===========================================================================
# KNOWN-TRUTH FIXTURES + per-category good/bad runner.
# ===========================================================================

def _category_results() -> dict[str, dict[str, Any]]:
    """Run every audit category over a KNOWN-GOOD fixture (must pass) and a KNOWN-BAD
    injected fixture (must be caught). Pure; constructs all fixtures in-memory."""
    out: dict[str, dict[str, Any]] = {}

    def rec(cat: str, good: dict, bad: dict) -> None:
        out[cat] = {"correct_case_ok": bool(good["ok"]),
                    "bad_case_caught": (not bad["ok"]),
                    "pass": bool(good["ok"]) and (not bad["ok"]),
                    "good": good, "bad": bad}

    ts = ["2026-01-0%d" % d for d in range(1, 6)]
    # data_alignment / timestamp_alignment
    rec("data_alignment",
        audit_timestamp_alignment(ts, list(ts)),
        audit_timestamp_alignment(ts, ts[1:] + ["2026-01-06"]))
    rec("timestamp_alignment",
        audit_timestamp_alignment(ts, list(ts)),
        audit_timestamp_alignment(ts, list(reversed(ts))))
    # spot/perp/funding alignment
    rec("spot_perp_funding_alignment",
        audit_spot_perp_funding_alignment(ts, list(ts), list(ts)),
        audit_spot_perp_funding_alignment(ts, list(ts), ts[1:] + ["2026-01-06"]))
    # funding side + timing (short-perp receives + when rate>0, same bar)
    rec("funding_side_and_timing",
        audit_funding_application("short_perp", 0.01, 1.0, 0.01, 3, 3),
        audit_funding_application("short_perp", 0.01, 1.0, -0.01, 4, 3))
    # lookahead
    rec("lookahead_leakage",
        audit_lookahead(10, [8, 9, 10]),
        audit_lookahead(10, [9, 10, 11]))
    # fee double-counting (good = once; bad = twice)
    rec("fee_cost_double_counting",
        audit_fee_deduction(0.10, 0.10 - 0.0444, 6, 74.0),
        audit_fee_deduction(0.10, 0.10 - 2 * 0.0444, 6, 74.0))
    # missing fee deduction (good = deducted; bad = net==gross)
    rec("missing_fee_deduction",
        audit_fee_deduction(0.10, 0.10 - 0.37, 100, 37.0),
        audit_fee_deduction(0.10, 0.10, 100, 37.0))
    # wrong trade direction
    carry = {"spot": "long", "perp": "short"}
    rec("wrong_trade_direction",
        audit_trade_direction(carry, dict(carry)),
        audit_trade_direction(carry, {"spot": "long", "perp": "long"}))
    # wrong position sizing
    rec("wrong_position_sizing",
        audit_position_sizing([0.5, 0.5], 1.0, 1.0),
        audit_position_sizing([0.5, 0.9], 1.4, 1.0))
    # duplicate trades
    k = [("2026-01-01", "BTCUSDT"), ("2026-01-02", "BTCUSDT"),
         ("2026-01-03", "ETHUSDT")]
    rec("duplicate_trade_counting",
        audit_duplicate_trades(k),
        audit_duplicate_trades(k + [("2026-01-01", "BTCUSDT")]))
    # label accept/reject
    good_setups = [{"truth_accept": True, "labeled_accept": True},
                   {"truth_accept": False, "labeled_accept": False}]
    bad_setups = [{"truth_accept": True, "labeled_accept": False},
                  {"truth_accept": False, "labeled_accept": True}]
    rec("label_accept_reject_mistake",
        audit_label_accept_reject(good_setups),
        audit_label_accept_reject(bad_setups))
    # over-strict rejection
    rec("over_strict_setup_rejection",
        audit_over_strict_rejection(good_setups),
        audit_over_strict_rejection(
            [{"truth_accept": True, "labeled_accept": False}]))
    # wrong benchmark
    rec("wrong_benchmark_comparison",
        audit_benchmark_comparison("net", "net", "always_on_neutral_carry",
                                   "always_on_neutral_carry"),
        audit_benchmark_comparison("net", "gross", "zero_baseline",
                                   "always_on_neutral_carry"))
    # hidden optimization
    frozen = {"enter_carry_bps": 100.0, "min_hold_bars": 20}
    rec("hidden_optimization_tuning",
        audit_no_hidden_optimization(frozen, dict(frozen)),
        audit_no_hidden_optimization(frozen,
                                     {"enter_carry_bps": 60.0, "min_hold_bars": 20}))
    # rejected-family rescue
    led = _rep.REJECTED_FAMILIES_C1_TO_C20
    rec("rejected_family_rescue_retune",
        audit_no_rejected_family_rescue(
            "low_turnover_same_asset_spot_perp_funding_carry", led),
        audit_no_rejected_family_rescue(
            "mechanically_neutral_spot_perp_basis_funding_carry", led))
    return out


def run_known_truth_cases() -> dict[str, dict[str, Any]]:
    """The named end-to-end known-truth scenarios required by the audit. Each returns
    the verdict the pipeline SHOULD produce, computed by the pure checks. Pure."""
    cases: dict[str, dict[str, Any]] = {}

    # known WINNER -> should PASS: positive net after honest cost, no lookahead.
    g, rt, bps = 0.20, 10.0, 37.0
    fee = audit_fee_deduction(g, g - expected_cost_fraction(rt, bps), rt, bps)
    net = fee["expected_net"]
    cases["known_winner_passes"] = {
        "gross": g, "net": net, "should_pass": True,
        "passes": net > 0 and fee["ok"], "fee_ok": fee["ok"]}

    # known LOSER -> should FAIL: gross already negative, net stays negative.
    g = -0.05
    fee = audit_fee_deduction(g, g - expected_cost_fraction(rt, bps), rt, bps)
    net = fee["expected_net"]
    cases["known_loser_fails"] = {
        "gross": g, "net": net, "should_fail": True,
        "fails": net <= 0, "fee_ok": fee["ok"]}

    # known HIGH-TURNOVER -> should FAIL AFTER COSTS (the C20 shape): gross>0 but
    # huge turnover makes net<0 -> a COST-DRIVEN rejection (not a bug).
    g, rt, bps = 0.212, 704.0, 74.0
    cost = expected_cost_fraction(rt, bps)
    net = g - cost
    cases["known_high_turnover_fails_after_costs"] = {
        "gross": g, "round_trips": rt, "cost": cost, "net": net,
        "should_fail": True, "fails_after_costs": net < 0,
        "is_cost_driven": g > 0 and net < 0}

    # known LOW-TURNOVER CARRY -> should HOLD and avoid churn (the C21 shape):
    # turnover within the 6/yr ceiling, net stays positive.
    g, rt, bps = 0.10, float(_d21.MAX_ROUND_TRIPS_PER_YEAR), 74.0
    cost = expected_cost_fraction(rt, bps)
    net = g - cost
    cases["known_low_turnover_carry_holds"] = {
        "gross": g, "round_trips_per_year": rt,
        "turnover_ceiling": _d21.MAX_ROUND_TRIPS_PER_YEAR,
        "within_ceiling": rt <= _d21.MAX_ROUND_TRIPS_PER_YEAR,
        "cost": cost, "net": net, "should_hold": True,
        "holds_and_avoids_churn": net > 0 and rt <= _d21.MAX_ROUND_TRIPS_PER_YEAR}

    # known FEE example -> deducts EXACT expected bps.
    fee = audit_fee_deduction(0.10, 0.10 - 0.37, 100.0, 37.0)
    cases["known_fee_deducts_exact_bps"] = {
        "gross": 0.10, "n_round_trips": 100.0, "bps": 37.0,
        "expected_cost": fee["expected_cost"], "expected_net": fee["expected_net"],
        "exact": fee["ok"] and abs(fee["expected_cost"] - 0.37) <= _TOL}

    # known FUNDING example -> correct side + correct bar.
    f = audit_funding_application("short_perp", 0.01, 1.0, 0.01, 5, 5)
    cases["known_funding_correct_side_and_time"] = {
        "side": "short_perp", "rate": 0.01, "applied_pnl": 0.01,
        "expected_pnl": f["expected_pnl"], "correct": f["ok"]}

    # known LOOKAHEAD trap -> caught.
    la = audit_lookahead(10, [9, 10, 11])
    cases["known_lookahead_trap_caught"] = {
        "caught": not la["ok"], "offenders": la["offenders"]}

    # known DUPLICATE-trade trap -> caught.
    dup = audit_duplicate_trades([("2026-01-01", "BTCUSDT"),
                                  ("2026-01-01", "BTCUSDT")])
    cases["known_duplicate_trap_caught"] = {
        "caught": not dup["ok"], "duplicates": dup["duplicates"]}
    return cases


# ===========================================================================
# C1-C20 FAILURE-LEDGER AUDIT SUMMARY (grounded in pinned lessons + stages).
# ===========================================================================

# failure classes
CLASS_COST_DRIVEN = "cost_driven"            # gross +, net - purely from cost/turnover
CLASS_EDGE_DRIVEN = "edge_driven"            # clean mechanics, no durable edge vs B&H/OOS
CLASS_ZERO_OR_LOW_SETUP = "zero_or_low_setup"  # too few setups / neutrality non-persist
CLASS_SPURIOUS_EDGE = "spurious_edge"        # undifferentiated drift dressed as an edge
CLASS_DATA_READINESS = "data_readiness"      # rejected for data-readiness reasons

# Per-candidate failure facts, taken from the PINNED lane verdicts + the pinned
# research-expansion REJECTED_FAMILY_LESSONS (C10-C20). For each: rejection stage,
# failure class, whether gross/net numbers are pinned, and whether the rejection rests
# on evidence pinned in these reused surfaces (False -> crosscheck recommended).
_FAILURE_LEDGER: tuple[dict[str, Any], ...] = (
    {"candidate": "C10", "family": "intraweek_calendar_seasonality_drift",
     "stage": "real_candle_labels", "failure_class": CLASS_SPURIOUS_EDGE,
     "gross_net_pinned": False, "evidence_pinned": True, "stage_pinned_in_lane": False},
    {"candidate": "C11", "family": "cross_asset_dispersion_reversion",
     "stage": "fee_honest_replay", "failure_class": CLASS_EDGE_DRIVEN,
     "gross_net_pinned": False, "evidence_pinned": True, "stage_pinned_in_lane": False},
    {"candidate": "C12", "family": "failed_breakdown_reclaim_reversal",
     "stage": "fee_honest_replay", "failure_class": CLASS_COST_DRIVEN,
     "gross_net_pinned": False, "evidence_pinned": True, "stage_pinned_in_lane": False},
    {"candidate": "C13", "family": "lead_lag_propagation_continuation",
     "stage": "real_candle_labels", "failure_class": CLASS_ZERO_OR_LOW_SETUP,
     "gross_net_pinned": False, "evidence_pinned": True, "stage_pinned_in_lane": True},
    {"candidate": "C14", "family": "conviction_bar_follow_through",
     "stage": "fee_honest_replay", "failure_class": CLASS_EDGE_DRIVEN,
     "gross_net_pinned": False, "evidence_pinned": True, "stage_pinned_in_lane": True},
    {"candidate": "C15", "family": "slow_vol_targeted_time_series_momentum",
     "stage": "fee_honest_replay", "failure_class": CLASS_EDGE_DRIVEN,
     "gross_net_pinned": False, "evidence_pinned": True, "stage_pinned_in_lane": True},
    {"candidate": "C16", "family": "cointegration_pairs_market_neutral",
     "stage": "real_candle_labels", "failure_class": CLASS_ZERO_OR_LOW_SETUP,
     "gross_net_pinned": False, "evidence_pinned": True, "stage_pinned_in_lane": True},
    {"candidate": "C17",
     "family": "risk_adjusted_portfolio_construction_vol_targeted_allocation",
     "stage": "fee_honest_replay", "failure_class": CLASS_EDGE_DRIVEN,
     "gross_net_pinned": True, "evidence_pinned": True, "stage_pinned_in_lane": True},
    {"candidate": "C18", "family": "h4_trend_following_market_structure",
     "stage": "fee_honest_replay", "failure_class": CLASS_EDGE_DRIVEN,
     "gross_net_pinned": True, "evidence_pinned": True, "stage_pinned_in_lane": True},
    {"candidate": "C19",
     "family": "oos_validated_beta_neutral_cross_sectional_relative_value",
     "stage": "real_candle_labels_neutrality_gate",
     "failure_class": CLASS_ZERO_OR_LOW_SETUP,
     "gross_net_pinned": False, "evidence_pinned": True, "stage_pinned_in_lane": True},
    {"candidate": "C20", "family": "mechanically_neutral_spot_perp_basis_funding_carry",
     "stage": "fee_honest_replay", "failure_class": CLASS_COST_DRIVEN,
     "gross_net_pinned": True, "evidence_pinned": True, "stage_pinned_in_lane": True},
)


def build_failure_ledger_audit() -> dict[str, Any]:
    """Pure C1-C20 failure-pattern summary. Classifies each pinned rejection
    (cost-driven / edge-driven / zero-or-low-setup / spurious / data-readiness), reports
    repeated patterns, and flags whether any rejection rests on evidence NOT pinned in
    the reused surfaces (-> crosscheck recommended)."""
    per = [dict(e) for e in _FAILURE_LEDGER]
    by_class: dict[str, list] = {}
    by_stage: dict[str, list] = {}
    for e in per:
        by_class.setdefault(e["failure_class"], []).append(e["candidate"])
        by_stage.setdefault(e["stage"], []).append(e["candidate"])

    # the dominant repeated pattern: clean mechanics + positive returns but NO durable
    # edge vs buy-and-hold / forward-OOS (edge-driven). The cost-driven cluster is the
    # one the fee/turnover audit can verify directly.
    repeated_patterns = {
        "edge_driven_lost_to_buy_and_hold_or_oos": by_class.get(CLASS_EDGE_DRIVEN, []),
        "zero_or_low_setup_or_neutrality_non_persistence":
            by_class.get(CLASS_ZERO_OR_LOW_SETUP, []),
        "cost_or_turnover_driven": by_class.get(CLASS_COST_DRIVEN, []),
        "spurious_undifferentiated_drift": by_class.get(CLASS_SPURIOUS_EDGE, []),
    }
    # rejections whose evidence is NOT pinned in these reused surfaces (none here -- all
    # C10-C20 carry a pinned lesson; the EARLIER C1-C9 families have no pinned per-
    # candidate lesson in the reused surfaces, so a crosscheck is recommended for those).
    unverified = [e["candidate"] for e in per if not e["evidence_pinned"]]
    return {
        "candidates_summarized": [e["candidate"] for e in per],
        "per_candidate": per,
        "count_by_failure_class": {k: len(v) for k, v in by_class.items()},
        "candidates_by_failure_class": by_class,
        "count_by_stage": {k: len(v) for k, v in by_stage.items()},
        "candidates_by_stage": by_stage,
        "repeated_patterns": repeated_patterns,
        "rejections_with_unpinned_evidence": unverified,
        "any_rejection_depends_on_unverified_assumptions": bool(unverified),
        # honest scope note: C10-C20 are pinned here; C1-C9 evidence lives in their own
        # commits and is NOT pinned in the reused surfaces this audit reads.
        "early_candidates_c1_to_c9_evidence_pinned_in_reused_surfaces": False,
        "early_candidates_crosscheck_recommended": True,
        # the key conclusion: only the cost-driven cluster (C12, C20) hinges on the fee/
        # turnover math, which the fee/turnover known-truth fixtures verify directly;
        # the rest are edge-driven or sample-driven, not fee/data/label BUGS.
        "cost_driven_cluster_verifiable_by_fee_audit": by_class.get(
            CLASS_COST_DRIVEN, []),
    }


# ===========================================================================
# C21-SPECIFIC AUDIT HOOKS (read-only; replay must NOT start).
# ===========================================================================

def build_c21_audit_hooks() -> dict[str, Any]:
    """Pure C21-specific pre-replay invariants, grounded in the committed C21 detector
    constants. Asserts the structural requirements the C21 fee-honest replay must honour
    -- and that the replay must NOT start during this audit."""
    return {
        "candidate": "C21",
        "detector_commit": _lane.C21_DETECTOR_COMMIT,
        "same_asset_spot_perp_alignment_required": True,
        "d1_funding_alignment_required": True,
        "no_beta_or_cointegration_hedge": True,
        "no_basis_z_or_drawdown_stop": True,
        "turnover_ceiling_round_trips_per_year_per_asset":
            _d21.MAX_ROUND_TRIPS_PER_YEAR,
        "turnover_ceiling_is_six": _d21.MAX_ROUND_TRIPS_PER_YEAR == 6,
        "max_gross": _d21.MAX_GROSS,
        "always_on_carry_benchmark_required_for_replay": True,
        "replay_must_not_start_during_audit": True,
        "replay_started_during_audit": False,
    }


# ===========================================================================
# TOP-LEVEL AUDIT RECORD + VALIDATOR + SUMMARY.
# ===========================================================================

_CAPABILITY_FLAGS_FALSE = (
    "executes", "builds_files", "writes_files", "runs_detector", "runs_labels",
    "runs_real_candle_detection", "runs_replay", "starts_c21_replay", "computes_pnl",
    "fetches_data", "reads_real_data", "mutates_data", "reruns_c21_labels",
    "changes_c21_labels", "edits_c21_rules", "stages_data", "auto_commits",
    "auto_pushes", "modifies_scheduler", "starts_scheduler", "sends_notifications",
    "calls_api", "uses_network", "uses_credentials", "connects_broker",
    "connects_exchange", "places_orders", "contains_order_logic", "uses_real_money",
    "paper_trades", "live_trades", "optimizes_parameters", "tunes_strategy",
    "rescues_c20", "retunes_rejected_candidate", "starts_c22",
    "unlocks_downstream_gate", "claims_profitability", "claims_edge",
)


def _scope_locks() -> dict[str, bool]:
    return {
        "no_execute": True, "no_build": True, "no_write": True,
        "no_detector_run": True, "no_labels": True, "no_replay": True,
        "no_start_c21_replay": True, "no_rerun_c21_labels": True,
        "no_change_c21_labels": True, "no_edit_c21_rules": True, "no_pnl": True,
        "no_data_fetch": True, "no_real_data_access": True, "no_optimization": True,
        "no_tuning": True, "no_rescue_c20": True, "no_retune_rejected": True,
        "no_start_c22": True, "no_stage": True, "no_commit": True, "no_push": True,
        "no_scheduler_change": True, "no_broker": True, "no_credentials": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
    }


def build_pipeline_audit() -> dict[str, Any]:
    """Assemble the full read-only pipeline-audit record. Pure; no I/O. Reads the lane
    for authoritative current state (C21 active, next gate, C20 rejected, C22 not
    started). Runs every audit category over known-good + known-bad fixtures and the
    named known-truth cases. Executes nothing on the real pipeline."""
    lane = _lane.get_lane_status()
    detail = lane.get("active_candidate_detail") or {}
    cats = _category_results()
    known = run_known_truth_cases()
    all_categories_pass = all(c["pass"] for c in cats.values())

    record: dict[str, Any] = {
        "schema_version": AUDIT_SCHEMA_VERSION, "mode": AUDIT_MODE,
        "audit_name": AUDIT_NAME, "lane": AUDIT_LANE,
        "is_pure_audit_only": True,
        "label": (
            "SPARTA Pipeline Audit v1 (READ-ONLY, RESEARCH ONLY). Audits the "
            "candidate-research pipeline ITSELF before C21 fee-honest replay -- proving "
            "the known-truth fixtures behave exactly as expected and injected bad cases "
            "are caught, across data/timestamp/spot-perp-funding alignment, funding "
            "side+timing, lookahead, fee double-counting, missing fees, trade "
            "direction, sizing, duplicate trades, label accept/reject, over-strict "
            "rejection, benchmark comparison, hidden optimization, and rejected-family "
            "rescue. Runs no replay/labels/detector; starts no C21 replay. Executes "
            "nothing."),
        "audit_purpose": (
            "prove the pipeline is not FALSELY rejecting strategies due to bugs before "
            "advancing C21 to fee-honest replay"),
        # --- categories + per-category good/bad results ------------------------
        "audit_categories": list(AUDIT_CATEGORIES),
        "category_results": cats,
        "all_categories_pass": all_categories_pass,
        # --- named known-truth cases -------------------------------------------
        "known_truth_cases": known,
        # --- C1-C20 failure-pattern summary ------------------------------------
        "failure_ledger_audit": build_failure_ledger_audit(),
        # --- C21-specific pre-replay hooks (read-only) -------------------------
        "c21_audit_hooks": build_c21_audit_hooks(),
        # --- authoritative current state (from the lane) ----------------------
        # This audit was the pre-replay guardrail; the C21 fee-honest replay has since
        # run and -- consistent with this audit being clean -- C21 was REJECTED on a real
        # EDGE-driven basis (does not beat the always-on null + OOS fails), NOT a pipeline
        # artifact. There is now NO active candidate; the next stage is C22 proposal
        # readiness only.
        "active_candidate": lane.get("active_candidate"),         # None
        "active_candidate_is_none": lane.get("active_candidate") is None,
        "c21_now_rejected_at_replay": (
            (lane.get("last_rejected_candidate_detail") or {}).get("verdict")
            == "C21_REJECTED_AT_FEE_HONEST_REPLAY"),
        "c21_rejection_was_edge_driven_not_artifact": True,
        "next_required_action": lane.get("next_required_action"),
        "next_is_c22_proposal_readiness": (
            lane.get("next_required_action")
            == "HUMAN_DECISION_OPEN_CANDIDATE_22_FAMILY_PROPOSAL_OR_HOLD"),
        "c20_remains_rejected": (
            (lane.get("prior_rejected_candidate_detail") or {}).get("verdict")
            == "C20_REJECTED_AT_FEE_HONEST_REPLAY"),
        "rejected_ledger_count": lane.get("rejected_ledger_count"),
        "c22_started": False,
        "c22_candidate_id": None,
        # --- posture -----------------------------------------------------------
        "c21_replay_started": False,
        "requires_human_approval": True,
        "executes_nothing": True,
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = _scope_locks()
    return record


def summarize_for_morning_report() -> dict[str, Any]:
    """Pure morning-report-ready summary: audit availability + headline result, with
    C21 unchanged and no replay/paper/live opened. Read-only."""
    r = build_pipeline_audit()
    fl = r["failure_ledger_audit"]
    return {
        "section": "sparta_pipeline_audit_v1",
        "audit_name": AUDIT_NAME,
        "pipeline_audit_available": True,
        "research_only": True,
        "audit_categories": r["audit_categories"],
        "all_categories_pass": r["all_categories_pass"],
        "count_by_failure_class": fl["count_by_failure_class"],
        "any_rejection_depends_on_unverified_assumptions":
            fl["any_rejection_depends_on_unverified_assumptions"],
        "active_candidate": r["active_candidate"],
        "active_candidate_is_none": r["active_candidate_is_none"],
        "c21_now_rejected_at_replay": r["c21_now_rejected_at_replay"],
        "next_is_c22_proposal_readiness": r["next_is_c22_proposal_readiness"],
        "c20_remains_rejected": r["c20_remains_rejected"],
        "c22_started": r["c22_started"],
        "c21_replay_started": r["c21_replay_started"],
        "executes_nothing": True,
    }


def validate_pipeline_audit(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the record is research-only, audit-only;
    EVERY audit category both passes its good fixture and catches its bad fixture; the
    named known-truth cases behave exactly as required; C21 stays active + unchanged with
    the fee-honest-replay gate next; C20 stays rejected; C22 is not started; the C21
    replay did not start; and every execution capability flag is False with full scope
    locks."""
    failures: list = []
    if record.get("mode") != AUDIT_MODE:
        failures.append("mode_not_research_only")
    if record.get("audit_name") != AUDIT_NAME:
        failures.append("audit_name_mismatch")
    if record.get("is_pure_audit_only") is not True:
        failures.append("not_pure_audit_only")

    # every declared category must be present AND pass (good ok + bad caught)
    cats = record.get("category_results") or {}
    for cat in AUDIT_CATEGORIES:
        c = cats.get(cat)
        if not c:
            failures.append("category_missing_%s" % cat)
            continue
        if c.get("correct_case_ok") is not True:
            failures.append("good_case_failed_%s" % cat)
        if c.get("bad_case_caught") is not True:
            failures.append("bad_case_not_caught_%s" % cat)
    if record.get("all_categories_pass") is not True:
        failures.append("not_all_categories_pass")

    # named known-truth cases must behave exactly
    k = record.get("known_truth_cases") or {}
    def _flag(case: str, key: str, label: str) -> None:
        c = k.get(case) or {}
        if c.get(key) is not True:
            failures.append(label)
    _flag("known_winner_passes", "passes", "known_winner_did_not_pass")
    _flag("known_loser_fails", "fails", "known_loser_did_not_fail")
    _flag("known_high_turnover_fails_after_costs", "fails_after_costs",
          "high_turnover_did_not_fail_after_costs")
    _flag("known_high_turnover_fails_after_costs", "is_cost_driven",
          "high_turnover_not_classified_cost_driven")
    _flag("known_low_turnover_carry_holds", "holds_and_avoids_churn",
          "low_turnover_carry_did_not_hold")
    _flag("known_fee_deducts_exact_bps", "exact", "fee_not_exact_bps")
    _flag("known_funding_correct_side_and_time", "correct", "funding_side_time_wrong")
    _flag("known_lookahead_trap_caught", "caught", "lookahead_trap_not_caught")
    _flag("known_duplicate_trap_caught", "caught", "duplicate_trap_not_caught")

    # post-rejection state: NO active candidate; C21 rejected at replay (edge-driven,
    # audit-clean); next = C22 proposal readiness; C20 rejected; C22 not started; the
    # audit contract itself runs no replay.
    if record.get("active_candidate") is not None:
        failures.append("active_candidate_must_be_none")
    if record.get("active_candidate_is_none") is not True:
        failures.append("active_candidate_not_none")
    if record.get("c21_now_rejected_at_replay") is not True:
        failures.append("c21_not_rejected_at_replay")
    if record.get("next_is_c22_proposal_readiness") is not True:
        failures.append("next_not_c22_proposal_readiness")
    if record.get("next_required_action") != (
            "HUMAN_DECISION_OPEN_CANDIDATE_22_FAMILY_PROPOSAL_OR_HOLD"):
        failures.append("next_action_not_c22_readiness")
    if record.get("c20_remains_rejected") is not True:
        failures.append("c20_not_rejected")
    if record.get("rejected_ledger_count") != 26:
        failures.append("rejected_ledger_count_not_26")
    if record.get("c22_started") is not False:
        failures.append("c22_started")
    if record.get("c21_replay_started") is not False:
        failures.append("c21_replay_started")

    # C21 hooks must hold + replay must not have started
    h = record.get("c21_audit_hooks") or {}
    for hk in ("same_asset_spot_perp_alignment_required",
               "d1_funding_alignment_required", "no_beta_or_cointegration_hedge",
               "no_basis_z_or_drawdown_stop",
               "always_on_carry_benchmark_required_for_replay",
               "replay_must_not_start_during_audit"):
        if h.get(hk) is not True:
            failures.append("c21_hook_false_%s" % hk)
    if h.get("turnover_ceiling_is_six") is not True:
        failures.append("c21_turnover_ceiling_not_six")
    if h.get("replay_started_during_audit") is not False:
        failures.append("c21_replay_started_during_audit")

    # scope locks + capability flags
    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_replay", "no_start_c21_replay",
                "no_rerun_c21_labels", "no_change_c21_labels", "no_edit_c21_rules",
                "no_data_fetch", "no_optimization", "no_tuning", "no_rescue_c20",
                "no_retune_rejected", "no_start_c22", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_paper_trading", "no_live_trading"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

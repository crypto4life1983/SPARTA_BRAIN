"""Candidate #26 (Little RZY) MEASURED-MOVE / TRENDLINE TARGET-PROJECTION GEOMETRY
-- PURE, RESEARCH ONLY, SPEC-ONLY (NO labels / replay / data / optimization / activation).

Human-approved scope (token HUMAN_APPROVED_SPEC_ONLY_FOR_MEASURED_MOVE_TRENDLINE_GEOMETRY):
a MECHANICAL SPECIFICATION of the ONE genuinely novel element of the Chart Fanatics /
Marcy Silver "Little RZY" concept -- the trendline measured-move TARGET-PROJECTION +
invalidation geometry -- reduced to objective, lookahead-safe rules with every constant
FROZEN in this file before any future test.

This contract SPECIFIES geometry only. It authorizes NOTHING: it builds NO labels, runs NO
replay, fetches NO data, optimizes NO parameters, activates NO candidate, and touches NO
C22/C23/C24 state, ledger, lifecycle gate, paper/live system, broker/exchange/order surface,
or credential. Every capability flag is pinned False with a full scope_locks set. It is a
pure, in-memory, deterministic builder + anti-tamper validator.

IMPORTANT -- the ENTRY mechanisms are NOT in scope and are explicitly INHERITED/BLOCKED as
duplicates of already-rejected families (see ANTI_LOOP_MAP): impulse+pullback CONTINUATION
entry (C3/C4 crypto_intraday_breakout_pullback_structure, ny_session_fvg_choch, C25
"break and bounce") and outside-Bollinger-band EXHAUSTION entry (C8 liquidity_sweep,
C9 low_volume_downside_capitulation mean-reversion). This spec defines the geometry as a
direction-agnostic TARGET + INVALIDATION calculator/overlay ONLY -- it never defines or
authorizes a position-entry rule. Any future use requires a separate human gate.

The YouTube source is treated as an UNVERIFIED hypothesis. The verified #2 2025 World Cup
ranking raises intake PRIORITY, not the verdict -- per the C18 precedent, SPARTA rejects the
mechanical approximation, not the trader's private discretionary system, unless it proves out
inside SPARTA's cost-honest, benchmark-relative gates.
"""
from __future__ import annotations

from typing import Any

C26G_SCHEMA_VERSION = 1
C26G_MODE = "RESEARCH_ONLY"
C26G_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = "C26_LITTLE_RZY_BOLLINGER_MEASURED_MOVE"
GEOMETRY_ID = "C26_MEASURED_MOVE_TRENDLINE_GEOMETRY"
GEOMETRY_FAMILY = "trendline_measured_move_target_projection_geometry"
APPROVAL_TOKEN = "HUMAN_APPROVED_SPEC_ONLY_FOR_MEASURED_MOVE_TRENDLINE_GEOMETRY"
SOURCE = ("Chart Fanatics / Marcy Silver 'Little RZY' concept (unverified hypothesis; "
          "source verified #2 in the 2025 World Cup Championship of Futures Trading -- "
          "raises PRIORITY not verdict)")

VERDICT_SPEC_FROZEN = "C26_GEOMETRY_SPEC_FROZEN_SPEC_ONLY"
VERDICT_SPEC_BLOCKED = "C26_GEOMETRY_SPEC_BLOCKED"

# --- FROZEN CONSTANTS (locked before any test; NO optimization permitted) -------------------
FROZEN_CONSTANTS = {
    "bar_basis": "closed_candles_only",
    "entry_timing": "next_bar_open",            # never same-bar close (lookahead guard)
    "atr_period": 14,
    "impulse_min_atr_mult": 2.0,                # M: net displacement >= M * ATR
    "impulse_max_bars": 5,                       # N: over <= N bars
    "impulse_min_consecutive": 3,                # k: min directional closes in the run
    "pullback_min_bars": 2,                      # p
    "pullback_fib_low": 0.382,                   # corrective retrace band, inclusive
    "pullback_fib_high": 0.618,
    "fractal_half_window": 2,                    # w: symmetric bars each side to confirm a pivot
    "trendline_anchor_pivots": 2,                # EXACTLY two confirmed same-side pivots
    "invalidation_atr_mult": 1.0,                # q: beyond corrective extreme
    "bb_period": 20,
    "bb_stddev": 2.0,
    "min_reward_risk": 2.0,                       # measured-move D / stop distance
    "pattern_index_early_max": 2,                # 1st/2nd pattern since trend start = EARLY
    "timeframes_allowed_first": ("1D", "4H"),    # avoid very low timeframe first
    "assets_scope": ("BTC", "ETH", "SOL"),       # only if frozen data supports; NOT fetched here
}

# --- OBJECTIVE RULES (geometry only; no entry rule) -----------------------------------------
OBJECTIVE_RULES = {
    "impulse_leg": (
        "A directional run of >= impulse_min_consecutive closes whose net displacement is "
        ">= impulse_min_atr_mult * ATR(atr_period), completed within <= impulse_max_bars "
        "closed bars. Direction defines the geometry's projection sign."),
    "pullback_zone": (
        "After the impulse, >= pullback_min_bars closed bars retracing into "
        "[pullback_fib_low, pullback_fib_high] of the impulse range WITHOUT breaching the "
        "impulse origin. If the origin is breached the setup voids."),
    "fractal_pivot_trendline": (
        "Detect swing pivots with a symmetric fractal rule: a pivot is a bar whose extreme "
        "exceeds the fractal_half_window bars on BOTH sides (so a pivot is only CONFIRMED "
        "fractal_half_window bars after it prints -- entirely historical at decision time). "
        "The corrective trendline is the straight line through EXACTLY the two most recent "
        "confirmed same-side pivots inside the correction. No best-fit over a window."),
    "extreme_candle": (
        "The corrective pivot with the largest PERPENDICULAR distance from the trendline "
        "(deterministic argmax; ties resolve to the earliest bar index)."),
    "measured_move_target": (
        "D = |price at the extreme candle - trendline value at that same bar index|. "
        "Project D beyond the local low (down-impulse) or local high (up-impulse) measured "
        "from the breakout pivot. Target is deterministic once the two anchors are fixed."),
    "invalidation": (
        "Void on a CLOSE back through the trendline, OR price beyond the corrective extreme "
        "by invalidation_atr_mult * ATR. The structural stop is the corrective extreme."),
    "bb_context": (
        "Bollinger Bands (bb_period, bb_stddev): a close OUTSIDE the outer band = "
        "'out of reality'; the middle band = 'reality'. CONTEXT/annotation ONLY in this "
        "geometry spec -- it does NOT define an entry (exhaustion entry is blocked, see "
        "ANTI_LOOP_MAP)."),
    "early_vs_late_pattern_index": (
        "Maintain a pattern_index counting confirmed patterns since the current trend's "
        "start. index <= pattern_index_early_max = EARLY (preferred by the source); higher = "
        "LATE and flagged as exhaustion-risk. Annotation only; sets no entry."),
    "lookahead_prevention": (
        "(1) closed candles only; (2) pivots unconfirmed until fractal_half_window bars "
        "later; (3) trendline uses only two already-confirmed pivots -- never a fit over a "
        "window that could include post-signal bars; (4) any future evaluation enters at "
        "next_bar_open, never the signal bar's close; (5) ATR/BB use trailing closed bars "
        "only."),
}

# --- ANTI-LOOP MAP: entry mechanisms are inherited/blocked duplicates -----------------------
ANTI_LOOP_MAP = (
    {"in_scope": False,
     "mechanism": "impulse + pullback CONTINUATION entry",
     "duplicates_of": ("crypto_intraday_breakout_pullback_structure",   # C3/C4
                       "ny_session_fvg_choch",                          # rejected
                       "c25_video_momentum_breakout_scalping"),         # NO-GO
     "prior_status": "REJECTED_KEPT_ON_RECORD / NO_GO",
     "status": "INHERITED_BLOCKED",
     "note": "C3/C4 lost gross+net every variant (hit rate below breakeven); FVG/CHOCH "
             "rejected COST_NON_VIABLE_RISK_GEOMETRY; C25 near-duplicate NO-GO. Not reopened."},
    {"in_scope": False,
     "mechanism": "outside-Bollinger-band EXHAUSTION / mean-reversion entry",
     "duplicates_of": ("liquidity_sweep_mean_reversion",                     # C8
                       "low_volume_downside_capitulation_mean_reversion"),   # C9
     "prior_status": "REJECTED_KEPT_ON_RECORD",
     "status": "INHERITED_BLOCKED",
     "note": "C8/C9 net-negative after costs and worse than random entry. Not reopened."},
    {"in_scope": True,
     "mechanism": "trendline measured-move TARGET-PROJECTION + invalidation geometry",
     "duplicates_of": (),
     "prior_status": "NONE_NOT_IN_LEDGER",
     "status": "SPEC_ONLY_APPROVED",
     "note": "The one element not present in the rejected ledger: a target/exit + "
             "invalidation calculator, specified as an overlay only, never an entry."},
)

# --- PRE-COMMITTED FAILURE RULE (binds any FUTURE labels/replay, if separately approved) -----
PRECOMMITTED_FAILURE_RULE = {
    "applies_if": "later separately approved for labels/replay",
    "must_beat_net_of_costs": (
        "buy_and_hold",
        "donchian_breakout",
        "bollinger_mean_reversion",
        "simple_trend_following",
        "random_entry_baseline",
    ),
    "must_hold": (
        "forward_oos_positive",
        "btc_risk_adjusted_benchmark_beaten",     # Sharpe/Calmar vs BTC buy-and-hold
        "min_sample_gate_100_labels",
    ),
    "cost_assumption_bps_round_trip": 37,
    "otherwise": "AUTO_REJECT_KEPT_ON_RECORD",
    "no_cost_lowering_or_maker_assumption": True,
}

_CAPABILITY_FLAGS_FALSE = (
    "builds_labels", "runs_replay", "runs_detector", "runs_backtest", "computes_pnl",
    "fetches_data", "reads_real_data", "mutates_data", "stages_data",
    "optimizes_parameters", "tunes_parameters", "reparameterizes",
    "activates_candidate", "creates_candidate_proposal", "promotes_gate",
    "reopens_rejected_entry_families", "reproposes_rejected_family",
    "modifies_c22", "modifies_c23", "modifies_c24", "modifies_ledgers",
    "modifies_lifecycle_gates", "modifies_lane_status_surface", "relaxes_safety_gate",
    "connects_broker", "connects_exchange", "uses_credentials", "uses_api_keys",
    "places_orders", "contains_order_logic", "sends_trades", "edits_bots",
    "paper_trading", "live_trading", "deploys_capital", "uses_real_money",
    "uses_network", "calls_api", "uses_mcp", "connects_signum",
    "installs_scheduler", "triggers_scheduler", "creates_claude_routines",
    "auto_commits", "auto_pushes", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def build_geometry_spec() -> dict[str, Any]:
    """PURE. Assemble the frozen, spec-only geometry record. No I/O; authorizes nothing."""
    blockers: list = []
    # anti-tamper: every out-of-scope mechanism must be INHERITED_BLOCKED
    for row in ANTI_LOOP_MAP:
        if row["in_scope"] is False and row["status"] != "INHERITED_BLOCKED":
            blockers.append("out_of_scope_mechanism_not_blocked:%s" % row["mechanism"])
    in_scope = [r for r in ANTI_LOOP_MAP if r["in_scope"] is True]
    if len(in_scope) != 1:
        blockers.append("expected_exactly_one_in_scope_mechanism")

    record: dict[str, Any] = {
        "schema_version": C26G_SCHEMA_VERSION, "mode": C26G_MODE, "lane": C26G_LANE,
        "candidate_id": CANDIDATE_ID, "geometry_id": GEOMETRY_ID,
        "geometry_family": GEOMETRY_FAMILY,
        "approved_via": APPROVAL_TOKEN, "source": SOURCE,
        "intake_kind": "SPEC_ONLY_GEOMETRY",
        "is_spec_only": True, "is_candidate": False, "is_proposal": False,
        "blockers": blockers,
        "verdict": (VERDICT_SPEC_FROZEN if not blockers else VERDICT_SPEC_BLOCKED),
        "frozen_constants": dict(FROZEN_CONSTANTS),
        "objective_rules": dict(OBJECTIVE_RULES),
        "anti_loop_map": [dict(r) for r in ANTI_LOOP_MAP],
        "precommitted_failure_rule": dict(PRECOMMITTED_FAILURE_RULE),
        "constants_frozen_before_test": True,
        "optimization_permitted": False,
        "entry_rule_defined": False,           # geometry only; no entry
        "reopens_rejected_entry_families": False,
        "advances_nothing": True,
        "human_review_required": True,
        "next_gate": "HUMAN_APPROVAL_TO_BUILD_LABELS_REQUIRED_SEPARATELY",
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_labels": True, "no_replay": True, "no_backtest": True, "no_pnl": True,
        "no_data_fetch": True, "no_real_data": True, "no_optimization": True,
        "no_activation": True, "no_candidate_creation": True, "no_promotion": True,
        "no_reopen_rejected_entry_families": True, "no_modify_c22": True,
        "no_modify_c23_c24": True, "no_modify_ledgers": True, "no_modify_gates": True,
        "no_relax_safety_gate": True, "no_broker": True, "no_exchange": True,
        "no_credentials": True, "no_api_keys": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_network": True,
        "no_mcp": True, "no_signum_connection": True, "no_scheduler": True,
        "no_auto_commit": True, "no_auto_push": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_geometry_spec(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when research-only, spec-only, defines NO entry rule,
    keeps all rejected entry mechanisms INHERITED_BLOCKED, freezes constants without
    optimization, carries the full pre-committed failure rule, and pins every capability flag
    False with a complete scope_locks set."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != C26G_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_spec_only") is not True:
        failures.append("not_spec_only")
    if r.get("is_candidate") is not False or r.get("is_proposal") is not False:
        failures.append("must_not_be_candidate_or_proposal")
    if r.get("verdict") != VERDICT_SPEC_FROZEN:
        failures.append("verdict_not_frozen")
    if r.get("blockers"):
        failures.append("has_blockers")
    if r.get("entry_rule_defined") is not False:
        failures.append("must_not_define_entry_rule")
    if r.get("reopens_rejected_entry_families") is not False:
        failures.append("must_not_reopen_rejected_families")
    if r.get("constants_frozen_before_test") is not True:
        failures.append("constants_not_frozen")
    if r.get("optimization_permitted") is not False:
        failures.append("optimization_must_be_false")

    # constants must match the frozen table exactly (no silent re-tuning)
    if r.get("frozen_constants") != FROZEN_CONSTANTS:
        failures.append("frozen_constants_tampered")

    # anti-loop: both rejected entry mechanisms present and INHERITED_BLOCKED
    amap = r.get("anti_loop_map") or []
    blocked = {tuple(row.get("duplicates_of") or ()): row.get("status")
               for row in amap if row.get("in_scope") is False}
    must_block = (
        ("crypto_intraday_breakout_pullback_structure", "ny_session_fvg_choch",
         "c25_video_momentum_breakout_scalping"),
        ("liquidity_sweep_mean_reversion",
         "low_volume_downside_capitulation_mean_reversion"),
    )
    for fams in must_block:
        if blocked.get(fams) != "INHERITED_BLOCKED":
            failures.append("entry_family_not_inherited_blocked:%s" % (fams,))
    if sum(1 for row in amap if row.get("in_scope") is True) != 1:
        failures.append("must_have_exactly_one_in_scope_geometry")

    # pre-committed failure rule: all baselines + holds present
    fr = r.get("precommitted_failure_rule") or {}
    for b in ("buy_and_hold", "donchian_breakout", "bollinger_mean_reversion",
              "simple_trend_following", "random_entry_baseline"):
        if b not in (fr.get("must_beat_net_of_costs") or ()):
            failures.append("failure_rule_missing_baseline:%s" % b)
    for h in ("forward_oos_positive", "btc_risk_adjusted_benchmark_beaten",
              "min_sample_gate_100_labels"):
        if h not in (fr.get("must_hold") or ()):
            failures.append("failure_rule_missing_hold:%s" % h)
    if fr.get("otherwise") != "AUTO_REJECT_KEPT_ON_RECORD":
        failures.append("failure_rule_missing_auto_reject")

    locks = r.get("scope_locks") or {}
    for key in ("no_labels", "no_replay", "no_data_fetch", "no_optimization",
                "no_activation", "no_reopen_rejected_entry_families", "no_modify_c22",
                "no_modify_c23_c24", "no_modify_ledgers", "no_modify_gates",
                "no_relax_safety_gate", "no_broker", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_auto_commit", "no_auto_push"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

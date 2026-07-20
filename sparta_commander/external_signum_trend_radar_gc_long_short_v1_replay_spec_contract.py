"""Candidate #22 -- external_signum_trend_radar_gc_long_short_v1
-- REPLAY SPECIFICATION (Phase A: SPEC-ONLY, PURE, ADDITIVE, RESEARCH-ONLY).

Human-approved build token (Phase A only):
HUMAN_APPROVED_BUILD_C22_REPLAY_SPECIFICATION_PHASE_A_SPEC_ONLY.

WHAT THIS IS: a PURE, deterministic freeze of *how* a future C22 fee-honest replay would be
run over the FROZEN V2 label evidence -- methodology, the exact forward data it needs,
proposed execution/cost model, required benchmarks + metrics, pre-committed rejection gates,
and a PROPOSED (not activated) lifecycle/token sequence. It IDENTIFIES every input a replay
needs and FAILS CLOSED where an input is not yet frozen.

WHAT THIS IS NOT: it runs / simulates NO replay, computes NO PnL, generates NO trade, fetches
/ stages NO data, issues / consumes NO token, unlocks NO gate, advances NO lifecycle/collection
state, edits NO V1/V2 artifact, optimizes NOTHING, and changes NO label / date / asset / signal
rule. Every capability flag is pinned False. It writes nothing by itself (a separate optional
report tool renders it).

SINGLE-SOURCED: signal set, sizing, dust/collision constants, leverage, and the exit triggers
are imported READ-ONLY from the FROZEN C22 detector/candidate spec and the V2 evidence contract;
no value is re-derived or invented. The replay-advance token is imported from the committed
labels-review contract.

PIVOTAL DATA FINDING (frozen here for human review): C22 exit conditions are evaluated against
the daily Trend Radar SNAPSHOT's `gc.upper` / `gc.filter` / `gc.trend` fields and radar
membership -- NOT against plain OHLC candles. Closing positions opened in the 26 frozen windows
therefore requires FORWARD daily Trend Radar snapshots AFTER 2026-07-15, which are a distinct,
not-yet-frozen dataset (the 2026-07-16/17/20 snapshots exist as future evidence but are
deliberately OUTSIDE V2). This is captured as a mandatory downstream data gate, not silently
resolved.
"""
from __future__ import annotations

import hashlib as _hashlib
import json as _json
from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v2_range_multi_window_real_candle_labels_contract as _v2  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_detector_spec_dry_run_contract as _dr  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_review_contract as _rev  # noqa: E501

SPEC_SCHEMA_VERSION = 1
SPEC_MODE = "RESEARCH_ONLY"
SPEC_LANE = "crypto_d1_auto_research"
BUILDER_VERSION = "replay_spec_phase_a_v1"
PHASE_A_BUILD_TOKEN = "HUMAN_APPROVED_BUILD_C22_REPLAY_SPECIFICATION_PHASE_A_SPEC_ONLY"

VERDICT_READY = "C22_REPLAY_SPEC_READY_FOR_HUMAN_REVIEW"
VERDICT_BLOCKED = "C22_REPLAY_SPEC_BLOCKED_BY_UNRESOLVED_REQUIREMENTS"

# --- FROZEN evidence (single-sourced from the V2 range contract semantics) -------------------
FROZEN_START = "2026-06-20"
FROZEN_END = "2026-07-15"
FROZEN_WINDOW_COUNT = 26
FROZEN_ROWS_PER_WINDOW = 50
FROZEN_TOTAL_ROWS = 1300
# actionable = non-NONE / non-SKIP entry signals in the frozen V2 artifact (13+72+3)
FROZEN_ACTIONABLE_LABELS = 88
FROZEN_ACTIONABLE_BREAKDOWN = {"LONG_ENTRY": 13, "BEAR_SHORT": 72, "HEDGE_SHORT": 3}
EXCLUDED_FUTURE_DATES = ("2026-07-16", "2026-07-17", "2026-07-20")

# signal set (single-sourced; never redefined)
SIGNALS = (_v2._v1.SIGNAL_LONG, _v2._v1.SIGNAL_HEDGE, _v2._v1.SIGNAL_BEAR,
           _v2._v1.SIGNAL_NONE, _v2._v1.SIGNAL_SKIP)
ACTIONABLE_SIGNALS = (_v2._v1.SIGNAL_LONG, _v2._v1.SIGNAL_HEDGE, _v2._v1.SIGNAL_BEAR)

# replay-advance human token (single-sourced from the committed labels-review contract)
REPLAY_ADVANCE_TOKEN = _rev.NEXT_ACTION_ADVANCE  # HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT

# provenance-tier boundaries (single-sourced from V2)
SIDECAR_MANDATORY_FROM = _v2.SIDECAR_MANDATORY_FROM   # 2026-06-28
RAW_MANDATORY_FROM = _v2.RAW_MANDATORY_FROM           # 2026-07-10
FROZEN_TIER_COUNTS = {"LEGACY_REDUCED_ONLY": 8,
                      "LEGACY_REDUCED_WITH_SIDECAR_NO_RAW": 12,
                      "FULL_RAW_REDUCTION_PROVENANCE": 6}

# forward exit-path deterministic horizon (PROPOSED, fail-closed; see notes below).
# NOT tuned to any observed outcome -- it is the daily decision cadence rounded to a full
# calendar month. If any position is still open at END_OF_TEST it is force-liquidated and
# flagged FORCED_OPEN_AT_END_OF_TEST (excluded from edge attribution).
PROPOSED_MAX_HOLD_HORIZON_CALENDAR_DAYS = 30
PROPOSED_END_OF_TEST_BASIS = "last_decision_date_plus_horizon_or_all_positions_closed"


def _frozen_evidence_block() -> dict:
    dates = _v2._v1._daterange(FROZEN_START, FROZEN_END)
    return {
        "date_range": [FROZEN_START, FROZEN_END],
        "expected_dates": list(dates),
        "decision_windows": FROZEN_WINDOW_COUNT,
        "rows_per_window": FROZEN_ROWS_PER_WINDOW,
        "total_label_rows": FROZEN_TOTAL_ROWS,
        "actionable_labels": FROZEN_ACTIONABLE_LABELS,
        "actionable_breakdown": FROZEN_ACTIONABLE_BREAKDOWN,
        "no_date_after": FROZEN_END,
        "excluded_future_dates": list(EXCLUDED_FUTURE_DATES),
        "no_asset_or_date_cherry_picking": True,
        "provenance_tier_counts_retained_in_attribution": FROZEN_TIER_COUNTS,
        "sidecar_mandatory_from": SIDECAR_MANDATORY_FROM,
        "raw_mandatory_from": RAW_MANDATORY_FROM,
        "v2_artifact_filename": _v2.v2_artifact_filename(
            FROZEN_START, FROZEN_END, FROZEN_WINDOW_COUNT),
    }


def _signal_handling_block() -> dict:
    return {
        "signal_set_single_sourced": list(SIGNALS),
        "actionable_signals": list(ACTIONABLE_SIGNALS),
        "detector_rules_unchanged": True,
        "decision_timestamp": "the run/as-of date D of each frozen daily window; the detector "
                              "reads the LATEST CLOSED daily candle + that day's gc block",
        "earliest_permissible_entry": "the OPEN of the NEXT daily session after decision date "
                                      "D (next-bar); NEVER the same closed bar that produced "
                                      "the signal",
        "lookahead_prevention": ["no same-bar fill", "no use of any candle/gc field dated after "
                                 "the fill bar", "exit evaluation uses only closed bars up to "
                                 "the evaluation date"],
        "one_position_per_asset": True,
        "overlapping_or_repeated_signals": "while a position in an asset is open, further "
                                           "entry signals for that asset are SKIPPED (already-"
                                           "held); no pyramiding / no averaging",
        "already_held_behavior": "skip new entry; keep managing the open position under the "
                                 "frozen exit rules",
        "dust_handling": {"entry_min_pct_nav": _dr.ENTRY_DUST_PCT_NAV,
                          "entry_min_usd": _dr.ENTRY_DUST_USD,
                          "exit_min_usd": _dr.EXIT_DUST_USD,
                          "held_dust_usd": _dr.HELD_DUST_USD},
        "ticker_collision_handling": {"skip_if_relative_diff_exceeds": _dr.COLLISION_THRESH},
        "position_sizing_pct_nav": {
            "long_breakout_within_%dd" % _dr.BREAKOUT_RECENT_DAYS: _dr.LONG_SIZE_RECENT_PCT,
            "long_otherwise": _dr.LONG_SIZE_ELSE_PCT,
            "hedge_short": _dr.HEDGE_SHORT_PCT,
            "bear_short": _dr.BEAR_SHORT_PCT},
        "leverage": _dr.LEVERAGE,
        "leverage_restriction": "1x only; no borrow-financed leverage beyond the short "
                                "instrument's inherent mechanics",
        "max_gross_exposure_pct_nav": 100.0,
        "max_net_exposure_pct_nav": 100.0,
        "exposure_exceeds_nav_rule": "size on a live NAV snapshot; never reuse a percentage; "
                                     "cap cumulative deployed at 100% NAV; if a new entry would "
                                     "exceed 100% NAV it is SKIPPED (deterministic, by ascending "
                                     "market rank), never scaled to force a fit",
    }


def _exit_methodology_block() -> dict:
    return {
        "exit_triggers_single_sourced_from_frozen_spec": True,
        "long_exit_below_upper_band": "latest_closed_close < gc.upper (UPPER GC band)",
        "long_exit_out_of_radar": "asset no longer in Trend Radar top-50 results on the "
                                  "evaluation date",
        "short_stop_close_above_filter": "latest_closed_close > gc.filter",
        "short_take_profit": "latest_closed_close <= %.2f * derived_short_entry_price"
                             % _dr.SHORT_TP_MULT,
        "short_exit_out_of_radar": "asset no longer in Trend Radar results on the evaluation "
                                   "date",
        "end_of_test_forced_liquidation": "any position still open at END_OF_TEST is liquidated "
                                          "at that date's close and flagged "
                                          "FORCED_OPEN_AT_END_OF_TEST (excluded from edge "
                                          "attribution)",
        "missing_candle_behavior": "FAIL-CLOSED: a missing expected daily bar/snapshot on a "
                                   "holding date is a data-integrity failure; the replay "
                                   "refuses to run rather than infer/interpolate a price",
        "delisted_or_unavailable_asset": "treated as out-of-radar -> exit at the last available "
                                         "close; flagged DELISTED_EXIT (not counted as a "
                                         "rule-based edge exit)",
        "max_holding_period_in_frozen_spec": None,
        "max_holding_period_note": "the FROZEN detector spec defines NO maximum holding period; "
                                   "positions are held until a frozen exit condition triggers. "
                                   "The only bound is the fail-closed END_OF_TEST horizon "
                                   "(PROPOSED %dd), which forces liquidation and is NOT a "
                                   "detector rule." % PROPOSED_MAX_HOLD_HORIZON_CALENDAR_DAYS,
        "unresolved_items": ["exact derived_short_entry_price reference (entry fill price vs "
                             "signal-bar close) must be pinned at dry-run against the frozen "
                             "entry-fill rule"],
    }


def _price_path_data_contract() -> dict:
    return {
        "critical_finding": "exit evaluation needs the daily Trend Radar SNAPSHOT (gc.upper, "
                            "gc.filter, gc.trend + radar membership), NOT plain OHLC candles; "
                            "only the take-profit (close <= 0.65*entry) is pure-price",
        "required_fields_per_asset_per_day": ["asset_identifier", "exchange_or_price_source",
                                              "ohlc.h", "ohlc.c", "gc.upper", "gc.filter",
                                              "gc.trend", "radar_membership(top-50 rank)"],
        "timeframe": "daily (D1), same cadence as collection",
        "timezone_and_daily_close_boundary": "the exact vendor Trend Radar daily close boundary "
                                             "used by the frozen windows (must match the "
                                             "collection convention; not inferred from data)",
        "entry_context_range": [FROZEN_START, FROZEN_END],
        "exit_path_range": ["2026-07-16", "END_OF_TEST (deterministic; see rule)"],
        "warm_up_requirements": "none for band/filter recomputation -- gc.upper/gc.filter are "
                               "vendor-provided per snapshot; previous_close for crossover is "
                               "the prior snapshot's latest-closed close (one prior daily bar)",
        "corporate_or_token_symbol_mapping": "exchange:symbol mapping frozen per the candidate "
                                            "spec's explicit collision/mapping rule; no "
                                            "silent re-mapping",
        "missing_bar_policy": "FAIL-CLOSED: any missing expected daily snapshot in the "
                             "contiguous exit-path range aborts the replay",
        "duplicate_bar_rejection": "duplicate (asset,date) rows are rejected, never merged",
        "deterministic_source_manifest": "per-file SHA-256 + (asset,date) coverage map; the "
                                         "exit-path dataset is a DISTINCT frozen artifact with "
                                         "its own manifest, separate from the V2 entry evidence",
        "end_of_test_fail_closed_rule": {
            "why_variable": "exits are open-ended; the true end date is not known a priori",
            "rule": "END_OF_TEST = min(date by which ALL open positions have closed under "
                    "frozen exit rules, last_decision_date + %dd). The exit-path dataset MUST "
                    "provide a CONTIGUOUS daily snapshot sequence from 2026-07-16 through "
                    "END_OF_TEST. If coverage is incomplete, the replay FAILS CLOSED (does not "
                    "run). Any position still open at END_OF_TEST is force-liquidated + flagged."
                    % PROPOSED_MAX_HOLD_HORIZON_CALENDAR_DAYS,
            "proposed_horizon_calendar_days": PROPOSED_MAX_HOLD_HORIZON_CALENDAR_DAYS,
            "horizon_is_proposed_not_tuned": True,
        },
        "no_fetch_in_this_task": True,
    }


def price_path_missing_data_inventory() -> dict:
    """The exact forward data that must be frozen + human-reviewed before a replay can run."""
    return {
        "status": "NOT_FROZEN_NOT_AUTHORIZED",
        "missing": [
            "contiguous daily Trend Radar snapshots (gc.upper/gc.filter/gc.trend + membership + "
            "ohlc.h/ohlc.c) for every trading date from 2026-07-16 through END_OF_TEST",
            "a deterministic exit-path source manifest (per-file SHA-256 + coverage map)",
            "human confirmation of END_OF_TEST horizon and of admitting post-2026-07-15 "
            "snapshots for EXIT-ONLY evaluation (no new entries after 2026-07-15)",
        ],
        "already_on_disk_but_out_of_scope_until_gated": ["2026-07-16", "2026-07-17", "2026-07-20"],
        "hard_rule": "post-2026-07-15 snapshots are admissible for EXIT EVALUATION ONLY; they "
                     "MUST NOT create new entries and MUST NOT enter the V2 entry evidence",
        "gate_required_before_use": "C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW",
    }


def _execution_and_cost_model() -> dict:
    return {
        "note_not_silently_inheriting_37bps": True,
        "entry_price_reference": "next daily session OPEN after decision date D (next-bar)",
        "exit_price_reference": "next daily session OPEN after the exit-trigger evaluation date",
        "gap_handling": "fill at the actual next-bar open even if it gaps beyond the trigger "
                        "level (no fill at the theoretical level)",
        "execution_style": "next-bar market execution; no same-bar fills",
        "proposed_transaction_cost_all_in_round_trip_bps": 37.0,
        "transaction_cost_scope": "PROPOSED baseline for BOTH long and short legs: taker fee + "
                                  "slippage + half-spread on entry and on exit (37 bps all-in "
                                  "round trip). This is the spot house baseline (C10/C11/C12) "
                                  "and is APPROPRIATE for the LONG leg; for SHORT it covers only "
                                  "the transaction, NOT the carry",
        "short_specific_costs_must_be_separately_modeled": {
            "instrument_unresolved": "the frozen detector spec does NOT fix the short "
                                     "instrument (perp vs spot-margin); this MUST be decided by "
                                     "human review before replay",
            "if_perp": "add perpetual funding accrued per HELD day (sign-correct) + perp taker "
                       "fee tier",
            "if_spot_margin": "add borrow interest accrued per HELD day + margin fee tier",
            "borrow_or_funding_drag_reported_separately": True,
        },
        "spread_assumption": "half-spread included inside the 37 bps; a wider explicit spread "
                             "may be required for thin top-50 names (flag, do not soften)",
        "turnover_calculation": "one round-trip per closed position; per-asset and portfolio "
                               "turnover reported; used in a turnover-sanity cross-check",
        "liquidity_constraints": "top-50 rank membership is the liquidity proxy; a per-name "
                                 "notional cap may be required (flag for human review)",
        "partial_fill_policy": "assume full fill at the next-bar open for top-50 names at the "
                               "proposed sizes; partial-fill modeling is out of scope for v1 "
                               "and flagged",
        "rejected_fill_policy": "if the next bar is missing (no open), the trade is FAIL-CLOSED "
                               "as a data-integrity error, not silently dropped",
    }


def _benchmarks_block() -> dict:
    return {
        "required": ["BTC_buy_and_hold", "equal_weight_passive_universe",
                     "zero_return_always_flat_null", "fixed_seed_random_entry_null",
                     "c22_signal_off_null", "gross_vs_net_strategy"],
        "fair_comparison_boundaries": {
            "date_range": [FROZEN_START, "END_OF_TEST"],
            "pricing": "same next-bar-open references and same daily snapshots",
            "costs": "same transaction-cost model applied to every benchmark that trades "
                     "(random-entry, signal-off entries); buy-and-hold pays one round trip",
        },
        "random_entry_determinism": "fixed seed; entry dates/assets drawn from the same 26 "
                                    "frozen windows so the null shares the strategy's "
                                    "opportunity set",
    }


def _required_results_block() -> dict:
    return {
        "return": ["gross_return", "net_return"],
        "annualized_return_with_short_sample_warning": True,
        "risk": ["max_drawdown", "sharpe", "calmar"],
        "trade_stats": ["win_rate", "closed_trade_count", "open_trade_count", "turnover"],
        "cost_drags": ["fee_drag", "slippage_drag", "borrow_or_funding_drag"],
        "attribution": ["long_contribution", "hedge_short_contribution", "bear_short_contribution",
                        "performance_by_asset", "performance_by_decision_date",
                        "performance_by_provenance_tier"],
        "exposure": ["exposure_over_time", "concentration"],
        "comparison": ["benchmark_comparison_table"],
        "integrity_audit": ["duplicate_trade_audit", "lookahead_audit"],
        "provenance_tiers_retained": FROZEN_TIER_COUNTS,
    }


def _precommitted_rejection_gates() -> dict:
    """Testable, pre-committed BEFORE any run; never tuned to the observed outcome."""
    return {
        "integrity_rejection": ["any duplicate trade", "any lookahead violation",
                                "cost arithmetic mismatch", "missing/interpolated bar used",
                                "provenance tiers not retained in attribution"],
        "execution_or_data_rejection": ["exit-path dataset not contiguous 2026-07-16..END_OF_TEST",
                                        "any missing expected daily snapshot on a holding date",
                                        "short instrument/carry model unspecified at run time",
                                        "a post-2026-07-15 snapshot used to create a new entry"],
        "economic_performance_rejection": [
            "net return <= 0 after costs",
            "non-positive net Sharpe",
            "does NOT beat the fixed-seed random-entry null on a risk-adjusted basis",
            "does NOT beat BTC buy-and-hold on a risk-adjusted basis",
            "forward/held-out segment not positive"],
        "insufficient_statistical_power_warning": {
            "actionable_labels": FROZEN_ACTIONABLE_LABELS,
            "decision_windows": FROZEN_WINDOW_COUNT,
            "warning": "88 actionable entries over 26 daily windows is a SHORT, low-power path; "
                       "annualized figures are fragile and any result is INDICATIVE, not "
                       "conclusive; a WARNING is mandatory on every annualized metric",
            "min_actionable_labels_reference": _rev.MIN_ACTIONABLE_LABELS_FOR_REPLAY},
        "no_post_run_rescue": True,
        "no_parameter_change_after_run": True,
        "no_selective_rerun": True,
        "negative_results_preserved": True,
    }


def _proposed_lifecycle_gates() -> list:
    """PROPOSED additive gate sequence + human token per gate. NOT activated; the live
    lifecycle orchestrator is NOT edited by this contract."""
    return [
        {"gate": "C22_REPLAY_SPEC_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews THIS frozen replay specification",
         "human_token": "HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE"},
        {"gate": "C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews the frozen exit-path snapshot dataset + manifest (exit-only "
                    "use of post-2026-07-15 snapshots)",
         "human_token": "HUMAN_DECISION_C22_FORWARD_PRICE_DATA_ACCEPT_OR_REJECT"},
        {"gate": "C22_DRY_RUN_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews the synthetic/no-PnL dry-run wiring (entry/exit/no-lookahead)",
         "human_token": "HUMAN_DECISION_C22_DRY_RUN_ACCEPT_OR_REJECT"},
        {"gate": "C22_FEE_HONEST_REPLAY_READY_FOR_HUMAN_AUTHORIZATION",
         "purpose": "human authorizes the ONE fee-honest replay run",
         "human_token": REPLAY_ADVANCE_TOKEN},
        {"gate": "C22_REPLAY_RESULTS_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews the frozen results + accept/reject decision",
         "human_token": "HUMAN_DECISION_C22_REPLAY_RESULTS_ACCEPT_OR_REJECT"},
    ]


_CAPABILITY_FLAGS_FALSE = (
    "runs_replay", "simulates_replay", "runs_backtest", "computes_pnl", "generates_trades",
    "fetches_data", "reads_real_data", "stages_data", "mutates_data",
    "mutates_v1_v2_artifacts", "optimizes_parameters", "tunes_parameters", "reparameterizes",
    "changes_labels", "changes_dates", "changes_assets", "changes_signal_rules",
    "unlocks_replay_gate", "advances_lifecycle", "changes_collection_state", "issues_token",
    "consumes_token", "auto_commits", "auto_pushes", "uses_network", "uses_credentials",
    "uses_mcp", "connects_signum", "places_orders", "paper_trading", "live_trading",
    "deploys_capital", "advances_without_human_approval", "invents_rule_values",
    "claims_profitability", "claims_edge",
)


def build_replay_spec() -> dict:
    """PURE. Assemble the full frozen replay specification. Writes NOTHING; authorizes NOTHING.
    Fails closed (verdict BLOCKED) if any frozen-evidence invariant is internally inconsistent."""
    blockers: list = []
    ev = _frozen_evidence_block()
    if len(ev["expected_dates"]) != FROZEN_WINDOW_COUNT:
        blockers.append("expected_dates_len_ne_window_count")
    if FROZEN_WINDOW_COUNT * FROZEN_ROWS_PER_WINDOW != FROZEN_TOTAL_ROWS:
        blockers.append("window_row_math_inconsistent")
    if sum(FROZEN_ACTIONABLE_BREAKDOWN.values()) != FROZEN_ACTIONABLE_LABELS:
        blockers.append("actionable_breakdown_sum_mismatch")
    if sum(FROZEN_TIER_COUNTS.values()) != FROZEN_WINDOW_COUNT:
        blockers.append("tier_counts_do_not_sum_to_windows")
    if any(d > FROZEN_END for d in ev["expected_dates"]):
        blockers.append("frozen_date_after_end")
    if any(d in ev["expected_dates"] for d in EXCLUDED_FUTURE_DATES):
        blockers.append("excluded_future_date_in_frozen_range")

    spec: dict[str, Any] = {
        "spec": "c22_signum_trend_radar_gc_long_short_v1_replay_specification",
        "schema_version": SPEC_SCHEMA_VERSION, "builder_version": BUILDER_VERSION,
        "mode": SPEC_MODE, "lane": SPEC_LANE, "candidate_id": _v2._v1.CANDIDATE_ID,
        "phase": "A_SPEC_ONLY", "phase_a_build_token": PHASE_A_BUILD_TOKEN,
        "frozen_evidence": ev,
        "signal_handling": _signal_handling_block(),
        "exit_methodology": _exit_methodology_block(),
        "price_path_data_contract": _price_path_data_contract(),
        "price_path_missing_data_inventory": price_path_missing_data_inventory(),
        "execution_and_cost_model": _execution_and_cost_model(),
        "benchmarks": _benchmarks_block(),
        "required_results": _required_results_block(),
        "precommitted_rejection_gates": _precommitted_rejection_gates(),
        "proposed_lifecycle_gates": _proposed_lifecycle_gates(),
        "replay_advance_token": REPLAY_ADVANCE_TOKEN,
        "human_review_required": True,
        "verdict": (VERDICT_READY if not blockers else VERDICT_BLOCKED),
        "blockers": blockers,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        spec[flag] = False
    spec["spec_sha256"] = _hashlib.sha256(canonical_spec_bytes(spec)).hexdigest()
    return spec


def canonical_spec_bytes(spec: dict) -> bytes:
    """Byte-stable serialization (indent=2, sort_keys, trailing newline). Excludes the
    self-referential spec_sha256 field so the hash is stable and reproducible."""
    payload = {k: v for k, v in spec.items() if k != "spec_sha256"}
    return _json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def validate_replay_spec(spec: Any) -> dict:
    """Anti-tamper validator. Valid only when research-only + spec-only, every capability flag
    False, frozen evidence exact (26/1300/88, tiers 8/12/6, no date > 2026-07-15, Jul16/17/20
    excluded), costs+benchmarks present and non-omittable, rejection gates present, the exit-path
    dataset is fail-closed + gated, the replay-advance token is the canonical one, and (READY)
    there are no blockers."""
    f: list = []
    if not isinstance(spec, dict):
        return {"valid": False, "failures": ["spec_not_a_dict"]}
    s = spec
    if s.get("mode") != SPEC_MODE:
        f.append("mode_not_research_only")
    if s.get("phase") != "A_SPEC_ONLY":
        f.append("not_phase_a_spec_only")
    ev = s.get("frozen_evidence") or {}
    if ev.get("date_range") != [FROZEN_START, FROZEN_END]:
        f.append("date_range_wrong")
    if ev.get("decision_windows") != FROZEN_WINDOW_COUNT:
        f.append("window_count_wrong")
    if ev.get("total_label_rows") != FROZEN_TOTAL_ROWS:
        f.append("total_rows_wrong")
    if ev.get("actionable_labels") != FROZEN_ACTIONABLE_LABELS:
        f.append("actionable_labels_wrong")
    if ev.get("provenance_tier_counts_retained_in_attribution") != FROZEN_TIER_COUNTS:
        f.append("tier_counts_wrong")
    for d in EXCLUDED_FUTURE_DATES:
        if d in (ev.get("expected_dates") or []):
            f.append("excluded_future_date_present:%s" % d)
    if any(d > FROZEN_END for d in (ev.get("expected_dates") or [])):
        f.append("date_after_frozen_end")
    # costs + benchmarks cannot be omitted
    if not s.get("execution_and_cost_model"):
        f.append("cost_model_missing")
    bm = (s.get("benchmarks") or {}).get("required") or []
    for req in ("BTC_buy_and_hold", "fixed_seed_random_entry_null", "c22_signal_off_null"):
        if req not in bm:
            f.append("benchmark_missing:%s" % req)
    if not s.get("required_results"):
        f.append("required_results_missing")
    if not s.get("precommitted_rejection_gates"):
        f.append("rejection_gates_missing")
    # exit-path data must be fail-closed + gated (not silently resolved)
    inv = s.get("price_path_missing_data_inventory") or {}
    if inv.get("status") != "NOT_FROZEN_NOT_AUTHORIZED":
        f.append("missing_data_inventory_not_fail_closed")
    if inv.get("gate_required_before_use") != "C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW":
        f.append("forward_data_gate_missing")
    # token single-sourced
    if s.get("replay_advance_token") != REPLAY_ADVANCE_TOKEN:
        f.append("replay_advance_token_not_canonical")
    # capability flags
    for flag in _CAPABILITY_FLAGS_FALSE:
        if s.get(flag) is not False:
            f.append("capability_flag_true:%s" % flag)
    # hash integrity
    if s.get("spec_sha256") and s["spec_sha256"] != _hashlib.sha256(
            canonical_spec_bytes(s)).hexdigest():
        f.append("spec_hash_mismatch")
    if s.get("verdict") == VERDICT_READY and s.get("blockers"):
        f.append("ready_with_blockers")
    return {"valid": not f, "failures": f}

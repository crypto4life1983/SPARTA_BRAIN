"""Candidate #22 -- external_signum_trend_radar_gc_long_short_v1
-- REPLAY SPECIFICATION (Phase A: SPEC-ONLY, PURE, ADDITIVE, RESEARCH-ONLY).

Human-approved build token (Phase A only):
HUMAN_APPROVED_BUILD_C22_REPLAY_SPECIFICATION_PHASE_A_SPEC_ONLY.

REVISION REV1 -- authored under the first human review decision
HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE = REVISE. Nine points were tightened:
 (1) no artificial 30-day *strategy* exit -- forced/administrative liquidation is a
     non-decisive truncation diagnostic only; unresolved positions after the reviewed
     forward coverage yield BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA and the coverage
     is EXTENDED in deterministic predeclared increments until every position closes
     naturally;
 (2) the short instrument stays UNRESOLVED behind a separate human selection + feasibility
     gate (perp+funding vs spot-margin+borrow), fail-closed on missing feasibility;
 (3) transaction costs are DISAGGREGATED (fee-in/fee-out/spread/slip-in/slip-out/funding-or-
     borrow/exceptional-exit); 37 bps survives only as a labelled sensitivity case, never the
     base case; base case comes from a separately reviewed execution-data contract frozen
     before replay; gross / transaction-cost-only / fully-net all required;
 (4) forward Trend Radar snapshot use is specified (which export, weekend/non-export,
     Friday->Monday, out-of-radar definition, malformed-export = fail-closed, timestamp
     alignment); post-2026-07-15 snapshots are EXIT_ONLY and rejected for any entry;
 (5) delisting is SEPARATED from out-of-radar (5 explicit categories, no invented price);
 (6) exposure ordering is deterministic (date -> market rank -> asset id), exits before
     entries, one position/asset, no simultaneous long+short, gross <= 100% NAV, deterministic
     rejection (never proportional resize);
 (7) benchmarks are survivorship-free + the random null is matched to side mix / holding
     process / exposure / costs and may not use easier execution than C22;
 (8) the ill-defined "held-out positive" hard gate becomes a LABELLED, NON-DECISIVE
     robustness diagnostic (no arbitrary decisive holdout over only 26 windows);
 (9) rejection gates are kept as four clearly separated classes; annualized metrics on this
     short sample are marked non-conclusive; no post-run rescue/rerun/selective removal.

WHAT THIS IS NOT: it runs / simulates NO replay, computes NO PnL, generates NO trade, fetches
/ admits NO data, issues / consumes NO token, unlocks NO gate, advances NO lifecycle/collection
state, edits NO V1/V2 artifact / detector / orchestrator / tracker / state file, optimizes
NOTHING, and changes NO label / date / asset / signal rule. Every capability flag is pinned
False. Signal set, sizing, dust/collision constants, leverage and the exit TRIGGERS are
imported READ-ONLY from the frozen detector/candidate spec and the V2 evidence contract; no
value is re-derived. The replay-advance token is imported from the committed labels-review
contract.
"""
from __future__ import annotations

import hashlib as _hashlib
import json as _json
from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v2_range_multi_window_real_candle_labels_contract as _v2  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_detector_spec_dry_run_contract as _dr  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_review_contract as _rev  # noqa: E501

SPEC_SCHEMA_VERSION = 2
SPEC_MODE = "RESEARCH_ONLY"
SPEC_LANE = "crypto_d1_auto_research"
BUILDER_VERSION = "replay_spec_phase_a_rev1"
REVISION = "REV1_POST_FIRST_HUMAN_REVIEW"
REVISE_DECISION_REF = "HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE=REVISE"
PHASE_A_BUILD_TOKEN = "HUMAN_APPROVED_BUILD_C22_REPLAY_SPECIFICATION_PHASE_A_SPEC_ONLY"

VERDICT_READY = "C22_REPLAY_SPEC_READY_FOR_SECOND_HUMAN_REVIEW"
VERDICT_BLOCKED = "C22_REPLAY_SPEC_BLOCKED_BY_UNRESOLVED_REQUIREMENTS"

# --- FROZEN evidence (single-sourced from the V2 range contract semantics) -------------------
FROZEN_START = "2026-06-20"
FROZEN_END = "2026-07-15"
FROZEN_WINDOW_COUNT = 26
FROZEN_ROWS_PER_WINDOW = 50
FROZEN_TOTAL_ROWS = 1300
FROZEN_ACTIONABLE_LABELS = 88               # 13 LONG + 72 BEAR + 3 HEDGE (non-NONE/non-SKIP)
FROZEN_ACTIONABLE_BREAKDOWN = {"LONG_ENTRY": 13, "BEAR_SHORT": 72, "HEDGE_SHORT": 3}
EXCLUDED_FUTURE_DATES = ("2026-07-16", "2026-07-17", "2026-07-20")
NO_NEW_ENTRY_AFTER = FROZEN_END

SIGNALS = (_v2._v1.SIGNAL_LONG, _v2._v1.SIGNAL_HEDGE, _v2._v1.SIGNAL_BEAR,
           _v2._v1.SIGNAL_NONE, _v2._v1.SIGNAL_SKIP)
ACTIONABLE_SIGNALS = (_v2._v1.SIGNAL_LONG, _v2._v1.SIGNAL_HEDGE, _v2._v1.SIGNAL_BEAR)
REPLAY_ADVANCE_TOKEN = _rev.NEXT_ACTION_ADVANCE  # HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT

SIDECAR_MANDATORY_FROM = _v2.SIDECAR_MANDATORY_FROM   # 2026-06-28
RAW_MANDATORY_FROM = _v2.RAW_MANDATORY_FROM           # 2026-07-10
FROZEN_TIER_COUNTS = {"LEGACY_REDUCED_ONLY": 8,
                      "LEGACY_REDUCED_WITH_SIDECAR_NO_RAW": 12,
                      "FULL_RAW_REDUCTION_PROVENANCE": 6}

# --- REV1 (point 1): deterministic forward exit-path REVIEW + EXTENSION, no strategy max-hold
INITIAL_FORWARD_REVIEW_CALENDAR_DAYS = 30      # first exit-only coverage window to review
FORWARD_EXTENSION_INCREMENT_CALENDAR_DAYS = 15  # predeclared deterministic extension step
BLOCKED_INSUFFICIENT_FORWARD = "BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA"

# --- REV1 (point 5): delisting / unavailability taxonomy (separate from out-of-radar) --------
UNAVAILABILITY_CATEGORIES = (
    "ABSENT_FROM_TOP50",            # valid export, asset simply not in top-50 -> out-of-radar
    "MISSING_FROM_SINGLE_EXPORT",   # traded but absent from one otherwise-valid export -> flag
    "TEMPORARY_SUSPENSION",         # halted, no executable price -> hold + flag, never invent
    "PERMANENT_DELISTING",          # exit only at a real last executable price, flagged
    "NO_EXECUTABLE_NEXT_BAR",       # data-integrity fail-closed unless permanent-delist rule
)


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
        "no_new_entry_after": NO_NEW_ENTRY_AFTER,
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
        "decision_timestamp": "the run/as-of date D of each frozen daily window; detector reads "
                              "the LATEST CLOSED daily candle + that day's gc block",
        "earliest_permissible_entry": "the OPEN of the NEXT executable market session after "
                                      "decision date D (next-bar); NEVER the same closed bar",
        "no_new_entry_after": NO_NEW_ENTRY_AFTER,
        "lookahead_prevention": ["no same-bar fill", "no candle/gc field dated after the fill "
                                 "bar", "exit evaluation uses only closed bars up to the "
                                 "evaluation date"],
        "one_position_per_asset": True,
        "no_simultaneous_long_and_short_same_asset": True,
        "exit_ordering_vs_entry": "on any execution session EXITS are processed BEFORE entries "
                                  "(freed NAV becomes available to that session's entries)",
        "deterministic_competition_ordering": ["decision_date_ascending", "market_rank_ascending",
                                               "stable_asset_identifier_ascending"],
        "insufficient_nav_rule": "DETERMINISTIC REJECTION by the ordering above -- a signal that "
                                 "does not fit under the 100% NAV cap is SKIPPED, never "
                                 "proportionally resized",
        "signal_while_exit_pending": "if an asset's exit is pending on the same session, its new "
                                     "entry signal is SKIPPED (already-held until the exit fills "
                                     "on that session; no same-session flip)",
        "overlapping_or_repeated_signals": "while a position is open, further entries for that "
                                           "asset are SKIPPED (already-held); no pyramiding",
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
        "leverage_restriction": "1x only",
        "max_gross_exposure_pct_nav": 100.0,
        "max_net_exposure_pct_nav": 100.0,
        "long_and_short_implementation_stated_separately": True,
    }


def _exit_methodology_block() -> dict:
    return {
        "exit_triggers_single_sourced_from_frozen_spec": True,
        "long_exit_below_upper_band": "latest_closed_close < gc.upper (UPPER GC band)",
        "long_exit_out_of_radar": "asset no longer in a VALID Trend Radar top-50 export on the "
                                  "evaluation date",
        "short_stop_close_above_filter": "latest_closed_close > gc.filter",
        "short_take_profit": "latest_closed_close <= %.2f * derived_short_entry_price"
                             % _dr.SHORT_TP_MULT,
        "short_exit_out_of_radar": "asset no longer in a VALID Trend Radar export on the "
                                   "evaluation date",
        "max_holding_period_in_frozen_spec": None,
        "no_artificial_strategy_max_hold": True,
        "forced_or_administrative_liquidation": {
            "is_a_strategy_exit": False,
            "role": "NON-DECISIVE truncation diagnostic ONLY; shown separately; NEVER included "
                    "in decisive strategy metrics (net return / Sharpe / Calmar / benchmark "
                    "comparison)",
        },
        "unresolved_positions_after_reviewed_coverage": BLOCKED_INSUFFICIENT_FORWARD,
        "missing_candle_or_export_behavior": "FAIL-CLOSED on an expected export/trading session "
                                             "(data-integrity halt); never infer/interpolate a "
                                             "price and never silently exit",
        "delisting_handled_separately": True,
        "unresolved_items": ["exact derived_short_entry_price reference (entry fill price) "
                             "pinned at dry-run against the frozen entry-fill rule"],
    }


def _forward_exit_path_extension_rule() -> dict:
    return {
        "no_new_entries_after": NO_NEW_ENTRY_AFTER,
        "initial_review_calendar_days": INITIAL_FORWARD_REVIEW_CALENDAR_DAYS,
        "rule": ("Review an INITIAL %d calendar days of EXIT-ONLY forward coverage (from "
                 "2026-07-16). If any position is still open at the end of the reviewed "
                 "coverage, the result is %s and the coverage is EXTENDED in deterministic "
                 "predeclared increments of %d calendar days until EVERY open position closes "
                 "naturally under the frozen exit rules. The horizon is NOT a strategy exit."
                 % (INITIAL_FORWARD_REVIEW_CALENDAR_DAYS, BLOCKED_INSUFFICIENT_FORWARD,
                    FORWARD_EXTENSION_INCREMENT_CALENDAR_DAYS)),
        "extension_increment_calendar_days": FORWARD_EXTENSION_INCREMENT_CALENDAR_DAYS,
        "increment_is_predeclared_not_outcome_driven": True,
        "extension_defined_without_examining_economic_results": True,
        "administrative_liquidation_diagnostic_only": True,
        "administrative_liquidation_excluded_from_decisive_metrics": True,
        "weekend_and_non_export_handling": "exit sessions occur ONLY on valid daily export "
                                           "dates; weekends / non-export days have NO decision "
                                           "session and the open position simply carries; the "
                                           "extension increment is counted in CALENDAR days but "
                                           "evaluation happens only on export sessions",
    }


def _forward_snapshot_alignment_block() -> dict:
    return {
        "authoritative_export_for_gc_fields": "the daily Signum Trend Radar 'gc/crypto' export "
                                              "for the evaluation date -- the same export family "
                                              "and reduced top-50 convention as the frozen "
                                              "collection windows; determines gc.upper, "
                                              "gc.filter, gc.trend and top-50 radar membership",
        "weekend_non_export_dates": "carry the previous valid snapshot's position state; NO new "
                                    "exit decision is taken on a non-export date (no session)",
        "friday_positions_before_monday": "a Friday-held position is evaluated on Friday's "
                                          "export; the next executable market bar is the next "
                                          "export session (typically Monday); no weekend fills",
        "out_of_radar_definition": "absence from the reduced TOP-50 of a VALID, well-formed "
                                   "export on the evaluation date == out-of-radar",
        "malformed_or_unavailable_export": "FAIL-CLOSED replay halt on an expected trading/"
                                           "export session (NOT an exit, NOT a skip); a missing "
                                           "expected session is a data-integrity failure",
        "timestamp_alignment": "the Trend Radar export's daily-close boundary maps to the NEXT "
                               "executable market bar open; entries/exits fill at that next "
                               "bar; exact boundary is single-sourced from the collection "
                               "convention, never inferred from data",
        "post_2026_07_15_snapshots": "marked EXIT_ONLY in the exit-path manifest; admissible "
                                     "ONLY for exit evaluation of positions opened <= "
                                     "2026-07-15; REJECTED (fail-closed) if used to create any "
                                     "entry",
        "exit_only_manifest_marker": "EXIT_ONLY",
    }


def _delisting_and_unavailability_block() -> dict:
    return {
        "categories": list(UNAVAILABILITY_CATEGORIES),
        "ABSENT_FROM_TOP50": "valid export, asset not in top-50 -> ordinary out-of-radar exit at "
                             "the next executable bar",
        "MISSING_FROM_SINGLE_EXPORT": "asset still trading but absent from ONE otherwise-valid "
                                      "export -> flagged SINGLE_EXPORT_ABSENCE; treated as "
                                      "out-of-radar but reported separately for human review, "
                                      "never silently",
        "TEMPORARY_SUSPENSION": "market halted / no executable price -> HOLD the position, flag "
                                "SUSPENDED; never invent a price; if it cannot resolve within "
                                "reviewed coverage -> %s" % BLOCKED_INSUFFICIENT_FORWARD,
        "PERMANENT_DELISTING": "exit ONLY at a real last executable market price, flagged "
                               "DELISTED_EXIT; excluded from decisive edge attribution; NO "
                               "invented/ favourable liquidation price",
        "NO_EXECUTABLE_NEXT_BAR": "data-integrity FAIL-CLOSED, unless the PERMANENT_DELISTING "
                                  "last-real-price rule applies (then flagged)",
        "delisting_not_treated_as_ordinary_out_of_radar": True,
        "all_unavailable_market_assumptions_flagged_and_reported_separately": True,
        "never_invent_favourable_price": True,
    }


def _price_path_data_contract() -> dict:
    return {
        "critical_finding": "exit evaluation needs the daily Trend Radar SNAPSHOT (gc.upper, "
                            "gc.filter, gc.trend + radar membership), NOT plain OHLC candles; "
                            "only the take-profit (close <= 0.65*entry) is pure-price",
        "required_fields_per_asset_per_day": ["asset_identifier", "exchange_or_price_source",
                                              "ohlc.h", "ohlc.c", "gc.upper", "gc.filter",
                                              "gc.trend", "radar_membership(top-50 rank)"],
        "timeframe": "daily (D1), same cadence + close boundary as collection",
        "entry_context_range": [FROZEN_START, FROZEN_END],
        "exit_path_range": ["2026-07-16", "until all positions close naturally (extended "
                            "deterministically) or %s" % BLOCKED_INSUFFICIENT_FORWARD],
        "warm_up_requirements": "gc.upper/gc.filter are vendor-provided per snapshot (no "
                               "recomputation); crossover needs one prior daily snapshot's "
                               "latest-closed close",
        "long_vs_short_price_series": "stated SEPARATELY -- the same OHLC series is NOT assumed "
                                      "for both; the short leg's series follows the chosen short "
                                      "instrument (see short_instrument_gate)",
        "duplicate_bar_rejection": "duplicate (asset,date) rows rejected, never merged",
        "deterministic_source_manifest": "per-file SHA-256 + (asset,date) coverage map; exit-"
                                         "path dataset is a DISTINCT frozen artifact, separate "
                                         "from V2 entry evidence, with post-2026-07-15 rows "
                                         "marked EXIT_ONLY",
        "no_fetch_in_this_task": True,
    }


def price_path_missing_data_inventory() -> dict:
    return {
        "status": "NOT_FROZEN_NOT_AUTHORIZED",
        "missing": [
            "contiguous daily Trend Radar snapshots (gc.upper/gc.filter/gc.trend + membership + "
            "ohlc.h/ohlc.c) from 2026-07-16 until every position closes naturally under the "
            "frozen rules (deterministic %d-day extension from an initial %d-day review)"
            % (FORWARD_EXTENSION_INCREMENT_CALENDAR_DAYS, INITIAL_FORWARD_REVIEW_CALENDAR_DAYS),
            "a deterministic exit-path source manifest (per-file SHA-256 + coverage map, "
            "post-2026-07-15 rows marked EXIT_ONLY)",
            "the chosen short instrument's historical price + funding/borrow series",
        ],
        "already_on_disk_but_out_of_scope_until_gated": ["2026-07-16", "2026-07-17", "2026-07-20"],
        "hard_rule": "post-2026-07-15 snapshots are EXIT_ONLY; they MUST NOT create new entries "
                     "and MUST NOT enter the V2 entry evidence",
        "insufficient_data_outcome": BLOCKED_INSUFFICIENT_FORWARD,
        "gate_required_before_use": "C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW",
    }


def _short_instrument_gate() -> dict:
    return {
        "status": "UNRESOLVED_PENDING_SEPARATE_HUMAN_SELECTION",
        "thirty_seven_bps_short_model_approved": False,
        "options": {
            "linear_perpetual_futures": "requires historical funding series (sign-correct, per "
                                        "held day)",
            "spot_margin_short": "requires historical borrow AVAILABILITY + borrow cost series",
        },
        "required_before_dry_run": ["explicit venue", "explicit symbol map (spot<->derivative, "
                                    "deterministic)", "instrument type", "historical price "
                                    "source"],
        "fail_closed_when": [
            "the required short instrument did not exist on the signal date",
            "historical funding (perp) or borrow cost (margin) is missing",
            "borrow availability cannot be established",
            "the spot and derivative symbol cannot be mapped deterministically",
            "the execution price source differs materially from the signal-price source "
            "without an approved basis adjustment",
        ],
        "long_and_short_stated_separately": True,
        "same_ohlc_for_both_not_assumed": True,
        "gate_required_before_dry_run": "C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW",
    }


def _execution_and_cost_model() -> dict:
    return {
        "note_not_silently_inheriting_37bps": True,
        "entry_price_reference": "next executable market session OPEN after decision date D",
        "exit_price_reference": "next executable market session OPEN after the exit-trigger "
                                "evaluation date",
        "gap_handling": "fill at the actual next-bar open even if it gaps beyond the trigger "
                        "level (no fill at the theoretical level)",
        "execution_style": "next-bar market execution; no same-bar fills",
        "disaggregated_cost_components": [
            "exchange_fee_entry", "exchange_fee_exit", "bid_ask_spread", "entry_slippage",
            "exit_slippage", "funding_or_borrow_cost", "exceptional_or_liquidation_exit_cost"],
        "base_case_values_source": "a SEPARATELY reviewed execution-data contract; the base-case "
                                   "component values MUST be frozen before replay (not set here)",
        "base_case_values_frozen_here": False,
        "thirty_seven_bps_role": "LABELLED SENSITIVITY CASE ONLY (not the approved base case)",
        "sensitivity_all_in_round_trip_bps": 37.0,
        "results_required_at_three_levels": ["gross", "transaction_cost_only", "fully_net"],
        "long_leg_costs": "spot fee-in/out + spread + slippage",
        "short_leg_costs": "transaction costs PLUS instrument-specific carry (perp funding OR "
                           "margin borrow) per held day -- pending the short-instrument "
                           "selection; modelled + reported separately",
        "turnover_calculation": "one round-trip per closed position; per-asset + portfolio; used "
                               "in a turnover-sanity cross-check",
        "liquidity_constraints": "top-50 membership is the liquidity proxy; a per-name notional "
                                 "cap may be required (flag for human review)",
        "partial_fill_policy": "assume full fill at next-bar open for top-50 names at proposed "
                               "sizes; partial-fill modelling out of scope for v1 (flagged)",
        "rejected_fill_policy": "missing next bar on an expected session -> FAIL-CLOSED "
                               "data-integrity error, never silently dropped",
    }


def _benchmarks_block() -> dict:
    return {
        "required": ["BTC_buy_and_hold", "equal_weight_passive_universe_point_in_time",
                     "zero_return_always_flat_null", "fixed_seed_matched_random_entry_null",
                     "c22_signal_off_control", "gross_vs_net_strategy"],
        "survivorship_bias_control": "the equal-weight passive universe uses ONLY assets KNOWN "
                                     "at each decision date (point-in-time top-50 membership); "
                                     "no asset admitted on later knowledge",
        "random_null_matching": "fixed seed; MATCHED to the strategy's side mix (long/hedge/"
                                "bear proportions), holding-duration process, exposure profile "
                                "and the SAME cost model; drawn from the same 26 frozen windows",
        "random_null_no_easier_execution": True,
        "fair_comparison_boundaries": {
            "date_range": [FROZEN_START, "natural close of all positions"],
            "pricing": "same next-bar-open references + same daily snapshots",
            "costs": "same disaggregated cost model for every benchmark that trades; "
                     "buy-and-hold pays one round trip",
        },
    }


def _required_results_block() -> dict:
    return {
        "return": ["gross_return", "transaction_cost_only_return", "net_return"],
        "annualized_return_marked_non_conclusive": True,
        "risk": ["max_drawdown", "sharpe", "calmar"],
        "trade_stats": ["win_rate", "closed_trade_count", "open_trade_count", "turnover"],
        "cost_drags": ["exchange_fee_drag", "spread_drag", "slippage_drag",
                       "funding_or_borrow_drag", "exceptional_exit_drag"],
        "attribution": ["long_contribution", "hedge_short_contribution",
                        "bear_short_contribution", "performance_by_asset",
                        "performance_by_decision_date", "performance_by_provenance_tier"],
        "exposure": ["exposure_over_time", "concentration"],
        "comparison": ["benchmark_comparison_table"],
        "integrity_audit": ["duplicate_trade_audit", "lookahead_audit"],
        "truncation_diagnostic_separate": "forced/administrative liquidation shown as a "
                                          "NON-DECISIVE truncation diagnostic, never in the "
                                          "decisive metrics",
        "provenance_tiers_retained": FROZEN_TIER_COUNTS,
    }


def _precommitted_rejection_gates() -> dict:
    return {
        "integrity_rejection": ["any duplicate trade", "any lookahead violation",
                                "cost arithmetic mismatch", "missing/interpolated bar used",
                                "provenance tiers not retained in attribution"],
        "data_or_execution_rejection": [
            "exit-path snapshots not contiguous from 2026-07-16 to natural close",
            "%s (positions unresolved after deterministic extension)" % BLOCKED_INSUFFICIENT_FORWARD,
            "short instrument/venue/symbol-map/carry not resolved + feasible at run time",
            "any post-2026-07-15 snapshot used to create a new entry",
            "malformed/missing expected export on a holding session"],
        "economic_performance_rejection": [
            "net return <= 0 after fully-net costs",
            "non-positive net Sharpe",
            "does NOT beat the matched fixed-seed random-entry null on a risk-adjusted basis",
            "does NOT beat BTC buy-and-hold on a risk-adjusted basis"],
        "insufficient_statistical_power_warning": {
            "actionable_labels": FROZEN_ACTIONABLE_LABELS,
            "decision_windows": FROZEN_WINDOW_COUNT,
            "warning": "88 actionable entries over 26 daily windows is a SHORT, low-power path; "
                       "annualized figures are NON-CONCLUSIVE and every annualized metric MUST "
                       "carry the warning; results are indicative only",
            "min_actionable_labels_reference": _rev.MIN_ACTIONABLE_LABELS_FOR_REPLAY},
        "held_out_segment": {
            "is_decisive_gate": False,
            "role": "LABELLED, NON-DECISIVE robustness diagnostic only",
            "rationale": "with only 26 decision windows an arbitrary decisive holdout would be "
                         "post-hoc and low-power; no repository convention defines a C22 "
                         "holdout, so it is NOT a hard rejection gate",
        },
        "no_post_run_rescue": True,
        "no_post_run_optimization": True,
        "no_parameter_change_after_run": True,
        "no_selective_asset_removal": True,
        "no_selective_date_removal": True,
        "no_selective_rerun": True,
        "negative_results_preserved": True,
    }


def _proposed_lifecycle_gates() -> list:
    return [
        {"gate": "C22_REPLAY_SPEC_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews the (revised) frozen replay specification",
         "human_token": "HUMAN_DECISION_C22_REPLAY_SPEC_ACCEPT_OR_REVISE"},
        {"gate": "C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews the frozen exit-path snapshot dataset + manifest AND the "
                    "resolved short instrument/venue/symbol-map/carry feasibility",
         "human_token": "HUMAN_DECISION_C22_FORWARD_PRICE_DATA_ACCEPT_OR_REJECT"},
        {"gate": "C22_DRY_RUN_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews the no-PnL dry-run wiring (entry/exit/no-lookahead/ordering)",
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
    "fetches_data", "admits_forward_data", "reads_real_data", "stages_data", "mutates_data",
    "mutates_v1_v2_artifacts", "modifies_detector", "modifies_lifecycle_orchestrator",
    "modifies_collection_tracker", "optimizes_parameters", "tunes_parameters", "reparameterizes",
    "changes_labels", "changes_dates", "changes_assets", "changes_signal_rules",
    "approves_short_instrument", "approves_cost_base_case", "unlocks_replay_gate",
    "advances_lifecycle", "changes_collection_state", "issues_token", "consumes_token",
    "auto_commits", "auto_pushes", "uses_network", "uses_credentials", "uses_mcp",
    "connects_signum", "places_orders", "paper_trading", "live_trading", "deploys_capital",
    "advances_without_human_approval", "invents_rule_values", "invents_prices",
    "claims_profitability", "claims_edge",
)


def build_replay_spec() -> dict:
    """PURE. Assemble the REV1 frozen replay specification. Writes NOTHING; authorizes NOTHING.
    Fails closed (verdict BLOCKED) on any internal frozen-evidence inconsistency."""
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
        "revision": REVISION, "revise_decision_ref": REVISE_DECISION_REF,
        "mode": SPEC_MODE, "lane": SPEC_LANE, "candidate_id": _v2._v1.CANDIDATE_ID,
        "phase": "A_SPEC_ONLY", "phase_a_build_token": PHASE_A_BUILD_TOKEN,
        "frozen_evidence": ev,
        "signal_handling": _signal_handling_block(),
        "exit_methodology": _exit_methodology_block(),
        "forward_exit_path_extension_rule": _forward_exit_path_extension_rule(),
        "forward_snapshot_alignment": _forward_snapshot_alignment_block(),
        "delisting_and_unavailability": _delisting_and_unavailability_block(),
        "price_path_data_contract": _price_path_data_contract(),
        "price_path_missing_data_inventory": price_path_missing_data_inventory(),
        "short_instrument_gate": _short_instrument_gate(),
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
    excluded), no artificial strategy max-hold + forced liquidation non-decisive, forward
    coverage extension deterministic, short instrument UNRESOLVED (37bps short not approved),
    costs disaggregated with 37bps only a sensitivity case, forward snapshots EXIT_ONLY + gated,
    delisting separated, exposure ordering deterministic, benchmarks survivorship-free + matched
    random null, held-out non-decisive, and the replay-advance token canonical."""
    f: list = []
    if not isinstance(spec, dict):
        return {"valid": False, "failures": ["spec_not_a_dict"]}
    s = spec
    if s.get("mode") != SPEC_MODE:
        f.append("mode_not_research_only")
    if s.get("phase") != "A_SPEC_ONLY":
        f.append("not_phase_a_spec_only")
    if s.get("revision") != REVISION:
        f.append("revision_marker_wrong")
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
    if ev.get("no_new_entry_after") != NO_NEW_ENTRY_AFTER:
        f.append("no_new_entry_after_wrong")
    for d in EXCLUDED_FUTURE_DATES:
        if d in (ev.get("expected_dates") or []):
            f.append("excluded_future_date_present:%s" % d)
    if any(d > FROZEN_END for d in (ev.get("expected_dates") or [])):
        f.append("date_after_frozen_end")
    # point 1: no artificial strategy max-hold; forced liquidation non-decisive
    em = s.get("exit_methodology") or {}
    if em.get("max_holding_period_in_frozen_spec") is not None:
        f.append("invented_max_holding_period")
    fl = em.get("forced_or_administrative_liquidation") or {}
    if fl.get("is_a_strategy_exit") is not False:
        f.append("forced_liquidation_treated_as_strategy_exit")
    if em.get("unresolved_positions_after_reviewed_coverage") != BLOCKED_INSUFFICIENT_FORWARD:
        f.append("unresolved_positions_outcome_wrong")
    fx = s.get("forward_exit_path_extension_rule") or {}
    if fx.get("extension_increment_calendar_days") != FORWARD_EXTENSION_INCREMENT_CALENDAR_DAYS \
            or not fx.get("increment_is_predeclared_not_outcome_driven"):
        f.append("forward_extension_rule_wrong")
    # point 2: short instrument unresolved, 37bps short not approved
    sg = s.get("short_instrument_gate") or {}
    if sg.get("status") != "UNRESOLVED_PENDING_SEPARATE_HUMAN_SELECTION":
        f.append("short_instrument_not_unresolved")
    if sg.get("thirty_seven_bps_short_model_approved") is not False:
        f.append("short_37bps_wrongly_approved")
    if not sg.get("fail_closed_when"):
        f.append("short_fail_closed_conditions_missing")
    # point 3: disaggregated costs; 37bps only sensitivity; base case not frozen here
    cm = s.get("execution_and_cost_model") or {}
    for comp in ("exchange_fee_entry", "exchange_fee_exit", "bid_ask_spread", "entry_slippage",
                 "exit_slippage", "funding_or_borrow_cost"):
        if comp not in (cm.get("disaggregated_cost_components") or []):
            f.append("cost_component_missing:%s" % comp)
    if cm.get("base_case_values_frozen_here") is not False:
        f.append("cost_base_case_wrongly_frozen_here")
    if "SENSITIVITY" not in str(cm.get("thirty_seven_bps_role", "")).upper():
        f.append("37bps_not_marked_sensitivity")
    for lvl in ("gross", "transaction_cost_only", "fully_net"):
        if lvl not in (cm.get("results_required_at_three_levels") or []):
            f.append("cost_result_level_missing:%s" % lvl)
    # point 4: forward snapshot alignment + EXIT_ONLY
    fa = s.get("forward_snapshot_alignment") or {}
    if fa.get("exit_only_manifest_marker") != "EXIT_ONLY":
        f.append("exit_only_marker_missing")
    if "FAIL-CLOSED" not in str(fa.get("malformed_or_unavailable_export", "")):
        f.append("malformed_export_not_fail_closed")
    # point 5: delisting separated
    du = s.get("delisting_and_unavailability") or {}
    if tuple(du.get("categories") or ()) != UNAVAILABILITY_CATEGORIES:
        f.append("delisting_categories_wrong")
    if du.get("delisting_not_treated_as_ordinary_out_of_radar") is not True \
            or du.get("never_invent_favourable_price") is not True:
        f.append("delisting_handling_wrong")
    # point 6: exposure ordering deterministic + rejection not resize
    sh = s.get("signal_handling") or {}
    if sh.get("deterministic_competition_ordering") != \
            ["decision_date_ascending", "market_rank_ascending",
             "stable_asset_identifier_ascending"]:
        f.append("exposure_ordering_wrong")
    if "REJECTION" not in str(sh.get("insufficient_nav_rule", "")).upper() \
            or "resized" not in str(sh.get("insufficient_nav_rule", "")):
        f.append("insufficient_nav_not_deterministic_rejection")
    if sh.get("no_simultaneous_long_and_short_same_asset") is not True:
        f.append("simultaneous_long_short_not_forbidden")
    if "EXITS are processed BEFORE entries" not in str(sh.get("exit_ordering_vs_entry", "")):
        f.append("exit_before_entry_not_stated")
    # point 7: benchmarks survivorship-free + matched random null, no easier execution
    bm = s.get("benchmarks") or {}
    req = bm.get("required") or []
    for b in ("BTC_buy_and_hold", "equal_weight_passive_universe_point_in_time",
              "fixed_seed_matched_random_entry_null", "c22_signal_off_control"):
        if b not in req:
            f.append("benchmark_missing:%s" % b)
    if not bm.get("survivorship_bias_control"):
        f.append("survivorship_control_missing")
    if bm.get("random_null_no_easier_execution") is not True:
        f.append("random_null_easier_execution_allowed")
    # point 8: held-out non-decisive
    rg = s.get("precommitted_rejection_gates") or {}
    ho = rg.get("held_out_segment") or {}
    if ho.get("is_decisive_gate") is not False:
        f.append("held_out_still_decisive")
    if any("held-out" in str(x).lower() or "forward/held-out" in str(x).lower()
           for x in (rg.get("economic_performance_rejection") or [])):
        f.append("held_out_still_in_economic_rejection")
    # point 9: four separated gate classes present
    for cls in ("integrity_rejection", "data_or_execution_rejection",
                "economic_performance_rejection", "insufficient_statistical_power_warning"):
        if not rg.get(cls):
            f.append("rejection_class_missing:%s" % cls)
    if cm.get("results_required_at_three_levels") and \
            s.get("required_results", {}).get("annualized_return_marked_non_conclusive") is not True:
        f.append("annualized_not_marked_non_conclusive")
    # data inventory fail-closed + gated
    inv = s.get("price_path_missing_data_inventory") or {}
    if inv.get("status") != "NOT_FROZEN_NOT_AUTHORIZED":
        f.append("missing_data_inventory_not_fail_closed")
    if inv.get("gate_required_before_use") != "C22_FORWARD_PRICE_DATA_READY_FOR_HUMAN_REVIEW":
        f.append("forward_data_gate_missing")
    if s.get("replay_advance_token") != REPLAY_ADVANCE_TOKEN:
        f.append("replay_advance_token_not_canonical")
    for flag in _CAPABILITY_FLAGS_FALSE:
        if s.get(flag) is not False:
            f.append("capability_flag_true:%s" % flag)
    if s.get("spec_sha256") and s["spec_sha256"] != _hashlib.sha256(
            canonical_spec_bytes(s)).hexdigest():
        f.append("spec_hash_mismatch")
    if s.get("verdict") == VERDICT_READY and s.get("blockers"):
        f.append("ready_with_blockers")
    return {"valid": not f, "failures": f}

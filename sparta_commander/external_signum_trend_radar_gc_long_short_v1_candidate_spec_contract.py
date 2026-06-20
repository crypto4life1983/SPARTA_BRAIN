"""Candidate #22 -- external_signum_trend_radar_gc_long_short_v1
-- CANDIDATE SPEC (PURE, RESEARCH ONLY, DETERMINISTIC TRANSCRIPTION).

A deterministic, research-only transcription of the user-provided Signum strategy prompt
"TR-GC-Crypto-LS-2" (Bot ID 25792) into a frozen candidate specification. Every numeric
value and rule below is copied VERBATIM from the user's source rules -- NOTHING is
invented. The three LIVE-ACTION steps (8 post-action re-fetch, 9 summary email, 10 bot
title edit) and all execution-adjacent behaviours (bot edits, set-trading-pair, fund
conversion, order send) are transcribed as their ORIGINAL live instruction but
represented ONLY as research-only / simulated / LOCKED-OUT behaviour -- this spec executes
none of them. Genuinely ambiguous rules are flagged
SPEC_AMBIGUITY_REQUIRES_HUMAN_REVIEW rather than guessed.

Chain-gated on the committed C22 family proposal (verdict
C22_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW), pinned to its pushed commit
b1b927957eb41669a9b5d1959aab93da0903cd77.

It builds NO detector, NO labels, NO replay; runs NO PnL / optimization / data fetch;
connects NOTHING (no Signum, no MCP, no Hyperliquid, no API keys / credentials); sends NO
email, edits NO bot, places NO order, sets NO trading pair, converts NO funds; touches NO
paper/live/broker/order/scheduler surface; and advances NOTHING. Every capability flag is
pinned False with a full scope_locks set. Advancing to the detector-spec dry-run gate
needs an explicit human decision.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_proposal_contract as _prop  # noqa: E501

S22_SCHEMA_VERSION = 1
S22_MODE = "RESEARCH_ONLY"
S22_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _prop.CANDIDATE_ID                 # "C22"
CANDIDATE_TOKEN = _prop.CANDIDATE_TOKEN
CANDIDATE_FAMILY = _prop.CANDIDATE_FAMILY
CANDIDATE_NAME = _prop.CANDIDATE_NAME

# --- the EXTERNAL source this spec transcribes (reference-only) --------------
SOURCE = {
    "provider": "Signum",
    "strategy_prompt_id": "TR-GC-Crypto-LS-2",
    "bot_id": "25792",
    "transcribed_verbatim_read_only": True,
    "no_values_invented": True,
    "original_strategy_intent_preserved": True,
}

# pinned pushed C22 proposal commit this spec is chain-gated on.
PROPOSAL_COMMIT = "b1b927957eb41669a9b5d1959aab93da0903cd77"
EXPECTED_PROPOSAL_VERDICT = "C22_PROPOSAL_FROZEN_FOR_HUMAN_REVIEW"

VERDICT_S22_FROZEN = "C22_SPEC_FROZEN_FOR_HUMAN_REVIEW"

GATE_SEQUENCE = (
    "family_proposal", "candidate_spec", "detector_spec_dry_run",
    "real_candle_labels_review", "fee_honest_replay_review",
    "rejection_or_promote_decision",
)
NEXT_HUMAN_GATE_AFTER_SPEC = (
    "HUMAN_DECISION_C22_ADVANCE_TO_DETECTOR_SPEC_DRY_RUN_OR_REJECT")

# --- human ambiguity resolutions (NOT vendor-original TR-GC-Crypto-LS-2 text) -
# The three genuine ambiguities below were resolved by an explicit human decision with
# deterministic, safety-first rules. They are clearly labelled as HUMAN resolutions; the
# original vendor rules above are preserved unchanged.
AMBIGUITY_RESOLUTION_ORIGIN = "HUMAN_AMBIGUITY_RESOLUTION_NOT_VENDOR_ORIGINAL"
AMBIGUITY_RESOLVED_STATUS = "RESOLVED_BY_HUMAN_AMBIGUITY_RESOLUTION"

# === STEP 1 -- holdings / NAV precondition (perpetual account required) ======
PRECONDITION = {
    "source_step": 1,
    "intent": ("fetch HOLDINGS, convert to USD for total NAV; if the trading account is "
               "not perpetual the bot cannot SHORT, so STOP the routine and notify"),
    "requires_perpetual_trading_account": True,
    "if_not_perpetual": "STOP_ROUTINE_CANNOT_SHORT_AND_NOTIFY",
    "nav_snapshot_taken_once_at_step1": True,
    "nav_not_recomputed_midrun": True,
    "research_only_no_live_fetch": True,
}

# === STEP 2 -- Crypto Trend Radar daily "gc" detector input schema ===========
DATA_INPUT_SCHEMA = {
    "source_step": 2,
    "detector": "gc",
    "timeframe": "daily",
    "include_indicators": True,
    "min_line_items": 50,
    "max_fetch_retries": 3,
    "refetch_if_fewer_than_min_line_items": True,
    "uses_latest_closed_candle": True,
    "candle_fields": ("ohlc.h", "ohlc.c"),
    "gc_block_fields": ("gc.trend", "gc.upper", "gc.filter"),
    "gc_trend_values": ("Green", "Red", "Grey"),
    "gc_upper_is_upper_band": True,
    "gc_filter_is_center_line": True,
    "asset_row_fields": ("breakoutDate", "cmcRefPriceUsd", "market_rank"),
    "all_assets_non_stablecoin_by_design": True,
    # the spec READS this from FROZEN data at a future, separately-gated stage; this
    # contract performs NO MCP fetch and connects to nothing.
    "research_only_no_mcp_fetch": True,
}

# === STEP 3 -- BTC regime ====================================================
BTC_REGIME = {
    "source_step": 3,
    "downtrend_when": "btc_latest_closed_close < btc.gc.filter",
    "otherwise_not_downtrend": True,
    # --- HUMAN ambiguity resolution (not vendor-original) -------------------
    "btc_absent_resolution": {
        "origin": AMBIGUITY_RESOLUTION_ORIGIN,
        "rule": ("if BTC is absent from the Trend Radar, or BTC lacks the latest CLOSED "
                 "candle or gc.filter, then BTC_DOWNTREND = False for this run -- this "
                 "DISABLES bear-short entries; HEDGE-short entries may still be "
                 "evaluated (they do not require BTC downtrend); all short entries remain "
                 "subject to 'when in doubt, skip'"),
        "btc_downtrend_defaults_false_when_absent_or_incomplete": True,
        "disables_bear_short_when_btc_downtrend_false": True,
        "hedge_short_still_evaluated_when_btc_absent": True,
        "all_shorts_remain_subject_to_when_in_doubt_skip": True,
    },
}

# === STEP 4 -- LONG EXITS ====================================================
LONG_EXIT = {
    "source_step": 4,
    "scope": "all LONG holdings, excluding fiat and stablecoins",
    "close_pct": 100,
    "triggers_any_of": (
        "latest_closed_close < gc.upper",          # close below the UPPER GC band
        "asset_no_longer_in_trend_radar_results",
    ),
}

# === STEP 5 -- SHORT EXITS ===================================================
SHORT_EXIT = {
    "source_step": 5,
    "scope": "all SHORT holdings",
    "close_pct": 100,
    "stop_trigger": "latest_closed_close > gc.filter",
    "take_profit_entry_price_formula":
        "(currentCollateralAsQuoteCoin + unrealizedPnlAsQuoteCoin) / sizeAsBaseCoin",
    "take_profit_multiple": 0.65,
    "take_profit_trigger": "latest_closed_close <= 0.65 * derived_short_entry_price",
    "also_exit_if": "asset_no_longer_in_trend_radar_results",
    "triggers_any_of": (
        "stop: latest_closed_close > gc.filter",
        "take_profit: latest_closed_close <= 0.65 * derived_short_entry_price",
        "asset_no_longer_in_trend_radar_results",
    ),
}

# === STEP 6 -- LONG ENTRIES ==================================================
LONG_ENTRY = {
    "source_step": 6,
    "universe": "Trend Radar assets sorted by market rank ASCENDING, first 50 rows",
    "sort_key": "market_rank",
    "sort_order": "ascending",
    "top_n_rows": 50,
    "entry_trigger": ("crossover UP through the upper GC band on the latest CLOSED "
                      "candle: latest_close > gc.upper AND previous_close <= gc.upper"),
    "never_enter_long_on_asset_long_exited_this_run": True,
    "skip_if_already_held_long_or_short": True,
    "one_position_per_coin": True,
    "held_dust_exception": True,   # "...unless it is dust" (see SPEC_AMBIGUITIES)
    "sizing_by_breakout_recency": {
        "breakout_recent_window_calendar_days": 25,
        "size_pct_nav_if_breakout_within_window": 8.0,
        "size_pct_nav_otherwise": 2.0,
        "breakout_not_required_to_enter_only_sets_size": True,
        "breakout_recency_reference": "run/as-of date (latest closed candle date)",
    },
    "leverage": "1x if Perpetual Futures Bot",
    "skip_if_indicator_data_for_crossover_missing": True,
    # --- HUMAN ambiguity resolutions (not vendor-original) -----------------
    "market_rank_resolution": {
        "origin": AMBIGUITY_RESOLUTION_ORIGIN,
        "rule": ("the source must provide a UNIQUE NUMERIC market-rank field per Trend "
                 "Radar row before top-50 selection; the spec does NOT invent the field "
                 "name -- the detector-spec/data-adapter gate must map the provider field "
                 "explicitly; if no unique numeric market-rank field is available, entry "
                 "evaluation is INVALID and entries must be skipped/rejected for the run"),
        "requires_unique_numeric_market_rank_field": True,
        "field_name_not_invented_mapped_at_adapter_gate": True,
        "skip_or_reject_entries_if_no_unique_numeric_market_rank": True,
    },
    "held_dust_resolution": {
        "origin": AMBIGUITY_RESOLUTION_ORIGIN,
        "rule": ("an already-held position counts as DUST only if its USD notional is "
                 "below the EXIT dust threshold (< $10); if held notional >= $10 it is an "
                 "ACTIVE position and no second position is opened in that coin; the "
                 "ENTRY dust threshold is NOT used for held-position dust"),
        "held_dust_threshold_usd": 10,
        "uses_exit_dust_threshold_for_held_position": True,
        "does_not_use_entry_threshold_for_held_position": True,
    },
}

# === STEP 7 -- SHORT ENTRIES =================================================
SHORT_ENTRY = {
    "source_step": 7,
    "universe": "Trend Radar assets sorted by market rank ASCENDING, first 50 rows",
    "sort_key": "market_rank",
    "sort_order": "ascending",
    "top_n_rows": 50,
    "scope": "any asset not already held",
    "hedge_short": {
        "condition": ("gc.trend == 'Red' AND cross DOWN through gc.filter on the latest "
                      "CLOSED candle: latest_close < gc.filter AND previous_close >= "
                      "gc.filter"),
        "size_pct_nav": 3.0,
    },
    "bear_short": {
        "evaluated_only_if_hedge_short_not_met": True,
        "condition": ("BTC is in a DOWNTREND AND gc.trend == 'Red' AND latest CLOSED "
                      "HIGH reached the filter (ohlc.h >= 0.98 * gc.filter) AND latest "
                      "CLOSED close < gc.filter"),
        "high_reaches_filter_multiple": 0.98,
        "size_pct_nav": 5.0,
        "requires_btc_downtrend_true": True,
        # per the BTC-absent HUMAN resolution: btc_downtrend defaults False when BTC is
        # absent/incomplete, which DISABLES bear shorts for the run.
        "disabled_when_btc_downtrend_false_per_human_resolution": True,
    },
    "never_enter_short_on_asset_short_exited_this_run": True,
    "leverage": "1x if Perpetual Futures Bot",
    "skip_if_indicator_data_for_cross_missing": True,
    "when_in_doubt_skip_short": True,
    # --- HUMAN ambiguity resolution (not vendor-original): same market-rank rule
    "market_rank_resolution": {
        "origin": AMBIGUITY_RESOLUTION_ORIGIN,
        "rule": ("the source must provide a UNIQUE NUMERIC market-rank field per Trend "
                 "Radar row before top-50 selection; mapped explicitly at the "
                 "detector-spec/data-adapter gate; if no unique numeric market-rank field "
                 "is available, entry evaluation is INVALID and entries are "
                 "skipped/rejected for the run"),
        "requires_unique_numeric_market_rank_field": True,
        "skip_or_reject_entries_if_no_unique_numeric_market_rank": True,
    },
}

# === STEP 8 -- post-action consistency check (LIVE -> research-only) =========
POST_ACTION_CHECK = {
    "source_step": 8,
    "original_live_instruction": ("re-fetch bot assets/positions and verify the trades "
                                  "resulted in the expected outcome"),
    "research_only_representation": "SIMULATED_POST_ACTION_CONSISTENCY_CHECK_ONLY",
    "never_executes_live_refetch": True,
}

# === STEP 9 -- summary email (LIVE -> research-only) =========================
SUMMARY_REPORT = {
    "source_step": 9,
    "original_live_instruction": "send a summary email once done",
    "research_only_representation": "SIMULATED_REPORTING_OUTPUT_ONLY",
    "never_sends_email": True,
}

# === STEP 10 -- bot title edit (LIVE -> PROHIBITED / locked out) =============
BOT_TITLE_EDIT = {
    "source_step": 10,
    "original_live_instruction": ("edit the bot so the prompt id is at the end of the "
                                  "title, e.g. '... (TR-GC-Crypto-LS-2)'"),
    "research_only_representation": "PROHIBITED_LIVE_BEHAVIOUR_LOCKED_OUT",
    "never_edits_bot": True,
    "recorded_as_original_live_instruction_only": True,
}

# === Trading-pair selection + ticker-collision guard ========================
TRADING_PAIR_RULES = {
    "intent": ("fetch available pairs the bot can access; use the pair best representing "
               "the target asset and holdings"),
    "ticker_collision_guard": {
        "method": "compare get-pair-price priceUsd to the asset USD reference",
        "usd_reference": ("indicators.cmcRefPriceUsd, or the newest "
                          "indicators.data[].ohlc.c if cmcRefPriceUsd is absent"),
        "skip_and_report_if_relative_diff_exceeds": 0.5,
        "skip_and_report_if_price_or_reference_missing": True,
    },
    "set_pair_before_signal_original_live_instruction": True,
    "research_only_representation": "SIMULATED_PAIR_SELECTION_NO_BOT_EDIT_NO_EXECUTION",
    "never_sets_trading_pair_live": True,
}

# === Conversion rules =======================================================
CONVERSION_RULES = {
    "convert_only_required_amount_for_the_quote_coin_not_held": True,
    "prefer_stablecoins_then_fiat": True,
    "skip_entry_and_report_if_no_direct_conversion_pair": True,
    "research_only_representation": "MODELED_AS_COST_BEARING_CONSTRAINTS_ONLY",
    "never_executes_conversion": True,
}

# === Signal translation =====================================================
SIGNAL_TRANSLATION = {
    "enter_long": "BUY, positionSize > 0",
    "exit_long": "SELL 100%, positionSize = 0",
    "enter_short": "SELL, positionSize < 0",
    "exit_short": "BUY back 100%, positionSize = 0",
    "always_state_target_position_size": True,
    "edit_bot_and_set_pair_before_signal_original_live_instruction": True,
    "research_only_representation": "SIMULATED_SIGNALS_ONLY_NO_SEND_NO_BOT_EDIT",
    "never_sends_signal": True,
}

# === Order-size calculation =================================================
ORDER_SIZE = {
    "percentage_ordersize_is_pct_of_base_or_quote_coin_not_nav": True,
    "nav_pct_to_ordersize": {
        "target_amount_quote_coin": "X% of NAV, using the step-1 NAV snapshot",
        "ordersize_pct_formula": ("target_amount / quote_coin_balance_available_now_"
                                  "after_prior_orders_in_this_run * 100"),
        "do_not_recompute_nav_midrun": True,
        "never_reuse_a_percentage_calculated_earlier_in_the_run": True,
        "cap_ordersize_pct_at_100": True,
    },
    "entry_min_order_value_pct_nav": 1.0,     # positionSize != 0
    "entry_min_order_value_usd": 10,
    "exit_min_order_value_usd": 10,           # positionSize == 0
    "skip_below_thresholds_as_dust_and_report": True,
}

# === Benchmark requirements (directional long+short) ========================
BENCHMARKS = {
    "is_directional_long_short": True,
    "judged_vs_buy_and_hold": True,
    "judged_vs_random_null": True,
    "net_of_fees_funding_slippage": True,
    "forward_oos_required": True,
    "do_not_promote_on_net_positive_alone": True,
}

# === genuine ambiguities -- flagged, then RESOLVED BY HUMAN (not vendor text) =
# Each was originally flagged (not guessed); each now carries an explicit, deterministic,
# safety-first HUMAN resolution. The original vendor rules are preserved unchanged.
SPEC_AMBIGUITIES = (
    {"id": "btc_absent_from_trend_radar",
     "rule_ref": "step 3 (BTC regime) + step 7b (bear short)",
     "description": ("the BTC downtrend regime is defined by BTC's own latest closed "
                     "close vs its gc.filter; the source does not define the regime when "
                     "BTC is absent from the Trend Radar results, which the bear-short "
                     "condition depends on"),
     "status": AMBIGUITY_RESOLVED_STATUS,
     "resolution_origin": AMBIGUITY_RESOLUTION_ORIGIN,
     "resolution": ("if BTC is absent from Trend Radar, or BTC lacks the latest closed "
                    "candle or gc.filter, then BTC_DOWNTREND = False for this run; this "
                    "disables BEAR short entries; HEDGE short entries may still be "
                    "evaluated (they do not require BTC downtrend); all short entries "
                    "remain subject to 'when in doubt, skip'")},
    {"id": "market_rank_field_source",
     "rule_ref": "steps 6 & 7 (sort by market rank ascending, first 50)",
     "description": ("'market rank' governs the top-50 selection, but the step-2 data "
                     "schema description does not name the exact field that carries the "
                     "market rank; the field source must be confirmed before detection"),
     "status": AMBIGUITY_RESOLVED_STATUS,
     "resolution_origin": AMBIGUITY_RESOLUTION_ORIGIN,
     "resolution": ("the source must provide a unique numeric market-rank field for each "
                    "Trend Radar row before top-50 selection; the spec does not invent "
                    "the field name -- the detector-spec/data-adapter gate must map the "
                    "provider field explicitly; if no unique numeric market-rank field is "
                    "available, entry evaluation is invalid and entries are "
                    "skipped/rejected for that run")},
    {"id": "held_dust_exception_threshold",
     "rule_ref": "step 6 ('skip ... already held ... unless it is dust')",
     "description": ("whether an existing DUST-sized holding permits a new entry, and "
                     "which dust threshold (the entry 1%-of-NAV / $10 rule) applies to "
                     "the HELD position rather than the new order, is not made explicit"),
     "status": AMBIGUITY_RESOLVED_STATUS,
     "resolution_origin": AMBIGUITY_RESOLUTION_ORIGIN,
     "resolution": ("an already-held position counts as dust only if its USD notional is "
                    "below the EXIT dust threshold (< $10); if held notional >= $10 it is "
                    "an active position and no second position is opened in that coin; "
                    "the ENTRY threshold is not used for held-position dust")},
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "builds_detector", "runs_detector", "runs_labels",
    "runs_replay", "runs_backtest", "computes_pnl", "optimizes_parameters",
    "reparameterizes", "tunes_parameters", "fetches_data", "reads_real_data",
    "mutates_data", "stages_data", "auto_commits", "auto_pushes", "modifies_scheduler",
    "installs_scheduler", "sends_notifications", "sends_email", "calls_api",
    "uses_network", "uses_credentials", "uses_api_keys", "connects_signum", "uses_mcp",
    "accesses_hyperliquid", "connects_broker", "connects_exchange", "sends_trades",
    "sends_signal", "edits_bots", "edits_bot_title", "sets_trading_pair",
    "converts_funds", "creates_claude_routines", "uses_real_money", "places_orders",
    "contains_order_logic", "adds_new_instrument_class", "paper_trading",
    "live_trading", "deploys_capital", "promotes_gate", "unlocks_downstream_gate",
    "skips_any_gate", "advances_without_human_approval", "invents_rule_values",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def get_candidate_22_spec_label() -> str:
    return (
        "Candidate #22 external_signum_trend_radar_gc_long_short_v1 candidate spec "
        "(READ-ONLY, RESEARCH ONLY). Deterministic verbatim transcription of the Signum "
        "TR-GC-Crypto-LS-2 rules (Bot 25792): perpetual-account precondition; daily 'gc' "
        "Trend Radar input; BTC regime via gc.filter; LONG exits below the upper GC band "
        "/ out-of-radar; SHORT exits on stop (close>filter), take-profit (close<=0.65x "
        "entry) or out-of-radar; LONG entries on close crossing above the upper band "
        "(top-50 by market rank), sized 8%/2% of NAV by 25-day breakout recency; SHORT "
        "entries hedge (Red + cross down filter, 3%) or bear (BTC downtrend + Red + "
        "high>=0.98x filter + close<filter, 5%); NAV-snapshot order sizing with 1%-NAV/"
        "$10 dust floors; ticker-collision 0.5 guard; conversion constraints. The live "
        "steps (re-fetch check, email, bot-title edit, set-pair, convert, send) are "
        "transcribed but LOCKED to research-only/simulated -- NOTHING executes, connects, "
        "or trades. 3 genuine ambiguities flagged then RESOLVED BY EXPLICIT HUMAN "
        "decision (BTC-absent -> downtrend False / bear shorts off; market-rank must be a "
        "unique numeric field mapped at the adapter gate or entries skipped; held-dust = "
        "<$10 exit threshold). NO values invented. PROPOSAL-chain-gated. NOT a "
        "profitability claim.")


def get_candidate_22_spec_next_action() -> str:
    return NEXT_HUMAN_GATE_AFTER_SPEC


def _deepish(d: dict) -> dict:
    out: dict = {}
    for k, v in d.items():
        out[k] = (dict(v) if isinstance(v, dict)
                  else (list(v) if isinstance(v, tuple) else v))
    return out


def build_c22_spec() -> dict[str, Any]:
    """Assemble the frozen Candidate #22 candidate-spec record. Pure; no I/O;
    spec only. Chain-gated on the committed C22 family proposal (verdict frozen)."""
    prop = _prop.build_c22_proposal()
    prop_valid = _prop.validate_c22_proposal(prop)["valid"]
    prop_verdict = prop.get("verdict")

    blockers: list = []
    if not prop_valid:
        blockers.append("c22_proposal_invalid")
    if prop_verdict != EXPECTED_PROPOSAL_VERDICT:
        blockers.append("c22_proposal_not_frozen")
    if prop.get("candidate_id") != "C22":
        blockers.append("proposal_not_c22")

    record: dict[str, Any] = {
        "schema_version": S22_SCHEMA_VERSION, "mode": S22_MODE, "lane": S22_LANE,
        "label": get_candidate_22_spec_label(),
        "candidate_id": CANDIDATE_ID, "candidate_token": CANDIDATE_TOKEN,
        "candidate_family": CANDIDATE_FAMILY, "candidate_name": CANDIDATE_NAME,
        "is_candidate_spec_only": True,
        "blockers": blockers,
        "verdict": (VERDICT_S22_FROZEN if not blockers else "C22_SPEC_BLOCKED"),
        # chain provenance (gated on the frozen, pushed proposal)
        "proposal_valid": prop_valid,
        "proposal_verdict": prop_verdict,
        "chain_gated_on_c22_proposal": not blockers,
        "proposal_commit": PROPOSAL_COMMIT,
        # the external source + transcription posture
        "source": dict(SOURCE),
        "transcribed_verbatim_read_only": True,
        "no_values_invented": True,
        "original_strategy_intent_preserved": True,
        # the frozen rule transcription (steps 1-10 + cross-cutting rules)
        "precondition": dict(PRECONDITION),                       # 1
        "data_input_schema": _deepish(DATA_INPUT_SCHEMA),         # 2
        "btc_regime": dict(BTC_REGIME),                           # 3
        "long_exit": _deepish(LONG_EXIT),                         # 4
        "short_exit": _deepish(SHORT_EXIT),                       # 5
        "long_entry": _deepish(LONG_ENTRY),                       # 6
        "short_entry": _deepish(SHORT_ENTRY),                     # 7
        "post_action_check": dict(POST_ACTION_CHECK),             # 8 (locked)
        "summary_report": dict(SUMMARY_REPORT),                   # 9 (locked)
        "bot_title_edit": dict(BOT_TITLE_EDIT),                   # 10 (prohibited)
        "trading_pair_rules": _deepish(TRADING_PAIR_RULES),
        "conversion_rules": dict(CONVERSION_RULES),
        "signal_translation": dict(SIGNAL_TRANSLATION),
        "order_size": _deepish(ORDER_SIZE),
        "benchmarks": dict(BENCHMARKS),
        # genuine ambiguities -- flagged (not guessed), then RESOLVED BY HUMAN
        "spec_ambiguities": [dict(a) for a in SPEC_AMBIGUITIES],
        "ambiguities_flagged_not_guessed": True,
        "all_ambiguities_resolved_by_human": True,
        "spec_has_unresolved_ambiguities": False,
        "resolutions_are_human_not_vendor_original": True,
        # identity
        "is_directional": True, "is_long_short_symmetric": True,
        "is_market_neutral": False,
        "gate_sequence": list(GATE_SEQUENCE),
        "human_review_required": True,
        "current_loop_stage": "candidate_spec",
        "next_required_action": NEXT_HUMAN_GATE_AFTER_SPEC,
        "advances_nothing": True,
        # downstream gates locked
        "detector_gate_locked": True, "labels_gate_locked": True,
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_build": True, "no_write": True, "no_execute": True,
        "no_detector": True, "no_labels": True, "no_replay": True,
        "no_backtest": True, "no_pnl": True, "no_optimization": True,
        "no_reparameterization": True, "no_tuning": True, "no_data_fetch": True,
        "no_real_data_access": True, "no_invent_values": True, "no_stage": True,
        "no_commit": True, "no_push": True, "no_auto_commit": True,
        "no_auto_push": True, "no_scheduler_change": True, "no_scheduler_install": True,
        "no_signum_connection": True, "no_mcp": True, "no_hyperliquid": True,
        "no_api_keys": True, "no_credentials": True, "no_send_email": True,
        "no_bot_edits": True, "no_bot_title_edit": True, "no_set_trading_pair": True,
        "no_convert_funds": True, "no_claude_routines": True, "no_send_trades": True,
        "no_send_signal": True, "no_broker": True, "no_order_logic": True,
        "no_paper_trading": True, "no_live_trading": True, "no_gate_skip": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_c22_spec(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the spec is research-only, spec-only,
    chain-gated on the frozen C22 proposal (verdict + pinned commit), a FAITHFUL verbatim
    transcription of the TR-GC-Crypto-LS-2 rules with every pinned numeric value matching
    the source and NO values invented, with the live steps (8/9/10 + bot edit / set-pair /
    convert / email / order send) represented ONLY as locked research-only/simulated
    behaviour, the directional buy-and-hold + random/null + forward-OOS benchmark set, the
    three genuine ambiguities flagged SPEC_AMBIGUITY_REQUIRES_HUMAN_REVIEW, downstream
    gates locked, advancing nothing, with every capability flag False."""
    failures: list = []
    if record.get("mode") != S22_MODE:
        failures.append("mode_not_research_only")
    if record.get("is_candidate_spec_only") is not True:
        failures.append("not_candidate_spec_only")
    if record.get("blockers"):
        failures.append("has_blockers")
    if record.get("verdict") != VERDICT_S22_FROZEN:
        failures.append("verdict_not_frozen")

    # chain gate on the frozen, pushed proposal
    if record.get("proposal_valid") is not True:
        failures.append("proposal_not_valid")
    if record.get("proposal_verdict") != EXPECTED_PROPOSAL_VERDICT:
        failures.append("proposal_not_frozen")
    if record.get("chain_gated_on_c22_proposal") is not True:
        failures.append("not_chain_gated_on_proposal")
    if not (isinstance(record.get("proposal_commit"), str)
            and len(record["proposal_commit"]) == 40):
        failures.append("proposal_commit_bad")
    if record.get("proposal_commit") != PROPOSAL_COMMIT:
        failures.append("proposal_commit_not_pinned")

    # identity
    if record.get("candidate_id") != "C22":
        failures.append("candidate_id_not_c22")
    if record.get("candidate_token") != CANDIDATE_TOKEN:
        failures.append("candidate_token_mismatch")
    if record.get("transcribed_verbatim_read_only") is not True:
        failures.append("not_verbatim_transcription")
    if record.get("no_values_invented") is not True:
        failures.append("values_may_be_invented")
    if record.get("original_strategy_intent_preserved") is not True:
        failures.append("intent_not_preserved")

    # --- pinned numeric values MUST match the source verbatim ----------------
    pre = record.get("precondition") or {}
    if pre.get("requires_perpetual_trading_account") is not True:
        failures.append("precondition_perpetual_missing")
    if pre.get("nav_not_recomputed_midrun") is not True:
        failures.append("nav_recompute_rule_missing")

    di = record.get("data_input_schema") or {}
    if di.get("detector") != "gc":
        failures.append("detector_not_gc")
    if di.get("min_line_items") != 50:
        failures.append("min_line_items_not_50")
    if di.get("max_fetch_retries") != 3:
        failures.append("retries_not_3")
    if di.get("research_only_no_mcp_fetch") is not True:
        failures.append("mcp_fetch_not_locked")

    if (record.get("btc_regime") or {}).get("downtrend_when") != (
            "btc_latest_closed_close < btc.gc.filter"):
        failures.append("btc_regime_rule_tampered")

    le = record.get("long_exit") or {}
    if le.get("close_pct") != 100:
        failures.append("long_exit_not_100pct")
    if "latest_closed_close < gc.upper" not in (le.get("triggers_any_of") or []):
        failures.append("long_exit_band_rule_missing")

    se = record.get("short_exit") or {}
    if se.get("stop_trigger") != "latest_closed_close > gc.filter":
        failures.append("short_stop_rule_tampered")
    if se.get("take_profit_multiple") != 0.65:
        failures.append("short_tp_multiple_not_0_65")
    if se.get("take_profit_entry_price_formula") != (
            "(currentCollateralAsQuoteCoin + unrealizedPnlAsQuoteCoin) / sizeAsBaseCoin"):
        failures.append("short_tp_entry_formula_tampered")

    lon = record.get("long_entry") or {}
    if lon.get("top_n_rows") != 50:
        failures.append("long_entry_top_n_not_50")
    if lon.get("sort_key") != "market_rank" or lon.get("sort_order") != "ascending":
        failures.append("long_entry_sort_tampered")
    sz = lon.get("sizing_by_breakout_recency") or {}
    if sz.get("breakout_recent_window_calendar_days") != 25:
        failures.append("breakout_window_not_25")
    if sz.get("size_pct_nav_if_breakout_within_window") != 8.0:
        failures.append("recent_size_not_8pct")
    if sz.get("size_pct_nav_otherwise") != 2.0:
        failures.append("else_size_not_2pct")
    if sz.get("breakout_not_required_to_enter_only_sets_size") is not True:
        failures.append("breakout_not_required_rule_missing")
    if lon.get("never_enter_long_on_asset_long_exited_this_run") is not True:
        failures.append("long_reentry_guard_missing")

    sh = record.get("short_entry") or {}
    if (sh.get("hedge_short") or {}).get("size_pct_nav") != 3.0:
        failures.append("hedge_short_not_3pct")
    bear = sh.get("bear_short") or {}
    if bear.get("size_pct_nav") != 5.0:
        failures.append("bear_short_not_5pct")
    if bear.get("high_reaches_filter_multiple") != 0.98:
        failures.append("bear_high_multiple_not_0_98")
    if bear.get("evaluated_only_if_hedge_short_not_met") is not True:
        failures.append("bear_short_precedence_missing")
    if sh.get("when_in_doubt_skip_short") is not True:
        failures.append("skip_short_when_in_doubt_missing")

    os_ = record.get("order_size") or {}
    if os_.get("percentage_ordersize_is_pct_of_base_or_quote_coin_not_nav") is not True:
        failures.append("ordersize_pct_basis_rule_missing")
    if os_.get("entry_min_order_value_pct_nav") != 1.0:
        failures.append("entry_dust_pct_not_1")
    if os_.get("entry_min_order_value_usd") != 10:
        failures.append("entry_dust_usd_not_10")
    if os_.get("exit_min_order_value_usd") != 10:
        failures.append("exit_dust_usd_not_10")
    nav = os_.get("nav_pct_to_ordersize") or {}
    if nav.get("never_reuse_a_percentage_calculated_earlier_in_the_run") is not True:
        failures.append("ordersize_reuse_guard_missing")
    if nav.get("cap_ordersize_pct_at_100") is not True:
        failures.append("ordersize_cap_missing")

    tp = record.get("trading_pair_rules") or {}
    if (tp.get("ticker_collision_guard") or {}).get(
            "skip_and_report_if_relative_diff_exceeds") != 0.5:
        failures.append("collision_threshold_not_0_5")
    if tp.get("never_sets_trading_pair_live") is not True:
        failures.append("set_pair_not_locked")

    cv = record.get("conversion_rules") or {}
    if cv.get("never_executes_conversion") is not True:
        failures.append("conversion_not_locked")
    if cv.get("prefer_stablecoins_then_fiat") is not True:
        failures.append("conversion_preference_missing")

    st = record.get("signal_translation") or {}
    if st.get("enter_short") != "SELL, positionSize < 0":
        failures.append("signal_enter_short_tampered")
    if st.get("never_sends_signal") is not True:
        failures.append("signal_send_not_locked")

    # --- live steps 8/9/10 represented ONLY as locked research-only behaviour -
    if (record.get("post_action_check") or {}).get(
            "never_executes_live_refetch") is not True:
        failures.append("post_action_not_locked")
    if (record.get("summary_report") or {}).get("never_sends_email") is not True:
        failures.append("email_not_locked")
    bte = record.get("bot_title_edit") or {}
    if bte.get("research_only_representation") != (
            "PROHIBITED_LIVE_BEHAVIOUR_LOCKED_OUT"):
        failures.append("bot_title_edit_not_prohibited")
    if bte.get("never_edits_bot") is not True:
        failures.append("bot_edit_not_locked")

    # --- benchmarks (directional: buy-and-hold + random/null + forward-OOS) ---
    bm = record.get("benchmarks") or {}
    for k in ("judged_vs_buy_and_hold", "judged_vs_random_null",
              "net_of_fees_funding_slippage", "forward_oos_required",
              "do_not_promote_on_net_positive_alone"):
        if bm.get(k) is not True:
            failures.append("benchmark_off_%s" % k)

    # --- the three ambiguities: flagged (not guessed) then RESOLVED BY HUMAN --
    ambs = record.get("spec_ambiguities") or []
    if len(ambs) != 3:
        failures.append("ambiguities_not_three")
    ids = {a.get("id") for a in ambs}
    for must in ("btc_absent_from_trend_radar", "market_rank_field_source",
                 "held_dust_exception_threshold"):
        if must not in ids:
            failures.append("ambiguity_missing_%s" % must)
    for a in ambs:
        if a.get("status") != AMBIGUITY_RESOLVED_STATUS:
            failures.append("ambiguity_not_resolved_%s" % a.get("id"))
        if a.get("resolution_origin") != AMBIGUITY_RESOLUTION_ORIGIN:
            failures.append("resolution_not_human_marked_%s" % a.get("id"))
        if not a.get("resolution"):
            failures.append("resolution_missing_%s" % a.get("id"))
    if record.get("ambiguities_flagged_not_guessed") is not True:
        failures.append("ambiguities_not_flagged")
    if record.get("all_ambiguities_resolved_by_human") is not True:
        failures.append("ambiguities_not_all_resolved")
    if record.get("spec_has_unresolved_ambiguities") is not False:
        failures.append("spec_still_has_unresolved_ambiguities")
    if record.get("resolutions_are_human_not_vendor_original") is not True:
        failures.append("resolutions_not_marked_human")

    # the resolutions are encoded into the relevant rule blocks (deterministic)
    btc_res = (record.get("btc_regime") or {}).get("btc_absent_resolution") or {}
    if btc_res.get("origin") != AMBIGUITY_RESOLUTION_ORIGIN:
        failures.append("btc_absent_resolution_not_human")
    if btc_res.get("btc_downtrend_defaults_false_when_absent_or_incomplete") is not True:
        failures.append("btc_absent_downtrend_not_false")
    if btc_res.get("disables_bear_short_when_btc_downtrend_false") is not True:
        failures.append("btc_absent_does_not_disable_bear")
    if btc_res.get("hedge_short_still_evaluated_when_btc_absent") is not True:
        failures.append("btc_absent_hedge_rule_missing")
    bear = (record.get("short_entry") or {}).get("bear_short") or {}
    if bear.get("requires_btc_downtrend_true") is not True:
        failures.append("bear_short_does_not_require_btc_downtrend")
    mr_res = (record.get("long_entry") or {}).get("market_rank_resolution") or {}
    if mr_res.get("origin") != AMBIGUITY_RESOLUTION_ORIGIN:
        failures.append("market_rank_resolution_not_human")
    if mr_res.get("requires_unique_numeric_market_rank_field") is not True:
        failures.append("market_rank_unique_numeric_rule_missing")
    if mr_res.get("skip_or_reject_entries_if_no_unique_numeric_market_rank") is not True:
        failures.append("market_rank_skip_rule_missing")
    hd_res = (record.get("long_entry") or {}).get("held_dust_resolution") or {}
    if hd_res.get("origin") != AMBIGUITY_RESOLUTION_ORIGIN:
        failures.append("held_dust_resolution_not_human")
    if hd_res.get("held_dust_threshold_usd") != 10:
        failures.append("held_dust_threshold_not_10")
    if hd_res.get("uses_exit_dust_threshold_for_held_position") is not True:
        failures.append("held_dust_not_exit_threshold")
    if hd_res.get("does_not_use_entry_threshold_for_held_position") is not True:
        failures.append("held_dust_uses_entry_threshold")

    # --- gate sequence + downstream locks + advances nothing -----------------
    if list(record.get("gate_sequence") or []) != list(GATE_SEQUENCE):
        failures.append("gate_sequence_tampered")
    if record.get("next_required_action") != NEXT_HUMAN_GATE_AFTER_SPEC:
        failures.append("next_action_not_detector_gate")
    if record.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")
    for gate in ("detector_gate_locked", "labels_gate_locked", "replay_gate_locked",
                 "paper_trading_gate_locked", "live_gate_locked"):
        if record.get(gate) is not True:
            failures.append("downstream_gate_unlocked_%s" % gate)

    locks = record.get("scope_locks") or {}
    for key in ("no_build", "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_data_fetch", "no_invent_values", "no_commit", "no_push",
                "no_signum_connection", "no_mcp", "no_hyperliquid", "no_api_keys",
                "no_credentials", "no_send_email", "no_bot_edits", "no_set_trading_pair",
                "no_convert_funds", "no_claude_routines", "no_send_trades",
                "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_gate_skip"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

"""Candidate #22 -- external_signum_trend_radar_gc_long_short_v1
-- REAL-CANDLE LABELS REVIEW (PURE, READ-ONLY, RESEARCH ONLY).

Reviews the ALREADY-PRODUCED, committed C22 real-candle entry-signal labels and recommends
the next gate. It verifies evidence integrity (the dataset SHA + the labels-artifact SHA
both match their pinned values, the labels record validates, the human marketRank
tie-breaker was applied WITHOUT mutating source data), assesses the SAMPLE SIZE honestly,
and produces ONE recommendation from a closed set:

  * ADVANCE_TO_REPLAY_REVIEW           -- only if the sample is sufficient AND the contract
                                          clearly justifies it;
  * HOLD_FOR_MORE_FROZEN_DATA_WINDOWS  -- evidence is sound but too thin to replay;
  * REJECT_AT_LABELS_REVIEW            -- evidence integrity is broken.

Honest sample-size stance (single daily Signum export):
The committed labels cover exactly ONE frozen daily export -> ONE decision date, with only
2 actionable entry signals out of 50 rows (LONG_ENTRY=1, BEAR_SHORT=1; HEDGE_SHORT=0;
NONE=48). A daily directional long/short detector cannot be replayed from a single snapshot:
there is no multi-day path of entries -> exits -> PnL, no out-of-sample window, and the
setup density is near zero. SPARTA precedent for real-candle label evidence is a MULTI-WEEK
frozen window (e.g. the breakout/pullback detector labels span ~2026-05-12..2026-06-10,
~30 days). One day is far below that bar. This contract does NOT justify single-day replay;
per the human safety rule it recommends HOLD_FOR_MORE_FROZEN_DATA_WINDOWS rather than
pretend the sample is enough.

It runs NO replay, fetches NO data, mutates NO dataset, edits NO label, optimizes NOTHING,
changes NO C22 rule, and advances NOTHING. Every dangerous capability is pinned False.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_dataset_validation_contract as _dv  # noqa: E501
import sparta_commander.external_signum_trend_radar_gc_long_short_v1_real_candle_labels_contract as _lb  # noqa: E501

LR22_SCHEMA_VERSION = 1
LR22_MODE = "RESEARCH_ONLY"
LR22_LANE = "crypto_d1_auto_research"

CANDIDATE_ID = _lb.CANDIDATE_ID
CANDIDATE_TOKEN = _lb.CANDIDATE_TOKEN
CANDIDATE_FAMILY = _lb.CANDIDATE_FAMILY
CANDIDATE_NAME = _lb.CANDIDATE_NAME

DATASET_SHA256 = _dv.DATASET_SHA256
LABELS_ARTIFACT_SHA256 = _lb.LABELS_ARTIFACT_SHA256

# sample-size policy for advancing a DAILY directional long/short detector to replay.
# A replay needs a multi-day path of decisions (entries -> exits -> PnL) over an
# out-of-sample-capable window -- a single daily export cannot provide one.
MIN_FROZEN_DATA_WINDOWS_FOR_REPLAY = 20      # >= ~1 month of daily exports
MIN_DISTINCT_DECISION_DATES_FOR_REPLAY = 20  # >= ~1 month of decision days
MIN_ACTIONABLE_LABELS_FOR_REPLAY = 30        # enough entry decisions to assess edge

# SPARTA precedent: prior real-candle label evidence spans a multi-week frozen window.
PRECEDENT_NOTE = (
    "SPARTA precedent for real-candle label evidence is a multi-week frozen window (e.g. "
    "the breakout/pullback detector labels span ~2026-05-12..2026-06-10, ~30 days). The "
    "C22 labels cover a single daily export (one decision date), far below that precedent.")

REC_ADVANCE = "ADVANCE_TO_REPLAY_REVIEW"
REC_HOLD = "HOLD_FOR_MORE_FROZEN_DATA_WINDOWS"
REC_REJECT = "REJECT_AT_LABELS_REVIEW"

NEXT_ACTION_HOLD = (
    "HUMAN_STAGE_MORE_FROZEN_DAILY_TREND_RADAR_GC_WINDOWS_THEN_REREVIEW_C22_LABELS")
NEXT_ACTION_ADVANCE = "HUMAN_DECISION_C22_ADVANCE_TO_REPLAY_OR_REJECT"
NEXT_ACTION_REJECT = "HUMAN_DECISION_C22_REJECT_RECORDED_AT_LABELS_REVIEW"

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "performs_file_io", "performs_network_io",
    "runs_replay", "builds_replay", "runs_backtest", "computes_pnl",
    "optimizes_parameters", "tunes_parameters", "reparameterizes", "fetches_data",
    "stages_data", "mutates_dataset", "edits_labels", "repairs_market_rank",
    "invents_ranks", "auto_commits", "auto_pushes", "modifies_scheduler",
    "installs_scheduler", "sends_notifications", "sends_email", "calls_api",
    "uses_network", "uses_credentials", "uses_api_keys", "connects_signum", "uses_mcp",
    "accesses_hyperliquid", "connects_broker", "connects_exchange", "sends_trades",
    "edits_bots", "sets_trading_pair", "creates_claude_routines", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "promotes_gate", "unlocks_replay_gate", "unlocks_downstream_gate",
    "advances_without_human_approval", "modifies_c22_rules", "starts_c23", "reopens_c21",
    "crosses_into_forbidden_gate",
)


def build_labels_review(labels_record: dict, observed_dataset_sha: str,
                        observed_labels_artifact_sha: str) -> dict[str, Any]:
    """Assemble the C22 labels review. Pure; no I/O. Verifies evidence integrity, assesses
    sample size, and recommends the next gate. The caller (runner/test) reads the dataset +
    labels artifact READ-ONLY and passes their observed SHA256s in."""
    labels = list(labels_record.get("labels") or [])
    counts = labels_record.get("label_counts") or {}
    n_total = labels_record.get("labels_produced") or len(labels)
    n_long = counts.get("LONG_ENTRY", 0)
    n_hedge = counts.get("HEDGE_SHORT", 0)
    n_bear = counts.get("BEAR_SHORT", 0)
    n_none = counts.get("NONE", 0)
    n_skip = counts.get("SKIP", 0)
    n_actionable = n_long + n_hedge + n_bear
    distinct_decision_dates = sorted({lab.get("latest_date") for lab in labels})
    n_decision_dates = len(distinct_decision_dates)
    # one staged daily Signum export -> one frozen data window.
    n_frozen_data_windows = 1

    setup_density = (n_actionable / n_total) if n_total else 0.0

    # --- evidence integrity --------------------------------------------------
    dataset_sha_ok = str(observed_dataset_sha).lower() == DATASET_SHA256
    labels_sha_ok = str(observed_labels_artifact_sha).lower() == LABELS_ARTIFACT_SHA256
    labels_valid = _lb.validate_labels(labels_record)["valid"]
    labels_produced_ok = (
        labels_record.get("verdict") == _lb.VERDICT_LABELS_PRODUCED)
    tiebreaker_applied = (
        list(labels_record.get("market_rank_tiebreaker") or [])
        == list(_dv.MARKET_RANK_TIEBREAKER))
    no_mutation = (labels_record.get("dataset_mutated") is False
                   and labels_record.get("repaired_market_rank") is False
                   and labels_record.get("invented_ranks") is False
                   and labels_record.get("raw_market_rank_preserved") is True)
    integrity_ok = (dataset_sha_ok and labels_sha_ok and labels_valid
                    and labels_produced_ok and tiebreaker_applied and no_mutation)

    # --- sample sufficiency --------------------------------------------------
    sample_sufficient_for_replay = (
        n_frozen_data_windows >= MIN_FROZEN_DATA_WINDOWS_FOR_REPLAY
        and n_decision_dates >= MIN_DISTINCT_DECISION_DATES_FOR_REPLAY
        and n_actionable >= MIN_ACTIONABLE_LABELS_FOR_REPLAY)
    # this contract does NOT justify replaying a single daily snapshot.
    single_day_replay_is_justified = False

    sample_size_reasons = []
    if n_frozen_data_windows < MIN_FROZEN_DATA_WINDOWS_FOR_REPLAY:
        sample_size_reasons.append(
            "only_%d_frozen_data_window_need_%d"
            % (n_frozen_data_windows, MIN_FROZEN_DATA_WINDOWS_FOR_REPLAY))
    if n_decision_dates < MIN_DISTINCT_DECISION_DATES_FOR_REPLAY:
        sample_size_reasons.append(
            "only_%d_decision_date_need_%d"
            % (n_decision_dates, MIN_DISTINCT_DECISION_DATES_FOR_REPLAY))
    if n_actionable < MIN_ACTIONABLE_LABELS_FOR_REPLAY:
        sample_size_reasons.append(
            "only_%d_actionable_labels_need_%d"
            % (n_actionable, MIN_ACTIONABLE_LABELS_FOR_REPLAY))

    # --- recommendation ------------------------------------------------------
    if not integrity_ok:
        recommendation = REC_REJECT
        next_action = NEXT_ACTION_REJECT
    elif sample_sufficient_for_replay and single_day_replay_is_justified:
        recommendation = REC_ADVANCE
        next_action = NEXT_ACTION_ADVANCE
    else:
        recommendation = REC_HOLD
        next_action = NEXT_ACTION_HOLD

    record: dict[str, Any] = {
        "schema_version": LR22_SCHEMA_VERSION, "mode": LR22_MODE, "lane": LR22_LANE,
        "candidate_id": CANDIDATE_ID, "candidate_token": CANDIDATE_TOKEN,
        "candidate_family": CANDIDATE_FAMILY, "candidate_name": CANDIDATE_NAME,
        "is_labels_review_only": True,
        "label": (
            "Candidate #22 real-candle labels review (READ-ONLY, RESEARCH ONLY). Verifies "
            "the committed dataset + labels-artifact SHAs, the tie-breaker-without-mutation "
            "provenance, and the sample size; recommends the next gate. Single daily export "
            "/ 2 actionable labels -> HOLD_FOR_MORE_FROZEN_DATA_WINDOWS. Runs no replay; "
            "advances nothing."),
        # integrity
        "dataset_sha256_pinned": DATASET_SHA256,
        "dataset_sha256_observed": str(observed_dataset_sha).lower(),
        "dataset_sha_matches": dataset_sha_ok,
        "labels_artifact_sha256_pinned": LABELS_ARTIFACT_SHA256,
        "labels_artifact_sha256_observed": str(observed_labels_artifact_sha).lower(),
        "labels_artifact_sha_matches": labels_sha_ok,
        "labels_record_valid": labels_valid,
        "labels_produced_verdict_ok": labels_produced_ok,
        "tiebreaker_applied_without_mutation": tiebreaker_applied and no_mutation,
        "source_data_not_mutated": no_mutation,
        "evidence_integrity_ok": integrity_ok,
        # label distribution
        "n_total_labels": n_total,
        "n_long_entry": n_long, "n_hedge_short": n_hedge, "n_bear_short": n_bear,
        "n_none": n_none, "n_skip": n_skip,
        "n_actionable_labels": n_actionable,
        "setup_density": round(setup_density, 4),
        "near_zero_setup_pressure": n_actionable <= 2,
        # sample size
        "n_frozen_data_windows": n_frozen_data_windows,
        "distinct_decision_dates": distinct_decision_dates,
        "n_distinct_decision_dates": n_decision_dates,
        "min_frozen_data_windows_for_replay": MIN_FROZEN_DATA_WINDOWS_FOR_REPLAY,
        "min_distinct_decision_dates_for_replay":
            MIN_DISTINCT_DECISION_DATES_FOR_REPLAY,
        "min_actionable_labels_for_replay": MIN_ACTIONABLE_LABELS_FOR_REPLAY,
        "sample_sufficient_for_replay": sample_sufficient_for_replay,
        "single_day_replay_is_justified": single_day_replay_is_justified,
        "sample_size_reasons": sample_size_reasons,
        "precedent_note": PRECEDENT_NOTE,
        # outcome
        "recommendation": recommendation,
        "next_required_action": next_action,
        "advances_nothing": True,
        "replay_gate_locked": True, "paper_trading_gate_locked": True,
        "live_gate_locked": True,
        "human_review_required": True,
        "current_loop_stage": "real_candle_labels_review",
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_file_io": True, "no_network_io": True,
        "no_replay": True, "no_build_replay": True, "no_backtest": True, "no_pnl": True,
        "no_optimization": True, "no_data_fetch": True, "no_stage_data": True,
        "no_mutate_dataset": True, "no_edit_labels": True, "no_repair_market_rank": True,
        "no_invent_ranks": True, "no_commit": True, "no_push": True,
        "no_auto_commit": True, "no_auto_push": True, "no_scheduler_change": True,
        "no_scheduler_install": True, "no_signum_connection": True, "no_mcp": True,
        "no_hyperliquid": True, "no_api_keys": True, "no_credentials": True,
        "no_send_email": True, "no_bot_edits": True, "no_set_trading_pair": True,
        "no_claude_routines": True, "no_send_trades": True, "no_broker": True,
        "no_order_logic": True, "no_paper_trading": True, "no_live_trading": True,
        "no_promote_gate": True, "no_unlock_replay_gate": True,
        "no_modify_c22_rules": True, "no_start_c23": True, "no_reopen_c21": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_labels_review(record: Any) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the review is research-only,
    labels-review-only; the recommendation is from the closed set and HONEST -- ADVANCE is
    allowed ONLY when the sample is sufficient AND single-day replay is justified, REJECT
    requires broken integrity, and a sound-but-thin sample yields HOLD; the replay gate
    stays locked; nothing is advanced; and every capability flag is False."""
    failures: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record

    if r.get("mode") != LR22_MODE:
        failures.append("mode_not_research_only")
    if r.get("is_labels_review_only") is not True:
        failures.append("not_labels_review_only")
    if r.get("recommendation") not in (REC_ADVANCE, REC_HOLD, REC_REJECT):
        failures.append("bad_recommendation")

    # SHAs pinned
    if r.get("dataset_sha256_pinned") != DATASET_SHA256:
        failures.append("dataset_sha_pin_tampered")
    if r.get("labels_artifact_sha256_pinned") != LABELS_ARTIFACT_SHA256:
        failures.append("labels_sha_pin_tampered")

    integrity_ok = r.get("evidence_integrity_ok") is True
    sufficient = r.get("sample_sufficient_for_replay") is True
    justified = r.get("single_day_replay_is_justified") is True
    rec = r.get("recommendation")

    # HONESTY: the recommendation must match the integrity + sample facts.
    if rec == REC_ADVANCE:
        if not (integrity_ok and sufficient and justified):
            failures.append("advance_without_sufficient_justified_sample")
        if r.get("next_required_action") != NEXT_ACTION_ADVANCE:
            failures.append("advance_next_action_wrong")
    elif rec == REC_REJECT:
        if integrity_ok:
            failures.append("reject_requires_broken_integrity")
        if r.get("next_required_action") != NEXT_ACTION_REJECT:
            failures.append("reject_next_action_wrong")
    else:  # HOLD
        if not integrity_ok:
            failures.append("hold_requires_intact_integrity")
        if sufficient and justified:
            failures.append("hold_but_sample_sufficient_and_justified")
        if not r.get("sample_size_reasons"):
            failures.append("hold_must_state_sample_size_reasons")
        if r.get("next_required_action") != NEXT_ACTION_HOLD:
            failures.append("hold_next_action_wrong")

    # sample facts must be internally consistent
    if r.get("n_actionable_labels") != (
            r.get("n_long_entry", 0) + r.get("n_hedge_short", 0)
            + r.get("n_bear_short", 0)):
        failures.append("actionable_count_inconsistent")
    counts_sum = (r.get("n_long_entry", 0) + r.get("n_hedge_short", 0)
                  + r.get("n_bear_short", 0) + r.get("n_none", 0) + r.get("n_skip", 0))
    if counts_sum != r.get("n_total_labels"):
        failures.append("label_counts_do_not_sum_to_total")

    # no mutation / no replay claimed; replay gate locked; advances nothing
    if r.get("source_data_not_mutated") is not True:
        failures.append("source_data_must_not_be_mutated")
    if r.get("advances_nothing") is not True:
        failures.append("must_advance_nothing")
    for gate in ("replay_gate_locked", "paper_trading_gate_locked", "live_gate_locked"):
        if r.get(gate) is not True:
            failures.append("gate_unlocked_%s" % gate)

    locks = r.get("scope_locks") or {}
    for key in ("no_execute", "no_replay", "no_build_replay", "no_data_fetch",
                "no_mutate_dataset", "no_edit_labels", "no_optimization", "no_commit",
                "no_push", "no_signum_connection", "no_mcp", "no_hyperliquid",
                "no_order_logic", "no_paper_trading", "no_live_trading",
                "no_unlock_replay_gate", "no_modify_c22_rules", "no_start_c23",
                "no_reopen_c21"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

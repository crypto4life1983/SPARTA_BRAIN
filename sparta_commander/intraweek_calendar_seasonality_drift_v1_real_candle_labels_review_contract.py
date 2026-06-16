"""SPARTA CANDIDATE #10 REAL-CANDLE DETECTOR LABELS REVIEW / EVIDENCE
FREEZE (READ-ONLY, RESEARCH ONLY, SAMPLE-SIZE ADEQUACY SATISFIED,
NOT A PROFITABILITY CLAIM, NOT A RESCUE):
INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1.

Freezes the one-pass real-candle detection result on the locally
promoted canonical BTCUSD 1d spot source for the out-of-sample window
2023-01-01_2025-12-31 produced by the tracked runner
tools/c10_real_candle_detection_once.py:

  - source = data/crypto_d1_spot/raw/BTC_1d.csv, SHA-256 pinned, range
    2019-01-01 .. 2026-06-08, 2716 rows; the 2019 in-sample coverage
    blocker that previously stopped detection is now cleared and stays
    on record as a SEPARATE, STALE artifact (it is NOT used as labels
    evidence);
  - the favorable ISO-weekday bucket was selected on the IN-SAMPLE
    window 2019-01-01..2022-12-31 ONLY: weekday 5 (Friday) is the
    unique in-sample winner whose mean cleared the 81 bps gross floor
    (per-weekday in-sample means are frozen in the artifact);
  - the scan then ran over the OUT-OF-SAMPLE window
    2023-01-01..2025-12-31 only, firing the calendar-only Friday
    trigger on 156 bars;
  - 156 accepted setups before the proposal-level anti-cluster filter;
  - 156 accepted setups after the proposal-level anti-cluster filter;
  - 0 dropped by anti-cluster (the 5-daily-bar weekly cadence means no
    two accepted Friday events fall inside the 5-bar gap);
  - 0 rejected by the scanner on this window (every Friday trigger in
    the OOS window produced a valid stop, a valid entry-bar close, an
    evaluation bar, and cleared the 81 bps fee-aware floor);
  - identity check 1: 156 + 0 = 156 (accepted-pre + rejected =
    attempts);
  - identity check 2: 156 + 0 = 156 (accepted-post + drops =
    accepted-pre);
  - SAMPLE-SIZE ADEQUACY SATISFIED: 156 accepted-post >= 100 threshold;
    below-minimum-at-dry-run = False; the sample-size adequacy gate
    enforced at this labels-review gate PASSES and does NOT consume the
    single C10 edit token;
  - anti-cluster: 5-bar min gap, proposal-locked, NOT edit token;
  - every accepted record is BTCUSD / 1d / long_only, status
    accepted_for_replay_review, trigger ISO weekday 5 (Friday),
    favorable_weekday_bucket 5, calendar_condition_passes True;
  - replay_executed_now: False; pnl_computed: False;
  - single C10 edit token NOT applied (a satisfied sample-size gate is
    not an edit).

EVIDENCE LANGUAGE ONLY. NO edge has been demonstrated. NO
profitability is claimed. The honest finding is that on the
out-of-sample window 2023-01-01..2025-12-31 the calendar-only Friday
trigger (selected from the in-sample window only) fired on 156 BTCUSD
daily bars, all 156 cleared the 81 bps fee-aware floor with a valid
stop / entry / evaluation bar, none were dropped by the 5-bar
anti-cluster filter, and the resulting 156 accepted setups MEET the
proposal-locked sample-size adequacy threshold of 100. Whether to
spend any C10 edit token, proceed to a replay evaluation, or reject
Candidate #10 is the HUMAN DECISION at the next gate. This labels
review authorizes NONE of those.

This module observes the UNTRACKED artifacts READ-ONLY, recounts
acceptance and drop totals from the labels JSON itself, re-verifies
the labels and summary SHA-256 pins, re-verifies the canonical source
SHA-256 / range / row-count pin, confirms the old coverage blocker is
unchanged and separate, verifies the summary's self-claimed flags,
and certifies every frozen fact. It runs nothing, fetches nothing,
modifies nothing, and authorizes nothing.

Chain-gated live on: the pushed nine-record rejection ledger (C1-C9),
the pushed C10 family proposal, the pushed C10 spec review, the pushed
C10 detector spec + synthetic-fixture dry-run path, the pushed C10
dry-run review, the pushed V5 + V4 + V3 rejected-family blacklists,
the pushed Overnight Research Autopilot V2, the pushed Recommendation
V1, and the pushed Autopilot Loop V1.
"""

from __future__ import annotations

import hashlib as _hashlib
import json as _json
import pathlib as _pathlib
from typing import Any

import sparta_commander.strategy_factory_autopilot_research_loop_v1_contract as _loop
import sparta_commander.strategy_factory_candidate_recommendation_v1_contract as _rec
from sparta_commander.btc_sol_long_trend_continuation_v1_result_and_rejection_record_contract import (
    REJECTION_STATUS as C3_STATUS,
)
from sparta_commander.crypto_intraday_breakout_pullback_structure_v2_result_and_rejection_record_contract import (
    REJECTION_STATUS as C2_STATUS,
)
from sparta_commander.eth_sol_relative_strength_rejection_record_contract import (
    REJECTION_STATUS as C5_STATUS,
)
from sparta_commander.intraweek_calendar_seasonality_drift_v1_detector_spec_dry_run_contract import (
    VERDICT_C10D_READY,
    build_candidate_10_detector_spec_contract,
)
from sparta_commander.intraweek_calendar_seasonality_drift_v1_dry_run_review_contract import (
    VERDICT_C10R_FROZEN,
    build_candidate_10_dry_run_review,
)
from sparta_commander.intraweek_calendar_seasonality_drift_v1_family_proposal_contract import (
    CANDIDATE_FAMILY,
    CANDIDATE_ID,
    VERDICT_C10P_READY,
    build_candidate_10_family_proposal,
)
from sparta_commander.intraweek_calendar_seasonality_drift_v1_spec_review_contract import (
    VERDICT_C10S_READY,
    build_candidate_10_spec_review,
)
from sparta_commander.liquidity_sweep_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C8_STATUS,
)
from sparta_commander.low_volume_downside_capitulation_mean_reversion_v1_rejection_record import (
    REJECTION_STATUS as C9_STATUS,
)
from sparta_commander.multi_symbol_relative_strength_rotation_filter_rejection_record_contract import (
    REJECTION_STATUS as C6_STATUS,
)
from sparta_commander.ny_session_fvg_choch_v3_result_and_candidate_rejection_record_contract import (
    REJECTION_STATUS as C1_STATUS,
)
from sparta_commander.sol_btc_long_1h_swing_structure_rejection_record_contract import (
    REJECTION_STATUS as C4_STATUS,
)
from sparta_commander.strategy_factory_overnight_research_autopilot_v2_contract import (
    VERDICT_OAP2_READY,
    build_overnight_research_autopilot_v2_contract,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v3_contract import (
    VERDICT_BL3_READY,
    build_rejected_family_blacklist_v3,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v4_contract import (
    VERDICT_BL4_READY,
    build_rejected_family_blacklist_v4,
)
from sparta_commander.strategy_factory_rejected_family_blacklist_v5_contract import (
    VERDICT_BL5_READY,
    build_rejected_family_blacklist_v5,
)
from sparta_commander.volatility_compression_expansion_v1_rejection_record import (
    REJECTION_STATUS as C7_STATUS,
)

C10L_SCHEMA_VERSION = (
    "intraweek_calendar_seasonality_drift_v1_real"
    "_candle_labels_review.v1")
C10L_LABEL = ("SPARTA Candidate #10 Real-Candle Labels Review / "
              "Evidence Freeze (READ-ONLY, RESEARCH ONLY, 156 "
              "ACCEPTED POST ANTI-CLUSTER, SAMPLE-SIZE ADEQUACY "
              "SATISFIED, NOT A PROFITABILITY CLAIM, NOT A RESCUE)")
C10L_MODE = "RESEARCH_ONLY"
VERDICT_C10L_FROZEN = (
    "CANDIDATE_10_REAL_CANDLE_LABELS_REVIEW_FROZEN")
VERDICT_C10L_REJECTED = (
    "CANDIDATE_10_REAL_CANDLE_LABELS_REVIEW_REJECTED")
VERDICT_C10L_BLOCKED = (
    "CANDIDATE_10_REAL_CANDLE_LABELS_REVIEW_BLOCKED")
NEXT_REQUIRED_ACTION = (
    "HUMAN_DECISION_C10_REPLAY_EVALUATION_OR_REJECT")
CURRENT_LOOP_STAGE = "detector_and_label_review"

HEAD_AT_DETECTION = "225c655f8afe28663b2cca4dbbb9252106092e17"
RUNNER_PATH = "tools/c10_real_candle_detection_once.py"
LABELS_PATH = (
    "data/intraweek_calendar_seasonality_c10/detector_labels/"
    "c10_detector_labels_2023-01-01_2025-12-31.json")
SUMMARY_PATH = (
    "data/intraweek_calendar_seasonality_c10/detector_labels/"
    "c10_detector_summary_2023-01-01_2025-12-31.json")
EXPECTED_LABELS_SHA256 = (
    "8276e9a6ee9bd9b89ff28a41f5c160973934bcc03ad8c5371095e62fb8f9c47d")
EXPECTED_SUMMARY_SHA256 = (
    "d23d0c34363d4e0cde3413d40266046c8fc4dbcd16a084afbefccfa933a2c8ee")

# ---- canonical source pin (promoted, MUST stay unchanged) ----------------
EXPECTED_SOURCE_PATH = "data/crypto_d1_spot/raw/BTC_1d.csv"
EXPECTED_SOURCE_SHA256 = (
    "043fb722b35e738a0c2050f9388defc7ca99322ed2f153989746ee28bbb89b88")
EXPECTED_SOURCE_FIRST_DATE = "2019-01-01"
EXPECTED_SOURCE_LAST_DATE = "2026-06-08"
EXPECTED_SOURCE_ROW_COUNT = 2716

# ---- old coverage blocker: must stay SEPARATE and STALE ------------------
BLOCKER_PATH = (
    "data/intraweek_calendar_seasonality_c10/coverage_blocker/"
    "c10_real_candle_coverage_blocker.json")
EXPECTED_BLOCKER_SHA256 = (
    "9e66f0f227e7cbd67710d8ae98288fb96303e2a81afe11a4b5eb4aafed66c7d6")

# ---- windows / selection -------------------------------------------------
EXPECTED_IN_SAMPLE_WINDOW = ["2019-01-01", "2022-12-31"]
EXPECTED_OUT_OF_SAMPLE_WINDOW = ["2023-01-01", "2025-12-31"]
EXPECTED_SAMPLE_TAG = "2023-01-01_2025-12-31"
EXPECTED_FAVORABLE_WEEKDAY_BUCKET = 5
EXPECTED_PER_WEEKDAY_IN_SAMPLE_MEAN_BPS = {
    "1": 42.439863, "2": 34.275643, "3": 28.648206,
    "4": 61.298382, "5": 83.896091, "6": 34.668263,
    "7": 69.495734,
}

# ---- frozen counts from the labels artifact ------------------------------
EXPECTED_TOTAL_ATTEMPTS = 156
EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER = 156
EXPECTED_ACCEPTED_POST_ANTI_CLUSTER = 156
EXPECTED_REJECTED_BY_SCANNER = 0
EXPECTED_DROPPED_BY_ANTI_CLUSTER = 0

EXPECTED_STATUS_BREAKDOWN = {
    "accepted_for_replay_review": 156,
}

EXPECTED_IDENTITY_CHECKS = {
    "accepted_pre_plus_rejected_equals_attempts":
        EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER
        + EXPECTED_REJECTED_BY_SCANNER == EXPECTED_TOTAL_ATTEMPTS,
    "accepted_post_plus_dropped_equals_accepted_pre":
        EXPECTED_ACCEPTED_POST_ANTI_CLUSTER
        + EXPECTED_DROPPED_BY_ANTI_CLUSTER
        == EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER,
}

EXPECTED_SAMPLE_SIZE_ADEQUACY = {
    "accepted_count": 156,
    "below_minimum_at_dry_run": False,
    "does_not_consume_edit_token": True,
    "enforced_at_labels_review_gate_only": True,
    "minimum_required_at_labels_review_gate": 100,
}
EXPECTED_SAMPLE_SIZE_SATISFIED = True
EXPECTED_SAMPLE_SIZE_STRUCTURAL_FAILURE = False

EXPECTED_ANTI_CLUSTER_FACTS = {
    "anti_cluster_min_bar_gap": 5,
    "tie_breaker": "keep_the_earlier_event_drop_the_later_one",
    "anti_cluster_does_not_consume_edit_token": True,
    "accepted_before_anti_cluster": 156,
    "accepted_after_anti_cluster": 156,
    "dropped_by_anti_cluster": 0,
}

EXPECTED_SCOPE_LOCKS = {
    "c10_contract_not_weakened_for_missing_2019": True,
    "frozen_regime_inputs_source_not_used": True,
    "no_api": True,
    "no_broker": True,
    "no_credentials": True,
    "no_downstream_gates_unlocked": True,
    "no_edit_token_consumed": True,
    "no_exchange": True,
    "no_fetch": True,
    "no_live_trading": True,
    "no_micro_live": True,
    "no_network": True,
    "no_paper_trading": True,
    "no_pnl": True,
    "no_relabel": True,
    "no_replay": True,
    "no_scheduler": True,
    "no_wallet": True,
}

EXPECTED_SUMMARY_SELF_CLAIMS = {
    "candidate_id": "INTRAWEEK_CALENDAR_SEASONALITY_DRIFT_V1",
    "candidate_family": "intraweek_calendar_seasonality_drift",
    "symbol": "BTCUSD",
    "timeframe": "1d",
    "direction": "long_only",
    "sample_tag": EXPECTED_SAMPLE_TAG,
    "favorable_weekday_bucket": EXPECTED_FAVORABLE_WEEKDAY_BUCKET,
    "attempts": EXPECTED_TOTAL_ATTEMPTS,
    "accepted_pre_anti_cluster": EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER,
    "accepted_post_anti_cluster":
        EXPECTED_ACCEPTED_POST_ANTI_CLUSTER,
    "anti_cluster_dropped_count": EXPECTED_DROPPED_BY_ANTI_CLUSTER,
    "anti_cluster_min_bar_gap": 5,
    "anti_cluster_does_not_consume_edit_token": True,
    "minimum_labels_review_threshold": 100,
    "source_path": EXPECTED_SOURCE_PATH,
    "source_sha256_before": EXPECTED_SOURCE_SHA256,
    "source_sha256_after": EXPECTED_SOURCE_SHA256,
    "source_first_date": EXPECTED_SOURCE_FIRST_DATE,
    "source_last_date": EXPECTED_SOURCE_LAST_DATE,
    "source_row_count": EXPECTED_SOURCE_ROW_COUNT,
    "source_unchanged_during_detection": True,
}

FROZEN_DETECTION_FACTS = (
    "single-symbol btcusd 1d, long-only labels-only research",
    "locally promoted canonical btcusd 1d spot source only; no fetch",
    "source range 2019-01-01..2026-06-08, 2716 rows, sha-256 pinned",
    "the missing-2019 in-sample coverage blocker is now cleared and "
    "remains a SEPARATE, STALE artifact; it is NOT used as labels "
    "evidence",
    "favorable iso-weekday bucket selected on the IN-SAMPLE window "
    "2019-01-01..2022-12-31 ONLY: weekday 5 (friday) is the unique "
    "in-sample winner clearing the 81 bps gross floor",
    "scan ran over the OUT-OF-SAMPLE window 2023-01-01..2025-12-31 "
    "only",
    "156 calendar-only friday trigger attempts on the oos window",
    "156 accepted before anti-cluster; 156 accepted after "
    "anti-cluster",
    "0 rejected by the scanner: every oos friday trigger produced a "
    "valid stop, a valid entry-bar close, an evaluation bar, and "
    "cleared the 81 bps fee-aware floor",
    "0 dropped by the 5-bar anti-cluster (the weekly friday cadence "
    "keeps every accepted event outside the 5-bar gap)",
    "156 + 0 = 156 (accepted-pre + rejected = attempts)",
    "156 + 0 = 156 (accepted-post + drops = accepted-pre)",
    "SAMPLE-SIZE ADEQUACY SATISFIED: 156 accepted-post >= 100 "
    "threshold; below-minimum-at-dry-run = false",
    "every accepted record is btcusd / 1d / long_only, status "
    "accepted_for_replay_review, trigger iso weekday 5, "
    "favorable_weekday_bucket 5, calendar_condition_passes true",
    "anti-cluster gap remains proposal-level locked at 5 bars and "
    "does NOT consume the single c10 edit token",
    "sample-size adequacy threshold remains proposal-level locked at "
    "100 accepted setups; the satisfied flag is recorded WITHOUT "
    "spending the token",
    "no replay; no pnl; no relabel; no edit token applied",
    "no profitability claim, no winner wording, no paper/live "
    "approval",
)

CLAIM_LOCKS = (
    "no_profitability_claim",
    "no_paper_approval",
    "no_live_approval",
    "no_execution_approval",
    "no_winner_wording",
    "no_replay_authorized_by_this_gate",
    "no_relabel_authorized_by_this_gate",
    "no_edit_token_applied_by_this_gate",
    "no_rejection_decision_made_by_this_gate",
    "no_promotion_decision_made_by_this_gate",
    "anti_cluster_gap_remains_proposal_level_locked",
    "sample_size_threshold_remains_proposal_level_locked",
    "old_coverage_blocker_remains_separate_and_stale",
)


def get_candidate_10_labels_review_label() -> str:
    return C10L_LABEL


def observe_c10_labels(repo_root: Any,
                       tracked_paths: Any = ()
                       ) -> dict[str, Any]:
    """Read the untracked artifacts READ-ONLY and recount the facts.
    Never raises on missing files; reports absence instead."""
    observation: dict[str, Any] = {
        "labels_exists": False, "summary_exists": False,
        "labels_sha256": None, "summary_sha256": None,
        "labels_accepted_post_count": None,
        "labels_dropped_count": None,
        "labels_all_accepted_symbol_btcusd": None,
        "labels_all_accepted_timeframe_1d": None,
        "labels_all_accepted_direction_long_only": None,
        "labels_all_accepted_status_accepted_for_replay_review":
            None,
        "labels_all_accepted_trigger_iso_weekday_5": None,
        "labels_all_accepted_favorable_weekday_bucket_5": None,
        "labels_all_accepted_calendar_condition_passes": None,
        "labels_all_dropped_status_clustered": None,
        "labels_anti_cluster_min_bar_gap": None,
        "labels_anti_cluster_tie_breaker": None,
        "labels_anti_cluster_does_not_consume_edit_token": None,
        "labels_attempts": None,
        "labels_accepted_pre_anti_cluster": None,
        "labels_accepted_post_anti_cluster": None,
        "labels_anti_cluster_dropped_count": None,
        "labels_status_breakdown": None,
        "labels_sample_size_adequacy": None,
        "labels_scope_locks": None,
        "labels_favorable_weekday_bucket": None,
        "labels_in_sample_selection_window": None,
        "labels_out_of_sample_window": None,
        "labels_sample_tag": None,
        "labels_per_weekday_in_sample_mean_bps": None,
        "labels_source_path": None,
        "labels_source_sha256_before": None,
        "labels_source_sha256_after": None,
        "labels_source_first_date": None,
        "labels_source_last_date": None,
        "labels_source_row_count": None,
        "labels_source_unchanged_during_detection": None,
        "summary_candidate_id": None,
        "summary_candidate_family": None,
        "summary_symbol": None,
        "summary_timeframe": None,
        "summary_direction": None,
        "summary_sample_tag": None,
        "summary_favorable_weekday_bucket": None,
        "summary_attempts": None,
        "summary_accepted_pre_anti_cluster": None,
        "summary_accepted_post_anti_cluster": None,
        "summary_anti_cluster_dropped_count": None,
        "summary_anti_cluster_min_bar_gap": None,
        "summary_anti_cluster_does_not_consume_edit_token": None,
        "summary_minimum_labels_review_threshold": None,
        "summary_source_path": None,
        "summary_source_sha256_before": None,
        "summary_source_sha256_after": None,
        "summary_source_first_date": None,
        "summary_source_last_date": None,
        "summary_source_row_count": None,
        "summary_source_unchanged_during_detection": None,
        "summary_status_breakdown": None,
        "summary_sample_size_adequacy": None,
        "summary_scope_locks": None,
        "summary_labels_sha256_self_reported": None,
        "source_sha256_now": None,
        "source_sha256_match": None,
        "blocker_exists": False,
        "blocker_sha256_now": None,
        "blocker_unchanged_and_separate": None,
        "artifacts_tracked_in_git": [],
    }
    root = _pathlib.Path(str(repo_root))
    tracked = {str(p).replace("\\", "/")
               for p in (tracked_paths or ())}
    # Only the two JSON artifacts must stay untracked. The runner and
    # the coverage blocker are intentionally tracked for C10.
    for rel in (LABELS_PATH, SUMMARY_PATH):
        if rel in tracked:
            observation["artifacts_tracked_in_git"].append(rel)
    # canonical source must be unchanged
    source_file = root / EXPECTED_SOURCE_PATH
    if source_file.is_file():
        observation["source_sha256_now"] = _hashlib.sha256(
            source_file.read_bytes()).hexdigest()
    observation["source_sha256_match"] = (
        observation["source_sha256_now"] == EXPECTED_SOURCE_SHA256)
    # old coverage blocker must be unchanged, separate and stale
    blocker_file = root / BLOCKER_PATH
    if blocker_file.is_file():
        observation["blocker_exists"] = True
        observation["blocker_sha256_now"] = _hashlib.sha256(
            blocker_file.read_bytes()).hexdigest()
    observation["blocker_unchanged_and_separate"] = (
        observation["blocker_sha256_now"] == EXPECTED_BLOCKER_SHA256
        and BLOCKER_PATH != LABELS_PATH
        and BLOCKER_PATH != SUMMARY_PATH)
    summary_file = root / SUMMARY_PATH
    labels_file = root / LABELS_PATH
    if summary_file.is_file():
        observation["summary_exists"] = True
        raw_summary = summary_file.read_bytes()
        observation["summary_sha256"] = _hashlib.sha256(
            raw_summary).hexdigest()
        summary = _json.loads(raw_summary.decode("utf-8"))
        for src_key, dst_key in (
                ("candidate_id", "summary_candidate_id"),
                ("candidate_family", "summary_candidate_family"),
                ("symbol", "summary_symbol"),
                ("timeframe", "summary_timeframe"),
                ("direction", "summary_direction"),
                ("sample_tag", "summary_sample_tag"),
                ("favorable_weekday_bucket",
                 "summary_favorable_weekday_bucket"),
                ("attempts", "summary_attempts"),
                ("accepted_pre_anti_cluster",
                 "summary_accepted_pre_anti_cluster"),
                ("accepted_post_anti_cluster",
                 "summary_accepted_post_anti_cluster"),
                ("anti_cluster_dropped_count",
                 "summary_anti_cluster_dropped_count"),
                ("anti_cluster_min_bar_gap",
                 "summary_anti_cluster_min_bar_gap"),
                ("anti_cluster_does_not_consume_edit_token",
                 "summary_anti_cluster_does_not_consume_edit_token"),
                ("minimum_labels_review_threshold",
                 "summary_minimum_labels_review_threshold"),
                ("source_path", "summary_source_path"),
                ("source_sha256_before",
                 "summary_source_sha256_before"),
                ("source_sha256_after",
                 "summary_source_sha256_after"),
                ("source_first_date", "summary_source_first_date"),
                ("source_last_date", "summary_source_last_date"),
                ("source_row_count", "summary_source_row_count"),
                ("source_unchanged_during_detection",
                 "summary_source_unchanged_during_detection"),
                ("status_breakdown", "summary_status_breakdown"),
                ("sample_size_adequacy",
                 "summary_sample_size_adequacy"),
                ("scope_locks", "summary_scope_locks"),
                ("labels_sha256",
                 "summary_labels_sha256_self_reported")):
            observation[dst_key] = summary.get(src_key)
    if not labels_file.is_file():
        return observation
    observation["labels_exists"] = True
    raw_labels = labels_file.read_bytes()
    observation["labels_sha256"] = _hashlib.sha256(
        raw_labels).hexdigest()
    labels = _json.loads(raw_labels.decode("utf-8"))
    accepted_post = labels.get(
        "accepted_setups_post_anti_cluster") or []
    dropped = labels.get("anti_cluster_dropped") or []
    observation["labels_accepted_post_count"] = len(accepted_post)
    observation["labels_dropped_count"] = len(dropped)
    observation["labels_all_accepted_symbol_btcusd"] = (
        len(accepted_post) > 0 and all(
            s.get("symbol") == "BTCUSD" for s in accepted_post))
    observation["labels_all_accepted_timeframe_1d"] = (
        len(accepted_post) > 0 and all(
            s.get("timeframe") == "1d" for s in accepted_post))
    observation["labels_all_accepted_direction_long_only"] = (
        len(accepted_post) > 0 and all(
            s.get("direction") == "long_only"
            for s in accepted_post))
    observation[
        "labels_all_accepted_status_accepted_for_replay_review"
    ] = (len(accepted_post) > 0 and all(
        s.get("status") == "accepted_for_replay_review"
        for s in accepted_post))
    observation["labels_all_accepted_trigger_iso_weekday_5"] = (
        len(accepted_post) > 0 and all(
            s.get("trigger_iso_weekday") == 5
            for s in accepted_post))
    observation[
        "labels_all_accepted_favorable_weekday_bucket_5"] = (
        len(accepted_post) > 0 and all(
            s.get("favorable_weekday_bucket") == 5
            for s in accepted_post))
    observation[
        "labels_all_accepted_calendar_condition_passes"] = (
        len(accepted_post) > 0 and all(
            s.get("calendar_condition_passes") is True
            for s in accepted_post))
    # vacuously True when no drops; otherwise verify clustered status.
    observation["labels_all_dropped_status_clustered"] = all(
        str(s.get("status", "")).startswith("rejected_clustered")
        for s in dropped)
    observation["labels_anti_cluster_min_bar_gap"] = labels.get(
        "anti_cluster_min_bar_gap")
    observation["labels_anti_cluster_tie_breaker"] = labels.get(
        "anti_cluster_tie_breaker")
    observation[
        "labels_anti_cluster_does_not_consume_edit_token"] = (
        labels.get("anti_cluster_does_not_consume_edit_token"))
    observation["labels_attempts"] = labels.get("attempts")
    observation["labels_accepted_pre_anti_cluster"] = labels.get(
        "accepted_pre_anti_cluster")
    observation["labels_accepted_post_anti_cluster"] = labels.get(
        "accepted_post_anti_cluster")
    observation["labels_anti_cluster_dropped_count"] = labels.get(
        "anti_cluster_dropped_count")
    observation["labels_status_breakdown"] = labels.get(
        "status_breakdown")
    observation["labels_sample_size_adequacy"] = labels.get(
        "sample_size_adequacy")
    observation["labels_scope_locks"] = labels.get("scope_locks")
    observation["labels_favorable_weekday_bucket"] = labels.get(
        "favorable_weekday_bucket")
    observation["labels_in_sample_selection_window"] = labels.get(
        "in_sample_selection_window")
    observation["labels_out_of_sample_window"] = labels.get(
        "out_of_sample_window")
    observation["labels_sample_tag"] = labels.get("sample_tag")
    observation["labels_per_weekday_in_sample_mean_bps"] = (
        labels.get("per_weekday_in_sample_mean_bps"))
    observation["labels_source_path"] = labels.get("source_path")
    observation["labels_source_sha256_before"] = labels.get(
        "source_sha256_before")
    observation["labels_source_sha256_after"] = labels.get(
        "source_sha256_after")
    observation["labels_source_first_date"] = labels.get(
        "source_first_date")
    observation["labels_source_last_date"] = labels.get(
        "source_last_date")
    observation["labels_source_row_count"] = labels.get(
        "source_row_count")
    observation[
        "labels_source_unchanged_during_detection"] = labels.get(
        "source_unchanged_during_detection")
    return observation


def certify_c10_labels_review(observation: Any) -> dict[str, Any]:
    """Pure certification of an observation against the frozen facts.
    Never raises."""
    failures: list[str] = []
    if not isinstance(observation, dict):
        return {"certified": False,
                "failures": ["observation_not_a_dict"]}
    o = observation
    if not o.get("labels_exists"):
        failures.append("labels_artifact_missing")
    if not o.get("summary_exists"):
        failures.append("summary_artifact_missing")
    if failures:
        return {"certified": False, "failures": failures}
    if o.get("labels_sha256") != EXPECTED_LABELS_SHA256:
        failures.append("labels_sha_mismatch")
    if o.get("summary_sha256") != EXPECTED_SUMMARY_SHA256:
        failures.append("summary_sha_mismatch")
    # recount from the labels JSON itself
    if o.get("labels_accepted_post_count") != (
            EXPECTED_ACCEPTED_POST_ANTI_CLUSTER):
        failures.append("labels_accepted_post_count_must_equal_156")
    if o.get("labels_dropped_count") != (
            EXPECTED_DROPPED_BY_ANTI_CLUSTER):
        failures.append("labels_dropped_count_must_equal_0")
    if o.get("labels_all_accepted_symbol_btcusd") is not True:
        failures.append("accepted_setups_not_all_btcusd")
    if o.get("labels_all_accepted_timeframe_1d") is not True:
        failures.append("accepted_setups_not_all_1d")
    if o.get("labels_all_accepted_direction_long_only") is not True:
        failures.append("accepted_setups_not_all_long_only")
    if o.get(
            "labels_all_accepted_status_accepted_for_replay_review"
    ) is not True:
        failures.append(
            "accepted_setups_not_all_accepted_for_replay_review")
    if o.get(
            "labels_all_accepted_trigger_iso_weekday_5") is not True:
        failures.append("accepted_setups_not_all_friday_weekday_5")
    if o.get(
            "labels_all_accepted_favorable_weekday_bucket_5"
    ) is not True:
        failures.append("accepted_setups_not_all_bucket_5")
    if o.get(
            "labels_all_accepted_calendar_condition_passes"
    ) is not True:
        failures.append(
            "accepted_setups_not_all_calendar_condition_passes")
    if o.get("labels_all_dropped_status_clustered") is not True:
        failures.append("dropped_setups_not_all_clustered_status")
    if o.get("labels_anti_cluster_min_bar_gap") != 5:
        failures.append("labels_anti_cluster_min_bar_gap_must_be_5")
    if o.get("labels_anti_cluster_tie_breaker") != (
            "keep_the_earlier_event_drop_the_later_one"):
        failures.append("labels_anti_cluster_tie_breaker_mismatch")
    if o.get(
            "labels_anti_cluster_does_not_consume_edit_token"
    ) is not True:
        failures.append(
            "labels_anti_cluster_must_not_consume_edit_token")
    if o.get("labels_attempts") != EXPECTED_TOTAL_ATTEMPTS:
        failures.append("labels_attempts_must_equal_156")
    if o.get("labels_accepted_pre_anti_cluster") != (
            EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER):
        failures.append("labels_accepted_pre_must_equal_156")
    if o.get("labels_accepted_post_anti_cluster") != (
            EXPECTED_ACCEPTED_POST_ANTI_CLUSTER):
        failures.append("labels_accepted_post_field_must_equal_156")
    if o.get("labels_anti_cluster_dropped_count") != (
            EXPECTED_DROPPED_BY_ANTI_CLUSTER):
        failures.append("labels_dropped_count_field_must_equal_0")
    if o.get("labels_status_breakdown") != EXPECTED_STATUS_BREAKDOWN:
        failures.append("labels_status_breakdown_mismatch")
    if o.get("labels_sample_size_adequacy") != (
            EXPECTED_SAMPLE_SIZE_ADEQUACY):
        failures.append("labels_sample_size_adequacy_mismatch")
    if o.get("labels_scope_locks") != EXPECTED_SCOPE_LOCKS:
        failures.append("labels_scope_locks_mismatch")
    if o.get("labels_favorable_weekday_bucket") != (
            EXPECTED_FAVORABLE_WEEKDAY_BUCKET):
        failures.append("labels_favorable_weekday_bucket_must_be_5")
    if o.get("labels_in_sample_selection_window") != (
            EXPECTED_IN_SAMPLE_WINDOW):
        failures.append("labels_in_sample_window_mismatch")
    if o.get("labels_out_of_sample_window") != (
            EXPECTED_OUT_OF_SAMPLE_WINDOW):
        failures.append("labels_out_of_sample_window_mismatch")
    if o.get("labels_sample_tag") != EXPECTED_SAMPLE_TAG:
        failures.append("labels_sample_tag_mismatch")
    if o.get("labels_per_weekday_in_sample_mean_bps") != (
            EXPECTED_PER_WEEKDAY_IN_SAMPLE_MEAN_BPS):
        failures.append("labels_per_weekday_in_sample_mean_mismatch")
    # source pin from the labels artifact
    if o.get("labels_source_path") != EXPECTED_SOURCE_PATH:
        failures.append("labels_source_path_mismatch")
    if o.get("labels_source_sha256_before") != EXPECTED_SOURCE_SHA256:
        failures.append("labels_source_sha_before_mismatch")
    if o.get("labels_source_sha256_after") != EXPECTED_SOURCE_SHA256:
        failures.append("labels_source_sha_after_mismatch")
    if o.get("labels_source_first_date") != (
            EXPECTED_SOURCE_FIRST_DATE):
        failures.append("labels_source_first_date_mismatch")
    if o.get("labels_source_last_date") != EXPECTED_SOURCE_LAST_DATE:
        failures.append("labels_source_last_date_mismatch")
    if o.get("labels_source_row_count") != EXPECTED_SOURCE_ROW_COUNT:
        failures.append("labels_source_row_count_mismatch")
    if o.get(
            "labels_source_unchanged_during_detection") is not True:
        failures.append(
            "labels_source_unchanged_during_detection_must_be_true")
    # summary self-claims
    for key, want in EXPECTED_SUMMARY_SELF_CLAIMS.items():
        got = o.get("summary_" + key)
        if got != want:
            failures.append("summary_claim_mismatch:" + key)
    if o.get("summary_status_breakdown") != (
            EXPECTED_STATUS_BREAKDOWN):
        failures.append("summary_status_breakdown_mismatch")
    if o.get("summary_sample_size_adequacy") != (
            EXPECTED_SAMPLE_SIZE_ADEQUACY):
        failures.append("summary_sample_size_adequacy_mismatch")
    if o.get("summary_scope_locks") != EXPECTED_SCOPE_LOCKS:
        failures.append("summary_scope_locks_mismatch")
    if o.get("summary_labels_sha256_self_reported") != (
            EXPECTED_LABELS_SHA256):
        failures.append("summary_labels_sha_self_report_mismatch")
    # canonical source unchanged on disk now
    if o.get("source_sha256_match") is not True:
        failures.append("canonical_source_sha_changed")
    # old coverage blocker unchanged, separate, stale
    if o.get("blocker_unchanged_and_separate") is not True:
        failures.append("old_coverage_blocker_not_separate_or_stale")
    # the two JSON artifacts must stay untracked
    if o.get("artifacts_tracked_in_git"):
        failures.append("labels_artifacts_must_stay_untracked")
    return {"certified": not failures, "failures": failures}


def build_c10_labels_review(repo_root: Any,
                            tracked_paths: Any = ()
                            ) -> dict[str, Any]:
    """Observe read-only and certify; chain-gated on the full pushed
    C10 lane (proposal -> spec -> detector spec/dry-run -> dry-run
    review) plus V5 + V4 + V3 + Autopilot V2 + Recommendation V1 +
    Autopilot Loop V1 + the nine-record rejection ledger."""
    record: dict[str, Any] = {
        "schema_version": C10L_SCHEMA_VERSION, "label": C10L_LABEL,
        "mode": C10L_MODE, "lane": "crypto_d1_auto_research",
        "verdict": None, "blockers": [], "failures": [],
        "candidate_id": CANDIDATE_ID,
        "candidate_family": CANDIDATE_FAMILY,
        "head_at_detection": HEAD_AT_DETECTION,
        "runner_path_tracked": RUNNER_PATH,
        "labels_path": LABELS_PATH, "summary_path": SUMMARY_PATH,
        "expected_labels_sha256": EXPECTED_LABELS_SHA256,
        "expected_summary_sha256": EXPECTED_SUMMARY_SHA256,
        "expected_source_path": EXPECTED_SOURCE_PATH,
        "expected_source_sha256": EXPECTED_SOURCE_SHA256,
        "expected_source_first_date": EXPECTED_SOURCE_FIRST_DATE,
        "expected_source_last_date": EXPECTED_SOURCE_LAST_DATE,
        "expected_source_row_count": EXPECTED_SOURCE_ROW_COUNT,
        "blocker_path": BLOCKER_PATH,
        "expected_blocker_sha256": EXPECTED_BLOCKER_SHA256,
        "expected_in_sample_window": list(EXPECTED_IN_SAMPLE_WINDOW),
        "expected_out_of_sample_window":
            list(EXPECTED_OUT_OF_SAMPLE_WINDOW),
        "expected_sample_tag": EXPECTED_SAMPLE_TAG,
        "expected_favorable_weekday_bucket":
            EXPECTED_FAVORABLE_WEEKDAY_BUCKET,
        "expected_per_weekday_in_sample_mean_bps":
            dict(EXPECTED_PER_WEEKDAY_IN_SAMPLE_MEAN_BPS),
        "expected_total_attempts": EXPECTED_TOTAL_ATTEMPTS,
        "expected_accepted_pre_anti_cluster":
            EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER,
        "expected_accepted_post_anti_cluster":
            EXPECTED_ACCEPTED_POST_ANTI_CLUSTER,
        "expected_rejected_by_scanner": EXPECTED_REJECTED_BY_SCANNER,
        "expected_dropped_by_anti_cluster":
            EXPECTED_DROPPED_BY_ANTI_CLUSTER,
        "expected_status_breakdown":
            dict(EXPECTED_STATUS_BREAKDOWN),
        "expected_identity_checks":
            dict(EXPECTED_IDENTITY_CHECKS),
        "expected_sample_size_adequacy":
            dict(EXPECTED_SAMPLE_SIZE_ADEQUACY),
        "expected_sample_size_satisfied":
            EXPECTED_SAMPLE_SIZE_SATISFIED,
        "expected_sample_size_structural_failure":
            EXPECTED_SAMPLE_SIZE_STRUCTURAL_FAILURE,
        "expected_anti_cluster_facts":
            dict(EXPECTED_ANTI_CLUSTER_FACTS),
        "expected_summary_self_claims":
            dict(EXPECTED_SUMMARY_SELF_CLAIMS),
        "expected_scope_locks": dict(EXPECTED_SCOPE_LOCKS),
        "frozen_detection_facts": list(FROZEN_DETECTION_FACTS),
        "claim_locks": list(CLAIM_LOCKS),
        "ledger_status_nine_records": None,
        "ledger_all_rejected_kept_on_record": None,
        "human_review_required": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True, "live_gate_locked": True,
        "is_labels_review_only": True,
        "is_a_rescue_attempt": False,
        "edit_token_applied_by_this_gate": False,
        "rejection_decision_made_by_this_gate": False,
        "promotion_decision_made_by_this_gate": False,
        "replay_authorized_by_this_gate": False,
        "relabel_authorized_by_this_gate": False,
        "executes": False, "writes_files": False, "labels_now": False,
        "runs_real_candle_detection": False,
        "runs_relabel": False, "runs_replay": False,
        "runs_real_detection_now": False, "runs_replay_now": False,
        "scores_now": False, "stages_data_now": False,
        "fetches_data": False, "calls_api": False,
        "uses_network": False,
        "uses_credentials": False, "uses_wallet": False,
        "uses_account": False, "connects_broker": False,
        "connects_exchange": False, "uses_real_money": False,
        "contains_order_logic": False,
        "contains_portfolio_allocation_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "auto_commits": False, "auto_pushes": False,
        "creates_runners_now": False,
        "creates_data_artifacts_now": False,
        "creates_detector_implementation_now": False,
        "computes_pnl_now": False,
        "modifies_canonical_source": False,
        "modifies_detector_labels_artifacts": False,
        "modifies_coverage_blocker": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False, "unlocks_downstream_gate": False,
        "unlocks_real_candle_detection": False,
        "unlocks_replay_now": False, "unlocks_relabel_now": False,
        "unlocks_edit_token_now": False,
        "claims_profitability": False,
        "next_required_action": NEXT_REQUIRED_ACTION,
        "current_loop_stage": CURRENT_LOOP_STAGE,
    }
    statuses = (C1_STATUS, C2_STATUS, C3_STATUS, C4_STATUS, C5_STATUS,
                C6_STATUS, C7_STATUS, C8_STATUS, C9_STATUS)
    record["ledger_status_nine_records"] = list(statuses)
    record["ledger_all_rejected_kept_on_record"] = all(
        s == "REJECTED_KEPT_ON_RECORD" for s in statuses)
    if not record["ledger_all_rejected_kept_on_record"]:
        record["verdict"] = VERDICT_C10L_BLOCKED
        record["blockers"].append("nine_record_ledger_broken")
        return record
    if build_candidate_10_family_proposal()["verdict"] != (
            VERDICT_C10P_READY):
        record["verdict"] = VERDICT_C10L_BLOCKED
        record["blockers"].append(
            "candidate_10_proposal_not_certifying")
        return record
    if build_candidate_10_spec_review()["verdict"] != (
            VERDICT_C10S_READY):
        record["verdict"] = VERDICT_C10L_BLOCKED
        record["blockers"].append(
            "candidate_10_spec_review_not_certifying")
        return record
    if build_candidate_10_detector_spec_contract()["verdict"] != (
            VERDICT_C10D_READY):
        record["verdict"] = VERDICT_C10L_BLOCKED
        record["blockers"].append(
            "candidate_10_detector_spec_not_certifying")
        return record
    if build_candidate_10_dry_run_review()["verdict"] != (
            VERDICT_C10R_FROZEN):
        record["verdict"] = VERDICT_C10L_BLOCKED
        record["blockers"].append(
            "candidate_10_dry_run_review_not_certifying")
        return record
    if build_rejected_family_blacklist_v5()["verdict"] != (
            VERDICT_BL5_READY):
        record["verdict"] = VERDICT_C10L_BLOCKED
        record["blockers"].append("v5_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v4()["verdict"] != (
            VERDICT_BL4_READY):
        record["verdict"] = VERDICT_C10L_BLOCKED
        record["blockers"].append("v4_blacklist_not_certifying")
        return record
    if build_rejected_family_blacklist_v3()["verdict"] != (
            VERDICT_BL3_READY):
        record["verdict"] = VERDICT_C10L_BLOCKED
        record["blockers"].append("v3_blacklist_not_certifying")
        return record
    if build_overnight_research_autopilot_v2_contract()["verdict"] != (
            VERDICT_OAP2_READY):
        record["verdict"] = VERDICT_C10L_BLOCKED
        record["blockers"].append(
            "overnight_research_autopilot_v2_not_certifying")
        return record
    if _rec.build_candidate_recommendation()["verdict"] != (
            _rec.VERDICT_CR_READY):
        record["verdict"] = VERDICT_C10L_BLOCKED
        record["blockers"].append("recommendation_not_certifying")
        return record
    if _loop.build_autopilot_loop_contract()["verdict"] != (
            _loop.VERDICT_AP_READY):
        record["verdict"] = VERDICT_C10L_BLOCKED
        record["blockers"].append("autopilot_loop_not_certifying")
        return record
    observation = observe_c10_labels(repo_root, tracked_paths)
    result = certify_c10_labels_review(observation)
    record["failures"] = result["failures"]
    record["verdict"] = (VERDICT_C10L_FROZEN if result["certified"]
                         else VERDICT_C10L_REJECTED)
    return record


def validate_c10_labels_review(record: Any) -> dict[str, Any]:
    """Validate shape, frozen facts, and safety invariants. Never
    raises."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"valid": False, "errors": ["record_not_a_dict"]}
    r = record
    if r.get("verdict") not in (VERDICT_C10L_FROZEN,
                                VERDICT_C10L_REJECTED,
                                VERDICT_C10L_BLOCKED):
        errors.append("bad_verdict")
    if r.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if r.get("candidate_family") != CANDIDATE_FAMILY:
        errors.append("candidate_family_tampered")
    if r.get("head_at_detection") != HEAD_AT_DETECTION:
        errors.append("head_tampered")
    if r.get("expected_labels_sha256") != EXPECTED_LABELS_SHA256:
        errors.append("labels_sha_tampered")
    if r.get("expected_summary_sha256") != EXPECTED_SUMMARY_SHA256:
        errors.append("summary_sha_tampered")
    if r.get("expected_source_path") != EXPECTED_SOURCE_PATH:
        errors.append("source_path_tampered")
    if r.get("expected_source_sha256") != EXPECTED_SOURCE_SHA256:
        errors.append("source_sha_tampered")
    if r.get("expected_source_first_date") != (
            EXPECTED_SOURCE_FIRST_DATE):
        errors.append("source_first_date_tampered")
    if r.get("expected_source_last_date") != (
            EXPECTED_SOURCE_LAST_DATE):
        errors.append("source_last_date_tampered")
    if r.get("expected_source_row_count") != (
            EXPECTED_SOURCE_ROW_COUNT):
        errors.append("source_row_count_tampered")
    if r.get("blocker_path") != BLOCKER_PATH:
        errors.append("blocker_path_tampered")
    if r.get("expected_blocker_sha256") != EXPECTED_BLOCKER_SHA256:
        errors.append("blocker_sha_tampered")
    if r.get("expected_in_sample_window") != (
            EXPECTED_IN_SAMPLE_WINDOW):
        errors.append("in_sample_window_tampered")
    if r.get("expected_out_of_sample_window") != (
            EXPECTED_OUT_OF_SAMPLE_WINDOW):
        errors.append("out_of_sample_window_tampered")
    if r.get("expected_sample_tag") != EXPECTED_SAMPLE_TAG:
        errors.append("sample_tag_tampered")
    if r.get("expected_favorable_weekday_bucket") != (
            EXPECTED_FAVORABLE_WEEKDAY_BUCKET):
        errors.append("favorable_weekday_bucket_tampered")
    if r.get("expected_per_weekday_in_sample_mean_bps") != (
            EXPECTED_PER_WEEKDAY_IN_SAMPLE_MEAN_BPS):
        errors.append("per_weekday_mean_tampered")
    if r.get("expected_total_attempts") != EXPECTED_TOTAL_ATTEMPTS:
        errors.append("total_attempts_tampered")
    if r.get("expected_accepted_pre_anti_cluster") != (
            EXPECTED_ACCEPTED_PRE_ANTI_CLUSTER):
        errors.append("accepted_pre_tampered")
    if r.get("expected_accepted_post_anti_cluster") != (
            EXPECTED_ACCEPTED_POST_ANTI_CLUSTER):
        errors.append("accepted_post_tampered")
    if r.get("expected_rejected_by_scanner") != (
            EXPECTED_REJECTED_BY_SCANNER):
        errors.append("rejected_count_tampered")
    if r.get("expected_dropped_by_anti_cluster") != (
            EXPECTED_DROPPED_BY_ANTI_CLUSTER):
        errors.append("anti_cluster_dropped_tampered")
    if r.get("expected_status_breakdown") != (
            EXPECTED_STATUS_BREAKDOWN):
        errors.append("status_breakdown_tampered")
    if r.get("expected_identity_checks") != (
            EXPECTED_IDENTITY_CHECKS):
        errors.append("identity_checks_tampered")
    if r.get("expected_sample_size_adequacy") != (
            EXPECTED_SAMPLE_SIZE_ADEQUACY):
        errors.append("sample_size_adequacy_tampered")
    if r.get("expected_sample_size_satisfied") is not (
            EXPECTED_SAMPLE_SIZE_SATISFIED):
        errors.append("sample_size_satisfied_tampered")
    if r.get("expected_sample_size_structural_failure") is not (
            EXPECTED_SAMPLE_SIZE_STRUCTURAL_FAILURE):
        errors.append("sample_size_structural_failure_tampered")
    if r.get("expected_anti_cluster_facts") != (
            EXPECTED_ANTI_CLUSTER_FACTS):
        errors.append("anti_cluster_facts_tampered")
    if r.get("expected_summary_self_claims") != (
            EXPECTED_SUMMARY_SELF_CLAIMS):
        errors.append("summary_self_claims_tampered")
    if r.get("expected_scope_locks") != EXPECTED_SCOPE_LOCKS:
        errors.append("scope_locks_tampered")
    if tuple(r.get("frozen_detection_facts") or ()) != (
            FROZEN_DETECTION_FACTS):
        errors.append("frozen_detection_facts_tampered")
    if tuple(r.get("claim_locks") or ()) != CLAIM_LOCKS:
        errors.append("claim_locks_tampered")
    if r.get("next_required_action") != NEXT_REQUIRED_ACTION:
        errors.append("next_required_action_tampered")
    if r.get("current_loop_stage") != CURRENT_LOOP_STAGE:
        errors.append("current_loop_stage_tampered")
    for key, want in (("human_review_required", True),
                      ("paper_trading_gate_locked", True),
                      ("micro_live_gate_locked", True),
                      ("live_gate_locked", True),
                      ("is_labels_review_only", True),
                      ("is_a_rescue_attempt", False)):
        if r.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("edit_token_applied_by_this_gate",
                "rejection_decision_made_by_this_gate",
                "promotion_decision_made_by_this_gate",
                "replay_authorized_by_this_gate",
                "relabel_authorized_by_this_gate"):
        if r.get(key) is not False:
            errors.append("downstream_lock_wrong:" + key)
    for key in ("executes", "writes_files", "labels_now",
                "runs_real_candle_detection",
                "runs_relabel", "runs_replay",
                "runs_real_detection_now", "runs_replay_now",
                "scores_now", "stages_data_now", "fetches_data",
                "calls_api", "uses_network", "uses_credentials",
                "uses_wallet", "uses_account", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic",
                "contains_portfolio_allocation_logic",
                "starts_scheduler", "sends_notifications",
                "auto_commits", "auto_pushes", "creates_runners_now",
                "creates_data_artifacts_now",
                "creates_detector_implementation_now",
                "computes_pnl_now",
                "modifies_canonical_source",
                "modifies_detector_labels_artifacts",
                "modifies_coverage_blocker",
                "authorizes_paper_execution", "authorizes_micro_live",
                "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate",
                "unlocks_real_candle_detection",
                "unlocks_replay_now", "unlocks_relabel_now",
                "unlocks_edit_token_now", "claims_profitability"):
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)
    if r.get("verdict") == VERDICT_C10L_FROZEN and r.get("failures"):
        errors.append("frozen_with_failures")
    return {"valid": not errors, "errors": errors}

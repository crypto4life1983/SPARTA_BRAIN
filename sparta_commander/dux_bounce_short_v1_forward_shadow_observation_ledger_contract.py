"""Dux Bounce Short V1 -- MANUAL FORWARD-SHADOW CASE-SERIES LEDGER (PURE, SPEC + TEMPLATE ONLY).

Human-approved build token:
HUMAN_APPROVED_BUILD_DUX_FORWARD_SHADOW_LEDGER_WITH_INTEGRITY_AMENDMENTS.

Classification: MANUAL_FORWARD_SHADOW_CASE_SERIES_ONLY.

This module specifies a forward-only, MANUALLY entered shadow observation ledger for the one
committed research branch DIRECT_PREMARKET_GAP_INTO_PRIOR_HIGH_VOLUME_RESISTANCE. It provides an
in-code schema, two blank-record factories (observation + daily review), and integrity
validators. It performs NO I/O: it fetches no market data, subscribes to no provider, runs no
scanner/backtest/replay/labels, places no paper or live order, connects to no broker, and
creates no candidate. The only conclusion this path may ever support is
SIGNAL_DIAGNOSTIC_ONLY_NOT_TRADABLE.

HONEST INTEGRITY LIMITATIONS (documented, not overstated):
  * The entry-snapshot hash is an integrity GUARD, not cryptographic proof against a person who
    deliberately rewrites the entire ledger and recomputes every hash.
  * An in-memory validator cannot prove that the final record -- or an entire historical ledger
    version -- was never deleted. See DELETION_LIMITATION. An external checkpoint could support
    that later; no persistence mechanism is approved now.
"""
from __future__ import annotations

import copy
import hashlib
import json
from datetime import datetime
from typing import Any

SCHEMA_VERSION = 1
MODE = "RESEARCH_ONLY"
CLASSIFICATION = "MANUAL_FORWARD_SHADOW_CASE_SERIES_ONLY"
SELECTED_BRANCH = "DIRECT_PREMARKET_GAP_INTO_PRIOR_HIGH_VOLUME_RESISTANCE"
PERMITTED_CONCLUSION = "SIGNAL_DIAGNOSTIC_ONLY_NOT_TRADABLE"
APPROVAL_TOKEN = "HUMAN_APPROVED_BUILD_DUX_FORWARD_SHADOW_LEDGER_WITH_INTEGRITY_AMENDMENTS"

MARKET_TZ_DEFAULT = "America/New_York"  # planning default, NOT a silently universal assumption
DUX_FLOAT_FILTER_NOT_YET_VALIDATED = "DUX_FLOAT_FILTER_NOT_YET_VALIDATED"
WITHIN_BAR_VAP_NOTE = (
    "Within-bar volume-at-price is not known; resistance-band volume is an approximation only.")

DELETION_LIMITATION = (
    "DELETION_OUTSIDE_THE_SUPPLIED_CHAIN_CANNOT_BE_PROVEN_WITHOUT_AN_EXTERNAL_CHECKPOINT")

PROHIBITED_CHARACTERIZATIONS = (
    "unbiased_universe_sample", "statistical_proof", "validated_edge", "backtest",
    "paper_trading", "executable_evidence")

# --- lifecycle status (record state) vs outcome label (result) -- kept strictly separate -----
LIFECYCLE_STATUSES = ("OPEN", "COMPLETED", "DISQUALIFIED_BEFORE_ENTRY",
                      "INVALIDATED_AFTER_ENTRY", "DATA_INCOMPLETE")
OUTCOME_LABELS = ("POSITIVE_SHORT_RETURN", "NEGATIVE_SHORT_RETURN", "FLAT",
                  "NOT_APPLICABLE", "UNKNOWN")
STATUSES_ALLOWING_OUTCOME_METRICS = ("COMPLETED", "INVALIDATED_AFTER_ENTRY")
PERMITTED_STATUS_TRANSITIONS = {
    "OPEN": {"COMPLETED", "DISQUALIFIED_BEFORE_ENTRY", "INVALIDATED_AFTER_ENTRY",
             "DATA_INCOMPLETE"},
    "DATA_INCOMPLETE": {"COMPLETED", "DISQUALIFIED_BEFORE_ENTRY", "INVALIDATED_AFTER_ENTRY",
                        "DATA_INCOMPLETE"},
    "COMPLETED": set(),
    "DISQUALIFIED_BEFORE_ENTRY": set(),
    "INVALIDATED_AFTER_ENTRY": set(),
}

# --- outcome definitions (explicit units + formulas; never mix pct / price / $ / R) -----------
SHORT_RETURN_FORMULA = (
    "short_return_pct = (hypothetical_entry_price - reference_exit_price) "
    "/ hypothetical_entry_price * 100")
MAE_DEFINITION = (
    "max_adverse_excursion_pct = (max_high_price_in_window - hypothetical_entry_price) "
    "/ hypothetical_entry_price * 100; adverse for a SHORT is price moving up; "
    "positive value = adverse.")
MFE_DEFINITION = (
    "max_favourable_excursion_pct = (hypothetical_entry_price - min_low_price_in_window) "
    "/ hypothetical_entry_price * 100; favourable for a SHORT is price moving down; "
    "positive value = favourable.")

OUTCOME_METRIC_FIELDS = ("max_adverse_excursion_pct", "max_favourable_excursion_pct",
                         "open_to_close_short_return_pct", "next_session_short_return_pct",
                         "three_session_short_return_pct")
OUTCOME_ALL_FIELDS = OUTCOME_METRIC_FIELDS + (
    "outcome_window_start_utc", "outcome_window_end_utc", "outcome_data_source",
    "outcome_calculation_version", "outcome_recorded_at_utc", "post_outcome_chart_ref",
    "outcome_label")

# provenance sub-record keys, applied to each separately-sourced external fact
PROVENANCE_KEYS = ("source_name", "source_timestamp", "source_reference",
                   "manually_estimated", "missing", "uncertainty_reason")
PROVENANCE_FACTS = ("historical_resistance_estimate", "historical_volume_estimate",
                    "shares_outstanding", "free_float", "corporate_action", "halt_status",
                    "ssr_status", "borrow_locate")

TRACKED_COUNTERS = ("total_registered_observations", "completed_observations",
                    "disqualified_observations", "invalidated_observations",
                    "incomplete_observations", "open_observations",
                    "positive_short_return_observations", "negative_short_return_observations",
                    "daily_reviews_completed", "daily_reviews_missing_or_incomplete")

_CAPABILITY_FLAGS_FALSE = (
    "is_candidate", "creates_candidate", "assigns_candidate_number", "auto_market_data_fetch",
    "provider_subscription", "runs_scanner", "runs_backtest", "runs_replay", "creates_labels",
    "paper_trades", "live_trades", "connects_broker", "requests_locates", "purchases_locates",
    "auto_commits", "auto_pushes", "reports_profitability", "reports_tradability",
    "is_statistical_proof", "is_validated_edge", "is_backtest", "is_unbiased_universe_sample",
    "claims_unbiased_sample", "claims_complete_market_coverage", "computes_portfolio_returns",
    "computes_account_pnl", "sizes_positions", "recommends_live_trade", "authorizes_next_stage",
    "borrow_controls_retention")


# ---------------------------------------------------------------------------------------------
# hashing helpers
# ---------------------------------------------------------------------------------------------
def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _blank_provenance() -> dict[str, Any]:
    return {fact: {k: None for k in PROVENANCE_KEYS} for fact in PROVENANCE_FACTS}


# entry-time fields covered by the immutable entry snapshot (outcome + chain fields excluded)
ENTRY_SNAPSHOT_FIELDS = (
    "observation_id", "selected_branch", "signal_recorded_at_utc",
    "hypothetical_entry_timestamp_utc", "signal_information_cutoff_utc", "market_timezone",
    "observation_date", "observation_timestamp", "ticker", "exchange", "sector", "issuer_country",
    "current_price", "premarket_gap_pct", "original_spike_date", "sessions_since_original_spike",
    "resistance_band_lower", "resistance_band_upper", "approx_historical_volume_in_band",
    "approximation_method", "approximation_method_version", "vap_source_bars_or_chart_ref",
    "within_bar_vap_note", "vap_exactness", "resistance_band_selected_before_outcome",
    "band_volume_is_full_spike_day_total", "original_spike_total_volume", "premarket_volume",
    "premarket_volume_as_of_time", "point_in_time_shares_outstanding", "free_float",
    "float_status_label", "shares_float_source", "shares_float_source_timestamp", "split_flag",
    "reverse_split_flag", "dilution_flag", "halt_status", "ssr_status", "borrow_locate_status",
    "hypothetical_entry_price", "hypothetical_invalidation_stop", "intended_target",
    "uncertainty_flags", "pre_outcome_chart_ref", "provenance")


def compute_entry_snapshot(obs: dict[str, Any]) -> dict[str, Any]:
    """The subset of fields frozen at registration time."""
    return {k: obs.get(k) for k in ENTRY_SNAPSHOT_FIELDS}


def compute_entry_snapshot_hash(obs: dict[str, Any]) -> str:
    return _sha256(_canonical(compute_entry_snapshot(obs)))


def stamp_entry_snapshot(obs: dict[str, Any], version: str = "v1") -> dict[str, Any]:
    """Return a copy with entry_snapshot_version + entry_snapshot_hash set (neither is inside the
    snapshot, so stamping does not alter the hash it records)."""
    out = copy.deepcopy(obs)
    out["entry_snapshot_version"] = version
    out["entry_snapshot_hash"] = compute_entry_snapshot_hash(out)
    return out


def compute_record_hash(obs: dict[str, Any]) -> str:
    content = {k: v for k, v in obs.items() if k != "record_hash"}
    return _sha256(_canonical(content))


# ---------------------------------------------------------------------------------------------
# record factories
# ---------------------------------------------------------------------------------------------
def new_observation_record() -> dict[str, Any]:
    """A blank observation. Outcome fields are None; float label defaults to the not-validated
    marker; VAP exactness is locked APPROXIMATE; status is OPEN."""
    return {
        # meta / chain / audit
        "observation_id": None, "selected_branch": SELECTED_BRANCH, "status": "OPEN",
        "sequence_number": None, "previous_record_hash": None, "record_hash": None,
        "recorded_at_utc": None, "signal_recorded_at_utc": None,
        "hypothetical_entry_timestamp_utc": None, "signal_information_cutoff_utc": None,
        "market_timezone": MARKET_TZ_DEFAULT,
        "entry_snapshot_version": None, "entry_snapshot_hash": None,
        # instrument identity + entry-time inputs
        "observation_date": None, "observation_timestamp": None, "ticker": None, "exchange": None,
        "sector": None, "issuer_country": None, "current_price": None, "premarket_gap_pct": None,
        "original_spike_date": None, "sessions_since_original_spike": None,
        "resistance_band_lower": None, "resistance_band_upper": None,
        "approx_historical_volume_in_band": None, "approximation_method": None,
        "approximation_method_version": None, "vap_source_bars_or_chart_ref": None,
        "within_bar_vap_note": WITHIN_BAR_VAP_NOTE, "vap_exactness": "APPROXIMATE",
        "resistance_band_selected_before_outcome": True,
        "band_volume_is_full_spike_day_total": False,
        "original_spike_total_volume": None, "premarket_volume": None,
        "premarket_volume_as_of_time": None, "point_in_time_shares_outstanding": None,
        "free_float": None, "float_status_label": DUX_FLOAT_FILTER_NOT_YET_VALIDATED,
        "shares_float_source": None, "shares_float_source_timestamp": None,
        "split_flag": None, "reverse_split_flag": None, "dilution_flag": None,
        "halt_status": None, "ssr_status": None, "borrow_locate_status": None,
        "hypothetical_entry_price": None, "hypothetical_invalidation_stop": None,
        "intended_target": None, "uncertainty_flags": None, "pre_outcome_chart_ref": None,
        "provenance": _blank_provenance(),
        # outcomes -- MUST stay None until the observation is already registered
        "outcome_label": None, "max_adverse_excursion_pct": None,
        "max_favourable_excursion_pct": None, "open_to_close_short_return_pct": None,
        "next_session_short_return_pct": None, "three_session_short_return_pct": None,
        "outcome_window_start_utc": None, "outcome_window_end_utc": None,
        "outcome_data_source": None, "outcome_calculation_version": None,
        "outcome_recorded_at_utc": None, "post_outcome_chart_ref": None,
    }


def new_daily_review_record() -> dict[str, Any]:
    """A blank daily-review record. Every reviewed market day -- including no-candidate days --
    should be represented so a comprehensiveness claim is only possible with full coverage."""
    return {
        "review_id": None, "market_date": None, "market_timezone": MARKET_TZ_DEFAULT,
        "review_started_at_utc": None, "review_completed_at_utc": None,
        "discovery_process_version": None, "reviewed_universe_description": None,
        "reviewed_sources": None, "review_completed": False, "candidate_count": 0,
        "candidate_observation_ids": [], "no_candidate_found": False,
        "incomplete_review_reason": None,
        "all_identified_candidates_recorded_attestation": False,
    }


# ---------------------------------------------------------------------------------------------
# timestamp helpers
# ---------------------------------------------------------------------------------------------
def _dt(v: Any):
    if not isinstance(v, str):
        return None
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return "ERR"


def _utc(name: str, v: Any, f: list):
    if v is None:
        return None
    d = _dt(v)
    if d == "ERR" or d is None:
        f.append("bad_timestamp:%s" % name)
        return None
    if d.tzinfo is None:
        f.append("timestamp_not_tz_aware:%s" % name)
        return None
    return d


# ---------------------------------------------------------------------------------------------
# validators
# ---------------------------------------------------------------------------------------------
def validate_observation(obs: Any) -> dict[str, Any]:
    """Per-record integrity: schema completeness, record-before-entry ordering, information
    cutoff, no-outcome-at-registration, entry-snapshot immutability, float/VAP/branch rules, and
    status/outcome separation."""
    f: list = []
    if not isinstance(obs, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    for k in new_observation_record():
        if k not in obs:
            f.append("missing_field:%s" % k)
    if f:
        return {"valid": False, "failures": f}

    if obs["selected_branch"] != SELECTED_BRANCH:
        f.append("selected_branch_changed")
    if obs["status"] not in LIFECYCLE_STATUSES:
        f.append("invalid_status")
    if obs["vap_exactness"] != "APPROXIMATE":
        f.append("vap_exactness_must_be_approximate")
    if obs["free_float"] is None and obs["float_status_label"] != DUX_FLOAT_FILTER_NOT_YET_VALIDATED:
        f.append("missing_float_requires_not_validated_label")
    if obs["resistance_band_selected_before_outcome"] is not True:
        f.append("resistance_band_must_be_selected_before_outcome")
    if obs["band_volume_is_full_spike_day_total"] is not False:
        f.append("spike_day_total_may_not_substitute_for_band_volume")
    if obs["approx_historical_volume_in_band"] is not None:
        for req in ("approximation_method", "approximation_method_version",
                    "resistance_band_lower", "resistance_band_upper",
                    "vap_source_bars_or_chart_ref", "within_bar_vap_note"):
            if not obs.get(req):
                f.append("approx_vap_missing:%s" % req)

    # outcome label domain + status/label separation
    if obs["outcome_label"] is not None and obs["outcome_label"] not in OUTCOME_LABELS:
        f.append("invalid_outcome_label")
    metrics_present = any(obs[m] is not None for m in OUTCOME_METRIC_FIELDS)
    if obs["status"] == "OPEN":
        for k in OUTCOME_ALL_FIELDS:
            if obs[k] is not None:
                f.append("outcome_field_set_while_open:%s" % k)
    if metrics_present:
        if obs["status"] not in STATUSES_ALLOWING_OUTCOME_METRICS:
            f.append("outcome_metrics_require_completed_or_invalidated_after_entry")
        if obs["outcome_recorded_at_utc"] is None:
            f.append("outcome_metrics_require_outcome_recorded_at")
        if obs["entry_snapshot_hash"] is None:
            f.append("outcome_requires_prior_entry_snapshot")

    # entry-snapshot immutability (integrity guard, not cryptographic proof)
    if obs["entry_snapshot_hash"] is not None:
        if obs["entry_snapshot_hash"] != compute_entry_snapshot_hash(obs):
            f.append("entry_snapshot_hash_mismatch_entry_field_changed")

    # timestamp ordering / tz-awareness
    sr = _utc("signal_recorded_at_utc", obs["signal_recorded_at_utc"], f)
    he = _utc("hypothetical_entry_timestamp_utc", obs["hypothetical_entry_timestamp_utc"], f)
    cut = _utc("signal_information_cutoff_utc", obs["signal_information_cutoff_utc"], f)
    orc = _utc("outcome_recorded_at_utc", obs["outcome_recorded_at_utc"], f)
    if sr and he and sr > he:
        f.append("registration_after_hypothetical_entry")
    if cut and he and cut > he:
        f.append("information_cutoff_after_hypothetical_entry")
    if orc and sr and orc < sr:
        f.append("outcome_recorded_before_registration")
    return {"valid": not f, "failures": f}


def validate_status_transition(old: str, new: str) -> bool:
    return new in PERMITTED_STATUS_TRANSITIONS.get(old, set())


def validate_daily_review(dr: Any) -> dict[str, Any]:
    f: list = []
    if not isinstance(dr, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    for k in new_daily_review_record():
        if k not in dr:
            f.append("missing_field:%s" % k)
    if f:
        return {"valid": False, "failures": f}
    ids = dr["candidate_observation_ids"]
    if not isinstance(ids, list):
        f.append("candidate_observation_ids_not_a_list")
        ids = []
    if dr["candidate_count"] != len(ids):
        f.append("candidate_count_must_equal_referenced_ids")
    if dr["no_candidate_found"] is True and dr["candidate_count"] != 0:
        f.append("no_candidate_found_requires_zero_count")
    if dr["review_completed"] is True and dr["candidate_count"] == 0 and dr["no_candidate_found"] is not True:
        f.append("completed_zero_candidate_review_must_set_no_candidate_found")
    if dr["review_completed"] is not True:
        if dr["all_identified_candidates_recorded_attestation"] is not False:
            f.append("incomplete_review_cannot_attest_all_candidates_recorded")
        if not dr["incomplete_review_reason"]:
            f.append("incomplete_review_requires_reason")
    return {"valid": not f, "failures": f}


def build_ledger(observations, daily_reviews=None) -> dict[str, Any]:
    """Chain a list of observations into an append-only ledger, stamping entry snapshots where
    absent and computing sequence numbers + hash links. Pure; no persistence."""
    obs: list = []
    prev = "GENESIS"
    for i, o in enumerate(observations, start=1):
        r = copy.deepcopy(o)
        if r.get("entry_snapshot_hash") is None:
            r = stamp_entry_snapshot(r)
        r["sequence_number"] = i
        r["previous_record_hash"] = prev
        r.pop("record_hash", None)
        r["record_hash"] = compute_record_hash(r)
        prev = r["record_hash"]
        obs.append(r)
    return {
        "observations": obs,
        "declared_record_count": len(obs),
        "first_record_hash": obs[0]["record_hash"] if obs else None,
        "last_record_hash": obs[-1]["record_hash"] if obs else None,
        "daily_reviews": list(daily_reviews or []),
        "deletion_limitation": DELETION_LIMITATION,
    }


def validate_ledger(ledger: Any) -> dict[str, Any]:
    """Detects duplicate IDs / sequence numbers, sequence gaps, reordering, broken hash links,
    record-count mismatch and first/last hash mismatch. Explicitly CANNOT prove that the final
    record or a whole historical ledger version was never deleted -- see DELETION_LIMITATION."""
    f: list = []
    if not isinstance(ledger, dict):
        return {"valid": False, "failures": ["ledger_not_a_dict"],
                "limitations": [DELETION_LIMITATION]}
    obs = ledger.get("observations")
    if not isinstance(obs, list):
        return {"valid": False, "failures": ["observations_not_a_list"],
                "limitations": [DELETION_LIMITATION]}
    n = len(obs)
    if ledger.get("declared_record_count") != n:
        f.append("declared_record_count_mismatch")
    ids = [o.get("observation_id") for o in obs]
    if len(set(ids)) != len(ids):
        f.append("duplicate_observation_ids")
    seqs = [o.get("sequence_number") for o in obs]
    if seqs != list(range(1, n + 1)):
        f.append("sequence_gap_duplicate_or_reordered")
    for i, o in enumerate(obs):
        expected_prev = "GENESIS" if i == 0 else obs[i - 1].get("record_hash")
        if o.get("previous_record_hash") != expected_prev:
            f.append("broken_hash_link_at_index:%d" % i)
        if o.get("record_hash") != compute_record_hash(o):
            f.append("record_hash_mismatch_at_index:%d" % i)
        ov = validate_observation(o)
        if not ov["valid"]:
            f.append("observation_invalid_at_index:%d:%s" % (i, ",".join(ov["failures"])))
    if n:
        if ledger.get("first_record_hash") != obs[0].get("record_hash"):
            f.append("first_record_hash_mismatch")
        if ledger.get("last_record_hash") != obs[-1].get("record_hash"):
            f.append("last_record_hash_mismatch")
    return {"valid": not f, "failures": f, "limitations": [DELETION_LIMITATION]}


def ledger_stats(ledger: dict[str, Any]) -> dict[str, Any]:
    obs = ledger.get("observations", [])
    drs = ledger.get("daily_reviews", [])

    def cnt(s):
        return sum(1 for o in obs if o.get("status") == s)

    def lbl(l):
        return sum(1 for o in obs if o.get("outcome_label") == l)

    dr_ok = sum(1 for d in drs
                if d.get("review_completed") is True and validate_daily_review(d)["valid"])
    return {
        "total_registered_observations": len(obs),
        "completed_observations": cnt("COMPLETED"),
        "disqualified_observations": cnt("DISQUALIFIED_BEFORE_ENTRY"),
        "invalidated_observations": cnt("INVALIDATED_AFTER_ENTRY"),
        "incomplete_observations": cnt("DATA_INCOMPLETE"),
        "open_observations": cnt("OPEN"),
        "positive_short_return_observations": lbl("POSITIVE_SHORT_RETURN"),
        "negative_short_return_observations": lbl("NEGATIVE_SHORT_RETURN"),
        "daily_reviews_completed": dr_ok,
        "daily_reviews_missing_or_incomplete": len(drs) - dr_ok,
    }


def can_claim_comprehensive(ledger: dict[str, Any]) -> dict[str, Any]:
    """A comprehensive-sample claim is only supported when every daily review is present, valid,
    completed and attested. Missing coverage => not comprehensive."""
    drs = ledger.get("daily_reviews", [])
    if not drs:
        return {"comprehensive_claim_supported": False, "reason": "no_daily_reviews"}
    for d in drs:
        if not validate_daily_review(d)["valid"]:
            return {"comprehensive_claim_supported": False, "reason": "invalid_daily_review"}
        if d.get("review_completed") is not True \
                or d.get("all_identified_candidates_recorded_attestation") is not True:
            return {"comprehensive_claim_supported": False,
                    "reason": "incomplete_daily_review_coverage"}
    return {"comprehensive_claim_supported": True,
            "reason": "all_daily_reviews_complete_and_attested"}


def build_observation_ledger_spec() -> dict[str, Any]:
    """PURE. Assemble the forward-shadow case-series specification. Approves nothing."""
    rec: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION, "mode": MODE, "classification": CLASSIFICATION,
        "approved_via": APPROVAL_TOKEN, "selected_branch": SELECTED_BRANCH,
        "permitted_conclusion": PERMITTED_CONCLUSION,
        "prohibited_characterizations": list(PROHIBITED_CHARACTERIZATIONS),
        "observation_schema_fields": sorted(new_observation_record().keys()),
        "daily_review_schema_fields": sorted(new_daily_review_record().keys()),
        "entry_snapshot_fields": list(ENTRY_SNAPSHOT_FIELDS),
        "outcome_fields": list(OUTCOME_ALL_FIELDS),
        "provenance_facts": list(PROVENANCE_FACTS), "provenance_keys": list(PROVENANCE_KEYS),
        "lifecycle_statuses": list(LIFECYCLE_STATUSES), "outcome_labels": list(OUTCOME_LABELS),
        "permitted_status_transitions": {k: sorted(v)
                                         for k, v in PERMITTED_STATUS_TRANSITIONS.items()},
        "short_return_formula": SHORT_RETURN_FORMULA, "mae_definition": MAE_DEFINITION,
        "mfe_definition": MFE_DEFINITION,
        "outcome_units": {m: "percent" for m in OUTCOME_METRIC_FIELDS},
        "float_absent_label": DUX_FLOAT_FILTER_NOT_YET_VALIDATED,
        "vap_exactness_locked": "APPROXIMATE", "within_bar_vap_note": WITHIN_BAR_VAP_NOTE,
        "checkpoint_at_completed_observations": 20,
        "checkpoint_label": "RULE_LEARNING_CHECKPOINT_NOT_STATISTICAL_PROOF",
        "checkpoint_is_statistical_proof": False, "tracked_counters": list(TRACKED_COUNTERS),
        "records_removable_when_losing_or_incomplete": False,
        "market_timezone_default": MARKET_TZ_DEFAULT,
        "deletion_limitation": DELETION_LIMITATION,
        "honest_limitations": {
            "entry_snapshot": ("Integrity guard, not cryptographic proof against a person "
                               "deliberately rewriting the entire ledger and recomputing every "
                               "hash."),
            "deletion": DELETION_LIMITATION,
            "manual_completeness": ("Comprehensiveness depends on complete manual daily-review "
                                    "coverage; missing daily reviews mean the case series is NOT "
                                    "comprehensive."),
        },
        "checkpoint_permissions": {
            "promotes_candidate": False, "approves_data_purchase": False,
            "authorizes_scanner": False, "authorizes_paper_or_live_trading": False,
            "reports_profitability": False,
        },
        "advances_nothing": True, "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        rec[flag] = False
    rec["scope_locks"] = {
        "no_market_data_fetch": True, "no_provider_subscription": True, "no_scanner": True,
        "no_candidate": True, "no_backtest": True, "no_replay": True, "no_labels": True,
        "no_paper_trades": True, "no_live_trades": True, "no_broker": True,
        "no_locate_request": True, "no_position_sizing": True, "no_pnl_computation": True,
        "no_unbiased_sample_claim": True, "no_complete_coverage_claim": True,
        "no_removal_of_losing_or_incomplete_records": True, "no_borrow_gated_retention": True,
        "no_exact_vap_claim": True, "no_next_stage_authorization": True,
        "no_auto_commit": True, "no_auto_push": True,
    }
    return rec


def validate_observation_ledger_spec(record: Any) -> dict[str, Any]:
    """Anti-tamper validator for the spec: pins classification/branch/conclusion, checkpoint
    (learning-only), locked VAP + float label, borrow-not-gating, non-removability, deletion
    limitation, short-return formula, prohibited characterizations, and all-False flags."""
    f: list = []
    if not isinstance(record, dict):
        return {"valid": False, "failures": ["record_not_a_dict"]}
    r = record
    if r.get("mode") != MODE:
        f.append("mode_not_research_only")
    if r.get("classification") != CLASSIFICATION:
        f.append("classification_wrong")
    if r.get("selected_branch") != SELECTED_BRANCH:
        f.append("selected_branch_changed")
    if r.get("permitted_conclusion") != PERMITTED_CONCLUSION:
        f.append("permitted_conclusion_wrong")
    for pc in PROHIBITED_CHARACTERIZATIONS:
        if pc not in (r.get("prohibited_characterizations") or []):
            f.append("missing_prohibited_characterization:%s" % pc)
    if r.get("checkpoint_at_completed_observations") != 20:
        f.append("checkpoint_threshold_wrong")
    if r.get("checkpoint_label") != "RULE_LEARNING_CHECKPOINT_NOT_STATISTICAL_PROOF":
        f.append("checkpoint_label_wrong")
    if r.get("checkpoint_is_statistical_proof") is not False:
        f.append("checkpoint_must_not_be_statistical_proof")
    if r.get("vap_exactness_locked") != "APPROXIMATE":
        f.append("vap_must_be_locked_approximate")
    if r.get("float_absent_label") != DUX_FLOAT_FILTER_NOT_YET_VALIDATED:
        f.append("float_absent_label_wrong")
    if r.get("records_removable_when_losing_or_incomplete") is not False:
        f.append("records_must_not_be_removable")
    if r.get("deletion_limitation") != DELETION_LIMITATION:
        f.append("deletion_limitation_missing")
    if r.get("short_return_formula") != SHORT_RETURN_FORMULA:
        f.append("short_return_formula_changed")
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            f.append("capability_flag_true:%s" % flag)
    if r.get("advances_nothing") is not True:
        f.append("must_advance_nothing")
    return {"valid": not f, "failures": f}

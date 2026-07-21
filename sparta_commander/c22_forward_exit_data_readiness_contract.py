"""Candidate #22 -- FORWARD EXIT-ONLY DATA READINESS CONTRACT
(Phase B1: CONTRACT + PLANNING ONLY, PURE, ADDITIVE, RESEARCH-ONLY).

Human-approved build token (Phase B1 only):
HUMAN_APPROVED_BUILD_C22_FORWARD_AND_EXECUTION_DATA_READINESS_PHASE_B1.

Freezes the EXACT forward Trend-Radar snapshot dataset required to evaluate EXITS after the
frozen entry cutoff, plus the deterministic horizon/extension math and the classification a
read-only inventory uses. It ADMITS NOTHING, FETCHES NOTHING, MUTATES NOTHING, and RUNS NO
replay/simulation. Bound to the accepted REV1 replay specification (SHA
9bf10af353521738f440c2e953af44cdd5ed093590f03a843a01972485dd9867) whose rules it single-sources.

Preserves the REV1 five-case distinction: absent-from-valid-top-50 -> OUT_OF_RADAR; entire
expected export missing/malformed -> fail-closed halt; temporary suspension -> hold+flag;
permanent delisting with a real executable price -> separately flagged diagnostic exit; no
executable price -> fail-closed halt. Every capability flag is pinned False; suggestion-only.
"""
from __future__ import annotations

import hashlib as _hashlib
import json as _json
from datetime import date as _date, timedelta as _timedelta
from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_replay_spec_contract as _spec  # noqa: E501
import sparta_commander.c22_signum_gc_data_collection_tracker_contract as _trk

FED_SCHEMA_VERSION = 1
FED_MODE = "RESEARCH_ONLY"
FED_LANE = "crypto_d1_auto_research"
BUILDER_VERSION = "forward_exit_data_readiness_b1_v1"
PHASE_B1_BUILD_TOKEN = "HUMAN_APPROVED_BUILD_C22_FORWARD_AND_EXECUTION_DATA_READINESS_PHASE_B1"
BOUND_SPEC_SHA256 = "9bf10af353521738f440c2e953af44cdd5ed093590f03a843a01972485dd9867"

VERDICT_READY = "C22_FORWARD_EXIT_DATA_CONTRACT_READY_FOR_HUMAN_REVIEW"
VERDICT_BLOCKED = "C22_FORWARD_EXIT_DATA_CONTRACT_BLOCKED"
BLOCKED_INSUFFICIENT_FORWARD = "BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA"

# --- frozen cutoff / horizon (single-sourced from the accepted REV1 spec) --------------------
ENTRY_CUTOFF = _spec.FROZEN_END                                   # 2026-07-15
FIRST_EXIT_ONLY_DATE = "2026-07-16"
INITIAL_REVIEW_CALENDAR_DAYS = _spec.INITIAL_FORWARD_REVIEW_CALENDAR_DAYS      # 30
EXTENSION_INCREMENT_CALENDAR_DAYS = _spec.FORWARD_EXTENSION_INCREMENT_CALENDAR_DAYS  # 15
EXIT_ONLY_MARKER = "EXIT_ONLY"
EXPORT_PREFIX = _trk.EXPORT_PREFIX                                # gc_crypto_trendradar_daily
DATA_DIR = _trk.DATA_DIR

# required per-snapshot fields the forward dataset must carry
REQUIRED_SNAPSHOT_FIELDS = (
    "runDate", "asset_identifier", "market_rank", "top50_membership",
    "gc.upper", "gc.filter", "gc.trend", "ohlc.h", "ohlc.c",
    "source_filename", "source_sha256", "row_count", "validation_status",
    "provenance_tier_or_source_class", "exit_only_admission_marker")

# expected-session handling (single-sourced from committed collection/export cadence)
EXPECTED_SESSION_RULES = {
    "weekend_non_export": "Saturday/Sunday and legitimate non-export dates have NO session; "
                          "an open position simply carries (no exit decision)",
    "missing_expected_weekday_export": "an expected weekday export that is absent -> "
                                       "MISSING_EXPECTED_EXPORT; on a HOLDING session this is a "
                                       "fail-closed halt (never a silent exit)",
    "malformed_export": "structurally invalid export on an expected session -> fail-closed halt",
    "duplicate_runDate": "two exports for one runDate -> DUPLICATE (rejected, never merged)",
    "duplicate_asset_rows": "duplicate (asset,runDate) rows -> rejected, never merged",
    "inconsistent_symbol_mapping": "asset<->symbol not deterministically mappable -> fail-closed",
    "incomplete_top50": "export present but < 50 valid ranked rows -> INVALID (fail-closed on a "
                        "holding session)",
    "asset_absent_from_valid_export": "asset not in a VALID top-50 export -> OUT_OF_RADAR exit",
    "entire_export_missing": "the whole expected export absent -> fail-closed halt",
}

# REV1 five-case distinction (preserved verbatim in spirit; single-sourced references)
REV1_FIVE_CASE_DISTINCTION = {
    "absent_from_valid_top50": "OUT_OF_RADAR",
    "entire_export_missing_or_malformed": "FAIL_CLOSED_HALT",
    "temporary_suspension": "HOLD_AND_FLAG",
    "permanent_delisting_with_real_price": "DELISTED_EXIT_DIAGNOSTIC",
    "no_executable_price": "FAIL_CLOSED_HALT",
}

# inventory classification (a report may assign; NONE of these is an admission)
INVENTORY_CLASSES = (
    "PRESENT_BUT_NOT_ADMITTED", "VALID_EXIT_ONLY_CANDIDATE", "INVALID", "DUPLICATE",
    "OUTSIDE_REQUIRED_RANGE", "MISSING_EXPECTED_EXPORT")

# administrative-liquidation status (non-decisive; single-sourced posture)
ADMIN_LIQUIDATION = {
    "non_decisive": True,
    "excluded_from_return_sharpe_calmar_benchmarks": True,
    "permitted_only_as_truncation_diagnostic": True,
}


def _iso(d: _date) -> str:
    return d.isoformat()


def _daterange_inclusive(start_iso: str, end_iso: str) -> list:
    s = _date.fromisoformat(start_iso); e = _date.fromisoformat(end_iso)
    out = []
    cur = s
    while cur <= e:
        out.append(_iso(cur)); cur += _timedelta(days=1)
    return out


def initial_exit_data_range() -> dict:
    """The initial exit-only calendar range [FIRST_EXIT_ONLY_DATE, +30 cal days)."""
    start = _date.fromisoformat(FIRST_EXIT_ONLY_DATE)
    end = start + _timedelta(days=INITIAL_REVIEW_CALENDAR_DAYS - 1)
    return {"start": FIRST_EXIT_ONLY_DATE, "end": _iso(end),
            "calendar_days": INITIAL_REVIEW_CALENDAR_DAYS}


def extension_range(n: int) -> dict:
    """The n-th (1-based) deterministic 15-calendar-day extension range after the initial
    horizon. Purely a function of n -- NOT of any observed position/economic result."""
    if n < 1:
        raise ValueError("extension index must be >= 1")
    init_end = _date.fromisoformat(initial_exit_data_range()["end"])
    start = init_end + _timedelta(days=1 + (n - 1) * EXTENSION_INCREMENT_CALENDAR_DAYS)
    end = start + _timedelta(days=EXTENSION_INCREMENT_CALENDAR_DAYS - 1)
    return {"index": n, "start": _iso(start), "end": _iso(end),
            "calendar_days": EXTENSION_INCREMENT_CALENDAR_DAYS}


def expected_export_sessions(start_iso: str, end_iso: str) -> list:
    """Deterministic expected EXPORT sessions in [start,end]: weekdays (Mon-Fri). Weekends are
    legitimate non-export dates. (Holiday/non-export exceptions are applied later against the
    committed calendar; this base rule is weekday cadence, never inferred from data.)"""
    sessions = []
    for iso in _daterange_inclusive(start_iso, end_iso):
        if _date.fromisoformat(iso).weekday() < 5:   # 0=Mon .. 4=Fri
            sessions.append(iso)
    return sessions


def classify_inventory_date(run_date: str, present: bool, structurally_valid: bool,
                            duplicate: bool, in_required_range: bool) -> str:
    """PURE classification for the read-only inventory. NEVER an admission. A present valid
    unique in-range post-cutoff snapshot is at most a VALID_EXIT_ONLY_CANDIDATE."""
    if not in_required_range:
        return "OUTSIDE_REQUIRED_RANGE"
    if duplicate:
        return "DUPLICATE"
    if not present:
        return "MISSING_EXPECTED_EXPORT"
    if not structurally_valid:
        return "INVALID"
    return "VALID_EXIT_ONLY_CANDIDATE"


def is_admissible_entry_date(run_date: str) -> bool:
    """Entries are permitted ONLY on/through the cutoff. Post-cutoff dates can NEVER create an
    entry (EXIT_ONLY). Used to hard-reject any attempt to use a forward snapshot for entry."""
    return run_date <= ENTRY_CUTOFF


def readiness_from_coverage(expected_sessions: list, present_valid_dates: set) -> dict:
    """PURE, FAILS CLOSED. Given the expected export sessions of a range and the set of
    present+valid dates, decide readiness. Missing any expected session -> not covered ->
    BLOCKED_BY_INSUFFICIENT_FORWARD_EXIT_PATH_DATA. Simulates NO positions."""
    missing = [d for d in expected_sessions if d not in present_valid_dates]
    covered = (len(missing) == 0)
    return {"expected_sessions": list(expected_sessions), "missing_sessions": missing,
            "covered": covered,
            "readiness": ("COVERAGE_COMPLETE_FOR_RANGE" if covered
                          else BLOCKED_INSUFFICIENT_FORWARD)}


_CAPABILITY_FLAGS_FALSE = (
    "network", "fetch", "import", "dataset_mutation", "forward_data_admission",
    "instrument_selection", "cost_base_case_approval", "replay", "simulation", "dry_run",
    "token_issuance", "token_consumption", "lifecycle_advancement", "commit", "push",
    "renames_files", "admits_any_snapshot", "changes_collection_state",
    "changes_entry_period", "generates_entry_after_cutoff",
)


def build_forward_exit_data_contract() -> dict:
    """PURE. Assemble the frozen forward exit-data readiness contract. Writes NOTHING."""
    blockers: list = []
    if ENTRY_CUTOFF != "2026-07-15":
        blockers.append("entry_cutoff_drift")
    if FIRST_EXIT_ONLY_DATE <= ENTRY_CUTOFF:
        blockers.append("first_exit_date_not_after_cutoff")
    if INITIAL_REVIEW_CALENDAR_DAYS != 30 or EXTENSION_INCREMENT_CALENDAR_DAYS != 15:
        blockers.append("horizon_constants_drift")
    if _spec.build_replay_spec()["spec_sha256"] != BOUND_SPEC_SHA256:
        blockers.append("bound_spec_sha_mismatch")

    contract: dict[str, Any] = {
        "contract": "c22_forward_exit_only_trend_radar_data_readiness",
        "schema_version": FED_SCHEMA_VERSION, "builder_version": BUILDER_VERSION,
        "mode": FED_MODE, "lane": FED_LANE, "candidate_id": _spec._v2._v1.CANDIDATE_ID,
        "phase": "B1_CONTRACT_AND_PLANNING_ONLY", "phase_b1_build_token": PHASE_B1_BUILD_TOKEN,
        "bound_replay_spec_sha256": BOUND_SPEC_SHA256,
        "entry_cutoff": ENTRY_CUTOFF, "first_exit_only_date": FIRST_EXIT_ONLY_DATE,
        "no_new_entries_after_cutoff": True,
        "post_cutoff_files_marked": EXIT_ONLY_MARKER,
        "post_cutoff_not_used_in_v2_labels_or_entries": True,
        "initial_review_calendar_days": INITIAL_REVIEW_CALENDAR_DAYS,
        "extension_increment_calendar_days": EXTENSION_INCREMENT_CALENDAR_DAYS,
        "extension_is_deterministic_not_outcome_driven": True,
        "required_snapshot_fields": list(REQUIRED_SNAPSHOT_FIELDS),
        "expected_session_rules": EXPECTED_SESSION_RULES,
        "rev1_five_case_distinction": REV1_FIVE_CASE_DISTINCTION,
        "inventory_classes": list(INVENTORY_CLASSES),
        "classification_never_admits": True,
        "administrative_liquidation": ADMIN_LIQUIDATION,
        "insufficient_data_outcome": BLOCKED_INSUFFICIENT_FORWARD,
        "initial_exit_data_range": initial_exit_data_range(),
        "first_extension_range": extension_range(1),
        "second_extension_range": extension_range(2),
        "export_prefix": EXPORT_PREFIX, "data_dir": DATA_DIR,
        "human_review_required": True,
        "verdict": (VERDICT_READY if not blockers else VERDICT_BLOCKED),
        "blockers": blockers,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        contract[flag] = False
    contract["contract_sha256"] = _hashlib.sha256(
        canonical_contract_bytes(contract)).hexdigest()
    return contract


def canonical_contract_bytes(contract: dict) -> bytes:
    payload = {k: v for k, v in contract.items() if k != "contract_sha256"}
    return _json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def validate_forward_exit_data_contract(c: Any) -> dict:
    """Anti-tamper validator. Valid only when research-only + B1 contract-only, bound to the
    accepted spec SHA, cutoff 2026-07-15, first-exit 2026-07-16, horizon 30/15 deterministic,
    the five-case distinction + all required fields present, classification never admits, admin
    liquidation non-decisive, and every capability flag False."""
    f: list = []
    if not isinstance(c, dict):
        return {"valid": False, "failures": ["contract_not_a_dict"]}
    if c.get("mode") != FED_MODE:
        f.append("mode_not_research_only")
    if c.get("phase") != "B1_CONTRACT_AND_PLANNING_ONLY":
        f.append("not_b1_contract_only")
    if c.get("bound_replay_spec_sha256") != BOUND_SPEC_SHA256:
        f.append("bound_spec_sha_wrong")
    if c.get("entry_cutoff") != "2026-07-15":
        f.append("entry_cutoff_wrong")
    if c.get("first_exit_only_date") != "2026-07-16":
        f.append("first_exit_date_wrong")
    if c.get("no_new_entries_after_cutoff") is not True:
        f.append("entries_after_cutoff_not_forbidden")
    if c.get("post_cutoff_files_marked") != "EXIT_ONLY":
        f.append("exit_only_marker_wrong")
    if c.get("initial_review_calendar_days") != 30 or \
            c.get("extension_increment_calendar_days") != 15:
        f.append("horizon_constants_wrong")
    if c.get("extension_is_deterministic_not_outcome_driven") is not True:
        f.append("extension_not_deterministic")
    for fld in REQUIRED_SNAPSHOT_FIELDS:
        if fld not in (c.get("required_snapshot_fields") or []):
            f.append("required_field_missing:%s" % fld)
    d = c.get("rev1_five_case_distinction") or {}
    if d.get("absent_from_valid_top50") != "OUT_OF_RADAR" or \
            d.get("entire_export_missing_or_malformed") != "FAIL_CLOSED_HALT" or \
            d.get("no_executable_price") != "FAIL_CLOSED_HALT" or \
            d.get("permanent_delisting_with_real_price") != "DELISTED_EXIT_DIAGNOSTIC" or \
            d.get("temporary_suspension") != "HOLD_AND_FLAG":
        f.append("five_case_distinction_wrong")
    if tuple(c.get("inventory_classes") or ()) != INVENTORY_CLASSES:
        f.append("inventory_classes_wrong")
    if c.get("classification_never_admits") is not True:
        f.append("classification_admits")
    al = c.get("administrative_liquidation") or {}
    if al.get("non_decisive") is not True or \
            al.get("excluded_from_return_sharpe_calmar_benchmarks") is not True:
        f.append("admin_liquidation_not_non_decisive")
    if c.get("insufficient_data_outcome") != BLOCKED_INSUFFICIENT_FORWARD:
        f.append("insufficient_outcome_wrong")
    for flag in _CAPABILITY_FLAGS_FALSE:
        if c.get(flag) is not False:
            f.append("capability_flag_true:%s" % flag)
    if c.get("contract_sha256") and c["contract_sha256"] != _hashlib.sha256(
            canonical_contract_bytes(c)).hexdigest():
        f.append("contract_hash_mismatch")
    if c.get("verdict") == VERDICT_READY and c.get("blockers"):
        f.append("ready_with_blockers")
    return {"valid": not f, "failures": f}

"""Candidate #22 -- HISTORICAL INSTRUMENT EVIDENCE ACQUISITION PLAN & SOURCE-FEASIBILITY REVIEW
(Phase B3: PLANNING + SOURCE-DEFINITION ONLY, PURE, ADDITIVE, RESEARCH-ONLY).

Human-approved build token (Phase B3 only):
HUMAN_APPROVED_BUILD_C22_HISTORICAL_EVIDENCE_ACQUISITION_PLAN_PHASE_B3.

Determines -- WITHOUT fetching, browsing, calling any API, using credentials, or selecting an
instrument -- whether the Phase-B2 requested evidence can realistically be acquired, from which
provider-NEUTRAL source classes, under what constraints, and with what validation. It defines a
strict source hierarchy, a full 22-asset feasibility matrix, acquisition groupings, credential/
safety classification, a proposed (uncreated) gitignored evidence layout, a fail-close-early
acquisition order, forward-horizon extension handling, and a proposed (inactive) authorization
sequence + tokens. Every capability flag is pinned False; suggestion-only.

Every externally unverified source assumption is marked REQUIRES_EXTERNAL_VERIFICATION.
Current-listing availability is NEVER used to infer historical instrument existence or borrow
availability. Bound to the accepted replay spec + Phase B1/B2 contracts by SHA.
"""
from __future__ import annotations

import hashlib as _hashlib
import json as _json
from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_replay_spec_contract as _spec  # noqa: E501
import sparta_commander.c22_forward_exit_data_readiness_contract as _fed
import sparta_commander.c22_short_instrument_evidence_request_contract as _er

AP_SCHEMA_VERSION = 1
AP_MODE = "RESEARCH_ONLY"
AP_LANE = "crypto_d1_auto_research"
BUILDER_VERSION = "historical_evidence_acquisition_plan_b3_v1"
PHASE_B3_BUILD_TOKEN = "HUMAN_APPROVED_BUILD_C22_HISTORICAL_EVIDENCE_ACQUISITION_PLAN_PHASE_B3"

BOUND_SPEC_SHA256 = "9bf10af353521738f440c2e953af44cdd5ed093590f03a843a01972485dd9867"
BOUND_FORWARD_CONTRACT_SHA256 = "f3a1029ae705bd67e4eb8cdebff144f949c2d0ff6a62f89344738fbec65e731c"
BOUND_EXECUTION_CONTRACT_SHA256 = "1a207918c7146182ab41d888d1daa14cf85fbb592d97295795701932bccf713f"
BOUND_EVIDENCE_REQUEST_SHA256 = "a08a4cd58caa373cd5c9ec4f8c980a646105aa6c126fe269c33d2534e7108b40"

VERDICT_READY = "C22_HISTORICAL_EVIDENCE_ACQUISITION_PLAN_READY_FOR_HUMAN_REVIEW"
VERDICT_BLOCKED = "C22_HISTORICAL_EVIDENCE_ACQUISITION_PLAN_BLOCKED"

EXTERNAL_MARK = "REQUIRES_EXTERNAL_VERIFICATION"
ACQUISITION_STATUS = "NOT_AUTHORIZED"

# --- strict provider-neutral source hierarchy (best -> worst) --------------------------------
SOURCE_HIERARCHY = (
    "T1_OFFICIAL_VENUE_HISTORICAL_FILES_OR_OFFICIAL_API_DOCS",
    "T2_OFFICIAL_ARCHIVED_INSTRUMENT_AND_FEE_RECORDS",
    "T3_REPUTABLE_INSTITUTIONAL_MARKET_DATA_SOURCE",
    "T4_INDEPENDENTLY_ARCHIVED_PUBLIC_DATASET",
    "T5_UNSUPPORTED_THIRD_PARTY_EXPLORATORY_ONLY_NOT_DECISIVE",
)
DECISIVE_MIN_TIER = "T3_REPUTABLE_INSTITUTIONAL_MARKET_DATA_SOURCE"  # T5 is never decisive

# --- perpetual + spot-margin evidence categories (acquisition units) -------------------------
PERP_EVIDENCE_CATEGORIES = (
    "historical_contract_registry", "instrument_listing_and_delisting_timestamps",
    "contract_migrations", "historical_ohlc", "historical_funding_rates",
    "funding_settlement_timestamps", "fee_schedules_and_effective_dates", "tick_size", "lot_size",
    "minimum_notional", "historical_volume", "historical_spread_or_orderbook_proxy",
    "instrument_availability_by_date")
MARGIN_EVIDENCE_CATEGORIES = (
    "historical_spot_symbol_registry", "historical_margin_eligibility", "borrow_availability",
    "borrow_rate_history", "borrow_charging_intervals", "fee_schedules", "lot_tick_minimum_rules",
    "historical_volume", "historical_spread", "suspension_and_delisting_history",
    "availability_by_date")

# per-category source rules (uniform provider-neutral schema; instantiated per category)
CATEGORY_RULE_FIELDS = (
    "preferred_source_class", "acceptable_backup_source_class", "unacceptable_source_class",
    "immutable_identifier_requirement", "sha256_or_content_manifest_requirement",
    "date_coverage_requirement", "expected_file_format", "validation_rule",
    "admission_review_requirement")

# --- difficulty classes ----------------------------------------------------------------------
DIFF_LOW = "LOW"
DIFF_MEDIUM = "MEDIUM"
DIFF_HIGH = "HIGH"
DIFF_POSSIBLY_UNAVAILABLE = "POSSIBLY_UNAVAILABLE"

# --- acquisition groups (must not weaken per-asset validation or allow cross-venue sub) ------
ACQUISITION_GROUPS = (
    "BINANCE_VENUE_GROUP", "VENUE_NATIVE_TOKENS", "HIGH_COLLISION_IDENTIFIERS",
    "MAPPING_SENSITIVE_OR_NEWER_ASSETS", "ASSETS_WITH_PARTIAL_LOCAL_EVIDENCE",
    "ASSETS_WITH_NO_LOCAL_EVIDENCE")

# --- credential / safety classification ------------------------------------------------------
CREDENTIAL_CLASSES = (
    "PUBLIC_NO_AUTH", "PUBLIC_API_WITH_RATE_LIMITS", "AUTHENTICATED_READ_ONLY_API",
    "PAID_VENDOR", "UNAVAILABLE_OR_UNCLEAR")
PROHIBITED_PERMISSIONS = (
    "trading_permissions", "withdrawal_permissions", "order_permissions",
    "broker_or_exchange_account_linking", "unrestricted_api_keys",
    "secrets_committed_to_repository", "credentials_in_reports_or_logs")

# --- proposed (UNCREATED) gitignored evidence layout -----------------------------------------
PROPOSED_EVIDENCE_ROOT = "data/c22_short_instrument_evidence"   # gitignored by data/ rule
PROPOSED_LAYOUT = {
    "raw_source_files": PROPOSED_EVIDENCE_ROOT + "/raw/<venue>/<asset>/",
    "canonical_normalized_files": PROPOSED_EVIDENCE_ROOT + "/canonical/<venue>/<asset>/",
    "manifests": PROPOSED_EVIDENCE_ROOT + "/manifests/",
    "validation_reports": PROPOSED_EVIDENCE_ROOT + "/validation/",
    "rejected_quarantine": PROPOSED_EVIDENCE_ROOT + "/_quarantine/<date>/",
    "instrument_registry": PROPOSED_EVIDENCE_ROOT + "/registry/",
    "funding": PROPOSED_EVIDENCE_ROOT + "/funding/<asset>/",
    "borrow": PROPOSED_EVIDENCE_ROOT + "/borrow/<asset>/",
    "ohlc": PROPOSED_EVIDENCE_ROOT + "/ohlc/<asset>/",
    "fees": PROPOSED_EVIDENCE_ROOT + "/fees/<venue>/",
    "liquidity": PROPOSED_EVIDENCE_ROOT + "/liquidity/<asset>/",
    "symbol_mappings": PROPOSED_EVIDENCE_ROOT + "/mappings/",
}
FILENAME_CONVENTION = ("<venue>__<asset>__<category>__<start>_<end>.<ext> ; dates ISO YYYY-MM-DD; "
                       "every file paired with a .sha256 sidecar; manifests list per-file "
                       "sha256 + coverage; NEVER overwrites")
LAYOUT_CREATED_THIS_PHASE = False

# --- fail-close-early acquisition order ------------------------------------------------------
ACQUISITION_ORDER = (
    "1_historical_instrument_existence_registry",
    "2_symbol_and_venue_mapping",
    "3_funding_or_borrow_availability",
    "4_historical_ohlc",
    "5_fee_tick_lot_minimum_rules",
    "6_liquidity_and_spread_evidence",
    "7_full_holding_period_coverage")
EARLY_FAIL_CLOSE_STEPS = {
    "1_historical_instrument_existence_registry":
        "if the instrument/contract never existed over the signal+holding window -> asset "
        "fail-closed BEFORE any OHLC/funding acquisition",
    "2_symbol_and_venue_mapping":
        "if signal symbol cannot be deterministically mapped (esp. SPX identity, venue-native "
        "tokens) -> fail-closed before further acquisition",
    "3_funding_or_borrow_availability":
        "if neither perp funding nor spot-margin borrow existed historically -> asset "
        "fail-closed for BOTH implementations before OHLC/fees/liquidity",
}

# --- forward-exit interaction ----------------------------------------------------------------
NO_NEW_ENTRY_AFTER = _fed.ENTRY_CUTOFF                          # 2026-07-15
MIN_ACQUISITION_RANGE_START = _fed.FROZEN_START if hasattr(_fed, "FROZEN_START") else "2026-06-20"
INITIAL_RANGE_END = _fed.initial_exit_data_range()["end"]      # 2026-08-14
EXTENSION_INCREMENT_DAYS = _fed.EXTENSION_INCREMENT_CALENDAR_DAYS  # 15


def _proposed_authorization_sequence() -> list:
    return [
        {"batch": "C22_INSTRUMENT_REGISTRY_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
         "purpose": "authorize fetching only the historical instrument-existence registry + "
                    "listing/delisting timestamps",
         "human_token": "HUMAN_DECISION_C22_INSTRUMENT_REGISTRY_FETCH_AUTHORIZE"},
        {"batch": "C22_FUNDING_AND_BORROW_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
         "purpose": "authorize fetching historical funding (perp) and/or borrow availability+rate",
         "human_token": "HUMAN_DECISION_C22_FUNDING_AND_BORROW_FETCH_AUTHORIZE"},
        {"batch": "C22_EXECUTION_OHLC_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
         "purpose": "authorize fetching execution-instrument historical OHLC",
         "human_token": "HUMAN_DECISION_C22_EXECUTION_OHLC_FETCH_AUTHORIZE"},
        {"batch": "C22_FEES_AND_LIQUIDITY_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
         "purpose": "authorize fetching fee/tick/lot/minimum + liquidity/spread evidence",
         "human_token": "HUMAN_DECISION_C22_FEES_AND_LIQUIDITY_FETCH_AUTHORIZE"},
        {"batch": "C22_HISTORICAL_INSTRUMENT_EVIDENCE_READY_FOR_ADMISSION_REVIEW",
         "purpose": "human reviews all acquired evidence for admission",
         "human_token": "HUMAN_DECISION_C22_HISTORICAL_INSTRUMENT_EVIDENCE_ADMIT_OR_REJECT"},
    ]


def acquisition_difficulty(venue: str, mapping_risk: str, partial_funding: bool) -> str:
    """PURE, deterministic. Venue-native + high-collision are POSSIBLY_UNAVAILABLE (perp/borrow
    may never have existed); mapping-sensitive + non-Binance standard are HIGH; Binance partial
    is MEDIUM; Binance standard is LOW. NEVER infers from current listings -- these are a-priori
    acquisition-effort priors, each carrying REQUIRES_EXTERNAL_VERIFICATION."""
    if mapping_risk in (_er.MAPPING_RISK_VENUE_LOCKED, _er.MAPPING_RISK_HIGH_COLLISION):
        return DIFF_POSSIBLY_UNAVAILABLE
    if mapping_risk == _er.MAPPING_RISK_SENSITIVE:
        return DIFF_HIGH
    if venue != "BINANCE":
        return DIFF_HIGH
    if partial_funding:
        return DIFF_MEDIUM
    return DIFF_LOW


def _mandatory_human_decisions(symbol: str, mapping_risk: str) -> list:
    decisions = ["select_perp_vs_spot_margin_short_instrument"]
    if mapping_risk == _er.MAPPING_RISK_HIGH_COLLISION:
        decisions.append("pin_specific_crypto_token_identity_and_prohibit_sp500_index_mapping")
    if mapping_risk == _er.MAPPING_RISK_VENUE_LOCKED:
        decisions.append("approve_home_venue_implementation_or_explicit_cross_venue_approval")
    if mapping_risk == _er.MAPPING_RISK_SENSITIVE:
        decisions.append("approve_symbol_map_and_verify_historical_listing_existence")
    return decisions


def build_asset_feasibility(er_record: dict) -> dict:
    """PURE. Derive one asset's source-feasibility row from its Phase-B2 evidence-request record.
    Fails closed on both implementations under current local evidence; adds source classes,
    difficulty, human decisions, dataset estimate, and REQUIRES_EXTERNAL_VERIFICATION marks."""
    sym = er_record["signal_symbol"]
    venue = er_record["venue"]
    risk = er_record["mapping_risk_class"]
    partial = (er_record["funding_status"] == _er.PARTIAL_FUNDING_MARKER)
    diff = acquisition_difficulty(venue, risk, partial)
    # provider-neutral candidate source classes (which TIERS could plausibly serve), all
    # externally unverified until a fetch is later authorized + reviewed.
    perp_sources = [SOURCE_HIERARCHY[0], SOURCE_HIERARCHY[1], SOURCE_HIERARCHY[2]]
    margin_sources = [SOURCE_HIERARCHY[0], SOURCE_HIERARCHY[1], SOURCE_HIERARCHY[2]]
    if risk in (_er.MAPPING_RISK_VENUE_LOCKED, _er.MAPPING_RISK_HIGH_COLLISION):
        # for venue-native / collision names even T1 existence is uncertain
        perp_sources = [SOURCE_HIERARCHY[0], SOURCE_HIERARCHY[3] + "_EXPLORATORY_ONLY"]
        margin_sources = [SOURCE_HIERARCHY[0], SOURCE_HIERARCHY[3] + "_EXPLORATORY_ONLY"]
    est_datasets = {DIFF_LOW: 6, DIFF_MEDIUM: 8, DIFF_HIGH: 10,
                    DIFF_POSSIBLY_UNAVAILABLE: 11}[diff]
    external_assumptions = [
        "%s: perpetual contract existence over signal+holding window" % EXTERNAL_MARK,
        "%s: spot-margin borrow availability over signal+holding window" % EXTERNAL_MARK,
        "%s: deterministic signal->execution symbol map" % EXTERNAL_MARK,
    ]
    if risk == _er.MAPPING_RISK_HIGH_COLLISION:
        external_assumptions.append(
            "%s: SPX resolves to the specific crypto token (NOT the S&P 500 index)" % EXTERNAL_MARK)
    return {
        "signal_symbol": sym, "stable_identifier": er_record["stable_identifier"],
        "venue": venue, "mapping_risk_class": risk,
        "short_signal_dates": list(er_record["short_signal_dates"]),
        "possible_perp_source_classes": perp_sources,
        "possible_margin_source_classes": margin_sources,
        "current_local_evidence": {
            "funding_status": er_record["funding_status"],
            "borrow_status": er_record["borrow_status"],
            "perp_ohlc": "ABSENT", "fees": "ABSENT", "liquidity": "ABSENT"},
        "externally_unverified_assumptions": external_assumptions,
        "expected_acquisition_difficulty": diff,
        "mandatory_human_decisions": _mandatory_human_decisions(sym, risk),
        "estimated_distinct_evidence_datasets": est_datasets,
        "no_cross_venue_substitution": True,
        "fail_closed_condition": (
            "fail-closed for an implementation if (a) the instrument/borrow never existed over "
            "the window, (b) the symbol cannot be deterministically mapped, or (c) mandatory "
            "cost/coverage evidence is absent; currently fail-closed under BOTH implementations"),
        "currently_fail_closed_both": True,
    }


def _source_hierarchy_rules() -> dict:
    """PURE. Uniform per-category source rules (same schema for every evidence category)."""
    def _rule(coverage: str, fmt: str) -> dict:
        return {
            "preferred_source_class": SOURCE_HIERARCHY[0],
            "acceptable_backup_source_class": SOURCE_HIERARCHY[2],
            "unacceptable_source_class": SOURCE_HIERARCHY[4],  # T5 never decisive
            "immutable_identifier_requirement": "official URL/path + retrieved-at-UTC + venue id",
            "sha256_or_content_manifest_requirement": "per-file SHA-256 + coverage manifest",
            "date_coverage_requirement": coverage,
            "expected_file_format": fmt,
            "validation_rule": "schema + monotonic timestamps + no gaps on required sessions + "
                               "no dup rows + %s on any external assumption" % EXTERNAL_MARK,
            "admission_review_requirement": "separate human admission review before use",
        }
    rules = {}
    for cat in PERP_EVIDENCE_CATEGORIES:
        rules["perp:%s" % cat] = _rule("signal+holding window", "csv|json")
    for cat in MARGIN_EVIDENCE_CATEGORIES:
        rules["margin:%s" % cat] = _rule("signal+holding window", "csv|json")
    return rules


def _acquisition_groupings(feasibility_rows: list) -> dict:
    groups = {g: [] for g in ACQUISITION_GROUPS}
    for r in feasibility_rows:
        sym = r["signal_symbol"]; risk = r["mapping_risk_class"]
        if r["venue"] == "BINANCE":
            groups["BINANCE_VENUE_GROUP"].append(sym)
        if risk == _er.MAPPING_RISK_VENUE_LOCKED:
            groups["VENUE_NATIVE_TOKENS"].append(sym)
        if risk == _er.MAPPING_RISK_HIGH_COLLISION:
            groups["HIGH_COLLISION_IDENTIFIERS"].append(sym)
        if risk == _er.MAPPING_RISK_SENSITIVE:
            groups["MAPPING_SENSITIVE_OR_NEWER_ASSETS"].append(sym)
        if r["current_local_evidence"]["funding_status"] == _er.PARTIAL_FUNDING_MARKER:
            groups["ASSETS_WITH_PARTIAL_LOCAL_EVIDENCE"].append(sym)
        else:
            groups["ASSETS_WITH_NO_LOCAL_EVIDENCE"].append(sym)
    return {g: sorted(v) for g, v in groups.items()}


_CAPABILITY_FLAGS_FALSE = (
    "network", "browsing", "api_call", "credentials", "fetch", "import", "admission",
    "instrument_selection", "mapping_approval", "basis_approval", "cost_approval", "dry_run",
    "replay", "simulation", "token_issuance", "token_consumption", "lifecycle_advancement",
    "commit", "push", "creates_evidence_layout", "modifies_gitignore",
    "infers_existence_from_current_listing", "cross_venue_substitution",
)


def build_acquisition_plan(er_records: list) -> dict:
    """PURE. Assemble the full acquisition plan + feasibility matrix from the Phase-B2 records.
    Fetches NOTHING; authorizes NOTHING; selects NOTHING. Fails closed on universe/count defect."""
    blockers: list = []
    rows = [build_asset_feasibility(r) for r in sorted(er_records, key=lambda x: x["signal_symbol"])]
    if len(rows) != _er.EXPECTED_SHORT_ASSET_COUNT:
        blockers.append("expected_%d_assets_got_%d" % (_er.EXPECTED_SHORT_ASSET_COUNT, len(rows)))
    syms = [r["signal_symbol"] for r in rows]
    if len(set(syms)) != len(syms):
        blockers.append("duplicate_assets")
    if not all(r["no_cross_venue_substitution"] for r in rows):
        blockers.append("cross_venue_substitution_allowed")
    if not all(r["currently_fail_closed_both"] for r in rows):
        blockers.append("asset_not_fail_closed")
    if _spec.build_replay_spec()["spec_sha256"] != BOUND_SPEC_SHA256:
        blockers.append("bound_spec_sha_mismatch")

    plan: dict[str, Any] = {
        "contract": "c22_historical_instrument_evidence_acquisition_plan",
        "schema_version": AP_SCHEMA_VERSION, "builder_version": BUILDER_VERSION,
        "mode": AP_MODE, "lane": AP_LANE, "candidate_id": _spec._v2._v1.CANDIDATE_ID,
        "phase": "B3_ACQUISITION_PLAN_ONLY", "phase_b3_build_token": PHASE_B3_BUILD_TOKEN,
        "bound_replay_spec_sha256": BOUND_SPEC_SHA256,
        "bound_forward_contract_sha256": BOUND_FORWARD_CONTRACT_SHA256,
        "bound_execution_contract_sha256": BOUND_EXECUTION_CONTRACT_SHA256,
        "bound_evidence_request_sha256": BOUND_EVIDENCE_REQUEST_SHA256,
        "source_hierarchy": list(SOURCE_HIERARCHY),
        "decisive_minimum_tier": DECISIVE_MIN_TIER,
        "t5_never_decisive": True,
        "source_hierarchy_rules": _source_hierarchy_rules(),
        "perp_evidence_categories": list(PERP_EVIDENCE_CATEGORIES),
        "margin_evidence_categories": list(MARGIN_EVIDENCE_CATEGORIES),
        "feasibility_matrix": rows, "asset_count": len(rows),
        "acquisition_groups": _acquisition_groupings(rows),
        "grouping_preserves_per_asset_validation": True,
        "credential_classes": list(CREDENTIAL_CLASSES),
        "prohibited_permissions": list(PROHIBITED_PERMISSIONS),
        "authenticated_source_is_future_human_decision": True,
        "no_credentials_created_or_requested": True,
        "proposed_evidence_root": PROPOSED_EVIDENCE_ROOT,
        "proposed_layout": PROPOSED_LAYOUT,
        "filename_convention": FILENAME_CONVENTION,
        "layout_created_this_phase": LAYOUT_CREATED_THIS_PHASE,
        "acquisition_order": list(ACQUISITION_ORDER),
        "early_fail_close_steps": EARLY_FAIL_CLOSE_STEPS,
        "no_new_entry_after": NO_NEW_ENTRY_AFTER,
        "min_acquisition_range_start": MIN_ACQUISITION_RANGE_START,
        "initial_range_end": INITIAL_RANGE_END,
        "extension_increment_days": EXTENSION_INCREMENT_DAYS,
        "incremental_update_procedure": "extend forward in %d-day increments; append-only; each "
                                        "increment adds files + updates the manifest; NEVER "
                                        "rewrites prior files or frozen entry dates"
                                        % EXTENSION_INCREMENT_DAYS,
        "manifest_continuity_required": True,
        "frozen_entry_dates_immutable": True,
        "final_exit_end_date_known": False,
        "acquisition_status": ACQUISITION_STATUS,
        "external_verification_marker": EXTERNAL_MARK,
        "proposed_authorization_sequence": _proposed_authorization_sequence(),
        "authorization_sequence_activated": False,
        "human_review_required": True,
        "verdict": (VERDICT_READY if not blockers else VERDICT_BLOCKED),
        "blockers": blockers,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        plan[flag] = False
    plan["contract_sha256"] = _hashlib.sha256(canonical_plan_bytes(plan)).hexdigest()
    return plan


def canonical_plan_bytes(plan: dict) -> bytes:
    payload = {k: v for k, v in plan.items() if k != "contract_sha256"}
    return _json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def validate_acquisition_plan(p: Any) -> dict:
    """Anti-tamper validator. Valid only when research-only + B3 plan-only, bound to the four
    accepted SHAs, 22 fail-closed assets, no cross-venue substitution, T5 never decisive,
    identity risks retained (SPX collision / venue-locked / sensitive), credentials read-only or
    no-auth with prohibited trade/withdraw/order permissions, layout not created + gitignore
    unchanged, acquisition NOT_AUTHORIZED, auth sequence proposed-inactive with no replay-token
    reuse, every external assumption marked, every capability flag False."""
    f: list = []
    if not isinstance(p, dict):
        return {"valid": False, "failures": ["plan_not_a_dict"]}
    if p.get("mode") != AP_MODE:
        f.append("mode_not_research_only")
    if p.get("phase") != "B3_ACQUISITION_PLAN_ONLY":
        f.append("not_b3_plan_only")
    for k, want in (("bound_replay_spec_sha256", BOUND_SPEC_SHA256),
                    ("bound_forward_contract_sha256", BOUND_FORWARD_CONTRACT_SHA256),
                    ("bound_execution_contract_sha256", BOUND_EXECUTION_CONTRACT_SHA256),
                    ("bound_evidence_request_sha256", BOUND_EVIDENCE_REQUEST_SHA256)):
        if p.get(k) != want:
            f.append("bound_sha_wrong:%s" % k)
    rows = p.get("feasibility_matrix") or []
    if len(rows) != _er.EXPECTED_SHORT_ASSET_COUNT:
        f.append("asset_count_wrong")
    syms = [r.get("signal_symbol") for r in rows]
    if len(set(syms)) != len(syms):
        f.append("duplicate_assets")
    byd = {r.get("signal_symbol"): r for r in rows}
    for r in rows:
        if r.get("no_cross_venue_substitution") is not True:
            f.append("cross_venue_substitution:%s" % r.get("signal_symbol"))
        if r.get("currently_fail_closed_both") is not True:
            f.append("not_fail_closed:%s" % r.get("signal_symbol"))
        if not any(EXTERNAL_MARK in a for a in r.get("externally_unverified_assumptions") or []):
            f.append("external_assumptions_not_marked:%s" % r.get("signal_symbol"))
    # identity-risk retention
    if byd.get("KRAKEN:SPXUSD", {}).get("mapping_risk_class") != _er.MAPPING_RISK_HIGH_COLLISION:
        f.append("spx_collision_not_retained")
    for s in _er.VENUE_LOCKED_NATIVE:
        if s in byd and byd[s]["mapping_risk_class"] != _er.MAPPING_RISK_VENUE_LOCKED:
            f.append("venue_locked_not_retained:%s" % s)
    for s in _er.MAPPING_SENSITIVE:
        if s in byd and byd[s]["mapping_risk_class"] != _er.MAPPING_RISK_SENSITIVE:
            f.append("sensitive_not_retained:%s" % s)
    # partial Binance funding still insufficient (not decisive evidence)
    for s in _er.PARTIAL_FUNDING_BINANCE:
        if s in byd and byd[s]["current_local_evidence"]["funding_status"] != _er.PARTIAL_FUNDING_MARKER:
            f.append("partial_funding_not_insufficient:%s" % s)
    # source hierarchy + T5 never decisive
    if tuple(p.get("source_hierarchy") or ()) != SOURCE_HIERARCHY:
        f.append("source_hierarchy_wrong")
    if p.get("t5_never_decisive") is not True:
        f.append("t5_decisive_allowed")
    if p.get("decisive_minimum_tier") != DECISIVE_MIN_TIER:
        f.append("decisive_min_tier_wrong")
    # credential safety
    if tuple(p.get("credential_classes") or ()) != CREDENTIAL_CLASSES:
        f.append("credential_classes_wrong")
    for perm in PROHIBITED_PERMISSIONS:
        if perm not in (p.get("prohibited_permissions") or []):
            f.append("prohibited_permission_missing:%s" % perm)
    if p.get("no_credentials_created_or_requested") is not True:
        f.append("credentials_created_or_requested")
    # layout not created + gitignore untouched
    if p.get("layout_created_this_phase") is not False:
        f.append("layout_created")
    if p.get("modifies_gitignore") is not False:
        f.append("gitignore_modified")
    # acquisition + forward-horizon
    if p.get("acquisition_status") != ACQUISITION_STATUS:
        f.append("acquisition_authorized")
    if p.get("no_new_entry_after") != NO_NEW_ENTRY_AFTER:
        f.append("entry_cutoff_wrong")
    if p.get("frozen_entry_dates_immutable") is not True:
        f.append("entry_dates_not_immutable")
    if p.get("final_exit_end_date_known") is not False:
        f.append("final_exit_wrongly_known")
    if p.get("initial_range_end") != INITIAL_RANGE_END or p.get("extension_increment_days") != 15:
        f.append("forward_horizon_wrong")
    # authorization sequence: proposed-inactive, no replay-token reuse
    seq = [b.get("batch") for b in (p.get("proposed_authorization_sequence") or [])]
    if seq != ["C22_INSTRUMENT_REGISTRY_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
               "C22_FUNDING_AND_BORROW_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
               "C22_EXECUTION_OHLC_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
               "C22_FEES_AND_LIQUIDITY_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
               "C22_HISTORICAL_INSTRUMENT_EVIDENCE_READY_FOR_ADMISSION_REVIEW"]:
        f.append("authorization_sequence_wrong")
    for b in (p.get("proposed_authorization_sequence") or []):
        if b.get("human_token") == _spec.REPLAY_ADVANCE_TOKEN:
            f.append("reused_replay_token")
    if p.get("authorization_sequence_activated") is not False:
        f.append("auth_sequence_activated")
    for flag in _CAPABILITY_FLAGS_FALSE:
        if p.get(flag) is not False:
            f.append("capability_flag_true:%s" % flag)
    if p.get("contract_sha256") and p["contract_sha256"] != _hashlib.sha256(
            canonical_plan_bytes(p)).hexdigest():
        f.append("contract_hash_mismatch")
    if p.get("verdict") == VERDICT_READY and p.get("blockers"):
        f.append("ready_with_blockers")
    return {"valid": not f, "failures": f}

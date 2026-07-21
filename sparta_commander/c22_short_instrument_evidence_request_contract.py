"""Candidate #22 -- SHORT-INSTRUMENT HISTORICAL EVIDENCE REQUEST CONTRACT
(Phase B2: CONTRACT + EVIDENCE-MATRIX + PLANNING ONLY, PURE, ADDITIVE, RESEARCH-ONLY).

Human-approved build token (Phase B2 only):
HUMAN_APPROVED_BUILD_C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST_PHASE_B2.

Produces a deterministic, PROVIDER-NEUTRAL historical-evidence request for every short asset in
the frozen V2 label evidence, so a human can later authorize acquisition and select a short
instrument. It BROWSES NOTHING, FETCHES NOTHING, calls NO API, imports/admits NO data, selects
NO instrument, approves NO mapping / basis / cost, runs NO dry-run/replay, and issues/consumes
NO token. Every capability flag is pinned False; suggestion-only.

The 22-asset short universe is DERIVED (never retyped) from the frozen V2 artifact via the
report tool's read-only loader; this contract holds the pure request schema, the mapping-risk
classification, the per-implementation required-evidence lists, the coverage-period rules, and
the fail-closed validator. Bound to the accepted replay spec + Phase B1 contracts by SHA.
"""
from __future__ import annotations

import hashlib as _hashlib
import json as _json
from typing import Any

import sparta_commander.external_signum_trend_radar_gc_long_short_v1_replay_spec_contract as _spec  # noqa: E501
import sparta_commander.c22_forward_exit_data_readiness_contract as _fed
import sparta_commander.c22_execution_data_short_instrument_feasibility_contract as _exe

ER_SCHEMA_VERSION = 1
ER_MODE = "RESEARCH_ONLY"
ER_LANE = "crypto_d1_auto_research"
BUILDER_VERSION = "short_instrument_evidence_request_b2_v1"
PHASE_B2_BUILD_TOKEN = "HUMAN_APPROVED_BUILD_C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST_PHASE_B2"

BOUND_SPEC_SHA256 = "9bf10af353521738f440c2e953af44cdd5ed093590f03a843a01972485dd9867"
BOUND_FORWARD_CONTRACT_SHA256 = "f3a1029ae705bd67e4eb8cdebff144f949c2d0ff6a62f89344738fbec65e731c"
BOUND_EXECUTION_CONTRACT_SHA256 = "1a207918c7146182ab41d888d1daa14cf85fbb592d97295795701932bccf713f"

VERDICT_READY = "C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST_READY_FOR_HUMAN_REVIEW"
VERDICT_BLOCKED = "C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST_BLOCKED"

# --- frozen expectations (single-sourced; the derived universe MUST match) -------------------
FROZEN_START = _spec.FROZEN_END and "2026-06-20"
FROZEN_END = _spec.FROZEN_END                      # 2026-07-15
EXPECTED_SHORT_ASSET_COUNT = 22
EXPECTED_BEAR_SHORT = 72
EXPECTED_HEDGE_SHORT = 3
SHORT_SIGNALS = (_spec._v2._v1.SIGNAL_BEAR, _spec._v2._v1.SIGNAL_HEDGE)  # BEAR_SHORT, HEDGE_SHORT
LONG_SIGNAL = _spec._v2._v1.SIGNAL_LONG

# --- identity-risk classes (retained explicitly) --------------------------------------------
HIGH_COLLISION_RISK = ("KRAKEN:SPXUSD",)
VENUE_LOCKED_NATIVE = ("GATE:GTUSDT", "OKX:OKBUSDT", "BITFINEX:LEOUSD")
MAPPING_SENSITIVE = ("BYBIT:GRAMUSDT", "BYBIT:TELUSDT", "GATE:ASTERUSDT", "BINANCE:VIRTUALUSDT")
MAPPING_RISK_STANDARD = "STANDARD_MAPPING"
MAPPING_RISK_HIGH_COLLISION = "HIGH_COLLISION_RISK"
MAPPING_RISK_VENUE_LOCKED = "VENUE_LOCKED_NATIVE"
MAPPING_RISK_SENSITIVE = "MAPPING_SENSITIVE"

# six Binance names with partial (insufficient) local funding, ending 2026-06-21
PARTIAL_FUNDING_BINANCE = ("BINANCE:AAVEUSDT", "BINANCE:CRVUSDT", "BINANCE:LINKUSDT",
                           "BINANCE:SOLUSDT", "BINANCE:TRXUSDT", "BINANCE:ZECUSDT")
PARTIAL_FUNDING_MARKER = "PARTIAL_EXPLORATORY_EVIDENCE_INSUFFICIENT"
PARTIAL_FUNDING_LOCAL_END = "2026-06-21"
BORROW_LOCAL_STATUS_ALL = "ABSENT_FOR_ALL_22"
BASIS_STATUS = "BASIS_ALIGNMENT_NOT_REVIEWED"
THIRTY_SEVEN_BPS_STATUS = "37_BPS_SENSITIVITY_CASE_NOT_BASE_CASE"

# --- per-implementation required evidence ----------------------------------------------------
PERP_REQUIRED_EVIDENCE = (
    "execution_venue", "historical_perpetual_contract_symbol", "base_asset", "quote_asset",
    "settlement_asset", "linear_or_inverse_classification", "instrument_listing_start_timestamp",
    "delisting_end_timestamp_if_applicable", "contract_migration_or_symbol_change_history",
    "historical_ohlc_covering_entry_and_holding_sessions", "historical_funding_rates",
    "funding_timestamps_and_settlement_intervals", "trading_fee_schedule_and_effective_dates",
    "maker_taker_assumptions", "tick_size", "lot_size", "minimum_notional",
    "daily_notional_volume", "spread_evidence", "availability_by_signal_and_holding_date",
    "deterministic_signal_to_execution_contract_mapping", "immutable_source_reference_or_sha256")

MARGIN_REQUIRED_EVIDENCE = (
    "execution_venue", "historical_spot_symbol", "cross_or_isolated_margin_mode",
    "historically_borrowable_asset", "historical_borrow_availability_series",
    "historical_borrow_rate_series", "borrow_charging_interval",
    "trading_fee_schedule_and_effective_dates", "maker_taker_assumptions", "tick_size",
    "lot_size", "minimum_notional", "daily_notional_volume", "spread_evidence",
    "suspension_and_delisting_history", "availability_on_every_signal_and_holding_date",
    "deterministic_signal_to_margin_symbol_mapping", "immutable_source_reference_or_sha256")

COST_COMPONENT_EVIDENCE = (
    "entry_trading_fee", "exit_trading_fee", "entry_half_spread", "exit_half_spread",
    "entry_slippage", "exit_slippage", "funding_or_borrow_cost", "exceptional_exit_cost",
    "basis_adjustment_cost_if_applicable")

BASIS_ALIGNMENT_FIELDS = (
    "trend_radar_signal_price_source", "execution_instrument_price_source", "signal_timestamp",
    "execution_timestamp", "signal_price", "execution_reference_price", "absolute_basis",
    "percentage_basis", "symbol_map_confidence", "approved_basis_adjustment_rule_if_later_needed")

# --- coverage periods (single-sourced) -------------------------------------------------------
ENTRY_EVIDENCE_PERIOD = [FROZEN_START, FROZEN_END]                       # 2026-06-20..2026-07-15
INITIAL_EXIT_EVIDENCE_PERIOD = [_fed.FIRST_EXIT_ONLY_DATE,
                                _fed.initial_exit_data_range()["end"]]   # 2026-07-16..2026-08-14
EXIT_EXTENSION_INCREMENT_DAYS = _fed.EXTENSION_INCREMENT_CALENDAR_DAYS   # 15

# --- provider-neutral acquisition categories (NOT authorized) --------------------------------
ACQUISITION_STATUS = "NOT_AUTHORIZED"
ACQUISITION_CATEGORY_FIELDS = (
    "required_fields", "frequency", "date_coverage", "immutable_identifier", "validation_rule",
    "expected_local_destination_class", "human_approval_required_before_fetch",
    "separate_admission_review_required_after")


def mapping_risk_class(symbol: str) -> str:
    if symbol in HIGH_COLLISION_RISK:
        return MAPPING_RISK_HIGH_COLLISION
    if symbol in VENUE_LOCKED_NATIVE:
        return MAPPING_RISK_VENUE_LOCKED
    if symbol in MAPPING_SENSITIVE:
        return MAPPING_RISK_SENSITIVE
    return MAPPING_RISK_STANDARD


def parse_symbol(symbol: str) -> dict:
    """PURE identity split. VENUE:PAIR -> venue, pair, base, quote. Deterministic, no inference."""
    if ":" in symbol:
        venue, pair = symbol.split(":", 1)
    else:
        venue, pair = "NONE", symbol
    base, quote = pair, ""
    for q in ("USDT", "USDC", "FDUSD", "BUSD", "USD"):
        if pair.endswith(q):
            base, quote = pair[:-len(q)], q
            break
    return {"venue": venue, "pair": pair, "base": base, "quote": quote}


def _asset_local_evidence(symbol: str) -> dict:
    """PURE local-evidence status for one asset. Perp funding is PARTIAL only for the six
    named Binance pairs (ends 2026-06-21, insufficient); borrow ABSENT for all; no
    present-day-availability inference anywhere."""
    perp = (PARTIAL_FUNDING_MARKER if symbol in PARTIAL_FUNDING_BINANCE else "ABSENT")
    return {
        "local_perp_funding_status": perp,
        "local_perp_funding_local_end": (PARTIAL_FUNDING_LOCAL_END
                                         if symbol in PARTIAL_FUNDING_BINANCE else None),
        "local_perp_ohlc_status": "ABSENT",
        "local_margin_borrow_availability_status": "ABSENT",
        "local_margin_borrow_rate_status": "ABSENT",
        "local_fee_schedule_status": "ABSENT",
        "local_tick_lot_notional_status": "ABSENT",
        "local_liquidity_volume_status": "ABSENT",
        "local_price_source_status": "SIGNAL_VENUE_ONLY_EXECUTION_SOURCE_UNKNOWN",
    }


def build_asset_record(symbol: str, short_dates: list, bear: int, hedge: int,
                       long_dates: list) -> dict:
    """PURE. Assemble one asset's evidence-request record from DERIVED signal facts. Fails
    closed under both implementations while required historical evidence is absent."""
    ident = parse_symbol(symbol)
    risk = mapping_risk_class(symbol)
    local = _asset_local_evidence(symbol)
    perp_blocker = ("perp_partial_funding_insufficient_plus_missing_ohlc_fees_tick_lot"
                    if symbol in PARTIAL_FUNDING_BINANCE
                    else "perp_instrument_and_cost_evidence_absent")
    return {
        "signal_symbol": symbol, "stable_identifier": symbol,
        "venue": ident["venue"], "base_asset": ident["base"], "quote_asset": ident["quote"],
        "short_label_count": bear + hedge, "bear_short_count": bear, "hedge_short_count": hedge,
        "first_short_date": short_dates[0], "last_short_date": short_dates[-1],
        "short_signal_dates": list(short_dates),
        "long_entry_dates": list(long_dates),
        "mapping_risk_class": risk,
        "local_evidence": local,
        "required_perp_evidence": list(PERP_REQUIRED_EVIDENCE),
        "required_margin_evidence": list(MARGIN_REQUIRED_EVIDENCE),
        "required_entry_coverage": list(ENTRY_EVIDENCE_PERIOD),
        "required_exit_coverage": list(INITIAL_EXIT_EVIDENCE_PERIOD),
        "required_exit_coverage_note": "extend deterministically in %d-day increments until the "
                                       "natural exit date; final end date NOT knowable until the "
                                       "forward-exit path is complete" % EXIT_EXTENSION_INCREMENT_DAYS,
        "funding_status": (PARTIAL_FUNDING_MARKER if symbol in PARTIAL_FUNDING_BINANCE
                           else "ABSENT"),
        "borrow_status": "ABSENT",
        "price_source_status": local["local_price_source_status"],
        "fee_status": "ABSENT", "liquidity_status": "ABSENT",
        "fail_closed_perp": True, "fail_closed_margin": True,
        "perp_blocker": perp_blocker,
        "margin_blocker": "margin_borrow_availability_and_rate_absent",
        "current_fail_closed_blocker": "no_admissible_historical_instrument_or_cost_evidence",
        "evidence_request_readiness": "READY_TO_REQUEST",
    }


def _proposed_lifecycle_gates() -> list:
    return [
        {"gate": "C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST_READY_FOR_HUMAN_REVIEW",
         "purpose": "human reviews this provider-neutral evidence request",
         "human_token": "HUMAN_DECISION_C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST_ACCEPT_OR_REVISE"},
        {"gate": "C22_HISTORICAL_INSTRUMENT_DATA_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
         "purpose": "human authorizes a specific provider-neutral acquisition (out of band)",
         "human_token": "HUMAN_DECISION_C22_HISTORICAL_INSTRUMENT_DATA_FETCH_AUTHORIZE"},
        {"gate": "C22_SHORT_INSTRUMENT_EVIDENCE_READY_FOR_ADMISSION_REVIEW",
         "purpose": "human reviews acquired evidence for admission",
         "human_token": "HUMAN_DECISION_C22_SHORT_INSTRUMENT_EVIDENCE_ADMIT_OR_REJECT"},
        {"gate": "C22_SHORT_INSTRUMENT_READY_FOR_HUMAN_SELECTION",
         "purpose": "human selects perp vs spot-margin per asset with full evidence",
         "human_token": "HUMAN_DECISION_C22_SHORT_INSTRUMENT_SELECT"},
    ]


_CAPABILITY_FLAGS_FALSE = (
    "network", "browsing", "api_call", "fetch", "import", "dataset_mutation",
    "evidence_admission", "instrument_selection", "symbol_mapping_approval",
    "basis_adjustment_selection", "cost_approval", "dry_run", "replay", "simulation",
    "token_issuance", "token_consumption", "lifecycle_advancement", "commit", "push",
    "infers_historical_from_present_availability",
)


def build_evidence_request(asset_records: list) -> dict:
    """PURE. Assemble the full evidence-request contract from DERIVED asset records. Writes
    NOTHING; authorizes NOTHING. Fails closed on any universe/count/duplicate/date defect."""
    blockers: list = []
    records = sorted(list(asset_records or []), key=lambda r: r["signal_symbol"])
    symbols = [r["signal_symbol"] for r in records]

    if len(records) != EXPECTED_SHORT_ASSET_COUNT:
        blockers.append("expected_%d_assets_got_%d" % (EXPECTED_SHORT_ASSET_COUNT, len(records)))
    if len(set(symbols)) != len(symbols):
        blockers.append("duplicate_asset_symbols")
    tot_bear = sum(r["bear_short_count"] for r in records)
    tot_hedge = sum(r["hedge_short_count"] for r in records)
    if tot_bear != EXPECTED_BEAR_SHORT:
        blockers.append("bear_short_total_%d_ne_%d" % (tot_bear, EXPECTED_BEAR_SHORT))
    if tot_hedge != EXPECTED_HEDGE_SHORT:
        blockers.append("hedge_short_total_%d_ne_%d" % (tot_hedge, EXPECTED_HEDGE_SHORT))
    for r in records:
        for d in r["short_signal_dates"]:
            if d > FROZEN_END:
                blockers.append("short_date_after_frozen_end:%s:%s" % (r["signal_symbol"], d))
        if len(set(r["short_signal_dates"])) != len(r["short_signal_dates"]):
            blockers.append("duplicate_short_date_for_asset:%s" % r["signal_symbol"])
    # identity-risk retention
    for sym in HIGH_COLLISION_RISK + VENUE_LOCKED_NATIVE + MAPPING_SENSITIVE:
        if sym in symbols:
            rec = next(r for r in records if r["signal_symbol"] == sym)
            if rec["mapping_risk_class"] == MAPPING_RISK_STANDARD:
                blockers.append("mapping_risk_not_retained:%s" % sym)

    request: dict[str, Any] = {
        "contract": "c22_short_instrument_historical_evidence_request",
        "schema_version": ER_SCHEMA_VERSION, "builder_version": BUILDER_VERSION,
        "mode": ER_MODE, "lane": ER_LANE, "candidate_id": _spec._v2._v1.CANDIDATE_ID,
        "phase": "B2_EVIDENCE_REQUEST_ONLY", "phase_b2_build_token": PHASE_B2_BUILD_TOKEN,
        "bound_replay_spec_sha256": BOUND_SPEC_SHA256,
        "bound_forward_contract_sha256": BOUND_FORWARD_CONTRACT_SHA256,
        "bound_execution_contract_sha256": BOUND_EXECUTION_CONTRACT_SHA256,
        "frozen_entry_range": [FROZEN_START, FROZEN_END],
        "expected_short_asset_count": EXPECTED_SHORT_ASSET_COUNT,
        "expected_bear_short": EXPECTED_BEAR_SHORT, "expected_hedge_short": EXPECTED_HEDGE_SHORT,
        "asset_records": records, "asset_count": len(records),
        "high_collision_risk_assets": list(HIGH_COLLISION_RISK),
        "venue_locked_native_assets": list(VENUE_LOCKED_NATIVE),
        "mapping_sensitive_assets": list(MAPPING_SENSITIVE),
        "partial_funding_binance_assets": list(PARTIAL_FUNDING_BINANCE),
        "partial_funding_marker": PARTIAL_FUNDING_MARKER,
        "partial_funding_local_end": PARTIAL_FUNDING_LOCAL_END,
        "borrow_local_status_all": BORROW_LOCAL_STATUS_ALL,
        "basis_alignment_status": BASIS_STATUS,
        "basis_alignment_fields": list(BASIS_ALIGNMENT_FIELDS),
        "cost_component_evidence": list(COST_COMPONENT_EVIDENCE),
        "thirty_seven_bps_status": THIRTY_SEVEN_BPS_STATUS,
        "entry_evidence_period": list(ENTRY_EVIDENCE_PERIOD),
        "initial_exit_evidence_period": list(INITIAL_EXIT_EVIDENCE_PERIOD),
        "exit_extension_increment_days": EXIT_EXTENSION_INCREMENT_DAYS,
        "final_exit_end_date_known": False,
        "acquisition_status": ACQUISITION_STATUS,
        "acquisition_category_fields": list(ACQUISITION_CATEGORY_FIELDS),
        "proposed_lifecycle_gates": _proposed_lifecycle_gates(),
        "lifecycle_gates_activated": False,
        "all_assets_fail_closed_perp": all(r["fail_closed_perp"] for r in records),
        "all_assets_fail_closed_margin": all(r["fail_closed_margin"] for r in records),
        "human_review_required": True,
        "verdict": (VERDICT_READY if not blockers else VERDICT_BLOCKED),
        "blockers": blockers,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        request[flag] = False
    request["contract_sha256"] = _hashlib.sha256(
        canonical_request_bytes(request)).hexdigest()
    return request


def canonical_request_bytes(request: dict) -> bytes:
    payload = {k: v for k, v in request.items() if k != "contract_sha256"}
    return _json.dumps(payload, indent=2, sort_keys=True).encode("utf-8") + b"\n"


def validate_evidence_request(r: Any) -> dict:
    """Anti-tamper validator. Valid only when research-only + B2 evidence-request-only, bound to
    the three accepted SHAs, exactly 22 assets / 72 BEAR / 3 HEDGE, no duplicate/late dates,
    identity risks retained (SPX collision, GT/OKB/LEO venue-locked, 4 sensitive), the 6 Binance
    partial-funding names marked insufficient, borrow ABSENT for all, all fail-closed under both
    implementations, acquisition NOT_AUTHORIZED, gates proposed-inactive, every capability flag
    False."""
    f: list = []
    if not isinstance(r, dict):
        return {"valid": False, "failures": ["request_not_a_dict"]}
    if r.get("mode") != ER_MODE:
        f.append("mode_not_research_only")
    if r.get("phase") != "B2_EVIDENCE_REQUEST_ONLY":
        f.append("not_b2_evidence_request_only")
    if r.get("bound_replay_spec_sha256") != BOUND_SPEC_SHA256:
        f.append("bound_spec_sha_wrong")
    if r.get("bound_forward_contract_sha256") != BOUND_FORWARD_CONTRACT_SHA256:
        f.append("bound_forward_sha_wrong")
    if r.get("bound_execution_contract_sha256") != BOUND_EXECUTION_CONTRACT_SHA256:
        f.append("bound_execution_sha_wrong")
    recs = r.get("asset_records") or []
    syms = [x.get("signal_symbol") for x in recs]
    if len(recs) != EXPECTED_SHORT_ASSET_COUNT:
        f.append("asset_count_wrong")
    if len(set(syms)) != len(syms):
        f.append("duplicate_assets")
    if sum(x.get("bear_short_count", 0) for x in recs) != EXPECTED_BEAR_SHORT:
        f.append("bear_short_total_wrong")
    if sum(x.get("hedge_short_count", 0) for x in recs) != EXPECTED_HEDGE_SHORT:
        f.append("hedge_short_total_wrong")
    for x in recs:
        for d in x.get("short_signal_dates", []):
            if d > FROZEN_END:
                f.append("short_date_after_end:%s" % x.get("signal_symbol"))
                break
        if x.get("fail_closed_perp") is not True or x.get("fail_closed_margin") is not True:
            f.append("asset_not_fail_closed:%s" % x.get("signal_symbol"))
    # identity-risk retention
    for sym in HIGH_COLLISION_RISK:
        rec = next((x for x in recs if x.get("signal_symbol") == sym), None)
        if rec and rec.get("mapping_risk_class") != MAPPING_RISK_HIGH_COLLISION:
            f.append("spx_collision_risk_not_retained")
    for sym in VENUE_LOCKED_NATIVE:
        rec = next((x for x in recs if x.get("signal_symbol") == sym), None)
        if rec and rec.get("mapping_risk_class") != MAPPING_RISK_VENUE_LOCKED:
            f.append("venue_locked_not_retained:%s" % sym)
    for sym in MAPPING_SENSITIVE:
        rec = next((x for x in recs if x.get("signal_symbol") == sym), None)
        if rec and rec.get("mapping_risk_class") != MAPPING_RISK_SENSITIVE:
            f.append("sensitive_not_retained:%s" % sym)
    # six Binance partial-funding names insufficient (not approval)
    for sym in PARTIAL_FUNDING_BINANCE:
        rec = next((x for x in recs if x.get("signal_symbol") == sym), None)
        if rec and rec.get("funding_status") != PARTIAL_FUNDING_MARKER:
            f.append("partial_funding_not_marked_insufficient:%s" % sym)
    if r.get("borrow_local_status_all") != BORROW_LOCAL_STATUS_ALL:
        f.append("borrow_status_wrong")
    if not all(x.get("borrow_status") == "ABSENT" for x in recs):
        f.append("borrow_not_absent_for_all")
    if r.get("all_assets_fail_closed_perp") is not True or \
            r.get("all_assets_fail_closed_margin") is not True:
        f.append("not_all_fail_closed")
    if r.get("basis_alignment_status") != BASIS_STATUS:
        f.append("basis_status_wrong")
    if r.get("thirty_seven_bps_status") != THIRTY_SEVEN_BPS_STATUS:
        f.append("37bps_not_sensitivity")
    if r.get("acquisition_status") != ACQUISITION_STATUS:
        f.append("acquisition_not_unauthorized")
    if r.get("final_exit_end_date_known") is not False:
        f.append("final_exit_end_date_wrongly_known")
    gates = [g.get("gate") for g in (r.get("proposed_lifecycle_gates") or [])]
    if gates != ["C22_SHORT_INSTRUMENT_EVIDENCE_REQUEST_READY_FOR_HUMAN_REVIEW",
                 "C22_HISTORICAL_INSTRUMENT_DATA_FETCH_READY_FOR_HUMAN_AUTHORIZATION",
                 "C22_SHORT_INSTRUMENT_EVIDENCE_READY_FOR_ADMISSION_REVIEW",
                 "C22_SHORT_INSTRUMENT_READY_FOR_HUMAN_SELECTION"]:
        f.append("proposed_gates_wrong")
    # must NOT reuse the final replay token for these phases
    for g in (r.get("proposed_lifecycle_gates") or []):
        if g.get("human_token") == _spec.REPLAY_ADVANCE_TOKEN:
            f.append("reused_replay_token")
    if r.get("lifecycle_gates_activated") is not False:
        f.append("gates_wrongly_activated")
    for flag in _CAPABILITY_FLAGS_FALSE:
        if r.get(flag) is not False:
            f.append("capability_flag_true:%s" % flag)
    if r.get("contract_sha256") and r["contract_sha256"] != _hashlib.sha256(
            canonical_request_bytes(r)).hexdigest():
        f.append("contract_hash_mismatch")
    if r.get("verdict") == VERDICT_READY and r.get("blockers"):
        f.append("ready_with_blockers")
    return {"valid": not f, "failures": f}

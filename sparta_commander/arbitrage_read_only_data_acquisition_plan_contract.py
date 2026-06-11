"""SPARTA Arbitrage Factory V1 - READ-ONLY DATA ACQUISITION PLAN (READ-ONLY).

The inventory found the repo's data structurally insufficient for arbitrage
(daily single-venue spot OHLCV; no funding, no perp leg, no bid/ask, no depth).
This contract PLANS how the missing arbitrage-shaped data may be acquired --
and fetches NOTHING itself: no network, no API, no exchange connection, no
credential, ever. It is a rulebook plus a pure plan-entry evaluator.

Allowed acquisition methods (read-only, no-auth, human-driven):
  - manual_export_from_venue_public_page  (a human copies public data by hand)
  - public_csv_download_no_auth           (a human downloads a public file)
  - public_webpage_snapshot_manual        (a human records public numbers)
  - future_no_auth_public_endpoint        (NOT allowed now; would need its own
                                           separate human-approved contract)

Forbidden methods (refused outright, validator-enforced):
  authenticated/keyed APIs, exchange account statements, wallet/order/fill/
  position exports, private keys, anything behind a login, paid private feeds.
  Acquired data describes MARKETS, never ACCOUNTS.

Everything acquired must be hand-transformed into the approved staged CSV
templates (exact headers, UTC timestamps, allowed labels), carry a provenance
source label, and meet the freshness rules. The source whitelist here is a
PROPOSAL for human review -- listing a source approves nothing.

Public API:
  - ACQ_SCHEMA_VERSION / ACQ_LABEL / ACQ_MODE
  - VERDICT_ACQ_PLAN_READY / VERDICT_ACQ_PLAN_BLOCKED
  - VERDICT_PLAN_ENTRY_ACCEPTED / VERDICT_PLAN_ENTRY_REFUSED
  - ALLOWED_METHODS / FORBIDDEN_METHODS / SOURCE_WHITELIST_PROPOSAL
  - TRANSFORMATION_RULES / FRESHNESS_RULES / PROVENANCE_RULES
  - MISSING_KIND_FIELDS / NEXT_REQUIRED_ACTION
  - get_data_acquisition_plan_label()
  - evaluate_acquisition_plan_entry(entry)
  - record_data_acquisition_plan(template_guide)
  - build_data_acquisition_plan()
  - validate_data_acquisition_plan(plan)
  - render_data_acquisition_plan_markdown(plan)
"""

from __future__ import annotations

import copy
from typing import Any

from sparta_commander.arbitrage_data_contract import (
    FORBIDDEN_FIELD_TOKENS,
    STAGED_DATASET_SPECS,
)
from sparta_commander.arbitrage_staged_data_csv_template_guide_contract import (
    VERDICT_TEMPLATE_GUIDE_READY,
    build_csv_template_guide,
    validate_csv_template_guide,
)

ACQ_SCHEMA_VERSION = "arbitrage_read_only_data_acquisition_plan_contract.v1"
ACQ_LABEL = (
    "SPARTA Arbitrage Factory V1 Read-Only Data Acquisition Plan "
    "(READ-ONLY, PLAN ONLY, FETCHES NOTHING)"
)
ACQ_MODE = "RESEARCH_ONLY"

VERDICT_ACQ_PLAN_READY = "ARBITRAGE_DATA_ACQUISITION_PLAN_READY"
VERDICT_ACQ_PLAN_BLOCKED = "ARBITRAGE_DATA_ACQUISITION_PLAN_BLOCKED"
VERDICT_PLAN_ENTRY_ACCEPTED = "ACQUISITION_PLAN_ENTRY_ACCEPTED"
VERDICT_PLAN_ENTRY_REFUSED = "ACQUISITION_PLAN_ENTRY_REFUSED"

NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_SOURCE_WHITELIST_PROPOSAL"

ALLOWED_METHODS: dict[str, dict[str, Any]] = {
    "manual_export_from_venue_public_page": {
        "allowed_now": True,
        "description": "a human reads a venue's PUBLIC page and types/copies "
                       "the numbers into the staged CSV template by hand",
    },
    "public_csv_download_no_auth": {
        "allowed_now": True,
        "description": "a human downloads a publicly linked file that needs "
                       "no login, no key, no account -- then hand-maps it",
    },
    "public_webpage_snapshot_manual": {
        "allowed_now": True,
        "description": "a human records publicly displayed quotes/fees/depth "
                       "numbers at a moment in time, with the timestamp",
    },
    "future_no_auth_public_endpoint": {
        "allowed_now": False,
        "description": "a future read-only no-auth public endpoint adapter; "
                       "NOT allowed now -- it would require its own separate "
                       "human-approved contract before any software touches "
                       "a network",
    },
}

FORBIDDEN_METHODS = (
    "authenticated_or_keyed_api_of_any_kind",
    "exchange_account_statements_or_trade_history_exports",
    "wallet_order_fill_or_position_data_in_any_form",
    "private_keys_session_tokens_or_login_protected_pages",
    "paid_private_feeds_or_signal_groups",
    "any_method_where_software_touches_a_network_without_its_own_approval",
)

# Required fields per missing kind, imported from the seq-2 single source.
MISSING_KIND_FIELDS: dict[str, tuple[str, ...]] = {
    kind: STAGED_DATASET_SPECS[kind]["required_columns"]
    for kind in ("funding_rates", "spot_perp_basis", "cross_exchange_quotes",
                 "liquidity_depth", "fee_schedule")
}

# Source whitelist PROPOSAL: every entry is PROPOSED, none is approved here.
SOURCE_WHITELIST_PROPOSAL = (
    {"kind": "funding_rates",
     "proposed_sources": "venue public funding-rate history pages "
                         "(binance/bybit/okx public, no login)",
     "status": "PROPOSED_FOR_HUMAN_REVIEW"},
    {"kind": "spot_perp_basis",
     "proposed_sources": "venue public spot and perp price pages sampled at "
                         "the same instant; public market-data aggregator "
                         "pages with no login",
     "status": "PROPOSED_FOR_HUMAN_REVIEW"},
    {"kind": "cross_exchange_quotes",
     "proposed_sources": "venue public order-book/top-of-book pages across "
                         "the five allowed venue labels",
     "status": "PROPOSED_FOR_HUMAN_REVIEW"},
    {"kind": "liquidity_depth",
     "proposed_sources": "venue public depth charts/order-book pages; depth "
                         "within 10 bps recorded by hand with timestamp",
     "status": "PROPOSED_FOR_HUMAN_REVIEW"},
    {"kind": "fee_schedule",
     "proposed_sources": "venue public fee pages (plus the existing reviewed "
                         "Kraken fees.json transcribed by hand, withdrawal "
                         "fees added from the public page)",
     "status": "PROPOSED_FOR_HUMAN_REVIEW"},
)

TRANSFORMATION_RULES = (
    "acquired_numbers_are_hand_mapped_into_the_exact_template_headers",
    "timestamps_converted_to_utc_iso8601_with_explicit_marker_before_staging",
    "symbols_and_venues_renamed_to_the_allowed_labels_only",
    "fees_expressed_as_decimal_fractions_not_percent_strings",
    "no_field_outside_the_template_header_is_ever_added",
    "every_transformed_file_must_pass_the_staging_manifest_pre_check",
)

FRESHNESS_RULES = (
    "quotes_and_depth_should_be_at_most_7_days_old_when_staged",
    "funding_and_basis_should_be_at_most_30_days_old_when_staged",
    "fee_schedules_must_be_re_checked_against_the_public_page_monthly",
    "anything_older_than_30_days_needs_explicit_stale_acknowledgement",
)

PROVENANCE_RULES = (
    "every_staged_file_gets_a_source_label_naming_the_public_page_and_date",
    "the_source_label_must_assert_no_login_no_key_no_account_was_used",
    "provenance_lives_in_the_staging_manifest_never_inside_the_csv_rows",
)

_FORBIDDEN_PLAN_TOKENS = FORBIDDEN_FIELD_TOKENS + (
    # "no login" is the GOOD assertion, so only login-gated phrasings ban.
    "behind my login", "behind a login", "logged-in", "signed request",
    "private feed", "signal group", "statement",
)


def get_data_acquisition_plan_label() -> str:
    """Human label for the recognized data acquisition plan contract."""
    return ACQ_LABEL


def evaluate_acquisition_plan_entry(entry: Any) -> dict[str, Any]:
    """Evaluate (pure, in-memory) ONE proposed acquisition plan entry:
    {kind, method, source_description, uses_auth?}. Fetches nothing.
    Never raises. Returns {"verdict": ..., "errors": [...]}."""
    errors: list[str] = []
    if not isinstance(entry, dict):
        return {"verdict": VERDICT_PLAN_ENTRY_REFUSED,
                "errors": ["entry_not_a_dict"]}

    kind = entry.get("kind")
    if kind not in MISSING_KIND_FIELDS:
        errors.append("kind_not_an_arbitrage_dataset:" + str(kind))

    method = entry.get("method")
    if method not in ALLOWED_METHODS:
        errors.append("method_not_in_allowed_set:" + str(method))
    elif ALLOWED_METHODS[method]["allowed_now"] is not True:
        errors.append("method_not_allowed_yet_needs_its_own_contract:" + str(method))

    if entry.get("uses_auth") is True:
        errors.append("entry_declares_authentication_refused_outright")

    source = str(entry.get("source_description", "")).strip()
    if not source:
        errors.append("source_description_missing")
    else:
        lowered = source.lower()
        for token in _FORBIDDEN_PLAN_TOKENS:
            if token in lowered:
                errors.append("forbidden_source_token:" + token)

    if errors:
        return {"verdict": VERDICT_PLAN_ENTRY_REFUSED, "errors": errors}
    return {"verdict": VERDICT_PLAN_ENTRY_ACCEPTED, "errors": []}


def _base_plan() -> dict[str, Any]:
    return {
        "schema_version": ACQ_SCHEMA_VERSION,
        "label": ACQ_LABEL,
        "mode": ACQ_MODE,
        "lane": "arbitrage_factory_v1",
        "verdict": None,
        "blockers": [],
        "template_guide_verdict": None,
        "allowed_methods": copy.deepcopy(ALLOWED_METHODS),
        "forbidden_methods": list(FORBIDDEN_METHODS),
        "missing_kind_fields": {
            kind: list(fields) for kind, fields in MISSING_KIND_FIELDS.items()
        },
        "source_whitelist_proposal": [dict(s) for s in SOURCE_WHITELIST_PROPOSAL],
        "transformation_rules": list(TRANSFORMATION_RULES),
        "freshness_rules": list(FRESHNESS_RULES),
        "provenance_rules": list(PROVENANCE_RULES),
        # Constitution, stated structurally:
        "plan_fetches_nothing": True,
        "whitelist_is_a_proposal_not_an_approval": True,
        "data_describes_markets_never_accounts": True,
        "no_software_touches_a_network_under_this_plan": True,
        "scanner_remains_blocked": True,
        "human_review_required": True,
        # Capability posture:
        "executes": False,
        "writes_files": False,
        "writes_reports": False,
        "sends_notifications": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "starts_scheduler": False,
        "starts_daemon": False,
        "starts_background_worker": False,
        "runs_loop": False,
        "fetches_data": False,
        "calls_api": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "contains_order_logic": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNTOUCHED):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def record_data_acquisition_plan(template_guide: Any) -> dict[str, Any]:
    """Record the acquisition plan, gated on a READY, valid CSV template
    guide. PURE: never raises, fetches nothing, writes nothing."""
    plan = _base_plan()

    if not isinstance(template_guide, dict):
        plan["verdict"] = VERDICT_ACQ_PLAN_BLOCKED
        plan["blockers"].append("template_guide_missing")
        return plan

    validation = validate_csv_template_guide(template_guide)
    if not validation.get("valid"):
        plan["verdict"] = VERDICT_ACQ_PLAN_BLOCKED
        plan["blockers"].append("template_guide_invalid")
        return plan

    if template_guide.get("verdict") != VERDICT_TEMPLATE_GUIDE_READY:
        plan["verdict"] = VERDICT_ACQ_PLAN_BLOCKED
        plan["blockers"].append("template_guide_not_ready")
        return plan

    plan["verdict"] = VERDICT_ACQ_PLAN_READY
    plan["template_guide_verdict"] = template_guide.get("verdict")
    return plan


def build_data_acquisition_plan() -> dict[str, Any]:
    """Build the plan against the real chain. Pure."""
    return record_data_acquisition_plan(build_csv_template_guide())


def validate_data_acquisition_plan(plan: Any) -> dict[str, Any]:
    """Validate (read-only) the plan's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return {"valid": False, "errors": ["plan_not_a_dict"]}
    p = plan

    verdict = p.get("verdict")
    if verdict not in (VERDICT_ACQ_PLAN_READY, VERDICT_ACQ_PLAN_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_ACQ_PLAN_BLOCKED and not p.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_ACQ_PLAN_READY:
        if p.get("blockers"):
            errors.append("ready_with_blockers")
        if p.get("template_guide_verdict") != VERDICT_TEMPLATE_GUIDE_READY:
            errors.append("ready_without_ready_template_guide")

    if p.get("lane") != "arbitrage_factory_v1":
        errors.append("wrong_lane")

    methods = p.get("allowed_methods")
    if not isinstance(methods, dict) or set(methods) != set(ALLOWED_METHODS):
        errors.append("allowed_methods_tampered")
    elif methods.get("future_no_auth_public_endpoint", {}).get(
        "allowed_now"
    ) is not False:
        errors.append("future_endpoint_enabled_without_its_own_contract")
    if tuple(p.get("forbidden_methods") or ()) != FORBIDDEN_METHODS:
        errors.append("forbidden_methods_weakened")

    expected_fields = {
        kind: list(fields) for kind, fields in MISSING_KIND_FIELDS.items()
    }
    if p.get("missing_kind_fields") != expected_fields:
        errors.append("kind_fields_diverge_from_data_contract")

    whitelist = p.get("source_whitelist_proposal") or []
    if len(whitelist) != len(SOURCE_WHITELIST_PROPOSAL):
        errors.append("whitelist_incomplete")
    elif any(s.get("status") != "PROPOSED_FOR_HUMAN_REVIEW" for s in whitelist):
        errors.append("whitelist_entry_claims_approval")

    for name, expected in (("transformation_rules", TRANSFORMATION_RULES),
                           ("freshness_rules", FRESHNESS_RULES),
                           ("provenance_rules", PROVENANCE_RULES)):
        if tuple(p.get(name) or ()) != expected:
            errors.append(name + "_tampered")

    for key, err in (
        ("plan_fetches_nothing", "plan_claims_to_fetch"),
        ("whitelist_is_a_proposal_not_an_approval", "whitelist_claims_approval"),
        ("data_describes_markets_never_accounts", "account_data_allowed"),
        ("no_software_touches_a_network_under_this_plan", "network_allowed"),
        ("scanner_remains_blocked", "scanner_block_dropped"),
        ("human_review_required", "human_review_dropped"),
    ):
        if p.get(key) is not True:
            errors.append(err)

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if p.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "writes_reports",
        "sends_notifications",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "starts_scheduler",
        "starts_daemon",
        "starts_background_worker",
        "runs_loop",
        "fetches_data",
        "calls_api",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "contains_order_logic",
        "authorizes_paper_execution",
        "authorizes_micro_live",
        "authorizes_live_trading",
        "promotes_gate",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if p.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_data_acquisition_plan_markdown(plan: Any) -> str:
    """Render the plan as deterministic markdown. Pure string work."""
    p = plan if isinstance(plan, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Arbitrage Factory V1 Read-Only Data Acquisition Plan")
    lines.append("")
    lines.append("- Verdict: " + str(p.get("verdict", "")))
    lines.append("- This plan FETCHES NOTHING; humans acquire public data by hand")
    lines.append("- The source whitelist is a PROPOSAL, not an approval")
    lines.append("- The scanner remains BLOCKED")
    lines.append("- Next required action: " + str(p.get("next_required_action", "")))
    lines.append("")
    blockers = p.get("blockers") or []
    if blockers:
        lines.append("## Blockers (BLOCKED defines nothing usable)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
        return "\n".join(lines)
    lines.append("## Allowed methods")
    for name, method in (p.get("allowed_methods") or {}).items():
        tag = "ALLOWED NOW" if method.get("allowed_now") else "NOT YET (own contract)"
        lines.append("- " + str(name) + " [" + tag + "]: "
                     + str(method.get("description")))
    lines.append("")
    lines.append("## Forbidden methods (refused outright)")
    for f in p.get("forbidden_methods") or []:
        lines.append("- " + str(f))
    lines.append("")
    lines.append("## Source whitelist PROPOSAL (for human review)")
    for s in p.get("source_whitelist_proposal") or []:
        lines.append("- " + str(s.get("kind")) + ": " + str(s.get("proposed_sources"))
                     + " [" + str(s.get("status")) + "]")
    lines.append("")
    lines.append("## Transformation / freshness / provenance rules")
    for name in ("transformation_rules", "freshness_rules", "provenance_rules"):
        for r in p.get(name) or []:
            lines.append("- " + str(r))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)

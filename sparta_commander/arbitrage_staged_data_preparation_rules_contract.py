"""SPARTA Arbitrage Factory V1 - STAGED-DATA PREPARATION RULES (READ-ONLY).

The operator runbook layer over the seq-2 data contract: HOW manually staged
market data must be prepared BEFORE any future scanner could ever read it.
The scanner is still BLOCKED; no staged data exists yet; this contract defines
the rules and validates IN-MEMORY MANIFESTS only -- a manifest is the
operator's *description* of files they intend to stage (filenames, kinds,
columns, timestamp ranges). NO FILE IS EVER READ by this module.

The rules:
  - Exactly one allowed folder: data/arbitrage_factory_v1/staged/ -- staged
    by a human operator's own hands. No fetch, no API, no connector, ever.
  - Exactly five dataset kinds (from the seq-2 contract), each with an exact
    filename pattern carrying the symbol/venue LABELS:
        funding_rates         funding_{symbol}_{venue}.csv
        spot_perp_basis       basis_{symbol}_{venue}.csv
        cross_exchange_quotes quotes_{symbol}_{venue}.csv
        fee_schedule          fees_{venue}.csv
        liquidity_depth       depth_{symbol}_{venue}.csv
  - Required columns per kind aligned (imported, not copied) from the seq-2
    data contract; account/credential/order/position fields refuse the WHOLE
    manifest entry via the same forbidden-token screen.
  - Timestamps: UTC ISO-8601 with explicit UTC marker (Z or +00:00) only.
  - Stale data (older than the research staleness window) must be explicitly
    acknowledged in the manifest -- never silently accepted.
  - Duplicate filenames refuse; unknown symbols/venues refuse; kinds not yet
    staged are reported as missing (the manifest can be accepted while
    incomplete, but it is never complete-for-scanner until all kinds exist).

Output is READINESS ONLY -- an accepted manifest means "these files, if placed
exactly as described, would satisfy the data contract." It is never a scan
result, never an authorization, and the scanner build stays BLOCKED.

Public API:
  - PREP_SCHEMA_VERSION / PREP_LABEL / PREP_MODE
  - VERDICT_PREP_RULES_READY / VERDICT_PREP_RULES_BLOCKED
  - VERDICT_MANIFEST_ACCEPTED / VERDICT_MANIFEST_REFUSED
  - STAGING_FOLDER / FILENAME_PATTERNS / PREPARATION_RULES
  - MAX_STALENESS_DAYS / NEXT_REQUIRED_ACTION
  - get_staged_data_preparation_rules_label()
  - record_staged_data_preparation_rules(data_contract)
  - build_staged_data_preparation_rules()
  - validate_staged_data_preparation_rules(contract)
  - validate_staged_file_name(filename)
  - validate_staging_manifest(manifest)
  - render_staged_data_preparation_rules_markdown(contract)
"""

from __future__ import annotations

import copy
import datetime as _dt
from typing import Any

from sparta_commander.arbitrage_data_contract import (
    ALLOWED_SYMBOLS,
    ALLOWED_VENUE_LABELS,
    MAX_STALENESS_DAYS_FOR_RESEARCH,
    STAGED_DATASET_SPECS,
    STAGING_ROOT,
    VERDICT_DATA_CONTRACT_READY,
    build_arbitrage_data_contract,
    validate_arbitrage_data_contract,
    validate_staged_dataset_descriptor,
)

PREP_SCHEMA_VERSION = "arbitrage_staged_data_preparation_rules_contract.v1"
PREP_LABEL = (
    "SPARTA Arbitrage Factory V1 Staged-Data Preparation Rules "
    "(READ-ONLY, RULES ONLY)"
)
PREP_MODE = "RESEARCH_ONLY"

VERDICT_PREP_RULES_READY = "ARBITRAGE_STAGED_DATA_PREP_RULES_READY"
VERDICT_PREP_RULES_BLOCKED = "ARBITRAGE_STAGED_DATA_PREP_RULES_BLOCKED"
VERDICT_MANIFEST_ACCEPTED = "STAGING_MANIFEST_ACCEPTED"
VERDICT_MANIFEST_REFUSED = "STAGING_MANIFEST_REFUSED"

# After the rules exist, the only next step is a HUMAN physically placing
# files; nothing in software moves.
NEXT_REQUIRED_ACTION = "HUMAN_PLACES_STAGED_DATA_MANUALLY"

STAGING_FOLDER = STAGING_ROOT  # data/arbitrage_factory_v1/staged/
MAX_STALENESS_DAYS = MAX_STALENESS_DAYS_FOR_RESEARCH

# filename prefix/shape per kind; labels are validated against the allowed
# symbol/venue lists. fee_schedule is per-venue only (no symbol in the name).
FILENAME_PATTERNS: dict[str, dict[str, Any]] = {
    "funding_rates": {"prefix": "funding", "has_symbol": True},
    "spot_perp_basis": {"prefix": "basis", "has_symbol": True},
    "cross_exchange_quotes": {"prefix": "quotes", "has_symbol": True},
    "fee_schedule": {"prefix": "fees", "has_symbol": False},
    "liquidity_depth": {"prefix": "depth", "has_symbol": True},
}
assert set(FILENAME_PATTERNS) == set(STAGED_DATASET_SPECS)

PREPARATION_RULES = (
    "files_live_only_under_data_arbitrage_factory_v1_staged",
    "files_are_placed_by_a_human_operator_no_fetch_no_api_no_connector",
    "filenames_must_match_the_exact_kind_pattern_with_allowed_labels_only",
    "timestamps_must_be_utc_iso8601_with_an_explicit_utc_marker",
    "stale_data_must_be_explicitly_acknowledged_never_silently_accepted",
    "duplicate_filenames_refuse_the_whole_manifest",
    "missing_kinds_are_reported_the_manifest_is_never_complete_until_all_exist",
    "forbidden_account_credential_order_position_fields_refuse_the_entry",
    "an_accepted_manifest_is_readiness_only_never_a_scan_result",
)


def get_staged_data_preparation_rules_label() -> str:
    """Human label for the recognized staged-data preparation rules contract."""
    return PREP_LABEL


def validate_staged_file_name(filename: Any) -> dict[str, Any]:
    """Validate (pure, in-memory) ONE proposed staged filename against the
    kind patterns and allowed labels. Reads nothing. Never raises.
    Returns {"acceptable": bool, "kind": str|None, "errors": [...]}."""
    if not isinstance(filename, str) or not filename:
        return {"acceptable": False, "kind": None,
                "errors": ["filename_missing_or_not_a_string"]}
    name = filename.strip()
    if "/" in name or "\\" in name or ".." in name:
        return {"acceptable": False, "kind": None,
                "errors": ["filename_must_be_a_bare_name_inside_the_staging_folder"]}
    if not name.endswith(".csv"):
        return {"acceptable": False, "kind": None,
                "errors": ["filename_must_end_with_csv"]}

    stem = name[: -len(".csv")]
    parts = stem.split("_")
    prefix = parts[0] if parts else ""
    for kind, pattern in FILENAME_PATTERNS.items():
        if pattern["prefix"] != prefix:
            continue
        if pattern["has_symbol"]:
            if len(parts) != 3:
                return {"acceptable": False, "kind": kind,
                        "errors": ["filename_shape_must_be_" + prefix
                                   + "_symbol_venue.csv"]}
            symbol, venue = parts[1].upper(), parts[2].lower()
            errors = []
            if symbol not in ALLOWED_SYMBOLS:
                errors.append("symbol_not_in_allowed_labels:" + parts[1])
            if venue not in ALLOWED_VENUE_LABELS:
                errors.append("venue_not_in_allowed_labels:" + parts[2])
            return {"acceptable": not errors, "kind": kind, "errors": errors}
        if len(parts) != 2:
            return {"acceptable": False, "kind": kind,
                    "errors": ["filename_shape_must_be_" + prefix + "_venue.csv"]}
        venue = parts[1].lower()
        if venue not in ALLOWED_VENUE_LABELS:
            return {"acceptable": False, "kind": kind,
                    "errors": ["venue_not_in_allowed_labels:" + parts[1]]}
        return {"acceptable": True, "kind": kind, "errors": []}

    return {"acceptable": False, "kind": None,
            "errors": ["filename_prefix_matches_no_dataset_kind:" + prefix]}


def _parse_utc(value: Any) -> _dt.datetime | None:
    """Parse a UTC ISO-8601 timestamp with an explicit UTC marker, else None."""
    if not isinstance(value, str):
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    if not text.endswith("+00:00"):
        return None
    try:
        parsed = _dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    return parsed


def validate_staging_manifest(manifest: Any) -> dict[str, Any]:
    """Validate (pure, in-memory) an operator's STAGING MANIFEST: a dict with
    'prepared_as_of_utc' and 'entries' (each entry: filename, kind, columns,
    first_timestamp_utc, last_timestamp_utc, optional stale_acknowledged).
    NO FILE IS READ. Never raises. Returns a result dict with the manifest
    verdict, per-entry errors, missing kinds, and completeness."""
    result: dict[str, Any] = {
        "verdict": None,
        "errors": [],
        "entry_errors": {},
        "kinds_covered": [],
        "missing_kinds": [],
        "manifest_complete_for_all_kinds": False,
        "acceptance_is_readiness_only_never_a_scan_result": True,
        "no_file_was_read": True,
    }

    if not isinstance(manifest, dict):
        result["verdict"] = VERDICT_MANIFEST_REFUSED
        result["errors"].append("manifest_not_a_dict")
        return result

    as_of = _parse_utc(manifest.get("prepared_as_of_utc"))
    if as_of is None:
        result["verdict"] = VERDICT_MANIFEST_REFUSED
        result["errors"].append("prepared_as_of_utc_missing_or_not_utc_iso8601")
        return result

    entries = manifest.get("entries")
    if not isinstance(entries, list) or not entries:
        result["verdict"] = VERDICT_MANIFEST_REFUSED
        result["errors"].append("entries_missing_or_empty")
        return result

    seen_names: set[str] = set()
    kinds_covered: set[str] = set()
    for i, entry in enumerate(entries):
        entry_errors: list[str] = []
        if not isinstance(entry, dict):
            result["entry_errors"]["entry_" + str(i)] = ["entry_not_a_dict"]
            continue
        filename = str(entry.get("filename", ""))

        if filename in seen_names:
            entry_errors.append("duplicate_filename_in_manifest")
        seen_names.add(filename)

        name_check = validate_staged_file_name(filename)
        entry_errors.extend(name_check["errors"])
        kind = entry.get("kind")
        if name_check["kind"] is not None and kind != name_check["kind"]:
            entry_errors.append("declared_kind_does_not_match_filename_pattern")

        if kind in STAGED_DATASET_SPECS:
            desc = validate_staged_dataset_descriptor(kind, entry.get("columns"))
            entry_errors.extend(desc["errors"])
        else:
            entry_errors.append("unknown_dataset_kind:" + str(kind))

        # fee_schedule is a reference table; the others carry timestamps.
        if kind != "fee_schedule":
            first = _parse_utc(entry.get("first_timestamp_utc"))
            last = _parse_utc(entry.get("last_timestamp_utc"))
            if first is None or last is None:
                entry_errors.append("timestamps_missing_or_not_utc_iso8601")
            elif last < first:
                entry_errors.append("last_timestamp_before_first")
            else:
                age_days = (as_of - last).days
                if age_days > MAX_STALENESS_DAYS and entry.get(
                    "stale_acknowledged"
                ) is not True:
                    entry_errors.append(
                        "stale_data_not_acknowledged_age_days_" + str(age_days))

        if entry_errors:
            result["entry_errors"][filename or ("entry_" + str(i))] = entry_errors
        elif kind in STAGED_DATASET_SPECS:
            kinds_covered.add(kind)

    result["kinds_covered"] = sorted(kinds_covered)
    result["missing_kinds"] = sorted(set(STAGED_DATASET_SPECS) - kinds_covered)
    result["manifest_complete_for_all_kinds"] = not result["missing_kinds"]

    if result["entry_errors"]:
        result["verdict"] = VERDICT_MANIFEST_REFUSED
        result["errors"].append("one_or_more_entries_refused")
    else:
        result["verdict"] = VERDICT_MANIFEST_ACCEPTED
    return result


def _base_contract() -> dict[str, Any]:
    return {
        "schema_version": PREP_SCHEMA_VERSION,
        "label": PREP_LABEL,
        "mode": PREP_MODE,
        "lane": "arbitrage_factory_v1",
        "verdict": None,
        "blockers": [],
        "data_contract_verdict": None,
        "staging_folder": STAGING_FOLDER,
        "filename_patterns": copy.deepcopy(FILENAME_PATTERNS),
        "dataset_kinds": sorted(STAGED_DATASET_SPECS),
        "required_columns_by_kind": {
            kind: list(spec["required_columns"])
            for kind, spec in STAGED_DATASET_SPECS.items()
        },
        "allowed_symbols": list(ALLOWED_SYMBOLS),
        "allowed_venue_labels": list(ALLOWED_VENUE_LABELS),
        "preparation_rules": list(PREPARATION_RULES),
        "max_staleness_days": MAX_STALENESS_DAYS,
        # Constitution, stated structurally:
        "operator_staged_only_no_fetch_no_api_no_connector": True,
        "scanner_remains_blocked": True,
        "rules_read_no_files": True,
        "output_is_readiness_only_never_a_scan_result": True,
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


def record_staged_data_preparation_rules(data_contract: Any) -> dict[str, Any]:
    """Record the preparation rules, gated on a READY, valid seq-2 data
    contract. PURE: never raises, reads no file, connects to nothing."""
    contract = _base_contract()

    if not isinstance(data_contract, dict):
        contract["verdict"] = VERDICT_PREP_RULES_BLOCKED
        contract["blockers"].append("data_contract_missing")
        return contract

    validation = validate_arbitrage_data_contract(data_contract)
    if not validation.get("valid"):
        contract["verdict"] = VERDICT_PREP_RULES_BLOCKED
        contract["blockers"].append("data_contract_invalid")
        return contract

    if data_contract.get("verdict") != VERDICT_DATA_CONTRACT_READY:
        contract["verdict"] = VERDICT_PREP_RULES_BLOCKED
        contract["blockers"].append("data_contract_not_ready")
        return contract

    contract["verdict"] = VERDICT_PREP_RULES_READY
    contract["data_contract_verdict"] = data_contract.get("verdict")
    return contract


def build_staged_data_preparation_rules() -> dict[str, Any]:
    """Build the rules against the real seq 0 -> 1 -> 2 chain. Pure."""
    return record_staged_data_preparation_rules(build_arbitrage_data_contract())


def validate_staged_data_preparation_rules(contract: Any) -> dict[str, Any]:
    """Validate (read-only) the rules contract's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(contract, dict):
        return {"valid": False, "errors": ["contract_not_a_dict"]}
    c = contract

    verdict = c.get("verdict")
    if verdict not in (VERDICT_PREP_RULES_READY, VERDICT_PREP_RULES_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_PREP_RULES_BLOCKED and not c.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_PREP_RULES_READY:
        if c.get("blockers"):
            errors.append("ready_with_blockers")
        if c.get("data_contract_verdict") != VERDICT_DATA_CONTRACT_READY:
            errors.append("ready_without_ready_data_contract")

    if c.get("lane") != "arbitrage_factory_v1":
        errors.append("wrong_lane")
    if c.get("staging_folder") != STAGING_FOLDER:
        errors.append("staging_folder_moved")
    if sorted(c.get("dataset_kinds") or []) != sorted(STAGED_DATASET_SPECS):
        errors.append("dataset_kinds_tampered")
    expected_cols = {
        kind: list(spec["required_columns"])
        for kind, spec in STAGED_DATASET_SPECS.items()
    }
    if c.get("required_columns_by_kind") != expected_cols:
        errors.append("required_columns_diverge_from_data_contract")
    if tuple(c.get("allowed_symbols") or ()) != ALLOWED_SYMBOLS:
        errors.append("symbols_tampered")
    if tuple(c.get("allowed_venue_labels") or ()) != ALLOWED_VENUE_LABELS:
        errors.append("venues_tampered")
    if tuple(c.get("preparation_rules") or ()) != PREPARATION_RULES:
        errors.append("preparation_rules_tampered")
    if c.get("max_staleness_days") != MAX_STALENESS_DAYS:
        errors.append("staleness_rule_tampered")
    if c.get("filename_patterns") != FILENAME_PATTERNS:
        errors.append("filename_patterns_tampered")

    for key, err in (
        ("operator_staged_only_no_fetch_no_api_no_connector",
         "operator_only_rule_dropped"),
        ("scanner_remains_blocked", "scanner_block_dropped"),
        ("rules_read_no_files", "rules_read_files"),
        ("output_is_readiness_only_never_a_scan_result", "scan_result_claimed"),
        ("human_review_required", "human_review_dropped"),
    ):
        if c.get(key) is not True:
            errors.append(err)

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if c.get(key) is not True:
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
        if c.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_staged_data_preparation_rules_markdown(contract: Any) -> str:
    """Render the rules contract as deterministic markdown. Pure string work."""
    c = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Arbitrage Factory V1 Staged-Data Preparation Rules")
    lines.append("")
    lines.append("- Verdict: " + str(c.get("verdict", "")))
    lines.append("- Folder: " + str(c.get("staging_folder")))
    lines.append("- Operator-staged only: no fetch, no API, no connector, ever")
    lines.append("- The scanner remains BLOCKED; acceptance is readiness only")
    lines.append("- Next required action: " + str(c.get("next_required_action", "")))
    lines.append("")
    blockers = c.get("blockers") or []
    if blockers:
        lines.append("## Blockers (BLOCKED defines nothing usable)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    lines.append("## Filename patterns")
    for kind, pattern in (c.get("filename_patterns") or {}).items():
        shape = (pattern["prefix"] + "_{symbol}_{venue}.csv"
                 if pattern.get("has_symbol")
                 else pattern["prefix"] + "_{venue}.csv")
        lines.append("- " + str(kind) + ": " + shape)
    lines.append("")
    lines.append("## Preparation rules")
    for r in c.get("preparation_rules") or []:
        lines.append("- " + str(r))
    lines.append("")
    lines.append("## Required columns by kind (aligned to the seq-2 contract)")
    for kind, cols in (c.get("required_columns_by_kind") or {}).items():
        lines.append("- " + str(kind) + ": " + ", ".join(cols))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)

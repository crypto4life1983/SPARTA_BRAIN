"""SPARTA Arbitrage Factory V1 - STAGED-DATA CSV TEMPLATE GUIDE (READ-ONLY).

The practical companion to the preparation rules: EXACT, copy-paste-ready CSV
templates for every file the human operator will place by hand under

    data/arbitrage_factory_v1/staged/

One template per dataset kind: the exact filename shape, the exact header line
(byte-for-byte the seq-2 required columns), two illustrative sample rows using
only allowed labels and obviously-safe market values, and the operator notes
that matter for that kind.

Templates are IN-MEMORY STRINGS. This module writes no file, creates no
folder, and reads nothing -- the operator copies the template text into a file
themselves, fills it with manually exported market data from their own
sources, and places it by hand. Every template is self-consistent with the
lane's own rules: the validator checks that each template's header matches the
seq-2 required columns exactly, that each example filename passes the
prep-rules filename validator, and that each sample row has exactly as many
fields as the header. Sample values are illustrative placeholders, never real
market claims.

Public API:
  - GUIDE_SCHEMA_VERSION / GUIDE_LABEL / GUIDE_MODE
  - VERDICT_TEMPLATE_GUIDE_READY / VERDICT_TEMPLATE_GUIDE_BLOCKED
  - CSV_TEMPLATES / PLACEMENT_CHECKLIST / NEXT_REQUIRED_ACTION
  - get_csv_template_guide_label()
  - get_csv_template(kind)
  - record_csv_template_guide(prep_rules)
  - build_csv_template_guide()
  - validate_csv_template_guide(guide)
  - render_csv_template_guide_markdown(guide)
"""

from __future__ import annotations

import copy
from typing import Any

from sparta_commander.arbitrage_data_contract import (
    STAGED_DATASET_SPECS,
    STAGING_ROOT,
)
from sparta_commander.arbitrage_staged_data_preparation_rules_contract import (
    VERDICT_PREP_RULES_READY,
    build_staged_data_preparation_rules,
    validate_staged_data_preparation_rules,
    validate_staged_file_name,
)

GUIDE_SCHEMA_VERSION = "arbitrage_staged_data_csv_template_guide_contract.v1"
GUIDE_LABEL = (
    "SPARTA Arbitrage Factory V1 Staged-Data CSV Template Guide "
    "(READ-ONLY, TEMPLATES ONLY)"
)
GUIDE_MODE = "RESEARCH_ONLY"

VERDICT_TEMPLATE_GUIDE_READY = "ARBITRAGE_CSV_TEMPLATE_GUIDE_READY"
VERDICT_TEMPLATE_GUIDE_BLOCKED = "ARBITRAGE_CSV_TEMPLATE_GUIDE_BLOCKED"

# The guide changes nothing about the next step: a human places files by hand.
NEXT_REQUIRED_ACTION = "HUMAN_PLACES_STAGED_DATA_MANUALLY"

# One template per dataset kind. Headers are derived from the seq-2 specs (the
# single source of truth); sample rows are illustrative placeholders only.
CSV_TEMPLATES: dict[str, dict[str, Any]] = {
    "funding_rates": {
        "filename_example": "funding_BTC_binance.csv",
        "header": ",".join(
            STAGED_DATASET_SPECS["funding_rates"]["required_columns"]),
        "sample_rows": (
            "2026-06-08T00:00:00Z,BTC,binance,0.000100,67250.50",
            "2026-06-08T08:00:00Z,BTC,binance,0.000085,67310.25",
        ),
        "notes": (
            "one row per funding interval; funding_rate_8h is the realized "
            "per-interval rate as a decimal fraction; mark_price in quote "
            "currency; export manually from your own venue statements"
        ),
    },
    "spot_perp_basis": {
        "filename_example": "basis_ETH_bybit.csv",
        "header": ",".join(
            STAGED_DATASET_SPECS["spot_perp_basis"]["required_columns"]),
        "sample_rows": (
            "2026-06-08T00:00:00Z,ETH,bybit,3520.10,3524.60,0.1278",
            "2026-06-08T01:00:00Z,ETH,bybit,3518.75,3522.40,0.1037",
        ),
        "notes": (
            "basis_pct = (perp_price - spot_price) / spot_price * 100; sample "
            "the two prices at the same instant; hourly or better is typical"
        ),
    },
    "cross_exchange_quotes": {
        "filename_example": "quotes_SOL_okx.csv",
        "header": ",".join(
            STAGED_DATASET_SPECS["cross_exchange_quotes"]["required_columns"]),
        "sample_rows": (
            "2026-06-08T00:00:00Z,SOL,okx,148.21,148.27,148.24",
            "2026-06-08T00:01:00Z,SOL,okx,148.18,148.25,148.215",
        ),
        "notes": (
            "top-of-book bid/ask plus mid; one file per symbol/venue; pair "
            "files across venues must share the timestamp grid for spreads"
        ),
    },
    "fee_schedule": {
        "filename_example": "fees_kraken.csv",
        "header": ",".join(
            STAGED_DATASET_SPECS["fee_schedule"]["required_columns"]),
        "sample_rows": (
            "kraken,BTC,0.0026,0.0016,0.00002",
            "kraken,ETH,0.0026,0.0016,0.001",
        ),
        "notes": (
            "reference table, no timestamps; fees as decimal fractions "
            "(0.0026 = 26 bps taker); withdrawal_flat_fee in units of the "
            "symbol; copy from the venue's public fee page by hand"
        ),
    },
    "liquidity_depth": {
        "filename_example": "depth_BTC_coinbase.csv",
        "header": ",".join(
            STAGED_DATASET_SPECS["liquidity_depth"]["required_columns"]),
        "sample_rows": (
            "2026-06-08T00:00:00Z,BTC,coinbase,250000.00,240000.00,1.8",
            "2026-06-08T01:00:00Z,BTC,coinbase,262500.00,251000.00,1.6",
        ),
        "notes": (
            "bid/ask depth in USD within 10 bps of mid; spread_bps is the "
            "quoted spread in basis points; the seq-3 model caps any "
            "evaluation at 10% of this depth"
        ),
    },
}

PLACEMENT_CHECKLIST = (
    "create_the_folder_data_arbitrage_factory_v1_staged_by_hand_if_absent",
    "copy_the_template_header_exactly_no_extra_no_missing_no_reordered_columns",
    "fill_rows_from_manually_exported_market_data_from_your_own_sources",
    "use_only_allowed_symbol_and_venue_labels_in_filenames_and_rows",
    "timestamps_utc_iso8601_with_explicit_utc_marker_only",
    "never_include_account_credential_balance_order_or_position_columns",
    "pre_check_your_plan_with_the_staging_manifest_validator_before_placing",
    "acknowledge_stale_data_explicitly_in_the_manifest_if_older_than_30_days",
    "placing_files_authorizes_nothing_the_scanner_stays_blocked_until_its_own_approval",
)


def get_csv_template_guide_label() -> str:
    """Human label for the recognized CSV template guide contract."""
    return GUIDE_LABEL


def get_csv_template(kind: Any) -> dict[str, Any]:
    """Return (a fresh copy of) the template for one dataset kind, or an
    error dict for unknown kinds. Pure; never raises."""
    if kind not in CSV_TEMPLATES:
        return {"available": False,
                "errors": ["unknown_dataset_kind:" + str(kind)]}
    template = copy.deepcopy(CSV_TEMPLATES[kind])
    template["available"] = True
    template["kind"] = kind
    template["place_under"] = STAGING_ROOT
    template["template_is_text_only_nothing_is_written"] = True
    return template


def _base_guide() -> dict[str, Any]:
    return {
        "schema_version": GUIDE_SCHEMA_VERSION,
        "label": GUIDE_LABEL,
        "mode": GUIDE_MODE,
        "lane": "arbitrage_factory_v1",
        "verdict": None,
        "blockers": [],
        "prep_rules_verdict": None,
        "staging_folder": STAGING_ROOT,
        "csv_templates": copy.deepcopy(CSV_TEMPLATES),
        "placement_checklist": list(PLACEMENT_CHECKLIST),
        # Constitution, stated structurally:
        "templates_are_text_only_nothing_is_written": True,
        "sample_values_are_illustrative_placeholders_only": True,
        "operator_fills_templates_from_manually_exported_data": True,
        "scanner_remains_blocked": True,
        "guide_reads_no_files": True,
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


def record_csv_template_guide(prep_rules: Any) -> dict[str, Any]:
    """Record the template guide, gated on READY, valid preparation rules.
    PURE: never raises, writes nothing, reads no file."""
    guide = _base_guide()

    if not isinstance(prep_rules, dict):
        guide["verdict"] = VERDICT_TEMPLATE_GUIDE_BLOCKED
        guide["blockers"].append("prep_rules_missing")
        return guide

    validation = validate_staged_data_preparation_rules(prep_rules)
    if not validation.get("valid"):
        guide["verdict"] = VERDICT_TEMPLATE_GUIDE_BLOCKED
        guide["blockers"].append("prep_rules_invalid")
        return guide

    if prep_rules.get("verdict") != VERDICT_PREP_RULES_READY:
        guide["verdict"] = VERDICT_TEMPLATE_GUIDE_BLOCKED
        guide["blockers"].append("prep_rules_not_ready")
        return guide

    guide["verdict"] = VERDICT_TEMPLATE_GUIDE_READY
    guide["prep_rules_verdict"] = prep_rules.get("verdict")
    return guide


def build_csv_template_guide() -> dict[str, Any]:
    """Build the guide against the real seq 0 -> 2 -> prep-rules chain. Pure."""
    return record_csv_template_guide(build_staged_data_preparation_rules())


def validate_csv_template_guide(guide: Any) -> dict[str, Any]:
    """Validate (read-only) the guide's shape, template self-consistency, and
    safety invariants. Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(guide, dict):
        return {"valid": False, "errors": ["guide_not_a_dict"]}
    g = guide

    verdict = g.get("verdict")
    if verdict not in (VERDICT_TEMPLATE_GUIDE_READY, VERDICT_TEMPLATE_GUIDE_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_TEMPLATE_GUIDE_BLOCKED and not g.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_TEMPLATE_GUIDE_READY:
        if g.get("blockers"):
            errors.append("ready_with_blockers")
        if g.get("prep_rules_verdict") != VERDICT_PREP_RULES_READY:
            errors.append("ready_without_ready_prep_rules")

    if g.get("lane") != "arbitrage_factory_v1":
        errors.append("wrong_lane")
    if g.get("staging_folder") != STAGING_ROOT:
        errors.append("staging_folder_moved")
    if tuple(g.get("placement_checklist") or ()) != PLACEMENT_CHECKLIST:
        errors.append("placement_checklist_tampered")

    templates = g.get("csv_templates")
    if not isinstance(templates, dict) or set(templates) != set(
        STAGED_DATASET_SPECS
    ):
        errors.append("templates_missing_or_kind_set_tampered")
    else:
        for kind, template in templates.items():
            header = str(template.get("header", ""))
            expected = ",".join(STAGED_DATASET_SPECS[kind]["required_columns"])
            if header != expected:
                errors.append("template_header_diverges:" + kind)
            name_check = validate_staged_file_name(
                template.get("filename_example"))
            if not name_check.get("acceptable") or name_check.get("kind") != kind:
                errors.append("template_filename_example_invalid:" + kind)
            column_count = len(header.split(","))
            for row in template.get("sample_rows") or ():
                if len(str(row).split(",")) != column_count:
                    errors.append("template_sample_row_field_count:" + kind)
                    break
            if not template.get("notes"):
                errors.append("template_notes_missing:" + kind)

    for key, err in (
        ("templates_are_text_only_nothing_is_written", "templates_claim_to_write"),
        ("sample_values_are_illustrative_placeholders_only",
         "samples_claim_real_market_data"),
        ("operator_fills_templates_from_manually_exported_data",
         "manual_export_rule_dropped"),
        ("scanner_remains_blocked", "scanner_block_dropped"),
        ("guide_reads_no_files", "guide_reads_files"),
        ("human_review_required", "human_review_dropped"),
    ):
        if g.get(key) is not True:
            errors.append(err)

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if g.get(key) is not True:
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
        if g.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_csv_template_guide_markdown(guide: Any) -> str:
    """Render the guide as deterministic markdown the operator can follow."""
    g = guide if isinstance(guide, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Arbitrage Factory V1 Staged-Data CSV Template Guide")
    lines.append("")
    lines.append("- Verdict: " + str(g.get("verdict", "")))
    lines.append("- Place files by hand under: " + str(g.get("staging_folder")))
    lines.append("- Templates are text only; nothing is written by software")
    lines.append("- Sample values are illustrative placeholders only")
    lines.append("- The scanner remains BLOCKED; placing files authorizes nothing")
    lines.append("- Next required action: " + str(g.get("next_required_action", "")))
    lines.append("")
    blockers = g.get("blockers") or []
    if blockers:
        lines.append("## Blockers (BLOCKED provides no templates)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
        return "\n".join(lines)
    for kind, template in (g.get("csv_templates") or {}).items():
        lines.append("## " + str(kind))
        lines.append("- File: " + str(template.get("filename_example")))
        lines.append("- Notes: " + str(template.get("notes")))
        lines.append("")
        lines.append("```csv")
        lines.append(str(template.get("header")))
        for row in template.get("sample_rows") or ():
            lines.append(str(row))
        lines.append("```")
        lines.append("")
    lines.append("## Placement checklist")
    for step in g.get("placement_checklist") or []:
        lines.append("- " + str(step))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)

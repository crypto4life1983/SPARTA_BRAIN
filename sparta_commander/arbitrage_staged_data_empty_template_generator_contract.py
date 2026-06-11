"""SPARTA Arbitrage Factory V1 - EMPTY TEMPLATE GENERATOR Contract (READ-ONLY).

A helper to reduce the operator's manual work: it PLANS the creation of
HEADER-ONLY placeholder CSV files under the approved staging folder

    data/arbitrage_factory_v1/staged/

so the human only has to fill rows from the approved public sources. This
module is the PLAN layer only -- it CREATES NO FILE. Executing a generation
plan (actually writing the header-only files) is a separate, future,
human-approved step under its own command.

Hard rules (validator-enforced):
  - Generated files would contain EXACTLY ONE LINE: the header from the CSV
    template guide -- byte-identical to the seq-2 required columns. NO sample
    rows, NO market values, NO placeholders beyond the header itself.
  - Filenames must pass the prep-rules filename validator (kind pattern +
    allowed labels); bare names only -- any path separator or '..' refuses.
  - Overwrite is refused: if the caller reports a filename as already
    existing, the plan refuses it (replacing an existing staged file would
    need its own separate approval).
  - Any request that includes row content is refused whole: the human fills
    values by hand from the approved public sources, never this module.

Public API:
  - GEN_SCHEMA_VERSION / GEN_LABEL / GEN_MODE
  - VERDICT_GENERATOR_READY / VERDICT_GENERATOR_BLOCKED
  - VERDICT_GENERATION_PLAN_ACCEPTED / VERDICT_GENERATION_PLAN_REFUSED
  - GENERATION_RULES / NEXT_REQUIRED_ACTION
  - get_empty_template_generator_label()
  - plan_empty_template_generation(requested_filenames, existing_filenames)
  - record_empty_template_generator(template_guide)
  - build_empty_template_generator()
  - validate_empty_template_generator(contract)
  - render_empty_template_generator_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.arbitrage_data_contract import STAGING_ROOT
from sparta_commander.arbitrage_staged_data_csv_template_guide_contract import (
    CSV_TEMPLATES,
    VERDICT_TEMPLATE_GUIDE_READY,
    build_csv_template_guide,
    validate_csv_template_guide,
)
from sparta_commander.arbitrage_staged_data_preparation_rules_contract import (
    validate_staged_file_name,
)

GEN_SCHEMA_VERSION = "arbitrage_staged_data_empty_template_generator_contract.v1"
GEN_LABEL = (
    "SPARTA Arbitrage Factory V1 Empty Template Generator "
    "(READ-ONLY, PLAN ONLY, CREATES NO FILE)"
)
GEN_MODE = "RESEARCH_ONLY"

VERDICT_GENERATOR_READY = "ARBITRAGE_EMPTY_TEMPLATE_GENERATOR_READY"
VERDICT_GENERATOR_BLOCKED = "ARBITRAGE_EMPTY_TEMPLATE_GENERATOR_BLOCKED"
VERDICT_GENERATION_PLAN_ACCEPTED = "EMPTY_TEMPLATE_GENERATION_PLAN_ACCEPTED"
VERDICT_GENERATION_PLAN_REFUSED = "EMPTY_TEMPLATE_GENERATION_PLAN_REFUSED"

# Executing an accepted plan is its own future, human-approved step.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_EMPTY_TEMPLATE_FILE_CREATION"

GENERATION_RULES = (
    "generated_files_contain_exactly_one_line_the_template_header",
    "no_sample_rows_no_market_values_no_placeholders_beyond_the_header",
    "destination_is_only_data_arbitrage_factory_v1_staged",
    "filenames_must_pass_the_prep_rules_filename_validator",
    "existing_files_are_never_overwritten_without_a_separate_approval",
    "the_human_fills_rows_by_hand_from_the_approved_public_sources_only",
    "this_contract_plans_only_actual_creation_needs_its_own_approval",
)


def get_empty_template_generator_label() -> str:
    """Human label for the recognized empty template generator contract."""
    return GEN_LABEL


def plan_empty_template_generation(
    requested_filenames: Any, existing_filenames: Any = ()
) -> dict[str, Any]:
    """Plan (pure, in-memory) the creation of header-only template files.
    CREATES NOTHING. The caller supplies which filenames already exist (this
    module reads no directory). Never raises."""
    result: dict[str, Any] = {
        "verdict": None,
        "errors": [],
        "planned_files": [],
        "refused_files": {},
        "plan_creates_no_files": True,
        "execution_requires_separate_human_approval": True,
    }

    if not isinstance(requested_filenames, (list, tuple)) or not requested_filenames:
        result["verdict"] = VERDICT_GENERATION_PLAN_REFUSED
        result["errors"].append("requested_filenames_missing_or_empty")
        return result
    existing = set(existing_filenames or ())

    seen: set[str] = set()
    for raw in requested_filenames:
        refusals: list[str] = []
        if isinstance(raw, dict):
            # row content smuggled into a generation request refuses it whole
            refusals.append("request_carries_content_only_bare_filenames_allowed")
            key = str(raw.get("filename", "entry"))
            result["refused_files"][key] = refusals
            continue
        filename = str(raw)
        if filename in seen:
            refusals.append("duplicate_request")
        seen.add(filename)

        name_check = validate_staged_file_name(filename)
        refusals.extend(name_check["errors"])
        kind = name_check.get("kind")

        if filename in existing:
            refusals.append("file_already_exists_overwrite_needs_separate_approval")

        if refusals:
            result["refused_files"][filename] = refusals
            continue

        result["planned_files"].append({
            "filename": filename,
            "kind": kind,
            "destination": STAGING_ROOT + filename,
            "content": CSV_TEMPLATES[kind]["header"],
            "content_is_header_only": True,
            "action": "CREATE_HEADER_ONLY_PLACEHOLDER",
        })

    if result["refused_files"]:
        result["verdict"] = VERDICT_GENERATION_PLAN_REFUSED
        result["errors"].append("one_or_more_requests_refused")
        result["planned_files"] = []
    else:
        result["verdict"] = VERDICT_GENERATION_PLAN_ACCEPTED
    return result


def _base_contract() -> dict[str, Any]:
    return {
        "schema_version": GEN_SCHEMA_VERSION,
        "label": GEN_LABEL,
        "mode": GEN_MODE,
        "lane": "arbitrage_factory_v1",
        "verdict": None,
        "blockers": [],
        "template_guide_verdict": None,
        "staging_folder": STAGING_ROOT,
        "generation_rules": list(GENERATION_RULES),
        "headers_by_kind": {
            kind: template["header"] for kind, template in CSV_TEMPLATES.items()
        },
        # Constitution, stated structurally:
        "plan_creates_no_files": True,
        "generated_files_would_be_header_only": True,
        "no_market_values_ever_generated": True,
        "overwrite_requires_separate_approval": True,
        "human_fills_values_from_approved_public_sources": True,
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


def record_empty_template_generator(template_guide: Any) -> dict[str, Any]:
    """Record the generator contract, gated on a READY, valid CSV template
    guide. PURE: never raises, creates nothing."""
    contract = _base_contract()

    if not isinstance(template_guide, dict):
        contract["verdict"] = VERDICT_GENERATOR_BLOCKED
        contract["blockers"].append("template_guide_missing")
        return contract

    validation = validate_csv_template_guide(template_guide)
    if not validation.get("valid"):
        contract["verdict"] = VERDICT_GENERATOR_BLOCKED
        contract["blockers"].append("template_guide_invalid")
        return contract

    if template_guide.get("verdict") != VERDICT_TEMPLATE_GUIDE_READY:
        contract["verdict"] = VERDICT_GENERATOR_BLOCKED
        contract["blockers"].append("template_guide_not_ready")
        return contract

    contract["verdict"] = VERDICT_GENERATOR_READY
    contract["template_guide_verdict"] = template_guide.get("verdict")
    return contract


def build_empty_template_generator() -> dict[str, Any]:
    """Build the generator contract against the real chain. Pure."""
    return record_empty_template_generator(build_csv_template_guide())


def validate_empty_template_generator(contract: Any) -> dict[str, Any]:
    """Validate (read-only) the generator contract's shape and safety
    invariants. Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(contract, dict):
        return {"valid": False, "errors": ["contract_not_a_dict"]}
    c = contract

    verdict = c.get("verdict")
    if verdict not in (VERDICT_GENERATOR_READY, VERDICT_GENERATOR_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_GENERATOR_BLOCKED and not c.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_GENERATOR_READY:
        if c.get("blockers"):
            errors.append("ready_with_blockers")
        if c.get("template_guide_verdict") != VERDICT_TEMPLATE_GUIDE_READY:
            errors.append("ready_without_ready_template_guide")

    if c.get("lane") != "arbitrage_factory_v1":
        errors.append("wrong_lane")
    if c.get("staging_folder") != STAGING_ROOT:
        errors.append("staging_folder_moved")
    if tuple(c.get("generation_rules") or ()) != GENERATION_RULES:
        errors.append("generation_rules_tampered")

    headers = c.get("headers_by_kind")
    expected = {kind: t["header"] for kind, t in CSV_TEMPLATES.items()}
    if headers != expected:
        errors.append("headers_diverge_from_template_guide")

    for key, err in (
        ("plan_creates_no_files", "plan_claims_to_create_files"),
        ("generated_files_would_be_header_only", "header_only_rule_dropped"),
        ("no_market_values_ever_generated", "market_values_allowed"),
        ("overwrite_requires_separate_approval", "overwrite_allowed"),
        ("human_fills_values_from_approved_public_sources",
         "manual_fill_rule_dropped"),
        ("scanner_remains_blocked", "scanner_block_dropped"),
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


def render_empty_template_generator_markdown(contract: Any) -> str:
    """Render the generator contract as deterministic markdown. Pure."""
    c = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Arbitrage Factory V1 Empty Template Generator (PLAN ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(c.get("verdict", "")))
    lines.append("- Destination: " + str(c.get("staging_folder")))
    lines.append("- This contract PLANS only; creating files is its own future "
                 "human-approved step")
    lines.append("- Generated files would be header-only; the human fills rows "
                 "from the approved public sources")
    lines.append("- The scanner remains BLOCKED")
    lines.append("- Next required action: " + str(c.get("next_required_action", "")))
    lines.append("")
    blockers = c.get("blockers") or []
    if blockers:
        lines.append("## Blockers (BLOCKED plans nothing)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
        return "\n".join(lines)
    lines.append("## Headers by kind (exactly one line per generated file)")
    for kind, header in (c.get("headers_by_kind") or {}).items():
        lines.append("- " + str(kind) + ": " + str(header))
    lines.append("")
    lines.append("## Generation rules")
    for r in c.get("generation_rules") or []:
        lines.append("- " + str(r))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)

"""SPARTA NY-Session FVG+CHOCH REAL-CANDLE FILE CREATION TOOL (READ-ONLY
BY DEFAULT, RESEARCH ONLY).

A controlled ONE-PASS tool that can LATER -- only after a separate explicit
human run approval -- accept approved no-auth public historical 1m/15m
candle rows and write validated staged CSV files under
data/ny_fvg_choch/staged/ plus a checksum manifest.

DISABLED BY DEFAULT: building a plan writes nothing; the single writing
function refuses unless it receives the exact human run-approval token. This
module performs no fetching itself -- candle rows are SUPPLIED to it (any
future fetch step is its own separately approved tool, mirroring the
arbitrage lane). Staged candle files are untracked operational data unless
separately approved as evidence artifacts.
"""

from __future__ import annotations

import datetime as _dt
import hashlib as _hashlib
import pathlib as _pathlib
from typing import Any

from sparta_commander.ny_session_fvg_choch_real_candle_staging_dry_run import (
    APPROVED_SOURCE_CATEGORY_FOR_DRY_RUN,
    run_real_candle_staging_dry_run,
    validate_staging_dry_run_record,
)
from sparta_commander.ny_session_fvg_choch_real_candle_staging_plan import (
    REQUIRED_CANDLE_FIELDS,
    REQUIRED_SYMBOLS,
    REQUIRED_TIMEFRAMES,
)
from sparta_commander.ny_session_fvg_choch_strategy_spec_contract import (
    CANDIDATE_ID,
)

FC_SCHEMA_VERSION = "ny_session_fvg_choch_real_candle_file_creation_tool.v1"
FC_LABEL = ("SPARTA NY-Session FVG+CHOCH Real-Candle File Creation Tool "
            "(READ-ONLY BY DEFAULT, RESEARCH ONLY, DISABLED WITHOUT HUMAN "
            "RUN APPROVAL)")
FC_MODE = "RESEARCH_ONLY"
TOOL_ENABLED_BY_DEFAULT = False
NEXT_REQUIRED_ACTION = "HUMAN_RUN_APPROVAL_FOR_REAL_CANDLE_FILE_CREATION"

STAGING_ROOT = "data/ny_fvg_choch/staged"
MANIFEST_NAME = "manifest.txt"
RUN_APPROVAL_TOKEN = (
    "RUN_NY_FVG_CHOCH_REAL_CANDLE_FILE_CREATION_APPROVED_BY_HUMAN")

FILE_CREATION_STATUSES = (
    "FILE_CREATION_PLAN_READY_FOR_HUMAN_RUN_APPROVAL",
    "FILE_CREATION_PLAN_BLOCKED_UPSTREAM_NOT_READY",
    "FILE_CREATION_PLAN_REJECTED_SOURCE_NOT_APPROVED",
    "FILE_CREATION_PLAN_REJECTED_FORBIDDEN_CAPABILITY",
    "FILE_CREATION_PLAN_REJECTED_PAYLOAD_INVALID",
    "FILE_CREATION_REFUSED_NOT_APPROVED",
    "FILE_CREATION_REFUSED_PLAN_INVALID",
    "FILE_CREATION_REFUSED_TARGET_EXISTS",
    "FILE_CREATION_COMPLETED_ONE_PASS",
)

_DRY_RUN_TO_PLAN_STATUS = {
    "STAGING_DRY_RUN_BLOCKED_UPSTREAM_NOT_READY":
        "FILE_CREATION_PLAN_BLOCKED_UPSTREAM_NOT_READY",
    "STAGING_DRY_RUN_REJECTED_SOURCE_NOT_APPROVED":
        "FILE_CREATION_PLAN_REJECTED_SOURCE_NOT_APPROVED",
    "STAGING_DRY_RUN_REJECTED_FORBIDDEN_CAPABILITY":
        "FILE_CREATION_PLAN_REJECTED_FORBIDDEN_CAPABILITY",
    "STAGING_DRY_RUN_REJECTED_PAYLOAD_INVALID":
        "FILE_CREATION_PLAN_REJECTED_PAYLOAD_INVALID",
}

FORBIDDEN = (
    "running_during_build_or_tests", "hidden_auto_run",
    "while_true_loops", "scheduler_or_cron_behavior",
    "optimizer_execution", "detector_replay_scorer_execution",
    "broker_exchange_private_api_access", "credentials_or_api_keys",
    "account_wallet_login_access", "trading_endpoints_of_any_kind",
    "paper_live_micro_live_authorization", "gate_unlocks",
    "report_artifact_creation_in_this_block",
)


def get_real_candle_file_creation_tool_label() -> str:
    return FC_LABEL


def _canonical_csv(rows: list[dict[str, Any]]) -> str:
    lines = [",".join(REQUIRED_CANDLE_FIELDS)]
    for row in rows:
        lines.append(",".join(str(row[f]) for f in REQUIRED_CANDLE_FIELDS))
    return "\n".join(lines) + "\n"


def _date_range(rows: list[dict[str, Any]]) -> str:
    first = _dt.datetime.fromisoformat(
        str(rows[0]["timestamp"]).replace("Z", "+00:00")).date().isoformat()
    last = _dt.datetime.fromisoformat(
        str(rows[-1]["timestamp"]).replace("Z", "+00:00")).date().isoformat()
    return first + "_" + last


def _base_plan() -> dict[str, Any]:
    return {
        "schema_version": FC_SCHEMA_VERSION, "label": FC_LABEL,
        "mode": FC_MODE, "lane": "crypto_d1_auto_research",
        "candidate_id": CANDIDATE_ID,
        "tool_enabled_by_default": TOOL_ENABLED_BY_DEFAULT,
        "source_category": APPROVED_SOURCE_CATEGORY_FOR_DRY_RUN,
        "staging_root": STAGING_ROOT,
        "plan_status": None, "errors": [], "planned_files": [],
        "manifest_plan": {"manifest_path": STAGING_ROOT + "/" + MANIFEST_NAME,
                          "checksum_algorithm": "sha256",
                          "line_format": "filename,sha256,row_count"},
        "staged_files_are_untracked_operational_data": True,
        "run_requires_exact_human_token": True,
        "modifies_mission_flow": False, "modifies_pm_lane": False,
        "human_review_required": True,
        "executes": False, "writes_files": False, "writes_reports": False,
        "runs_detector_now": False, "runs_replay_now": False,
        "scores_now": False, "fetches_data": False, "calls_api": False,
        "uses_network": False, "uses_credentials": False, "uses_wallet": False,
        "connects_broker": False, "connects_exchange": False,
        "uses_real_money": False, "contains_order_logic": False,
        "starts_scheduler": False, "sends_notifications": False,
        "authorizes_paper_execution": False, "authorizes_micro_live": False,
        "authorizes_live_trading": False, "promotes_gate": False,
        "unlocks_downstream_gate": False,
        "paper_trading_gate_locked": True, "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_file_creation_plan(source_proposal: Any,
                             payloads: Any) -> dict[str, Any]:
    """Validate everything through the pushed staging dry run and produce a
    write PLAN (paths, row counts, sha256). WRITES NOTHING."""
    plan = _base_plan()
    if not isinstance(payloads, list) or not payloads:
        plan["plan_status"] = "FILE_CREATION_PLAN_REJECTED_PAYLOAD_INVALID"
        plan["errors"] = ["payloads_missing_or_empty"]
        return plan
    seen_targets: set[str] = set()
    for index, payload in enumerate(payloads):
        record = run_real_candle_staging_dry_run(source_proposal, payload)
        if (record["staging_status"]
                != "STAGING_DRY_RUN_READY_FOR_HUMAN_FILE_APPROVAL"
                or not validate_staging_dry_run_record(record)["valid"]):
            plan["plan_status"] = _DRY_RUN_TO_PLAN_STATUS.get(
                record["staging_status"],
                "FILE_CREATION_PLAN_REJECTED_PAYLOAD_INVALID")
            plan["errors"] = ["payload_%d" % index + ":" + e
                              for e in (record["errors"]
                                        or ["dry_run_not_ready"])]
            plan["planned_files"] = []
            return plan
        symbol, timeframe = payload["symbol"], payload["timeframe"]
        # belt-and-braces: path parts come only from the closed approved sets
        assert symbol in REQUIRED_SYMBOLS and timeframe in REQUIRED_TIMEFRAMES
        rows = payload["rows"]
        content = _canonical_csv(rows)
        file_name = "%s_%s_%s.csv" % (symbol, timeframe, _date_range(rows))
        target = STAGING_ROOT + "/" + file_name
        if target in seen_targets:
            plan["plan_status"] = "FILE_CREATION_PLAN_REJECTED_PAYLOAD_INVALID"
            plan["errors"] = ["duplicate_target_file:" + target]
            plan["planned_files"] = []
            return plan
        seen_targets.add(target)
        plan["planned_files"].append({
            "target_path": target, "symbol": symbol, "timeframe": timeframe,
            "row_count": len(rows),
            "sha256": _hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "content": content,
        })
    plan["plan_status"] = "FILE_CREATION_PLAN_READY_FOR_HUMAN_RUN_APPROVAL"
    return plan


def validate_file_creation_plan(plan: Any) -> dict[str, Any]:
    """Validate a plan's shape and safety invariants. Never raises."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return {"valid": False, "errors": ["plan_not_a_dict"]}
    p = plan
    if p.get("plan_status") not in FILE_CREATION_STATUSES:
        errors.append("bad_plan_status")
    if p.get("candidate_id") != CANDIDATE_ID:
        errors.append("candidate_id_tampered")
    if p.get("tool_enabled_by_default") is not False:
        errors.append("tool_must_be_disabled_by_default")
    if p.get("source_category") != APPROVED_SOURCE_CATEGORY_FOR_DRY_RUN:
        errors.append("source_category_tampered")
    if p.get("staging_root") != STAGING_ROOT:
        errors.append("staging_root_tampered")
    if (p.get("plan_status") == "FILE_CREATION_PLAN_READY_FOR_HUMAN_RUN_APPROVAL"
            and (p.get("errors") or not p.get("planned_files"))):
        errors.append("ready_plan_inconsistent")
    for entry in p.get("planned_files") or []:
        if not str(entry.get("target_path", "")).startswith(
                STAGING_ROOT + "/"):
            errors.append("planned_file_outside_staging_root")
    for key, want in (
        ("staged_files_are_untracked_operational_data", True),
        ("run_requires_exact_human_token", True),
        ("modifies_mission_flow", False), ("modifies_pm_lane", False),
        ("human_review_required", True),
        ("paper_trading_gate_locked", True),
        ("micro_live_gate_locked", True), ("live_gate_locked", True),
    ):
        if p.get(key) is not want:
            errors.append("constitution_flag_wrong:" + key)
    for key in ("executes", "writes_files", "writes_reports",
                "runs_detector_now", "runs_replay_now", "scores_now",
                "fetches_data", "calls_api", "uses_network",
                "uses_credentials", "uses_wallet", "connects_broker",
                "connects_exchange", "uses_real_money",
                "contains_order_logic", "starts_scheduler",
                "sends_notifications", "authorizes_paper_execution",
                "authorizes_micro_live", "authorizes_live_trading",
                "promotes_gate", "unlocks_downstream_gate"):
        if p.get(key) is not False:
            errors.append("capability_not_false:" + key)
    return {"valid": not errors, "errors": errors}


def execute_file_creation(plan: Any, run_approval: Any,
                          repo_root: Any) -> dict[str, Any]:
    """The ONLY writing function. Refuses unless run_approval is the exact
    human token AND the plan is valid and READY. One pass, exclusive-create,
    inside the staging root only."""
    result: dict[str, Any] = {
        "schema_version": FC_SCHEMA_VERSION, "label": FC_LABEL,
        "mode": FC_MODE, "candidate_id": CANDIDATE_ID,
        "run_status": None, "errors": [], "files_written": [],
        "manifest_written": None,
    }
    if run_approval != RUN_APPROVAL_TOKEN:
        result["run_status"] = "FILE_CREATION_REFUSED_NOT_APPROVED"
        result["errors"] = ["human_run_approval_token_missing_or_wrong"]
        return result
    check = validate_file_creation_plan(plan)
    if (not check["valid"] or plan.get("plan_status")
            != "FILE_CREATION_PLAN_READY_FOR_HUMAN_RUN_APPROVAL"):
        result["run_status"] = "FILE_CREATION_REFUSED_PLAN_INVALID"
        result["errors"] = check.get("errors") or ["plan_not_ready"]
        return result
    root = _pathlib.Path(str(repo_root)).resolve()
    staging_dir = (root / STAGING_ROOT).resolve()
    if root not in staging_dir.parents:
        result["run_status"] = "FILE_CREATION_REFUSED_PLAN_INVALID"
        result["errors"] = ["staging_root_escapes_repo_root"]
        return result
    targets = []
    for entry in plan["planned_files"]:
        target = (root / entry["target_path"]).resolve()
        if staging_dir not in target.parents:
            result["run_status"] = "FILE_CREATION_REFUSED_PLAN_INVALID"
            result["errors"] = ["target_outside_staging_root:"
                                + entry["target_path"]]
            return result
        if target.exists():
            result["run_status"] = "FILE_CREATION_REFUSED_TARGET_EXISTS"
            result["errors"] = ["refusing_to_overwrite:"
                                + entry["target_path"]]
            return result
        targets.append((target, entry))
    staging_dir.mkdir(parents=True, exist_ok=True)
    manifest_lines = []
    for target, entry in targets:
        with open(target, "x", encoding="utf-8", newline="") as handle:
            handle.write(entry["content"])
        result["files_written"].append(entry["target_path"])
        manifest_lines.append("%s,%s,%d" % (target.name, entry["sha256"],
                                            entry["row_count"]))
    manifest_path = staging_dir / MANIFEST_NAME
    with open(manifest_path, "w", encoding="utf-8", newline="") as handle:
        handle.write("\n".join(manifest_lines) + "\n")
    result["manifest_written"] = STAGING_ROOT + "/" + MANIFEST_NAME
    result["run_status"] = "FILE_CREATION_COMPLETED_ONE_PASS"
    return result

"""Validation-factory report schema + writer (Factory-D2).

Smallest safe foundation for the reusable validation runner planned in
reports/factory_d1_reusable_validation_runner_plan/ (committed 93b5299). This
module ONLY defines the standard validation-report structure, validates it, and
renders it to report.json + report.md. It runs NO strategy, NO backtest, NO
IS/OOS, NO optimization, NO data fetch.

OFFLINE / INERT: Python standard library only (json, os, datetime). It opens no
network connection, spawns no child process, runs no git command, and has no
global side effects at import time (only constant + function/class definitions).

It is a COMMON REPORT WRITER -- it validates report STRUCTURE, never trading
performance. A report can be structurally valid and describe a failed strategy;
judging the strategy is a later module's job, not this one's.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple


# The frozen report-structure standard from Factory-D1 (section 8), plus the
# title/created_utc/status/notes envelope fields. Each field maps to its single
# expected JSON-serializable type. bool is intentionally NOT accepted where a
# str/list/dict is required.
EXPECTED_TYPES: Dict[str, type] = {
    "branch_id": str,
    "module_id": str,
    "title": str,
    "created_utc": str,
    "status": str,
    "verdict": str,
    "source_commits": dict,
    "input_files": list,
    "data_window": dict,
    "frozen_parameters": dict,
    "metrics": dict,
    "caveats": list,
    "next_allowed_step": str,
    "forbidden_actions": list,
    "notes": list,
}

REQUIRED_FIELDS: Tuple[str, ...] = tuple(EXPECTED_TYPES.keys())


def utc_now_iso() -> str:
    """Explicit UTC timestamp helper (the ONLY place a time value is generated).

    Callers pass this into `created_utc`; the writer never injects a timestamp on
    its own, so writing the same report twice is byte-identical.
    """
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ValidationReport:
    """Typed builder for the standard validation report.

    `to_dict()` returns the plain-dict canonical form that `validate_report` /
    `write_report` operate on. Using a dataclass here is a convenience for
    callers; the validator still works on raw dicts (so a hand-built dict missing
    a field is correctly rejected).
    """

    branch_id: str
    module_id: str
    title: str
    status: str
    verdict: str
    created_utc: str = ""
    source_commits: Dict[str, Any] = field(default_factory=dict)
    input_files: List[Any] = field(default_factory=list)
    data_window: Dict[str, Any] = field(default_factory=dict)
    frozen_parameters: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    caveats: List[Any] = field(default_factory=list)
    next_allowed_step: str = ""
    forbidden_actions: List[Any] = field(default_factory=list)
    notes: List[Any] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if not d.get("created_utc"):
            d["created_utc"] = utc_now_iso()
        return d


def make_report(
    branch_id: str,
    module_id: str,
    title: str,
    status: str,
    verdict: str,
    *,
    created_utc: str = "",
    source_commits: Dict[str, Any] = None,
    input_files: List[Any] = None,
    data_window: Dict[str, Any] = None,
    frozen_parameters: Dict[str, Any] = None,
    metrics: Dict[str, Any] = None,
    caveats: List[Any] = None,
    next_allowed_step: str = "",
    forbidden_actions: List[Any] = None,
    notes: List[Any] = None,
) -> Dict[str, Any]:
    """Build a standard report dict with safe empty defaults.

    `created_utc` defaults to an explicit `utc_now_iso()` call (the only implicit
    time source, and only here -- never inside `write_report`).
    """
    return {
        "branch_id": branch_id,
        "module_id": module_id,
        "title": title,
        "created_utc": created_utc or utc_now_iso(),
        "status": status,
        "verdict": verdict,
        "source_commits": dict(source_commits or {}),
        "input_files": list(input_files or []),
        "data_window": dict(data_window or {}),
        "frozen_parameters": dict(frozen_parameters or {}),
        "metrics": dict(metrics or {}),
        "caveats": list(caveats or []),
        "next_allowed_step": next_allowed_step,
        "forbidden_actions": list(forbidden_actions or []),
        "notes": list(notes or []),
    }


def validate_report(report: Any) -> List[str]:
    """Return a list of structural errors (EMPTY list == valid).

    This function NEVER raises for a malformed report; it reports problems as
    strings so a caller can decide what to do. `write_report` is the layer that
    turns a non-empty error list into a hard `ValueError` (refuse-before-write).
    Only structure/type is checked -- not trading correctness.
    """
    errors: List[str] = []
    if not isinstance(report, dict):
        return [f"report must be a dict, got {type(report).__name__}"]
    for fname, ftype in EXPECTED_TYPES.items():
        if fname not in report:
            errors.append(f"missing required field: {fname}")
            continue
        value = report[fname]
        # Reject bool where a non-bool type is required (bool is an int subclass).
        if isinstance(value, bool) and ftype is not bool:
            errors.append(
                f"field {fname} must be {ftype.__name__}, got bool"
            )
            continue
        if not isinstance(value, ftype):
            errors.append(
                f"field {fname} must be {ftype.__name__}, got {type(value).__name__}"
            )
    return errors


def _to_canonical_json(report: Dict[str, Any]) -> str:
    """Deterministic pretty JSON: sorted keys, 2-space indent, trailing newline.

    sort_keys makes repeat writes of the same input byte-identical regardless of
    dict insertion order.
    """
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def _md_block(value: Any) -> str:
    """Render a nested value inline for markdown (compact JSON for dict/list)."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return str(value)


def render_markdown(report: Dict[str, Any]) -> str:
    """Render the standard report as simple, human-readable markdown.

    Validates first so a malformed report cannot produce half-rendered output.
    """
    errors = validate_report(report)
    if errors:
        raise ValueError("cannot render invalid report: " + "; ".join(errors))

    lines: List[str] = []
    lines.append(f"# {report['title']}")
    lines.append("")
    lines.append(f"- **Status:** {report['status']}")
    lines.append(f"- **Verdict:** {report['verdict']}")
    lines.append(f"- **Branch:** {report['branch_id']}")
    lines.append(f"- **Module:** {report['module_id']}")
    lines.append(f"- **Created (UTC):** {report['created_utc']}")
    lines.append("")

    lines.append("## Source commits")
    if report["source_commits"]:
        for label in sorted(report["source_commits"]):
            lines.append(f"- {label}: {report['source_commits'][label]}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Input files")
    if report["input_files"]:
        for f in report["input_files"]:
            lines.append(f"- {f}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Data window")
    if report["data_window"]:
        for k in sorted(report["data_window"]):
            lines.append(f"- {k}: {_md_block(report['data_window'][k])}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Frozen parameters")
    if report["frozen_parameters"]:
        for k in sorted(report["frozen_parameters"]):
            lines.append(f"- {k}: {_md_block(report['frozen_parameters'][k])}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Metrics")
    if report["metrics"]:
        for k in sorted(report["metrics"]):
            lines.append(f"- {k}: {_md_block(report['metrics'][k])}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Caveats")
    if report["caveats"]:
        for c in report["caveats"]:
            lines.append(f"- {c}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Next allowed step")
    lines.append(report["next_allowed_step"] or "- (none)")
    lines.append("")

    lines.append("## Forbidden actions")
    if report["forbidden_actions"]:
        for a in report["forbidden_actions"]:
            lines.append(f"- {a}")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.append("## Notes")
    if report["notes"]:
        for nline in report["notes"]:
            lines.append(f"- {nline}")
    else:
        lines.append("- (none)")
    lines.append("")

    return "\n".join(lines)


def write_report(report: Dict[str, Any], output_dir: str) -> Dict[str, str]:
    """Validate, then write report.json + report.md into `output_dir`.

    Refuse-before-write: if the report is structurally invalid, raise ValueError
    BEFORE creating the directory or any file, so no partial artifacts are left.
    Returns {"report_json": <path>, "report_md": <path>}.
    """
    errors = validate_report(report)
    if errors:
        raise ValueError("refusing to write invalid report: " + "; ".join(errors))

    # Render BEFORE touching the filesystem so a render failure also leaves
    # nothing partial behind.
    md_text = render_markdown(report)
    json_text = _to_canonical_json(report)

    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, "report.json")
    md_path = os.path.join(output_dir, "report.md")
    with open(json_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json_text)
    with open(md_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(md_text)
    return {"report_json": json_path, "report_md": md_path}

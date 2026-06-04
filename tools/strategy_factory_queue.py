"""SPARTA Strategy Factory v1 — Step 2: Research Queue schema + loader/validator.

A tiny, deterministic, standard-library-only loader and fail-closed validator
for ``configs/research_queue.json``. The queue declares which research tasks MAY
be *considered* later by the orchestrator. This module ONLY loads and validates
that declaration. It does not — and in v1 cannot — execute anything.

Hard guarantees (asserted by tests/test_strategy_factory_queue.py):
  * NEVER executes. No subprocess, no network, no runner import, no broker /
    exchange / order / fetch path. It only reads a JSON file and re-describes it.
  * FAIL CLOSED. Missing required fields, an unknown runner, an unknown dataset,
    or any forbidden safety flag set true => the item is BLOCKED (recorded in
    ``blocked_reasons``), never executed and never silently accepted.
  * NON-EXECUTABLE BY CONSTRUCTION. ``executable`` is always False in v1.
    ``execution_authorized`` must be false on every item; any true value is a
    hard block. "Approved for research listing" (``approved_for_research``) is
    kept strictly separate from "approved for execution" — the latter does not
    exist in v1.
  * DETERMINISTIC. Items are ordered by (priority, task_id); JSON is sorted-key.
  * If output is written at all (``--write``), it goes ONLY to
    ``reports/strategy_factory_queue_v1_build/`` — never to the dashboard,
    ``data/``, datasets, or other reports.

Standard library only. No third-party imports. No runner imports.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

SCHEMA_VERSION = 1
LAYER_NAME = "strategy_factory_queue_v1"

# The single config this loader understands.
_QUEUE_RELPATH = Path("configs") / "research_queue.json"

# Allowlists — the only runner / dataset / mode a queue item may name in v1.
ALLOWED_RUNNERS = frozenset({"tools/crypto_d1_backtest_runner.py"})
ALLOWED_DATASETS = frozenset({"CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002"})
ALLOWED_MODES = frozenset({"momentum_confirmation_v1"})

# Every field a queue item must carry. Missing any => the item is blocked.
REQUIRED_ITEM_FIELDS = (
    "task_id", "strategy_id", "strategy_family", "market", "dataset_id",
    "allowed_runner", "allowed_mode", "priority", "status",
    "approved_for_research", "blocked_reasons", "max_runtime_seconds",
    "expected_outputs", "safety_flags", "created_at", "updated_at",
    "next_action",
)

# The one flag that must be True and the flags that must be False on every item.
_FLAG_MUST_BE_TRUE = "research_only"
_FLAGS_MUST_BE_FALSE = (
    "paper_live_authorized",
    "broker_path_enabled",
    "exchange_path_enabled",
    "order_path_enabled",
    "active_strong_promoted",
    "bundle_23_started",
    "dataset_mutation_allowed",
    "execution_authorized",
)
REQUIRED_SAFETY_FLAGS = (_FLAG_MUST_BE_TRUE,) + _FLAGS_MUST_BE_FALSE

# Canonical pinned-false posture used on the report envelope. Constants.
QUEUE_SAFETY_FLAGS = {
    "research_only": True,
    "paper_live_authorized": False,
    "broker_path_enabled": False,
    "exchange_path_enabled": False,
    "order_path_enabled": False,
    "active_strong_promoted": False,
    "bundle_23_started": False,
    "dataset_mutation_allowed": False,
    "execution_authorized": False,
}

# Output is opt-in and confined to this single build folder.
_BUILD_OUT_RELDIR = Path("reports") / "strategy_factory_queue_v1_build"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# IO — fail closed.
# ---------------------------------------------------------------------------

def load_queue_file(path: Path) -> tuple[Optional[dict], str]:
    """Return (obj, status). status in {'ok', 'missing', 'error'}."""
    try:
        path = Path(path)
        if not path.is_file():
            return None, "missing"
        obj = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            return None, "error"
        return obj, "ok"
    except Exception:  # noqa: BLE001 — fail closed; caller records a warning
        return None, "error"


# ---------------------------------------------------------------------------
# Per-item validation (pure, deterministic, fail-closed).
# ---------------------------------------------------------------------------

def _validate_item(raw: Any) -> dict:
    """Normalize and validate a single queue item.

    Returns a normalized entry carrying ``valid``, ``blocked_reasons``,
    ``eligible_for_research_listing`` and ``executable`` (always False in v1).
    Never raises; problems become blocked_reasons.
    """
    blocked: list[str] = []

    if not isinstance(raw, dict):
        return {
            "task_id": None,
            "valid": False,
            "blocked_reasons": ["item is not a JSON object"],
            "eligible_for_research_listing": False,
            "executable": False,
            "safety_flags": dict(QUEUE_SAFETY_FLAGS),
        }

    task_id = raw.get("task_id")
    task_id = str(task_id) if task_id not in (None, "") else None

    # 1) Required-field presence.
    for field in REQUIRED_ITEM_FIELDS:
        if field not in raw:
            blocked.append(f"missing required field: {field}")

    # 2) Runner allowlist.
    runner = raw.get("allowed_runner")
    runner = str(runner).replace("\\", "/") if runner not in (None, "") else None
    if runner is None:
        blocked.append("allowed_runner is empty")
    elif runner not in ALLOWED_RUNNERS:
        blocked.append(f"unknown runner not in allowlist: {runner}")

    # 3) Dataset allowlist.
    dataset_id = raw.get("dataset_id")
    dataset_id = str(dataset_id) if dataset_id not in (None, "") else None
    if dataset_id is None:
        blocked.append("dataset_id is empty")
    elif dataset_id not in ALLOWED_DATASETS:
        blocked.append(f"unknown dataset not in allowlist: {dataset_id}")

    # 4) Mode allowlist.
    mode = raw.get("allowed_mode")
    mode = str(mode) if mode not in (None, "") else None
    if mode is None:
        blocked.append("allowed_mode is empty")
    elif mode not in ALLOWED_MODES:
        blocked.append(f"unknown mode not in allowlist: {mode}")

    # 5) Safety-flag enforcement. research_only must be True; every other flag
    #    (including execution_authorized) must be present and False.
    flags = raw.get("safety_flags")
    if not isinstance(flags, dict):
        blocked.append("safety_flags missing or not an object")
        flags = {}
    else:
        for flag in REQUIRED_SAFETY_FLAGS:
            if flag not in flags:
                blocked.append(f"safety_flags missing: {flag}")
        if flags.get(_FLAG_MUST_BE_TRUE) is not True:
            blocked.append(f"safety_flags.{_FLAG_MUST_BE_TRUE} must be true")
        for flag in _FLAGS_MUST_BE_FALSE:
            if flags.get(flag) is True:
                blocked.append(f"forbidden safety flag is true: {flag}")

    # 6) Execution must never be authorized in v1 (explicit, on top of the flag
    #    check) — keeps "approved for listing" strictly separate from execution.
    if raw.get("execution_authorized") is True:
        blocked.append("execution_authorized is true (forbidden in v1)")

    # 7) approved_for_research must be a bool; even when true it confers ONLY
    #    research-listing eligibility, never execution.
    approved = raw.get("approved_for_research")
    if not isinstance(approved, bool):
        blocked.append("approved_for_research must be a boolean")
        approved = False

    # Carry author-declared blocked_reasons through (deduped, deterministic).
    author_blocked = raw.get("blocked_reasons")
    if isinstance(author_blocked, list):
        for r in author_blocked:
            blocked.append(f"author: {r}")

    valid = len(blocked) == 0
    entry = {
        "task_id": task_id,
        "strategy_id": _as_str(raw.get("strategy_id")),
        "strategy_family": _as_str(raw.get("strategy_family")),
        "market": _as_str(raw.get("market")),
        "dataset_id": dataset_id,
        "allowed_runner": runner,
        "allowed_mode": mode,
        "priority": raw.get("priority"),
        "status": _as_str(raw.get("status")),
        "approved_for_research": bool(approved),
        "max_runtime_seconds": raw.get("max_runtime_seconds"),
        "expected_outputs": raw.get("expected_outputs")
            if isinstance(raw.get("expected_outputs"), list) else [],
        "safety_flags": dict(QUEUE_SAFETY_FLAGS),
        "created_at": _as_str(raw.get("created_at")),
        "updated_at": _as_str(raw.get("updated_at")),
        "next_action": _as_str(raw.get("next_action")),
        "valid": valid,
        "blocked_reasons": sorted(set(blocked)),
        # Listing eligibility: a structurally valid, author-approved item. This
        # is NOT execution authorization.
        "eligible_for_research_listing": valid and bool(approved),
        # v1 invariant: nothing is ever executable from the queue.
        "executable": False,
    }
    return entry


def _as_str(v: Any) -> Optional[str]:
    return str(v) if v not in (None, "") else None


# ---------------------------------------------------------------------------
# Top-level validate / build (read-only, deterministic).
# ---------------------------------------------------------------------------

def validate_queue(queue_obj: Optional[dict], *, load_status: str = "ok",
                   source: Optional[str] = None) -> dict:
    """Validate an in-memory queue object and return the normalized report.

    Never raises. A missing/corrupt file yields an empty, fail-closed report
    with a recorded warning rather than an exception.
    """
    warnings: list[str] = []
    items_out: list[dict] = []

    if load_status == "missing":
        warnings.append("research_queue.json not found; queue is empty")
    elif load_status == "error" or not isinstance(queue_obj, dict):
        warnings.append("research_queue.json unreadable; queue is empty")
        queue_obj = {}
    else:
        raw_items = queue_obj.get("items")
        if not isinstance(raw_items, list):
            warnings.append("queue 'items' missing or not a list; treated as empty")
            raw_items = []
        for raw in raw_items:
            entry = _validate_item(raw)
            if not entry["valid"]:
                warnings.append(
                    f"{entry.get('task_id') or '<no task_id>'}: blocked "
                    f"({len(entry['blocked_reasons'])} reason(s))")
            items_out.append(entry)

    items_out.sort(key=lambda e: (_priority_key(e.get("priority")),
                                  e.get("task_id") or ""))

    blocked_count = sum(1 for e in items_out if not e["valid"])
    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER_NAME,
        "read_only": True,
        "executes_anything": False,
        "source": source,
        "safety_flags": dict(QUEUE_SAFETY_FLAGS),
        "allowed_runners": sorted(ALLOWED_RUNNERS),
        "allowed_datasets": sorted(ALLOWED_DATASETS),
        "allowed_modes": sorted(ALLOWED_MODES),
        "item_count": len(items_out),
        "valid_item_count": len(items_out) - blocked_count,
        "blocked_item_count": blocked_count,
        "items": items_out,
        "warnings": warnings,
    }


def _priority_key(p: Any) -> tuple:
    """Sort numeric priorities first (ascending), then non-numeric by string."""
    if isinstance(p, bool):  # bool is an int subclass — exclude it
        return (1, str(p))
    if isinstance(p, (int, float)):
        return (0, p)
    return (1, str(p))


def build(base: Path) -> dict:
    """Load ``base/configs/research_queue.json`` and return the validated report.

    Pure read: never writes, never runs a subprocess, never touches the network,
    never imports a runner. Deterministic given the same on-disk file.
    """
    base = Path(base)
    path = base / _QUEUE_RELPATH
    obj, status = load_queue_file(path)
    source = _QUEUE_RELPATH.as_posix() if status != "missing" else None
    return validate_queue(obj, load_status=status, source=source)


def to_stable_json(report: dict) -> str:
    """Deterministic JSON text (sorted keys, trailing newline)."""
    return json.dumps(report, indent=2, sort_keys=True,
                      ensure_ascii=False) + "\n"


def render_markdown(report: dict) -> str:
    lines = ["# Research Queue v1 (read-only, non-executable)", ""]
    lines.append(f"- schema_version: {report.get('schema_version')}")
    lines.append(f"- item_count: {report.get('item_count')} "
                 f"(valid: {report.get('valid_item_count')}, "
                 f"blocked: {report.get('blocked_item_count')})")
    lines.append("- safety: research_only=true; execution_authorized=false; "
                 "paper/live, broker, exchange, order paths disabled; no "
                 "ACTIVE/STRONG; no Bundle 23. Nothing here is executable in v1.")
    lines.append("")
    lines.append("| task_id | strategy_id | mode | priority | status | "
                 "valid | listing_eligible | executable |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for e in report.get("items", []):
        lines.append(
            "| {t} | {s} | {m} | {p} | {st} | {v} | {le} | {ex} |".format(
                t=e.get("task_id"), s=e.get("strategy_id"),
                m=e.get("allowed_mode"), p=e.get("priority"),
                st=e.get("status"), v=e.get("valid"),
                le=e.get("eligible_for_research_listing"),
                ex=e.get("executable")))
    for e in report.get("items", []):
        if e.get("blocked_reasons"):
            lines += ["", f"### Blocked: {e.get('task_id')}", ""]
            lines += [f"- {r}" for r in e["blocked_reasons"]]
    warns = report.get("warnings", [])
    if warns:
        lines += ["", "## Warnings", ""]
        lines += [f"- {w}" for w in warns]
    return "\n".join(lines) + "\n"


def write_build_report(base: Path, report: dict) -> list[str]:
    """Opt-in: write the validated queue report to the single allowed build
    folder. Returns the repo-relative paths written. Writes nowhere else."""
    out_dir = Path(base) / _BUILD_OUT_RELDIR
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "queue.json"
    md_path = out_dir / "queue.md"
    json_path.write_text(to_stable_json(report), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return [json_path.relative_to(base).as_posix(),
            md_path.relative_to(base).as_posix()]


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Strategy Factory Research Queue v1 validator "
                    "(loads + validates only; executes nothing).")
    parser.add_argument("--base", default=None,
                        help="repo root (default: auto-detected)")
    parser.add_argument("--format", choices=("json", "md"), default="json")
    parser.add_argument(
        "--write", action="store_true",
        help="ALSO write queue.json/.md to "
             "reports/strategy_factory_queue_v1_build/ (read-only otherwise)")
    args = parser.parse_args(argv)

    base = Path(args.base) if args.base else _repo_root()
    report = build(base)
    if args.write:
        written = write_build_report(base, report)
        sys.stderr.write("wrote: " + ", ".join(written) + "\n")
    sys.stdout.write(render_markdown(report) if args.format == "md"
                     else to_stable_json(report))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())

"""SPARTA Strategy Factory v1 — Step 4: Dry-run Research Orchestrator.

A tiny, deterministic, standard-library-only orchestrator that JOINS the three
shipped read-only layers:

  1. Strategy Report Registry v1  (tools/strategy_report_registry.py)  — what has
     happened: per-strategy stage + clamped verdict.
  2. Research Queue v1            (tools/strategy_factory_queue.py)     — the
     human-authored approved backlog of considerable tasks.
  3. Safety Contract v1           (tools/strategy_factory_safety.py)    — the
     central gate every task must pass before it may be considered.

It emits a deterministic "what WOULD run / what is blocked / why" plan. It is
DRY-RUN ONLY: it constructs no command, calls no runner, and pins
``executable=false`` for every task. It imports the three factory tools above
(which are themselves read-only) but NEVER a runner module.

Hard guarantees (asserted by tests/test_strategy_factory_orchestrator.py):
  * DRY-RUN ONLY. ``executes_anything=False``; ``executable`` is pinned false on
    every task; ``would_run_command`` is always null; ``would_write_outputs`` is
    always empty. Any command-ish preview is a clearly-labeled, incomplete,
    non-executable prose ``disabled_preview`` — never a copy-pasteable command.
  * FAIL CLOSED. Missing registry / missing queue / missing-or-unsafe safety
    contract halts execution-readiness for everything; an invalid queue item or
    an unknown strategy_id blocks that task. No path raises.
  * NO subprocess, NO network, NO runner import.
  * DETERMINISTIC. Tasks sorted by task_id; sorted-key JSON; no wall-clock.
  * If output is written at all (``--write``), it goes ONLY to
    ``reports/strategy_factory_orchestrator_v1_build/``.

Standard library only. No third-party imports. No runner imports.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

# Sibling factory tools live in this same directory; make them importable when
# this module is run as a script. These are read-only tools, NOT runners.
_THIS_DIR = Path(__file__).resolve().parent
if str(_THIS_DIR) not in sys.path:
    sys.path.insert(0, str(_THIS_DIR))

import strategy_report_registry as srr        # noqa: E402  (read-only)
import strategy_factory_queue as sfq          # noqa: E402  (read-only)
import strategy_factory_safety as sfs         # noqa: E402  (read-only)

SCHEMA_VERSION = 1
LAYER_NAME = "strategy_factory_orchestrator_v1"

# Output is opt-in and confined to this single build folder.
_BUILD_OUT_RELDIR = Path("reports") / "strategy_factory_orchestrator_v1_build"

# Standing reason present on EVERY task: this layer never executes.
_NO_EXEC_REASON = ("execution not authorized: dry-run orchestrator v1 never "
                   "executes (executable is pinned false)")


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Per-task join (pure, deterministic, fail-closed).
# ---------------------------------------------------------------------------

def _disabled_preview(runner: Optional[str], mode: Optional[str],
                      dataset: Optional[str]) -> str:
    """A deliberately INCOMPLETE, NON-EXECUTABLE prose description. This is not a
    command: it has no entrypoint, no flags, and cannot be copied and run."""
    return ("DISABLED_PREVIEW (non-executable, incomplete): if this task were "
            "ever separately approved, it would involve the runner "
            f"'{runner or 'n/a'}' in mode '{mode or 'n/a'}' over dataset "
            f"'{dataset or 'n/a'}'. No command line is constructed; no "
            "arguments or entrypoint are emitted; nothing here is runnable.")


def _build_task_entry(item: dict, reg_by_id: dict, contract_by_task: dict,
                      contract_safe: bool) -> dict:
    blocked: list[str] = []
    warnings: list[str] = []

    task_id = item.get("task_id")
    strategy_id = item.get("strategy_id")

    # --- Safety-contract join (uses the contract screen of the RAW queue item,
    #     so a smuggled forbidden flag/term is caught, not masked). ---
    cres = contract_by_task.get(task_id) if contract_safe else None
    if cres is not None:
        contract_conformant = bool(cres.get("contract_conformant"))
        allowed_for_listing = bool(cres.get("allowed_for_listing"))
        blocked += [f"contract: {r}" for r in cres.get("blocked_reasons", [])]
    else:
        contract_conformant = False
        allowed_for_listing = False
        blocked.append("safety contract unsafe or missing: task not screened; "
                       "no execution")

    # --- Queue-level validity join. ---
    if not item.get("valid", False):
        blocked += [f"queue: {r}" for r in item.get("blocked_reasons", [])]

    # --- Registry join by strategy_id. ---
    reg = reg_by_id.get(strategy_id)
    if reg is None:
        blocked.append(f"unknown strategy_id not found in registry: "
                       f"{strategy_id or '<empty>'}")
        current_stage = None
        current_verdict = None
    else:
        current_stage = reg.get("stage")
        current_verdict = reg.get("verdict")

    # --- Standing non-execution reasons (always present). ---
    blocked.append(_NO_EXEC_REASON)
    if not item.get("approved_for_research", False):
        blocked.append("task not approved_for_research: create the N=20 "
                       "deeper-validation plan before any execution")

    return {
        "task_id": str(task_id) if task_id not in (None, "") else None,
        "strategy_id": strategy_id,
        "current_stage": current_stage,
        "current_verdict": current_verdict,
        "queue_status": item.get("status"),
        "contract_conformant": contract_conformant,
        "allowed_for_listing": allowed_for_listing,
        "executable": False,  # hard-pinned invariant
        "blocked_reasons": sorted(set(blocked)),
        "warnings": warnings,
        "next_action": item.get("next_action"),
        "would_run_command": None,
        "would_write_outputs": [],
        "disabled_preview": _disabled_preview(
            item.get("allowed_runner"), item.get("allowed_mode"),
            item.get("dataset_id")),
    }


# ---------------------------------------------------------------------------
# Top-level dry-run plan (read-only, deterministic).
# ---------------------------------------------------------------------------

def build_dry_run_plan(base: Path) -> dict:
    """Join registry + queue + safety contract into a deterministic dry-run plan.

    Pure read: never writes, never runs a subprocess, never touches the network,
    never imports a runner. Deterministic given the same on-disk files.
    """
    base = Path(base)

    registry = srr.build_registry(base)
    queue = sfq.build(base)
    safety = sfs.build(base)

    # Fail-closed precondition detection.
    registry_missing = any("no reports/ directory" in w
                           for w in registry.get("warnings", []))
    queue_missing = any(("not found" in w or "unreadable" in w)
                        for w in queue.get("warnings", []))
    contract_safe = bool(safety.get("safe"))

    halt_reasons: list[str] = []
    if registry_missing:
        halt_reasons.append("registry missing (no reports/ directory): no execution")
    if queue_missing:
        halt_reasons.append("queue missing or unreadable: no execution")
    if not contract_safe:
        halt_reasons.append("safety contract unsafe or missing: no execution")

    reg_by_id = {e.get("strategy_id"): e
                 for e in registry.get("strategies", [])}
    ci = safety.get("queue_integration") or {}
    contract_by_task = (
        {e.get("task_id"): e for e in ci.get("items", [])}
        if ci.get("checked") else {})

    tasks = [
        _build_task_entry(item, reg_by_id, contract_by_task, contract_safe)
        for item in queue.get("items", [])
    ]
    tasks.sort(key=lambda e: e.get("task_id") or "")

    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER_NAME,
        "read_only": True,
        "executes_anything": False,
        "dry_run": True,
        "execution_halted": len(halt_reasons) > 0,
        "halt_reasons": halt_reasons,
        "would_run_command": None,
        "inputs": {
            "registry_strategy_count": registry.get("strategy_count", 0),
            "registry_missing": registry_missing,
            "queue_item_count": queue.get("item_count", 0),
            "queue_missing": queue_missing,
            "contract_safe": contract_safe,
        },
        "safety_flags": dict(sfs.CONTRACT_SAFETY_FLAGS),
        "task_count": len(tasks),
        "tasks": tasks,
        "warnings": sorted(set(
            list(registry.get("warnings", []))
            + list(queue.get("warnings", []))
            + list(safety.get("warnings", [])))),
    }


def to_stable_json(plan: dict) -> str:
    """Deterministic JSON text (sorted keys, trailing newline)."""
    return json.dumps(plan, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_markdown(plan: dict) -> str:
    lines = ["# Strategy Factory Dry-run Orchestrator v1", ""]
    lines.append(f"- schema_version: {plan.get('schema_version')}")
    lines.append(f"- **dry_run: {plan.get('dry_run')}  |  executes_anything: "
                 f"{plan.get('executes_anything')}  |  execution_halted: "
                 f"{plan.get('execution_halted')}**")
    inp = plan.get("inputs", {})
    lines.append(f"- inputs: registry={inp.get('registry_strategy_count')} "
                 f"strategies, queue={inp.get('queue_item_count')} items, "
                 f"contract_safe={inp.get('contract_safe')}")
    halts = plan.get("halt_reasons") or []
    if halts:
        lines += ["", "## Halt reasons (no execution)", ""]
        lines += [f"- {h}" for h in halts]
    lines += ["", "## Dry-run plan", ""]
    lines.append("| task_id | strategy_id | stage | verdict | queue_status | "
                 "conformant | listing | executable |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for e in plan.get("tasks", []):
        lines.append("| {t} | {s} | {st} | {v} | {qs} | {c} | {l} | {x} |".format(
            t=e.get("task_id"), s=e.get("strategy_id"),
            st=e.get("current_stage"), v=e.get("current_verdict"),
            qs=e.get("queue_status"), c=e.get("contract_conformant"),
            l=e.get("allowed_for_listing"), x=e.get("executable")))
    for e in plan.get("tasks", []):
        if e.get("blocked_reasons"):
            lines += ["", f"### Blocked: {e.get('task_id')}", ""]
            lines += [f"- {r}" for r in e["blocked_reasons"]]
    return "\n".join(lines) + "\n"


def write_build_report(base: Path, plan: dict) -> list[str]:
    """Opt-in: write the dry-run plan to the single allowed build folder. Returns
    the repo-relative paths written. Writes nowhere else."""
    out_dir = Path(base) / _BUILD_OUT_RELDIR
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "dry_run_plan.json"
    md_path = out_dir / "dry_run_plan.md"
    json_path.write_text(to_stable_json(plan), encoding="utf-8")
    md_path.write_text(render_markdown(plan), encoding="utf-8")
    return [json_path.relative_to(base).as_posix(),
            md_path.relative_to(base).as_posix()]


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only DRY-RUN Strategy Factory orchestrator v1 "
                    "(joins registry+queue+safety; executes nothing).")
    parser.add_argument("--base", default=None,
                        help="repo root (default: auto-detected)")
    parser.add_argument("--format", choices=("json", "md"), default="json")
    parser.add_argument(
        "--write", action="store_true",
        help="ALSO write dry_run_plan.json/.md to "
             "reports/strategy_factory_orchestrator_v1_build/ (read-only otherwise)")
    args = parser.parse_args(argv)

    base = Path(args.base) if args.base else _repo_root()
    plan = build_dry_run_plan(base)
    if args.write:
        written = write_build_report(base, plan)
        sys.stderr.write("wrote: " + ", ".join(written) + "\n")
    sys.stdout.write(render_markdown(plan) if args.format == "md"
                     else to_stable_json(plan))
    # Non-zero exit when execution is halted, so a caller can gate on it.
    return 0 if not plan.get("execution_halted") else 2


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())

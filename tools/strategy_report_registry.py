"""SPARTA Strategy Factory v1 — Step 1: Strategy Report Registry (read-only).

A tiny, deterministic, standard-library-only scanner that reads EXISTING
committed research artifacts under ``reports/`` and produces a normalized
registry of known experiments: their latest stage, lane status, clamped
verdict, run_id, and the paths to the plan / result / decision-memo files.

It is the read-only "single source of truth" component from the Strategy
Factory v1 plan (``reports/strategy_factory_v1_plan/``). It does NOT run any
backtest, NOT touch datasets, NOT call the network, NOT place orders, and NOT
promote anything. It only reads ``report.json`` artifacts and re-describes them.

Design contract (asserted by tests in tests/test_strategy_report_registry.py):
  * READ-ONLY by default. The core ``build_registry()`` writes nothing.
  * FAIL CLOSED. Missing/corrupt files produce warnings, never exceptions.
  * VERDICT CEILING. A raw verdict of ACTIVE / STRONG / PASS is treated as
    tampering and clamped to WATCH with a recorded warning; an unknown/empty
    verdict becomes UNKNOWN. The registry never surfaces PASS/ACTIVE/STRONG.
  * DETERMINISTIC. Stable strategy ordering, stable sorted-key JSON, and
    timestamps derived only from the artifacts (no wall-clock dependence).
  * If output is written at all (``--write``), it goes ONLY to
    ``reports/strategy_factory_registry_v1_build/`` — never to the dashboard,
    ``data/``, or any frozen-dataset folder.

Standard library only. No third-party imports.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

SCHEMA_VERSION = 1
LAYER_NAME = "strategy_report_registry_v1"

# The plan -> result -> decision-memo tree this scanner understands. Mirrors the
# glob the shipped (read-only) JARVIS Crypto-D1 Lane Monitor already uses.
PLAN_GLOB = "crypto_d1_*plan*/report.json"

# A verdict in this set may NEVER surface on the registry. classify_run never
# auto-PASSes, so any of these in a result file is treated as tampering and
# clamped to WATCH. (Same contract as the Lane Monitor, plus PASS.)
FORBIDDEN_VERDICTS = frozenset({"ACTIVE", "STRONG", "PASS"})

# Pinned-False safety invariants. Constants — never computed True.
REGISTRY_SAFETY_FLAGS = {
    "research_only": True,
    "paper_live_authorized": False,
    "broker_path_enabled": False,
    "exchange_path_enabled": False,
    "order_path_enabled": False,
    "active_strong_promoted": False,
    "bundle_23_started": False,
    "dataset_mutation_allowed": False,
}

# Output is opt-in and confined to this single build folder.
_BUILD_OUT_RELDIR = Path("reports") / "strategy_factory_registry_v1_build"

_VERSION_SUFFIX_RE = re.compile(r"_v\d+$")
_DATASET_VERSION_RE = re.compile(r"_V\d+.*$")


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# IO helpers — every read fails closed.
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> tuple[Optional[dict], str]:
    """Return (obj, status). status in {'ok', 'missing', 'error'}."""
    try:
        if not path.is_file():
            return None, "missing"
        obj = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            return None, "error"
        return obj, "ok"
    except Exception:  # noqa: BLE001 — fail closed; caller records a warning
        return None, "error"


# ---------------------------------------------------------------------------
# Field-derivation helpers (pure, deterministic).
# ---------------------------------------------------------------------------

def _derive_dataset_id(dataset_str: Optional[str]) -> Optional[str]:
    if not dataset_str:
        return None
    norm = str(dataset_str).replace("\\", "/").strip("/")
    marker = "crypto_d1_research/"
    if marker in norm:
        return norm.split(marker, 1)[1]
    parts = [p for p in norm.split("/") if p]
    if len(parts) >= 2:
        return "/".join(parts[-2:])
    return norm or None


def _derive_market(dataset_id: Optional[str]) -> Optional[str]:
    if not dataset_id:
        return None
    head = dataset_id.split("/", 1)[0]
    return _DATASET_VERSION_RE.sub("", head) or head


def _derive_family(runner_mode: Optional[str], strategy_id: str) -> str:
    base = runner_mode or strategy_id
    if base.startswith("crypto_d1_"):
        base = base[len("crypto_d1_"):]
    return _VERSION_SUFFIX_RE.sub("", base) or base


def _clamp_verdict(raw: Optional[str], warnings: list[str],
                   strategy_id: str) -> tuple[Optional[str], Optional[str]]:
    """Return (verdict, clamped_from). PASS/ACTIVE/STRONG -> WATCH (+warning);
    empty -> UNKNOWN; otherwise the upper-cased raw verdict."""
    up = str(raw or "").strip().upper()
    if not up:
        return "UNKNOWN", None
    if up in FORBIDDEN_VERDICTS:
        warnings.append(
            f"{strategy_id}: result verdict {up} is forbidden on the registry; "
            "clamped to WATCH")
        return "WATCH", up
    return up, None


def _next_action_for_stage(stage: str) -> str:
    return {
        "PLAN_ONLY": "Implement the runner + tests, then run the experiment "
                     "(separately approved).",
        "EXECUTED": "Operator review of the executed result; record a decision "
                    "memo (no promotion without a separate operator decision).",
        "DECISION_RECORDED": "Proceed to the next checkpoint per the recorded "
                             "decision memo.",
    }.get(stage, "Resolve the plan artifact.")


# ---------------------------------------------------------------------------
# Per-strategy scan.
# ---------------------------------------------------------------------------

def _scan_plan(base: Path, plan_json: Path, warnings: list[str]) -> Optional[dict]:
    plan_obj, st = _load_json(plan_json)
    if st != "ok" or plan_obj is None:
        warnings.append(
            f"plan unreadable ({st}): {plan_json.relative_to(base).as_posix()}")
        return None

    plan_dir = plan_json.parent
    dir_name = plan_dir.name
    had_plan_suffix = dir_name.endswith("_plan")
    strategy_id = dir_name[:-len("_plan")] if had_plan_suffix else dir_name
    plan_rel = plan_json.relative_to(base).as_posix()

    # Resolve the result dir by the "drop trailing _plan" convention. Only when
    # the dir actually ended with _plan does a DISTINCT result dir exist; without
    # the suffix the result dir would collapse onto the plan dir and the plan's
    # own report.json would be misread as a result — so we stay plan-only there.
    result_dir = plan_dir.parent / strategy_id
    report_rel = run_id = memo_rel = None
    result_obj: Optional[dict] = None
    result_generated_at = None
    if not had_plan_suffix:
        warnings.append(
            f"{strategy_id}: plan dir does not end with '_plan'; result-dir "
            "convention not applied (treated as plan-only)")
    elif result_dir.is_dir():
        try:
            memos = sorted(result_dir.rglob("decision_memo.md"))
        except Exception:  # noqa: BLE001 — presence probe fails closed
            memos = []
        if memos:
            memo_rel = memos[-1].relative_to(base).as_posix()
        try:
            rpts = sorted(p for p in result_dir.rglob("*report*.json"))
        except Exception:  # noqa: BLE001 — presence probe fails closed
            rpts = []
        if rpts:
            rp = rpts[-1]
            robj, rst = _load_json(rp)
            if rst == "ok" and robj is not None:
                result_obj = robj
                report_rel = rp.relative_to(base).as_posix()
                run_id = str(robj.get("run_id", "") or "") or None
                result_generated_at = \
                    str(robj.get("generated_at", "") or "") or None
            else:
                warnings.append(f"{strategy_id}: result report unreadable "
                                f"({rst}): {rp.relative_to(base).as_posix()}")
    else:
        warnings.append(
            f"{strategy_id}: no result dir at "
            f"{result_dir.relative_to(base).as_posix()} (plan-only)")

    # Stage precedence: decision memo > executed result > plan-only.
    if memo_rel is not None:
        stage = "DECISION_RECORDED"
    elif report_rel is not None:
        stage = "EXECUTED"
    else:
        stage = "PLAN_ONLY"

    # Verdict only exists once a result has been produced.
    verdict = clamped_from = None
    if result_obj is not None:
        verdict, clamped_from = _clamp_verdict(
            result_obj.get("pass_watch_fail_status"), warnings, strategy_id)

    # runner_mode: prefer the executed result's config, else the plan's proposal.
    runner_mode = None
    if result_obj is not None:
        runner_mode = str(result_obj.get("config_mode", "") or "") or None
    if runner_mode is None:
        rrd = plan_obj.get("runner_and_reporting_design")
        if isinstance(rrd, dict):
            runner_mode = str(rrd.get("proposed_config_name", "") or "") or None

    # dataset: prefer the result's input dir, else the plan's frozen dataset.
    dataset_str = None
    if result_obj is not None:
        dataset_str = result_obj.get("input_data_dir")
    if not dataset_str:
        fi = plan_obj.get("frozen_inputs_must_remain_unchanged")
        if isinstance(fi, dict):
            dataset_str = fi.get("dataset")
    dataset_id = _derive_dataset_id(dataset_str)

    # status (lane status) from the plan; never promote past the plan's claim.
    status = (str(plan_obj.get("lane_status_unchanged", "") or "").strip()
              or "WATCH")

    plan_date = str(plan_obj.get("plan_date", "") or "") or None

    entry = {
        "strategy_id": strategy_id,
        "strategy_family": _derive_family(runner_mode, strategy_id),
        "market": _derive_market(dataset_id),
        "dataset_id": dataset_id,
        "runner_mode": runner_mode,
        "stage": stage,
        "status": status,
        "verdict": verdict,
        "run_id": run_id,
        "report_path": report_rel,
        "plan_path": plan_rel,
        "decision_memo_path": memo_rel,
        "safety_flags": dict(REGISTRY_SAFETY_FLAGS),
        "next_action": _next_action_for_stage(stage),
        "created_at": plan_date,
        "updated_at": result_generated_at or plan_date,
    }
    if clamped_from is not None:
        entry["verdict_clamped_from"] = clamped_from
        entry["unsafe_verdict_flagged"] = True
    return entry


# ---------------------------------------------------------------------------
# Top-level build (read-only, deterministic, no wall-clock).
# ---------------------------------------------------------------------------

def build_registry(base: Path) -> dict:
    """Scan ``base/reports`` and return the normalized registry dict.

    Pure read: never writes, never runs a subprocess, never touches the
    network. Deterministic given the same on-disk artifacts."""
    base = Path(base)
    warnings: list[str] = []
    reports_dir = base / "reports"
    strategies: list[dict] = []

    if reports_dir.is_dir():
        try:
            plan_files = sorted(reports_dir.glob(PLAN_GLOB),
                                key=lambda p: p.parent.name)
        except Exception:  # noqa: BLE001 — presence probe fails closed
            plan_files = []
            warnings.append("plan scan failed; registry is empty")
        for pj in plan_files:
            entry = _scan_plan(base, pj, warnings)
            if entry is not None:
                strategies.append(entry)
    else:
        warnings.append("no reports/ directory found; registry is empty")

    strategies.sort(key=lambda e: e["strategy_id"])
    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER_NAME,
        "read_only": True,
        "safety_flags": dict(REGISTRY_SAFETY_FLAGS),
        "strategy_count": len(strategies),
        "strategies": strategies,
        "warnings": warnings,
    }


def to_stable_json(registry: dict) -> str:
    """Deterministic JSON text (sorted keys, trailing newline)."""
    return json.dumps(registry, indent=2, sort_keys=True,
                      ensure_ascii=False) + "\n"


def render_markdown(registry: dict) -> str:
    lines = ["# Strategy Report Registry v1 (read-only scan)", ""]
    lines.append(f"- schema_version: {registry.get('schema_version')}")
    lines.append(f"- strategy_count: {registry.get('strategy_count')}")
    lines.append("- safety: research_only=true; paper/live, broker, exchange, "
                 "order paths disabled; no ACTIVE/STRONG; no Bundle 23.")
    lines.append("")
    lines.append("| strategy_id | stage | status | verdict | run_id |")
    lines.append("|---|---|---|---|---|")
    for e in registry.get("strategies", []):
        lines.append("| {sid} | {stage} | {status} | {verdict} | {run} |".format(
            sid=e.get("strategy_id"), stage=e.get("stage"),
            status=e.get("status"), verdict=e.get("verdict"),
            run=e.get("run_id") or "—"))
    warns = registry.get("warnings", [])
    if warns:
        lines += ["", "## Warnings", ""]
        lines += [f"- {w}" for w in warns]
    return "\n".join(lines) + "\n"


def write_build_report(base: Path, registry: dict) -> list[str]:
    """Opt-in: write the registry to the single allowed build folder. Returns
    the repo-relative paths written. Writes nowhere else."""
    out_dir = Path(base) / _BUILD_OUT_RELDIR
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "registry.json"
    md_path = out_dir / "registry.md"
    json_path.write_text(to_stable_json(registry), encoding="utf-8")
    md_path.write_text(render_markdown(registry), encoding="utf-8")
    return [json_path.relative_to(base).as_posix(),
            md_path.relative_to(base).as_posix()]


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Strategy Report Registry v1 scanner.")
    parser.add_argument("--base", default=None,
                        help="repo root (default: auto-detected)")
    parser.add_argument("--format", choices=("json", "md"), default="json")
    parser.add_argument(
        "--write", action="store_true",
        help="ALSO write registry.json/.md to "
             "reports/strategy_factory_registry_v1_build/ (read-only otherwise)")
    args = parser.parse_args(argv)

    base = Path(args.base) if args.base else _repo_root()
    registry = build_registry(base)
    if args.write:
        written = write_build_report(base, registry)
        sys.stderr.write("wrote: " + ", ".join(written) + "\n")
    sys.stdout.write(render_markdown(registry) if args.format == "md"
                     else to_stable_json(registry))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())

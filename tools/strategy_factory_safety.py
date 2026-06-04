"""SPARTA Strategy Factory v1 — Step 3: Safety Contract schema + validator.

A tiny, deterministic, standard-library-only loader and FAIL-CLOSED validator for
the central safety contract ``configs/strategy_factory_safety.json``. EVERY future
Strategy Factory component (queue, orchestrator, runner-adapter, dashboard feed)
must validate against this contract before any research task may even be
*considered*. This module ONLY loads, validates, and re-describes that contract —
plus an optional read-only integration check of the research queue against it.

Hard guarantees (asserted by tests/test_strategy_factory_safety.py):
  * NEVER executes. No subprocess, no network, no runner import, no broker /
    exchange / order / fetch path. It only reads JSON and re-describes it.
  * FAIL CLOSED. A missing file, malformed JSON, a missing required key, any
    forbidden flag set true, or an unknown runner/dataset/mode/market makes the
    result UNSAFE (``safe=False``) — never an exception, never silent.
  * AUTHORIZES NOTHING. ``research_only`` must be true; every execution / paper /
    live / broker / exchange / order / fetch / promotion / Bundle-23 flag must be
    present and false; human approval is required for execution, paper/live, and
    promotion.
  * DETERMINISTIC. Normalized output has sorted allowlists / sorted-key JSON and
    no wall-clock dependence.
  * If output is written at all (``--write``), it goes ONLY to
    ``reports/strategy_factory_safety_v1_build/`` — never to the dashboard,
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
LAYER_NAME = "strategy_factory_safety_v1"

_SAFETY_RELPATH = Path("configs") / "strategy_factory_safety.json"
_QUEUE_RELPATH = Path("configs") / "research_queue.json"

# Canonical allowlists — the contract may declare nothing beyond these in v1.
CANON_DATASETS = frozenset({"CRYPTO_D1_SPOT_BTC_ETH_SOL_V001_V002"})
CANON_RUNNERS = frozenset({"tools/crypto_d1_backtest_runner.py"})
CANON_MODES = frozenset({"momentum_confirmation_v1"})
CANON_MARKETS = frozenset({"crypto"})

# Required top-level keys the contract must carry.
REQUIRED_TOP_KEYS = (
    "schema_version", "layer", "research_only", "safety_flags",
    "allowed_datasets", "allowed_runners", "allowed_modes", "allowed_markets",
    "forbidden_terms", "human_approval",
)

# Safety flags: research_only must be True; every other flag must be present and
# False. ``fetch_live_data_enabled`` covers the fetch/live-data path.
_FLAG_MUST_BE_TRUE = "research_only"
_FLAGS_MUST_BE_FALSE = (
    "paper_live_authorized",
    "broker_path_enabled",
    "exchange_path_enabled",
    "order_path_enabled",
    "fetch_live_data_enabled",
    "dataset_mutation_allowed",
    "active_strong_promoted",
    "bundle_23_started",
    "execution_authorized",
)
REQUIRED_SAFETY_FLAGS = (_FLAG_MUST_BE_TRUE,) + _FLAGS_MUST_BE_FALSE

# Forbidden terms every component must screen candidate values/paths against.
REQUIRED_FORBIDDEN_TERMS = (
    "broker", "exchange", "order", "live", "paper", "fetch",
    "kraken", "binance live", "ACTIVE", "STRONG", "Bundle 23",
)

# Human-approval gates — all three must be present and True.
REQUIRED_HUMAN_APPROVAL = (
    "human_approval_required_for_execution",
    "human_approval_required_for_paper_live",
    "human_approval_required_for_promotion",
)

# Pinned-false posture surfaced on the result envelope. Constants.
CONTRACT_SAFETY_FLAGS = {
    "research_only": True,
    "paper_live_authorized": False,
    "broker_path_enabled": False,
    "exchange_path_enabled": False,
    "order_path_enabled": False,
    "fetch_live_data_enabled": False,
    "dataset_mutation_allowed": False,
    "active_strong_promoted": False,
    "bundle_23_started": False,
    "execution_authorized": False,
}

# Output is opt-in and confined to this single build folder.
_BUILD_OUT_RELDIR = Path("reports") / "strategy_factory_safety_v1_build"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# IO — fail closed.
# ---------------------------------------------------------------------------

def load_safety_file(path: Path) -> tuple[Optional[dict], str]:
    """Return (obj, status). status in {'ok', 'missing', 'error'}."""
    try:
        path = Path(path)
        if not path.is_file():
            return None, "missing"
        obj = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            return None, "error"
        return obj, "ok"
    except Exception:  # noqa: BLE001 — fail closed; caller records a reason
        return None, "error"


# ---------------------------------------------------------------------------
# Forbidden-term screening (applies to CANDIDATE values, not the contract's own
# metadata — the contract legitimately names "broker"/"order"/etc. in its
# forbidden_terms list and flag names).
# ---------------------------------------------------------------------------

def screen_text(text: Any, forbidden_terms) -> list[str]:
    """Return the sorted forbidden terms found in ``text`` (case-insensitive)."""
    s = str(text or "").lower()
    hits = {term for term in forbidden_terms if str(term).lower() in s}
    return sorted(hits)


# ---------------------------------------------------------------------------
# Contract structure validation (pure, deterministic, fail-closed).
# ---------------------------------------------------------------------------

def _unsafe(reason: str, *, valid: bool = False,
           source: Optional[str] = None) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER_NAME,
        "read_only": True,
        "executes_anything": False,
        "source": source,
        "valid": valid,
        "safe": False,
        "blocked_reasons": [reason],
        "warnings": [],
        "normalized_contract": None,
        "safety_flags": dict(CONTRACT_SAFETY_FLAGS),
    }


def validate_contract(contract_obj: Optional[dict], *, load_status: str = "ok",
                      source: Optional[str] = None) -> dict:
    """Validate an in-memory safety contract; return the result object.

    Result fields: valid, safe, blocked_reasons, warnings, normalized_contract,
    safety_flags. Never raises.
    """
    if load_status == "missing":
        return _unsafe("safety contract file not found (fail-closed: UNSAFE)",
                       source=source)
    if load_status == "error" or not isinstance(contract_obj, dict):
        return _unsafe("safety contract unreadable / malformed JSON "
                       "(fail-closed: UNSAFE)", source=source)

    blocked: list[str] = []
    warnings: list[str] = []

    # 1) Required top-level keys.
    for key in REQUIRED_TOP_KEYS:
        if key not in contract_obj:
            blocked.append(f"missing required key: {key}")

    # 2) research_only must be True.
    if contract_obj.get("research_only") is not True:
        blocked.append("research_only must be true")

    # 3) Safety flags: research_only True; all others present and False.
    flags = contract_obj.get("safety_flags")
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

    # 4) Allowlists: present, non-empty, and nothing outside the canonical set.
    norm_datasets = _check_allowlist(
        contract_obj.get("allowed_datasets"), CANON_DATASETS,
        "allowed_datasets", "dataset", blocked)
    norm_runners = _check_allowlist(
        contract_obj.get("allowed_runners"), CANON_RUNNERS,
        "allowed_runners", "runner", blocked)
    norm_modes = _check_allowlist(
        contract_obj.get("allowed_modes"), CANON_MODES,
        "allowed_modes", "mode", blocked)
    norm_markets = _check_allowlist(
        contract_obj.get("allowed_markets"), CANON_MARKETS,
        "allowed_markets", "market", blocked)

    # 5) Forbidden terms: must include every required term.
    raw_terms = contract_obj.get("forbidden_terms")
    if not isinstance(raw_terms, list):
        blocked.append("forbidden_terms missing or not a list")
        norm_terms: list[str] = []
    else:
        norm_terms = [str(t) for t in raw_terms]
        lowered = {t.lower() for t in norm_terms}
        for term in REQUIRED_FORBIDDEN_TERMS:
            if term.lower() not in lowered:
                blocked.append(f"forbidden_terms missing required term: {term}")

    # 6) Human approval gates: all three present and True.
    approval = contract_obj.get("human_approval")
    if not isinstance(approval, dict):
        blocked.append("human_approval missing or not an object")
        approval = {}
    else:
        for gate in REQUIRED_HUMAN_APPROVAL:
            if approval.get(gate) is not True:
                blocked.append(f"human_approval.{gate} must be true")

    safe = len(blocked) == 0
    normalized = {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER_NAME,
        "research_only": True,
        "safety_flags": dict(CONTRACT_SAFETY_FLAGS),
        "allowed_datasets": norm_datasets,
        "allowed_runners": norm_runners,
        "allowed_modes": norm_modes,
        "allowed_markets": norm_markets,
        "forbidden_terms": sorted(set(norm_terms)) if norm_terms else [],
        "human_approval": {g: True for g in REQUIRED_HUMAN_APPROVAL},
    } if safe else None

    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER_NAME,
        "read_only": True,
        "executes_anything": False,
        "source": source,
        "valid": True,
        "safe": safe,
        "blocked_reasons": sorted(set(blocked)),
        "warnings": warnings,
        "normalized_contract": normalized,
        "safety_flags": dict(CONTRACT_SAFETY_FLAGS),
    }


def _check_allowlist(raw: Any, canon: frozenset, key: str, noun: str,
                     blocked: list[str]) -> list[str]:
    if not isinstance(raw, list) or not raw:
        blocked.append(f"{key} missing or empty")
        return sorted(canon)
    values = [str(v).replace("\\", "/") for v in raw]
    for v in values:
        if v not in canon:
            blocked.append(f"unknown {noun} not allowed by contract: {v}")
    return sorted(set(values))


# ---------------------------------------------------------------------------
# Read-only integration: screen a candidate task against a SAFE contract.
# ---------------------------------------------------------------------------

def validate_task_against_contract(task: Any, normalized_contract: dict) -> dict:
    """Check one queue-style task against the normalized contract. Returns a
    per-task result: contract_conformant, allowed_for_listing, executable
    (always False), blocked_reasons. Never raises, never executes."""
    blocked: list[str] = []
    nc = normalized_contract or {}
    runners = set(nc.get("allowed_runners", []))
    datasets = set(nc.get("allowed_datasets", []))
    modes = set(nc.get("allowed_modes", []))
    markets = set(nc.get("allowed_markets", []))
    terms = nc.get("forbidden_terms", [])

    if not isinstance(task, dict):
        return {
            "task_id": None,
            "contract_conformant": False,
            "allowed_for_listing": False,
            "executable": False,
            "blocked_reasons": ["task is not a JSON object"],
        }

    task_id = task.get("task_id")
    runner = str(task.get("allowed_runner") or "").replace("\\", "/")
    dataset = str(task.get("dataset_id") or "")
    mode = str(task.get("allowed_mode") or "")
    market = str(task.get("market") or "")

    if runner not in runners:
        blocked.append(f"runner not allowed by contract: {runner or '<empty>'}")
    if dataset not in datasets:
        blocked.append(f"dataset not allowed by contract: {dataset or '<empty>'}")
    if mode not in modes:
        blocked.append(f"mode not allowed by contract: {mode or '<empty>'}")
    if market not in markets:
        blocked.append(f"market not allowed by contract: {market or '<empty>'}")

    # Forbidden-term screen on the candidate identifiers (NOT the allowlisted
    # values themselves, which are clean by construction — this catches a task
    # that smuggles a broker/order/live/etc. token into its own fields).
    for field in ("task_id", "strategy_id", "strategy_family", "next_action"):
        hits = screen_text(task.get(field), terms)
        if hits:
            blocked.append(f"forbidden term(s) in {field}: {', '.join(hits)}")

    # Safety flags on the task must conform.
    flags = task.get("safety_flags")
    if not isinstance(flags, dict):
        blocked.append("task safety_flags missing or not an object")
    else:
        if flags.get("research_only") is not True:
            blocked.append("task safety_flags.research_only must be true")
        for flag in _FLAGS_MUST_BE_FALSE:
            if flags.get(flag) is True:
                blocked.append(f"task forbidden safety flag is true: {flag}")

    if task.get("execution_authorized") is True:
        blocked.append("task execution_authorized is true (forbidden)")

    conformant = len(blocked) == 0
    return {
        "task_id": str(task_id) if task_id not in (None, "") else None,
        "contract_conformant": conformant,
        # The contract permits LISTING a conformant task. This is NOT execution.
        "allowed_for_listing": conformant,
        # v1 invariant: nothing is ever executable.
        "executable": False,
        "blocked_reasons": sorted(set(blocked)),
    }


def validate_queue_against_contract(base: Path, contract_result: dict) -> dict:
    """Read-only integration check: load research_queue.json and screen every
    item against the (safe) normalized contract. Never imports a runner."""
    base = Path(base)
    nc = contract_result.get("normalized_contract")
    if not contract_result.get("safe") or not nc:
        return {
            "checked": False,
            "reason": "contract is unsafe; queue not screened",
            "items": [],
        }
    obj, status = load_safety_file(base / _QUEUE_RELPATH)
    if status != "ok" or not isinstance(obj, dict):
        return {
            "checked": False,
            "reason": f"research_queue.json {status}",
            "items": [],
        }
    raw_items = obj.get("items")
    raw_items = raw_items if isinstance(raw_items, list) else []
    items = [validate_task_against_contract(it, nc) for it in raw_items]
    items.sort(key=lambda e: e.get("task_id") or "")
    return {
        "checked": True,
        "source": _QUEUE_RELPATH.as_posix(),
        "item_count": len(items),
        "conformant_count": sum(1 for e in items if e["contract_conformant"]),
        "items": items,
    }


# ---------------------------------------------------------------------------
# Top-level build (read-only, deterministic).
# ---------------------------------------------------------------------------

def build(base: Path) -> dict:
    """Load + validate the contract, then run the read-only queue integration.

    Pure read: never writes, never runs a subprocess, never touches the network,
    never imports a runner. Deterministic given the same on-disk files.
    """
    base = Path(base)
    obj, status = load_safety_file(base / _SAFETY_RELPATH)
    source = _SAFETY_RELPATH.as_posix() if status != "missing" else None
    result = validate_contract(obj, load_status=status, source=source)
    result["queue_integration"] = validate_queue_against_contract(base, result)
    return result


def to_stable_json(result: dict) -> str:
    """Deterministic JSON text (sorted keys, trailing newline)."""
    return json.dumps(result, indent=2, sort_keys=True,
                      ensure_ascii=False) + "\n"


def render_markdown(result: dict) -> str:
    lines = ["# Strategy Factory Safety Contract v1 (read-only validator)", ""]
    lines.append(f"- schema_version: {result.get('schema_version')}")
    lines.append(f"- valid: {result.get('valid')}  |  **safe: "
                 f"{result.get('safe')}**")
    lines.append("- posture: research_only=true; execution/paper/live/broker/"
                 "exchange/order/fetch disabled; no ACTIVE/STRONG; no Bundle 23; "
                 "human approval required for execution, paper/live, promotion.")
    blocked = result.get("blocked_reasons") or []
    if blocked:
        lines += ["", "## Blocked reasons (UNSAFE)", ""]
        lines += [f"- {r}" for r in blocked]
    qi = result.get("queue_integration") or {}
    if qi.get("checked"):
        lines += ["", "## Queue integration (read-only)", ""]
        lines.append(f"- item_count: {qi.get('item_count')}, conformant: "
                     f"{qi.get('conformant_count')}")
        lines.append("| task_id | contract_conformant | allowed_for_listing | "
                     "executable |")
        lines.append("|---|---|---|---|")
        for e in qi.get("items", []):
            lines.append("| {t} | {c} | {l} | {x} |".format(
                t=e.get("task_id"), c=e.get("contract_conformant"),
                l=e.get("allowed_for_listing"), x=e.get("executable")))
    warns = result.get("warnings") or []
    if warns:
        lines += ["", "## Warnings", ""]
        lines += [f"- {w}" for w in warns]
    return "\n".join(lines) + "\n"


def write_build_report(base: Path, result: dict) -> list[str]:
    """Opt-in: write the validation result to the single allowed build folder.
    Returns the repo-relative paths written. Writes nowhere else."""
    out_dir = Path(base) / _BUILD_OUT_RELDIR
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "safety.json"
    md_path = out_dir / "safety.md"
    json_path.write_text(to_stable_json(result), encoding="utf-8")
    md_path.write_text(render_markdown(result), encoding="utf-8")
    return [json_path.relative_to(base).as_posix(),
            md_path.relative_to(base).as_posix()]


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only Strategy Factory Safety Contract v1 validator "
                    "(loads + validates only; executes nothing).")
    parser.add_argument("--base", default=None,
                        help="repo root (default: auto-detected)")
    parser.add_argument("--format", choices=("json", "md"), default="json")
    parser.add_argument(
        "--write", action="store_true",
        help="ALSO write safety.json/.md to "
             "reports/strategy_factory_safety_v1_build/ (read-only otherwise)")
    args = parser.parse_args(argv)

    base = Path(args.base) if args.base else _repo_root()
    result = build(base)
    if args.write:
        written = write_build_report(base, result)
        sys.stderr.write("wrote: " + ", ".join(written) + "\n")
    sys.stdout.write(render_markdown(result) if args.format == "md"
                     else to_stable_json(result))
    # Non-zero exit on UNSAFE so a caller can gate on it.
    return 0 if result.get("safe") else 2


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())

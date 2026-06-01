"""SPARTA Strategy Factory — Next Bundle Generator v1 (research-only).

Reads existing Strategy Factory Routine Layer runtime outputs (queue, daily state,
weekly review, JARVIS snapshot) and produces the exact next Claude/Codex prompt
bundle for the highest-value next research or JARVIS task.

Hard non-negotiable guarantees (enforced by tests):
  * Read-only with respect to all research inputs.
  * No broker control, no exchange/Alpaca API, no order placement.
  * No live trading, no paper-order execution, no autonomous trade decision.
  * No network calls, no credentials, no .env, no scheduler/daemon.
  * Standard library only -- no imports beyond stdlib.
  * Writes ONLY inside reports/strategy_factory_routines/next_bundle/.

The three trading-safety flags below are pinned False everywhere and asserted by
the test suite:
  live_trading_enabled / broker_control_enabled / paper_order_execution_enabled

This module imports nothing beyond the Python standard library.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
LAYER = "strategy_factory_next_bundle_generator_v1"

# Pinned-False safety invariants. Constants, never computed True.
SAFETY_FLAGS = {
    "live_trading_enabled": False,
    "broker_control_enabled": False,
    "paper_order_execution_enabled": False,
}

SAFETY_NOTES = [
    "Research-only Next Bundle Generator. Reads queue + state; never executes.",
    "No broker, no exchange/Alpaca API, no order placement, no paper/live.",
    "No network calls, no credentials, no scheduler/daemon.",
    "Outputs are prompt + report files for human + Claude review only.",
]

FORBIDDEN_ACTIONS_BASE = (
    "no_broker_control",
    "no_live_trading",
    "no_paper_order_execution",
    "no_order_placement",
    "no_external_network_calls",
    "no_api_keys_or_credentials",
    "no_scheduler_or_daemon",
    "no_modification_of_paper_or_live_execution_files",
)

# Substrings (lowercase) that imply danger; any match in an item rejects it as
# defense-in-depth (in addition to the safety_level / blocked filter).
DANGER_KEYWORDS_REJECT = (
    "broker", "live trading", "live trade", "live_trade", "live-trade",
    "place order", "order placement", "order_placement", "order execution",
    "paper order", "paper_order", "paper-order",
    "alpaca", "ibkr", "exchange api", "binance api",
    "credential", "api key", "api_key", "secret token",
    "scheduler", "background daemon", "cron install",
)

# Preference hints (case-insensitive substring matching against title/lane/reason).
COPY_PASTE_REDUCE_HINTS = (
    "summary", "registry", "checklist", "report", "snapshot", "scaffold",
    "memo", "template", "automation", "panel",
)
VALIDATION_QUALITY_HINTS = (
    "validation", "qa", "audit", "freeze", "data contract", "data-contract",
    "pre-registration", "preregistration", "prereg", "decision gate",
)
EDGE_HINTS = (
    "evidence", "edge", "oos", "out-of-sample", "live-grade", "live grade", "k9",
)
PROTOCOL_FIRST_HINTS = (
    "protocol", "spec ", " spec", "pre-registration", "prereg",
    "specification", "memo", "data contract", "data-contract",
)
DATA_FIRST_HINTS = (
    "data qa", "data freeze", "data contract", "data-contract",
    "data hygiene", "data integrity",
)
JARVIS_HINTS = ("jarvis", "automation", "dashboard", "commander", "panel")
CRYPTO_HINTS = ("crypto", "btc", "eth", "sol")

REPO_ROOT = Path(__file__).resolve().parent.parent

# Source files (read-only).
QUEUE_REL = "reports/strategy_factory_routines/strategy_queue/queue.json"
DAILY_REL = "reports/strategy_factory_routines/daily_state/latest_state.json"
WEEKLY_REL = "reports/strategy_factory_routines/weekly_review/latest_weekly_review.json"
# Optional input (Bundle 3 — registry). Used to skip FAILED/RETIRED lanes and
# bonus-score ACTIVE/WATCH lanes. Tool degrades gracefully if absent.
REGISTRY_REL = "reports/strategy_factory_routines/candidate_registry/candidates.json"
SNAPSHOT_REL = "storage/jarvis/strategy_factory/latest_strategy_factory_snapshot.json"

# Output (runtime; gitignored).
OUTPUT_DIR_REL = "reports/strategy_factory_routines/next_bundle"
OUTPUT_JSON = "next_bundle.json"
OUTPUT_MD = "next_bundle.md"
OUTPUT_PROMPT = "next_claude_prompt.txt"

REQUIRED_JSON_KEYS = (
    "generated_at", "selected_bundle_id", "title", "lane", "reason", "priority",
    "blocked", "safety_level", "required_inputs", "expected_outputs",
    "forbidden_actions", "allowed_paths", "forbidden_paths", "tests_to_run",
    "acceptance_criteria", "rollback_notes", "next_claude_prompt_path",
    "source_files_read", "warnings",
)


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _lower(value: Any) -> str:
    return str(value or "").lower()


def _contains_any(haystack: str, needles) -> bool:
    return any(n in haystack for n in needles)


def _read_json_safe(path: Path) -> tuple[Any, str | None]:
    """Return (data_or_None, error_or_None). Never raises on missing/invalid."""
    if not path.exists():
        return None, f"missing: {path.as_posix()}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001 — graceful: any read/parse error is reported as text
        return None, f"invalid: {path.as_posix()} ({type(exc).__name__}: {exc!s:.120})"


def _is_research_only_safety(level: Any) -> bool:
    return _lower(level).strip() in {"research_only", "analysis_only", "read_only"}


def _item_blob(item: dict) -> str:
    return " ".join([
        _lower(item.get("title")),
        _lower(item.get("lane")),
        _lower(item.get("reason")),
        _lower(item.get("expected_output")),
        _lower(item.get("next_bundle_suggestion")),
        " ".join(_lower(r) for r in (item.get("required_inputs") or [])),
    ])


def _has_danger_signals(item: dict) -> tuple[bool, list]:
    blob = _item_blob(item)
    hits = [k for k in DANGER_KEYWORDS_REJECT if k in blob]
    return (bool(hits), hits)


def _score_item(item: dict, context: dict) -> tuple[int, dict]:
    """Deterministic integer score plus a per-axis breakdown for transparency."""
    weekly = context.get("weekly") or {}
    daily = context.get("daily") or {}
    blob = _item_blob(item)
    lane = _lower(item.get("lane"))

    breakdown: dict[str, int] = {}

    # Priority weight (assume 1 = highest, 10 = lowest; clamp).
    try:
        p = int(item.get("priority"))
    except (TypeError, ValueError):
        p = 5
    p = max(1, min(p, 10))
    breakdown["priority_weight"] = (10 - p) * 10

    # Weekly-review match.
    target = _lower(weekly.get("lane_deserving_next_deep_bundle"))
    breakdown["weekly_deep_bundle_match"] = (
        50 if target and (lane == target or target in lane or lane in target) else 0
    )

    # Active lane bonus.
    active_lanes = [_lower(x) for x in (daily.get("active_lanes") or [])]
    breakdown["active_lane_bonus"] = (
        20 if lane and any(lane == al or lane in al or al in lane for al in active_lanes) else 0
    )

    # Wasting time -> penalty.
    waste = [_lower(x) for x in (weekly.get("lanes_wasting_time") or [])]
    breakdown["wasting_time_penalty"] = (
        -30 if lane and any(lane == w or lane in w or w in lane for w in waste) else 0
    )

    # Preference signals (substring heuristics on title/lane/reason/expected).
    breakdown["reduces_copy_paste"] = 25 if _contains_any(blob, COPY_PASTE_REDUCE_HINTS) else 0
    breakdown["improves_validation_quality"] = 20 if _contains_any(blob, VALIDATION_QUALITY_HINTS) else 0
    breakdown["closer_to_real_edge"] = 15 if _contains_any(blob, EDGE_HINTS) else 0
    breakdown["protocol_first_pref"] = 30 if _contains_any(blob, PROTOCOL_FIRST_HINTS) else 0
    breakdown["data_first_pref"] = 30 if _contains_any(blob, DATA_FIRST_HINTS) else 0

    # JARVIS / automation: small boost when no active lane (improves visibility).
    if _contains_any(blob, JARVIS_HINTS):
        breakdown["jarvis_automation"] = 10 if not active_lanes else 5

    # Crypto separation: if any non-crypto active lane is running, prefer non-crypto.
    if _contains_any(blob, CRYPTO_HINTS):
        non_crypto_active = any(al and not _contains_any(al, CRYPTO_HINTS) for al in active_lanes)
        breakdown["crypto_separation_penalty"] = -15 if non_crypto_active else 0

    # Registry-aware bonus: ACTIVE/WATCH candidates score higher (Bundle 3 integration).
    # If no registry is loaded, the index is empty and this axis contributes 0.
    registry = context.get("registry_by_lane") or {}
    reg = registry.get(lane) or {}
    status = _lower(reg.get("status")) if reg else ""
    if status == "active":
        breakdown["registry_active_bonus"] = 25
    elif status == "watch":
        breakdown["registry_watch_bonus"] = 15

    # Defense-in-depth: hard penalty if any danger keyword slipped past the filter.
    danger, _ = _has_danger_signals(item)
    breakdown["danger_signal_penalty"] = -200 if danger else 0

    return sum(breakdown.values()), breakdown


_REGISTRY_REJECT_STATUSES = {"failed", "retired"}


def _filter_eligible(queue, registry_by_lane=None) -> list:
    """Drop blocked / non-research_only / danger-keyword items, plus any item
    whose lane is marked FAILED or RETIRED in the optional candidate registry."""
    reg = registry_by_lane or {}
    out = []
    for item in queue:
        if not isinstance(item, dict):
            continue
        if item.get("blocked") is True:
            continue
        if not _is_research_only_safety(item.get("safety_level")):
            continue
        danger, _ = _has_danger_signals(item)
        if danger:
            continue
        lane = _lower(item.get("lane"))
        reg_item = reg.get(lane) or {}
        if _lower(reg_item.get("status")) in _REGISTRY_REJECT_STATUSES:
            continue
        out.append(item)
    return out


def select_bundle(queue, context: dict) -> tuple:
    """Return (selected_item_or_None, ranked_breakdown_list). Deterministic."""
    eligible = _filter_eligible(queue or [], context.get("registry_by_lane"))
    scored = []
    for item in eligible:
        score, br = _score_item(item, context)
        scored.append({
            "title": item.get("title"),
            "lane": item.get("lane"),
            "priority": item.get("priority"),
            "score": score,
            "breakdown": br,
        })
    pairs = list(zip(eligible, scored))
    # Deterministic ordering: score desc, then lane asc, then title asc.
    pairs.sort(key=lambda x: (
        -x[1]["score"],
        str(x[0].get("lane") or ""),
        str(x[0].get("title") or ""),
    ))
    ranked = [s for _, s in pairs]
    if not pairs:
        return None, ranked
    return pairs[0][0], ranked


def build_bundle_payload(repo_root: Path = REPO_ROOT) -> dict:
    """Read all inputs, choose next bundle, return the full JSON payload."""
    queue_data, q_err = _read_json_safe(repo_root / QUEUE_REL)
    daily_data, d_err = _read_json_safe(repo_root / DAILY_REL)
    weekly_data, w_err = _read_json_safe(repo_root / WEEKLY_REL)
    snapshot_data, s_err = _read_json_safe(repo_root / SNAPSHOT_REL)
    # Bundle 3 optional input: candidate registry. Missing is normal.
    registry_data, r_err = _read_json_safe(repo_root / REGISTRY_REL)

    warnings = [e for e in (q_err, d_err, w_err, s_err) if e]
    # r_err is intentionally NOT a warning when missing: the registry is optional.
    registry_state = "ready" if registry_data is not None else ("missing" if (r_err and r_err.startswith("missing")) else "missing_or_invalid")
    source_files_read = [
        {"name": "strategy_queue/queue.json", "state": "missing_or_invalid" if q_err else "ready", "detail": q_err},
        {"name": "daily_state/latest_state.json", "state": "missing_or_invalid" if d_err else "ready", "detail": d_err},
        {"name": "weekly_review/latest_weekly_review.json", "state": "missing_or_invalid" if w_err else "ready", "detail": w_err},
        {"name": "jarvis/latest_strategy_factory_snapshot.json", "state": "missing_or_invalid" if s_err else "ready", "detail": s_err},
        {"name": "candidate_registry/candidates.json (optional)", "state": registry_state, "detail": r_err},
    ]

    queue_list = []
    if isinstance(queue_data, dict):
        q = queue_data.get("queue")
        if isinstance(q, list):
            queue_list = [it for it in q if isinstance(it, dict)]

    registry_by_lane: dict = {}
    if isinstance(registry_data, dict):
        for c in (registry_data.get("candidates") or []):
            if isinstance(c, dict) and c.get("lane"):
                registry_by_lane[_lower(c.get("lane"))] = c

    context = {
        "queue": queue_list,
        "daily": daily_data if isinstance(daily_data, dict) else {},
        "weekly": weekly_data if isinstance(weekly_data, dict) else {},
        "snapshot": snapshot_data if isinstance(snapshot_data, dict) else {},
        "registry_by_lane": registry_by_lane,
    }

    selected, ranked = select_bundle(queue_list, context)

    bundle_id = ""
    if selected:
        slug = _lower(selected.get("title")).replace(" ", "_").replace("/", "_")[:50]
        bundle_id = f"{_lower(selected.get('lane')) or 'unknown'}__{slug or 'untitled'}"

    forbidden_paths = [
        "paper_trading/weekly_rs_s21_forward_paper_harness/cycle.py",
        "paper_trading/weekly_rs_s21_forward_paper_harness/safety.py",
        "paper_trading/weekly_rs_s21_forward_paper_harness/manifest.py",
        "paper_trading/weekly_rs_s21_forward_paper_harness/portfolio.py",
        "paper_trading/weekly_rs_s21_forward_paper_harness/signal.py",
        "paper_trading/weekly_rs_s21_forward_paper_harness/killswitch.py",
        "paper_trading/weekly_rs_s21_forward_paper_harness/runs/",
        "data/s21_d1_weekly_rs_rotation_fresh_universe_long_history/",
        "data/branch_multi_market_bad_regime_predictor/oos_2025_sealed/",
        "local_secrets/",
        "brain_memory/projects/trading_bot/lessons.md",
    ]
    allowed_paths = [
        "tools/strategy_factory_routines.py (read-only reference)",
        "tools/strategy_next_bundle.py (this generator)",
        "reports/strategy_factory_routines/ (read-only inputs; write only inside next_bundle/)",
        "storage/jarvis/strategy_factory/latest_strategy_factory_snapshot.json (read-only)",
        "tests/ (add new tests for the proposed bundle; --rootdir=tests)",
        "reports/strategy_factory_next_bundle_generator/ (trackable docs)",
    ]

    tests_to_run = ["python -m pytest tests/test_strategy_next_bundle.py --rootdir=tests -q"]

    if selected:
        sel_blob = _item_blob(selected)
        if any(t in sel_blob for t in ("test", "qa", "validation", "spec")):
            tests_to_run.append("the proposed bundle's own pytest suite (research-only; --rootdir=tests)")
        title = selected.get("title")
        lane = selected.get("lane")
        priority = selected.get("priority")
        blocked = bool(selected.get("blocked"))
        safety_level = selected.get("safety_level")
        reason = selected.get("reason")
        required_inputs = list(selected.get("required_inputs") or [])
        expected_outputs = [selected.get("expected_output")] if selected.get("expected_output") else []
        next_claude_suggestion = selected.get("next_bundle_suggestion") or ""
    else:
        title = "(no eligible bundle in queue)"
        lane = None
        priority = None
        blocked = False
        safety_level = None
        reason = "Queue is empty or every item is blocked/unsafe/contains danger signals."
        required_inputs = []
        expected_outputs = []
        next_claude_suggestion = ""

    forbidden_actions = list(FORBIDDEN_ACTIONS_BASE)
    acceptance_criteria = [
        "All required inputs are listed; missing inputs are reported as warnings, never silently ignored.",
        "Generated outputs land ONLY inside reports/strategy_factory_routines/next_bundle/.",
        "The three trading-safety flags stay pinned False everywhere.",
        "The bundle's tests pass with --rootdir=tests.",
        "Generator imports nothing beyond Python standard library.",
        "No file written outside the output folder.",
        "No file read outside the source list reported in source_files_read.",
        "The selected item is not blocked and has safety_level in {research_only, analysis_only, read_only}.",
    ]

    payload = {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER,
        "kind": "next_bundle",
        "read_only": True,
        "generated_at": _now_utc(),
        "selected_bundle_id": bundle_id,
        "title": title,
        "lane": lane,
        "reason": reason,
        "priority": priority,
        "blocked": blocked,
        "safety_level": safety_level,
        "required_inputs": required_inputs,
        "expected_outputs": expected_outputs,
        "forbidden_actions": forbidden_actions,
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "tests_to_run": tests_to_run,
        "acceptance_criteria": acceptance_criteria,
        "rollback_notes": (
            "All generator outputs are gitignored runtime artifacts. Deleting "
            "reports/strategy_factory_routines/next_bundle/ restores prior state. "
            "The generator never modifies inputs or any paper/live execution file."
        ),
        "next_claude_prompt_path": (Path(OUTPUT_DIR_REL) / OUTPUT_PROMPT).as_posix(),
        "source_files_read": source_files_read,
        "warnings": warnings,
        "ranked_candidates": ranked,
        "context_snapshot": {
            "weekly_lane_deserving_next_deep_bundle": weekly_data.get("lane_deserving_next_deep_bundle") if isinstance(weekly_data, dict) else None,
            "lanes_wasting_time": weekly_data.get("lanes_wasting_time") if isinstance(weekly_data, dict) else [],
            "active_lanes": daily_data.get("active_lanes") if isinstance(daily_data, dict) else [],
            "snapshot_color": snapshot_data.get("commander_color") if isinstance(snapshot_data, dict) else None,
            "snapshot_posture": snapshot_data.get("posture") if isinstance(snapshot_data, dict) else None,
        },
        "safety_flags": dict(SAFETY_FLAGS),
        "safety_notes": list(SAFETY_NOTES),
        "next_claude_suggestion_from_queue": next_claude_suggestion,
    }
    return payload


def render_markdown(payload: dict) -> str:
    lines = [
        "# Next Bundle — selected",
        "",
        f"**Title:** {payload['title']}  ",
        f"**Lane:** {payload.get('lane') or '—'}  ",
        f"**Priority:** {payload.get('priority')}  ",
        f"**Generated:** {payload['generated_at']}",
        "",
        "## Why this is the best next step",
        payload.get("reason") or "—",
        "",
        "## What this bundle will build",
    ]
    for eo in (payload.get("expected_outputs") or ["(none listed)"]):
        lines.append(f"- {eo}")
    lines += ["", "## What this bundle must NOT touch"]
    for fp in payload["forbidden_paths"]:
        lines.append(f"- {fp}")
    lines += ["", "## Safety rules (pinned, never relaxed)"]
    for fa in payload["forbidden_actions"]:
        lines.append(f"- {fa}")
    for note in payload["safety_notes"]:
        lines.append(f"- {note}")
    lines += ["", "## Expected commands / tests"]
    for t in payload["tests_to_run"]:
        lines.append(f"- `{t}`")
    lines += [
        "",
        "## Commit boundary",
        "- Do not stage, commit, or push unless separately authorized by the operator.",
        "- Use explicit pathspecs only (`git commit -- <paths>`); never `git add .`.",
        "",
        "## Paste this into Claude next",
        f"See `{payload['next_claude_prompt_path']}` (ready to copy/paste).",
        "",
        "## Ranked candidates",
        "| Rank | Score | Lane | Title |",
        "| ---: | ---: | --- | --- |",
    ]
    for i, r in enumerate(payload["ranked_candidates"], 1):
        lines.append(f"| {i} | {r['score']} | {r.get('lane') or '—'} | {r.get('title') or '—'} |")
    if payload.get("warnings"):
        lines += ["", "## Warnings"]
        for w in payload["warnings"]:
            lines.append(f"- {w}")
    return "\n".join(lines) + "\n"


def render_prompt(payload: dict) -> str:
    parts = [
        "You are working in the existing SPARTA_BRAIN repo.",
        "",
        f"BUNDLE: {payload['title']}",
        f"LANE:   {payload.get('lane') or '(unknown)'}",
        "",
        "MISSION:",
        payload.get("reason") or payload.get("next_claude_suggestion_from_queue") or "(none captured)",
        "",
        "CURRENT COMMITTED CHECKPOINTS (DO NOT REVERT):",
        "* Strategy Factory Routine Layer v1 — 98f8918 (committed + pushed)",
        "* JARVIS Strategy Factory Dashboard Integration — 5fe3107 (committed + pushed)",
        "* Next Bundle Generator v1 — local generator producing this prompt",
        "",
        "BEFORE STARTING:",
        "1. git status --short  (must be clean)",
        "2. git log --oneline -5",
        "3. Confirm read-only source inputs are present:",
    ]
    for src in payload.get("source_files_read", []):
        parts.append(f"   - {src['name']} ({src['state']})")
    parts += ["", "ALLOWED PATHS (stay inside these unless a follow-up authorization extends scope):"]
    for p in payload["allowed_paths"]:
        parts.append(f"  - {p}")
    parts += ["", "FORBIDDEN PATHS (do not read, do not modify):"]
    for p in payload["forbidden_paths"]:
        parts.append(f"  - {p}")
    parts += [
        "",
        "CRITICAL SAFETY RULES (none may be weakened):",
        "* Research-only.",
        "* No broker control. No live trading. No paper order execution. No order placement.",
        "* No scheduler / background daemon / cron install.",
        "* No external network calls. No API keys, no .env, no credentials.",
        "* No modification of paper or live execution files.",
        "* Standard-library imports only unless this bundle's spec explicitly authorizes a dependency.",
        "* Pin these flags False everywhere: live_trading_enabled, broker_control_enabled, paper_order_execution_enabled.",
        "",
        "BUILD REQUIREMENTS:",
    ]
    for e in (payload.get("expected_outputs") or []):
        parts.append(f"* {e}")
    if payload.get("required_inputs"):
        parts += ["", "REQUIRED INPUTS:"]
        for r in payload["required_inputs"]:
            parts.append(f"* {r}")
    parts += ["", "TESTS REQUIRED:"]
    for t in payload["tests_to_run"]:
        parts.append(f"* {t}")
    parts += ["", "ACCEPTANCE CRITERIA:"]
    for a in payload["acceptance_criteria"]:
        parts.append(f"* {a}")
    parts += [
        "",
        "FINAL REPORT REQUIRED:",
        "* Exact files created / edited",
        "* git diff --stat",
        "* Tests run and pass counts (no failures, no errors)",
        "* Safety confirmation (no broker / live / paper-order code, no network call, no key)",
        "* Whether brain_memory/lessons.md was touched (default: no; call it out explicitly if yes)",
        "* Final git status --short",
        "* Exact proposed commit file list (do not commit unless explicitly approved)",
        "",
        "COMMIT BOUNDARY:",
        "* Do not stage. Do not commit. Do not push unless explicitly approved.",
        "* When approval comes, use explicit pathspecs only (`git commit -- <paths>`); never `git add .`.",
        "",
        f"-- end prompt (generated_at={payload['generated_at']}; layer={payload['layer']}) --",
    ]
    return "\n".join(parts) + "\n"


def generate(repo_root: Path = REPO_ROOT) -> dict:
    payload = build_bundle_payload(repo_root)
    out_dir = repo_root / OUTPUT_DIR_REL
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / OUTPUT_JSON).write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    (out_dir / OUTPUT_MD).write_text(render_markdown(payload), encoding="utf-8")
    (out_dir / OUTPUT_PROMPT).write_text(render_prompt(payload), encoding="utf-8")
    return payload


def validate(repo_root: Path = REPO_ROOT) -> tuple[bool, list]:
    """Validate next_bundle.json schema + safety presence."""
    errors: list = []
    jpath = repo_root / OUTPUT_DIR_REL / OUTPUT_JSON
    ppath = repo_root / OUTPUT_DIR_REL / OUTPUT_PROMPT
    if not jpath.exists():
        return False, [f"missing: {jpath.as_posix()}"]
    try:
        data = json.loads(jpath.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return False, [f"invalid JSON ({type(exc).__name__}): {jpath.as_posix()}"]
    if not isinstance(data, dict):
        return False, ["next_bundle.json is not a JSON object"]
    for k in REQUIRED_JSON_KEYS:
        if k not in data:
            errors.append(f"missing key: {k}")
    sf = data.get("safety_flags") or {}
    for flag in ("live_trading_enabled", "broker_control_enabled", "paper_order_execution_enabled"):
        if sf.get(flag) is not False:
            errors.append(f"safety_flag {flag} not pinned False")
    fa = set(data.get("forbidden_actions") or [])
    must_have = {"no_broker_control", "no_live_trading", "no_paper_order_execution"}
    if not must_have.issubset(fa):
        errors.append(f"forbidden_actions missing one of {sorted(must_have - fa)}")
    if not ppath.exists():
        errors.append(f"missing: {ppath.as_posix()}")
    else:
        prompt_text = ppath.read_text(encoding="utf-8")
        for must in ("No broker control", "No live trading", "No paper order execution"):
            if must not in prompt_text:
                errors.append(f"prompt missing safety phrase: {must!r}")
        if "Do not stage" not in prompt_text:
            errors.append("prompt missing commit boundary 'Do not stage'")
        if "TESTS REQUIRED" not in prompt_text:
            errors.append("prompt missing 'TESTS REQUIRED' section")
    return (not errors), errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Strategy Factory Next Bundle Generator v1 (research-only)",
    )
    parser.add_argument("command", choices=("generate", "show", "validate"))
    parser.add_argument("--repo-root", default=str(REPO_ROOT),
                       help="Override repo root (for tests).")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()

    if args.command == "generate":
        payload = generate(root)
        print(f"generated_at: {payload['generated_at']}")
        print(f"selected:     {payload['title']} (lane={payload.get('lane')}, priority={payload.get('priority')})")
        print(f"prompt:       {(root / OUTPUT_DIR_REL / OUTPUT_PROMPT).as_posix()}")
        return 0
    if args.command == "show":
        jpath = root / OUTPUT_DIR_REL / OUTPUT_JSON
        if not jpath.exists():
            print(f"no next_bundle.json yet; run `generate` first ({jpath.as_posix()})")
            return 1
        data = json.loads(jpath.read_text(encoding="utf-8"))
        print(f"selected: {data.get('title')} (lane={data.get('lane')}, priority={data.get('priority')})")
        print(f"reason:   {data.get('reason')}")
        print(f"prompt:   {(root / OUTPUT_DIR_REL / OUTPUT_PROMPT).as_posix()}")
        return 0
    if args.command == "validate":
        ok, errs = validate(root)
        if ok:
            print("validate: OK")
            return 0
        print("validate: FAIL")
        for e in errs:
            print(f"  - {e}")
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""SPARTA Strategy Factory — Routine Layer v1 (additive, research-only).

A tiny, deterministic, standard-library-only command/report framework that
reads EXISTING SPARTA research outputs (the agentic validation-factory
report.json files) and produces clean, JARVIS-readable status files. Its
only purpose is to cut copy-paste work: summarize current research state,
suggest which research lane is next, and self-grade the pipeline.

Hard non-negotiable guarantees (enforced by tests):
  * Read-only with respect to all research inputs.
  * No broker control, no exchange/Alpaca API, no order placement.
  * No live trading, no paper-order execution, no autonomous trade decision.
  * No network calls, no credentials, no .env, no scheduler/daemon install.
  * Writes ONLY inside reports/strategy_factory_routines/ and
    storage/jarvis/strategy_factory/.

The three safety flags below are pinned False everywhere and asserted by the
test-suite:
  live_trading_enabled / broker_control_enabled / paper_order_execution_enabled

This module imports nothing beyond the Python standard library.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
LAYER_NAME = "strategy_factory_routine_layer_v1"

# Pinned-False safety invariants. These are constants, never computed True.
SAFETY_FLAGS = {
    "live_trading_enabled": False,
    "broker_control_enabled": False,
    "paper_order_execution_enabled": False,
}

SAFETY_NOTES = [
    "Research-only routine layer. Reads existing reports; never executes.",
    "No broker, no exchange/Alpaca API, no order placement, no paper/live.",
    "No network calls, no credentials, no scheduler/daemon.",
    "Outputs are summaries for human + JARVIS review only.",
]

# Input source: the agentic validation factory's per-step report tree.
_FACTORY_REPORTS_RELDIR = Path("trading_research") / "agentic_factory" / "reports"
# Optional cross-reference: JARVIS read-only snapshot.
_JARVIS_SNAPSHOT_RELPATH = (
    Path("storage") / "jarvis" / "snapshots" / "latest_snapshot.json"
)

# Output roots (relative to repo root).
_DAILY_STATE_RELDIR = (
    Path("reports") / "strategy_factory_routines" / "daily_state"
)
_QUEUE_RELDIR = (
    Path("reports") / "strategy_factory_routines" / "strategy_queue"
)
_WEEKLY_RELDIR = (
    Path("reports") / "strategy_factory_routines" / "weekly_review"
)
_JARVIS_OUT_RELDIR = (
    Path("storage") / "jarvis" / "strategy_factory"
)

_WEEK_DAYS = 7

# Keys, in priority order, used to extract a one-line verdict from any
# report.json regardless of its bespoke shape.
_VERDICT_KEYS = (
    "verdict",
    "final_recommendation",
    "trading_recommendation",
    "recommended_research_direction_after_hygiene",
)

_FAIL_RE = re.compile(r"\b(IS_FAIL|OOS_FAIL|FAIL|PARKED|PARK|KILL)\b")
_PASS_RE = re.compile(r"\b(PASS|PASSED|PROMOTED|VALIDATED|CONTINUE|GREEN)\b")
_WATCH_RE = re.compile(r"\b(WATCH|IS_WATCH|UNCERTAIN|YELLOW|HYGIENE)\b")


# ---------------------------------------------------------------------------
# Repo-root + IO helpers (all paths derive from a single repo root so the
# whole layer is trivially testable against a temp tree).
# ---------------------------------------------------------------------------

def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def _safe_load_json(path: Path) -> dict[str, Any] | None:
    try:
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _write_pair(out_dir: Path, stem: str, payload: dict[str, Any],
                markdown: str) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / f"{stem}.json"
    md_path = out_dir / f"{stem}.md"
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str),
        encoding="utf-8",
    )
    md_path.write_text(markdown, encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


# ---------------------------------------------------------------------------
# Input scanning
# ---------------------------------------------------------------------------

def _lane_of(name: str) -> str:
    n = name.lower()
    if n.startswith("crypto") or "crypto" in n:
        return "crypto"
    if n.startswith("repo_hygiene") or "hygiene" in n:
        return "infra_hygiene"
    if n.startswith("factory") or "factory" in n:
        return "factory_core"
    if re.match(r"^s\d+_", n) or n.startswith("turtle") or n.startswith("nq"):
        return "futures"
    return "other"


def _extract_verdict(data: dict[str, Any]) -> str | None:
    for key in _VERDICT_KEYS:
        val = data.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
        if isinstance(val, dict):
            choice = val.get("choice")
            if isinstance(choice, str) and choice.strip():
                return choice.strip()
    return None


def _classify_outcome(verdict: str | None, blob: str) -> str:
    """Bucket a report as pass / fail / watch / unknown from its text."""
    haystack = f"{verdict or ''} {blob}".upper()
    if _FAIL_RE.search(haystack):
        return "fail"
    if _PASS_RE.search(haystack):
        return "pass"
    if _WATCH_RE.search(haystack):
        return "watch"
    return "unknown"


def scan_factory_reports(repo_root: Path) -> list[dict[str, Any]]:
    """Return one record per agentic-factory report.json, newest first.

    Returns an empty list (never raises) if the source tree is absent so the
    routines degrade gracefully.
    """
    src = repo_root / _FACTORY_REPORTS_RELDIR
    records: list[dict[str, Any]] = []
    if not src.is_dir():
        return records
    for report_path in sorted(src.glob("*/report.json")):
        data = _safe_load_json(report_path)
        if data is None:
            continue
        try:
            mtime = report_path.stat().st_mtime
        except OSError:
            mtime = 0.0
        verdict = _extract_verdict(data)
        # A bounded text blob for keyword classification only.
        blob = json.dumps(data, default=str)[:20000]
        records.append({
            "name": report_path.parent.name,
            "rel_path": str(report_path.relative_to(repo_root)).replace(
                "\\", "/"),
            "title": data.get("title") or data.get("step") or
            report_path.parent.name,
            "step": data.get("step"),
            "created": data.get("created"),
            "lane": _lane_of(report_path.parent.name),
            "verdict": verdict,
            "outcome": _classify_outcome(verdict, blob),
            "modified_at": _iso(
                datetime.fromtimestamp(mtime, tz=timezone.utc)),
            "_mtime": mtime,
            "_data": data,
        })
    records.sort(key=lambda r: r["_mtime"], reverse=True)
    return records


def _public_record(rec: dict[str, Any]) -> dict[str, Any]:
    """A record with the heavy raw payload stripped (for serialization)."""
    return {k: v for k, v in rec.items() if not k.startswith("_")}


def _missing_inputs(repo_root: Path) -> list[str]:
    missing: list[str] = []
    if not (repo_root / _FACTORY_REPORTS_RELDIR).is_dir():
        missing.append(
            f"factory reports dir not found: {_FACTORY_REPORTS_RELDIR}")
    if not (repo_root / _JARVIS_SNAPSHOT_RELPATH).is_file():
        missing.append(
            f"jarvis snapshot not found: {_JARVIS_SNAPSHOT_RELPATH}")
    return missing


# ---------------------------------------------------------------------------
# Shared derivations
# ---------------------------------------------------------------------------

def _latest_memo(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    """The newest report that looks like a roadmap/closeout memo, else the
    newest report overall."""
    for rec in records:
        data = rec["_data"]
        if data.get("memo_only") or "roadmap" in rec["name"].lower() or any(
            k.startswith("6_next_roadmap") or k.startswith("7_final")
            for k in data.keys()
        ):
            return rec
    return records[0] if records else None


def _next_best_action(records: list[dict[str, Any]]) -> str:
    memo = _latest_memo(records)
    if memo is None:
        return "Awaiting factory reports — no input to derive next action."
    data = memo["_data"]
    final = data.get("7_final_recommendation")
    if isinstance(final, dict):
        choice = final.get("choice")
        after = final.get("research_direction_after_hygiene")
        if choice and after:
            return f"{choice} -> then {after}"
        if choice:
            return str(choice)
    rec = data.get("final_recommendation")
    after = data.get("recommended_research_direction_after_hygiene")
    if rec and after:
        return f"{rec} -> then {after}"
    if rec:
        return str(rec)
    return f"Continue from latest report: {memo['title']}"


def _active_lanes(records: list[dict[str, Any]], top_n: int = 8) -> list[str]:
    seen: list[str] = []
    for rec in records[:top_n]:
        if rec["lane"] not in seen:
            seen.append(rec["lane"])
    return seen


def _derive_blockers(repo_root: Path,
                     records: list[dict[str, Any]]) -> list[str]:
    blockers: list[str] = []
    if not records:
        blockers.append(
            "No factory reports found — cannot assess research state.")
        return blockers
    memo = _latest_memo(records)
    if memo is not None:
        data = memo["_data"]
        rec = (data.get("final_recommendation") or "")
        if isinstance(rec, str) and "HYGIENE" in rec.upper():
            blockers.append(
                "Latest memo recommends REPO_HYGIENE_FIRST before opening a "
                "new research lane.")
    # Cross-reference JARVIS snapshot for a dirty working tree signal.
    snap = _safe_load_json(repo_root / _JARVIS_SNAPSHOT_RELPATH)
    if isinstance(snap, dict):
        git = snap.get("git") or {}
        if git.get("dirty") is True:
            blockers.append(
                "Git working tree reported dirty by JARVIS snapshot — "
                "stabilize before unattended automation.")
    if not _validated_strategy_exists(records):
        blockers.append(
            "No validated/paper-ready/live-ready strategy exists yet "
            "(all tested branches PARKED).")
    return blockers


def _validated_strategy_exists(records: list[dict[str, Any]]) -> bool:
    """True only if some report explicitly asserts a validated/promoted
    strategy. Conservative: defaults to False."""
    for rec in records:
        data = rec["_data"]
        totals = (data.get("candidate_registry") or {}).get("totals")
        if isinstance(totals, dict):
            promoted = totals.get("promoted")
            if isinstance(promoted, int) and promoted > 0:
                return True
        val = data.get("validated_crypto_strategy")
        if isinstance(val, str) and val.strip().upper() not in (
                "NONE", "", "NO"):
            return True
    return False


def _posture(blockers: list[str], records: list[dict[str, Any]]) -> str:
    """GREEN / YELLOW / RED research posture.

    RED is reserved for a safety-invariant breach (should never happen while
    the pinned flags hold). YELLOW = caution / open blockers / missing inputs.
    GREEN = inputs present and no open blockers.
    """
    if any(v is not False for v in SAFETY_FLAGS.values()):
        return "RED"
    if not records:
        return "YELLOW"
    if blockers:
        return "YELLOW"
    return "GREEN"


# ---------------------------------------------------------------------------
# Routine 1 — Daily State
# ---------------------------------------------------------------------------

def build_daily_state(repo_root: Path) -> dict[str, Any]:
    records = scan_factory_reports(repo_root)
    missing = _missing_inputs(repo_root)
    blockers = _derive_blockers(repo_root, records)
    active = _active_lanes(records)
    recent = [_public_record(r) for r in records[:10]]
    next_action = _next_best_action(records)
    posture = _posture(blockers, records)
    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER_NAME,
        "routine": "daily_state",
        "read_only": True,
        "generated_at": _iso(_utc_now()),
        "research_posture": posture,
        "active_lanes": active,
        "recently_completed_reports": recent,
        "report_count": len(records),
        "blockers": blockers,
        "what_should_run_next": next_action,
        "missing_inputs": missing,
        "safety_status": {
            **SAFETY_FLAGS,
            "read_only": True,
            "any_live_or_broker_control_exists": False,
        },
        "safety_notes": SAFETY_NOTES,
    }


def render_daily_state_md(state: dict[str, Any]) -> str:
    lines = ["# SPARTA Strategy Factory — Daily State", ""]
    lines.append(f"- Generated (UTC): `{state['generated_at']}`")
    lines.append(f"- Research posture: **{state['research_posture']}**")
    lines.append(f"- Reports scanned: `{state['report_count']}`")
    lines.append(
        "- Active lanes: " + (
            ", ".join(f"`{l}`" for l in state["active_lanes"]) or "_none_"))
    lines.append("")
    lines.append("## What should run next")
    lines.append("")
    lines.append(f"> {state['what_should_run_next']}")
    lines.append("")
    lines.append("## Blockers")
    lines.append("")
    if state["blockers"]:
        for b in state["blockers"]:
            lines.append(f"- {b}")
    else:
        lines.append("- _none detected_")
    lines.append("")
    lines.append("## Recently completed reports")
    lines.append("")
    if state["recently_completed_reports"]:
        lines.append("| step | lane | outcome | verdict |")
        lines.append("| --- | --- | --- | --- |")
        for r in state["recently_completed_reports"]:
            verdict = (r.get("verdict") or "—")
            if len(verdict) > 60:
                verdict = verdict[:57] + "…"
            lines.append(
                f"| {r.get('step') or r['name']} | {r['lane']} | "
                f"{r['outcome']} | {verdict} |")
    else:
        lines.append("- _no reports found_")
    lines.append("")
    if state["missing_inputs"]:
        lines.append("## Missing inputs (degraded gracefully)")
        lines.append("")
        for m in state["missing_inputs"]:
            lines.append(f"- {m}")
        lines.append("")
    lines.append("## Safety status")
    lines.append("")
    for k, v in state["safety_status"].items():
        lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("---")
    lines.append(
        "_ROUTINE LAYER ONLY. Research-only summary. Not a trade signal, "
        "not a forecast, not an instruction to execute anything._")
    lines.append("")
    return "\n".join(lines)


def run_daily_state(repo_root: Path) -> dict[str, Any]:
    state = build_daily_state(repo_root)
    paths = _write_pair(
        repo_root / _DAILY_STATE_RELDIR, "latest_state", state,
        render_daily_state_md(state))
    return {"payload": state, "paths": paths}


# ---------------------------------------------------------------------------
# Routine 2 — Strategy Queue
# ---------------------------------------------------------------------------

# Static catalog of research-only lanes. Priorities/blocked flags are tuned at
# build time from the latest roadmap memo so the queue reflects real repo
# state without ever inventing a trade action.
_QUEUE_CATALOG = [
    {
        "lane": "data_qa_freeze",
        "title": "Data QA / freeze tasks",
        "reason": "Frozen, provenance-pinned, QA-clean data is a precondition "
                  "for every downstream validation step.",
        "required_inputs": ["existing offline snapshots", "provenance sidecars"],
        "expected_output": "QA report confirming snapshots unchanged + sealed.",
        "safety_level": "research_only",
        "next_bundle_suggestion": "Claude/Codex: data-freeze verification bundle",
    },
    {
        "lane": "jarvis_checkpoint",
        "title": "JARVIS checkpoint tasks",
        "reason": "Keep the read-only JARVIS/Commander snapshot accurate and "
                  "stop background automation from racing HEAD.",
        "required_inputs": ["storage/jarvis snapshots", "git status"],
        "expected_output": "Refreshed read-only JARVIS snapshot.",
        "safety_level": "research_only",
        "next_bundle_suggestion": "Claude/Codex: JARVIS snapshot refresh bundle",
    },
    {
        "lane": "crypto_4h_protocol",
        "title": "Crypto 4H protocol",
        "reason": "Daily-spot crash/reversion family exhausted at v1; more bars "
                  "per day may afford a real confirmation filter (D8 fallback).",
        "required_inputs": [
            "new immutable SHA256-pinned BTC/ETH/SOL 4H spot snapshot (offline)"],
        "expected_output": "Frozen 4H data + protocol spec (no fetch, no run).",
        "safety_level": "research_only",
        "next_bundle_suggestion": "Claude/Codex: crypto 4H data-freeze + spec bundle",
    },
    {
        "lane": "crypto_d1_protocol",
        "title": "Crypto D1 protocol",
        "reason": "Daily-spot idea space largely picked over; revisit only with "
                  "a genuinely new structural hypothesis.",
        "required_inputs": ["existing frozen daily snapshot"],
        "expected_output": "New frozen daily spec OR explicit retirement memo.",
        "safety_level": "research_only",
        "next_bundle_suggestion": "Claude/Codex: new daily hypothesis spec bundle",
    },
    {
        "lane": "nq_es_futures_trend",
        "title": "NQ/ES futures trend research",
        "reason": "Mature lane with a complete validation ladder; no fresh "
                  "futures hypothesis currently queued.",
        "required_inputs": ["data_offline NQ/ES daily"],
        "expected_output": "New futures hypothesis spec (frozen).",
        "safety_level": "research_only",
        "next_bundle_suggestion": "Claude/Codex: futures hypothesis spec bundle",
    },
    {
        "lane": "donchian_variants",
        "title": "Donchian variants",
        "reason": "Reference baseline only; entry edge not supported and "
                  "sequence-fragile in prior runs.",
        "required_inputs": ["Donchian engine + offline data"],
        "expected_output": "Variant spec + IS-only diagnostic (research).",
        "safety_level": "research_only",
        "next_bundle_suggestion": "Claude/Codex: Donchian variant diagnostic bundle",
    },
    {
        "lane": "vol_confirmed_trend_continuation",
        "title": "Volatility-confirmed trend continuation",
        "reason": "Structural idea worth a frozen-spec attempt under the same "
                  "11-rung ladder.",
        "required_inputs": ["offline data", "volatility features"],
        "expected_output": "Frozen spec + IS baseline protocol.",
        "safety_level": "research_only",
        "next_bundle_suggestion": "Claude/Codex: vol-confirmed continuation spec bundle",
    },
    {
        "lane": "arbitrage_research_protocol",
        "title": "Arbitrage research protocol",
        "reason": "Exploratory; requires its own data contract before any "
                  "evidence claim.",
        "required_inputs": ["paired-series data contract (offline)"],
        "expected_output": "Data-requirements + pre-registration memo.",
        "safety_level": "research_only",
        "next_bundle_suggestion": "Claude/Codex: arbitrage data-contract bundle",
    },
]


def build_strategy_queue(repo_root: Path) -> dict[str, Any]:
    records = scan_factory_reports(repo_root)
    missing = _missing_inputs(repo_root)
    memo = _latest_memo(records)
    hygiene_first = False
    recommended_direction = None
    if memo is not None:
        data = memo["_data"]
        rec = data.get("final_recommendation")
        if isinstance(rec, str) and "HYGIENE" in rec.upper():
            hygiene_first = True
        recommended_direction = (
            data.get("recommended_research_direction_after_hygiene"))
        final = data.get("7_final_recommendation")
        if isinstance(final, dict):
            recommended_direction = (
                final.get("research_direction_after_hygiene")
                or recommended_direction)

    # Map the memo's recommended direction to a catalog lane.
    direction_lane = None
    if isinstance(recommended_direction, str):
        rd = recommended_direction.upper()
        if "4H" in rd:
            direction_lane = "crypto_4h_protocol"
        elif "D1" in rd or "DAILY" in rd:
            direction_lane = "crypto_d1_protocol"
        elif "FUTURES" in rd:
            direction_lane = "nq_es_futures_trend"

    items: list[dict[str, Any]] = []
    for entry in _QUEUE_CATALOG:
        lane = entry["lane"]
        is_hygiene = lane in ("data_qa_freeze", "jarvis_checkpoint")
        if is_hygiene and hygiene_first:
            priority = 1
            blocked = False
        elif lane == direction_lane:
            priority = 2
            # Recommended research direction is gated behind hygiene-first.
            blocked = hygiene_first
        else:
            priority = 3
            blocked = False
        reason = entry["reason"]
        if lane == direction_lane:
            reason = (
                f"Latest roadmap memo recommends this lane next "
                f"({recommended_direction}). " + reason)
        if blocked:
            reason += (
                " Blocked: hygiene-first must complete before this lane opens.")
        items.append({
            "lane": lane,
            "title": entry["title"],
            "priority": priority,
            "reason": reason,
            "required_inputs": entry["required_inputs"],
            "expected_output": entry["expected_output"],
            "safety_level": entry["safety_level"],
            "blocked": blocked,
            "next_bundle_suggestion": entry["next_bundle_suggestion"],
        })
    items.sort(key=lambda it: (it["priority"], it["lane"]))

    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER_NAME,
        "routine": "strategy_queue",
        "read_only": True,
        "generated_at": _iso(_utc_now()),
        "hygiene_first": hygiene_first,
        "recommended_research_direction": recommended_direction,
        "queue": items,
        "queue_length": len(items),
        "missing_inputs": missing,
        "safety_status": {**SAFETY_FLAGS, "read_only": True},
        "safety_notes": SAFETY_NOTES,
    }


def render_strategy_queue_md(q: dict[str, Any]) -> str:
    lines = ["# SPARTA Strategy Factory — Strategy Queue", ""]
    lines.append(f"- Generated (UTC): `{q['generated_at']}`")
    lines.append(f"- Hygiene-first gate: **{q['hygiene_first']}**")
    lines.append(
        "- Recommended research direction: "
        f"`{q.get('recommended_research_direction') or 'n/a'}`")
    lines.append(f"- Queue length: `{q['queue_length']}`")
    lines.append("")
    lines.append("| pri | lane | blocked | safety | next bundle |")
    lines.append("| --- | --- | --- | --- | --- |")
    for it in q["queue"]:
        lines.append(
            f"| {it['priority']} | {it['lane']} | {it['blocked']} | "
            f"{it['safety_level']} | {it['next_bundle_suggestion']} |")
    lines.append("")
    lines.append("## Detail")
    lines.append("")
    for it in q["queue"]:
        lines.append(f"### {it['title']} (`{it['lane']}`)")
        lines.append(f"- Priority: {it['priority']} | Blocked: {it['blocked']} "
                     f"| Safety: {it['safety_level']}")
        lines.append(f"- Reason: {it['reason']}")
        lines.append(
            "- Required inputs: " + ", ".join(it["required_inputs"]))
        lines.append(f"- Expected output: {it['expected_output']}")
        lines.append(f"- Next bundle: {it['next_bundle_suggestion']}")
        lines.append("")
    lines.append("---")
    lines.append(
        "_ROUTINE LAYER ONLY. Every queued item is research-only; none places "
        "an order, touches a broker, or authorizes execution._")
    lines.append("")
    return "\n".join(lines)


def run_strategy_queue(repo_root: Path) -> dict[str, Any]:
    q = build_strategy_queue(repo_root)
    paths = _write_pair(
        repo_root / _QUEUE_RELDIR, "queue", q, render_strategy_queue_md(q))
    return {"payload": q, "paths": paths}


# ---------------------------------------------------------------------------
# Routine 3 — Weekly Review
# ---------------------------------------------------------------------------

def _gap_readiness(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    for rec in records:
        gap = rec["_data"].get("gap_analysis")
        if isinstance(gap, dict):
            exists = gap.get("exists")
            missing = gap.get("missing_for_overnight_automation")
            if isinstance(exists, list) and isinstance(missing, list):
                total = len(exists) + len(missing)
                score = round(100 * len(exists) / total) if total else 0
                return {
                    "exists_count": len(exists),
                    "missing_count": len(missing),
                    "score": score,
                    "source": rec["name"],
                }
    return None


def build_weekly_review(repo_root: Path) -> dict[str, Any]:
    records = scan_factory_reports(repo_root)
    missing = _missing_inputs(repo_root)
    now = _utc_now()
    cutoff = now - timedelta(days=_WEEK_DAYS)
    in_window = [
        r for r in records
        if datetime.fromtimestamp(r["_mtime"], tz=timezone.utc) >= cutoff
    ]

    tested_or_built = [r["title"] for r in in_window]
    passed = [r["name"] for r in in_window if r["outcome"] == "pass"]
    failed = [r["name"] for r in in_window if r["outcome"] == "fail"]
    uncertain = [
        r["name"] for r in in_window if r["outcome"] in ("watch", "unknown")]

    validated = _validated_strategy_exists(records)

    # Lanes that produced only fails/parks this week are flagged low-value.
    lane_outcomes: dict[str, set[str]] = {}
    for r in in_window:
        lane_outcomes.setdefault(r["lane"], set()).add(r["outcome"])
    wasting_time = sorted(
        lane for lane, outs in lane_outcomes.items()
        if outs and outs <= {"fail"})

    queue = build_strategy_queue(repo_root)
    next_lane = None
    for it in queue["queue"]:
        if not it["blocked"]:
            next_lane = it["lane"]
            break
    if next_lane is None and queue["queue"]:
        next_lane = queue["queue"][0]["lane"]

    # --- deterministic scores (0-100) -------------------------------------
    safety_score = 100 if all(v is False for v in SAFETY_FLAGS.values()) else 0

    gap = _gap_readiness(records)
    automation_readiness_score = gap["score"] if gap else 0

    # Research quality = share of in-window reports that reached an explicit
    # verdict (discipline signal). No reports in window -> 0 with a note.
    with_verdict = sum(1 for r in in_window if r["verdict"])
    research_quality_score = (
        round(100 * with_verdict / len(in_window)) if in_window else 0)

    closer_to_edge = bool(validated)

    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER_NAME,
        "routine": "weekly_review",
        "read_only": True,
        "generated_at": _iso(now),
        "window_start": _iso(cutoff),
        "window_end": _iso(now),
        "reports_in_window": len(in_window),
        "what_was_tested_or_built": tested_or_built,
        "what_passed": passed,
        "what_failed": failed,
        "what_remains_uncertain": uncertain,
        "closer_to_real_edge": closer_to_edge,
        "validated_strategy_exists": validated,
        "lanes_wasting_time": wasting_time,
        "lane_deserving_next_deep_bundle": next_lane,
        "next_action_recommendation": _next_best_action(records),
        "scores": {
            "safety_score": safety_score,
            "automation_readiness_score": automation_readiness_score,
            "research_quality_score": research_quality_score,
        },
        "automation_readiness_detail": gap,
        "missing_inputs": missing,
        "safety_status": {**SAFETY_FLAGS, "read_only": True},
        "safety_notes": SAFETY_NOTES,
    }


def render_weekly_review_md(w: dict[str, Any]) -> str:
    lines = ["# SPARTA Strategy Factory — Weekly Review", ""]
    lines.append(f"- Generated (UTC): `{w['generated_at']}`")
    lines.append(
        f"- Window: `{w['window_start']}` -> `{w['window_end']}`")
    lines.append(f"- Reports in window: `{w['reports_in_window']}`")
    lines.append("")
    lines.append("## Scores")
    lines.append("")
    for k, v in w["scores"].items():
        lines.append(f"- `{k}`: **{v}/100**")
    lines.append("")
    lines.append("## Progress")
    lines.append("")
    lines.append(f"- Closer to a real edge: **{w['closer_to_real_edge']}**")
    lines.append(
        f"- Validated strategy exists: **{w['validated_strategy_exists']}**")
    lines.append(
        "- Lane deserving next deep bundle: "
        f"`{w['lane_deserving_next_deep_bundle']}`")
    lines.append(
        "- Lanes wasting time: " + (
            ", ".join(f"`{l}`" for l in w["lanes_wasting_time"]) or "_none_"))
    lines.append("")
    lines.append("## Next action")
    lines.append("")
    lines.append(f"> {w['next_action_recommendation']}")
    lines.append("")

    def _bullets(title: str, items: list[str]) -> None:
        lines.append(f"## {title}")
        lines.append("")
        if items:
            for it in items:
                lines.append(f"- {it}")
        else:
            lines.append("- _none_")
        lines.append("")

    _bullets("What was tested or built", w["what_was_tested_or_built"])
    _bullets("What passed", w["what_passed"])
    _bullets("What failed", w["what_failed"])
    _bullets("What remains uncertain", w["what_remains_uncertain"])
    if w["missing_inputs"]:
        _bullets("Missing inputs (degraded gracefully)", w["missing_inputs"])
    lines.append("---")
    lines.append(
        "_ROUTINE LAYER ONLY. Self-graded research summary. Not a trade "
        "signal, not a forecast, not an instruction to execute anything._")
    lines.append("")
    return "\n".join(lines)


def run_weekly_review(repo_root: Path) -> dict[str, Any]:
    w = build_weekly_review(repo_root)
    paths = _write_pair(
        repo_root / _WEEKLY_RELDIR, "latest_weekly_review", w,
        render_weekly_review_md(w))
    return {"payload": w, "paths": paths}


# ---------------------------------------------------------------------------
# Routine 4 — JARVIS Snapshot
# ---------------------------------------------------------------------------

def _commander_color(posture: str) -> str:
    return posture if posture in ("GREEN", "YELLOW", "RED") else "YELLOW"


def build_jarvis_snapshot(repo_root: Path) -> dict[str, Any]:
    records = scan_factory_reports(repo_root)
    blockers = _derive_blockers(repo_root, records)
    posture = _posture(blockers, records)
    active = _active_lanes(records)
    last_reports = [
        {
            "name": r["name"],
            "rel_path": r["rel_path"],
            "outcome": r["outcome"],
            "modified_at": r["modified_at"],
        }
        for r in records[:5]
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER_NAME,
        "kind": "strategy_factory_snapshot",
        "read_only": True,
        "generated_at": _iso(_utc_now()),
        "posture": posture,
        "active_lane": active[0] if active else "none",
        "next_best_action": _next_best_action(records),
        "blockers": blockers,
        "last_reports": last_reports,
        "live_trading_enabled": False,
        "broker_control_enabled": False,
        "paper_order_execution_enabled": False,
        "safety_notes": SAFETY_NOTES,
        "commander_color": _commander_color(posture),
    }


def render_jarvis_snapshot_md(s: dict[str, Any]) -> str:
    lines = ["# SPARTA Strategy Factory — JARVIS Snapshot", ""]
    lines.append(f"- Generated (UTC): `{s['generated_at']}`")
    lines.append(f"- Commander color: **{s['commander_color']}**")
    lines.append(f"- Posture: **{s['posture']}**")
    lines.append(f"- Active lane: `{s['active_lane']}`")
    lines.append("")
    lines.append("## Next best action")
    lines.append("")
    lines.append(f"> {s['next_best_action']}")
    lines.append("")
    lines.append("## Blockers")
    lines.append("")
    if s["blockers"]:
        for b in s["blockers"]:
            lines.append(f"- {b}")
    else:
        lines.append("- _none_")
    lines.append("")
    lines.append("## Last reports")
    lines.append("")
    if s["last_reports"]:
        for r in s["last_reports"]:
            lines.append(
                f"- `{r['name']}` ({r['outcome']}) — {r['modified_at']}")
    else:
        lines.append("- _none_")
    lines.append("")
    lines.append("## Safety")
    lines.append("")
    lines.append(f"- live_trading_enabled: {s['live_trading_enabled']}")
    lines.append(f"- broker_control_enabled: {s['broker_control_enabled']}")
    lines.append(
        f"- paper_order_execution_enabled: "
        f"{s['paper_order_execution_enabled']}")
    lines.append("")
    lines.append("---")
    lines.append(
        "_ROUTINE LAYER ONLY. Read-only snapshot for JARVIS/Commander. "
        "Never trades, never executes._")
    lines.append("")
    return "\n".join(lines)


def run_jarvis_snapshot(repo_root: Path) -> dict[str, Any]:
    s = build_jarvis_snapshot(repo_root)
    paths = _write_pair(
        repo_root / _JARVIS_OUT_RELDIR, "latest_strategy_factory_snapshot",
        s, render_jarvis_snapshot_md(s))
    return {"payload": s, "paths": paths}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

_COMMANDS = {
    "daily-state": run_daily_state,
    "strategy-queue": run_strategy_queue,
    "weekly-review": run_weekly_review,
    "jarvis-snapshot": run_jarvis_snapshot,
}


def run_all(repo_root: Path) -> dict[str, Any]:
    return {name: fn(repo_root) for name, fn in _COMMANDS.items()}


def _cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="strategy_factory_routines",
        description=(
            "SPARTA Strategy Factory Routine Layer v1 — research-only, "
            "read-only, stdlib-only. Reads existing factory reports and "
            "writes JARVIS-readable status files. No network, no broker, "
            "no trading, no scheduler."),
    )
    parser.add_argument(
        "command",
        choices=list(_COMMANDS.keys()) + ["all"],
        help="which routine to run",
    )
    parser.add_argument(
        "--repo-root", default=None,
        help="repo root (defaults to the SPARTA_BRAIN checkout containing "
             "this tool); override for testing against a temp tree.",
    )
    args = parser.parse_args(argv)
    repo_root = (
        Path(args.repo_root).resolve() if args.repo_root
        else default_repo_root())

    if args.command == "all":
        results = run_all(repo_root)
        for name, res in results.items():
            print(f"[{name}]")
            print(f"  json: {res['paths']['json']}")
            print(f"  md:   {res['paths']['markdown']}")
    else:
        res = _COMMANDS[args.command](repo_root)
        payload = res["payload"]
        print(f"[{args.command}]")
        print(f"  json: {res['paths']['json']}")
        print(f"  md:   {res['paths']['markdown']}")
        if "research_posture" in payload:
            print(f"  posture: {payload['research_posture']}")
        if "commander_color" in payload:
            print(f"  commander_color: {payload['commander_color']}")
    return 0


if __name__ == "__main__":
    sys.exit(_cli())

"""SPARTA Strategy Candidate Registry v1 (research-only, stdlib).

A deterministic, **research-only** registry of every strategy/lane SPARTA has
tested, parked, failed, or wants to test next. It exists to be the central memory
of candidate status so future research/JARVIS work does not repeat retired or
failed lanes.

Hard non-negotiable guarantees (enforced by tests):
  * Read-only with respect to all inputs.
  * No broker control, no exchange/Alpaca API, no order placement.
  * No live trading, no paper-order execution, no autonomous trade decision.
  * No network calls, no credentials, no .env, no scheduler/daemon, no subprocess.
  * Standard library only -- no imports beyond stdlib.
  * Writes ONLY inside reports/strategy_factory_routines/candidate_registry/.

The three trading-safety flags below are pinned False everywhere and asserted by
the test suite:
  live_trading_enabled / broker_control_enabled / paper_order_execution_enabled
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
LAYER = "strategy_candidate_registry_v1"

SAFETY_FLAGS = {
    "live_trading_enabled": False,
    "broker_control_enabled": False,
    "paper_order_execution_enabled": False,
}

SAFETY_NOTES = [
    "Research-only Strategy Candidate Registry. Reads existing reports; never executes.",
    "No broker, no exchange/Alpaca API, no order placement, no paper/live.",
    "No network calls, no credentials, no scheduler/daemon, no subprocess.",
    "Outputs are status summaries for human + Claude + JARVIS review only.",
]

# Pinned posture statements every candidate carries.
ALLOWED_NEXT_STEPS_BASE = (
    "Read-only research memos and protocol specs.",
    "Pre-registered offline backtests against frozen data.",
    "Data QA / freeze workflows.",
    "Documentation, audit, summary, and visibility upgrades.",
)
FORBIDDEN_NEXT_STEPS_BASE = (
    "Live trading. Paper order execution. Order placement.",
    "Broker control / exchange API integration.",
    "Scheduler / background daemon / cron install.",
    "External network calls.",
    "API keys, credentials, .env handling.",
    "Modification of paper or live execution files.",
)

REPO_ROOT = Path(__file__).resolve().parent.parent

# Input sources (all optional; tool degrades gracefully if absent).
AGENTIC_REPORTS_REL = "trading_research/agentic_factory/reports"
STRATEGY_QUEUE_REL = "reports/strategy_factory_routines/strategy_queue/queue.json"
SNAPSHOT_REL = "storage/jarvis/strategy_factory/latest_strategy_factory_snapshot.json"

# Output (runtime; gitignored).
OUTPUT_DIR_REL = "reports/strategy_factory_routines/candidate_registry"
OUTPUT_JSON = "candidates.json"
OUTPUT_MD = "candidates.md"

REQUIRED_CANDIDATE_KEYS = (
    "candidate_id", "title", "lane", "market", "timeframe", "hypothesis",
    "status", "evidence_level", "last_tested_at", "source_reports",
    "best_result_summary", "failure_reason", "blockers", "next_action",
    "priority", "safety_level", "allowed_next_steps", "forbidden_next_steps",
    "notes",
)

VALID_STATUSES = ("IDEA", "ACTIVE", "WATCH", "FAILED", "PARKED", "BLOCKED", "RETIRED")
VALID_EVIDENCE = ("NONE", "WEAK", "MIXED", "STRONG")


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json_safe(path: Path):
    if not path.exists():
        return None, f"missing: {path.as_posix()}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid: {path.as_posix()} ({type(exc).__name__})"


def _lower(value: Any) -> str:
    return str(value or "").lower()


# Seed lanes (deterministic, conservative). Each lane lists folder-name substring
# patterns (lowercase) that should be considered evidence the lane has been worked
# on; classification then upgrades/downgrades status based on report keywords.
SEED_LANES = (
    {
        "candidate_id": "crypto_d1_protocol",
        "title": "Crypto D1 protocol",
        "lane": "crypto_d1_protocol",
        "market": "CRYPTO",
        "timeframe": "D1",
        "hypothesis": "Daily-bar crypto strategies (crash-candle reversion, regime gating) under rigorous IS/OOS gates.",
        "report_match_substrings": ("crypto_d",),
    },
    {
        "candidate_id": "crypto_4h_protocol",
        "title": "Crypto 4H protocol",
        "lane": "crypto_4h_protocol",
        "market": "CRYPTO",
        "timeframe": "4H",
        "hypothesis": "Intraday crypto strategies on 4-hour bars. Requires its own data contract before any evidence claim.",
        "report_match_substrings": ("crypto_4h", "crypto4h"),
    },
    {
        "candidate_id": "nq_es_futures_trend",
        "title": "NQ/ES futures trend research",
        "lane": "nq_es_futures_trend",
        "market": "FUTURES",
        "timeframe": "D1",
        "hypothesis": "Trend / momentum / ORB on NQ / ES daily continuous front-month with explicit cost + friction model.",
        "report_match_substrings": ("nq_", "nq_orb", "data_quality_nq", "es_"),
    },
    {
        "candidate_id": "donchian_variants",
        "title": "Donchian variants",
        "lane": "donchian_variants",
        "market": "FUTURES",
        "timeframe": "D1",
        "hypothesis": "Donchian-channel breakouts and watch-list variants on futures and ETFs.",
        "report_match_substrings": ("s23_", "donchian"),
    },
    {
        "candidate_id": "vol_confirmed_trend_continuation",
        "title": "Volatility-confirmed trend continuation",
        "lane": "vol_confirmed_trend_continuation",
        "market": "FUTURES",
        "timeframe": "D1",
        "hypothesis": "Trend continuation entries gated by EMA/RSI + friction-stress on futures.",
        "report_match_substrings": ("s26_",),
    },
    {
        "candidate_id": "arbitrage_research_protocol",
        "title": "Arbitrage / inefficiency research protocol",
        "lane": "arbitrage_research_protocol",
        "market": "MULTI",
        "timeframe": "N_A",
        "hypothesis": "Paired-series / cross-venue inefficiency research with its own data contract.",
        "report_match_substrings": ("arbitrage", "stat_arb", "pair"),
        # Bundle 4: SPARTA-side Arbitrage Research Protocol v1 docs.
        # Bundle 5: SPARTA-side Arbitrage Data Contract v1 docs.
        # Bundle 6: SPARTA-side Arbitrage Dataset Manifest v1 docs.
        # All of these filenames contain "protocol" / "data" / "manifest" (no
        # FAILED / RETIRED / closeout keywords), so the classifier keeps this
        # lane at IDEA evidence (never ACTIVE, never STRONG) just because docs
        # exist.
        "extra_files": (
            "reports/arbitrage_research_protocol_v1/protocol.md",
            "reports/arbitrage_research_protocol_v1/protocol.json",
            "reports/arbitrage_data_contract_v1/data_contract.md",
            "reports/arbitrage_data_contract_v1/data_contract.json",
            "reports/arbitrage_dataset_manifest_v1/dataset_manifest.md",
            "reports/arbitrage_dataset_manifest_v1/dataset_manifest.json",
        ),
    },
    {
        "candidate_id": "data_qa_freeze",
        "title": "Data QA / freeze tasks",
        "lane": "data_qa_freeze",
        "market": "MULTI",
        "timeframe": "N_A",
        "hypothesis": "Data quality, provenance, and freeze workflows that gate all strategy testing.",
        "report_match_substrings": ("data_quality", "data_freeze", "factory_data_freeze", "provenance"),
    },
    {
        "candidate_id": "jarvis_automation",
        "title": "JARVIS / automation infrastructure",
        "lane": "jarvis_automation",
        "market": "N_A",
        "timeframe": "N_A",
        "hypothesis": "JARVIS dashboard, voice, snapshot panels, and other operator-visibility automation.",
        "report_match_substrings": ("jarvis", "commander"),
    },
    {
        "candidate_id": "strategy_factory_infra",
        "title": "Strategy Factory / routine infrastructure",
        "lane": "strategy_factory_infra",
        "market": "N_A",
        "timeframe": "N_A",
        "hypothesis": "Strategy Factory routine layer, next-bundle generator, candidate registry, and related research-only automation.",
        "report_match_substrings": ("factory_", "strategy_factory", "next_bundle"),
    },
)


# Classification rules: substring → strongest signal carried by a matching report.
# Order matters: first hit wins per report. STATUS_KEYWORDS is searched in
# folder/file names; CONTENT_KEYWORDS is searched in report JSON when available.
STATUS_KEYWORDS = (
    # (substring, status, evidence_level, failure_text_or_none)
    ("failed_", "FAILED", "WEAK", "report name contains 'failed_'"),
    ("rejected", "FAILED", "WEAK", "report name contains 'rejected'"),
    ("retire", "RETIRED", "WEAK", None),
    ("park", "PARKED", "MIXED", None),
    ("closeout", "PARKED", "MIXED", None),  # closing out a lane / next-roadmap memo
    ("block", "BLOCKED", "NONE", "report name contains 'block'"),
    ("watch", "WATCH", "MIXED", None),
    ("oos_result", "WATCH", "MIXED", None),
    ("is_baseline", "ACTIVE", "MIXED", None),
    ("baseline", "ACTIVE", "MIXED", None),
    ("spec", "IDEA", "NONE", None),
    ("protocol", "IDEA", "NONE", None),
    ("plan", "IDEA", "NONE", None),
)

# Strength order so we can pick the "worst" outcome across multiple reports for a
# lane (we are deliberately conservative).
STATUS_PRIORITY = {
    "RETIRED": 7,
    "FAILED": 6,
    "BLOCKED": 5,
    "PARKED": 4,
    "WATCH": 3,
    "ACTIVE": 2,
    "IDEA": 1,
}
EVIDENCE_PRIORITY = {"NONE": 0, "WEAK": 1, "MIXED": 2, "STRONG": 3}

_DATE_RE = re.compile(r"(20\d{2})[-_]?(\d{2})[-_]?(\d{2})")


def _find_report_dirs(repo_root: Path) -> list:
    """Return sorted list of report folder names (deterministic). Empty if absent."""
    base = repo_root / AGENTIC_REPORTS_REL
    if not base.exists():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_dir())


def _find_report_files(repo_root: Path) -> list:
    """Return sorted list of report *file* names too (some are .json/.md not folders)."""
    base = repo_root / AGENTIC_REPORTS_REL
    if not base.exists():
        return []
    return sorted(p.name for p in base.iterdir() if p.is_file())


def _classify_report_name(name: str):
    """Return (status, evidence_level, failure_reason_or_None) inferred from name only.
    Returns (None, None, None) if no keyword matched -- caller keeps prior best."""
    n = name.lower()
    for sub, status, evidence, fail in STATUS_KEYWORDS:
        if sub in n:
            return status, evidence, fail
    return None, None, None


def _date_from_name(name: str):
    """Best-effort deterministic date extraction; returns YYYY-MM-DD or None."""
    m = _DATE_RE.search(name)
    if not m:
        return None
    y, mo, d = m.groups()
    try:
        return f"{y}-{mo}-{d}"
    except Exception:
        return None


def _match_lane_reports(lane_seed: dict, all_names: list, repo_root: Path = REPO_ROOT) -> list:
    """Return all report names whose lowercase contains any seed substring, plus
    the basenames of any seed-specified extra_files that exist on disk."""
    subs = tuple(s.lower() for s in lane_seed.get("report_match_substrings", ()))
    hits = []
    for n in all_names:
        low = n.lower()
        if subs and any(s in low for s in subs):
            hits.append(n)
    # Bundle 4: SPARTA-side protocol/spec docs may live outside the agentic
    # factory reports tree. A seed can list explicit relative paths under
    # `extra_files`; if any exist on disk, their basenames are added to the
    # match list and classified the same way as agentic-factory report names.
    for rel in lane_seed.get("extra_files", ()):
        p = Path(repo_root) / rel
        if p.exists():
            hits.append(p.name)
    # Deterministic + de-duplicate (preserve sort order).
    return sorted(set(hits))


def _build_queue_index(queue_data) -> dict:
    out: dict = {}
    if not isinstance(queue_data, dict):
        return out
    queue = queue_data.get("queue") if isinstance(queue_data.get("queue"), list) else []
    for it in queue:
        if not isinstance(it, dict):
            continue
        lane = _lower(it.get("lane"))
        if lane:
            out[lane] = it
    return out


def _build_candidate(seed: dict, matched_reports: list, queue_index: dict) -> dict:
    """Apply classification rules to produce a single candidate dict."""
    # Start with conservative defaults.
    status = "IDEA"
    evidence = "NONE"
    failure_reason = None

    # Walk matched reports; keep the most-severe status seen (CONSERVATIVE: a single
    # FAILED/PARKED/BLOCKED report wins over many "spec"/"baseline" ones).
    best_failure = None
    for name in matched_reports:
        s, e, f = _classify_report_name(name)
        if s is None:
            continue
        if STATUS_PRIORITY.get(s, 0) > STATUS_PRIORITY.get(status, 0):
            status = s
            evidence = e
            failure_reason = f or failure_reason
            best_failure = f or best_failure
        elif EVIDENCE_PRIORITY.get(e, 0) > EVIDENCE_PRIORITY.get(evidence, 0) and STATUS_PRIORITY.get(s, 0) == STATUS_PRIORITY.get(status, 0):
            evidence = e

    # If there are matched reports but no keyword hit at all, mark IDEA / MIXED.
    if matched_reports and status == "IDEA" and evidence == "NONE":
        evidence = "MIXED"

    # Hard guardrail: never STRONG without explicit external support.
    if evidence == "STRONG":
        evidence = "MIXED"

    # last_tested_at: latest YYYY-MM-DD-style date found in matched report names.
    dates = sorted([d for d in (_date_from_name(n) for n in matched_reports) if d])
    last_tested_at = dates[-1] if dates else None

    queue_item = queue_index.get(_lower(seed.get("lane"))) or {}
    blockers = []
    if isinstance(queue_item.get("blocked"), bool) and queue_item.get("blocked"):
        blockers.append("queue: blocked=True")
    if queue_item.get("required_inputs"):
        for r in queue_item["required_inputs"]:
            blockers.append(f"requires: {r}")

    next_action = queue_item.get("next_bundle_suggestion") or ""
    if not next_action:
        if status in ("FAILED", "RETIRED"):
            next_action = "No further work; lane is closed unless a strictly different hypothesis is proposed."
        elif status == "PARKED":
            next_action = "Park; do not optimize/re-tune in place. Revisit only with new evidence."
        elif status == "BLOCKED":
            next_action = "Resolve named blocker(s) before any new strategy work."
        elif status == "WATCH":
            next_action = "Monitor only; no re-tune. Wait for fresh OOS or external evidence."
        elif status == "ACTIVE":
            next_action = "Continue research-only work; no live/paper execution."
        else:
            next_action = "Author or update the lane's pre-registration / data-contract memo."

    priority = queue_item.get("priority")
    try:
        priority = int(priority) if priority is not None else 5
    except (TypeError, ValueError):
        priority = 5

    cand = {
        "candidate_id": str(seed["candidate_id"]),
        "title": str(seed["title"]),
        "lane": str(seed["lane"]),
        "market": str(seed.get("market", "N_A")),
        "timeframe": str(seed.get("timeframe", "N_A")),
        "hypothesis": str(seed.get("hypothesis", "")),
        "status": status,
        "evidence_level": evidence,
        "last_tested_at": last_tested_at,
        "source_reports": list(matched_reports),
        "best_result_summary": None,  # never claimed unless explicitly supported
        "failure_reason": failure_reason,
        "blockers": blockers,
        "next_action": next_action,
        "priority": priority,
        "safety_level": "research_only",
        "allowed_next_steps": list(ALLOWED_NEXT_STEPS_BASE),
        "forbidden_next_steps": list(FORBIDDEN_NEXT_STEPS_BASE),
        "notes": "",
    }
    return cand


def build_registry(repo_root: Path = REPO_ROOT) -> dict:
    report_dirs = _find_report_dirs(repo_root)
    report_files = _find_report_files(repo_root)
    all_names = sorted(set(report_dirs) | set(report_files))

    queue_data, q_err = _read_json_safe(repo_root / STRATEGY_QUEUE_REL)
    snapshot_data, s_err = _read_json_safe(repo_root / SNAPSHOT_REL)
    queue_index = _build_queue_index(queue_data)

    warnings = []
    if not all_names:
        warnings.append(f"missing: {AGENTIC_REPORTS_REL} (no reports found; seeded with defaults)")
    if q_err:
        warnings.append(q_err)
    if s_err:
        warnings.append(s_err)

    candidates = []
    for seed in SEED_LANES:
        matched = _match_lane_reports(seed, all_names, repo_root)
        cand = _build_candidate(seed, matched, queue_index)
        candidates.append(cand)

    # Deterministic ordering: by candidate_id alphabetic.
    candidates.sort(key=lambda c: c["candidate_id"])

    status_counts: dict = {s: 0 for s in VALID_STATUSES}
    evidence_counts: dict = {e: 0 for e in VALID_EVIDENCE}
    for c in candidates:
        status_counts[c["status"]] = status_counts.get(c["status"], 0) + 1
        evidence_counts[c["evidence_level"]] = evidence_counts.get(c["evidence_level"], 0) + 1

    payload = {
        "schema_version": SCHEMA_VERSION,
        "layer": LAYER,
        "kind": "candidate_registry",
        "read_only": True,
        "generated_at": _now_utc(),
        "candidates": candidates,
        "candidate_count": len(candidates),
        "status_counts": status_counts,
        "evidence_counts": evidence_counts,
        "input_inventory": {
            "agentic_reports_dir": AGENTIC_REPORTS_REL,
            "report_dirs_seen": report_dirs,
            "report_files_seen": report_files,
        },
        "warnings": warnings,
        "safety_flags": dict(SAFETY_FLAGS),
        "safety_notes": list(SAFETY_NOTES),
    }
    return payload


def render_markdown(payload: dict) -> str:
    lines = [
        "# Strategy Candidate Registry v1",
        "",
        f"Generated: {payload['generated_at']}",
        f"Candidates: {payload['candidate_count']}",
        "",
        "## Status counts",
        "",
    ]
    for s, c in payload["status_counts"].items():
        lines.append(f"- **{s}**: {c}")
    lines += ["", "## Evidence counts", ""]
    for e, c in payload["evidence_counts"].items():
        lines.append(f"- **{e}**: {c}")
    lines += [
        "",
        "## Candidates (deterministic order: candidate_id asc)",
        "",
        "| ID | Title | Lane | Market | TF | Status | Evidence | Last tested | Priority | Reports |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | ---: | ---: |",
    ]
    for c in payload["candidates"]:
        lines.append(
            f"| `{c['candidate_id']}` | {c['title']} | {c['lane']} | {c['market']} | "
            f"{c['timeframe']} | **{c['status']}** | {c['evidence_level']} | "
            f"{c['last_tested_at'] or '—'} | {c['priority']} | {len(c['source_reports'])} |"
        )
    lines += ["", "## Per-candidate detail", ""]
    for c in payload["candidates"]:
        lines += [
            f"### `{c['candidate_id']}` — {c['title']}",
            f"- **status:** {c['status']} · **evidence:** {c['evidence_level']} · **safety:** {c['safety_level']}",
            f"- **hypothesis:** {c['hypothesis']}",
            f"- **next action:** {c['next_action']}",
        ]
        if c["blockers"]:
            lines.append("- **blockers:**")
            for b in c["blockers"]:
                lines.append(f"  - {b}")
        if c["source_reports"]:
            lines.append(f"- **source reports ({len(c['source_reports'])}):** "
                        + ", ".join(f"`{r}`" for r in c["source_reports"][:8])
                        + ("…" if len(c["source_reports"]) > 8 else ""))
        if c["failure_reason"]:
            lines.append(f"- **failure reason:** {c['failure_reason']}")
        lines.append("")
    if payload.get("warnings"):
        lines += ["## Warnings", ""]
        for w in payload["warnings"]:
            lines.append(f"- {w}")
    return "\n".join(lines) + "\n"


def generate(repo_root: Path = REPO_ROOT) -> dict:
    payload = build_registry(repo_root)
    out_dir = repo_root / OUTPUT_DIR_REL
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / OUTPUT_JSON).write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    (out_dir / OUTPUT_MD).write_text(render_markdown(payload), encoding="utf-8")
    return payload


def validate(repo_root: Path = REPO_ROOT):
    errors: list = []
    jpath = repo_root / OUTPUT_DIR_REL / OUTPUT_JSON
    mpath = repo_root / OUTPUT_DIR_REL / OUTPUT_MD
    if not jpath.exists():
        return False, [f"missing: {jpath.as_posix()}"]
    try:
        data = json.loads(jpath.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return False, [f"invalid JSON ({type(exc).__name__}): {jpath.as_posix()}"]
    if not isinstance(data, dict):
        return False, ["candidates.json is not a JSON object"]
    sf = data.get("safety_flags") or {}
    for flag in ("live_trading_enabled", "broker_control_enabled", "paper_order_execution_enabled"):
        if sf.get(flag) is not False:
            errors.append(f"safety_flag {flag} not pinned False")
    cands = data.get("candidates")
    if not isinstance(cands, list) or not cands:
        errors.append("candidates list missing or empty")
    else:
        for c in cands:
            if not isinstance(c, dict):
                errors.append("non-dict candidate")
                continue
            for k in REQUIRED_CANDIDATE_KEYS:
                if k not in c:
                    errors.append(f"candidate {c.get('candidate_id', '?')!r}: missing key {k}")
            if c.get("status") not in VALID_STATUSES:
                errors.append(f"candidate {c.get('candidate_id', '?')!r}: invalid status {c.get('status')!r}")
            if c.get("evidence_level") not in VALID_EVIDENCE:
                errors.append(f"candidate {c.get('candidate_id', '?')!r}: invalid evidence_level {c.get('evidence_level')!r}")
            if c.get("safety_level") != "research_only":
                errors.append(f"candidate {c.get('candidate_id', '?')!r}: safety_level != research_only")
            if c.get("evidence_level") == "STRONG":
                # Hard rule: registry never claims STRONG unless explicit external support
                # (which we never produce automatically).
                errors.append(f"candidate {c.get('candidate_id', '?')!r}: evidence_level STRONG not allowed without explicit support")
    if not mpath.exists():
        errors.append(f"missing: {mpath.as_posix()}")
    return (not errors), errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="SPARTA Strategy Candidate Registry v1 (research-only)",
    )
    parser.add_argument("command", choices=("build", "show", "validate"))
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    if args.command == "build":
        payload = generate(root)
        print(f"generated_at: {payload['generated_at']}")
        print(f"candidates:   {payload['candidate_count']}")
        for s, c in payload["status_counts"].items():
            if c:
                print(f"  {s:>8}: {c}")
        print(f"json:         {(root / OUTPUT_DIR_REL / OUTPUT_JSON).as_posix()}")
        return 0
    if args.command == "show":
        jpath = root / OUTPUT_DIR_REL / OUTPUT_JSON
        if not jpath.exists():
            print(f"no candidates.json yet; run `build` first ({jpath.as_posix()})")
            return 1
        data = json.loads(jpath.read_text(encoding="utf-8"))
        print(f"candidate_count: {data.get('candidate_count')}")
        print("status_counts:")
        for s, c in (data.get("status_counts") or {}).items():
            if c:
                print(f"  {s:>8}: {c}")
        print(f"json:            {jpath.as_posix()}")
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

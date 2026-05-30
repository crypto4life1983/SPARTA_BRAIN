"""Reusable final-decision / readiness orchestration (Factory-D8).

Ladder modules K (readiness_gate) + L (final_decision): take the per-module
verdicts already produced by the earlier factory steps and map them -- by a fixed,
conservative rule set -- to ONE research decision and ONE readiness level. It is
the anti-emotion gate: it converts "this looks promising" into a mechanical
disposition against the documented anti-overfit lessons (Donchian path-luck, S26
single-regime / single-year concentration, IS_FAIL-must-stop-before-OOS).

It decides nothing on its own beyond combining supplied verdicts/metrics. It runs
NO strategy, fetches NO data, and -- critically -- NEVER promotes a candidate to a
paper/live readiness level on its own: those require an explicit separate-memo
override field, so the default path can never reach them.

OFFLINE / INERT: Python standard library only (typing) plus the report writer. It
opens no network connection, spawns no child process, fetches no data, runs no
shell or version-control call, reads no real market data, and does NO dynamic code
loading. It mutates nothing and writes nothing.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from engine import validation_reports


# Research decisions (ladder module L).
CONTINUE_RESEARCH = "CONTINUE_RESEARCH"
PARK_CANDIDATE = "PARK_CANDIDATE"
FAIL_CANDIDATE = "FAIL_CANDIDATE"
REDESIGN_REQUIRED = "REDESIGN_REQUIRED"

# Readiness levels (ladder module K), lowest -> highest.
BLOCKED = "BLOCKED"
RESEARCH_CANDIDATE = "RESEARCH_CANDIDATE"
VALIDATION_CANDIDATE = "VALIDATION_CANDIDATE"
PAPER_REVIEW_CANDIDATE = "PAPER_REVIEW_CANDIDATE"
PAPER_READY = "PAPER_READY"
LIVE_READY = "LIVE_READY"


# Ladder order for human-readable summaries / known-key validation.
LADDER_ORDER: List[str] = [
    "spec_check", "is_baseline", "oos", "entry_significance",
    "sequence_risk", "regime", "walk_forward", "friction", "multimarket",
]
KNOWN_MODULES = set(LADDER_ORDER)

# The five core risk modules whose acceptability gates promotion.
CORE = ["entry_significance", "sequence_risk", "regime", "walk_forward", "friction"]

# Per-module verdict classification. POSITIVE == acceptable; FAIL == terminal /
# severe; anything present but in neither is treated as a "weak" middle.
_POSITIVE: Dict[str, set] = {
    "is_baseline": {"IS_CONTINUE", "IS_PASS", "CONTINUE", "PASS"},
    "oos": {"PASS", "OOS_PASS"},
    "entry_significance": {"ENTRY_EDGE_SUPPORTED"},
    "sequence_risk": {"SEQUENCE_RISK_ACCEPTABLE"},
    "regime": {"REGIME_RISK_ACCEPTABLE"},
    "walk_forward": {"WALK_FORWARD_STABLE"},
    "friction": {"FRICTION_ROBUST"},
}
_FAIL: Dict[str, set] = {
    "is_baseline": {"IS_FAIL", "FAIL"},
    "oos": {"FAIL", "OOS_FAIL"},
    "entry_significance": {"ENTRY_EDGE_NOT_SUPPORTED"},
    "sequence_risk": {"SEQUENCE_RISK_FRAGILE"},
    "regime": {"REGIME_RISK_FAIL"},
    "walk_forward": {"WALK_FORWARD_FAIL"},
    "friction": {"FRICTION_FAIL"},
}


def _is_pos(module: str, v: Any) -> bool:
    return isinstance(v, str) and v in _POSITIVE.get(module, set())


def _is_fail(module: str, v: Any) -> bool:
    return isinstance(v, str) and v in _FAIL.get(module, set())


def _classify(module: str, v: Any) -> str:
    """One of 'absent' / 'ok' / 'bad' / 'weak' for a single module verdict."""
    if v is None:
        return "absent"
    if _is_pos(module, v):
        return "ok"
    if _is_fail(module, v):
        return "bad"
    return "weak"


def _data_integrity_fail(metrics: Optional[Dict[str, Any]]) -> bool:
    if not metrics:
        return False
    if metrics.get("data_integrity") in ("FAIL", "BAD"):
        return True
    if metrics.get("data_integrity_ok") is False:
        return True
    return False


def normalize_module_verdicts(verdicts: Dict[str, Any]) -> Dict[str, Any]:
    """Validate + normalize a {module: verdict} mapping.

    Rejects a non-dict input. Drops non-string / empty verdicts with a warning,
    flags unknown module keys (but retains them), and returns
    {"normalized", "warnings", "unknown_keys"}.
    """
    if not isinstance(verdicts, dict):
        raise TypeError("verdicts must be a dict of {module: verdict}")

    normalized: Dict[str, str] = {}
    warnings: List[str] = []
    unknown: List[str] = []
    for k, v in verdicts.items():
        if not isinstance(v, str) or not v.strip():
            warnings.append(f"{k}: non-string/empty verdict ignored")
            continue
        val = v.strip()
        if k not in KNOWN_MODULES:
            warnings.append(f"unknown module key: {k}")
            unknown.append(k)
        normalized[k] = val
    return {"normalized": normalized, "warnings": warnings, "unknown_keys": unknown}


def hard_blockers(
    verdicts: Dict[str, Any], metrics: Optional[Dict[str, Any]] = None
) -> List[str]:
    """Return the list of hard promotion blockers (empty == none).

    Any non-empty result forces readiness to BLOCKED. A terminal IS/OOS verdict, a
    fragile trade sequence, a regime/walk-forward/friction failure, an unsupported
    entry edge corroborated by another weakness, a non-positive post-friction OOS,
    a data-integrity failure, or a paper/live request without a passed gate each
    count as a blocker.
    """
    out: List[str] = []
    is_v = verdicts.get("is_baseline")
    oos_v = verdicts.get("oos")

    if _is_fail("is_baseline", is_v):
        out.append("IS_FAIL: in-sample baseline failed")
    if _is_fail("oos", oos_v):
        out.append("OOS_FAIL: out-of-sample failed")
    if verdicts.get("sequence_risk") == "SEQUENCE_RISK_FRAGILE":
        out.append("SEQUENCE_RISK_FRAGILE: trade-sequence fragility")
    if verdicts.get("regime") == "REGIME_RISK_FAIL":
        out.append("REGIME_RISK_FAIL: edge confined to one regime")
    if verdicts.get("walk_forward") == "WALK_FORWARD_FAIL":
        out.append("WALK_FORWARD_FAIL: unstable across rolling windows")
    if verdicts.get("friction") == "FRICTION_FAIL":
        out.append("FRICTION_FAIL: no edge after costs")

    if verdicts.get("entry_significance") == "ENTRY_EDGE_NOT_SUPPORTED":
        others = [
            m for m in CORE
            if m != "entry_significance"
            and _classify(m, verdicts.get(m)) in ("weak", "bad")
        ]
        if others:
            out.append(
                "ENTRY_EDGE_NOT_SUPPORTED with corroborating weakness: "
                + ", ".join(others)
            )

    if metrics:
        oaf = metrics.get("oos_net_r_after_friction")
        if oaf is not None and oaf <= 0:
            out.append("OOS net R is non-positive after friction")
        if _data_integrity_fail(metrics):
            out.append("data integrity failure")
        if metrics.get("paper_or_live_requested") and not metrics.get("paper_gate_passed"):
            out.append("paper/live requested without a passed readiness gate")
    return out


def derive_research_decision(
    verdicts: Dict[str, Any], metrics: Optional[Dict[str, Any]] = None
) -> str:
    """Map module verdicts to ONE conservative research decision.

    FAIL_CANDIDATE     -- IS or OOS failed, or a data-integrity failure.
    REDESIGN_REQUIRED  -- a hard blocker exists AND metrics flag `redesign_hint`
                          (kept rare; a modified hypothesis may still be useful).
    PARK_CANDIDATE     -- a non-IS/OOS hard blocker, a terminal core module, an
                          unproven IS baseline, or two-plus inconclusive core
                          modules: evidence is weak/thin but not an outright fail.
    CONTINUE_RESEARCH  -- IS positive, no hard blockers, no terminal core module,
                          and at most one inconclusive core module.
    """
    is_v = verdicts.get("is_baseline")
    oos_v = verdicts.get("oos")

    if _is_fail("is_baseline", is_v) or _is_fail("oos", oos_v) or _data_integrity_fail(metrics):
        return FAIL_CANDIDATE

    blockers = hard_blockers(verdicts, metrics)
    if blockers:
        if metrics and metrics.get("redesign_hint") is True:
            return REDESIGN_REQUIRED
        return PARK_CANDIDATE

    bad = sum(1 for m in CORE if _classify(m, verdicts.get(m)) == "bad")
    weak = sum(1 for m in CORE if _classify(m, verdicts.get(m)) == "weak")
    if bad >= 1:
        return PARK_CANDIDATE
    if not _is_pos("is_baseline", is_v):
        return PARK_CANDIDATE
    if weak <= 1:
        return CONTINUE_RESEARCH
    return PARK_CANDIDATE


def derive_readiness_level(
    verdicts: Dict[str, Any], metrics: Optional[Dict[str, Any]] = None
) -> str:
    """Map module verdicts to ONE conservative readiness level.

    Any hard blocker -> BLOCKED. With no OOS pass yet the ceiling is
    RESEARCH_CANDIDATE. An OOS pass with every core risk module acceptable reaches
    VALIDATION_CANDIDATE. PAPER_REVIEW_CANDIDATE requires explicit, passed paper
    gates. PAPER_READY / LIVE_READY are NEVER reached on the default path -- each
    needs an explicit separate-memo override field, so this module cannot promote
    a candidate into paper/live on its own.
    """
    if hard_blockers(verdicts, metrics):
        return BLOCKED

    if not _is_pos("oos", verdicts.get("oos")):
        return RESEARCH_CANDIDATE

    core_all_present = all(verdicts.get(m) is not None for m in CORE)
    core_all_ok = all(_is_pos(m, verdicts.get(m)) for m in CORE)
    if not (core_all_present and core_all_ok):
        return RESEARCH_CANDIDATE

    level = VALIDATION_CANDIDATE
    if not (metrics and metrics.get("paper_review_gates_passed") is True):
        return level

    level = PAPER_REVIEW_CANDIDATE
    if metrics.get("live_ready_override") is True and metrics.get("live_ready_memo_commit"):
        return LIVE_READY
    if metrics.get("paper_ready_override") is True and metrics.get("paper_ready_memo_commit"):
        return PAPER_READY
    return level


def summarize_validation_ladder(verdicts: Dict[str, Any]) -> str:
    """Concise, human-readable one-line-per-module status summary."""
    lines: List[str] = []
    seen = set()
    for key in LADDER_ORDER:
        if key in verdicts:
            lines.append(f"{key}: {verdicts[key]}")
            seen.add(key)
    for key in verdicts:
        if key not in seen:
            lines.append(f"{key}: {verdicts[key]} (unknown module)")
    if not lines:
        return "(no module verdicts supplied)"
    return "\n".join(lines)


def build_decision_report(
    *,
    branch_id: str,
    title: str,
    verdicts: Dict[str, Any],
    metrics: Optional[Dict[str, Any]] = None,
    decision: Optional[str] = None,
    readiness: Optional[str] = None,
    module_id: str = "final_decision",
    source_commits: Optional[Dict[str, Any]] = None,
    input_files: Optional[List[str]] = None,
    data_window: Optional[Dict[str, Any]] = None,
    frozen_parameters: Optional[Dict[str, Any]] = None,
    status: str = "COMPLETE",
    caveats: Optional[List[Any]] = None,
    next_allowed_step: str = "human_review",
    forbidden_actions: Optional[List[Any]] = None,
    notes: Optional[List[Any]] = None,
    created_utc: str = "",
) -> Dict[str, Any]:
    """Assemble a Factory-D2-schema final-decision report.

    The report `verdict` is the research decision; the readiness level, hard
    blockers, normalized module verdicts, and the ladder summary are recorded in
    `metrics`. Both the decision and the readiness default to the derived values
    but the caller may override. Writes nothing.
    """
    norm = normalize_module_verdicts(verdicts)
    v_norm = norm["normalized"]
    blockers = hard_blockers(v_norm, metrics)
    dec = decision or derive_research_decision(v_norm, metrics)
    rd = readiness or derive_readiness_level(v_norm, metrics)

    report_metrics: Dict[str, Any] = {
        "module_verdicts": v_norm,
        "verdict_warnings": norm["warnings"],
        "hard_blockers": blockers,
        "research_decision": dec,
        "readiness_level": rd,
        "ladder_summary": summarize_validation_ladder(v_norm),
    }
    if metrics:
        report_metrics["context_metrics"] = dict(metrics)

    default_forbidden = [
        "no_auto_promotion", "no_paper_or_live", "no_optimization",
        "no_data_fetch", "no_execution_or_api", "no_hidden_failures",
    ]
    return validation_reports.make_report(
        branch_id=branch_id,
        module_id=module_id,
        title=title,
        status=status,
        verdict=dec,
        created_utc=created_utc,
        source_commits=dict(source_commits or {}),
        input_files=list(input_files or []),
        data_window=dict(data_window or {}),
        frozen_parameters=dict(frozen_parameters or {}),
        metrics=report_metrics,
        caveats=list(caveats if caveats is not None else blockers),
        next_allowed_step=next_allowed_step,
        forbidden_actions=list(forbidden_actions or default_forbidden),
        notes=list(notes or []),
    )

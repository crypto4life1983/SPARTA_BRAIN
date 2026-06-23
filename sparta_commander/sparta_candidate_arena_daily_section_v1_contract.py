"""SPARTA Candidate Arena DAILY SECTION v1 -- PURE, READ-ONLY display section.

Folds the committed `sparta_candidate_arena_v1_contract` into a compact summary + display-only
HTML/markdown section for the daily/morning/control report surface. It is DISPLAY-ONLY: it reads
the pure arena contract (frozen/known state), summarizes the top promising signal, the active
HOLD candidate, the blocked candidates, the data-pipeline statuses, and the next safe
human-gated action -- and renders them with NO execution affordances (no script/onclick/form/
button). It fetches NOTHING, connects to NOTHING, promotes NOTHING, advances NOTHING, and ranks
NOTHING for action. VRP Phase-2 stays DATA_COLLECTION_STATUS only (never strategy evidence);
MISSING_EVIDENCE stays explicit. Deterministic.
"""
from __future__ import annotations

from typing import Any

import sparta_commander.sparta_candidate_arena_v1_contract as _arena

SEC_SCHEMA_VERSION = 1
SEC_MODE = "RESEARCH_ONLY"


def _row(rows, cid):
    for r in rows:
        if r.get("candidate_id") == cid:
            return r
    return None


def build_arena_daily_summary() -> dict[str, Any]:
    """PURE. Compact daily summary derived from the committed arena contract. No I/O."""
    arena = _arena.build_candidate_arena()
    arena_valid = _arena.validate_candidate_arena(arena)["valid"]
    rows = arena["rows"]

    promising = [r for r in rows if str(r.get("evidence_status", "")).startswith("PROMISING")]
    top = promising[0] if promising else None
    hold = next((r for r in rows if r.get("current_status") == "ACTIVE_HOLD"), None)
    blocked = [r for r in rows if r.get("current_status") in ("REJECTED", "NO_GO")]
    data_pipelines = [r for r in rows if r.get("current_status") == "DATA_COLLECTION_STATUS"]

    def slim(r, keys):
        return {k: r.get(k) for k in keys} if r else None

    summary: dict[str, Any] = {
        "schema_version": SEC_SCHEMA_VERSION, "mode": SEC_MODE,
        "section": "sparta_candidate_arena_daily",
        "is_read_only_section": True,
        "as_of": arena["as_of"],
        "arena_valid": arena_valid,
        "top_promising_signal": slim(top, ("candidate_id", "family_name", "evidence_status",
                                           "current_status", "blocker_reason",
                                           "next_safe_action")),
        "top_promising_is_promoted": bool(top and "NOT_PROMOTED" not in top.get(
            "current_status", "")) if top else False,
        "active_hold": slim(hold, ("candidate_id", "current_status", "evidence_status",
                                   "blocker_reason", "next_safe_action")),
        "blocked_candidates": [slim(r, ("candidate_id", "current_status", "blocker_reason"))
                               for r in blocked],
        "data_pipeline_statuses": [
            {**slim(r, ("candidate_id", "current_status", "evidence_status", "blocker_reason")),
             "is_strategy_evidence": False} for r in data_pipelines],
        "next_safe_human_gated_action": (top or {}).get(
            "next_safe_action", "no safe action -- continue frozen-window collection / data "
            "pipelines; promotion human-gated"),
        "anything_ready_for_human_review": arena["anything_ready_for_human_review"],
        "anything_ready_for_promotion": arena["anything_ready_for_promotion"],
        "missing_evidence_cells": arena["missing_evidence_cells"],
        # preservation
        "vrp_phase2_is_data_status_only": bool(data_pipelines) and all(
            r.get("evidence_status") == "NOT_BACKTEST_EVIDENCE" for r in data_pipelines),
        "promotes_nothing": True, "advances_c22": False, "reactivates_c23_c24": False,
        "fetches_nothing": True, "ranks_for_action": False,
    }
    return summary


def validate_arena_daily_summary(summary: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when read-only, the underlying arena is valid, the top
    promising signal is NOT promoted, every data-pipeline status is NOT strategy evidence, nothing
    is review/promotion ready, MISSING_EVIDENCE is preserved, and nothing is advanced/promoted."""
    f: list = []
    if summary.get("mode") != SEC_MODE:
        f.append("mode_not_research_only")
    if summary.get("is_read_only_section") is not True:
        f.append("not_read_only")
    if summary.get("arena_valid") is not True:
        f.append("underlying_arena_invalid")
    if summary.get("top_promising_is_promoted") is not False:
        f.append("top_promising_marked_promoted")
    tps = summary.get("top_promising_signal") or {}
    if tps and "NOT_PROMOTED" not in str(tps.get("current_status", "")):
        f.append("top_promising_current_status_not_unpromoted")
    for d in (summary.get("data_pipeline_statuses") or []):
        if d.get("is_strategy_evidence") is not False:
            f.append("data_pipeline_treated_as_evidence")
        if d.get("evidence_status") != "NOT_BACKTEST_EVIDENCE":
            f.append("data_pipeline_not_marked_status_only")
    ah = summary.get("active_hold") or {}
    if ah and ah.get("current_status") != "ACTIVE_HOLD":
        f.append("active_hold_not_hold")
    if summary.get("anything_ready_for_promotion") is not False:
        f.append("must_not_be_promotion_ready")
    if summary.get("anything_ready_for_human_review") is not False:
        f.append("must_not_be_review_ready")
    if not isinstance(summary.get("missing_evidence_cells"), int) or summary[
            "missing_evidence_cells"] <= 0:
        f.append("missing_evidence_not_preserved")
    for k in ("promotes_nothing", "fetches_nothing"):
        if summary.get(k) is not True:
            f.append("flag_off_%s" % k)
    if summary.get("advances_c22") is not False or summary.get("reactivates_c23_c24") is not False:
        f.append("must_not_advance_or_reactivate")
    if summary.get("ranks_for_action") is not False:
        f.append("must_not_rank_for_action")
    return {"valid": not f, "failures": f}


def _esc(s: Any) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _np_suffix(action: Any) -> str:
    # cosmetic: append "(NOT promoted)" only if the action text doesn't already say it
    return "" if "not promoted" in str(action).lower() else " (NOT promoted)"


def render_arena_section_html(summary: dict[str, Any] | None = None) -> str:
    """PURE. Display-only HTML section. No script/onclick/form/button."""
    s = summary or build_arena_daily_summary()
    tps = s.get("top_promising_signal") or {}
    ah = s.get("active_hold") or {}
    out = ["<div class='jv-am-h'>Candidate Arena (read-only) — as-of %s</div>"
           % _esc(s.get("as_of"))]
    out.append("<div class='jv-detail'>Top promising signal: <b>%s</b> [%s] — %s%s</div>"
               % (_esc(tps.get("candidate_id")), _esc(tps.get("evidence_status")),
                  _esc(tps.get("next_safe_action")), _np_suffix(tps.get("next_safe_action"))))
    out.append("<div class='jv-detail'>Active HOLD: <b>%s</b> — %s</div>"
               % (_esc(ah.get("candidate_id")), _esc(ah.get("blocker_reason"))))
    out.append("<div class='jv-detail'>Blocked: %s</div>"
               % _esc(", ".join("%s(%s)" % (b["candidate_id"], b["current_status"])
                                for b in s.get("blocked_candidates") or [])))
    for d in s.get("data_pipeline_statuses") or []:
        out.append("<div class='jv-detail'>Data pipeline: <b>%s</b> = %s (DATA_COLLECTION_STATUS "
                   "only, not strategy evidence)</div>"
                   % (_esc(d["candidate_id"]), _esc(d["evidence_status"])))
    out.append("<div class='jv-detail'>Next safe human-gated action: %s</div>"
               % _esc(s.get("next_safe_human_gated_action")))
    out.append("<div class='jv-detail'>ready_for_human_review=%s | ready_for_promotion=%s | "
               "missing_evidence_cells=%s | promotion is human-gated</div>"
               % (s.get("anything_ready_for_human_review"),
                  s.get("anything_ready_for_promotion"), s.get("missing_evidence_cells")))
    return "".join(out)


def render_arena_section_markdown(summary: dict[str, Any] | None = None) -> str:
    """PURE. Display-only markdown section."""
    s = summary or build_arena_daily_summary()
    tps = s.get("top_promising_signal") or {}
    ah = s.get("active_hold") or {}
    lines = ["### Candidate Arena (read-only) — as-of %s" % s.get("as_of"),
             "- **Top promising signal:** %s [%s] — %s%s" % (
                 tps.get("candidate_id"), tps.get("evidence_status"),
                 tps.get("next_safe_action"), _np_suffix(tps.get("next_safe_action"))),
             "- **Active HOLD:** %s — %s" % (ah.get("candidate_id"), ah.get("blocker_reason")),
             "- **Blocked:** %s" % ", ".join("%s(%s)" % (b["candidate_id"], b["current_status"])
                                             for b in s.get("blocked_candidates") or [])]
    for d in s.get("data_pipeline_statuses") or []:
        lines.append("- **Data pipeline:** %s = %s (DATA_COLLECTION_STATUS only, not strategy "
                     "evidence)" % (d["candidate_id"], d["evidence_status"]))
    lines.append("- **Next safe human-gated action:** %s" % s.get("next_safe_human_gated_action"))
    lines.append("- ready_for_human_review=%s | ready_for_promotion=%s | missing_evidence_cells=%s"
                 % (s.get("anything_ready_for_human_review"),
                    s.get("anything_ready_for_promotion"), s.get("missing_evidence_cells")))
    return "\n".join(lines)

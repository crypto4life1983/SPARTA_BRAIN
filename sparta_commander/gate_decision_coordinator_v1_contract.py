"""SPARTA Gate Decision Coordinator v1 -- THIN, PURE, RESEARCH-ONLY.

A thin coordination layer ON TOP of the existing SPARTA research-automation pieces
(Safe Research Autopilot v1, Research Expansion Plan v1, Research Expansion
Autopilot Integration v1, the Morning Report, candidate-lifecycle status, and the
rejected-ledger status). It does NOT replace any of them. It reads the already-
gathered, DECLARED state (repo cleanliness / ahead-behind, candidate status,
rejected-ledger status) and CLARIFIES the current gate: it emits a single
recommended next SAFE command (a human-pasteable token) and a decision-ready
morning-report block.

It does NOTHING else: it does NOT commit, NOT push, NOT advance/reject, NOT run any
replay / detector / labels / relabel / optimization, NOT fetch data, NOT write
files, and NOT touch any paper / live / broker / order surface. Every recommended
command is a HUMAN-approval token -- the coordinator only recommends; the human
still approves every commit, push, advance/reject, and any trading-adjacent action.
Every capability flag is pinned False with a full scope_locks set.

Recommendation priority (each is a recommendation to the HUMAN, never an action):
  1. uncommitted APPROVED unit        -> recommend COMMIT approval
     uncommitted but NOT yet approved -> STOP and await human approval
  2. local commits ahead of origin    -> recommend PUSH approval
  3. rejected-ledger mismatch         -> recommend LEDGER-BUMP approval
  4. an open candidate gate           -> recommend the gate's HUMAN_DECISION token
  5. clean + synced + no open gate    -> recommend NEXT candidate research
"""
from __future__ import annotations

from typing import Any

import sparta_commander.research_expansion_plan_v1_contract as _rep
import sparta_commander.research_expansion_autopilot_integration_v1_spec as _rei
import sparta_commander.safe_research_autopilot_v1_contract as _sara
import sparta_commander.crypto_d1_candidate_research_lane_status_v1_contract as _lane

GDC_SCHEMA_VERSION = 1
GDC_MODE = "RESEARCH_ONLY"
GDC_LANE = "crypto_d1_auto_research"

# The pieces this coordinator sits on top of (it clarifies, never replaces).
INTEGRATES_WITH = (
    "safe_research_autopilot_v1",
    "research_expansion_plan_v1",
    "research_expansion_autopilot_integration_v1",
    "sparta_autopilot_morning_report",
    "candidate_lifecycle_status",
    "rejected_ledger_status",
)

# The CURRENT canonical rejected ledger (C1-C15) -- reused, not redefined.
CANONICAL_REJECTED_FAMILIES = tuple(_rep.REJECTED_FAMILIES_C1_TO_C16)
EXPECTED_LEDGER_COUNT = len(CANONICAL_REJECTED_FAMILIES)            # 21 (C1-C16)

# The only token the coordinator may recommend to OPEN new research.
NEXT_CANDIDATE_TOKEN = _rei.ALLOWED_BATCH_RECOMMENDED_TOKEN  # BUILD_NEXT_..._ONLY

# Recommendation kinds (the COMPLETE allowlist).
REC_NEXT_CANDIDATE = "RECOMMEND_NEXT_CANDIDATE_RESEARCH"
REC_AUTOMATION_READINESS = "RECOMMEND_AUTOMATION_READINESS_STEP"
REC_PUSH = "RECOMMEND_PUSH_APPROVAL"
REC_COMMIT = "RECOMMEND_COMMIT_APPROVAL"
REC_LEDGER_BUMP = "RECOMMEND_LEDGER_BUMP_APPROVAL"
REC_GATE_DECISION = "RECOMMEND_GATE_DECISION"
REC_STOP_AWAIT_APPROVAL = "STOP_AWAIT_HUMAN_APPROVAL"
ALL_RECOMMENDATION_KINDS = (
    REC_NEXT_CANDIDATE, REC_AUTOMATION_READINESS, REC_PUSH, REC_COMMIT,
    REC_LEDGER_BUMP, REC_GATE_DECISION, REC_STOP_AWAIT_APPROVAL,
)

# The candidate-research-lane directive (authoritative): post-C16 the idle/default
# recommendation must NOT drift back to "next candidate research" -- it is
# automation readiness.
AUTOMATION_READINESS_TOKEN = _lane.AUTOMATION_READINESS_TOKEN  # stable prior-stage token

# Substrings the coordinator must NEVER emit in a recommended command.
FORBIDDEN_COMMAND_SUBSTRINGS = (
    "paper", "live", "broker", "order", "exchange", "wallet", "credential",
    "auto_commit", "auto_push", "auto-commit", "auto-push", "place", "execute_trade",
    "deploy_capital", "micro_live",
)

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "auto_commits", "auto_pushes", "auto_advances",
    "auto_rejects", "runs_replay", "runs_detector", "runs_labels", "relabels",
    "optimizes_parameters", "runs_robustness", "runs_portfolio_compute",
    "fetches_data", "reads_real_data", "mutates_data", "modifies_scheduler",
    "sends_notifications", "calls_api", "uses_network", "uses_credentials",
    "connects_broker", "connects_exchange", "uses_real_money", "places_orders",
    "contains_order_logic", "paper_trading", "live_trading", "deploys_capital",
    "promotes_gate", "unlocks_downstream_gate", "skips_any_gate",
    "replaces_autopilot_or_orchestrator", "reproposes_rejected_family",
    "advances_without_human_approval", "claims_profitability", "claims_edge",
    "crosses_into_forbidden_gate",
)


def _open_candidates(candidates: dict) -> list:
    out = []
    for key in sorted((candidates or {}).keys()):
        c = candidates[key] or {}
        action = c.get("next_action") or ""
        if c.get("active") and action and not str(action).startswith("NONE"):
            out.append({"candidate": key, "family": c.get("family"),
                        "next_action": action})
    return out


def closed_excluded_candidates(candidates: dict) -> list:
    """Pure: the closed/rejected candidates, each tagged with whether it is in the
    current canonical rejected ledger (i.e. permanently excluded from re-proposal)
    and whether its lifecycle has shipped."""
    out = []
    for key in sorted((candidates or {}).keys()):
        c = candidates[key] or {}
        status = str(c.get("status", ""))
        if status.startswith("REJECTED"):
            fam = c.get("family")
            out.append({
                "candidate": key, "family": fam,
                "status": "rejected",
                "kept_on_record": "KEPT_ON_RECORD" in status,
                "shipped": bool(c.get("shipped")),
                "excluded_from_reproposal": fam in CANONICAL_REJECTED_FAMILIES,
            })
    return out


def _ledger_status(ledger: dict) -> dict:
    ledger = ledger or {}
    canonical = ledger.get("canonical_count", EXPECTED_LEDGER_COUNT)
    expected = ledger.get("expected_count", EXPECTED_LEDGER_COUNT)
    reconciles = ledger.get("reconciles", True)
    consistent = bool(reconciles) and canonical == expected
    return {
        "canonical_count": canonical, "expected_count": expected,
        "reconciles": bool(reconciles), "consistent": consistent,
        "missing_family": ledger.get("missing_family"),
    }


def coordinate(state: dict) -> dict[str, Any]:
    """PURE thin coordinator. Reads declared (repo / candidates / ledger) state and
    returns the single recommended next SAFE command -- always a HUMAN-approval
    token. Executes nothing; recommends nothing trading-adjacent."""
    repo = (state or {}).get("repo") or {}
    candidates = (state or {}).get("candidates") or {}
    ledger = (state or {}).get("ledger") or {}

    ls = _ledger_status(ledger)
    opens = _open_candidates(candidates)
    closed = closed_excluded_candidates(candidates)

    rec_kind = None
    command = None
    reason = None
    detected_gate = None

    uncommitted = bool(repo.get("uncommitted_changes"))
    approved_unit = repo.get("approved_unit_pending_commit")
    ahead = int(repo.get("ahead", 0) or 0)

    # 1) uncommitted changes
    if uncommitted and approved_unit:
        rec_kind = REC_COMMIT
        detected_gate = "uncommitted_approved_unit"
        command = "APPROVE_COMMIT_%s" % str(approved_unit).upper()
        reason = ("an approved unit (%s) is committed-ready in the working tree; "
                  "recommend the human paste the commit-approval token (no "
                  "auto-commit)" % approved_unit)
    elif uncommitted and not approved_unit:
        rec_kind = REC_STOP_AWAIT_APPROVAL
        detected_gate = "uncommitted_unapproved_changes"
        command = "STOP_AWAIT_HUMAN_APPROVAL_FOR_UNCOMMITTED_CHANGES"
        reason = ("the working tree has uncommitted changes that are NOT yet "
                  "approved; STOP and await explicit human approval (never "
                  "auto-commit)")
    # 2) local ahead of origin
    elif ahead > 0:
        rec_kind = REC_PUSH
        detected_gate = "local_ahead_of_origin"
        command = "APPROVE_PUSH_LOCAL_STACK"
        reason = ("%d local commit(s) are ahead of origin/master; recommend the "
                  "human paste the push-approval token (no auto-push)" % ahead)
    # 3) rejected-ledger mismatch
    elif not ls["consistent"]:
        rec_kind = REC_LEDGER_BUMP
        detected_gate = "rejected_ledger_mismatch"
        miss = ls.get("missing_family")
        command = (ledger.get("add_token")
                   or ("UPDATE_REJECTED_LEDGERS_ADD_%s"
                       % (str(miss).upper() if miss else "MISSING_FAMILY")))
        reason = ("the rejected ledger is inconsistent (canonical=%s expected=%s "
                  "reconciles=%s); recommend a human-approved ledger bump"
                  % (ls["canonical_count"], ls["expected_count"], ls["reconciles"]))
    # 4) an open candidate gate
    elif opens:
        rec_kind = REC_GATE_DECISION
        nxt = opens[-1]
        detected_gate = "open_candidate_gate"
        command = nxt["next_action"]
        reason = ("candidate %s is at an open gate; recommend the human paste its "
                  "decision token (advance/reject stays human-gated)"
                  % nxt["candidate"])
    # 5) clean + synced + ledger ok + no open gate IN STATE -> defer to the
    #    candidate-research-lane directive (authoritative). If the lane has an
    #    ACTIVE open candidate (e.g. C17 frozen proposal), recommend its human
    #    decision; else if the lane is at automation readiness, recommend that;
    #    else fall back to next-candidate research.
    else:
        _lane_status = _lane.get_lane_status()
        if _lane_status.get("open_candidate_gate") is True:
            rec_kind = REC_GATE_DECISION
            detected_gate = "active_candidate_open_gate"
            command = _lane_status.get("next_required_action")
            reason = ("candidate %s is an open frozen artifact on the lane; "
                      "recommend its human decision (advance or reject)"
                      % _lane_status.get("active_candidate"))
        elif _lane_status.get("next_is_automation_readiness") is True:
            rec_kind = REC_AUTOMATION_READINESS
            detected_gate = "candidate_lane_complete_automation_readiness"
            command = AUTOMATION_READINESS_TOKEN
            reason = ("repo is clean and synced and no candidate gate is open; the "
                      "candidate-research lane is at AUTOMATION READINESS, not "
                      "another candidate")
        else:
            rec_kind = REC_NEXT_CANDIDATE
            detected_gate = "clean_synced_idle"
            command = NEXT_CANDIDATE_TOKEN
            reason = ("repo is clean and synced, the rejected ledger is consistent, "
                      "and no candidate gate is open; recommend selecting the next "
                      "candidate family to research (automation lane continues)")

    decision: dict[str, Any] = {
        "schema_version": GDC_SCHEMA_VERSION, "mode": GDC_MODE, "lane": GDC_LANE,
        "is_pure_coordinator_only": True,
        "does_not_replace_autopilot_or_orchestrator": True,
        "integrates_with": list(INTEGRATES_WITH),
        "detected_gate": detected_gate,
        "recommendation_kind": rec_kind,
        "next_safe_command": command,
        "reason": reason,
        "requires_human_approval": True,
        "is_recommendation_only": True,
        "executes_nothing": True,
        "automation_lane_continues": True,
        "next_research_recommended": rec_kind == REC_NEXT_CANDIDATE,
        "open_candidates": opens,
        "closed_excluded_candidates": closed,
        "ledger_status": ls,
        "repo_status": {
            "clean": bool(repo.get("clean", not uncommitted)),
            "ahead": ahead, "behind": int(repo.get("behind", 0) or 0),
            "uncommitted_changes": uncommitted,
            "approved_unit_pending_commit": approved_unit,
            "in_sync": ahead == 0 and int(repo.get("behind", 0) or 0) == 0
            and not uncommitted,
        },
        "human_review_required": True,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        decision[flag] = False
    decision["scope_locks"] = {
        "no_auto_commit": True, "no_auto_push": True, "no_auto_advance": True,
        "no_auto_reject": True, "no_replay": True, "no_detector_run": True,
        "no_labels": True, "no_relabel": True, "no_optimization": True,
        "no_robustness": True, "no_portfolio_compute": True, "no_data_fetch": True,
        "no_write": True, "no_execute": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_gate_skip": True,
        "no_replace_autopilot_or_orchestrator": True,
        "no_downstream_gate_unlock": True, "no_profitability_claim": True,
        "no_crossing_into_forbidden_gate": True,
    }
    return decision


def summarize_for_morning_report(decision: dict) -> dict[str, Any]:
    """PURE decision-ready morning-report block. Read-only; executes nothing."""
    d = decision or {}
    closed = d.get("closed_excluded_candidates") or []
    return {
        "section": "gate_decision_coordinator",
        "decision_ready": True,
        "detected_gate": d.get("detected_gate"),
        "recommendation_kind": d.get("recommendation_kind"),
        "next_safe_command": d.get("next_safe_command"),
        "paste_this": d.get("next_safe_command"),
        "reason": d.get("reason"),
        "requires_human_approval": True,
        "open_gates": [c["candidate"] for c in (d.get("open_candidates") or [])],
        "closed_excluded": [
            {"candidate": c["candidate"], "status": c["status"],
             "shipped": c["shipped"],
             "excluded_from_reproposal": c["excluded_from_reproposal"]}
            for c in closed],
        "ledger_consistent": (d.get("ledger_status") or {}).get("consistent"),
        "automation_lane_continues": d.get("automation_lane_continues"),
        "next_research_recommended": d.get("next_research_recommended"),
        "executes_nothing": True,
    }


def get_gate_decision_coordinator_label() -> str:
    return (
        "SPARTA Gate Decision Coordinator v1 (THIN, READ-ONLY, RESEARCH ONLY). "
        "Sits on top of the Safe Research Autopilot / Research Expansion Plan / "
        "Integration spec / Morning Report to clarify the current gate and "
        "recommend the next SAFE human-approval command (commit / push / ledger "
        "bump / gate decision / next candidate). Does NOT replace the autopilot or "
        "orchestrator. RECOMMENDS ONLY -- the human still approves every commit, "
        "push, advance/reject, and any trading-adjacent action. NEVER recommends "
        "any paper/live/broker/order action. EXECUTES NOTHING.")


def validate_coordinator_decision(decision: dict) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the decision is research-only,
    coordinator-only, emits a command from the allowlist that contains NO
    forbidden (paper/live/broker/order/auto-commit/auto-push) substring, preserves
    human approval, never claims to replace the autopilot/orchestrator, and pins
    every capability flag False."""
    failures: list = []
    if decision.get("mode") != GDC_MODE:
        failures.append("mode_not_research_only")
    if decision.get("is_pure_coordinator_only") is not True:
        failures.append("not_pure_coordinator_only")
    if decision.get("does_not_replace_autopilot_or_orchestrator") is not True:
        failures.append("must_not_replace_autopilot_or_orchestrator")

    kind = decision.get("recommendation_kind")
    if kind not in ALL_RECOMMENDATION_KINDS:
        failures.append("recommendation_kind_not_in_allowlist")

    cmd = decision.get("next_safe_command")
    if not isinstance(cmd, str) or not cmd:
        failures.append("missing_command")
    else:
        low = cmd.lower()
        for bad in FORBIDDEN_COMMAND_SUBSTRINGS:
            if bad in low:
                failures.append("command_contains_forbidden_%s" % bad)

    # human approval preserved
    if decision.get("requires_human_approval") is not True:
        failures.append("human_approval_not_required")
    if decision.get("executes_nothing") is not True:
        failures.append("executes_nothing_not_set")
    if decision.get("automation_lane_continues") is not True:
        failures.append("automation_lane_not_continued")

    # next-candidate recommendation must be the canonical proposal token only
    if kind == REC_NEXT_CANDIDATE and cmd != NEXT_CANDIDATE_TOKEN:
        failures.append("next_candidate_command_unexpected")
    # automation-readiness recommendation must be the lane directive token only
    if kind == REC_AUTOMATION_READINESS and cmd != AUTOMATION_READINESS_TOKEN:
        failures.append("automation_readiness_command_unexpected")

    locks = decision.get("scope_locks") or {}
    for key in ("no_auto_commit", "no_auto_push", "no_auto_advance",
                "no_auto_reject", "no_replay", "no_detector_run", "no_labels",
                "no_optimization", "no_broker", "no_order_logic",
                "no_paper_trading", "no_live_trading", "no_gate_skip",
                "no_replace_autopilot_or_orchestrator"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if decision.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

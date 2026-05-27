"""Generate pending decisions from candidate state + latest audit.

A pending decision is a structured dict (persisted as JSON) describing an
action the operator may approve. The engine never executes — only proposes.
"""

from __future__ import annotations

import datetime as _dt
from typing import Any

from .l1_checker import L1_FULL, L1_MISSING, L1_PARTIAL
from .state import (
    CandidateState, K9_FAIL, K9_NOT_EVALUATED, K9_PASS, PHASE_DUPLICATE_CHAIN,
    PHASE_P11_LIFECYCLE, PHASE_P3_BUILD, PHASE_P4_SMOKE, PHASE_P6_5_COST_STRESS,
    PHASE_P6_IS, PHASE_P7_DECISION, PHASE_SEAL,
)


# Decision action ids (kept stable; UI references these).
ACCEPT_AND_WRITE_L1_SUPPLEMENT = "ACCEPT_AND_WRITE_L1_CARRY_SUPPLEMENT"
ACCEPT_AND_PARK = "ACCEPT_AND_PARK"
AUTHORIZE_P6_5_COST_STRESS = "AUTHORIZE_P6_5_COST_STRESS"
AUTHORIZE_P7_DECISION_MEMO = "AUTHORIZE_P7_DECISION_MEMO"
AUTHORIZE_P10_OOS_GATE = "AUTHORIZE_P10_OOS_GATE"
AUTHORIZE_P11_PARK_MEMO = "AUTHORIZE_P11_PARK_MEMO"
WRITE_L1_CARRY_SUPPLEMENT = "WRITE_L1_CARRY_SUPPLEMENT"
DISCARD_DUPLICATE_UNTRACKED_REPORT = "DISCARD_DUPLICATE_UNTRACKED_REPORT"
HALT_FOR_RECONCILIATION = "HALT_FOR_RECONCILIATION"
IGNORE_DUPLICATE_CHAIN = "IGNORE_DUPLICATE_CHAIN"
PARK_CANDIDATE = "PARK_CANDIDATE"

# Priority levels for the UI to sort by.
PRIORITY_HIGH = "HIGH"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_LOW = "LOW"


def _decision(
    candidate_id: str, action: str, priority: str, reason: str, **extras: Any
) -> dict[str, Any]:
    out = {
        "candidate_id": candidate_id,
        "action": action,
        "priority": priority,
        "reason": reason,
        "created_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="microseconds"),
        "status": "pending_operator_approval",
    }
    out.update(extras)
    return out


def evaluate(
    state: CandidateState,
    latest_audit: dict[str, Any] | None = None,
    repo_snapshot: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Return zero or more pending decisions for this candidate.

    Inputs:
        state          -- current CandidateState
        latest_audit   -- output of gate_evaluator + l1_checker for the latest
                          sealed report on the canonical chain (optional)
        repo_snapshot  -- output of git_sentinel.scan().to_dict() (optional)
    """
    out: list[dict[str, Any]] = []
    audit = latest_audit or {}
    snap = repo_snapshot or {}

    # ---- L1 carry-forward gap detection ----
    if state.rec1_t1_carry_status in (L1_PARTIAL, L1_MISSING):
        priority = PRIORITY_HIGH if state.current_phase in (
            PHASE_P3_BUILD, PHASE_P4_SMOKE, PHASE_P6_IS, PHASE_P6_5_COST_STRESS
        ) else PRIORITY_MEDIUM
        out.append(_decision(
            state.candidate_id,
            WRITE_L1_CARRY_SUPPLEMENT,
            priority,
            (
                f"Current phase {state.current_phase} carries only "
                f"{state.rec1_t1_carry_status}; REC1_T1 byte-equivalent must be "
                "attached to the chain step via a sealed supplement before the "
                "next phase is authored."
            ),
            current_phase=state.current_phase,
            l1_status=state.rec1_t1_carry_status,
            approval_level_required=2,
        ))

    # ---- Phase-specific decisions ----
    if state.current_phase == PHASE_SEAL:
        out.append(_decision(
            state.candidate_id,
            "AUTHORIZE_P1_PLAN_LOCK",
            PRIORITY_MEDIUM,
            "SEAL accepted; next lifecycle step is P1 plan-lock authoring.",
            approval_level_required=2,
        ))

    elif state.current_phase == PHASE_P3_BUILD:
        out.append(_decision(
            state.candidate_id,
            "AUTHORIZE_P4_SYNTHETIC_SMOKE",
            PRIORITY_MEDIUM,
            "P3 BUILD complete; P4 synthetic smoke runs 29 unit/scaffold tests on synthetic fixture only.",
            approval_level_required=3,  # P4 executes tests
        ))

    elif state.current_phase == PHASE_P4_SMOKE:
        out.append(_decision(
            state.candidate_id,
            AUTHORIZE_P6_5_COST_STRESS,
            PRIORITY_LOW,
            "P4 smoke passed; P6 IS diagnostic is the next executable phase (real sealed CSV).",
            approval_level_required=3,
        ))

    elif state.current_phase == PHASE_P6_IS:
        if state.k9_status == K9_FAIL:
            out.append(_decision(
                state.candidate_id,
                ACCEPT_AND_PARK,
                PRIORITY_HIGH,
                (
                    f"P6 IS K9 FAILED ({state.closed_trades_observed} < "
                    f"{state.k9_threshold}). Park is the analytically clean choice; "
                    "OOS K9 will fail more severely."
                ),
                approval_level_required=2,
            ))
            out.append(_decision(
                state.candidate_id,
                AUTHORIZE_P11_PARK_MEMO,
                PRIORITY_HIGH,
                "Author sealed P11 PARK memo on IS K9 failure + REC1 binding.",
                approval_level_required=2,
            ))
        elif state.k9_status == K9_PASS:
            # Check DR10 elevation if available
            turnover = audit.get("annual_turnover")
            if isinstance(turnover, (int, float)) and turnover > 0.50:
                out.append(_decision(
                    state.candidate_id,
                    AUTHORIZE_P6_5_COST_STRESS,
                    PRIORITY_HIGH,
                    (
                        f"P6 K9 PASSED ({state.closed_trades_observed}) but "
                        f"annual_turnover={turnover:.2f} elevates DR10. "
                        "P6.5 cost-stress required to formally evaluate."
                    ),
                    approval_level_required=3,
                ))
            else:
                out.append(_decision(
                    state.candidate_id,
                    AUTHORIZE_P6_5_COST_STRESS,
                    PRIORITY_MEDIUM,
                    f"P6 K9 PASSED ({state.closed_trades_observed}); P6.5 cost-stress is the next gate.",
                    approval_level_required=3,
                ))
            # Implied OOS K9 check from observed rate
            trades_per_year = audit.get("trades_per_year_observed")
            if isinstance(trades_per_year, (int, float)) and trades_per_year * 2.0 < 100:
                out.append(_decision(
                    state.candidate_id,
                    ACCEPT_AND_PARK,
                    PRIORITY_HIGH,
                    (
                        f"Observed IS rate {trades_per_year:.2f}/y implies OOS K9 "
                        f"= {trades_per_year * 2.0:.1f} trades < 100 floor. "
                        "Per REC1_T1, OOS K9 expected to FIRE. Early PARK avoids "
                        "P10 OOS window consumption for a predetermined verdict."
                    ),
                    approval_level_required=2,
                ))

    elif state.current_phase == PHASE_P6_5_COST_STRESS:
        verdict = state.latest_verdict or ""
        if "REJECT_FAST" in verdict:
            out.append(_decision(
                state.candidate_id,
                AUTHORIZE_P11_PARK_MEMO,
                PRIORITY_HIGH,
                f"P6.5 verdict {verdict}. Terminal-class; P11 PARK on REJECT_FAST.",
                approval_level_required=2,
            ))
        else:
            out.append(_decision(
                state.candidate_id,
                AUTHORIZE_P7_DECISION_MEMO,
                PRIORITY_MEDIUM,
                "P6.5 complete; P7 decision memo formalizes the next-phase choice.",
                approval_level_required=2,
            ))

    elif state.current_phase == PHASE_P7_DECISION:
        out.append(_decision(
            state.candidate_id,
            AUTHORIZE_P10_OOS_GATE,
            PRIORITY_LOW,
            "P7 decision memo complete; P10 OOS gate is the next executable phase.",
            approval_level_required=3,
        ))

    elif state.current_phase == PHASE_P11_LIFECYCLE:
        # Already parked; nothing to do except observation
        pass

    # ---- Repo-state housekeeping ----
    # Protected-file drift: distinguish KNOWN (operator-accepted baseline) from NEW.
    # KNOWN drift -> single LOW informational decision, NOT per-candidate HIGH halt.
    # NEW drift   -> HIGH halt per the original policy (true blocker).
    drift_details = snap.get("protected_drift_details") or []
    if drift_details:
        new_drift_paths = [
            d["path"] for d in drift_details
            if d.get("classification") == "NEW_PROTECTED_DRIFT"
        ]
        known_drift_paths = [
            d["path"] for d in drift_details
            if d.get("classification") == "KNOWN_PRE_EXISTING_DRIFT"
        ]
        if new_drift_paths:
            out.append(_decision(
                state.candidate_id,
                HALT_FOR_RECONCILIATION,
                PRIORITY_HIGH,
                (
                    "NEW protected-file drift detected (no accepted baseline OR "
                    f"hash changed from baseline): {new_drift_paths}. "
                    "Manual operator intervention required. Use "
                    "`--accept-protected-drift <path> --reason ...` to record a "
                    "new baseline if the change is intentional."
                ),
                approval_level_required=0,
                blocking=True,
                new_drift_paths=new_drift_paths,
            ))
        elif known_drift_paths:
            out.append(_decision(
                state.candidate_id,
                "ACKNOWLEDGE_KNOWN_PROTECTED_DRIFT",
                PRIORITY_LOW,
                (
                    f"Known pre-existing drift in protected file(s): {known_drift_paths}. "
                    "Working-tree hash matches an operator-accepted baseline. "
                    "Hard guards still refuse to stage/commit these files."
                ),
                approval_level_required=0,
                blocking=False,
                known_drift_paths=known_drift_paths,
            ))
    elif snap.get("dirty_protected_files"):
        # Fallback for older callers that don't pass protected_drift_details
        out.append(_decision(
            state.candidate_id,
            HALT_FOR_RECONCILIATION,
            PRIORITY_HIGH,
            (
                "Protected file(s) modified (no drift baseline data available): "
                f"{snap['dirty_protected_files']}. Manual operator intervention required."
            ),
            approval_level_required=0,
            blocking=True,
        ))

    if snap.get("untracked_tmp_helpers"):
        for h in snap["untracked_tmp_helpers"]:
            # Only propose deletion for `.tmp_` author scripts we created (not parallel session leftovers)
            if h.startswith(".tmp_"):
                out.append(_decision(
                    state.candidate_id,
                    "DELETE_UNTRACKED_TMP_HELPER",
                    PRIORITY_LOW,
                    f"Stale author helper script in working tree: {h}",
                    path=h,
                    approval_level_required=1,
                ))

    if snap.get("duplicate_chain_files"):
        out.append(_decision(
            state.candidate_id,
            IGNORE_DUPLICATE_CHAIN,
            PRIORITY_LOW,
            (
                "Duplicate-chain (SEAL-B-style) artifacts detected: "
                f"{snap['duplicate_chain_files'][:3]}{'...' if len(snap['duplicate_chain_files']) > 3 else ''}. "
                "Standing pattern is to acknowledge but not anchor."
            ),
            files=snap["duplicate_chain_files"],
            approval_level_required=0,
        ))

    return out

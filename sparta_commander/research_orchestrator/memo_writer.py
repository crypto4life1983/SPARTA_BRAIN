"""Draft sealed memo bodies (JSON + MD pairs).

This module ONLY drafts in-memory bodies + computes their canonical seal.
It does NOT write files, stage, or commit — that is the safe_executor's job
under LEVEL_2 approval.

Drafted memo types:
    - L1 carry-forward supplement
    - P11 PARK memo
    - Observation memo
    - Duplicate-chain disambiguation memo
    - Comparison memo
"""

from __future__ import annotations

import datetime as _dt
from typing import Any

from .seal_verifier import canonical_recompute


REC1_T1_BINDING_TEXT = (
    "REC1_T1 (binding): Under the L1 epistemic-discount framework, the candidate's "
    "trade-rate estimate is classified as HEURISTIC_ESTIMATE_L1_DISCOUNT_APPLIES "
    "pending operator-supplied specific citation or hand-count validation. At the "
    "2x conservative discount, OOS K9 FIRES; expected OOS verdict is "
    "OOS_INSUFFICIENT_SAMPLE or PARKED_SAFE_BUT_OOS_INDETERMINATE_K9_FIRED. At "
    "the 3x conservative discount, BOTH IS K9 and OOS K9 fire. The chain shall "
    "NOT relax K9 at any phase. Pursuing the candidate without independent source "
    "validation accepts the structural likelihood of OOS PARK outcomes."
)


HARD_BOUNDARIES_SUPPLEMENT_TEMPLATE = {
    "supplement_only_no_phase_rerun": True,
    "supplement_only_no_phase_authorization": True,
    "supplement_only_no_build": True,
    "supplement_only_no_tests": True,
    "supplement_only_no_diagnostics": True,
    "supplement_only_no_signal_computation": True,
    "supplement_only_no_csv_read": True,
    "supplement_only_no_data_fetch": True,
    "supplement_only_no_databento_call": True,
    "supplement_only_no_databento_api_key_access": True,
    "supplement_only_no_network_call": True,
    "supplement_only_no_strategy_logic_modification": True,
    "no_modification_of_any_sealed_artifact": True,
    "no_modification_of_parallel_seal_b_chain": True,
    "no_lessons_md_touched": True,
    "no_k9_relaxation": True,
    "no_rec1_demotion": True,
    "no_rec1_t1_demotion": True,
    "no_dr_redefinition": True,
    "no_threshold_loosening": True,
    "no_phase_pre_approved_by_this_supplement": True,
    "no_staging": True,
    "no_commit": True,
}


POSTURE_INVARIANTS_TEMPLATE = {
    "trading_status": "PAUSED",
    "live_status": "BLOCKED_AT_6_GATES",
    "frc_status": "NEVER_GRANTED",
    "advisory_label_permanent": "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE",
    "profitability_claim_made": False,
    "live_readiness_claim_made": False,
    "oos_confirmation_claim_made": False,
    "k9_threshold_relaxed": False,
    "rec1_binding_demoted": False,
    "rec1_t1_binding_demoted": False,
    "permanent_live_block": True,
}


def _now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="microseconds")


def _seal_and_finalize(body: dict[str, Any]) -> dict[str, Any]:
    """Compute LESSON_HUNTER_004 seal and attach to body."""
    body_check = {k: v for k, v in body.items() if k not in ("report_seal_sha256", "seal_method")}
    body["report_seal_sha256"] = canonical_recompute(body_check)
    body["seal_method"] = (
        "LESSON_HUNTER_004 canonical roundtrip "
        "(json.dumps sort_keys=True separators=',:' ensure_ascii=False default=str "
        "EXCLUDING report_seal_sha256 + seal_method)"
    )
    return body


def draft_l1_carry_supplement(
    candidate_id: str,
    phase: str,
    chain_step_commit: str,
    cross_references: dict[str, dict[str, str]],
    rec1_t1_text: str = REC1_T1_BINDING_TEXT,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Draft a sealed L1 carry-forward supplement for one chain step.

    Returns a dict body with `report_seal_sha256` attached.
    Caller is responsible for writing to disk (via safe_executor LEVEL_2).
    """
    body: dict[str, Any] = {
        "schema_id": f"sparta.research_orchestrator.{candidate_id}_{phase.lower()}_l1_carry_supplement_sealed.v1",
        "candidate_record_id": candidate_id,
        "phase": f"{phase}_L1_CARRY_FORWARD_SUPPLEMENT",
        "lifecycle_state": f"{phase}_L1_CARRY_FORWARD_SUPPLEMENT_SEALED",
        "title": f"{candidate_id} {phase} L1-carry-forward supplement",
        "report_kind": (
            f"Sealed supplement attaching REC1_T1_BINDING_K9_DISCLOSURE to the "
            f"{phase} chain step at commit {chain_step_commit}. Drafted by research "
            "orchestrator; awaiting LEVEL_2 operator approval before commit."
        ),
        "authored_at_utc": _now_utc(),
        "binding": True,
        "labels": [
            "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE",
            "SUPPLEMENT_ONLY",
            f"REC1_T1_BINDING_K9_DISCLOSURE_ATTACHED_TO_{phase}_CHAIN_STEP",
            "BYTE_EQUIVALENT_CARRY_MANDATED",
        ],
        "attachment_chain_step": chain_step_commit,
        "rec1_t1_binding_text_verbatim": rec1_t1_text,
        "cross_references_binding": cross_references,
        "posture_invariants": POSTURE_INVARIANTS_TEMPLATE,
        "hard_boundaries_held_this_supplement_turn": HARD_BOUNDARIES_SUPPLEMENT_TEMPLATE,
        "next_phase_requirements": {
            "no_phase_pre_approved_by_this_supplement": True,
            "all_subsequent_phases_require_separate_authorization": True,
            "all_subsequent_phases_must_carry_rec1_t1_byte_equivalent": True,
        },
    }
    if extras:
        body.update(extras)
    return _seal_and_finalize(body)


def draft_park_memo(
    candidate_id: str,
    lifecycle_decision: str,
    reasons: list[str],
    chain_anchors: dict[str, Any],
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Draft a sealed P11 PARK memo."""
    body: dict[str, Any] = {
        "schema_id": f"sparta.research_orchestrator.{candidate_id}_p11_lifecycle_park_decision_sealed.v1",
        "candidate_record_id": candidate_id,
        "phase": "P11_LIFECYCLE_DECISION",
        "lifecycle_state": "P11_LIFECYCLE_PARK_DECISION_SEALED",
        "title": f"{candidate_id} P11 lifecycle PARK decision",
        "report_kind": (
            "Sealed P11 PARK decision memo drafted by research orchestrator; "
            "awaiting LEVEL_2 operator approval before commit."
        ),
        "authored_at_utc": _now_utc(),
        "binding": True,
        "labels": [
            "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE",
            "P11_LIFECYCLE_PARK_DECISION_SEALED",
            lifecycle_decision,
            "NO_PROFITABILITY_CLAIM",
            "NO_LIVE_READINESS_CLAIM",
            "NO_OOS_CONFIRMATION_CLAIM",
            "K9_THRESHOLD_INVIOLATE",
        ],
        "lifecycle_decision": lifecycle_decision,
        "decision_reasons": reasons,
        "chain_anchors": chain_anchors,
        "posture_invariants": POSTURE_INVARIANTS_TEMPLATE,
        "hard_boundaries_held_this_park_turn": {
            **HARD_BOUNDARIES_SUPPLEMENT_TEMPLATE,
            "no_revival_authorized_by_this_park_memo": True,
            "park_is_terminal_for_this_candidate_record_id": True,
        },
    }
    if extras:
        body.update(extras)
    return _seal_and_finalize(body)


def draft_observation_memo(
    title: str,
    subject: str,
    findings: list[str],
    references: dict[str, str],
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Draft a sealed observation memo (lightweight, no binding decision)."""
    body: dict[str, Any] = {
        "schema_id": "sparta.research_orchestrator.observation_memo_sealed.v1",
        "phase": "OBSERVATION",
        "lifecycle_state": "OBSERVATION_MEMO_SEALED",
        "title": title,
        "subject": subject,
        "authored_at_utc": _now_utc(),
        "binding": False,  # observations are advisory
        "findings": findings,
        "references": references,
        "labels": ["DIAGNOSTIC_ONLY_NOT_LIVE_GRADE", "OBSERVATION_ONLY", "NOT_BINDING"],
        "posture_invariants": POSTURE_INVARIANTS_TEMPLATE,
    }
    if extras:
        body.update(extras)
    return _seal_and_finalize(body)


def draft_duplicate_chain_disambiguation(
    candidate_id: str,
    canonical_chain: list[str],
    duplicate_chain: list[str],
    recommendation: str,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Draft a sealed memo disambiguating canonical vs duplicate chain."""
    body: dict[str, Any] = {
        "schema_id": f"sparta.research_orchestrator.{candidate_id}_duplicate_chain_disambiguation_sealed.v1",
        "candidate_record_id": candidate_id,
        "phase": "OBSERVATION",
        "lifecycle_state": "DUPLICATE_CHAIN_DISAMBIGUATION_SEALED",
        "title": f"{candidate_id} duplicate-chain disambiguation",
        "authored_at_utc": _now_utc(),
        "binding": True,
        "canonical_chain": canonical_chain,
        "duplicate_chain_acknowledged_not_anchored": duplicate_chain,
        "recommendation": recommendation,
        "labels": [
            "DIAGNOSTIC_ONLY_NOT_LIVE_GRADE",
            "CANONICAL_CHAIN_IDENTIFIED",
            "DUPLICATE_CHAIN_ACKNOWLEDGED_NOT_ANCHORED",
        ],
        "posture_invariants": POSTURE_INVARIANTS_TEMPLATE,
    }
    if extras:
        body.update(extras)
    return _seal_and_finalize(body)


def draft_comparison_memo(
    title: str,
    candidate_a: dict[str, Any],
    candidate_b: dict[str, Any],
    comparison_axes: list[str],
    recommendation: str,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Draft a sealed comparison memo between two candidates."""
    body: dict[str, Any] = {
        "schema_id": "sparta.research_orchestrator.comparison_memo_sealed.v1",
        "phase": "OBSERVATION",
        "lifecycle_state": "COMPARISON_MEMO_SEALED",
        "title": title,
        "authored_at_utc": _now_utc(),
        "binding": False,
        "candidate_a": candidate_a,
        "candidate_b": candidate_b,
        "comparison_axes": comparison_axes,
        "recommendation": recommendation,
        "labels": ["DIAGNOSTIC_ONLY_NOT_LIVE_GRADE", "COMPARISON_MEMO"],
        "posture_invariants": POSTURE_INVARIANTS_TEMPLATE,
    }
    if extras:
        body.update(extras)
    return _seal_and_finalize(body)


def render_markdown_companion(body: dict[str, Any]) -> str:
    """Render a minimal markdown companion for a sealed body.

    Caller-driven richness; this is the baseline that always works.
    """
    lines = [
        f"# {body.get('title', body.get('candidate_record_id', 'Sealed Memo'))}",
        "",
        f"- **Seal SHA-256:** `{body.get('report_seal_sha256', '<unsealed>')}`",
        f"- **Authored at UTC:** {body.get('authored_at_utc', '?')}",
        f"- **Phase:** `{body.get('phase', '?')}` · **Lifecycle:** `{body.get('lifecycle_state', '?')}`",
        f"- **Binding:** {body.get('binding', False)}",
        "",
    ]
    if "lifecycle_decision" in body:
        lines += [f"## Lifecycle decision", "", f"**`{body['lifecycle_decision']}`**", ""]
    if "decision_reasons" in body and isinstance(body["decision_reasons"], list):
        lines += ["## Decision reasons", ""]
        for r in body["decision_reasons"]:
            lines.append(f"- {r}")
        lines.append("")
    if "rec1_t1_binding_text_verbatim" in body:
        lines += ["## REC1_T1 (binding)", "", f"> *{body['rec1_t1_binding_text_verbatim']}*", ""]
    if "cross_references_binding" in body and isinstance(body["cross_references_binding"], dict):
        lines += ["## Cross-references", "", "| Artifact | Commit | Seal |", "|---|---|---|"]
        for name, ref in body["cross_references_binding"].items():
            commit = ref.get("commit", "?") if isinstance(ref, dict) else "?"
            seal = ref.get("seal_sha256", "?") if isinstance(ref, dict) else "?"
            lines.append(f"| {name} | `{commit}` | `{seal[:16]}…` |")
        lines.append("")
    if "posture_invariants" in body:
        pi = body["posture_invariants"]
        lines += ["## Posture invariants", "",
                  f"- Trading **{pi.get('trading_status', '?')}** · Live **{pi.get('live_status', '?')}** · FRC **{pi.get('frc_status', '?')}**",
                  "- No profitability / live-readiness / OOS-confirmation claims",
                  "- K9 not relaxed · REC1 not demoted · REC1_T1 not demoted",
                  ""]
    return "\n".join(lines) + "\n"

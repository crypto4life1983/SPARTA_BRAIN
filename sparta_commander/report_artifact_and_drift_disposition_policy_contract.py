"""SPARTA Report Artifact & Local Drift Disposition Policy Contract (READ-ONLY).

A PURE, stdlib-only, read-only POLICY module produced after the sealed Blocks 175->189
resume-policy research arc. It decides and documents -- WITHOUT performing -- how to
handle:

  1. the three untracked report directories the pushed contracts cite as evidence
     (``reports/crypto_d1_resume_policy_sim/``,
     ``reports/crypto_d1_rc1_out_of_sample_replay/``,
     ``reports/crypto_d1_rc2_cross_policy_replay/``); and
  2. the nine long-lived LOCAL DRIFT files that must never ride along in feature commits.

The core problem this policy fixes: the pushed research contracts reference report
artifacts that exist ONLY on this machine. A disk failure would erase the evidence the
whole arc cites. The recommended disposition is therefore to COMMIT each report directory
AS IMMUTABLE EVIDENCE -- but ONLY via a SEPARATE, future, explicitly human-approved
evidence commit, never bundled with code, and never performed by this contract.

The drift files are CLASSIFIED (from a read-only investigation of their diffs) but NOT
changed, staged, reverted, or cleaned: every classification carries a recommended handling
that defers any action to a separate future human decision.

This contract RUNS NOTHING and WRITES NOTHING: no git commands, no subprocess, no data
fetch, no replay, no simulation, no backtest, no broker/exchange, no network, no
credentials, no file modification. Its only I/O is a read-only existence check of the
expected report files. It UNLOCKS no gate and changes no trading logic.

Public API:
  - DISPOSITION_SCHEMA_VERSION / DISPOSITION_LABEL / DISPOSITION_MODE
  - VERDICT_POLICY_READY / VERDICT_POLICY_BLOCKED / NEXT_REQUIRED_ACTION
  - DISPOSITION_COMMIT_AS_EVIDENCE / DISPOSITION_KEEP_LOCAL_ONLY
  - DISPOSITION_ARCHIVE / DISPOSITION_GITIGNORE / ALLOWED_DISPOSITIONS
  - REPORT_DIR_POLICIES / DRIFT_FILE_CLASSIFICATIONS / EVIDENCE_COMMIT_PATH
  - get_disposition_policy_label()
  - report_dir_policies() / drift_file_classifications() / evidence_commit_path()
  - build_disposition_policy(repo_root)
  - validate_disposition_policy(policy)
  - render_disposition_policy_markdown(policy)
"""

from __future__ import annotations

import copy
import os
from typing import Any

DISPOSITION_SCHEMA_VERSION = (
    "report_artifact_and_drift_disposition_policy_contract.v1"
)
DISPOSITION_LABEL = (
    "SPARTA Report Artifact & Local Drift Disposition Policy (READ-ONLY)"
)
DISPOSITION_MODE = "RESEARCH_ONLY"

VERDICT_POLICY_READY = "DISPOSITION_POLICY_READY"
VERDICT_POLICY_BLOCKED = "DISPOSITION_POLICY_BLOCKED"

# After this policy is recorded, the only next step is a SEPARATE explicit human approval
# of the evidence commit (and, separately, of any drift handling). Nothing here performs
# or authorizes either.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_EVIDENCE_COMMIT_OR_NEW_DIRECTIVE"

DISPOSITION_COMMIT_AS_EVIDENCE = "COMMIT_AS_IMMUTABLE_EVIDENCE_VIA_SEPARATE_APPROVAL"
DISPOSITION_KEEP_LOCAL_ONLY = "KEEP_LOCAL_ONLY"
DISPOSITION_ARCHIVE = "ARCHIVE_OUTSIDE_REPO"
DISPOSITION_GITIGNORE = "ADD_TO_GITIGNORE"
ALLOWED_DISPOSITIONS: tuple[str, ...] = (
    DISPOSITION_COMMIT_AS_EVIDENCE,
    DISPOSITION_KEEP_LOCAL_ONLY,
    DISPOSITION_ARCHIVE,
    DISPOSITION_GITIGNORE,
)

# --- 1: report directory policies -------------------------------------------
# Every pushed research contract from the 175->189 arc cites these artifacts; they are
# the evidence chain. Recommended disposition: commit as immutable evidence, each via its
# own separate, explicitly human-approved commit -- never bundled with code commits, and
# never modified after commit.
REPORT_DIR_POLICIES: list[dict[str, Any]] = [
    {
        "path": "reports/crypto_d1_resume_policy_sim",
        "expected_files": [
            "resume_policy_sim_log.jsonl",
            "resume_policy_sim_report.json",
            "resume_policy_sim_report.md",
        ],
        "cited_by": "Blocks 176-179 (resume-policy simulation evidence)",
        "recommended_disposition": DISPOSITION_COMMIT_AS_EVIDENCE,
        "rationale": (
            "The Block 177/178 reviews and every downstream decision cite this report; "
            "it exists only on this machine. Committing it preserves the evidence chain "
            "the pushed contracts depend on."
        ),
    },
    {
        "path": "reports/crypto_d1_rc1_out_of_sample_replay",
        "expected_files": [
            "rc1_oos_replay_log.jsonl",
            "rc1_oos_replay_report.json",
            "rc1_oos_replay_report.md",
        ],
        "cited_by": "Blocks 182-184 (RC1 out-of-sample evidence)",
        "recommended_disposition": DISPOSITION_COMMIT_AS_EVIDENCE,
        "rationale": (
            "The RC1 degradation finding (mean +27.7% vs +155.4% in-sample) lives only "
            "in this directory; losing it would orphan the Block 182/183 decisions."
        ),
    },
    {
        "path": "reports/crypto_d1_rc2_cross_policy_replay",
        "expected_files": [
            "rc2_cross_policy_replay_log.jsonl",
            "rc2_cross_policy_replay_report.json",
            "rc2_cross_policy_replay_report.md",
        ],
        "cited_by": "Blocks 186-189 (RC2 leadership-flip evidence)",
        "recommended_disposition": DISPOSITION_COMMIT_AS_EVIDENCE,
        "rationale": (
            "The leadership flip (RP6 leads zero OOS categories) is the pivotal finding "
            "of the whole arc and exists only here; it must survive this machine."
        ),
    },
]

# --- 2: drift file classifications ------------------------------------------
# Classified from a read-only diff investigation; NOTHING here changes, stages, reverts,
# or cleans any file. Every handling defers action to a separate future human decision.
_CLASS_HOOK_APPENDS = "auto_pytest_marker_hook_appends"
_CLASS_PRE_EXISTING = "pre_existing_session_start_drift_unreviewed"
_CLASS_CONCURRENT_DEV = "concurrent_local_development_unattributed_to_this_session"

_HANDLE_NEVER_BUNDLE = (
    "never stage with feature commits; separate future human decision on "
    "commit-or-revert"
)
_HANDLE_HUMAN_REVIEW = (
    "requires separate human review of the diff before any commit; protected by the "
    "standing do-not-touch list"
)
_HANDLE_ATTRIBUTE_FIRST = (
    "coherent, commented feature edits from a concurrent local session; attribute the "
    "source session, then review and commit (or revert) via that session's own path -- "
    "never bundle here"
)

DRIFT_FILE_CLASSIFICATIONS: list[dict[str, Any]] = [
    {
        "path": "brain_memory/projects/trading_bot/decisions.md",
        "classification": _CLASS_HOOK_APPENDS,
        "recommended_handling": _HANDLE_NEVER_BUNDLE,
        "evidence": (
            "the auto-pytest-marker hook appends timestamped markers on every pytest "
            "run; the large diff (~1634 lines) also shows reformatting consistent with "
            "external edits -- review before any commit"
        ),
    },
    {
        "path": "brain_memory/projects/trading_bot/lessons.md",
        "classification": _CLASS_HOOK_APPENDS,
        "recommended_handling": _HANDLE_NEVER_BUNDLE,
        "evidence": "small pure-append diff (+8 lines) matching the hook's marker format",
    },
    {
        "path": "brain_memory/projects/trading_bot/next_actions.md",
        "classification": _CLASS_HOOK_APPENDS,
        "recommended_handling": _HANDLE_NEVER_BUNDLE,
        "evidence": "small pure-append diff (+4 lines) matching the hook's marker format",
    },
    {
        "path": "app.py",
        "classification": _CLASS_PRE_EXISTING,
        "recommended_handling": _HANDLE_HUMAN_REVIEW,
        "evidence": "modified before this session began (~75 changed lines); origin unknown",
    },
    {
        "path": "templates/jarvis.html",
        "classification": _CLASS_PRE_EXISTING,
        "recommended_handling": _HANDLE_HUMAN_REVIEW,
        "evidence": "modified before this session began (~223 changed lines); origin unknown",
    },
    {
        "path": "spartacus/animation_engine.py",
        "classification": _CLASS_PRE_EXISTING,
        "recommended_handling": _HANDLE_HUMAN_REVIEW,
        "evidence": "modified before this session began (~58 changed lines); origin unknown",
    },
    {
        "path": "jarvis_conversation_safety.py",
        "classification": _CLASS_CONCURRENT_DEV,
        "recommended_handling": _HANDLE_ATTRIBUTE_FIRST,
        "evidence": (
            "appeared mid-session: +12 lines adding commented, fail-closed-preserving "
            "safe-info regex patterns for 'update' briefing phrasings -- deliberate "
            "feature work, not corruption"
        ),
    },
    {
        "path": "jarvis_knowledge_map.py",
        "classification": _CLASS_CONCURRENT_DEV,
        "recommended_handling": _HANDLE_ATTRIBUTE_FIRST,
        "evidence": (
            "appeared mid-session: commented vocative-stripping ('Jarvis, ...') and "
            "status-word edits with a docstring-consistent style -- deliberate feature "
            "work, not corruption"
        ),
    },
    {
        "path": "tests/test_jarvis_ask_contract.py",
        "classification": _CLASS_CONCURRENT_DEV,
        "recommended_handling": _HANDLE_ATTRIBUTE_FIRST,
        "evidence": (
            "appeared mid-session alongside the two jarvis module edits (~23 changed "
            "lines); matching test updates for the same feature work"
        ),
    },
]

# --- 3: the separate evidence-commit path (inert documentation) --------------
# Defining this path documents it; it does NOT authorize it and this contract never
# performs it.
EVIDENCE_COMMIT_PATH: dict[str, Any] = {
    "is_authorization": False,
    "performed_by_this_contract": False,
    "requires_separate_human_approval": True,
    "rules": [
        "one evidence commit per report directory, or one combined evidence-only commit",
        "evidence commits contain report artifacts ONLY -- never code, never drift files",
        "artifacts are immutable after commit: any future rerun writes NEW files, "
        "never edits committed evidence",
        "drift handling is a separate future path: hook-append files and concurrent-dev "
        "files each get their own human decision, never bundled with evidence or code",
    ],
    "note": (
        "Until a human approves the evidence commit, the report directories stay "
        "local-only and untouched."
    ),
}


def get_disposition_policy_label() -> str:
    """Human label for the recognized disposition policy contract."""
    return DISPOSITION_LABEL


def report_dir_policies() -> list[dict[str, Any]]:
    """Return fresh deep copies of the fixed report-directory policies. Pure."""
    return [copy.deepcopy(p) for p in REPORT_DIR_POLICIES]


def drift_file_classifications() -> list[dict[str, Any]]:
    """Return fresh copies of the fixed drift-file classifications. Pure."""
    return [dict(c) for c in DRIFT_FILE_CLASSIFICATIONS]


def evidence_commit_path() -> dict[str, Any]:
    """Return a fresh copy of the inert evidence-commit path documentation. Pure;
    authorizes nothing and performs nothing."""
    path = dict(EVIDENCE_COMMIT_PATH)
    path["rules"] = list(EVIDENCE_COMMIT_PATH["rules"])
    return path


def build_disposition_policy(repo_root: str = ".") -> dict[str, Any]:
    """Assemble the disposition policy with a READ-ONLY existence check of the expected
    report artifacts (os.path only -- no git, no subprocess, no modification). Missing
    artifacts become blockers because the policy would then be protecting evidence that
    no longer exists. Writes nothing; changes nothing; unlocks no gate."""
    blockers: list[str] = []
    risk_notes: list[str] = []

    dir_status: list[dict[str, Any]] = []
    for p in REPORT_DIR_POLICIES:
        dir_path = os.path.join(repo_root, p["path"])
        present = os.path.isdir(dir_path)
        missing_files = [
            f for f in p["expected_files"]
            if not os.path.isfile(os.path.join(dir_path, f))
        ]
        dir_status.append({
            "path": p["path"],
            "directory_present": present,
            "missing_files": missing_files,
        })
        if not present:
            blockers.append("report_directory_missing:" + p["path"])
        elif missing_files:
            blockers.append(
                "report_files_missing:" + p["path"] + ":" + ",".join(missing_files)
            )

    risk_notes.append("policy_is_documentation_only_no_file_was_changed")
    risk_notes.append("evidence_commit_requires_separate_explicit_human_approval")
    risk_notes.append("drift_files_classified_not_cleaned_or_staged")
    risk_notes.append(
        "report_artifacts_must_never_be_bundled_into_code_or_feature_commits"
    )
    risk_notes.append("cleanup_if_any_is_a_separate_future_human_decision")

    verdict = VERDICT_POLICY_READY if not blockers else VERDICT_POLICY_BLOCKED
    return {
        "schema_version": DISPOSITION_SCHEMA_VERSION,
        "label": DISPOSITION_LABEL,
        "mode": DISPOSITION_MODE,
        "verdict": verdict,
        "report_dir_policies": report_dir_policies(),
        "report_dir_status": dir_status,
        "drift_file_classifications": drift_file_classifications(),
        "evidence_commit_path": evidence_commit_path(),
        # Headline answers, stated explicitly:
        "future_commit_may_include_report_artifacts": True,
        "report_artifacts_only_via_separate_evidence_commit": True,
        "cleanup_must_be_separate_future_decision": True,
        "any_file_changed_by_this_contract": False,
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        # Capability posture (this policy executes / authorizes / writes nothing):
        "executes": False,
        "writes_files": False,
        "modifies_report_artifacts": False,
        "stages_or_commits_anything": False,
        "runs_replay": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "fetches_data": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "changes_trading_logic": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this policy):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def validate_disposition_policy(policy: Any) -> dict[str, Any]:
    """Validate (read-only) a disposition policy's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(policy, dict):
        return {"valid": False, "errors": ["policy_not_a_dict"]}
    p = policy

    if p.get("verdict") not in (VERDICT_POLICY_READY, VERDICT_POLICY_BLOCKED):
        errors.append("bad_verdict")
    if p.get("schema_version") != DISPOSITION_SCHEMA_VERSION:
        errors.append("bad_schema_version")

    dirs = p.get("report_dir_policies")
    if not isinstance(dirs, list) or len(dirs) != 3:
        errors.append("report_dir_policies_not_three")
        dirs = []
    for d in dirs:
        if not isinstance(d, dict):
            errors.append("dir_policy_not_a_dict")
            continue
        if d.get("recommended_disposition") not in ALLOWED_DISPOSITIONS:
            errors.append("bad_disposition:" + str(d.get("path")))

    drifts = p.get("drift_file_classifications")
    if not isinstance(drifts, list) or len(drifts) != 9:
        errors.append("drift_classifications_not_nine")
        drifts = []
    seen: set[str] = set()
    for c in drifts:
        if not isinstance(c, dict):
            errors.append("drift_classification_not_a_dict")
            continue
        for key in ("path", "classification", "recommended_handling", "evidence"):
            if key not in c:
                errors.append("drift_classification_missing_field:" + key)
        path = c.get("path")
        if path in seen:
            errors.append("duplicate_drift_path:" + str(path))
        if isinstance(path, str):
            seen.add(path)

    ecp = p.get("evidence_commit_path") or {}
    if ecp.get("is_authorization") is not False:
        errors.append("evidence_commit_path_claims_authorization")
    if ecp.get("performed_by_this_contract") is not False:
        errors.append("evidence_commit_claimed_performed")
    if ecp.get("requires_separate_human_approval") is not True:
        errors.append("evidence_commit_not_human_gated")

    # Headline invariants.
    if p.get("future_commit_may_include_report_artifacts") is not True:
        errors.append("evidence_preservation_dropped")
    if p.get("report_artifacts_only_via_separate_evidence_commit") is not True:
        errors.append("evidence_commit_separation_dropped")
    if p.get("cleanup_must_be_separate_future_decision") is not True:
        errors.append("cleanup_separation_dropped")
    if p.get("any_file_changed_by_this_contract") is not False:
        errors.append("contract_claims_to_have_changed_files")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if p.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "modifies_report_artifacts",
        "stages_or_commits_anything",
        "runs_replay",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "fetches_data",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "changes_trading_logic",
        "promotes_gate",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if p.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_disposition_policy_markdown(policy: Any) -> str:
    """Render a disposition policy as deterministic markdown. Pure string work."""
    p = policy if isinstance(policy, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Report Artifact & Local Drift Disposition Policy (READ-ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(p.get("verdict", "")))
    lines.append("- Any file changed by this contract: "
                 + str(p.get("any_file_changed_by_this_contract", "")))
    lines.append("- Future commit may include report artifacts: "
                 + str(p.get("future_commit_may_include_report_artifacts", "")))
    lines.append("- Report artifacts only via separate evidence commit: "
                 + str(p.get("report_artifacts_only_via_separate_evidence_commit", "")))
    lines.append("- Cleanup must be a separate future decision: "
                 + str(p.get("cleanup_must_be_separate_future_decision", "")))
    lines.append("- Next required action: " + str(p.get("next_required_action", "")))
    lines.append("")
    lines.append("## Report directories")
    status = {s.get("path"): s for s in p.get("report_dir_status") or []}
    for d in p.get("report_dir_policies") or []:
        st = status.get(d.get("path")) or {}
        lines.append("### " + str(d.get("path")))
        lines.append("- Disposition: " + str(d.get("recommended_disposition")))
        lines.append("- Cited by: " + str(d.get("cited_by")))
        lines.append("- Present: " + str(st.get("directory_present"))
                     + " | missing files: "
                     + (", ".join(st.get("missing_files") or []) or "(none)"))
        lines.append("- " + str(d.get("rationale")))
    lines.append("")
    lines.append("## Drift file classifications (classified, NOT changed)")
    for c in p.get("drift_file_classifications") or []:
        lines.append("### " + str(c.get("path")))
        lines.append("- Classification: " + str(c.get("classification")))
        lines.append("- Handling: " + str(c.get("recommended_handling")))
        lines.append("- Evidence: " + str(c.get("evidence")))
    lines.append("")
    lines.append("## Evidence commit path (documentation only, authorizes nothing)")
    ecp = p.get("evidence_commit_path") or {}
    lines.append("- Is authorization: " + str(ecp.get("is_authorization")))
    lines.append("- Performed by this contract: "
                 + str(ecp.get("performed_by_this_contract")))
    for rule in ecp.get("rules") or []:
        lines.append("  - " + str(rule))
    lines.append("")
    lines.append("## Blockers")
    for b in (p.get("blockers") or ["(none)"]):
        lines.append("- " + str(b))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)

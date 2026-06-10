"""Crypto-D1 V2 RC1 Out-of-Sample Robustness Research Contract (READ-ONLY, PLAN ONLY).

A PURE, stdlib-only, read-only module that SPECIFIES (but never runs) the RC1 research
direction selected by the human from the Block 179 post resume-policy research continuation
plan: testing whether the evidence-leading resume policy (RP6 on the committed evidence)
remains robust OUT OF SAMPLE, with its parameters strictly UNCHANGED.

It consumes the Block 179 plan (which itself chains read-only through Blocks 178/177 to the
local simulation report), re-validates it with Block 179's own validator, confirms RC1 is a
recognized direction of that plan, and emits a FIXED, hand-specified set of evaluation
windows over the ALREADY-EXISTING QA-passed local CSVs:

  - one TRUE held-out window: 2020-01-01..2020-08-10 (BTC/ETH only; SOL's data starts
    2020-08-11) -- this history was never part of the Block 175 evidence regimes and
    includes the March 2020 crash;
  - fixed boundary-straddling windows that cross the original regime boundaries -- honestly
    labeled as WINDOW-ROBUSTNESS checks, not strictly out-of-sample, because the underlying
    data was seen by the original evidence windows.

Every planned replay keeps the leading policy's parameters UNCHANGED (no optimization, no
parameter search, no fitting, no selection-by-results) and is NOT RUN here: each carries
``is_run=False`` and requires a SEPARATE explicit human command. The contract strictly
PRESERVES ``DO_NOT_PROMOTE_RESUME_POLICY_YET``.

It RUNS NOTHING and WRITES NOTHING: no data fetch, no new simulation, no backtest, no
broker/exchange, no network, no credentials, no real order, no file write. It UNLOCKS no
gate: paper_trading_gate, micro_live_gate and the live gate all stay LOCKED.

Public API:
  - RC1_SCHEMA_VERSION / RC1_LABEL / RC1_MODE / SELECTED_DIRECTION_ID
  - VERDICT_RC1_SPEC_READY / VERDICT_RC1_SPEC_BLOCKED
  - HUMAN_DECISION_PRESERVED / NEXT_REQUIRED_ACTION / SELECTED_VARIANT_ID
  - WINDOW_TYPE_HELD_OUT / WINDOW_TYPE_BOUNDARY_STRADDLING / OUT_OF_SAMPLE_WINDOWS
  - get_rc1_out_of_sample_robustness_contract_label()
  - out_of_sample_windows() / planned_out_of_sample_replays()
  - record_rc1_out_of_sample_spec(continuation_plan)
  - build_rc1_out_of_sample_robustness_spec(repo_root)
  - validate_rc1_out_of_sample_robustness_spec(spec)
  - render_rc1_out_of_sample_robustness_spec_markdown(spec)
"""

from __future__ import annotations

import copy
from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_research_plan import (
    REGIMES_TO_COVER,
)
from sparta_commander.strategy_factory_crypto_d1_post_resume_policy_research_continuation_plan_contract import (
    HUMAN_DECISION_PRESERVED,
    VERDICT_PLAN_READY,
    build_post_resume_policy_research_continuation_plan,
    validate_post_resume_policy_research_continuation_plan,
)

RC1_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_rc1_out_of_sample_robustness_research_contract.v1"
)
RC1_LABEL = (
    "Crypto-D1 V2 RC1 Out-of-Sample Robustness Research Contract (READ-ONLY, PLAN ONLY)"
)
RC1_MODE = "RESEARCH_ONLY"

# The Block 179 direction this contract realizes; the human selected it explicitly.
SELECTED_DIRECTION_ID = "RC1_out_of_sample_robustness_of_leading_policy"

VERDICT_RC1_SPEC_READY = "RC1_OUT_OF_SAMPLE_SPEC_READY"
VERDICT_RC1_SPEC_BLOCKED = "RC1_OUT_OF_SAMPLE_SPEC_BLOCKED"

# After this spec is recorded, the only next step is a SEPARATE explicit human command to
# actually run the planned replays. Nothing here is an execution authorization.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_RC1_OUT_OF_SAMPLE_REPLAY"

WINDOW_TYPE_HELD_OUT = "held_out_early_history"
WINDOW_TYPE_BOUNDARY_STRADDLING = "boundary_straddling_robustness"

# Fixed, hand-specified evaluation windows over the EXISTING QA-passed local CSVs. The data
# files cover BTC/ETH from 2020-01-01 and SOL from 2020-08-11, through 2026-06-08; every
# Block 175 evidence regime started at 2020-08-11, so only the early-2020 window is truly
# held out. The straddle windows reuse seen data and are honestly typed as window-robustness
# checks. These windows are a FIXED design, never a search space.
OUT_OF_SAMPLE_WINDOWS: list[dict[str, Any]] = [
    {
        "window_id": "OOS_W1_2020_early_held_out",
        "window": "2020-01-01..2020-08-10",
        "window_type": WINDOW_TYPE_HELD_OUT,
        "symbols_expected": ["BTC", "ETH"],
        "character": (
            "True held-out history never used in the Block 175 evidence regimes; includes "
            "the March 2020 crash. SOL is absent (its local data starts 2020-08-11)."
        ),
    },
    {
        "window_id": "OOS_W2_2021H2_2022H1_straddle",
        "window": "2021-07-01..2022-06-30",
        "window_type": WINDOW_TYPE_BOUNDARY_STRADDLING,
        "symbols_expected": ["BTC", "ETH", "SOL"],
        "character": (
            "Bull-to-bear transition straddling the 2021/2022 evidence regime boundary; "
            "tests robustness to window choice, not strictly out-of-sample."
        ),
    },
    {
        "window_id": "OOS_W3_2022H2_2023H1_straddle",
        "window": "2022-07-01..2023-06-30",
        "window_type": WINDOW_TYPE_BOUNDARY_STRADDLING,
        "symbols_expected": ["BTC", "ETH", "SOL"],
        "character": (
            "Bear-to-recovery transition straddling the 2022/2023 evidence regime boundary; "
            "tests robustness to window choice, not strictly out-of-sample."
        ),
    },
    {
        "window_id": "OOS_W4_2024H2_2025H1_straddle",
        "window": "2024-07-01..2025-06-30",
        "window_type": WINDOW_TYPE_BOUNDARY_STRADDLING,
        "symbols_expected": ["BTC", "ETH", "SOL"],
        "character": (
            "Recovery-to-recent transition straddling the 2024/2025 evidence regime "
            "boundary; tests robustness to window choice, not strictly out-of-sample."
        ),
    },
]


def get_rc1_out_of_sample_robustness_contract_label() -> str:
    """Human label for the recognized Crypto-D1 RC1 out-of-sample robustness contract."""
    return RC1_LABEL


def out_of_sample_windows() -> list[dict[str, Any]]:
    """Return fresh deep copies of the fixed evaluation windows. Pure."""
    return [copy.deepcopy(w) for w in OUT_OF_SAMPLE_WINDOWS]


def planned_out_of_sample_replays() -> list[dict[str, Any]]:
    """Build the FIXED future replay plan: one planned replay per window, the leading
    policy's parameters UNCHANGED, each NOT YET RUN and each gated on a separate explicit
    human command. Pure; runs nothing."""
    plan: list[dict[str, Any]] = []
    for w in OUT_OF_SAMPLE_WINDOWS:
        plan.append({
            "replay_id": "REPLAY_" + w["window_id"],
            "window_id": w["window_id"],
            "selected_variant_id": SELECTED_VARIANT_ID,
            "policy_source": "evidence_leading_policy_from_block_177_unchanged",
            "policy_parameters_changed": False,
            "data_scope": "QA_PASSED_LOCAL_CSV_ONLY",
            "metrics_to_collect": [
                "total_return", "max_drawdown", "sharpe_ratio",
                "time_in_market", "num_resume_events", "post_resume_drawdown",
            ],
            "is_run": False,
            "requires_human_command": True,
            "authorization_required": NEXT_REQUIRED_ACTION,
        })
    return plan


def record_rc1_out_of_sample_spec(continuation_plan: Any) -> dict[str, Any]:
    """Record the RC1 out-of-sample robustness spec over the Block 179 continuation plan.
    PURE: takes the plan dict (or None), returns a spec dict. Never raises. The carried
    human decision is ALWAYS DO_NOT_PROMOTE; this contract has no promote branch, changes
    no parameter, and unlocks nothing."""
    blockers: list[str] = []
    risk_notes: list[str] = []

    if not isinstance(continuation_plan, dict):
        blockers.append("continuation_plan_missing")
        return _spec(
            VERDICT_RC1_SPEC_BLOCKED, blockers, risk_notes,
            leading={}, recommended_path=None, report_found=False,
        )

    cp = continuation_plan

    plan_validation = validate_post_resume_policy_research_continuation_plan(cp)
    if not plan_validation.get("valid"):
        blockers.append("continuation_plan_invalid")
        blockers.extend("plan:" + e for e in plan_validation.get("errors", []))

    if cp.get("verdict") != VERDICT_PLAN_READY:
        blockers.append("continuation_plan_not_ready")

    if cp.get("human_decision") != HUMAN_DECISION_PRESERVED:
        blockers.append("human_decision_not_do_not_promote")

    direction_ids = {
        d.get("direction_id")
        for d in (cp.get("research_continuation_directions") or [])
        if isinstance(d, dict)
    }
    if SELECTED_DIRECTION_ID not in direction_ids:
        blockers.append("rc1_direction_not_in_continuation_plan")

    leading = dict(cp.get("evidence_leading_policy") or {})
    leader_id = leading.get("policy_id")
    if leader_id:
        risk_notes.append("acknowledged_evidence_leading_policy:" + str(leader_id))
        risk_notes.append("acknowledged_as_evidence_only_not_promotion")
    else:
        blockers.append("no_evidence_leading_policy_to_evaluate")

    risk_notes.append("leading_policy_parameters_unchanged_no_optimization_no_search")
    risk_notes.append("held_out_early_history_covers_btc_eth_only_sol_starts_2020_08_11")
    risk_notes.append(
        "boundary_straddling_windows_are_window_robustness_not_strictly_out_of_sample"
    )
    risk_notes.append("running_any_replay_requires_separate_human_command")
    risk_notes.append("promotion_requires_separate_explicit_human_command")

    ready = (
        not blockers
        and cp.get("verdict") == VERDICT_PLAN_READY
        and cp.get("human_decision") == HUMAN_DECISION_PRESERVED
    )
    verdict = VERDICT_RC1_SPEC_READY if ready else VERDICT_RC1_SPEC_BLOCKED
    return _spec(
        verdict, blockers, risk_notes,
        leading=leading,
        recommended_path=cp.get("recommended_path"),
        report_found=bool(cp.get("resume_policy_sim_report_found")),
    )


def _spec(
    verdict: str,
    blockers: list[str],
    risk_notes: list[str],
    *,
    leading: dict[str, Any],
    recommended_path: Any,
    report_found: bool,
) -> dict[str, Any]:
    """Assemble an RC1 spec dict carrying the read-only safety posture. This contract
    authorizes nothing: paper / micro-live / live stay LOCKED unconditionally and the
    carried human decision is always DO_NOT_PROMOTE."""
    return {
        "schema_version": RC1_SCHEMA_VERSION,
        "label": RC1_LABEL,
        "mode": RC1_MODE,
        "verdict": verdict,
        "selected_direction_id": SELECTED_DIRECTION_ID,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "human_decision": HUMAN_DECISION_PRESERVED,
        "approved_for_execution": False,
        "human_review_required": True,
        "recommended_path": recommended_path,
        "evidence_leading_policy": dict(leading),
        "leading_policy_parameters_changed": False,
        # What the original evidence covered, for transparency about what is held out:
        "in_sample_evidence_windows": [dict(r) for r in REGIMES_TO_COVER],
        "out_of_sample_windows": out_of_sample_windows(),
        "planned_replays": planned_out_of_sample_replays(),
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        "resume_policy_sim_report_found": report_found,
        # Capability posture (this is a SPEC; it executes / runs / authorizes nothing):
        "executes": False,
        "writes_files": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "ran_parameter_search": False,
        "parameters_changed_based_on_results": False,
        "fetches_data": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "promotes_resume_policy": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNCHANGED by this spec):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_rc1_out_of_sample_robustness_spec(repo_root: str = ".") -> dict[str, Any]:
    """Load the Block 179 continuation plan (read-only via Blocks 178/177) and record the
    RC1 spec over it. Reads nothing itself beyond what the upstream chain reads; writes
    nothing; runs no simulation; unlocks no gate."""
    plan = build_post_resume_policy_research_continuation_plan(repo_root)
    spec = record_rc1_out_of_sample_spec(plan)
    spec["continuation_plan_verdict"] = plan.get("verdict")
    return spec


def validate_rc1_out_of_sample_robustness_spec(spec: Any) -> dict[str, Any]:
    """Validate (read-only) an RC1 spec's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(spec, dict):
        return {"valid": False, "errors": ["spec_not_a_dict"]}
    s = spec

    if s.get("verdict") not in (VERDICT_RC1_SPEC_READY, VERDICT_RC1_SPEC_BLOCKED):
        errors.append("bad_verdict")
    if s.get("schema_version") != RC1_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if s.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")
    if s.get("selected_direction_id") != SELECTED_DIRECTION_ID:
        errors.append("bad_selected_direction")

    if s.get("human_decision") != HUMAN_DECISION_PRESERVED:
        errors.append("human_decision_not_do_not_promote")
    if s.get("approved_for_execution") is not False:
        errors.append("spec_marked_approved")
    if s.get("human_review_required") is not True:
        errors.append("spec_not_flagging_human_review")
    if s.get("leading_policy_parameters_changed") is not False:
        errors.append("leading_policy_parameters_changed")

    windows = s.get("out_of_sample_windows")
    if not isinstance(windows, list) or not windows:
        errors.append("no_out_of_sample_windows")
        windows = []
    window_ids: set[str] = set()
    held_out_count = 0
    for w in windows:
        if not isinstance(w, dict):
            errors.append("window_not_a_dict")
            continue
        for key in ("window_id", "window", "window_type", "symbols_expected", "character"):
            if key not in w:
                errors.append("window_missing_field:" + key)
        wid = w.get("window_id")
        if wid in window_ids:
            errors.append("duplicate_window_id:" + str(wid))
        if isinstance(wid, str):
            window_ids.add(wid)
        wtype = w.get("window_type")
        if wtype not in (WINDOW_TYPE_HELD_OUT, WINDOW_TYPE_BOUNDARY_STRADDLING):
            errors.append("bad_window_type:" + str(wtype))
        if wtype == WINDOW_TYPE_HELD_OUT:
            held_out_count += 1
    if windows and held_out_count == 0:
        errors.append("no_truly_held_out_window")

    replays = s.get("planned_replays")
    if not isinstance(replays, list) or not replays:
        errors.append("no_planned_replays")
        replays = []
    referenced: set[str] = set()
    for r in replays:
        if not isinstance(r, dict):
            errors.append("replay_not_a_dict")
            continue
        # No replay may be marked as already run -- this is a spec, nothing has executed.
        if r.get("is_run") is not False:
            errors.append("replay_marked_run:" + str(r.get("replay_id")))
        if r.get("requires_human_command") is not True:
            errors.append("replay_not_human_gated:" + str(r.get("replay_id")))
        if r.get("policy_parameters_changed") is not False:
            errors.append("replay_changes_parameters:" + str(r.get("replay_id")))
        if r.get("data_scope") != "QA_PASSED_LOCAL_CSV_ONLY":
            errors.append("replay_bad_data_scope:" + str(r.get("replay_id")))
        rwid = r.get("window_id")
        if rwid not in window_ids:
            errors.append("replay_references_unknown_window:" + str(rwid))
        if isinstance(rwid, str):
            referenced.add(rwid)
    missing = window_ids - referenced
    if missing:
        errors.append("windows_without_replay:" + ",".join(sorted(missing)))

    if s.get("verdict") == VERDICT_RC1_SPEC_READY and (s.get("blockers") or []):
        errors.append("ready_with_blockers")
    if s.get("verdict") == VERDICT_RC1_SPEC_BLOCKED and not (s.get("blockers") or []):
        errors.append("blocked_without_blockers")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if s.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "ran_parameter_search",
        "parameters_changed_based_on_results",
        "fetches_data",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "authorizes_paper_execution",
        "authorizes_micro_live",
        "authorizes_live_trading",
        "promotes_gate",
        "promotes_resume_policy",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_rc1_out_of_sample_robustness_spec_markdown(spec: Any) -> str:
    """Render an RC1 spec as deterministic markdown. Pure string work."""
    s = spec if isinstance(spec, dict) else {}
    lead = s.get("evidence_leading_policy") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 RC1 Out-of-Sample Robustness Research Spec (PLAN ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(s.get("verdict", "")))
    lines.append("- Selected direction: " + str(s.get("selected_direction_id", "")))
    lines.append("- Selected variant: " + str(s.get("selected_variant_id", "")))
    lines.append("- Human decision (preserved): " + str(s.get("human_decision", "")))
    lines.append("- Approved for execution: " + str(s.get("approved_for_execution", "")))
    lines.append("- Next required action: " + str(s.get("next_required_action", "")))
    lines.append("")
    lines.append("## Policy under evaluation (evidence only, parameters UNCHANGED)")
    lines.append("- Policy: " + str(lead.get("policy_id")))
    lines.append("- Parameters changed: " + str(s.get("leading_policy_parameters_changed")))
    lines.append("")
    lines.append("## In-sample evidence windows (what the original evidence covered)")
    for r in s.get("in_sample_evidence_windows") or []:
        lines.append("- " + str(r.get("regime_id")) + " (" + str(r.get("window")) + ")")
    lines.append("")
    lines.append("## Evaluation windows (fixed; never a search space)")
    for w in s.get("out_of_sample_windows") or []:
        lines.append("### " + str(w.get("window_id")))
        lines.append("- Window: " + str(w.get("window")))
        lines.append("- Type: " + str(w.get("window_type")))
        lines.append("- Symbols expected: " + ", ".join(w.get("symbols_expected") or []))
        lines.append("- " + str(w.get("character")))
    lines.append("")
    lines.append("## Planned replays (NOT YET RUN)")
    for r in s.get("planned_replays") or []:
        lines.append("- " + str(r.get("replay_id")) + " -> window " + str(r.get("window_id"))
                     + " | is_run: " + str(r.get("is_run"))
                     + " | requires_human_command: " + str(r.get("requires_human_command")))
    lines.append("")
    lines.append("## Blockers")
    for b in (s.get("blockers") or ["(none)"]):
        lines.append("- " + str(b))
    lines.append("")
    lines.append("## Risk notes")
    for note in s.get("risk_notes") or ["(none)"]:
        lines.append("- " + str(note))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- runs_simulation: False (a separate human command is required to run any replay)")
    return "\n".join(lines)

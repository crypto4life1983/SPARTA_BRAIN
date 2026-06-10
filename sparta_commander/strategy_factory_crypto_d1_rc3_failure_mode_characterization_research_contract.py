"""Crypto-D1 V2 RC3 Failure-Mode Characterization Research Contract (READ-ONLY).

A PURE, stdlib-only, read-only module that CHARACTERIZES -- purely descriptively, with NO
recompute -- why the RC1 evidence leader (RP6 on the committed evidence) failed out of
sample after leading in sample, and why the simpler re-entry rules (RP4/RP5 on the
committed evidence) held up better. Every number it cites is read verbatim from the two
ALREADY-PERSISTED replay reports; nothing is re-simulated, re-ranked, fitted, or tuned.

It is gated on the Block 187 human evidence decision (which selected the RC3 direction)
and reads ONLY the local artifacts
``reports/crypto_d1_rc1_out_of_sample_replay/rc1_oos_replay_report.json`` and
``reports/crypto_d1_rc2_cross_policy_replay/rc2_cross_policy_replay_report.json``
(read-only, re-validated with their own runners' validators).

It examines a FIXED catalog of candidate failure modes and marks each SUPPORTED or NOT
on the committed evidence:
  - FM1 volatility_cooldown_overfit  -- the leader's in-sample edge did not transfer;
  - FM2 regime_sensitivity           -- the leader's results vary sharply across windows;
  - FM3 delayed_or_over_filtered_reentry -- waiting/filtered policies lag responsive ones;
  - FM4 ranking_instability          -- the in-sample ranking did not survive out of sample.

RP4/RP5 remain EVIDENCE ONLY -- NOT selected successors (``successors_selected`` is
structurally False) -- and the carried human decision is ALWAYS
``DO_NOT_PROMOTE_RESUME_POLICY_YET``. It RUNS NOTHING and WRITES NOTHING: no data fetch,
no replay, no simulation, no backtest, no optimization, no parameter search, no
broker/exchange, no network, no credentials, no real order, no file write. It UNLOCKS no
gate: paper_trading_gate, micro_live_gate and the live gate all stay LOCKED.

Public API:
  - RC3_SCHEMA_VERSION / RC3_LABEL / RC3_MODE / SELECTED_VARIANT_ID
  - VERDICT_RC3_COMPLETE / VERDICT_RC3_BLOCKED / NEXT_REQUIRED_ACTION
  - FAILURE_MODE_IDS
  - get_rc3_failure_mode_characterization_label()
  - characterize_failure_modes(rc1_report, rc2_report, human_evidence_decision)
  - build_rc3_failure_mode_characterization(repo_root)
  - validate_rc3_failure_mode_characterization(decision)
  - render_rc3_failure_mode_characterization_markdown(decision)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_paper_trading_prep_contract import (
    SELECTED_VARIANT_ID,
)
from sparta_commander.strategy_factory_crypto_d1_resume_policy_results_review_contract import (
    DO_NOT_PROMOTE_RESUME_POLICY_YET,
)
from sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_replay_runner import (
    validate_rc1_out_of_sample_replay_report,
)
from sparta_commander.strategy_factory_crypto_d1_rc1_out_of_sample_results_review_contract import (
    load_rc1_oos_replay_report,
)
from sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_replay_runner import (
    validate_rc2_cross_policy_replay_report,
)
from sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_results_review_contract import (
    load_rc2_cross_policy_replay_report,
)
from sparta_commander.strategy_factory_crypto_d1_rc2_cross_policy_human_evidence_decision_contract import (
    DIRECTION_RC3_FAILURE_MODE_CHARACTERIZATION,
    VERDICT_DECISION_RECORDED,
    build_rc2_cross_policy_human_evidence_decision,
    validate_rc2_cross_policy_human_evidence_decision,
)

RC3_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_rc3_failure_mode_characterization_research_contract.v1"
)
RC3_LABEL = (
    "Crypto-D1 V2 RC3 Failure-Mode Characterization Research Contract (READ-ONLY)"
)
RC3_MODE = "RESEARCH_ONLY"

VERDICT_RC3_COMPLETE = "RC3_CHARACTERIZATION_COMPLETE"
VERDICT_RC3_BLOCKED = "RC3_CHARACTERIZATION_BLOCKED"

# After this characterization the ONLY next step is a human decision over the RC3
# findings; no execution is authorized here.
NEXT_REQUIRED_ACTION = "HUMAN_DECISION_ON_RC3_FINDINGS"

FAILURE_MODE_IDS: tuple[str, ...] = (
    "FM1_volatility_cooldown_overfit",
    "FM2_regime_sensitivity",
    "FM3_delayed_or_over_filtered_reentry",
    "FM4_ranking_instability",
)

# Fixed descriptive taxonomy of the SIX known candidates: which wait/filter before
# re-entry versus which re-enter responsively. Documentation of the existing design,
# never a new parameterization.
_WAITING_FILTERED_POLICIES = (
    "RP2_wait_14d_trend_on",
    "RP3_wait_30d_trend_on",
    "RP6_resume_after_volatility_cools",
)
_RESPONSIVE_POLICIES = (
    "RP1_wait_7d_trend_on",
    "RP4_breadth_2of3_above_sma200",
    "RP5_half_then_full_on_confirmation",
)


def get_rc3_failure_mode_characterization_label() -> str:
    """Human label for the recognized Crypto-D1 RC3 failure-mode characterization
    contract."""
    return RC3_LABEL


def _pct(x: Any) -> str:
    try:
        return f"{float(x) * 100:.2f}%"
    except (TypeError, ValueError):
        return str(x)


def _rc2_aggregates(rc2_report: dict[str, Any]) -> dict[str, dict[str, float]]:
    """policy_id -> aggregate numbers, read verbatim from the RC2 report. Pure."""
    out: dict[str, dict[str, float]] = {}
    for p in rc2_report.get("policy_results") or []:
        pid = p.get("policy_id")
        agg = p.get("aggregate") or {}
        if isinstance(pid, str):
            out[pid] = {
                "mean_total_return": float(agg.get("mean_total_return", 0.0) or 0.0),
                "worst_max_drawdown": float(agg.get("worst_max_drawdown", 0.0) or 0.0),
                "mean_sharpe_ratio": float(agg.get("mean_sharpe_ratio", 0.0) or 0.0),
            }
    return out


def characterize_failure_modes(
    rc1_report: Any,
    rc2_report: Any,
    human_evidence_decision: Any,
) -> dict[str, Any]:
    """Characterize the failure modes purely descriptively from the two persisted reports,
    gated on the Block 187 human decision. PURE: takes dicts (or None), returns a decision
    dict. Never raises. Recomputes no simulation, selects no successor, and the carried
    human decision is ALWAYS DO_NOT_PROMOTE."""
    blockers: list[str] = []
    risk_notes: list[str] = []

    # Gate: the human must have selected the RC3 direction in Block 187.
    if not isinstance(human_evidence_decision, dict):
        blockers.append("rc2_human_evidence_decision_missing")
    else:
        hed = human_evidence_decision
        hed_validation = validate_rc2_cross_policy_human_evidence_decision(hed)
        if not hed_validation.get("valid"):
            blockers.append("rc2_human_evidence_decision_invalid")
        if hed.get("verdict") != VERDICT_DECISION_RECORDED:
            blockers.append("rc2_human_evidence_decision_not_recorded")
        if hed.get("selected_research_direction") != (
            DIRECTION_RC3_FAILURE_MODE_CHARACTERIZATION
        ):
            blockers.append("rc3_direction_not_selected_by_human")

    if not isinstance(rc1_report, dict):
        blockers.append("rc1_oos_replay_report_missing")
        rc1_report = {}
    elif not validate_rc1_out_of_sample_replay_report(rc1_report).get("valid"):
        blockers.append("rc1_oos_replay_report_invalid")

    if not isinstance(rc2_report, dict):
        blockers.append("rc2_cross_policy_replay_report_missing")
        rc2_report = {}
    elif not validate_rc2_cross_policy_replay_report(rc2_report).get("valid"):
        blockers.append("rc2_cross_policy_replay_report_invalid")

    aggs = _rc2_aggregates(rc2_report)
    ls = dict(rc2_report.get("leader_stability") or {})
    rc1_leader = ls.get("rc1_leader_policy_id")
    flip = bool(rc1_leader) and not ls.get("rc1_leader_leads_any_category")
    in_sample = dict(rc1_report.get("in_sample_reference") or {})
    leader_agg = aggs.get(str(rc1_leader), {})

    failure_modes: list[dict[str, Any]] = []

    # FM1 -- volatility_cooldown_overfit: the leader's in-sample edge did not transfer.
    is_mean = float(in_sample.get("mean_total_return", 0.0) or 0.0)
    oos_mean = float(leader_agg.get("mean_total_return", 0.0) or 0.0)
    fm1_supported = bool(rc1_leader) and flip and is_mean > 0 and oos_mean < 0.5 * is_mean
    failure_modes.append({
        "failure_mode_id": "FM1_volatility_cooldown_overfit",
        "description": (
            "The leader's volatility-cooldown trigger looks fitted to the in-sample "
            "evidence: its edge collapses out of sample."
        ),
        "supported": fm1_supported,
        "evidence": [
            f"leader in-sample mean return {_pct(is_mean)} vs OOS mean {_pct(oos_mean)}",
            "leader leads zero OOS ranking categories" if flip
            else "leader still leads at least one OOS category",
        ],
    })

    # FM2 -- regime_sensitivity: the leader's per-window RC1 results vary sharply.
    leader_windows = [
        w for w in (rc1_report.get("window_results") or []) if w.get("evaluated")
    ]
    rets = [float((w.get("metrics") or {}).get("total_return", 0.0) or 0.0)
            for w in leader_windows]
    dds = [float((w.get("metrics") or {}).get("max_drawdown", 0.0) or 0.0)
           for w in leader_windows]
    negative_windows = [
        str(w.get("window_id")) for w in leader_windows
        if float((w.get("metrics") or {}).get("total_return", 0.0) or 0.0) < 0
    ]
    is_worst_dd = float(in_sample.get("worst_max_drawdown", 0.0) or 0.0)
    oos_worst_dd = min(dds) if dds else 0.0
    fm2_supported = bool(leader_windows) and (
        bool(negative_windows) or oos_worst_dd < is_worst_dd
    )
    failure_modes.append({
        "failure_mode_id": "FM2_regime_sensitivity",
        "description": (
            "The leader's results swing sharply across the fixed windows: strong in some "
            "regimes, negative or deeply drawn down in others."
        ),
        "supported": fm2_supported,
        "evidence": [
            f"leader OOS window returns span {_pct(min(rets))} to {_pct(max(rets))}"
            if rets else "no evaluated leader windows",
            f"negative windows: {', '.join(negative_windows) or '(none)'}",
            f"leader OOS worst drawdown {_pct(oos_worst_dd)} vs in-sample {_pct(is_worst_dd)}",
        ],
    })

    # FM3 -- delayed_or_over_filtered_reentry: waiting/filtered policies lag responsive
    # ones on the SAME windows.
    waiting = [aggs[p]["mean_total_return"] for p in _WAITING_FILTERED_POLICIES if p in aggs]
    responsive = [aggs[p]["mean_total_return"] for p in _RESPONSIVE_POLICIES if p in aggs]
    fm3_supported = (
        bool(waiting) and bool(responsive)
        and (sum(responsive) / len(responsive)) > (sum(waiting) / len(waiting))
    )
    failure_modes.append({
        "failure_mode_id": "FM3_delayed_or_over_filtered_reentry",
        "description": (
            "Policies that wait longer or add extra filters before re-entry give up "
            "recovery returns versus responsive re-entry rules on the same windows."
        ),
        "supported": fm3_supported,
        "evidence": [
            "responsive group mean return "
            + (_pct(sum(responsive) / len(responsive)) if responsive else "(n/a)")
            + " vs waiting/filtered group "
            + (_pct(sum(waiting) / len(waiting)) if waiting else "(n/a)"),
            "groups are a fixed descriptive taxonomy of the six known candidates",
        ],
    })

    # FM4 -- ranking_instability: the in-sample ranking did not survive out of sample.
    rankings = dict(rc2_report.get("rankings") or {})
    fm4_supported = flip
    failure_modes.append({
        "failure_mode_id": "FM4_ranking_instability",
        "description": (
            "The in-sample policy ranking carried no out-of-sample information: the "
            "in-sample leader is dethroned and new leaders emerge per category."
        ),
        "supported": fm4_supported,
        "evidence": [
            f"in-sample leader: {rc1_leader}",
            "OOS category leaders: " + ", ".join(
                f"{k}={v}" for k, v in sorted(rankings.items())
            ) if rankings else "no rankings present",
        ],
    })

    # Why the strongest candidates held up -- descriptive only, never a selection.
    strongest = sorted(set(str(v) for v in rankings.values() if v))
    strength_analysis = {
        "strongest_evidence_policies": strongest,
        "evidence_only_not_selected_successors": True,
        "observations": [
            "simple breadth re-entry reacts to trend resumption without fitted "
            "thresholds or extra lag",
            "staged exposure caps the cost of a false re-entry while still "
            "participating early",
            "neither observation selects a successor: validating any candidate "
            "requires fresh evidence, not the same windows",
        ],
        "aggregates": {p: aggs[p] for p in strongest if p in aggs},
    }

    supported_ids = [
        fm["failure_mode_id"] for fm in failure_modes if fm.get("supported")
    ]
    risk_notes.append("characterization_is_descriptive_only_no_recompute")
    risk_notes.append("strongest_policies_are_evidence_only_not_selected_successors")
    risk_notes.append("oos_evidence_supports_keeping_do_not_promote")
    risk_notes.append("human_review_required_before_any_execution_promotion")

    verdict = VERDICT_RC3_COMPLETE if not blockers else VERDICT_RC3_BLOCKED
    return {
        "schema_version": RC3_SCHEMA_VERSION,
        "label": RC3_LABEL,
        "mode": RC3_MODE,
        "verdict": verdict,
        "selected_variant_id": SELECTED_VARIANT_ID,
        "human_decision": DO_NOT_PROMOTE_RESUME_POLICY_YET,
        "approved_for_execution": False,
        "human_review_required": True,
        "successors_selected": False,
        "rc1_leader_policy_id": rc1_leader,
        "failure_modes": failure_modes,
        "supported_failure_modes": supported_ids,
        "strength_analysis": strength_analysis,
        "blockers": list(blockers),
        "risk_notes": list(risk_notes),
        # Capability posture (this contract executes / authorizes / writes nothing live):
        "executes": False,
        "writes_files": False,
        "runs_replay": False,
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
        # Gate posture (UNCHANGED by this characterization):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_rc3_failure_mode_characterization(repo_root: str = ".") -> dict[str, Any]:
    """Load the two persisted replay reports and the Block 187 decision (all read-only)
    and characterize the failure modes over them. Writes nothing; runs no replay; unlocks
    no gate."""
    rc1_loaded = load_rc1_oos_replay_report(repo_root)
    rc2_loaded = load_rc2_cross_policy_replay_report(repo_root)
    hed = build_rc2_cross_policy_human_evidence_decision(repo_root)
    decision = characterize_failure_modes(
        rc1_loaded["report"], rc2_loaded["report"], hed
    )
    decision["rc1_oos_replay_report_found"] = rc1_loaded["found"]
    decision["rc1_oos_replay_report_path"] = rc1_loaded["path"]
    decision["rc2_replay_report_found"] = rc2_loaded["found"]
    decision["rc2_replay_report_path"] = rc2_loaded["path"]
    decision["human_evidence_decision_verdict"] = hed.get("verdict")
    return decision


def validate_rc3_failure_mode_characterization(decision: Any) -> dict[str, Any]:
    """Validate (read-only) an RC3 characterization's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(decision, dict):
        return {"valid": False, "errors": ["decision_not_a_dict"]}
    d = decision

    if d.get("verdict") not in (VERDICT_RC3_COMPLETE, VERDICT_RC3_BLOCKED):
        errors.append("bad_verdict")
    if d.get("schema_version") != RC3_SCHEMA_VERSION:
        errors.append("bad_schema_version")
    if d.get("selected_variant_id") != SELECTED_VARIANT_ID:
        errors.append("bad_selected_variant")

    if d.get("human_decision") != DO_NOT_PROMOTE_RESUME_POLICY_YET:
        errors.append("human_decision_not_do_not_promote")
    if d.get("approved_for_execution") is not False:
        errors.append("decision_marked_approved")
    if d.get("human_review_required") is not True:
        errors.append("decision_not_flagging_human_review")
    if d.get("successors_selected") is not False:
        errors.append("successor_policy_marked_selected")

    fms = d.get("failure_modes")
    if not isinstance(fms, list) or not fms:
        errors.append("no_failure_modes")
        fms = []
    seen: set[str] = set()
    for fm in fms:
        if not isinstance(fm, dict):
            errors.append("failure_mode_not_a_dict")
            continue
        for key in ("failure_mode_id", "description", "supported", "evidence"):
            if key not in fm:
                errors.append("failure_mode_missing_field:" + key)
        fid = fm.get("failure_mode_id")
        if fid in seen:
            errors.append("duplicate_failure_mode_id:" + str(fid))
        if isinstance(fid, str):
            seen.add(fid)
        if not isinstance(fm.get("supported"), bool):
            errors.append("failure_mode_supported_not_bool:" + str(fid))
    if fms and seen != set(FAILURE_MODE_IDS):
        errors.append("failure_mode_catalog_mismatch")

    sa = d.get("strength_analysis") or {}
    if sa.get("evidence_only_not_selected_successors") is not True:
        errors.append("strength_analysis_not_marked_evidence_only")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if d.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_replay",
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
        if d.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_rc3_failure_mode_characterization_markdown(decision: Any) -> str:
    """Render an RC3 characterization as deterministic markdown. Pure string work."""
    d = decision if isinstance(decision, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 V2 RC3 Failure-Mode Characterization (READ-ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(d.get("verdict", "")))
    lines.append("- Selected variant: " + str(d.get("selected_variant_id", "")))
    lines.append("- Human decision (preserved): " + str(d.get("human_decision", "")))
    lines.append("- Successors selected: " + str(d.get("successors_selected", "")))
    lines.append("- RC1 leader characterized: " + str(d.get("rc1_leader_policy_id", "")))
    lines.append("- Supported failure modes: "
                 + (", ".join(d.get("supported_failure_modes") or []) or "(none)"))
    lines.append("- Next required action: " + str(d.get("next_required_action", "")))
    lines.append("")
    lines.append("## Failure modes (descriptive, from persisted evidence only)")
    for fm in d.get("failure_modes") or []:
        lines.append("### " + str(fm.get("failure_mode_id"))
                     + " -- supported: " + str(fm.get("supported")))
        lines.append("- " + str(fm.get("description")))
        for e in fm.get("evidence") or []:
            lines.append("  - " + str(e))
    lines.append("")
    sa = d.get("strength_analysis") or {}
    lines.append("## Why the strongest candidates held up (evidence only, NOT successors)")
    lines.append("- Policies: " + (", ".join(sa.get("strongest_evidence_policies") or [])
                                   or "(none)"))
    for o in sa.get("observations") or []:
        lines.append("- " + str(o))
    lines.append("")
    lines.append("## Blockers")
    for b in (d.get("blockers") or ["(none)"]):
        lines.append("- " + str(b))
    lines.append("")
    lines.append("## Risk notes")
    for note in d.get("risk_notes") or ["(none)"]:
        lines.append("- " + str(note))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    lines.append("- authorizes_paper_execution: False (separate human gate + command required)")
    return "\n".join(lines)

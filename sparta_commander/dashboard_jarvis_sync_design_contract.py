"""SPARTA Dashboard / JARVIS Sync DESIGN Contract (READ-ONLY, DISPLAY MODEL ONLY).

Roadmap link L6 (build sequence seq 6) -- the FINAL link of the Strategy Factory
Automation Roadmap. It defines how the completed automation chain is SURFACED on
the dashboard and through JARVIS, as a pure display model.

    idea -> intake -> adapter -> packet -> batch + ONE signature
      -> cycle SPEC -> safe report payload                         [L1-L5, live]
      -> THIS MODULE: dashboard/JARVIS display model               [L6]

What this module produces: an in-memory DISPLAY MODEL -- dashboard panel fields,
a JARVIS status sentence, the automation-roadmap status rows, the current chain
state, the next required action, and the human-action-needed banner. Display
only. There is no button, link, or control in the model that can trigger work:
the model carries no callbacks, no commands wired to handlers, nothing
executable -- only TEXT a human reads before deciding what to command next.

What this module can never do (validator-enforced):
  - It does NOT touch the real dashboard or JARVIS runtime: no template edit,
    no route change, no DB write, no transport. Wiring the display model into
    app.py/jarvis is a future, separately approved change.
  - It refuses unsafe display content: secrets, credentials, balances, order
    ids, live positions, and trade-execution language can never be displayed.
  - It refuses performance claims unless the text carries an explicit evidence
    label ("[evidence: ...]"); an unlabeled "profit"/"win rate" line refuses.
  - No implied approval: the display always says a human action is needed, and
    every command shown is marked as a recommendation the human must issue.

Public API:
  - SYNC_SCHEMA_VERSION / SYNC_LABEL / SYNC_MODE
  - ROADMAP_LINK_ID / ROADMAP_SEQ
  - VERDICT_SYNC_DISPLAY_READY / VERDICT_SYNC_DISPLAY_REFUSED
  - AUTOMATION_CHAIN_LINKS / FORBIDDEN_DISPLAY_TOKENS
  - PERFORMANCE_CLAIM_TOKENS / EVIDENCE_LABEL_MARKER
  - NEXT_REQUIRED_ACTION
  - get_dashboard_jarvis_sync_design_label()
  - build_sync_display_model(result_report)
  - validate_sync_display_model(model)
  - render_sync_display_markdown(model)
"""

from __future__ import annotations

import hashlib
from typing import Any

from sparta_commander.result_notification_reporting_contract import (
    FORBIDDEN_CONTENT_TOKENS,
    VERDICT_REPORT_READY,
    validate_result_report,
)

SYNC_SCHEMA_VERSION = "dashboard_jarvis_sync_design_contract.v1"
SYNC_LABEL = (
    "SPARTA Dashboard / JARVIS Sync DESIGN (READ-ONLY, DISPLAY MODEL ONLY)"
)
SYNC_MODE = "RESEARCH_ONLY"

ROADMAP_LINK_ID = "L6_dashboard_jarvis_automation_sync"
ROADMAP_SEQ = 6

VERDICT_SYNC_DISPLAY_READY = "SYNC_DISPLAY_MODEL_READY"
VERDICT_SYNC_DISPLAY_REFUSED = "SYNC_DISPLAY_MODEL_REFUSED"

# The roadmap is complete after this link; what remains is the human's review.
NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_COMPLETED_ROADMAP"

# The automation chain as it should be displayed (status rows, display text).
AUTOMATION_CHAIN_LINKS = (
    {"link": "L1_intake_to_queue_adapter",
     "display": "idea triage routed into an in-memory proposal", "built": True},
    {"link": "L2_lane_specific_approval_packet_generator",
     "display": "unsigned, lane-aware approval packet", "built": True},
    {"link": "L3_batch_approval_schema",
     "display": "one human signature per fully enumerated chain", "built": True},
    {"link": "L4_scheduled_research_cycle_controller",
     "display": "cycle rulebook (spec only, no scheduler built)", "built": True},
    {"link": "L5_result_notification_reporting_layer",
     "display": "safe report payloads (nothing sent)", "built": True},
    {"link": "L6_dashboard_jarvis_automation_sync",
     "display": "this display model (display only, no controls)", "built": True},
)

# Display content screen: inherited from L5 plus display-specific bans.
FORBIDDEN_DISPLAY_TOKENS = FORBIDDEN_CONTENT_TOKENS + (
    "long btc", "short btc", "leverage", "stop loss hit",
)

# Performance claims refuse UNLESS the text carries an explicit evidence label.
PERFORMANCE_CLAIM_TOKENS = (
    "profit", "profitable", "win rate", "winrate", "guaranteed", "returns of",
    "made money", "outperform", "alpha of", "sharpe of",
)
EVIDENCE_LABEL_MARKER = "[evidence:"


def get_dashboard_jarvis_sync_design_label() -> str:
    """Human label for the recognized dashboard/JARVIS sync design contract."""
    return SYNC_LABEL


def _find_forbidden_display_token(*texts: Any) -> str | None:
    """Return the first forbidden display token found in any text, else None."""
    joined = " ".join(str(t) for t in texts if t is not None).lower()
    for token in FORBIDDEN_DISPLAY_TOKENS:
        if token in joined:
            return token
    return None


def _find_unlabeled_performance_claim(*texts: Any) -> str | None:
    """Return the first performance-claim token found in text that lacks an
    explicit evidence label, else None."""
    joined = " ".join(str(t) for t in texts if t is not None).lower()
    if EVIDENCE_LABEL_MARKER in joined:
        return None
    for token in PERFORMANCE_CLAIM_TOKENS:
        if token in joined:
            return token
    return None


def _base_model() -> dict[str, Any]:
    return {
        "schema_version": SYNC_SCHEMA_VERSION,
        "label": SYNC_LABEL,
        "mode": SYNC_MODE,
        "roadmap_link_id": ROADMAP_LINK_ID,
        "roadmap_seq": ROADMAP_SEQ,
        "verdict": None,
        "blockers": [],
        "display_id": None,
        "lane": None,
        "dashboard_display": None,
        "jarvis_display": None,
        "automation_chain_display": [dict(l) for l in AUTOMATION_CHAIN_LINKS],
        # Constitution, stated structurally:
        "display_only_no_controls": True,
        "no_button_or_action_can_trigger_work": True,
        "display_modifies_no_dashboard": True,
        "display_modifies_no_jarvis_runtime": True,
        "no_transport_nothing_sent": True,
        "no_implied_approval_of_anything": True,
        "no_unlabeled_performance_claims": True,
        "human_action_needed": True,
        "model_is_in_memory_only": True,
        "human_review_required": True,
        # Capability posture:
        "executes": False,
        "writes_files": False,
        "writes_queue": False,
        "writes_ledger": False,
        "writes_dashboard": False,
        "modifies_jarvis_runtime": False,
        "sends_notifications": False,
        "runs_research": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "starts_scheduler": False,
        "starts_daemon": False,
        "starts_background_worker": False,
        "runs_loop": False,
        "advances_any_cycle": False,
        "fetches_data": False,
        "calls_api": False,
        "connects_broker": False,
        "connects_exchange": False,
        "uses_real_money": False,
        "uses_network": False,
        "uses_credentials": False,
        "contains_order_logic": False,
        "authorizes_paper_execution": False,
        "authorizes_micro_live": False,
        "authorizes_live_trading": False,
        "promotes_gate": False,
        "unlocks_downstream_gate": False,
        # Gate posture (UNTOUCHED):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def build_sync_display_model(result_report: Any) -> dict[str, Any]:
    """Turn a READY safe report payload into a dashboard/JARVIS DISPLAY MODEL;
    refuse anything unsafe. PURE: never raises, never writes a dashboard,
    never touches the JARVIS runtime, never sends, never runs anything."""
    model = _base_model()

    if not isinstance(result_report, dict):
        model["verdict"] = VERDICT_SYNC_DISPLAY_REFUSED
        model["blockers"].append("result_report_missing_or_not_a_dict")
        return model

    report_validation = validate_result_report(result_report)
    if not report_validation.get("valid"):
        model["verdict"] = VERDICT_SYNC_DISPLAY_REFUSED
        model["blockers"].append("result_report_invalid")
        return model

    if result_report.get("verdict") != VERDICT_REPORT_READY:
        model["verdict"] = VERDICT_SYNC_DISPLAY_REFUSED
        model["blockers"].append("no_ready_report_to_display")
        return model

    summary = result_report.get("summary")
    recommendation = result_report.get("next_safe_command_recommendation")

    token = _find_forbidden_display_token(summary, recommendation)
    if token is not None:
        model["verdict"] = VERDICT_SYNC_DISPLAY_REFUSED
        model["blockers"].append("forbidden_display_token:" + token)
        return model

    claim = _find_unlabeled_performance_claim(summary, recommendation)
    if claim is not None:
        model["verdict"] = VERDICT_SYNC_DISPLAY_REFUSED
        model["blockers"].append("unlabeled_performance_claim:" + claim)
        return model

    lane = result_report.get("lane")
    result_type = result_report.get("result_type")
    chain_state_line = (
        "automation chain L1-L6 designed; current update: "
        + str(result_type).replace("_", " ")
    )
    model["verdict"] = VERDICT_SYNC_DISPLAY_READY
    model["display_id"] = "display_" + hashlib.sha256(
        (str(result_report.get("report_id")) + "|sync").encode("utf-8")
    ).hexdigest()[:12]
    model["lane"] = lane
    model["dashboard_display"] = {
        "panel_title": "Strategy Factory Automation",
        "lane": lane,
        "chain_state_line": chain_state_line,
        "report_summary": summary,
        "next_required_action_display": (
            "Next required action: " + str(result_report.get("next_required_action"))
        ),
        "recommendation_display": (
            "Suggested next safe command (human must issue it): "
            + str(recommendation)
        ),
        "human_action_needed_banner": "HUMAN ACTION NEEDED -- nothing proceeds on its own",
        "automation_roadmap_rows": [dict(l) for l in AUTOMATION_CHAIN_LINKS],
        "display_only": True,
        "action_buttons": [],
        "buttons_forbidden_by_design": True,
    }
    model["jarvis_display"] = {
        "status_sentence": (
            "The strategy factory has an update waiting for your review: "
            + str(result_type).replace("_", " ") + " on lane " + str(lane)
            + ". No action was taken, and nothing will move until you decide."
        ),
        "spoken_next_action": (
            "When you are ready, review the report and issue the next command "
            "yourself. I can only describe; I cannot act."
        ),
        "contains_no_performance_claims": True,
        "display_only": True,
    }
    return model


def validate_sync_display_model(model: Any) -> dict[str, Any]:
    """Validate (read-only) a display model's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(model, dict):
        return {"valid": False, "errors": ["model_not_a_dict"]}
    m = model

    verdict = m.get("verdict")
    if verdict not in (VERDICT_SYNC_DISPLAY_READY, VERDICT_SYNC_DISPLAY_REFUSED):
        errors.append("bad_verdict")

    chain = m.get("automation_chain_display")
    if not isinstance(chain, list) or [c.get("link") for c in chain] != [
        l["link"] for l in AUTOMATION_CHAIN_LINKS
    ]:
        errors.append("automation_chain_display_tampered")

    if verdict == VERDICT_SYNC_DISPLAY_REFUSED:
        if not m.get("blockers"):
            errors.append("refused_model_without_blockers")
        if m.get("dashboard_display") is not None:
            errors.append("refused_model_carries_dashboard_display")
        if m.get("jarvis_display") is not None:
            errors.append("refused_model_carries_jarvis_display")

    if verdict == VERDICT_SYNC_DISPLAY_READY:
        if m.get("blockers"):
            errors.append("ready_model_carries_blockers")
        if not m.get("display_id"):
            errors.append("ready_model_without_id")
        dash = m.get("dashboard_display")
        jarv = m.get("jarvis_display")
        if not isinstance(dash, dict):
            errors.append("dashboard_display_missing")
        else:
            if dash.get("display_only") is not True:
                errors.append("dashboard_display_not_display_only")
            if dash.get("action_buttons"):
                errors.append("dashboard_display_carries_action_buttons")
            if dash.get("buttons_forbidden_by_design") is not True:
                errors.append("button_ban_dropped")
            if "HUMAN ACTION NEEDED" not in str(
                dash.get("human_action_needed_banner")
            ):
                errors.append("human_action_banner_missing")
            if "human must issue it" not in str(dash.get("recommendation_display")):
                errors.append("recommendation_not_marked_human_issued")
            token = _find_forbidden_display_token(*dash.values())
            if token is not None:
                errors.append("forbidden_display_content_in_dashboard:" + token)
            claim = _find_unlabeled_performance_claim(
                dash.get("report_summary"), dash.get("recommendation_display"))
            if claim is not None:
                errors.append("unlabeled_performance_claim_in_dashboard:" + claim)
        if not isinstance(jarv, dict):
            errors.append("jarvis_display_missing")
        else:
            if jarv.get("display_only") is not True:
                errors.append("jarvis_display_not_display_only")
            if jarv.get("contains_no_performance_claims") is not True:
                errors.append("jarvis_display_allows_performance_claims")
            if "I cannot act" not in str(jarv.get("spoken_next_action")):
                errors.append("jarvis_cannot_act_line_missing")
            token = _find_forbidden_display_token(*jarv.values())
            if token is not None:
                errors.append("forbidden_display_content_in_jarvis:" + token)

    # Constitution invariants.
    for key, err in (
        ("display_only_no_controls", "controls_allowed"),
        ("no_button_or_action_can_trigger_work", "work_trigger_allowed"),
        ("display_modifies_no_dashboard", "dashboard_modification_claimed"),
        ("display_modifies_no_jarvis_runtime", "jarvis_modification_claimed"),
        ("no_transport_nothing_sent", "transport_claimed"),
        ("no_implied_approval_of_anything", "implied_approval_allowed"),
        ("no_unlabeled_performance_claims", "performance_claim_rule_dropped"),
        ("human_action_needed", "human_action_dropped"),
        ("model_is_in_memory_only", "model_not_in_memory_only"),
        ("human_review_required", "human_review_dropped"),
    ):
        if m.get(key) is not True:
            errors.append(err)

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if m.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "writes_queue",
        "writes_ledger",
        "writes_dashboard",
        "modifies_jarvis_runtime",
        "sends_notifications",
        "runs_research",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "starts_scheduler",
        "starts_daemon",
        "starts_background_worker",
        "runs_loop",
        "advances_any_cycle",
        "fetches_data",
        "calls_api",
        "connects_broker",
        "connects_exchange",
        "uses_real_money",
        "uses_network",
        "uses_credentials",
        "contains_order_logic",
        "authorizes_paper_execution",
        "authorizes_micro_live",
        "authorizes_live_trading",
        "promotes_gate",
        "unlocks_downstream_gate",
    )
    for key in must_be_false:
        if m.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_sync_display_markdown(model: Any) -> str:
    """Render a display model as deterministic markdown. Pure string work."""
    m = model if isinstance(model, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Dashboard / JARVIS Sync Display Model (DISPLAY ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(m.get("verdict", "")))
    lines.append("- Display id: " + str(m.get("display_id")))
    lines.append("- Lane: " + str(m.get("lane")))
    lines.append("- Controls/buttons: NONE (forbidden by design)")
    lines.append("- Next required action: " + str(m.get("next_required_action", "")))
    lines.append("")
    blockers = m.get("blockers") or []
    if blockers:
        lines.append("## Blockers (refused; nothing is displayed)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    dash = m.get("dashboard_display")
    if isinstance(dash, dict):
        lines.append("## Dashboard panel (display only)")
        lines.append("- " + str(dash.get("panel_title")))
        lines.append("- " + str(dash.get("chain_state_line")))
        lines.append("- " + str(dash.get("report_summary")))
        lines.append("- " + str(dash.get("recommendation_display")))
        lines.append("- " + str(dash.get("human_action_needed_banner")))
        lines.append("")
    jarv = m.get("jarvis_display")
    if isinstance(jarv, dict):
        lines.append("## JARVIS status (spoken, display only)")
        lines.append("- " + str(jarv.get("status_sentence")))
        lines.append("- " + str(jarv.get("spoken_next_action")))
        lines.append("")
    lines.append("## Automation roadmap status")
    for row in m.get("automation_chain_display") or []:
        lines.append("- " + str(row.get("link")) + ": " + str(row.get("display"))
                     + (" [designed]" if row.get("built") else " [pending]"))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)

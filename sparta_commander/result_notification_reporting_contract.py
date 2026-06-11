"""SPARTA Result Notification / Reporting Contract (READ-ONLY, PAYLOAD ONLY).

Roadmap link L5 (build sequence seq 5) of the Strategy Factory Automation Roadmap:
how research-cycle outcomes are turned into SAFE, human-facing report payloads.

    idea -> intake -> adapter -> packet -> batch + ONE signature -> cycle SPEC
      -> THIS MODULE: cycle result -> safe report payload                [L5]
      -> dashboard / JARVIS / Telegram surfaces render it                [L6, future]

What this module produces: an in-memory PAYLOAD -- dashboard-ready fields,
JARVIS-ready fields, and Telegram-ready fields -- describing what happened in a
research cycle (a step finished, the cycle stopped, was refused, completed, or
needs a human). The payload may RECOMMEND the next safe command; it can never
issue it, and it always says a human action is needed.

What this module can never do (validator-enforced):
  - It is NOT a notifier. Nothing is sent: no Telegram message, no email, no
    webhook, no dashboard write. Every channel block carries
    payload_only_nothing_sent=True, and the module imports no transport library.
  - It refuses unsafe content: any text smelling of secrets, credentials,
    private keys, API keys, seed phrases, account balances, live order/position
    data, or trading instructions refuses the WHOLE report. A report about
    research can never become a leak channel or an execution channel.
  - No implied approval: a payload never claims a step was approved, never
    advances anything, and its recommendation is marked "recommendation only".
  - It runs nothing, fetches nothing, schedules nothing, unlocks nothing.

Public API:
  - REPORT_SCHEMA_VERSION / REPORT_LABEL / REPORT_MODE
  - ROADMAP_LINK_ID / ROADMAP_SEQ
  - VERDICT_REPORT_READY / VERDICT_REPORT_REFUSED
  - REPORT_STATES / RESULT_TYPES / FORBIDDEN_CONTENT_TOKENS
  - TELEGRAM_TEXT_MAX_CHARS / NEXT_REQUIRED_ACTION
  - get_result_notification_reporting_label()
  - build_result_report(cycle_spec, result_event)
  - validate_result_report(report)
  - render_result_report_markdown(report)
"""

from __future__ import annotations

import hashlib
from typing import Any

from sparta_commander.research_cycle_scheduler_spec_contract import (
    VERDICT_CYCLE_SPEC_READY,
    VERDICT_CYCLE_SPEC_REFUSED,
    validate_research_cycle_spec,
)

REPORT_SCHEMA_VERSION = "result_notification_reporting_contract.v1"
REPORT_LABEL = (
    "SPARTA Result Notification / Reporting (READ-ONLY, PAYLOAD ONLY, NOTHING SENT)"
)
REPORT_MODE = "RESEARCH_ONLY"

ROADMAP_LINK_ID = "L5_result_notification_reporting_layer"
ROADMAP_SEQ = 5

VERDICT_REPORT_READY = "RESULT_REPORT_READY_FOR_HUMAN"
VERDICT_REPORT_REFUSED = "RESULT_REPORT_REFUSED"

# The roadmap's seq 6 block: surfacing the automation state on dashboard/JARVIS.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_DASHBOARD_JARVIS_SYNC_DESIGN"

# CLOSED set of states a report can describe. No state celebrates, approves,
# or implies that anything will run next.
REPORT_STATES = (
    "REPORT_READY_FOR_HUMAN",
    "REPORT_REFUSED",
)

# CLOSED set of result types a cycle can report.
RESULT_TYPE_STEP_DONE = "step_done"
RESULT_TYPE_CYCLE_STOPPED = "cycle_stopped"
RESULT_TYPE_CYCLE_REFUSED = "cycle_refused"
RESULT_TYPE_CYCLE_COMPLETE = "cycle_complete"
RESULT_TYPE_HUMAN_REVIEW_REQUIRED = "human_review_required"
RESULT_TYPES = (
    RESULT_TYPE_STEP_DONE,
    RESULT_TYPE_CYCLE_STOPPED,
    RESULT_TYPE_CYCLE_REFUSED,
    RESULT_TYPE_CYCLE_COMPLETE,
    RESULT_TYPE_HUMAN_REVIEW_REQUIRED,
)

# Content screen: any of these tokens anywhere in report text refuses the WHOLE
# report. A research report can never carry secrets or live trading data.
FORBIDDEN_CONTENT_TOKENS = (
    "api key", "api_key", "apikey", "secret", "password", "passphrase",
    "private key", "seed phrase", "mnemonic", "credential", "bearer ",
    "account balance", "wallet balance", "order id", "order_id", "fill price",
    "open position", "live position", "place order", "execute trade",
    "buy now", "sell now",
)

TELEGRAM_TEXT_MAX_CHARS = 500


def get_result_notification_reporting_label() -> str:
    """Human label for the recognized result notification/reporting contract."""
    return REPORT_LABEL


def _report_id(cycle_id: Any, result_type: Any, summary: Any) -> str:
    """Stable report id. Pure."""
    seed = str(cycle_id) + "|" + str(result_type) + "|" + str(summary)
    return "report_" + hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def _find_forbidden_token(*texts: Any) -> str | None:
    """Return the first forbidden content token found in any text, else None."""
    joined = " ".join(str(t) for t in texts if t is not None).lower()
    for token in FORBIDDEN_CONTENT_TOKENS:
        if token in joined:
            return token
    return None


def _base_report() -> dict[str, Any]:
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "label": REPORT_LABEL,
        "mode": REPORT_MODE,
        "roadmap_link_id": ROADMAP_LINK_ID,
        "roadmap_seq": ROADMAP_SEQ,
        "verdict": None,
        "report_state": None,
        "blockers": [],
        "report_id": None,
        "cycle_id": None,
        "lane": None,
        "result_type": None,
        "step_seq": None,
        "summary": None,
        # Channel payloads -- shaped, never sent.
        "dashboard_payload": None,
        "jarvis_payload": None,
        "telegram_payload": None,
        # Constitution, stated structurally:
        "payload_only_nothing_sent": True,
        "report_sends_no_telegram": True,
        "report_sends_no_email": True,
        "report_writes_no_dashboard": True,
        "no_implied_approval_of_anything": True,
        "recommendation_is_suggestion_only": True,
        "human_action_needed": True,
        "report_is_in_memory_only": True,
        "human_review_required": True,
        "next_safe_command_recommendation": None,
        # Capability posture:
        "executes": False,
        "writes_files": False,
        "writes_queue": False,
        "writes_ledger": False,
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


def build_result_report(cycle_spec: Any, result_event: Any) -> dict[str, Any]:
    """Turn a cycle outcome into a safe, human-facing report PAYLOAD; refuse
    anything unsafe. PURE: never raises, never sends, never persists, never
    runs or advances anything."""
    report = _base_report()

    if not isinstance(cycle_spec, dict):
        report["verdict"] = VERDICT_REPORT_REFUSED
        report["report_state"] = "REPORT_REFUSED"
        report["blockers"].append("cycle_spec_missing_or_not_a_dict")
        return report

    spec_validation = validate_research_cycle_spec(cycle_spec)
    if not spec_validation.get("valid"):
        report["verdict"] = VERDICT_REPORT_REFUSED
        report["report_state"] = "REPORT_REFUSED"
        report["blockers"].append("cycle_spec_invalid")
        return report

    if not isinstance(result_event, dict):
        report["verdict"] = VERDICT_REPORT_REFUSED
        report["report_state"] = "REPORT_REFUSED"
        report["blockers"].append("result_event_missing_or_not_a_dict")
        return report

    result_type = result_event.get("result_type")
    if result_type not in RESULT_TYPES:
        report["verdict"] = VERDICT_REPORT_REFUSED
        report["report_state"] = "REPORT_REFUSED"
        report["blockers"].append("result_type_not_in_closed_set:" + str(result_type))
        return report

    spec_verdict = cycle_spec.get("verdict")
    if result_type == RESULT_TYPE_CYCLE_REFUSED:
        if spec_verdict != VERDICT_CYCLE_SPEC_REFUSED:
            report["verdict"] = VERDICT_REPORT_REFUSED
            report["report_state"] = "REPORT_REFUSED"
            report["blockers"].append("refusal_report_needs_a_refused_cycle_spec")
            return report
    else:
        if spec_verdict != VERDICT_CYCLE_SPEC_READY:
            report["verdict"] = VERDICT_REPORT_REFUSED
            report["report_state"] = "REPORT_REFUSED"
            report["blockers"].append("result_needs_a_ready_cycle_spec")
            return report

    summary = result_event.get("summary")
    if not summary or not str(summary).strip():
        report["verdict"] = VERDICT_REPORT_REFUSED
        report["report_state"] = "REPORT_REFUSED"
        report["blockers"].append("summary_missing")
        return report
    summary = str(summary).strip()

    step_seq = result_event.get("step_seq")
    if result_type == RESULT_TYPE_STEP_DONE:
        step_count = cycle_spec.get("step_count") or 0
        if not isinstance(step_seq, int) or not (1 <= step_seq <= step_count):
            report["verdict"] = VERDICT_REPORT_REFUSED
            report["report_state"] = "REPORT_REFUSED"
            report["blockers"].append("step_done_needs_a_valid_step_seq")
            return report

    recommendation = cycle_spec.get("next_safe_command_recommendation")
    token = _find_forbidden_token(summary, recommendation)
    if token is not None:
        report["verdict"] = VERDICT_REPORT_REFUSED
        report["report_state"] = "REPORT_REFUSED"
        report["blockers"].append("forbidden_content_token:" + token)
        return report

    cycle_id = cycle_spec.get("cycle_id")
    lane = cycle_spec.get("lane")
    status_line = (
        "research cycle " + str(result_type).replace("_", " ")
        + " | lane " + str(lane)
        + " | human action needed"
    )
    rec_text = (
        str(recommendation) if recommendation
        else "await a fresh human directive -- recommendation only"
    )
    telegram_text = (
        "[SPARTA research] " + status_line + " | " + summary
    )[:TELEGRAM_TEXT_MAX_CHARS]

    report["verdict"] = VERDICT_REPORT_READY
    report["report_state"] = "REPORT_READY_FOR_HUMAN"
    report["report_id"] = _report_id(cycle_id, result_type, summary)
    report["cycle_id"] = cycle_id
    report["lane"] = lane
    report["result_type"] = result_type
    report["step_seq"] = step_seq if result_type == RESULT_TYPE_STEP_DONE else None
    report["summary"] = summary
    report["next_safe_command_recommendation"] = rec_text
    report["dashboard_payload"] = {
        "title": "Research cycle update: " + str(result_type),
        "lane": lane,
        "cycle_id": cycle_id,
        "result_type": result_type,
        "status_line": status_line,
        "summary": summary,
        "next_safe_command_recommendation": rec_text,
        "human_action_needed": True,
        "payload_only_nothing_sent": True,
    }
    report["jarvis_payload"] = {
        "spoken_summary": (
            "A research cycle update is waiting for you: " + status_line
            + ". No performance claims; no action was taken."
        ),
        "result_type": result_type,
        "human_action_needed": True,
        "contains_no_performance_claims": True,
        "payload_only_nothing_sent": True,
    }
    report["telegram_payload"] = {
        "text": telegram_text,
        "max_chars": TELEGRAM_TEXT_MAX_CHARS,
        "human_action_needed": True,
        "payload_only_not_sent": True,
        "send_requires_separate_human_approved_transport": True,
    }
    return report


def validate_result_report(report: Any) -> dict[str, Any]:
    """Validate (read-only) a report payload's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {"valid": False, "errors": ["report_not_a_dict"]}
    r = report

    verdict = r.get("verdict")
    if verdict not in (VERDICT_REPORT_READY, VERDICT_REPORT_REFUSED):
        errors.append("bad_verdict")
    if r.get("report_state") not in REPORT_STATES:
        errors.append("report_state_outside_closed_set")

    if verdict == VERDICT_REPORT_REFUSED:
        if not r.get("blockers"):
            errors.append("refused_report_without_blockers")
        for ch in ("dashboard_payload", "jarvis_payload", "telegram_payload"):
            if r.get(ch) is not None:
                errors.append("refused_report_carries_payload:" + ch)

    if verdict == VERDICT_REPORT_READY:
        if r.get("blockers"):
            errors.append("ready_report_carries_blockers")
        if r.get("result_type") not in RESULT_TYPES:
            errors.append("result_type_outside_closed_set")
        if not r.get("report_id"):
            errors.append("ready_report_without_id")
        token = _find_forbidden_token(
            r.get("summary"), r.get("next_safe_command_recommendation"))
        if token is not None:
            errors.append("forbidden_content_in_report:" + token)
        dash = r.get("dashboard_payload")
        jarv = r.get("jarvis_payload")
        tele = r.get("telegram_payload")
        if not isinstance(dash, dict) or dash.get("human_action_needed") is not True:
            errors.append("dashboard_payload_missing_or_no_human_action")
        if not isinstance(jarv, dict):
            errors.append("jarvis_payload_missing")
        elif jarv.get("contains_no_performance_claims") is not True:
            errors.append("jarvis_payload_allows_performance_claims")
        if not isinstance(tele, dict):
            errors.append("telegram_payload_missing")
        else:
            if tele.get("payload_only_not_sent") is not True:
                errors.append("telegram_payload_claims_sent")
            if tele.get(
                "send_requires_separate_human_approved_transport"
            ) is not True:
                errors.append("telegram_transport_boundary_dropped")
            text = tele.get("text")
            if not text or len(str(text)) > TELEGRAM_TEXT_MAX_CHARS:
                errors.append("telegram_text_missing_or_too_long")
            if _find_forbidden_token(text) is not None:
                errors.append("forbidden_content_in_telegram_text")
        for ch, payload in (("dashboard", dash), ("jarvis", jarv)):
            if isinstance(payload, dict) and _find_forbidden_token(
                *payload.values()
            ) is not None:
                errors.append("forbidden_content_in_" + ch + "_payload")
        rec = r.get("next_safe_command_recommendation")
        if not rec or "recommendation only" not in str(rec).lower():
            errors.append("recommendation_missing_or_not_marked_suggestion_only")

    # Constitution invariants.
    for key, err in (
        ("payload_only_nothing_sent", "report_claims_to_send"),
        ("report_sends_no_telegram", "telegram_send_claimed"),
        ("report_sends_no_email", "email_send_claimed"),
        ("report_writes_no_dashboard", "dashboard_write_claimed"),
        ("no_implied_approval_of_anything", "implied_approval_allowed"),
        ("recommendation_is_suggestion_only", "recommendation_not_suggestion_only"),
        ("human_action_needed", "human_action_dropped"),
        ("report_is_in_memory_only", "report_not_in_memory_only"),
        ("human_review_required", "human_review_dropped"),
    ):
        if r.get(key) is not True:
            errors.append(err)

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if r.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "writes_queue",
        "writes_ledger",
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
        if r.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_result_report_markdown(report: Any) -> str:
    """Render a report payload as deterministic markdown. Pure string work."""
    r = report if isinstance(report, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Research Result Report (PAYLOAD ONLY, NOTHING SENT)")
    lines.append("")
    lines.append("- Verdict: " + str(r.get("verdict", "")))
    lines.append("- Report id: " + str(r.get("report_id")))
    lines.append("- Cycle: " + str(r.get("cycle_id")) + " | Lane: " + str(r.get("lane")))
    lines.append("- Result type: " + str(r.get("result_type")))
    lines.append("- Human action needed: " + str(r.get("human_action_needed", "")))
    lines.append("- Next required action: " + str(r.get("next_required_action", "")))
    lines.append("")
    blockers = r.get("blockers") or []
    if blockers:
        lines.append("## Blockers (refused; no payload exists)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    if r.get("summary"):
        lines.append("## Summary")
        lines.append("- " + str(r.get("summary")))
        lines.append("")
        lines.append("## Recommendation (suggestion only, human must issue it)")
        lines.append("- " + str(r.get("next_safe_command_recommendation")))
        lines.append("")
        tele = r.get("telegram_payload") or {}
        lines.append("## Telegram-ready text (payload only, NOT sent)")
        lines.append("- " + str(tele.get("text")))
        lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)

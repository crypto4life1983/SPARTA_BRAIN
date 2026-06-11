"""SPARTA Arbitrage Factory V1 - ALERT / REPORT SCHEMA Contract (READ-ONLY).

Roadmap seq 4 of the Arbitrage Factory V1 lane: the FROZEN shape of every
research alert and report the future scanner may ever emit. The lane's whole
output surface is defined here -- and it is alerts and reports ONLY.

An ALERT RECORD is one fully-costed research observation:
    alert_id, timestamp_utc, family_id, symbol, venue(s),
    gross_edge_bps + the full cost breakdown (taker fee, spread, slippage,
    funding adjustment, withdrawal amortization), net_edge_bps,
    verdict (PASS / WATCH / FAIL), data_staleness_days, evidence_label,
    and the mandatory human flags.

Honesty is enforced STRUCTURALLY (validator-enforced):
  - The verdict on an alert MUST equal the seq-3 model's own classification of
    its net edge -- an alert cannot say PASS while the model says FAIL.
  - The net edge MUST equal gross minus every cost in the breakdown; a report
    cannot quietly drop a cost.
  - Every alert carries alert_is_research_only_not_a_trade_signal=True and
    human_action_needed=True, plus the mandatory disclaimer line.
  - Forbidden content (credentials, account/wallet/balance data, order/fill/
    position fields, trade instructions like "buy now"/"place order") refuses
    the WHOLE alert.
  - Reports may only ever live under reports/arbitrage_factory_v1/ (aligned
    with the seq-1 scanner spec), one report per human-approved run,
    append-only -- and THIS module still writes nothing: it is the schema.

Public API:
  - REPORT_SCHEMA_VERSION / REPORT_SCHEMA_LABEL / REPORT_SCHEMA_MODE
  - VERDICT_REPORT_SCHEMA_READY / VERDICT_REPORT_SCHEMA_BLOCKED
  - ALERT_VERDICT_STATES / ALERT_REQUIRED_FIELDS / ALERT_COST_FIELDS
  - REPORT_FILE_RULES / FORBIDDEN_ALERT_CONTENT / MANDATORY_DISCLAIMER
  - REPORTS_ROOT / NEXT_REQUIRED_ACTION
  - get_arbitrage_alert_report_schema_label()
  - record_arbitrage_alert_report_schema(fee_slippage_model)
  - build_arbitrage_alert_report_schema()
  - validate_arbitrage_alert_report_schema(schema)
  - validate_alert_record(record)
  - render_arbitrage_alert_report_schema_markdown(schema)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.arbitrage_data_contract import (
    ALLOWED_SYMBOLS,
    ALLOWED_VENUE_LABELS,
    FORBIDDEN_FIELD_TOKENS,
)
from sparta_commander.arbitrage_fee_slippage_model_contract import (
    VERDICT_MODEL_READY,
    build_arbitrage_fee_slippage_model,
    classify_net_edge,
    validate_arbitrage_fee_slippage_model,
)

REPORT_SCHEMA_VERSION = "arbitrage_alert_report_schema_contract.v1"
REPORT_SCHEMA_LABEL = (
    "SPARTA Arbitrage Factory V1 Alert/Report Schema (READ-ONLY, SCHEMA ONLY)"
)
REPORT_SCHEMA_MODE = "RESEARCH_ONLY"

VERDICT_REPORT_SCHEMA_READY = "ARBITRAGE_ALERT_REPORT_SCHEMA_READY"
VERDICT_REPORT_SCHEMA_BLOCKED = "ARBITRAGE_ALERT_REPORT_SCHEMA_BLOCKED"

# Roadmap seq 5: the lane review contract, under its own human approval.
NEXT_REQUIRED_ACTION = "HUMAN_APPROVED_LANE_REVIEW_CONTRACT"

# Aligned with the seq-1 scanner spec's output surface.
REPORTS_ROOT = "reports/arbitrage_factory_v1/"

ALERT_VERDICT_STATES = ("PASS", "WATCH", "FAIL")

# The cost breakdown every alert must carry (mirrors the seq-3 model formula).
ALERT_COST_FIELDS = (
    "taker_fee_bps",
    "spread_cost_bps",
    "slippage_bps",
    "funding_adjustment_bps",
    "withdrawal_amortization_bps",
)

ALERT_REQUIRED_FIELDS = (
    "alert_id",
    "timestamp_utc",
    "family_id",
    "symbol",
    "venues",
    "gross_edge_bps",
) + ALERT_COST_FIELDS + (
    "net_edge_bps",
    "verdict",
    "data_staleness_days",
    "evidence_label",
    "summary",
    "alert_is_research_only_not_a_trade_signal",
    "human_action_needed",
    "disclaimer",
)

MANDATORY_DISCLAIMER = (
    "research alert only - not financial advice - no trade signal - "
    "human review required"
)

# Content screen: account/credential/order/position tokens (from the seq-2
# data contract) plus trade-instruction language. One hit refuses the alert.
FORBIDDEN_ALERT_CONTENT = FORBIDDEN_FIELD_TOKENS + (
    "buy now", "sell now", "place order", "execute trade", "go long",
    "go short", "enter position", "use leverage",
)

REPORT_FILE_RULES = (
    "reports_live_only_under_reports_arbitrage_factory_v1",
    "one_report_per_human_approved_run_no_continuous_streams",
    "reports_are_append_only_existing_reports_are_never_modified",
    "every_report_carries_the_mandatory_disclaimer_verbatim",
    "every_alert_verdict_must_equal_the_seq3_model_classification",
    "every_net_edge_must_equal_gross_minus_the_full_cost_breakdown",
    "blocked_or_refused_runs_write_nothing",
)


def get_arbitrage_alert_report_schema_label() -> str:
    """Human label for the recognized alert/report schema contract."""
    return REPORT_SCHEMA_LABEL


def _find_forbidden_content(*texts: Any) -> str | None:
    """Return the first forbidden content token found in any text, else None."""
    joined = " ".join(str(t) for t in texts if t is not None).lower()
    for token in FORBIDDEN_ALERT_CONTENT:
        if token in joined:
            return token
    return None


def validate_alert_record(record: Any) -> dict[str, Any]:
    """Validate (read-only, in-memory) ONE proposed alert record against the
    frozen schema. Reads no file, writes no file. Never raises.
    Returns {"acceptable": bool, "errors": [...]}."""
    errors: list[str] = []
    if not isinstance(record, dict):
        return {"acceptable": False, "errors": ["record_not_a_dict"]}

    for field in ALERT_REQUIRED_FIELDS:
        if field not in record:
            errors.append("missing_required_field:" + field)
    if errors:
        return {"acceptable": False, "errors": errors}

    # Forbidden content screen FIRST: a poisoned alert is refused whole.
    token = _find_forbidden_content(
        record.get("summary"), record.get("evidence_label"),
        record.get("alert_id"), record.get("family_id"))
    if token is not None:
        return {"acceptable": False,
                "errors": ["forbidden_alert_content:" + token]}
    for key in record:
        lowered = str(key).lower()
        for bad in FORBIDDEN_FIELD_TOKENS:
            if bad in lowered:
                return {"acceptable": False,
                        "errors": ["forbidden_alert_field:" + str(key)]}

    if record.get("verdict") not in ALERT_VERDICT_STATES:
        errors.append("verdict_outside_closed_set")

    if record.get("symbol") not in ALLOWED_SYMBOLS:
        errors.append("symbol_not_in_allowed_labels")
    venues = record.get("venues")
    if not isinstance(venues, (list, tuple)) or not venues or not all(
        v in ALLOWED_VENUE_LABELS for v in venues
    ):
        errors.append("venues_not_in_allowed_labels")

    numeric_fields = ("gross_edge_bps", "net_edge_bps") + ALERT_COST_FIELDS
    values: dict[str, float] = {}
    for name in numeric_fields:
        raw = record.get(name)
        if not isinstance(raw, (int, float)) or isinstance(raw, bool):
            errors.append("non_numeric:" + name)
        else:
            values[name] = float(raw)
    if not errors:
        # Honesty check 1: net edge equals gross minus every cost.
        expected_net = (
            values["gross_edge_bps"]
            - 2.0 * values["taker_fee_bps"]
            - values["spread_cost_bps"]
            - values["slippage_bps"]
            - values["funding_adjustment_bps"]
            - values["withdrawal_amortization_bps"]
        )
        if abs(expected_net - values["net_edge_bps"]) > 1e-9:
            errors.append("net_edge_does_not_match_cost_breakdown")
        # Honesty check 2: the verdict equals the seq-3 model classification.
        if record.get("verdict") != classify_net_edge(values["net_edge_bps"]):
            errors.append("verdict_disagrees_with_seq3_model_classification")

    staleness = record.get("data_staleness_days")
    if not isinstance(staleness, (int, float)) or isinstance(staleness, bool) or (
        staleness < 0
    ):
        errors.append("staleness_missing_or_negative")

    if record.get("alert_is_research_only_not_a_trade_signal") is not True:
        errors.append("research_only_flag_dropped")
    if record.get("human_action_needed") is not True:
        errors.append("human_action_flag_dropped")
    if record.get("disclaimer") != MANDATORY_DISCLAIMER:
        errors.append("disclaimer_missing_or_altered")

    return {"acceptable": not errors, "errors": errors}


def _base_schema() -> dict[str, Any]:
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "label": REPORT_SCHEMA_LABEL,
        "mode": REPORT_SCHEMA_MODE,
        "lane": "arbitrage_factory_v1",
        "roadmap_seq": 4,
        "verdict": None,
        "blockers": [],
        "fee_slippage_model_verdict": None,
        "reports_root": REPORTS_ROOT,
        "alert_verdict_states": list(ALERT_VERDICT_STATES),
        "alert_required_fields": list(ALERT_REQUIRED_FIELDS),
        "alert_cost_fields": list(ALERT_COST_FIELDS),
        "report_file_rules": list(REPORT_FILE_RULES),
        "forbidden_alert_content": list(FORBIDDEN_ALERT_CONTENT),
        "mandatory_disclaimer": MANDATORY_DISCLAIMER,
        # Constitution, stated structurally:
        "alerts_are_research_only_never_trade_signals": True,
        "verdicts_must_agree_with_seq3_model": True,
        "net_edge_must_match_cost_breakdown": True,
        "schema_writes_no_reports": True,
        "output_is_schema_readiness_only": True,
        "human_review_required": True,
        # Capability posture:
        "executes": False,
        "writes_files": False,
        "writes_reports": False,
        "sends_notifications": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
        "starts_scheduler": False,
        "starts_daemon": False,
        "starts_background_worker": False,
        "runs_loop": False,
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


def record_arbitrage_alert_report_schema(fee_slippage_model: Any) -> dict[str, Any]:
    """Record the alert/report schema, gated on a READY, valid seq-3
    fee/slippage model. PURE: never raises, writes nothing."""
    schema = _base_schema()

    if not isinstance(fee_slippage_model, dict):
        schema["verdict"] = VERDICT_REPORT_SCHEMA_BLOCKED
        schema["blockers"].append("fee_slippage_model_missing")
        return schema

    validation = validate_arbitrage_fee_slippage_model(fee_slippage_model)
    if not validation.get("valid"):
        schema["verdict"] = VERDICT_REPORT_SCHEMA_BLOCKED
        schema["blockers"].append("fee_slippage_model_invalid")
        return schema

    if fee_slippage_model.get("verdict") != VERDICT_MODEL_READY:
        schema["verdict"] = VERDICT_REPORT_SCHEMA_BLOCKED
        schema["blockers"].append("fee_slippage_model_not_ready")
        return schema

    schema["verdict"] = VERDICT_REPORT_SCHEMA_READY
    schema["fee_slippage_model_verdict"] = fee_slippage_model.get("verdict")
    return schema


def build_arbitrage_alert_report_schema() -> dict[str, Any]:
    """Build the schema against the real seq 0 -> 1 -> 2 -> 3 chain. Pure."""
    return record_arbitrage_alert_report_schema(
        build_arbitrage_fee_slippage_model())


def validate_arbitrage_alert_report_schema(schema: Any) -> dict[str, Any]:
    """Validate (read-only) the schema contract's shape and safety invariants.
    Returns {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(schema, dict):
        return {"valid": False, "errors": ["schema_not_a_dict"]}
    s = schema

    verdict = s.get("verdict")
    if verdict not in (VERDICT_REPORT_SCHEMA_READY, VERDICT_REPORT_SCHEMA_BLOCKED):
        errors.append("bad_verdict")
    if verdict == VERDICT_REPORT_SCHEMA_BLOCKED and not s.get("blockers"):
        errors.append("blocked_without_blockers")
    if verdict == VERDICT_REPORT_SCHEMA_READY:
        if s.get("blockers"):
            errors.append("ready_with_blockers")
        if s.get("fee_slippage_model_verdict") != VERDICT_MODEL_READY:
            errors.append("ready_without_ready_model")

    if s.get("lane") != "arbitrage_factory_v1":
        errors.append("wrong_lane")
    if s.get("roadmap_seq") != 4:
        errors.append("wrong_roadmap_seq")
    if s.get("reports_root") != REPORTS_ROOT:
        errors.append("reports_root_moved")

    if tuple(s.get("alert_verdict_states") or ()) != ALERT_VERDICT_STATES:
        errors.append("verdict_states_tampered")
    if tuple(s.get("alert_required_fields") or ()) != ALERT_REQUIRED_FIELDS:
        errors.append("required_fields_tampered")
    if tuple(s.get("alert_cost_fields") or ()) != ALERT_COST_FIELDS:
        errors.append("cost_fields_tampered")
    if tuple(s.get("report_file_rules") or ()) != REPORT_FILE_RULES:
        errors.append("file_rules_tampered")
    if tuple(s.get("forbidden_alert_content") or ()) != FORBIDDEN_ALERT_CONTENT:
        errors.append("forbidden_content_weakened")
    if s.get("mandatory_disclaimer") != MANDATORY_DISCLAIMER:
        errors.append("disclaimer_tampered")

    for key, err in (
        ("alerts_are_research_only_never_trade_signals", "trade_signal_allowed"),
        ("verdicts_must_agree_with_seq3_model", "model_agreement_dropped"),
        ("net_edge_must_match_cost_breakdown", "cost_breakdown_check_dropped"),
        ("schema_writes_no_reports", "schema_writes_reports"),
        ("output_is_schema_readiness_only", "output_overclaims"),
        ("human_review_required", "human_review_dropped"),
    ):
        if s.get(key) is not True:
            errors.append(err)

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if s.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "writes_reports",
        "sends_notifications",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
        "starts_scheduler",
        "starts_daemon",
        "starts_background_worker",
        "runs_loop",
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
        if s.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_arbitrage_alert_report_schema_markdown(schema: Any) -> str:
    """Render the schema contract as deterministic markdown. Pure string work."""
    s = schema if isinstance(schema, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Arbitrage Factory V1 Alert/Report Schema (SCHEMA ONLY)")
    lines.append("")
    lines.append("- Verdict: " + str(s.get("verdict", "")))
    lines.append("- Lane: " + str(s.get("lane", "")) + " (roadmap seq "
                 + str(s.get("roadmap_seq", "")) + ")")
    lines.append("- Alerts are research only, NEVER trade signals")
    lines.append("- Reports live only under " + str(s.get("reports_root")))
    lines.append("- Next required action: " + str(s.get("next_required_action", "")))
    lines.append("")
    blockers = s.get("blockers") or []
    if blockers:
        lines.append("## Blockers (BLOCKED defines nothing usable)")
        for b in blockers:
            lines.append("- " + str(b))
        lines.append("")
    lines.append("## Alert verdict states (closed)")
    lines.append("- " + ", ".join(s.get("alert_verdict_states") or []))
    lines.append("")
    lines.append("## Alert record fields (all required)")
    lines.append("- " + ", ".join(s.get("alert_required_fields") or []))
    lines.append("")
    lines.append("## Report file rules")
    for r in s.get("report_file_rules") or []:
        lines.append("- " + str(r))
    lines.append("")
    lines.append("## Mandatory disclaimer (verbatim on every report)")
    lines.append("- " + str(s.get("mandatory_disclaimer")))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)

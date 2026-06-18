"""H4 discretionary trend-following — RESEARCH BACKLOG NOTE (PURE, RESEARCH ONLY).

A research-only BACKLOG SEED note -- NOT a candidate proposal. It records, for
possible FUTURE research, a discretionary trend-following / trend-continuation /
add-to-winners concept OBSERVED from a profitable trader. It assigns NO candidate
number (no C18), enters NO candidate lifecycle, and creates nothing: no detector,
no labels, no replay, no data fetch, no optimization, no trading code.

It is a pure, in-memory record: it DECLARES the observed setup (H4 timeframe,
BTCUSD + XAUUSD instruments, the trader's qualitative claims), a list of possible
objective families to test LATER, and the evidence bar required BEFORE this seed
could ever be promoted to a candidate (3-5 annotated chart examples). Status is
pinned BACKLOG_ONLY_NOT_CANDIDATE. Every capability flag is False with a full
scope_locks set. Promotion to a candidate needs an explicit, separate human
decision -- this note can never promote itself.

NOTE: the observed instruments include XAUUSD (gold), which is OUTSIDE the current
crypto-D1 research lane; this is recorded as an observation only, not a commitment
to trade or test gold.
"""
from __future__ import annotations

from typing import Any

NOTE_SCHEMA_VERSION = 1
NOTE_MODE = "RESEARCH_ONLY"
NOTE_KIND = "research_backlog_note"

NOTE_ID = "BACKLOG_H4_DISCRETIONARY_TREND_FOLLOWING_V1"
NOTE_TITLE = ("H4 discretionary trend-following / trend-continuation / "
              "add-to-winners (observed from a profitable trader)")
STATUS = "BACKLOG_ONLY_NOT_CANDIDATE_YET"

# --- the observation --------------------------------------------------------
OBSERVED_TIMEFRAME = "H4"
OBSERVED_INSTRUMENTS = ("BTCUSD", "XAUUSD")
TRADER_CLAIMS = (
    "uses no indicators",
    "follows the trend",
    "is patient",
    "does not overtrade",
    "adds to winners",
)
# evidence currently on hand is only the observed screenshots/conversation --
# there are NO direct annotated chart examples yet.
EVIDENCE_SOURCE = ("observed screenshots/conversation only, no direct chart "
                   "examples available")
CHART_EXAMPLES_CURRENTLY_AVAILABLE = 0

# --- possible objective families to test LATER (declared, not built) --------
POSSIBLE_OBJECTIVE_FAMILIES = (
    "H4 market-structure trend continuation",
    "H4 breakout-and-retest continuation",
    "H4 pullback in trend",
    "H4 pyramiding / add-to-winners",
    "Daily trend filter + H4 entry",
    "BTC/XAU strong-trend regime filter",
)

# --- evidence bar required BEFORE promotion to a candidate ------------------
REQUIRED_EVIDENCE_BEFORE_PROMOTION = (
    "3-5 annotated chart examples, each showing the entry, the stop, the "
    "add-to-winner points, and the exit")
MIN_CHART_EXAMPLES = 3
MAX_CHART_EXAMPLES = 5

NEXT_REQUIRED_ACTION = (
    "NONE__BACKLOG_ONLY__REQUIRES_EXPLICIT_HUMAN_DECISION_TO_PROMOTE_TO_CANDIDATE_"
    "WITH_3_TO_5_ANNOTATED_CHART_EXAMPLES")

_CAPABILITY_FLAGS_FALSE = (
    "executes", "writes_files", "is_candidate", "assigns_candidate_number",
    "enters_candidate_lifecycle", "builds_proposal", "builds_spec",
    "builds_detector", "runs_detector", "runs_labels", "runs_replay",
    "runs_backtest", "computes_pnl", "optimizes_parameters", "fetches_data",
    "reads_real_data", "mutates_data", "stages_data", "auto_commits", "auto_pushes",
    "modifies_scheduler", "sends_notifications", "calls_api", "uses_network",
    "uses_credentials", "connects_broker", "connects_exchange", "uses_real_money",
    "places_orders", "contains_order_logic", "paper_trading", "live_trading",
    "deploys_capital", "promotes_to_candidate", "advances_without_human_approval",
    "claims_profitability", "claims_edge", "crosses_into_forbidden_gate",
)


def get_h4_backlog_note_label() -> str:
    return (
        "H4 discretionary trend-following research BACKLOG NOTE (READ-ONLY, RESEARCH "
        "ONLY). A FUTURE research seed observed from a profitable trader -- NOT a "
        "candidate, NO C18 assigned, NO detector / labels / replay / data fetch / "
        "optimization / trading. Requires 3-5 annotated chart examples (entry / stop "
        "/ add / exit) before it could ever be promoted to a candidate, which needs "
        "an explicit human decision. NOT a profitability claim.")


def get_h4_backlog_note_next_action() -> str:
    return NEXT_REQUIRED_ACTION


def build_h4_backlog_note() -> dict[str, Any]:
    """Assemble the frozen H4 discretionary trend-following research backlog note.
    Pure; no I/O; backlog-note only. Assigns no candidate number; promotes
    nothing."""
    record: dict[str, Any] = {
        "schema_version": NOTE_SCHEMA_VERSION, "mode": NOTE_MODE, "kind": NOTE_KIND,
        "label": get_h4_backlog_note_label(),
        "note_id": NOTE_ID, "title": NOTE_TITLE,
        "is_research_backlog_note_only": True,
        "status": STATUS,
        "is_candidate": False,
        "candidate_number_assigned": None,
        "no_c18_assigned": True,
        # the observation
        "observed_timeframe": OBSERVED_TIMEFRAME,
        "observed_instruments": list(OBSERVED_INSTRUMENTS),
        "trader_claims": list(TRADER_CLAIMS),
        "style": ("no indicators, trend-following, patience, do not overtrade, "
                  "add to winners"),
        "observation_source": "profitable_trader_observed_claims_external_unverified",
        "evidence_source": EVIDENCE_SOURCE,
        "chart_examples_currently_available": CHART_EXAMPLES_CURRENTLY_AVAILABLE,
        "claims_are_unverified": True,
        # possible objective families to test later
        "possible_objective_families": list(POSSIBLE_OBJECTIVE_FAMILIES),
        "objective_families_are_declared_not_built": True,
        # evidence bar before promotion (NOT yet met -- no chart examples on hand)
        "required_evidence_before_promotion": REQUIRED_EVIDENCE_BEFORE_PROMOTION,
        "min_chart_examples": MIN_CHART_EXAMPLES,
        "max_chart_examples": MAX_CHART_EXAMPLES,
        "evidence_bar_met": False,
        "promotion_requires_explicit_human_decision": True,
        # scope notes
        "xauusd_outside_crypto_d1_lane": True,
        "recorded_as_observation_only": True,
        "human_review_required": True,
        "current_loop_stage": "research_backlog_note",
        "next_required_action": NEXT_REQUIRED_ACTION,
    }
    for flag in _CAPABILITY_FLAGS_FALSE:
        record[flag] = False
    record["scope_locks"] = {
        "no_execute": True, "no_write": True, "no_candidate_creation": True,
        "no_candidate_number_assignment": True, "no_lifecycle_entry": True,
        "no_proposal": True, "no_spec": True, "no_detector": True,
        "no_labels": True, "no_replay": True, "no_backtest": True, "no_pnl": True,
        "no_optimization": True, "no_data_fetch": True, "no_real_data_access": True,
        "no_stage": True, "no_commit": True, "no_push": True, "no_broker": True,
        "no_credentials": True, "no_order_logic": True, "no_paper_trading": True,
        "no_live_trading": True, "no_promotion_without_human": True,
        "no_profitability_claim": True, "no_crossing_into_forbidden_gate": True,
    }
    return record


def validate_h4_backlog_note(record: dict[str, Any]) -> dict[str, Any]:
    """Anti-tamper validator. Valid only when the note is research-only,
    backlog-note-only, status BACKLOG_ONLY_NOT_CANDIDATE with NO candidate number
    (no C18), records the observed H4 / BTCUSD+XAUUSD setup + the trader claims +
    the possible objective families + the 3-5-chart evidence bar, keeps promotion
    human-gated, and pins every capability flag False."""
    failures: list = []
    if record.get("mode") != NOTE_MODE:
        failures.append("mode_not_research_only")
    if record.get("kind") != NOTE_KIND:
        failures.append("kind_not_backlog_note")
    if record.get("is_research_backlog_note_only") is not True:
        failures.append("not_backlog_note_only")
    if record.get("status") != STATUS:
        failures.append("status_not_backlog_only_not_candidate")

    # explicitly NOT a candidate; no C18 assigned
    if record.get("is_candidate") is not False:
        failures.append("must_not_be_candidate")
    if record.get("candidate_number_assigned") is not None:
        failures.append("candidate_number_must_be_none")
    if record.get("no_c18_assigned") is not True:
        failures.append("c18_must_not_be_assigned")

    # the observation present + correct
    if record.get("observed_timeframe") != "H4":
        failures.append("timeframe_not_h4")
    if list(record.get("observed_instruments") or []) != ["BTCUSD", "XAUUSD"]:
        failures.append("instruments_not_btc_xau")
    claims = record.get("trader_claims") or []
    if len(claims) < 5:
        failures.append("trader_claims_incomplete")
    claims_blob = " || ".join(claims).lower()
    for must in ("trend", "overtrade", "patient", "add"):
        if must not in claims_blob:
            failures.append("claim_missing_%s" % must)
    if record.get("claims_are_unverified") is not True:
        failures.append("claims_must_be_unverified")
    # evidence source is screenshots/conversation only; no chart examples yet
    if not record.get("evidence_source"):
        failures.append("evidence_source_missing")
    if record.get("chart_examples_currently_available") != 0:
        failures.append("chart_examples_should_be_zero")

    # possible objective families (the 6)
    fams = record.get("possible_objective_families") or []
    if len(fams) < 6:
        failures.append("objective_families_incomplete")
    fam_blob = " || ".join(fams).lower()
    for must in ("trend continuation", "breakout-and-retest", "pullback",
                 "add-to-winners", "daily trend filter", "btc/xau"):
        if must not in fam_blob:
            failures.append("objective_family_missing_%s" % must.split()[0])

    # evidence bar before promotion -- declared but NOT yet met
    if not record.get("required_evidence_before_promotion"):
        failures.append("evidence_bar_missing")
    if record.get("min_chart_examples") != 3:
        failures.append("min_charts_not_3")
    if record.get("max_chart_examples") != 5:
        failures.append("max_charts_not_5")
    if "entry" not in str(record.get("required_evidence_before_promotion")).lower():
        failures.append("evidence_missing_entry")
    if record.get("evidence_bar_met") is not False:
        failures.append("evidence_bar_must_not_be_met_yet")
    if record.get("promotion_requires_explicit_human_decision") is not True:
        failures.append("promotion_not_human_gated")
    if record.get("next_required_action") != NEXT_REQUIRED_ACTION:
        failures.append("next_action_not_backlog_only")

    locks = record.get("scope_locks") or {}
    for key in ("no_execute", "no_candidate_creation",
                "no_candidate_number_assignment", "no_lifecycle_entry",
                "no_detector", "no_labels", "no_replay", "no_pnl",
                "no_optimization", "no_data_fetch", "no_commit", "no_push",
                "no_broker", "no_order_logic", "no_paper_trading",
                "no_live_trading", "no_promotion_without_human"):
        if locks.get(key) is not True:
            failures.append("scope_lock_false_%s" % key)
    for flag in _CAPABILITY_FLAGS_FALSE:
        if record.get(flag) is not False:
            failures.append("capability_flag_true_%s" % flag)

    return {"valid": not failures, "failures": failures}

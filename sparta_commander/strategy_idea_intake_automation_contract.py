"""SPARTA Strategy Idea Intake Automation Contract (READ-ONLY, TRIAGE ONLY).

A PURE, stdlib-only, read-only module that is the automated FRONT DOOR for new strategy
ideas: the operator describes an idea, and the system answers YES / NO / MAYBE, routes it
to the right research lane, and suggests the NEXT SAFE COMMAND -- a suggestion only,
which the human must still issue explicitly. The intake itself starts no work, runs no
research, fetches nothing, and unlocks nothing.

Triage is DETERMINISTIC and RULES-BASED (keyword classification over the idea text plus
explicit structured flags). The rules encode the standing SPARTA constitution and the
lessons of the sealed Crypto-D1 Blocks 175->190 arc:

  - HARD NO (rejected): ideas that require order execution, live/paper/micro-live
    trading, exchange credentials, autonomous trading bots, private/authenticated data,
    or re-mining the already-consumed Crypto-D1 evidence windows; and ideas pitched as
    guaranteed/riskless profit.
  - YES (researchable now): research-only ideas that fit an EXISTING lane --
    * arbitrage_factory_v1 (funding/basis/spread/cross-exchange research, alerts only),
    * crypto_d1 (ONLY as fresh-evidence work under the frozen Block 190 rulebook);
    each YES carries the lane, the matched family/track, and the next safe command.
  - MAYBE (needs human clarification): everything else -- the answer lists the exact
    clarifying questions a human must resolve before the idea can be re-triaged.

Every decision carries ``human_review_required=True`` and
``intake_starts_no_work=True``: the suggested command is a proposal, never an action.

Public API:
  - INTAKE_SCHEMA_VERSION / INTAKE_LABEL / INTAKE_MODE
  - ANSWER_YES / ANSWER_NO / ANSWER_MAYBE
  - LANE_ARBITRAGE / LANE_CRYPTO_D1 / LANE_NEW_REQUIRED / KNOWN_LANES
  - NEXT_REQUIRED_ACTION
  - get_strategy_idea_intake_label()
  - intake_strategy_idea(idea)
  - validate_intake_decision(decision)
  - render_intake_decision_markdown(decision)
"""

from __future__ import annotations

from typing import Any

INTAKE_SCHEMA_VERSION = "strategy_idea_intake_automation_contract.v1"
INTAKE_LABEL = "SPARTA Strategy Idea Intake Automation (READ-ONLY, TRIAGE ONLY)"
INTAKE_MODE = "RESEARCH_ONLY"

ANSWER_YES = "YES_RESEARCHABLE_NOW"
ANSWER_NO = "NO_REJECTED"
ANSWER_MAYBE = "MAYBE_NEEDS_HUMAN_CLARIFICATION"

LANE_ARBITRAGE = "arbitrage_factory_v1"
LANE_CRYPTO_D1 = "crypto_d1"
LANE_NEW_REQUIRED = "new_lane_required"
KNOWN_LANES: tuple[str, ...] = (LANE_ARBITRAGE, LANE_CRYPTO_D1, LANE_NEW_REQUIRED)

# After any intake decision the only next step is a human reviewing it; the suggested
# command is a proposal the human must issue explicitly.
NEXT_REQUIRED_ACTION = "HUMAN_REVIEW_OF_INTAKE_DECISION"

# --- hard-NO keyword classes (execution / credentials / private data / hype) ---
_EXECUTION_KEYWORDS = (
    "place order", "place orders", "execute trade", "execute trades", "auto-trade",
    "autotrade", "auto trade", "live trade", "live trading", "go live",
    "micro-live", "micro live", "paper trade", "paper trading", "trading bot that trades",
    "submit order", "market order", "limit order", "fill order", "take the trade",
)
_CREDENTIAL_KEYWORDS = (
    "api key", "api keys", "secret key", "private key", "exchange account",
    "exchange login", "credentials", "withdraw", "deposit funds",
)
_PRIVATE_DATA_KEYWORDS = (
    "private feed", "authenticated endpoint", "insider", "paid signal", "signal group",
)
_HYPE_KEYWORDS = (
    "guaranteed profit", "guaranteed returns", "risk-free profit", "riskless profit",
    "can't lose", "cannot lose", "sure thing", "100% win",
)
# Re-mining the consumed Crypto-D1 evidence windows repeats the overfit mistake.
_TAINTED_WINDOW_KEYWORDS = (
    "same rc1 windows", "same rc2 windows", "reuse the oos windows",
    "re-run the old windows", "rerun the old windows", "re-optimize rp",
    "reoptimize rp", "tune rp6", "tweak rp6 parameters",
)

# --- lane routing keyword classes ---
_ARBITRAGE_KEYWORDS = (
    "arbitrage", "funding rate", "funding rates", "basis", "spot-perp", "spot perp",
    "perp", "perpetual", "cross-exchange", "cross exchange", "spread between",
    "pair spread", "price difference between", "net edge", "carry trade",
)
_CRYPTO_D1_KEYWORDS = (
    "resume policy", "resume-policy", "rp4", "rp5", "rp6", "crypto-d1", "crypto d1",
    "fresh evidence", "trend filter", "re-entry rule", "reentry rule",
    "v2_trend_plus_cash", "kill switch",
)

# Suggested next safe commands per route (proposals only; the human issues them).
_NEXT_SAFE_COMMAND_ARBITRAGE = "BUILD_ARBITRAGE_DATA_CONTRACT_READ_ONLY"
_NEXT_SAFE_COMMAND_CRYPTO_D1 = (
    "AWAIT_FRESH_EVIDENCE_ACCRUAL (stage post-2026-06-08 daily CSVs manually; "
    "evaluation only under the frozen Block 190 bars)"
)
_NEXT_SAFE_COMMAND_NEW_LANE = (
    "BUILD_<NEW_LANE>_RESEARCH_READINESS_CONTRACT_READ_ONLY (open a new lane with its "
    "own constitution first, like Arbitrage Factory V1 did)"
)


def get_strategy_idea_intake_label() -> str:
    """Human label for the recognized strategy idea intake contract."""
    return INTAKE_LABEL


def _idea_text(idea: Any) -> str:
    """Normalize the idea into one lowercase text blob. Pure."""
    if isinstance(idea, str):
        return idea.lower()
    if isinstance(idea, dict):
        parts = [str(idea.get(k, "")) for k in ("title", "description", "mechanism",
                                                "asset_class", "notes")]
        return " ".join(parts).lower()
    return ""


def _matches(text: str, keywords: tuple[str, ...]) -> list[str]:
    """Return the keywords found in the text. Pure."""
    return [k for k in keywords if k in text]


def intake_strategy_idea(idea: Any) -> dict[str, Any]:
    """Triage one strategy idea. PURE and DETERMINISTIC: same idea, same answer.
    Returns a decision dict with answer YES/NO/MAYBE, lane routing, reasons, the next
    safe command (a suggestion the human must issue), and clarifications when MAYBE.
    Starts no work; runs nothing; unlocks nothing. Never raises."""
    text = _idea_text(idea)
    structured = idea if isinstance(idea, dict) else {}
    reasons: list[str] = []
    clarifications: list[str] = []

    if not text.strip():
        return _decision(ANSWER_MAYBE, lane=LANE_NEW_REQUIRED, matched=[],
                         reasons=["empty_idea_nothing_to_triage"],
                         clarifications=["describe the idea: market, mechanism, and "
                                         "what data it needs"],
                         next_safe_command=None)

    # --- HARD NO rules (checked FIRST; any hit rejects) ---
    exec_hits = _matches(text, _EXECUTION_KEYWORDS)
    if structured.get("needs_execution") is True:
        exec_hits.append("structured_flag:needs_execution")
    cred_hits = _matches(text, _CREDENTIAL_KEYWORDS)
    if structured.get("needs_credentials") is True:
        cred_hits.append("structured_flag:needs_credentials")
    private_hits = _matches(text, _PRIVATE_DATA_KEYWORDS)
    hype_hits = _matches(text, _HYPE_KEYWORDS)
    tainted_hits = _matches(text, _TAINTED_WINDOW_KEYWORDS)

    if exec_hits:
        reasons.append("requires_order_execution_which_no_lane_may_ever_do: "
                       + ", ".join(exec_hits))
    if cred_hits:
        reasons.append("requires_exchange_credentials_which_no_agent_may_hold: "
                       + ", ".join(cred_hits))
    if private_hits:
        reasons.append("requires_private_or_authenticated_data: "
                       + ", ".join(private_hits))
    if hype_hits:
        reasons.append("guaranteed_or_riskless_profit_claims_are_auto_rejected: "
                       + ", ".join(hype_hits))
    if tainted_hits:
        reasons.append("re_mining_consumed_crypto_d1_windows_repeats_the_overfit_"
                       "mistake: " + ", ".join(tainted_hits))

    if exec_hits or cred_hits or private_hits or hype_hits or tainted_hits:
        return _decision(ANSWER_NO, lane=None, matched=[], reasons=reasons,
                         clarifications=[],
                         next_safe_command=None)

    # --- lane routing ---
    arb_hits = _matches(text, _ARBITRAGE_KEYWORDS)
    d1_hits = _matches(text, _CRYPTO_D1_KEYWORDS)

    if arb_hits and not d1_hits:
        reasons.append("matches_arbitrage_factory_v1_research_families: "
                       + ", ".join(arb_hits))
        reasons.append("lane_is_alerts_and_reports_only_execution_absent")
        return _decision(ANSWER_YES, lane=LANE_ARBITRAGE, matched=arb_hits,
                         reasons=reasons, clarifications=[],
                         next_safe_command=_NEXT_SAFE_COMMAND_ARBITRAGE)

    if d1_hits and not arb_hits:
        reasons.append("matches_the_sealed_crypto_d1_lane: " + ", ".join(d1_hits))
        reasons.append("crypto_d1_thread_is_closed_only_fresh_evidence_work_qualifies")
        reasons.append("frozen_block_190_bars_apply_no_new_tuning_no_window_reuse")
        return _decision(ANSWER_YES, lane=LANE_CRYPTO_D1, matched=d1_hits,
                         reasons=reasons, clarifications=[],
                         next_safe_command=_NEXT_SAFE_COMMAND_CRYPTO_D1)

    if arb_hits and d1_hits:
        reasons.append("idea_spans_two_lanes_human_must_pick_one")
        clarifications.append("does this idea belong to the arbitrage lane "
                              "(alerts/reports) or the crypto-d1 fresh-evidence path?")
        return _decision(ANSWER_MAYBE, lane=None, matched=arb_hits + d1_hits,
                         reasons=reasons, clarifications=clarifications,
                         next_safe_command=None)

    # No lane match: a genuinely new idea needs its own lane constitution first.
    reasons.append("no_existing_lane_matches_a_new_lane_constitution_is_required_first")
    clarifications.append("what market/instrument does this idea trade or observe?")
    clarifications.append("what data does it need, and can that data be manually staged "
                          "read-only?")
    clarifications.append("confirm it is research/alerts only with no execution ever")
    return _decision(ANSWER_MAYBE, lane=LANE_NEW_REQUIRED, matched=[],
                     reasons=reasons, clarifications=clarifications,
                     next_safe_command=_NEXT_SAFE_COMMAND_NEW_LANE)


def _decision(
    answer: str,
    *,
    lane: str | None,
    matched: list[str],
    reasons: list[str],
    clarifications: list[str],
    next_safe_command: str | None,
) -> dict[str, Any]:
    """Assemble an intake decision dict carrying the read-only safety posture. The
    intake starts no work: the suggested command is a proposal the human must issue."""
    return {
        "schema_version": INTAKE_SCHEMA_VERSION,
        "label": INTAKE_LABEL,
        "mode": INTAKE_MODE,
        "answer": answer,
        "lane": lane,
        "matched_keywords": list(matched),
        "reasons": list(reasons),
        "clarifications": list(clarifications),
        "next_safe_command": next_safe_command,
        "next_safe_command_is_a_suggestion_only": True,
        "human_review_required": True,
        "intake_starts_no_work": True,
        # Capability posture (triage only; runs / fetches / authorizes nothing):
        "executes": False,
        "writes_files": False,
        "runs_research": False,
        "runs_scanner": False,
        "runs_simulation": False,
        "runs_backtest": False,
        "runs_optimization": False,
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
        # Gate posture (the global trading gates are UNTOUCHED and stay locked):
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
        "live_gate_locked": True,
        "next_required_action": NEXT_REQUIRED_ACTION,
    }


def validate_intake_decision(decision: Any) -> dict[str, Any]:
    """Validate (read-only) an intake decision's shape and safety invariants. Returns
    {"valid": bool, "errors": [...]}; never raises."""
    errors: list[str] = []
    if not isinstance(decision, dict):
        return {"valid": False, "errors": ["decision_not_a_dict"]}
    d = decision

    if d.get("answer") not in (ANSWER_YES, ANSWER_NO, ANSWER_MAYBE):
        errors.append("bad_answer")
    if d.get("schema_version") != INTAKE_SCHEMA_VERSION:
        errors.append("bad_schema_version")

    lane = d.get("lane")
    if lane is not None and lane not in KNOWN_LANES:
        errors.append("unknown_lane:" + str(lane))

    if d.get("answer") == ANSWER_YES:
        if lane not in (LANE_ARBITRAGE, LANE_CRYPTO_D1):
            errors.append("yes_without_existing_lane")
        if not d.get("next_safe_command"):
            errors.append("yes_without_next_safe_command")
    if d.get("answer") == ANSWER_NO:
        if d.get("next_safe_command") is not None:
            errors.append("rejected_idea_carries_a_command")
        if not (d.get("reasons") or []):
            errors.append("rejection_without_reasons")
    if d.get("answer") == ANSWER_MAYBE:
        if not (d.get("clarifications") or []):
            errors.append("maybe_without_clarifications")

    if d.get("next_safe_command_is_a_suggestion_only") is not True:
        errors.append("suggestion_only_flag_dropped")
    if d.get("human_review_required") is not True:
        errors.append("human_review_dropped")
    if d.get("intake_starts_no_work") is not True:
        errors.append("intake_claims_to_start_work")

    must_be_locked = ("paper_trading_gate_locked", "micro_live_gate_locked", "live_gate_locked")
    for key in must_be_locked:
        if d.get(key) is not True:
            errors.append("gate_not_locked:" + key)

    must_be_false = (
        "executes",
        "writes_files",
        "runs_research",
        "runs_scanner",
        "runs_simulation",
        "runs_backtest",
        "runs_optimization",
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
        if d.get(key) is not False:
            errors.append("capability_not_false:" + key)

    return {"valid": not errors, "errors": errors}


def render_intake_decision_markdown(decision: Any) -> str:
    """Render an intake decision as deterministic markdown. Pure string work."""
    d = decision if isinstance(decision, dict) else {}
    lines: list[str] = []
    lines.append("# SPARTA Strategy Idea Intake Decision")
    lines.append("")
    lines.append("- Answer: " + str(d.get("answer", "")))
    lines.append("- Lane: " + str(d.get("lane", "")))
    lines.append("- Next safe command (suggestion only, human must issue): "
                 + str(d.get("next_safe_command", "")))
    lines.append("- Human review required: " + str(d.get("human_review_required", "")))
    lines.append("- Intake starts no work: " + str(d.get("intake_starts_no_work", "")))
    lines.append("")
    lines.append("## Reasons")
    for r in d.get("reasons") or ["(none)"]:
        lines.append("- " + str(r))
    lines.append("")
    lines.append("## Clarifications needed")
    for c in d.get("clarifications") or ["(none)"]:
        lines.append("- " + str(c))
    lines.append("")
    lines.append("## Gates (read-only metadata, UNCHANGED)")
    lines.append("- paper_trading_gate: LOCKED")
    lines.append("- micro_live_gate: LOCKED")
    lines.append("- live_gate: LOCKED")
    return "\n".join(lines)

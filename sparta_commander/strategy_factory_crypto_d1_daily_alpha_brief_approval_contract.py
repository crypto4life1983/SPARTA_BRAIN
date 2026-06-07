"""SPARTA Offline Strategy Factory - CRYPTO-D1 DAILY ALPHA BRIEF (APPROVAL).

A PURE, stdlib-only *read-only paper contract* that *approves* the output of the
Crypto-D1 Daily Alpha Brief Review Contract (Block 127) for RESEARCH RECORD ONLY,
without executing anything. It takes a small, caller-provided ``upstream`` dict
(the daily alpha brief review result/verdict, or a similarly shaped dict) and
returns a deterministic, structured approval verdict: whether the reviewed brief
may be archived as research evidence and the single research-only next step.

CORE RULE: the approval records, on paper, that a clean research-only review may
be filed as research evidence; it NEVER promotes a brief beyond WATCH /
RESEARCH_ONLY and it authorizes nothing. The highest stance it can ever hold is
WATCH / RESEARCH_ONLY. An APPROVED verdict means ONLY
``DAILY_ALPHA_BRIEF_APPROVED_FOR_RESEARCH_RECORD`` -- it does NOT mean real-data
QA, baseline, backtest, paper trading, live trading, broker/exchange, automation,
or any runtime/dashboard write is approved.

This contract authorizes NOTHING real. It does NOT fetch any data, call any API,
inspect any dataset, acquire any real data, load any file, open any network, run
any QA, baseline, backtest, or simulation, produce any trade signal, reach any
broker / exchange / order / account / API surface, trade any paper and any live,
promote any strategy, unlock any downstream gate (real_data_qa,
baseline_backtest, paper_trading_gate, micro_live_gate stay blocked / locked),
trigger any automation, write any runtime / registry / ledger / dashboard /
report state, spawn any child process, read any environment, record any
wall-clock time, mint any random id, or dynamically import anything. It ONLY
inspects the static ``upstream`` dict the caller passes in, using pure
dict/string arithmetic.

Approval outcomes (precedence, highest first):
    REJECTED > PARKED > NEEDS_MORE_INFO > APPROVED > AWAIT
  - AWAIT            -> no upstream review was supplied; nothing to approve yet.
  - APPROVED         -> upstream review is a clean, complete, research-only READY
                        verdict; the reviewed brief may be filed as research
                        evidence (DAILY_ALPHA_BRIEF_APPROVED_FOR_RESEARCH_RECORD).
                        The approval stance still stays WATCH / RESEARCH_ONLY.
  - NEEDS_MORE_INFO  -> upstream review is safe but not a clean READY verdict
                        (it is AWAIT / NEEDS_MORE_INFO, or otherwise incomplete).
  - PARKED           -> upstream review was PARKED, or recorded forbidden
                        capability requests; a human must look before anything
                        proceeds.
  - REJECTED         -> upstream review is unsafe: executes=True, not
                        research_only, any authorization flag True, a REJECTED
                        upstream verdict, any promotion beyond WATCH, any request
                        to unlock or approve real_data_qa / baseline / paper /
                        live / automation, or any executable signal/order/trade
                        field.

Evidence lanes stay observation-only at all times: External Bot Evidence,
Hyperliquid Whale Evidence, Funding Rate Evidence, Bitcoin Cycle Timing
Evidence, Daily Alpha Brief Research, and Daily Alpha Brief Review.

Public API:
  - DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION
  - DAILY_ALPHA_BRIEF_APPROVAL_LABEL
  - DAILY_ALPHA_BRIEF_APPROVAL_STATUS
  - DAILY_ALPHA_BRIEF_APPROVAL_MODE
  - DAILY_ALPHA_BRIEF_APPROVAL_CORE_RULE
  - DAILY_ALPHA_BRIEF_APPROVAL_RESULT
  - DAILY_ALPHA_BRIEF_APPROVAL_SAFETY_POSTURE
  - DAILY_ALPHA_BRIEF_APPROVAL_OBSERVATION_ONLY_EVIDENCE_LANES
  - DAILY_ALPHA_BRIEF_APPROVAL_OUTCOMES
  - OUTCOME_REJECTED / OUTCOME_PARKED / OUTCOME_NEEDS_MORE_INFO /
    OUTCOME_APPROVED / OUTCOME_AWAIT
  - DAILY_ALPHA_BRIEF_APPROVAL_STANCE
  - DAILY_ALPHA_BRIEF_APPROVAL_AUTHORIZATION_FLAGS
  - DAILY_ALPHA_BRIEF_APPROVAL_GATE_LOCK_FLAGS
  - DAILY_ALPHA_BRIEF_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS
  - DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_APPROVAL_REQUEST_FLAGS
  - DAILY_ALPHA_BRIEF_APPROVAL_EXECUTABLE_SIGNAL_FIELDS
  - DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_TRADE_TERMS
  - DAILY_ALPHA_BRIEF_APPROVAL_NEXT_REQUIRED_ACTION
  - DAILY_ALPHA_BRIEF_APPROVAL_CURRENT_STAGE
  - DEFAULT_SAMPLE_UPSTREAM
  - approve_daily_alpha_brief(upstream)
  - build_crypto_d1_daily_alpha_brief_approval_contract(upstream=None)
  - validate_crypto_d1_daily_alpha_brief_approval_contract(contract)
  - render_crypto_d1_daily_alpha_brief_approval_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION",
    "DAILY_ALPHA_BRIEF_APPROVAL_LABEL",
    "DAILY_ALPHA_BRIEF_APPROVAL_STATUS",
    "DAILY_ALPHA_BRIEF_APPROVAL_MODE",
    "DAILY_ALPHA_BRIEF_APPROVAL_CORE_RULE",
    "DAILY_ALPHA_BRIEF_APPROVAL_RESULT",
    "DAILY_ALPHA_BRIEF_APPROVAL_SAFETY_POSTURE",
    "DAILY_ALPHA_BRIEF_APPROVAL_OBSERVATION_ONLY_EVIDENCE_LANES",
    "DAILY_ALPHA_BRIEF_APPROVAL_OUTCOMES",
    "OUTCOME_REJECTED",
    "OUTCOME_PARKED",
    "OUTCOME_NEEDS_MORE_INFO",
    "OUTCOME_APPROVED",
    "OUTCOME_AWAIT",
    "DAILY_ALPHA_BRIEF_APPROVAL_STANCE",
    "DAILY_ALPHA_BRIEF_APPROVAL_AUTHORIZATION_FLAGS",
    "DAILY_ALPHA_BRIEF_APPROVAL_GATE_LOCK_FLAGS",
    "DAILY_ALPHA_BRIEF_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS",
    "DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_APPROVAL_REQUEST_FLAGS",
    "DAILY_ALPHA_BRIEF_APPROVAL_EXECUTABLE_SIGNAL_FIELDS",
    "DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_TRADE_TERMS",
    "DAILY_ALPHA_BRIEF_APPROVAL_NEXT_REQUIRED_ACTION",
    "DAILY_ALPHA_BRIEF_APPROVAL_CURRENT_STAGE",
    "DEFAULT_SAMPLE_UPSTREAM",
    "approve_daily_alpha_brief",
    "build_crypto_d1_daily_alpha_brief_approval_contract",
    "validate_crypto_d1_daily_alpha_brief_approval_contract",
    "render_crypto_d1_daily_alpha_brief_approval_contract_markdown",
]

DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_daily_alpha_brief_approval_contract.v1"
)
# The exact contract label required by the bundle spec (Block 129).
DAILY_ALPHA_BRIEF_APPROVAL_LABEL = (
    "Block 129 - Crypto-D1 Daily Alpha Brief Approval Contract"
)
DAILY_ALPHA_BRIEF_APPROVAL_STATUS = (
    "READ_ONLY_CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT"
)
DAILY_ALPHA_BRIEF_APPROVAL_MODE = "RESEARCH_ONLY"

DAILY_ALPHA_BRIEF_APPROVAL_CORE_RULE = (
    "The approval records, on paper, that a clean research-only review may be "
    "filed as research evidence; it never promotes a brief beyond WATCH / "
    "RESEARCH_ONLY and it authorizes nothing."
)

# The single meaning an APPROVED verdict can ever carry. It is a research-record
# approval only -- never a QA, baseline, backtest, paper, live, broker/exchange,
# automation, or runtime/dashboard-write approval.
DAILY_ALPHA_BRIEF_APPROVAL_RESULT = "DAILY_ALPHA_BRIEF_APPROVED_FOR_RESEARCH_RECORD"

# The approval never holds a stance higher than WATCH / RESEARCH_ONLY. Even an
# APPROVED verdict keeps this exact stance -- an approved brief is still only
# research evidence, never a trade.
DAILY_ALPHA_BRIEF_APPROVAL_STANCE = "WATCH"

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering
# this contract is the separate, later Block 130; importing the registry would
# also risk a circular import).
DAILY_ALPHA_BRIEF_APPROVAL_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT"
)
DAILY_ALPHA_BRIEF_APPROVAL_CURRENT_STAGE = (
    "CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_REQUIRED"
)

# Evidence lanes that remain observation-only at every approval outcome. The
# approval reads about them; it never wires any of them to a fetch, a QA run, a
# backtest, a trade, a broker/exchange, an order, or any automation.
DAILY_ALPHA_BRIEF_APPROVAL_OBSERVATION_ONLY_EVIDENCE_LANES: tuple[str, ...] = (
    "external_bot_evidence",
    "hyperliquid_whale_evidence",
    "funding_rate_evidence",
    "bitcoin_cycle_timing_evidence",
    "daily_alpha_brief_research",
    "daily_alpha_brief_review",
)

# Approval outcomes, in precedence order (highest first). When more than one
# finding applies, the highest-precedence outcome wins.
OUTCOME_REJECTED = "REJECTED"
OUTCOME_PARKED = "PARKED"
OUTCOME_NEEDS_MORE_INFO = "NEEDS_MORE_INFO"
OUTCOME_APPROVED = "APPROVED"
OUTCOME_AWAIT = "AWAIT"

DAILY_ALPHA_BRIEF_APPROVAL_OUTCOMES: tuple[str, ...] = (
    OUTCOME_REJECTED,
    OUTCOME_PARKED,
    OUTCOME_NEEDS_MORE_INFO,
    OUTCOME_APPROVED,
    OUTCOME_AWAIT,
)
_OUTCOME_SET: frozenset[str] = frozenset(DAILY_ALPHA_BRIEF_APPROVAL_OUTCOMES)
# Lower index == higher precedence.
_OUTCOME_PRECEDENCE: dict[str, int] = {
    OUTCOME_REJECTED: 0,
    OUTCOME_PARKED: 1,
    OUTCOME_NEEDS_MORE_INFO: 2,
    OUTCOME_APPROVED: 3,
    OUTCOME_AWAIT: 4,
}

# Read-only safety posture. The three True flags are *posture* facts (this is a
# read-only, research-only contract that requires human approval); every
# capability/authorization/unlock flag is False.
DAILY_ALPHA_BRIEF_APPROVAL_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "executes": False,
    "human_approval_required": True,
    "authorizes_trading": False,
    "authorizes_data_fetch": False,
    "authorizes_backtest": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_automation": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}

# Upstream authorization flags that, if truthy, force a REJECTED verdict. (The
# ``executes`` flag is handled separately so it can be reported distinctly.)
DAILY_ALPHA_BRIEF_APPROVAL_AUTHORIZATION_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "unlocks_downstream_gate",
)

# Upstream gate-lock flags that MUST be True (blocked / locked). If any is
# present and not True, the upstream tried to unlock a gate -> REJECTED.
DAILY_ALPHA_BRIEF_APPROVAL_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, force a REJECTED verdict.
DAILY_ALPHA_BRIEF_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
)

# Requests asking this approval to mean something beyond a research record. Any
# truthy value forces a REJECTED verdict: approval can ONLY ever mean
# DAILY_ALPHA_BRIEF_APPROVED_FOR_RESEARCH_RECORD.
DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_APPROVAL_REQUEST_FLAGS: tuple[str, ...] = (
    "approve_real_data_qa",
    "approve_baseline_backtest",
    "approve_baseline",
    "approve_backtest",
    "approve_paper_trading",
    "approve_live_trading",
    "approve_broker_exchange",
    "approve_automation",
    "approve_runtime_write",
    "approve_dashboard_write",
    "approve_trading",
)

# Fields whose presence (non-empty) signals an executable signal / order / trade
# instruction in the upstream -> REJECTED. An approval never carries execution.
DAILY_ALPHA_BRIEF_APPROVAL_EXECUTABLE_SIGNAL_FIELDS: tuple[str, ...] = (
    "signal",
    "order",
    "trade",
    "trade_instruction",
    "execution",
    "position",
    "entry",
    "exit",
    "side",
)

# Execution / promotion verbs the approval's own generated guidance must never
# contain, and which (as whole words) in an upstream verdict/stance signal an
# attempt to promote beyond WATCH.
DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
    "order",
)

# Tokens in an upstream verdict/stance that indicate promotion beyond a research
# WATCH (e.g. a PASS / ACTIVE / STRONG / LIVE verdict).
_PROMOTION_TOKENS: frozenset[str] = frozenset(
    {
        "pass",
        "passed",
        "active",
        "strong",
        "promote",
        "promoted",
        "promotion",
        "live",
        "execute",
        "executed",
        "tradeable",
        "buy",
        "sell",
        "long",
        "short",
        "entry",
        "exit",
        "order",
    }
)

# Upstream review outcomes the approval treats as a clean READY verdict (the only
# states that may be APPROVED for research record).
_CLEAN_REVIEW_OUTCOMES: frozenset[str] = frozenset({"READY", "REVIEW_READY"})
# Upstream review outcomes the approval recognizes as safe-but-not-approvable.
_AWAIT_REVIEW_OUTCOMES: frozenset[str] = frozenset(
    {"AWAIT", "NEEDS_MORE_INFO", "INCOMPLETE", "INCOMPLETE_EVIDENCE"}
)
_PARKED_REVIEW_OUTCOMES: frozenset[str] = frozenset({"PARKED"})
_REJECTED_REVIEW_OUTCOMES: frozenset[str] = frozenset({"REJECTED"})

# Upstream stance values the approval treats as legitimately research-only
# (anything else on the stance field is a promotion attempt).
_ALLOWED_UPSTREAM_STANCES: frozenset[str] = frozenset(
    {"WATCH", "RESEARCH_ONLY", "MIXED", "INCOMPLETE_EVIDENCE"}
)

# A deterministic, illustrative paper sample modeling a clean, safe,
# research-only daily alpha brief *review* result -> approves as APPROVED.
# Nothing here is real data; these are static example fields only.
DEFAULT_SAMPLE_UPSTREAM: dict[str, Any] = {
    "label": "Block 127 - Crypto-D1 Daily Alpha Brief Review Contract",
    "mode": "RESEARCH_ONLY",
    "outcome": "READY",
    "review_stance": "WATCH",
    "read_only": True,
    "executes": False,
    "research_only": True,
    "promotes_beyond_watch": False,
    "authorizes_trading": False,
    "authorizes_data_fetch": False,
    "authorizes_backtest": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_automation": False,
    "authorizes_real_world_action": False,
    "unlocks_downstream_gate": False,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
    "rejection_reasons": [],
    "park_reasons": [],
    "needs_more_info_reasons": [],
    "requested_forbidden_flags": [],
}


def _as_text(value: Any) -> str:
    """Coerce any value to a stripped string; non-str/None -> ''."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _truthy(value: Any) -> bool:
    """Conservative truthiness for caller-supplied flags."""
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in ("true", "yes", "1", "on", "allow")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value != 0
    return False


def _isolated(value: Any) -> Any:
    """Return an isolated copy so the contract never shares mutable references
    with caller input."""
    if isinstance(value, dict):
        return {k: _isolated(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_isolated(v) for v in value]
    return value


def _word_tokens(text: str) -> set[str]:
    """Lowercased alphabetic whole-word tokens of a string."""
    tokens: set[str] = set()
    word: list[str] = []
    for ch in text.lower():
        if ch.isalpha():
            word.append(ch)
        else:
            if word:
                tokens.add("".join(word))
                word = []
    if word:
        tokens.add("".join(word))
    return tokens


def _non_empty(value: Any) -> bool:
    """True when a caller field is present and carries real content."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return len(value) > 0
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return True


def _executes_findings(upstream: dict[str, Any]) -> list[str]:
    if _truthy(upstream.get("executes")):
        return ["upstream review executes=True"]
    return []


def _research_only_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if upstream.get("research_only") is not True:
        reasons.append("upstream review research_only is not True")
    if "read_only" in upstream and upstream.get("read_only") is not True:
        reasons.append("upstream review read_only is not True")
    mode = _as_text(upstream.get("mode"))
    if mode and mode != "RESEARCH_ONLY":
        reasons.append("upstream review mode is not RESEARCH_ONLY")
    return reasons


def _authorization_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for flag in DAILY_ALPHA_BRIEF_APPROVAL_AUTHORIZATION_FLAGS:
        if _truthy(upstream.get(flag)):
            reasons.append("authorization flag True: " + flag)
    return reasons


def _gate_unlock_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for flag in DAILY_ALPHA_BRIEF_APPROVAL_GATE_LOCK_FLAGS:
        if flag in upstream and upstream.get(flag) is not True:
            reasons.append("gate unlock attempt: " + flag + " is not locked")
    for flag in DAILY_ALPHA_BRIEF_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS:
        if _truthy(upstream.get(flag)):
            reasons.append("gate unlock request: " + flag)
    return reasons


def _forbidden_approval_request_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for flag in DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_APPROVAL_REQUEST_FLAGS:
        if _truthy(upstream.get(flag)):
            reasons.append(
                "forbidden approval request: "
                + flag
                + " (approval can only mean "
                + DAILY_ALPHA_BRIEF_APPROVAL_RESULT
                + ")"
            )
    return reasons


def _executable_signal_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for field in DAILY_ALPHA_BRIEF_APPROVAL_EXECUTABLE_SIGNAL_FIELDS:
        if field in upstream and _non_empty(upstream.get(field)):
            reasons.append("executable signal/order/trade field present: " + field)
    return reasons


def _promotion_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if _truthy(upstream.get("promotes_beyond_watch")):
        reasons.append("upstream review promotes beyond WATCH")
    if _truthy(upstream.get("promote")) or _truthy(upstream.get("promoted")):
        reasons.append("promotion requested beyond WATCH")
    stance = _as_text(upstream.get("review_stance")) or _as_text(
        upstream.get("stance")
    )
    if stance and stance not in _ALLOWED_UPSTREAM_STANCES:
        reasons.append("upstream stance promotes beyond WATCH: " + stance)
    for field in ("review_stance", "stance", "requested_stance", "verdict"):
        tokens = _word_tokens(_as_text(upstream.get(field)))
        hits = sorted(tokens & _PROMOTION_TOKENS)
        if hits:
            reasons.append(
                "promotion token in " + field + ": " + ", ".join(hits)
            )
    return reasons


def _upstream_outcome_rejection_findings(upstream: dict[str, Any]) -> list[str]:
    outcome = _as_text(upstream.get("outcome")).upper()
    if outcome and outcome in _REJECTED_REVIEW_OUTCOMES:
        return ["upstream review outcome is REJECTED; cannot approve"]
    # An unrecognized, non-empty outcome that is not any known safe state and
    # carries a promotion token is treated as a promotion attempt.
    if (
        outcome
        and outcome not in _CLEAN_REVIEW_OUTCOMES
        and outcome not in _AWAIT_REVIEW_OUTCOMES
        and outcome not in _PARKED_REVIEW_OUTCOMES
        and (_word_tokens(outcome) & _PROMOTION_TOKENS)
    ):
        return ["upstream review outcome promotes beyond WATCH: " + outcome]
    return []


def _park_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    outcome = _as_text(upstream.get("outcome")).upper()
    if outcome in _PARKED_REVIEW_OUTCOMES:
        reasons.append("upstream review outcome is PARKED; human review required")
    requested = upstream.get("requested_forbidden_flags")
    if isinstance(requested, (list, tuple)) and len(requested) > 0:
        reasons.append(
            "upstream recorded "
            + str(len(requested))
            + " forbidden capability request(s) (never honored); human review "
            "required"
        )
    park_reasons = upstream.get("park_reasons")
    if isinstance(park_reasons, (list, tuple)) and len(park_reasons) > 0:
        reasons.append(
            "upstream review recorded "
            + str(len(park_reasons))
            + " park finding(s); human review required"
        )
    return reasons


def _needs_more_info_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    outcome = _as_text(upstream.get("outcome")).upper()
    if outcome in _AWAIT_REVIEW_OUTCOMES:
        reasons.append(
            "upstream review outcome is " + outcome + "; not a clean READY verdict"
        )
    elif outcome and outcome not in _CLEAN_REVIEW_OUTCOMES:
        # Recognized non-clean handled elsewhere; an entirely unknown, harmless
        # outcome is treated as incomplete information rather than approvable.
        if (
            outcome not in _PARKED_REVIEW_OUTCOMES
            and outcome not in _REJECTED_REVIEW_OUTCOMES
            and not (_word_tokens(outcome) & _PROMOTION_TOKENS)
        ):
            reasons.append(
                "upstream review outcome is not a clean READY verdict: " + outcome
            )
    rev_rejections = upstream.get("rejection_reasons")
    if isinstance(rev_rejections, (list, tuple)) and len(rev_rejections) > 0:
        reasons.append(
            "upstream review recorded "
            + str(len(rev_rejections))
            + " rejection reason(s); not a clean READY verdict"
        )
    nmi = upstream.get("needs_more_info_reasons")
    if isinstance(nmi, (list, tuple)) and len(nmi) > 0:
        reasons.append(
            "upstream review recorded "
            + str(len(nmi))
            + " needs-more-info finding(s)"
        )
    return reasons


def approve_daily_alpha_brief(upstream: Any) -> dict[str, Any]:
    """Return a deterministic, research-only approval verdict for an upstream
    daily-alpha-brief *review* result. Pure; no I/O, no data fetch, no clock
    read, no mutation, no random id. Malformed / missing inputs never raise -- a
    missing upstream resolves to AWAIT. The approval stance is always WATCH /
    RESEARCH_ONLY and an APPROVED verdict only ever means
    DAILY_ALPHA_BRIEF_APPROVED_FOR_RESEARCH_RECORD; it authorizes nothing."""
    present = isinstance(upstream, dict) and len(upstream) > 0
    src = upstream if isinstance(upstream, dict) else {}

    rejection_reasons: list[str] = []
    park_reasons: list[str] = []
    needs_more_info_reasons: list[str] = []

    if present:
        rejection_reasons = (
            _executes_findings(src)
            + _research_only_findings(src)
            + _authorization_findings(src)
            + _gate_unlock_findings(src)
            + _forbidden_approval_request_findings(src)
            + _executable_signal_findings(src)
            + _promotion_findings(src)
            + _upstream_outcome_rejection_findings(src)
        )
        park_reasons = _park_findings(src)
        needs_more_info_reasons = _needs_more_info_findings(src)

    if not present:
        outcome = OUTCOME_AWAIT
    elif rejection_reasons:
        outcome = OUTCOME_REJECTED
    elif park_reasons:
        outcome = OUTCOME_PARKED
    elif needs_more_info_reasons:
        outcome = OUTCOME_NEEDS_MORE_INFO
    else:
        outcome = OUTCOME_APPROVED

    approval_result = (
        DAILY_ALPHA_BRIEF_APPROVAL_RESULT if outcome == OUTCOME_APPROVED else ""
    )

    return {
        "outcome": outcome,
        "approval_result": approval_result,
        "approval_stance": DAILY_ALPHA_BRIEF_APPROVAL_STANCE,
        "mode": DAILY_ALPHA_BRIEF_APPROVAL_MODE,
        "upstream_present": present,
        "rejection_reasons": rejection_reasons,
        "park_reasons": park_reasons,
        "needs_more_info_reasons": needs_more_info_reasons,
        "promotes_beyond_watch": False,
        "approves_research_record_only": True,
        "authorizes_nothing": True,
    }


def _approval_summary_section(approval: dict[str, Any]) -> list[str]:
    return [
        "Approval outcome: " + approval["outcome"] + ".",
        "Approval stance: "
        + approval["approval_stance"]
        + " / RESEARCH_ONLY (attention only).",
        "Upstream daily alpha brief review present: "
        + ("yes" if approval["upstream_present"] else "no")
        + ".",
        "An APPROVED verdict means only "
        + DAILY_ALPHA_BRIEF_APPROVAL_RESULT
        + "; it is not a trade plan and it authorizes nothing.",
    ]


def _approval_findings_section(approval: dict[str, Any]) -> list[str]:
    outcome = approval["outcome"]
    if outcome == OUTCOME_AWAIT:
        return [
            "No upstream daily alpha brief review was supplied; there is nothing "
            "to approve yet.",
            "AWAIT never resolves to an execution decision.",
        ]
    if outcome == OUTCOME_REJECTED:
        lines = [
            "Upstream review REJECTED for approval; it is not safe research-only "
            "state:"
        ]
        lines.extend("- " + reason for reason in approval["rejection_reasons"])
        lines.append(
            "Rejection authorizes nothing and unlocks no gate; the review must "
            "be redone as research-only."
        )
        return lines
    if outcome == OUTCOME_PARKED:
        lines = ["Upstream review PARKED for human attention:"]
        lines.extend("- " + reason for reason in approval["park_reasons"])
        lines.append(
            "Parking authorizes nothing; a human must inspect before any "
            "research-only approval is recorded."
        )
        return lines
    if outcome == OUTCOME_NEEDS_MORE_INFO:
        lines = ["Upstream review is safe but not a clean READY verdict:"]
        lines.extend(
            "- " + reason for reason in approval["needs_more_info_reasons"]
        )
        lines.append(
            "Incomplete review resolves to NEEDS_MORE_INFO; it never resolves to "
            "an execution decision."
        )
        return lines
    return [
        "Upstream review is a clean, complete, research-only READY verdict; the "
        "reviewed brief may be filed as research evidence.",
        "APPROVED means only "
        + DAILY_ALPHA_BRIEF_APPROVAL_RESULT
        + " and it still authorizes nothing; the approval stance stays WATCH / "
        "RESEARCH_ONLY.",
        "It does not approve real-data QA, baseline, backtest, paper trading, "
        "live trading, broker/exchange, automation, or any runtime/dashboard "
        "write.",
    ]


def _observation_only_section() -> list[str]:
    lines = [
        lane + " remains observation-only (attention only)."
        for lane in DAILY_ALPHA_BRIEF_APPROVAL_OBSERVATION_ONLY_EVIDENCE_LANES
    ]
    lines.append(
        "No evidence lane is ever wired to a data fetch, an API call, a "
        "dataset, a QA run, a backtest, a paper/live trade, a broker or "
        "exchange, or any automation."
    )
    return lines


_NO_EXECUTION_AUTHORIZATION_SECTION: tuple[str, ...] = (
    "This approval authorizes no trade and no position of any kind.",
    "It permits no data fetch, no API call, no dataset inspection, no QA, no "
    "baseline, and no backtest.",
    "It permits no paper trading, no live trading, no broker or exchange "
    "connection, and no automation.",
    "It writes no runtime, registry, ledger, or dashboard state.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
    "The highest stance it can hold is WATCH / RESEARCH_ONLY; an APPROVED "
    "verdict only files the reviewed brief as research evidence and never "
    "produces an execution instruction.",
)

_OPERATOR_NEXT_STEP = (
    "Research-only: a human reviewer must read this approval verdict, "
    "independently confirm every finding, and treat an APPROVED outcome as a "
    "research-record approval only. The single permitted next step is to "
    "register or assemble the next research-only contract on paper. No "
    "execution of any kind is authorized."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 daily alpha brief approval contract template and is "
    "execution-free.",
    "It inspects an already-produced static daily alpha brief review result and "
    "reports whether it may be filed as research evidence; it runs nothing, "
    "fetches nothing, and connects nowhere.",
    "Core rule: the approval records what may be archived as research, never "
    "what to trade, and never promotes a brief beyond WATCH / RESEARCH_ONLY.",
    "Outcome precedence is REJECTED > PARKED > NEEDS_MORE_INFO > APPROVED > "
    "AWAIT; a missing upstream resolves to AWAIT.",
    "An unsafe upstream (executes=True, not research_only, any authorization "
    "flag True, a REJECTED review, any promotion beyond WATCH, any gate unlock "
    "or forbidden approval request, or any executable signal/order/trade field) "
    "resolves to REJECTED and unlocks nothing.",
    "An APPROVED verdict means only "
    + DAILY_ALPHA_BRIEF_APPROVAL_RESULT
    + "; it never means real-data QA, baseline, backtest, paper, live, broker/"
    "exchange, automation, or runtime/dashboard write is approved.",
    "Every finding is attention-only and needs independent confirmation; the "
    "approval never converts evidence into permission.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human reviewer must read the structured approval verdict before any "
    "further research-only contract is built.",
    "A human reviewer must confirm an APPROVED outcome is treated only as a "
    "research-record approval and is never wired to a data fetch, an API call, "
    "a dataset, a QA run, a backtest, a paper/live trade, a broker or exchange, "
    "an order, or any automation.",
    "A human reviewer must independently confirm every finding before it is "
    "trusted.",
    "A human reviewer must confirm the next step is only to register or build "
    "the next research-only contract, still on paper.",
    "No execution, data fetch, API call, dataset inspection, data acquisition, "
    "QA, backtest, paper/live, broker/exchange, automation, promotion, or "
    "downstream-gate unlock may proceed.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "stage",
    "mode",
    "core_rule",
    "approval_result_meaning",
    "approval_next_required_action",
    "approval_current_stage",
    "observation_only_evidence_lanes",
    "outcomes",
    "approval_stance",
    "authorization_flags",
    "gate_lock_flags",
    "gate_unlock_request_flags",
    "forbidden_approval_request_flags",
    "executable_signal_fields",
    "forbidden_trade_terms",
    "upstream",
    "approval",
    "outcome",
    "approval_result",
    "upstream_present",
    "rejection_reasons",
    "park_reasons",
    "needs_more_info_reasons",
    "approval_summary_section",
    "approval_findings_section",
    "observation_only_section",
    "no_execution_authorization_section",
    "operator_next_step",
    "safety_posture",
    "operator_notes",
    "human_operator_required_next_steps",
    "requires_independent_confirmation",
    "human_approval_required",
    "read_only",
    "executes",
    "research_only",
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "unlocks_downstream_gate",
    "unlocks_real_data_qa",
    "unlocks_baseline_backtest",
    "unlocks_paper_trading",
    "unlocks_micro_live",
    "promotes_beyond_watch",
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the posture (callers cannot taint the global)."""
    return dict(DAILY_ALPHA_BRIEF_APPROVAL_SAFETY_POSTURE)


def build_crypto_d1_daily_alpha_brief_approval_contract(
    upstream: Any = None,
) -> dict[str, Any]:
    """Build the read-only daily alpha brief approval contract. Pure; no I/O, no
    data fetch, no mutation of inputs, no clock read, no random id. When no
    upstream is given, the static DEFAULT_SAMPLE_UPSTREAM is approved. A fresh
    dict (with fresh lists/dicts) is returned every call. The contract never
    holds a stance higher than WATCH / RESEARCH_ONLY, an APPROVED verdict only
    ever means DAILY_ALPHA_BRIEF_APPROVED_FOR_RESEARCH_RECORD, and it authorizes
    nothing."""
    if upstream is None:
        source = _isolated(DEFAULT_SAMPLE_UPSTREAM)
    elif isinstance(upstream, dict):
        source = _isolated(upstream)
    else:
        source = upstream

    approval = approve_daily_alpha_brief(source)

    contract: dict[str, Any] = {
        "schema_version": DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION,
        "label": DAILY_ALPHA_BRIEF_APPROVAL_LABEL,
        "status": DAILY_ALPHA_BRIEF_APPROVAL_STATUS,
        "stage": "CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_ONLY",
        "mode": DAILY_ALPHA_BRIEF_APPROVAL_MODE,
        "core_rule": DAILY_ALPHA_BRIEF_APPROVAL_CORE_RULE,
        "approval_result_meaning": DAILY_ALPHA_BRIEF_APPROVAL_RESULT,
        "approval_next_required_action": (
            DAILY_ALPHA_BRIEF_APPROVAL_NEXT_REQUIRED_ACTION
        ),
        "approval_current_stage": DAILY_ALPHA_BRIEF_APPROVAL_CURRENT_STAGE,
        "observation_only_evidence_lanes": (
            DAILY_ALPHA_BRIEF_APPROVAL_OBSERVATION_ONLY_EVIDENCE_LANES
        ),
        "outcomes": DAILY_ALPHA_BRIEF_APPROVAL_OUTCOMES,
        "approval_stance": DAILY_ALPHA_BRIEF_APPROVAL_STANCE,
        "authorization_flags": DAILY_ALPHA_BRIEF_APPROVAL_AUTHORIZATION_FLAGS,
        "gate_lock_flags": DAILY_ALPHA_BRIEF_APPROVAL_GATE_LOCK_FLAGS,
        "gate_unlock_request_flags": (
            DAILY_ALPHA_BRIEF_APPROVAL_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_approval_request_flags": (
            DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_APPROVAL_REQUEST_FLAGS
        ),
        "executable_signal_fields": (
            DAILY_ALPHA_BRIEF_APPROVAL_EXECUTABLE_SIGNAL_FIELDS
        ),
        "forbidden_trade_terms": (
            DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_TRADE_TERMS
        ),
        "upstream": _isolated(source) if isinstance(source, dict) else {},
        "approval": approval,
        "outcome": approval["outcome"],
        "approval_result": approval["approval_result"],
        "upstream_present": approval["upstream_present"],
        "rejection_reasons": list(approval["rejection_reasons"]),
        "park_reasons": list(approval["park_reasons"]),
        "needs_more_info_reasons": list(approval["needs_more_info_reasons"]),
        "approval_summary_section": _approval_summary_section(approval),
        "approval_findings_section": _approval_findings_section(approval),
        "observation_only_section": _observation_only_section(),
        "no_execution_authorization_section": list(
            _NO_EXECUTION_AUTHORIZATION_SECTION
        ),
        "operator_next_step": _OPERATOR_NEXT_STEP,
        "safety_posture": _safety_posture(),
        "operator_notes": list(_OPERATOR_NOTES),
        "human_operator_required_next_steps": list(
            _HUMAN_OPERATOR_REQUIRED_NEXT_STEPS
        ),
        "requires_independent_confirmation": True,
        "human_approval_required": True,
        "read_only": True,
        "executes": False,
        "research_only": True,
        "authorizes_trading": False,
        "authorizes_data_fetch": False,
        "authorizes_backtest": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "authorizes_broker_exchange": False,
        "authorizes_automation": False,
        "authorizes_real_world_action": False,
        "unlocks_downstream_gate": False,
        "unlocks_real_data_qa": False,
        "unlocks_baseline_backtest": False,
        "unlocks_paper_trading": False,
        "unlocks_micro_live": False,
        "promotes_beyond_watch": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return contract


# Top-level posture flags that must all be exactly False for a valid contract.
_REQUIRED_FALSE_FLAGS: tuple[str, ...] = (
    "executes",
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "unlocks_downstream_gate",
    "unlocks_real_data_qa",
    "unlocks_baseline_backtest",
    "unlocks_paper_trading",
    "unlocks_micro_live",
    "promotes_beyond_watch",
)

# The generated-guidance fields whose text is the approval's own actionable
# output. These must never contain an execution verb. (The raw echoed
# ``upstream`` is caller input, not the approval's guidance, and is excluded.)
_ACTIONABLE_TEXT_FIELDS: tuple[str, ...] = (
    "outcome",
    "approval_result",
    "approval_stance",
    "operator_next_step",
    "approval_summary_section",
    "approval_findings_section",
    "observation_only_section",
    "no_execution_authorization_section",
)


def _contains_forbidden_term(text: str) -> bool:
    tokens = _word_tokens(text)
    return any(
        term in tokens
        for term in DAILY_ALPHA_BRIEF_APPROVAL_FORBIDDEN_TRADE_TERMS
    )


def _no_forbidden_trade_terms(contract: dict[str, Any]) -> bool:
    """True when none of the approval's actionable guidance fields contain an
    execution verb as a whole word. Pure; reads only the contract dict.

    The findings section can legitimately echo an upstream rejection reason that
    quotes a promotion token (e.g. a rejected upstream stance), so that section
    is judged by whether it is reporting a REJECTED verdict rather than issuing
    an instruction."""
    rejected = contract.get("outcome") == OUTCOME_REJECTED
    for field in _ACTIONABLE_TEXT_FIELDS:
        if field == "approval_findings_section" and rejected:
            # A REJECTED findings section is allowed to quote the offending
            # upstream term while explaining the rejection.
            continue
        value = contract.get(field)
        if isinstance(value, str):
            if _contains_forbidden_term(value):
                return False
        elif isinstance(value, (list, tuple)):
            for item in value:
                if isinstance(item, str) and _contains_forbidden_term(item):
                    return False
    return True


def _validate(contract: dict[str, Any]) -> dict[str, Any]:
    """Pure deterministic validation of a contract dict (no I/O)."""
    safe = contract if isinstance(contract, dict) else {}

    missing = tuple(f for f in _REQUIRED_CONTRACT_FIELDS if f not in safe)
    schema_ok = (
        safe.get("schema_version") == DAILY_ALPHA_BRIEF_APPROVAL_SCHEMA_VERSION
    )
    label_ok = safe.get("label") == DAILY_ALPHA_BRIEF_APPROVAL_LABEL
    read_only = safe.get("read_only") is True
    research_only = (
        safe.get("research_only") is True
        and safe.get("mode") == "RESEARCH_ONLY"
    )
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_DAILY_ALPHA_BRIEF_APPROVAL_CONTRACT_ONLY"
    )
    core_rule_ok = (
        safe.get("core_rule") == DAILY_ALPHA_BRIEF_APPROVAL_CORE_RULE
    )
    result_meaning_ok = (
        safe.get("approval_result_meaning") == DAILY_ALPHA_BRIEF_APPROVAL_RESULT
    )
    human_required = safe.get("human_approval_required") is True
    confirmation_required = (
        safe.get("requires_independent_confirmation") is True
    )
    flags_false = all(
        safe.get(flag) is False for flag in _REQUIRED_FALSE_FLAGS
    )
    gates_locked = (
        safe.get("real_data_qa_blocked") is True
        and safe.get("baseline_backtest_blocked") is True
        and safe.get("paper_trading_gate_locked") is True
        and safe.get("micro_live_gate_locked") is True
    )

    posture = safe.get("safety_posture")
    posture_ok = (
        isinstance(posture, dict)
        and posture == DAILY_ALPHA_BRIEF_APPROVAL_SAFETY_POSTURE
    )

    outcome_ok = safe.get("outcome") in _OUTCOME_SET
    stance_ok = (
        safe.get("approval_stance") == DAILY_ALPHA_BRIEF_APPROVAL_STANCE
    )
    # The approval_result is the research-record meaning iff APPROVED, else "".
    if safe.get("outcome") == OUTCOME_APPROVED:
        result_ok = safe.get("approval_result") == DAILY_ALPHA_BRIEF_APPROVAL_RESULT
    else:
        result_ok = safe.get("approval_result") == ""

    lanes_ok = (
        tuple(safe.get("observation_only_evidence_lanes") or ())
        == DAILY_ALPHA_BRIEF_APPROVAL_OBSERVATION_ONLY_EVIDENCE_LANES
    )
    outcomes_ok = (
        tuple(safe.get("outcomes") or ())
        == DAILY_ALPHA_BRIEF_APPROVAL_OUTCOMES
    )

    approval = safe.get("approval")
    approval_ok = (
        isinstance(approval, dict)
        and approval.get("authorizes_nothing") is True
        and approval.get("approves_research_record_only") is True
        and approval.get("outcome") in _OUTCOME_SET
        and approval.get("approval_stance")
        == DAILY_ALPHA_BRIEF_APPROVAL_STANCE
    )

    no_trade_language = _no_forbidden_trade_terms(safe)

    sections_ok = all(
        len(tuple(safe.get(section) or ())) >= 1
        for section in (
            "approval_summary_section",
            "approval_findings_section",
            "observation_only_section",
            "no_execution_authorization_section",
            "operator_notes",
            "human_operator_required_next_steps",
        )
    )
    operator_next_step_ok = bool(_as_text(safe.get("operator_next_step")))

    valid = (
        not missing
        and schema_ok
        and label_ok
        and read_only
        and research_only
        and stage_ok
        and core_rule_ok
        and result_meaning_ok
        and human_required
        and confirmation_required
        and flags_false
        and gates_locked
        and posture_ok
        and outcome_ok
        and stance_ok
        and result_ok
        and lanes_ok
        and outcomes_ok
        and approval_ok
        and no_trade_language
        and sections_ok
        and operator_next_step_ok
    )

    return {
        "valid": bool(valid),
        "missing_fields": missing,
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "read_only": read_only,
        "research_only": research_only,
        "stage_ok": stage_ok,
        "core_rule_ok": core_rule_ok,
        "result_meaning_ok": result_meaning_ok,
        "human_required": human_required,
        "confirmation_required": confirmation_required,
        "flags_false": flags_false,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "outcome_ok": outcome_ok,
        "stance_ok": stance_ok,
        "result_ok": result_ok,
        "lanes_ok": lanes_ok,
        "outcomes_ok": outcomes_ok,
        "approval_ok": approval_ok,
        "no_trade_language": no_trade_language,
        "sections_ok": sections_ok,
        "operator_next_step_ok": operator_next_step_ok,
    }


def validate_crypto_d1_daily_alpha_brief_approval_contract(
    contract: Any,
) -> dict[str, Any]:
    """Public validation entry point; returns the deterministic verdict dict."""
    return _validate(contract)


def render_crypto_d1_daily_alpha_brief_approval_contract_markdown(
    contract: Any,
) -> str:
    """Render an informational, read-only markdown summary of the contract.
    Pure; builds and returns a string, writes nothing."""
    safe = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Daily Alpha Brief Approval Contract")
    lines.append("")
    lines.append("- Label: " + _as_text(safe.get("label")))
    lines.append("- Mode: " + _as_text(safe.get("mode")))
    lines.append("- Status: " + _as_text(safe.get("status")))
    lines.append("- Outcome: " + _as_text(safe.get("outcome")))
    lines.append("- Approval result: " + _as_text(safe.get("approval_result")))
    lines.append("- Approval stance: " + _as_text(safe.get("approval_stance")))
    lines.append("- Read-only: " + str(safe.get("read_only")))
    lines.append("- Executes: " + str(safe.get("executes")))
    lines.append(
        "- Requires independent confirmation: "
        + str(safe.get("requires_independent_confirmation"))
    )
    lines.append(
        "- real_data_qa blocked: " + str(safe.get("real_data_qa_blocked"))
    )
    lines.append(
        "- baseline_backtest blocked: "
        + str(safe.get("baseline_backtest_blocked"))
    )
    lines.append(
        "- paper_trading_gate locked: "
        + str(safe.get("paper_trading_gate_locked"))
    )
    lines.append(
        "- micro_live_gate locked: " + str(safe.get("micro_live_gate_locked"))
    )

    def _emit(title: str, key: str) -> None:
        lines.append("")
        lines.append("## " + title)
        section = safe.get(key)
        if isinstance(section, (list, tuple)) and section:
            for item in section:
                lines.append("- " + _as_text(item))
        else:
            lines.append("- (none)")

    _emit("Approval Summary", "approval_summary_section")
    _emit("Approval Findings", "approval_findings_section")
    _emit("Observation-Only Evidence Lanes", "observation_only_section")
    _emit("No Execution Authorization", "no_execution_authorization_section")
    lines.append("")
    lines.append("## Operator Next Step")
    lines.append("- " + _as_text(safe.get("operator_next_step")))
    return "\n".join(lines)

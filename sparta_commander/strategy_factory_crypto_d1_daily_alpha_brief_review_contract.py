"""SPARTA Offline Strategy Factory - CRYPTO-D1 DAILY ALPHA BRIEF (REVIEW).

A PURE, stdlib-only *read-only paper contract* that *reviews* the output of the
Crypto-D1 Daily Alpha Brief Research Contract (Block 125) without executing
anything. It takes a small, caller-provided ``upstream`` dict (the daily alpha
brief research result, or a similarly shaped dict) and returns a deterministic,
structured review verdict: whether the brief is safe, complete, and
research-only, plus the single research-only next step.

CORE RULE: the review judges whether a daily alpha brief is safe, complete, and
research-only; it NEVER promotes a brief beyond WATCH / RESEARCH_ONLY and it
authorizes nothing. The highest stance it can ever hold is WATCH / RESEARCH_ONLY.

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

Review outcomes (precedence, highest first):
    REJECTED > PARKED > NEEDS_MORE_INFO > READY > AWAIT
  - AWAIT            -> no upstream brief was supplied; nothing to review yet.
  - READY            -> upstream is complete, safe, and research-only; the
                        brief may be read by a human as research evidence. The
                        review stance still stays WATCH / RESEARCH_ONLY.
  - NEEDS_MORE_INFO  -> upstream is safe but incomplete (missing evidence lanes
                        or an AWAIT / INCOMPLETE_EVIDENCE brief).
  - PARKED           -> upstream recorded forbidden capability requests (which
                        the research contract never honored); a human must look
                        before anything proceeds.
  - REJECTED         -> upstream is unsafe: executes=True, not research_only,
                        any authorization flag True, any promotion beyond WATCH,
                        or any request to unlock real_data_qa / baseline /
                        paper / live.

Evidence lanes stay observation-only at all times: External Bot Evidence,
Hyperliquid Whale Evidence, Funding Rate Evidence, Bitcoin Cycle Timing
Evidence, and Daily Alpha Brief Research.

Public API:
  - DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION
  - DAILY_ALPHA_BRIEF_REVIEW_LABEL
  - DAILY_ALPHA_BRIEF_REVIEW_STATUS
  - DAILY_ALPHA_BRIEF_REVIEW_MODE
  - DAILY_ALPHA_BRIEF_REVIEW_CORE_RULE
  - DAILY_ALPHA_BRIEF_REVIEW_SAFETY_POSTURE
  - DAILY_ALPHA_BRIEF_REVIEW_OBSERVATION_ONLY_EVIDENCE_LANES
  - DAILY_ALPHA_BRIEF_REVIEW_OUTCOMES
  - OUTCOME_REJECTED / OUTCOME_PARKED / OUTCOME_NEEDS_MORE_INFO /
    OUTCOME_READY / OUTCOME_AWAIT
  - DAILY_ALPHA_BRIEF_REVIEW_STANCE
  - DAILY_ALPHA_BRIEF_REVIEW_AUTHORIZATION_FLAGS
  - DAILY_ALPHA_BRIEF_REVIEW_GATE_LOCK_FLAGS
  - DAILY_ALPHA_BRIEF_REVIEW_GATE_UNLOCK_REQUEST_FLAGS
  - DAILY_ALPHA_BRIEF_REVIEW_FORBIDDEN_TRADE_TERMS
  - DAILY_ALPHA_BRIEF_REVIEW_NEXT_REQUIRED_ACTION
  - DAILY_ALPHA_BRIEF_REVIEW_CURRENT_STAGE
  - DEFAULT_SAMPLE_UPSTREAM
  - review_daily_alpha_brief(upstream)
  - build_crypto_d1_daily_alpha_brief_review_contract(upstream=None)
  - validate_crypto_d1_daily_alpha_brief_review_contract(contract)
  - render_crypto_d1_daily_alpha_brief_review_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION",
    "DAILY_ALPHA_BRIEF_REVIEW_LABEL",
    "DAILY_ALPHA_BRIEF_REVIEW_STATUS",
    "DAILY_ALPHA_BRIEF_REVIEW_MODE",
    "DAILY_ALPHA_BRIEF_REVIEW_CORE_RULE",
    "DAILY_ALPHA_BRIEF_REVIEW_SAFETY_POSTURE",
    "DAILY_ALPHA_BRIEF_REVIEW_OBSERVATION_ONLY_EVIDENCE_LANES",
    "DAILY_ALPHA_BRIEF_REVIEW_OUTCOMES",
    "OUTCOME_REJECTED",
    "OUTCOME_PARKED",
    "OUTCOME_NEEDS_MORE_INFO",
    "OUTCOME_READY",
    "OUTCOME_AWAIT",
    "DAILY_ALPHA_BRIEF_REVIEW_STANCE",
    "DAILY_ALPHA_BRIEF_REVIEW_AUTHORIZATION_FLAGS",
    "DAILY_ALPHA_BRIEF_REVIEW_GATE_LOCK_FLAGS",
    "DAILY_ALPHA_BRIEF_REVIEW_GATE_UNLOCK_REQUEST_FLAGS",
    "DAILY_ALPHA_BRIEF_REVIEW_FORBIDDEN_TRADE_TERMS",
    "DAILY_ALPHA_BRIEF_REVIEW_NEXT_REQUIRED_ACTION",
    "DAILY_ALPHA_BRIEF_REVIEW_CURRENT_STAGE",
    "DEFAULT_SAMPLE_UPSTREAM",
    "review_daily_alpha_brief",
    "build_crypto_d1_daily_alpha_brief_review_contract",
    "validate_crypto_d1_daily_alpha_brief_review_contract",
    "render_crypto_d1_daily_alpha_brief_review_contract_markdown",
]

DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_daily_alpha_brief_review_contract.v1"
)
# The exact contract label required by the bundle spec (Block 127).
DAILY_ALPHA_BRIEF_REVIEW_LABEL = (
    "Block 127 - Crypto-D1 Daily Alpha Brief Review Contract"
)
DAILY_ALPHA_BRIEF_REVIEW_STATUS = (
    "READ_ONLY_CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT"
)
DAILY_ALPHA_BRIEF_REVIEW_MODE = "RESEARCH_ONLY"

DAILY_ALPHA_BRIEF_REVIEW_CORE_RULE = (
    "The review judges whether a daily alpha brief is safe, complete, and "
    "research-only; it never promotes a brief beyond WATCH / RESEARCH_ONLY and "
    "it authorizes nothing."
)

# The review never holds a stance higher than WATCH / RESEARCH_ONLY. Even a
# READY verdict keeps this exact stance -- a READY brief is still only research
# evidence, never a trade.
DAILY_ALPHA_BRIEF_REVIEW_STANCE = "WATCH"

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering
# this contract is the separate, later Block 128; importing the registry would
# also risk a circular import).
DAILY_ALPHA_BRIEF_REVIEW_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT"
)
DAILY_ALPHA_BRIEF_REVIEW_CURRENT_STAGE = (
    "CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_REQUIRED"
)

# Evidence lanes that remain observation-only at every review outcome. The
# review reads about them; it never wires any of them to a fetch, a QA run, a
# backtest, a trade, a broker/exchange, an order, or any automation.
DAILY_ALPHA_BRIEF_REVIEW_OBSERVATION_ONLY_EVIDENCE_LANES: tuple[str, ...] = (
    "external_bot_evidence",
    "hyperliquid_whale_evidence",
    "funding_rate_evidence",
    "bitcoin_cycle_timing_evidence",
    "daily_alpha_brief_research",
)

# Review outcomes, in precedence order (highest first). When more than one
# finding applies, the highest-precedence outcome wins.
OUTCOME_REJECTED = "REJECTED"
OUTCOME_PARKED = "PARKED"
OUTCOME_NEEDS_MORE_INFO = "NEEDS_MORE_INFO"
OUTCOME_READY = "READY"
OUTCOME_AWAIT = "AWAIT"

DAILY_ALPHA_BRIEF_REVIEW_OUTCOMES: tuple[str, ...] = (
    OUTCOME_REJECTED,
    OUTCOME_PARKED,
    OUTCOME_NEEDS_MORE_INFO,
    OUTCOME_READY,
    OUTCOME_AWAIT,
)
_OUTCOME_SET: frozenset[str] = frozenset(DAILY_ALPHA_BRIEF_REVIEW_OUTCOMES)
# Lower index == higher precedence.
_OUTCOME_PRECEDENCE: dict[str, int] = {
    OUTCOME_REJECTED: 0,
    OUTCOME_PARKED: 1,
    OUTCOME_NEEDS_MORE_INFO: 2,
    OUTCOME_READY: 3,
    OUTCOME_AWAIT: 4,
}

# Read-only safety posture. The three True flags are *posture* facts (this is a
# read-only, research-only contract that requires human approval); every
# capability/authorization flag is False.
DAILY_ALPHA_BRIEF_REVIEW_SAFETY_POSTURE: dict[str, bool] = {
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
}

# Upstream authorization flags that, if truthy, force a REJECTED verdict. (The
# ``executes`` flag is handled separately so it can be reported distinctly.)
DAILY_ALPHA_BRIEF_REVIEW_AUTHORIZATION_FLAGS: tuple[str, ...] = (
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
DAILY_ALPHA_BRIEF_REVIEW_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, force a REJECTED verdict.
DAILY_ALPHA_BRIEF_REVIEW_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
)

# Execution / promotion verbs the review's own generated guidance must never
# contain, and which (as whole words) in an upstream decision/stance signal an
# attempt to promote beyond WATCH.
DAILY_ALPHA_BRIEF_REVIEW_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
    "order",
)

# Tokens in an upstream decision/stance that indicate promotion beyond a
# research WATCH (e.g. a PASS / ACTIVE / STRONG / LIVE verdict).
_PROMOTION_TOKENS: frozenset[str] = frozenset(
    {
        "pass",
        "passed",
        "active",
        "strong",
        "approved",
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

# Upstream decision / stance values the review treats as legitimately
# research-only (anything else on those two fields is a promotion attempt).
_ALLOWED_UPSTREAM_DECISIONS: frozenset[str] = frozenset(
    {"AWAIT", "MIXED_WATCH", "NEUTRAL_WATCH", "RESEARCH_WATCH_ONLY"}
)
_ALLOWED_UPSTREAM_STANCES: frozenset[str] = frozenset(
    {"INCOMPLETE_EVIDENCE", "MIXED", "WATCH", "RESEARCH_ONLY"}
)

# The recognized daily-alpha-brief evidence lanes (used only to judge upstream
# completeness, never to fetch anything).
_BRIEF_EVIDENCE_LANES: tuple[str, ...] = (
    "external_bot_evidence_intake",
    "hyperliquid_whale_evidence",
    "funding_rate_evidence",
    "bitcoin_cycle_timing_evidence",
)

# A deterministic, illustrative paper sample modeling a complete, safe,
# research-only daily alpha brief result -> reviews as READY. Nothing here is
# real data; these are static example fields only.
DEFAULT_SAMPLE_UPSTREAM: dict[str, Any] = {
    "label": "Block 125 - Crypto-D1 Daily Alpha Brief Research Contract",
    "mode": "RESEARCH_ONLY",
    "decision": "RESEARCH_WATCH_ONLY",
    "alpha_stance": "RESEARCH_ONLY",
    "present_lanes": list(_BRIEF_EVIDENCE_LANES),
    "missing_lanes": [],
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
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
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


def _executes_findings(upstream: dict[str, Any]) -> list[str]:
    if _truthy(upstream.get("executes")):
        return ["upstream executes=True"]
    return []


def _research_only_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if upstream.get("research_only") is not True:
        reasons.append("upstream research_only is not True")
    if "read_only" in upstream and upstream.get("read_only") is not True:
        reasons.append("upstream read_only is not True")
    mode = _as_text(upstream.get("mode"))
    if mode and mode != "RESEARCH_ONLY":
        reasons.append("upstream mode is not RESEARCH_ONLY")
    return reasons


def _authorization_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for flag in DAILY_ALPHA_BRIEF_REVIEW_AUTHORIZATION_FLAGS:
        if _truthy(upstream.get(flag)):
            reasons.append("authorization flag True: " + flag)
    return reasons


def _gate_unlock_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    for flag in DAILY_ALPHA_BRIEF_REVIEW_GATE_LOCK_FLAGS:
        if flag in upstream and upstream.get(flag) is not True:
            reasons.append("gate unlock attempt: " + flag + " is not locked")
    for flag in DAILY_ALPHA_BRIEF_REVIEW_GATE_UNLOCK_REQUEST_FLAGS:
        if _truthy(upstream.get(flag)):
            reasons.append("gate unlock request: " + flag)
    return reasons


def _promotion_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if _truthy(upstream.get("promote")) or _truthy(upstream.get("promoted")):
        reasons.append("promotion requested beyond WATCH")
    decision = _as_text(upstream.get("decision"))
    if decision and decision not in _ALLOWED_UPSTREAM_DECISIONS:
        reasons.append("upstream decision promotes beyond WATCH: " + decision)
    stance = _as_text(upstream.get("alpha_stance"))
    if stance and stance not in _ALLOWED_UPSTREAM_STANCES:
        reasons.append("upstream stance promotes beyond WATCH: " + stance)
    for field in ("decision", "alpha_stance", "requested_stance", "verdict"):
        tokens = _word_tokens(_as_text(upstream.get(field)))
        hits = sorted(tokens & _PROMOTION_TOKENS)
        if hits:
            reasons.append(
                "promotion token in " + field + ": " + ", ".join(hits)
            )
    return reasons


def _park_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    requested = upstream.get("requested_forbidden_flags")
    if isinstance(requested, (list, tuple)) and len(requested) > 0:
        reasons.append(
            "upstream recorded "
            + str(len(requested))
            + " forbidden capability request(s) (never honored); human review "
            "required"
        )
    return reasons


def _needs_more_info_findings(upstream: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    missing = upstream.get("missing_lanes")
    if isinstance(missing, (list, tuple)) and len(missing) > 0:
        reasons.append(
            "upstream brief is incomplete: "
            + str(len(missing))
            + " missing evidence lane(s)"
        )
    decision = _as_text(upstream.get("decision"))
    if decision == "AWAIT":
        reasons.append("upstream brief decision is AWAIT (incomplete evidence)")
    stance = _as_text(upstream.get("alpha_stance"))
    if stance == "INCOMPLETE_EVIDENCE":
        reasons.append("upstream brief stance is INCOMPLETE_EVIDENCE")
    present = upstream.get("present_lanes")
    if isinstance(present, (list, tuple)) and 0 < len(present) < len(
        _BRIEF_EVIDENCE_LANES
    ):
        reasons.append(
            "upstream brief lists only "
            + str(len(present))
            + " of "
            + str(len(_BRIEF_EVIDENCE_LANES))
            + " evidence lanes present"
        )
    return reasons


def review_daily_alpha_brief(upstream: Any) -> dict[str, Any]:
    """Return a deterministic, research-only review verdict for an upstream
    daily-alpha-brief result. Pure; no I/O, no data fetch, no clock read, no
    mutation, no random id. Malformed / missing inputs never raise -- a missing
    upstream resolves to AWAIT. The review stance is always WATCH /
    RESEARCH_ONLY and the verdict authorizes nothing."""
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
            + _promotion_findings(src)
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
        outcome = OUTCOME_READY

    return {
        "outcome": outcome,
        "review_stance": DAILY_ALPHA_BRIEF_REVIEW_STANCE,
        "mode": DAILY_ALPHA_BRIEF_REVIEW_MODE,
        "upstream_present": present,
        "rejection_reasons": rejection_reasons,
        "park_reasons": park_reasons,
        "needs_more_info_reasons": needs_more_info_reasons,
        "promotes_beyond_watch": False,
        "authorizes_nothing": True,
    }


def _review_summary_section(review: dict[str, Any]) -> list[str]:
    return [
        "Review outcome: " + review["outcome"] + ".",
        "Review stance: "
        + review["review_stance"]
        + " / RESEARCH_ONLY (attention only).",
        "Upstream daily alpha brief present: "
        + ("yes" if review["upstream_present"] else "no")
        + ".",
        "This is a research-only review verdict; it is not a trade plan and it "
        "authorizes nothing.",
    ]


def _review_findings_section(review: dict[str, Any]) -> list[str]:
    outcome = review["outcome"]
    if outcome == OUTCOME_AWAIT:
        return [
            "No upstream daily alpha brief was supplied; there is nothing to "
            "review yet.",
            "AWAIT never resolves to an execution decision.",
        ]
    if outcome == OUTCOME_REJECTED:
        lines = ["Upstream brief REJECTED; it is not safe research-only state:"]
        lines.extend("- " + reason for reason in review["rejection_reasons"])
        lines.append(
            "Rejection authorizes nothing and unlocks no gate; the brief must "
            "be rebuilt as research-only."
        )
        return lines
    if outcome == OUTCOME_PARKED:
        lines = ["Upstream brief PARKED for human attention:"]
        lines.extend("- " + reason for reason in review["park_reasons"])
        lines.append(
            "Parking authorizes nothing; a human must inspect before any "
            "further research-only contract is built."
        )
        return lines
    if outcome == OUTCOME_NEEDS_MORE_INFO:
        lines = ["Upstream brief is safe but incomplete:"]
        lines.extend(
            "- " + reason for reason in review["needs_more_info_reasons"]
        )
        lines.append(
            "Incomplete evidence resolves to NEEDS_MORE_INFO; it never resolves "
            "to an execution decision."
        )
        return lines
    return [
        "Upstream brief is complete, safe, and research-only; it may be read by "
        "a human as research evidence.",
        "READY is the highest verdict and it still authorizes nothing; the "
        "review stance stays WATCH / RESEARCH_ONLY.",
    ]


def _observation_only_section() -> list[str]:
    lines = [
        lane + " remains observation-only (attention only)."
        for lane in DAILY_ALPHA_BRIEF_REVIEW_OBSERVATION_ONLY_EVIDENCE_LANES
    ]
    lines.append(
        "No evidence lane is ever wired to a data fetch, an API call, a "
        "dataset, a QA run, a backtest, a paper/live trade, a broker or "
        "exchange, or any automation."
    )
    return lines


_NO_EXECUTION_AUTHORIZATION_SECTION: tuple[str, ...] = (
    "This review authorizes no trade and no position of any kind.",
    "It permits no data fetch, no API call, no dataset inspection, no QA, no "
    "baseline, and no backtest.",
    "It permits no paper trading, no live trading, no broker or exchange "
    "connection, and no automation.",
    "It writes no runtime, registry, ledger, or dashboard state.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
    "The highest stance it can hold is WATCH / RESEARCH_ONLY; it never promotes "
    "a brief and never produces an execution instruction.",
)

_OPERATOR_NEXT_STEP = (
    "Research-only: a human reviewer must read this review verdict, "
    "independently confirm every finding, and treat the upstream brief as "
    "attention-only research evidence. The single permitted next step is to "
    "register or assemble the next research-only contract on paper. No "
    "execution of any kind is authorized."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 daily alpha brief review contract template and is "
    "execution-free.",
    "It inspects an already-produced static daily alpha brief result and "
    "reports whether it is safe, complete, and research-only; it runs nothing, "
    "fetches nothing, and connects nowhere.",
    "Core rule: the review judges what to watch and research, never what to "
    "trade, and never promotes a brief beyond WATCH / RESEARCH_ONLY.",
    "Outcome precedence is REJECTED > PARKED > NEEDS_MORE_INFO > READY > "
    "AWAIT; a missing upstream resolves to AWAIT.",
    "An unsafe upstream (executes=True, not research_only, any authorization "
    "flag True, any promotion beyond WATCH, or any gate unlock request) "
    "resolves to REJECTED and unlocks nothing.",
    "Every finding is attention-only and needs independent confirmation; the "
    "review never converts evidence into permission.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human reviewer must read the structured review verdict before any "
    "further research-only contract is built.",
    "A human reviewer must confirm each finding is treated as attention-only "
    "evidence and is never wired to a data fetch, an API call, a dataset, a QA "
    "run, a backtest, a paper/live trade, a broker or exchange, an order, or "
    "any automation.",
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
    "review_next_required_action",
    "review_current_stage",
    "observation_only_evidence_lanes",
    "outcomes",
    "review_stance",
    "authorization_flags",
    "gate_lock_flags",
    "gate_unlock_request_flags",
    "forbidden_trade_terms",
    "upstream",
    "review",
    "outcome",
    "upstream_present",
    "rejection_reasons",
    "park_reasons",
    "needs_more_info_reasons",
    "review_summary_section",
    "review_findings_section",
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
    "promotes_beyond_watch",
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the posture (callers cannot taint the global)."""
    return dict(DAILY_ALPHA_BRIEF_REVIEW_SAFETY_POSTURE)


def build_crypto_d1_daily_alpha_brief_review_contract(
    upstream: Any = None,
) -> dict[str, Any]:
    """Build the read-only daily alpha brief review contract. Pure; no I/O, no
    data fetch, no mutation of inputs, no clock read, no random id. When no
    upstream is given, the static DEFAULT_SAMPLE_UPSTREAM is reviewed. A fresh
    dict (with fresh lists/dicts) is returned every call. The contract never
    holds a stance higher than WATCH / RESEARCH_ONLY and authorizes nothing."""
    if upstream is None:
        source = _isolated(DEFAULT_SAMPLE_UPSTREAM)
    elif isinstance(upstream, dict):
        source = _isolated(upstream)
    else:
        source = upstream

    review = review_daily_alpha_brief(source)

    contract: dict[str, Any] = {
        "schema_version": DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION,
        "label": DAILY_ALPHA_BRIEF_REVIEW_LABEL,
        "status": DAILY_ALPHA_BRIEF_REVIEW_STATUS,
        "stage": "CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_ONLY",
        "mode": DAILY_ALPHA_BRIEF_REVIEW_MODE,
        "core_rule": DAILY_ALPHA_BRIEF_REVIEW_CORE_RULE,
        "review_next_required_action": (
            DAILY_ALPHA_BRIEF_REVIEW_NEXT_REQUIRED_ACTION
        ),
        "review_current_stage": DAILY_ALPHA_BRIEF_REVIEW_CURRENT_STAGE,
        "observation_only_evidence_lanes": (
            DAILY_ALPHA_BRIEF_REVIEW_OBSERVATION_ONLY_EVIDENCE_LANES
        ),
        "outcomes": DAILY_ALPHA_BRIEF_REVIEW_OUTCOMES,
        "review_stance": DAILY_ALPHA_BRIEF_REVIEW_STANCE,
        "authorization_flags": DAILY_ALPHA_BRIEF_REVIEW_AUTHORIZATION_FLAGS,
        "gate_lock_flags": DAILY_ALPHA_BRIEF_REVIEW_GATE_LOCK_FLAGS,
        "gate_unlock_request_flags": (
            DAILY_ALPHA_BRIEF_REVIEW_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_trade_terms": DAILY_ALPHA_BRIEF_REVIEW_FORBIDDEN_TRADE_TERMS,
        "upstream": _isolated(source) if isinstance(source, dict) else {},
        "review": review,
        "outcome": review["outcome"],
        "upstream_present": review["upstream_present"],
        "rejection_reasons": list(review["rejection_reasons"]),
        "park_reasons": list(review["park_reasons"]),
        "needs_more_info_reasons": list(review["needs_more_info_reasons"]),
        "review_summary_section": _review_summary_section(review),
        "review_findings_section": _review_findings_section(review),
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
    "promotes_beyond_watch",
)

# The generated-guidance fields whose text is the review's own actionable
# output. These must never contain an execution verb. (The raw echoed
# ``upstream`` is caller input, not the review's guidance, and is excluded.)
_ACTIONABLE_TEXT_FIELDS: tuple[str, ...] = (
    "outcome",
    "review_stance",
    "operator_next_step",
    "review_summary_section",
    "review_findings_section",
    "observation_only_section",
    "no_execution_authorization_section",
)


def _contains_forbidden_term(text: str) -> bool:
    tokens = _word_tokens(text)
    return any(
        term in tokens
        for term in DAILY_ALPHA_BRIEF_REVIEW_FORBIDDEN_TRADE_TERMS
    )


def _no_forbidden_trade_terms(contract: dict[str, Any]) -> bool:
    """True when none of the review's actionable guidance fields contain an
    execution verb as a whole word. Pure; reads only the contract dict.

    The findings section can legitimately echo an upstream rejection reason that
    quotes a promotion token (e.g. a rejected upstream stance), so that section
    is judged by whether it is reporting a REJECTED verdict rather than issuing
    an instruction."""
    rejected = contract.get("outcome") == OUTCOME_REJECTED
    for field in _ACTIONABLE_TEXT_FIELDS:
        if field == "review_findings_section" and rejected:
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
        safe.get("schema_version") == DAILY_ALPHA_BRIEF_REVIEW_SCHEMA_VERSION
    )
    label_ok = safe.get("label") == DAILY_ALPHA_BRIEF_REVIEW_LABEL
    read_only = safe.get("read_only") is True
    research_only = (
        safe.get("research_only") is True
        and safe.get("mode") == "RESEARCH_ONLY"
    )
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_DAILY_ALPHA_BRIEF_REVIEW_CONTRACT_ONLY"
    )
    core_rule_ok = safe.get("core_rule") == DAILY_ALPHA_BRIEF_REVIEW_CORE_RULE
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
        and posture == DAILY_ALPHA_BRIEF_REVIEW_SAFETY_POSTURE
    )

    outcome_ok = safe.get("outcome") in _OUTCOME_SET
    stance_ok = safe.get("review_stance") == DAILY_ALPHA_BRIEF_REVIEW_STANCE

    lanes_ok = (
        tuple(safe.get("observation_only_evidence_lanes") or ())
        == DAILY_ALPHA_BRIEF_REVIEW_OBSERVATION_ONLY_EVIDENCE_LANES
    )
    outcomes_ok = (
        tuple(safe.get("outcomes") or ()) == DAILY_ALPHA_BRIEF_REVIEW_OUTCOMES
    )

    review = safe.get("review")
    review_ok = (
        isinstance(review, dict)
        and review.get("authorizes_nothing") is True
        and review.get("outcome") in _OUTCOME_SET
        and review.get("review_stance") == DAILY_ALPHA_BRIEF_REVIEW_STANCE
    )

    no_trade_language = _no_forbidden_trade_terms(safe)

    sections_ok = all(
        len(tuple(safe.get(section) or ())) >= 1
        for section in (
            "review_summary_section",
            "review_findings_section",
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
        and human_required
        and confirmation_required
        and flags_false
        and gates_locked
        and posture_ok
        and outcome_ok
        and stance_ok
        and lanes_ok
        and outcomes_ok
        and review_ok
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
        "human_required": human_required,
        "confirmation_required": confirmation_required,
        "flags_false": flags_false,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "outcome_ok": outcome_ok,
        "stance_ok": stance_ok,
        "lanes_ok": lanes_ok,
        "outcomes_ok": outcomes_ok,
        "review_ok": review_ok,
        "no_trade_language": no_trade_language,
        "sections_ok": sections_ok,
        "operator_next_step_ok": operator_next_step_ok,
    }


def validate_crypto_d1_daily_alpha_brief_review_contract(
    contract: Any,
) -> dict[str, Any]:
    """Public validation entry point; returns the deterministic verdict dict."""
    return _validate(contract)


def render_crypto_d1_daily_alpha_brief_review_contract_markdown(
    contract: Any,
) -> str:
    """Render an informational, read-only markdown summary of the contract.
    Pure; builds and returns a string, writes nothing."""
    safe = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Daily Alpha Brief Review Contract")
    lines.append("")
    lines.append("- Label: " + _as_text(safe.get("label")))
    lines.append("- Mode: " + _as_text(safe.get("mode")))
    lines.append("- Status: " + _as_text(safe.get("status")))
    lines.append("- Outcome: " + _as_text(safe.get("outcome")))
    lines.append("- Review stance: " + _as_text(safe.get("review_stance")))
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

    _emit("Review Summary", "review_summary_section")
    _emit("Review Findings", "review_findings_section")
    _emit("Observation-Only Evidence Lanes", "observation_only_section")
    _emit("No Execution Authorization", "no_execution_authorization_section")
    lines.append("")
    lines.append("## Operator Next Step")
    lines.append("- " + _as_text(safe.get("operator_next_step")))
    return "\n".join(lines)

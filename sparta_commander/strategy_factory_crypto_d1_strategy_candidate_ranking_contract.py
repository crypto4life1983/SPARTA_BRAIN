"""SPARTA Offline Strategy Factory - CRYPTO-D1 STRATEGY CANDIDATE RANKING.

A PURE, stdlib-only *read-only paper contract* that *ranks* a small,
caller-provided set of already-scored strategy candidates and sorts the whole
set into exactly one research-only verdict plus a deterministic per-candidate
review tier. It returns a deterministic, structured ranking result: the verdict,
the ordered shortlist, the per-candidate tiers, the penalties applied, and a
plain-language explanation -- so a human can decide, on paper, which strategy
candidates (if any) are worth a research review.

CORE RULE: a candidate's rank follows its evidence verdict first (a verdict
produced earlier, on paper, by the strategy-evidence-scoring contract), then its
count of INDEPENDENT positive booked cohorts, then a deterministic id tie-break.
The ranking can ONLY sort candidates into SHORTLIST_FOR_REVIEW / NO_SHORTLIST /
NEEDS_MORE_CANDIDATES / BLOCK for human research review. Being ranked #1 means
ONLY that a human may *review* that candidate first; top rank is not selection,
authorizes nothing, and unlocks no gate.

Ranking principles (all applied deterministically, on paper):
  - A candidate is only shortlist-eligible if its evidence verdict is
    PROMOTE_TO_REVIEW with enough INDEPENDENT positive booked cohorts; a
    NEEDS_MORE_DATA candidate is HOLD, a KEEP_WATCH candidate is WATCH.
  - Independent positive cohorts outrank raw booked counts; correlated piles do
    not lift a candidate above an independent one.
  - Ties break deterministically on candidate id so the order never depends on
    insertion order, a clock, or a random seed.
  - Any unsafe candidate (an authorization flag, a gate-unlock or
    forbidden-promotion request, or an executable order/signal field) forces the
    whole verdict to BLOCK.

This contract authorizes NOTHING real. It does NOT fetch any data, call any API,
inspect any dataset, acquire any real data, load any file, open any network, run
any QA, baseline, backtest, or simulation, produce any trade signal, reach any
broker / exchange / order / account / API surface, trade any paper and any live,
promote any candidate beyond a research review, unlock any downstream gate
(real_data_qa, baseline_backtest, paper_trading_gate, micro_live_gate stay
blocked / locked), trigger any automation, write any runtime / registry /
ledger / dashboard / report state, spawn any child process, read any
environment, record any wall-clock time, mint any random id, or dynamically
import anything. It ONLY inspects the static candidate records the caller passes
in, using pure dict / string / number arithmetic.

Ranking outcomes (precedence, highest first / most restrictive first):
    BLOCK > NEEDS_MORE_CANDIDATES > NO_SHORTLIST > SHORTLIST_FOR_REVIEW
  - BLOCK                -> the payload is unsafe: an authorization flag is set, a
                            gate-unlock or forbidden-promotion request is present,
                            or a candidate carries an executable order/signal
                            field.
  - NEEDS_MORE_CANDIDATES-> there are no candidates to rank yet; supply static
                            already-scored candidates for a future review.
  - NO_SHORTLIST         -> candidates exist, but none qualifies for the review
                            shortlist (all HOLD / WATCH). Keep researching.
  - SHORTLIST_FOR_REVIEW -> one or more candidates qualify; a human may REVIEW the
                            ordered shortlist. This unlocks nothing.

Public API:
  - STRATEGY_CANDIDATE_RANKING_SCHEMA_VERSION
  - STRATEGY_CANDIDATE_RANKING_LABEL
  - STRATEGY_CANDIDATE_RANKING_STATUS
  - STRATEGY_CANDIDATE_RANKING_MODE
  - STRATEGY_CANDIDATE_RANKING_CORE_RULE
  - STRATEGY_CANDIDATE_RANKING_SAFETY_POSTURE
  - STRATEGY_CANDIDATE_RANKING_OBSERVATION_ONLY_EVIDENCE_LANES
  - STRATEGY_CANDIDATE_RANKING_OUTCOMES
  - OUTCOME_BLOCK / OUTCOME_NEEDS_MORE_CANDIDATES / OUTCOME_NO_SHORTLIST /
    OUTCOME_SHORTLIST_FOR_REVIEW
  - STRATEGY_CANDIDATE_RANKING_TIERS
  - TIER_BLOCK / TIER_HOLD / TIER_WATCH / TIER_REVIEW_SHORTLIST
  - STRATEGY_CANDIDATE_RANKING_MIN_INDEPENDENT_COHORTS_FOR_SHORTLIST
  - STRATEGY_CANDIDATE_RANKING_EVIDENCE_OUTCOMES
  - STRATEGY_CANDIDATE_RANKING_SHORTLIST_ELIGIBLE_EVIDENCE_OUTCOMES
  - STRATEGY_CANDIDATE_RANKING_AUTHORIZATION_FLAGS
  - STRATEGY_CANDIDATE_RANKING_GATE_LOCK_FLAGS
  - STRATEGY_CANDIDATE_RANKING_GATE_UNLOCK_REQUEST_FLAGS
  - STRATEGY_CANDIDATE_RANKING_FORBIDDEN_PROMOTION_REQUEST_FLAGS
  - STRATEGY_CANDIDATE_RANKING_EXECUTABLE_SIGNAL_FIELDS
  - STRATEGY_CANDIDATE_RANKING_FORBIDDEN_TRADE_TERMS
  - STRATEGY_CANDIDATE_RANKING_NEXT_REQUIRED_ACTION
  - STRATEGY_CANDIDATE_RANKING_CURRENT_STAGE
  - DEFAULT_SAMPLE_CANDIDATES
  - rank_strategy_candidates(payload)
  - build_crypto_d1_strategy_candidate_ranking_contract(payload=None)
  - validate_crypto_d1_strategy_candidate_ranking_contract(contract)
  - render_crypto_d1_strategy_candidate_ranking_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "STRATEGY_CANDIDATE_RANKING_SCHEMA_VERSION",
    "STRATEGY_CANDIDATE_RANKING_LABEL",
    "STRATEGY_CANDIDATE_RANKING_STATUS",
    "STRATEGY_CANDIDATE_RANKING_MODE",
    "STRATEGY_CANDIDATE_RANKING_CORE_RULE",
    "STRATEGY_CANDIDATE_RANKING_SAFETY_POSTURE",
    "STRATEGY_CANDIDATE_RANKING_OBSERVATION_ONLY_EVIDENCE_LANES",
    "STRATEGY_CANDIDATE_RANKING_OUTCOMES",
    "OUTCOME_BLOCK",
    "OUTCOME_NEEDS_MORE_CANDIDATES",
    "OUTCOME_NO_SHORTLIST",
    "OUTCOME_SHORTLIST_FOR_REVIEW",
    "STRATEGY_CANDIDATE_RANKING_TIERS",
    "TIER_BLOCK",
    "TIER_HOLD",
    "TIER_WATCH",
    "TIER_REVIEW_SHORTLIST",
    "STRATEGY_CANDIDATE_RANKING_MIN_INDEPENDENT_COHORTS_FOR_SHORTLIST",
    "STRATEGY_CANDIDATE_RANKING_EVIDENCE_OUTCOMES",
    "STRATEGY_CANDIDATE_RANKING_SHORTLIST_ELIGIBLE_EVIDENCE_OUTCOMES",
    "STRATEGY_CANDIDATE_RANKING_AUTHORIZATION_FLAGS",
    "STRATEGY_CANDIDATE_RANKING_GATE_LOCK_FLAGS",
    "STRATEGY_CANDIDATE_RANKING_GATE_UNLOCK_REQUEST_FLAGS",
    "STRATEGY_CANDIDATE_RANKING_FORBIDDEN_PROMOTION_REQUEST_FLAGS",
    "STRATEGY_CANDIDATE_RANKING_EXECUTABLE_SIGNAL_FIELDS",
    "STRATEGY_CANDIDATE_RANKING_FORBIDDEN_TRADE_TERMS",
    "STRATEGY_CANDIDATE_RANKING_NEXT_REQUIRED_ACTION",
    "STRATEGY_CANDIDATE_RANKING_CURRENT_STAGE",
    "DEFAULT_SAMPLE_CANDIDATES",
    "rank_strategy_candidates",
    "build_crypto_d1_strategy_candidate_ranking_contract",
    "validate_crypto_d1_strategy_candidate_ranking_contract",
    "render_crypto_d1_strategy_candidate_ranking_contract_markdown",
]

STRATEGY_CANDIDATE_RANKING_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_strategy_candidate_ranking_contract.v1"
)
STRATEGY_CANDIDATE_RANKING_LABEL = (
    "Block 162 - Crypto-D1 Strategy Candidate Ranking Contract"
)
STRATEGY_CANDIDATE_RANKING_STATUS = (
    "READ_ONLY_CRYPTO_D1_STRATEGY_CANDIDATE_RANKING_CONTRACT"
)
STRATEGY_CANDIDATE_RANKING_MODE = "RESEARCH_ONLY"

STRATEGY_CANDIDATE_RANKING_CORE_RULE = (
    "A candidate's rank follows its evidence verdict first, then its count of "
    "independent positive booked cohorts, then a deterministic id tie-break; the "
    "ranking can only sort candidates into SHORTLIST_FOR_REVIEW / NO_SHORTLIST / "
    "NEEDS_MORE_CANDIDATES / BLOCK for human research review, and it authorizes "
    "nothing."
)

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering
# this contract is the separate, later step; importing the registry would also
# risk a circular import).
STRATEGY_CANDIDATE_RANKING_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_CANDIDATE_RANKING_CONTRACT"
)
STRATEGY_CANDIDATE_RANKING_CURRENT_STAGE = (
    "CRYPTO_D1_STRATEGY_CANDIDATE_RANKING_CONTRACT_REQUIRED"
)

# A candidate is only shortlist-eligible when its evidence verdict carries at
# least this many INDEPENDENT positive booked cohorts. A correlated pile is not
# enough.
STRATEGY_CANDIDATE_RANKING_MIN_INDEPENDENT_COHORTS_FOR_SHORTLIST = 3

# Evidence lanes that remain observation-only at every ranking outcome. The
# ranking reads about them; it never wires any of them to a fetch, a QA run, a
# backtest, a trade, a broker/exchange, an order, or any automation.
STRATEGY_CANDIDATE_RANKING_OBSERVATION_ONLY_EVIDENCE_LANES: tuple[str, ...] = (
    "external_bot_evidence",
    "external_human_trader_evidence",
    "hyperliquid_whale_evidence",
    "funding_rate_evidence",
    "bitcoin_cycle_timing_evidence",
    "daily_alpha_brief",
    "open_unrealized_pnl",
)

# Ranking outcomes, in precedence order (highest / most restrictive first).
OUTCOME_BLOCK = "BLOCK"
OUTCOME_NEEDS_MORE_CANDIDATES = "NEEDS_MORE_CANDIDATES"
OUTCOME_NO_SHORTLIST = "NO_SHORTLIST"
OUTCOME_SHORTLIST_FOR_REVIEW = "SHORTLIST_FOR_REVIEW"

STRATEGY_CANDIDATE_RANKING_OUTCOMES: tuple[str, ...] = (
    OUTCOME_BLOCK,
    OUTCOME_NEEDS_MORE_CANDIDATES,
    OUTCOME_NO_SHORTLIST,
    OUTCOME_SHORTLIST_FOR_REVIEW,
)
_OUTCOME_SET: frozenset[str] = frozenset(STRATEGY_CANDIDATE_RANKING_OUTCOMES)
# Lower index == higher precedence / more restrictive.
_OUTCOME_PRECEDENCE: dict[str, int] = {
    OUTCOME_BLOCK: 0,
    OUTCOME_NEEDS_MORE_CANDIDATES: 1,
    OUTCOME_NO_SHORTLIST: 2,
    OUTCOME_SHORTLIST_FOR_REVIEW: 3,
}

# Per-candidate review tiers (research-review only; never selection).
TIER_BLOCK = "TIER_BLOCK"
TIER_HOLD = "TIER_HOLD"
TIER_WATCH = "TIER_WATCH"
TIER_REVIEW_SHORTLIST = "TIER_REVIEW_SHORTLIST"

STRATEGY_CANDIDATE_RANKING_TIERS: tuple[str, ...] = (
    TIER_BLOCK,
    TIER_HOLD,
    TIER_WATCH,
    TIER_REVIEW_SHORTLIST,
)

# Evidence verdicts a candidate may carry (produced earlier, on paper, by the
# strategy-evidence-scoring contract). An empty / unknown verdict is treated as
# the most conservative non-shortlist verdict (KEEP_WATCH).
_EVIDENCE_OUTCOME_BLOCK = "BLOCK"
_EVIDENCE_OUTCOME_NEEDS_MORE_DATA = "NEEDS_MORE_DATA"
_EVIDENCE_OUTCOME_KEEP_WATCH = "KEEP_WATCH"
_EVIDENCE_OUTCOME_PROMOTE_TO_REVIEW = "PROMOTE_TO_REVIEW"

STRATEGY_CANDIDATE_RANKING_EVIDENCE_OUTCOMES: tuple[str, ...] = (
    _EVIDENCE_OUTCOME_BLOCK,
    _EVIDENCE_OUTCOME_NEEDS_MORE_DATA,
    _EVIDENCE_OUTCOME_KEEP_WATCH,
    _EVIDENCE_OUTCOME_PROMOTE_TO_REVIEW,
)
_EVIDENCE_OUTCOME_SET: frozenset[str] = frozenset(
    STRATEGY_CANDIDATE_RANKING_EVIDENCE_OUTCOMES
)

# Only candidates whose evidence verdict is in this set may enter the review
# shortlist (still gated on the independent-cohort minimum).
STRATEGY_CANDIDATE_RANKING_SHORTLIST_ELIGIBLE_EVIDENCE_OUTCOMES: tuple[
    str, ...
] = (_EVIDENCE_OUTCOME_PROMOTE_TO_REVIEW,)
_SHORTLIST_ELIGIBLE_SET: frozenset[str] = frozenset(
    STRATEGY_CANDIDATE_RANKING_SHORTLIST_ELIGIBLE_EVIDENCE_OUTCOMES
)

# Top-level (or per-candidate) authorization flags that, if truthy, force BLOCK.
STRATEGY_CANDIDATE_RANKING_AUTHORIZATION_FLAGS: tuple[str, ...] = (
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

# Gate-lock flags that MUST be True (blocked / locked). If present and not True,
# the payload tried to unlock a gate -> BLOCK.
STRATEGY_CANDIDATE_RANKING_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, force BLOCK.
STRATEGY_CANDIDATE_RANKING_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
)

# Requests asking the ranking to mean execution / live promotion. Any truthy
# value forces BLOCK: a verdict can only ever mean a research-review sort.
STRATEGY_CANDIDATE_RANKING_FORBIDDEN_PROMOTION_REQUEST_FLAGS: tuple[str, ...] = (
    "force_promote",
    "promote_to_live",
    "promote_to_paper",
    "approve_trade",
    "authorize_trade",
    "execute",
    "place_order",
    "go_live",
    "select_for_trading",
)

# Fields whose presence (non-empty) on a candidate signals an executable order /
# signal instruction rather than historical ranking metadata -> BLOCK.
STRATEGY_CANDIDATE_RANKING_EXECUTABLE_SIGNAL_FIELDS: tuple[str, ...] = (
    "order",
    "signal",
    "trade_instruction",
    "execution",
    "live_order",
    "place_order",
)

# Execution / promotion verbs the ranking's own generated guidance must never
# contain as whole words.
STRATEGY_CANDIDATE_RANKING_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
    "order",
)

# Read-only safety posture. The three True flags are *posture* facts (this is a
# read-only, research-only contract that requires human approval); every
# capability / authorization / unlock flag is False.
STRATEGY_CANDIDATE_RANKING_SAFETY_POSTURE: dict[str, bool] = {
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


# A deterministic, illustrative paper sample: four already-scored candidates.
# Only one carries a PROMOTE_TO_REVIEW verdict with enough independent positive
# cohorts, so the default build scores SHORTLIST_FOR_REVIEW with a one-candidate
# shortlist. Nothing here is real data; static example only.
DEFAULT_SAMPLE_CANDIDATES: dict[str, Any] = {
    "label": "Crypto-D1 strategy candidate ranking (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "research_only": True,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
    "candidates": [
        {
            "id": "cand_btc_trend",
            "family": "trend_breakout_d1",
            "universe": "BTC",
            "evidence_outcome": "PROMOTE_TO_REVIEW",
            "independent_positive_cohorts": 4,
            "booked_count": 9,
        },
        {
            "id": "cand_eth_meanrev",
            "family": "mean_reversion_d1",
            "universe": "ETH",
            "evidence_outcome": "NEEDS_MORE_DATA",
            "independent_positive_cohorts": 1,
            "booked_count": 3,
        },
        {
            "id": "cand_sol_carry",
            "family": "carry_d1",
            "universe": "SOL",
            "evidence_outcome": "KEEP_WATCH",
            "independent_positive_cohorts": 0,
            "booked_count": 0,
        },
        {
            "id": "cand_btc_momo",
            "family": "momentum_d1",
            "universe": "BTC",
            "evidence_outcome": "PROMOTE_TO_REVIEW",
            "independent_positive_cohorts": 2,
            "booked_count": 5,
        },
    ],
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


def _as_int(value: Any) -> int:
    """Coerce a caller count to a non-negative int; bad/negative -> 0. Bools 0."""
    if isinstance(value, bool):
        return 0
    if isinstance(value, int):
        return value if value > 0 else 0
    if isinstance(value, float):
        ivalue = int(value)
        return ivalue if ivalue > 0 else 0
    if isinstance(value, str):
        try:
            ivalue = int(float(value.strip()))
        except ValueError:
            return 0
        return ivalue if ivalue > 0 else 0
    return 0


def _candidate_id(candidate: dict[str, Any], index: int) -> str:
    cid = _as_text(candidate.get("id"))
    return cid if cid else "#" + str(index)


def _evidence_outcome(candidate: dict[str, Any]) -> str:
    """The candidate's already-produced evidence verdict; unknown -> KEEP_WATCH
    (the most conservative non-shortlist verdict)."""
    outcome = _as_text(candidate.get("evidence_outcome")).upper()
    if outcome in _EVIDENCE_OUTCOME_SET:
        return outcome
    return _EVIDENCE_OUTCOME_KEEP_WATCH


def _safety_block_findings(
    controls: dict[str, Any], candidates: list[dict[str, Any]]
) -> list[str]:
    """Reasons the whole payload is unsafe and must score BLOCK. Pure."""
    reasons: list[str] = []
    for flag in STRATEGY_CANDIDATE_RANKING_AUTHORIZATION_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("authorization flag requested: " + flag)
    for flag in STRATEGY_CANDIDATE_RANKING_GATE_LOCK_FLAGS:
        if flag in controls and controls.get(flag) is not True:
            reasons.append("gate unlock attempt: " + flag + " is not locked")
    for flag in STRATEGY_CANDIDATE_RANKING_GATE_UNLOCK_REQUEST_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("gate unlock request: " + flag)
    for flag in STRATEGY_CANDIDATE_RANKING_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("forbidden promotion/execution request: " + flag)
    for index, candidate in enumerate(candidates):
        cid = _candidate_id(candidate, index)
        for field in STRATEGY_CANDIDATE_RANKING_EXECUTABLE_SIGNAL_FIELDS:
            if field in candidate and _non_empty(candidate.get(field)):
                reasons.append(
                    "candidate " + cid + " carries executable field: " + field
                )
        for flag in (
            STRATEGY_CANDIDATE_RANKING_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ):
            if _truthy(candidate.get(flag)):
                reasons.append(
                    "candidate "
                    + cid
                    + " requests forbidden promotion/execution: "
                    + flag
                )
        for flag in STRATEGY_CANDIDATE_RANKING_AUTHORIZATION_FLAGS:
            if _truthy(candidate.get(flag)):
                reasons.append(
                    "candidate " + cid + " requests authorization: " + flag
                )
    return reasons


def _candidate_tier(evidence_outcome: str, independent_positive: int) -> str:
    """Deterministic per-candidate review tier from its evidence verdict and
    independent positive cohort count."""
    if evidence_outcome == _EVIDENCE_OUTCOME_BLOCK:
        return TIER_BLOCK
    if (
        evidence_outcome in _SHORTLIST_ELIGIBLE_SET
        and independent_positive
        >= STRATEGY_CANDIDATE_RANKING_MIN_INDEPENDENT_COHORTS_FOR_SHORTLIST
    ):
        return TIER_REVIEW_SHORTLIST
    if evidence_outcome == _EVIDENCE_OUTCOME_KEEP_WATCH:
        return TIER_WATCH
    # PROMOTE_TO_REVIEW with too few independent cohorts, or NEEDS_MORE_DATA.
    return TIER_HOLD


def _ranking_explanations(
    outcome: str,
    candidate_count: int,
    shortlist_count: int,
    hold_count: int,
    watch_count: int,
    blocked_candidate_count: int,
    min_cohorts: int,
) -> list[str]:
    """Plain-language rationale for the verdict. References counts only (never a
    raw candidate family or universe), so the guidance never emits an execution
    verb."""
    lines = [
        "Ranked "
        + str(candidate_count)
        + " candidate(s): "
        + str(shortlist_count)
        + " shortlist, "
        + str(hold_count)
        + " hold, "
        + str(watch_count)
        + " watch, "
        + str(blocked_candidate_count)
        + " blocked.",
        "A candidate is shortlist-eligible only with a PROMOTE_TO_REVIEW "
        "evidence verdict and at least "
        + str(min_cohorts)
        + " independent positive booked cohort(s).",
    ]
    if outcome == OUTCOME_BLOCK:
        lines.append(
            "Verdict BLOCK: the payload requested an authorization, a gate "
            "unlock, a forbidden promotion, or carried an executable field; the "
            "ranking refuses it and authorizes nothing."
        )
    elif outcome == OUTCOME_NEEDS_MORE_CANDIDATES:
        lines.append(
            "Verdict NEEDS_MORE_CANDIDATES: there is nothing to rank yet; "
            "supply static already-scored candidates for a future research "
            "review."
        )
    elif outcome == OUTCOME_NO_SHORTLIST:
        lines.append(
            "Verdict NO_SHORTLIST: candidates exist but none qualifies for the "
            "review shortlist (all hold or watch); keep researching on paper."
        )
    else:
        lines.append(
            "Verdict SHORTLIST_FOR_REVIEW: one or more candidates qualify, so a "
            "human may REVIEW the ordered shortlist. Being ranked first is not "
            "selection; it unlocks no QA, no baseline, no backtest, no paper, no "
            "live, no broker/exchange, and no automation."
        )
    return lines


def rank_strategy_candidates(payload: Any) -> dict[str, Any]:
    """Return a deterministic, research-only ranking for a static candidate
    payload.

    Pure; no I/O, no data fetch, no clock read, no mutation, no random id.
    Malformed / missing inputs never raise. ``payload`` may be a list of
    candidate records, or a dict carrying a ``candidates`` list plus optional
    control flags. The verdict is one of BLOCK / NEEDS_MORE_CANDIDATES /
    NO_SHORTLIST / SHORTLIST_FOR_REVIEW; SHORTLIST_FOR_REVIEW only authorizes a
    human research review and unlocks nothing."""
    if isinstance(payload, dict):
        controls = payload
        raw_candidates = payload.get("candidates")
    elif isinstance(payload, (list, tuple)):
        controls = {}
        raw_candidates = payload
    else:
        controls = {}
        raw_candidates = None

    if isinstance(raw_candidates, (list, tuple)):
        candidates = [c for c in raw_candidates if isinstance(c, dict)]
    else:
        candidates = []

    block_reasons = _safety_block_findings(controls, candidates)

    min_cohorts = (
        STRATEGY_CANDIDATE_RANKING_MIN_INDEPENDENT_COHORTS_FOR_SHORTLIST
    )

    tiered: list[dict[str, Any]] = []
    for index, candidate in enumerate(candidates):
        cid = _candidate_id(candidate, index)
        evidence_outcome = _evidence_outcome(candidate)
        independent_positive = _as_int(
            candidate.get("independent_positive_cohorts")
        )
        booked = _as_int(candidate.get("booked_count"))
        tier = _candidate_tier(evidence_outcome, independent_positive)
        tiered.append(
            {
                "id": cid,
                "family": _as_text(candidate.get("family")),
                "universe": _as_text(candidate.get("universe")),
                "evidence_outcome": evidence_outcome,
                "independent_positive_cohorts": independent_positive,
                "booked_count": booked,
                "tier": tier,
            }
        )

    shortlist_entries = [t for t in tiered if t["tier"] == TIER_REVIEW_SHORTLIST]
    hold_count = sum(1 for t in tiered if t["tier"] == TIER_HOLD)
    watch_count = sum(1 for t in tiered if t["tier"] == TIER_WATCH)
    blocked_candidate_count = sum(1 for t in tiered if t["tier"] == TIER_BLOCK)

    # Deterministic order: more independent positive cohorts first, then more
    # booked records, then candidate id ascending. Never insertion order.
    ranked_shortlist = sorted(
        shortlist_entries,
        key=lambda t: (
            -t["independent_positive_cohorts"],
            -t["booked_count"],
            t["id"],
        ),
    )
    ranked_shortlist_ids = [t["id"] for t in ranked_shortlist]

    tier_summaries: list[str] = []
    for entry in sorted(tiered, key=lambda t: t["id"]):
        tier_summaries.append(
            "Candidate "
            + entry["id"]
            + ": evidence "
            + entry["evidence_outcome"]
            + ", "
            + str(entry["independent_positive_cohorts"])
            + " independent positive cohort(s) -> "
            + entry["tier"]
            + "."
        )

    penalty_findings: list[str] = []
    promote_but_thin = sum(
        1
        for t in tiered
        if t["evidence_outcome"] == _EVIDENCE_OUTCOME_PROMOTE_TO_REVIEW
        and t["tier"] != TIER_REVIEW_SHORTLIST
    )
    if promote_but_thin > 0:
        penalty_findings.append(
            "thin-shortlist penalty: "
            + str(promote_but_thin)
            + " candidate(s) carry a PROMOTE_TO_REVIEW verdict but have fewer "
            "than "
            + str(min_cohorts)
            + " independent positive cohort(s) and are held back."
        )
    if hold_count > 0:
        penalty_findings.append(
            "hold penalty: "
            + str(hold_count)
            + " candidate(s) need more independent booked evidence before "
            "review."
        )
    if watch_count > 0:
        penalty_findings.append(
            "watch penalty: "
            + str(watch_count)
            + " candidate(s) show no booked edge yet and stay observation-only."
        )
    if blocked_candidate_count > 0:
        penalty_findings.append(
            "candidate-block penalty: "
            + str(blocked_candidate_count)
            + " candidate(s) carry a BLOCK evidence verdict and cannot be "
            "ranked for review."
        )

    candidate_count = len(candidates)

    if block_reasons:
        outcome = OUTCOME_BLOCK
    elif candidate_count == 0:
        outcome = OUTCOME_NEEDS_MORE_CANDIDATES
    elif ranked_shortlist:
        outcome = OUTCOME_SHORTLIST_FOR_REVIEW
    else:
        outcome = OUTCOME_NO_SHORTLIST

    ranking_explanations = _ranking_explanations(
        outcome,
        candidate_count=candidate_count,
        shortlist_count=len(ranked_shortlist),
        hold_count=hold_count,
        watch_count=watch_count,
        blocked_candidate_count=blocked_candidate_count,
        min_cohorts=min_cohorts,
    )

    return {
        "outcome": outcome,
        "mode": STRATEGY_CANDIDATE_RANKING_MODE,
        "candidates_present": candidate_count > 0,
        "candidate_count": candidate_count,
        "shortlist_count": len(ranked_shortlist),
        "hold_count": hold_count,
        "watch_count": watch_count,
        "blocked_candidate_count": blocked_candidate_count,
        "min_independent_cohorts_for_shortlist": min_cohorts,
        "ranked_shortlist": ranked_shortlist,
        "ranked_shortlist_ids": ranked_shortlist_ids,
        "tiered_candidates": tiered,
        "tier_summaries": tier_summaries,
        "block_reasons": block_reasons,
        "penalty_findings": penalty_findings,
        "ranking_explanations": ranking_explanations,
        "promotes_beyond_review": False,
        "ranks_research_only": True,
        "authorizes_nothing": True,
    }


def _ranking_summary_section(ranking: dict[str, Any]) -> list[str]:
    return [
        "Ranking verdict: " + ranking["outcome"] + ".",
        "Mode: " + ranking["mode"] + " (research review sort only).",
        "Candidates ranked: "
        + str(ranking["candidate_count"])
        + " ("
        + str(ranking["shortlist_count"])
        + " shortlist, "
        + str(ranking["hold_count"])
        + " hold, "
        + str(ranking["watch_count"])
        + " watch, "
        + str(ranking["blocked_candidate_count"])
        + " blocked).",
        "Ordered review shortlist: "
        + (
            ", ".join(ranking["ranked_shortlist_ids"])
            if ranking["ranked_shortlist_ids"]
            else "(none)"
        )
        + ".",
        "Being ranked first means only that a human may review that candidate "
        "first; top rank is not selection and authorizes nothing.",
    ]


def _ranking_findings_section(ranking: dict[str, Any]) -> list[str]:
    outcome = ranking["outcome"]
    if outcome == OUTCOME_BLOCK:
        lines = ["Payload scored BLOCK; it is unsafe and is refused:"]
        lines.extend("- " + reason for reason in ranking["block_reasons"])
        lines.append(
            "BLOCK authorizes nothing and unlocks no gate; the unsafe payload "
            "must be rebuilt as static research-only candidates."
        )
        return lines
    lines = list(ranking["ranking_explanations"])
    if ranking["penalty_findings"]:
        lines.append("Penalties applied:")
        lines.extend("- " + finding for finding in ranking["penalty_findings"])
    return lines


def _observation_only_section() -> list[str]:
    lines = [
        lane + " remains observation-only (attention only)."
        for lane in STRATEGY_CANDIDATE_RANKING_OBSERVATION_ONLY_EVIDENCE_LANES
    ]
    lines.append(
        "No evidence lane is ever wired to a data fetch, an API call, a "
        "dataset, a QA run, a backtest, a paper/live trade, a broker or "
        "exchange, or any automation."
    )
    return lines


_NO_EXECUTION_AUTHORIZATION_SECTION: tuple[str, ...] = (
    "This ranking authorizes no trade and no position of any kind.",
    "It permits no data fetch, no API call, no dataset inspection, no QA, no "
    "baseline, and no backtest.",
    "It permits no paper trading, no live trading, no broker or exchange "
    "connection, and no automation.",
    "It writes no runtime, registry, ledger, or dashboard state.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
    "The most a verdict can do is SHORTLIST_FOR_REVIEW, which only invites a "
    "human research review and never produces an execution instruction.",
)

_OPERATOR_NEXT_STEP = (
    "Research-only: a human reviewer must read this ranking verdict, "
    "independently confirm every tier and penalty, and treat a "
    "SHORTLIST_FOR_REVIEW outcome as an invitation to review the shortlisted "
    "candidates on paper only. The single permitted next step is to register or "
    "assemble the next research-only contract. No execution of any kind is "
    "authorized."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 strategy candidate ranking contract template and is "
    "execution-free.",
    "It inspects an already-scored static set of candidates and reports one "
    "research-only verdict plus per-candidate review tiers; it runs nothing, "
    "fetches nothing, and connects nowhere.",
    "Core rule: a candidate's rank follows its evidence verdict, then its "
    "independent positive booked cohorts, then a deterministic id tie-break; the "
    "verdict sorts candidates for a human, never promotes a candidate beyond a "
    "research review.",
    "Outcome precedence is BLOCK > NEEDS_MORE_CANDIDATES > NO_SHORTLIST > "
    "SHORTLIST_FOR_REVIEW; an unsafe payload always scores BLOCK.",
    "Only a PROMOTE_TO_REVIEW evidence verdict with enough independent positive "
    "cohorts is shortlist-eligible; HOLD and WATCH candidates stay in research.",
    "A SHORTLIST_FOR_REVIEW verdict never unlocks real-data QA, baseline, "
    "backtest, paper, live, broker/exchange, or automation, and top rank is "
    "never selection.",
    "Every finding is attention-only and needs independent confirmation; the "
    "ranking never converts a rank into permission.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human reviewer must read the structured ranking verdict before any "
    "further research-only contract is built.",
    "A human reviewer must confirm a SHORTLIST_FOR_REVIEW outcome is treated "
    "only as an invitation to review the shortlisted candidates and is never "
    "wired to a data fetch, an API call, a dataset, a QA run, a backtest, a "
    "paper/live trade, a broker or exchange, an order, or any automation.",
    "A human reviewer must independently confirm every tier and penalty before "
    "it is trusted, and must treat top rank as review order, never selection.",
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
    "ranking_next_required_action",
    "ranking_current_stage",
    "observation_only_evidence_lanes",
    "outcomes",
    "tiers",
    "min_independent_cohorts_for_shortlist",
    "evidence_outcomes",
    "shortlist_eligible_evidence_outcomes",
    "authorization_flags",
    "gate_lock_flags",
    "gate_unlock_request_flags",
    "forbidden_promotion_request_flags",
    "executable_signal_fields",
    "forbidden_trade_terms",
    "candidates",
    "ranking",
    "outcome",
    "candidate_count",
    "shortlist_count",
    "hold_count",
    "watch_count",
    "blocked_candidate_count",
    "ranked_shortlist_ids",
    "tier_summaries",
    "block_reasons",
    "penalty_findings",
    "ranking_explanations",
    "ranking_summary_section",
    "ranking_findings_section",
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
    "promotes_beyond_review",
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def _safety_posture() -> dict[str, bool]:
    """Return a fresh copy of the posture (callers cannot taint the global)."""
    return dict(STRATEGY_CANDIDATE_RANKING_SAFETY_POSTURE)


def build_crypto_d1_strategy_candidate_ranking_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build the read-only strategy candidate ranking contract. Pure; no I/O, no
    data fetch, no mutation of inputs, no clock read, no random id. When no
    payload is given, the static DEFAULT_SAMPLE_CANDIDATES is ranked. A fresh
    dict (with fresh lists/dicts) is returned every call. The contract never
    promotes a candidate beyond a research review and it authorizes nothing."""
    if payload is None:
        source = _isolated(DEFAULT_SAMPLE_CANDIDATES)
    elif isinstance(payload, (dict, list, tuple)):
        source = _isolated(payload)
    else:
        source = payload

    ranking = rank_strategy_candidates(source)

    contract: dict[str, Any] = {
        "schema_version": STRATEGY_CANDIDATE_RANKING_SCHEMA_VERSION,
        "label": STRATEGY_CANDIDATE_RANKING_LABEL,
        "status": STRATEGY_CANDIDATE_RANKING_STATUS,
        "stage": "CRYPTO_D1_STRATEGY_CANDIDATE_RANKING_CONTRACT_ONLY",
        "mode": STRATEGY_CANDIDATE_RANKING_MODE,
        "core_rule": STRATEGY_CANDIDATE_RANKING_CORE_RULE,
        "ranking_next_required_action": (
            STRATEGY_CANDIDATE_RANKING_NEXT_REQUIRED_ACTION
        ),
        "ranking_current_stage": STRATEGY_CANDIDATE_RANKING_CURRENT_STAGE,
        "observation_only_evidence_lanes": (
            STRATEGY_CANDIDATE_RANKING_OBSERVATION_ONLY_EVIDENCE_LANES
        ),
        "outcomes": STRATEGY_CANDIDATE_RANKING_OUTCOMES,
        "tiers": STRATEGY_CANDIDATE_RANKING_TIERS,
        "min_independent_cohorts_for_shortlist": (
            STRATEGY_CANDIDATE_RANKING_MIN_INDEPENDENT_COHORTS_FOR_SHORTLIST
        ),
        "evidence_outcomes": STRATEGY_CANDIDATE_RANKING_EVIDENCE_OUTCOMES,
        "shortlist_eligible_evidence_outcomes": (
            STRATEGY_CANDIDATE_RANKING_SHORTLIST_ELIGIBLE_EVIDENCE_OUTCOMES
        ),
        "authorization_flags": (
            STRATEGY_CANDIDATE_RANKING_AUTHORIZATION_FLAGS
        ),
        "gate_lock_flags": STRATEGY_CANDIDATE_RANKING_GATE_LOCK_FLAGS,
        "gate_unlock_request_flags": (
            STRATEGY_CANDIDATE_RANKING_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_promotion_request_flags": (
            STRATEGY_CANDIDATE_RANKING_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ),
        "executable_signal_fields": (
            STRATEGY_CANDIDATE_RANKING_EXECUTABLE_SIGNAL_FIELDS
        ),
        "forbidden_trade_terms": (
            STRATEGY_CANDIDATE_RANKING_FORBIDDEN_TRADE_TERMS
        ),
        "candidates": _isolated(source)
        if isinstance(source, (dict, list))
        else {},
        "ranking": ranking,
        "outcome": ranking["outcome"],
        "candidate_count": ranking["candidate_count"],
        "shortlist_count": ranking["shortlist_count"],
        "hold_count": ranking["hold_count"],
        "watch_count": ranking["watch_count"],
        "blocked_candidate_count": ranking["blocked_candidate_count"],
        "ranked_shortlist_ids": list(ranking["ranked_shortlist_ids"]),
        "tier_summaries": list(ranking["tier_summaries"]),
        "block_reasons": list(ranking["block_reasons"]),
        "penalty_findings": list(ranking["penalty_findings"]),
        "ranking_explanations": list(ranking["ranking_explanations"]),
        "ranking_summary_section": _ranking_summary_section(ranking),
        "ranking_findings_section": _ranking_findings_section(ranking),
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
        "promotes_beyond_review": False,
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
    "promotes_beyond_review",
)

# The generated-guidance fields whose text is the ranking's own actionable
# output. These must never contain an execution verb. (The raw echoed
# ``candidates``, ``tier_summaries``, ``penalty_findings`` and ``block_reasons``
# embed caller-supplied family / universe names and are excluded from this
# check.)
_ACTIONABLE_TEXT_FIELDS: tuple[str, ...] = (
    "outcome",
    "operator_next_step",
    "ranking_summary_section",
    "ranking_findings_section",
    "observation_only_section",
    "no_execution_authorization_section",
    "ranking_explanations",
)


def _contains_forbidden_term(text: str) -> bool:
    tokens = _word_tokens(text)
    return any(
        term in tokens
        for term in STRATEGY_CANDIDATE_RANKING_FORBIDDEN_TRADE_TERMS
    )


def _no_forbidden_trade_terms(contract: dict[str, Any]) -> bool:
    """True when none of the ranking's actionable guidance fields contain an
    execution verb as a whole word. Pure; reads only the contract dict.

    A BLOCK findings section can legitimately quote an offending input field
    name while explaining the refusal, so that section is skipped when the
    verdict is BLOCK."""
    blocked = contract.get("outcome") == OUTCOME_BLOCK
    for field in _ACTIONABLE_TEXT_FIELDS:
        if field == "ranking_findings_section" and blocked:
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
        safe.get("schema_version")
        == STRATEGY_CANDIDATE_RANKING_SCHEMA_VERSION
    )
    label_ok = safe.get("label") == STRATEGY_CANDIDATE_RANKING_LABEL
    read_only = safe.get("read_only") is True
    research_only = (
        safe.get("research_only") is True
        and safe.get("mode") == "RESEARCH_ONLY"
    )
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_STRATEGY_CANDIDATE_RANKING_CONTRACT_ONLY"
    )
    core_rule_ok = (
        safe.get("core_rule") == STRATEGY_CANDIDATE_RANKING_CORE_RULE
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
        and posture == STRATEGY_CANDIDATE_RANKING_SAFETY_POSTURE
    )

    outcome_ok = safe.get("outcome") in _OUTCOME_SET
    lanes_ok = (
        tuple(safe.get("observation_only_evidence_lanes") or ())
        == STRATEGY_CANDIDATE_RANKING_OBSERVATION_ONLY_EVIDENCE_LANES
    )
    outcomes_ok = (
        tuple(safe.get("outcomes") or ())
        == STRATEGY_CANDIDATE_RANKING_OUTCOMES
    )
    tiers_ok = (
        tuple(safe.get("tiers") or ()) == STRATEGY_CANDIDATE_RANKING_TIERS
    )

    ranking = safe.get("ranking")
    ranking_ok = (
        isinstance(ranking, dict)
        and ranking.get("authorizes_nothing") is True
        and ranking.get("ranks_research_only") is True
        and ranking.get("promotes_beyond_review") is False
        and ranking.get("outcome") in _OUTCOME_SET
    )

    no_trade_language = _no_forbidden_trade_terms(safe)

    sections_ok = all(
        len(tuple(safe.get(section) or ())) >= 1
        for section in (
            "ranking_summary_section",
            "ranking_findings_section",
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
        and lanes_ok
        and outcomes_ok
        and tiers_ok
        and ranking_ok
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
        "lanes_ok": lanes_ok,
        "outcomes_ok": outcomes_ok,
        "tiers_ok": tiers_ok,
        "ranking_ok": ranking_ok,
        "no_trade_language": no_trade_language,
        "sections_ok": sections_ok,
        "operator_next_step_ok": operator_next_step_ok,
    }


def validate_crypto_d1_strategy_candidate_ranking_contract(
    contract: Any,
) -> dict[str, Any]:
    """Public validation entry point; returns the deterministic verdict dict."""
    return _validate(contract)


def render_crypto_d1_strategy_candidate_ranking_contract_markdown(
    contract: Any,
) -> str:
    """Render an informational, read-only markdown summary of the contract.
    Pure; builds and returns a string, writes nothing."""
    safe = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Strategy Candidate Ranking Contract")
    lines.append("")
    lines.append("- Label: " + _as_text(safe.get("label")))
    lines.append("- Mode: " + _as_text(safe.get("mode")))
    lines.append("- Status: " + _as_text(safe.get("status")))
    lines.append("- Outcome: " + _as_text(safe.get("outcome")))
    lines.append("- Candidates ranked: " + str(safe.get("candidate_count")))
    lines.append("- Shortlist: " + str(safe.get("shortlist_count")))
    lines.append("- Hold: " + str(safe.get("hold_count")))
    lines.append("- Watch: " + str(safe.get("watch_count")))
    lines.append(
        "- Blocked candidates: " + str(safe.get("blocked_candidate_count"))
    )
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

    _emit("Ranking Summary", "ranking_summary_section")
    _emit("Ranking Findings", "ranking_findings_section")
    _emit("Tiers", "tier_summaries")
    _emit("Penalties", "penalty_findings")
    _emit("Observation-Only Evidence Lanes", "observation_only_section")
    _emit("No Execution Authorization", "no_execution_authorization_section")
    lines.append("")
    lines.append("## Operator Next Step")
    lines.append("- " + _as_text(safe.get("operator_next_step")))
    return "\n".join(lines)

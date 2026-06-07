"""SPARTA Offline Strategy Factory - CRYPTO-D1 STRATEGY EVIDENCE SCORING.

A PURE, stdlib-only *read-only paper contract* that *scores* a small,
caller-provided set of static trading-evidence and external-evidence records and
sorts the whole set into exactly one research-only verdict. It returns a
deterministic, structured scoring result: the verdict, the per-cohort summaries,
the penalties applied, and a plain-language explanation -- so a human can decide,
on paper, whether a strategy candidate's evidence is worth a research review.

CORE RULE: the scoring weighs booked (closed/realized) evidence over open
(unrealized) PnL, weighs independent cohorts over correlated clusters, and can
ONLY sort the evidence into PROMOTE_TO_REVIEW / KEEP_WATCH / NEEDS_MORE_DATA /
BLOCK for human research review. A PROMOTE_TO_REVIEW verdict means ONLY that a
human may *review* the evidence; it authorizes nothing and unlocks no gate.

Scoring principles (all applied deterministically, on paper):
  - Closed / booked trades carry weight; open / unrealized PnL is
    observation-only and contributes zero proof weight (it is not proof).
  - Correlated trades are grouped into cohorts: trades that share a macro event,
    or share the same symbol and the same direction, count as ONE independent
    event, not many independent wins.
  - Same-symbol duplicates and same-direction pileups are penalized (reported).
  - A tiny independent sample is penalized: PROMOTE_TO_REVIEW requires several
    INDEPENDENT positive booked cohorts, not one cohort repeated.
  - Evidence from external bots, whale tracking, funding rates, BTC cycle timing,
    and the daily alpha brief stays research-only and never counts as proof.

This contract authorizes NOTHING real. It does NOT fetch any data, call any API,
inspect any dataset, acquire any real data, load any file, open any network, run
any QA, baseline, backtest, or simulation, produce any trade signal, reach any
broker / exchange / order / account / API surface, trade any paper and any live,
promote any strategy beyond a research review, unlock any downstream gate
(real_data_qa, baseline_backtest, paper_trading_gate, micro_live_gate stay
blocked / locked), trigger any automation, write any runtime / registry /
ledger / dashboard / report state, spawn any child process, read any
environment, record any wall-clock time, mint any random id, or dynamically
import anything. It ONLY inspects the static records the caller passes in, using
pure dict / string / number arithmetic.

Scoring outcomes (precedence, highest first / most restrictive first):
    BLOCK > NEEDS_MORE_DATA > KEEP_WATCH > PROMOTE_TO_REVIEW
  - BLOCK            -> the payload is unsafe: an authorization flag is set, a
                        gate-unlock or forbidden-promotion request is present, or
                        a record carries an executable order/signal field.
  - NEEDS_MORE_DATA  -> there is some positive BOOKED evidence, but too few
                        INDEPENDENT positive cohorts (correlated cluster, or a
                        single small sample). Promising, not yet reviewable.
  - KEEP_WATCH       -> only open / unrealized or external-research evidence
                        (observation only, not booked proof), or booked evidence
                        with no positive edge. Weak; keep observing.
  - PROMOTE_TO_REVIEW-> several INDEPENDENT positive booked cohorts; a human may
                        REVIEW the evidence. This unlocks nothing.

Public API:
  - STRATEGY_EVIDENCE_SCORING_SCHEMA_VERSION
  - STRATEGY_EVIDENCE_SCORING_LABEL
  - STRATEGY_EVIDENCE_SCORING_STATUS
  - STRATEGY_EVIDENCE_SCORING_MODE
  - STRATEGY_EVIDENCE_SCORING_CORE_RULE
  - STRATEGY_EVIDENCE_SCORING_SAFETY_POSTURE
  - STRATEGY_EVIDENCE_SCORING_OBSERVATION_ONLY_EVIDENCE_LANES
  - STRATEGY_EVIDENCE_SCORING_OUTCOMES
  - OUTCOME_BLOCK / OUTCOME_NEEDS_MORE_DATA / OUTCOME_KEEP_WATCH /
    OUTCOME_PROMOTE_TO_REVIEW
  - STRATEGY_EVIDENCE_SCORING_MIN_INDEPENDENT_COHORTS_FOR_PROMOTE
  - STRATEGY_EVIDENCE_SCORING_TRADE_SOURCE_TAGS
  - STRATEGY_EVIDENCE_SCORING_EXTERNAL_RESEARCH_SOURCE_TAGS
  - STRATEGY_EVIDENCE_SCORING_BOOKED_STATUS_TAGS
  - STRATEGY_EVIDENCE_SCORING_OPEN_STATUS_TAGS
  - STRATEGY_EVIDENCE_SCORING_AUTHORIZATION_FLAGS
  - STRATEGY_EVIDENCE_SCORING_GATE_LOCK_FLAGS
  - STRATEGY_EVIDENCE_SCORING_GATE_UNLOCK_REQUEST_FLAGS
  - STRATEGY_EVIDENCE_SCORING_FORBIDDEN_PROMOTION_REQUEST_FLAGS
  - STRATEGY_EVIDENCE_SCORING_EXECUTABLE_SIGNAL_FIELDS
  - STRATEGY_EVIDENCE_SCORING_FORBIDDEN_TRADE_TERMS
  - STRATEGY_EVIDENCE_SCORING_NEXT_REQUIRED_ACTION
  - STRATEGY_EVIDENCE_SCORING_CURRENT_STAGE
  - DEFAULT_SAMPLE_EVIDENCE
  - score_strategy_evidence(payload)
  - build_crypto_d1_strategy_evidence_scoring_contract(payload=None)
  - validate_crypto_d1_strategy_evidence_scoring_contract(contract)
  - render_crypto_d1_strategy_evidence_scoring_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "STRATEGY_EVIDENCE_SCORING_SCHEMA_VERSION",
    "STRATEGY_EVIDENCE_SCORING_LABEL",
    "STRATEGY_EVIDENCE_SCORING_STATUS",
    "STRATEGY_EVIDENCE_SCORING_MODE",
    "STRATEGY_EVIDENCE_SCORING_CORE_RULE",
    "STRATEGY_EVIDENCE_SCORING_SAFETY_POSTURE",
    "STRATEGY_EVIDENCE_SCORING_OBSERVATION_ONLY_EVIDENCE_LANES",
    "STRATEGY_EVIDENCE_SCORING_OUTCOMES",
    "OUTCOME_BLOCK",
    "OUTCOME_NEEDS_MORE_DATA",
    "OUTCOME_KEEP_WATCH",
    "OUTCOME_PROMOTE_TO_REVIEW",
    "STRATEGY_EVIDENCE_SCORING_MIN_INDEPENDENT_COHORTS_FOR_PROMOTE",
    "STRATEGY_EVIDENCE_SCORING_TRADE_SOURCE_TAGS",
    "STRATEGY_EVIDENCE_SCORING_EXTERNAL_RESEARCH_SOURCE_TAGS",
    "STRATEGY_EVIDENCE_SCORING_BOOKED_STATUS_TAGS",
    "STRATEGY_EVIDENCE_SCORING_OPEN_STATUS_TAGS",
    "STRATEGY_EVIDENCE_SCORING_AUTHORIZATION_FLAGS",
    "STRATEGY_EVIDENCE_SCORING_GATE_LOCK_FLAGS",
    "STRATEGY_EVIDENCE_SCORING_GATE_UNLOCK_REQUEST_FLAGS",
    "STRATEGY_EVIDENCE_SCORING_FORBIDDEN_PROMOTION_REQUEST_FLAGS",
    "STRATEGY_EVIDENCE_SCORING_EXECUTABLE_SIGNAL_FIELDS",
    "STRATEGY_EVIDENCE_SCORING_FORBIDDEN_TRADE_TERMS",
    "STRATEGY_EVIDENCE_SCORING_NEXT_REQUIRED_ACTION",
    "STRATEGY_EVIDENCE_SCORING_CURRENT_STAGE",
    "DEFAULT_SAMPLE_EVIDENCE",
    "score_strategy_evidence",
    "build_crypto_d1_strategy_evidence_scoring_contract",
    "validate_crypto_d1_strategy_evidence_scoring_contract",
    "render_crypto_d1_strategy_evidence_scoring_contract_markdown",
]

STRATEGY_EVIDENCE_SCORING_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_strategy_evidence_scoring_contract.v1"
)
STRATEGY_EVIDENCE_SCORING_LABEL = (
    "Block 131 - Crypto-D1 Strategy Evidence Scoring Contract"
)
STRATEGY_EVIDENCE_SCORING_STATUS = (
    "READ_ONLY_CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT"
)
STRATEGY_EVIDENCE_SCORING_MODE = "RESEARCH_ONLY"

STRATEGY_EVIDENCE_SCORING_CORE_RULE = (
    "The scoring weighs booked evidence over open PnL and independent cohorts "
    "over correlated clusters; it can only sort evidence into PROMOTE_TO_REVIEW "
    "/ KEEP_WATCH / NEEDS_MORE_DATA / BLOCK for human research review, and it "
    "authorizes nothing."
)

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering
# this contract is the separate, later block; importing the registry would also
# risk a circular import).
STRATEGY_EVIDENCE_SCORING_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT"
)
STRATEGY_EVIDENCE_SCORING_CURRENT_STAGE = (
    "CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT_REQUIRED"
)

# A PROMOTE_TO_REVIEW verdict requires at least this many INDEPENDENT positive
# booked cohorts. One cohort repeated (a correlated cluster) is not enough.
STRATEGY_EVIDENCE_SCORING_MIN_INDEPENDENT_COHORTS_FOR_PROMOTE = 3

# Evidence lanes that remain observation-only at every scoring outcome. The
# scoring reads about them; it never wires any of them to a fetch, a QA run, a
# backtest, a trade, a broker/exchange, an order, or any automation.
STRATEGY_EVIDENCE_SCORING_OBSERVATION_ONLY_EVIDENCE_LANES: tuple[str, ...] = (
    "external_bot_evidence",
    "hyperliquid_whale_evidence",
    "funding_rate_evidence",
    "bitcoin_cycle_timing_evidence",
    "daily_alpha_brief",
    "open_unrealized_pnl",
)

# Scoring outcomes, in precedence order (highest / most restrictive first).
OUTCOME_BLOCK = "BLOCK"
OUTCOME_NEEDS_MORE_DATA = "NEEDS_MORE_DATA"
OUTCOME_KEEP_WATCH = "KEEP_WATCH"
OUTCOME_PROMOTE_TO_REVIEW = "PROMOTE_TO_REVIEW"

STRATEGY_EVIDENCE_SCORING_OUTCOMES: tuple[str, ...] = (
    OUTCOME_BLOCK,
    OUTCOME_NEEDS_MORE_DATA,
    OUTCOME_KEEP_WATCH,
    OUTCOME_PROMOTE_TO_REVIEW,
)
_OUTCOME_SET: frozenset[str] = frozenset(STRATEGY_EVIDENCE_SCORING_OUTCOMES)
# Lower index == higher precedence / more restrictive.
_OUTCOME_PRECEDENCE: dict[str, int] = {
    OUTCOME_BLOCK: 0,
    OUTCOME_NEEDS_MORE_DATA: 1,
    OUTCOME_KEEP_WATCH: 2,
    OUTCOME_PROMOTE_TO_REVIEW: 3,
}

# Source tags treated as first-party trade evidence (booked or open). An empty /
# missing source defaults to trade evidence.
STRATEGY_EVIDENCE_SCORING_TRADE_SOURCE_TAGS: tuple[str, ...] = (
    "trade",
    "booked_trade",
    "closed_trade",
    "open_trade",
    "position",
)

# Source tags treated as external research context. These NEVER count as proof.
STRATEGY_EVIDENCE_SCORING_EXTERNAL_RESEARCH_SOURCE_TAGS: tuple[str, ...] = (
    "external_bot",
    "hyperliquid_whale",
    "funding_rate",
    "bitcoin_cycle_timing",
    "daily_alpha_brief",
)

# Record statuses treated as BOOKED (closed / realized) -> carry proof weight.
STRATEGY_EVIDENCE_SCORING_BOOKED_STATUS_TAGS: tuple[str, ...] = (
    "closed",
    "booked",
    "realized",
    "settled",
)

# Record statuses treated as OPEN (unrealized) -> observation only, zero proof.
STRATEGY_EVIDENCE_SCORING_OPEN_STATUS_TAGS: tuple[str, ...] = (
    "open",
    "unrealized",
    "live",
    "running",
    "floating",
)

_TRADE_SOURCE_SET: frozenset[str] = frozenset(
    STRATEGY_EVIDENCE_SCORING_TRADE_SOURCE_TAGS
)
_EXTERNAL_SOURCE_SET: frozenset[str] = frozenset(
    STRATEGY_EVIDENCE_SCORING_EXTERNAL_RESEARCH_SOURCE_TAGS
)
_BOOKED_STATUS_SET: frozenset[str] = frozenset(
    STRATEGY_EVIDENCE_SCORING_BOOKED_STATUS_TAGS
)
_OPEN_STATUS_SET: frozenset[str] = frozenset(
    STRATEGY_EVIDENCE_SCORING_OPEN_STATUS_TAGS
)

# Top-level (or per-record) authorization flags that, if truthy, force BLOCK.
STRATEGY_EVIDENCE_SCORING_AUTHORIZATION_FLAGS: tuple[str, ...] = (
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
STRATEGY_EVIDENCE_SCORING_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, force BLOCK.
STRATEGY_EVIDENCE_SCORING_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
)

# Requests asking the scoring to mean execution / live promotion. Any truthy
# value forces BLOCK: a verdict can only ever mean a research-review sort.
STRATEGY_EVIDENCE_SCORING_FORBIDDEN_PROMOTION_REQUEST_FLAGS: tuple[str, ...] = (
    "force_promote",
    "promote_to_live",
    "promote_to_paper",
    "approve_trade",
    "authorize_trade",
    "execute",
    "place_order",
    "go_live",
)

# Fields whose presence (non-empty) on a record signals an executable order /
# signal instruction rather than historical evidence -> BLOCK.
STRATEGY_EVIDENCE_SCORING_EXECUTABLE_SIGNAL_FIELDS: tuple[str, ...] = (
    "order",
    "signal",
    "trade_instruction",
    "execution",
    "live_order",
    "place_order",
)

# Execution / promotion verbs the scoring's own generated guidance must never
# contain as whole words.
STRATEGY_EVIDENCE_SCORING_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
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
STRATEGY_EVIDENCE_SCORING_SAFETY_POSTURE: dict[str, bool] = {
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


# A deterministic, illustrative paper sample: three booked ETH records that all
# share one macro move and the same direction. They are PROMISING but
# CORRELATED -- one independent event, not three independent wins -> the default
# build scores NEEDS_MORE_DATA. Nothing here is real data; static example only.
DEFAULT_SAMPLE_EVIDENCE: dict[str, Any] = {
    "label": "Crypto-D1 strategy candidate evidence (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "research_only": True,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
    "evidence": [
        {
            "id": "E",
            "symbol": "ETH",
            "direction": "short",
            "status": "closed",
            "pnl": 1.4,
            "macro_event": "eth_dump_2026_05",
            "source": "trade",
        },
        {
            "id": "E2",
            "symbol": "ETH",
            "direction": "short",
            "status": "closed",
            "pnl": 0.9,
            "macro_event": "eth_dump_2026_05",
            "source": "trade",
        },
        {
            "id": "F2",
            "symbol": "ETH",
            "direction": "short",
            "status": "closed",
            "pnl": 1.1,
            "macro_event": "eth_dump_2026_05",
            "source": "trade",
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


def _as_number(value: Any) -> float:
    """Coerce a caller PnL value to a float; non-numeric -> 0.0. Bools are 0.0."""
    if isinstance(value, bool):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return 0.0
    return 0.0


def _record_id(record: dict[str, Any], index: int) -> str:
    rid = _as_text(record.get("id"))
    return rid if rid else "#" + str(index)


def _record_source(record: dict[str, Any]) -> str:
    """The normalized source tag; empty / unknown source defaults to trade."""
    src = _as_text(record.get("source")).lower()
    if src in _EXTERNAL_SOURCE_SET:
        return src
    return src if src in _TRADE_SOURCE_SET else "trade"


def _record_status(record: dict[str, Any]) -> str:
    return _as_text(record.get("status")).lower()


def _cohort_key(record: dict[str, Any]) -> str:
    """Correlated trades share a cohort key. A shared macro event collapses many
    trades (one macro move counted many times) into one event; absent that, the
    same symbol and same direction collapse into one event."""
    macro = _as_text(record.get("macro_event")).lower()
    if macro:
        return "macro:" + macro
    sym = _as_text(record.get("symbol")).lower()
    direction = _as_text(record.get("direction")).lower()
    return "sd:" + sym + "|" + direction


def _safety_block_findings(
    controls: dict[str, Any], records: list[dict[str, Any]]
) -> list[str]:
    """Reasons the whole payload is unsafe and must score BLOCK. Pure."""
    reasons: list[str] = []
    for flag in STRATEGY_EVIDENCE_SCORING_AUTHORIZATION_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("authorization flag requested: " + flag)
    for flag in STRATEGY_EVIDENCE_SCORING_GATE_LOCK_FLAGS:
        if flag in controls and controls.get(flag) is not True:
            reasons.append("gate unlock attempt: " + flag + " is not locked")
    for flag in STRATEGY_EVIDENCE_SCORING_GATE_UNLOCK_REQUEST_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("gate unlock request: " + flag)
    for flag in STRATEGY_EVIDENCE_SCORING_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("forbidden promotion/execution request: " + flag)
    for index, record in enumerate(records):
        rid = _record_id(record, index)
        for field in STRATEGY_EVIDENCE_SCORING_EXECUTABLE_SIGNAL_FIELDS:
            if field in record and _non_empty(record.get(field)):
                reasons.append(
                    "record " + rid + " carries executable field: " + field
                )
        for flag in STRATEGY_EVIDENCE_SCORING_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
            if _truthy(record.get(flag)):
                reasons.append(
                    "record "
                    + rid
                    + " requests forbidden promotion/execution: "
                    + flag
                )
        for flag in STRATEGY_EVIDENCE_SCORING_AUTHORIZATION_FLAGS:
            if _truthy(record.get(flag)):
                reasons.append(
                    "record " + rid + " requests authorization: " + flag
                )
    return reasons


def _score_explanations(
    outcome: str,
    record_count: int,
    booked_count: int,
    open_count: int,
    external_count: int,
    independent_positive: int,
    independent_cohorts: int,
    min_promote: int,
) -> list[str]:
    """Plain-language rationale for the verdict. References counts only (never a
    raw symbol or trade direction), so the guidance never emits an execution
    verb."""
    lines = [
        "Scored "
        + str(record_count)
        + " record(s): "
        + str(booked_count)
        + " booked, "
        + str(open_count)
        + " open/unrealized, "
        + str(external_count)
        + " external-research.",
        "Independent positive booked cohorts: "
        + str(independent_positive)
        + " (of "
        + str(independent_cohorts)
        + " cohort(s)); "
        + str(min_promote)
        + " independent positive cohorts are required to be reviewable.",
    ]
    if outcome == OUTCOME_BLOCK:
        lines.append(
            "Verdict BLOCK: the payload requested an authorization, a gate "
            "unlock, a forbidden promotion, or carried an executable field; the "
            "scoring refuses it and authorizes nothing."
        )
    elif outcome == OUTCOME_NEEDS_MORE_DATA and record_count == 0:
        lines.append(
            "Verdict NEEDS_MORE_DATA: there is nothing to score yet; supply "
            "static booked evidence records for a future research review."
        )
    elif outcome == OUTCOME_NEEDS_MORE_DATA:
        lines.append(
            "Verdict NEEDS_MORE_DATA: the booked evidence is promising but the "
            "independent positive sample is too small (a correlated cluster or a "
            "single cohort); more INDEPENDENT booked evidence is needed."
        )
    elif outcome == OUTCOME_KEEP_WATCH and booked_count == 0:
        lines.append(
            "Verdict KEEP_WATCH: only open/unrealized or external-research "
            "evidence is present; that is observation-only and is not booked "
            "proof. Keep observing."
        )
    elif outcome == OUTCOME_KEEP_WATCH:
        lines.append(
            "Verdict KEEP_WATCH: the booked evidence shows no positive edge "
            "(flat or negative); the candidate is weak. Keep observing."
        )
    else:
        lines.append(
            "Verdict PROMOTE_TO_REVIEW: several INDEPENDENT positive booked "
            "cohorts are present, so a human may REVIEW the evidence. This "
            "unlocks no QA, no baseline, no backtest, no paper, no live, no "
            "broker/exchange, and no automation."
        )
    return lines


def score_strategy_evidence(payload: Any) -> dict[str, Any]:
    """Return a deterministic, research-only score for a static evidence payload.

    Pure; no I/O, no data fetch, no clock read, no mutation, no random id.
    Malformed / missing inputs never raise. ``payload`` may be a list of evidence
    records, or a dict carrying an ``evidence`` list plus optional control flags.
    The verdict is one of BLOCK / NEEDS_MORE_DATA / KEEP_WATCH /
    PROMOTE_TO_REVIEW; PROMOTE_TO_REVIEW only authorizes a human research review
    and unlocks nothing."""
    if isinstance(payload, dict):
        controls = payload
        raw_evidence = payload.get("evidence")
    elif isinstance(payload, (list, tuple)):
        controls = {}
        raw_evidence = payload
    else:
        controls = {}
        raw_evidence = None

    if isinstance(raw_evidence, (list, tuple)):
        records = [r for r in raw_evidence if isinstance(r, dict)]
    else:
        records = []

    block_reasons = _safety_block_findings(controls, records)

    trade_records: list[dict[str, Any]] = []
    external_records: list[dict[str, Any]] = []
    for record in records:
        if _record_source(record) in _EXTERNAL_SOURCE_SET:
            external_records.append(record)
        else:
            trade_records.append(record)

    booked: list[dict[str, Any]] = []
    open_records: list[dict[str, Any]] = []
    for record in trade_records:
        if _record_status(record) in _BOOKED_STATUS_SET:
            booked.append(record)
        else:
            open_records.append(record)

    cohorts: dict[str, list[dict[str, Any]]] = {}
    for record in booked:
        cohorts.setdefault(_cohort_key(record), []).append(record)

    cohort_summaries: list[str] = []
    independent_positive = 0
    independent_negative = 0
    for key in sorted(cohorts):
        members = cohorts[key]
        net = sum(_as_number(m.get("pnl")) for m in members)
        if net > 0:
            independent_positive += 1
            sign = "positive"
        elif net < 0:
            independent_negative += 1
            sign = "negative"
        else:
            sign = "flat"
        correlated = (
            " (correlated; counts as 1 independent event)"
            if len(members) > 1
            else ""
        )
        cohort_summaries.append(
            "Cohort "
            + key
            + ": "
            + str(len(members))
            + " booked record(s)"
            + correlated
            + "; net booked PnL "
            + sign
            + "."
        )

    independent_cohorts = len(cohorts)
    correlated_record_count = sum(len(m) - 1 for m in cohorts.values())

    symbol_counts: dict[str, int] = {}
    direction_counts: dict[str, int] = {}
    for record in booked:
        sym = _as_text(record.get("symbol")).lower()
        if sym:
            symbol_counts[sym] = symbol_counts.get(sym, 0) + 1
        direction = _as_text(record.get("direction")).lower()
        if direction:
            direction_counts[direction] = direction_counts.get(direction, 0) + 1
    same_symbol_duplicate_count = sum(c - 1 for c in symbol_counts.values())
    same_direction_pileup_count = sum(c - 1 for c in direction_counts.values())

    booked_count = len(booked)
    open_count = len(open_records)
    record_count = len(records)
    min_promote = STRATEGY_EVIDENCE_SCORING_MIN_INDEPENDENT_COHORTS_FOR_PROMOTE
    small_sample = independent_positive < min_promote

    penalty_findings: list[str] = []
    if open_count > 0:
        penalty_findings.append(
            "open/unrealized PnL penalty: "
            + str(open_count)
            + " record(s) are observation-only and contribute 0 proof weight."
        )
    if correlated_record_count > 0:
        penalty_findings.append(
            "correlation penalty: "
            + str(correlated_record_count)
            + " booked record(s) are correlated within a cohort (not "
            "independent)."
        )
    if same_symbol_duplicate_count > 0:
        penalty_findings.append(
            "same-symbol duplicate penalty: "
            + str(same_symbol_duplicate_count)
            + " booked record(s) repeat a symbol already counted."
        )
    if same_direction_pileup_count > 0:
        penalty_findings.append(
            "same-direction pileup penalty: "
            + str(same_direction_pileup_count)
            + " booked record(s) pile onto a trade direction already counted."
        )
    if external_records:
        penalty_findings.append(
            "external-research penalty: "
            + str(len(external_records))
            + " record(s) are external research context and never count as "
            "proof."
        )
    if booked_count > 0 and small_sample:
        penalty_findings.append(
            "small-sample penalty: "
            + str(independent_positive)
            + " independent positive booked cohort(s) is below the "
            + str(min_promote)
            + " required to be reviewable."
        )

    if block_reasons:
        outcome = OUTCOME_BLOCK
    elif record_count == 0:
        outcome = OUTCOME_NEEDS_MORE_DATA
    elif booked_count == 0:
        outcome = OUTCOME_KEEP_WATCH
    elif independent_positive >= min_promote:
        outcome = OUTCOME_PROMOTE_TO_REVIEW
    elif independent_positive >= 1:
        outcome = OUTCOME_NEEDS_MORE_DATA
    else:
        outcome = OUTCOME_KEEP_WATCH

    score_explanations = _score_explanations(
        outcome,
        record_count=record_count,
        booked_count=booked_count,
        open_count=open_count,
        external_count=len(external_records),
        independent_positive=independent_positive,
        independent_cohorts=independent_cohorts,
        min_promote=min_promote,
    )

    return {
        "outcome": outcome,
        "mode": STRATEGY_EVIDENCE_SCORING_MODE,
        "evidence_present": record_count > 0,
        "record_count": record_count,
        "trade_record_count": len(trade_records),
        "external_record_count": len(external_records),
        "booked_count": booked_count,
        "open_count": open_count,
        "independent_cohorts": independent_cohorts,
        "independent_positive_cohorts": independent_positive,
        "independent_negative_cohorts": independent_negative,
        "correlated_record_count": correlated_record_count,
        "same_symbol_duplicate_count": same_symbol_duplicate_count,
        "same_direction_pileup_count": same_direction_pileup_count,
        "open_pnl_observation_only_count": open_count,
        "min_independent_cohorts_for_promote": min_promote,
        "small_sample": small_sample,
        "block_reasons": block_reasons,
        "penalty_findings": penalty_findings,
        "cohort_summaries": cohort_summaries,
        "score_explanations": score_explanations,
        "promotes_beyond_review": False,
        "scores_research_only": True,
        "authorizes_nothing": True,
    }


def _scoring_summary_section(score: dict[str, Any]) -> list[str]:
    return [
        "Scoring verdict: " + score["outcome"] + ".",
        "Mode: " + score["mode"] + " (research review sort only).",
        "Records scored: "
        + str(score["record_count"])
        + " ("
        + str(score["booked_count"])
        + " booked, "
        + str(score["open_count"])
        + " open/unrealized, "
        + str(score["external_record_count"])
        + " external-research).",
        "Independent positive booked cohorts: "
        + str(score["independent_positive_cohorts"])
        + " of "
        + str(score["independent_cohorts"])
        + " cohort(s).",
        "A PROMOTE_TO_REVIEW verdict means only that a human may review the "
        "evidence; it authorizes nothing.",
    ]


def _scoring_findings_section(score: dict[str, Any]) -> list[str]:
    outcome = score["outcome"]
    if outcome == OUTCOME_BLOCK:
        lines = ["Payload scored BLOCK; it is unsafe and is refused:"]
        lines.extend("- " + reason for reason in score["block_reasons"])
        lines.append(
            "BLOCK authorizes nothing and unlocks no gate; the unsafe payload "
            "must be rebuilt as static research-only evidence."
        )
        return lines
    lines = list(score["score_explanations"])
    if score["penalty_findings"]:
        lines.append("Penalties applied:")
        lines.extend("- " + finding for finding in score["penalty_findings"])
    return lines


def _observation_only_section() -> list[str]:
    lines = [
        lane + " remains observation-only (attention only)."
        for lane in STRATEGY_EVIDENCE_SCORING_OBSERVATION_ONLY_EVIDENCE_LANES
    ]
    lines.append(
        "No evidence lane is ever wired to a data fetch, an API call, a "
        "dataset, a QA run, a backtest, a paper/live trade, a broker or "
        "exchange, or any automation."
    )
    return lines


_NO_EXECUTION_AUTHORIZATION_SECTION: tuple[str, ...] = (
    "This scoring authorizes no trade and no position of any kind.",
    "It permits no data fetch, no API call, no dataset inspection, no QA, no "
    "baseline, and no backtest.",
    "It permits no paper trading, no live trading, no broker or exchange "
    "connection, and no automation.",
    "It writes no runtime, registry, ledger, or dashboard state.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
    "The most a verdict can do is PROMOTE_TO_REVIEW, which only invites a human "
    "research review and never produces an execution instruction.",
)

_OPERATOR_NEXT_STEP = (
    "Research-only: a human reviewer must read this scoring verdict, "
    "independently confirm every cohort and penalty, and treat a "
    "PROMOTE_TO_REVIEW outcome as an invitation to review evidence on paper "
    "only. The single permitted next step is to register or assemble the next "
    "research-only contract. No execution of any kind is authorized."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 strategy evidence scoring contract template and is "
    "execution-free.",
    "It inspects an already-produced static set of evidence records and reports "
    "one research-only verdict; it runs nothing, fetches nothing, and connects "
    "nowhere.",
    "Core rule: booked evidence outweighs open/unrealized PnL, and independent "
    "cohorts outweigh correlated clusters; the verdict sorts evidence for a "
    "human, never promotes a strategy beyond a research review.",
    "Outcome precedence is BLOCK > NEEDS_MORE_DATA > KEEP_WATCH > "
    "PROMOTE_TO_REVIEW; an unsafe payload always scores BLOCK.",
    "Open/unrealized PnL is observation-only and contributes zero proof weight; "
    "external bot/whale/funding/BTC-cycle/daily-alpha evidence never counts as "
    "proof.",
    "A PROMOTE_TO_REVIEW verdict never unlocks real-data QA, baseline, "
    "backtest, paper, live, broker/exchange, or automation.",
    "Every finding is attention-only and needs independent confirmation; the "
    "scoring never converts evidence into permission.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human reviewer must read the structured scoring verdict before any "
    "further research-only contract is built.",
    "A human reviewer must confirm a PROMOTE_TO_REVIEW outcome is treated only "
    "as an invitation to review evidence and is never wired to a data fetch, an "
    "API call, a dataset, a QA run, a backtest, a paper/live trade, a broker or "
    "exchange, an order, or any automation.",
    "A human reviewer must independently confirm every cohort and penalty "
    "before it is trusted.",
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
    "scoring_next_required_action",
    "scoring_current_stage",
    "observation_only_evidence_lanes",
    "outcomes",
    "min_independent_cohorts_for_promote",
    "trade_source_tags",
    "external_research_source_tags",
    "booked_status_tags",
    "open_status_tags",
    "authorization_flags",
    "gate_lock_flags",
    "gate_unlock_request_flags",
    "forbidden_promotion_request_flags",
    "executable_signal_fields",
    "forbidden_trade_terms",
    "evidence",
    "scoring",
    "outcome",
    "record_count",
    "booked_count",
    "open_count",
    "independent_cohorts",
    "independent_positive_cohorts",
    "correlated_record_count",
    "same_symbol_duplicate_count",
    "same_direction_pileup_count",
    "open_pnl_observation_only_count",
    "small_sample",
    "block_reasons",
    "penalty_findings",
    "cohort_summaries",
    "score_explanations",
    "scoring_summary_section",
    "scoring_findings_section",
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
    return dict(STRATEGY_EVIDENCE_SCORING_SAFETY_POSTURE)


def build_crypto_d1_strategy_evidence_scoring_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build the read-only strategy evidence scoring contract. Pure; no I/O, no
    data fetch, no mutation of inputs, no clock read, no random id. When no
    payload is given, the static DEFAULT_SAMPLE_EVIDENCE is scored. A fresh dict
    (with fresh lists/dicts) is returned every call. The contract never promotes
    a strategy beyond a research review and it authorizes nothing."""
    if payload is None:
        source = _isolated(DEFAULT_SAMPLE_EVIDENCE)
    elif isinstance(payload, (dict, list, tuple)):
        source = _isolated(payload)
    else:
        source = payload

    score = score_strategy_evidence(source)

    contract: dict[str, Any] = {
        "schema_version": STRATEGY_EVIDENCE_SCORING_SCHEMA_VERSION,
        "label": STRATEGY_EVIDENCE_SCORING_LABEL,
        "status": STRATEGY_EVIDENCE_SCORING_STATUS,
        "stage": "CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT_ONLY",
        "mode": STRATEGY_EVIDENCE_SCORING_MODE,
        "core_rule": STRATEGY_EVIDENCE_SCORING_CORE_RULE,
        "scoring_next_required_action": (
            STRATEGY_EVIDENCE_SCORING_NEXT_REQUIRED_ACTION
        ),
        "scoring_current_stage": STRATEGY_EVIDENCE_SCORING_CURRENT_STAGE,
        "observation_only_evidence_lanes": (
            STRATEGY_EVIDENCE_SCORING_OBSERVATION_ONLY_EVIDENCE_LANES
        ),
        "outcomes": STRATEGY_EVIDENCE_SCORING_OUTCOMES,
        "min_independent_cohorts_for_promote": (
            STRATEGY_EVIDENCE_SCORING_MIN_INDEPENDENT_COHORTS_FOR_PROMOTE
        ),
        "trade_source_tags": STRATEGY_EVIDENCE_SCORING_TRADE_SOURCE_TAGS,
        "external_research_source_tags": (
            STRATEGY_EVIDENCE_SCORING_EXTERNAL_RESEARCH_SOURCE_TAGS
        ),
        "booked_status_tags": STRATEGY_EVIDENCE_SCORING_BOOKED_STATUS_TAGS,
        "open_status_tags": STRATEGY_EVIDENCE_SCORING_OPEN_STATUS_TAGS,
        "authorization_flags": STRATEGY_EVIDENCE_SCORING_AUTHORIZATION_FLAGS,
        "gate_lock_flags": STRATEGY_EVIDENCE_SCORING_GATE_LOCK_FLAGS,
        "gate_unlock_request_flags": (
            STRATEGY_EVIDENCE_SCORING_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_promotion_request_flags": (
            STRATEGY_EVIDENCE_SCORING_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ),
        "executable_signal_fields": (
            STRATEGY_EVIDENCE_SCORING_EXECUTABLE_SIGNAL_FIELDS
        ),
        "forbidden_trade_terms": (
            STRATEGY_EVIDENCE_SCORING_FORBIDDEN_TRADE_TERMS
        ),
        "evidence": _isolated(source)
        if isinstance(source, (dict, list))
        else {},
        "scoring": score,
        "outcome": score["outcome"],
        "record_count": score["record_count"],
        "booked_count": score["booked_count"],
        "open_count": score["open_count"],
        "independent_cohorts": score["independent_cohorts"],
        "independent_positive_cohorts": score["independent_positive_cohorts"],
        "correlated_record_count": score["correlated_record_count"],
        "same_symbol_duplicate_count": score["same_symbol_duplicate_count"],
        "same_direction_pileup_count": score["same_direction_pileup_count"],
        "open_pnl_observation_only_count": (
            score["open_pnl_observation_only_count"]
        ),
        "small_sample": score["small_sample"],
        "block_reasons": list(score["block_reasons"]),
        "penalty_findings": list(score["penalty_findings"]),
        "cohort_summaries": list(score["cohort_summaries"]),
        "score_explanations": list(score["score_explanations"]),
        "scoring_summary_section": _scoring_summary_section(score),
        "scoring_findings_section": _scoring_findings_section(score),
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

# The generated-guidance fields whose text is the scoring's own actionable
# output. These must never contain an execution verb. (The raw echoed
# ``evidence``, ``cohort_summaries``, ``penalty_findings`` and ``block_reasons``
# embed caller-supplied symbols and are excluded from this check.)
_ACTIONABLE_TEXT_FIELDS: tuple[str, ...] = (
    "outcome",
    "operator_next_step",
    "scoring_summary_section",
    "scoring_findings_section",
    "observation_only_section",
    "no_execution_authorization_section",
    "score_explanations",
)


def _contains_forbidden_term(text: str) -> bool:
    tokens = _word_tokens(text)
    return any(
        term in tokens
        for term in STRATEGY_EVIDENCE_SCORING_FORBIDDEN_TRADE_TERMS
    )


def _no_forbidden_trade_terms(contract: dict[str, Any]) -> bool:
    """True when none of the scoring's actionable guidance fields contain an
    execution verb as a whole word. Pure; reads only the contract dict.

    A BLOCK findings section can legitimately quote an offending input field
    name while explaining the refusal, so that section is skipped when the
    verdict is BLOCK."""
    blocked = contract.get("outcome") == OUTCOME_BLOCK
    for field in _ACTIONABLE_TEXT_FIELDS:
        if field == "scoring_findings_section" and blocked:
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
        == STRATEGY_EVIDENCE_SCORING_SCHEMA_VERSION
    )
    label_ok = safe.get("label") == STRATEGY_EVIDENCE_SCORING_LABEL
    read_only = safe.get("read_only") is True
    research_only = (
        safe.get("research_only") is True
        and safe.get("mode") == "RESEARCH_ONLY"
    )
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_STRATEGY_EVIDENCE_SCORING_CONTRACT_ONLY"
    )
    core_rule_ok = (
        safe.get("core_rule") == STRATEGY_EVIDENCE_SCORING_CORE_RULE
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
        and posture == STRATEGY_EVIDENCE_SCORING_SAFETY_POSTURE
    )

    outcome_ok = safe.get("outcome") in _OUTCOME_SET
    lanes_ok = (
        tuple(safe.get("observation_only_evidence_lanes") or ())
        == STRATEGY_EVIDENCE_SCORING_OBSERVATION_ONLY_EVIDENCE_LANES
    )
    outcomes_ok = (
        tuple(safe.get("outcomes") or ())
        == STRATEGY_EVIDENCE_SCORING_OUTCOMES
    )

    scoring = safe.get("scoring")
    scoring_ok = (
        isinstance(scoring, dict)
        and scoring.get("authorizes_nothing") is True
        and scoring.get("scores_research_only") is True
        and scoring.get("promotes_beyond_review") is False
        and scoring.get("outcome") in _OUTCOME_SET
    )

    no_trade_language = _no_forbidden_trade_terms(safe)

    sections_ok = all(
        len(tuple(safe.get(section) or ())) >= 1
        for section in (
            "scoring_summary_section",
            "scoring_findings_section",
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
        and scoring_ok
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
        "scoring_ok": scoring_ok,
        "no_trade_language": no_trade_language,
        "sections_ok": sections_ok,
        "operator_next_step_ok": operator_next_step_ok,
    }


def validate_crypto_d1_strategy_evidence_scoring_contract(
    contract: Any,
) -> dict[str, Any]:
    """Public validation entry point; returns the deterministic verdict dict."""
    return _validate(contract)


def render_crypto_d1_strategy_evidence_scoring_contract_markdown(
    contract: Any,
) -> str:
    """Render an informational, read-only markdown summary of the contract.
    Pure; builds and returns a string, writes nothing."""
    safe = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Strategy Evidence Scoring Contract")
    lines.append("")
    lines.append("- Label: " + _as_text(safe.get("label")))
    lines.append("- Mode: " + _as_text(safe.get("mode")))
    lines.append("- Status: " + _as_text(safe.get("status")))
    lines.append("- Outcome: " + _as_text(safe.get("outcome")))
    lines.append("- Records scored: " + str(safe.get("record_count")))
    lines.append("- Booked: " + str(safe.get("booked_count")))
    lines.append("- Open/unrealized: " + str(safe.get("open_count")))
    lines.append(
        "- Independent positive cohorts: "
        + str(safe.get("independent_positive_cohorts"))
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

    _emit("Scoring Summary", "scoring_summary_section")
    _emit("Scoring Findings", "scoring_findings_section")
    _emit("Cohorts", "cohort_summaries")
    _emit("Penalties", "penalty_findings")
    _emit("Observation-Only Evidence Lanes", "observation_only_section")
    _emit("No Execution Authorization", "no_execution_authorization_section")
    lines.append("")
    lines.append("## Operator Next Step")
    lines.append("- " + _as_text(safe.get("operator_next_step")))
    return "\n".join(lines)

"""SPARTA Offline Strategy Factory - CRYPTO-D1 EXTERNAL HUMAN TRADER EVIDENCE.

A PURE, stdlib-only *read-only paper contract* that *classifies* a small,
caller-provided set of static external human-trader evidence records (calls and
notes attributed to human traders -- signal groups, paid mentors, influencers,
screenshot PnL) and sorts the whole set into exactly one research-only verdict.
It returns a deterministic, structured assessment: the verdict, the per-record
observation lanes, the penalties applied, and a plain-language explanation -- so
a human can decide, on paper, whether any external human-trader evidence is
worth logging as a research observation.

CORE RULE: external human-trader evidence is ALWAYS observation-only and NEVER
counts as proof or permission. The most a verdict can do is log the evidence as
an observation for a human to review; it authorizes nothing and unlocks no gate.
A verifiable, attributable note is logged as a research note; a bare directional
call with no verifiable track record is logged as risky-unverified; a marketing
/ guaranteed-profit / hype claim is discarded.

Classification stances (all applied deterministically, on paper):
  - A claim of guaranteed profit, risk-free returns, or get-rich hype is
    discarded -- it is noise, never evidence.
  - A directional call with no verifiable, timestamped, audited, or on-chain
    track record is risky-unverified -- observation-only, flagged.
  - A concrete, attributable, verifiable note is a research note -- still
    observation-only and still requires independent confirmation.
  - Screenshot PnL and influencer calls never count as booked proof.

This contract authorizes NOTHING real. It does NOT fetch any data, call any API,
inspect any dataset, acquire any real data, load any file, open any network, run
any QA, baseline, backtest, or simulation, produce any trade signal, reach any
broker / exchange / order / account / API surface, trade any paper and any live,
promote any strategy beyond a research observation, unlock any downstream gate
(real_data_qa, baseline_backtest, paper_trading_gate, micro_live_gate stay
blocked / locked), trigger any automation, write any runtime / registry /
ledger / dashboard / report state, spawn any child process, read any
environment, record any wall-clock time, mint any random id, or dynamically
import anything. It ONLY inspects the static records the caller passes in, using
pure dict / string / number arithmetic.

Assessment outcomes (precedence, highest first / most restrictive first):
    BLOCK > NO_EVIDENCE > DISCARD_HYPE > LOG_AS_OBSERVATION
  - BLOCK             -> the payload is unsafe: an authorization flag is set, a
                         gate-unlock or forbidden-promotion request is present,
                         or a record carries an executable order/signal field.
  - NO_EVIDENCE       -> there is nothing to assess yet; supply static external
                         human-trader evidence records for a future review.
  - DISCARD_HYPE      -> records exist, but every one is marketing / hype /
                         guaranteed-profit noise; nothing is logged.
  - LOG_AS_OBSERVATION-> one or more records are usable observation-only evidence
                         (a research note or a risky-unverified call); a human
                         may REVIEW them as observations. This unlocks nothing.

Public API:
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_SCHEMA_VERSION
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_LABEL
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_STATUS
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_MODE
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_CORE_RULE
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_SAFETY_POSTURE
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_OBSERVATION_ONLY_EVIDENCE_LANES
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_OUTCOMES
  - OUTCOME_BLOCK / OUTCOME_NO_EVIDENCE / OUTCOME_DISCARD_HYPE /
    OUTCOME_LOG_AS_OBSERVATION
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_LANES
  - LANE_RESEARCH_NOTE / LANE_RISKY_UNVERIFIED / LANE_HYPE_DISCARD
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_HYPE_MARKERS
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_VERIFIABLE_MARKERS
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_AUTHORIZATION_FLAGS
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_LOCK_FLAGS
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_UNLOCK_REQUEST_FLAGS
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_EXECUTABLE_SIGNAL_FIELDS
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_TRADE_TERMS
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_NEXT_REQUIRED_ACTION
  - EXTERNAL_HUMAN_TRADER_EVIDENCE_CURRENT_STAGE
  - DEFAULT_SAMPLE_HUMAN_TRADER_EVIDENCE
  - assess_external_human_trader_evidence(payload)
  - build_crypto_d1_external_human_trader_evidence_contract(payload=None)
  - validate_crypto_d1_external_human_trader_evidence_contract(contract)
  - render_crypto_d1_external_human_trader_evidence_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

__all__ = [
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_SCHEMA_VERSION",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_LABEL",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_STATUS",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_MODE",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_CORE_RULE",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_SAFETY_POSTURE",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_OBSERVATION_ONLY_EVIDENCE_LANES",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_OUTCOMES",
    "OUTCOME_BLOCK",
    "OUTCOME_NO_EVIDENCE",
    "OUTCOME_DISCARD_HYPE",
    "OUTCOME_LOG_AS_OBSERVATION",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_LANES",
    "LANE_RESEARCH_NOTE",
    "LANE_RISKY_UNVERIFIED",
    "LANE_HYPE_DISCARD",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_HYPE_MARKERS",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_VERIFIABLE_MARKERS",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_AUTHORIZATION_FLAGS",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_LOCK_FLAGS",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_UNLOCK_REQUEST_FLAGS",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_EXECUTABLE_SIGNAL_FIELDS",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_TRADE_TERMS",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_NEXT_REQUIRED_ACTION",
    "EXTERNAL_HUMAN_TRADER_EVIDENCE_CURRENT_STAGE",
    "DEFAULT_SAMPLE_HUMAN_TRADER_EVIDENCE",
    "assess_external_human_trader_evidence",
    "build_crypto_d1_external_human_trader_evidence_contract",
    "validate_crypto_d1_external_human_trader_evidence_contract",
    "render_crypto_d1_external_human_trader_evidence_contract_markdown",
]

EXTERNAL_HUMAN_TRADER_EVIDENCE_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_external_human_trader_evidence_contract.v1"
)
EXTERNAL_HUMAN_TRADER_EVIDENCE_LABEL = (
    "Block 163 - Crypto-D1 External Human Trader Evidence Contract"
)
EXTERNAL_HUMAN_TRADER_EVIDENCE_STATUS = (
    "READ_ONLY_CRYPTO_D1_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT"
)
EXTERNAL_HUMAN_TRADER_EVIDENCE_MODE = "RESEARCH_ONLY"

EXTERNAL_HUMAN_TRADER_EVIDENCE_CORE_RULE = (
    "External human-trader evidence is always observation-only and never counts "
    "as proof or permission; the most a verdict can do is log the evidence as an "
    "observation for a human to review, and it authorizes nothing."
)

# Next action / stage this contract FULFILLS on paper. Defined locally as plain
# strings so this module never imports the mission-flow registry (registering
# this contract is the separate, later step; importing the registry would also
# risk a circular import).
EXTERNAL_HUMAN_TRADER_EVIDENCE_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT"
)
EXTERNAL_HUMAN_TRADER_EVIDENCE_CURRENT_STAGE = (
    "CRYPTO_D1_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT_REQUIRED"
)

# Evidence lanes that remain observation-only at every assessment outcome. The
# assessment reads about them; it never wires any of them to a fetch, a QA run, a
# backtest, a trade, a broker/exchange, an order, or any automation.
EXTERNAL_HUMAN_TRADER_EVIDENCE_OBSERVATION_ONLY_EVIDENCE_LANES: tuple[
    str, ...
] = (
    "external_human_trader_call",
    "signal_group_call",
    "paid_mentor_call",
    "influencer_call",
    "screenshot_pnl_evidence",
    "open_unrealized_pnl",
)

# Assessment outcomes, in precedence order (highest / most restrictive first).
OUTCOME_BLOCK = "BLOCK"
OUTCOME_NO_EVIDENCE = "NO_EVIDENCE"
OUTCOME_DISCARD_HYPE = "DISCARD_HYPE"
OUTCOME_LOG_AS_OBSERVATION = "LOG_AS_OBSERVATION"

EXTERNAL_HUMAN_TRADER_EVIDENCE_OUTCOMES: tuple[str, ...] = (
    OUTCOME_BLOCK,
    OUTCOME_NO_EVIDENCE,
    OUTCOME_DISCARD_HYPE,
    OUTCOME_LOG_AS_OBSERVATION,
)
_OUTCOME_SET: frozenset[str] = frozenset(
    EXTERNAL_HUMAN_TRADER_EVIDENCE_OUTCOMES
)
# Lower index == higher precedence / more restrictive.
_OUTCOME_PRECEDENCE: dict[str, int] = {
    OUTCOME_BLOCK: 0,
    OUTCOME_NO_EVIDENCE: 1,
    OUTCOME_DISCARD_HYPE: 2,
    OUTCOME_LOG_AS_OBSERVATION: 3,
}

# Per-record observation lanes (all observation-only; none is ever proof).
LANE_RESEARCH_NOTE = "research_note"
LANE_RISKY_UNVERIFIED = "risky_unverified"
LANE_HYPE_DISCARD = "hype_discard"

EXTERNAL_HUMAN_TRADER_EVIDENCE_LANES: tuple[str, ...] = (
    LANE_RESEARCH_NOTE,
    LANE_RISKY_UNVERIFIED,
    LANE_HYPE_DISCARD,
)

# Substrings that mark a record as marketing / hype / guaranteed-profit noise.
# Matched case-insensitively against the record's joined text.
EXTERNAL_HUMAN_TRADER_EVIDENCE_HYPE_MARKERS: tuple[str, ...] = (
    "guaranteed",
    "guarantee",
    "risk-free",
    "risk free",
    "riskfree",
    "riskless",
    "cant lose",
    "can't lose",
    "no loss",
    "no-loss",
    "easy money",
    "free money",
    "financial freedom",
    "get rich",
    "100x",
    "1000x",
    "surefire",
    "sure thing",
    "moon shot",
    "to the moon",
    "lambo",
    "pump group",
)

# Substrings that mark a record as a concrete, verifiable research note. Matched
# case-insensitively against the record's joined text. A truthy ``verifiable``
# field also qualifies.
EXTERNAL_HUMAN_TRADER_EVIDENCE_VERIFIABLE_MARKERS: tuple[str, ...] = (
    "verifiable",
    "verified",
    "track record",
    "trackrecord",
    "timestamped",
    "time-stamped",
    "audited",
    "on-chain",
    "on chain",
    "onchain",
    "documented",
    "logged trade",
    "public ledger",
)

# Top-level (or per-record) authorization flags that, if truthy, force BLOCK.
EXTERNAL_HUMAN_TRADER_EVIDENCE_AUTHORIZATION_FLAGS: tuple[str, ...] = (
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
EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, force BLOCK.
EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
)

# Requests asking the assessment to mean execution / live promotion / copy
# trading. Any truthy value forces BLOCK: a verdict can only ever mean a
# research-observation log.
EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS: tuple[
    str, ...
] = (
    "force_promote",
    "promote_to_live",
    "promote_to_paper",
    "approve_trade",
    "authorize_trade",
    "execute",
    "place_order",
    "go_live",
    "copy_trade",
    "auto_follow",
)

# Fields whose presence (non-empty) on a record signals an executable order /
# signal instruction rather than historical evidence -> BLOCK.
EXTERNAL_HUMAN_TRADER_EVIDENCE_EXECUTABLE_SIGNAL_FIELDS: tuple[str, ...] = (
    "order",
    "signal",
    "trade_instruction",
    "execution",
    "live_order",
    "place_order",
    "copy_trade_command",
)

# Execution / promotion verbs the assessment's own generated guidance must never
# contain as whole words.
EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
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
EXTERNAL_HUMAN_TRADER_EVIDENCE_SAFETY_POSTURE: dict[str, bool] = {
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


# A deterministic, illustrative paper sample: three external human-trader
# evidence records -- one verifiable research note, one bare unverified call, and
# one hype claim. Because at least one record is usable observation-only
# evidence, the default build assesses LOG_AS_OBSERVATION. Nothing here is real
# data; static example only.
DEFAULT_SAMPLE_HUMAN_TRADER_EVIDENCE: dict[str, Any] = {
    "label": "Crypto-D1 external human-trader evidence (static sample)",
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
            "id": "h1",
            "trader_handle": "onchain_desk",
            "note": "BTC swing thesis with an on-chain, timestamped track "
            "record",
            "source": "external_human_trader_call",
        },
        {
            "id": "h2",
            "trader_handle": "fast_calls",
            "note": "A bare directional ETH call shared without proof",
            "source": "signal_group_call",
        },
        {
            "id": "h3",
            "trader_handle": "moon_mentor",
            "note": "Guaranteed 100x risk-free returns, financial freedom",
            "source": "influencer_call",
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


def _record_id(record: dict[str, Any], index: int) -> str:
    rid = _as_text(record.get("id"))
    return rid if rid else "#" + str(index)


def _record_text(record: dict[str, Any]) -> str:
    """Lowercased join of the record's string values, used for marker matching.
    Only string keys/values contribute; flags and numbers are ignored here."""
    parts: list[str] = []
    for key, value in record.items():
        if isinstance(value, str):
            parts.append(value)
    return " ".join(parts).lower()


def _classify_record(record: dict[str, Any]) -> str:
    """Deterministic per-record observation lane. Hype noise is discarded; a
    verifiable note is a research note; everything else is risky-unverified."""
    text = _record_text(record)
    for marker in EXTERNAL_HUMAN_TRADER_EVIDENCE_HYPE_MARKERS:
        if marker in text:
            return LANE_HYPE_DISCARD
    if _truthy(record.get("verifiable")):
        return LANE_RESEARCH_NOTE
    for marker in EXTERNAL_HUMAN_TRADER_EVIDENCE_VERIFIABLE_MARKERS:
        if marker in text:
            return LANE_RESEARCH_NOTE
    return LANE_RISKY_UNVERIFIED


def _safety_block_findings(
    controls: dict[str, Any], records: list[dict[str, Any]]
) -> list[str]:
    """Reasons the whole payload is unsafe and must score BLOCK. Pure."""
    reasons: list[str] = []
    for flag in EXTERNAL_HUMAN_TRADER_EVIDENCE_AUTHORIZATION_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("authorization flag requested: " + flag)
    for flag in EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_LOCK_FLAGS:
        if flag in controls and controls.get(flag) is not True:
            reasons.append("gate unlock attempt: " + flag + " is not locked")
    for flag in EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_UNLOCK_REQUEST_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("gate unlock request: " + flag)
    for flag in EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        if _truthy(controls.get(flag)):
            reasons.append("forbidden promotion/execution request: " + flag)
    for index, record in enumerate(records):
        rid = _record_id(record, index)
        for field in EXTERNAL_HUMAN_TRADER_EVIDENCE_EXECUTABLE_SIGNAL_FIELDS:
            if field in record and _non_empty(record.get(field)):
                reasons.append(
                    "record " + rid + " carries executable field: " + field
                )
        for flag in (
            EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ):
            if _truthy(record.get(flag)):
                reasons.append(
                    "record "
                    + rid
                    + " requests forbidden promotion/execution: "
                    + flag
                )
        for flag in EXTERNAL_HUMAN_TRADER_EVIDENCE_AUTHORIZATION_FLAGS:
            if _truthy(record.get(flag)):
                reasons.append(
                    "record " + rid + " requests authorization: " + flag
                )
    return reasons


def _assessment_explanations(
    outcome: str,
    record_count: int,
    research_note_count: int,
    risky_unverified_count: int,
    hype_discard_count: int,
) -> list[str]:
    """Plain-language rationale for the verdict. References counts only (never a
    raw trader handle or claim text), so the guidance never emits an execution
    verb."""
    lines = [
        "Assessed "
        + str(record_count)
        + " external human-trader record(s): "
        + str(research_note_count)
        + " research note(s), "
        + str(risky_unverified_count)
        + " risky-unverified, "
        + str(hype_discard_count)
        + " hype-discard.",
        "External human-trader evidence is observation-only and never counts as "
        "booked proof; the best a verdict can do is log it for a human to "
        "review.",
    ]
    if outcome == OUTCOME_BLOCK:
        lines.append(
            "Verdict BLOCK: the payload requested an authorization, a gate "
            "unlock, a forbidden promotion, or carried an executable field; the "
            "assessment refuses it and authorizes nothing."
        )
    elif outcome == OUTCOME_NO_EVIDENCE:
        lines.append(
            "Verdict NO_EVIDENCE: there is nothing to assess yet; supply static "
            "external human-trader evidence records for a future research "
            "review."
        )
    elif outcome == OUTCOME_DISCARD_HYPE:
        lines.append(
            "Verdict DISCARD_HYPE: every record is marketing / hype / "
            "guaranteed-profit noise; nothing is logged as an observation."
        )
    else:
        lines.append(
            "Verdict LOG_AS_OBSERVATION: one or more records are usable "
            "observation-only evidence, so a human may REVIEW them as "
            "observations. This unlocks no QA, no baseline, no backtest, no "
            "paper, no live, no broker/exchange, and no automation, and it is "
            "never booked proof."
        )
    return lines


def assess_external_human_trader_evidence(payload: Any) -> dict[str, Any]:
    """Return a deterministic, research-only assessment for a static external
    human-trader evidence payload.

    Pure; no I/O, no data fetch, no clock read, no mutation, no random id.
    Malformed / missing inputs never raise. ``payload`` may be a list of evidence
    records, or a dict carrying an ``evidence`` list plus optional control flags.
    The verdict is one of BLOCK / NO_EVIDENCE / DISCARD_HYPE / LOG_AS_OBSERVATION;
    LOG_AS_OBSERVATION only authorizes a human research review and unlocks
    nothing."""
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

    classified: list[dict[str, Any]] = []
    for index, record in enumerate(records):
        rid = _record_id(record, index)
        lane = _classify_record(record)
        classified.append(
            {
                "id": rid,
                "trader_handle": _as_text(record.get("trader_handle")),
                "source": _as_text(record.get("source")),
                "lane": lane,
            }
        )

    research_note_count = sum(
        1 for c in classified if c["lane"] == LANE_RESEARCH_NOTE
    )
    risky_unverified_count = sum(
        1 for c in classified if c["lane"] == LANE_RISKY_UNVERIFIED
    )
    hype_discard_count = sum(
        1 for c in classified if c["lane"] == LANE_HYPE_DISCARD
    )
    usable_observation_count = research_note_count + risky_unverified_count

    lane_summaries: list[str] = []
    for entry in sorted(classified, key=lambda c: c["id"]):
        lane_summaries.append(
            "Record " + entry["id"] + " -> " + entry["lane"] + "."
        )

    penalty_findings: list[str] = []
    if risky_unverified_count > 0:
        penalty_findings.append(
            "unverified penalty: "
            + str(risky_unverified_count)
            + " record(s) carry no verifiable track record and stay "
            "observation-only, never proof."
        )
    if hype_discard_count > 0:
        penalty_findings.append(
            "hype penalty: "
            + str(hype_discard_count)
            + " record(s) are marketing / guaranteed-profit noise and are "
            "discarded."
        )
    if research_note_count > 0:
        penalty_findings.append(
            "observation-only reminder: "
            + str(research_note_count)
            + " verifiable research note(s) still require independent "
            "confirmation and never count as booked proof."
        )

    record_count = len(records)

    if block_reasons:
        outcome = OUTCOME_BLOCK
    elif record_count == 0:
        outcome = OUTCOME_NO_EVIDENCE
    elif usable_observation_count >= 1:
        outcome = OUTCOME_LOG_AS_OBSERVATION
    else:
        outcome = OUTCOME_DISCARD_HYPE

    assessment_explanations = _assessment_explanations(
        outcome,
        record_count=record_count,
        research_note_count=research_note_count,
        risky_unverified_count=risky_unverified_count,
        hype_discard_count=hype_discard_count,
    )

    return {
        "outcome": outcome,
        "mode": EXTERNAL_HUMAN_TRADER_EVIDENCE_MODE,
        "evidence_present": record_count > 0,
        "record_count": record_count,
        "research_note_count": research_note_count,
        "risky_unverified_count": risky_unverified_count,
        "hype_discard_count": hype_discard_count,
        "usable_observation_count": usable_observation_count,
        "classified_records": classified,
        "lane_summaries": lane_summaries,
        "block_reasons": block_reasons,
        "penalty_findings": penalty_findings,
        "assessment_explanations": assessment_explanations,
        "promotes_beyond_review": False,
        "logs_research_only": True,
        "counts_as_proof": False,
        "authorizes_nothing": True,
    }


def _assessment_summary_section(assessment: dict[str, Any]) -> list[str]:
    return [
        "Assessment verdict: " + assessment["outcome"] + ".",
        "Mode: " + assessment["mode"] + " (research observation log only).",
        "Records assessed: "
        + str(assessment["record_count"])
        + " ("
        + str(assessment["research_note_count"])
        + " research note, "
        + str(assessment["risky_unverified_count"])
        + " risky-unverified, "
        + str(assessment["hype_discard_count"])
        + " hype-discard).",
        "Usable observation-only records: "
        + str(assessment["usable_observation_count"])
        + ".",
        "External human-trader evidence never counts as booked proof; a "
        "LOG_AS_OBSERVATION verdict authorizes nothing.",
    ]


def _assessment_findings_section(assessment: dict[str, Any]) -> list[str]:
    outcome = assessment["outcome"]
    if outcome == OUTCOME_BLOCK:
        lines = ["Payload scored BLOCK; it is unsafe and is refused:"]
        lines.extend("- " + reason for reason in assessment["block_reasons"])
        lines.append(
            "BLOCK authorizes nothing and unlocks no gate; the unsafe payload "
            "must be rebuilt as static research-only evidence."
        )
        return lines
    lines = list(assessment["assessment_explanations"])
    if assessment["penalty_findings"]:
        lines.append("Penalties applied:")
        lines.extend(
            "- " + finding for finding in assessment["penalty_findings"]
        )
    return lines


def _observation_only_section() -> list[str]:
    lines = [
        lane + " remains observation-only (attention only)."
        for lane in (
            EXTERNAL_HUMAN_TRADER_EVIDENCE_OBSERVATION_ONLY_EVIDENCE_LANES
        )
    ]
    lines.append(
        "No evidence lane is ever wired to a data fetch, an API call, a "
        "dataset, a QA run, a backtest, a paper/live trade, a broker or "
        "exchange, or any automation."
    )
    return lines


_NO_EXECUTION_AUTHORIZATION_SECTION: tuple[str, ...] = (
    "This assessment authorizes no trade and no position of any kind.",
    "It permits no data fetch, no API call, no dataset inspection, no QA, no "
    "baseline, and no backtest.",
    "It permits no paper trading, no live trading, no broker or exchange "
    "connection, no copy trading, and no automation.",
    "It writes no runtime, registry, ledger, or dashboard state.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
    "The most a verdict can do is LOG_AS_OBSERVATION, which only invites a human "
    "research review and never produces an execution instruction.",
)

_OPERATOR_NEXT_STEP = (
    "Research-only: a human reviewer must read this assessment verdict, "
    "independently confirm every lane and penalty, and treat a "
    "LOG_AS_OBSERVATION outcome as an invitation to review observations on paper "
    "only. The single permitted next step is to register or assemble the next "
    "research-only contract. No execution of any kind is authorized."
)

_OPERATOR_NOTES: tuple[str, ...] = (
    "This is a crypto-d1 external human-trader evidence contract template and "
    "is execution-free.",
    "It inspects an already-produced static set of external human-trader "
    "records and reports one research-only verdict; it runs nothing, fetches "
    "nothing, and connects nowhere.",
    "Core rule: external human-trader evidence is always observation-only and "
    "never counts as proof or permission; the verdict logs evidence for a human, "
    "never promotes a strategy beyond a research observation.",
    "Outcome precedence is BLOCK > NO_EVIDENCE > DISCARD_HYPE > "
    "LOG_AS_OBSERVATION; an unsafe payload always scores BLOCK.",
    "Guaranteed-profit and hype claims are discarded; unverified calls stay "
    "risky observation-only; only verifiable notes become research notes, and "
    "even those need independent confirmation.",
    "A LOG_AS_OBSERVATION verdict never unlocks real-data QA, baseline, "
    "backtest, paper, live, broker/exchange, copy trading, or automation.",
    "Every finding is attention-only and needs independent confirmation; the "
    "assessment never converts evidence into permission.",
    "real_data_qa stays BLOCKED, baseline_backtest stays BLOCKED, and "
    "paper/micro-live stay LOCKED.",
)

_HUMAN_OPERATOR_REQUIRED_NEXT_STEPS: tuple[str, ...] = (
    "A human reviewer must read the structured assessment verdict before any "
    "further research-only contract is built.",
    "A human reviewer must confirm a LOG_AS_OBSERVATION outcome is treated only "
    "as an invitation to review observations and is never wired to a data "
    "fetch, an API call, a dataset, a QA run, a backtest, a paper/live trade, a "
    "broker or exchange, an order, copy trading, or any automation.",
    "A human reviewer must independently confirm every lane and penalty before "
    "it is trusted, and must treat all of it as observation-only, never proof.",
    "A human reviewer must confirm the next step is only to register or build "
    "the next research-only contract, still on paper.",
    "No execution, data fetch, API call, dataset inspection, data acquisition, "
    "QA, backtest, paper/live, broker/exchange, copy trading, automation, "
    "promotion, or downstream-gate unlock may proceed.",
)

# Top-level fields required for a contract to validate.
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "stage",
    "mode",
    "core_rule",
    "assessment_next_required_action",
    "assessment_current_stage",
    "observation_only_evidence_lanes",
    "outcomes",
    "lanes",
    "hype_markers",
    "verifiable_markers",
    "authorization_flags",
    "gate_lock_flags",
    "gate_unlock_request_flags",
    "forbidden_promotion_request_flags",
    "executable_signal_fields",
    "forbidden_trade_terms",
    "evidence",
    "assessment",
    "outcome",
    "record_count",
    "research_note_count",
    "risky_unverified_count",
    "hype_discard_count",
    "usable_observation_count",
    "lane_summaries",
    "block_reasons",
    "penalty_findings",
    "assessment_explanations",
    "assessment_summary_section",
    "assessment_findings_section",
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
    "counts_as_proof",
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
    return dict(EXTERNAL_HUMAN_TRADER_EVIDENCE_SAFETY_POSTURE)


def build_crypto_d1_external_human_trader_evidence_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build the read-only external human-trader evidence contract. Pure; no I/O,
    no data fetch, no mutation of inputs, no clock read, no random id. When no
    payload is given, the static DEFAULT_SAMPLE_HUMAN_TRADER_EVIDENCE is
    assessed. A fresh dict (with fresh lists/dicts) is returned every call. The
    contract never promotes a strategy beyond a research observation and it
    authorizes nothing."""
    if payload is None:
        source = _isolated(DEFAULT_SAMPLE_HUMAN_TRADER_EVIDENCE)
    elif isinstance(payload, (dict, list, tuple)):
        source = _isolated(payload)
    else:
        source = payload

    assessment = assess_external_human_trader_evidence(source)

    contract: dict[str, Any] = {
        "schema_version": EXTERNAL_HUMAN_TRADER_EVIDENCE_SCHEMA_VERSION,
        "label": EXTERNAL_HUMAN_TRADER_EVIDENCE_LABEL,
        "status": EXTERNAL_HUMAN_TRADER_EVIDENCE_STATUS,
        "stage": "CRYPTO_D1_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT_ONLY",
        "mode": EXTERNAL_HUMAN_TRADER_EVIDENCE_MODE,
        "core_rule": EXTERNAL_HUMAN_TRADER_EVIDENCE_CORE_RULE,
        "assessment_next_required_action": (
            EXTERNAL_HUMAN_TRADER_EVIDENCE_NEXT_REQUIRED_ACTION
        ),
        "assessment_current_stage": (
            EXTERNAL_HUMAN_TRADER_EVIDENCE_CURRENT_STAGE
        ),
        "observation_only_evidence_lanes": (
            EXTERNAL_HUMAN_TRADER_EVIDENCE_OBSERVATION_ONLY_EVIDENCE_LANES
        ),
        "outcomes": EXTERNAL_HUMAN_TRADER_EVIDENCE_OUTCOMES,
        "lanes": EXTERNAL_HUMAN_TRADER_EVIDENCE_LANES,
        "hype_markers": EXTERNAL_HUMAN_TRADER_EVIDENCE_HYPE_MARKERS,
        "verifiable_markers": (
            EXTERNAL_HUMAN_TRADER_EVIDENCE_VERIFIABLE_MARKERS
        ),
        "authorization_flags": (
            EXTERNAL_HUMAN_TRADER_EVIDENCE_AUTHORIZATION_FLAGS
        ),
        "gate_lock_flags": EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_LOCK_FLAGS,
        "gate_unlock_request_flags": (
            EXTERNAL_HUMAN_TRADER_EVIDENCE_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_promotion_request_flags": (
            EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ),
        "executable_signal_fields": (
            EXTERNAL_HUMAN_TRADER_EVIDENCE_EXECUTABLE_SIGNAL_FIELDS
        ),
        "forbidden_trade_terms": (
            EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_TRADE_TERMS
        ),
        "evidence": _isolated(source)
        if isinstance(source, (dict, list))
        else {},
        "assessment": assessment,
        "outcome": assessment["outcome"],
        "record_count": assessment["record_count"],
        "research_note_count": assessment["research_note_count"],
        "risky_unverified_count": assessment["risky_unverified_count"],
        "hype_discard_count": assessment["hype_discard_count"],
        "usable_observation_count": assessment["usable_observation_count"],
        "lane_summaries": list(assessment["lane_summaries"]),
        "block_reasons": list(assessment["block_reasons"]),
        "penalty_findings": list(assessment["penalty_findings"]),
        "assessment_explanations": list(
            assessment["assessment_explanations"]
        ),
        "assessment_summary_section": _assessment_summary_section(assessment),
        "assessment_findings_section": _assessment_findings_section(
            assessment
        ),
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
        "counts_as_proof": False,
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
    "counts_as_proof",
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

# The generated-guidance fields whose text is the assessment's own actionable
# output. These must never contain an execution verb. (The raw echoed
# ``evidence``, ``lane_summaries``, ``penalty_findings`` and ``block_reasons``
# embed caller-supplied handles / notes and are excluded from this check.)
_ACTIONABLE_TEXT_FIELDS: tuple[str, ...] = (
    "outcome",
    "operator_next_step",
    "assessment_summary_section",
    "assessment_findings_section",
    "observation_only_section",
    "no_execution_authorization_section",
    "assessment_explanations",
)


def _contains_forbidden_term(text: str) -> bool:
    tokens = _word_tokens(text)
    return any(
        term in tokens
        for term in EXTERNAL_HUMAN_TRADER_EVIDENCE_FORBIDDEN_TRADE_TERMS
    )


def _no_forbidden_trade_terms(contract: dict[str, Any]) -> bool:
    """True when none of the assessment's actionable guidance fields contain an
    execution verb as a whole word. Pure; reads only the contract dict.

    A BLOCK findings section can legitimately quote an offending input field
    name while explaining the refusal, so that section is skipped when the
    verdict is BLOCK."""
    blocked = contract.get("outcome") == OUTCOME_BLOCK
    for field in _ACTIONABLE_TEXT_FIELDS:
        if field == "assessment_findings_section" and blocked:
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
        == EXTERNAL_HUMAN_TRADER_EVIDENCE_SCHEMA_VERSION
    )
    label_ok = safe.get("label") == EXTERNAL_HUMAN_TRADER_EVIDENCE_LABEL
    read_only = safe.get("read_only") is True
    research_only = (
        safe.get("research_only") is True
        and safe.get("mode") == "RESEARCH_ONLY"
    )
    stage_ok = (
        safe.get("stage")
        == "CRYPTO_D1_EXTERNAL_HUMAN_TRADER_EVIDENCE_CONTRACT_ONLY"
    )
    core_rule_ok = (
        safe.get("core_rule") == EXTERNAL_HUMAN_TRADER_EVIDENCE_CORE_RULE
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
        and posture == EXTERNAL_HUMAN_TRADER_EVIDENCE_SAFETY_POSTURE
    )

    outcome_ok = safe.get("outcome") in _OUTCOME_SET
    lanes_ok = (
        tuple(safe.get("observation_only_evidence_lanes") or ())
        == EXTERNAL_HUMAN_TRADER_EVIDENCE_OBSERVATION_ONLY_EVIDENCE_LANES
    )
    outcomes_ok = (
        tuple(safe.get("outcomes") or ())
        == EXTERNAL_HUMAN_TRADER_EVIDENCE_OUTCOMES
    )
    record_lanes_ok = (
        tuple(safe.get("lanes") or ()) == EXTERNAL_HUMAN_TRADER_EVIDENCE_LANES
    )

    assessment = safe.get("assessment")
    assessment_ok = (
        isinstance(assessment, dict)
        and assessment.get("authorizes_nothing") is True
        and assessment.get("logs_research_only") is True
        and assessment.get("counts_as_proof") is False
        and assessment.get("promotes_beyond_review") is False
        and assessment.get("outcome") in _OUTCOME_SET
    )

    no_trade_language = _no_forbidden_trade_terms(safe)

    sections_ok = all(
        len(tuple(safe.get(section) or ())) >= 1
        for section in (
            "assessment_summary_section",
            "assessment_findings_section",
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
        and record_lanes_ok
        and assessment_ok
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
        "record_lanes_ok": record_lanes_ok,
        "assessment_ok": assessment_ok,
        "no_trade_language": no_trade_language,
        "sections_ok": sections_ok,
        "operator_next_step_ok": operator_next_step_ok,
    }


def validate_crypto_d1_external_human_trader_evidence_contract(
    contract: Any,
) -> dict[str, Any]:
    """Public validation entry point; returns the deterministic verdict dict."""
    return _validate(contract)


def render_crypto_d1_external_human_trader_evidence_contract_markdown(
    contract: Any,
) -> str:
    """Render an informational, read-only markdown summary of the contract.
    Pure; builds and returns a string, writes nothing."""
    safe = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 External Human Trader Evidence Contract")
    lines.append("")
    lines.append("- Label: " + _as_text(safe.get("label")))
    lines.append("- Mode: " + _as_text(safe.get("mode")))
    lines.append("- Status: " + _as_text(safe.get("status")))
    lines.append("- Outcome: " + _as_text(safe.get("outcome")))
    lines.append("- Records assessed: " + str(safe.get("record_count")))
    lines.append("- Research notes: " + str(safe.get("research_note_count")))
    lines.append(
        "- Risky-unverified: " + str(safe.get("risky_unverified_count"))
    )
    lines.append("- Hype-discard: " + str(safe.get("hype_discard_count")))
    lines.append(
        "- Usable observations: " + str(safe.get("usable_observation_count"))
    )
    lines.append("- Read-only: " + str(safe.get("read_only")))
    lines.append("- Executes: " + str(safe.get("executes")))
    lines.append("- Counts as proof: " + str(safe.get("counts_as_proof")))
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

    _emit("Assessment Summary", "assessment_summary_section")
    _emit("Assessment Findings", "assessment_findings_section")
    _emit("Lanes", "lane_summaries")
    _emit("Penalties", "penalty_findings")
    _emit("Observation-Only Evidence Lanes", "observation_only_section")
    _emit("No Execution Authorization", "no_execution_authorization_section")
    lines.append("")
    lines.append("## Operator Next Step")
    lines.append("- " + _as_text(safe.get("operator_next_step")))
    return "\n".join(lines)

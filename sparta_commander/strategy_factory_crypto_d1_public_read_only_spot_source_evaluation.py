"""Crypto-D1 Public Read-Only Spot Source Evaluation Contract (Block 167).

A PURE, stdlib-only, *read-only* paper contract. It answers exactly one
research-only question, on paper: does a caller-supplied STATIC description of a
candidate PUBLIC read-only spot data source look sound enough to put in front of
a human for a source review? It NEVER calls an endpoint, NEVER fetches a URL,
NEVER implements a provider, and NEVER crosses the Real Data QA boundary. It only
reasons over a static, caller-supplied source description and returns one verdict:

    READY_FOR_HUMAN_SOURCE_REVIEW  - every evaluation item passes and no unsafe
                                      flag is set, so a human MAY now review the
                                      described source as a candidate.
    HOLD_NEEDS_MORE_PREP           - one or more required items are missing, or an
                                      unsafe flag / live-endpoint claim /
                                      credential need / order-trade-account field /
                                      boundary-crossing requirement is present; do
                                      NOT put the source in front of a human yet.

    CURRENT_STAGE        = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    NEXT_REQUIRED_ACTION = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

CORE RULE: evaluating a described source authorizes nothing and runs nothing. A
READY_FOR_HUMAN_SOURCE_REVIEW verdict only means "the paper description is sound
enough for a human to review the source"; choosing, onboarding, or fetching from
any real source is a separate, future, explicitly human-approved act OUTSIDE this
contract. real_data_qa stays BLOCKED, baseline stays BLOCKED, and the paper /
micro-live gates stay LOCKED here, always.

It executes NOTHING. It does not call a provider, fetch a URL, open a network,
import a CSV, read or parse any file, write any file, read or inspect any
credential, read a .env, print / store / log any secret, run QA / baseline /
backtest / simulation, touch any broker / exchange / order / account / portfolio
endpoint, trigger automation, mint an id, or record a timestamp. It only reasons
over a static, caller-supplied source description.

The ten evaluation items, aligned with the Block 151 read-only spot provider
adapter rules:
  1.  source_is_public                  - source is described as publicly
                                          accessible (no private / gated access)
  2.  read_only_access                  - read-only historical data access only;
                                          no trading / account / order endpoint
  3.  no_credentials_required           - no API key / credential / secret needed
                                          to read the public data
  4.  spot_instrument_only              - spot instrument data only; no futures /
                                          perps / leverage / positions
  5.  daily_timeframe_supported         - supports the daily (D1) bars Crypto-D1
                                          needs
  6.  approved_symbol_coverage          - covers at least one approved Crypto-D1
                                          symbol
  7.  ohlcv_fields_described            - the described row schema includes the
                                          required OHLCV fields
  8.  clear_source_license              - source / license is clearly described
                                          (no unclear-source rejection)
  9.  no_live_call_required_to_evaluate - evaluating it now requires no live
                                          endpoint call / fetch
  10. matches_block151_adapter_rules    - overall the description fits the Block
                                          151 read-only spot adapter contract, and
                                          mission flow is still at the boundary

If any required item is missing, the verdict is HOLD_NEEDS_MORE_PREP, with the
failing item ids and human reasons attached. If an unsafe flag is set -- an
authorization, gate-unlock, promotion, live-endpoint, credential-need,
order/trade/account/balance/position field, or boundary-crossing requirement --
the contract records a safety violation and the verdict is still
HOLD_NEEDS_MORE_PREP (never READY): an unsafe payload can never be ready.

Public API:
  - SOURCE_EVALUATION_SCHEMA_VERSION / _LABEL / _STATUS / _MODE
  - SOURCE_EVALUATION_CORE_RULE
  - SOURCE_EVALUATION_NEXT_REQUIRED_ACTION / _CURRENT_STAGE
  - SOURCE_EVALUATION_MISSION_FLOW_CURRENT_STAGE
  - SOURCE_EVALUATION_MISSION_FLOW_NEXT_REQUIRED_ACTION
  - SOURCE_EVALUATION_ITEMS / _ITEM_IDS
  - OUTCOME_READY / OUTCOME_HOLD / SOURCE_EVALUATION_OUTCOMES
  - SOURCE_EVALUATION_AUTHORIZATION_FLAGS / _GATE_LOCK_FLAGS
  - SOURCE_EVALUATION_GATE_UNLOCK_REQUEST_FLAGS
  - SOURCE_EVALUATION_FORBIDDEN_PROMOTION_REQUEST_FLAGS
  - SOURCE_EVALUATION_LIVE_ENDPOINT_FLAGS / _CREDENTIAL_NEED_FLAGS
  - SOURCE_EVALUATION_ACCOUNT_TRADE_FIELDS
  - SOURCE_EVALUATION_FORBIDDEN_TRADE_TERMS
  - SOURCE_EVALUATION_SAFETY_POSTURE
  - DEFAULT_SAMPLE_SOURCE_EVALUATION_INPUT
  - assess_public_read_only_spot_source_evaluation(payload)
  - build_crypto_d1_public_read_only_spot_source_evaluation(payload=None)
  - validate_crypto_d1_public_read_only_spot_source_evaluation(contract)
  - render_crypto_d1_public_read_only_spot_source_evaluation_markdown(contract)
"""

from __future__ import annotations

from typing import Any

SOURCE_EVALUATION_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_public_read_only_spot_source_evaluation.v1"
)
SOURCE_EVALUATION_LABEL = (
    "Block 167 - Crypto-D1 Public Read-Only Spot Source Evaluation Contract"
)
SOURCE_EVALUATION_STATUS = (
    "READ_ONLY_CRYPTO_D1_PUBLIC_SPOT_SOURCE_EVALUATION"
)
SOURCE_EVALUATION_MODE = "RESEARCH_ONLY"

SOURCE_EVALUATION_CORE_RULE = (
    "Evaluating a described public read-only spot source authorizes nothing and "
    "runs nothing. A READY_FOR_HUMAN_SOURCE_REVIEW verdict only means the paper "
    "description is sound enough for a human to review the source; choosing, "
    "onboarding, or fetching from any real source is a separate, future, "
    "explicitly human-approved act OUTSIDE this contract. No provider is called, "
    "no URL is fetched, no network is opened, no credential is read. real_data_qa "
    "stays BLOCKED, baseline stays BLOCKED, and the paper / micro-live gates stay "
    "LOCKED here, always."
)

# The action that BUILDING this contract satisfies, and the stage it occupies.
SOURCE_EVALUATION_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_PUBLIC_READ_ONLY_SPOT_SOURCE_EVALUATION"
)
SOURCE_EVALUATION_CURRENT_STAGE = (
    "CRYPTO_D1_PUBLIC_READ_ONLY_SPOT_SOURCE_EVALUATION_REQUIRED"
)

# The current mission-flow truth this contract is anchored to. The companion test
# cross-checks these against the live status module so they cannot silently drift.
SOURCE_EVALUATION_MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
SOURCE_EVALUATION_MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# The ten evaluation items (id, human label), in display order. READY requires
# all of them to pass.
SOURCE_EVALUATION_ITEMS: tuple[tuple[str, str], ...] = (
    (
        "source_is_public",
        "Source is described as publicly accessible (no private / gated access)",
    ),
    (
        "read_only_access",
        "Read-only historical data access only; no trading / account / order "
        "endpoint",
    ),
    (
        "no_credentials_required",
        "No API key / credential / secret needed to read the public data",
    ),
    (
        "spot_instrument_only",
        "Spot instrument data only; no futures / perps / leverage / positions",
    ),
    (
        "daily_timeframe_supported",
        "Supports the daily (D1) bars Crypto-D1 needs",
    ),
    (
        "approved_symbol_coverage",
        "Covers at least one approved Crypto-D1 symbol",
    ),
    (
        "ohlcv_fields_described",
        "Described row schema includes the required OHLCV fields",
    ),
    (
        "clear_source_license",
        "Source / license is clearly described (no unclear-source rejection)",
    ),
    (
        "no_live_call_required_to_evaluate",
        "Evaluating it now requires no live endpoint call / fetch",
    ),
    (
        "matches_block151_adapter_rules",
        "Overall the description fits the Block 151 read-only spot adapter "
        "contract, and mission flow is still at the boundary",
    ),
)
SOURCE_EVALUATION_ITEM_IDS: tuple[str, ...] = tuple(
    item_id for item_id, _label in SOURCE_EVALUATION_ITEMS
)

# Contract outcomes (exactly one assigned).
OUTCOME_READY = "READY_FOR_HUMAN_SOURCE_REVIEW"
OUTCOME_HOLD = "HOLD_NEEDS_MORE_PREP"

SOURCE_EVALUATION_OUTCOMES: tuple[str, ...] = (
    OUTCOME_READY,
    OUTCOME_HOLD,
)

# Top-level authorization flags that, if truthy, are an unsafe request -> safety
# violation -> HOLD.
SOURCE_EVALUATION_AUTHORIZATION_FLAGS: tuple[str, ...] = (
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
# the payload tried to unlock a gate -> safety violation -> HOLD.
SOURCE_EVALUATION_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, are an unsafe request.
SOURCE_EVALUATION_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "allow_real_data_qa",
    "allow_baseline_backtest",
    "allow_paper_trading",
    "allow_live_trading",
)

# Requests asking the contract to MEAN execution / live promotion / a boundary
# crossing. Any truthy value is an unsafe request.
SOURCE_EVALUATION_FORBIDDEN_PROMOTION_REQUEST_FLAGS: tuple[str, ...] = (
    "force_promote",
    "promote_to_live",
    "promote_to_paper",
    "approve_trade",
    "authorize_trade",
    "execute",
    "place_order",
    "go_live",
    "cross_boundary",
    "cross_real_data_qa_boundary",
    "auto_approve_source",
    "auto_push",
)

# Flags whose truthy value means the described source would require a live
# endpoint call / fetch / network access now -> unsafe (this contract only ever
# reasons over a static description).
SOURCE_EVALUATION_LIVE_ENDPOINT_FLAGS: tuple[str, ...] = (
    "performs_live_fetch",
    "calls_endpoint_now",
    "requires_live_endpoint_call",
    "opens_network",
    "fetches_url",
    "live_endpoint",
)

# Flags whose truthy value means the described source would require a credential /
# secret / account auth to read -> not a public read-only source -> unsafe.
SOURCE_EVALUATION_CREDENTIAL_NEED_FLAGS: tuple[str, ...] = (
    "requires_credentials",
    "requires_api_key",
    "requires_secret",
    "requires_account_auth",
    "requires_login",
)

# Fields whose presence (non-empty) on the payload signals account / trading /
# order data rather than a static public-source description -> safety violation.
SOURCE_EVALUATION_ACCOUNT_TRADE_FIELDS: tuple[str, ...] = (
    "order",
    "trade",
    "account",
    "balance",
    "position",
    "portfolio",
    "signal",
    "execution",
)

# Execution / promotion verbs the contract's own generated guidance must never
# contain as whole words.
SOURCE_EVALUATION_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
    "order",
)

# Read-only safety posture. The True flags are *posture* facts; every capability /
# authorization / unlock flag is False.
SOURCE_EVALUATION_SAFETY_POSTURE: dict[str, bool] = {
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
    "calls_endpoint": False,
    "fetches_url": False,
    "opens_network": False,
    "reads_credential": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}


# A deterministic, illustrative paper sample describing a sound public read-only
# spot source: every required item is asserted, every gate is locked, and no
# unsafe flag is set, so the default evaluation is READY_FOR_HUMAN_SOURCE_REVIEW.
# Nothing here is real data and no real source is named; static example only.
DEFAULT_SAMPLE_SOURCE_EVALUATION_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 public read-only spot source description (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "research_only": True,
    "mission_flow_current_stage": (
        "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
    ),
    "mission_flow_next_required_action": (
        "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
    ),
    "source_is_public": True,
    "read_only_access": True,
    "no_credentials_required": True,
    "spot_instrument_only": True,
    "daily_timeframe_supported": True,
    "approved_symbol_coverage": True,
    "ohlcv_fields_described": True,
    "clear_source_license": True,
    "no_live_call_required_to_evaluate": True,
    "matches_block151_adapter_rules": True,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
}


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _is_truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _as_payload(payload: Any) -> dict[str, Any]:
    return dict(payload) if isinstance(payload, dict) else {}


def _tokenize(text: str) -> list[str]:
    token: list[str] = []
    out: list[str] = []
    for ch in str(text).lower():
        if ch.isalnum() or ch == "_":
            token.append(ch)
        else:
            if token:
                out.append("".join(token))
                token = []
    if token:
        out.append("".join(token))
    return out


def _unsafe_flag_hits(payload: dict[str, Any]) -> list[str]:
    """Collect any payload keys that attempt to authorize, unlock, promote, claim
    a live endpoint, need a credential, or carry an account / trade instruction.
    Pure; reads only the static payload."""
    hits: list[str] = []
    for flag in SOURCE_EVALUATION_AUTHORIZATION_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in SOURCE_EVALUATION_GATE_UNLOCK_REQUEST_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in SOURCE_EVALUATION_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in SOURCE_EVALUATION_LIVE_ENDPOINT_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in SOURCE_EVALUATION_CREDENTIAL_NEED_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for field in SOURCE_EVALUATION_ACCOUNT_TRADE_FIELDS:
        value = payload.get(field)
        if value not in (None, "", [], {}, 0, False):
            hits.append(field)
    for flag in SOURCE_EVALUATION_GATE_LOCK_FLAGS:
        if flag in payload and not _is_truthy(payload.get(flag)):
            hits.append("unlocked:" + flag)
    seen: set[str] = set()
    ordered: list[str] = []
    for h in hits:
        if h not in seen:
            seen.add(h)
            ordered.append(h)
    return ordered


def _gates_all_locked(payload: dict[str, Any]) -> bool:
    """True only when every gate-lock flag is present AND True."""
    return all(
        _is_truthy(payload.get(flag))
        for flag in SOURCE_EVALUATION_GATE_LOCK_FLAGS
    )


# --------------------------------------------------------------------------- #
# assessment
# --------------------------------------------------------------------------- #
def assess_public_read_only_spot_source_evaluation(
    payload: Any,
) -> dict[str, Any]:
    """Assess (read-only) a described public read-only spot source. Returns a
    fresh dict every call. Authorizes nothing and unlocks nothing under any
    outcome -- a READY_FOR_HUMAN_SOURCE_REVIEW result only means the paper
    description is sound enough for a human to review the source."""
    data = _as_payload(payload)

    mf_stage = data.get(
        "mission_flow_current_stage",
        SOURCE_EVALUATION_MISSION_FLOW_CURRENT_STAGE,
    )
    mf_action = data.get(
        "mission_flow_next_required_action",
        SOURCE_EVALUATION_MISSION_FLOW_NEXT_REQUIRED_ACTION,
    )
    mission_flow_aligned = (
        str(mf_stage) == SOURCE_EVALUATION_MISSION_FLOW_CURRENT_STAGE
        and str(mf_action)
        == SOURCE_EVALUATION_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    unsafe_hits = _unsafe_flag_hits(data)
    gates_locked = _gates_all_locked(data)

    # Each item passes only when the caller's static description asserts it AND no
    # unsafe flag undermines it. The two derived items below additionally require
    # that no unsafe flag is set / mission flow is still at the boundary.
    item_results: dict[str, bool] = {
        "source_is_public": _is_truthy(data.get("source_is_public")),
        "read_only_access": _is_truthy(data.get("read_only_access")),
        "no_credentials_required": _is_truthy(
            data.get("no_credentials_required")
        ),
        "spot_instrument_only": _is_truthy(data.get("spot_instrument_only")),
        "daily_timeframe_supported": _is_truthy(
            data.get("daily_timeframe_supported")
        ),
        "approved_symbol_coverage": _is_truthy(
            data.get("approved_symbol_coverage")
        ),
        "ohlcv_fields_described": _is_truthy(
            data.get("ohlcv_fields_described")
        ),
        "clear_source_license": _is_truthy(data.get("clear_source_license")),
        "no_live_call_required_to_evaluate": _is_truthy(
            data.get("no_live_call_required_to_evaluate")
        )
        and len(unsafe_hits) == 0,
        "matches_block151_adapter_rules": _is_truthy(
            data.get("matches_block151_adapter_rules")
        )
        and mission_flow_aligned,
    }

    _reasons = {
        "source_is_public": (
            "source is described as publicly accessible"
            if item_results["source_is_public"]
            else "source is NOT confirmed publicly accessible"
        ),
        "read_only_access": (
            "read-only historical data access only; no trading / account / order "
            "endpoint"
            if item_results["read_only_access"]
            else "read-only access is NOT confirmed"
        ),
        "no_credentials_required": (
            "no API key / credential / secret needed to read the public data"
            if item_results["no_credentials_required"]
            else "a credential / API key / secret appears to be required"
        ),
        "spot_instrument_only": (
            "spot instrument data only; no futures / perps / leverage"
            if item_results["spot_instrument_only"]
            else "spot-only instrument coverage is NOT confirmed"
        ),
        "daily_timeframe_supported": (
            "supports the daily (D1) bars Crypto-D1 needs"
            if item_results["daily_timeframe_supported"]
            else "daily (D1) timeframe support is NOT confirmed"
        ),
        "approved_symbol_coverage": (
            "covers at least one approved Crypto-D1 symbol"
            if item_results["approved_symbol_coverage"]
            else "approved-symbol coverage is NOT confirmed"
        ),
        "ohlcv_fields_described": (
            "described row schema includes the required OHLCV fields"
            if item_results["ohlcv_fields_described"]
            else "required OHLCV fields are NOT confirmed in the description"
        ),
        "clear_source_license": (
            "source / license is clearly described"
            if item_results["clear_source_license"]
            else "source / license is unclear (rejection rule)"
        ),
        "no_live_call_required_to_evaluate": (
            "evaluating it now requires no live endpoint call / fetch"
            if item_results["no_live_call_required_to_evaluate"]
            else "a live endpoint call / fetch or unsafe flag was detected"
        ),
        "matches_block151_adapter_rules": (
            "the description fits the Block 151 read-only spot adapter contract, "
            "and mission flow is still at the boundary"
            if item_results["matches_block151_adapter_rules"]
            else "the description does NOT fit the Block 151 adapter rules, or "
            "mission flow has left the boundary"
        ),
    }

    evaluation_items = [
        {
            "id": item_id,
            "label": label,
            "passed": item_results[item_id],
            "reason": _reasons[item_id],
        }
        for item_id, label in SOURCE_EVALUATION_ITEMS
    ]

    failed_items = [c["id"] for c in evaluation_items if not c["passed"]]
    safety_violation = len(unsafe_hits) > 0

    if safety_violation or failed_items:
        outcome = OUTCOME_HOLD
    else:
        outcome = OUTCOME_READY

    return {
        "mode": SOURCE_EVALUATION_MODE,
        "outcome": outcome,
        "mission_flow_current_stage": str(mf_stage),
        "mission_flow_next_required_action": str(mf_action),
        "mission_flow_aligned": mission_flow_aligned,
        "evaluation_items": evaluation_items,
        "evaluation_item_ids": list(SOURCE_EVALUATION_ITEM_IDS),
        "passed_item_ids": [c["id"] for c in evaluation_items if c["passed"]],
        "failed_item_ids": list(failed_items),
        "unsafe_flag_hits": list(unsafe_hits),
        "safety_violation": safety_violation,
        "gates_blocked_locked": gates_locked,
        "ready": outcome == OUTCOME_READY,
        "ready_for_human_source_review": outcome == OUTCOME_READY,
        "evaluates_research_only": True,
        "calls_endpoint": False,
        "fetches_url": False,
        "unlocks_real_data_qa": False,
        "crosses_boundary": False,
        "authorizes_nothing": True,
    }


# --------------------------------------------------------------------------- #
# contract build
# --------------------------------------------------------------------------- #
def _operator_next_step(assessment: dict[str, Any]) -> str:
    if assessment["outcome"] == OUTCOME_READY:
        return (
            "Ready to put the described source in front of a human for source "
            "review. Readiness is not selection: a human must still review the "
            "described source and separately decide whether to ever onboard it. "
            "This contract calls nothing and fetches nothing; real_data_qa "
            "remains BLOCKED until a separate, future, explicitly human-approved "
            "step provides authorization."
        )
    if assessment["safety_violation"]:
        return (
            "Hold. An unsafe flag was set (authorization / gate-unlock / "
            "promotion / live-endpoint / credential-need / account-trade field / "
            "boundary-crossing). Do NOT put the source in front of a human yet. "
            "Rebuild the source description as a static, research-only, public, "
            "read-only summary; call nothing and fetch nothing. real_data_qa "
            "remains BLOCKED."
        )
    return (
        "Hold. One or more required evaluation items are missing -- resolve every "
        "failing item before putting the described source in front of a human. "
        "Nothing is called, fetched, or run; real_data_qa remains BLOCKED."
    )


def build_crypto_d1_public_read_only_spot_source_evaluation(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only Public Read-Only Spot Source
    Evaluation contract record. All capability flags are False and all gate locks
    are True regardless of the assessed outcome."""
    data = (
        dict(DEFAULT_SAMPLE_SOURCE_EVALUATION_INPUT)
        if payload is None
        else _as_payload(payload)
    )
    assessment = assess_public_read_only_spot_source_evaluation(data)

    contract: dict[str, Any] = {
        "schema_version": SOURCE_EVALUATION_SCHEMA_VERSION,
        "label": SOURCE_EVALUATION_LABEL,
        "status": SOURCE_EVALUATION_STATUS,
        "stage": SOURCE_EVALUATION_CURRENT_STAGE,
        "mode": SOURCE_EVALUATION_MODE,
        "core_rule": SOURCE_EVALUATION_CORE_RULE,
        "contract_next_required_action": (
            SOURCE_EVALUATION_NEXT_REQUIRED_ACTION
        ),
        "contract_current_stage": SOURCE_EVALUATION_CURRENT_STAGE,
        "mission_flow_current_stage": (
            SOURCE_EVALUATION_MISSION_FLOW_CURRENT_STAGE
        ),
        "mission_flow_next_required_action": (
            SOURCE_EVALUATION_MISSION_FLOW_NEXT_REQUIRED_ACTION
        ),
        "mission_flow_aligned": assessment["mission_flow_aligned"],
        "outcomes": list(SOURCE_EVALUATION_OUTCOMES),
        "outcome": assessment["outcome"],
        "ready": assessment["ready"],
        "ready_for_human_source_review": (
            assessment["ready_for_human_source_review"]
        ),
        "safety_violation": assessment["safety_violation"],
        "evaluation_item_ids": list(SOURCE_EVALUATION_ITEM_IDS),
        "evaluation_items": assessment["evaluation_items"],
        "passed_item_ids": list(assessment["passed_item_ids"]),
        "failed_item_ids": list(assessment["failed_item_ids"]),
        "unsafe_flag_hits": list(assessment["unsafe_flag_hits"]),
        "authorization_flags": list(SOURCE_EVALUATION_AUTHORIZATION_FLAGS),
        "gate_lock_flags": list(SOURCE_EVALUATION_GATE_LOCK_FLAGS),
        "gate_unlock_request_flags": list(
            SOURCE_EVALUATION_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_promotion_request_flags": list(
            SOURCE_EVALUATION_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ),
        "live_endpoint_flags": list(SOURCE_EVALUATION_LIVE_ENDPOINT_FLAGS),
        "credential_need_flags": list(SOURCE_EVALUATION_CREDENTIAL_NEED_FLAGS),
        "account_trade_fields": list(SOURCE_EVALUATION_ACCOUNT_TRADE_FIELDS),
        "forbidden_trade_terms": list(SOURCE_EVALUATION_FORBIDDEN_TRADE_TERMS),
        "assessment": assessment,
        "operator_next_step": _operator_next_step(assessment),
        "operator_notes": (
            "Read-only public spot source evaluation. It confirms the ten "
            "evaluation items; it never selects, never onboards, never fetches, "
            "and never crosses the boundary. Even a READY_FOR_HUMAN_SOURCE_REVIEW "
            "result authorizes nothing."
        ),
        "human_operator_required_next_steps": [
            "A human confirms the ten evaluation items passed.",
            "A human reviewer separately decides whether to ever onboard the "
            "described source as a candidate.",
            "A separate, future, explicitly human-approved step is required "
            "before any real source is selected or read.",
        ],
        "safety_posture": dict(SOURCE_EVALUATION_SAFETY_POSTURE),
        "requires_independent_confirmation": True,
        "requires_separate_future_human_approved_step": True,
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
        "authorizes_nothing": True,
        "calls_endpoint": False,
        "fetches_url": False,
        "opens_network": False,
        "reads_credential": False,
        "unlocks_downstream_gate": False,
        "unlocks_real_data_qa": False,
        "unlocks_baseline_backtest": False,
        "unlocks_paper_trading": False,
        "unlocks_micro_live": False,
        "crosses_boundary": False,
        "promotes_beyond_boundary": False,
        "real_data_qa_blocked": True,
        "baseline_backtest_blocked": True,
        "paper_trading_gate_locked": True,
        "micro_live_gate_locked": True,
    }
    return contract


# --------------------------------------------------------------------------- #
# validation
# --------------------------------------------------------------------------- #
_REQUIRED_CONTRACT_FIELDS: tuple[str, ...] = (
    "schema_version",
    "label",
    "status",
    "stage",
    "mode",
    "core_rule",
    "mission_flow_current_stage",
    "mission_flow_next_required_action",
    "outcome",
    "outcomes",
    "assessment",
    "evaluation_items",
    "operator_next_step",
    "safety_posture",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_data_fetch",
    "authorizes_backtest",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_automation",
    "authorizes_real_world_action",
    "calls_endpoint",
    "fetches_url",
    "opens_network",
    "reads_credential",
    "unlocks_downstream_gate",
    "unlocks_real_data_qa",
    "unlocks_baseline_backtest",
    "unlocks_paper_trading",
    "unlocks_micro_live",
    "crosses_boundary",
    "promotes_beyond_boundary",
)

_ALL_GATE_LOCKS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def validate_crypto_d1_public_read_only_spot_source_evaluation(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built contract. Returns a verdict dict of boolean
    checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == SOURCE_EVALUATION_SCHEMA_VERSION
    label_ok = c.get("label") == SOURCE_EVALUATION_LABEL
    mode_ok = c.get("mode") == SOURCE_EVALUATION_MODE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    human_required = c.get("human_approval_required") is True
    confirmation_required = c.get("requires_independent_confirmation") is True
    future_step_required = (
        c.get("requires_separate_future_human_approved_step") is True
    )
    stage_ok = c.get("stage") == SOURCE_EVALUATION_CURRENT_STAGE
    core_rule_ok = c.get("core_rule") == SOURCE_EVALUATION_CORE_RULE
    outcome_ok = c.get("outcome") in SOURCE_EVALUATION_OUTCOMES
    outcomes_ok = (
        tuple(c.get("outcomes") or ()) == SOURCE_EVALUATION_OUTCOMES
    )
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage")
        == SOURCE_EVALUATION_MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == SOURCE_EVALUATION_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == SOURCE_EVALUATION_SAFETY_POSTURE

    items = c.get("evaluation_items")
    ten_evaluation_items = (
        isinstance(items, list)
        and len(items) == 10
        and [item.get("id") for item in items]
        == list(SOURCE_EVALUATION_ITEM_IDS)
    )

    # READY may only appear when every evaluation item passed AND no safety
    # violation was recorded.
    ready_value = c.get("ready") is True
    all_items_passed = isinstance(items, list) and all(
        bool(item.get("passed")) for item in items
    )
    no_safety_violation = c.get("safety_violation") is False
    ready_only_when_all_pass = (not ready_value) or (
        all_items_passed and no_safety_violation
    )

    # the contract must never directly unlock real data QA or cross the boundary
    real_data_qa_stays_blocked = (
        c.get("unlocks_real_data_qa") is False
        and c.get("real_data_qa_blocked") is True
        and c.get("crosses_boundary") is False
    )

    # generated guidance must carry no execution / trade verbs as whole words
    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "operator_notes", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (
        tokens & set(SOURCE_EVALUATION_FORBIDDEN_TRADE_TERMS)
    )

    sections_ok = isinstance(c.get("operator_next_step"), str) and bool(
        c.get("operator_next_step")
    )

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "mode_ok": mode_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "human_required": human_required,
        "confirmation_required": confirmation_required,
        "future_step_required": future_step_required,
        "stage_ok": stage_ok,
        "core_rule_ok": core_rule_ok,
        "outcome_ok": outcome_ok,
        "outcomes_ok": outcomes_ok,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "ten_evaluation_items": ten_evaluation_items,
        "ready_only_when_all_pass": ready_only_when_all_pass,
        "real_data_qa_stays_blocked": real_data_qa_stays_blocked,
        "no_trade_language": no_trade_language,
        "sections_ok": sections_ok,
    }
    verdict = dict(checks)
    verdict["missing_fields"] = missing
    verdict["valid"] = (not missing) and all(checks.values())
    return verdict


# --------------------------------------------------------------------------- #
# render
# --------------------------------------------------------------------------- #
def _emit(lines: list[str], heading: str, rows: list[str]) -> None:
    lines.append("")
    lines.append("## " + heading)
    if not rows:
        lines.append("- (none)")
        return
    for row in rows:
        lines.append("- " + row)


def render_crypto_d1_public_read_only_spot_source_evaluation_markdown(
    contract: Any,
) -> str:
    """Render a built contract as a deterministic markdown brief. Pure string
    formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Public Read-Only Spot Source Evaluation")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Outcome: " + str(c.get("outcome", "")))
    lines.append("- Ready: " + str(c.get("ready", False)))
    lines.append("- Safety violation: " + str(c.get("safety_violation", False)))
    lines.append(
        "- Mission flow stage: " + str(c.get("mission_flow_current_stage", ""))
    )
    lines.append(
        "- Calls endpoint: " + str(c.get("calls_endpoint", False))
    )
    lines.append("- Fetches url: " + str(c.get("fetches_url", False)))
    lines.append(
        "- Unlocks real_data_qa: " + str(c.get("unlocks_real_data_qa", False))
    )
    lines.append("- Crosses boundary: " + str(c.get("crosses_boundary", False)))
    lines.append(
        "- real_data_qa_blocked: " + str(c.get("real_data_qa_blocked", True))
    )

    _emit(
        lines,
        "Source Evaluation",
        [
            str(item.get("id"))
            + ": "
            + ("PASS" if item.get("passed") else "FAIL")
            + " - "
            + str(item.get("reason"))
            for item in (c.get("evaluation_items") or [])
        ],
    )
    _emit(lines, "Failed Items", list(c.get("failed_item_ids") or []))
    _emit(lines, "Unsafe Flag Hits", list(c.get("unsafe_flag_hits") or []))
    _emit(
        lines,
        "No Execution Authorization",
        [
            "authorizes_nothing: " + str(c.get("authorizes_nothing", True)),
            "calls_endpoint: " + str(c.get("calls_endpoint", False)),
            "fetches_url: " + str(c.get("fetches_url", False)),
            "unlocks_real_data_qa: "
            + str(c.get("unlocks_real_data_qa", False)),
            "crosses_boundary: " + str(c.get("crosses_boundary", False)),
            "requires_separate_future_human_approved_step: "
            + str(c.get("requires_separate_future_human_approved_step", True)),
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)

"""Crypto-D1 Selected Read-Only Spot Provider Fetch Runner Dry Run (Block 169).

A PURE, stdlib-only, *read-only* paper dry-run contract. It answers exactly one
research-only question, on paper: does a caller-supplied STATIC description of a
dry run of the selected read-only spot provider fetch runner -- exercised ONLY
against an in-memory FAKE provider -- look complete and safe enough, and aligned
with the Block 151 read-only spot provider adapter rules, to put in front of a
human for a dry-run review? It NEVER injects a real provider, NEVER calls an
endpoint, NEVER fetches a URL, NEVER reads a credential, NEVER acquires real
data, and NEVER crosses the Real Data QA boundary. It only reasons over a static,
caller-supplied dry-run description and returns one verdict:

    READY_FOR_HUMAN_DRY_RUN_REVIEW - every dry-run item passes and no unsafe flag
                                     is set, so a human MAY now review the
                                     described fake-provider dry run as a
                                     candidate runner exercise.
    HOLD_NEEDS_MORE_PREP           - one or more required items are missing, or an
                                     unsafe flag / real-provider injection /
                                     live-endpoint / credential need /
                                     order-trade-account field / boundary-crossing
                                     requirement is present; do NOT put the dry run
                                     in front of a human yet.

    CURRENT_STAGE        = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    NEXT_REQUIRED_ACTION = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

CORE RULE: describing a fake-provider dry run on paper authorizes nothing and runs
nothing. A READY_FOR_HUMAN_DRY_RUN_REVIEW verdict only means "the paper dry run is
sound enough for a human to review the exercise"; running, wiring, or fetching with
any real provider is a separate, future, explicitly human-approved act OUTSIDE this
contract. real_data_qa stays BLOCKED, baseline stays BLOCKED, and the paper /
micro-live gates stay LOCKED here, always.

It executes NOTHING. It does not inject a real provider, call a provider, fetch a
URL, open a network, import a CSV, read or parse any file, write any file, read or
inspect any credential, read a .env, print / store / log any secret, run QA /
baseline / backtest / simulation, touch any broker / exchange / order / account /
portfolio endpoint, trigger automation, mint an id, or record a timestamp. It only
reasons over a static, caller-supplied dry-run description.

The ten dry-run items, aligned with the Block 151 read-only spot provider adapter
rules (required method `fetch_read_only_daily_spot_ohlcv`; required return fields
date/open/high/low/close/volume/source/instrument_type; instrument_type "spot";
rejection of futures/perps, account-auth APIs, and unclear source/license):
  1.  uses_fake_provider_only        - the dry run uses only an in-memory FAKE
                                       provider; no real provider is injected
  2.  read_only_fetch_call_only      - the runner invokes only the read-only fetch
                                       method; no trading / account / order call
  3.  returns_required_ohlcv_fields  - the fake provider rows include the required
                                       OHLCV + source + instrument_type fields
  4.  spot_instrument_type_only      - fake rows declare instrument_type "spot"
                                       only; no futures / perps / leverage
  5.  daily_timeframe_only           - fake rows are daily (D1) bars only; matches
                                       Crypto-D1
  6.  no_credentials_in_dry_run      - the dry run needs no API key / credential /
                                       secret
  7.  deterministic_dry_run_result   - the dry run yields a deterministic in-memory
                                       result; no order / trade side effect
  8.  no_real_data_persisted         - the dry run persists / writes no real data;
                                       in-memory only
  9.  no_network_in_dry_run          - the dry run opens no network, fetches no URL,
                                       and calls no endpoint
  10. matches_block151_adapter_contract - overall the dry run exercises the Block
                                       151 read-only spot adapter contract, and
                                       mission flow is still at the boundary

If any required item is missing, the verdict is HOLD_NEEDS_MORE_PREP, with the
failing item ids and human reasons attached. If an unsafe flag is set -- an
authorization, gate-unlock, promotion, real-provider injection, live-endpoint,
credential-need, order/trade/account/balance/position field, or boundary-crossing
requirement -- the contract records a safety violation and the verdict is still
HOLD_NEEDS_MORE_PREP (never READY): an unsafe payload can never be ready.

Public API:
  - DRY_RUN_SCHEMA_VERSION / _LABEL / _STATUS / _MODE
  - DRY_RUN_CORE_RULE
  - DRY_RUN_NEXT_REQUIRED_ACTION / _CURRENT_STAGE
  - DRY_RUN_MISSION_FLOW_CURRENT_STAGE
  - DRY_RUN_MISSION_FLOW_NEXT_REQUIRED_ACTION
  - DRY_RUN_ITEMS / _ITEM_IDS
  - OUTCOME_READY / OUTCOME_HOLD / DRY_RUN_OUTCOMES
  - DRY_RUN_AUTHORIZATION_FLAGS / _GATE_LOCK_FLAGS
  - DRY_RUN_GATE_UNLOCK_REQUEST_FLAGS
  - DRY_RUN_FORBIDDEN_PROMOTION_REQUEST_FLAGS
  - DRY_RUN_REAL_PROVIDER_FLAGS
  - DRY_RUN_LIVE_ENDPOINT_FLAGS / _CREDENTIAL_NEED_FLAGS
  - DRY_RUN_ACCOUNT_TRADE_FIELDS
  - DRY_RUN_FORBIDDEN_TRADE_TERMS
  - DRY_RUN_SAFETY_POSTURE
  - DEFAULT_SAMPLE_DRY_RUN_INPUT
  - assess_selected_read_only_spot_provider_fetch_runner_dry_run(payload)
  - build_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run(payload=None)
  - validate_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run(contract)
  - render_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run_markdown(contract)
"""

from __future__ import annotations

from typing import Any

DRY_RUN_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run.v1"
)
DRY_RUN_LABEL = (
    "Block 169 - Crypto-D1 Selected Read-Only Spot Provider Fetch Runner Dry Run"
)
DRY_RUN_STATUS = (
    "READ_ONLY_CRYPTO_D1_SELECTED_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN"
)
DRY_RUN_MODE = "RESEARCH_ONLY"

DRY_RUN_CORE_RULE = (
    "Describing a fake-provider dry run of the selected read-only spot provider "
    "fetch runner on paper authorizes nothing and runs nothing. A "
    "READY_FOR_HUMAN_DRY_RUN_REVIEW verdict only means the paper dry run is sound "
    "enough for a human to review the exercise; running, wiring, or fetching with "
    "any real provider is a separate, future, explicitly human-approved act OUTSIDE "
    "this contract. No real provider is injected, no provider is called, no URL is "
    "fetched, no network is opened, no credential is read, and no real data is "
    "acquired. real_data_qa stays BLOCKED, baseline stays BLOCKED, and the paper / "
    "micro-live gates stay LOCKED here, always."
)

# The action that BUILDING this contract satisfies, and the stage it occupies.
DRY_RUN_NEXT_REQUIRED_ACTION = (
    "BUILD_CRYPTO_D1_SELECTED_READ_ONLY_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN"
)
DRY_RUN_CURRENT_STAGE = (
    "CRYPTO_D1_SELECTED_READ_ONLY_SPOT_PROVIDER_FETCH_RUNNER_DRY_RUN_REQUIRED"
)

# The current mission-flow truth this contract is anchored to. The companion test
# cross-checks these against the live status module so they cannot silently drift.
DRY_RUN_MISSION_FLOW_CURRENT_STAGE = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED"
)
DRY_RUN_MISSION_FLOW_NEXT_REQUIRED_ACTION = (
    "HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION"
)

# The ten dry-run items (id, human label), in display order. READY requires all of
# them to pass.
DRY_RUN_ITEMS: tuple[tuple[str, str], ...] = (
    (
        "uses_fake_provider_only",
        "Dry run uses only an in-memory FAKE provider; no real provider is "
        "injected",
    ),
    (
        "read_only_fetch_call_only",
        "Runner invokes only the read-only fetch method; no trading / account / "
        "order call",
    ),
    (
        "returns_required_ohlcv_fields",
        "Fake provider rows include the required OHLCV + source + instrument_type "
        "fields",
    ),
    (
        "spot_instrument_type_only",
        "Fake rows declare instrument_type 'spot' only; no futures / perps / "
        "leverage",
    ),
    (
        "daily_timeframe_only",
        "Fake rows are daily (D1) bars only; matches Crypto-D1",
    ),
    (
        "no_credentials_in_dry_run",
        "Dry run needs no API key / credential / secret",
    ),
    (
        "deterministic_dry_run_result",
        "Dry run yields a deterministic in-memory result; no order / trade side "
        "effect",
    ),
    (
        "no_real_data_persisted",
        "Dry run persists / writes no real data; in-memory only",
    ),
    (
        "no_network_in_dry_run",
        "Dry run opens no network, fetches no URL, and calls no endpoint",
    ),
    (
        "matches_block151_adapter_contract",
        "Overall the dry run exercises the Block 151 read-only spot adapter "
        "contract, and mission flow is still at the boundary",
    ),
)
DRY_RUN_ITEM_IDS: tuple[str, ...] = tuple(
    item_id for item_id, _label in DRY_RUN_ITEMS
)

# Contract outcomes (exactly one assigned).
OUTCOME_READY = "READY_FOR_HUMAN_DRY_RUN_REVIEW"
OUTCOME_HOLD = "HOLD_NEEDS_MORE_PREP"

DRY_RUN_OUTCOMES: tuple[str, ...] = (
    OUTCOME_READY,
    OUTCOME_HOLD,
)

# Top-level authorization flags that, if truthy, are an unsafe request -> safety
# violation -> HOLD.
DRY_RUN_AUTHORIZATION_FLAGS: tuple[str, ...] = (
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
DRY_RUN_GATE_LOCK_FLAGS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)

# Explicit gate-unlock request flags that, if truthy, are an unsafe request.
DRY_RUN_GATE_UNLOCK_REQUEST_FLAGS: tuple[str, ...] = (
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
DRY_RUN_FORBIDDEN_PROMOTION_REQUEST_FLAGS: tuple[str, ...] = (
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
    "auto_approve_dry_run",
    "auto_run_real_provider",
    "auto_push",
)

# Flags whose truthy value means the dry run would inject / swap in a REAL provider
# rather than the in-memory FAKE provider -> unsafe (this contract only ever
# reasons over a static fake-provider dry-run description).
DRY_RUN_REAL_PROVIDER_FLAGS: tuple[str, ...] = (
    "injects_real_provider",
    "uses_real_provider",
    "binds_live_provider",
    "swaps_in_real_provider",
    "real_provider",
)

# Flags whose truthy value means the described dry run would implement / call a
# live endpoint / fetch / network now -> unsafe (this contract only ever reasons
# over a static fake-provider description).
DRY_RUN_LIVE_ENDPOINT_FLAGS: tuple[str, ...] = (
    "implements_live_provider",
    "performs_live_fetch",
    "calls_endpoint_now",
    "requires_live_endpoint_call",
    "opens_network",
    "fetches_url",
    "live_endpoint",
)

# Flags whose truthy value means the described dry run would require a credential /
# secret / account auth -> not a public read-only fake-provider dry run -> unsafe.
DRY_RUN_CREDENTIAL_NEED_FLAGS: tuple[str, ...] = (
    "requires_credentials",
    "requires_api_key",
    "requires_secret",
    "requires_account_auth",
    "requires_login",
)

# Fields whose presence (non-empty) on the payload signals account / trading /
# order data rather than a static read-only dry-run description -> safety violation.
DRY_RUN_ACCOUNT_TRADE_FIELDS: tuple[str, ...] = (
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
DRY_RUN_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
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
DRY_RUN_SAFETY_POSTURE: dict[str, bool] = {
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
    "injects_real_provider": False,
    "implements_provider": False,
    "calls_endpoint": False,
    "fetches_url": False,
    "opens_network": False,
    "reads_credential": False,
    "acquires_real_data": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}


# A deterministic, illustrative paper sample describing a sound fake-provider dry
# run of the selected read-only spot provider fetch runner: every required item is
# asserted, every gate is locked, and no unsafe flag is set, so the default
# evaluation is READY_FOR_HUMAN_DRY_RUN_REVIEW. Nothing here is real and no real
# provider is named or injected; static example only.
DEFAULT_SAMPLE_DRY_RUN_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 selected read-only spot provider fetch runner dry run (static sample)",
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
    "uses_fake_provider_only": True,
    "read_only_fetch_call_only": True,
    "returns_required_ohlcv_fields": True,
    "spot_instrument_type_only": True,
    "daily_timeframe_only": True,
    "no_credentials_in_dry_run": True,
    "deterministic_dry_run_result": True,
    "no_real_data_persisted": True,
    "no_network_in_dry_run": True,
    "matches_block151_adapter_contract": True,
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
    """Collect any payload keys that attempt to authorize, unlock, promote, inject
    a real provider, claim a live endpoint, need a credential, or carry an account
    / trade instruction. Pure; reads only the static payload."""
    hits: list[str] = []
    for flag in DRY_RUN_AUTHORIZATION_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in DRY_RUN_GATE_UNLOCK_REQUEST_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in DRY_RUN_FORBIDDEN_PROMOTION_REQUEST_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in DRY_RUN_REAL_PROVIDER_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in DRY_RUN_LIVE_ENDPOINT_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for flag in DRY_RUN_CREDENTIAL_NEED_FLAGS:
        if _is_truthy(payload.get(flag)):
            hits.append(flag)
    for field in DRY_RUN_ACCOUNT_TRADE_FIELDS:
        value = payload.get(field)
        if value not in (None, "", [], {}, 0, False):
            hits.append(field)
    for flag in DRY_RUN_GATE_LOCK_FLAGS:
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
        for flag in DRY_RUN_GATE_LOCK_FLAGS
    )


# --------------------------------------------------------------------------- #
# assessment
# --------------------------------------------------------------------------- #
def assess_selected_read_only_spot_provider_fetch_runner_dry_run(
    payload: Any,
) -> dict[str, Any]:
    """Assess (read-only) a described fake-provider dry run of the selected
    read-only spot provider fetch runner. Returns a fresh dict every call.
    Authorizes nothing and unlocks nothing under any outcome -- a
    READY_FOR_HUMAN_DRY_RUN_REVIEW result only means the paper dry run is sound
    enough for a human to review the exercise."""
    data = _as_payload(payload)

    mf_stage = data.get(
        "mission_flow_current_stage",
        DRY_RUN_MISSION_FLOW_CURRENT_STAGE,
    )
    mf_action = data.get(
        "mission_flow_next_required_action",
        DRY_RUN_MISSION_FLOW_NEXT_REQUIRED_ACTION,
    )
    mission_flow_aligned = (
        str(mf_stage) == DRY_RUN_MISSION_FLOW_CURRENT_STAGE
        and str(mf_action)
        == DRY_RUN_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    unsafe_hits = _unsafe_flag_hits(data)
    gates_locked = _gates_all_locked(data)

    # Each item passes only when the caller's static description asserts it AND no
    # unsafe flag undermines it. The two derived items below additionally require
    # that no unsafe flag is set / mission flow is still at the boundary.
    item_results: dict[str, bool] = {
        "uses_fake_provider_only": _is_truthy(
            data.get("uses_fake_provider_only")
        ),
        "read_only_fetch_call_only": _is_truthy(
            data.get("read_only_fetch_call_only")
        ),
        "returns_required_ohlcv_fields": _is_truthy(
            data.get("returns_required_ohlcv_fields")
        ),
        "spot_instrument_type_only": _is_truthy(
            data.get("spot_instrument_type_only")
        ),
        "daily_timeframe_only": _is_truthy(data.get("daily_timeframe_only")),
        "no_credentials_in_dry_run": _is_truthy(
            data.get("no_credentials_in_dry_run")
        ),
        "deterministic_dry_run_result": _is_truthy(
            data.get("deterministic_dry_run_result")
        ),
        "no_real_data_persisted": _is_truthy(
            data.get("no_real_data_persisted")
        ),
        "no_network_in_dry_run": _is_truthy(
            data.get("no_network_in_dry_run")
        )
        and len(unsafe_hits) == 0,
        "matches_block151_adapter_contract": _is_truthy(
            data.get("matches_block151_adapter_contract")
        )
        and mission_flow_aligned,
    }

    _reasons = {
        "uses_fake_provider_only": (
            "the dry run uses only an in-memory FAKE provider; no real provider "
            "is injected"
            if item_results["uses_fake_provider_only"]
            else "fake-provider-only dry run is NOT confirmed"
        ),
        "read_only_fetch_call_only": (
            "the runner invokes only the read-only fetch method; no trading / "
            "account / order call"
            if item_results["read_only_fetch_call_only"]
            else "read-only-only fetch call surface is NOT confirmed"
        ),
        "returns_required_ohlcv_fields": (
            "the fake provider rows include the required OHLCV + source + "
            "instrument_type fields"
            if item_results["returns_required_ohlcv_fields"]
            else "required OHLCV / source / instrument_type fields are NOT "
            "confirmed"
        ),
        "spot_instrument_type_only": (
            "fake rows declare instrument_type 'spot' only; no futures / perps / "
            "leverage"
            if item_results["spot_instrument_type_only"]
            else "spot-only instrument_type is NOT confirmed"
        ),
        "daily_timeframe_only": (
            "fake rows are daily (D1) bars only; matches Crypto-D1"
            if item_results["daily_timeframe_only"]
            else "daily (D1) timeframe-only is NOT confirmed"
        ),
        "no_credentials_in_dry_run": (
            "the dry run needs no API key / credential / secret"
            if item_results["no_credentials_in_dry_run"]
            else "a credential / API key / secret appears to be required"
        ),
        "deterministic_dry_run_result": (
            "the dry run yields a deterministic in-memory result; no order / "
            "trade side effect"
            if item_results["deterministic_dry_run_result"]
            else "a deterministic in-memory dry-run result is NOT confirmed"
        ),
        "no_real_data_persisted": (
            "the dry run persists / writes no real data; in-memory only"
            if item_results["no_real_data_persisted"]
            else "no-real-data-persisted is NOT confirmed"
        ),
        "no_network_in_dry_run": (
            "the dry run opens no network, fetches no URL, and calls no endpoint"
            if item_results["no_network_in_dry_run"]
            else "a network open / URL fetch / endpoint call or unsafe flag was "
            "detected"
        ),
        "matches_block151_adapter_contract": (
            "the dry run exercises the Block 151 read-only spot adapter contract, "
            "and mission flow is still at the boundary"
            if item_results["matches_block151_adapter_contract"]
            else "the dry run does NOT fit the Block 151 adapter contract, or "
            "mission flow has left the boundary"
        ),
    }

    dry_run_items = [
        {
            "id": item_id,
            "label": label,
            "passed": item_results[item_id],
            "reason": _reasons[item_id],
        }
        for item_id, label in DRY_RUN_ITEMS
    ]

    failed_items = [c["id"] for c in dry_run_items if not c["passed"]]
    safety_violation = len(unsafe_hits) > 0

    if safety_violation or failed_items:
        outcome = OUTCOME_HOLD
    else:
        outcome = OUTCOME_READY

    return {
        "mode": DRY_RUN_MODE,
        "outcome": outcome,
        "mission_flow_current_stage": str(mf_stage),
        "mission_flow_next_required_action": str(mf_action),
        "mission_flow_aligned": mission_flow_aligned,
        "dry_run_items": dry_run_items,
        "dry_run_item_ids": list(DRY_RUN_ITEM_IDS),
        "passed_item_ids": [c["id"] for c in dry_run_items if c["passed"]],
        "failed_item_ids": list(failed_items),
        "unsafe_flag_hits": list(unsafe_hits),
        "safety_violation": safety_violation,
        "gates_blocked_locked": gates_locked,
        "ready": outcome == OUTCOME_READY,
        "ready_for_human_dry_run_review": outcome == OUTCOME_READY,
        "describes_research_only": True,
        "injects_real_provider": False,
        "implements_provider": False,
        "calls_endpoint": False,
        "fetches_url": False,
        "acquires_real_data": False,
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
            "Ready to put the described fake-provider dry run in front of a human "
            "for dry-run review. Readiness is not execution: a human must still "
            "review the described dry run and separately decide whether to ever run "
            "it against a real provider. This contract injects nothing, calls "
            "nothing, and fetches nothing; real_data_qa remains BLOCKED until a "
            "separate, future, explicitly human-approved step provides "
            "authorization."
        )
    if assessment["safety_violation"]:
        return (
            "Hold. An unsafe flag was set (authorization / gate-unlock / "
            "promotion / real-provider injection / live-endpoint / credential-need "
            "/ account-trade field / boundary-crossing). Do NOT put the dry run in "
            "front of a human yet. Rebuild it as a static, research-only, "
            "fake-provider, read-only description; inject nothing, call nothing, "
            "fetch nothing. real_data_qa remains BLOCKED."
        )
    return (
        "Hold. One or more required dry-run items are missing -- resolve every "
        "failing item before putting the described fake-provider dry run in front "
        "of a human. Nothing is injected, called, fetched, or run; real_data_qa "
        "remains BLOCKED."
    )


def build_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the read-only Selected Read-Only Spot Provider Fetch
    Runner Dry Run contract record. All capability flags are False and all gate
    locks are True regardless of the assessed outcome."""
    data = (
        dict(DEFAULT_SAMPLE_DRY_RUN_INPUT)
        if payload is None
        else _as_payload(payload)
    )
    assessment = assess_selected_read_only_spot_provider_fetch_runner_dry_run(
        data
    )

    contract: dict[str, Any] = {
        "schema_version": DRY_RUN_SCHEMA_VERSION,
        "label": DRY_RUN_LABEL,
        "status": DRY_RUN_STATUS,
        "stage": DRY_RUN_CURRENT_STAGE,
        "mode": DRY_RUN_MODE,
        "core_rule": DRY_RUN_CORE_RULE,
        "contract_next_required_action": (
            DRY_RUN_NEXT_REQUIRED_ACTION
        ),
        "contract_current_stage": DRY_RUN_CURRENT_STAGE,
        "mission_flow_current_stage": (
            DRY_RUN_MISSION_FLOW_CURRENT_STAGE
        ),
        "mission_flow_next_required_action": (
            DRY_RUN_MISSION_FLOW_NEXT_REQUIRED_ACTION
        ),
        "mission_flow_aligned": assessment["mission_flow_aligned"],
        "outcomes": list(DRY_RUN_OUTCOMES),
        "outcome": assessment["outcome"],
        "ready": assessment["ready"],
        "ready_for_human_dry_run_review": (
            assessment["ready_for_human_dry_run_review"]
        ),
        "safety_violation": assessment["safety_violation"],
        "dry_run_item_ids": list(DRY_RUN_ITEM_IDS),
        "dry_run_items": assessment["dry_run_items"],
        "passed_item_ids": list(assessment["passed_item_ids"]),
        "failed_item_ids": list(assessment["failed_item_ids"]),
        "unsafe_flag_hits": list(assessment["unsafe_flag_hits"]),
        "authorization_flags": list(DRY_RUN_AUTHORIZATION_FLAGS),
        "gate_lock_flags": list(DRY_RUN_GATE_LOCK_FLAGS),
        "gate_unlock_request_flags": list(
            DRY_RUN_GATE_UNLOCK_REQUEST_FLAGS
        ),
        "forbidden_promotion_request_flags": list(
            DRY_RUN_FORBIDDEN_PROMOTION_REQUEST_FLAGS
        ),
        "real_provider_flags": list(DRY_RUN_REAL_PROVIDER_FLAGS),
        "live_endpoint_flags": list(DRY_RUN_LIVE_ENDPOINT_FLAGS),
        "credential_need_flags": list(DRY_RUN_CREDENTIAL_NEED_FLAGS),
        "account_trade_fields": list(DRY_RUN_ACCOUNT_TRADE_FIELDS),
        "forbidden_trade_terms": list(DRY_RUN_FORBIDDEN_TRADE_TERMS),
        "assessment": assessment,
        "operator_next_step": _operator_next_step(assessment),
        "operator_notes": (
            "Read-only fake-provider dry run. It confirms the ten dry-run items; "
            "it never injects a real provider, never wires, never fetches, and "
            "never crosses the boundary. Even a READY_FOR_HUMAN_DRY_RUN_REVIEW "
            "result authorizes nothing."
        ),
        "human_operator_required_next_steps": [
            "A human confirms the ten dry-run items passed.",
            "A human reviewer separately decides whether to ever run the "
            "described dry run against a real provider.",
            "A separate, future, explicitly human-approved step is required "
            "before any real provider is injected or run.",
        ],
        "safety_posture": dict(DRY_RUN_SAFETY_POSTURE),
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
        "injects_real_provider": False,
        "implements_provider": False,
        "calls_endpoint": False,
        "fetches_url": False,
        "opens_network": False,
        "reads_credential": False,
        "acquires_real_data": False,
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
    "dry_run_items",
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
    "injects_real_provider",
    "implements_provider",
    "calls_endpoint",
    "fetches_url",
    "opens_network",
    "reads_credential",
    "acquires_real_data",
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


def validate_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built contract. Returns a verdict dict of boolean
    checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == DRY_RUN_SCHEMA_VERSION
    label_ok = c.get("label") == DRY_RUN_LABEL
    mode_ok = c.get("mode") == DRY_RUN_MODE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    human_required = c.get("human_approval_required") is True
    confirmation_required = c.get("requires_independent_confirmation") is True
    future_step_required = (
        c.get("requires_separate_future_human_approved_step") is True
    )
    stage_ok = c.get("stage") == DRY_RUN_CURRENT_STAGE
    core_rule_ok = c.get("core_rule") == DRY_RUN_CORE_RULE
    outcome_ok = c.get("outcome") in DRY_RUN_OUTCOMES
    outcomes_ok = (
        tuple(c.get("outcomes") or ()) == DRY_RUN_OUTCOMES
    )
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage")
        == DRY_RUN_MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == DRY_RUN_MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == DRY_RUN_SAFETY_POSTURE

    items = c.get("dry_run_items")
    ten_dry_run_items = (
        isinstance(items, list)
        and len(items) == 10
        and [item.get("id") for item in items]
        == list(DRY_RUN_ITEM_IDS)
    )

    # READY may only appear when every dry-run item passed AND no safety violation
    # was recorded.
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
        tokens & set(DRY_RUN_FORBIDDEN_TRADE_TERMS)
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
        "ten_dry_run_items": ten_dry_run_items,
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


def render_crypto_d1_selected_read_only_spot_provider_fetch_runner_dry_run_markdown(
    contract: Any,
) -> str:
    """Render a built contract as a deterministic markdown brief. Pure string
    formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    lines: list[str] = []
    lines.append(
        "# Crypto-D1 Selected Read-Only Spot Provider Fetch Runner Dry Run"
    )
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
        "- Injects real provider: " + str(c.get("injects_real_provider", False))
    )
    lines.append(
        "- Calls endpoint: " + str(c.get("calls_endpoint", False))
    )
    lines.append("- Fetches url: " + str(c.get("fetches_url", False)))
    lines.append(
        "- Acquires real data: " + str(c.get("acquires_real_data", False))
    )
    lines.append(
        "- Unlocks real_data_qa: " + str(c.get("unlocks_real_data_qa", False))
    )
    lines.append("- Crosses boundary: " + str(c.get("crosses_boundary", False)))
    lines.append(
        "- real_data_qa_blocked: " + str(c.get("real_data_qa_blocked", True))
    )

    _emit(
        lines,
        "Dry Run",
        [
            str(item.get("id"))
            + ": "
            + ("PASS" if item.get("passed") else "FAIL")
            + " - "
            + str(item.get("reason"))
            for item in (c.get("dry_run_items") or [])
        ],
    )
    _emit(lines, "Failed Items", list(c.get("failed_item_ids") or []))
    _emit(lines, "Unsafe Flag Hits", list(c.get("unsafe_flag_hits") or []))
    _emit(
        lines,
        "No Execution Authorization",
        [
            "authorizes_nothing: " + str(c.get("authorizes_nothing", True)),
            "injects_real_provider: "
            + str(c.get("injects_real_provider", False)),
            "calls_endpoint: " + str(c.get("calls_endpoint", False)),
            "fetches_url: " + str(c.get("fetches_url", False)),
            "acquires_real_data: " + str(c.get("acquires_real_data", False)),
            "unlocks_real_data_qa: "
            + str(c.get("unlocks_real_data_qa", False)),
            "crosses_boundary: " + str(c.get("crosses_boundary", False)),
            "requires_separate_future_human_approved_step: "
            + str(c.get("requires_separate_future_human_approved_step", True)),
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)

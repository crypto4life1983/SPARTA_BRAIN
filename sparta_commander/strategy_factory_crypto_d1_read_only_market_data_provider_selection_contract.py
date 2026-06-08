"""Crypto-D1 Read-Only Market Data Provider Selection Contract (Block 145).

A PURE, stdlib-only, *read-only* CONTRACT / SPEC layer. It ranks candidate
READ-ONLY historical market-data providers for the three missing Crypto-D1 daily
spot pairs (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d) after Block 144's approved one-time
Databento fetch could not run -- the current Databento account exposes NO crypto
spot dataset for those pairs.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

THIS contract executes NOTHING. It does NOT fetch data, call any API, open a
network, read or inspect any credential, read a .env file, print / store / log any
secret, touch any broker / exchange / trading / account / order endpoint, run QA /
baseline / backtest, write any file, or unlock any gate. It only reasons over a
static, caller-supplied (or default) list of candidate provider descriptors and
emits a deterministic ranking plus a single recommended next action.

WHAT THE CONTRACT DOES (and nothing else):
  1. Records that the CURRENT Databento account is unavailable for the approved
     crypto spot pairs (no crypto spot dataset on this subscription).
  2. Explicitly REJECTS wrong-instrument substitution -- in particular, CME crypto
     FUTURES must never be substituted for BTCUSD / ETHUSD / SOLUSD SPOT.
  3. Defines the acceptable-provider criteria (read-only historical, covers the
     three spot USD pairs or clean equivalents, daily timeframe, no trading /
     account / order endpoint, no secret exposure, clear license / source
     metadata).
  4. Classifies each candidate into exactly one ranking category:
     APPROVED_CANDIDATE / NEEDS_PROVIDER_REVIEW / REJECTED_WRONG_INSTRUMENT /
     REJECTED_TRADING_ENDPOINT_RISK / REJECTED_INSUFFICIENT_COVERAGE.
  5. Emits the next recommended action: HOLD_FOR_PROVIDER_CHOICE (a human still
     chooses among approved candidates; the contract chooses nothing).
  6. Keeps every gate blocked / locked.

CORE RULE: ranking providers authorizes nothing, chooses nothing, and crosses no
real-world boundary. real_data_qa stays BLOCKED, baseline stays BLOCKED, and
paper / micro-live stay LOCKED. Selecting and connecting a real provider is a
SEPARATE, future, human-approved action outside this contract.

Public API:
  - SELECTION_SCHEMA_VERSION / SELECTION_LABEL / SELECTION_STATUS / SELECTION_MODE
  - SELECTION_CORE_RULE / MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - SELECTION_APPROVED_SYMBOLS / SELECTION_APPROVED_TIMEFRAMES
  - CATEGORY_APPROVED_CANDIDATE / CATEGORY_NEEDS_PROVIDER_REVIEW /
    CATEGORY_REJECTED_WRONG_INSTRUMENT / CATEGORY_REJECTED_TRADING_ENDPOINT_RISK /
    CATEGORY_REJECTED_INSUFFICIENT_COVERAGE / SELECTION_CATEGORIES
  - NEXT_RECOMMENDED_ACTION
  - SELECTION_PROVIDER_CRITERIA / SELECTION_WRONG_INSTRUMENT_REJECTION_RULES
  - DATABENTO_CURRENT_ACCOUNT_RECORD / DEFAULT_PROVIDER_CANDIDATES
  - SELECTION_SAFETY_POSTURE / DEFAULT_SELECTION_INPUT
  - classify_provider_candidate(descriptor)
  - build_crypto_d1_read_only_market_data_provider_selection_contract(payload=None)
  - validate_crypto_d1_read_only_market_data_provider_selection_contract(contract)
  - render_crypto_d1_read_only_market_data_provider_selection_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    FETCH_APPROVED_SYMBOLS,
    FETCH_APPROVED_TIMEFRAMES,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

SELECTION_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_read_only_market_data_provider_selection_contract.v1"
)
SELECTION_LABEL = (
    "Block 145 - Crypto-D1 Read-Only Market Data Provider Selection Contract"
)
SELECTION_STATUS = "READ_ONLY_PROVIDER_SELECTION_CONTRACT"
SELECTION_MODE = "RESEARCH_ONLY"

SELECTION_CORE_RULE = (
    "Ranking candidate read-only historical market-data providers authorizes "
    "nothing, chooses nothing, and crosses no real-world boundary. No data is "
    "fetched, no API is called, no network is opened, no credential is read, and "
    "no .env is read. Selecting and connecting a real provider is a SEPARATE, "
    "future, human-approved action. real_data_qa stays BLOCKED, baseline stays "
    "BLOCKED, and paper / micro-live stay LOCKED."
)

SELECTION_APPROVED_SYMBOLS: tuple[str, ...] = FETCH_APPROVED_SYMBOLS
SELECTION_APPROVED_TIMEFRAMES: tuple[str, ...] = FETCH_APPROVED_TIMEFRAMES

# 4. Ranking categories.
CATEGORY_APPROVED_CANDIDATE = "APPROVED_CANDIDATE"
CATEGORY_NEEDS_PROVIDER_REVIEW = "NEEDS_PROVIDER_REVIEW"
CATEGORY_REJECTED_WRONG_INSTRUMENT = "REJECTED_WRONG_INSTRUMENT"
CATEGORY_REJECTED_TRADING_ENDPOINT_RISK = "REJECTED_TRADING_ENDPOINT_RISK"
CATEGORY_REJECTED_INSUFFICIENT_COVERAGE = "REJECTED_INSUFFICIENT_COVERAGE"
SELECTION_CATEGORIES: tuple[str, ...] = (
    CATEGORY_APPROVED_CANDIDATE,
    CATEGORY_NEEDS_PROVIDER_REVIEW,
    CATEGORY_REJECTED_WRONG_INSTRUMENT,
    CATEGORY_REJECTED_TRADING_ENDPOINT_RISK,
    CATEGORY_REJECTED_INSUFFICIENT_COVERAGE,
)

# 5. The single next recommended action this contract emits.
NEXT_RECOMMENDED_ACTION = "HOLD_FOR_PROVIDER_CHOICE"

# 3. Acceptable-provider criteria.
SELECTION_PROVIDER_CRITERIA: tuple[str, ...] = (
    "Read-only historical market data (no execution capability).",
    "Covers BTCUSD, ETHUSD, SOLUSD or clean equivalent spot USD pairs.",
    "Daily (1d) timeframe is available.",
    "No trading endpoint required.",
    "No account / portfolio endpoint required.",
    "No order endpoint required.",
    "No secret exposure (no credential printed, logged, or stored).",
    "Clear license / source metadata.",
)

# 2. Wrong-instrument rejection rules (explicit).
SELECTION_WRONG_INSTRUMENT_REJECTION_RULES: tuple[str, ...] = (
    "CME crypto FUTURES must never be substituted for BTCUSD / ETHUSD / SOLUSD "
    "SPOT. Futures are a different instrument with different prices, expiries, and "
    "settlement -- not a clean spot daily series.",
    "Any non-spot or derivative instrument presented as a substitute for the "
    "approved spot pairs is REJECTED_WRONG_INSTRUMENT.",
    "Only genuine spot USD pairs (or a clean spot equivalent) are eligible.",
)

# 1. Record: current Databento account is unavailable for the approved crypto spot
# pairs (no crypto spot dataset on this subscription). Factual, not a judgement on
# Databento as a vendor -- a crypto add-on could later change this.
DATABENTO_CURRENT_ACCOUNT_RECORD: dict[str, Any] = {
    "provider": "databento_current_account",
    "available_for_approved_crypto_spot": False,
    "observed_via": "read-only metadata catalog listing (no data fetch)",
    "finding": (
        "The current Databento subscription exposes US equities, US / EU futures, "
        "and options datasets only. No crypto SPOT dataset for BTCUSD / ETHUSD / "
        "SOLUSD is available on this account."
    ),
    "note": (
        "A future Databento crypto add-on / subscription could move this to "
        "NEEDS_PROVIDER_REVIEW. This contract neither enables nor requests it."
    ),
}

# Default static candidate descriptors. These are illustrative ARCHETYPES plus the
# two factual records the contract must carry; they name no chosen vendor and
# commit to nothing. Each is classified deterministically by the criteria above.
DEFAULT_PROVIDER_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "name": "databento_current_account",
        "kind": "historical_market_data",
        "instrument": "equities / futures / options only (no crypto spot)",
        "read_only_historical": True,
        "covers_symbols": [],
        "daily_timeframe": True,
        "requires_trading_endpoint": False,
        "requires_account_endpoint": False,
        "requires_order_endpoint": False,
        "requires_portfolio_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": True,
        "available_on_current_account": False,
        "is_crypto_futures_substitute": False,
    },
    {
        "name": "cme_crypto_futures_via_databento_archetype",
        "kind": "futures",
        "instrument": "CME crypto FUTURES (e.g. BTC futures) -- not spot",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "requires_trading_endpoint": False,
        "requires_account_endpoint": False,
        "requires_order_endpoint": False,
        "requires_portfolio_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": True,
        "available_on_current_account": True,
        "is_crypto_futures_substitute": True,
    },
    {
        "name": "crypto_exchange_trading_api_archetype",
        "kind": "exchange_api",
        "instrument": "BTCUSD / ETHUSD / SOLUSD spot via an exchange trading API",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "requires_trading_endpoint": True,
        "requires_account_endpoint": True,
        "requires_order_endpoint": False,
        "requires_portfolio_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": True,
        "available_on_current_account": True,
        "is_crypto_futures_substitute": False,
    },
    {
        "name": "read_only_spot_historical_provider_archetype_clear_license",
        "kind": "historical_market_data",
        "instrument": "BTCUSD / ETHUSD / SOLUSD spot daily bars",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "requires_trading_endpoint": False,
        "requires_account_endpoint": False,
        "requires_order_endpoint": False,
        "requires_portfolio_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": True,
        "available_on_current_account": True,
        "is_crypto_futures_substitute": False,
    },
    {
        "name": "read_only_spot_historical_provider_archetype_unclear_license",
        "kind": "historical_market_data",
        "instrument": "BTCUSD / ETHUSD / SOLUSD spot daily bars",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "requires_trading_endpoint": False,
        "requires_account_endpoint": False,
        "requires_order_endpoint": False,
        "requires_portfolio_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": False,
        "available_on_current_account": True,
        "is_crypto_futures_substitute": False,
    },
)

# Top-level flags that, if truthy on an operator's input, mark it unsafe.
SELECTION_FORBIDDEN_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "authorizes_qa_baseline",
    "unlocks_downstream_gate",
    "print_credentials",
    "expose_secret",
    "inspect_dotenv",
    "fetch_data_now",
    "call_provider_now",
    "choose_provider_now",
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "place_order",
    "go_live",
)

# Execution / promotion verbs the authored NARRATIVE must never contain as whole
# words.
SELECTION_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Read-only safety posture. Posture facts are True; every capability flag is False.
SELECTION_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "human_choice_required": True,
    "executes": False,
    "performs_data_fetch": False,
    "calls_provider_api": False,
    "uses_network": False,
    "fetches_data": False,
    "downloads_data": False,
    "checks_live_credentials": False,
    "reads_dotenv": False,
    "exposes_secret": False,
    "reads_data_files": False,
    "writes_data_files": False,
    "writes_reports": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "runs_qa": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "chooses_provider": False,
    "connects_provider": False,
    "authorizes_trading": False,
    "authorizes_paper_trading": False,
    "authorizes_live_trading": False,
    "authorizes_broker_exchange": False,
    "authorizes_order_placement": False,
    "authorizes_account_control": False,
    "authorizes_portfolio_control": False,
    "authorizes_strategy_promotion": False,
    "authorizes_automation_trading": False,
    "authorizes_qa_baseline": False,
    "unlocks_real_data_qa": False,
    "unlocks_baseline_backtest": False,
    "unlocks_paper_trading": False,
    "unlocks_micro_live": False,
}

# Deterministic static input. No real data, no secret, no candidates override.
DEFAULT_SELECTION_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 provider selection contract input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
    "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
    "real_data_qa_blocked": True,
    "baseline_backtest_blocked": True,
    "paper_trading_gate_locked": True,
    "micro_live_gate_locked": True,
}


# --------------------------------------------------------------------------- #
# small pure helpers
# --------------------------------------------------------------------------- #
def _as_payload(payload: Any) -> dict[str, Any]:
    return dict(payload) if isinstance(payload, dict) else {}


def _is_truthy(value: Any) -> bool:
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "on"}
    return bool(value)


def _as_str_set(value: Any) -> set[str]:
    if not isinstance(value, (list, tuple, set)):
        return set()
    return {str(v).strip().upper() for v in value if str(v).strip()}


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


_SECRET_VALUE_TOKENS: tuple[str, ...] = (
    "api_key",
    "apikey",
    "secret",
    "password",
    "private_key",
    "bearer",
    "access_token",
)


def _has_secret_value(obj: Any) -> bool:
    """True if any dict key looks like a secret AND carries a non-empty string
    value. A secret VALUE is always a string; booleans / counts are flags."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_l = str(key).lower()
            looks_secret = any(tok in key_l for tok in _SECRET_VALUE_TOKENS)
            if looks_secret and isinstance(value, str) and value.strip():
                return True
            if _has_secret_value(value):
                return True
    elif isinstance(obj, (list, tuple)):
        for item in obj:
            if _has_secret_value(item):
                return True
    return False


# --------------------------------------------------------------------------- #
# classification
# --------------------------------------------------------------------------- #
def classify_provider_candidate(descriptor: Any) -> dict[str, Any]:
    """Classify (read-only) ONE candidate provider descriptor into exactly one
    ranking category, with the criteria booleans and human-readable reasons.
    Pure: reads only the static descriptor; calls nothing."""
    d = _as_payload(descriptor)
    name = str(d.get("name", "")) or "unnamed_candidate"

    approved = set(SELECTION_APPROVED_SYMBOLS)
    covers = _as_str_set(d.get("covers_symbols"))
    covers_all_symbols = bool(
        approved <= covers or _is_truthy(d.get("covers_equivalent_spot_usd"))
    )
    daily_ok = _is_truthy(d.get("daily_timeframe"))
    read_only_ok = _is_truthy(d.get("read_only_historical"))
    no_trading_endpoint = not _is_truthy(d.get("requires_trading_endpoint"))
    no_account_endpoint = not _is_truthy(d.get("requires_account_endpoint"))
    no_order_endpoint = not _is_truthy(d.get("requires_order_endpoint"))
    no_portfolio_endpoint = not _is_truthy(d.get("requires_portfolio_endpoint"))
    no_secret_exposure = not _is_truthy(d.get("exposes_secret"))
    has_license = _is_truthy(d.get("has_license_metadata"))
    available = _is_truthy(d.get("available_on_current_account", True))
    wrong_instrument = _is_truthy(
        d.get("is_crypto_futures_substitute")
    ) or _is_truthy(d.get("is_wrong_instrument_substitute"))

    criteria = {
        "covers_all_symbols": covers_all_symbols,
        "daily_timeframe_ok": daily_ok,
        "read_only_historical_ok": read_only_ok,
        "no_trading_endpoint": no_trading_endpoint,
        "no_account_endpoint": no_account_endpoint,
        "no_order_endpoint": no_order_endpoint,
        "no_portfolio_endpoint": no_portfolio_endpoint,
        "no_secret_exposure": no_secret_exposure,
        "has_license_metadata": has_license,
        "available_for_approved_pairs": available,
        "wrong_instrument_substitute": wrong_instrument,
    }

    reasons: list[str] = []
    # Priority order: wrong instrument -> endpoint / safety risk -> coverage ->
    # license review -> approved.
    if wrong_instrument:
        category = CATEGORY_REJECTED_WRONG_INSTRUMENT
        reasons.append(
            "Non-spot / derivative instrument offered as a substitute for the "
            "approved spot pairs (e.g. CME crypto futures)."
        )
    elif not (
        read_only_ok
        and no_trading_endpoint
        and no_account_endpoint
        and no_order_endpoint
        and no_portfolio_endpoint
        and no_secret_exposure
    ):
        category = CATEGORY_REJECTED_TRADING_ENDPOINT_RISK
        if not read_only_ok:
            reasons.append("Not read-only historical (execution-capable).")
        if not no_trading_endpoint:
            reasons.append("Requires a trading endpoint.")
        if not no_account_endpoint:
            reasons.append("Requires an account endpoint.")
        if not no_order_endpoint:
            reasons.append("Requires an order endpoint.")
        if not no_portfolio_endpoint:
            reasons.append("Requires a portfolio endpoint.")
        if not no_secret_exposure:
            reasons.append("Exposes a secret / credential.")
    elif not (covers_all_symbols and daily_ok and available):
        category = CATEGORY_REJECTED_INSUFFICIENT_COVERAGE
        if not covers_all_symbols:
            reasons.append(
                "Does not cover BTCUSD / ETHUSD / SOLUSD (or clean spot "
                "equivalents)."
            )
        if not daily_ok:
            reasons.append("Daily (1d) timeframe not available.")
        if not available:
            reasons.append(
                "Not available for the approved crypto spot pairs on the current "
                "account / subscription."
            )
    elif not has_license:
        category = CATEGORY_NEEDS_PROVIDER_REVIEW
        reasons.append(
            "Meets data criteria but lacks clear license / source metadata -- "
            "needs human review before it can be an approved candidate."
        )
    else:
        category = CATEGORY_APPROVED_CANDIDATE
        reasons.append(
            "Meets every criterion: read-only historical, covers the approved "
            "spot pairs at daily resolution, no trading / account / order "
            "endpoint, no secret exposure, clear license metadata. Eligible for "
            "human selection (not selected by this contract)."
        )

    return {
        "name": name,
        "kind": str(d.get("kind", "")),
        "instrument": str(d.get("instrument", "")),
        "category": category,
        "criteria": criteria,
        "reasons": reasons,
    }


# --------------------------------------------------------------------------- #
# contract build
# --------------------------------------------------------------------------- #
def build_crypto_d1_read_only_market_data_provider_selection_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the provider selection contract. Every capability
    flag is False and every gate lock is True regardless of input. The contract
    chooses no provider; the next recommended action is always
    HOLD_FOR_PROVIDER_CHOICE."""
    data = dict(DEFAULT_SELECTION_INPUT) if payload is None else _as_payload(payload)

    mf_stage = data.get("mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE)
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_flag_hits = [
        f for f in SELECTION_FORBIDDEN_FLAGS if _is_truthy(data.get(f))
    ]
    safe = mission_flow_aligned and not forbidden_flag_hits

    candidates = data.get("candidates")
    if not isinstance(candidates, (list, tuple)) or not candidates:
        candidates = DEFAULT_PROVIDER_CANDIDATES

    classifications = [classify_provider_candidate(c) for c in candidates]
    by_category: dict[str, list[str]] = {cat: [] for cat in SELECTION_CATEGORIES}
    for item in classifications:
        by_category.setdefault(item["category"], []).append(item["name"])
    category_counts = {cat: len(by_category.get(cat, [])) for cat in SELECTION_CATEGORIES}
    approved_candidates = list(by_category.get(CATEGORY_APPROVED_CANDIDATE, []))

    spec = {
        # 1. Databento current-account record
        "databento_current_account_record": dict(DATABENTO_CURRENT_ACCOUNT_RECORD),
        # 2. wrong-instrument rejection rules
        "wrong_instrument_rejection_rules": list(
            SELECTION_WRONG_INSTRUMENT_REJECTION_RULES
        ),
        # 3. provider criteria
        "provider_criteria": list(SELECTION_PROVIDER_CRITERIA),
        # 4. ranking
        "ranking_categories": list(SELECTION_CATEGORIES),
        "classifications": classifications,
        "by_category": by_category,
        "category_counts": category_counts,
        "approved_candidates": approved_candidates,
        # 5. next recommended action
        "next_recommended_action": NEXT_RECOMMENDED_ACTION,
        # no-unlock confirmation
        "no_unlock_confirmation": {
            "unlocks_real_data_qa": False,
            "unlocks_baseline_backtest": False,
            "unlocks_paper_trading": False,
            "unlocks_micro_live": False,
            "real_data_qa_state": "BLOCKED",
            "baseline_backtest_state": "BLOCKED",
            "paper_live_state": "LOCKED",
        },
    }

    contract: dict[str, Any] = {
        "schema_version": SELECTION_SCHEMA_VERSION,
        "label": SELECTION_LABEL,
        "status": SELECTION_STATUS,
        "mode": SELECTION_MODE,
        "core_rule": SELECTION_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": mission_flow_aligned,
        "safe": safe,
        "forbidden_flag_hits": list(forbidden_flag_hits),
        "approved_symbols": list(SELECTION_APPROVED_SYMBOLS),
        "approved_timeframes": list(SELECTION_APPROVED_TIMEFRAMES),
        "selection_contract": spec,
        "next_recommended_action": NEXT_RECOMMENDED_ACTION,
        "selection_summary": (
            "Read-only ranking of candidate historical market-data providers for "
            "the missing Crypto-D1 spot pairs (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d). "
            "The current Databento account has no crypto spot dataset for these "
            "pairs; CME crypto futures are rejected as a wrong-instrument "
            "substitute. THIS contract ranks only -- it fetches nothing, calls no "
            "API, chooses no provider, and unlocks no gate."
        ),
        "operator_next_step": (
            "A human reviews this ranking and, as a SEPARATE action, decides "
            "whether to onboard one of the approved candidates. Reviewing this "
            "ranking acquires no data, calls no provider, and unlocks no gate; the "
            "recommended next action is HOLD_FOR_PROVIDER_CHOICE."
        ),
        "human_operator_required_next_steps": [
            "A human reviews this read-only provider ranking.",
            "A human separately chooses whether to onboard an approved candidate "
            "and provision its read-only access OUTSIDE this contract.",
            "Only after a separate human-approved onboarding could a future "
            "read-only fetch be planned; this contract unlocks no gate.",
        ],
        "requires_human_provider_choice": True,
        "this_contract_chooses_provider": False,
        "safety_posture": dict(SELECTION_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "read_only": True,
        "research_only": True,
        "executes": False,
        "performs_data_fetch": False,
        "calls_provider_api": False,
        "uses_network": False,
        "fetches_data": False,
        "downloads_data": False,
        "checks_live_credentials": False,
        "reads_dotenv": False,
        "exposes_secret": False,
        "reads_data_files": False,
        "writes_data_files": False,
        "writes_reports": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
        "runs_qa": False,
        "runs_backtest": False,
        "runs_simulation": False,
        "chooses_provider": False,
        "connects_provider": False,
        "authorizes_trading": False,
        "authorizes_paper_trading": False,
        "authorizes_live_trading": False,
        "authorizes_broker_exchange": False,
        "authorizes_order_placement": False,
        "authorizes_account_control": False,
        "authorizes_portfolio_control": False,
        "authorizes_strategy_promotion": False,
        "authorizes_automation_trading": False,
        "authorizes_nothing": True,
        "unlocks_real_data_qa": False,
        "unlocks_baseline_backtest": False,
        "unlocks_paper_trading": False,
        "unlocks_micro_live": False,
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
    "mode",
    "core_rule",
    "mission_flow_current_stage",
    "mission_flow_next_required_action",
    "selection_contract",
    "next_recommended_action",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_REQUIRED_SPEC_KEYS: tuple[str, ...] = (
    "databento_current_account_record",
    "wrong_instrument_rejection_rules",
    "provider_criteria",
    "ranking_categories",
    "classifications",
    "by_category",
    "category_counts",
    "approved_candidates",
    "next_recommended_action",
    "no_unlock_confirmation",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "performs_data_fetch",
    "calls_provider_api",
    "uses_network",
    "fetches_data",
    "downloads_data",
    "checks_live_credentials",
    "reads_dotenv",
    "exposes_secret",
    "reads_data_files",
    "writes_data_files",
    "writes_reports",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
    "runs_qa",
    "runs_backtest",
    "runs_simulation",
    "chooses_provider",
    "connects_provider",
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_portfolio_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "unlocks_real_data_qa",
    "unlocks_baseline_backtest",
    "unlocks_paper_trading",
    "unlocks_micro_live",
)

_ALL_GATE_LOCKS: tuple[str, ...] = (
    "real_data_qa_blocked",
    "baseline_backtest_blocked",
    "paper_trading_gate_locked",
    "micro_live_gate_locked",
)


def validate_crypto_d1_read_only_market_data_provider_selection_contract(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built selection contract. Returns a verdict dict of
    boolean checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing_fields = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == SELECTION_SCHEMA_VERSION
    label_ok = c.get("label") == SELECTION_LABEL
    status_ok = c.get("status") == SELECTION_STATUS
    mode_ok = c.get("mode") == SELECTION_MODE
    core_rule_ok = c.get("core_rule") == SELECTION_CORE_RULE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    performs_fetch_false = c.get("performs_data_fetch") is False
    chooses_provider_false = c.get("chooses_provider") is False
    this_chooses_false = c.get("this_contract_chooses_provider") is False
    human_choice_required = c.get("requires_human_provider_choice") is True
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == SELECTION_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
    )
    next_action_ok = c.get("next_recommended_action") == NEXT_RECOMMENDED_ACTION

    spec = c.get("selection_contract")
    spec_is_dict = isinstance(spec, dict)
    spec_keys_ok = spec_is_dict and all(k in spec for k in _REQUIRED_SPEC_KEYS)

    # Databento current account recorded unavailable.
    dba = spec.get("databento_current_account_record") if spec_is_dict else None
    databento_recorded_unavailable = isinstance(dba, dict) and (
        dba.get("available_for_approved_crypto_spot") is False
    )

    # categories list intact and every classification uses a valid category.
    categories_ok = spec_is_dict and spec.get("ranking_categories") == list(
        SELECTION_CATEGORIES
    )
    classifications = spec.get("classifications") if spec_is_dict else None
    classifications_valid = isinstance(classifications, list) and bool(
        classifications
    ) and all(
        isinstance(x, dict) and x.get("category") in SELECTION_CATEGORIES
        for x in classifications
    )

    # wrong-instrument rejection present, and any crypto-futures substitute in the
    # classifications is in fact REJECTED_WRONG_INSTRUMENT.
    wir = spec.get("wrong_instrument_rejection_rules") if spec_is_dict else None
    wrong_instrument_rule_present = isinstance(wir, list) and bool(wir)
    futures_rejected_ok = isinstance(classifications, list) and all(
        x.get("category") == CATEGORY_REJECTED_WRONG_INSTRUMENT
        for x in classifications
        if isinstance(x, dict)
        and x.get("criteria", {}).get("wrong_instrument_substitute") is True
    )

    criteria_present = spec_is_dict and bool(spec.get("provider_criteria"))
    next_action_in_spec_ok = spec_is_dict and spec.get(
        "next_recommended_action"
    ) == NEXT_RECOMMENDED_ACTION

    nuc = spec.get("no_unlock_confirmation") if spec_is_dict else None
    no_unlock_ok = isinstance(nuc, dict) and (
        nuc.get("unlocks_real_data_qa") is False
        and nuc.get("unlocks_baseline_backtest") is False
        and nuc.get("unlocks_paper_trading") is False
        and nuc.get("unlocks_micro_live") is False
        and nuc.get("real_data_qa_state") == "BLOCKED"
        and nuc.get("baseline_backtest_state") == "BLOCKED"
    )

    no_secret_value_fields = not _has_secret_value(c)

    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "selection_summary", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(SELECTION_FORBIDDEN_TRADE_TERMS))

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "status_ok": status_ok,
        "mode_ok": mode_ok,
        "core_rule_ok": core_rule_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "performs_fetch_false": performs_fetch_false,
        "chooses_provider_false": chooses_provider_false,
        "this_chooses_false": this_chooses_false,
        "human_choice_required": human_choice_required,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "next_action_ok": next_action_ok,
        "spec_keys_ok": spec_keys_ok,
        "databento_recorded_unavailable": databento_recorded_unavailable,
        "categories_ok": categories_ok,
        "classifications_valid": classifications_valid,
        "wrong_instrument_rule_present": wrong_instrument_rule_present,
        "futures_rejected_ok": futures_rejected_ok,
        "criteria_present": criteria_present,
        "next_action_in_spec_ok": next_action_in_spec_ok,
        "no_unlock_ok": no_unlock_ok,
        "no_secret_value_fields": no_secret_value_fields,
        "no_trade_language": no_trade_language,
    }
    verdict = dict(checks)
    verdict["missing_fields"] = missing_fields
    verdict["valid"] = (not missing_fields) and all(checks.values())
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


def render_crypto_d1_read_only_market_data_provider_selection_contract_markdown(
    contract: Any,
) -> str:
    """Render a built selection contract as a deterministic markdown brief. Pure
    string formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    spec = c.get("selection_contract") or {}
    record = spec.get("databento_current_account_record") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Read-Only Market Data Provider Selection Contract")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Next recommended action: " + str(c.get("next_recommended_action", ""))
    )
    lines.append(
        "- This contract chooses provider: "
        + str(c.get("this_contract_chooses_provider", False))
    )
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(
        lines,
        "1. Databento Current-Account Record",
        [
            "available_for_approved_crypto_spot: "
            + str(record.get("available_for_approved_crypto_spot", "")),
            "finding: " + str(record.get("finding", "")),
            "note: " + str(record.get("note", "")),
        ],
    )
    _emit(
        lines,
        "2. Wrong-Instrument Rejection Rules",
        list(spec.get("wrong_instrument_rejection_rules") or []),
    )
    _emit(lines, "3. Provider Criteria", list(spec.get("provider_criteria") or []))
    _emit(lines, "4. Ranking Categories", list(spec.get("ranking_categories") or []))

    rank_rows: list[str] = []
    for item in spec.get("classifications") or []:
        if isinstance(item, dict):
            rank_rows.append(
                str(item.get("name", ""))
                + " -> "
                + str(item.get("category", ""))
                + (
                    (" (" + "; ".join(item.get("reasons") or []) + ")")
                    if item.get("reasons")
                    else ""
                )
            )
    _emit(lines, "Candidate Classifications", rank_rows)
    _emit(
        lines,
        "Category Counts",
        [
            str(k) + ": " + str(v)
            for k, v in (spec.get("category_counts") or {}).items()
        ],
    )
    _emit(
        lines,
        "Approved Candidates (eligible for human choice)",
        list(spec.get("approved_candidates") or []),
    )
    _emit(
        lines,
        "5. Next Recommended Action",
        [str(spec.get("next_recommended_action", ""))],
    )
    _emit(
        lines,
        "No-Unlock Confirmation",
        [
            str(k) + ": " + str(v)
            for k, v in (spec.get("no_unlock_confirmation") or {}).items()
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)

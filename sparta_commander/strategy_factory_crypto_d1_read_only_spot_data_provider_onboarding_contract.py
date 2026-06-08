"""Crypto-D1 Read-Only Spot Data Provider Onboarding Contract (Block 146).

A PURE, stdlib-only, *read-only* CONTRACT / PLAN layer. It EVALUATES candidate
READ-ONLY historical SPOT data providers for the three missing Crypto-D1 daily
pairs (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d) and classifies each into one onboarding
category. It is the successor to Block 145's provider *selection* contract: where
145 ranked, 146 evaluates each candidate against a 10-point onboarding checklist
and emits HOLD_FOR_PROVIDER_SELECTION.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

THIS contract executes NOTHING. It does NOT call any provider, fetch data, open a
network, read or inspect any credential, read a .env file, print / store / log any
secret, connect a provider, write any file (no cache, no manifest, no gap report),
run QA / baseline / backtest / simulation, touch any broker / exchange / trading /
account / order / portfolio endpoint, or unlock any gate. It only reasons over a
static, caller-supplied (or default) list of candidate provider descriptors and
emits a deterministic evaluation plus a single recommended next action.

WHAT THE CONTRACT DOES (and nothing else):
  1. Evaluates each candidate against the 10-point onboarding checklist
     (spot coverage / read-only historical / no trading API / no account control /
     no execution endpoints / clear license / approved-future-only local cache /
     approved-future-only manifest report / secrets hidden / reviewable before any
     future API call).
  2. Explicitly REJECTS wrong-instrument substitution -- in particular, CME crypto
     FUTURES (and any futures-only provider) must never substitute SPOT.
  3. Classifies each candidate into exactly one onboarding category:
     APPROVED_CANDIDATE_FOR_REVIEW / NEEDS_PROVIDER_REVIEW /
     REJECTED_WRONG_INSTRUMENT / REJECTED_TRADING_ENDPOINT_RISK /
     REJECTED_INSUFFICIENT_COVERAGE / REJECTED_LICENSE_OR_SOURCE_UNCLEAR.
  4. Records the approved-FUTURE-only cache path and manifest report path (recorded
     as strings; NOTHING is written and no path is created).
  5. Emits the next recommended action: HOLD_FOR_PROVIDER_SELECTION (a human still
     selects among approved-for-review candidates; the contract selects nothing).
  6. Keeps every gate blocked / locked.

CORE RULE: evaluating providers authorizes nothing, selects nothing, calls
nothing, and crosses no real-world boundary. No data is fetched, no API is called,
no network is opened, no credential is read, and no .env is read. real_data_qa
stays BLOCKED, baseline stays BLOCKED, and paper / micro-live stay LOCKED.
Selecting, connecting, and provisioning a real provider is a SEPARATE, future,
human-approved action OUTSIDE this contract.

Public API:
  - ONBOARDING_SCHEMA_VERSION / ONBOARDING_LABEL / ONBOARDING_STATUS / ONBOARDING_MODE
  - ONBOARDING_CORE_RULE / MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - ONBOARDING_APPROVED_SYMBOLS / ONBOARDING_APPROVED_TIMEFRAMES
  - CATEGORY_APPROVED_CANDIDATE_FOR_REVIEW / CATEGORY_NEEDS_PROVIDER_REVIEW /
    CATEGORY_REJECTED_WRONG_INSTRUMENT / CATEGORY_REJECTED_TRADING_ENDPOINT_RISK /
    CATEGORY_REJECTED_INSUFFICIENT_COVERAGE /
    CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR / ONBOARDING_CATEGORIES
  - NEXT_RECOMMENDED_ACTION
  - ONBOARDING_EVALUATION_CRITERIA / ONBOARDING_WRONG_INSTRUMENT_REJECTION_RULES
  - ONBOARDING_APPROVED_FUTURE_CACHE_PATH / ONBOARDING_APPROVED_FUTURE_REPORT_DIR
  - DEFAULT_PROVIDER_CANDIDATES / ONBOARDING_SAFETY_POSTURE / DEFAULT_ONBOARDING_INPUT
  - evaluate_provider_candidate(descriptor)
  - build_crypto_d1_read_only_spot_data_provider_onboarding_contract(payload=None)
  - validate_crypto_d1_read_only_spot_data_provider_onboarding_contract(contract)
  - render_crypto_d1_read_only_spot_data_provider_onboarding_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    FETCH_APPROVED_SYMBOLS,
    FETCH_APPROVED_TIMEFRAMES,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

ONBOARDING_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_read_only_spot_data_provider_onboarding_contract.v1"
)
ONBOARDING_LABEL = (
    "Block 146 - Crypto-D1 Read-Only Spot Data Provider Onboarding Contract"
)
ONBOARDING_STATUS = "PROVIDER_ONBOARDING_PLAN_ONLY"
ONBOARDING_MODE = "RESEARCH_ONLY"

ONBOARDING_CORE_RULE = (
    "Evaluating candidate read-only historical SPOT data providers authorizes "
    "nothing, selects nothing, calls nothing, and crosses no real-world boundary. "
    "No data is fetched, no API is called, no network is opened, no credential is "
    "read, and no .env is read. Selecting, connecting, and provisioning a real "
    "provider is a SEPARATE, future, human-approved action. real_data_qa stays "
    "BLOCKED, baseline stays BLOCKED, and paper / micro-live stay LOCKED."
)

ONBOARDING_APPROVED_SYMBOLS: tuple[str, ...] = FETCH_APPROVED_SYMBOLS
ONBOARDING_APPROVED_TIMEFRAMES: tuple[str, ...] = FETCH_APPROVED_TIMEFRAMES

# Onboarding categories (six).
CATEGORY_APPROVED_CANDIDATE_FOR_REVIEW = "APPROVED_CANDIDATE_FOR_REVIEW"
CATEGORY_NEEDS_PROVIDER_REVIEW = "NEEDS_PROVIDER_REVIEW"
CATEGORY_REJECTED_WRONG_INSTRUMENT = "REJECTED_WRONG_INSTRUMENT"
CATEGORY_REJECTED_TRADING_ENDPOINT_RISK = "REJECTED_TRADING_ENDPOINT_RISK"
CATEGORY_REJECTED_INSUFFICIENT_COVERAGE = "REJECTED_INSUFFICIENT_COVERAGE"
CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR = "REJECTED_LICENSE_OR_SOURCE_UNCLEAR"
ONBOARDING_CATEGORIES: tuple[str, ...] = (
    CATEGORY_APPROVED_CANDIDATE_FOR_REVIEW,
    CATEGORY_NEEDS_PROVIDER_REVIEW,
    CATEGORY_REJECTED_WRONG_INSTRUMENT,
    CATEGORY_REJECTED_TRADING_ENDPOINT_RISK,
    CATEGORY_REJECTED_INSUFFICIENT_COVERAGE,
    CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR,
)

# The single next recommended action this contract emits.
NEXT_RECOMMENDED_ACTION = "HOLD_FOR_PROVIDER_SELECTION"

# Approved FUTURE-only paths. Recorded as strings; NOTHING is written here and no
# path is created. A future, separately-approved workflow could write under these.
ONBOARDING_APPROVED_FUTURE_CACHE_PATH = "data/crypto_d1_spot_cache/"
ONBOARDING_APPROVED_FUTURE_REPORT_DIR = "reports/research_os/data_qa/"

# The 10-point onboarding checklist (evaluation criteria).
ONBOARDING_EVALUATION_CRITERIA: tuple[str, ...] = (
    "Supports BTCUSD@1d, ETHUSD@1d, SOLUSD@1d or clean equivalent spot USD daily "
    "pairs.",
    "Is read-only historical market data only.",
    "Does not require trading API access.",
    "Does not require broker / exchange account control.",
    "Does not expose order placement, portfolio control, paper / live trading, or "
    "execution endpoints.",
    "Has clear source / license metadata.",
    "Allows local cache storage under an approved future path only "
    "(data/crypto_d1_spot_cache/).",
    "Allows manifest / gap report under an approved future report path only "
    "(reports/research_os/data_qa/).",
    "Keeps secrets hidden and never prints / logs / stores credentials.",
    "Can be reviewed before any future API call.",
)

# Wrong-instrument rejection rules (explicit).
ONBOARDING_WRONG_INSTRUMENT_REJECTION_RULES: tuple[str, ...] = (
    "CME crypto FUTURES (and any futures-only provider) must never be substituted "
    "for BTCUSD / ETHUSD / SOLUSD SPOT. Futures are a different instrument with "
    "different prices, expiries, and settlement -- not a clean spot daily series.",
    "Any non-spot or derivative instrument presented as a substitute for the "
    "approved spot pairs is REJECTED_WRONG_INSTRUMENT.",
    "Only genuine spot USD pairs (or a clean spot equivalent) are eligible.",
)

# Default static candidate descriptors -- illustrative ARCHETYPES, one per the
# candidate kinds the contract must be able to evaluate. They name no chosen vendor
# and commit to nothing. Each is classified deterministically by the criteria.
DEFAULT_PROVIDER_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "name": "clear_license_read_only_spot_historical_provider_archetype",
        "kind": "historical_market_data",
        "instrument": "BTCUSD / ETHUSD / SOLUSD spot daily bars",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "requires_trading_endpoint": False,
        "requires_account_endpoint": False,
        "requires_order_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_execution_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": True,
        "requires_source_review": False,
        "allows_local_cache_storage": True,
        "allows_manifest_report": True,
        "reviewable_before_api_call": True,
        "available_on_current_account": True,
        "is_wrong_instrument_substitute": False,
    },
    {
        "name": "unclear_license_spot_provider_archetype",
        "kind": "historical_market_data",
        "instrument": "BTCUSD / ETHUSD / SOLUSD spot daily bars (license unclear)",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "requires_trading_endpoint": False,
        "requires_account_endpoint": False,
        "requires_order_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_execution_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": False,
        "requires_source_review": False,
        "allows_local_cache_storage": True,
        "allows_manifest_report": True,
        "reviewable_before_api_call": True,
        "available_on_current_account": True,
        "is_wrong_instrument_substitute": False,
    },
    {
        "name": "exchange_trading_api_provider_archetype",
        "kind": "exchange_api",
        "instrument": "BTCUSD / ETHUSD / SOLUSD spot via an exchange trading API",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "requires_trading_endpoint": True,
        "requires_account_endpoint": True,
        "requires_order_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_execution_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": True,
        "requires_source_review": False,
        "allows_local_cache_storage": True,
        "allows_manifest_report": True,
        "reviewable_before_api_call": True,
        "available_on_current_account": True,
        "is_wrong_instrument_substitute": False,
    },
    {
        "name": "futures_only_provider_archetype",
        "kind": "futures",
        "instrument": "CME / crypto FUTURES only -- not spot",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "requires_trading_endpoint": False,
        "requires_account_endpoint": False,
        "requires_order_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_execution_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": True,
        "requires_source_review": False,
        "allows_local_cache_storage": True,
        "allows_manifest_report": True,
        "reviewable_before_api_call": True,
        "available_on_current_account": True,
        "is_wrong_instrument_substitute": True,
    },
    {
        "name": "aggregator_provider_archetype",
        "kind": "aggregator",
        "instrument": "BTCUSD / ETHUSD / SOLUSD spot aggregated from many sources",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "requires_trading_endpoint": False,
        "requires_account_endpoint": False,
        "requires_order_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_execution_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": True,
        "requires_source_review": True,
        "allows_local_cache_storage": True,
        "allows_manifest_report": True,
        "reviewable_before_api_call": True,
        "available_on_current_account": True,
        "is_wrong_instrument_substitute": False,
    },
    {
        "name": "csv_manual_import_provider_archetype",
        "kind": "manual_import",
        "instrument": "BTCUSD / ETHUSD / SOLUSD spot daily bars via CSV import",
        "read_only_historical": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
        "daily_timeframe": True,
        "requires_trading_endpoint": False,
        "requires_account_endpoint": False,
        "requires_order_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_execution_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": True,
        "requires_source_review": False,
        "allows_local_cache_storage": True,
        "allows_manifest_report": True,
        "reviewable_before_api_call": True,
        "available_on_current_account": True,
        "is_wrong_instrument_substitute": False,
    },
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
        "requires_execution_endpoint": False,
        "exposes_secret": False,
        "has_license_metadata": True,
        "requires_source_review": False,
        "allows_local_cache_storage": True,
        "allows_manifest_report": True,
        "reviewable_before_api_call": True,
        "available_on_current_account": False,
        "is_wrong_instrument_substitute": False,
    },
)

# Top-level flags that, if truthy on an operator's input, mark it unsafe.
ONBOARDING_FORBIDDEN_FLAGS: tuple[str, ...] = (
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
    "connect_provider_now",
    "choose_provider_now",
    "select_provider_now",
    "write_cache_now",
    "write_manifest_now",
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "place_order",
    "go_live",
)

# Execution / promotion verbs the authored NARRATIVE must never contain as whole
# words.
ONBOARDING_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Read-only safety posture. Posture facts are True; every capability flag is False.
ONBOARDING_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "human_selection_required": True,
    "executes": False,
    "performs_data_fetch": False,
    "calls_provider_api": False,
    "connects_provider": False,
    "uses_network": False,
    "fetches_data": False,
    "downloads_data": False,
    "checks_live_credentials": False,
    "reads_dotenv": False,
    "exposes_secret": False,
    "reads_data_files": False,
    "writes_data_files": False,
    "writes_cache": False,
    "writes_manifest": False,
    "writes_gap_report": False,
    "writes_reports": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "runs_qa": False,
    "runs_backtest": False,
    "runs_simulation": False,
    "chooses_provider": False,
    "selects_provider": False,
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
DEFAULT_ONBOARDING_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 provider onboarding contract input (static sample)",
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
# evaluation
# --------------------------------------------------------------------------- #
def evaluate_provider_candidate(descriptor: Any) -> dict[str, Any]:
    """Evaluate (read-only) ONE candidate provider descriptor against the 10-point
    onboarding checklist and classify it into exactly one onboarding category.
    Pure: reads only the static descriptor; calls nothing."""
    d = _as_payload(descriptor)
    name = str(d.get("name", "")) or "unnamed_candidate"

    approved = set(ONBOARDING_APPROVED_SYMBOLS)
    covers = _as_str_set(d.get("covers_symbols"))
    covers_all_symbols = bool(
        approved <= covers or _is_truthy(d.get("covers_equivalent_spot_usd"))
    )
    daily_ok = _is_truthy(d.get("daily_timeframe"))
    read_only_ok = _is_truthy(d.get("read_only_historical"))
    no_trading_endpoint = not _is_truthy(d.get("requires_trading_endpoint"))
    no_account_control = not _is_truthy(d.get("requires_account_endpoint"))
    no_order_endpoint = not _is_truthy(d.get("requires_order_endpoint"))
    no_portfolio_endpoint = not _is_truthy(d.get("requires_portfolio_endpoint"))
    no_execution_endpoint = not _is_truthy(d.get("requires_execution_endpoint"))
    no_execution_endpoints = (
        no_order_endpoint and no_portfolio_endpoint and no_execution_endpoint
    )
    no_secret_exposure = not _is_truthy(d.get("exposes_secret"))
    has_license = _is_truthy(d.get("has_license_metadata"))
    allows_cache = _is_truthy(d.get("allows_local_cache_storage", True))
    allows_manifest = _is_truthy(d.get("allows_manifest_report", True))
    reviewable = _is_truthy(d.get("reviewable_before_api_call", True))
    requires_source_review = _is_truthy(d.get("requires_source_review"))
    available = _is_truthy(d.get("available_on_current_account", True))
    wrong_instrument = _is_truthy(
        d.get("is_wrong_instrument_substitute")
    ) or _is_truthy(d.get("is_crypto_futures_substitute"))

    criteria = {
        "covers_all_symbols": covers_all_symbols,
        "read_only_historical_ok": read_only_ok,
        "no_trading_endpoint": no_trading_endpoint,
        "no_account_control": no_account_control,
        "no_execution_endpoints": no_execution_endpoints,
        "has_clear_license_metadata": has_license,
        "allows_local_cache_under_approved_path": allows_cache,
        "allows_manifest_gap_report_under_approved_path": allows_manifest,
        "no_secret_exposure": no_secret_exposure,
        "reviewable_before_api_call": reviewable,
        "available_for_approved_pairs": available,
        "wrong_instrument_substitute": wrong_instrument,
    }

    needs_review = requires_source_review or not (
        allows_cache and allows_manifest and reviewable
    )

    reasons: list[str] = []
    # Priority: wrong instrument -> endpoint / safety risk -> coverage ->
    # license / source unclear -> needs review -> approved for review.
    if wrong_instrument:
        category = CATEGORY_REJECTED_WRONG_INSTRUMENT
        reasons.append(
            "Non-spot / derivative instrument (e.g. crypto futures) offered as a "
            "substitute for the approved spot pairs."
        )
    elif not (
        read_only_ok
        and no_trading_endpoint
        and no_account_control
        and no_execution_endpoints
        and no_secret_exposure
    ):
        category = CATEGORY_REJECTED_TRADING_ENDPOINT_RISK
        if not read_only_ok:
            reasons.append("Not read-only historical (execution-capable).")
        if not no_trading_endpoint:
            reasons.append("Requires trading API access.")
        if not no_account_control:
            reasons.append("Requires broker / exchange account control.")
        if not no_execution_endpoints:
            reasons.append(
                "Exposes order placement / portfolio control / execution endpoint."
            )
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
        category = CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR
        reasons.append(
            "Meets data criteria but lacks clear source / license metadata."
        )
    elif needs_review:
        category = CATEGORY_NEEDS_PROVIDER_REVIEW
        if requires_source_review:
            reasons.append(
                "Aggregated / multi-source provider whose underlying sources need "
                "human review before it can be an approved candidate."
            )
        if not allows_cache:
            reasons.append(
                "Does not permit local cache storage under the approved future path."
            )
        if not allows_manifest:
            reasons.append(
                "Does not permit a manifest / gap report under the approved future "
                "report path."
            )
        if not reviewable:
            reasons.append("Cannot be reviewed before a future API call.")
    else:
        category = CATEGORY_APPROVED_CANDIDATE_FOR_REVIEW
        reasons.append(
            "Meets every onboarding criterion: read-only historical spot, covers "
            "the approved pairs at daily resolution, no trading / account / "
            "execution endpoint, clear license metadata, approved-future-only "
            "cache + manifest, no secret exposure, reviewable before any API call. "
            "Eligible for human selection (not selected by this contract)."
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
def build_crypto_d1_read_only_spot_data_provider_onboarding_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the provider onboarding contract. Every capability
    flag is False and every gate lock is True regardless of input. The contract
    selects no provider; the next recommended action is always
    HOLD_FOR_PROVIDER_SELECTION."""
    data = (
        dict(DEFAULT_ONBOARDING_INPUT) if payload is None else _as_payload(payload)
    )

    mf_stage = data.get("mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE)
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_flag_hits = [
        f for f in ONBOARDING_FORBIDDEN_FLAGS if _is_truthy(data.get(f))
    ]
    safe = mission_flow_aligned and not forbidden_flag_hits

    candidates = data.get("candidates")
    if not isinstance(candidates, (list, tuple)) or not candidates:
        candidates = DEFAULT_PROVIDER_CANDIDATES

    evaluations = [evaluate_provider_candidate(c) for c in candidates]
    by_category: dict[str, list[str]] = {cat: [] for cat in ONBOARDING_CATEGORIES}
    for item in evaluations:
        by_category.setdefault(item["category"], []).append(item["name"])
    category_counts = {
        cat: len(by_category.get(cat, [])) for cat in ONBOARDING_CATEGORIES
    }
    approved_candidates_for_review = list(
        by_category.get(CATEGORY_APPROVED_CANDIDATE_FOR_REVIEW, [])
    )

    spec = {
        "evaluation_criteria": list(ONBOARDING_EVALUATION_CRITERIA),
        "wrong_instrument_rejection_rules": list(
            ONBOARDING_WRONG_INSTRUMENT_REJECTION_RULES
        ),
        "ranking_categories": list(ONBOARDING_CATEGORIES),
        "evaluations": evaluations,
        "by_category": by_category,
        "category_counts": category_counts,
        "approved_candidates_for_review": approved_candidates_for_review,
        "next_recommended_action": NEXT_RECOMMENDED_ACTION,
        # approved FUTURE-only paths -- recorded only; nothing written / created.
        "approved_future_cache_path": ONBOARDING_APPROVED_FUTURE_CACHE_PATH,
        "approved_future_report_dir": ONBOARDING_APPROVED_FUTURE_REPORT_DIR,
        "no_write_confirmation": {
            "writes_cache": False,
            "writes_manifest": False,
            "writes_gap_report": False,
            "approved_paths_are_future_only": True,
            "paths_created_now": False,
        },
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
        "schema_version": ONBOARDING_SCHEMA_VERSION,
        "label": ONBOARDING_LABEL,
        "status": ONBOARDING_STATUS,
        "mode": ONBOARDING_MODE,
        "core_rule": ONBOARDING_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": mission_flow_aligned,
        "safe": safe,
        "forbidden_flag_hits": list(forbidden_flag_hits),
        "approved_symbols": list(ONBOARDING_APPROVED_SYMBOLS),
        "approved_timeframes": list(ONBOARDING_APPROVED_TIMEFRAMES),
        "onboarding_contract": spec,
        "next_recommended_action": NEXT_RECOMMENDED_ACTION,
        "onboarding_summary": (
            "Read-only evaluation of candidate historical SPOT data providers for "
            "the missing Crypto-D1 pairs (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d). Each "
            "candidate is scored against the 10-point onboarding checklist; "
            "futures-only and trading-API providers are rejected, unclear-license "
            "providers are rejected, aggregators need review. THIS contract "
            "evaluates only -- it fetches nothing, calls no API, connects no "
            "provider, selects no provider, writes nothing, and unlocks no gate."
        ),
        "operator_next_step": (
            "A human reviews this evaluation and, as a SEPARATE action, decides "
            "whether to select and provision one of the approved-for-review "
            "candidates. Reviewing this evaluation acquires no data, calls no "
            "provider, writes nothing, and unlocks no gate; the recommended next "
            "action is HOLD_FOR_PROVIDER_SELECTION."
        ),
        "human_operator_required_next_steps": [
            "A human reviews this read-only provider evaluation.",
            "A human separately selects whether to onboard an approved-for-review "
            "candidate and provision its read-only access OUTSIDE this contract.",
            "Only after a separate human-approved onboarding could a future "
            "read-only fetch be planned; this contract writes nothing and unlocks "
            "no gate.",
        ],
        "requires_human_provider_selection": True,
        "this_contract_chooses_provider": False,
        "this_contract_calls_provider": False,
        "this_contract_fetches_data": False,
        "safety_posture": dict(ONBOARDING_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "read_only": True,
        "research_only": True,
        "executes": False,
        "performs_data_fetch": False,
        "calls_provider_api": False,
        "connects_provider": False,
        "uses_network": False,
        "fetches_data": False,
        "downloads_data": False,
        "checks_live_credentials": False,
        "reads_dotenv": False,
        "exposes_secret": False,
        "reads_data_files": False,
        "writes_data_files": False,
        "writes_cache": False,
        "writes_manifest": False,
        "writes_gap_report": False,
        "writes_reports": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
        "runs_qa": False,
        "runs_backtest": False,
        "runs_simulation": False,
        "chooses_provider": False,
        "selects_provider": False,
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
    "onboarding_contract",
    "next_recommended_action",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_REQUIRED_SPEC_KEYS: tuple[str, ...] = (
    "evaluation_criteria",
    "wrong_instrument_rejection_rules",
    "ranking_categories",
    "evaluations",
    "by_category",
    "category_counts",
    "approved_candidates_for_review",
    "next_recommended_action",
    "approved_future_cache_path",
    "approved_future_report_dir",
    "no_write_confirmation",
    "no_unlock_confirmation",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "performs_data_fetch",
    "calls_provider_api",
    "connects_provider",
    "uses_network",
    "fetches_data",
    "downloads_data",
    "checks_live_credentials",
    "reads_dotenv",
    "exposes_secret",
    "reads_data_files",
    "writes_data_files",
    "writes_cache",
    "writes_manifest",
    "writes_gap_report",
    "writes_reports",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
    "runs_qa",
    "runs_backtest",
    "runs_simulation",
    "chooses_provider",
    "selects_provider",
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


def validate_crypto_d1_read_only_spot_data_provider_onboarding_contract(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built onboarding contract. Returns a verdict dict of
    boolean checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing_fields = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == ONBOARDING_SCHEMA_VERSION
    label_ok = c.get("label") == ONBOARDING_LABEL
    status_ok = c.get("status") == ONBOARDING_STATUS
    mode_ok = c.get("mode") == ONBOARDING_MODE
    core_rule_ok = c.get("core_rule") == ONBOARDING_CORE_RULE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    performs_fetch_false = c.get("performs_data_fetch") is False
    chooses_provider_false = c.get("chooses_provider") is False
    this_chooses_false = c.get("this_contract_chooses_provider") is False
    this_calls_false = c.get("this_contract_calls_provider") is False
    this_fetches_false = c.get("this_contract_fetches_data") is False
    human_selection_required = c.get("requires_human_provider_selection") is True
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == ONBOARDING_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
    )
    next_action_ok = c.get("next_recommended_action") == NEXT_RECOMMENDED_ACTION

    spec = c.get("onboarding_contract")
    spec_is_dict = isinstance(spec, dict)
    spec_keys_ok = spec_is_dict and all(k in spec for k in _REQUIRED_SPEC_KEYS)

    categories_ok = spec_is_dict and spec.get("ranking_categories") == list(
        ONBOARDING_CATEGORIES
    )
    evaluations = spec.get("evaluations") if spec_is_dict else None
    evaluations_valid = isinstance(evaluations, list) and bool(evaluations) and all(
        isinstance(x, dict) and x.get("category") in ONBOARDING_CATEGORIES
        for x in evaluations
    )

    wir = spec.get("wrong_instrument_rejection_rules") if spec_is_dict else None
    wrong_instrument_rule_present = isinstance(wir, list) and bool(wir)
    futures_rejected_ok = isinstance(evaluations, list) and all(
        x.get("category") == CATEGORY_REJECTED_WRONG_INSTRUMENT
        for x in evaluations
        if isinstance(x, dict)
        and x.get("criteria", {}).get("wrong_instrument_substitute") is True
    )

    criteria_present = spec_is_dict and bool(spec.get("evaluation_criteria"))
    criteria_count_ok = spec_is_dict and len(
        spec.get("evaluation_criteria") or []
    ) >= 10
    next_action_in_spec_ok = spec_is_dict and spec.get(
        "next_recommended_action"
    ) == NEXT_RECOMMENDED_ACTION

    approved_paths_ok = (
        spec_is_dict
        and spec.get("approved_future_cache_path")
        == ONBOARDING_APPROVED_FUTURE_CACHE_PATH
        and spec.get("approved_future_report_dir")
        == ONBOARDING_APPROVED_FUTURE_REPORT_DIR
    )

    nwc = spec.get("no_write_confirmation") if spec_is_dict else None
    no_write_ok = isinstance(nwc, dict) and (
        nwc.get("writes_cache") is False
        and nwc.get("writes_manifest") is False
        and nwc.get("writes_gap_report") is False
        and nwc.get("approved_paths_are_future_only") is True
        and nwc.get("paths_created_now") is False
    )

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
        for k in ("operator_next_step", "onboarding_summary", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(ONBOARDING_FORBIDDEN_TRADE_TERMS))

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
        "this_calls_false": this_calls_false,
        "this_fetches_false": this_fetches_false,
        "human_selection_required": human_selection_required,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "next_action_ok": next_action_ok,
        "spec_keys_ok": spec_keys_ok,
        "categories_ok": categories_ok,
        "evaluations_valid": evaluations_valid,
        "wrong_instrument_rule_present": wrong_instrument_rule_present,
        "futures_rejected_ok": futures_rejected_ok,
        "criteria_present": criteria_present,
        "criteria_count_ok": criteria_count_ok,
        "next_action_in_spec_ok": next_action_in_spec_ok,
        "approved_paths_ok": approved_paths_ok,
        "no_write_ok": no_write_ok,
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


def render_crypto_d1_read_only_spot_data_provider_onboarding_contract_markdown(
    contract: Any,
) -> str:
    """Render a built onboarding contract as a deterministic markdown brief. Pure
    string formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    spec = c.get("onboarding_contract") or {}
    lines: list[str] = []
    lines.append(
        "# Crypto-D1 Read-Only Spot Data Provider Onboarding Contract"
    )
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
    lines.append(
        "- This contract calls provider: "
        + str(c.get("this_contract_calls_provider", False))
    )
    lines.append(
        "- This contract fetches data: "
        + str(c.get("this_contract_fetches_data", False))
    )
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(
        lines,
        "1. Onboarding Evaluation Criteria",
        list(spec.get("evaluation_criteria") or []),
    )
    _emit(
        lines,
        "2. Wrong-Instrument Rejection Rules",
        list(spec.get("wrong_instrument_rejection_rules") or []),
    )
    _emit(
        lines,
        "3. Onboarding Categories",
        list(spec.get("ranking_categories") or []),
    )

    rank_rows: list[str] = []
    for item in spec.get("evaluations") or []:
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
    _emit(lines, "Candidate Evaluations", rank_rows)
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
        "Approved Candidates For Review (eligible for human selection)",
        list(spec.get("approved_candidates_for_review") or []),
    )
    _emit(
        lines,
        "Approved FUTURE-Only Paths (recorded only; nothing written)",
        [
            "cache: " + str(spec.get("approved_future_cache_path", "")),
            "report: " + str(spec.get("approved_future_report_dir", "")),
        ],
    )
    _emit(
        lines,
        "4. Next Recommended Action",
        [str(spec.get("next_recommended_action", ""))],
    )
    _emit(
        lines,
        "No-Write Confirmation",
        [
            str(k) + ": " + str(v)
            for k, v in (spec.get("no_write_confirmation") or {}).items()
        ],
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

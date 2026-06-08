"""Automated Read-Only Crypto-D1 Spot Data Source Acquisition Orchestrator (Block 148).

A PURE, stdlib-only, *read-only* ORCHESTRATION / PLAN layer. Given a static,
caller-supplied (or default) list of candidate provider / source *descriptors*
(metadata only -- NEVER file contents, NEVER a live endpoint), it AUTOMATICALLY
ranks and selects the SAFEST source path for the three missing Crypto-D1 daily SPOT
pairs (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d) and emits a human-approval packet.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

Selection ranking (safest first):
  1. clear-license READ-ONLY spot historical provider
  2. manual CSV import (if no safe API provider exists)
  3. hold (if no safe source exists)

Rejection rules (a candidate in any of these is never selectable):
  - trading API providers
  - broker / exchange account APIs
  - futures / perps offered as a spot substitute
  - unclear license / source
  - providers requiring order / account / portfolio access

THIS orchestrator executes NOTHING. Even when a caller passes human_run_approved,
it does NOT fetch, import, read a file, write a file, call a provider, open a
network, read a credential / .env, run QA / baseline / backtest, touch a broker /
exchange / order endpoint, or unlock a gate. Automating the *choice* and the
*approval packet* is all this layer does; the actual run is a SEPARATE, future,
human-approved action OUTSIDE this contract. real_data_qa stays BLOCKED, baseline
stays BLOCKED, and paper / micro-live stay LOCKED.

Public API:
  - ORCH_SCHEMA_VERSION / ORCH_LABEL / ORCH_STATUS / ORCH_MODE / ORCH_CORE_RULE
  - MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - ORCH_REQUIRED_SYMBOLS / ORCH_REQUIRED_TIMEFRAMES / ORCH_SYMBOL_ALIASES
  - CATEGORY_ELIGIBLE_CLEAR_LICENSE_API / CATEGORY_ELIGIBLE_MANUAL_CSV /
    CATEGORY_NEEDS_SOURCE_REVIEW / CATEGORY_REJECTED_TRADING_API /
    CATEGORY_REJECTED_BROKER_ACCOUNT_API / CATEGORY_REJECTED_WRONG_INSTRUMENT /
    CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR /
    CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS / ORCH_CATEGORIES
  - SELECTED_TYPE_CLEAR_LICENSE_API / SELECTED_TYPE_MANUAL_CSV / SELECTED_TYPE_HOLD
  - NEXT_ACTION_API / NEXT_ACTION_CSV / NEXT_ACTION_HOLD
  - ORCH_ALLOWED_PATHS / ORCH_FORBIDDEN_PATHS / ORCH_HARD_STOP_RULES
  - ORCH_SCOPED_TESTS / DEFAULT_SOURCE_CANDIDATES / ORCH_SAFETY_POSTURE
  - evaluate_source_candidate(descriptor)
  - orchestrate_crypto_d1_spot_data_source_acquisition(payload=None)
  - build_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator(payload=None)
  - validate_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator(contract)
  - render_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    FETCH_APPROVED_SYMBOLS,
    FETCH_APPROVED_TIMEFRAMES,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

ORCH_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator.v1"
)
ORCH_LABEL = (
    "Block 148 - Automated Read-Only Crypto-D1 Spot Data Source Acquisition Orchestrator"
)
ORCH_STATUS = "AUTOMATED_SOURCE_SELECTION_ONLY"
ORCH_MODE = "RESEARCH_ONLY"

ORCH_CORE_RULE = (
    "Automating the source CHOICE and the human-approval PACKET authorizes nothing "
    "and runs nothing. No API is called, no network is opened, no data is fetched, "
    "no CSV is imported, no file content is read, no file is written, no credential "
    "is read, and no .env is read -- even when human_run_approved is passed. The "
    "actual read-only acquisition run is a SEPARATE, future, human-approved action "
    "OUTSIDE this orchestrator. real_data_qa stays BLOCKED, baseline stays BLOCKED, "
    "and paper / micro-live stay LOCKED."
)

ORCH_REQUIRED_SYMBOLS: tuple[str, ...] = FETCH_APPROVED_SYMBOLS
ORCH_REQUIRED_TIMEFRAMES: tuple[str, ...] = FETCH_APPROVED_TIMEFRAMES

# Acceptable written forms for each required symbol (normalized by removing the
# slash / dash and upper-casing -- e.g. "BTC/USD" -> "BTCUSD").
ORCH_SYMBOL_ALIASES: dict[str, tuple[str, ...]] = {
    "BTCUSD": ("BTCUSD", "BTC/USD", "BTC-USD", "XBTUSD"),
    "ETHUSD": ("ETHUSD", "ETH/USD", "ETH-USD"),
    "SOLUSD": ("SOLUSD", "SOL/USD", "SOL-USD"),
}

# Per-candidate evaluation categories (eight).
CATEGORY_ELIGIBLE_CLEAR_LICENSE_API = "ELIGIBLE_CLEAR_LICENSE_API"
CATEGORY_ELIGIBLE_MANUAL_CSV = "ELIGIBLE_MANUAL_CSV"
CATEGORY_NEEDS_SOURCE_REVIEW = "NEEDS_SOURCE_REVIEW"
CATEGORY_REJECTED_TRADING_API = "REJECTED_TRADING_API"
CATEGORY_REJECTED_BROKER_ACCOUNT_API = "REJECTED_BROKER_ACCOUNT_API"
CATEGORY_REJECTED_WRONG_INSTRUMENT = "REJECTED_WRONG_INSTRUMENT"
CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR = "REJECTED_LICENSE_OR_SOURCE_UNCLEAR"
CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS = "REJECTED_REQUIRES_ACCOUNT_ACCESS"
ORCH_CATEGORIES: tuple[str, ...] = (
    CATEGORY_ELIGIBLE_CLEAR_LICENSE_API,
    CATEGORY_ELIGIBLE_MANUAL_CSV,
    CATEGORY_NEEDS_SOURCE_REVIEW,
    CATEGORY_REJECTED_TRADING_API,
    CATEGORY_REJECTED_BROKER_ACCOUNT_API,
    CATEGORY_REJECTED_WRONG_INSTRUMENT,
    CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR,
    CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS,
)

# Selected source-path types (the orchestrator's automatic choice).
SELECTED_TYPE_CLEAR_LICENSE_API = "CLEAR_LICENSE_READ_ONLY_SPOT_HISTORICAL_PROVIDER"
SELECTED_TYPE_MANUAL_CSV = "MANUAL_CSV_IMPORT"
SELECTED_TYPE_HOLD = "HOLD_NO_SAFE_SOURCE"

# Next recommended action per selected type.
NEXT_ACTION_API = "HOLD_FOR_HUMAN_RUN_APPROVAL_OF_SELECTED_READ_ONLY_PROVIDER"
NEXT_ACTION_CSV = "HOLD_FOR_MANUAL_CSV_IMPORT_APPROVAL"
NEXT_ACTION_HOLD = "HOLD_NO_SAFE_SOURCE_AVAILABLE"

# Approved FUTURE-only paths (recorded only; NOTHING is written / read / created).
ORCH_ALLOWED_PATHS: tuple[str, ...] = (
    "data/manual_import_candidates/crypto_d1/",
    "data/crypto_d1_spot_cache/",
    "reports/research_os/data_qa/",
)

# Paths / boundaries this orchestrator (and any future run) must never cross.
ORCH_FORBIDDEN_PATHS: tuple[str, ...] = (
    "any write outside the approved future paths",
    "any credential store / .env / secret file",
    "any broker / exchange / trading / order / account / portfolio endpoint",
    "any live or paper trading runtime",
    "any runtime / dashboard output path",
    "any gate-unlock or mission-flow status mutation",
)

# Hard stops -- if any are true, the orchestrator selects HOLD and runs nothing.
ORCH_HARD_STOP_RULES: tuple[str, ...] = (
    "trading API / order endpoint detected in a candidate.",
    "broker / exchange account API detected in a candidate.",
    "futures / perps offered as a spot substitute.",
    "unclear source / license.",
    "candidate requires order / account / portfolio access.",
    "any attempt to fetch / import / read file contents / write / call a provider.",
    "any gate unlock attempt.",
    "any QA / backtest / paper / live attempt.",
)

# The single scoped test file for this block.
ORCH_SCOPED_TESTS: tuple[str, ...] = (
    "tests/test_strategy_factory_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator.py",
)

# Default static candidate SOURCE DESCRIPTORS (metadata only -- NEVER file contents,
# NEVER a live endpoint). Illustrative archetypes; each is classified
# deterministically by the rules below.
DEFAULT_SOURCE_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "name": "clear_license_readonly_spot_history_api_archetype",
        "endpoint_type": "read_only_historical",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "read_only_historical": True,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_clear_license_metadata": True,
        "requires_trading_endpoint": False,
        "requires_order_endpoint": False,
        "requires_account_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_account_access": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "manual_csv_import_archetype",
        "endpoint_type": "manual_import",
        "kind": "manual_import",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "read_only_historical": True,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_clear_license_metadata": True,
        "requires_trading_endpoint": False,
        "requires_order_endpoint": False,
        "requires_account_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_account_access": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "exchange_trading_api_archetype",
        "endpoint_type": "trading_api",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "read_only_historical": True,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_clear_license_metadata": True,
        "requires_trading_endpoint": True,
        "requires_order_endpoint": False,
        "requires_account_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_account_access": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "broker_account_api_archetype",
        "endpoint_type": "broker_account_api",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "read_only_historical": True,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_clear_license_metadata": True,
        "requires_trading_endpoint": False,
        "requires_order_endpoint": False,
        "requires_account_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_account_access": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "futures_substitute_api_archetype",
        "endpoint_type": "read_only_historical",
        "instrument": "futures",
        "is_futures_or_perp": True,
        "read_only_historical": True,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_clear_license_metadata": True,
        "requires_trading_endpoint": False,
        "requires_order_endpoint": False,
        "requires_account_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_account_access": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "unclear_license_api_archetype",
        "endpoint_type": "read_only_historical",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "read_only_historical": True,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_clear_license_metadata": False,
        "requires_trading_endpoint": False,
        "requires_order_endpoint": False,
        "requires_account_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_account_access": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "portfolio_access_api_archetype",
        "endpoint_type": "read_only_historical",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "read_only_historical": True,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_clear_license_metadata": True,
        "requires_trading_endpoint": False,
        "requires_order_endpoint": False,
        "requires_account_endpoint": False,
        "requires_portfolio_endpoint": True,
        "requires_account_access": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "incomplete_coverage_spot_api_archetype",
        "endpoint_type": "read_only_historical",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "read_only_historical": True,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_clear_license_metadata": True,
        "requires_trading_endpoint": False,
        "requires_order_endpoint": False,
        "requires_account_endpoint": False,
        "requires_portfolio_endpoint": False,
        "requires_account_access": False,
        "covers_symbols": ["BTCUSD"],
    },
)

# Top-level flags that, if truthy on an operator's input, mark it unsafe.
ORCH_FORBIDDEN_FLAGS: tuple[str, ...] = (
    "authorizes_trading",
    "authorizes_paper_trading",
    "authorizes_live_trading",
    "authorizes_broker_exchange",
    "authorizes_order_placement",
    "authorizes_account_control",
    "authorizes_portfolio_control",
    "authorizes_strategy_promotion",
    "authorizes_automation_trading",
    "authorizes_qa_baseline",
    "unlocks_downstream_gate",
    "print_credentials",
    "expose_secret",
    "inspect_dotenv",
    "fetch_data_now",
    "run_acquisition_now",
    "call_provider_now",
    "import_csv_now",
    "read_file_contents_now",
    "write_cache_now",
    "write_report_now",
    "run_qa_now",
    "run_backtest_now",
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "place_order",
    "go_live",
)

# Execution / promotion verbs the authored NARRATIVE must never contain as whole
# words.
ORCH_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Read-only safety posture. Posture facts are True; every capability flag is False.
ORCH_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "automated_selection_only": True,
    "human_run_required": True,
    "executes": False,
    "performs_data_fetch": False,
    "performs_data_import": False,
    "imports_csv": False,
    "reads_file_contents": False,
    "calls_provider_api": False,
    "connects_provider": False,
    "uses_network": False,
    "fetches_data": False,
    "checks_live_credentials": False,
    "reads_dotenv": False,
    "exposes_secret": False,
    "reads_data_files": False,
    "writes_data_files": False,
    "writes_cache": False,
    "writes_report": False,
    "writes_runtime_outputs": False,
    "writes_dashboard_outputs": False,
    "runs_validation": False,
    "runs_qa": False,
    "runs_backtest": False,
    "runs_simulation": False,
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
DEFAULT_ORCH_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 automated source-selection orchestrator input (static sample)",
    "mode": "RESEARCH_ONLY",
    "read_only": True,
    "executes": False,
    "human_run_approved": False,
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


def _normalize_symbol(value: Any) -> str:
    out: list[str] = []
    for ch in str(value).upper():
        if ch.isalnum():
            out.append(ch)
    return "".join(out)


def _covers_required_symbols(value: Any) -> bool:
    if not isinstance(value, (list, tuple, set)):
        return False
    present = {_normalize_symbol(v) for v in value if str(v).strip()}
    for canonical, aliases in ORCH_SYMBOL_ALIASES.items():
        accepted = {_normalize_symbol(a) for a in aliases}
        if not (present & accepted):
            return False
    return True


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
def evaluate_source_candidate(descriptor: Any) -> dict[str, Any]:
    """Evaluate (read-only) ONE candidate provider / source *descriptor* (metadata
    only -- NEVER file contents, NEVER a live endpoint) and classify it into exactly
    one category. Pure: reads only the static descriptor; reads no file, calls
    nothing.

    Priority (safety-first): trading API -> broker/exchange account API ->
    order/account/portfolio access -> futures/perps -> unclear license -> manual
    CSV (eligible) -> clean read-only spot API (eligible) -> structural gaps
    (needs review)."""
    d = _as_payload(descriptor)
    name = str(d.get("name", "")) or "unnamed_source"
    endpoint = str(d.get("endpoint_type", "")).strip().lower()
    kind = str(d.get("kind", "")).strip().lower()

    requires_trading = _is_truthy(d.get("requires_trading_endpoint")) or (
        endpoint in {"trading_api", "exchange_trading_api", "order_api"}
    )
    requires_broker_account_api = endpoint in {
        "broker_account_api",
        "exchange_account_api",
        "account_api",
    }
    requires_account_access = (
        _is_truthy(d.get("requires_order_endpoint"))
        or _is_truthy(d.get("requires_account_endpoint"))
        or _is_truthy(d.get("requires_portfolio_endpoint"))
        or _is_truthy(d.get("requires_account_access"))
    )
    is_futures_or_perp = _is_truthy(d.get("is_futures_or_perp")) or (
        str(d.get("instrument", "")).strip().lower() in {"futures", "perp", "perps"}
    )
    has_license = _is_truthy(d.get("has_clear_license_metadata"))
    read_only_historical = _is_truthy(d.get("read_only_historical"))
    usd_ok = _is_truthy(d.get("usd_quote_or_mappable"))
    daily_ok = _is_truthy(d.get("daily_timeframe"))
    covers_required = _covers_required_symbols(d.get("covers_symbols"))
    is_manual_csv = kind == "manual_import" or endpoint == "manual_import"

    criteria = {
        "read_only_historical": read_only_historical,
        "spot_not_futures": not is_futures_or_perp,
        "usd_quote_or_mappable": usd_ok,
        "daily_timeframe": daily_ok,
        "has_clear_license_metadata": has_license,
        "no_trading_endpoint": not requires_trading,
        "no_broker_account_api": not requires_broker_account_api,
        "no_account_access_required": not requires_account_access,
        "covers_required_symbols": covers_required,
        "is_manual_csv": is_manual_csv,
        "is_futures_or_perp": is_futures_or_perp,
        "requires_trading_endpoint": requires_trading,
        "requires_broker_account_api": requires_broker_account_api,
        "requires_account_access": requires_account_access,
    }

    reasons: list[str] = []
    if requires_trading:
        category = CATEGORY_REJECTED_TRADING_API
        reasons.append("Trading API / order endpoint -- not a read-only data source.")
    elif requires_broker_account_api:
        category = CATEGORY_REJECTED_BROKER_ACCOUNT_API
        reasons.append("Broker / exchange account API -- not a read-only data source.")
    elif requires_account_access:
        category = CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS
        reasons.append(
            "Requires order / account / portfolio access to obtain data."
        )
    elif is_futures_or_perp:
        category = CATEGORY_REJECTED_WRONG_INSTRUMENT
        reasons.append("Futures / perps offered as a spot substitute -- not spot.")
    elif not has_license:
        category = CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR
        reasons.append("Unclear source / license metadata.")
    elif is_manual_csv and (usd_ok and daily_ok and covers_required):
        category = CATEGORY_ELIGIBLE_MANUAL_CSV
        reasons.append(
            "Clean manual CSV import path: clear license, spot, USD-or-mappable, "
            "daily, covers required symbols. Eligible for a FUTURE human-approved "
            "import (not imported by this orchestrator)."
        )
    elif (
        read_only_historical
        and usd_ok
        and daily_ok
        and covers_required
    ):
        category = CATEGORY_ELIGIBLE_CLEAR_LICENSE_API
        reasons.append(
            "Clear-license READ-ONLY spot historical provider: no trading / account "
            "endpoints, spot, USD-or-mappable, daily, covers required symbols. "
            "Eligible for a FUTURE human-approved read-only run (not run by this "
            "orchestrator)."
        )
    else:
        category = CATEGORY_NEEDS_SOURCE_REVIEW
        if not read_only_historical and not is_manual_csv:
            reasons.append("Read-only historical access not confirmed.")
        if not usd_ok:
            reasons.append("USD quote / mappable USD spot pair not confirmed.")
        if not daily_ok:
            reasons.append("Daily (1d) timeframe not confirmed.")
        if not covers_required:
            reasons.append(
                "Does not clearly cover BTCUSD / ETHUSD / SOLUSD (or accepted "
                "aliases)."
            )

    return {
        "name": name,
        "endpoint_type": str(d.get("endpoint_type", "")),
        "instrument": str(d.get("instrument", "")),
        "category": category,
        "criteria": criteria,
        "reasons": reasons,
    }


def _select_source_path(evaluations: list[dict[str, Any]]) -> dict[str, Any]:
    """Automatic, deterministic ranking: clear-license API first, else manual CSV,
    else hold. Returns the selected type / name / reason / next action."""
    api = [
        e for e in evaluations
        if e.get("category") == CATEGORY_ELIGIBLE_CLEAR_LICENSE_API
    ]
    csv = [
        e for e in evaluations
        if e.get("category") == CATEGORY_ELIGIBLE_MANUAL_CSV
    ]
    if api:
        chosen = api[0]
        return {
            "selected_candidate_type": SELECTED_TYPE_CLEAR_LICENSE_API,
            "selected_candidate_name": chosen.get("name"),
            "reason": (
                "Ranked safest: a clear-license READ-ONLY spot historical provider "
                "is available. Selecting it for a FUTURE human-approved read-only "
                "run; nothing is fetched now."
            ),
            "next_recommended_action": NEXT_ACTION_API,
        }
    if csv:
        chosen = csv[0]
        return {
            "selected_candidate_type": SELECTED_TYPE_MANUAL_CSV,
            "selected_candidate_name": chosen.get("name"),
            "reason": (
                "No safe read-only API provider available; falling back to the "
                "lower-risk manual CSV import path for a FUTURE human-approved "
                "import. Nothing is imported now."
            ),
            "next_recommended_action": NEXT_ACTION_CSV,
        }
    return {
        "selected_candidate_type": SELECTED_TYPE_HOLD,
        "selected_candidate_name": None,
        "reason": (
            "No safe source available: every candidate is rejected or needs review. "
            "Holding; nothing is fetched, imported, or unlocked."
        ),
        "next_recommended_action": NEXT_ACTION_HOLD,
    }


# --------------------------------------------------------------------------- #
# orchestration (selection + approval packet)
# --------------------------------------------------------------------------- #
def orchestrate_crypto_d1_spot_data_source_acquisition(
    payload: Any = None,
) -> dict[str, Any]:
    """Automatically rank / select the safest source path and emit the required
    outputs (selection + human-approval packet). Pure: imports nothing, runs
    nothing, fetches nothing -- even if human_run_approved is truthy."""
    data = dict(DEFAULT_ORCH_INPUT) if payload is None else _as_payload(payload)

    candidates = data.get("candidates")
    if not isinstance(candidates, (list, tuple)) or not candidates:
        candidates = DEFAULT_SOURCE_CANDIDATES

    evaluations = [evaluate_source_candidate(c) for c in candidates]
    by_category: dict[str, list[str]] = {cat: [] for cat in ORCH_CATEGORIES}
    for item in evaluations:
        by_category.setdefault(item["category"], []).append(item["name"])
    category_counts = {cat: len(by_category.get(cat, [])) for cat in ORCH_CATEGORIES}

    selection = _select_source_path(evaluations)

    # human_run_approved is ECHOED only. It NEVER causes a fetch / run here -- the
    # actual run is a separate, future block. run_executed is always False.
    human_run_approved = _is_truthy(data.get("human_run_approved"))

    approval_packet = {
        "selected_candidate_type": selection["selected_candidate_type"],
        "selected_candidate_name": selection["selected_candidate_name"],
        "target_symbols": list(ORCH_REQUIRED_SYMBOLS),
        "target_timeframes": list(ORCH_REQUIRED_TIMEFRAMES),
        "human_run_approval_required": True,
        "human_run_approved_flag_name": "human_run_approved",
        "human_run_approved_echo": human_run_approved,
        "run_executed": False,
        "run_performed_by_this_block": False,
        "performed_action": "AUTOMATED_SOURCE_SELECTION_ONLY",
        "what_a_human_must_approve": (
            "A SEPARATE, future block performs the read-only acquisition run for the "
            "selected source only after an explicit human_run_approved decision. "
            "This orchestrator fetches / imports nothing and unlocks no gate."
        ),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
    }

    return {
        "selected_candidate_type": selection["selected_candidate_type"],
        "selected_candidate_name": selection["selected_candidate_name"],
        "reason": selection["reason"],
        "required_human_approval_packet": approval_packet,
        "allowed_paths": list(ORCH_ALLOWED_PATHS),
        "forbidden_paths": list(ORCH_FORBIDDEN_PATHS),
        "scoped_tests": list(ORCH_SCOPED_TESTS),
        "hard_stop_rules": list(ORCH_HARD_STOP_RULES),
        "next_recommended_action": selection["next_recommended_action"],
        "categories": list(ORCH_CATEGORIES),
        "evaluations": evaluations,
        "by_category": by_category,
        "category_counts": category_counts,
        "human_run_approved_echo": human_run_approved,
        "run_executed": False,
    }


# --------------------------------------------------------------------------- #
# contract build
# --------------------------------------------------------------------------- #
def build_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the orchestrator contract. Every capability flag is
    False and every gate lock is True regardless of input -- including when
    human_run_approved is passed. The orchestrator runs nothing."""
    data = dict(DEFAULT_ORCH_INPUT) if payload is None else _as_payload(payload)

    mf_stage = data.get("mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE)
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_flag_hits = [
        f for f in ORCH_FORBIDDEN_FLAGS if _is_truthy(data.get(f))
    ]
    safe = mission_flow_aligned and not forbidden_flag_hits

    orchestration = orchestrate_crypto_d1_spot_data_source_acquisition(data)

    contract: dict[str, Any] = {
        "schema_version": ORCH_SCHEMA_VERSION,
        "label": ORCH_LABEL,
        "status": ORCH_STATUS,
        "mode": ORCH_MODE,
        "core_rule": ORCH_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": mission_flow_aligned,
        "safe": safe,
        "forbidden_flag_hits": list(forbidden_flag_hits),
        "orchestration": orchestration,
        # promoted top-level required outputs (mirror orchestration)
        "selected_candidate_type": orchestration["selected_candidate_type"],
        "selected_candidate_name": orchestration["selected_candidate_name"],
        "reason": orchestration["reason"],
        "required_human_approval_packet": orchestration[
            "required_human_approval_packet"
        ],
        "allowed_paths": orchestration["allowed_paths"],
        "forbidden_paths": orchestration["forbidden_paths"],
        "scoped_tests": orchestration["scoped_tests"],
        "hard_stop_rules": orchestration["hard_stop_rules"],
        "next_recommended_action": orchestration["next_recommended_action"],
        "orchestrator_summary": (
            "Read-only AUTOMATED source-selection orchestrator for the missing "
            "Crypto-D1 spot pairs (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d). It ranks "
            "candidate source descriptors (metadata only), automatically selects "
            "the safest path (clear-license read-only API > manual CSV > hold), and "
            "emits a human-approval packet. THIS orchestrator selects only -- it "
            "fetches nothing, imports nothing, reads no file contents, writes "
            "nothing, and unlocks no gate, even when human_run_approved is passed."
        ),
        "operator_next_step": (
            "A human reviews the selected source and the approval packet and, as a "
            "SEPARATE action, decides whether to authorize a future read-only "
            "acquisition run via an explicit human_run_approved decision. Reviewing "
            "this selection fetches no data, imports nothing, reads no file, writes "
            "nothing, and unlocks no gate."
        ),
        "human_operator_required_next_steps": [
            "A human reviews this read-only source selection and approval packet.",
            "A human separately authorizes a future read-only acquisition run for "
            "the selected source OUTSIDE this orchestrator.",
            "Only after a separate human-approved run + validation step could real "
            "spot data exist; this orchestrator fetches nothing and unlocks no gate.",
        ],
        "requires_human_run": True,
        "this_orchestrator_fetches_data": False,
        "this_orchestrator_imports_csv": False,
        "this_orchestrator_reads_file_contents": False,
        "this_orchestrator_writes_files": False,
        "this_orchestrator_runs_acquisition": False,
        "human_run_approved_echo": orchestration["human_run_approved_echo"],
        "run_executed": False,
        "safety_posture": dict(ORCH_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "read_only": True,
        "research_only": True,
        "executes": False,
        "performs_data_fetch": False,
        "performs_data_import": False,
        "imports_csv": False,
        "reads_file_contents": False,
        "calls_provider_api": False,
        "connects_provider": False,
        "uses_network": False,
        "fetches_data": False,
        "checks_live_credentials": False,
        "reads_dotenv": False,
        "exposes_secret": False,
        "reads_data_files": False,
        "writes_data_files": False,
        "writes_cache": False,
        "writes_report": False,
        "writes_runtime_outputs": False,
        "writes_dashboard_outputs": False,
        "runs_validation": False,
        "runs_qa": False,
        "runs_backtest": False,
        "runs_simulation": False,
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
    "orchestration",
    "selected_candidate_type",
    "reason",
    "required_human_approval_packet",
    "allowed_paths",
    "forbidden_paths",
    "scoped_tests",
    "hard_stop_rules",
    "next_recommended_action",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_REQUIRED_ORCH_KEYS: tuple[str, ...] = (
    "selected_candidate_type",
    "selected_candidate_name",
    "reason",
    "required_human_approval_packet",
    "allowed_paths",
    "forbidden_paths",
    "scoped_tests",
    "hard_stop_rules",
    "next_recommended_action",
    "categories",
    "evaluations",
    "by_category",
    "category_counts",
    "run_executed",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "performs_data_fetch",
    "performs_data_import",
    "imports_csv",
    "reads_file_contents",
    "calls_provider_api",
    "connects_provider",
    "uses_network",
    "fetches_data",
    "checks_live_credentials",
    "reads_dotenv",
    "exposes_secret",
    "reads_data_files",
    "writes_data_files",
    "writes_cache",
    "writes_report",
    "writes_runtime_outputs",
    "writes_dashboard_outputs",
    "runs_validation",
    "runs_qa",
    "runs_backtest",
    "runs_simulation",
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

_VALID_SELECTED_TYPES: tuple[str, ...] = (
    SELECTED_TYPE_CLEAR_LICENSE_API,
    SELECTED_TYPE_MANUAL_CSV,
    SELECTED_TYPE_HOLD,
)

_VALID_NEXT_ACTIONS: tuple[str, ...] = (
    NEXT_ACTION_API,
    NEXT_ACTION_CSV,
    NEXT_ACTION_HOLD,
)


def validate_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built orchestrator contract. Returns a verdict dict of
    boolean checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing_fields = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == ORCH_SCHEMA_VERSION
    label_ok = c.get("label") == ORCH_LABEL
    status_ok = c.get("status") == ORCH_STATUS
    mode_ok = c.get("mode") == ORCH_MODE
    core_rule_ok = c.get("core_rule") == ORCH_CORE_RULE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    fetches_false = c.get("fetches_data") is False
    this_fetches_false = c.get("this_orchestrator_fetches_data") is False
    this_imports_false = c.get("this_orchestrator_imports_csv") is False
    this_reads_false = c.get("this_orchestrator_reads_file_contents") is False
    this_writes_false = c.get("this_orchestrator_writes_files") is False
    this_runs_false = c.get("this_orchestrator_runs_acquisition") is False
    run_executed_false = c.get("run_executed") is False
    human_run_required = c.get("requires_human_run") is True
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == ORCH_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
    )

    selected_type_ok = c.get("selected_candidate_type") in _VALID_SELECTED_TYPES
    next_action_ok = c.get("next_recommended_action") in _VALID_NEXT_ACTIONS

    orch = c.get("orchestration")
    orch_is_dict = isinstance(orch, dict)
    orch_keys_ok = orch_is_dict and all(k in orch for k in _REQUIRED_ORCH_KEYS)

    allowed_paths_ok = c.get("allowed_paths") == list(ORCH_ALLOWED_PATHS)
    forbidden_paths_present = isinstance(c.get("forbidden_paths"), list) and len(
        c.get("forbidden_paths") or []
    ) >= 6
    scoped_tests_ok = c.get("scoped_tests") == list(ORCH_SCOPED_TESTS)
    hard_stops_present = isinstance(c.get("hard_stop_rules"), list) and len(
        c.get("hard_stop_rules") or []
    ) >= 6

    categories_ok = orch_is_dict and orch.get("categories") == list(ORCH_CATEGORIES)
    evaluations = orch.get("evaluations") if orch_is_dict else None
    evaluations_valid = isinstance(evaluations, list) and bool(evaluations) and all(
        isinstance(x, dict) and x.get("category") in ORCH_CATEGORIES
        for x in evaluations
    )

    # No trading API, broker/account API, account-access, or futures candidate may
    # ever be selected (i.e. it must be REJECTED).
    unsafe_never_selected_ok = isinstance(evaluations, list) and all(
        str(x.get("category", "")).startswith("REJECTED")
        for x in evaluations
        if isinstance(x, dict)
        and (
            x.get("criteria", {}).get("requires_trading_endpoint") is True
            or x.get("criteria", {}).get("requires_broker_account_api") is True
            or x.get("criteria", {}).get("requires_account_access") is True
            or x.get("criteria", {}).get("is_futures_or_perp") is True
        )
    )

    # The selected name (if any) must NOT correspond to a rejected candidate.
    selected_name = c.get("selected_candidate_name")
    selected_is_safe = True
    if selected_name and isinstance(evaluations, list):
        for x in evaluations:
            if isinstance(x, dict) and x.get("name") == selected_name:
                selected_is_safe = str(x.get("category", "")).startswith("ELIGIBLE")
                break

    packet = c.get("required_human_approval_packet")
    packet_ok = isinstance(packet, dict) and (
        packet.get("human_run_approval_required") is True
        and packet.get("run_executed") is False
        and packet.get("run_performed_by_this_block") is False
        and packet.get("real_data_qa_state") == "BLOCKED"
        and packet.get("baseline_backtest_state") == "BLOCKED"
        and packet.get("paper_live_state") == "LOCKED"
    )

    no_secret_value_fields = not _has_secret_value(c)

    guidance_blob = " ".join(
        str(c.get(k, ""))
        for k in ("operator_next_step", "orchestrator_summary", "core_rule", "reason")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(ORCH_FORBIDDEN_TRADE_TERMS))

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "status_ok": status_ok,
        "mode_ok": mode_ok,
        "core_rule_ok": core_rule_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "fetches_false": fetches_false,
        "this_fetches_false": this_fetches_false,
        "this_imports_false": this_imports_false,
        "this_reads_false": this_reads_false,
        "this_writes_false": this_writes_false,
        "this_runs_false": this_runs_false,
        "run_executed_false": run_executed_false,
        "human_run_required": human_run_required,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "selected_type_ok": selected_type_ok,
        "next_action_ok": next_action_ok,
        "orch_keys_ok": orch_keys_ok,
        "allowed_paths_ok": allowed_paths_ok,
        "forbidden_paths_present": forbidden_paths_present,
        "scoped_tests_ok": scoped_tests_ok,
        "hard_stops_present": hard_stops_present,
        "categories_ok": categories_ok,
        "evaluations_valid": evaluations_valid,
        "unsafe_never_selected_ok": unsafe_never_selected_ok,
        "selected_is_safe": selected_is_safe,
        "packet_ok": packet_ok,
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


def render_crypto_d1_automated_read_only_spot_data_source_acquisition_orchestrator_markdown(
    contract: Any,
) -> str:
    """Render a built orchestrator contract as a deterministic markdown brief. Pure
    string formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    orch = c.get("orchestration") or {}
    packet = c.get("required_human_approval_packet") or {}
    lines: list[str] = []
    lines.append(
        "# Automated Read-Only Crypto-D1 Spot Data Source Acquisition Orchestrator"
    )
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Selected candidate type: " + str(c.get("selected_candidate_type", ""))
    )
    lines.append(
        "- Selected candidate name: " + str(c.get("selected_candidate_name", ""))
    )
    lines.append("- Reason: " + str(c.get("reason", "")))
    lines.append(
        "- Next recommended action: " + str(c.get("next_recommended_action", ""))
    )
    lines.append(
        "- This orchestrator fetches data: "
        + str(c.get("this_orchestrator_fetches_data", False))
    )
    lines.append("- Run executed: " + str(c.get("run_executed", False)))
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(
        lines,
        "Required Human Approval Packet",
        [str(k) + ": " + str(v) for k, v in packet.items()],
    )
    _emit(lines, "Allowed Paths (future-only; nothing written)", list(c.get("allowed_paths") or []))
    _emit(lines, "Forbidden Paths", list(c.get("forbidden_paths") or []))
    _emit(lines, "Scoped Tests", list(c.get("scoped_tests") or []))
    _emit(lines, "Hard Stop Rules", list(c.get("hard_stop_rules") or []))

    rank_rows: list[str] = []
    for item in orch.get("evaluations") or []:
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
    _emit(lines, "Candidate Source Evaluations", rank_rows)
    _emit(
        lines,
        "Category Counts",
        [
            str(k) + ": " + str(v)
            for k, v in (orch.get("category_counts") or {}).items()
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)

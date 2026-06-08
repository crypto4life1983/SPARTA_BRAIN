"""Crypto-D1 Manual CSV Spot Data Import Plan Contract (Block 147).

A PURE, stdlib-only, *read-only* CONTRACT / PLAN layer. It DEFINES the requirements
and the validation plan for a FUTURE, human-performed manual CSV import of the
three missing Crypto-D1 daily SPOT pairs (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d). It is
the lowest-risk path coming out of the Block 146 onboarding evaluation: the
CSV / manual-import provider archetype was APPROVED_CANDIDATE_FOR_REVIEW.

    MISSION_FLOW_CURRENT_STAGE = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION_REQUIRED
    MISSION_FLOW_NEXT_ACTION   = HUMAN_CONTROLLED_REAL_DATA_QA_BOUNDARY_DECISION

THIS contract executes NOTHING. It does NOT import a CSV, read or parse any file's
contents, write any file, call any provider, open a network, read or inspect any
credential, read a .env file, print / store / log any secret, run validation / QA /
baseline / backtest / simulation, touch any broker / exchange / trading / account /
order endpoint, or unlock any gate. It only reasons over a static, caller-supplied
(or default) list of candidate CSV *source descriptors* (metadata only -- NEVER
file contents) and emits a deterministic import plan.

WHAT THE CONTRACT DOES (and nothing else):
  1. Defines the required CSV source criteria (clear license, spot not futures,
     USD-or-mappable quote, daily timeframe, OHLCV columns, dated column).
  2. Records the required symbols (BTCUSD / ETHUSD / SOLUSD) and required columns
     (date / open / high / low / close / volume).
  3. Defines the rejection rules (futures / perps, trading-export account/order
     fields, unclear license, broker/exchange account access, intraday-only).
  4. Records the approved FUTURE-only import paths (input candidate folder,
     validated output, report dir) as strings -- NOTHING is written or created.
  5. Defines the future validation checks (schema / symbol+timeframe / duplicate
     date / missing-date gap / OHLC sanity / volume sanity / source+license).
  6. Lists the hard stops.
  7. Evaluates each candidate source descriptor into exactly one category.
  8. Keeps every gate blocked / locked.

CORE RULE: planning a manual import authorizes nothing, imports nothing, reads no
file contents, writes nothing, and crosses no real-world boundary. real_data_qa
stays BLOCKED, baseline stays BLOCKED, and paper / micro-live stay LOCKED. The
actual import, validation, and caching is a SEPARATE, future, human-approved action
OUTSIDE this contract.

Public API:
  - IMPORT_SCHEMA_VERSION / IMPORT_LABEL / IMPORT_STATUS / IMPORT_MODE
  - IMPORT_CORE_RULE / MISSION_FLOW_CURRENT_STAGE / MISSION_FLOW_NEXT_REQUIRED_ACTION
  - IMPORT_REQUIRED_SYMBOLS / IMPORT_REQUIRED_TIMEFRAMES / IMPORT_REQUIRED_COLUMNS
  - IMPORT_SYMBOL_ALIASES
  - CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT / CATEGORY_NEEDS_SOURCE_REVIEW /
    CATEGORY_REJECTED_WRONG_INSTRUMENT / CATEGORY_REJECTED_TRADING_EXPORT /
    CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR /
    CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS / CATEGORY_REJECTED_INTRADAY_ONLY /
    IMPORT_CATEGORIES
  - NEXT_RECOMMENDED_ACTION
  - IMPORT_SOURCE_CRITERIA / IMPORT_REJECTION_RULES / IMPORT_VALIDATION_CHECKS /
    IMPORT_HARD_STOPS
  - IMPORT_INPUT_CANDIDATE_PATH / IMPORT_VALIDATED_OUTPUT_PATH / IMPORT_REPORT_DIR
  - DEFAULT_CSV_SOURCE_CANDIDATES / IMPORT_SAFETY_POSTURE / DEFAULT_IMPORT_INPUT
  - evaluate_csv_source_descriptor(descriptor)
  - build_crypto_d1_manual_csv_spot_data_import_plan_contract(payload=None)
  - validate_crypto_d1_manual_csv_spot_data_import_plan_contract(contract)
  - render_crypto_d1_manual_csv_spot_data_import_plan_contract_markdown(contract)
"""

from __future__ import annotations

from typing import Any

from sparta_commander.strategy_factory_crypto_d1_databento_read_only_fetch_execution_contract import (  # noqa: E501
    FETCH_APPROVED_SYMBOLS,
    FETCH_APPROVED_TIMEFRAMES,
    MISSION_FLOW_CURRENT_STAGE,
    MISSION_FLOW_NEXT_REQUIRED_ACTION,
)

IMPORT_SCHEMA_VERSION = (
    "strategy_factory_crypto_d1_manual_csv_spot_data_import_plan_contract.v1"
)
IMPORT_LABEL = (
    "Block 147 - Crypto-D1 Manual CSV Spot Data Import Plan Contract"
)
IMPORT_STATUS = "MANUAL_CSV_IMPORT_PLAN_ONLY"
IMPORT_MODE = "RESEARCH_ONLY"

IMPORT_CORE_RULE = (
    "Planning a manual CSV import authorizes nothing, imports nothing, reads no "
    "file contents, writes nothing, and crosses no real-world boundary. No CSV is "
    "imported, no file is read or parsed, no file is written, no API is called, no "
    "network is opened, no credential is read, and no .env is read. The actual "
    "import, validation, and caching is a SEPARATE, future, human-approved action. "
    "real_data_qa stays BLOCKED, baseline stays BLOCKED, and paper / micro-live "
    "stay LOCKED."
)

IMPORT_REQUIRED_SYMBOLS: tuple[str, ...] = FETCH_APPROVED_SYMBOLS
IMPORT_REQUIRED_TIMEFRAMES: tuple[str, ...] = FETCH_APPROVED_TIMEFRAMES
IMPORT_REQUIRED_COLUMNS: tuple[str, ...] = (
    "date",
    "open",
    "high",
    "low",
    "close",
    "volume",
)

# Acceptable written forms for each required symbol (normalized by removing the
# slash and upper-casing -- e.g. "BTC/USD" -> "BTCUSD").
IMPORT_SYMBOL_ALIASES: dict[str, tuple[str, ...]] = {
    "BTCUSD": ("BTCUSD", "BTC/USD", "BTC-USD", "XBTUSD"),
    "ETHUSD": ("ETHUSD", "ETH/USD", "ETH-USD"),
    "SOLUSD": ("SOLUSD", "SOL/USD", "SOL-USD"),
}

# Evaluation categories (seven).
CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT = "ACCEPTED_FOR_FUTURE_IMPORT"
CATEGORY_NEEDS_SOURCE_REVIEW = "NEEDS_SOURCE_REVIEW"
CATEGORY_REJECTED_WRONG_INSTRUMENT = "REJECTED_WRONG_INSTRUMENT"
CATEGORY_REJECTED_TRADING_EXPORT = "REJECTED_TRADING_EXPORT"
CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR = "REJECTED_LICENSE_OR_SOURCE_UNCLEAR"
CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS = "REJECTED_REQUIRES_ACCOUNT_ACCESS"
CATEGORY_REJECTED_INTRADAY_ONLY = "REJECTED_INTRADAY_ONLY"
IMPORT_CATEGORIES: tuple[str, ...] = (
    CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT,
    CATEGORY_NEEDS_SOURCE_REVIEW,
    CATEGORY_REJECTED_WRONG_INSTRUMENT,
    CATEGORY_REJECTED_TRADING_EXPORT,
    CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR,
    CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS,
    CATEGORY_REJECTED_INTRADAY_ONLY,
)

# The single next recommended action this contract emits.
NEXT_RECOMMENDED_ACTION = "HOLD_FOR_MANUAL_CSV_IMPORT_APPROVAL"

# 1. Required CSV source criteria.
IMPORT_SOURCE_CRITERIA: tuple[str, ...] = (
    "Clear public / source / license metadata.",
    "Spot market, not futures / perps.",
    "USD quote or a clearly mappable USD spot pair.",
    "Daily (1d) timeframe.",
    "OHLCV columns or a mappable equivalent.",
    "Date column with a clear timezone / date format.",
)

# 4. Rejection rules.
IMPORT_REJECTION_RULES: tuple[str, ...] = (
    "Reject futures / perps as a wrong-instrument substitute for spot.",
    "Reject trading-export files that carry account / order / trade fields.",
    "Reject files with unclear license / source.",
    "Reject files that require broker / exchange account access.",
    "Reject intraday-only files unless explicitly aggregated to daily in a future "
    "approved step.",
)

# 6. Future validation checks (run only in a separate, future approved step).
IMPORT_VALIDATION_CHECKS: tuple[str, ...] = (
    "schema_check: required columns present or mappable.",
    "symbol_timeframe_check: symbol is BTCUSD / ETHUSD / SOLUSD and timeframe is "
    "1d.",
    "duplicate_date_check: no duplicate dates.",
    "missing_date_gap_check: no unexpected missing dates / gaps.",
    "ohlc_sanity_check: low <= open/close <= high and non-negative prices.",
    "volume_sanity_check: non-negative volume, no absurd outliers.",
    "source_license_check: license / source metadata is recorded and clear.",
)

# 7. Hard stops.
IMPORT_HARD_STOPS: tuple[str, ...] = (
    "account / order / trade fields detected in a candidate file.",
    "futures / perps instrument detected.",
    "unclear source / license.",
    "any write outside the approved future paths.",
    "any gate unlock attempt.",
    "any QA / backtest / paper / live attempt.",
)

# 5. Approved FUTURE-only import paths. Recorded as strings; NOTHING is written /
# read / created here. A future, separately-approved workflow could use these.
IMPORT_INPUT_CANDIDATE_PATH = "data/manual_import_candidates/crypto_d1/"
IMPORT_VALIDATED_OUTPUT_PATH = "data/crypto_d1_spot_cache/"
IMPORT_REPORT_DIR = "reports/research_os/data_qa/"

# Default static candidate SOURCE DESCRIPTORS (metadata only -- NEVER file
# contents). Illustrative archetypes, one per category. They name no chosen vendor
# and read no file; each is classified deterministically by the rules above.
DEFAULT_CSV_SOURCE_CANDIDATES: tuple[dict[str, Any], ...] = (
    {
        "name": "clean_daily_spot_ohlcv_csv_archetype",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_ohlcv_columns": True,
        "has_date_column_with_format": True,
        "has_clear_license_metadata": True,
        "has_account_or_order_fields": False,
        "requires_account_access": False,
        "intraday_only": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "partial_columns_spot_csv_archetype",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_ohlcv_columns": False,
        "has_date_column_with_format": True,
        "has_clear_license_metadata": True,
        "has_account_or_order_fields": False,
        "requires_account_access": False,
        "intraday_only": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "futures_daily_csv_archetype",
        "instrument": "futures",
        "is_futures_or_perp": True,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_ohlcv_columns": True,
        "has_date_column_with_format": True,
        "has_clear_license_metadata": True,
        "has_account_or_order_fields": False,
        "requires_account_access": False,
        "intraday_only": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "exchange_trading_export_csv_archetype",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_ohlcv_columns": True,
        "has_date_column_with_format": True,
        "has_clear_license_metadata": True,
        "has_account_or_order_fields": True,
        "requires_account_access": False,
        "intraday_only": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "unclear_license_spot_csv_archetype",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_ohlcv_columns": True,
        "has_date_column_with_format": True,
        "has_clear_license_metadata": False,
        "has_account_or_order_fields": False,
        "requires_account_access": False,
        "intraday_only": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "broker_account_required_csv_archetype",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "usd_quote_or_mappable": True,
        "daily_timeframe": True,
        "has_ohlcv_columns": True,
        "has_date_column_with_format": True,
        "has_clear_license_metadata": True,
        "has_account_or_order_fields": False,
        "requires_account_access": True,
        "intraday_only": False,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
    {
        "name": "intraday_only_spot_csv_archetype",
        "instrument": "spot",
        "is_futures_or_perp": False,
        "usd_quote_or_mappable": True,
        "daily_timeframe": False,
        "has_ohlcv_columns": True,
        "has_date_column_with_format": True,
        "has_clear_license_metadata": True,
        "has_account_or_order_fields": False,
        "requires_account_access": False,
        "intraday_only": True,
        "covers_symbols": ["BTCUSD", "ETHUSD", "SOLUSD"],
    },
)

# Top-level flags that, if truthy on an operator's input, mark it unsafe.
IMPORT_FORBIDDEN_FLAGS: tuple[str, ...] = (
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
    "import_csv_now",
    "read_csv_now",
    "read_file_contents_now",
    "parse_csv_now",
    "write_cache_now",
    "write_report_now",
    "run_validation_now",
    "run_qa_now",
    "run_backtest_now",
    "call_provider_now",
    "fetch_data_now",
    "unlock_real_data_qa",
    "unlock_baseline_backtest",
    "unlock_paper_trading_gate",
    "unlock_micro_live_gate",
    "place_order",
    "go_live",
)

# Execution / promotion verbs the authored NARRATIVE must never contain as whole
# words.
IMPORT_FORBIDDEN_TRADE_TERMS: tuple[str, ...] = (
    "buy",
    "sell",
    "long",
    "short",
    "entry",
    "exit",
)

# Read-only safety posture. Posture facts are True; every capability flag is False.
IMPORT_SAFETY_POSTURE: dict[str, bool] = {
    "read_only": True,
    "research_only": True,
    "human_import_required": True,
    "executes": False,
    "performs_data_import": False,
    "imports_csv": False,
    "reads_file_contents": False,
    "reads_csv": False,
    "parses_csv": False,
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
DEFAULT_IMPORT_INPUT: dict[str, Any] = {
    "label": "Crypto-D1 manual CSV import plan contract input (static sample)",
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
    for canonical, aliases in IMPORT_SYMBOL_ALIASES.items():
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
def evaluate_csv_source_descriptor(descriptor: Any) -> dict[str, Any]:
    """Evaluate (read-only) ONE candidate CSV *source descriptor* (metadata only --
    NEVER file contents) and classify it into exactly one category. Pure: reads
    only the static descriptor; reads no file, calls nothing.

    Priority (safety-first): trading-export account/order fields -> required
    account access -> futures / perps -> unclear license -> intraday-only ->
    structural gaps (needs review) -> accepted for future import."""
    d = _as_payload(descriptor)
    name = str(d.get("name", "")) or "unnamed_csv_source"

    is_futures_or_perp = _is_truthy(d.get("is_futures_or_perp")) or (
        str(d.get("instrument", "")).strip().lower() in {"futures", "perp", "perps"}
    )
    has_account_or_order_fields = _is_truthy(d.get("has_account_or_order_fields"))
    requires_account_access = _is_truthy(d.get("requires_account_access"))
    has_license = _is_truthy(d.get("has_clear_license_metadata"))
    usd_ok = _is_truthy(d.get("usd_quote_or_mappable"))
    daily_ok = _is_truthy(d.get("daily_timeframe"))
    intraday_only = _is_truthy(d.get("intraday_only")) or (
        not daily_ok and _is_truthy(d.get("has_intraday"))
    )
    has_ohlcv = _is_truthy(d.get("has_ohlcv_columns"))
    has_date_format = _is_truthy(d.get("has_date_column_with_format"))
    covers_required = _covers_required_symbols(d.get("covers_symbols"))

    criteria = {
        "spot_not_futures": not is_futures_or_perp,
        "usd_quote_or_mappable": usd_ok,
        "daily_timeframe": daily_ok,
        "has_ohlcv_columns": has_ohlcv,
        "has_date_column_with_format": has_date_format,
        "has_clear_license_metadata": has_license,
        "no_account_or_order_fields": not has_account_or_order_fields,
        "no_account_access_required": not requires_account_access,
        "covers_required_symbols": covers_required,
        "is_futures_or_perp": is_futures_or_perp,
        "has_account_or_order_fields": has_account_or_order_fields,
    }

    reasons: list[str] = []
    if has_account_or_order_fields:
        category = CATEGORY_REJECTED_TRADING_EXPORT
        reasons.append(
            "Trading-export file carrying account / order / trade fields -- not a "
            "clean market-data CSV."
        )
    elif requires_account_access:
        category = CATEGORY_REJECTED_REQUIRES_ACCOUNT_ACCESS
        reasons.append("Requires broker / exchange account access to obtain.")
    elif is_futures_or_perp:
        category = CATEGORY_REJECTED_WRONG_INSTRUMENT
        reasons.append("Futures / perps instrument -- not clean spot.")
    elif not has_license:
        category = CATEGORY_REJECTED_LICENSE_OR_SOURCE_UNCLEAR
        reasons.append("Unclear source / license metadata.")
    elif intraday_only or not daily_ok:
        category = CATEGORY_REJECTED_INTRADAY_ONLY
        reasons.append(
            "Intraday-only / non-daily file. Eligible only if explicitly aggregated "
            "to daily in a future approved step."
        )
    elif not (usd_ok and has_ohlcv and has_date_format and covers_required):
        category = CATEGORY_NEEDS_SOURCE_REVIEW
        if not usd_ok:
            reasons.append("USD quote / mappable USD spot pair not confirmed.")
        if not has_ohlcv:
            reasons.append("OHLCV columns (or mappable equivalent) not confirmed.")
        if not has_date_format:
            reasons.append("Dated column with a clear date / timezone format not "
                           "confirmed.")
        if not covers_required:
            reasons.append(
                "Does not clearly cover BTCUSD / ETHUSD / SOLUSD (or accepted "
                "aliases)."
            )
    else:
        category = CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT
        reasons.append(
            "Meets every source criterion: clean spot, USD-or-mappable quote, "
            "daily timeframe, OHLCV + dated columns, clear license, no account / "
            "order fields, no account access required, covers the required "
            "symbols. Eligible for a FUTURE human-performed import (not imported "
            "by this contract)."
        )

    return {
        "name": name,
        "instrument": str(d.get("instrument", "")),
        "category": category,
        "criteria": criteria,
        "reasons": reasons,
    }


# --------------------------------------------------------------------------- #
# contract build
# --------------------------------------------------------------------------- #
def build_crypto_d1_manual_csv_spot_data_import_plan_contract(
    payload: Any = None,
) -> dict[str, Any]:
    """Build (fresh each call) the manual CSV import plan contract. Every capability
    flag is False and every gate lock is True regardless of input. The contract
    imports nothing; the next recommended action is always
    HOLD_FOR_MANUAL_CSV_IMPORT_APPROVAL."""
    data = dict(DEFAULT_IMPORT_INPUT) if payload is None else _as_payload(payload)

    mf_stage = data.get("mission_flow_current_stage", MISSION_FLOW_CURRENT_STAGE)
    mf_action = data.get(
        "mission_flow_next_required_action", MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    mission_flow_aligned = (
        str(mf_stage) == MISSION_FLOW_CURRENT_STAGE
        and str(mf_action) == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )

    forbidden_flag_hits = [
        f for f in IMPORT_FORBIDDEN_FLAGS if _is_truthy(data.get(f))
    ]
    safe = mission_flow_aligned and not forbidden_flag_hits

    candidates = data.get("candidates")
    if not isinstance(candidates, (list, tuple)) or not candidates:
        candidates = DEFAULT_CSV_SOURCE_CANDIDATES

    evaluations = [evaluate_csv_source_descriptor(c) for c in candidates]
    by_category: dict[str, list[str]] = {cat: [] for cat in IMPORT_CATEGORIES}
    for item in evaluations:
        by_category.setdefault(item["category"], []).append(item["name"])
    category_counts = {
        cat: len(by_category.get(cat, [])) for cat in IMPORT_CATEGORIES
    }
    accepted_for_future_import = list(
        by_category.get(CATEGORY_ACCEPTED_FOR_FUTURE_IMPORT, [])
    )

    spec = {
        # 1. required CSV source criteria
        "source_criteria": list(IMPORT_SOURCE_CRITERIA),
        # 2. required symbols + timeframe
        "required_symbols": list(IMPORT_REQUIRED_SYMBOLS),
        "required_timeframes": list(IMPORT_REQUIRED_TIMEFRAMES),
        "symbol_aliases": {k: list(v) for k, v in IMPORT_SYMBOL_ALIASES.items()},
        # 3. required columns
        "required_columns": list(IMPORT_REQUIRED_COLUMNS),
        # 4. rejection rules
        "rejection_rules": list(IMPORT_REJECTION_RULES),
        # 5. approved FUTURE-only import paths
        "approved_future_paths": {
            "input_candidate_path": IMPORT_INPUT_CANDIDATE_PATH,
            "validated_output_path": IMPORT_VALIDATED_OUTPUT_PATH,
            "report_dir": IMPORT_REPORT_DIR,
        },
        # 6. future validation checks
        "future_validation_checks": list(IMPORT_VALIDATION_CHECKS),
        # 7. hard stops
        "hard_stops": list(IMPORT_HARD_STOPS),
        # evaluation
        "categories": list(IMPORT_CATEGORIES),
        "evaluations": evaluations,
        "by_category": by_category,
        "category_counts": category_counts,
        "accepted_for_future_import": accepted_for_future_import,
        "next_recommended_action": NEXT_RECOMMENDED_ACTION,
        # no-write confirmation
        "no_write_confirmation": {
            "reads_file_contents": False,
            "writes_cache": False,
            "writes_report": False,
            "approved_paths_are_future_only": True,
            "paths_created_now": False,
        },
        # 8. no-unlock confirmation
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
        "schema_version": IMPORT_SCHEMA_VERSION,
        "label": IMPORT_LABEL,
        "status": IMPORT_STATUS,
        "mode": IMPORT_MODE,
        "core_rule": IMPORT_CORE_RULE,
        "mission_flow_current_stage": MISSION_FLOW_CURRENT_STAGE,
        "mission_flow_next_required_action": MISSION_FLOW_NEXT_REQUIRED_ACTION,
        "mission_flow_aligned": mission_flow_aligned,
        "safe": safe,
        "forbidden_flag_hits": list(forbidden_flag_hits),
        "import_plan": spec,
        "next_recommended_action": NEXT_RECOMMENDED_ACTION,
        "import_summary": (
            "Read-only PLAN for a FUTURE human-performed manual CSV import of the "
            "missing Crypto-D1 spot pairs (BTCUSD@1d, ETHUSD@1d, SOLUSD@1d). It "
            "defines the source criteria, required symbols / columns, rejection "
            "rules, future validation checks, hard stops, and approved-future-only "
            "paths, and classifies candidate source descriptors (metadata only). "
            "THIS contract plans only -- it imports nothing, reads no file "
            "contents, writes nothing, and unlocks no gate."
        ),
        "operator_next_step": (
            "A human reviews this plan and, as a SEPARATE action, decides whether "
            "to place an accepted-for-import CSV under the approved input candidate "
            "path and run the future validation step. Reviewing this plan imports "
            "no data, reads no file, writes nothing, and unlocks no gate; the "
            "recommended next action is HOLD_FOR_MANUAL_CSV_IMPORT_APPROVAL."
        ),
        "human_operator_required_next_steps": [
            "A human reviews this read-only import plan.",
            "A human separately provides a clean, clearly-licensed daily spot CSV "
            "under the approved input candidate path OUTSIDE this contract.",
            "Only after a separate human-approved import + validation step could "
            "the validated daily spot data exist; this contract writes nothing and "
            "unlocks no gate.",
        ],
        "requires_human_import": True,
        "this_contract_imports_csv": False,
        "this_contract_reads_file_contents": False,
        "this_contract_writes_files": False,
        "safety_posture": dict(IMPORT_SAFETY_POSTURE),
        "real_data_qa_state": "BLOCKED",
        "baseline_backtest_state": "BLOCKED",
        "paper_live_state": "LOCKED",
        "read_only": True,
        "research_only": True,
        "executes": False,
        "performs_data_import": False,
        "imports_csv": False,
        "reads_file_contents": False,
        "reads_csv": False,
        "parses_csv": False,
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
    "import_plan",
    "next_recommended_action",
    "operator_next_step",
    "safety_posture",
    "real_data_qa_state",
    "baseline_backtest_state",
    "paper_live_state",
)

_REQUIRED_SPEC_KEYS: tuple[str, ...] = (
    "source_criteria",
    "required_symbols",
    "required_timeframes",
    "required_columns",
    "rejection_rules",
    "approved_future_paths",
    "future_validation_checks",
    "hard_stops",
    "categories",
    "evaluations",
    "by_category",
    "category_counts",
    "accepted_for_future_import",
    "next_recommended_action",
    "no_write_confirmation",
    "no_unlock_confirmation",
)

_ALL_CAPABILITY_FLAGS: tuple[str, ...] = (
    "executes",
    "performs_data_import",
    "imports_csv",
    "reads_file_contents",
    "reads_csv",
    "parses_csv",
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


def validate_crypto_d1_manual_csv_spot_data_import_plan_contract(
    contract: Any,
) -> dict[str, Any]:
    """Validate (read-only) a built manual CSV import plan contract. Returns a
    verdict dict of boolean checks plus an overall `valid`."""
    c = contract if isinstance(contract, dict) else {}
    missing_fields = [f for f in _REQUIRED_CONTRACT_FIELDS if f not in c]

    schema_ok = c.get("schema_version") == IMPORT_SCHEMA_VERSION
    label_ok = c.get("label") == IMPORT_LABEL
    status_ok = c.get("status") == IMPORT_STATUS
    mode_ok = c.get("mode") == IMPORT_MODE
    core_rule_ok = c.get("core_rule") == IMPORT_CORE_RULE
    read_only = c.get("read_only") is True
    research_only = c.get("research_only") is True
    executes_false = c.get("executes") is False
    imports_csv_false = c.get("imports_csv") is False
    reads_contents_false = c.get("reads_file_contents") is False
    this_imports_false = c.get("this_contract_imports_csv") is False
    this_reads_false = c.get("this_contract_reads_file_contents") is False
    this_writes_false = c.get("this_contract_writes_files") is False
    human_import_required = c.get("requires_human_import") is True
    mission_flow_refs_ok = (
        c.get("mission_flow_current_stage") == MISSION_FLOW_CURRENT_STAGE
        and c.get("mission_flow_next_required_action")
        == MISSION_FLOW_NEXT_REQUIRED_ACTION
    )
    flags_false = all(c.get(f) is False for f in _ALL_CAPABILITY_FLAGS)
    authorizes_nothing = c.get("authorizes_nothing") is True
    gates_locked = all(c.get(g) is True for g in _ALL_GATE_LOCKS)
    posture_ok = c.get("safety_posture") == IMPORT_SAFETY_POSTURE
    states_blocked_locked = (
        c.get("real_data_qa_state") == "BLOCKED"
        and c.get("baseline_backtest_state") == "BLOCKED"
        and c.get("paper_live_state") == "LOCKED"
    )
    next_action_ok = c.get("next_recommended_action") == NEXT_RECOMMENDED_ACTION

    spec = c.get("import_plan")
    spec_is_dict = isinstance(spec, dict)
    spec_keys_ok = spec_is_dict and all(k in spec for k in _REQUIRED_SPEC_KEYS)

    criteria_present = spec_is_dict and len(spec.get("source_criteria") or []) >= 6
    columns_ok = spec_is_dict and spec.get("required_columns") == list(
        IMPORT_REQUIRED_COLUMNS
    )
    symbols_ok = spec_is_dict and spec.get("required_symbols") == list(
        IMPORT_REQUIRED_SYMBOLS
    )
    rejection_rules_present = spec_is_dict and len(
        spec.get("rejection_rules") or []
    ) >= 5
    validation_checks_present = spec_is_dict and len(
        spec.get("future_validation_checks") or []
    ) >= 7
    hard_stops_present = spec_is_dict and len(spec.get("hard_stops") or []) >= 6

    paths = spec.get("approved_future_paths") if spec_is_dict else None
    approved_paths_ok = isinstance(paths, dict) and (
        paths.get("input_candidate_path") == IMPORT_INPUT_CANDIDATE_PATH
        and paths.get("validated_output_path") == IMPORT_VALIDATED_OUTPUT_PATH
        and paths.get("report_dir") == IMPORT_REPORT_DIR
    )

    categories_ok = spec_is_dict and spec.get("categories") == list(
        IMPORT_CATEGORIES
    )
    evaluations = spec.get("evaluations") if spec_is_dict else None
    evaluations_valid = isinstance(evaluations, list) and bool(evaluations) and all(
        isinstance(x, dict) and x.get("category") in IMPORT_CATEGORIES
        for x in evaluations
    )

    # No futures / perps and no trading-export file may ever be ACCEPTED.
    futures_rejected_ok = isinstance(evaluations, list) and all(
        str(x.get("category", "")).startswith("REJECTED")
        for x in evaluations
        if isinstance(x, dict)
        and x.get("criteria", {}).get("is_futures_or_perp") is True
    )
    trading_export_rejected_ok = isinstance(evaluations, list) and all(
        str(x.get("category", "")).startswith("REJECTED")
        for x in evaluations
        if isinstance(x, dict)
        and x.get("criteria", {}).get("has_account_or_order_fields") is True
    )

    next_action_in_spec_ok = spec_is_dict and spec.get(
        "next_recommended_action"
    ) == NEXT_RECOMMENDED_ACTION

    nwc = spec.get("no_write_confirmation") if spec_is_dict else None
    no_write_ok = isinstance(nwc, dict) and (
        nwc.get("reads_file_contents") is False
        and nwc.get("writes_cache") is False
        and nwc.get("writes_report") is False
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
        for k in ("operator_next_step", "import_summary", "core_rule")
    )
    guidance_blob += " " + " ".join(
        str(s) for s in (c.get("human_operator_required_next_steps") or [])
    )
    tokens = set(_tokenize(guidance_blob))
    no_trade_language = not (tokens & set(IMPORT_FORBIDDEN_TRADE_TERMS))

    checks = {
        "schema_ok": schema_ok,
        "label_ok": label_ok,
        "status_ok": status_ok,
        "mode_ok": mode_ok,
        "core_rule_ok": core_rule_ok,
        "read_only": read_only,
        "research_only": research_only,
        "executes_false": executes_false,
        "imports_csv_false": imports_csv_false,
        "reads_contents_false": reads_contents_false,
        "this_imports_false": this_imports_false,
        "this_reads_false": this_reads_false,
        "this_writes_false": this_writes_false,
        "human_import_required": human_import_required,
        "mission_flow_refs_ok": mission_flow_refs_ok,
        "flags_false": flags_false,
        "authorizes_nothing": authorizes_nothing,
        "gates_locked": gates_locked,
        "posture_ok": posture_ok,
        "states_blocked_locked": states_blocked_locked,
        "next_action_ok": next_action_ok,
        "spec_keys_ok": spec_keys_ok,
        "criteria_present": criteria_present,
        "columns_ok": columns_ok,
        "symbols_ok": symbols_ok,
        "rejection_rules_present": rejection_rules_present,
        "validation_checks_present": validation_checks_present,
        "hard_stops_present": hard_stops_present,
        "approved_paths_ok": approved_paths_ok,
        "categories_ok": categories_ok,
        "evaluations_valid": evaluations_valid,
        "futures_rejected_ok": futures_rejected_ok,
        "trading_export_rejected_ok": trading_export_rejected_ok,
        "next_action_in_spec_ok": next_action_in_spec_ok,
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


def render_crypto_d1_manual_csv_spot_data_import_plan_contract_markdown(
    contract: Any,
) -> str:
    """Render a built manual CSV import plan contract as a deterministic markdown
    brief. Pure string formatting; writes nothing."""
    c = contract if isinstance(contract, dict) else {}
    spec = c.get("import_plan") or {}
    paths = spec.get("approved_future_paths") or {}
    lines: list[str] = []
    lines.append("# Crypto-D1 Manual CSV Spot Data Import Plan Contract")
    lines.append("")
    lines.append("- Label: " + str(c.get("label", "")))
    lines.append("- Mode: " + str(c.get("mode", "")))
    lines.append("- Status: " + str(c.get("status", "")))
    lines.append("- Safe: " + str(c.get("safe", False)))
    lines.append(
        "- Next recommended action: " + str(c.get("next_recommended_action", ""))
    )
    lines.append(
        "- This contract imports CSV: " + str(c.get("this_contract_imports_csv", False))
    )
    lines.append(
        "- This contract reads file contents: "
        + str(c.get("this_contract_reads_file_contents", False))
    )
    lines.append("- real_data_qa state: " + str(c.get("real_data_qa_state", "")))
    lines.append(
        "- baseline_backtest state: " + str(c.get("baseline_backtest_state", ""))
    )
    lines.append("- paper / live state: " + str(c.get("paper_live_state", "")))

    _emit(lines, "1. Required CSV Source Criteria", list(spec.get("source_criteria") or []))
    _emit(lines, "2. Required Symbols", list(spec.get("required_symbols") or []))
    _emit(lines, "2b. Required Timeframes", list(spec.get("required_timeframes") or []))
    _emit(lines, "3. Required Columns", list(spec.get("required_columns") or []))
    _emit(lines, "4. Rejection Rules", list(spec.get("rejection_rules") or []))
    _emit(
        lines,
        "5. Approved FUTURE-Only Import Paths (recorded only; nothing written)",
        [
            "input_candidate_path: " + str(paths.get("input_candidate_path", "")),
            "validated_output_path: " + str(paths.get("validated_output_path", "")),
            "report_dir: " + str(paths.get("report_dir", "")),
        ],
    )
    _emit(
        lines,
        "6. Future Validation Checks",
        list(spec.get("future_validation_checks") or []),
    )
    _emit(lines, "7. Hard Stops", list(spec.get("hard_stops") or []))

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
    _emit(lines, "Candidate Source Evaluations", rank_rows)
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
        "Accepted For Future Import (eligible for human import)",
        list(spec.get("accepted_for_future_import") or []),
    )
    _emit(
        lines,
        "Next Recommended Action",
        [str(spec.get("next_recommended_action", ""))],
    )
    _emit(
        lines,
        "8. No-Unlock Confirmation",
        [
            str(k) + ": " + str(v)
            for k, v in (spec.get("no_unlock_confirmation") or {}).items()
        ],
    )
    _emit(
        lines,
        "No-Write Confirmation",
        [
            str(k) + ": " + str(v)
            for k, v in (spec.get("no_write_confirmation") or {}).items()
        ],
    )
    _emit(lines, "Operator Next Step", [str(c.get("operator_next_step", ""))])
    return "\n".join(lines)
